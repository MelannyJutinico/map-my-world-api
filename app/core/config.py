from pydantic_settings import BaseSettings
# app/core/config.py

from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Map My World"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./mapmyworld.db"
    OPENCAGE_API_KEY : str

    # Aquí defines los orígenes permitidos para CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "https://mapmyworld.example.com"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
