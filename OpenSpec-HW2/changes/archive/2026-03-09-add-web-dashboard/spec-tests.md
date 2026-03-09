# Spec-Test Mapping: add-web-dashboard
Generated: 2026-03-08

## Use Case ID Mapping

| ID | Use Case |
|----|----------|
| R1-UC1 | View dashboard overview |
| R1-UC2 | Manage data updates via dashboard |
| R1-UC3 | Browse stock universe |
| R1-UC4 | Analyze factor exposures |
| R1-UC5 | View trading signals |
| R1-UC6 | Monitor portfolio risk |
| R1-UC7 | Run and view backtest |
| R1-UC8 | View performance report |
| R1-UC9 | Start the web server |

## Requirement Traceability Matrix

| ID | Requirement | Type | Test Type | Test Case | Status |
|----|-------------|------|-----------|-----------|--------|
| R1-UC1 | View dashboard overview Full Flow | Flow | Integration | | ❌ |
| R1-UC1-S1 | Analyst navigates to dashboard home page | Step | Unit | | ❌ |
| R1-UC1-S2 | System loads data freshness timestamps | Step | Unit | `tests/web/test_data_routes.py:7` | ✅ |
| R1-UC1-S3 | System loads current risk status | Step | Unit | `tests/web/test_risk_routes.py:6` | ✅ |
| R1-UC1-S4 | System loads latest portfolio metrics | Step | Unit | `tests/web/test_report_routes.py:9` | ✅ |
| R1-UC1-S5 | System renders overview with summary cards and mini NAV chart | Step | Unit | | ❌ |
| R1-UC1-S6 | Analyst sees complete overview | Step | Integration | | ❌ |
| R1-UC1-E1 | No data fetched yet — shows "No data" status | Extension | Unit | `tests/web/test_data_routes.py:22` | ⚠️ |
| R1-UC1-E2 | No backtest run — shows empty metrics | Extension | Unit | `tests/web/test_report_routes.py:34` | ✅ |
| R1-UC1-E3 | Database error — shows error card | Extension | Unit | `tests/web/test_data_routes.py:33` | ✅ |
| R1-UC2 | Manage data updates Full Flow | Flow | Integration | `tests/web/test_integration.py:8`, `tests/web/test_integration.py:14` | ✅ |
| R1-UC2-S1 | Analyst navigates to Data Management page | Step | Unit | | ❌ |
| R1-UC2-S2 | System displays data freshness per category | Step | Unit | `tests/web/test_data_routes.py:7` | ✅ |
| R1-UC2-S3 | Analyst selects categories or "Update All" | Step | Unit | `tests/web/test_data_routes.py:53` | ✅ |
| R1-UC2-S3 | Analyst selects categories or "Update All" | Step | Component | `tests/web/test_data_routes.py:36` | ✅ |
| R1-UC2-S4 | System triggers data pipeline | Step | Component | `tests/web/test_data_routes.py:36` | ✅ |
| R1-UC2-S5 | System reports completion status | Step | Component | `tests/web/test_data_routes.py:36` | ✅ |
| R1-UC2-S6 | System refreshes data freshness display | Step | Component | `tests/web/test_data_routes.py:36` | ⚠️ |
| R1-UC2-E1 | Tushare token invalid — error returned | Extension | Unit | `tests/web/test_data_routes.py:68` | ⚠️ |
| R1-UC2-E2 | Category fails during update — reports failure | Extension | Unit | `tests/web/test_data_routes.py:68` | ⚠️ |
| R1-UC2-E3 | Force refresh re-downloads all data | Extension | Unit | `tests/web/test_data_routes.py:79` | ✅ |
| R1-UC3 | Browse stock universe Full Flow | Flow | Integration | `tests/web/test_integration.py:22` | ✅ |
| R1-UC3-S1 | Analyst opens Universe page | Step | Unit | | ❌ |
| R1-UC3-S2 | System loads current universe | Step | Unit | `tests/web/test_universe_routes.py:7` | ✅ |
| R1-UC3-S3 | System displays stock table | Step | Component | `tests/web/test_universe_routes.py:7` | ✅ |
| R1-UC3-S4 | System displays sub-sector pie chart | Step | Unit | | ❌ |
| R1-UC3-S5 | Analyst filters by sub-sector or name | Step | Unit | `tests/web/test_universe_routes.py:21` | ✅ |
| R1-UC3-E1 | No universe data — shows prompt | Extension | Unit | `tests/web/test_universe_routes.py:35` | ✅ |
| R1-UC3-E2 | Filter returns no results | Extension | Unit | `tests/web/test_universe_routes.py:35` | ✅ |
| R1-UC4 | Analyze factor exposures Full Flow | Flow | Integration | `tests/web/test_integration.py:29`, `tests/web/test_integration.py:36` | ✅ |
| R1-UC4-S1 | Analyst opens Factor Analysis page | Step | Unit | | ❌ |
| R1-UC4-S2 | System loads latest factor matrix | Step | Unit | `tests/web/test_factors_routes.py:7` | ✅ |
| R1-UC4-S3 | System renders factor heatmap | Step | Unit | | ❌ |
| R1-UC4-S4 | System renders category-level summary | Step | Component | `tests/web/test_factors_routes.py:7` | ⚠️ |
| R1-UC4-S5 | Analyst clicks factor for detail view | Step | Unit | | ❌ |
| R1-UC4-S6 | System renders factor detail with histogram and IC | Step | Unit | | ❌ |
| R1-UC4-E1 | Factors not computed — "Compute Factors" button | Extension | Unit | `tests/web/test_factors_routes.py:20` | ✅ |
| R1-UC4-E1 | Factors not computed — compute trigger | Extension | Unit | `tests/web/test_factors_routes.py:37` | ✅ |
| R1-UC4-E2 | IC data unavailable | Extension | Unit | | ❌ |
| R1-UC5 | View trading signals Full Flow | Flow | Integration | `tests/web/test_integration.py:43` | ✅ |
| R1-UC5-S1 | Analyst opens Signals page | Step | Unit | | ❌ |
| R1-UC5-S2 | System loads latest signal output | Step | Unit | `tests/web/test_signals_routes.py:6` | ✅ |
| R1-UC5-S3 | System displays ranked table with scores, direction, sentiment | Step | Component | `tests/web/test_signals_routes.py:6` | ✅ |
| R1-UC5-S4 | Analyst clicks stock row for detail | Step | Unit | | ❌ |
| R1-UC5-S5 | System shows factor contributions | Step | Component | `tests/web/test_signals_routes.py:6` | ✅ |
| R1-UC5-E1 | No signals generated — shows prompt | Extension | Unit | `tests/web/test_signals_routes.py:26` | ✅ |
| R1-UC5-E2 | Sentiment data unavailable — shows without sentiment | Extension | Unit | `tests/web/test_signals_routes.py:33` | ✅ |
| R1-UC6 | Monitor portfolio risk Full Flow | Flow | Integration | `tests/web/test_integration.py:50` | ✅ |
| R1-UC6-S1 | Analyst opens Risk Monitor page | Step | Unit | | ❌ |
| R1-UC6-S2 | System loads portfolio state | Step | Unit | `tests/web/test_risk_routes.py:6` | ✅ |
| R1-UC6-S3 | System displays drawdown chart | Step | Unit | | ❌ |
| R1-UC6-S4 | System displays active risk alerts | Step | Unit | `tests/web/test_risk_routes.py:6` | ✅ |
| R1-UC6-S4 | System displays active risk alerts (critical) | Step | Unit | `tests/web/test_risk_routes.py:39` | ✅ |
| R1-UC6-S5 | System displays position-level risk metrics | Step | Component | `tests/web/test_risk_routes.py:6` | ✅ |
| R1-UC6-E1 | No portfolio data — shows prompt | Extension | Unit | `tests/web/test_risk_routes.py:54` | ✅ |
| R1-UC6-E2 | No active alerts — shows "All clear" | Extension | Unit | `tests/web/test_risk_routes.py:25` | ✅ |
| R1-UC7 | Run and view backtest Full Flow | Flow | Integration | `tests/web/test_integration.py:56`, `tests/web/test_integration.py:65` | ✅ |
| R1-UC7-S1 | Analyst opens Backtest page | Step | Unit | | ❌ |
| R1-UC7-S2 | Analyst sets start date, end date, initial capital | Step | Component | `tests/web/test_backtest_routes.py:9` | ✅ |
| R1-UC7-S3 | Analyst clicks "Run Backtest" | Step | Component | `tests/web/test_backtest_routes.py:9` | ✅ |
| R1-UC7-S4 | System executes backtest engine | Step | Component | `tests/web/test_backtest_routes.py:9` | ✅ |
| R1-UC7-S5 | System returns metrics, NAV, trade log | Step | Unit | `tests/web/test_backtest_routes.py:9` | ✅ |
| R1-UC7-S6 | System renders NAV curve, metrics cards, trade table | Step | Unit | | ❌ |
| R1-UC7-S7 | Analyst reviews performance | Step | Unit | | ❌ |
| R1-UC7-E1 | Insufficient data — returns error | Extension | Unit | `tests/web/test_backtest_routes.py:33` | ✅ |
| R1-UC7-E2 | Load previous backtest result | Extension | Unit | `tests/web/test_backtest_routes.py:45` | ✅ |
| R1-UC7-E2 | No previous result — returns error | Extension | Unit | `tests/web/test_backtest_routes.py:61` | ✅ |
| R1-UC8 | View performance report Full Flow | Flow | Integration | `tests/web/test_integration.py:71` | ✅ |
| R1-UC8-S1 | Analyst opens Report page | Step | Unit | | ❌ |
| R1-UC8-S2 | System loads latest backtest result as JSON | Step | Unit | `tests/web/test_report_routes.py:9` | ✅ |
| R1-UC8-S3 | System renders metrics, NAV, drawdown, heatmap, holdings | Step | Component | `tests/web/test_report_routes.py:9` | ✅ |
| R1-UC8-S4 | Analyst toggles chart views | Step | Unit | | ❌ |
| R1-UC8-S5 | Analyst exports report as HTML/PDF | Step | Unit | | ❌ |
| R1-UC8-E1 | No backtest result — shows prompt | Extension | Unit | `tests/web/test_report_routes.py:34` | ✅ |
| R1-UC8-E2 | PDF export fails — fallback to HTML | Extension | Unit | | ❌ |
| R1-UC9 | Start the web server Full Flow | Flow | Integration | `tests/web/test_server_startup.py:13` | ⚠️ |
| R1-UC9-S1 | Analyst runs `python main.py serve` | Step | Unit | `tests/web/test_server_startup.py:42` | ✅ |
| R1-UC9-S2 | System loads configuration | Step | Unit | `tests/web/test_server_startup.py:9` | ✅ |
| R1-UC9-S2 | System loads configuration | Step | Unit | `tests/web/test_server_startup.py:28` | ✅ |
| R1-UC9-S3 | System starts FastAPI server | Step | Unit | `tests/web/test_server_startup.py:9` | ⚠️ |
| R1-UC9-S4 | System serves frontend and API endpoints | Step | Integration | `tests/web/test_server_startup.py:13` | ✅ |
| R1-UC9-S5 | System prints dashboard URL | Step | Unit | | ❌ |
| R1-UC9-E1 | Port already in use | Extension | Unit | | ❌ |
| R1-UC9-E2 | Config file missing — uses defaults | Extension | Unit | `tests/web/test_server_startup.py:34` | ⚠️ |

## Use Case Details: View dashboard overview (ID: R1-UC1)

### Main Scenario
- **R1-UC1-S1**: Analyst navigates to dashboard home page — ❌ (frontend navigation, not API-testable)
- **R1-UC1-S2**: System loads data freshness timestamps
  - `tests/web/test_data_routes.py:7` test_returns_all_categories (Unit)
- **R1-UC1-S3**: System loads current risk status
  - `tests/web/test_risk_routes.py:6` test_returns_risk_data (Unit)
- **R1-UC1-S4**: System loads latest portfolio metrics
  - `tests/web/test_report_routes.py:9` test_returns_full_report (Unit)
- **R1-UC1-S5**: System renders overview with summary cards and mini NAV chart — ❌ (frontend rendering)
- **R1-UC1-S6**: Analyst sees complete overview — ❌ (frontend rendering)

### Extensions
- **R1-UC1-E1**: No data fetched yet → `tests/web/test_data_routes.py:22` test_handles_missing_table (Unit) ⚠️
- **R1-UC1-E2**: No backtest run → `tests/web/test_report_routes.py:34` test_no_data_returns_error (Unit) ✅
- **R1-UC1-E3**: Database error → `tests/web/test_data_routes.py:33` test_database_error_returns_error (Unit) ✅

### Full Flow Tests
- `R1-UC1` — ❌ No full-flow overview test

---

## Use Case Details: Manage data updates (ID: R1-UC2)

### Main Scenario
- **R1-UC2-S1**: Analyst navigates to Data Management page — ❌ (frontend navigation)
- **R1-UC2-S2**: System displays data freshness per category
  - `tests/web/test_data_routes.py:7` test_returns_all_categories (Unit)
- **R1-UC2-S3**: Analyst selects categories or "Update All"
  - `tests/web/test_data_routes.py:53` test_update_specific_category (Unit)
  - `tests/web/test_data_routes.py:36` test_update_all (Component)
- **R1-UC2-S4**: System triggers data pipeline
  - `tests/web/test_data_routes.py:36` test_update_all — verifies pipeline.run called (Component)
- **R1-UC2-S5**: System reports completion status
  - `tests/web/test_data_routes.py:36` test_update_all — checks status:"ok" (Component)
- **R1-UC2-S6**: System refreshes data freshness display — ⚠️ (verified via status:"ok" + results, no explicit re-query test)

### Extensions
- **R1-UC2-E1**: Tushare token invalid → `tests/web/test_data_routes.py:68` test_update_error_returns_error (Unit) ⚠️
- **R1-UC2-E2**: Category fails → `tests/web/test_data_routes.py:68` test_update_error_returns_error (Unit) ⚠️
- **R1-UC2-E3**: Force refresh → `tests/web/test_data_routes.py:79` test_update_with_force_refresh (Unit) ✅

### Full Flow Tests
- `R1-UC2` — `tests/web/test_integration.py:8` test_data_status_returns_json (Integration) ✅
- `R1-UC2` — `tests/web/test_integration.py:14` test_data_update_returns_json (Integration) ✅

---

## Use Case Details: Browse stock universe (ID: R1-UC3)

### Main Scenario
- **R1-UC3-S1**: Analyst opens Universe page — ❌ (frontend navigation)
- **R1-UC3-S2**: System loads current universe
  - `tests/web/test_universe_routes.py:7` test_returns_stocks_and_subsectors (Unit)
- **R1-UC3-S3**: System displays stock table
  - `tests/web/test_universe_routes.py:7` test_returns_stocks_and_subsectors (Component)
- **R1-UC3-S4**: System displays sub-sector pie chart — ❌ (frontend rendering, but subsector_counts data verified)
- **R1-UC3-S5**: Analyst filters by sub-sector or name
  - `tests/web/test_universe_routes.py:21` test_filter_by_subsector (Unit)

### Extensions
- **R1-UC3-E1**: No universe data → `tests/web/test_universe_routes.py:35` test_empty_universe (Unit) ✅
- **R1-UC3-E2**: Filter returns no results → `tests/web/test_universe_routes.py:35` test_filter_returns_empty_when_no_match (Unit) ✅

### Full Flow Tests
- `R1-UC3` — `tests/web/test_integration.py:22` test_universe_returns_json (Integration) ✅

---

## Use Case Details: Analyze factor exposures (ID: R1-UC4)

### Main Scenario
- **R1-UC4-S1**: Analyst opens Factor Analysis page — ❌ (frontend navigation)
- **R1-UC4-S2**: System loads latest factor matrix
  - `tests/web/test_factors_routes.py:7` test_returns_matrix_and_categories (Unit)
- **R1-UC4-S3**: System renders factor heatmap — ❌ (frontend rendering)
- **R1-UC4-S4**: System renders category-level summary
  - `tests/web/test_factors_routes.py:7` test_returns_matrix_and_categories (Component) ⚠️
- **R1-UC4-S5**: Analyst clicks factor for detail — ❌ (frontend interaction)
- **R1-UC4-S6**: System renders factor detail — ❌ (frontend rendering)

### Extensions
- **R1-UC4-E1**: Factors not computed — "Compute Factors"
  - `tests/web/test_factors_routes.py:20` test_empty_matrix (Unit) ✅
  - `tests/web/test_factors_routes.py:37` test_compute_returns_matrix (Unit) ✅
- **R1-UC4-E2**: IC data unavailable — ❌

### Full Flow Tests
- `R1-UC4` — `tests/web/test_integration.py:29` test_factors_get_returns_json (Integration) ✅
- `R1-UC4` — `tests/web/test_integration.py:36` test_factors_compute_returns_json (Integration) ✅

---

## Use Case Details: View trading signals (ID: R1-UC5)

### Main Scenario
- **R1-UC5-S1**: Analyst opens Signals page — ❌ (frontend navigation)
- **R1-UC5-S2**: System loads latest signal output
  - `tests/web/test_signals_routes.py:6` test_returns_signals_with_sentiment (Unit)
- **R1-UC5-S3**: System displays ranked table with scores, direction, sentiment
  - `tests/web/test_signals_routes.py:6` test_returns_signals_with_sentiment (Component)
- **R1-UC5-S4**: Analyst clicks stock row — ❌ (frontend interaction)
- **R1-UC5-S5**: System shows factor contributions
  - `tests/web/test_signals_routes.py:6` test_returns_signals_with_sentiment — verifies factor_contributions (Component)

### Extensions
- **R1-UC5-E1**: No signals → `tests/web/test_signals_routes.py:26` test_empty_signals (Unit) ✅
- **R1-UC5-E2**: Sentiment unavailable → `tests/web/test_signals_routes.py:33` test_sentiment_failure_still_returns_signals (Unit) ✅

### Full Flow Tests
- `R1-UC5` — `tests/web/test_integration.py:43` test_signals_returns_json (Integration) ✅

---

## Use Case Details: Monitor portfolio risk (ID: R1-UC6)

### Main Scenario
- **R1-UC6-S1**: Analyst opens Risk Monitor page — ❌ (frontend navigation)
- **R1-UC6-S2**: System loads portfolio state
  - `tests/web/test_risk_routes.py:6` test_returns_risk_data (Unit)
- **R1-UC6-S3**: System displays drawdown chart — ❌ (frontend rendering, drawdown data from report endpoint)
- **R1-UC6-S4**: System displays active risk alerts
  - `tests/web/test_risk_routes.py:6` test_returns_risk_data — verifies stop_loss type (Unit)
  - `tests/web/test_risk_routes.py:39` test_critical_metal_crash — verifies critical severity (Unit)
- **R1-UC6-S5**: System displays position-level risk metrics
  - `tests/web/test_risk_routes.py:6` test_returns_risk_data — verifies positions array (Component)

### Extensions
- **R1-UC6-E1**: No portfolio data → `tests/web/test_risk_routes.py:54` test_error_returns_error (Unit) ✅
- **R1-UC6-E2**: No active alerts → `tests/web/test_risk_routes.py:25` test_no_alerts (Unit) ✅

### Full Flow Tests
- `R1-UC6` — `tests/web/test_integration.py:50` test_risk_returns_json (Integration) ✅

---

## Use Case Details: Run and view backtest (ID: R1-UC7)

### Main Scenario
- **R1-UC7-S1**: Analyst opens Backtest page — ❌ (frontend navigation)
- **R1-UC7-S2**: Analyst sets start date, end date, initial capital
  - `tests/web/test_backtest_routes.py:9` test_run_returns_results (Component)
- **R1-UC7-S3**: Analyst clicks "Run Backtest"
  - `tests/web/test_backtest_routes.py:9` test_run_returns_results (Component)
- **R1-UC7-S4**: System executes backtest engine
  - `tests/web/test_backtest_routes.py:9` test_run_returns_results (Component)
- **R1-UC7-S5**: System returns metrics, NAV, trade log
  - `tests/web/test_backtest_routes.py:9` test_run_returns_results (Unit)
- **R1-UC7-S6**: System renders NAV curve, metrics cards, trade table — ❌ (frontend rendering)
- **R1-UC7-S7**: Analyst reviews performance — ❌ (frontend interaction)

### Extensions
- **R1-UC7-E1**: Insufficient data → `tests/web/test_backtest_routes.py:33` test_run_error (Unit) ✅
- **R1-UC7-E2**: Load previous result
  - `tests/web/test_backtest_routes.py:45` test_returns_latest_result (Unit) ✅
  - `tests/web/test_backtest_routes.py:61` test_no_results_returns_error (Unit) ✅

### Full Flow Tests
- `R1-UC7` — `tests/web/test_integration.py:56` test_backtest_run_returns_json (Integration) ✅
- `R1-UC7` — `tests/web/test_integration.py:65` test_backtest_latest_returns_json (Integration) ✅

---

## Use Case Details: View performance report (ID: R1-UC8)

### Main Scenario
- **R1-UC8-S1**: Analyst opens Report page — ❌ (frontend navigation)
- **R1-UC8-S2**: System loads latest backtest result as JSON
  - `tests/web/test_report_routes.py:9` test_returns_full_report (Unit)
- **R1-UC8-S3**: System renders metrics, NAV, drawdown, heatmap, holdings
  - `tests/web/test_report_routes.py:9` test_returns_full_report — verifies all data fields (Component)
- **R1-UC8-S4**: Analyst toggles chart views — ❌ (frontend interaction)
- **R1-UC8-S5**: Analyst exports report as HTML/PDF — ❌ (frontend-only feature)

### Extensions
- **R1-UC8-E1**: No backtest result → `tests/web/test_report_routes.py:34` test_no_data_returns_error (Unit) ✅
- **R1-UC8-E2**: PDF export fails — ❌ (frontend-only, no API endpoint)

### Full Flow Tests
- `R1-UC8` — `tests/web/test_integration.py:71` test_report_returns_json (Integration) ✅

---

## Use Case Details: Start the web server (ID: R1-UC9)

### Main Scenario
- **R1-UC9-S1**: Analyst runs `python main.py serve`
  - `tests/web/test_server_startup.py:42` test_serve_command_exists_in_main (Unit)
- **R1-UC9-S2**: System loads configuration
  - `tests/web/test_server_startup.py:9` test_app_has_config_in_state (Unit)
  - `tests/web/test_server_startup.py:28` test_config_has_web_section (Unit)
- **R1-UC9-S3**: System starts FastAPI server — ⚠️ (config verified, actual uvicorn start tested manually)
- **R1-UC9-S4**: System serves frontend and API endpoints
  - `tests/web/test_server_startup.py:13` test_app_registers_all_api_routes (Integration)
- **R1-UC9-S5**: System prints dashboard URL — ❌ (print output not tested)

### Extensions
- **R1-UC9-E1**: Port already in use — ❌ (uvicorn handles this, hard to unit test)
- **R1-UC9-E2**: Config file missing — uses defaults
  - `tests/web/test_server_startup.py:34` test_app_creation_with_missing_frontend_build (Unit) ⚠️

### Full Flow Tests
- `R1-UC9` — `tests/web/test_server_startup.py:13` test_app_registers_all_api_routes (Integration) ⚠️
