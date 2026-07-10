import { request } from "./client";

export function getSandboxStatus() {
  return request("/api/sandbox/status", {}, { auth: false });
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

export function publishSandboxCircular(circularId) {
  return request(`/api/sandbox/circulars/${encodeURIComponent(circularId)}/publish`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function sandboxPdfUrl(circularId) {
  const base = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  return `${base.replace(/\/+$/, "")}/api/sandbox/circulars/${encodeURIComponent(circularId)}/pdf`;
}
