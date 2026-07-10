import { describe, expect, it } from "vitest";

import {
  getSpeechSupport,
  isSecureSpeechContext,
  speechErrorMessage,
} from "../services/speechService";

describe("speechService", () => {
  it("allows speech on localhost without HTTPS", () => {
    expect(isSecureSpeechContext({ protocol: "http:", hostname: "127.0.0.1" })).toBe(true);
    expect(isSecureSpeechContext({ protocol: "http:", hostname: "localhost" })).toBe(true);
  });

  it("blocks speech on insecure non-local origins", () => {
    const support = getSpeechSupport({
      win: {},
      location: { protocol: "http:", hostname: "example.com" },
      navigatorRef: {},
    });

    expect(support.supported).toBe(false);
    expect(support.reason).toContain("localhost or HTTPS");
  });

  it("reports unsupported speech without blocking text fallback", () => {
    const support = getSpeechSupport({
      win: {},
      location: { protocol: "https:", hostname: "demo.test" },
      navigatorRef: {},
    });

    expect(support.supported).toBe(false);
    expect(support.reason).toBe("Voice input is not available in this browser. You can continue using text.");
  });

  it("maps browser permission and service failures to demo-safe messages", () => {
    expect(speechErrorMessage("not-allowed")).toContain("Use Text Instead");
    expect(speechErrorMessage("network")).toBe("Voice input is not available in this browser. You can continue using text.");
    expect(speechErrorMessage("service-not-allowed")).toBe(
      "Voice input is not available in this browser. You can continue using text.",
    );
  });
});
