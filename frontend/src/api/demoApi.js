import { request } from "./client";

export function runFullEndToEndDemo() {
  return request("/api/demo/run-full-end-to-end", { method: "POST" }, { auth: false });
}

export function getVerifiedAIExplanation(question = "Explain GO-138 in simple words") {
  return request(
    "/api/ai/verified-explanation",
    {
      method: "POST",
      body: JSON.stringify({ question }),
    },
    { auth: false },
  );
}

export function askHybridDemoQuestion(question) {
  return request(
    "/api/hybrid/answer",
    {
      method: "POST",
      body: JSON.stringify({
        question,
        language: "auto",
        context: { service_id: "income_certificate" },
        profile: {},
      }),
    },
    { auth: false },
  );
}
