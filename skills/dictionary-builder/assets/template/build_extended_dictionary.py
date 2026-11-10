from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from dictionary_config import CONFIG, output_name

ROOT = Path(__file__).resolve().parent
LOCAL_OUTPUT = ROOT / "local_output"
DATA_DIR = ROOT / "extended_data" / "v1.1"
BASE_SOURCE = ROOT / CONFIG['base_source'] if CONFIG.get('base_source') else None
ADDITION_DIR = ROOT / CONFIG['additions_dir']
COMMUNITY_DIR = ROOT / CONFIG['community_dir']
BASELINE = ROOT / "CS_AI_Dictionary_Enhanced_v1.0_EudicBuilder.txt"
OUTPUT = LOCAL_OUTPUT / output_name('Extended', '_EudicBuilder.txt')
PREVIEW = LOCAL_OUTPUT / output_name('Extended', '_preview.html')
BASELINE_ARCHIVE = ROOT / "backups" / "v1.0_2026-11-09" / "CS_AI_Dictionary_Enhanced_v1.0_EudicBuilder.txt"

DOMAIN_ZH = CONFIG['domains']
POS_ZH = {
    "n.": "名词",
    "v.": "动词",
    "n./v.": "名词 / 动词",
    "v./n.": "动词 / 名词",
    "abbr.": "缩写",
}
ENTRY_KEYS = {
    "word", "ipa", "pos", "domain", "core", "definition", "contexts",
    "context_note", "collocations", "examples", "distinction", "status", "batch",
}
CSS = """
.csai-entry{--csai-accent:#167d78;--csai-ink:#172524;--csai-muted:#687876;--csai-line:#e2ebea;box-sizing:border-box;max-width:980px;margin:0 auto;padding:clamp(16px,3vw,28px);background:#fff;color:var(--csai-ink);border:1px solid var(--csai-line);border-radius:14px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif;font-size:15px;line-height:1.75;text-align:left}
.csai-entry *{box-sizing:border-box}.csai-head{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.csai-word{font-size:clamp(27px,4vw,32px);line-height:1.25;font-weight:750;color:#10201f;overflow-wrap:anywhere}.csai-domain{display:inline-block;padding:1px 10px;border-radius:999px;background:#e5f6ee;color:#16815d;font-size:12px;font-weight:600;line-height:1.8}.csai-meta{margin:4px 0 20px;color:var(--csai-muted);font-size:13px}.csai-core{margin:0 0 8px;font-size:clamp(21px,3vw,24px);line-height:1.45;font-weight:700;color:#123f3b}.csai-definition{margin:0 0 22px;line-height:1.9}.csai-fold{margin:10px 0;border:1px solid #dce9e7;border-radius:9px;background:#f4f9f8;overflow:hidden}.csai-fold>summary{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:11px 15px;cursor:pointer;list-style:none;color:var(--csai-accent);font-size:16px;font-weight:700;outline:none}.csai-fold>summary::-webkit-details-marker{display:none}.csai-fold>summary::marker{display:none}.csai-arrow{flex:0 0 12px;width:12px;height:12px;position:relative}.csai-arrow::before{content:'';position:absolute;left:1px;top:1px;width:7px;height:7px;border-right:2px solid #4c9691;border-bottom:2px solid #4c9691;transform:rotate(-45deg);transition:transform .16s ease}.csai-fold[open] .csai-arrow::before{top:4px;transform:rotate(45deg)}.csai-fold-body{padding:4px 15px 16px;border-top:1px solid #dce9e7;background:#fff}.csai-table{width:100%;margin:8px 0 4px;border-collapse:collapse;table-layout:auto}.csai-table th{padding:9px 10px;background:#f3f7f6;color:#304441;font-size:13px;text-align:left;border-bottom:1px solid var(--csai-line)}.csai-table td{padding:10px;vertical-align:top;border-bottom:1px solid #e8efee;overflow-wrap:anywhere}.csai-table tr:last-child td{border-bottom:0}.csai-table td:first-child{font-weight:600}.csai-note{color:#52625f}.csai-example{margin:12px 0;padding:12px 14px;border-left:3px solid #71b7b0;border-radius:0 7px 7px 0;background:#f6f9f9}.csai-example-en{display:block;color:#243937;font-family:'Cascadia Code','SFMono-Regular',Consolas,monospace;font-size:14px;line-height:1.65;overflow-wrap:anywhere}.csai-example-zh{display:block;margin-top:5px;color:#455653}.csai-distinction{margin:10px 0 0;padding:12px 14px;border-radius:8px;background:#fff8e8;color:#55472e;line-height:1.85}.csai-distinction b{color:#8b6616}.csai-entry code{padding:1px 5px;border-radius:4px;background:#eff4f3;color:#235b56;font-family:'Cascadia Code','SFMono-Regular',Consolas,monospace;font-size:.93em}.csai-original{margin:10px 0 0;color:#52625f}.csai-related{margin-top:12px;color:#52625f;font-size:14px}
""".strip()


def normalize_headword(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def has_cjk(value: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", value))


def load_json_entries(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict) and "entries" in data:
        data = data["entries"]
    if isinstance(data, dict):
        data = list(data.values())
    if not isinstance(data, list):
        raise ValueError(f"{path.name} 必须是词条数组、以词头为键的对象，或包含 entries 的对象")
    return data


def load_entries() -> tuple[list[dict[str, Any]], list[str]]:
    entries = load_json_entries(BASE_SOURCE) if BASE_SOURCE else []
    loaded_files = [BASE_SOURCE.name] if BASE_SOURCE else []
    for path in sorted(ADDITION_DIR.glob("*.jsonl")) + sorted(COMMUNITY_DIR.glob("*.jsonl")):
        loaded_files.append(path.name)
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{line_number} JSON 解析失败：{exc}") from exc
            entry.setdefault("status", "new")
            entry.setdefault("batch", path.stem)
            entries.append(entry)
    for path in sorted(ADDITION_DIR.glob("*.json")):
        loaded_files.append(path.name)
        for entry in load_json_entries(path):
            entry.setdefault("status", "new")
            entry.setdefault("batch", path.stem)
            entries.append(entry)
    return entries, loaded_files


def validate_entry(entry: dict[str, Any], location: str) -> None:
    unknown = set(entry) - ENTRY_KEYS
    if unknown:
        raise ValueError(f"{location} 含未知字段：{sorted(unknown)}")
    missing = {"word", "pos", "domain", "core", "definition", "contexts",
               "collocations", "examples", "distinction"} - set(entry)
    if missing:
        raise ValueError(f"{location} 缺少字段：{sorted(missing)}")
    word = entry["word"]
    if not isinstance(word, str) or not word.strip():
        raise ValueError(f"{location} 的 word 不能为空")
    if "@" in word or "\n" in word or "\r" in word:
        raise ValueError(f"{word} 的词头不能包含 @ 或换行")
    if entry["domain"] not in DOMAIN_ZH:
        raise ValueError(f"{word} 的 domain 无效：{entry['domain']}")
    for field in ("core", "definition", "distinction"):
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{word} 的 {field} 不能为空")
        if not has_cjk(value):
            raise ValueError(f"{word} 的 {field} 必须包含中文")
    if entry.get("status") == "new":
        if len(entry["definition"].strip()) < 20:
            raise ValueError(f"{word} 的专业释义过短")
        if len(entry["distinction"].strip()) < 10:
            raise ValueError(f"{word} 的易混淆词辨析过短")
    if not isinstance(entry["pos"], str) or not entry["pos"].strip():
        raise ValueError(f"{word} 的 pos 不能为空")
    if entry.get("ipa") and not isinstance(entry["ipa"], str):
        raise ValueError(f"{word} 的 ipa 必须是字符串")
    contexts = entry["contexts"]
    if not isinstance(contexts, list) or not 1 <= len(contexts) <= 4:
        raise ValueError(f"{word} 的 contexts 数量应为 1–4")
    for item in contexts:
        if not isinstance(item, dict) or set(item) != {"scene", "translation", "note"}:
            raise ValueError(f"{word} 的 context 必须且只能包含 scene/translation/note")
        for key in ("scene", "translation", "note"):
            value = item[key]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{word} 的 context.{key} 不能为空")
        if not has_cjk(item["note"]):
            raise ValueError(f"{word} 的 context.note 必须包含中文")
    collocations = entry["collocations"]
    if not isinstance(collocations, list) or not 3 <= len(collocations) <= 5:
        raise ValueError(f"{word} 的 collocations 数量应为 3–5")
    for item in collocations:
        if not isinstance(item, dict) or set(item) != {"en", "zh"}:
            raise ValueError(f"{word} 的 collocation 必须且只能包含 en/zh")
        if not isinstance(item["en"], str) or not item["en"].strip():
            raise ValueError(f"{word} 的 collocation.en 不能为空")
        if not isinstance(item["zh"], str) or not item["zh"].strip():
            raise ValueError(f"{word} 的 collocation.zh 不能为空")
    examples = entry["examples"]
    if not isinstance(examples, list) or not 1 <= len(examples) <= 3:
        raise ValueError(f"{word} 的 examples 数量应为 1–3")
    for item in examples:
        if not isinstance(item, dict) or set(item) != {"en", "zh"}:
            raise ValueError(f"{word} 的 example 必须且只能包含 en/zh")
        if not isinstance(item["en"], str) or not item["en"].strip():
            raise ValueError(f"{word} 的 example.en 不能为空")
        if not isinstance(item["zh"], str) or not item["zh"].strip() or not has_cjk(item["zh"]):
            raise ValueError(f"{word} 的 example.zh 必须是非空中文")
    if entry.get("context_note"):
        if not isinstance(entry["context_note"], str) or not has_cjk(entry["context_note"]):
            raise ValueError(f"{word} 的 context_note 必须是非空中文")
    if entry.get("status") not in {"preserved", "new"}:
        raise ValueError(f"{word} 的 status 无效")
    if entry.get("batch") is not None and not isinstance(entry["batch"], str):
        raise ValueError(f"{word} 的 batch 必须是字符串")


def validate_entries(entries: list[dict[str, Any]]) -> Counter:
    if not entries:
        raise ValueError("词典不能为空")
    seen: dict[str, str] = {}
    counts: Counter = Counter()
    for index, entry in enumerate(entries, 1):
        location = f"第 {index} 条"
        validate_entry(entry, location)
        key = normalize_headword(entry["word"])
        if key in seen:
            raise ValueError(f"重复词头（大小写归一化）：{seen[key]} / {entry['word']}")
        seen[key] = entry["word"]
        counts[entry["domain"]] += 1
    return counts


def esc(value: str) -> str:
    return html.escape(value, quote=True).replace("@", "&#64;")


def rich_text(value: str) -> str:
    escaped = esc(value)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)


def fold(title: str, content: str) -> str:
    return (
        '<details class="csai-fold">'
        f'<summary><span>{esc(title)}</span><span class="csai-arrow" aria-hidden="true"></span></summary>'
        f'<div class="csai-fold-body">{content}</div></details>'
    )


def render_entry(entry: dict[str, Any]) -> str:
    word = entry["word"].strip()
    domain = DOMAIN_ZH[entry["domain"]]
    pos = entry["pos"].strip()
    pos_zh = POS_ZH.get(pos, "")
    meta_parts = []
    ipa = entry.get("ipa", "").strip()
    if ipa:
        meta_parts.append(ipa if ipa.startswith(("/", "[")) else f"/{ipa}/")
    meta_parts.append(pos)
    if pos_zh:
        meta_parts.append(pos_zh)
    meta = " · ".join(meta_parts)
    context_rows = "".join(
        f'<tr><td>{esc(item["scene"])}</td><td>{esc(item["translation"])}</td><td class="csai-note">{rich_text(item["note"])}</td></tr>'
        for item in entry["contexts"]
    )
    contexts = (
        '<table class="csai-table"><thead><tr><th>使用场景</th><th>推荐翻译</th><th>语境说明</th></tr></thead>'
        f'<tbody>{context_rows}</tbody></table>'
    )
    if entry.get("context_note"):
        contexts += f'<p class="csai-original"><b>原场景辨析：</b>{rich_text(entry["context_note"])}</p>'
    collocation_rows = "".join(
        f'<tr><td>{rich_text(item["en"])}</td><td>{esc(item["zh"])}</td></tr>'
        for item in entry["collocations"]
    )
    collocations = (
        '<table class="csai-table"><thead><tr><th>英文表达</th><th>推荐翻译</th></tr></thead>'
        f'<tbody>{collocation_rows}</tbody></table>'
    )
    examples = "".join(
        f'<div class="csai-example"><span class="csai-example-en">{rich_text(item["en"])}</span>'
        f'<span class="csai-example-zh">{esc(item["zh"])}</span></div>'
        for item in entry["examples"]
    )
    distinction = f'<div class="csai-distinction"><b>关键区别：</b>{rich_text(entry["distinction"])}</div>'
    return "".join([
        '<div class="csai-entry">',
        f'<style>{CSS}</style>',
        f'<div class="csai-head"><span class="csai-word">{esc(word)}</span><span class="csai-domain">{esc(domain)}</span></div>',
        f'<div class="csai-meta">{esc(meta)}</div>',
        f'<div class="csai-core">{esc(entry["core"])}</div>',
        f'<div class="csai-definition">{rich_text(entry["definition"])}</div>',
        fold("不同语境下的含义", contexts),
        fold("常见搭配", collocations),
        fold("实际例句", examples),
        fold("易混淆词辨析", distinction),
        '</div>',
    ])


def source_line(entry: dict[str, Any]) -> str:
    word = entry["word"].strip()
    body = render_entry(entry).replace("\r", " ").replace("\n", " ")
    line = f"{word}@{body}"
    if line.count("@") != 1:
        raise ValueError(f"{word} 的解释中包含未转义的 @")
    body = line.split("@", 1)[1]
    if body.count('<details class="csai-fold">') != 4:
        raise ValueError(f"{word} 必须包含四个折叠板块")
    if body.count("<details") != body.count("</details>"):
        raise ValueError(f"{word} 的 details 标签不配平")
    return line


def baseline_path() -> Path:
    """基线文件优先取项目根目录，v1.0 增强版归档后自动回退到 backups。"""
    for candidate in (BASELINE, BASELINE_ARCHIVE):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("找不到 v1.0 增强版基线文件，--baseline-check 无法执行")


def check_baseline(entries: list[dict[str, Any]]) -> None:
    base = [entry for entry in entries if entry.get("status") == "preserved"]
    actual = [source_line(entry) for entry in base]
    expected = baseline_path().read_text(encoding="utf-8").splitlines()
    if len(expected) != 300:
        raise ValueError(f"基线文件应为 300 行，实际 {len(expected)} 行")
    if actual != expected:
        for index, (left, right) in enumerate(zip(actual, expected), 1):
            if left != right:
                raise ValueError(f"基线第 {index} 行无法逐字重建，样式或内容已发生变化")
        raise ValueError("基线与现有 300 条输出不一致")
    print("基线检查通过：现有 300 条词条可逐字重建，UI 与内容未变化。")


def build_preview(rendered: list[tuple[str, str]]) -> None:
    articles = "".join(
        f'<article id="entry-{index}" data-word="{esc(word.lower())}" style="display:none;margin:24px auto">{body}</article>'
        for index, (word, body) in enumerate(rendered)
    )
    options = "".join(f'<option value="{esc(word)}">' for word, _ in rendered)
    document = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(CONFIG['name'])} {esc(CONFIG['version'])} Preview</title>
<style>body{{margin:0;background:#eef3f2;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Microsoft YaHei',sans-serif}}.preview-nav{{position:sticky;top:0;z-index:5;padding:14px 20px;background:#ffffffee;border-bottom:1px solid #dce6e4;backdrop-filter:blur(8px)}}.preview-nav input{{box-sizing:border-box;width:min(680px,100%);padding:11px 14px;border:1px solid #bdcecb;border-radius:8px;font-size:16px;outline:none}}.preview-nav input:focus{{border-color:#167d78;box-shadow:0 0 0 3px #167d7820}}#empty{{display:none;text-align:center;color:#687876}}</style></head>
<body><div class="preview-nav"><input id="search" list="words" value="session" aria-label="查询词条" autocomplete="off"><datalist id="words">{options}</datalist></div><main>{articles}</main><p id="empty">未找到词条</p>
<script>
const input=document.getElementById('search');const articles=[...document.querySelectorAll('article')];const empty=document.getElementById('empty');
function showEntry(){{const query=input.value.trim().toLowerCase();let shown=0;for(const article of articles){{const match=article.dataset.word===query;article.style.display=match?'block':'none';if(match)shown++}}empty.style.display=shown?'none':'block'}}
input.addEventListener('input',showEntry);showEntry();
</script></body></html>"""
    # 新领域不一定包含 session，预览默认显示当前词典的第一条。
    document = document.replace('value="session"', f'value="{esc(rendered[0][0])}"', 1)
    PREVIEW.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=f"构建 {CONFIG['name']} 增强版")
    parser.add_argument("--check", action="store_true", help="只校验，不写文件")
    parser.add_argument("--strict", action="store_true", help="兼容旧命令；所有构建始终执行结构与重复词校验，无词数配额")
    parser.add_argument("--baseline-check", action="store_true", help="校验现有 300 条可逐字重建")
    args = parser.parse_args()

    entries, loaded_files = load_entries()
    counts = validate_entries(entries)
    if args.baseline_check:
        check_baseline(entries)
    print(f"词条总数：{len(entries)}")
    print("数据文件：", ", ".join(loaded_files))
    print("领域分布：")
    for domain in DOMAIN_ZH:
        print(f"  {DOMAIN_ZH[domain]}：{counts[domain]}")
    if args.check:
        print("结构校验通过。")
        return
    # 如果 local_output 不存在，就自动创建
    LOCAL_OUTPUT.mkdir(exist_ok=True)
    rendered = [(entry["word"].strip(), render_entry(entry)) for entry in entries]
    lines = [source_line(entry) for entry in entries]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    build_preview(rendered)
    print(f"已生成 {len(lines)} 个词条：{OUTPUT}")
    print(f"已生成浏览器预览：{PREVIEW}")


if __name__ == "__main__":
    main()
