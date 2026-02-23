## Use Cases

### Use Case: Play a new Sudoku puzzle

**Primary Actor:** Player
**Scope:** Sudoku Game Web Application
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants an enjoyable, correctly generated puzzle at their chosen difficulty

**Preconditions:**
- The game is running and accessible in the browser via localhost

**Success Guarantee (Postconditions):**
- A new valid Sudoku puzzle is displayed with the appropriate number of pre-filled cells for the selected difficulty
- Timer is reset and running
- The grid is interactive and ready for input

**Trigger:** Player selects a difficulty level and requests a new game

**Main Success Scenario:**
1. Player selects a difficulty level (easy, medium, or hard).
2. Player requests a new game.
3. System generates a valid 9x9 Sudoku puzzle with a unique solution.
4. System removes cells according to the chosen difficulty level.
5. System displays the puzzle grid with pre-filled cells locked and empty cells editable.
6. System starts the timer at 00:00.

**Extensions:**
- 3a. Generation takes too long: System uses a fallback pre-built puzzle for the requested difficulty.

**Open Questions:**
- None

---

### Use Case: Solve the puzzle by entering numbers

**Primary Actor:** Player
**Scope:** Sudoku Game Web Application
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to fill in numbers and receive immediate feedback on conflicts

**Preconditions:**
- A puzzle is displayed with empty cells available for input

**Success Guarantee (Postconditions):**
- The selected cell contains the player's chosen number
- Any conflicts with the same row, column, or 3x3 box are visually highlighted

**Trigger:** Player selects an empty cell and enters a number

**Main Success Scenario:**
1. Player selects an empty cell on the grid.
2. System highlights the selected cell and its row, column, and box.
3. Player enters a number (1-9).
4. System places the number in the cell.
5. System checks for conflicts against the same row, column, and 3x3 box.
6. System displays the cell without conflict styling (no duplicates found).

**Extensions:**
- 1a. Player selects a pre-filled (locked) cell: System indicates the cell is not editable. Player selects a different cell.
- 3a. Player enters an invalid character (not 1-9): System ignores the input.
- 5a. A conflict is detected: System highlights the conflicting cells so the player can see the duplication.
- 3b. Player clears the cell (backspace/delete): System removes the number and clears any conflict highlighting related to that cell.

**Open Questions:**
- None

---

### Use Case: Check the completed solution

**Primary Actor:** Player
**Scope:** Sudoku Game Web Application
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to know whether their completed puzzle is correct

**Preconditions:**
- All 81 cells contain a number

**Success Guarantee (Postconditions):**
- Player knows whether the solution is correct or has errors

**Trigger:** Player requests a solution check

**Main Success Scenario:**
1. Player requests to check the solution.
2. System verifies every row, column, and 3x3 box contains the digits 1-9 exactly once.
3. System displays a success message and stops the timer, showing the final time.

**Extensions:**
- 1a. Not all cells are filled: System notifies the player that the puzzle is incomplete.
- 2a. Solution has errors: System highlights the incorrect cells and prompts the player to continue.

**Open Questions:**
- None

---

### Use Case: Reset the current puzzle

**Primary Actor:** Player
**Scope:** Sudoku Game Web Application
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to start over on the same puzzle without generating a new one

**Preconditions:**
- A puzzle is currently in progress with at least one player-entered number

**Success Guarantee (Postconditions):**
- All player-entered numbers are cleared; pre-filled cells remain
- Timer is reset to 00:00 and restarted

**Trigger:** Player requests a reset

**Main Success Scenario:**
1. Player requests to reset the puzzle.
2. System clears all player-entered numbers from the grid.
3. System keeps the original pre-filled cells intact.
4. System resets the timer to 00:00 and restarts it.
5. System clears all conflict highlighting.

**Extensions:**
- None

**Open Questions:**
- None

---

### Use Case: Start the game server

**Primary Actor:** Developer/Player
**Scope:** Sudoku Game Server
**Level:** Subfunction

**Stakeholders and Interests:**
- Developer/Player — wants to launch the game locally with a single command

**Preconditions:**
- Node.js or Python is installed on the machine
- The game files exist in `testing_project/`

**Success Guarantee (Postconditions):**
- The HTTP server is running and serving the game on a localhost port
- The player can open the game in a browser

**Trigger:** User runs the server start command

**Main Success Scenario:**
1. User runs the start command from the `testing_project/` directory.
2. System starts an HTTP server on a default port (e.g., 3000).
3. System logs the URL where the game is accessible.
4. User opens the URL in a browser.
5. System serves the game files and the player sees the Sudoku interface.

**Extensions:**
- 2a. Default port is already in use: System logs an error and suggests using a different port.

**Open Questions:**
- None
