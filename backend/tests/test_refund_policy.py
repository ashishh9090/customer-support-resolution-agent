import pytest
from sqlalchemy.orm import Session
from backend.app.services import refund_service
from backend.app.models.approval import ApprovalAction, ApprovalStatus


def test_refund_calculation_with_shipping_deduction(db_session: Session):
    # ORD-1001 total is $42.50
    calc = refund_service.calculate_refund_amount(
        db_session, "tenant_nova", "ORD-1001", "cust-nova-1", return_type="voluntary", deduct_shipping=True
    )
    assert calc["success"] is True
    # 42.50 - 5.99 = 36.51
    assert calc["amount"] == 36.51
    assert calc["requires_approval"] is False


def test_refund_threshold_triggers_approval(db_session: Session):
    # ORD-1002 total is $129.99
    calc = refund_service.calculate_refund_amount(
        db_session, "tenant_nova", "ORD-1002", "cust-nova-1"
    )
    assert calc["success"] is True
    assert calc["amount"] == 129.99
    assert calc["requires_approval"] is True


def test_refund_ineligible_when_past_window(db_session: Session):
    # ORD-1004 delivered 45 days ago
    elig = refund_service.check_refund_eligibility(
        db_session, "tenant_nova", "ORD-1004", "cust-nova-1"
    )
    assert elig["eligible"] is False
    assert "exceeding the 30-day return window" in elig["reason"]


def test_idempotent_refund_execution(db_session: Session):
    # Create approval
    appr = refund_service.create_approval_request(
        db_session, "tenant_nova", "tck-test-1", "cust-nova-1", "ord-1001",
        ApprovalAction.REFUND, 42.50, "USD", "Test approved refund"
    )
    assert appr.status == ApprovalStatus.PENDING

    # First execution -> Success
    res1 = refund_service.execute_approved_refund(
        db_session, "tenant_nova", appr.id, "usr-nova-approver", "Approved by lead"
    )
    assert res1["success"] is True
    assert res1["idempotent"] is False
    assert res1["gateway_status"] == "SANDBOX_SIMULATION_SUCCESS"

    # Second execution with same approval -> Idempotent replay, no double charge!
    res2 = refund_service.execute_approved_refund(
        db_session, "tenant_nova", appr.id, "usr-nova-approver", "Approved again"
    )
    assert res2["success"] is True
    assert res2["idempotent"] is True
    assert "already executed" in res2["message"]
