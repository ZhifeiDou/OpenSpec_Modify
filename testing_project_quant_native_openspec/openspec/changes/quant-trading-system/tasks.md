## 1. Project Setup

- [x] 1.1 Create project directory structure: `src/data/`, `src/universe/`, `src/factors/`, `src/strategy/`, `src/risk/`, `src/backtest/`, `src/report/`, `src/timing/`, `config/`, `tests/`
- [x] 1.2 Create `requirements.txt` with all dependencies (akshare, baostock, tushare, pandas, numpy, scipy, plotly, pandas-ta, pytest)
- [x] 1.3 Create `config/settings.yaml` with all configurable parameters (data sources, factor weights, risk thresholds, backtest params)

## 2. Data Pipeline

- [x] 2.1 Implement `src/data/fetcher.py` — multi-source data fetching with AKShare/BaoStock/Tushare auto-failover
- [x] 2.2 Implement `src/data/cache.py` — SQLite caching layer with incremental update support
- [x] 2.3 Implement `src/data/api_akshare.py` — AKShare wrapper for stock prices, fundamentals, futures, macro, fund flow data
- [x] 2.4 Implement `src/data/api_baostock.py` — BaoStock wrapper as first fallback
- [x] 2.5 Implement `src/data/api_tushare.py` — Tushare wrapper as second fallback
- [x] 2.6 Write tests for data pipeline: source failover, caching, incremental update

## 3. Stock Universe

- [x] 3.1 Implement `src/universe/filter.py` — CSRC industry code filtering for non-ferrous metals (C22)
- [x] 3.2 Implement `src/universe/subsector.py` — sub-sector classification mapping (copper/aluminum/gold/lithium/cobalt/zinc/rare-earth)
- [x] 3.3 Implement `src/universe/quality.py` — liquidity and quality filters (listing days, turnover, ST exclusion)
- [x] 3.4 Write tests for universe filtering and sub-sector classification

## 4. Factor Engine

- [x] 4.1 Implement `src/factors/commodity.py` — commodity factors: metal price momentum, futures basis, inventory change
- [x] 4.2 Implement `src/factors/fundamental.py` — fundamental factors: PB percentile, gross margin trend, ROE_TTM, EV/EBITDA
- [x] 4.3 Implement `src/factors/technical.py` — technical factors: momentum (60d skip5), mean reversion (5d), turnover (20d), volatility (20d)
- [x] 4.4 Implement `src/factors/flow.py` — fund flow factors: financing balance change (5d), northbound net buy (10d)
- [x] 4.5 Implement `src/factors/macro.py` — macro factors: PMI direction, USD index momentum, M1 growth
- [x] 4.6 Implement `src/factors/normalize.py` — cross-sectional z-score normalization and ±3σ winsorization
- [x] 4.7 Write tests for each factor category and normalization

## 5. Scoring Strategy

- [x] 5.1 Implement `src/strategy/scorer.py` — equal-weight and IC-weighted composite scoring
- [x] 5.2 Implement `src/strategy/selector.py` — top 20% stock selection (max 10 stocks)
- [x] 5.3 Implement `src/strategy/allocator.py` — score-proportional position allocation with single-stock (10%) and sub-sector (25%) limits
- [x] 5.4 Write tests for scoring modes, selection, and allocation constraints

## 6. Risk Management

- [x] 6.1 Implement `src/risk/stop_loss.py` — hard stop-loss (2x ATR) and trailing stop-loss (10% gain activation, 8% peak drawdown)
- [x] 6.2 Implement `src/risk/drawdown.py` — portfolio drawdown control (15% half-position, 20% full liquidation)
- [x] 6.3 Implement `src/risk/position_sizing.py` — max 2% portfolio loss per stock position sizing
- [x] 6.4 Implement `src/risk/alerts.py` — metal crash alert (>3% daily drop)
- [x] 6.5 Write tests for stop-loss triggers, drawdown levels, position sizing, T+1 constraint on stop-loss

## 7. Market Timing

- [x] 7.1 Implement `src/timing/gold_hedge.py` — gold price momentum timing signal
- [x] 7.2 Implement `src/timing/pmi_signal.py` — PMI direction timing signal
- [x] 7.3 Implement `src/timing/composite.py` — composite timing multiplier combining all signals
- [x] 7.4 Write tests for timing signals and composite multiplier

## 8. Backtest Engine

- [x] 8.1 Implement `src/backtest/engine.py` — event-driven daily loop with fixed processing order
- [x] 8.2 Implement `src/backtest/order.py` — order queue with T+1 enforcement and limit-up/down handling
- [x] 8.3 Implement `src/backtest/portfolio.py` — portfolio state tracking (positions, cash, NAV)
- [x] 8.4 Implement `src/backtest/costs.py` — transaction cost calculation (stamp tax, commission, slippage)
- [x] 8.5 Write tests for T+1 rule, limit-up/down blocking, suspended stock handling, cost calculation

## 9. Report Dashboard

- [x] 9.1 Implement `src/report/metrics.py` — performance metrics calculation (return, drawdown, Sharpe, Calmar, win rate, P/L ratio)
- [x] 9.2 Implement `src/report/charts.py` — Plotly interactive charts (NAV curve, drawdown chart, position history)
- [x] 9.3 Implement `src/report/generator.py` — HTML report assembly and PNG export
- [x] 9.4 Write tests for metrics calculation

## 10. CLI Interface

- [x] 10.1 Implement `main.py` — CLI entry point with 7 subcommands (update, universe, factors, signal, risk-check, backtest, report)
- [x] 10.2 Integration test: end-to-end backtest with sample data
