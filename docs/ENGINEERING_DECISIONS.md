# Engineering decisions behind NiyamGuard

These are incidents visible in code and history, not reconstructed success stories.

## Sandbox routes remained reachable outside demo mode

**Problem.** Mock systems, the full-demo runner, the virtual-government flow, and sandbox routes were registered like ordinary application routes.

**User impact.** An operator could set production-like configuration while still exposing synthetic reset and mutation endpoints. The interface boundary said “sandbox,” but the server did not enforce that boundary centrally.

**Reproduction.** On the earlier tree, start the API with `DEMO_MODE=false` and request `/api/mock-systems`, `/api/demo/run-full-end-to-end`, `/api/virtual-gov/scenarios`, or `/api/sandbox/status`. Route registration did not depend on demo mode.

**Investigation.** `backend/app/main.py` included all five routers unconditionally. Environment validation also allowed a production environment to start with a placeholder secret, debug mode, or demo mode.

**Root cause.** Demo labeling existed in product copy and configuration, but it was not a server-side precondition shared by the sandbox routers.

**Fix.** `require_demo_mode` now returns 404 when demo mode is disabled, and the dependency is attached when the routers are registered. `validate_runtime_settings` also rejects placeholder production secrets, debug mode, and demo mode during startup.

**Regression test.** `backend/app/tests/test_runtime_boundaries.py` parametrically checks the four representative sandbox paths with demo mode disabled and checks every rejected production configuration.

**Trade-off.** Returning 404 deliberately hides sandbox route availability, which is less diagnostic than 403 but avoids advertising non-production surfaces. Local demos must explicitly enable `DEMO_MODE`.

**Relevant files.** `backend/app/main.py`, `backend/app/dependencies.py`, `backend/app/config.py`, `backend/app/tests/test_runtime_boundaries.py`.

**Reference.** Commit [`d5a3a35`](https://github.com/badugujashwanth-create/NiyamGuard/commit/d5a3a35fd3105573eab09717ee32b72ce8349c2e), merged in [PR #6](https://github.com/badugujashwanth-create/NiyamGuard/pull/6).

## Readiness looked authoritative without being derived from findings

**Problem.** The government dashboard presented fixed drift/compliance copy and had no department-level aggregation tied to the current connected-system evidence.

**User impact.** A reviewer could change the synthetic findings while the dashboard continued to display the old summary. That made a demonstrative number look like a computed control.

**Reproduction.** In the earlier frontend, inspect `DashboardPage`: the pills were literal `3 drifted` and `1 compliant`. There was no service that excluded inactive systems or represented an unassessed department.

**Investigation.** Findings and priority records already existed, but the UI summarized seed assumptions rather than querying an aggregation over active connected systems.

**Root cause.** The first dashboard was built around the known GO-138 fixture, so presentation logic captured fixture values instead of domain rules.

**Fix.** `compliance_metrics` and `department_readiness` now calculate compliance, coverage, drift, and critical counts from the current store. Unknown denominators return `None`, rendered as “Not assessed.” The frontend consumes those APIs and builds relationship and lineage views from current records.

**Regression test.** `test_dashboard_metrics_exclude_inactive_connected_systems` changes a system's active state and asserts bounded coverage; `test_department_readiness_aggregates_real_findings` verifies the returned department evidence. `frontend/src/test/App.test.jsx` checks the resulting score, readiness row, relationship search, and lineage.

**Trade-off.** The score is deliberately descriptive rather than predictive. It cannot represent real departmental readiness without governed production data and a validated metric definition.

**Relevant files.** `backend/app/compliance/analytics_service.py`, `backend/app/tests/test_priority_dashboard.py`, `frontend/src/government-portal/components/AdminPortal.jsx`, `frontend/src/test/App.test.jsx`.

**Reference.** Commit [`9098f61`](https://github.com/badugujashwanth-create/NiyamGuard/commit/9098f61d66e4f016de20b797128ba8b25c318631), merged in [PR #8](https://github.com/badugujashwanth-create/NiyamGuard/pull/8).
