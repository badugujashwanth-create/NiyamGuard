# Recording guide

## Preparation

1. Install dependencies using docs/DEVELOPMENT.md.
2. Copy example environment files and use only local or synthetic values.
3. Start the demo with scripts/run-demo.ps1 or the component-specific command.
4. Confirm the complete workflow manually before recording.
5. Close notifications, unrelated applications, password managers, and personal browser profiles.

## Record

Run `scripts/record-demo.ps1 -BaseUrl http://127.0.0.1:5180` after the final UI and feature build is healthy. The Playwright specification executes the real product simulation: policy lifecycle, full synthetic service flow, sourced answer, stale-system reset and patch, certificate verification, evidence-derived readiness, policy lineage, knowledge relationships, and audit view. The script then adds narration, preserves WebVTT captions, creates eleven verification frames, and rejects output shorter than three minutes.

## Post-production

Do not splice in fake success states. Inspect all eleven generated frames, verify narration/captions against visible states, and reject any frame containing unrelated or personal content. Commit only the compressed WebM, caption file, thumbnail, and verification evidence.

