## 1. Python Dependencies and Project Setup

- [x] 1.1 Add `fastapi>=0.104.0`, `uvicorn>=0.24.0`, `python-multipart>=0.0.6` to `requirements.txt`
- [x] 1.2 Add `web` section to `config/settings.yaml` with `host: localhost`, `port: 8000`, `cors_origins: ["http://localhost:3000"]`

## 2. FastAPI Application Core

- [x] 2.1 Create `src/web/__init__.py`
- [x] 2.2 Create `src/web/app.py` with FastAPI app, CORS middleware, static file mounting for `frontend/build/`, and a root route that serves `index.html`
- [x] 2.3 Create `src/web/routes/__init__.py`
- [x] 2.4 Add `serve` command to `main.py` that imports and runs the FastAPI app via uvicorn

## 3. API Routes — Data

- [x] 3.1 Create `src/web/routes/data.py` with `GET /api/data/status` endpoint returning last-updated timestamps and row counts per category
- [x] 3.2 Add `POST /api/data/update` endpoint accepting `{"categories": [...], "force": false}`, triggering DataPipeline, returning per-category results

## 4. API Routes — Universe

- [x] 4.1 Create `src/web/routes/universe.py` with `GET /api/universe` endpoint returning stock list as JSON, supporting `?subsector=` filter

## 5. API Routes — Factors

- [x] 5.1 Create `src/web/routes/factors.py` with `GET /api/factors` endpoint returning the latest factor matrix as JSON
- [x] 5.2 Add `POST /api/factors/compute` endpoint triggering factor computation and returning the updated matrix

## 6. API Routes — Signals

- [x] 6.1 Create `src/web/routes/signals.py` with `GET /api/signals` endpoint returning ranked signal list with scores, direction, sentiment labels, and per-factor contributions

## 7. API Routes — Risk

- [x] 7.1 Create `src/web/routes/risk.py` with `GET /api/risk` endpoint returning drawdown, alerts, and per-position risk metrics

## 8. API Routes — Backtest

- [x] 8.1 Create `src/web/routes/backtest.py` with `POST /api/backtest/run` endpoint accepting start_date, end_date, initial_capital, running backtest engine, returning metrics + NAV series + trade log as JSON
- [x] 8.2 Add `GET /api/backtest/latest` endpoint returning the most recent backtest result

## 9. API Routes — Report

- [x] 9.1 Create `src/web/routes/report.py` with `GET /api/report` endpoint returning structured report data (metrics, NAV series, drawdown series, factor exposures, trade log)
- [x] 9.2 Update `src/report/exporter.py` to add `format="dict"` option returning a Python dict for API consumption

## 10. Frontend Scaffold

- [x] 10.1 Initialize React app in `frontend/` with TypeScript template: `npx create-react-app frontend --template typescript`
- [x] 10.2 Install MUI dependencies: `@mui/material`, `@mui/icons-material`, `@emotion/react`, `@emotion/styled`
- [x] 10.3 Install chart dependencies: `react-plotly.js`, `plotly.js`
- [x] 10.4 Install HTTP client: `axios`
- [x] 10.5 Configure proxy in `frontend/package.json`: `"proxy": "http://localhost:8000"` for dev API forwarding

## 11. Frontend Theme and Layout

- [x] 11.1 Create `frontend/src/theme.ts` with custom MUI theme: primary `#1976d2`, background `#f5f5f5`, Roboto font, minimal elevation
- [x] 11.2 Create `frontend/src/components/Layout.tsx` with persistent left sidebar (Drawer) and top AppBar
- [x] 11.3 Create `frontend/src/components/Sidebar.tsx` with navigation links: Overview, Data, Universe, Factors, Signals, Risk, Backtest, Report
- [x] 11.4 Set up React Router in `frontend/src/App.tsx` with routes for each page

## 12. Frontend Pages — Overview

- [x] 12.1 Create `frontend/src/pages/Overview.tsx` with summary cards (data freshness, NAV, Sharpe, drawdown) and a mini NAV chart
- [x] 12.2 Create `frontend/src/api/client.ts` with axios instance and typed API functions for all endpoints

## 13. Frontend Pages — Data Management

- [x] 13.1 Create `frontend/src/pages/DataManagement.tsx` with data freshness table, per-category update buttons, "Update All" button, and loading state

## 14. Frontend Pages — Universe

- [x] 14.1 Create `frontend/src/pages/Universe.tsx` with searchable/sortable stock table and sub-sector pie chart (Plotly)

## 15. Frontend Pages — Factor Analysis

- [x] 15.1 Create `frontend/src/pages/Factors.tsx` with factor heatmap (Plotly), category summary bar chart, and factor detail panel with distribution histogram and IC chart

## 16. Frontend Pages — Signals

- [x] 16.1 Create `frontend/src/pages/Signals.tsx` with ranked signal table, color-coded direction, expandable rows showing per-factor contributions

## 17. Frontend Pages — Risk Monitor

- [x] 17.1 Create `frontend/src/pages/Risk.tsx` with drawdown chart (Plotly), alert panel, and position risk table

## 18. Frontend Pages — Backtest

- [x] 18.1 Create `frontend/src/pages/Backtest.tsx` with parameter form (start/end date, capital), run button, NAV curve chart, metrics cards, and trade log table

## 19. Frontend Pages — Report

- [x] 19.1 Create `frontend/src/pages/Report.tsx` with full report view (NAV chart, drawdown chart, factor heatmap, holdings table, metrics grid) and HTML export button

## 20. Production Build and Static Serving

- [x] 20.1 Configure FastAPI to serve `frontend/build/` as static files and fall back to `index.html` for client-side routing
- [x] 20.2 Add `frontend/build/` to `.gitignore`
- [x] 20.3 Test production flow: `cd frontend && npm run build`, then `python main.py serve` serves the built dashboard

## 21. Responsive Layout

- [x] 21.1 Add responsive breakpoints to Layout: sidebar collapses to hamburger menu on screens < 768px, cards stack vertically on mobile

## 22. Testing

- [x] 22.1 Add unit tests for each API route in `tests/web/` with mocked pipeline/engine dependencies
- [x] 22.2 Add integration test: start server, call each endpoint, verify JSON response structure
- [x] 22.3 Smoke test: run `python main.py serve` and manually verify dashboard loads in browser
