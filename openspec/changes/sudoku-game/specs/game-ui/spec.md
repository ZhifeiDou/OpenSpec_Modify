## ADDED Requirements

### Requirement: Display a 9x9 Sudoku grid
The system SHALL render a 9x9 grid in the browser with visible borders distinguishing the nine 3x3 boxes. Pre-filled cells MUST be visually distinct from empty (editable) cells.

#### Scenario: Initial grid rendering
- **WHEN** a new puzzle is loaded
- **THEN** the grid displays 81 cells arranged in a 9x9 layout
- **AND** 3x3 box boundaries are visually emphasized
- **AND** pre-filled cells show their digit and are not editable
- **AND** empty cells are editable

### Requirement: Cell selection and number input
The system SHALL allow the player to select an empty cell and enter a digit 1-9 via keyboard. Selecting a cell SHALL visually highlight the selected cell and its related row, column, and 3x3 box.

#### Scenario: Selecting an empty cell
- **WHEN** the player clicks an empty cell
- **THEN** the cell is highlighted as selected
- **AND** the corresponding row, column, and 3x3 box are subtly highlighted

#### Scenario: Entering a valid digit
- **WHEN** the player types a digit 1-9 while a cell is selected
- **THEN** the digit is placed in the selected cell

#### Scenario: Entering an invalid character
- **WHEN** the player types a character that is not 1-9
- **THEN** the input is ignored and the cell remains unchanged

#### Scenario: Selecting a pre-filled cell
- **WHEN** the player clicks a pre-filled cell
- **THEN** the cell does not become editable

#### Scenario: Clearing a cell
- **WHEN** the player presses Backspace or Delete on a player-entered cell
- **THEN** the digit is removed and the cell becomes empty

### Requirement: Real-time conflict highlighting
The system SHALL highlight conflicting cells in real-time whenever a player enters a digit that duplicates another digit in the same row, column, or 3x3 box.

#### Scenario: Conflict detected
- **WHEN** the player enters a digit that already exists in the same row, column, or 3x3 box
- **THEN** the conflicting cells (both the new entry and the existing duplicate) are highlighted with an error style

#### Scenario: Conflict resolved
- **WHEN** the player changes or clears a digit that was causing a conflict
- **THEN** the error highlighting is removed from all previously conflicting cells (if no other conflicts remain)

### Requirement: Difficulty selector
The system SHALL provide a control for the player to select a difficulty level (easy, medium, hard) before starting a new game.

#### Scenario: Selecting difficulty
- **WHEN** the player selects a difficulty level and starts a new game
- **THEN** the generated puzzle reflects the chosen difficulty (number of empty cells)

### Requirement: Game timer
The system SHALL display a running timer that starts at 00:00 when a new game begins and counts up in seconds.

#### Scenario: Timer starts on new game
- **WHEN** a new puzzle is displayed
- **THEN** the timer starts at 00:00 and increments every second

#### Scenario: Timer stops on successful check
- **WHEN** the player checks the solution and it is correct
- **THEN** the timer stops and the final time is displayed

### Requirement: New game control
The system SHALL provide a "New Game" control that generates and displays a fresh puzzle at the currently selected difficulty.

#### Scenario: Starting a new game
- **WHEN** the player activates "New Game"
- **THEN** a new puzzle is generated at the selected difficulty
- **AND** the grid is refreshed and the timer resets to 00:00

### Requirement: Reset control
The system SHALL provide a "Reset" control that clears all player-entered digits while preserving the original pre-filled cells.

#### Scenario: Resetting the puzzle
- **WHEN** the player activates "Reset"
- **THEN** all player-entered digits are cleared
- **AND** pre-filled cells remain unchanged
- **AND** the timer resets to 00:00
- **AND** all conflict highlighting is cleared

### Requirement: Check solution control
The system SHALL provide a "Check" control that validates the current grid state.

#### Scenario: Correct and complete solution
- **WHEN** the player activates "Check" and all cells are filled correctly
- **THEN** a success message is displayed and the timer stops

#### Scenario: Incomplete puzzle
- **WHEN** the player activates "Check" and not all cells are filled
- **THEN** the system notifies the player that the puzzle is incomplete

#### Scenario: Incorrect solution
- **WHEN** the player activates "Check" and the grid contains errors
- **THEN** the system highlights the incorrect cells
