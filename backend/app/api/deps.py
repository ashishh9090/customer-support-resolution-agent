from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.customer import Customer
from backend.app.security.auth import decode_access_token, AuthenticatedContext

security_scheme = HTTPBearer(auto_error=False)


def get_current_user_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
    db: Session = Depends(get_db),
) -> AuthenticatedContext:
    # 1. Bearer Token Check
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload:
            tenant_id = payload.get("tenant_id")
            user_id = payload.get("user_id")
            role_str = payload.get("role", "customer")
            email = payload.get("email", "")
            full_name = payload.get("full_name", "")
            customer_id = payload.get("customer_id")

            try:
                role = UserRole(role_str)
            except ValueError:
                role = UserRole.CUSTOMER

            return AuthenticatedContext(
                tenant_id=tenant_id,
                user_id=user_id,
                email=email,
                role=role,
                full_name=full_name,
                customer_id=customer_id,
            )

    # 2. Development / Demo Headers Fallback
    if x_tenant_id and x_user_id:
        user = db.query(User).filter(User.tenant_id == x_tenant_id, User.id == x_user_id).first()
        if user:
            customer = db.query(Customer).filter(Customer.tenant_id == x_tenant_id, Customer.user_id == user.id).first()
            return AuthenticatedContext(
                tenant_id=user.tenant_id,
                user_id=user.id,
                email=user.email,
                role=user.role,
                full_name=user.full_name,
                customer_id=customer.id if customer else None,
            )
        else:
            # Synthetic dev context
            try:
                role = UserRole(x_user_role) if x_user_role else UserRole.CUSTOMER
            except ValueError:
                role = UserRole.CUSTOMER
            return AuthenticatedContext(
                tenant_id=x_tenant_id,
                user_id=x_user_id,
                email=f"{x_user_id}@{x_tenant_id}.local",
                role=role,
                full_name=f"Dev User ({x_user_id})",
                customer_id=x_user_id if role == UserRole.CUSTOMER else None,
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please provide a valid Bearer token or development identity headers.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_roles(allowed_roles: List[UserRole]):
    def role_checker(ctx: AuthenticatedContext = Depends(get_current_user_context)) -> AuthenticatedContext:
        if ctx.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of {[r.value for r in allowed_roles]}, user has role '{ctx.role.value}'."
            )
        return ctx
    return role_checker
