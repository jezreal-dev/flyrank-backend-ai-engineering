import { inngest } from "../client";
import { askDecision } from "@/lib/llm";
import { updateRun } from "@/lib/executionStore";
import { DecisionResult, ExecutionLogEntry } from "@/types/flow";

export const executeDecisionFlow = inngest.createFunction(
  {
    id: "execute-decision-flow",
    name: "Execute AI Decision Flow",
    retries: 2,
  },
  { event: "workflow/execute" },
  async ({ event, step }) => {
    const { runId, workflowId, inputPayload, nodes, edges, startNodeId } = event.data;

    await step.run("initialize-execution", async () => {
      updateRun(runId, {
        status: "running",
        startTime: new Date().toISOString(),
      });
      return { initialized: true };
    });

    let currentNodeId = startNodeId;
    let stepIndex = 0;
    const maxSteps = 15; // Prevent infinite loops in cyclic graphs

    while (currentNodeId && stepIndex < maxSteps) {
      stepIndex++;
      const node = nodes.find((n: any) => n.id === currentNodeId);
      if (!node) break;

      const isDecision = node.type === "decisionNode";
      const isAction = node.type === "actionNode";

      if (isDecision) {
        // Execute LLM decision inside durable Inngest step
        const evalResult = await step.run(
          `step-${stepIndex}-eval-${node.id}`,
          async () => {
            const prompt = node.data?.prompt || "Is this valid?";
            const { decision, latencyMs, raw } = await askDecision(prompt, inputPayload);

            const logEntry: ExecutionLogEntry = {
              timestamp: new Date().toISOString(),
              nodeId: node.id,
              nodeLabel: node.data?.label || node.id,
              stepName: `Evaluate: ${node.data?.label || node.id}`,
              prompt,
              decision,
              latencyMs,
              status: "success",
              details: `Model output: '${raw}'. Branch chosen: ${decision}`,
            };

            // Update shared state for live UI reflection
            updateRun(runId, {
              activeNodeId: node.id,
              visitedNodes: [node.id],
              decisions: { [node.id]: decision },
              logs: [logEntry],
            });

            return { decision, latencyMs };
          }
        );

        // Find the matching edge based on YES or NO
        const chosenDecision: DecisionResult = evalResult.decision;
        const matchingEdge = edges.find((e: any) => {
          if (e.source !== node.id) return false;
          // Check handle or edge condition
          const handle = (e.sourceHandle || "").toLowerCase();
          const condition = (e.data?.condition || "").toUpperCase();
          return handle === chosenDecision.toLowerCase() || condition === chosenDecision;
        });

        if (matchingEdge) {
          await step.run(`traverse-edge-${matchingEdge.id}`, async () => {
            updateRun(runId, {
              visitedEdges: [matchingEdge.id],
            });
            return { next: matchingEdge.target };
          });
          currentNodeId = matchingEdge.target;
        } else {
          // No outbound branch for this decision
          break;
        }
      } else if (isAction) {
        // Terminal Action node reached
        await step.run(`step-${stepIndex}-action-${node.id}`, async () => {
          const logEntry: ExecutionLogEntry = {
            timestamp: new Date().toISOString(),
            nodeId: node.id,
            nodeLabel: node.data?.label || node.id,
            stepName: `Final Action: ${node.data?.label || node.id}`,
            prompt: node.data?.description || "Terminal action executed",
            decision: "YES",
            latencyMs: 10,
            status: "success",
            details: `Workflow arrived at terminal node: ${node.data?.label || node.id}`,
          };

          updateRun(runId, {
            activeNodeId: node.id,
            visitedNodes: [node.id],
            logs: [logEntry],
          });

          return { completedNode: node.id };
        });
        break; // Terminal node reached
      } else {
        break;
      }
    }

    // Finalize execution
    await step.run("finalize-workflow", async () => {
      updateRun(runId, {
        status: "completed",
        activeNodeId: null,
        endTime: new Date().toISOString(),
      });
      return { completed: true };
    });

    return { runId, status: "completed", stepsExecuted: stepIndex };
  }
);
