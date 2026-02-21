## ADDED Requirements

### Requirement: In-game date system
The system SHALL maintain an in-game date consisting of year, month, and day. The date SHALL advance by one day per game tick (1 second of real time). The date SHALL be displayed in YYYY.MM.DD format (e.g., "2024.09.06").

#### Scenario: Date advances each tick
- **WHEN** the current date is 2024.09.06 and a game tick occurs
- **THEN** the date becomes 2024.09.07

#### Scenario: Month rollover
- **WHEN** the current date is 2024.09.30 and a game tick occurs
- **THEN** the date becomes 2024.10.01

#### Scenario: Year rollover
- **WHEN** the current date is 2024.12.31 and a game tick occurs
- **THEN** the date becomes 2025.01.01

### Requirement: Date display in UI
The system SHALL display the current in-game date in the sub-header area, preceded by a pause/play icon. The format SHALL be YYYY.MM.DD.

#### Scenario: Date rendering
- **WHEN** the in-game date is September 6, 2024
- **THEN** the UI displays "2024.09.06" with a pause icon to its left

### Requirement: Pause and resume
The system SHALL provide a pause/resume toggle button adjacent to the date display. When paused, the game tick SHALL stop — no currency accumulation, no date advancement. When resumed, ticks SHALL restart.

#### Scenario: Pausing the game
- **WHEN** the player taps the pause button while the game is running
- **THEN** the game loop stops, the button changes to a play/resume icon, and the date and currency freeze

#### Scenario: Resuming the game
- **WHEN** the player taps the resume button while the game is paused
- **THEN** the game loop restarts, the button changes back to a pause icon, and ticks resume

### Requirement: Pause state persistence
The system SHALL save the paused/running state as part of the game state. If the game was paused when saved, it SHALL remain paused when loaded.

#### Scenario: Save while paused
- **WHEN** the game is paused and auto-saved, then the page is reloaded
- **THEN** the game loads in a paused state

### Requirement: Calendar correctness
The date system SHALL correctly handle months with different day counts (28/29/30/31 days). February SHALL have 28 days in non-leap years and 29 days in leap years.

#### Scenario: February in a leap year
- **WHEN** the date is 2024.02.28 (leap year) and a tick occurs
- **THEN** the date becomes 2024.02.29

#### Scenario: February in a non-leap year
- **WHEN** the date is 2025.02.28 (non-leap year) and a tick occurs
- **THEN** the date becomes 2025.03.01
