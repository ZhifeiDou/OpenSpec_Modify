"""Metal crash alert monitoring."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


class MetalCrashAlert:
    """Monitor daily metal futures prices for crash alerts."""

    def __init__(self, daily_drop_threshold: float = 0.03):
        self.threshold = daily_drop_threshold

    def check(self, metal_prices: dict[str, pd.DataFrame]) -> list[dict]:
        """Check all tracked metals for crash conditions.

        Args:
            metal_prices: Dict of metal name to DataFrame with 'date' and 'close'.

        Returns:
            List of alert dicts with 'metal', 'drop_pct', 'date'.
        """
        alerts = []
        for metal, df in metal_prices.items():
            if len(df) < 2:
                continue
            prev_close = df["close"].iloc[-2]
            curr_close = df["close"].iloc[-1]
            if prev_close > 0:
                drop = (prev_close - curr_close) / prev_close
                if drop > self.threshold:
                    alert = {
                        "metal": metal,
                        "drop_pct": drop,
                        "date": str(df["date"].iloc[-1]),
                    }
                    alerts.append(alert)
                    logger.warning(
                        f"METAL CRASH ALERT: {metal} dropped {drop:.2%} on {alert['date']}"
                    )
        return alerts
