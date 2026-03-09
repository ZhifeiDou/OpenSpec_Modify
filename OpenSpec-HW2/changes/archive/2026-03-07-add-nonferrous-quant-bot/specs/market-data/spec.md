## ADDED Requirements

### Requirement: Fetch stock market data
The system SHALL fetch A-share stock daily OHLCV (open, high, low, close, volume) and turnover data from the configured API endpoint. Data SHALL be stored as CSV files in `{data_dir}/stock/` with one file per stock symbol.

#### Scenario: Incremental fetch
- **WHEN** local stock data exists up to 2026-03-01 and user runs `fetch-data --category stock`
- **THEN** system downloads only data from 2026-03-02 onward and appends to existing files

#### Scenario: Full fetch with force flag
- **WHEN** user runs `fetch-data --category stock --force`
- **THEN** system re-downloads all stock data from scratch, replacing existing files

#### Scenario: Custom start date
- **WHEN** user runs `fetch-data --category stock --from 2025-01-01`
- **THEN** system fetches data starting from 2025-01-01 regardless of existing local data

### Requirement: Fetch commodity futures data
The system SHALL fetch daily price data for non-ferrous metal futures (copper, aluminum, zinc, tin, nickel, lead, gold, silver) from the configured API. Data SHALL be stored in `{data_dir}/commodity/`.

#### Scenario: Fetch all commodity data
- **WHEN** user runs `fetch-data --category commodity`
- **THEN** system downloads futures price data for all configured metals and writes CSV files per metal

### Requirement: Fetch macro indicator data
The system SHALL fetch macroeconomic indicators (PMI, USD index, interest rates) and store them in `{data_dir}/macro/`.

#### Scenario: Fetch macro data
- **WHEN** user runs `fetch-data --category macro`
- **THEN** system downloads the latest macro indicator values and appends to local CSV files

### Requirement: Fetch fund flow data
The system SHALL fetch margin trading balance and northbound capital flow data, storing in `{data_dir}/flow/`.

#### Scenario: Fetch flow data
- **WHEN** user runs `fetch-data --category flow`
- **THEN** system downloads margin and northbound flow data and writes to local CSV files

### Requirement: Fetch all data categories
The system SHALL support fetching all categories in a single command.

#### Scenario: Fetch all
- **WHEN** user runs `fetch-data` or `fetch-data --category all`
- **THEN** system fetches stock, commodity, macro, and flow data sequentially

### Requirement: API retry on failure
The system SHALL retry failed API requests up to `max_retries` times with `api_delay_ms` delay between retries.

#### Scenario: Transient API failure
- **WHEN** an API request fails on the first attempt but succeeds on retry
- **THEN** system retries and completes the fetch without error

#### Scenario: Persistent API failure
- **WHEN** all retry attempts are exhausted
- **THEN** system reports the error with the HTTP status code and exits with non-zero status
