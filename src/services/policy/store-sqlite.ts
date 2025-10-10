import Database = require("better-sqlite3")

export type Severity = "ok" | "warn" | "crit"
export type Role = "admin" | "manager" | "operator"
export type Window = { days: number[]; start: string; end: string }
export type When = { kpiId: string; severity: Severity[] }
export type Approval = {
  required: boolean
  roles?: Role[]
  bypassIfSeverity?: Severity
}
export type Rule = {
  id: string
  when: When
  action: "pricing.adjust" | "inventory.reorder" | "sales.notify"
  params?: Record<string, unknown>
  limits?: Record<string, number>
  window?: Window
  approval?: Approval
  autoExecute?: boolean
  autoSuggest?: boolean
}

type DBRow = {
  id: string
  when_kpiId: string
  when_severity: string
  action: string
  params: string | null
  limits: string | null
  window: string | null
  approval: string | null
  autoExecute: number
  autoSuggest: number
}

/**
 * PolicyStore - SQLite-basierte Persistenz für Policy-Regeln
 */
export class PolicyStore {
  private db: Database.Database

  constructor(filename = "data/policies.db") {
    this.db = new Database(filename)
    this.db.pragma("journal_mode = WAL")
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS policies (
        id TEXT PRIMARY KEY,
        when_kpiId TEXT NOT NULL,
        when_severity TEXT NOT NULL, -- JSON string array
        action TEXT NOT NULL,
        params TEXT,    -- JSON
        limits TEXT,    -- JSON
        window TEXT,    -- JSON
        approval TEXT,  -- JSON
        autoExecute INTEGER, -- 0/1
        autoSuggest INTEGER  -- 0/1
      );
    `)
  }

  /**
   * Listet alle Policies auf
   */
  list(): Rule[] {
    const rows = this.db.prepare(`SELECT * FROM policies ORDER BY id`).all() as DBRow[]
    return rows.map((r): Rule => ({
      id: r.id,
      when: { kpiId: r.when_kpiId, severity: JSON.parse(r.when_severity) as Severity[] },
      action: r.action as Rule["action"],
      params: r.params !== null ? (JSON.parse(r.params) as Record<string, unknown>) : undefined,
      limits: r.limits !== null ? (JSON.parse(r.limits) as Record<string, number>) : undefined,
      window: r.window !== null ? (JSON.parse(r.window) as Window) : undefined,
      approval: r.approval !== null ? (JSON.parse(r.approval) as Approval) : undefined,
      autoExecute: r.autoExecute === 1,
      autoSuggest: r.autoSuggest === 1,
    }))
  }

  /**
   * Erstellt oder aktualisiert eine Policy
   */
  upsert(rule: Rule): void {
    this.db
      .prepare(
        `
      INSERT INTO policies (id, when_kpiId, when_severity, action, params, limits, window, approval, autoExecute, autoSuggest)
      VALUES (@id, @when_kpiId, @when_severity, @action, @params, @limits, @window, @approval, @autoExecute, @autoSuggest)
      ON CONFLICT(id) DO UPDATE SET
        when_kpiId=excluded.when_kpiId,
        when_severity=excluded.when_severity,
        action=excluded.action,
        params=excluded.params,
        limits=excluded.limits,
        window=excluded.window,
        approval=excluded.approval,
        autoExecute=excluded.autoExecute,
        autoSuggest=excluded.autoSuggest
    `
      )
      .run({
        id: rule.id,
        when_kpiId: rule.when.kpiId,
        when_severity: JSON.stringify(rule.when.severity),
        action: rule.action,
        params: rule.params !== undefined ? JSON.stringify(rule.params) : null,
        limits: rule.limits !== undefined ? JSON.stringify(rule.limits) : null,
        window: rule.window !== undefined ? JSON.stringify(rule.window) : null,
        approval: rule.approval !== undefined ? JSON.stringify(rule.approval) : null,
        autoExecute: rule.autoExecute === true ? 1 : 0,
        autoSuggest: rule.autoSuggest === true ? 1 : 0,
      })
  }

  /**
   * Bulk-Upsert für mehrere Policies (transaktional)
   */
  bulkUpsert(rules: Rule[]): void {
    const tx = this.db.transaction((arr: Rule[]): void => {
      for (const r of arr) {
        this.upsert(r)
      }
    })
    tx(rules)
  }

  /**
   * Löscht eine Policy
   */
  delete(id: string): void {
    this.db.prepare(`DELETE FROM policies WHERE id = ?`).run(id)
  }

  /**
   * Holt eine einzelne Policy
   */
  get(id: string): Rule | undefined {
    const r = this.db.prepare(`SELECT * FROM policies WHERE id=?`).get(id) as DBRow | undefined
    if (r === undefined) {
      return undefined
    }
    return {
      id: r.id,
      when: { kpiId: r.when_kpiId, severity: JSON.parse(r.when_severity) as Severity[] },
      action: r.action as Rule["action"],
      params: r.params !== null ? (JSON.parse(r.params) as Record<string, unknown>) : undefined,
      limits: r.limits !== null ? (JSON.parse(r.limits) as Record<string, number>) : undefined,
      window: r.window !== null ? (JSON.parse(r.window) as Window) : undefined,
      approval: r.approval !== null ? (JSON.parse(r.approval) as Approval) : undefined,
      autoExecute: r.autoExecute === 1,
      autoSuggest: r.autoSuggest === 1,
    }
  }

  /**
   * Backup: Exportiert alle Policies als JSON
   */
  exportToJson(): string {
    return JSON.stringify({ rules: this.list() }, null, 2)
  }

  /**
   * Restore: Importiert Policies aus JSON (ersetzt alle bestehenden)
   */
  restoreFromJson(json: string): void {
    const parsed = JSON.parse(json) as { rules: Rule[] }
    if (!Array.isArray(parsed.rules)) {
      throw new Error("Invalid JSON: rules[] missing")
    }

    // Transaktional: Alle löschen, dann neu einfügen
    const tx = this.db.transaction((): void => {
      this.db.prepare(`DELETE FROM policies`).run()
      for (const rule of parsed.rules) {
        this.upsert(rule)
      }
    })
    tx()
  }
}

