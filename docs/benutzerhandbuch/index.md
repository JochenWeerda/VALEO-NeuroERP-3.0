---
title: Benutzerhandbuch
type: explanation
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-01
version: 3.2.0
---

# Benutzerhandbuch

Aufgabenorientierte Anleitungen fuer die taegliche Arbeit, gegliedert nach
Fachdomaene statt nach technischer Menuestruktur. Jede Anleitung folgt dem
Muster: Ziel, Voraussetzungen, Schritte, Ergebnis und haeufige Fehler.

## Bereiche

- [**Einstieg**](einstieg.md) - Anmeldung, Mandantenwahl, Navigation.
- [**Dashboard und Workflows**](dashboard-workflows.md) - Leitstand, Flow Spine, Freigaben, Prozessüberwachung, KI-Copilot. (35 Masken).
- [**Masken-Plattform (Universal Mask Runtime)**](masken-plattform.md) - Einheitliche Detailmasken, Sort/Filter, Rollout-Piloten, Agenten-Modus. (1 Masken).
- [**Moderne Bedienung**](moderne-bedienung.md) - Omnibox/Kommandoleiste (Strg+K), Rollen-Workspaces, Sprach-Eingabe/Diktat, persoenliche Ansichten, Prozessband, Notizen, Planungskalender, Leitstand-Belegungsplan, ESG-Kachel.
- [**Wissensbasis und Kundenportal**](wissensbasis-kundenportal.md) - Interne Wissensdatenbank und externes Kundenportal. (20 Masken).
- [**Ernteannahme und Waage**](annahme.md) - LKW, Waage, Qualität, Hofliste, Wiegung. (19 Masken).
- [**Agrar-Kontrakte**](agrar-kontrakte.md) - Kontrakt, Fixierung, Erfüllung, Settlement. (20 Masken).
- [**Agrar-Warenwirtschaft**](agrar-warenwirtschaft.md) - PSM, Düngung, Saatgut, Feldbuch, Tierhaltung, Agrar-Stammdaten. (91 Masken).
- [**Verkauf (Auftrag bis Rechnung)**](verkauf.md) - O2C-Belegkette, Angebot, Auftrag, Lieferschein, Rechnung. (57 Masken).
- [**Einkauf und Beschaffung**](einkauf.md) - P2P, Bestellung, Wareneingang, Lieferantenbewertung, Bestell-Inbox. (82 Masken).
- [**Vertreter und Provisionen**](vertreter-provisionen.md) - Außendienst, Vertreterstamm, Provisionsabrechnung. (2 Masken).
- [**CRM und Marketing**](crm.md) - Kontakte, Leads, Kampagnen, DSGVO, KIM, Termine. (91 Masken).
- [**Preise und Kalkulation**](preise-kalkulation.md) - Preislisten, Kalkulation, Konditionen. (7 Masken).
- [**Artikel und Stammdaten**](artikel-stammdaten.md) - Artikelstamm, Chargen, Warengruppen, Etikettendruck. (18 Masken).
- [**Lager und Bestände**](lager.md) - Bestand, Bewegungen, Inventur, Silo, Verladung, Rückverfolgbarkeit. (34 Masken).
- [**Futtermittel und Produktion**](futtermittel-produktion.md) - Rezeptur, Produktionsauftrag, Chargen. (43 Masken).
- [**Qualitätssicherung**](qualitaetssicherung.md) - Proben, Labor, QS-Leitstand, Reklamation. (14 Masken).
- [**Compliance und Meldewesen**](compliance-meldewesen.md) - Register, Meldungen, GoBD, PCN/UFI, ESG, EUDR. (35 Masken).
- [**NaWaRo**](nawaro.md) - Verträge, Anbauflächen, Mitteilungen. (4 Masken).
- [**Streckengeschäft**](strecke-handelsgeschaeft.md) - Streckenhandel, Dokumente, Abrechnung. (12 Masken).
- [**Logistik und Touren**](logistik.md) - Disposition, Touren, Frachtbriefe, Fahrer. (16 Masken).
- [**Fuhrpark**](fuhrpark.md) - Fahrzeuge, Wartung, Kosten, Tankstelle. (14 Masken).
- [**Finanzbuchhaltung**](finanzbuchhaltung.md) - Hauptbuch, OP, Zahlungen, Abschluss, Bank, Mahnwesen, Schnittstellen. (122 Masken).
- [**Controlling und Kostenrechnung**](controlling-kostenrechnung.md) - Kostenstellen, Umlagen, Auswertungen. (7 Masken).
- [**POS und Kasse**](pos-kasse.md) - Bon, Zahlungsarten, Tagesabschluss. (17 Masken).
- [**Personal, Zeit und Lohn**](personal-lohn.md) - Zeiterfassung, Abwesenheit, Schichtplan, Lohnabrechnung. (19 Masken).
- [**Genossenschaft**](genossenschaft.md) - Mitglieder, Geschäftsanteile, Dividende. (2 Masken).
- [**Dokumente und Belegarchiv**](dokumente-belegarchiv.md) - DMS, Versand, Archivierung. (5 Masken).
- [**Reports und Analytics**](reports-analytics.md) - Standardreports, KPI-Dashboards, Statistik. (7 Masken).
- [**Service und Support**](service-support.md) - Servicefälle, Projekte, Schäden, Wartung, Versicherungen, Energie. (24 Masken).
- [**Release Notes**](release-notes.md) - Anwenderrelevante Änderungen.
- [**Glossar**](glossar.md) - Fachbegriffe Landhandel/Agrar.
- [**In-App-Hilfe**](in-app-hilfe.md) - kontextsensitive Deep-Links.

## Screenshots

Screenshots liegen als **WebP** unter `benutzerhandbuch/img/` und werden so
eingebunden:

```markdown
![Dashboard](img/einstieg-dashboard.webp)
```

**Automatische Vollaufnahme** (~830 Endnutzer-Routen aus `route-inventory.gen.json`):

```bash
# Terminal 1 — Backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend mit Universal-Mask-Flags
cd packages/frontend-web
set VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true
set VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true
set VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER=true
set VITE_ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT=true
pnpm run dev -- --host 127.0.0.1 --port 3001

# Terminal 3 — Playwright-Screenshots (Desktop 1440×900)
set PLAYWRIGHT_SKIP_WEBSERVER=1
set FRONTEND_BASE_URL=http://127.0.0.1:3001
pnpm run handbuch:screenshots

# WebP komprimieren + Handbuch neu generieren (Repo-Root)
python scripts/handbuch_screenshot_qc.py process
python scripts/handbuch_screenshot_qc.py review-html
python scripts/compress_screenshots.py
python scripts/generate_benutzerhandbuch_full.py
```

**Sichtkontrolle:** `docs/benutzerhandbuch/screenshot-review.html` im Browser öffnen.
Nur `approval=approved` wird ins Handbuch eingebunden. Freigabe z. B.:

```bash
python scripts/handbuch_screenshot_qc.py approve --slug einkauf__bestellungen
python scripts/handbuch_screenshot_qc.py approve --all-pending
```

**Zuschnitt:** Playwright erfasst nur den Masken-Kern (`main`, ObjectPage, Native Runtime) —
kein Sidebar-/Header-Chrome. `process` trimmt zusätzlich weiße Ränder.

Dateiname-Schema: Route `einkauf/bestellungen` → `img/einkauf__bestellungen.webp`.
Manifest: `docs/benutzerhandbuch/screenshot-manifest.json`.

**Manuelles Verfahren** (Einzelmasken):

1. Frontend oeffnen (Docker: `valeo-neuro-erp-frontend`, Port 3000).
2. Dev-Session aktivieren: Im Browser `localStorage.setItem('access_token','dev-token')`
   setzen und neu laden. Der `AuthService` erzeugt damit einen Mock-Admin und
   umgeht den OIDC-Login (siehe `src/lib/auth.ts`); das Backend akzeptiert den
   Wert aus `API_DEV_TOKEN`.
3. Zielmaske oeffnen, dem ersten Aufruf genuegend Zeit geben (Vite kompiliert
   Lazy-Chunks on-demand, bis etwa 20 Sekunden), dann Screenshot erstellen.
4. Rohbild (PNG) als `img/<bereich>-<maske>.png` ablegen und mit
   `python scripts/compress_screenshots.py` zu WebP komprimieren
   (ersetzt die PNG, etwa 60 bis 80 Prozent kleiner, Text bleibt scharf).
5. WebP-Bild in der jeweiligen How-to einbinden.

!!! note "Aktueller Stand"
    Automatisierte Screenshot-Pipeline für alle App-Routen:
    `tests/e2e/handbuch-screenshots.spec.ts` + `scripts/generate_benutzerhandbuch_full.py`.
    Legacy-Kernscreenshots (Dashboard, Rohware-Annahme, …) bleiben unter den
    bisherigen Dateinamen erhalten; neue Masken nutzen das `__`-Pfadschema.

## Quellen und Reverse-Pflege

- Bestehende Handbuchseiten unter `docs/benutzerhandbuch/`.
- MkDocs-Navigation in `mkdocs.yml`.
- Prozess-, Slice- und Workflow-Quellen sind auf den jeweiligen Unterseiten
  genannt.

Reverse-Pflege: Wenn neue Benutzerhandbuchseiten angelegt, umbenannt oder
archiviert werden, diese Startseite und `mkdocs.yml` im gleichen Slice
aktualisieren.
