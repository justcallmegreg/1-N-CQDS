// playwright.config.ts — lives at repo /e2e; drives the frontend dev server.
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  timeout: 30_000,
  use: { baseURL: process.env.BASE_URL ?? "http://localhost:5173", trace: "on-first-retry" },
  webServer: process.env.BASE_URL
    ? undefined
    : { command: "npm --prefix ../frontend run dev", url: "http://localhost:5173", reuseExistingServer: true, timeout: 60_000 },
});
