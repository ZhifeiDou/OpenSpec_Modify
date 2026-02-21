/**
 * main.js — Game entry point, game loop, startup flow
 */
var Game = window.Game || {};

Game.main = (function() {

    var loopTimer = null;

    function startLoop() {
        stopLoop();
        loopTimer = setInterval(function() {
            var state = Game.state.getState();
            if (!state.isPaused) {
                Game.time.advanceDate();
                Game.economy.applyTick();
            }
            Game.ui.render();
        }, 1000);
    }

    function stopLoop() {
        if (loopTimer) {
            clearInterval(loopTimer);
            loopTimer = null;
        }
    }

    function startup() {
        // Initialize UI
        Game.ui.init();

        // Try to load saved game
        var saved = Game.state.loadGame();

        if (saved) {
            // Calculate offline earnings
            var earnings = Game.state.calculateOfflineEarnings();

            // Render current state
            Game.ui.render();

            // Show offline earnings if any
            if (earnings > 0) {
                Game.ui.showOfflineEarnings(earnings);
            }

            // Start the loop
            startLoop();
            Game.state.startAutosave();
        } else {
            // New game — ask for family name
            Game.ui.showNamePrompt(function(name) {
                Game.state.initNewGame(name);
                Game.ui.render();
                startLoop();
                Game.state.startAutosave();
            });
        }
    }

    // Boot when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startup);
    } else {
        startup();
    }

    return {
        startLoop: startLoop,
        stopLoop: stopLoop
    };
})();

window.Game = Game;
