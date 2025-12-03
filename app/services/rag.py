from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text

from app.models import DocumentChunk
from app.services.embeddings import get_query_embedding


def search_relevant_chunks(query: str, top_k: int, db: Session) -> List[DocumentChunk]:
    embedding = get_query_embedding(query)

    # Use raw SQL with pgvector operator
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    sql = """
        SELECT id, url, title, chunk_index, content, embedding, created_at
        FROM document_chunks
        ORDER BY embedding <-> :embedding
        LIMIT :k
    """

    rows = db.execute(
        sa_text(sql),
        {"embedding": embedding_str, "k": top_k},
    ).fetchall()

    return rows


def build_context(chunks: List) -> str:
    parts = []
    for row in chunks:
        parts.append(f"Source: {row.title or ''} ({row.url})\n{row.content}\n")
    return "\n---\n".join(parts[:5])
