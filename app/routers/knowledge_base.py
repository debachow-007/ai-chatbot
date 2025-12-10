from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.schemas import KnowledgeBaseCreate, KnowledgeBaseItem
from app.services.knowledge_base import add_kb_item, get_all_kb_items


router = APIRouter(prefix="/kb", tags=["kb"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=KnowledgeBaseItem)
def create_kb_item(data: KnowledgeBaseCreate, db: Session = Depends(get_db)):
    return add_kb_item(data.question, data.answer, db)


@router.get("/", response_model=list[KnowledgeBaseItem])
def list_kb_items(db: Session = Depends(get_db)):
    return get_all_kb_items(db)
