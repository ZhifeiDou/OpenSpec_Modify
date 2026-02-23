"""Stock universe filters — exclude ST, suspended, illiquid, newly listed stocks."""
from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


def filter_universe(
    df: pd.DataFrame, config: dict, date: str | None = None
) -> pd.DataFrame:
    """Apply all universe filters to a raw stock list.

    Filters applied:
    1. Exclude ST / *ST stocks (by name pattern)
    2. Exclude suspended stocks (if data available)
    3. Exclude stocks listed < min_listing_days
    4. Exclude stocks with daily turnover < min_daily_turnover
    """
    if df.empty:
        return df

    universe_cfg = config.get("universe", {})
    exclude_st = universe_cfg.get("exclude_st", True)
    min_listing_days = universe_cfg.get("min_listing_days", 60)
    min_turnover = universe_cfg.get("min_daily_turnover", 5_000_000)

    original_count = len(df)
    exclusions = []

    # 1. Exclude ST stocks
    if exclude_st and "name" in df.columns:
        st_mask = df["name"].str.contains(r"ST|st|\*ST", na=False, regex=True)
        n_st = st_mask.sum()
        if n_st > 0:
            df = df[~st_mask]
            exclusions.append(f"ST: {n_st}")

    # 2. Exclude suspended (if volume data available)
    if "volume" in df.columns:
        suspended = df["volume"] == 0
        n_susp = suspended.sum()
        if n_susp > 0:
            df = df[~suspended]
            exclusions.append(f"suspended: {n_susp}")

    # 3. Exclude newly listed stocks
    if "list_date" in df.columns:
        ref_date = pd.to_datetime(date) if date else pd.Timestamp.now()
        df["list_date"] = pd.to_datetime(df["list_date"], errors="coerce")
        newly_listed = (ref_date - df["list_date"]).dt.days < min_listing_days
        n_new = newly_listed.sum()
        if n_new > 0:
            df = df[~newly_listed]
            exclusions.append(f"newly listed: {n_new}")

    # 4. Exclude illiquid stocks
    if "avg_turnover" in df.columns:
        illiquid = df["avg_turnover"] < min_turnover
        n_illiquid = illiquid.sum()
        if n_illiquid > 0:
            df = df[~illiquid]
            exclusions.append(f"illiquid: {n_illiquid}")

    filtered_count = len(df)
    if exclusions:
        logger.info(
            "Universe filtered: %d → %d (%s)",
            original_count, filtered_count, ", ".join(exclusions),
        )

    return df


def get_point_in_time_universe(
    config: dict, date: str, store=None
) -> pd.DataFrame:
    """Get the stock universe as of a historical date.

    Uses cached historical classification data to prevent look-ahead bias.
    Falls back to current universe if historical data not available.
    """
    if store:
        cached = store.read_table(
            "universe_history",
            where="date = ?",
            params=(date,),
        )
        if not cached.empty:
            return cached

    # Fallback: use current universe (with warning about potential bias)
    logger.warning(
        "No historical universe data for %s, using current universe (potential look-ahead bias)",
        date,
    )
    from src.universe.classifier import get_universe
    return get_universe(config, date=date, store=store)
