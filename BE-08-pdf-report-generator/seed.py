#!/usr/bin/env python3
"""
Stage 1: Seed script for BE-08 PDF Report Generator.
Creates report.db and seeds ~200 orders across the last 30 days.
Idempotent: deletes all existing rows before inserting, ensuring running twice leaves exactly 200 rows.
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "report.db")

PRODUCTS = [
    "Ergonomic Chair",
    "Mechanical Keyboard",
    "UltraWide Monitor",
    "Noise-Cancelling Headphones",
    "USB-C Docking Station",
    "Smart Desk Lamp",
]

CUSTOMERS = [
    "Alice Johnson",
    "Bob Smith",
    "Carol Davis",
    "David Wilson",
    "Emma Brown",
    "Frank Miller",
    "Grace Lee",
    "Henry Taylor",
    "Isla Clark",
    "Jack White",
    "Karen Scott",
    "Liam Adams",
    "Mia Roberts",
    "Noah Evans",
    "Olivia Campbell",
]


def init_db(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def seed_orders(count: int = 200) -> int:
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cursor = conn.cursor()

    # Rule: start by deleting all rows so running it twice leaves exactly one clean copy
    cursor.execute("DELETE FROM orders")
    conn.commit()

    # Fix seed for reproducible baseline amounts and dates
    random.seed(42)
    now = datetime.now()

    rows = []
    for _ in range(count):
        customer = random.choice(CUSTOMERS)
        product = random.choice(PRODUCTS)
        # Amounts between 15.00 and 195.00
        amount = round(random.uniform(15.0, 195.0), 2)
        # Random dates in the last 30 days
        days_ago = random.randint(0, 29)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        order_date = (now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((customer, product, amount, order_date))

    cursor.executemany(
        """
        INSERT INTO orders (customer, product, amount, created_at)
        VALUES (?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM orders")
    total = cursor.fetchone()[0]
    conn.close()
    return total


if __name__ == "__main__":
    count = seed_orders(200)
    print(f"Seeded report.db: {count} orders present in table 'orders'.")
