import { useEffect, useState } from "react";

import {
  getVirtualGovScenarios,
  getVirtualGovStatus,
  runVirtualGovScenario,
} from "../services/api";

function ScenarioStep({ step }) {
  const entries = Object.entries(step.payload || {}).slice(0, 6);
  return (
    <article className="admin-finding-card">
      <div className="admin-card-heading">
        <div>
          <span>{step.step_id}</span>
          <h3>{step.title}</h3>
        </div>
        <span className="admin-pill admin-pill-green">{step.status}</span>
      </div>
      <dl>
        {entries.map(([key, value]) => (
          <div key={key}>
            <dt>{key.replaceAll("_", " ")}</dt>
            <dd>{formatStepValue(value)}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

function formatStepValue(value) {
  if (value === null || value === undefined || value === "") return "Not found";
  if (Array.isArray(value)) return `${value.length} records`;
  if (typeof value === "object") {
    return value.title || value.answer || value.status || value.certificate_number || value.application_number || "Available";
  }
  return String(value);
}

export default function VirtualGovernmentSandbox() {
  const [status, setStatus] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        const [statusResponse, scenarioResponse] = await Promise.all([
          getVirtualGovStatus(),
          getVirtualGovScenarios(),
        ]);
        if (!active) return;
        setStatus(statusResponse);
        setScenarios(scenarioResponse.scenarios || []);
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

  async function handleRun() {
    setRunning(true);
    setError("");
    try {
      const response = await runVirtualGovScenario({
        scenarioId: scenarios[0]?.scenario_id || "income_certificate_full_flow",
        resetBeforeRun: true,
      });
      setResult(response);
      setStatus(await getVirtualGovStatus());
    } catch (runError) {
      setError(runError.message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <main className="admin-main sandbox-page">
      <header className="admin-header">
        <div>
          <p className="eyebrow">Synthetic government sandbox</p>
          <h1>Virtual Government Sandbox</h1>
        </div>
        <div className="admin-header-actions">
          <a className="button button-secondary" href="/demo">Demo dashboard</a>
          <a className="button button-secondary" href="/admin/readiness">Readiness</a>
        </div>
      </header>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {loading ? <p className="admin-loading">Loading virtual government sandbox...</p> : null}

      {!loading ? (
        <>
          <section className="admin-section">
            <div className="admin-page-summary">
              <div>
                <h2>Regulation To Certificate Demo</h2>
                <p>
                  Runs the full synthetic path from regulatory Q&A to application,
                  evidence, payment, officer approval, certificate verification, and audit context.
                </p>
              </div>
              <button className="button button-primary" disabled={running} onClick={handleRun} type="button">
                {running ? "Running..." : "Run Sandbox Scenario"}
              </button>
            </div>
            <div className="admin-card-grid">
              <article className="admin-stat-card">
                <span>Applications</span>
                <strong>{status?.applications || 0}</strong>
                <p>Created in the virtual sandbox.</p>
              </article>
              <article className="admin-stat-card">
                <span>Certificates</span>
                <strong>{status?.certificates || 0}</strong>
                <p>Synthetic certificates issued and verifiable.</p>
              </article>
              <article className="admin-stat-card">
                <span>Audit Events</span>
                <strong>{status?.audit_events || 0}</strong>
                <p>Evidence of scenario actions.</p>
              </article>
            </div>
          </section>

          {result ? (
            <section className="admin-section">
              <div className="admin-page-summary">
                <div>
                  <h2>{result.title}</h2>
                  <p>{result.artifacts?.application_number} / {result.artifacts?.certificate_number}</p>
                </div>
                <span className="admin-pill admin-pill-green">completed</span>
              </div>
              <div className="admin-finding-grid">
                {(result.steps || []).map((step) => (
                  <ScenarioStep key={step.step_id} step={step} />
                ))}
              </div>
            </section>
          ) : null}
        </>
      ) : null}
    </main>
  );
}
