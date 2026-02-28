import os
import pytest
from quant_bot.utils.helpers import load_config


def test_load_config():
    config = load_config()
    assert "stock_pool" in config
    assert "factors" in config
    assert config["stock_pool"]["sector"] == "有色金属"
    assert config["strategy"]["top_n"] == 5


def test_load_config_custom_path():
    config = load_config("config/config.yaml")
    assert config["backtest"]["initial_capital"] == 1000000
