## ADDED Requirements

### Requirement: Currency accumulation per tick
The system SHALL add the net family income to the player's total currency once per second (each game tick). Net income is the sum of all family members' individual income/cost rates.

#### Scenario: Positive net income
- **WHEN** a game tick occurs and net family income is +800/S
- **THEN** the total currency increases by 800

#### Scenario: Negative net income with sufficient funds
- **WHEN** a game tick occurs, net income is -200/S, and total currency is 1000
- **THEN** the total currency decreases to 800

#### Scenario: Negative net income with insufficient funds
- **WHEN** a game tick occurs, net income is -200/S, and total currency is 50
- **THEN** the total currency is set to 0 (SHALL NOT go below zero)

### Requirement: Currency display with Chinese formatting
The system SHALL display currency values using Chinese number units. Values ≥ 10,000 SHALL display as `X.XX万`. Values ≥ 100,000,000 SHALL display as `X.XX亿`. Values below 10,000 SHALL display as the raw integer.

#### Scenario: Value in wan range
- **WHEN** the total currency is 72,100
- **THEN** it displays as "7.21万"

#### Scenario: Value below wan threshold
- **WHEN** the total currency is 5,000
- **THEN** it displays as "5000"

#### Scenario: Value in yi range
- **WHEN** the total currency is 350,000,000
- **THEN** it displays as "3.50亿"

### Requirement: Income rate display
The system SHALL display the total net income rate in the top HUD as "X/S" (e.g., "800/S"). This value SHALL update whenever a family member is added, removed, or their rate changes.

#### Scenario: Income rate in HUD
- **WHEN** family members have rates of +350/S, +650/S, -100/S, -100/S
- **THEN** the HUD displays "800/S" as the net income rate

### Requirement: Premium currency (diamonds)
The system SHALL maintain a diamond count as a separate premium currency. Diamonds SHALL be displayed in the top HUD next to a diamond icon. Diamonds SHALL be earned through activities and events, not through idle accumulation.

#### Scenario: Diamond display
- **WHEN** the player has 3 diamonds
- **THEN** the HUD shows a diamond icon with the number "3"

#### Scenario: Earning diamonds
- **WHEN** an activity or event awards 2 diamonds
- **THEN** the diamond count increases by 2 and the display updates

### Requirement: Double income buff
The system SHALL support a "double income" (双倍收入) buff that multiplies all positive income rates by 2 for a limited duration. The buff SHALL be indicated by a button/icon on the left sidebar showing the multiplier.

#### Scenario: Double income active
- **WHEN** the double income buff is active with multiplier x2
- **THEN** all positive member income rates are doubled in the net income calculation

#### Scenario: Double income expires
- **WHEN** the double income buff duration ends
- **THEN** income rates return to normal values
