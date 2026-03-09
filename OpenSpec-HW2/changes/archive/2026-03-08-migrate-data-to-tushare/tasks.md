## 1. Dependencies and Configuration

- [x] 1.1 Add `tushare` and `python-dotenv` to `requirements.txt`
- [x] 1.2 Create `.env.example` in project root with `TUSHARE_TOKEN=your_token_here`
- [x] 1.3 Add `.env` entry to `.gitignore` (create `.gitignore` if not present)
- [x] 1.4 Update `config/settings.yaml`: change `primary_source` to `tushare`, add `tushare_token_env: TUSHARE_TOKEN`, remove `fallback_sources`

## 2. Token Management

- [x] 2.1 Add `load_dotenv()` call in `src/data/pipeline.py` (or a shared startup module) to load `.env` on pipeline initialization
- [x] 2.2 Implement token loading: read env var name from config (`data.tushare_token_env`, default `TUSHARE_TOKEN`), call `os.environ.get()`, raise clear error if missing
- [x] 2.3 Implement token validation: call `pro.trade_cal(start_date=today, end_date=today)` on TushareSource init, raise error with instructions if token is invalid

## 3. TushareSource Adapter

- [x] 3.1 Create `src/data/sources/tushare_source.py` with `TushareSource` class skeleton implementing `DataSource` protocol
- [x] 3.2 Implement `_to_tushare_code(symbol)` helper: 6-digit → `XXXXXX.SZ` (0/3 prefix) or `XXXXXX.SH` (6/9 prefix)
- [x] 3.3 Implement `_to_tushare_date(date_str)` helper: `YYYY-MM-DD` → `YYYYMMDD`
- [x] 3.4 Implement `_from_tushare_date(date_str)` helper: `YYYYMMDD` → `YYYY-MM-DD` datetime
- [x] 3.5 Add retry decorator (reuse pattern from akshare_source.py) with configurable delay and max_retries
- [x] 3.6 Implement `fetch_stock_daily()`: call `pro.daily(ts_code, start_date, end_date)`, map columns (`trade_date`→`date`, `vol`→`volume`), return `[date, open, high, low, close, volume, amount]`
- [x] 3.7 Implement `fetch_financials()`: call `pro.income()` and/or `pro.balancesheet()`, map to internal schema columns
- [x] 3.8 Implement `fetch_futures_daily()`: map metal code to `{METAL}0.{EXCHANGE}` (SHF for SHFE metals, INE for LC), call `pro.fut_daily()`, map `oi`→`open_interest`, return `[date, open, high, low, close, settle, volume, open_interest]`
- [x] 3.9 Implement `fetch_inventory()`: return empty DataFrame (Tushare lacks direct inventory API)
- [x] 3.10 Implement `fetch_macro()`: map indicators to Tushare functions (`pmi`→`cn_pmi`/`pmi010000`, `m1`→`cn_m`/`m1_yoy`, `cpi`→`cn_cpi`/`nt_yoy`, `ppi`→`cn_ppi`/`ppi_yoy`), normalize monthly dates to `YYYY-MM-01`, return `[date, value]`
- [x] 3.11 Implement `fetch_fund_flow()`: call `pro.margin_detail()` for margin (`rzrqye`→`margin_balance`), call `pro.moneyflow_hsgt()` for northbound (`north_money`→`northbound_net_buy`), join on date, return `[date, margin_balance, northbound_net_buy]`
- [x] 3.12 Implement `fetch_industry_stocks()`: use Tushare index member or `stock_basic` API filtered by industry, return `[symbol, name, industry_code, industry_name]`

## 4. Pipeline Integration

- [x] 4.1 Update `src/data/pipeline.py`: import `TushareSource` instead of `AKShareSource`/`BaoStockSource`, instantiate as primary source, remove fallback logic
- [x] 4.2 Update `src/universe/classifier.py`: change `AKShareSource()` to `TushareSource()` import and instantiation
- [x] 4.3 Update `src/news/fetcher.py`: keep AKShare for news fetching, add `try/except ImportError` guard so AKShare is optional

## 5. Cleanup

- [x] 5.1 Delete `src/data/sources/akshare_source.py`
- [x] 5.2 Delete `src/data/sources/baostock_source.py`
- [x] 5.3 Remove `akshare` and `baostock` from `requirements.txt` (keep `akshare` if news fetcher still uses it, mark as optional comment)

## 6. Testing

- [x] 6.1 Update existing data source tests to mock `tushare` API calls instead of `akshare`/`baostock`
- [x] 6.2 Add unit tests for `TushareSource._to_tushare_code()` symbol conversion
- [x] 6.3 Add unit tests for `TushareSource._to_tushare_date()` and `_from_tushare_date()` date conversion
- [x] 6.4 Add unit tests for each `fetch_*` method with mocked Tushare responses
- [x] 6.5 Add test for token loading error path (missing env var)
- [ ] 6.6 Smoke test: run `python main.py update --category stock` with a real Tushare token to verify end-to-end
