"""Offline integrity tests for role selection and orchestration skill docs.

These do not contact T3, model providers or GitHub.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RoleOrchestrationDocs(unittest.TestCase):
    def text(self, relpath):
        return (ROOT / relpath).read_text(encoding='utf-8')

    def test_role_model_selection_is_hard_gate(self):
        skill = self.text('SKILL.md')
        ref = self.text('references/role-orchestration.md')
        for term in ('orchestrator_capabilities', 'delegate_task', 'provider', 'model'):
            self.assertIn(term, skill)
            self.assertIn(term, ref)
        self.assertIn('ask the user', skill.lower())
        self.assertIn('No delegation while a required mapping is missing or invalid.', skill)
        self.assertIn('Do not call `delegate_task` until the user has chosen', ref)
        self.assertIn('one provider + model for all roles', ref)
        self.assertIn('per-role mapping', ref)
        self.assertIn('inherit parent', ref)
        self.assertIn('Do **not** treat an omitted model/role as implicit consent', ref)

    def test_all_supported_roles_and_handoffs(self):
        ref = self.text('references/role-orchestration.md')
        worksheet = self.text('assets/role-assignment.md')
        brief = self.text('assets/delegation-brief.md')
        for role in ('research', 'design', 'implementation', 'test', 'review', 'general'):
            self.assertIn(f'`{role}`', ref)
            self.assertIn(f'`{role}`', worksheet)
        self.assertIn('Parent coordinator', ref)
        self.assertIn('candidate commit/PR', ref)
        self.assertIn('implementation', brief)
        self.assertIn('Selected provider instance', brief)
        self.assertIn('Selected model', brief)
        self.assertIn('Role handoff', brief)

    def test_explicit_targets_and_evidence_tracking(self):
        skill = self.text('SKILL.md')
        ref = self.text('references/role-orchestration.md')
        t3 = self.text('references/t3-delegation.md')
        self.assertIn('"providerInstanceId"', skill)
        self.assertIn('"providerInstanceId"', ref)
        self.assertIn('"model"', ref)
        self.assertIn('explicitly chose inherit parent', ref)
        self.assertIn('Actual provider + model', ref)
        self.assertIn('selected role/model mapping', t3)
        self.assertIn('actual', t3)

    def test_local_reference_links_resolve(self):
        for relpath in ('README.md', 'SKILL.md', 'references/t3-delegation.md', 'references/role-orchestration.md'):
            page = ROOT / relpath
            for href in re.findall(r'\]\(([^)]+)\)', page.read_text()):
                if href.startswith(('https:', 'http:', 't3-thread:', '#')):
                    continue
                local = (page.parent / href.split('#', 1)[0]).resolve()
                self.assertTrue(local.is_file(), f'{relpath} has broken link: {href}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
