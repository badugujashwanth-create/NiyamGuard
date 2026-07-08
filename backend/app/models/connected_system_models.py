from typing import Literal

from pydantic import BaseModel


ConnectedSystemType = Literal[
    "portal",
    "form",
    "sop",
    "faq",
    "notification",
    "district_office",
    "manual",
]
ConnectedSystemStatus = Literal["active", "inactive"]
SnapshotSource = Literal["manual_seed", "api_import", "scraped", "uploaded_doc", "demo"]


class ConnectedSystem(BaseModel):
    id: str
    name: str
    system_type: ConnectedSystemType
    department: str
    district: str | None = None
    service_id: str
    owner: str
    status: ConnectedSystemStatus
    last_checked_at: str | None = None
    created_at: str
    updated_at: str


class ConnectedSystemRuleSnapshot(BaseModel):
    id: str
    connected_system_id: str
    service_id: str
    rule_key: str
    displayed_value: str
    unit: str | None = None
    source_location: str
    last_synced_at: str | None = None
    snapshot_source: SnapshotSource
    created_at: str
    updated_at: str


class ConnectedSystemCreate(BaseModel):
    name: str
    system_type: ConnectedSystemType
    department: str
    district: str | None = None
    service_id: str
    owner: str
    status: ConnectedSystemStatus = "active"


class SnapshotCreate(BaseModel):
    service_id: str
    rule_key: str
    displayed_value: str
    unit: str | None = None
    source_location: str
    snapshot_source: SnapshotSource = "demo"
