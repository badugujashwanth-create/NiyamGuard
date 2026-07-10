from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VirtualScenarioRequest(BaseModel):
    scenario_id: str = "income_certificate_full_flow"
    reset_before_run: bool = True


class VirtualScenarioStep(BaseModel):
    step_id: str
    title: str
    status: str = "completed"
    payload: dict[str, Any] = Field(default_factory=dict)


class VirtualScenarioResult(BaseModel):
    success: bool
    scenario_id: str
    title: str
    steps: list[VirtualScenarioStep]
    artifacts: dict[str, Any] = Field(default_factory=dict)
