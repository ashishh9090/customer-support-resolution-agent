import React, { useEffect, useState } from "react";
import type { DashboardMetrics, SupportTicket } from "../types";
import { fetchDashboardMetrics, fetchTickets } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import {
  Ticket,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileCheck2,
  DollarSign,
  Zap,
  ArrowRight,
  Sparkles,
} from "lucide-react";

interface DashboardPageProps {
  onNavigateToChatWithPrompt: (prompt: string) => void;
  onSelectTicket: (ticketId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigateToChatWithPrompt,
  onSelectTicket,
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentTickets, setRecentTickets] = useState<SupportTicket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchDashboardMetrics(), fetchTickets()])
      .then(([m, t]) => {
        setMetrics(m);
        setRecentTickets(t.slice(0, 6));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const sampleScenarios = [
    {
      title: "1. Order Status Inquiry",
      desc: "Look up verified live carrier tracking on delivered order ORD-1001.",
      prompt: "Where is my order ORD-1001? Can you check the delivery status?",
      badge: "Verified Tool",
    },
    {
      title: "2. Auto-Eligible Refund",
      desc: "Request refund for ORD-1001 ($42.50) processed instantly in sandbox mode.",
      prompt: "I want to return my earbuds from order ORD-1001 and request a refund.",
      badge: "Auto ≤ $50",
    },
    {
      title: "3. Refund Requiring Approval",
      desc: "Smartwatch ORD-1002 ($129.99) exceeds $50 limit, entering supervisor approval queue.",
      prompt: "I want a full refund for my smartwatch order ORD-1002.",
      badge: "Approval > $50",
    },
    {
      title: "4. Damaged Product Complaint",
      desc: "Report damaged delivery opening a priority ticket and resolution workflow.",
      prompt: "My order ORD-1001 arrived with a broken and shattered case! It is damaged.",
      badge: "High Priority",
    },
    {
      title: "5. Failed Payment Inquiry",
      desc: "Inquire about declined transaction on ORD-1006 with exact decline code.",
      prompt: "Why was my payment declined on order ORD-1006?",
      badge: "Gateway Check",
    },
    {
      title: "6. Shipping Policy RAG",
      desc: "Ask general shipping rules and receive grounded citations.",
      prompt: "What shipping methods and delivery timelines do you offer?",
      badge: "RAG Citation",
    },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Top Banner */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Resolution Operations Dashboard</h2>
        <p className="text-sm text-slate-400 mt-1">
          Stateful LangGraph Agent telemetry, verified tool operations, and approval queue monitoring.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Tickets</span>
            <Ticket className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white">{metrics?.total_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Resolved</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400">{metrics?.resolved_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Pending Action</span>
            <Clock className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-bold text-cyan-400">{metrics?.pending_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Approval Queue</span>
            <FileCheck2 className="h-4 w-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400">{metrics?.approval_queue_count ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Escalated</span>
            <AlertTriangle className="h-4 w-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400">{metrics?.escalated_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Refunds</span>
            <DollarSign className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white">
            ${metrics?.total_refunds_processed_usd?.toFixed(2) ?? "0.00"}
          </p>
        </div>
      </div>

      {/* Scenario Quick Launcher */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-indigo-400" />
            <h3 className="text-lg font-bold text-white">Interactive Scenario Demonstrations</h3>
          </div>
          <span className="text-xs text-slate-400">Click any scenario to test live agent orchestration</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sampleScenarios.map((sc, i) => (
            <div
              key={i}
              onClick={() => onNavigateToChatWithPrompt(sc.prompt)}
              className="glass-panel p-5 cursor-pointer hover:border-indigo-500/50 hover:bg-slate-800/50 transition-all group flex flex-col justify-between space-y-3"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-300">{sc.title}</span>
                  <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-[10px] font-semibold text-indigo-400 border border-indigo-500/20">
                    {sc.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-300">{sc.desc}</p>
                <div className="rounded bg-slate-900/60 p-2 text-[11px] font-mono text-slate-400">
                  "{sc.prompt}"
                </div>
              </div>
              <div className="flex items-center text-xs font-semibold text-indigo-400 group-hover:text-indigo-300 gap-1">
                <span>Run in Chat</span>
                <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Tickets Table */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white">Recent Support Tickets</h3>
          <span className="text-xs text-slate-400">{recentTickets.length} tickets recorded</span>
        </div>

        {recentTickets.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">No tickets found for this tenant.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-700/60 text-slate-400">
                <tr>
                  <th className="pb-3 font-semibold">Ticket #</th>
                  <th className="pb-3 font-semibold">Title</th>
                  <th className="pb-3 font-semibold">Category</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Priority</th>
                  <th className="pb-3 font-semibold">Created</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {recentTickets.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/30">
                    <td className="py-3 font-mono font-medium text-indigo-300">{t.ticket_number}</td>
                    <td className="py-3 font-medium text-slate-200">{t.title}</td>
                    <td className="py-3 text-slate-400 capitalize">{t.category}</td>
                    <td className="py-3">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="py-3 text-slate-300">{t.priority}</td>
                    <td className="py-3 text-slate-400">
                      {new Date(t.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectTicket(t.id)}
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
                      >
                        View &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
