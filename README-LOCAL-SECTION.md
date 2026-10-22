
## Local-only installation (consolidated layout)

CODEX SWARM now supports a consolidated installation under `.codex/swarm/` in target applications. The installer adds local Git exclusions in `.git/info/exclude` so toolkit files, generated profiles, and an untracked SWARM `AGENTS.md` are not accidentally committed. It refuses to modify an already Git-tracked root `AGENTS.md`. Existing SWARM installations need manual migration of old paths and policies.

```bash
python /path/to/codex-swarm/scripts/install.py --target /path/to/your-app --dry-run
python /path/to/codex-swarm/scripts/install.py --target /path/to/your-app
```

See [local-only installation and migration](docs/LOCAL-ONLY-INSTALLATION.md). Git exclusions do **not** control what Codex sends to its service or what is included in deployment artifacts.
