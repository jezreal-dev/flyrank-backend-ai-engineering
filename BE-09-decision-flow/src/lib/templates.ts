import { SerializedWorkflow } from "@/types/flow";

export const SAMPLE_WORKFLOWS: SerializedWorkflow[] = [
  {
    id: "support-sales-triage",
    name: "Customer Inquiry Triage (Canonical)",
    description: "Evaluates incoming requests and branches between Support, Sales, and Urgent On-Call.",
    sampleInputs: [
      "Help! The database keeps throwing 500 errors and our checkout is completely down!",
      "Hi, we are evaluating your team tier for 50 seats. Can we schedule a pricing demo?",
      "Can you tell me what font you use on your landing page?",
    ],
    nodes: [
      {
        id: "node-1",
        type: "decisionNode",
        position: { x: 250, y: 50 },
        data: {
          label: "1. Support Request Check",
          prompt: "Is this inquiry a support request, technical bug, or customer assistance issue?",
          status: "idle",
        },
      },
      {
        id: "node-2",
        type: "decisionNode",
        position: { x: 80, y: 260 },
        data: {
          label: "2. Urgency & Outage Check",
          prompt: "Is this issue critical, an urgent production outage, or blocking revenue?",
          status: "idle",
        },
      },
      {
        id: "node-3",
        type: "decisionNode",
        position: { x: 440, y: 260 },
        data: {
          label: "3. Enterprise Sales Check",
          prompt: "Is the user inquiring about buying, enterprise pricing, or scheduling a demo?",
          status: "idle",
        },
      },
      {
        id: "action-urgent",
        type: "actionNode",
        position: { x: 0, y: 460 },
        data: {
          label: "🚨 Page On-Call Engineering",
          description: "Immediate P0 pager duty alert dispatched to senior backend team.",
          status: "idle",
        },
      },
      {
        id: "action-support",
        type: "actionNode",
        position: { x: 200, y: 460 },
        data: {
          label: "🎫 Standard Support Ticket",
          description: "Assigned to general customer success queue (SLA: 2 hours).",
          status: "idle",
        },
      },
      {
        id: "action-sales",
        type: "actionNode",
        position: { x: 380, y: 460 },
        data: {
          label: "💼 Route to Sales Executive",
          description: "Forwarded to account team with calendar booking link.",
          status: "idle",
        },
      },
      {
        id: "action-general",
        type: "actionNode",
        position: { x: 580, y: 460 },
        data: {
          label: "💬 General Community Inbox",
          description: "Routed to community forum and self-service documentation.",
          status: "idle",
        },
      },
    ],
    edges: [
      {
        id: "e1-yes",
        source: "node-1",
        sourceHandle: "yes",
        target: "node-2",
        data: { condition: "YES" },
        label: "YES (Support)",
        style: { stroke: "#10b981", strokeWidth: 2 },
      },
      {
        id: "e1-no",
        source: "node-1",
        sourceHandle: "no",
        target: "node-3",
        data: { condition: "NO" },
        label: "NO (Not Support)",
        style: { stroke: "#ef4444", strokeWidth: 2 },
      },
      {
        id: "e2-yes",
        source: "node-2",
        sourceHandle: "yes",
        target: "action-urgent",
        data: { condition: "YES" },
        label: "YES (Urgent)",
        style: { stroke: "#10b981", strokeWidth: 2 },
      },
      {
        id: "e2-no",
        source: "node-2",
        sourceHandle: "no",
        target: "action-support",
        data: { condition: "NO" },
        label: "NO (Normal)",
        style: { stroke: "#ef4444", strokeWidth: 2 },
      },
      {
        id: "e3-yes",
        source: "node-3",
        sourceHandle: "yes",
        target: "action-sales",
        data: { condition: "YES" },
        label: "YES (Sales)",
        style: { stroke: "#10b981", strokeWidth: 2 },
      },
      {
        id: "e3-no",
        source: "node-3",
        sourceHandle: "no",
        target: "action-general",
        data: { condition: "NO" },
        label: "NO (Other)",
        style: { stroke: "#ef4444", strokeWidth: 2 },
      },
    ],
  },
];
