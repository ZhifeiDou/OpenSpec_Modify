/**
 * family.js — Family member management, tree data
 */
var Game = window.Game || {};

Game.family = (function() {
    var MALE_AVATARS = ['👨', '👦'];
    var FEMALE_AVATARS = ['👩', '👧'];
    var MALE_NAMES = ['小明', '小刚', '小强', '大伟', '志远'];
    var FEMALE_NAMES = ['小红', '小丽', '小美', '晓雪', '思琪'];
    var CHILD_MALE_NAMES = ['天天', '乐乐', '壮壮', '小宝', '阳阳'];
    var CHILD_FEMALE_NAMES = ['甜甜', '朵朵', '妮妮', '贝贝', '萌萌'];
    var EMOJI_EXPRESSIONS = ['🤔', '😊', '😄', '😎', '🥰', '😁'];

    var BASE_INCOME_FATHER = 350;
    var BASE_INCOME_MOTHER = 650;
    var CHILD_COST = -100;
    var LEVEL_INCOME_BONUS = 15;

    function createMember(options) {
        return {
            id: Game.utils.generateId(),
            name: options.name,
            role: options.role, // 'parent' or 'child'
            gender: options.gender, // 'male' or 'female'
            avatar: options.avatar,
            expression: options.expression || '',
            level: options.level || 0,
            incomePerSecond: options.incomePerSecond || 0
        };
    }

    function createDefaultParents() {
        var father = createMember({
            name: Game.utils.randomPick(MALE_NAMES),
            role: 'parent',
            gender: 'male',
            avatar: '👨',
            expression: Game.utils.randomPick(EMOJI_EXPRESSIONS),
            level: 1,
            incomePerSecond: BASE_INCOME_FATHER
        });

        var mother = createMember({
            name: Game.utils.randomPick(FEMALE_NAMES),
            role: 'parent',
            gender: 'female',
            avatar: '👩',
            expression: Game.utils.randomPick(EMOJI_EXPRESSIONS),
            level: 1,
            incomePerSecond: BASE_INCOME_MOTHER
        });

        return [father, mother];
    }

    function addChildMember() {
        var state = Game.state.getState();
        if (state.members.length >= Game.state.getMaxMembers()) {
            return null; // at capacity
        }

        var gender = Math.random() < 0.5 ? 'male' : 'female';
        var names = gender === 'male' ? CHILD_MALE_NAMES : CHILD_FEMALE_NAMES;
        var avatars = gender === 'male' ? MALE_AVATARS : FEMALE_AVATARS;

        var child = createMember({
            name: Game.utils.randomPick(names),
            role: 'child',
            gender: gender,
            avatar: avatars[1], // child avatar
            level: 0,
            incomePerSecond: CHILD_COST
        });

        state.members.push(child);
        return child;
    }

    function levelUpMember(memberId) {
        var state = Game.state.getState();
        var member = state.members.find(function(m) { return m.id === memberId; });
        if (!member) return;

        member.level++;

        if (member.role === 'parent') {
            member.incomePerSecond += LEVEL_INCOME_BONUS;
        } else {
            // Reduce cost for children (make less negative, min 0)
            member.incomePerSecond = Math.min(0, member.incomePerSecond + 5);
        }
    }

    function getParents() {
        var state = Game.state.getState();
        return state.members.filter(function(m) { return m.role === 'parent'; });
    }

    function getChildren() {
        var state = Game.state.getState();
        return state.members.filter(function(m) { return m.role === 'child'; });
    }

    return {
        createDefaultParents: createDefaultParents,
        addChildMember: addChildMember,
        levelUpMember: levelUpMember,
        getParents: getParents,
        getChildren: getChildren
    };
})();

window.Game = Game;
