#!/usr/bin/env python3
"""Offline, bounded project stack and UI discovery (Python 3.9+)."""
import argparse
import hashlib
import json
import re
from pathlib import Path

MANIFESTS = ('composer.json','composer.lock','package.json','package-lock.json','pnpm-lock.yaml','yarn.lock','pyproject.toml','requirements.txt','go.mod','Cargo.toml','vite.config.js','vite.config.ts','tailwind.config.js','tailwind.config.ts')
SAMPLE_DIRS = ('resources/views','resources/css','resources/js','app/Livewire','app/View/Components','src/components','src/pages')
SUFFIXES = ('.php','.html','.vue','.tsx','.jsx','.css','.js','.ts')

def safe_read(path, root):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 30000 or not path.resolve().is_relative_to(root.resolve()): return ''
    return path.read_text(encoding='utf-8', errors='replace')

def inspect(root):
    deps={}
    for name in ('composer.json','package.json'):
        try: obj=json.loads(safe_read(root/name,root))
        except (ValueError, OSError): continue
        if not isinstance(obj,dict): continue
        for section in ('require','require-dev','dependencies','devDependencies'):
            group=obj.get(section,{})
            if isinstance(group,dict):
                for k,v in group.items():
                    if isinstance(v,str): deps[k.lower()]={'declared':v,'source':name,'section':section}
    files=[]
    for d in SAMPLE_DIRS:
        folder=root/d
        if folder.is_symlink() or not folder.is_dir(): continue
        for p in sorted(folder.rglob('*')):
            if len(files)>=80: break
            if p.is_symlink() or not p.is_file() or not p.name.endswith(SUFFIXES): continue
            if any(x.startswith('.') for x in p.relative_to(root).parts): continue
            if p.stat().st_size<=30000: files.append(p)
    texts={str(p.relative_to(root)):safe_read(p,root) for p in files}
    def put(pkgs,pattern):
        declared=[x for x in pkgs if x in deps]
        used=[n for n,v in texts.items() if re.search(pattern,v,re.I)][:5]
        return {'status':'observed_usage' if used else 'declared_only','packages':declared,'evidence':used} if declared or used else None
    checks={
      'laravel': (['laravel/framework'],r'@extends\b|Route::|<x-[\w:-]+'),
      'livewire': (['livewire/livewire'],r'wire:(?:click|model|submit|loading|navigate)\b|<livewire:'),
      'tailwind': (['tailwindcss','@tailwindcss/vite'],r'@import\s+[\'\"]tailwindcss|@tailwind\s+(?:base|utilities)|class=[\'\"][^\'\"]*\b(?:flex|grid|rounded|px-\d)'),
      'flux': (['livewire/flux','livewire/flux-pro'],r'<flux:[\w.-]+'),
      'alpine_direct': (['alpinejs'],r'\bx-(?:data|on|show|model|bind|transition)\b|\bAlpine\.(?:data|store|start)\s*\('),
      'react': (['react'],r'from\s+[\'\"]react[\'\"]|useState\s*\('),
      'vue': (['vue'],r'<template>|defineComponent\s*\('),
      'inertia': (['inertiajs/inertia-laravel','@inertiajs/react','@inertiajs/vue3'],r'@inertia|createInertiaApp'),
    }
    tech={k:v for k,(pkgs,pattern) in checks.items() if (v:=put(pkgs,pattern))}
    for f,k in [('pyproject.toml','python_project'),('go.mod','go_project'),('Cargo.toml','rust_project')]:
        if (root/f).is_file():tech[k]={'status':'manifest_detected','packages':[],'evidence':[f]}
    manifests=[n for n in MANIFESTS if (root/n).is_file() and not (root/n).is_symlink()]
    fingerprint=hashlib.sha256()
    for p in [root/n for n in manifests]+files:
        fingerprint.update(str(p.relative_to(root)).encode());fingerprint.update(hashlib.sha256(p.read_bytes()).digest())
    rules=[]
    if tech.get('flux',{}).get('status')=='observed_usage':rules.append('Prefer existing Flux components and variants.')
    if 'livewire' in tech:rules.append('Follow existing Livewire component patterns.')
    if 'tailwind' in tech:rules.append('Reuse Tailwind tokens and existing layout conventions.')
    if 'alpine_direct' not in tech:rules.append('No direct Alpine observed in bounded sample; internal Alpine may still exist.')
    return {'schema_version':2,'fingerprint':fingerprint.hexdigest(),'manifests':manifests,'sampled_files':len(files),'technologies':tech,'inferred_ui_rules':rules,'limitations':['Bounded sampling; absence of evidence does not prove absence.','Declared packages may not be used.','No .env or secret values inspected.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,default=Path('.'))
    s=p.add_subparsers(dest='command',required=True)
    for name in ('scan','show','doctor'):s.add_parser(name)
    a=p.parse_args();root=a.target.expanduser().resolve()
    if not root.is_dir():p.error('target directory missing')
    data=root/'.codex'/'swarm'/'data';cache=data/'project-profile.json'
    if a.command=='scan':
        profile=inspect(root);override=data/'project-preferences.json'
        if override.is_file() and not override.is_symlink() and override.stat().st_size<10000:
            try:
                prefs=json.loads(override.read_text(encoding='utf-8'))
                if isinstance(prefs,dict):profile['user_preferences']=prefs
            except (ValueError,OSError):pass
        data.mkdir(parents=True,exist_ok=True);cache.write_text(json.dumps(profile,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps(profile,indent=2,ensure_ascii=False))
    elif a.command=='show':
        if not cache.is_file():p.error('profile missing; run scan first')
        print(cache.read_text(encoding='utf-8'))
    else:print(json.dumps({'profile_exists':cache.is_file(),'offline':True,'secrets_scanned':False},indent=2))
if __name__=='__main__':main()
