## MODIFIED Requirements
### Requirement: Tool-Agnostic Updates
The update command SHALL refresh OpenSpec-HW2-managed files in a predictable manner while respecting each team's chosen tooling.

#### Scenario: Updating files
- **WHEN** updating files
- **THEN** completely replace `openspec-hw2/AGENTS.md` with the latest template
- **AND** create or refresh the root-level `AGENTS.md` stub using the managed marker block, even if the file was previously absent
- **AND** update only the OpenSpec-HW2-managed sections inside existing AI tool files, leaving user-authored content untouched
- **AND** avoid creating new native-tool configuration files (slash commands, CLAUDE.md, etc.) unless they already exist
