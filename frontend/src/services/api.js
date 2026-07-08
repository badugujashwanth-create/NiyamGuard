const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
export const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(message, status = 0, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
  } catch (error) {
    throw new ApiError(
      "Cannot reach the assistant backend. Check that FastAPI is running on port 8000.",
      0,
      error,
    );
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail;
    const message =
      payload?.message ||
      (typeof detail === "string"
        ? detail
        : `Backend request failed with status ${response.status}.`);
    throw new ApiError(message, response.status, payload);
  }
  return payload;
}

export function getIncomeCertificateForm() {
  return request("/api/forms/income-certificate");
}

export function getForms() {
  return request("/api/forms");
}

export function getForm(formId) {
  return request(`/api/forms/${encodeURIComponent(formId)}`);
}

export function getServices() {
  return request("/api/services");
}

export function searchServices(query = "") {
  return request(`/api/services/search?q=${encodeURIComponent(query)}`);
}

export function createSession(language = "auto", formId = "income_certificate") {
  return request("/api/sessions", {
    method: "POST",
    body: JSON.stringify({
      form_id: formId,
      language,
    }),
  });
}

export function askAssistant({
  sessionId,
  formId = "income_certificate",
  message,
  currentField,
  currentDocument = null,
  lastVisibleSection = null,
  language = "auto",
}) {
  return request("/api/assistant/ask", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      form_id: formId,
      message,
      current_field: currentField || null,
      current_document: currentDocument || null,
      last_visible_section: lastVisibleSection,
      language,
    }),
  });
}

export async function transcribeAudio({
  audioBlob,
  languageHint = "auto",
  formId = "income_certificate",
  sessionId = "",
  fallbackTranscript = "",
}) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "niyamguard-voice.webm");
  formData.append("language_hint", languageHint);
  formData.append("form_id", formId);
  formData.append("session_id", sessionId);
  if (fallbackTranscript) {
    formData.append("fallback_transcript", fallbackTranscript);
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/stt/transcribe`, {
      method: "POST",
      body: formData,
    });
  } catch (error) {
    throw new ApiError(
      "Cannot reach backend listening service. Browser speech fallback may be used.",
      0,
      error,
    );
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(
      payload?.message || "Could not transcribe audio clearly.",
      response.status,
      payload,
    );
  }
  return payload;
}

export function validateInput(field, value) {
  return request("/api/assistant/validate", {
    method: "POST",
    body: JSON.stringify({ field, value }),
  });
}

export function generateSummary({
  sessionId,
  formId = "income_certificate",
  formValues,
  uploadedDocuments = {},
  language = "auto",
}) {
  return request("/api/assistant/summary", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      form_id: formId,
      form_values: formValues,
      uploaded_documents: uploadedDocuments,
      language,
    }),
  });
}

export async function requestTtsAudio({
  text,
  languageCode,
  detectedLanguage,
  provider = "auto",
}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/tts/speak`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        language_code: languageCode,
        detected_language: detectedLanguage,
        provider,
      }),
    });
  } catch (error) {
    throw new ApiError(
      "Cannot reach backend voice output. Check that FastAPI is running.",
      0,
      error,
    );
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new ApiError(
      payload?.message ||
        "Could not generate voice output for this language. Please check internet or TTS provider.",
      response.status,
      payload,
    );
  }

  return {
    blob: await response.blob(),
    languageCode:
      response.headers.get("X-TTS-Language-Code") || languageCode,
    provider: response.headers.get("X-TTS-Provider") || provider,
    cacheStatus: response.headers.get("X-TTS-Cache") || null,
  };
}

export function getTtsHealth() {
  return request("/api/tts/health");
}

export function getIntegrationHealth() {
  return request("/api/integration/health");
}

export function getLatestPublicRule(
  serviceId = "income_certificate",
  ruleKey = "validity",
) {
  return request(
    `/api/public/rules/latest?service_id=${encodeURIComponent(serviceId)}&rule_key=${encodeURIComponent(ruleKey)}`,
  );
}

export function reverseLocation({ latitude, longitude, language = "auto" }) {
  return request("/api/location/reverse", {
    method: "POST",
    body: JSON.stringify({ latitude, longitude, language }),
  });
}

export function getAdminSummary() {
  return request("/api/admin/summary");
}

export function getModuleStatus() {
  return request("/api/admin/module-status");
}

export function runCompliance() {
  return request("/api/compliance/run", { method: "POST" });
}

export function getConnectedSystems() {
  return request("/api/connected-systems");
}

export function getComplianceFindings() {
  return request("/api/compliance/findings");
}

export function getCascadeForFinding(findingId) {
  return request(`/api/cascade/finding/${encodeURIComponent(findingId)}`);
}

export function recalculatePriority() {
  return request("/api/dashboard/recalculate-priority", { method: "POST" });
}

export function getPriorityFindings() {
  return request("/api/dashboard/priority-findings");
}

export function getDashboardSummary() {
  return request("/api/dashboard/summary");
}

export function scanConflicts() {
  return request("/api/conflicts/scan", { method: "POST" });
}

export function getConflicts() {
  return request("/api/conflicts");
}

export function getKnowledgeRules() {
  return request("/api/knowledge/rules");
}

export function getReportsSummary() {
  return request("/api/reports/summary");
}

export function reportExportUrl(type, format) {
  return `${API_BASE_URL}/api/reports/export?type=${encodeURIComponent(type)}&format=${encodeURIComponent(format)}`;
}
