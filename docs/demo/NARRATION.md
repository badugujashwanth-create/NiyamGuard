# NiyamGuard recruiter walkthrough narration

NiyamGuard is a synthetic policy-compliance and citizen-service sandbox. It is not an official government portal, and every identity, application, payment, connected system, and certificate in this walkthrough is demo data. The product explores one question: when a policy circular changes a rule, how can every dependent experience stay consistent and traceable?

The guided dashboard presents the whole lifecycle. A sandbox circular such as G O one thirty-eight changes Income Certificate validity from twelve months to six months. The system keeps ingestion, extracted rule candidates, human review, publication, compliance checks, and downstream propagation as separate states. Optional AI may explain verified context, but it never becomes the policy authority.

Now the actual end-to-end simulation runs. It creates the circular and reviewed rule state, checks mock connected systems, creates a synthetic citizen application, records a simulated payment, performs an officer review, issues a demo certificate, verifies it publicly, and writes audit evidence. The generated application number, certificate number, and verification hash prove that the visible result comes from the running backend rather than a static mockup.

The hybrid answer engine then answers a test question from the verified G O one thirty-eight source. The local model integration is optional. If Ollama is unavailable, NiyamGuard says that it used deterministic fallback instead of pretending an AI provider succeeded. Source, method, provider, confidence, and verification labels remain visible.

Next, the self-updating policy simulation deliberately resets the mock MeeSeva and public FAQ representations to the stale twelve-month value. Running the approval and demo-patch workflow updates only those local synthetic systems to the verified six-month rule. No real portal is contacted, and the mutation is explicitly labelled as a demo patch.

The citizen portal consumes the same verified knowledge boundary. A citizen asks for Income Certificate validity and receives the six-month answer with a visible source card. Voice support has a text fallback, location is optional, and the assistant does not auto-fill or submit an official application.

The public verification step checks the generated demo certificate using the hash created by the simulation. This is useful for explaining end-to-end state and integrity, but it is not a government digital signature or certificate authority. The audit page then shows how important sandbox actions remain reviewable by actor and event.

The completion build is verified by more than two hundred backend tests, sixty frontend tests, the frontend production build, dependency checks, and secret scans. Those checks support a strong local sandbox claim, not production or government readiness. Real deployment would still require authorized identity, payment, messaging, official APIs, managed secrets, privacy and accessibility reviews, monitoring, legal approval, and department sign-off.

NiyamGuard demonstrates an evidence-led rule-to-service architecture: human approval before publication, deterministic verified sources before model explanation, explicit sandbox mutations, citizen-facing provenance, and an audit trail. The value is in making policy drift visible and testable without pretending that the prototype already operates public infrastructure.
