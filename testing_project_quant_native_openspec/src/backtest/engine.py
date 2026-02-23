"""Event-driven daily backtesting engine."""

import logging
import pandas as pd
import yaml

from src.backtest.portfolio import Portfolio
from src.backtest.order import OrderQueue
from src.backtest.costs import TransactionCosts
from src.risk.stop_loss import StopLossManager
from src.risk.drawdown import DrawdownController

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Event-driven daily backtest engine for A-share trading."""

    def __init__(self, config_path: str = "config/settings.yaml"):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        bt_config = config["backtest"]
        risk_config = config["risk"]

        self.portfolio = Portfolio(bt_config["initial_capital"])
        self.order_queue = OrderQueue(bt_config.get("price_limit", 0.10))
        self.costs = TransactionCosts(
            stamp_tax=bt_config["costs"]["stamp_tax"],
            commission=bt_config["costs"]["commission"],
            commission_min=bt_config["costs"]["commission_min"],
            slippage=bt_config["costs"]["slippage"],
        )
        self.stop_loss = StopLossManager(
            atr_period=risk_config["hard_stop_loss"]["atr_period"],
            atr_multiplier=risk_config["hard_stop_loss"]["atr_multiplier"],
            activation_gain=risk_config["trailing_stop"]["activation_gain"],
            drawdown_trigger=risk_config["trailing_stop"]["peak_drawdown_trigger"],
        )
        self.drawdown = DrawdownController(
            level1_threshold=risk_config["portfolio_drawdown"]["level1_threshold"],
            level2_threshold=risk_config["portfolio_drawdown"]["level2_threshold"],
        )

        self.rebalance_freq = bt_config.get("rebalance_frequency", "monthly")
        self.buy_dates: dict[str, str] = {}  # code -> buy date for T+1

    def run(self, trading_dates: list[str],
            price_data: dict[str, pd.DataFrame],
            rebalance_callback=None) -> Portfolio:
        """Run backtest over trading dates.

        Args:
            trading_dates: List of trading date strings.
            price_data: Dict of stock code to DataFrame with OHLCV data.
            rebalance_callback: Function(date, portfolio, price_data) -> dict of target weights.

        Returns:
            Portfolio with complete history.
        """
        prev_month = None

        for i, date_str in enumerate(trading_dates):
            # 1. Update prices
            current_prices = {}
            prev_closes = {}
            volumes = {}
            for code, df in price_data.items():
                day_data = df[df["date"] == date_str]
                if len(day_data) > 0:
                    row = day_data.iloc[0]
                    current_prices[code] = row["close"]
                    volumes[code] = row["volume"]
                    # Get previous close
                    idx = df.index[df["date"] == date_str][0]
                    if idx > 0:
                        prev_closes[code] = df.iloc[idx - 1]["close"]
                    else:
                        prev_closes[code] = row["close"]

            self.portfolio.update_prices(current_prices)
            self.drawdown.update(self.portfolio.nav)

            # 2. Check risk / stop-loss
            sell_signals = []
            for code, pos in list(self.portfolio.positions.items()):
                if code in price_data:
                    history = price_data[code][price_data[code]["date"] <= date_str].tail(30)
                    result = self.stop_loss.check(
                        code, pos.current_price, pos.entry_price, history
                    )
                    if result["should_sell"]:
                        sell_signals.append(code)

            # Portfolio drawdown check
            dd_result = self.drawdown.check(self.portfolio.nav)
            if dd_result["level"] == 2:
                sell_signals = list(self.portfolio.positions.keys())
            elif dd_result["level"] == 1:
                for code, pos in self.portfolio.positions.items():
                    target_shares = pos.shares // 2
                    if target_shares < pos.shares:
                        self.order_queue.add_order(
                            code, "sell", pos.shares - target_shares,
                            date_str, "drawdown_reduce"
                        )

            for code in sell_signals:
                if code in self.portfolio.positions:
                    self.order_queue.add_order(
                        code, "sell", self.portfolio.positions[code].shares,
                        date_str, "stop_loss"
                    )

            # 3. Execute pending orders
            executable, _ = self.order_queue.process_orders(
                date_str, current_prices, prev_closes, volumes, self.buy_dates
            )
            for order in executable:
                price = current_prices.get(order.code, 0)
                if price <= 0:
                    continue
                if order.direction == "buy":
                    cost = self.costs.calculate_buy_cost(order.shares * price)
                    self.portfolio.buy(order.code, order.shares, price, cost, date_str)
                    self.buy_dates[order.code] = date_str
                elif order.direction == "sell":
                    cost = self.costs.calculate_sell_cost(order.shares * price)
                    self.portfolio.sell(order.code, order.shares, price, cost, date_str)
                    if order.code not in self.portfolio.positions:
                        self.stop_loss.remove_position(order.code)
                        self.buy_dates.pop(order.code, None)

            # 4. Rebalance if needed
            if rebalance_callback and self._is_rebalance_day(date_str, prev_month):
                target_weights = rebalance_callback(date_str, self.portfolio, price_data)
                self._generate_rebalance_orders(target_weights, current_prices, date_str)
                current_month = date_str[:7]
                prev_month = current_month

            # 5. Record NAV
            self.portfolio.record_nav(date_str)

        return self.portfolio

    def _is_rebalance_day(self, date_str: str, prev_month: str | None) -> bool:
        """Check if current date is a rebalance day."""
        current_month = date_str[:7]  # YYYY-MM
        if self.rebalance_freq == "monthly":
            return current_month != prev_month
        return False  # simplified

    def _generate_rebalance_orders(self, target_weights: dict[str, float],
                                     current_prices: dict[str, float],
                                     date_str: str):
        """Generate buy/sell orders to reach target weights."""
        total_value = self.portfolio.nav

        # Sell positions not in target
        for code in list(self.portfolio.positions.keys()):
            if code not in target_weights:
                pos = self.portfolio.positions[code]
                self.order_queue.add_order(code, "sell", pos.shares, date_str, "rebalance")

        # Adjust existing and add new positions
        for code, target_w in target_weights.items():
            target_value = total_value * target_w
            current_value = 0
            if code in self.portfolio.positions:
                current_value = self.portfolio.positions[code].market_value

            diff = target_value - current_value
            price = current_prices.get(code, 0)
            if price <= 0:
                continue

            shares = abs(int(diff / price))
            shares = (shares // 100) * 100  # A-share lot size

            if shares > 0:
                if diff > 0:
                    self.order_queue.add_order(code, "buy", shares, date_str, "rebalance")
                else:
                    self.order_queue.add_order(code, "sell", shares, date_str, "rebalance")
