# Commands

This is the reference for OpenSpec-HW2's slash commands. These commands are invoked in your AI coding assistant's chat interface (e.g., Claude Code, Cursor, Windsurf).

For workflow patterns and when to use each command, see [Workflows](workflows.md). For CLI commands, see [CLI](cli.md).

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/opsx-hw2:explore` | Think through ideas before committing to a change |
| `/opsx-hw2:new` | Start a new change |
| `/opsx-hw2:continue` | Create the next artifact based on dependencies |
| `/opsx-hw2:ff` | Fast-forward: create all planning artifacts at once |
| `/opsx-hw2:apply` | Implement tasks from the change |
| `/opsx-hw2:verify` | Validate implementation matches artifacts |
| `/opsx-hw2:sync` | Merge delta specs into main specs |
| `/opsx-hw2:archive` | Archive a completed change |
| `/opsx-hw2:bulk-archive` | Archive multiple changes at once |
| `/opsx-hw2:onboard` | Guided tutorial through the complete workflow |

---

## Command Reference

### `/opsx-hw2:explore`

Think through ideas, investigate problems, and clarify requirements before committing to a change.

**Syntax:**
```
/opsx-hw2:explore [topic]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `topic` | No | What you want to explore or investigate |

**What it does:**
- Opens an exploratory conversation with no structure required
- Investigates the codebase to answer questions
- Compares options and approaches
- Creates visual diagrams to clarify thinking
- Can transition to `/opsx-hw2:new` when insights crystallize

**Example:**
```text
You: /opsx-hw2:explore

AI:  What would you like to explore?

You: How should we handle authentication for the mobile app?

AI:  Let me investigate your current auth setup...
     [Analyzes codebase]

     I see you're using session-based auth for the web app.
     For mobile, we have three main options:

     1. JWT tokens (stateless, works offline)
     2. OAuth2 (if you need third-party login)
     3. Extend current sessions (simpler, but requires connectivity)

     Your API already has CORS configured. Which direction interests you?

You: Let's go with JWT. Can we start a change for that?

AI:  Ready when you are. Run /opsx-hw2:new add-jwt-auth to begin.
```

**Tips:**
- Use when requirements are unclear or you need to investigate
- No artifacts are created during exploration
- Good for comparing multiple approaches before deciding
- Can read files and search the codebase

---

### `/opsx-hw2:new`

Start a new change. Creates the change folder structure and scaffolds it with the selected schema.

**Syntax:**
```
/opsx-hw2:new [change-name] [--schema <schema-name>]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Name for the change folder (prompted if not provided) |
| `--schema` | No | Workflow schema to use (default: from config or `spec-driven`) |

**What it does:**
- Creates `openspec-hw2/changes/<change-name>/` directory
- Creates `.openspec-hw2.yaml` metadata file in the change folder
- Shows the first artifact template ready for creation
- Prompts for change name and schema if not provided

**What it creates:**
```
openspec-hw2/changes/<change-name>/
└── .openspec-hw2.yaml    # Change metadata (schema, created date)
```

**Example:**
```
You: /opsx-hw2:new add-dark-mode

AI:  Created openspec-hw2/changes/add-dark-mode/
     Schema: spec-driven

     Ready to create: proposal
     Use /opsx-hw2:continue to create it, or /opsx-hw2:ff to create all artifacts.
```

**Tips:**
- Use descriptive names: `add-feature`, `fix-bug`, `refactor-module`
- Avoid generic names like `update`, `changes`, `wip`
- Schema can also be set in project config (`openspec-hw2/config.yaml`)

---

### `/opsx-hw2:continue`

Create the next artifact in the dependency chain. Creates one artifact at a time for incremental progress.

**Syntax:**
```
/opsx-hw2:continue [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to continue (inferred from context if not provided) |

**What it does:**
- Queries the artifact dependency graph
- Shows which artifacts are ready vs blocked
- Creates the first ready artifact
- Reads dependency files for context
- Shows what becomes available after creation

**Example:**
```
You: /opsx-hw2:continue

AI:  Change: add-dark-mode

     Artifact status:
     ✓ proposal    (done)
     ◆ specs       (ready)
     ◆ design      (ready)
     ○ tasks       (blocked - needs: specs)

     Creating specs...

     [Reads proposal.md, creates specs based on requirements]

     ✓ Created openspec-hw2/changes/add-dark-mode/specs/ui/spec.md

     Now available: tasks
     Run /opsx-hw2:continue to create the next artifact.
```

**Tips:**
- Use when you want to review each artifact before proceeding
- Good for complex changes where you want control
- Multiple artifacts may become ready simultaneously
- You can edit created artifacts before continuing

---

### `/opsx-hw2:ff`

Fast-forward through artifact creation. Creates all planning artifacts at once.

**Syntax:**
```
/opsx-hw2:ff [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to fast-forward (inferred from context if not provided) |

**What it does:**
- Creates all artifacts in dependency order
- Tracks progress via todo list
- Stops when all `apply-required` artifacts are complete
- Reads each dependency before creating the next artifact

**Example:**
```
You: /opsx-hw2:ff add-dark-mode

AI:  Fast-forwarding add-dark-mode...

     ✓ Creating proposal.md
     ✓ Creating specs/ui/spec.md
     ✓ Creating design.md
     ✓ Creating tasks.md

     All planning artifacts complete!
     Ready for implementation. Run /opsx-hw2:apply to begin.
```

**Tips:**
- Use when you have a clear picture of what you're building
- Faster than `/opsx-hw2:continue` for straightforward changes
- You can still edit artifacts afterward
- Good for small to medium features

---

### `/opsx-hw2:apply`

Implement tasks from the change. Works through the task list, writing code and checking off items.

**Syntax:**
```
/opsx-hw2:apply [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to implement (inferred from context if not provided) |

**What it does:**
- Reads `tasks.md` and identifies incomplete tasks
- Works through tasks one by one
- Writes code, creates files, runs tests as needed
- Marks tasks complete with checkboxes `[x]`

**Example:**
```
You: /opsx-hw2:apply

AI:  Implementing add-dark-mode...

     Reading tasks.md:
     - [ ] 1.1 Create ThemeContext
     - [ ] 1.2 Add CSS custom properties
     - [ ] 1.3 Implement localStorage persistence

     Working on 1.1: Create ThemeContext...
     [Creates src/context/ThemeContext.tsx]

     ✓ 1.1 Complete

     Working on 1.2: Add CSS custom properties...
     [Updates src/styles/globals.css]

     ✓ 1.2 Complete
     ...
```

**Tips:**
- Can resume where you left off if interrupted
- Use for parallel changes by specifying the change name
- Completion state is tracked in `tasks.md` checkboxes

---

### `/opsx-hw2:verify`

Validate that implementation matches your change artifacts. Checks completeness, correctness, and coherence.

**Syntax:**
```
/opsx-hw2:verify [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to verify (inferred from context if not provided) |

**What it does:**
- Checks three dimensions of implementation quality
- Searches codebase for implementation evidence
- Reports issues categorized as CRITICAL, WARNING, or SUGGESTION
- Does not block archive, but surfaces issues

**Verification dimensions:**

| Dimension | What it validates |
|-----------|-------------------|
| **Completeness** | All tasks done, all requirements implemented, scenarios covered |
| **Correctness** | Implementation matches spec intent, edge cases handled |
| **Coherence** | Design decisions reflected in code, patterns consistent |

**Example:**
```
You: /opsx-hw2:verify

AI:  Verifying add-dark-mode...

     COMPLETENESS
     ✓ All 8 tasks in tasks.md are checked
     ✓ All requirements in specs have corresponding code
     ⚠ Scenario "System preference detection" has no test coverage

     CORRECTNESS
     ✓ Implementation matches spec intent
     ✓ Edge cases from scenarios are handled
     ✓ Error states match spec definitions

     COHERENCE
     ✓ Design decisions reflected in code structure
     ✓ Naming conventions consistent with design.md
     ⚠ Design mentions "CSS variables" but implementation uses Tailwind classes

     SUMMARY
     ─────────────────────────────
     Critical issues: 0
     Warnings: 2
     Ready to archive: Yes (with warnings)

     Recommendations:
     1. Add test for system preference detection
     2. Update design.md to reflect Tailwind usage, or refactor to use CSS variables
```

**Tips:**
- Run before archiving to catch mismatches early
- Warnings don't block archive but indicate potential issues
- Good for reviewing AI's work before committing
- Can reveal drift between artifacts and implementation

---

### `/opsx-hw2:sync`

**Optional command.** Merge delta specs from a change into main specs. Archive will prompt to sync if needed, so you typically don't need to run this manually.

**Syntax:**
```
/opsx-hw2:sync [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to sync (inferred from context if not provided) |

**What it does:**
- Reads delta specs from change folder
- Parses ADDED/MODIFIED/REMOVED/RENAMED sections
- Merges changes into main `openspec-hw2/specs/` directory
- Preserves existing content not mentioned in delta
- Does not archive the change (remains active)

**Example:**
```text
You: /opsx-hw2:sync

AI:  Syncing add-dark-mode delta specs...

     Reading: openspec-hw2/changes/add-dark-mode/specs/ui/spec.md
     Target:  openspec-hw2/specs/ui/spec.md

     Changes to apply:
     ✓ ADDED: Theme Selection requirement (2 scenarios)
     ✓ ADDED: Accessibility requirement (1 scenario)

     Merging...
     ✓ openspec-hw2/specs/ui/spec.md updated

     Change remains active. Run /opsx-hw2:archive when ready to complete.
```

**When to use manually:**

| Scenario | Use sync? |
|----------|-----------|
| Long-running change, want specs in main before archiving | Yes |
| Multiple parallel changes need the updated base specs | Yes |
| Want to preview/review the merge separately | Yes |
| Quick change, going straight to archive | No (archive handles it) |

**Tips:**
- Sync is intelligent, not copy-paste
- Can add scenarios to existing requirements without duplicating
- Change stays active after sync (not archived)
- Most users will never need to call this directly—archive prompts if needed

---

### `/opsx-hw2:archive`

Archive a completed change. Finalizes the change and moves it to the archive folder.

**Syntax:**
```
/opsx-hw2:archive [change-name]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-name` | No | Which change to archive (inferred from context if not provided) |

**What it does:**
- Checks artifact completion status
- Checks task completion (warns if incomplete)
- Offers to sync delta specs if not already synced
- Moves change folder to `openspec-hw2/changes/archive/YYYY-MM-DD-<name>/`
- Preserves all artifacts for audit trail

**Example:**
```text
You: /opsx-hw2:archive

AI:  Archiving add-dark-mode...

     Artifact status:
     ✓ proposal.md exists
     ✓ specs/ exists
     ✓ design.md exists
     ✓ tasks.md exists (8/8 tasks complete)

     Delta specs: Not yet synced
     → Sync now? (recommended)

You: Yes

AI:  ✓ Synced specs to openspec-hw2/specs/ui/spec.md
     ✓ Moved to openspec-hw2/changes/archive/2025-01-24-add-dark-mode/

     Change archived successfully.
```

**Tips:**
- Archive won't block on incomplete tasks, but will warn
- Delta specs can be synced during archive or beforehand
- Archived changes are preserved for history
- Use `/opsx-hw2:verify` first to catch issues

---

### `/opsx-hw2:bulk-archive`

Archive multiple completed changes at once. Handles spec conflicts between changes.

**Syntax:**
```
/opsx-hw2:bulk-archive [change-names...]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `change-names` | No | Specific changes to archive (prompts to select if not provided) |

**What it does:**
- Lists all completed changes
- Validates each change before archiving
- Detects spec conflicts across changes
- Resolves conflicts by checking what's actually implemented
- Archives in chronological order

**Example:**
```
You: /opsx-hw2:bulk-archive

AI:  Found 3 completed changes:
     - add-dark-mode (8/8 tasks complete)
     - fix-login-bug (3/3 tasks complete)
     - update-footer (2/2 tasks complete)

     Checking for spec conflicts...
     ⚠ add-dark-mode and update-footer both touch specs/ui/

     Inspecting codebase to resolve...
     Both changes are implemented. Will merge in chronological order:
     1. add-dark-mode (created Jan 20)
     2. update-footer (created Jan 22)

     Archive all 3 changes?

You: Yes

AI:  ✓ Archived add-dark-mode
     ✓ Archived fix-login-bug
     ✓ Archived update-footer
     Specs merged: add-dark-mode → update-footer
```

**Tips:**
- Good for parallel work streams
- Conflict resolution is agentic (checks codebase)
- Changes are archived in order of creation
- Prompts before overwriting spec content

---

### `/opsx-hw2:onboard`

Guided onboarding through the complete OpenSpec-HW2 workflow. An interactive tutorial using your actual codebase.

**Syntax:**
```
/opsx-hw2:onboard
```

**What it does:**
- Walks through a complete workflow cycle with narration
- Scans your codebase for real improvement opportunities
- Creates an actual change with real artifacts
- Implements actual work (small, safe changes)
- Archives the completed change
- Explains each step as it happens

**Phases:**
1. Welcome and codebase analysis
2. Finding an improvement opportunity
3. Creating a change (`/opsx-hw2:new`)
4. Writing the proposal
5. Creating specs
6. Writing the design
7. Creating tasks
8. Implementing tasks (`/opsx-hw2:apply`)
9. Verifying implementation
10. Archiving the change
11. Summary and next steps

**Example:**
```
You: /opsx-hw2:onboard

AI:  Welcome to OpenSpec-HW2!

     I'll walk you through the complete workflow using your actual codebase.
     We'll find something small to improve, create a proper change for it,
     implement it, and archive it.

     Let me scan your codebase for opportunities...

     [Analyzes codebase]

     I found a few things we could work on:
     1. Add input validation to the contact form
     2. Improve error messages in the auth flow
     3. Add loading states to async buttons

     Which interests you? (or suggest something else)
```

**Tips:**
- Best for new users learning the workflow
- Uses real code, not toy examples
- Creates a real change you can keep or discard
- Takes 15-30 minutes to complete

---

## Command Syntax by AI Tool

Different AI tools use slightly different command syntax. Use the format that matches your tool:

| Tool | Syntax Example |
|------|----------------|
| Claude Code | `/opsx-hw2:new`, `/opsx-hw2:apply` |
| Cursor | `/opsx-hw2-new`, `/opsx-hw2-apply` |
| Windsurf | `/opsx-hw2-new`, `/opsx-hw2-apply` |
| Copilot (IDE) | `/opsx-hw2-new`, `/opsx-hw2-apply` |
| Trae | `/openspec-hw2-new-change`, `/openspec-hw2-apply-change` |

The functionality is identical regardless of syntax.

> **Note:** GitHub Copilot commands (`.github/prompts/*.prompt.md`) are only available in IDE extensions (VS Code, JetBrains, Visual Studio). GitHub Copilot CLI does not currently support custom prompt files — see [Supported Tools](supported-tools.md) for details and workarounds.

---

## Legacy Commands

These commands use the older "all-at-once" workflow. They still work but OPSX commands are recommended.

| Command | What it does |
|---------|--------------|
| `/openspec-hw2:proposal` | Create all artifacts at once (proposal, specs, design, tasks) |
| `/openspec-hw2:apply` | Implement the change |
| `/openspec-hw2:archive` | Archive the change |

**When to use legacy commands:**
- Existing projects using the old workflow
- Simple changes where you don't need incremental artifact creation
- Preference for the all-or-nothing approach

**Migrating to OPSX:**
Legacy changes can be continued with OPSX commands. The artifact structure is compatible.

---

## Troubleshooting

### "Change not found"

The command couldn't identify which change to work on.

**Solutions:**
- Specify the change name explicitly: `/opsx-hw2:apply add-dark-mode`
- Check that the change folder exists: `openspec-hw2 list`
- Verify you're in the right project directory

### "No artifacts ready"

All artifacts are either complete or blocked by missing dependencies.

**Solutions:**
- Run `openspec-hw2 status --change <name>` to see what's blocking
- Check if required artifacts exist
- Create missing dependency artifacts first

### "Schema not found"

The specified schema doesn't exist.

**Solutions:**
- List available schemas: `openspec-hw2 schemas`
- Check spelling of schema name
- Create the schema if it's custom: `openspec-hw2 schema init <name>`

### Commands not recognized

The AI tool doesn't recognize OpenSpec-HW2 commands.

**Solutions:**
- Ensure OpenSpec-HW2 is initialized: `openspec-hw2 init`
- Regenerate skills: `openspec-hw2 update`
- Check that `.claude/skills/` directory exists (for Claude Code)
- Restart your AI tool to pick up new skills

### Artifacts not generating properly

The AI creates incomplete or incorrect artifacts.

**Solutions:**
- Add project context in `openspec-hw2/config.yaml`
- Add per-artifact rules for specific guidance
- Provide more detail in your change description
- Use `/opsx-hw2:continue` instead of `/opsx-hw2:ff` for more control

---

## Next Steps

- [Workflows](workflows.md) - Common patterns and when to use each command
- [CLI](cli.md) - Terminal commands for management and validation
- [Customization](customization.md) - Create custom schemas and workflows
