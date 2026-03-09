"""Unit tests for report API routes."""
import json
from unittest.mock import patch

import pandas as pd


class TestGetReport:
    def test_returns_full_report(self, client, config, tmp_path):
        config["report"] = {"output_dir": str(tmp_path)}

        metrics = {"annual_return": 0.12, "sharpe_ratio": 1.5, "max_drawdown": 0.08}
        (tmp_path / "last_metrics.json").write_text(json.dumps(metrics))

        nav = pd.Series([1e6, 1.05e6, 1.02e6], index=["2024-01-02", "2024-01-03", "2024-01-04"])
        nav.to_frame("nav").to_csv(tmp_path / "last_nav.csv")

        pd.DataFrame({"date": ["2024-01-02"], "symbol": ["601600.SH"], "action": ["buy"],
                       "price": [15.0], "quantity": [1000]}).to_csv(tmp_path / "last_trades.csv", index=False)

        fm = pd.DataFrame({"momentum": [0.5, -0.2]}, index=["601600.SH", "601899.SH"])
        with patch("src.factors.base.compute_all_factors", return_value=fm):
            resp = client.get("/api/report")

        assert resp.status_code == 200
        data = resp.json()
        assert data["metrics"]["sharpe_ratio"] == 1.5
        assert len(data["nav_series"]) == 3
        assert len(data["drawdown_series"]) == 3
        assert data["drawdown_series"][0]["drawdown"] == 0.0
        assert len(data["trade_log"]) == 1
        assert len(data["factor_exposures"]) == 2

    def test_no_data_returns_error(self, client, config, tmp_path):
        config["report"] = {"output_dir": str(tmp_path)}
        resp = client.get("/api/report")

        assert resp.status_code == 200
        assert "error" in resp.json()

    def test_factor_failure_still_returns_report(self, client, config, tmp_path):
        config["report"] = {"output_dir": str(tmp_path)}
        (tmp_path / "last_metrics.json").write_text(json.dumps({"sharpe_ratio": 1.0}))

        with patch("src.factors.base.compute_all_factors", side_effect=Exception("no data")):
            resp = client.get("/api/report")

        assert resp.status_code == 200
        data = resp.json()
        assert data["metrics"]["sharpe_ratio"] == 1.0
        assert data["factor_exposures"] == []
