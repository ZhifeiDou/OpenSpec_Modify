"""Tests for circuit breaker mechanism."""
import pytest

from src.risk.circuit_breaker import (
    CircuitBreakerState,
    check_circuit_breaker,
    check_recovery,
    is_circuit_breaker_active,
    get_position_scale,
)


def _default_config():
    return {
        "risk": {
            "circuit_breaker_level1_threshold": 0.03,
            "circuit_breaker_level2_threshold": 0.05,
            "circuit_breaker_level1_recovery_days": 3,
            "circuit_breaker_level2_recovery_days": 5,
        }
    }


class TestCircuitBreakerTrigger:
    """Test circuit breaker trigger conditions."""

    def test_level1_trigger_3pct_drop(self):
        """UC-3.1: 3.5% daily drop triggers Level 1."""
        state = CircuitBreakerState()
        config = _default_config()
        new_state, actions = check_circuit_breaker(965_000, 1_000_000, state, config)
        assert new_state.status == "level_1"
        assert "reduce_50" in actions

    def test_level2_trigger_5pct_drop(self):
        """UC-3.2: 6% daily drop triggers Level 2."""
        state = CircuitBreakerState()
        config = _default_config()
        new_state, actions = check_circuit_breaker(940_000, 1_000_000, state, config)
        assert new_state.status == "level_2"
        assert "liquidate" in actions

    def test_no_trigger_below_threshold(self):
        """UC-3.10: 2.95% drop does NOT trigger."""
        state = CircuitBreakerState()
        config = _default_config()
        new_state, actions = check_circuit_breaker(970_500, 1_000_000, state, config)
        assert new_state.status == "normal"
        assert actions == []

    def test_no_trigger_on_first_day(self):
        """UC-3.9: No previous NAV → no trigger."""
        state = CircuitBreakerState()
        config = _default_config()
        new_state, actions = check_circuit_breaker(1_000_000, None, state, config)
        assert new_state.status == "normal"
        assert actions == []

    def test_escalation_level1_to_level2(self):
        """UC-3.6: Level 1 active, next day drops > 5% → escalate to Level 2."""
        state = CircuitBreakerState(status="level_1", trigger_nav=970_000)
        config = _default_config()
        # 6% drop from 970_000
        new_state, actions = check_circuit_breaker(911_800, 970_000, state, config)
        assert new_state.status == "level_2"
        assert "liquidate" in actions


class TestCircuitBreakerRecovery:
    """Test circuit breaker recovery conditions."""

    def test_level1_recovery_3_up_days(self):
        """UC-3.4: 3 consecutive up days → Level 1 recovered."""
        state = CircuitBreakerState(
            status="level_1", trigger_nav=960_000,
            recovery_target_days=3, consecutive_up_days=0,
        )
        config = _default_config()

        # Day 1: up
        state, actions = check_circuit_breaker(962_000, 960_000, state, config)
        assert state.status == "level_1"
        assert state.consecutive_up_days == 1

        # Day 2: up
        state, actions = check_circuit_breaker(965_000, 962_000, state, config)
        assert state.status == "level_1"
        assert state.consecutive_up_days == 2

        # Day 3: up → recovered
        state, actions = check_circuit_breaker(968_000, 965_000, state, config)
        assert state.status == "normal"
        assert "recovered" in actions

    def test_recovery_interrupted(self):
        """UC-3.5: 2 up days then down → counter resets."""
        state = CircuitBreakerState(
            status="level_1", trigger_nav=960_000,
            recovery_target_days=3, consecutive_up_days=0,
        )
        config = _default_config()

        # Day 1: up
        state, _ = check_circuit_breaker(962_000, 960_000, state, config)
        assert state.consecutive_up_days == 1

        # Day 2: down → reset
        state, _ = check_circuit_breaker(961_000, 962_000, state, config)
        assert state.consecutive_up_days == 0
        assert state.status == "level_1"

    def test_level2_recovery_5_up_days(self):
        """UC-3.8: 5 consecutive up days → Level 2 enters 'recovering'."""
        state = CircuitBreakerState(
            status="level_2", trigger_nav=900_000,
            recovery_target_days=5, consecutive_up_days=0,
        )
        config = _default_config()

        navs = [900_000, 901_000, 903_000, 906_000, 910_000, 915_000]
        for i in range(1, 6):
            state, actions = check_circuit_breaker(navs[i], navs[i-1], state, config)

        assert state.status == "recovering"
        assert "recovered" in actions


class TestCircuitBreakerHelpers:
    """Test helper functions."""

    def test_is_active(self):
        assert is_circuit_breaker_active(CircuitBreakerState(status="normal")) is False
        assert is_circuit_breaker_active(CircuitBreakerState(status="level_1")) is True
        assert is_circuit_breaker_active(CircuitBreakerState(status="level_2")) is True
        assert is_circuit_breaker_active(CircuitBreakerState(status="recovering")) is True

    def test_position_scale(self):
        assert get_position_scale(CircuitBreakerState(status="normal")) == 1.0
        assert get_position_scale(CircuitBreakerState(status="level_1")) == 0.5
        assert get_position_scale(CircuitBreakerState(status="level_2")) == 0.0
        assert get_position_scale(CircuitBreakerState(status="recovering")) == 0.5
