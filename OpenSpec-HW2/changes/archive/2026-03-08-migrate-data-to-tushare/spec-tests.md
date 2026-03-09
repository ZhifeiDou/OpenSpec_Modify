# Spec-Test Mapping: migrate-data-to-tushare
Generated: 2026-03-08

## Use Case ID Mapping

| ID | Use Case |
|----|----------|
| R1-UC1 | Configure Tushare API Token |
| R2-UC1 | Fetch Stock Daily Data via Tushare |
| R3-UC1 | Fetch Futures Daily Data via Tushare |
| R4-UC1 | Fetch Macro Indicators via Tushare |
| R5-UC1 | Fetch Fund Flow Data via Tushare |
| R6-UC1 | Fetch Industry Stocks for Universe Classification |
| R7-UC1 | Run Full Data Update Pipeline |

## Requirement Traceability Matrix

| ID | Requirement | Type | Test Type | Test Case | Status |
|----|-------------|------|-----------|-----------|--------|
| R1-UC1 | Configure Tushare API Token Full Flow | Flow | Integration | | ❌ |
| R1-UC1-S1 | Developer copies .env.example to .env | Step | | (manual/setup step) | ❌ |
| R1-UC1-S2 | Developer pastes token into TUSHARE_TOKEN field | Step | | (manual/setup step) | ❌ |
| R1-UC1-S3 | System loads token from env var on startup | Step | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_from_env` | ✅ |
| R1-UC1-S4 | System validates token via trade_cal | Step | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_from_env` | ✅ |
| R1-UC1-S5 | System confirms token valid and proceeds | Step | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_from_env` | ✅ |
| R1-UC1-E1 | No TUSHARE_TOKEN env var → error with instructions | Extension | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_missing_token_raises_error` | ✅ |
| R1-UC1-E2 | Token invalid/expired → auth failure with link | Extension | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_validation_failure` | ✅ |
| R2-UC1 | Fetch Stock Daily Full Flow | Flow | Integration | | ❌ |
| R2-UC1-S1 | System determines last update date from metadata | Step | Unit | `tests/data/test_tushare_pipeline.py::TestStockDailyIncremental::test_incremental_update_uses_last_date` | ✅ |
| R2-UC1-S2 | System converts 6-digit symbol to Tushare format | Step | Unit | `tests/data/test_tushare_source.py::TestToTushareCode::test_shenzhen_stock_0_prefix` | ✅ |
| R2-UC1-S2 | System converts 6-digit symbol to Tushare format | Step | Unit | `tests/data/test_tushare_source.py::TestToTushareCode::test_shanghai_stock_6_prefix` | ✅ |
| R2-UC1-S2 | System converts 6-digit symbol to Tushare format | Step | Unit | `tests/data/test_tushare_source.py::TestToTushareCode::test_shenzhen_stock_3_prefix` | ✅ |
| R2-UC1-S2 | System converts 6-digit symbol to Tushare format | Step | Unit | `tests/data/test_tushare_source.py::TestToTushareCode::test_shanghai_stock_9_prefix` | ✅ |
| R2-UC1-S3 | System calls pro.daily() | Step | Component | `tests/data/test_tushare_source.py::TestFetchStockDaily::test_fetch_stock_daily_success` | ✅ |
| R2-UC1-S4 | System maps Tushare columns to internal schema | Step | Component | `tests/data/test_tushare_source.py::TestFetchStockDaily::test_fetch_stock_daily_success` | ✅ |
| R2-UC1-S5 | System validates data and stores in SQLite | Step | Component | `tests/data/test_tushare_pipeline.py::TestStockDailyIncremental::test_stock_data_stored_in_sqlite` | ✅ |
| R2-UC1-S6 | System updates last-updated metadata | Step | Unit | `tests/data/test_tushare_pipeline.py::TestStockDailyIncremental::test_metadata_updated_after_store` | ✅ |
| R2-UC1-E1 | API rate limit → retries | Extension | Unit | `tests/data/test_tushare_source.py::TestRetryBehavior::test_retry_then_succeed` | ✅ |
| R2-UC1-E2 | All retries exhausted → skip, continue next | Extension | Component | `tests/data/test_tushare_pipeline.py::TestStockDailyRetryAndSkip::test_skip_on_fetch_failure_continues` | ✅ |
| R2-UC1-E3 | Empty response → skip with log | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchStockDaily::test_fetch_stock_daily_empty` | ✅ |
| R3-UC1 | Fetch Futures Daily Full Flow | Flow | Integration | | ❌ |
| R3-UC1-S1 | System iterates over configured metals | Step | Component | `tests/data/test_tushare_pipeline.py::TestFuturesPipelineIteration::test_all_metals_fetched` | ✅ |
| R3-UC1-S1 | System iterates over configured metals | Step | Unit | `tests/data/test_pipeline_silver.py::TestSilverInMetalsList::test_ag_in_metals_list` | ✅ |
| R3-UC1-S2 | System maps metal code to Tushare contract code | Step | Component | `tests/data/test_tushare_source.py::TestFetchFuturesDaily::test_fetch_copper_futures` | ✅ |
| R3-UC1-S3 | System calls pro.fut_daily() | Step | Component | `tests/data/test_tushare_source.py::TestFetchFuturesDaily::test_fetch_copper_futures` | ✅ |
| R3-UC1-S3 | System calls pro.fut_daily() | Step | Component | `tests/data/test_pipeline_silver.py::TestSilverFuturesFetch::test_pipeline_calls_fetch_for_ag` | ✅ |
| R3-UC1-S4 | System maps Tushare columns (oi → open_interest) | Step | Component | `tests/data/test_tushare_source.py::TestFetchFuturesDaily::test_fetch_copper_futures` | ✅ |
| R3-UC1-S5 | System validates and stores data | Step | Component | `tests/data/test_pipeline_silver.py::TestSilverFuturesFetch::test_fetch_returns_ag_data` | ✅ |
| R3-UC1-E1 | Metal code not mappable → log warning, skip | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchFuturesDaily::test_unmapped_metal_returns_empty` | ✅ |
| R3-UC1-E2 | API failure → retry, skip on exhaustion | Extension | Component | `tests/data/test_pipeline_silver.py::TestSilverApiFail::test_ag_fetch_exception_continues` | ✅ |
| R4-UC1 | Fetch Macro Indicators Full Flow | Flow | Integration | | ❌ |
| R4-UC1-S1 | System iterates over macro indicators | Step | Component | `tests/data/test_tushare_pipeline.py::TestMacroPipelineIteration::test_all_indicators_fetched` | ✅ |
| R4-UC1-S2 | System maps indicator to Tushare function (PMI) | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_pmi` | ✅ |
| R4-UC1-S2 | System maps indicator to Tushare function (M1) | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_m1` | ✅ |
| R4-UC1-S2 | System maps indicator to Tushare function (CPI) | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_cpi` | ✅ |
| R4-UC1-S2 | System maps indicator to Tushare function (PPI) | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_ppi` | ✅ |
| R4-UC1-S3 | System calls Tushare function | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_pmi` | ✅ |
| R4-UC1-S4 | System extracts value column, normalizes (date, value) | Step | Component | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_pmi` | ✅ |
| R4-UC1-S5 | System stores in SQLite | Step | Component | `tests/data/test_tushare_pipeline.py::TestMacroPipelineStorage::test_macro_data_counted_in_result` | ✅ |
| R4-UC1-E1 | Unknown indicator → log, skip | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchMacro::test_fetch_unsupported_indicator` | ✅ |
| R4-UC1-E2 | Monthly YYYYMM → converts to YYYY-MM-01 | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchMacro::test_monthly_date_normalized_to_first_of_month` | ✅ |
| R5-UC1 | Fetch Fund Flow Full Flow | Flow | Integration | | ❌ |
| R5-UC1-S1 | System calls pro.margin_detail() for margin | Step | Component | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_with_both_sources` | ✅ |
| R5-UC1-S2 | System extracts rzrqye as margin_balance | Step | Component | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_with_both_sources` | ✅ |
| R5-UC1-S3 | System calls pro.moneyflow_hsgt() for northbound | Step | Component | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_with_both_sources` | ✅ |
| R5-UC1-S4 | System extracts north_money as northbound_net_buy | Step | Component | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_with_both_sources` | ✅ |
| R5-UC1-S5 | System joins on date and stores | Step | Component | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_with_both_sources` | ✅ |
| R5-UC1-E1 | Stock not in margin program → NaN for margin | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_no_margin` | ✅ |
| R5-UC1-E2 | HSGT unavailable weekends → skip non-trading | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchFundFlow::test_fetch_fund_flow_only_trading_days` | ✅ |
| R6-UC1 | Fetch Industry Stocks Full Flow | Flow | Integration | | ❌ |
| R6-UC1-S1 | System calls Tushare index member API | Step | Unit | `tests/data/test_tushare_source.py::TestFetchIndustryStocks::test_fetch_via_index_member` | ✅ |
| R6-UC1-S2 | System normalizes column names | Step | Unit | `tests/data/test_tushare_source.py::TestFetchIndustryStocks::test_fetch_via_index_member` | ✅ |
| R6-UC1-S3 | System returns DataFrame | Step | Unit | `tests/data/test_tushare_source.py::TestFetchIndustryStocks::test_fetch_via_index_member` | ✅ |
| R6-UC1-E1 | No direct Shenwan L2 API → fallback stock_basic | Extension | Unit | `tests/data/test_tushare_source.py::TestFetchIndustryStocks::test_fetch_via_stock_basic_fallback` | ✅ |
| R7-UC1 | Run Full Data Update Pipeline | Flow | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_full_pipeline_runs_all_categories` | ✅ |
| R7-UC1-S1 | System validates Tushare token on startup | Step | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_from_env` | ✅ |
| R7-UC1-S2 | System updates stock daily data | Step | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_full_pipeline_runs_all_categories` | ✅ |
| R7-UC1-S3 | System updates futures data | Step | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_full_pipeline_runs_all_categories` | ✅ |
| R7-UC1-S4 | System updates macro indicators | Step | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_full_pipeline_runs_all_categories` | ✅ |
| R7-UC1-S5 | System updates fund flow data | Step | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_full_pipeline_runs_all_categories` | ✅ |
| R7-UC1-S6 | System prints update summary | Step | Integration | `tests/data/test_tushare_pipeline.py::TestPipelineSummaryOutput::test_summary_printed` | ✅ |
| R7-UC1-E1 | Token invalid → abort | Extension | Unit | `tests/data/test_tushare_source.py::TestTokenLoading::test_token_validation_failure` | ✅ |
| R7-UC1-E2 | Individual category fails → continues | Extension | Integration | `tests/data/test_tushare_pipeline.py::TestFullPipelineFlow::test_category_failure_continues` | ✅ |

## Use Case Details

### Use Case: Configure Tushare API Token (R1-UC1)

#### Main Scenario
- **R1-UC1-S1**: Developer copies .env.example to .env (manual setup step, not testable)
- **R1-UC1-S2**: Developer pastes token (manual setup step, not testable)
- **R1-UC1-S3**: System loads token from env var
  - `tests/data/test_tushare_source.py:82` test_token_from_env (Unit)
- **R1-UC1-S4**: System validates token via trade_cal
  - `tests/data/test_tushare_source.py:82` test_token_from_env (Unit) — validates as part of init
- **R1-UC1-S5**: System confirms token valid
  - `tests/data/test_tushare_source.py:82` test_token_from_env (Unit) — asserts no error

#### Extensions
- **R1-UC1-E1**: No env var → error with instructions
  - `tests/data/test_tushare_source.py:71` test_missing_token_raises_error (Unit)
- **R1-UC1-E2**: Invalid token → auth failure
  - `tests/data/test_tushare_source.py:94` test_token_validation_failure (Unit)

#### Full Flow Tests
- None (manual setup steps make full-flow integration testing impractical)

---

### Use Case: Fetch Stock Daily Data via Tushare (R2-UC1)

#### Main Scenario
- **R2-UC1-S1**: Determine last update date
  - `tests/data/test_tushare_pipeline.py` test_incremental_update_uses_last_date (Unit)
- **R2-UC1-S2**: Convert 6-digit symbol to Tushare format
  - `tests/data/test_tushare_source.py:25` test_shenzhen_stock_0_prefix (Unit)
  - `tests/data/test_tushare_source.py:28` test_shenzhen_stock_3_prefix (Unit)
  - `tests/data/test_tushare_source.py:31` test_shanghai_stock_6_prefix (Unit)
  - `tests/data/test_tushare_source.py:34` test_shanghai_stock_9_prefix (Unit)
  - `tests/data/test_tushare_source.py:37` test_already_tushare_format (Unit)
- **R2-UC1-S3**: Call pro.daily()
  - `tests/data/test_tushare_source.py:121` test_fetch_stock_daily_success (Component)
- **R2-UC1-S4**: Map columns (vol→volume, trade_date→date)
  - `tests/data/test_tushare_source.py:121` test_fetch_stock_daily_success (Component)
- **R2-UC1-S5**: Validate and store in SQLite
  - `tests/data/test_tushare_pipeline.py` test_stock_data_stored_in_sqlite (Component)
- **R2-UC1-S6**: Update last-updated metadata
  - `tests/data/test_tushare_pipeline.py` test_metadata_updated_after_store (Unit)

#### Extensions
- **R2-UC1-E1**: API rate limit → retries
  - `tests/data/test_tushare_source.py` test_retry_then_succeed (Unit)
- **R2-UC1-E2**: All retries exhausted → skip, continue
  - `tests/data/test_tushare_pipeline.py` test_skip_on_fetch_failure_continues (Component)
- **R2-UC1-E3**: Empty response → skip
  - `tests/data/test_tushare_source.py:141` test_fetch_stock_daily_empty (Unit)

#### Full Flow Tests
- None

---

### Use Case: Fetch Futures Daily Data via Tushare (R3-UC1)

#### Main Scenario
- **R3-UC1-S1**: Iterate configured metals
  - `tests/data/test_tushare_pipeline.py` test_all_metals_fetched (Component)
  - `tests/data/test_pipeline_silver.py:54` test_ag_in_metals_list (Unit)
  - `tests/data/test_pipeline_silver.py:61` test_au_also_in_metals_list (Unit)
- **R3-UC1-S2**: Map metal code to Tushare contract code
  - `tests/data/test_tushare_source.py:164` test_fetch_copper_futures (Component)
- **R3-UC1-S3**: Call pro.fut_daily()
  - `tests/data/test_tushare_source.py:164` test_fetch_copper_futures (Component)
  - `tests/data/test_pipeline_silver.py:73` test_pipeline_calls_fetch_for_ag (Component)
- **R3-UC1-S4**: Map columns (oi→open_interest)
  - `tests/data/test_tushare_source.py:164` test_fetch_copper_futures (Component)
- **R3-UC1-S5**: Validate and store data
  - `tests/data/test_pipeline_silver.py:85` test_fetch_returns_ag_data (Component)

#### Extensions
- **R3-UC1-E1**: Unmappable metal → warning, skip
  - `tests/data/test_tushare_source.py:184` test_unmapped_metal_returns_empty (Unit)
- **R3-UC1-E2**: API failure → retry, skip
  - `tests/data/test_pipeline_silver.py:122` test_ag_fetch_exception_continues (Component)

#### Full Flow Tests
- None

---

### Use Case: Fetch Macro Indicators via Tushare (R4-UC1)

#### Main Scenario
- **R4-UC1-S1**: Iterate macro indicators
  - `tests/data/test_tushare_pipeline.py` test_all_indicators_fetched (Component)
- **R4-UC1-S2**: Map indicator to Tushare function
  - `tests/data/test_tushare_source.py:205` test_fetch_pmi (Component)
  - `tests/data/test_tushare_source.py:217` test_fetch_m1 (Component)
  - `tests/data/test_tushare_source.py` test_fetch_cpi (Component)
  - `tests/data/test_tushare_source.py` test_fetch_ppi (Component)
- **R4-UC1-S3**: Call Tushare function with date range
  - `tests/data/test_tushare_source.py:205` test_fetch_pmi (Component)
- **R4-UC1-S4**: Extract value column, normalize to (date, value)
  - `tests/data/test_tushare_source.py:205` test_fetch_pmi (Component)
- **R4-UC1-S5**: Store in SQLite
  - `tests/data/test_tushare_pipeline.py` test_macro_data_counted_in_result (Component)

#### Extensions
- **R4-UC1-E1**: Unknown indicator → log, skip
  - `tests/data/test_tushare_source.py:229` test_fetch_unsupported_indicator (Unit)
- **R4-UC1-E2**: Monthly YYYYMM → YYYY-MM-01
  - `tests/data/test_tushare_source.py` test_monthly_date_normalized_to_first_of_month (Unit)

#### Full Flow Tests
- None

---

### Use Case: Fetch Fund Flow Data via Tushare (R5-UC1)

#### Main Scenario
- **R5-UC1-S1**: Call pro.margin_detail()
  - `tests/data/test_tushare_source.py:250` test_fetch_fund_flow_with_both_sources (Component)
- **R5-UC1-S2**: Extract rzrqye as margin_balance
  - `tests/data/test_tushare_source.py:250` test_fetch_fund_flow_with_both_sources (Component)
- **R5-UC1-S3**: Call pro.moneyflow_hsgt()
  - `tests/data/test_tushare_source.py:250` test_fetch_fund_flow_with_both_sources (Component)
- **R5-UC1-S4**: Extract north_money as northbound_net_buy
  - `tests/data/test_tushare_source.py:250` test_fetch_fund_flow_with_both_sources (Component)
- **R5-UC1-S5**: Join on date and store
  - `tests/data/test_tushare_source.py:250` test_fetch_fund_flow_with_both_sources (Component)

#### Extensions
- **R5-UC1-E1**: Stock not in margin → NaN for margin fields
  - `tests/data/test_tushare_source.py:268` test_fetch_fund_flow_no_margin (Unit)
- **R5-UC1-E2**: HSGT unavailable weekends → only trading days returned
  - `tests/data/test_tushare_source.py` test_fetch_fund_flow_only_trading_days (Unit)

#### Full Flow Tests
- None

---

### Use Case: Fetch Industry Stocks for Universe Classification (R6-UC1)

#### Main Scenario
- **R6-UC1-S1**: Call Tushare index member API
  - `tests/data/test_tushare_source.py` test_fetch_via_index_member (Unit)
- **R6-UC1-S2**: Normalize column names
  - `tests/data/test_tushare_source.py` test_fetch_via_index_member (Unit)
- **R6-UC1-S3**: Return DataFrame
  - `tests/data/test_tushare_source.py` test_fetch_via_index_member (Unit)

#### Extensions
- **R6-UC1-E1**: No Shenwan L2 API → fallback stock_basic
  - `tests/data/test_tushare_source.py` test_fetch_via_stock_basic_fallback (Unit)

#### Full Flow Tests
- None

---

### Use Case: Run Full Data Update Pipeline (R7-UC1)

#### Main Scenario
- **R7-UC1-S1**: Validate Tushare token
  - `tests/data/test_tushare_source.py:82` test_token_from_env (Unit)
- **R7-UC1-S2**: Update stock daily data
  - `tests/data/test_tushare_pipeline.py` test_full_pipeline_runs_all_categories (Integration)
- **R7-UC1-S3**: Update futures data
  - `tests/data/test_tushare_pipeline.py` test_full_pipeline_runs_all_categories (Integration)
- **R7-UC1-S4**: Update macro indicators
  - `tests/data/test_tushare_pipeline.py` test_full_pipeline_runs_all_categories (Integration)
- **R7-UC1-S5**: Update fund flow data
  - `tests/data/test_tushare_pipeline.py` test_full_pipeline_runs_all_categories (Integration)
- **R7-UC1-S6**: Print update summary
  - `tests/data/test_tushare_pipeline.py` test_summary_printed (Integration)

#### Extensions
- **R7-UC1-E1**: Token invalid → abort
  - `tests/data/test_tushare_source.py:94` test_token_validation_failure (Unit)
- **R7-UC1-E2**: Individual category fails → continues
  - `tests/data/test_tushare_pipeline.py` test_category_failure_continues (Integration)

#### Full Flow Tests
- `R7-UC1` — "Run full pipeline" → `tests/data/test_tushare_pipeline.py` test_full_pipeline_runs_all_categories (Integration)
