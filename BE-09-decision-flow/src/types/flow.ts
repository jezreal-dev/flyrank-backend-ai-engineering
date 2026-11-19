export type DecisionResult = "YES" | "NO";

export type NodeExecutionStatus = "idle" | "running" | "yes" | "no" | "visited" | "done" | "failed";

export interface DecisionNodeData {
  label: string;
  prompt: string;
  status?: NodeExecutionStatus;
  decision?: DecisionResult | null;
  latencyMs?: number | null;
  error?: string | null;
}

export interface ActionNodeData {
  label: string;
  description?: string;
  status?: NodeExecutionStatus;
}

export interface FlowEdgeData {
  condition: DecisionResult;
}

export interface ExecutionLogEntry {
  timestamp: string;
  nodeId: string;
  nodeLabel: string;
  stepName: string;
  prompt: string;
  decision: DecisionResult;
  latencyMs: number;
  status: "success" | "retry" | "error";
  details?: string;
}

export interface WorkflowExecutionState {
  runId: string;
  workflowId: string;
  inputPayload: string;
  status: "pending" | "running" | "completed" | "failed";
  activeNodeId?: string | null;
  visitedNodes: string[];
  visitedEdges: string[];
  decisions: Record<string, DecisionResult>;
  logs: ExecutionLogEntry[];
  startTime?: string;
  endTime?: string;
  error?: string | null;
}

export interface SerializedWorkflow {
  id: string;
  name: string;
  description: string;
  nodes: any[];
  edges: any[];
  sampleInputs: string[];
}
