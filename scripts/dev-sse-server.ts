/* eslint-disable no-console */
import express from "express";
import { randomUUID } from "crypto";

const app = express();
const PORT = Number(process.env.SSE_PORT ?? 5174);

function send(res: express.Response, event: unknown): void {
  res.write(`data: ${JSON.stringify(event)}\n\n`);
}

app.get("/api/events", (req, res) => {
  if (req.query.stream !== "mcp") {
    res.status(404).end();
    return;
  }

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const logInterval = setInterval(() => {
    send(res, {
      id: randomUUID(),
      ts: new Date().toISOString(),
      source: "mcp",
      topic: "log",
      level: "info",
      scope: "dev-server",
      text: "heartbeat ok",
    });
  }, 5_000);

  const toastTimeout = setTimeout(() => {
    send(res, {
      id: randomUUID(),
      ts: new Date().toISOString(),
      source: "mcp",
      topic: "toast",
      variant: "success",
      title: "MCP connected",
      description: "Realtime stream established.",
    });
  }, 1_200);

  req.on("close", () => {
    clearInterval(logInterval);
    clearTimeout(toastTimeout);
  });
});

app.listen(PORT, () => {
  console.log(`Dev SSE server available at http://localhost:${PORT}/api/events?stream=mcp`);
});
