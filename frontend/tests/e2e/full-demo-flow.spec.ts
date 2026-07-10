import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const assetsDir = path.resolve(process.cwd(), "../docs/recording-assets");

async function screenshot(page, name: string) {
  fs.mkdirSync(assetsDir, { recursive: true });
  await page.screenshot({ path: path.join(assetsDir, name), fullPage: true });
}

test("full visible NiyamGuard demo flow", async ({ page }) => {
  await page.goto("/government");
  await expect(page.getByRole("heading", { name: "NiyamGuard Government Portal" })).toBeVisible();
  await expect(page.getByText(/Demo and pilot testing only/)).toBeVisible();
  await screenshot(page, "e2e-step-01-portal.png");

  await page.getByRole("button", { name: "Run Full End-to-End Demo" }).click();
  await expect(page.getByText(/Certificate Generated/i)).toBeVisible({ timeout: 30_000 });
  await expect(page.getByTestId("demo-application-number")).toContainText("NGSP-");
  await expect(page.getByTestId("demo-certificate-number")).toContainText("NGCERT-");
  const verificationHash = (await page.getByTestId("demo-verification-hash").textContent())?.trim() || "";
  expect(verificationHash.length).toBeGreaterThan(16);
  await screenshot(page, "e2e-step-02-scenario.png");

  await page.goto("/services");
  await expect(page.getByRole("heading", { name: "Public Services" })).toBeVisible();
  await expect(page.getByText("Income Certificate")).toBeVisible();
  await screenshot(page, "e2e-step-03-services.png");

  await page.goto("/login");
  await page.getByLabel("Email").fill("officer@niyamguard.local");
  await page.getByLabel("Password").fill("Officer@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Officer Review" })).toBeVisible();
  await screenshot(page, "e2e-step-04-officer.png");

  await page.goto("/verify-certificate");
  await page.getByLabel("Certificate number or hash").fill(verificationHash);
  await page.getByRole("button", { name: "Verify" }).last().click();
  await expect(page.getByRole("heading", { name: "Certificate is valid" })).toBeVisible();
  await screenshot(page, "e2e-step-05-verify-certificate.png");

  await page.goto("/admin/compliance");
  await expect(page.getByRole("heading", { name: "Compliance" })).toBeVisible();
  await screenshot(page, "e2e-step-06-compliance.png");

  await page.goto("/admin/audit");
  await expect(page.getByRole("heading", { name: "Audit" })).toBeVisible();
  await expect(page.getByText("Audit Log")).toBeVisible();
  await screenshot(page, "e2e-step-07-audit.png");

  await page.goto("/government");
  await page.getByRole("button", { name: "Ask Hybrid Test Question" }).click();
  await expect(page.getByTestId("hybrid-output")).toContainText("Income Certificate");
  await expect(page.getByTestId("hybrid-output")).toContainText(/Verified Source|exact_rule_engine/);
  await screenshot(page, "e2e-step-08-hybrid-answer.png");

  await page.getByRole("button", { name: "Explain GO-138 Using Local AI" }).first().click();
  await expect(page.getByTestId("ollama-output")).toContainText(/GO-138|6 months|fallback/i);
  await screenshot(page, "e2e-step-09-ollama-status.png");

  await page.goto("/citizen/assistant");
  await expect(page.getByRole("heading", { name: "Choose a simplified service form" })).toBeVisible();
  await page
    .locator("article")
    .filter({ has: page.getByRole("heading", { name: "Income Certificate" }) })
    .getByRole("button", { name: "Start Application" })
    .click();
  await expect(page.getByRole("heading", { name: "Income Certificate Application" })).toBeVisible();
  await page.getByRole("button", { name: "Use Text Instead" }).click();
  await expect(page.getByLabel("Type your question")).toBeVisible();
  await screenshot(page, "e2e-step-10-speech-fallback.png");

  const video = page.video();
  await page.close();
  if (video) {
    const sourcePath = await video.path();
    fs.copyFileSync(sourcePath, path.join(assetsDir, "final-full-e2e-demo.webm"));
  }
});
