# NiyamGuard Synthetic Dataset Pack v1

This pack contains complete synthetic datasets for building and testing **NiyamGuard AI**, a regulatory compliance monitoring, policy drift detection, evidence review, risk scoring, and audit platform.

## Important
These files are **synthetic demo data**, not official regulatory data and not legal advice. Use them for hackathon demos, local development, RAG indexing, model evaluation, seed data, and UI testing.

## Folder structure

- `raw/` — source-like regulatory circulars and internal policy documents.
- `processed/` — extracted obligations, mappings, controls, evidence, findings, drift cases, and risk labels.
- `ml/` — QA pairs, intent labels, instruction-tuning JSONL, RAG documents, and API test cases.
- `app_seed/` — organizations, users, and audit events for backend seeding.
- `scripts/` — starter SQL schema and row-count loader helper.
- `data_dictionary.csv` — file-by-file schema and row counts.

## Suggested import order

1. `raw/regulators.csv`
2. `app_seed/organizations.csv`
3. `app_seed/users.csv`
4. `raw/regulatory_circulars.csv`
5. `raw/internal_policies.csv`
6. `processed/obligations.csv`
7. `processed/policy_obligation_mapping.csv`
8. `processed/controls.csv`
9. `processed/compliance_evidence.csv`
10. `processed/gap_findings.csv`
11. `processed/regulatory_drift_cases.csv`
12. `processed/risk_scoring_labels.csv`
13. `app_seed/audit_events.csv`

## How to use for AI

- RAG/vector search: index `ml/rag_documents.jsonl`.
- Intent classifier: train/evaluate using `ml/intent_classification.csv`.
- LLM instruction tuning / LoRA experiments: use `ml/instruction_train.jsonl`, `ml/instruction_validation.jsonl`, and `ml/instruction_test.jsonl`.
- Product/API QA: use `ml/api_test_cases.csv` and `ml/policy_qa_pairs.csv`.

## Recommended demo flows

1. User uploads or imports a circular.
2. NiyamGuard extracts obligations from `processed/obligations.csv`.
3. System maps obligations to policies using `processed/policy_obligation_mapping.csv`.
4. Gaps are shown from `processed/gap_findings.csv`.
5. Evidence status comes from `processed/compliance_evidence.csv`.
6. Risk score comes from `processed/risk_scoring_labels.csv`.
7. Every action is recorded in `app_seed/audit_events.csv`.

Generated at: 2026-07-09T12:40:27
