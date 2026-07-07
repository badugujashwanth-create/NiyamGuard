import { vi } from "vitest";

export const fields = [
  {
    key: "applicant_name",
    label: "Applicant Full Name",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter your full name.",
      telugu: "మీ పూర్తి పేరు టైప్ చేయండి.",
      hindi: "अपना पूरा नाम लिखें.",
    },
  },
  {
    key: "monthly_income",
    label: "Monthly Income",
    type: "number",
    required: true,
    validation: "positive_number",
    help: {
      english: "Enter monthly income.",
      telugu: "నెలవారీ ఆదాయం టైప్ చేయండి.",
      hindi: "महीने की आमदनी लिखें.",
    },
  },
  {
    key: "mobile_number",
    label: "Mobile Number",
    type: "phone",
    required: true,
    validation: "10_digits",
    help: {
      english: "Enter mobile number.",
      telugu: "మొబైల్ నంబర్ టైప్ చేయండి.",
      hindi: "मोबाइल नंबर लिखें.",
    },
  },
  {
    key: "district",
    label: "District",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter district.",
      telugu: "జిల్లా టైప్ చేయండి.",
      hindi: "जिला लिखें.",
    },
  },
  {
    key: "mandal",
    label: "Mandal",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter mandal.",
      telugu: "మండలం టైప్ చేయండి.",
      hindi: "मंडल लिखें.",
    },
  },
  {
    key: "purpose",
    label: "Purpose of Certificate",
    type: "text",
    required: true,
    validation: "non_empty",
    help: {
      english: "Enter why you need the certificate.",
      telugu: "Certificate ఎందుకు కావాలో టైప్ చేయండి.",
      hindi: "Certificate क्यों चाहिए लिखें.",
    },
  },
];

export const documents = [
  {
    key: "aadhaar",
    label: "Aadhaar Card",
    required: true,
    accepted_file_types: ["pdf", "jpg", "jpeg", "png"],
    max_size_mb: 5,
    examples: ["Aadhaar PDF"],
    help: {
      english: "Upload Aadhaar card.",
      telugu: "Aadhaar upload చేయండి.",
      hindi: "Aadhaar upload करें.",
    },
  },
  {
    key: "income_proof",
    label: "Income Proof",
    required: true,
    accepted_file_types: ["pdf", "jpg", "jpeg", "png"],
    max_size_mb: 1,
    examples: ["Salary slip", "Income affidavit"],
    help: {
      english: "Upload salary slip or affidavit.",
      telugu: "Salary slip లేదా affidavit upload చేయండి.",
      hindi: "Salary slip या affidavit upload करें.",
    },
  },
];

export const incomeForm = {
  form_id: "income_certificate",
  service_name: "Income Certificate",
  form_name: "Income Certificate Application",
  department: "Revenue",
  category: "Certificates",
  description: "Test income form",
  common_use_cases: ["Scholarship", "Fee reimbursement"],
  fields,
  required_documents: documents,
  assistant_examples: {
    english: ["monthly income"],
    telugu: ["purpose lo emi rayali"],
    hindi: ["purpose mein kya likhna hai"],
  },
  assistant_guidance: {},
  translations: {},
  status: "ready",
};

export const services = [
  {
    form_id: "income_certificate",
    service_name: "Income Certificate",
    department: "Revenue",
    category: "Certificates",
    description: "Citizen-friendly income certificate.",
    common_use_cases: ["Scholarship", "Fee reimbursement", "Jobs", "Benefits"],
    required_document_count: 2,
    status: "ready",
    has_detailed_schema: true,
  },
  {
    form_id: "birth_certificate",
    service_name: "Birth Certificate",
    department: "Municipal / Panchayat",
    category: "Certificates",
    description: "Birth certificate guidance.",
    common_use_cases: ["School admission", "Passport"],
    required_document_count: 2,
    status: "ready",
    has_detailed_schema: true,
  },
  {
    form_id: "loan_eligibility_card",
    service_name: "Loan Eligibility Card",
    department: "Agriculture / Revenue",
    category: "Agriculture",
    description: "General guidance for loan eligibility card requirements.",
    common_use_cases: ["Agriculture loan", "Bank support"],
    required_document_count: 0,
    status: "catalog_only",
    has_detailed_schema: false,
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
  function maybeDelay(payload) {
    if (!overrides.askDelayMs) return jsonResponse(payload);
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(jsonResponse(payload));
      }, overrides.askDelayMs);
    });
  }

  const fetchMock = vi.fn((url, options = {}) => {
    if (url.endsWith("/api/forms")) {
      return jsonResponse({ success: true, forms: overrides.services || services });
    }
    if (url.includes("/api/services/search")) {
      return jsonResponse({ success: true, services: overrides.services || services });
    }
    if (url.endsWith("/api/services")) {
      return jsonResponse({ success: true, services: overrides.services || services });
    }
    if (url.endsWith("/api/forms/income-certificate")) {
      return jsonResponse({ success: true, form: incomeForm });
    }
    if (url.endsWith("/api/forms/income_certificate")) {
      return jsonResponse({ success: true, form: overrides.form || incomeForm });
    }
    if (url.endsWith("/api/forms/birth_certificate")) {
      return jsonResponse({ success: true, form: { ...incomeForm, form_id: "birth_certificate", service_name: "Birth Certificate" } });
    }
    if (url.endsWith("/api/sessions")) {
      const requestBody = JSON.parse(options.body);
      return jsonResponse({
        success: true,
        session_id:
          requestBody.form_id === "catalog" ? "catalog-session" : "session-123",
        form_id: requestBody.form_id,
        language: requestBody.language,
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
    if (url.endsWith("/api/stt/transcribe")) {
      return jsonResponse(
        overrides.stt || {
          success: true,
          transcript: "purpose lo scholarship ani rayacha",
          detected_language: "telugu",
          language_code: "te-IN",
          confidence: 0.85,
          provider: "browser-fallback",
        },
      );
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
      const defaultResponse =
        requestBody.form_id === "catalog"
          ? {
              success: true,
              field: null,
              reply:
                "It looks like you may need the Income Certificate form.",
              suggested_form_id: "income_certificate",
              suggested_form_name: "Income Certificate",
              related_values: {},
              location_matches: [],
              warning: null,
              detected_language: "english",
              language_code: "en-IN",
              auto_fill: false,
              should_submit: false,
            }
          : {
              success: true,
              field: "monthly_income",
              reply:
                "You can enter 15000 in Monthly Income. If Annual Income is asked, enter 180000.",
              suggested_value: "15000",
              related_values: { annual_income: "180000" },
              location_matches: [],
              warning: null,
              detected_language: "english",
              language_code: "en-IN",
              auto_fill: false,
              should_submit: false,
            };
      return maybeDelay(
        (typeof overrides.ask === "function"
          ? overrides.ask(requestBody)
          : overrides.ask) || defaultResponse,
      );
    }
    if (url.endsWith("/api/assistant/summary")) {
      return jsonResponse(
        overrides.summary || {
          success: true,
          summary: "Please review your details.",
          missing_fields: [],
          missing_documents: [],
          warnings: [],
          detected_language: "english",
          language_code: "en-IN",
          auto_fill: false,
          should_submit: false,
        },
      );
    }
    if (url.endsWith("/api/assistant/validate")) {
      const requestBody = JSON.parse(options.body);
      return jsonResponse({
        success: true,
        field: requestBody.field,
        valid: true,
        message: `${requestBody.field} is valid.`,
        auto_fill: false,
        should_submit: false,
      });
    }
    return jsonResponse({ detail: "Not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { fetchMock };
}
