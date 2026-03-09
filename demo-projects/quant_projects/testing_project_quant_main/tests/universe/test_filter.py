"""Tests for stock universe filtering."""
import pandas as pd
from src.universe.filter import filter_universe
from src.universe.classifier import classify_subsector


def _make_config(**overrides):
    cfg = {
        "universe": {
            "exclude_st": True,
            "min_listing_days": 60,
            "min_daily_turnover": 5_000_000,
        }
    }
    cfg["universe"].update(overrides)
    return cfg


def test_exclude_st_stocks():
    df = pd.DataFrame({
        "symbol": ["601899", "000666", "600362"],
        "name": ["紫金矿业", "*ST某某", "江西铜业"],
        "subsector": ["copper", "copper", "copper"],
    })
    result = filter_universe(df, _make_config())
    assert len(result) == 2
    assert "000666" not in result["symbol"].values


def test_exclude_suspended():
    df = pd.DataFrame({
        "symbol": ["601899", "600362"],
        "name": ["紫金矿业", "江西铜业"],
        "subsector": ["copper", "copper"],
        "volume": [5000000, 0],
    })
    result = filter_universe(df, _make_config())
    assert len(result) == 1
    assert result.iloc[0]["symbol"] == "601899"


def test_classify_subsector():
    assert classify_subsector("紫金矿业", "铜") == "copper"
    assert classify_subsector("山东黄金", "黄金") == "gold"
    assert classify_subsector("赣锋锂业", "锂") == "lithium"
    assert classify_subsector("北方稀土", "稀土") == "rare_earth"
    assert classify_subsector("中国铝业", "铝") == "aluminum"
    assert classify_subsector("华友钴业", "钴") == "cobalt_nickel"
    assert classify_subsector("驰宏锌锗", "锌") == "zinc_lead"


def test_configurable_thresholds():
    df = pd.DataFrame({
        "symbol": ["601899", "600362"],
        "name": ["紫金矿业", "江西铜业"],
        "subsector": ["copper", "copper"],
        "avg_turnover": [20_000_000, 3_000_000],
    })
    # Default threshold 5M: both pass except 600362
    result = filter_universe(df, _make_config())
    assert len(result) == 1

    # Raised threshold 25M: only 601899 would fail too... let's use lower
    result2 = filter_universe(df, _make_config(min_daily_turnover=1_000_000))
    assert len(result2) == 2
