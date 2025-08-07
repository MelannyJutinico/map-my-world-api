"""
Database session management module.

Defines the SQLAlchemy engine, base class for models, and a dependency
provider for generating and closing database sessions in request handlers.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///./mapmyworld.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    Dependency function that yields a database session and ensures closure.

    Use this in FastAPI endpoints via:
        db: Session = Depends(get_db)

    :yield: Active SQLAlchemy Session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
