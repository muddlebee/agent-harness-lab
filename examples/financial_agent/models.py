from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolEvent:
    name: str
    arguments: dict[str, Any]
    outcome: str
    result: Any | None = None
    error: str | None = None


@dataclass
class RunTrace:
    task_id: str
    events: list[ToolEvent] = field(default_factory=list)

    def record_success(self, name: str, arguments: dict[str, Any], result: Any) -> None:
        self.events.append(ToolEvent(name=name, arguments=arguments, outcome="ok", result=result))

    def record_error(self, name: str, arguments: dict[str, Any], error: Exception) -> None:
        self.events.append(
            ToolEvent(name=name, arguments=arguments, outcome="error", error=str(error))
        )

    def as_dict(self) -> dict[str, Any]:
        return {"task_id": self.task_id, "events": [asdict(event) for event in self.events]}


@dataclass
class FinancialContext:
    """Runtime-only dependencies. It is never exposed as a model-controlled user id."""

    service: Any
    trace: RunTrace
    authenticated_user_id: str = "maya"
