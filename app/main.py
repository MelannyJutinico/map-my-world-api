from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import locations
from app.db.session import engine
from app.core.models.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0"
)


app.include_router(locations.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to Map My World API!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}