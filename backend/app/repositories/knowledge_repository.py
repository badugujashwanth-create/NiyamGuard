from app.models.knowledge_models import VerifiedPolicyRule
from app.knowledge_base.platform_store import now_iso, read_store, write_store


class KnowledgeRepository:
    def list_rules(self, service_id: str | None = None) -> list[VerifiedPolicyRule]:
        rules = read_store().verified_rules
        return [rule for rule in rules if service_id in {None, rule.service_id}]

    def get_rule(self, rule_id: str) -> VerifiedPolicyRule | None:
        return next((rule for rule in read_store().verified_rules if rule.id == rule_id), None)

    def get_latest_rule(self, service_id: str, rule_key: str) -> VerifiedPolicyRule | None:
        candidates = [
            rule
            for rule in read_store().verified_rules
            if rule.service_id == service_id and rule.rule_key == rule_key and rule.status == "active"
        ]
        return sorted(candidates, key=lambda item: item.effective_date, reverse=True)[0] if candidates else None

    def supersede_old_rule(self, new_rule: VerifiedPolicyRule) -> VerifiedPolicyRule:
        store = read_store()
        for rule in store.verified_rules:
            if (
                rule.id != new_rule.id
                and rule.service_id == new_rule.service_id
                and rule.rule_key == new_rule.rule_key
                and rule.status == "active"
                and rule.effective_date < new_rule.effective_date
            ):
                rule.status = "superseded"
                rule.updated_at = now_iso()
                new_rule.supersedes_rule_id = rule.id
        new_rule.updated_at = now_iso()
        write_store(store)
        return new_rule


knowledge_repository = KnowledgeRepository()
