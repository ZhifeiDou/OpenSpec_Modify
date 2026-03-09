## Use Cases

### Use Case: Configure Tushare API Token

**Primary Actor:** Developer / Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** Subfunction

**Stakeholders and Interests:**
- Developer — wants to securely configure their Tushare Pro token without hardcoding it in source code
- Security — token must never appear in version-controlled files

**Preconditions:**
- Developer has a Tushare Pro account and obtained their API token from https://tushare.pro/user/token

**Success Guarantee (Postconditions):**
- Token is stored in an environment variable or `.env` file
- `.env` is listed in `.gitignore`
- System can authenticate with Tushare Pro API on next run

**Trigger:** Developer sets up the project for the first time or rotates their token.

**Main Success Scenario:**
1. Developer copies `.env.example` to `.env` in the project root.
2. Developer pastes their Tushare token into the `TUSHARE_TOKEN=` field.
3. System loads the token from the environment variable on startup.
4. System validates the token by making a lightweight Tushare API call (e.g., `trade_cal`).
5. System confirms token is valid and proceeds.

**Extensions:**
- 3a. No `TUSHARE_TOKEN` environment variable found: System logs a clear error message with instructions and exits with non-zero status.
- 4a. Token is invalid or expired: System reports authentication failure with a link to the Tushare token page and exits.

---

### Use Case: Fetch Stock Daily Data via Tushare

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** User goal

**Stakeholders and Interests:**
- Quant Analyst — wants reliable, forward-adjusted daily OHLCV data for portfolio stock universe
- System — needs data in a normalized format (date, open, high, low, close, volume, amount)

**Preconditions:**
- Tushare token is configured and valid
- Stock symbols are known (from universe)

**Success Guarantee (Postconditions):**
- Stock daily data is stored in SQLite with columns: date, open, high, low, close, volume, amount
- Incremental update metadata is updated

**Trigger:** User runs `python main.py update --category stock`

**Main Success Scenario:**
1. System determines the last update date for each symbol from metadata.
2. System converts 6-digit symbol to Tushare format (e.g., `000001` → `000001.SZ`).
3. System calls `pro.daily(ts_code=..., start_date=..., end_date=...)`.
4. System maps Tushare columns (`vol` → `volume`, `trade_date` → `date`) to internal schema.
5. System validates data and stores in SQLite.
6. System updates the last-updated metadata.

**Extensions:**
- 3a. API rate limit hit: System waits `api_delay_seconds` and retries up to `max_retries` times.
- 3b. All retries exhausted: System logs the error, skips this symbol, and continues with next.
- 4a. Empty response (e.g., suspended stock or no new data): System skips with info log.

---

### Use Case: Fetch Futures Daily Data via Tushare

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** User goal

**Stakeholders and Interests:**
- Quant Analyst — needs commodity futures price data for cross-metal ratio factors

**Preconditions:**
- Tushare token configured
- Metals list defined in config (cu, al, zn, ni, sn, pb, au, ag)

**Success Guarantee (Postconditions):**
- Futures daily data stored with columns: date, open, high, low, close, settle, volume, open_interest

**Trigger:** User runs `python main.py update --category futures`

**Main Success Scenario:**
1. System iterates over configured metals.
2. System maps metal code to Tushare futures contract code (e.g., `cu` → `CU0.SHF` for main continuous contract).
3. System calls `pro.fut_daily(ts_code=..., start_date=..., end_date=...)`.
4. System maps Tushare columns (`oi` → `open_interest`) to internal schema.
5. System validates and stores data.

**Extensions:**
- 2a. Metal code not mappable to Tushare contract (e.g., `LC` for lithium): System logs warning and skips.
- 3a. API failure: Retry with delay, skip on exhaustion.

---

### Use Case: Fetch Macro Indicators via Tushare

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** User goal

**Stakeholders and Interests:**
- Quant Analyst — needs PMI, M1, CPI, PPI for macro factor scoring

**Preconditions:**
- Tushare token configured

**Success Guarantee (Postconditions):**
- Macro indicator time series stored with columns: date, value

**Trigger:** User runs `python main.py update --category macro`

**Main Success Scenario:**
1. System iterates over configured macro indicators (pmi, m1, cpi, ppi).
2. System maps each indicator to its Tushare function (`pmi` → `pro.cn_pmi()`, `m1` → `pro.cn_m()`, `cpi` → `pro.cn_cpi()`, `ppi` → `pro.cn_ppi()`).
3. System calls the Tushare function with date range parameters.
4. System extracts the relevant value column and normalizes to (date, value) format.
5. System stores in SQLite.

**Extensions:**
- 2a. Unknown indicator name: System logs warning and skips.
- 3a. Tushare returns monthly granularity (YYYYMM format): System converts to date (`YYYY-MM-01`).

---

### Use Case: Fetch Fund Flow Data via Tushare

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** User goal

**Stakeholders and Interests:**
- Quant Analyst — needs margin balance and northbound capital flow for flow factor

**Preconditions:**
- Tushare token configured
- Stock symbols known

**Success Guarantee (Postconditions):**
- Fund flow data stored with columns: date, margin_balance, northbound_net_buy

**Trigger:** User runs `python main.py update --category flow`

**Main Success Scenario:**
1. System calls `pro.margin_detail(ts_code=..., start_date=..., end_date=...)` for margin data per stock.
2. System extracts `rzrqye` (total margin+short balance) as `margin_balance`.
3. System calls `pro.moneyflow_hsgt(start_date=..., end_date=...)` for northbound flow.
4. System extracts `north_money` as `northbound_net_buy`.
5. System joins margin and northbound data on date and stores.

**Extensions:**
- 1a. Stock not in margin trading program: System stores null for margin fields.
- 3a. HSGT data not available for weekends/holidays: System skips non-trading dates.

---

### Use Case: Fetch Industry Stocks for Universe Classification

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** Subfunction

**Stakeholders and Interests:**
- Quant Analyst — needs the list of stocks in Shenwan non-ferrous metals sector

**Preconditions:**
- Tushare token configured

**Success Guarantee (Postconditions):**
- Industry stocks DataFrame with columns: symbol, name, industry_name

**Trigger:** Universe update or classification runs.

**Main Success Scenario:**
1. System calls Tushare index member API or sector classification API to get stocks in non-ferrous metals.
2. System normalizes column names to (symbol, name, industry_name).
3. System returns the DataFrame for further filtering.

**Extensions:**
- 1a. Tushare does not have a direct Shenwan L2 index member API: System uses `pro.index_member(index_code=...)` for Shenwan index constituents, or falls back to `pro.stock_basic()` filtered by industry.

---

### Use Case: Run Full Data Update Pipeline

**Primary Actor:** Quant Analyst
**Scope:** Quant Data Pipeline
**Level:** Summary

**Stakeholders and Interests:**
- Quant Analyst — wants a single command to update all data categories

**Preconditions:**
- Tushare token configured and valid
- `config/settings.yaml` specifies Tushare as primary source

**Success Guarantee (Postconditions):**
- All data categories (stock, futures, macro, flow) are up to date in SQLite

**Trigger:** User runs `python main.py update`

**Main Success Scenario:**
1. System validates Tushare token on startup.
2. System updates stock daily data for all universe symbols.
3. System updates futures data for all configured metals.
4. System updates macro indicators.
5. System updates fund flow data.
6. System prints update summary with row counts and any errors.

**Extensions:**
- 1a. Token invalid: System aborts with clear error before any API calls.
- 2a–5a. Individual category fails: System logs error and continues with remaining categories.
