"""Tests for independently bounded management-context hook outputs.

Run in the Nexus template root:
    python3 -m unittest discover -s tests -p 'test_nexus_management_context.py' -v
No Claude service or API calls are required.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TEMPLATE = Path(__file__).resolve().parents[1]
MAIN = '.claude/hooks/nexus-prompt-gate.py'
ALGORITHM_HANDLER = '.claude/hooks/nexus-management-algorithm.py'
LAUNCHERS = {'core': '.claude/hooks/nexus-algorithm-core.py',
             'reading': '.claude/hooks/nexus-algorithm-reading.py'}
HELPER = '.claude/hooks/_nexus_common.py'
ALGO = 'knowledge/specs/spec--system--management-algorithm.md'
SETTINGS = '.claude/settings.json'
LIMIT = 10000


class ManagementHookTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in (MAIN, ALGORITHM_HANDLER, *LAUNCHERS.values(), HELPER, ALGO, SETTINGS):
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(TEMPLATE / rel, dest)
        self.charter = self.root / 'process/charter.md'
        self.charter.parent.mkdir(parents=True, exist_ok=True)
        self.charter.write_text('---\nstatus: approved\n---\n# Test charter\n', encoding='utf-8')
        self.navigation = self.root / 'process/navigation.md'
        self.write_navigation('5.4 of T1 — assess results', '5.3 of T1 — work finished')
        self.state = self.root / '.nexus/state.json'
        self.state.parent.mkdir(parents=True, exist_ok=True)
        self.write_state()

    def write_navigation(self, step, came_from):
        self.navigation.write_text(
            '---\ntype: navigation\n---\n# Navigation\n\n## Now\n\n'
            'Position: test\nHeading: test; contract process/iteration--test.md\n'
            'Why here: test\nIgnoring: later work\n'
            f'Step: {step}\nCame from: {came_from}\n\n## Net\n...\n',
            encoding='utf-8',
        )

    def write_state(self, completed=True):
        state = {
            'session_id': 'unit-test',
            'bootstrap': {'status': 'completed' if completed else 'pending',
                          'read_ledger': [], 'required_files': [], 'invariant_read_count': 1},
            'turn': {'index': 0, 'decision_gate_seen': False},
        }
        self.state.write_text(json.dumps(state), encoding='utf-8')

    def invoke(self, name, part=None):
        # The algorithm parts are invoked as registered: through their launchers.
        command = ['python3', str(self.root / (MAIN if name == 'main' else LAUNCHERS[part]))]
        result = subprocess.run(
            command,
            input=json.dumps({'session_id': 'unit-test', 'hook_event_name': 'UserPromptSubmit'}),
            capture_output=True, text=True,
            env=dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root)),
            check=True,
        )
        data = json.loads(result.stdout)
        ctx = data['hookSpecificOutput']['additionalContext']
        self.assertEqual(data['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')
        self.assertLessEqual(len(ctx), LIMIT, f'{name}/{part} exceeds hook output limit')
        return ctx

    def all_parts(self):
        return (self.invoke('main'), self.invoke('algorithm', 'core'),
                self.invoke('algorithm', 'reading'))

    def test_registered_as_three_independent_hook_commands(self):
        cfg = json.loads((self.root / SETTINGS).read_text())
        cmds = [h['command'] for g in cfg['hooks']['UserPromptSubmit'] for h in g['hooks']]
        self.assertEqual(len(cmds), 3)
        self.assertEqual(len(set(cmds)), 3)
        self.assertEqual(sum('nexus-prompt-gate.py' in c for c in cmds), 1)
        for launcher in LAUNCHERS.values():
            self.assertEqual(sum(c.endswith('/' + launcher) for c in cmds), 1)

    def test_updater_recognises_every_registration_as_a_unit(self):
        # A hook entry reaches a host only as a `<event>/<nexus-*.py>` unit
        # (spec--system--nexus-update.md §2.2); an entry the updater cannot
        # key is foreign to it and is never delivered.
        import importlib.util
        spec = importlib.util.spec_from_file_location('nexus_update', TEMPLATE / 'tools/nexus-update.py')
        updater = importlib.util.module_from_spec(spec)
        sys.modules['nexus_update'] = updater
        spec.loader.exec_module(updater)
        units = updater.units_hooks_merge((self.root / SETTINGS).read_bytes())
        self.assertEqual(
            sorted(k for k in units if k.startswith('UserPromptSubmit/')),
            ['UserPromptSubmit/nexus-algorithm-core.py',
             'UserPromptSubmit/nexus-algorithm-reading.py',
             'UserPromptSubmit/nexus-prompt-gate.py'],
        )

    def test_direct_part_argument_still_works(self):
        result = subprocess.run(
            ['python3', str(self.root / ALGORITHM_HANDLER), '--part', 'core'],
            input='{}', capture_output=True, text=True,
            env=dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root)), check=True,
        )
        self.assertIn('PART 1/2', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])

    def test_algorithm_and_counter_delivered_without_truncation(self):
        before = self.navigation.read_bytes()
        main, core, reading = self.all_parts()
        self.assertIn('Program Counter (node): 5.4', main)
        self.assertIn('Current Objective: T1', main)
        self.assertIn('Last transition (verbatim): 5.3 of T1', main)
        self.assertIn('NEXUS TURN CONTRACT', main)
        self.assertIn('PART 1/2', core)
        self.assertIn('## 1. Definitions', core)
        self.assertIn('## 2. The algorithm', core)
        self.assertIn('PART 2/2', reading)
        self.assertIn('## 3. Reading the algorithm', reading)
        self.assertNotIn('## 4. What this specification does not define', main+core+reading)
        self.assertEqual(before, self.navigation.read_bytes())

    def test_algorithm_sections_identical_to_canonical_file(self):
        source = (self.root / ALGO).read_text()
        a = source.index('## 1. Definitions')
        b = source.index('## 3. Reading the algorithm')
        c = source.index('## 4. What this specification does not define')
        core = self.invoke('algorithm', 'core')
        reading = self.invoke('algorithm', 'reading')
        self.assertIn(source[a:b].rstrip(), core)
        self.assertIn(source[b:c].rstrip(), reading)

    def test_second_and_third_hook_do_not_update_turn_index(self):
        self.invoke('algorithm', 'reading')
        self.invoke('algorithm', 'core')
        self.assertEqual(json.loads(self.state.read_text())['turn']['index'], 0)
        self.invoke('main')
        self.assertEqual(json.loads(self.state.read_text())['turn']['index'], 1)

    def test_new_position_is_loaded_next_prompt(self):
        self.invoke('main')
        self.write_navigation('7 — review Project Goal', '6b of T1 — objective unjustified')
        content = self.invoke('main')
        self.assertIn('Program Counter (node): 7', content)
        self.assertIn('Current Objective: none named', content)
        self.assertIn('6b of T1', content)

    def test_bootstrap_pending_keeps_management_position_and_reading(self):
        self.write_state(completed=False)
        main, core, reading = self.all_parts()
        self.assertIn('BOOTSTRAP STILL PENDING', main)
        self.assertIn('Program Counter (node): 5.4', main)
        self.assertIn('## 2. The algorithm', core)
        self.assertIn('## 3. Reading the algorithm', reading)

    def test_missing_navigation_is_not_guessed(self):
        self.navigation.unlink()
        self.assertIn('PROGRAM COUNTER UNAVAILABLE', self.invoke('main'))
        self.write_navigation('unknown now', 'unknown earlier')
        self.assertIn('PROGRAM COUNTER FORMAT UNCLEAR', self.invoke('main'))

    def test_missing_algorithm_reports_both_parts(self):
        (self.root / ALGO).unlink()
        self.assertIn('ALGORITHM UNAVAILABLE', self.invoke('algorithm', 'core'))
        self.assertIn('ALGORITHM UNAVAILABLE', self.invoke('algorithm', 'reading'))

    def test_no_charter_does_not_invent_objective(self):
        self.charter.unlink()
        self.assertIn('second layer is not yet active', self.invoke('main'))
        self.assertIn('## 2. The algorithm', self.invoke('algorithm', 'core'))

    def test_unapproved_charter_is_reported(self):
        self.charter.write_text('---\nstatus: review\n---\n')
        self.assertIn('Project Goal is not recorded as agreed', self.invoke('main'))

    def test_oversize_core_is_explicit_error_not_silent_truncation(self):
        path = self.root / ALGO
        contents = path.read_text()
        contents = contents.replace('## 2. The algorithm',
                                    '## 2. The algorithm\n' + 'large-diagram-line ' * 600)
        path.write_text(contents)
        core = self.invoke('algorithm', 'core')
        self.assertIn('ALGORITHM PART TOO LARGE', core)
        self.assertNotIn('large-diagram-line', core)
        self.assertIn('## 3. Reading the algorithm', self.invoke('algorithm', 'reading'))

    def test_missing_section_is_explicit_format_error(self):
        path = self.root / ALGO
        path.write_text(path.read_text().replace('## 3. Reading the algorithm', '## 3. Changed'))
        self.assertIn('ALGORITHM FORMAT ERROR', self.invoke('algorithm', 'core'))


if __name__ == '__main__':
    unittest.main()
