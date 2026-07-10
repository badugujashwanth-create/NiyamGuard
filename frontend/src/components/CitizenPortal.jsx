import { useState } from "react";

import { askHybridDemoQuestion } from "../services/api";
import VoiceAssistantPanel from "./VoiceAssistantPanel";

function message(role, text) {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text,
  };
}

const citizenActions = [
  {
    title: "Browse Services",
    description: "See available citizen services and requirements.",
    href: "/services",
    action: "Open Services",
  },
  {
    title: "Apply for Service",
    description: "Start the Income Certificate application flow.",
    href: "/apply/income_certificate",
    action: "Apply Income Certificate",
  },
  {
    title: "My Applications",
    description: "Review submitted applications and certificates.",
    href: "/applications",
    action: "Open My Applications",
  },
  {
    title: "Track Application",
    description: "Track a submitted application number.",
    href: "/track",
    action: "Track Application",
  },
  {
    title: "Verify Certificate",
    description: "Verify a certificate number or hash.",
    href: "/verify-certificate",
    action: "Verify Certificate",
  },
  {
    title: "Citizen Assistant / Hybrid Answer Engine",
    description: "Ask questions and receive source-backed answers.",
    href: "/citizen/assistant",
    action: "Open Assistant",
  },
  {
    title: "Find Possible Services",
    description: "Answer simple questions to find matching services.",
    href: "/scheme-finder",
    action: "Open Scheme Finder",
  },
];

const assistantChips = [
  "income certificate validity entha",
  "What documents are needed for income certificate?",
  "How do I track my application?",
  "Certificate verify kaise kare?",
];

export default function CitizenPortal() {
  const [question, setQuestion] = useState("income certificate validity entha");
  const [answer, setAnswer] = useState(null);
  const [assistantReply, setAssistantReply] = useState(null);
  const [messages, setMessages] = useState([]);
  const [speechCommand, setSpeechCommand] = useState(null);
  const [asking, setAsking] = useState(false);
  const [lastDetectedLanguage, setLastDetectedLanguage] = useState("english");
  const [lastLanguageCode, setLastLanguageCode] = useState("en-IN");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");

  function sourceCardFromHybrid(response) {
    const source = response.sources?.[0] || response.source || {};
    const metadata = source.metadata || {};
    return {
      method: response.method,
      provider: response.provider,
      sourceType: source.type || "verified_rule",
      verified: Boolean(response.verified || source.verified),
      circular: source.circular_number || metadata.circular_number || source.label || "GO-138",
      department: source.department || metadata.department || "Revenue",
      rule: source.rule_key || "Income Certificate Validity",
      currentValue: source.value || "6 months",
      confidence: source.confidence || metadata.confidence || response.confidence,
      effectiveDate: source.effective_date || metadata.effective_date,
      whySelected: "Selected because the question asks about the verified income certificate validity rule.",
    };
  }

  function applyAssistantResponse(response, userText = "") {
    const reply = {
      success: Boolean(response.success),
      reply: response.answer || response.reply || "No answer returned.",
      warning: response.fallback ? "Fallback answer used. Verify critical details from official sources." : null,
      detected_language: response.language || "english",
      language_code: response.language_code || "en-IN",
      verified_rule: Boolean(response.verified || response.sources?.length || response.source),
      verified_source: sourceCardFromHybrid(response),
    };
    setAnswer(response);
    setAssistantReply(reply);
    setLastDetectedLanguage(reply.detected_language);
    setLastLanguageCode(reply.language_code);
    setMessages((current) => [
      ...current,
      ...(userText ? [message("user", userText)] : []),
      message("assistant", reply.reply),
    ]);
    setSpeechCommand({
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      text: reply.reply,
      detectedLanguage: reply.detected_language,
      languageCode: reply.language_code,
    });
    return reply;
  }

  async function askCitizenAssistant(text) {
    const cleaned = text.trim();
    if (!cleaned) return null;
    setAsking(true);
    setStatus("Asking assistant...");
    setError("");
    try {
      const response = await askHybridDemoQuestion(cleaned);
      const reply = applyAssistantResponse(response, cleaned);
      setStatus("Source-backed answer returned.");
      return reply;
    } catch (assistantError) {
      setStatus("");
      setError(assistantError.message);
      const reply = {
        reply: "I could not contact the guidance service. Please try again.",
        warning: assistantError.message,
        detected_language: "english",
        language_code: "en-IN",
      };
      setAssistantReply(reply);
      setMessages((current) => [...current, message("assistant", reply.reply)]);
      return null;
    } finally {
      setAsking(false);
    }
  }

  async function handleAskAssistant(event) {
    event.preventDefault();
    setAnswer(null);
    await askCitizenAssistant(question);
  }

  async function handleUseLocation() {
    const reply = {
      success: true,
      answer: "Location lookup is optional in this demo. You can type your pincode or continue with text guidance.",
      language: lastDetectedLanguage,
      language_code: lastLanguageCode,
      method: "safe_fallback",
      provider: "deterministic",
      verified: false,
      fallback: true,
      source: {
        type: "safe_fallback",
        label: "Citizen demo guidance",
        verified: false,
      },
    };
    return applyAssistantResponse(reply);
  }

  return (
    <main className="unified-shell citizen-portal-shell">
      <section className="unified-banner" role="note">
        NiyamGuard citizen demo - Sandbox only. No official application is submitted.
      </section>

      <header className="unified-header citizen-portal-header">
        <div>
          <p className="eyebrow">Citizen Portal</p>
          <h1>Citizen Portal</h1>
          <p>
            Citizens can find services, apply online, upload documents, complete sandbox payment,
            track application status, verify certificate, and ask source-backed questions.
          </p>
        </div>
        <div className="unified-actions">
          <a className="button button-secondary" href="/">
            Back to Portals
          </a>
        </div>
      </header>

      <section className="citizen-quick-actions" aria-label="Citizen quick demo actions">
        <a className="button button-primary" href="/services">Open Services</a>
        <a className="button button-primary" href="/apply/income_certificate">Apply Income Certificate</a>
        <a className="button button-secondary" href="/track">Track Application</a>
        <a className="button button-secondary" href="/verify-certificate">Verify Certificate</a>
        <button className="button button-secondary" onClick={(event) => void handleAskAssistant(event)} type="button">
          Ask Assistant
        </button>
        <a className="button button-secondary" href="#citizen-voice-assistant">Start Voice Assistant</a>
      </section>

      {error ? <div className="global-error" role="alert">{error}</div> : null}

      <section className="citizen-voice-layout" id="citizen-voice-assistant" aria-label="Main Voice Assistant">
        <div className="unified-section-heading citizen-section-heading">
          <div>
            <p className="eyebrow">Main Voice Assistant</p>
            <h2>Apply for Certificates with Voice Assistant</h2>
          </div>
          <span className="unified-status unified-status-ready">Text fallback ready</span>
        </div>
        <VoiceAssistantPanel
          activeDocument=""
          activeField=""
          asking={asking}
          assistantReply={assistantReply}
          formId="income_certificate"
          lastDetectedLanguage={lastDetectedLanguage}
          lastLanguageCode={lastLanguageCode}
          messages={messages}
          onAsk={askCitizenAssistant}
          onUseLocation={handleUseLocation}
          sessionId="citizen-portal"
          sessionStatus="ready"
          speechCommand={speechCommand}
        />
        <article className="unified-result-panel citizen-voice-notes">
          <p className="eyebrow">Text Assistant Fallback</p>
          <h2>Voice is optional. Text always works.</h2>
          <p>
            The main assistant supports Telugu, Hindi, English, and common mixed-language
            questions. If browser speech is unavailable, use the text box in the assistant.
          </p>
          <div className="source-badges">
            <span>Verified Source</span>
            <span>GO-138</span>
            <span>Hybrid Answer Engine</span>
          </div>
        </article>
      </section>

      <section className="unified-grid citizen-feature-grid" aria-label="Citizen features">
        {citizenActions.map((item) => (
          <article className="unified-card" key={item.title}>
            <div className="unified-card-top">
              <h2>{item.title}</h2>
            </div>
            <p>{item.description}</p>
            <div className="unified-card-actions">
              <a className="button button-secondary" href={item.href}>{item.action}</a>
            </div>
          </article>
        ))}
      </section>

      <section className="unified-result-panel citizen-assistant-panel" aria-labelledby="citizen-assistant-title">
        <p className="eyebrow">Citizen Assistant / Hybrid Answer Engine</p>
        <h2 id="citizen-assistant-title">Ask a Source-Backed Question</h2>
        <div className="citizen-question-chips" aria-label="Source-backed citizen Q&A examples">
          {assistantChips.map((chip) => (
            <button
              className="button button-secondary"
              key={chip}
              onClick={() => {
                setQuestion(chip);
                void askCitizenAssistant(chip);
              }}
              type="button"
            >
              {chip}
            </button>
          ))}
        </div>
        <form className="citizen-assistant-form" onSubmit={(event) => void handleAskAssistant(event)}>
          <label htmlFor="citizen-question">Question</label>
          <div>
            <input
              id="citizen-question"
              onChange={(event) => setQuestion(event.target.value)}
              value={question}
            />
            <button className="button button-primary" type="submit">Ask Assistant</button>
          </div>
        </form>
        {status ? <p className="support-message">{status}</p> : null}
        {answer ? (
          <div className="unified-ai-output" data-testid="citizen-hybrid-output">
            <div className="source-badges">
              <span>{answer.method || "hybrid"}</span>
              <span>{answer.provider || "source-backed"}</span>
              {answer.verified ? <span>Verified Source</span> : null}
            </div>
            <p>{answer.answer}</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
