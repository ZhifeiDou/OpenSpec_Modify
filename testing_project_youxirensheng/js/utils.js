/**
 * utils.js — Shared helper functions
 */
var Game = window.Game || {};

Game.utils = (function() {
    /**
     * Format currency with Chinese units (万, 亿)
     */
    function formatCurrency(value) {
        if (value >= 100000000) {
            return (value / 100000000).toFixed(2) + '亿';
        } else if (value >= 10000) {
            return (value / 10000).toFixed(2) + '万';
        }
        return Math.floor(value).toString();
    }

    /**
     * Format date as YYYY.MM.DD
     */
    function formatDate(date) {
        var y = date.year;
        var m = String(date.month).padStart(2, '0');
        var d = String(date.day).padStart(2, '0');
        return y + '.' + m + '.' + d;
    }

    /**
     * Generate a unique ID
     */
    function generateId() {
        return 'member_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
    }

    /**
     * Pick a random element from an array
     */
    function randomPick(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    /**
     * Clamp a value between min and max
     */
    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    return {
        formatCurrency: formatCurrency,
        formatDate: formatDate,
        generateId: generateId,
        randomPick: randomPick,
        clamp: clamp
    };
})();

window.Game = Game;
