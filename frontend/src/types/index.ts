export type UserRole = "customer" | "support_agent" | "approver" | "admin";

export interface DemoUser {
  user_id: string;
  tenant_id: string;
  tenant_name: string;
  email: string;
  full_name: string;
  role: UserRole;
  customer_id?: string;
  description: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  tenant_id: string;
  user_id: string;
  role: UserRole;
  email: string;
  full_name: string;
  customer_id?: string;
}

export interface WorkflowEvent {
  step_name: string;
  timestamp: string;
  status: "STARTED" | "COMPLETED" | "FAILED" | "PAUSED";
  details: Record<string, any>;
}

export interface ChatMessage {
  id: string;
  sender_type: "customer" | "agent" | "system";
  content: string;
  timestamp: string;
  intent?: string;
  confidence?: number;
  citations?: string[];
  timeline?: WorkflowEvent[];
  executed_tools?: any[];
  requires_approval?: boolean;
  approval_id?: string;
}

export interface SupportTicket {
  id: string;
  ticket_number: string;
  customer_id: string;
  order_id?: string;
  title: string;
  description: string;
  status: "OPEN" | "IN_PROGRESS" | "WAITING_APPROVAL" | "RESOLVED" | "CLOSED" | "ESCALATED";
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  category: string;
  resolution_summary?: string;
  created_at: string;
  updated_at: string;
}

export interface TicketDetail extends SupportTicket {
  customer_name?: string;
  customer_email?: string;
  order_details?: {
    id: string;
    order_number: string;
    status: string;
    total_amount: number;
    refunded_amount: number;
    tracking_number?: string;
    carrier?: string;
    items: Array<{ sku: string; name: string; quantity: number; unit_price: number }>;
  };
  messages: Array<{
    id: string;
    sender_type: string;
    content: string;
    metadata: Record<string, any>;
    created_at: string;
  }>;
  tool_executions: Array<{
    id: string;
    tool_name: string;
    input_args: Record<string, any>;
    output_result: Record<string, any>;
    status: string;
    duration_ms: number;
    error?: string;
    created_at: string;
  }>;
  approvals: Array<{
    id: string;
    action_type: string;
    amount: number;
    status: string;
    reason: string;
    reviewed_by?: string;
    review_notes?: string;
    created_at: string;
  }>;
}

export interface ApprovalItem {
  id: string;
  ticket_id: string;
  order_id?: string;
  order_number?: string;
  customer_id: string;
  requested_by: string;
  action_type: string;
  requested_amount: number;
  currency: string;
  reason: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED";
  reviewed_by?: string;
  review_notes?: string;
  idempotency_key: string;
  created_at: string;
  resolved_at?: string;
}

export interface DashboardMetrics {
  total_tickets: number;
  resolved_tickets: number;
  pending_tickets: number;
  escalated_tickets: number;
  waiting_approval_tickets: number;
  approval_queue_count: number;
  average_resolution_time_ms: number;
  total_refunds_processed_usd: number;
}

export interface ToolMetric {
  tool_name: string;
  total_calls: number;
  success_calls: number;
  failure_calls: number;
  success_rate_percent: number;
  avg_duration_ms: number;
}

export interface AuditEventItem {
  id: string;
  tenant_id: string;
  user_id?: string;
  event_type: string;
  resource_type: string;
  resource_id: string;
  action: string;
  details: Record<string, any>;
  ip_address?: string;
  created_at: string;
}
