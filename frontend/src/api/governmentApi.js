import { request } from "./client";

export function getGovernmentCircularInbox() {
  return request("/api/government/circular-inbox");
}

export function parseGovernmentCircular(circularId) {
  return request(`/api/government/circulars/${encodeURIComponent(circularId)}/parse`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function approveGovernmentPolicyUpdate(updateId, notes = "") {
  return request(`/api/government/policy-updates/${encodeURIComponent(updateId)}/approve`, {
    method: "POST",
    body: JSON.stringify({ notes }),
  });
}

export function getPortalSummary() {
  return request("/api/demo/portal-summary", {}, { auth: false });
}
