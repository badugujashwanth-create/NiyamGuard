import { request } from "./client";

export function getAdminSummary() {
  return request("/api/admin/summary");
}

export function getModuleStatus() {
  return request("/api/admin/module-status");
}

export function getConnectedSystems() {
  return request("/api/connected-systems");
}

export function getCascadeForFinding(findingId) {
  return request(`/api/cascade/finding/${encodeURIComponent(findingId)}`);
}

export function recalculatePriority() {
  return request("/api/dashboard/recalculate-priority", { method: "POST" });
}

export function getPriorityFindings() {
  return request("/api/dashboard/priority-findings");
}

export function getKnowledgeRules() {
  return request("/api/knowledge/rules");
}

export function getAuditEvents() {
  return request("/api/audit/events");
}

export function verifyAudit() {
  return request("/api/audit/verify");
}
