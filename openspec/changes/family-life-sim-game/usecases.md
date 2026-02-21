## Use Cases

### Use Case: Start a New Family

**Primary Actor:** Player
**Scope:** Family Life Sim Game
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to begin a new game session with a named family

**Preconditions:**
- Game is loaded in the browser with no existing save data (or player chose "new game")

**Success Guarantee (Postconditions):**
- A new family is created with a name, two initial parent members, and starting currency
- The game date is initialized
- The family tree is displayed with the two parents

**Trigger:** Player opens the game for the first time or selects "new game"

**Main Success Scenario:**
1. Player opens the game.
2. System detects no existing save data.
3. System prompts the player to enter a family name.
4. Player provides a family name (e.g., "姚家族").
5. System creates a family with two default parent members, starting currency (e.g., 1000), 0 diamonds, and an initial date.
6. System renders the family tree with both parents displayed as avatar nodes.
7. System starts the game loop (economy ticking, date advancing).

**Extensions:**
- 2a. Existing save data found: System loads the saved game state and skips to step 6.
- 4a. Player provides an empty name: System uses a default family name.

---

### Use Case: Earn Currency Passively

**Primary Actor:** Player (passive)
**Scope:** Family Life Sim Game — Idle Economy
**Level:** Subfunction

**Stakeholders and Interests:**
- Player — wants to accumulate wealth over time without active input

**Preconditions:**
- Game is running and not paused
- At least one family member has a positive income rate

**Success Guarantee (Postconditions):**
- Currency total increases by the net family income each second
- HUD displays the updated currency value and income rate

**Trigger:** Each 1-second game tick

**Main Success Scenario:**
1. System calculates net income by summing all family members' income/cost rates.
2. System adds the net income to the total currency.
3. System updates the currency display in the HUD with Chinese number formatting.
4. System updates the income rate display (e.g., "800/S").

**Extensions:**
- 1a. Net income is negative and currency would drop below zero: System sets currency to zero (cannot go negative).
- 1b. Game is paused: System skips the tick — no currency change.

---

### Use Case: View and Navigate the Family Tree

**Primary Actor:** Player
**Scope:** Family Life Sim Game — Family Tree
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to see the family structure and each member's stats

**Preconditions:**
- Game is running with at least one family member

**Success Guarantee (Postconditions):**
- Family tree is displayed with all members as connected avatar nodes
- Each node shows the member's avatar, level badge, and income/cost rate

**Trigger:** Player views the Family (家庭) tab (default view)

**Main Success Scenario:**
1. System renders parent nodes in the upper row, connected by a horizontal line.
2. System renders child nodes in the lower row, connected to parents by curved lines.
3. Each node displays a circular avatar, the member's level, and their income or cost rate label (e.g., "+350/S" or "-100/S").
4. Player taps on a family member node.
5. System displays the member's detail panel with full stats.

**Extensions:**
- 4a. Player uses zoom controls: System scales the tree view to the selected zoom percentage.
- 5a. No member is tapped: Tree remains in default view showing all nodes.

---

### Use Case: Add a Family Member

**Primary Actor:** Player
**Scope:** Family Life Sim Game — Family Members
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to grow the family to increase income or unlock content

**Preconditions:**
- Game is running
- Family has not reached the maximum member count

**Success Guarantee (Postconditions):**
- A new family member (child) is added to the family tree
- The member appears as a new node connected to their parents
- Family member count is updated (e.g., "人数: 3/4" → "人数: 4/4")

**Trigger:** Player initiates the "add member" action

**Main Success Scenario:**
1. Player selects the option to add a new family member.
2. System presents the new member with a random name, avatar, and initial attributes (level 0, cost rate of -100/S).
3. System adds the member to the family tree data.
4. System renders the new member node connected to the parent nodes.
5. System updates the family member count display.
6. System recalculates net income (new child costs -100/S).

**Extensions:**
- 1a. Family is at maximum capacity: System informs the player the family is full.
- 6a. Net income becomes negative: System continues; currency will decrease each tick.

---

### Use Case: Pause and Resume the Game

**Primary Actor:** Player
**Scope:** Family Life Sim Game — Time Progression
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to stop time progression temporarily

**Preconditions:**
- Game is running

**Success Guarantee (Postconditions):**
- Game pause state is toggled
- When paused, economy ticks and date progression stop; when resumed, they restart

**Trigger:** Player taps the pause/resume button next to the date display

**Main Success Scenario:**
1. Player taps the pause button.
2. System pauses the game loop — economy ticks stop, date stops advancing.
3. System updates the pause button to show a "resume" state.
4. Player taps the resume button.
5. System resumes the game loop — ticks and date progression restart.
6. System updates the button back to the "pause" state.

**Extensions:**
- 2a. Player navigates away while paused: System saves the paused state; on return, the game remains paused.

---

### Use Case: Progress Through In-Game Time

**Primary Actor:** System (automatic)
**Scope:** Family Life Sim Game — Time Progression
**Level:** Subfunction

**Stakeholders and Interests:**
- Player — wants to see the game world advance in time, providing a sense of progression

**Preconditions:**
- Game is running and not paused

**Success Guarantee (Postconditions):**
- In-game date advances by one day per tick interval
- Date display updates to reflect the new date

**Trigger:** Each game tick (1 second = 1 in-game day)

**Main Success Scenario:**
1. System advances the in-game date by one day.
2. System updates the date display in YYYY.MM.DD format.
3. System checks for any date-triggered events (e.g., milestones, random events).

**Extensions:**
- 1a. Date reaches end of month: System rolls over to the first day of the next month.
- 1b. Date reaches end of year: System rolls over to January 1 of the next year.
- 3a. A date-triggered event fires: System presents the event via the mystery events system.

---

### Use Case: Interact with Side Activities

**Primary Actor:** Player
**Scope:** Family Life Sim Game — Side Activities
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to engage with events and tasks for rewards or variety

**Preconditions:**
- Game is running
- The selected activity is available (not on cooldown or locked)

**Success Guarantee (Postconditions):**
- Player sees the activity content and receives any associated rewards

**Trigger:** Player taps a side activity button (e.g., 神秘事件, 任务, 火山逃生)

**Main Success Scenario:**
1. Player taps an activity button on the left or right sidebar.
2. System displays a modal dialog describing the activity.
3. System presents activity content (description, choices, or placeholder text for v1).
4. Player interacts with or dismisses the dialog.
5. System grants any rewards (currency, diamonds, buffs) and closes the dialog.

**Extensions:**
- 2a. Activity is locked or on cooldown: System shows a message indicating when it becomes available.
- 5a. Activity grants a buff (e.g., double income): System applies the buff for its duration and shows an indicator.

---

### Use Case: Switch Between Game Sections

**Primary Actor:** Player
**Scope:** Family Life Sim Game — Game UI
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants to access different parts of the game (inventory, achievements, family, help, trophies)

**Preconditions:**
- Game is loaded and running

**Success Guarantee (Postconditions):**
- The selected section is displayed
- The active tab is highlighted in the navigation bar

**Trigger:** Player taps a tab in the bottom navigation bar

**Main Success Scenario:**
1. Player taps a tab icon in the bottom navigation bar.
2. System highlights the selected tab as active.
3. System transitions the main content area to show the selected section's view.
4. The game loop continues running in the background regardless of which section is viewed.

**Extensions:**
- 3a. Section content is not yet implemented (v1): System shows a placeholder screen with the section name.

---

### Use Case: Save and Load Game Progress

**Primary Actor:** System (automatic) / Player (manual)
**Scope:** Family Life Sim Game — Game State
**Level:** User goal

**Stakeholders and Interests:**
- Player — wants game progress to persist across browser sessions

**Preconditions:**
- Game is running with an active game state

**Success Guarantee (Postconditions):**
- Game state is persisted to localStorage
- On reload, game resumes from the last saved state with offline earnings applied

**Trigger:** Auto-save every 30 seconds, on page unload, or manual save

**Main Success Scenario:**
1. System serializes the current game state to JSON.
2. System writes the JSON to localStorage.
3. Player closes or refreshes the browser.
4. Player reopens the game.
5. System detects saved data in localStorage.
6. System deserializes the game state and calculates offline earnings for the elapsed time.
7. System renders the game from the restored state with offline earnings added.

**Extensions:**
- 5a. No saved data found: System starts a new game (see "Start a New Family" use case).
- 6a. Saved data is corrupted or invalid: System warns the player and starts a new game.
- 6b. Elapsed offline time exceeds a cap (e.g., 24 hours): System grants earnings up to the cap.
