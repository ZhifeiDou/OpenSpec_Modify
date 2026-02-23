## ADDED Requirements

### Requirement: Activity buttons layout
The system SHALL display activity buttons along the left and right edges of the main screen. Left-side activities SHALL include: 双倍收入 (Double Income), 管家 (Butler), 神秘事件 (Mystery Events), 任务 (Tasks), 火山逃生 (Volcano Escape), 救救白骨精 (Save Bone Spirit). Right-side activities SHALL include: 计算机专业 (Computer Science), 新手奖励 (Newbie Rewards), 异世界大门 (Other World Gate).

#### Scenario: Activity buttons visible on family screen
- **WHEN** the player is on the Family (家庭) tab
- **THEN** all activity buttons are visible along the left and right screen edges with icons and Chinese labels

### Requirement: Activity button interaction
Each activity button SHALL be tappable. Tapping a button SHALL open a modal dialog with the activity's content. In v1, activities that are not fully implemented SHALL display a placeholder description.

#### Scenario: Tapping an implemented activity
- **WHEN** the player taps the 神秘事件 (Mystery Events) button
- **THEN** a modal dialog opens with the event content

#### Scenario: Tapping a placeholder activity
- **WHEN** the player taps the 火山逃生 (Volcano Escape) button
- **THEN** a modal dialog opens with a placeholder message indicating the activity is coming soon

### Requirement: Mystery events system
The system SHALL provide random mystery events that the player can trigger. Each event SHALL present a short narrative and a reward (currency or diamonds). Events SHALL be drawn from a predefined pool.

#### Scenario: Triggering a mystery event
- **WHEN** the player opens a mystery event
- **THEN** the system selects a random event from the pool and displays its narrative and reward

#### Scenario: Claiming event reward
- **WHEN** the player confirms/claims the event reward
- **THEN** the reward is added to the player's currency or diamonds and the dialog closes

### Requirement: Tasks/quests system
The system SHALL provide a list of tasks (任务) that award currency or diamonds upon completion. Tasks SHALL have descriptions and completion conditions. Completed tasks SHALL be marked as done.

#### Scenario: Viewing tasks
- **WHEN** the player opens the tasks panel
- **THEN** a list of available and completed tasks is displayed

#### Scenario: Completing a task
- **WHEN** the player meets a task's completion condition
- **THEN** the task is marked as complete and the reward is granted

### Requirement: Newbie rewards
The system SHALL provide a set of one-time newbie rewards (新手奖励) for new players. These rewards SHALL be claimable from the right sidebar button and grant currency or diamonds.

#### Scenario: Claiming newbie reward
- **WHEN** a new player taps the newbie rewards button
- **THEN** the system displays available one-time rewards that can be claimed

#### Scenario: All newbie rewards claimed
- **WHEN** all newbie rewards have been claimed
- **THEN** the newbie rewards button shows a "completed" state

### Requirement: Butler system
The system SHALL provide a butler (管家) feature accessible from the left sidebar. The butler SHALL provide gameplay tips or auto-management suggestions to the player.

#### Scenario: Opening butler
- **WHEN** the player taps the butler button
- **THEN** a dialog opens with butler advice or management options
