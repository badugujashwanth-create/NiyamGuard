# Self-Updating Policy Engine

This module is a demo-ready policy update loop for NiyamGuard. It does not connect to live government portals. It uses configured circular sources, deterministic rule extraction, officer approval, verified rule publication, propagation tasks, mock connected systems, compliance reruns, and audit logging.

## Flow

1. Source sync reads configured circular sources.
2. Circular ingestion stores deduplicated circular documents by content hash.
3. Rule extraction creates policy rule candidates and deltas.
4. Officer approval marks a candidate ready for publication.
5. Publication creates an immutable rule version and updates the verified rule.
6. Knowledge update events record public API/RAG refresh.
7. Propagation tasks are generated for portals, forms, SOPs, and FAQs.
8. Demo patch endpoints update local snapshots and mock system pages.
9. Compliance reruns compare connected systems against the verified rule.

## Key APIs

```text
GET  /api/sources
POST /api/sources/{source_id}/sync
GET  /api/circulars
POST /api/circulars/sync-all
POST /api/circulars/{circular_id}/extract-rules
GET  /api/rule-candidates
POST /api/rule-candidates/{candidate_id}/approve
POST /api/policy-updates/{candidate_id}/publish
GET  /api/policy-updates/history
GET  /api/policy-updates/versions
POST /api/policy-updates/rules/{rule_id}/rollback
GET  /api/knowledge/update-events
POST /api/knowledge/reindex
GET  /api/propagation/tasks
POST /api/propagation/tasks/{task_id}/apply-demo-patch
POST /api/compliance/rerun-for-rule/{rule_id}
GET  /api/mock-systems
POST /api/demo/run-self-update-scenario
```

## Admin UI

Open `/admin` and use:

```text
Sources
Circulars
Rule Candidates
Policy Updates
Propagation
Scheduler
Scale View
Impact
```

## Safety

The module never claims live MeeSeva or official portal integration. Mock patches only update demo snapshots and `/mock/meeseva` plus `/mock/public-faq`.
