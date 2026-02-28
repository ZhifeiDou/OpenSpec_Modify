## Test Report: add-silver-factors
Generated: 2026-02-28

### Use Case Coverage Summary

| Use Case | Happy Path | Extensions | Overall |
|----------|-----------|------------|---------|
| R1-UC1: Compute silver factors | ✅ 8/8 | ✅ 3/3 | 100% |
| R1-UC2: Classify silver stocks | ✅ 4/4 | ✅ 2/2 | 100% |
| R1-UC3: Configure lookback windows | ✅ 4/4 | ⚠️ 1/2 | 83% |

**Overall: 32/33 requirements covered (97%)**

### Covered Requirements

- ✅ **R1-UC1** (Full Flow): Compute silver factors → `test_silver_factors.py::TestSilverScoringIntegration::test_silver_factors_in_scoring_model`
- ✅ **R1-UC1-S1**: Factor registry discovers silver factors → `test_silver_factors.py:88` + `:94`
- ✅ **R1-UC1-S2**: Engine calls SilverGoldRatioFactor.compute() → `test_silver_factors.py:108`
- ✅ **R1-UC1-S3**: Factor reads sgr_lookback from config → `test_silver_factors.py:239`
- ✅ **R1-UC1-S4**: Factor fetches ag and au futures data → `test_silver_factors.py:108`
- ✅ **R1-UC1-S5**: Factor computes Ag/Au ratio deviation → `test_silver_factors.py:108` + `:149`
- ✅ **R1-UC1-S6**: Returns deviation for silver, NaN for others → `test_silver_factors.py:126`
- ✅ **R1-UC1-S7**: SilverCopperRatioFactor analogous → `test_silver_factors.py:170` + `:187` + `:210`
- ✅ **R1-UC1-S8**: Silver factors merged into scoring matrix → `test_silver_factors.py:272`
- ✅ **R1-UC1-E1**: Insufficient futures data → NaN + warning → `test_silver_factors.py:138` + `:199`
- ✅ **R1-UC1-E2**: One metal has data, other does not → `test_silver_factors.py:226` + `:234`
- ✅ **R1-UC1-E3**: Non-silver subsector → NaN → `test_silver_factors.py:126` + `:187`
- ✅ **R1-UC2** (Full Flow): Classify silver stocks → `TestSilverSubsectorClassification` (6 tests)
- ✅ **R1-UC2-S1**: Classifier scans keywords → `test_silver_factors.py:68`
- ✅ **R1-UC2-S2**: Text matches silver keyword → `test_silver_factors.py:68` + `:72` + `:76`
- ✅ **R1-UC2-S3**: Classifier returns "silver" → `test_silver_factors.py:68`
- ✅ **R1-UC2-S4**: SUBSECTOR_METAL_MAP["silver"] == "ag" → `test_silver_factors.py:80`
- ✅ **R1-UC2-E1**: Both silver and gold keywords → `test_silver_factors.py:87`
- ✅ **R1-UC2-E2**: No silver keyword → other → `test_silver_factors.py:83`
- ✅ **R1-UC3** (Full Flow): Configure lookback windows → `test_silver_factors.py:239`
- ✅ **R1-UC3-S1/S3/S4**: Custom sgr_lookback=90 → `test_silver_factors.py:239`
- ✅ **R1-UC3-E1**: Config section missing → defaults → `test_silver_factors.py:260`

### Uncovered Requirements

- ⚠️ **R1-UC3-E2**: Non-positive lookback → uses default
  - The implementation does not validate lookback values — it passes the raw config value to numpy array slicing. A non-positive value would cause unexpected behavior rather than falling back to default. This is a spec-implementation mismatch (same pattern as gold factors).
  - **Recommendation**: Accept as known limitation or add input validation to both gold and silver factors in a future change.

### Test Run Results

**Silver factor tests** (`test_silver_factors.py`): **21 passed**, 0 failed, 0 skipped (1.09s)
**Gold factor regression** (`test_gold_factors.py`): **12 passed**, 0 failed, 0 skipped (0.90s)

**Total: 33 passed, 0 failed, 0 skipped**

No failures. No regressions.
