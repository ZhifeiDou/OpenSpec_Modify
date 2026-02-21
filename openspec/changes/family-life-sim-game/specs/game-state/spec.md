## ADDED Requirements

### Requirement: Central game state object
The system SHALL maintain a single central game state object containing: family name, total currency, diamond count, in-game date, pause state, family members array, activity states, settings (zoom level), and last-save timestamp.

#### Scenario: State structure on new game
- **WHEN** a new game is initialized
- **THEN** the game state contains a family name, starting currency, 0 diamonds, a starting date, isPaused=false, two parent members, and default settings

### Requirement: New game initialization
The system SHALL initialize a new game when no saved data exists or when the player starts a new game. Initialization SHALL prompt for a family name, create two default parent members, set starting currency, and set the starting date.

#### Scenario: First time launch
- **WHEN** the player opens the game with no localStorage data
- **THEN** the system prompts for a family name and creates a new game with default values

#### Scenario: New game after reset
- **WHEN** the player confirms ending the current game
- **THEN** localStorage is cleared and a new game initialization begins

### Requirement: Auto-save to localStorage
The system SHALL automatically save the game state to localStorage every 30 seconds while the game is running. The system SHALL also save on page beforeunload (tab close/refresh).

#### Scenario: Auto-save interval
- **WHEN** 30 seconds have elapsed since the last save
- **THEN** the current game state is serialized to JSON and written to localStorage

#### Scenario: Save on page close
- **WHEN** the player closes or refreshes the browser tab
- **THEN** the game state is saved to localStorage before the page unloads

### Requirement: Load saved game
The system SHALL check localStorage for saved game data on startup. If valid data exists, the system SHALL deserialize it and restore the game state.

#### Scenario: Loading valid save
- **WHEN** the game starts and valid JSON exists in localStorage
- **THEN** the game state is restored from the saved data

#### Scenario: Corrupted save data
- **WHEN** the game starts and localStorage contains invalid JSON
- **THEN** the system discards the corrupted data and starts a new game

### Requirement: Offline earnings calculation
The system SHALL calculate offline earnings when loading a saved game. The elapsed time between the last-save timestamp and the current time SHALL be used to compute accumulated currency (net income × elapsed seconds), capped at a maximum of 24 hours (86,400 seconds).

#### Scenario: Returning after 1 hour
- **WHEN** the player returns after 3,600 seconds with a net income of 800/S
- **THEN** the system grants 2,880,000 currency (800 × 3600) as offline earnings

#### Scenario: Returning after more than 24 hours
- **WHEN** the player returns after 48 hours with a net income of 800/S
- **THEN** the system grants earnings for only 24 hours (800 × 86400 = 69,120,000)

#### Scenario: Game was paused when saved
- **WHEN** the player returns and the saved state has isPaused=true
- **THEN** no offline earnings are granted (game was paused)

### Requirement: Game loop coordination
The system SHALL run a main game loop using a 1-second interval timer. Each tick SHALL: advance the in-game date, calculate and apply income, update the UI, and increment the tick counter. The loop SHALL respect the pause state.

#### Scenario: Normal tick
- **WHEN** the game is running and not paused
- **THEN** each second the date advances, currency updates, and the UI re-renders

#### Scenario: Paused tick
- **WHEN** the game is paused
- **THEN** the tick interval continues but no state changes occur

### Requirement: Render cycle
The system SHALL provide a render function that updates all DOM elements to reflect the current game state. The render function SHALL be called after each tick and after any user action that modifies state.

#### Scenario: State change triggers render
- **WHEN** the player levels up a family member
- **THEN** the render function updates the member's level badge and income rate display immediately
