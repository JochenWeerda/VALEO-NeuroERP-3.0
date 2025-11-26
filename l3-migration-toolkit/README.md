***REMOVED*** 🎯 L3 Migration Toolkit für VALEO-NeuroERP

**Automatische Screenshot-Erfassung von L3-Masken via Apache Guacamole**

---

***REMOVED******REMOVED*** 🚀 Quick Start (5 Minuten)

```powershell
***REMOVED*** 1. Verzeichnis
cd C:\Users\Jochen\VALEO-NeuroERP-3.0\l3-migration-toolkit

***REMOVED*** 2. .env erstellen
Copy-Item .env.example .env
***REMOVED*** → PASSWÖRTER ANPASSEN!

***REMOVED*** 3. Container starten
docker compose up -d

***REMOVED*** 4. Warten
Start-Sleep -Seconds 30

***REMOVED*** 5. DB initialisieren (EINMALIG!)
docker exec -i l3-guacamole /opt/guacamole/bin/initdb.sh --postgres | docker exec -i l3-postgres psql -U guacamole_user -d guacamole_db

***REMOVED*** 6. Guacamole neu starten
docker restart l3-guacamole

***REMOVED*** 7. Browser öffnen
Start-Process "http://localhost:8090/guacamole"
***REMOVED*** Login: guacadmin / guacadmin
***REMOVED*** → PASSWORT SOFORT ÄNDERN!

***REMOVED*** 8. RDP-Verbindung anlegen (siehe SETUP.md)

***REMOVED*** 9. Playwright installieren
cd playwright-snap
npm install
npm run install:pw

***REMOVED*** 10. Test-Screenshot
npm run snap
```

**Fertig!** ✅

---

***REMOVED******REMOVED*** 📁 Verzeichnisstruktur

```
l3-migration-toolkit/          ***REMOVED*** Isoliertes Verzeichnis
├── docker-compose.yml         ***REMOVED*** Guacamole Stack (IP: 172.25.0.0/24)
├── .env.example               ***REMOVED*** Umgebungsvariablen-Template
├── README.md                  ***REMOVED*** Diese Datei
├── SETUP.md                   ***REMOVED*** Detaillierte Anleitung
├── BEWERTUNG-GUACAMOLE-ANSATZ.md  ***REMOVED*** Technische Bewertung
├── run-screenshot.ps1         ***REMOVED*** PowerShell-Runner für Task Scheduler
├── playwright-snap/           ***REMOVED*** Screenshot-Automation
│   ├── package.json
│   ├── snap-single.js        ***REMOVED*** Einzelner Screenshot
│   └── (weitere Tools folgen)
├── screenshots/               ***REMOVED*** Screenshot-Output
│   ├── stammdaten/
│   ├── verkauf/
│   ├── einkauf/
│   └── fibu/
└── shared/                    ***REMOVED*** Datenaustausch mit Webtop
```

---

***REMOVED******REMOVED*** 🌐 Netzwerk-Isolation

**Eigener IP-Bereich:** `172.25.0.0/24`

| Service | IP | Host-Port | Container-Port |
|---------|-----|-----------|----------------|
| PostgreSQL | 172.25.0.10 | - | 5432 |
| Guacd | 172.25.0.11 | - | 4822 |
| Guacamole | 172.25.0.12 | **8090** | 8080 |
| Webtop | 172.25.0.13 | **3010** | 3000 |

**VALEO-NeuroERP (parallel):**
- Frontend: `localhost:3000`
- Backend: `localhost:8000`
- PostgreSQL: `localhost:5432`

**→ Komplett isoliert, keine Konflikte!** ✅

---

***REMOVED******REMOVED*** 📸 Screenshot-Automation

***REMOVED******REMOVED******REMOVED*** Manueller Screenshot

```powershell
cd playwright-snap

***REMOVED*** Umgebungsvariablen setzen
$env:GUAC_URL = "http://localhost:8090/guacamole"
$env:GUAC_USER = "guacadmin"
$env:GUAC_PASS = "DEIN_NEUES_PASSWORT"
$env:OUT_DIR = "../screenshots"
$env:WAIT_SECONDS = "10"

***REMOVED*** Screenshot erstellen
npm run snap
```

**Output:** `screenshots/l3_2025-10-16T21-30-00.png` + `.json`

***REMOVED******REMOVED******REMOVED*** Automatische Screenshots (Task Scheduler)

```powershell
***REMOVED*** Task anlegen
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
  -User "$env:USERNAME" `
  -RunLevel Highest
```

**Ergebnis:** Alle 5 Minuten ein Screenshot

---

***REMOVED******REMOVED*** 🎯 Workflow für Masken-Migration

***REMOVED******REMOVED******REMOVED*** 1. Screenshots sammeln (2 Wochen)

```
Woche 1-2:
├─ Tag 1-5:   Stammdaten-Masken (Kunden, Artikel, Lieferanten)
├─ Tag 6-10:  Verkaufs-Masken (Angebot, Auftrag, Rechnung)
└─ Tag 11-14: Einkauf & Fibu-Masken

Erwartung: 80-120 Screenshots
```

***REMOVED******REMOVED******REMOVED*** 2. Screenshots analysieren (1 Woche)

```
- Felder auflisten (Excel-Tabelle)
- Validierungen dokumentieren
- Workflows zeichnen
- Feldmapping erstellen (L3→VALEO)
```

***REMOVED******REMOVED******REMOVED*** 3. VALEO-Masken bauen (3-4 Wochen)

```typescript
// Pro L3-Maske → 1 VALEO ObjectPage-Config
const l3_mask_config = {
  fields: [...],  // Aus Screenshot extrahiert
  validation: {...},
  actions: [...]
}
```

***REMOVED******REMOVED******REMOVED*** 4. Import & Test (1 Woche)

```
- L3-Daten importieren
- VALEO-Masken mit echten Daten testen
- Funktionalität vergleichen
- Differenzen beheben
```

**Gesamt:** 7-8 Wochen für vollständige L3→VALEO Migration

---

***REMOVED******REMOVED*** 📊 Erwartetes Ergebnis

Nach 2 Wochen Screenshot-Phase:

```
screenshots/
├── stammdaten/
│   ├── L3_Kundenstamm.png
│   ├── L3_Artikelstamm.png
│   ├── L3_Lieferantenstamm.png
│   └── ... (15-20 Masken)
├── verkauf/
│   ├── L3_Angebot.png
│   ├── L3_Auftrag_Kopf.png
│   ├── L3_Auftrag_Positionen.png
│   ├── L3_Rechnung.png
│   └── ... (20-30 Masken)
├── einkauf/
│   ├── L3_Bestellung.png
│   ├── L3_Wareneingang.png
│   └── ... (10-15 Masken)
└── fibu/
    ├── L3_Buchungsjournal.png
    ├── L3_Debitor.png
    ├── L3_Kreditor.png
    └── ... (20-30 Masken)

GESAMT: 80-120 Screenshots
```

**Jeder Screenshot:**
- ✅ Pixelgenau
- ✅ Mit Timestamp
- ✅ Mit JSON-Metadaten
- ✅ Organisiert nach Modul

---

***REMOVED******REMOVED*** 🎨 Von L3 zu VALEO (Beispiel)

***REMOVED******REMOVED******REMOVED*** L3-Maske: Kundenstamm

**Screenshot zeigt:**
```
Felder (3 Spalten):
┌─────────────┬─────────────┬─────────────┐
│ Kundennr    │ Name 1      │ Telefon     │
│ Matchcode   │ Name 2      │ Telefax     │
│ Branche     │ Straße      │ E-Mail      │
│ Anrede      │ PLZ         │ Homepage    │
│             │ Ort         │             │
└─────────────┴─────────────┴─────────────┘

Buttons: [Speichern] [Löschen] [Drucken]
```

***REMOVED******REMOVED******REMOVED*** VALEO-Äquivalent

```typescript
// packages/frontend-web/src/pages/crm/kunde-stamm.tsx
const kundeStammConfig = {
  title: "Kundenstamm",
  sections: [
    {
      title: "Basisdaten",
      fields: [
        { name: "id", label: "Kundennummer", type: "text", readonly: true },
        { name: "matchcode", label: "Matchcode", type: "text" },
        { name: "company", label: "Firma", type: "text", required: true },
        { name: "contact_type", label: "Branche", type: "select" },
      ]
    },
    {
      title: "Adresse",
      fields: [
        { name: "street", label: "Straße", type: "text" },
        { name: "postal_code", label: "PLZ", type: "text", maxLength: 5 },
        { name: "city", label: "Ort", type: "text" },
      ]
    },
    {
      title: "Kontakt",
      fields: [
        { name: "phone", label: "Telefon", type: "tel" },
        { name: "fax", label: "Telefax", type: "tel" },
        { name: "email", label: "E-Mail", type: "email" },
        { name: "website", label: "Homepage", type: "url" },
      ]
    }
  ],
  actions: [
    { label: "Speichern", action: "save", variant: "default" },
    { label: "Löschen", action: "delete", variant: "destructive" },
    { label: "Drucken", action: "print", variant: "outline" },
  ]
}
```

**Ergebnis:**
- ✅ Gleiche Felder wie L3
- ✅ Bessere Gruppierung (3 Sections)
- ✅ Moderne UI (Tailwind, shadcn/ui)
- ✅ Responsive (mobile-friendly)
- ✅ Validierung (Pydantic + Zod)

---

***REMOVED******REMOVED*** 📞 Support & Troubleshooting

**Logs ansehen:**
```powershell
docker compose logs -f l3-guacamole
```

**Container neu starten:**
```powershell
docker compose restart
```

**Komplett neu aufsetzen:**
```powershell
docker compose down -v
docker compose up -d
***REMOVED*** DB-Init wiederholen
```

**Weitere Hilfe:** Siehe `SETUP.md` (Troubleshooting-Sektion)

---

***REMOVED******REMOVED*** ✨ Zusatz-Features (Coming Soon)

- [ ] **OCR-Integration** (Tesseract.js) - Automatische Feldextraktion
- [ ] **Batch-Screenshots** - Alle Masken in einem Durchlauf
- [ ] **Diff-Analyse** - Vergleich L3 ↔ VALEO
- [ ] **Field-Extractor** - Automatisches Feldmapping
- [ ] **Report-Generator** - PDF-Doku aller Masken

---

**Status: READY TO USE** 🎉  
**Isoliertes Netzwerk:** 172.25.0.0/24 ✅  
**Keine Konflikte mit VALEO-NeuroERP:** ✅

