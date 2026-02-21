## 1. Project Setup

- [x] 1.1 Create project directory structure (src/data, src/universe, src/factors, src/strategy, src/risk, src/backtest, src/report, config, tests, notebooks)
- [x] 1.2 Create requirements.txt with dependencies (akshare, baostock, tushare, pandas, numpy, scipy, plotly, matplotlib, mplfinance, pyyaml, pandas-ta)
- [x] 1.3 Create config/settings.yaml with all default parameters (data sources, factor weights, risk thresholds, backtest costs)
- [x] 1.4 Create main.py CLI entry point with argparse commands (update, universe, factors, signal, risk-check, backtest, report)
- [x] 1.5 Set up pytest configuration and test directory structure

## 2. Data Pipeline (data-pipeline)

- [x] 2.1 Implement DataSource protocol in src/data/sources/base.py with unified interface (fetch_stock_daily, fetch_financials, fetch_futures_daily, fetch_macro, fetch_fund_flow)
- [x] 2.2 Implement AKShareSource adapter in src/data/sources/akshare_source.py with 0.5s API delay and retry logic (2 retries)
- [x] 2.3 Implement BaoStockSource adapter in src/data/sources/baostock_source.py as fallback for historical stock data
- [x] 2.4 Implement storage layer in src/data/storage.py with SQLite backend (tables: stock_daily, financials, futures_daily, macro, fund_flow, meta)
- [x] 2.5 Implement data pipeline in src/data/pipeline.py with incremental update logic (check last_updated timestamp, fetch only new records)
- [x] 2.6 Implement data quality validators in src/data/validators.py (null check, price range check, date continuity check, duplicate check)
- [x] 2.7 Add force-refresh option to pipeline for full re-download
- [x] 2.8 Write tests for data pipeline (mock API responses, verify incremental logic, verify validation)

## 3. Stock Universe (stock-universe)

- [x] 3.1 Implement Shenwan industry classifier in src/universe/classifier.py (fetch 801050 constituents, map to Level-2 sub-sectors)
- [x] 3.2 Define SUBSECTOR_METAL_MAP mapping sub-sectors to futures symbols (copper→cu, aluminum→al, gold→au, lithium→LC, cobalt_nickel→ni, zinc_lead→zn)
- [x] 3.3 Implement stock filters in src/universe/filter.py (exclude ST, suspended, newly listed < 60 days, daily turnover < 5M)
- [x] 3.4 Implement point-in-time universe query for backtesting (use historical classification data to prevent look-ahead bias)
- [x] 3.5 Add configurable filter thresholds from settings.yaml
- [x] 3.6 Write tests for universe (verify filtering logic, sub-sector mapping, point-in-time correctness)

## 4. Factor Engine (factor-engine)

- [x] 4.1 Implement BaseFactor class and factor registry in src/factors/base.py (decorator-based registration, compute() method returning pd.Series)
- [x] 4.2 Implement fundamental factors in src/factors/fundamental.py (pb_percentile_3y, gross_margin_qoq_change, roe_ttm, ev_ebitda)
- [x] 4.3 Implement technical factors in src/factors/technical.py (momentum_60d_skip5, reversal_5d, turnover_ratio_20d, realized_volatility_20d)
- [x] 4.4 Implement commodity factors in src/factors/commodity.py (metal_price_momentum_60d, futures_basis, inventory_weekly_change)
- [x] 4.5 Implement macro factors in src/factors/macro.py (pmi_direction, usd_index_momentum_20d, m1_yoy_direction)
- [x] 4.6 Implement fund flow factors in src/factors/flow.py (margin_balance_change_5d, northbound_net_buy_10d)
- [x] 4.7 Implement cross-sectional standardizer in src/factors/standardizer.py (MAD winsorization at 3x, Z-Score normalization)
- [x] 4.8 Handle edge cases: missing financial data (use lagged), insufficient history (return NaN), small universe warning (< 10 stocks)
- [x] 4.9 Write tests for each factor category (verify calculation correctness with known inputs, verify standardization)

## 5. Scoring Strategy (scoring-strategy)

- [x] 5.1 Implement multi-factor scorer in src/strategy/scorer.py (equal-weight mode: commodity 35%, fundamental 25%, technical 20%, flow 15%, macro 5%)
- [x] 5.2 Implement stock selection by ranking (top N = min(max_stocks, floor(universe * 0.2)))
- [x] 5.3 Implement IC-weighted scoring mode in scorer.py (rolling 12-month rank IC, fallback to equal-weight when history < 12 months)
- [x] 5.4 Implement position allocator in src/strategy/allocator.py (score-proportional weights, single stock cap 10%, sub-sector cap 25%)
- [x] 5.5 Implement trade signal generator in src/strategy/signal.py (compare target vs current holdings, output BUY/ADD/REDUCE/SELL signals with estimated costs)
- [x] 5.6 Implement skip-trivial-rebalance logic (skip when all weight changes < 2%)
- [x] 5.7 Write tests for scoring and allocation (verify weight constraints, verify signal generation)

## 6. Market Timing (market-timing)

- [x] 6.1 Implement commodity momentum timing in src/strategy/timing.py (check SHFE copper/aluminum 20d and 60d momentum, output position ratio 1.0/0.6/0.3/0.2)
- [x] 6.2 Implement gold hedging signal (shift to gold sub-sector when industrial metals negative and gold momentum > 5%)
- [x] 6.3 Implement timing override mechanism (user can force a fixed position ratio via config)
- [x] 6.4 Write tests for timing logic (verify each signal scenario from spec)

## 7. Risk Management (risk-management)

- [x] 7.1 Implement hard stop-loss in src/risk/stop_loss.py (trigger when loss > 2x ATR, flag for sell respecting T+1)
- [x] 7.2 Implement trailing stop-loss (activate at +10% gain, trigger when price drops 8% from peak)
- [x] 7.3 Implement portfolio drawdown monitor in src/risk/drawdown.py (tiered response: 15% → reduce to 50%, 20% → recommend liquidation)
- [x] 7.4 Implement volatility-based position sizer in src/risk/position_sizer.py (max loss per stock = 2% of portfolio at 2x ATR stop distance)
- [x] 7.5 Implement metal price crash alert in src/risk/alerts.py (trigger when any metal drops > 3% daily, list affected holdings)
- [x] 7.6 Write tests for risk management (verify stop-loss triggers, drawdown thresholds, position sizing calculations)

## 8. Backtest Engine (backtest-engine)

- [x] 8.1 Implement portfolio state manager in src/backtest/portfolio.py (track holdings, cash, NAV, drawdown, buy dates for T+1 enforcement)
- [x] 8.2 Implement simulated broker in src/backtest/broker.py (T+1 rule, price limit detection ±10%/±20%, suspension detection, transaction cost deduction)
- [x] 8.3 Implement backtest engine main loop in src/backtest/engine.py (daily iteration: update prices → check risk → execute orders → rebalance on schedule → record NAV)
- [x] 8.4 Implement survivorship bias prevention (use point-in-time universe from stock-universe module at each backtest date)
- [x] 8.5 Implement performance metrics calculator in src/backtest/metrics.py (annualized return, volatility, Sharpe ratio, max drawdown, max drawdown duration, win rate, profit/loss ratio, turnover, total costs)
- [x] 8.6 Output trade log DataFrame (entry/exit dates, prices, returns, costs per trade)
- [x] 8.7 Write integration test: run full backtest over 1 year of sample data and verify metrics are within reasonable ranges

## 9. Report Dashboard (report-dashboard)

- [x] 9.1 Implement NAV curve chart in src/report/charts.py (strategy vs benchmark line chart using Plotly)
- [x] 9.2 Implement drawdown underwater chart (filled area chart, highlight worst drawdown period)
- [x] 9.3 Implement holdings overview (table + sub-sector pie chart)
- [x] 9.4 Implement factor exposure heatmap (stocks x factor categories, color by Z-Score)
- [x] 9.5 Implement factor IC tracking chart (rolling 12-month IC per factor, reference line at 0.03)
- [x] 9.6 Implement report exporter in src/report/exporter.py (HTML with interactive Plotly, PNG with Matplotlib fallback)
- [x] 9.7 Add Chinese font support for Plotly charts
- [x] 9.8 Write tests for report generation (verify chart objects are created, verify HTML export produces valid file)

## 10. Integration & Documentation

- [x] 10.1 Wire all modules together in main.py CLI (update → universe → factors → signal → risk-check → backtest → report)
- [x] 10.2 Create a Jupyter notebook in notebooks/ demonstrating full workflow (data update → backtest → view report)
- [x] 10.3 Run end-to-end integration test: full pipeline from data fetch to report generation
- [x] 10.4 Add inline code comments for key algorithms (factor calculation, backtest loop, risk checks)
- [x] 10.5 Create a README.md with setup instructions, usage guide, and architecture overview
