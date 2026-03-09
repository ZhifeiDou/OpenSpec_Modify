## Purpose

Strategy backtesting engine that simulates portfolio performance over historical data with realistic transaction cost modeling, risk check integration, and comprehensive performance metrics.

## Requirements

### Requirement: Backtest date range iteration
The system SHALL iterate through the specified date range from `--from` to `--to`, rebalancing at the configured frequency (`rebalance_freq`: monthly or weekly). Between rebalance dates, the system SHALL mark positions to market daily.

#### Scenario: Monthly rebalance
- **WHEN** backtest runs from 2025-01-01 to 2025-06-30 with `rebalance_freq = monthly`
- **THEN** system rebalances at the start of each month (approximately 6 rebalance events)

#### Scenario: Weekly rebalance
- **WHEN** backtest runs with `rebalance_freq = weekly`
- **THEN** system rebalances every Monday (or next trading day if Monday is a holiday)

### Requirement: Transaction cost modeling
The system SHALL model the following costs on each trade:
- Stamp tax: `stamp_tax` rate on sell transactions only (A-share convention)
- Commission: `commission` rate on both buy and sell, with minimum `min_commission` per trade
- Slippage: `slippage` rate applied to both buy and sell executions

#### Scenario: Sell cost calculation
- **WHEN** selling 10,000 shares at 15.00 (value = 150,000) with stamp_tax=0.0005, commission=0.0003, slippage=0.0015
- **THEN** total cost = 150,000 * (0.0005 + 0.0003 + 0.0015) = 345.00

#### Scenario: Minimum commission
- **WHEN** a small trade has calculated commission of 3.00 and `min_commission = 5.0`
- **THEN** commission charged is 5.00

### Requirement: Daily NAV tracking
The system SHALL compute and record the net asset value (NAV) of the portfolio at the close of each trading day during the backtest period.

#### Scenario: NAV series
- **WHEN** backtest runs for 120 trading days
- **THEN** the NAV series has 120 data points, one per trading day

### Requirement: Performance metrics calculation
The system SHALL compute the following metrics from the backtest results:
- Annualized return
- Annualized Sharpe ratio (using configured `risk_free_rate`)
- Maximum drawdown (percentage)
- Maximum drawdown duration (trading days)
- Win rate (percentage of profitable trades)
- Total number of trades

#### Scenario: Sharpe ratio calculation
- **WHEN** daily returns have mean 0.0005 and std 0.015 with risk_free_rate=0.02
- **THEN** annualized Sharpe = (0.0005 * 252 - 0.02) / (0.015 * sqrt(252)) = approximately 0.45

#### Scenario: Max drawdown calculation
- **WHEN** NAV reaches peak 1,200,000 then drops to trough 1,020,000
- **THEN** max drawdown is (1,200,000 - 1,020,000) / 1,200,000 = 15.0%

### Requirement: Risk check integration during backtest
The system SHALL apply risk control rules (hard stop, trailing stop, drawdown limits, metal crash) during the backtest. Positions stopped out SHALL be sold at the next available price with transaction costs.

#### Scenario: Stop loss during backtest
- **WHEN** a position triggers the ATR hard stop on a non-rebalance day
- **THEN** system sells the position at next day's open price (with slippage) and records the trade

### Requirement: Backtest result persistence
The system SHALL write backtest results to `output/backtest_result.json` containing: daily NAV series, trade log (date, symbol, action, shares, price, cost), and performance metrics summary.

#### Scenario: Result file output
- **WHEN** backtest completes successfully
- **THEN** JSON file contains `nav_series` array, `trades` array, and `metrics` object

### Requirement: Configurable initial capital
The system SHALL use `initial_capital` from config (or `--capital` CLI override) as the starting portfolio value.

#### Scenario: Custom capital
- **WHEN** user runs `backtest --from 2025-01-01 --to 2025-12-31 --capital 2000000`
- **THEN** backtest starts with 2,000,000 CNY initial capital instead of the config default

### Requirement: Empty universe handling
The system SHALL hold cash (earn zero return) for any rebalance period where the filtered universe is empty.

#### Scenario: No valid stocks
- **WHEN** all stocks are filtered out during a particular month
- **THEN** portfolio holds 100% cash for that period with no trades
