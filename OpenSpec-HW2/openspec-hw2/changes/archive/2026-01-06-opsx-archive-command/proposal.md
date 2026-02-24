## Why

The experimental workflow (OPSX) provides a schema-driven, artifact-by-artifact approach to creating changes with `/opsx-hw2:new`, `/opsx-hw2:continue`, `/opsx-hw2:ff`, `/opsx-hw2:apply`, and `/opsx-hw2:sync`. However, there's no corresponding archive command to finalize and archive completed changes. Users must currently fall back to the regular `openspec-hw2 archive` command, which doesn't integrate with the OPSX philosophy of agent-driven spec syncing and schema-aware artifact tracking.

## What Changes

- Add `/opsx-hw2:archive` slash command for archiving changes in the experimental workflow
- Use artifact graph to check completion status (schema-aware) instead of just validating proposal + specs
- Prompt for `/opsx-hw2:sync` before archiving instead of programmatically applying specs
- Preserve `.openspec-hw2.yaml` schema metadata when moving to archive
- Integrate with existing OPSX commands for a cohesive workflow

## Capabilities

### New Capabilities

- `opsx-hw2-archive-skill`: Slash command and skill for archiving completed changes in the experimental workflow. Checks artifact completion via artifact graph, verifies task completion, optionally syncs specs via `/opsx-hw2:sync`, and moves the change to `archive/YYYY-MM-DD-<name>/`.

### Modified Capabilities

(none - this is a new skill that doesn't modify existing specs)

## Impact

- New file: `.claude/commands/opsx/archive.md`
- New skill definition (generated via `openspec-hw2 artifact-experimental-setup`)
- No changes to existing archive command or other OPSX commands
- Completes the OPSX command suite for full lifecycle management
