import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.order import Order, OrderStatus
from backend.app.models.payment import Payment, PaymentStatus
from backend.app.models.approval import ApprovalRequest, ApprovalAction, ApprovalStatus
from backend.app.models.ticket import SupportTicket, TicketStatus
from backend.app.services.order_service import get_order_by_id_or_number
from backend.app.services.audit_service import log_audit_event


def check_refund_eligibility(
    db: Session,
    tenant_id: str,
    order_id_or_number: str,
    customer_id: str,
    reason: str = "customer_request"
) -> Dict[str, Any]:
    """
    Evaluates refund rules:
    - Order existence and customer ownership.
    - Status check (CANCELLED or REFUNDED orders cannot be refunded again).
    - Delivery window check (within 30 days of delivery).
    - Payment capture status.
    - Previous refunds count in last 90 days.
    """
    order_res = get_order_by_id_or_number(db, tenant_id, order_id_or_number, customer_id)
    if not order_res["found"]:
        return {
            "eligible": False,
            "reason": order_res["error"],
            "requires_approval": False,
            "max_refundable_amount": 0.0,
        }

    order: Order = order_res["order"]

    if order.status == OrderStatus.REFUNDED:
        return {
            "eligible": False,
            "reason": f"Order {order.order_number} has already been fully refunded.",
            "requires_approval": False,
            "max_refundable_amount": 0.0,
        }

    payment = (
        db.query(Payment)
        .filter(Payment.tenant_id == tenant_id, Payment.order_id == order.id)
        .first()
    )

    if not payment or payment.status not in (PaymentStatus.CAPTURED, PaymentStatus.PARTIALLY_REFUNDED):
        return {
            "eligible": False,
            "reason": f"Order {order.order_number} does not have a settled/captured payment (Status: {payment.status.value if payment else 'NONE'}).",
            "requires_approval": False,
            "max_refundable_amount": 0.0,
        }

    # Delivery window check if delivered
    now = datetime.now(timezone.utc)
    if order.status == OrderStatus.DELIVERED and order.delivered_at:
        # Normalize timezone if needed
        deliv = order.delivered_at
        if deliv.tzinfo is None:
            deliv = deliv.replace(tzinfo=timezone.utc)
        days_since_delivery = (now - deliv).days
        if days_since_delivery > settings.REFUND_WINDOW_DAYS:
            return {
                "eligible": False,
                "reason": f"Delivery was {days_since_delivery} days ago, exceeding the {settings.REFUND_WINDOW_DAYS}-day return window.",
                "requires_approval": True,  # Policy override could be requested
                "max_refundable_amount": 0.0,
            }

    # Check 90-day previous refunds
    ninety_days_ago = now - timedelta(days=90)
    prev_refunds_count = (
        db.query(ApprovalRequest)
        .filter(
            ApprovalRequest.tenant_id == tenant_id,
            ApprovalRequest.customer_id == customer_id,
            ApprovalRequest.action_type == ApprovalAction.REFUND,
            ApprovalRequest.status == ApprovalStatus.APPROVED,
            ApprovalRequest.created_at >= ninety_days_ago,
        )
        .count()
    )

    remaining_amount = max(0.0, order.total_amount - order.refunded_amount)
    if remaining_amount <= 0:
        return {
            "eligible": False,
            "reason": "Order balance has already been completely refunded.",
            "requires_approval": False,
            "max_refundable_amount": 0.0,
        }

    # High frequency or amount > threshold requires approval
    requires_approval = (
        remaining_amount > settings.AUTO_REFUND_LIMIT_USD
        or prev_refunds_count >= settings.MAX_REFUNDS_PER_90_DAYS
    )

    return {
        "eligible": True,
        "reason": "Order meets refund eligibility criteria.",
        "requires_approval": requires_approval,
        "order_id": order.id,
        "order_number": order.order_number,
        "total_amount": order.total_amount,
        "already_refunded": order.refunded_amount,
        "max_refundable_amount": remaining_amount,
        "currency": order.currency,
        "previous_refunds_90d": prev_refunds_count,
    }


def calculate_refund_amount(
    db: Session,
    tenant_id: str,
    order_id_or_number: str,
    customer_id: str,
    return_type: str = "full",
    deduct_shipping: bool = False
) -> Dict[str, Any]:
    """Calculate permitted refund amount strictly on the server."""
    eligibility = check_refund_eligibility(db, tenant_id, order_id_or_number, customer_id)
    if not eligibility["eligible"]:
        return {
            "success": False,
            "amount": 0.0,
            "reason": eligibility["reason"],
            "requires_approval": eligibility.get("requires_approval", False)
        }

    max_amount = eligibility["max_refundable_amount"]
    calculated = max_amount

    if deduct_shipping and calculated > 5.99:
        calculated -= 5.99

    calculated = round(calculated, 2)
    requires_approval = calculated > settings.AUTO_REFUND_LIMIT_USD or eligibility["requires_approval"]

    return {
        "success": True,
        "order_id": eligibility["order_id"],
        "order_number": eligibility["order_number"],
        "amount": calculated,
        "currency": eligibility["currency"],
        "requires_approval": requires_approval,
        "reason": "Calculated by server policy."
    }


def create_approval_request(
    db: Session,
    tenant_id: str,
    ticket_id: str,
    customer_id: str,
    order_id: str,
    action_type: ApprovalAction,
    amount: float,
    currency: str,
    reason: str,
    requested_by: str = "ai_agent"
) -> ApprovalRequest:
    idempotency_key = f"approval-{tenant_id}-{order_id}-{action_type.value}-{amount}-{uuid.uuid4().hex[:6]}"
    
    approval = ApprovalRequest(
        id=f"appr-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        ticket_id=ticket_id,
        customer_id=customer_id,
        order_id=order_id,
        requested_by=requested_by,
        action_type=action_type,
        requested_amount=amount,
        currency=currency,
        reason=reason,
        evidence_data=json.dumps({"order_id": order_id, "amount": amount, "timestamp": datetime.now(timezone.utc).isoformat()}),
        status=ApprovalStatus.PENDING,
        idempotency_key=idempotency_key,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)

    log_audit_event(
        db=db,
        tenant_id=tenant_id,
        event_type="APPROVAL_REQUESTED",
        resource_type="ApprovalRequest",
        resource_id=approval.id,
        action="CREATE",
        details={"ticket_id": ticket_id, "amount": amount, "reason": reason},
        user_id=requested_by
    )
    return approval


def execute_approved_refund(
    db: Session,
    tenant_id: str,
    approval_id: str,
    reviewer_id: str,
    review_notes: str = ""
) -> Dict[str, Any]:
    """
    Executes an approved refund with idempotency protection and sandbox payment processing.
    """
    approval: Optional[ApprovalRequest] = (
        db.query(ApprovalRequest)
        .filter(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.id == approval_id)
        .first()
    )

    if not approval:
        return {"success": False, "error": f"Approval request '{approval_id}' not found."}

    if approval.status == ApprovalStatus.APPROVED:
        # Idempotent response
        return {
            "success": True,
            "idempotent": True,
            "message": "Refund already executed previously.",
            "approval_id": approval.id,
            "amount": approval.requested_amount,
            "gateway_status": "SANDBOX_SIMULATION_SUCCESS"
        }

    if approval.status != ApprovalStatus.PENDING:
        return {"success": False, "error": f"Approval request is already in status '{approval.status.value}'."}

    order: Optional[Order] = (
        db.query(Order)
        .filter(
            Order.tenant_id == tenant_id,
            (Order.id == approval.order_id) | (Order.order_number == approval.order_id)
        )
        .first()
    )

    if not order:
        return {"success": False, "error": "Associated order could not be found."}

    # Execute refund in transaction
    now = datetime.now(timezone.utc)
    approval.status = ApprovalStatus.APPROVED
    approval.reviewed_by = reviewer_id
    approval.review_notes = review_notes
    approval.resolved_at = now

    order.refunded_amount = round(order.refunded_amount + approval.requested_amount, 2)
    if order.refunded_amount >= order.total_amount:
        order.status = OrderStatus.REFUNDED

    # Update associated payment
    payment = (
        db.query(Payment)
        .filter(Payment.tenant_id == tenant_id, Payment.order_id == order.id)
        .first()
    )
    if payment:
        payment.status = PaymentStatus.REFUNDED if order.status == OrderStatus.REFUNDED else PaymentStatus.PARTIALLY_REFUNDED
        payment.gateway_response_json = json.dumps({
            "provider": "SANDBOX_SIMULATION_PAYMENT_GATEWAY",
            "refund_id": f"rfnd-sim-{uuid.uuid4().hex[:8]}",
            "amount": approval.requested_amount,
            "currency": approval.currency,
            "idempotency_key": approval.idempotency_key,
            "timestamp": now.isoformat(),
            "status": "SANDBOX_SIMULATION_SUCCESS"
        })

    # Update ticket status if present
    if approval.ticket_id:
        ticket = db.query(SupportTicket).filter(SupportTicket.id == approval.ticket_id).first()
        if ticket:
            ticket.status = TicketStatus.RESOLVED
            ticket.resolution_summary = f"Refund of {approval.currency} {approval.requested_amount:.2f} executed via sandbox payment gateway. Approved by {reviewer_id}."

    db.commit()

    log_audit_event(
        db=db,
        tenant_id=tenant_id,
        event_type="REFUND_EXECUTED",
        resource_type="Order",
        resource_id=order.id,
        action="REFUND",
        details={
            "approval_id": approval.id,
            "amount": approval.requested_amount,
            "order_number": order.order_number,
            "reviewer_id": reviewer_id,
            "gateway": "SANDBOX_SIMULATION_PAYMENT_GATEWAY"
        },
        user_id=reviewer_id
    )

    return {
        "success": True,
        "idempotent": False,
        "approval_id": approval.id,
        "order_number": order.order_number,
        "amount": approval.requested_amount,
        "currency": approval.currency,
        "gateway_status": "SANDBOX_SIMULATION_SUCCESS",
        "message": f"Successfully processed sandbox refund of {approval.currency} {approval.requested_amount:.2f}."
    }
