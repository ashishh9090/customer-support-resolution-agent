from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str
    description: str
    category: str = "general"
    priority: str = "MEDIUM"
    order_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    sender_type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class TicketResponse(BaseModel):
    id: str
    ticket_number: str
    customer_id: str
    order_id: Optional[str] = None
    title: str
    description: str
    status: str
    priority: str
    category: str
    resolution_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TicketDetailResponse(TicketResponse):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    order_details: Optional[Dict[str, Any]] = None
    messages: List[MessageResponse] = Field(default_factory=list)
    tool_executions: List[Dict[str, Any]] = Field(default_factory=list)
    approvals: List[Dict[str, Any]] = Field(default_factory=list)
