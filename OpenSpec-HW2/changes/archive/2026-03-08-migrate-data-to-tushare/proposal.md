## Why

The current data pipeline relies on AKShare (primary) and BaoStock (fallback) as market data providers. AKShare's free API is unstable with frequent rate-limiting and occasional breaking changes in response formats. Tushare Pro provides a more stable, well-documented API with consistent data quality for A-share stocks, futures, macro indicators, and fund flows — all data categories the system requires. Migrating to Tushare as the primary source improves reliability and data consistency while also adding secure token-based authentication.

## What Changes

- **BREAKING**: Replace AKShare as primary data source with Tushare Pro across all data categories (stock daily, financials, futures, macro, fund flow, news, industry classification)
- Remove BaoStock fallback adapter (Tushare covers all required data)
- Add Tushare token management via environment variable (`TUSHARE_TOKEN`) with `.env` file support
- Update `config/settings.yaml` to configure Tushare as primary source with token env var reference
- Add symbol format conversion layer (current 6-digit codes → Tushare `XXXXXX.SZ`/`XXXXXX.SH` format)
- Update futures symbol format (current `cu0` → Tushare `CU0.SHF` format)
- Map macro indicator functions to Tushare equivalents (`cn_pmi`, `cn_m`, `cn_cpi`, `cn_ppi`)
- Replace AKShare news fetching with Tushare `news()` or keep AKShare news as optional fallback
- Update `requirements.txt`: add `tushare`, `python-dotenv`; optionally keep `akshare` for news fallback

## Capabilities

### New Capabilities
- `tushare-data-source`: Tushare Pro adapter implementing the DataSource protocol for all 7 data methods (stock daily, financials, futures, inventory, macro, fund flow, industry stocks)
- `token-management`: Secure API token handling via environment variables and `.env` file with validation on startup

### Modified Capabilities
- `market-data`: Primary source changes from AKShare to Tushare; symbol format changes; macro indicator API mapping changes
- `stock-universe`: Industry stock classification source changes from AKShare/Shenwan index to Tushare member API

## Impact

- **Code**: `src/data/sources/` — new `tushare_source.py`, remove `akshare_source.py` and `baostock_source.py`
- **Code**: `src/data/pipeline.py` — update primary/fallback source instantiation
- **Code**: `src/news/fetcher.py` — replace AKShare news API call (or keep as fallback)
- **Code**: `src/universe/classifier.py` — update data source import
- **Config**: `config/settings.yaml` — add `tushare_token_env` field, update `primary_source`
- **Dependencies**: `requirements.txt` — add `tushare`, `python-dotenv`
- **New file**: `.env.example` — template showing `TUSHARE_TOKEN=your_token_here`
- **Security**: Token never hardcoded; loaded from environment variable only
