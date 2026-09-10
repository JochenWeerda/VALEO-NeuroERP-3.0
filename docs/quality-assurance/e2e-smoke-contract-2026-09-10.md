---
title: E2E Smoke Vertragsreparatur
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-10
version: 1.0.0
description: Ursachen und Nachweise der Inventory- und Finance-Smoke-Reparatur.
---

# E2E Smoke Vertragsreparatur

## Belegte Ursachen

GitHub-Lauf 34470538019, Commit `fde08d92c`: Inventory erwartete die Zahl
1000, erhielt aber den korrekten Decimal-JSON-String `"1000.0"`.
Die Assertion prueft jetzt den exakten Dezimalwert als Text mit optionalen
Null-Nachkommastellen; ein falscher Betrag oder ein anderer JSON-Typ scheitert.

Finance erhielt HTTP 500: `eskaliere_mahnstufe` liefert fuer die Stufen
1 bis 3 Integer, `MahnstufeOut` verlangt Strings. Ein Before-Validator
ueberfuehrt ausschliesslich Integer zu Text; gespeicherte String-Werte,
INKASSO und der initiale Nullwert bleiben erhalten. Service-Logik und
historische Daten bleiben unveraendert.

## Staerkere Abnahme

Der Mahnstufen-Smoke verwendet eine eindeutige Rechnungsreferenz je Lauf
und prueft viermal HTTP 201, aktuelle und vorherige Stufe, die Sperre nach
INKASSO (422) sowie vier Eintraege im Audit-Trail. Der bisherige breite
Erfolg fuer 201/422/503 entfaellt bei diesem Test. Fuenf Regressionstests
fuehren die echte Service-Logik mit einem DB-Double durch FastAPI-Response-
Validierung. Keine zusaetzlichen Skips oder gelockerten Fehlercodes.

## Stand

Claim `44481ee09`. 35 Backend-Regressionstests bestanden; Slice-Readiness
und Agent-Handbuch-Driftcheck bestanden. Lokaler kombinierter Smoke-Lauf:
19 bestanden, ein bestehender bedingter UI-Skip, drei Finance-Verbindungsabbrueche
waehrend des Backend-Neustarts. Nach bestaetigtem HTTP 200 auf `/readyz`
bestanden alle drei Finance-Lifecycle-Tests im gezielten Wiederholungslauf.
Inventory-Lifecycle einschliesslich Decimal-Assertion bestand bereits im
kombinierten Lauf. Keine neuen Skips. GitHub-Gesamtlauf nach Push noch offen.
