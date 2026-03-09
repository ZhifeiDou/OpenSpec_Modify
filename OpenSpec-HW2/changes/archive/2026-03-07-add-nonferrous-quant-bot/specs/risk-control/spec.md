## ADDED Requirements

### Requirement: ATR hard stop loss
The system SHALL flag any position whose unrealized loss from entry price exceeds `hard_stop_atr_multiple` times the 20-day ATR (Average True Range). Flagged positions SHALL be marked as "liquidate immediately".

#### Scenario: Hard stop triggered
- **WHEN** a stock was entered at 20.00, current price is 17.00 (loss = 3.00), and 20-day ATR is 1.20 with `hard_stop_atr_multiple = 2.0`
- **THEN** loss (3.00) > 2.0 * ATR (2.40), so position is flagged for immediate liquidation

#### Scenario: Hard stop not triggered
- **WHEN** a stock was entered at 20.00, current price is 19.00 (loss = 1.00), and 20-day ATR is 1.20
- **THEN** loss (1.00) < 2.0 * ATR (2.40), so position is not flagged

### Requirement: Trailing stop
The system SHALL track the highest price since entry for each position. When a position's gain from entry exceeds `trailing_stop_activation` (e.g., 10%), the trailing stop activates. Once active, if the price drops `trailing_stop_drop` (e.g., 8%) from the peak, the position SHALL be flagged for exit.

#### Scenario: Trailing stop activation and trigger
- **WHEN** entry price is 10.00, peak price reached 11.50 (15% gain, exceeds 10% activation), current price drops to 10.58 (8% drop from 11.50 peak)
- **THEN** trailing stop triggers and position is flagged for exit

#### Scenario: Trailing stop not yet activated
- **WHEN** entry price is 10.00 and peak price is 10.80 (8% gain, below 10% activation)
- **THEN** trailing stop is not active regardless of current price

### Requirement: Portfolio max drawdown control
The system SHALL monitor the portfolio's drawdown from its peak NAV. When drawdown exceeds `max_drawdown_reduce` (e.g., 15%), the system SHALL recommend reducing position sizes by 50%. When drawdown exceeds `max_drawdown_liquidate` (e.g., 20%), the system SHALL recommend full liquidation.

#### Scenario: Drawdown reduce threshold
- **WHEN** portfolio peak NAV is 1,200,000 and current NAV is 1,010,000 (drawdown = 15.8%)
- **THEN** system recommends reducing all positions by 50%

#### Scenario: Drawdown liquidate threshold
- **WHEN** portfolio peak NAV is 1,200,000 and current NAV is 950,000 (drawdown = 20.8%)
- **THEN** system recommends full liquidation of all positions

### Requirement: Metal crash circuit breaker
The system SHALL detect a "metal crash" condition when the non-ferrous metals sector index drops more than `metal_crash_threshold` (e.g., 3%) in a single day. During a crash, the system SHALL recommend halting all new buy orders.

#### Scenario: Metal crash detected
- **WHEN** the non-ferrous metals sector index drops 4% in one day and `metal_crash_threshold = 0.03`
- **THEN** system flags "metal crash" and recommends no new buys

#### Scenario: Normal market decline
- **WHEN** the sector index drops 2% in one day
- **THEN** metal crash is NOT triggered

### Requirement: Risk report output
The system SHALL output a risk check report containing: per-position status (symbol, entry_price, current_price, pnl_pct, stop_status), portfolio-level metrics (current_drawdown, peak_nav, current_nav), and any triggered alerts.

#### Scenario: Risk report format
- **WHEN** risk check completes for a portfolio of 8 positions
- **THEN** system displays a table with per-position risk status and a summary section with portfolio-level metrics
