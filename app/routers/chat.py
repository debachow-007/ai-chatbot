# app/routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app import models
from app.schemas import ChatRequest, ChatResponse
from app.services.rag import search_relevant_chunks, build_context
from app.services.gemini_chat import generate_answer
from app.services.intent import detect_intent
from app.services.suggestions import generate_suggested_questions
from app.services.portfolio import semantic_portfolio_search
from app.services.behavior import decide_behavior

router = APIRouter(prefix="/chat", tags=["chat"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def build_chat_history(session: models.ChatSession) -> list[dict]:
    return [
        {"role": msg.role, "content": msg.content}
        for msg in sorted(session.messages, key=lambda m: m.created_at)
        if msg.role in ("user", "assistant")
    ]


@router.post("/", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):

    # Create or fetch chat session
    session = db.query(models.ChatSession).get(req.session_id) if req.session_id else None
    if session is None:
        session = models.ChatSession()
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    db.add(models.ChatMessage(session_id=session.id, role="user", content=req.message))
    db.commit()

    # Build history
    history = build_chat_history(session)

    # Knowledge RAG
    chunks = search_relevant_chunks(req.message, top_k=5, db=db)
    context = build_context(chunks) if chunks else ""

    # Detect intent
    intent = detect_intent(req.message)
    print(f"Detected intent: {intent}")

    # Generate reply
    try:
        reply_text = generate_answer(
            user_message=req.message,
            context=context,
            chat_history=history,
        )
    except Exception as e:
        print("Generate_answer error:", e)
        reply_text = "I'm having trouble answering right now. Could you rephrase that?"

    # Save assistant message
    db.add(models.ChatMessage(session_id=session.id, role="assistant", content=reply_text))
    db.commit()

    # Portfolio search if relevant
    projects = []
    try:
        if intent in ("portfolio"):
            print("Running portfolio search")
            projects = semantic_portfolio_search(req.message, db, limit=6)
    except Exception as e:
        print("Portfolio search error:", e)
        db.rollback()  # Make sure DB is safe
        projects = []

    images = [p["image_url"] for p in projects]
    has_projects = len(projects) > 0

    # Decide frontend rendering mode
    response_type = "portfolio" if intent == "portfolio" and has_projects else decide_behavior(intent, has_projects)

    # Suggested question generation
    suggested_questions = generate_suggested_questions(
        user_message=req.message,
        last_answer=reply_text,
        intent=intent,
    )

    return ChatResponse(
        session_id=session.id,
        reply=reply_text,
        intent=intent,
        response_type=response_type,
        suggested_questions=suggested_questions or [],
        images=images or [],
        projects=projects or [],
    )
