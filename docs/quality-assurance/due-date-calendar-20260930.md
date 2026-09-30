---
title: Faelligkeit plus 30 Kalendertage
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Korrektur und Zentralisierung von elf fehlerhaften Faelligkeitsberechnungen.
---

# Faelligkeit plus 30 Kalendertage

## Fehlerbild

Elf Buchungs- und Abrechnungspfade berechneten „in 30 Tagen“ mit
`replace(day=min(today.day + 30, 28))`. Das addiert keine Tage, sondern ersetzt
den Tag im selben Monat. Am 30. September entstand dadurch der 28. September,
also eine bereits vergangene Faelligkeit. Monats-, Jahres- und
Schaltjahrgrenzen waren generell falsch.

## Umsetzung

`business_date_after(days, from_date=...)` in `app/core/business_time.py`
addiert echte Kalendertage. Ohne explizites Startdatum verwendet der Helfer den
Geschaeftstag der konfigurierten Betriebszeitzone. Alle elf Aufrufer verwenden
nun `business_today()` fuer das Rechnungsdatum und `business_date_after(30)`
fuer die Faelligkeit.

Betroffen waren Sammelabrechnung, E-Rechnungsimport, ERS, Streckengeschaeft,
Zinsabrechnung, Dauerauftraege, Rechnungspruefung, Lieferschein-Fakturierung
sowie die Agrar- und Einkauf-Kompatibilitaetsdienste.

## Nachweis

- 25 fokussierte Tests bestanden, darunter Januar-, September-, Jahres- und
  Schaltjahrgrenzen sowie alle elf Aufrufer.
- Das alte `replace(day=min(... + 30, 28))`-Muster kommt unter `app/` nicht mehr vor.
- Der Business-Time-Ratchet sinkt von 244 auf 212 Stellen und bleibt gruen.

Die fachliche Annahme bleibt „30 Kalendertage“. Individuelle
Zahlungsbedingungen sind ein eigener Fachvertrag und werden durch diese
Fehlerkorrektur nicht vorweggenommen.
