"""Offline smoke checks with a fake `gh`. No GitHub authentication or writes.
Run: python3 tests/test_smoke.py
"""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

FAKE_GH = '''#!/usr/bin/env python3
import json,os,sys
args=sys.argv[1:]
with open(os.environ['GH_MOCK_LOG'],'a') as f:f.write(json.dumps(args)+'\\n')
if args[:2]==['project','field-list']:
 print(json.dumps({'fields':[
  {'name':'Status','id':'PVTSSF_A','type':'ProjectV2SingleSelectField','options':[{'name':'In Progress','id':'optA'}, {'name':'Done','id':'optB'}]},
  {'name':'Points','id':'PVTF_B','type':'ProjectV2Field','dataType':'NUMBER'},
  {'name':'Iteration','id':'PVTIF_C','type':'ProjectV2IterationField','configuration':{'iterations':[{'title':'Sprint 1','id':'itrA'}]}}
 ]}))
elif args[:2]==['project','view']:
 print(json.dumps({'id':'PVT_X'}))
elif args[:2]==['project','item-list']:
 print(json.dumps({'items':[{'id':'PVTI_Z','content':{'url':'https://github.com/owner/repo/issues/3'}}]}))
elif args[:2]==['project','item-edit']:
 print(json.dumps({'ok':True}))
elif args[:2]==['repo','view']:
 print('owner/repo')
elif args[:2]==['issue','list']:
 if '--state' in args and args[args.index('--state')+1]=='open':
  print(json.dumps([{'number':3,'title':'Bug','url':'https://github.com/owner/repo/issues/3','assignees':[],'labels':[],'updatedAt':'2025-01-01T00:00:00Z'}]))
 else: print('[]')
elif args[:2]==['pr','list']:
 print('[]')
elif args[:1]==['api']:
 print(json.dumps([[{'title':'v1','open_issues':1,'closed_issues':2,'due_on':None}]]))
else:
 sys.exit('Unexpected gh command: '+repr(args))
'''

class Smoke(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = Path(self.tmp.name)
        gh = p / 'gh'
        gh.write_text(FAKE_GH)
        gh.chmod(0o755)
        self.log = p / 'gh_calls'
        self.env = {**os.environ, 'PATH':str(p)+os.pathsep+os.environ['PATH'], 'GH_MOCK_LOG': str(self.log)}

    def run_script(self, name, *args):
        return subprocess.run(['bash', str(ROOT/'scripts'/name), *args], env=self.env, text=True, capture_output=True)

    def calls(self):
        import json
        return [json.loads(x) for x in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_dry_run_is_read_only(self):
        r = self.run_script('project_set_field.sh','--owner','owner','--project','7','--repo','owner/repo','--issue','3','--field','Status','--value','In Progress','--dry-run')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('--single-select-option-id optA',r.stdout)
        self.assertFalse(any(c[:2]==['project','item-edit'] for c in self.calls()))

    def test_field_edit_executes_after_checks(self):
        r = self.run_script('project_set_field.sh','--owner','owner','--project','7','--repo','owner/repo','--issue','3','--field','Status','--value','Done')
        self.assertEqual(r.returncode,0,r.stderr)
        edits = [c for c in self.calls() if c[:2]==['project','item-edit']]
        self.assertEqual(len(edits),1)
        self.assertEqual(edits[0][-2:],['--single-select-option-id','optB'])

    def test_missing_option_makes_no_write(self):
        r = self.run_script('project_set_field.sh','--owner','owner','--project','7','--repo','owner/repo','--issue','3','--field','Status','--value','Invented')
        self.assertNotEqual(r.returncode,0)
        self.assertFalse(any(c[:2]==['project','item-edit'] for c in self.calls()))

    def test_iteration_resolves_by_title(self):
        r = self.run_script('project_set_field.sh','--owner','owner','--project','7','--repo','owner/repo','--issue','3','--field','Iteration','--value','Sprint 1','--dry-run')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('--iteration-id itrA',r.stdout)

    def test_report_is_read_only_and_contains_urls(self):
        r = self.run_script('status_report.sh','-R','owner/repo')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('# GitHub status: owner/repo',r.stdout)
        self.assertIn('https://github.com/owner/repo/issues/3',r.stdout)
        self.assertIn('GitHub-only snapshot',r.stdout)
        self.assertFalse(any(c[:2]==['project','item-edit'] for c in self.calls()))

if __name__ == '__main__':
    unittest.main(verbosity=2)
