import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from citation import (  # noqa: E402
    SAMPLE_LIB,
    CitationFinder,
    split_sentences,
)


class TestSplitSentences(unittest.TestCase):
    def test_split_and_offset(self):
        text = "第一句话。第二句话！第三句?"
        sents = split_sentences(text)
        self.assertEqual(len(sents), 3)
        # 偏移应能在原文拼回句子
        for s, off in sents:
            self.assertEqual(text[off:off + len(s)], s)


class TestFinder(unittest.TestCase):
    def setUp(self):
        self.f = CitationFinder()
        for name, t in SAMPLE_LIB.items():
            self.f.add_document(name, t)

    def test_finds_supporting(self):
        hits = self.f.find("余弦相似度取值在 -1 到 1 之间", k=1)
        self.assertEqual(len(hits), 1)
        top = hits[0]
        self.assertEqual(top.doc, "向量检索.txt")
        self.assertIn("-1", top.sentence)

    def test_position_annotated(self):
        hits = self.f.find("混合检索兼顾关键词和语义", k=1)
        top = hits[0]
        self.assertGreaterEqual(top.char_offset, 0)
        self.assertGreaterEqual(top.sent_index, 0)

    def test_ordered(self):
        hits = self.f.find("向量 余弦 检索", k=3)
        scores = [h.score for h in hits]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_no_match(self):
        self.assertEqual(self.f.find("量子引力和弦理论"), [])

    def test_empty_claim(self):
        self.assertEqual(self.f.find(""), [])

    def test_empty_lib(self):
        self.assertEqual(CitationFinder().find("任意"), [])


if __name__ == "__main__":
    unittest.main()
