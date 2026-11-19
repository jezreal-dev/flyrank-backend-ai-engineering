# Harness Project Router (File-Based RAG)

This router acts as the index for the agent. Instead of passing one massive monolithic prompt into the model's context window, the agent reads this router to locate targeted context files on demand.

---

## Guide Index

| Topic | Target File | Scope & Usage |
| :--- | :--- | :--- |
| **Operational Rules & Hard-Won Facts** | [`guides/lessons.md`](./lessons.md) | Ground-truth engineering fixes and anti-patterns. |
| **Endpoint Contract Specification** | [`contracts/post_tasks.contract.json`](../contracts/post_tasks.contract.json) | The frozen schema and invariant definitions. |
| **Execution Job Brief** | [`brief.md`](../brief.md) | Job scope, definition of done, and termination states. |
| **Measurement Proofs** | [`proofs/receipt.json`](../proofs/receipt.json) | The fresh measurement file written on disk. |

---

## "Wrote It Down" vs. "Proved It"
- **Wrote It Down:** A prompt asserting *"The endpoint works and returns 201."* This is unverified text.
- **Proved It:** A probe measuring the actual endpoint, hashing the response bytes, validating the schema, and writing a cryptographic receipt to disk. The harness only accepts the latter.
