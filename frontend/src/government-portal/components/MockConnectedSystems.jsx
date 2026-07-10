import { useEffect, useState } from "react";

import { getMockMeeseva, getMockPublicFaq } from "../../services/api";

function MockShell({ children, title, subtitle }) {
  return (
    <main className="mock-shell">
      <header className="mock-header">
        <div>
          <p className="eyebrow">Demo connected system</p>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        <nav className="mock-nav" aria-label="Mock system links">
          <a className="button button-secondary" href="/demo">Demo</a>
          <a className="button button-secondary" href="/admin/propagation">Propagation</a>
        </nav>
      </header>
      {children}
    </main>
  );
}

function StatusLine({ system }) {
  const updated = system?.sync_status === "updated";
  return (
    <div className={`mock-status ${updated ? "mock-status-updated" : "mock-status-outdated"}`}>
      <strong>{updated ? "Updated" : "Outdated"}</strong>
      <span>Expected: {system?.expected_value || "6 months"}</span>
      <span>Source: {system?.source_circular || "not synced"}</span>
    </div>
  );
}

export function MockMeeSevaPortal() {
  const [system, setSystem] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getMockMeeseva()
      .then((response) => {
        if (active) setSystem(response.system);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <MockShell
      title="Mock MeeSeva Portal"
      subtitle="Synthetic portal screen used to demonstrate downstream policy propagation."
    >
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <section className="mock-service-layout">
        <div className="mock-form-panel">
          <h2>Income Certificate Application</h2>
          <StatusLine system={system} />
          <dl>
            <div>
              <dt>Certificate validity rule</dt>
              <dd>{system?.displayed_value || "Loading"}</dd>
            </div>
            <div>
              <dt>Service</dt>
              <dd>Income Certificate</dd>
            </div>
            <div>
              <dt>Rule key</dt>
              <dd>{system?.rule_key || "validity"}</dd>
            </div>
            <div>
              <dt>Last updated</dt>
              <dd>{system?.last_updated_at || "Not synced"}</dd>
            </div>
          </dl>
          <form className="mock-form">
            <label htmlFor="mock-name">Applicant name<input id="mock-name" readOnly value="Demo Citizen" /></label>
            <label htmlFor="mock-purpose">Purpose<input id="mock-purpose" readOnly value="Scholarship" /></label>
            <label htmlFor="mock-validity">Portal validation hint<input id="mock-validity" readOnly value={system?.displayed_value || ""} /></label>
          </form>
        </div>
        <aside className="mock-side-panel">
          <h2>Operational Status</h2>
          <p>This mock system changes only when NiyamGuard applies the demo propagation patch.</p>
          <a className="button button-primary" href="/demo">Return to demo controls</a>
        </aside>
      </section>
    </MockShell>
  );
}

export function MockPublicFaq() {
  const [system, setSystem] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getMockPublicFaq()
      .then((response) => {
        if (active) setSystem(response.system);
      })
      .catch((loadError) => {
        if (active) setError(loadError.message);
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <MockShell
      title="Mock Public FAQ"
      subtitle="Synthetic FAQ and citizen form content used to show public content propagation."
    >
      {error ? <div className="global-error" role="alert">{error}</div> : null}
      <section className="mock-service-layout">
        <div className="mock-form-panel">
          <h2>Income Certificate Help</h2>
          <StatusLine system={system} />
          <article className="mock-faq-item">
            <h3>How long is an income certificate valid?</h3>
            <p>{system?.faq_value || "Loading"} from the current displayed public FAQ content.</p>
          </article>
          <article className="mock-faq-item">
            <h3>Form hint shown to citizens</h3>
            <p>Please upload an income certificate issued within {system?.form_hint_value || "loading"}.</p>
          </article>
          <dl>
            <div>
              <dt>Expected value</dt>
              <dd>{system?.expected_value || "6 months"}</dd>
            </div>
            <div>
              <dt>Last updated</dt>
              <dd>{system?.last_updated_at || "Not synced"}</dd>
            </div>
          </dl>
        </div>
        <aside className="mock-side-panel">
          <h2>Content Status</h2>
          <p>The FAQ and form hint are patched together so citizens receive one consistent rule.</p>
          <a className="button button-primary" href="/demo">Return to demo controls</a>
        </aside>
      </section>
    </MockShell>
  );
}
