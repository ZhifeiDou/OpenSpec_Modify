## 1. Project Scaffolding

- [x] 1.1 Create the directory structure: `testing_project_youxirensheng/css/` and `testing_project_youxirensheng/js/`
- [x] 1.2 Create `index.html` with the HTML shell: doctype, meta viewport, CSS link, script tags for all JS files in dependency order, and the main layout containers (top HUD, sub-header, main area, bottom nav)
- [x] 1.3 Create `css/style.css` with CSS reset, CSS custom properties (colors, sizes), and the 3-row CSS Grid layout (fixed top, flexible middle, fixed bottom)
- [x] 1.4 Create `js/utils.js` with the Chinese number formatting function (万/亿 units) and any shared helper functions

## 2. Game State & Persistence

- [x] 2.1 Create `js/state.js` with the central `gameState` object structure (familyName, currency, diamonds, date, isPaused, members array, activities, settings, lastSaveTimestamp)
- [x] 2.2 Implement `initNewGame()` — prompt for family name, create two default parent members with positive income rates, set starting currency and date
- [x] 2.3 Implement `saveGame()` — serialize gameState to JSON and write to localStorage
- [x] 2.4 Implement `loadGame()` — read localStorage, validate JSON, restore gameState; fall back to new game if invalid or missing
- [x] 2.5 Implement offline earnings calculation on load — compute elapsed seconds since lastSaveTimestamp, cap at 86,400s, multiply by net income, add to currency
- [x] 2.6 Wire auto-save on a 30-second interval and on `beforeunload` event

## 3. Game Loop & Time Progression

- [x] 3.1 Create `js/time.js` with the date model (year, month, day) and `advanceDate()` function handling month/year rollover and leap years
- [x] 3.2 Create `js/economy.js` with `calculateNetIncome()` (sum all member rates, apply double income buff if active) and `applyTick()` (add net income to currency, clamp to ≥ 0)
- [x] 3.3 Create `js/main.js` with the game loop — `setInterval` at 1000ms calling advanceDate(), applyTick(), and render(); respect isPaused state
- [x] 3.4 Implement pause/resume toggle — clicking the pause button toggles `gameState.isPaused`, updates the button icon, and stops/starts state changes on tick

## 4. Family Members System

- [x] 4.1 Create `js/family.js` with family member data model (id, name, role, avatar, gender, level, incomePerSecond, parentId)
- [x] 4.2 Implement `createDefaultParents()` — generate two parent members (one male, one female) with starting income rates and level 1
- [x] 4.3 Implement `addChildMember()` — create a child member with a cost rate of -100/S, level 0, linked to parents; enforce max capacity check
- [x] 4.4 Implement `levelUpMember(memberId)` — increment level, increase income rate (or reduce cost rate for children)

## 5. Family Tree Rendering

- [x] 5.1 Create the family tree container in the main area with `position: relative` for absolute node positioning
- [x] 5.2 Implement `renderFamilyTree()` — create/update DOM nodes for each family member: circular avatar div with emoji, colored border (blue for male, pink for female), level badge, and income/cost rate label
- [x] 5.3 Implement SVG connector lines — draw a horizontal line between parents and curved lines from parent pair down to each child using SVG `<path>` elements
- [x] 5.4 Position parent nodes in the upper-center row and child nodes in the lower row using absolute positioning calculated from member count
- [x] 5.5 Implement node tap/click handler — tapping a member node opens a detail panel/modal with full member stats
- [x] 5.6 Implement zoom controls — plus/minus buttons and percentage label at bottom-right; apply CSS `transform: scale()` to the tree container, clamp between 50%-200%

## 6. Top HUD & Sub-Header

- [x] 6.1 Style the top HUD bar — green currency pill (icon + formatted value + /S rate), diamond icon with count, "+" button, "..." menu dots
- [x] 6.2 Style the sub-header — back arrow, pause button + date display (YYYY.MM.DD), family name (large centered text), edit/share/stop buttons, member count
- [x] 6.3 Create `js/ui.js` with `render()` function that updates all HUD elements: currency display (Chinese formatted), income rate, diamond count, date string, member count, pause button state
- [x] 6.4 Implement family name editing — pencil button opens an inline text input; confirming updates gameState.familyName and re-renders
- [x] 6.5 Implement stop/end game button (终止) — shows confirmation modal; on confirm, clears localStorage and calls initNewGame()

## 7. Bottom Navigation Bar

- [x] 7.1 Style the 5-tab bottom nav bar with icons: inventory (📦), achievements (⭐), family/家庭 (🏠❤️), help (?), trophies (🏆)
- [x] 7.2 Implement tab switching — tapping a tab highlights it and swaps the main content area to show the corresponding section view
- [x] 7.3 Create placeholder content panels for non-family tabs (inventory, achievements, help, trophies) with section name labels

## 8. Side Activities

- [x] 8.1 Create `js/activities.js` with activity data definitions — each activity has an id, Chinese label, icon/emoji, position (left/right sidebar), and a handler function
- [x] 8.2 Render left sidebar activity buttons: 双倍收入 (💰x2), 管家 (👔), 神秘事件 (📜), 任务 (📋), 火山逃生 (🌋), 救救白骨精 (🦴)
- [x] 8.3 Render right sidebar activity buttons: 计算机专业 (💻), 新手奖励 (🎁), 异世界大门 (🌀)
- [x] 8.4 Implement the modal dialog component — semi-transparent backdrop, centered panel, close button; reusable for all activities
- [x] 8.5 Implement mystery events (神秘事件) — random event pool with narrative text and rewards (currency/diamonds); display in modal, grant reward on claim
- [x] 8.6 Implement tasks/quests (任务) — predefined task list with descriptions and completion conditions; display in modal with checkboxes; grant rewards on completion
- [x] 8.7 Implement newbie rewards (新手奖励) — one-time claimable rewards for new players; track claimed state in gameState
- [x] 8.8 Implement double income buff (双倍收入) — activate a x2 multiplier on positive income rates for a duration; show active indicator
- [x] 8.9 Wire placeholder modals for butler (管家), volcano escape (火山逃生), save bone spirit (救救白骨精), computer science (计算机专业), other world gate (异世界大门)

## 9. Visual Polish & Background

- [x] 9.1 Create the background scenery — light blue-green CSS gradient with faint mountain silhouettes using CSS shapes or inline SVG behind the main area
- [x] 9.2 Style all activity buttons with rounded corners, shadows, icon+label layout matching the reference screenshot
- [x] 9.3 Style member avatar nodes — circular shape, border color by gender, emoji avatar centered, green/red rate labels with +/- prefix
- [x] 9.4 Add CSS transitions for modal open/close, tab switching, and button hover/active states
- [x] 9.5 Ensure all tap targets are ≥ 44px and all text is readable on mobile viewports (360-414px)

## 10. Integration & Testing

- [x] 10.1 Wire the startup flow: load saved game → calculate offline earnings → show offline earnings popup → start game loop → render
- [x] 10.2 Test new game flow: first open → name prompt → default family created → tree renders → economy ticking
- [x] 10.3 Test save/load cycle: play for a bit → refresh page → verify state restored and offline earnings applied
- [x] 10.4 Test pause/resume: pause → verify no currency/date changes → resume → verify ticking resumes
- [x] 10.5 Test family member operations: add child → verify tree updates, income recalculates, count updates; test capacity limit
- [x] 10.6 Test all activity buttons open their respective modals and mystery events grant rewards correctly
- [x] 10.7 Verify Chinese number formatting at various thresholds (below 万, in 万 range, in 亿 range)
- [x] 10.8 Test on mobile viewport (360px) — verify layout, no overflow, all buttons tappable
