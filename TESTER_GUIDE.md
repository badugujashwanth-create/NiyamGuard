# Test NiyamGuard with synthetic data

NiyamGuard needs feedback on whether its policy evidence is understandable—not confirmation that it looks polished. Three to five testers can use this guide without government credentials or personal data.

## Access

There is no owner-verified public backend at present. Run the local sandbox using the [README setup](README.md#run-the-sandbox-locally), then open `http://127.0.0.1:5180`.

Use only these synthetic identities:

| Role | Email | Password |
| --- | --- | --- |
| Reviewer | `reviewer@niyamguard.local` | `Reviewer@12345` |
| Officer | `officer@niyamguard.local` | `Officer@12345` |
| Citizen | `citizen@niyamguard.local` | `Citizen@12345` |

Everything in the sandbox—including circulars, users, documents, payments, and certificates—is fictional.

## Five tasks

1. As a reviewer, find the GO-138 candidate, identify the old and new validity values, and decide what evidence you would need before approval.
2. Publish the approved synthetic rule, run compliance, and explain which mock surface is still out of date.
3. Use policy lineage to locate the prior version and effective date, then check whether the relationship view connects the rule to the affected system.
4. As a citizen, ask how long an Income Certificate is valid and identify the source and answer method shown by the interface.
5. Complete the synthetic application path through mock certificate verification, noting any point that could be mistaken for a real government transaction.

## Feedback that is useful

- the exact task and step where you became uncertain;
- what you expected to happen and what happened instead;
- whether source, effective date, review state, and synthetic boundaries were clear;
- keyboard, zoom, screen-reader, contrast, or mobile problems;
- screenshots with only synthetic data;
- browser, operating system, viewport/zoom, and reproducible steps.

“It did not work” is hard to act on; a short reproduction is much more useful. Do not invent impact or severity.

## Report a bug or limitation

Search [existing NiyamGuard issues](https://github.com/badugujashwanth-create/NiyamGuard/issues) first. If it is new, open an issue with:

- the task number above;
- steps to reproduce;
- expected and actual behavior;
- browser/OS;
- console or server error text with secrets removed.

Do not upload real identity documents, official circulars that are not already public, credentials, tokens, private URLs, or personal information. Use the seeded fixtures only.

## Known limits

- This is not an official portal and produces no valid application, payment, or certificate.
- Ollama is optional; labeled deterministic fallback is expected when it is absent.
- Manual screen-reader and scaling coverage is incomplete.
- Cross-jurisdiction rules, policy expiry, and production operations are not implemented.
- Testers should not evaluate medical, legal, or benefit eligibility from this sandbox.
