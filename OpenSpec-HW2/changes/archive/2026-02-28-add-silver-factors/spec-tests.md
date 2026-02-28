# Spec-Test Mapping: add-silver-factors
Generated: 2026-02-28

## Use Case ID Mapping

| ID | Use Case / Step / Extension |
|----|-----------------------------|
| R1-UC1 | Compute silver cross-metal ratio factors during scoring |
| R1-UC1-S1 | Factor engine discovers SilverGoldRatioFactor and SilverCopperRatioFactor via @register_factor registry |
| R1-UC1-S2 | For SilverGoldRatioFactor, engine calls compute(universe, date, store, config) |
| R1-UC1-S3 | Factor reads silver_cross_metal.sgr_lookback from config (default 60) |
| R1-UC1-S4 | Factor fetches "ag" and "au" futures close prices from the data store |
| R1-UC1-S5 | Factor computes the Ag/Au ratio series, calculates rolling mean, derives deviation |
| R1-UC1-S6 | Factor returns deviation value for silver-subsector stocks and NaN for all others |
| R1-UC1-S7 | Steps 2–6 repeat analogously for SilverCopperRatioFactor using "ag" and "cu" prices |
| R1-UC1-S8 | Factor engine merges both silver factor columns into the scoring matrix |
| R1-UC1-E1 | 4a. Insufficient futures data: logs warning, returns NaN for all stocks |
| R1-UC1-E2 | 4b. One metal has data but other does not: returns NaN for all stocks |
| R1-UC1-E3 | 6a. Stock's subsector not "ag": returns NaN for that stock |
| R1-UC2 | Classify silver stocks into the silver subsector |
| R1-UC2-S1 | Classifier scans stock's name and industry text against _SUBSECTOR_KEYWORDS |
| R1-UC2-S2 | Text matches a silver keyword |
| R1-UC2-S3 | Classifier returns "silver" as the subsector |
| R1-UC2-S4 | Downstream code looks up SUBSECTOR_METAL_MAP["silver"] and gets "ag" |
| R1-UC2-E1 | 2a. Stock name contains both silver and gold keywords: returns whichever matches first |
| R1-UC2-E2 | 2b. No silver keyword matches: classified under another subsector or "other" |
| R1-UC3 | Configure silver factor lookback windows |
| R1-UC3-S1 | Researcher sets factors.silver_cross_metal.sgr_lookback to 90 |
| R1-UC3-S2 | Factor engine loads config and passes to SilverGoldRatioFactor.compute() |
| R1-UC3-S3 | Factor reads lookback = 90 from config and uses 90-day rolling mean window |
| R1-UC3-S4 | Factor output reflects the updated lookback |
| R1-UC3-E1 | 1a. silver_cross_metal section absent: defaults (sgr: 60, scr: 20) |
| R1-UC3-E2 | 1b. Lookback value is non-positive or non-integer: uses default |

## Requirement Traceability Matrix

| ID | Requirement | Type | Test Type | Test Case | Status |
|----|-------------|------|-----------|-----------|--------|
| R1-UC1 | Compute silver factors Full Flow | Flow | Integration | `tests/factors/test_silver_factors.py::TestSilverScoringIntegration::test_silver_factors_in_scoring_model` | ✅ |
| R1-UC1-S1 | Factor registry discovers silver factors | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverFactorRegistration::test_silver_gold_ratio_registered` | ✅ |
| R1-UC1-S1 | Factor registry discovers silver factors | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverFactorRegistration::test_silver_copper_ratio_registered` | ✅ |
| R1-UC1-S2 | Engine calls SilverGoldRatioFactor.compute() | Step | Component | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_correct_ratio_deviation` | ✅ |
| R1-UC1-S3 | Factor reads sgr_lookback from config | Step | Component | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_sgr_custom_lookback_90` | ✅ |
| R1-UC1-S4 | Factor fetches ag and au futures data | Step | Component | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_correct_ratio_deviation` | ✅ |
| R1-UC1-S5 | Factor computes Ag/Au ratio deviation | Step | Component | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_correct_ratio_deviation` | ✅ |
| R1-UC1-S5 | Factor computes Ag/Au ratio deviation (zero edge) | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_zero_price_no_exception` | ✅ |
| R1-UC1-S6 | Returns deviation for silver, NaN for others | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_nan_for_non_silver_stocks` | ✅ |
| R1-UC1-S7 | SilverCopperRatioFactor analogous computation | Step | Component | `tests/factors/test_silver_factors.py::TestSilverCopperRatioFactor::test_correct_rate_of_change` | ✅ |
| R1-UC1-S7 | SilverCopperRatioFactor NaN for non-silver | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverCopperRatioFactor::test_nan_for_non_silver_stocks` | ✅ |
| R1-UC1-S7 | SilverCopperRatioFactor zero edge case | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverCopperRatioFactor::test_zero_price_no_exception` | ✅ |
| R1-UC1-S8 | Silver factors merged into scoring matrix | Step | Integration | `tests/factors/test_silver_factors.py::TestSilverScoringIntegration::test_silver_factors_in_scoring_model` | ✅ |
| R1-UC1-E1 | Insufficient futures data → NaN + warning (SGR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_nan_with_insufficient_data` | ✅ |
| R1-UC1-E1 | Insufficient futures data → NaN + warning (SCR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverCopperRatioFactor::test_nan_with_insufficient_data` | ✅ |
| R1-UC1-E2 | One metal has data, other does not (SGR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestOneMetalMissing::test_sgr_only_ag_data_no_au` | ✅ |
| R1-UC1-E2 | One metal has data, other does not (SCR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestOneMetalMissing::test_scr_only_ag_data_no_cu` | ✅ |
| R1-UC1-E3 | Non-silver subsector → NaN (SGR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverGoldRatioFactor::test_nan_for_non_silver_stocks` | ✅ |
| R1-UC1-E3 | Non-silver subsector → NaN (SCR) | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverCopperRatioFactor::test_nan_for_non_silver_stocks` | ✅ |
| R1-UC2 | Classify silver stocks Full Flow | Flow | Component | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification` (all 6 tests) | ✅ |
| R1-UC2-S1 | Classifier scans keywords | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_classify_bayin_keyword` | ✅ |
| R1-UC2-S2 | Text matches silver keyword (白银) | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_classify_bayin_keyword` | ✅ |
| R1-UC2-S2 | Text matches silver keyword (English) | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_classify_english_keyword` | ✅ |
| R1-UC2-S2 | Text matches silver keyword (银矿) | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_classify_yinkuang_keyword` | ✅ |
| R1-UC2-S3 | Classifier returns "silver" | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_classify_bayin_keyword` | ✅ |
| R1-UC2-S4 | SUBSECTOR_METAL_MAP["silver"] == "ag" | Step | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_metal_map_silver` | ✅ |
| R1-UC2-E1 | Both silver and gold keywords | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_dual_silver_gold_keywords_returns_first_match` | ✅ |
| R1-UC2-E2 | No silver keyword → other | Extension | Unit | `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification::test_no_silver_keyword_returns_other` | ✅ |
| R1-UC3 | Configure lookback windows Full Flow | Flow | Component | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_sgr_custom_lookback_90` | ✅ |
| R1-UC3-S1 | Set sgr_lookback to 90 | Step | Component | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_sgr_custom_lookback_90` | ✅ |
| R1-UC3-S3 | Factor uses 90-day rolling mean window | Step | Component | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_sgr_custom_lookback_90` | ✅ |
| R1-UC3-S4 | Output reflects updated lookback | Step | Component | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_sgr_custom_lookback_90` | ✅ |
| R1-UC3-E1 | Config section missing → defaults | Extension | Unit | `tests/factors/test_silver_factors.py::TestCustomLookbackConfig::test_config_section_missing_uses_defaults` | ✅ |
| R1-UC3-E2 | Non-positive lookback → default | Extension | Unit | | ⚠️ |

## Use Case Details

### Use Case: Compute silver cross-metal ratio factors during scoring (R1-UC1)

### Main Scenario
- **R1-UC1-S1**: Factor engine discovers silver factors via registry
  - `tests/factors/test_silver_factors.py:88` test_silver_gold_ratio_registered (Unit)
  - `tests/factors/test_silver_factors.py:94` test_silver_copper_ratio_registered (Unit)
- **R1-UC1-S2**: Engine calls SilverGoldRatioFactor.compute()
  - `tests/factors/test_silver_factors.py:108` test_correct_ratio_deviation (Component)
- **R1-UC1-S3**: Factor reads sgr_lookback from config
  - `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)
- **R1-UC1-S4**: Factor fetches ag and au futures data
  - `tests/factors/test_silver_factors.py:108` test_correct_ratio_deviation (Component)
- **R1-UC1-S5**: Factor computes Ag/Au ratio deviation
  - `tests/factors/test_silver_factors.py:108` test_correct_ratio_deviation (Component)
  - `tests/factors/test_silver_factors.py:149` test_zero_price_no_exception (Unit)
- **R1-UC1-S6**: Returns deviation for silver, NaN for others
  - `tests/factors/test_silver_factors.py:126` test_nan_for_non_silver_stocks (Unit)
- **R1-UC1-S7**: SilverCopperRatioFactor analogous
  - `tests/factors/test_silver_factors.py:170` test_correct_rate_of_change (Component)
  - `tests/factors/test_silver_factors.py:187` test_nan_for_non_silver_stocks (Unit)
  - `tests/factors/test_silver_factors.py:210` test_zero_price_no_exception (Unit)
- **R1-UC1-S8**: Merges into scoring matrix
  - `tests/factors/test_silver_factors.py:272` test_silver_factors_in_scoring_model (Integration)

### Extensions
- **R1-UC1-E1**: Insufficient data → NaN + warning
  - `tests/factors/test_silver_factors.py:138` test_nan_with_insufficient_data (Unit, SGR)
  - `tests/factors/test_silver_factors.py:199` test_nan_with_insufficient_data (Unit, SCR)
- **R1-UC1-E2**: One metal missing → NaN
  - `tests/factors/test_silver_factors.py:226` test_sgr_only_ag_data_no_au (Unit)
  - `tests/factors/test_silver_factors.py:234` test_scr_only_ag_data_no_cu (Unit)
- **R1-UC1-E3**: Non-silver subsector → NaN
  - `tests/factors/test_silver_factors.py:126` test_nan_for_non_silver_stocks (Unit, SGR)
  - `tests/factors/test_silver_factors.py:187` test_nan_for_non_silver_stocks (Unit, SCR)

### Full Flow Tests
- `R1-UC1` — "Compute silver factors" → `tests/factors/test_silver_factors.py:272` test_silver_factors_in_scoring_model (Integration)

---

### Use Case: Classify silver stocks into the silver subsector (R1-UC2)

### Main Scenario
- **R1-UC2-S1**: Classifier scans keywords
  - `tests/factors/test_silver_factors.py:68` test_classify_bayin_keyword (Unit)
- **R1-UC2-S2**: Text matches silver keyword
  - `tests/factors/test_silver_factors.py:68` test_classify_bayin_keyword (Unit)
  - `tests/factors/test_silver_factors.py:72` test_classify_english_keyword (Unit)
  - `tests/factors/test_silver_factors.py:76` test_classify_yinkuang_keyword (Unit)
- **R1-UC2-S3**: Returns "silver"
  - `tests/factors/test_silver_factors.py:68` test_classify_bayin_keyword (Unit)
- **R1-UC2-S4**: SUBSECTOR_METAL_MAP["silver"] == "ag"
  - `tests/factors/test_silver_factors.py:80` test_metal_map_silver (Unit)

### Extensions
- **R1-UC2-E1**: Both silver and gold keywords
  - `tests/factors/test_silver_factors.py:87` test_dual_silver_gold_keywords_returns_first_match (Unit)
- **R1-UC2-E2**: No silver keyword → other
  - `tests/factors/test_silver_factors.py:83` test_no_silver_keyword_returns_other (Unit)

### Full Flow Tests
- `R1-UC2` — "Classify silver stocks" → `tests/factors/test_silver_factors.py::TestSilverSubsectorClassification` (6 unit tests cover full flow)

---

### Use Case: Configure silver factor lookback windows (R1-UC3)

### Main Scenario
- **R1-UC3-S1**: Set sgr_lookback to 90
  - `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)
- **R1-UC3-S2**: Engine passes config to compute()
  - `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)
- **R1-UC3-S3**: Factor uses 90-day window
  - `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)
- **R1-UC3-S4**: Output reflects updated lookback
  - `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)

### Extensions
- **R1-UC3-E1**: Config section missing → defaults
  - `tests/factors/test_silver_factors.py:260` test_config_section_missing_uses_defaults (Unit)
- **R1-UC3-E2**: Non-positive lookback → default → ⚠️ not tested (implementation does not validate; passes raw value to numpy slicing)

### Full Flow Tests
- `R1-UC3` — "Configure lookback windows" → `tests/factors/test_silver_factors.py:239` test_sgr_custom_lookback_90 (Component)
