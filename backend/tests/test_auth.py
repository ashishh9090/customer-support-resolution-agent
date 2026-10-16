import pytest
from fastapi.testclient import TestClient


def test_login_success(client: TestClient):
    res = client.post("/api/v1/auth/login", json={"email": "admin@novastore.com", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["tenant_id"] == "tenant_nova"


def test_login_invalid_password(client: TestClient):
    res = client.post("/api/v1/auth/login", json={"email": "admin@novastore.com", "password": "wrongpassword"})
    assert res.status_code == 401


def test_demo_users_list(client: TestClient):
    res = client.get("/api/v1/auth/demo-users")
    assert res.status_code == 200
    users = res.json()
    assert len(users) >= 4
    roles = {u["role"] for u in users}
    assert "customer" in roles
    assert "approver" in roles


def test_switch_demo_user(client: TestClient):
    res = client.post("/api/v1/auth/switch-demo-user/usr-nova-cust1")
    assert res.status_code == 200
    data = res.json()
    assert data["user_id"] == "usr-nova-cust1"
    assert data["customer_id"] == "cust-nova-1"
