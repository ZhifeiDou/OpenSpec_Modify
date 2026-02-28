## Context

The system currently has three generic commodity factors (metal_price_mom_60d, futures_basis, inventory_weekly_change) applied uniformly to all metals via `SUBSECTOR_METAL_MAP`. Gold (au) and copper (cu) futures data are already fetched, but silver (ag) is missing from the pipeline. The `fetch_inventory` mapping also lacks entries for gold and silver. The factor engine uses a decorator-based registry (`@register_factor`) and equal-weight scoring within categories, so new factors are auto-discovered with no scorer changes needed.

## Goals / Non-Goals

**Goals:**
- Add two gold-specific cross-metal factors: gold-silver ratio deviation and gold-copper ratio rate-of-change
- Add silver (ag) futures data to the data pipeline
- Fix inventory data mapping for gold (au) and silver (ag)
- Keep new factors configurable (lookback windows) via `settings.yaml`

**Non-Goals:**
- Changing the overall commodity category weight (stays at 0.30)
- Adding silver-subsector stock classification or silver-specific factors
- Modifying the cross-sectional standardization or scoring logic
- Adding COMEX or international gold data sources

## Decisions

### 1. Place new factors in `commodity.py` rather than a new file

**Decision**: Add `GoldSilverRatioFactor` and `GoldCopperRatioFactor` to the existing `src/factors/commodity.py`.

**Rationale**: Both factors share the same `_get_stock_metal` helper and `SUBSECTOR_METAL_MAP` dependency as the existing commodity factors. Creating a separate file would fragment related logic. The file remains manageable at ~170 lines after additions.

**Alternative considered**: Separate `src/factors/gold.py` — rejected because it would require duplicating or importing `_get_stock_metal` and adds unnecessary module complexity for just two classes.

### 2. Gold-only factor application via subsector filtering

**Decision**: New factors return NaN for all non-gold stocks by checking the stock's subsector from `universe_cache`.

**Rationale**: Gold-silver and gold-copper ratios are only meaningful signals for gold-mining stocks. Applying them to copper or aluminum stocks would add noise. The existing `_get_stock_metal` function already provides subsector lookup; the new factors add a simple `if metal != "au": return NaN` guard.

**Alternative considered**: Apply ratios to all stocks with the numerator being their respective metal — rejected because the Au/Ag ratio has no informational value for zinc stocks.

### 3. Ratio computation approach

**Decision**:
- **Gold-silver ratio factor**: Compute `(current_ratio - rolling_mean) / rolling_mean` where `current_ratio = au_close / ag_close` and rolling mean is over `gsr_lookback` days (default 60).
- **Gold-copper ratio factor**: Compute simple rate-of-change `(ratio_today - ratio_N_days_ago) / ratio_N_days_ago` over `gcr_lookback` days (default 20).

**Rationale**: The gold-silver ratio is a mean-reverting indicator, so deviation from mean captures the signal. The gold-copper ratio is a trend indicator, so rate-of-change is more appropriate. These align with standard commodity trading practice.

### 4. Add silver to `_metals` list and fix inventory mapping

**Decision**: Add `"ag"` to `DataPipeline._metals` and add `"au": "黄金"` and `"ag": "白银"` to `AKShareSource.fetch_inventory.metal_names`.

**Rationale**: Silver futures data is required for the gold-silver ratio factor. The inventory mapping fix ensures `InventoryWeeklyChangeFactor` can also compute values for gold and silver stocks. Both are one-line additions to existing data structures.

### 5. Configuration structure

**Decision**: Add a `gold_cross_metal` section under `factors` in `settings.yaml`:
```yaml
factors:
  gold_cross_metal:
    gsr_lookback: 60   # Gold-silver ratio rolling mean window
    gcr_lookback: 20   # Gold-copper ratio rate-of-change window
```

**Rationale**: Groups gold-specific factor parameters together. Follows the existing pattern of `factors.momentum.lookback`.

## Risks / Trade-offs

- **[NaN sparsity]** Gold-subsector stocks are a small portion of the universe; new factors will be NaN for most stocks. → The standardizer and scorer already handle NaN gracefully (NaN values are excluded from cross-sectional ranking).

- **[Silver data availability]** AKShare silver futures (`ag0`) availability has not been verified. → Mitigation: factor returns NaN if data is missing, with a logged warning. No crash path.

- **[Score dilution]** Adding two new commodity factors dilutes the per-factor weight within the commodity category (from 0.30/3 = 0.10 each to 0.30/5 = 0.06 each). → Acceptable trade-off. The new factors only apply to gold stocks where they add signal; for non-gold stocks the NaN values cause these factors to be effectively excluded from scoring.
