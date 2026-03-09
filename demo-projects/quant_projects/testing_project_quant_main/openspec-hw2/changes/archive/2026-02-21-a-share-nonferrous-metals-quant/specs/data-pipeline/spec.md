## ADDED Requirements

### Requirement: Multi-source data acquisition
The system SHALL support fetching data from AKShare (primary), BaoStock (historical supplement), and Tushare (financial supplement). Each data source SHALL be wrapped in an adapter with a unified interface so that sources can be swapped or added without changing downstream code.

#### Scenario: Fetch daily OHLCV data from AKShare
- **WHEN** user requests stock price update for symbol "601899" from "2024-01-01" to "2024-12-31"
- **THEN** system returns a DataFrame with columns: date, open, high, low, close, volume, amount, with all values non-null and prices > 0

#### Scenario: Fallback when primary source fails
- **WHEN** AKShare API returns an error or times out after 2 retries
- **THEN** system logs the error and attempts to fetch the same data from BaoStock, returning the result transparently

### Requirement: Incremental data update
The system SHALL track the last-updated timestamp for each data category (stock prices, financials, futures, macro, fund flows) and only fetch new records since the last update. Full re-download SHALL be available via an explicit force-refresh option.

#### Scenario: Incremental stock price update
- **WHEN** local database has stock prices up to 2024-11-30 and user requests update
- **THEN** system fetches only data from 2024-12-01 onward, appends to local storage, and updates the timestamp

#### Scenario: Force full refresh
- **WHEN** user triggers update with force-refresh flag
- **THEN** system re-downloads all data for the specified category, replacing existing records

### Requirement: Commodity futures data
The system SHALL fetch SHFE futures prices (copper cu, aluminum al, zinc zn, nickel ni, tin sn, lead pb) and LME corresponding metal prices. The system SHALL also fetch SHFE warehouse inventory data and futures basis (spot minus futures).

#### Scenario: Fetch SHFE copper main contract price
- **WHEN** user requests copper futures update
- **THEN** system returns daily OHLCV for the continuous main contract (cu0) with settlement price

#### Scenario: Fetch LME metals prices
- **WHEN** user requests LME data update
- **THEN** system returns daily closing prices for all 6 base metals (copper, aluminum, zinc, nickel, tin, lead)

### Requirement: Macro and fund flow data
The system SHALL fetch macro indicators (PMI, USD/CNY exchange rate, M1 money supply, total social financing) and fund flow data (margin trading balances, northbound capital net inflow per stock).

#### Scenario: Fetch PMI data
- **WHEN** user requests macro data update
- **THEN** system returns monthly PMI values with publication dates, including the latest available month

#### Scenario: Fetch northbound capital data
- **WHEN** user requests fund flow update for stock "601899"
- **THEN** system returns daily northbound net buy amount and cumulative holding shares

### Requirement: Data quality validation
The system SHALL validate all fetched data before writing to storage. Validation checks SHALL include: no null values in required fields, prices within reasonable ranges (> 0), date continuity (no unexpected gaps on trading days), and no duplicate records.

#### Scenario: Detect anomalous price data
- **WHEN** fetched data contains a stock price of 0 or negative
- **THEN** system flags the record as anomalous, excludes it from storage, and includes it in the update summary warning

#### Scenario: Detect date gaps
- **WHEN** fetched daily data is missing a trading day that is not a holiday
- **THEN** system logs a warning with the missing date(s) in the update summary

### Requirement: Local storage with caching
The system SHALL store all data locally using SQLite (default) or Parquet files. The storage format SHALL be configurable. Repeated queries for the same data range SHALL be served from local cache without network requests.

#### Scenario: Cache hit on repeated query
- **WHEN** user queries stock prices for a date range that is fully covered by local storage
- **THEN** system returns data from local storage without making any API calls

#### Scenario: Switch storage backend
- **WHEN** user configures storage format as "parquet" in settings
- **THEN** system reads and writes all data using Parquet files instead of SQLite
