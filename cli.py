#!/usr/bin/env python3
"""cli.py — citation-finder-lite 命令行入口。

用法：python3 cli.py "你的论断句"

在内置样例文档库中找最支撑该论断的句子，并标注来源。
"""
from __future__ import annotations

import sys

from citation import SAMPLE_LIB, CitationFinder


def main(argv=None) -> int:
    claim = argv[0] if argv else "余弦相似度的取值范围是 -1 到 1"
    finder = CitationFinder()
    for name, text in SAMPLE_LIB.items():
        finder.add_document(name, text)

    print(f"论断：{claim}\n")
    hits = finder.find(claim, k=3)
    if not hits:
        print("未找到任何相关出处。")
        return 1
    print(f"最支撑的 {len(hits)} 个出处：")
    for rank, c in enumerate(hits, 1):
        print(f"  {rank}. [score={c.score:.4f}] 《{c.doc}》"
              f" 第{c.sent_index + 1}句 (偏移{c.char_offset})")
        print(f"     「{c.sentence}」")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
