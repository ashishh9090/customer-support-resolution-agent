import React, { useEffect, useState } from "react";
import type { DemoUser, AuthToken } from "../types";
import { fetchDemoUsers, switchUser } from "../services/api";
import { UtensilsCrossed, UserCheck, Sparkles, Store, ShieldCheck, HeartHandshake } from "lucide-react";

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
      <div className="flex items-center gap-3.5">
        {/* Zomato Logo Mark */}
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#E23744] to-[#FF5E6D] shadow-lg shadow-[#E23744]/40">
          <UtensilsCrossed className="h-5 w-5 text-white" />
        </div>
        
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="zomato-wordmark text-2xl leading-none">zomato</span>
            <span className="rounded-full bg-[#E23744]/20 px-2 py-0.5 text-[10px] font-extrabold tracking-wider text-[#FF6B77] border border-[#E23744]/40">
              CARE
            </span>
            <span className="hidden sm:inline-flex rounded-full bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/30">
              LIVE ASSISTANT
            </span>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">Order Issues • Instant Refunds • Live Rider Tracking</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Current Tenant / Kitchen Badge */}
        <div className="hidden md:flex items-center gap-1.5 rounded-lg border border-[#E23744]/25 bg-slate-900/70 px-3 py-1.5 text-xs text-slate-300">
          <Store className="h-3.5 w-3.5 text-[#E23744]" />
          <span>Partner: <strong className="text-white">{currentUser?.tenant_id === "tenant_apex" ? "Apex Gourmet Kitchens" : "NovaFoods & Retail"}</strong></span>
        </div>

        {/* Demo User Switcher */}
        <div className="flex items-center gap-2">
          <UserCheck className="h-4 w-4 text-slate-400" />
          <select
            id="demo-user-select"
            value={currentUser?.user_id || ""}
            onChange={handleSelectUser}
            className="rounded-lg border border-[#E23744]/30 bg-[#16181F] px-3 py-1.5 text-xs text-slate-200 focus:border-[#E23744] focus:outline-none focus:ring-1 focus:ring-[#E23744]/40 cursor-pointer font-medium"
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
