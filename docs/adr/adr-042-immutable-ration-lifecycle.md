---
title: ADR-042 Unveraenderliche Rationsversionen und expliziter Lebenszyklus
type: adr
audience: [architektur, fachlich, entwickler, qa]
owner: domain/agrar
status: accepted
last_reviewed: 2026-07-14
version: 1.0.0
---

# ADR-042 Unveraenderliche Rationsversionen und expliziter Lebenszyklus

## Status

Accepted, 2026-07-14.

## Kontext

Der bisherige Solver hielt Rationsvarianten nur im Browser. Ein Solver-Ergebnis
konnte dadurch ohne fachliche Freigabe als aktive Fuetterung erscheinen. Gruppen,
Versionen, Freigabegrund, Aktivierungszeitpunkt und Aenderungshistorie waren nicht
tenantweit nachvollziehbar.

## Entscheidung

Fuetterungsgruppen, Rationskoepfe und Rationsversionen werden serverseitig und
tenantisoliert gespeichert. Der Inhalts-Snapshot einer Version ist nach Anlage
unveraenderlich; fachliche Aenderungen erzeugen eine neue fortlaufende Version.
Nur der Lifecycle-Zustand ist veraenderlich und folgt dem Automaten:

```text
draft -> in_review -> approved -> scheduled -> active -> retired -> archived
                  \-> draft        \-> active
```

Rueckgabe zur Bearbeitung, Freigabe, Planung, Aktivierung und Archivierung werden
mit Akteur, Zeitpunkt, Grund und Delta auditiert. Aktivierung ist nur nach Freigabe
moeglich. Pro Tenant und Fuetterungsgruppe darf hoechstens eine Version aktiv sein;
eine neue Aktivierung setzt die bisher aktive Version auf `retired`.

Der Experten-Solver ist ein Entwurfswerkzeug. Er uebergibt einen fachlichen
Snapshot an den Lifecycle, aktiviert aber keine Ration selbst. Native Meridian-
Worklist und ObjectPage bilden Review und Statuswechsel ab. Das mobile
Fuetterungsprotokoll liest die aktive Ration vom Server und nutzt Browserdaten nur
als abwaertskompatiblen Offline-Fallback.

## Konsequenzen

- Entscheidungen und Fuetterungsbeginn sind reproduzierbar und auditierbar.
- Optimistische Statuspruefungen verhindern verlorene parallele Aenderungen.
- Zeitgesteuerte Aktivierungen laufen isoliert im Scheduler.
- Inhaltskorrekturen erfolgen immer als neue Version.
- Rollen fuer Lesen, Bearbeiten und Freigeben werden am API-Vertrag erzwungen.

## Verworfene Alternativen

- **Browserzustand als Source of Truth:** nicht tenantweit und nicht revisionsfest.
- **Ueberschreibbare Rationszeilen:** historische Berechnungen waeren nicht mehr
  reproduzierbar.
- **Freigabe nur als UI-Schritt:** kann durch direkte API-Aufrufe umgangen werden.

