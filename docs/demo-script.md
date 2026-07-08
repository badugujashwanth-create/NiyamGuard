# NiyamGuard AI Demo Script

## Setup

Run the demo stack:

```powershell
cd D:\niyam\niyamguard-call-assistant
powershell -ExecutionPolicy Bypass -File .\scripts\start-demo.ps1
```

Open:

```text
http://127.0.0.1:5173/demo
```

## Speaker Notes

1. Open `/demo`.

   "This is the final NiyamGuard AI demo dashboard. It shows the complete flow from verified government circulars to citizen-safe voice guidance."

2. Explain the problem.

   "Circular GO-138 changed Income Certificate validity from 12 months to 6 months, but the portal, officer SOP, and public FAQ still show the old 12-month rule. That mismatch can cause delay, wrong approval, or rejection."

3. Open `/admin`.

   "This is the government admin portal. It is not a chatbot screen; it is the policy operations dashboard."

4. Show dashboard counters.

   "We have 2 verified rules, 5 connected systems, 4 compliance findings, 3 drifted systems, and 1 open conflict in the seeded demo."

5. Open `/admin/compliance`.

   "The compliance engine compares the verified GO-138 rule against every connected system."

6. Show 3 drifted systems and 1 compliant system.

   "MeeSeva portal, officer SOP, and public FAQ still show 12 months. The simplified citizen form is already compliant at 6 months."

7. Show conflict detection.

   "The conflict page catches old GO-112 saying 12 months while GO-138 says 6 months. The recommendation is to keep GO-138 active and supersede GO-112."

8. Open the citizen portal.

   "Now we move to the citizen side. Citizens should not see internal JSON or policy operations; they should get a clear, verified answer."

9. Select Income Certificate.

   "The citizen selects the Income Certificate form from the service catalog."

10. Ask the voice assistant: `income certificate validity entha`.

    "The assistant detects this as a validity question and calls the public verified rule API."

11. Show Telugu answer with GO-138 source card.

    "The answer stays in the user's language and shows the verified source: GO-138, Revenue Department, Income Certificate Validity, current value 6 months, confidence 91%."

12. Show no auto-submit safety.

    "The assistant guides only. It does not auto-fill, upload, submit, handle OTP, or call a real government portal."

13. Export report.

    "Finally, officials can export compliance CSV, conflicts CSV, and verified rules JSON from the reports page."

## Closing Line

"NiyamGuard AI prevents policy drift from reaching citizens by connecting verified circulars, compliance checks, admin workflows, and a citizen-safe voice assistant."
