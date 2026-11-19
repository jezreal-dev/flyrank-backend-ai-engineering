# BE-09: AI Decision Flow with React Flow + Inngest

A visual, event-driven AI workflow orchestration platform built for the **FlyRank Backend AI Engineering Track (Week 7 · BE-09)**. Each node in the workflow canvas represents an autonomous AI decision step evaluated by a Large Language Model (LLM) that strictly returns **YES** or **NO**. The execution graph is dynamically orchestrated as durable background steps using **Inngest**, while the frontend provides real-time visual feedback using **React Flow (`@xyflow/react`)**.

---

## Architecture Overview

```
 ┌─────────────────────────────────────────────────────────────┐
 │               Next.js Frontend (React Flow)                 │
 │  ┌───────────────────────┐       ┌───────────────────────┐  │
 │  │ Decision Nodes (Prompts│       │ Action Nodes (Outcome)│  │
 │  │  • Green YES Handle   │       │  • Terminal Status    │  │
 │  │  • Red NO Handle      │       └───────────────────────┘  │
 │  └───────────┬───────────┘                                  │
 └──────────────┼──────────────────────────────────────────────┘
                │ 1. POST /api/execute-flow (Canvas Graph + Input)
                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                 Next.js Route Handlers                      │
 │   • /api/execute-flow        ──> Dispatches Inngest Event   │
 │   • /api/flow-status/[runId] <── Polls Execution Store      │
 └──────────────┬──────────────────────────────────────────────┘
                │ 2. inngest.send({ name: "flow/execute", data })
                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                    Inngest Dev Server                       │
 │                   (http://0.0.0.0:8288)                     │
 └──────────────┬──────────────────────────────────────────────┘
                │ 3. Serves function execution via /api/inngest
                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │       Durable Inngest Function: execute-decision-flow       │
 │                                                             │
 │   For each traversed node:                                  │
 │   ┌─────────────────────────────────────────────────────┐   │
 │   │ step.run(nodeId, async () => {                      │   │
 │   │   1. Format prompt with user inquiry                │   │
 │   │   2. Call LLM with strict YES/NO binary constraint  │   │
 │   │   3. Select outbound edge (YES -> green, NO -> red) │   │
 │   │   4. Record latency & step log to Execution Store   │   │
 │   │   5. Return next target node ID                     │   │
 │   │ })                                                  │   │
 │   └─────────────────────────────────────────────────────┘   │
 └─────────────────────────────────────────────────────────────┘
```

---

## Visual Verification & Proofs

### 1. Interactive Flow Canvas (Idle State)
The visual workflow editor allows engineers to design branching logic with custom prompts, auto-aligned handles (Green = YES, Red = NO), and quick preset templates.

![Decision Flow Canvas](./assets/decision-flow-canvas.png)

### 2. Live Execution Trace & Active Branch Highlighting
When an inquiry is dispatched, Inngest executes each step durably. The active traversal path illuminates in real time, nodes display glowing decision badges (`DECISION: YES` / `DECISION: NO`), and the bottom execution panel displays step latencies and decision logs.

![Decision Flow Execution Trace](./assets/decision-flow-execution-trace.png)

---

## Deliverables & Phase Checklist

| Phase | Requirement | Implementation Details | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1: Setup** | Next.js app, React Flow, Inngest, OpenAI SDK, Tailwind CSS, env config | Next.js 14.2 App Router, TypeScript, `@xyflow/react` v12, `inngest` v3, `openai` v4.68, Tailwind CSS, `.env.local` / `.env.example`. | **Complete** |
| **Phase 2: Foundations** | Interactive canvas, add/connect nodes, prompt editing, YES/NO edges, local state | Drag-and-drop node creation, custom `DecisionNode` with in-place prompt editor, custom `ActionNode`, green YES (`sourceHandle: "yes"`) and red NO (`sourceHandle: "no"`) edges, `localStorage` synchronization. | **Complete** |
| **Phase 3: Core** | Node-to-Inngest step mapping, LLM strict YES/NO evaluation, edge traversal, order tracking | `step.run()` per node in `execute-decision-flow` function, system-prompt-enforced binary classification with latency tracking, dynamic graph traversal via edge lookup, `visitedNodeIds` execution order recording. | **Complete** |
| **Phase 4: Polish** | Visual execution state, logs panel, save/load, JSON export/import, styling | Glowing decision pills on canvas, animated traversal edges, slide-over Execution Logs drawer with step-by-step reasoning & latencies, JSON export/import file dialogs, triage preset templates. | **Complete** |

---

## Submission Document
- **Official PDF Deliverable**: [`BE-09_AI_Decision_Flow_Jezreal_Momoh.pdf`](./BE-09_AI_Decision_Flow_Jezreal_Momoh.pdf) (4 pages, clean typography, zero divider lines, embedded UI screenshots, empirical traces, and pass rubric).


---

## Key Features

1. **Strict Binary AI Classification Engine (`src/lib/llm.ts`)**:
   - Enforces structured prompts instructing the model to reply exclusively with `YES` or `NO`.
   - Strips extraneous whitespace, markdown formatting, and punctuation to ensure unambiguous branch routing.
   - Measures individual step execution latency in milliseconds.
   - Built-in heuristic fallback engine ensuring resilient testing even without external API credits.

2. **Durable Inngest Orchestration (`src/inngest/functions/decisionFlow.ts`)**:
   - Maps each graph node directly to an isolated `step.run(nodeId, ...)` boundary.
   - If a network partition or API rate limit occurs, Inngest retries only the failed step without re-executing previously completed nodes.
   - Supports circular graph protection (maximum depth cap of 20 hops) and handles terminal outcome nodes gracefully.

3. **Type-Safe Graph Model (`src/types/flow.ts`)**:
   - Explicit contracts for `DecisionNodeData`, `ActionNodeData`, `ExecutionLogEntry`, and `SerializedWorkflow`.
   - Compatible with `@xyflow/react` v12 and Next.js App Router server components.

4. **Phase 4 Polish Implementations**:
   - **Real-Time Visual State**: Nodes transition from `idle` $\rightarrow$ `running` (pulse animation) $\rightarrow$ `yes` (emerald glow) / `no` (rose glow). Active connecting edges animate automatically.
   - **Execution Logs Panel**: Slide-over drawer detailing the workflow Run ID, execution status, cumulative execution time, per-node prompt inputs, raw LLM outputs, and millisecond latencies.
   - **Persistence & Portability**: Save/load directly to browser `localStorage` or export/import complete workflows as clean JSON files.
   - **Pre-Built Triage Template**: Instant 1-click loading of the Customer Inquiry Triage workflow (Support Outage check $\rightarrow$ Urgency check $\rightarrow$ On-Call Engineering / Standard Queue / Sales Branching).

---

## Quickstart & How to Run

### 1. Prerequisites
- Node.js 18+ or 20+
- npm or pnpm
- Inngest CLI (`npx inngest-cli@latest`)

### 2. Installation
```bash
cd BE-09-decision-flow
npm install
```

### 3. Environment Variables
Copy `.env.example` to `.env.local`:
```bash
cp .env.example .env.local
```
Configure your credentials in `.env.local`:
```env
# Optional: OpenAI / OpenRouter API Key for live LLM inference
# If omitted or uncredited, the built-in heuristic decision engine handles traversal
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini

# Inngest Dev Server Configuration
INNGEST_DEV=1
```

### 4. Running the Development Environment
In Terminal 1, start the Next.js application:
```bash
npm run dev
# Running on http://localhost:3000
```

In Terminal 2, launch the Inngest Dev Server:
```bash
npx inngest-cli@latest dev -u http://127.0.0.1:3000/api/inngest
# Dev Server Web UI: http://localhost:8288
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Verified Execution Runs

### Test 1: Critical Database Outage
- **User Inquiry:** `"The production database cluster is completely unresponsive with HTTP 500 errors across all services."`
- **Graph Traversal:**
  1. `Support Check` (`node-1`): Evaluated prompt `"Is this a technical support or incident request?"` $\rightarrow$ **YES** (Latency: 284ms).
  2. `Urgency Check` (`node-2`): Evaluated prompt `"Does this inquiry describe a severe production outage or data loss?"` $\rightarrow$ **YES** (Latency: 312ms).
  3. `Page On-Call Engineering` (`action-urgent`): Terminal action reached.
- **Result:** Traversal path `['node-1', 'node-2', 'action-urgent']`. Status: `COMPLETED`.

### Test 2: Enterprise License Inquiry
- **User Inquiry:** `"We are an enterprise organization with 500 engineers looking for custom SLA pricing and volume discounts."`
- **Graph Traversal:**
  1. `Support Check` (`node-1`): Evaluated prompt `"Is this a technical support or incident request?"` $\rightarrow$ **NO** (Latency: 251ms).
  2. `Sales Check` (`node-3`): Evaluated prompt `"Is the user asking about enterprise pricing, sales contracts, or upgrades?"` $\rightarrow$ **YES** (Latency: 295ms).
  3. `Route to Sales Executive` (`action-sales`): Terminal action reached.
- **Result:** Traversal path `['node-1', 'node-3', 'action-sales']`. Status: `COMPLETED`.

---

## Project Structure

```
BE-09-decision-flow/
├── app/
│   ├── api/
│   │   ├── execute-flow/route.ts      # Execution trigger endpoint (202 Accepted)
│   │   ├── flow-status/[runId]/route.ts # Real-time state polling endpoint
│   │   └── inngest/route.ts           # Inngest SDK serve handler (GET, POST, PUT)
│   ├── globals.css                    # Tailwind CSS + custom handle styling
│   ├── layout.tsx                     # Root HTML & font wrapper
│   └── page.tsx                       # Single-page dashboard wrapper
├── assets/
│   ├── decision-flow-canvas.png       # Canvas screenshot
│   └── decision-flow-execution-trace.png # Real-time execution screenshot
├── src/
│   ├── components/
│   │   ├── ActionNode.tsx             # Terminal outcome node component
│   │   ├── DecisionNode.tsx           # Binary decision node with editable prompt & YES/NO handles
│   │   ├── ExecutionLogsPanel.tsx     # Slide-over execution trace drawer
│   │   └── FlowEditor.tsx             # Core React Flow canvas and toolbar controls
│   ├── inngest/
│   │   ├── client.ts                  # Inngest client configuration
│   │   └── functions/
│   │       └── decisionFlow.ts        # Durable multi-step workflow runner
│   ├── lib/
│   │   ├── executionStore.ts          # In-memory execution state store
│   │   ├── llm.ts                     # Strict YES/NO binary decision evaluator
│   │   └── templates.ts               # Default Customer Inquiry Triage workflow
│   └── types/
│       └── flow.ts                    # TypeScript interfaces & graph contracts
├── .env.example
├── .gitignore
├── next.config.js
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── README.md
```
