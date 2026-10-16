import React, { useEffect, useState } from "react";
import type { DashboardMetrics, SupportTicket } from "../types";
import { fetchDashboardMetrics, fetchTickets, fetchOrder } from "../services/api";
import { StatusBadge } from "../components/StatusBadge";
import { InteractiveOrderCard, type OrderCardData } from "../components/InteractiveOrderCard";
import { LiveRiderModal } from "../components/LiveRiderModal";
import { ToastContainer, type ToastMessage } from "../components/Toast";
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
  Bike,
  UtensilsCrossed,
  ShieldCheck,
  CreditCard,
  PackageOpen,
  HelpCircle,
  Search,
  ChevronRight,
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

  // Live Order Lookup State
  const [searchOrderId, setSearchOrderId] = useState("ORD-1001");
  const [lookedUpOrder, setLookedUpOrder] = useState<OrderCardData | null>(null);
  const [orderLoading, setOrderLoading] = useState(false);
  const [orderError, setOrderError] = useState<string | null>(null);
  const [activeTrackingOrder, setActiveTrackingOrder] = useState<OrderCardData | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (message: string, type: "success" | "error" | "info" = "info") => {
    const id = `toast-${Date.now()}-${Math.random()}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const handleLookupOrder = async (orderIdToLookup?: string) => {
    const id = (orderIdToLookup || searchOrderId).trim();
    if (!id) return;
    setOrderLoading(true);
    setOrderError(null);
    try {
      const data = await fetchOrder(id);
      setLookedUpOrder(data);
      addToast(`Retrieved verified details for ${id}`, "success");
    } catch (err: any) {
      setOrderError(err.message || `Order ${id} not found`);
      setLookedUpOrder(null);
      addToast(err.message || `Order ${id} not found`, "error");
    } finally {
      setOrderLoading(false);
    }
  };

  useEffect(() => {
    Promise.all([fetchDashboardMetrics(), fetchTickets()])
      .then(([m, t]) => {
        setMetrics(m);
        setRecentTickets(t.slice(0, 6));
      })
      .catch(console.error)
      .finally(() => setLoading(false));

    // Auto-lookup default order ORD-1001 on mount
    handleLookupOrder("ORD-1001");
  }, []);

  const sampleScenarios = [
    {
      title: "1. Order & Rider Tracking",
      desc: "Track live courier delivery and verified transit status for order ORD-1001.",
      prompt: "Where is my order ORD-1001? Can you check the delivery status?",
      badge: "Live Tracking",
      icon: Bike,
    },
    {
      title: "2. Instant Meal Refund",
      desc: "Fast auto-refund for order ORD-1001 ($42.50) processed instantly under $50 limit.",
      prompt: "I want to return my order ORD-1001 and request a full refund.",
      badge: "Instant ≤ $50",
      icon: Zap,
    },
    {
      title: "3. Large Order Refund Approval",
      desc: "Order ORD-1002 ($129.99) exceeds $50 safety limit and pauses for manager review.",
      prompt: "I want a full refund for my order ORD-1002.",
      badge: "Requires Review > $50",
      icon: ShieldCheck,
    },
    {
      title: "4. Spilled / Damaged Delivery",
      desc: "Report damaged food or broken items with automatic replacement ticket creation.",
      prompt: "My order ORD-1001 arrived with a broken and shattered case! It is damaged.",
      badge: "Quality Claim",
      icon: PackageOpen,
    },
    {
      title: "5. UPI & Card Payment Help",
      desc: "Investigate failed checkout charge on ORD-1006 with real gateway failure codes.",
      prompt: "Why was my payment declined on order ORD-1006?",
      badge: "Payment Diagnosis",
      icon: CreditCard,
    },
    {
      title: "6. Zomato Refund Policy FAQ",
      desc: "Ask general delivery and return rules with verified policy citations.",
      prompt: "What shipping methods and return policies do you offer?",
      badge: "Verified Citations",
      icon: HelpCircle,
    },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Toast Notification Container */}
      <ToastContainer
        toasts={toasts}
        onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))}
      />

      {/* Live Rider Map Modal */}
      {activeTrackingOrder && (
        <LiveRiderModal
          orderNumber={activeTrackingOrder.order_number}
          carrier={activeTrackingOrder.carrier}
          trackingNumber={activeTrackingOrder.tracking_number}
          shippingAddress={activeTrackingOrder.shipping_address}
          onClose={() => setActiveTrackingOrder(null)}
          onShowToast={(msg) => addToast(msg, "success")}
        />
      )}

      {/* Zomato Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-[#E23744] via-[#CB202D] to-[#99111D] p-6 text-white shadow-xl shadow-[#E23744]/25">
        <div className="relative z-10 max-w-2xl space-y-2">
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-black tracking-wider uppercase backdrop-blur-sm">
              Zomato AI Care Hub
            </span>
            <span className="text-xs text-white/80 font-medium">Verified Live Operations</span>
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight font-['Outfit']">
            Hungry for help? We've got your back.
          </h2>
          <p className="text-sm text-white/90 leading-relaxed">
            Stateful LangGraph Agent with real-time delivery lookups, instant refund safety controls, 
            supervisor review checkpoints, and verified knowledge citations.
          </p>
        </div>
        <div className="absolute -right-8 -bottom-10 opacity-15 pointer-events-none">
          <UtensilsCrossed className="w-64 h-64 text-white" />
        </div>
      </div>

      {/* Interactive Instant Order Lookup & Live Radar Widget */}
      <div className="glass-panel p-6 space-y-4 border-l-4 border-l-[#E23744]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-white font-['Outfit'] flex items-center gap-2">
              <Bike className="h-5 w-5 text-[#E23744]" />
              Instant Order & Delivery Radar
            </h3>
            <p className="text-xs text-slate-400">
              Select or type any Order ID to inspect live items, tracking, or launch instant refund actions.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={searchOrderId}
              onChange={(e) => setSearchOrderId(e.target.value)}
              placeholder="e.g. ORD-1001"
              className="rounded-xl border border-slate-700 bg-slate-900/90 px-3 py-1.5 text-xs text-white placeholder-slate-500 font-mono focus:border-[#E23744] focus:outline-none"
            />
            <button
              onClick={() => handleLookupOrder()}
              disabled={orderLoading}
              className="btn-primary text-xs py-1.5 px-3"
            >
              <Search className="h-3.5 w-3.5" />
              <span>{orderLoading ? "Fetching..." : "Lookup"}</span>
            </button>
          </div>
        </div>

        {/* Quick Select Buttons */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mr-1">
            Quick Inquire:
          </span>
          {["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1005", "ORD-1006"].map((ordId) => (
            <button
              key={ordId}
              onClick={() => {
                setSearchOrderId(ordId);
                handleLookupOrder(ordId);
              }}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-mono transition-all ${
                searchOrderId === ordId
                  ? "bg-[#E23744] text-white font-bold"
                  : "bg-slate-800/80 hover:bg-slate-700 text-slate-300"
              }`}
            >
              {ordId}
            </button>
          ))}
        </div>

        {orderError && (
          <div className="rounded-xl border border-rose-500/40 bg-rose-950/20 p-3 text-xs text-rose-300 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-rose-400" />
            <span>{orderError}</span>
          </div>
        )}

        {lookedUpOrder && (
          <InteractiveOrderCard
            order={lookedUpOrder}
            onTrackRider={(ord) => setActiveTrackingOrder(ord)}
            onRequestRefund={(ordNum) =>
              onNavigateToChatWithPrompt(`I want a refund for order ${ordNum}`)
            }
            onReportDamaged={(ordNum) =>
              onNavigateToChatWithPrompt(`My order ${ordNum} arrived damaged with broken parts!`)
            }
            onCopyText={(text) => {
              navigator.clipboard.writeText(text);
              addToast(`Copied ${text} to clipboard!`, "success");
            }}
          />
        )}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-[#E23744]">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">Total Tickets</span>
            <Ticket className="h-4 w-4 text-[#E23744]" />
          </div>
          <p className="text-2xl font-black text-white font-['Outfit']">{metrics?.total_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-emerald-500">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">Resolved</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-black text-emerald-400 font-['Outfit']">{metrics?.resolved_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-cyan-500">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">In Transit / Active</span>
            <Clock className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="text-2xl font-black text-cyan-400 font-['Outfit']">{metrics?.pending_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-amber-500">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">Review Queue</span>
            <FileCheck2 className="h-4 w-4 text-amber-400" />
          </div>
          <p className="text-2xl font-black text-amber-400 font-['Outfit']">{metrics?.approval_queue_count ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-[#FF6B77]">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">Escalated</span>
            <AlertTriangle className="h-4 w-4 text-[#FF6B77]" />
          </div>
          <p className="text-2xl font-black text-[#FF6B77] font-['Outfit']">{metrics?.escalated_tickets ?? 0}</p>
        </div>

        <div className="glass-panel p-4 space-y-1 border-t-2 border-t-[#F4A261]">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-bold font-['Outfit']">Refunds Issued</span>
            <DollarSign className="h-4 w-4 text-[#F4A261]" />
          </div>
          <p className="text-2xl font-black text-[#F4A261] font-['Outfit']">
            ${metrics?.total_refunds_processed_usd?.toFixed(2) ?? "0.00"}
          </p>
        </div>
      </div>

      {/* 6 Quick Scenario Launcher Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UtensilsCrossed className="h-5 w-5 text-[#E23744]" />
            <h3 className="text-lg font-bold text-white font-['Outfit']">
              Quick Resolution Scenarios
            </h3>
          </div>
          <span className="text-xs text-slate-400">Click any card to launch interactive test flow</span>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sampleScenarios.map((sc, i) => {
            const Icon = sc.icon;
            return (
              <div
                key={i}
                onClick={() => onNavigateToChatWithPrompt(sc.prompt)}
                className="glass-panel p-5 space-y-3 cursor-pointer group hover:border-[#E23744]/60 hover:bg-[#20242D] transition-all relative overflow-hidden"
              >
                <div className="flex items-center justify-between">
                  <span className="badge badge-zomato text-[10px]">
                    {sc.badge}
                  </span>
                  <Icon className="h-4 w-4 text-slate-500 group-hover:text-[#E23744] transition-colors" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-[#FF5E6D] transition-colors font-['Outfit']">
                    {sc.title}
                  </h4>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">{sc.desc}</p>
                </div>
                <div className="pt-2 flex items-center justify-between border-t border-slate-700/40 text-xs font-bold text-[#E23744]">
                  <span>Launch in Chat</span>
                  <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Support Tickets Section */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Ticket className="h-5 w-5 text-[#E23744]" />
            <h3 className="text-base font-bold text-white font-['Outfit']">Recent Care Tickets</h3>
          </div>
          <span className="text-xs text-slate-400">Real-time database records</span>
        </div>

        {recentTickets.length === 0 ? (
          <p className="text-xs text-slate-500 py-4 text-center">No active tickets found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[10px]">
                  <th className="pb-3 font-semibold">Ticket</th>
                  <th className="pb-3 font-semibold">Customer / Order</th>
                  <th className="pb-3 font-semibold">Subject</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Priority</th>
                  <th className="pb-3 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentTickets.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 font-mono font-bold text-white">{t.ticket_number}</td>
                    <td className="py-3 text-slate-300">
                      <div>{t.customer_name || "Customer"}</div>
                      <div className="text-[10px] text-slate-500">{t.order_number || "No Order"}</div>
                    </td>
                    <td className="py-3 text-slate-200 max-w-xs truncate">{t.subject}</td>
                    <td className="py-3">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="py-3">
                      <span className="rounded px-2 py-0.5 text-[10px] font-bold bg-[#E23744]/15 text-[#FF6B77]">
                        {t.priority}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectTicket(t.id)}
                        className="rounded-lg bg-[#E23744]/10 hover:bg-[#E23744]/25 text-[#FF5A67] px-2.5 py-1 text-[11px] font-bold transition-all"
                      >
                        Inspect Details
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
