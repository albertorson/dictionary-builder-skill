# 词条结构

使用 UTF-8 JSONL，每行一个 JSON 对象。模板位于 assets/template/examples/entry.jsonl，复制后替换全部示例内容，domain 必须与项目配置匹配。

| 字段 | 要求 |
|---|---|
| word | 非空词头，全库忽略大小写及多余空格后唯一 |
| pos | 词性，如 n.、v.、abbr. |
| domain | dictionary_config.json 的 domains 键 |
| core | 中文简短释义 |
| definition | 中文专业释义，新条目至少 20 字符 |
| contexts | 1–4 个对象，各有 scene、translation、note |
| collocations | 3–5 个对象，各有 en、zh |
| examples | 1–3 个对象，各有 en、zh |
| distinction | 中文易混辨析，至少 10 字符 |
| ipa | 可选，不确定时省略，避免编造 |

status 和 batch 由读取器补充，新词不设 preserved。简洁版采用第一条例句；增强版包含全部语境、搭配与例句。专业领域配置可随项目扩充。

来源记录放 SOURCES.md，以词头或批次映射来源链接/书目、参考用途、AI 辅助和人工核实状态；不要添加未被 schema 支持的字段。验证器检查结构与重复，不检查知识真实性。
