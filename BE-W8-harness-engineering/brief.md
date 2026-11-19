# Harness Brief: Task Ingestion Endpoint (`POST /tasks`)

**Target System:** Task API (`POST /tasks`)  
**Harness Role:** Verification & Guardrail Engine  
**Playbook Reference:** [https://github.com/flyrank-bih/harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook)

---

## 1. Job Description
Verify that the `POST /tasks` endpoint strictly conforms to the frozen production contract. The harness executes an end-to-end verification cycle against the live service without manual intervention, recording deterministic evidence to disk.

## 2. Source of Truth
The canonical standard is the frozen contract located at:
`contracts/post_tasks.contract.json`

The contract is sealed with a cryptographic SHA-256 fingerprint in:
`contracts/post_tasks.contract.fingerprint`

Any modification or tampering with the contract by the executing agent triggers an immediate `BLOCKED` halt.

## 3. Definition of Done
The run transitions to `DONE` if and only if all of the following conditions are simultaneously met:
1. **Contract Integrity:** The SHA-256 hash of `contracts/post_tasks.contract.json` matches the fingerprint.
2. **HTTP Invariant:** The endpoint returns HTTP status `201 Created` for valid input payloads.
3. **Schema Compliance:** The response contains fields `id` (string), `title` (string), `description` (string), `status` (enum: `pending` | `in_progress` | `completed`), and `created_at` (ISO timestamp).
4. **Latency Ceiling:** Response time is less than 500ms.
5. **Receipt on Disk:** A fresh measurement receipt is saved to `proofs/receipt.json` with matching request/response hashes.
6. **Safety Ceiling:** The total execution loop completes within the maximum step bound ($\le 5$ iterations).

---

## 4. Termination Endings
The harness runner supports exactly three terminal states:
- `DONE` (Exit code 0): Verification succeeded, all invariants satisfied, receipt sealed on disk.
- `BLOCKED` (Exit code 2): Precondition failed, schema mismatch, fingerprint invalid, or invariant violated.
- `SAFETY_LIMIT` (Exit code 3): Maximum execution steps reached without convergence.
