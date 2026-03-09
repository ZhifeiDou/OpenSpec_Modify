## 1. Data Pipeline Changes

- [x] 1.1 Add `"ag"` to `DataPipeline._metals` list in `src/data/pipeline.py`
- [x] 1.2 Add `"au": "黄金"` and `"ag": "白银"` to `metal_names` dict in `AKShareSource.fetch_inventory` in `src/data/sources/akshare_source.py`

## 2. Configuration

- [x] 2.1 Add `gold_cross_metal` section to `config/settings.yaml` with `gsr_lookback: 60` and `gcr_lookback: 20`

## 3. Factor Implementation

- [x] 3.1 Implement `GoldSilverRatioFactor` class in `src/factors/commodity.py` with `@register_factor`, name `gold_silver_ratio`, category `commodity`, reading au/ag futures data and computing deviation from rolling mean
- [x] 3.2 Implement `GoldCopperRatioFactor` class in `src/factors/commodity.py` with `@register_factor`, name `gold_copper_ratio`, category `commodity`, reading au/cu futures data and computing rate-of-change
- [x] 3.3 Both factors return NaN for non-gold subsector stocks via `_get_stock_metal` check

## 4. Tests

- [x] 4.1 Add unit test for `GoldSilverRatioFactor`: verify correct ratio deviation calculation with mock futures data
- [x] 4.2 Add unit test for `GoldCopperRatioFactor`: verify correct rate-of-change calculation with mock futures data
- [x] 4.3 Add test verifying both factors return NaN for non-gold subsector stocks
- [x] 4.4 Add test verifying both factors return NaN when insufficient futures data is available
- [x] 4.5 Add test verifying `fetch_inventory` correctly maps `"au"` → `"黄金"` and `"ag"` → `"白银"`
