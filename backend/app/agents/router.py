from typing import Literal
from backend.app.agents.state import SupportAgentState


def route_after_input_validation(state: SupportAgentState) -> Literal["escalation", "response_generation", "intent_classification"]:
    if state.get("escalation_required"):
        return "escalation"
    if state.get("clarification_needed"):
        return "response_generation"
    return "intent_classification"


def route_after_intent_classification(state: SupportAgentState) -> Literal["escalation", "customer_authorization"]:
    if state.get("escalation_required"):
        return "escalation"
    return "customer_authorization"


def route_after_customer_authorization(state: SupportAgentState) -> Literal["escalation", "context_retrieval"]:
    if state.get("escalation_required"):
        return "escalation"
    return "context_retrieval"


def route_after_policy_evaluation(state: SupportAgentState) -> Literal["resolution_planning"]:
    return "resolution_planning"


def route_after_resolution_planning(state: SupportAgentState) -> Literal["response_generation", "tool_execution"]:
    if state.get("clarification_needed"):
        return "response_generation"
    return "tool_execution"


def route_after_tool_execution(state: SupportAgentState) -> Literal["human_approval", "outcome_verification"]:
    if state.get("requires_approval") and state.get("approval_status") != "APPROVED":
        return "human_approval"
    return "outcome_verification"


def route_after_human_approval(state: SupportAgentState) -> Literal["outcome_verification"]:
    return "outcome_verification"


def route_after_outcome_verification(state: SupportAgentState) -> Literal["escalation", "response_generation"]:
    if state.get("escalation_required"):
        return "escalation"
    return "response_generation"


def route_after_response_generation(state: SupportAgentState) -> Literal["audit_and_completion"]:
    return "audit_and_completion"


def route_after_escalation(state: SupportAgentState) -> Literal["audit_and_completion"]:
    return "audit_and_completion"
