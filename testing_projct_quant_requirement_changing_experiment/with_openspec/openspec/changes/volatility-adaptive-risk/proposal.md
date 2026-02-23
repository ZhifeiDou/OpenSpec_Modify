# Proposal: Volatility-Adaptive Risk Controls

## Problem Statement

During the 2024 nonferrous metals market turbulence (e.g., copper price surge and crash in Q2), the system's fixed-parameter risk controls proved too slow to react. Key issues:

1. **Fixed stop-loss lagged**: The 2x ATR hard stop triggered only after significant drawdown, failing to protect capital during rapid price declines
2. **Fixed monthly rebalance too infrequent**: In high-volatility regimes, a month between rebalances left the portfolio overexposed to deteriorating positions
3. **No portfolio-level circuit breaker**: When the entire portfolio suffered a single-day crash, there was no automatic mechanism to reduce risk exposure

## Proposed Solution

Introduce a **volatility regime detection** mechanism using a 20-day/120-day volatility ratio, and use this ratio to dynamically adjust three risk parameters:

### Change 1: Volatility-Adaptive Stop-Loss
- Compute `volatility_ratio = std(returns, 20d) / median(std(returns, 120d))`
- Low volatility (ratio < 0.8): Tighten to 1.5x ATR
- Normal volatility (0.8 ≤ ratio ≤ 1.5): Keep 2.0x ATR (unchanged)
- High volatility (ratio > 1.5): Widen to 2.5x ATR

### Change 2: Dynamic Rebalance Frequency
- Normal volatility (ratio ≤ 1.5): Monthly (unchanged)
- High volatility (1.5 < ratio ≤ 2.0): Bi-weekly
- Extreme volatility (ratio > 2.0): Weekly

### Change 3: Circuit Breaker Mechanism (NEW)
- Level 1: Portfolio NAV drops > 3% in a single day → Reduce all positions by 50%
- Level 2: Portfolio NAV drops > 5% in a single day → Full liquidation
- Recovery: Requires 3 consecutive days (Level 1) or 5 consecutive days (Level 2) of NAV improvement before resuming normal operations

## Affected Specs

| Spec | Impact | Reason |
|------|--------|--------|
| risk-management | MODIFIED | Stop-loss adaptive logic, circuit breaker rules |
| backtest-engine | MODIFIED | Dynamic rebalance scheduling, circuit breaker integration in daily loop |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Circuit breaker + T+1 conflict | Defer execution to T+1 for same-day purchases; clearly documented in usecases |
| Volatility ratio undefined with insufficient data | Fallback to fixed parameters when < 20 days of data |
| Frequent regime switching causes whipsawing | Use daily close data only; minimum interval between frequency changes |
