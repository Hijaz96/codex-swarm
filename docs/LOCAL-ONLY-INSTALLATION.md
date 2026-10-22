# CODEX SWARM — local-only installation

This release changes the **target project** layout to `.codex/swarm/` while keeping the toolkit's **public source repository** versioned normally.

## Install into an application (run from the downloaded SWARM source checkout)

```bash
python /path/to/codex-swarm/scripts/install.py --target /path/to/your-app --dry-run
python /path/to/codex-swarm/scripts/install.py --target /path/to/your-app
```

The target application gets `.codex/swarm/` with policies, tools and skills, plus a local root `AGENTS.md` instruction block. Runtime files are generated in `.codex/swarm/data/`. The installer appends patterns to the target checkout's `.git/info/exclude` (not its committed `.gitignore`). This does **not** affect the public SWARM source repository. No network upload is performed by these Python scripts.

## Usage

```bash
python .codex/swarm/tools/swarm_project.py --target . scan
python .codex/swarm/tools/swarm_project.py --target . show
python .codex/swarm/tools/swarm_knowledge.py --target . doctor
```

Optional `.codex/swarm/data/project-preferences.json`:

```json
{"ui_library":"Flux Pro","reactivity":"Livewire","direct_alpine_usage":"disallowed","ui_rules":["Reuse existing Flux components"]}
```

## Migrating an existing installation

1. Back up `.swarm/` if it contains memories/preferences. The new database/profile location is `.codex/swarm/data/`.
2. Install the new version. Existing `.codex/swarm/` files are not silently overwritten: review any `SKIPPED` messages and merge updated `ORCHESTRATOR.md` manually.
3. If an old `AGENTS.md` contains the existing SWARM block, replace its block with the new local paths. The installer does not silently rewrite existing blocks.
4. **Only after verifying the new version works**, remove obsolete legacy scripts/skills from your application checkout. Do not delete the public toolkit source files.
5. If legacy files were already tracked by Git, local exclude rules cannot untrack them. Inspect `git ls-files .codex/swarm .swarm scripts/swarm_project.py scripts/swarm_knowledge.py skills/swarm-project-intelligence skills/swarm-knowledge-engine AGENTS.md` and decide explicitly whether to untrack with `git rm --cached` or revert any published content. Untracking changes the repository index and will affect future commits; do not do it blindly.

## Privacy and limitations

- `.git/info/exclude` is **local to one Git checkout**. It is not propagated to another machine or worktree.
- Ignoring does not remove files already committed, copied, included in Docker build contexts, uploaded by IDE extensions, or transmitted to an AI service. Add Docker `.dockerignore` rules separately if applicable.
- Codex itself processes project context according to the user's Codex account/service settings. Local Git exclusions do not control model training, data retention or remote processing.
- If root `AGENTS.md` is already Git-tracked, this installer refuses to modify it: otherwise local-only confidentiality would be misleading.
- An existing `.codex/swarm/` installation is preserved on conflicts, so migration requires manual review.
- For truly local-only operation, do not explicitly `git add -f` ignored paths, and inspect `git status` before every commit.
