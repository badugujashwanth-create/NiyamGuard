import { useEffect, useMemo, useState } from "react";

import CitizenAssistantLayout, { isCitizenAssistantRoute } from "../citizen-portal/components/CitizenAssistantLayout";
import DynamicFormPage from "../citizen-portal/components/DynamicFormPage";
import AdminPortal from "../government-portal/components/AdminPortal";
import DemoDashboard from "../government-portal/components/DemoDashboard";
import { MockMeeSevaPortal, MockPublicFaq } from "../government-portal/components/MockConnectedSystems";
import CitizenPortal from "../citizen-portal/components/CitizenPortal";
import GovernmentPortal from "../government-portal/components/GovernmentPortal";
import SchemeFinder from "../citizen-portal/components/SchemeFinder";
import ServicePortal from "../citizen-portal/components/ServicePortal";
import ServiceCatalog from "../citizen-portal/components/ServiceCatalog";
import UnifiedLanding from "../shared/components/UnifiedLanding";
import VirtualGovernmentSandbox from "../government-portal/components/VirtualGovernmentSandbox";
import { useCitizenAssistant, useCitizenAssistantPageContext } from "../citizen-portal/context/CitizenAssistantContext";
import {
  askAssistant,
  generateSummary,
  getAccessToken,
  getForm,
  getForms,
  getStoredUser,
  login as loginAdmin,
  logout as logoutAdmin,
  searchServices,
} from "../services/api";

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
        <p className="login-hint">
          Demo admin: admin@niyamguard.local / Admin@12345<br />
          Citizen: citizen@niyamguard.local / Citizen@12345<br />
          Officer: officer@niyamguard.local / Officer@12345
        </p>
        <div className="login-links">
          <a href="/demo">Open public demo</a>
          <a href="/">Open citizen portal</a>
        </div>
      </section>
    </main>
  );
}

function CitizenApp() {
  const assistant = useCitizenAssistant();
  const [services, setServices] = useState([]);
  const [catalogStatus, setCatalogStatus] = useState("loading");
  const [catalogReply, setCatalogReply] = useState(null);
  const [catalogAsking, setCatalogAsking] = useState(false);

  const [selectedForm, setSelectedForm] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [uploadedDocuments, setUploadedDocuments] = useState({});
  const [currentField, setCurrentField] = useState("");
  const [currentDocument, setCurrentDocument] = useState("");
  const [lastVisibleSection, setLastVisibleSection] = useState("");
  const [globalError, setGlobalError] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);

  useEffect(() => {
    let active = true;
    async function initializeCatalog() {
      setCatalogStatus("loading");
      try {
        const formsResponse = await getForms();
        if (!active) return;
        setServices(formsResponse.forms || []);
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

  const pageContext = useMemo(
    () => ({
      mode: selectedForm ? "form" : "catalog",
      routePath: "/citizen/assistant",
      formId: activeFormId,
      serviceName: selectedForm?.service_name || "Guided Service Catalog",
      formFields: selectedForm?.fields || [],
      requiredDocuments: selectedForm?.required_documents || [],
      activeField: currentField,
      activeDocument: currentDocument,
      lastVisibleSection: lastVisibleSection || (selectedForm ? "details" : "catalog"),
    }),
    [activeFormId, currentDocument, currentField, lastVisibleSection, selectedForm],
  );

  useCitizenAssistantPageContext(pageContext);

  async function startApplication(formId) {
    setGlobalError("");
    const service = services.find((item) => item.form_id === formId);
    if (service && (service.status === "catalog_only" || service.has_detailed_schema === false)) {
      setGlobalError("Detailed guided form coming soon for this service.");
      return;
    }
    try {
      const formResponse = await getForm(formId);
      const form = formResponse.form;
      setSelectedForm(form);
      setFormValues(emptyValuesFor(form));
      setUploadedDocuments({});
      setCurrentField("");
      setCurrentDocument("");
      setLastVisibleSection("details");
      window.scrollTo?.({ top: 0, behavior: "smooth" });
    } catch (error) {
      setGlobalError(error.message);
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
    setCatalogAsking(true);
    setGlobalError("");
    try {
      if (!assistant.sessionId) {
        setGlobalError("The assistant session is not ready.");
        return;
      }
      const response = await askAssistant({
        sessionId: assistant.sessionId,
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

  async function handleReview() {
    if (!assistant.sessionId || !selectedForm) return;
    setLoadingSummary(true);
    setGlobalError("");
    try {
      const response = await generateSummary({
        sessionId: assistant.sessionId,
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
      assistant.publishAssistantReply({
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

  function backToCatalog() {
    setSelectedForm(null);
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
        <main className="workspace workspace-single">
          <DynamicFormPage
            backendReady={assistant.sessionStatus === "ready"}
            form={selectedForm}
            language={assistant.lastDetectedLanguage}
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
    const next = new URLSearchParams(window.location.search).get("next");
    if (next) {
      navigate(next);
      return;
    }
    if (user?.role === "citizen") {
      navigate("/services");
      return;
    }
    if (user?.email === "officer@niyamguard.local" || user?.role === "reviewer") {
      navigate("/officer");
      return;
    }
    navigate("/admin");
  }

  function renderCitizenContent() {
    if (path === "/citizen") return <CitizenPortal />;
    if (path.startsWith("/citizen/assistant")) return <CitizenApp />;
    if (path.startsWith("/scheme-finder")) {
      return (
        <SchemeFinder
          onStartForm={(formId) => {
            navigate(`/apply/${formId}`);
          }}
        />
      );
    }
    return <ServicePortal path={window.location.pathname} />;
  }

  if (path === "/" || path.startsWith("/portal")) return <UnifiedLanding />;
  if (isCitizenAssistantRoute(path)) {
    return (
      <CitizenAssistantLayout onNavigate={setPath} path={path}>
        {renderCitizenContent()}
      </CitizenAssistantLayout>
    );
  }
  if (path.startsWith("/government")) return <GovernmentPortal />;
  if (path.startsWith("/demo")) return <DemoDashboard />;
  if (path.startsWith("/mock/meeseva")) return <MockMeeSevaPortal />;
  if (path.startsWith("/mock/public-faq")) return <MockPublicFaq />;
  if (path.startsWith("/virtual-gov")) return <VirtualGovernmentSandbox />;
  if (path.startsWith("/officer")) {
    return <ServicePortal path={window.location.pathname} />;
  }
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
