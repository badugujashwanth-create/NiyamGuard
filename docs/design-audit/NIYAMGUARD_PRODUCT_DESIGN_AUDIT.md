# NiyamGuard Product Design Audit

Audit date: 2026-08-07
Surface: local React/Vite landing (`/`) and government reviewer workflow (`/government`)
Capture: Playwright, Chromium headless, logged-out synthetic sandbox

## Captured flow

1. Landing before the change — `frontend/docs/design-audit/01-landing.png`
2. Government reviewer entry before the run — `frontend/docs/design-audit/02-government.png`
3. Government reviewer after the connected policy lifecycle — `frontend/docs/design-audit/04-government-after-run.png`
4. Government reviewer at 390 × 844 — `frontend/docs/design-audit/05-government-mobile.png`
5. Revised landing at 1440 × 1000 — `frontend/docs/design-audit/06-landing-revised.png`
6. Revised landing at 390 × 844 — `frontend/docs/design-audit/07-landing-mobile.png`

## Findings and fixes

- **P1 — The original landing hid the differentiator.** The two equal portal cards made NiyamGuard look like a generic services portal and did not show policy drift, evidence, or impact. The revised landing leads with the synthetic GO-138 change (12 months → 6 months), an impact summary, and two clearly labelled workflow paths.
- **P2 — The reviewer surface was information-dense but coherent.** The current reviewer screen exposes lifecycle status, source evidence, version lineage, downstream impact, and deterministic eligibility outcomes. It was retained rather than replaced; the landing now provides the missing narrative entry point.
- **P2 — Mobile readability required a responsive check.** At 390 × 844, Playwright reported equal `scrollWidth` and `clientWidth` (390px); the revised incident card stacks cleanly and both actions remain visible without horizontal overflow.

## Accessibility checks visible from the capture

- Heading hierarchy and labelled workflow sections are present.
- The impact list is not colour-only; it uses counts and text.
- The synthetic boundary is visible before actions.
- Buttons/links remain reachable in the narrow viewport.

Not established by screenshots alone: keyboard focus order, screen-reader announcements, contrast ratios, reduced-motion behavior, and assistive-technology support. Those remain automated/manual QA gates.

## Result

The landing now communicates the policy-drift thesis before asking the visitor to choose a portal, while preserving the existing working reviewer and citizen workflows.

## Verification rerun (2026-08-07)

- Fresh Chromium captures were accepted for the landing at desktop and 390 × 844 mobile widths, plus the reviewer entry and post-lifecycle states. The accepted files are kept in the ignored `frontend/docs/design-audit/current/` evidence folder.
- With both local origins explicitly allowed, the reviewer workspace reported `Backend online`, 10 services, and completed all 11 lifecycle steps. The citizen explanation correctly displayed deterministic fallback rather than implying a live model.
- The 390 × 844 reviewer capture reported zero horizontal overflow.
- A controlled backend-failure test now surfaces an actionable alert and marks dependent status cards `Unavailable`; it no longer presents zero counts as a working system.
