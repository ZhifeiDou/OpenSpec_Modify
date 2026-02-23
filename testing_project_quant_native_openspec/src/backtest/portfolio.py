"""Portfolio state tracking: positions, cash, NAV."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Position:
    code: str
    shares: int
    entry_price: float
    entry_date: str
    current_price: float = 0.0
    peak_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.shares

    def update_price(self, price: float):
        self.current_price = price
        self.peak_price = max(self.peak_price, price)


class Portfolio:
    """Track portfolio state."""

    def __init__(self, initial_capital: float = 1_000_000):
        self.cash: float = initial_capital
        self.initial_capital = initial_capital
        self.positions: dict[str, Position] = {}
        self.nav_history: list[dict] = []
        self.trade_log: list[dict] = []

    @property
    def market_value(self) -> float:
        return sum(pos.market_value for pos in self.positions.values())

    @property
    def nav(self) -> float:
        return self.cash + self.market_value

    def buy(self, code: str, shares: int, price: float, cost: float, date_str: str):
        """Execute a buy order."""
        amount = shares * price + cost
        if amount > self.cash:
            affordable = int((self.cash - cost) / price)
            affordable = (affordable // 100) * 100
            if affordable <= 0:
                return
            shares = affordable
            amount = shares * price + cost

        self.cash -= amount
        if code in self.positions:
            pos = self.positions[code]
            total_shares = pos.shares + shares
            pos.entry_price = (pos.entry_price * pos.shares + price * shares) / total_shares
            pos.shares = total_shares
        else:
            self.positions[code] = Position(
                code=code, shares=shares, entry_price=price,
                entry_date=date_str, current_price=price, peak_price=price
            )

        self.trade_log.append({
            "date": date_str, "code": code, "direction": "buy",
            "price": price, "shares": shares, "cost": cost,
            "amount": amount,
        })

    def sell(self, code: str, shares: int, price: float, cost: float, date_str: str):
        """Execute a sell order."""
        if code not in self.positions:
            return
        pos = self.positions[code]
        shares = min(shares, pos.shares)
        amount = shares * price - cost
        self.cash += amount
        pos.shares -= shares

        if pos.shares <= 0:
            del self.positions[code]

        self.trade_log.append({
            "date": date_str, "code": code, "direction": "sell",
            "price": price, "shares": shares, "cost": cost,
            "amount": amount,
        })

    def update_prices(self, prices: dict[str, float]):
        """Update all position prices."""
        for code, pos in self.positions.items():
            if code in prices:
                pos.update_price(prices[code])

    def record_nav(self, date_str: str):
        """Record daily NAV."""
        self.nav_history.append({
            "date": date_str,
            "nav": self.nav,
            "cash": self.cash,
            "market_value": self.market_value,
            "n_positions": len(self.positions),
        })
