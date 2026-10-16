import React, { useState } from "react";
import type { WorkflowEvent } from "../types";
import { ChevronDown, ChevronUp, Cpu, CheckCircle2, AlertTriangle, Clock, Terminal, Copy, Check, Filter } from "lucide-react";

interface ExecutionTimelineProps {
  timeline: WorkflowEvent[];
  executedTools?: any[];
  onCopyTrace?: (text: string) => void;
}

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({
  timeline,
  executedTools = [],
  onCopyTrace,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState<"all" | "tools" | "failures">("all");
  const [copied, setCopied] = useState(false);

  if (!timeline || timeline.length === 0) return null;

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    const payload = JSON.stringify({ timeline, executedTools }, null, 2);
    navigator.clipboard.writeText(payload);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    if (onCopyTrace) onCopyTrace("Copied execution trace to clipboard!");
  };

  const filteredTimeline = timeline.filter((step) => {
    if (selectedFilter === "tools") return step.step_name === "tool_execution";
    if (selectedFilter === "failures") return step.status === "FAILED";
    return true;
  });

  return (
    <div className="mt-3 rounded-xl border border-[#E23744]/25 bg-gradient-to-b from-[#181A22] to-[#12141A] p-3 text-xs shadow-md">
      {/* Accordion Toggle Bar */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between font-bold text-slate-200 cursor-pointer select-none"
        id="toggle-timeline-btn"
      >
        <span className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-[#E23744]" />
          <span>Workflow Execution Stepper ({timeline.length} Steps)</span>
          {executedTools.length > 0 && (
            <span className="rounded-full bg-[#E23744]/20 px-2 py-0.5 text-[10px] text-[#FF6B77] border border-[#E23744]/30 font-mono">
              {executedTools.length} Tool Calls
            </span>
          )}
        </span>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-[10px] px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            title="Copy trace JSON"
          >
            {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
            <span>{copied ? "Copied" : "JSON"}</span>
          </button>
          {expanded ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </div>
      </div>

      {expanded && (
        <div className="mt-3 space-y-3 pt-2 border-t border-slate-700/50">
          {/* Filter Pills */}
          <div className="flex items-center gap-1.5 pb-1">
            <span className="text-[10px] text-slate-500 font-semibold mr-1 flex items-center gap-1">
              <Filter className="h-3 w-3" /> Filter:
            </span>
            <button
              onClick={() => setSelectedFilter("all")}
              className={`rounded px-2 py-0.5 text-[10px] font-bold transition-all ${
                selectedFilter === "all"
                  ? "bg-[#E23744] text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              All Steps ({timeline.length})
            </button>
            <button
              onClick={() => setSelectedFilter("tools")}
              className={`rounded px-2 py-0.5 text-[10px] font-bold transition-all ${
                selectedFilter === "tools"
                  ? "bg-[#E23744] text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              Tools Only ({executedTools.length})
            </button>
            <button
              onClick={() => setSelectedFilter("failures")}
              className={`rounded px-2 py-0.5 text-[10px] font-bold transition-all ${
                selectedFilter === "failures"
                  ? "bg-[#E23744] text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white"
              }`}
            >
              Failures/Warnings
            </button>
          </div>

          {/* Workflow Steps List */}
          <div className="space-y-2">
            {filteredTimeline.map((step, idx) => {
              const isDone = step.status === "COMPLETED";
              const isPaused = step.status === "PAUSED";
              const isFailed = step.status === "FAILED";

              return (
                <div key={idx} className="timeline-item">
                  <div
                    className={`timeline-dot ${
                      isDone ? "completed" : isPaused ? "paused" : isFailed ? "failed" : ""
                    }`}
                  />
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-white text-[11px]">
                      {step.step_name}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                          isDone
                            ? "text-emerald-400 bg-emerald-950/40"
                            : isPaused
                            ? "text-amber-400 bg-amber-950/40"
                            : "text-rose-400 bg-rose-950/40"
                        }`}
                      >
                        {step.status}
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}
                      </span>
                    </div>
                  </div>
                  {step.details && Object.keys(step.details).length > 0 && (
                    <pre className="mt-1 max-h-24 overflow-x-auto rounded-lg bg-black/60 p-2 text-[10px] text-slate-300 font-mono border border-slate-800">
                      {JSON.stringify(step.details, null, 2)}
                    </pre>
                  )}
                </div>
              );
            })}
          </div>

          {/* Executed Tools Details */}
          {executedTools.length > 0 && selectedFilter !== "failures" && (
            <div className="border-t border-slate-700/50 pt-2.5 space-y-2">
              <div className="flex items-center gap-1.5 font-bold text-emerald-400 text-xs">
                <Terminal className="h-3.5 w-3.5" />
                Verified Tool Invocations:
              </div>
              <div className="space-y-2">
                {executedTools.map((t, i) => (
                  <div key={i} className="rounded-xl bg-black/70 p-2.5 font-mono text-[11px] border border-slate-800">
                    <div className="flex items-center justify-between text-slate-200">
                      <span className="font-bold text-[#FF6B77]">{t.tool}</span>
                      <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        t.success ? "bg-emerald-950 text-emerald-300" : "bg-rose-950 text-rose-300"
                      }`}>
                        {t.success ? "SUCCESS" : "FAILED"}
                      </span>
                    </div>
                    {t.data && Object.keys(t.data).length > 0 && (
                      <pre className="mt-1 text-[10px] text-slate-400 max-h-28 overflow-x-auto">
                        {JSON.stringify(t.data, null, 2)}
                      </pre>
                    )}
                    {t.error && (
                      <div className="mt-1 text-[10px] text-rose-400">
                        Error: {t.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
