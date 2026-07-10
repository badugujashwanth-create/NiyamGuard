import { request } from "./client";

export function getDatasetStatus() {
  return request("/api/dataset/status", {}, { auth: false });
}

export function getDatasetDemoFlow(orgId = "") {
  const query = orgId ? `?org_id=${encodeURIComponent(orgId)}` : "";
  return request(`/api/dataset/demo-flow${query}`, {}, { auth: false });
}

export function askDatasetQA({ question, topK = 5 }) {
  return request(
    "/api/dataset/qa",
    {
      method: "POST",
      body: JSON.stringify({ question, top_k: topK }),
    },
    { auth: false },
  );
}
