#!/usr/bin/env python3
"""Install CODEX SWARM policy files into a target repository, conservatively."""
import argparse
from pathlib import Path
import shutil
import sys

START = '<!-- CODEX SWARM START -->'
END = '<!-- CODEX SWARM END -->'
BLOCK = f"""
{START}
## CODEX SWARM adaptive delegation
For substantial engineering tasks, read and follow `.codex/swarm/ORCHESTRATOR.md`,
`.codex/swarm/AGENT_CONTRACT.md`, and `.codex/swarm/PROFILE_PROMOTION.md`.
These policies guide native Codex subagent use when supported; never simulate delegation.
{END}
"""
FILES = ['ORCHESTRATOR.md', 'AGENT_CONTRACT.md', 'PROFILE_PROMOTION.md']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='Target project directory')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        parser.error('Target must be an existing directory')
    for name in FILES:
        src = root / '.codex' / 'swarm' / name
        dst = target / '.codex' / 'swarm' / name
        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                print('UNCHANGED', dst)
                continue
            print('SKIPPED (already exists; review manually)', dst)
            continue
        print('CREATE', dst)
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    agents = target / 'AGENTS.md'
    old = agents.read_text(encoding='utf-8') if agents.exists() else ''
    if START in old or END in old:
        print('UNCHANGED (CODEX SWARM marker exists)', agents)
    else:
        print('APPEND', agents)
        if not args.dry_run:
            if agents.exists():
                backup = agents.with_name('AGENTS.md.bak')
                if backup.exists():
                    print('ERROR: backup already exists; refusing to modify AGENTS.md', file=sys.stderr)
                    return 2
                shutil.copy2(agents, backup)
                print('BACKUP', backup)
            agents.write_text(old.rstrip() + '\n' + BLOCK, encoding='utf-8')
    print('Done. Review files, enable native delegation per your installed Codex version, and start a new session.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
