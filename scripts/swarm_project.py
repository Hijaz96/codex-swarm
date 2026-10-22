#!/usr/bin/env python3
"""CODEX SWARM project intelligence: bounded, offline, safe project discovery."""
import argparse
import hashlib
import json
import re
from pathlib import Path

VERSION = 1
MANIFESTS = ['composer.json','composer.lock','package.json','package-lock.json','pnpm-lock.yaml','yarn.lock','pyproject.toml','requirements.txt','go.mod','Cargo.toml','vite.config.js','vite.config.ts','tailwind.config.js','tailwind.config.ts','.env.example']
SAMPLE_DIRS = ['resources/views','resources/css','resources/js','app/Livewire','app/View/Components','src/components','src/pages']
SUFFIXES = {'.php','.blade.php','.html','.vue','.tsx','.jsx','.css','.js','.ts'}
MAX_FILES = 80
MAX_BYTES = 30000

def read_safe(path, root):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        return ''
    if not path.resolve().is_relative_to(root.resolve()):
        return ''
    return path.read_text(encoding='utf-8', errors='replace')

def sample_files(root):
    result=[]
    for d in SAMPLE_DIRS:
        folder=root/d
        if not folder.is_dir() or folder.is_symlink():
            continue
        for path in sorted(folder.rglob('*')):
            if len(result)>=MAX_FILES: return result
            if not path.is_file() or path.is_symlink() or any(p.startswith('.') for p in path.relative_to(root).parts):
                continue
            if not (path.name.endswith('.blade.php') or path.suffix in SUFFIXES): continue
            if path.stat().st_size>MAX_BYTES: continue
            result.append(path)
    return result

def dependencies(root):
    deps={}
    for name in ['composer.json','package.json']:
        raw=read_safe(root/name,root)
        if not raw: continue
        try: data=json.loads(raw)
        except json.JSONDecodeError: continue
        if not isinstance(data,dict): continue
        for section in ('require','require-dev','dependencies','devDependencies'):
            group=data.get(section,{})
            if isinstance(group,dict):
                for key,val in group.items():
                    if isinstance(val,str): deps[key.lower()]={'declared':val,'source':name,'section':section}
    return deps

def inspect(root):
    deps=dependencies(root)
    files=sample_files(root)
    texts={str(p.relative_to(root)):read_safe(p,root) for p in files}
    joined='\n'.join(texts.values())
    def evidence(pattern, max_results=4):
        return [name for name,content in texts.items() if re.search(pattern,content,re.I)][:max_results]
    def installed(*names): return [name for name in names if name in deps]
    tech={}
    def put(name,packages,usage=None):
        pkgs=installed(*packages)
        used=evidence(usage) if usage else []
        if pkgs or used:
            tech[name]={'status':'used' if used else 'declared_only','packages':pkgs,'evidence':used}
    put('laravel',['laravel/framework'],r'@extends\b|route\(|<x-[\w:-]+')
    put('livewire',['livewire/livewire'],r'wire:(?:click|model|submit|loading|navigate)\b|<livewire:')
    put('tailwind',['tailwindcss','@tailwindcss/vite'],r'@import\s+[\'\"]tailwindcss|@tailwind\s+(?:base|utilities)|class=[\'\"][^\'\"]*\b(?:flex|grid|rounded|px-\d)')
    put('flux',['livewire/flux','livewire/flux-pro'],r'<flux:[\w.-]+')
    put('alpine_direct',['alpinejs'],r'\bx-(?:data|on|show|model|bind|transition)\b|\bAlpine\.(?:data|store|start)\s*\(')
    put('react',['react'],r'from\s+[\'\"]react[\'\"]|useState\s*\(')
    put('vue',['vue'],r'<template>|defineComponent\s*\(')
    put('inertia',['inertiajs/inertia-laravel','@inertiajs/react','@inertiajs/vue3'],r'@inertia|createInertiaApp')
    if (root/'pyproject.toml').exists(): tech['python_project']={'status':'manifest_detected','packages':[],'evidence':['pyproject.toml']}
    if (root/'go.mod').exists(): tech['go_project']={'status':'manifest_detected','packages':[],'evidence':['go.mod']}
    if (root/'Cargo.toml').exists(): tech['rust_project']={'status':'manifest_detected','packages':[],'evidence':['Cargo.toml']}
    manifest_present=[n for n in MANIFESTS if (root/n).is_file() and not (root/n).is_symlink()]
    # Never read .env, .env.example, credentials, or arbitrary config values into the report.
    manifest_present=[n for n in manifest_present if n!='.env.example']
    fingerprint=hashlib.sha256()
    for p in [root/n for n in manifest_present]+files:
        rel=str(p.relative_to(root));fingerprint.update(rel.encode());fingerprint.update(hashlib.sha256(p.read_bytes()).digest())
    rules=[]
    if 'flux' in tech and tech['flux']['status']=='used':rules.append('Prefer existing Flux components and variants for new UI.')
    if 'livewire' in tech:rules.append('Follow existing Livewire component and action patterns.')
    if 'tailwind' in tech:rules.append('Reuse existing Tailwind spacing, typography, and design tokens.')
    if 'alpine_direct' not in tech:rules.append('No direct Alpine usage observed in bounded sample; do not assume Alpine is absent from runtime.')
    return {'schema_version':VERSION,'fingerprint':fingerprint.hexdigest(),'manifests':manifest_present,'sampled_files':len(files),'technologies':tech,'inferred_ui_rules':rules,'limitations':['Sample-based detection; absence of evidence is not evidence of absence.','Declared dependencies do not prove active use.','No .env or secret values were inspected.','Review representative layouts/components manually before UI changes.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target',type=Path,default=Path('.'))
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('scan');sub.add_parser('show');sub.add_parser('doctor')
    args=parser.parse_args();root=args.target.expanduser().resolve()
    if not root.is_dir():parser.error('target must be a directory')
    cache=root/'.swarm'/'project-profile.json'
    if args.command=='scan':
        profile=inspect(root)
        # User overrides live in separate, developer-maintained file and are never rewritten.
        override=root/'.swarm'/'project-preferences.json'
        if override.is_file() and not override.is_symlink() and override.stat().st_size<10000:
            try:
                prefs=json.loads(override.read_text(encoding='utf-8'))
                if isinstance(prefs,dict):profile['user_preferences']=prefs
            except (ValueError,OSError):pass
        cache.parent.mkdir(parents=True,exist_ok=True)
        cache.write_text(json.dumps(profile,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(profile,indent=2,ensure_ascii=False))
    elif args.command=='show':
        if not cache.is_file():parser.error('no profile; run scan first')
        print(cache.read_text(encoding='utf-8'))
    else:
        print(json.dumps({'script':'available','profile_exists':cache.is_file(),'target':str(root),'scan_mode':'offline, bounded, no .env read'},indent=2))
if __name__=='__main__':main()
