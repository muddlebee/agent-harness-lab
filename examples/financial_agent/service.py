from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field


class SimulatedToolFailure(RuntimeError):
    pass


@dataclass
class FailurePlan:
    """Scenario-controlled failures: useful to test recovery without random flakiness."""

    fail_on_call: dict[str, int] = field(default_factory=dict)
    calls: dict[str, int] = field(default_factory=dict)

    def before(self, operation: str) -> None:
        self.calls[operation] = self.calls.get(operation, 0) + 1
        if self.calls[operation] == self.fail_on_call.get(operation):
            raise SimulatedToolFailure(f"{operation} timed out (simulated)")


class FinancialService:
    """Backend contract used by production and eval sandbox."""

    def __init__(self, connection: sqlite3.Connection, failures: FailurePlan | None = None):
        self.connection = connection
        self.failures = failures or FailurePlan()

    def monthly_spending(self, user_id: str, month: str) -> int:
        self.failures.before("monthly_spending")
        row = self.connection.execute(
            """
            SELECT COALESCE(SUM(amount_paise), 0) AS total
            FROM transactions
            WHERE user_id = ? AND occurred_on >= ? AND occurred_on < date(?, '+1 month')
              AND status = 'posted'
            """,
            (user_id, f"{month}-01", f"{month}-01"),
        ).fetchone()
        return int(row["total"])

    def category_breakdown(self, user_id: str, month: str) -> dict[str, int]:
        self.failures.before("category_breakdown")
        rows = self.connection.execute(
            """
            SELECT category, SUM(amount_paise) AS total
            FROM transactions
            WHERE user_id = ? AND occurred_on >= ? AND occurred_on < date(?, '+1 month')
              AND status = 'posted'
            GROUP BY category ORDER BY total DESC
            """,
            (user_id, f"{month}-01", f"{month}-01"),
        ).fetchall()
        return {str(row["category"]): int(row["total"]) for row in rows}

    def set_budget(self, user_id: str, category: str, monthly_limit_paise: int) -> None:
        self.failures.before("set_budget")
        self.connection.execute(
            """
            INSERT INTO budgets(user_id, category, monthly_limit_paise) VALUES (?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit_paise = excluded.monthly_limit_paise
            """,
            (user_id, category, monthly_limit_paise),
        )
        self.connection.commit()

    def get_budget(self, user_id: str, category: str) -> int | None:
        self.failures.before("get_budget")
        row = self.connection.execute(
            "SELECT monthly_limit_paise FROM budgets WHERE user_id = ? AND category = ?",
            (user_id, category),
        ).fetchone()
        return None if row is None else int(row["monthly_limit_paise"])

    def search_transactions(self, user_id: str, merchant: str) -> list[dict[str, str | int]]:
        self.failures.before("search_transactions")
        rows = self.connection.execute(
            """
            SELECT occurred_on, category, merchant, amount_paise, status
            FROM transactions
            WHERE user_id = ? AND lower(merchant) LIKE lower(?)
            ORDER BY occurred_on DESC
            """,
            (user_id, f"%{merchant}%"),
        ).fetchall()
        return [
            {
                "occurred_on": str(row["occurred_on"]),
                "category": str(row["category"]),
                "merchant": str(row["merchant"]),
                "amount_paise": int(row["amount_paise"]),
                "status": str(row["status"]),
            }
            for row in rows
        ]

    def balance(self, user_id: str) -> dict[str, str | int]:
        self.failures.before("balance")
        row = self.connection.execute(
            "SELECT balance_paise, last_updated FROM account_syncs WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if row is None:
            raise LookupError("no connected account")
        return {
            "balance_paise": int(row["balance_paise"]),
            "last_updated": str(row["last_updated"]),
        }


def rupees(paise: int) -> str:
    return f"₹{paise / 100:,.0f}"


def month_before(month: str) -> str:
    year, month_number = map(int, month.split("-"))
    return f"{year - 1}-12" if month_number == 1 else f"{year}-{month_number - 1:02d}"
