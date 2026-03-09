## Context

The quant data pipeline currently uses AKShare (primary) and BaoStock (fallback) to fetch A-share market data across 7 categories: stock daily, financials, futures, inventory, macro, fund flow, and industry stocks. All data sources implement the `DataSource` protocol defined in `src/data/sources/base.py`. The pipeline orchestrator in `src/data/pipeline.py` hardcodes `AKShareSource` as primary and `BaoStockSource` as fallback.

Additionally, `src/news/fetcher.py` directly imports AKShare for news, and `src/universe/classifier.py` directly imports `AKShareSource` for industry stock classification.

Tushare Pro requires a registered account token (free tier: 120 points/day, 2000+ points unlock advanced APIs). The token is obtained from https://tushare.pro/user/token.

## Goals / Non-Goals

**Goals:**
- Replace all AKShare/BaoStock data fetching with Tushare Pro API calls
- Implement secure token management via environment variables / `.env` file
- Maintain the existing `DataSource` protocol — downstream code (pipeline, factors, backtest) unchanged
- Provide clear setup instructions for token configuration

**Non-Goals:**
- Keeping AKShare/BaoStock as fallback sources (clean replacement)
- Changing the `DataSource` protocol interface or return column schemas
- Modifying downstream consumers (factors, strategy, risk, backtest, report)
- Adding Tushare Pro paid-tier features (real-time quotes, tick data)
- Migrating news fetching if Tushare's news API is insufficient (keep AKShare for news only if needed)

## Decisions

### Decision 1: Direct replacement, not multi-source abstraction
**Choice**: Replace AKShare/BaoStock entirely with Tushare rather than adding Tushare as another option alongside them.
**Rationale**: The user explicitly requested replacing all data interfaces. Maintaining multiple adapters adds complexity without benefit since Tushare covers all required data categories. The `DataSource` protocol already provides the abstraction layer — swapping one implementation for another is clean.
**Alternative considered**: Keep AKShare as fallback behind Tushare. Rejected because it doubles the maintenance surface and the user wants a complete migration.

### Decision 2: Token via environment variable with python-dotenv
**Choice**: Use `os.environ.get()` with `python-dotenv` loading from `.env` file.
**Rationale**: This is the standard Python pattern for secret management. It works in development (`.env` file), CI (environment variables), and production (secrets managers that inject env vars). No custom config parsing needed.
**Alternative considered**: Store token in `settings.yaml`. Rejected because YAML files are version-controlled, creating a security risk.

### Decision 3: Symbol format conversion in TushareSource
**Choice**: Handle all symbol format conversion (6-digit → `XXXXXX.SZ`/`.SH`, metal code → `CU0.SHF`) inside `TushareSource`, keeping the public interface using the same plain codes the rest of the system uses.
**Rationale**: Encapsulates Tushare-specific format requirements. No changes needed in pipeline, factors, or any caller code.

### Decision 4: Macro indicator value extraction
**Choice**: Map each macro indicator to a specific Tushare column:
- `pmi` → `cn_pmi().pmi010000` (manufacturing PMI)
- `m1` → `cn_m().m1_yoy` (M1 YoY growth)
- `cpi` → `cn_cpi().nt_yoy` (national CPI YoY)
- `ppi` → `cn_ppi().ppi_yoy` (PPI YoY)
**Rationale**: These are the most commonly used headline values. The existing system returns `(date, value)` for macro data — we pick the single most relevant column.

### Decision 5: Futures contract code mapping
**Choice**: Map metal codes to Tushare continuous main contract codes:
```
cu → CU0.SHF    al → AL0.SHF    zn → ZN0.SHF
ni → NI0.SHF    sn → SN0.SHF    pb → PB0.SHF
au → AU0.SHF    ag → AG0.SHF    LC → LC0.INE
```
All SHFE metals use `.SHF` suffix. Lithium carbonate (`LC`) is traded on INE (`.INE`).
**Rationale**: Tushare uses `{METAL}0.{EXCHANGE}` for continuous main contracts, matching our existing concept of `metal + "0"` from AKShare.

### Decision 6: News fetching strategy
**Choice**: Keep AKShare for news fetching (`stock_news_em`) since Tushare's news API has limited coverage for sector-specific keyword search. Mark the AKShare dependency as optional (news-only).
**Rationale**: Tushare's `news()` function provides general market news but lacks the keyword-based financial news search that `stock_news_em` provides. News is a secondary feature — switching it provides no benefit.
**Alternative considered**: Remove news fetching entirely. Rejected because sentiment factor depends on it.

### Decision 7: Fund flow data — separate margin and northbound calls
**Choice**: Call `pro.margin_detail()` per stock for margin data, and `pro.moneyflow_hsgt()` once for aggregate northbound flow. Join on date.
**Rationale**: Tushare separates these into distinct APIs (unlike AKShare's `stock_hsgt_individual_em` which was per-stock northbound). Northbound flow is market-wide, so one call suffices for all stocks.

## Risks / Trade-offs

**[Risk] Tushare point system limits API calls** → Free tier has 120 points/day. Most APIs require 100-2000 points accumulated (not per-day). Mitigation: Users need to accumulate points via Tushare community participation. Document minimum point requirements (2000 for futures/margin data).

**[Risk] Tushare date format differences** → Tushare uses `YYYYMMDD` strings vs our internal `YYYY-MM-DD`. Mitigation: Convert in TushareSource — strip hyphens on input, add hyphens on output.

**[Risk] Inventory data may not be available via Tushare** → Tushare does not have a direct warehouse inventory API for metals. Mitigation: `fetch_inventory` returns empty DataFrame (same as BaoStock did). If needed later, can add a specialized source.

**[Risk] Breaking change for existing users** → Users with existing AKShare/BaoStock setups will need to obtain a Tushare token. Mitigation: Clear error message on missing token with setup instructions. Provide `.env.example`.

**[Trade-off] Single source dependency** → Removing fallback means if Tushare is down, data pipeline fails. Acceptable because: (1) Tushare has good uptime, (2) pipeline already handles partial failures gracefully, (3) data is cached in SQLite.

## Migration Plan

1. Add `tushare` and `python-dotenv` to `requirements.txt`
2. Create `.env.example` with `TUSHARE_TOKEN=your_token_here`
3. Add `.env` to `.gitignore`
4. Create `src/data/sources/tushare_source.py` implementing `DataSource`
5. Update `src/data/pipeline.py` to use `TushareSource` as primary, remove fallback
6. Update `src/universe/classifier.py` to use `TushareSource`
7. Update `src/news/fetcher.py` — keep AKShare for news, add import guard
8. Update `config/settings.yaml` — add `tushare_token_env` field, change `primary_source`
9. Remove `src/data/sources/akshare_source.py` and `src/data/sources/baostock_source.py`
10. Update tests to mock Tushare API calls

**Rollback**: Restore deleted AKShare/BaoStock files from git history. Revert pipeline.py changes.

## Open Questions

- Should we add `pro.daily_basic()` for PE/PB data to enrich the financials method, or keep the current financial abstract approach?
- What is the minimum Tushare point level required for all APIs we use? Need to document this clearly for users.
- Should `fetch_inventory` attempt to use Tushare's `fut_holding()` (futures holdings) as a proxy for inventory data?
