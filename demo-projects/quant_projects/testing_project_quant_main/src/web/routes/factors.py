"""Factors API routes."""
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def get_factors(request: Request):
    """Return the latest factor matrix as JSON."""
    config = request.app.state.config
    try:
        from src.factors.base import compute_all_factors

        factor_matrix = compute_all_factors(config)
        if factor_matrix.empty:
            return {"matrix": [], "categories": {}}

        # Per-stock factor values
        matrix = factor_matrix.reset_index().rename(columns={"index": "symbol"})
        matrix_records = matrix.fillna("null").to_dict(orient="records")

        # Category-level summary (mean of absolute values)
        category_summary = {}
        factor_categories = config.get("factors", {}).get("weights", {})
        for cat in factor_categories:
            cat_cols = [c for c in factor_matrix.columns if cat in c.lower()]
            if cat_cols:
                category_summary[cat] = float(factor_matrix[cat_cols].mean().mean())

        return {"matrix": matrix_records, "categories": category_summary}
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}


@router.post("/compute")
async def compute_factors(request: Request):
    """Trigger factor computation and return updated matrix."""
    config = request.app.state.config
    try:
        from src.factors.base import compute_all_factors

        factor_matrix = compute_all_factors(config)
        matrix = factor_matrix.reset_index().rename(columns={"index": "symbol"})
        matrix_records = matrix.fillna("null").to_dict(orient="records")

        return {"status": "ok", "matrix": matrix_records, "shape": list(factor_matrix.shape)}
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}
