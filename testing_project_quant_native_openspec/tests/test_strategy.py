"""Tests for scoring, selection, and allocation."""

import pytest
import pandas as pd
from src.strategy.scorer import equal_weight_score
from src.strategy.selector import select_top_stocks
from src.strategy.allocator import allocate_positions


class TestScoring:
    def test_equal_weight_score(self):
        factor_df = pd.DataFrame({
            "metal_momentum": [0.5, -0.3, 0.8],
            "momentum": [0.2, 0.5, -0.1],
        }, index=["A", "B", "C"])
        weights = {"commodity": 0.35, "technical": 0.20}
        scores = equal_weight_score(factor_df, weights)
        assert len(scores) == 3
        assert scores["C"] != scores["A"]  # different scores


class TestSelection:
    def test_select_top_stocks(self):
        scores = pd.Series({"A": 5, "B": 3, "C": 8, "D": 1, "E": 6})
        selected = select_top_stocks(scores, top_percent=0.4, max_stocks=10)
        assert "C" in selected
        assert "E" in selected
        assert len(selected) == 2

    def test_max_stocks_limit(self):
        scores = pd.Series({f"S{i}": i for i in range(20)})
        selected = select_top_stocks(scores, top_percent=0.5, max_stocks=5)
        assert len(selected) == 5


class TestAllocation:
    def test_basic_allocation(self):
        scores = pd.Series({"A": 3, "B": 2, "C": 1})
        selected = ["A", "B", "C"]
        subsectors = {"A": "copper", "B": "aluminum", "C": "gold"}
        weights = allocate_positions(scores, selected, subsectors)
        assert abs(sum(weights.values()) - 1.0) < 0.01
        assert weights["A"] > weights["C"]

    def test_single_stock_cap(self):
        scores = pd.Series({"A": 100, "B": 1})
        selected = ["A", "B"]
        subsectors = {"A": "copper", "B": "aluminum"}
        weights = allocate_positions(scores, selected, subsectors, single_max=0.10)
        # After capping and renormalization, both should sum to 1.0
        assert abs(sum(weights.values()) - 1.0) < 0.01
