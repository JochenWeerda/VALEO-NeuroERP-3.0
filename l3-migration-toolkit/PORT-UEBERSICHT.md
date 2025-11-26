# 🌐 Port-Übersicht - L3 Migration Toolkit

**Status:** ✅ **KEINE PORT-KONFLIKTE**

---

## 📊 Port-Belegung

### VALEO-NeuroERP (Haupt-System)

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Frontend (React) | **3000** | http://localhost:3000 | ✅ Läuft |
| Backend (FastAPI) | **8000** | http://localhost:8000 | ✅ Läuft |
| PostgreSQL | **5432** | localhost:5432 | ✅ Läuft |

### L3 Migration Toolkit (Isoliert)

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Guacamole Web-UI | **8090** | http://localhost:8090/guacamole | ✅ Frei |
| Webtop (Linux Desktop) | **3010** | http://localhost:3010 | ✅ Frei |
| Guac PostgreSQL | - | 172.25.0.10:5432 | ✅ Intern |
| Guacd (Daemon) | - | 172.25.0.11:4822 | ✅ Intern |

---

## 🎯 Zugriff

### Während Migration-Arbeit gleichzeitig offen:

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

## 🔧 Port-Konflikte vermeiden

### Falls Port 8090 belegt ist:

**Ändern in docker-compose.yml:**
```yaml
guacamole:
  ports:
    - "8091:8080"   # Statt 8090
```

**Dann verwenden:**
```
http://localhost:8091/guacamole
```

### Falls Port 3010 belegt ist:

**Ändern in docker-compose.yml:**
```yaml
webtop:
  ports:
    - "3011:3000"   # Statt 3010
```

---

## 🌐 Netzwerk-Isolation

### L3 Migration Toolkit

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

### VALEO-NeuroERP

**Netzwerk:** `valeo-network` (aus docker-compose.dev.yml)  
**Subnet:** Default Docker Bridge

**→ Komplett getrennt!** ✅

---

## ✅ Port-Test

```powershell
# Welche Ports sind belegt?
netstat -ano | findstr "LISTENING" | findstr ":3000 :8000 :8090 :3010"

# Erwartetes Ergebnis:
# :3000 → node.exe (VALEO Frontend)
# :8000 → python.exe (VALEO Backend)
# :8090 → Sollte frei sein (oder Docker)
# :3010 → Sollte frei sein (oder Docker)
```

### Wenn Ports belegt:

```powershell
# Port 8090 finden
Get-Process -Id (Get-NetTCPConnection -LocalPort 8090).OwningProcess

# Port 3010 finden
Get-Process -Id (Get-NetTCPConnection -LocalPort 3010).OwningProcess

# Falls nötig: Process beenden oder andere Ports verwenden
```

---

## 📊 Finale Port-Tabelle

| Port | Service | Projekt | Konflikt? |
|------|---------|---------|-----------|
| 3000 | React Frontend | VALEO-NeuroERP | - |
| 3010 | Webtop | L3 Migration | ✅ Frei |
| 5432 | PostgreSQL | VALEO-NeuroERP | - |
| 8000 | FastAPI Backend | VALEO-NeuroERP | - |
| 8090 | Guacamole | L3 Migration | ✅ Frei |

**GESAMT: 5 Ports, 0 Konflikte** ✅

---

## 🎯 Zusammenfassung

**L3 Migration Toolkit ist deployment-ready:**

- ✅ Eigenes Verzeichnis (`l3-migration-toolkit/`)
- ✅ Eigenes Netzwerk (172.25.0.0/24)
- ✅ Eigene Ports (8090, 3010)
- ✅ Eigene Container-Namen (`l3-*`)
- ✅ Eigene Volumes (`l3-migration-*`)

**Parallel zu VALEO-NeuroERP nutzbar ohne Konflikte!** 🚀

---

**Bereit zum Starten?** Alle Dateien sind erstellt! 😊

