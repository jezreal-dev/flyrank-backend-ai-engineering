import { NextResponse } from "next/server";
import { inngest } from "@/inngest/client";
import { saveRun } from "@/lib/executionStore";
import { WorkflowExecutionState } from "@/types/flow";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { workflowId, inputPayload, nodes, edges, startNodeId } = body;

    if (!inputPayload || typeof inputPayload !== "string") {
      return NextResponse.json(
        { error: "Input payload text is required" },
        { status: 400 }
      );
    }

    if (!nodes || !Array.isArray(nodes) || nodes.length === 0) {
      return NextResponse.json(
        { error: "Workflow requires at least one node" },
        { status: 400 }
      );
    }

    const runId = `run_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    const initialRun: WorkflowExecutionState = {
      runId,
      workflowId: workflowId || "default-workflow",
      inputPayload,
      status: "pending",
      activeNodeId: startNodeId || nodes[0].id,
      visitedNodes: [],
      visitedEdges: [],
      decisions: {},
      logs: [],
      startTime: new Date().toISOString(),
    };

    saveRun(initialRun);

    // Dispatch event to Inngest background engine
    await inngest.send({
      name: "workflow/execute",
      data: {
        runId,
        workflowId: workflowId || "default-workflow",
        inputPayload,
        nodes,
        edges,
        startNodeId: startNodeId || nodes[0].id,
      },
    });

    return NextResponse.json(
      {
        runId,
        status: "pending",
        message: "Workflow queued for execution with Inngest",
      },
      { status: 202 }
    );
  } catch (err: any) {
    console.error("Execution dispatch failed:", err);
    return NextResponse.json(
      { error: "Failed to dispatch workflow execution", details: err.message },
      { status: 500 }
    );
  }
}
