"""Optional live OpenAI Agents SDK path.

The same FinancialContext and service contract are used in a real run and in evals.
"""
from __future__ import annotations

from typing import Annotated

from .model_provider import live_model_from_environment
from .models import FinancialContext
from .tools import (
    get_balance,
    get_category_breakdown,
    get_monthly_spending,
    search_transactions,
    update_budget,
    verify_budget,
)

SYSTEM_PROMPT = """You are a careful financial assistant for the authenticated user.
Use tools for financial facts and calculations; never invent a number after a tool error.
For a budget update, verify the write before claiming success. State data limitations clearly.
"""


def build_agent():
    try:
        from agents import Agent, RunContextWrapper, function_tool
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("Install project dependencies with uv sync to use the live agent.") from error

    @function_tool
    def monthly_spending(
        ctx: RunContextWrapper[FinancialContext], month: Annotated[str, "YYYY-MM"]
    ) -> int:
        return get_monthly_spending(ctx.context, month)

    @function_tool
    def category_breakdown(
        ctx: RunContextWrapper[FinancialContext], month: Annotated[str, "YYYY-MM"]
    ) -> dict[str, int]:
        return get_category_breakdown(ctx.context, month)

    @function_tool
    def set_budget(
        ctx: RunContextWrapper[FinancialContext],
        category: Annotated[str, "budget category"],
        monthly_limit_paise: Annotated[int, "monthly amount in paise"],
    ) -> str:
        update_budget(ctx.context, category, monthly_limit_paise)
        return "Budget write submitted. Verify it before telling the user it succeeded."

    @function_tool
    def get_budget(
        ctx: RunContextWrapper[FinancialContext], category: Annotated[str, "budget category"]
    ) -> int | None:
        return verify_budget(ctx.context, category)

    @function_tool
    def find_transactions(
        ctx: RunContextWrapper[FinancialContext], merchant: Annotated[str, "merchant text to search"]
    ) -> list[dict[str, str | int]]:
        return search_transactions(ctx.context, merchant)

    @function_tool
    def account_balance(ctx: RunContextWrapper[FinancialContext]) -> dict[str, str | int]:
        return get_balance(ctx.context)

    return Agent(
        name="Financial Assistant",
        instructions=SYSTEM_PROMPT,
        model=live_model_from_environment(),
        tools=[
            monthly_spending,
            category_breakdown,
            set_budget,
            get_budget,
            find_transactions,
            account_balance,
        ],
    )
