from app.models.priority_models import PriorityScore
from app.knowledge_base.platform_store import read_store, write_store


class PriorityRepository:
    def list_scores(self) -> list[PriorityScore]:
        return read_store().priority_scores

    def replace_scores(self, scores: list[PriorityScore]) -> list[PriorityScore]:
        store = read_store()
        store.priority_scores = scores
        write_store(store)
        return scores


priority_repository = PriorityRepository()
