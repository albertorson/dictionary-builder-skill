---
name: dictionary-builder
description: 为指定专业领域创建可持续维护的中英欧路词典项目，生成结构化词条、简洁版与增强版 TXT、HTML 预览和打包指南。适用于金融、电气工程等领域的新词典或扩充现有词典。
---

# 专业词典制作

交付可运行的词典工程，词条数量由任务决定，不设固定配额。模板只生成 TXT/HTML，最终 .eudic 需 Windows 欧路构建器打包；不得把 TXT 改后缀冒充成品。

## 流程

1. 从用户请求确定领域、目标读者、词典名称、范围及规模；仅对影响内容的缺失信息提问。未指定规模时先做 10 条可运行样例，明确报告实际数量，不凑词。
2. 使用 `scripts/init_dictionary.py` 初始化新目录，命令参数见下。模板随 Skill 提供，不需要下载 CS-AI 的 3000 条数据，也不需要 API key。
3. 编辑生成的 `dictionary_config.json`：设置名称、slug、版本和 domains。领域标识可用英文或中文，词条 domain 必须匹配配置。创建 JSONL 文件前先读取 [references/entries.md](references/entries.md)。
4. 先做 5–10 个代表性词条供检查；用户已授权自动完成时继续分批制作。为专业定义查阅可靠来源，记录在 `SOURCES.md`，不编造引用。金融定义区分语境，工程术语注明必要的单位/适用条件；AI 草稿不等于专业审校。
5. 每批保存至 `data/entries/<主题>.jsonl`，已有词条直接修改原记录。填充有效例句和辨析，避免仅换词重复解释。来源许可不允许复制时用自己撰写的解释并记录参考依据。
6. 运行 `python build.py --check` 和 `python build.py`。核对统计与任务范围，检查 HTML 中几条代表性术语。写好项目 README（用途、实际词数、构建命令、限制）及 SOURCES.md。
7. 交付项目目录、两个 TXT 和 HTML 的本地路径、实际检查结果与未核实内容。按 `PACKAGING.md` 指导最终打包；有用户授权及工具时可协助操作，但必须验证实际产出的 .eudic 后才宣称完成。

## 初始化

在 Skill 文件夹运行（路径按当前环境替换）：

```bash
python scripts/init_dictionary.py --output /path/to/new-project --name "金融专业词典" --slug Finance_Dictionary --domain Finance --label 金融
```

初始化器只复制工程骨架，不自动生成真实词条。用户授权操作的已有项目应原位修改，不以初始化覆盖它。生成项目支持 Python 3.10+，只依赖标准库。不要修改 Skill 模板来代替修改生成项目。

## 交付约定

- JSONL 是唯一编辑源；TXT/HTML/CSV 位于 local_output 并被 Git 忽略。
- 保留模板的许可及来源说明；模板采用 CC BY-NC-SA 4.0，不擅自承诺商业授权。
- 不自动发布仓库、提交 PR 或上传词典，除非用户任务明确包含这些动作。
- 用户拿到的是可独立运行的工程，不能依赖作者电脑上的绝对路径。
