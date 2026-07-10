from app.models.conflict_models import CircularConflict
from app.knowledge_base.platform_store import read_store, write_store


class ConflictRepository:
    def list_conflicts(self, status: str | None = None) -> list[CircularConflict]:
        conflicts = read_store().conflicts
        return [conflict for conflict in conflicts if status in {None, conflict.status}]

    def replace_open_conflicts(self, conflicts: list[CircularConflict]) -> list[CircularConflict]:
        store = read_store()
        existing_resolved = [
            conflict for conflict in store.conflicts if conflict.status in {"resolved", "ignored"}
        ]
        store.conflicts = existing_resolved + conflicts
        write_store(store)
        return store.conflicts


conflict_repository = ConflictRepository()
