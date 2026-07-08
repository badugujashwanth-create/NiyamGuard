import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  askAssistant,
  createSession,
  generateSummary,
  getForm,
  getForms,
  getIntegrationHealth,
  getLatestPublicRule,
  requestTtsAudio,
  reverseLocation,
  searchServices,
  transcribeAudio,
  validateInput,
} from "../services/api";
import { jsonResponse } from "./fixtures";

describe("API client", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => jsonResponse({ success: true, session_id: "abc" })),
    );
  });

  it("creates an auto-language income-certificate session", async () => {
    await createSession("auto", "income_certificate");
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      form_id: "income_certificate",
      language: "auto",
    });
  });

  it("sends current field and language with assistant questions", async () => {
    await askAssistant({
      sessionId: "abc",
      formId: "income_certificate",
      message: "help with income",
      currentField: "monthly_income",
      currentDocument: "income_proof",
      lastVisibleSection: "details",
      language: "auto",
    });
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      session_id: "abc",
      form_id: "income_certificate",
      message: "help with income",
      current_field: "monthly_income",
      current_document: "income_proof",
      last_visible_section: "details",
      language: "auto",
    });
  });

  it("sends validation and summary values without mutating them", async () => {
    await validateInput("mobile_number", "9876543210");
    await generateSummary({
      sessionId: "abc",
      formId: "income_certificate",
      formValues: { purpose: "Scholarship" },
      uploadedDocuments: { aadhaar: { name: "aadhaar.pdf", uploaded: true } },
    });

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      field: "mobile_number",
      value: "9876543210",
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({
      session_id: "abc",
      form_id: "income_certificate",
      form_values: { purpose: "Scholarship" },
      uploaded_documents: { aadhaar: { name: "aadhaar.pdf", uploaded: true } },
      language: "auto",
    });
  });

  it("fetches forms, selected form, and service search", async () => {
    await getForms();
    await getForm("income_certificate");
    await searchServices("income");

    expect(fetch.mock.calls[0][0]).toContain("/api/forms");
    expect(fetch.mock.calls[1][0]).toContain("/api/forms/income_certificate");
    expect(fetch.mock.calls[2][0]).toContain("/api/services/search?q=income");
  });

  it("fetches integration health and public verified rules", async () => {
    await getIntegrationHealth();
    await getLatestPublicRule("income_certificate", "validity");

    expect(fetch.mock.calls[0][0]).toContain("/api/integration/health");
    expect(fetch.mock.calls[1][0]).toContain(
      "/api/public/rules/latest?service_id=income_certificate&rule_key=validity",
    );
  });

  it("requests backend TTS audio with language metadata", async () => {
    const audioBlob = new Blob(["audio"], { type: "audio/mpeg" });
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          headers: {
            get: (name) =>
              ({
                "X-TTS-Language-Code": "te-IN",
                "X-TTS-Provider": "gtts",
                "X-TTS-Cache": "MISS",
              })[name] || null,
          },
          blob: () => Promise.resolve(audioBlob),
        }),
      ),
    );

    const result = await requestTtsAudio({
      text: "నమస్తే",
      languageCode: "te-IN",
      detectedLanguage: "telugu",
    });
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      text: "నమస్తే",
      language_code: "te-IN",
      detected_language: "telugu",
      provider: "auto",
    });
    expect(result.blob).toBe(audioBlob);
    expect(result.provider).toBe("gtts");
  });

  it("sends audio blobs to the backend STT endpoint", async () => {
    await transcribeAudio({
      audioBlob: new Blob(["voice"], { type: "audio/webm" }),
      languageHint: "auto",
      formId: "income_certificate",
      sessionId: "abc",
      fallbackTranscript: "purpose lo scholarship ani rayacha",
    });
    const [url, options] = fetch.mock.calls[0];
    expect(url).toContain("/api/stt/transcribe");
    expect(options.method).toBe("POST");
    expect(options.body).toBeInstanceOf(FormData);
    expect(options.body.get("fallback_transcript")).toBe(
      "purpose lo scholarship ani rayacha",
    );
  });

  it("sends coordinates only after reverse location is requested", async () => {
    await reverseLocation({
      latitude: 17.444,
      longitude: 78.377,
      language: "telugu",
    });
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      latitude: 17.444,
      longitude: 78.377,
      language: "telugu",
    });
  });
});
