---
title: Einheitlicher sicherer Bank- und Zahlungsabgleich
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-10-01
---

# Bank- und Zahlungsabgleich

Claims cbd92693a und c6e48664b. Der vorherige manuelle Pfad nahm eine volle
Zahlung an, ohne Bankzeile zu lesen. Der Auto-Pfad schloss Rechnungen anhand
des verbrauchten Zahlungsbetrags statt des OP-Rests. Fresh-Schema-Vertraege
zeigten zusaetzlich eine nicht migrierte op_betrag-Spalte. Zwei neue Vertraege
waren vor Umsetzung rot (501 und SQL-Fehler); Log artifacts/bank-matching-before.log.

## Gemeinsamer Vertrag

Import mit auto_match, POST /payments/match/{payment_id} und
POST /payments/auto-match nutzen dieselben internen Funktionen im bestehenden
payment_matching-Modul. Keine neuen Routes, Services, Container oder Tabellen:
Minor-Bugfix vorhandener Finance-Operationen. C4/Indexzuordnung bleibt Finance.

- Tenant aus bestehender X-Tenant-ID-Dependency; tenant_id-Queryparameter
  ueberschreiben den Header nicht. Der vorhandene Frontend-apiClient setzt
  diesen Header bereits fuer alle drei Bedienwege.
- Reale Bankzeile und ihr tenantgleicher Auszug sind Voraussetzung jeder Zuordnung.
  Richtung: positiver Eingang zu Debitoren, negativer Ausgang zu Kreditoren.
  Waehrung muss exakt stimmen; keine FX-Umrechnung oder Cent-Toleranz.
- Automatik verwendet vollstaendige, exakte Belegreferenzen, maximal zwei
  Kandidaten und maximal 100 Bankzeilen pro Aufruf. Mehrdeutigkeit, fehlende
  Referenz und Ueberzahlung bleiben unzugeordnet. Keine Buchung durch blosse
  Namens-/Betragsschaetzung. Weitere Zeilen koennen im naechsten Batch folgen.
- Tenantbezogene Transaktionssperre und Zeilensperren schuetzen parallele
  Zuordnungen. Guard-Updates mit RETURNING verhindern stille Nulltreffer.
- Die ganze Bankzeile wird einem OP zugeordnet. Teilzahlung reduziert den
  OP-Rest exakt; op_status ist teilweise, die Bankzeile MATCHED, weil deren
  ganzer Betrag verwendet wurde. MatchResult.match_type ist dann PARTIAL;
  remaining_amount bezeichnet den unverbrauchten Zahlungsbetrag (hier null),
  nicht den OP-Rest. Ueberzahlungen werden nicht ohne Restbetragsmodell verteilt.
- BEZAHLT erst bei OP-Rest null. Vorhandene Dokumente werden gesperrt und
  ihre Tenantkennung muss eindeutig stimmen; fehlende/fremde Kennungen und
  stornierte/gutgeschriebene Belege verhindern die Auszifferung. Importierte OP
  ohne Dokument im Store bleiben moeglich. Kein In-Memory-Fallback.
- Bankzeile, OP, Beleg und hashverketteter Pruefnachweis teilen einen Commit.
  Jeder Fehler rollt zurueck, auch Audit- oder Commitfehler. Wiederholung
  derselben Zuordnung ist idempotent; Umlenkung auf einen anderen OP ist 409.
- Auditwerte enthalten Dezimalbetraege als Strings. Der Akteur kommt aus den
  vom Sicherheitslayer verifizierten token_claims; ohne sub ist die Ausfuehrung
  ausdruecklich System. Ein unpruefbarer X-User-ID-Header wird nicht uebernommen.

Die voruebergehende 501-Sperre des Import-Meilensteins ist damit ersetzt.
Bestehende Matching-Lesewege verwenden die migrierte betrag-Spalte.

## Abnahme

30 neue Matching-Vertraege, 12 Kontoauszugsimport-, 10 Zahlungs-CSV- und
17 Zahlungslauf-Vertraege: **69 bestanden** (14,89 s). Reales PostgreSQL auf
dem vorhandenen valeo_probe, eigene Testdaten, keine neue DB/Dockerinstanz,
kein Reset und keine Migration. Log artifacts/bank-matching-tests.log.

Zusaetzlich der regulaere Lauf mit den damals 24 Matching-Vertraegen und
13 bestehenden DQ-/Ausfallvertraegen: **37 bestanden** (46,13 s).
Die 13 bestehenden Vertraege sind zusaetzliche Tests; insgesamt **82 verschiedene
Vertraege** bestanden. Log artifacts/bank-matching-regression.log.

Nachgewiesen: volle/teilweise Zahlung, Debitor/Kreditor, fehlende Bankzeile,
Waehrung/Vorzeichen/Ueberzahlung, Mehrdeutigkeit/Referenzpraefix, Fremdmandant,
fremde/fehlende Belegkennung, Storno/Gutschrift, Guard gegen Umlenkung,
Batch-Wiederholung und zwei echte parallele Aufrufe derselben Bankzeile.
Echte PostgreSQL-Fehler bei OP-, Bankzeilen-, Dokument- und Auditschreiben
sowie Commitfehler lassen keine Teilwirkungen zurueck. Der Auditnachweis
ist hashverkettet und entsteht bei Wiederholung nicht erneut.

Ruff und Diff-Whitespace gruen. Agent-Handbuch: fuenf Artefakte aktuell.
Baseline-Integritaet gegen cbd92693a gruen. Eigene unbeschraenkte Importabfrage
abgebaut und nur deren Baselineeintrag entfernt; neue Batch-/Kandidatabfragen
sind in SQL und beim Fetch begrenzt. Keine Baseline angehoben.

## Offene Grenzen

Projektweite Gates sind nicht insgesamt gruen: Pagination hat aktive fremde
POS-/Webhook-Funde, Godfile meldet CRM und Maskenbruecke, Architecture-Index
hat Drift im parallelen Arbeitsstand. C4 und Containerinventar sind aktuell.
Keine fremde Baseline/Datei fuer einen scheinbar gruenen Gesamtstand umgeschrieben.
OpenAPI-Tenantparameter aendern sich; der aktive OPENAPI-DRIFT-REFRESH-Owner
muss die Spezifikation aus dem integrierten Stand generieren.

Bestehende Identitaets-/Rollenmiddleware wird konsumiert, nicht neu bewiesen.
Bankkonto-/IBAN-Bindung, Importdatei-Idempotenz ueber mehrere neue Auszuege,
CAMT-/MT940-Parserdetails, Rueckbuchung und GL-Journalintegration sind separate
Fachvertraege. Derselbe bereits gespeicherte Zahlungssatz ist wiederholbar;
der erneute Upload derselben Datei erzeugt weiterhin einen neuen Auszug.
Legacy-PARTIAL-Zuordnungen ohne gespeicherten Verteilbetrag werden nicht
blind weiterverrechnet. GitHub-CI/Deployment bleiben externe Abnahmen.
