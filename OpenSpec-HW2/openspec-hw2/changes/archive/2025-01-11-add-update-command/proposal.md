# Add Update Command

## Why

Users need a way to update their local OpenSpec-HW2 instructions (README.md and CLAUDE.md) when the OpenSpec-HW2 package releases new versions with improved AI agent instructions or structural conventions.

## What Changes

- Add new `openspec-hw2 update` CLI command that updates OpenSpec-HW2 instructions
- Replace `openspec-hw2/README.md` with the latest template
  - Safe because this file is fully OpenSpec-HW2-managed
- Update only the OpenSpec-HW2-managed block in `CLAUDE.md` using markers
  - Preserve all user content outside markers
  - If `CLAUDE.md` is missing, create it with the managed block
- Display success message after update (ASCII-safe): "Updated OpenSpec-HW2 instructions"
  - A leading checkmark MAY be shown when the terminal supports it
  - Operation is idempotent (re-running yields identical results)

## Impact

- Affected specs: `cli-update` (new capability)
- Affected code:
  - `src/core/update.ts` (new command class, mirrors `InitCommand` placement)
  - `src/cli/index.ts` (register new command)
  - Uses existing templates via `TemplateManager` and `readmeTemplate`

## Out of Scope

- No `.openspec-hw2/config.json` is introduced by this change. The default directory name `openspec-hw2` is used.