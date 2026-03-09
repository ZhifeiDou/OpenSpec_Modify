## Use Cases

### Use Case: Fetch market data

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs fresh market data for factor calculation and backtesting

**Preconditions:**
- config.toml exists with valid API endpoint and data directory settings

**Success Guarantee (Postconditions):**
- Local data directory contains up-to-date CSV files for the requested category
- Incremental fetch only downloads new data since last update

**Trigger:** User runs `quant-bot fetch-data`

**Main Success Scenario:**
1. User invokes `fetch-data` with optional category filter (stock, commodity, macro, flow, or all)
2. System reads config to determine API endpoint and data directory
3. System detects the last-fetched date from existing local files
4. System downloads incremental data from the API for the date range
5. System writes CSV files to the local data directory
6. System reports the number of records fetched and the date range covered

**Extensions:**
- 3a. No local files exist: System performs a full download from the configured start date
- 4a. API returns error or timeout: System retries up to max_retries, then reports error
- 1a. User passes `--force`: System ignores local cache and re-downloads all data

---

### Use Case: Manage stock universe

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs a filtered set of non-ferrous metal stocks to trade

**Preconditions:**
- Market data has been fetched (stock listing data available locally)

**Success Guarantee (Postconditions):**
- Universe file contains only stocks passing all filter criteria
- Stocks are tagged with their sub-sector classification

**Trigger:** User runs `quant-bot universe update`

**Main Success Scenario:**
1. User invokes `universe update`
2. System loads raw stock list from local data
3. System filters by Shenwan non-ferrous metals sector classification
4. System applies exclusion rules: ST stocks, suspended stocks, stocks with listing days < threshold
5. System applies minimum daily turnover filter
6. System writes the filtered universe to a local CSV
7. System prints the universe count and sub-sector breakdown

**Extensions:**
- 2a. No stock data available: System reports error and suggests running `fetch-data` first
- 1a. User passes `--subsector copper`: System further filters to the specified sub-sector only
- 1b. User runs `universe show`: System displays the current universe without updating

---

### Use Case: Calculate factor values

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs standardized factor scores for signal generation

**Preconditions:**
- Stock universe has been generated
- Required market, commodity, and macro data are available locally

**Success Guarantee (Postconditions):**
- Factor matrix CSV written to output directory with one row per stock, one column per factor
- All factor values are cross-sectionally standardized (z-score)

**Trigger:** User runs `quant-bot calc-factors`

**Main Success Scenario:**
1. User invokes `calc-factors` with an optional date
2. System loads the current universe
3. System iterates through all registered factor calculators (commodity, fundamental, technical, flow, macro, cross-metal ratio)
4. Each calculator reads relevant data and computes raw factor values for the universe
5. System applies cross-sectional z-score standardization to all factor columns
6. System writes the factor matrix to `output/factors_YYYYMMDD.csv`
7. System reports the number of stocks and factors computed

**Extensions:**
- 2a. Universe is empty: System warns and exits without computing
- 2b. Universe has fewer than 10 stocks: System warns about unreliable standardization but continues
- 4a. A single factor calculator fails: System fills that column with nulls and continues with remaining factors

---

### Use Case: Generate trading signals

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs actionable buy/sell/hold signals with target weights

**Preconditions:**
- Factor matrix has been calculated for the current date

**Success Guarantee (Postconditions):**
- Signal output contains target portfolio weights for each stock
- Weights respect max single stock and max sub-sector constraints

**Trigger:** User runs `quant-bot signal`

**Main Success Scenario:**
1. User invokes `signal` with an optional current portfolio file
2. System loads the latest factor matrix
3. System computes a composite score per stock using configured factor category weights
4. System ranks stocks and selects top N (max_stocks)
5. System runs the allocator to assign weights respecting concentration limits
6. System applies timing adjustment based on macro/market conditions
7. System outputs the target portfolio with stock symbols, weights, and suggested trades

**Extensions:**
- 2a. No factor matrix found: System reports error and suggests running `calc-factors` first
- 1a. Current portfolio provided: System calculates trade deltas (buys/sells) relative to current holdings
- 6a. Timing signal is extreme bearish: System reduces overall position size

---

### Use Case: Execute risk check

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs to verify portfolio is within risk limits before/after trading

**Preconditions:**
- A current portfolio (holdings CSV) exists

**Success Guarantee (Postconditions):**
- Risk report shows per-position and portfolio-level risk status
- Any breached limits are flagged with recommended action

**Trigger:** User runs `quant-bot risk-check`

**Main Success Scenario:**
1. User invokes `risk-check` with a portfolio file
2. System loads the portfolio holdings
3. System evaluates per-position rules: ATR hard stop, trailing stop activation/drop
4. System evaluates portfolio-level rules: max drawdown thresholds
5. System checks for metal crash condition (sector index drop > threshold)
6. System outputs a risk report with status per position and overall portfolio

**Extensions:**
- 3a. A position has breached the hard stop: System flags it as "liquidate immediately"
- 4a. Drawdown exceeds reduce threshold but not liquidate: System recommends partial reduction
- 4b. Drawdown exceeds liquidate threshold: System recommends full liquidation
- 5a. Metal crash detected: System recommends halting all new buys

---

### Use Case: Run strategy backtest

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs to evaluate strategy performance on historical data before live trading

**Preconditions:**
- Historical market data is available for the backtest date range
- Factor calculators are configured

**Success Guarantee (Postconditions):**
- Backtest result JSON contains daily NAV series, trade log, and performance metrics
- Performance metrics include annualized return, Sharpe ratio, max drawdown, win rate

**Trigger:** User runs `quant-bot backtest --from YYYY-MM-DD --to YYYY-MM-DD`

**Main Success Scenario:**
1. User invokes `backtest` with start date, end date, and optional capital/rebalance frequency
2. System initializes portfolio with the specified capital
3. System iterates through each rebalance period in the date range
4. At each rebalance: system computes factors, generates signals, and executes trades with cost modeling (stamp tax, commission, slippage)
5. Between rebalances: system marks positions to market daily and applies risk checks
6. System computes final performance metrics
7. System writes backtest results to `output/backtest_result.json`

**Extensions:**
- 1a. Start date is after end date: System reports error
- 4a. No valid stocks in universe for a rebalance period: System holds cash for that period
- 5a. Risk check triggers stop-loss during a period: System executes the stop and records the trade

---

### Use Case: View performance report

**Primary Actor:** Quant trader
**Scope:** Quant trading bot CLI
**Level:** User goal

**Stakeholders and Interests:**
- Quant trader - needs a readable summary of strategy or backtest performance

**Preconditions:**
- A backtest result file or NAV CSV exists

**Success Guarantee (Postconditions):**
- Report is displayed in the requested format (table, CSV, or JSON)

**Trigger:** User runs `quant-bot report`

**Main Success Scenario:**
1. User invokes `report` with optional source file and format
2. System loads the backtest result or NAV data
3. System computes summary metrics (return, Sharpe, max drawdown, win rate, etc.)
4. System formats output in the requested format
5. System displays the report

**Extensions:**
- 1a. User passes `--holdings`: System includes per-stock holding analysis in the report
- 1b. User passes `--factors`: System includes factor exposure breakdown
- 1c. User passes `--drawdowns`: System includes drawdown period analysis with recovery times
- 2a. Source file not found: System looks for the default backtest result path
