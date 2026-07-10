import { request } from "./client";

export function getAIStatus() {
  return request("/api/ai/status", {}, { auth: false });
}

export function generateAIFindingSummary(findingId) {
  return request(`/api/ai/finding/${findingId}/impact-summary`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}
