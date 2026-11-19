"""
Automated Pytest Suite for the Harness Engineering System
Verifies all three terminal states completely offline:
- Case 1: Compliant probe execution -> DONE (exit 0)
- Case 2: Tampered/Non-compliant probe -> BLOCKED (exit 2)
- Case 3: Tampered contract fingerprint -> BLOCKED (exit 2)
- Case 4: Non-converging infinite worker -> SAFETY_LIMIT (exit 3)
"""

import os
import sys
import json
import pytest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from runner import run_harness, CONTRACT_PATH, FINGERPRINT_PATH, RECEIPT_PATH, GAPS_PATH, STATE_PATH

def test_harness_ending_done():
    """Verify normal compliant execution produces DONE (exit code 0) and sealed receipt."""
    code, status = run_harness(worker_mode="success")
    assert code == 0
    assert status == "DONE"
    assert os.path.exists(RECEIPT_PATH)

    with open(RECEIPT_PATH, "r", encoding="utf-8") as f:
        receipt = json.load(f)
    assert receipt["harness_status"] == "DONE"
    assert receipt["status_code"] == 201
    assert "verified_invariants" in receipt

def test_harness_ending_blocked_on_gap():
    """Verify schema or status code violation triggers BLOCKED (exit code 2) and records gaps."""
    code, status = run_harness(worker_mode="tamper")
    assert code == 2
    assert status == "BLOCKED"
    assert os.path.exists(GAPS_PATH)

    with open(GAPS_PATH, "r", encoding="utf-8") as f:
        gaps_data = json.load(f)
    assert len(gaps_data["gaps"]) > 0

def test_harness_ending_blocked_on_fingerprint_tamper(monkeypatch):
    """Verify modifying contract or fingerprint triggers immediate BLOCKED (exit code 2)."""
    # Temporarily modify the fingerprint file
    with open(FINGERPRINT_PATH, "r", encoding="utf-8") as f:
        original_hash = f.read().strip()
    
    try:
        with open(FINGERPRINT_PATH, "w", encoding="utf-8") as f:
            f.write("0000000000000000000000000000000000000000000000000000000000000000")
        
        code, status = run_harness(worker_mode="success")
        assert code == 2
        assert status == "BLOCKED"
    finally:
        # Restore original fingerprint
        with open(FINGERPRINT_PATH, "w", encoding="utf-8") as f:
            f.write(original_hash)

def test_harness_ending_safety_limit():
    """Verify non-convergent worker hits max step ceiling and triggers SAFETY_LIMIT (exit code 3)."""
    code, status = run_harness(worker_mode="infinite_loop")
    assert code == 3
    assert status == "SAFETY_LIMIT"

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)
    assert state["state"] == "SAFETY_LIMIT"
    assert state["step"] == 5
