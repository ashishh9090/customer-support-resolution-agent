from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.payment import Payment
from backend.app.services.order_service import get_order_by_id_or_number


def get_payment_for_order(
    db: Session,
    tenant_id: str,
    order_id_or_number: str,
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    order_res = get_order_by_id_or_number(db, tenant_id, order_id_or_number, customer_id)
    if not order_res["found"]:
        return order_res

    order = order_res["order"]
    payment = (
        db.query(Payment)
        .filter(Payment.tenant_id == tenant_id, Payment.order_id == order.id)
        .order_by(Payment.created_at.desc())
        .first()
    )

    if not payment:
        return {
            "found": False,
            "error": f"No payment record found for order '{order.order_number}'."
        }

    return {
        "found": True,
        "payment": payment,
        "order": order
    }
