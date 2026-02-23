## Why

We want to build a family life simulation idle game (inspired by 游戏人生 / "Game of Life") as a web-based application. The game combines idle/incremental mechanics with family management and life simulation, where players grow a family, earn currency passively, and engage with events and activities. This is a new project built from scratch.

## What Changes

- Create a complete web-based family life simulation idle game
- Implement a **family tree system** where family members are visually connected in a tree layout, each with avatar, level, and income/cost rate per second
- Implement an **idle economy engine** with currency (coins) accumulating per second based on net family income, plus a premium currency (diamonds)
- Implement a **time/date progression system** that advances the in-game date, with pause/resume controls
- Implement **family member management** — adding members (parents, children), each with distinct income (+X/S) or cost (-X/S) attributes and levels
- Implement a **side activities panel** with events, tasks, and mini-games accessible from the main screen
- Implement a **bottom navigation bar** for switching between game sections (inventory, achievements, family/home, help, trophies)
- Implement a **top HUD** showing total currency, income rate, diamond count, and date
- Create a responsive mobile-first UI with a soft, colorful art style

## Capabilities

### New Capabilities

- `family-tree`: Family tree data model and visual tree layout — adding/removing members, parent-child relationships, displaying members as circular avatar nodes connected by lines
- `idle-economy`: Core idle/incremental economy engine — currency accumulation per second, net income calculation from all family members, premium currency (diamonds), and currency display formatting (e.g., 7.21万)
- `family-members`: Individual family member system — member attributes (name, avatar, level, income/cost rate), leveling up, and per-member stats display (+350/S, -100/S)
- `time-progression`: In-game date/time system — date advances over time, pause/resume toggle, date display (YYYY.MM.DD format)
- `side-activities`: Side panel activities — mystery events, tasks/quests, mini-games (volcano escape, etc.), and activity button UI along the screen edges
- `game-ui`: Main game UI shell — top HUD (currency, diamonds, income rate), bottom navigation bar (5 tabs), zoom controls, background scenery, and responsive mobile-first layout
- `game-state`: Core game state management — save/load game, initializing a new family, game loop (tick-based updates), and overall state coordination

### Modified Capabilities

_(none — this is a new project with no existing specs)_

## Impact

- **New project**: All code is new; no existing codebase is affected
- **Technology**: Web-based (HTML/CSS/JavaScript) — intended to run in a browser, mobile-first responsive design
- **Dependencies**: Minimal external dependencies; may use a lightweight framework (e.g., vanilla JS or a small library) for state management and rendering
- **Assets**: Will need placeholder avatar images/icons for family members, activity buttons, and currency icons
- **Target**: `testing_project_youxirensheng/` directory as the project output folder
