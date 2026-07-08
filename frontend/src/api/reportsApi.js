import { API_BASE_URL, request } from "./client";

function queryString(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, value);
    }
  });
  return search.toString();
}

export function getReportsSummary() {
  return request("/api/reports/summary");
}

export function reportExportUrl(type, format) {
  return `${API_BASE_URL}/api/reports/export?${queryString({ type, format })}`;
}

export function demoReportExportUrl(type, format) {
  return `${API_BASE_URL}/api/demo/reports/export?${queryString({ type, format })}`;
}

export async function downloadReport(type, format, filters = {}) {
  const params = queryString({ type, format, ...filters });
  const blob = await request(
    `/api/reports/export?${params}`,
    { headers: { Accept: format === "json" ? "application/json" : "*/*" } },
    { parseAs: "blob" },
  );
  const filename = `${type}.${format === "html" ? "html" : format}`;
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
  return { success: true, filename };
}

