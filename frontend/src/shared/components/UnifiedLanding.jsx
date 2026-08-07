export default function UnifiedLanding() {
  return (
    <main className="unified-shell two-portal-shell">
      <section className="unified-banner" role="note">
        NiyamGuard Virtual Government Sandbox - Synthetic pilot testing only. Not an official government portal.
      </section>

      <header className="two-portal-header">
        <p className="eyebrow">Policy drift detection · human review required</p>
        <h1>A government rule changed. Downstream systems are still wrong.</h1>
        <p>
          NiyamGuard follows one synthetic circular from source evidence to verified rule,
          then shows which connected services still carry the old value.
        </p>
      </header>

      <section className="policy-incident" aria-labelledby="incident-title">
        <div className="policy-incident-copy">
          <p className="eyebrow">Synthetic incident · GO-138</p>
          <h2 id="incident-title">Income Certificate validity</h2>
          <p>
            A reviewer can inspect the exact clause, compare versions, approve the change,
            and rerun deterministic checks before publishing a propagation plan.
          </p>
          <div className="policy-delta" aria-label="Policy change from twelve months to six months">
            <span><small>Previous</small><strong>12 months</strong></span>
            <span className="policy-arrow" aria-hidden="true">→</span>
            <span><small>Proposed</small><strong>6 months</strong></span>
          </div>
          <p className="policy-meta">Effective 01 Jul 2026 · Revenue Department · synthetic source</p>
        </div>
        <div className="policy-impact" aria-label="Policy impact summary">
          <p className="eyebrow">Impact chain</p>
          <h3>What needs attention?</h3>
          <ul>
            <li><strong>4</strong><span>connected systems to review</span></li>
            <li><strong>1</strong><span>open conflict requiring a decision</span></li>
            <li><strong>1</strong><span>verified version after human approval</span></li>
          </ul>
        </div>
      </section>

      <section className="two-portal-grid" aria-label="NiyamGuard workflows">
        <article className="two-portal-card">
          <div>
            <p className="eyebrow">Reviewer workflow</p>
            <h2>See the evidence trail</h2>
            <p>Run the circular → candidate → review → publish → drift scenario in the government sandbox.</p>
          </div>
          <a className="button button-primary" href="/government">Open Reviewer Workflow</a>
        </article>
        <article className="two-portal-card">
          <div>
            <p className="eyebrow">Citizen workflow</p>
            <h2>Ask against verified guidance</h2>
            <p>Explore synthetic services and receive source-backed answers without automatic submission.</p>
          </div>
          <a className="button button-primary" href="/citizen">Open Citizen Portal</a>
        </article>
      </section>

      <p className="policy-boundary">Synthetic data only · no government system is patched · every publication requires human approval.</p>
    </main>
  );
}
