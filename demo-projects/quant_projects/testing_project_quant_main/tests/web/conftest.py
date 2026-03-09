"""Shared fixtures for web API tests."""
import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient


@pytest.fixture
def config():
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def app(config):
    """Create a fresh FastAPI app for testing (no static file mount)."""
    from fastapi import FastAPI
    from src.web.routes import data, universe, factors, signals, risk, backtest, report

    test_app = FastAPI()
    test_app.state.config = config
    test_app.include_router(data.router, prefix="/api/data")
    test_app.include_router(universe.router, prefix="/api/universe")
    test_app.include_router(factors.router, prefix="/api/factors")
    test_app.include_router(signals.router, prefix="/api/signals")
    test_app.include_router(risk.router, prefix="/api/risk")
    test_app.include_router(backtest.router, prefix="/api/backtest")
    test_app.include_router(report.router, prefix="/api/report")
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)
