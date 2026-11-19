#!/usr/bin/env python3
"""
Comprehensive test script for BE-08 PDF Report Generator API.
Validates Stage 4 endpoints and Stage 5 idempotency logic.
"""

import os
import sys
from fastapi.testclient import TestClient

from main import app, get_db_connection
from seed import seed_orders

client = TestClient(app)


def run_tests():
    print("=== 1. Seeding test database ===")
    count = seed_orders(200)
    print(f"Seeded {count} orders.")

    # Clean existing reports table for clean test run
    conn = get_db_connection()
    conn.cursor().execute("DELETE FROM reports")
    conn.commit()
    conn.close()

    print("\n=== 2. Testing GET /health ===")
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
    print("✓ GET /health: 200 OK")

    print("\n=== 3. Testing POST /reports (Stage 4 Checkpoint) ===")
    res1 = client.post("/reports")
    print("POST /reports status:", res1.status_code)
    print("POST /reports body:", res1.json())
    assert res1.status_code == 201
    data1 = res1.json()
    report_id_1 = data1["id"]
    file_endpoint_1 = data1["file"]
    assert file_endpoint_1 == f"/reports/{report_id_1}/file"
    print(f"✓ Generated Report #{report_id_1}")

    print("\n=== 4. Testing GET /reports/:id (Metadata) ===")
    res_meta = client.get(f"/reports/{report_id_1}")
    assert res_meta.status_code == 200
    meta = res_meta.json()
    assert meta["id"] == report_id_1
    assert os.path.exists(meta["path"])
    print(f"✓ Metadata verified. File exists on disk: {meta['path']}")

    print("\n=== 5. Testing GET /reports/:id/file (Download PDF) ===")
    res_file = client.get(file_endpoint_1)
    assert res_file.status_code == 200
    assert res_file.headers["content-type"] == "application/pdf"
    pdf_bytes = res_file.content
    print(f"✓ Downloaded PDF. Size: {len(pdf_bytes)} bytes. Starts with %PDF: {pdf_bytes.startswith(b'%PDF')}")
    assert pdf_bytes.startswith(b"%PDF")

    print("\n=== 6. Testing 404 for unknown report ID ===")
    res_404 = client.get("/reports/999999")
    assert res_404.status_code == 404
    print("✓ GET /reports/999999 returned 404 Not Found")

    print("\n=== 7. Testing Stage 5 Idempotency (Ask twice, get one) ===")
    # Fire second POST immediately without force
    res2 = client.post("/reports")
    print("Second POST /reports status:", res2.status_code)
    print("Second POST /reports body:", res2.json())
    assert res2.status_code == 200  # Idempotent return should be 200 OK
    data2 = res2.json()
    assert data2["id"] == report_id_1, f"Expected same ID {report_id_1}, got {data2['id']}"
    print("✓ Second request returned existing report ID (200 OK) without generating duplicate file!")

    print("\n=== 8. Testing Stage 5 Force Bypass ({'force': True}) ===")
    res3 = client.post("/reports", json={"force": True})
    print("Forced POST /reports status:", res3.status_code)
    print("Forced POST /reports body:", res3.json())
    assert res3.status_code == 201
    data3 = res3.json()
    assert data3["id"] != report_id_1, f"Expected new ID, got {data3['id']}"
    print(f"✓ Forced request generated fresh Report #{data3['id']} (201 Created)")

    print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    run_tests()
