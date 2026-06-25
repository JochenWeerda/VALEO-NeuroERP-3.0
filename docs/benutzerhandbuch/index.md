---
title: Benutzerhandbuch
type: explanation
audience: [endnutzer, power-user]
owner: Cursor
status: entwurf
last_reviewed: 2026-06-25
version: 3.0.0
---

# Benutzerhandbuch

Aufgabenorientierte Anleitungen für die tägliche Arbeit — gegliedert nach
Fachdomäne, nicht nach Menüstruktur. Jede Anleitung folgt dem Muster: Ziel →
Voraussetzungen → Schritte → Ergebnis → häufige Fehler.

## Bereiche

- [**Einstieg**](einstieg.md) — Anmeldung, Mandantenwahl, Navigation, Tastatur.
- [**Annahme**](annahme.md) — LKW-Registrierung, Waage, Qualität, Ernteannahme.
- [**Verkauf**](verkauf.md) — Auftrag → Lieferschein → Rechnung.
- [**Lager**](lager.md) — Bestand, Umlagerung, Inventur, Silo.
- [**Finanzbuchhaltung**](finanzbuchhaltung.md) — Offene Posten, Mahnwesen, Zahlungen.
- [**Glossar**](glossar.md) — Fachbegriffe Landhandel/Agrar.
- [**In-App-Hilfe**](in-app-hilfe.md) — kontextsensitive Deep-Links.

> Einkauf und CRM folgen als weitere How-tos.

## Screenshots

Screenshots liegen unter `benutzerhandbuch/img/` und werden so eingebunden:

```markdown
![Anmeldemaske](img/einstieg-login.png)
```

**Aufnahme-Verfahren** (erfordert eine laufende, **angemeldete** Oberfläche):

1. Frontend starten/öffnen (Docker: `valeo-neuro-erp-frontend`, Port 3000) und
   mit gültigen Zugangsdaten anmelden.
2. Zielmaske öffnen und Screenshot erstellen (Browser/UI-Explorer).
3. Bild als `img/<bereich>-<maske>.png` ablegen und in der jeweiligen How-to
   einbinden.

!!! note "Status"
    Automatisierte Screenshot-Aufnahme ist vorbereitet, aber noch offen: Die
    Oberfläche benötigt eine authentifizierte Session (OIDC). Sobald
    Test-Zugangsdaten (`NEUROERP_USER` / `NEUROERP_PASS`) bereitstehen, können
    die Bilder per Browser-Automation erzeugt und hier abgelegt werden.
