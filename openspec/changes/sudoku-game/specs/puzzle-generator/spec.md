## ADDED Requirements

### Requirement: Generate a complete valid Sudoku grid
The system SHALL generate a fully filled 9x9 Sudoku grid where every row, column, and 3x3 box contains the digits 1-9 exactly once. The generation algorithm MUST use randomization so that each generated grid is different.

#### Scenario: Grid validity
- **WHEN** the system generates a complete grid
- **THEN** every row contains digits 1-9 exactly once
- **AND** every column contains digits 1-9 exactly once
- **AND** every 3x3 box contains digits 1-9 exactly once

#### Scenario: Randomized output
- **WHEN** the system generates two grids in sequence
- **THEN** the grids SHALL differ (with overwhelming probability)

### Requirement: Create a puzzle by removing cells
The system SHALL create a puzzle from a complete grid by removing cell values. The resulting puzzle MUST have exactly one valid solution.

#### Scenario: Unique solution
- **WHEN** the system creates a puzzle by removing cells from a complete grid
- **THEN** the puzzle SHALL have exactly one solution that matches the original complete grid

### Requirement: Support three difficulty levels
The system SHALL support three difficulty levels — easy, medium, and hard — that control how many cells are removed from the complete grid.

#### Scenario: Easy difficulty
- **WHEN** the difficulty is set to "easy"
- **THEN** the puzzle SHALL have between 36 and 40 empty cells

#### Scenario: Medium difficulty
- **WHEN** the difficulty is set to "medium"
- **THEN** the puzzle SHALL have between 41 and 50 empty cells

#### Scenario: Hard difficulty
- **WHEN** the difficulty is set to "hard"
- **THEN** the puzzle SHALL have between 51 and 55 empty cells

### Requirement: Solve a Sudoku puzzle
The system SHALL provide a solver function that can determine all solutions for a given puzzle state. The solver MUST be used during generation to verify uniqueness.

#### Scenario: Solving a valid puzzle
- **WHEN** the solver is given a puzzle with one solution
- **THEN** it SHALL return the correct completed grid

#### Scenario: Detecting multiple solutions
- **WHEN** the solver is given a puzzle with more than one solution
- **THEN** it SHALL detect that multiple solutions exist (used to reject invalid removals during generation)
