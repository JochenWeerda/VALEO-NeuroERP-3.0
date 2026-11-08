---
title: Scheduler PR43 - gezielte Integration
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-25
---

# Scheduler-Schemaimport

Quelle PR43, Commit bbd7d577a026f5f178627ca292e05aba8793ee49. Genau Schema und neuer Regressionstest wurden gegen den Integrations-HEAD und die vorhandene Arbeitsansicht konfliktgeprueft und uebernommen. Keine Paketmanifeste oder Lockfiles aus dem gestapelten PR42 blind uebernommen; der bereits gepruefte DND-Vertrag bleibt erhalten.

Die drei zusammengesetzten Indizes sind innerhalb des runs-Tabellencallbacks definiert. Namen und Spalten bleiben identisch. Keine Verbraucher der bisherigen einzelnen Exporte im PR belegt; der Integrationsstand erhaelt keine konkurrierenden Exporte.

Lokale Abnahme mit vorhandener Installation: Vitest4.1.12, db-schema.test.ts 1/1 bestanden. Der Test importiert das echte Schema und prueft Namen und Spalten der drei Indizes. Keine Datenbank, Migration oder Container angelegt. Claudes berichtete 24/9-Paketsuite und identische Typfehler wurden hier nicht erneut als eigene Vollabnahme ausgegeben.

GitHub: PR43 Docs Build und Docs Governance success. Der vom Autor berichtete Quality-Gate-Nachweis40222509662 betrifft den gestapelten Basisstand; kein neuer Gesamtlauf nach Integration behauptet. PR42-Abhaengigkeitsintegration und Claudes Folgeauftrag zu Migrationen/Seeds/HR bleiben getrennt offen.
