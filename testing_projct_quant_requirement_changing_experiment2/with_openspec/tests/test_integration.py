"""End-to-end integration test: full pipeline with synthetic data."""
import os
import tempfile
import numpy as np
import pandas as pd
import pytest

from src.data.storage import DataStore
from src.backtest.portfolio import Portfolio
from src.backtest.metrics import compute_metrics
from src.factors.standardizer import cross_sectional_standardize
from src.strategy.scorer import score_stocks, select_top_stocks
from src.strategy.allocator import allocate_weights
from src.strategy.timing import _determine_position_ratio
from src.risk.drawdown import compute_drawdown, check_drawdown


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SQLite database with synthetic data."""
    db_path = str(tmp_path / "test.db")
    store = DataStore(db_path)

    # Insert synthetic stock daily data
    dates = pd.date_range("2023-01-01", "2024-12-31", freq="B")
    symbols = ["SH601899", "SH603993", "SH600362", "SH601600", "SH600489"]

    for sym in symbols:
        np.random.seed(hash(sym) % 2**31)
        n = len(dates)
        base_price = np.random.uniform(5, 50)
        returns = np.random.normal(0.0003, 0.02, n)
        prices = base_price * np.cumprod(1 + returns)

        df = pd.DataFrame({
            "symbol": sym,
            "date": [d.strftime("%Y-%m-%d") for d in dates],
            "open": prices * np.random.uniform(0.98, 1.0, n),
            "high": prices * np.random.uniform(1.0, 1.03, n),
            "low": prices * np.random.uniform(0.97, 1.0, n),
            "close": prices,
            "volume": np.random.uniform(1e6, 5e7, n),
            "amount": prices * np.random.uniform(1e7, 5e8, n),
        })
        store.save_dataframe("stock_daily", df)

    # Insert futures data
    for metal in ["cu", "al", "au", "ni", "zn"]:
        np.random.seed(hash(metal) % 2**31)
        n = len(dates)
        base = np.random.uniform(1000, 80000)
        returns = np.random.normal(0.0002, 0.015, n)
        prices = base * np.cumprod(1 + returns)

        df = pd.DataFrame({
            "metal": metal,
            "date": [d.strftime("%Y-%m-%d") for d in dates],
            "open": prices * 0.99,
            "high": prices * 1.01,
            "low": prices * 0.98,
            "close": prices,
            "settle": prices * 1.001,
            "volume": np.random.uniform(1e4, 1e6, n),
            "open_interest": np.random.uniform(1e5, 1e6, n),
        })
        store.save_dataframe("futures_daily", df)

    return store, db_path


@pytest.fixture
def config(tmp_db):
    store, db_path = tmp_db
    return {
        "data": {"db_path": db_path},
        "universe": {
            "industry_code": "801050",
            "min_listing_days": 60,
            "min_daily_turnover": 0,  # Accept all in test
        },
        "factors": {
            "weights": {
                "commodity": 0.35,
                "fundamental": 0.25,
                "technical": 0.20,
                "flow": 0.15,
                "macro": 0.05,
            },
            "scoring_mode": "equal_weight",
            "winsorize_mad_multiple": 3.0,
            "small_universe_warning": 3,
        },
        "strategy": {
            "max_stocks": 3,
            "top_ratio": 0.5,
            "max_single_weight": 0.40,
            "max_subsector_weight": 0.60,
            "rebalance_freq": "monthly",
            "skip_rebalance_threshold": 0.02,
        },
        "timing": {"enabled": False},
        "risk": {
            "hard_stop_atr_multiple": 2.0,
            "trailing_stop_activation": 0.10,
            "trailing_stop_drop": 0.08,
            "max_risk_per_stock": 0.02,
            "max_drawdown_reduce": 0.15,
            "max_drawdown_liquidate": 0.20,
            "metal_crash_threshold": 0.03,
        },
        "backtest": {
            "initial_capital": 1_000_000,
            "stamp_tax": 0.0005,
            "commission": 0.0003,
            "min_commission": 5,
            "slippage": 0.0015,
            "risk_free_rate": 0.02,
        },
        "report": {"format": "html", "output_dir": "reports"},
    }


def test_factor_pipeline(tmp_db, config):
    """Test: standardize synthetic factor data."""
    raw = pd.DataFrame({
        "f1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "f2": [10.0, 20.0, 30.0, 40.0, 50.0],
    }, index=["A", "B", "C", "D", "E"])

    result = cross_sectional_standardize(raw, mad_multiple=3.0)
    assert result.shape == raw.shape
    assert abs(result["f1"].mean()) < 0.1


def test_scoring_pipeline(config):
    """Test: score → select → allocate full pipeline."""
    factor_matrix = pd.DataFrame({
        "f1": [1.5, 0.3, -0.5, 0.8, -1.2],
        "f2": [0.8, -0.2, 1.0, 0.1, 0.5],
    }, index=["A", "B", "C", "D", "E"])

    scores = score_stocks(factor_matrix, config)
    assert len(scores) == 5

    selected = select_top_stocks(scores, config, universe_size=5)
    assert len(selected) > 0

    weights = allocate_weights(selected, scores, config)
    assert abs(weights.sum() - 1.0) < 0.01


def test_timing_signal():
    """Test: timing determines correct position ratios."""
    assert _determine_position_ratio(0.05, 0.10) == 1.0
    assert _determine_position_ratio(0.05, -0.03) == 0.6
    assert _determine_position_ratio(-0.02, 0.05) == 0.3
    assert _determine_position_ratio(-0.05, -0.10) == 0.2


def test_risk_pipeline(config):
    """Test: drawdown detection and tiered response."""
    nav = [100, 110, 95, 90, 88]  # ~20% dd from peak of 110
    dd = compute_drawdown(nav)
    assert dd > 0.15

    alert = check_drawdown(nav, config)
    assert alert is not None
    assert alert.tier in ("reduce", "liquidate")


def test_portfolio_roundtrip():
    """Test: buy → price update → sell → verify NAV."""
    p = Portfolio(initial_capital=100_000)
    p.buy("A", 1000, 10.0, "2024-01-01")
    p.update_prices({"A": 12.0})
    assert p.nav > 100_000

    p.sell("A", 1000, 12.0)
    assert len(p.holdings) == 0
    assert p.cash > 100_000  # Made profit


def test_metrics_calculation():
    """Test: metrics computed on synthetic NAV series."""
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.01, 252)
    nav_values = 100_000 * np.cumprod(1 + returns)
    nav = pd.Series(nav_values, index=[f"d{i}" for i in range(252)])

    metrics = compute_metrics(nav, pd.DataFrame(), 100_000,
                              {"backtest": {"risk_free_rate": 0.02}})
    assert "annual_return" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics
    assert metrics["n_trading_days"] == 252
