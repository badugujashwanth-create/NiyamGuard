import { useEffect, useMemo, useState } from "react";

import {
  getDashboardSummary,
  getIntegrationHealth,
  getLatestPublicRule,
  reportExportUrl,
  runCompliance,
  scanConflicts,
} from "../services/api";

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

export default function DemoDashboard() {
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [verifiedRule, setVerifiedRule] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState("");
  const [error, setError] = useState("");

  async function refreshDemoData() {
    const [healthResponse, summaryResponse, ruleResponse] = await Promise.all([
      getIntegrationHealth(),
      getDashboardSummary(),
      getLatestPublicRule("income_certificate", "validity"),
    ]);
    setHealth(healthResponse);
    setSummary(summaryResponse.summary);
    setVerifiedRule(ruleResponse);
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
      await runCompliance();
      await scanConflicts();
      await refreshDemoData();
      setActionStatus("Compliance demo complete: drift and conflict data refreshed.");
    } catch (actionError) {
      setError(actionError.message);
      setActionStatus("");
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
    ],
    [health, summary],
  );

  return (
    <main className="demo-shell">
      <section className="demo-hero">
        <div>
          <p className="eyebrow">Final presentation dashboard</p>
          <h1>NiyamGuard AI Demo</h1>
          <p>
            One path for judges: verified circulars, compliance drift detection,
            citizen impact tracing, and a voice assistant that answers from the
            approved public rule API.
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
            <a className="button button-primary" href={reportExportUrl("compliance", "csv")}>
              Export Compliance CSV
            </a>
            <a className="button button-secondary" href={reportExportUrl("conflicts", "csv")}>
              Export Conflicts CSV
            </a>
            <a className="button button-secondary" href={reportExportUrl("rules", "json")}>
              Export Rules JSON
            </a>
          </div>
        </article>
      </section>
    </main>
  );
}
