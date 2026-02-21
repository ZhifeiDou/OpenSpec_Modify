## ADDED Requirements

### Requirement: Top HUD bar
The system SHALL display a fixed top bar containing: a currency pill (green background with currency icon, formatted value, and "/S" income rate), a diamond counter (diamond icon + count), and a "+" button for acquiring more diamonds. A "..." menu button SHALL be at the far right.

#### Scenario: Currency pill display
- **WHEN** the player has 72,100 currency with 800/S net income
- **THEN** the top bar shows a green pill with "7.21万" and "800/S" below it

#### Scenario: Diamond counter display
- **WHEN** the player has 3 diamonds
- **THEN** the top bar shows a diamond icon with "3" next to it

### Requirement: Sub-header area
The system SHALL display a sub-header below the top HUD containing: a back arrow button (left), the pause/date display, the family name (large centered text, e.g., "姚家族"), edit/share/stop action buttons, and the member count ("人数: X/Y").

#### Scenario: Family name and controls
- **WHEN** the family is named "姚家族" with 4/4 members
- **THEN** the sub-header shows "姚家族" centered, with "人数: 4/4" below it, and edit (pencil), share, and stop (终止) buttons to the right

### Requirement: Bottom navigation bar
The system SHALL display a fixed bottom navigation bar with 5 tab icons. The tabs SHALL be, left to right: inventory (box icon), achievements (star/medal icon), family/home (heart house icon, labeled "家庭"), help (question mark icon), and trophies (trophy icon). The active tab SHALL be visually highlighted.

#### Scenario: Family tab active
- **WHEN** the player is on the family screen
- **THEN** the "家庭" tab is highlighted with an accent color and the other tabs are dimmed

#### Scenario: Switching tabs
- **WHEN** the player taps the trophies tab
- **THEN** the trophies tab becomes highlighted and the main content area switches to the trophies section

### Requirement: Mobile-first responsive layout
The system SHALL use a mobile-first layout optimized for portrait phone screens (360-414px width). The layout SHALL use CSS Grid with three rows: fixed top HUD, scrollable/zoomable main area, fixed bottom nav bar. All text and UI elements SHALL be sized for touch interaction (minimum 44px tap targets).

#### Scenario: Phone viewport
- **WHEN** the game is opened on a 390px wide viewport
- **THEN** all UI elements fit within the viewport, no horizontal scrolling occurs, and buttons are easily tappable

#### Scenario: Larger viewport
- **WHEN** the game is opened on a desktop browser
- **THEN** the game centers in the viewport with a max-width container, maintaining the mobile layout

### Requirement: Background scenery
The system SHALL display a soft gradient background with subtle mountain/landscape silhouettes behind the family tree area, matching the reference's calm, light blue-green aesthetic.

#### Scenario: Background rendering
- **WHEN** the family screen is displayed
- **THEN** a light blue-green gradient background with faint mountain shapes is visible behind the family tree

### Requirement: Modal dialog system
The system SHALL provide a reusable modal dialog component for activities, events, and member details. The modal SHALL have a semi-transparent backdrop, a centered content panel, and a close/dismiss button.

#### Scenario: Opening a modal
- **WHEN** an activity or event triggers a modal
- **THEN** a semi-transparent overlay covers the screen and a centered panel displays the content

#### Scenario: Closing a modal
- **WHEN** the player taps the close button or the backdrop
- **THEN** the modal closes and the player returns to the main view

### Requirement: Family name editing
The system SHALL allow the player to rename their family by tapping the edit (pencil) button next to the family name. A text input SHALL appear allowing the player to type a new name and confirm.

#### Scenario: Renaming the family
- **WHEN** the player taps the edit button, types "王家族", and confirms
- **THEN** the family name updates to "王家族" in the sub-header and in the game state

### Requirement: Stop/end game button
The system SHALL display a stop button (终止) in the sub-header. Tapping it SHALL prompt for confirmation before ending the current game and resetting to a new game state.

#### Scenario: Ending the game
- **WHEN** the player taps the stop button and confirms
- **THEN** the current game state is cleared and a new game initialization begins
