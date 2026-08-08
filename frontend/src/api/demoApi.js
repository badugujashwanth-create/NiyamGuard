import { request } from "./client";

export function runFullEndToEndDemo() {
  return request("/api/demo/run-full-end-to-end", { method: "POST" }, { auth: false });
}

export function runPolicyLifecycleDemo() {
  return request("/api/demo/run-policy-lifecycle", { method: "POST" }, { auth: false });
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

export function askHybridDemoQuestion(question, { serviceId = "income_certificate", language = "auto" } = {}) {
  return request(
    "/api/hybrid/answer",
    {
      method: "POST",
      body: JSON.stringify({
        question,
        language,
        context: { service_id: serviceId },
        profile: {},
      }),
    },
    { auth: false },
  );
}
