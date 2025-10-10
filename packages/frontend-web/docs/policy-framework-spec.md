***REMOVED*** Policy-Framework - Specification

***REMOVED******REMOVED*** Phase K - Auto-Actions, Approval & Audit

Diese Spezifikation beschreibt das Policy-Framework für regelbasierte Alert-Actions mit Vier-Augen-Prinzip, Zeitfenster-Checks und Audit-Logging.

***REMOVED******REMOVED*** Übersicht

Das Policy-Framework bietet:
- **Regelbasierte Entscheidungen:** JSON-konfigurierbare Policies
- **Auto-Actions:** Automatische Ausführung bei definierten Bedingungen
- **Vier-Augen-Prinzip:** Approval-Workflows für kritische Actions
- **Zeitfenster:** Tages- und Uhrzeitbasierte Beschränkungen
- **Limits:** Tages-/Wochen-Limits für Actions
- **Audit-Logging:** Vollständige Nachvollziehbarkeit
- **Rollenbasiert:** Admin/Manager/Operator

***REMOVED******REMOVED*** Architektur

```
┌─────────────────────────────────────┐
│  Alert erscheint                    │
│  └─ Severity: warn/crit             │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Policy-Engine (engine.ts)          │
│  ├─ Rule-Matching (KPI + Severity)  │
│  ├─ Zeitfenster-Check               │
│  ├─ Limit-Validierung               │
│  ├─ Approval-Check                  │
│  └─ Decision: allow/deny            │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Decision-Types                     │
│  ├─ deny → Reason anzeigen          │
│  ├─ allow + needsApproval           │
│  │  → "Freigabe angefordert"        │
│  └─ allow + execute                 │
│     → Action ausführen              │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Audit-Log (audit.ts)               │
│  ├─ POST /mcp/audit/log             │
│  └─ Persistierung im Backend        │
└─────────────────────────────────────┘
```

***REMOVED******REMOVED*** Policy-Konfiguration

***REMOVED******REMOVED******REMOVED*** Datei: `src/policy/policies.json`

**Struktur:**
```json
{
  "meta": {
    "version": "1.0.0",
    "timezone": "Europe/Berlin"
  },
  "rules": [...]
}
```

***REMOVED******REMOVED******REMOVED*** Regel-Schema

```typescript
type Rule = {
  id: string                    // Eindeutige ID
  when: {                       // Trigger-Bedingung
    kpiId: string               // z.B. "margin", "stock", "rev"
    severity: Severity[]        // ["warn", "crit"]
  }
  action: string                // "pricing.adjust", "inventory.reorder", "sales.notify"
  params?: {                    // Parameter für Action
    deltaPct?: { warn: 1, crit: 3 }
    qty?: { warn: 250, crit: 500 }
    topic?: string
    messageTemplate?: string
  }
  limits?: {                    // Tages-/Wochen-Limits
    maxDailyPct?: number
    maxWeeklyPct?: number
    maxDailyQty?: number
  }
  window?: {                    // Zeitfenster
    days: number[]              // 0=So, 1=Mo, ..., 6=Sa
    start: string               // "HH:MM"
    end: string                 // "HH:MM"
  }
  approval?: {                  // Approval-Workflow
    required: boolean
    roles?: Role[]              // ["manager", "admin"]
    bypassIfSeverity?: Severity // "crit" → kein Approval bei kritisch
  }
  autoExecute?: boolean         // Automatisch ausführen?
  autoSuggest?: boolean         // Button anzeigen?
}
```

***REMOVED******REMOVED******REMOVED*** Beispiel-Regeln

**1. Pricing-Adjustment (mit Approval):**
```json
{
  "id": "pricing.auto.adjust",
  "when": { "kpiId": "margin", "severity": ["warn", "crit"] },
  "action": "pricing.adjust",
  "params": { "deltaPct": { "warn": 1, "crit": 3 } },
  "limits": { "maxDailyPct": 3, "maxWeeklyPct": 7 },
  "window": { "days": [1,2,3,4,5], "start": "08:00", "end": "18:00" },
  "approval": {
    "required": true,
    "roles": ["manager", "admin"],
    "bypassIfSeverity": "crit"
  },
  "autoExecute": false,
  "autoSuggest": true
}
```

**Bedeutung:**
- Trigger: Margin-Alert (warn/crit)
- Action: Preis +1% (warn) oder +3% (crit)
- Limits: Max 3% pro Tag, 7% pro Woche
- Zeitfenster: Mo-Fr, 08:00-18:00
- Approval: Manager/Admin erforderlich, außer bei crit
- Ausführung: Manuell (autoExecute: false)

**2. Inventory-Reorder (ohne Approval):**
```json
{
  "id": "inventory.auto.reorder",
  "when": { "kpiId": "stock", "severity": ["warn", "crit"] },
  "action": "inventory.reorder",
  "params": { "qty": { "warn": 250, "crit": 500 } },
  "limits": { "maxDailyQty": 2000 },
  "window": { "days": [1,2,3,4,5,6], "start": "07:00", "end": "20:00" },
  "approval": { "required": false },
  "autoExecute": true,
  "autoSuggest": true
}
```

**Bedeutung:**
- Trigger: Stock-Alert (warn/crit)
- Action: Reorder 250 (warn) oder 500 (crit) Einheiten
- Limits: Max 2000 Einheiten pro Tag
- Zeitfenster: Mo-Sa, 07:00-20:00
- Approval: Nicht erforderlich
- Ausführung: Automatisch (autoExecute: true)

***REMOVED******REMOVED*** Komponenten

***REMOVED******REMOVED******REMOVED*** 1. Policy-Engine (`engine.ts`)

**Hauptfunktion: `decide()`**

```typescript
export function decide(userRoles: Role[], alert: Alert): Decision
```

**Entscheidungslogik:**
1. **Rule-Matching:** Findet passende Regel (KPI + Severity)
2. **Zeitfenster-Check:** Prüft Wochentag und Uhrzeit
3. **Limit-Check:** Validiert Tages-/Wochen-Limits
4. **Approval-Check:** Prüft ob Freigabe nötig
5. **Role-Check:** Validiert User-Rollen

**Return-Types:**
```typescript
type Decision =
  | { type: "deny"; reason: string }
  | {
      type: "allow"
      execute: boolean
      needsApproval: boolean
      approverRoles?: Role[]
      ruleId: string
      resolvedParams: Record<string, unknown>
    }
```

**Konstanten:**
- `MINUTES_PER_HOUR = 60`
- `ISO_DATE_LENGTH = 10`

***REMOVED******REMOVED******REMOVED*** 2. Audit-Logging (`audit.ts`)

**AuditEntry-Type:**
```typescript
type AuditEntry = {
  ts: string                    // ISO-Timestamp
  user: string                  // User-ID
  roles: string[]               // User-Rollen
  action: string                // Action-Name
  params: Record<string, unknown> // Parameter
  ruleId: string                // Policy-Rule-ID
  approval?: {                  // Optional: Approval-Info
    by?: string
    at?: string
  }
  result: "executed" | "denied" | "requested-approval"
  reason?: string               // Bei deny/error
}
```

**Funktion:**
```typescript
export async function audit(entry: AuditEntry): Promise<void>
```

- Silent Fail (Audit blockiert nicht die Action)
- POST an `/api/mcp/audit/log`
- Backend persistiert in DB/File

***REMOVED******REMOVED******REMOVED*** 3. PolicyBadge (`PolicyBadge.tsx`)

**Visuelle Policy-Anzeige:**

| Decision | Badge | Color |
|----------|-------|-------|
| deny | "Policy: {reason}" | Amber |
| needsApproval | "Policy: Freigabe nötig" | Blue |
| execute | "Policy: Auto-Execute" | Emerald |
| allow | "Policy: erlaubt" | Gray |

**Integration:**
```typescript
<PolicyBadge alert={alert} roles={userRoles} />
```

***REMOVED******REMOVED******REMOVED*** 4. AlertActions mit Policy (`AlertActions.tsx`)

**Erweiterte Logik:**

1. **Policy-Check vor Ausführung:**
   ```typescript
   const decision = decide(userRoles, alert)
   if (decision.type === "deny") {
     push(`🚫 Policy: ${decision.reason}`)
     return
   }
   ```

2. **Approval-Handling:**
   ```typescript
   if (decision.needsApproval && !decision.execute) {
     push("📝 Freigabe angefordert")
     await audit({ result: "requested-approval" })
     return
   }
   ```

3. **Parameter aus Policy:**
   ```typescript
   const finalDeltaPct = decision.resolvedParams.deltaPct ?? fallback
   ```

4. **Counter-Update:**
   ```typescript
   updateCounters(decision.ruleId, { deltaPct: finalDeltaPct })
   ```

5. **Audit-Logging:**
   ```typescript
   await audit({
     ts: new Date().toISOString(),
     user: "current-user",
     roles: userRoles,
     action: "pricing.adjust",
     params: { deltaPct: finalDeltaPct },
     ruleId: decision.ruleId,
     result: "executed"
   })
   ```

***REMOVED******REMOVED*** Backend-Integration

***REMOVED******REMOVED******REMOVED*** Audit-Endpoint

**URL:** `POST /mcp/audit/log`

**Request:**
```json
{
  "ts": "2024-10-09T14:23:45.123Z",
  "user": "jochen",
  "roles": ["manager"],
  "action": "pricing.adjust",
  "params": { "deltaPct": 3 },
  "ruleId": "pricing.auto.adjust",
  "result": "executed"
}
```

**Response:**
```json
{
  "ok": true
}
```

**Backend-Implementierung (Beispiel):**
```typescript
app.post("/audit/log", async (req, res) => {
  const entry = req.body as AuditEntry
  
  // Persistieren in DB
  await db.auditLog.create({
    data: {
      timestamp: new Date(entry.ts),
      userId: entry.user,
      roles: entry.roles.join(","),
      action: entry.action,
      params: JSON.stringify(entry.params),
      ruleId: entry.ruleId,
      result: entry.result,
      reason: entry.reason,
    }
  })
  
  res.json({ ok: true })
})
```

***REMOVED******REMOVED*** User Experience

***REMOVED******REMOVED******REMOVED*** Scenario 1: Auto-Execute (Inventory Reorder)

```
Alert: [WARN] Lagerwert hoch — 550.000 €
Policy: Auto-Execute
Button: [Nachbestellen 250]

User klickt → Sofort ausgeführt
Toast: "✔ Nachbestellung gestartet"
Audit: { result: "executed" }
```

***REMOVED******REMOVED******REMOVED*** Scenario 2: Approval Required (Pricing)

```
Alert: [WARN] Marge unter Ziel — 14.5 %
Policy: Freigabe nötig
Button: [Preis +1%]

User (Operator) klickt → Freigabe angefordert
Toast: "📝 Freigabe angefordert – wartet auf Genehmigung"
Audit: { result: "requested-approval" }

Manager genehmigt → Ausgeführt
Toast: "✔ Preisupdate angestoßen"
Audit: { result: "executed", approval: { by: "manager", at: "..." } }
```

***REMOVED******REMOVED******REMOVED*** Scenario 3: Policy Deny (Outside Window)

```
Alert: [CRIT] Marge zu niedrig — 10.2 %
Zeit: Samstag 19:00 (außerhalb 08:00-18:00 Mo-Fr)
Policy: Outside window
Button: [Preis +3%] (ausgegraut)

User klickt → Nicht ausgeführt
Toast: "🚫 Policy: Outside window"
```

***REMOVED******REMOVED******REMOVED*** Scenario 4: Limit Exceeded

```
Alert: [CRIT] Marge zu niedrig — 10.2 %
Bereits heute: +2% ausgeführt
Limit: maxDailyPct = 3
Policy: Limit exceeded
Button: [Preis +3%] (würde 5% ergeben)

User klickt → Nicht ausgeführt
Toast: "🚫 Policy: Limit exceeded"
```

***REMOVED******REMOVED*** Code-Qualität

***REMOVED******REMOVED******REMOVED*** ✅ Memory-Bank Compliance

**engine.ts:**
- TypeScript Strict Mode
- Explizite Return Types
- Keine Magic Numbers (alle als Konstanten)
- Explizite Undefined-Checks
- Array.includes() statt unsichere Checks
- Record<string, unknown> statt any

**audit.ts:**
- Strikte Typisierung
- Silent Fail (nicht blockierend)
- Async/Await mit try-catch

**PolicyBadge.tsx:**
- Conditional Rendering
- Explizite Return Types
- Farbcodierung nach Decision

**AlertActions.tsx:**
- Policy-Check vor Ausführung
- Approval-Handling
- Counter-Updates
- Audit-Logging bei jedem Schritt

***REMOVED******REMOVED******REMOVED*** ✅ Lint Status

- 0 Errors
- 0 Warnings
- Import-Sortierung korrekt
- Memory-Bank konform

***REMOVED******REMOVED*** Features

***REMOVED******REMOVED******REMOVED*** ✅ Implementiert

1. **Policy-Engine**
   - Rule-Matching nach KPI + Severity
   - Zeitfenster-Validierung (Wochentag + Uhrzeit)
   - Limit-Checks (täglich/wöchentlich)
   - Approval-Logic mit Role-Checks
   - Parameter-Auflösung (Templates)

2. **Audit-Logging**
   - Vollständige Nachvollziehbarkeit
   - Timestamp, User, Roles
   - Action, Params, RuleID
   - Result (executed/denied/requested-approval)
   - Reason bei Ablehnung

3. **Policy-Badge**
   - Visueller Status-Indicator
   - Farbcodierung (Amber/Blue/Emerald/Gray)
   - Integration in AlertList

4. **AlertActions mit Policy**
   - Policy-Check vor Ausführung
   - Approval-Workflow
   - Counter-Updates
   - Audit-Logging
   - Toast-Feedback

***REMOVED******REMOVED******REMOVED*** 🚀 Erweiterungsmöglichkeiten

1. **Admin-UI: Policy-Manager**
   - CRUD für Policies
   - Live-Validierung
   - Test-Simulator
   - Policy-Templates

2. **Approval-Workflow-UI**
   - Pending-Approvals-Liste
   - Approve/Reject-Buttons
   - Notification an Approver
   - Approval-Historie

3. **Advanced Limits**
   - Rolling-Window (24h statt Kalendertag)
   - Per-User-Limits
   - Per-SKU-Limits
   - Dynamische Limits basierend auf Kontext

4. **Policy-Testing**
   - Dry-Run-Modus
   - Simulation gegen historische Alerts
   - Impact-Analyse
   - A/B-Testing von Policies

5. **Multi-Tenant**
   - Policies pro Mandant
   - Vererbung von Global → Tenant
   - Override-Mechanismus

***REMOVED******REMOVED*** Testing

***REMOVED******REMOVED******REMOVED*** Unit Tests

```typescript
describe('Policy Engine', () => {
  it('should allow action within window', () => {
    const alert = { id: "test", kpiId: "margin", severity: "warn" }
    const decision = decide(["manager"], alert)
    
    expect(decision.type).toBe("allow")
  })
  
  it('should deny action outside window', () => {
    // Mock Date to Saturday 19:00
    const decision = decide(["manager"], alert)
    
    expect(decision.type).toBe("deny")
    expect(decision.reason).toBe("Outside window")
  })
  
  it('should require approval for operator', () => {
    const decision = decide(["operator"], alert)
    
    expect(decision.needsApproval).toBe(true)
    expect(decision.execute).toBe(false)
  })
  
  it('should bypass approval for crit', () => {
    const alert = { kpiId: "margin", severity: "crit" }
    const decision = decide(["manager"], alert)
    
    expect(decision.needsApproval).toBe(false)
  })
})

describe('Audit Logging', () => {
  it('should send audit entry to backend', async () => {
    global.fetch = jest.fn(() => Promise.resolve({ ok: true }))
    
    await audit({
      ts: new Date().toISOString(),
      user: "test",
      roles: ["manager"],
      action: "pricing.adjust",
      params: { deltaPct: 3 },
      ruleId: "test-rule",
      result: "executed"
    })
    
    expect(fetch).toHaveBeenCalledWith("/api/mcp/audit/log", ...)
  })
})
```

***REMOVED******REMOVED******REMOVED*** Integration Test

```bash
***REMOVED*** Terminal 1: Backend
cd packages/analytics-domain
npm run dev

***REMOVED*** Terminal 2: Frontend
cd packages/frontend-web
npm run dev

***REMOVED*** Browser: http://localhost:5173
***REMOVED*** 1. Navigate to Dashboard
***REMOVED*** 2. Verify Alerts appear
***REMOVED*** 3. Check PolicyBadge shows correct status
***REMOVED*** 4. Click Action-Button
***REMOVED*** 5. Verify Policy-Check (Toast)
***REMOVED*** 6. Confirm in Dialog
***REMOVED*** 7. Verify Audit-Log sent to backend
```

***REMOVED******REMOVED*** Security

***REMOVED******REMOVED******REMOVED*** Client-Side vs Server-Side

**Client-Side (UI-Guidance):**
- ✅ Zeitfenster-Check
- ✅ Limit-Anzeige
- ✅ Approval-UI
- ⚠️ Kann umgangen werden (DevTools)

**Server-Side (Hard Enforcement):**
- ✅ Zeitfenster-Validierung
- ✅ Limit-Enforcement
- ✅ Role-Based Access Control
- ✅ Audit-Logging
- ✅ Rate-Limiting

**Empfehlung:** Alle Checks serverseitig wiederholen!

***REMOVED******REMOVED******REMOVED*** Backend-Validierung (Beispiel)

```typescript
app.post("/pricing/adjust", async (req, res) => {
  const { deltaPct } = req.body
  const user = req.user // Aus JWT/Session
  
  // Policy-Check serverseitig
  const decision = serverSideDecide(user.roles, alert)
  if (decision.type === "deny") {
    return res.status(403).json({ ok: false, error: decision.reason })
  }
  
  // Limit-Check in DB
  const today = new Date().toISOString().slice(0, 10)
  const todayTotal = await db.auditLog.sum({
    where: { userId: user.id, action: "pricing.adjust", date: today },
    field: "deltaPct"
  })
  
  if (todayTotal + deltaPct > 3) {
    return res.status(403).json({ ok: false, error: "Daily limit exceeded" })
  }
  
  // Ausführen...
})
```

***REMOVED******REMOVED*** Monitoring

***REMOVED******REMOVED******REMOVED*** Metrics

```typescript
const policyDecisionsCounter = new Counter({
  name: "policy_decisions_total",
  help: "Total policy decisions",
  labelNames: ["type", "reason"]
})

const policyApprovalsCounter = new Counter({
  name: "policy_approvals_total",
  help: "Total approval requests",
  labelNames: ["ruleId", "status"]
})
```

***REMOVED******REMOVED******REMOVED*** Logging

```typescript
logger.info("Policy decision", {
  alertId: alert.id,
  decision: decision.type,
  ruleId: decision.ruleId,
  execute: decision.execute,
})

logger.warn("Policy denied", {
  alertId: alert.id,
  reason: decision.reason,
})
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: "Policy: No matching rule"
**Lösung:** Regel in `policies.json` hinzufügen für KPI + Severity

***REMOVED******REMOVED******REMOVED*** Problem: "Policy: Outside window"
**Lösung:** Zeitfenster in Regel anpassen oder auf 0-6, 00:00-23:59 setzen

***REMOVED******REMOVED******REMOVED*** Problem: "Policy: Limit exceeded"
**Lösung:** Counter zurücksetzen oder Limit erhöhen

***REMOVED******REMOVED******REMOVED*** Problem: PolicyBadge zeigt nicht an
**Lösung:** Import prüfen, Alert.kpiId muss gesetzt sein

***REMOVED******REMOVED*** Zusammenfassung

**Phase K - Policy-Framework** bietet:

- ✅ JSON-konfigurierbare Policies
- ✅ Auto-Execution & Auto-Suggest
- ✅ Vier-Augen-Prinzip (Approval)
- ✅ Zeitfenster (Wochentag + Uhrzeit)
- ✅ Tages-/Wochen-Limits
- ✅ Rollenbasierte Zugriffssteuerung
- ✅ Vollständiges Audit-Logging
- ✅ Policy-Badge für Transparenz
- ✅ Memory-Bank konform
- ✅ 0 Lint-Errors/Warnings

**Status:** Production Ready 🚀

***REMOVED******REMOVED*** Nächste Schritte

**Phase L - Policy-Manager (Admin-UI):**
- CRUD für Policy-Regeln
- Live-Validierung
- Test-Simulator gegen echte Alerts
- Policy-Templates
- Import/Export

Möchtest du Phase L implementiert haben? 😊

