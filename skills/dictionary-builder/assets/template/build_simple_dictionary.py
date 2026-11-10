# -*- coding: utf-8 -*-
"""从项目配置指定的共享数据渲染欧路简洁版 TXT。

格式与 v1.0 简洁版完全同构：每行「词头@单段 HTML」，七个字段：
中文释义 / 词性 / 专业释义 / 场景辨析 / 例句 / 易混淆词 / 所属领域。
与增强版共用同一份主数据，只是渲染更轻。
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any
from dictionary_config import CONFIG, output_name

ROOT = Path(__file__).resolve().parent
LOCAL_OUTPUT = ROOT / "local_output"
DATA_DIR = ROOT / "extended_data" / "v1.1"
BASE_SOURCE = DATA_DIR / "base_v1.0.json"
ADDITION_DIR = DATA_DIR / "additions"
# 简洁版生成结果放入本地输出目录
OUTPUT = LOCAL_OUTPUT / output_name('Simple', '_EudicBuilder.txt')

# 读取增强版 TXT，检查两个版本的词头是否一致
EXTENDED_TXT = LOCAL_OUTPUT / output_name('Extended', '_EudicBuilder.txt')

FIELDS = ("中文释义", "词性", "专业释义", "场景辨析", "例句", "易混淆词", "所属领域")


def load_entries() -> list[dict[str, Any]]:
    from build_extended_dictionary import load_entries as load_all, validate_entries
    entries, _ = load_all()
    validate_entries(entries)
    return entries


def esc(value: str) -> str:
    return html.escape(value.replace("\r", " ").replace("\n", " "), quote=True).replace("@", "&#64;")


def rich(value: str) -> str:
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", esc(value))


def scene_text(entry: dict[str, Any]) -> str:
    """旧 300 条有整段 context_note 就直接用；新增条目按「场景：译法（说明）」串起来。"""
    note = (entry.get("context_note") or "").strip()
    if note:
        return note
    parts = []
    for item in entry["contexts"]:
        scene = item["scene"].strip()
        translation = item["translation"].strip()
        detail = item["note"].strip().rstrip("。；;.")
        parts.append(f"{scene}：{translation}（{detail}）" if detail else f"{scene}：{translation}")
    return "；".join(parts)


def render_line(entry: dict[str, Any]) -> str:
    example = entry["examples"][0]
    en = example["en"].replace("`", "").strip()
    zh = example["zh"].replace("`", "").strip()
    body = (
        f"<b>中文释义：</b>{rich(entry['core'])}<br>"
        f"<b>词性：</b>{esc(entry['pos'].strip())}<br>"
        f"<b>专业释义：</b>{rich(entry['definition'])}<br>"
        f"<b>场景辨析：</b>{rich(scene_text(entry))}<br>"
        f"<b>例句：</b><br><code>{esc(en)} — {esc(zh)}</code><br>"
        f"<b>易混淆词：</b>{rich(entry['distinction'])}<br>"
        f"<b>所属领域：</b>{esc(entry['domain'])}"
    )
    line = f"{entry['word'].strip()}@{body}"
    if line.count("@") != 1:
        raise ValueError(f"{entry['word']} 的解释中包含未转义的 @")
    return line


def verify(lines: list[str]) -> None:
    """按 prepare_extended_data.py 的解析规则反解，确保欧路与后续脚本都能读回。"""
    pattern = re.compile(rf"<b>({'|'.join(FIELDS)})：</b>(.*?)(?=<br><b>(?:{'|'.join(FIELDS)})：</b>|$)")
    seen: dict[str, str] = {}
    for index, line in enumerate(lines, 1):
        if line.count("@") != 1:
            raise ValueError(f"第 {index} 行 @ 数量不为 1")
        word, body = line.split("@", 1)
        found = {m.group(1) for m in pattern.finditer(body)}
        missing = [field for field in FIELDS if field not in found]
        if missing:
            raise ValueError(f"第 {index} 行（{word}）缺少字段：{missing}")
        example = re.search(r"<b>例句：</b><br><code>(.*?)</code>", body)
        if not example:
            raise ValueError(f"第 {index} 行（{word}）例句格式异常")
        if len(re.split(r"\s+—\s+", example.group(1))) != 2:
            raise ValueError(f"第 {index} 行（{word}）例句无法拆成英文和中文")
        key = re.sub(r"\s+", " ", word.strip()).casefold()
        if key in seen:
            raise ValueError(f"重复词头：{seen[key]} / {word}")
        seen[key] = word


def main() -> None:
    parser = argparse.ArgumentParser(description=f"构建 {CONFIG['name']} 简洁版")
    parser.add_argument("--check", action="store_true", help="只校验，不写文件")
    args = parser.parse_args()

    entries = load_entries()
    lines = [render_line(entry) for entry in entries]
    verify(lines)
    print(f"词条总数：{len(lines)}")
    print("结构校验通过：7 字段齐全、每行 1 个 @、例句可拆分、词头无重复且与增强版一致。")
    if args.check:
        return
    LOCAL_OUTPUT.mkdir(exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"已生成 {len(lines)} 行：{OUTPUT}")


if __name__ == "__main__":
    main()
