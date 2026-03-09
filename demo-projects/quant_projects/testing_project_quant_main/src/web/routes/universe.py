"""Universe API routes."""
from __future__ import annotations

from fastapi import APIRouter, Request, Query

router = APIRouter()


@router.get("")
async def get_universe(request: Request, subsector: str | None = Query(None)):
    """Return the current stock universe as JSON."""
    config = request.app.state.config
    try:
        from src.universe.classifier import get_universe as _get_universe

        universe = _get_universe(config)
        if universe.empty:
            return {"stocks": [], "subsector_counts": {}}

        if subsector:
            universe = universe[universe["subsector"] == subsector]

        stocks = universe.to_dict(orient="records")
        subsector_counts = universe["subsector"].value_counts().to_dict()

        return {"stocks": stocks, "subsector_counts": subsector_counts}
    except Exception as e:
        return {"error": str(e), "detail": "Run 'universe update' first"}
