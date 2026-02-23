## 1. Project Setup

- [x] 1.1 Create `testing_project/` directory structure with `index.html`, `style.css`, `sudoku.js`, `server.js`

## 2. Puzzle Generator

- [x] 2.1 Implement backtracking Sudoku solver that can find solutions and detect multiple solutions
- [x] 2.2 Implement complete grid generator using randomized backtracking to fill a valid 9x9 grid
- [x] 2.3 Implement puzzle creator that removes cells from a complete grid while verifying unique solvability
- [x] 2.4 Implement difficulty levels — easy (36-40 empties), medium (41-50 empties), hard (51-55 empties)

## 3. Game UI — Grid and Input

- [x] 3.1 Build the 9x9 CSS Grid layout with 3x3 box borders in `style.css`
- [x] 3.2 Render puzzle to the grid — pre-filled cells locked, empty cells as editable inputs
- [x] 3.3 Implement cell selection — click to select, highlight selected cell's row, column, and box
- [x] 3.4 Implement keyboard input — accept digits 1-9, ignore invalid characters, backspace/delete to clear

## 4. Game UI — Conflict Detection

- [x] 4.1 Implement real-time conflict checking — scan row, column, and 3x3 box on each input change
- [x] 4.2 Add conflict highlighting CSS styles — mark conflicting cells with error styling
- [x] 4.3 Clear conflict highlighting when conflicts are resolved (cell changed or cleared)

## 5. Game UI — Controls and Timer

- [x] 5.1 Add difficulty selector (easy/medium/hard dropdown or buttons)
- [x] 5.2 Implement game timer — starts at 00:00 on new game, counts up each second, displays MM:SS
- [x] 5.3 Implement "New Game" button — generates fresh puzzle at selected difficulty, resets timer
- [x] 5.4 Implement "Reset" button — clears player-entered digits, keeps pre-filled cells, resets timer
- [x] 5.5 Implement "Check" button — validates solution, shows success/incomplete/error feedback, stops timer on success

## 6. Server

- [x] 6.1 Create `server.js` using Node.js built-in `http`, `fs`, `path` modules
- [x] 6.2 Serve static files from `testing_project/` with correct MIME types (html, css, js)
- [x] 6.3 Default to port 3000 with error message if port is in use
- [x] 6.4 Log the localhost URL on successful startup

## 7. Integration and Polish

- [x] 7.1 Wire up all UI controls to puzzle generator and game logic
- [x] 7.2 Verify end-to-end flow: start server, open browser, play a full game at each difficulty
- [x] 7.3 Style polish — clean layout, readable fonts, responsive sizing for desktop
