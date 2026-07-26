"""Text embeddings for RAG.

Local sentence-transformers by default (free, runs offline, 384-dim, deterministic
— no second API key). The 'voyage' provider is scaffolded in config but not wired
here yet.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model(name: str):
    """Load (and cache) the sentence-transformers model. First call is slow."""
    from sentence_transformers import SentenceTransformer

    log.info("embedder_load", model=name)
    return SentenceTransformer(name)


class Embedder:
    """Wraps a local sentence-transformers model, returning normalized vectors."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        if settings.embedding_provider != "sentence_transformers":
            raise NotImplementedError(
                f"embedding_provider={settings.embedding_provider!r} not wired; "
                "use 'sentence_transformers'"
            )
        self.model_name = model or settings.sentence_transformers_model

    def encode(self, texts: list[str]) -> np.ndarray:
        """Return an (n, dim) float32 array of L2-normalized embeddings.

        Normalizing here means cosine similarity reduces to a dot product at
        retrieval time.
        """
        model = _load_model(self.model_name)
        vecs = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return np.asarray(vecs, dtype=np.float32)

    def encode_one(self, text: str) -> np.ndarray:
        """Embed a single string, returning a 1-D vector."""
        return self.encode([text])[0]
