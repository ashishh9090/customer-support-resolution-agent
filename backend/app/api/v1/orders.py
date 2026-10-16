import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user_context
from backend.app.security.auth import AuthenticatedContext
from backend.app.models.user import UserRole
from backend.app.models.order import Order
from backend.app.schemas.order import OrderResponse
from backend.app.services.order_service import get_order_by_id_or_number

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderResponse])
def list_orders(
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Order).filter(Order.tenant_id == ctx.tenant_id)
    if ctx.role == UserRole.CUSTOMER:
        query = query.filter(Order.customer_id == ctx.customer_id)

    orders = query.order_by(Order.placed_at.desc()).all()
    results = []
    for o in orders:
        try:
            items = json.loads(o.items_json) if o.items_json else []
        except Exception:
            items = []
        results.append(
            OrderResponse(
                id=o.id,
                order_number=o.order_number,
                customer_id=o.customer_id,
                status=o.status.value,
                total_amount=o.total_amount,
                refunded_amount=o.refunded_amount,
                currency=o.currency,
                shipping_address=o.shipping_address,
                tracking_number=o.tracking_number,
                carrier=o.carrier,
                placed_at=o.placed_at,
                delivered_at=o.delivered_at,
                items=items,
            )
        )
    return results


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    customer_id = ctx.customer_id if ctx.role == UserRole.CUSTOMER else None
    res = get_order_by_id_or_number(db, ctx.tenant_id, order_id, customer_id)

    if not res["found"]:
        if res.get("ownership_mismatch"):
            raise HTTPException(status_code=403, detail=res["error"])
        raise HTTPException(status_code=404, detail=res["error"])

    o: Order = res["order"]
    try:
        items = json.loads(o.items_json) if o.items_json else []
    except Exception:
        items = []

    return OrderResponse(
        id=o.id,
        order_number=o.order_number,
        customer_id=o.customer_id,
        status=o.status.value,
        total_amount=o.total_amount,
        refunded_amount=o.refunded_amount,
        currency=o.currency,
        shipping_address=o.shipping_address,
        tracking_number=o.tracking_number,
        carrier=o.carrier,
        placed_at=o.placed_at,
        delivered_at=o.delivered_at,
        items=items,
    )
