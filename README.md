# citation-finder-lite

零第三方依赖的"论断 → 来源定位"工具：给定一个论断句，在文档库里找出最能支撑它的句子，并标注来源文档、句序号与字符偏移。

## 功能简介

- 把每个文档按句号/问号/感叹号切成句子，并记录每句的字符偏移；
- 对论断句做句子级词袋余弦匹配，找出最相关的出处；
- 返回结构化结果：来源文件、原句、句序号、字符位置、相关度分数。

## 快速开始

```bash
python3 cli.py "余弦相似度的取值范围是 -1 到 1"
python3 cli.py "生产环境怎么平衡关键词和语义检索"
```

代码调用：

```python
from citation import CitationFinder
f = CitationFinder()
f.add_document("notes.txt", "一些文档内容……")
hits = f.find("某条论断", k=3)  # -> [Citation(doc, sentence, sent_index, char_offset, score)]
```

## 无 API key 如何运行

本项目**完全不需要 API key**，句子切分与匹配全部本地完成。

## 目录说明

```
citation-finder-lite/
├── citation.py              # 核心库：split_sentences / CitationFinder / Citation
├── cli.py                   # 命令行入口
├── tests/test_citation.py   # unittest 测试
└── README.md
```

## 运行测试

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT License，Copyright (c) 2026 ljiang9
