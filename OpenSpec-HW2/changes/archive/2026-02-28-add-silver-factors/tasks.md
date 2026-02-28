## 1. Silver Subsector Classification

- [x] 1.1 Add `"silver": ["白银", "silver", "银矿"]` to `_SUBSECTOR_KEYWORDS` in `src/universe/classifier.py`
- [x] 1.2 Add `"silver": "ag"` to `SUBSECTOR_METAL_MAP` in `src/universe/classifier.py`

## 2. Silver Factor Implementation

- [x] 2.1 Add `SilverGoldRatioFactor` class to `src/factors/commodity.py` — registered with `@register_factor`, `name = "silver_gold_ratio"`, `category = "commodity"`, reads `silver_cross_metal.sgr_lookback` (default 60), computes `(current_ag_au - rolling_mean) / rolling_mean`, returns NaN for non-silver stocks
- [x] 2.2 Add `SilverCopperRatioFactor` class to `src/factors/commodity.py` — registered with `@register_factor`, `name = "silver_copper_ratio"`, `category = "commodity"`, reads `silver_cross_metal.scr_lookback` (default 20), computes `(ag_cu_today - ag_cu_past) / ag_cu_past`, returns NaN for non-silver stocks

## 3. Configuration

- [x] 3.1 Add `silver_cross_metal` section to `config/settings.yaml` with `sgr_lookback: 60` and `scr_lookback: 20`

## 4. Tests

- [x] 4.1 Create `tests/factors/test_silver_factors.py` with test fixtures mirroring `test_gold_factors.py` (seeded "ag", "au", "cu" futures data and universe cache with silver-subsector stock)
- [x] 4.2 Add test: `SilverGoldRatioFactor` returns correct deviation value for silver stock with sufficient data
- [x] 4.3 Add test: `SilverCopperRatioFactor` returns correct rate-of-change value for silver stock with sufficient data
- [x] 4.4 Add test: both factors return NaN for non-silver-subsector stocks
- [x] 4.5 Add test: both factors return NaN and log warning when insufficient futures data
- [x] 4.6 Add test: both factors handle zero prices / zero rolling mean without raising exceptions
- [x] 4.7 Add test: classifier returns `"silver"` for stock names containing silver keywords
- [x] 4.8 Add test: `SUBSECTOR_METAL_MAP["silver"]` equals `"ag"`

## 5. Verification

- [x] 5.1 Run full test suite and confirm all existing tests still pass (no regressions)
- [x] 5.2 Verify both silver factors appear in `compute_all_factors()` output columns
