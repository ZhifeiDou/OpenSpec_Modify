## ADDED Requirements

### Requirement: Industry classification based stock filtering
The system SHALL use Shenwan (申万) industry classification to identify non-ferrous metals sector stocks. The primary source SHALL be Shenwan Level-1 industry code 801050. The system SHALL also map stocks to Shenwan Level-2 sub-sectors.

#### Scenario: Get full non-ferrous metals universe
- **WHEN** user requests the stock universe for a given date
- **THEN** system returns all stocks classified under Shenwan non-ferrous metals (801050) as of that date

#### Scenario: Fallback on classification data failure
- **WHEN** Shenwan classification API is unavailable
- **THEN** system uses the most recently cached classification data and logs a warning

### Requirement: Sub-sector classification
The system SHALL classify each stock into one of 7 sub-sectors: copper (铜), aluminum (铝), gold (黄金), rare earth (稀土), lithium (锂), cobalt-nickel (钴镍), zinc-lead (锌铅). Classification SHALL be based on Shenwan Level-2 codes and the company's primary revenue source.

#### Scenario: Classify a copper mining company
- **WHEN** stock "601899" (Zijin Mining) is in the universe
- **THEN** system assigns sub-sector "copper" based on its primary business

#### Scenario: List stocks by sub-sector
- **WHEN** user queries all stocks in the "lithium" sub-sector
- **THEN** system returns only stocks whose primary classification is lithium

### Requirement: Automatic exclusion filters
The system SHALL automatically exclude: ST and *ST stocks, stocks suspended on the query date, stocks listed less than 60 trading days, and stocks with 20-day average daily turnover below 5 million CNY.

#### Scenario: Exclude ST stocks
- **WHEN** stock "000666" is marked as ST on the query date
- **THEN** system excludes it from the universe and records the exclusion reason

#### Scenario: Exclude illiquid stocks
- **WHEN** stock "600961" has a 20-day average daily turnover of 3 million CNY
- **THEN** system excludes it from the universe with reason "below liquidity threshold"

#### Scenario: Exclude recently listed stocks
- **WHEN** stock IPO date is within the last 60 trading days
- **THEN** system excludes it from the universe with reason "newly listed"

### Requirement: Configurable filter thresholds
The system SHALL allow users to override default filter thresholds: minimum listing days (default 60), minimum daily turnover (default 5 million CNY). Custom thresholds SHALL be persisted in configuration.

#### Scenario: User raises liquidity threshold
- **WHEN** user sets minimum daily turnover to 10 million CNY
- **THEN** system uses 10 million as the cutoff for subsequent universe queries

### Requirement: Point-in-time universe
The system SHALL support querying the universe as of any historical date, using the industry classification and stock status valid on that date, to prevent look-ahead bias in backtesting.

#### Scenario: Historical universe query
- **WHEN** user queries the universe as of 2023-06-30
- **THEN** system returns stocks that were classified as non-ferrous metals on that date, including stocks that have since been delisted or reclassified
