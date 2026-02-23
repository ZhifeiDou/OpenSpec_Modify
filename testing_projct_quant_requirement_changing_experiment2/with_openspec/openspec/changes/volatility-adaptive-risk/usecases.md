# Use Cases: Volatility-Adaptive Risk Controls

## UC-1: Volatility-Adaptive Stop-Loss

### UC-1.1: Low volatility tightens stop-loss
- **GIVEN** the portfolio holds stock "601899" bought at 15.00
- **AND** the 20-day volatility is 0.015 (daily std of returns)
- **AND** the 120-day median volatility is 0.025
- **AND** volatility_ratio = 0.015 / 0.025 = 0.60 (< 0.8, low volatility)
- **AND** 14-day ATR is 0.60
- **WHEN** the system evaluates stop-loss on the current trading day
- **THEN** the stop-loss multiple is set to 1.5x ATR
- **AND** the stop price = 15.00 - 1.5 × 0.60 = 14.10
- **AND** if current price ≤ 14.10, the hard stop-loss triggers

### UC-1.2: High volatility widens stop-loss
- **GIVEN** the portfolio holds stock "600362" bought at 20.00
- **AND** volatility_ratio = 1.80 (> 1.5, high volatility)
- **AND** 14-day ATR is 1.20
- **WHEN** the system evaluates stop-loss
- **THEN** the stop-loss multiple is set to 2.5x ATR
- **AND** the stop price = 20.00 - 2.5 × 1.20 = 17.00

### UC-1.3: Normal volatility keeps default
- **GIVEN** volatility_ratio = 1.10 (0.8 ≤ ratio ≤ 1.5)
- **WHEN** the system evaluates stop-loss
- **THEN** the stop-loss multiple remains 2.0x ATR (no change)

### UC-1.4: Insufficient historical data fallback
- **GIVEN** a stock has only 15 trading days of history (< 20 required)
- **WHEN** the system attempts to compute volatility_ratio
- **THEN** the system falls back to the default fixed ATR multiple (2.0x)
- **AND** logs a warning about insufficient data

### UC-1.5: Volatility ratio boundary values
- **GIVEN** volatility_ratio = 0.80 exactly
- **WHEN** the system evaluates stop-loss
- **THEN** the stop-loss multiple is 2.0x ATR (normal range, inclusive lower bound)

- **GIVEN** volatility_ratio = 1.50 exactly
- **WHEN** the system evaluates stop-loss
- **THEN** the stop-loss multiple is 2.0x ATR (normal range, inclusive upper bound)

---

## UC-2: Dynamic Rebalance Frequency

### UC-2.1: Normal volatility keeps monthly rebalance
- **GIVEN** the current volatility_ratio is 1.20 (≤ 1.5)
- **WHEN** the backtest engine determines the next rebalance date
- **THEN** the next rebalance occurs on the first trading day of the next month

### UC-2.2: High volatility switches to bi-weekly
- **GIVEN** the current volatility_ratio is 1.80 (1.5 < ratio ≤ 2.0)
- **AND** the last rebalance was 10 trading days ago
- **WHEN** the engine checks if today is a rebalance day
- **THEN** the engine uses bi-weekly frequency (approximately every 10 trading days)
- **AND** today qualifies as a rebalance day

### UC-2.3: Extreme volatility switches to weekly
- **GIVEN** the current volatility_ratio is 2.30 (> 2.0)
- **WHEN** the engine determines the rebalance schedule
- **THEN** the engine uses weekly frequency (first trading day of each week)

### UC-2.4: Frequency changes mid-month
- **GIVEN** volatility_ratio was 1.0 at last rebalance (monthly mode)
- **AND** 8 trading days have passed since last rebalance
- **AND** today's volatility_ratio jumps to 1.80 (bi-weekly mode)
- **WHEN** the engine evaluates today
- **THEN** the engine immediately switches to bi-weekly frequency
- **AND** since 8 days > half a bi-weekly period, the next rebalance could be soon

### UC-2.5: Frequency decreases (high → normal)
- **GIVEN** volatility_ratio drops from 1.80 to 1.20
- **WHEN** the engine updates the rebalance schedule
- **THEN** the engine reverts to monthly frequency
- **AND** the next rebalance is the first trading day of the next month

---

## UC-3: Circuit Breaker Mechanism

### UC-3.1: Level 1 circuit breaker — 3% daily drop
- **GIVEN** yesterday's portfolio NAV was 1,000,000
- **AND** today's portfolio NAV is 965,000 (daily drop = 3.5%)
- **WHEN** the daily risk check runs at end of day
- **THEN** the system triggers Level 1 circuit breaker
- **AND** generates sell orders for 50% of each position's shares
- **AND** sets circuit breaker state to "level_1"
- **AND** records the circuit breaker trigger date and NAV

### UC-3.2: Level 2 circuit breaker — 5% daily drop
- **GIVEN** yesterday's NAV was 1,000,000
- **AND** today's NAV is 940,000 (daily drop = 6.0%)
- **WHEN** the daily risk check runs
- **THEN** the system triggers Level 2 circuit breaker
- **AND** generates sell orders for ALL positions
- **AND** sets circuit breaker state to "level_2"

### UC-3.3: Circuit breaker + T+1 conflict
- **GIVEN** Level 1 circuit breaker triggers today
- **AND** stocks A, B, C are held
- **AND** stock C was bought today (T+0)
- **WHEN** the system generates 50% reduction orders
- **THEN** stocks A and B are immediately sold (50% each)
- **AND** stock C's sell order is deferred to tomorrow (T+1)
- **AND** the system logs "T+1 constraint: stock C sell deferred to next trading day"

### UC-3.4: Level 1 recovery — 3 consecutive up days
- **GIVEN** Level 1 circuit breaker was triggered on Day 0 with NAV = 970,000
- **AND** after position reduction, NAV stabilized at 960,000 (circuit breaker NAV)
- **AND** Day 1 NAV = 962,000 (up from 960,000) ✓
- **AND** Day 2 NAV = 965,000 (up from 962,000) ✓
- **AND** Day 3 NAV = 968,000 (up from 965,000) ✓
- **WHEN** the system checks recovery conditions at end of Day 3
- **THEN** the circuit breaker state is reset to "normal"
- **AND** the next rebalance will restore positions to full allocation

### UC-3.5: Recovery interrupted — not 3 consecutive days
- **GIVEN** Level 1 circuit breaker active
- **AND** Day 1 NAV is up ✓
- **AND** Day 2 NAV is down ✗
- **WHEN** the system checks recovery
- **THEN** the consecutive up-day counter resets to 0
- **AND** the circuit breaker remains active

### UC-3.6: Escalation from Level 1 to Level 2
- **GIVEN** Level 1 circuit breaker is active (positions at 50%)
- **AND** today's NAV drops > 5% from yesterday
- **WHEN** the daily risk check runs
- **THEN** the system escalates to Level 2 (full liquidation)
- **AND** all remaining positions are sold

### UC-3.7: Circuit breaker suspends rebalance
- **GIVEN** the circuit breaker is in "level_1" state
- **AND** today is a scheduled rebalance day
- **WHEN** the engine checks whether to run rebalance
- **THEN** the rebalance is skipped
- **AND** the system logs "Rebalance skipped: circuit breaker active"

### UC-3.8: Level 2 recovery — 5 consecutive up days with gradual restore
- **GIVEN** Level 2 circuit breaker was triggered (all positions liquidated)
- **AND** 5 consecutive trading days of NAV increase have passed
- **WHEN** the system recovers
- **THEN** the circuit breaker state changes to "recovering"
- **AND** the next rebalance allocates to 50% of normal position sizes
- **AND** the subsequent rebalance (if still in recovery) restores to 100%

### UC-3.9: Circuit breaker trigger on day 1 (no previous NAV)
- **GIVEN** backtest is on the first trading day (no previous NAV)
- **WHEN** the circuit breaker check runs
- **THEN** the check is skipped (no previous NAV to compare)
- **AND** no circuit breaker is triggered

### UC-3.10: NAV calculation precision
- **GIVEN** yesterday's NAV was 1,000,000
- **AND** today's NAV is 970,500 (drop = 2.95%)
- **WHEN** the system checks circuit breaker
- **THEN** NO circuit breaker triggers (2.95% < 3% threshold)
