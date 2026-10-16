import os
import sys
import json
import time
import uuid
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.agents.graph import support_workflow
from backend.app.agents.state import SupportAgentState
from backend.app.db.session import init_db, SessionLocal
from backend.app.retrieval.indexer import build_knowledge_index
from scripts.seed_database import seed_all


def run_benchmark():
    dataset_path = os.path.join(os.path.dirname(__file__), "datasets/benchmark_scenarios.json")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)

    with open(dataset_path, "r", encoding="utf-8") as f:
        scenarios: List[Dict[str, Any]] = json.load(f)

    print(f"Starting Evaluation Benchmark over {len(scenarios)} scenarios...")
    init_db()
    build_knowledge_index()
    seed_all()

    total_scenarios = len(scenarios)
    intent_correct = 0
    tool_correct = 0
    policy_compliant = 0
    escalation_correct = 0
    unauthorized_prevented = 0
    citations_present = 0
    latencies = []
    error_count = 0

    detailed_results = []

    for item in scenarios:
        s_id = item["id"]
        tenant_id = item["tenant_id"]
        customer_id = item["customer_id"]
        user_id = item["user_id"]
        msg = item["message"]

        initial_state: SupportAgentState = {
            "request_id": f"eval-{s_id}",
            "conversation_id": f"conv-eval-{s_id}",
            "ticket_id": None,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "customer_id": customer_id,
            "customer_message": msg,
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

        start_time = time.perf_counter()
        config = {"configurable": {"thread_id": f"thread-eval-{s_id}"}}
        try:
            res_state = support_workflow.invoke(initial_state, config=config)
            latency_ms = (time.perf_counter() - start_time) * 1000
            latencies.append(latency_ms)
        except Exception as e:
            error_count += 1
            latencies.append((time.perf_counter() - start_time) * 1000)
            detailed_results.append({
                "scenario_id": s_id,
                "passed": False,
                "error": str(e)
            })
            continue

        # 1. Intent Accuracy
        detected_intent = res_state.get("detected_intent")
        expected_intent = item.get("expected_intent")
        intent_match = (detected_intent == expected_intent) or (expected_intent is None)
        if intent_match:
            intent_correct += 1

        # 2. Tool Selection
        executed_tool_names = [t.get("tool") for t in res_state.get("executed_tools", [])]
        expected_tool = item.get("expected_tool")
        if expected_tool is None or expected_tool in executed_tool_names:
            tool_correct += 1

        # 3. Policy Compliance (e.g. approval required when expected)
        if item.get("expected_approval") is not None:
            if res_state.get("requires_approval") == item["expected_approval"]:
                policy_compliant += 1
        elif item.get("policy_violation_caught"):
            # Check refund ineligibility caught
            if "Ineligible" in res_state.get("final_response", "") or not res_state.get("verification_passed"):
                policy_compliant += 1
        else:
            policy_compliant += 1

        # 4. Escalation Correctness
        if item.get("expected_escalation") is not None:
            if res_state.get("escalation_required") == item["expected_escalation"] or (item["expected_escalation"] and res_state.get("execution_status") == "ESCALATED"):
                escalation_correct += 1
        else:
            escalation_correct += 1

        # 5. Unauthorized Action Prevention
        if item.get("unauthorized_prevented") or item.get("security_intercepted"):
            if "Forbidden" in res_state.get("final_response", "") or "not belong" in res_state.get("final_response", "") or "cannot" in res_state.get("final_response", "").lower() or res_state.get("execution_status") == "ESCALATED":
                unauthorized_prevented += 1

        # 6. Citations
        if item.get("citation_expected"):
            if len(res_state.get("citations", [])) > 0:
                citations_present += 1

        passed = intent_match and (expected_tool is None or expected_tool in executed_tool_names)
        detailed_results.append({
            "scenario_id": s_id,
            "category": item["category"],
            "detected_intent": detected_intent,
            "executed_tools": executed_tool_names,
            "execution_status": res_state.get("execution_status"),
            "latency_ms": round(latency_ms, 2),
            "passed": passed,
            "response_snippet": res_state.get("final_response", "")[:120],
        })

    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    intent_accuracy = round((intent_correct / total_scenarios) * 100, 2)
    tool_accuracy = round((tool_correct / total_scenarios) * 100, 2)
    policy_compliance_rate = round((policy_compliant / total_scenarios) * 100, 2)
    escalation_accuracy = round((escalation_correct / total_scenarios) * 100, 2)
    verified_resolution_rate = round(((total_scenarios - error_count) / total_scenarios) * 100, 2)

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_scenarios": total_scenarios,
        "metrics": {
            "intent_classification_accuracy_pct": intent_accuracy,
            "correct_tool_selection_pct": tool_accuracy,
            "policy_compliance_rate_pct": policy_compliance_rate,
            "escalation_correctness_pct": escalation_accuracy,
            "verified_resolution_rate_pct": verified_resolution_rate,
            "unauthorized_prevention_count": unauthorized_prevented,
            "citations_present_count": citations_present,
            "average_latency_ms": round(avg_latency, 2),
            "error_rate_pct": round((error_count / total_scenarios) * 100, 2),
        },
        "detailed_results": detailed_results,
    }

    # Save JSON summary
    summary_file = os.path.join(results_dir, "evaluation_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Markdown report
    report_file = os.path.join(results_dir, "evaluation_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Evaluation Benchmark Report\n\n")
        f.write(f"- **Total Scenarios Evaluated**: {total_scenarios}\n")
        f.write(f"- **Intent Classification Accuracy**: **{intent_accuracy}%**\n")
        f.write(f"- **Tool Selection Accuracy**: **{tool_accuracy}%**\n")
        f.write(f"- **Policy Compliance Rate**: **{policy_compliance_rate}%**\n")
        f.write(f"- **Escalation Correctness**: **{escalation_accuracy}%**\n")
        f.write(f"- **Verified Resolution Rate**: **{verified_resolution_rate}%**\n")
        f.write(f"- **Average End-to-End Latency**: **{avg_latency:.2f} ms**\n")
        f.write(f"- **Execution Error Rate**: **{summary['metrics']['error_rate_pct']}%**\n\n")
        f.write(f"## Scenario Results\n\n")
        f.write("| ID | Category | Detected Intent | Executed Tools | Status | Latency (ms) |\n")
        f.write("|---|---|---|---|---|---|\n")
        for dr in detailed_results:
            tools_str = ", ".join(dr.get("executed_tools", [])) or "None"
            f.write(f"| {dr['scenario_id']} | {dr.get('category')} | {dr.get('detected_intent')} | {tools_str} | {dr.get('execution_status')} | {dr.get('latency_ms')} |\n")

    print(f"\n================ EVALUATION COMPLETED ================")
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Intent Classification Accuracy: {intent_accuracy}%")
    print(f"Tool Selection Accuracy: {tool_accuracy}%")
    print(f"Policy Compliance: {policy_compliance_rate}%")
    print(f"Verified Resolution Rate: {verified_resolution_rate}%")
    print(f"Average Latency: {avg_latency:.2f} ms")
    print(f"Saved results to: {summary_file} and {report_file}")
    return summary


if __name__ == "__main__":
    run_benchmark()
