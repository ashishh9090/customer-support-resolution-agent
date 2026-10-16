import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user_context
from backend.app.security.auth import AuthenticatedContext
from backend.app.schemas.chat import ChatRequest, ChatResponse, WorkflowEventSchema
from backend.app.agents.graph import support_workflow
from backend.app.agents.state import SupportAgentState
from backend.app.services.ticket_service import (
    get_or_create_conversation,
    add_message_to_conversation,
)

router = APIRouter(prefix="/chat", tags=["Agent Chat"])


@router.post("", response_model=ChatResponse)
def submit_chat_message(
    req: ChatRequest,
    ctx: AuthenticatedContext = Depends(get_current_user_context),
    db: Session = Depends(get_db)
):
    """
    Submit a message to the AI Support Resolution Agent.
    Executes real stateful LangGraph workflow with tool invocations and audit logging.
    """
    customer_id = ctx.customer_id or ctx.user_id
    tenant_id = ctx.tenant_id

    # Get or create conversation in persistent DB
    conv = get_or_create_conversation(
        db=db,
        tenant_id=tenant_id,
        customer_id=customer_id,
        ticket_id=req.ticket_id
    )

    # Persist inbound customer message
    add_message_to_conversation(
        db=db,
        conversation_id=conv.id,
        sender_type="customer",
        content=req.message,
    )

    request_id = f"req-{uuid.uuid4().hex[:12]}"

    # Initial typed state
    initial_state: SupportAgentState = {
        "request_id": request_id,
        "conversation_id": conv.id,
        "ticket_id": req.ticket_id or conv.ticket_id,
        "tenant_id": tenant_id,
        "user_id": ctx.user_id,
        "customer_id": customer_id,
        "customer_message": req.message,
        "conversation_history": [],
        "detected_intent": None,
        "classification_confidence": 0.0,
        "extracted_entities": {},
        "retrieved_context": [],
        "citations": [],
        "customer_info": None,
        "order_info": None,
        "payment_info": None,
        "eligibility_info": None,
        "proposed_resolution": None,
        "requires_approval": False,
        "approval_id": None,
        "approval_status": "NONE",
        "planned_tools": [],
        "executed_tools": [],
        "verification_passed": True,
        "final_response": "",
        "escalation_required": False,
        "escalation_reason": None,
        "clarification_needed": False,
        "timeline": [],
        "execution_status": "PROCESSING",
        "error_details": None,
    }

    # Run LangGraph workflow with thread checkpointing
    config = {"configurable": {"thread_id": conv.id}}
    result_state = support_workflow.invoke(initial_state, config=config)

    # Convert timeline events to schema
    timeline_schemas = [
        WorkflowEventSchema(
            step_name=ev.get("step_name", "unknown"),
            timestamp=ev.get("timestamp", ""),
            status=ev.get("status", "COMPLETED"),
            details=ev.get("details", {}),
        )
        for ev in result_state.get("timeline", [])
    ]

    return ChatResponse(
        request_id=request_id,
        conversation_id=conv.id,
        ticket_id=result_state.get("ticket_id"),
        response=result_state.get("final_response", ""),
        detected_intent=result_state.get("detected_intent"),
        confidence=result_state.get("classification_confidence", 0.0),
        citations=result_state.get("citations", []),
        execution_status=result_state.get("execution_status", "COMPLETED"),
        requires_approval=result_state.get("requires_approval", False),
        approval_id=result_state.get("approval_id"),
        order_info=result_state.get("order_info"),
        payment_info=result_state.get("payment_info"),
        timeline=timeline_schemas,
        executed_tools=result_state.get("executed_tools", []),
    )
