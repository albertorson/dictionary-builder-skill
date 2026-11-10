"""Create a standalone dictionary project from the bundled template."""
import argparse
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--name', required=True)
    parser.add_argument('--slug', required=True)
    parser.add_argument('--domain', required=True)
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    template = Path(__file__).resolve().parents[1] / 'assets' / 'template'
    # copytree refuses an existing target, so it cannot overwrite someone's project.
    shutil.copytree(template, args.output)
    config = dict(name=args.name, slug=args.slug, version='0.1', base_source=None,
                  additions_dir='data/entries', community_dir='data/community',
                  domains={args.domain: args.label})
    (args.output / 'dictionary_config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.output / 'data/entries').mkdir(parents=True)
    (args.output / 'data/community').mkdir(parents=True)
    print(f'Created {args.output.resolve()}; add JSONL entries, then run python build.py')


if __name__ == '__main__':
    main()
