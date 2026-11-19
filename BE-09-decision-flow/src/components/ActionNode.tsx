"use client";

import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { ActionNodeData } from "@/types/flow";
import { ArrowRightCircle, CheckCheck } from "lucide-react";

export const ActionNode = memo(({ id, data, isConnectable }: NodeProps<any>) => {
  const nodeData = data as ActionNodeData;
  const isVisited = nodeData.status === "visited" || nodeData.status === "done";

  return (
    <div
      className={`w-64 bg-slate-900 text-slate-100 rounded-xl shadow-xl border-2 transition-all duration-200 ${
        isVisited
          ? "border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-950/20"
          : "border-slate-800 hover:border-slate-600"
      }`}
    >
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!w-3 !h-3 !bg-slate-400 !border-2 !border-slate-900"
      />

      <div className="flex items-center justify-between px-3 py-2 border-b border-slate-800 bg-slate-950/40 rounded-t-xl">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-md bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <ArrowRightCircle className="w-3.5 h-3.5" />
          </div>
          <span className="font-semibold text-xs text-slate-200">Terminal Action</span>
        </div>
        {isVisited && (
          <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-700">
            <CheckCheck className="w-3 h-3" /> Reached
          </span>
        )}
      </div>

      <div className="p-3">
        <input
          type="text"
          defaultValue={nodeData.label}
          onChange={(e) => {
            nodeData.label = e.target.value;
          }}
          className="w-full text-xs font-semibold bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-100 focus:outline-none focus:border-purple-500"
        />
        <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
          {nodeData.description || "Final routing destination for this decision path."}
        </p>
      </div>
    </div>
  );
});

ActionNode.displayName = "ActionNode";
