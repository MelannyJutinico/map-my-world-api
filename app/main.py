from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import locations, categories,recommendations,reviews
from app.db.session import engine
from app.core.models.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0"
)


app.include_router(locations.router, prefix="/api/v1/locations")
app.include_router(categories.router, prefix="/api/v1/categories")
app.include_router(recommendations.router, prefix="/api/v1/recommendations")
app.include_router(reviews.router, prefix="/api/v1/reviews")


@app.get("/health")
def health_check():
    return {"status": "ok"}