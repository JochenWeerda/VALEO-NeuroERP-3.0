/* eslint-disable no-console */
const express = require("express");
const { randomUUID } = require("crypto");

const app = express();
const PORT = Number(process.env.SSE_PORT ?? 5174);

function send(res, event) {
  res.write(`data: ${JSON.stringify(event)}\n\n`);
}

// very small CORS helper so Vite dev server can consume SSE locally
app.use((req, res, next) => {
  const origin = req.headers.origin ?? "*";
  res.header("Access-Control-Allow-Origin", origin);
  res.header("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.header("Access-Control-Allow-Credentials", "true");
  res.header("Vary", "Origin");

  if (req.method === "OPTIONS") {
    res.sendStatus(204);
    return;
  }

  next();
});

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    timestamp: new Date().toISOString(),
  });
});

app.get("/api/events", (req, res) => {
  const stream = req.query.stream;
  if (stream !== "mcp") {
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
