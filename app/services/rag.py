from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text

from app.models import DocumentChunk
from app.services.embeddings import get_query_embedding


def search_relevant_chunks(query: str, top_k: int, db: Session) -> List[DocumentChunk]:
    print("Searching relevant knowledge chunks ...")
    try:
        embedding = get_query_embedding(query)
        if not embedding:
            print("⚠ No embedding generated — returning empty chunks")
            return []

        embedding_str = "[" + ",".join(map(str, embedding)) + "]"
        print(f"Embedding generated with length: {len(embedding)}")

        sql = """
            SELECT 
                id, 
                url, 
                title, 
                chunk_index, 
                content, 
                created_at
            FROM document_chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <-> :embedding
            LIMIT :k
        """

        print("Executing semantic chunk ranking SQL")
        rows = db.execute(
            sa_text(sql),
            {"embedding": embedding_str, "k": top_k},
        ).fetchall()

        print(f"Chunk search returned {len(rows)} results")
        return rows

    except Exception as e:
        print(f"Search_relevant_chunks error: {e}")
        db.rollback()
        return []


def build_context(chunks: List) -> str:
    if not chunks:
        print("ℹ build_context: No chunks to build context from")
        return ""

    print("Building RAG context from chunks")

    parts = []
    for row in chunks[:5]:  # extra defensive slice
        title = row.title if hasattr(row, "title") else ""
        url = row.url if hasattr(row, "url") else ""
        content = row.content if hasattr(row, "content") else ""

        # Trim super-long content to avoid bill shock
        content = (content[:1200] + "…") if len(content) > 1200 else content

        parts.append(f"Source: {title} ({url})\n\n{content}\n")

    context = "\n----------------\n".join(parts)

    print(f"Final RAG context length: {len(context)} chars")
    return context
