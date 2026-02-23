"""Circuit breaker: portfolio-level emergency risk control for extreme market events."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CircuitBreakerState:
    """Tracks the current circuit breaker status and recovery progress."""
    status: str = "normal"  # "normal", "level_1", "level_2", "recovering"
    trigger_date: str | None = None
    trigger_nav: float | None = None
    consecutive_up_days: int = 0
    recovery_target_days: int = 0
    previous_nav: float | None = None  # Track for daily change calculation


def check_circuit_breaker(
    current_nav: float,
    previous_nav: float | None,
    state: CircuitBreakerState,
    config: dict,
) -> tuple[CircuitBreakerState, list[str]]:
    """Check circuit breaker conditions and return actions.

    Args:
        current_nav: Today's portfolio NAV.
        previous_nav: Yesterday's portfolio NAV (None on first day).
        state: Current circuit breaker state.
        config: Settings dict.

    Returns:
        (updated_state, actions) where actions is a list of:
        - "reduce_50": sell 50% of all positions
        - "liquidate": sell 100% of all positions
        - "recovered": circuit breaker lifted
        - []: no action needed
    """
    risk_cfg = config.get("risk", {})
    level1_threshold = risk_cfg.get("circuit_breaker_level1_threshold", 0.03)
    level2_threshold = risk_cfg.get("circuit_breaker_level2_threshold", 0.05)
    level1_recovery = risk_cfg.get("circuit_breaker_level1_recovery_days", 3)
    level2_recovery = risk_cfg.get("circuit_breaker_level2_recovery_days", 5)

    actions = []

    # Cannot evaluate without previous NAV
    if previous_nav is None or previous_nav <= 0:
        state.previous_nav = current_nav
        return state, actions

    daily_change = (current_nav - previous_nav) / previous_nav

    # If circuit breaker is already active, check recovery first
    if state.status in ("level_1", "level_2", "recovering"):
        # Check for escalation (level_1 → level_2)
        if state.status == "level_1" and daily_change < -level2_threshold:
            state.status = "level_2"
            state.trigger_nav = current_nav
            state.consecutive_up_days = 0
            state.recovery_target_days = level2_recovery
            actions.append("liquidate")
            logger.warning(
                "Circuit breaker ESCALATED to Level 2: daily change %.2f%%",
                daily_change * 100,
            )
        else:
            # Check recovery: is today an up day?
            state, recovery_actions = check_recovery(current_nav, previous_nav, state)
            actions.extend(recovery_actions)

        state.previous_nav = current_nav
        return state, actions

    # Normal state: check for new triggers
    if daily_change < -level2_threshold:
        # Level 2: full liquidation
        state.status = "level_2"
        state.trigger_date = None  # Will be set by caller with actual date
        state.trigger_nav = current_nav
        state.consecutive_up_days = 0
        state.recovery_target_days = level2_recovery
        actions.append("liquidate")
        logger.warning(
            "Circuit breaker TRIGGERED Level 2: daily change %.2f%%, NAV %.2f",
            daily_change * 100, current_nav,
        )
    elif daily_change < -level1_threshold:
        # Level 1: reduce 50%
        state.status = "level_1"
        state.trigger_date = None
        state.trigger_nav = current_nav
        state.consecutive_up_days = 0
        state.recovery_target_days = level1_recovery
        actions.append("reduce_50")
        logger.warning(
            "Circuit breaker TRIGGERED Level 1: daily change %.2f%%, NAV %.2f",
            daily_change * 100, current_nav,
        )

    state.previous_nav = current_nav
    return state, actions


def check_recovery(
    current_nav: float,
    previous_nav: float,
    state: CircuitBreakerState,
) -> tuple[CircuitBreakerState, list[str]]:
    """Check if circuit breaker recovery conditions are met.

    An "up day" = current_nav > previous_nav.

    Returns:
        (updated_state, actions)
    """
    actions = []

    if current_nav > previous_nav:
        state.consecutive_up_days += 1
        logger.info(
            "Circuit breaker recovery: %d/%d consecutive up days",
            state.consecutive_up_days, state.recovery_target_days,
        )
    else:
        state.consecutive_up_days = 0
        logger.debug("Circuit breaker recovery reset: NAV did not increase")

    if state.consecutive_up_days >= state.recovery_target_days:
        if state.status == "level_1":
            state.status = "normal"
            state.consecutive_up_days = 0
            state.trigger_date = None
            state.trigger_nav = None
            actions.append("recovered")
            logger.info("Circuit breaker Level 1 RECOVERED: returning to normal")
        elif state.status == "level_2":
            state.status = "recovering"
            state.consecutive_up_days = 0
            actions.append("recovered")
            logger.info("Circuit breaker Level 2 RECOVERED: entering recovery mode (50%% allocation)")
        elif state.status == "recovering":
            state.status = "normal"
            state.consecutive_up_days = 0
            state.trigger_date = None
            state.trigger_nav = None
            actions.append("recovered")
            logger.info("Circuit breaker fully RECOVERED: returning to normal")

    return state, actions


def is_circuit_breaker_active(state: CircuitBreakerState) -> bool:
    """Check if circuit breaker is currently restricting trading."""
    return state.status in ("level_1", "level_2", "recovering")


def get_position_scale(state: CircuitBreakerState) -> float:
    """Get the position scaling factor based on circuit breaker state.

    Returns:
        1.0 for normal, 0.5 for level_1/recovering, 0.0 for level_2.
    """
    if state.status == "normal":
        return 1.0
    elif state.status in ("level_1", "recovering"):
        return 0.5
    elif state.status == "level_2":
        return 0.0
    return 1.0
