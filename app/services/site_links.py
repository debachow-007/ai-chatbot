from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text
from app.services.embeddings import get_query_embedding


def _clean_url_title(url: str) -> str:
    part = url.rstrip("/").split("/")[-1]
    part = part.replace("-", " ").replace("_", " ").strip()
    return part.title() if part else "Learn More"


def get_relevant_links_from_chunks(query: str, db: Session, limit: int = 3):
    print("🔗 [site_links] Searching with pgvector + keywords for:", query)

    links = []
    seen = set()

    try:
        embed = get_query_embedding(query)  # Should return Python list of floats
        embedding_str = f"[{', '.join(str(float(x)) for x in embed)}]"

        vector_sql = """
            SELECT url, COALESCE(title, '') AS title,
                   (embedding <-> CAST(:embedding AS vector)) AS distance
            FROM document_chunks
            WHERE embedding IS NOT NULL AND url IS NOT NULL AND url != ''
            ORDER BY embedding <-> CAST(:embedding AS vector)
            LIMIT :limit;
        """

        vector_rows = db.execute(
            sa_text(vector_sql),
            {"embedding": embedding_str, "limit": limit * 3}
        ).fetchall()

        print("🔗 Vector matches:", len(vector_rows))

        for url, title, distance in vector_rows:
            url = url.split("?")[0].split("#")[0].rstrip("/")
            if url in seen:
                continue

            seen.add(url)
            safe_title = title.strip() if title.strip() else _clean_url_title(url)
            links.append({"url": url, "title": safe_title, "score": float(distance)})

            if len(links) >= limit:
                return links

    except Exception as e:
        print("❌ Vector search failed:", e)
        db.rollback()

    words = [w.strip() for w in query.lower().split() if w.strip()]
    if not words:
        return links[:limit]

    patterns = [f"%{w}%" for w in words]

    try:
        keyword_sql = """
            SELECT url, COALESCE(title, '') AS title, COUNT(*) AS score
            FROM document_chunks
            WHERE (LOWER(content) ILIKE ANY(:patterns)
                OR LOWER(title) ILIKE ANY(:patterns))
            GROUP BY url, title
            HAVING COUNT(*) >= 2
            ORDER BY score DESC
            LIMIT :limit;
        """

        keyword_rows = db.execute(
            sa_text(keyword_sql),
            {"patterns": patterns, "limit": limit * 3}
        ).fetchall()

        print("🔗 Keyword matches:", len(keyword_rows))

        for url, title, score in keyword_rows:
            url = url.split("?")[0].split("#")[0].rstrip("/")
            if url in seen:
                continue

            seen.add(url)
            safe_title = title.strip() if title.strip() else _clean_url_title(url)
            links.append({"url": url, "title": safe_title, "score": int(score)})

            if len(links) >= limit:
                break

    except Exception as e:
        print("❌ Keyword search failed:", e)
        db.rollback()

    return links[:limit]
