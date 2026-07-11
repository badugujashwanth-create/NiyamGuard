import { request } from "./client";

export function getSandboxStatus() {
  return request("/api/sandbox/status");
}

export function listSandboxCirculars() {
  return request("/api/sandbox/circulars");
}

export function createSandboxCircular(payload) {
  return request("/api/sandbox/circulars", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function generateSandboxCircularPdf(circularId, payload = null) {
  if (circularId) {
    return request(`/api/sandbox/circulars/${encodeURIComponent(circularId)}/generate-pdf`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  }
  return request("/api/sandbox/circulars/generate-pdf", {
    method: "POST",
    body: JSON.stringify(payload || {}),
  });
}

export function exportSandboxCircular(circularId) {
  return request(`/api/sandbox/circulars/${encodeURIComponent(circularId)}/export`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function publishSandboxCircular(circularId) {
  return request(`/api/sandbox/circulars/${encodeURIComponent(circularId)}/publish`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function downloadSandboxCircularPdf(circularId) {
  return request(
    `/api/sandbox/circulars/${encodeURIComponent(circularId)}/pdf`,
    {},
    { parseAs: "blob" },
  );
}
