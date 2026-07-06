import { useCallback, useEffect, useMemo, useState } from "react";

import IncomeCertificateForm from "./components/IncomeCertificateForm";
import VoiceAssistantPanel from "./components/VoiceAssistantPanel";
import {
  askAssistant,
  createSession,
  generateSummary,
  getIncomeCertificateForm,
} from "./services/api";

const FALLBACK_FIELDS = [
  ["applicant_name", "Applicant Full Name", "text"],
  ["father_name", "Father Name", "text"],
  ["mobile_number", "Mobile Number", "phone"],
  ["aadhaar_number", "Aadhaar Number", "aadhaar"],
  ["district", "District", "text"],
  ["mandal", "Mandal", "text"],
  ["village", "Village", "text"],
  ["monthly_income", "Monthly Income", "number"],
  ["annual_income", "Annual Income", "number"],
  ["purpose", "Purpose of Certificate", "text"],
  ["address", "Address", "textarea"],
].map(([key, label, type]) => ({
  key,
  label,
  type,
  required: true,
  help: `Enter ${label.toLowerCase()} manually.`,
}));

function message(role, text) {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text,
  };
}

export default function App() {
  const [fields, setFields] = useState([]);
  const [formValues, setFormValues] = useState({});
  const [currentField, setCurrentField] = useState("");
  const [language, setLanguage] = useState("english");
  const [sessionId, setSessionId] = useState("");
  const [sessionStatus, setSessionStatus] = useState("loading");
  const [globalError, setGlobalError] = useState("");
  const [messages, setMessages] = useState([]);
  const [assistantReply, setAssistantReply] = useState(null);
  const [speechCommand, setSpeechCommand] = useState(null);
  const [asking, setAsking] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);

  const displayedFields = fields.length ? fields : FALLBACK_FIELDS;

  const initializeSession = useCallback(async (selectedLanguage = "english") => {
    setSessionStatus("loading");
    setGlobalError("");
    try {
      const session = await createSession(selectedLanguage);
      setSessionId(session.session_id);
      setSessionStatus("ready");
      return session.session_id;
    } catch (error) {
      setSessionId("");
      setSessionStatus("error");
      setGlobalError(error.message);
      return null;
    }
  }, []);

  useEffect(() => {
    let active = true;
    async function initialize() {
      const [formResult] = await Promise.allSettled([
        getIncomeCertificateForm(),
        initializeSession("english"),
      ]);
      if (!active) return;
      if (formResult.status === "fulfilled") {
        const loadedFields = formResult.value.form.fields;
        setFields(loadedFields);
        setFormValues(
          Object.fromEntries(loadedFields.map((field) => [field.key, ""])),
        );
      } else {
        setFields(FALLBACK_FIELDS);
        setFormValues(
          Object.fromEntries(FALLBACK_FIELDS.map((field) => [field.key, ""])),
        );
        setGlobalError((current) => current || formResult.reason.message);
      }
    }
    initialize();
    return () => {
      active = false;
    };
  }, [initializeSession]);

  const completion = useMemo(() => {
    if (!displayedFields.length) return 0;
    const completed = displayedFields.filter((field) =>
      formValues[field.key]?.toString().trim(),
    ).length;
    return Math.round((completed / displayedFields.length) * 100);
  }, [displayedFields, formValues]);

  async function handleAsk(text) {
    if (!sessionId) {
      setGlobalError("The assistant session is not ready.");
      return;
    }
    setAsking(true);
    setGlobalError("");
    setMessages((current) => [...current, message("user", text)]);
    try {
      const response = await askAssistant({
        sessionId,
        message: text,
        currentField,
        language,
      });
      const safeResponse = {
        ...response,
        suggested_value: response.auto_fill === false ? response.suggested_value : null,
      };
      setAssistantReply(safeResponse);
      setMessages((current) => [
        ...current,
        message("assistant", safeResponse.reply),
      ]);
      setSpeechCommand({ id: Date.now(), text: safeResponse.reply });
      return safeResponse;
    } catch (error) {
      setGlobalError(error.message);
      const errorReply = "I could not contact the guidance service. Please try again.";
      setAssistantReply({ reply: errorReply, warning: error.message });
      setMessages((current) => [...current, message("assistant", errorReply)]);
      return null;
    } finally {
      setAsking(false);
    }
  }

  async function handleReview() {
    if (!sessionId) return;
    setLoadingSummary(true);
    setGlobalError("");
    try {
      const response = await generateSummary(sessionId, formValues);
      const warningText = response.warnings.length
        ? ` ${response.warnings.join(" ")}`
        : "";
      const reply = `${response.summary}${warningText}`.trim();
      const summaryReply = {
        reply,
        warning: response.warnings.length ? response.warnings.join(" ") : null,
      };
      setAssistantReply(summaryReply);
      setMessages((current) => [...current, message("assistant", reply)]);
      setSpeechCommand({ id: Date.now(), text: reply });
    } catch (error) {
      setGlobalError(error.message);
    } finally {
      setLoadingSummary(false);
    }
  }

  async function handleClear() {
    setMessages([]);
    setAssistantReply(null);
    setSpeechCommand(null);
    await initializeSession(language);
  }

  async function handleLanguageChange(nextLanguage) {
    setLanguage(nextLanguage);
    setMessages([]);
    setAssistantReply(null);
    setSpeechCommand(null);
    await initializeSession(nextLanguage);
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand">
          <span className="brand-emblem" aria-hidden="true">
            नियम
          </span>
          <div>
            <p>Citizen Assistance Service</p>
            <h1>NiyamGuard</h1>
          </div>
        </div>
        <div className="progress-summary" aria-label={`${completion}% form completed`}>
          <span>Form progress</span>
          <strong>{completion}%</strong>
          <div>
            <span style={{ width: `${completion}%` }} />
          </div>
        </div>
      </header>

      {globalError ? (
        <div className="global-error" role="alert">
          <span>{globalError}</span>
          {sessionStatus === "error" ? (
            <button onClick={() => initializeSession(language)} type="button">
              Retry connection
            </button>
          ) : null}
        </div>
      ) : null}

      <main className="workspace">
        <IncomeCertificateForm
          backendReady={sessionStatus === "ready"}
          fields={displayedFields}
          loadingSummary={loadingSummary}
          onFieldFocus={setCurrentField}
          onReview={handleReview}
          onValueChange={(field, value) =>
            setFormValues((current) => ({ ...current, [field]: value }))
          }
          values={formValues}
        />
        <VoiceAssistantPanel
          asking={asking}
          assistantReply={assistantReply}
          currentField={currentField}
          fields={displayedFields}
          language={language}
          messages={messages}
          onAsk={handleAsk}
          onClear={handleClear}
          onCurrentFieldChange={setCurrentField}
          onLanguageChange={handleLanguageChange}
          sessionStatus={sessionStatus}
          speechCommand={speechCommand}
        />
      </main>

      <footer>
        NiyamGuard provides guidance only. Always verify your details before using
        an official government portal.
      </footer>
    </div>
  );
}
