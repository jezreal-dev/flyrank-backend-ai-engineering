"""
AI-Generated Version (Quarantined Reference Implementation).
Represents the typical output when an AI is asked to "generate a PDF report backend"
without specific production guardrails.

Notice the 5 classic mistakes:
1. SELECT * into memory and aggregating in Python loops (N+1 / high memory).
2. Sliced table rows (no @page or page-break-inside: avoid).
3. Returning base64 encoded PDF directly in JSON payload (passing 20MB around).
4. No idempotency check (double click creates duplicate reports).
5. Synchronous blocking handler without job queue support.
"""

import base64
import os
import sqlite3
from io import BytesIO
from fastapi import FastAPI
from xhtml2pdf import pisa

app = FastAPI(title="AI Naive Report Generator")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "report.db")


@app.post("/generate-report")
def generate_report():
    # Pitfall 1: Querying ALL rows into memory instead of SQL aggregation
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT customer, product, amount, created_at FROM orders")
    all_orders = cursor.fetchall()
    conn.close()

    total_orders = len(all_orders)
    total_revenue = 0.0
    product_revenue = {}

    for row in all_orders:
        amt = row[2]
        prod = row[1]
        total_revenue += amt
        product_revenue[prod] = product_revenue.get(prod, 0.0) + amt

    # Sort in python
    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

    # Pitfall 2: Basic HTML without print CSS page break rules
    html = f"""
    <html>
    <body>
        <h1>Sales Report</h1>
        <p>Total Revenue: ${total_revenue:.2f}</p>
        <p>Total Orders: {total_orders}</p>
        <h2>Top Products</h2>
        <table>
            <tr><th>Product</th><th>Revenue</th></tr>
            {"".join(f"<tr><td>{p[0]}</td><td>${p[1]:.2f}</td></tr>" for p in top_products)}
        </table>
        <h2>All Orders</h2>
        <table>
            <tr><th>Customer</th><th>Product</th><th>Amount</th></tr>
            {"".join(f"<tr><td>{o[0]}</td><td>{o[1]}</td><td>${o[2]:.2f}</td></tr>" for o in all_orders)}
        </table>
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    # Pitfall 3: Returning Base64 encoded PDF directly in JSON response!
    # Pitfall 4: No idempotency check
    # Pitfall 5: Blocking synchronous generation
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    return {
        "status": "success",
        "file_name": "sales-report.pdf",
        "size_bytes": len(pdf_bytes),
        "data_base64": encoded_pdf,
    }
