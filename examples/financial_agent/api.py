from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException

from .db import create_sandbox, seed_maya_spending_spike
from .service import FinancialService

app = FastAPI(title="Synthetic Financial API")
connection = create_sandbox()
seed_maya_spending_spike(connection)
service = FinancialService(connection)


@app.get("/spending/{month}")
def spending(month: str) -> dict[str, int]:
    return {"total_paise": service.monthly_spending("maya", month)}


@app.get("/budgets/{category}")
def budget(category: str) -> dict[str, int]:
    value = service.get_budget("maya", category)
    if value is None:
        raise HTTPException(status_code=404, detail="budget not found")
    return {"monthly_limit_paise": value}


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8000)
