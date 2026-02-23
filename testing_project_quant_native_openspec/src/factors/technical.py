"""Technical factors: momentum, mean reversion, turnover, volatility."""

import numpy as np
import pandas as pd


def momentum(prices: pd.Series, window: int = 60, skip: int = 5) -> float:
    """Calculate momentum: N-day return excluding most recent skip days."""
    needed = window + skip
    if len(prices) < needed:
        return np.nan
    recent = prices.iloc[-(skip + 1)]
    past = prices.iloc[-needed]
    if past == 0:
        return np.nan
    return (recent - past) / past


def mean_reversion(prices: pd.Series, window: int = 5) -> float:
    """Mean reversion: negative of N-day return."""
    if len(prices) < window:
        return np.nan
    recent = prices.iloc[-1]
    past = prices.iloc[-window]
    if past == 0:
        return np.nan
    return -((recent - past) / past)


def turnover_ratio(volume: pd.Series, window: int = 20) -> float:
    """Average turnover ratio over N days."""
    if len(volume) < window:
        return np.nan
    return volume.tail(window).mean()


def realized_volatility(prices: pd.Series, window: int = 20) -> float:
    """Realized volatility: annualized std of daily returns."""
    if len(prices) < window + 1:
        return np.nan
    returns = prices.pct_change().dropna().tail(window)
    return returns.std() * np.sqrt(252)


def compute_technical_factors(price_df: pd.DataFrame,
                               momentum_window: int = 60,
                               momentum_skip: int = 5,
                               reversion_window: int = 5,
                               turnover_window: int = 20,
                               vol_window: int = 20) -> dict:
    """Compute all technical factors for a stock."""
    close = price_df["close"]
    vol = price_df["volume"]
    return {
        "momentum": momentum(close, momentum_window, momentum_skip),
        "mean_reversion": mean_reversion(close, reversion_window),
        "turnover": turnover_ratio(vol, turnover_window),
        "volatility": realized_volatility(close, vol_window),
    }
