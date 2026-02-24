# Supported Tools

OpenSpec-HW2 works with 20+ AI coding assistants. When you run `openspec-hw2 init`, you'll be prompted to select which tools you use, and OpenSpec-HW2 will configure the appropriate integrations.

## How It Works

For each tool you select, OpenSpec-HW2 installs:

1. **Skills** — Reusable instruction files that power the `/opsx-hw2:*` workflow commands
2. **Commands** — Tool-specific slash command bindings

## Tool Directory Reference

| Tool | Skills Location | Commands Location |
|------|-----------------|-------------------|
| Amazon Q Developer | `.amazonq/skills/` | `.amazonq/prompts/` |
| Antigravity | `.agent/skills/` | `.agent/workflows/` |
| Auggie (Augment CLI) | `.augment/skills/` | `.augment/commands/` |
| Claude Code | `.claude/skills/` | `.claude/commands/opsx/` |
| Cline | `.cline/skills/` | `.clinerules/workflows/` |
| CodeBuddy | `.codebuddy/skills/` | `.codebuddy/commands/opsx/` |
| Codex | `.codex/skills/` | `~/.codex/prompts/`\* |
| Continue | `.continue/skills/` | `.continue/prompts/` |
| CoStrict | `.cospec/skills/` | `.cospec/openspec-hw2/commands/` |
| Crush | `.crush/skills/` | `.crush/commands/opsx/` |
| Cursor | `.cursor/skills/` | `.cursor/commands/` |
| Factory Droid | `.factory/skills/` | `.factory/commands/` |
| Gemini CLI | `.gemini/skills/` | `.gemini/commands/opsx/` |
| GitHub Copilot | `.github/skills/` | `.github/prompts/`\*\* |
| iFlow | `.iflow/skills/` | `.iflow/commands/` |
| Kilo Code | `.kilocode/skills/` | `.kilocode/workflows/` |
| Kiro | `.kiro/skills/` | `.kiro/prompts/` |
| OpenCode | `.opencode/skills/` | `.opencode/command/` |
| Qoder | `.qoder/skills/` | `.qoder/commands/opsx/` |
| Qwen Code | `.qwen/skills/` | `.qwen/commands/` |
| RooCode | `.roo/skills/` | `.roo/commands/` |
| Trae | `.trae/skills/` | `.trae/skills/` (via `/openspec-hw2-*`) |
| Windsurf | `.windsurf/skills/` | `.windsurf/workflows/` |

\* Codex commands are installed to the global home directory (`~/.codex/prompts/` or `$CODEX_HOME/prompts/`), not the project directory.

\*\* GitHub Copilot's `.github/prompts/*.prompt.md` files are recognized as custom slash commands in **IDE extensions only** (VS Code, JetBrains, Visual Studio). GitHub Copilot CLI does not currently support custom prompts from this directory — see [github/copilot-cli#618](https://github.com/github/copilot-cli/issues/618). If you use Copilot CLI, you may need to manually set up [custom agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents) in `.github/agents/` as a workaround.

## Non-Interactive Setup

For CI/CD or scripted setup, use the `--tools` flag:

```bash
# Configure specific tools
openspec-hw2 init --tools claude,cursor

# Configure all supported tools
openspec-hw2 init --tools all

# Skip tool configuration
openspec-hw2 init --tools none
```

**Available tool IDs:** `amazon-q`, `antigravity`, `auggie`, `claude`, `cline`, `codebuddy`, `codex`, `continue`, `costrict`, `crush`, `cursor`, `factory`, `gemini`, `github-copilot`, `iflow`, `kilocode`, `kiro`, `opencode`, `qoder`, `qwen`, `roocode`, `trae`, `windsurf`

## What Gets Installed

For each tool, OpenSpec-HW2 generates 10 skill files that power the OPSX workflow:

| Skill | Purpose |
|-------|---------|
| `openspec-hw2-explore` | Thinking partner for exploring ideas |
| `openspec-hw2-new-change` | Start a new change |
| `openspec-hw2-continue-change` | Create the next artifact |
| `openspec-hw2-ff-change` | Fast-forward through all planning artifacts |
| `openspec-hw2-apply-change` | Implement tasks |
| `openspec-hw2-verify-change` | Verify implementation completeness |
| `openspec-hw2-sync-specs` | Sync delta specs to main (optional—archive prompts if needed) |
| `openspec-hw2-archive-change` | Archive a completed change |
| `openspec-hw2-bulk-archive-change` | Archive multiple changes at once |
| `openspec-hw2-onboard` | Guided onboarding through a complete workflow cycle |

These skills are invoked via slash commands like `/opsx-hw2:new`, `/opsx-hw2:apply`, etc. See [Commands](commands.md) for the full list.

## Adding a New Tool

Want to add support for another AI coding assistant? Check out the [command adapter pattern](../CONTRIBUTING.md) or open an issue on GitHub.

---

## Related

- [CLI Reference](cli.md) — Terminal commands
- [Commands](commands.md) — Slash commands and skills
- [Getting Started](getting-started.md) — First-time setup
