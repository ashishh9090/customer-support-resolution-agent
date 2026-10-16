from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DashboardMetrics(BaseModel):
    total_tickets: int
    resolved_tickets: int
    pending_tickets: int
    escalated_tickets: int
    waiting_approval_tickets: int
    approval_queue_count: int
    average_resolution_time_ms: float
    total_refunds_processed_usd: float


class ToolMetricItem(BaseModel):
    tool_name: str
    total_calls: int
    success_calls: int
    failure_calls: int
    success_rate_percent: float
    avg_duration_ms: float


class AuditEventResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: Optional[str] = None
    event_type: str
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    created_at: datetime
