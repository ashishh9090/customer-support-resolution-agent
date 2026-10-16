from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.chat import router as chat_router
from backend.app.api.v1.tickets import router as tickets_router
from backend.app.api.v1.orders import router as orders_router
from backend.app.api.v1.approvals import router as approvals_router
from backend.app.api.v1.audit import router as audit_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(tickets_router)
api_v1_router.include_router(orders_router)
api_v1_router.include_router(approvals_router)
api_v1_router.include_router(audit_router)
api_v1_router.include_router(analytics_router)
