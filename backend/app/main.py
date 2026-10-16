import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.app.config import settings
from backend.app.db.session import init_db, SessionLocal
from backend.app.retrieval.indexer import build_knowledge_index
from backend.app.api.v1 import api_v1_router
from scripts.seed_database import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and knowledge base is indexed
    init_db()
    build_knowledge_index()
    
    # Auto-seed if database is empty
    db = SessionLocal()
    try:
        from backend.app.models.tenant import Tenant
        count = db.query(Tenant).count()
        if count == 0:
            print("Auto-seeding initial database with tenants, orders, and users...")
            seed_all(db)
    finally:
        db.close()
        
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Style AI Customer Support Resolution Agent with LangGraph Orchestration, Human Approval, RAG, and Multi-Tenancy.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Consistent error handling
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "path": request.url.path,
        },
    )


# Mount API V1
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "AI Customer Support Resolution Agent API is online",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "health_url": f"{settings.API_V1_STR}/health",
    }
