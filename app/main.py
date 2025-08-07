from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Map My World API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}