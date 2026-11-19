"""
Harness Runner: State Machine, Guardrail, and Verification Engine
Implements the 3-ending protocol:
- DONE (Exit 0): All contracts verified, invariants hold, receipt sealed on disk.
- BLOCKED (Exit 2): Contract altered, invariant violated, or preconditions unmet.
- SAFETY_LIMIT (Exit 3): Max iterations reached without convergence.
"""

import os
import sys
import json
import hashlib
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONTRACT_PATH = os.path.join(BASE_DIR, "contracts", "post_tasks.contract.json")
FINGERPRINT_PATH = os.path.join(BASE_DIR, "contracts", "post_tasks.contract.fingerprint")
STATE_PATH = os.path.join(BASE_DIR, "state.json")
RESULT_PATH = os.path.join(BASE_DIR, "proofs", "result.json")
RECEIPT_PATH = os.path.join(BASE_DIR, "proofs", "receipt.json")
GAPS_PATH = os.path.join(BASE_DIR, "proofs", "gaps.json")
MAX_STEPS = 5

def verify_contract_fingerprint():
    """Step 4: Lock contracts. Seals the contract with a fingerprint that cannot be edited."""
    if not os.path.exists(CONTRACT_PATH) or not os.path.exists(FINGERPRINT_PATH):
        return False, "Contract or fingerprint file missing."
    
    with open(CONTRACT_PATH, "rb") as f:
        contract_bytes = f.read()
    actual_hash = hashlib.sha256(contract_bytes).hexdigest()

    with open(FINGERPRINT_PATH, "r", encoding="utf-8") as f:
        expected_hash = f.read().strip()

    if actual_hash != expected_hash:
        return False, f"Contract fingerprint mismatch! Expected {expected_hash}, got {actual_hash}"
    return True, actual_hash

def update_state(state, step, message=""):
    data = {
        "state": state,
        "step": step,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "message": message
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data

def run_harness(worker_mode="success"):
    print("=" * 72)
    print("HARNESS RUNNER · STATE MACHINE & GUARDRAIL ENGINE")
    print(f"Target: POST /tasks | Worker Mode: {worker_mode}")
    print("=" * 72)

    update_state("INITIALIZING", 0, "Checking prerequisites...")

    # Step 1: Verify contract fingerprint
    valid, fp_msg = verify_contract_fingerprint()
    if not valid:
        print(f"[GUARDRAIL BLOCKED] {fp_msg}")
        update_state("BLOCKED", 0, fp_msg)
        return 2, "BLOCKED"

    print(f"[Fingerprint Lock] Contract verified: {fp_msg[:16]}... OK")

    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract = json.load(f)

    # Step 2: Loop with safety ceiling
    from stub_worker import execute_stub

    for step in range(1, MAX_STEPS + 1):
        update_state("RUNNING", step, f"Executing worker step {step}/{MAX_STEPS}")
        print(f"[Step {step}/{MAX_STEPS}] Invoking worker (mode: {worker_mode})...")

        if worker_mode == "infinite_loop":
            execute_stub(mode="infinite_loop")
            print(f"  -> Worker stalled in non-converging state.")
            continue

        # Execute worker
        execute_stub(mode=worker_mode)

        if not os.path.exists(RESULT_PATH):
            update_state("BLOCKED", step, "Result file missing after execution.")
            return 2, "BLOCKED"

        with open(RESULT_PATH, "r", encoding="utf-8") as f:
            result = json.load(f)

        # Step 5 & 6: Source vs Copy & Proof on Disk
        gaps = []

        # Check HTTP Status Code
        if result.get("status_code") != contract["response"]["expected_status"]:
            gaps.append(f"Expected status {contract['response']['expected_status']}, received {result.get('status_code')}")

        # Check Latency
        if result.get("latency_ms", 9999) > contract["invariants"]["max_latency_ms"]:
            gaps.append(f"Latency {result.get('latency_ms')}ms exceeded ceiling {contract['invariants']['max_latency_ms']}ms")

        # Check Body & Required Fields
        body = result.get("response_body")
        if not isinstance(body, dict):
            gaps.append("Response body is not a JSON object")
        else:
            for field in contract["response"]["required_fields"]:
                if field not in body:
                    gaps.append(f"Missing required response field: '{field}'")
            
            # Check Status Enum
            if body.get("status") not in contract["response"]["allowed_statuses"]:
                gaps.append(f"Invalid status value: '{body.get('status')}'")
            
            # Check ID format invariant
            if not str(body.get("id", "")).startswith(contract["invariants"]["immutable_id_format"]):
                gaps.append(f"Task ID '{body.get('id')}' does not start with '{contract['invariants']['immutable_id_format']}'")

        if gaps:
            print(f"  -> GAPS DETECTED ({len(gaps)} violations):")
            for g in gaps:
                print(f"     * {g}")
            with open(GAPS_PATH, "w", encoding="utf-8") as f:
                json.dump({"step": step, "gaps": gaps, "timestamp": datetime.now(timezone.utc).isoformat()}, f, indent=2)
            
            update_state("BLOCKED", step, f"Contract invariant violation: {gaps[0]}")
            return 2, "BLOCKED"

        # SUCCESS: Write receipt on disk
        receipt = {
            "harness_status": "DONE",
            "step": step,
            "contract_fingerprint": fp_msg,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": contract["endpoint"],
            "method": contract["method"],
            "status_code": result["status_code"],
            "latency_ms": result["latency_ms"],
            "response_body": body,
            "content_hash": result["content_hash"],
            "verified_invariants": [
                "HTTP Status == 201 Created",
                "Schema fields [id, title, description, status, created_at] verified",
                "Allowed status in ('pending', 'in_progress', 'completed')",
                "Latency < 500ms ceiling",
                "Contract SHA-256 fingerprint verified"
            ]
        }
        with open(RECEIPT_PATH, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2)

        print(f"  -> VERIFICATION COMPLETE: 0 gaps. Proof sealed to proofs/receipt.json.")
        update_state("DONE", step, "Contract satisfied, proof sealed.")
        return 0, "DONE"

    # If loop finishes without returning, safety limit hit
    print(f"[SAFETY LIMIT HIT] Maximum steps ({MAX_STEPS}) reached without convergence.")
    update_state("SAFETY_LIMIT", MAX_STEPS, "Maximum step budget exhausted.")
    return 3, "SAFETY_LIMIT"

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "success"
    code, status = run_harness(mode)
    print(f"\n[HARNESS EXIT] Code: {code} ({status})")
    sys.exit(code)
