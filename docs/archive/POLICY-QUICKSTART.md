# 🚀 Policy Manager - Schnellstart

## 3 Schritte zur vollen Funktionalität

### 1️⃣ Datenbank initialisieren
```bash
pnpm run policy:seed
```
✅ Erstellt `data/policies.db` mit 3 Standard-Policies

### 2️⃣ Backend starten
```bash
pnpm run mcp:dev
```
✅ Server läuft auf **http://localhost:7070**

### 3️⃣ Frontend öffnen
Navigiere zu: **http://localhost:5173/policies**

---

## ✨ Fertig!

Du kannst jetzt:
- ✅ Policies ansehen/löschen
- ✅ JSON importieren/exportieren
- ✅ Simulator testen (Alert → Decision)

---

## 🧪 API testen

```bash
# Health-Check
curl http://localhost:7070/healthz

# Policies auflisten
curl http://localhost:7070/api/mcp/policy/list

# Simulator
curl -X POST http://localhost:7070/api/mcp/policy/test \
  -H "Content-Type: application/json" \
  -d '{
    "alert": {
      "id": "test",
      "kpiId": "margin",
      "title": "Test",
      "message": "Test",
      "severity": "warn"
    },
    "roles": ["manager"]
  }'
```

---

## 📚 Weitere Infos

- Vollständige Doku: `POLICY-MANAGER-COMPLETE.md`
- Backend-Details: `src/services/policy/README.md`
- Frontend-Integration: `packages/frontend-web/docs/policy-manager-backend-integration.md`


