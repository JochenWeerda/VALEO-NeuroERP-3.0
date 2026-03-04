"""
KI Usability API Configuration
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """KI Usability service settings"""

    HOST: str = "0.0.0.0"
    PORT: int = 5200
    DEBUG: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://frontend-web:3000",
        "http://backend:8000",
    ]

    # Optional: AI service for NLU fallback
    AI_SERVICE_URL: str = "http://ai:5000"
    AI_SERVICE_ENABLED: bool = False

    class Config:
        env_prefix = "KI_USABILITY_"
        case_sensitive = True
        env_file = ".env"


settings = Settings()
