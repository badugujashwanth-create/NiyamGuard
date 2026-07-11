import { API_BASE_URL, ApiError, request } from "./client";

export function createSession(language = "auto", formId = "income_certificate") {
  return request(
    "/api/sessions",
    {
      method: "POST",
      body: JSON.stringify({
        form_id: formId,
        language,
      }),
    },
  );
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
  return request(
    "/api/assistant/ask",
    {
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
    },
  );
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
      payload?.error?.message || payload?.message || "Could not transcribe audio clearly.",
      response.status,
      payload,
    );
  }
  return payload;
}

export function validateInput(field, value) {
  return request(
    "/api/assistant/validate",
    {
      method: "POST",
      body: JSON.stringify({ field, value }),
    },
    { auth: false },
  );
}

export function generateSummary({
  sessionId,
  formId = "income_certificate",
  formValues,
  uploadedDocuments = {},
  language = "auto",
}) {
  return request(
    "/api/assistant/summary",
    {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        form_id: formId,
        form_values: formValues,
        uploaded_documents: uploadedDocuments,
        language,
      }),
    },
    { auth: false },
  );
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
      payload?.error?.message ||
        payload?.message ||
        "Could not generate voice output for this language. Please check internet or TTS provider.",
      response.status,
      payload,
    );
  }

  return {
    blob: await response.blob(),
    languageCode: response.headers.get("X-TTS-Language-Code") || languageCode,
    provider: response.headers.get("X-TTS-Provider") || provider,
    cacheStatus: response.headers.get("X-TTS-Cache") || null,
  };
}

export function getTtsHealth() {
  return request("/api/tts/health", {}, { auth: false });
}

export function reverseLocation({ latitude, longitude, language = "auto" }) {
  return request(
    "/api/location/reverse",
    {
      method: "POST",
      body: JSON.stringify({ latitude, longitude, language }),
    },
    { auth: false },
  );
}
