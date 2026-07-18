import { useEffect, useMemo, useState } from "react";

import {
  demoReportExportUrl,
  applyMockDemoPatch,
  getAIStatus,
  getDashboardSummary,
  getIntegrationHealth,
  getLatestPublicRule,
  getMockSystems,
  resetMockSystems,
  runDemo,
  runSelfUpdateScenario,
  runVirtualGovScenario,
} from "../../services/api";

const demoCards = [
  {
    title: "Government Admin Portal",
    status: "Ready",
    demonstrates: "Live counters for circulars, verified rules, connected systems, drift, and conflicts.",
    href: "/admin",
    sample: "Open the dashboard and show the full government-core control room.",
  },
  {
    title: "Compliance Verification",
    status: "Online",
    demonstrates: "Checks verified GO-138 against portals, SOPs, FAQs, and forms.",
    href: "/admin/compliance",
    sample: "Run the compliance demo and show 3 drifted systems plus 1 compliant form.",
  },
  {
    title: "Cascade Impact Tracing",
    status: "Ready",
    demonstrates: "Explains how stale policy data can lead to wrong citizen outcomes.",
    href: "/admin/cascade",
    sample: "Trace circular change to portal drift and citizen harm risk.",
  },
  {
    title: "Priority Dashboard",
    status: "Ready",
    demonstrates: "Ranks drift findings by citizen impact, urgency, and service risk.",
    href: "/admin",
    sample: "Show critical findings at the top of the dashboard.",
  },
  {
    title: "Conflict Detection",
    status: "Ready",
    demonstrates: "Detects old GO-112 saying 12 months while GO-138 says 6 months.",
    href: "/admin/conflicts",
    sample: "Show the recommendation to keep GO-138 active and supersede GO-112.",
  },
  {
    title: "Citizen Voice Form Assistant",
    status: "Ready",
    demonstrates: "Guides citizens through forms in Telugu, Hindi, and English without auto-submitting.",
    href: "/",
    sample: "Ask: income certificate validity entha.",
  },
  {
    title: "Citizen Scheme Finder",
    status: "Ready",
    demonstrates: "Suggests possible services from simple profile answers with cautious source-labelled guidance.",
    href: "/scheme-finder",
    sample: "Select student + scholarship and show Income Certificate recommendation.",
  },
  {
    title: "Public Verified Rule API",
    status: "Online",
    demonstrates: "Exposes citizen-safe verified answers sourced from approved circulars.",
    href: "/",
    sample: "Show verified 6 months answer with GO-138 source.",
  },
  {
    title: "Reports & Export",
    status: "Ready",
    demonstrates: "Exports compliance, conflict, and rule data for officials.",
    href: "/admin/reports",
    sample: "Export the compliance CSV report.",
  },
];

const storySteps = [
  "Government uploads circular",
  "AI extracts policy rule",
  "Officer approves verified rule",
  "System checks connected systems",
  "Drift is detected in portal, SOP, and FAQ",
  "Cascade trace shows citizen harm",
  "Priority dashboard ranks the risk",
  "Citizen assistant uses verified rule",
  "Report is exported",
];

const platformFlowCards = [
  {
    title: "Virtual Gazette",
    description: "Publishes sandbox circulars like GO-138 for demo policy updates.",
    href: "/virtual-gov",
  },
  {
    title: "Policy Engine",
    description: "Ingests circular data and updates verified rule versions.",
    href: "/admin/policy-updates",
  },
  {
    title: "Service Portal",
    description: "Shows citizen services that reflect the current verified rules.",
    href: "/services",
  },
  {
    title: "Citizen Application",
    description: "Creates a sandbox application draft with documents and status tracking.",
    href: "/apply/income_certificate",
  },
  {
    title: "Officer Review",
    description: "Lets an officer review evidence and approve the sandbox application.",
    href: "/officer",
  },
  {
    title: "Demo Certificate Service",
    description: "Generates a synthetic demo certificate after officer approval.",
    href: "/officer",
  },
  {
    title: "Public Verification",
    description: "Verifies a demo certificate number or hash from the public page.",
    href: "/verify-certificate",
  },
  {
    title: "Compliance Engine",
    description: "Detects drift between verified rules and connected systems.",
    href: "/admin/compliance",
  },
  {
    title: "Audit Trail",
    description: "Records important sandbox events for review and traceability.",
    href: "/admin/audit",
  },
  {
    title: "Hybrid Answer Engine",
    description: "Answers citizen questions with deterministic rules and source cards.",
    href: "/admin/regulatory-ai",
  },
];

const manualDemoLinks = [
  ["Demo Dashboard", "/demo"],
  ["Virtual Government", "/virtual-gov"],
  ["Services", "/services"],
  ["Citizen Applications", "/applications"],
  ["Officer Portal", "/officer"],
  ["Certificate Verification", "/verify-certificate"],
  ["Admin Compliance", "/admin/compliance"],
  ["Admin Readiness", "/admin/readiness"],
  ["Admin Audit", "/admin/audit"],
];

const demoAccounts = [
  ["Admin", "admin@niyamguard.local", "Admin@12345"],
  ["Officer", "officer@niyamguard.local", "Officer@12345"],
  ["Citizen", "citizen@niyamguard.local", "Citizen@12345"],
];

function statusText(isOnline) {
  return isOnline ? "Online" : "Offline";
}

function StatusBadge({ children, tone = "ready" }) {
  return <span className={`demo-status demo-status-${tone}`}>{children}</span>;
}

function valueFromPublicRule(rule) {
  const answer = rule?.answer || "";
  const match = answer.match(/currently\s+(.+?)\.?$/i);
  return match?.[1]?.replace(/\.$/, "") || "Source not available";
}

function hasScenarioStep(result, stepId) {
  return Boolean(result?.steps?.some((step) => step.step_id === stepId));
}

function scenarioResultRows(result) {
  const certificateStep = result?.steps?.find((step) => step.step_id === "certificate_issued");
  return [
    ["Circular Published", Boolean(result?.success)],
    ["Rule Updated", Boolean(result?.success && (result?.artifacts?.source_rule || hasScenarioStep(result, "regulation_question")))],
    ["Citizen Application Created", hasScenarioStep(result, "application_created")],
    ["Payment Completed", hasScenarioStep(result, "payment_completed")],
    ["Officer Approved", hasScenarioStep(result, "certificate_issued")],
    ["Certificate Generated", Boolean(result?.artifacts?.certificate_number)],
    ["Certificate Verified", Boolean(certificateStep?.payload?.certificate_valid)],
    ["Compliance Rerun", hasScenarioStep(result, "compliance_demo_flow")],
    ["Audit Events Created", Boolean(result?.success)],
  ];
}

export default function DemoDashboard() {
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [verifiedRule, setVerifiedRule] = useState(null);
  const [mockSystems, setMockSystems] = useState({});
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState("");
  const [fullDemoStatus, setFullDemoStatus] = useState("idle");
  const [fullDemoResult, setFullDemoResult] = useState(null);
  const [fullDemoError, setFullDemoError] = useState("");
  const [error, setError] = useState("");

  async function refreshDemoData() {
    const [healthResponse, summaryResponse, ruleResponse, aiResponse, mockResponse] = await Promise.all([
      getIntegrationHealth(),
      getDashboardSummary(),
      getLatestPublicRule("income_certificate", "validity"),
      getAIStatus(),
      getMockSystems(),
    ]);
    setHealth(healthResponse);
    setSummary(summaryResponse.summary);
    setVerifiedRule(ruleResponse);
    setAiStatus(aiResponse);
    setMockSystems(mockResponse.systems || {});
  }

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        await refreshDemoData();
      } catch (loadError) {
        if (active) setError(loadError.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, []);

  async function runComplianceDemo() {
    setActionStatus("Running compliance verification...");
    setError("");
    try {
      await runDemo();
      await refreshDemoData();
      setActionStatus("Compliance demo complete: drift and conflict data refreshed.");
    } catch (actionError) {
      setError(actionError.message);
      setActionStatus("");
    }
  }

  async function runSelfUpdateDemo(applyDemoPatch = false) {
    setActionStatus(applyDemoPatch ? "Running self-update scenario and patching mock systems..." : "Running self-update scenario...");
    setError("");
    try {
      await runSelfUpdateScenario({ applyDemoPatch, resetMockSystems: applyDemoPatch });
      await refreshDemoData();
      setActionStatus(applyDemoPatch ? "Self-update scenario complete: mock systems now show 6 months." : "Self-update workflow complete: propagation tasks are ready.");
    } catch (actionError) {
      setError(actionError.message);
      setActionStatus("");
    }
  }

  async function resetMockDemo() {
    setActionStatus("Resetting mock systems to outdated 12-month values...");
    setError("");
    try {
      await resetMockSystems();
      await refreshDemoData();
      setActionStatus("Mock systems reset. MeeSeva and FAQ now show outdated values.");
    } catch (actionError) {
      setError(actionError.message);
      setActionStatus("");
    }
  }

  async function patchMockDemo() {
    setActionStatus("Applying demo patch to mock connected systems...");
    setError("");
    try {
      await applyMockDemoPatch();
      await refreshDemoData();
      setActionStatus("Mock systems patched to the verified 6-month rule.");
    } catch (actionError) {
      setError(actionError.message);
      setActionStatus("");
    }
  }

  async function runFullVirtualGovernmentDemo() {
    setFullDemoStatus("running");
    setFullDemoResult(null);
    setFullDemoError("");
    setError("");
    try {
      const result = await runVirtualGovScenario({
        scenarioId: "income_certificate_full_flow",
        resetBeforeRun: true,
      });
      if (!result?.success) {
        throw new Error(result?.error || "Scenario runner did not return success.");
      }
      setFullDemoResult(result);
      setFullDemoStatus("complete");
    } catch {
      setFullDemoStatus("fallback");
      setFullDemoError("Scenario runner is not available. Please use the manual demo links below.");
    }
  }

  const healthCards = useMemo(
    () => [
      ["Backend API", Boolean(health), statusText(Boolean(health))],
      ["Integration health", health?.status === "online", health?.status || "Offline"],
      [
        "Verified Knowledge Base",
        Number(health?.counts?.verified_rules || summary?.verified_rules || 0) > 0,
        `${health?.counts?.verified_rules || summary?.verified_rules || 0} rules`,
      ],
      ["Admin Dashboard", true, "Ready"],
      ["Citizen Portal", true, "Ready"],
      [
        "AI Provider Status",
        aiStatus?.status === "online",
        aiStatus?.status === "online" ? "Online" : "Fallback",
      ],
      [
        "Ollama Local LLM",
        aiStatus?.status === "online",
        aiStatus?.model || "qwen2.5:7b-instruct",
      ],
      ["RAG Knowledge Index", Boolean(aiStatus?.rag_enabled), aiStatus?.rag_enabled ? "Enabled" : "Off"],
    ],
    [aiStatus, health, summary],
  );

  return (
    <main className="demo-shell">
      <section className="unified-banner" role="note">
        Recruiter walkthrough — synthetic data only. No official application, payment, or certificate is created.
      </section>
      <section className="demo-hero">
        <div>
          <p className="eyebrow">Guided product simulation</p>
          <h1>NiyamGuard AI Demo</h1>
          <p>
            One recruiter-friendly path through a policy change, human approval,
            compliance drift, citizen impact, a synthetic service journey, and
            source-backed guidance.
          </p>
        </div>
        <div className="demo-hero-actions" aria-label="Demo quick links">
          <a className="button button-primary" href="/">
            Open Citizen Portal
          </a>
          <a className="button button-secondary" href="/admin">
            Open Admin Portal
          </a>
          <button className="button button-primary" onClick={runComplianceDemo} type="button">
            Run Compliance Demo
          </button>
          <button
            className="button button-secondary"
            onClick={() => void refreshDemoData()}
            type="button"
          >
            Open Verified Rule
          </button>
          <a className="button button-secondary" href="/admin/reports">
            Open Reports
          </a>
        </div>
      </section>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {loading ? <p className="demo-loading">Loading demo status...</p> : null}
      {actionStatus ? <p className="demo-action-status">{actionStatus}</p> : null}

      <section className="demo-health" aria-label="Live health status">
        {healthCards.map(([label, online, value]) => (
          <article key={label}>
            <span>{label}</span>
            <StatusBadge tone={online ? "ready" : "offline"}>{value}</StatusBadge>
          </article>
        ))}
      </section>

      <section className="demo-story demo-how-it-works" aria-labelledby="how-it-works-title">
        <div>
          <p className="eyebrow">How everything works</p>
          <h2 id="how-it-works-title">Full virtual government flow</h2>
          <p>
            Virtual Government Sandbox - for demonstration and pilot testing only.
            Not an official government portal.
          </p>
          <button
            className="button button-primary"
            disabled={fullDemoStatus === "running"}
            onClick={runFullVirtualGovernmentDemo}
            type="button"
          >
            {fullDemoStatus === "running" ? "Running Demo..." : "Run Full Virtual Government Demo"}
          </button>
        </div>
        <div className="demo-flow-grid">
          {platformFlowCards.map((card) => (
            <article className="demo-flow-card" key={card.title}>
              <div>
                <StatusBadge>Working</StatusBadge>
                <h3>{card.title}</h3>
                <p>{card.description}</p>
              </div>
              <a className="button button-secondary" href={card.href}>
                Open
              </a>
            </article>
          ))}
        </div>
      </section>

      {fullDemoStatus === "complete" && fullDemoResult ? (
        <section className="demo-source-panel demo-result-panel" aria-labelledby="full-demo-result-title">
          <p className="eyebrow">Run demo result</p>
          <h2 id="full-demo-result-title">Full virtual government demo completed</h2>
          <div className="demo-result-grid">
            {scenarioResultRows(fullDemoResult).map(([label, ok]) => (
              <article key={label}>
                <span>{label}</span>
                <StatusBadge tone={ok ? "ready" : "offline"}>{ok ? "success" : "not shown"}</StatusBadge>
              </article>
            ))}
          </div>
          <dl>
            <div>
              <dt>Application</dt>
              <dd>{fullDemoResult.artifacts?.application_number || "Not available"}</dd>
            </div>
            <div>
              <dt>Certificate</dt>
              <dd>{fullDemoResult.artifacts?.certificate_number || "Not available"}</dd>
            </div>
            <div>
              <dt>Verification Hash</dt>
              <dd>{fullDemoResult.artifacts?.verification_hash || "Not available"}</dd>
            </div>
          </dl>
        </section>
      ) : null}

      {fullDemoStatus === "fallback" ? (
        <section className="demo-source-panel demo-result-panel" aria-label="Scenario fallback">
          <p>{fullDemoError}</p>
        </section>
      ) : null}

      <section className="demo-story" aria-labelledby="demo-story-title">
        <div>
          <p className="eyebrow">Demo case</p>
          <h2 id="demo-story-title">GO-138 changed the rule, old systems still show 12 months</h2>
          <p>
            Circular GO-138 changed Income Certificate validity from 12 months to
            6 months. MeeSeva portal, officer SOP, and public FAQ still show 12
            months. NiyamGuard detects this drift and exposes the verified
            6-month rule to the citizen side.
          </p>
        </div>
        <ol>
          {storySteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </section>

      <section className="demo-story" aria-labelledby="demo-ai-title">
        <div>
          <p className="eyebrow">Where AI is used</p>
          <h2 id="demo-ai-title">Local explanations, deterministic decisions</h2>
          <p>
            NiyamGuard uses deterministic verification for sandbox compliance decisions.
            A local LLM through Ollama is used only to explain verified findings and answer
            citizen questions from retrieved knowledge sources.
          </p>
        </div>
        <ol>
          <li>Verified Rule badge means the answer came from approved policy data.</li>
          <li>RAG Source badge means the answer was grounded in retrieved knowledge chunks.</li>
          <li>Seed Demo Data badge means the source is useful for demos but not official.</li>
          <li>Fallback badge means Ollama was unavailable and a deterministic template answered.</li>
        </ol>
      </section>

      <section className="demo-story" aria-labelledby="self-update-demo-title">
        <div>
          <p className="eyebrow">Live connected system demo</p>
          <h2 id="self-update-demo-title">Self-updating policy engine</h2>
          <p>
            Start with the mock MeeSeva and public FAQ pages showing stale 12-month
            validity. Run the update workflow to publish the verified rule, then
            patch the mock systems to show 6 months from GO-138.
          </p>
          <div className="demo-export-actions">
            <button className="button button-secondary" onClick={resetMockDemo} type="button">
              Reset Mock Systems
            </button>
            <button className="button button-secondary" onClick={() => void runSelfUpdateDemo(false)} type="button">
              Run Update Workflow
            </button>
            <button className="button button-primary" onClick={() => void runSelfUpdateDemo(true)} type="button">
              Run and Patch
            </button>
            <button className="button button-secondary" onClick={patchMockDemo} type="button">
              Patch Only
            </button>
          </div>
        </div>
        <ol>
          {Object.values(mockSystems).map((system) => (
            <li key={system.id}>
              {system.system_name}: {system.displayed_value || system.faq_value} / {system.sync_status}
            </li>
          ))}
          <li><a href="/mock/meeseva">Open mock MeeSeva portal</a></li>
          <li><a href="/mock/public-faq">Open mock public FAQ</a></li>
        </ol>
      </section>

      <section className="demo-module-grid" aria-label="Demo modules">
        {demoCards.map((card) => (
          <article className="demo-module-card" key={card.title}>
            <div>
              <div className="demo-card-topline">
                <StatusBadge>{card.status}</StatusBadge>
              </div>
              <h3>{card.title}</h3>
              <p>{card.demonstrates}</p>
            </div>
            <div className="demo-card-action">
              <span>Sample action: {card.sample}</span>
              <a className="button button-secondary" href={card.href}>
                Open
              </a>
            </div>
          </article>
        ))}
      </section>

      <section className="demo-final-grid" aria-label="Verified data and exports">
        <article className="demo-source-panel">
          <p className="eyebrow">Verified public rule</p>
          <h2>Income Certificate Validity</h2>
          {verifiedRule?.verified ? (
            <dl>
              <div>
                <dt>Current Value</dt>
                <dd>{valueFromPublicRule(verifiedRule)}</dd>
              </div>
              <div>
                <dt>Circular</dt>
                <dd>{verifiedRule.source?.circular_number || "Source not available"}</dd>
              </div>
              <div>
                <dt>Department</dt>
                <dd>{verifiedRule.source?.department || "Source not available"}</dd>
              </div>
              <div>
                <dt>Confidence</dt>
                <dd>
                  {verifiedRule.source?.confidence
                    ? `${Math.round(verifiedRule.source.confidence * 100)}%`
                    : "Source not available"}
                </dd>
              </div>
            </dl>
          ) : (
            <p>Source not available. Please verify from official government source.</p>
          )}
        </article>
        <article className="demo-source-panel">
          <p className="eyebrow">Reports</p>
          <h2>Presentation exports</h2>
          <p>
            Use these exports when explaining what officials receive after drift
            is detected and prioritized.
          </p>
          <div className="demo-export-actions">
            <a className="button button-primary" href={demoReportExportUrl("compliance", "csv")}>
              Export Compliance CSV
            </a>
            <a className="button button-secondary" href={demoReportExportUrl("conflicts", "csv")}>
              Export Conflicts CSV
            </a>
            <a className="button button-secondary" href={demoReportExportUrl("rules", "json")}>
              Export Rules JSON
            </a>
          </div>
        </article>
      </section>

      <section className="demo-final-grid" aria-label="Manual demo links and accounts">
        <article className="demo-source-panel">
          <p className="eyebrow">Manual demo links</p>
          <h2>Open these screens one by one</h2>
          <div className="demo-link-list">
            {manualDemoLinks.map(([label, href]) => (
              <a href={href} key={href}>
                <span>{label}</span>
                <code>{href}</code>
              </a>
            ))}
          </div>
        </article>
        <article className="demo-source-panel">
          <p className="eyebrow">Demo accounts</p>
          <h2>Use these logins</h2>
          <div className="demo-account-table" role="table" aria-label="Demo accounts">
            {demoAccounts.map(([role, email, password]) => (
              <div role="row" key={role}>
                <strong role="cell">{role}</strong>
                <code role="cell">{email}</code>
                <code role="cell">{password}</code>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
