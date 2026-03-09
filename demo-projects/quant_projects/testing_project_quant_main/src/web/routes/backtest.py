"""Backtest API routes."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class BacktestRequest(BaseModel):
    start_date: str
    end_date: str
    initial_capital: float | None = None


@router.post("/run")
async def run_backtest(body: BacktestRequest, request: Request):
    """Run backtest and return results."""
    config = request.app.state.config
    try:
        from src.backtest.engine import BacktestEngine

        if body.initial_capital:
            config = {**config, "backtest": {**config.get("backtest", {}), "initial_capital": body.initial_capital}}

        engine = BacktestEngine(config)
        result = engine.run(start_date=body.start_date, end_date=body.end_date)

        metrics = result.metrics

        nav_series = []
        if result.nav_series is not None and not result.nav_series.empty:
            nav_series = [
                {"date": str(idx), "nav": float(val)}
                for idx, val in result.nav_series.items()
            ]

        trade_log = []
        if result.trade_log is not None and not result.trade_log.empty:
            trade_log = result.trade_log.to_dict(orient="records")

        # Save for later retrieval
        report_dir = Path(config.get("report", {}).get("output_dir", "reports"))
        report_dir.mkdir(parents=True, exist_ok=True)
        result.nav_series.to_csv(report_dir / "last_nav.csv")
        if not result.trade_log.empty:
            result.trade_log.to_csv(report_dir / "last_trades.csv", index=False)
        with open(report_dir / "last_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

        return {
            "status": "ok",
            "metrics": metrics,
            "nav_series": nav_series,
            "trade_log": trade_log,
        }
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}


@router.get("/latest")
async def get_latest_backtest(request: Request):
    """Return the most recent backtest result."""
    config = request.app.state.config
    report_dir = Path(config.get("report", {}).get("output_dir", "reports"))

    metrics_path = report_dir / "last_metrics.json"
    if not metrics_path.exists():
        return {"error": "No backtest results found", "detail": "Run a backtest first"}

    import pandas as pd

    with open(metrics_path) as f:
        metrics = json.load(f)

    nav_series = []
    nav_path = report_dir / "last_nav.csv"
    if nav_path.exists():
        df = pd.read_csv(nav_path, index_col=0)
        series = df.iloc[:, 0]
        nav_series = [
            {"date": str(idx), "nav": float(val)}
            for idx, val in series.items()
        ]

    trade_log = []
    trades_path = report_dir / "last_trades.csv"
    if trades_path.exists():
        trade_log = pd.read_csv(trades_path).to_dict(orient="records")

    return {
        "metrics": metrics,
        "nav_series": nav_series,
        "trade_log": trade_log,
    }
