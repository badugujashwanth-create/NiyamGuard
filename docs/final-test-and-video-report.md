# Final test and video report

Date: 2026-07-19

Branch: `pilot-readiness-2026`

## Verified status

NiyamGuard is a portfolio-ready synthetic sandbox. It is not an official government portal and no percentage-based production-readiness claim is made.

| Check | Result | Evidence |
|---|---|---|
| Backend suite | Pass | 243 tests; 2 known framework deprecation warnings |
| Frontend suite | Pass | 60 tests across 3 files |
| Frontend build | Pass | Vite production bundle generated |
| Product simulation | Pass | Playwright completed the real browser flow and recording |
| Final video | Pass | 337.408 seconds, 1280×720, VP9, Opus narration |
| Full-stack container | Pass | Same-origin SPA/API runtime, health endpoint, deep route, and API 404 verified |
| Captions | Pass | `docs/demo/demo-captions.vtt` |
| Production npm audit | Pass | 0 known production dependency vulnerabilities |
| Backend dependency audit | Pass | No known vulnerabilities in the installed environment |
| Secret scans | Pass | Gitleaks current tree and audited Git history clean |

## Demonstrated flow

The accepted walkthrough shows the synthetic boundary, policy circular publication and extraction, human approval, verified-rule publication, downstream drift, mock-system remediation, citizen service application, mock payment and officer review, demo certificate generation, public verification, source-backed citizen guidance, optional local-AI fallback, evidence-derived compliance and department readiness, immutable policy lineage, searchable knowledge relationships, and authenticated audit history.

## Video evidence

- Asset: `docs/demo/demo.webm`
- Captions: `docs/demo/demo-captions.vtt`
- Duration: 337.408 seconds (5:37)
- Size: 13,708,739 bytes
- SHA-256: `859c36d0571f9b18ec32edf2520d500617ef5f595bdeeec7c460edd052f3aff2`
- Machine-readable evidence: `docs/demo/verification/verification.json`
- Visual samples: `docs/demo/verification/01-frame.png` through `11-frame.png`

## Honest limits

Government, identity, payment, messaging, document-signing, and Ollama integrations are mocked, synthetic, optional, or unavailable. A real pilot would require an authorized integration program, managed identity and secrets, privacy and retention controls, threat modeling, accessibility research, observability, deployment approval, and legal/compliance review.
