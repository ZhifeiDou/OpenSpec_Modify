# Change: Adopt Verb–Noun CLI Structure (Deprecate Noun-Based Commands)

## Why

Most widely used CLIs (git, docker, kubectl) start with an action (verb) followed by the object (noun). This matches how users think: “do X to Y”. Using verbs as top-level commands improves clarity, discoverability, and extensibility.

## What Changes

- Promote top-level verb commands as primary entry points: `list`, `show`, `validate`, `diff`, `archive`.
- Deprecate noun-based top-level commands: `openspec-hw2 spec ...` and `openspec-hw2 change ...`.
- Introduce consistent noun scoping via flags where applicable (e.g., `--changes`, `--specs`) and keep smart defaults.
- Clarify disambiguation for `show` and `validate` when names collide.

### Mappings (From → To)

- **List**
  - From: `openspec-hw2 change list`
  - To: `openspec-hw2 list --changes` (default), or `openspec-hw2 list --specs`

- **Show**
  - From: `openspec-hw2 spec show <spec-id>` / `openspec-hw2 change show <change-id>`
  - To: `openspec-hw2 show <item-id>` with auto-detect, use `--type spec|change` if ambiguous

- **Validate**
  - From: `openspec-hw2 spec validate <spec-id>` / `openspec-hw2 change validate <change-id>`
  - To: `openspec-hw2 validate <item-id> --type spec|change`, or bulk: `openspec-hw2 validate --specs` / `--changes` / `--all`

### Backward Compatibility

- Keep `openspec-hw2 spec` and `openspec-hw2 change` available with deprecation warnings for one release cycle.
- Update help text to point users to the verb–noun alternatives.

## Impact

- **Affected specs**:
  - `cli-list`: Add support for `--specs` and explicit `--changes` (default remains changes)
  - `openspec-hw2-conventions`: Add explicit requirement establishing verb–noun CLI design and deprecation guidance
- **Affected code**:
  - `src/cli/index.ts`: Un-deprecate top-level `list`; mark `change list` as deprecated; ensure help text and warnings align
  - `src/core/list.ts`: Support listing specs via `--specs` and default to changes; shared output shape
  - Optional follow-ups: tighten `show`/`validate` help and ambiguity handling

## Explicit Changes

**CLI Design**
- From: Mixed model with nouns (`spec`, `change`) and some top-level verbs; `openspec-hw2 list` currently deprecated
- To: Verbs as primary: `openspec-hw2 list|show|validate|diff|archive`; nouns scoped via flags or item ids; noun commands deprecated
- Reason: Align with common CLIs; improve UX; simpler mental model
- Impact: Non-breaking with deprecation period; users migrate incrementally

**Listing Behavior**
- From: `openspec-hw2 change list` (primary), `openspec-hw2 list` (deprecated)
- To: `openspec-hw2 list` as primary, defaulting to `--changes`; add `--specs` to list specs
- Reason: Consistent verb–noun style; better discoverability
- Impact: New option; preserves existing behavior via default

## Rollout and Deprecation Policy

- Show deprecation warnings on noun-based commands for one release.
- Document new usage in `openspec-hw2/README.md` and CLI help.
- After one release, consider removing noun-based commands, or keep as thin aliases without warnings.

## Open Questions

- Should `show` also accept `--changes`/`--specs` for discovery without an id? (Out of scope here; current auto-detect and `--type` remain.)


