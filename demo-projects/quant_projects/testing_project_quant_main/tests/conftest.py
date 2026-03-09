"""Shared test fixtures."""
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def config():
    """Load test configuration."""
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_stock_data():
    """Sample stock OHLCV data for testing."""
    import pandas as pd
    import numpy as np

    dates = pd.date_range("2024-01-02", periods=100, freq="B")
    np.random.seed(42)
    close = 15.0 + np.cumsum(np.random.randn(100) * 0.3)
    return pd.DataFrame({
        "date": dates,
        "open": close + np.random.randn(100) * 0.1,
        "high": close + abs(np.random.randn(100) * 0.2),
        "low": close - abs(np.random.randn(100) * 0.2),
        "close": close,
        "volume": np.random.randint(1000000, 10000000, 100),
        "amount": np.random.randint(10000000, 100000000, 100),
    })
