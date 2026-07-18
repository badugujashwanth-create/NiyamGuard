# NiyamGuard interview guide

## Tell me about this project.

NiyamGuard is a synthetic policy-compliance and citizen-service sandbox. It models policy ingestion, human review, publication, downstream drift checks, citizen explanations, and an audit trail without connecting to real government systems.

## Why did you build it?

The engineering problem is consistency: one policy change can affect several portals, forms, SOPs, and guidance surfaces. The project explores how a verified rule lifecycle can make those changes traceable.

## What was your contribution?

Discuss only work you can defend from this repository: the integrated FastAPI/React pilot, policy and citizen workflows, test/CI evidence, demo mode, and documentation. Do not claim ownership of external government systems or any referenced collaborator work.

## What was the hardest technical problem?

Keeping AI-assisted extraction subordinate to human review while propagating approved changes through several modeled systems. The solution was explicit review/publication state, versioning, audit events, and synthetic adapters.

## How does the architecture work?

Two React portal experiences call one FastAPI backend. The backend coordinates policy, workflow, audit, AI, and persistence boundaries through SQLAlchemy. External identity, payment, messaging, government, and Ollama services remain mocked or optional.

## What would you improve?

Add contract-tested adapters, production identity/authorization, realistic load tests, observability, retention controls, and user research before any real pilot.

## How did you test it?

The verified branch passes 239 backend and 60 frontend tests, plus a frontend production build and security checks in CI. A 4:43 browser-driven walkthrough exercises the real synthetic workflow. Explain that this is strong local evidence, not proof of production integrations.

## What are its security limitations?

Demo accounts are synthetic. Real citizen data, official identity, payment, messaging, and government connections are not supported. A deployment would require managed secrets, hardened roles, privacy controls, and formal authorization.

## How would you scale it?

Separate ingestion/propagation into queued jobs, use managed relational storage, cache verified policy retrieval carefully, partition audit workloads, and scale citizen queries independently while preserving provenance.

## What did you learn?

Explainability is a system property. Approval state, evidence, versioning, and failure behavior matter more than presenting a fluent model answer.
