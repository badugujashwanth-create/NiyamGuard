import { expect, test } from "@playwright/test";

test.use({ video: "off", screenshot: "off" });
const baseUrl = process.env.DEMO_BASE_URL || "http://127.0.0.1:5180";

test("core reviewer workflow exposes accessible landmarks and lifecycle feedback", async ({ page }) => {
  await page.goto(`${baseUrl}/`);
  await expect(page.getByRole("heading", { name: "A government rule changed. Downstream systems are still wrong." })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Reviewer Workflow" })).toBeVisible();

  await page.goto(`${baseUrl}/government`);
  await expect(page.getByRole("main", { name: "NiyamGuard Government Portal" })).toBeVisible();
  await expect(page.getByRole("status", { name: "Status: pending" })).toBeVisible();

  await page.getByRole("button", { name: "Run Connected Policy Lifecycle" }).click();
  await expect(page.getByRole("status", { name: "Status: success" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByTestId("lifecycle-evidence")).toContainText("GO-138");

  await page.goto(`${baseUrl}/login`);
  await page.getByLabel("Email").fill("admin@niyamguard.local");
  await page.getByLabel("Password").fill("Admin@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("main", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  await expect(page.getByRole("status", { name: /Loading government-core demo data/ })).toHaveCount(0);
});
