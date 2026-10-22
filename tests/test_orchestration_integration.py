import subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / 'scripts' / 'install.py'

class IntegrationTests(unittest.TestCase):
    def run_install(self, project, *flags):
        return subprocess.run(['python', str(INSTALL), '--target', str(project), *flags], capture_output=True, text=True)

    def test_fresh_install_includes_memory_and_policy(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); r=self.run_install(p)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue((p/'scripts/swarm_knowledge.py').is_file())
            self.assertTrue((p/'skills/swarm-knowledge-engine/SKILL.md').is_file())
            self.assertIn('Knowledge-first discovery',(p/'.codex/swarm/ORCHESTRATOR.md').read_text())

    def test_dry_run_no_writes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);r=self.run_install(p,'--dry-run');self.assertEqual(r.returncode,0)
            self.assertEqual(list(p.iterdir()),[])

    def test_backup_conflict_no_partial_install(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'AGENTS.md').write_text('Existing');(p/'AGENTS.md.bak').write_text('Backup')
            r=self.run_install(p);self.assertNotEqual(r.returncode,0)
            self.assertFalse((p/'.codex').exists())

    def test_incomplete_marker_no_partial_install(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'AGENTS.md').write_text('<!-- CODEX SWARM START -->')
            r=self.run_install(p);self.assertNotEqual(r.returncode,0)
            self.assertFalse((p/'.codex').exists())

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.assertEqual(self.run_install(p).returncode,0)
            self.assertEqual(self.run_install(p).returncode,0)
            self.assertEqual((p/'AGENTS.md').read_text().count('<!-- CODEX SWARM START -->'),1)

if __name__=='__main__': unittest.main()
