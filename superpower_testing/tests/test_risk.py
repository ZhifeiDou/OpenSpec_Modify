import pytest
from quant_bot.risk.manager import RiskManager


@pytest.fixture
def risk_config():
    return {
        "risk": {
            "max_position_pct": 0.3,
            "stop_loss_pct": 0.08,
            "take_profit_pct": 0.20,
        }
    }


def test_check_position_limit(risk_config):
    rm = RiskManager(risk_config)
    positions = {"A": 0.5, "B": 0.3, "C": 0.2}
    adjusted = rm.check_position_limits(positions)
    assert adjusted["A"] <= 0.3


def test_check_stop_loss(risk_config):
    rm = RiskManager(risk_config)
    holdings = {"A": {"buy_price": 10.0, "current_price": 9.0}}
    signals = rm.check_stop_loss(holdings)
    assert "A" in signals


def test_no_stop_loss_if_within_threshold(risk_config):
    rm = RiskManager(risk_config)
    holdings = {"A": {"buy_price": 10.0, "current_price": 9.5}}
    signals = rm.check_stop_loss(holdings)
    assert "A" not in signals


def test_check_take_profit(risk_config):
    rm = RiskManager(risk_config)
    holdings = {"A": {"buy_price": 10.0, "current_price": 12.5}}
    signals = rm.check_take_profit(holdings)
    assert "A" in signals
