import { expect, test } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

const baseUrl = process.env.DEMO_BASE_URL || "http://127.0.0.1:5180";
const assetsDir = path.resolve(process.cwd(), "../docs/recording-assets");

function demoPdf() {
  // Generated from the repository's own `build_simple_pdf` helper so the UI
  // test exercises the same valid-PDF intake boundary as the demo artifact.
  return Buffer.from(
    "JVBERi0xLjQKMSAwIG9iajw8IC9UeXBlIC9DYXRhbG9nIC9QYWdlcyAyIDAgUiA+PmVuZG9iagoyIDAgb2JqPDwgL1R5cGUgL1BhZ2VzIC9LaWRzIFszIDAgUl0gL0NvdW50IDEgPj5lbmRvYmoKMyAwIG9iajw8IC9UeXBlIC9QYWdlIC9QYXJlbnQgMiAwIFIgL01lZGlhQm94IFswIDAgNjEyIDc5Ml0gL0NvbnRlbnRzIDQgMCBSIC9SZXNvdXJjZXM8PCAvRm9udDw8IC9GMSA1IDAgUiA+PiA+PiA+PmVuZG9iago0IDAgb2JqPDwgL0xlbmd0aCAyNzUgPj5zdHJlYW0KQlQgL0YxIDExIFRmCjUwIDc4MCBUZCAoR08tMTM4IFJldmlldzogSW5jb21lIENlcnRpZmljYXRlIHZhbGlkaXR5IGNoYW5nZWQgZnJvbSAxMiBtb250aHMgdG8gNiBtb250aHMuKSBUaiAwIC0xNiBUZAo1MCA3NjQgVGQgKEVmZmVjdGl2ZSAyMDI2LTA4LTAxLiBFeHBpcmVzIG9uIDIwMjctMDctMzEuKSBUaiAwIC0xNiBUZAo1MCA3NDggVGQgKFN5bnRoZXRpYyByZXZpZXcgYXJ0aWZhY3QgZm9yIGxvY2FsIE5peWFtR3VhcmQgc2ltdWxhdGlvbiBvbmx5LikgVGogMCAtMTYgVGQKRVQKZW5kc3RyZWFtCmVuZG9iago1IDAgb2JqPDwgL1R5cGUgL0ZvbnQgL1N1YnR5cGUgL1R5cGUxIC9CYXNlRm9udCAvSGVsdmV0aWNhID4+ZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDU2IDAwMDAwIG4gCjAwMDAwMDAxMTEgMDAwMDAgbiAKMDAwMDAwMDIzMyAwMDAwMCBuIAowMDAwMDAwNTU3IDAwMDAwIG4gCnRyYWlsZXI8PCAvU2l6ZSA2IC9Sb290IDEgMCBSID4+CnN0YXJ0eHJlZgo2MjUKJSVFT0YK",
    "base64",
  );
}

async function capture(page, name: string) {
  fs.mkdirSync(assetsDir, { recursive: true });
  await page.screenshot({ path: path.join(assetsDir, name), fullPage: true });
}

test("final synthetic PDF-to-remediation simulation", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto(`${baseUrl}/`);
  await expect(page.getByRole("heading", { name: "A government rule changed. Downstream systems are still wrong." })).toBeVisible();
  await capture(page, "e2e-step-01-landing.png");

  await page.goto(`${baseUrl}/government`);
  await page.getByRole("button", { name: "Run Connected Policy Lifecycle" }).click();
  await expect(page.getByRole("status", { name: "Status: success" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByTestId("lifecycle-evidence")).toContainText("GO-138");
  await capture(page, "e2e-step-02-policy-lifecycle.png");

  await page.goto(`${baseUrl}/login`);
  await page.getByLabel("Email").fill("admin@niyamguard.local");
  await page.getByLabel("Password").fill("Admin@12345");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("main", { name: "Dashboard" })).toBeVisible();

  await page.goto(`${baseUrl}/admin/circulars`);
  await expect(page.getByRole("heading", { name: "Circular Intake" })).toBeVisible();
  await capture(page, "e2e-step-03-circular-upload.png");
  await page.getByLabel("Circular source file").setInputFiles({
    name: "go-138-review.pdf",
    mimeType: "application/pdf",
    buffer: demoPdf(),
  });
  await page.getByRole("button", { name: "Upload and validate circular" }).click();
  await expect(page.getByRole("status")).toContainText("Uploaded GO-138-REVIEW", { timeout: 30_000 });
  await expect(page.getByRole("alert")).toHaveCount(0);
  const uploadedRow = page.locator("tr").filter({ hasText: "GO-138-REVIEW" });
  await expect(uploadedRow).toBeVisible();
  await uploadedRow.getByRole("button", { name: "Extract Rules" }).click();
  await expect(page.getByRole("status")).toContainText("Rule extraction completed.", { timeout: 30_000 });
  await capture(page, "e2e-step-04-extraction-evidence.png");

  await page.goto(`${baseUrl}/admin/rule-candidates`);
  const candidates = page.locator(".admin-finding-card");
  const newestCandidate = candidates.last();
  await expect(newestCandidate).toContainText("6 months");
  await newestCandidate.getByRole("button", { name: "Approve" }).click();
  await expect(page.getByRole("status")).toContainText("Candidate approved.", { timeout: 30_000 });
  await capture(page, "e2e-step-05-human-approval.png");
  await newestCandidate.getByRole("button", { name: "Publish" }).click();
  await expect(page.getByRole("status")).toContainText("Policy update published.", { timeout: 30_000 });
  await capture(page, "e2e-step-06-policy-publication.png");

  await page.goto(`${baseUrl}/admin/compliance`);
  await expect(page.getByRole("heading", { name: "Compliance" })).toBeVisible();
  await capture(page, "e2e-step-07-drift.png");
  await page.goto(`${baseUrl}/admin/cascade`);
  await expect(page.getByRole("heading", { name: "Cascade" })).toBeVisible();
  await capture(page, "e2e-step-08-impact.png");

  await page.goto(`${baseUrl}/admin/propagation`);
  await page.getByRole("button", { name: "Patch Mocks" }).click();
  await expect(page.getByRole("status")).toContainText("Mock systems patched.", { timeout: 30_000 });
  await capture(page, "e2e-step-09-remediation.png");
  await page.goto(`${baseUrl}/admin/audit`);
  await expect(page.getByRole("heading", { name: "Audit" })).toBeVisible();
  await capture(page, "e2e-step-10-audit.png");

  await page.goto(`${baseUrl}/citizen`);
  const citizenQuestion = page.locator("#citizen-question");
  await citizenQuestion.fill("income certificate validity entha");
  await page.getByRole("button", { name: "Ask Assistant" }).last().click();
  await expect(page.getByTestId("citizen-hybrid-output")).toContainText(/6 months/i, { timeout: 30_000 });
  await capture(page, "e2e-step-11-grounded-answer.png");
  await citizenQuestion.fill("What is the secret subsidy formula for next year?");
  await page.getByRole("button", { name: "Ask Assistant" }).last().click();
  await expect(page.getByTestId("citizen-hybrid-output")).toContainText("Verified data is not available", { timeout: 30_000 });
  await capture(page, "e2e-step-12-safe-fallback.png");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${baseUrl}/`);
  expect(await page.locator("html").evaluate((node) => node.scrollWidth === node.clientWidth)).toBe(true);
  await capture(page, "e2e-step-13-mobile.png");
});
