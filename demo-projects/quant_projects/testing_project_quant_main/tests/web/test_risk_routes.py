"""Unit tests for risk API routes."""
from unittest.mock import patch


class TestGetRisk:
    def test_returns_risk_data(self, client):
        mock_report = {
            "drawdown": 0.08,
            "stop_loss_alerts": [{"symbol": "601600.SH", "msg": "approaching stop"}],
            "metal_crash_alerts": [],
            "positions": [
                {"symbol": "601600.SH", "weight": 0.15, "stop_price": 12.5, "distance_to_stop": 5.2},
            ],
        }
        with patch("src.risk.alerts.run_daily_risk_check", return_value=mock_report):
            resp = client.get("/api/risk")

        assert resp.status_code == 200
        data = resp.json()
        assert data["drawdown"] == 0.08
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["type"] == "stop_loss"
        assert len(data["positions"]) == 1

    def test_no_alerts(self, client):
        mock_report = {
            "drawdown": 0.02,
            "stop_loss_alerts": [],
            "metal_crash_alerts": [],
            "positions": [],
        }
        with patch("src.risk.alerts.run_daily_risk_check", return_value=mock_report):
            resp = client.get("/api/risk")

        assert resp.status_code == 200
        data = resp.json()
        assert data["alerts"] == []

    def test_critical_metal_crash(self, client):
        mock_report = {
            "drawdown": 0.15,
            "stop_loss_alerts": [],
            "metal_crash_alerts": [{"metal": "copper", "drop": -0.08}],
            "positions": [],
        }
        with patch("src.risk.alerts.run_daily_risk_check", return_value=mock_report):
            resp = client.get("/api/risk")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["severity"] == "critical"

    def test_error_returns_error(self, client):
        with patch("src.risk.alerts.run_daily_risk_check", side_effect=Exception("fail")):
            resp = client.get("/api/risk")

        assert resp.status_code == 200
        assert "error" in resp.json()
