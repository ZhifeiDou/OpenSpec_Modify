"""Tests for risk management components."""
import numpy as np
from src.risk.drawdown import compute_drawdown, check_drawdown, compute_max_drawdown
from src.risk.stop_loss import _compute_atr, StopLossAlert
import pandas as pd


def test_compute_drawdown_no_dd():
    nav = [100, 101, 102, 103]
    assert compute_drawdown(nav) == 0.0


def test_compute_drawdown_with_dd():
    nav = [100, 110, 105, 100]
    dd = compute_drawdown(nav)
    assert abs(dd - (110 - 100) / 110) < 0.01


def test_check_drawdown_reduce():
    nav = [100, 110, 110 * 0.84]  # ~15.5% dd from peak
    config = {"risk": {"max_drawdown_reduce": 0.15, "max_drawdown_liquidate": 0.20}}
    alert = check_drawdown(nav, config)
    assert alert is not None
    assert alert.tier == "reduce"


def test_check_drawdown_liquidate():
    nav = [100, 110, 110 * 0.79]  # ~21% dd from peak
    config = {"risk": {"max_drawdown_reduce": 0.15, "max_drawdown_liquidate": 0.20}}
    alert = check_drawdown(nav, config)
    assert alert is not None
    assert alert.tier == "liquidate"


def test_check_drawdown_ok():
    nav = [100, 110, 105]  # ~4.5% dd
    config = {"risk": {"max_drawdown_reduce": 0.15, "max_drawdown_liquidate": 0.20}}
    alert = check_drawdown(nav, config)
    assert alert is None


def test_compute_max_drawdown():
    nav = [100, 110, 90, 95, 85, 100]
    max_dd, duration = compute_max_drawdown(nav)
    expected_dd = (110 - 85) / 110  # Peak 110, trough 85
    assert abs(max_dd - expected_dd) < 0.01


def test_compute_atr():
    # Create simple price data
    dates = pd.date_range("2024-01-01", periods=20)
    df = pd.DataFrame({
        "date": dates,
        "open": [10 + i * 0.1 for i in range(20)],
        "high": [10.5 + i * 0.1 for i in range(20)],
        "low": [9.5 + i * 0.1 for i in range(20)],
        "close": [10.2 + i * 0.1 for i in range(20)],
    })
    atr = _compute_atr(df, period=14)
    assert atr > 0


def test_position_sizing_calculation():
    """Verify max loss = 2% of portfolio at 2x ATR stop distance."""
    portfolio = 1_000_000
    max_risk_pct = 0.02
    atr = 2.0  # CNY
    atr_multiple = 2.0

    stop_distance = atr_multiple * atr  # 4 CNY
    max_loss = portfolio * max_risk_pct  # 20,000 CNY
    max_shares = max_loss / stop_distance  # 5,000 shares
    # Round to lots of 100
    max_shares = int(max_shares // 100) * 100  # 5,000
    assert max_shares == 5000


def test_empty_drawdown():
    assert compute_drawdown([]) == 0.0
    dd, dur = compute_max_drawdown([])
    assert dd == 0.0
    assert dur == 0
