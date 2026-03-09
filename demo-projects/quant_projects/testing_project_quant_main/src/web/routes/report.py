"""Report API routes."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def get_report(request: Request):
    """Return structured report data for frontend rendering."""
    config = request.app.state.config
    report_dir = Path(config.get("report", {}).get("output_dir", "reports"))

    import pandas as pd
    import numpy as np

    # Load metrics
    metrics = None
    metrics_path = report_dir / "last_metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            metrics = json.load(f)

    # Load NAV series
    nav_series = []
    drawdown_series = []
    nav_path = report_dir / "last_nav.csv"
    if nav_path.exists():
        df = pd.read_csv(nav_path, index_col=0)
        series = df.iloc[:, 0]
        nav_series = [
            {"date": str(idx), "nav": float(val)}
            for idx, val in series.items()
        ]
        # Compute drawdown series
        nav_arr = series.values
        peak = np.maximum.accumulate(nav_arr)
        dd = (nav_arr - peak) / peak
        drawdown_series = [
            {"date": str(idx), "drawdown": float(d)}
            for idx, d in zip(series.index, dd)
        ]

    # Load trade log
    trade_log = []
    trades_path = report_dir / "last_trades.csv"
    if trades_path.exists():
        trade_log = pd.read_csv(trades_path).to_dict(orient="records")

    # Load factor exposures if available
    factor_exposures = []
    try:
        from src.factors.base import compute_all_factors
        fm = compute_all_factors(config)
        if not fm.empty:
            factor_exposures = fm.reset_index().rename(columns={"index": "symbol"}).fillna(0).to_dict(orient="records")
    except Exception:
        pass

    if not metrics and not nav_series:
        return {"error": "No report data available", "detail": "Run a backtest first"}

    return {
        "metrics": metrics,
        "nav_series": nav_series,
        "drawdown_series": drawdown_series,
        "trade_log": trade_log,
        "factor_exposures": factor_exposures,
    }
