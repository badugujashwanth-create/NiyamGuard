import { useCallback, useEffect, useMemo, useState } from "react";

import DynamicFormPage from "./components/DynamicFormPage";
import AdminPortal from "./components/AdminPortal";
import ServiceCatalog from "./components/ServiceCatalog";
import VoiceAssistantPanel from "./components/VoiceAssistantPanel";
import {
  askAssistant,
  createSession,
  generateSummary,
  getForm,
  getForms,
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
  const isAdminPath = window.location.pathname.startsWith("/admin");
  return isAdminPath ? <AdminPortal /> : <CitizenApp />;
}
