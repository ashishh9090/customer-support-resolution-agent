from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.order import Order


def get_order_by_id_or_number(
    db: Session,
    tenant_id: str,
    order_id_or_number: str,
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve order with strict tenant isolation and customer ownership validation.
    Returns structured dictionary with verification status.
    """
    query = db.query(Order).filter(
        Order.tenant_id == tenant_id,
        (Order.id == order_id_or_number) | (Order.order_number == order_id_or_number)
    )
    order = query.first()

    if not order:
        return {
            "found": False,
            "error": f"Order '{order_id_or_number}' not found for tenant '{tenant_id}'."
        }

    # Verify customer ownership if customer_id is provided
    if customer_id and order.customer_id != customer_id:
        return {
            "found": False,
            "ownership_mismatch": True,
            "error": f"Order '{order_id_or_number}' does not belong to customer '{customer_id}'."
        }

    return {
        "found": True,
        "ownership_mismatch": False,
        "order": order
    }
