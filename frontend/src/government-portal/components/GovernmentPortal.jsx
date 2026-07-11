import { useEffect, useMemo, useState } from "react";

import { OfficerApplicationReview } from "../../citizen-portal/components/ServicePortal";
import SpotlightCard from "../../shared/react-bits/SpotlightCard";
import {
  approveRuleCandidate,
  getCascadeForFinding,
  getCircularDocuments,
  getComplianceFindings,
  getDashboardSummary,
  getGovernmentAuditEvents,
  getPriorityFindings,
  getRuleCandidates,
  recalculatePriority,
  runCompliance,
  uploadCircularFile,
} from "../../services/api";

const navItems = [
  { href: "/government", label: "Overview" },
  { href: "/government/circulars", label: "Circular Intake" },
  { href: "/government/compliance", label: "Compliance" },
  { href: "/government/priority", label: "Priority" },
  { href: "/government/cascade", label: "Cascade" },
  { href: "/government/audit", label: "Audit" },
  { href: "/government/applications", label: "Application Review" },
];

function titleCase(value = "") {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function navigateTo(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new Event("popstate"));
}

function isActiveNavPath(activePath, href) {
  if (href === "/government") return activePath === href;
  return activePath === href || activePath.startsWith(`${href}/`);
}

function Pill({ children, tone = "neutral" }) {
  return <span className={`admin-pill admin-pill-${tone}`}>{children}</span>;
}

function DataTable({ columns, rows, empty }) {
  return (
    <div className="admin-table-wrap">
      <table className="admin-table">
        <thead>
          <tr>{columns.map((column) => <th key={column.key}>{column.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.length ? rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>)}
            </tr>
          )) : (
            <tr><td colSpan={columns.length}>{empty}</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

function CircularUploadPanel({ busy, onUpload }) {
  const [file, setFile] = useState(null);
  const [circularNumber, setCircularNumber] = useState("");
  const [title, setTitle] = useState("");
  const [department, setDepartment] = useState("");
  const [effectiveDate, setEffectiveDate] = useState("");

  async function submit(event) {
    event.preventDefault();
    const form = event.currentTarget;
    await onUpload({ file, circularNumber, title, department, effectiveDate });
    setFile(null);
    form.reset();
    setCircularNumber("");
    setTitle("");
    setDepartment("");
    setEffectiveDate("");
  }

  return (
    <SpotlightCard as="section" className="admin-finding-card circular-upload-panel">
      <div className="admin-page-summary">
        <div>
          <h3>Upload New Circular</h3>
          <p>Upload a PDF or text circular. NiyamGuard extracts rule changes and holds them for officer review.</p>
        </div>
      </div>
      <form className="admin-filter-grid" onSubmit={submit}>
        <label>
          Circular document
          <input accept=".pdf,.txt,.md,application/pdf,text/plain" onChange={(event) => setFile(event.target.files?.[0] || null)} required type="file" />
        </label>
        <label>
          Circular ID / number
          <input onChange={(event) => setCircularNumber(event.target.value)} placeholder="GO-204" required value={circularNumber} />
        </label>
        <label>
          Title
          <input onChange={(event) => setTitle(event.target.value)} placeholder="Income Certificate Rule Update" required value={title} />
        </label>
        <label>
          Department
          <input onChange={(event) => setDepartment(event.target.value)} placeholder="Revenue Department" required value={department} />
        </label>
        <label>
          Effective date
          <input onChange={(event) => setEffectiveDate(event.target.value)} required type="date" value={effectiveDate} />
        </label>
        <button className="button button-primary" disabled={busy || !file} type="submit">
          {busy ? "Extracting..." : "Upload & Extract"}
        </button>
      </form>
    </SpotlightCard>
  );
}

export default function GovernmentPortal() {
  const [path, setPath] = useState(window.location.pathname);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [circulars, setCirculars] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [findings, setFindings] = useState([]);
  const [priorityFindings, setPriorityFindings] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [trace, setTrace] = useState(null);
  const [summary, setSummary] = useState({});
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    function handlePopState() {
      setPath(window.location.pathname);
    }
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [circularResponse, candidateResponse, findingResponse, priorityResponse, auditResponse, summaryResponse] = await Promise.all([
        getCircularDocuments(),
        getRuleCandidates(),
        getComplianceFindings(),
        getPriorityFindings(),
        getGovernmentAuditEvents(),
        getDashboardSummary(),
      ]);
      let nextFindings = findingResponse.findings || [];
      let nextPriorityFindings = priorityResponse.priority_findings || [];
      if (!nextFindings.length) {
        const complianceResponse = await runCompliance();
        nextFindings = complianceResponse.findings || [];
      }
      if (!nextPriorityFindings.length && nextFindings.length) {
        const priorityRefresh = await recalculatePriority();
        nextPriorityFindings = priorityRefresh.priority_findings || [];
      }
      setCirculars(circularResponse.circulars || []);
      setCandidates(candidateResponse.candidates || []);
      setFindings(nextFindings);
      setPriorityFindings(nextPriorityFindings);
      setAuditEvents(auditResponse.events || []);
      setSummary(summaryResponse.summary || {});
      const firstDrift = nextFindings.find((finding) => finding.status === "drifted");
      if (firstDrift) {
        const cascade = await getCascadeForFinding(firstDrift.id);
        setTrace(cascade.trace);
      }
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const priorityByFinding = useMemo(
    () => Object.fromEntries(priorityFindings.map((item) => [item.finding_id, item])),
    [priorityFindings],
  );
  const activePath = path === "/government/dashboard" ? "/government" : path;
  const activeNavItem = navItems.find((item) => isActiveNavPath(activePath, item.href));
  const applicationRouteSegment = activePath.split("/").filter(Boolean)[2];
  const applicationId = applicationRouteSegment && !["pending", "approved", "rejected"].includes(applicationRouteSegment)
    ? applicationRouteSegment
    : null;
  const overviewStats = useMemo(
    () => ({
      circulars: Math.max(circulars.length, Number(summary.total_circulars || 0)),
      ruleCandidates: Math.max(candidates.length, Number(summary.pending_extractions || 0), Number(summary.verified_rules || 0)),
      openMismatches: Math.max(
        findings.filter((finding) => finding.status === "drifted").length,
        Number(summary.drifted_findings || 0),
      ),
      criticalPriority: Math.max(
        priorityFindings.filter((item) => item.priority_level === "critical").length,
        Number(summary.critical_findings || 0),
      ),
    }),
    [candidates.length, circulars.length, findings, priorityFindings, summary],
  );

  async function refreshCompliance() {
    setStatus("Running compliance and priority checks...");
    await runCompliance();
    await recalculatePriority();
    await load();
    setStatus("Compliance data refreshed.");
  }

  async function uploadCircular(payload) {
    setUploading(true);
    setError("");
    setStatus("Uploading circular and extracting rule changes...");
    try {
      const response = await uploadCircularFile(payload);
      const confidence = response.candidates?.[0]?.confidence_score;
      await load();
      setStatus(
        `Circular uploaded. ${response.candidates?.length || 0} rule candidate(s) are pending review${confidence ? ` at ${Math.round(confidence * 100)}% confidence` : ""}.`,
      );
    } catch (uploadError) {
      setError(uploadError.message);
      setStatus("");
      throw uploadError;
    } finally {
      setUploading(false);
    }
  }

  async function approveCandidate(candidateId) {
    setError("");
    setStatus("Approving rule and running connected-system compliance checks...");
    try {
      const response = await approveRuleCandidate(candidateId, "Approved in Circular Intake");
      await load();
      setStatus(response.publication?.compliance_run
        ? "Rule approved, published, and compliance checks completed."
        : "Rule approved and published. Compliance configuration did not request an automatic rerun.");
    } catch (approvalError) {
      setError(approvalError.message);
      setStatus("");
    }
  }

  return (
    <div className="government-shell">
      <header className="portal-header">
        <div className="brand">
          <span className="brand-emblem" aria-hidden="true">NG</span>
          <div>
            <p>Government Officer Portal</p>
            <h1>Policy Operations</h1>
          </div>
        </div>
        <nav className="portal-nav" aria-label="Government officer portal">
          {navItems.map((item) => (
            <button
              className={isActiveNavPath(activePath, item.href) ? "active" : ""}
              key={item.href}
              onClick={() => navigateTo(item.href)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="admin-main">
        <header className="admin-header">
          <div>
            <p className="eyebrow">Officer workspace</p>
            <h2>{activeNavItem?.label || "Overview"}</h2>
          </div>
          <button className="button button-secondary" onClick={() => void refreshCompliance()} type="button">
            Refresh Checks
          </button>
        </header>

        {error ? <div className="global-error" role="alert">{error}</div> : null}
        {status ? <p className="admin-action-status">{status}</p> : null}
        {loading ? <p className="admin-loading">Loading government operations...</p> : null}

        {!loading && activePath === "/government" ? (
          <section className="admin-section">
            <CircularUploadPanel busy={uploading} onUpload={uploadCircular} />
            <div className="admin-card-grid">
              <SpotlightCard as="article" className="admin-stat-card">
                <span>Circulars</span>
                <strong>{overviewStats.circulars}</strong>
                <p>Uploaded, synced, or seeded circular documents available for officer review.</p>
              </SpotlightCard>
              <SpotlightCard as="article" className="admin-stat-card">
                <span>Rule Candidates</span>
                <strong>{overviewStats.ruleCandidates}</strong>
                <p>Extracted or verified rule changes available to officers.</p>
              </SpotlightCard>
              <SpotlightCard as="article" className="admin-stat-card">
                <span>Open Mismatches</span>
                <strong>{overviewStats.openMismatches}</strong>
                <p>Connected systems that still need updates.</p>
              </SpotlightCard>
              <SpotlightCard as="article" className="admin-stat-card">
                <span>Critical Priority</span>
                <strong>{overviewStats.criticalPriority}</strong>
                <p>Citizen-impacting items requiring urgent handling.</p>
              </SpotlightCard>
            </div>
          </section>
        ) : null}

        {!loading && activePath === "/government/circulars" ? (
          <section className="admin-section">
            <CircularUploadPanel busy={uploading} onUpload={uploadCircular} />
            <div className="admin-page-summary">
              <div>
                <h3>Circular Intake</h3>
                <p>Review uploaded circulars and backend-extracted rule candidates. Sandbox generation is admin-only.</p>
              </div>
            </div>
            <DataTable
              columns={[
                { key: "circular_number", label: "Circular ID" },
                { key: "title", label: "Title" },
                { key: "department", label: "Department" },
                { key: "status", label: "Status", render: (row) => <Pill>{titleCase(row.status)}</Pill> },
                { key: "effective_date", label: "Effective Date" },
              ]}
              empty="No circulars available."
              rows={circulars}
            />
            <h3>Rule Candidates</h3>
            <DataTable
              columns={[
                { key: "circular_id", label: "Circular" },
                { key: "service_id", label: "Service", render: (row) => titleCase(row.service_id) },
                { key: "change_summary", label: "What Changed" },
                { key: "confidence_score", label: "Confidence", render: (row) => `${Math.round(Number(row.confidence_score || 0) * 100)}%` },
                { key: "status", label: "Status", render: (row) => <Pill>{titleCase(row.status)}</Pill> },
                { key: "effective_date", label: "Date" },
                {
                  key: "review",
                  label: "Review",
                  render: (row) => row.status === "pending_review" ? (
                    <button className="button button-primary" onClick={() => void approveCandidate(row.id)} type="button">Approve & Check</button>
                  ) : <span>{titleCase(row.status)}</span>,
                },
              ]}
              empty="No rule candidates available."
              rows={candidates}
            />
          </section>
        ) : null}

        {!loading && (activePath === "/government/applications" || activePath.startsWith("/government/applications/")) ? (
          <OfficerApplicationReview applicationId={applicationId} path={activePath} />
        ) : null}

        {!loading && activePath === "/government/compliance" ? (
          <section className="admin-section">
            <DataTable
              columns={[
                { key: "id", label: "Finding" },
                { key: "service_id", label: "Service", render: (row) => titleCase(row.service_id) },
                { key: "status", label: "Status", render: (row) => <Pill tone={row.status === "drifted" ? "red" : "green"}>{titleCase(row.status)}</Pill> },
                { key: "severity", label: "Severity", render: (row) => titleCase(row.severity) },
                { key: "finding_summary", label: "Summary" },
              ]}
              empty="No compliance findings available."
              rows={findings}
            />
          </section>
        ) : null}

        {!loading && activePath === "/government/priority" ? (
          <section className="admin-section">
            <DataTable
              columns={[
                { key: "finding_id", label: "Finding" },
                { key: "priority_level", label: "Priority", render: (row) => <Pill tone={row.priority_level === "critical" ? "red" : "blue"}>{titleCase(row.priority_level)}</Pill> },
                { key: "score", label: "Score" },
                { key: "reason", label: "Reason" },
              ]}
              empty="No priority scores available."
              rows={priorityFindings.map((item) => ({ ...item, id: item.id || item.finding_id }))}
            />
          </section>
        ) : null}

        {!loading && activePath === "/government/cascade" ? (
          <section className="admin-section">
            <div className="admin-page-summary">
              <div>
                <h3>Cascade Trace</h3>
                <p>{trace?.impact_summary || "No cascade trace available until a drift finding exists."}</p>
              </div>
            </div>
            <div className="admin-card-grid">
              {(trace?.nodes || []).map((node) => (
                <article className="admin-finding-card" key={node.id}>
                  <h3>{node.label}</h3>
                  <p>{node.type ? titleCase(node.type) : "Trace node"}</p>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {!loading && activePath === "/government/audit" ? (
          <section className="admin-section">
            <DataTable
              columns={[
                { key: "created_at", label: "Time" },
                { key: "action", label: "Action", render: (row) => titleCase(row.action) },
                { key: "actor_email", label: "Actor" },
                { key: "entity_type", label: "Entity" },
              ]}
              empty="No audit events available."
              rows={auditEvents}
            />
          </section>
        ) : null}
      </main>
    </div>
  );
}
