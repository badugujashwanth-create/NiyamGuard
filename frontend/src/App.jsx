import { useCallback, useEffect, useMemo, useState } from "react";

import DynamicFormPage from "./components/DynamicFormPage";
import AdminPortal from "./components/AdminPortal";
import DemoDashboard from "./components/DemoDashboard";
import ServiceCatalog from "./components/ServiceCatalog";
import VoiceAssistantPanel from "./components/VoiceAssistantPanel";
import {
  askAssistant,
  askChat,
  createSession,
  generateSummary,
  getAccessToken,
  getForm,
  getForms,
  getLatestPublicRule,
  getStoredUser,
  login as loginAdmin,
  logout as logoutAdmin,
  reverseLocation,
  searchServices,
} from "./services/api";

function message(role, text) {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text,
  };
}

function emptyValuesFor(form) {
  return Object.fromEntries(
    form.fields.map((field) => [field.key, field.type === "checkbox" ? false : ""]),
  );
}

function publicDocumentState(uploadedDocuments) {
  return Object.fromEntries(
    Object.entries(uploadedDocuments).map(([key, value]) => [
      key,
      value
        ? {
            name: value.name,
            size: value.size,
            type: value.type,
            uploaded: Boolean(value.uploaded && !value.error),
          }
        : null,
    ]),
  );
}

function detectQuestionLanguage(text) {
  const normalized = text.toLowerCase();
  if (/[\u0c00-\u0c7f]/.test(text) || /\b(entha|enti|aa|kavali|cheppandi|lo|kosam)\b/.test(normalized)) {
    return { detected_language: "telugu", language_code: "te-IN" };
  }
  if (/[\u0900-\u097f]/.test(text) || /\b(kya|kitne|hai|abhi|bataiye|anusaar|ke liye)\b/.test(normalized)) {
    return { detected_language: "hindi", language_code: "hi-IN" };
  }
  return { detected_language: "english", language_code: "en-IN" };
}

function isIncomeValidityQuestion(text, formId) {
  const normalized = text.toLowerCase();
  const mentionsValidity =
    /\b(validity|valid|months?|rule|entha)\b/.test(normalized) ||
    /validity|valid/.test(normalized);
  const mentionsIncomeCertificate =
    /\b(income certificate|certificate|income)\b/.test(normalized) ||
    formId === "income_certificate";
  return mentionsValidity && mentionsIncomeCertificate;
}

function formatVerifiedRuleReply(ruleResponse, language) {
  const source = ruleResponse.source || {};
  const circular = source.circular_number || "source not available";
  const department = source.department || "department not available";
  const value = valueFromRuleResponse(ruleResponse);
  if (!ruleResponse?.verified) {
    if (language.detected_language === "telugu") {
      return "Verified rule source dorakaledu. Dayachesi official government source nunchi verify cheyyandi.";
    }
    if (language.detected_language === "hindi") {
      return "Verified rule source available nahi hai. Kripya official government source se verify karein.";
    }
    return "Verified rule source is not available. Please verify from the official government source.";
  }
  if (language.detected_language === "telugu") {
    return `ప్రస్తుత verified rule ప్రకారం Income Certificate validity ${value}. Source: ${circular}, ${department} Department.`;
  }
  if (language.detected_language === "hindi") {
    return `Verified rule के अनुसार Income Certificate validity अभी ${value} है. Source: ${circular}, ${department} Department.`;
  }
  return `According to the verified rule, Income Certificate validity is currently ${value}. Source: ${circular}, ${department} Department.`;
}

function valueFromRuleResponse(ruleResponse) {
  const answer = ruleResponse?.answer || "";
  const match = answer.match(/currently\s+(.+?)\.?$/i);
  return match?.[1]?.replace(/\.$/, "") || "source not available";
}

function sourceCardFromRule(ruleResponse) {
  const source = ruleResponse?.source;
  if (!source) return null;
  return {
    circular: source.circular_number,
    department: source.department,
    rule: "Income Certificate Validity",
    currentValue: valueFromRuleResponse(ruleResponse),
    confidence: source.confidence,
    effectiveDate: source.effective_date,
    sourceType: "verified_rule",
    verified: true,
    provider: "deterministic",
    whySelected: "Matched income certificate validity against the latest verified public rule.",
  };
}

function titleCase(value = "") {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isCitizenKnowledgeQuestion(text, formId) {
  const normalized = text.toLowerCase();
  const asksFormFieldHelp =
    /\b(purpose|monthly income|field|box|mandal|pincode|what should i enter|rayacha|likhna)\b/.test(
      normalized,
    ) && !/\b(document|documents|docs|eligib|process|apply|validity|fee|timeline|old rule|new rule)\b/.test(normalized);
  if (asksFormFieldHelp) return false;

  const hasIntent = /\b(document|documents|docs|proof|eligib|qualify|process|apply|steps|validity|valid|fee|cost|timeline|days|old rule|new rule|compare|which service|which form)\b/.test(
    normalized,
  ) || /\b(enti|entha|kavali|kaise|kya)\b/.test(normalized);
  const hasKnownService =
    /\b(income certificate|residence certificate|caste certificate|community certificate|ews|scholarship|post matric|pension|old age|widow|disability|birth certificate|death certificate|family member|ration card|food security)\b/.test(
      normalized,
    ) || formId !== "catalog";

  return hasIntent && hasKnownService;
}

function sourceCardFromChat(chatResponse) {
  const firstReference = chatResponse?.source?.references?.[0] || {};
  return {
    circular:
      firstReference.circular_number ||
      firstReference.source_label ||
      firstReference.label ||
      chatResponse?.source?.label ||
      "NiyamGuard Knowledge Base",
    department: firstReference.department || "Citizen Services Knowledge",
    rule: titleCase(chatResponse?.intent || "Citizen Knowledge"),
    currentValue:
      firstReference.current_value ||
      titleCase(chatResponse?.scheme_or_service || chatResponse?.source?.type || "Guidance"),
    confidence: chatResponse?.confidence,
    effectiveDate: firstReference.effective_date,
    lastUpdated: firstReference.last_updated,
    sourceType: chatResponse?.source?.type,
    sourceSourceType: firstReference.source_type,
    verified: Boolean(chatResponse?.verified),
    provider: chatResponse?.provider,
    fallback: Boolean(chatResponse?.fallback),
    whySelected: `Matched this question to ${titleCase(chatResponse?.intent || "knowledge")} guidance for ${titleCase(chatResponse?.scheme_or_service || "citizen services")}.`,
  };
}

function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState("admin@niyamguard.local");
  const [password, setPassword] = useState("Admin@12345");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const response = await loginAdmin(email, password);
      onLoginSuccess(response.user);
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-brand">
          <span className="brand-emblem" aria-hidden="true">NG</span>
          <div>
            <p>Secure government access</p>
            <h1 id="login-title">NiyamGuard Admin Login</h1>
          </div>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          <label htmlFor="admin-email">Email</label>
          <input
            autoComplete="username"
            id="admin-email"
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            value={email}
          />
          <label htmlFor="admin-password">Password</label>
          <input
            autoComplete="current-password"
            id="admin-password"
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            value={password}
          />
          {error ? <p className="login-error" role="alert">{error}</p> : null}
          <button className="button button-primary" disabled={submitting} type="submit">
            {submitting ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="login-hint">Demo admin: admin@niyamguard.local / Admin@12345</p>
        <div className="login-links">
          <a href="/demo">Open public demo</a>
          <a href="/">Open citizen portal</a>
        </div>
      </section>
    </main>
  );
}

function CitizenApp() {
  const [services, setServices] = useState([]);
  const [catalogStatus, setCatalogStatus] = useState("loading");
  const [catalogSessionId, setCatalogSessionId] = useState("");
  const [catalogReply, setCatalogReply] = useState(null);
  const [catalogAsking, setCatalogAsking] = useState(false);

  const [selectedForm, setSelectedForm] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [uploadedDocuments, setUploadedDocuments] = useState({});
  const [currentField, setCurrentField] = useState("");
  const [currentDocument, setCurrentDocument] = useState("");
  const [lastVisibleSection, setLastVisibleSection] = useState("");
  const [lastDetectedLanguage, setLastDetectedLanguage] = useState("english");
  const [lastLanguageCode, setLastLanguageCode] = useState("en-IN");
  const [sessionId, setSessionId] = useState("");
  const [sessionStatus, setSessionStatus] = useState("idle");
  const [globalError, setGlobalError] = useState("");
  const [messages, setMessages] = useState([]);
  const [assistantReply, setAssistantReply] = useState(null);
  const [speechCommand, setSpeechCommand] = useState(null);
  const [asking, setAsking] = useState(false);
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    let active = true;
    async function initializeCatalog() {
      setCatalogStatus("loading");
      try {
        const [formsResponse, sessionResponse] = await Promise.all([
          getForms(),
          createSession("auto", "catalog"),
        ]);
        if (!active) return;
        setServices(formsResponse.forms || []);
        setCatalogSessionId(sessionResponse.session_id);
        setCatalogStatus("ready");
      } catch (error) {
        if (!active) return;
        setGlobalError(error.message);
        setCatalogStatus("error");
      }
    }
    void initializeCatalog();
    return () => {
      active = false;
    };
  }, []);

  const completion = useMemo(() => {
    if (!selectedForm?.fields?.length) return 0;
    const completed = selectedForm.fields.filter((field) => {
      const value = formValues[field.key];
      return typeof value === "boolean" ? value : Boolean(value?.toString().trim());
    }).length;
    return Math.round((completed / selectedForm.fields.length) * 100);
  }, [formValues, selectedForm]);

  const activeFormId = selectedForm?.form_id || "catalog";

  function applyAssistantResponse(response) {
    const safeResponse = {
      ...response,
      suggested_value:
        response.auto_fill === false ? response.suggested_value : null,
      detected_language: response.detected_language || "english",
      language_code: response.language_code || "en-IN",
    };
    setAssistantReply(safeResponse);
    setLastDetectedLanguage(safeResponse.detected_language);
    setLastLanguageCode(safeResponse.language_code);
    setMessages((current) => [
      ...current,
      message("assistant", safeResponse.reply),
    ]);
    setSpeechCommand({
      id: `${Date.now()}-${Math.random()}`,
      text: safeResponse.reply,
      languageCode: safeResponse.language_code,
      detectedLanguage: safeResponse.detected_language,
    });
    return safeResponse;
  }

  async function startApplication(formId) {
    setGlobalError("");
    const service = services.find((item) => item.form_id === formId);
    if (service && (service.status === "catalog_only" || service.has_detailed_schema === false)) {
      setGlobalError("Detailed guided form coming soon for this service.");
      return;
    }
    setSessionStatus("loading");
    try {
      const [formResponse, sessionResponse] = await Promise.all([
        getForm(formId),
        createSession("auto", formId),
      ]);
      const form = formResponse.form;
      setSelectedForm(form);
      setFormValues(emptyValuesFor(form));
      setUploadedDocuments({});
      setCurrentField("");
      setCurrentDocument("");
      setLastVisibleSection("details");
      setLastDetectedLanguage("english");
      setLastLanguageCode("en-IN");
      setMessages([]);
      setAssistantReply(null);
      setSpeechCommand(null);
      setSessionId(sessionResponse.session_id);
      setSessionStatus("ready");
      window.scrollTo?.({ top: 0, behavior: "smooth" });
    } catch (error) {
      setGlobalError(error.message);
      setSessionStatus("error");
    }
  }

  async function handleCatalogSearch(query) {
    try {
      const response = await searchServices(query);
      setServices(response.services || []);
    } catch (error) {
      setGlobalError(error.message);
    }
  }

  async function handleCatalogAsk(text) {
    if (!catalogSessionId) return;
    setCatalogAsking(true);
    setGlobalError("");
    try {
      const response = await askAssistant({
        sessionId: catalogSessionId,
        formId: "catalog",
        message: text,
        language: "auto",
      });
      setCatalogReply(response);
    } catch (error) {
      setGlobalError(error.message);
    } finally {
      setCatalogAsking(false);
    }
  }

  async function handleAsk(text) {
    if (!sessionId) {
      setGlobalError("The assistant session is not ready.");
      return null;
    }
    setAsking(true);
    setGlobalError("");
    setMessages((current) => [...current, message("user", text)]);
    try {
      if (isIncomeValidityQuestion(text, activeFormId)) {
        const language = detectQuestionLanguage(text);
        try {
          const ruleResponse = await getLatestPublicRule(
            "income_certificate",
            "validity",
          );
          return applyAssistantResponse({
            success: Boolean(ruleResponse.success),
            field: null,
            reply: formatVerifiedRuleReply(ruleResponse, language),
            suggested_value: null,
            related_values: {},
            location_matches: [],
            warning: ruleResponse.source
              ? null
              : "Source not available. Please verify from official government source.",
            detected_language: language.detected_language,
            language_code: language.language_code,
            auto_fill: false,
            should_submit: false,
            verified_rule: true,
            verified_source: sourceCardFromRule(ruleResponse),
          });
        } catch (ruleError) {
          return applyAssistantResponse({
            success: false,
            field: null,
            reply: formatVerifiedRuleReply({ verified: false }, language),
            suggested_value: null,
            related_values: {},
            location_matches: [],
            warning: ruleError.message,
            detected_language: language.detected_language,
            language_code: language.language_code,
            auto_fill: false,
            should_submit: false,
            verified_rule: true,
            verified_source: null,
          });
        }
      }
      if (isCitizenKnowledgeQuestion(text, activeFormId)) {
        const chatResponse = await askChat({
          message: text,
          language: "auto",
          context: {
            service_id: activeFormId === "catalog" ? undefined : activeFormId,
            form_id: activeFormId,
          },
          profile: {},
        });
        return applyAssistantResponse({
          success: Boolean(chatResponse.success),
          field: null,
          reply: chatResponse.answer,
          suggested_value: null,
          related_values: {},
          location_matches: [],
          warning: chatResponse.fallback
            ? "No verified source was available for this question."
            : null,
          detected_language: chatResponse.language || "english",
          language_code: chatResponse.language_code || "en-IN",
          auto_fill: false,
          should_submit: false,
          verified_rule: true,
          verified_source: sourceCardFromChat(chatResponse),
        });
      }
      const response = await askAssistant({
        sessionId,
        formId: activeFormId,
        message: text,
        currentField,
        currentDocument,
        lastVisibleSection,
        language: "auto",
      });
      return applyAssistantResponse(response);
    } catch (error) {
      setGlobalError(error.message);
      const errorReply =
        "I could not contact the guidance service. Please try again.";
      setAssistantReply({
        reply: errorReply,
        warning: error.message,
        detected_language: "english",
        language_code: "en-IN",
      });
      setMessages((current) => [...current, message("assistant", errorReply)]);
      return null;
    } finally {
      setAsking(false);
    }
  }

  async function handleReview() {
    if (!sessionId || !selectedForm) return;
    setLoadingSummary(true);
    setGlobalError("");
    try {
      const response = await generateSummary({
        sessionId,
        formId: selectedForm.form_id,
        formValues,
        uploadedDocuments: publicDocumentState(uploadedDocuments),
        language: "auto",
      });
      const missingDocs = response.missing_documents?.length
        ? ` Missing documents: ${response.missing_documents.join(", ")}.`
        : "";
      const warningText = response.warnings?.length
        ? ` ${response.warnings.join(" ")}`
        : "";
      const reply = `${response.summary}${missingDocs}${warningText}`.trim();
      applyAssistantResponse({
        reply,
        warning: response.warnings?.length ? response.warnings.join(" ") : null,
        detected_language: response.detected_language,
        language_code: response.language_code || "en-IN",
        auto_fill: false,
        should_submit: false,
      });
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
    setLastDetectedLanguage("english");
    setLastLanguageCode("en-IN");
    if (selectedForm) {
      try {
        const session = await createSession("auto", selectedForm.form_id);
        setSessionId(session.session_id);
        setSessionStatus("ready");
      } catch (error) {
        setGlobalError(error.message);
        setSessionStatus("error");
      }
    }
  }

  async function handleUseLocation({ latitude, longitude }) {
    setGlobalError("");
    try {
      const response = await reverseLocation({
        latitude,
        longitude,
        language: lastDetectedLanguage || "auto",
      });
      applyAssistantResponse(response);
      return response;
    } catch (error) {
      setGlobalError(error.message);
      return null;
    }
  }

  function backToCatalog() {
    setSelectedForm(null);
    setSessionId("");
    setSessionStatus("idle");
    setMessages([]);
    setAssistantReply(null);
    setSpeechCommand(null);
    setCurrentField("");
    setCurrentDocument("");
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand">
          <span className="brand-emblem" aria-hidden="true">
            NG
          </span>
          <div>
            <p>Citizen Assistance Service</p>
            <h1>NiyamGuard</h1>
          </div>
        </div>
        <div className="progress-summary" aria-label={`${completion}% form completed`}>
          <span>{selectedForm ? "Form progress" : "Catalog ready"}</span>
          <strong>{selectedForm ? `${completion}%` : services.length}</strong>
          <div>
            <span style={{ width: selectedForm ? `${completion}%` : "100%" }} />
          </div>
        </div>
      </header>

      {globalError ? (
        <div className="global-error" role="alert">
          <span>{globalError}</span>
          <button onClick={() => setGlobalError("")} type="button">
            Dismiss
          </button>
        </div>
      ) : null}

      {selectedForm ? (
        <main className="workspace">
          <DynamicFormPage
            backendReady={sessionStatus === "ready"}
            form={selectedForm}
            language={lastDetectedLanguage}
            loadingSummary={loadingSummary}
            onBack={backToCatalog}
            onDocumentChange={(key, value) =>
              setUploadedDocuments((current) => ({
                ...current,
                [key]: value,
              }))
            }
            onFieldFocus={(field) => {
              if (field.startsWith("document:")) {
                setCurrentDocument(field.split(":", 2)[1]);
                setLastVisibleSection("documents");
              } else {
                setCurrentField(field);
                setCurrentDocument("");
                setLastVisibleSection("details");
              }
            }}
            onReview={() => void handleReview()}
            onValueChange={(field, value) =>
              setFormValues((current) => ({ ...current, [field]: value }))
            }
            uploadedDocuments={uploadedDocuments}
            values={formValues}
          />
          <VoiceAssistantPanel
            asking={asking}
            assistantReply={assistantReply}
            lastDetectedLanguage={lastDetectedLanguage}
            lastLanguageCode={lastLanguageCode}
            messages={messages}
            onAsk={handleAsk}
            onClear={handleClear}
            onReview={() => void handleReview()}
            onUseLocation={handleUseLocation}
            sessionId={sessionId}
            formId={activeFormId}
            activeField={currentField}
            activeDocument={currentDocument}
            sessionStatus={sessionStatus}
            speechCommand={speechCommand}
          />
        </main>
      ) : (
        <ServiceCatalog
          assistantReply={catalogReply}
          asking={catalogAsking}
          loading={catalogStatus === "loading"}
          onAskCatalog={handleCatalogAsk}
          onSearch={handleCatalogSearch}
          onStart={(formId) => void startApplication(formId)}
          services={services}
        />
      )}

      <footer>
        The assistant guides the citizen but does not submit the application.
        The citizen remains in control.
      </footer>
    </div>
  );
}

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());

  useEffect(() => {
    function handlePopState() {
      setPath(window.location.pathname);
    }
    function handleAuthChanged(event) {
      setCurrentUser(event.detail?.user || getStoredUser());
    }
    window.addEventListener("popstate", handlePopState);
    window.addEventListener("niyamguard:auth-changed", handleAuthChanged);
    return () => {
      window.removeEventListener("popstate", handlePopState);
      window.removeEventListener("niyamguard:auth-changed", handleAuthChanged);
    };
  }, []);

  useEffect(() => {
    if (path.startsWith("/admin") && !getAccessToken()) {
      window.history.replaceState({}, "", "/login");
      setPath("/login");
    }
  }, [path, currentUser]);

  function navigate(nextPath) {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  }

  async function handleLogout() {
    await logoutAdmin().catch(() => {});
    setCurrentUser(null);
    navigate("/login");
  }

  function handleLoginSuccess(user) {
    setCurrentUser(user);
    navigate("/admin");
  }

  if (path.startsWith("/demo")) return <DemoDashboard />;
  if (path.startsWith("/login")) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }
  if (path.startsWith("/admin")) {
    return (
      <AdminPortal
        currentUser={currentUser}
        onLogout={handleLogout}
        onUnauthorized={() => navigate("/login")}
      />
    );
  }
  return <CitizenApp />;
}
