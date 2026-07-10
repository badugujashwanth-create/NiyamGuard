import { useEffect } from "react";

import { CitizenAssistantProvider, useCitizenAssistant } from "../context/CitizenAssistantContext";
import VoiceAssistantPanel from "./VoiceAssistantPanel";

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
    path.startsWith("/verify-certificate") ||
    path.startsWith("/payment")
  );
}

function isPlainLeftClick(event) {
  return event.button === 0 && !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;
}

function CitizenAssistantHost() {
  const assistant = useCitizenAssistant();

  return (
    <section
      className="global-citizen-assistant"
      id="global-citizen-voice-assistant"
      aria-label="Citizen voice assistant"
    >
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
    </section>
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
    <div className="citizen-assistant-layout" onClick={handleClick}>
      <CitizenAssistantHost />
      <div className="citizen-assistant-page">{children}</div>
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
