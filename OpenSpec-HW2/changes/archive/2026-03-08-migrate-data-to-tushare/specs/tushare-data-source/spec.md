## ADDED Requirements

### Requirement: Tushare adapter implements DataSource protocol
The system SHALL provide a `TushareSource` class in `src/data/sources/tushare_source.py` that implements the `DataSource` protocol with all 7 methods: `fetch_stock_daily`, `fetch_financials`, `fetch_futures_daily`, `fetch_inventory`, `fetch_macro`, `fetch_fund_flow`, `fetch_industry_stocks`.

#### Scenario: Protocol compliance
- **WHEN** `TushareSource` is instantiated
- **THEN** `isinstance(source, DataSource)` returns `True`

### Requirement: Fetch stock daily OHLCV via Tushare
The system SHALL call `pro.daily(ts_code=..., start_date=..., end_date=...)` to fetch daily stock data. The system SHALL convert the 6-digit symbol input to Tushare format (`XXXXXX.SZ` for codes starting with 0/3, `XXXXXX.SH` for codes starting with 6/9`). The system SHALL map Tushare output columns to the internal schema: `trade_date` → `date`, `vol` → `volume`, and return columns `[date, open, high, low, close, volume, amount]`.

#### Scenario: Fetch Shenzhen stock
- **WHEN** `fetch_stock_daily("000001", "2025-01-01", "2025-01-31")` is called
- **THEN** system calls `pro.daily(ts_code="000001.SZ", start_date="20250101", end_date="20250131")` and returns a DataFrame with columns `[date, open, high, low, close, volume, amount]`

#### Scenario: Fetch Shanghai stock
- **WHEN** `fetch_stock_daily("600000", "2025-01-01", "2025-01-31")` is called
- **THEN** system calls `pro.daily(ts_code="600000.SH", start_date="20250101", end_date="20250131")`

#### Scenario: Empty result
- **WHEN** Tushare returns an empty DataFrame (e.g., suspended stock)
- **THEN** system returns an empty DataFrame without raising an exception

### Requirement: Fetch financial statements via Tushare
The system SHALL call `pro.income(ts_code=...)` and `pro.balancesheet(ts_code=...)` to fetch financial data. The system SHALL map available fields to the internal schema columns: `symbol, report_date, pb, roe_ttm, gross_margin, ev, ebitda, total_revenue, net_profit, total_assets, total_liabilities`.

#### Scenario: Fetch financials for a stock
- **WHEN** `fetch_financials("000001")` is called
- **THEN** system calls Tushare income and balance sheet APIs and returns a DataFrame with available financial columns

#### Scenario: No financial data available
- **WHEN** Tushare returns empty for a stock's financials
- **THEN** system returns an empty DataFrame

### Requirement: Fetch futures daily via Tushare
The system SHALL call `pro.fut_daily(ts_code=..., start_date=..., end_date=...)` to fetch futures data. The system SHALL map metal codes to Tushare contract symbols using exchange suffix `.SHF` for SHFE metals (cu, al, zn, ni, sn, pb, au, ag). The continuous main contract code SHALL be uppercase metal + `0` (e.g., `cu` → `CU0.SHF`).

#### Scenario: Fetch copper futures
- **WHEN** `fetch_futures_daily("cu", "2025-01-01", "2025-06-30")` is called
- **THEN** system calls `pro.fut_daily(ts_code="CU0.SHF", start_date="20250101", end_date="20250630")` and returns columns `[date, open, high, low, close, settle, volume, open_interest]`

#### Scenario: Map Tushare futures columns
- **WHEN** Tushare returns `oi` column
- **THEN** system renames it to `open_interest` in the output DataFrame

### Requirement: Fetch macro indicators via Tushare
The system SHALL map macro indicator names to Tushare functions: `pmi` → `pro.cn_pmi()`, `m1` → `pro.cn_m()`, `cpi` → `pro.cn_cpi()`, `ppi` → `pro.cn_ppi()`. The system SHALL normalize monthly YYYYMM date format to `YYYY-MM-01` date and extract the primary value column for each indicator.

#### Scenario: Fetch PMI
- **WHEN** `fetch_macro("pmi")` is called
- **THEN** system calls `pro.cn_pmi()` and returns a DataFrame with columns `[date, value]` where value is `pmi010000` (manufacturing PMI)

#### Scenario: Fetch M1 money supply
- **WHEN** `fetch_macro("m1")` is called
- **THEN** system calls `pro.cn_m()` and returns a DataFrame with columns `[date, value]` where value is the `m1_yoy` (M1 year-over-year growth rate)

#### Scenario: Fetch CPI
- **WHEN** `fetch_macro("cpi")` is called
- **THEN** system calls `pro.cn_cpi()` and returns a DataFrame with columns `[date, value]` where value is `nt_yoy` (national CPI YoY)

#### Scenario: Fetch PPI
- **WHEN** `fetch_macro("ppi")` is called
- **THEN** system calls `pro.cn_ppi()` and returns a DataFrame with columns `[date, value]` where value is `ppi_yoy`

#### Scenario: Unsupported indicator
- **WHEN** `fetch_macro("unknown_indicator")` is called
- **THEN** system logs a warning and returns an empty DataFrame

### Requirement: Fetch fund flow via Tushare
The system SHALL fetch margin data via `pro.margin_detail(ts_code=..., start_date=..., end_date=...)` extracting `rzrqye` as `margin_balance`. The system SHALL fetch northbound flow via `pro.moneyflow_hsgt(start_date=..., end_date=...)` extracting `north_money` as `northbound_net_buy`. The system SHALL return a DataFrame with columns `[date, margin_balance, northbound_net_buy]`.

#### Scenario: Fetch fund flow for a stock
- **WHEN** `fetch_fund_flow("000001", "2025-01-01", "2025-01-31")` is called
- **THEN** system returns DataFrame with margin balance and northbound flow columns

#### Scenario: Stock not in margin program
- **WHEN** Tushare margin_detail returns empty for the stock
- **THEN** system returns DataFrame with `margin_balance` as NaN and northbound flow populated

### Requirement: Fetch industry stocks via Tushare
The system SHALL use Tushare's index member or sector classification API to retrieve stocks in a given industry classification. The system SHALL return a DataFrame with columns `[symbol, name, industry_code, industry_name]`.

#### Scenario: Fetch non-ferrous metals stocks
- **WHEN** `fetch_industry_stocks("801050")` is called
- **THEN** system returns a DataFrame listing stocks in the Shenwan non-ferrous metals sector

### Requirement: Rate limiting and retry
The system SHALL respect `api_delay_seconds` between API calls and retry failed calls up to `max_retries` times. The retry decorator SHALL be configurable via constructor parameters.

#### Scenario: Retry on transient failure
- **WHEN** a Tushare API call fails on the first attempt but succeeds on retry
- **THEN** system returns the successful result without raising an exception

#### Scenario: All retries exhausted
- **WHEN** all retry attempts fail
- **THEN** system raises the last exception to the caller
