import pytest
from typing import Generator
from fastapi.testclient import TestClient

from backend.app.config import settings
TEST_DB_URL = "sqlite:///./test_support_agent.db"
settings.DATABASE_URL = TEST_DB_URL

# Rebind engine and SessionLocal in db.session
import backend.app.db.session as db_session_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

db_session_module.engine = test_engine
db_session_module.SessionLocal = TestingSessionLocal

from backend.app.main import app
from backend.app.models.base import Base
from backend.app.retrieval.indexer import build_knowledge_index
from scripts.seed_database import seed_all
from backend.app.security.auth import create_access_token


@pytest.fixture(autouse=True)
def reset_database_per_test():
    """Reset and re-seed the test database before each test for complete isolation."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    build_knowledge_index()

    db = TestingSessionLocal()
    seed_all(db)
    db.close()
    yield


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[db_session_module.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def nova_customer_token() -> str:
    return create_access_token({
        "tenant_id": "tenant_nova",
        "user_id": "usr-nova-cust1",
        "email": "john.doe@example.com",
        "role": "customer",
        "full_name": "John Doe",
        "customer_id": "cust-nova-1",
    })


@pytest.fixture
def nova_approver_token() -> str:
    return create_access_token({
        "tenant_id": "tenant_nova",
        "user_id": "usr-nova-approver",
        "email": "sarah.approver@novastore.com",
        "role": "approver",
        "full_name": "Sarah Jenkins",
        "customer_id": None,
    })


@pytest.fixture
def apex_customer_token() -> str:
    return create_access_token({
        "tenant_id": "tenant_apex",
        "user_id": "usr-apex-cust1",
        "email": "bob.smith@example.com",
        "role": "customer",
        "full_name": "Bob Smith",
        "customer_id": "cust-apex-1",
    })
