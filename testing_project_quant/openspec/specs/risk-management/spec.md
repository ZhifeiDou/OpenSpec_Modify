# Risk Management

## Purpose
Enforce position-level and portfolio-level risk controls including stop-loss mechanisms, drawdown limits, volatility-based position sizing, and metal price crash alerts to protect capital.

## Requirements

### Requirement: Individual stock hard stop-loss
The system SHALL trigger a hard stop-loss when a position's unrealized loss exceeds 2x the stock's 20-day ATR (approximately 6-8%). When triggered, the system SHALL mark the position for full liquidation at the next available trading opportunity.

#### Scenario: Hard stop-loss triggered
- **WHEN** stock "601899" entry price is 15.00, 20-day ATR is 0.60, and current price drops to 13.70 (loss = 1.30 > 2 * 0.60 = 1.20)
- **THEN** system flags "601899" for immediate sell with reason "hard stop-loss"

#### Scenario: Stop-loss on T+0 (cannot sell)
- **WHEN** hard stop-loss is triggered on the same day as purchase (T+0)
- **THEN** system flags the position for sell on T+1 due to A-share T+1 rule

### Requirement: Trailing stop-loss for profitable positions
The system SHALL activate a trailing stop-loss when a position's unrealized gain exceeds 10%. Once activated, the system SHALL trigger a sell when the price drops more than 8% from its highest price since entry.

#### Scenario: Trailing stop activated and triggered
- **WHEN** stock "601899" entry at 15.00, reached high of 18.00 (gain 20%), then drops to 16.50 (8.3% below high)
- **THEN** system flags "601899" for sell with reason "trailing stop-loss"

#### Scenario: Trailing stop not yet activated
- **WHEN** stock "601899" has unrealized gain of 7% (below 10% threshold)
- **THEN** trailing stop is not active, only hard stop-loss applies

### Requirement: Portfolio drawdown control
The system SHALL compute portfolio-level drawdown (peak-to-trough decline). The system SHALL enforce tiered responses: reduce to 50% position when drawdown exceeds 15%, and recommend full liquidation when drawdown exceeds 20%.

#### Scenario: Drawdown exceeds 15%
- **WHEN** portfolio peak value was 1,000,000 and current value is 840,000 (drawdown 16%)
- **THEN** system generates signals to reduce all positions to 50% of current weight

#### Scenario: Drawdown exceeds 20%
- **WHEN** portfolio drawdown reaches 21%
- **THEN** system recommends full liquidation and marks strategy as "paused"

### Requirement: Position sizing by volatility
The system SHALL size each position so that the maximum loss per stock (at 2x ATR stop distance) does not exceed 2% of total portfolio value. Additionally, single stock weight SHALL NOT exceed 10% and single sub-sector SHALL NOT exceed 25%.

#### Scenario: Volatility-based sizing
- **WHEN** portfolio value is 1,000,000, stock ATR is 0.50, stock price is 15.00
- **THEN** max shares = (1,000,000 * 0.02) / (2 * 0.50) = 20,000 shares, position value = 300,000 (30%), capped at 10% = 100,000

#### Scenario: Sub-sector concentration check
- **WHEN** target portfolio has 30% weight in copper sub-sector
- **THEN** system reduces copper stocks to fit within 25% cap

### Requirement: Metal price crash alert
The system SHALL monitor daily metal futures price changes. When any tracked metal drops more than 3% in a single day, the system SHALL generate an alert listing all affected holdings and their estimated impact.

#### Scenario: Copper price crash alert
- **WHEN** SHFE copper drops 4% in one day
- **THEN** system generates alert with all copper-related holdings, their current weight, and estimated portfolio impact
