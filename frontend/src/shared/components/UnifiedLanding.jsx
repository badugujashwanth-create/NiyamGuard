export default function UnifiedLanding() {
  return (
    <main className="ng-landing" id="about">
      <header className="ng-landing-header">
        <a className="ng-wordmark" href="/" aria-label="NiyamGuard AI home">
          <span aria-hidden="true">NG</span>
          <strong>NiyamGuard AI</strong>
        </a>
        <nav aria-label="Primary navigation">
          <a href="#about">About</a>
          <a href="#how-it-works">How it works</a>
          <a className="ng-login-link" href="/login">Login</a>
        </nav>
      </header>

      <section className="ng-landing-hero" aria-labelledby="ng-landing-title">
        <p className="eyebrow">Policy intelligence for citizens</p>
        <h1 id="ng-landing-title">Government policies, simplified.</h1>
        <p>
          NiyamGuard detects policy changes and tells citizens what changed using verified policy sources.
        </p>
        <div className="ng-landing-actions">
          <a className="button button-primary" href="/login?next=%2Fcitizen%2Fhome">Open Citizen Portal</a>
          <a className="button button-secondary" href="/login?next=%2Fadmin%2Fdashboard">Admin Portal</a>
        </div>
      </section>

      <section className="ng-how-it-works" id="how-it-works" aria-label="How NiyamGuard works">
        <span>Upload policy</span><span aria-hidden="true">→</span><span>Review change</span><span aria-hidden="true">→</span><span>Publish verified update</span>
      </section>

      <footer>
        NiyamGuard AI — Synthetic sandbox demonstration. No real government application, payment, certificate, or system is affected.
      </footer>
    </main>
  );
}
