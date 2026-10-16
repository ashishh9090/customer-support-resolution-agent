from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.agents.state import SupportAgentState
from backend.app.agents.nodes import (
    node_input_validation,
    node_intent_classification,
    node_customer_authorization,
    node_context_retrieval,
    node_policy_evaluation,
    node_resolution_planning,
    node_tool_execution,
    node_human_approval,
    node_outcome_verification,
    node_response_generation,
    node_escalation,
    node_audit_and_completion,
)
from backend.app.agents.router import (
    route_after_input_validation,
    route_after_intent_classification,
    route_after_customer_authorization,
    route_after_policy_evaluation,
    route_after_resolution_planning,
    route_after_tool_execution,
    route_after_human_approval,
    route_after_outcome_verification,
    route_after_response_generation,
    route_after_escalation,
)


def create_support_agent_workflow():
    builder = StateGraph(SupportAgentState)

    # 1. Add All 12 Nodes
    builder.add_node("input_validation", node_input_validation)
    builder.add_node("intent_classification", node_intent_classification)
    builder.add_node("customer_authorization", node_customer_authorization)
    builder.add_node("context_retrieval", node_context_retrieval)
    builder.add_node("policy_evaluation", node_policy_evaluation)
    builder.add_node("resolution_planning", node_resolution_planning)
    builder.add_node("tool_execution", node_tool_execution)
    builder.add_node("human_approval", node_human_approval)
    builder.add_node("outcome_verification", node_outcome_verification)
    builder.add_node("response_generation", node_response_generation)
    builder.add_node("escalation", node_escalation)
    builder.add_node("audit_and_completion", node_audit_and_completion)

    # 2. Add Edges and Conditional Routing
    builder.add_edge(START, "input_validation")

    builder.add_conditional_edges(
        "input_validation",
        route_after_input_validation,
        {
            "escalation": "escalation",
            "response_generation": "response_generation",
            "intent_classification": "intent_classification",
        }
    )

    builder.add_conditional_edges(
        "intent_classification",
        route_after_intent_classification,
        {
            "escalation": "escalation",
            "customer_authorization": "customer_authorization",
        }
    )

    builder.add_conditional_edges(
        "customer_authorization",
        route_after_customer_authorization,
        {
            "escalation": "escalation",
            "context_retrieval": "context_retrieval",
        }
    )

    builder.add_edge("context_retrieval", "policy_evaluation")

    builder.add_conditional_edges(
        "policy_evaluation",
        route_after_policy_evaluation,
        {
            "resolution_planning": "resolution_planning",
        }
    )

    builder.add_conditional_edges(
        "resolution_planning",
        route_after_resolution_planning,
        {
            "response_generation": "response_generation",
            "tool_execution": "tool_execution",
        }
    )

    builder.add_conditional_edges(
        "tool_execution",
        route_after_tool_execution,
        {
            "human_approval": "human_approval",
            "outcome_verification": "outcome_verification",
        }
    )

    builder.add_conditional_edges(
        "human_approval",
        route_after_human_approval,
        {
            "outcome_verification": "outcome_verification",
        }
    )

    builder.add_conditional_edges(
        "outcome_verification",
        route_after_outcome_verification,
        {
            "escalation": "escalation",
            "response_generation": "response_generation",
        }
    )

    builder.add_conditional_edges(
        "response_generation",
        route_after_response_generation,
        {
            "audit_and_completion": "audit_and_completion",
        }
    )

    builder.add_conditional_edges(
        "escalation",
        route_after_escalation,
        {
            "audit_and_completion": "audit_and_completion",
        }
    )

    builder.add_edge("audit_and_completion", END)

    # 3. Checkpointing for stateful execution and pause/resume
    checkpointer = MemorySaver()
    compiled_graph = builder.compile(checkpointer=checkpointer)
    return compiled_graph


# Global compiled workflow instance
support_workflow = create_support_agent_workflow()
