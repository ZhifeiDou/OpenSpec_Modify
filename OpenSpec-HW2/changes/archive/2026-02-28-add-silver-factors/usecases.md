## Use Cases

### Use Case: Compute silver cross-metal ratio factors during scoring

**Primary Actor:** Factor scoring engine
**Scope:** Quant factor pipeline (`src/factors/`)
**Level:** User goal

**Stakeholders and Interests:**
- Portfolio manager — wants silver-subsector stocks scored with silver-specific commodity signals, not generic defaults
- Factor engine — needs each registered factor to return a `pd.Series` indexed by symbol

**Preconditions:**
- Silver futures ("ag"), gold futures ("au"), and copper futures ("cu") daily price data are present in the data store with sufficient history
- The stock universe has been classified and silver-subsector stocks are tagged with subsector `"silver"`

**Success Guarantee (Postconditions):**
- `SilverGoldRatioFactor` returns a finite numeric value for every silver-subsector stock and `NaN` for all non-silver stocks
- `SilverCopperRatioFactor` returns a finite numeric value for every silver-subsector stock and `NaN` for all non-silver stocks
- Factor values are included in the composite scoring matrix alongside existing factors

**Trigger:** The factor engine calls `compute_all_factors()` for a given date and universe.

**Main Success Scenario:**
1. Factor engine discovers `SilverGoldRatioFactor` and `SilverCopperRatioFactor` via the `@register_factor` registry.
2. For `SilverGoldRatioFactor`, the engine calls `compute(universe, date, store, config)`.
3. Factor reads `silver_cross_metal.sgr_lookback` from config (default 60).
4. Factor fetches "ag" and "au" futures close prices from the data store up to the given date.
5. Factor computes the Ag/Au ratio series, calculates the rolling mean over the lookback window, and derives the deviation: `(current_ratio - rolling_mean) / rolling_mean`.
6. Factor returns the deviation value for silver-subsector stocks and `NaN` for all others.
7. Steps 2–6 repeat analogously for `SilverCopperRatioFactor` using "ag" and "cu" prices with `scr_lookback` (default 20) and rate-of-change formula.
8. Factor engine merges both silver factor columns into the scoring matrix.

**Extensions:**
- 4a. Insufficient futures data (fewer rows than lookback + 1): Factor logs a warning and returns `NaN` for all stocks.
- 4b. One metal has data but the other does not: Factor returns `NaN` for all stocks (cannot compute ratio with missing side).
- 6a. Stock's subsector is not in `SUBSECTOR_METAL_MAP` or maps to a metal other than "ag": Factor returns `NaN` for that stock.

---

### Use Case: Classify silver stocks into the silver subsector

**Primary Actor:** Universe classifier
**Scope:** Stock universe classification (`src/universe/classifier.py`)
**Level:** Subfunction

**Stakeholders and Interests:**
- Factor engine — needs to know which stocks are silver-related so silver factors apply only to them
- Data pipeline — needs consistent subsector labels in `universe_cache`

**Preconditions:**
- Raw stock list with name and industry columns is available from AKShare

**Success Guarantee (Postconditions):**
- Stocks whose name or industry contains silver keywords ("白银", "silver", "银矿") are classified as subsector `"silver"`
- `SUBSECTOR_METAL_MAP["silver"]` resolves to `"ag"`

**Trigger:** `classify_subsector(name, industry_name)` is called for a stock during universe refresh.

**Main Success Scenario:**
1. Classifier scans the stock's name and industry text against `_SUBSECTOR_KEYWORDS`.
2. Text matches a silver keyword (e.g., "白银" in the company name).
3. Classifier returns `"silver"` as the subsector.
4. Downstream code looks up `SUBSECTOR_METAL_MAP["silver"]` and gets `"ag"`.

**Extensions:**
- 2a. Stock name contains both silver and gold keywords: Classifier returns whichever subsector matches first in iteration order.
- 2b. No silver keyword matches: Stock is classified under another subsector or `"other"`.

---

### Use Case: Configure silver factor lookback windows

**Primary Actor:** Quant researcher
**Scope:** Configuration (`config/settings.yaml`)
**Level:** Subfunction

**Stakeholders and Interests:**
- Quant researcher — wants to tune silver factor sensitivity independently from gold factors
- Factor engine — reads lookback values at compute time

**Preconditions:**
- `settings.yaml` contains a `factors.silver_cross_metal` section

**Success Guarantee (Postconditions):**
- `SilverGoldRatioFactor` uses `sgr_lookback` from config (or defaults to 60 if missing)
- `SilverCopperRatioFactor` uses `scr_lookback` from config (or defaults to 20 if missing)

**Trigger:** Researcher edits `settings.yaml` and runs the factor pipeline.

**Main Success Scenario:**
1. Researcher sets `factors.silver_cross_metal.sgr_lookback` to 90 in `settings.yaml`.
2. Factor engine loads config and passes it to `SilverGoldRatioFactor.compute()`.
3. Factor reads lookback = 90 from config and uses 90-day rolling mean window.
4. Factor output reflects the updated lookback.

**Extensions:**
- 1a. `silver_cross_metal` section is absent from config: Factors fall back to hardcoded defaults (sgr: 60, scr: 20).
- 1b. Lookback value is non-positive or non-integer: Factor uses the default value.
