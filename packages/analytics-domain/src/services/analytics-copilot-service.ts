/**
 * VALEO NeuroERP – MCP Analytics Copilot Service
 * Erzeugt KI-Analysen auf Basis der KPIs & Trends.
 * Typisiert, erweiterbar, mit WebSocket-Broadcast für Echtzeit-Frontends.
 */

import type { Request, Response, NextFunction } from "express"
import express from "express"
import fetch from "node-fetch"
import { WebSocketServer, type WebSocket } from "ws"
import { z } from "zod"

const HTTP_STATUS_BAD_REQUEST = 400
const HTTP_STATUS_INTERNAL_ERROR = 500
const WEBSOCKET_READY_STATE_OPEN = 1

// 🔹 Eingabemodell
const KPISchema = z.object({
  id: z.string(),
  label: z.string(),
  value: z.number(),
  delta: z.number(),
  unit: z.string().optional(),
})

const TrendSchema = z.object({
  date: z.string(),
  sales: z.number(),
  inventory: z.number(),
})

const InputSchema = z.object({
  kpis: z.array(KPISchema),
  trends: z.array(TrendSchema),
})

// 🔹 Ausgabemodell
const InsightSchema = z.object({
  summary: z.string(),
  factors: z.array(z.string()),
  suggestions: z.array(z.string()),
})

export type Insight = z.infer<typeof InsightSchema>
type InputData = z.infer<typeof InputSchema>

// 🔹 WebSocket Event
type CopilotEvent = {
  service: string
  type: string
  payload: Insight
  timestamp: number
}

/**
 * Erstellt den Copilot-Service mit Express-App und WebSocket-Server
 */
export function createCopilotService(): {
  app: express.Application
  wss: WebSocketServer
} {
  const app = express()
  app.use(express.json())

  // Optional: WebSocket für Echtzeit-Events
  const wss = new WebSocketServer({ noServer: true })

  /**
   * Broadcast-Funktion für WebSocket-Clients
   */
  function broadcast(event: CopilotEvent): void {
    const msg = JSON.stringify(event)
    wss.clients.forEach((client: WebSocket): void => {
      if (client.readyState === WEBSOCKET_READY_STATE_OPEN) {
        client.send(msg)
      }
    })
  }

  /**
   * Ruft die LLM-API auf und parst die Antwort
   */
  async function callLLM(prompt: string): Promise<Insight> {
    const llmApiUrl =
      process.env.LLM_API_URL ?? "https://api.openai.com/v1/chat/completions"
    const llmApiKey = process.env.LLM_API_KEY ?? ""
    const llmModel = process.env.LLM_MODEL ?? "gpt-4o-mini"

    try {
      const resp = await fetch(llmApiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${llmApiKey}`,
        },
        body: JSON.stringify({
          model: llmModel,
          messages: [
            {
              role: "system",
              content:
                "Du bist ein betriebswirtschaftlicher Assistent für Agrarhandel.",
            },
            { role: "user", content: prompt },
          ],
          response_format: { type: "json_object" },
        }),
      })

      if (!resp.ok) {
        throw new Error(`LLM API returned status ${resp.status}`)
      }

      const json = (await resp.json()) as {
        choices?: Array<{ message?: { content?: string } }>
      }
      const content = json.choices?.[0]?.message?.content ?? "{}"
      const parsedContent = JSON.parse(content) as unknown

      const parsedInsight = InsightSchema.safeParse(parsedContent)
      if (parsedInsight.success) {
        return parsedInsight.data
      }

      return {
        summary: "LLM-Antwort konnte nicht geparst werden.",
        factors: ["Unklare Eingabe"],
        suggestions: ["Bitte Eingabedaten prüfen"],
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err)
      return {
        summary: "Fehler bei der LLM-Analyse",
        factors: [errorMessage],
        suggestions: ["Bitte API-Konfiguration prüfen"],
      }
    }
  }

  /**
   * Berechnet Durchschnittswerte aus Trends
   */
  function calculateAverageStock(trends: InputData["trends"]): number {
    if (trends.length === 0) {
      return 0
    }
    const total = trends.reduce((acc, trend) => acc + trend.inventory, 0)
    return total / trends.length
  }

  /**
   * Erstellt den Prompt für die LLM-Analyse
   */
  function buildPrompt(data: InputData): string {
    const revenueKpi = data.kpis.find((k) => k.id === "rev")
    const marginKpi = data.kpis.find((k) => k.id === "margin")

    const revenue = revenueKpi?.value ?? 0
    const delta = revenueKpi?.delta ?? 0
    const margin = marginKpi?.value ?? 0
    const avgStock = calculateAverageStock(data.trends)

    return `
Analysiere folgende Unternehmenskennzahlen im Kontext eines Agrar-ERP-Systems.
Erstelle eine kurze Zusammenfassung, 3 Einflussfaktoren und 3 Empfehlungen.

Daten:
- Umsatz: ${revenue} €, Änderung ${delta} %
- Marge: ${margin} %
- Durchschnittlicher Lagerbestand: ${avgStock}

Antworte im JSON-Format:
{
  "summary": "Kurze Zusammenfassung der Situation",
  "factors": ["Faktor 1", "Faktor 2", "Faktor 3"],
  "suggestions": ["Empfehlung 1", "Empfehlung 2", "Empfehlung 3"]
}
    `.trim()
  }

  // 🔸 Analyse-Endpoint
  app.post(
    "/analyze",
    async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        const parsed = InputSchema.safeParse(req.body)
        if (!parsed.success) {
          res.status(HTTP_STATUS_BAD_REQUEST).json({
            ok: false,
            error: parsed.error.message,
          })
          return
        }

        const data = parsed.data
        const prompt = buildPrompt(data)
        const insight = await callLLM(prompt)

        // Broadcast an WebSocket-Clients
        const event: CopilotEvent = {
          service: "analytics",
          type: "updated",
          payload: insight,
          timestamp: Date.now(),
        }
        broadcast(event)

        res.json({ ok: true, data: insight })
      } catch (err) {
        next(err)
      }
    }
  )

  // 🔸 Health-Check Endpoint
  app.get("/health", (_req: Request, res: Response): void => {
    res.json({
      ok: true,
      service: "analytics-copilot",
      timestamp: Date.now(),
    })
  })

  // 🔸 Forecast & Anomaly Detection Endpoint
  app.post(
    "/forecast",
    async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        const { trends } = req.body as {
          trends?: Array<{ date: string; sales: number; inventory: number }>
        }

        if (!Array.isArray(trends) || trends.length < 3) {
          res.status(HTTP_STATUS_BAD_REQUEST).json({
            ok: false,
            error: "Zu wenige Trenddaten (mindestens 3 benötigt)",
          })
          return
        }

        // Einfache Regressions-Vorhersage
        const lastTrend = trends[trends.length - 1]
        if (lastTrend === undefined) {
          res.status(HTTP_STATUS_BAD_REQUEST).json({
            ok: false,
            error: "Keine Trenddaten verfügbar",
          })
          return
        }

        // Berechne durchschnittliche Änderung der letzten 3 Perioden
        const recentTrends = trends.slice(-3)
        let totalDelta = 0
        for (let i = 1; i < recentTrends.length; i++) {
          const current = recentTrends[i]
          const previous = recentTrends[i - 1]
          if (current !== undefined && previous !== undefined) {
            totalDelta += current.sales - previous.sales
          }
        }
        const avgDeltaSales = totalDelta / (recentTrends.length - 1)
        const nextSales = lastTrend.sales + avgDeltaSales

        // Anomalie-Erkennung: > 15% Abweichung
        const ANOMALY_THRESHOLD = 0.15
        const anomaly = Math.abs(avgDeltaSales) > ANOMALY_THRESHOLD * lastTrend.sales

        let forecastSummary = `Prognostizierter Umsatz morgen: ${nextSales.toFixed(
          0
        )} €`
        if (anomaly) {
          forecastSummary += " ⚠️ Anomalie erkannt!"
        }

        // Optional: LLM-gestützte Textanalyse
        let factors: string[] = []
        const llmApiKey = process.env.LLM_API_KEY
        if (
          typeof llmApiKey === "string" &&
          llmApiKey.length > 0 &&
          llmApiKey !== "your-api-key-here"
        ) {
          try {
            const llmApiUrl =
              process.env.LLM_API_URL ??
              "https://api.openai.com/v1/chat/completions"
            const llmModel = process.env.LLM_MODEL ?? "gpt-4o-mini"

            const recentTrendsForLLM = trends.slice(-5)
            const resp = await fetch(llmApiUrl, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${llmApiKey}`,
              },
              body: JSON.stringify({
                model: llmModel,
                messages: [
                  {
                    role: "system",
                    content:
                      "Du bist ein Wirtschaftsanalyst für Agrarhandel. Analysiere Trends und nenne 3 Hauptfaktoren.",
                  },
                  {
                    role: "user",
                    content: `Analysiere folgende Trenddaten: ${JSON.stringify(
                      recentTrendsForLLM
                    )}`,
                  },
                ],
              }),
            })

            if (resp.ok) {
              const json = (await resp.json()) as {
                choices?: Array<{ message?: { content?: string } }>
              }
              const txt = json.choices?.[0]?.message?.content ?? ""
              factors = txt
                .split(/[\n•\-]/)
                .map((f) => f.trim())
                .filter((f) => f.length > 0)
                .slice(0, 3)
            }
          } catch {
            // LLM optional - continue without
          }
        }

        const result = {
          forecast: { sales: nextSales, anomaly },
          summary: forecastSummary,
          factors,
        }

        // Broadcast an WebSocket-Clients
        const event: CopilotEvent = {
          service: "analytics",
          type: "forecast-updated",
          payload: result,
          timestamp: Date.now(),
        }
        broadcast(event)

        res.json({ ok: true, data: result })
      } catch (err) {
        next(err)
      }
    }
  )

  // 🔸 Chat-Endpoint
  app.post(
    "/chat",
    async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        const { message, history } = req.body as {
          message?: string
          history?: Array<{ role: string; content: string }>
        }

        if (typeof message !== "string" || message.length === 0) {
          res.status(HTTP_STATUS_BAD_REQUEST).json({
            ok: false,
            error: "No message provided",
          })
          return
        }

        const llmApiUrl =
          process.env.LLM_API_URL ??
          "https://api.openai.com/v1/chat/completions"
        const llmApiKey = process.env.LLM_API_KEY ?? ""
        const llmModel = process.env.LLM_MODEL ?? "gpt-4o-mini"

        const messages = [
          {
            role: "system",
            content:
              "Du bist der betriebswirtschaftliche Copilot-Advisor von VALEO NeuroERP. Beantworte Fragen zu KPIs, Lager, Preisen und Prognosen präzise und hilfreich.",
          },
          ...(history ?? []),
          { role: "user", content: message },
        ]

        const resp = await fetch(llmApiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${llmApiKey}`,
          },
          body: JSON.stringify({
            model: llmModel,
            messages,
            temperature: 0.4,
          }),
        })

        if (!resp.ok) {
          throw new Error(`LLM API returned status ${resp.status}`)
        }

        const json = (await resp.json()) as {
          choices?: Array<{ message?: { content?: string } }>
        }
        const reply =
          json.choices?.[0]?.message?.content ?? "Keine Antwort erhalten."

        res.json({ ok: true, reply })
      } catch (err) {
        next(err)
      }
    }
  )

  // 🔸 Error Handler
  app.use(
    (
      err: Error,
      _req: Request,
      res: Response,
      _next: NextFunction
    ): void => {
      res.status(HTTP_STATUS_INTERNAL_ERROR).json({
        ok: false,
        error: err.message,
      })
    }
  )

  return { app, wss }
}
