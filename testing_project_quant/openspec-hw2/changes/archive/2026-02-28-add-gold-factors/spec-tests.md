# Spec-Test Mapping: add-gold-factors
Generated: 2026-02-28

## Use Case ID Mapping

| ID | Use Case |
|----|----------|
| R1-UC1 | Compute gold cross-metal ratio factors for stock scoring |
| R2-UC1 | Fetch and store silver futures data |
| R3-UC1 | Fix gold and silver inventory data mapping |

### R1-UC1 Steps
| ID | Description |
|----|-------------|
| R1-UC1-S1 | Scoring pipeline iterates over registered factors and reaches GoldSilverRatioFactor |
| R1-UC1-S2 | Factor reads gold (au) and silver (ag) futures close prices for the trailing window |
| R1-UC1-S3 | Factor computes the Au/Ag price ratio and its deviation from the rolling mean |
| R1-UC1-S4 | Factor assigns the deviation score to gold-subsector stocks; non-gold stocks receive NaN |
| R1-UC1-S5 | Scoring pipeline proceeds to GoldCopperRatioFactor |
| R1-UC1-S6 | Factor reads gold (au) and copper (cu) futures close prices and computes Au/Cu ratio rate-of-change |
| R1-UC1-S7 | Factor assigns the rate-of-change score to gold-subsector stocks |
| R1-UC1-S8 | Both factor outputs are combined with existing commodity factors in the weighted scoring model |

### R1-UC1 Extensions
| ID | Description |
|----|-------------|
| R1-UC1-E1 | 2a. Silver futures data is missing or has fewer rows than required lookback |
| R1-UC1-E2 | 6a. Copper futures data is missing or insufficient |
| R1-UC1-E3 | 4a. No stocks are classified under the gold subsector |

### R2-UC1 Steps
| ID | Description |
|----|-------------|
| R2-UC1-S1 | Data pipeline iterates over the _metals list, which now includes "ag" |
| R2-UC1-S2 | Pipeline calls fetch_futures_daily("ag", start_date, end_date) |
| R2-UC1-S3 | AKShare returns silver continuous contract (ag0) daily data |
| R2-UC1-S4 | Pipeline stores the data in futures_daily table |

### R2-UC1 Extensions
| ID | Description |
|----|-------------|
| R2-UC1-E1 | 3a. AKShare returns empty data for ag0 |
| R2-UC1-E2 | 3b. API call fails after retries |

### R3-UC1 Steps
| ID | Description |
|----|-------------|
| R3-UC1-S1 | Pipeline calls fetch_inventory("au") |
| R3-UC1-S2 | metal_names dict resolves "au" to "黄金" |
| R3-UC1-S3 | AKShare returns gold inventory data |
| R3-UC1-S4 | Pipeline stores inventory data with metal = 'au' |
| R3-UC1-S5 | Same flow repeats for "ag" → "白银" |

### R3-UC1 Extensions
| ID | Description |
|----|-------------|
| R3-UC1-E1 | 3a. AKShare does not have gold inventory data |
| R3-UC1-E2 | 5a. AKShare does not have silver inventory data |

## Requirement Traceability Matrix

| ID | Requirement | Type | Test Type | Test Case | Status |
|----|-------------|------|-----------|-----------|--------|
| R1-UC1 | Compute gold cross-metal ratio factors Full Flow | Flow | Integration | `tests/factors/test_gold_factors.py::TestScoringIntegration::test_gold_factors_in_scoring_model` | ⚠️ |
| R1-UC1-S1 | Scoring pipeline reaches GoldSilverRatioFactor | Step | Unit | `tests/factors/test_gold_factors.py::TestFactorRegistration::test_gold_silver_ratio_registered` | ✅ |
| R1-UC1-S2 | Factor reads au and ag futures close prices | Step | Unit | `tests/factors/test_gold_factors.py::TestGoldSilverRatioFactor::test_correct_ratio_deviation` | ✅ |
| R1-UC1-S3 | Factor computes Au/Ag ratio deviation from rolling mean | Step | Unit | `tests/factors/test_gold_factors.py::TestGoldSilverRatioFactor::test_correct_ratio_deviation` | ✅ |
| R1-UC1-S4 | Gold-subsector stocks get score; non-gold get NaN | Step | Unit | `tests/factors/test_gold_factors.py::TestGoldSilverRatioFactor::test_nan_for_non_gold_stocks` | ✅ |
| R1-UC1-S5 | Scoring pipeline proceeds to GoldCopperRatioFactor | Step | Unit | `tests/factors/test_gold_factors.py::TestFactorRegistration::test_gold_copper_ratio_registered` | ✅ |
| R1-UC1-S6 | Factor reads au and cu futures and computes Au/Cu ratio RoC | Step | Unit | `tests/factors/test_gold_factors.py::TestGoldCopperRatioFactor::test_correct_rate_of_change` | ✅ |
| R1-UC1-S7 | Gold-subsector stocks get GCR score; non-gold get NaN | Step | Unit | `tests/factors/test_gold_factors.py::TestGoldCopperRatioFactor::test_nan_for_non_gold_stocks` | ✅ |
| R1-UC1-S8 | Both factors combined with existing commodity factors in scoring | Step | Integration | `tests/factors/test_gold_factors.py::TestScoringIntegration::test_gold_factors_in_scoring_model` | ✅ |
| R1-UC1-E1 | Silver futures data missing or insufficient | Extension | Unit | `tests/factors/test_gold_factors.py::TestGoldSilverRatioFactor::test_nan_with_insufficient_data` | ✅ |
| R1-UC1-E2 | Copper futures data missing or insufficient | Extension | Unit | `tests/factors/test_gold_factors.py::TestGoldCopperRatioFactor::test_nan_with_insufficient_data` | ✅ |
| R1-UC1-E3 | No gold-subsector stocks in universe | Extension | Unit | `tests/factors/test_gold_factors.py::TestNoGoldStocksInUniverse::test_no_gold_stocks_returns_nan_for_all` | ✅ |
| R2-UC1 | Fetch and store silver futures data Full Flow | Flow | Component | `tests/data/test_pipeline_silver.py::TestSilverFuturesFetch::test_fetch_returns_ag0_data` | ✅ |
| R2-UC1-S1 | _metals list includes "ag" | Step | Unit | `tests/data/test_pipeline_silver.py::TestSilverInMetalsList::test_ag_in_metals_list` | ✅ |
| R2-UC1-S2 | Pipeline calls fetch_futures_daily("ag", ...) | Step | Unit | `tests/data/test_pipeline_silver.py::TestSilverFuturesFetch::test_pipeline_calls_fetch_for_ag` | ✅ |
| R2-UC1-S3 | AKShare returns ag0 daily data | Step | Unit | `tests/data/test_pipeline_silver.py::TestSilverFuturesFetch::test_fetch_returns_ag0_data` | ✅ |
| R2-UC1-S4 | Pipeline stores silver data in futures_daily | Step | Unit | `tests/data/test_pipeline_silver.py::TestSilverFuturesStorage::test_silver_data_stored_with_metal_ag` | ✅ |
| R2-UC1-E1 | AKShare returns empty data for ag0 | Extension | Unit | `tests/data/test_pipeline_silver.py::TestSilverEmptyData::test_empty_ag_data_no_crash`, `tests/data/test_pipeline_silver.py::TestSilverEmptyData::test_empty_ag_data_no_storage` | ✅ |
| R2-UC1-E2 | API call fails after retries | Extension | Unit | `tests/data/test_pipeline_silver.py::TestSilverApiFail::test_ag_fetch_exception_continues` | ✅ |
| R3-UC1 | Fix gold/silver inventory mapping Full Flow | Flow | Component | `tests/data/test_pipeline_silver.py::TestInventoryMappingSource::test_fetch_inventory_au_uses_huangjin`, `tests/data/test_pipeline_silver.py::TestInventoryReturnsData::test_gold_inventory_data_returned` | ⚠️ |
| R3-UC1-S1 | fetch_inventory("au") resolves to correct API call | Step | Unit | `tests/data/test_pipeline_silver.py::TestInventoryMappingSource::test_fetch_inventory_au_uses_huangjin` | ✅ |
| R3-UC1-S2 | metal_names resolves "au" to "黄金" | Step | Unit | `tests/factors/test_gold_factors.py::TestInventoryMapping::test_gold_inventory_mapping`, `tests/data/test_pipeline_silver.py::TestInventoryMappingSource::test_fetch_inventory_au_uses_huangjin` | ✅ |
| R3-UC1-S3 | AKShare returns gold inventory data | Step | Unit | `tests/data/test_pipeline_silver.py::TestInventoryReturnsData::test_gold_inventory_data_returned` | ✅ |
| R3-UC1-S4 | Pipeline stores gold inventory with metal = 'au' | Step | Unit | | ⚠️ |
| R3-UC1-S5 | Same flow for "ag" → "白银" | Step | Unit | `tests/factors/test_gold_factors.py::TestInventoryMapping::test_silver_inventory_mapping`, `tests/data/test_pipeline_silver.py::TestInventoryMappingSource::test_fetch_inventory_ag_uses_baiyin` | ✅ |
| R3-UC1-E1 | AKShare has no gold inventory data | Extension | Unit | `tests/data/test_pipeline_silver.py::TestInventoryEmptyData::test_empty_gold_inventory` | ✅ |
| R3-UC1-E2 | AKShare has no silver inventory data | Extension | Unit | `tests/data/test_pipeline_silver.py::TestInventoryEmptyData::test_empty_silver_inventory` | ✅ |

## Use Case Details: Compute gold cross-metal ratio factors (ID: R1-UC1)

### Main Scenario
- **R1-UC1-S1**: Scoring pipeline reaches GoldSilverRatioFactor
  - `tests/factors/test_gold_factors.py:67` test_gold_silver_ratio_registered (Unit)
- **R1-UC1-S2**: Factor reads au and ag futures close prices
  - `tests/factors/test_gold_factors.py:141` test_correct_ratio_deviation (Unit)
- **R1-UC1-S3**: Factor computes Au/Ag ratio deviation from rolling mean
  - `tests/factors/test_gold_factors.py:141` test_correct_ratio_deviation (Unit)
- **R1-UC1-S4**: Gold-subsector stocks get score; non-gold get NaN
  - `tests/factors/test_gold_factors.py:161` test_nan_for_non_gold_stocks (Unit)
- **R1-UC1-S5**: Scoring pipeline proceeds to GoldCopperRatioFactor
  - `tests/factors/test_gold_factors.py:75` test_gold_copper_ratio_registered (Unit)
- **R1-UC1-S6**: Factor reads au and cu futures and computes Au/Cu ratio RoC
  - `tests/factors/test_gold_factors.py:186` test_correct_rate_of_change (Unit)
- **R1-UC1-S7**: Gold-subsector stocks get GCR score; non-gold get NaN
  - `tests/factors/test_gold_factors.py:203` test_nan_for_non_gold_stocks (Unit)
- **R1-UC1-S8**: Both factors combined with existing commodity factors in scoring
  - `tests/factors/test_gold_factors.py:105` test_gold_factors_in_scoring_model (Integration)

### Extensions
- **R1-UC1-E1**: Silver futures data missing or insufficient
  - `tests/factors/test_gold_factors.py:173` test_nan_with_insufficient_data (Unit)
- **R1-UC1-E2**: Copper futures data missing or insufficient
  - `tests/factors/test_gold_factors.py:215` test_nan_with_insufficient_data (Unit)
- **R1-UC1-E3**: No gold-subsector stocks in universe
  - `tests/factors/test_gold_factors.py:86` test_no_gold_stocks_returns_nan_for_all (Unit)

### Full Flow Tests
- `R1-UC1` — "Compute gold cross-metal ratio factors" -> `tests/factors/test_gold_factors.py:105` test_gold_factors_in_scoring_model (Integration) ⚠️ covers S8 but not full pipeline flow

## Use Case Details: Fetch and store silver futures data (ID: R2-UC1)

### Main Scenario
- **R2-UC1-S1**: _metals list includes "ag"
  - `tests/data/test_pipeline_silver.py:70` test_ag_in_metals_list (Unit)
- **R2-UC1-S2**: Pipeline calls fetch_futures_daily("ag", ...)
  - `tests/data/test_pipeline_silver.py:85` test_pipeline_calls_fetch_for_ag (Unit)
- **R2-UC1-S3**: AKShare returns ag0 daily data
  - `tests/data/test_pipeline_silver.py:96` test_fetch_returns_ag0_data (Unit)
- **R2-UC1-S4**: Pipeline stores silver data in futures_daily
  - `tests/data/test_pipeline_silver.py:118` test_silver_data_stored_with_metal_ag (Unit)

### Extensions
- **R2-UC1-E1**: AKShare returns empty data for ag0
  - `tests/data/test_pipeline_silver.py:140` test_empty_ag_data_no_crash (Unit)
  - `tests/data/test_pipeline_silver.py:148` test_empty_ag_data_no_storage (Unit)
- **R2-UC1-E2**: API call fails after retries
  - `tests/data/test_pipeline_silver.py:162` test_ag_fetch_exception_continues (Unit)

### Full Flow Tests
- `R2-UC1` — "Fetch and store silver futures data" -> `tests/data/test_pipeline_silver.py:96` test_fetch_returns_ag0_data (Component) — covers S2-S4 with mocked source

## Use Case Details: Fix gold/silver inventory mapping (ID: R3-UC1)

### Main Scenario
- **R3-UC1-S1**: fetch_inventory("au") resolves to correct API call
  - `tests/data/test_pipeline_silver.py:189` test_fetch_inventory_au_uses_huangjin (Unit)
- **R3-UC1-S2**: metal_names resolves "au" to "黄金"
  - `tests/factors/test_gold_factors.py:228` test_gold_inventory_mapping (Unit)
  - `tests/data/test_pipeline_silver.py:189` test_fetch_inventory_au_uses_huangjin (Unit)
- **R3-UC1-S3**: AKShare returns gold inventory data
  - `tests/data/test_pipeline_silver.py:206` test_gold_inventory_data_returned (Unit)
- **R3-UC1-S4**: Pipeline stores gold inventory with metal = 'au' -> ⚠️ no _update_inventory in pipeline
- **R3-UC1-S5**: Same flow for "ag" → "白银"
  - `tests/factors/test_gold_factors.py:238` test_silver_inventory_mapping (Unit)
  - `tests/data/test_pipeline_silver.py:197` test_fetch_inventory_ag_uses_baiyin (Unit)
  - `tests/data/test_pipeline_silver.py:214` test_silver_inventory_data_returned (Unit)

### Extensions
- **R3-UC1-E1**: AKShare has no gold inventory data
  - `tests/data/test_pipeline_silver.py:224` test_empty_gold_inventory (Unit)
- **R3-UC1-E2**: AKShare has no silver inventory data
  - `tests/data/test_pipeline_silver.py:232` test_empty_silver_inventory (Unit)

### Full Flow Tests
- `R3-UC1` — "Fix gold/silver inventory mapping" -> ⚠️ partial coverage (source-level tests; no pipeline-level _update_inventory method exists)
