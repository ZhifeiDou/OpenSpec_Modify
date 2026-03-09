"""Unit tests for factors API routes."""
from unittest.mock import patch
import pandas as pd


class TestGetFactors:
    def test_returns_matrix_and_categories(self, client):
        fm = pd.DataFrame(
            {"momentum_20d": [0.5, -0.2], "value_pe": [1.1, 0.8]},
            index=["601600.SH", "601899.SH"],
        )
        with patch("src.factors.base.compute_all_factors", return_value=fm):
            resp = client.get("/api/factors")

        assert resp.status_code == 200
        data = resp.json()
        assert len(data["matrix"]) == 2
        assert data["matrix"][0]["symbol"] == "601600.SH"

    def test_empty_matrix(self, client):
        with patch("src.factors.base.compute_all_factors", return_value=pd.DataFrame()):
            resp = client.get("/api/factors")

        assert resp.status_code == 200
        data = resp.json()
        assert data["matrix"] == []

    def test_error_returns_error(self, client):
        with patch("src.factors.base.compute_all_factors", side_effect=Exception("no data")):
            resp = client.get("/api/factors")

        assert resp.status_code == 200
        assert "error" in resp.json()


class TestComputeFactors:
    def test_compute_returns_matrix(self, client):
        fm = pd.DataFrame(
            {"momentum_20d": [0.5]},
            index=["601600.SH"],
        )
        with patch("src.factors.base.compute_all_factors", return_value=fm):
            resp = client.post("/api/factors/compute")

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert len(data["matrix"]) == 1
        assert data["shape"] == [1, 1]

    def test_compute_error(self, client):
        with patch("src.factors.base.compute_all_factors", side_effect=Exception("fail")):
            resp = client.post("/api/factors/compute")

        assert resp.status_code == 200
        assert "error" in resp.json()
