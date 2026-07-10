const portalChoices = [
  {
    title: "Citizen Portal",
    description:
      "Find services, apply online, track application status, verify certificates, and ask source-backed questions.",
    href: "/citizen",
    action: "Open Citizen Portal",
  },
  {
    title: "Government Portal",
    description:
      "Run the sandbox demo, update verified rules, review applications, issue certificates, monitor integrations, and test local AI.",
    href: "/government",
    action: "Open Government Portal",
  },
];

export default function UnifiedLanding() {
  return (
    <main className="unified-shell two-portal-shell">
      <section className="unified-banner" role="note">
        NiyamGuard Virtual Government Sandbox - Demo and pilot testing only. Not an official government portal.
      </section>

      <header className="two-portal-header">
        <p className="eyebrow">NiyamGuard</p>
        <h1>NiyamGuard</h1>
        <p>Choose one portal to start the demo.</p>
      </header>

      <section className="two-portal-grid" aria-label="NiyamGuard portals">
        {portalChoices.map((portal) => (
          <article className="two-portal-card" key={portal.title}>
            <div>
              <h2>{portal.title}</h2>
              <p>{portal.description}</p>
            </div>
            <a className="button button-primary" href={portal.href}>
              {portal.action}
            </a>
          </article>
        ))}
      </section>
    </main>
  );
}
