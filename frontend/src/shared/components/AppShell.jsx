import SpotlightCard from "../react-bits/SpotlightCard";

function isPlainLeftClick(event) {
  return event.button === 0 && !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;
}

export default function AppShell({ children, currentUser, onLogout, onNavigate, path }) {
  function handleClick(event) {
    if (!isPlainLeftClick(event)) return;
    const anchor = event.target.closest?.("a[href]");
    if (!anchor || anchor.target || anchor.hasAttribute("download")) return;
    const url = new URL(anchor.href, window.location.href);
    if (url.origin !== window.location.origin) return;
    event.preventDefault();
    onNavigate(`${url.pathname}${url.search}${url.hash}`);
  }

  return (
    <div className="app-frame" onClick={handleClick}>
      <SpotlightCard as="nav" aria-label="Primary navigation" className="app-topbar" spotlightColor="rgba(23, 104, 78, 0.12)">
        <a className="app-brand-link" href="/">
          <span className="brand-emblem" aria-hidden="true">NG</span>
          <span>
            <strong>NiyamGuard</strong>
            <small>{currentUser?.role ? `${currentUser.role} account` : "public access"}</small>
          </span>
        </a>
        <span className="app-route-label" aria-live="polite">
          {path.startsWith("/admin")
            ? "Admin Portal"
            : path.startsWith("/government") || path.startsWith("/officer")
              ? "Government Officer Portal"
              : path.startsWith("/verify")
                ? "Certificate Verification"
                : path.startsWith("/citizen") ||
                    path.startsWith("/services") ||
                    path.startsWith("/apply") ||
                    path.startsWith("/applications") ||
                    path.startsWith("/track") ||
                    path.startsWith("/payment") ||
                    path.startsWith("/scheme-finder")
                  ? "Citizen Portal"
                  : "NiyamGuard"}
        </span>
        <div className="app-account">
          {currentUser ? (
            <>
              <span>{currentUser.email}</span>
              <button className="button button-secondary" onClick={() => void onLogout()} type="button">
                Logout
              </button>
            </>
          ) : (
            <a className="button button-secondary" href="/login">Login</a>
          )}
        </div>
      </SpotlightCard>
      <div className="app-content">{children}</div>
    </div>
  );
}
