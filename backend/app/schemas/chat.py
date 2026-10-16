from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., description="Customer message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID if ongoing")
    ticket_id: Optional[str] = Field(None, description="Associated ticket ID if known")


class WorkflowEventSchema(BaseModel):
    step_name: str
    timestamp: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    request_id: str
    conversation_id: str
    ticket_id: Optional[str] = None
    response: str
    detected_intent: Optional[str] = None
    confidence: float = 0.0
    citations: List[str] = Field(default_factory=list)
    execution_status: str
    requires_approval: bool = False
    approval_id: Optional[str] = None
    order_info: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None
    timeline: List[WorkflowEventSchema] = Field(default_factory=list)
    executed_tools: List[Dict[str, Any]] = Field(default_factory=list)
