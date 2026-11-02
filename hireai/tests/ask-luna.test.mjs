import assert from "node:assert/strict";
import { after, test } from "node:test";

const originalWebhookUrl = process.env.LUNA_WEBHOOK_URL;
process.env.LUNA_WEBHOOK_URL =
  "https://dongle036-n8n.dochelper.org/webhook-test/agent/luna";
const { handler } = await import("../../netlify/functions/ask-luna.mjs");
const originalFetch = globalThis.fetch;
after(() => {
  globalThis.fetch = originalFetch;
  if (originalWebhookUrl === undefined) {
    delete process.env.LUNA_WEBHOOK_URL;
  } else {
    process.env.LUNA_WEBHOOK_URL = originalWebhookUrl;
  }
});

const callHandler = (event) => handler({
  httpMethod: "POST",
  body: JSON.stringify({ message: "Hello Luna", sessionId: "luna-test" }),
  ...event,
});

test("forwards a valid chat request and extracts an n8n array response", async () => {
  globalThis.fetch = async (url, options) => {
    assert.equal(url, "https://dongle036-n8n.dochelper.org/webhook-test/agent/luna");
    assert.equal(options.method, "POST");
    assert.deepEqual(JSON.parse(options.body), {
      message: "Hello Luna",
      chatInput: "Hello Luna",
      sessionId: "luna-test",
    });
    return new Response(JSON.stringify([{ output: "Hi, how can I help?" }]), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  const result = await callHandler({});
  assert.equal(result.statusCode, 200);
  assert.deepEqual(JSON.parse(result.body), { reply: "Hi, how can I help?" });
});

test("rejects malformed or oversized requests without calling the webhook", async () => {
  globalThis.fetch = async () => {
    throw new Error("Webhook should not be called for invalid input.");
  };

  const malformed = await handler({ httpMethod: "POST", body: "{" });
  assert.equal(malformed.statusCode, 400);

  const oversized = await callHandler({
    body: JSON.stringify({ message: "x".repeat(4001), sessionId: "luna-test" }),
  });
  assert.equal(oversized.statusCode, 400);
});

test("returns an explicit error when the webhook fails", async () => {
  globalThis.fetch = async () => new Response("unavailable", { status: 503 });

  const result = await callHandler({});
  assert.equal(result.statusCode, 502);
  assert.match(JSON.parse(result.body).error, /HTTP 503/);
});

test("rejects methods other than POST", async () => {
  const result = await handler({ httpMethod: "GET" });
  assert.equal(result.statusCode, 405);
});
