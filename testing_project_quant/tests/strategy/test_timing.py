"""Tests for market timing logic."""
from src.strategy.timing import _determine_position_ratio, compute_timing_signal
import numpy as np


def test_both_positive():
    assert _determine_position_ratio(0.05, 0.10) == 1.0


def test_early_recovery():
    assert _determine_position_ratio(0.05, -0.03) == 0.6


def test_weakening_trend():
    assert _determine_position_ratio(-0.02, 0.05) == 0.3


def test_both_negative():
    assert _determine_position_ratio(-0.05, -0.10) == 0.2


def test_nan_fallback():
    assert _determine_position_ratio(np.nan, 0.05) == 0.6
    assert _determine_position_ratio(0.05, np.nan) == 0.6


def test_override_ratio():
    config = {"timing": {"override_ratio": 0.5}}
    result = compute_timing_signal(config)
    assert result["position_ratio"] == 0.5
    assert result["details"]["override"] is True


def test_timing_disabled():
    config = {"timing": {"enabled": False}}
    result = compute_timing_signal(config)
    assert result["position_ratio"] == 1.0
