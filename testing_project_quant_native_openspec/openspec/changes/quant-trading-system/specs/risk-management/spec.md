## ADDED Requirements

### Requirement: Hard stop-loss
The system SHALL trigger a hard stop-loss sell when a stock's unrealized loss exceeds 2x ATR (approximately 6-8%), forcing immediate liquidation of the position.

#### Scenario: Hard stop-loss triggered
- **WHEN** a stock's current price drops below entry_price - 2 × ATR(14)
- **THEN** system generates a sell signal for 100% of the position

#### Scenario: T+1 constraint on stop-loss
- **WHEN** a hard stop-loss is triggered on a stock bought today (T+0)
- **THEN** sell order is queued for execution on the next trading day (T+1)

### Requirement: Trailing stop-loss
The system SHALL activate a trailing stop after a stock gains 10% from entry, and trigger a sell when the price drops 8% from its peak since entry.

#### Scenario: Trailing stop activation
- **WHEN** a stock's highest price since entry exceeds entry_price × 1.10
- **THEN** trailing stop is activated with threshold at peak_price × 0.92

#### Scenario: Trailing stop triggered
- **WHEN** trailing stop is active and current price drops below peak_price × 0.92
- **THEN** system generates a sell signal for 100% of the position

### Requirement: Portfolio drawdown control
The system SHALL implement tiered portfolio drawdown control: reduce to 50% position when portfolio drawdown exceeds 15%, and fully liquidate when drawdown exceeds 20%.

#### Scenario: Level-1 drawdown (15%)
- **WHEN** portfolio NAV drops more than 15% from its historical peak
- **THEN** system reduces all positions to 50% of target weight

#### Scenario: Level-2 drawdown (20%)
- **WHEN** portfolio NAV drops more than 20% from its historical peak
- **THEN** system liquidates all positions

### Requirement: Position sizing
The system SHALL limit maximum loss per stock to 2% of total portfolio value when calculating position sizes.

#### Scenario: Position size calculation
- **WHEN** system calculates position size for a new stock
- **THEN** max_shares = (portfolio_value × 0.02) / (2 × ATR(14))

### Requirement: Metal crash alert
The system SHALL monitor daily metal futures prices and generate an alert when any tracked metal drops more than 3% in a single day.

#### Scenario: Metal crash detected
- **WHEN** a metal futures price drops more than 3% from previous close
- **THEN** system generates a metal crash alert with metal name and drop percentage
