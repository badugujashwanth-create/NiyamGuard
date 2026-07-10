# RAG Dataset Pipeline

Dataset pack location:

```text
data/niyamguard_dataset_pack_v1/
```

Important files:

- `raw/regulatory_circulars.csv`
- `raw/internal_policies.csv`
- `processed/obligations.csv`
- `processed/policy_obligation_mapping.csv`
- `processed/compliance_evidence.csv`
- `processed/gap_findings.csv`
- `processed/regulatory_drift_cases.csv`
- `processed/risk_scoring_labels.csv`
- `app_seed/audit_events.csv`
- `ml/rag_documents.jsonl`
- `ml/policy_qa_pairs.csv`
- `ml/intent_classification.csv`
- `ml/instruction_*.jsonl`
- `ml/api_test_cases.csv`

Import and index:

```powershell
cd backend
python -m app.data_pipeline.dataset_pack_loader --import-db --build-rag
```

The importer writes idempotently into `niyamguard_dataset_records`. The RAG
builder creates a TF-IDF index from dataset RAG docs, circulars, policies,
obligations, QA pairs, and citizen-service seed chunks.
