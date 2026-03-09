## Purpose

Multi-factor calculation engine for the non-ferrous metals quant strategy. Computes 18+ factors across 6 categories (commodity, fundamental, technical, fund flow, macro, cross-metal ratio), applies cross-sectional standardization, and outputs a factor matrix.

## Requirements

### Requirement: Factor calculator trait
The system SHALL define a `FactorCalculator` trait with methods `name() -> &str` and `calculate(universe: &DataFrame, date: NaiveDate) -> Result<Series>`. All factor implementations MUST implement this trait.

#### Scenario: Trait contract
- **WHEN** a new factor calculator is registered
- **THEN** it implements `name()` returning a unique factor name and `calculate()` returning a Series with one value per stock

### Requirement: Commodity factors
The system SHALL compute the following commodity factors:
- `metal_momentum_60d`: 60-day price momentum of the primary metal linked to each stock's sub-sector
- `futures_basis`: Percentage difference between futures and spot prices for the relevant metal
- `inventory_change`: Week-over-week change in exchange warehouse inventory for the relevant metal

#### Scenario: Metal momentum calculation
- **WHEN** copper futures price was 70000 sixty days ago and is 75000 today
- **THEN** `metal_momentum_60d` for copper-linked stocks is approximately 0.0714 (7.14%)

#### Scenario: Futures basis calculation
- **WHEN** copper futures price is 75000 and spot price is 74000
- **THEN** `futures_basis` is approximately 0.0135 (1.35% contango)

### Requirement: Fundamental factors
The system SHALL compute the following fundamental factors:
- `pb_percentile`: Current PB ratio's percentile rank within its 3-year historical range
- `gross_margin_change`: Year-over-year change in gross profit margin from latest financial report
- `roe_ttm`: Trailing twelve months return on equity

#### Scenario: PB percentile at historical low
- **WHEN** a stock's current PB is at the 10th percentile of its 3-year range
- **THEN** `pb_percentile` is 0.10

#### Scenario: ROE TTM calculation
- **WHEN** a stock's trailing four quarters net income sums to 500M and average equity is 5000M
- **THEN** `roe_ttm` is 0.10 (10%)

### Requirement: Technical factors
The system SHALL compute the following technical factors:
- `momentum_60d`: 60-day stock price return
- `reversal_5d`: 5-day stock price return (negative implies reversal signal)
- `turnover_ratio_20d`: 20-day average turnover ratio
- `volatility_20d`: 20-day annualized return volatility

#### Scenario: Momentum calculation
- **WHEN** a stock's price was 10.00 sixty days ago and is 12.00 today
- **THEN** `momentum_60d` is 0.20 (20%)

#### Scenario: Volatility calculation
- **WHEN** a stock's daily returns over 20 days have a standard deviation of 0.02
- **THEN** `volatility_20d` is approximately 0.02 * sqrt(252) = 0.3175

### Requirement: Fund flow factors
The system SHALL compute the following flow factors:
- `margin_change_5d`: 5-day change in margin trading balance as a percentage
- `northbound_net_10d`: 10-day cumulative net northbound capital flow (in CNY)

#### Scenario: Margin balance increase
- **WHEN** margin balance was 100M five days ago and is 110M today
- **THEN** `margin_change_5d` is 0.10 (10%)

### Requirement: Macro factors
The system SHALL compute the following macro factors:
- `pmi_direction`: +1 if latest PMI > 50, -1 if < 50, 0 if equal (same value for all stocks)
- `usd_momentum_20d`: 20-day USD index momentum (inverse relationship: strong USD is bearish for metals)

#### Scenario: PMI above expansion threshold
- **WHEN** the latest PMI reading is 51.3
- **THEN** `pmi_direction` is +1 for all stocks

### Requirement: Cross-metal ratio factors
The system SHALL compute the following cross-metal ratio factors:
- `gold_silver_ratio` (GSR): Gold price / Silver price, with 60-day z-score
- `gold_copper_ratio` (GCR): Gold price / Copper price, with 60-day z-score
- `silver_copper_ratio` (SCR): Silver price / Copper price, with 60-day z-score
- `silver_gold_ratio` (SGR): Silver price / Gold price (inverse of GSR), with 60-day z-score

#### Scenario: GSR z-score calculation
- **WHEN** current GSR is 85 and the 60-day mean is 80 with std dev 3
- **THEN** GSR z-score is approximately 1.67

#### Scenario: GCR z-score calculation
- **WHEN** gold price is 2000 USD and copper price is 8500 USD
- **THEN** GCR raw value is approximately 0.235 and z-score is computed against 60-day history

### Requirement: Cross-sectional standardization
The system SHALL apply cross-sectional z-score standardization to all factor values across the universe. The standardized value for stock i is `(raw_i - mean) / std` where mean and std are computed across all stocks in the universe for that factor.

#### Scenario: Standardization with sufficient sample
- **WHEN** universe has 50 stocks and momentum_60d values range from -0.1 to 0.3
- **THEN** standardized values have mean approximately 0 and std approximately 1

#### Scenario: Small universe warning
- **WHEN** universe has fewer than 10 stocks
- **THEN** system prints a warning about unreliable standardization but proceeds

### Requirement: Factor matrix output
The system SHALL write the computed factor matrix to `output/factors_YYYYMMDD.csv` with columns: symbol, plus one column per factor (all standardized).

#### Scenario: Factor output file
- **WHEN** factor calculation completes for 2026-03-07 with 45 stocks and 18 factors
- **THEN** output file `output/factors_20260307.csv` has 45 rows and 19 columns (symbol + 18 factors)

### Requirement: Graceful factor failure
The system SHALL handle individual factor calculation failures by filling the failed factor column with null values and continuing with remaining factors.

#### Scenario: Single factor failure
- **WHEN** `futures_basis` calculation fails due to missing commodity data but all other factors succeed
- **THEN** the `futures_basis` column contains nulls and all other factors are computed normally
