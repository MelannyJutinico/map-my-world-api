"""
Entry point for the Map My World API application.

This module initializes the FastAPI app, configures middleware,
registers routers under a consistent versioned prefix, and
handles startup tasks like database migrations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import engine
from app.core.models.database import Base
from app.api.v1.endpoints import (
    locations,
    categories,
    recommendations,
    reviews
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_prefix = "/api/v1"
app.include_router(locations.router, prefix=f"{api_v1_prefix}/locations")
app.include_router(categories.router, prefix=f"{api_v1_prefix}/categories")
app.include_router(recommendations.router, prefix=f"{api_v1_prefix}/recommendations")
app.include_router(reviews.router, prefix=f"{api_v1_prefix}/reviews")


@app.get("/health", summary="Health check endpoint")
def health_check():
    """
    Simple endpoint to verify that the application is running.

    :return: A JSON object with service status.
    """
    return {"status": "ok"}
