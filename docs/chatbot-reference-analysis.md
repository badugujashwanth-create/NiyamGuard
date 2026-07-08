# Chatbot Reference Analysis

Repository: `https://github.com/adepushivasai901-ops/niyam-guard`

## Useful Chatbot Patterns

- Single `/api/chat` entrypoint.
- Deterministic intent routing before response formatting.
- Separate handlers for documents, eligibility, process, version comparison, scheme comparison, and circular lookup.
- Seeded scheme data for stable demos.
- No-hallucination posture: handlers retrieve stored data and return safe fallbacks when data is missing.
- Structured source/citation metadata is suitable for voice assistant integration.

## Useful Ideas Reimplemented Here

- `/api/chat` with deterministic intent detection.
- Intents for documents, eligibility, process, validity, fee, timeline, old-vs-new, which-service, form-help, and unknown.
- Seeded local knowledge for certificates, pensions, scholarship, and food security card.
- Verified GO-138 answer for income certificate validity via the existing public verified-rule API.
- Safe fallback when verified/local knowledge is unavailable.
- Source metadata on every answer.

## What Should Not Be Copied

- The reference frontend should not replace Jashwanth's citizen portal or voice assistant.
- Its database schema should not replace the existing service catalog and verified-rule models.
- Any freeform answer behavior that could hallucinate official government data.
