"""Tests for volatility regime detection module."""
import pytest

from src.risk.volatility import get_adaptive_atr_multiple, get_rebalance_regime


class TestGetAdaptiveAtrMultiple:
    """Test ATR multiple mapping based on volatility ratio."""

    def _config(self, **overrides):
        cfg = {
            "risk": {
                "atr_multiple_low_vol": 1.5,
                "atr_multiple_normal_vol": 2.0,
                "atr_multiple_high_vol": 2.5,
                "volatility_low_threshold": 0.8,
                "volatility_high_threshold": 1.5,
            }
        }
        cfg["risk"].update(overrides)
        return cfg

    def test_low_volatility(self):
        """UC-1.1: Low volatility (ratio < 0.8) tightens stop to 1.5x."""
        assert get_adaptive_atr_multiple(0.60, self._config()) == 1.5

    def test_low_volatility_very_low(self):
        assert get_adaptive_atr_multiple(0.10, self._config()) == 1.5

    def test_normal_volatility(self):
        """UC-1.3: Normal volatility keeps 2.0x."""
        assert get_adaptive_atr_multiple(1.10, self._config()) == 2.0

    def test_high_volatility(self):
        """UC-1.2: High volatility (ratio > 1.5) widens stop to 2.5x."""
        assert get_adaptive_atr_multiple(1.80, self._config()) == 2.5

    def test_boundary_low(self):
        """UC-1.5: Ratio = 0.80 exactly is normal (inclusive lower bound)."""
        assert get_adaptive_atr_multiple(0.80, self._config()) == 2.0

    def test_boundary_high(self):
        """UC-1.5: Ratio = 1.50 exactly is normal (inclusive upper bound)."""
        assert get_adaptive_atr_multiple(1.50, self._config()) == 2.0

    def test_just_below_low_boundary(self):
        assert get_adaptive_atr_multiple(0.79, self._config()) == 1.5

    def test_just_above_high_boundary(self):
        assert get_adaptive_atr_multiple(1.51, self._config()) == 2.5

    def test_default_config(self):
        """Works with empty config (uses defaults)."""
        assert get_adaptive_atr_multiple(1.0, {}) == 2.0
        assert get_adaptive_atr_multiple(0.5, {}) == 1.5
        assert get_adaptive_atr_multiple(2.0, {}) == 2.5


class TestGetRebalanceRegime:
    """Test rebalance frequency mapping based on volatility ratio."""

    def test_normal_monthly(self):
        """UC-2.1: Normal volatility keeps monthly."""
        assert get_rebalance_regime(1.20) == "monthly"

    def test_high_biweekly(self):
        """UC-2.2: High volatility switches to bi-weekly."""
        assert get_rebalance_regime(1.80) == "biweekly"

    def test_extreme_weekly(self):
        """UC-2.3: Extreme volatility switches to weekly."""
        assert get_rebalance_regime(2.30) == "weekly"

    def test_boundary_biweekly(self):
        """Ratio = 1.5 is still monthly (not exceeded)."""
        assert get_rebalance_regime(1.50) == "monthly"

    def test_boundary_weekly(self):
        """Ratio = 2.0 is still biweekly (not exceeded)."""
        assert get_rebalance_regime(2.00) == "biweekly"

    def test_just_above_biweekly(self):
        assert get_rebalance_regime(1.51) == "biweekly"

    def test_just_above_weekly(self):
        assert get_rebalance_regime(2.01) == "weekly"
