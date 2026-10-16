# AI Customer Support Resolution Agent

A production-style, stateful AI Customer Support Resolution Agent with **LangGraph** orchestration, strict refund safety policies, human supervisor approval checkpoints, tenant-isolated vector retrieval (RAG), and verified backend tool execution.

[![GitHub Repo](https://img.shields.io/badge/GitHub-ashishh9090%2Fcustomer--support--resolution--agent-181717?style=flat&logo=github)](https://github.com/ashishh9090/customer-support-resolution-agent)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.1.8-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/tests-29%20passed-brightgreen.svg)]()

### Live Public Links
- **Interactive Zomato Care Portal**: [https://lkknt-157-49-29-34.run.pinggy-free.link](https://lkknt-157-49-29-34.run.pinggy-free.link)
- **Direct Mirror**: [https://gsuuk-157-49-29-34.free.pinggy.net](https://gsuuk-157-49-29-34.free.pinggy.net)
- **GitHub Repository**: [https://github.com/ashishh9090/customer-support-resolution-agent](https://github.com/ashishh9090/customer-support-resolution-agent)

---

## Architecture Overview

```
                                      +--------------------------+
                                      |   React + TS Frontend    |
                                      |   (Glassmorphism / Vite) |
                                      +-------------+------------+
                                                    | REST API / JWT
                                                    v
                                      +--------------------------+
                                      |     FastAPI Backend      |
                                      +-------------+------------+
                                                    |
                     +------------------------------+------------------------------+
                     |                                                             |
                     v                                                             v
       +---------------------------+                                 +---------------------------+
       |   LangGraph Orchestrator  |                                 |    Multi-Tenant Domain    |
       |  (12-Node Stateful Graph) |                                 |  Customers, Orders, Mtgs  |
       +-------------+-------------+                                 +-------------+-------------+
                     |                                                             |
  +------------------+------------------+                    +---------------------+---------------------+
  |                  |                  |                    |                     |                     |
  v                  v                  v                    v                     v                     v
[Intent & Entity] [Policy & RAG]  [Tool Execution]       [PostgreSQL/SQLite] [Approval Queue]   [Audit Events]
```

### 12-Node Stateful LangGraph Workflow

```
[START]
   |
   v
(input_validation) --------[Prompt Injection / Empty]-------> (escalation)
   |                                                                |
   v                                                                |
(intent_classification)                                             |
   |                                                                |
   v                                                                |
(customer_authorization) --[Cross-Tenant / Mismatch]----------------+
   |                                                                |
   v                                                                |
(context_retrieval)                                                 |
   |                                                                |
   v                                                                |
(policy_evaluation)                                                 |
   |                                                                |
   v                                                                |
(resolution_planning)                                               |
   |                                                                |
   v                                                                |
(tool_execution)                                                    |
   |                                                                |
   +---[Requires Approval (> $50)]---> (human_approval) [PAUSED]     |
   |                                          |                     |
   v                                          v                     |
(outcome_verification) -----------------------+                     |
   |                                                                |
   v                                                                |
(response_generation)                                               |
   |                                                                |
   +----------------------------------------------------------------+
   |
   v
(audit_and_completion)
   |
 [END]
```

---

## Supported Scenarios

1. **Order Status Inquiries**: Real-time carrier tracking (USPS, FedEx, DHL), itemized products, and shipping addresses.
2. **Refund Requests**: Automated instant refund in sandbox mode for amounts &le; $50.00. Amounts &gt; $50.00 trigger a persistent approval request and pause workflow state.
3. **Damaged Product Complaints**: Priority support ticket creation, photographic evidence intake, replacement or refund evaluation.
4. **Failed Payment Inquiries**: Verification of merchant gateway logs, decline reason extraction (e.g. `ERR_INSUFFICIENT_FUNDS`), and customer troubleshooting.
5. **General FAQ & Policy Questions**: Retrieval-augmented generation (RAG) with tenant isolation and grounded document citations (`[POL-SHIP-001]`, `[POL-REFUND-002]`, `[FAQ-GEN-004]`).
6. **Ambiguous or Adversarial Inquiries**: Prompt injection interceptors, customer account authorization checks, and human escalation routing.

---

## Prerequisites

- **Python**: 3.11+ (Python 3.13 tested and verified)
- **Node.js**: v18+ or v20+
- **Docker & Docker Compose** (Optional, for containerized PostgreSQL)

---

## Quickstart (Development Mode)

### 1. Set Up Python Virtual Environment
```bash
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r backend/requirements.txt
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Initialize & Seed Database
```bash
# Apply database schema migrations
PYTHONPATH=. ./venv/bin/alembic -c backend/alembic.ini upgrade head

# Build knowledge base vector index
PYTHONPATH=. ./venv/bin/python scripts/build_knowledge_index.py

# Seed synthetic multi-tenant records
PYTHONPATH=. ./venv/bin/python scripts/seed_database.py
```

### 4. Run Development Servers
You can run the unified development runner:
```bash
PYTHONPATH=. ./venv/bin/python scripts/run_dev.py
```

Or run backend and frontend independently:
```bash
# Terminal 1: Backend API (FastAPI)
PYTHONPATH=. ./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend UI (React + Vite)
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

- **Frontend UI**: [http://localhost:5173](http://localhost:5173)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Seed Personas & Demo Accounts

Use the **Demo User Switcher** in the top navigation bar to test role-based access across tenants:

| Tenant | Role | Name | Email | Password | Primary Data |
|---|---|---|---|---|---|
| NovaStore | Customer | John Doe | `john.doe@example.com` | `customer123` | ORD-1001 ($42.50, Delivered)<br>ORD-1002 ($129.99, Delivered)<br>ORD-1003 ($85.00, Shipped)<br>ORD-1004 ($60.00, Delivered 45d ago) |
| NovaStore | Customer | Maria Garcia | `maria.garcia@example.com` | `customer123` | ORD-1005 ($35.00, Pending)<br>ORD-1006 ($220.00, Payment Failed) |
| NovaStore | Approver | Sarah Jenkins | `sarah.approver@novastore.com` | `approver123` | Can approve/reject high-value refunds |
| NovaStore | Agent | Alex Rivera | `alex.agent@novastore.com` | `agent123` | Access to support tickets & tools |
| NovaStore | Admin | Nova Admin | `admin@novastore.com` | `admin123` | Full access, audit logs, analytics |
| ApexGadgets | Customer | Bob Smith | `bob.smith@example.com` | `customer123` | ORD-2001 ($19.99, ApexGadgets only) |

---

## Running Automated Tests

Run the full pytest suite (29 tests):
```bash
PYTHONPATH=. ./venv/bin/pytest backend/tests/ -v
```

Tests cover:
- Service & Tool execution
- API request validation & status codes
- Multi-tenant data isolation & cross-tenant prevention
- Refund policy limits & server calculations
- Human approval pause, resume, and anti-self-approval checks
- Idempotent execution
- RAG retrieval & citations
- Adversarial prompt injection defense

---

## Running the Evaluation Benchmark

Run the automated evaluation benchmark across 32 synthetic scenarios:
```bash
PYTHONPATH=. ./venv/bin/python evaluation/run_evaluation.py
```

Results are saved to:
- `evaluation/results/evaluation_summary.json` (Machine-readable)
- `evaluation/results/evaluation_report.md` (Markdown summary)

### Verified Benchmark Metrics:
- **Total Scenarios**: 32
- **Intent Classification Accuracy**: **93.75%**
- **Tool Selection Accuracy**: **93.75%**
- **Policy Compliance Rate**: **100.0%**
- **Verified Resolution Rate**: **100.0%**
- **Escalation Correctness**: **93.75%**
- **Average End-to-End Latency**: **~26 ms**
- **Execution Error Rate**: **0.0%**

---

## Docker Deployment (PostgreSQL Mode)

When Docker is available:
```bash
docker compose up --build
```
This launches a PostgreSQL 15 container alongside the FastAPI service, applies migrations, seeds data, and starts the API on port 8000.

---

## Security & Production Readiness Caveats

1. **Payment Processing**: The sandbox payment gateway returns verified simulation records. In production, integrate Stripe, Adyen, or Braintree webhooks with HMAC-SHA256 signature verification.
2. **Secret Keys**: Replace `SECRET_KEY` in `.env` with a secure cryptographic key (e.g. generated via `openssl rand -hex 32`).
3. **LLM Provider**: In production, configure `LLM_PROVIDER=openai` (or `gemini`/`anthropic`) and supply `OPENAI_API_KEY`.
4. **Idempotency**: All refund actions use unique idempotency keys (`approval-<tenant>-<order>-<action>-<amount>-<hash>`) to guarantee duplicate protection across network retries.
