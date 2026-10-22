import importlib.util
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('swarm_knowledge',Path(__file__).resolve().parents[1]/'scripts'/'swarm_knowledge.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestKnowledge(unittest.TestCase):
    def test_memory_recall(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);m.add(root,'Laravel customer query','failed','Eager loading increased memory','test')
            self.assertIn('Eager loading',m.retrieve(root,'customer query',200,5))
    def test_wiki(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'docs'/'knowledge').mkdir(parents=True)
            (root/'docs'/'knowledge'/'architecture.md').write_text('# Architecture\nLaravel queues process notifications')
            self.assertIn('Laravel queues',m.retrieve(root,'queues architecture',200,5))
    def test_budget(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);m.add(root,'customer','decision','X'*5000,'test')
            self.assertLessEqual(len(m.retrieve(root,'customer',10,5)),40)
    def test_redaction(self):
        self.assertNotIn('supersecret',m.scrub('api_key=supersecret'))
    def test_no_match(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn('No relevant',m.retrieve(Path(d),'unmatched',100,5))
if __name__=='__main__':unittest.main()
