# Design: Volatility-Adaptive Risk Controls

## Architecture Overview

The changes introduce a new `volatility` module and modify three existing modules. The key design principle is **separation of concerns**: volatility detection is a shared utility, each risk feature (adaptive stop-loss, circuit breaker) is in its own module, and the backtest engine orchestrates them.

```
src/risk/
├── volatility.py     # NEW: volatility ratio computation
├── stop_loss.py      # MODIFIED: adaptive ATR multiple
├── drawdown.py       # (unchanged)
├── circuit_breaker.py # NEW: circuit breaker state machine
├── alerts.py         # MODIFIED: integrate circuit breaker in daily check
└── position_sizer.py # (unchanged)

src/backtest/
├── engine.py         # MODIFIED: dynamic rebalance + circuit breaker integration
└── ...

config/
└── settings.yaml     # MODIFIED: new config parameters

tests/risk/
├── test_risk.py          # EXISTING
├── test_volatility.py    # NEW
├── test_circuit_breaker.py # NEW
└── test_adaptive_stop.py # NEW
```

## Component Design

### 1. Volatility Module (`src/risk/volatility.py`) — NEW

```python
def compute_volatility_ratio(
    store: DataStore,
    date: str,
    short_window: int = 20,
    long_window: int = 120,
) -> float:
    """Compute volatility ratio using portfolio/index returns.

    Returns 1.0 (normal) if insufficient data.
    """

def get_adaptive_atr_multiple(volatility_ratio: float, config: dict) -> float:
    """Map volatility ratio to ATR multiple.

    Low (< 0.8) → 1.5x
    Normal (0.8 - 1.5) → 2.0x
    High (> 1.5) → 2.5x
    """

def get_rebalance_regime(volatility_ratio: float) -> str:
    """Map volatility ratio to rebalance frequency.

    Returns: "monthly", "biweekly", or "weekly"
    """
```

**Data source**: Uses the stock_daily table aggregate or a representative market index to compute daily returns.

### 2. Adaptive Stop-Loss (`src/risk/stop_loss.py`) — MODIFIED

Changes to `check_hard_stop()`:
- Accept an optional `volatility_ratio` parameter
- Call `get_adaptive_atr_multiple()` to determine the ATR multiplier
- Default behavior unchanged when `volatility_ratio` is not provided

**Backward compatibility**: The function signature is extended with a default parameter, so existing callers continue to work.

### 3. Circuit Breaker (`src/risk/circuit_breaker.py`) — NEW

```python
@dataclass
class CircuitBreakerState:
    status: str  # "normal", "level_1", "level_2", "recovering"
    trigger_date: str | None
    trigger_nav: float | None
    consecutive_up_days: int
    recovery_target_days: int  # 3 for level_1, 5 for level_2

def check_circuit_breaker(
    current_nav: float,
    previous_nav: float,
    state: CircuitBreakerState,
    config: dict,
) -> tuple[CircuitBreakerState, list[str]]:
    """Check circuit breaker conditions.

    Returns updated state and list of actions:
    - "reduce_50" — sell 50% of all positions
    - "liquidate" — sell all positions
    - "recovered" — circuit breaker lifted
    - empty list — no action
    """

def check_recovery(
    current_nav: float,
    previous_nav: float,
    state: CircuitBreakerState,
) -> CircuitBreakerState:
    """Check if recovery conditions are met."""
```

**State machine**:
```
normal → level_1 (drop > 3%)
normal → level_2 (drop > 5%)
level_1 → level_2 (drop > 5%)
level_1 → normal (3 consecutive up days)
level_2 → recovering (5 consecutive up days)
recovering → normal (after next rebalance at 100%)
```

### 4. Backtest Engine (`src/backtest/engine.py`) — MODIFIED

Key changes to `BacktestEngine.run()`:
1. Add `CircuitBreakerState` tracking variable
2. Compute `volatility_ratio` each day using `compute_volatility_ratio()`
3. Pass `volatility_ratio` to `check_hard_stop()`
4. Replace static `_get_rebalance_dates()` with dynamic per-day check `_is_rebalance_day()`
5. Add circuit breaker check after NAV computation, before rebalance

Changes to `_check_risk()`:
- Accept `volatility_ratio` parameter
- Pass it to `check_hard_stop()`

New method `_is_rebalance_day()`:
- Accept current date and volatility_ratio
- Determine if today is a rebalance day based on current regime
- Track last rebalance date to compute intervals

### 5. Configuration (`config/settings.yaml`) — MODIFIED

New parameters under `risk:`:
```yaml
risk:
  # ... existing params ...
  # Volatility-adaptive stop-loss
  volatility_short_window: 20
  volatility_long_window: 120
  atr_multiple_low_vol: 1.5
  atr_multiple_normal_vol: 2.0
  atr_multiple_high_vol: 2.5
  volatility_low_threshold: 0.8
  volatility_high_threshold: 1.5
  # Circuit breaker
  circuit_breaker_level1_threshold: 0.03
  circuit_breaker_level2_threshold: 0.05
  circuit_breaker_level1_recovery_days: 3
  circuit_breaker_level2_recovery_days: 5
  # Dynamic rebalance
  volatility_biweekly_threshold: 1.5
  volatility_weekly_threshold: 2.0
```

## Edge Cases and Design Decisions

1. **Volatility ratio on day 1**: Return 1.0 (normal) — no adaptive behavior until sufficient data
2. **Circuit breaker + T+1**: The engine already tracks `buy_date` per holding; circuit breaker uses the same mechanism to defer sells for T+0 purchases
3. **Circuit breaker + existing drawdown control**: Circuit breaker fires BEFORE the existing drawdown check. If circuit breaker is active, the old drawdown check is skipped to avoid conflicting signals
4. **Rebalance date stability**: When volatility regime changes, the engine doesn't retroactively add/remove past rebalance dates; it only affects future dates from the point of detection
