# Update Command Specification

## Purpose

As a developer using OpenSpec-HW2, I want to update the OpenSpec-HW2 instructions in my project when new versions are released, so that I can benefit from improvements to AI agent instructions.

## Core Requirements

### Update Behavior

The update command SHALL update OpenSpec-HW2 instruction files to the latest templates.

WHEN a user runs `openspec-hw2 update` THEN the command SHALL:
- Check if the `openspec-hw2` directory exists
- Replace `openspec-hw2/README.md` with the latest template (complete replacement)
- Update the OpenSpec-HW2-managed block in `CLAUDE.md` using markers
  - Preserve user content outside markers
  - Create `CLAUDE.md` if missing
- Display ASCII-safe success message: "Updated OpenSpec-HW2 instructions"

### Prerequisites

The command SHALL require:
- An existing `openspec-hw2` directory (created by `openspec-hw2 init`)

IF the `openspec-hw2` directory does not exist THEN:
- Display error: "No OpenSpec-HW2 directory found. Run 'openspec-hw2 init' first."
- Exit with code 1

### File Handling

The update command SHALL:
- Completely replace `openspec-hw2/README.md` with the latest template
- Update only the OpenSpec-HW2-managed block in `CLAUDE.md` using markers
- Use the default directory name `openspec-hw2`
- Be idempotent (repeated runs have no additional effect)

## Edge Cases

### File Permissions
IF file write fails THEN let the error bubble up naturally with file path.

### Missing CLAUDE.md
IF CLAUDE.md doesn't exist THEN create it with the template content.

### Custom Directory Name
Not supported in this change. The default directory name `openspec-hw2` SHALL be used.

## Success Criteria

Users SHALL be able to:
- Update OpenSpec-HW2 instructions with a single command
- Get the latest AI agent instructions
- See clear confirmation of the update

The update process SHALL be:
- Simple and fast (no version checking)
- Predictable (same result every time)
- Self-contained (no network required)