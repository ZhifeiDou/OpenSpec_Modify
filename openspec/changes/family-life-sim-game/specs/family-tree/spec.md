## ADDED Requirements

### Requirement: Family tree data model
The system SHALL maintain a tree data structure representing family relationships. Each member node SHALL store a reference to its parent node(s). The tree SHALL support a two-generation hierarchy: parents (generation 0) and children (generation 1).

#### Scenario: Initial family tree structure
- **WHEN** a new game is started
- **THEN** the family tree contains exactly two parent nodes at generation 0 with no children

#### Scenario: Adding a child to the tree
- **WHEN** a new child member is added
- **THEN** the child node is linked to both parent nodes and placed at generation 1

### Requirement: Family tree visual layout
The system SHALL render the family tree as a visual node graph in the center of the main game area. Parent nodes SHALL be positioned in an upper row. Child nodes SHALL be positioned in a lower row below the parents.

#### Scenario: Rendering parents
- **WHEN** the family tree is displayed
- **THEN** parent member nodes are rendered side by side in the upper-center area of the screen

#### Scenario: Rendering children
- **WHEN** the family tree has children
- **THEN** child member nodes are rendered in a row below the parents, spaced evenly

### Requirement: Family tree connector lines
The system SHALL draw curved connector lines (SVG paths) between parent nodes and their child nodes. A single line SHALL connect the parents horizontally, and branching lines SHALL extend downward from the parent pair to each child.

#### Scenario: Parent-to-child connections
- **WHEN** the family tree has at least one child
- **THEN** SVG curved lines connect the parent pair to each child node

#### Scenario: No children
- **WHEN** the family has only parents and no children
- **THEN** only a horizontal connector line between the two parents is displayed

### Requirement: Family member node display
Each family member node SHALL be rendered as a circular avatar container. The node SHALL display: the member's avatar (emoji or styled initial), a level badge (small circle with level number), and an income/cost rate label below the node (e.g., "+350/S" or "-100/S").

#### Scenario: Node with positive income
- **WHEN** a member has a positive income rate
- **THEN** the rate label displays in green with a "+" prefix (e.g., "+350/S")

#### Scenario: Node with negative cost
- **WHEN** a member has a negative cost rate
- **THEN** the rate label displays in red with a "-" prefix (e.g., "-100/S")

### Requirement: Family member node interaction
The system SHALL allow the player to tap/click on a family member node. Tapping a node SHALL display a detail panel or highlight for that member.

#### Scenario: Tapping a member node
- **WHEN** the player taps a family member node
- **THEN** the system displays that member's detail information (name, level, full stats)

### Requirement: Family tree zoom
The system SHALL provide zoom controls (minus button, plus button, percentage display) at the bottom-right of the screen. The zoom SHALL scale the entire family tree view between 50% and 200%, defaulting to 100%.

#### Scenario: Zoom in
- **WHEN** the player taps the "+" zoom button
- **THEN** the family tree view scale increases by 10% and the percentage label updates

#### Scenario: Zoom out
- **WHEN** the player taps the "-" zoom button
- **THEN** the family tree view scale decreases by 10% and the percentage label updates

#### Scenario: Zoom limits
- **WHEN** the zoom level reaches 50% or 200%
- **THEN** the corresponding zoom button becomes disabled
