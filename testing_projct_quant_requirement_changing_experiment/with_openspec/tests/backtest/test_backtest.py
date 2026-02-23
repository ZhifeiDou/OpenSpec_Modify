"""Tests for backtest engine components."""
import numpy as np
import pandas as pd
from src.backtest.portfolio import Portfolio, Holding
from src.backtest.metrics import compute_metrics


def test_portfolio_buy():
    p = Portfolio(initial_capital=100_000)
    cost = p.buy("SH600000", 1000, 10.0, "2024-01-02")
    assert cost == 10_000
    assert p.cash == 90_000
    assert "SH600000" in p.holdings
    assert p.holdings["SH600000"].shares == 1000


def test_portfolio_sell():
    p = Portfolio(initial_capital=100_000)
    p.buy("SH600000", 1000, 10.0, "2024-01-02")
    proceeds = p.sell("SH600000", 500, 11.0)
    assert proceeds == 5_500
    assert p.holdings["SH600000"].shares == 500


def test_portfolio_sell_all():
    p = Portfolio(initial_capital=100_000)
    p.buy("SH600000", 1000, 10.0, "2024-01-02")
    p.sell("SH600000", 1000, 11.0)
    assert "SH600000" not in p.holdings


def test_portfolio_nav():
    p = Portfolio(initial_capital=100_000)
    p.buy("SH600000", 1000, 10.0, "2024-01-02")
    p.update_prices({"SH600000": 12.0})
    # Cash = 90k, Holdings = 1000 * 12 = 12k
    assert abs(p.nav - 102_000) < 1


def test_portfolio_record_nav():
    p = Portfolio(initial_capital=100_000)
    p.record_nav("2024-01-01")
    p.record_nav("2024-01-02")
    assert len(p.nav_history) == 2


def test_compute_metrics_basic():
    # Simple NAV series: 100k → 110k over 252 days
    nav = pd.Series(
        np.linspace(100_000, 110_000, 252),
        index=[f"2024-{i//22+1:02d}-{i%22+1:02d}" for i in range(252)],
    )
    config = {"backtest": {"risk_free_rate": 0.02}}
    metrics = compute_metrics(nav, pd.DataFrame(), 100_000, config)
    assert metrics["annual_return"] > 0
    assert metrics["max_drawdown"] >= 0
    assert metrics["n_trading_days"] == 252


def test_compute_metrics_empty():
    nav = pd.Series(dtype=float)
    config = {"backtest": {"risk_free_rate": 0.02}}
    metrics = compute_metrics(nav, pd.DataFrame(), 100_000, config)
    assert metrics["annual_return"] == 0.0


def test_portfolio_weights():
    p = Portfolio(initial_capital=100_000)
    p.buy("A", 500, 10.0, "2024-01-02")
    p.buy("B", 500, 10.0, "2024-01-02")
    p.update_prices({"A": 10.0, "B": 10.0})
    weights = p.get_weights()
    assert abs(weights["A"] - weights["B"]) < 0.01  # Equal weights


def test_portfolio_insufficient_cash():
    p = Portfolio(initial_capital=1000)
    cost = p.buy("A", 10000, 10.0, "2024-01-02")
    # Should buy what it can afford
    if cost > 0:
        assert p.holdings["A"].shares <= 100  # max affordable at lots of 100
