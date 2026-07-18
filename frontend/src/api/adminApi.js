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

export function getDepartmentReadiness() {
  return request("/api/dashboard/departments");
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

export function getAdminReadiness() {
  return request("/api/admin/readiness");
}

export function getOpsStatus() {
  return request("/api/ops/status", {}, { auth: false });
}

export function getVirtualGovStatus() {
  return request("/api/virtual-gov/status", {}, { auth: false });
}

export function getVirtualGovScenarios() {
  return request("/api/virtual-gov/scenarios", {}, { auth: false });
}

export function runVirtualGovScenario({ scenarioId = "income_certificate_full_flow", resetBeforeRun = true } = {}) {
  return request(
    "/api/virtual-gov/run",
    {
      method: "POST",
      body: JSON.stringify({
        scenario_id: scenarioId,
        reset_before_run: resetBeforeRun,
      }),
    },
    { auth: false },
  );
}

export function getSources() {
  return request("/api/sources");
}

export function syncSource(sourceId) {
  return request(`/api/sources/${encodeURIComponent(sourceId)}/sync`, { method: "POST" });
}

export function getCircularDocuments() {
  return request("/api/circulars");
}

export function syncCirculars() {
  return request("/api/circulars/sync-all", { method: "POST" });
}

export function extractCircularRules(circularId) {
  return request(`/api/circulars/${encodeURIComponent(circularId)}/extract-rules`, { method: "POST" });
}

export function getRuleCandidates() {
  return request("/api/rule-candidates");
}

export function approveRuleCandidate(candidateId, notes = "") {
  return request(`/api/rule-candidates/${encodeURIComponent(candidateId)}/approve`, {
    method: "POST",
    body: JSON.stringify({ notes }),
  });
}

export function publishRuleCandidate(candidateId, notes = "") {
  return request(`/api/policy-updates/${encodeURIComponent(candidateId)}/publish`, {
    method: "POST",
    body: JSON.stringify({ notes }),
  });
}

export function getPolicyUpdateHistory() {
  return request("/api/policy-updates/history");
}

export function getPolicyRuleVersions() {
  return request("/api/policy-updates/versions");
}

export function getPolicyRuleLineage(ruleId) {
  return request(`/api/policy-updates/rules/${encodeURIComponent(ruleId)}/lineage`);
}

export function getKnowledgeUpdateEvents() {
  return request("/api/knowledge/update-events");
}

export function reindexKnowledge() {
  return request("/api/knowledge/reindex", { method: "POST" });
}

export function getPropagationTasks() {
  return request("/api/propagation/tasks");
}

export function applyPropagationDemoPatch(taskId) {
  return request(`/api/propagation/tasks/${encodeURIComponent(taskId)}/apply-demo-patch`, { method: "POST" });
}

export function getSchedulerStatus() {
  return request("/api/scheduler/status");
}

export function runSchedulerNow() {
  return request("/api/scheduler/run-now", { method: "POST" });
}

export function rerunComplianceForRule(ruleId) {
  return request(`/api/compliance/rerun-for-rule/${encodeURIComponent(ruleId)}`, { method: "POST" });
}

export function getComplianceRuns() {
  return request("/api/compliance/runs");
}

export function getMockSystems() {
  return request("/api/mock-systems", {}, { auth: false });
}

export function getMockMeeseva() {
  return request("/api/mock-systems/meeseva", {}, { auth: false });
}

export function getMockPublicFaq() {
  return request("/api/mock-systems/public-faq", {}, { auth: false });
}

export function resetMockSystems() {
  return request("/api/mock-systems/reset-demo", { method: "POST" }, { auth: false });
}

export function applyMockDemoPatch() {
  return request("/api/mock-systems/apply-demo-patch", { method: "POST" }, { auth: false });
}

export function runSelfUpdateScenario({ applyDemoPatch = false, resetMockSystems: reset = false } = {}) {
  return request(
    "/api/demo/run-self-update-scenario",
    {
      method: "POST",
      body: JSON.stringify({
        apply_demo_patch: applyDemoPatch,
        reset_mock_systems: reset,
      }),
    },
    { auth: false },
  );
}
