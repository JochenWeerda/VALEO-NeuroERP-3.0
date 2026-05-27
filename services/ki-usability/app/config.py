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

    # Slice-013: Local voice polish (Ollama) + faster-whisper STT
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_POLISH_MODEL: str = "mistral"
    OLLAMA_TIMEOUT_SEC: float = 60.0
    VOICE_POLISH_ENABLED: bool = True
    FASTER_WHISPER_MODEL: str = "small"
    FASTER_WHISPER_DEVICE: str = "cpu"
    FASTER_WHISPER_COMPUTE: str = "int8"

    class Config:
        env_prefix = "KI_USABILITY_"
        case_sensitive = True
        env_file = ".env"


settings = Settings()
