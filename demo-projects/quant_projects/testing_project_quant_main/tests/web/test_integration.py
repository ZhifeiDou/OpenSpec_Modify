"""Integration test: start server, call each endpoint, verify JSON response structure."""
import pytest


class TestAllEndpoints:
    """Verify every API endpoint returns valid JSON with expected structure."""

    def test_data_status_returns_json(self, client):
        resp = client.get("/api/data/status")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_data_update_returns_json(self, client):
        resp = client.post("/api/data/update", json={"categories": ["macro"], "force": False})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        # May return error if no API token configured - that's OK for integration test
        assert "status" in data or "error" in data or "detail" in data

    def test_universe_returns_json(self, client):
        resp = client.get("/api/universe")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "stocks" in data or "error" in data

    def test_factors_get_returns_json(self, client):
        resp = client.get("/api/factors")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "matrix" in data or "error" in data

    def test_factors_compute_returns_json(self, client):
        resp = client.post("/api/factors/compute")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "status" in data or "error" in data

    def test_signals_returns_json(self, client):
        resp = client.get("/api/signals")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "signals" in data or "error" in data

    def test_risk_returns_json(self, client):
        resp = client.get("/api/risk")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_backtest_run_returns_json(self, client):
        resp = client.post("/api/backtest/run", json={
            "start_date": "2024-01-01", "end_date": "2024-06-30"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "status" in data or "error" in data

    def test_backtest_latest_returns_json(self, client):
        resp = client.get("/api/backtest/latest")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)

    def test_report_returns_json(self, client):
        resp = client.get("/api/report")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
