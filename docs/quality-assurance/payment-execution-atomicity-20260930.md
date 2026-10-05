---
title: Atomare Ausführung von Kreditoren-Zahlungsläufen
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Korrektur von Teilzahlungsstatus, internen Commits und verschluckten Fehlern.
---

# Zahlungslauf: Transaktionsvertrag

Claim: `52a4b317e`, Slice `PAYMENT-EXECUTION-ATOMICITY-20260930`.
Die Fehlerhistorie zu stillen Fallbacks, toten PostgreSQL-Transaktionen und
widersprüchlichen Belegketten ist in konkrete Abnahmetests umgesetzt.

## Verhalten

- Ein Lauf wird mandantengebunden vor dem Lesen gesperrt. Wiederholung und
  parallele Ausführung können denselben Lauf nicht zweimal ausziffern.
- Anzahl, Summe und Status der mandantengebundenen Positionen müssen zum
  freigegebenen Kopf passen. Ein fremder Kinddatensatz wird nicht ausgeführt.
- Ein Kreditoren-OP wird nur bei ausreichendem Restbetrag reduziert. Fehlender,
  fremder oder Debitoren-OP sowie widersprüchliche Rechnungsreferenzen führen
  zu 409 und vollständigem Rollback.
- Nur ein vollständig ausgeglichener OP setzt einen vorhandenen AP-Beleg auf
  BEZAHLT. Ein Rechnungsnummernfeld allein genügt nicht; Teilzahlungen lassen
  den Belegstatus bestehen. Fremde oder stornierte vorhandene Vollausgleichs-
  Belege blockieren den Lauf.
- Zahlungslauf, Positionen, OP und aktualisierter vorhandener Beleg gehören
  zu einer Transaktion. `DocumentRepository.save_document(commit=False)`
  speichert ohne eigenen Commit; alle bisherigen Aufrufer behalten ihren
  Standard `commit=True`. Kein Prozessspeicher-Fallback im Zahlungslauf.
- Listen- und Einzelabruf melden Datenbankfehler mit 500 und Rollback,
  statt eine leere Erfolgsliste oder SQL-Details zurückzugeben.
- Die Antwort wird vor dem einzigen Commit gelesen. SQL-, Beleg- und
  Antwort-Lesefehler rollen alle Schreibvorgänge zurück; HTTP 500 enthält
  keine Datenbankdetails.

## Nachweis

Eigene Datenbank `valeo_test_payment_01a0f3fc_20260930`, frisch aus leerem
Schema bis `lastschrift_mandant_20260930` migriert. Keine Rücksetzung von
`valeo_probe` oder der Entwicklungsdatenbank. Tests erstellen eindeutig
zugehörige Datensätze und entfernen ausschließlich diese Datensätze.

- **26 grün:** 17 reale PostgreSQL-Transaktions-/Parallel-/Integritätstests
  plus neun bestehende Zahlungslauf-/Belegtests.
- **45 grün:** bestehende Zahlungslauf-, Beleg- und Wave-1-Verträge.
- Kontrolllauf mit dem alten Zahlungslauf: zehn der ersten elf neuen Tests
  reproduzieren die Fehler, einer prüft unverändertes Repository-Verhalten.
- SQL-Bind-Casts, Pagination und Baseline-Integrität grün; Compile und
  Diff-Whitespace-Prüfung sowie Ruff für die neuen Tests grün.
  Dead-Transaction-Inventur sinkt von 78 auf 76; die alte globale Schwelle
  78 hat noch Spielraum und benötigt einen eigenen strengeren Folgeclaim. Log: `artifacts/payment-execution-tests.log`.

## Grenzen und Handshake

Das bestehende Fachmodell bleibt erhalten: Ausführung erzeugt SEPA und
reserviert/settelt die zugeordneten Posten; externe Bankannahme wird dadurch
nicht behauptet. Importierte OP ohne Dokument in `documents` bleiben erlaubt;
Legacy-Belege ohne Tenantkennung benötigen weiterhin eine gesonderte
Datenmigration. Skonto-/Buchungs-/Rückläuferprozesse und externe Bankfreigabe
sind eigenständige Abnahmen, keine durch diese Tests geschlossenen Gaps.

Die projektweite Godfile-Ratsche findet während paralleler Arbeit
`crm_360.py` neu über 1000 Zeilen und `mask_frontend_bridges.py` über seiner
Baseline. Beide liegen außerhalb dieses Claims; keine Baseline-Anhebung und
keine Übernahme fremder Dateien. Eine lokale grüne Teilprüfung ist kein
projektweiter grüner CI-Nachweis.
