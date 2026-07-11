import { expect, test } from "@playwright/test";

const API_BASE_URL = process.env.VITE_API_BASE_URL || "http://127.0.0.1:8010";

const citizenRoutes = [
  "/citizen",
  "/citizen/assistant",
  "/services",
  "/scheme-finder",
  "/apply/income_certificate",
  "/track",
];

async function loginCitizen(page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Citizen" }).click();
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByText(/Citizen Portal - landing/i)).toBeVisible();
}

async function loginOfficer(page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Officer" }).click();
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Policy Operations" })).toBeVisible();
}

async function loginAdmin(page) {
  await page.goto("/login");
  await page.getByRole("button", { name: "Admin" }).click();
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: "Policy Operations" })).toBeVisible();
}

async function logout(page) {
  await page.getByRole("button", { name: "Logout" }).click();
  await expect(page.getByRole("heading", { name: "NiyamGuard Login" })).toBeVisible();
}

async function loginWithCredentials(page, email, password, expectedHeading) {
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.getByRole("heading", { name: expectedHeading })).toBeVisible();
}

test("unified NiyamGuard app satisfies citizen, government, admin, and sandbox flows", async ({ page, request }) => {
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];
  const failedResponses: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400) failedResponses.push(`${response.status()} ${response.url()}`);
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "NiyamGuard" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Citizen Portal" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Government Portal" })).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();

  await loginCitizen(page);

  for (const route of citizenRoutes) {
    await page.goto(route);
    await expect(page.locator("#global-citizen-voice-assistant")).toBeVisible();
  }

  await page.goto("/verify-certificate");
  await expect(page.locator(".app-route-label")).toHaveText("Certificate Verification");

  await page.goto("/citizen");
  await expect(page.getByText(/Citizen Portal - landing/i)).toBeVisible();
  await page.getByRole("button", { name: "Type" }).click();
  await page.getByLabel("Message").fill("residence certificate documents");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.getByText(/For Residence Certificate, the required documents are/i)).toBeVisible();
  await expect(page.getByText("Certificate Baseline")).toBeVisible();

  await logout(page);

  await loginOfficer(page);

  await page.goto("/government");
  await expect(page.getByRole("heading", { name: "Policy Operations" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Overview" })).toBeVisible();
  await expect(page.locator("#global-citizen-voice-assistant")).toHaveCount(0);

  // Regression check: statistics cards must display actual seeded non-zero counts, not a generic error or 0
  await expect(page.locator("article:has-text('Circulars') strong")).not.toHaveText("0");
  await expect(page.locator("article:has-text('Rule Candidates') strong")).not.toHaveText("0");
  await expect(page.locator("article:has-text('Open Mismatches') strong")).not.toHaveText("0");
  await expect(page.locator("article:has-text('Critical Priority') strong")).not.toHaveText("0");

  const uploadedCircularNumber = `GO-OFFICER-${Date.now()}`;
  await page.getByLabel("Circular document").setInputFiles({
    name: "officer-rule-change.txt",
    mimeType: "text/plain",
    buffer: Buffer.from(
      `${uploadedCircularNumber} Revenue Department circular. Income Certificate validity is changed from 12 months to 6 months.`,
    ),
  });
  await page.getByLabel("Circular ID / number").fill(uploadedCircularNumber);
  await page.getByLabel("Title").fill("Officer Uploaded Income Certificate Update");
  await page.getByLabel("Department").fill("Revenue Department");
  await page.getByLabel("Effective date").fill("2026-11-01");
  await page.getByRole("button", { name: "Upload & Extract" }).click();
  await expect(page.getByText(/rule candidate\(s\) are pending review at 91% confidence/i)).toBeVisible();

  const officerToken = await page.evaluate(() => window.localStorage.getItem("niyamguard.access_token"));
  const uploadedDocuments = await request.get(`${API_BASE_URL}/api/circulars`, {
    headers: { Authorization: `Bearer ${officerToken}` },
  });
  const uploadedDocument = (await uploadedDocuments.json()).circulars.find(
    (item) => item.circular_number === uploadedCircularNumber,
  );
  expect(uploadedDocument).toBeTruthy();
  await page.getByRole("button", { name: "Circular Intake" }).click();
  const candidateRow = page.locator("table.admin-table tbody tr").filter({ hasText: uploadedDocument.id });
  await candidateRow.getByRole("button", { name: "Approve & Check" }).click();
  await expect(page.getByText("Rule approved, published, and compliance checks completed.")).toBeVisible();

  await logout(page);

  await loginAdmin(page);
  await expect(page.locator(".admin-loading")).toHaveCount(0);

  await page.goto("/admin/impact");
  await expect(page.getByRole("heading", { name: "Impact" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Citizen Impact Dashboard" })).toBeVisible();
  await expect(page.getByText("Priority / Urgency")).toBeVisible();
  await expect(page.getByRole("img", { name: "Findings over time chart" })).toBeVisible();
  await expect(page.getByText("By Department")).toBeVisible();
  await expect(page.getByText("By Service")).toBeVisible();

  await page.goto("/admin/policy-updates");
  await expect(page.getByRole("heading", { name: "Policy Updates" })).toBeVisible();
  const policyTable = page.locator("table.admin-table").first();
  await expect(policyTable.getByRole("columnheader", { name: "Circular ID" })).toBeVisible();
  await expect(policyTable.getByRole("columnheader", { name: "Service affected" })).toBeVisible();
  await expect(policyTable.getByRole("columnheader", { name: "What Changed" })).toBeVisible();
  await expect(policyTable.getByRole("columnheader", { name: "Status" })).toBeVisible();
  await expect(policyTable.getByRole("columnheader", { name: "Date" })).toBeVisible();
  await expect(policyTable.getByRole("columnheader", { name: "Confidence" })).toHaveCount(0);
  await policyTable.locator("tbody tr").first().click();
  await expect(page.getByLabel("Policy update details")).toBeVisible();

  await page.goto("/virtual-gov");
  await expect(page.getByRole("heading", { name: "Virtual Government Sandbox" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Sandbox Holding Area" })).toBeVisible();
  const uiCircularNumber = `GO-UI-${Date.now()}`;
  await page.getByLabel("Circular Number").fill(uiCircularNumber);
  await page.getByLabel("Effective Date").fill("2026-12-01");
  await page.locator("form").getByRole("button", { name: "Generate PDF" }).click();
  const generatedRow = page.locator("tbody tr").filter({ hasText: uiCircularNumber }).first();
  await expect(generatedRow).toBeVisible();
  await expect(generatedRow.getByRole("button", { name: "Open PDF" })).toBeEnabled();
  await expect(generatedRow.getByRole("button", { name: "Publish to NiyamGuard" })).toBeEnabled();
  await generatedRow.getByRole("button", { name: "Publish to NiyamGuard" }).click();
  await expect(page.getByRole("heading", { name: "Government Delivery" })).toBeVisible();
  await expect(page.getByText(/published to the NiyamGuard Government Circular Inbox/i)).toBeVisible();

  const login = await request.post(`${API_BASE_URL}/api/auth/login`, {
    data: { email: "admin@niyamguard.local", password: "Admin@12345" },
  });
  expect(login.ok()).toBeTruthy();
  const { access_token: token } = await login.json();
  const circularNumber = `GO-E2E-${Date.now()}`;
  const create = await request.post(`${API_BASE_URL}/api/sandbox/circulars`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {
      department: "Revenue Department",
      circular_number: circularNumber,
      title: "E2E Sandbox Circular",
      service_affected: "Income Certificate",
      rule_key: "validity",
      old_value: "12 months",
      new_value: "6 months",
      body: "Playwright verifies sandbox publishing into the officer review inbox.",
    },
  });
  expect(create.ok()).toBeTruthy();
  const created = await create.json();
  const circularId = created.circular.id;
  const pdf = await request.post(`${API_BASE_URL}/api/sandbox/circulars/${circularId}/generate-pdf`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {},
  });
  expect(pdf.ok()).toBeTruthy();
  const published = await request.post(`${API_BASE_URL}/api/sandbox/circulars/${circularId}/publish`, {
    headers: { Authorization: `Bearer ${token}` },
    data: {},
  });
  expect(published.ok()).toBeTruthy();
  const inbox = await request.get(`${API_BASE_URL}/api/government/circular-inbox`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  expect(inbox.ok()).toBeTruthy();
  expect(JSON.stringify(await inbox.json())).toContain(circularNumber);

  await logout(page);
  await loginWithCredentials(page, "reviewer@niyamguard.local", "Reviewer@12345", "Policy Operations");
  expect(page.url()).toContain("/government");
  await expect(page.locator(".admin-loading")).toHaveCount(0);
  await logout(page);
  await loginWithCredentials(page, "sandbox@niyamguard.local", "Sandbox@12345", "Virtual Government Sandbox");
  expect(page.url()).toContain("/sandbox");

  expect(consoleErrors).toEqual([]);
  expect(pageErrors).toEqual([]);
  expect(failedResponses).toEqual([]);
});
