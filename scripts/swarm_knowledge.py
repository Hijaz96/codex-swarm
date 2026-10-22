#!/usr/bin/env python3
"""Local, opt-in project memory + wiki retrieval + context budget. Python 3.9+ stdlib."""
import argparse
import datetime as dt
import json
import re
import sqlite3
from pathlib import Path

DB = '.swarm/knowledge.sqlite3'
IGNORE = {'password','secret','token','api_key','private_key'}

def db(root):
    path = root / DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, topic TEXT NOT NULL, status TEXT NOT NULL, summary TEXT NOT NULL, source TEXT NOT NULL, created TEXT NOT NULL)')
    return conn

def words(text):
    return set(re.findall(r'[a-z0-9_]{3,}', text.lower()))

def scrub(text):
    text = re.sub(r'(?i)(password|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*\S+', r'\1=[REDACTED]', text)
    text = re.sub(r'\bgh[pousr]_[A-Za-z0-9_]{12,}\b', '[REDACTED]', text)
    text = re.sub(r'\bsk-[A-Za-z0-9_-]{12,}\b', '[REDACTED]', text)
    return text

def add(root, topic, status, summary, source):
    if not summary.strip() or not topic.strip():
        raise ValueError('topic and summary required')
    with db(root) as conn:
        conn.execute('INSERT INTO memories(topic,status,summary,source,created) VALUES(?,?,?,?,?)',
                     (scrub(topic),status,scrub(summary),scrub(source),dt.datetime.now(dt.timezone.utc).isoformat()))

def wiki_files(root):
    folder = root / 'docs' / 'knowledge'
    if not folder.exists(): return []
    return sorted(p for p in folder.rglob('*.md') if p.is_file() and len(p.relative_to(folder).parts) <= 4)

def retrieve(root, query, budget, limit):
    q = words(query)
    matches = []
    with db(root) as conn:
        for ident, topic, status, summary, source, created in conn.execute('SELECT id,topic,status,summary,source,created FROM memories ORDER BY id DESC LIMIT 2000'):
            text = f'{topic} {summary}'
            score = len(q & words(text))
            if score:
                matches.append((score, f'[memory:{ident}] [{status}] {topic}\n{summary}\nSource: {source}\n'))
    for p in wiki_files(root):
        # Keep docs bounded, and never ingest hidden files or arbitrary source trees.
        if p.stat().st_size > 200_000: continue
        content = p.read_text(encoding='utf-8', errors='replace')
        for index, section in enumerate(re.split(r'(?=^#{1,3} )',content, flags=re.M)):
            if not section.strip(): continue
            score = len(q & words(section))
            if score:
                matches.append((score, f'[wiki:{p.relative_to(root)}:{index}]\n{scrub(section[:3500])}\n'))
    matches.sort(key=lambda item: (-item[0], len(item[1])))
    # Approximation only, not model-tokenizer accurate.
    chars = max(0, budget) * 4
    output=[]
    for _, item in matches:
        if len(output) >= limit or chars <= 0: break
        snippet=item[:chars]
        output.append(snippet)
        chars -= len(snippet)
    return '\n---\n'.join(output) if output else 'No relevant saved knowledge. Inspect current source code.'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target',type=Path,default=Path('.'))
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('remember');a.add_argument('--topic',required=True);a.add_argument('--summary',required=True);a.add_argument('--status',choices=['success','failed','decision','finding'],required=True);a.add_argument('--source',default='manual')
    s=sub.add_parser('recall');s.add_argument('query');s.add_argument('--budget',type=int,default=800);s.add_argument('--limit',type=int,default=5)
    sub.add_parser('doctor')
    args=p.parse_args();root=args.target.expanduser().resolve()
    if not root.is_dir(): p.error('target must exist')
    if args.cmd=='remember':add(root,args.topic,args.status,args.summary,args.source);print('Saved project-local memory.')
    elif args.cmd=='recall':print(retrieve(root,args.query,args.budget,args.limit))
    else:
        with db(root) as conn: count=conn.execute('SELECT COUNT(*) FROM memories').fetchone()[0]
        print(json.dumps({'project':str(root),'memory_count':count,'wiki_pages':len(wiki_files(root)),'budget':'approximate 4 chars/token','capture':'manual opt-in','providers':'local only'},indent=2))

if __name__=='__main__':main()
