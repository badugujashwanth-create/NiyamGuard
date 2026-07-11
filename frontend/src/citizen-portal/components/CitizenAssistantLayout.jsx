import { useEffect, useState } from "react";

import { CitizenAssistantProvider, useCitizenAssistant } from "../context/CitizenAssistantContext";
import VoiceAssistantPanel from "./VoiceAssistantPanel";
import SpotlightCard from "../../shared/react-bits/SpotlightCard";

const citizenNavItems = [
  { href: "/citizen", label: "Home" },
  { href: "/services", label: "Services" },
  { href: "/scheme-finder", label: "Scheme Finder" },
  { href: "/applications", label: "Applications" },
  { href: "/track", label: "Track" },
  { href: "/citizen/profile", label: "Profile" },
  { href: "/citizen/documents", label: "Documents" },
];

export function isCitizenAssistantRoute(path = "/") {
  return (
    path === "/citizen" ||
    path.startsWith("/citizen/assistant") ||
    path.startsWith("/citizen/profile") ||
    path.startsWith("/citizen/documents") ||
    path.startsWith("/scheme-finder") ||
    path.startsWith("/services") ||
    path.startsWith("/apply") ||
    path.startsWith("/applications") ||
    path.startsWith("/track") ||
    path.startsWith("/payment")
  );
}

function isPlainLeftClick(event) {
  return event.button === 0 && !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;
}

function CitizenAssistantHost() {
  const assistant = useCitizenAssistant();
  const [collapsed, setCollapsed] = useState(false);
  const contextLabel = [
    assistant.pageContext.serviceName,
    assistant.pageContext.mode?.replaceAll("_", " "),
  ].filter(Boolean).join(" - ");

  return (
    <aside
      className={`global-citizen-chatbot${collapsed ? " chatbot-collapsed" : ""}`}
      id="global-citizen-voice-assistant"
      aria-label="Citizen chatbot assistant"
    >
      <SpotlightCard as="div" className="chatbot-toolbar" spotlightColor="rgba(23, 104, 78, 0.16)">
        <div>
          <span>NiyamGuard Chatbot</span>
          <strong>{contextLabel || "Citizen services"}</strong>
        </div>
        <button className="button button-secondary" onClick={() => setCollapsed((current) => !current)} type="button">
          {collapsed ? "Open" : "Minimize"}
        </button>
      </SpotlightCard>
      {!collapsed ? (
        <>
          <VoiceAssistantPanel
            activeDocument={assistant.pageContext.activeDocument || ""}
            activeField={assistant.pageContext.activeField || ""}
            asking={assistant.asking}
            assistantReply={assistant.assistantReply}
            formId={assistant.formId}
            introText={assistant.introText}
            lastDetectedLanguage={assistant.lastDetectedLanguage}
            lastLanguageCode={assistant.lastLanguageCode}
            messages={assistant.messages}
            onAsk={assistant.ask}
            onClear={assistant.clear}
            onUseLocation={assistant.useLocation}
            sessionId={assistant.sessionId}
            sessionStatus={assistant.sessionStatus}
            speechCommand={assistant.speechCommand}
            textPlaceholder={assistant.placeholder}
          />
          {assistant.error ? <p className="support-message support-error">{assistant.error}</p> : null}
        </>
      ) : (
        <button className="chatbot-collapsed-button" onClick={() => setCollapsed(false)} type="button">
          <span>NG</span>
          <strong>Chat</strong>
        </button>
      )}
    </aside>
  );
}

function CitizenAssistantLayoutInner({ children, onNavigate, path }) {
  const { setRoutePath } = useCitizenAssistant();

  useEffect(() => {
    setRoutePath(path);
  }, [path, setRoutePath]);

  function handleClick(event) {
    if (!isPlainLeftClick(event)) return;
    const anchor = event.target.closest?.("a[href]");
    if (!anchor || anchor.target || anchor.hasAttribute("download")) return;
    const url = new URL(anchor.href, window.location.href);
    if (url.origin !== window.location.origin) return;
    if (!isCitizenAssistantRoute(url.pathname)) return;
    event.preventDefault();
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
    onNavigate(url.pathname);
    if (url.hash) {
      window.requestAnimationFrame(() => {
        document.querySelector(url.hash)?.scrollIntoView?.({ behavior: "smooth", block: "start" });
      });
    }
  }

  return (
    <div className="citizen-chatbot-layout" onClick={handleClick}>
      <SpotlightCard as="header" className="citizen-portal-toolbar" spotlightColor="rgba(23, 104, 78, 0.12)">
        <div>
          <p className="eyebrow">Citizen Portal</p>
          <h1>NiyamGuard Services</h1>
        </div>
        <nav className="citizen-portal-nav" aria-label="Citizen portal">
          {citizenNavItems.map((item) => (
            <a
              className={path === item.href || path.startsWith(`${item.href}/`) ? "active" : ""}
              href={item.href}
              key={item.href}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </SpotlightCard>
      <CitizenAssistantHost />
      <div className="citizen-chatbot-page">{children}</div>
    </div>
  );
}

export default function CitizenAssistantLayout({ children, onNavigate, path }) {
  return (
    <CitizenAssistantProvider>
      <CitizenAssistantLayoutInner onNavigate={onNavigate} path={path}>
        {children}
      </CitizenAssistantLayoutInner>
    </CitizenAssistantProvider>
  );
}
