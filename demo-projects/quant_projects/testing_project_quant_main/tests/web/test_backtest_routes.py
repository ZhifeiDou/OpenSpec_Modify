"""Unit tests for backtest API routes."""
import json
from unittest.mock import patch, MagicMock

import pandas as pd


class TestRunBacktest:
    def test_run_returns_results(self, client, config, tmp_path):
        mock_result = MagicMock()
        mock_result.metrics = {"annual_return": 0.12, "sharpe_ratio": 1.5, "max_drawdown": 0.08, "win_rate": 0.6}
        mock_result.nav_series = pd.Series([1e6, 1.05e6, 1.1e6], index=["2024-01-02", "2024-01-03", "2024-01-04"])
        mock_result.trade_log = pd.DataFrame({
            "date": ["2024-01-02"], "symbol": ["601600.SH"], "action": ["buy"],
            "price": [15.0], "quantity": [1000],
        })

        config["report"] = {"output_dir": str(tmp_path)}

        with patch("src.backtest.engine.BacktestEngine") as MockEngine:
            MockEngine.return_value.run.return_value = mock_result
            resp = client.post("/api/backtest/run", json={
                "start_date": "2024-01-01", "end_date": "2024-12-31", "initial_capital": 1000000
            })

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["metrics"]["annual_return"] == 0.12
        assert len(data["nav_series"]) == 3
        assert len(data["trade_log"]) == 1

    def test_run_error(self, client):
        with patch("src.backtest.engine.BacktestEngine") as MockEngine:
            MockEngine.return_value.run.side_effect = Exception("insufficient data")
            resp = client.post("/api/backtest/run", json={
                "start_date": "2024-01-01", "end_date": "2024-12-31"
            })

        assert resp.status_code == 200
        assert "error" in resp.json()


class TestGetLatestBacktest:
    def test_returns_latest_result(self, client, config, tmp_path):
        config["report"] = {"output_dir": str(tmp_path)}

        (tmp_path / "last_metrics.json").write_text(json.dumps({"sharpe_ratio": 1.2}))
        nav_df = pd.DataFrame({"nav": [1e6, 1.05e6]}, index=["2024-01-02", "2024-01-03"])
        nav_df.to_csv(tmp_path / "last_nav.csv")
        pd.DataFrame({"date": ["2024-01-02"], "symbol": ["601600.SH"], "action": ["buy"],
                       "price": [15.0], "quantity": [1000]}).to_csv(tmp_path / "last_trades.csv", index=False)

        resp = client.get("/api/backtest/latest")

        assert resp.status_code == 200
        data = resp.json()
        assert data["metrics"]["sharpe_ratio"] == 1.2
        assert len(data["nav_series"]) == 2

    def test_no_results_returns_error(self, client, config, tmp_path):
        config["report"] = {"output_dir": str(tmp_path)}
        resp = client.get("/api/backtest/latest")

        assert resp.status_code == 200
        assert "error" in resp.json()
