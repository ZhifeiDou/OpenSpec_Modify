"""Commodity factors: metal price momentum, futures basis, inventory change."""

import pandas as pd
import numpy as np


def metal_price_momentum(futures_prices: pd.DataFrame, window: int = 60) -> float:
    """Calculate metal price momentum as N-day return of futures."""
    if len(futures_prices) < window:
        return np.nan
    recent = futures_prices["close"].iloc[-1]
    past = futures_prices["close"].iloc[-window]
    if past == 0:
        return np.nan
    return (recent - past) / past


def futures_basis(spot_price: float, futures_price: float) -> float:
    """Calculate futures basis: (spot - futures) / futures."""
    if futures_price == 0:
        return np.nan
    return (spot_price - futures_price) / futures_price


def inventory_change(inventory_series: pd.Series, window: int = 20) -> float:
    """Calculate inventory change rate over window."""
    if len(inventory_series) < window:
        return np.nan
    current = inventory_series.iloc[-1]
    past = inventory_series.iloc[-window]
    if past == 0:
        return np.nan
    return (current - past) / past


def compute_commodity_factors(stock_code: str, subsector: str,
                              metal_futures: dict[str, pd.DataFrame],
                              window: int = 60) -> dict:
    """Compute all commodity factors for a stock."""
    # Map subsector to metal
    sector_metal_map = {
        "copper": "copper", "aluminum": "aluminum", "gold": "gold",
        "zinc": "zinc", "lithium": "lithium",
        "cobalt": "copper",  # cobalt proxied by copper
        "rare_earth": "aluminum",  # rare earth proxied by aluminum
    }
    metal = sector_metal_map.get(subsector, "copper")
    futures_df = metal_futures.get(metal, pd.DataFrame())

    momentum = metal_price_momentum(futures_df, window)
    basis = np.nan  # basis requires spot data, simplified here

    return {
        "metal_momentum": momentum,
        "futures_basis": basis,
        "inventory_change": np.nan,  # requires inventory data source
    }
