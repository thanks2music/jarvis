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
├── design-workflow.md               ← Design tool decision guide (Claude Design / Figma / skills), adoption criteria for third-party design tools
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
├── session-history.md               ← Session JSONL store, --resume cwd matching, safe directory-rename procedure, Zed/ACP visibility
├── harness.md                       ← Anthropic's agentic harness design guide
├── best-practices.md                ← ClaudeCode best practices (kept fresh via the claude-docs-sync skill)
├── claude-tag.md                    ← Claude Tag (org-shared @Claude in Slack) — which repo config loads, session/sandbox model, per-scope permissions, usage billing
├── github-actions-claude-code-review.md ← GitHub Actions claude[bot] PR review setup (2-layer permissions, troubleshooting)
├── zed.md                           ← Zed editor guide (ACP host for Claude Code, shortcuts, dev workflow, parallel agents)
├── zed-shortcuts.md                 ← Personal cheatsheet for the customized keymap.json (multi-project navigation, mnemonics, troubleshooting)
├── model-comparison.md              ← Claude model comparison and plan-limit consumption (Fable 5 / Opus 5 / Sonnet 5 / Haiku 4.5, Fable 5 promotional access ended 2026-07-19)
├── llm-api-pricing-comparison.md    ← Cross-vendor LLM API pricing & specs (Anthropic / OpenAI / Google) — unit prices, caching & batch discounts, long-context surcharges, image-token formulas
├── remote-async-communication.md    ← Remote work & async communication practices for small teams — sync/async criteria, reaction-vs-reply boundary, response-time norms, by-team-size adoption ladder, failure patterns
├── diagrams/                        ← Mermaid / image assets referenced from the docs above
└── sync-reports/                    ← Dated diff reports produced by the claude-docs-sync skill

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

> **The entries below are plain Markdown links, not `@`-imports** — Claude reads each on demand, so they stay out of always-loaded context. Persona files, `.jarvis/CLAUDE.md`, and `profile.md` remain `@`-imports because they must always be present.

<!--
Maintainer rationale — kept out of Claude's context on purpose: block-level HTML comments in
CLAUDE.md are stripped before injection (https://code.claude.com/docs/en/memory; see also
docs/memory.md "HTML コメントで Claude から隠す"). Visible to humans opening this file, zero context cost.

Why plain links instead of @-imports:
- @-imports are expanded and loaded at launch (Manage memory: "imported files load at launch"),
  so listing every reference doc as an @-import kept the whole docs/ tree in each session's base
  context — measured ~192k tokens (~19%) per session. Converting to links dropped Memory files
  from 215k to ~24k, verified in a fresh session.
- Official guidance for shrinking always-loaded context is to move specialized instructions into
  skills or path-scoped rules (Manage costs: "Move instructions from CLAUDE.md to skills"). Plain
  links are a lighter-weight step for pure reference docs; a link has no auto-firing mechanism
  (unlike a skill's description match), so Claude reads on demand.
- Do NOT convert these back to @-imports without re-checking cost via /context.
- Follow-up (claude[bot] review, PR #12): some converted files (e.g. best-practices.md, hooks.md)
  double as operational guides. If on-demand reading of one stops being reliable in practice,
  promote just that file to a path-scoped rule under .claude/rules/ rather than reverting to @-import.
-->

- Project overview: [README.md](README.md)
- Tool stack: [docs/tool-stack.md](docs/tool-stack.md)
- Design workflow & tool decision guide: [docs/design-workflow.md](docs/design-workflow.md)
- Configuration files: [docs/config-files.md](docs/config-files.md)
- Claude Desktop: [docs/claude-desktop.md](docs/claude-desktop.md)
- MCP setup: [docs/mcp-setup.md](docs/mcp-setup.md)
- Slash commands: [docs/slash-commands.md](docs/slash-commands.md)
- Skills guide: [docs/skills.md](docs/skills.md)
- Skills progressive disclosure: [docs/skills-progressive-disclosure.md](docs/skills-progressive-disclosure.md)
- Plugins guide: [docs/plugins.md](docs/plugins.md)
- SubAgents guide: [docs/sub-agents.md](docs/sub-agents.md)
- Hooks guide: [docs/hooks.md](docs/hooks.md)
- Memory (CLAUDE.md) guide: [docs/memory.md](docs/memory.md)
- Session history & `--resume` guide: [docs/session-history.md](docs/session-history.md)
- Harness design guide: [docs/harness.md](docs/harness.md)
- Best practices: [docs/best-practices.md](docs/best-practices.md)
- Claude Tag (Slack) guide: [docs/claude-tag.md](docs/claude-tag.md)
- GitHub Actions Claude Code review: [docs/github-actions-claude-code-review.md](docs/github-actions-claude-code-review.md)
- Zed editor guide: [docs/zed.md](docs/zed.md)
- Zed shortcuts cheatsheet: [docs/zed-shortcuts.md](docs/zed-shortcuts.md)
- Model comparison & plan limits: [docs/model-comparison.md](docs/model-comparison.md)
- LLM API pricing comparison (Anthropic / OpenAI / Google): [docs/llm-api-pricing-comparison.md](docs/llm-api-pricing-comparison.md)
- Remote work & async communication: [docs/remote-async-communication.md](docs/remote-async-communication.md)
- JARVIS Plugin guide (local-only): [docs/jarvis/jarvis-plugin.md](docs/jarvis/jarvis-plugin.md)
- JARVIS Plugin architecture (local-only): [docs/jarvis/jarvis-plugin-architecture.md](docs/jarvis/jarvis-plugin-architecture.md)
- JARVIS × harness integration (local-only): [docs/jarvis/jarvis-harness-integration.md](docs/jarvis/jarvis-harness-integration.md)
- **JARVIS virtual-org structure (always loaded)**: @.jarvis/CLAUDE.md
- Private profile (local-only): @docs/private/profile.md

> **Why `.jarvis/CLAUDE.md` is always loaded**: By the JARVIS Plugin's default design, `.jarvis/CLAUDE.md` loads only via the `/jarvis` skill. As an operating policy, however, BOSS wants department-aware routing and judgment to work even in a normal Claude session (without invoking `/jarvis`), so this repository imports it at all times. Each department's own `CLAUDE.md` loads on demand when its folder is touched.

## Best Practices Update Policy

`docs/best-practices.md` is an important document built by carefully reading and analyzing the official ClaudeCode documentation. Because best practices change continuously as ClaudeCode evolves, **editing is permitted, on the premise that updates are grounded in official primary sources (English)**. The former "do-not-edit (sanctuary)" designation has been lifted.

- Prefer updating through the `claude-docs-sync` skill (`/claude-docs-sync`), which researches the latest official information and applies changes safely via: diff report → BOSS approval → apply.
- When editing manually, always ground changes in official primary sources and record the source URL and the update date.
- For model-generation notes, append (keep the history) rather than replace, so the evolution stays traceable.

> **Where the `claude-docs-sync` skill lives**: the skill body is **not** in this repository. Every ClaudeCode skill and plugin is version-controlled in the private `avengers` repository, and this one is no exception — the real files are at `avengers/dot-claude/global/skills/claude-docs-sync/`, symlinked into `.claude/skills/claude-docs-sync` here.
>
> - **Edit it on the avengers side**, then commit there. Editing through the symlink also writes to avengers (the only copy), so that path works too — just remember the commit belongs to avengers.
> - It stays a **project-scope** skill on purpose. It is JARVIS-repository-specific (it exits early unless `docs/` and the fingerprint files are present), so putting it in `~/.claude/skills/` would load its description into every other project's context for no benefit. Official docs confirm a project-location skill entry may be a symlink, so scope and single-source management are not in conflict here.
> - The symlink itself is gitignored (it would otherwise commit an absolute local path to a public repo). `.claude/skills/.gitkeep` keeps the directory tracked so `avengers/bootstrap.sh` has somewhere to place the link after a fresh clone.

## Operating Principles (decision criteria)

Make proposals and updates in line with the principles stated in the README:

- **Progress over perfection**: improve step by step rather than chasing the ideal.
- **AI as a tool, humans at the helm**: design, decisions, and accountability always rest with the human.
- **Document for reproducibility**: record specifics so the same setup can be rebuilt in any environment.
- **Keep it fresh**: actively update or remove outdated information.

## Git / GitHub Workflow (this repo)

This repo authorizes JARVIS to run the full delivery loop autonomously on an explicit request, without pausing between steps:

commit → push → PR (English title & body) → respond to AI review (claude[bot] / Copilot), each finding verified against official primary sources → fix → push.

- Use `/git-commit` for commits and `/review-all-ai` for AI-review responses; do not restate their procedures here.
- **PR titles and bodies are written in English** (consistent with the committed, public-facing config). Docs deliverables stay Japanese.
- `gh pr merge` and force-push (`git push --force` / `-f` / `--force-with-lease`) remain **human-only**.
- The no-confirmation permissions are defined deterministically in `.claude/settings.json` (`permissions.allow` / `deny`) — not here. CLAUDE.md only declares intent; `settings.json` enforces it (deny takes precedence across all scopes, overriding broader allows in `settings.local.json`).
