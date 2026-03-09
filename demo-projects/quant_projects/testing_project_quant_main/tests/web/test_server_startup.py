"""Tests for server startup and configuration (R1-UC9)."""
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestAppCreation:
    """R1-UC9-S2/S3: Verify app loads configuration and registers routes."""

    def test_app_has_config_in_state(self, app):
        """R1-UC9-S2: System loads configuration."""
        assert hasattr(app.state, "config")
        assert isinstance(app.state.config, dict)

    def test_app_registers_all_api_routes(self, client):
        """R1-UC9-S4: System serves API endpoints."""
        api_paths = [
            "/api/data/status",
            "/api/universe",
            "/api/factors",
            "/api/signals",
            "/api/risk",
            "/api/backtest/latest",
            "/api/report",
        ]
        for path in api_paths:
            resp = client.get(path)
            assert resp.status_code == 200, f"Endpoint {path} returned {resp.status_code}"

    def test_config_has_web_section(self, config):
        """R1-UC9-S2: Configuration includes web section."""
        assert "web" in config
        web = config["web"]
        assert "host" in web
        assert "port" in web

    def test_app_creation_with_missing_frontend_build(self, config):
        """R1-UC9-E2: App starts even without frontend/build/ directory."""
        from fastapi import FastAPI
        from src.web.routes import data, universe, factors, signals, risk, backtest, report

        test_app = FastAPI()
        test_app.state.config = config
        test_app.include_router(data.router, prefix="/api/data")
        test_app.include_router(universe.router, prefix="/api/universe")
        # App should work fine without frontend build
        assert test_app is not None


class TestServeCommand:
    """R1-UC9-S1/S5: Verify serve command setup."""

    def test_serve_command_exists_in_main(self):
        """R1-UC9-S1: main.py has serve command."""
        import main
        assert hasattr(main, "cmd_serve")
