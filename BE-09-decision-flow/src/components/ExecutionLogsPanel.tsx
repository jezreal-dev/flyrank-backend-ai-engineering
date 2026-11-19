"use client";

import React from "react";
import { ExecutionLogEntry, WorkflowExecutionState } from "@/types/flow";
import {
  Activity,
  CheckCircle2,
  Clock,
  Code2,
  Terminal,
  XCircle,
  Zap,
} from "lucide-react";

interface Props {
  executionState: WorkflowExecutionState | null;
  onClear: () => void;
}

export function ExecutionLogsPanel({ executionState, onClear }: Props) {
  if (!executionState) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-500">
        <Terminal className="w-10 h-10 mb-3 stroke-[1.5] text-slate-600" />
        <h4 className="text-sm font-semibold text-slate-400">Execution Panel Ready</h4>
        <p className="text-xs text-slate-500 max-w-[240px] mt-1">
          Enter an input query above and click &quot;Run Workflow&quot; to watch Inngest execute each decision step.
        </p>
      </div>
    );
  }

  const { runId, status, logs, visitedNodes, decisions } = executionState;

  return (
    <div className="h-full flex flex-col bg-slate-950 border-l border-slate-800 text-slate-200">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-sm">Execution Trace</h3>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${
              status === "completed"
                ? "bg-emerald-950 text-emerald-400 border-emerald-700"
                : status === "running"
                ? "bg-blue-950 text-blue-400 border-blue-700 animate-pulse"
                : "bg-slate-800 text-slate-400 border-slate-700"
            }`}
          >
            {status}
          </span>
          <button
            onClick={onClear}
            className="text-[11px] text-slate-400 hover:text-slate-200 px-2 py-0.5 rounded hover:bg-slate-800 transition"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Meta Bar */}
      <div className="px-4 py-2 bg-slate-950/80 border-b border-slate-900 text-[11px] text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
        <div>
          Run: <span className="font-mono text-slate-300">{runId.slice(0, 16)}</span>
        </div>
        <div>
          Nodes Traversed:{" "}
          <span className="font-mono text-indigo-400">{visitedNodes.length}</span>
        </div>
      </div>

      {/* Step List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {logs.length === 0 ? (
          <div className="text-xs text-slate-500 italic p-2">Initializing execution steps in Inngest...</div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs space-y-2 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded-full bg-slate-800 text-indigo-400 flex items-center justify-center text-[10px]">
                    {index + 1}
                  </span>
                  {log.nodeLabel}
                </span>
                <span
                  className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                    log.decision === "YES"
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : "bg-rose-950 text-rose-400 border border-rose-800"
                  }`}
                >
                  {log.decision === "YES" ? (
                    <CheckCircle2 className="w-3 h-3" />
                  ) : (
                    <XCircle className="w-3 h-3" />
                  )}
                  {log.decision}
                </span>
              </div>

              <div className="bg-slate-950/70 p-2 rounded border border-slate-900 font-mono text-[11px] text-slate-300">
                &ldquo;{log.prompt}&rdquo;
              </div>

              <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                <span className="text-slate-400">{log.details}</span>
                <span className="flex items-center gap-1 text-slate-400">
                  <Clock className="w-3 h-3 text-slate-500" />
                  {log.latencyMs}ms
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
