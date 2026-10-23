// Prepared for execution on a local isolated demo; NOT executed in the build environment.
import { test, expect } from "@playwright/test";
test("worker reports a case through MCP and sees it after refresh", async ({
  page,
}) => {
  test.skip(
    !process.env.DEMO_PASSWORD,
    "Set DEMO_PASSWORD for an isolated local demo",
  );
  await page.goto("/");
  await page.getByLabel("Email address").fill("alex@demo.carrysafe.test");
  await page
    .getByLabel("Password", { exact: true })
    .fill(process.env.DEMO_PASSWORD!);
  await page.getByRole("button", { name: "Enter workspace" }).click();
  await expect(
    page.getByRole("heading", { name: "Nothing left behind." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Brief me on the handover", exact: false })
    .click();
  await expect(
    page.getByText("list_open_incidents", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Report incident", exact: true })
    .click();
  await page
    .getByLabel("Description *")
    .fill("SYNTHETIC browser verification: oil leak at loading bay");
  await page
    .getByLabel("Location id *")
    .selectOption({ label: "Loading Bay 2" });
  await page
    .getByLabel("Shift id *")
    .selectOption({ label: "Shift A — Morning" });
  await page
    .getByRole("button", { name: "Review change", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirm and save", exact: true })
    .click();
  await expect(
    page.getByText(
      "Incident recorded through MCP. The confirmed record is below.",
    ),
  ).toBeVisible();
  await page.getByRole("link", { name: "Operations", exact: true }).click();
  await page
    .getByLabel("Search incidents")
    .fill("SYNTHETIC browser verification");
  await expect(
    page
      .getByText("SYNTHETIC browser verification: oil leak at loading bay", {
        exact: false,
      })
      .first(),
  ).toBeVisible();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: "The work in progress." }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("heading", { name: "The work in progress." }),
  ).toBeVisible();
});
