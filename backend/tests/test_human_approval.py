import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.models.approval import ApprovalRequest, ApprovalStatus


def test_agent_workflow_pauses_for_approval(client: TestClient, nova_customer_token: str):
    headers = {"Authorization": f"Bearer {nova_customer_token}"}
    res = client.post(
        "/api/v1/chat",
        json={"message": "I want a refund for my order ORD-1002"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["requires_approval"] is True
    assert data["execution_status"] == "AWAITING_APPROVAL"
    assert data["approval_id"] is not None
    assert "Pending Human Supervisor Review" in data["response"]


def test_approver_can_approve_and_resume(client: TestClient, nova_customer_token: str, nova_approver_token: str):
    # Customer triggers approval
    c_headers = {"Authorization": f"Bearer {nova_customer_token}"}
    chat_res = client.post(
        "/api/v1/chat",
        json={"message": "Please refund order ORD-1002"},
        headers=c_headers,
    )
    approval_id = chat_res.json()["approval_id"]
    assert approval_id is not None

    # Approver approves
    a_headers = {"Authorization": f"Bearer {nova_approver_token}"}
    decision_res = client.post(
        f"/api/v1/approvals/{approval_id}/action",
        json={"decision": "APPROVED", "review_notes": "Authorized under store warranty exception"},
        headers=a_headers,
    )
    assert decision_res.status_code == 200
    assert decision_res.json()["status"] == "APPROVED"
    assert decision_res.json()["reviewed_by"] == "usr-nova-approver"


def test_self_approval_prevented(client: TestClient, nova_customer_token: str, db_session: Session):
    # If a user requested the approval, they cannot approve their own
    from backend.app.services.refund_service import create_approval_request
    from backend.app.models.approval import ApprovalAction
    appr = create_approval_request(
        db_session, "tenant_nova", "tck-test", "cust-nova-1", "ord-1002",
        ApprovalAction.REFUND, 129.99, "USD", "Self approval test", requested_by="usr-nova-approver"
    )

    # Attempt to approve with the same user ID
    token = client.post("/api/v1/auth/switch-demo-user/usr-nova-approver").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        f"/api/v1/approvals/{appr.id}/action",
        json={"decision": "APPROVED", "review_notes": "Attempting self approval"},
        headers=headers,
    )
    assert res.status_code == 403
    assert "Conflict of interest" in res.json()["detail"]
