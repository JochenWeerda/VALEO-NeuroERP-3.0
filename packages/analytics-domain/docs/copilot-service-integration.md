# Analytics Copilot Service - Integration Guide

## Phase F - Backend MCP-Copilot-Service

Dieser Guide beschreibt die Integration des Analytics Copilot Service in das VALEO NeuroERP Backend.

## Übersicht

Der Analytics Copilot Service ist ein LLM-agnostischer Backend-Service, der:
- KPIs und Trends analysiert
- GPT/LLM-basierte Insights generiert
- WebSocket-Events für Realtime-Updates bereitstellt
- Vollständig typisiert ist (TypeScript + Zod)
- Production-ready mit Error-Handling

## Architektur

```
┌──────────────────────────────┐
│  analytics-copilot-service   │  ← MCP-Domain-Service
├──────────────────────────────┤
│  POST /analyze               │  ← empfängt KPIs & Trends
│  ├─ Zod-Validation           │
│  ├─ Prompt-Generierung       │
│  ├─ LLM API Call             │
│  ├─ JSON-Parsing             │
│  └─ WebSocket Broadcast      │
│                              │
│  GET /health                 │  ← Health-Check
│  WS /ws                      │  ← WebSocket-Verbindung
└──────────────────────────────┘
```

## Installation

### 1. Dependencies prüfen

Der Service benötigt folgende Dependencies (sollten bereits installiert sein):

```json
{
  "express": "^4.18.0",
  "node-fetch": "^3.3.0",
  "ws": "^8.14.0",
  "zod": "^3.22.0"
}
```

### 2. Umgebungsvariablen konfigurieren

Erstelle eine `.env` Datei im `analytics-domain` Package:

```bash
# LLM API Configuration
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini

# Server Configuration
PORT=7070
NODE_ENV=development
```

### Alternative LLM-Provider

#### OpenRouter
```bash
LLM_API_URL=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=your-openrouter-key
LLM_MODEL=anthropic/claude-3-sonnet
```

#### Ollama (Local)
```bash
LLM_API_URL=http://localhost:11434/v1/chat/completions
LLM_API_KEY=ollama
LLM_MODEL=llama2
```

#### Azure OpenAI
```bash
LLM_API_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2023-05-15
LLM_API_KEY=your-azure-key
LLM_MODEL=gpt-4
```

## Integration

### Option 1: In bestehenden MCP-Server integrieren

```typescript
// src/index.ts oder src/server.ts
import http from "http"
import express from "express"
import { createCopilotService } from "./services/analytics-copilot-service"

const app = express()
const server = http.createServer(app)

// Bestehende Middleware
app.use(express.json())

// Copilot-Service
const { app: copilotApp, wss } = createCopilotService()
app.use("/mcp/copilot", copilotApp)

// WebSocket Upgrade
server.on("upgrade", (req, socket, head) => {
  if (req.url === "/mcp/copilot/ws") {
    wss.handleUpgrade(req, socket, head, (ws) => {
      wss.emit("connection", ws, req)
    })
  }
})

// Start
const port = process.env.PORT ?? 7070
server.listen(port, () => {
  console.log(`🚀 MCP Server läuft auf Port ${port}`)
})
```

### Option 2: Standalone-Service

```typescript
// src/services/copilot-standalone.ts
import { startServer } from "./copilot-integration-example"

startServer()
```

Dann:
```bash
cd packages/analytics-domain
node dist/services/copilot-standalone.js
```

## API Endpoints

### POST /mcp/copilot/analyze

Analysiert KPIs und Trends und generiert Insights.

**Request:**
```json
{
  "kpis": [
    {
      "id": "rev",
      "label": "Umsatz (Monat)",
      "value": 483210,
      "delta": 5.6,
      "unit": " €"
    },
    {
      "id": "margin",
      "label": "Marge",
      "value": 18.7,
      "delta": 0.9,
      "unit": "%"
    }
  ],
  "trends": [
    { "date": "01.10", "sales": 24000, "inventory": 82000 },
    { "date": "02.10", "sales": 26000, "inventory": 81500 }
  ]
}
```

**Response (Success):**
```json
{
  "ok": true,
  "data": {
    "summary": "Der Umsatz liegt bei 483.210 €, steigend um 5.6 %. Die Marge beträgt 18.7 %...",
    "factors": [
      "Starke Nachfrage nach Milchpulversegment",
      "Steigende Logistikkosten",
      "Gute Zahlungsmoral der Kunden"
    ],
    "suggestions": [
      "Lageroptimierung: Prüfe Putaway-Zyklen für Top-Seller",
      "Preisanpassung bei stabiler Nachfrage > 5 %",
      "Automatische Nachdisposition aktivieren"
    ]
  }
}
```

**Response (Error):**
```json
{
  "ok": false,
  "error": "Validation error: ..."
}
```

### GET /mcp/copilot/health

Health-Check Endpoint.

**Response:**
```json
{
  "ok": true,
  "service": "analytics-copilot",
  "timestamp": 1699876543210
}
```

### WebSocket: ws://localhost:7070/mcp/copilot/ws

Empfängt Realtime-Updates wenn neue Insights generiert werden.

**Event Format:**
```json
{
  "service": "analytics",
  "type": "updated",
  "payload": {
    "summary": "...",
    "factors": [...],
    "suggestions": [...]
  },
  "timestamp": 1699876543210
}
```

## Frontend-Integration

### 1. Hook aktualisieren (`useCopilotInsight.ts`)

```typescript
import { useEffect, useState } from "react"
import { useMcpQuery } from "@/lib/mcp"

export function useCopilotInsight() {
  const { data: kpiData } = useMcpQuery("analytics", "kpis", [])
  const { data: trendData } = useMcpQuery("analytics", "trends", [])
  const [insight, setInsight] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!kpiData || !trendData) return
    
    setLoading(true)
    
    // Echter API-Call statt Simulation
    fetch("/api/mcp/copilot/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        kpis: kpiData.data,
        trends: trendData.data,
      }),
    })
      .then((res) => res.json())
      .then((json) => {
        if (json.ok) {
          setInsight(json.data)
        }
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })
  }, [kpiData, trendData])

  return { insight, loading }
}
```

### 2. WebSocket-Integration

```typescript
// In useMcpRealtime.ts oder separater Hook
useEffect(() => {
  const ws = new WebSocket("ws://localhost:7070/mcp/copilot/ws")
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.service === "analytics" && data.type === "updated") {
      // Query invalidieren für automatisches Neuladen
      queryClient.invalidateQueries(["analytics", "insights"])
    }
  }
  
  return () => ws.close()
}, [])
```

## TypeScript Types

### Service Types

```typescript
import type { Insight } from "./analytics-copilot-service"

// KPI Input
type KPI = {
  id: string
  label: string
  value: number
  delta: number
  unit?: string
}

// Trend Input
type TrendPoint = {
  date: string
  sales: number
  inventory: number
}

// Insight Output
type Insight = {
  summary: string
  factors: string[]
  suggestions: string[]
}
```

## Testing

### Unit Tests

```typescript
import { describe, it, expect, vi } from "vitest"
import { createCopilotService } from "./analytics-copilot-service"

describe("Analytics Copilot Service", () => {
  it("should create service with app and wss", () => {
    const { app, wss } = createCopilotService()
    expect(app).toBeDefined()
    expect(wss).toBeDefined()
  })
  
  it("should validate input schema", async () => {
    const { app } = createCopilotService()
    const response = await request(app)
      .post("/analyze")
      .send({ invalid: "data" })
    
    expect(response.status).toBe(400)
    expect(response.body.ok).toBe(false)
  })
})
```

### Integration Tests

```bash
# Terminal 1: Start Service
cd packages/analytics-domain
npm run dev

# Terminal 2: Test Request
curl -X POST http://localhost:7070/mcp/copilot/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "kpis": [{"id":"rev","label":"Umsatz","value":100000,"delta":5.0}],
    "trends": [{"date":"01.10","sales":10000,"inventory":50000}]
  }'
```

## Monitoring & Logging

### Empfohlene Logging-Integration

```typescript
import winston from "winston"

const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: "copilot-error.log", level: "error" }),
    new winston.transports.File({ filename: "copilot-combined.log" }),
  ],
})

// In callLLM():
logger.info("LLM API call", { model: llmModel, promptLength: prompt.length })
logger.error("LLM API error", { error: errorMessage })
```

### Metrics (Optional)

```typescript
import { Counter, Histogram } from "prom-client"

const llmCallCounter = new Counter({
  name: "copilot_llm_calls_total",
  help: "Total number of LLM API calls",
})

const llmLatency = new Histogram({
  name: "copilot_llm_latency_seconds",
  help: "LLM API call latency",
})
```

## Security

### API-Key Sicherheit

- ✅ Niemals API-Keys in Code committen
- ✅ Verwende `.env` Dateien (in `.gitignore`)
- ✅ In Production: Verwende Secret-Management (AWS Secrets Manager, Azure Key Vault)

### Rate-Limiting (Empfohlen)

```typescript
import rateLimit from "express-rate-limit"

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 Minuten
  max: 100, // Max 100 Requests pro IP
})

app.use("/analyze", limiter)
```

## Troubleshooting

### Problem: "LLM API returned status 401"
**Lösung:** API-Key prüfen in `.env`

### Problem: "Cannot find module 'node-fetch'"
**Lösung:** `npm install node-fetch@3`

### Problem: WebSocket verbindet nicht
**Lösung:** Prüfe ob `server.on("upgrade")` korrekt konfiguriert ist

### Problem: JSON-Parsing schlägt fehl
**Lösung:** LLM-Antwort prüfen, evtl. `response_format` anpassen

## Code-Qualität

### ✅ Memory-Bank Compliance

- TypeScript Strict Mode
- Explizite Return Types
- Keine Magic Numbers (alle als Konstanten)
- Kein `any` Typ
- Zod-Validation für alle Inputs
- Error-Handling mit try-catch
- WebSocket-State-Checks

### ✅ Production-Ready Features

- Health-Check Endpoint
- Error-Handler Middleware
- Zod-Schema Validation
- Graceful Error-Fallbacks
- WebSocket Broadcast
- Environment-Variable Configuration

## Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
ENV PORT=7070
EXPOSE 7070
CMD ["node", "dist/services/copilot-standalone.js"]
```

### Environment Variables (Production)

```bash
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=${SECRET_LLM_API_KEY}
LLM_MODEL=gpt-4o
PORT=7070
NODE_ENV=production
```

## Zusammenfassung

**Phase F - Backend MCP-Copilot-Service** stellt bereit:

- ✅ LLM-agnostischer Backend-Service
- ✅ GPT/OpenAI/Ollama/Claude kompatibel
- ✅ WebSocket-Support für Realtime-Updates
- ✅ Vollständige TypeScript-Typisierung
- ✅ Zod-Schema-Validation
- ✅ Production-ready Error-Handling
- ✅ Health-Check & Monitoring-Ready
- ✅ Memory-Bank konform

**Status:** Production Ready 🚀
