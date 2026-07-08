import { request } from "./client";

export function runCompliance() {
  return request("/api/compliance/run", { method: "POST" });
}

export function getComplianceFindings() {
  return request("/api/compliance/findings");
}

export function scanConflicts() {
  return request("/api/conflicts/scan", { method: "POST" });
}

export function getConflicts() {
  return request("/api/conflicts");
}

export function runDemo() {
  return request("/api/demo/run", { method: "POST" }, { auth: false });
}

