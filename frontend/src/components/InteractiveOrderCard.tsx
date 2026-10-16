import React from "react";
import { Package, Bike, ArrowRight, DollarSign, AlertTriangle, CheckCircle2, Clock, Copy, Utensils } from "lucide-react";
import { StatusBadge } from "./StatusBadge";

export interface OrderItemData {
  sku?: string;
  name: string;
  quantity: number;
  unit_price: number;
}

export interface OrderCardData {
  id: string;
  order_number: string;
  customer_id: string;
  status: string;
  total_amount: number;
  refunded_amount?: number;
  currency?: string;
  carrier?: string;
  tracking_number?: string;
  shipping_address?: string;
  items?: OrderItemData[];
  delivered_at?: string;
}

interface InteractiveOrderCardProps {
  order: OrderCardData;
  onTrackRider: (order: OrderCardData) => void;
  onRequestRefund: (orderNumber: string, amount: number) => void;
  onReportDamaged: (orderNumber: string) => void;
  onCopyText: (text: string) => void;
}

export const InteractiveOrderCard: React.FC<InteractiveOrderCardProps> = ({
  order,
  onTrackRider,
  onRequestRefund,
  onReportDamaged,
  onCopyText,
}) => {
  const isDelivered = order.status.toUpperCase() === "DELIVERED";
  const isPending = order.status.toUpperCase() === "PENDING" || order.status.toUpperCase() === "PROCESSING";
  const isFailed = order.status.toUpperCase() === "FAILED";
  const isRefunded = order.status.toUpperCase() === "REFUNDED";

  const isEligibleAutoRefund = isDelivered && order.total_amount <= 50.0;
  const isHighValue = isDelivered && order.total_amount > 50.0;

  return (
    <div className="mt-3 rounded-2xl border border-[#E23744]/30 bg-gradient-to-b from-[#1C1F28] to-[#14161E] p-4 text-xs space-y-3.5 shadow-xl shadow-black/40">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-[#E23744]/20 border border-[#E23744]/40 flex items-center justify-center">
            <Utensils className="h-3.5 w-3.5 text-[#E23744]" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-mono font-bold text-white text-sm">{order.order_number}</span>
              <button
                onClick={() => onCopyText(order.order_number)}
                className="p-1 hover:text-white text-slate-400 rounded transition-colors"
                title="Copy Order ID"
              >
                <Copy className="h-3 w-3" />
              </button>
            </div>
            <p className="text-[10px] text-slate-400">Total Bill: <strong className="text-white">${order.total_amount.toFixed(2)}</strong></p>
          </div>
        </div>
        <StatusBadge status={order.status} />
      </div>

      {/* Visual Delivery Progress Tracker */}
      <div className="space-y-1.5 py-1">
        <div className="flex items-center justify-between text-[10px] font-bold text-slate-400">
          <span className="text-emerald-400">1. Placed</span>
          <span className={!isFailed ? "text-emerald-400" : "text-slate-500"}>2. Prepared</span>
          <span className={isDelivered ? "text-emerald-400" : "text-amber-400"}>3. Out for Delivery</span>
          <span className={isDelivered ? "text-emerald-400" : "text-slate-500"}>4. Delivered</span>
        </div>
        <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden flex">
          <div className="h-full bg-emerald-500 w-1/4" />
          <div className={`h-full ${!isFailed ? "bg-emerald-500" : "bg-rose-500"} w-1/4`} />
          <div className={`h-full ${isDelivered ? "bg-emerald-500" : "bg-amber-500"} w-1/4`} />
          <div className={`h-full ${isDelivered ? "bg-emerald-500" : "bg-slate-700"} w-1/4`} />
        </div>
      </div>

      {/* Ordered Items List */}
      {order.items && order.items.length > 0 && (
        <div className="rounded-xl bg-slate-900/60 p-2.5 space-y-1.5 border border-slate-800">
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Order Items:</p>
          <div className="space-y-1">
            {order.items.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-[11px] text-slate-300">
                <span className="flex items-center gap-1.5">
                  <span className="text-[#E23744] font-bold">1x</span>
                  <span>{item.name}</span>
                </span>
                <span className="font-mono text-white font-semibold">${item.unit_price.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tracking Details */}
      {order.tracking_number && (
        <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
          <span>Carrier: <strong className="text-white">{order.carrier || "Zomato Courier"}</strong></span>
          <span>Waybill: <strong className="font-mono text-slate-300">{order.tracking_number}</strong></span>
        </div>
      )}

      {/* Interactive Action Buttons */}
      <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-700/50">
        <button
          onClick={() => onTrackRider(order)}
          className="flex-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-bold px-3 py-2 text-[11px] flex items-center justify-center gap-1.5 transition-all border border-slate-700"
        >
          <Bike className="h-3.5 w-3.5 text-[#E23744]" />
          <span>Track Live Courier</span>
        </button>

        {isDelivered && !isRefunded && (
          <button
            onClick={() => onRequestRefund(order.order_number, order.total_amount)}
            className={`rounded-xl px-3 py-2 text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              isEligibleAutoRefund
                ? "bg-[#E23744]/20 hover:bg-[#E23744]/35 text-[#FF6B77] border border-[#E23744]/40"
                : "bg-amber-500/20 hover:bg-amber-500/35 text-amber-300 border border-amber-500/40"
            }`}
          >
            <DollarSign className="h-3.5 w-3.5" />
            <span>{isEligibleAutoRefund ? "Instant Refund" : "Request Refund Review"}</span>
          </button>
        )}

        {isDelivered && !isRefunded && (
          <button
            onClick={() => onReportDamaged(order.order_number)}
            className="rounded-xl bg-rose-500/15 hover:bg-rose-500/30 text-rose-300 border border-rose-500/30 px-3 py-2 text-[11px] font-bold flex items-center gap-1.5 transition-all"
          >
            <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
            <span>Report Spilled / Damaged</span>
          </button>
        )}
      </div>
    </div>
  );
};
