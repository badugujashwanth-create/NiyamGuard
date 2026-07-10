import { useState } from "react";

import { recommendSchemes } from "../../services/api";

const initialProfile = {
  age: "",
  income: "",
  category: "",
  student: false,
  occupation: "",
  district: "",
  disability: false,
  widow: false,
  purpose: "scholarship",
};

function toPayload(profile) {
  return {
    ...profile,
    age: profile.age ? Number(profile.age) : null,
    income: profile.income ? Number(profile.income) : null,
  };
}

export default function SchemeFinder({ onStartForm }) {
  const [profile, setProfile] = useState(initialProfile);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  function update(field, value) {
    setProfile((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus("Checking possible matches...");
    setError("");
    try {
      const response = await recommendSchemes(toPayload(profile));
      setResult(response);
      setStatus("Recommendations ready.");
    } catch (submitError) {
      setError(submitError.message);
      setStatus("");
    }
  }

  return (
    <main className="scheme-shell">
      <header className="scheme-header">
        <div>
          <p className="eyebrow">Citizen Scheme Finder</p>
          <h1>Find services that may match your need</h1>
          <p>
            Answer a few optional questions. NiyamGuard gives cautious demo
            recommendations and points you to forms or assistant help.
          </p>
        </div>
        <nav className="scheme-header-actions" aria-label="Citizen navigation">
          <a className="button button-secondary" href="/">Citizen portal</a>
          <a className="button button-secondary" href="/demo">Demo</a>
        </nav>
      </header>

      {error ? <div className="global-error" role="alert">{error}</div> : null}
      {status ? <p className="demo-action-status">{status}</p> : null}

      <section className="scheme-layout">
        <form className="scheme-form-panel" onSubmit={handleSubmit}>
          <h2>Profile Questions</h2>
          <div className="scheme-form-grid">
            <label htmlFor="scheme-age">Age<input id="scheme-age" min="0" onChange={(event) => update("age", event.target.value)} type="number" value={profile.age} /></label>
            <label htmlFor="scheme-income">Annual income<input id="scheme-income" min="0" onChange={(event) => update("income", event.target.value)} type="number" value={profile.income} /></label>
            <label htmlFor="scheme-category">Category<input id="scheme-category" onChange={(event) => update("category", event.target.value)} placeholder="General, BC, SC, ST..." value={profile.category} /></label>
            <label htmlFor="scheme-district">District<input id="scheme-district" onChange={(event) => update("district", event.target.value)} value={profile.district} /></label>
            <label htmlFor="scheme-occupation">Occupation<input id="scheme-occupation" onChange={(event) => update("occupation", event.target.value)} placeholder="student, farmer..." value={profile.occupation} /></label>
            <label htmlFor="scheme-purpose">Purpose<select id="scheme-purpose" onChange={(event) => update("purpose", event.target.value)} value={profile.purpose}>
              <option value="scholarship">Scholarship</option>
              <option value="pension">Pension</option>
              <option value="certificate">Certificate</option>
              <option value="agriculture loan">Agriculture loan</option>
              <option value="ews certificate">EWS certificate</option>
            </select></label>
          </div>
          <div className="scheme-checks">
            <label><input checked={profile.student} onChange={(event) => update("student", event.target.checked)} type="checkbox" /> Student</label>
            <label><input checked={profile.widow} onChange={(event) => update("widow", event.target.checked)} type="checkbox" /> Widow status</label>
            <label><input checked={profile.disability} onChange={(event) => update("disability", event.target.checked)} type="checkbox" /> Disability status</label>
          </div>
          <button className="button button-primary" type="submit">Find Possible Services</button>
          <p className="scheme-safe-note">Do not enter sensitive details unless needed. Demo answers are not official eligibility decisions.</p>
        </form>

        <section className="scheme-results" aria-label="Scheme recommendations">
          <h2>Recommendations</h2>
          {result?.recommendations?.length ? (
            <div className="scheme-result-list">
              {result.recommendations.map((item) => (
                <article className="admin-finding-card" key={item.form_id}>
                  <div className="admin-card-heading">
                    <div>
                      <span>{item.department}</span>
                      <h3>{item.service_name}</h3>
                    </div>
                    <span className="admin-pill admin-pill-blue">{Math.round(item.confidence * 100)}%</span>
                  </div>
                  <p>{item.why_it_may_match}</p>
                  <p><strong>Safe note:</strong> {item.safe_note}</p>
                  <dl>
                    <div><dt>Documents</dt><dd>{item.required_documents.join(", ")}</dd></div>
                    <div><dt>Source</dt><dd>{item.source.label}</dd></div>
                    <div><dt>Status</dt><dd>{item.status}</dd></div>
                  </dl>
                  <div className="admin-report-actions">
                    {item.start_application_available ? (
                      <button className="button button-primary" onClick={() => onStartForm?.(item.form_id)} type="button">
                        Start Application
                      </button>
                    ) : null}
                    <a className="button button-secondary" href="/">Ask Assistant</a>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty-state">Recommendations will appear after you answer the questions.</p>
          )}
        </section>
      </section>
    </main>
  );
}
