## Use Cases

### Use Case: View dashboard overview

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Web server is running (`python main.py serve`)
- SQLite database exists with at least one data update completed

**Success Guarantee (Postconditions):**
- Analyst sees a summary dashboard with data freshness, latest signals, risk status, and key performance metrics

**Trigger:** Analyst opens the dashboard URL in a browser

**Main Success Scenario:**
1. Analyst navigates to the dashboard home page
2. System loads latest data freshness timestamps for each category (stock, futures, macro, flow)
3. System loads current risk status (drawdown level, active alerts)
4. System loads latest portfolio metrics (NAV, daily return, Sharpe ratio)
5. System renders an overview page with summary cards and a mini NAV chart
6. Analyst sees the complete overview at a glance

**Extensions:**
- 2a. No data has been fetched yet: System shows "No data" status with a prompt to run data update
- 3a. No backtest has been run: System shows empty metrics cards with a prompt to run backtest first
- 5a. Server encounters a database error: System shows an error card with the error message

---

### Use Case: Manage data updates via dashboard

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Web server is running
- Tushare token is configured in `.env`

**Success Guarantee (Postconditions):**
- Selected data categories are updated and dashboard reflects new timestamps

**Trigger:** Analyst clicks "Update Data" on the data management page

**Main Success Scenario:**
1. Analyst navigates to the Data Management page
2. System displays data freshness for each category (stock, futures, macro, flow) with last-updated timestamps
3. Analyst selects which categories to update (or "Update All")
4. System triggers the data pipeline for selected categories
5. System reports progress and completion status
6. System refreshes the data freshness display with new timestamps

**Extensions:**
- 4a. Tushare token is invalid: System returns an error indicating token validation failed
- 5a. A category fails during update: System reports the failure for that category and continues with remaining categories
- 3a. Analyst toggles "Force Refresh": System re-downloads all data from scratch instead of incremental

---

### Use Case: Browse stock universe

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Universe has been computed at least once

**Success Guarantee (Postconditions):**
- Analyst sees the filtered stock list with sub-sector breakdown

**Trigger:** Analyst navigates to the Universe page

**Main Success Scenario:**
1. Analyst opens the Universe page
2. System loads the current universe from the database
3. System displays a table of stocks with columns: symbol, name, sub-sector, listing date, avg turnover
4. System displays a sub-sector distribution pie chart
5. Analyst filters or searches by sub-sector or stock name

**Extensions:**
- 2a. No universe data exists: System shows a prompt to run universe classification first
- 5a. Filter returns no results: System shows "No stocks match the filter"

---

### Use Case: Analyze factor exposures

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Factors have been computed for the current universe

**Success Guarantee (Postconditions):**
- Analyst sees factor values, heatmaps, and IC tracking for the universe

**Trigger:** Analyst navigates to the Factors page

**Main Success Scenario:**
1. Analyst opens the Factor Analysis page
2. System loads the latest factor matrix (stocks x factors)
3. System renders a factor heatmap showing Z-scores per stock per factor
4. System renders category-level summary (commodity, fundamental, technical, flow, macro, sentiment)
5. Analyst clicks on a specific factor to see its distribution and IC history
6. System renders the factor detail view with histogram and IC tracking chart

**Extensions:**
- 2a. Factors not computed yet: System shows a "Compute Factors" button that triggers computation
- 5a. IC data unavailable: System shows the factor distribution without IC tracking

---

### Use Case: View trading signals

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Signal generation has been run at least once

**Success Guarantee (Postconditions):**
- Analyst sees current buy/sell signals with scores and sentiment labels

**Trigger:** Analyst navigates to the Signals page

**Main Success Scenario:**
1. Analyst opens the Signals page
2. System loads the latest signal output
3. System displays a ranked table of stocks with composite scores, signal direction (buy/hold/sell), and sentiment labels
4. Analyst clicks a stock row to see detailed factor breakdown
5. System shows the individual factor contributions to that stock's score

**Extensions:**
- 2a. No signals generated: System shows a prompt to generate signals first
- 4a. News sentiment data unavailable: System shows factor breakdown without sentiment detail

---

### Use Case: Monitor portfolio risk

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- At least one backtest or live portfolio session exists

**Success Guarantee (Postconditions):**
- Analyst sees current drawdown, stop-loss status, and risk alerts

**Trigger:** Analyst navigates to the Risk Monitor page

**Main Success Scenario:**
1. Analyst opens the Risk Monitor page
2. System loads current portfolio state (drawdown, position sizes, stop-loss levels)
3. System displays a drawdown underwater chart
4. System displays active risk alerts (if any): max drawdown breach, trailing stop triggers, metal crash warnings
5. System displays position-level risk metrics: per-stock weight, ATR-based stop prices

**Extensions:**
- 2a. No portfolio data: System shows empty state with prompt to run backtest
- 4a. No active alerts: System shows "All clear — no risk alerts" status

---

### Use Case: Run and view backtest

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- Stock data, factors, and signals are available for the requested date range

**Success Guarantee (Postconditions):**
- Backtest completes and results are displayed with NAV curve, metrics, and trade log

**Trigger:** Analyst configures backtest parameters and clicks "Run Backtest"

**Main Success Scenario:**
1. Analyst opens the Backtest page
2. Analyst sets start date, end date, and initial capital
3. Analyst clicks "Run Backtest"
4. System executes the backtest engine with the specified parameters
5. System returns results: summary metrics, NAV time series, trade log
6. System renders NAV curve chart (strategy vs benchmark), metrics cards, and trade history table
7. Analyst reviews performance and explores individual trades

**Extensions:**
- 4a. Backtest fails due to insufficient data: System returns an error indicating missing data for the date range
- 3a. Analyst loads a previous backtest result: System displays the saved result without re-running

---

### Use Case: View performance report

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** User goal

**Preconditions:**
- A backtest result exists

**Success Guarantee (Postconditions):**
- Analyst sees a comprehensive report with all charts and metrics

**Trigger:** Analyst navigates to the Report page or clicks "View Report" from backtest results

**Main Success Scenario:**
1. Analyst opens the Report page
2. System loads the latest backtest result as structured JSON
3. System renders: summary metrics grid, NAV chart, drawdown chart, factor heatmap, holdings table
4. Analyst can toggle between different chart views
5. Analyst exports the report as HTML or PDF

**Extensions:**
- 2a. No backtest result: System shows prompt to run backtest first
- 5a. PDF export fails: System falls back to HTML export with a notification

---

### Use Case: Start the web server

**Primary Actor:** Analyst
**Scope:** Web Dashboard
**Level:** Subfunction

**Preconditions:**
- Python dependencies installed (fastapi, uvicorn)
- Frontend built (or dev server available)

**Success Guarantee (Postconditions):**
- Web server is running and dashboard is accessible at `http://localhost:8000`

**Trigger:** Analyst runs `python main.py serve`

**Main Success Scenario:**
1. Analyst runs `python main.py serve`
2. System loads configuration from `config/settings.yaml`
3. System starts FastAPI server on configured host/port (default `localhost:8000`)
4. System serves the frontend static files and API endpoints
5. System prints the dashboard URL to the terminal

**Extensions:**
- 3a. Port already in use: System reports the conflict and suggests an alternative port
- 2a. Configuration file missing: System uses sensible defaults and warns
