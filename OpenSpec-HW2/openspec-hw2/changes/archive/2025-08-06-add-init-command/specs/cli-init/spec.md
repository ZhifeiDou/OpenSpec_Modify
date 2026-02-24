# CLI Init Specification

## Purpose

The `openspec-hw2 init` command SHALL create a complete OpenSpec-HW2 directory structure in any project, enabling immediate adoption of OpenSpec-HW2 conventions with support for multiple AI coding assistants.

## Behavior

### Progress Indicators

WHEN executing initialization steps
THEN validate environment silently in background (no output unless error)
AND display progress with ora spinners:
- Show spinner: "⠋ Creating OpenSpec-HW2 structure..."
- Then success: "✔ OpenSpec-HW2 structure created"
- Show spinner: "⠋ Configuring AI tools..."
- Then success: "✔ AI tools configured"

### Directory Creation

WHEN `openspec-hw2 init` is executed
THEN create the following directory structure:
```
openspec-hw2/
├── project.md
├── README.md
├── specs/
└── changes/
    └── archive/
```

### File Generation

The command SHALL generate:
- `README.md` containing complete OpenSpec-HW2 instructions for AI assistants
- `project.md` with project context template

### AI Tool Configuration

WHEN run interactively
THEN prompt user to select AI tools to configure:
- Claude Code (updates/creates CLAUDE.md with OpenSpec-HW2 markers)
- Cursor (future)
- Aider (future)

### AI Tool Configuration Details

WHEN Claude Code is selected
THEN create or update `CLAUDE.md` in the project root directory (not inside openspec-hw2/)

WHEN CLAUDE.md does not exist
THEN create new file with OpenSpec-HW2 content wrapped in markers:
```markdown
<!-- OPENSPEC-HW2:START -->
# OpenSpec-HW2 Project

This document provides instructions for AI coding assistants on how to use OpenSpec-HW2 conventions for spec-driven development. Follow these rules precisely when working on OpenSpec-HW2-enabled projects.

This project uses OpenSpec-HW2 for spec-driven development. Specifications are the source of truth.

See @openspec-hw2/README.md for detailed conventions and guidelines.
<!-- OPENSPEC-HW2:END -->
```

WHEN CLAUDE.md already exists
THEN preserve all existing content
AND insert OpenSpec-HW2 content at the beginning of the file using markers
AND ensure markers don't duplicate if they already exist

The marker system SHALL:
- Use `<!-- OPENSPEC-HW2:START -->` to mark the beginning of managed content
- Use `<!-- OPENSPEC-HW2:END -->` to mark the end of managed content
- Allow OpenSpec-HW2 to update its content without affecting user customizations
- Preserve all content outside the markers intact

WHY use markers:
- Users may have existing CLAUDE.md instructions they want to keep
- OpenSpec-HW2 can update its instructions in future versions
- Clear boundary between OpenSpec-HW2-managed and user-managed content

### Interactive Mode

WHEN run
THEN prompt user with: "Which AI tool do you use?"
AND show single-select menu with available tools:
- Claude Code
AND show disabled options as "coming soon" (not selectable):
- Cursor (coming soon)
- Aider (coming soon)  
- Continue (coming soon)

User navigation:
- Use arrow keys to move between options
- Press Enter to select the highlighted option

### Safety Checks

WHEN `openspec-hw2/` directory already exists
THEN display error with ora fail indicator:
"✖ Error: OpenSpec-HW2 seems to already be initialized. Use 'openspec-hw2 update' to update the structure."

WHEN checking initialization feasibility
THEN verify write permissions in the target directory silently
AND only display error if permissions are insufficient

### Success Output

WHEN initialization completes successfully
THEN display actionable prompts for AI-driven workflow:
```
✔ OpenSpec-HW2 initialized successfully!

Next steps - Copy these prompts to Claude:

────────────────────────────────────────────────────────────
1. Populate your project context:
   "Please read openspec-hw2/project.md and help me fill it out
    with details about my project, tech stack, and conventions"

2. Create your first change proposal:
   "I want to add [YOUR FEATURE HERE]. Please create an
    OpenSpec-HW2 change proposal for this feature"

3. Learn the OpenSpec-HW2 workflow:
   "Please explain the OpenSpec-HW2 workflow from openspec-hw2/README.md
    and how I should work with you on this project"
────────────────────────────────────────────────────────────
```

The prompts SHALL:
- Be copy-pasteable for immediate use with AI tools
- Guide users through the AI-driven workflow
- Replace placeholder text ([YOUR FEATURE HERE]) with actual features

### Exit Codes

- 0: Success
- 1: General error (including when OpenSpec-HW2 directory already exists)
- 2: Insufficient permissions (reserved for future use)
- 3: User cancelled operation (reserved for future use)

## Why

Manual creation of OpenSpec-HW2 structure is error-prone and creates adoption friction. A standardized init command ensures:
- Consistent structure across all projects
- Proper AI instruction files are always included
- Quick onboarding for new projects
- Clear conventions from the start