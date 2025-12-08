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

    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    AWS_KEY: str = os.getenv("AWS_KEY", "")
    AWS_SECRET: str = os.getenv("AWS_SECRET", "")
    AWS_BUCKET: str = os.getenv("AWS_BUCKET", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # Service account path
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not GOOGLE_APPLICATION_CREDENTIALS:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS environment variable is required.")



settings = Settings()
