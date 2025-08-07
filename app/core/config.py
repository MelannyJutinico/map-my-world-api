from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Map My World API"
    OPENCAGE_API_KEY : str
    class Config:
        env_file = ".env"


settings = Settings()