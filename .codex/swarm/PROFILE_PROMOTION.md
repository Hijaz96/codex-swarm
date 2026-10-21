# Reusable profile promotion policy

Temporary task-specific subagents are the default. Propose a persistent project role only if:

1. The specialty is repeatedly needed for this repository.
2. The scope is stable and distinct from existing roles.
3. A profile would materially improve consistency or delegation.
4. The user approves creation or update.

Proposal must include: role name, evidence of recurring need, boundaries, expected benefits, and exact config diff. Check the current Codex documentation for the supported role syntax before editing. Avoid storing secrets or task-specific data in profiles. Store project roles under `.codex/agents/` only if supported by the installed version; register them in the appropriate Codex config. Never silently edit `~/.codex/config.toml`.
