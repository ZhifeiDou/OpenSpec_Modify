# Backtest Engine

## Purpose
Simulate the quantitative strategy over historical data with realistic A-share market constraints including T+1 trading rules, price limits, transaction costs, and survivorship bias prevention, producing reliable performance metrics.

## Requirements

### Requirement: Event-driven backtest loop
The system SHALL run backtests by iterating through trading days chronologically. On each day, the system SHALL: (1) update market data, (2) check risk management conditions, (3) execute pending orders, (4) on rebalance days execute factor scoring and signal generation. The backtest SHALL produce a daily NAV series.

#### Scenario: Monthly rebalance backtest
- **WHEN** user runs backtest from 2022-01-01 to 2024-12-31 with monthly rebalance
- **THEN** system executes rebalance on the first trading day of each month and produces 3 years of daily NAV data

#### Scenario: Daily risk check during backtest
- **WHEN** a held stock triggers stop-loss on a non-rebalance day
- **THEN** system executes the stop-loss sell on the next available day (respecting T+1)

### Requirement: T+1 trading rule enforcement
The system SHALL enforce A-share T+1 rule: stocks bought on day T cannot be sold until day T+1 or later. Any sell signal generated on the buy date SHALL be deferred to the next trading day.

#### Scenario: Cannot sell on buy day
- **WHEN** system buys stock "601899" on Monday and stop-loss triggers on the same Monday
- **THEN** system defers the sell to Tuesday

#### Scenario: Normal sell
- **WHEN** system bought stock "601899" on Monday and sell signal triggers on Wednesday
- **THEN** system executes the sell on Wednesday (T+1 constraint satisfied)

### Requirement: Price limit handling
The system SHALL simulate A-share price limit rules: ±10% for main board stocks, ±20% for ChiNext/STAR Market. Buy orders SHALL fail when the stock is at upper limit. Sell orders SHALL fail when the stock is at lower limit. Failed orders SHALL be retried on subsequent days.

#### Scenario: Cannot buy at upper limit
- **WHEN** target stock closes at +9.8% (near upper limit) on the execution day
- **THEN** system marks the buy as failed, retains cash, and retries next day

#### Scenario: Cannot sell at lower limit
- **WHEN** held stock closes at -9.8% (near lower limit) and stop-loss is pending
- **THEN** system marks the sell as failed and retries the next trading day

### Requirement: Transaction cost simulation
The system SHALL deduct realistic transaction costs for each trade: stamp tax 0.05% (sell only), broker commission 0.03% (both sides, minimum 5 CNY), and configurable slippage (default 0.15%). Total single-trip cost SHALL be approximately 0.08-0.12%.

#### Scenario: Sell transaction cost calculation
- **WHEN** selling 100,000 CNY worth of stock
- **THEN** total cost = stamp tax 50 + commission 30 + slippage 150 = 230 CNY (0.23%)

#### Scenario: Minimum commission
- **WHEN** trade value is 10,000 CNY (commission would be 3 CNY)
- **THEN** system applies minimum commission of 5 CNY

### Requirement: Survivorship bias prevention
The system SHALL use point-in-time industry classification data. The stock universe at each backtest date SHALL include only stocks that were classified as non-ferrous metals on that date, including stocks that have since been delisted, renamed, or reclassified.

#### Scenario: Include delisted stock in historical period
- **WHEN** backtesting over 2020-2024 and stock "600xxx" was delisted in 2023
- **THEN** system includes "600xxx" in the universe for dates before its delisting

#### Scenario: Exclude future IPO
- **WHEN** backtesting date is 2022-01-01 and stock "688xxx" IPO'd in 2023
- **THEN** system excludes "688xxx" from the 2022-01-01 universe

### Requirement: Suspension handling
The system SHALL handle stock suspensions: suspended stocks cannot be bought or sold. If a held stock is suspended, its position SHALL be frozen until trading resumes. The stock's last traded price SHALL be used for NAV calculation during suspension.

#### Scenario: Held stock suspended
- **WHEN** stock "601899" is suspended for 5 trading days while held
- **THEN** system freezes the position, uses last traded price for NAV, and resumes normal handling on the resume day

### Requirement: Performance metrics output
The system SHALL compute and output: annualized return, annualized volatility, Sharpe ratio (risk-free rate = 2%), maximum drawdown (peak-to-trough), maximum drawdown duration, win rate, profit/loss ratio, total turnover, and total transaction costs.

#### Scenario: Complete metrics output
- **WHEN** backtest completes
- **THEN** system outputs all metrics plus a daily NAV DataFrame and a trade log DataFrame with entry/exit dates, prices, returns, and costs for each trade
