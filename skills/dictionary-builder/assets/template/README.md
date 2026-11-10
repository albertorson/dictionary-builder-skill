# 自定义专业词典

在 dictionary_config.json 中设置项目名称、slug、版本和领域。在 data/entries/*.jsonl 编写词条，参考 examples/entry.jsonl 的结构；不要将示例原样计入实际词库。

```bash
# Python 3.10+，无需额外依赖
python build.py --check
python build.py
```

输出位于 local_output：Simple/Extended TXT、增强版 HTML 和 statistics.json。TXT 是词头@HTML格式，不是 TSV。最终 .eudic 制作见 PACKAGING.md。

记录参考资料、AI 辅助和核实情况到 SOURCES.md。交付时补充用途、实际词数及已知限制。此工程模板源自 albertorson 的 CS-AI Dictionary / dictionary-builder-skill，受随附 LICENSE（CC BY-NC-SA 4.0）约束；新增内容的权利和来源由贡献者说明。
