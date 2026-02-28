"""Shenwan industry classification and sub-sector mapping."""
from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

from src.data.sources.akshare_source import AKShareSource
from src.data.storage import DataStore

logger = logging.getLogger(__name__)

# Shenwan Level-2 sub-sector keyword mapping
_SUBSECTOR_KEYWORDS = {
    "copper": ["铜", "copper"],
    "aluminum": ["铝", "aluminum", "氧化铝"],
    "gold": ["黄金", "gold", "金矿"],
    "rare_earth": ["稀土", "rare earth", "稀有"],
    "lithium": ["锂", "lithium", "碳酸锂"],
    "cobalt_nickel": ["钴", "镍", "cobalt", "nickel"],
    "zinc_lead": ["锌", "铅", "zinc", "lead"],
    "silver": ["白银", "silver", "银矿"],
}

# Sub-sector to futures metal symbol mapping
SUBSECTOR_METAL_MAP = {
    "copper": "cu",
    "aluminum": "al",
    "gold": "au",
    "rare_earth": None,
    "lithium": "LC",
    "cobalt_nickel": "ni",
    "zinc_lead": "zn",
    "silver": "ag",
}


def classify_subsector(name: str, industry_name: str = "") -> str:
    """Classify a stock into a sub-sector based on name and industry."""
    text = (name + " " + industry_name).lower()
    for subsector, keywords in _SUBSECTOR_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text or kw in text:
                return subsector
    return "other"


def get_universe(
    config: dict,
    date: str | None = None,
    store: DataStore | None = None,
) -> pd.DataFrame:
    """Get filtered non-ferrous metals stock universe.

    Returns DataFrame with columns: symbol, name, subsector, industry_name
    """
    universe_cfg = config.get("universe", {})
    industry_code = universe_cfg.get("industry_code", "801050")

    source = AKShareSource()
    raw = source.fetch_industry_stocks(industry_code)

    if raw.empty:
        logger.warning("Failed to fetch industry stocks, trying cache")
        if store:
            cached = store.read_table("universe_cache")
            if not cached.empty:
                return cached
        return pd.DataFrame(columns=["symbol", "name", "subsector"])

    # Normalize columns
    if "symbol" not in raw.columns:
        # AKShare may use different column names
        col_map = {}
        for col in raw.columns:
            cl = col.lower()
            if "代码" in cl or "code" in cl:
                col_map[col] = "symbol"
            elif "名称" in cl or "name" in cl:
                col_map[col] = "name"
            elif "行业" in cl or "industry" in cl:
                col_map[col] = "industry_name"
        raw = raw.rename(columns=col_map)

    if "symbol" not in raw.columns:
        logger.error("Cannot identify symbol column in industry data")
        return pd.DataFrame(columns=["symbol", "name", "subsector"])

    if "name" not in raw.columns:
        raw["name"] = ""
    if "industry_name" not in raw.columns:
        raw["industry_name"] = ""

    # Classify sub-sectors
    raw["subsector"] = raw.apply(
        lambda r: classify_subsector(str(r.get("name", "")), str(r.get("industry_name", ""))),
        axis=1,
    )

    # Apply filters
    df = apply_filters(raw, config, date)

    return df[["symbol", "name", "subsector"]].reset_index(drop=True)


def apply_filters(
    df: pd.DataFrame, config: dict, date: str | None = None
) -> pd.DataFrame:
    """Apply stock universe filters from src/universe/filter.py logic."""
    from src.universe.filter import filter_universe
    return filter_universe(df, config, date)
