***REMOVED*** 🌐 Port-Übersicht - L3 Migration Toolkit

**Status:** ✅ **KEINE PORT-KONFLIKTE**

---

***REMOVED******REMOVED*** 📊 Port-Belegung

***REMOVED******REMOVED******REMOVED*** VALEO-NeuroERP (Haupt-System)

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Frontend (React) | **3000** | http://localhost:3000 | ✅ Läuft |
| Backend (FastAPI) | **8000** | http://localhost:8000 | ✅ Läuft |
| PostgreSQL | **5432** | localhost:5432 | ✅ Läuft |

***REMOVED******REMOVED******REMOVED*** L3 Migration Toolkit (Isoliert)

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Guacamole Web-UI | **8090** | http://localhost:8090/guacamole | ✅ Frei |
| Webtop (Linux Desktop) | **3010** | http://localhost:3010 | ✅ Frei |
| Guac PostgreSQL | - | 172.25.0.10:5432 | ✅ Intern |
| Guacd (Daemon) | - | 172.25.0.11:4822 | ✅ Intern |

---

***REMOVED******REMOVED*** 🎯 Zugriff

***REMOVED******REMOVED******REMOVED*** Während Migration-Arbeit gleichzeitig offen:

**Browser-Tabs:**
1. **VALEO Frontend** → http://localhost:3000
2. **VALEO Backend API** → http://localhost:8000/docs
3. **L3 via Guacamole** → http://localhost:8090/guacamole
4. **Webtop (optional)** → http://localhost:3010

**Workflow:**
```
Tab 1: L3-Maske (via Guacamole)
Tab 2: VALEO-Maske (zum Nachbauen)
Tab 3: VALEO API-Docs (für Backend-Integration)
Tab 4: Webtop (für Screenshots organisieren)
```

**→ Perfektes Setup für paralleles Arbeiten!** 🎨

---

***REMOVED******REMOVED*** 🔧 Port-Konflikte vermeiden

***REMOVED******REMOVED******REMOVED*** Falls Port 8090 belegt ist:

**Ändern in docker-compose.yml:**
```yaml
guacamole:
  ports:
    - "8091:8080"   ***REMOVED*** Statt 8090
```

**Dann verwenden:**
```
http://localhost:8091/guacamole
```

***REMOVED******REMOVED******REMOVED*** Falls Port 3010 belegt ist:

**Ändern in docker-compose.yml:**
```yaml
webtop:
  ports:
    - "3011:3000"   ***REMOVED*** Statt 3010
```

---

***REMOVED******REMOVED*** 🌐 Netzwerk-Isolation

***REMOVED******REMOVED******REMOVED*** L3 Migration Toolkit

**Netzwerk:** `l3-network`  
**Subnet:** `172.25.0.0/24`  
**Gateway:** `172.25.0.1`

**Container IPs:**
```
172.25.0.10 → l3-postgres
172.25.0.11 → l3-guacd
172.25.0.12 → l3-guacamole
172.25.0.13 → l3-webtop
```

***REMOVED******REMOVED******REMOVED*** VALEO-NeuroERP

**Netzwerk:** `valeo-network` (aus docker-compose.dev.yml)  
**Subnet:** Default Docker Bridge

**→ Komplett getrennt!** ✅

---

***REMOVED******REMOVED*** ✅ Port-Test

```powershell
***REMOVED*** Welche Ports sind belegt?
netstat -ano | findstr "LISTENING" | findstr ":3000 :8000 :8090 :3010"

***REMOVED*** Erwartetes Ergebnis:
***REMOVED*** :3000 → node.exe (VALEO Frontend)
***REMOVED*** :8000 → python.exe (VALEO Backend)
***REMOVED*** :8090 → Sollte frei sein (oder Docker)
***REMOVED*** :3010 → Sollte frei sein (oder Docker)
```

***REMOVED******REMOVED******REMOVED*** Wenn Ports belegt:

```powershell
***REMOVED*** Port 8090 finden
Get-Process -Id (Get-NetTCPConnection -LocalPort 8090).OwningProcess

***REMOVED*** Port 3010 finden
Get-Process -Id (Get-NetTCPConnection -LocalPort 3010).OwningProcess

***REMOVED*** Falls nötig: Process beenden oder andere Ports verwenden
```

---

***REMOVED******REMOVED*** 📊 Finale Port-Tabelle

| Port | Service | Projekt | Konflikt? |
|------|---------|---------|-----------|
| 3000 | React Frontend | VALEO-NeuroERP | - |
| 3010 | Webtop | L3 Migration | ✅ Frei |
| 5432 | PostgreSQL | VALEO-NeuroERP | - |
| 8000 | FastAPI Backend | VALEO-NeuroERP | - |
| 8090 | Guacamole | L3 Migration | ✅ Frei |

**GESAMT: 5 Ports, 0 Konflikte** ✅

---

***REMOVED******REMOVED*** 🎯 Zusammenfassung

**L3 Migration Toolkit ist deployment-ready:**

- ✅ Eigenes Verzeichnis (`l3-migration-toolkit/`)
- ✅ Eigenes Netzwerk (172.25.0.0/24)
- ✅ Eigene Ports (8090, 3010)
- ✅ Eigene Container-Namen (`l3-*`)
- ✅ Eigene Volumes (`l3-migration-*`)

**Parallel zu VALEO-NeuroERP nutzbar ohne Konflikte!** 🚀

---

**Bereit zum Starten?** Alle Dateien sind erstellt! 😊

