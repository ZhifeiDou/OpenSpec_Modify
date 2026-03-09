"""Unit tests for universe API routes."""
from unittest.mock import patch
import pandas as pd


class TestGetUniverse:
    def test_returns_stocks_and_subsectors(self, client):
        mock_df = pd.DataFrame({
            "symbol": ["601600.SH", "601899.SH"],
            "name": ["中国铝业", "紫金矿业"],
            "subsector": ["铝", "黄金"],
        })
        with patch("src.universe.classifier.get_universe", return_value=mock_df):
            resp = client.get("/api/universe")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["stocks"]) == 2
        assert "subsector_counts" in data

    def test_filter_by_subsector(self, client):
        mock_df = pd.DataFrame({
            "symbol": ["601600.SH", "601899.SH", "600362.SH"],
            "name": ["中国铝业", "紫金矿业", "江西铜业"],
            "subsector": ["铝", "黄金", "铜"],
        })
        with patch("src.universe.classifier.get_universe", return_value=mock_df):
            resp = client.get("/api/universe?subsector=铝")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["stocks"]) == 1
        assert data["stocks"][0]["symbol"] == "601600.SH"

    def test_empty_universe(self, client):
        with patch("src.universe.classifier.get_universe", return_value=pd.DataFrame()):
            resp = client.get("/api/universe")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stocks"] == []

    def test_filter_returns_empty_when_no_match(self, client):
        """R1-UC3-E2: Filter returns no results."""
        mock_df = pd.DataFrame({
            "symbol": ["601600.SH"],
            "name": ["中国铝业"],
            "subsector": ["铝"],
        })
        with patch("src.universe.classifier.get_universe", return_value=mock_df):
            resp = client.get("/api/universe?subsector=不存在的板块")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stocks"] == []

    def test_error_returns_error_message(self, client):
        with patch("src.universe.classifier.get_universe", side_effect=Exception("no data")):
            resp = client.get("/api/universe")

        assert resp.status_code == 200
        assert "error" in resp.json()
