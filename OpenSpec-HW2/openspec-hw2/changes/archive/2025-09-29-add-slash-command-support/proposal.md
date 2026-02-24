# Add Slash Command Support for Coding Agents

## Summary
- Enable OpenSpec-HW2 to generate and update custom slash commands for supported coding agents (Claude Code and Cursor).
- Provide three slash commands aligned with OpenSpec-HW2's workflow: proposal (start a change proposal), apply (implement), and archive.
- Share slash command templating between agents to make future extensions simple.

## Motivation
Developers use different coding agents and editors. Having consistent slash commands across tools for the OpenSpec-HW2 workflow reduces friction and ensures a standard way to trigger the workflow. Supporting both Claude Code and Cursor now lays a foundation for future agents that introduce slash command features.

## Proposal
1. During `openspec-hw2 init`, when a user selects a supported tool, generate slash command configuration for three OpenSpec-HW2 workflow stages:
   - Claude (namespaced): `/openspec-hw2/proposal`, `/openspec-hw2/apply`, `/openspec-hw2/archive`.
   - Cursor (flat, prefixed): `/openspec-hw2-proposal`, `/openspec-hw2-apply`, `/openspec-hw2-archive`.
   - Semantics:
     - Create – scaffold a change (ID, `proposal.md`, `tasks.md`, delta specs); validate strictly.
     - Apply – implement an approved change; complete tasks; validate strictly.
     - Archive – archive after deployment; update specs if needed.
   - Each command file MUST embed concise, step-by-step instructions sourced from `openspec-hw2/README.md` (see Template Content section).
2. Store slash command files per tool:
   - Claude Code: `.claude/commands/openspec-hw2/{proposal,apply,archive}.md`
   - Cursor: `.cursor/commands/{openspec-hw2-proposal,openspec-hw2-apply,openspec-hw2-archive}.md`
   - Ensure nested directories are created.
3. Command file format and metadata:
   - Use Markdown with optional YAML frontmatter for tool metadata (name/title, description, category/tags) when supported by the tool.
   - Place OpenSpec-HW2 markers around the body only, never inside frontmatter.
   - Keep the visible slash name, file name, and any frontmatter `name`/`id` consistently aligned (e.g., `proposal`, `openspec-hw2-proposal`).
   - Namespacing: categorize these under “OpenSpec-HW2” and prefer unique IDs (e.g., `openspec-hw2-proposal`) to avoid collisions.
4. Centralize templates: define command bodies once and reuse across tools; apply minimal per-tool wrappers (frontmatter, categories, filenames).
5. During `openspec-hw2 update`, refresh only existing slash command files (per-file basis) within markers; do not create missing files or new tools.

## Design Ideas
- Introduce `SlashCommandConfigurator` to manage multiple files per tool.
  - Expose targets rather than a single `configFileName` (e.g., `getTargets(): Array<{ path: string; kind: 'slash'; id: string }>`).
  - Provide `generateAll(projectPath, openspecHw2Dir)` for init and `updateExisting(projectPath, openspecHw2Dir)` for update.
- Per-tool adapters add only frontmatter and pathing; bodies come from shared templates.
- Templates live in `TemplateManager` with helpers that extract concise, authoritative snippets from `openspec-hw2/README.md`.
- Update flow logs per-file results so users see exactly which slash files were refreshed.

### Marker Placement
- Markers MUST wrap only the Markdown body contents:
  - Frontmatter (if present) goes first.
  - Then `<!-- OPENSPEC-HW2:START -->` … body … `<!-- OPENSPEC-HW2:END -->`.
  - Avoid inserting markers into the YAML block to prevent parse errors.

### Idempotency and Creation Rules
- `init`: create all three files for the chosen tool(s) once; subsequent `init` runs are no-ops for existing files.
- `update`: refresh only files that exist; skip missing ones without creating new files.
- Directory creation for `.claude/commands/openspec-hw2/` and `.cursor/commands/` is the configurator’s responsibility.

### Command Naming & UX
- Claude Code: use namespacing in the slash itself for readability and grouping: `/openspec-hw2/proposal`, `/openspec-hw2/apply`, `/openspec-hw2/archive`.
- Cursor: use flat names with an `openspec-hw2-` prefix: `/openspec-hw2-proposal`, `/openspec-hw2-apply`, `/openspec-hw2-archive`. Group via `category: OpenSpec-HW2` when supported.
- Consistency: align file names, visible slash names, and any frontmatter `id` (e.g., `id: openspec-hw2-apply`).
- Migration: do not rename existing commands during `update`; apply new naming only on `init` (or via an explicit migrate step).

## Open Questions
- Validate exact metadata/frontmatter supported by each tool version; if unsupported, omit frontmatter and ship Markdown body only.
- Confirm the final Cursor command file location for the targeted versions; fall back to Markdown-only if Cursor does not parse frontmatter.
- Evaluate additional commands beyond the initial three (e.g., `/show-change`, `/validate-all`) based on user demand.

## Alternatives
- Hard-code slash command text per tool (rejected: duplicates content; increases maintenance).
- Delay Cursor support until its config stabilizes (partial accept): gate Cursor behind a feature flag until verified in real environments.

## Risks
- Tool configuration formats may change, requiring updates to wrappers/frontmatter.
- Incorrect paths or categories can hide commands; add path existence checks and clear logging.
- Marker misuse (inside frontmatter) can break parsing; enforce placement rules in tests.

## Future Work
- Support additional editors/agents that expose slash command APIs.
- Allow users to customize command names and categories during `openspec-hw2 init`.
- Provide a dedicated command to regenerate slash commands without running full `update`.

## File Format Examples
The following examples illustrate expected structure. If a tool does not support frontmatter, omit the YAML block and keep only the markers + body.

### Claude Code: `.claude/commands/openspec-hw2/proposal.md`
```markdown
---
name: OpenSpec-HW2: Proposal
description: Scaffold a new OpenSpec-HW2 change and validate strictly.
category: OpenSpec-HW2
tags: [openspec-hw2, change]
---
<!-- OPENSPEC-HW2:START -->
...command body from shared template...
<!-- OPENSPEC-HW2:END -->
```

Slash invocation: `/openspec-hw2/proposal` (namespaced)

### Cursor: `.cursor/commands/openspec-hw2-proposal.md`
```markdown
---
name: /openspec-hw2-proposal
id: openspec-hw2-proposal
category: OpenSpec-HW2
description: Scaffold a new OpenSpec-HW2 change and validate strictly.
---
<!-- OPENSPEC-HW2:START -->
...command body from shared template...
<!-- OPENSPEC-HW2:END -->
```

Slash invocation: `/openspec-hw2-proposal` (flat, prefixed)

## Template Content
Templates should be brief, actionable, and sourced from `openspec-hw2/README.md` to avoid duplication. Each command body includes:
- Guardrails: ask 1–2 clarifying questions if needed; follow minimal-complexity rules; use `pnpm` for Node projects.
- Step list tailored to the workflow stage (proposal, apply, archive), including strict validation commands.
- Pointers to `openspec-hw2 show`, `openspec-hw2 list`, and troubleshooting tips when validation fails.

## Testing Strategy
- Golden snapshots for generated files per tool (frontmatter + markers + body).
- Partial presence tests: if 1–2 files exist, `update` only refreshes those and does not create missing ones.
- Marker placement tests: ensure markers never appear inside frontmatter; cover missing/duplicated marker recovery behavior.
- Logging tests: `update` reports per-file updates for slash commands.
