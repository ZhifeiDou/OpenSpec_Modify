## Purpose

Market data acquisition module for fetching A-share stock daily OHLCV, commodity futures prices, macroeconomic indicators, and fund flow data from Tushare Pro APIs with incremental update and local SQLite storage.

## Requirements

### Requirement: Fetch stock market data
The system SHALL fetch A-share stock daily OHLCV (open, high, low, close, volume) and turnover data from Tushare Pro via `pro.daily()`. Data SHALL be stored in SQLite via the DataStore. The system SHALL convert 6-digit stock codes to Tushare format (`XXXXXX.SZ` or `XXXXXX.SH`) before calling the API.

#### Scenario: Incremental fetch
- **WHEN** local stock data exists up to 2026-03-01 and user runs `fetch-data --category stock`
- **THEN** system downloads only data from 2026-03-02 onward via Tushare and appends to existing storage

#### Scenario: Full fetch with force flag
- **WHEN** user runs `fetch-data --category stock --force`
- **THEN** system re-downloads all stock data from Tushare from scratch, replacing existing data

#### Scenario: Custom start date
- **WHEN** user runs `fetch-data --category stock --from 2025-01-01`
- **THEN** system fetches data from Tushare starting from 2025-01-01 regardless of existing local data

### Requirement: Fetch commodity futures data
The system SHALL fetch daily price data for non-ferrous metal futures (copper, aluminum, zinc, tin, nickel, lead, gold, silver) from Tushare Pro via `pro.fut_daily()`. The system SHALL use SHFE exchange suffix `.SHF` for metal futures contracts. Data SHALL be stored in SQLite.

#### Scenario: Fetch all commodity data
- **WHEN** user runs `fetch-data --category commodity`
- **THEN** system downloads futures price data for all configured metals via Tushare and stores per metal

### Requirement: Fetch macro indicator data
The system SHALL fetch macroeconomic indicators from Tushare Pro: PMI via `pro.cn_pmi()`, M1 via `pro.cn_m()`, CPI via `pro.cn_cpi()`, PPI via `pro.cn_ppi()`. Monthly YYYYMM dates SHALL be normalized to `YYYY-MM-01` format.

#### Scenario: Fetch macro data
- **WHEN** user runs `fetch-data --category macro`
- **THEN** system downloads PMI, M1, CPI, and PPI data from Tushare and stores in SQLite

### Requirement: Fetch fund flow data
The system SHALL fetch margin trading data via `pro.margin_detail()` and northbound capital flow via `pro.moneyflow_hsgt()` from Tushare Pro.

#### Scenario: Fetch flow data
- **WHEN** user runs `fetch-data --category flow`
- **THEN** system downloads margin and northbound flow data from Tushare and stores in SQLite

### Requirement: Fetch all data categories
The system SHALL support fetching all categories in a single command.

#### Scenario: Fetch all
- **WHEN** user runs `fetch-data` or `fetch-data --category all`
- **THEN** system fetches stock, commodity, macro, and flow data sequentially via Tushare

### Requirement: API retry on failure
The system SHALL retry failed Tushare API requests up to `max_retries` times with `api_delay_seconds` delay between retries.

#### Scenario: Transient API failure
- **WHEN** a Tushare API request fails on the first attempt but succeeds on retry
- **THEN** system retries and completes the fetch without error

#### Scenario: Persistent API failure
- **WHEN** all retry attempts are exhausted
- **THEN** system reports the error and continues with remaining data categories
