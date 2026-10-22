# CODEX SWARM

**Adaptive, project-aware delegation for OpenAI Codex.**

CODEX SWARM is an open-source **instruction and configuration starter kit**, not a separate agent runtime or VS Code extension. It asks Codex to inspect each repository, choose useful specialist subagents for each task, coordinate independent work, and propose reusable project-specific agent profiles when they prove valuable.

> **Compatibility:** Native delegation depends on your installed Codex version, enabled features, trust settings, and available tools. The prompt alone cannot create or force subagents. Verify actual spawn events in your Codex session. Configuration flags can change across releases.

## Features

- Project-aware specialist selection, not a fixed roster
- Parallel delegation where native Codex subagents are available
- Task contracts and file ownership to reduce collisions
- Human-approved promotion of repeat roles into persistent agent profiles
- Read-only delegation smoke test
- Conservative, reversible installation

## Quick start

Requires Python 3.9+, Git (recommended), VS Code with the official Codex extension, and a Codex version that exposes native multi-agent delegation.

1. Download or clone this repository.
2. From your target project's root run:

   ```bash
   python /path/to/codex-swarm/scripts/install.py --target . --dry-run
   python /path/to/codex-swarm/scripts/install.py --target .
   ```

3. Review the added `AGENTS.md` section and `.codex/swarm/ORCHESTRATOR.md`.
4. Enable native multi-agent support **only if documented for your installed Codex version**. A commonly documented setting is:

   ```toml
   [features]
   multi_agent = true
   ```

   Put this in the Codex config file your extension actually loads (often `~/.codex/config.toml`); do not blindly overwrite an existing `[features]` table. Check current [Codex documentation](https://developers.openai.com/codex/) for version-specific configuration. Some releases expose multi-agent via an experimental feature toggle.
5. Start a **new Codex session** and paste `examples/verify-delegation.md` test prompt.

## Installation & Getting Started

New to CODEX SWARM? Follow the [step-by-step installation guide](docs/INSTALLATION.md) to install, configure, and verify multi-agent delegation in VS Code.

### What gets installed?

- `.codex/swarm/ORCHESTRATOR.md`: adaptive delegation policy
- `.codex/swarm/AGENT_CONTRACT.md`: delegation task template
- `.codex/swarm/PROFILE_PROMOTION.md`: human-approved persistence policy
- An instruction block in root `AGENTS.md` telling Codex to read the above files

Existing files are not silently overwritten. The installer creates `.bak` backups for any preexisting root `AGENTS.md` it modifies. It does **not** change global Codex settings or create permanent agents automatically.

## Architecture

```text
User task
  -> Codex lead (reads AGENTS.md)
     -> inspect repository and identify dependencies
     -> select temporary specialists for independent work
     -> delegate using native subagent tools if available
     -> integrate and test
     -> propose reusable project-specific roles (approval required)
```

## Example

> Implement an accessible customer dashboard with Laravel API endpoints and tests. Inspect the repository first. Delegate independent design, backend, and test-planning work when native subagents are available. Coordinate API contracts before integration. Report actual delegation evidence.

## Limits

- Agent profiles are **not trained models**; they are instructions and configuration.
- A Codex session may decline to delegate or may lack subagent tools.
- Automatic profile promotion is deliberately **approval-gated** and may require explicit file edits.
- Subagents sharing a workspace can collide; assign disjoint files or use separate worktrees where supported.
- No background daemon, autonomous scheduler, or guarantees of simultaneous execution are included.

## Repository layout

```text
.codex/swarm/                 Policy and contract templates
scripts/install.py            Idempotent installer
examples/                     Smoke test and example request
profiles/                     Optional role profile example
.github/                      Issue and PR templates
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues: see [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
