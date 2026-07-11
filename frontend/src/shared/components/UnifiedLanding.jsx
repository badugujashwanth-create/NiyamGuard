import SpotlightCard from "../react-bits/SpotlightCard";

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
      "Review circulars and applications, approve verified rule changes, check compliance, prioritize drift, and trace officer actions.",
    href: "/government",
    action: "Open Government Portal",
  },
  {
    title: "Admin Portal",
    description:
      "Run the virtual government sandbox, manage users and roles, monitor system readiness, and review the system-wide audit trail.",
    href: "/admin",
    action: "Open Admin Portal",
  },
  {
    title: "Certificate Verification",
    description:
      "Verify a NiyamGuard demo certificate from its public certificate number or verification hash without signing in.",
    href: "/verify-certificate",
    action: "Verify a Certificate",
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
        <p>Choose the role-specific portal or use public certificate verification.</p>
      </header>

      <section className="two-portal-grid" aria-label="NiyamGuard portals">
        {portalChoices.map((portal) => (
          <SpotlightCard as="article" className="two-portal-card" key={portal.title}>
            <div>
              <h2>{portal.title}</h2>
              <p>{portal.description}</p>
            </div>
            <a className="button button-primary" href={portal.href}>
              {portal.action}
            </a>
          </SpotlightCard>
        ))}
      </section>
    </main>
  );
}
