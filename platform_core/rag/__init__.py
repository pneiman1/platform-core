"""Retrieval-augmented-generation toolkit: embeddings, corpus store, retrieval.

Backend-agnostic by design. Embeddings are local (sentence-transformers) and the
corpus persists in the warehouse; retrieval is an in-process cosine top-k, which
is more than adequate for a tens-of-documents corpus. The RagDocument shape and
the store interface leave room for a pgvector backend later (platform-core
already ships the pgvector deps + config).
"""
from platform_core.rag.embedder import Embedder
from platform_core.rag.retrieve import top_k
from platform_core.rag.store import RagDocument, read_corpus, write_corpus

__all__ = ["Embedder", "RagDocument", "read_corpus", "write_corpus", "top_k"]
