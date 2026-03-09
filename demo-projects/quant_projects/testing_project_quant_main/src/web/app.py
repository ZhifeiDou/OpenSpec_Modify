"""FastAPI application for the quant dashboard."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.web.routes import data, universe, factors, signals, risk, backtest, report


def _load_config() -> dict:
    config_path = os.environ.get("QUANT_CONFIG", "config/settings.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = _load_config()
web_cfg = config.get("web", {})

app = FastAPI(title="有色金属量化系统", version="1.0.0")

# CORS
cors_origins = web_cfg.get("cors_origins", ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store config in app state for route access
app.state.config = config

# Register API routers
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(universe.router, prefix="/api/universe", tags=["universe"])
app.include_router(factors.router, prefix="/api/factors", tags=["factors"])
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(backtest.router, prefix="/api/backtest", tags=["backtest"])
app.include_router(report.router, prefix="/api/report", tags=["report"])

# Serve frontend static files (production build)
_frontend_build = Path(__file__).resolve().parent.parent.parent / "frontend" / "build"
if _frontend_build.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_build / "static")), name="static-files")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React app — fall back to index.html for client-side routing."""
        file_path = _frontend_build / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_frontend_build / "index.html"))
