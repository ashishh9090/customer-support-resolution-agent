from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
import operator


class WorkflowEvent(TypedDict):
    step_name: str
    timestamp: str
    status: str  # "STARTED", "COMPLETED", "FAILED", "PAUSED"
    details: Dict[str, Any]


class SupportAgentState(TypedDict):
    # Identifiers
    request_id: str
    conversation_id: str
    ticket_id: Optional[str]
    tenant_id: str
    user_id: str
    customer_id: str

    # Inputs & History
    customer_message: str
    conversation_history: List[Dict[str, str]]

    # Intent & Classification
    detected_intent: Optional[str]  # order_status, refund_request, damaged_product, payment_inquiry, general_faq, unknown_ambiguous, prompt_injection
    classification_confidence: float
    extracted_entities: Dict[str, Any]  # e.g. {"order_id": "ORD-1001", "return_reason": "damaged"}

    # Context & Retrieval
    retrieved_context: List[Dict[str, Any]]
    citations: List[str]

    # Domain Data
    customer_info: Optional[Dict[str, Any]]
    order_info: Optional[Dict[str, Any]]
    payment_info: Optional[Dict[str, Any]]
    eligibility_info: Optional[Dict[str, Any]]

    # Resolution & Tools
    proposed_resolution: Optional[str]
    requires_approval: bool
    approval_id: Optional[str]
    approval_status: Optional[str]  # "NONE", "PENDING", "APPROVED", "REJECTED"
    
    # Tool Execution Tracking
    planned_tools: List[Dict[str, Any]]
    executed_tools: Annotated[List[Dict[str, Any]], operator.add]
    
    # Final Outcomes
    verification_passed: bool
    final_response: str
    escalation_required: bool
    escalation_reason: Optional[str]
    clarification_needed: bool
    
    # Execution Trace / Audit
    timeline: Annotated[List[WorkflowEvent], operator.add]
    execution_status: str  # "PROCESSING", "AWAITING_APPROVAL", "COMPLETED", "ESCALATED", "ERROR"
    error_details: Optional[str]
