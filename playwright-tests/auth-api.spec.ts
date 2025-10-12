import { test, expect } from "@playwright/test";

const apiBase = process.env.API_URL;
const devToken = process.env.API_DEV_TOKEN ?? "dev-token";

test.describe("API authentication", () => {
  test.skip(!apiBase, "API_URL not configured for API authentication checks");

  test("rejects unauthenticated requests", async ({ request }) => {
    const response = await request.get(`${apiBase}/api/v1/status`);
    expect(response.status()).toBe(401);
  });

  test("accepts requests with dev token", async ({ request }) => {
    const response = await request.get(`${apiBase}/api/v1/status`, {
      headers: {
        Authorization: `Bearer ${devToken}`,
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.status).toBe("ok");
  });
});
