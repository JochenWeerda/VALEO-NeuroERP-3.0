---
title: Claude Code Teilauftrag Journal-Source
type: how-to
audience: [agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-09-10
version: 1.0.0
description: Abgegrenzter Parallelauftrag zur Journal-Leseregression mit Dateibesitz und Abnahme.
---

# Auftrag fuer Claude Code

Arbeite im Repository `C:/Users/Jochen/VALEO-NeuroERP-3.0` parallel zu Codex.
Lies AGENTS.md und die vorgeschriebenen Einstiegsdokumente. Claim zuerst
den offenen Workboard-Slice `L3-JOURNAL-SOURCE-20260910` mit eigenem Namen
und separatem Claim-Commit. Codex ist Lead und bearbeitet andere Live-Fehler.

## Befund und Ziel

Der aktuelle API-Sweep vom 2026-09-10 liefert bei
`GET /api/v1/journal-entries/` HTTP 500. Die Fehlermeldung nennt die
`JournalEntry.source`-Validierung: erlaubt sind nur `manual`, `system`,
`integration`, `import`, `cash_close`; mindestens eine vorhandene Quelle
wird abgelehnt. Der lokale Bericht liegt unter
`artifacts/runtime-sweep-2026-09-10.json`.

Ermittle die tatsaechliche Herkunft im Leseweg und die bereits vorhandenen
Schreiber. Beispiele im Code sind `delivery_note`, `sales_invoice`,
`ap_invoice_kernel` und `agrar_settlement`; diese Liste ist kein vollstaendiger
oder ungeprueft zu uebernehmender Sollvertrag. Behebe die Ursache so, dass
die Journal-Liste vorhandene fachliche Herkunft unveraendert lesen kann und
ungueltige Schreibeingaben weiterhin abgewiesen werden.

Keine Datenkorrektur, keine Umdeutung historischer Herkunft, keine leere
Liste als Fehlerersatz und kein blosses Entfernen der Validierung ohne
belegten Lese-/Schreibvertrag.

## Besitz und Zusammenarbeit

Dein Besitz: `app/api/v1/schemas/finance.py`, bei Bedarf
`app/api/v1/endpoints/journal_entries.py`, neue Datei
`tests/test_journal_source_contract.py`, eigener Workboard-Abschnitt,
eigene Slice-YAML und dieser Bericht. Bestehende Services und Migrationen
nur lesen; Erweiterungen des Besitzes zuerst im Workboard abstimmen.

Codex behaelt Docker, API-Sweep, Bereitschaft, CRM, Reportberechtigungen,
Policy-Backup, Mask-Builder und die vorbereitete Reparaturmigration.
Keine Container-Neustarts: Bedarf im Workboard melden, Codex integriert.

## Abnahme und Lieferung

Fokussierte Tests fuer reale fachliche Quellen und ungueltige Schreibeingaben;
bestehende `tests/test_journal_entries.py` und
`tests/test_journal_entries_api.py` ausfuehren. Reale Journal-Liste mit
HTTP 200 nachweisen oder den fuer den Live-Nachweis erforderlichen Neustart
an Codex melden. Testdaten und Details ohne personenbezogene Inhalte.

Geteilter Working Tree: eigene Aenderungen im HEAD-Worktree isolieren und
ueber `update-index` uebernehmen. Kein `git add -A`, kein `git commit --only`,
kein Rebase/Autostash fremden WIPs. Nach jeder geprueften Welle committen
und nach `origin/main` pushen. Workboard als Nachrichtenboard verwenden:
Status, Dateibesitz-Erweiterungen, SHA, Testergebnisse und Restbefunde dort
eintragen. Zum Abschluss diesen Bericht um deine Nachweise ergaenzen.
