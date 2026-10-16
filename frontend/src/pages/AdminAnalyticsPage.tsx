import React, { useEffect, useState } from "react";
import type { ToolMetric, AuditEventItem } from "../types";
import { fetchToolMetrics, fetchAuditTrail } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import {
  BarChart3,
  Terminal,
  Shield,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
} from "lucide-react";

export const AdminAnalyticsPage: React.FC = () => {
  const [toolMetrics, setToolMetrics] = useState<ToolMetric[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [auditFilter, setAuditFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchToolMetrics(), fetchAuditTrail(100)])
      .then(([tm, at]) => {
        setToolMetrics(tm);
        setAuditEvents(at);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filteredAudit = auditEvents.filter(
    (a) =>
      a.event_type.toLowerCase().includes(auditFilter.toLowerCase()) ||
      a.action.toLowerCase().includes(auditFilter.toLowerCase()) ||
      a.resource_type.toLowerCase().includes(auditFilter.toLowerCase()) ||
      a.resource_id.toLowerCase().includes(auditFilter.toLowerCase())
  );

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-[#E23744]" />
          <h2 className="text-xl font-bold text-white font-['Outfit']">Zomato Partner & Systems Analytics</h2>
        </div>
        <p className="text-xs text-slate-400 mt-1">
          Tool invocation success rates, audit logs, and security compliance telemetry for Zomato Care operations.
        </p>
      </div>

      {/* Tool Performance Metrics */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-emerald-400" />
            <h3 className="text-sm font-bold text-white">Tool Invocation Telemetry & Success Rates</h3>
          </div>
          <span className="text-xs text-slate-400">Total Tool Types: {toolMetrics.length}</span>
        </div>

        {loading ? (
          <div className="py-6 text-center text-xs text-slate-400">Loading metrics...</div>
        ) : toolMetrics.length === 0 ? (
          <div className="py-6 text-center text-xs text-slate-500">No tools recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-700/60 text-slate-400">
                <tr>
                  <th className="pb-2 font-semibold">Tool Name</th>
                  <th className="pb-2 font-semibold">Total Calls</th>
                  <th className="pb-2 font-semibold text-emerald-400">Success</th>
                  <th className="pb-2 font-semibold text-rose-400">Failed</th>
                  <th className="pb-2 font-semibold">Success Rate</th>
                  <th className="pb-2 font-semibold text-right">Avg Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {toolMetrics.map((tm) => (
                  <tr key={tm.tool_name} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-bold text-indigo-300">{tm.tool_name}</td>
                    <td className="py-2.5 text-slate-200">{tm.total_calls}</td>
                    <td className="py-2.5 text-emerald-400">{tm.success_calls}</td>
                    <td className="py-2.5 text-rose-400">{tm.failure_calls}</td>
                    <td className="py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full"
                            style={{ width: `${tm.success_rate_percent}%` }}
                          />
                        </div>
                        <span className="font-semibold text-white">{tm.success_rate_percent}%</span>
                      </div>
                    </td>
                    <td className="py-2.5 text-right text-slate-400">
                      {tm.avg_duration_ms.toFixed(1)} ms
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Filterable Audit History */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Immutable Tenant Audit Log</h3>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              value={auditFilter}
              onChange={(e) => setAuditFilter(e.target.value)}
              placeholder="Filter by event, action, or resource..."
              className="w-full rounded-lg border border-slate-700 bg-slate-900/80 pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        </div>

        {filteredAudit.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-500">No audit events found.</div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {filteredAudit.map((ae) => (
              <div
                key={ae.id}
                className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between font-mono">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-indigo-300 border border-indigo-500/20">
                      {ae.event_type}
                    </span>
                    <span className="text-slate-300 font-bold">{ae.action}</span>
                    <span className="text-slate-400">
                      on {ae.resource_type}: <strong className="text-white">{ae.resource_id}</strong>
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500">
                    {new Date(ae.created_at).toLocaleTimeString()}
                  </span>
                </div>
                {ae.details && Object.keys(ae.details).length > 0 && (
                  <pre className="rounded bg-slate-950/70 p-2 text-[10px] text-slate-400 font-mono overflow-x-auto">
                    {JSON.stringify(ae.details, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
