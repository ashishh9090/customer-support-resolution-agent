from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user_context, require_roles
from backend.app.security.auth import AuthenticatedContext
from backend.app.models.user import UserRole
from backend.app.models.approval import ApprovalRequest, ApprovalStatus
from backend.app.models.order import Order
from backend.app.schemas.approval import ApprovalResponse, ApprovalDecisionRequest
from backend.app.tools.support_tools import tool_approve_or_reject_action

router = APIRouter(prefix="/approvals", tags=["Human Approvals"])


@router.get("", response_model=List[ApprovalResponse])
def list_approvals(
    status_filter: Optional[ApprovalStatus] = Query(None, alias="status"),
    ctx: AuthenticatedContext = Depends(require_roles([UserRole.SUPPORT_AGENT, UserRole.APPROVER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    query = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == ctx.tenant_id)
    if status_filter:
        query = query.filter(ApprovalRequest.status == status_filter)

    approvals = query.order_by(ApprovalRequest.created_at.desc()).all()
    results = []
    for a in approvals:
        order = db.query(Order).filter(Order.id == a.order_id).first() if a.order_id else None
        results.append(
            ApprovalResponse(
                id=a.id,
                ticket_id=a.ticket_id,
                order_id=a.order_id,
                order_number=order.order_number if order else None,
                customer_id=a.customer_id,
                requested_by=a.requested_by,
                action_type=a.action_type.value,
                requested_amount=a.requested_amount,
                currency=a.currency,
                reason=a.reason,
                status=a.status.value,
                reviewed_by=a.reviewed_by,
                review_notes=a.review_notes,
                idempotency_key=a.idempotency_key,
                created_at=a.created_at,
                resolved_at=a.resolved_at,
            )
        )
    return results


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
def decide_approval(
    approval_id: str,
    req: ApprovalDecisionRequest,
    ctx: AuthenticatedContext = Depends(require_roles([UserRole.APPROVER, UserRole.ADMIN, UserRole.SUPPORT_AGENT])),
    db: Session = Depends(get_db)
):
    # Retrieve approval
    approval = db.query(ApprovalRequest).filter(
        ApprovalRequest.tenant_id == ctx.tenant_id,
        ApprovalRequest.id == approval_id
    ).first()

    if not approval:
        raise HTTPException(status_code=404, detail=f"Approval request '{approval_id}' not found.")

    # Prevent self-approval if requested by the same user
    if approval.requested_by == ctx.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conflict of interest: Requesters cannot approve their own approval requests."
        )

    # Execute tool
    res = tool_approve_or_reject_action(
        db=db,
        tenant_id=ctx.tenant_id,
        approval_id=approval_id,
        decision=req.decision,
        reviewer_id=ctx.user_id,
        review_notes=req.review_notes
    )

    if not res.success:
        raise HTTPException(status_code=400, detail=res.error)

    # Refresh
    db.refresh(approval)
    order = db.query(Order).filter(Order.id == approval.order_id).first() if approval.order_id else None

    return ApprovalResponse(
        id=approval.id,
        ticket_id=approval.ticket_id,
        order_id=approval.order_id,
        order_number=order.order_number if order else None,
        customer_id=approval.customer_id,
        requested_by=approval.requested_by,
        action_type=approval.action_type.value,
        requested_amount=approval.requested_amount,
        currency=approval.currency,
        reason=approval.reason,
        status=approval.status.value,
        reviewed_by=approval.reviewed_by,
        review_notes=approval.review_notes,
        idempotency_key=approval.idempotency_key,
        created_at=approval.created_at,
        resolved_at=approval.resolved_at,
    )
