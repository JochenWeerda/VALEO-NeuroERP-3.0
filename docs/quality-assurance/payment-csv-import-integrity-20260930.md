---
title: Wahrheitsgemäßer und atomarer CSV-Zahlungsimport
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
description: Positive Importverträge, Erhalt der Währung und reale SQL-Rollbacks.
---

# CSV-Zahlungsimport

Slice `PAYMENT-CSV-IMPORT-INTEGRITY-20260930`, Claim `2b5f9704f`.
Die Handshakes zu toten Transaktionen und falschen Importzählern werden
für `payment_matching.import_payments_csv` konkret geschlossen.

## Gefundene Fehler

1. **Jeder gültige Import wurde abgewiesen.** Die Duplikatprüfung schließt
   das aktuelle Objekt per Identität aus. Der Import baute stattdessen
   für die Prüfung eine neue Kopie und fand die ursprüngliche Zeile als
   vermeintliches Duplikat. Die alten Tests prüften nur ungültige Daten.
2. **Speicherfehler wurden übersprungen.** Kopf- und Zeilenfehler konnten
   die Transaktion vergiften; Antwort und Zähler stammten dann aus der
   Schleife und nicht aus gespeicherten Datensätzen.
3. **Währungen gingen verloren.** Gelesene USD/CHF/GBP-Beträge wurden
   als EUR gespeichert und ausgegeben, ohne Umrechnung.
4. **IDs kollidierten innerhalb einer Sekunde.** Uhrzeit und Bankpräfix
   ersetzten keine eindeutige Importkennung.
5. **Beträge wurden still gerundet.** NUMERIC(15,2) speicherte andere Werte
   als die ungerundete Antwort, wenn die Eingabe mehr Nachkommastellen hatte.

## Umsetzung und Entscheidungen

Die DQ-Prüfung erhält das vorhandene aktuelle Objekt aus dem Batch. Echte
Duplikate bleiben blockiert. Sämtliche Daten werden vor dem ersten Schreibzugriff
geprüft. Zulässige Währungen bleiben in SQL und Antwort erhalten; eine
unbekannte Währung wird beim persistierenden Zahlungsimport mit 422 blockiert.
Die bestehende PI-004-Warnung bleibt in allgemeinen DQ-Auswertungen unverändert.
Dies ist eine explizite strengere Importentscheidung: keine unterstützte
Währung vortäuschen und keine Warnung mangels Antwortfeld verlieren.

Beträge müssen endlich und ohne Rundung mit der Zweistelligkeit des
bestehenden Datenbankschemas darstellbar sein. UUIDv7 ersetzt die
Sekundenkennung. Kopf und alle Zeilen gehören zu einem Commit; jeder
Schreib-/Commitfehler führt zum vollständigen Rollback und einer generischen
500-Antwort ohne SQL-Details. Teilimporte werden nicht als Erfolg ausgegeben.

## Nachweis

Frisch migrierte PostgreSQL-Datenbank `valeo_test_payment_01a0f3fc_20260930`
auf `lastschrift_mandant_20260930`, keine Veränderung fremder Datensätze.

- Erster Red-Lauf: sechs Fehler; gültige Daten erreichten wegen Selbstduplikat
  noch keinen Schreibpfad.
- Nach isolierter DQ-Korrektur: acht Fehler reproduzieren Speicher-,
  Währungs-, Kennungs- und Rundungsprobleme.
- **10/10 PostgreSQL-/HTTP-Verträge grün**, einschließlich echter Fehler
  bei Kopf, zweiter Zeile, Commit und VARCHAR-Bedingung sowie positiver
  gespeicherter Währungswerte und zweier Importe bei gleicher Uhrzeit.
- Der Transaktionsscanner sinkt von 76 auf **75**; die Ratsche wird von
  ihrer historischen 78 auf den tatsächlichen Stand 75 gesenkt.
- **6/6 bestehende DQ-/Duplikatverträge grün** mit den regulären
  Test-Fixtures. Der erste isolierte Lauf ohne Auth-Fixture ergab 401
  beim fachfremden Bulk-HTTP-Test; es wurde kein Auth-Vertrag aufgeweicht.
- SQL-Bind-Casts, Compile, Diff-Whitespace und Ruff für neue Tests grün.

Logs: `artifacts/payment-csv-red.log`,
`artifacts/payment-csv-after-dq-red.log`, `artifacts/payment-csv-green.log`.

## Offene Folgearbeit

CAMT/MT940-Import, Bankstatement-Automatching und Belegausgleich besitzen
weitere bekannte Transaktions-/Mandanten-/Teilzahlungsrisiken. Dieser Slice
schließt deren separate Gaps nicht. Die 75 verbleibenden Scannerbefunde
brauchen Fachreparaturen und langfristig einen positionsbezogenen Schutz
statt einer alleinigen globalen Zahl. Aktive Fremdclaims bleiben unberührt.
