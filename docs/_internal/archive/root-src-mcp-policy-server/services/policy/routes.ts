import { Router, type Request, type Response } from "express"
import { z } from "zod"
import { PolicyStore, type Rule } from "./store-sqlite"
import { AlertSchema, decide } from "./engine"

const MAX_WEEKDAY = 6

/**
 * Zod-Schema für Rule-Validierung
 */
const RuleSchema: z.ZodType<Rule> = z.object({
  id: z.string().min(1),
  when: z.object({
    kpiId: z.string().min(1),
    severity: z.array(z.enum(["ok", "warn", "crit"])).nonempty(),
  }),
  action: z.enum(["pricing.adjust", "inventory.reorder", "sales.notify"]),
  params: z.record(z.unknown()).optional(),
  limits: z.record(z.number()).optional(),
  window: z
    .object({
      days: z.array(z.number().int().min(0).max(MAX_WEEKDAY)).nonempty(),
      start: z.string(),
      end: z.string(),
    })
    .optional(),
  approval: z
    .object({
      required: z.boolean(),
      roles: z.array(z.enum(["admin", "manager", "operator"])).optional(),
      bypassIfSeverity: z.enum(["ok", "warn", "crit"]).optional(),
    })
    .optional(),
  autoExecute: z.boolean().optional(),
  autoSuggest: z.boolean().optional(),
})

/**
 * Erstellt Express-Router für Policy-Endpoints
 */
export function createPolicyRouter(store: PolicyStore): Router {
  const r = Router()

  // LIST - Alle Policies auflisten
  r.get("/list", (_req: Request, res: Response): void => {
    res.json({ ok: true, data: store.list() })
  })

  // UPSERT - Erstellt oder aktualisiert Policies (einzeln oder bulk)
  r.post("/upsert", (req: Request, res: Response): void => {
    const body = req.body as { rules?: unknown } | unknown
    if (typeof body === "object" && body !== null && "rules" in body) {
      // Bulk-Import
      try {
        const rules = body.rules as unknown[]
        if (!Array.isArray(rules)) {
          res.status(400).json({ ok: false, error: "rules must be an array" })
          return
        }
        const valid = rules.map((x) => RuleSchema.parse(x))
        store.bulkUpsert(valid)
        res.json({ ok: true, count: valid.length })
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e)
        res.status(400).json({ ok: false, error: errorMessage })
      }
    } else {
      // Einzelne Rule
      try {
        const rule = RuleSchema.parse(body)
        store.upsert(rule)
        res.json({ ok: true })
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e)
        res.status(400).json({ ok: false, error: errorMessage })
      }
    }
  })

  // CREATE (Alias für upsert, für Kompatibilität)
  r.post("/create", (req: Request, res: Response): void => {
    const body = req.body as { rules?: unknown } | unknown
    if (typeof body === "object" && body !== null && "rules" in body) {
      // Bulk-Import
      try {
        const rules = body.rules as unknown[]
        if (!Array.isArray(rules)) {
          res.status(400).json({ ok: false, error: "rules must be an array" })
          return
        }
        const valid = rules.map((x) => RuleSchema.parse(x))
        store.bulkUpsert(valid)
        res.json({ ok: true, count: valid.length })
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e)
        res.status(400).json({ ok: false, error: errorMessage })
      }
    } else {
      // Einzelne Rule
      try {
        const rule = RuleSchema.parse(body)
        store.upsert(rule)
        res.json({ ok: true })
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : String(e)
        res.status(400).json({ ok: false, error: errorMessage })
      }
    }
  })

  // UPDATE - Aktualisiert eine existierende Policy
  r.post("/update", (req: Request, res: Response): void => {
    try {
      const rule = RuleSchema.parse(req.body)
      if (store.get(rule.id) === undefined) {
        res.status(404).json({ ok: false, error: "not found" })
        return
      }
      store.upsert(rule)
      res.json({ ok: true })
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e)
      res.status(400).json({ ok: false, error: errorMessage })
    }
  })

  // DELETE - Löscht eine Policy
  r.post("/delete", (req: Request, res: Response): void => {
    const body = req.body as { id?: unknown }
    const id = String(body?.id ?? "")
    if (id.length === 0) {
      res.status(400).json({ ok: false, error: "id required" })
      return
    }
    if (store.get(id) === undefined) {
      res.status(404).json({ ok: false, error: "not found" })
      return
    }
    store.delete(id)
    res.json({ ok: true })
  })

  // TEST - Simulator (testet Policy-Entscheidung)
  r.post("/test", (req: Request, res: Response): void => {
    try {
      const body = req.body as { alert?: unknown; roles?: unknown }
      const alert = AlertSchema.parse(body?.alert)
      const roles = z.array(z.string()).parse(body?.roles ?? [])
      const decision = decide(roles, alert, store.list())
      res.json({ ok: true, decision })
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e)
      res.status(400).json({ ok: false, error: errorMessage })
    }
  })

  // EXPORT - Exportiert alle Policies als JSON
  r.get("/export", (_req: Request, res: Response): void => {
    try {
      const json = store.exportToJson()
      res.setHeader("Content-Type", "application/json")
      res.setHeader("Content-Disposition", 'attachment; filename="policies-backup.json"')
      res.send(json)
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e)
      res.status(500).json({ ok: false, error: errorMessage })
    }
  })

  // RESTORE - Importiert Policies aus JSON (ersetzt alle!)
  r.post("/restore", (req: Request, res: Response): void => {
    try {
      const body = req.body as { json?: unknown }
      const json = String(body?.json ?? "")
      if (json.length === 0) {
        res.status(400).json({ ok: false, error: "json required" })
        return
      }
      store.restoreFromJson(json)
      res.json({ ok: true })
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : String(e)
      res.status(400).json({ ok: false, error: errorMessage })
    }
  })

  return r
}

