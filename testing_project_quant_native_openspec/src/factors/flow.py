"""Fund flow factors: financing balance change, northbound net buy."""

import numpy as np
import pandas as pd


def financing_balance_change(balance_series: pd.Series, window: int = 5) -> float:
    """Calculate financing balance change rate over N days."""
    if len(balance_series) < window:
        return np.nan
    current = balance_series.iloc[-1]
    past = balance_series.iloc[-window]
    if past == 0:
        return np.nan
    return (current - past) / past


def northbound_net_buy(flow_series: pd.Series, window: int = 10) -> float:
    """Calculate cumulative northbound net buy over N days."""
    if len(flow_series) < window:
        return np.nan
    return flow_series.tail(window).sum()


def compute_flow_factors(financing_data: pd.DataFrame,
                          northbound_data: pd.DataFrame,
                          financing_window: int = 5,
                          northbound_window: int = 10) -> dict:
    """Compute all fund flow factors for a stock."""
    fin_change = np.nan
    if not financing_data.empty and "financing_balance" in financing_data.columns:
        fin_change = financing_balance_change(
            financing_data["financing_balance"], financing_window
        )

    nb_flow = np.nan
    if not northbound_data.empty and "net_flow" in northbound_data.columns:
        nb_flow = northbound_net_buy(northbound_data["net_flow"], northbound_window)

    return {
        "financing_change": fin_change,
        "northbound_flow": nb_flow,
    }
