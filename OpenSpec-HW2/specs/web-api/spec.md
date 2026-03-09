## ADDED Requirements

### Requirement: FastAPI server startup
The system SHALL provide a FastAPI application in `src/web/app.py` that starts via `python main.py serve`. The server SHALL serve both REST API endpoints and the frontend static files. The default host SHALL be `localhost` and default port SHALL be `8000`, configurable via `config/settings.yaml` under `web.host` and `web.port`.

#### Scenario: Start server
- **WHEN** user runs `python main.py serve`
- **THEN** FastAPI server starts on `http://localhost:8000` and prints the URL to terminal

#### Scenario: Port conflict
- **WHEN** port 8000 is already in use
- **THEN** system reports the conflict and exits with a clear error message

### Requirement: Data update API
The system SHALL expose `POST /api/data/update` accepting a JSON body with `categories` (list of strings: "stock", "futures", "macro", "flow", or "all") and optional `force` boolean. The endpoint SHALL trigger the DataPipeline and return a JSON result with per-category status and row counts.

#### Scenario: Update all data
- **WHEN** client sends `POST /api/data/update {"categories": ["all"]}`
- **THEN** system runs the full data pipeline and returns `{"status": "ok", "results": {"stock": "50 rows", "futures": "40 rows", ...}}`

#### Scenario: Update with force refresh
- **WHEN** client sends `POST /api/data/update {"categories": ["stock"], "force": true}`
- **THEN** system re-downloads all stock data from scratch

### Requirement: Data status API
The system SHALL expose `GET /api/data/status` returning last-updated timestamps for each data category and total record counts.

#### Scenario: Get data freshness
- **WHEN** client sends `GET /api/data/status`
- **THEN** system returns `{"stock": {"last_updated": "2026-03-08", "rows": 5000}, "futures": {...}, ...}`

### Requirement: Universe API
The system SHALL expose `GET /api/universe` returning the current stock universe as a JSON array with fields: `symbol`, `name`, `subsector`, `listing_date`, `avg_turnover_20d`. The system SHALL support optional query parameter `subsector` for filtering.

#### Scenario: Get full universe
- **WHEN** client sends `GET /api/universe`
- **THEN** system returns all stocks in the current universe

#### Scenario: Filter by subsector
- **WHEN** client sends `GET /api/universe?subsector=copper`
- **THEN** system returns only copper-subsector stocks

### Requirement: Factors API
The system SHALL expose `GET /api/factors` returning the latest factor matrix as JSON. The system SHALL expose `POST /api/factors/compute` to trigger factor computation. The factor matrix response SHALL include per-stock factor values and category-level summaries.

#### Scenario: Get factor matrix
- **WHEN** client sends `GET /api/factors`
- **THEN** system returns `{"matrix": [{"symbol": "601899", "metal_price_mom_60d": 0.12, ...}], "categories": {"commodity": 0.35, ...}}`

#### Scenario: Compute factors
- **WHEN** client sends `POST /api/factors/compute`
- **THEN** system runs factor computation and returns the updated matrix

### Requirement: Signals API
The system SHALL expose `GET /api/signals` returning the latest trading signals as JSON with fields: `symbol`, `name`, `score`, `signal` (buy/hold/sell), `sentiment_label`, and per-factor contributions.

#### Scenario: Get signals
- **WHEN** client sends `GET /api/signals`
- **THEN** system returns ranked signal list sorted by composite score descending

### Requirement: Risk API
The system SHALL expose `GET /api/risk` returning current risk status: portfolio drawdown percentage, active alerts (drawdown breach, trailing stop, metal crash), and per-position risk metrics (weight, stop price, distance to stop).

#### Scenario: Get risk status
- **WHEN** client sends `GET /api/risk`
- **THEN** system returns `{"drawdown": -0.05, "alerts": [], "positions": [...]}`

### Requirement: Backtest API
The system SHALL expose `POST /api/backtest/run` accepting `start_date`, `end_date`, and optional `initial_capital`. The endpoint SHALL run the backtest engine and return results as JSON including: summary metrics, NAV time series, and trade log. The system SHALL also expose `GET /api/backtest/latest` to retrieve the most recent backtest result.

#### Scenario: Run backtest
- **WHEN** client sends `POST /api/backtest/run {"start_date": "2024-01-01", "end_date": "2025-12-31"}`
- **THEN** system runs the backtest and returns metrics, NAV series, and trade log

#### Scenario: Get latest result
- **WHEN** client sends `GET /api/backtest/latest`
- **THEN** system returns the most recent backtest result, or 404 if none exists

### Requirement: Report API
The system SHALL expose `GET /api/report` returning the latest report data as structured JSON suitable for frontend chart rendering: metrics, NAV series, drawdown series, factor exposures, and trade log.

#### Scenario: Get report data
- **WHEN** client sends `GET /api/report`
- **THEN** system returns structured JSON with all report sections

### Requirement: CORS configuration
The system SHALL enable CORS for the configured frontend origin (default `http://localhost:3000` for development). In production mode (frontend served as static files), CORS SHALL be restricted to same-origin.

#### Scenario: Development CORS
- **WHEN** frontend dev server runs on port 3000
- **THEN** API allows cross-origin requests from `http://localhost:3000`

### Requirement: Error response format
All API endpoints SHALL return errors as JSON with `{"error": "<message>", "detail": "<optional detail>"}` and appropriate HTTP status codes (400, 404, 500).

#### Scenario: Invalid request
- **WHEN** client sends an invalid request body
- **THEN** system returns HTTP 400 with a descriptive JSON error message
