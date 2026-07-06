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

export function createSession(language = "auto") {
  return request("/api/sessions", {
    method: "POST",
    body: JSON.stringify({
      form_id: "income_certificate",
      language,
    }),
  });
}

export function askAssistant({
  sessionId,
  message,
  currentField,
  language = "auto",
}) {
  return request("/api/assistant/ask", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      message,
      current_field: currentField || null,
      language,
    }),
  });
}

export function validateInput(field, value) {
  return request("/api/assistant/validate", {
    method: "POST",
    body: JSON.stringify({ field, value }),
  });
}

export function generateSummary(sessionId, formValues, language = "auto") {
  return request("/api/assistant/summary", {
    method: "POST",
    body: JSON.stringify({
      session_id: sessionId,
      form_values: formValues,
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

export function reverseLocation({ latitude, longitude, language = "auto" }) {
  return request("/api/location/reverse", {
    method: "POST",
    body: JSON.stringify({ latitude, longitude, language }),
  });
}
