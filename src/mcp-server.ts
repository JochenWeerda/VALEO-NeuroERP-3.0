/**
 * MCP Server - Policy Manager Backend
 * Minimaler Express-Server für Policy-Management
 */

import express from "express"
import http from "http"
import { PolicyStore } from "./services/policy/store-sqlite"
import { createPolicyRouter } from "./services/policy/routes"

const app = express()
app.use(express.json())

// CORS für Frontend
app.use((_req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*")
  res.header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization")
  if (_req.method === "OPTIONS") {
    res.sendStatus(200)
    return
  }
  next()
})

// Policy-Store initialisieren
const policyStore = new PolicyStore(process.env.POLICY_DB ?? "data/policies.db")

// Policy-Routes mounten
app.use("/api/mcp/policy", createPolicyRouter(policyStore))

// Health-Check
app.get("/healthz", (_req, res) => {
  res.json({ ok: true, service: "policy-mcp-server" })
})

// 404-Handler
app.use((_req, res) => {
  res.status(404).json({ ok: false, error: "Not Found" })
})

// Server starten
const server = http.createServer(app)
const port = Number(process.env.PORT ?? 7070)

server.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`🚀 MCP Policy Server listening on http://localhost:${port}`)
  // eslint-disable-next-line no-console
  console.log(`📊 Policy endpoints available at http://localhost:${port}/api/mcp/policy/*`)
})

// Graceful Shutdown
process.on("SIGTERM", () => {
  // eslint-disable-next-line no-console
  console.log("SIGTERM signal received: closing HTTP server")
  server.close(() => {
    // eslint-disable-next-line no-console
    console.log("HTTP server closed")
  })
})

