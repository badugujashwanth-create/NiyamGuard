import { useEffect, useMemo, useState } from "react";

import {
  askDatasetQA,
  createUser,
  applyMockDemoPatch,
  applyPropagationDemoPatch,
  approveRuleCandidate,
  downloadReport,
  extractCircularRules,
  generateAIFindingSummary,
  getAIStatus,
  getAdminReadiness,
  getAdminSummary,
  getAdminPortalCertificates,
  getAdminPortalForms,
  getAdminPortalServices,
  getAuditEvents,
  getCascadeForFinding,
  getCircularDocuments,
  getComplianceRuns,
  getComplianceFindings,
  getConnectedSystems,
  getDatasetDemoFlow,
  getDatasetStatus,
  getConflicts,
  getKnowledgeUpdateEvents,
  getKnowledgeRules,
  getMockSystems,
  getModuleStatus,
  getPolicyRuleVersions,
  getPolicyUpdateHistory,
  getPriorityFindings,
  getPropagationTasks,
  getReportsSummary,
  getRuleCandidates,
  getSchedulerStatus,
  getSources,
  getUsers,
  publishRuleCandidate,
  recalculatePriority,
  reindexKnowledge,
  resetMockSystems,
  rerunComplianceForRule,
  runCompliance,
  runSchedulerNow,
  runSelfUpdateScenario,
  runVirtualGovScenario,
  scanConflicts,
  syncCirculars,
  syncSource,
  verifyAudit,
} from "../services/api";

const pages = [
  { path: "/admin", label: "Dashboard" },
  { path: "/admin/compliance", label: "Compliance" },
  { path: "/admin/cascade", label: "Cascade" },
  { path: "/admin/conflicts", label: "Conflicts" },
  { path: "/admin/scale-view", label: "Scale View" },
  { path: "/admin/impact", label: "Impact" },
  { path: "/admin/knowledge-base", label: "Knowledge Base" },
  { path: "/admin/sources", label: "Sources" },
  { path: "/admin/circulars", label: "Circulars" },
  { path: "/admin/rule-candidates", label: "Rule Candidates" },
  { path: "/admin/policy-updates", label: "Policy Updates" },
  { path: "/admin/propagation", label: "Propagation" },
  { path: "/admin/scheduler", label: "Scheduler" },
  { path: "/admin/regulatory-ai", label: "Regulatory AI" },
  { path: "/admin/readiness", label: "Readiness" },
  { path: "/admin/services", label: "Services" },
  { path: "/admin/forms", label: "Forms" },
  { path: "/admin/certificates", label: "Certificates" },
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

async function loadSelfUpdateData() {
  const [
    sourceList,
    circularList,
    candidateList,
    updateHistory,
    versionList,
    knowledgeEvents,
    propagationTaskList,
    scheduler,
    complianceRunList,
    mockSystemList,
  ] = await Promise.all([
    getSources(),
    getCircularDocuments(),
    getRuleCandidates(),
    getPolicyUpdateHistory(),
    getPolicyRuleVersions(),
    getKnowledgeUpdateEvents(),
    getPropagationTasks(),
    getSchedulerStatus(),
    getComplianceRuns(),
    getMockSystems(),
  ]);
  return {
    sourceList,
    circularList,
    candidateList,
    updateHistory,
    versionList,
    knowledgeEvents,
    propagationTaskList,
    scheduler,
    complianceRunList,
    mockSystemList,
  };
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
  const [sources, setSources] = useState([]);
  const [circularDocuments, setCircularDocuments] = useState([]);
  const [ruleCandidates, setRuleCandidates] = useState([]);
  const [policyHistory, setPolicyHistory] = useState([]);
  const [ruleVersions, setRuleVersions] = useState([]);
  const [knowledgeEvents, setKnowledgeEvents] = useState([]);
  const [propagationTasks, setPropagationTasks] = useState([]);
  const [schedulerStatus, setSchedulerStatus] = useState(null);
  const [complianceRuns, setComplianceRuns] = useState([]);
  const [mockSystems, setMockSystems] = useState({});
  const [portalServices, setPortalServices] = useState([]);
  const [portalForms, setPortalForms] = useState([]);
  const [portalCertificates, setPortalCertificates] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [virtualGovResult, setVirtualGovResult] = useState(null);

  function applySelfUpdateData(data) {
    setSources(data.sourceList.sources || []);
    setCircularDocuments(data.circularList.circulars || []);
    setRuleCandidates(data.candidateList.candidates || []);
    setPolicyHistory(data.updateHistory.events || []);
    setRuleVersions(data.versionList.versions || []);
    setKnowledgeEvents(data.knowledgeEvents.events || []);
    setPropagationTasks(data.propagationTaskList.tasks || []);
    setSchedulerStatus(data.scheduler.scheduler || null);
    setComplianceRuns(data.complianceRunList.runs || []);
    setMockSystems(data.mockSystemList.systems || {});
  }

  async function refreshSelfUpdateData() {
    applySelfUpdateData(await loadSelfUpdateData());
  }

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
          selfUpdateData,
          adminPortalServices,
          adminPortalForms,
          adminPortalCertificates,
          readinessReport,
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
          loadSelfUpdateData(),
          getAdminPortalServices(),
          getAdminPortalForms(),
          getAdminPortalCertificates(),
          getAdminReadiness(),
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
        applySelfUpdateData(selfUpdateData);
        setPortalServices(adminPortalServices.services || []);
        setPortalForms(adminPortalForms.forms || []);
        setPortalCertificates(adminPortalCertificates.certificates || []);
        setReadiness(readinessReport);
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

        {!loading && activePage === "/admin/scale-view" ? (
          <ScaleViewPage findings={findings} systems={systems} />
        ) : null}

        {!loading && activePage === "/admin/impact" ? (
          <ImpactPage findings={findings} priorityFindings={priorityFindings} rulesById={rulesById} systemsById={systemsById} />
        ) : null}

        {!loading && activePage === "/admin/knowledge-base" ? (
          <KnowledgePage moduleStatus={moduleStatus} rules={rules} />
        ) : null}

        {!loading && activePage === "/admin/sources" ? (
          <SourcesPage
            onRefresh={refreshSelfUpdateData}
            onRunScheduler={async () => {
              setReportStatus("Running circular scheduler...");
              await runSchedulerNow();
              await refreshSelfUpdateData();
              setReportStatus("Circular scheduler completed.");
            }}
            onSyncSource={async (sourceId) => {
              setReportStatus(`Syncing ${sourceId}...`);
              await syncSource(sourceId);
              await refreshSelfUpdateData();
              setReportStatus("Source sync completed.");
            }}
            schedulerStatus={schedulerStatus}
            sources={sources}
          />
        ) : null}

        {!loading && activePage === "/admin/circulars" ? (
          <CircularsPage
            circulars={circularDocuments}
            onExtract={async (circularId) => {
              setReportStatus(`Extracting rules from ${circularId}...`);
              await extractCircularRules(circularId);
              await refreshSelfUpdateData();
              setReportStatus("Rule extraction completed.");
            }}
            onSyncAll={async () => {
              setReportStatus("Syncing circular sources...");
              await syncCirculars();
              await refreshSelfUpdateData();
              setReportStatus("Circular sync completed.");
            }}
          />
        ) : null}

        {!loading && activePage === "/admin/rule-candidates" ? (
          <RuleCandidatesPage
            candidates={ruleCandidates}
            onApprove={async (candidateId) => {
              setReportStatus(`Approving ${candidateId}...`);
              await approveRuleCandidate(candidateId, "Approved from admin console.");
              await refreshSelfUpdateData();
              setReportStatus("Candidate approved.");
            }}
            onPublish={async (candidateId) => {
              setReportStatus(`Publishing ${candidateId}...`);
              await publishRuleCandidate(candidateId, "Published from admin console.");
              await refreshSelfUpdateData();
              setReportStatus("Policy update published.");
            }}
          />
        ) : null}

        {!loading && activePage === "/admin/policy-updates" ? (
          <PolicyUpdatesPage
            complianceRuns={complianceRuns}
            events={policyHistory}
            knowledgeEvents={knowledgeEvents}
            onReindex={async () => {
              setReportStatus("Reindexing verified policy knowledge...");
              await reindexKnowledge();
              await refreshSelfUpdateData();
              setReportStatus("Knowledge update completed.");
            }}
            onRerunCompliance={async () => {
              setReportStatus("Rerunning compliance for rule_001...");
              await rerunComplianceForRule("rule_001");
              await refreshSelfUpdateData();
              setReportStatus("Compliance rerun completed.");
            }}
            versions={ruleVersions}
          />
        ) : null}

        {!loading && activePage === "/admin/propagation" ? (
          <PropagationPage
            mockSystems={mockSystems}
            onApplyMockPatch={async () => {
              setReportStatus("Applying demo patch to mock connected systems...");
              await applyMockDemoPatch();
              await refreshSelfUpdateData();
              setReportStatus("Mock systems patched.");
            }}
            onApplyTaskPatch={async (taskId) => {
              setReportStatus(`Applying propagation patch ${taskId}...`);
              await applyPropagationDemoPatch(taskId);
              await refreshSelfUpdateData();
              setReportStatus("Propagation patch applied.");
            }}
            onResetMocks={async () => {
              setReportStatus("Resetting mock connected systems...");
              await resetMockSystems();
              await refreshSelfUpdateData();
              setReportStatus("Mock systems reset to outdated values.");
            }}
            tasks={propagationTasks}
          />
        ) : null}

        {!loading && activePage === "/admin/scheduler" ? (
          <SchedulerPage
            onRunScenario={async (applyDemoPatch) => {
              setReportStatus(applyDemoPatch ? "Running full self-update and patch scenario..." : "Running self-update scenario...");
              await runSelfUpdateScenario({ applyDemoPatch, resetMockSystems: applyDemoPatch });
              await refreshSelfUpdateData();
              setReportStatus(applyDemoPatch ? "Full self-update demo completed." : "Self-update workflow completed.");
            }}
            onRunScheduler={async () => {
              setReportStatus("Running scheduler now...");
              await runSchedulerNow();
              await refreshSelfUpdateData();
              setReportStatus("Scheduler run completed.");
            }}
            scheduler={schedulerStatus}
          />
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

        {!loading && activePage === "/admin/readiness" ? (
          <ReadinessPage
            onRunVirtualGov={async () => {
              setReportStatus("Running virtual government sandbox scenario...");
              const response = await runVirtualGovScenario({
                scenarioId: "income_certificate_full_flow",
                resetBeforeRun: true,
              });
              setVirtualGovResult(response);
              const nextReadiness = await getAdminReadiness();
              setReadiness(nextReadiness);
              setReportStatus("Virtual government sandbox completed.");
            }}
            readiness={readiness}
            virtualGovResult={virtualGovResult}
          />
        ) : null}

        {!loading && activePage === "/admin/services" ? (
          <AdminServicesPage services={portalServices} />
        ) : null}

        {!loading && activePage === "/admin/forms" ? (
          <AdminFormsPage forms={portalForms} />
        ) : null}

        {!loading && activePage === "/admin/certificates" ? (
          <AdminCertificatesPage certificates={portalCertificates} />
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

function ScaleViewPage({ findings, systems }) {
  const systemsByDepartment = systems.reduce((acc, system) => {
    const key = system.department || "Unknown";
    acc[key] = acc[key] || [];
    acc[key].push(system);
    return acc;
  }, {});
  const findingsBySystem = findings.reduce((acc, finding) => {
    acc[finding.connected_system_id] = acc[finding.connected_system_id] || [];
    acc[finding.connected_system_id].push(finding);
    return acc;
  }, {});
  const outdated = findings.filter((item) => item.status === "drifted");

  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Multi-District / Department Scale View</h3>
          <p>Demo operational data for MVP. Shows which departments, systems, and public surfaces are lagging after GO-138.</p>
        </div>
        <div className="admin-mini-metrics">
          <StatusPill tone="red">{outdated.length} outdated surfaces</StatusPill>
          <StatusPill tone="blue">{systems.length} connected systems</StatusPill>
        </div>
      </div>
      <div className="admin-insight-grid">
        {Object.entries(systemsByDepartment).map(([department, departmentSystems]) => {
          const drifted = departmentSystems.filter((system) =>
            (findingsBySystem[system.id] || []).some((finding) => finding.status === "drifted"),
          );
          return (
            <section className="admin-panel" key={department}>
              <h3>{department}</h3>
              <p>{drifted.length} of {departmentSystems.length} connected systems need updates.</p>
              <ul className="admin-compact-list">
                {departmentSystems.map((system) => {
                  const systemFinding = (findingsBySystem[system.id] || [])[0];
                  return (
                    <li key={system.id}>
                      <strong>{system.system_type}</strong>
                      <span>{system.name}</span>
                      <em>{systemFinding?.status || "unchecked"}</em>
                    </li>
                  );
                })}
              </ul>
            </section>
          );
        })}
      </div>
    </section>
  );
}

function ImpactPage({ findings, priorityFindings, rulesById, systemsById }) {
  const priorityByFinding = Object.fromEntries(priorityFindings.map((item) => [item.finding_id, item]));
  const highImpact = findings
    .filter((finding) => finding.status !== "compliant")
    .sort((a, b) => (priorityByFinding[b.id]?.score || 0) - (priorityByFinding[a.id]?.score || 0));

  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Citizen Impact Dashboard</h3>
          <p>Prioritizes circular drift by citizen impact, service urgency, and live application risk.</p>
        </div>
        <StatusPill tone={highImpact.length ? "red" : "green"}>{highImpact.length} high-impact items</StatusPill>
      </div>
      <div className="admin-finding-grid">
        {highImpact.map((finding) => {
          const priority = priorityByFinding[finding.id] || {};
          const system = systemsById[finding.connected_system_id];
          const rule = rulesById[finding.verified_rule_id];
          return (
            <article className="admin-finding-card finding-drifted" key={finding.id}>
              <div className="admin-card-heading">
                <div>
                  <span>{system?.system_type || "system"}</span>
                  <h3>{system?.name || finding.connected_system_id}</h3>
                </div>
                <StatusPill tone="red">{priority.priority_level || finding.severity}</StatusPill>
              </div>
              <dl>
                <div><dt>Expected</dt><dd>{finding.expected_value}</dd></div>
                <div><dt>Actual</dt><dd>{finding.actual_value || "Missing"}</dd></div>
                <div><dt>Score</dt><dd>{priority.score || "Not scored"}</dd></div>
                <div><dt>Source</dt><dd>{sourceCircular(rule)}</dd></div>
              </dl>
              <p><strong>Reason:</strong> {priority.reason || finding.citizen_impact_reason}</p>
              <p><strong>Required action:</strong> {finding.recommended_fix}</p>
            </article>
          );
        })}
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

function SourcesPage({ onRefresh, onRunScheduler, onSyncSource, schedulerStatus, sources }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Official Circular Sources</h3>
          <p>Configured source registry for regulatory circular sync and manual upload workflows.</p>
        </div>
        <div className="admin-mini-metrics">
          <StatusPill tone={schedulerStatus?.enabled ? "green" : "neutral"}>
            {schedulerStatus?.enabled ? "Auto sync enabled" : "Manual sync"}
          </StatusPill>
          <button className="button button-secondary" onClick={() => void onRefresh()} type="button">
            Refresh
          </button>
          <button className="button button-primary" onClick={() => void onRunScheduler()} type="button">
            Run Scheduler
          </button>
        </div>
      </div>
      <div className="admin-finding-grid">
        {sources.map((source) => (
          <article className="admin-finding-card" key={source.id}>
            <div className="admin-card-heading">
              <div>
                <span>{source.department}</span>
                <h3>{source.name}</h3>
              </div>
              <StatusPill tone={source.enabled ? "green" : "red"}>{source.source_type}</StatusPill>
            </div>
            <dl>
              <div><dt>Source ID</dt><dd>{source.id}</dd></div>
              <div><dt>URL</dt><dd>{source.url || "Manual upload"}</dd></div>
              <div><dt>Last checked</dt><dd>{source.last_checked_at || "Not checked"}</dd></div>
              <div><dt>Last success</dt><dd>{source.last_success_at || "Not synced"}</dd></div>
            </dl>
            <button className="button button-primary" onClick={() => void onSyncSource(source.id)} type="button">
              Sync Source
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}

function CircularsPage({ circulars, onExtract, onSyncAll }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Circular Intake</h3>
          <p>New regulatory documents are ingested, deduplicated, and prepared for rule extraction.</p>
        </div>
        <button className="button button-primary" onClick={() => void onSyncAll()} type="button">
          Sync Circulars
        </button>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Circular</th>
              <th>Title</th>
              <th>Department</th>
              <th>Effective</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {circulars.length ? circulars.map((circular) => (
              <tr key={circular.id}>
                <td>{circular.circular_number}</td>
                <td>{circular.title}</td>
                <td>{circular.department}</td>
                <td>{circular.effective_date}</td>
                <td>{circular.status}</td>
                <td>
                  <button className="button button-secondary" onClick={() => void onExtract(circular.id)} type="button">
                    Extract Rules
                  </button>
                </td>
              </tr>
            )) : (
              <tr><td colSpan="6">No circular documents synced yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function RuleCandidatesPage({ candidates, onApprove, onPublish }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Extracted Rule Candidates</h3>
          <p>Officer review queue for AI/deterministic policy-rule extraction before publication.</p>
        </div>
        <StatusPill tone={candidates.length ? "blue" : "neutral"}>{candidates.length} candidates</StatusPill>
      </div>
      <div className="admin-finding-grid">
        {candidates.length ? candidates.map((candidate) => (
          <article className="admin-finding-card" key={candidate.id}>
            <div className="admin-card-heading">
              <div>
                <span>{candidate.service_id}</span>
                <h3>{titleCase(candidate.rule_key)}</h3>
              </div>
              <StatusPill tone={candidate.status === "approved" ? "green" : "blue"}>{candidate.status}</StatusPill>
            </div>
            <dl>
              <div><dt>Old value</dt><dd>{candidate.old_value || "New rule"}</dd></div>
              <div><dt>New value</dt><dd>{candidate.new_value} {candidate.unit}</dd></div>
              <div><dt>Effective</dt><dd>{candidate.effective_date}</dd></div>
              <div><dt>Confidence</dt><dd>{Math.round(candidate.confidence_score * 100)}%</dd></div>
              <div><dt>Delta</dt><dd>{candidate.delta?.change_type || "Not calculated"}</dd></div>
              <div><dt>Impact</dt><dd>{candidate.delta?.impact_level || "Not calculated"}</dd></div>
            </dl>
            <p>{candidate.source_excerpt}</p>
            <div className="admin-report-actions">
              <button className="button button-secondary" onClick={() => void onApprove(candidate.id)} type="button">
                Approve
              </button>
              <button className="button button-primary" onClick={() => void onPublish(candidate.id)} type="button">
                Publish
              </button>
            </div>
          </article>
        )) : (
          <section className="admin-panel"><p>No rule candidates yet. Sync and extract circulars first.</p></section>
        )}
      </div>
    </section>
  );
}

function PolicyUpdatesPage({ complianceRuns, events, knowledgeEvents, onReindex, onRerunCompliance, versions }) {
  const currentVersions = versions.filter((version) => version.is_current);
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Published Policy Updates</h3>
          <p>Version history, knowledge-base refreshes, and compliance reruns triggered by policy changes.</p>
        </div>
        <div className="admin-mini-metrics">
          <button className="button button-secondary" onClick={() => void onReindex()} type="button">
            Reindex Knowledge
          </button>
          <button className="button button-primary" onClick={() => void onRerunCompliance()} type="button">
            Rerun Compliance
          </button>
        </div>
      </div>
      <div className="admin-card-grid">
        <article className="admin-stat-card"><span>Versions</span><strong>{versions.length}</strong><p>Immutable policy-rule version records.</p></article>
        <article className="admin-stat-card"><span>Publications</span><strong>{events.length}</strong><p>Approved rule updates published to the source of truth.</p></article>
        <article className="admin-stat-card"><span>Compliance Runs</span><strong>{complianceRuns.length}</strong><p>Verification jobs after updates or patches.</p></article>
      </div>
      <div className="admin-insight-grid">
        <section className="admin-panel">
          <h3>Current Rule Versions</h3>
          <ul className="admin-compact-list">
            {currentVersions.map((version) => (
              <li key={version.id}>
                <strong>{version.source_circular_number}</strong>
                <span>{titleCase(version.service_id)} / {version.rule_key}: {version.value} {version.unit}</span>
                <em>v{version.version_number}</em>
              </li>
            ))}
          </ul>
        </section>
        <section className="admin-panel">
          <h3>Knowledge Updates</h3>
          <ul className="admin-compact-list">
            {knowledgeEvents.length ? knowledgeEvents.slice(-5).map((event) => (
              <li key={event.id}>
                <strong>{event.status}</strong>
                <span>{event.update_type}</span>
                <em>{event.rule_key}</em>
              </li>
            )) : <li><span>No knowledge update events yet.</span></li>}
          </ul>
        </section>
      </div>
    </section>
  );
}

function PropagationPage({ mockSystems, onApplyMockPatch, onApplyTaskPatch, onResetMocks, tasks }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Propagation Tasks</h3>
          <p>Downstream portal, form, FAQ, and SOP update tasks created after a verified policy publication.</p>
        </div>
        <div className="admin-mini-metrics">
          <a className="button button-secondary" href="/mock/meeseva">Open Mock MeeSeva</a>
          <a className="button button-secondary" href="/mock/public-faq">Open Mock FAQ</a>
          <button className="button button-secondary" onClick={() => void onResetMocks()} type="button">Reset Mocks</button>
          <button className="button button-primary" onClick={() => void onApplyMockPatch()} type="button">Patch Mocks</button>
        </div>
      </div>
      <div className="admin-insight-grid">
        {Object.values(mockSystems).map((system) => (
          <section className="admin-panel" key={system.id}>
            <h3>{system.system_name}</h3>
            <p>{system.displayed_value || system.faq_value || "No displayed value"} expected {system.expected_value}.</p>
            <StatusPill tone={system.sync_status === "updated" ? "green" : "red"}>{system.sync_status}</StatusPill>
          </section>
        ))}
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Task</th>
              <th>System</th>
              <th>Type</th>
              <th>Old</th>
              <th>New</th>
              <th>Status</th>
              <th>Patch</th>
            </tr>
          </thead>
          <tbody>
            {tasks.length ? tasks.map((task) => (
              <tr key={task.id}>
                <td>{task.id}</td>
                <td>{task.connected_system_id}</td>
                <td>{task.task_type}</td>
                <td>{task.old_value || "-"}</td>
                <td>{task.new_value}</td>
                <td>{task.status}</td>
                <td>
                  <button className="button button-secondary" onClick={() => void onApplyTaskPatch(task.id)} type="button">
                    Apply Patch
                  </button>
                </td>
              </tr>
            )) : (
              <tr><td colSpan="7">No propagation tasks yet. Publish a rule candidate first.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SchedulerPage({ onRunScenario, onRunScheduler, scheduler }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Self-Update Scheduler</h3>
          <p>Manual controls for the circular sync loop and the complete demo policy-update sequence.</p>
        </div>
        <StatusPill tone={scheduler?.enabled ? "green" : "neutral"}>{scheduler?.message || "Scheduler status unavailable"}</StatusPill>
      </div>
      <div className="admin-finding-grid">
        <article className="admin-finding-card">
          <div className="admin-card-heading">
            <div>
              <span>{scheduler?.source_mode || "manual"}</span>
              <h3>Run Circular Sync</h3>
            </div>
            <StatusPill tone="blue">{scheduler?.interval_minutes || 60} min</StatusPill>
          </div>
          <p>Poll configured circular sources and deduplicate already-ingested circular documents.</p>
          <button className="button button-primary" onClick={() => void onRunScheduler()} type="button">
            Run Now
          </button>
        </article>
        <article className="admin-finding-card">
          <div className="admin-card-heading">
            <div>
              <span>Demo sequence</span>
              <h3>Sync, Extract, Approve, Publish</h3>
            </div>
            <StatusPill tone="green">Grounded demo</StatusPill>
          </div>
          <p>Runs the end-to-end policy update without paid APIs. Publication creates propagation tasks and a compliance rerun.</p>
          <div className="admin-report-actions">
            <button className="button button-secondary" onClick={() => void onRunScenario(false)} type="button">
              Run Workflow
            </button>
            <button className="button button-primary" onClick={() => void onRunScenario(true)} type="button">
              Run and Patch Mocks
            </button>
          </div>
        </article>
      </div>
    </section>
  );
}

function recordPayload(record) {
  return record?.payload || {};
}

function ReadinessPage({ onRunVirtualGov, readiness, virtualGovResult }) {
  const controls = readiness?.controls || [];
  const ops = readiness?.ops || {};
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Government Pilot Readiness</h3>
          <p>Control matrix for a synthetic government pilot with local AI fallback, dataset grounding, RBAC, audit, backup, and sandbox OTP checks.</p>
        </div>
        <StatusPill tone={readiness?.pilot_status === "ready" ? "green" : "red"}>
          {readiness?.pilot_status || "unknown"}
        </StatusPill>
      </div>

      <div className="admin-card-grid">
        <article className="admin-stat-card">
          <span>Ready controls</span>
          <strong>{readiness?.ready_controls || 0}/{readiness?.total_controls || 0}</strong>
          <p>Controls reported by backend readiness service.</p>
        </article>
        <article className="admin-stat-card">
          <span>Dataset records</span>
          <strong>{ops.dataset?.imported_records || 0}</strong>
          <p>Imported records available for grounded AI answers.</p>
        </article>
        <article className="admin-stat-card">
          <span>Search chunks</span>
          <strong>{ops.search?.indexed_chunks || 0}</strong>
          <p>Indexed records available to the hybrid retriever.</p>
        </article>
        <article className="admin-stat-card">
          <span>AI provider</span>
          <strong>{ops.ai?.active_provider || "fallback"}</strong>
          <p>{ops.ai?.fallback_available ? "Deterministic fallback available" : "Fallback unavailable"}</p>
        </article>
      </div>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Control</th>
              <th>Status</th>
              <th>Evidence</th>
            </tr>
          </thead>
          <tbody>
            {controls.map((control) => (
              <tr key={control.control_id}>
                <td>{control.name}</td>
                <td>{control.status}</td>
                <td>{control.evidence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section className="admin-panel">
        <div className="admin-card-heading">
          <div>
            <span>Virtual Government Sandbox</span>
            <h3>Run Regulation To Certificate Flow</h3>
          </div>
          <button className="button button-primary" onClick={() => void onRunVirtualGov()} type="button">
            Run Sandbox Scenario
          </button>
        </div>
        {virtualGovResult ? (
          <div className="admin-insight-grid">
            <article className="admin-finding-card">
              <h3>Scenario Artifacts</h3>
              <dl>
                <div>
                  <dt>Application</dt>
                  <dd>{virtualGovResult.artifacts?.application_number}</dd>
                </div>
                <div>
                  <dt>Certificate</dt>
                  <dd>{virtualGovResult.artifacts?.certificate_number}</dd>
                </div>
                <div>
                  <dt>Status</dt>
                  <dd>{virtualGovResult.artifacts?.tracking?.status}</dd>
                </div>
              </dl>
            </article>
            <article className="admin-finding-card">
              <h3>Completed Steps</h3>
              <ul className="admin-compact-list">
                {(virtualGovResult.steps || []).map((step) => (
                  <li key={step.step_id}>
                    <strong>{step.status}</strong>
                    <span>{step.title}</span>
                    <em>{step.step_id}</em>
                  </li>
                ))}
              </ul>
            </article>
          </div>
        ) : (
          <p>Run the sandbox to create synthetic application, payment, certificate, evidence, risk, and audit artifacts.</p>
        )}
      </section>
    </section>
  );
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

function AdminServicesPage({ services }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Service Definitions</h3>
          <p>Seeded public service catalog used by the NiyamGuard Service Portal.</p>
        </div>
        <StatusPill tone="blue">{services.length} services</StatusPill>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Category</th>
              <th>Fee</th>
              <th>SLA</th>
              <th>Required documents</th>
            </tr>
          </thead>
          <tbody>
            {services.map((service) => (
              <tr key={service.service_id}>
                <td>{service.name}</td>
                <td>{service.category}</td>
                <td>{service.fee_amount ? `Rs ${service.fee_amount}` : "No fee"}</td>
                <td>{service.processing_days} days</td>
                <td>{service.required_documents_json?.filter((item) => item.required).length || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AdminFormsPage({ forms }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Form Definitions</h3>
          <p>Versioned application form schemas used by citizen application routes.</p>
        </div>
        <StatusPill tone="blue">{forms.length} forms</StatusPill>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Service ID</th>
              <th>Version</th>
              <th>Fields</th>
              <th>Required documents</th>
              <th>Current</th>
            </tr>
          </thead>
          <tbody>
            {forms.map((form) => (
              <tr key={form.id}>
                <td>{form.service_id}</td>
                <td>{form.version}</td>
                <td>{form.fields_json?.map((field) => field.label).join(", ")}</td>
                <td>{form.validation_rules_json?.required_documents?.join(", ") || "-"}</td>
                <td>{form.is_current ? "yes" : "no"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AdminCertificatesPage({ certificates }) {
  return (
    <section className="admin-section">
      <div className="admin-page-summary">
        <div>
          <h3>Certificates</h3>
          <p>Generated demo certificates and public verification hashes.</p>
        </div>
        <StatusPill tone="green">{certificates.length} issued</StatusPill>
      </div>
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Certificate</th>
              <th>Service</th>
              <th>Status</th>
              <th>Issued</th>
              <th>Expires</th>
              <th>Verification</th>
            </tr>
          </thead>
          <tbody>
            {certificates.length ? certificates.map((certificate) => (
              <tr key={certificate.id}>
                <td>{certificate.certificate_number}</td>
                <td>{certificate.service_id}</td>
                <td>{certificate.status}</td>
                <td>{certificate.issued_at}</td>
                <td>{certificate.expires_at || "Not time limited"}</td>
                <td>{certificate.verification_hash}</td>
              </tr>
            )) : (
              <tr>
                <td colSpan="6">No certificates issued yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
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
