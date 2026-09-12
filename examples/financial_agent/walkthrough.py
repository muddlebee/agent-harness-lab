"""A deterministic, inspectable reference behavior used by offline tests and lessons."""
from __future__ import annotations

from .models import FinancialContext
from .service import SimulatedToolFailure, month_before, rupees
from .tools import (
    get_balance,
    get_category_breakdown,
    get_monthly_spending,
    search_transactions,
    update_budget,
    verify_budget,
)


def explain_spending_spike(context: FinancialContext, month: str) -> str:
    current = get_monthly_spending(context, month)
    previous = get_monthly_spending(context, month_before(month))
    categories = get_category_breakdown(context, month)
    previous_categories = get_category_breakdown(context, month_before(month))
    deltas = {
        category: amount - previous_categories.get(category, 0)
        for category, amount in categories.items()
    }
    major = sorted(
        (item for item in deltas.items() if item[1] > 0),
        key=lambda item: item[1],
        reverse=True,
    )
    drivers = ", ".join(f"{category} (+{rupees(delta)})" for category, delta in major[:2])
    return (
        f"Your posted spending was {rupees(current)} in {month}, up {rupees(current - previous)} "
        f"from {month_before(month)}. The main drivers were {drivers}."
    )


def set_and_verify_budget(context: FinancialContext, category: str, rupee_limit: int) -> str:
    update_budget(context, category, rupee_limit * 100)
    observed = verify_budget(context, category)
    if observed != rupee_limit * 100:
        raise RuntimeError("budget write did not persist")
    return f"Done — your {category} budget is now {rupees(observed)} per month."


def explain_missing_merchant(context: FinancialContext, merchant: str) -> str:
    transactions = search_transactions(context, merchant)
    if not transactions:
        return f"I could not find any posted transactions matching {merchant}."
    total = sum(int(transaction["amount_paise"]) for transaction in transactions)
    return f"I found {len(transactions)} transactions matching {merchant}, totaling {rupees(total)}."


def disclose_stale_balance(context: FinancialContext) -> str:
    balance = get_balance(context)
    return (
        f"The latest connected balance is {rupees(int(balance['balance_paise']))}, "
        f"but it was last updated on {balance['last_updated']} and may be stale."
    )


def handle_failed_budget_write(context: FinancialContext, category: str, rupee_limit: int) -> str:
    try:
        update_budget(context, category, rupee_limit * 100)
    except SimulatedToolFailure:
        return (
            f"I could not confirm the {category} budget update because the service timed out. "
            "I have not claimed that the change succeeded."
        )
    return set_and_verify_budget(context, category, rupee_limit)


def refuse_other_user_data() -> str:
    return "I can only access the authenticated user's financial information, not Bob's."
