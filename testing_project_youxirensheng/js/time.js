/**
 * time.js — In-game date system with correct calendar handling
 */
var Game = window.Game || {};

Game.time = (function() {

    function isLeapYear(year) {
        return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    }

    function daysInMonth(year, month) {
        var days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        if (month === 2 && isLeapYear(year)) {
            return 29;
        }
        return days[month];
    }

    function advanceDate() {
        var state = Game.state.getState();
        if (state.isPaused) return;

        var date = state.date;
        date.day++;

        if (date.day > daysInMonth(date.year, date.month)) {
            date.day = 1;
            date.month++;

            if (date.month > 12) {
                date.month = 1;
                date.year++;
            }
        }
    }

    function togglePause() {
        var state = Game.state.getState();
        state.isPaused = !state.isPaused;
    }

    return {
        advanceDate: advanceDate,
        togglePause: togglePause,
        isLeapYear: isLeapYear,
        daysInMonth: daysInMonth
    };
})();

window.Game = Game;
