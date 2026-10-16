import pytest
from sqlalchemy.orm import Session
from backend.app.tools.support_tools import (
    tool_get_customer,
    tool_get_order,
    tool_get_payment_status,
    tool_check_refund_eligibility,
    tool_calculate_refund_amount,
    tool_create_support_ticket,
    tool_search_knowledge_base,
    tool_request_human_approval,
    tool_approve_or_reject_action,
    tool_escalate_to_human,
)


def test_tool_get_customer(db_session: Session):
    res = tool_get_customer(db_session, "tenant_nova", "cust-nova-1")
    assert res.success is True
    assert res.data["email"] == "john.doe@example.com"

    res_missing = tool_get_customer(db_session, "tenant_nova", "cust-nonexistent")
    assert res_missing.success is False


def test_tool_get_order(db_session: Session):
    res = tool_get_order(db_session, "tenant_nova", "ORD-1001", "cust-nova-1")
    assert res.success is True
    assert res.data["total_amount"] == 42.50
    assert res.data["status"] == "DELIVERED"

    # Cross-customer ownership check
    res_mismatch = tool_get_order(db_session, "tenant_nova", "ORD-1001", "cust-nova-2")
    assert res_mismatch.success is False
    assert "does not belong" in res_mismatch.error


def test_tool_get_payment_status(db_session: Session):
    # Captured payment
    res_cap = tool_get_payment_status(db_session, "tenant_nova", "ORD-1001", "cust-nova-1")
    assert res_cap.success is True
    assert res_cap.data["status"] == "CAPTURED"

    # Failed payment
    res_fail = tool_get_payment_status(db_session, "tenant_nova", "ORD-1006", "cust-nova-2")
    assert res_fail.success is True
    assert res_fail.data["status"] == "FAILED"
    assert "ERR_INSUFFICIENT_FUNDS" in res_fail.data["failure_reason"]


def test_tool_check_refund_eligibility(db_session: Session):
    # Under $50, delivered recently -> eligible, no approval required
    res_auto = tool_check_refund_eligibility(db_session, "tenant_nova", "ORD-1001", "cust-nova-1")
    assert res_auto.success is True
    assert res_auto.data["requires_approval"] is False

    # Over $50 ($129.99) -> requires approval
    res_high = tool_check_refund_eligibility(db_session, "tenant_nova", "ORD-1002", "cust-nova-1")
    assert res_high.success is True
    assert res_high.data["requires_approval"] is True

    # Delivered 45 days ago -> ineligible past 30-day window
    res_old = tool_check_refund_eligibility(db_session, "tenant_nova", "ORD-1004", "cust-nova-1")
    assert res_old.success is False
    assert "exceeding the 30-day return window" in res_old.error


def test_tool_create_ticket_and_escalate(db_session: Session):
    t_res = tool_create_support_ticket(
        db_session, "tenant_nova", "cust-nova-1", "Test Broken Screen", "Customer screen cracked on delivery", "damaged_product", "HIGH"
    )
    assert t_res.success is True
    ticket_id = t_res.data["ticket_id"]

    esc_res = tool_escalate_to_human(db_session, "tenant_nova", ticket_id, "Customer requested supervisor")
    assert esc_res.success is True
    assert esc_res.data["status"] == "ESCALATED"
