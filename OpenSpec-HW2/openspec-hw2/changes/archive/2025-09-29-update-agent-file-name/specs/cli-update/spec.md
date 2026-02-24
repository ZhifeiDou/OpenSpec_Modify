## MODIFIED Requirements

### Requirement: Update Behavior
The update command SHALL update OpenSpec-HW2 instruction files to the latest templates in a team-friendly manner.

#### Scenario: Running update command
- **WHEN** a user runs `openspec-hw2 update`
- **THEN** replace `openspec-hw2/AGENTS.md` with the latest template

### Requirement: File Handling
The update command SHALL handle file updates in a predictable and safe manner.

#### Scenario: Updating files
- **WHEN** updating files
- **THEN** completely replace `openspec-hw2/AGENTS.md` with the latest template

### Requirement: Core Files Always Updated
The update command SHALL always update the core OpenSpec-HW2 files and display an ASCII-safe success message.

#### Scenario: Successful update
- **WHEN** the update completes successfully
- **THEN** replace `openspec-hw2/AGENTS.md` with the latest template
