from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.customer import Customer
from backend.app.models.tenant import Tenant
from backend.app.security.auth import verify_password, create_access_token, AuthenticatedContext
from backend.app.schemas.auth import Token, LoginRequest, DemoUser
from backend.app.api.deps import get_current_user_context

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    query = db.query(User).filter(User.email == req.email.strip().lower())
    if req.tenant_id:
        query = query.filter(User.tenant_id == req.tenant_id)
    user = query.first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer = db.query(Customer).filter(Customer.tenant_id == user.tenant_id, Customer.user_id == user.id).first()
    customer_id = customer.id if customer else None

    token_data = {
        "tenant_id": user.tenant_id,
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
        "customer_id": customer_id,
    }
    access_token = create_access_token(token_data)

    return Token(
        access_token=access_token,
        token_type="bearer",
        tenant_id=user.tenant_id,
        user_id=user.id,
        role=user.role,
        email=user.email,
        full_name=user.full_name,
        customer_id=customer_id,
    )


@router.get("/me")
def get_current_user_profile(ctx: AuthenticatedContext = Depends(get_current_user_context)):
    return ctx


@router.get("/demo-users", response_model=List[DemoUser])
def get_demo_users(db: Session = Depends(get_db)):
    """Return synthetic demo personas across tenants for testing & evaluation."""
    users = db.query(User).filter(User.is_active == True).all()
    demo_list = []
    for u in users:
        tenant = db.query(Tenant).filter(Tenant.id == u.tenant_id).first()
        customer = db.query(Customer).filter(Customer.tenant_id == u.tenant_id, Customer.user_id == u.id).first()
        
        desc = f"{u.role.value.capitalize()} in {tenant.name if tenant else u.tenant_id}"
        demo_list.append(
            DemoUser(
                user_id=u.id,
                tenant_id=u.tenant_id,
                tenant_name=tenant.name if tenant else u.tenant_id,
                email=u.email,
                full_name=u.full_name,
                role=u.role,
                customer_id=customer.id if customer else None,
                description=desc,
            )
        )
    return demo_list


@router.post("/switch-demo-user/{user_id}", response_model=Token)
def switch_demo_user(user_id: str, db: Session = Depends(get_db)):
    """Convenience endpoint to log in as any seeded demo user without password friction."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Demo user not found.")

    customer = db.query(Customer).filter(Customer.tenant_id == user.tenant_id, Customer.user_id == user.id).first()
    customer_id = customer.id if customer else None

    token_data = {
        "tenant_id": user.tenant_id,
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "full_name": user.full_name,
        "customer_id": customer_id,
    }
    access_token = create_access_token(token_data)

    return Token(
        access_token=access_token,
        token_type="bearer",
        tenant_id=user.tenant_id,
        user_id=user.id,
        role=user.role,
        email=user.email,
        full_name=user.full_name,
        customer_id=customer_id,
    )
