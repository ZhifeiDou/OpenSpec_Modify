## ADDED Requirements

### Requirement: Event-driven daily loop
The system SHALL implement an event-driven backtesting engine that iterates day by day, processing events in a fixed order: update prices → check risk/stop-loss → execute pending orders → rebalance (if rebalance day) → record NAV.

#### Scenario: Daily processing order
- **WHEN** backtest processes a trading day
- **THEN** events execute in order: price_update → risk_check → order_execution → rebalance → nav_record

### Requirement: T+1 trading rule
The system SHALL enforce the A-share T+1 rule: shares purchased on day T cannot be sold until day T+1.

#### Scenario: Same-day sell blocked
- **WHEN** a sell signal is generated for a stock bought on the current day
- **THEN** sell order is queued and executed on the next trading day

#### Scenario: Next-day sell allowed
- **WHEN** a sell signal is generated for a stock held since yesterday or earlier
- **THEN** sell order is executed immediately at current day's price

### Requirement: Limit-up and limit-down handling
The system SHALL simulate the A-share 10% daily price limit: no buy execution at limit-up, no sell execution at limit-down.

#### Scenario: Buy blocked at limit-up
- **WHEN** a buy order targets a stock that hit the 10% limit-up
- **THEN** buy order is cancelled for the day

#### Scenario: Sell blocked at limit-down
- **WHEN** a sell order targets a stock that hit the 10% limit-down
- **THEN** sell order is deferred to the next trading day

### Requirement: Suspended stock handling
The system SHALL detect suspended stocks (zero volume) and freeze their positions — no buy or sell orders executed.

#### Scenario: Stock suspended
- **WHEN** a stock has zero trading volume on a given day
- **THEN** all pending orders for that stock are deferred until trading resumes

### Requirement: Transaction cost simulation
The system SHALL deduct realistic transaction costs: stamp tax 0.05% (sell only), commission 0.03% (both sides, minimum 5 CNY), and slippage 0.15%.

#### Scenario: Sell transaction costs
- **WHEN** a sell order of ¥100,000 is executed
- **THEN** costs deducted = stamp_tax(¥50) + commission(max(¥30, ¥5)) + slippage(¥150) = ¥230

#### Scenario: Buy transaction costs
- **WHEN** a buy order of ¥100,000 is executed
- **THEN** costs deducted = commission(max(¥30, ¥5)) + slippage(¥150) = ¥180

### Requirement: Monthly rebalancing
The system SHALL rebalance the portfolio on a configurable schedule (default: monthly on the first trading day of each month).

#### Scenario: Monthly rebalance trigger
- **WHEN** the current trading day is the first trading day of a new month
- **THEN** system triggers a full portfolio rebalance: compute factors → score → generate signals

### Requirement: NAV tracking
The system SHALL track daily net asset value (NAV) and record it for performance analysis.

#### Scenario: Daily NAV calculation
- **WHEN** all orders and costs are processed for the day
- **THEN** NAV = cash + Σ(shares × close_price) for all held positions
