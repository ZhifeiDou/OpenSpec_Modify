"""Transaction cost calculation for A-share trading."""


class TransactionCosts:
    """Calculate realistic A-share transaction costs."""

    def __init__(self, stamp_tax: float = 0.0005,
                 commission: float = 0.0003,
                 commission_min: float = 5.0,
                 slippage: float = 0.0015):
        self.stamp_tax = stamp_tax
        self.commission = commission
        self.commission_min = commission_min
        self.slippage = slippage

    def calculate_buy_cost(self, amount: float) -> float:
        """Calculate buy transaction cost.

        Buy costs: commission + slippage (no stamp tax).
        """
        comm = max(amount * self.commission, self.commission_min)
        slip = amount * self.slippage
        return comm + slip

    def calculate_sell_cost(self, amount: float) -> float:
        """Calculate sell transaction cost.

        Sell costs: stamp tax + commission + slippage.
        """
        stamp = amount * self.stamp_tax
        comm = max(amount * self.commission, self.commission_min)
        slip = amount * self.slippage
        return stamp + comm + slip
