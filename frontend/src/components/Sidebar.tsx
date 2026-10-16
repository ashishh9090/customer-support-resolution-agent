import React from "react";
import { LayoutDashboard, MessageSquareText, Ticket, CheckSquare, BarChart3, ShieldCheck, HeartHandshake, Sparkles } from "lucide-react";
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
    { id: "dashboard", label: "Care Dashboard", icon: LayoutDashboard },
    { id: "chat", label: "Zomato Support Chat", icon: MessageSquareText },
    { id: "tickets", label: "Orders & Complaints", icon: Ticket },
    {
      id: "approvals",
      label: "Refund Approvals",
      icon: CheckSquare,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: "admin", label: "Partner Analytics", icon: BarChart3, staffOnly: true },
  ];

  return (
    <aside className="sidebar p-4 space-y-6">
      <div className="space-y-1">
        <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-500">
          Zomato Resolution
        </p>
        <nav className="space-y-1.5 pt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            if (item.staffOnly && !isStaff) return null;

            return (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => onTabSelect(item.id as NavTab)}
                className={`flex w-full items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-[#E23744]/15 text-[#FF5A67] border border-[#E23744]/35 shadow-sm shadow-[#E23744]/10"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`h-4 w-4 ${isActive ? "text-[#E23744]" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span className="rounded-full bg-[#E23744] px-2 py-0.5 text-[10px] font-bold text-white shadow-sm shadow-[#E23744]/40">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Zomato Order Protection Banner */}
      <div className="rounded-2xl border border-[#E23744]/25 bg-gradient-to-b from-[#E23744]/10 to-[#E23744]/5 p-3.5 text-[11px] text-slate-300">
        <p className="font-bold text-white mb-1.5 flex items-center gap-1.5 font-['Outfit']">
          <ShieldCheck className="h-4 w-4 text-[#E23744]" />
          Zomato Guarantee
        </p>
        <ul className="space-y-1.5 text-[11px] text-slate-400">
          <li className="flex items-start gap-1.5">
            <span className="text-[#E23744] font-bold">•</span>
            <span><strong>Instant Refund:</strong> Orders &le; $50.00</span>
          </li>
          <li className="flex items-start gap-1.5">
            <span className="text-[#E23744] font-bold">•</span>
            <span><strong>Manager Verification:</strong> Orders &gt; $50.00</span>
          </li>
          <li className="flex items-start gap-1.5">
            <span className="text-[#E23744] font-bold">•</span>
            <span><strong>Spilled / Damaged:</strong> 14-day replacement</span>
          </li>
          <li className="flex items-start gap-1.5">
            <span className="text-[#E23744] font-bold">•</span>
            <span><strong>Safe Sandbox:</strong> Verified transactions</span>
          </li>
        </ul>
      </div>
    </aside>
  );
};
