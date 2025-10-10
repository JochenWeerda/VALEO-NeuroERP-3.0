# Policy Manager - Backend Integration

## Übersicht

Der Policy Manager benötigt folgende MCP-Endpoints für vollständige Funktionalität.

## Erforderliche Endpoints

### 1. GET `/api/mcp/policy/list`

Listet alle aktiven Policy-Regeln auf.

**Response:**
```json
{
  "ok": true,
  "data": [
    {
      "id": "pricing.auto.adjust",
      "when": { "kpiId": "margin", "severity": ["warn","crit"] },
      "action": "pricing.adjust",
      "params": { "deltaPct": { "warn": 1, "crit": 3 } },
      "limits": { "maxDailyPct": 3, "maxWeeklyPct": 7 },
      "window": { "days": [1,2,3,4,5], "start": "08:00", "end": "18:00" },
      "approval": { "required": true, "roles": ["manager","admin"], "bypassIfSeverity": "crit" },
      "autoExecute": false,
      "autoSuggest": true
    }
  ]
}
```

### 2. POST `/api/mcp/policy/upsert`

Erstellt oder aktualisiert mehrere Policies (Bulk-Import).

**Request:**
```json
{
  "rules": [
    {
      "id": "inventory.auto.reorder",
      "when": { "kpiId": "stock", "severity": ["warn","crit"] },
      "action": "inventory.reorder",
      "params": { "qty": { "warn": 250, "crit": 500 } },
      "limits": { "maxDailyQty": 2000 },
      "window": { "days": [1,2,3,4,5,6], "start": "07:00", "end": "20:00" },
      "approval": { "required": false },
      "autoExecute": true,
      "autoSuggest": true
    }
  ]
}
```

**Response:**
```json
{
  "ok": true
}
```

### 3. POST `/api/mcp/policy/delete`

Löscht eine Policy.

**Request:**
```json
{
  "id": "pricing.auto.adjust"
}
```

**Response:**
```json
{
  "ok": true
}
```

### 4. POST `/api/mcp/policy/test`

Testet eine Policy-Entscheidung gegen einen Alert (Simulator).

**Request:**
```json
{
  "alert": {
    "id": "sim-1",
    "kpiId": "margin",
    "title": "Marge unter Ziel",
    "message": "Marge 14,2%",
    "severity": "warn",
    "delta": -3
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

Oder bei Ablehnung:
```json
{
  "ok": true,
  "decision": {
    "type": "deny",
    "reason": "Outside window"
  }
}
```

## Persistenz

Policies sollten persistent gespeichert werden:
- **SQLite**: Eigene Tabelle `policies` mit JSON-Spalte für `rule`
- **JSON-Datei**: `config/policies.json` (einfacher, aber weniger robust)
- **PostgreSQL**: Separate Tabelle mit JSONB-Spalte

## Validierung

Serverseitig sollte die Zod-Schema-Validierung aus `packages/frontend-web/src/policy/schema.ts` repliziert werden, um ungültige Regeln abzulehnen.

## Realtime-Updates

Bei Änderungen an Policies sollte ein WebSocket-Event gesendet werden:

```json
{
  "service": "policy",
  "type": "rules-updated"
}
```

Dies triggert automatisch ein Re-Fetch im Frontend via React Query Invalidation.

## Sicherheit

- **RBAC**: Nur Nutzer mit Rolle `admin` oder `manager` sollten Policies ändern dürfen
- **Audit-Log**: Jede Änderung sollte im Audit-Log festgehalten werden
- **Validierung**: Alle Regeln müssen serverseitig gegen Schema validiert werden

## Beispiel-Implementation (Python/FastAPI)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json

router = APIRouter(prefix="/api/mcp/policy")

# In-Memory Store (ersetzen durch DB)
policies_store: List[Dict[str, Any]] = []

class Rule(BaseModel):
    id: str
    when: Dict[str, Any]
    action: str
    params: Dict[str, Any] | None = None
    limits: Dict[str, float] | None = None
    window: Dict[str, Any] | None = None
    approval: Dict[str, Any] | None = None
    autoExecute: bool | None = None
    autoSuggest: bool | None = None

@router.get("/list")
async def list_policies():
    return {"ok": True, "data": policies_store}

@router.post("/upsert")
async def upsert_policies(body: Dict[str, Any]):
    rules = body.get("rules", [])
    for rule_data in rules:
        rule = Rule(**rule_data)
        # Ersetze bestehende oder füge hinzu
        existing_idx = next((i for i, r in enumerate(policies_store) if r["id"] == rule.id), None)
        if existing_idx is not None:
            policies_store[existing_idx] = rule.dict()
        else:
            policies_store.append(rule.dict())
    
    # Broadcast WS-Event
    # await ws_broadcast({"service": "policy", "type": "rules-updated"})
    
    return {"ok": True}

@router.post("/delete")
async def delete_policy(body: Dict[str, str]):
    rule_id = body.get("id")
    global policies_store
    policies_store = [r for r in policies_store if r["id"] != rule_id]
    
    # Broadcast WS-Event
    # await ws_broadcast({"service": "policy", "type": "rules-updated"})
    
    return {"ok": True}

@router.post("/test")
async def test_policy(body: Dict[str, Any]):
    # Importiere Policy-Engine aus Phase K
    # decision = policy_engine.decide(body["roles"], body["alert"])
    
    # Mock für Demo
    decision = {
        "type": "allow",
        "execute": False,
        "needsApproval": True,
        "approverRoles": ["manager", "admin"],
        "ruleId": "pricing.auto.adjust",
        "resolvedParams": {"deltaPct": 1}
    }
    
    return {"ok": True, "decision": decision}
```

## Next Steps

1. Backend-Endpoints implementieren (siehe Beispiel oben)
2. Policy-Engine aus `packages/frontend-web/src/policy/engine.ts` nach Python/Backend portieren
3. WebSocket-Events für Realtime-Updates einrichten
4. Audit-Logging für Policy-Änderungen aktivieren
5. RBAC-Checks für Policy-CRUD aktivieren

