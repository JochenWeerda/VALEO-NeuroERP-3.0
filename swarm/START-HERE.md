# 🚀 Swarm System - Start Here

## Schnellstart (3 Schritte)

### 1️⃣ Umgebungsvariablen setzen

```powershell
# PowerShell (Windows)
.\swarm\start-swarm.ps1
```

Das Script:
- ✅ Prüft Docker
- ✅ Erstellt `.env.swarm` falls nicht vorhanden
- ✅ Startet alle Services
- ✅ Zeigt Status

**Oder manuell:**

```powershell
# .env.swarm erstellen/bearbeiten
$env:NEUROERP_URL="http://localhost:3000"
$env:NEUROERP_USER="admin"
$env:NEUROERP_PASS="admin123"
```

### 2️⃣ Frontend prüfen/starten

**Option A: Bestehendes Frontend nutzen (wenn bereits auf localhost:3000 läuft)**

```powershell
# Prüfe Health-Endpoint
curl http://localhost:3000/health
```

**Option B: Neues Frontend für Swarm starten**

```powershell
# Starte Frontend im Swarm-Netzwerk
docker compose -f docker-compose.swarm.yml up neuroerp-frontend -d

# Warte auf Ready
docker compose -f docker-compose.swarm.yml logs -f neuroerp-frontend
```

### 3️⃣ Erste Mission starten

**UI-Explorer (Finance Module explorieren):**

```powershell
# Mit Docker
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

# Oder lokal
python swarm/ui_explorer.py
```

**Output:**
- 📸 Screenshots: `evidence/screenshots/`
- 📝 Handoff: `swarm/handoffs/ui-explorer-finance-*.md`

## 📋 Nächste Schritte

1. **Tests generieren** aus Handoff-Notizen
2. **GAP-Analyse** durchführen
3. **Lücken schließen** basierend auf Analyse

## 📚 Dokumentation

- **Quickstart**: `swarm/QUICKSTART.md`
- **README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`

## 🆘 Hilfe

- **Troubleshooting**: Siehe `swarm/QUICKSTART.md`
- **Logs anzeigen**: `docker compose -f docker-compose.swarm.yml logs -f`
- **Services stoppen**: `docker compose -f docker-compose.swarm.yml down`


