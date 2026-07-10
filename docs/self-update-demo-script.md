# Self-Update Demo Script

1. Open `/demo`.
2. Click `Reset Mock Systems`.
3. Open `/mock/meeseva` and `/mock/public-faq`; both show `12 months`.
4. Return to `/demo`.
5. Click `Run Update Workflow`.
6. Open `/admin/rule-candidates`; show the extracted GO-138 candidate.
7. Open `/admin/policy-updates`; show rule versions and knowledge update events.
8. Open `/admin/propagation`; show pending downstream update tasks.
9. Click `Run and Patch` on `/demo` or `Patch Mocks` on `/admin/propagation`.
10. Reopen `/mock/meeseva` and `/mock/public-faq`; both show `6 months`.
11. Open `/admin/compliance` or `/admin/impact`; show drift/priority context and compliance reruns.

Visible limitation to state during demo:

```text
These are synthetic mock connected systems. NiyamGuard is not logging into MeeSeva and is not submitting real applications.
```
