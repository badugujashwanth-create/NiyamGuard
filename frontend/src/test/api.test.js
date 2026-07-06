import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  askAssistant,
  createSession,
  generateSummary,
  requestTtsAudio,
  reverseLocation,
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
    await createSession();
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      form_id: "income_certificate",
      language: "auto",
    });
  });

  it("sends current field and language with assistant questions", async () => {
    await askAssistant({
      sessionId: "abc",
      message: "help with income",
      currentField: "monthly_income",
      language: "auto",
    });
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      session_id: "abc",
      message: "help with income",
      current_field: "monthly_income",
      language: "auto",
    });
  });

  it("sends validation and summary values without mutating them", async () => {
    await validateInput("mobile_number", "9876543210");
    await generateSummary("abc", { purpose: "Scholarship" });

    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
      field: "mobile_number",
      value: "9876543210",
    });
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({
      session_id: "abc",
      form_values: { purpose: "Scholarship" },
      language: "auto",
    });
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
