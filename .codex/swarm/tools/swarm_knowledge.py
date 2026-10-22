#!/usr/bin/env python3
"""Local-only, manual opt-in knowledge storage and retrieval."""
import argparse
import datetime as dt
import json
import re
import sqlite3
from pathlib import Path

def scrub(text):
    text=re.sub(r'(?i)(password|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*\S+',r'\1=[REDACTED]',text)
    text=re.sub(r'\bgh[pousr]_[A-Za-z0-9_]{12,}\b','[REDACTED]',text)
    return re.sub(r'\bsk-[A-Za-z0-9_-]{12,}\b','[REDACTED]',text)

def connect(root):
    path=root/'.codex'/'swarm'/'data'/'knowledge.sqlite3';path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path)
    conn.execute('CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, topic TEXT NOT NULL, status TEXT NOT NULL, summary TEXT NOT NULL, source TEXT NOT NULL, created TEXT NOT NULL)')
    return conn

def words(text):return set(re.findall(r'[a-z0-9_]{3,}',text.lower()))

def recall(root,query,budget,limit):
    q=words(query);matches=[]
    with connect(root) as conn:
        for ident,topic,status,summary,source in conn.execute('SELECT id,topic,status,summary,source FROM memories ORDER BY id DESC LIMIT 2000'):
            score=len(q & words(topic+' '+summary))
            if score:matches.append((score,f'[memory:{ident}] [{status}] {topic}\n{summary}\nSource: {source}\n'))
    wiki=root/'docs'/'knowledge'
    if wiki.is_dir() and not wiki.is_symlink():
        for p in sorted(wiki.rglob('*.md')):
            if p.is_symlink() or not p.is_file() or len(p.relative_to(wiki).parts)>4 or p.stat().st_size>200000:continue
            content=p.read_text(encoding='utf-8',errors='replace')
            for idx,section in enumerate(re.split(r'(?=^#{1,3} )',content,flags=re.M)):
                score=len(q & words(section))
                if score:matches.append((score,f'[wiki:{p.relative_to(root)}:{idx}]\n{scrub(section[:3500])}\n'))
    matches.sort(key=lambda item:(-item[0],len(item[1])))
    chars=max(0,budget)*4;out=[]
    for _,item in matches:
        if len(out)>=limit or chars<=0:break
        out.append(item[:chars]);chars-=len(out[-1])
    return '\n---\n'.join(out) if out else 'No relevant saved knowledge. Inspect current source code.'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--target',type=Path,default=Path('.'))
    s=p.add_subparsers(dest='cmd',required=True)
    a=s.add_parser('remember');a.add_argument('--topic',required=True);a.add_argument('--summary',required=True);a.add_argument('--status',choices=['success','failed','decision','finding'],required=True);a.add_argument('--source',default='manual')
    a=s.add_parser('recall');a.add_argument('query');a.add_argument('--budget',type=int,default=800);a.add_argument('--limit',type=int,default=5)
    s.add_parser('doctor');a=p.parse_args();root=a.target.expanduser().resolve()
    if not root.is_dir():p.error('target must exist')
    if a.cmd=='remember':
        with connect(root) as conn:conn.execute('INSERT INTO memories(topic,status,summary,source,created) VALUES(?,?,?,?,?)',(scrub(a.topic),a.status,scrub(a.summary),scrub(a.source),dt.datetime.now(dt.timezone.utc).isoformat()))
        print('Saved project-local memory.')
    elif a.cmd=='recall':print(recall(root,a.query,a.budget,a.limit))
    else:
        with connect(root) as conn:count=conn.execute('SELECT COUNT(*) FROM memories').fetchone()[0]
        print(json.dumps({'memory_count':count,'manual_opt_in':True,'local_only':True},indent=2))
if __name__=='__main__':main()
