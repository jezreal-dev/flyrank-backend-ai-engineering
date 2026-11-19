"""
Stub Worker for Testing the Harness
Simulates agent execution under three distinct testing modes:
- "success": produces a valid, contract-compliant measurement receipt.
- "tamper": produces an invalid measurement (e.g. status 500, missing fields) or fails invariant.
- "infinite_loop": simulates an uncooperative agent that loops without converging.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

base_dir = os.path.dirname(os.path.abspath(__file__))

def execute_stub(mode="success"):
    result_path = os.path.join(base_dir, "proofs", "result.json")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)

    if mode == "success":
        # Compliant execution via probe
        from probe import run_probe
        return run_probe(output_path=result_path)

    elif mode == "tamper":
        # Non-compliant output violating the contract
        tampered_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/tasks",
            "method": "POST",
            "request_payload": {"title": "X"}, # Invalid title length
            "status_code": 500,                 # Internal Server Error violation
            "headers": {"content-type": "text/plain"},
            "response_body": {"error": "Broken schema invariant"},
            "latency_ms": 12.5,
            "content_hash": "deadbeef00000000000000000000000000000000000000000000000000000000"
        }
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(tampered_result, f, indent=2)
        return tampered_result

    elif mode == "infinite_loop":
        # Simulates repeated non-convergent attempt
        return {"status": "in_progress", "iteration": "stalled"}

    else:
        raise ValueError(f"Unknown stub mode: {mode}")

if __name__ == "__main__":
    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "success"
    print(f"[StubWorker] Running in mode: {mode_arg}")
    res = execute_stub(mode_arg)
    print(f"[StubWorker] Output generated.")
