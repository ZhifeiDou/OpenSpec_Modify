"""Simulated broker: T+1, price limits, suspension, transaction costs."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from src.backtest.portfolio import Portfolio
from src.data.storage import DataStore

logger = logging.getLogger(__name__)


@dataclass
class OrderResult:
    symbol: str
    action: str  # "BUY" or "SELL"
    requested_shares: int
    executed_shares: int
    price: float
    commission: float
    stamp_tax: float
    slippage_cost: float
    total_cost: float
    rejected: bool = False
    reject_reason: str = ""


class SimulatedBroker:
    """Simulated broker enforcing A-share trading rules."""

    def __init__(self, config: dict, store: DataStore):
        self.config = config
        self.store = store
        bt_cfg = config.get("backtest", {})
        self.stamp_tax_rate = bt_cfg.get("stamp_tax", 0.0005)
        self.commission_rate = bt_cfg.get("commission", 0.0003)
        self.min_commission = bt_cfg.get("min_commission", 5)
        self.slippage_rate = bt_cfg.get("slippage", 0.0015)

    def execute_buy(
        self, portfolio: Portfolio, symbol: str, target_value: float,
        date: str, subsector: str = "other",
    ) -> OrderResult:
        """Execute a buy order with A-share rules."""
        df = self.store.read_stock_daily(symbol, end_date=date)
        if df.empty:
            return self._rejected(symbol, "BUY", 0, "No price data")

        price = df["close"].iloc[-1]

        # Check limit-up (cannot buy at limit-up)
        if len(df) >= 2:
            prev_close = df["close"].iloc[-2]
            change_pct = (price - prev_close) / prev_close
            if change_pct >= 0.095:  # Near or at +10% limit
                return self._rejected(symbol, "BUY", 0, "Limit-up: cannot buy")

        # Check suspension (volume = 0)
        if len(df) >= 1 and df["volume"].iloc[-1] == 0:
            return self._rejected(symbol, "BUY", 0, "Suspended")

        # Apply slippage (buy at higher price)
        exec_price = price * (1 + self.slippage_rate)

        # Calculate shares (lots of 100)
        shares = int(target_value / exec_price // 100) * 100
        if shares <= 0:
            return self._rejected(symbol, "BUY", 0, "Value too small for 1 lot")

        actual_value = shares * exec_price
        commission = max(actual_value * self.commission_rate, self.min_commission)
        total_cost = actual_value + commission

        if total_cost > portfolio.cash:
            shares = int(portfolio.cash / (exec_price * 1.001) // 100) * 100
            if shares <= 0:
                return self._rejected(symbol, "BUY", 0, "Insufficient cash")
            actual_value = shares * exec_price
            commission = max(actual_value * self.commission_rate, self.min_commission)
            total_cost = actual_value + commission

        # Execute
        portfolio.buy(symbol, shares, exec_price, date, subsector)
        portfolio.cash -= commission  # Commission deducted separately

        return OrderResult(
            symbol=symbol,
            action="BUY",
            requested_shares=int(target_value / exec_price // 100) * 100,
            executed_shares=shares,
            price=exec_price,
            commission=commission,
            stamp_tax=0.0,
            slippage_cost=shares * price * self.slippage_rate,
            total_cost=total_cost,
        )

    def execute_sell(
        self, portfolio: Portfolio, symbol: str, shares: int, date: str,
    ) -> OrderResult:
        """Execute a sell order with A-share rules."""
        if symbol not in portfolio.holdings:
            return self._rejected(symbol, "SELL", shares, "Not in portfolio")

        holding = portfolio.holdings[symbol]

        # T+1: cannot sell stocks bought today
        if holding.buy_date >= date:
            return self._rejected(symbol, "SELL", shares, "T+1: bought today")

        df = self.store.read_stock_daily(symbol, end_date=date)
        if df.empty:
            return self._rejected(symbol, "SELL", shares, "No price data")

        price = df["close"].iloc[-1]

        # Check limit-down (cannot sell at limit-down)
        if len(df) >= 2:
            prev_close = df["close"].iloc[-2]
            change_pct = (price - prev_close) / prev_close
            if change_pct <= -0.095:  # Near or at -10% limit
                return self._rejected(symbol, "SELL", shares, "Limit-down: cannot sell")

        # Check suspension
        if df["volume"].iloc[-1] == 0:
            return self._rejected(symbol, "SELL", shares, "Suspended")

        # Apply slippage (sell at lower price)
        exec_price = price * (1 - self.slippage_rate)
        actual_shares = min(shares, holding.shares)

        proceeds = actual_shares * exec_price
        commission = max(proceeds * self.commission_rate, self.min_commission)
        stamp_tax = proceeds * self.stamp_tax_rate  # Sell-side only
        net_proceeds = proceeds - commission - stamp_tax

        # Execute
        portfolio.sell(symbol, actual_shares, exec_price)
        portfolio.cash -= (commission + stamp_tax)

        return OrderResult(
            symbol=symbol,
            action="SELL",
            requested_shares=shares,
            executed_shares=actual_shares,
            price=exec_price,
            commission=commission,
            stamp_tax=stamp_tax,
            slippage_cost=actual_shares * price * self.slippage_rate,
            total_cost=commission + stamp_tax,
        )

    def _rejected(self, symbol: str, action: str, shares: int, reason: str) -> OrderResult:
        logger.info("Order rejected: %s %s %d shares — %s", action, symbol, shares, reason)
        return OrderResult(
            symbol=symbol,
            action=action,
            requested_shares=shares,
            executed_shares=0,
            price=0.0,
            commission=0.0,
            stamp_tax=0.0,
            slippage_cost=0.0,
            total_cost=0.0,
            rejected=True,
            reject_reason=reason,
        )
