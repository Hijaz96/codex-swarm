## Optional SWARM Knowledge Engine

The [SWARM Knowledge Engine](docs/INSTALL-KNOWLEDGE-ENGINE.md) adds project-local **session memory**, **approved project wiki retrieval**, and **budget-aware context selection**. It is inspired by Claude-Mem, OpenWiki and TokenWar, but does not bundle those upstream tools or automatically capture Codex conversations.

**Start here:** [Install and use the Knowledge Engine](docs/INSTALL-KNOWLEDGE-ENGINE.md) · [Skill instructions](skills/swarm-knowledge-engine/SKILL.md) · [Technical reference](docs/KNOWLEDGE-ENGINE.md).

The add-on must be copied into the target project and referenced by its `AGENTS.md`; uploading it to the CODEX SWARM repository alone does not activate it. Native skill discovery depends on the Codex version.
