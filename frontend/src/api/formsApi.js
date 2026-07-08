import { request } from "./client";

export function getIncomeCertificateForm() {
  return request("/api/forms/income-certificate", {}, { auth: false });
}

export function getForms() {
  return request("/api/forms", {}, { auth: false });
}

export function getForm(formId) {
  return request(`/api/forms/${encodeURIComponent(formId)}`, {}, { auth: false });
}

export function getServices() {
  return request("/api/services", {}, { auth: false });
}

export function searchServices(query = "") {
  return request(`/api/services/search?q=${encodeURIComponent(query)}`, {}, { auth: false });
}

