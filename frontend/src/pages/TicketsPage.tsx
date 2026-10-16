import React, { useEffect, useState } from "react";
import type { SupportTicket } from "../types";
import { fetchTickets } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import { Ticket, Search, Filter, Plus, ArrowRight } from "lucide-react";

interface TicketsPageProps {
  onSelectTicket: (ticketId: string) => void;
}

export const TicketsPage: React.FC<TicketsPageProps> = ({ onSelectTicket }) => {
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const loadTickets = (status?: string) => {
    setLoading(true);
    fetchTickets(status)
      .then(setTickets)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadTickets(filterStatus);
  }, [filterStatus]);

  const filteredTickets = tickets.filter(
    (t) =>
      t.ticket_number.toLowerCase().includes(search.toLowerCase()) ||
      t.title.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase())
  );

  const statusOptions = [
    { label: "All Tickets", value: "" },
    { label: "Open", value: "OPEN" },
    { label: "In Progress", value: "IN_PROGRESS" },
    { label: "Waiting Approval", value: "WAITING_APPROVAL" },
    { label: "Resolved", value: "RESOLVED" },
    { label: "Escalated", value: "ESCALATED" },
  ];

  return (
    <div className="p-8 space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Ticket className="h-5 w-5 text-indigo-400" />
            Support Ticket Management
          </h2>
          <p className="text-xs text-slate-400">
            View, track, and inspect ticket states and resolution outcomes.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
          <input
            id="ticket-search-input"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tickets by number, issue, or title..."
            className="w-full rounded-lg border border-slate-700 bg-slate-900/80 pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1 sm:pb-0">
          {statusOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setFilterStatus(opt.value)}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition-colors whitespace-nowrap ${
                filterStatus === opt.value
                  ? "bg-indigo-600 text-white"
                  : "bg-slate-800/60 text-slate-400 hover:bg-slate-700/60 hover:text-white"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tickets Table */}
      <div className="glass-panel overflow-hidden">
        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading tickets...</div>
        ) : filteredTickets.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-500">
            No support tickets match the selected criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-700/60 bg-slate-900/40 text-slate-400">
                <tr>
                  <th className="py-3 px-4 font-semibold">Ticket #</th>
                  <th className="py-3 px-4 font-semibold">Title</th>
                  <th className="py-3 px-4 font-semibold">Category</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">Priority</th>
                  <th className="py-3 px-4 font-semibold">Created</th>
                  <th className="py-3 px-4 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredTickets.map((t) => (
                  <tr
                    key={t.id}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                    onClick={() => onSelectTicket(t.id)}
                  >
                    <td className="py-3 px-4 font-mono font-medium text-indigo-400">
                      {t.ticket_number}
                    </td>
                    <td className="py-3 px-4 font-medium text-white max-w-xs truncate">
                      {t.title}
                    </td>
                    <td className="py-3 px-4 text-slate-400 capitalize">{t.category}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="py-3 px-4 text-slate-300 font-medium">{t.priority}</td>
                    <td className="py-3 px-4 text-slate-400">
                      {new Date(t.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1">
                        View <ArrowRight className="h-3 w-3" />
                      </span>
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
