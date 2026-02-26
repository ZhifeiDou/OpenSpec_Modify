import pytest
import pandas as pd
import numpy as np
from quant_bot.backtest.engine import BacktestEngine


@pytest.fixture
def config():
    return {
        "factors": {
            "momentum": {"weight": 0.3, "lookback": 5},
            "value": {"weight": 0.3},
            "volatility": {"weight": 0.2},
            "quality": {"weight": 0.2},
        },
        "strategy": {"top_n": 2, "rebalance": "daily"},
        "backtest": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "initial_capital": 1000000,
            "commission": 0.001,
            "slippage": 0.002,
        },
        "risk": {
            "max_position_pct": 0.5,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.20,
        },
    }


def make_mock_stock_data():
    dates = pd.date_range("2024-01-02", periods=20, freq="B")
    np.random.seed(42)
    stocks = {}
    for code in ["STOCK_A", "STOCK_B", "STOCK_C"]:
        prices = 10 + np.cumsum(np.random.randn(20) * 0.3)
        stocks[code] = pd.DataFrame({
            "date": dates.strftime("%Y-%m-%d"),
            "open": prices + np.random.randn(20) * 0.1,
            "close": prices,
            "high": prices + abs(np.random.randn(20) * 0.2),
            "low": prices - abs(np.random.randn(20) * 0.2),
            "volume": np.random.randint(1000, 10000, 20),
            "pe_ttm": np.random.uniform(8, 25, 20),
            "pb": np.random.uniform(1, 4, 20),
            "dividend_yield_ttm": np.random.uniform(0, 3, 20),
            "roe": np.random.uniform(5, 25, 20),
            "gross_margin": np.random.uniform(15, 40, 20),
        })
    return stocks


def test_backtest_runs(config):
    engine = BacktestEngine(config)
    stocks_data = make_mock_stock_data()
    stock_names = {"STOCK_A": "A", "STOCK_B": "B", "STOCK_C": "C"}
    result = engine.run(stocks_data, stock_names)
    assert "portfolio_values" in result
    assert "metrics" in result
    assert len(result["portfolio_values"]) > 0


def test_backtest_metrics(config):
    engine = BacktestEngine(config)
    stocks_data = make_mock_stock_data()
    stock_names = {"STOCK_A": "A", "STOCK_B": "B", "STOCK_C": "C"}
    result = engine.run(stocks_data, stock_names)
    metrics = result["metrics"]
    assert "annual_return" in metrics
    assert "max_drawdown" in metrics
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
