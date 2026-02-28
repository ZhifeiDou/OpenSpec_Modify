## ADDED Requirements

### Requirement: Silver subsector classification
The classifier SHALL recognise stocks as subsector `"silver"` when the stock name or industry text contains any of the keywords: "白银", "silver", "银矿". `SUBSECTOR_METAL_MAP` SHALL map `"silver"` to futures metal code `"ag"`.

#### Scenario: Stock name contains Chinese silver keyword
- **WHEN** `classify_subsector` is called with name containing "白银"
- **THEN** the function returns `"silver"`

#### Scenario: Stock name contains English silver keyword
- **WHEN** `classify_subsector` is called with name containing "silver"
- **THEN** the function returns `"silver"`

#### Scenario: Metal map lookup for silver subsector
- **WHEN** code looks up `SUBSECTOR_METAL_MAP["silver"]`
- **THEN** the result is `"ag"`

### Requirement: SilverGoldRatioFactor computation
The system SHALL provide a `SilverGoldRatioFactor` registered factor with `name = "silver_gold_ratio"` and `category = "commodity"`. It SHALL compute the deviation of the current Ag/Au price ratio from its rolling mean: `(current_ratio - rolling_mean) / rolling_mean`.

#### Scenario: Normal computation with sufficient data
- **WHEN** `compute()` is called with at least `sgr_lookback + 1` trading days of "ag" and "au" futures data
- **THEN** for each silver-subsector stock, the factor returns `(current_ag_au_ratio - mean_of_prior_ratios) / mean_of_prior_ratios`
- **AND** for each non-silver stock, the factor returns `NaN`

#### Scenario: Insufficient futures data
- **WHEN** `compute()` is called and either "ag" or "au" data has fewer than `sgr_lookback + 1` rows
- **THEN** the factor logs a warning and returns `NaN` for all stocks

#### Scenario: Division by zero in ratio
- **WHEN** a futures close price is zero or the rolling mean is zero
- **THEN** the factor returns `NaN` for all stocks (no exception raised)

### Requirement: SilverCopperRatioFactor computation
The system SHALL provide a `SilverCopperRatioFactor` registered factor with `name = "silver_copper_ratio"` and `category = "commodity"`. It SHALL compute the rate-of-change of the Ag/Cu price ratio: `(ratio_today - ratio_past) / ratio_past`, where `ratio_past` is the ratio `scr_lookback` trading days ago.

#### Scenario: Normal computation with sufficient data
- **WHEN** `compute()` is called with at least `scr_lookback + 1` trading days of "ag" and "cu" futures data
- **THEN** for each silver-subsector stock, the factor returns `(ag_cu_ratio_today - ag_cu_ratio_past) / ag_cu_ratio_past`
- **AND** for each non-silver stock, the factor returns `NaN`

#### Scenario: Insufficient futures data
- **WHEN** `compute()` is called and either "ag" or "cu" data has fewer than `scr_lookback + 1` rows
- **THEN** the factor logs a warning and returns `NaN` for all stocks

#### Scenario: Division by zero in ratio
- **WHEN** a futures close price is zero or the past ratio is zero
- **THEN** the factor returns `NaN` for all stocks (no exception raised)

### Requirement: Silver factor configuration
The system SHALL read lookback windows from `config["factors"]["silver_cross_metal"]`. Key `sgr_lookback` controls SilverGoldRatioFactor (default 60). Key `scr_lookback` controls SilverCopperRatioFactor (default 20).

#### Scenario: Custom lookback from config
- **WHEN** `settings.yaml` contains `factors.silver_cross_metal.sgr_lookback: 90`
- **THEN** `SilverGoldRatioFactor` uses a 90-day rolling window

#### Scenario: Config section missing
- **WHEN** `settings.yaml` has no `factors.silver_cross_metal` section
- **THEN** `SilverGoldRatioFactor` defaults to lookback 60 and `SilverCopperRatioFactor` defaults to lookback 20

### Requirement: Silver factors are auto-discovered
Both `SilverGoldRatioFactor` and `SilverCopperRatioFactor` SHALL use the `@register_factor` decorator so they are automatically included when `compute_all_factors()` runs.

#### Scenario: Factor registry includes silver factors
- **WHEN** `compute_all_factors()` is invoked
- **THEN** both `"silver_gold_ratio"` and `"silver_copper_ratio"` appear in the resulting factor matrix columns

### Requirement: Silver factors only apply to silver-subsector stocks
Both silver factors SHALL return `NaN` for any stock whose subsector does not map to metal code `"ag"`.

#### Scenario: Non-silver stock receives NaN
- **WHEN** a stock's subsector is `"copper"` (metal = "cu")
- **THEN** both `SilverGoldRatioFactor` and `SilverCopperRatioFactor` return `NaN` for that stock

#### Scenario: Silver stock receives computed value
- **WHEN** a stock's subsector is `"silver"` (metal = "ag") and sufficient data exists
- **THEN** both factors return a finite numeric value for that stock
