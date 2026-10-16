from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVED' or 'REJECTED'")
    review_notes: str = Field("", description="Optional notes or rationale")


class ApprovalResponse(BaseModel):
    id: str
    ticket_id: str
    order_id: Optional[str] = None
    customer_id: str
    requested_by: str
    action_type: str
    requested_amount: float
    currency: str
    reason: str
    status: str
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    idempotency_key: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    order_number: Optional[str] = None
