import { useEffect, useState } from "react";

import { getPublicPolicyUpdates } from "../../services/api";
import CitizenAssistantDock from "./CitizenAssistantDock";

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new Event("popstate"));
}

function policyFromResponse(rule) {
  const source = rule?.source || {};
  return {
    id: rule.id,
    label: source.circular_number || "Verified source",
    title: rule.title || "Verified policy update",
    previous: rule.previous_value || "No prior published value",
    current: [rule.current_value, rule.unit].filter(Boolean).join(" ") || "Published value",
    effective: rule.effective_date || "Effective date pending",
    service: rule.service_id?.replaceAll("_", " ") || "Digital citizen services",
    source: source.circular_number || "Verified policy source",
  };
}

function PolicyCard({ policy }) {
  return (
    <article className="citizen-policy-card">
      <div><p className="eyebrow">{policy.label}</p><h2>{policy.title}</h2></div>
      <span className="citizen-policy-status">Verified</span>
      <p className="citizen-policy-change"><strong>{policy.previous}</strong><span aria-hidden="true">→</span><strong>{policy.current}</strong></p>
      <dl><div><dt>Effective</dt><dd>{policy.effective}</dd></div><div><dt>Service</dt><dd>{policy.service}</dd></div><div><dt>Source</dt><dd>{policy.source}</dd></div></dl>
      <button className="button button-secondary" onClick={() => navigate("/citizen/updates")} type="button">View details</button>
    </article>
  );
}

export default function CitizenPolicyPortal({ path, currentUser, onLogout }) {
  const [policies, setPolicies] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getPublicPolicyUpdates()
      .then((response) => active && setPolicies((response.updates || []).map(policyFromResponse)))
      .catch(() => active && setError("Verified policy updates are temporarily unavailable."));
    return () => { active = false; };
  }, []);

  const section = path.includes("/updates") ? "updates" : path.includes("/services") ? "services" : "home";
  const updateCards = policies.map((policy) => <PolicyCard key={policy.id} policy={policy} />);

  return (
    <div className="citizen-policy-shell">
      <header className="citizen-policy-header">
        <a className="ng-wordmark" href="/citizen/home"><span aria-hidden="true">NG</span><strong>NiyamGuard AI</strong></a>
        <nav aria-label="Citizen portal"><button onClick={() => navigate("/citizen/home")} type="button">Home</button><button onClick={() => navigate("/citizen/updates")} type="button">Updates</button><button onClick={() => navigate("/citizen/services")} type="button">Services</button><button onClick={() => document.querySelector(".citizen-assistant-launcher")?.click()} type="button">Assistant</button></nav>
        <div className="citizen-profile"><span>{currentUser?.email || "Citizen"}</span><button onClick={onLogout} type="button">Logout</button></div>
      </header>
      <main className="citizen-policy-main">
        {error ? <p className="global-error">{error}</p> : null}
        {section === "home" ? <><p className="eyebrow">Citizen home</p><h1>Stay informed about verified government policy changes.</h1><section className="citizen-policy-hero"><p className="eyebrow">New policy update</p>{policies[0] ? <PolicyCard policy={policies[0]} /> : <p>Loading verified updates…</p>}</section><h2>Recent updates</h2><div className="citizen-policy-grid">{updateCards}</div></> : null}
        {section === "updates" ? <><p className="eyebrow">Verified policy updates</p><h1>Updates</h1><p className="citizen-policy-intro">Only approved and published policy updates appear here.</p><div className="citizen-policy-grid">{updateCards.length ? updateCards : <p>Loading verified updates…</p>}</div></> : null}
        {section === "services" ? <><p className="eyebrow">Current requirements</p><h1>Services</h1><p className="citizen-policy-intro">Find the latest verified guidance for a service. Application processing remains outside this policy-awareness portal.</p><div className="citizen-service-list"><button onClick={() => navigate("/services/income_certificate")} type="button">Income Certificate <span>View current requirements →</span></button><button onClick={() => navigate("/services/residence_certificate")} type="button">Residence Certificate <span>View current requirements →</span></button><button onClick={() => navigate("/services/birth_certificate")} type="button">Birth Certificate <span>View current requirements →</span></button></div></> : null}
      </main>
      <CitizenAssistantDock />
    </div>
  );
}
