import React, { useEffect, useState } from "react";
import type { TicketDetail } from "../types";
import { fetchTicketDetail } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import {
  ArrowLeft,
  Package,
  CreditCard,
  Terminal,
  FileCheck2,
  AlertTriangle,
  User,
  Clock,
  CheckCircle2,
} from "lucide-react";

interface TicketDetailPageProps {
  ticketId: string;
  onBack: () => void;
}

export const TicketDetailPage: React.FC<TicketDetailPageProps> = ({ ticketId, onBack }) => {
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTicketDetail(ticketId)
      .then(setTicket)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [ticketId]);

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading ticket details...</div>;
  }

  if (error || !ticket) {
    return (
      <div className="p-8 space-y-4">
        <button onClick={onBack} className="btn-secondary text-xs">
          <ArrowLeft className="h-4 w-4" /> Back to Tickets
        </button>
        <div className="rounded-lg border border-rose-500/30 bg-rose-950/20 p-4 text-xs text-rose-300">
          {error || "Ticket not found"}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      {/* Back button and Header */}
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="btn-secondary text-xs" id="btn-back-tickets">
          <ArrowLeft className="h-4 w-4" /> Back to Tickets
        </button>
        <div className="flex items-center gap-2">
          <StatusBadge status={ticket.status} />
          <span className="text-xs text-slate-400">Priority: <strong>{ticket.priority}</strong></span>
        </div>
      </div>

      <div className="glass-panel p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/60 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-indigo-400">{ticket.ticket_number}</span>
              <h2 className="text-lg font-bold text-white">{ticket.title}</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Customer: <strong className="text-slate-200">{ticket.customer_name || ticket.customer_id}</strong> •{" "}
              {ticket.customer_email || "Email on file"}
            </p>
          </div>
          <div className="text-xs text-slate-400">
            Created: {new Date(ticket.created_at).toLocaleString()}
          </div>
        </div>

        {/* Description / Customer Issue */}
        <div className="space-y-1">
          <h4 className="text-xs font-semibold text-slate-300">Customer Issue:</h4>
          <div className="rounded-lg bg-slate-900/60 p-3 text-xs text-slate-200 whitespace-pre-wrap">
            {ticket.description}
          </div>
        </div>

        {/* Resolution Summary if resolved/escalated */}
        {ticket.resolution_summary && (
          <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-3 text-xs text-emerald-300">
            <strong>Resolution Summary:</strong> {ticket.resolution_summary}
          </div>
        )}
      </div>

      {/* Grid: Order Info & Approvals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Order Details */}
        <div className="glass-panel p-5 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm text-white border-b border-slate-700/60 pb-2">
            <Package className="h-4 w-4 text-cyan-400" />
            Verified Order Records
          </div>

          {ticket.order_details ? (
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Order Number:</span>
                <span className="font-mono font-bold text-slate-200">{ticket.order_details.order_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Order Status:</span>
                <StatusBadge status={ticket.order_details.status} />
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Order Total:</span>
                <span className="font-bold text-white">${ticket.order_details.total_amount.toFixed(2)}</span>
              </div>
              {ticket.order_details.refunded_amount > 0 && (
                <div className="flex justify-between text-rose-300">
                  <span>Refunded Amount:</span>
                  <span className="font-bold">-${ticket.order_details.refunded_amount.toFixed(2)}</span>
                </div>
              )}
              {ticket.order_details.tracking_number && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Tracking Number:</span>
                  <span className="font-mono text-cyan-300">{ticket.order_details.tracking_number}</span>
                </div>
              )}

              {ticket.order_details.items && ticket.order_details.items.length > 0 && (
                <div className="pt-2 border-t border-slate-700/40">
                  <span className="text-[11px] font-semibold text-slate-400">Items Ordered:</span>
                  <div className="mt-1 space-y-1">
                    {ticket.order_details.items.map((it, idx) => (
                      <div key={idx} className="flex justify-between text-[11px] text-slate-300 bg-slate-900/40 p-1.5 rounded">
                        <span>{it.name} (x{it.quantity})</span>
                        <span>${(it.unit_price * it.quantity).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-500 py-4">No order directly attached to this ticket.</div>
          )}
        </div>

        {/* Approvals */}
        <div className="glass-panel p-5 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm text-white border-b border-slate-700/60 pb-2">
            <FileCheck2 className="h-4 w-4 text-amber-400" />
            Associated Approval Requests
          </div>

          {ticket.approvals && ticket.approvals.length > 0 ? (
            <div className="space-y-3 text-xs">
              {ticket.approvals.map((appr) => (
                <div key={appr.id} className="rounded-lg border border-slate-700 bg-slate-900/60 p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-indigo-300">{appr.action_type}</span>
                    <StatusBadge status={appr.status} />
                  </div>
                  <div className="text-sm font-bold text-white">${appr.amount.toFixed(2)}</div>
                  <p className="text-slate-400 text-[11px]">{appr.reason}</p>
                  {appr.reviewed_by && (
                    <div className="pt-1 text-[10px] text-slate-500">
                      Reviewed by: {appr.reviewed_by} • Notes: {appr.review_notes || "None"}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-xs text-slate-500 py-4">No approval requests generated for this ticket.</div>
          )}
        </div>
      </div>

      {/* Tool Executions Trace */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center gap-2 font-bold text-sm text-white border-b border-slate-700/60 pb-3">
          <Terminal className="h-4 w-4 text-emerald-400" />
          Verified Backend Tool Executions for this Ticket ({ticket.tool_executions?.length || 0})
        </div>

        {ticket.tool_executions && ticket.tool_executions.length > 0 ? (
          <div className="space-y-2">
            {ticket.tool_executions.map((te) => (
              <div key={te.id} className="rounded-lg border border-slate-700/80 bg-slate-900/80 p-3 font-mono text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-400">{te.tool_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-400">{te.duration_ms.toFixed(1)} ms</span>
                    <StatusBadge status={te.status} />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px]">
                  <div>
                    <span className="text-slate-500 block mb-0.5">Input Arguments:</span>
                    <pre className="rounded bg-slate-950 p-2 text-slate-300 overflow-x-auto">
                      {JSON.stringify(te.input_args, null, 2)}
                    </pre>
                  </div>
                  <div>
                    <span className="text-slate-500 block mb-0.5">Output Result:</span>
                    <pre className="rounded bg-slate-950 p-2 text-slate-300 overflow-x-auto">
                      {JSON.stringify(te.output_result, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-slate-500 py-4">No tools recorded yet for this ticket.</div>
        )}
      </div>
    </div>
  );
};
