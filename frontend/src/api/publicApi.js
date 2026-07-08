import { request } from "./client";

export function getIntegrationHealth() {
  return request("/api/integration/health", {}, { auth: false });
}

export function getLatestPublicRule(serviceId = "income_certificate", ruleKey = "validity") {
  return request(
    `/api/public/rules/latest?service_id=${encodeURIComponent(serviceId)}&rule_key=${encodeURIComponent(ruleKey)}`,
    {},
    { auth: false },
  );
}

export function getDashboardSummary() {
  return request("/api/dashboard/summary", {}, { auth: false });
}

