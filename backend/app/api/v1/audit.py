import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import require_roles
from backend.app.security.auth import AuthenticatedContext
from backend.app.models.user import UserRole
from backend.app.models.audit import AuditEvent
from backend.app.schemas.analytics import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["Audit Events"])


@router.get("", response_model=List[AuditEventResponse])
def get_audit_trail(
    event_type: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    limit: int = 100,
    offset: int = 0,
    ctx: AuthenticatedContext = Depends(require_roles([UserRole.SUPPORT_AGENT, UserRole.APPROVER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent).filter(AuditEvent.tenant_id == ctx.tenant_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    if resource_type:
        query = query.filter(AuditEvent.resource_type == resource_type)
    if resource_id:
        query = query.filter(AuditEvent.resource_id == resource_id)

    events = query.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit).all()
    results = []
    for e in events:
        try:
            details = json.loads(e.details_json) if e.details_json else {}
        except Exception:
            details = {}
        results.append(
            AuditEventResponse(
                id=e.id,
                tenant_id=e.tenant_id,
                user_id=e.user_id,
                event_type=e.event_type,
                resource_type=e.resource_type,
                resource_id=e.resource_id,
                action=e.action,
                details=details,
                ip_address=e.ip_address,
                created_at=e.created_at,
            )
        )
    return results
