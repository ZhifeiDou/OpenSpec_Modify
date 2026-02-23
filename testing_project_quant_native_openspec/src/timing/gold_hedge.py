"""Gold price momentum timing signal."""

import numpy as np
import pandas as pd


def gold_hedge_signal(gold_prices: pd.DataFrame,
                       momentum_window: int = 20,
                       threshold: float = 0.05,
                       reduction_factor: float = 0.70) -> dict:
    """Generate gold hedge timing signal.

    Args:
        gold_prices: DataFrame with 'date' and 'close' columns.
        momentum_window: Window for momentum calculation.
        threshold: Momentum threshold for risk-off signal.
        reduction_factor: Position reduction multiplier when risk-off.

    Returns:
        dict with 'signal' ('risk-off', 'neutral') and 'multiplier'.
    """
    if len(gold_prices) < momentum_window:
        return {"signal": "neutral", "multiplier": 1.0}

    recent = gold_prices["close"].iloc[-1]
    past = gold_prices["close"].iloc[-momentum_window]
    if past == 0:
        return {"signal": "neutral", "multiplier": 1.0}

    momentum = (recent - past) / past

    if momentum > threshold:
        return {"signal": "risk-off", "multiplier": reduction_factor}
    else:
        return {"signal": "neutral", "multiplier": 1.0}
