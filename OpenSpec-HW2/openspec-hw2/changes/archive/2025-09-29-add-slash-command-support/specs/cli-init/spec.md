## ADDED Requirements
### Requirement: Slash Command Configuration
The init command SHALL generate slash command files for supported editors using shared templates.

#### Scenario: Generating slash commands for Claude Code
- **WHEN** the user selects Claude Code during initialization
- **THEN** create `.claude/commands/openspec-hw2/proposal.md`, `.claude/commands/openspec-hw2/apply.md`, and `.claude/commands/openspec-hw2/archive.md`
- **AND** populate each file from shared templates so command text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage

#### Scenario: Generating slash commands for Cursor
- **WHEN** the user selects Cursor during initialization
- **THEN** create `.cursor/commands/openspec-hw2-proposal.md`, `.cursor/commands/openspec-hw2-apply.md`, and `.cursor/commands/openspec-hw2-archive.md`
- **AND** populate each file from shared templates so command text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage

#### Scenario: Generating slash commands for OpenCode
- **WHEN** the user selects OpenCode during initialization
- **THEN** create `.opencode/commands/openspec-hw2-proposal.md`, `.opencode/commands/openspec-hw2-apply.md`, and `.opencode/commands/openspec-hw2-archive.md`
- **AND** populate each file from shared templates so command text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage
