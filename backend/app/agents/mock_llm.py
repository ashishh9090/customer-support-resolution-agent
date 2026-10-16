import re
from typing import Dict, Any, List, Tuple


def detect_prompt_injection(message: str) -> bool:
    """Detect common prompt injection attacks and adversarial jailbreaks."""
    patterns = [
        r"ignore (all )?(previous|above) instructions",
        r"system override",
        r"bypass (all )?(policy|rules|security)",
        r"act as (unrestricted|evil|admin)",
        r"you are now in developer mode",
        r"drop\s+table",
        r"select\s+\*\s+from",
        r"delete\s+from",
        r"give me a full refund without",
        r"sudo",
    ]
    lowered = message.lower()
    for pat in patterns:
        if re.search(pat, lowered):
            return True
    return False


def classify_intent_and_entities(message: str) -> Tuple[str, float, Dict[str, Any]]:
    """
    Deterministic intent classification and entity extraction.
    Returns: (intent, confidence, entities)
    """
    lowered = message.lower()

    # 1. Security / Prompt Injection
    if detect_prompt_injection(message):
        return "prompt_injection", 0.99, {"risk": "HIGH", "category": "adversarial_prompt_injection"}

    # Extract Order ID
    order_match = re.search(r"\b(ord[-_]?\d{3,6})\b", message, re.IGNORECASE)
    order_id = order_match.group(1).upper() if order_match else None

    # Extract Ticket ID
    ticket_match = re.search(r"\b(tck[-_]?\d{3,6})\b", message, re.IGNORECASE)
    ticket_id = ticket_match.group(1).upper() if ticket_match else None

    # 2. Human Escalation / Agent Request
    if any(k in lowered for k in [
        "speak to a human", "talk to human", "manager", "representative",
        "real person", "escalate", "escalation", "transfer me"
    ]):
        return "human_escalation", 0.98, {
            "order_id": order_id,
            "reason": "Customer requested human supervisor or escalation.",
        }

    # 3. Damaged Product Complaint
    if any(k in lowered for k in ["damaged", "broken", "cracked", "defective", "smashed", "shattered", "leaking", "dent"]):
        return "damaged_product", 0.95, {
            "order_id": order_id,
            "ticket_id": ticket_id,
            "issue": "product_damage",
        }

    # 4. Refund / Return Request / Cancellation
    if any(k in lowered for k in ["refund", "return my", "money back", "cancel order", "cancel", "want my money", "send it back"]):
        return "refund_request", 0.96, {
            "order_id": order_id,
            "ticket_id": ticket_id,
            "action": "refund",
        }

    # 5. Payment Inquiry / Failure / Billing
    if any(k in lowered for k in [
        "payment failed", "card declined", "charged twice", "charge declined",
        "payment error", "billing issue", "double charged", "payment went through",
        "bank authorization", "card statement", "declined"
    ]):
        return "payment_inquiry", 0.93, {
            "order_id": order_id,
            "issue": "payment_failure",
        }

    # 6. Order Status Inquiry (including when order_id is present)
    if any(k in lowered for k in [
        "where is my order", "track", "shipping status", "order status",
        "delivery status", "package arrived", "when will it arrive", "has it shipped",
        "been processed", "status of order", "status on order", "status of my order"
    ]) or (order_id is not None and any(k in lowered for k in ["status", "check", "arrive", "where", "tell me", "processed", "order"])):
        return "order_status", 0.95, {
            "order_id": order_id,
            "ticket_id": ticket_id,
        }

    # 7. General FAQ / Policy
    if any(k in lowered for k in [
        "policy", "shipping options", "delivery timelines", "how do i", "warranty",
        "international shipping", "faq", "accepted payment", "payment methods",
        "change my delivery address", "change address"
    ]):
        return "general_faq", 0.92, {
            "query": message,
        }

    # 8. Ambiguous or Unknown (e.g. short greetings, greetings without order)
    if len(message.strip().split()) <= 2 and not order_id:
        return "unknown_ambiguous", 0.40, {}

    # Default fallback to general FAQ
    return "general_faq", 0.70, {"query": message}
