from concurrent.futures import ThreadPoolExecutor

from examples.financial_agent.db import create_sandbox, seed_maya_spending_spike
from examples.financial_agent.service import FinancialService


def test_service_scopes_queries_to_authenticated_user() -> None:
    connection = create_sandbox()
    seed_maya_spending_spike(connection)
    service = FinancialService(connection)

    # Bob's ₹80k purchase must never appear in Maya's total.
    assert service.monthly_spending("maya", "2026-08") == 4_990_000


def test_pending_transactions_are_not_spend() -> None:
    connection = create_sandbox()
    seed_maya_spending_spike(connection)
    connection.execute(
        """INSERT INTO transactions(user_id, occurred_on, category, merchant, amount_paise, status)
        VALUES ('maya', '2026-08-29', 'shopping', 'Pending Shop', 3_000_000, 'pending')"""
    )
    assert FinancialService(connection).monthly_spending("maya", "2026-08") == 4_990_000


def test_sandbox_connection_is_usable_from_a_function_tool_worker() -> None:
    connection = create_sandbox()
    seed_maya_spending_spike(connection)

    with ThreadPoolExecutor(max_workers=1) as executor:
        total = executor.submit(
            lambda: connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        ).result()

    assert total == 11
