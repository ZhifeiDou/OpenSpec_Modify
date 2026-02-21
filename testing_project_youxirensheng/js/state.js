/**
 * state.js — Central game state, save/load, initialization
 */
var Game = window.Game || {};

Game.state = (function() {
    var STORAGE_KEY = 'family_life_sim_save';
    var AUTOSAVE_INTERVAL = 30000; // 30 seconds
    var MAX_OFFLINE_SECONDS = 86400; // 24 hours
    var MAX_MEMBERS = 4;

    var gameState = {
        familyName: '家族',
        currency: 0,
        diamonds: 0,
        date: { year: 2024, month: 1, day: 1 },
        isPaused: false,
        members: [],
        doubleIncomeBuff: { active: false, endsAt: 0 },
        newbieRewardsClaimed: [],
        completedTasks: [],
        settings: { zoom: 100 },
        lastSaveTimestamp: Date.now()
    };

    var autosaveTimer = null;

    function getState() {
        return gameState;
    }

    function getMaxMembers() {
        return MAX_MEMBERS;
    }

    function initNewGame(familyName) {
        gameState.familyName = familyName || '新家族';
        gameState.currency = 1000;
        gameState.diamonds = 0;
        gameState.date = { year: 2024, month: 1, day: 1 };
        gameState.isPaused = false;
        gameState.members = Game.family.createDefaultParents();
        gameState.doubleIncomeBuff = { active: false, endsAt: 0 };
        gameState.newbieRewardsClaimed = [];
        gameState.completedTasks = [];
        gameState.settings = { zoom: 100 };
        gameState.lastSaveTimestamp = Date.now();
        saveGame();
    }

    function saveGame() {
        try {
            gameState.lastSaveTimestamp = Date.now();
            localStorage.setItem(STORAGE_KEY, JSON.stringify(gameState));
        } catch (e) {
            // localStorage may be full or unavailable
        }
    }

    function loadGame() {
        try {
            var data = localStorage.getItem(STORAGE_KEY);
            if (!data) return null;

            var parsed = JSON.parse(data);
            if (!parsed || !parsed.familyName || !parsed.members) {
                return null;
            }

            // Restore state
            Object.keys(parsed).forEach(function(key) {
                if (parsed[key] !== undefined) {
                    gameState[key] = parsed[key];
                }
            });

            return gameState;
        } catch (e) {
            // Corrupted data
            localStorage.removeItem(STORAGE_KEY);
            return null;
        }
    }

    function calculateOfflineEarnings() {
        if (gameState.isPaused) return 0;
        if (!gameState.lastSaveTimestamp) return 0;

        var now = Date.now();
        var elapsedMs = now - gameState.lastSaveTimestamp;
        var elapsedSeconds = Math.floor(elapsedMs / 1000);

        if (elapsedSeconds <= 1) return 0;

        // Cap at 24 hours
        elapsedSeconds = Math.min(elapsedSeconds, MAX_OFFLINE_SECONDS);

        var netIncome = Game.economy.calculateNetIncome();
        var earnings = netIncome * elapsedSeconds;

        if (earnings > 0) {
            gameState.currency += earnings;
        }

        return earnings;
    }

    function startAutosave() {
        stopAutosave();
        autosaveTimer = setInterval(saveGame, AUTOSAVE_INTERVAL);
        window.addEventListener('beforeunload', saveGame);
    }

    function stopAutosave() {
        if (autosaveTimer) {
            clearInterval(autosaveTimer);
            autosaveTimer = null;
        }
        window.removeEventListener('beforeunload', saveGame);
    }

    function clearSave() {
        localStorage.removeItem(STORAGE_KEY);
    }

    return {
        getState: getState,
        getMaxMembers: getMaxMembers,
        initNewGame: initNewGame,
        saveGame: saveGame,
        loadGame: loadGame,
        calculateOfflineEarnings: calculateOfflineEarnings,
        startAutosave: startAutosave,
        stopAutosave: stopAutosave,
        clearSave: clearSave
    };
})();

window.Game = Game;
