import { expect, test } from "@playwright/test";

const baseUrl = process.env.DEMO_BASE_URL || "http://127.0.0.1:5180";
const sceneScale = Number(process.env.DEMO_SCENE_SCALE || "1");
const scene = (page, milliseconds: number) => page.waitForTimeout(Math.max(100, milliseconds * sceneScale));

test.use({
  viewport: { width: 1280, height: 720 },
  video: { mode: "on", size: { width: 1280, height: 720 } },
});

test("record the complete recruiter simulation", async ({ page }) => {
  test.setTimeout(360_000);

  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "NiyamGuard", exact: true })).toBeVisible();
  await expect(page.getByText(/not an official government portal/i)).toBeVisible();
  await scene(page, 12_000);

  await page.goto(`${baseUrl}/demo`, { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "NiyamGuard Product Overview" })).toBeVisible();
  await expect(page.getByText(/synthetic data only/i)).toBeVisible();
  await scene(page, 12_000);
  await page.getByRole("heading", { name: "Synthetic policy-to-service flow" }).scrollIntoViewIfNeeded();
  await scene(page, 12_000);

  await page.goto(`${baseUrl}/government`, { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "NiyamGuard Government Portal" })).toBeVisible();
  await scene(page, 15_000);
  await page.getByRole("button", { name: "Run Full End-to-End Simulation" }).click();
  await expect(page.getByTestId("demo-application-number")).toContainText("NGSP-", { timeout: 60_000 });
  await expect(page.getByTestId("demo-certificate-number")).toContainText("NGCERT-", { timeout: 60_000 });
  const verificationHash = (await page.getByTestId("demo-verification-hash").textContent())?.trim() || "";
  expect(verificationHash.length).toBeGreaterThan(12);
  await page.getByRole("heading", { name: "Run Full End-to-End Simulation" }).scrollIntoViewIfNeeded();
  await scene(page, 30_000);

  await page.getByRole("button", { name: "Ask Hybrid Test Question" }).click();
  await expect(page.getByTestId("hybrid-output")).toContainText(/GO-138|6 months|verified/i);
  await scene(page, 20_000);
  await page.getByRole("button", { name: "Explain GO-138 using Local AI" }).last().click();
  await expect(page.getByTestId("ollama-output")).toContainText(/GO-138|6 months|fallback/i, { timeout: 30_000 });
  await scene(page, 20_000);

  await page.goto(`${baseUrl}/demo`, { waitUntil: "networkidle" });
  await page.getByRole("heading", { name: "Self-updating policy engine" }).scrollIntoViewIfNeeded();
  await scene(page, 10_000);
  await page.getByRole("button", { name: "Reset Mock Systems" }).click();
  await expect(page.getByText(/now show outdated values/i)).toBeVisible();
  await scene(page, 15_000);
  await page.getByRole("button", { name: "Run and Patch" }).click();
  await expect(page.getByText(/now show 6 months/i)).toBeVisible({ timeout: 60_000 });
  await scene(page, 25_000);

  await page.goto(`${baseUrl}/citizen`, { waitUntil: "networkidle" });
  await expect(page.getByText(/No official application is submitted/i)).toBeVisible();
  await page.getByRole("heading", { name: "Ask a Source-Backed Question" }).scrollIntoViewIfNeeded();
  await scene(page, 12_000);
  await page.getByRole("textbox", { name: "Question", exact: true }).fill("What is the verified income certificate validity?");
  await page.getByRole("button", { name: "Ask Assistant" }).last().click();
  await expect(page.getByLabel("Verified Source")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByText(/6 months/i).first()).toBeVisible();
  await scene(page, 25_000);

  await page.goto(`${baseUrl}/verify-certificate`, { waitUntil: "networkidle" });
  await page.getByLabel("Certificate number or hash").fill(verificationHash);
  await page.getByRole("main").getByRole("button", { name: "Verify", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Certificate is valid" })).toBeVisible();
  await scene(page, 22_000);

  await page.goto(`${baseUrl}/login`, { waitUntil: "networkidle" });
  await page.getByLabel("Email").fill("admin@niyamguard.local");
  await page.getByLabel("Password").fill("Admin@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await page.goto(`${baseUrl}/admin/audit`, { waitUntil: "networkidle" });
  await expect(page.getByRole("heading", { name: "Audit", exact: true })).toBeVisible();
  await scene(page, 22_000);

  await page.goto(`${baseUrl}/demo`, { waitUntil: "networkidle" });
  await expect(page.getByText(/not an official government portal/i)).toBeVisible();
  await page.getByText(/known limitation|official government|synthetic/i).last().scrollIntoViewIfNeeded();
  await scene(page, 20_000);
});
