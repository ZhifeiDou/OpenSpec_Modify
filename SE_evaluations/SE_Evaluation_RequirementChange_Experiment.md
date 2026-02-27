# Software Engineering Quality Evaluation: Requirements Change Experiment

**Date:** 2026-02-25
**Evaluator:** Claude Opus 4.6 (Independent SE Quality Assessment)
**Scope:** Two quantitative trading system projects compared across five SE dimensions in a **requirements change** scenario

---

## Experiment Context

Both projects start from the same baseline quantitative trading system for A-share nonferrous metals. The experiment introduces **three identical requirements changes** and compares how each approach handles them:

1. **Volatility-Adaptive Stop-Loss** -- dynamic ATR multiplier based on market volatility ratio
2. **Dynamic Rebalance Frequency** -- auto-switch between monthly/biweekly/weekly based on volatility
3. **Circuit Breaker Mechanism** -- two-tier emergency portfolio protection (3% and 5% NAV drops)

| Aspect | WITH OpenSpec-HW | WITHOUT OpenSpec |
|--------|-----------------|-----------------|
| **Location** | `with_openspec/` | `without_openspec/` |
| **Approach** | Specification-driven (proposal -> usecases -> design -> specs -> tasks -> code) | Direct coding (requirements -> code) |
| **AI Tool** | Claude + OpenSpec-HW workflow | Claude (native, no framework) |

---

## Project Metrics at a Glance

| Metric | WITH OpenSpec-HW | WITHOUT OpenSpec |
|--------|:----------------:|:----------------:|
| Source files | 40+ (across 8 packages) | 6 (flat modules) |
| Source LOC | ~2,500+ | ~1,370 |
| Test files | 3 new + existing suite | 0 |
| Test cases (new) | 31 | 0 |
| Spec/Design artifacts | 6 documents (~636 lines) | 0 |
| Config format | YAML (92 lines, 19 new params) | Python dict (91 lines, 4 new params) |
| New modules created | 3 (`volatility.py`, `circuit_breaker.py`, updated `stop_loss.py`) | 0 (all changes in `backtester.py`) |
| Files modified | 4 source + config + 3 test files | 2 (`backtester.py` + `config.py`) |
| Boundary cases identified | 10 | 2 |
| Boundary cases missed | 0 | 3 critical |

---

## Dimension 1: Specifications and Requirements

| Project | Score | Rating |
|---------|:-----:|--------|
| WITH OpenSpec-HW | **5 / 5** | Excellent |
| WITHOUT OpenSpec | **1 / 5** | Poor |

### WITH OpenSpec-HW (5/5)

**Complete artifact chain produced before any code was written:**

- **proposal.md** (45 lines): Clear problem statement rooted in real 2024 market events. Explains *why* fixed-parameter risk controls failed. Defines scope with three concrete deliverables. Identifies risks (T+1 settlement conflicts) and mitigations upfront.

- **usecases.md** (160 lines): 10 detailed use cases covering all three requirements. Each use case includes specific numerical scenarios with exact calculations (e.g., "stop price = 15.00 - 1.5 x 0.60 = 14.10"). Covers 8 boundary scenarios including:
  - Exact-boundary volatility ratios (ratio = 0.80, ratio = 1.50)
  - T+1 settlement conflicts during circuit breaker liquidation
  - Mid-month rebalance frequency transitions
  - Circuit breaker recovery interrupted by new drops
  - Escalation from Level 1 to Level 2 during recovery

- **Delta specs** (204 lines across 2 spec files): Formal requirements using scenario-based WHEN/THEN format. Clear definitions of terms (e.g., "up day = current NAV > previous NAV"). Explicit cross-references to use cases.

- **design.md** (164 lines): Architecture diagrams, component design for 5 modules, state machine specification for circuit breaker (4 states, 6 transitions), configuration parameters enumerated.

- **tasks.md** (68 lines): 10 implementation tasks with dependency ordering. Tasks 8-10 explicitly call out which use cases each test must cover.

**Key strength:** The usecases.md phase forced systematic boundary-case thinking *before* implementation. This is why the OpenSpec version identified T+1 conflicts, gradual recovery semantics, and frequency-switching edge cases that the non-OpenSpec version missed entirely.

### WITHOUT OpenSpec (1/5)

- **Zero specification documents** of any kind.
- No proposal explaining why these changes are needed.
- No use cases documenting expected behavior.
- No design document describing how the three features interact.
- No task breakdown for implementation planning.
- The only "requirements" are the external `requirement_change.md` file -- but no project-internal interpretation, refinement, or boundary-case analysis was performed.
- A future developer looking at this project would have to reverse-engineer the *intent* from the *code* -- the most expensive form of knowledge transfer.

---

## Dimension 2: Design

| Project | Score | Rating |
|---------|:-----:|--------|
| WITH OpenSpec-HW | **5 / 5** | Excellent |
| WITHOUT OpenSpec | **1 / 5** | Poor |

### WITH OpenSpec-HW (5/5)

**Architectural decisions documented with rationale:**

- **Separation of concerns**: Volatility ratio computation (`volatility.py`), circuit breaker state machine (`circuit_breaker.py`), and adaptive stop-loss (`stop_loss.py`) are each isolated modules. This means a bug in circuit breaker logic cannot corrupt stop-loss calculations, and each module can be tested independently.

- **State machine design**: The circuit breaker uses a well-defined 4-state model (normal -> level_1 -> level_2 -> recovering -> normal) with explicit transition rules. The `CircuitBreakerState` dataclass cleanly encapsulates state (level, trigger_nav, consecutive_up_days, recovery_target_days).

- **Backward compatibility by design**: The modified `check_hard_stop()` function accepts an *optional* `volatility_ratio` parameter. When `None`, it falls back to the original 2.0x ATR multiplier. Existing callers work without modification.

- **Configuration externalization**: 19 new parameters (volatility windows, ATR multiples per regime, circuit breaker thresholds, recovery days, rebalance frequency thresholds) are all in `settings.yaml`, not hardcoded.

- **Integration architecture**: The `engine.py` backtest loop integrates all three features in a clear daily sequence: (1) compute volatility ratio -> (2) check circuit breaker -> (3) apply position scale -> (4) determine rebalance frequency -> (5) check adaptive stop-loss.

### WITHOUT OpenSpec (1/5)

- **Zero design documents**. No architecture description, no decision records, no component diagrams.
- **Monolithic approach**: All three new features (volatility ratio, dynamic rebalance, circuit breaker) were implemented directly inside `backtester.py`'s `run_backtest()` function. The file grew from 257 to 416 lines (+62%), creating a single function that handles data fetching, factor calculation, signal generation, rebalancing, risk management, and performance metrics.
- **No separation of concerns**: Volatility ratio calculation is embedded in the backtest loop, not extractable for use by other components.
- **No state machine**: Circuit breaker logic uses inline if/elif chains with mutable variables (`circuit_level`, `recovery_counter`, `positions_before_circuit`). The state transitions are implicit and scattered across ~40 lines of nested conditions.
- **Hardcoded thresholds**: Stop-loss percentages (-6%, -8%, -10%), rebalance intervals (5, 10, 20 days), and circuit breaker levels (-3%, -5%) are inline constants in `backtester.py`, not configurable without code changes.
- **Duplicated logic**: The backtester re-implements a simplified momentum calculation that already exists in `factor_engine.py`, indicating no architectural planning was done.

---

## Dimension 3: Implementation

| Project | Score | Rating |
|---------|:-----:|--------|
| WITH OpenSpec-HW | **4 / 5** | Very Good |
| WITHOUT OpenSpec | **2 / 5** | Below Average |

### WITH OpenSpec-HW (4/5)

**Code quality strengths:**

- **Type hints throughout**: All functions use proper type annotations (`def compute_volatility_ratio(date: str, store: DataStore, config: dict) -> float`).
- **Comprehensive docstrings**: Each function documents parameters, return values, and algorithm overview.
- **Structured logging**: Uses `logging.debug()` and `logging.warning()` for operational visibility (e.g., "Circuit breaker LEVEL 1 triggered: daily change -3.2%").
- **Defensive programming**: Guards against division by zero (`median_vol <= 0`), insufficient data (`len(closes) < short_window`), and missing values (`volatility_ratio=None` fallback).
- **Clean dataclass usage**: `CircuitBreakerState` with 6 typed fields; `StopLossAlert` for structured return values.

**Weaknesses identified:**

- Integer division truncation: `shares // 2` for 50% reduction may leave an extra share (101 shares -> 50 sold, not 50.5).
- Missing tests for `compute_volatility_ratio()` function itself (pure function tests exist for `get_adaptive_atr_multiple` and `get_rebalance_regime`, but the main ratio computation is only tested via integration).
- `test_adaptive_stop.py` assertions are too loose: checks `isinstance(alerts, list)` but doesn't verify the actual stop-loss price calculations.
- Potential interaction issue: circuit breaker and existing drawdown control could both reduce positions on the same day (design says drawdown check is skipped during circuit breaker, but engine code at line 359 doesn't enforce this).

### WITHOUT OpenSpec (2/5)

**Code quality strengths:**

- Functional: The code *works* -- all three requirements are implemented and produce results.
- Zero-division protection via `1e-9` guards in multiple places.
- Performance metrics calculation (Sharpe ratio, max drawdown, win rate) is reasonably complete.
- Missing price data handled with fallback to previous close.

**Weaknesses identified:**

- **No type hints** anywhere in the project.
- **No logging framework** -- uses `print()` throughout.
- **Monolithic function**: `run_backtest()` is ~250 lines handling everything from data fetching to metrics calculation.
- **Position tracking bug**: Line 277 stores `"cost": price` (current trade price) instead of weighted average cost, breaking cost-basis tracking for rebalanced positions.
- **Simplified factor calculation**: Lines 214-246 re-implement a stripped-down momentum/MACD scoring that differs from the full `factor_engine.py` multifactor model, producing inconsistent signals.
- **Volatile ratio calculation vulnerability**: Line 316 accesses `all_dates[j+1]` without bounds checking.
- **Stop-loss as percentage, not ATR-based**: Despite the requirement specifying ATR-based stop-loss with volatility-adaptive multipliers, the implementation uses simple percentage thresholds (-6%, -8%, -10%). This is a **requirements deviation** -- the implementation doesn't match the specification.
- **Circuit breaker recovery is simplistic**: 3/5-day counters implemented, but no handling of T+1 settlement conflict (same-day purchases can't be sold), no gradual recovery (jumps straight from reduced to full positions), and no escalation path during recovery.

---

## Dimension 4: Verification and Validation

| Project | Score | Rating |
|---------|:-----:|--------|
| WITH OpenSpec-HW | **4 / 5** | Very Good |
| WITHOUT OpenSpec | **1 / 5** | Poor |

### WITH OpenSpec-HW (4/5)

**Testing infrastructure:**

- **31 new test cases** across 3 dedicated test files:
  - `test_volatility.py` (87 lines, 16 tests): Covers all three volatility regimes, boundary values at exact thresholds (0.80, 1.50), just-above/just-below boundary values, default config behavior.
  - `test_circuit_breaker.py` (142 lines, 14 tests): Tests Level 1 trigger, Level 2 trigger, below-threshold (2.95%), first-day handling, escalation (L1 -> L2), Level 1 recovery (3 up days), interrupted recovery, Level 2 recovery (5 up days), helper functions.
  - `test_adaptive_stop.py` (133 lines, 6 tests): Backward compatibility (no volatility_ratio), low/normal/high volatility scenarios, T+1 constraint.

- **Use case traceability**: Test method names reference specific use cases (e.g., `test_low_vol_multiplier_UC1_1`, `test_level1_trigger_UC3_1`), creating a traceable link from requirements to verification.

- **Boundary value testing**: Exact threshold values tested (0.80 maps to 1.5x ATR, 1.50 maps to 2.0x ATR). Just-below and just-above tested (0.79, 0.81, 1.49, 1.51).

**Gaps:**
- No unit test for `compute_volatility_ratio()` function (the most complex calculation).
- No integration test for the dynamic rebalance frequency feature.
- `test_adaptive_stop.py` assertions only check return type, not actual stop-price values.
- No tests for circuit breaker + drawdown interaction.

### WITHOUT OpenSpec (1/5)

- **Zero tests**. No `tests/` directory, no `test_*.py` files, no `pytest.ini`, no testing infrastructure of any kind.
- No CI/CD configuration.
- No linting or static analysis configuration.
- For a quantitative trading system where numerical correctness directly impacts financial outcomes, the complete absence of verification is a **critical deficiency**.
- The three critical boundary cases missed (T+1 conflict, gradual recovery, frequency switching) would likely have been caught by even basic test design, had any testing been attempted.

---

## Dimension 5: Maintenance and Evolution

| Project | Score | Rating |
|---------|:-----:|--------|
| WITH OpenSpec-HW | **5 / 5** | Excellent |
| WITHOUT OpenSpec | **1 / 5** | Poor |

### WITH OpenSpec-HW (5/5)

**Knowledge preservation for future developers:**

- **Complete change audit trail**: The `openspec/changes/volatility-adaptive-risk/` directory preserves *why* these changes were made (proposal.md), *what behavior* was expected (usecases.md), *how* the architecture was modified (design.md), *what specifications* changed (delta specs), and *what tasks* were done (tasks.md). A new developer joining the team 6 months later can understand the full context without asking anyone.

- **Modular extensibility**: Adding a 4th risk regime (e.g., "extreme" above 3.0x ratio) requires only:
  1. Add a threshold in `settings.yaml`
  2. Add an `elif` branch in `get_adaptive_atr_multiple()` and `get_rebalance_regime()`
  3. Add corresponding tests
  No other files need modification.

- **Isolated impact of future changes**: Because circuit breaker, volatility, and stop-loss are separate modules, a future requirement to "replace the circuit breaker with a VIX-based mechanism" affects only `circuit_breaker.py` and its tests -- no risk of breaking stop-loss or rebalance logic.

- **Configuration-driven tuning**: All 19 new risk parameters are in YAML. A portfolio manager can adjust thresholds (e.g., change L1 from 3% to 4%) without touching code, without requiring a developer, and without risk of introducing bugs.

- **Reproducible change process**: The OpenSpec workflow itself is preserved in `.claude/skills/openspec-*/`. Future requirements changes can follow the same structured process, ensuring consistent quality.

### WITHOUT OpenSpec (1/5)

- **No README** -- no setup instructions, no architecture overview, no usage guide.
- **No design rationale** -- a future developer must reverse-engineer *why* circuit breaker uses 3%/5% thresholds, *why* rebalance intervals are 5/10/20 days, and *why* stop-loss percentages are -6%/-8%/-10%.
- **No specifications** -- no way to distinguish intended behavior from bugs. Is the absence of T+1 handling in the circuit breaker a deliberate design choice or an oversight?
- **No tests** -- any future modification risks silent regression with no detection mechanism.
- **Monolithic coupling**: Adding a 4th risk regime requires modifying `backtester.py` in multiple scattered locations (stop-loss section, rebalance section, volatility section), with high risk of introducing bugs.
- **Hardcoded thresholds**: Changing any risk parameter requires a code change, a commit, and redeployment. No separation between configuration and logic.
- **No change history**: When the next requirements change arrives, there is no record of what was done for *this* change, what boundary cases were considered (or missed), or what design decisions were made.

---

## Summary Comparison

### Score Matrix

| Dimension | WITH OpenSpec-HW | WITHOUT OpenSpec | Gap |
|-----------|:----------------:|:----------------:|:---:|
| 1. Specifications & Requirements | **5** | **1** | +4 |
| 2. Design | **5** | **1** | +4 |
| 3. Implementation | **4** | **2** | +2 |
| 4. Verification & Validation | **4** | **1** | +3 |
| 5. Maintenance & Evolution | **5** | **1** | +4 |
| **Total (out of 25)** | **23** | **6** | **+17** |
| **Average (out of 5.0)** | **4.6** | **1.2** | **+3.4** |

### Visual Comparison

```
Dimension                    WITHOUT OpenSpec    WITH OpenSpec-HW
                             (Score / 5)         (Score / 5)
                             ──────────────      ──────────────
1. Specifications            [#............]  1  [#############]  5
2. Design                    [#............]  1  [#############]  5
3. Implementation            [###..........]  2  [##########...]  4
4. Verification              [#............]  1  [##########...]  4
5. Maintenance               [#............]  1  [#############]  5
                             ──────────────      ──────────────
TOTAL                              6 / 25              23 / 25
```

---

## Key Findings

### 1. The specification phase is the highest-leverage intervention

The OpenSpec-HW project scored 5/5 on specifications because the structured workflow (proposal -> usecases -> design -> specs -> tasks) forces systematic thinking about boundary cases, failure modes, and inter-feature interactions *before* any code is written. The 160-line usecases.md document identified 10 scenarios including 8 boundary cases. The non-OpenSpec project identified only 2 boundary cases and missed 3 critical ones (T+1 settlement conflict, gradual recovery, frequency switching during active circuit breaker).

### 2. Design quality is a direct consequence of specification quality

When requirements are explicit and boundary cases are enumerated, the natural architectural response is modular: separate modules for separate concerns, with clear interfaces. The OpenSpec project created 3 new modules totaling ~480 lines. The non-OpenSpec project added 159 lines to an existing monolithic function. The resulting designs differ not because of developer skill, but because the OpenSpec workflow created the *information* needed for good design decisions.

### 3. Implementation quality shows the smallest gap (4 vs 2)

Both approaches produce functional code. The non-OpenSpec implementation *works* for the common case. The gap is in edge-case handling, code organization, and engineering practices (type hints, logging, defensive programming). This suggests that while specifications and design have the largest impact on quality, they don't fully determine implementation craftsmanship.

### 4. Zero tests correlates perfectly with zero specifications

The non-OpenSpec project has no tests. This is not coincidental -- without explicit behavioral specifications, there is nothing to *test against*. The OpenSpec project's 31 tests are directly traceable to use case scenarios (test methods named after UC-1.1, UC-2.1, etc.). Specifications create the preconditions for meaningful verification.

### 5. The maintenance gap is existential, not incremental

The difference between the two projects is not "one is slightly easier to maintain." The non-OpenSpec project has *zero documentation*, *zero tests*, *zero design rationale*, and *hardcoded configuration*. Any future modification is essentially starting from scratch -- the developer must read and understand all 416 lines of backtester.py before making any change, with no safety net against regression. The OpenSpec project's combination of specs, tests, modular code, and configuration externalization makes future changes *routine* rather than *risky*.

---

## Recommendations

### For the WITHOUT OpenSpec project (Score: 6/25)

If this project were to be brought to production quality:
1. **Immediate**: Extract circuit breaker, volatility ratio, and adaptive stop-loss into separate modules
2. **Immediate**: Add a test suite for the three new features (at minimum, 10-15 tests covering the boundary cases in `requirement_change.md`)
3. **Short-term**: Replace hardcoded thresholds with a configuration file
4. **Short-term**: Fix the position cost-tracking bug (line 277) and factor calculation inconsistency
5. **Medium-term**: Write a README and document the design decisions that were made
6. **Consider**: Adopting OpenSpec or a similar specification workflow for future changes

### For the WITH OpenSpec-HW project (Score: 23/25)

To reach the theoretical maximum:
1. Add unit tests for `compute_volatility_ratio()` (the core calculation function has no direct tests)
2. Add integration tests for the dynamic rebalance frequency feature
3. Strengthen `test_adaptive_stop.py` assertions to verify actual stop-price calculations, not just return types
4. Resolve the potential circuit breaker + drawdown double-reduction interaction
5. Fix integer division truncation in 50% position reduction (`shares // 2`)
