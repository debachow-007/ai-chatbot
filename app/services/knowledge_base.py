from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models import KnowledgeBase
from app.services.embeddings import embed_text


def add_kb_item(question: str, answer: str, db: Session):
    embedding = embed_text(question)

    item = KnowledgeBase(
        question=question,
        answer=answer,
        embedding=embedding
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_all_kb_items(db: Session):
    return db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()


def kb_exact_match(user_message: str, db: Session):
    """Case-insensitive exact match"""
    item = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.question.ilike(user_message.strip()))
        .first()
    )
    return item.answer if item else None

def to_pgvector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{v}" for v in vec) + "]"

def kb_semantic_match(user_message: str, db: Session, threshold: float = 0.78):
    """Vector similarity search"""

    user_emb = embed_text(user_message)
    emb_literal = "[" + ",".join(str(v) for v in user_emb) + "]"  # pgvector literal

    query = text("""
        SELECT id, answer, (embedding <-> CAST(:query_embedding AS vector)) AS distance
        FROM knowledge_base
        ORDER BY embedding <-> CAST(:query_embedding AS vector)
        LIMIT 1;
    """)

    result = db.execute(
        query,
        {"query_embedding": emb_literal}
    ).fetchone()

    if not result:
        return None

    kb_id, kb_answer, distance = result

    if distance > threshold:
        return None

    return kb_answer
