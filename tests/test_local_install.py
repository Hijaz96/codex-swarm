import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INSTALL=ROOT/'scripts'/'install.py'
SCAN=ROOT/'.codex'/'swarm'/'tools'/'swarm_project.py'
MEM=ROOT/'.codex'/'swarm'/'tools'/'swarm_knowledge.py'

def run(*args):return subprocess.run(['python',*map(str,args)],capture_output=True,text=True)

class LocalInstallTests(unittest.TestCase):
    def test_git_local_only_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q',str(p)],check=True)
            self.assertEqual(run(INSTALL,'--target',p).returncode,0)
            self.assertEqual(run(INSTALL,'--target',p).returncode,0)
            self.assertTrue((p/'.codex/swarm/tools/swarm_project.py').exists())
            self.assertEqual((p/'AGENTS.md').read_text().count('<!-- CODEX SWARM START -->'),1)
            r=subprocess.run(['git','-C',str(p),'status','--porcelain','--untracked-files=all'],capture_output=True,text=True)
            self.assertEqual(r.stdout.strip(),'')
            self.assertIn('/.codex/swarm/',(p/'.git/info/exclude').read_text())
    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q',str(p)],check=True)
            before=(p/'.git/info/exclude').read_text()
            self.assertEqual(run(INSTALL,'--target',p,'--dry-run').returncode,0)
            self.assertFalse((p/'AGENTS.md').exists())
            self.assertEqual((p/'.git/info/exclude').read_text(),before)
    def test_tracked_agents_rejected_without_partial_install(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);subprocess.run(['git','init','-q',str(p)],check=True)
            (p/'AGENTS.md').write_text('Existing instructions')
            subprocess.run(['git','-C',str(p),'add','AGENTS.md'],check=True)
            r=run(INSTALL,'--target',p)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse((p/'.codex').exists())
    def test_scan_flux_without_direct_alpine(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'resources/views').mkdir(parents=True)
            (p/'composer.json').write_text(json.dumps({'require':{'laravel/framework':'^12','livewire/livewire':'^3','livewire/flux-pro':'^2'}}))
            (p/'resources/views/index.blade.php').write_text('<flux:button wire:click="save">Save</flux:button>')
            r=run(SCAN,'--target',p,'scan');self.assertEqual(r.returncode,0,r.stderr)
            profile=json.loads(r.stdout)
            self.assertEqual(profile['technologies']['flux']['status'],'observed_usage')
            self.assertNotIn('alpine_direct',profile['technologies'])
            self.assertTrue((p/'.codex/swarm/data/project-profile.json').exists())
    def test_memory_local_path(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);r=run(MEM,'--target',p,'remember','--topic','interface','--status','decision','--summary','Use Flux Pro')
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue((p/'.codex/swarm/data/knowledge.sqlite3').exists())
            self.assertIn('Use Flux Pro',run(MEM,'--target',p,'recall','interface').stdout)

if __name__=='__main__':unittest.main()
