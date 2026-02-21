## Context

This is a greenfield web-based family life simulation idle game inspired by 游戏人生. The game runs entirely in the browser with no backend. Players manage a family, earn currency passively, and interact with events and activities. The UI is mobile-first with a portrait orientation, featuring a central family tree, surrounding activity buttons, a top HUD, and a bottom navigation bar.

The target output is `testing_project_youxirensheng/` as a self-contained static web app (no build step required — open `index.html` in a browser to play).

## Goals / Non-Goals

**Goals:**
- Faithful visual replication of the reference screenshot's layout: top HUD, family tree center, side activity buttons, bottom nav bar
- Smooth idle economy that updates currency every second based on net family income
- Clean single-page app architecture with no build tools — just HTML, CSS, and vanilla JavaScript
- Mobile-first responsive design that looks correct on phone-sized viewports (360-414px wide)
- Persistent game state via localStorage so progress survives page refresh
- Chinese-locale number formatting (万 for 10,000+) and Chinese UI labels matching the reference

**Non-Goals:**
- No backend server, multiplayer, or cloud save
- No real payment/IAP system for diamonds (diamonds are earned in-game only)
- No actual mini-game implementations for side activities (volcano escape, etc.) — these will be placeholder dialogs in v1
- No audio/sound effects in initial version
- No complex animation system — CSS transitions only where needed
- No framework or build toolchain (no React, Vue, Webpack, etc.)

## Decisions

### 1. Vanilla HTML/CSS/JS — No Framework

**Decision**: Build with plain HTML, CSS, and vanilla JavaScript. Single `index.html` with linked CSS and JS files.

**Rationale**: The game is a single-screen UI with modest interactivity. A framework would add build complexity and bundle size for little benefit. Vanilla JS keeps the project simple to open and run (just double-click `index.html`).

**Alternatives considered**:
- React/Vue: Overkill for a single-screen idle game; requires build tooling
- Phaser/PixiJS: Game engine overhead not needed — this is mostly UI, not a physics/sprite game

### 2. DOM-Based Rendering for Family Tree

**Decision**: Render the family tree using absolutely-positioned DOM elements (divs with CSS) and SVG `<line>` or `<path>` elements for connector lines between family members.

**Rationale**: The family tree is a small number of nodes (max ~8-10 members). DOM rendering gives us easy click handlers, CSS styling (rounded avatars, colored borders, badges), and accessibility. SVG lines are simple to calculate for parent-child connections.

**Alternatives considered**:
- HTML5 Canvas: More complex to handle click targets, text rendering, and styling; better suited for large numbers of sprites
- Pure CSS lines: Limited to straight vertical/horizontal lines; SVG paths allow the curved connectors shown in the reference

### 3. Game Loop with setInterval (1-second tick)

**Decision**: Use `setInterval` with a 1-second tick for the core economy loop. Use `requestAnimationFrame` only for smooth UI counter animations.

**Rationale**: The idle economy updates once per second ("+X/S" rates). A 1-second interval is the natural tick rate. For the currency counter display, we can use `requestAnimationFrame` to animate the number smoothly between ticks, but the actual state mutation happens on the 1-second boundary.

**Alternatives considered**:
- Pure requestAnimationFrame with delta time: More precise but unnecessary complexity for a 1/s tick rate
- Web Worker for tick: Overkill; the computation is trivial

### 4. State Management with a Central Game Object

**Decision**: Single `gameState` JavaScript object holding all game data. Modules read/write to this shared object. State changes trigger a `render()` function that updates the DOM.

**Structure**:
```
gameState = {
  familyName: "姚家族",
  currency: 72100,
  diamonds: 3,
  date: { year: 2024, month: 9, day: 6 },
  isPaused: false,
  tickRate: 1000,
  members: [
    { id, name, avatar, role, level, incomePerSecond, parentId, ... }
  ],
  activities: [...],
  settings: { zoom: 100 }
}
```

**Rationale**: Simple, debuggable, and easy to serialize to localStorage. No need for reactive state, observables, or event buses at this scale.

### 5. localStorage for Persistence

**Decision**: Auto-save `gameState` to `localStorage` every 30 seconds and on page unload. Load on startup. On first visit, initialize a default family.

**Rationale**: Simplest persistence for a client-only game. No backend needed. `localStorage` is synchronous and has ~5MB limit — more than enough for game state JSON.

**Alternatives considered**:
- IndexedDB: More complex API; no benefit for small JSON state
- Cookies: Size-limited, not designed for structured data

### 6. CSS-Drawn Avatars with Emoji Fallbacks

**Decision**: Use CSS-styled circular containers with solid color backgrounds and single-character emoji or initials as placeholder avatars. Activity buttons use emoji icons.

**Rationale**: Avoids dependency on external image assets. The reference uses cartoon avatars, but for a replication we can use stylized CSS circles with emoji faces (👨, 👩, 👦, 👧) or SVG simple illustrations. This keeps the project self-contained with zero asset downloads.

**Alternatives considered**:
- External image assets: Would require hosting or bundling images; harder to distribute as a single project
- Canvas-drawn avatars: More complex than needed for simple circular portraits

### 7. Chinese Number Formatting

**Decision**: Format currency using Chinese units: numbers ≥10,000 display as `X.XX万`, numbers ≥100,000,000 display as `X.XX亿`. Below 10,000, show the raw number.

**Rationale**: Matches the reference UI (shows "7.21万"). This is a simple formatting function, not a full i18n system.

### 8. File Structure

```
testing_project_youxirensheng/
├── index.html          # Single HTML page, entry point
├── css/
│   └── style.css       # All styles (mobile-first, layout, components)
├── js/
│   ├── main.js         # Entry point, game loop init, event binding
│   ├── state.js        # gameState object, save/load, initialization
│   ├── economy.js      # Tick calculation, income/cost aggregation
│   ├── family.js       # Family member management, tree data
│   ├── time.js         # Date progression, pause/resume
│   ├── activities.js   # Side activities data and handlers
│   ├── ui.js           # DOM rendering, HUD updates, nav bar
│   └── utils.js        # Currency formatting, helpers
└── unnamed.jpg         # Reference screenshot (already exists)
```

### 9. Layout Architecture

**Decision**: Use CSS Grid for the overall page layout (top HUD, main area, bottom nav). The main area uses position:relative with absolutely-positioned family tree nodes and side buttons. The family tree uses a flexbox-based vertical layout for generations with SVG overlay for connector lines.

**Screen regions** (matching the reference):
- **Top bar** (fixed): Currency pill, diamond count, add button, menu dots
- **Sub-header**: Back arrow, date/pause, family name, edit/share/stop buttons, member count
- **Left sidebar** (absolute): Double income, butler, mystery events, tasks, volcano escape, save bone spirit, chat
- **Right sidebar** (absolute): Computer science major, newbie rewards, other world gate
- **Center area**: Family tree with connected member nodes
- **Bottom bar** (fixed): 5 tab icons — inventory, achievements, family (active), help, trophies
- **Zoom control**: Bottom-right, minus/plus with percentage

## Risks / Trade-offs

- **[No real avatars]** → CSS/emoji placeholders won't look as polished as the cartoon art style in the reference. Mitigation: Use well-styled CSS circles with gradient backgrounds and expressive emoji to approximate the feel. Can be upgraded to actual images later.

- **[Placeholder side activities]** → Mini-games and events won't have real gameplay in v1. Mitigation: Show modal dialogs with descriptions and placeholder rewards so the UI is complete and clickable, even if the underlying systems are stubs.

- **[No offline progress]** → Unlike the reference game, currency won't accumulate when the tab is closed. Mitigation: On load, calculate elapsed time since last save and grant accumulated currency for the offline period.

- **[localStorage limits]** → If a user clears browser data, progress is lost. Mitigation: Add an export/import JSON feature for manual backup (low priority, post-v1).

- **[Single-file JS modules without ES modules]** → Using `<script>` tags in order means global scope pollution. Mitigation: Each file wraps its code in an IIFE or uses a namespace pattern (e.g., `window.Game.economy`). Keep the dependency order clear in the HTML script tags.
