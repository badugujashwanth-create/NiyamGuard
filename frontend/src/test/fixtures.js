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
    json: () => Promise.resolve(payload),
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
        language: "english",
      }, 201);
    }
    if (url.endsWith("/api/assistant/ask")) {
      return jsonResponse(
        overrides.ask || {
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
