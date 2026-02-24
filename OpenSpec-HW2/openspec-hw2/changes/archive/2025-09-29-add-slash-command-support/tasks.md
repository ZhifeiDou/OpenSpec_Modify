# Implementation Tasks

## 1. Templates and Configurators
- [x] 1.1 Create shared templates for the Proposal, Apply, and Archive commands with instructions for each workflow stage from `openspec-hw2/README.md`.
- [x] 1.2 Implement a `SlashCommandConfigurator` base and tool-specific configurators for Claude Code and Cursor.

## 2. Claude Code Integration
- [x] 2.1 Generate `.claude/commands/openspec-hw2/{proposal,apply,archive}.md` during `openspec-hw2 init` using shared templates.
- [x] 2.2 Update existing `.claude/commands/openspec-hw2/*` files during `openspec-hw2 update`.

## 3. Cursor Integration
- [x] 3.1 Generate `.cursor/commands/{openspec-hw2-proposal,openspec-hw2-apply,openspec-hw2-archive}.md` during `openspec-hw2 init` using shared templates.
- [x] 3.2 Update existing `.cursor/commands/*` files during `openspec-hw2 update`.

## 4. Verification
- [x] 4.1 Add tests verifying slash command files are created and updated correctly.

## 5. OpenCode Integration
- [x] 5.1 Generate `.opencode/commands/{openspec-hw2-proposal,openspec-hw2-apply,openspec-hw2-archive}.md` during `openspec-hw2 init` using shared templates.
- [x] 5.2 Update existing `.opencode/commands/*` files during `openspec-hw2 update`.
