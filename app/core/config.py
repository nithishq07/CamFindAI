from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "CamFindAI"
    VERSION: str = "0.1.0"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str = "camfindai"
    POSTGRES_PASSWORD: str = "password123"
    POSTGRES_DB: str = "camfindai_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
    
    # ReID
    REID_THRESHOLD: float = 0.72
    
    # Alert Rules
    LOITERING_THRESHOLD_SEC: int = 60
    
    # Model device
    DEVICE: Optional[str] = None # can be "cuda", "mps", "cpu"
    
    # Security
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
