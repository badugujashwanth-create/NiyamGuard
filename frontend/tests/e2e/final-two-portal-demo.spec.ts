import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const assetsDir = path.resolve(process.cwd(), "../docs/recording-assets");

async function screenshot(page, name: string) {
  fs.mkdirSync(assetsDir, { recursive: true });
  await page.screenshot({ path: path.join(assetsDir, name), fullPage: true });
}

test("final two portal demo flow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "NiyamGuard" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Citizen Portal" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Government Portal" })).toBeVisible();
  await expect(page.getByText("Run Full End-to-End Demo")).toHaveCount(0);
  await screenshot(page, "final-two-portal-01-landing.png");

  await page.getByRole("link", { name: "Open Citizen Portal" }).click();
  await expect(page.getByRole("heading", { name: "Citizen Portal" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Services" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Apply Income Certificate" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Track Application" }).first()).toBeVisible();
  await expect(page.getByRole("link", { name: "Verify Certificate" }).first()).toBeVisible();
  await expect(page.getByRole("complementary", { name: "NiyamGuard Voice Assistant" })).toBeVisible();
  await page.getByRole("textbox", { name: "Question" }).fill("income certificate validity entha");
  await page.getByRole("button", { name: "Ask Assistant" }).last().click();
  await expect(page.getByTestId("citizen-hybrid-output")).toContainText(/Income Certificate|6 months/i);
  await expect(page.getByTestId("citizen-hybrid-output")).toContainText(/Verified Source|exact_rule_engine|verified/i);
  await expect(page.getByText("Compliance Drift")).toHaveCount(0);
  await expect(page.getByText("Audit Trail")).toHaveCount(0);
  await screenshot(page, "final-two-portal-02-citizen.png");

  await page.goto("/government");
  await expect(page.getByRole("heading", { name: "NiyamGuard Government Portal" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Virtual Government Sandbox" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Hybrid Answer Engine / Ollama" })).toBeVisible();
  await screenshot(page, "final-two-portal-03-government.png");

  await page.getByRole("button", { name: "Run Full End-to-End Demo" }).click();
  await expect(page.getByTestId("demo-application-number")).toContainText("NGSP-", { timeout: 60_000 });
  await expect(page.getByTestId("demo-certificate-number")).toContainText("NGCERT-", { timeout: 60_000 });
  await expect(page.getByText("Ollama Explanation Generated or Fallback Active")).toBeVisible();
  await expect(page.getByText(/Success|Fallback/).first()).toBeVisible();
  const applicationNumber = (await page.getByTestId("demo-application-number").textContent())?.trim() || "";
  const certificateNumber = (await page.getByTestId("demo-certificate-number").textContent())?.trim() || "";
  const verificationHash = (await page.getByTestId("demo-verification-hash").textContent())?.trim() || "";
  expect(applicationNumber.length).toBeGreaterThan(6);
  expect(certificateNumber.length).toBeGreaterThan(6);
  expect(verificationHash.length).toBeGreaterThan(12);
  await expect(page.getByText(/Ollama Status: Online|Ollama Status: Fallback active/)).toBeVisible();
  await expect(page.locator("body")).not.toContainText(/Check your connection or use the text box/i);
  await screenshot(page, "final-two-portal-04-demo-result.png");

  await page.goto("/verify-certificate");
  await page.getByLabel("Certificate number or hash").fill(verificationHash);
  await page.getByRole("button", { name: "Verify" }).last().click();
  await expect(page.getByRole("heading", { name: "Certificate is valid" })).toBeVisible();
  await expect(page.getByText(certificateNumber)).toBeVisible();
  await screenshot(page, "final-two-portal-05-verification.png");

  await page.goto("/login");
  await page.getByLabel("Email").fill("admin@niyamguard.local");
  await page.getByLabel("Password").fill("Admin@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();

  await page.goto("/admin/compliance");
  await expect(page.getByRole("heading", { name: "Compliance" })).toBeVisible();
  await expect(page.getByText(/Compliance Findings|drifted systems/i).first()).toBeVisible();

  await page.goto("/admin/audit");
  await expect(page.getByRole("heading", { name: "Audit" })).toBeVisible();
  await expect(page.getByText(/Audit Log|full_end_to_end_demo/i).first()).toBeVisible();

  await page.goto("/government");
  await expect(page.getByText(/Ollama Status: Online|Ollama Status: Fallback active/)).toBeVisible();
  await expect(page.locator("body")).not.toContainText(/Check your connection or use the text box/i);
  await expect(page.locator("body")).not.toContainText(/Text assistant.*ready/i);

  const video = page.video();
  await page.close();
  if (video) {
    const sourcePath = await video.path();
    fs.copyFileSync(sourcePath, path.join(assetsDir, "final-two-portal-demo.webm"));
  }
});
