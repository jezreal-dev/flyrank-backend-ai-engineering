import { serve } from "inngest/next";
import { inngest } from "@/inngest/client";
import { executeDecisionFlow } from "@/inngest/functions/decisionFlow";

export const { GET, POST, PUT } = serve({
  client: inngest,
  functions: [executeDecisionFlow],
});
