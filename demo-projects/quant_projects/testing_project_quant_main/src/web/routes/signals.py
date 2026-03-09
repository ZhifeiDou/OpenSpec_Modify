"""Signals API routes."""
from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("")
async def get_signals(request: Request):
    """Return the latest trading signals as JSON."""
    config = request.app.state.config
    try:
        from src.strategy.signal import generate_signals, get_sentiment_labels

        signals = generate_signals(config)
        if not signals:
            return {"signals": []}

        symbols = [s["symbol"] for s in signals]
        try:
            sentiment_labels = get_sentiment_labels(symbols, config)
        except Exception:
            sentiment_labels = {}

        result = []
        for sig in signals:
            result.append({
                "symbol": sig["symbol"],
                "name": sig.get("name", ""),
                "score": sig.get("score", 0),
                "signal": sig.get("action", "hold"),
                "target_weight": sig.get("target_weight", 0),
                "sentiment_label": sentiment_labels.get(sig["symbol"], ""),
                "factor_contributions": sig.get("factor_contributions", {}),
            })

        return {"signals": result}
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}
