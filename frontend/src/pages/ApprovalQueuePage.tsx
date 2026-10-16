import React, { useEffect, useState } from "react";
import type { ApprovalItem } from "../types";
import { fetchApprovals, submitApprovalDecision } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import {
  CheckSquare,
  Check,
  X,
  AlertCircle,
  Clock,
  ShieldCheck,
  DollarSign,
  Package,
} from "lucide-react";

export const ApprovalQueuePage: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewNotes, setReviewNotes] = useState<Record<string, string>>({});
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [processingId, setProcessingId] = useState<string | null>(null);

  const loadApprovals = () => {
    setLoading(true);
    fetchApprovals()
      .then(setApprovals)
      .catch((err) => setActionError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleDecision = async (approvalId: string, decision: "APPROVED" | "REJECTED") => {
    setActionError(null);
    setActionSuccess(null);
    setProcessingId(approvalId);

    const notes = reviewNotes[approvalId] || (decision === "APPROVED" ? "Approved by supervisor" : "Rejected");

    try {
      await submitApprovalDecision(approvalId, decision, notes);
      setActionSuccess(`Successfully marked request as ${decision}.`);
      loadApprovals();
    } catch (err: any) {
      setActionError(err.message || "Failed to execute decision");
    } finally {
      setProcessingId(null);
    }
  };

  const pendingList = approvals.filter((a) => a.status === "PENDING");
  const historyList = approvals.filter((a) => a.status !== "PENDING");

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <CheckSquare className="h-5 w-5 text-[#E23744]" />
          <h2 className="text-xl font-bold text-white font-['Outfit']">Zomato Care | Supervisor Approval Center</h2>
          <span className="rounded-full bg-[#E23744]/20 px-2 py-0.5 text-[10px] font-bold text-[#FF6B77] border border-[#E23744]/40">
            {pendingList.length} PENDING
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Review high-value refunds (&gt; $50.00), catering adjustments, and policy overrides with full audit accountability.
        </p>
      </div>

      {actionSuccess && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-950/20 p-3 text-xs text-emerald-300 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          {actionSuccess}
        </div>
      )}

      {actionError && (
        <div className="rounded-lg border border-rose-500/30 bg-rose-950/20 p-3 text-xs text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-rose-400" />
          {actionError}
        </div>
      )}

      {/* Pending Queue Section */}
      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-200">Pending Review Queue</h3>

        {loading ? (
          <div className="glass-panel p-8 text-center text-xs text-slate-400">Loading queue...</div>
        ) : pendingList.length === 0 ? (
          <div className="glass-panel p-8 text-center text-xs text-slate-500">
            No pending approval requests! All actions are up to date.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {pendingList.map((appr) => (
              <div key={appr.id} className="glass-panel p-5 space-y-4 border-amber-500/30">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-700/60 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-amber-400">{appr.id}</span>
                      <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-[10px] font-semibold text-indigo-300 border border-indigo-500/30">
                        {appr.action_type}
                      </span>
                      <StatusBadge status={appr.status} />
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      Order: <strong className="font-mono text-white">{appr.order_number || appr.order_id || "N/A"}</strong> • Customer: <span className="font-mono">{appr.customer_id}</span>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-xs text-slate-400">Requested Amount:</span>
                    <div className="text-xl font-bold text-white">
                      ${appr.requested_amount.toFixed(2)} {appr.currency}
                    </div>
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400">System Justification:</span>
                  <p className="rounded bg-slate-900/60 p-3 text-xs text-slate-200">
                    {appr.reason}
                  </p>
                </div>

                <div className="rounded bg-slate-900/40 p-2 font-mono text-[10px] text-slate-400 flex items-center justify-between">
                  <span>Idempotency Key: {appr.idempotency_key}</span>
                  <span className="text-amber-400">Sandbox Payment Simulation</span>
                </div>

                {/* Supervisor Notes & Decision Actions */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
                  <input
                    type="text"
                    placeholder="Add supervisor notes or rationale..."
                    value={reviewNotes[appr.id] || ""}
                    onChange={(e) =>
                      setReviewNotes({ ...reviewNotes, [appr.id]: e.target.value })
                    }
                    className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
                  />
                  <div className="flex gap-2">
                    <button
                      id={`btn-approve-${appr.id}`}
                      disabled={processingId === appr.id}
                      onClick={() => handleDecision(appr.id, "APPROVED")}
                      className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-50 flex items-center gap-1.5 shadow-md shadow-emerald-600/20"
                    >
                      <Check className="h-4 w-4" /> Approve & Execute
                    </button>
                    <button
                      id={`btn-reject-${appr.id}`}
                      disabled={processingId === appr.id}
                      onClick={() => handleDecision(appr.id, "REJECTED")}
                      className="rounded-lg bg-rose-600/30 border border-rose-500/40 px-4 py-2 text-xs font-semibold text-rose-300 hover:bg-rose-600/50 disabled:opacity-50 flex items-center gap-1.5"
                    >
                      <X className="h-4 w-4" /> Reject
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* History Section */}
      {historyList.length > 0 && (
        <div className="space-y-3 pt-6 border-t border-slate-800">
          <h3 className="text-sm font-bold text-slate-300">Resolved Approval History</h3>
          <div className="glass-panel overflow-hidden">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-700/60 bg-slate-900/40 text-slate-400">
                <tr>
                  <th className="py-2.5 px-4 font-semibold">Approval ID</th>
                  <th className="py-2.5 px-4 font-semibold">Action</th>
                  <th className="py-2.5 px-4 font-semibold">Amount</th>
                  <th className="py-2.5 px-4 font-semibold">Decision</th>
                  <th className="py-2.5 px-4 font-semibold">Reviewer</th>
                  <th className="py-2.5 px-4 font-semibold">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {historyList.map((h) => (
                  <tr key={h.id}>
                    <td className="py-2.5 px-4 font-mono text-indigo-400">{h.id}</td>
                    <td className="py-2.5 px-4 font-medium text-slate-200">{h.action_type}</td>
                    <td className="py-2.5 px-4 font-bold text-white">${h.requested_amount.toFixed(2)}</td>
                    <td className="py-2.5 px-4">
                      <StatusBadge status={h.status} />
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">{h.reviewed_by || "System"}</td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {new Date(h.resolved_at || h.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
