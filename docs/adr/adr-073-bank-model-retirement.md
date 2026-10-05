---
title: ADR-073 Ein aktives Bankauszugsmodell
type: adr
audience: [architektur, entwickler, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-10-01
version: 1.0.0
---

# ADR-073 Ein aktives Bankauszugsmodell

**Status:** Proposed
**Datum:** 2026-10-01

## Kontext und Freigabe

INT-BANK-001 montierte vier Routen unter /api/v1/bank mit eigenem Speicher,
Parsern und DTOs. Substring-/Betragsmatching, float-Betraege, Datumsersatz und
getrennte Commitpfade konkurrierten mit dem sicheren FIBU-BNK-02-Vertrag.
Kein Frontend-Aufrufer der vier Alt-Routen wurde im aktuellen Code gefunden.
Read-only 2026-10-01: Entwicklungsdatenbank 8 alte Auszuege/8 Zeilen,
valeo_probe 0/0. Diese Zahlen sind keine Produktionsaussage.

Explizite User-Freigabe 2026-10-01: Entwicklungsphase, saemtliche Altlasten
duerfen entfernt werden. Daher kein neues Archiv oder Kompatibilitaetsadapter.
Die acht alten Auszuege werden nicht in echte Zahlungen umgedeutet.

## Entscheidung

Ein aktives Modell: domain_erp.bank_statements/bank_statement_lines, gebunden
an ein aktives eigenes Bankkonto. Import:
`POST /api/v1/finance/bank-statements/import` mit bank_account_id und format.
Zeilen: `GET /api/v1/finance/bank-statements/{statement_id}/lines`.
Zuordnung: `POST /api/v1/finance/payments/match/{payment_id}` und
`POST /api/v1/finance/payments/auto-match`. X-Tenant-ID bestimmt den Mandanten.
Der bestehende Payments-CSV-Einstieg verwendet denselben Speicher/Replayvertrag.

## Entfernung

Bank-Altmodul, Router-Montage, vier DTOs und ihre konkurrierenden Tests werden
entfernt. Alte URLs liefern 404; keine Redirects, IBAN-Kontoraten oder alten
Antwortformen. CAMT.08 wird dadurch nicht automatisch als CAMT.02 freigegeben.

Migration bank_legacy_retirement_20261001 loescht ausschliesslich
domain_finance.bank_statement_lines und domain_finance.bank_statements,
inklusive alter Entwicklungsdatensaetze. Kein CASCADE, keine OP-Aenderung,
keine automatische Neubuchung und keine neue Archivstruktur. Das kanonische
Modell muss vorhanden sein; unvollstaendige Altschemata oder unerwartete
Abhaengigkeiten brechen die Transaktion ab. Alte Migrationshistorie bleibt
reproduzierbar; eine Folgemigration entfernt deren Altmodell.

## Konsequenzen

Die Anwendung darf nur auf dem migrierten kanonischen Modell starten.
Development-Retirement ist bewusst irreversibel: Downgrade bricht explizit ab,
statt leere Altstrukturen oder erfundene Historie zu erzeugen. Falls ein
bewusstes Zuruecksetzen benoetigt wird, vorhandenen Backupstand wiederherstellen.
GitHub-CI und Deployment bleiben separate Abnahmen. Keine Produktionsfreigabe
aus der Entwicklungsfreigabe ableiten.

## Nachweise

[Retirement-Abnahme](../quality-assurance/bank-legacy-retirement-20261001.md),
ADR-003 Canonical Domain Model und Finance Domain Pack.
