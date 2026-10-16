from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.customer import Customer


def get_customer(db: Session, tenant_id: str, customer_id: str) -> Optional[Customer]:
    """Retrieve customer by ID strictly within tenant boundary."""
    return (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.id == customer_id)
        .first()
    )


def get_customer_by_email(db: Session, tenant_id: str, email: str) -> Optional[Customer]:
    """Retrieve customer by email strictly within tenant boundary."""
    return (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.email.ilike(email.strip()))
        .first()
    )
