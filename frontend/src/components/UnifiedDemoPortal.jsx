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
  runFullEndToEndDemo,
} from "../services/api";

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
      "Virtual gazette, identity provider, OTP provider, payment gateway, certificate authority, document vault, integration monitor, and scenario runner.",
    href: "/virtual-gov",
    status: "Working",
    action: "Run Virtual Government Scenario",
    primaryLabel: "Open Sandbox",
    links: [
      { href: "/virtual-gov/scenario-runner", label: "Scenario Runner" },
      { href: "/virtual-gov/cert-authority", label: "Certificate Authority" },
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
    description: "Generate certificates, sign in the sandbox certificate authority, and verify publicly.",
    href: "/verify-certificate",
    status: "Working",
    action: "Verify Certificate",
    primaryLabel: "Open Verification",
    links: [{ href: "/virtual-gov/cert-authority", label: "Certificate Authority" }],
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
  {
    key: "legacy_demo",
    title: "Legacy Demo Dashboard",
    description: "Original live presentation dashboard remains available as a secondary route.",
    href: "/demo",
    status: "Working",
    action: "Open Demo",
    primaryLabel: "Open Demo",
  },
];

const orderedStepKeys = [
  "reset_sandbox",
  "publish_circular",
  "ingest_circular",
  "update_verified_rule",
  "update_service_portal",
  "create_citizen_identity",
  "submit_application",
  "verify_otp",
  "complete_payment",
  "officer_approval",
  "generate_certificate",
  "sign_certificate",
  "verify_certificate",
  "patch_connected_systems",
  "rerun_compliance",
  "write_audit_trail",
  "ask_hybrid_answer",
  "generate_ollama_explanation",
];

const pendingSteps = [
  "Reset Sandbox",
  "Circular Published",
  "Circular Ingested",
  "Policy Rule Updated",
  "Service Portal Updated",
  "Citizen Identity Created",
  "Application Submitted",
  "OTP Verified",
  "Payment Completed",
  "Officer Approved",
  "Certificate Generated",
  "Certificate Signed",
  "Certificate Verified",
  "Connected Systems Patched",
  "Compliance Rerun",
  "Audit Trail Written",
  "Hybrid Answer Generated",
  "Ollama Explanation Generated or Fallback Active",
].map((label, index) => ({
  key: orderedStepKeys[index],
  label,
  status: "pending",
  details: "Waiting for demo run.",
}));

const stepDisplayLabels = {
  publish_circular: "Circular Published",
  ingest_circular: "Circular Ingested",
  update_verified_rule: "Policy Rule Updated",
  update_service_portal: "Service Portal Updated",
  create_citizen_identity: "Citizen Identity Created",
  submit_application: "Application Submitted",
  verify_otp: "OTP Verified",
  complete_payment: "Payment Completed",
  officer_approval: "Officer Approved",
  generate_certificate: "Certificate Generated",
  sign_certificate: "Certificate Signed",
  verify_certificate: "Certificate Verified",
  patch_connected_systems: "Connected Systems Patched",
  rerun_compliance: "Compliance Rerun",
  write_audit_trail: "Audit Trail Written",
  ask_hybrid_answer: "Hybrid Answer Generated",
  generate_ollama_explanation: "Ollama Explanation Generated or Fallback Active",
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
  if (step?.key === "generate_ollama_explanation" && step?.payload?.fallback) return "Fallback";
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
    setEntities({});
    setSteps(pendingSteps.map((step) => ({ ...step, status: "running", details: "Queued." })));
    try {
      const result = await runFullEndToEndDemo();
      const resultSteps = result.steps?.length ? result.steps : [];
      setSteps(resultSteps);
      setEntities(result.entities || {});
      const ollamaStep = resultSteps.find((step) => step.key === "generate_ollama_explanation");
      if (ollamaStep?.payload) {
        setAiExplanation({
          provider: ollamaStep.payload.provider,
          model: ollamaStep.payload.model,
          fallback: ollamaStep.payload.fallback,
          answer: ollamaStep.payload.text,
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
        NiyamGuard Virtual Government Sandbox - Demo and pilot testing only. Not an official government portal.
      </section>

      <header className="unified-header">
        <div>
          <p className="eyebrow">Government Portal</p>
          <h1>NiyamGuard Government Portal</h1>
          <p>
            Government users can publish sandbox circulars, update verified rules, run
            compliance checks, review applications, issue certificates, verify integrations,
            monitor audit trails, and test local AI explanation.
          </p>
        </div>
        <div className="unified-actions">
          <button className="button button-primary" disabled={runStatus === "running"} onClick={handleRunFullDemo} type="button">
            {runStatus === "running" ? "Running Full Demo..." : "Run Full End-to-End Demo"}
          </button>
          <button className="button button-secondary" disabled={loading} onClick={() => void loadStatus()} type="button">
            Refresh Status
          </button>
          <a className="button button-secondary" href="/">Back to Portals</a>
        </div>
      </header>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {loading ? <p className="demo-loading">Loading portal status...</p> : null}

      <section className="unified-live-strip" aria-label="Live demo status">
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

      <section className="unified-grid" aria-label="Unified demo modules">
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
            <h2 id="portal-stepper-title">Run Full End-to-End Demo</h2>
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
          <p className="eyebrow">Generated entities</p>
          <h2>Scenario output</h2>
          <dl>
            <div>
              <dt>Application number</dt>
              <dd data-testid="demo-application-number">{formatValue(entities.application_number)}</dd>
            </div>
            <div>
              <dt>Certificate number</dt>
              <dd data-testid="demo-certificate-number">{formatValue(entities.certificate_number)}</dd>
            </div>
            <div>
              <dt>Verification hash</dt>
              <dd data-testid="demo-verification-hash">{formatValue(entities.verification_hash)}</dd>
            </div>
            <div>
              <dt>Rule ID</dt>
              <dd>{formatValue(entities.rule_id)}</dd>
            </div>
          </dl>
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Hybrid Answer Engine</p>
          <h2>Source-backed answer</h2>
          <button className="button button-primary" onClick={handleAskHybrid} type="button">
            Ask Hybrid Test Question
          </button>
          {hybridAnswer ? (
            <div className="unified-ai-output" data-testid="hybrid-output">
              <div className="source-badges">
                <span>{hybridAnswer.method || "answer"}</span>
                <span>{hybridAnswer.provider || "deterministic"}</span>
                {hybridAnswer.verified ? <span>Verified Source</span> : null}
              </div>
              <p>{hybridAnswer.answer}</p>
            </div>
          ) : null}
        </article>

        <article className="unified-result-panel">
          <p className="eyebrow">Local AI / Ollama</p>
          <h2>Ollama Status: {aiStatus?.status === "online" ? "Online" : "Fallback active"}</h2>
          <p>
            Model: {aiStatus?.model || "qwen2.5:7b-instruct"}.
            {aiStatus?.status === "online"
              ? " Local Ollama is available for verified explanations."
              : " Ollama unavailable. Deterministic fallback is active."}
          </p>
          <p>
            Official policy answers and compliance decisions come from deterministic verified rules.
            Ollama only explains verified context.
          </p>
          <button className="button button-primary" onClick={handleTestOllama} type="button">
            Explain GO-138 using Local AI
          </button>
          {testStatus ? <p className="support-message">{testStatus}</p> : null}
          {aiExplanation ? (
            <div className="unified-ai-output" data-testid="ollama-output">
              <div className="source-badges">
                <span>{aiExplanation.fallback ? "Fallback" : "Ollama"}</span>
                <span>{aiExplanation.provider || "provider unknown"}</span>
              </div>
              <p>{aiExplanation.answer || aiExplanation.summary || "No explanation returned."}</p>
            </div>
          ) : null}
        </article>
      </section>
    </main>
  );
}
