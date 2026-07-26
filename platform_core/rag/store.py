"""Persist + load the RAG corpus (documents + embeddings) in Snowflake.

Embeddings are stored as JSON strings for portability (no dependence on a
warehouse-native VECTOR type). Retrieval loads the whole corpus and ranks in
process — fine for a tens-of-documents corpus. The read/write interface is
backend-agnostic so a pgvector store can drop in later.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd
from snowflake.connector import SnowflakeConnection

from platform_core.config import get_settings
from platform_core.utils.logging import get_logger
from platform_core.warehouse.load import load_dataframe
from platform_core.warehouse.schemas import schema_name

log = get_logger(__name__)

CORPUS_TABLE = "rag_corpus"


@dataclass
class RagDocument:
    """One retrievable knowledge-base document."""

    doc_id: str
    title: str
    source: str  # originating mart / definition, surfaced as a citation
    text: str
    embedding: list[float]


def write_corpus(
    conn: SnowflakeConnection,
    docs: list[RagDocument],
    tenant_id: str,
    *,
    layer: str = "mart",
) -> int:
    """Full-refresh the tenant's corpus table. Returns rows written."""
    df = pd.DataFrame(
        {
            "doc_id": [d.doc_id for d in docs],
            "title": [d.title for d in docs],
            "source": [d.source for d in docs],
            "doc_text": [d.text for d in docs],
            "embedding": [json.dumps(d.embedding) for d in docs],
        }
    )
    n = load_dataframe(
        conn,
        df,
        table=CORPUS_TABLE,
        schema=schema_name(layer, tenant_id),
        overwrite=True,
    )
    log.info("write_corpus", rows=n, tenant=tenant_id)
    return n


def read_corpus(
    conn: SnowflakeConnection, tenant_id: str, *, layer: str = "mart"
) -> list[RagDocument]:
    """Load the full corpus (with embeddings) for a tenant."""
    db = get_settings().snowflake_database
    table = f"{db}.{schema_name(layer, tenant_id)}.{CORPUS_TABLE}"
    cur = conn.cursor()
    cur.execute(f"select doc_id, title, source, doc_text, embedding from {table}")
    docs = [
        RagDocument(
            doc_id=row[0],
            title=row[1],
            source=row[2],
            text=row[3],
            embedding=json.loads(row[4]),
        )
        for row in cur.fetchall()
    ]
    log.info("read_corpus", rows=len(docs), tenant=tenant_id)
    return docs
