***REMOVED*** L3 Migration Toolkit - Setup-Anleitung

**Zweck:** Automatische Screenshots & Analyse von L3-Masken für VALEO-NeuroERP Migration

---

***REMOVED******REMOVED*** 🎯 Isoliertes Setup

***REMOVED******REMOVED******REMOVED*** Netzwerk

**IP-Bereich:** `172.25.0.0/24` (komplett isoliert von VALEO-NeuroERP)

| Service | IP | Port (Host) | Port (Container) |
|---------|-----|-------------|------------------|
| PostgreSQL | 172.25.0.10 | - | 5432 |
| Guacd | 172.25.0.11 | - | 4822 |
| Guacamole | 172.25.0.12 | **8090** | 8080 |
| Webtop | 172.25.0.13 | **3010** | 3000 |

**VALEO-NeuroERP läuft weiter auf:**
- Frontend: Port 3000
- Backend: Port 8000  
- PostgreSQL: Port 5432

**→ Keine Konflikte!** ✅

---

***REMOVED******REMOVED*** 🚀 Quick Start

***REMOVED******REMOVED******REMOVED*** Schritt 1: Voraussetzungen prüfen

```powershell
***REMOVED*** Docker Desktop läuft?
docker version

***REMOVED*** Remotedesktop aktiv?
***REMOVED*** Einstellungen → System → Remotedesktop → Aktiviert
```

***REMOVED******REMOVED******REMOVED*** Schritt 2: .env-Datei erstellen

```powershell
***REMOVED*** Im Verzeichnis l3-migration-toolkit/
Copy-Item .env.example .env

***REMOVED*** .env bearbeiten:
***REMOVED*** - POSTGRES_PASSWORD setzen
***REMOVED*** - L3_RDP_PASSWORD mit deinem Windows-Passwort
```

***REMOVED******REMOVED******REMOVED*** Schritt 3: Container starten

```powershell
cd C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit

docker compose up -d
```

**Warte ~30 Sekunden** für vollständigen Start.

***REMOVED******REMOVED******REMOVED*** Schritt 4: Guacamole DB initialisieren (EINMALIG!)

```powershell
docker exec -i l3-guacamole /opt/guacamole/bin/initdb.sh --postgres | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db
```

***REMOVED******REMOVED******REMOVED*** Schritt 5: Guacamole neu starten

```powershell
docker restart l3-guacamole
```

**Warte ~10 Sekunden**.

---

***REMOVED******REMOVED*** 🔐 Guacamole einrichten

***REMOVED******REMOVED******REMOVED*** Login

**URL:** http://localhost:8090/guacamole  
**User:** `guacadmin`  
**Pass:** `guacadmin` (⚠️ **SOFORT ÄNDERN!**)

***REMOVED******REMOVED******REMOVED*** Passwort ändern

1. Oben rechts: **guacadmin** → **Settings**
2. **Preferences** → **Change Password**
3. Neues sicheres Passwort setzen
4. Speichern

***REMOVED******REMOVED******REMOVED*** RDP-Verbindung zu Windows (L3) anlegen

1. **Settings** → **Connections** → **New Connection**
2. **Name:** `L3-Windows-RDP`
3. **Protocol:** `RDP`
4. **Parameters:**
   - **Hostname:** `host.docker.internal`
   - **Port:** `3389`
   - **Username:** `Jochen` (dein Windows-User)
   - **Password:** (dein Windows-Passwort)
   - **Security mode:** `Any`
   - **Ignore server certificate:** ✅
5. **Performance-Optimierungen:**
   - ✅ Disable wallpaper
   - ✅ Disable font smoothing
   - ✅ Disable full window drag
6. **Speichern**

***REMOVED******REMOVED******REMOVED*** Alternative: VNC-Verbindung (empfohlen bei Session-Problemen)

**Falls RDP schwarzen Bildschirm zeigt:**

1. **TightVNC auf Windows installieren:**
   - Download: https://www.tightvnc.com/
   - Installation: Server + Viewer
   - Port: 5900
   - Passwort setzen

2. **In Guacamole VNC-Connection anlegen:**
   - **Name:** `L3-Windows-VNC`
   - **Protocol:** `VNC`
   - **Hostname:** `host.docker.internal`
   - **Port:** `5900`
   - **Password:** (dein VNC-Passwort)

---

***REMOVED******REMOVED*** 📸 Screenshot-Automation einrichten

***REMOVED******REMOVED******REMOVED*** Installation

```powershell
cd C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\playwright-snap

***REMOVED*** Dependencies installieren
npm install

***REMOVED*** Playwright Browser installieren
npm run install:pw
```

***REMOVED******REMOVED******REMOVED*** Konfiguration

**Umgebungsvariablen setzen:**

```powershell
$env:GUAC_URL = "http://localhost:8090/guacamole"
$env:GUAC_USER = "guacadmin"
$env:GUAC_PASS = "DEIN_NEUES_PASSWORT"
$env:CONNECTION_NAME = "L3-Windows-RDP"
$env:OUT_DIR = "C:/Users/Jochen/VALEO-NeuroERP-3.0/l3-migration-toolkit/screenshots"
$env:WAIT_SECONDS = "10"
```

***REMOVED******REMOVED******REMOVED*** Test-Screenshot

```powershell
npm run snap
```

**Ergebnis:** Screenshot in `screenshots/l3_YYYY-MM-DD....png`

---

***REMOVED******REMOVED*** ⏰ Automatische Screenshots (Task Scheduler)

***REMOVED******REMOVED******REMOVED*** PowerShell-Script erstellen

**Datei:** `l3-migration-toolkit/run-screenshot.ps1`

```powershell
***REMOVED***!/usr/bin/env pwsh
***REMOVED*** L3 Screenshot Automation

$ErrorActionPreference = "Stop"

***REMOVED*** Wechsle ins Playwright-Verzeichnis
Set-Location "C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\playwright-snap"

***REMOVED*** Umgebungsvariablen
$env:GUAC_URL = "http://localhost:8090/guacamole"
$env:GUAC_USER = "guacadmin"
$env:GUAC_PASS = "DEIN_PASSWORT_HIER"  ***REMOVED*** ⚠️ ANPASSEN!
$env:CONNECTION_NAME = "L3-Windows-RDP"
$env:OUT_DIR = "C:/Users/Jochen/VALEO-NeuroERP-3.0/l3-migration-toolkit/screenshots"
$env:WAIT_SECONDS = "10"

***REMOVED*** Screenshot erstellen
try {
    npm run snap
    Write-Host "✅ Screenshot erfolgreich" -ForegroundColor Green
} catch {
    Write-Host "❌ Fehler: $_" -ForegroundColor Red
    exit 1
}
```

***REMOVED******REMOVED******REMOVED*** Task Scheduler einrichten

```powershell
***REMOVED*** Task anlegen (alle 5 Minuten)
$Action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-ExecutionPolicy Bypass -File C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\run-screenshot.ps1"

$Trigger = New-ScheduledTaskTrigger `
  -Once `
  -At (Get-Date).AddMinutes(1) `
  -RepetitionInterval (New-TimeSpan -Minutes 5) `
  -RepetitionDuration ([TimeSpan]::MaxValue)

Register-ScheduledTask `
  -TaskName "L3-Screenshot-Automation" `
  -Action $Action `
  -Trigger $Trigger `
  -Description "Automatische Screenshots von L3-Masken für VALEO-NeuroERP Migration" `
  -User "$env:USERNAME" `
  -RunLevel Highest

Write-Host "✅ Task Scheduler eingerichtet: Alle 5 Minuten" -ForegroundColor Green
```

***REMOVED******REMOVED******REMOVED*** Task verwalten

```powershell
***REMOVED*** Status prüfen
Get-ScheduledTask -TaskName "L3-Screenshot-Automation"

***REMOVED*** Manuell ausführen
Start-ScheduledTask -TaskName "L3-Screenshot-Automation"

***REMOVED*** Deaktivieren
Disable-ScheduledTask -TaskName "L3-Screenshot-Automation"

***REMOVED*** Löschen
Unregister-ScheduledTask -TaskName "L3-Screenshot-Automation" -Confirm:$false
```

---

***REMOVED******REMOVED*** 📊 Screenshots analysieren

***REMOVED******REMOVED******REMOVED*** Metadaten ansehen

```powershell
Get-ChildItem C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\screenshots\*.json | Get-Content | ConvertFrom-Json
```

***REMOVED******REMOVED******REMOVED*** Statistik

```powershell
$screenshots = Get-ChildItem C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit\screenshots\*.png

Write-Host "📊 L3-Screenshot Statistik:" -ForegroundColor Cyan
Write-Host "   Gesamt-Screenshots: $($screenshots.Count)"
Write-Host "   Gesamtgröße: $([math]::Round(($screenshots | Measure-Object -Property Length -Sum).Sum / 1MB, 2)) MB"
Write-Host "   Ältester: $($screenshots | Sort-Object LastWriteTime | Select-Object -First 1 | Select-Object -ExpandProperty LastWriteTime)"
Write-Host "   Neuester: $($screenshots | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Select-Object -ExpandProperty LastWriteTime)"
```

---

***REMOVED******REMOVED*** 🔧 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: "Keine Verbindung gefunden"

**Lösung:** Prüfe in Guacamole Web-UI, ob Verbindung angelegt ist:
1. Login: http://localhost:8090/guacamole
2. Settings → Connections
3. Falls leer: RDP/VNC-Connection anlegen (siehe oben)

***REMOVED******REMOVED******REMOVED*** Problem: "Schwarzer Bildschirm" bei RDP

**Ursache:** Windows erlaubt nur eine aktive RDP-Session.

**Lösung 1:** TightVNC verwenden (siehe Anleitung oben)

**Lösung 2:** Windows-Session trennen (nicht abmelden):
```powershell
***REMOVED*** In RDP-Session
tsdiscon
```

***REMOVED******REMOVED******REMOVED*** Problem: "Canvas nicht gefunden"

**Lösung:** Wartezeit erhöhen:
```powershell
$env:WAIT_SECONDS = "15"
npm run snap
```

***REMOVED******REMOVED******REMOVED*** Problem: "Docker-Container läuft nicht"

```powershell
***REMOVED*** Status prüfen
docker compose ps

***REMOVED*** Logs ansehen
docker compose logs l3-guacamole

***REMOVED*** Neu starten
docker compose restart
```

---

***REMOVED******REMOVED*** 🎯 Workflow für L3-Masken-Analyse

***REMOVED******REMOVED******REMOVED*** 1. L3 starten & Maske öffnen

1. L3-Software auf Windows starten
2. Gewünschte Maske öffnen (z.B. Kundenstamm)
3. Maske vollständig laden lassen

***REMOVED******REMOVED******REMOVED*** 2. Screenshot erstellen

**Manuell:**
```powershell
cd l3-migration-toolkit/playwright-snap
npm run snap
```

**Automatisch:** Task Scheduler macht alle 5 Min einen Screenshot

***REMOVED******REMOVED******REMOVED*** 3. Screenshots organisieren

```powershell
***REMOVED*** Umbenennen nach Masken-Name
Move-Item screenshots/l3_2025-10-16....png screenshots/L3_Kundenstamm_001.png

***REMOVED*** Ordner-Struktur
mkdir screenshots/stammdaten
mkdir screenshots/verkauf
mkdir screenshots/einkauf
```

***REMOVED******REMOVED******REMOVED*** 4. Feldanalyse (manuell oder mit OCR)

Für jede Maske dokumentieren:
- Feldnamen (Labels)
- Feldtypen (Text, Dropdown, Date)
- Positionen
- Validierungen
- Buttons & Aktionen

***REMOVED******REMOVED******REMOVED*** 5. VALEO-Maske nachbauen

**ObjectPage-Konfiguration erstellen:**

```typescript
// Beispiel: L3 Kundenstamm → VALEO CRM Contact
const kundenStammConfig = {
  title: "Kundenstamm",
  fields: [
    { name: "nummer", label: "Kundennummer", type: "text", readonly: true },
    { name: "name1", label: "Name 1", type: "text", required: true },
    { name: "name2", label: "Name 2", type: "text" },
    { name: "strasse", label: "Straße", type: "text" },
    { name: "plz", label: "PLZ", type: "text", maxLength: 5 },
    { name: "ort", label: "Ort", type: "text" },
    // ... weitere Felder aus Screenshot
  ],
  actions: [
    { label: "Speichern", action: "save" },
    { label: "Löschen", action: "delete" },
  ]
}
```

---

***REMOVED******REMOVED*** 📁 Verzeichnisstruktur

```
l3-migration-toolkit/
├── docker-compose.yml          ***REMOVED*** Guacamole Stack
├── .env.example                ***REMOVED*** Umgebungsvariablen
├── SETUP.md                    ***REMOVED*** Diese Anleitung
├── run-screenshot.ps1          ***REMOVED*** PowerShell Runner
├── playwright-snap/
│   ├── package.json
│   ├── snap-single.js         ***REMOVED*** Einzelner Screenshot
│   └── (weitere Tools)
├── screenshots/               ***REMOVED*** Output
│   ├── stammdaten/
│   ├── verkauf/
│   ├── einkauf/
│   └── fibu/
└── shared/                    ***REMOVED*** Datenaustausch mit Webtop
```

---

***REMOVED******REMOVED*** 🎨 Webtop verwenden (Optional)

**URL:** http://localhost:3010

**Login:** 
- User: `valeo`
- Pass: `ValeoWebtop2024!` (aus .env)

**Verwendung:**
- Screenshots ansehen
- Bildbearbeitung (GIMP)
- Remmina für alternative RDP/VNC-Verbindung
- Dateimanager für Screenshot-Organisation

---

***REMOVED******REMOVED*** 📊 Erwartetes Ergebnis

Nach Setup sollten Sie:

1. ✅ Guacamole Web-UI sehen (http://localhost:8090/guacamole)
2. ✅ Login erfolgreich
3. ✅ L3-Windows-Verbindung sehen
4. ✅ L3-Desktop im Browser rendern
5. ✅ Screenshot per `npm run snap` erstellen können
6. ✅ Task Scheduler macht alle 5 Min automatisch Screenshots

**→ Perfekte Basis für L3→VALEO Migration!** 🎯

---

***REMOVED******REMOVED*** 🎯 Migration-Workflow

***REMOVED******REMOVED******REMOVED*** Phase 1: Masken dokumentieren (1-2 Wochen)

```powershell
***REMOVED*** L3 starten
***REMOVED*** Jede Maske öffnen
***REMOVED*** Screenshot machen (automatisch alle 5 Min)
***REMOVED*** → ~50-100 Screenshots erwarten
```

***REMOVED******REMOVED******REMOVED*** Phase 2: Feldmapping erstellen (1 Woche)

Für jede L3-Maske:
- Screenshot öffnen
- Felder auflisten
- Zu PostgreSQL-Spalten mappen
- VALEO-ObjectPage-Config schreiben

***REMOVED******REMOVED******REMOVED*** Phase 3: VALEO-Masken bauen (2-3 Wochen)

- ObjectPage-Komponenten erstellen
- Validierungen übernehmen
- Workflows nachbauen
- Tests durchführen

***REMOVED******REMOVED******REMOVED*** Phase 4: Datenimport (1 Woche)

- L3-Daten als CSV exportieren
- Import-Scripts ausführen
- Daten-Transformation
- Validierung

**Gesamt-Aufwand:** 5-7 Wochen

---

***REMOVED******REMOVED*** 📞 Support

**Guacamole-Logs:**
```powershell
docker compose logs -f l3-guacamole
```

**Playwright-Debug:**
```powershell
$env:DEBUG = "pw:api"
npm run snap
```

**Container neu starten:**
```powershell
docker compose restart
```

**Komplett neu aufsetzen:**
```powershell
docker compose down -v
docker compose up -d
***REMOVED*** DB-Init wiederholen (siehe Schritt 4)
```

---

***REMOVED******REMOVED*** ✨ Nächste Schritte

1. ✅ Dieses Setup durchführen
2. ✅ Erste L3-Maske im Browser öffnen
3. ✅ Test-Screenshot machen
4. ✅ Task Scheduler aktivieren
5. ⏳ 24h laufen lassen → ~300 Screenshots
6. ⏳ Screenshots analysieren
7. ⏳ VALEO-Masken nachbauen

---

**Status: READY TO DEPLOY** 🚀

