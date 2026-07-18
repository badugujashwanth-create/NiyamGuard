# NiyamGuard case study

## 1. Project summary

NiyamGuard is an explainable policy-compliance and citizen-service sandbox. It models how a policy circular can be ingested, reviewed, published, checked against dependent systems, and used to answer citizen questions without pretending to connect to real government infrastructure.

## 2. Problem being solved

Policy changes frequently affect portals, forms, SOPs, FAQs, and eligibility guidance at the same time. If those surfaces update independently, citizens and officials can receive inconsistent answers.

## 3. Target users

- Policy officers reviewing extracted rule changes
- Service administrators tracking downstream compliance drift
- Citizens seeking source-backed explanations and guided workflows
- Technical teams evaluating a pilot architecture before real integration

## 4. Why existing approaches are insufficient

Document repositories can store circulars but do not necessarily identify downstream inconsistencies. Generic chatbots can produce fluent answers without enforcing verified sources or approval state. NiyamGuard combines a reviewed knowledge lifecycle with workflow and audit evidence.

## 5. Product approach

The product uses a synthetic government sandbox. Officers ingest seeded or uploaded circulars, review extracted rules, publish verified versions, inspect affected mock systems, and observe an audit trail. Citizen-facing workflows consume only the verified knowledge boundary.

## 6. System architecture

The React frontend exposes separate citizen and government portals. A FastAPI backend owns API, policy, workflow, audit, and AI-service boundaries. SQLAlchemy persists local data; optional services such as Ollama, messaging, identity, payment, and government systems remain sandboxed or mocked.

See [architecture.md](architecture.md) for components and data flow.

## 7. Main engineering decisions

- Require human review before extracted rules become verified.
- Preserve rule versions and audit events instead of overwriting policy state silently.
- Separate citizen and officer workflows while sharing one verified knowledge source.
- Treat local-model explanations as optional and subordinate to verified rules.
- Use synthetic accounts and data so the demo is reproducible without real identities.

## 8. Difficult technical challenges

- Representing a policy change and its impact across heterogeneous dependent systems
- Preventing unreviewed AI output from becoming authoritative state
- Keeping a large workflow demo runnable without external government services
- Testing authorization, workflow transitions, and citizen-facing behavior together

## 9. How those challenges were solved

The backend models review/publication state explicitly, records version/audit evidence, and checks mock connected-system representations for drift. External integrations are adapters or sandbox boundaries. Backend and frontend tests exercise the local workflow without requiring live providers.

## 10. Security and privacy considerations

Demo identities and credentials are synthetic. The project does not submit real applications or process production citizen data. Authorization, payment, government identity, messaging, and local-model boundaries are documented. A real deployment would need managed secrets, hardened role enforcement, data-retention policy, threat review, and authorized integrations.

## 11. Testing strategy

The verified branch passes 235 backend tests and 60 frontend tests. Coverage includes API behavior, production configuration boundaries, demo-route isolation, policy workflows, permissions, service logic, and portal behavior. CI runs both suites, dependency/security checks, and the frontend production build.

## 12. Performance considerations

The current focus is deterministic pilot behavior rather than scale benchmarks. A production design would profile document ingestion, policy retrieval, audit growth, concurrent citizen queries, and background propagation separately. No throughput or latency claim is made.

## 13. Current limitations

- External government, identity, payment, messaging, and Ollama services are not production-verified.
- Demo data and connected systems are synthetic.
- The project is an MVP/pilot prototype, not an official portal or legal authority.
- Production operations, retention, monitoring, and compliance certification remain future work.

## 14. Results demonstrated

The repository demonstrates a working local policy lifecycle, two role-oriented interfaces, compliance-drift modeling, source-aware citizen guidance, an audit trail, 295 passing tests, a production frontend build, and a 4:44 narrated, captioned sandbox walkthrough.

## 15. What the developer learned

The strongest engineering lesson is that explainability requires workflow design, not only model output. Approval state, provenance, audit evidence, and safe fallbacks must be represented directly in the system.

## 16. Next engineering steps

1. Add contract tests for each external adapter.
2. Add production-grade identity and authorization only with an approved provider.
3. Benchmark retrieval and propagation workloads with realistic synthetic volumes.
4. Add deployment observability, retention controls, and incident procedures.
5. Conduct accessibility and threat-model reviews with intended pilot users.
