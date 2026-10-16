import React, { useEffect, useState } from "react";
import type { DemoUser, AuthToken } from "../types";
import { fetchDemoUsers, switchUser } from "../services/api";
import { Bot, UserCheck, ShieldCheck, Sparkles, Store } from "lucide-react";

interface NavbarProps {
  currentUser: AuthToken | null;
  onUserChanged: (user: AuthToken) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentUser, onUserChanged }) => {
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);

  useEffect(() => {
    fetchDemoUsers().then(setDemoUsers).catch(console.error);
  }, []);

  const handleSelectUser = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const userId = e.target.value;
    if (!userId) return;
    try {
      const updated = await switchUser(userId);
      onUserChanged(updated);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <header className="glass-nav flex h-16 items-center justify-between px-6 z-20">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 shadow-lg shadow-indigo-500/30">
          <Bot className="h-6 w-6 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold text-white tracking-tight">AI Support Resolution Agent</h1>
            <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/30">
              SANDBOX SIMULATION
            </span>
          </div>
          <p className="text-xs text-slate-400">LangGraph Orchestrated • Verified RAG • Multi-Tenant</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Current Tenant Badge */}
        <div className="hidden sm:flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-900/60 px-3 py-1.5 text-xs text-slate-300">
          <Store className="h-3.5 w-3.5 text-indigo-400" />
          <span>Tenant: <strong className="text-white">{currentUser?.tenant_id === "tenant_apex" ? "ApexGadgets" : "NovaStore Retail"}</strong></span>
        </div>

        {/* Demo User Switcher */}
        <div className="flex items-center gap-2">
          <UserCheck className="h-4 w-4 text-slate-400" />
          <select
            id="demo-user-select"
            value={currentUser?.user_id || ""}
            onChange={handleSelectUser}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            {demoUsers.map((u) => (
              <option key={u.user_id} value={u.user_id}>
                {u.full_name} ({u.role.toUpperCase()} - {u.tenant_name})
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};
