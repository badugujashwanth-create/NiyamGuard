import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const assetsDir = path.resolve(process.cwd(), "../docs/recording-assets");

async function screenshot(page, name: string) {
  fs.mkdirSync(assetsDir, { recursive: true });
  await page.screenshot({ path: path.join(assetsDir, name), fullPage: true });
}

test("restored full feature access through two portals", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "NiyamGuard" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Citizen Portal" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Government Portal" })).toBeVisible();
  await expect(page.getByText("Run Full End-to-End Demo")).toHaveCount(0);
  await screenshot(page, "restored-01-home.png");

  await page.goto("/citizen");
  await expect(page.getByRole("heading", { name: "Citizen Portal" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Apply for Certificates with Voice Assistant" })).toBeVisible();
  await expect(page.getByRole("complementary", { name: "NiyamGuard Voice Assistant" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Services" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Apply Income Certificate" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Track Application" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Verify Certificate" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Start Voice Assistant" })).toBeVisible();
  await page.getByRole("button", { name: "Use Text Instead" }).click();
  await page.getByLabel("Type your question").fill("income certificate validity entha");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.getByText(/Income Certificate validity|6 months/i).first()).toBeVisible();
  await expect(page.getByLabel("Verified Source")).toBeVisible();
  await expect(page.locator("body")).not.toContainText(/Check your connection or use the text box/i);
  await screenshot(page, "restored-02-citizen-voice-assistant.png");

  await page.goto("/government");
  await expect(page.getByRole("heading", { name: "NiyamGuard Government Portal" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Circulars & Policy Updates", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Self-Updating Policy Engine", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Compliance Drift", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Connected Systems / Propagation", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Virtual Government Sandbox", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Officer Review", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Certificates", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Audit Trail", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Reports", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Hybrid Answer Engine / Ollama", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Readiness & Ops", exact: true })).toBeVisible();
  await screenshot(page, "restored-03-government-overview.png");

  await page.goto("/login");
  await page.getByLabel("Email").fill("admin@niyamguard.local");
  await page.getByLabel("Password").fill("Admin@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  await page.goto("/admin/policy-updates");
  await expect(page.getByRole("heading", { name: "Policy Updates" })).toBeVisible();
  await expect(page.getByText(/Version history|compliance reruns/i)).toBeVisible();
  await screenshot(page, "restored-04-circular-policy.png");

  await page.goto("/admin/compliance");
  await expect(page.getByRole("heading", { name: "Compliance" })).toBeVisible();
  await expect(page.getByText(/Compliance Findings|drifted systems|compliant system/i).first()).toBeVisible();
  await screenshot(page, "restored-05-compliance.png");

  await page.goto("/virtual-gov");
  await expect(page.getByRole("heading", { name: "Virtual Government Sandbox" })).toBeVisible();
  await expect(page.getByText(/Virtual Gazette|Certificate Authority|Scenario/i).first()).toBeVisible();
  await screenshot(page, "restored-06-virtual-gov.png");

  await page.goto("/government");
  await page.getByRole("button", { name: "Run Full End-to-End Demo" }).click();
  await expect(page.getByTestId("demo-application-number")).toContainText("NGSP-", { timeout: 60_000 });
  await expect(page.getByTestId("demo-certificate-number")).toContainText("NGCERT-", { timeout: 60_000 });
  await expect(page.getByText("Ollama Explanation Generated or Fallback Active")).toBeVisible();
  await expect(page.getByRole("button", { name: "Explain GO-138 using Local AI" }).first()).toBeVisible();
  await page.getByRole("button", { name: "Explain GO-138 using Local AI" }).first().click();
  await expect(page.getByTestId("ollama-output")).toContainText(/GO-138|6 months|fallback/i, { timeout: 30_000 });
  const certificateNumber = (await page.getByTestId("demo-certificate-number").textContent())?.trim() || "";
  const verificationHash = (await page.getByTestId("demo-verification-hash").textContent())?.trim() || "";
  expect(certificateNumber.length).toBeGreaterThan(6);
  expect(verificationHash.length).toBeGreaterThan(12);

  await page.goto("/verify-certificate");
  await page.getByLabel("Certificate number or hash").fill(verificationHash);
  await page.getByRole("button", { name: "Verify" }).last().click();
  await expect(page.getByRole("heading", { name: "Certificate is valid" })).toBeVisible();
  await expect(page.getByText(certificateNumber)).toBeVisible();
  await screenshot(page, "restored-07-e2e-result.png");

  await page.goto("/demo");
  await expect(page.getByRole("heading", { name: "NiyamGuard AI Demo" })).toBeVisible();

  await page.goto("/mock/meeseva");
  await expect(page.getByText(/MeeSeva|Income Certificate/i).first()).toBeVisible();

  await page.goto("/mock/public-faq");
  await expect(page.getByText(/Public FAQ|Income Certificate/i).first()).toBeVisible();
});
