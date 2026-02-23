"""PMI direction timing signal."""

import numpy as np
import pandas as pd


def pmi_timing_signal(pmi_data: pd.DataFrame,
                       expansion_threshold: float = 50.0,
                       reduction_factor: float = 0.70) -> dict:
    """Generate PMI-based timing signal.

    Bullish: PMI > 50 and rising.
    Bearish: PMI < 50 and falling.

    Args:
        pmi_data: DataFrame with 'date' and 'pmi' columns.
        expansion_threshold: PMI level separating expansion/contraction.
        reduction_factor: Position reduction when bearish.

    Returns:
        dict with 'signal' ('bullish', 'bearish', 'neutral') and 'multiplier'.
    """
    if len(pmi_data) < 2:
        return {"signal": "neutral", "multiplier": 1.0}

    current = pmi_data["pmi"].iloc[-1]
    previous = pmi_data["pmi"].iloc[-2]

    if pd.isna(current) or pd.isna(previous):
        return {"signal": "neutral", "multiplier": 1.0}

    if current > expansion_threshold and current > previous:
        return {"signal": "bullish", "multiplier": 1.0}
    elif current < expansion_threshold and current < previous:
        return {"signal": "bearish", "multiplier": reduction_factor}
    else:
        return {"signal": "neutral", "multiplier": 1.0}
