# Fine-Tuning Plan

Current approach: RAG with optional Ollama.

Why:

- Faster and safer for demos.
- Auditable source references.
- No GPU or paid API required.
- Avoids training on unreviewed records.

Future fine-tuning can use:

```text
data/niyamguard_dataset_pack_v1/ml/instruction_train.jsonl
data/niyamguard_dataset_pack_v1/ml/instruction_validation.jsonl
data/niyamguard_dataset_pack_v1/ml/instruction_test.jsonl
data/niyamguard_dataset_pack_v1/ml/policy_qa_pairs.csv
```

Prepare JSONL:

```powershell
python scripts/prepare_finetune_jsonl.py
```

Recommended schema:

```json
{"instruction":"Answer using only NiyamGuard dataset context","input":"...","output":"...","source":"niyamguard_dataset_pack_v1","verified":false}
```
