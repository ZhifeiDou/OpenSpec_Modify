## 1. Project Scaffold & Config

- [x] 1.1 Create Rust project with Cargo.toml (polars, reqwest, clap, chrono, serde, toml, comfy-table, thiserror)
- [x] 1.2 Implement `config.rs`: Config struct with nested sections (data, universe, factors, strategy, risk, backtest), TOML deserialization, and validation (factor weights sum to 1.0)
- [x] 1.3 Create `config.toml` with default values for all sections
- [x] 1.4 Implement `main.rs` CLI with clap derive: all 8 subcommands (fetch-data, universe, calc-factors, signal, risk-check, backtest, report, config) with their argument definitions
- [x] 1.5 Implement `config` subcommand: show and validate actions

## 2. Data Fetching Module

- [x] 2.1 Implement `data/fetcher.rs`: HTTP client wrapper with retry logic (max_retries, api_delay_ms)
- [x] 2.2 Implement `data/parser.rs`: CSV parsing utilities for stock, commodity, macro, and flow data
- [x] 2.3 Implement `data/mod.rs` `run_fetch()`: dispatch by category (stock/commodity/macro/flow/all), detect last-fetched date for incremental updates, support --force full re-download and --from custom start date
- [x] 2.4 Create `data/` directory structure with subdirectories (stock, commodity, macro, flow)

## 3. Stock Universe Module

- [x] 3.1 Implement `universe/subsector.rs`: Shenwan non-ferrous metals sector classification and sub-sector tagging (copper, aluminum, zinc, tin, nickel, lead, rare earth, tungsten, lithium, cobalt, precious metals, other)
- [x] 3.2 Implement `universe/filter.rs`: apply filters (ST exclusion, suspension, min_listing_days, min_daily_turnover), load/save universe CSV
- [x] 3.3 Implement `universe/mod.rs` `run_universe()`: update action (filter and write), show action (display breakdown), --subsector filtering

## 4. Factor Engine — Traits & Infrastructure

- [x] 4.1 Implement `factors/traits.rs`: FactorCalculator trait (name, category, calculate) and FactorCategory enum (Commodity, Fundamental, Technical, Flow, Macro, CrossMetal)
- [x] 4.2 Implement `factors/standardizer.rs`: cross-sectional z-score standardization across all factor columns

## 5. Factor Engine — Individual Factors

- [x] 5.1 Implement `factors/commodity.rs`: MetalMomentum60d, FuturesBasis, InventoryChange
- [x] 5.2 Implement `factors/fundamental.rs`: PbPercentile, GrossMarginChange, RoeTtm
- [x] 5.3 Implement `factors/technical.rs`: Momentum60d, Reversal5d, TurnoverRatio20d, Volatility20d
- [x] 5.4 Implement `factors/flow.rs`: MarginChange5d, NorthboundNet10d
- [x] 5.5 Implement `factors/macro_factor.rs`: PmiDirection, UsdMomentum20d
- [x] 5.6 Implement `factors/cross_metal.rs`: GoldSilverRatio (GSR), GoldCopperRatio (GCR), SilverCopperRatio (SCR), SilverGoldRatio (SGR) with 60-day z-scores
- [x] 5.7 Implement `factors/mod.rs` `run_calc_factors()`: register all calculators, iterate and compute, handle failures with null fill, write factor matrix CSV

## 6. Signal Generation Module

- [x] 6.1 Implement `strategy/scorer.rs`: compute composite score per stock using configured factor category weights
- [x] 6.2 Implement `strategy/allocator.rs`: score-proportional weight allocation with max_single_weight and max_subsector_weight constraints (iterative clip and redistribute)
- [x] 6.3 Implement `strategy/timing.rs`: timing multiplier based on PMI direction and metal/USD momentum (range 0.0–1.0)
- [x] 6.4 Implement `strategy/signal.rs`: trade delta calculation (buy/sell/hold) when current portfolio is provided
- [x] 6.5 Implement `strategy/mod.rs` `run_signal()`: load factors, score, allocate, apply timing, output signal table and CSV

## 7. Risk Control Module

- [x] 7.1 Implement ATR hard stop loss check: flag positions with loss > hard_stop_atr_multiple * 20-day ATR
- [x] 7.2 Implement trailing stop: track peak price, activate after trailing_stop_activation gain, trigger on trailing_stop_drop from peak
- [x] 7.3 Implement portfolio max drawdown control: reduce at max_drawdown_reduce threshold, liquidate at max_drawdown_liquidate
- [x] 7.4 Implement metal crash circuit breaker: detect sector index drop > metal_crash_threshold, halt new buys
- [x] 7.5 Implement `risk/mod.rs` `run_risk_check()`: load portfolio, run all checks, output risk report table

## 8. Backtest Engine

- [x] 8.1 Implement backtest date range iteration with configurable rebalance frequency (monthly/weekly)
- [x] 8.2 Implement transaction cost modeling: stamp tax (sell only), commission (with minimum), slippage
- [x] 8.3 Implement daily mark-to-market NAV tracking
- [x] 8.4 Integrate risk checks during backtest: execute stop-loss trades at next day open
- [x] 8.5 Implement performance metrics: annualized return, Sharpe ratio, max drawdown, max drawdown duration, win rate, total trades
- [x] 8.6 Implement `backtest/mod.rs` `run_backtest()`: main loop, write backtest_result.json with NAV series, trade log, and metrics
- [x] 8.7 Handle empty universe periods (hold cash)

## 9. Report Module

- [x] 9.1 Implement summary metrics display (annualized return, Sharpe, max drawdown, duration, trades, win rate, profit factor, final NAV)
- [x] 9.2 Implement multi-format output: table (comfy-table), CSV, JSON
- [x] 9.3 Implement --holdings analysis: per-stock breakdown with entry/exit price, PnL, weight
- [x] 9.4 Implement --factors analysis: portfolio factor exposure by category and individual loadings
- [x] 9.5 Implement --drawdowns analysis: top 5 drawdown periods with start/trough/recovery dates
- [x] 9.6 Implement `report/mod.rs` `run_report()`: load source (default or --source), dispatch format, apply optional analyses

## 10. Testing

- [x] 10.1 Add unit tests for config loading and validation
- [x] 10.2 Add unit tests for universe filtering logic
- [x] 10.3 Add unit tests for each factor calculator (commodity, fundamental, technical, flow, macro, cross-metal)
- [x] 10.4 Add unit tests for composite scoring and weight allocation
- [x] 10.5 Add unit tests for risk check rules (hard stop, trailing stop, drawdown, crash)
- [x] 10.6 Add unit tests for transaction cost calculations
- [x] 10.7 Add integration test: end-to-end backtest with sample data
