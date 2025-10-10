***REMOVED*** ✅ Policy Manager - FastAPI Integration KOMPLETT!

***REMOVED******REMOVED*** 🎉 Backend vollständig integriert!

Der Policy-Manager ist jetzt nahtlos in dein **FastAPI-Backend** integriert!

---

***REMOVED******REMOVED*** 📦 Was wurde integriert

***REMOVED******REMOVED******REMOVED*** **1. Policy Service** (`app/services/policy_service.py`)
- ✅ `PolicyStore` - SQLite-Persistenz
- ✅ `PolicyEngine` - Decision-Engine
- ✅ Pydantic-Models (Rule, Alert, Decision, etc.)
- ✅ `within_window()` - Zeitfenster-Prüfung
- ✅ `resolve_params()` - Parameter-Auflösung
- ✅ `decide()` - Policy-Matching

***REMOVED******REMOVED******REMOVED*** **2. FastAPI-Router** (`app.api.v1.endpoints.policies.py`)
- ✅ `GET /api/v1/mcp/policy/list`
- ✅ `POST /api/v1/mcp/policy/upsert`
- ✅ `POST /api/v1/mcp/policy/create`
- ✅ `POST /api/v1/mcp/policy/update`
- ✅ `POST /api/v1/mcp/policy/delete`
- ✅ `POST /api/v1/mcp/policy/test`
- ✅ `GET /api/v1/mcp/policy/export`
- ✅ `POST /api/v1/mcp/policy/restore`

***REMOVED******REMOVED******REMOVED*** **3. API-Integration**
- ✅ Router in `app/api/v1/api.py` eingebunden
- ✅ Endpoint-Import in `__init__.py` ergänzt
- ✅ Prefix: `/api/v1/mcp/policy/*`

***REMOVED******REMOVED******REMOVED*** **4. Python-Seed-Script** (`scripts/seed_policies.py`)
- ✅ Befüllt DB mit 3 Standard-Policies
- ✅ Ausführbar: `python scripts/seed_policies.py`

---

***REMOVED******REMOVED*** 🚀 Schnellstart

***REMOVED******REMOVED******REMOVED*** 1. Datenbank initialisieren
```bash
python scripts/seed_policies.py
```

**Output:**
```
✅ Seeded 3 policies to data/policies.db
```

***REMOVED******REMOVED******REMOVED*** 2. FastAPI-Server starten
```bash
uvicorn main:app --reload --port 8000
```

***REMOVED******REMOVED******REMOVED*** 3. API testen
```bash
***REMOVED*** Health-Check
curl http://localhost:8000/api/v1/health

***REMOVED*** Policies auflisten
curl http://localhost:8000/api/v1/mcp/policy/list

***REMOVED*** Simulator testen
curl -X POST http://localhost:8000/api/v1/mcp/policy/test \
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

***REMOVED******REMOVED******REMOVED*** 4. Frontend verbinden
Das Frontend (`packages/frontend-web`) muss nun auf **`http://localhost:8000/api/v1/mcp/policy/*`** zeigen.

Aktualisiere `packages/frontend-web/src/lib/mcp.ts`:

```typescript
const BASE_URL = "http://localhost:8000/api/v1/mcp"

export function useMcpQuery<T>(
  service: string,
  method: string,
  args: unknown[]
): UseQueryResult<T> {
  return useQuery({
    queryKey: ["mcp", service, method, ...args],
    queryFn: async (): Promise<T> => {
      const res = await fetch(`${BASE_URL}/${service}/${method}`)
      if (!res.ok) throw new Error(`MCP Error: ${res.statusText}`)
      return res.json() as Promise<T>
    },
  })
}
```

---

***REMOVED******REMOVED*** 📍 API-Endpoints (vollständige Liste)

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/v1/mcp/policy/list` | GET | Alle Policies |
| `/api/v1/mcp/policy/upsert` | POST | Bulk-Upsert (rules[]) |
| `/api/v1/mcp/policy/create` | POST | Einzelne Policy |
| `/api/v1/mcp/policy/update` | POST | Policy aktualisieren |
| `/api/v1/mcp/policy/delete` | POST | Policy löschen |
| `/api/v1/mcp/policy/test` | POST | Simulator |
| `/api/v1/mcp/policy/export` | GET | JSON-Download |
| `/api/v1/mcp/policy/restore` | POST | JSON-Import |

---

***REMOVED******REMOVED*** 🧪 API-Tests

***REMOVED******REMOVED******REMOVED*** List Policies
```bash
curl http://localhost:8000/api/v1/mcp/policy/list | jq
```

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "id": "pricing.auto.adjust",
      "when": {
        "kpiId": "margin",
        "severity": ["warn", "crit"]
      },
      "action": "pricing.adjust",
      ...
    }
  ]
}
```

***REMOVED******REMOVED******REMOVED*** Test Simulator
```bash
curl -X POST http://localhost:8000/api/v1/mcp/policy/test \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "id": "sim-1",
      "kpiId": "margin",
      "title": "Marge unter Ziel",
      "message": "Marge 14,2%",
      "severity": "warn",
      "delta": -3
    },
    "roles": ["manager"]
  }' | jq
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
    "resolvedParams": {
      "deltaPct": 1
    }
  }
}
```

***REMOVED******REMOVED******REMOVED*** Export Policies
```bash
curl http://localhost:8000/api/v1/mcp/policy/export > backup.json
```

***REMOVED******REMOVED******REMOVED*** Delete Policy
```bash
curl -X POST http://localhost:8000/api/v1/mcp/policy/delete \
  -H "Content-Type: application/json" \
  -d '{"id": "test.rule"}'
```

---

***REMOVED******REMOVED*** 📂 Dateistruktur

```
VALEO-NeuroERP-3.0/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── __init__.py          ***REMOVED*** ✅ policies import
│   │   │   └── policies.py          ***REMOVED*** ✅ NEU - Policy-Router
│   │   └── api.py                   ***REMOVED*** ✅ policies.router included
│   └── services/
│       └── policy_service.py        ***REMOVED*** ✅ NEU - Policy-Engine & Store
├── scripts/
│   └── seed_policies.py             ***REMOVED*** ✅ NEU - Python-Seed
├── data/
│   └── policies.db                  ***REMOVED*** ✅ SQLite-DB (generiert)
└── main.py                          ***REMOVED*** ✅ Keine Änderung nötig!
```

---

***REMOVED******REMOVED*** ✅ DoD-Check

- ✅ **Policy-Service (Python)** - Store + Engine
- ✅ **FastAPI-Router** - 8 Endpoints
- ✅ **API-Integration** - Router eingebunden
- ✅ **Seed-Script** - Python-Version
- ✅ **SQLite-Persistenz** - Shared DB (data/policies.db)
- ✅ **Pydantic-Validierung** - Alle Endpoints
- ✅ **Logging** - Alle Actions geloggt
- ✅ **Error-Handling** - HTTPException mit Details

---

***REMOVED******REMOVED*** 🔒 Sicherheit (TODO)

**Aktuell:** Keine Auth - alle Endpoints sind öffentlich!

**Für Production:**

1. **JWT-Auth hinzufügen:**
```python
from fastapi import Depends
from app.core.security import get_current_user

@router.post("/delete")
async def delete_policy(
    request: DeleteRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    ***REMOVED*** Nur admin/manager dürfen löschen
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    ...
```

2. **RBAC-Middleware:**
```python
from app.core.security import require_roles

@router.post("/delete")
@require_roles(["admin", "manager"])
async def delete_policy(...):
    ...
```

3. **Rate-Limiting:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/restore")
@limiter.limit("5/hour")
async def restore_policies(...):
    ...
```

---

***REMOVED******REMOVED*** 🚀 Frontend-Integration

Das Frontend (`/policies`) ist bereits fertig und zeigt auf `/api/mcp/policy/*`.

**Anpassung falls nötig:**

In `packages/frontend-web/src/lib/mcp.ts` die Base-URL ändern:

```typescript
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/mcp"
```

Dann `.env` anlegen:
```bash
***REMOVED*** packages/frontend-web/.env
VITE_API_URL=http://localhost:8000/api/v1/mcp
```

---

***REMOVED******REMOVED*** 📊 Standard-Policies

Nach `python scripts/seed_policies.py`:

***REMOVED******REMOVED******REMOVED*** 1. `pricing.auto.adjust`
- **Trigger:** Marge warn/crit
- **Action:** Preis +1%/+3%
- **Approval:** ✅ Manager/Admin
- **Zeitfenster:** Mo-Fr 08:00-18:00

***REMOVED******REMOVED******REMOVED*** 2. `inventory.auto.reorder`
- **Trigger:** Stock warn/crit
- **Action:** Nachbestellen (250/500)
- **Auto-Execute:** ✅
- **Zeitfenster:** Mo-Sa 07:00-20:00

***REMOVED******REMOVED******REMOVED*** 3. `sales.notify.drop`
- **Trigger:** Revenue warn/crit
- **Action:** Vertrieb benachrichtigen
- **Auto-Execute:** ✅
- **Zeitfenster:** 24/7

---

***REMOVED******REMOVED*** 🔧 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Port bereits belegt
```bash
uvicorn main:app --reload --port 8001
```

***REMOVED******REMOVED******REMOVED*** DB-Fehler
```bash
rm data/policies.db
python scripts/seed_policies.py
```

***REMOVED******REMOVED******REMOVED*** Frontend kann Backend nicht erreichen
1. Prüfe CORS in `app/core/config.py`
2. Füge `http://localhost:5173` zu `BACKEND_CORS_ORIGINS` hinzu
3. Starte FastAPI neu

---

***REMOVED******REMOVED*** 📚 Weiterführende Doku

- **TypeScript-Backend:** `src/services/policy/README.md`
- **Frontend:** `packages/frontend-web/docs/policy-manager-backend-integration.md`
- **Vollständige Doku:** `POLICY-MANAGER-COMPLETE.md`
- **Schnellstart:** `POLICY-QUICKSTART.md`

---

***REMOVED******REMOVED*** 🎉 Fertig!

**Der Policy-Manager ist vollständig in dein FastAPI-Backend integriert!**

**Nächste Schritte:**
1. ✅ Backend läuft (`uvicorn main:app --reload`)
2. ✅ Frontend läuft (`cd packages/frontend-web && pnpm run dev`)
3. ✅ Öffne http://localhost:5173/policies
4. 🚀 Policies verwalten, testen, importieren/exportieren!

---

**Möchtest du jetzt WebSocket-Support für Realtime-Policy-Updates hinzufügen?** 😊

