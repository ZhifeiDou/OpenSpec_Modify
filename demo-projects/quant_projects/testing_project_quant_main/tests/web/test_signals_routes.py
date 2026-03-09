"""Unit tests for signals API routes."""
from unittest.mock import patch


class TestGetSignals:
    def test_returns_signals_with_sentiment(self, client):
        mock_signals = [
            {"symbol": "601600.SH", "name": "中国铝业", "score": 0.85, "action": "buy",
             "target_weight": 0.15, "factor_contributions": {"momentum": 0.3, "value": 0.2}},
            {"symbol": "601899.SH", "name": "紫金矿业", "score": 0.4, "action": "hold",
             "target_weight": 0.05, "factor_contributions": {}},
        ]
        mock_sentiment = {"601600.SH": "positive", "601899.SH": "neutral"}

        with patch("src.strategy.signal.generate_signals", return_value=mock_signals), \
             patch("src.strategy.signal.get_sentiment_labels", return_value=mock_sentiment):
            resp = client.get("/api/signals")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["signals"]) == 2
        assert data["signals"][0]["signal"] == "buy"
        assert data["signals"][0]["sentiment_label"] == "positive"
        assert "momentum" in data["signals"][0]["factor_contributions"]

    def test_empty_signals(self, client):
        with patch("src.strategy.signal.generate_signals", return_value=[]):
            resp = client.get("/api/signals")

        assert resp.status_code == 200
        assert resp.json()["signals"] == []

    def test_sentiment_failure_still_returns_signals(self, client):
        mock_signals = [
            {"symbol": "601600.SH", "score": 0.5, "action": "hold", "target_weight": 0.1},
        ]
        with patch("src.strategy.signal.generate_signals", return_value=mock_signals), \
             patch("src.strategy.signal.get_sentiment_labels", side_effect=Exception("API error")):
            resp = client.get("/api/signals")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["signals"]) == 1
        assert data["signals"][0]["sentiment_label"] == ""

    def test_error_returns_error(self, client):
        with patch("src.strategy.signal.generate_signals", side_effect=Exception("fail")):
            resp = client.get("/api/signals")

        assert resp.status_code == 200
        assert "error" in resp.json()
