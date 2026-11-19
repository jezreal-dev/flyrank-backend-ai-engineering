"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { DecisionNodeData } from "@/types/flow";
import { Brain, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export const DecisionNode = memo(({ id, data, isConnectable }: NodeProps<any>) => {
  const nodeData = data as DecisionNodeData;
  const status = nodeData.status || "idle";

  const getBorderColor = () => {
    switch (status) {
      case "running":
        return "border-blue-500 ring-4 ring-blue-500/20";
      case "yes":
        return "border-emerald-500 ring-2 ring-emerald-500/30";
      case "no":
        return "border-rose-500 ring-2 ring-rose-500/30";
      case "visited":
        return "border-amber-500";
      default:
        return "border-slate-700 hover:border-slate-500";
    }
  };

  const getStatusBadge = () => {
    switch (status) {
      case "running":
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded-full border border-blue-800">
            <Loader2 className="w-3 h-3 animate-spin" /> Evaluating
          </span>
        );
      case "yes":
        return (
          <span className="flex items-center gap-1 text-[11px] font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-700">
            <CheckCircle2 className="w-3 h-3" /> DECISION: YES
          </span>
        );
      case "no":
        return (
          <span className="flex items-center gap-1 text-[11px] font-bold text-rose-400 bg-rose-950/80 px-2 py-0.5 rounded-full border border-rose-700">
            <XCircle className="w-3 h-3" /> DECISION: NO
          </span>
        );
      default:
        return (
          <span className="text-[10px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-full border border-slate-700">
            Decision Step
          </span>
        );
    }
  };

  return (
    <div
      className={`w-72 bg-slate-900 text-slate-100 rounded-xl shadow-xl border-2 transition-all duration-200 ${getBorderColor()}`}
    >
      {/* Incoming Connection Handle */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!w-3 !h-3 !bg-slate-400 !border-2 !border-slate-900"
      />

      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-800 bg-slate-950/60 rounded-t-xl">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Brain className="w-4 h-4" />
          </div>
          <span className="font-semibold text-xs text-slate-200 truncate">
            {nodeData.label || "Decision Step"}
          </span>
        </div>
        {getStatusBadge()}
      </div>

      {/* Prompt Body */}
      <div className="p-3 space-y-2">
        <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
          AI Decision Prompt (Returns YES / NO)
        </label>
        <textarea
          defaultValue={nodeData.prompt}
          onChange={(e) => {
            nodeData.prompt = e.target.value;
          }}
          placeholder="e.g. Is this a support request?"
          className="w-full text-xs bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200 focus:outline-none focus:border-indigo-500 resize-none h-16 transition-colors"
        />
        {nodeData.latencyMs !== undefined && nodeData.latencyMs !== null && (
          <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1">
            <span>LLM Response:</span>
            <span className="font-mono text-indigo-300">{nodeData.latencyMs}ms</span>
          </div>
        )}
      </div>

      {/* Outbound Decision Handles: YES (Green) & NO (Red) */}
      <div className="flex justify-between items-center px-4 py-2 border-t border-slate-800/80 bg-slate-950/40 rounded-b-xl text-[11px] font-bold">
        {/* YES Handle */}
        <div className="relative flex items-center gap-1.5 text-emerald-400">
          <Handle
            type="source"
            position={Position.Bottom}
            id="yes"
            isConnectable={isConnectable}
            className="!left-4 !w-3.5 !h-3.5 !bg-emerald-500 !border-2 !border-slate-950 hover:!scale-125 transition-transform"
          />
          <span className="pl-3">YES</span>
        </div>

        {/* NO Handle */}
        <div className="relative flex items-center gap-1.5 text-rose-400">
          <span className="pr-3">NO</span>
          <Handle
            type="source"
            position={Position.Bottom}
            id="no"
            isConnectable={isConnectable}
            className="!right-4 !w-3.5 !h-3.5 !bg-rose-500 !border-2 !border-slate-950 hover:!scale-125 transition-transform"
          />
        </div>
      </div>
    </div>
  );
});

DecisionNode.displayName = "DecisionNode";
