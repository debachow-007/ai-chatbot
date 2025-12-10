from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text

from app.services.embeddings import get_query_embedding


STOPWORDS = {"show", "me", "give", "tell", "about", "some", "example", "examples", "please", "project", "projects"}


def _keyword_fallback_search(query: str, db: Session, limit: int) -> List[Dict[str, Any]]:
    print("\nEntering fuzzy keyword fallback search")

    words = [w.strip() for w in query.lower().split() if w.strip() and w not in STOPWORDS]
    if not words:
        print("No valid keywords extracted.")
        return []

    cleaned_query = " ".join(words)
    print(f"Cleaned query: {cleaned_query}")

    sql = """
        SELECT
            image_url,
            title,
            description,
            category,
            project_url,
            (
                0.6 * similarity(LOWER(title), :q) +
                0.3 * similarity(LOWER(description), :q) +
                0.1 * similarity(LOWER(category), :q)
            ) AS score
        FROM portfolio_items
        WHERE
            similarity(LOWER(title), :q) > 0.1
            OR similarity(LOWER(description), :q) > 0.1
            OR similarity(LOWER(category), :q) > 0.1
        ORDER BY score DESC
        LIMIT :limit
    """

    try:
        rows = db.execute(sa_text(sql), {"q": cleaned_query, "limit": limit}).fetchall()
        print(f"Fuzzy returned {len(rows)} rows")
    except Exception as e:
        print("Fallback fuzzy query failed:", e)
        db.rollback()
        return []

    return [
        {
            "image_url": r[0],
            "title": r[1],
            "description": r[2],
            "category": r[3],
            "project_url": r[4],
        }
        for r in rows
    ]


def semantic_portfolio_search(query: str, db: Session, limit: int = 3) -> List[Dict[str, Any]]:
    print("\nRunning semantic portfolio search")

    try:
        print(f"Query text: {query}")
        embedding_list = get_query_embedding(query)

        if not embedding_list:
            raise ValueError("Embedding unavailable")

        embedding_str = "[" + ",".join(map(str, embedding_list)) + "]"
        print(f"Embedding vector prepared (length {len(embedding_list)})")

        sql = """
            SELECT
                image_url,
                title,
                description,
                category,
                project_url,
                (
                    0.50 * (1 - (embedding <-> :embedding)) +
                    0.30 * similarity(LOWER(title), :query) +
                    0.15 * similarity(LOWER(description), :query) +
                    0.05 * CASE WHEN LOWER(category) = LOWER(:query) THEN 1 ELSE 0 END
                ) AS score
            FROM portfolio_items
            WHERE embedding IS NOT NULL
            ORDER BY score DESC
            LIMIT :limit
        """

        print("Executing semantic search SQL...")
        rows = db.execute(
            sa_text(sql),
            {"embedding": embedding_str, "query": query.lower(), "limit": limit},
        ).fetchall()

        projects = [
            {
                "image_url": r[0],
                "title": r[1],
                "description": r[2],
                "category": r[3],
                "project_url": r[4],
            }
            for r in rows
        ]

        print(f"Semantic search returned {len(projects)} projects")

        if projects:
            return projects

        print("No semantic results → switching to fuzzy fallback")

    except Exception as e:
        print("Semantic search error:", e)
        db.rollback()

    return _keyword_fallback_search(query, db, limit)
