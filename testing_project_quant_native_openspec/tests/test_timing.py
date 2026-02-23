"""Tests for timing signals and composite multiplier."""

import pytest
import pandas as pd
from src.timing.gold_hedge import gold_hedge_signal
from src.timing.pmi_signal import pmi_timing_signal
from src.timing.composite import composite_timing_signal


class TestGoldHedge:
    def test_risk_off_signal(self):
        prices = pd.DataFrame({
            "date": [f"2024-01-{i:02d}" for i in range(1, 25)],
            "close": list(range(100, 124)),  # strong uptrend >5%
        })
        result = gold_hedge_signal(prices, momentum_window=20, threshold=0.05)
        assert result["signal"] == "risk-off"
        assert result["multiplier"] < 1.0

    def test_neutral_signal(self):
        prices = pd.DataFrame({
            "date": [f"2024-01-{i:02d}" for i in range(1, 25)],
            "close": [100] * 24,  # flat
        })
        result = gold_hedge_signal(prices, momentum_window=20, threshold=0.05)
        assert result["signal"] == "neutral"
        assert result["multiplier"] == 1.0

    def test_insufficient_data(self):
        prices = pd.DataFrame({"date": ["2024-01-01"], "close": [100]})
        result = gold_hedge_signal(prices, momentum_window=20)
        assert result["multiplier"] == 1.0


class TestPMISignal:
    def test_bullish_signal(self):
        pmi = pd.DataFrame({"date": ["2024-01", "2024-02"], "pmi": [50.5, 51.2]})
        result = pmi_timing_signal(pmi)
        assert result["signal"] == "bullish"
        assert result["multiplier"] == 1.0

    def test_bearish_signal(self):
        pmi = pd.DataFrame({"date": ["2024-01", "2024-02"], "pmi": [49.5, 48.8]})
        result = pmi_timing_signal(pmi)
        assert result["signal"] == "bearish"
        assert result["multiplier"] < 1.0


class TestCompositeSignal:
    def test_combined_caution(self):
        signals = [
            {"signal": "risk-off", "multiplier": 0.7},
            {"signal": "bearish", "multiplier": 0.7},
        ]
        result = composite_timing_signal(signals)
        assert abs(result["multiplier"] - 0.49) < 0.01

    def test_timing_disabled(self):
        signals = [{"signal": "risk-off", "multiplier": 0.7}]
        result = composite_timing_signal(signals, enabled=False)
        assert result["multiplier"] == 1.0
