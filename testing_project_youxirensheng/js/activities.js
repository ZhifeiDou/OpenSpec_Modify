/**
 * activities.js — Side activities data and handlers
 */
var Game = window.Game || {};

Game.activities = (function() {

    // Mystery event pool
    var MYSTERY_EVENTS = [
        { title: '路边捡到红包', text: '你在散步时发现了一个红包！', rewardType: 'currency', reward: 5000 },
        { title: '彩票中奖', text: '家人买的彩票中了一个小奖！', rewardType: 'currency', reward: 10000 },
        { title: '意外的礼物', text: '一位远房亲戚寄来了神秘礼物！', rewardType: 'diamonds', reward: 1 },
        { title: '股票大涨', text: '投资的股票今天涨停了！', rewardType: 'currency', reward: 20000 },
        { title: '发现宝石', text: '在整理旧物时发现了一颗宝石！', rewardType: 'diamonds', reward: 2 },
        { title: '邻居的感谢', text: '帮助邻居后收到了感谢礼金。', rewardType: 'currency', reward: 3000 },
        { title: '网上中奖', text: '参加网上抽奖活动幸运中奖！', rewardType: 'currency', reward: 8000 },
        { title: '旧物变宝', text: '家里的旧物在二手市场卖了好价钱！', rewardType: 'currency', reward: 15000 }
    ];

    // Task/quest definitions
    var TASKS = [
        { id: 'task_earn_10k', desc: '累计收入达到1万', condition: function(s) { return s.currency >= 10000; }, rewardType: 'currency', reward: 2000 },
        { id: 'task_earn_100k', desc: '累计收入达到10万', condition: function(s) { return s.currency >= 100000; }, rewardType: 'diamonds', reward: 1 },
        { id: 'task_earn_1m', desc: '累计收入达到100万', condition: function(s) { return s.currency >= 1000000; }, rewardType: 'diamonds', reward: 3 },
        { id: 'task_add_child', desc: '添加第一个孩子', condition: function(s) { return s.members.length >= 3; }, rewardType: 'currency', reward: 5000 },
        { id: 'task_full_family', desc: '家庭成员达到上限', condition: function(s) { return s.members.length >= Game.state.getMaxMembers(); }, rewardType: 'diamonds', reward: 2 },
        { id: 'task_level_10', desc: '任意成员等级达到10', condition: function(s) { return s.members.some(function(m) { return m.level >= 10; }); }, rewardType: 'currency', reward: 10000 }
    ];

    // Newbie rewards
    var NEWBIE_REWARDS = [
        { id: 'newbie_welcome', desc: '欢迎礼包', rewardType: 'currency', reward: 5000 },
        { id: 'newbie_diamond', desc: '新手钻石', rewardType: 'diamonds', reward: 3 },
        { id: 'newbie_boost', desc: '首次加速', rewardType: 'currency', reward: 10000 }
    ];

    // Activity button definitions
    var LEFT_ACTIVITIES = [
        { id: 'double-income', icon: '💰', label: '双倍收入', sublabel: 'x2', handler: handleDoubleIncome },
        { id: 'butler', icon: '👔', label: '管家', handler: handlePlaceholder },
        { id: 'mystery-event', icon: '📜', label: '神秘事件', handler: handleMysteryEvent },
        { id: 'tasks', icon: '📋', label: '任务', handler: handleTasks },
        { id: 'volcano-escape', icon: '🌋', label: '火山逃生', handler: handlePlaceholder },
        { id: 'save-bone-spirit', icon: '🦴', label: '救救白骨精', handler: handlePlaceholder }
    ];

    var RIGHT_ACTIVITIES = [
        { id: 'computer-science', icon: '💻', label: '计算机专业', handler: handlePlaceholder },
        { id: 'newbie-rewards', icon: '🎁', label: '新手奖励', handler: handleNewbieRewards },
        { id: 'other-world', icon: '🌀', label: '异世界大门', handler: handlePlaceholder }
    ];

    function handleDoubleIncome() {
        var state = Game.state.getState();
        if (state.doubleIncomeBuff && state.doubleIncomeBuff.active) {
            Game.ui.showModal('双倍收入', '<p class="modal-text">双倍收入已激活中！</p>');
            return;
        }

        var cost = 1; // costs 1 diamond
        if (state.diamonds < cost) {
            Game.ui.showModal('双倍收入', '<p class="modal-text">钻石不足！需要 ' + cost + ' 颗钻石。</p>');
            return;
        }

        var content = '<p class="modal-text">消耗 1 颗钻石，激活双倍收入 60 秒！</p>' +
            '<button class="modal-btn confirm" onclick="Game.activities.confirmDoubleIncome()">确认激活</button>' +
            '<button class="modal-btn cancel" onclick="Game.ui.closeModal()">取消</button>';
        Game.ui.showModal('💰 双倍收入', content);
    }

    function confirmDoubleIncome() {
        var state = Game.state.getState();
        state.diamonds -= 1;
        Game.economy.activateDoubleIncome(60000);
        Game.ui.closeModal();
        Game.ui.render();
    }

    function handleMysteryEvent() {
        var event = Game.utils.randomPick(MYSTERY_EVENTS);
        var rewardText = event.rewardType === 'currency'
            ? Game.utils.formatCurrency(event.reward) + ' 金币'
            : event.reward + ' 颗钻石';

        var content = '<p class="modal-text">' + event.text + '</p>' +
            '<div class="modal-reward">🎉 奖励: ' + rewardText + '</div>' +
            '<button class="modal-btn confirm" onclick="Game.activities.claimEventReward(\'' +
            event.rewardType + '\',' + event.reward + ')">领取奖励</button>';

        Game.ui.showModal('🔮 ' + event.title, content);
    }

    function claimEventReward(type, amount) {
        var state = Game.state.getState();
        if (type === 'currency') {
            state.currency += amount;
        } else {
            state.diamonds += amount;
        }
        Game.ui.closeModal();
        Game.ui.render();
    }

    function handleTasks() {
        var state = Game.state.getState();
        var html = '<ul class="task-list">';

        TASKS.forEach(function(task) {
            var done = state.completedTasks.indexOf(task.id) !== -1;
            var met = !done && task.condition(state);
            var rewardText = task.rewardType === 'currency'
                ? Game.utils.formatCurrency(task.reward)
                : task.reward + '💎';

            html += '<li class="task-item' + (done ? ' done' : '') + '">';
            html += '<div class="task-check"></div>';
            html += '<span class="task-desc">' + task.desc + '</span>';

            if (done) {
                html += '<span class="task-reward">✅</span>';
            } else if (met) {
                html += '<button class="claim-btn" onclick="Game.activities.claimTask(\'' + task.id + '\',\'' +
                    task.rewardType + '\',' + task.reward + ')">领取 ' + rewardText + '</button>';
            } else {
                html += '<span class="task-reward">' + rewardText + '</span>';
            }

            html += '</li>';
        });

        html += '</ul>';
        Game.ui.showModal('📋 任务', html);
    }

    function claimTask(taskId, rewardType, reward) {
        var state = Game.state.getState();
        if (state.completedTasks.indexOf(taskId) !== -1) return;

        state.completedTasks.push(taskId);
        if (rewardType === 'currency') {
            state.currency += reward;
        } else {
            state.diamonds += reward;
        }

        // Re-render the tasks modal
        handleTasks();
        Game.ui.render();
    }

    function handleNewbieRewards() {
        var state = Game.state.getState();
        var html = '';

        NEWBIE_REWARDS.forEach(function(reward) {
            var claimed = state.newbieRewardsClaimed.indexOf(reward.id) !== -1;
            var rewardText = reward.rewardType === 'currency'
                ? Game.utils.formatCurrency(reward.reward) + ' 金币'
                : reward.reward + ' 颗钻石';

            html += '<div class="reward-item">';
            html += '<span class="reward-desc">' + reward.desc + ' (' + rewardText + ')</span>';

            if (claimed) {
                html += '<button class="claim-btn" disabled>已领取</button>';
            } else {
                html += '<button class="claim-btn" onclick="Game.activities.claimNewbieReward(\'' +
                    reward.id + '\',\'' + reward.rewardType + '\',' + reward.reward + ')">领取</button>';
            }

            html += '</div>';
        });

        var allClaimed = NEWBIE_REWARDS.every(function(r) {
            return state.newbieRewardsClaimed.indexOf(r.id) !== -1;
        });

        if (allClaimed) {
            html += '<p class="modal-text" style="text-align:center;margin-top:12px;">🎉 所有新手奖励已领取！</p>';
        }

        Game.ui.showModal('🎁 新手奖励', html);
    }

    function claimNewbieReward(rewardId, rewardType, reward) {
        var state = Game.state.getState();
        if (state.newbieRewardsClaimed.indexOf(rewardId) !== -1) return;

        state.newbieRewardsClaimed.push(rewardId);
        if (rewardType === 'currency') {
            state.currency += reward;
        } else {
            state.diamonds += reward;
        }

        // Re-render
        handleNewbieRewards();
        Game.ui.render();
    }

    function handlePlaceholder() {
        Game.ui.showModal('🔜 敬请期待', '<p class="modal-text" style="text-align:center;">此功能即将推出，敬请期待！</p>');
    }

    function getLeftActivities() {
        return LEFT_ACTIVITIES;
    }

    function getRightActivities() {
        return RIGHT_ACTIVITIES;
    }

    return {
        getLeftActivities: getLeftActivities,
        getRightActivities: getRightActivities,
        confirmDoubleIncome: confirmDoubleIncome,
        claimEventReward: claimEventReward,
        claimTask: claimTask,
        claimNewbieReward: claimNewbieReward,
        handleDoubleIncome: handleDoubleIncome,
        handleMysteryEvent: handleMysteryEvent,
        handleTasks: handleTasks,
        handleNewbieRewards: handleNewbieRewards
    };
})();

window.Game = Game;
