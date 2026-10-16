import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user_context
from backend.app.security.auth import AuthenticatedContext
from backend.app.models.user import UserRole
from backend.app.models.ticket import SupportTicket, TicketStatus, TicketPriority, Conversation, ConversationMessage
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.models.tool_execution import ToolExecution
from backend.app.models.approval import ApprovalRequest
from backend.app.schemas.ticket import TicketCreate, TicketResponse, TicketDetailResponse, MessageResponse
from backend.app.services import ticket_service

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    limit: int = 50,
    offset: int = 0,
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    # If role is customer, restrict to customer's own tickets
    customer_id = ctx.customer_id if ctx.role == UserRole.CUSTOMER else None

    tickets = ticket_service.list_support_tickets(
        db=db,
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        status_filter=status_filter,
        limit=limit,
        offset=offset
    )
    return tickets


@router.post("", response_model=TicketResponse)
def create_ticket(
    req: TicketCreate,
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    customer_id = ctx.customer_id or ctx.user_id
    try:
        prio = TicketPriority[req.priority.upper()]
    except Exception:
        prio = TicketPriority.MEDIUM

    ticket = ticket_service.create_support_ticket(
        db=db,
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        title=req.title,
        description=req.description,
        category=req.category,
        priority=prio,
        order_id=req.order_id
    )
    return ticket


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket_details(
    ticket_id: str,
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    ticket = ticket_service.get_support_ticket(db, ctx.tenant_id, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")

    if ctx.role == UserRole.CUSTOMER and ticket.customer_id != ctx.customer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot access other customers' tickets.")

    # Customer info
    cust = db.query(Customer).filter(Customer.id == ticket.customer_id).first()

    # Associated order details
    order_details = None
    if ticket.order_id:
        order = db.query(Order).filter(Order.id == ticket.order_id).first()
        if order:
            try:
                items = json.loads(order.items_json) if order.items_json else []
            except Exception:
                items = []
            order_details = {
                "id": order.id,
                "order_number": order.order_number,
                "status": order.status.value,
                "total_amount": order.total_amount,
                "refunded_amount": order.refunded_amount,
                "tracking_number": order.tracking_number,
                "carrier": order.carrier,
                "items": items,
            }

    # Fetch conversation messages
    conv = db.query(Conversation).filter(Conversation.ticket_id == ticket.id).first()
    message_responses = []
    if conv:
        raw_msgs = db.query(ConversationMessage).filter(ConversationMessage.conversation_id == conv.id).order_by(ConversationMessage.created_at.asc()).all()
        for m in raw_msgs:
            try:
                meta = json.loads(m.metadata_json) if m.metadata_json else {}
            except Exception:
                meta = {}
            message_responses.append(
                MessageResponse(
                    id=m.id,
                    sender_type=m.sender_type,
                    content=m.content,
                    metadata=meta,
                    created_at=m.created_at,
                )
            )

    # Fetch tool executions for this ticket
    tool_execs = (
        db.query(ToolExecution)
        .filter(ToolExecution.tenant_id == ctx.tenant_id, ToolExecution.ticket_id == ticket.id)
        .order_by(ToolExecution.created_at.asc())
        .all()
    )
    tool_exec_data = [
        {
            "id": te.id,
            "tool_name": te.tool_name,
            "input_args": json.loads(te.input_args) if te.input_args else {},
            "output_result": json.loads(te.output_result) if te.output_result else {},
            "status": te.status,
            "duration_ms": te.execution_duration_ms,
            "error": te.error_message,
            "created_at": te.created_at.isoformat(),
        }
        for te in tool_execs
    ]

    # Fetch approvals
    approvals = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.tenant_id == ctx.tenant_id, ApprovalRequest.ticket_id == ticket.id)
        .all()
    )
    approval_data = [
        {
            "id": a.id,
            "action_type": a.action_type.value,
            "amount": a.requested_amount,
            "status": a.status.value,
            "reason": a.reason,
            "reviewed_by": a.reviewed_by,
            "review_notes": a.review_notes,
            "created_at": a.created_at.isoformat(),
        }
        for a in approvals
    ]

    return TicketDetailResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        customer_id=ticket.customer_id,
        order_id=ticket.order_id,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status.value,
        priority=ticket.priority.value,
        category=ticket.category,
        resolution_summary=ticket.resolution_summary,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        customer_name=cust.name if cust else None,
        customer_email=cust.email if cust else None,
        order_details=order_details,
        messages=message_responses,
        tool_executions=tool_exec_data,
        approvals=approval_data,
    )
