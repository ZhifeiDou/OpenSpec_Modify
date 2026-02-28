## Use Cases

### Use Case: Compute gold cross-metal ratio factors for stock scoring

**Primary Actor:** Quant Engine (automated factor computation pipeline)
**Scope:** Multi-factor scoring system
**Level:** User goal

**Stakeholders and Interests:**
- Quant Researcher — wants gold-specific cross-metal signals (gold-silver ratio, gold-copper ratio) included in factor scoring to improve gold-subsector stock selection
- System Operator — wants the new factors to integrate seamlessly with existing commodity factor pipeline without manual intervention

**Preconditions:**
- Gold (au), silver (ag), and copper (cu) futures daily data are available in the `futures_daily` table
- Stock universe has been classified with subsector labels (including "gold" subsector)

**Success Guarantee (Postconditions):**
- `GoldSilverRatioFactor` produces a numeric score for every stock in the universe
- `GoldCopperRatioFactor` produces a numeric score for every stock in the universe
- Gold-subsector stocks receive factor values derived from Au/Ag and Au/Cu ratios
- Non-gold stocks receive `NaN` for these factors (factors are gold-specific)
- Factor values are standardized and fed into the multi-factor scorer alongside existing commodity factors

**Trigger:** The scoring pipeline invokes `compute()` on all registered factors for a given date.

**Main Success Scenario:**
1. Scoring pipeline iterates over registered factors and reaches `GoldSilverRatioFactor`.
2. Factor reads gold (au) and silver (ag) futures close prices for the trailing window from the data store.
3. Factor computes the Au/Ag price ratio and its deviation from the rolling mean.
4. Factor assigns the deviation score to each gold-subsector stock; non-gold stocks receive `NaN`.
5. Scoring pipeline proceeds to `GoldCopperRatioFactor`.
6. Factor reads gold (au) and copper (cu) futures close prices and computes the Au/Cu ratio rate-of-change.
7. Factor assigns the rate-of-change score to each gold-subsector stock.
8. Both factor outputs are combined with existing commodity factors in the weighted scoring model.

**Extensions:**
- 2a. Silver futures data is missing or has fewer rows than required lookback: Factor returns `NaN` for all stocks and logs a warning.
- 6a. Copper futures data is missing or insufficient: Factor returns `NaN` for all stocks and logs a warning.
- 4a. No stocks are classified under the gold subsector: Factor returns an empty series; scoring proceeds without error.

**Open Questions:**
- Should gold cross-metal factors also apply to stocks in closely related subsectors (e.g., silver miners)?

---

### Use Case: Fetch and store silver futures data

**Primary Actor:** Data Pipeline (automated data update)
**Scope:** Data ingestion subsystem
**Level:** Subfunction

**Stakeholders and Interests:**
- Factor Engine — requires silver (ag) futures daily OHLCV to compute gold-silver ratio
- Data Pipeline — needs a consistent fetch-and-store pattern matching existing metals

**Preconditions:**
- AKShare API is accessible
- Silver continuous contract symbol `ag0` is available on Sina futures

**Success Guarantee (Postconditions):**
- Silver futures daily data is stored in `futures_daily` table with `metal = 'ag'`
- Data format matches existing metals (date, open, high, low, close, volume)

**Trigger:** `pipeline.update(categories=["futures"])` is invoked (manually or scheduled).

**Main Success Scenario:**
1. Data pipeline iterates over the `_metals` list, which now includes `"ag"`.
2. Pipeline calls `fetch_futures_daily("ag", start_date, end_date)`.
3. AKShare returns silver continuous contract (ag0) daily data.
4. Pipeline stores the data in `futures_daily` table.

**Extensions:**
- 3a. AKShare returns empty data for ag0: Pipeline logs a warning and continues with other metals.
- 3b. API call fails after retries: Pipeline logs an error and continues; factor will use `NaN` values.

---

### Use Case: Fix gold and silver inventory data mapping

**Primary Actor:** Data Pipeline (automated data update)
**Scope:** Data ingestion subsystem
**Level:** Subfunction

**Stakeholders and Interests:**
- Inventory Factor — needs correct Chinese name mapping to fetch gold/silver exchange inventory via AKShare
- Data Integrity — existing metals should not be affected by the mapping fix

**Preconditions:**
- AKShare `futures_inventory_em` API accepts Chinese metal names

**Success Guarantee (Postconditions):**
- `fetch_inventory("au")` uses `"黄金"` as the lookup name and returns gold inventory data
- `fetch_inventory("ag")` uses `"白银"` as the lookup name and returns silver inventory data
- Existing metal mappings (cu→铜, al→铝, etc.) remain unchanged

**Trigger:** `pipeline.update(categories=["futures"])` triggers inventory fetch for each metal.

**Main Success Scenario:**
1. Pipeline calls `fetch_inventory("au")`.
2. `metal_names` dict resolves `"au"` to `"黄金"`.
3. AKShare returns gold inventory data.
4. Pipeline stores inventory data with `metal = 'au'`.
5. Same flow repeats for `"ag"` → `"白银"`.

**Extensions:**
- 3a. AKShare does not have gold inventory data: Function returns empty DataFrame; inventory factor uses `NaN`.
- 5a. AKShare does not have silver inventory data: Same handling as 3a.
