# Installing CODEX SWARM

> **CODEX SWARM** is a project-level instruction and configuration toolkit for the **official OpenAI Codex extension in Visual Studio Code**. It is **not** a separate VS Code extension or a GitHub Copilot Chat agent. Native subagent execution requires a compatible Codex version and available delegation tools.

## Requirements

- [Visual Studio Code](https://code.visualstudio.com/)
- The official **OpenAI Codex** VS Code extension, signed in to a supported account
- [Git](https://git-scm.com/)
- Python **3.9 or newer** (`python --version`; on Windows you may need `py --version`)
- An existing local software project you can open in VS Code

You can keep GitHub Copilot installed, but open **Codex** for the steps below.

## 1. Install Codex in VS Code

1. Open VS Code.
2. Open **Extensions** (`Ctrl+Shift+X` on Windows/Linux or `Cmd+Shift+X` on macOS).
3. Search for **Codex** and select the official extension published by **OpenAI**.
4. Install it, open its panel, and sign in.
5. Open the software project where you want SWARM to work.

## 2. Download CODEX SWARM

Open **Terminal → New Terminal** in VS Code and clone the repository. For example, if you keep projects under a shared parent folder:

```bash
git clone https://github.com/Hijaz96/codex-swarm.git
```

Keep `codex-swarm` **next to** the target project, rather than inside it. Example:

```text
Projects/
├── codex-swarm/        # downloaded toolkit
└── my-application/     # your own project
```

Alternatively, download the repository as a ZIP from GitHub and extract it beside your project.

## 3. Preview installation

Open **your own project** in VS Code. From its root directory, run the installer using the path to the downloaded toolkit.

**Windows (PowerShell)** — if both directories are under `C:\Projects`:

```powershell
cd C:\Projects\my-application
python ..\codex-swarm\scripts\install.py --target . --dry-run
```

If Windows does not recognize `python`, try `py` instead.

**macOS / Linux** — if both directories are under `~/Projects`:

```bash
cd ~/Projects/my-application
python ../codex-swarm/scripts/install.py --target . --dry-run
```

The `--dry-run` command only previews changes. Review its output before proceeding.

## 4. Install into your project

From the same project directory, rerun the command **without** `--dry-run`.

**Windows:**

```powershell
python ..\codex-swarm\scripts\install.py --target .
```

**macOS / Linux:**

```bash
python ../codex-swarm/scripts/install.py --target .
```

Your project will gain the following instruction files:

```text
my-application/
├── AGENTS.md
└── .codex/
    └── swarm/
        ├── ORCHESTRATOR.md
        ├── AGENT_CONTRACT.md
        └── PROFILE_PROMOTION.md
```

- `AGENTS.md` points Codex to the SWARM policies.
- `ORCHESTRATOR.md` describes project discovery, specialist selection, and integration.
- `AGENT_CONTRACT.md` defines boundaries and deliverables for delegated work.
- `PROFILE_PROMOTION.md` explains when reusable specialist profiles may be proposed.

**Safety:** The installer skips differing existing SWARM policy files rather than overwriting them. It backs up an existing root `AGENTS.md` before appending the SWARM instruction block. If `AGENTS.md.bak` already exists and an append is needed, the installer refuses that modification; resolve the backup conflict before retrying. The installer does not change global Codex configuration.

## 5. Enable native multi-agent support, if available

Open the Codex configuration file that **your extension actually loads** (commonly `~/.codex/config.toml`, or `%USERPROFILE%\.codex\config.toml` on Windows).

For versions that support this feature flag, add:

```toml
[features]
multi_agent = true
```

If a `[features]` section already exists, **add only** `multi_agent = true` within that section. Do not duplicate TOML tables or overwrite other settings.

Native subagent support, settings, and UI controls can change by release. Check the [official Codex documentation](https://developers.openai.com/codex/) for the version you have installed. If your version does not expose delegation tools, the SWARM policy alone cannot activate them.

**Start a new Codex conversation** after installing and updating configuration.

## 6. Use SWARM for a normal development task

Open Codex in your target project and ask naturally, for example:

> Build a responsive customer dashboard with customer statistics, search, filtering, and role-based permissions. Follow this repository's existing architecture. Run relevant tests and report your findings.

The SWARM instructions ask the lead Codex agent to inspect the project, choose task-specific expertise, delegate independent work when native tools are available, coordinate contracts, integrate changes, and verify the result. You do **not** have to choose from a fixed list of agents.

For simple tasks, Codex may work alone. For dependent tasks, it may work sequentially. More agents do not always mean better results.

## 7. Verify real subagent delegation

Use a **new Codex session** and paste this **read-only** smoke test:

> Inspect this repository using three independent read-only specialist subagents, where native delegation is available: (1) architecture, (2) test coverage, and (3) security-sensitive surfaces. Do not modify files. Report actual subagent creation/activity evidence, each specialist's findings, and whether their execution overlapped. If native delegation is unavailable, say so explicitly.

**Pass criteria:** Codex session activity shows real subagent/delegation operations and separate findings returned to the lead. Merely printing headings such as “Agent 1” and “Agent 2” is **not** proof of multi-agent execution. Read the [verification examples](../examples/verify-delegation.md).

## 8. Reusable specialists (adaptive hybrid)

Temporary specialists are the default. When a role is repeatedly useful for your project, the lead may **propose** a reusable project-specific agent profile. Review its scope and exact configuration before approving it. Profiles are instruction/configuration files, **not trained models**, and profile creation is **not automatic** in this starter kit.

## 9. Update or remove SWARM

To download toolkit updates, open the downloaded `codex-swarm` directory and run:

```bash
git pull
```

Then review the new policy files before applying them to an existing project. **Re-running the installer does not overwrite differing existing SWARM policy files**, so updating installed policies is a manual review/merge step.

To remove SWARM, delete the SWARM instruction block between `<!-- CODEX SWARM START -->` and `<!-- CODEX SWARM END -->` in the target project's `AGENTS.md`, then delete `.codex/swarm/` if you no longer need it. Preserve unrelated project instructions. If you enabled `multi_agent` only for SWARM, you may remove that setting separately. No automatic uninstaller is included.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `python` not found | Install Python 3.9+, check PATH, or try `py` on Windows. |
| Installer says target does not exist | Open your target project and check the `--target` path. |
| Installer skips a policy file | An existing file differs; compare it and merge manually. |
| Installer refuses `AGENTS.md` append | Check the existing `AGENTS.md.bak` and resolve the backup conflict. |
| Codex ignores SWARM | Confirm you opened the **target project**, `AGENTS.md` is in its root, and you started a new Codex session. |
| No subagents appear | Check Codex version, feature availability, trusted project settings, and actual native delegation tools. |
| Agent names appear without activity | Treat delegation as **unverified**; run the read-only smoke test. |
| You only see GitHub Copilot Chat | Open the official **OpenAI Codex** extension; this is not a native Copilot extension. |

## Current limitations

CODEX SWARM is a configuration and instruction starter kit. It does **not** ship a separate agent runtime, a background daemon, guaranteed parallel execution, an automatic profile-training system, or a native GitHub Copilot integration. Actual behavior depends on the installed Codex runtime and project environment.

[Back to README](../README.md) · [Report an issue](https://github.com/Hijaz96/codex-swarm/issues)
