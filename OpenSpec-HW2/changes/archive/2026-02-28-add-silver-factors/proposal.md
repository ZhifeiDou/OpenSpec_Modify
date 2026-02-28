## Why

The quant system currently has gold cross-metal ratio factors (GSR, GCR) that only apply to gold-subsector stocks. Silver (白银) stocks exist in the A-share non-ferrous metals universe but have no dedicated cross-metal ratio factors. Silver futures data ("ag") is already ingested by the data pipeline, so adding silver-specific factors is a natural extension that improves signal coverage for silver-related holdings.

## What Changes

- Add a "silver" subsector to the stock classifier (`_SUBSECTOR_KEYWORDS` and `SUBSECTOR_METAL_MAP`) so silver stocks are identified and mapped to the "ag" futures symbol
- Add `SilverGoldRatioFactor` — deviation of Ag/Au ratio from its rolling mean (mirrors GSR logic, applied to silver-subsector stocks)
- Add `SilverCopperRatioFactor` — rate-of-change of Ag/Cu ratio (mirrors GCR logic, applied to silver-subsector stocks)
- Add `silver_cross_metal` configuration section in `settings.yaml` with independent lookback windows
- Add unit tests for the new silver factors following the existing gold factor test patterns

## Capabilities

### New Capabilities
- `silver-cross-metal-factors`: Silver cross-metal ratio factors (SilverGoldRatio and SilverCopperRatio) with subsector classification and configuration

### Modified Capabilities

_(none — no existing spec-level requirements change)_

## Impact

- **Code**: `src/universe/classifier.py` (new subsector), `src/factors/commodity.py` (new factor classes), `config/settings.yaml` (new config section)
- **Tests**: New test file `tests/factors/test_silver_factors.py`
- **Data**: No new data sources — "ag", "au", and "cu" futures are already fetched
- **APIs / Dependencies**: No external changes; factor registry auto-discovers new classes via `@register_factor`
