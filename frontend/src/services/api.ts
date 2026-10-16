import type { AuthToken, DemoUser, SupportTicket, TicketDetail, ApprovalItem, DashboardMetrics, ToolMetric, AuditEventItem } from "../types";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "/api/v1";

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("support_token");
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  // Default to demo John Doe header if not stored
  return {
    "X-Tenant-ID": "tenant_nova",
    "X-User-ID": "usr-nova-cust1",
    "X-User-Role": "customer",
  };
}

export async function fetchDemoUsers(): Promise<DemoUser[]> {
  const res = await fetch(`${API_BASE}/auth/demo-users`);
  if (!res.ok) throw new Error("Failed to fetch demo users");
  return res.json();
}

export async function switchUser(userId: string): Promise<AuthToken> {
  const res = await fetch(`${API_BASE}/auth/switch-demo-user/${userId}`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to switch demo user");
  const data: AuthToken = await res.json();
  localStorage.setItem("support_token", data.access_token);
  localStorage.setItem("support_user", JSON.stringify(data));
  return data;
}

export async function sendChatMessage(message: string, conversationId?: string, ticketId?: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ message, conversation_id: conversationId, ticket_id: ticketId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to process chat message");
  }
  return res.json();
}

export async function fetchTickets(status?: string): Promise<SupportTicket[]> {
  const url = status ? `${API_BASE}/tickets?status=${status}` : `${API_BASE}/tickets`;
  const res = await fetch(url, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch tickets");
  return res.json();
}

export async function fetchOrders(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/orders`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch orders");
  return res.json();
}

export async function fetchOrder(orderId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/orders/${orderId}`, { headers: getAuthHeader() });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Order ${orderId} not found`);
  }
  return res.json();
}

export async function fetchTicketDetail(ticketId: string): Promise<TicketDetail> {
  const res = await fetch(`${API_BASE}/tickets/${ticketId}`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch ticket detail");
  return res.json();
}

export async function fetchApprovals(status?: string): Promise<ApprovalItem[]> {
  const url = status ? `${API_BASE}/approvals?status=${status}` : `${API_BASE}/approvals`;
  const res = await fetch(url, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch approvals");
  return res.json();
}

export async function submitApprovalDecision(approvalId: string, decision: "APPROVED" | "REJECTED", reviewNotes: string) {
  const res = await fetch(`${API_BASE}/approvals/${approvalId}/action`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeader(),
    },
    body: JSON.stringify({ decision, review_notes: reviewNotes }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to execute approval decision");
  }
  return res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/analytics/dashboard`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch dashboard metrics");
  return res.json();
}

export async function fetchToolMetrics(): Promise<ToolMetric[]> {
  const res = await fetch(`${API_BASE}/analytics/tools`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch tool metrics");
  return res.json();
}

export async function fetchAuditTrail(limit = 50): Promise<AuditEventItem[]> {
  const res = await fetch(`${API_BASE}/audit?limit=${limit}`, { headers: getAuthHeader() });
  if (!res.ok) throw new Error("Failed to fetch audit trail");
  return res.json();
}
