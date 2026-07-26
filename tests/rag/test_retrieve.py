"""Unit tests for cosine top-k retrieval (no external services)."""
from __future__ import annotations

import numpy as np

from platform_core.rag.retrieve import top_k
from platform_core.rag.store import RagDocument


def _doc(doc_id: str, vec: list[float]) -> RagDocument:
    v = np.asarray(vec, dtype=np.float32)
    v = v / (float(np.linalg.norm(v)) or 1.0)
    return RagDocument(doc_id=doc_id, title=doc_id, source="test", text="", embedding=v.tolist())


def test_top_k_ranks_by_cosine_similarity():
    docs = [
        _doc("a", [1.0, 0.0, 0.0]),
        _doc("b", [0.0, 1.0, 0.0]),
        _doc("c", [0.9, 0.1, 0.0]),
    ]
    query = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    ranked = top_k(query, docs, k=2)

    assert [d.doc_id for d, _ in ranked] == ["a", "c"]
    assert ranked[0][1] > ranked[1][1]


def test_top_k_empty_corpus_returns_empty():
    assert top_k(np.asarray([1.0, 0.0]), [], k=3) == []


def test_top_k_caps_at_corpus_size():
    docs = [_doc("a", [1.0, 0.0]), _doc("b", [0.0, 1.0])]
    assert len(top_k(np.asarray([1.0, 1.0]), docs, k=10)) == 2
