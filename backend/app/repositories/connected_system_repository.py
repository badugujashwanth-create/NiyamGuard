from app.models.connected_system_models import ConnectedSystem, ConnectedSystemRuleSnapshot
from app.knowledge_base.platform_store import read_store


class ConnectedSystemRepository:
    def list_systems(self, service_id: str | None = None) -> list[ConnectedSystem]:
        systems = read_store().connected_systems
        return [system for system in systems if service_id in {None, system.service_id}]

    def get_system(self, system_id: str) -> ConnectedSystem | None:
        return next((system for system in read_store().connected_systems if system.id == system_id), None)

    def list_snapshots(self, connected_system_id: str | None = None) -> list[ConnectedSystemRuleSnapshot]:
        snapshots = read_store().snapshots
        return [
            snapshot
            for snapshot in snapshots
            if connected_system_id in {None, snapshot.connected_system_id}
        ]


connected_system_repository = ConnectedSystemRepository()
