"""Data management API routes."""
from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class UpdateRequest(BaseModel):
    categories: list[str] = ["all"]
    force: bool = False


@router.get("/status")
async def data_status(request: Request):
    """Return last-updated timestamps and row counts per data category."""
    config = request.app.state.config

    try:
        from src.data.storage import DataStore

        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

        categories = ["stock", "futures", "macro", "flow"]
        table_map = {
            "stock": "stock_daily",
            "futures": "futures_daily",
            "macro": "macro",
            "flow": "fund_flow",
        }

        result = {}
        for cat in categories:
            last_updated = store.get_last_updated(cat)
            try:
                df = store.read_table(table_map[cat])
                row_count = len(df)
            except Exception:
                row_count = 0
            result[cat] = {"last_updated": last_updated, "rows": row_count}

        return result
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}


@router.post("/update")
async def data_update(body: UpdateRequest, request: Request):
    """Trigger data pipeline for selected categories."""
    config = request.app.state.config

    try:
        from src.data.pipeline import DataPipeline

        pipeline = DataPipeline(config)

        cats = body.categories if "all" not in body.categories else None

        # Resolve symbols for stock/flow
        symbols = None
        need_symbols = cats is None or "stock" in cats or "flow" in cats
        if need_symbols:
            try:
                from src.universe.classifier import get_universe
                universe = get_universe(config)
                symbols = universe["symbol"].tolist() if not universe.empty else None
            except Exception:
                symbols = None

        pipeline.run(
            symbols=symbols,
            categories=cats,
            force_refresh=body.force,
        )
        # Re-read status after update
        from src.data.storage import DataStore
        data_cfg = config.get("data", {})
        store = DataStore(data_cfg.get("db_path", "data/quant.db"))

        results = {}
        table_map = {"stock": "stock_daily", "futures": "futures_daily", "macro": "macro", "flow": "fund_flow"}
        for cat in (cats or ["stock", "futures", "macro", "flow"]):
            last_updated = store.get_last_updated(cat)
            try:
                df = store.read_table(table_map.get(cat, cat))
                row_count = len(df)
            except Exception:
                row_count = 0
            results[cat] = {"last_updated": last_updated, "rows": row_count}

        return {"status": "ok", "results": results}
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}
