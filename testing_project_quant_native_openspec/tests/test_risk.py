"""Tests for risk management: stop-loss, drawdown, position sizing."""

import pytest
import pandas as pd
import numpy as np
from src.risk.stop_loss import check_hard_stop_loss, check_trailing_stop, calculate_atr
from src.risk.drawdown import DrawdownController
from src.risk.position_sizing import calculate_position_size
from src.risk.alerts import MetalCrashAlert


class TestStopLoss:
    def test_hard_stop_loss_triggered(self):
        assert check_hard_stop_loss(
            current_price=9.0, entry_price=10.0, atr=0.4, multiplier=2.0
        ) is True

    def test_hard_stop_loss_not_triggered(self):
        assert check_hard_stop_loss(
            current_price=9.5, entry_price=10.0, atr=0.4, multiplier=2.0
        ) is False

    def test_trailing_stop_not_active(self):
        active, triggered = check_trailing_stop(
            current_price=10.5, entry_price=10.0, peak_price=10.5,
            activation_gain=0.10
        )
        assert active is False
        assert triggered is False

    def test_trailing_stop_active_not_triggered(self):
        active, triggered = check_trailing_stop(
            current_price=11.5, entry_price=10.0, peak_price=12.0,
            activation_gain=0.10, drawdown_trigger=0.08
        )
        assert active is True
        assert triggered is False

    def test_trailing_stop_triggered(self):
        active, triggered = check_trailing_stop(
            current_price=10.9, entry_price=10.0, peak_price=12.0,
            activation_gain=0.10, drawdown_trigger=0.08
        )
        assert active is True
        assert triggered is True

    def test_atr_calculation(self):
        data = pd.DataFrame({
            "high": [11, 11.5, 12, 11.8, 12.2] * 4,
            "low": [9.5, 10, 10.5, 10.2, 10.8] * 4,
            "close": [10, 10.5, 11, 10.8, 11.5] * 4,
        })
        atr = calculate_atr(data, period=14)
        assert atr > 0


class TestDrawdown:
    def test_no_drawdown(self):
        dc = DrawdownController()
        dc.update(100)
        result = dc.check(100)
        assert result["level"] == 0
        assert result["action"] == "hold"

    def test_level1_drawdown(self):
        dc = DrawdownController(level1_threshold=0.15)
        dc.update(100)
        result = dc.check(84)
        assert result["level"] == 1
        assert result["position_multiplier"] == 0.5

    def test_level2_drawdown(self):
        dc = DrawdownController(level2_threshold=0.20)
        dc.update(100)
        result = dc.check(79)
        assert result["level"] == 2
        assert result["position_multiplier"] == 0.0


class TestPositionSizing:
    def test_basic_position_size(self):
        shares = calculate_position_size(
            portfolio_value=1_000_000, max_loss_pct=0.02,
            atr=0.5, atr_multiplier=2.0, stock_price=10.0
        )
        assert shares > 0
        assert shares % 100 == 0  # A-share lot size

    def test_zero_atr(self):
        shares = calculate_position_size(
            portfolio_value=1_000_000, max_loss_pct=0.02,
            atr=0.0, stock_price=10.0
        )
        assert shares == 0


class TestMetalAlert:
    def test_crash_alert_triggered(self):
        alert = MetalCrashAlert(daily_drop_threshold=0.03)
        prices = {
            "copper": pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "close": [100.0, 96.0],  # 4% drop
            })
        }
        alerts = alert.check(prices)
        assert len(alerts) == 1
        assert alerts[0]["metal"] == "copper"

    def test_no_alert_small_drop(self):
        alert = MetalCrashAlert(daily_drop_threshold=0.03)
        prices = {
            "copper": pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "close": [100.0, 98.0],  # 2% drop
            })
        }
        alerts = alert.check(prices)
        assert len(alerts) == 0
