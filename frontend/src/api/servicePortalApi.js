import { request } from "./client";

export function getPortalServices() {
  return request("/api/portal/services", {}, { auth: false });
}

export function getPortalService(serviceId) {
  return request(`/api/portal/services/${encodeURIComponent(serviceId)}`, {}, { auth: false });
}

export function getPortalServiceForm(serviceId) {
  return request(`/api/portal/services/${encodeURIComponent(serviceId)}/form`, {}, { auth: false });
}

export function getCitizenProfile() {
  return request("/api/citizen/profile");
}

export function updateCitizenProfile(payload) {
  return request("/api/citizen/profile", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function getCitizenDocuments() {
  return request("/api/citizen/documents");
}

export function createPortalApplication(payload) {
  return request("/api/applications", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updatePortalApplication(applicationId, payload) {
  return request(`/api/applications/${encodeURIComponent(applicationId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function submitPortalApplication(applicationId) {
  return request(`/api/applications/${encodeURIComponent(applicationId)}/submit`, { method: "POST" });
}

export function uploadPortalDocument(applicationId, documentType, file) {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("file", file);
  return request(`/api/applications/${encodeURIComponent(applicationId)}/documents`, {
    method: "POST",
    body: formData,
  });
}

export function getPortalApplications(status = "") {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/api/applications${query}`);
}

export function getPortalApplication(applicationId) {
  return request(`/api/applications/${encodeURIComponent(applicationId)}`);
}

export function getApplicationHistory(applicationId) {
  return request(`/api/applications/${encodeURIComponent(applicationId)}/status-history`);
}

export function trackPortalApplication(applicationNumber) {
  return request(`/api/track/${encodeURIComponent(applicationNumber)}`, {}, { auth: false });
}

export function createPortalPayment(applicationId) {
  return request(`/api/payments/${encodeURIComponent(applicationId)}/create`, { method: "POST" });
}

export function simulatePortalPaymentSuccess(paymentId) {
  return request(`/api/payments/${encodeURIComponent(paymentId)}/simulate-success`, { method: "POST" });
}

export function getOfficerApplications(status = "") {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/api/officer/applications${query}`);
}

export function getOfficerPendingApplications() {
  return request("/api/officer/pending");
}

export function approvePortalApplication(applicationId, notes = "") {
  return request(`/api/officer/applications/${encodeURIComponent(applicationId)}/approve`, {
    method: "POST",
    body: JSON.stringify({ notes }),
  });
}

export function rejectPortalApplication(applicationId, reason) {
  return request(`/api/officer/applications/${encodeURIComponent(applicationId)}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function requestPortalDocuments(applicationId, notes, requestedDocuments = []) {
  return request(`/api/officer/applications/${encodeURIComponent(applicationId)}/request-documents`, {
    method: "POST",
    body: JSON.stringify({ notes, requested_documents: requestedDocuments }),
  });
}

export function getPortalCertificate(certificateId) {
  return request(`/api/certificates/${encodeURIComponent(certificateId)}`);
}

export function downloadPortalCertificate(certificateId) {
  return request(
    `/api/certificates/${encodeURIComponent(certificateId)}/download`,
    {},
    { parseAs: "blob" },
  );
}

export function verifyPortalCertificate(query) {
  return request(`/api/certificates/verify/${encodeURIComponent(query)}`, {}, { auth: false });
}

export function getPortalNotifications() {
  return request("/api/notifications");
}

export function markPortalNotificationRead(notificationId) {
  return request(`/api/notifications/${encodeURIComponent(notificationId)}/read`, { method: "PATCH" });
}

export function getAdminPortalServices() {
  return request("/api/admin/services");
}

export function getAdminPortalForms() {
  return request("/api/admin/forms");
}

export function getAdminPortalCertificates() {
  return request("/api/admin/certificates");
}
