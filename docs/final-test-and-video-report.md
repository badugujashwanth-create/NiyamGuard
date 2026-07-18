# Final test and video report

Date: 2026-07-18

Branch: `product-completion-2026`

## Verified status

NiyamGuard is a portfolio-ready synthetic sandbox. It is not an official government portal and no percentage-based production-readiness claim is made.

| Check | Result | Evidence |
|---|---|---|
| Backend suite | Pass | 239 tests; 2 known framework deprecation warnings |
| Frontend suite | Pass | 60 tests across 3 files |
| Frontend build | Pass | Vite production bundle generated |
| Recruiter simulation | Pass | Playwright completed the real browser flow in 4.9 minutes |
| Final video | Pass | 283.648 seconds, 1280×720, VP9, Opus narration |
| Full-stack container | Pass | Same-origin SPA/API runtime, health endpoint, deep route, and API 404 verified |
| Captions | Pass | `docs/demo/demo-captions.vtt` |
| Production npm audit | Pass | 0 known production dependency vulnerabilities |
| Backend dependency audit | Pass | No known vulnerabilities in the installed environment |
| Secret scans | Pass | Gitleaks current tree and audited Git history clean |

## Demonstrated flow

The accepted walkthrough shows the synthetic boundary, policy circular publication and extraction, human approval, verified-rule publication, downstream drift, mock-system remediation, citizen service application, mock payment and officer review, demo certificate generation, public verification, source-backed citizen guidance, optional local-AI fallback, and authenticated audit history.

## Video evidence

- Asset: `docs/demo/demo.webm`
- Captions: `docs/demo/demo-captions.vtt`
- Duration: 283.648 seconds
- SHA-256: `5802108062397c3e95d234d58832672589d1b027d908a82c680318e6e2e0c633`
- Machine-readable evidence: `docs/demo/verification/verification.json`
- Visual samples: `docs/demo/verification/01-frame.png` through `07-frame.png`

## Honest limits

Government, identity, payment, messaging, document-signing, and Ollama integrations are mocked, synthetic, optional, or unavailable. A real pilot would require an authorized integration program, managed identity and secrets, privacy and retention controls, threat modeling, accessibility research, observability, deployment approval, and legal/compliance review.
