## ADDED Requirements

### Requirement: Commodity factor calculation
The system SHALL compute commodity-related factors with configurable weight (default 35%): metal price momentum (60-day), futures basis (spot vs futures), and inventory change rate.

#### Scenario: Metal price momentum
- **WHEN** system calculates commodity factors for a stock
- **THEN** metal price momentum is computed as the 60-day return of the corresponding metal futures price

#### Scenario: Futures basis
- **WHEN** spot and futures prices are available for a metal
- **THEN** basis factor is calculated as (spot - futures) / futures

### Requirement: Fundamental factor calculation
The system SHALL compute fundamental factors with configurable weight (default 25%): PB percentile (3-year rolling), gross margin trend, ROE_TTM, and EV/EBITDA.

#### Scenario: PB percentile
- **WHEN** 3-year PB history is available for a stock
- **THEN** PB percentile ranks current PB against the 3-year distribution (lower percentile = cheaper = better score)

#### Scenario: Insufficient history for PB
- **WHEN** a stock has less than 1 year of PB data
- **THEN** PB factor returns NaN for that stock

### Requirement: Technical factor calculation
The system SHALL compute technical factors with configurable weight (default 20%): momentum (60-day skip 5), mean reversion (5-day), turnover ratio (20-day), and realized volatility (20-day).

#### Scenario: Momentum factor
- **WHEN** system calculates momentum for a stock
- **THEN** momentum is the 60-day return excluding the most recent 5 days

#### Scenario: Mean reversion factor
- **WHEN** system calculates mean reversion
- **THEN** factor value is the negative of the 5-day return (lower recent return = higher reversion score)

### Requirement: Fund flow factor calculation
The system SHALL compute fund flow factors with configurable weight (default 15%): financing balance change (5-day) and northbound fund net buy amount (10-day).

#### Scenario: Northbound flow
- **WHEN** northbound fund flow data is available
- **THEN** factor value is the 10-day cumulative net buy amount for the stock

### Requirement: Macro factor calculation
The system SHALL compute macro factors with configurable weight (default 5%): PMI direction, USD index momentum, and M1 growth direction.

#### Scenario: PMI direction
- **WHEN** latest PMI data is available
- **THEN** PMI direction factor is +1 if PMI > 50 (expansion), -1 if PMI < 50 (contraction)

### Requirement: Factor standardization
The system SHALL standardize all factor values using cross-sectional z-score normalization and winsorize extreme values at ±3 standard deviations before scoring.

#### Scenario: Z-score normalization
- **WHEN** raw factor values are computed for all stocks in the universe
- **THEN** each factor is z-score normalized across all stocks (mean=0, std=1)

#### Scenario: Winsorization
- **WHEN** a z-score exceeds ±3
- **THEN** the value is clipped to ±3
