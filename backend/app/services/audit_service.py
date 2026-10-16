import uuid
import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditEvent


def log_audit_event(
    db: Session,
    tenant_id: str,
    event_type: str,
    resource_type: str,
    resource_id: str,
    action: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditEvent:
    event = AuditEvent(
        id=f"audit-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        details_json=json.dumps(details, default=str),
        ip_address=ip_address,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
