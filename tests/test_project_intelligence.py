import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('swarm_project',ROOT/'scripts/swarm_project.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class ProjectIntelligenceTests(unittest.TestCase):
    def test_flux_livewire_without_direct_alpine(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'composer.json').write_text(json.dumps({'require':{'laravel/framework':'^12','livewire/livewire':'^3','livewire/flux-pro':'^2'}}))
            f=p/'resources/views';f.mkdir(parents=True)
            (f/'dashboard.blade.php').write_text('<flux:button wire:click="save">Save</flux:button>')
            data=mod.inspect(p)
            self.assertEqual(data['technologies']['flux']['status'],'used')
            self.assertEqual(data['technologies']['livewire']['status'],'used')
            self.assertNotIn('alpine_direct',data['technologies'])
    def test_declared_not_assumed_used(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'package.json').write_text('{"dependencies":{"alpinejs":"^3"}}')
            self.assertEqual(mod.inspect(p)['technologies']['alpine_direct']['status'],'declared_only')
    def test_never_reads_env(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.env').write_text('DB_PASSWORD=supersecret')
            self.assertNotIn('supersecret',json.dumps(mod.inspect(p)))
    def test_symlink_not_read(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);outside=p/'private.txt';outside.write_text('password=secret')
            (p/'composer.json').symlink_to(outside)
            self.assertEqual(mod.inspect(p)['manifests'],[])
    def test_stable_fingerprint(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'package.json').write_text('{"dependencies":{"react":"18"}}')
            a=mod.inspect(p)['fingerprint'];b=mod.inspect(p)['fingerprint']
            self.assertEqual(a,b)
            (p/'package.json').write_text('{"dependencies":{"react":"19"}}')
            self.assertNotEqual(a,mod.inspect(p)['fingerprint'])

if __name__=='__main__':unittest.main()
