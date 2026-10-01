---
title: ADR-074 Bankvergleich ohne Direktbuchung
type: adr
audience: [architektur, entwickler, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-10-01
version: 1.0.0
---

# ADR-074 Bankvergleich ohne Direktbuchung

**Status:** Proposed
**Datum:** 2026-10-01

## Kontext

Der Saldenvergleich schrieb direkt posted-Journale mit geratenen Konten
1000/1200, konnte ohne zwei Buchungszeilen fortfahren und markierte Bankzeilen
MATCHED ohne OP-Zuordnung. Fehler wurden pro Vorschlag verschluckt. Interne
Aufrufe liessen auto_book weg: dessen FastAPI-Query-Objekt war truthy.
Die Maske markierte anhand lokaler Textmuster oder Checkboxen zugeordnet,
ohne Backend-Nachweis. Die User-Freigabe erlaubt das Entfernen aller Altlasten
in der Entwicklungsphase; ein neuer Kompatibilitaetsadapter ist nicht noetig.

## Entscheidung

Den konkurrierenden Direktbuchungsweg vollstaendig entfernen. auto_book=true
explizit mit 409 ablehnen, vor Datenbankzugriff; Standardwert echtes False.
Abgleich meldet stets can_be_booked=false, keine Buchungsvorschlaege und
keine geratenen Gegenkonten. Ungeklaerte Zeilen bekommen INVESTIGATE.
Echte OP-Zuordnung bleibt im vorhandenen Payment-Matching-Vertrag, echte
Journalbuchung im vorhandenen Journalworkflow mit dessen Pruefungen.

Die vorhandene ObjectPage wird ausschliesslich vom unsicheren Altverhalten
bereinigt: keine lokale Zuordnung, keine Direktbuchungsaktion, Save prueft.
Kein Maskenredesign oder paralleler Renderer. Eine spaetere funktionale
Umstellung erfolgt durch ScreenDefinition/RenderPlan/UniversalMaskRuntime.

## Konsequenzen

Alte Direktbuchungsaufrufe muessen umgestellt werden; kein stiller Erfolg.
Bereits erzeugte Entwicklungs-Journale werden hier nicht pauschal geloescht:
Abhaengigkeiten und kanonische Journalform muessen zuerst nachvollzogen werden.
Dies ist keine Abnahme des Hauptbuchvergleichs: Konto-/Mandantenbindung,
fehlender expliziter GL-Link, doppelte Journalbetragsfelder, PARTIAL-Zaehler,
CSV-Saldonachweis und verschluckte Lesefehler sind offene Folgethemen.
Keine neue Datenbank, Migration oder Dockerinstanz.
