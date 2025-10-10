# ✅ Policy Manager - Vollständige Implementation

## 🎉 Phase L abgeschlossen!

Das vollständige Policy-Framework ist implementiert - Frontend + Backend + SQLite-Persistenz!

---

## 📦 Was wurde gebaut

### **Frontend** (`packages/frontend-web/`)

#### 1. **Zod-Schemas** (`src/policy/schema.ts`)
- `RuleSchema` für Policy-Validierung
- `AlertInputSchema` für Simulator
- Strikte TypeScript-Typen

#### 2. **Policy-Manager Page** (`src/pages/policy-manager.tsx`)
- ✅ Rules-Liste mit Metadaten-Anzeige
- ✅ Löschen mit Confirm-Dialog
- ✅ Import-Dialog mit Zod-Validierung
- ✅ Export als JSON-Download
- ✅ Test-Simulator mit Live-Preview
- ✅ Strict TypeScript (keine `any`)

#### 3. **Routing & Navigation**
- Route `/policies` in `main.tsx`
- Navigation-Link in `DashboardLayout.tsx`

---

### **Backend** (`src/services/policy/`)

#### 1. **SQLite-Store** (`store-sqlite.ts`)
- CRUD-Operationen (list, upsert, delete, get)
- Bulk-Upsert (transaktional)
- Backup: `exportToJson()`
- Restore: `restoreFromJson()`
- WAL-Mode für bessere Performance

#### 2. **Policy-Engine** (`engine.ts`)
- `decide()` - Matched Alerts gegen Regeln
- `withinWindow()` - Zeitfenster-Prüfung
- `resolveParams()` - Severity-abhängige Parameter
- Approval-Workflow-Logik

#### 3. **Express-Routes** (`routes.ts`)
- `GET /api/mcp/policy/list`
- `POST /api/mcp/policy/upsert` (einzeln & bulk)
- `POST /api/mcp/policy/create` (alias)
- `POST /api/mcp/policy/update`
- `POST /api/mcp/policy/delete`
- `POST /api/mcp/policy/test` (Simulator)
- `GET /api/mcp/policy/export`
- `POST /api/mcp/policy/restore`

#### 4. **MCP-Server** (`src/mcp-server.ts`)
- Standalone Express-Server
- CORS-Support
- Health-Check (`/healthz`)
- Graceful Shutdown

#### 5. **Seed-Script** (`scripts/seed-policies.ts`)
- Befüllt DB mit 3 Standard-Policies
- `pricing.auto.adjust`
- `inventory.auto.reorder`
- `sales.notify.drop`

---

## 🚀 Quickstart

### 1. Datenbank initialisieren
```bash
pnpm run policy:seed
```

**Output:**
```
✅ Seeded 3 policies to data/policies.db
```

### 2. Backend starten
```bash
pnpm run mcp:dev
```

**Server läuft auf:** `http://localhost:7070`

### 3. Frontend öffnen
Navigiere zu: **`http://localhost:5173/policies`**

---

## 📍 API-Endpoints

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/mcp/policy/list` | Alle Policies auflisten |
| POST | `/api/mcp/policy/upsert` | Policy erstellen/aktualisieren |
| POST | `/api/mcp/policy/delete` | Policy löschen |
| POST | `/api/mcp/policy/test` | Simulator (Alert → Decision) |
| GET | `/api/mcp/policy/export` | JSON-Export (Download) |
| POST | `/api/mcp/policy/restore` | JSON-Import (ersetzt alle!) |
| GET | `/healthz` | Health-Check |

---

## 🧪 Testen

### Health-Check
```bash
curl http://localhost:7070/healthz
```

**Response:**
```json
{
  "ok": true,
  "service": "policy-mcp-server"
}
```

### Policies auflisten
```bash
curl http://localhost:7070/api/mcp/policy/list
```

### Test-Simulator
```bash
curl -X POST http://localhost:7070/api/mcp/policy/test \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "id": "test-1",
      "kpiId": "margin",
      "title": "Marge niedrig",
      "message": "Marge 14%",
      "severity": "warn",
      "delta": -2
    },
    "roles": ["manager"]
  }'
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

---

## 📂 Dateistruktur

```
VALEO-NeuroERP-3.0/
├── data/
│   └── policies.db               # SQLite-Datenbank
├── packages/frontend-web/
│   ├── src/
│   │   ├── policy/
│   │   │   ├── schema.ts         # Zod-Schemas
│   │   │   ├── engine.ts         # (Frontend-Engine, bereits aus Phase K)
│   │   │   ├── audit.ts          # (bereits aus Phase K)
│   │   │   └── PolicyBadge.tsx   # (bereits aus Phase K)
│   │   ├── pages/
│   │   │   └── policy-manager.tsx # Admin-UI
│   │   └── main.tsx              # ← Route ergänzt
│   └── docs/
│       └── policy-manager-backend-integration.md
├── src/
│   ├── services/policy/
│   │   ├── store-sqlite.ts       # SQLite-Store
│   │   ├── engine.ts             # Policy-Engine (Backend)
│   │   ├── routes.ts             # Express-Router
│   │   └── README.md             # Backend-Doku
│   └── mcp-server.ts             # Standalone-Server
├── scripts/
│   └── seed-policies.ts          # Seed-Script
└── package.json                  # ← Scripts ergänzt
```

---

## 🔧 npm-Scripts

| Script | Befehl | Beschreibung |
|--------|--------|--------------|
| `mcp:dev` | `ts-node src/mcp-server.ts` | Startet MCP-Server |
| `policy:seed` | `ts-node scripts/seed-policies.ts` | Seed-Datenbank |

---

## 🎯 Features

### Frontend
- ✅ **Policy-Liste** mit Löschen
- ✅ **JSON-Import** mit Zod-Validierung
- ✅ **JSON-Export** als Download
- ✅ **Test-Simulator** mit Live-Decision-Preview
- ✅ **Strict TypeScript** (keine Magic Numbers, sortierte Imports)

### Backend
- ✅ **SQLite-Persistenz** (WAL-Mode)
- ✅ **CRUD-Operations**
- ✅ **Bulk-Import** (transaktional)
- ✅ **Backup/Restore** via API
- ✅ **Test-Simulator** (serverseitige Engine)
- ✅ **Zod-Validierung** auf allen Endpoints

---

## ⚠️ Sicherheit

**Aktuell:** Der Server erlaubt alle Origins (`*`) und hat keine Auth.

**Für Production:**

1. **CORS einschränken:**
   ```typescript
   // In src/mcp-server.ts
   res.header("Access-Control-Allow-Origin", "https://your-domain.com")
   ```

2. **JWT/Session-Auth hinzufügen:**
   ```typescript
   import { authMiddleware } from './middleware/auth'
   app.use('/api/mcp/policy', authMiddleware, createPolicyRouter(...))
   ```

3. **RBAC prüfen:**
   ```typescript
   // Nur admin/manager dürfen Policies ändern
   if (!req.user.roles.includes('admin')) {
     return res.status(403).json({ ok: false, error: 'Forbidden' })
   }
   ```

4. **Audit-Logging:**
   ```typescript
   // Jede Policy-Änderung loggen
   await audit({
     ts: new Date().toISOString(),
     user: req.user.id,
     action: 'policy.delete',
     params: { id }
   })
   ```

---

## 🔄 Integration in bestehenden Server

Falls du bereits einen MCP-Server hast (z. B. `main.py` oder `index.ts`):

```typescript
import { PolicyStore } from './services/policy/store-sqlite'
import { createPolicyRouter } from './services/policy/routes'

// In deinem Express-App:
const policyStore = new PolicyStore('data/policies.db')
app.use('/api/mcp/policy', createPolicyRouter(policyStore))
```

---

## 💾 Backup & Restore

### Manuelles Backup (SQLite-Datei)
```bash
cp data/policies.db data/policies-backup-$(date +%Y%m%d).db
```

### Export via API
```bash
curl http://localhost:7070/api/mcp/policy/export > policies-backup.json
```

### Restore via API
```bash
curl -X POST http://localhost:7070/api/mcp/policy/restore \
  -H "Content-Type: application/json" \
  -d "{\"json\": \"$(cat policies-backup.json)\"}"
```

---

## 📊 Standard-Policies

Nach `pnpm run policy:seed` sind folgende Regeln aktiv:

### 1. `pricing.auto.adjust`
- **Trigger:** Marge warn/crit
- **Action:** Preis anpassen (+1% warn, +3% crit)
- **Limits:** Max +3%/Tag, +7%/Woche
- **Zeitfenster:** Mo-Fr, 08:00-18:00
- **Approval:** ✅ (Manager/Admin), Bypass bei crit

### 2. `inventory.auto.reorder`
- **Trigger:** Stock warn/crit
- **Action:** Nachbestellen (250/500 Einheiten)
- **Limits:** Max 2000/Tag
- **Zeitfenster:** Mo-Sa, 07:00-20:00
- **Auto-Execute:** ✅

### 3. `sales.notify.drop`
- **Trigger:** Revenue warn/crit
- **Action:** Vertrieb benachrichtigen
- **Zeitfenster:** 24/7
- **Auto-Execute:** ✅

---

## 🐛 Troubleshooting

### Port 7070 bereits belegt
```bash
PORT=8080 pnpm run mcp:dev
```

### Datenbank korrupt
```bash
rm data/policies.db
pnpm run policy:seed
```

### Frontend kann Backend nicht erreichen
1. Prüfe ob Server läuft: `curl http://localhost:7070/healthz`
2. Prüfe CORS-Header in Browser DevTools
3. Ändere Frontend-`useMcpQuery` Base-URL falls nötig

---

## ✅ DoD-Check

- ✅ SQLite-Store mit CRUD
- ✅ Policy-Engine (serverseitig)
- ✅ Express-Routes (8 Endpoints)
- ✅ Seed-Script
- ✅ Standalone MCP-Server
- ✅ Frontend Policy-Manager Page
- ✅ Import/Export (JSON)
- ✅ Test-Simulator (Frontend & Backend)
- ✅ Backup/Restore-Funktionen
- ✅ Strict TypeScript (Frontend & Backend)
- ✅ Dokumentation (README, API-Docs)

---

## 🚧 Nächste Schritte (Optional)

1. **Auth/RBAC** – JWT-Middleware für Policy-Endpoints
2. **Audit-Log-Backend** – Persistenz für `/api/mcp/audit/log`
3. **Realtime-Updates** – WebSocket-Events bei Policy-Änderungen
4. **Policy-Versioning** – Historie von Policy-Änderungen
5. **Advanced UI** – Inline-Editor für Policies (statt nur JSON-Import)
6. **Tests** – Unit-Tests für Engine + Integration-Tests für Routes

---

## 📚 Weitere Dokumentation

- **Backend:** `src/services/policy/README.md`
- **Frontend-Integration:** `packages/frontend-web/docs/policy-manager-backend-integration.md`
- **Phase K (Policy-Framework):** siehe vorherige Phase

---

**🎉 Alles fertig! Der Policy-Manager ist produktionsbereit (nach Auth/RBAC-Ergänzung).**

**Möchtest du jetzt die Realtime-WebSocket-Integration für Policy-Updates bauen? 😊**

