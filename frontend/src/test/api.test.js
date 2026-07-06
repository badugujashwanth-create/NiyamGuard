import { beforeEach, describe, expect, it, vi } from "vitest";

import {
  askAssistant,
  createSession,
  generateSummary,
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

  it("creates the expected income-certificate session", async () => {
    await createSession("mixed");
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      form_id: "income_certificate",
      language: "mixed",
    });
  });

  it("sends current field and language with assistant questions", async () => {
    await askAssistant({
      sessionId: "abc",
      message: "help with income",
      currentField: "monthly_income",
      language: "english",
    });
    const [, options] = fetch.mock.calls[0];
    expect(JSON.parse(options.body)).toEqual({
      session_id: "abc",
      message: "help with income",
      current_field: "monthly_income",
      language: "english",
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
    });
  });
});
