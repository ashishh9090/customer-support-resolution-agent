import pytest
from fastapi.testclient import TestClient


def test_health_and_ready(client: TestClient):
    res_h = client.get("/api/v1/health")
    assert res_h.status_code == 200
    assert res_h.json()["status"] == "healthy"

    res_r = client.get("/api/v1/ready")
    assert res_r.status_code == 200
    assert res_r.json()["ready"] is True


def test_chat_order_inquiry(client: TestClient, nova_customer_token: str):
    headers = {"Authorization": f"Bearer {nova_customer_token}"}
    res = client.post(
        "/api/v1/chat",
        json={"message": "Where is my order ORD-1001?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["detected_intent"] == "order_status"
    assert "DELIVERED" in data["response"]
    assert len(data["timeline"]) >= 5
    assert len(data["executed_tools"]) >= 1


def test_tickets_api(client: TestClient, nova_customer_token: str):
    headers = {"Authorization": f"Bearer {nova_customer_token}"}
    res = client.get("/api/v1/tickets", headers=headers)
    assert res.status_code == 200
    tickets = res.json()
    assert isinstance(tickets, list)


def test_analytics_api(client: TestClient, nova_approver_token: str):
    headers = {"Authorization": f"Bearer {nova_approver_token}"}
    res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    metrics = res.json()
    assert "total_tickets" in metrics
    assert "resolved_tickets" in metrics


def test_audit_api(client: TestClient, nova_approver_token: str):
    headers = {"Authorization": f"Bearer {nova_approver_token}"}
    res = client.get("/api/v1/audit", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
