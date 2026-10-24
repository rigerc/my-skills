import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_tape import lint
from inspect_render import inspect

class TapeLintTests(unittest.TestCase):
    def check(self, value):
        with tempfile.TemporaryDirectory() as d:
            tape=Path(d)/'test.tape'
            tape.write_text(value)
            return lint(tape)
    def test_good(self):
        self.assertFalse([i for i in self.check('Output demo.gif\nSet Width 800\nType "echo ok"\nEnter\n') if i['level']=='error'])
    def test_missing_output(self):
        self.assertTrue(any('No Output' in i['message'] for i in self.check('Type "hi"\n')))
    def test_conflicting_dimensions(self):
        self.assertTrue(any('conflicts' in i['message'] for i in self.check('Output x.gif\nSet Width 800\nSet Columns 80\n')))
    def test_misplaced_setting(self):
        self.assertTrue(any('ignored' in i['message'] for i in self.check('Output x.gif\nType "hi"\nSet Height 400\n')))
    def test_hidden(self):
        self.assertTrue(any('Hide' in i['message'] for i in self.check('Output x.gif\nHide\n')))
    def test_missing_artifact(self):
        self.assertFalse(inspect(Path('/this-path-should-not-exist/nonexistent.gif'))['ok'])

if __name__=='__main__': unittest.main()
