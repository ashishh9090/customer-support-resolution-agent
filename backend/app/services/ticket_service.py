import uuid
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.ticket import (
    SupportTicket,
    TicketStatus,
    TicketPriority,
    Conversation,
    ConversationMessage,
)
from backend.app.services.audit_service import log_audit_event


def create_support_ticket(
    db: Session,
    tenant_id: str,
    customer_id: str,
    title: str,
    description: str,
    category: str = "general",
    priority: TicketPriority = TicketPriority.MEDIUM,
    order_id: Optional[str] = None
) -> SupportTicket:
    ticket_count = db.query(SupportTicket).filter(SupportTicket.tenant_id == tenant_id).count()
    ticket_number = f"TCK-{ticket_count + 1001}"

    ticket = SupportTicket(
        id=f"tck-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        customer_id=customer_id,
        order_id=order_id,
        ticket_number=ticket_number,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Automatically create an associated conversation
    conv = Conversation(
        id=f"conv-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        ticket_id=ticket.id,
        customer_id=customer_id,
        channel="web_chat",
    )
    db.add(conv)
    db.commit()

    log_audit_event(
        db=db,
        tenant_id=tenant_id,
        event_type="TICKET_CREATED",
        resource_type="SupportTicket",
        resource_id=ticket.id,
        action="CREATE",
        details={"ticket_number": ticket_number, "title": title, "category": category},
        user_id=customer_id
    )

    return ticket


def get_support_ticket(
    db: Session,
    tenant_id: str,
    ticket_id_or_number: str
) -> Optional[SupportTicket]:
    return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.tenant_id == tenant_id,
            (SupportTicket.id == ticket_id_or_number) | (SupportTicket.ticket_number == ticket_id_or_number)
        )
        .first()
    )


def list_support_tickets(
    db: Session,
    tenant_id: str,
    customer_id: Optional[str] = None,
    status_filter: Optional[TicketStatus] = None,
    limit: int = 50,
    offset: int = 0
) -> List[SupportTicket]:
    query = db.query(SupportTicket).filter(SupportTicket.tenant_id == tenant_id)
    if customer_id:
        query = query.filter(SupportTicket.customer_id == customer_id)
    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    
    return query.order_by(SupportTicket.created_at.desc()).offset(offset).limit(limit).all()


def update_ticket_status(
    db: Session,
    tenant_id: str,
    ticket_id: str,
    status: TicketStatus,
    resolution_summary: Optional[str] = None
) -> Optional[SupportTicket]:
    ticket = get_support_ticket(db, tenant_id, ticket_id)
    if not ticket:
        return None

    ticket.status = status
    if resolution_summary:
        ticket.resolution_summary = resolution_summary

    db.commit()
    db.refresh(ticket)
    return ticket


def get_or_create_conversation(
    db: Session,
    tenant_id: str,
    customer_id: str,
    ticket_id: Optional[str] = None
) -> Conversation:
    query = db.query(Conversation).filter(
        Conversation.tenant_id == tenant_id,
        Conversation.customer_id == customer_id
    )
    if ticket_id:
        query = query.filter(Conversation.ticket_id == ticket_id)
    
    conv = query.order_by(Conversation.created_at.desc()).first()
    if not conv:
        conv = Conversation(
            id=f"conv-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            ticket_id=ticket_id,
            customer_id=customer_id,
            channel="web_chat"
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    return conv


def add_message_to_conversation(
    db: Session,
    conversation_id: str,
    sender_type: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ConversationMessage:
    msg = ConversationMessage(
        id=f"msg-{uuid.uuid4().hex[:12]}",
        conversation_id=conversation_id,
        sender_type=sender_type,
        content=content,
        metadata_json=json.dumps(metadata or {}, default=str),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
