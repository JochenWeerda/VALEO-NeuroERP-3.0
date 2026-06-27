---
title: Benutzerhandbuch
type: explanation
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# Benutzerhandbuch

Aufgabenorientierte Anleitungen fuer die taegliche Arbeit, gegliedert nach
Fachdomaene statt nach technischer Menuestruktur. Jede Anleitung folgt dem
Muster: Ziel, Voraussetzungen, Schritte, Ergebnis und haeufige Fehler.

## Bereiche

- [**Einstieg**](einstieg.md) - Anmeldung, Mandantenwahl, Navigation.
- [**Dashboard und Workflows**](dashboard-workflows.md) - Leitstand, Flow Spine, Freigaben, Prozessüberwachung, KI-Copilot. (35 Masken).
- [**Wissensbasis und Kundenportal**](wissensbasis-kundenportal.md) - Interne Wissensdatenbank und externes Kundenportal. (20 Masken).
- [**Ernteannahme und Waage**](annahme.md) - LKW, Waage, Qualität, Hofliste, Wiegung. (19 Masken).
- [**Agrar-Kontrakte**](agrar-kontrakte.md) - Kontrakt, Fixierung, Erfüllung, Settlement. (23 Masken).
- [**Agrar-Warenwirtschaft**](agrar-warenwirtschaft.md) - PSM, Düngung, Saatgut, Feldbuch, Tierhaltung, Agrar-Stammdaten. (88 Masken).
- [**Verkauf (Auftrag bis Rechnung)**](verkauf.md) - O2C-Belegkette, Angebot, Auftrag, Lieferschein, Rechnung. (57 Masken).
- [**Einkauf und Beschaffung**](einkauf.md) - P2P, Bestellung, Wareneingang, Lieferantenbewertung, Bestell-Inbox. (78 Masken).
- [**Vertreter und Provisionen**](vertreter-provisionen.md) - Außendienst, Vertreterstamm, Provisionsabrechnung. (2 Masken).
- [**CRM und Marketing**](crm.md) - Kontakte, Leads, Kampagnen, DSGVO, KIM, Termine. (107 Masken).
- [**Preise und Kalkulation**](preise-kalkulation.md) - Preislisten, Kalkulation, Konditionen. (7 Masken).
- [**Artikel und Stammdaten**](artikel-stammdaten.md) - Artikelstamm, Chargen, Warengruppen, Etikettendruck. (18 Masken).
- [**Lager und Bestände**](lager.md) - Bestand, Bewegungen, Inventur, Silo, Verladung, Rückverfolgbarkeit. (33 Masken).
- [**Futtermittel und Produktion**](futtermittel-produktion.md) - Rezeptur, Produktionsauftrag, Chargen. (43 Masken).
- [**Qualitätssicherung**](qualitaetssicherung.md) - Proben, Labor, QS-Leitstand, Reklamation. (14 Masken).
- [**Compliance und Meldewesen**](compliance-meldewesen.md) - Register, Meldungen, GoBD, PCN/UFI, ESG, EUDR. (35 Masken).
- [**NaWaRo**](nawaro.md) - Verträge, Anbauflächen, Mitteilungen. (4 Masken).
- [**Streckengeschäft**](strecke-handelsgeschaeft.md) - Streckenhandel, Dokumente, Abrechnung. (12 Masken).
- [**Logistik und Touren**](logistik.md) - Disposition, Touren, Frachtbriefe, Fahrer. (16 Masken).
- [**Fuhrpark**](fuhrpark.md) - Fahrzeuge, Wartung, Kosten, Tankstelle. (14 Masken).
- [**Finanzbuchhaltung**](finanzbuchhaltung.md) - Hauptbuch, OP, Zahlungen, Abschluss, Bank, Mahnwesen, Schnittstellen. (121 Masken).
- [**Controlling und Kostenrechnung**](controlling-kostenrechnung.md) - Kostenstellen, Umlagen, Auswertungen. (7 Masken).
- [**POS und Kasse**](pos-kasse.md) - Bon, Zahlungsarten, Tagesabschluss. (17 Masken).
- [**Personal, Zeit und Lohn**](personal-lohn.md) - Zeiterfassung, Abwesenheit, Schichtplan, Lohnabrechnung. (18 Masken).
- [**Genossenschaft**](genossenschaft.md) - Mitglieder, Geschäftsanteile, Dividende. (2 Masken).
- [**Dokumente und Belegarchiv**](dokumente-belegarchiv.md) - DMS, Versand, Archivierung. (5 Masken).
- [**Reports und Analytics**](reports-analytics.md) - Standardreports, KPI-Dashboards, Statistik. (15 Masken).
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

**Aufnahme-Verfahren** (lokale Dev-/Docker-Umgebung):

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
    Die Kern-Masken sind als komprimierte WebP-Screenshots hinterlegt:
    Dashboard, Rohware-Annahme, Auftrags-Erfassung, Einkauf-Bestellungen,
    Bestandsuebersicht, Hauptbuch und CRM-Kontakte. Fuer die neu ergaenzten
    Randdomaenen ist das Handbuch textuell nutzbar; Screenshots koennen mit dem
    oben beschriebenen Verfahren nachgezogen werden.

## Quellen und Reverse-Pflege

- Bestehende Handbuchseiten unter `docs/benutzerhandbuch/`.
- MkDocs-Navigation in `mkdocs.yml`.
- Prozess-, Slice- und Workflow-Quellen sind auf den jeweiligen Unterseiten
  genannt.

Reverse-Pflege: Wenn neue Benutzerhandbuchseiten angelegt, umbenannt oder
archiviert werden, diese Startseite und `mkdocs.yml` im gleichen Slice
aktualisieren.
