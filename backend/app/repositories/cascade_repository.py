from app.models.cascade_models import CascadeTrace
from app.knowledge_base.platform_store import read_store, write_store


class CascadeRepository:
    def get_by_finding(self, finding_id: str) -> CascadeTrace | None:
        return next((trace for trace in read_store().cascade_traces if trace.finding_id == finding_id), None)

    def upsert_trace(self, trace: CascadeTrace) -> CascadeTrace:
        store = read_store()
        store.cascade_traces = [item for item in store.cascade_traces if item.finding_id != trace.finding_id]
        store.cascade_traces.append(trace)
        write_store(store)
        return trace


cascade_repository = CascadeRepository()
