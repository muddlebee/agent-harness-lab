from __future__ import annotations

from .models import FinancialContext


def _invoke(context: FinancialContext, name: str, arguments: dict, callback):
    try:
        result = callback()
    except Exception as error:
        context.trace.record_error(name, arguments, error)
        raise
    context.trace.record_success(name, arguments, result)
    return result


def get_monthly_spending(context: FinancialContext, month: str) -> int:
    return _invoke(
        context,
        "get_monthly_spending",
        {"month": month},
        lambda: context.service.monthly_spending(context.authenticated_user_id, month),
    )


def get_category_breakdown(context: FinancialContext, month: str) -> dict[str, int]:
    return _invoke(
        context,
        "get_category_breakdown",
        {"month": month},
        lambda: context.service.category_breakdown(context.authenticated_user_id, month),
    )


def update_budget(context: FinancialContext, category: str, monthly_limit_paise: int) -> None:
    return _invoke(
        context,
        "update_budget",
        {"category": category, "monthly_limit_paise": monthly_limit_paise},
        lambda: context.service.set_budget(context.authenticated_user_id, category, monthly_limit_paise),
    )


def verify_budget(context: FinancialContext, category: str) -> int | None:
    return _invoke(
        context,
        "verify_budget",
        {"category": category},
        lambda: context.service.get_budget(context.authenticated_user_id, category),
    )


def search_transactions(context: FinancialContext, merchant: str) -> list[dict[str, str | int]]:
    return _invoke(
        context,
        "search_transactions",
        {"merchant": merchant},
        lambda: context.service.search_transactions(context.authenticated_user_id, merchant),
    )


def get_balance(context: FinancialContext) -> dict[str, str | int]:
    return _invoke(
        context,
        "get_balance",
        {},
        lambda: context.service.balance(context.authenticated_user_id),
    )
