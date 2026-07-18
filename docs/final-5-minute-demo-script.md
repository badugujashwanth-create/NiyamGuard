# Final 5 Minute Demo Script

## 1. Opening problem

NiyamGuard started as a circular compliance checker, but now it is a full virtual government operating platform. It helps departments test how policy changes flow from circulars into citizen services, officer workflows, certificates, public verification, compliance checks, and audit records.

Government rules change through circulars, but citizen portals, officer SOPs, FAQs, forms, and help desks can stay outdated. That creates wrong guidance, rejected applications, and weak audit visibility.

## 2. What NiyamGuard is

NiyamGuard is a virtual MeeSeva-style government sandbox. It shows how a department can publish a circular, convert it into a verified rule, push that rule into services, and verify whether connected systems are aligned.

This is a virtual government sandbox and MeeSeva-style prototype, not an official government portal. It is designed for pilot testing before real government API integration.

## 3. Virtual government sandbox

Open `http://127.0.0.1:5180/demo`.

Start with the "How everything works" section. Explain that the cards show the full pilot flow: virtual gazette, policy engine, service portal, citizen application, officer review, synthetic certificate service, public verification, compliance engine, audit trail, and hybrid answer engine.

## 4. Circular update flow

Open `http://127.0.0.1:5180/virtual-gov`.

Explain GO-138: Income Certificate validity changed from 12 months to 6 months. NiyamGuard treats the verified rule as the source of truth and then checks if connected systems still show old values.

## 5. Citizen service application flow

Open `http://127.0.0.1:5180/services`.

Show the Income Certificate service. Explain that the citizen can apply in a sandbox flow, upload document evidence, complete simulated payment, and track the application.

## 6. Officer review and certificate flow

Log in as officer:

```text
officer@niyamguard.local / Officer@12345
```

Open `http://127.0.0.1:5180/officer`.

Show that the officer can review a pending application and approve it in the sandbox. After approval, the system issues a demo certificate.

## 7. Public certificate verification

Open `http://127.0.0.1:5180/verify-certificate`.

Use:

```text
hash_demo
```

Show that the public verification page confirms the certificate is valid.

## 8. Compliance drift and audit trail

Open `http://127.0.0.1:5180/admin/compliance`.

Explain that MeeSeva, SOP, and FAQ can still show 12 months while GO-138 says 6 months. NiyamGuard detects this drift and prioritizes fixes.

Open `http://127.0.0.1:5180/admin/audit`.

Show that important actions are recorded for accountability.

## 9. Hybrid answer engine

Open the citizen portal at `http://127.0.0.1:5180/`.

Ask:

```text
income certificate validity entha
```

Point to the source card. Official answers and compliance decisions are deterministic and source-backed. The local AI layer is optional and used only for explanation. The system works even without paid API keys.

## 10. Final impact

Close with this:

NiyamGuard helps government teams test a complete rule-to-service operating flow before connecting real government systems. It reduces stale guidance risk, makes citizen services easier to verify, and gives officers a clear audit trail for policy changes.
