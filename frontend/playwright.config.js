import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 90_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: "http://127.0.0.1:5180",
    trace: "retain-on-failure",
    video: {
      mode: "on",
      size: { width: 1280, height: 720 },
    },
    screenshot: "only-on-failure",
  },
  reporter: [["html", { open: "never" }], ["list"]],
});
