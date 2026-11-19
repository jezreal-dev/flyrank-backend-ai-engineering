#!/usr/bin/env python3
"""
Stage 3: HTML-to-PDF Renderer for BE-08 PDF Report Generator.
Renders an HTML template into a multi-page PDF document using xhtml2pdf / Playwright.
Solves the page-break trap:
1. `tr { page-break-inside: avoid; break-inside: avoid; }` prevents rows from being sliced in half.
2. `<thead>` elements are structured to repeat table headers across page breaks.
"""

import os
from datetime import datetime
from typing import Any, Dict
from xhtml2pdf import pisa

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def generate_report_html(data: Dict[str, Any], generated_at: str = None) -> str:
    if not generated_at:
        generated_at = datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")

    summary = data.get("summary", {})
    total_orders = summary.get("total_orders", 0)
    total_revenue = summary.get("total_revenue", 0.0)
    top_products = data.get("top_products", [])
    daily_breakdown = data.get("daily_breakdown", [])
    all_orders = data.get("all_orders", [])

    # Format top 5 products rows
    top_products_rows = ""
    for idx, item in enumerate(top_products, start=1):
        top_products_rows += f"""
        <tr>
            <td style="text-align: center; width: 40px;">{idx}</td>
            <td style="font-weight: bold;">{item['product']}</td>
            <td style="text-align: right;">{item['units_sold']} units</td>
            <td style="text-align: right; font-weight: bold; color: #047857;">${item['revenue']:,.2f}</td>
        </tr>
        """

    # Format daily breakdown rows
    daily_rows = ""
    for item in daily_breakdown:
        daily_rows += f"""
        <tr>
            <td>{item['order_date']}</td>
            <td style="text-align: right;">{item['order_count']} orders</td>
            <td style="text-align: right; font-weight: bold;">${item['daily_revenue']:,.2f}</td>
        </tr>
        """

    # Format all ~200 orders rows (long table)
    orders_rows = ""
    for order in all_orders:
        orders_rows += f"""
        <tr>
            <td style="text-align: center;">#{order['id']}</td>
            <td>{order['created_at']}</td>
            <td>{order['customer']}</td>
            <td>{order['product']}</td>
            <td style="text-align: right; font-weight: bold;">${order['amount']:,.2f}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Executive Sales & Inventory Report</title>
<style>
    @page {{
        size: a4 portrait;
        margin: 1.5cm 1.5cm 1.8cm 1.5cm;
        @bottom-right {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 8pt;
            color: #64748b;
        }};
        @bottom-left {{
            content: "FlyRank Backend AI Engineering - BE-08 PDF Report Generator";
            font-size: 8pt;
            color: #64748b;
        }};
    }}

    body {{
        font-family: Helvetica, Arial, sans-serif;
        color: #0f172a;
        font-size: 9.5pt;
        line-height: 1.4;
    }}

    .header-box {{
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #0f172a;
    }}

    h1 {{
        font-size: 20pt;
        margin: 0 0 6px 0;
        color: #0f172a;
        font-weight: bold;
    }}

    .meta-subtitle {{
        font-size: 9pt;
        color: #64748b;
        margin: 0;
    }}

    /* Executive KPI cards */
    .kpi-container {{
        width: 100%;
        margin-bottom: 20px;
    }}

    .kpi-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 12px 0;
    }}

    .kpi-card {{
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        border-radius: 6px;
        text-align: left;
    }}

    .kpi-label {{
        font-size: 8pt;
        text-transform: uppercase;
        color: #64748b;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}

    .kpi-value {{
        font-size: 18pt;
        font-weight: bold;
        color: #0f172a;
        margin-top: 4px;
    }}

    h2 {{
        font-size: 12pt;
        color: #0f172a;
        margin: 22px 0 8px 0;
        border-bottom: 1px solid #cbd5e1;
        padding-bottom: 4px;
    }}

    /* Tables */
    table.data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 6px;
        margin-bottom: 16px;
    }}

    table.data-table th, table.data-table td {{
        border: 1px solid #e2e8f0;
        padding: 6px 8px;
        font-size: 8.5pt;
    }}

    table.data-table th {{
        background-color: #f1f5f9;
        color: #1e293b;
        font-weight: bold;
        text-align: left;
    }}

    /* The crucial page-break trap fixes */
    thead {{
        display: table-header-group;
    }}

    tr {{
        page-break-inside: avoid !important;
        break-inside: avoid !important;
    }}

    .page-break {{
        page-break-before: always;
    }}
</style>
</head>
<body>

<div class="header-box">
    <h1>Executive Sales & Inventory Report</h1>
    <p class="meta-subtitle">Automated Report Generator · Generated on: {generated_at} · Dataset: Store Orders (SQLite)</p>
</div>

<!-- Section 1: Top Totals -->
<div class="kpi-container">
    <table class="kpi-table">
        <tr>
            <td class="kpi-card" style="width: 50%;">
                <div class="kpi-label">Total Completed Orders</div>
                <div class="kpi-value">{total_orders:,}</div>
            </td>
            <td class="kpi-card" style="width: 50%;">
                <div class="kpi-label">Gross Revenue (USD)</div>
                <div class="kpi-value" style="color: #047857;">${total_revenue:,.2f}</div>
            </td>
        </tr>
    </table>
</div>

<!-- Section 2: Top 5 Products by Revenue -->
<h2>Top 5 Products by Revenue</h2>
<table class="data-table">
    <thead>
        <tr>
            <th style="text-align: center; width: 40px;">Rank</th>
            <th>Product Name</th>
            <th style="text-align: right; width: 100px;">Units Sold</th>
            <th style="text-align: right; width: 120px;">Total Revenue</th>
        </tr>
    </thead>
    <tbody>
        {top_products_rows}
    </tbody>
</table>

<!-- Section 3: Orders Per Day (Last 7 Days) -->
<h2>Daily Orders Summary (Last 7 Active Days)</h2>
<table class="data-table">
    <thead>
        <tr>
            <th>Order Date</th>
            <th style="text-align: right; width: 140px;">Orders Logged</th>
            <th style="text-align: right; width: 160px;">Daily Volume (USD)</th>
        </tr>
    </thead>
    <tbody>
        {daily_rows}
    </tbody>
</table>

<!-- Section 4: Full Orders Appendix (Long Table spanning across page breaks) -->
<h2 style="margin-top: 24px;">Full Order Ledger Appendix ({len(all_orders)} Orders)</h2>
<p style="font-size: 8pt; color: #64748b; margin-top: -4px; margin-bottom: 8px;">
    Complete historical ledger of orders. Headers automatically repeat on subsequent pages without slicing table rows.
</p>

<table class="data-table">
    <thead>
        <tr>
            <th style="text-align: center; width: 45px;">ID</th>
            <th style="width: 125px;">Timestamp</th>
            <th style="width: 110px;">Customer</th>
            <th>Product</th>
            <th style="text-align: right; width: 75px;">Amount</th>
        </tr>
    </thead>
    <tbody>
        {orders_rows}
    </tbody>
</table>

</body>
</html>
"""
    return html


def render_report_to_pdf(data: Dict[str, Any], output_path: str = None) -> str:
    if not output_path:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        output_path = os.path.join(REPORTS_DIR, "test.pdf")
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    html_content = generate_report_html(data)

    with open(output_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if pisa_status.err:
        raise RuntimeError(f"PDF generation failed with pisa error code: {pisa_status.err}")

    return output_path


if __name__ == "__main__":
    from report_data import get_report_data

    print("Fetching aggregation data from report.db...")
    data = get_report_data()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    test_pdf_path = os.path.join(REPORTS_DIR, "test.pdf")
    print(f"Rendering PDF to {test_pdf_path}...")
    rendered_file = render_report_to_pdf(data, test_pdf_path)

    file_size = os.path.getsize(rendered_file)
    print(f"Rendered successfully! File: {rendered_file} ({file_size} bytes)")
