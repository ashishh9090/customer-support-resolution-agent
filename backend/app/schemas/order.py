from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class OrderItemSchema(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price: float


class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer_id: str
    status: str
    total_amount: float
    refunded_amount: float
    currency: str
    shipping_address: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    placed_at: datetime
    delivered_at: Optional[datetime] = None
    items: List[Dict[str, Any]] = Field(default_factory=list)
