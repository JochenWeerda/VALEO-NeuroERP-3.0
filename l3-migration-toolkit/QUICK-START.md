# ⚡ L3 Migration Toolkit - Quick Start

**Ziel:** In 10 Minuten einsatzbereit!

---

## 📋 Checkliste

```powershell
# ✅ 1. Verzeichnis
cd C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit

# ✅ 2. .env erstellen
"POSTGRES_PASSWORD=GuacSecure2024!
WEBTOP_PASSWORD=ValeoWebtop2024!
L3_RDP_USER=Jochen
L3_RDP_PASSWORD=DEIN_WINDOWS_PASSWORT_HIER" | Out-File -FilePath .env -Encoding ASCII

# ✅ 3. Docker starten
docker compose up -d

# ✅ 4. Warten (wichtig!)
Start-Sleep -Seconds 30

# ✅ 5. Guacamole DB init (EINMALIG!)
docker exec -i l3-guacamole /opt/guacamole/bin/initdb.sh --postgres | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db

# ✅ 6. Guacamole neu starten
docker restart l3-guacamole
Start-Sleep -Seconds 10

# ✅ 7. Guacamole öffnen
Start-Process "http://localhost:8090/guacamole"
# Login: guacadmin / guacadmin
```

---

## 🔐 In Guacamole (Web-UI)

### 1. Passwort ändern (SOFORT!)

1. Oben rechts: **guacadmin** → **Settings**
2. **Change Password**
3. Neues Passwort: `GuacSecure2024!` (oder besser)

### 2. RDP-Verbindung anlegen

**Settings** → **Connections** → **New Connection**

```
Name: L3-Windows-RDP
Protocol: RDP

Parameters:
  Hostname: host.docker.internal
  Port: 3389
  Username: Jochen
  Password: [DEIN WINDOWS PASSWORT]
  Security mode: Any
  Ignore server certificate: ✅

Performance:
  ✅ Disable wallpaper
  ✅ Disable font smoothing
```

**Save** → **Back to home** → **Klick auf "L3-Windows-RDP"**

**→ Dein Windows-Desktop sollte im Browser erscheinen!** 🎉

---

## 📸 Screenshot-Test

```powershell
# Playwright installieren
cd playwright-snap
npm install
npm run install:pw

# Umgebungsvariablen
$env:GUAC_URL = "http://localhost:8090/guacamole"
$env:GUAC_USER = "guacadmin"
$env:GUAC_PASS = "GuacSecure2024!"
$env:OUT_DIR = "../screenshots"

# Screenshot machen
npm run snap
```

**Ergebnis:** `screenshots/l3_....png` ✅

---

## ⏰ Automation einrichten

```powershell
# PowerShell-Script testen
.\run-screenshot.ps1

# Task Scheduler (alle 5 Min)
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\run-screenshot.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "L3-Screenshot-Automation" -Action $Action -Trigger $Trigger -User "$env:USERNAME" -RunLevel Highest
```

---

## 🎯 Nächste Schritte

1. ✅ L3 auf Windows starten
2. ✅ Verschiedene Masken öffnen & durchklicken
3. ✅ 24 Stunden laufen lassen → ~300 Screenshots
4. ⏳ Screenshots organisieren (nach Modul sortieren)
5. ⏳ Feldmapping erstellen
6. ⏳ VALEO-Masken nachbauen

---

## 📊 Services im Überblick

| Service | URL | Credentials |
|---------|-----|-------------|
| **Guacamole** | http://localhost:8090/guacamole | guacadmin / GuacSecure2024! |
| **Webtop** | http://localhost:3010 | valeo / ValeoWebtop2024! |
| **VALEO Frontend** | http://localhost:3000 | - |
| **VALEO Backend** | http://localhost:8000 | - |

---

## 🐛 Probleme?

```powershell
# Container-Status
docker compose ps

# Logs
docker compose logs -f

# Neu starten
docker compose restart

# Komplett neu
docker compose down -v
docker compose up -d
# → DB-Init wiederholen
```

---

## ✅ Erfolgs-Kriterien

Nach Setup solltest du:

- ✅ Guacamole im Browser sehen
- ✅ Auf deinen Windows-Desktop via RDP/VNC zugreifen
- ✅ L3-Software im Guacamole-Browser starten können
- ✅ Screenshots automatisch erstellen können
- ✅ Task Scheduler läuft

**→ Dann bist du ready für L3-Migration!** 🚀

---

**Netzwerk:** 172.25.0.0/24 (isoliert)  
**Ports:** 8090 (Guacamole), 3010 (Webtop)  
**Status:** ✅ READY TO DEPLOY


