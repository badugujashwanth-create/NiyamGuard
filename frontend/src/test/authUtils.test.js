import { describe, expect, it } from "vitest";

import { canAccessRoute, isPublicRoute, roleHomePath } from "../utils/authUtils";

describe("role-isolated portal routing", () => {
  it("routes every demo role to its dedicated portal", () => {
    expect(roleHomePath({ role: "citizen" })).toBe("/citizen");
    expect(roleHomePath({ role: "officer" })).toBe("/government");
    expect(roleHomePath({ role: "reviewer" })).toBe("/government");
    expect(roleHomePath({ role: "admin" })).toBe("/admin");
    expect(roleHomePath({ role: "sandbox_admin" })).toBe("/admin/sandbox");
  });

  it("allows citizens only inside citizen workflows", () => {
    const citizen = { role: "citizen" };
    expect(canAccessRoute("/apply/income_certificate", citizen)).toBe(true);
    expect(canAccessRoute("/chatbot", citizen)).toBe(true);
    expect(canAccessRoute("/government", citizen)).toBe(false);
    expect(canAccessRoute("/admin", citizen)).toBe(false);
  });

  it("allows officers and reviewers only inside the government portal", () => {
    expect(canAccessRoute("/government/applications/pending", { role: "officer" })).toBe(true);
    expect(canAccessRoute("/government/circulars", { role: "reviewer" })).toBe(true);
    expect(canAccessRoute("/officer/pending", { role: "reviewer" })).toBe(false);
    expect(canAccessRoute("/admin/audit", { role: "officer" })).toBe(false);
    expect(canAccessRoute("/citizen", { role: "reviewer" })).toBe(false);
  });

  it("keeps administrators out of citizen and officer workflows", () => {
    const admin = { role: "admin" };
    expect(canAccessRoute("/admin", admin)).toBe(true);
    expect(canAccessRoute("/admin/sandbox", admin)).toBe(true);
    expect(canAccessRoute("/admin/audit", admin)).toBe(true);
    expect(canAccessRoute("/admin/users", admin)).toBe(true);
    expect(canAccessRoute("/citizen", admin)).toBe(false);
    expect(canAccessRoute("/government", admin)).toBe(false);
    expect(canAccessRoute("/admin/compliance", admin)).toBe(false);
  });

  it("restricts sandbox administrators to the sandbox nested under Admin", () => {
    const sandboxAdmin = { role: "sandbox_admin" };
    expect(canAccessRoute("/admin/sandbox", sandboxAdmin)).toBe(true);
    expect(canAccessRoute("/sandbox", sandboxAdmin)).toBe(false);
    expect(canAccessRoute("/admin", sandboxAdmin)).toBe(false);
    expect(canAccessRoute("/government", sandboxAdmin)).toBe(false);
  });

  it("denies unknown and prefix-lookalike paths", () => {
    expect(canAccessRoute("/unknown", { role: "citizen" })).toBe(false);
    expect(canAccessRoute("/administrator", { role: "admin" })).toBe(false);
    expect(canAccessRoute("/governmental", { role: "officer" })).toBe(false);
    expect(isPublicRoute("/verify-certificate?query=demo")).toBe(true);
    expect(isPublicRoute("/verification-admin")).toBe(false);
  });
});
