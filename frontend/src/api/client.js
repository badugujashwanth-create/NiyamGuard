const defaultBaseUrl = import.meta.env.PROD && typeof window !== "undefined"
  ? window.location.origin
  : "http://127.0.0.1:8000";
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL || defaultBaseUrl;
export const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, "");

export const ACCESS_TOKEN_KEY = "niyamguard.access_token";
export const REFRESH_TOKEN_KEY = "niyamguard.refresh_token";
export const USER_KEY = "niyamguard.user";

export class ApiError extends Error {
  constructor(message, status = 0, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export function getAccessToken() {
  return window.localStorage?.getItem(ACCESS_TOKEN_KEY) || "";
}

export function getRefreshToken() {
  return window.localStorage?.getItem(REFRESH_TOKEN_KEY) || "";
}

export function getStoredUser() {
  const stored = window.localStorage?.getItem(USER_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

export function setAuthSession({ accessToken, refreshToken, user }) {
  if (accessToken) window.localStorage?.setItem(ACCESS_TOKEN_KEY, accessToken);
  if (refreshToken) window.localStorage?.setItem(REFRESH_TOKEN_KEY, refreshToken);
  if (user) window.localStorage?.setItem(USER_KEY, JSON.stringify(user));
  window.dispatchEvent(new CustomEvent("niyamguard:auth-changed", { detail: { user } }));
}

export function clearAuthSession() {
  window.localStorage?.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage?.removeItem(REFRESH_TOKEN_KEY);
  window.localStorage?.removeItem(USER_KEY);
  window.dispatchEvent(new CustomEvent("niyamguard:auth-changed", { detail: { user: null } }));
}

function buildUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_BASE_URL}${path}`;
}

function errorMessage(payload, status) {
  if (payload?.error?.message) return payload.error.message;
  if (payload?.message) return payload.message;
  if (typeof payload?.detail === "string") return payload.detail;
  if (Array.isArray(payload?.detail) && payload.detail.length) {
    return payload.detail
      .map((item) => item.msg || item.message || "Invalid value")
      .join(" ");
  }
  return `Backend request failed with status ${status}.`;
}

async function parseResponse(response, parseAs) {
  if (parseAs === "blob") return response.blob();
  if (parseAs === "text") return response.text();
  return response.json().catch(() => null);
}

export async function request(path, options = {}, { auth = true, parseAs = "json" } = {}) {
  const headers = new Headers(options.headers || {});
  const hasFormData = options.body instanceof FormData;
  if (!hasFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = getAccessToken();
  if (auth && token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  let response;
  try {
    response = await fetch(buildUrl(path), {
      ...options,
      headers,
    });
  } catch (error) {
    throw new ApiError(
      `Cannot reach the NiyamGuard backend. Check that FastAPI is running at ${API_BASE_URL}.`,
      0,
      error,
    );
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    if (response.status === 401 && auth) {
      clearAuthSession();
    }
    throw new ApiError(errorMessage(payload, response.status), response.status, payload);
  }

  return parseResponse(response, parseAs);
}
