"""统一检查和构建入口，Python 3.10+，无需第三方依赖。"""
import argparse
import json
from collections import Counter
import build_extended_dictionary as extended
import build_simple_dictionary as simple


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='仅校验，不写文件')
    args = parser.parse_args()
    entries, files = extended.load_entries()
    counts = extended.validate_entries(entries)
    detailed = [extended.source_line(e) for e in entries]
    compact = [simple.render_line(e) for e in entries]
    simple.verify(compact)
    assert [s.split('@', 1)[0] for s in detailed] == [s.split('@', 1)[0] for s in compact]
    print(f'两版校验通过：{len(entries)} 条，{len(files)} 个数据文件')
    if args.check:
        return
    out = extended.LOCAL_OUTPUT
    out.mkdir(exist_ok=True)
    extended.OUTPUT.write_text('\n'.join(detailed) + '\n', encoding='utf-8')
    simple.OUTPUT.write_text('\n'.join(compact) + '\n', encoding='utf-8')
    extended.build_preview([(e['word'], extended.render_entry(e)) for e in entries])
    (out / 'statistics.json').write_text(json.dumps({'total': len(entries), 'domains': dict(counts)}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已生成两版 TXT、HTML 和动态统计：{out}')
    print('文件名来自 dictionary_config.json；新增数据需重新用欧路构建器打包为 .eudic。')


if __name__ == '__main__':
    main()
