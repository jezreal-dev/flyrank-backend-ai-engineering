import { WorkflowExecutionState } from "@/types/flow";

// In-memory execution store shared across API routes and Inngest execution steps
const globalStore = global as unknown as {
  __executionStore?: Map<string, WorkflowExecutionState>;
};

if (!globalStore.__executionStore) {
  globalStore.__executionStore = new Map<string, WorkflowExecutionState>();
}

export const executionStore = globalStore.__executionStore;

export function getRun(runId: string): WorkflowExecutionState | undefined {
  return executionStore.get(runId);
}

export function saveRun(run: WorkflowExecutionState): void {
  executionStore.set(run.runId, run);
}

export function updateRun(
  runId: string,
  update: Partial<WorkflowExecutionState>
): WorkflowExecutionState | undefined {
  const existing = executionStore.get(runId);
  if (!existing) return undefined;

  const updated: WorkflowExecutionState = {
    ...existing,
    ...update,
    logs: update.logs ? [...existing.logs, ...update.logs] : existing.logs,
    visitedNodes: update.visitedNodes
      ? Array.from(new Set([...existing.visitedNodes, ...update.visitedNodes]))
      : existing.visitedNodes,
    visitedEdges: update.visitedEdges
      ? Array.from(new Set([...existing.visitedEdges, ...update.visitedEdges]))
      : existing.visitedEdges,
    decisions: {
      ...existing.decisions,
      ...(update.decisions || {}),
    },
  };

  executionStore.set(runId, updated);
  return updated;
}
