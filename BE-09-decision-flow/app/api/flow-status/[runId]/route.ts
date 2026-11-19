import { NextResponse } from "next/server";
import { getRun } from "@/lib/executionStore";

export async function GET(
  req: Request,
  { params }: { params: { runId: string } }
) {
  const { runId } = params;
  const run = getRun(runId);

  if (!run) {
    return NextResponse.json(
      { error: `Run '${runId}' not found` },
      { status: 404 }
    );
  }

  return NextResponse.json(run, { status: 200 });
}
