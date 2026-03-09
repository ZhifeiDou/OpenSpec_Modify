## Why

The quant system is currently CLI-only — users must run terminal commands and read static HTML report files to interact with the system. This creates a high barrier for non-technical users and makes it difficult to monitor live portfolio status, explore factor exposures interactively, or trigger data updates without memorizing CLI commands. A clean, Google Material Design-style web dashboard would make the system accessible to a broader team and provide real-time visibility into data, signals, risk, and backtest performance.

## What Changes

- Add a FastAPI backend server exposing REST API endpoints for all major system operations (data update, universe, factors, signals, risk, backtest, report)
- Add a React + TypeScript frontend with Google Material Design styling (clean, minimal, card-based layout)
- Dashboard pages: Overview, Data Management, Universe, Factor Analysis, Signals, Risk Monitor, Backtest, Report
- Real-time status indicators for data freshness and risk alerts
- Interactive Plotly charts embedded in the frontend (reusing existing chart logic)
- Single-command launch: `python main.py serve` starts both backend and frontend

## Capabilities

### New Capabilities
- `web-api`: FastAPI REST API layer exposing system operations as HTTP endpoints (data update, universe query, factor computation, signal generation, risk check, backtest execution, report retrieval)
- `web-dashboard`: React + TypeScript frontend with Material Design UI — pages for overview, data, universe, factors, signals, risk, backtest, and reports with interactive Plotly charts

### Modified Capabilities
- `report-output`: Add JSON API response format for report data, enabling the dashboard to fetch and render reports dynamically instead of only generating static HTML files

## Impact

- **New dependencies**: `fastapi`, `uvicorn`, `python-multipart` (backend); `react`, `typescript`, `@mui/material`, `plotly.js` (frontend via npm)
- **New directories**: `src/web/` (API routes, server), `frontend/` (React app)
- **Modified files**: `main.py` (add `serve` command), `src/report/exporter.py` (add JSON dict output)
- **Build**: Frontend requires Node.js for development; production build can be served as static files by FastAPI
- **No breaking changes**: All existing CLI commands remain unchanged
