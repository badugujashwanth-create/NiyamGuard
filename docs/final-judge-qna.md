# Final Judge Q&A

## 1. What problem does NiyamGuard solve?

It solves policy drift. When a circular changes a rule, portals, SOPs, FAQs, and forms can stay outdated. NiyamGuard checks those systems against verified source-backed rules.

## 2. How is this different from a normal government portal?

A normal portal mainly accepts applications. NiyamGuard shows the whole operating flow: circular update, verified rule, citizen service, officer review, certificate issue, public verification, compliance drift, and audit trail.

## 3. Is this an official government system?

No. It is a virtual government sandbox and MeeSeva-style prototype for pilot testing. Real production use needs government approval and real API integration.

## 4. How does the system update rules from circulars?

It ingests sandbox circular data, extracts a rule candidate, lets an officer/admin approve it, publishes a verified rule version, and then checks connected systems for drift.

## 5. How do you avoid wrong AI answers?

Official answers and compliance decisions are deterministic and source-backed. AI is used only for explanation. The UI shows source cards, method badges, and fallback status.

## 6. Why not use only LLM?

Because government answers need traceability. A pure LLM can hallucinate. NiyamGuard uses exact rules, decision tables, verified search, and RAG first; the LLM layer is optional explanation only.

## 7. Does it require paid API keys?

No. The system works with deterministic fallback and optional local Ollama support. Paid APIs are not required for core verified answers.

## 8. How does certificate verification work?

The sandbox creates a certificate with a certificate number and verification hash. The public verification page checks that value against the stored certificate record.

## 9. How does officer approval work?

The officer portal shows pending applications, evidence, fee status, and citizen details. The officer can approve in sandbox mode, which issues a demo certificate.

## 10. How does audit trail work?

Important actions are recorded as audit events with actor, action, entity, request ID, and timestamp. The audit page also shows hash-chain verification.

## 11. What is the virtual government sandbox?

It is a safe demo environment that simulates a government department, circular publication, services, payments, officer approval, certificates, verification, and audit records.

## 12. What happens when real government APIs are available?

The sandbox adapters can be replaced with official API integrations. The same verified-rule, compliance, audit, and citizen-guidance logic can remain.

## 13. What is completed now?

The prototype includes service portal, citizen application flow, officer review, certificate verification, compliance drift, audit trail, readiness APIs, hybrid answer engine, and demo recording assets.

## 14. What is still pending for real production?

Real production needs official government approval, real identity/payment/document APIs, security review, hosting approval, monitoring, and legal compliance validation.

## 15. Why is this useful for government departments?

It lets departments test policy changes before they affect citizens. They can find stale portal content, prove source-backed answers, and review a clear audit trail.
