# -*- coding: utf-8 -*-
"""从主数据（base_v1.0.json + additions/*.jsonl）单向生成可编辑 CSV 镜像。"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from dictionary_config import output_name

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "extended_data" / "v1.1"
ADDITION_DIR = DATA_DIR / "additions"
LOCAL_OUTPUT = ROOT / "local_output"
OUT = LOCAL_OUTPUT / output_name('Extended', '.csv')


def load_entries() -> list[dict]:
    from build_extended_dictionary import load_entries as load_all, validate_entries
    entries, _ = load_all()
    validate_entries(entries)
    return entries


def flatten_contexts(items: list[dict]) -> str:
    return " || ".join(
        f"场景：{x['scene']}；翻译：{x['translation']}；说明：{x['note']}" for x in items
    )


def flatten_pairs(items: list[dict], en_key: str, zh_key: str) -> str:
    return " || ".join(f"{x[en_key]} — {x[zh_key]}" for x in items)


def main() -> None:
    entries = load_entries()
    fields = [
        "word", "ipa", "pos", "domain", "core", "definition",
        "contexts", "context_note", "collocations", "examples",
        "distinction", "status", "batch",
    ]
    LOCAL_OUTPUT.mkdir(exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for e in entries:
            writer.writerow({
                "word": e["word"],
                "ipa": e.get("ipa", ""),
                "pos": e["pos"],
                "domain": e["domain"],
                "core": e["core"],
                "definition": e["definition"],
                "contexts": flatten_contexts(e["contexts"]),
                "context_note": e.get("context_note", ""),
                "collocations": flatten_pairs(e["collocations"], "en", "zh"),
                "examples": flatten_pairs(e["examples"], "en", "zh"),
                "distinction": e["distinction"],
                "status": e.get("status", "new"),
                "batch": e.get("batch", ""),
            })
    print(f"已导出 {len(entries)} 条：{OUT}")


if __name__ == "__main__":
    main()
