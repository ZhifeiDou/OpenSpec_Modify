# Tasks: Volatility-Adaptive Risk Controls

## Task 1: Create volatility module
- **File**: `src/risk/volatility.py` (NEW)
- **What**: Implement `compute_volatility_ratio()`, `get_adaptive_atr_multiple()`, `get_rebalance_regime()`
- **Spec reference**: risk-management delta spec → "Volatility regime detection"
- **Dependencies**: DataStore (existing)

## Task 2: Modify stop_loss for adaptive ATR multiple
- **File**: `src/risk/stop_loss.py` (MODIFY)
- **What**: Update `check_hard_stop()` to accept `volatility_ratio` parameter and use `get_adaptive_atr_multiple()` for the ATR multiplier
- **Spec reference**: risk-management delta spec → "Individual stock hard stop-loss (MODIFIED)"
- **Dependencies**: Task 1 (volatility module)

## Task 3: Create circuit breaker module
- **File**: `src/risk/circuit_breaker.py` (NEW)
- **What**: Implement `CircuitBreakerState`, `check_circuit_breaker()`, `check_recovery()`
- **Spec reference**: risk-management delta spec → "Circuit breaker mechanism"
- **Dependencies**: None

## Task 4: Integrate circuit breaker into daily risk check
- **File**: `src/risk/alerts.py` (MODIFY)
- **What**: Update `run_daily_risk_check()` to include circuit breaker state tracking and checks
- **Spec reference**: risk-management delta spec → "Circuit breaker suspends rebalance"
- **Dependencies**: Task 3 (circuit breaker module)

## Task 5: Implement dynamic rebalance in backtest engine
- **File**: `src/backtest/engine.py` (MODIFY)
- **What**:
  1. Add `_is_rebalance_day()` method that uses `get_rebalance_regime()` for dynamic scheduling
  2. Replace static `rebalance_dates` set with per-day dynamic check
  3. Track last rebalance date for interval computation
  4. Pass `volatility_ratio` to `_check_risk()`
- **Spec reference**: backtest-engine delta spec → "Dynamic rebalance scheduling"
- **Dependencies**: Task 1 (volatility module)

## Task 6: Integrate circuit breaker into backtest engine
- **File**: `src/backtest/engine.py` (MODIFY)
- **What**:
  1. Add `CircuitBreakerState` to the daily loop
  2. Compute daily NAV change and check circuit breaker BEFORE rebalance
  3. Generate emergency sell orders when circuit breaker triggers
  4. Skip rebalance when circuit breaker is active
  5. Handle recovery state transitions
  6. Handle T+1 constraint for circuit breaker sells
- **Spec reference**: backtest-engine delta spec → "Daily backtest loop (MODIFIED)"
- **Dependencies**: Task 3 (circuit breaker), Task 5 (dynamic rebalance)

## Task 7: Update configuration
- **File**: `config/settings.yaml` (MODIFY)
- **What**: Add all new configuration parameters for volatility thresholds, adaptive ATR multiples, circuit breaker thresholds, and dynamic rebalance thresholds
- **Spec reference**: design.md → "Configuration"
- **Dependencies**: None

## Task 8: Write tests for volatility module
- **File**: `tests/risk/test_volatility.py` (NEW)
- **What**: Test `compute_volatility_ratio()` with sufficient data, insufficient data, boundary values. Test `get_adaptive_atr_multiple()` for all three regimes plus boundaries.
- **Covers**: UC-1.1 through UC-1.5

## Task 9: Write tests for circuit breaker
- **File**: `tests/risk/test_circuit_breaker.py` (NEW)
- **What**: Test Level 1 trigger, Level 2 trigger, below-threshold, T+1 conflict, recovery (3 and 5 days), recovery interrupted, escalation, rebalance suspension
- **Covers**: UC-3.1 through UC-3.10

## Task 10: Write tests for adaptive stop-loss integration
- **File**: `tests/risk/test_adaptive_stop.py` (NEW)
- **What**: Test that `check_hard_stop()` correctly uses adaptive ATR multiple based on volatility_ratio
- **Covers**: UC-1.1 through UC-1.5
