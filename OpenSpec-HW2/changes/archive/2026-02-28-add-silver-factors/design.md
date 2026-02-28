## Context

The quant system already has two gold cross-metal ratio factors (`GoldSilverRatioFactor`, `GoldCopperRatioFactor`) in `src/factors/commodity.py` that apply exclusively to gold-subsector stocks. The data pipeline already ingests silver ("ag") futures alongside gold ("au") and copper ("cu"). The classifier in `src/universe/classifier.py` does not yet have a "silver" subsector — silver-related stocks currently fall into "other".

The change adds two analogous silver factors and the subsector plumbing to support them.

## Goals / Non-Goals

**Goals:**
- Add "silver" subsector classification so silver stocks are identified and mapped to "ag"
- Add `SilverGoldRatioFactor` and `SilverCopperRatioFactor` mirroring the gold factor patterns
- Make lookback windows independently configurable via `settings.yaml`
- Full test coverage for the new factors

**Non-Goals:**
- Refactoring existing gold factors (they remain unchanged)
- Adding silver-specific inventory or momentum factors (future work)
- Changing factor category weights — silver factors inherit the existing `commodity: 0.30` weight
- Adding new data sources — "ag", "au", "cu" futures are already ingested

## Decisions

### D1: Place silver factors in existing `commodity.py`

**Choice:** Add both silver factor classes to `src/factors/commodity.py` alongside the gold factors.

**Alternative considered:** Create a separate `src/factors/silver.py` file. Rejected because the gold factors live in `commodity.py`, the module docstring already covers cross-metal ratios, and splitting would fragment related code. If the file grows too large in future, all commodity factors can be refactored together.

### D2: Mirror the gold factor implementation pattern exactly

**Choice:** `SilverGoldRatioFactor` uses the same deviation-from-rolling-mean formula as `GoldSilverRatioFactor`; `SilverCopperRatioFactor` uses the same rate-of-change formula as `GoldCopperRatioFactor`. The only differences are: ratio direction (Ag/Au instead of Au/Ag, Ag/Cu instead of Au/Cu), subsector filter (`"ag"` instead of `"au"`), and config key namespace (`silver_cross_metal` instead of `gold_cross_metal`).

**Rationale:** Consistency reduces cognitive load. The formulas are proven correct in the gold implementation, and a symmetric pair (gold factors for gold stocks, silver factors for silver stocks) makes the system easy to reason about.

### D3: Use `_get_stock_metal()` for subsector filtering

**Choice:** Reuse the existing `_get_stock_metal(symbol, config, store)` helper that reads `universe_cache` and looks up `SUBSECTOR_METAL_MAP`. Silver factors check `metal == "ag"` just as gold factors check `metal == "au"`.

**Alternative considered:** Add a dedicated `_is_silver_stock()` helper. Rejected because `_get_stock_metal` already handles the lookup and is used by all other commodity factors.

### D4: Separate config namespace `silver_cross_metal`

**Choice:** Add `factors.silver_cross_metal.sgr_lookback` and `factors.silver_cross_metal.scr_lookback` in `settings.yaml`, independent from `gold_cross_metal`.

**Rationale:** Silver and gold may have different optimal lookback windows. Naming mirrors the gold pattern (`gold_cross_metal` → `silver_cross_metal`). Defaults match gold's (sgr: 60, scr: 20) so the system works without config changes.

### D5: Test file structure

**Choice:** Create `tests/factors/test_silver_factors.py` as a new file, following the same fixture and helper patterns used in `tests/factors/test_gold_factors.py`.

**Alternative considered:** Add silver tests into `test_gold_factors.py`. Rejected because the file would become too long and the factors are logically separate.

## Risks / Trade-offs

**[Risk] Silver keyword overlap with other subsectors** → The keyword "银" alone could match unrelated stocks (e.g., "银行" = bank). Mitigation: use specific keywords "白银", "silver", "银矿" that are unambiguous for silver mining/refining companies. This matches the existing pattern where gold uses "黄金", "gold", "金矿" rather than just "金".

**[Risk] Iteration order determines classification when keywords overlap** → If a stock name contains both gold and silver keywords, `classify_subsector` returns whichever matches first in dict iteration order. Mitigation: This is an existing design constraint that applies equally to gold. In practice, A-share companies focus on one primary metal, so overlap is rare.

**[Risk] No silver-subsector stocks in the current universe** → If no listed company matches the silver keywords, the factors will produce all-NaN columns, adding computation cost with no signal. Mitigation: The cost is negligible (two extra ratio calculations per rebalance). The factors are ready when silver stocks enter the universe.
