## ADDED Requirements

### Requirement: Multi-source data fetching
The system SHALL support fetching market data from multiple data sources (AKShare as primary, BaoStock and Tushare as fallback), with automatic failover when the primary source is unavailable or returns errors.

#### Scenario: Primary source available
- **WHEN** AKShare API is accessible and returns valid data
- **THEN** system fetches data from AKShare and stores it in local SQLite database

#### Scenario: Primary source fails with fallback
- **WHEN** AKShare API fails or times out
- **THEN** system automatically retries with BaoStock, and if BaoStock also fails, tries Tushare

#### Scenario: All sources fail
- **WHEN** all three data sources are unavailable
- **THEN** system logs error with details and raises a DataSourceError exception

### Requirement: Local SQLite caching
The system SHALL cache all fetched data in a local SQLite database to minimize redundant API calls and support offline analysis.

#### Scenario: Data already cached
- **WHEN** requested data date range is fully covered in local cache
- **THEN** system returns cached data without making any API call

#### Scenario: Incremental update
- **WHEN** user runs `update` command and local cache has data up to date D
- **THEN** system only fetches data from date D+1 to today, appending to existing cache

### Requirement: Multi-type data support
The system SHALL fetch and store stock prices (daily OHLCV), fundamental data (PB, ROE, gross margin, EV/EBITDA), metal futures prices, macro indicators (PMI, USD index, M1), and northbound fund flow data.

#### Scenario: Stock price data fetch
- **WHEN** user requests price data for a given stock code and date range
- **THEN** system returns a DataFrame with columns: date, open, high, low, close, volume, amount

#### Scenario: Fundamental data fetch
- **WHEN** user requests fundamental data for a stock
- **THEN** system returns latest PB, ROE_TTM, gross_margin, EV_EBITDA values

#### Scenario: Metal futures data fetch
- **WHEN** user requests metal futures data for copper, aluminum, gold, etc.
- **THEN** system returns daily settlement prices for the specified metal commodity

#### Scenario: Macro indicator fetch
- **WHEN** user requests macro data
- **THEN** system returns latest PMI value, USD index, and M1 growth rate

### Requirement: API rate limiting
The system SHALL enforce configurable delays between API calls to avoid triggering rate limits from data providers.

#### Scenario: Rate limit compliance
- **WHEN** system makes consecutive API calls to the same data source
- **THEN** system waits at least the configured delay (default 0.5s) between each call
