## Context

This is a greenfield project — no existing code in `testing_project/`. The game must be a self-contained web application served on localhost with zero external runtime dependencies. The target is a simple, single-player Sudoku game that runs in any modern browser.

Constraints:
- Pure HTML/CSS/JavaScript — no frameworks, no build tools, no npm packages at runtime
- Single-page application served as static files
- Must work offline once loaded (no API calls)
- Server is only needed for serving static files

## Goals / Non-Goals

**Goals:**
- Playable Sudoku with correct puzzle generation (unique solutions)
- Three difficulty levels (easy, medium, hard)
- Real-time conflict detection
- Clean, responsive UI that works on desktop browsers
- One-command server startup

**Non-Goals:**
- Mobile-optimized touch interface
- Multiplayer or leaderboards
- Puzzle saving/persistence across sessions
- User accounts or authentication
- Pencil marks / candidate notation
- Undo/redo history

## Decisions

### 1. Single HTML file vs. separate files

**Decision:** Separate files — `index.html`, `style.css`, `sudoku.js`, `server.js`

**Rationale:** Separate files keep concerns clear and are easier to maintain. A single HTML file would work but mixes markup, styles, and logic. Since we have a server anyway, there's no benefit to inlining everything.

**Alternatives considered:**
- Single HTML file with embedded CSS/JS — simpler to distribute but harder to read and edit

### 2. Puzzle generation approach

**Decision:** Backtracking solver that generates a complete grid, then removes cells while verifying unique solvability.

**Rationale:** This is the standard, well-understood approach for Sudoku generation:
1. Fill the grid using a randomized backtracking algorithm
2. Remove cells one at a time in random order
3. After each removal, verify the puzzle still has exactly one solution (run solver — if it finds >1 solution, restore the cell)
4. Stop removing when the target number of empty cells is reached

**Alternatives considered:**
- Pre-built puzzle bank — simpler but limited variety
- Pattern-based generation — faster but doesn't guarantee unique solutions

**Difficulty mapping (approximate empty cells):**
- Easy: 36-40 empty cells
- Medium: 41-50 empty cells
- Hard: 51-55 empty cells

### 3. Server technology

**Decision:** Node.js with built-in `http` and `fs` modules (zero dependencies).

**Rationale:** Node.js is the most likely runtime already installed on a developer's machine. Using only built-in modules means no `npm install` step — just `node server.js`. Falls back cleanly if the port is busy.

**Alternatives considered:**
- Python `http.server` — also zero-dependency, but Node is more natural for a JS project
- Express.js — adds an npm dependency for no real benefit when serving static files

### 4. UI layout and interaction

**Decision:** CSS Grid for the 9x9 board. Click to select a cell, then type a number. Keyboard-only input (no on-screen number pad).

**Rationale:** CSS Grid maps naturally to a 9x9 Sudoku board with 3x3 box borders. Keyboard input is the fastest interaction model for desktop. Each cell is an `<input>` element with `maxlength="1"`, making validation straightforward.

**Alternatives considered:**
- `<table>` layout — semantically odd, harder to style the 3x3 box borders
- On-screen number buttons — adds complexity, slower for desktop users

### 5. Conflict detection strategy

**Decision:** On every input change, scan the affected row, column, and 3x3 box for duplicates. Add a CSS class to all conflicting cells.

**Rationale:** With only 81 cells, scanning is instant. No need for incremental tracking or complex data structures. Re-scan on every change keeps the logic simple and stateless.

## Risks / Trade-offs

- **[Puzzle generation speed]** Backtracking with uniqueness verification can be slow for hard puzzles (many removals to test). → Mitigation: Set a maximum attempt count; if exceeded, reduce removals slightly. In practice, generation under 1 second is typical for browser JS.
- **[No mobile support]** Keyboard-only input doesn't work well on phones. → Accepted as a non-goal. Desktop browser is the target.
- **[No persistence]** Refreshing the page loses progress. → Accepted as a non-goal for this version. Could add `localStorage` later.
