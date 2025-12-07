from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Card Collection Tracker"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./cards.db"  # Start with SQLite, can upgrade to PostgreSQL later

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    @property
    def UPLOAD_DIR(self) -> str:
        """Get absolute path to upload directory"""
        base = Path(__file__).parent.parent.parent  # backend/
        return str((base / "uploads").resolve())

    # Image Processing Settings
    MAX_IMAGE_DIMENSION: int = 1024
    IMAGE_QUALITY: int = 85
    ALLOWED_IMAGE_FORMATS: List[str] = [
        'image/jpeg', 'image/jpg', 'image/png',
        'image/webp', 'image/heic', 'image/heif'
    ]

    # AI/ML Settings (add API keys here later)
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
