# UAT Checklist

1. Seed the dataset and build the RAG index.
2. Confirm `/api/ops/status` is `ok`.
3. Log in as admin and confirm `/api/admin/readiness` reports all controls.
4. Ask "income certificate validity entha" and verify GO-138 source.
5. Ask "scholarship documents enti" and verify service-definition grounding.
6. Run dataset demo flow from `/api/dataset/demo-flow`.
7. Request and verify sandbox OTP with code `123456`.
8. Run backup command and confirm the file appears under `backups/`.
9. Review audit logs for the demo session.
10. Confirm the UI pages show dataset records, gaps, drift, risk, Q&A, and audit logs.
