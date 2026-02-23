# Factor Engine

## Purpose
Compute and standardize all alpha factors used by the quantitative strategy, spanning fundamental, technical, commodity, macro, and fund flow categories, with cross-sectional normalization for comparable scoring.

## Requirements

### Requirement: Fundamental factor calculation
The system SHALL compute the following fundamental factors for each stock: PB percentile (current PB rank within 3-year history), gross margin quarter-over-quarter change, ROE TTM, and EV/EBITDA. Financial data SHALL use the most recently disclosed report.

#### Scenario: Calculate PB percentile
- **WHEN** system computes PB percentile for stock "601899" with 3-year lookback
- **THEN** result is a value between 0 and 1 representing where current PB falls in the 3-year distribution

#### Scenario: Handle missing financial data
- **WHEN** a stock has not yet disclosed Q3 financials while others have
- **THEN** system uses the Q2 report for that stock and flags the factor value as "lagged"

### Requirement: Technical factor calculation
The system SHALL compute: 60-day momentum (skipping most recent 5 days), 5-day reversal, 20-day turnover ratio (current vs 20-day average), and 20-day realized volatility (standard deviation of daily returns).

#### Scenario: Calculate 60-day momentum with skip
- **WHEN** system computes momentum for a stock on date T
- **THEN** result equals close[T-5] / close[T-65] - 1, using adjusted closing prices

#### Scenario: Insufficient data for factor
- **WHEN** a stock has fewer than 65 trading days of price history
- **THEN** system returns NaN for that stock's momentum factor and excludes it from cross-sectional ranking

### Requirement: Commodity factor calculation
The system SHALL compute: related metal SHFE 60-day price momentum, futures basis (spot minus near-month futures / near-month futures), and LME/SHFE inventory weekly change rate. Each stock SHALL be linked to its primary metal for commodity factor mapping.

#### Scenario: Compute copper price momentum for a copper stock
- **WHEN** system computes commodity factor for stock "601899" (copper-related)
- **THEN** system uses SHFE copper main contract 60-day return as the factor value

#### Scenario: Compute inventory change rate
- **WHEN** SHFE copper inventory was 150,000 tons last week and 140,000 tons this week
- **THEN** inventory change rate is (140000 - 150000) / 150000 = -6.67%, indicating destocking

### Requirement: Macro factor calculation
The system SHALL compute: PMI month-over-month direction (rising = 1, falling = -1), USD index 20-day momentum, and M1 YoY growth direction. Macro factors SHALL be applied uniformly across all stocks (not stock-specific).

#### Scenario: PMI direction factor
- **WHEN** last month PMI was 49.8 and this month PMI is 50.2
- **THEN** PMI direction factor value is 1 (rising)

#### Scenario: Macro data publication lag
- **WHEN** the latest PMI has not been published yet for the current month
- **THEN** system uses the most recently available PMI value

### Requirement: Fund flow factor calculation
The system SHALL compute: individual stock margin balance 5-day change rate, and northbound capital 10-day cumulative net buy amount. These factors SHALL be stock-specific.

#### Scenario: Compute margin balance change
- **WHEN** stock "601899" margin balance was 500M CNY 5 days ago and is 550M CNY today
- **THEN** margin balance change rate is (550 - 500) / 500 = 10%

#### Scenario: Missing margin data
- **WHEN** margin data is not available for a particular stock (e.g., not on margin trading list)
- **THEN** system sets margin factor to 0 (neutral) for that stock

### Requirement: Cross-sectional standardization
The system SHALL standardize all factor values cross-sectionally using: (1) winsorize at 3x MAD (Median Absolute Deviation) to handle outliers, then (2) Z-Score normalization (subtract mean, divide by standard deviation). The standardized factor matrix (stocks x factors) SHALL be the output.

#### Scenario: Winsorize extreme values
- **WHEN** a stock's PB percentile Z-Score raw value is 5.2 (far from mean)
- **THEN** system clips it to 3x MAD boundary before Z-Score normalization

#### Scenario: Small universe warning
- **WHEN** fewer than 10 stocks remain in the universe after filters
- **THEN** system logs a warning that cross-sectional standardization may be unreliable
