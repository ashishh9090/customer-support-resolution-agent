import React from "react";
import { LayoutDashboard, MessageSquareText, Ticket, CheckSquare, BarChart3, ShieldAlert } from "lucide-react";
import type { UserRole } from "../types";

export type NavTab = "dashboard" | "chat" | "tickets" | "approvals" | "admin";

interface SidebarProps {
  activeTab: NavTab;
  onTabSelect: (tab: NavTab) => void;
  pendingApprovalsCount?: number;
  userRole?: UserRole;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabSelect,
  pendingApprovalsCount = 0,
  userRole = "customer",
}) => {
  const isStaff = userRole === "support_agent" || userRole === "approver" || userRole === "admin";

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "chat", label: "Support Chat", icon: MessageSquareText },
    { id: "tickets", label: "Tickets", icon: Ticket },
    {
      id: "approvals",
      label: "Approval Center",
      icon: CheckSquare,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: "admin", label: "Administration", icon: BarChart3, staffOnly: true },
  ];

  return (
    <aside className="sidebar p-4 space-y-6">
      <div className="space-y-1">
        <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500">
          Navigation
        </p>
        <nav className="space-y-1 pt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            if (item.staffOnly && !isStaff) return null;

            return (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => onTabSelect(item.id as NavTab)}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/30">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-3 text-[11px] text-slate-400">
        <p className="font-semibold text-slate-200 mb-1 flex items-center gap-1.5">
          <ShieldAlert className="h-3.5 w-3.5 text-indigo-400" />
          Safety & Policies
        </p>
        <ul className="space-y-1 list-disc list-inside text-[10px] text-slate-400">
          <li>Auto-refund: &le; $50.00 USD</li>
          <li>Supervisor approval: &gt; $50.00</li>
          <li>Return window: 30 days</li>
          <li>Damaged report: 14 days</li>
        </ul>
      </div>
    </aside>
  );
};
