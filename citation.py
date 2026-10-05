"""citation.py — 论断 -> 来源定位（零第三方依赖）。

给定一个论断句，在文档库中找出最能支撑它的句子，并标注来源文档、
句序号与字符位置。本质是"句子级"的检索：先把文档切成句子，再用
词袋余弦 + 关键词重合打分，取最高分句子作为出处。
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]+")
_SENT_SPLIT = re.compile(r"(?<=[。！？!?；;\n])")


def tokenize(text: str) -> List[str]:
    """英文/数字成词；中文连续段切二元组（bigram），避免单字噪声。"""
    out: List[str] = []
    for m in _TOKEN_RE.findall(text.lower()):
        if re.match(r"[\u4e00-\u9fff]", m):
            if len(m) == 1:
                out.append(m)
            else:
                out.extend(m[i:i + 2] for i in range(len(m) - 1))
        else:
            out.append(m)
    return out


def split_sentences(text: str) -> List[Tuple[str, int]]:
    """切句子，返回 [(句子, 起始字符偏移), ...]。"""
    out: List[Tuple[str, int]] = []
    pos = 0
    for raw in _SENT_SPLIT.split(text):
        s = raw.strip()
        if not s:
            pos += len(raw)
            continue
        idx = text.find(s, pos)
        if idx < 0:
            idx = pos
        out.append((s, idx))
        pos = idx + len(s)
    return out


@dataclass
class Citation:
    doc: str
    sentence: str
    sent_index: int
    char_offset: int
    score: float


class CitationFinder:
    def __init__(self) -> None:
        self.docs: Dict[str, str] = {}
        # sentences: list of (doc, sent_index, offset, text, counter)
        self.index: List[Tuple[str, int, int, str, Counter]] = []

    def add_document(self, name: str, text: str) -> None:
        self.docs[name] = text
        for i, (sent, offset) in enumerate(split_sentences(text)):
            self.index.append((name, i, offset, sent, Counter(tokenize(sent))))

    @staticmethod
    def _cos(a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        dot = sum(c * b.get(t, 0) for t, c in a.items())
        na = math.sqrt(sum(c * c for c in a.values()))
        nb = math.sqrt(sum(c * c for c in b.values()))
        return dot / (na * nb) if na and nb else 0.0

    def find(self, claim: str, k: int = 3) -> List[Citation]:
        q = Counter(tokenize(claim))
        if not q or not self.index:
            return []
        scored: List[Citation] = []
        for doc, sidx, offset, sent, scount in self.index:
            score = self._cos(q, scount)
            if score > 0:
                scored.append(Citation(doc, sent, sidx, offset, score))
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:k]


# 内置样例文档（无 key 即可跑）。
SAMPLE_LIB: Dict[str, str] = {
    "向量检索.txt": (
        "余弦相似度衡量两个向量夹角的余弦值。它对文本长度不敏感，取值在 -1 到 1 之间。"
        "向量检索把文本映射到高维空间后召回最相似的片段。"
    ),
    "工程实践.txt": (
        "生产环境通常先用 BM25 粗召，再用向量精排。"
        "混合检索能同时兼顾关键词精确匹配与语义泛化。"
        "上线前要做离线评测和灰度。"
    ),
}
