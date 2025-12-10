from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import Base, engine
from app.routers import chat, knowledge_base
from app.admin.admin_router import admin_router
from app.admin.auth_router import auth_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vibes AI Chatbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(knowledge_base.router)

app.mount("/static", StaticFiles(directory="app/admin/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}
