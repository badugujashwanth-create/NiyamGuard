from typing import Any

from pydantic import BaseModel


class CascadeTrace(BaseModel):
    id: str
    finding_id: str
    trace_type: str
    nodes_json: list[dict[str, Any]]
    edges_json: list[dict[str, str]]
    impact_summary: str
    created_at: str
