from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID] = None


class PortfolioProject(BaseModel):
    image_url: str
    title: str
    description: str
    category: str
    project_url: str


class ChatResponse(BaseModel):
    session_id: UUID
    reply: str
    suggested_questions: List[str]
    images: List[str] = []
    response_type: str = "text"
    intent: str = "other"
    projects: List[PortfolioProject] = []
