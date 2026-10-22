# SWARM Knowledge Engine — installation and operation

This is an optional skill pack for CODEX SWARM, combining the *ideas* of session memory, project wiki, and budget-aware retrieval. It does not bundle or execute Claude-Mem, OpenWiki, TokenWar, Graphify, or their dependencies.

## Install into CODEX SWARM
Copy `skills/swarm-knowledge-engine/SKILL.md` and `scripts/swarm_knowledge.py` into the matching paths in your CODEX SWARM repository. For a target project, run the script with `--target /path/to/project`. Codex must have instructions to discover the skill; add the following line to the target project's `AGENTS.md`:

> For substantial coding tasks, consult the optional `skills/swarm-knowledge-engine/SKILL.md` and run its local retrieval tool before redundant repository exploration, if installed. Follow user approval and privacy rules.

**Important:** A skill stored only in the separate CODEX SWARM toolkit repository may not be discoverable in the target project's Codex session. Either install it using your Codex version's supported skill location or copy it into your target project and adjust the script path. This pack does not auto-register itself.

## Setup
Python 3.9+ standard library only. No API keys. For the target project, add `.swarm/` to `.gitignore` if you do not want local memory committed. Approved documentation belongs under `docs/knowledge/` and can be versioned in Git.

## Usage
```bash
python scripts/swarm_knowledge.py --target ../my-project doctor
python scripts/swarm_knowledge.py --target ../my-project remember --topic "Database query" --status success --summary "Index on customer_id fixed slow lookup; verified with EXPLAIN" --source "commit abc123"
python scripts/swarm_knowledge.py --target ../my-project recall "slow customer database query" --budget 800
```

## Design boundaries
- Manual opt-in capture; **not** automatic conversation-history ingestion.
- Lexical relevance search; **not** embeddings, semantic similarity or live code graph.
- Approximate context budget; **not** measured API usage or provider billing.
- Wiki pages must be created/approved by a developer; **not** automatic OpenWiki generation.
- SQLite database is project-local; no cross-project memory by default.
- Future integrations can add optional Claude-Mem/Graphify/TokenWar adapters after license, version and security reviews.

## Verification
Run `python -m unittest discover -s tests -v` in this package. Run Codex-native delegation separately; this skill does not create agents.
