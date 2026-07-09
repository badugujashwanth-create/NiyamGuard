import { useEffect, useMemo, useState } from "react";

import {
  askDatasetQA,
  createUser,
  downloadReport,
  generateAIFindingSummary,
  getAIStatus,
  getAdminSummary,
  getAuditEvents,
  getCascadeForFinding,
  getComplianceFindings,
  getConnectedSystems,
  getDatasetDemoFlow,
  getDatasetStatus,
  getConflicts,
  getKnowledgeRules,
  getModuleStatus,
  getPriorityFindings,
  getReportsSummary,
  getUsers,
  recalculatePriority,
  runCompliance,
  scanConflicts,
  verifyAudit,
} from "../services/api";

const pages = [
  { path: "/admin", label: "Dashboard" },
  { path: "/admin/compliance", label: "Compliance" },
  { path: "/admin/cascade", label: "Cascade" },
  { path: "/admin/conflicts", label: "Conflicts" },
  { path: "/admin/knowledge-base", label: "Knowledge Base" },
  { path: "/admin/regulatory-ai", label: "Regulatory AI" },
  { path: "/admin/reports", label: "Reports" },
  { path: "/admin/audit", label: "Audit" },
  { path: "/admin/users", label: "Users" },
];

const circularById = {
  circ_001: "GO-138",
  circ_000: "GO-112",
};

function numberOrZero(value) {
  return Number.isFinite(Number(value)) ? Number(value) : 0;
}

function titleCase(value = "") {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function StatusPill({ children, tone = "neutral" }) {
  return <span className={`admin-pill admin-pill-${tone}`}>{children}</span>;
}

function sourceCircular(rule) {
  return circularById[rule?.circular_id] || rule?.circular_id || "GO-138";
}

function ruleValue(rule) {
  if (!rule) return "Rule unavailable";
  return `${sourceCircular(rule)}: ${rule.current_value} ${rule.unit || ""}`.trim();
}

export default function AdminPortal({ currentUser, onLogout, onUnauthorized }) {
  const [path, setPath] = useState(window.location.pathname);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reportStatus, setReportStatus] = useState("");
  const [summary, setSummary] = useState(null);
  const [moduleStatus, setModuleStatus] = useState([]);
  const [systems, setSystems] = useState([]);
  const [findings, setFindings] = useState([]);
  const [priorityFindings, setPriorityFindings] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [rules, setRules] = useState([]);
  const [reports, setReports] = useState(null);
  const [aiStatus, setAiStatus] = useState(null);
  const [datasetStatus, setDatasetStatus] = useState(null);
  const [datasetFlow, setDatasetFlow] = useState(null);
  const [datasetAnswer, setDatasetAnswer] = useState(null);
  const [datasetQuestion, setDatasetQuestion] = useState("Why is ORG-0029 high risk?");
  const [aiSummaries, setAiSummaries] = useState({});
  const [aiSummaryStatus, setAiSummaryStatus] = useState("");
  const [trace, setTrace] = useState(null);
  const [auditEvents, setAuditEvents] = useState([]);
  const [auditVerification, setAuditVerification] = useState(null);
  const [users, setUsers] = useState([]);
  const [usersError, setUsersError] = useState("");

  useEffect(() => {
    function handlePopState() {
      setPath(window.location.pathname);
    }
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    let active = true;
    async function loadAdminData() {
      setLoading(true);
      setError("");
      try {
        if (["admin", "reviewer"].includes(currentUser?.role)) {
          await runCompliance();
          await recalculatePriority();
          await scanConflicts();
        }
        const [
          adminSummary,
          modules,
          systemList,
          compliance,
          priorities,
          conflictList,
          knowledge,
          reportSummary,
          ai,
          dataStatus,
          dataFlow,
          auditList,
          auditVerify,
        ] = await Promise.all([
          getAdminSummary(),
          getModuleStatus(),
          getConnectedSystems(),
          getComplianceFindings(),
          getPriorityFindings(),
          getConflicts(),
          getKnowledgeRules(),
          getReportsSummary(),
          getAIStatus(),
          getDatasetStatus(),
          getDatasetDemoFlow("ORG-0029"),
          getAuditEvents(),
          verifyAudit(),
        ]);
        if (!active) return;
        const nextFindings = compliance.findings || [];
        setSummary(adminSummary.summary);
        setModuleStatus(modules.modules || []);
        setSystems(systemList.systems || []);
        setFindings(nextFindings);
        setPriorityFindings(priorities.priority_findings || []);
        setConflicts(conflictList.conflicts || []);
        setRules(knowledge.rules || []);
        setReports(reportSummary.summary);
        setAiStatus(ai);
        setDatasetStatus(dataStatus);
        setDatasetFlow(dataFlow);
        setAuditEvents(auditList.events || []);
        setAuditVerification(auditVerify);
        if (currentUser?.role === "admin") {
          try {
            const userList = await getUsers();
            if (active) setUsers(userList.users || []);
          } catch (userLoadError) {
            if (active) setUsersError(userLoadError.message);
          }
        }
        const firstDrift = nextFindings.find((item) => item.status === "drifted");
        if (firstDrift) {
          const cascade = await getCascadeForFinding(firstDrift.id);
          if (active) setTrace(cascade.trace);
        }
      } catch (loadError) {
        if (loadError.status === 401) {
          onUnauthorized?.();
          return;
        }
        if (active) setError(loadError.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadAdminData();
    return () => {
      active = false;
    };
  }, [currentUser?.role]);

  function navigate(nextPath) {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  }

  const activePage = path === "/admin/dashboard" ? "/admin" : path;
  const systemsById = useMemo(
    () => Object.fromEntries(systems.map((system) => [system.id, system])),
    [systems],
  );
  const rulesById = useMemo(
    () => Object.fromEntries(rules.map((rule) => [rule.id, rule])),
    [rules],
  );
  const driftedFindings = findings.filter((finding) => finding.status === "drifted");
  const compliantFindings = findings.filter((finding) => finding.status === "compliant");

  const cards = useMemo(
    () => [
      ["Verified Rules", summary?.verified_rules, "Officer-approved source of truth"],
      ["Connected Systems", summary?.connected_systems, "Portals, SOPs, FAQs, and forms checked"],
      ["Compliance Findings", summary?.compliance_findings, "Total system checks in this demo"],
      ["Drifted Systems", summary?.drifted_findings, "Systems still showing old policy"],
      ["Open Conflicts", summary?.open_conflicts, "Circular conflicts requiring officer action"],
    ],
    [summary],
  );

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <span>NG</span>
          <div>
            <p>Government Core</p>
            <h1>NiyamGuard Admin</h1>
          </div>
        </div>
        <nav aria-label="Admin pages">
          {pages.map((page) => (
            <button
              className={activePage === page.path ? "admin-nav-active" : ""}
              key={page.path}
              onClick={() => navigate(page.path)}
              type="button"
            >
              {page.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="admin-main">
        <header className="admin-header">
          <div>
            <p className="eyebrow">Verified policy operations</p>
            <h2>{pages.find((page) => page.path === activePage)?.label || "Dashboard"}</h2>
          </div>
          <div className="admin-header-actions">
            <div className="admin-user-chip" aria-label="Current user">
              <span>{currentUser?.email || "Signed in"}</span>
              <StatusPill tone="blue">{currentUser?.role || "user"}</StatusPill>
            </div>
            <a className="button button-secondary" href="/demo">
              Demo dashboard
            </a>
            <a className="button button-secondary" href="/">
              Citizen app
            </a>
            <button className="button button-secondary" onClick={onLogout} type="button">
              Logout
            </button>
          </div>
        </header>

        {error ? <div className="global-error" role="alert">{error}</div> : null}
        {reportStatus ? <p className="admin-action-status">{reportStatus}</p> : null}
        {loading ? <p className="admin-loading">Loading government-core demo data...</p> : null}

        {!loading && activePage === "/admin" ? (
          <DashboardPage
            cards={cards}
            conflicts={conflicts}
            findings={findings}
            moduleStatus={moduleStatus}
            onExport={async (type, format) => {
              setReportStatus(`Preparing ${titleCase(type)} ${format.toUpperCase()} export...`);
              try {
                const result = await downloadReport(type, format);
                setReportStatus(`Downloaded ${result.filename}.`);
              } catch (downloadError) {
                setReportStatus(downloadError.message);
              }
            }}
            priorityFindings={priorityFindings}
            reports={reports}
            rules={rules}
            aiStatus={aiStatus}
          />
        ) : null}

        {!loading && activePage === "/admin/compliance" ? (
          <CompliancePage
            compliantFindings={compliantFindings}
            driftedFindings={driftedFindings}
            findings={findings}
            rulesById={rulesById}
            systemsById={systemsById}
            aiSummaries={aiSummaries}
            aiSummaryStatus={aiSummaryStatus}
            aiStatus={aiStatus}
            onGenerateSummary={async (findingId) => {
              setAiSummaryStatus(`Generating AI summary for ${findingId}...`);
              try {
                const result = await generateAIFindingSummary(findingId);
                setAiSummaries((current) => ({ ...current, [findingId]: result }));
                setAiSummaryStatus("AI summary ready.");
              } catch (summaryError) {
                setAiSummaryStatus(summaryError.message);
              }
            }}
          />
        ) : null}

        {!loading && activePage === "/admin/cascade" ? (
          <CascadePage trace={trace} />
        ) : null}

        {!loading && activePage === "/admin/conflicts" ? (
          <ConflictPage conflicts={conflicts} rulesById={rulesById} />
        ) : null}

        {!loading && activePage === "/admin/knowledge-base" ? (
          <KnowledgePage moduleStatus={moduleStatus} rules={rules} />
        ) : null}

        {!loading && activePage === "/admin/regulatory-ai" ? (
          <RegulatoryAIPage
            answer={datasetAnswer}
            flow={datasetFlow}
            onAsk={async (question) => {
              setDatasetQuestion(question);
              const response = await askDatasetQA({ question });
              setDatasetAnswer(response);
            }}
            question={datasetQuestion}
            status={datasetStatus}
          />
        ) : null}

        {!loading && activePage === "/admin/reports" ? (
          <ReportsPage
            onExport={async (type, format) => {
              setReportStatus(`Preparing ${titleCase(type)} ${format.toUpperCase()} export...`);
              try {
                const result = await downloadReport(type, format);
                setReportStatus(`Downloaded ${result.filename}.`);
              } catch (downloadError) {
                setReportStatus(downloadError.message);
              }
            }}
            reports={reports}
          />
        ) : null}

        {!loading && activePage === "/admin/audit" ? (
          <AuditPage events={auditEvents} verification={auditVerification} />
        ) : null}

        {!loading && activePage === "/admin/users" && currentUser?.role !== "admin" ? (
          <UnauthorizedPage />
        ) : null}

        {!loading && activePage === "/admin/users" && currentUser?.role === "admin" ? (
          <UsersPage
            error={usersError}
            onCreateUser={async (payload) => {
              const response = await createUser(payload);
              setUsers((current) => [...current, response.user].sort((a, b) => a.email.localeCompare(b.email)));
            }}
            users={users}
          />
        ) : null}
      </main>
    </div>
  );
}

function DashboardPage({
  aiStatus,
  cards,
  conflicts,
  findings,
  moduleStatus,
  onExport,
  priorityFindings,
  reports,
  rules,
}) {
  const driftedCount = findings.filter((item) => item.status === "drifted").length;
  const compliantCount = findings.filter((item) => item.status === "compliant").length;

  return (
    <section className="admin-section" aria-label="Dashboard summary">
      <p className="admin-explainer">
        NiyamGuard compares verified circular rules against portals, forms, SOPs,
        and FAQs to detect policy drift before citizens are harmed.
      </p>
      <div className="admin-card-grid">
        {cards.map(([label, value, caption]) => (
          <article className="admin-stat-card" key={label}>
            <span>{label}</span>
            <strong>{numberOrZero(value)}</strong>
            <p>{caption}</p>
          </article>
        ))}
      </div>

      <div className="admin-insight-grid">
        <section className="admin-panel">
          <h3>Compliance Snapshot</h3>
          <p>
            {driftedCount} drifted systems and {compliantCount} compliant system
            found for the GO-138 income certificate demo.
          </p>
          <div className="admin-mini-metrics">
            <StatusPill tone="red">3 drifted</StatusPill>
            <StatusPill tone="green">1 compliant</StatusPill>
          </div>
        </section>

        <section className="admin-panel">
          <h3>High Priority Findings</h3>
          <ul className="admin-compact-list">
            {priorityFindings.slice(0, 3).map((priority) => (
              <li key={priority.id || priority.finding_id}>
                <strong>{priority.priority_level}</strong>
                <span>{priority.finding_id}</span>
                <em>{priority.score}</em>
              </li>
            ))}
          </ul>
        </section>

        <section className="admin-panel">
          <h3>Conflict Summary</h3>
          <p>
            Old GO-112 says 12 months. New GO-138 says 6 months. Recommended
            action: keep GO-138 active and supersede GO-112.
          </p>
          <StatusPill tone={conflicts.length ? "red" : "green"}>
            {conflicts.length} open conflict
          </StatusPill>
        </section>

        <section className="admin-panel">
          <h3>Knowledge Base Status</h3>
          <p>{rules.length} verified rules are available to admin and public APIs.</p>
          <div className="admin-module-grid">
            {moduleStatus.slice(0, 4).map((module) => (
              <div key={module.name}>
                <span>{module.name.replaceAll("_", " ")}</span>
                <StatusPill tone="green">{module.status}</StatusPill>
              </div>
            ))}
          </div>
        </section>

        <section className="admin-panel">
          <h3>Local AI Status</h3>
          <p>
            Ollama explains verified findings and RAG answers only from retrieved
            sources. Deterministic compliance remains separate.
          </p>
          <div className="admin-mini-metrics">
            <StatusPill tone={aiStatus?.status === "online" ? "green" : "red"}>
              {aiStatus?.status === "online" ? "Ollama AI" : "Fallback"}
            </StatusPill>
            <StatusPill tone="blue">{aiStatus?.model || "qwen2.5:7b-instruct"}</StatusPill>
            <StatusPill tone={aiStatus?.rag_enabled ? "green" : "red"}>
              RAG Knowledge Index
            </StatusPill>
          </div>
        </section>

        <section className="admin-panel admin-panel-wide">
          <h3>Report Export</h3>
          <p>
            Export official-ready CSV or JSON artifacts after the demo run.
            Current report summary includes {numberOrZero(reports?.compliance_findings)} compliance findings.
          </p>
          <div className="admin-report-actions">
            <button className="button button-primary" onClick={() => void onExport("compliance", "csv")} type="button">
              Export Compliance CSV
            </button>
            <button className="button button-secondary" onClick={() => void onExport("conflicts", "csv")} type="button">
              Export Conflicts CSV
            </button>
            <button className="button button-secondary" onClick={() => void onExport("rules", "json")} type="button">
              Export Rules JSON
            </button>
          </div>
        </section>
      </div>
    </section>
  );
}

function CompliancePage({
  aiSummaries,
  aiSummaryStatus,
  aiStatus,
  compliantFindings,
  driftedFindings,
  findings,
  onGenerateSummary,
  rulesById,
  systemsById,
}) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Compliance Findings</h3>
          <p>
            GO-138 expects Income Certificate validity to be 6 months. The demo
            checks each connected system against that verified rule.
          </p>
        </div>
        <div className="admin-mini-metrics">
          <StatusPill tone="red">{driftedFindings.length} drifted systems</StatusPill>
          <StatusPill tone="green">{compliantFindings.length} compliant system</StatusPill>
        </div>
      </div>
      {aiSummaryStatus ? <p className="admin-action-status">{aiSummaryStatus}</p> : null}

      <div className="admin-finding-grid">
        {findings.map((finding) => {
          const system = systemsById[finding.connected_system_id];
          const rule = rulesById[finding.verified_rule_id];
          const aiSummary = aiSummaries[finding.id];
          return (
            <article className={`admin-finding-card finding-${finding.status}`} key={finding.id}>
              <div className="admin-card-heading">
                <div>
                  <span>{titleCase(system?.system_type || "system")}</span>
                  <h3>{system?.name || titleCase(finding.connected_system_id)}</h3>
                </div>
                <StatusPill tone={finding.status === "drifted" ? "red" : "green"}>
                  {finding.status}
                </StatusPill>
              </div>
              <dl>
                <div>
                  <dt>Expected rule</dt>
                  <dd>{finding.expected_value}</dd>
                </div>
                <div>
                  <dt>Actual system value</dt>
                  <dd>{finding.actual_value || "Missing"}</dd>
                </div>
                <div>
                  <dt>Severity</dt>
                  <dd>{finding.severity}</dd>
                </div>
                <div>
                  <dt>Source circular</dt>
                  <dd>{sourceCircular(rule)}</dd>
                </div>
              </dl>
              <p><strong>Recommended fix:</strong> {finding.recommended_fix}</p>
              <p><strong>Citizen impact:</strong> {finding.citizen_impact_reason}</p>
              <div className="admin-ai-actions">
                <button
                  className="button button-secondary"
                  onClick={() => void onGenerateSummary(finding.id)}
                  type="button"
                >
                  Generate AI Summary
                </button>
                <div className="source-badges" aria-label="AI source badges">
                  <span>Verified Rule</span>
                  <span>{aiStatus?.status === "online" ? "Ollama AI" : "Fallback"}</span>
                </div>
              </div>
              {aiSummary ? (
                <section className="admin-ai-summary" aria-label="AI impact summary">
                  <h4>AI Impact Summary</h4>
                  <p>{aiSummary.summary}</p>
                  <p><strong>Citizen:</strong> {aiSummary.citizen_friendly_explanation}</p>
                  <p><strong>Officer:</strong> {aiSummary.officer_friendly_explanation}</p>
                  <div className="source-badges">
                    <span>{aiSummary.provider === "ollama" ? "Ollama AI" : "Fallback"}</span>
                    <span>Verified Rule</span>
                    <span>{aiSummary.source?.circular || "Source available"}</span>
                  </div>
                </section>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function CascadePage({ trace }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Cascade Trace</h3>
          <p>
            This shows how one stale portal rule can flow into officer behavior,
            citizen action, and wrong approval or rejection risk.
          </p>
        </div>
      </div>
      <section className="admin-panel">
        {trace ? (
          <>
            <p>{trace.impact_summary}</p>
            <ol className="admin-trace">
              {trace.nodes_json.map((node) => (
                <li key={node.id}>{node.label}</li>
              ))}
            </ol>
          </>
        ) : (
          <p>No drifted finding is available for cascade tracing.</p>
        )}
      </section>
    </section>
  );
}

function ConflictPage({ conflicts, rulesById }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Conflict Detection</h3>
          <p>
            The seed conflict demonstrates old GO-112 saying 12 months while new
            GO-138 says 6 months.
          </p>
        </div>
      </div>
      <div className="admin-finding-grid">
        {conflicts.map((conflict) => (
          <article className="admin-finding-card finding-drifted" key={conflict.id}>
            <div className="admin-card-heading">
              <div>
                <span>{conflict.conflict_type || "active value conflict"}</span>
                <h3>{titleCase(conflict.service_id)} / {conflict.rule_key}</h3>
              </div>
              <StatusPill tone="red">{conflict.severity}</StatusPill>
            </div>
            <dl>
              <div>
                <dt>Affected service</dt>
                <dd>{conflict.service_id}</dd>
              </div>
              <div>
                <dt>Rule key</dt>
                <dd>{conflict.rule_key}</dd>
              </div>
              <div>
                <dt>Rule A</dt>
                <dd>{ruleValue(rulesById[conflict.rule_a_id])}</dd>
              </div>
              <div>
                <dt>Rule B</dt>
                <dd>{ruleValue(rulesById[conflict.rule_b_id])}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{conflict.status}</dd>
              </div>
            </dl>
            <p><strong>Recommendation:</strong> keep GO-138 active and supersede GO-112.</p>
            <p>{conflict.recommendation || conflict.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function KnowledgePage({ moduleStatus, rules }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Knowledge Base Status</h3>
          <p>Officer-approved circular rules available to public and internal APIs.</p>
        </div>
      </div>
      <div className="admin-card-grid">
        {rules.map((rule) => (
          <article className="admin-stat-card admin-rule-card" key={rule.id}>
            <span>{sourceCircular(rule)}</span>
            <strong>{rule.current_value} {rule.unit}</strong>
            <p>{rule.rule_name}</p>
            <p>{rule.source_clause}</p>
          </article>
        ))}
      </div>
      <section className="admin-panel">
        <h3>Ready Modules</h3>
        <div className="admin-module-grid">
          {moduleStatus.map((module) => (
            <div key={module.name}>
              <span>{module.name.replaceAll("_", " ")}</span>
              <StatusPill tone="green">{module.status}</StatusPill>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}

function recordPayload(record) {
  return record?.payload || {};
}

function RegulatoryAIPage({ answer, flow, onAsk, question, status }) {
  const [draft, setDraft] = useState(question);
  const collections = status?.collections || {};
  const summaryCards = [
    ["Regulatory circulars", collections.regulatory_circulars || 0],
    ["Internal policies", collections.internal_policies || 0],
    ["Obligations", collections.obligations || 0],
    ["Compliance gaps", collections.gap_findings || 0],
    ["Drift alerts", collections.regulatory_drift_cases || 0],
    ["Risk scores", collections.risk_scoring_labels || 0],
    ["Audit logs", collections.dataset_audit_events || 0],
  ];
  const regulation = recordPayload(flow?.regulation);
  const obligation = recordPayload(flow?.obligation);
  const policy = recordPayload(flow?.internal_policy);
  const gap = recordPayload(flow?.gap);
  const drift = recordPayload(flow?.drift);
  const risk = recordPayload(flow?.risk);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!draft.trim()) return;
    await onAsk(draft.trim());
  }

  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Regulatory AI Dataset Explorer</h3>
          <p>
            These cards are backed by the synthetic dataset pack: circulars,
            policies, obligations, evidence, gaps, drift, risk labels, and audit events.
          </p>
        </div>
        <StatusPill tone={status?.loaded_records ? "green" : "red"}>
          {status?.loaded_records || 0} records
        </StatusPill>
      </div>

      <div className="admin-card-grid">
        {summaryCards.map(([label, value]) => (
          <article className="admin-stat-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
            <p>Loaded from {status?.pack_version || "dataset pack"}.</p>
          </article>
        ))}
      </div>

      <section className="admin-panel">
        <h3>AI Q&A</h3>
        <form className="dataset-qa-form" onSubmit={handleSubmit}>
          <label htmlFor="dataset-question">
            Ask from dataset
            <input
              id="dataset-question"
              onChange={(event) => setDraft(event.target.value)}
              value={draft}
            />
          </label>
          <button className="button button-primary" type="submit">Ask Dataset</button>
        </form>
        {answer ? (
          <div className="dataset-answer">
            <p>{answer.answer}</p>
            <div className="source-badges">
              <span>{answer.provider || "dataset"}</span>
              <span>{answer.fallback ? "Fallback" : "Dataset Source"}</span>
            </div>
            <ul className="admin-compact-list">
              {(answer.references || []).slice(0, 3).map((reference) => (
                <li key={reference.chunk_id}>
                  <strong>{reference.source?.type || "source"}</strong>
                  <span>{reference.title || reference.service_id}</span>
                  <em>{Math.round((reference.score || 0) * 100)}%</em>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>

      <div className="admin-finding-grid">
        <DatasetRecordCard
          eyebrow="Regulatory circular"
          title={regulation.title}
          rows={[
            ["Circular", regulation.circular_id],
            ["Regulator", regulation.regulator_code],
            ["Sector", regulation.sector],
            ["Effective", regulation.effective_date],
            ["Severity", regulation.severity],
          ]}
          text={regulation.summary}
        />
        <DatasetRecordCard
          eyebrow="Extracted obligation"
          title={obligation.obligation_id}
          rows={[
            ["Actor", obligation.accountable_actor],
            ["Action", obligation.action_required],
            ["Frequency", obligation.frequency],
            ["Evidence", obligation.evidence_required],
            ["Risk", obligation.penalty_risk],
          ]}
          text={obligation.obligation_text}
        />
        <DatasetRecordCard
          eyebrow="Internal policy"
          title={policy.policy_title}
          rows={[
            ["Policy", policy.policy_id],
            ["Org", policy.org_id],
            ["Department", policy.department],
            ["Owner", policy.owner_role],
            ["Status", policy.status],
          ]}
          text={policy.policy_text}
        />
        <DatasetRecordCard
          eyebrow="Policy gap"
          title={gap.finding_id}
          rows={[
            ["Severity", gap.severity],
            ["Type", gap.finding_type],
            ["Owner", gap.owner_team],
            ["Status", gap.status],
            ["Target", gap.target_date],
          ]}
          text={gap.recommended_fix || gap.finding_summary}
        />
        <DatasetRecordCard
          eyebrow="Drift alert"
          title={drift.drift_id}
          rows={[
            ["Type", drift.drift_type],
            ["Old", drift.old_requirement],
            ["New", drift.new_requirement],
            ["Score", drift.drift_score],
            ["Label", drift.ground_truth_label],
          ]}
          text={drift.recommended_action}
        />
        <DatasetRecordCard
          eyebrow="Risk score"
          title={risk.org_id}
          rows={[
            ["Band", risk.risk_band],
            ["Score", risk.risk_score],
            ["Open findings", risk.open_findings_count],
            ["Weak evidence", risk.bad_evidence_count],
            ["Source", risk.label_source],
          ]}
          text={flow?.risk_explanation}
        />
      </div>

      <div className="admin-insight-grid">
        <section className="admin-panel">
          <h3>Evidence Review</h3>
          <ul className="admin-compact-list">
            {(flow?.evidence || []).slice(0, 3).map((record) => {
              const payload = recordPayload(record);
              return (
                <li key={payload.evidence_id}>
                  <strong>{payload.status}</strong>
                  <span>{payload.evidence_title}</span>
                  <em>{payload.evidence_score}</em>
                </li>
              );
            })}
          </ul>
        </section>
        <section className="admin-panel">
          <h3>Audit Trail</h3>
          <ul className="admin-compact-list">
            {(flow?.audit_trail || []).slice(0, 5).map((record) => {
              const payload = recordPayload(record);
              return (
                <li key={payload.audit_id}>
                  <strong>{payload.event_type}</strong>
                  <span>{payload.entity_type} {payload.entity_id}</span>
                  <em>{payload.success}</em>
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </section>
  );
}

function DatasetRecordCard({ eyebrow, title, rows, text }) {
  return (
    <article className="admin-finding-card">
      <div className="admin-card-heading">
        <div>
          <span>{eyebrow}</span>
          <h3>{title || "Not found in available dataset"}</h3>
        </div>
      </div>
      <dl>
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value || "Not found"}</dd>
          </div>
        ))}
      </dl>
      <p>{text || "Not found in available dataset."}</p>
    </article>
  );
}

function ReportsPage({ reports, onExport }) {
  const reportCards = [
    {
      title: "Export Compliance CSV",
      type: "compliance",
      format: "csv",
      description: "A row-by-row record of expected rule, actual system value, severity, fix, and citizen impact.",
      metric: `${numberOrZero(reports?.compliance_findings)} findings`,
      tone: "primary",
    },
    {
      title: "Export Conflicts CSV",
      type: "conflicts",
      format: "csv",
      description: "Circular conflicts that need officer resolution before policy reaches citizens.",
      metric: `${numberOrZero(reports?.conflicts)} conflicts`,
      tone: "secondary",
    },
    {
      title: "Export Rules JSON",
      type: "rules",
      format: "json",
      description: "Machine-readable verified rules for downstream systems and public API integrations.",
      metric: `${numberOrZero(reports?.verified_rules)} rules`,
      tone: "secondary",
    },
  ];

  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Reports</h3>
          <p>
            Export clean artifacts for officials after the compliance and
            conflict checks finish.
          </p>
        </div>
      </div>
      <div className="admin-report-grid">
        {reportCards.map((report) => (
          <article className="admin-finding-card" key={report.title}>
            <div className="admin-card-heading">
              <div>
                <span>{report.metric}</span>
                <h3>{report.title}</h3>
              </div>
            </div>
            <p>{report.description}</p>
            <button
              className={`button ${report.tone === "primary" ? "button-primary" : "button-secondary"}`}
              onClick={() => void onExport(report.type, report.format)}
              type="button"
            >
              {report.title}
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

function AuditPage({ events, verification }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Audit Log</h3>
          <p>Important government-core actions are recorded with actor, request, and hash-chain metadata.</p>
        </div>
        <StatusPill tone={verification?.valid ? "green" : "red"}>
          {verification?.valid ? "Hash chain verified" : "Verification warning"}
        </StatusPill>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Action</th>
              <th>Actor</th>
              <th>Entity</th>
              <th>Request</th>
            </tr>
          </thead>
          <tbody>
            {events.length ? (
              events.map((event) => (
                <tr key={event.id}>
                  <td>{event.created_at}</td>
                  <td>{titleCase(event.action)}</td>
                  <td>{event.actor_email || "system"}</td>
                  <td>{event.entity_type || "-"} {event.entity_id || ""}</td>
                  <td>{event.request_id || "-"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">No audit events yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function UsersPage({ error, users, onCreateUser }) {
  const [form, setForm] = useState({
    email: "",
    password: "User@12345",
    role: "viewer",
    is_active: true,
  });
  const [status, setStatus] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("Creating user...");
    try {
      await onCreateUser(form);
      setForm({
        email: "",
        password: "User@12345",
        role: "viewer",
        is_active: true,
      });
      setStatus("User created.");
    } catch (createError) {
      setStatus(createError.message);
    }
  }

  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>User Management</h3>
          <p>Admin users can create officer, reviewer, viewer, and citizen accounts.</p>
        </div>
      </div>
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <form className="admin-user-form" onSubmit={handleSubmit}>
        <label htmlFor="new-user-email">
          Email
          <input
            id="new-user-email"
            onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
            required
            type="email"
            value={form.email}
          />
        </label>
        <label htmlFor="new-user-password">
          Password
          <input
            id="new-user-password"
            minLength="8"
            onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
            required
            type="password"
            value={form.password}
          />
        </label>
        <label htmlFor="new-user-role">
          Role
          <select
            id="new-user-role"
            onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}
            value={form.role}
          >
            <option value="admin">admin</option>
            <option value="reviewer">reviewer</option>
            <option value="viewer">viewer</option>
            <option value="citizen">citizen</option>
          </select>
        </label>
        <button className="button button-primary" type="submit">Create User</button>
      </form>
      {status ? <p className="admin-action-status">{status}</p> : null}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.email}</td>
                <td>{user.role}</td>
                <td>{user.is_active ? "active" : "disabled"}</td>
                <td>{user.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function UnauthorizedPage() {
  return (
    <section className="admin-section">
      <div className="admin-panel">
        <h3>403 - You do not have permission</h3>
        <p>This page requires the admin role.</p>
      </div>
    </section>
  );
}
