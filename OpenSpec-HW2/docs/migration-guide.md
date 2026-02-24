# Migrating to OPSX

This guide helps you transition from the legacy OpenSpec-HW2 workflow to OPSX. The migration is designed to be smooth—your existing work is preserved, and the new system offers more flexibility.

## What's Changing?

OPSX replaces the old phase-locked workflow with a fluid, action-based approach. Here's the key shift:

| Aspect | Legacy | OPSX |
|--------|--------|------|
| **Commands** | `/openspec-hw2:proposal`, `/openspec-hw2:apply`, `/openspec-hw2:archive` | `/opsx-hw2:new`, `/opsx-hw2:continue`, `/opsx-hw2:apply`, and more |
| **Workflow** | Create all artifacts at once | Create incrementally or all at once—your choice |
| **Going back** | Awkward phase gates | Natural—update any artifact anytime |
| **Customization** | Fixed structure | Schema-driven, fully hackable |
| **Configuration** | `CLAUDE.md` with markers + `project.md` | Clean config in `openspec-hw2/config.yaml` |

**The philosophy change:** Work isn't linear. OPSX stops pretending it is.

---

## Before You Begin

### Your Existing Work Is Safe

The migration process is designed with preservation in mind:

- **Active changes in `openspec-hw2/changes/`** — Completely preserved. You can continue them with OPSX commands.
- **Archived changes** — Untouched. Your history remains intact.
- **Main specs in `openspec-hw2/specs/`** — Untouched. These are your source of truth.
- **Your content in CLAUDE.md, AGENTS.md, etc.** — Preserved. Only the OpenSpec-HW2 marker blocks are removed; everything you wrote stays.

### What Gets Removed

Only OpenSpec-HW2-managed files that are being replaced:

| What | Why |
|------|-----|
| Legacy slash command directories/files | Replaced by the new skills system |
| `openspec-hw2/AGENTS.md` | Obsolete workflow trigger |
| OpenSpec-HW2 markers in `CLAUDE.md`, `AGENTS.md`, etc. | No longer needed |

**Legacy command locations by tool** (examples—your tool may vary):

- Claude Code: `.claude/commands/openspec-hw2/`
- Cursor: `.cursor/commands/openspec-hw2-*.md`
- Windsurf: `.windsurf/workflows/openspec-hw2-*.md`
- Cline: `.clinerules/workflows/openspec-hw2-*.md`
- Roo: `.roo/commands/openspec-hw2-*.md`
- GitHub Copilot: `.github/prompts/openspec-hw2-*.prompt.md` (IDE extensions only; not supported in Copilot CLI)
- And others (Augment, Continue, Amazon Q, etc.)

The migration detects whichever tools you have configured and cleans up their legacy files.

The removal list may seem long, but these are all files that OpenSpec-HW2 originally created. Your own content is never deleted.

### What Needs Your Attention

One file requires manual migration:

**`openspec-hw2/project.md`** — This file isn't deleted automatically because it may contain project context you've written. You'll need to:

1. Review its contents
2. Move useful context to `openspec-hw2/config.yaml` (see guidance below)
3. Delete the file when ready

**Why we made this change:**

The old `project.md` was passive—agents might read it, might not, might forget what they read. We found reliability was inconsistent.

The new `config.yaml` context is **actively injected into every OpenSpec-HW2 planning request**. This means your project conventions, tech stack, and rules are always present when the AI is creating artifacts. Higher reliability.

**The tradeoff:**

Because context is injected into every request, you'll want to be concise. Focus on what really matters:
- Tech stack and key conventions
- Non-obvious constraints the AI needs to know
- Rules that frequently got ignored before

Don't worry about getting it perfect. We're still learning what works best here, and we'll be improving how context injection works as we experiment.

---

## Running the Migration

Both `openspec-hw2 init` and `openspec-hw2 update` detect legacy files and guide you through the same cleanup process. Use whichever fits your situation:

### Using `openspec-hw2 init`

Run this if you want to add new tools or reconfigure which tools are set up:

```bash
openspec-hw2 init
```

The init command detects legacy files and guides you through cleanup:

```
Upgrading to the new OpenSpec-HW2

OpenSpec-HW2 now uses agent skills, the emerging standard across coding
agents. This simplifies your setup while keeping everything working
as before.

Files to remove
No user content to preserve:
  • .claude/commands/openspec-hw2/
  • openspec-hw2/AGENTS.md

Files to update
OpenSpec-HW2 markers will be removed, your content preserved:
  • CLAUDE.md
  • AGENTS.md

Needs your attention
  • openspec-hw2/project.md
    We won't delete this file. It may contain useful project context.

    The new openspec-hw2/config.yaml has a "context:" section for planning
    context. This is included in every OpenSpec-HW2 request and works more
    reliably than the old project.md approach.

    Review project.md, move any useful content to config.yaml's context
    section, then delete the file when ready.

? Upgrade and clean up legacy files? (Y/n)
```

**What happens when you say yes:**

1. Legacy slash command directories are removed
2. OpenSpec-HW2 markers are stripped from `CLAUDE.md`, `AGENTS.md`, etc. (your content stays)
3. `openspec-hw2/AGENTS.md` is deleted
4. New skills are installed in `.claude/skills/`
5. `openspec-hw2/config.yaml` is created with a default schema

### Using `openspec-hw2 update`

Run this if you just want to migrate and refresh your existing tools to the latest version:

```bash
openspec-hw2 update
```

The update command also detects and cleans up legacy artifacts, then refreshes your skills to the latest version.

### Non-Interactive / CI Environments

For scripted migrations:

```bash
openspec-hw2 init --force --tools claude
```

The `--force` flag skips prompts and auto-accepts cleanup.

---

## Migrating project.md to config.yaml

The old `openspec-hw2/project.md` was a freeform markdown file for project context. The new `openspec-hw2/config.yaml` is structured and—critically—**injected into every planning request** so your conventions are always present when the AI works.

### Before (project.md)

```markdown
# Project Context

This is a TypeScript monorepo using React and Node.js.
We use Jest for testing and follow strict ESLint rules.
Our API is RESTful and documented in docs/api.md.

## Conventions

- All public APIs must maintain backwards compatibility
- New features should include tests
- Use Given/When/Then format for specifications
```

### After (config.yaml)

```yaml
schema: spec-driven

context: |
  Tech stack: TypeScript, React, Node.js
  Testing: Jest with React Testing Library
  API: RESTful, documented in docs/api.md
  We maintain backwards compatibility for all public APIs

rules:
  proposal:
    - Include rollback plan for risky changes
  specs:
    - Use Given/When/Then format for scenarios
    - Reference existing patterns before inventing new ones
  design:
    - Include sequence diagrams for complex flows
```

### Key Differences

| project.md | config.yaml |
|------------|-------------|
| Freeform markdown | Structured YAML |
| One blob of text | Separate context and per-artifact rules |
| Unclear when it's used | Context appears in ALL artifacts; rules appear in matching artifacts only |
| No schema selection | Explicit `schema:` field sets default workflow |

### What to Keep, What to Drop

When migrating, be selective. Ask yourself: "Does the AI need this for *every* planning request?"

**Good candidates for `context:`**
- Tech stack (languages, frameworks, databases)
- Key architectural patterns (monorepo, microservices, etc.)
- Non-obvious constraints ("we can't use library X because...")
- Critical conventions that often get ignored

**Move to `rules:` instead**
- Artifact-specific formatting ("use Given/When/Then in specs")
- Review criteria ("proposals must include rollback plans")
- These only appear for the matching artifact, keeping other requests lighter

**Leave out entirely**
- General best practices the AI already knows
- Verbose explanations that could be summarized
- Historical context that doesn't affect current work

### Migration Steps

1. **Create config.yaml** (if not already created by init):
   ```yaml
   schema: spec-driven
   ```

2. **Add your context** (be concise—this goes into every request):
   ```yaml
   context: |
     Your project background goes here.
     Focus on what the AI genuinely needs to know.
   ```

3. **Add per-artifact rules** (optional):
   ```yaml
   rules:
     proposal:
       - Your proposal-specific guidance
     specs:
       - Your spec-writing rules
   ```

4. **Delete project.md** once you've moved everything useful.

**Don't overthink it.** Start with the essentials and iterate. If you notice the AI missing something important, add it. If context feels bloated, trim it. This is a living document.

### Need Help? Use This Prompt

If you're unsure how to distill your project.md, ask your AI assistant:

```
I'm migrating from OpenSpec-HW2's old project.md to the new config.yaml format.

Here's my current project.md:
[paste your project.md content]

Please help me create a config.yaml with:
1. A concise `context:` section (this gets injected into every planning request, so keep it tight—focus on tech stack, key constraints, and conventions that often get ignored)
2. `rules:` for specific artifacts if any content is artifact-specific (e.g., "use Given/When/Then" belongs in specs rules, not global context)

Leave out anything generic that AI models already know. Be ruthless about brevity.
```

The AI will help you identify what's essential vs. what can be trimmed.

---

## The New Commands

After migration, you have 9 OPSX commands instead of 3:

| Command | Purpose |
|---------|---------|
| `/opsx-hw2:explore` | Think through ideas with no structure |
| `/opsx-hw2:new` | Start a new change |
| `/opsx-hw2:continue` | Create the next artifact (one at a time) |
| `/opsx-hw2:ff` | Fast-forward—create all planning artifacts at once |
| `/opsx-hw2:apply` | Implement tasks from tasks.md |
| `/opsx-hw2:verify` | Validate implementation matches specs |
| `/opsx-hw2:sync` | Preview spec merge (optional—archive prompts if needed) |
| `/opsx-hw2:archive` | Finalize and archive the change |
| `/opsx-hw2:bulk-archive` | Archive multiple changes at once |

### Command Mapping from Legacy

| Legacy | OPSX Equivalent |
|--------|-----------------|
| `/openspec-hw2:proposal` | `/opsx-hw2:new` then `/opsx-hw2:ff` |
| `/openspec-hw2:apply` | `/opsx-hw2:apply` |
| `/openspec-hw2:archive` | `/opsx-hw2:archive` |

### New Capabilities

**Granular artifact creation:**
```
/opsx-hw2:continue
```
Creates one artifact at a time based on dependencies. Use this when you want to review each step.

**Exploration mode:**
```
/opsx-hw2:explore
```
Think through ideas with a partner before committing to a change.

---

## Understanding the New Architecture

### From Phase-Locked to Fluid

The legacy workflow forced linear progression:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   PLANNING   │ ───► │ IMPLEMENTING │ ───► │   ARCHIVING  │
│    PHASE     │      │    PHASE     │      │    PHASE     │
└──────────────┘      └──────────────┘      └──────────────┘

If you're in implementation and realize the design is wrong?
Too bad. Phase gates don't let you go back easily.
```

OPSX uses actions, not phases:

```
         ┌───────────────────────────────────────────────┐
         │           ACTIONS (not phases)                │
         │                                               │
         │     new ◄──► continue ◄──► apply ◄──► archive │
         │      │          │           │             │   │
         │      └──────────┴───────────┴─────────────┘   │
         │                    any order                  │
         └───────────────────────────────────────────────┘
```

### Dependency Graph

Artifacts form a directed graph. Dependencies are enablers, not gates:

```
                        proposal
                       (root node)
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
           specs                       design
        (requires:                  (requires:
         proposal)                   proposal)
              │                           │
              └─────────────┬─────────────┘
                            │
                            ▼
                         tasks
                     (requires:
                     specs, design)
```

When you run `/opsx-hw2:continue`, it checks what's ready and offers the next artifact. You can also create multiple ready artifacts in any order.

### Skills vs Commands

The legacy system used tool-specific command files:

```
.claude/commands/openspec-hw2/
├── proposal.md
├── apply.md
└── archive.md
```

OPSX uses the emerging **skills** standard:

```
.claude/skills/
├── openspec-hw2-explore/SKILL.md
├── openspec-hw2-new-change/SKILL.md
├── openspec-hw2-continue-change/SKILL.md
├── openspec-hw2-apply-change/SKILL.md
└── ...
```

Skills are recognized across multiple AI coding tools and provide richer metadata.

---

## Continuing Existing Changes

Your in-progress changes work seamlessly with OPSX commands.

**Have an active change from the legacy workflow?**

```
/opsx-hw2:apply add-my-feature
```

OPSX reads the existing artifacts and continues from where you left off.

**Want to add more artifacts to an existing change?**

```
/opsx-hw2:continue add-my-feature
```

Shows what's ready to create based on what already exists.

**Need to see status?**

```bash
openspec-hw2 status --change add-my-feature
```

---

## The New Config System

### config.yaml Structure

```yaml
# Required: Default schema for new changes
schema: spec-driven

# Optional: Project context (max 50KB)
# Injected into ALL artifact instructions
context: |
  Your project background, tech stack,
  conventions, and constraints.

# Optional: Per-artifact rules
# Only injected into matching artifacts
rules:
  proposal:
    - Include rollback plan
  specs:
    - Use Given/When/Then format
  design:
    - Document fallback strategies
  tasks:
    - Break into 2-hour maximum chunks
```

### Schema Resolution

When determining which schema to use, OPSX checks in order:

1. **CLI flag**: `--schema <name>` (highest priority)
2. **Change metadata**: `.openspec-hw2.yaml` in the change directory
3. **Project config**: `openspec-hw2/config.yaml`
4. **Default**: `spec-driven`

### Available Schemas

| Schema | Artifacts | Best For |
|--------|-----------|----------|
| `spec-driven` | proposal → specs → design → tasks | Most projects |

List all available schemas:

```bash
openspec-hw2 schemas
```

### Custom Schemas

Create your own workflow:

```bash
openspec-hw2 schema init my-workflow
```

Or fork an existing one:

```bash
openspec-hw2 schema fork spec-driven my-workflow
```

See [Customization](customization.md) for details.

---

## Troubleshooting

### "Legacy files detected in non-interactive mode"

You're running in a CI or non-interactive environment. Use:

```bash
openspec-hw2 init --force
```

### Commands not appearing after migration

Restart your IDE. Skills are detected at startup.

### "Unknown artifact ID in rules"

Check that your `rules:` keys match your schema's artifact IDs:

- **spec-driven**: `proposal`, `specs`, `design`, `tasks`

Run this to see valid artifact IDs:

```bash
openspec-hw2 schemas --json
```

### Config not being applied

1. Ensure the file is at `openspec-hw2/config.yaml` (not `.yml`)
2. Validate YAML syntax
3. Config changes take effect immediately—no restart needed

### project.md not migrated

The system intentionally preserves `project.md` because it may contain your custom content. Review it manually, move useful parts to `config.yaml`, then delete it.

### Want to see what would be cleaned up?

Run init and decline the cleanup prompt—you'll see the full detection summary without any changes being made.

---

## Quick Reference

### Files After Migration

```
project/
├── openspec-hw2/
│   ├── specs/                    # Unchanged
│   ├── changes/                  # Unchanged
│   │   └── archive/              # Unchanged
│   └── config.yaml               # NEW: Project configuration
├── .claude/
│   └── skills/                   # NEW: OPSX skills
│       ├── openspec-hw2-explore/
│       ├── openspec-hw2-new-change/
│       └── ...
├── CLAUDE.md                     # OpenSpec-HW2 markers removed, your content preserved
└── AGENTS.md                     # OpenSpec-HW2 markers removed, your content preserved
```

### What's Gone

- `.claude/commands/openspec-hw2/` — replaced by `.claude/skills/`
- `openspec-hw2/AGENTS.md` — obsolete
- `openspec-hw2/project.md` — migrate to `config.yaml`, then delete
- OpenSpec-HW2 marker blocks in `CLAUDE.md`, `AGENTS.md`, etc.

### Command Cheatsheet

```
/opsx-hw2:new          Start a change
/opsx-hw2:continue     Create next artifact
/opsx-hw2:ff           Create all planning artifacts
/opsx-hw2:apply        Implement tasks
/opsx-hw2:archive      Finish and archive
```

---

## Getting Help

- **Discord**: [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC)
- **GitHub Issues**: [github.com/Fission-AI/OpenSpec-HW2/issues](https://github.com/Fission-AI/OpenSpec-HW2/issues)
- **Documentation**: [docs/opsx.md](opsx.md) for the full OPSX reference
