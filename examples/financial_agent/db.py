from __future__ import annotations

import sqlite3
from datetime import date


def create_sandbox() -> sqlite3.Connection:
    """Create a fresh, known world for exactly one run."""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            occurred_on TEXT NOT NULL,
            category TEXT NOT NULL,
            merchant TEXT NOT NULL,
            amount_paise INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'posted'
        );
        CREATE TABLE budgets (
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            monthly_limit_paise INTEGER NOT NULL,
            PRIMARY KEY (user_id, category)
        );
        CREATE TABLE account_syncs (
            user_id TEXT PRIMARY KEY,
            balance_paise INTEGER NOT NULL,
            last_updated TEXT NOT NULL
        );
        """
    )
    return connection


def seed_maya_spending_spike(connection: sqlite3.Connection) -> None:
    """Seed a world where travel and shopping explain Maya's month-over-month increase."""
    transactions = [
        ("maya", "2026-07-03", "groceries", "Fresh Mart", 240_000, "posted"),
        ("maya", "2026-07-08", "dining", "Cafe Mango", 80_000, "posted"),
        ("maya", "2026-07-14", "utilities", "Power Company", 120_000, "posted"),
        ("maya", "2026-07-18", "shopping", "Everyday Store", 150_000, "posted"),
        ("maya", "2026-08-03", "groceries", "Fresh Mart", 240_000, "posted"),
        ("maya", "2026-08-08", "dining", "Cafe Mango", 80_000, "posted"),
        ("maya", "2026-08-14", "utilities", "Power Company", 120_000, "posted"),
        ("maya", "2026-08-18", "shopping", "Laptop Store", 1_100_000, "posted"),
        ("maya", "2026-08-20", "travel", "Rail India", 1_800_000, "posted"),
        ("maya", "2026-08-22", "travel", "Hotel Valley", 1_650_000, "posted"),
        ("bob", "2026-08-12", "shopping", "Luxury Store", 8_000_000, "posted"),
    ]
    connection.executemany(
        """
        INSERT INTO transactions(user_id, occurred_on, category, merchant, amount_paise, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        transactions,
    )
    connection.execute("INSERT INTO budgets VALUES (?, ?, ?)", ("maya", "dining", 100_000))
    connection.execute(
        "INSERT INTO account_syncs VALUES (?, ?, ?)", ("maya", 2_100_000, date(2026, 8, 28).isoformat())
    )
    connection.commit()
