import { expect, test } from "@playwright/test";

const runProductionExperience = process.env.NIYAMGUARD_PRODUCTION_E2E === "true";

test.describe("production citizen guidance", () => {
  test.skip(!runProductionExperience, "Run only against the production-facing local UI verification server.");

  test("keeps public services and guidance available without exposing evaluation controls", async ({ page }) => {
    const auditDirectory = "test-results/citizen-assistant-audit";
    await page.goto("/", { waitUntil: "networkidle" });

    await expect(page.getByRole("heading", { name: "Public Services" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Services" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Track" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Verify" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Need help?" })).toBeVisible();
    await expect(page.getByText(/synthetic government sandbox|run full demo|reset mock/i)).toHaveCount(0);
    await page.screenshot({ path: `${auditDirectory}/01-services.png`, fullPage: true });

    await page.getByRole("button", { name: "Need help?" }).click();
    await expect(page.getByRole("heading", { name: "How can we help?" })).toBeVisible();
    await page.screenshot({ path: `${auditDirectory}/02-chat-dock.png`, fullPage: true });
    await expect(page.getByRole("tab", { name: "Chat" })).toHaveAttribute("aria-selected", "true");
    await page.getByLabel("Language").selectOption("telugu");
    await page.getByLabel(/Ask about forms/).fill("income certificate validity entha");
    await page.getByRole("button", { name: "Ask" }).click();
    await expect(page.getByText("Guidance answer")).toBeVisible();

    await page.getByRole("tab", { name: "Voice" }).click();
    await expect(page.getByText(/Speak in English, Telugu, or Hindi/)).toBeVisible();
    await page.screenshot({ path: `${auditDirectory}/03-voice-dock.png`, fullPage: true });
  });
});
