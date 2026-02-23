"""Portfolio drawdown control."""


class DrawdownController:
    """Tiered portfolio drawdown control."""

    def __init__(self, level1_threshold: float = 0.15,
                 level2_threshold: float = 0.20):
        self.level1_threshold = level1_threshold
        self.level2_threshold = level2_threshold
        self.peak_nav: float = 0.0

    def update(self, nav: float):
        """Update peak NAV."""
        self.peak_nav = max(self.peak_nav, nav)

    def check(self, nav: float) -> dict:
        """Check drawdown level and recommended action.

        Returns:
            dict with 'drawdown', 'level', 'action', 'position_multiplier'.
        """
        if self.peak_nav == 0:
            return {"drawdown": 0.0, "level": 0, "action": "hold",
                    "position_multiplier": 1.0}

        drawdown = (self.peak_nav - nav) / self.peak_nav

        if drawdown >= self.level2_threshold:
            return {"drawdown": drawdown, "level": 2, "action": "liquidate",
                    "position_multiplier": 0.0}
        elif drawdown >= self.level1_threshold:
            return {"drawdown": drawdown, "level": 1, "action": "reduce_50",
                    "position_multiplier": 0.5}
        else:
            return {"drawdown": drawdown, "level": 0, "action": "hold",
                    "position_multiplier": 1.0}
