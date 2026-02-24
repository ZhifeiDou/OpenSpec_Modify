## MODIFIED Requirements
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

#### Scenario: Generating slash commands for Factory Droid
- **WHEN** the user selects Factory Droid during initialization
- **THEN** create `.factory/commands/openspec-hw2-proposal.md`, `.factory/commands/openspec-hw2-apply.md`, and `.factory/commands/openspec-hw2-archive.md`
- **AND** populate each file from shared templates that include Factory-compatible YAML frontmatter for the `description` and `argument-hint` fields
- **AND** include the `$ARGUMENTS` placeholder in the template body so droid receives any user-supplied input
- **AND** wrap the generated content in OpenSpec-HW2 managed markers so `openspec-hw2 update` can safely refresh the commands

#### Scenario: Generating slash commands for OpenCode
- **WHEN** the user selects OpenCode during initialization
- **THEN** create `.opencode/commands/openspec-hw2-proposal.md`, `.opencode/commands/openspec-hw2-apply.md`, and `.opencode/commands/openspec-hw2-archive.md`
- **AND** populate each file from shared templates so command text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage

#### Scenario: Generating slash commands for Windsurf
- **WHEN** the user selects Windsurf during initialization
- **THEN** create `.windsurf/workflows/openspec-hw2-proposal.md`, `.windsurf/workflows/openspec-hw2-apply.md`, and `.windsurf/workflows/openspec-hw2-archive.md`
- **AND** populate each file from shared templates (wrapped in OpenSpec-HW2 markers) so workflow text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage

#### Scenario: Generating slash commands for Kilo Code
- **WHEN** the user selects Kilo Code during initialization
- **THEN** create `.kilocode/workflows/openspec-hw2-proposal.md`, `.kilocode/workflows/openspec-hw2-apply.md`, and `.kilocode/workflows/openspec-hw2-archive.md`
- **AND** populate each file from shared templates (wrapped in OpenSpec-HW2 markers) so workflow text matches other tools
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage

#### Scenario: Generating slash commands for Codex
- **WHEN** the user selects Codex during initialization
- **THEN** create global prompt files at `~/.codex/prompts/openspec-hw2-proposal.md`, `~/.codex/prompts/openspec-hw2-apply.md`, and `~/.codex/prompts/openspec-hw2-archive.md` (or under `$CODEX_HOME/prompts` if set)
- **AND** populate each file from shared templates that map the first numbered placeholder (`$1`) to the primary user input (e.g., change identifier or question text)
- **AND** wrap the generated content in OpenSpec-HW2 markers so `openspec-hw2 update` can refresh the prompts without touching surrounding custom notes

#### Scenario: Generating slash commands for GitHub Copilot
- **WHEN** the user selects GitHub Copilot during initialization
- **THEN** create `.github/prompts/openspec-hw2-proposal.prompt.md`, `.github/prompts/openspec-hw2-apply.prompt.md`, and `.github/prompts/openspec-hw2-archive.prompt.md`
- **AND** populate each file with YAML frontmatter containing a `description` field that summarizes the workflow stage
- **AND** include `$ARGUMENTS` placeholder to capture user input
- **AND** wrap the shared template body with OpenSpec-HW2 markers so `openspec-hw2 update` can refresh the content
- **AND** each template includes instructions for the relevant OpenSpec-HW2 workflow stage
