from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.db.session import get_db
from backend.app.config import settings
from backend.app.retrieval.indexer import global_vector_store

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = False

    return {
        "ready": db_ok,
        "database": "connected" if db_ok else "disconnected",
        "knowledge_base_chunks": len(global_vector_store.chunks),
        "llm_provider": settings.LLM_PROVIDER,
    }
