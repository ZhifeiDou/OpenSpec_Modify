# Update Agent Instruction File Name

## Problem
The agent instructions live in `openspec-hw2/README.md`, which clashes with conventional project README usage and creates confusion for tooling and contributors.

## Solution
Rename the agent instruction file to `openspec-hw2/AGENTS.md` and update OpenSpec-HW2 tooling to use the new filename:
- `openspec-hw2 init` generates `AGENTS.md` instead of `README.md`
- Templates and code reference `AGENTS.md`
- Specifications and documentation are updated accordingly

## Benefits
- Clear separation from project documentation
- Consistent naming with other agent instruction files
- Simplifies tooling and project onboarding

## Implementation
- Rename instruction file and template
- Update CLI commands (`init`, `update`) to read/write `AGENTS.md`
- Adjust specs and documentation to reference the new path

## Risks
- Existing projects may still rely on `README.md`
- Tooling may miss lingering references to the old filename

## Success Metrics
- `openspec-hw2 init` creates `openspec-hw2/AGENTS.md`
- `openspec-hw2 update` refreshes `AGENTS.md`
- All specs reference `openspec-hw2/AGENTS.md`
