"""Tests for multi-factor scoring and allocation."""
import numpy as np
import pandas as pd
from src.strategy.scorer import score_stocks, select_top_stocks, _equal_weighted
from src.strategy.allocator import allocate_weights


def _make_config(mode="equal_weight"):
    return {
        "factors": {
            "weights": {
                "commodity": 0.35,
                "fundamental": 0.25,
                "technical": 0.20,
                "flow": 0.15,
                "macro": 0.05,
            },
            "scoring_mode": mode,
            "winsorize_mad_multiple": 3.0,
        },
        "strategy": {
            "max_stocks": 3,
            "top_ratio": 0.5,
            "max_single_weight": 0.40,
            "max_subsector_weight": 0.60,
            "skip_rebalance_threshold": 0.02,
        },
    }


def test_equal_weight_scoring():
    # Use registered factor names to get proper weights
    import src.factors.fundamental  # noqa: F401 - trigger registration
    import src.factors.technical  # noqa: F401
    from src.factors.base import get_registered_factors
    registry = get_registered_factors()
    # Pick two real factor names
    names = list(registry.keys())[:2] if len(registry) >= 2 else ["f1", "f2"]
    factor_matrix = pd.DataFrame({
        names[0]: [1.0, 0.5, -0.3, 0.8, -1.0],
        names[1]: [0.2, -0.1, 0.5, 0.3, 0.0],
    }, index=["A", "B", "C", "D", "E"])
    config = _make_config()
    scores = score_stocks(factor_matrix, config)
    assert len(scores) == 5
    # Stock A has highest combined factor values
    assert scores["A"] > scores["E"]


def test_select_top_stocks():
    scores = pd.Series({"A": 2.0, "B": 1.5, "C": 0.5, "D": -0.1, "E": -1.0})
    config = _make_config()
    selected = select_top_stocks(scores, config, universe_size=5)
    assert len(selected) <= 3
    assert "A" in selected
    assert "B" in selected


def test_allocate_single_stock_cap():
    scores = pd.Series({"A": 10.0, "B": 1.0, "C": 1.0})
    config = _make_config()
    weights = allocate_weights(["A", "B", "C"], scores, config)
    # A would get ~83% without cap, should be clipped to 40%
    assert weights["A"] <= 0.41  # Allow small floating point margin


def test_allocate_subsector_cap():
    scores = pd.Series({"A": 1.0, "B": 1.0, "C": 1.0, "D": 1.0})
    config = _make_config()
    subsector_map = {"A": "copper", "B": "copper", "C": "copper", "D": "aluminum"}
    weights = allocate_weights(
        ["A", "B", "C", "D"], scores, config, subsector_map=subsector_map
    )
    copper_weight = weights["A"] + weights["B"] + weights["C"]
    assert copper_weight <= 0.61  # sub-sector cap 60% + margin


def test_allocate_with_position_ratio():
    scores = pd.Series({"A": 1.0, "B": 1.0})
    config = _make_config()
    weights = allocate_weights(["A", "B"], scores, config, position_ratio=0.6)
    assert abs(weights.sum() - 0.6) < 0.01


def test_empty_scores():
    scores = pd.Series(dtype=float)
    config = _make_config()
    selected = select_top_stocks(scores, config)
    assert selected == []
