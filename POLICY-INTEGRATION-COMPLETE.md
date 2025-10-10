# ✅ Policy Manager - FastAPI Integration KOMPLETT!

## 🎉 Backend vollständig integriert!

Der Policy-Manager ist jetzt nahtlos in dein **FastAPI-Backend** integriert!

---

## 📦 Was wurde integriert

### **1. Policy Service** (`app/services/policy_service.py`)
- ✅ `PolicyStore` - SQLite-Persistenz
- ✅ `PolicyEngine` - Decision-Engine
- ✅ Pydantic-Models (Rule, Alert, Decision, etc.)
- ✅ `within_window()` - Zeitfenster-Prüfung
- ✅ `resolve_params()` - Parameter-Auflösung
- ✅ `decide()` - Policy-Matching

### **2. FastAPI-Router** (`app/api/v1/endpoints/policies.py`)
- ✅ `GET /api/v1/mcp/policy/list`
- ✅ `POST /api/v1/mcp/policy/upsert`
- ✅ `POST /api/v1/mcp/policy/create`
- ✅ `POST /api/v1/mcp/policy/update`
- ✅ `POST /api/v1/mcp/policy/delete`
- ✅ `POST /api/v1/mcp/policy/test`
- ✅ `GET /api/v1/mcp/policy/export`
- ✅ `POST /api/v1/mcp/policy/restore`

### **3. API-Integration**
- ✅ Router in `app/api/v1/api.py` eingebunden
- ✅ Endpoint-Import in `__init__.py` ergänzt
- ✅ Prefix: `/api/v1/mcp/policy/*`

### **4. Python-Seed-Script** (`scripts/seed_policies.py`)
- ✅ Befüllt DB mit 3 Standard-Policies
- ✅ Ausführbar: `python scripts/seed_policies.py`

---

## 🚀 Schnellstart

### 1. Datenbank initialisieren
```bash
python scripts/seed_policies.py
```

**Output:**
```
✅ Seeded 3 policies to data/policies.db
```

### 2. FastAPI-Server starten
```bash
uvicorn main:app --reload --port 8000
```

### 3. API testen
```bash
# Health-Check
curl http://localhost:8000/api/v1/health

# Policies auflisten
curl http://localhost:8000/api/v1/mcp/policy/list

# Simulator testen
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

### 4. Frontend verbinden
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

## 📍 API-Endpoints (vollständige Liste)

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

## 🧪 API-Tests

### List Policies
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

### Test Simulator
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

### Export Policies
```bash
curl http://localhost:8000/api/v1/mcp/policy/export > backup.json
```

### Delete Policy
```bash
curl -X POST http://localhost:8000/api/v1/mcp/policy/delete \
  -H "Content-Type: application/json" \
  -d '{"id": "test.rule"}'
```

---

## 📂 Dateistruktur

```
VALEO-NeuroERP-3.0/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   ├── __init__.py          # ✅ policies import
│   │   │   └── policies.py          # ✅ NEU - Policy-Router
│   │   └── api.py                   # ✅ policies.router included
│   └── services/
│       └── policy_service.py        # ✅ NEU - Policy-Engine & Store
├── scripts/
│   └── seed_policies.py             # ✅ NEU - Python-Seed
├── data/
│   └── policies.db                  # ✅ SQLite-DB (generiert)
└── main.py                          # ✅ Keine Änderung nötig!
```

---

## ✅ DoD-Check

- ✅ **Policy-Service (Python)** - Store + Engine
- ✅ **FastAPI-Router** - 8 Endpoints
- ✅ **API-Integration** - Router eingebunden
- ✅ **Seed-Script** - Python-Version
- ✅ **SQLite-Persistenz** - Shared DB (data/policies.db)
- ✅ **Pydantic-Validierung** - Alle Endpoints
- ✅ **Logging** - Alle Actions geloggt
- ✅ **Error-Handling** - HTTPException mit Details

---

## 🔒 Sicherheit (TODO)

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
    # Nur admin/manager dürfen löschen
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

## 🚀 Frontend-Integration

Das Frontend (`/policies`) ist bereits fertig und zeigt auf `/api/mcp/policy/*`.

**Anpassung falls nötig:**

In `packages/frontend-web/src/lib/mcp.ts` die Base-URL ändern:

```typescript
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1/mcp"
```

Dann `.env` anlegen:
```bash
# packages/frontend-web/.env
VITE_API_URL=http://localhost:8000/api/v1/mcp
```

---

## 📊 Standard-Policies

Nach `python scripts/seed_policies.py`:

### 1. `pricing.auto.adjust`
- **Trigger:** Marge warn/crit
- **Action:** Preis +1%/+3%
- **Approval:** ✅ Manager/Admin
- **Zeitfenster:** Mo-Fr 08:00-18:00

### 2. `inventory.auto.reorder`
- **Trigger:** Stock warn/crit
- **Action:** Nachbestellen (250/500)
- **Auto-Execute:** ✅
- **Zeitfenster:** Mo-Sa 07:00-20:00

### 3. `sales.notify.drop`
- **Trigger:** Revenue warn/crit
- **Action:** Vertrieb benachrichtigen
- **Auto-Execute:** ✅
- **Zeitfenster:** 24/7

---

## 🔧 Troubleshooting

### Port bereits belegt
```bash
uvicorn main:app --reload --port 8001
```

### DB-Fehler
```bash
rm data/policies.db
python scripts/seed_policies.py
```

### Frontend kann Backend nicht erreichen
1. Prüfe CORS in `app/core/config.py`
2. Füge `http://localhost:5173` zu `BACKEND_CORS_ORIGINS` hinzu
3. Starte FastAPI neu

---

## 📚 Weiterführende Doku

- **TypeScript-Backend:** `src/services/policy/README.md`
- **Frontend:** `packages/frontend-web/docs/policy-manager-backend-integration.md`
- **Vollständige Doku:** `POLICY-MANAGER-COMPLETE.md`
- **Schnellstart:** `POLICY-QUICKSTART.md`

---

## 🎉 Fertig!

**Der Policy-Manager ist vollständig in dein FastAPI-Backend integriert!**

**Nächste Schritte:**
1. ✅ Backend läuft (`uvicorn main:app --reload`)
2. ✅ Frontend läuft (`cd packages/frontend-web && pnpm run dev`)
3. ✅ Öffne http://localhost:5173/policies
4. 🚀 Policies verwalten, testen, importieren/exportieren!

---

**Möchtest du jetzt WebSocket-Support für Realtime-Policy-Updates hinzufügen?** 😊

