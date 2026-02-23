# Risk Management — Delta Spec (volatility-adaptive-risk)

**Status**: MODIFIED

## Changes Summary

| Section | Change Type | Description |
|---------|------------|-------------|
| Volatility regime detection | ADDED | New shared utility to compute volatility_ratio |
| Hard stop-loss | MODIFIED | ATR multiple now varies by volatility regime |
| Circuit breaker mechanism | ADDED | New portfolio-level emergency risk control |

---

## ADDED: Volatility regime detection

### Requirement: Compute volatility ratio
The system SHALL compute a `volatility_ratio` for the overall market as follows:
1. Compute the standard deviation of daily returns over the most recent 20 trading days (`vol_20d`)
2. Compute the rolling 20-day standard deviation over the past 120 trading days and take its **median** (`vol_120d_median`)
3. `volatility_ratio = vol_20d / vol_120d_median`

The volatility ratio SHALL be computed using a representative stock from the portfolio or the portfolio's aggregate daily returns. It SHALL use closing prices only.

#### Scenario: Sufficient data
- **WHEN** at least 120 trading days of history are available
- **THEN** the system computes volatility_ratio normally

#### Scenario: Insufficient history (< 120 days but ≥ 20 days)
- **WHEN** only 60 trading days of history are available
- **THEN** the system uses the available data to compute vol_120d_median (using 60 days instead of 120)

#### Scenario: Insufficient history (< 20 days)
- **WHEN** fewer than 20 trading days are available
- **THEN** the system returns `volatility_ratio = 1.0` (normal) and logs a warning

---

## MODIFIED: Individual stock hard stop-loss

**Previous**: Fixed 2x ATR hard stop-loss.

**Updated**: The ATR multiple for hard stop-loss SHALL vary based on the current volatility regime:

| Volatility Regime | Condition | ATR Multiple |
|-------------------|-----------|-------------|
| Low volatility | volatility_ratio < 0.8 | 1.5x |
| Normal volatility | 0.8 ≤ volatility_ratio ≤ 1.5 | 2.0x |
| High volatility | volatility_ratio > 1.5 | 2.5x |

The system SHALL compute the volatility_ratio at the start of each trading day and apply the corresponding ATR multiple when evaluating hard stop-loss for all positions.

#### Scenario: Low volatility tightens stop
- **WHEN** volatility_ratio = 0.60 and stock entry price is 15.00 with ATR = 0.60
- **THEN** stop price = 15.00 - 1.5 × 0.60 = 14.10

#### Scenario: High volatility widens stop
- **WHEN** volatility_ratio = 1.80 and stock entry price is 20.00 with ATR = 1.20
- **THEN** stop price = 20.00 - 2.5 × 1.20 = 17.00

#### Scenario: Fallback when data insufficient
- **WHEN** volatility_ratio cannot be computed (< 20 days data)
- **THEN** system uses default 2.0x ATR multiple

---

## ADDED: Circuit breaker mechanism

### Requirement: Portfolio circuit breaker
The system SHALL implement a portfolio-level circuit breaker that monitors daily NAV changes and triggers automatic position reduction in extreme scenarios.

**Trigger Rules:**

| Condition | Action | State |
|-----------|--------|-------|
| Daily NAV drop > 3% | Sell 50% of all positions | level_1 |
| Daily NAV drop > 5% | Sell 100% of all positions | level_2 |

**Daily NAV change** = (current_day_NAV - previous_day_NAV) / previous_day_NAV

#### Scenario: Level 1 trigger
- **WHEN** daily NAV change = -3.5%
- **THEN** system enters "level_1" state and generates sell orders for 50% of each position

#### Scenario: Level 2 trigger
- **WHEN** daily NAV change = -6.0%
- **THEN** system enters "level_2" state and generates sell orders for all positions

#### Scenario: Below threshold
- **WHEN** daily NAV change = -2.9%
- **THEN** no circuit breaker triggers

### Requirement: Circuit breaker T+1 handling
When the circuit breaker triggers, positions purchased on the same day (T+0) SHALL NOT be sold immediately. The system SHALL defer these sells to the next trading day (T+1). Positions purchased on prior days SHALL be sold immediately.

#### Scenario: Mixed T+0 and T+1 positions
- **WHEN** circuit breaker triggers and positions A (bought yesterday) and B (bought today) are held
- **THEN** A is sold immediately; B's sell is deferred to tomorrow

### Requirement: Circuit breaker recovery
The system SHALL require consecutive trading days of NAV improvement before restoring normal position levels:

| State | Recovery Requirement | Recovery Behavior |
|-------|---------------------|-------------------|
| level_1 | 3 consecutive up days | Reset to "normal", next rebalance uses full allocation |
| level_2 | 5 consecutive up days | Reset to "recovering", next rebalance uses 50% allocation, then 100% |

An "up day" is defined as: current_day_NAV > previous_day_NAV.

#### Scenario: Successful Level 1 recovery
- **WHEN** circuit breaker is "level_1" and 3 consecutive up days occur
- **THEN** state resets to "normal"

#### Scenario: Recovery interrupted
- **WHEN** circuit breaker is "level_1", 2 up days occurred, then a down day
- **THEN** consecutive up-day counter resets to 0, circuit breaker remains active

#### Scenario: Escalation from Level 1 to Level 2
- **WHEN** circuit breaker is "level_1" and daily NAV drops > 5%
- **THEN** state escalates to "level_2" and all remaining positions are liquidated

### Requirement: Circuit breaker suspends rebalance
The system SHALL NOT execute scheduled rebalances while the circuit breaker is in "level_1" or "level_2" state. Rebalancing resumes when the circuit breaker state returns to "normal" or "recovering".

#### Scenario: Rebalance day during circuit breaker
- **WHEN** today is a scheduled rebalance day and circuit breaker is "level_1"
- **THEN** the rebalance is skipped
