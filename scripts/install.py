#!/usr/bin/env python3
"""Install CODEX SWARM locally without adding toolkit files to project commits."""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

START = '<!-- CODEX SWARM START -->'
END = '<!-- CODEX SWARM END -->'
BLOCK = f'''\n{START}\n## Local CODEX SWARM\nFor nontrivial development tasks, consult `.codex/swarm/ORCHESTRATOR.md`.\nThe project intelligence and knowledge tools live in `.codex/swarm/tools/`.\nNever read `.env` or secrets for discovery; respect developer preferences.\n{END}\n'''
EXCLUDES = ['/.codex/swarm/', '/AGENTS.md.bak', '/.swarm/', '/scripts/swarm_project.py', '/scripts/swarm_knowledge.py', '/skills/swarm-project-intelligence/', '/skills/swarm-knowledge-engine/']

def git(root, *args):
    p = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    return p

def git_root(target):
    p = git(target, 'rev-parse', '--show-toplevel')
    return Path(p.stdout.strip()).resolve() if p.returncode == 0 else None

def tracked(target, path):
    return git(target, 'ls-files', '--error-unmatch', '--', path).returncode == 0

def install(source, target, dry_run=False):
    if not target.is_dir():
        raise ValueError('Target must be an existing directory')
    agents = target / 'AGENTS.md'
    old = agents.read_text(encoding='utf-8') if agents.exists() else ''
    if (START in old) != (END in old):
        raise ValueError('Incomplete CODEX SWARM markers in AGENTS.md')
    if START not in old and agents.exists() and (target/'AGENTS.md.bak').exists():
        raise ValueError('AGENTS.md.bak already exists; refusing partial installation')
    repo = git_root(target)
    if repo and repo != target:
        raise ValueError('Run installer at Git repository root to ensure local ignore rules are correct')
    if repo and tracked(target, 'AGENTS.md') and START not in old:
        raise ValueError('AGENTS.md is already tracked: modifying it would be included in Git commits. Use a separate local clone or manually arrange a safe untracked instruction strategy.')
    if repo and tracked(target, 'AGENTS.md') and START in old:
        raise ValueError('AGENTS.md already tracked with SWARM instructions; cannot guarantee local-only. Untrack/reconcile it before continuing.')
    payload = source/'.codex'/'swarm'
    if not (payload/'ORCHESTRATOR.md').is_file():
        raise ValueError('Installer package missing .codex/swarm/ORCHESTRATOR.md')
    for src in sorted(payload.rglob('*')):
        if not src.is_file(): continue
        rel = src.relative_to(source)
        dst = target/rel
        if dst.exists():
            if dst.read_bytes() == src.read_bytes(): print('UNCHANGED', rel)
            else: print('SKIPPED (different; review manually)', rel)
        else:
            print('CREATE', rel)
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    if repo:
        exclude = target/'.git'/'info'/'exclude'
        if not exclude.parent.is_dir():
            # .git can be a file in a worktree; resolve its actual git directory.
            gd = git(target, 'rev-parse', '--absolute-git-dir')
            if gd.returncode != 0: raise ValueError('Unable to find Git directory')
            exclude = Path(gd.stdout.strip())/'info'/'exclude'
        excludes = EXCLUDES + (['/AGENTS.md'] if not tracked(target, 'AGENTS.md') else [])
        existing = exclude.read_text(encoding='utf-8') if exclude.exists() else ''
        missing = [line for line in excludes if line not in existing.splitlines()]
        if missing:
            print('LOCAL GIT EXCLUDE', ', '.join(missing))
            if not dry_run:
                exclude.parent.mkdir(parents=True, exist_ok=True)
                with exclude.open('a', encoding='utf-8') as f:
                    if existing and not existing.endswith('\n'): f.write('\n')
                    f.write('# CODEX SWARM local-only files\n'+'\n'.join(missing)+'\n')
    else:
        print('WARNING: target is not a Git repository; local Git excludes not installed.')
    if START not in old:
        print('APPEND AGENTS.md')
        if not dry_run:
            if agents.exists(): shutil.copy2(agents, target/'AGENTS.md.bak')
            agents.write_text(old.rstrip()+'\n'+BLOCK, encoding='utf-8')
    else:
        print('UNCHANGED AGENTS.md')
    if repo:
        legacy = ['scripts/swarm_project.py','scripts/swarm_knowledge.py','skills/swarm-project-intelligence/SKILL.md','skills/swarm-knowledge-engine/SKILL.md']
        existing_tracked = [p for p in legacy if tracked(target, p)]
        if existing_tracked:
            print('WARNING: legacy SWARM files already tracked; ignore rules do not untrack them:', ', '.join(existing_tracked))
    print('Installation complete. New SWARM files stay local in this Git checkout.')
    return 0

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', type=Path, required=True)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    try: return install(Path(__file__).resolve().parents[1], args.target.expanduser().resolve(), args.dry_run)
    except (ValueError, OSError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 2

if __name__ == '__main__': raise SystemExit(main())
