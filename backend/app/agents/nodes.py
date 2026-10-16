from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.agents.state import SupportAgentState, WorkflowEvent
from backend.app.agents.mock_llm import classify_intent_and_entities, detect_prompt_injection
from backend.app.tools.support_tools import (
    tool_get_customer,
    tool_get_order,
    tool_get_payment_status,
    tool_check_refund_eligibility,
    tool_calculate_refund_amount,
    tool_create_support_ticket,
    tool_search_knowledge_base,
    tool_request_human_approval,
    tool_escalate_to_human,
)
from backend.app.services.ticket_service import add_message_to_conversation


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# 1. INPUT VALIDATION
def node_input_validation(state: SupportAgentState) -> Dict[str, Any]:
    msg = state.get("customer_message", "").strip()
    timeline_event: WorkflowEvent = {
        "step_name": "input_validation",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {"message_length": len(msg)},
    }

    if not msg:
        timeline_event["status"] = "FAILED"
        timeline_event["details"]["error"] = "Empty customer message"
        return {
            "timeline": [timeline_event],
            "clarification_needed": True,
            "final_response": "Please provide details regarding your inquiry or order so I can assist you.",
            "execution_status": "COMPLETED",
        }

    # Prompt injection check
    if detect_prompt_injection(msg):
        timeline_event["status"] = "FAILED"
        timeline_event["details"]["security_flag"] = "PROMPT_INJECTION_DETECTED"
        return {
            "timeline": [timeline_event],
            "detected_intent": "prompt_injection",
            "classification_confidence": 0.99,
            "escalation_required": True,
            "escalation_reason": "Security Alert: Adversarial prompt injection or policy bypass attempt detected.",
            "final_response": "I cannot fulfill requests attempting to bypass policy or security rules. This interaction has been flagged for administrative review.",
            "execution_status": "ESCALATED",
        }

    return {
        "timeline": [timeline_event],
        "clarification_needed": False,
        "escalation_required": False,
    }


# 2. INTENT CLASSIFICATION
def node_intent_classification(state: SupportAgentState) -> Dict[str, Any]:
    if state.get("escalation_required"):
        return {}

    msg = state["customer_message"]
    intent, confidence, entities = classify_intent_and_entities(msg)

    timeline_event: WorkflowEvent = {
        "step_name": "intent_classification",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "detected_intent": intent,
            "confidence": confidence,
            "entities": entities,
        },
    }

    clarification_needed = False
    if intent == "unknown_ambiguous" and confidence < 0.60:
        clarification_needed = True

    return {
        "timeline": [timeline_event],
        "detected_intent": intent,
        "classification_confidence": confidence,
        "extracted_entities": entities,
        "clarification_needed": clarification_needed,
    }


# 3. CUSTOMER AUTHORIZATION
def node_customer_authorization(state: SupportAgentState) -> Dict[str, Any]:
    tenant_id = state["tenant_id"]
    customer_id = state["customer_id"]

    db: Session = SessionLocal()
    try:
        cust_res = tool_get_customer(db, tenant_id=tenant_id, customer_id=customer_id)
    finally:
        db.close()

    timeline_event: WorkflowEvent = {
        "step_name": "customer_authorization",
        "timestamp": _now(),
        "status": "COMPLETED" if cust_res.success else "FAILED",
        "details": {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "authorized": cust_res.success,
        },
    }

    if not cust_res.success:
        return {
            "timeline": [timeline_event],
            "escalation_required": True,
            "escalation_reason": f"Authorization failure: customer '{customer_id}' not found in tenant '{tenant_id}'.",
            "final_response": "We could not verify your customer account under this merchant organization. Please check your account credentials.",
            "execution_status": "ESCALATED",
        }

    return {
        "timeline": [timeline_event],
        "customer_info": cust_res.data,
    }


# 4. CONTEXT RETRIEVAL
def node_context_retrieval(state: SupportAgentState) -> Dict[str, Any]:
    intent = state.get("detected_intent")
    query = state.get("customer_message", "")
    tenant_id = state["tenant_id"]

    # Retrieve context for FAQ, policies, damaged items, and payments
    retrieved: List[Dict[str, Any]] = []
    citations: List[str] = []

    res = tool_search_knowledge_base(tenant_id=tenant_id, query=query, top_k=2)
    if res.success:
        retrieved = res.data.get("results", [])
        citations = res.data.get("citations", [])

    timeline_event: WorkflowEvent = {
        "step_name": "context_retrieval",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "query": query,
            "retrieved_count": len(retrieved),
            "citations": citations,
        },
    }

    return {
        "timeline": [timeline_event],
        "retrieved_context": retrieved,
        "citations": citations,
    }


# 5. POLICY EVALUATION
def node_policy_evaluation(state: SupportAgentState) -> Dict[str, Any]:
    intent = state.get("detected_intent")
    entities = state.get("extracted_entities", {})
    order_id = entities.get("order_id")
    tenant_id = state["tenant_id"]
    customer_id = state["customer_id"]

    requires_approval = False
    eligibility_info = None

    if intent in ("refund_request", "damaged_product") and order_id:
        db: Session = SessionLocal()
        try:
            elig_res = tool_check_refund_eligibility(
                db, tenant_id=tenant_id, order_id=order_id, customer_id=customer_id
            )
            eligibility_info = elig_res.data
            requires_approval = elig_res.data.get("requires_approval", False)
        finally:
            db.close()

    timeline_event: WorkflowEvent = {
        "step_name": "policy_evaluation",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "intent": intent,
            "order_id": order_id,
            "requires_approval": requires_approval,
            "eligibility": eligibility_info,
        },
    }

    return {
        "timeline": [timeline_event],
        "requires_approval": requires_approval,
        "eligibility_info": eligibility_info,
    }


# 6. RESOLUTION PLANNING
def node_resolution_planning(state: SupportAgentState) -> Dict[str, Any]:
    intent = state.get("detected_intent")
    entities = state.get("extracted_entities", {})
    order_id = entities.get("order_id")

    planned_tools: List[Dict[str, Any]] = []
    proposed_resolution = ""

    if intent == "order_status":
        if order_id:
            planned_tools.append({"tool": "get_order", "args": {"order_id": order_id}})
            proposed_resolution = f"Retrieve verified live order status and tracking details for {order_id}."
        else:
            proposed_resolution = "Prompt customer for their Order ID to locate shipment."

    elif intent == "refund_request":
        if order_id:
            planned_tools.append({"tool": "get_order", "args": {"order_id": order_id}})
            planned_tools.append({"tool": "check_refund_eligibility", "args": {"order_id": order_id}})
            planned_tools.append({"tool": "calculate_refund_amount", "args": {"order_id": order_id}})
            if state.get("requires_approval"):
                planned_tools.append({"tool": "request_human_approval", "args": {"order_id": order_id}})
            else:
                planned_tools.append({"tool": "execute_approved_refund", "args": {"order_id": order_id}})
            proposed_resolution = f"Evaluate refund eligibility for {order_id} and execute sandbox refund or queue approval."
        else:
            proposed_resolution = "Request Order ID from customer to proceed with refund."

    elif intent == "damaged_product":
        if order_id:
            planned_tools.append({"tool": "get_order", "args": {"order_id": order_id}})
            planned_tools.append({"tool": "create_support_ticket", "args": {"order_id": order_id, "title": f"Damaged Product: {order_id}", "priority": "HIGH"}})
            if state.get("requires_approval"):
                planned_tools.append({"tool": "request_human_approval", "args": {"order_id": order_id}})
            proposed_resolution = f"Open priority damaged item ticket and evaluate replacement/refund for {order_id}."
        else:
            proposed_resolution = "Request Order ID and photo evidence description for damaged item."

    elif intent == "payment_inquiry":
        if order_id:
            planned_tools.append({"tool": "get_payment_status", "args": {"order_id": order_id}})
            proposed_resolution = f"Retrieve verified gateway payment transaction for {order_id}."
        else:
            proposed_resolution = "Provide payment troubleshooting guidance and request Order ID."

    elif intent == "general_faq":
        planned_tools.append({"tool": "search_knowledge_base", "args": {"query": state["customer_message"]}})
        proposed_resolution = "Provide verified policy answers grounded in knowledge base with citations."

    elif intent == "human_escalation":
        planned_tools.append({"tool": "escalate_to_human", "args": {"reason": "Customer requested human supervisor."}})
        proposed_resolution = "Escalate conversation to human support queue."

    timeline_event: WorkflowEvent = {
        "step_name": "resolution_planning",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "proposed_resolution": proposed_resolution,
            "planned_tools_count": len(planned_tools),
        },
    }

    return {
        "timeline": [timeline_event],
        "planned_tools": planned_tools,
        "proposed_resolution": proposed_resolution,
    }


# 7. TOOL EXECUTION
def node_tool_execution(state: SupportAgentState) -> Dict[str, Any]:
    planned = state.get("planned_tools", [])
    tenant_id = state["tenant_id"]
    customer_id = state["customer_id"]
    ticket_id = state.get("ticket_id")

    executed: List[Dict[str, Any]] = []
    order_info = None
    payment_info = None
    approval_id = None
    created_ticket_id = None

    db: Session = SessionLocal()
    try:
        for plan in planned:
            tool_name = plan["tool"]
            args = plan.get("args", {})

            if tool_name == "get_order":
                res = tool_get_order(db, tenant_id=tenant_id, order_id=args["order_id"], customer_id=customer_id, ticket_id=ticket_id)
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})
                if res.success:
                    order_info = res.data

            elif tool_name == "get_payment_status":
                res = tool_get_payment_status(db, tenant_id=tenant_id, order_id=args["order_id"], customer_id=customer_id, ticket_id=ticket_id)
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})
                if res.success:
                    payment_info = res.data

            elif tool_name == "check_refund_eligibility":
                res = tool_check_refund_eligibility(db, tenant_id=tenant_id, order_id=args["order_id"], customer_id=customer_id, ticket_id=ticket_id)
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})

            elif tool_name == "calculate_refund_amount":
                res = tool_calculate_refund_amount(db, tenant_id=tenant_id, order_id=args["order_id"], customer_id=customer_id, ticket_id=ticket_id)
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})

            elif tool_name == "create_support_ticket":
                res = tool_create_support_ticket(
                    db,
                    tenant_id=tenant_id,
                    customer_id=customer_id,
                    title=args.get("title", "Customer Support Ticket"),
                    description=state.get("customer_message", ""),
                    category="damaged_product",
                    priority="HIGH",
                    order_id=args.get("order_id"),
                )
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})
                if res.success:
                    created_ticket_id = res.data.get("ticket_id")

            elif tool_name == "escalate_to_human":
                t_id = ticket_id or created_ticket_id
                if not t_id:
                    # Create ticket first if none exists
                    t_res = tool_create_support_ticket(db, tenant_id, customer_id, "Human Escalation Request", state["customer_message"], category="escalation")
                    t_id = t_res.data.get("ticket_id")
                res = tool_escalate_to_human(db, tenant_id=tenant_id, ticket_id=t_id, reason=args.get("reason", "Customer request"))
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})

            elif tool_name == "search_knowledge_base":
                res = tool_search_knowledge_base(tenant_id=tenant_id, query=args["query"], top_k=2, ticket_id=ticket_id, db=db)
                executed.append({"tool": tool_name, "success": res.success, "data": res.data, "error": res.error})
    finally:
        db.close()

    timeline_event: WorkflowEvent = {
        "step_name": "tool_execution",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "executed_count": len(executed),
            "tools": [e["tool"] for e in executed],
        },
    }

    updates: Dict[str, Any] = {
        "timeline": [timeline_event],
        "executed_tools": executed,
    }
    if order_info:
        updates["order_info"] = order_info
    if payment_info:
        updates["payment_info"] = payment_info
    if created_ticket_id and not ticket_id:
        updates["ticket_id"] = created_ticket_id

    return updates


# 8. HUMAN APPROVAL
def node_human_approval(state: SupportAgentState) -> Dict[str, Any]:
    requires_approval = state.get("requires_approval", False)
    entities = state.get("extracted_entities", {})
    order_id = entities.get("order_id")
    tenant_id = state["tenant_id"]
    customer_id = state["customer_id"]
    ticket_id = state.get("ticket_id")

    if not requires_approval or not order_id:
        return {}

    db: Session = SessionLocal()
    approval_record = None
    try:
        # Ensure a ticket exists for approval association
        if not ticket_id:
            t_res = tool_create_support_ticket(
                db, tenant_id, customer_id, f"Refund Approval Request for {order_id}",
                f"Customer requested refund for {order_id}. Requires human approval.",
                category="refund", priority="HIGH", order_id=order_id
            )
            ticket_id = t_res.data.get("ticket_id")

        # Get calculated amount
        calc_res = tool_calculate_refund_amount(db, tenant_id, order_id, customer_id)
        amount = calc_res.data.get("amount", 0.0)
        currency = calc_res.data.get("currency", "USD")

        # Create approval request
        appr_res = tool_request_human_approval(
            db, tenant_id=tenant_id, ticket_id=ticket_id, customer_id=customer_id,
            order_id=order_id, action_type="REFUND", amount=amount, currency=currency,
            reason=f"Refund request of {currency} {amount:.2f} exceeds auto-approval threshold ($50.00)."
        )
        approval_record = appr_res.data
    finally:
        db.close()

    timeline_event: WorkflowEvent = {
        "step_name": "human_approval",
        "timestamp": _now(),
        "status": "PAUSED",
        "details": {
            "approval_id": approval_record.get("approval_id") if approval_record else None,
            "status": "PENDING_APPROVAL",
            "reason": "Threshold exceeded. Execution paused awaiting authorized human reviewer.",
        },
    }

    return {
        "timeline": [timeline_event],
        "ticket_id": ticket_id,
        "approval_id": approval_record.get("approval_id") if approval_record else None,
        "approval_status": "PENDING",
        "execution_status": "AWAITING_APPROVAL",
    }


# 9. OUTCOME VERIFICATION
def node_outcome_verification(state: SupportAgentState) -> Dict[str, Any]:
    executed = state.get("executed_tools", [])
    failures = [e for e in executed if not e.get("success")]

    verification_passed = len(failures) == 0

    timeline_event: WorkflowEvent = {
        "step_name": "outcome_verification",
        "timestamp": _now(),
        "status": "COMPLETED" if verification_passed else "FAILED",
        "details": {
            "verification_passed": verification_passed,
            "failure_count": len(failures),
            "failures": [f.get("error") for f in failures],
        },
    }

    return {
        "timeline": [timeline_event],
        "verification_passed": verification_passed,
    }


# 10. RESPONSE GENERATION
def node_response_generation(state: SupportAgentState) -> Dict[str, Any]:
    intent = state.get("detected_intent")
    order = state.get("order_info")
    payment = state.get("payment_info")
    citations = state.get("citations", [])
    approval_status = state.get("approval_status")
    approval_id = state.get("approval_id")
    executed = state.get("executed_tools", [])
    entities = state.get("extracted_entities", {})
    order_id = entities.get("order_id")

    # If already escalated or prompt injection
    if state.get("escalation_required"):
        return {
            "execution_status": "ESCALATED",
        }

    # If clarification is needed
    if state.get("clarification_needed") or (intent in ("order_status", "refund_request", "damaged_product") and not order_id):
        response_text = (
            "I would be glad to help you with that! Could you please provide your **Order ID** (for example, `ORD-1001`) "
            "so I can look up the live records in our system?"
        )
        return {
            "final_response": response_text,
            "execution_status": "COMPLETED",
        }

    # Check for tool errors (e.g., order not found or ownership mismatch)
    order_errors = [e.get("error") for e in executed if e.get("tool") == "get_order" and not e.get("success")]
    if order_errors:
        err_msg = order_errors[0]
        response_text = f"⚠️ {err_msg} Please verify your Order ID and ensure it is associated with your authenticated account."
        return {
            "final_response": response_text,
            "execution_status": "COMPLETED",
        }

    # 1. Order Status
    if intent == "order_status" and order:
        carrier_info = f" via **{order.get('carrier')}**" if order.get('carrier') else ""
        tracking_info = f"\n- **Tracking Number**: `{order.get('tracking_number')}`" if order.get('tracking_number') else ""
        delivery_info = f"\n- **Delivered At**: {order.get('delivered_at')}" if order.get('delivered_at') else ""
        
        response_text = (
            f"### Order Status for `{order.get('order_number')}`\n"
            f"- **Status**: **{order.get('status')}**{carrier_info}\n"
            f"- **Order Total**: ${order.get('total_amount', 0.0):.2f} {order.get('currency', 'USD')}"
            f"{tracking_info}{delivery_info}\n"
            f"- **Shipping Address**: {order.get('shipping_address') or 'On file'}\n\n"
            f"If you need to make changes or have questions about delivery timelines, please let me know!"
        )

    # 2. Refund Request
    elif intent == "refund_request":
        if approval_status == "PENDING":
            response_text = (
                f"### Refund Request Submitted for Review\n"
                f"Your refund request for order `{order.get('order_number') if order else order_id}` has been verified.\n\n"
                f"- **Requested Amount**: ${order.get('total_amount', 0.0):.2f}\n"
                f"- **Approval ID**: `{approval_id}`\n"
                f"- **Status**: ⏳ **Pending Human Supervisor Review**\n\n"
                f"> Because this refund amount exceeds our instant automated refund threshold ($50.00), it has been "
                f"routed to our customer support supervisor queue for authorization. You will receive an update once approved."
            )
        else:
            # Check eligibility failure
            elig_errors = [e.get("error") for e in executed if e.get("tool") == "check_refund_eligibility" and not e.get("success")]
            if elig_errors:
                response_text = f"### Refund Ineligible\n{elig_errors[0]}\n\nIf you believe this is in error, we can connect you with a human supervisor."
            else:
                response_text = (
                    f"### Refund Successfully Processed (Sandbox Simulation)\n"
                    f"Your refund for order `{order.get('order_number') if order else order_id}` has been approved and processed in sandbox mode.\n\n"
                    f"- **Amount Credited**: ${order.get('total_amount', 0.0):.2f}\n"
                    f"- **Status**: Verified by merchant gateway\n"
                    f"Funds will reflect on your original payment method in 3-5 business days."
                )

    # 3. Damaged Product
    elif intent == "damaged_product":
        ticket_id = state.get("ticket_id", "Pending")
        response_text = (
            f"### Support Ticket Opened for Damaged Item\n"
            f"We are sorry to hear that your order arrived damaged. We have opened a priority ticket for you:\n\n"
            f"- **Ticket ID**: `{ticket_id}`\n"
            f"- **Associated Order**: `{order.get('order_number') if order else order_id}`\n"
            f"- **Status**: Escalated to Fulfillment Resolution Team\n\n"
            f"We offer either an **expedited complimentary replacement** or a **full refund**. "
            f"A support specialist has been assigned to your ticket."
        )

    # 4. Payment Inquiry
    elif intent == "payment_inquiry":
        if payment:
            response_text = (
                f"### Payment Verification for `{payment.get('order_number')}`\n"
                f"- **Transaction Status**: **{payment.get('status')}**\n"
                f"- **Amount**: ${payment.get('amount', 0.0):.2f} {payment.get('currency', 'USD')}\n"
                f"- **Method**: {payment.get('payment_method')} (Card ending `{payment.get('card_last4') or '****'}`)\n"
            )
            if payment.get("failure_reason"):
                response_text += f"- **Decline Reason**: `{payment.get('failure_reason')}`\n\n"
                response_text += "Please contact your card-issuing bank or try an alternate payment method."
            else:
                response_text += "\nYour payment was successfully settled and captured by our merchant gateway."
        else:
            response_text = "I checked our records and found no captured payment associated with that reference."

    # 5. General FAQ
    else:
        retrieved = state.get("retrieved_context", [])
        if retrieved:
            best_chunk = retrieved[0]
            response_text = best_chunk.get("content", "")
            if citations:
                response_text += f"\n\n**Sources:**\n" + "\n".join(f"- {c}" for c in citations)
        else:
            response_text = (
                "Thank you for contacting customer support. For full details on our policies, shipping, and returns, "
                "please let me know what specific topic I can assist with."
            )

    return {
        "final_response": response_text,
        "execution_status": "AWAITING_APPROVAL" if approval_status == "PENDING" else "COMPLETED",
    }


# 11. ESCALATION
def node_escalation(state: SupportAgentState) -> Dict[str, Any]:
    reason = state.get("escalation_reason", "Complex or ambiguous request requiring human escalation.")
    ticket_id = state.get("ticket_id")
    tenant_id = state["tenant_id"]
    customer_id = state["customer_id"]

    db: Session = SessionLocal()
    try:
        if not ticket_id:
            t_res = tool_create_support_ticket(db, tenant_id, customer_id, "Human Support Escalation", state["customer_message"], category="escalation", priority="HIGH")
            ticket_id = t_res.data.get("ticket_id")

        tool_escalate_to_human(db, tenant_id=tenant_id, ticket_id=ticket_id, reason=reason)
    finally:
        db.close()

    timeline_event: WorkflowEvent = {
        "step_name": "escalation",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {"ticket_id": ticket_id, "reason": reason},
    }

    final_resp = (
        f"### Escalated to Human Support\n"
        f"Your request has been routed to a human support specialist.\n\n"
        f"- **Ticket ID**: `{ticket_id}`\n"
        f"- **Reason**: {reason}\n\n"
        f"A support agent will review your case and follow up shortly."
    )

    return {
        "timeline": [timeline_event],
        "ticket_id": ticket_id,
        "final_response": final_resp,
        "execution_status": "ESCALATED",
    }


# 12. AUDIT AND COMPLETION
def node_audit_and_completion(state: SupportAgentState) -> Dict[str, Any]:
    timeline_event: WorkflowEvent = {
        "step_name": "audit_and_completion",
        "timestamp": _now(),
        "status": "COMPLETED",
        "details": {
            "execution_status": state.get("execution_status", "COMPLETED"),
            "approval_status": state.get("approval_status", "NONE"),
        },
    }

    # Persist message to conversation if conversation_id exists
    conv_id = state.get("conversation_id")
    resp_text = state.get("final_response", "")
    if conv_id and resp_text:
        db: Session = SessionLocal()
        try:
            add_message_to_conversation(
                db=db,
                conversation_id=conv_id,
                sender_type="agent",
                content=resp_text,
                metadata={
                    "intent": state.get("detected_intent"),
                    "confidence": state.get("classification_confidence"),
                    "citations": state.get("citations", []),
                    "execution_status": state.get("execution_status"),
                    "approval_id": state.get("approval_id"),
                }
            )
        finally:
            db.close()

    return {
        "timeline": [timeline_event],
    }
