# Integration Readiness Checklist

Generated: 2026-07-10

| Integration | Backend service | API route | Frontend status | Used in demo flow | Audit event | Current status | Remaining issue |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Virtual Gazette | `circular_sync_service`, `circular_ingestion_service` | `/api/sources`, `/api/circulars`, `/api/demo/run-full-end-to-end` | `/portal`, `/admin/circulars` | Yes | `circular_ingested`, `rule_extracted` | Working mock | Not official feed |
| Verified Rule Engine | `rule_extraction_service`, `policy_publication_service` | `/api/rule-candidates`, `/api/policy-updates`, `/api/demo/run-full-end-to-end` | `/portal`, `/admin/policy-updates` | Yes | `candidate_approved`, `rule_published` | Working | Deterministic demo extraction |
| Citizen Service Portal | `service_portal_service` | `/api/portal/services`, `/api/applications` | `/portal`, `/services`, `/apply/*` | Yes | `service_application_created`, `service_application_submitted` | Working | Synthetic service data |
| Virtual Identity Provider | `service_portal_service`, `readiness_service` | `/api/citizen/profile`, `/api/security/otp/request` | `/portal`, `/admin/readiness` | Yes | `citizen_profile_created` | Mock | No real eKYC |
| Virtual OTP/SMS Provider | `readiness_service` | `/api/security/otp/request`, `/api/security/otp/verify` | `/portal`, `/admin/readiness` | Yes | Included through demo audit trail | Mock | Deterministic code only |
| Virtual Payment Gateway | `service_portal_service` | `/api/payments/{id}/create`, `/api/payments/{id}/simulate-success` | `/portal`, `/payment/*` | Yes | `service_payment_created`, `service_payment_success` | Mock | No real gateway |
| Synthetic certificate service | `service_portal_service` | `/api/certificates/*`, `/api/certificates/verify/*` | `/portal`, `/verify-certificate` | Yes | `service_application_approved` | Mock | No official signing authority |
| Virtual Document Vault | `virtual_government_service`, `service_portal_service` | `/api/applications/{id}/documents` | `/portal`, application pages | Yes | `virtual_government_documents_attached` | Mock | Local metadata/files only |
| Virtual Integration Monitor | `mock_system_service`, `connected_system_service` | `/api/mock-systems`, `/api/connected-systems` | `/portal`, `/mock/*`, `/admin/propagation` | Yes | `mock_meeseva_patched`, `mock_public_faq_patched` | Working mock | No real external systems |
| Compliance Engine | `compliance_service`, `compliance_orchestrator_service` | `/api/compliance/run`, `/api/compliance/findings` | `/portal`, `/admin/compliance` | Yes | `compliance_run_completed`, `compliance_rerun` | Working | Demo snapshots only |
| Audit Trail | `audit_service`, `audit_repository` | `/api/audit/events`, `/api/audit/verify` | `/portal`, `/admin/audit` | Yes | All core events | Working | Production hash-chain review pending |
| Hybrid Answer Engine | `hybrid_answer_service` | `/api/hybrid/answer`, `/api/search/status` | `/portal`, `/`, `/admin/regulatory-ai` | Yes | Demo completion event captures result context | Working | RAG data is synthetic |
| Ollama Provider | `AIProviderFactory`, `OllamaProvider` | `/api/ai/status`, `/api/ai/verified-explanation` | `/portal`, `/admin/regulatory-ai` | Yes | Demo records fallback/provider in entities | Needs local config | Ollama must be running for online status |

