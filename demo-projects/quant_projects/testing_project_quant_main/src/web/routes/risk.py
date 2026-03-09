"""Risk monitoring API routes."""
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def get_risk(request: Request):
    """Return current risk status."""
    config = request.app.state.config
    try:
        from src.risk.alerts import run_daily_risk_check

        report = run_daily_risk_check(config)
        return {
            "drawdown": report.get("drawdown", 0),
            "alerts": [
                *[{"type": "stop_loss", "severity": "warning", "detail": a}
                  for a in report.get("stop_loss_alerts", [])],
                *[{"type": "metal_crash", "severity": "critical", "detail": a}
                  for a in report.get("metal_crash_alerts", [])],
            ],
            "positions": report.get("positions", []),
        }
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}
