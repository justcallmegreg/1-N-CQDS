// language-switch.spec.ts — the mandatory e2e case. Runtime switch + cookie persistence.
//
// MANDATORY e2e case: runtime language switch. The STRUCTURE is reusable as-is.
// Adapt TWO project-specific things when you copy this into a new app:
//   1. Your App must render the primary localized string in an element with
//      data-testid="app-tagline" (bound to t("app.tagline")). This spec drives it.
//   2. Replace the asserted tagline substrings below with YOUR en/de dictionary values.
import { test, expect } from "@playwright/test";

test("switches language at runtime without reload and persists via cookie", async ({ page }) => {
  await page.goto("/");
  // English is the default first paint.
  await expect(page.getByTestId("app-tagline")).toContainText("Record observations offline");

  // Switch to German — in place, no navigation.
  await page.getByTestId("language-select").selectOption("de");
  await expect(page.getByTestId("app-tagline")).toContainText("Beobachtungen offline erfassen");

  // The cookie was written.
  const cookies = await page.context().cookies();
  expect(cookies.find((c) => c.name === "locale")?.value).toBe("de");

  // Reload — the choice survives, and there is no flash back to English.
  await page.reload();
  await expect(page.getByTestId("app-tagline")).toContainText("Beobachtungen offline erfassen");
});
