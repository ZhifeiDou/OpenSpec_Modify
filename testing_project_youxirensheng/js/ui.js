/**
 * ui.js — DOM rendering, HUD updates, family tree, nav bar, modals
 */
var Game = window.Game || {};

Game.ui = (function() {

    // Cache DOM elements
    var els = {};

    function init() {
        els.currencyValue = document.getElementById('currency-value');
        els.incomeRate = document.getElementById('income-rate');
        els.diamondCount = document.getElementById('diamond-count');
        els.dateValue = document.getElementById('date-value');
        els.familyName = document.getElementById('family-name');
        els.memberCount = document.getElementById('member-count-value');
        els.btnPause = document.getElementById('btn-pause');
        els.btnEditName = document.getElementById('btn-edit-name');
        els.btnStop = document.getElementById('btn-stop');
        els.btnShare = document.getElementById('btn-share');
        els.btnBack = document.getElementById('btn-back');
        els.btnAddDiamond = document.getElementById('btn-add-diamond');
        els.btnMenu = document.getElementById('btn-menu');
        els.treeContainer = document.getElementById('family-tree-container');
        els.treeNodes = document.getElementById('tree-nodes');
        els.treeLines = document.getElementById('tree-lines');
        els.sidebarLeft = document.getElementById('sidebar-left');
        els.sidebarRight = document.getElementById('sidebar-right');
        els.zoomIn = document.getElementById('btn-zoom-in');
        els.zoomOut = document.getElementById('btn-zoom-out');
        els.zoomValue = document.getElementById('zoom-value');
        els.bottomNav = document.getElementById('bottom-nav');
        els.modalOverlay = document.getElementById('modal-overlay');
        els.modalContent = document.getElementById('modal-content');
        els.modalClose = document.getElementById('modal-close');
        els.nameModal = document.getElementById('name-modal');
        els.nameInput = document.getElementById('name-input');
        els.nameConfirm = document.getElementById('name-confirm');
        els.offlineModal = document.getElementById('offline-modal');
        els.offlineMessage = document.getElementById('offline-message');
        els.offlineConfirm = document.getElementById('offline-confirm');

        els.btnAddChild = document.getElementById('btn-add-child');

        bindEvents();
        renderSidebars();
    }

    function bindEvents() {
        // Pause/Resume
        els.btnPause.addEventListener('click', function() {
            Game.time.togglePause();
            render();
        });

        // Edit family name
        els.btnEditName.addEventListener('click', startNameEdit);

        // Stop game
        els.btnStop.addEventListener('click', function() {
            showModal('⏹ 终止游戏', '<p class="modal-text">确定要结束当前游戏吗？所有进度将丢失。</p>' +
                '<button class="modal-btn confirm" onclick="Game.ui.confirmStopGame()">确认终止</button>' +
                '<button class="modal-btn cancel" onclick="Game.ui.closeModal()">取消</button>');
        });

        // Add child
        els.btnAddChild.addEventListener('click', function() {
            var state = Game.state.getState();
            if (state.members.length >= Game.state.getMaxMembers()) {
                showModal('家庭已满', '<p class="modal-text">家庭成员已达上限！</p>');
                return;
            }
            var child = Game.family.addChildMember();
            if (child) {
                render();
            }
        });

        // Zoom
        els.zoomIn.addEventListener('click', function() {
            var state = Game.state.getState();
            state.settings.zoom = Game.utils.clamp(state.settings.zoom + 10, 50, 200);
            applyZoom();
        });

        els.zoomOut.addEventListener('click', function() {
            var state = Game.state.getState();
            state.settings.zoom = Game.utils.clamp(state.settings.zoom - 10, 50, 200);
            applyZoom();
        });

        // Bottom nav tabs
        els.bottomNav.addEventListener('click', function(e) {
            var tab = e.target.closest('.nav-tab');
            if (!tab) return;
            switchTab(tab.dataset.tab);
        });

        // Modal close
        els.modalClose.addEventListener('click', closeModal);
        els.modalOverlay.addEventListener('click', function(e) {
            if (e.target === els.modalOverlay) closeModal();
        });

        // Offline confirm
        els.offlineConfirm.addEventListener('click', function() {
            els.offlineModal.classList.add('hidden');
        });

        // Name modal confirm
        els.nameConfirm.addEventListener('click', function() {
            var name = els.nameInput.value.trim();
            if (name) {
                Game.state.getState().familyName = name;
            }
            els.nameModal.classList.add('hidden');
            Game.ui.render();
        });

        els.nameInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                els.nameConfirm.click();
            }
        });

        // Add diamond (placeholder)
        els.btnAddDiamond.addEventListener('click', function() {
            showModal('💎 获取钻石', '<p class="modal-text">完成任务和事件可以获得钻石！</p>');
        });

        // Share (placeholder)
        els.btnShare.addEventListener('click', function() {
            showModal('📤 分享', '<p class="modal-text">分享功能即将推出！</p>');
        });

        // Back button (placeholder)
        els.btnBack.addEventListener('click', function() {
            switchTab('family');
        });

        // Menu (placeholder)
        els.btnMenu.addEventListener('click', function() {
            showModal('⚙️ 菜单', '<p class="modal-text">设置功能即将推出！</p>');
        });
    }

    // === Rendering ===

    function render() {
        var state = Game.state.getState();

        // HUD
        els.currencyValue.textContent = Game.utils.formatCurrency(state.currency);
        els.incomeRate.textContent = Game.economy.calculateNetIncome() + '/S';
        els.diamondCount.textContent = state.diamonds;
        els.dateValue.textContent = Game.utils.formatDate(state.date);
        els.familyName.textContent = state.familyName;
        els.memberCount.textContent = state.members.length + '/' + Game.state.getMaxMembers();

        // Pause button
        els.btnPause.textContent = state.isPaused ? '▶️' : '⏸';

        // Double income indicator
        var diBtn = document.querySelector('[data-activity="double-income"]');
        if (diBtn) {
            if (state.doubleIncomeBuff && state.doubleIncomeBuff.active) {
                diBtn.classList.add('buff-active');
            } else {
                diBtn.classList.remove('buff-active');
            }
        }

        // Add child button
        if (els.btnAddChild) {
            els.btnAddChild.disabled = state.members.length >= Game.state.getMaxMembers();
        }

        // Family tree
        renderFamilyTree();
        applyZoom();
    }

    function renderFamilyTree() {
        var state = Game.state.getState();
        var parents = Game.family.getParents();
        var children = Game.family.getChildren();

        // Clear
        els.treeNodes.innerHTML = '';
        els.treeLines.innerHTML = '';

        var containerRect = els.treeContainer.getBoundingClientRect();
        var cw = containerRect.width || 360;
        var ch = containerRect.height || 500;

        var parentY = ch * 0.3;
        var childY = ch * 0.65;
        var centerX = cw / 2;

        // Render parent nodes
        var parentPositions = [];
        var parentSpacing = 100;

        parents.forEach(function(member, i) {
            var x = centerX + (i === 0 ? -parentSpacing / 2 - 36 : parentSpacing / 2 - 36);
            var y = parentY - 36;
            parentPositions.push({ x: x + 36, y: y + 36, member: member });
            renderMemberNode(member, x, y);
        });

        // Render child nodes
        var childPositions = [];
        if (children.length > 0) {
            var totalChildWidth = children.length * 120;
            var startX = centerX - totalChildWidth / 2 + 24;

            children.forEach(function(member, i) {
                var x = startX + i * 120;
                var y = childY - 36;
                childPositions.push({ x: x + 36, y: y + 36, member: member });
                renderMemberNode(member, x, y);
            });
        }

        // Draw connector lines
        drawConnectorLines(parentPositions, childPositions);
    }

    function renderMemberNode(member, x, y) {
        var node = document.createElement('div');
        node.className = 'member-node';
        node.style.left = x + 'px';
        node.style.top = y + 'px';

        var genderClass = member.gender === 'female' ? ' female' : '';
        var rateClass = member.incomePerSecond >= 0 ? 'positive' : 'negative';
        var ratePrefix = member.incomePerSecond >= 0 ? '+' : '';
        var rateText = ratePrefix + member.incomePerSecond + '/S';

        node.innerHTML =
            '<div class="avatar-wrapper">' +
                '<div class="avatar-circle' + genderClass + '">' + member.avatar + '</div>' +
                '<div class="level-badge">' + member.level + '</div>' +
                (member.expression ? '<div class="avatar-emoji">' + member.expression + '</div>' : '') +
            '</div>' +
            '<div class="rate-label ' + rateClass + '">' + rateText + '</div>';

        node.addEventListener('click', function() {
            showMemberDetail(member);
        });

        els.treeNodes.appendChild(node);
    }

    function drawConnectorLines(parentPositions, childPositions) {
        if (parentPositions.length < 2) return;

        var svgNS = 'http://www.w3.org/2000/svg';
        var p1 = parentPositions[0];
        var p2 = parentPositions[1];

        // Horizontal line between parents
        var midX = (p1.x + p2.x) / 2;
        var midY = (p1.y + p2.y) / 2;

        var hLine = document.createElementNS(svgNS, 'line');
        hLine.setAttribute('x1', p1.x);
        hLine.setAttribute('y1', p1.y + 36);
        hLine.setAttribute('x2', p2.x);
        hLine.setAttribute('y2', p2.y + 36);
        els.treeLines.appendChild(hLine);

        // Lines to children
        if (childPositions.length > 0) {
            var branchY = midY + 60;

            // Vertical line down from parent midpoint
            var vLine = document.createElementNS(svgNS, 'line');
            vLine.setAttribute('x1', midX);
            vLine.setAttribute('y1', midY + 36);
            vLine.setAttribute('x2', midX);
            vLine.setAttribute('y2', branchY);
            els.treeLines.appendChild(vLine);

            childPositions.forEach(function(child) {
                // Curved path from branch point to child
                var path = document.createElementNS(svgNS, 'path');
                var startX = midX;
                var startY = branchY;
                var endX = child.x;
                var endY = child.y - 36;
                var cpY = startY + (endY - startY) * 0.5;

                var d = 'M ' + startX + ' ' + startY +
                    ' C ' + startX + ' ' + cpY + ', ' + endX + ' ' + cpY + ', ' + endX + ' ' + endY;
                path.setAttribute('d', d);
                els.treeLines.appendChild(path);
            });
        }
    }

    function showMemberDetail(member) {
        var rateClass = member.incomePerSecond >= 0 ? 'positive' : 'negative';
        var ratePrefix = member.incomePerSecond >= 0 ? '+' : '';
        var roleText = member.role === 'parent' ? '家长' : '孩子';
        var genderText = member.gender === 'male' ? '男' : '女';

        var content = '<div class="member-detail">' +
            '<div class="detail-avatar">' + member.avatar + '</div>' +
            '<div class="detail-name">' + member.name + '</div>' +
            '<div class="detail-stats">' +
                '<div class="stat-item"><div class="stat-label">角色</div><div class="stat-value">' + roleText + '</div></div>' +
                '<div class="stat-item"><div class="stat-label">性别</div><div class="stat-value">' + genderText + '</div></div>' +
                '<div class="stat-item"><div class="stat-label">等级</div><div class="stat-value">' + member.level + '</div></div>' +
                '<div class="stat-item"><div class="stat-label">收入</div><div class="stat-value ' + rateClass + '">' + ratePrefix + member.incomePerSecond + '/S</div></div>' +
            '</div>' +
            '<button class="modal-btn confirm" onclick="Game.ui.levelUpFromModal(\'' + member.id + '\')">⬆️ 升级 (花费 ' +
            Game.utils.formatCurrency(getLevelUpCost(member)) + ')</button>' +
            '</div>';

        showModal('👤 ' + member.name, content);
    }

    function getLevelUpCost(member) {
        return (member.level + 1) * 500;
    }

    function levelUpFromModal(memberId) {
        var state = Game.state.getState();
        var member = state.members.find(function(m) { return m.id === memberId; });
        if (!member) return;

        var cost = getLevelUpCost(member);
        if (state.currency < cost) {
            showModal('升级失败', '<p class="modal-text">金币不足！需要 ' + Game.utils.formatCurrency(cost) + '</p>');
            return;
        }

        state.currency -= cost;
        Game.family.levelUpMember(memberId);
        showMemberDetail(member);
        render();
    }

    // === Sidebars ===

    function renderSidebars() {
        var leftActivities = Game.activities.getLeftActivities();
        var rightActivities = Game.activities.getRightActivities();

        els.sidebarLeft.innerHTML = '';
        leftActivities.forEach(function(act) {
            els.sidebarLeft.appendChild(createActivityButton(act));
        });

        els.sidebarRight.innerHTML = '';
        rightActivities.forEach(function(act) {
            els.sidebarRight.appendChild(createActivityButton(act));
        });
    }

    function createActivityButton(activity) {
        var btn = document.createElement('button');
        btn.className = 'activity-btn';
        btn.dataset.activity = activity.id;

        var iconHtml = '<span class="act-icon">' + activity.icon + '</span>';
        var labelHtml = '<span class="act-label">' + activity.label + '</span>';
        if (activity.sublabel) {
            iconHtml = '<span class="act-icon">' + activity.icon + '</span>';
            labelHtml = '<span class="act-label">' + activity.label + '</span>';
        }

        btn.innerHTML = iconHtml + labelHtml;
        btn.addEventListener('click', activity.handler);

        return btn;
    }

    // === Tabs ===

    function switchTab(tabName) {
        // Update nav
        var tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(function(tab) {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        // Update content
        var contents = document.querySelectorAll('.tab-content');
        contents.forEach(function(content) {
            content.classList.toggle('active', content.id === 'tab-' + tabName);
        });
    }

    // === Zoom ===

    function applyZoom() {
        var state = Game.state.getState();
        var zoom = state.settings.zoom;
        els.treeContainer.style.transform = 'scale(' + (zoom / 100) + ')';
        els.zoomValue.textContent = zoom + '%';
        els.zoomIn.disabled = zoom >= 200;
        els.zoomOut.disabled = zoom <= 50;
    }

    // === Modals ===

    function showModal(title, contentHtml) {
        els.modalContent.innerHTML = '<div class="modal-title">' + title + '</div>' + contentHtml;
        els.modalOverlay.classList.remove('hidden');
    }

    function closeModal() {
        els.modalOverlay.classList.add('hidden');
        els.modalContent.innerHTML = '';
    }

    function showNamePrompt(callback) {
        els.nameInput.value = '';
        els.nameModal.classList.remove('hidden');
        els.nameInput.focus();

        var handler = function() {
            var name = els.nameInput.value.trim() || '新家族';
            els.nameModal.classList.add('hidden');
            els.nameConfirm.removeEventListener('click', handler);
            if (callback) callback(name);
        };

        // Remove old listeners and add new
        els.nameConfirm.replaceWith(els.nameConfirm.cloneNode(true));
        els.nameConfirm = document.getElementById('name-confirm');
        els.nameConfirm.addEventListener('click', handler);

        // Also handle enter key
        var keyHandler = function(e) {
            if (e.key === 'Enter') {
                handler();
                els.nameInput.removeEventListener('keydown', keyHandler);
            }
        };
        els.nameInput.addEventListener('keydown', keyHandler);
    }

    function showOfflineEarnings(earnings) {
        if (earnings <= 0) return;
        els.offlineMessage.textContent = '你离线期间获得了 ' + Game.utils.formatCurrency(earnings) + ' 金币！';
        els.offlineModal.classList.remove('hidden');
    }

    // === Name Editing ===

    function startNameEdit() {
        var state = Game.state.getState();
        var currentName = state.familyName;

        var nameSpan = els.familyName;
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'name-edit-input';
        input.value = currentName;
        input.maxLength = 10;

        nameSpan.replaceWith(input);
        input.focus();
        input.select();

        var finish = function() {
            var newName = input.value.trim() || currentName;
            state.familyName = newName;

            var newSpan = document.createElement('span');
            newSpan.id = 'family-name';
            newSpan.textContent = newName;
            input.replaceWith(newSpan);

            els.familyName = newSpan;
        };

        input.addEventListener('blur', finish);
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                input.blur();
            }
        });
    }

    // === Stop Game ===

    function confirmStopGame() {
        closeModal();
        Game.state.stopAutosave();
        Game.state.clearSave();
        // Restart
        if (Game.main && Game.main.stopLoop) {
            Game.main.stopLoop();
        }
        showNamePrompt(function(name) {
            Game.state.initNewGame(name);
            render();
            if (Game.main && Game.main.startLoop) {
                Game.main.startLoop();
            }
            Game.state.startAutosave();
        });
    }

    return {
        init: init,
        render: render,
        showModal: showModal,
        closeModal: closeModal,
        showNamePrompt: showNamePrompt,
        showOfflineEarnings: showOfflineEarnings,
        confirmStopGame: confirmStopGame,
        levelUpFromModal: levelUpFromModal,
        switchTab: switchTab
    };
})();

window.Game = Game;
