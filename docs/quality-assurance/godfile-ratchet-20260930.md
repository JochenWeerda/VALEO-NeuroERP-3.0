---
title: Pfadbezogener Godfile-Ratchet
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Exakte, nur sinkende Baseline fuer Python-Endpunkte ueber 1.000 Zeilen.
---

# Pfadbezogener Godfile-Ratchet

## Befund

Der Quality-Gate erlaubte global 12 Endpunktdateien ueber 1.000 Zeilen, obwohl
der eingecheckte Stand 15 enthielt. Damit war der Check dauerhaft rot und alle
nachfolgenden Backend-Pruefungen blieben unsichtbar. Eine reine Anhebung auf 15
haette Verschiebungen und Wachstum vorhandener Grossdateien nicht erkannt.

## Vertrag

`config/godfile_baseline.json` inventarisiert die 15 betroffenen Pfade mit ihrer
exakten Zeilenzahl. `scripts/check_file_size.py` blockiert nun:

- eine neue oder verschobene Datei ueber 1.000 Zeilen,
- jede weitere Zeile in einem vorhandenen Godfile,
- eine veraltete Baseline nach einer Verkleinerung oder Zerlegung.

Damit muss jeder Abbau im selben Commit in der Baseline sichtbar werden. Die
Option `--update-baseline` erzeugt den aktuellen, sortierten Bestand. Der alte
Parameter `--threshold` bleibt als klar markierte Kompatibilitaetsoption
lesbar, steuert den Gate-Vertrag aber nicht mehr.

## Nachweis

- `pytest tests/test_file_size_gate.py -q --no-cov`: 5 bestanden.
- Gate gegen den eingecheckten Endpunktstand: 15/15, Exit 0.
- Der parallele Arbeitsbaum wird korrekt rot: `crm_360.py` ist dort mit 1.235
  Zeilen ein neues Godfile und gehoert dem laufenden CRM-Slice.

Die drei kleinsten Abbaukandidaten sind `logistics_tours.py` (1.033),
`admin_suite.py` (1.038) und `einkauf_bestellvorschlag.py` (1.058). Ihre
Zerlegung bleibt eigenstaendige Facharbeit; die Ratsche verhindert bis dahin
weitere Verschlechterung.
