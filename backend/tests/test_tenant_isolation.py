import pytest
from fastapi.testclient import TestClient


def test_cross_tenant_order_access_forbidden(client: TestClient, nova_customer_token: str):
    """NovaStore customer attempting to get ApexGadgets order ORD-2001."""
    headers = {"Authorization": f"Bearer {nova_customer_token}"}
    res = client.get("/api/v1/orders/ORD-2001", headers=headers)
    # Order belongs to tenant_apex, so within tenant_nova it does not exist -> 404
    assert res.status_code == 404


def test_customer_ownership_mismatch_forbidden(client: TestClient, nova_customer_token: str):
    """Customer 1 attempting to query Customer 2's order ORD-1005 within same tenant."""
    headers = {"Authorization": f"Bearer {nova_customer_token}"}
    res = client.get("/api/v1/orders/ORD-1005", headers=headers)
    assert res.status_code == 403
    assert "does not belong to customer" in res.json()["detail"]


def test_cross_tenant_ticket_access_prevented(client: TestClient, apex_customer_token: str):
    """Apex customer attempting to access NovaStore ticket TCK-1001."""
    headers = {"Authorization": f"Bearer {apex_customer_token}"}
    res = client.get("/api/v1/tickets/TCK-1001", headers=headers)
    assert res.status_code == 404


def test_approvals_isolated_by_tenant(client: TestClient, nova_approver_token: str):
    """Approver in NovaStore only sees approvals belonging to tenant_nova."""
    headers = {"Authorization": f"Bearer {nova_approver_token}"}
    res = client.get("/api/v1/approvals", headers=headers)
    assert res.status_code == 200
    approvals = res.json()
    for a in approvals:
        assert a.get("order_number") != "ORD-2001"
