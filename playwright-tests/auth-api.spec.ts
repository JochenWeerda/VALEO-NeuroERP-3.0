import { test, expect } from "@playwright/test";
import { apiToken } from "./helpers/anmeldung";

const apiBase = process.env.API_URL;

test.describe("API authentication", () => {
  test.skip(!apiBase, "API_URL not configured for API authentication checks");

  test("rejects unauthenticated requests", async ({ request }) => {
    const response = await request.get(`${apiBase}/api/v1/status`);
    expect(response.status()).toBe(401);
  });

  test("accepts requests with a provider token", async ({ request }) => {
    const response = await request.get(`${apiBase}/api/v1/status`, {
      headers: {
        Authorization: `Bearer ${apiToken()}`,
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ok");
  });
});
