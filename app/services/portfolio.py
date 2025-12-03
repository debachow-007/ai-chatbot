from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text as sa_text

from app.services.embeddings import get_query_embedding


def _keyword_fallback_search(query: str, db: Session, limit: int) -> List[Dict[str, Any]]:
    words = [w.strip() for w in query.lower().split() if w.strip()]
    if not words:
        return []

    patterns = [f"%{w}%" for w in words]

    sql = """
        SELECT
            image_url,
            title,
            description,
            category,
            project_url
        FROM portfolio_items
        WHERE
            (
                LOWER(title) ILIKE ANY(:patterns)
                OR LOWER(description) ILIKE ANY(:patterns)
                OR LOWER(category) ILIKE ANY(:patterns)
                OR EXISTS (
                    SELECT 1 FROM unnest(tags) t
                    WHERE LOWER(t) ILIKE ANY(:patterns)
                )
            )
        LIMIT :limit
    """

    rows = db.execute(
        sa_text(sql),
        {"patterns": patterns, "limit": limit},
    ).fetchall()

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


def semantic_portfolio_search(query: str, db: Session, limit: int = 6) -> List[Dict[str, Any]]:
    print("Running semantic portfolio search")
    try:
        embedding_list = get_query_embedding(query)
        if not embedding_list:
            raise ValueError("Empty embedding")

        embedding_str = "[" + ",".join(map(str, embedding_list)) + "]"

        # hybrid score: semantic + fuzzy + category
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

        if projects:
            return projects

        print("ℹNo semantic matches, falling back to keyword search.")

    except Exception as e:
        print("Semantic search error → switching to keyword fallback:", e)
        db.rollback()

    print("Fallback to keyword search")
    try:
        return _keyword_fallback_search(query, db, limit)
    except Exception as e:
        print("Fallback search failed:", e)
        db.rollback()
        return []
