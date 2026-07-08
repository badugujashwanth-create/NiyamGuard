import { useEffect, useMemo, useState } from "react";

import {
  getAdminSummary,
  getCascadeForFinding,
  getComplianceFindings,
  getConflicts,
  getKnowledgeRules,
  getModuleStatus,
  getPriorityFindings,
  getReportsSummary,
  recalculatePriority,
  reportExportUrl,
  runCompliance,
  scanConflicts,
} from "../services/api";

const pages = [
  { path: "/admin", label: "Dashboard" },
  { path: "/admin/compliance", label: "Compliance" },
  { path: "/admin/cascade", label: "Cascade" },
  { path: "/admin/conflicts", label: "Conflicts" },
  { path: "/admin/knowledge-base", label: "Knowledge Base" },
  { path: "/admin/reports", label: "Reports" },
];

function numberOrZero(value) {
  return Number.isFinite(Number(value)) ? Number(value) : 0;
}

function StatusPill({ children, tone = "neutral" }) {
  return <span className={`admin-pill admin-pill-${tone}`}>{children}</span>;
}

export default function AdminPortal() {
  const [path, setPath] = useState(window.location.pathname);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);
  const [moduleStatus, setModuleStatus] = useState([]);
  const [findings, setFindings] = useState([]);
  const [priorityFindings, setPriorityFindings] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [rules, setRules] = useState([]);
  const [reports, setReports] = useState(null);
  const [trace, setTrace] = useState(null);

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
        await runCompliance();
        await recalculatePriority();
        await scanConflicts();
        const [
          adminSummary,
          modules,
          compliance,
          priorities,
          conflictList,
          knowledge,
          reportSummary,
        ] = await Promise.all([
          getAdminSummary(),
          getModuleStatus(),
          getComplianceFindings(),
          getPriorityFindings(),
          getConflicts(),
          getKnowledgeRules(),
          getReportsSummary(),
        ]);
        if (!active) return;
        const nextFindings = compliance.findings || [];
        setSummary(adminSummary.summary);
        setModuleStatus(modules.modules || []);
        setFindings(nextFindings);
        setPriorityFindings(priorities.priority_findings || []);
        setConflicts(conflictList.conflicts || []);
        setRules(knowledge.rules || []);
        setReports(reportSummary.summary);
        const firstDrift = nextFindings.find((item) => item.status === "drifted");
        if (firstDrift) {
          const cascade = await getCascadeForFinding(firstDrift.id);
          if (active) setTrace(cascade.trace);
        }
      } catch (loadError) {
        if (active) setError(loadError.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    void loadAdminData();
    return () => {
      active = false;
    };
  }, []);

  function navigate(nextPath) {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  }

  const activePage = path === "/admin/dashboard" ? "/admin" : path;
  const cards = useMemo(
    () => [
      ["Circulars", summary?.total_circulars],
      ["Verified Rules", summary?.verified_rules],
      ["Connected Systems", summary?.connected_systems],
      ["Drifted Findings", summary?.drifted_findings],
      ["Critical Findings", summary?.critical_findings],
      ["Open Conflicts", summary?.open_conflicts],
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
          <a className="button button-secondary" href="/" onClick={(event) => {
            event.preventDefault();
            window.history.pushState({}, "", "/");
            window.location.reload();
          }}>
            Citizen app
          </a>
        </header>

        {error ? <div className="global-error" role="alert">{error}</div> : null}
        {loading ? <p className="admin-loading">Loading government-core demo data...</p> : null}

        {!loading && activePage === "/admin" ? (
          <section className="admin-section" aria-label="Dashboard summary">
            <div className="admin-card-grid">
              {cards.map(([label, value]) => (
                <article className="admin-stat-card" key={label}>
                  <span>{label}</span>
                  <strong>{numberOrZero(value)}</strong>
                </article>
              ))}
            </div>
            <div className="admin-panel">
              <h3>Module Status</h3>
              <div className="admin-module-grid">
                {moduleStatus.map((module) => (
                  <div key={module.name}>
                    <span>{module.name.replaceAll("_", " ")}</span>
                    <StatusPill tone="green">{module.status}</StatusPill>
                  </div>
                ))}
              </div>
            </div>
            <PriorityTable priorities={priorityFindings} />
          </section>
        ) : null}

        {!loading && activePage === "/admin/compliance" ? (
          <section className="admin-section">
            <FindingTable findings={findings} />
          </section>
        ) : null}

        {!loading && activePage === "/admin/cascade" ? (
          <section className="admin-section">
            <div className="admin-panel">
              <h3>Cascade Trace</h3>
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
            </div>
          </section>
        ) : null}

        {!loading && activePage === "/admin/conflicts" ? (
          <section className="admin-section">
            <SimpleTable
              columns={["Service", "Rule", "Severity", "Status", "Summary"]}
              rows={conflicts.map((conflict) => [
                conflict.service_id,
                conflict.rule_key,
                conflict.severity,
                conflict.status,
                conflict.summary,
              ])}
            />
          </section>
        ) : null}

        {!loading && activePage === "/admin/knowledge-base" ? (
          <section className="admin-section">
            <SimpleTable
              columns={["Rule", "Service", "Current", "Previous", "Status", "Source"]}
              rows={rules.map((rule) => [
                rule.rule_name,
                rule.service_id,
                `${rule.current_value} ${rule.unit || ""}`.trim(),
                `${rule.previous_value || ""} ${rule.unit || ""}`.trim(),
                rule.status,
                rule.source_clause,
              ])}
            />
          </section>
        ) : null}

        {!loading && activePage === "/admin/reports" ? (
          <section className="admin-section">
            <div className="admin-panel">
              <h3>Reports</h3>
              <div className="admin-card-grid">
                {Object.entries(reports || {}).map(([label, value]) => (
                  <article className="admin-stat-card" key={label}>
                    <span>{label.replaceAll("_", " ")}</span>
                    <strong>{numberOrZero(value)}</strong>
                  </article>
                ))}
              </div>
              <div className="admin-report-actions">
                <a className="button button-primary" href={reportExportUrl("compliance", "csv")}>
                  Export Compliance CSV
                </a>
                <a className="button button-secondary" href={reportExportUrl("rules", "json")}>
                  Export Rules JSON
                </a>
              </div>
            </div>
          </section>
        ) : null}
      </main>
    </div>
  );
}

function PriorityTable({ priorities }) {
  return (
    <div className="admin-panel">
      <h3>Priority Findings</h3>
      <SimpleTable
        columns={["Finding", "Score", "Priority", "Reason"]}
        rows={priorities.map((priority) => [
          priority.finding_id,
          priority.score,
          priority.priority_level,
          priority.reason,
        ])}
      />
    </div>
  );
}

function FindingTable({ findings }) {
  return (
    <div className="admin-panel">
      <h3>Compliance Findings</h3>
      <SimpleTable
        columns={["Service", "Rule", "Expected", "Actual", "Status", "Fix"]}
        rows={findings.map((finding) => [
          finding.service_id,
          finding.rule_key,
          finding.expected_value,
          finding.actual_value || "Missing",
          finding.status,
          finding.recommended_fix,
        ])}
      />
    </div>
  );
}

function SimpleTable({ columns, rows }) {
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length ? (
            rows.map((row, rowIndex) => (
              <tr key={`${row[0]}-${rowIndex}`}>
                {row.map((cell, cellIndex) => (
                  <td key={`${cellIndex}-${cell}`}>{cell}</td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={columns.length}>No records available.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
