## Context

The quant system is a Python CLI tool with 7 commands (update, universe, factors, signal, risk-check, backtest, report). It stores data in SQLite, computes factors, generates signals, runs backtests, and exports static HTML reports with Plotly charts. There is no web interface — all interaction is via terminal commands.

The project already uses Plotly for charting and has well-structured modules with clear boundaries (data pipeline, factor engine, signal generation, risk control, backtest engine, report exporter). This modular structure maps cleanly to REST API endpoints.

## Goals / Non-Goals

**Goals:**
- Add a web dashboard accessible via browser at `http://localhost:8000`
- Google Material Design aesthetic: clean, minimal, card-based layout with Roboto font
- Expose all system operations as REST API endpoints
- Interactive charts using Plotly (reusing existing chart patterns)
- Single-command launch: `python main.py serve`
- Production-ready: frontend builds to static files served by FastAPI

**Non-Goals:**
- Real-time streaming / WebSocket push (polling is sufficient for this use case)
- User authentication or multi-user support (single-user local tool)
- Mobile-native app (responsive web is sufficient)
- Rewriting existing CLI commands (they remain unchanged)
- Docker deployment or cloud hosting

## Decisions

### D1: FastAPI for the backend API

**Decision**: Use FastAPI as the API framework.

**Alternatives considered**:
- Flask: Simpler but lacks async support, auto-docs, and type validation
- Django REST Framework: Too heavy for a single-user local tool
- Streamlit: Easy for dashboards but limited customization, not Google Material style

**Rationale**: FastAPI provides automatic OpenAPI docs, Pydantic validation, async support, and static file serving — all with minimal code. The auto-generated `/docs` page is useful for debugging. It's lightweight enough for a local tool.

### D2: React + TypeScript + MUI for the frontend

**Decision**: Use React with TypeScript and MUI (Material UI) component library.

**Alternatives considered**:
- Vue + Vuetify: Good Material Design support but React ecosystem is larger
- Vanilla HTML + CSS: Too much manual work for a polished dashboard
- Streamlit: Python-only but lacks the Google Material look and fine-grained layout control

**Rationale**: MUI provides production-quality Google Material Design components out of the box. React + TypeScript gives type safety and a large ecosystem. `react-plotly.js` allows embedding Plotly charts directly, reusing the chart patterns already established in the Python codebase.

### D3: API-first architecture with thin wrappers

**Decision**: Each API endpoint is a thin wrapper around existing Python modules — no business logic in the API layer.

**Rationale**: The system already has well-structured modules (DataPipeline, FactorEngine, SignalGenerator, etc.). API routes simply instantiate these classes, call their methods, and return results as JSON. This keeps the API layer maintainable and avoids code duplication.

**Structure**:
```
src/web/
  app.py          # FastAPI app, static file serving, CORS
  routes/
    data.py       # /api/data/* → DataPipeline
    universe.py   # /api/universe → UniverseFilter
    factors.py    # /api/factors/* → factor computation
    signals.py    # /api/signals → SignalGenerator
    risk.py       # /api/risk → RiskManager
    backtest.py   # /api/backtest/* → BacktestEngine
    report.py     # /api/report → ReportExporter
```

### D4: Frontend served as static files in production

**Decision**: Frontend builds to `frontend/build/` and FastAPI mounts it as static files. In development, React dev server runs on port 3000 with CORS proxy to the API on port 8000.

**Rationale**: No need for a separate web server in production. A single `python main.py serve` command serves everything. Development workflow uses standard React dev server with hot reload.

### D5: Chart rendering in the frontend with react-plotly.js

**Decision**: Charts are rendered client-side using `react-plotly.js`. The API returns raw data (time series, matrices), and the frontend constructs Plotly chart configs.

**Alternatives considered**:
- Server-side chart rendering (return Plotly HTML): Simpler but loses interactivity and increases payload
- Recharts: Good React integration but less powerful than Plotly for financial charts

**Rationale**: Plotly charts are already used throughout the project. `react-plotly.js` provides the same chart types with full client-side interactivity (zoom, pan, hover tooltips). The frontend can reuse the same chart configurations as the existing Python Plotly code.

### D6: MUI theme customization for Google style

**Decision**: Create a custom MUI theme with:
- Primary color: `#1976d2` (Google Blue)
- Background: `#ffffff` with `#f5f5f5` card backgrounds
- Font: Roboto (MUI default)
- Elevation: Minimal — use subtle borders instead of heavy shadows
- Spacing: 8px grid system (MUI default)

**Rationale**: MUI's default theme is already close to Google Material Design. A few tweaks (reduced elevation, lighter cards) achieve the clean Google look the user requested.

## Risks / Trade-offs

- **[Node.js required for frontend development]** → Document in README; production build is static files only, no Node.js needed at runtime
- **[Long-running operations block API]** → Backtest and data update can take minutes. Use FastAPI's `BackgroundTasks` for data updates; for backtest, run synchronously but show a loading state in the frontend. Future improvement: add async task queue
- **[Frontend bundle size]** → MUI + Plotly.js add significant bundle size (~2MB). Acceptable for a local tool; use code splitting for chart components
- **[No authentication]** → Server only binds to `localhost` by default. Document that exposing to network requires user responsibility

## Migration Plan

1. Add Python dependencies (fastapi, uvicorn)
2. Create `src/web/` with API routes
3. Add `serve` command to `main.py`
4. Scaffold React app in `frontend/`
5. Build frontend pages one by one
6. Add `report-output` dict format for API consumption
7. Configure static file serving
8. Test end-to-end

No database migration needed. No breaking changes to existing CLI.
