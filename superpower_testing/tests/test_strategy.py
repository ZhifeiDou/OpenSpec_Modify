import pytest
from quant_bot.strategy.multi_factor import MultiFactorStrategy


@pytest.fixture
def config():
    return {
        "factors": {
            "momentum": {"weight": 0.3, "lookback": 20},
            "value": {"weight": 0.3},
            "volatility": {"weight": 0.2},
            "quality": {"weight": 0.2},
        },
        "strategy": {"top_n": 2, "rebalance": "daily"},
    }


def test_score_stocks(config):
    stocks_data = {
        "stock_A": {"return_n": 0.1, "ep_ratio": 0.05, "hist_volatility": 0.2, "roe_score": 15},
        "stock_B": {"return_n": 0.2, "ep_ratio": 0.08, "hist_volatility": 0.3, "roe_score": 20},
        "stock_C": {"return_n": -0.05, "ep_ratio": 0.03, "hist_volatility": 0.15, "roe_score": 10},
    }
    strategy = MultiFactorStrategy(config)
    scores = strategy.score_stocks(stocks_data)
    assert isinstance(scores, dict)
    assert len(scores) == 3
    for s in scores.values():
        assert isinstance(s, (int, float))


def test_select_top_n(config):
    strategy = MultiFactorStrategy(config)
    scores = {"A": 0.8, "B": 0.5, "C": 0.9, "D": 0.3}
    selected = strategy.select_top_n(scores)
    assert len(selected) == 2
    assert "C" in selected
    assert "A" in selected


def test_generate_target_positions(config):
    strategy = MultiFactorStrategy(config)
    selected = ["A", "B"]
    positions = strategy.generate_target_positions(selected)
    assert len(positions) == 2
    assert abs(sum(positions.values()) - 1.0) < 1e-6
