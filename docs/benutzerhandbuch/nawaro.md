---
title: NaWaRo-Meldungen
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.2.0
---

# NaWaRo-Meldungen

Nachwachsende Rohstoffe (NaWaRo) erfordern Vertrags-, Flächen- und Liefermeldungen
gegenüber Behörden und Partnern. Diese Anleitung beschreibt den operativen Ablauf
im ERP.

!!! warning "Externe Meldepflicht"
    Fachliche Freigabe der Meldung gegenüber Behörde/Verbund bleibt eine externe
    Gate — das ERP stellt Daten, Vorschau und Export bereit.

## Voraussetzungen

- Modul **NaWaRo** ist freigeschaltet.
- Verträge, Anbauflächen und Lieferanten-/Mitgliederstammdaten sind gepflegt.
- Erntekampagne und Erntefenster sind konfiguriert.

## Verträge und Anbauflächen pflegen

1. Öffnen Sie *Agrar* → *NaWaRo* → *Verträge*.
2. Prüfen Sie Vertragspartner, Kultur, Fläche und Kampagnenbezug.
3. Öffnen Sie *Anbauflächen* und gleichen Sie Flächen mit Schlag-/Mitgliedsdaten ab.
4. Ergänzen Sie fehlende Raps-Profile oder Sonderkulturen in *Raps-Profil*.

## Mitteilung vorbereiten und drucken

1. Öffnen Sie *NaWaRo* → *Mitteilung drucken*.
2. Wählen Sie Kampagne, Vertrag und Meldezeitraum.
3. Prüfen Sie Mengen, Flächen und Parteidaten in der Vorschau.
4. Exportieren oder drucken Sie die Mitteilung (CSV/HTML je nach Maske).
5. Archivieren Sie den Export im Belegarchiv.

## Streckengeschäft und Übersichten

1. Für Streckenlieferungen: *Logistik/Strecke* → *NaWaRo-Verträge prüfen*.
2. Öffnen Sie *NaWaRo-Übersicht* für aggregierte Liefer- und Vertragsstände.
3. Drucken Sie Ernterklärung oder Übersicht für interne Freigabe.
4. Klären Sie Abweichungen zwischen Vertrag, Lieferung und Annahme vor der Meldung.

## Ergebnis

- Verträge, Flächen und Lieferungen sind für NaWaRo-Meldungen konsistent.
- Mitteilungen lassen sich nachvollziehbar exportieren und archivieren.
- Strecken- und Annahmedaten sind vor Behördenmeldung abgestimmt.

## Häufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Mitteilung leer | Keine Verträge/Flächen zur Kampagne | Stammdaten und Kampagne prüfen |
| Fläche stimmt nicht | Schlagkartei nicht synchron | Anbauflächen und Feldbuch abgleichen |
| Liefermenge abweichend | Annahme nicht zugeordnet | Annahme/Vertrag verknüpfen |
| Export blockiert | Pflichtfelder fehlen | Vorschau-Hinweise ausfüllen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: NaWaRo-Menü.
- `packages/frontend-web/src/lib/nawaro-communication.ts`: Export/Vorschau-Helfer.
- `docs/agent-ops/slices/TAIL-NAWARO-001.yaml`: Dubletten-/Export-Verifikation.
- `docs/benutzerhandbuch/annahme.md`: Lieferbezug Ernteannahme.

Reverse-Pflege: Bei neuen NaWaRo-Meldefeldern, Exportformaten oder
Strecken-Prüfregeln diese Seite und `nawaro-communication.ts` gemeinsam pflegen.
