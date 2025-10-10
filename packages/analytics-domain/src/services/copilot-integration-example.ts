/**
 * Beispiel-Integration des Analytics Copilot Service in den MCP-Server
 * 
 * Diese Datei zeigt, wie der Copilot-Service in einen bestehenden
 * Express/HTTP-Server integriert wird.
 */

import http from "http"
import express from "express"
import type { IncomingMessage } from "http"
import type { Duplex } from "stream"
import { createCopilotService } from "./analytics-copilot-service"

/**
 * Erstellt und konfiguriert den MCP-Server mit Copilot-Integration
 */
export function setupMCPServerWithCopilot(): http.Server {
  const app = express()
  const server = http.createServer(app)

  // Bestehende Middleware
  app.use(express.json())

  // Copilot-Service erstellen
  const { app: copilotApp, wss } = createCopilotService()

  // Copilot-Routen unter /mcp/copilot mounten
  app.use("/mcp/copilot", copilotApp)

  // Weitere bestehende Routen...
  // app.use("/mcp/analytics", analyticsRouter)
  // app.use("/mcp/inventory", inventoryRouter)

  // WebSocket Upgrade Handler
  server.on(
    "upgrade",
    (request: IncomingMessage, socket: Duplex, head: Buffer): void => {
      if (request.url === "/mcp/copilot/ws") {
        wss.handleUpgrade(request, socket, head, (ws): void => {
          wss.emit("connection", ws, request)
        })
      }
    }
  )

  return server
}

/**
 * Startet den Server
 */
export function startServer(): void {
  const server = setupMCPServerWithCopilot()
  const port = process.env.PORT ?? "7070"

  server.listen(port, (): void => {
    // eslint-disable-next-line no-console
    console.info(`🚀 MCP Server läuft auf Port ${port}`)
    // eslint-disable-next-line no-console
    console.info(`📡 Copilot WebSocket: ws://localhost:${port}/mcp/copilot/ws`)
    // eslint-disable-next-line no-console
    console.info(`🤖 Copilot API: http://localhost:${port}/mcp/copilot/analyze`)
  })
}

// Wenn direkt ausgeführt
if (require.main === module) {
  startServer()
}
