"""Backtest engine: daily iteration with factor computation, risk checks, and order execution."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.data.storage import DataStore
from src.backtest.portfolio import Portfolio
from src.backtest.broker import SimulatedBroker
from src.backtest.metrics import compute_metrics
from src.factors.base import compute_all_factors
from src.strategy.scorer import score_stocks, select_top_stocks
from src.strategy.allocator import allocate_weights
from src.strategy.timing import compute_timing_signal
from src.risk.stop_loss import check_hard_stop, check_trailing_stop
from src.risk.drawdown import check_drawdown
from src.risk.volatility import compute_volatility_ratio, get_rebalance_regime
from src.risk.circuit_breaker import (
    CircuitBreakerState,
    check_circuit_breaker,
    is_circuit_breaker_active,
    get_position_scale,
)

logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    date: str
    symbol: str
    action: str
    shares: int
    price: float
    cost: float
    pnl: float = 0.0  # Filled on close


@dataclass
class BacktestResult:
    nav_series: pd.Series
    trade_log: pd.DataFrame
    metrics: dict
    daily_snapshots: list[dict] = field(default_factory=list)


class BacktestEngine:
    """Event-driven daily backtest engine."""

    def __init__(self, config: dict):
        self.config = config
        data_cfg = config.get("data", {})
        self.store = DataStore(data_cfg.get("db_path", "data/quant.db"))
        self.broker = SimulatedBroker(config, self.store)

    def run(self, start_date: str, end_date: str) -> BacktestResult:
        """Run backtest over the specified date range.

        Daily loop (updated with volatility-adaptive risk controls):
        1. Update prices in portfolio
        2. Compute daily NAV change
        3. Check circuit breaker (before other risk checks)
        4. Check risk / stop-loss conditions (with adaptive ATR multiple)
        5. Execute pending orders (from previous day due to T+1)
        6. On rebalance days (dynamic frequency): compute factors → score → signals
        7. Record NAV
        """
        bt_cfg = self.config.get("backtest", {})
        initial_capital = bt_cfg.get("initial_capital", 1_000_000)

        portfolio = Portfolio(initial_capital=initial_capital)
        trade_log: list[TradeRecord] = []
        pending_orders: list[dict] = []

        # Circuit breaker state
        cb_state = CircuitBreakerState()

        # Dynamic rebalance tracking
        last_rebalance_date: str | None = None

        # Get trading dates
        trading_dates = self._get_trading_dates(start_date, end_date)
        if not trading_dates:
            logger.error("No trading dates found between %s and %s", start_date, end_date)
            return BacktestResult(
                nav_series=pd.Series(dtype=float),
                trade_log=pd.DataFrame(),
                metrics={},
            )

        logger.info(
            "Starting backtest: %s to %s (%d trading days)",
            start_date, end_date, len(trading_dates),
        )

        for date in trading_dates:
            date_str = date if isinstance(date, str) else date.strftime("%Y-%m-%d")

            # 1. Update prices
            prices = self._get_current_prices(portfolio.holdings.keys(), date_str)
            portfolio.update_prices(prices)

            # 2. Compute volatility ratio for today
            volatility_ratio = compute_volatility_ratio(self.store, date_str)

            # 3. Check circuit breaker FIRST
            cb_actions = []
            if len(portfolio.nav_history) >= 1:
                current_nav = portfolio.nav
                previous_nav = portfolio.nav_history[-1] if portfolio.nav_history else None
                cb_state, cb_actions = check_circuit_breaker(
                    current_nav, previous_nav, cb_state, self.config,
                )
                if cb_state.trigger_date is None and cb_actions:
                    cb_state.trigger_date = date_str

            # Execute circuit breaker actions
            if "liquidate" in cb_actions:
                for sym in list(portfolio.holdings.keys()):
                    h = portfolio.holdings[sym]
                    buy_date = h.buy_date if hasattr(h, 'buy_date') else ""
                    can_sell = buy_date < date_str
                    if can_sell:
                        result = self.broker.execute_sell(portfolio, sym, h.shares, date_str)
                        if not result.rejected:
                            trade_log.append(TradeRecord(
                                date=date_str, symbol=sym, action="SELL_CIRCUIT_BREAKER",
                                shares=result.executed_shares, price=result.price,
                                cost=result.total_cost,
                            ))
                    else:
                        # T+1 constraint: defer to next day
                        pending_orders.append({
                            "symbol": sym, "action": "SELL",
                            "shares": h.shares,
                        })
                        logger.info("T+1 constraint: %s sell deferred to next trading day", sym)

            elif "reduce_50" in cb_actions:
                for sym in list(portfolio.holdings.keys()):
                    h = portfolio.holdings[sym]
                    buy_date = h.buy_date if hasattr(h, 'buy_date') else ""
                    can_sell = buy_date < date_str
                    shares_to_sell = h.shares // 2
                    if shares_to_sell <= 0:
                        continue
                    if can_sell:
                        result = self.broker.execute_sell(portfolio, sym, shares_to_sell, date_str)
                        if not result.rejected:
                            trade_log.append(TradeRecord(
                                date=date_str, symbol=sym, action="SELL_CIRCUIT_BREAKER",
                                shares=result.executed_shares, price=result.price,
                                cost=result.total_cost,
                            ))
                    else:
                        pending_orders.append({
                            "symbol": sym, "action": "SELL",
                            "shares": shares_to_sell,
                        })
                        logger.info("T+1 constraint: %s sell deferred to next trading day", sym)

            # 4. Risk checks — generate emergency sell orders (skip if circuit breaker active)
            if not is_circuit_breaker_active(cb_state):
                emergency_sells = self._check_risk(portfolio, date_str, volatility_ratio)
                for sym in emergency_sells:
                    if sym in portfolio.holdings:
                        h = portfolio.holdings[sym]
                        result = self.broker.execute_sell(portfolio, sym, h.shares, date_str)
                        if not result.rejected:
                            trade_log.append(TradeRecord(
                                date=date_str, symbol=sym, action="SELL_STOP",
                                shares=result.executed_shares, price=result.price,
                                cost=result.total_cost,
                            ))

            # 5. Execute pending orders from previous rebalance / deferred circuit breaker
            for order in pending_orders:
                sym = order["symbol"]
                if order["action"] == "BUY":
                    result = self.broker.execute_buy(
                        portfolio, sym, order["target_value"], date_str,
                        subsector=order.get("subsector", "other"),
                    )
                    if not result.rejected:
                        trade_log.append(TradeRecord(
                            date=date_str, symbol=sym, action="BUY",
                            shares=result.executed_shares, price=result.price,
                            cost=result.total_cost,
                        ))
                elif order["action"] == "SELL":
                    if sym in portfolio.holdings:
                        shares = order.get("shares", portfolio.holdings[sym].shares)
                        result = self.broker.execute_sell(portfolio, sym, shares, date_str)
                        if not result.rejected:
                            trade_log.append(TradeRecord(
                                date=date_str, symbol=sym, action="SELL",
                                shares=result.executed_shares, price=result.price,
                                cost=result.total_cost,
                            ))
            pending_orders = []

            # 6. Dynamic rebalance check (skip if circuit breaker is active)
            if not is_circuit_breaker_active(cb_state):
                if self._is_rebalance_day(date_str, volatility_ratio, last_rebalance_date, trading_dates):
                    position_scale = get_position_scale(cb_state)
                    pending_orders = self._generate_rebalance_orders(
                        portfolio, date_str, position_scale=position_scale,
                    )
                    last_rebalance_date = date_str
            else:
                logger.debug("Rebalance skipped on %s: circuit breaker active (%s)", date_str, cb_state.status)

            # 7. Record NAV
            # Update prices again after trades
            prices = self._get_current_prices(portfolio.holdings.keys(), date_str)
            portfolio.update_prices(prices)
            portfolio.record_nav(date_str)

        # Compute metrics
        nav_series = pd.Series(portfolio.nav_history, index=portfolio.date_history)
        trade_df = pd.DataFrame([
            {"date": t.date, "symbol": t.symbol, "action": t.action,
             "shares": t.shares, "price": t.price, "cost": t.cost}
            for t in trade_log
        ]) if trade_log else pd.DataFrame()

        metrics = compute_metrics(
            nav_series,
            trade_df,
            initial_capital,
            self.config,
        )

        return BacktestResult(
            nav_series=nav_series,
            trade_log=trade_df,
            metrics=metrics,
        )

    def _get_trading_dates(self, start: str, end: str) -> list[str]:
        """Get list of trading dates from stock_daily data."""
        with self.store._get_conn() as conn:
            rows = conn.execute(
                "SELECT DISTINCT date FROM stock_daily WHERE date >= ? AND date <= ? ORDER BY date",
                (start, end),
            ).fetchall()
        return [r[0] for r in rows]

    def _get_rebalance_dates(self, trading_dates: list[str], freq: str) -> set[str]:
        """Determine rebalance dates based on frequency (legacy static method)."""
        if not trading_dates:
            return set()

        rebalance = set()
        if freq == "monthly":
            current_month = None
            for d in trading_dates:
                month = d[:7]  # YYYY-MM
                if month != current_month:
                    rebalance.add(d)  # First trading day of each month
                    current_month = month
        elif freq == "weekly":
            # Every Monday (or first trading day of the week)
            dates_pd = pd.to_datetime(trading_dates)
            current_week = None
            for dt, d_str in zip(dates_pd, trading_dates):
                week = dt.isocalendar()[1]
                if week != current_week:
                    rebalance.add(d_str)
                    current_week = week
        else:
            # Default: first day only
            rebalance.add(trading_dates[0])

        return rebalance

    def _is_rebalance_day(
        self,
        date_str: str,
        volatility_ratio: float,
        last_rebalance_date: str | None,
        trading_dates: list[str],
    ) -> bool:
        """Dynamically determine if today is a rebalance day based on volatility regime.

        Regimes:
        - monthly: first trading day of a new month
        - biweekly: first trading day of a new 2-week period
        - weekly: first trading day of a new week
        """
        regime = get_rebalance_regime(volatility_ratio, self.config)
        dt = pd.Timestamp(date_str)

        if regime == "monthly":
            # First trading day of a new month
            if last_rebalance_date is None:
                return True
            return date_str[:7] != last_rebalance_date[:7]

        elif regime == "biweekly":
            # Every ~10 trading days (2 weeks)
            if last_rebalance_date is None:
                return True
            # Count trading days since last rebalance
            try:
                last_idx = trading_dates.index(last_rebalance_date)
                curr_idx = trading_dates.index(date_str)
                days_elapsed = curr_idx - last_idx
                return days_elapsed >= 10
            except ValueError:
                return False

        elif regime == "weekly":
            # First trading day of each week
            if last_rebalance_date is None:
                return True
            last_dt = pd.Timestamp(last_rebalance_date)
            return dt.isocalendar()[1] != last_dt.isocalendar()[1] or dt.year != last_dt.year

        return False

    def _get_current_prices(self, symbols, date: str) -> dict[str, float]:
        """Get closing prices for given symbols on a date."""
        prices = {}
        for sym in symbols:
            df = self.store.read_stock_daily(sym, end_date=date)
            if not df.empty:
                prices[sym] = df["close"].iloc[-1]
        return prices

    def _check_risk(
        self,
        portfolio: Portfolio,
        date: str,
        volatility_ratio: float | None = None,
    ) -> list[str]:
        """Run risk checks and return symbols that need emergency selling."""
        sell_symbols = []
        holdings = portfolio.get_holdings_dict()

        # Hard stop-loss (with adaptive ATR multiple)
        hard_alerts = check_hard_stop(
            holdings, self.store, self.config, date,
            volatility_ratio=volatility_ratio,
        )
        for alert in hard_alerts:
            if alert.can_sell_today:
                sell_symbols.append(alert.symbol)

        # Trailing stop
        trail_alerts = check_trailing_stop(holdings, self.store, self.config, date)
        for alert in trail_alerts:
            if alert.can_sell_today:
                sell_symbols.append(alert.symbol)

        # Drawdown check
        dd_alert = check_drawdown(portfolio.nav_history, self.config)
        if dd_alert and dd_alert.tier == "liquidate":
            sell_symbols = list(portfolio.holdings.keys())
        elif dd_alert and dd_alert.tier == "reduce":
            # Sell half of each position
            for sym in list(portfolio.holdings.keys()):
                if sym not in sell_symbols:
                    sell_symbols.append(sym)

        return list(set(sell_symbols))

    def _generate_rebalance_orders(
        self,
        portfolio: Portfolio,
        date: str,
        position_scale: float = 1.0,
    ) -> list[dict]:
        """Generate rebalance orders: compute factors, score, allocate.

        Args:
            portfolio: Current portfolio.
            date: Current date.
            position_scale: Scale factor for position sizes (0.5 during circuit breaker recovery).
        """
        try:
            factor_matrix = compute_all_factors(self.config, date=date, store=self.store)
        except Exception as e:
            logger.error("Factor computation failed on %s: %s", date, e)
            return []

        if factor_matrix.empty:
            return []

        # Timing signal
        timing = compute_timing_signal(self.config, date=date, store=self.store)
        position_ratio = timing["position_ratio"] * position_scale

        # Score and select
        scores = score_stocks(factor_matrix, self.config)
        selected = select_top_stocks(scores, self.config, len(factor_matrix))

        # Build subsector map
        subsector_map = {}
        for sym in factor_matrix.index:
            df = self.store.read_table("universe_cache", where="symbol = ?", params=(sym,))
            if not df.empty and "subsector" in df.columns:
                subsector_map[sym] = df.iloc[0]["subsector"]
            else:
                subsector_map[sym] = "other"

        # Allocate
        target_weights = allocate_weights(
            selected, scores, self.config,
            subsector_map=subsector_map,
            position_ratio=position_ratio,
        )

        # Generate orders by comparing current vs target
        current_weights = portfolio.get_weights()
        orders = []
        nav = portfolio.nav

        # Sell first (free up cash)
        for sym in list(portfolio.holdings.keys()):
            if sym not in target_weights.index or target_weights.get(sym, 0) == 0:
                orders.append({
                    "symbol": sym,
                    "action": "SELL",
                    "shares": portfolio.holdings[sym].shares,
                })

        # Then buy / adjust
        for sym in target_weights.index:
            tw = target_weights[sym]
            cw = current_weights.get(sym, 0)
            diff = tw - cw

            if diff > 0.005:  # Buy threshold
                target_value = diff * nav
                orders.append({
                    "symbol": sym,
                    "action": "BUY",
                    "target_value": target_value,
                    "subsector": subsector_map.get(sym, "other"),
                })

        return orders
