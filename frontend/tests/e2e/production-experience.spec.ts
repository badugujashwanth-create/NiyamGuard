import { expect, test } from "@playwright/test";

const runProductionExperience = process.env.NIYAMGUARD_PRODUCTION_E2E === "true";

test.describe("production experience", () => {
  test.skip(!runProductionExperience, "Run only against the production-facing local UI verification server.");
  test.describe.configure({ mode: "serial" });

  test("keeps the policy workflow focused and hides evaluation controls", async ({ page }) => {
    await page.goto("/login", { waitUntil: "networkidle" });
    await expect(page.getByRole("heading", { name: "NiyamGuard" })).toBeVisible();
    await expect(page.getByText(/Demo admin:/)).toHaveCount(0);
    await expect(page.getByText(/evaluation workspace/i)).toHaveCount(0);
    await expect(page.getByRole("link", { name: /public demo|citizen app/i })).toHaveCount(0);

    await page.getByLabel("Email").fill(process.env.NIYAMGUARD_E2E_EMAIL || "admin@niyamguard.local");
    await page.getByLabel("Password").fill(process.env.NIYAMGUARD_E2E_PASSWORD || "Admin@12345");
    await page.getByRole("button", { name: "Sign In" }).click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("Loading policy operations...")).toHaveCount(0);
    await expect(page.getByRole("button", { name: "Run Full Demo" })).toHaveCount(0);
    await expect(page.getByRole("button", { name: /reset mocks|patch mocks/i })).toHaveCount(0);

    const routes = [
      ["Circulars", "Circular Intake"],
      ["Rule Review", "Rule Review"],
      ["Verified Rules", "Verified Rules"],
      ["Connected Systems", "Connected Systems"],
      ["Drift Findings", "Drift Findings"],
      ["Impact", "Citizen Impact Dashboard"],
      ["Remediation", "Remediation"],
      ["Audit", "Audit Log"],
      ["Reports", "Reports"],
    ];

    for (const [navigationLabel, pageContent] of routes) {
      await page.getByRole("button", { name: navigationLabel, exact: true }).click();
      await expect(page.getByText(pageContent, { exact: true }).first()).toBeVisible();
      await expect(page.getByText(/mock|sandbox|synthetic/i)).toHaveCount(0);
    }
  });

  test("captures the final desktop and mobile production audit", async ({ page }) => {
    const auditDirectory = "test-results/production-screenshot-audit";
    const capture = async (name) => page.screenshot({ path: `${auditDirectory}/${name}.png`, fullPage: true });

    await page.goto("/login", { waitUntil: "networkidle" });
    await capture("01-login");
    await page.getByLabel("Email").fill(process.env.NIYAMGUARD_E2E_EMAIL || "admin@niyamguard.local");
    await page.getByLabel("Password").fill(process.env.NIYAMGUARD_E2E_PASSWORD || "Admin@12345");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("Loading policy operations...")).toHaveCount(0);
    await capture("02-dashboard");

    const captureRoute = async (navigationLabel, content, imageName) => {
      await page.getByRole("button", { name: navigationLabel, exact: true }).click();
      await expect(page.getByText(content, { exact: true }).first()).toBeVisible();
      await expect(page.getByText("Loading policy operations...")).toHaveCount(0);
      await capture(imageName);
    };

    await captureRoute("Circulars", "Circular Intake", "03-circulars");
    await capture("04-circular-upload");
    await captureRoute("Rule Review", "Rule Review", "05-rule-review");
    await capture("06-source-evidence");
    await captureRoute("Verified Rules", "Verified Rules", "07-rule-timeline");
    await captureRoute("Connected Systems", "Connected Systems", "08-systems");
    await captureRoute("Drift Findings", "Drift Findings", "09-drift-findings");
    await captureRoute("Impact", "Citizen Impact Dashboard", "10-impact");
    await captureRoute("Remediation", "Remediation", "11-remediation");
    await captureRoute("Audit", "Audit Log", "12-audit");
    await captureRoute("Reports", "Reports", "13-reports");

    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole("button", { name: "Menu", exact: true }).click();
    await page.getByRole("button", { name: "Dashboard", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await capture("14-mobile-dashboard");
    await page.getByRole("button", { name: "Menu", exact: true }).click();
    await page.getByRole("button", { name: "Rule Review", exact: true }).click();
    await expect(page.getByRole("heading", { name: "Rule Review", level: 2, exact: true })).toBeVisible();
    await capture("15-mobile-rule-review");
  });
});
