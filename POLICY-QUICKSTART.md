***REMOVED*** 🚀 Policy Manager - Schnellstart

***REMOVED******REMOVED*** 3 Schritte zur vollen Funktionalität

***REMOVED******REMOVED******REMOVED*** 1️⃣ Datenbank initialisieren
```bash
pnpm run policy:seed
```
✅ Erstellt `data/policies.db` mit 3 Standard-Policies

***REMOVED******REMOVED******REMOVED*** 2️⃣ Backend starten
```bash
pnpm run mcp:dev
```
✅ Server läuft auf **http://localhost:7070**

***REMOVED******REMOVED******REMOVED*** 3️⃣ Frontend öffnen
Navigiere zu: **http://localhost:5173/policies**

---

***REMOVED******REMOVED*** ✨ Fertig!

Du kannst jetzt:
- ✅ Policies ansehen/löschen
- ✅ JSON importieren/exportieren
- ✅ Simulator testen (Alert → Decision)

---

***REMOVED******REMOVED*** 🧪 API testen

```bash
***REMOVED*** Health-Check
curl http://localhost:7070/healthz

***REMOVED*** Policies auflisten
curl http://localhost:7070/api/mcp/policy/list

***REMOVED*** Simulator
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

***REMOVED******REMOVED*** 📚 Weitere Infos

- Vollständige Doku: `POLICY-MANAGER-COMPLETE.md`
- Backend-Details: `src/services/policy/README.md`
- Frontend-Integration: `packages/frontend-web/docs/policy-manager-backend-integration.md`

