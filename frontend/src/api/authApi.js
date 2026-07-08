import {
  clearAuthSession,
  getRefreshToken,
  request,
  setAuthSession,
} from "./client";

export async function login(email, password) {
  const response = await request(
    "/api/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    },
    { auth: false },
  );
  setAuthSession({
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    user: response.user,
  });
  return response;
}

export async function logout() {
  const refreshToken = getRefreshToken();
  try {
    await request("/api/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } finally {
    clearAuthSession();
  }
}

export async function refresh() {
  const response = await request(
    "/api/auth/refresh",
    {
      method: "POST",
      body: JSON.stringify({ refresh_token: getRefreshToken() }),
    },
    { auth: false },
  );
  setAuthSession({
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    user: response.user,
  });
  return response;
}

export function getMe() {
  return request("/api/auth/me");
}

export function getUsers() {
  return request("/api/auth/users");
}

export function createUser(payload) {
  return request("/api/auth/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateUser(userId, payload) {
  return request(`/api/auth/users/${encodeURIComponent(userId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

