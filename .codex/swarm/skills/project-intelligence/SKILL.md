---
name: swarm-project-intelligence
description: Discover the project's frameworks, UI libraries, and design conventions before substantial coding.
---
Use `python .codex/swarm/tools/swarm_project.py --target . scan` when project profile is missing or stale; use `show` otherwise. Respect `.codex/swarm/data/project-preferences.json` and verify representative layouts and components. Do not inspect `.env` or credentials.
