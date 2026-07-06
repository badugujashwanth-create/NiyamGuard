import { vi } from "vitest";

export const fields = [
  {
    key: "applicant_name",
    label: "Applicant Full Name",
    type: "text",
    required: true,
    help: "Enter your full name.",
    simple_question: "What is your full name?",
  },
  {
    key: "monthly_income",
    label: "Monthly Income",
    type: "number",
    required: true,
    help: "Enter monthly income.",
    simple_question: "What is your monthly income?",
  },
  {
    key: "mobile_number",
    label: "Mobile Number",
    type: "phone",
    required: true,
    help: "Enter mobile number.",
    simple_question: "What is your mobile number?",
  },
  {
    key: "district",
    label: "District",
    type: "text",
    required: true,
    help: "Enter district.",
    simple_question: "What is your district?",
  },
  {
    key: "mandal",
    label: "Mandal",
    type: "text",
    required: true,
    help: "Enter mandal.",
    simple_question: "What is your mandal?",
  },
  {
    key: "purpose",
    label: "Purpose of Certificate",
    type: "text",
    required: true,
    help: "Enter why you need the certificate.",
    simple_question: "Why do you need it?",
  },
];

export function jsonResponse(payload, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => null },
    json: () => Promise.resolve(payload),
    blob: () => Promise.resolve(new Blob()),
  });
}

export function audioResponse(
  content = "fake-mp3",
  {
    languageCode = "te-IN",
    provider = "gtts",
    cacheStatus = "MISS",
  } = {},
) {
  const headers = new Map([
    ["x-tts-language-code", languageCode],
    ["x-tts-provider", provider],
    ["x-tts-cache", cacheStatus],
  ]);
  return Promise.resolve({
    ok: true,
    status: 200,
    headers: {
      get: (name) => headers.get(name.toLowerCase()) || null,
    },
    json: () => Promise.reject(new Error("Audio response")),
    blob: () => Promise.resolve(new Blob([content], { type: "audio/mpeg" })),
  });
}

export function installApiMock(overrides = {}) {
  const calls = [];
  const fetchMock = vi.fn((url, options = {}) => {
    calls.push({ url, options });

    if (url.endsWith("/api/forms/income-certificate")) {
      return jsonResponse({
        success: true,
        form: {
          form_id: "income_certificate",
          form_name: "Income Certificate Application",
          description: "Test form",
          fields,
        },
      });
    }
    if (url.endsWith("/api/sessions")) {
      return jsonResponse({
        success: true,
        session_id: "session-123",
        form_id: "income_certificate",
        language: "auto",
      }, 201);
    }
    if (url.endsWith("/api/tts/health")) {
      return jsonResponse({
        success: true,
        available_providers: ["browser", "gtts"],
        default_provider: "gtts",
        supported_languages: {
          telugu: "te-IN",
          hindi: "hi-IN",
          english: "en-IN",
        },
      });
    }
    if (url.endsWith("/api/tts/speak")) {
      if (overrides.ttsError) {
        return jsonResponse(
          {
            success: false,
            message:
              "TTS provider failed. Text response is available, but voice audio could not be generated.",
          },
          503,
        );
      }
      const requestBody = JSON.parse(options.body);
      return audioResponse("fake-mp3", {
        languageCode: requestBody.language_code,
      });
    }
    if (url.endsWith("/api/location/reverse")) {
      return jsonResponse(
        overrides.location || {
          success: true,
          detected_language: "english",
          language_code: "en-IN",
          reply:
            "Location permission received, but exact mandal lookup is not available in this MVP. Please enter a pincode or village name.",
          matches: [],
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/ask")) {
      const requestBody = JSON.parse(options.body);
      return jsonResponse(
        (typeof overrides.ask === "function"
          ? overrides.ask(requestBody)
          : overrides.ask) || {
          success: true,
          field: "monthly_income",
          reply:
            "You can enter 15000 in Monthly Income. If Annual Income is asked, enter 180000.",
          suggested_value: "15000",
          related_values: { annual_income: "180000" },
          warning: null,
          detected_language: "english",
          language_code: "en-IN",
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/summary")) {
      return jsonResponse(
        overrides.summary || {
          success: true,
          summary: "Please review your details.",
          missing_fields: [],
          warnings: [],
          detected_language: "english",
          language_code: "en-IN",
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/validate")) {
      return jsonResponse({
        success: true,
        field: "monthly_income",
        valid: true,
        message: "Monthly income is valid.",
        auto_fill: false,
        should_submit: false,
      });
    }
    return jsonResponse({ detail: "Not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock, calls };
}
