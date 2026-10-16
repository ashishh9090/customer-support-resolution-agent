import React, { useEffect } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export interface ToastMessage {
  id: string;
  type: "success" | "error" | "info";
  message: string;
}

interface ToastProps {
  toasts: ToastMessage[];
  onDismiss: (id: string) => void;
}

export const ToastContainer: React.FC<ToastProps> = ({ toasts, onDismiss }) => {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm pointer-events-none">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`pointer-events-auto flex items-center justify-between gap-3 p-3.5 rounded-xl shadow-xl text-xs font-semibold backdrop-blur-md transition-all transform translate-y-0 animate-in fade-in slide-in-from-bottom-2 ${
            toast.type === "success"
              ? "bg-[#18231E]/95 text-emerald-300 border border-emerald-500/40 shadow-emerald-950/40"
              : toast.type === "error"
              ? "bg-[#251619]/95 text-rose-300 border border-[#E23744]/50 shadow-rose-950/40"
              : "bg-[#1A1E29]/95 text-[#F4A261] border border-[#F4A261]/40 shadow-slate-950/40"
          }`}
        >
          <div className="flex items-center gap-2.5">
            {toast.type === "success" && <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />}
            {toast.type === "error" && <AlertCircle className="h-4 w-4 text-[#E23744] shrink-0" />}
            {toast.type === "info" && <Info className="h-4 w-4 text-[#F4A261] shrink-0" />}
            <span>{toast.message}</span>
          </div>
          <button
            onClick={() => onDismiss(toast.id)}
            className="p-1 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};
