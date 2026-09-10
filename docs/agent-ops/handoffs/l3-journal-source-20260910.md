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

## Nachweise Claude Code (2026-09-10)

**Ursache.** Der Whitelist-Validator `validate_source` sass auf
`JournalEntryBase`. Diese Basisklasse wird von `JournalEntryCreate`
(Schreibweg) *und* von `JournalEntry` geerbt, dem Response-Model der
Journal-Liste. Damit galt eine Schreibregel auf dem Leseweg. Da
`list_journal_entries` die `ValidationError` im generischen
`except Exception` faengt, liess eine einzige gespeicherte Buchung mit nicht
gelisteter Herkunft die gesamte Liste mit HTTP 500 fehlschlagen.

**Abgelehnter Wert.** `produktion_mischfutter`, geschrieben von
`app/api/v1/endpoints/produktion_mischfutter.py` ueber
`FinanceTransactionService.create(source=...)`. In den Daten am 2026-09-10:
`manual` 362, `produktion_mischfutter` 5, `reversal` 1, `sales_invoice` 1,
`bulk_import` 1.

**Erhobener Schreibvertrag.** Die im Auftrag genannten Beispiele haben sich nur
teilweise bestaetigt: `sales_invoice` und `ap_invoice_kernel` existieren,
`delivery_note` und `agrar_settlement` als `source`-Wert nicht — der
Lieferschein-Pfad schreibt `sales_invoice`. Belegt sind 17 Herkuenfte, jede mit
Fundstelle in `JOURNAL_ENTRY_WRITE_SOURCES` hinterlegt:
`accrual_provision`, `ap_invoice_kernel`, `bank_reconciliation`,
`booking_template`, `bulk_import`, `cash_close`, `connector`, `import`,
`integration`, `manual`, `op_settlement`, `POS`, `produktion_mischfutter`,
`reversal`, `sales_credit_note`, `sales_invoice`, `system`. Die alte Whitelist
deckte 12 davon nicht ab. `system`, `integration` und `import` haben keinen
Schreiber im Code, bleiben aber als Bestandsvertrag zulaessig; sie zu
entfernen waere eine Verschaerfung und gehoert in eine eigene Entscheidung.

**Loesung.** Schreib- und Lesevertrag getrennt. Der Validator sitzt jetzt auf
`JournalEntryCreate` und weist unbelegte Eingaben weiterhin ab (Meldung
unveraendert, `tests/test_journal_entries.py::test_invalid_source_rejected`
bleibt gruen). `JournalEntry` deklariert `source` als
`Optional[str]` ohne Pruefung und reicht gespeicherte Herkunft unveraendert
durch; die Spalte ist nullable und wird von `storage_fees`,
`finance_closing_service` und `inventory_operations` gar nicht geschrieben.
Keine Datenkorrektur, keine Umdeutung, kein Entfernen der Validierung.

**Verifikation.** In-Process-Lauf der echten Route gegen die echte Datenbank:

| Mandant | vorher | nachher |
|---|---|---|
| `00000000-0000-0000-0000-000000000001` (Sweep) | 500 | **200**, 7 Buchungen, Herkunft unveraendert |
| `test-tenant` | 200 | 200, 363 Buchungen |
| `system` | 500 | 500 — andere Ursache, siehe Restbefund 1 |

Zusaetzlich alle 370 gespeicherten Buchungen einzeln durch das Lesemodell
validiert. Gegenprobe auf die uebrigen Pflichtfelder (`posting_date`,
`entry_number`, `description`, `entry_date`, Betraege, `status`, `tenant_id`):
keine NULL-, Laengen- oder Reihenfolgeverletzung.

**Tests.** 37 neue Vertragstests in `tests/test_journal_source_contract.py`
(Leseweg inkl. NULL, unbekanntem Wert und Strukturschutz gegen erneute
Vererbung; Schreibweg inkl. abgewiesener Eingaben; Vertragsdeckung), ohne
Datenbank und ohne Netzwerk. 34 Bestandstests aus
`tests/test_journal_entries.py` und `tests/test_journal_entries_api.py` gruen.
621 Tests im Bereich `finance|journal|booking|accrual|open_item` gruen.

**Commits.** `ec310b565` (Claim), `b7316ba6d` (Fix + Tests), beide nach
`origin/main` gepusht; Doku-Commit folgt. Isoliert ueber HEAD-Blob und
`update-index` beim Workboard, kein `git add -A`, kein Rebase; fremder WIP
unangetastet.

**Offen — Live-Nachweis.** Der laufende Worker antwortet weiterhin mit der
alten Whitelist-Meldung. Die Aenderung ist reiner Code ohne Migration und
wirkt erst nach Neustart. Neustart bitte durch Codex.

**Offen — zwei Restbefunde ausserhalb meines Dateibesitzes.**

1. Mandant `system` liefert weiterhin HTTP 500: zwei Zeilen in
   `domain_erp.journal_entry_lines` (Buchung `IMP-AUDIT-001`) haben
   `tenant_id NULL`, waehrend `JournalEntryLine` `tenant_id` als Pflichtfeld
   fuehrt. Das ist ein Mandantenisolations- und Datenbefund. Ich habe das
   Lesemodell hier bewusst *nicht* aufgeweicht: eine tolerante `tenant_id`
   wuerde eine Mandantengrenze verwaessern statt einen Datenfehler zu melden.
2. `app/services/pos_compat_service.py` schreibt `journal_entry_lines` ohne
   `tenant_id` und ohne `account_id` und erzeugt denselben Defekt neu.
