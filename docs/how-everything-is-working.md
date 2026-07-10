# How Everything Is Working

1. Virtual Government Sandbox
What it does:
Simulates a full government service flow from regulation question to application, payment, officer approval, certificate, and audit evidence.
How to open:
Frontend: `http://127.0.0.1:5180/virtual-gov`
Backend: `http://127.0.0.1:8010/api/virtual-gov/status`
How to test:
Click `Run Sandbox Scenario` or call `POST http://127.0.0.1:8010/api/virtual-gov/run`.

2. Circular and Policy Update Flow
What it does:
Shows how GO-138 is ingested, extracted as a rule candidate, approved, published, and propagated to connected systems.
How to open:
Frontend: `http://127.0.0.1:5180/admin/sources`
Backend: `http://127.0.0.1:8010/api/circulars`
How to test:
Open Sources, Rule Candidates, Policy Updates, and Propagation in the admin sidebar.

3. Citizen Service Portal
What it does:
Lists services and lets a citizen create a sandbox application for Income Certificate.
How to open:
Frontend: `http://127.0.0.1:5180/services`
Backend: `http://127.0.0.1:8010/api/portal/services`
How to test:
Open Income Certificate, create a draft, submit evidence, simulate payment, and track the application.

4. Officer Review
What it does:
Lets an officer review submitted applications and approve a sandbox certificate.
How to open:
Frontend: `http://127.0.0.1:5180/officer`
Backend: `http://127.0.0.1:8010/api/officer/applications`
How to test:
Log in as `officer@niyamguard.local / Officer@12345`, open a pending application, and approve it.

5. Certificate Generation and Verification
What it does:
Generates a sandbox certificate after approval and verifies it publicly by certificate number or hash.
How to open:
Frontend: `http://127.0.0.1:5180/verify-certificate`
Backend: `http://127.0.0.1:8010/api/certificates/verify/hash_demo`
How to test:
Enter `hash_demo` or run the virtual government scenario and use the returned verification hash.

6. Compliance Drift
What it does:
Compares verified GO-138 against connected systems and detects stale 12-month values.
How to open:
Frontend: `http://127.0.0.1:5180/admin/compliance`
Backend: `http://127.0.0.1:8010/api/compliance/findings`
How to test:
Click `Run Compliance Demo` on `/demo`, then open the compliance page.

7. Audit Trail
What it does:
Records important system actions and verifies the audit hash chain.
How to open:
Frontend: `http://127.0.0.1:5180/admin/audit`
Backend: `http://127.0.0.1:8010/api/audit/events`
How to test:
Open Audit and confirm events such as login, report export, and sandbox actions are listed.

8. Hybrid Answer Engine
What it does:
Answers citizen questions using exact rules, decision tables, RAG, and deterministic fallback with source cards.
How to open:
Frontend: `http://127.0.0.1:5180/`
Backend: `http://127.0.0.1:8010/api/hybrid/answer`
How to test:
Ask `income certificate validity entha` and verify the GO-138 source card.

9. Readiness Page
What it does:
Shows pilot readiness controls for source-backed answers, RBAC, audit, sandbox, backup, and operational checks.
How to open:
Frontend: `http://127.0.0.1:5180/admin/readiness`
Backend: `http://127.0.0.1:8010/api/admin/readiness`
How to test:
Open the readiness page and click `Run Sandbox Scenario`.
