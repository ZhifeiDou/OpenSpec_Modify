"""Portfolio state manager: track holdings, cash, NAV, and T+1 buy dates."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from copy import deepcopy

logger = logging.getLogger(__name__)


@dataclass
class Holding:
    symbol: str
    shares: int
    avg_price: float
    buy_date: str
    peak_price: float = 0.0
    subsector: str = "other"

    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_price


@dataclass
class Portfolio:
    """Track portfolio state during backtest."""

    initial_capital: float = 1_000_000.0
    cash: float = 0.0
    holdings: dict[str, Holding] = field(default_factory=dict)
    nav_history: list[float] = field(default_factory=list)
    date_history: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.cash == 0:
            self.cash = self.initial_capital

    @property
    def holdings_value(self) -> float:
        """Total market value of all holdings."""
        return sum(h.shares * h.peak_price for h in self.holdings.values())

    @property
    def nav(self) -> float:
        """Net asset value = cash + holdings value."""
        return self.cash + self.holdings_value

    @property
    def current_drawdown(self) -> float:
        """Current drawdown from peak NAV."""
        if not self.nav_history:
            return 0.0
        peak = max(self.nav_history)
        if peak <= 0:
            return 0.0
        return (peak - self.nav) / peak

    def update_prices(self, prices: dict[str, float]):
        """Update holdings with current market prices."""
        for symbol, holding in self.holdings.items():
            if symbol in prices:
                price = prices[symbol]
                if price > holding.peak_price:
                    holding.peak_price = price

    def record_nav(self, date: str):
        """Record current NAV for the day."""
        self.nav_history.append(self.nav)
        self.date_history.append(date)

    def buy(self, symbol: str, shares: int, price: float, date: str,
            subsector: str = "other") -> float:
        """Execute a buy order. Returns total cost including the price paid."""
        if shares <= 0 or price <= 0:
            return 0.0

        cost = shares * price

        if cost > self.cash:
            # Reduce shares to what we can afford (lots of 100)
            affordable = int(self.cash / price // 100) * 100
            if affordable <= 0:
                logger.warning("Insufficient cash to buy %s", symbol)
                return 0.0
            shares = affordable
            cost = shares * price

        self.cash -= cost

        if symbol in self.holdings:
            h = self.holdings[symbol]
            total_shares = h.shares + shares
            h.avg_price = (h.cost_basis + cost) / total_shares
            h.shares = total_shares
            h.peak_price = max(h.peak_price, price)
        else:
            self.holdings[symbol] = Holding(
                symbol=symbol,
                shares=shares,
                avg_price=price,
                buy_date=date,
                peak_price=price,
                subsector=subsector,
            )

        return cost

    def sell(self, symbol: str, shares: int, price: float) -> float:
        """Execute a sell order. Returns proceeds."""
        if symbol not in self.holdings:
            return 0.0

        h = self.holdings[symbol]
        shares = min(shares, h.shares)
        if shares <= 0:
            return 0.0

        proceeds = shares * price
        self.cash += proceeds

        h.shares -= shares
        if h.shares <= 0:
            del self.holdings[symbol]

        return proceeds

    def get_weights(self) -> dict[str, float]:
        """Get current portfolio weights."""
        total = self.nav
        if total <= 0:
            return {}
        return {sym: (h.shares * h.peak_price) / total for sym, h in self.holdings.items()}

    def get_holdings_dict(self) -> dict:
        """Get holdings as a plain dict for risk checks."""
        return {
            sym: {
                "entry_price": h.avg_price,
                "buy_date": h.buy_date,
                "peak_price": h.peak_price,
                "shares": h.shares,
                "subsector": h.subsector,
            }
            for sym, h in self.holdings.items()
        }

    def snapshot(self) -> dict:
        """Create a snapshot of current state."""
        return {
            "cash": self.cash,
            "nav": self.nav,
            "holdings_value": self.holdings_value,
            "num_holdings": len(self.holdings),
            "holdings": deepcopy(self.get_holdings_dict()),
        }
