## ADDED Requirements

### Requirement: Industry classification filtering
The system SHALL filter stocks belonging to the non-ferrous metals sector using China Securities Regulatory Commission (CSRC) industry classification codes.

#### Scenario: Filter by industry code
- **WHEN** system runs universe selection
- **THEN** only stocks classified under non-ferrous metals industry (CSRC code C22) are included

### Requirement: Sub-sector classification
The system SHALL classify filtered stocks into sub-sectors: copper, aluminum, gold, lithium, cobalt, zinc, and rare earth, based on their primary business.

#### Scenario: Sub-sector mapping
- **WHEN** a stock is identified as non-ferrous metals
- **THEN** system assigns it to one of the 7 predefined sub-sectors based on keyword matching in business description

### Requirement: Liquidity and quality filter
The system SHALL exclude stocks that fail minimum liquidity or quality criteria: minimum listing days (default 120), minimum daily turnover threshold, and ST/\*ST status.

#### Scenario: Exclude newly listed stocks
- **WHEN** a stock has been listed for fewer than 120 trading days
- **THEN** stock is excluded from the universe

#### Scenario: Exclude low turnover stocks
- **WHEN** a stock's 20-day average turnover is below the configured threshold
- **THEN** stock is excluded from the universe

#### Scenario: Exclude ST stocks
- **WHEN** a stock has ST or *ST designation
- **THEN** stock is excluded from the universe

### Requirement: Dynamic universe update
The system SHALL regenerate the stock universe on each rebalance day, reflecting newly listed stocks, delistings, and classification changes.

#### Scenario: Universe refresh on rebalance
- **WHEN** the backtest engine reaches a rebalance date
- **THEN** system recalculates the stock universe using current classification and filter criteria
