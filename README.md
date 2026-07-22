# NiyamGuard — Policy Drift and Citizen Guidance Sandbox

NiyamGuard explores one specific failure mode in public-service delivery: a policy circular changes, but the portals, forms, FAQs, and operating procedures used by citizens and officers do not change with it.

This repository is a **synthetic pilot sandbox**, not an official government system. It does not submit applications to a department, verify identity, collect real payments, or replace an officer's decision.

[Watch the 5:37 narrated walkthrough](https://jashwanth-portfolio-ten.vercel.app/work/niyamguard/) · [MP4](https://jashwanth-portfolio-ten.vercel.app/media/niyamguard/demo.mp4) · [Captions](https://jashwanth-portfolio-ten.vercel.app/media/niyamguard/demo-captions.vtt) · [Tester guide](TESTER_GUIDE.md)

## The policy-drift problem

A circular is useful only when its effective rule reaches every dependent service surface. NiyamGuard models that lifecycle explicitly:

1. ingest a seeded or synthetic circular;
2. extract candidate rules with source and confidence evidence;
3. require a human reviewer to approve or reject each candidate;
4. publish an immutable verified rule version with an effective date;
5. compare connected mock systems against that version;
6. prioritize conflicts and drift by citizen impact;
7. remediate the mock surfaces and retain an audit trail; and
8. answer citizen questions only from the verified knowledge boundary.

### Worked synthetic example

The bundled GO-138 scenario changes Income Certificate validity from **12 months to 6 months**. A prior circular and several mock surfaces still contain the 12-month value. The sandbox shows the reviewer approving the new candidate, publishing a version, detecting the conflict, tracing affected systems, updating the mock configuration, and returning a citizen answer that cites GO-138.

The example is fictional training data. It demonstrates rule propagation; it is not legal guidance or evidence of a Telangana government integration.

## Two users, one evidence boundary

### Officer and reviewer workflow

- inspect the circular and extracted rule candidate;
- compare source text, confidence, effective date, and prior versions;
- approve before publication;
- run compliance checks across mock portals, SOPs, forms, and FAQs;
- inspect conflicts, priority, lineage, propagation, and audit evidence.

### Citizen workflow

- find a synthetic service;
- ask a question against verified rules;
- see the circular and method used for the answer;
- exercise a mock application, payment, officer-review, and certificate flow;
- verify a synthetic certificate without implying an official transaction.

## Why the assistant cannot publish policy

Deterministic rule evaluation is authoritative. Optional Ollama output can explain verified context, but it cannot approve a candidate, change an effective date, or publish a rule. When Ollama is unavailable, a labeled deterministic fallback remains active. Human review is required before a candidate enters the verified knowledge set.

## Run the sandbox locally

Python 3.12 and Node.js are required. No government or paid-provider credentials are needed.

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m app.seed_demo
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8010
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5180
```

Open `http://127.0.0.1:5180`. Demo identities are listed in [TESTER_GUIDE.md](TESTER_GUIDE.md).

## Verification

```powershell
backend\.venv\Scripts\python -m pytest backend/app/tests -q
npm test --prefix frontend -- --run
npm run build --prefix frontend
```

Current release evidence records **243 backend tests**, **60 frontend tests**, a Vite production build, and a same-origin container check. The useful detail is in [engineering decisions](docs/ENGINEERING_DECISIONS.md), not the test count alone.

## Current limits

- Circulars, people, connected systems, applications, payments, and certificates are synthetic.
- No real government identity, Gazette, MeeSeva, DigiLocker, eSign, payment, or messaging integration is verified.
- The current score is descriptive for one synthetic snapshot; it is not a forecast or policy-performance metric.
- Cross-jurisdiction comparison, expiry detection, a formal hallucination benchmark, and manual assistive-technology testing remain open work.
- A deployment blueprint exists, but no owner-verified public backend is currently claimed.

## Evidence and orientation

- [Architecture](docs/architecture.md)
- [Engineering decisions](docs/ENGINEERING_DECISIONS.md)
- [Policy-readiness gaps](docs/PILOT_READINESS_GAP_MATRIX.md)
- [Test report](docs/TEST_REPORT.md)
- [Deployment boundary](docs/deployment.md)
- [Case study](docs/CASE_STUDY.md)
- [Contributing](CONTRIBUTING.md)

## License status

No license file is present. All rights remain with the copyright holders until ownership and contributor approval are reviewed.
