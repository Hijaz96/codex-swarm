# CODEX SWARM — Knowledge-first orchestration integration

## What this update changes

- `scripts/install.py` installs the optional Knowledge Engine script and skill alongside SWARM policies. It now preflights incomplete AGENTS.md markers and backup conflicts before writing files.
- `.codex/swarm/ORCHESTRATOR.md` directs the Codex lead to recall relevant project knowledge **before** scanning widely or delegating, validate results against source, and ask approval before saving findings.
- The knowledge engine remains local, opt-in and based on SQLite and Markdown. This does **not** automatically capture Codex conversations or guarantee native delegation.

## Android: update your public GitHub repository

1. Download `codex-swarm-orchestration-integration.zip` into Downloads.
2. In Termux:

```sh
cd ~/codex-upload/codex-swarm
git pull --ff-only origin main
unzip -o ~/storage/downloads/codex-swarm-orchestration-integration.zip -d .
python -m unittest discover -s tests -p 'test_knowledge.py' -v
python -m unittest discover -s tests -p 'test_orchestration_integration.py' -v
git add scripts/install.py .codex/swarm/ORCHESTRATOR.md docs/ORCHESTRATION-INTEGRATION.md tests/test_orchestration_integration.py
git commit -m "Integrate knowledge recall into Codex orchestration"
git push origin main
```

**Important:** This ZIP also contains `scripts/swarm_knowledge.py` and `skills/swarm-knowledge-engine/SKILL.md` to support new installations. Existing copies are not meant to change. Review `git diff` before committing. Do not overwrite unrelated local changes.

## Laptop: install in an existing software project

From the project root, assuming CODEX SWARM is cloned beside it:

```sh
python ../codex-swarm/scripts/install.py --target . --dry-run
python ../codex-swarm/scripts/install.py --target .
```

**Existing SWARM users:** the installer intentionally skips different existing `.codex/swarm/ORCHESTRATOR.md` files. Manually review and merge the new **Knowledge-first discovery** section from the repository into your project's orchestrator policy. The script and skill are installed if missing. Existing AGENTS.md markers are preserved.

Add `.swarm/` to your target project's `.gitignore` so local memory does not enter source control. Verify with `git status` before committing.

## Try the knowledge pipeline

From your project root:

```sh
python scripts/swarm_knowledge.py --target . doctor
python scripts/swarm_knowledge.py --target . remember --topic "customer N+1 query" --status failed --summary "Earlier approach caused excessive memory; verify pagination" --source "manual test"
python scripts/swarm_knowledge.py --target . recall "customer query performance" --budget 800 --limit 5
```

Create a new Codex conversation and ask:

> Investigate customer query performance. Follow CODEX SWARM orchestration instructions. Before broad scanning or delegating, check relevant local knowledge if available, verify it against current code, and tell me whether retrieval actually ran. Do not save memory without asking.

Expected: Codex executes the recall command if relevant and supported, validates findings, then decides whether delegation is worthwhile. A text-only claim is not proof: inspect Codex activity. The `remember` command above is just a manual demonstration, not automatic transcript capture.

## Troubleshooting

- **No recall:** Ensure `scripts/swarm_knowledge.py` exists in the target project and the new orchestrator section was merged; restart Codex session.
- **No memories:** Run `remember` after approval or create approved Markdown under `docs/knowledge/`.
- **No subagents:** Native Codex multi-agent support must be available separately.
- **Secrets:** Basic redaction is best effort; never record credentials or raw private transcripts. Keep `.swarm/` local.
- **Token counts:** `--budget` is approximate, not a verified token meter.
