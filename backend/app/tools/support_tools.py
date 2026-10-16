import time
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.tools.base import ToolResult, record_tool_execution
from backend.app.services import customer_service, order_service, payment_service, refund_service, ticket_service, audit_service
from backend.app.retrieval.rag import query_knowledge_base
from backend.app.models.approval import ApprovalAction, ApprovalStatus
from backend.app.models.ticket import TicketStatus, TicketPriority


# 1. get_customer
class GetCustomerInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer ID")


def tool_get_customer(db: Session, tenant_id: str, customer_id: str, ticket_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    cust = customer_service.get_customer(db, tenant_id=tenant_id, customer_id=customer_id)
    duration = (time.perf_counter() - start) * 1000

    if not cust:
        res = ToolResult(success=False, error=f"Customer '{customer_id}' not found in tenant '{tenant_id}'.", execution_duration_ms=duration)
    else:
        res = ToolResult(
            success=True,
            data={
                "id": cust.id,
                "name": cust.name,
                "email": cust.email,
                "phone": cust.phone,
                "account_tier": cust.account_tier,
                "tenant_id": cust.tenant_id,
            },
            execution_duration_ms=duration,
        )
    record_tool_execution(db, tenant_id, "get_customer", {"customer_id": customer_id}, res, ticket_id)
    return res


# 2. get_order
class GetOrderInput(BaseModel):
    order_id: str = Field(..., description="Order ID or Order Number")
    customer_id: Optional[str] = Field(None, description="Customer ID to verify ownership")


def tool_get_order(db: Session, tenant_id: str, order_id: str, customer_id: Optional[str] = None, ticket_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    res_dict = order_service.get_order_by_id_or_number(db, tenant_id, order_id, customer_id)
    duration = (time.perf_counter() - start) * 1000

    if not res_dict["found"]:
        res = ToolResult(success=False, error=res_dict["error"], execution_duration_ms=duration)
    else:
        order = res_dict["order"]
        try:
            items = json.loads(order.items_json) if order.items_json else []
        except Exception:
            items = []
        res = ToolResult(
            success=True,
            data={
                "id": order.id,
                "order_number": order.order_number,
                "customer_id": order.customer_id,
                "status": order.status.value,
                "total_amount": order.total_amount,
                "refunded_amount": order.refunded_amount,
                "currency": order.currency,
                "carrier": order.carrier,
                "tracking_number": order.tracking_number,
                "shipping_address": order.shipping_address,
                "placed_at": order.placed_at.isoformat() if order.placed_at else None,
                "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                "items": items,
            },
            execution_duration_ms=duration,
        )
    record_tool_execution(db, tenant_id, "get_order", {"order_id": order_id, "customer_id": customer_id}, res, ticket_id)
    return res


# 3. get_payment_status
def tool_get_payment_status(db: Session, tenant_id: str, order_id: str, customer_id: Optional[str] = None, ticket_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    res_dict = payment_service.get_payment_for_order(db, tenant_id, order_id, customer_id)
    duration = (time.perf_counter() - start) * 1000

    if not res_dict["found"]:
        res = ToolResult(success=False, error=res_dict["error"], execution_duration_ms=duration)
    else:
        payment = res_dict["payment"]
        order = res_dict["order"]
        res = ToolResult(
            success=True,
            data={
                "payment_id": payment.id,
                "order_number": order.order_number,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status.value,
                "payment_method": payment.payment_method,
                "card_last4": payment.card_last4,
                "failure_reason": payment.failure_reason,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
            },
            execution_duration_ms=duration,
        )
    record_tool_execution(db, tenant_id, "get_payment_status", {"order_id": order_id, "customer_id": customer_id}, res, ticket_id)
    return res


# 4. check_refund_eligibility
def tool_check_refund_eligibility(db: Session, tenant_id: str, order_id: str, customer_id: str, reason: str = "customer_request", ticket_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    eligibility = refund_service.check_refund_eligibility(db, tenant_id, order_id, customer_id, reason)
    duration = (time.perf_counter() - start) * 1000

    res = ToolResult(
        success=eligibility["eligible"],
        data=eligibility,
        error=None if eligibility["eligible"] else eligibility.get("reason"),
        execution_duration_ms=duration,
    )
    record_tool_execution(db, tenant_id, "check_refund_eligibility", {"order_id": order_id, "customer_id": customer_id, "reason": reason}, res, ticket_id)
    return res


# 5. calculate_refund_amount
def tool_calculate_refund_amount(db: Session, tenant_id: str, order_id: str, customer_id: str, return_type: str = "full", deduct_shipping: bool = False, ticket_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    calc = refund_service.calculate_refund_amount(db, tenant_id, order_id, customer_id, return_type, deduct_shipping)
    duration = (time.perf_counter() - start) * 1000

    res = ToolResult(
        success=calc["success"],
        data=calc,
        error=None if calc["success"] else calc.get("reason"),
        execution_duration_ms=duration,
    )
    record_tool_execution(db, tenant_id, "calculate_refund_amount", {"order_id": order_id, "customer_id": customer_id, "return_type": return_type}, res, ticket_id)
    return res


# 6. create_support_ticket
def tool_create_support_ticket(db: Session, tenant_id: str, customer_id: str, title: str, description: str, category: str = "general", priority: str = "MEDIUM", order_id: Optional[str] = None) -> ToolResult:
    start = time.perf_counter()
    try:
        prio = TicketPriority[priority.upper()]
    except Exception:
        prio = TicketPriority.MEDIUM

    ticket = ticket_service.create_support_ticket(
        db, tenant_id=tenant_id, customer_id=customer_id, title=title, description=description, category=category, priority=prio, order_id=order_id
    )
    duration = (time.perf_counter() - start) * 1000

    res = ToolResult(
        success=True,
        data={
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "title": ticket.title,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "category": ticket.category,
        },
        execution_duration_ms=duration,
    )
    record_tool_execution(db, tenant_id, "create_support_ticket", {"customer_id": customer_id, "title": title, "category": category}, res, ticket.id)
    return res


# 7. get_support_ticket
def tool_get_support_ticket(db: Session, tenant_id: str, ticket_id: str) -> ToolResult:
    start = time.perf_counter()
    ticket = ticket_service.get_support_ticket(db, tenant_id=tenant_id, ticket_id_or_number=ticket_id)
    duration = (time.perf_counter() - start) * 1000

    if not ticket:
        res = ToolResult(success=False, error=f"Ticket '{ticket_id}' not found in tenant '{tenant_id}'.", execution_duration_ms=duration)
    else:
        res = ToolResult(
            success=True,
            data={
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "customer_id": ticket.customer_id,
                "order_id": ticket.order_id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value,
                "priority": ticket.priority.value,
                "category": ticket.category,
                "resolution_summary": ticket.resolution_summary,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            },
            execution_duration_ms=duration,
        )
    record_tool_execution(db, tenant_id, "get_support_ticket", {"ticket_id": ticket_id}, res, ticket_id)
    return res


# 8. search_knowledge_base
def tool_search_knowledge_base(tenant_id: str, query: str, top_k: int = 3, ticket_id: Optional[str] = None, db: Optional[Session] = None) -> ToolResult:
    start = time.perf_counter()
    results = query_knowledge_base(query=query, tenant_id=tenant_id, top_k=top_k)
    duration = (time.perf_counter() - start) * 1000

    citations = [r["citation"] for r in results]
    res = ToolResult(
        success=len(results) > 0,
        data={
            "query": query,
            "count": len(results),
            "citations": citations,
            "results": results,
        },
        error=None if results else "No matching policy or knowledge base document found.",
        execution_duration_ms=duration,
    )
    if db:
        record_tool_execution(db, tenant_id, "search_knowledge_base", {"query": query, "top_k": top_k}, res, ticket_id)
    return res


# 9. request_human_approval
def tool_request_human_approval(
    db: Session,
    tenant_id: str,
    ticket_id: str,
    customer_id: str,
    order_id: str,
    action_type: str,
    amount: float,
    currency: str,
    reason: str,
    requested_by: str = "ai_agent"
) -> ToolResult:
    start = time.perf_counter()
    try:
        act = ApprovalAction[action_type.upper()]
    except Exception:
        act = ApprovalAction.REFUND

    approval = refund_service.create_approval_request(
        db, tenant_id=tenant_id, ticket_id=ticket_id, customer_id=customer_id, order_id=order_id, action_type=act, amount=amount, currency=currency, reason=reason, requested_by=requested_by
    )
    # Update ticket status to WAITING_APPROVAL
    ticket_service.update_ticket_status(db, tenant_id, ticket_id, TicketStatus.WAITING_APPROVAL, f"Waiting for human approval: {reason}")
    duration = (time.perf_counter() - start) * 1000

    res = ToolResult(
        success=True,
        data={
            "approval_id": approval.id,
            "status": approval.status.value,
            "action_type": approval.action_type.value,
            "amount": approval.requested_amount,
            "currency": approval.currency,
            "idempotency_key": approval.idempotency_key,
            "message": f"Approval request created. Workflow paused awaiting review by human supervisor."
        },
        execution_duration_ms=duration,
    )
    record_tool_execution(db, tenant_id, "request_human_approval", {"ticket_id": ticket_id, "amount": amount, "action_type": action_type}, res, ticket_id)
    return res


# 10. approve_or_reject_action
def tool_approve_or_reject_action(
    db: Session,
    tenant_id: str,
    approval_id: str,
    decision: str,  # "APPROVED" or "REJECTED"
    reviewer_id: str,
    review_notes: str = ""
) -> ToolResult:
    start = time.perf_counter()
    if decision.upper() == "APPROVED":
        exec_res = refund_service.execute_approved_refund(db, tenant_id, approval_id, reviewer_id, review_notes)
        duration = (time.perf_counter() - start) * 1000
        res = ToolResult(success=exec_res["success"], data=exec_res, error=exec_res.get("error"), execution_duration_ms=duration)
    else:
        # Rejection
        from backend.app.models.approval import ApprovalRequest
        approval = db.query(ApprovalRequest).filter(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.id == approval_id).first()
        duration = (time.perf_counter() - start) * 1000
        if not approval:
            res = ToolResult(success=False, error=f"Approval request '{approval_id}' not found.", execution_duration_ms=duration)
        else:
            approval.status = ApprovalStatus.REJECTED
            approval.reviewed_by = reviewer_id
            approval.review_notes = review_notes
            if approval.ticket_id:
                ticket_service.update_ticket_status(db, tenant_id, approval.ticket_id, TicketStatus.CLOSED, f"Action rejected by reviewer {reviewer_id}: {review_notes}")
            db.commit()
            audit_service.log_audit_event(
                db, tenant_id, "APPROVAL_REJECTED", "ApprovalRequest", approval.id, "REJECT", {"reviewer": reviewer_id, "notes": review_notes}, reviewer_id
            )
            res = ToolResult(
                success=True,
                data={"approval_id": approval.id, "status": "REJECTED", "notes": review_notes},
                execution_duration_ms=duration
            )
    record_tool_execution(db, tenant_id, "approve_or_reject_action", {"approval_id": approval_id, "decision": decision, "reviewer_id": reviewer_id}, res)
    return res


# 11. execute_approved_refund
def tool_execute_approved_refund(db: Session, tenant_id: str, approval_id: str, reviewer_id: str, review_notes: str = "") -> ToolResult:
    start = time.perf_counter()
    exec_res = refund_service.execute_approved_refund(db, tenant_id, approval_id, reviewer_id, review_notes)
    duration = (time.perf_counter() - start) * 1000
    res = ToolResult(
        success=exec_res["success"],
        data=exec_res,
        error=exec_res.get("error"),
        execution_duration_ms=duration
    )
    record_tool_execution(db, tenant_id, "execute_approved_refund", {"approval_id": approval_id, "reviewer_id": reviewer_id}, res)
    return res


# 12. escalate_to_human
def tool_escalate_to_human(db: Session, tenant_id: str, ticket_id: str, reason: str, details: Optional[Dict[str, Any]] = None) -> ToolResult:
    start = time.perf_counter()
    ticket = ticket_service.update_ticket_status(
        db, tenant_id, ticket_id, TicketStatus.ESCALATED, f"Escalated to human support: {reason}"
    )
    duration = (time.perf_counter() - start) * 1000

    audit_service.log_audit_event(
        db, tenant_id, "TICKET_ESCALATED", "SupportTicket", ticket_id, "ESCALATE", {"reason": reason, "details": details or {}}
    )
    res = ToolResult(
        success=True,
        data={
            "ticket_id": ticket_id,
            "status": "ESCALATED",
            "reason": reason,
            "message": "Ticket has been escalated to human support operations. A support lead will review and respond."
        },
        execution_duration_ms=duration,
    )
    record_tool_execution(db, tenant_id, "escalate_to_human", {"ticket_id": ticket_id, "reason": reason}, res, ticket_id)
    return res
