"""Order queue with T+1 enforcement and limit-up/down handling."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    code: str
    direction: str  # "buy" or "sell"
    shares: int
    created_date: str
    reason: str = ""


class OrderQueue:
    """Manage pending orders with T+1 and limit-up/down rules."""

    def __init__(self, price_limit: float = 0.10):
        self.pending: list[Order] = []
        self.price_limit = price_limit

    def add_order(self, code: str, direction: str, shares: int,
                  date_str: str, reason: str = ""):
        """Add a new order to the queue."""
        self.pending.append(Order(
            code=code, direction=direction, shares=shares,
            created_date=date_str, reason=reason
        ))

    def is_limit_up(self, current_price: float, prev_close: float) -> bool:
        """Check if stock hit limit-up (10% daily max)."""
        if prev_close == 0:
            return False
        return (current_price - prev_close) / prev_close >= self.price_limit - 0.001

    def is_limit_down(self, current_price: float, prev_close: float) -> bool:
        """Check if stock hit limit-down (10% daily min)."""
        if prev_close == 0:
            return False
        return (prev_close - current_price) / prev_close >= self.price_limit - 0.001

    def is_suspended(self, volume: float) -> bool:
        """Check if stock is suspended (zero volume)."""
        return volume == 0

    def process_orders(self, current_date: str, prices: dict,
                        prev_closes: dict, volumes: dict,
                        buy_dates: dict) -> tuple[list[Order], list[Order]]:
        """Process pending orders, returning executable and deferred orders.

        Args:
            current_date: Current trading date.
            prices: Current prices by stock code.
            prev_closes: Previous close prices by stock code.
            volumes: Current volumes by stock code.
            buy_dates: Dict of stock code to buy date for T+1 checking.

        Returns:
            (executable, deferred): Orders that can execute and those deferred.
        """
        executable = []
        deferred = []

        for order in self.pending:
            code = order.code
            price = prices.get(code, 0)
            prev = prev_closes.get(code, 0)
            vol = volumes.get(code, 0)

            # Suspended stock
            if self.is_suspended(vol):
                deferred.append(order)
                continue

            if order.direction == "buy":
                # Cannot buy at limit-up
                if self.is_limit_up(price, prev):
                    deferred.append(order)
                else:
                    executable.append(order)

            elif order.direction == "sell":
                # T+1: cannot sell stocks bought today
                bought_date = buy_dates.get(code, "")
                if bought_date == current_date:
                    deferred.append(order)
                    continue

                # Cannot sell at limit-down
                if self.is_limit_down(price, prev):
                    deferred.append(order)
                else:
                    executable.append(order)

        self.pending = deferred
        return executable, deferred
