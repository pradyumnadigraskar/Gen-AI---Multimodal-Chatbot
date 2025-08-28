# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 120
    JWT_SECURE_COOKIE: bool = False
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "chat_history"
    QDRANT_VECTOR_DIM: int = 1024

    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_TEXT_MODEL: str = "mistral:latest"
    OLLAMA_VISION_MODEL: str = "llava:latest"

    USE_LOCAL_EMBEDDINGS: bool = True
    SENTENCE_EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    A1111_URL: str = "http://127.0.0.1:7860"

    # Piper / TTS (leave empty here; set in .env)
    PIPER_EXE: str | None = None
    PIPER_VOICE: str | None = None
    PIPER_VOICE_CONFIG: str | None = None
    PIPER_ESPEAK_DATA: str | None = None
    TTS_OUTPUT_FORMAT: str = "mp3"   # "wav" or "mp3"
    FFMPEG_EXE: str | None = None

    ENABLE_SVD: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
