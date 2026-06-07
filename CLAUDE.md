# CLAUDE.md — JARVIS Operating Manual

> **JARVIS** (Just a Really Very Intelligent System) — the persona of the ClaudeCode instance operating in this repository.

<!-- JARVIS persona, tone, and research rules live in local-only files (gitignored) and are imported below. -->
@docs/private/jarvis-identity.md
@docs/private/jarvis-tone.md
@docs/private/jarvis-research-rules.md

## Repository Overview

**JARVIS** is the personal repository of @thanks2music. It documents the trial-and-error, experiments, and verification of AI-powered development centered on ClaudeCode, and collects the current best practices. It is entirely personal — not shared with any team or community.

- **GitHub**: https://github.com/thanks2music/jarvis

## Language & Writing Conventions

- **This root `CLAUDE.md` is written in English.** It is an instruction file for Claude, kept in English for token efficiency and as the committed, public-facing config.
- **All deliverables are written in Japanese.** Everything under `docs/` uses Japanese in plain form (だ・である調). `README.md` uses a hybrid layout: English first, Japanese below.
- Keep technical terms in their original English form (ClaudeCode, MCP, GitHub, etc.).
- The imported JARVIS persona files above are intentionally kept in Japanese for the owner's readability (local-only, gitignored).

## Documentation Structure

`README.md` serves as the overview and table of contents; detailed docs live under `docs/`.

```
README.md                            ← overview, principles, doc links
docs/
├── tool-stack.md                    ← tool stack in use
├── config-files.md                  ← ClaudeCode configuration files and their roles
├── claude-desktop.md                ← Claude Desktop configuration files
├── mcp-setup.md                     ← MCP server setup guide
├── slash-commands.md                ← ClaudeCode slash commands guide
├── skills.md                        ← ClaudeCode Skills guide
├── skills-progressive-disclosure.md ← Skills progressive disclosure design
├── plugins.md                       ← ClaudeCode Plugins guide
├── sub-agents.md                    ← ClaudeCode SubAgents guide
├── hooks.md                         ← ClaudeCode Hooks guide
├── memory.md                        ← Memory (CLAUDE.md) system guide
├── harness.md                       ← Anthropic's agentic harness design guide
└── best-practices.md                ← ClaudeCode best practices (kept fresh via the claude-docs-sync skill)

# local-only (gitignored)
docs/jarvis/
├── jarvis-plugin.md                 ← /jarvis Plugin usage guide
├── jarvis-plugin-architecture.md    ← /jarvis Plugin internal design
└── jarvis-harness-integration.md    ← JARVIS × harness integration guide
docs/private/
├── jarvis-identity.md               ← JARVIS definition & organization (imported above)
├── jarvis-tone.md                   ← JARVIS tone & manner (imported above)
├── jarvis-research-rules.md         ← JARVIS research rules (imported above)
└── profile.md                       ← owner private profile
```

## Documentation References

- Project overview: @README.md
- Tool stack: @docs/tool-stack.md
- Configuration files: @docs/config-files.md
- Claude Desktop: @docs/claude-desktop.md
- MCP setup: @docs/mcp-setup.md
- Slash commands: @docs/slash-commands.md
- Skills guide: @docs/skills.md
- Skills progressive disclosure: @docs/skills-progressive-disclosure.md
- Plugins guide: @docs/plugins.md
- SubAgents guide: @docs/sub-agents.md
- Hooks guide: @docs/hooks.md
- Memory (CLAUDE.md) guide: @docs/memory.md
- Harness design guide: @docs/harness.md
- Best practices: @docs/best-practices.md
- JARVIS Plugin guide (local-only): @docs/jarvis/jarvis-plugin.md
- JARVIS Plugin architecture (local-only): @docs/jarvis/jarvis-plugin-architecture.md
- JARVIS × harness integration (local-only): @docs/jarvis/jarvis-harness-integration.md
- **JARVIS virtual-org structure (always loaded)**: @.jarvis/CLAUDE.md
- Private profile (local-only): @docs/private/profile.md

> **Why `.jarvis/CLAUDE.md` is always loaded**: By the JARVIS Plugin's default design, `.jarvis/CLAUDE.md` loads only via the `/jarvis` skill. As an operating policy, however, BOSS wants department-aware routing and judgment to work even in a normal Claude session (without invoking `/jarvis`), so this repository imports it at all times. Each department's own `CLAUDE.md` loads on demand when its folder is touched.

## Best Practices Update Policy

`docs/best-practices.md` is an important document built by carefully reading and analyzing the official ClaudeCode documentation. Because best practices change continuously as ClaudeCode evolves, **editing is permitted, on the premise that updates are grounded in official primary sources (English)**. The former "do-not-edit (sanctuary)" designation has been lifted.

- Prefer updating through the `claude-docs-sync` skill (`/claude-docs-sync`), which researches the latest official information and applies changes safely via: diff report → BOSS approval → apply.
- When editing manually, always ground changes in official primary sources and record the source URL and the update date.
- For model-generation notes, append (keep the history) rather than replace, so the evolution stays traceable.

## Operating Principles (decision criteria)

Make proposals and updates in line with the principles stated in the README:

- **Progress over perfection**: improve step by step rather than chasing the ideal.
- **AI as a tool, humans at the helm**: design, decisions, and accountability always rest with the human.
- **Document for reproducibility**: record specifics so the same setup can be rebuilt in any environment.
- **Keep it fresh**: actively update or remove outdated information.
