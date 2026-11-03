import { test, expect } from "@playwright/test";
import { randomUUID } from "node:crypto";

test("analyzes text through the running Python API", async ({ page }) => {
  await page.goto("/analyzer");
  await page.getByLabel("Your text", { exact: true }).fill("Python python learning");
  await page.getByRole("button", { name: "Analyze text", exact: true }).click();
  await expect(page.getByRole("cell", { name: "python", exact: true })).toBeVisible();
  await expect(page.getByRole("cell", { name: "2", exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("creates, reads, edits and deletes a fictional student", async ({ page }) => {
  const name = "Browser Learner " + randomUUID();
  await page.goto("/students");
  await page.getByLabel("Name", { exact: false }).fill(name);
  await page.getByLabel("Country *", { exact: true }).fill("Testland");
  await page.getByLabel("City *", { exact: true }).fill("Test City");
  await page.getByLabel("Date of birth").fill("2000-01-01");
  await page.getByLabel("Skills (comma separated)").fill("Python, React");
  await page.getByRole("button", { name: "Create student", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Student created." })).toBeVisible();
  await page.getByLabel("Filter by country").fill("Testland");
  await page.getByRole("button", { name: "Apply", exact: true }).click();
  await page.getByRole("button", { name, exact: true }).click();
  await expect(page.getByRole("region", { name: "Selected student" }).getByText("Test City, Testland")).toBeVisible();
  await page.getByRole("button", { name: "Edit " + name, exact: true }).click();
  await page.getByLabel("City *", { exact: true }).fill("Updated City");
  await page.getByRole("button", { name: "Save changes", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Student updated." })).toBeVisible();
  await expect(page.getByRole("region", { name: "Selected student" }).getByText("Updated City, Testland")).toBeVisible();
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "Delete " + name, exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Student deleted." })).toBeVisible();
  await expect(page.getByRole("button", { name, exact: true })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test("preserves text after an API failure", async ({ page }) => {
  await page.route("**/api/v1/analysis", route => route.fulfill({
    status: 503, contentType: "application/json", body: JSON.stringify({ detail: "Please try again" }),
  }));
  await page.goto("/analyzer");
  await page.getByLabel("Your text", { exact: true }).fill("Keep my text");
  await page.getByRole("button", { name: "Analyze text", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "Please try again" })).toBeVisible();
  await expect(page.getByLabel("Your text", { exact: true })).toHaveValue("Keep my text");
});
