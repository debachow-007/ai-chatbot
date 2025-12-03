import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    PROJECT_ID: str = os.getenv("PROJECT_ID", "vibesai-2025")
    LOCATION: str = os.getenv("LOCATION", "us-central1")

    # Models
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-005")

    # DB
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:admin123@localhost:5432/ai_chatbot",
    )

    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Service account path
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "vertex-key.json"
    )


settings = Settings()
