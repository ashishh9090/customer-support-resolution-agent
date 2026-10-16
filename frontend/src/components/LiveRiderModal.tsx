import React, { useState } from "react";
import { X, Bike, MapPin, Phone, ShieldCheck, Heart, Star, Navigation, Clock } from "lucide-react";

interface LiveRiderModalProps {
  orderNumber: string;
  carrier?: string;
  trackingNumber?: string;
  shippingAddress?: string;
  onClose: () => void;
  onShowToast: (msg: string) => void;
}

export const LiveRiderModal: React.FC<LiveRiderModalProps> = ({
  orderNumber,
  carrier = "Zomato Express Rider",
  trackingNumber = "ZOM-778920-IND",
  shippingAddress = "742 Evergreen Terrace, Springfield, OR 97477",
  onClose,
  onShowToast,
}) => {
  const [tipped, setTipped] = useState(false);

  const handleTip = () => {
    setTipped(true);
    onShowToast("❤️ Added $2.00 tip for Rajesh! Thank you for supporting our delivery hero.");
  };

  const handleCall = () => {
    onShowToast("📞 Connecting simulated sandbox call to Rajesh (+91 98765-43210)...");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in">
      <div className="relative w-full max-w-lg glass-panel border-[#E23744]/40 bg-[#16181F] p-6 space-y-5 shadow-2xl shadow-[#E23744]/20 rounded-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#E23744]/20 border border-[#E23744]/40">
              <Bike className="h-5 w-5 text-[#E23744] animate-bounce" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white font-['Outfit']">Live Delivery GPS Tracking</h3>
              <p className="text-[11px] text-slate-400 font-mono">Order: {orderNumber} • Carrier: {carrier}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Simulated Animated Radar Map */}
        <div className="relative h-44 rounded-xl bg-gradient-to-b from-[#1C202B] to-[#12141A] border border-slate-700/60 overflow-hidden flex items-center justify-center">
          {/* Grid lines */}
          <div className="absolute inset-0 opacity-15 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]" />
          
          {/* Animated Route Line */}
          <div className="absolute w-3/4 h-0.5 bg-gradient-to-r from-emerald-500 via-[#E23744] to-[#F4A261] border-dashed" />
          
          {/* Pulse Ripple */}
          <div className="absolute left-1/3 w-16 h-16 rounded-full bg-[#E23744]/20 animate-ping" />
          
          {/* Rider Bike Icon */}
          <div className="absolute left-1/3 flex flex-col items-center">
            <div className="h-8 w-8 rounded-full bg-[#E23744] flex items-center justify-center shadow-lg shadow-[#E23744]/50 border-2 border-white">
              <Bike className="h-4 w-4 text-white" />
            </div>
            <span className="mt-1 text-[9px] font-bold bg-black/80 px-2 py-0.5 rounded text-white font-mono">
              Rajesh (Rider)
            </span>
          </div>

          {/* Delivery Destination Pin */}
          <div className="absolute right-1/4 flex flex-col items-center">
            <div className="h-8 w-8 rounded-full bg-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/40 border-2 border-white">
              <MapPin className="h-4 w-4 text-white" />
            </div>
            <span className="mt-1 text-[9px] font-bold bg-black/80 px-2 py-0.5 rounded text-white font-mono">
              Your Doorstep
            </span>
          </div>

          {/* Live Speed / Status Badge */}
          <div className="absolute top-2.5 left-2.5 flex items-center gap-1.5 rounded-full bg-black/70 border border-slate-700/60 px-2.5 py-1 text-[10px] text-white">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Transit: <strong>On-Time Guarantee Met</strong></span>
          </div>
        </div>

        {/* Delivery Partner Details */}
        <div className="flex items-center justify-between rounded-xl bg-slate-800/50 p-3.5 border border-slate-700/50">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-[#E23744] to-[#F4A261] flex items-center justify-center text-white font-black text-sm font-['Outfit']">
              RK
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h4 className="text-xs font-bold text-white font-['Outfit']">Rajesh Kumar</h4>
                <span className="flex items-center gap-0.5 text-[10px] text-amber-400 font-bold">
                  <Star className="h-3 w-3 fill-amber-400 text-amber-400" /> 4.92
                </span>
                <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[9px] text-emerald-400 font-bold">
                  Vaccinated
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Hero Splendor • 1,480 safe deliveries</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={handleCall}
              className="p-2 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-slate-200 hover:text-white transition-all text-xs"
              title="Call Driver"
            >
              <Phone className="h-4 w-4" />
            </button>
            <button
              onClick={handleTip}
              disabled={tipped}
              className={`p-2 rounded-lg flex items-center gap-1 text-xs font-bold transition-all ${
                tipped
                  ? "bg-emerald-600/30 text-emerald-300 border border-emerald-500/40"
                  : "bg-[#E23744]/20 text-[#FF6B77] hover:bg-[#E23744]/30 border border-[#E23744]/40"
              }`}
            >
              <Heart className={`h-3.5 w-3.5 ${tipped ? "fill-emerald-400 text-emerald-400" : ""}`} />
              <span>{tipped ? "Tipped $2" : "Tip $2"}</span>
            </button>
          </div>
        </div>

        {/* Address and Tracking Details */}
        <div className="space-y-1.5 text-xs">
          <div className="flex items-start gap-2 text-slate-300">
            <MapPin className="h-4 w-4 text-[#E23744] shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-white">Delivery Address:</p>
              <p className="text-[11px] text-slate-400">{shippingAddress}</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
            <Clock className="h-3.5 w-3.5 text-slate-500" />
            <span>Tracking Number: <strong className="font-mono text-white">{trackingNumber}</strong></span>
          </div>
        </div>

        {/* Close Button */}
        <button
          onClick={onClose}
          className="w-full btn-secondary justify-center py-2 text-xs font-bold"
        >
          Close Tracking Map
        </button>
      </div>
    </div>
  );
};
