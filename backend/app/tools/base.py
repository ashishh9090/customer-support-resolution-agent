import time
import json
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.app.models.tool_execution import ToolExecution


class ToolResult(BaseModel):
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_duration_ms: float = 0.0


def record_tool_execution(
    db: Session,
    tenant_id: str,
    tool_name: str,
    input_args: Dict[str, Any],
    result: ToolResult,
    ticket_id: Optional[str] = None,
) -> ToolExecution:
    exec_record = ToolExecution(
        id=f"exec-{uuid.uuid4().hex[:12]}",
        tenant_id=tenant_id,
        ticket_id=ticket_id,
        tool_name=tool_name,
        input_args=json.dumps(input_args, default=str),
        output_result=json.dumps(result.data, default=str),
        status="SUCCESS" if result.success else "FAILED",
        execution_duration_ms=result.execution_duration_ms,
        error_message=result.error,
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)
    return exec_record
