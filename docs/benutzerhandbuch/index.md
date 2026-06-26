---
title: Benutzerhandbuch
type: explanation
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# Benutzerhandbuch

Aufgabenorientierte Anleitungen fuer die taegliche Arbeit, gegliedert nach
Fachdomaene statt nach technischer Menuestruktur. Jede Anleitung folgt dem
Muster: Ziel, Voraussetzungen, Schritte, Ergebnis und haeufige Fehler.

## Bereiche

- [**Einstieg**](einstieg.md) - Anmeldung, Mandantenwahl, Navigation, Tastatur.
- [**Annahme**](annahme.md) - LKW-Registrierung, Waage, Qualitaet, Ernteannahme.
- [**Agrar-Kontrakte**](agrar-kontrakte.md) - Kontrakt, Erfüllung, Fixierung, Settlement.
- [**Verkauf**](verkauf.md) - Auftrag, Lieferschein, Rechnung.
- [**Einkauf**](einkauf.md) - Bestellung, Wareneingang, 3-Wege-Match.
- [**Lager**](lager.md) - Bestand, Umlagerung, Inventur, Silo.
- [**Logistik und Touren**](logistik.md) - Tourplanung, Frachtbrief, ePOD.
- [**Futtermittel und Produktion**](futtermittel-produktion.md) - Einzelfutter, Rezept, Produktionsauftrag, Charge.
- [**Finanzbuchhaltung**](finanzbuchhaltung.md) - Offene Posten, Mahnwesen, Zahlungen.
- [**Controlling und Kostenrechnung**](controlling-kostenrechnung.md) - Kostenstellen, BAB, Umlagen, Abschluss.
- [**POS und Kasse**](pos-kasse.md) - Bon, Zahlungsarten, TSE, Tagesabschluss.
- [**Personal, Zeit und Lohn**](personal-lohn.md) - Zeiterfassung, Abwesenheit, Payroll, Lohn-Connector.
- [**CRM**](crm.md) - Kontakte, Leads, Aktivitaeten.
- [**Qualitaetssicherung**](qualitaetssicherung.md) - Proben, Labor, Charge, Reklamation.
- [**Compliance und Meldewesen**](compliance-meldewesen.md) - Register, Jobs, PCN/UFI, UStVA.
- [**NaWaRo**](nawaro.md) - Verträge, Anbauflächen, Mitteilungen, Streckenprüfung.
- [**Genossenschaft**](genossenschaft.md) - Mitglieder, Geschäftsanteile.
- [**Dokumente und Belegarchiv**](dokumente-belegarchiv.md) - QM-Dokumente, Versand, Archiv.
- [**Release Notes**](release-notes.md) - Anwenderrelevante Aenderungen.
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
