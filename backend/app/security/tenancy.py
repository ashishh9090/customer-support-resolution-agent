from fastapi import HTTPException, status
from backend.app.security.auth import AuthenticatedContext
from backend.app.models.user import UserRole


def verify_tenant_access(ctx: AuthenticatedContext, target_tenant_id: str) -> None:
    """Ensure the user can only access resources matching their tenant."""
    if ctx.tenant_id != target_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cross-tenant access forbidden: user belongs to {ctx.tenant_id}, target resource is {target_tenant_id}"
        )


def verify_role_access(ctx: AuthenticatedContext, allowed_roles: list[UserRole]) -> None:
    """Ensure the user has one of the required roles."""
    if ctx.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: action requires one of {[r.value for r in allowed_roles]}, user has {ctx.role.value}"
        )
