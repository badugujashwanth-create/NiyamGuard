# Ollama RAG AI Plan

NiyamGuard uses deterministic compliance logic for official decisions and local
AI only for explanations and dataset-grounded Q&A.

Allowed AI use:

- Explain verified compliance findings.
- Answer regulatory questions from retrieved dataset chunks.
- Summarize circulars, obligations, gaps, drift, risk, evidence, and audit data.

Disallowed AI use:

- Inventing regulatory requirements.
- Deciding official compliance status from model memory.
- Replacing `VerifiedPolicyRule`, `ComplianceFinding`, or imported dataset records.

Flow:

```text
Verified or imported dataset records
  -> TF-IDF RAG index
  -> Retriever returns cited chunks
  -> Ollama explains only from context
  -> Deterministic fallback if Ollama is unavailable
```

Missing data response:

```text
Not found in available dataset.
```
