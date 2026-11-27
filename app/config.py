import os
from pathlib import Path

# Load .env file with native fallback if python-dotenv is not yet installed
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env"

try:
    from dotenv import load_dotenv
    load_dotenv(env_file)
except ImportError:
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        k, v = stripped.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Dastawez.ai - DocuMind")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dastawez-super-secret-key-change-in-production-2024")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'documind.db'}")
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "yes")
    
    # Vector DB
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: str = os.getenv("QDRANT_PORT", "6333")
    QDRANT_URL: str = os.getenv("QDRANT_URL", f"http://{QDRANT_HOST}:{QDRANT_PORT}")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    # OpenAI & LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # File Uploads
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024))) # 50 MB
    UPLOAD_FOLDER: Path = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
    ALLOWED_EXTENSIONS: set = set(
        ext.strip().lower().lstrip(".") for ext in os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,txt,md,markdown,rtf").split(",") if ext.strip()
    ) or {"pdf", "docx", "txt", "md", "markdown", "rtf"}
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() in ("true", "1", "yes")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "300"))

    # CORS
    CORS_ORIGINS: list = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:3000,http://localhost:8000"
        ).split(",") if origin.strip()
    ]

    # Host Validation
    ALLOWED_HOSTS: list = [
        host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()
    ] or ["*"]
    
    # Static & Upload folder ensure
    def __init__(self):
        try:
            self.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
            (BASE_DIR / "app" / "static").mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

settings = Settings()
