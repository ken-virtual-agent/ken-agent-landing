const WEBHOOK_URL =
  process.env.LUNA_WEBHOOK_URL ||
  "https://dongle036-n8n.dochelper.org/webhook/agent/luna";

const jsonResponse = (statusCode, body) => ({
  statusCode,
  headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  },
  body: JSON.stringify(body),
});

const extractReply = (text) => {
  if (!text.trim()) {
    throw new Error("The Luna webhook returned an empty response.");
  }

  let response;
  try {
    response = JSON.parse(text);
  } catch {
    return text;
  }

  if (Array.isArray(response)) {
    response = response[0];
  }

  if (typeof response === "string") {
    return response;
  }

  const reply =
    response?.output ??
    response?.reply ??
    response?.response ??
    response?.text ??
    response?.message;

  return typeof reply === "string" ? reply : JSON.stringify(response);
};

export const handler = async (event) => {
  if (event.httpMethod !== "POST") {
    return jsonResponse(405, { error: "Method not allowed." });
  }

  let data;
  try {
    data = JSON.parse(event.body || "");
  } catch {
    return jsonResponse(400, { error: "Request body must be valid JSON." });
  }

  if (
    !data ||
    typeof data.message !== "string" ||
    !data.message.trim() ||
    data.message.length > 4000 ||
    typeof data.sessionId !== "string" ||
    !data.sessionId.trim()
  ) {
    return jsonResponse(400, {
      error: "A message of 1-4000 characters and a session ID are required.",
    });
  }

  try {
    const response = await fetch(WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: data.message.trim(),
        chatInput: data.message.trim(),
        sessionId: data.sessionId.slice(0, 100),
      }),
      signal: AbortSignal.timeout(30000),
    });

    if (!response.ok) {
      console.error(`Luna webhook returned HTTP ${response.status}.`);
      return jsonResponse(502, {
        error: `Luna is unavailable (webhook HTTP ${response.status}).`,
      });
    }

    const reply = extractReply(await response.text());
    return jsonResponse(200, { reply });
  } catch (error) {
    console.error("Luna webhook request failed:", error);
    if (error.name === "TimeoutError" || error.name === "AbortError") {
      return jsonResponse(504, { error: "Luna's response timed out. Please try again." });
    }
    return jsonResponse(502, { error: "Unable to reach Luna. Please try again." });
  }
};
