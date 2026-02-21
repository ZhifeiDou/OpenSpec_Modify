# Backtest Engine — Delta Spec (volatility-adaptive-risk)

**Status**: MODIFIED

## Changes Summary

| Section | Change Type | Description |
|---------|------------|-------------|
| Rebalance scheduling | MODIFIED | Dynamic frequency based on volatility regime |
| Daily loop | MODIFIED | Integrate circuit breaker checks and state management |

---

## MODIFIED: Dynamic rebalance scheduling

**Previous**: Fixed rebalance frequency (monthly or weekly) determined at backtest start.

**Updated**: The rebalance frequency SHALL be dynamically determined on each trading day based on the current `volatility_ratio`:

| Volatility Regime | Condition | Rebalance Frequency |
|-------------------|-----------|-------------------|
| Normal | volatility_ratio ≤ 1.5 | Monthly (first trading day of month) |
| High | 1.5 < volatility_ratio ≤ 2.0 | Bi-weekly (every 2 weeks, first trading day) |
| Extreme | volatility_ratio > 2.0 | Weekly (first trading day of week) |

The system SHALL evaluate the volatility_ratio each trading day and determine whether today qualifies as a rebalance day under the current regime.

#### Scenario: Monthly rebalance in normal regime
- **WHEN** volatility_ratio = 1.20 and today is the first trading day of a new month
- **THEN** the system triggers rebalance

#### Scenario: Bi-weekly rebalance in high volatility
- **WHEN** volatility_ratio = 1.80 and today is the first trading day of a new 2-week period
- **THEN** the system triggers rebalance

#### Scenario: Weekly rebalance in extreme volatility
- **WHEN** volatility_ratio = 2.30 and today is the first trading day of the week (Monday or first available)
- **THEN** the system triggers rebalance

#### Scenario: Regime change mid-period
- **WHEN** volatility_ratio changes from 1.2 (monthly) to 1.8 (bi-weekly) on day 10 of the month
- **THEN** the engine immediately uses bi-weekly logic
- **AND** the next bi-weekly boundary triggers a rebalance

---

## MODIFIED: Daily backtest loop

**Previous**: The daily loop was: update prices → risk checks → execute orders → rebalance (if scheduled) → record NAV.

**Updated**: The daily loop SHALL now include circuit breaker state management:

1. Update market prices
2. Compute daily NAV change
3. **Check circuit breaker** (before other risk checks):
   - If circuit breaker triggers: generate emergency sell orders, update state
   - If circuit breaker is active: check recovery conditions
   - If circuit breaker is active: skip rebalance
4. Check individual stock stop-loss (with volatility-adaptive multiplier)
5. Execute pending orders (respecting T+1)
6. If no circuit breaker active AND today is rebalance day: run rebalance
7. Record NAV

#### Scenario: Circuit breaker fires before rebalance
- **WHEN** the daily NAV drop exceeds 3% and today is also a rebalance day
- **THEN** the circuit breaker fires first, generates sell orders, and the rebalance is skipped

#### Scenario: Normal day with adaptive stop-loss
- **WHEN** the circuit breaker is not active
- **THEN** the daily loop runs as before, except stop-loss uses the volatility-adaptive ATR multiple

#### Scenario: Recovery day
- **WHEN** circuit breaker is in "level_1" state and NAV increases
- **THEN** the consecutive up-day counter increments
- **AND** if counter reaches 3, state resets to "normal"
