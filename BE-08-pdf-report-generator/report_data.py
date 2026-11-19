#!/usr/bin/env python3
"""
Stage 2: SQL Aggregation module for BE-08 PDF Report Generator.
Aggregates ~200 orders into 4 key business sections:
1. Total number of orders (COUNT)
2. Total revenue (SUM(amount))
3. Top 5 products by revenue (GROUP BY product ORDER BY revenue DESC LIMIT 5)
4. Orders per day for the last 7 days (GROUP BY date(created_at) ORDER BY date DESC LIMIT 7)
Also retrieves detailed orders for the document appendix table.
"""

import os
import sqlite3
from typing import Any, Dict, List

DB_PATH = os.path.join(os.path.dirname(__file__), "report.db")


def get_report_data(db_path: str = DB_PATH) -> Dict[str, Any]:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}. Please run seed.py first.")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Total number of orders
    cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
    total_orders = cursor.fetchone()["total_orders"]

    # 2. Total revenue
    cursor.execute("SELECT ROUND(COALESCE(SUM(amount), 0.0), 2) as total_revenue FROM orders")
    total_revenue = cursor.fetchone()["total_revenue"]

    # 3. Top 5 products by revenue
    cursor.execute(
        """
        SELECT 
            product,
            ROUND(SUM(amount), 2) as revenue,
            COUNT(*) as units_sold
        FROM orders
        GROUP BY product
        ORDER BY revenue DESC
        LIMIT 5
        """
    )
    top_products = [
        {"product": row["product"], "revenue": row["revenue"], "units_sold": row["units_sold"]}
        for row in cursor.fetchall()
    ]

    # 4. Orders per day for the last 7 recorded days
    cursor.execute(
        """
        SELECT 
            substr(created_at, 1, 10) as order_date,
            COUNT(*) as order_count,
            ROUND(SUM(amount), 2) as daily_revenue
        FROM orders
        GROUP BY order_date
        ORDER BY order_date DESC
        LIMIT 7
        """
    )
    recent_daily_orders = [
        {"order_date": row["order_date"], "order_count": row["order_count"], "daily_revenue": row["daily_revenue"]}
        for row in cursor.fetchall()
    ]

    # Detailed all orders for the document table (used in Stage 3 long table)
    cursor.execute(
        """
        SELECT id, customer, product, amount, created_at
        FROM orders
        ORDER BY created_at DESC
        """
    )
    all_orders = [
        {
            "id": row["id"],
            "customer": row["customer"],
            "product": row["product"],
            "amount": row["amount"],
            "created_at": row["created_at"],
        }
        for row in cursor.fetchall()
    ]

    conn.close()

    return {
        "summary": {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
        },
        "top_products": top_products,
        "daily_breakdown": recent_daily_orders,
        "all_orders": all_orders,
    }


if __name__ == "__main__":
    import json

    data = get_report_data()
    # Print clean JSON without dumping the full 200 orders to console
    summary_preview = {
        "summary": data["summary"],
        "top_5_products": data["top_products"],
        "last_7_days_orders": data["daily_breakdown"],
        "total_detailed_orders_count": len(data["all_orders"]),
    }
    print(json.dumps(summary_preview, indent=2))
