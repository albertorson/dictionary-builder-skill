import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/dictionary-builder'


class InitializeTests(unittest.TestCase):
    def test_two_domains_build_independently(self):
        for slug, domain, label in [('Finance', 'Finance', '金融'), ('Electrical', 'Electrical Engineering', '电气工程')]:
            with self.subTest(domain=domain), tempfile.TemporaryDirectory() as temp:
                project = Path(temp) / slug
                subprocess.run([sys.executable, str(SKILL / 'scripts/init_dictionary.py'), '--output', str(project), '--name', label + '词典', '--slug', slug, '--domain', domain, '--label', label], check=True, capture_output=True)
                item = json.loads((project / 'examples/entry.jsonl').read_text(encoding='utf-8'))
                item['domain'] = domain
                # A format fixture, not a claimed expert-reviewed dictionary entry.
                (project / 'data/entries/sample.jsonl').write_text(json.dumps(item, ensure_ascii=False) + '\n', encoding='utf-8')
                subprocess.run([sys.executable, '-X', 'utf8', 'build.py'], cwd=project, check=True, capture_output=True)
                output = project / 'local_output'
                self.assertTrue((output / f'{slug}_Simple_v0.1_EudicBuilder.txt').exists())
                preview = (output / f'{slug}_Extended_v0.1_preview.html').read_text(encoding='utf-8')
                self.assertIn(label + '词典', preview)
                self.assertEqual(json.loads((output / 'statistics.json').read_text(encoding='utf-8'))['total'], 1)


if __name__ == '__main__':
    unittest.main()
