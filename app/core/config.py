from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Map My World API"
  
    class Config:
        env_file = ".env"


settings = Settings()