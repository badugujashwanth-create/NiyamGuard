const configuredEnvironment = String(import.meta.env.VITE_APP_ENV || "").trim().toLowerCase();

// A production build must be conservative when a host has not supplied an
// environment label. Test and demo tooling are opt-in; they are never exposed
// by a normal production build.
export const appEnvironment = configuredEnvironment || (import.meta.env.PROD ? "production" : "development");
export const isTestEnvironment = import.meta.env.MODE === "test";
export const isDemoEnvironment = isTestEnvironment
  || appEnvironment === "demo"
  || String(import.meta.env.VITE_DEMO_MODE || "").toLowerCase() === "true";
export const isProductionExperience = appEnvironment === "production";
export const showDemoCredentials = isDemoEnvironment
  && !isProductionExperience
  && String(import.meta.env.VITE_SHOW_DEMO_CREDENTIALS || "true").toLowerCase() !== "false";
export const enableSyntheticControls = isDemoEnvironment
  && !isProductionExperience
  && String(import.meta.env.VITE_ENABLE_SYNTHETIC_CONTROLS || "true").toLowerCase() !== "false";

export function safeReturnPath(candidate) {
  return typeof candidate === "string"
    && candidate.startsWith("/")
    && !candidate.startsWith("//")
    && !candidate.includes("\\")
    ? candidate
    : null;
}
