## ADDED Requirements

### Requirement: Gold-silver ratio factor
The system SHALL compute a gold-silver ratio factor (`gold_silver_ratio`) that measures the deviation of the current Au/Ag price ratio from its rolling mean. The factor SHALL read daily close prices for gold (au) and silver (ag) futures from the data store. The lookback window for the rolling mean SHALL default to 60 trading days and be configurable via `config.factors.gold_cross_metal.gsr_lookback`. The factor SHALL only produce values for stocks classified under the "gold" subsector; all other stocks SHALL receive NaN. A higher-than-average gold-silver ratio is bullish for gold stocks.

#### Scenario: Compute gold-silver ratio deviation
- **WHEN** the system computes `gold_silver_ratio` on date T with 60-day lookback, and gold close is 2300, silver close is 27, and the 60-day average Au/Ag ratio is 80
- **THEN** the factor value for gold-subsector stocks is (2300/27 - 80) / 80 = 0.0648

#### Scenario: Apply factor only to gold-subsector stocks
- **WHEN** the universe contains stocks from copper, aluminum, and gold subsectors
- **THEN** only gold-subsector stocks receive a numeric `gold_silver_ratio` value; copper and aluminum stocks receive NaN

#### Scenario: Insufficient silver futures data
- **WHEN** fewer than 61 trading days of silver (ag) futures data are available
- **THEN** the factor returns NaN for all stocks and logs a warning

#### Scenario: Configurable lookback window
- **WHEN** `config.factors.gold_cross_metal.gsr_lookback` is set to 120
- **THEN** the rolling mean is computed over the most recent 120 trading days instead of the default 60

### Requirement: Gold-copper ratio factor
The system SHALL compute a gold-copper ratio factor (`gold_copper_ratio`) that measures the rate-of-change of the Au/Cu price ratio over a trailing window. The factor SHALL read daily close prices for gold (au) and copper (cu) futures from the data store. The lookback window SHALL default to 20 trading days and be configurable via `config.factors.gold_cross_metal.gcr_lookback`. The factor SHALL only produce values for stocks classified under the "gold" subsector; all other stocks SHALL receive NaN. A rising gold-copper ratio indicates risk-off sentiment and is bullish for gold stocks.

#### Scenario: Compute gold-copper ratio rate-of-change
- **WHEN** the system computes `gold_copper_ratio` on date T with 20-day lookback, and the Au/Cu ratio today is 33.5 and 20 days ago was 32.0
- **THEN** the factor value for gold-subsector stocks is (33.5 - 32.0) / 32.0 = 0.0469

#### Scenario: Apply factor only to gold-subsector stocks
- **WHEN** the universe contains stocks from multiple subsectors
- **THEN** only gold-subsector stocks receive a numeric `gold_copper_ratio` value; all others receive NaN

#### Scenario: Insufficient copper or gold futures data
- **WHEN** fewer than 21 trading days of gold or copper futures data are available
- **THEN** the factor returns NaN for all stocks and logs a warning

### Requirement: Factor registration and category
Both `GoldSilverRatioFactor` and `GoldCopperRatioFactor` SHALL be registered via the `@register_factor` decorator. Both factors SHALL belong to the `"commodity"` category so they are weighted under the existing commodity factor weight in the scoring model.

#### Scenario: Factors appear in registered factor list
- **WHEN** the factor engine loads all registered factors
- **THEN** `gold_silver_ratio` and `gold_copper_ratio` appear in the factor registry under category `"commodity"`

#### Scenario: Factors contribute to commodity category score
- **WHEN** the multi-factor scorer computes the commodity category score
- **THEN** `gold_silver_ratio` and `gold_copper_ratio` are included alongside existing commodity factors (metal_price_mom_60d, futures_basis, inventory_weekly_change)
