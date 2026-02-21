/**
 * economy.js — Idle economy engine: income calculation, tick application
 */
var Game = window.Game || {};

Game.economy = (function() {

    function calculateNetIncome() {
        var state = Game.state.getState();
        var total = 0;

        state.members.forEach(function(member) {
            var rate = member.incomePerSecond;
            // Apply double income buff to positive rates only
            if (rate > 0 && state.doubleIncomeBuff && state.doubleIncomeBuff.active) {
                rate *= 2;
            }
            total += rate;
        });

        return total;
    }

    function applyTick() {
        var state = Game.state.getState();
        if (state.isPaused) return;

        var netIncome = calculateNetIncome();
        state.currency += netIncome;

        // Currency cannot go below zero
        if (state.currency < 0) {
            state.currency = 0;
        }

        // Check double income buff expiration
        if (state.doubleIncomeBuff && state.doubleIncomeBuff.active) {
            if (Date.now() >= state.doubleIncomeBuff.endsAt) {
                state.doubleIncomeBuff.active = false;
            }
        }
    }

    function activateDoubleIncome(durationMs) {
        var state = Game.state.getState();
        state.doubleIncomeBuff = {
            active: true,
            endsAt: Date.now() + (durationMs || 60000) // default 60s
        };
    }

    return {
        calculateNetIncome: calculateNetIncome,
        applyTick: applyTick,
        activateDoubleIncome: activateDoubleIncome
    };
})();

window.Game = Game;
