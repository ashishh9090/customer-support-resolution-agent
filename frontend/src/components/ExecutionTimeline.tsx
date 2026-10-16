import React, { useState } from "react";
import type { WorkflowEvent } from "../types";
import { ChevronDown, ChevronUp, Cpu, CheckCircle2, AlertTriangle, Clock, Terminal } from "lucide-react";

interface ExecutionTimelineProps {
  timeline: WorkflowEvent[];
  executedTools?: any[];
}

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({ timeline, executedTools = [] }) => {
  const [expanded, setExpanded] = useState(false);

  if (!timeline || timeline.length === 0) return null;

  return (
    <div className="mt-3 rounded-lg border border-indigo-500/20 bg-indigo-950/20 p-3 text-xs">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between font-semibold text-indigo-300 hover:text-indigo-200"
        id="toggle-timeline-btn"
      >
        <span className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-indigo-400" />
          Agent Reasoning & Execution Timeline ({timeline.length} Steps)
          {executedTools.length > 0 && (
            <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-[10px] text-indigo-300">
              {executedTools.length} Tools Invocations
            </span>
          )}
        </span>
        {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {expanded && (
        <div className="mt-3 space-y-3 pt-2">
          {/* Workflow Steps */}
          <div className="space-y-2">
            {timeline.map((step, idx) => {
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
                    <span className="font-mono font-medium text-slate-200">
                      {step.step_name}
                    </span>
                    <span className="text-[10px] text-slate-400">
                      {step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}
                    </span>
                  </div>
                  {step.details && Object.keys(step.details).length > 0 && (
                    <pre className="mt-1 max-h-24 overflow-x-auto rounded bg-slate-900/60 p-1.5 text-[10px] text-slate-300">
                      {JSON.stringify(step.details, null, 2)}
                    </pre>
                  )}
                </div>
              );
            })}
          </div>

          {/* Executed Tools Details */}
          {executedTools.length > 0 && (
            <div className="border-t border-slate-700/50 pt-2">
              <div className="mb-1 flex items-center gap-1.5 font-semibold text-emerald-400">
                <Terminal className="h-3.5 w-3.5" />
                Verified Tool Executions:
              </div>
              <div className="space-y-1.5">
                {executedTools.map((t, i) => (
                  <div key={i} className="rounded bg-slate-900/80 p-2 font-mono text-[11px]">
                    <div className="flex items-center justify-between text-slate-200">
                      <span className="font-bold text-emerald-300">{t.tool}</span>
                      <span className={t.success ? "text-emerald-400" : "text-rose-400"}>
                        {t.success ? "SUCCESS" : "FAILED"}
                      </span>
                    </div>
                    {t.data && (
                      <pre className="mt-1 text-[10px] text-slate-400">
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
