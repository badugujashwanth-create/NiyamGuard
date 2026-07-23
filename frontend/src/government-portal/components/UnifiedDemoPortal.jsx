import { useEffect, useMemo, useState } from "react";

import {
  getAIStatus,
  getDashboardSummary,
  getIntegrationHealth,
  getMockSystems,
  getPortalServices,
  getVerifiedAIExplanation,
  getVirtualGovStatus,
  askHybridDemoQuestion,
  runCompliance,
  runPolicyLifecycleDemo,
} from "../../services/api";

const portalCards = [
  {
    key: "circular_policy",
    title: "Circulars & Policy Updates",
    description:
      "Publish GO-138, ingest the circular, extract rule candidates, approve the rule, and review policy history.",
    href: "/admin/policy-updates",
    status: "Working",
    action: "Publish / Update Circular",
    primaryLabel: "Open Policy Updates",
    links: [
      { href: "/admin/circulars", label: "Open Circulars" },
      { href: "/virtual-gov/gazette", label: "Virtual Gazette" },
    ],
  },
  {
    key: "self_updating_policy",
    title: "Self-Updating Policy Engine",
    description:
      "Income Certificate validity changed from 12 months to 6 months using verified source GO-138.",
    href: "/admin/policy-updates",
    status: "Working",
    action: "Open Policy Updates",
    primaryLabel: "Open Policy Updates",
    facts: ["Old rule: 12 months", "New rule: 6 months", "Service affected: Income Certificate", "Propagation: tracked"],
  },
  {
    key: "compliance",
    title: "Compliance Drift",
    description:
      "Review compliance findings, outdated connected systems, severity, priority, and rerun checks.",
    href: "/admin/compliance",
    status: "Working",
    action: "Run Compliance Check",
    primaryLabel: "Open Compliance",
  },
  {
    key: "connected_systems",
    title: "Connected Systems / Propagation",
    description:
      "Track mock MeeSeva, public FAQ/form, propagation tasks, patch status, and integration health.",
    href: "/admin/propagation",
    status: "Working",
    action: "Open Propagation",
    primaryLabel: "Open Propagation",
    links: [
      { href: "/mock/meeseva", label: "Mock MeeSeva" },
      { href: "/mock/public-faq", label: "Mock Public FAQ" },
    ],
  },
  {
    key: "virtual_government",
    title: "Virtual Government Sandbox",
    description:
      "Virtual gazette, identity provider, OTP provider, payment gateway, demo certificate service, document vault, integration monitor, and scenario runner.",
    href: "/virtual-gov",
    status: "Working",
    action: "Run Virtual Government Scenario",
    primaryLabel: "Open Sandbox",
    links: [
      { href: "/virtual-gov/scenario-runner", label: "Scenario Runner" },
      { href: "/virtual-gov/cert-authority", label: "Demo Certificate Service" },
    ],
  },
  {
    key: "officer",
    title: "Officer Review",
    description: "Review pending applications, approve or reject requests, and trigger certificate generation.",
    href: "/officer",
    status: "Working",
    action: "Open Officer Review",
    primaryLabel: "Open Officer Review",
  },
  {
    key: "certificates",
    title: "Certificates",
    description: "Generate synthetic certificates in the sandbox and verify them publicly.",
    href: "/verify-certificate",
    status: "Working",
    action: "Verify Certificate",
    primaryLabel: "Open Verification",
    links: [{ href: "/virtual-gov/cert-authority", label: "Demo Certificate Service" }],
  },
  {
    key: "audit",
    title: "Audit Trail",
    description: "Records traceable events for policy, application, certificate, and demo actions.",
    href: "/admin/audit",
    status: "Working",
    action: "Run full flow",
    primaryLabel: "Open Audit Trail",
  },
  {
    key: "reports",
    title: "Reports",
    description: "Exports clean compliance, conflict, rule, and audit reports for review.",
    href: "/admin/reports",
    status: "Working",
    action: "Open reports",
    primaryLabel: "Open Reports",
  },
  {
    key: "hybrid_ollama",
    title: "Hybrid Answer Engine / Ollama",
    description:
      "Exact rule engine, RAG/search, deterministic fallback, Ollama status, and verified-context explanation.",
    href: "/admin/regulatory-ai",
    status: "Working",
    action: "Explain GO-138 using Local AI",
    primaryLabel: "Open Regulatory AI",
  },
  {
    key: "readiness",
    title: "Readiness & Ops",
    description: "Integration health, API health, database status, MFA/OTP status, and pilot readiness.",
    href: "/admin/readiness",
    status: "Working",
    action: "Open Readiness",
    primaryLabel: "Open Readiness",
  },
];

const orderedStepKeys = [
  "reset",
  "ingest",
  "extract",
  "compare",
  "conflicts",
  "impact",
  "review",
  "publish",
  "explain",
  "eligibility",
  "audit",
];

const pendingSteps = [
  "Reset Synthetic Sandbox",
  "Ingest Synthetic Circular",
  "Extract Metadata and Clauses",
  "Compare Policy Versions",
  "Detect Conflicts",
  "Trace Downstream Impact",
  "Send to Officer Review",
  "Approve and Publish",
  "Generate Officer and Citizen Views",
  "Rerun Eligibility Scenarios",
  "Preserve Audit History",
].map((label, index) => ({
  key: orderedStepKeys[index],
  label,
  status: "pending",
  details: "Waiting for demo run.",
}));

const stepDisplayLabels = {
  reset: "Reset Synthetic Sandbox",
  ingest: "Ingest Synthetic Circular",
  extract: "Extract Metadata and Clauses",
  compare: "Compare Policy Versions",
  conflicts: "Detect Conflicts",
  impact: "Trace Downstream Impact",
  review: "Send to Officer Review",
  publish: "Approve and Publish",
  explain: "Generate Officer and Citizen Views",
  eligibility: "Rerun Eligibility Scenarios",
  audit: "Preserve Audit History",
};

function statusTone(status) {
  if (status === "Working" || status === "success" || status === "Online") return "ready";
  if (status === "Mock" || status === "Fallback") return "mock";
  if (status === "Failed" || status === "failed") return "failed";
  return "config";
}

function StatusBadge({ children }) {
  return <span className={`unified-status unified-status-${statusTone(children)}`}>{children}</span>;
}

function stepStatusLabel(status, step) {
  if (step?.key === "explain" && step?.payload?.citizen_explanation?.fallback) return "Fallback";
  if (status === "success") return "Success";
  if (status === "failed") return "Failed";
  if (status === "running") return "Running";
  return "Pending";
}

function stepDisplayLabel(step) {
  return stepDisplayLabels[step?.key] || step?.label || "Demo step";
}

function enrichCards(cards, liveStatus, aiStatus) {
  return cards.map((card) => {
    if (card.key === "hybrid_ollama") {
      if (aiStatus?.status === "online") {
        return { ...card, status: "Online" };
      }
      return { ...card, status: "Fallback" };
    }
    if (card.key === "virtual_government" && liveStatus?.virtualGovError) {
      return { ...card, status: "Failed" };
    }
    return card;
  });
}

function formatValue(value) {
  if (value === null || value === undefined || value === "") return "Not available";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function primaryLinkLabel(card) {
  if (card.primaryLabel) return card.primaryLabel;
  if (/^(Open|Verify)/.test(card.action || "")) return card.action;
  return "Open";
}

export default function UnifiedDemoPortal() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [liveStatus, setLiveStatus] = useState({});
  const [aiStatus, setAiStatus] = useState(null);
  const [runStatus, setRunStatus] = useState("idle");
  const [steps, setSteps] = useState(pendingSteps);
  const [entities, setEntities] = useState({});
  const [lifecycleResult, setLifecycleResult] = useState(null);
  const [aiExplanation, setAiExplanation] = useState(null);
  const [hybridAnswer, setHybridAnswer] = useState(null);
  const [testStatus, setTestStatus] = useState("");

  async function loadStatus() {
    setLoading(true);
    setError("");
    try {
      const [integration, summary, virtualGov, services, mockSystems, ai] = await Promise.allSettled([
        getIntegrationHealth(),
        getDashboardSummary(),
        getVirtualGovStatus(),
        getPortalServices(),
        getMockSystems(),
        getAIStatus(),
      ]);
      setLiveStatus({
        integration: integration.value,
        summary: summary.value?.summary,
        virtualGov: virtualGov.value,
        virtualGovError: virtualGov.status === "rejected",
        serviceCount: services.value?.services?.length || 0,
        mockSystems: mockSystems.value?.systems || {},
      });
      setAiStatus(ai.value || null);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadStatus();
  }, []);

  const cards = useMemo(() => enrichCards(portalCards, liveStatus, aiStatus), [aiStatus, liveStatus]);

  async function handleRunFullDemo() {
    setRunStatus("running");
    setError("");
    setAiExplanation(null);
    setLifecycleResult(null);
    setEntities({});
    setSteps(pendingSteps.map((step) => ({ ...step, status: "running", details: "Queued." })));
    try {
      const result = await runPolicyLifecycleDemo();
      const resultSteps = result.steps?.length ? result.steps : [];
      setSteps(resultSteps);
      setLifecycleResult(result);
      setEntities({
        circular_number: result.circular?.circular_number,
        effective_date: result.circular?.effective_date,
        expiry_date: result.circular?.expiry_date,
        previous_version: result.comparison?.previous_version?.id,
        current_version: result.publication?.rule_version?.id,
        conflict_count: result.conflicts?.length || 0,
        changed_scenarios: result.eligibility?.changed_count || 0,
      });
      if (result.citizen_explanation) {
        setAiExplanation({
          provider: result.citizen_explanation.provider,
          model: result.citizen_explanation.model,
          fallback: result.citizen_explanation.fallback,
          answer: result.citizen_explanation.text,
        });
      }
      setRunStatus(result.success ? "success" : "failed");
      await loadStatus();
    } catch (runError) {
      setRunStatus("failed");
      setError(runError.message);
      setSteps((current) =>
        current.map((step) => (step.status === "running" ? { ...step, status: "failed", details: runError.message } : step)),
      );
    }
  }

  async function handleTestOllama() {
    setTestStatus("Testing local AI explanation...");
    setError("");
    try {
      const explanation = await getVerifiedAIExplanation("Explain GO-138 in simple words");
      setAiExplanation(explanation);
      setTestStatus(
        explanation.fallback
          ? "Ollama unavailable. Deterministic fallback is active."
          : "Ollama explanation returned from local model.",
      );
      setAiStatus(await getAIStatus());
    } catch (testError) {
      setTestStatus("");
      setError(testError.message);
    }
  }

async function handleAskHybrid() {
    setTestStatus("Asking hybrid answer engine...");
    setError("");
    try {
      const answer = await askHybridDemoQuestion("income certificate validity entha");
      setHybridAnswer(answer);
      setTestStatus("Hybrid answer engine returned a source-backed answer.");
    } catch (answerError) {
      setTestStatus("");
      setError(answerError.message);
    }
  }

  async function handleRunCompliance() {
    setTestStatus("Running compliance check...");
    setError("");
    try {
      await runCompliance();
      setTestStatus("Compliance check completed.");
      await loadStatus();
    } catch (complianceError) {
      setTestStatus("");
      setError(complianceError.message);
    }
  }

  return (
    <main className="unified-shell">
      <section className="unified-banner" role="note">
        NiyamGuard Virtual Government Sandbox - Synthetic pilot testing only. Not an official government portal.
      </section>

      <header className="unified-header">
        <div>
          <p className="eyebrow">Government Portal</p>
          <h1>NiyamGuard Government Portal</h1>
          <p>
            Follow one synthetic circular from validated intake through extraction, version
            comparison, conflict and impact analysis, human review, citizen guidance,
            eligibility reruns, and an auditable publication result.
          </p>
        </div>
        <div className="unified-actions">
          <button className="button button-primary" disabled={runStatus === "running"} onClick={handleRunFullDemo} type="button">
            {runStatus === "running" ? "Running Policy Lifecycle..." : "Run Connected Policy Lifecycle"}
          </button>
          <button className="button button-secondary" disabled={loading} onClick={() => void loadStatus()} type="button">
            Refresh Status
          </button>
          <a className="button button-secondary" href="/">Back to Portals</a>
        </div>
      </header>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {loading ? <p className="demo-loading">Loading portal status...</p> : null}

      <section className="unified-live-strip" aria-label="Live system status">
        <article>
          <span>Backend</span>
          <strong>{liveStatus.integration?.status || "Unknown"}</strong>
        </article>
        <article>
          <span>Services</span>
          <strong>{liveStatus.serviceCount || 0}</strong>
        </article>
        <article>
          <span>Virtual apps</span>
          <strong>{liveStatus.virtualGov?.applications || 0}</strong>
        </article>
        <article>
          <span>Certificates</span>
          <strong>{liveStatus.virtualGov?.certificates || 0}</strong>
        </article>
        <article>
          <span>Local AI</span>
          <strong>
            {aiStatus?.status === "online"
              ? `Ollama Online - ${aiStatus?.model || "qwen2.5:7b-instruct"}`
              : "Fallback"}
          </strong>
        </article>
      </section>

      <section className="unified-grid" aria-label="Government product modules">
        {cards.map((card) => (
          <article className="unified-card" key={card.key}>
            <div className="unified-card-top">
              <StatusBadge>{card.status}</StatusBadge>
              <h2>{card.title}</h2>
            </div>
            <p>{card.description}</p>
            <div className="unified-card-actions">
              {card.key === "hybrid_ollama" ? (
                <button className="button button-secondary" onClick={handleTestOllama} type="button">
                  Explain GO-138 using Local AI
                </button>
              ) : card.key === "compliance" ? (
                <button className="button button-secondary" onClick={handleRunCompliance} type="button">
                  Run Compliance Check
                </button>
              ) : card.key === "circular_policy" ? (
                <button className="button button-secondary" disabled={runStatus === "running"} onClick={handleRunFullDemo} type="button">
                  Publish / Update Circular
                </button>
              ) : card.key === "hybrid" ? (
                <button className="button button-secondary" onClick={handleAskHybrid} type="button">
                  Ask Test Question
                </button>
              ) : card.key === "virtual_government" || card.action === "Run full flow" ? (
                <button className="button button-secondary" disabled={runStatus === "running"} onClick={handleRunFullDemo} type="button">
                  {card.action}
                </button>
              ) : null}
              <a className="button button-secondary" href={card.href}>{primaryLinkLabel(card)}</a>
              {(card.links || []).map((link) => (
                <a className="button button-secondary" href={link.href} key={link.href}>{link.label}</a>
              ))}
            </div>
            {card.facts?.length ? (
              <ul className="unified-card-facts">
                {card.facts.map((fact) => <li key={fact}>{fact}</li>)}
              </ul>
            ) : null}
          </article>
        ))}
      </section>

      <section className="unified-stepper" aria-labelledby="portal-stepper-title">
        <div className="unified-section-heading">
          <div>
            <p className="eyebrow">Guided workflow</p>
            <h2 id="portal-stepper-title">One circular, one connected evidence trail</h2>
          </div>
          <StatusBadge>{runStatus === "success" ? "success" : runStatus === "failed" ? "failed" : runStatus === "running" ? "running" : "pending"}</StatusBadge>
        </div>
        <ol>
          {steps.map((step, index) => (
            <li className={`unified-step unified-step-${step.status}`} key={step.key || `${step.label}-${index}`}>
              <span>{index + 1}</span>
              <div>
                <h3>{stepDisplayLabel(step)}</h3>
                <p>{step.details}</p>
              </div>
              <strong>{stepStatusLabel(step.status, step)}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="unified-result-grid" aria-label="Generated demo entities">
        <article className="unified-result-panel">
          <p className="eyebrow">Policy result</p>
          <h2>Verified lifecycle output</h2>
          <dl>
            <div>
              <dt>Circular</dt>
              <dd data-testid="lifecycle-circular">{formatValue(entities.circular_number)}</dd>
            </div>
            <div>
              <dt>Effective date</dt>
              <dd>{formatValue(entities.effective_date)}</dd>
            </div>
            <div>
              <dt>Expiry date</dt>
              <dd>{formatValue(entities.expiry_date)}</dd>
            </div>
            <div>
              <dt>Version link</dt>
              <dd>{formatValue(entities.previous_version)} → {formatValue(entities.current_version)}</dd>
            </div>
            <div>
              <dt>Open conflicts</dt>
              <dd>{formatValue(entities.conflict_count)}</dd>
            </div>
            <div>
              <dt>Eligibility outcomes changed</dt>
              <dd>{formatValue(entities.changed_scenarios)}</dd>
            </div>
          </dl>
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Source evidence</p>
          <h2>Clause and review boundary</h2>
          {lifecycleResult?.source_evidence ? (
            <div className="unified-ai-output" data-testid="lifecycle-evidence">
              <div className="source-badges">
                <span>{lifecycleResult.source_evidence.circular_number}</span>
                <span>Synthetic source</span>
                <span>Hash verified</span>
              </div>
              <p>{lifecycleResult.source_evidence.excerpt}</p>
              <p>
                Character range {lifecycleResult.source_evidence.character_range?.join("–")}.
                Review actions: {lifecycleResult.review_queue?.available_decisions?.join(", ")}.
              </p>
            </div>
          ) : null}
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Two audiences</p>
          <h2>Officer and citizen guidance</h2>
          {lifecycleResult?.officer_summary ? (
            <div className="unified-ai-output">
              <div className="source-badges"><span>Officer summary</span></div>
              <p>{lifecycleResult.officer_summary}</p>
            </div>
          ) : null}
          {aiExplanation ? (
            <div className="unified-ai-output" data-testid="ollama-output">
              <div className="source-badges">
                <span>Citizen explanation</span>
                <span>{aiExplanation.fallback ? "Deterministic fallback" : "Local Ollama"}</span>
                <span>{aiExplanation.provider || "provider unknown"}</span>
              </div>
              <p>{aiExplanation.answer || aiExplanation.summary || "No explanation returned."}</p>
            </div>
          ) : null}
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Impact chain</p>
          <h2>Connected services and systems</h2>
          {lifecycleResult?.impact ? (
            <dl>
              <div><dt>Schemes</dt><dd>{lifecycleResult.impact.schemes?.map((item) => item.name).join(", ") || "None"}</dd></div>
              <div><dt>Forms</dt><dd>{lifecycleResult.impact.forms?.map((item) => item.name).join(", ") || "None"}</dd></div>
              <div><dt>Department</dt><dd>{lifecycleResult.impact.departments?.map((item) => item.name).join(", ") || "None"}</dd></div>
              <div><dt>Connected systems</dt><dd>{lifecycleResult.impact.connected_systems?.length || 0}</dd></div>
            </dl>
          ) : <p>Run the lifecycle to resolve downstream impact.</p>}
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Eligibility regression</p>
          <h2>Before and after rule evaluation</h2>
          {lifecycleResult?.eligibility?.results?.length ? (
            <ul className="unified-card-facts" data-testid="eligibility-results">
              {lifecycleResult.eligibility.results.map((scenario) => (
                <li key={scenario.id}>
                  <strong>{scenario.certificate_age_months} months:</strong>{" "}
                  {scenario.eligible_before ? "eligible" : "not eligible"} →{" "}
                  {scenario.eligible_after ? "eligible" : "not eligible"}
                  {scenario.changed ? " (changed)" : ""}
                </li>
              ))}
            </ul>
          ) : <p>Run the lifecycle to evaluate deterministic fixtures.</p>}
        </article>
      </section>
    </main>
  );
}
