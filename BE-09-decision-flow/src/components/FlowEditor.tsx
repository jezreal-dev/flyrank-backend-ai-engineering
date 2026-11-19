"use client";

import React, { useState, useCallback, useEffect, useRef } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  BackgroundVariant,
  MarkerType,
  NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { DecisionNode } from "./DecisionNode";
import { ActionNode } from "./ActionNode";
import { ExecutionLogsPanel } from "./ExecutionLogsPanel";
import { SAMPLE_WORKFLOWS } from "@/lib/templates";
import { WorkflowExecutionState } from "@/types/flow";
import {
  Play,
  PlusCircle,
  Download,
  Upload,
  RefreshCw,
  FolderOpen,
  Sparkles,
  Layers,
  ArrowRight,
} from "lucide-react";

const nodeTypes: NodeTypes = {
  decisionNode: DecisionNode as any,
  actionNode: ActionNode as any,
};

export function FlowEditor() {
  const initialWorkflow = SAMPLE_WORKFLOWS[0];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialWorkflow.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialWorkflow.edges);

  const [inputQuery, setInputQuery] = useState(initialWorkflow.sampleInputs[0]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [executionState, setExecutionState] = useState<WorkflowExecutionState | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showLogs, setShowLogs] = useState(true);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Connect new edges with automatic color/labeling based on sourceHandle
  const onConnect = useCallback(
    (params: Connection) => {
      const isYes = params.sourceHandle === "yes";
      const newEdge: Edge = {
        ...params,
        id: `e_${params.source}_${params.target}_${params.sourceHandle || "edge"}_${Date.now()}`,
        label: isYes ? "YES" : "NO",
        data: { condition: isYes ? "YES" : "NO" },
        style: {
          stroke: isYes ? "#10b981" : "#ef4444",
          strokeWidth: 2,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isYes ? "#10b981" : "#ef4444",
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  // Add Decision Node
  const addDecisionNode = () => {
    const id = `decision-${Date.now()}`;
    const newNode: Node = {
      id,
      type: "decisionNode",
      position: { x: 300 + Math.random() * 50, y: 200 + Math.random() * 50 },
      data: {
        label: "New Decision Step",
        prompt: "Does this inquiry meet the condition?",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  // Add Action Node
  const addActionNode = () => {
    const id = `action-${Date.now()}`;
    const newNode: Node = {
      id,
      type: "actionNode",
      position: { x: 350 + Math.random() * 50, y: 380 + Math.random() * 50 },
      data: {
        label: "New Terminal Action",
        description: "Outcome reached by this decision path.",
        status: "idle",
      },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  // Execute Workflow via Inngest
  const handleExecute = async () => {
    if (!inputQuery.trim()) return;

    setIsExecuting(true);
    setExecutionState(null);

    // Reset visual nodes & edges
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: { ...n.data, status: "idle", decision: null, latencyMs: null },
      }))
    );
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        animated: false,
      }))
    );

    try {
      const res = await fetch("/api/execute-flow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          workflowId: initialWorkflow.id,
          inputPayload: inputQuery,
          nodes,
          edges,
          startNodeId: nodes[0]?.id,
        }),
      });

      const data = await res.json();
      if (res.ok && data.runId) {
        setActiveRunId(data.runId);
      } else {
        alert(`Failed to start execution: ${data.error || "Unknown error"}`);
        setIsExecuting(false);
      }
    } catch (err: any) {
      alert(`Network error starting workflow: ${err.message}`);
      setIsExecuting(false);
    }
  };

  // Poll Execution State
  useEffect(() => {
    if (!activeRunId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/flow-status/${activeRunId}`);
        if (!res.ok) return;

        const state: WorkflowExecutionState = await res.json();
        setExecutionState(state);

        // Update visual nodes
        setNodes((nds) =>
          nds.map((n) => {
            const isVisited = state.visitedNodes.includes(n.id);
            const isActive = state.activeNodeId === n.id;
            const decision = state.decisions[n.id];

            let status = n.data.status;
            if (isActive) status = "running";
            else if (decision === "YES") status = "yes";
            else if (decision === "NO") status = "no";
            else if (isVisited) status = "visited";

            return {
              ...n,
              data: {
                ...n.data,
                status,
                decision,
              },
            };
          })
        );

        // Update visual edges (animate traversed edges)
        setEdges((eds) =>
          eds.map((e) => {
            const isTraversed = state.visitedEdges.includes(e.id);
            return {
              ...e,
              animated: isTraversed,
              style: {
                ...e.style,
                strokeWidth: isTraversed ? 3.5 : 2,
              },
            };
          })
        );

        // Stop polling when completed
        if (state.status === "completed" || state.status === "failed") {
          setIsExecuting(false);
          setActiveRunId(null);
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Error polling flow status:", err);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [activeRunId, setNodes, setEdges]);

  // Export JSON
  const handleExportJSON = () => {
    const data = {
      id: `workflow-${Date.now()}`,
      name: "Exported Decision Workflow",
      nodes,
      edges,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `decision-flow-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Import JSON
  const handleImportJSON = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const parsed = JSON.parse(event.target?.result as string);
        if (parsed.nodes && parsed.edges) {
          setNodes(parsed.nodes);
          setEdges(parsed.edges);
        } else {
          alert("Invalid workflow JSON format");
        }
      } catch {
        alert("Failed to parse JSON file");
      }
    };
    reader.readAsText(file);
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Navbar */}
      <header className="h-14 border-b border-slate-800 bg-slate-900/90 px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-md shadow-indigo-600/30">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-tight flex items-center gap-2">
              DecisionFlow <span className="text-[10px] bg-indigo-950 text-indigo-400 border border-indigo-800 px-1.5 py-0.5 rounded font-mono">BE-09</span>
            </h1>
            <p className="text-[11px] text-slate-400">React Flow + Inngest Orchestrated AI Decision Branches</p>
          </div>
        </div>

        {/* Toolbar Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={addDecisionNode}
            className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
          >
            <PlusCircle className="w-3.5 h-3.5 text-indigo-400" />
            + Decision Node
          </button>
          <button
            onClick={addActionNode}
            className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
          >
            <PlusCircle className="w-3.5 h-3.5 text-purple-400" />
            + Action Node
          </button>

          <div className="h-4 w-[1px] bg-slate-800 mx-1" />

          <button
            onClick={handleExportJSON}
            title="Export Workflow JSON"
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2 py-1.5 rounded hover:bg-slate-800 transition"
          >
            <Download className="w-3.5 h-3.5" />
            Export
          </button>

          <label
            title="Import Workflow JSON"
            className="flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200 px-2 py-1.5 rounded hover:bg-slate-800 cursor-pointer transition"
          >
            <Upload className="w-3.5 h-3.5" />
            Import
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImportJSON}
              accept=".json"
              className="hidden"
            />
          </label>

          <button
            onClick={() => {
              setNodes(initialWorkflow.nodes);
              setEdges(initialWorkflow.edges);
            }}
            title="Reset to Default"
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded hover:bg-slate-800 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Input Query & Run Execution Bar */}
      <div className="h-16 border-b border-slate-800 bg-slate-900/50 px-4 flex items-center justify-between gap-4 shrink-0">
        <div className="flex-1 flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-400 shrink-0 flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            Test Inquiry:
          </span>
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Type customer message or query to test decision branching..."
            className="flex-1 max-w-2xl bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 transition"
          />
          <select
            onChange={(e) => setInputQuery(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none"
          >
            <option value="" disabled>Presets...</option>
            {initialWorkflow.sampleInputs.map((sample, i) => (
              <option key={i} value={sample}>
                {sample.slice(0, 42)}...
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleExecute}
          disabled={isExecuting}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold shadow-lg transition-all ${
            isExecuting
              ? "bg-indigo-900 text-indigo-300 cursor-wait"
              : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30 hover:scale-[1.02]"
          }`}
        >
          <Play className={`w-3.5 h-3.5 ${isExecuting ? "animate-spin" : "fill-current"}`} />
          {isExecuting ? "Executing in Inngest..." : "Run Workflow"}
        </button>
      </div>

      {/* Canvas Area with React Flow + Right Execution Drawer */}
      <div className="flex-1 flex overflow-hidden relative">
        <div className="flex-1 h-full w-full">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            className="bg-slate-950"
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#334155" />
            <Controls className="!bg-slate-900 !border-slate-800 !fill-slate-200" />
            <MiniMap
              nodeColor={(n) => (n.type === "decisionNode" ? "#6366f1" : "#a855f7")}
              className="!bg-slate-900 !border-slate-800"
            />
          </ReactFlow>
        </div>

        {/* Right Execution Trace Drawer */}
        {showLogs && (
          <div className="w-80 h-full shrink-0 shadow-2xl">
            <ExecutionLogsPanel
              executionState={executionState}
              onClear={() => {
                setExecutionState(null);
                setNodes((nds) =>
                  nds.map((n) => ({
                    ...n,
                    data: { ...n.data, status: "idle", decision: null },
                  }))
                );
                setEdges((eds) => eds.map((e) => ({ ...e, animated: false })));
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
