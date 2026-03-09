## Test Report: add-web-dashboard
Generated: 2026-03-08

### Use Case Coverage Summary
| Use Case | Happy Path | Extensions | Overall |
|----------|-----------|------------|---------|
| R1-UC1 View dashboard overview | ✅ 3/6 | ✅ 3/3 | 67% |
| R1-UC2 Manage data updates | ✅ 5/6 | ✅ 3/3 | 89% |
| R1-UC3 Browse stock universe | ✅ 3/5 | ✅ 2/2 | 71% |
| R1-UC4 Analyze factor exposures | ✅ 2/6 | ✅ 2/3 | 44% |
| R1-UC5 View trading signals | ✅ 3/5 | ✅ 2/2 | 71% |
| R1-UC6 Monitor portfolio risk | ✅ 4/5 | ✅ 2/2 | 86% |
| R1-UC7 Run and view backtest | ✅ 4/7 | ✅ 3/3 | 70% |
| R1-UC8 View performance report | ✅ 2/5 | ✅ 1/2 | 43% |
| R1-UC9 Start the web server | ✅ 3/5 | ⚠️ 1/2 | 57% |

**Overall: 54/79 paths/steps covered (68%)**

> Note: 17 of the 25 uncovered items are **frontend-only** (React rendering, chart interactions, page navigation) and cannot be tested from Python backend tests. Excluding frontend-only items, backend API coverage is **54/62 (87%)**.

### Covered Requirements

- ✅ **R1-UC1-S2**: System loads data freshness timestamps (`tests/web/test_data_routes.py:7`)
- ✅ **R1-UC1-S3**: System loads current risk status (`tests/web/test_risk_routes.py:6`)
- ✅ **R1-UC1-S4**: System loads latest portfolio metrics (`tests/web/test_report_routes.py:9`)
- ⚠️ **R1-UC1-E1**: No data fetched yet — shows "No data" (`tests/web/test_data_routes.py:22`)
- ✅ **R1-UC1-E2**: No backtest run — shows empty metrics (`tests/web/test_report_routes.py:34`)
- ✅ **R1-UC1-E3**: Database error — shows error card (`tests/web/test_data_routes.py:33`)
- ✅ **R1-UC2** Full Flow (`tests/web/test_integration.py:8,14`)
- ✅ **R1-UC2-S2**: System displays data freshness per category (`tests/web/test_data_routes.py:7`)
- ✅ **R1-UC2-S3**: Analyst selects categories or "Update All" (`tests/web/test_data_routes.py:36,53`)
- ✅ **R1-UC2-S4**: System triggers data pipeline (`tests/web/test_data_routes.py:36`)
- ✅ **R1-UC2-S5**: System reports completion status (`tests/web/test_data_routes.py:36`)
- ⚠️ **R1-UC2-S6**: System refreshes data freshness display (`tests/web/test_data_routes.py:36`)
- ⚠️ **R1-UC2-E1**: Tushare token invalid (`tests/web/test_data_routes.py:68`)
- ⚠️ **R1-UC2-E2**: Category fails during update (`tests/web/test_data_routes.py:68`)
- ✅ **R1-UC2-E3**: Force refresh re-downloads all data (`tests/web/test_data_routes.py:79`)
- ✅ **R1-UC3** Full Flow (`tests/web/test_integration.py:22`)
- ✅ **R1-UC3-S2**: System loads current universe (`tests/web/test_universe_routes.py:7`)
- ✅ **R1-UC3-S3**: System displays stock table (`tests/web/test_universe_routes.py:7`)
- ✅ **R1-UC3-S5**: Analyst filters by sub-sector (`tests/web/test_universe_routes.py:21`)
- ✅ **R1-UC3-E1**: No universe data (`tests/web/test_universe_routes.py:35`)
- ✅ **R1-UC3-E2**: Filter returns no results (`tests/web/test_universe_routes.py:35`)
- ✅ **R1-UC4** Full Flow (`tests/web/test_integration.py:29,36`)
- ✅ **R1-UC4-S2**: System loads latest factor matrix (`tests/web/test_factors_routes.py:7`)
- ⚠️ **R1-UC4-S4**: System renders category-level summary (`tests/web/test_factors_routes.py:7`)
- ✅ **R1-UC4-E1**: Factors not computed — compute trigger (`tests/web/test_factors_routes.py:20,37`)
- ✅ **R1-UC5** Full Flow (`tests/web/test_integration.py:43`)
- ✅ **R1-UC5-S2**: System loads latest signal output (`tests/web/test_signals_routes.py:6`)
- ✅ **R1-UC5-S3**: System displays ranked table (`tests/web/test_signals_routes.py:6`)
- ✅ **R1-UC5-S5**: System shows factor contributions (`tests/web/test_signals_routes.py:6`)
- ✅ **R1-UC5-E1**: No signals generated (`tests/web/test_signals_routes.py:26`)
- ✅ **R1-UC5-E2**: Sentiment data unavailable (`tests/web/test_signals_routes.py:33`)
- ✅ **R1-UC6** Full Flow (`tests/web/test_integration.py:50`)
- ✅ **R1-UC6-S2**: System loads portfolio state (`tests/web/test_risk_routes.py:6`)
- ✅ **R1-UC6-S4**: System displays active risk alerts (`tests/web/test_risk_routes.py:6,39`)
- ✅ **R1-UC6-S5**: System displays position-level risk metrics (`tests/web/test_risk_routes.py:6`)
- ✅ **R1-UC6-E1**: No portfolio data (`tests/web/test_risk_routes.py:54`)
- ✅ **R1-UC6-E2**: No active alerts (`tests/web/test_risk_routes.py:25`)
- ✅ **R1-UC7** Full Flow (`tests/web/test_integration.py:56,65`)
- ✅ **R1-UC7-S2**: Analyst sets parameters (`tests/web/test_backtest_routes.py:9`)
- ✅ **R1-UC7-S3**: Analyst clicks "Run Backtest" (`tests/web/test_backtest_routes.py:9`)
- ✅ **R1-UC7-S4**: System executes backtest engine (`tests/web/test_backtest_routes.py:9`)
- ✅ **R1-UC7-S5**: System returns metrics, NAV, trade log (`tests/web/test_backtest_routes.py:9`)
- ✅ **R1-UC7-E1**: Insufficient data — returns error (`tests/web/test_backtest_routes.py:33`)
- ✅ **R1-UC7-E2**: Load previous backtest result (`tests/web/test_backtest_routes.py:45,61`)
- ✅ **R1-UC8** Full Flow (`tests/web/test_integration.py:71`)
- ✅ **R1-UC8-S2**: System loads latest backtest result as JSON (`tests/web/test_report_routes.py:9`)
- ✅ **R1-UC8-S3**: System renders metrics, NAV, drawdown, heatmap, holdings (`tests/web/test_report_routes.py:9`)
- ✅ **R1-UC8-E1**: No backtest result (`tests/web/test_report_routes.py:34`)
- ⚠️ **R1-UC9** Full Flow (`tests/web/test_server_startup.py:13`)
- ✅ **R1-UC9-S1**: Analyst runs `python main.py serve` (`tests/web/test_server_startup.py:42`)
- ✅ **R1-UC9-S2**: System loads configuration (`tests/web/test_server_startup.py:9,28`)
- ⚠️ **R1-UC9-S3**: System starts FastAPI server (`tests/web/test_server_startup.py:9`)
- ✅ **R1-UC9-S4**: System serves frontend and API endpoints (`tests/web/test_server_startup.py:13`)
- ⚠️ **R1-UC9-E2**: Config file missing — uses defaults (`tests/web/test_server_startup.py:34`)

### Uncovered Requirements

**API-level gaps (could add Python tests):**
- ❌ **R1-UC1**: View dashboard overview Full Flow: No aggregated overview test
- ❌ **R1-UC4-E2**: IC data unavailable: No API endpoint exposes IC data separately
- ❌ **R1-UC9-S5**: System prints dashboard URL: Print output not captured in tests
- ❌ **R1-UC9-E1**: Port already in use: Uvicorn-level error, hard to unit test

**Frontend-only gaps (require React Testing Library, not Python-testable):**
- ❌ **R1-UC1-S1**: Analyst navigates to dashboard home page
- ❌ **R1-UC1-S5**: System renders overview with summary cards and mini NAV chart
- ❌ **R1-UC1-S6**: Analyst sees complete overview
- ❌ **R1-UC2-S1**: Analyst navigates to Data Management page
- ❌ **R1-UC3-S1**: Analyst opens Universe page
- ❌ **R1-UC3-S4**: System displays sub-sector pie chart
- ❌ **R1-UC4-S1**: Analyst opens Factor Analysis page
- ❌ **R1-UC4-S3**: System renders factor heatmap
- ❌ **R1-UC4-S5**: Analyst clicks factor for detail view
- ❌ **R1-UC4-S6**: System renders factor detail with histogram and IC
- ❌ **R1-UC5-S1**: Analyst opens Signals page
- ❌ **R1-UC5-S4**: Analyst clicks stock row for detail
- ❌ **R1-UC6-S1**: Analyst opens Risk Monitor page
- ❌ **R1-UC6-S3**: System displays drawdown chart
- ❌ **R1-UC7-S1**: Analyst opens Backtest page
- ❌ **R1-UC7-S6**: System renders NAV curve, metrics cards, trade table
- ❌ **R1-UC7-S7**: Analyst reviews performance
- ❌ **R1-UC8-S1**: Analyst opens Report page
- ❌ **R1-UC8-S4**: Analyst toggles chart views
- ❌ **R1-UC8-S5**: Analyst exports report as HTML/PDF
- ❌ **R1-UC8-E2**: PDF export fails — fallback to HTML

### Test Run Results

```
47 passed in 4.42s
0 failed
0 skipped
```

**Test files:**
- `tests/web/test_data_routes.py` — 7 tests (data status + update)
- `tests/web/test_universe_routes.py` — 5 tests (universe list + filter)
- `tests/web/test_factors_routes.py` — 5 tests (factor matrix + compute)
- `tests/web/test_signals_routes.py` — 4 tests (signals + sentiment)
- `tests/web/test_risk_routes.py` — 4 tests (risk + alerts)
- `tests/web/test_backtest_routes.py` — 4 tests (run + latest)
- `tests/web/test_report_routes.py` — 3 tests (report + factor failure)
- `tests/web/test_server_startup.py` — 5 tests (app config + routes + serve command)
- `tests/web/test_integration.py` — 10 tests (all endpoints JSON response)
