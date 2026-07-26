"""In-process cosine top-k retrieval over an embedded corpus."""
from __future__ import annotations

import numpy as np

from platform_core.rag.store import RagDocument


def top_k(
    query_vec: np.ndarray, docs: list[RagDocument], k: int = 6
) -> list[tuple[RagDocument, float]]:
    """Return the k documents most similar to ``query_vec`` with cosine scores.

    Corpus embeddings are stored L2-normalized, so cosine similarity is a dot
    product against the (normalized) query vector.
    """
    if not docs:
        return []
    matrix = np.asarray([d.embedding for d in docs], dtype=np.float32)
    q = np.asarray(query_vec, dtype=np.float32)
    q = q / (float(np.linalg.norm(q)) or 1.0)
    scores = matrix @ q
    order = np.argsort(-scores)[: max(0, k)]
    return [(docs[i], float(scores[i])) for i in order]
