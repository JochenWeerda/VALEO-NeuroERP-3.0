***REMOVED*** Policy Manager Backend

Vollständige SQLite-basierte Backend-Implementation für das Policy-Framework.

***REMOVED******REMOVED*** Architektur

- **`store-sqlite.ts`**: SQLite-Store mit CRUD + Backup/Restore
- **`engine.ts`**: Policy-Entscheidungs-Engine (decide, resolveParams, withinWindow)
- **`routes.ts`**: Express-Router mit allen Endpoints

***REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Dependencies sind bereits installiert
pnpm install
```

***REMOVED******REMOVED*** Datenbank initialisieren

```bash
***REMOVED*** Seed mit Standard-Policies
pnpm run policy:seed
```

Dies erstellt `data/policies.db` mit 3 Standard-Regeln:
- `pricing.auto.adjust`
- `inventory.auto.reorder`
- `sales.notify.drop`

***REMOVED******REMOVED*** MCP-Server starten

```bash
***REMOVED*** Development-Server
pnpm run mcp:dev
```

Server läuft auf: **http://localhost:7070**

***REMOVED******REMOVED*** API-Endpoints

***REMOVED******REMOVED******REMOVED*** GET `/api/mcp/policy/list`
Listet alle Policies

**Response:**
```json
{
  "ok": true,
  "data": [ /* Rule[] */ ]
}
```

***REMOVED******REMOVED******REMOVED*** POST `/api/mcp/policy/upsert`
Erstellt oder aktualisiert Policies (einzeln oder bulk)

**Request (einzeln):**
```json
{
  "id": "test.rule",
  "when": { "kpiId": "margin", "severity": ["warn"] },
  "action": "pricing.adjust",
  "autoExecute": false
}
```

**Request (bulk):**
```json
{
  "rules": [
    { /* Rule */ },
    { /* Rule */ }
  ]
}
```

***REMOVED******REMOVED******REMOVED*** POST `/api/mcp/policy/delete`
Löscht eine Policy

**Request:**
```json
{
  "id": "test.rule"
}
```

***REMOVED******REMOVED******REMOVED*** POST `/api/mcp/policy/test`
Simulator - testet Policy-Entscheidung gegen Alert

**Request:**
```json
{
  "alert": {
    "id": "sim-1",
    "kpiId": "margin",
    "title": "Marge niedrig",
    "message": "14%",
    "severity": "warn",
    "delta": -2
  },
  "roles": ["manager"]
}
```

**Response:**
```json
{
  "ok": true,
  "decision": {
    "type": "allow",
    "execute": false,
    "needsApproval": true,
    "approverRoles": ["manager", "admin"],
    "ruleId": "pricing.auto.adjust",
    "resolvedParams": { "deltaPct": 1 }
  }
}
```

***REMOVED******REMOVED******REMOVED*** GET `/api/mcp/policy/export`
Exportiert alle Policies als JSON-Download

***REMOVED******REMOVED******REMOVED*** POST `/api/mcp/policy/restore`
Importiert Policies aus JSON (ACHTUNG: ersetzt alle bestehenden!)

**Request:**
```json
{
  "json": "{ \"rules\": [ ... ] }"
}
```

***REMOVED******REMOVED*** Integration in bestehenden Server

Falls du bereits einen MCP-Server hast:

```typescript
import { PolicyStore } from './services/policy/store-sqlite'
import { createPolicyRouter } from './services/policy/routes'

// In deinem Express-App:
const policyStore = new PolicyStore('data/policies.db')
app.use('/api/mcp/policy', createPolicyRouter(policyStore))
```

***REMOVED******REMOVED*** Backup & Restore

***REMOVED******REMOVED******REMOVED*** Manuelles Backup
```bash
***REMOVED*** SQLite-Datei kopieren
cp data/policies.db data/policies-backup-$(date +%Y%m%d).db
```

***REMOVED******REMOVED******REMOVED*** Export via API
```bash
curl http://localhost:7070/api/mcp/policy/export > policies-backup.json
```

***REMOVED******REMOVED******REMOVED*** Restore via API
```bash
curl -X POST http://localhost:7070/api/mcp/policy/restore \
  -H "Content-Type: application/json" \
  -d '{"json": "..."}'
```

***REMOVED******REMOVED*** Sicherheit

⚠️ **Wichtig:**

1. **Authentifizierung**: Endpoints sollten mit JWT/Session geschützt werden
2. **RBAC**: Nur `admin`/`manager` sollten Policies ändern dürfen
3. **Audit-Log**: Jede Policy-Änderung sollte geloggt werden
4. **Rate-Limiting**: Import/Delete sollten rate-limited sein

***REMOVED******REMOVED*** TypeScript Types

Alle Types sind exportiert aus `store-sqlite.ts`:

```typescript
import type { Rule, Severity, Role, Window, When, Approval } from './services/policy/store-sqlite'
```

***REMOVED******REMOVED*** Testing

```bash
***REMOVED*** Health-Check
curl http://localhost:7070/healthz

***REMOVED*** Policy auflisten
curl http://localhost:7070/api/mcp/policy/list

***REMOVED*** Test-Simulator
curl -X POST http://localhost:7070/api/mcp/policy/test \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "id": "test-1",
      "kpiId": "margin",
      "title": "Test",
      "message": "Test",
      "severity": "warn"
    },
    "roles": ["manager"]
  }'
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Port bereits belegt
```bash
***REMOVED*** Anderen Port verwenden
PORT=8080 pnpm run mcp:dev
```

***REMOVED******REMOVED******REMOVED*** Datenbank korrupt
```bash
***REMOVED*** Neu initialisieren
rm data/policies.db
pnpm run policy:seed
```

***REMOVED******REMOVED******REMOVED*** CORS-Fehler
Der Server erlaubt standardmäßig alle Origins (`*`). Für Production sollte dies eingeschränkt werden:

```typescript
// In mcp-server.ts
res.header("Access-Control-Allow-Origin", "https://your-domain.com")
```

***REMOVED******REMOVED*** Next Steps

1. ✅ Backend implementiert
2. ✅ Datenbank befüllt
3. ✅ Server startet
4. Frontend mit `http://localhost:7070` verbinden
5. Auth/RBAC hinzufügen
6. Audit-Logging aktivieren
7. Production-Deployment

