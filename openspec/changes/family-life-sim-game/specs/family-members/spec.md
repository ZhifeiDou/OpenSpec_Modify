## ADDED Requirements

### Requirement: Family member attributes
Each family member SHALL have the following attributes: unique ID, name, role (parent or child), avatar identifier (emoji or style key), level (integer starting at 0 or 1), income rate per second (positive for earners, negative for dependents), and a parent generation link.

#### Scenario: Parent member attributes
- **WHEN** a parent member is created
- **THEN** it has a role of "parent", a positive income rate (e.g., +350/S), and a level ≥ 1

#### Scenario: Child member attributes
- **WHEN** a child member is created
- **THEN** it has a role of "child", a negative cost rate (e.g., -100/S), and a level of 0

### Requirement: Default starting family
The system SHALL create two default parent members when a new game starts. The first parent (father) SHALL have an initial income rate and the second parent (mother) SHALL have an initial income rate. Both SHALL start at level 1.

#### Scenario: New game family
- **WHEN** a new game is initialized
- **THEN** two parent members exist with positive income rates and level 1

### Requirement: Family member count and capacity
The system SHALL enforce a maximum family member count. The current count and maximum SHALL be displayed as "人数: X/Y" below the family name. Players SHALL NOT be able to add members beyond the maximum.

#### Scenario: Display member count
- **WHEN** the family has 4 members and maximum is 4
- **THEN** the display shows "人数: 4/4"

#### Scenario: Family at capacity
- **WHEN** the player attempts to add a member and the family is at maximum capacity
- **THEN** the system prevents the addition and informs the player

### Requirement: Member level system
Each family member SHALL have a level that can increase. Leveling up a member SHALL increase their income rate (for earners) or decrease their cost rate (for dependents). The level SHALL be displayed as a small badge on the member's tree node.

#### Scenario: Level up an earner
- **WHEN** a parent member at level 24 with +350/S is leveled up
- **THEN** the member's level becomes 25 and income rate increases

#### Scenario: Level badge display
- **WHEN** a member has level 24
- **THEN** a circular badge with "24" is shown on their tree node

### Requirement: Member avatar display
Each family member SHALL be displayed with a circular avatar. The avatar border color SHALL indicate the member's role or gender (e.g., blue border for male, pink border for female). The avatar content SHALL be an emoji face or styled initial.

#### Scenario: Male parent avatar
- **WHEN** a male parent member is displayed
- **THEN** the avatar has a blue-toned circular border with an appropriate emoji or icon

#### Scenario: Female child avatar
- **WHEN** a female child member is displayed
- **THEN** the avatar has a pink-toned circular border with an appropriate emoji or icon
