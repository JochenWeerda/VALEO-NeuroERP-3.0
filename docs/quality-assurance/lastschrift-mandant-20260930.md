---
title: Lastschriften — eine Einzugsermächtigung gehört einem Haus
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Warum domain_shared.direct_debit_items ohne tenant_id angelegt wurde, was ein fremdes Haus damit lesen und auslösen konnte, und warum sepa_ready wahr war, wenn kein Mandat existierte.
---

# Lastschriften

## Der Befund in einem Satz

**`domain_shared.direct_debit_items` trug keinen Mandanten.** Getrennt waren die
Lastschriftläufe nur durch ihre `run_id`, und `direct_debits.py` nahm den
Mandanten entgegen, ohne ihn zu benutzen.

Was ein fremdes Haus damit konnte — alles über die reguläre API, ohne Kunstgriff:

| Weg | Wirkung |
|---|---|
| `GET /finance/direct-debits` | die Läufe **aller** Häuser, mit Anzahl und Gesamtbetrag |
| `GET /finance/direct-debits/{run_id}` | ein fremder Lauf im Einzelnen: Name, **IBAN**, BIC, Mandatsreferenz, Betrag |
| `POST …/{run_id}/export` | einen fremden Lauf auf `exported` setzen |
| `POST /mask-bridges/finance/direct-debits/{run_id}/approve` | einen fremden Lauf freigeben |
| `POST …/{run_id}/execute` | einen fremden Lauf **ausführen** |
| `DELETE …/{run_id}` | einen fremden Lauf stornieren |

Dass niemandem Geld abgebucht wurde, lag nicht an einer Prüfung, sondern daran,
dass der einzige Weg, der Lastschriften *sammelt*, ohnehin nicht lief (siehe
unten). Die Tabelle war in beiden Datenbanken leer.

## Zwei Hälften, die sich über dieselbe Tabelle widersprachen

Die Migration `mask_frontend_bridges_20260917` legte die Tabelle **ohne**
`tenant_id`, `debitor_id` und `currency` an. Die eine Hälfte des Codes richtete
sich danach, die andere nicht:

| Datei | nimmt an |
|---|---|
| `direct_debits.py`, `mask_frontend_bridges.py` | es gibt keinen Mandanten — filtert nur nach `run_id` |
| `finance_followup.py`, `finance_actions.py` | es gibt `tenant_id` **und** `debitor_id` — filtert seit immer danach |

Die zweite Hälfte scheiterte deshalb bei **jeder** Abfrage, still. Diese
Migration entscheidet den Widerspruch zugunsten des Lesepfads: Die Tabelle
bekommt die drei Spalten.

`tenant_id` ist `NOT NULL` — ohne Nachfüllen, weil die Tabelle am 30.09.2026 in
beiden Datenbanken leer war. Die Migration setzt die Bedingung in zwei Schritten
(anlegen, dann verschärfen): Auf einer Installation, auf der doch Zeilen liegen,
schlägt der zweite Schritt fehl und zeigt das an, statt die Zeilen einem
beliebigen Haus zuzuschlagen.

## `sepa_ready` war wahr, wenn kein Mandat existierte

```python
sepa_ready=(mandate_expired_count == 0 and debitor_count > 0)
```

Der Kommentar daneben sagte „alle Mandate gültig". Geprüft wurde nur, dass
keines **abgelaufen** ist — und das ist auch dann wahr, wenn es zu keinem
einzigen Debitor ein Mandat gibt. Dazu kam: Die Abfrage lag in einem `except`,
das jeden Fehler verschluckte, also blieben die Zähler auch bei einem
Datenbankfehler auf 0, und `sepa_ready` wurde wahr.

Jetzt heißt `sepa_ready`, was der Kommentar behauptet: Die Mandatsabfrage muss
**gelaufen** sein, der Lauf muss Debitoren haben, keines der Mandate darf
abgelaufen sein, **und** jeder Debitor muss ein gültiges Mandat haben. Gezählt
werden dabei Debitoren (`COUNT(DISTINCT debitor_id)`), nicht Mandatszeilen —
zwei Mandate für denselben Debitor sind ein Debitor mit Mandat, nicht zwei.

Ein nicht lesbarer Mandatsbestand ist jetzt ein 503, kein „bereit".

## Der Lastschriftenlauf lief überhaupt nicht

`POST /finance/direct-debit/run` ist der einzige Weg, der fällige offene Posten
zu Lastschriften macht. Er scheiterte an drei Stellen gleichzeitig:

1. `domain_shared.sepa_mandates` **existierte nirgends** — auch nicht in der
   gewachsenen Entwicklungsdatenbank. Der JOIN traf ins Leere.
2. Der `INSERT` nannte `mandate_ref`; die Spalte heißt `mandate_id`.
3. Er las `oi.debitor_id` aus `open_items`; der Debitor heißt dort `partner_id`.

Gemeldet wurde davon „Lastschriftenlauf fehlgeschlagen: …" oder — sobald der
erste Fehler behoben wäre — „Keine fälligen Posten mit gültigem SEPA-Mandat
gefunden." Beides sah nach einer leeren Lage aus, nicht nach einem Defekt.

Alle drei sind behoben; der Lauf sammelt jetzt.

## Handshake an den Finanz-Owner: das vollständige SEPA-Mandat fehlt

`domain_shared.sepa_mandates` ist in dieser Migration **minimal** — genau die
fünf Spalten, die der Code nennt: `tenant_id`, `debitor_id`,
`mandate_reference`, `mandate_valid`, `mandate_expired_at`. Sie sind nicht
erfunden, sondern übernommen.

Für eine echte **pain.008** reicht das nicht. Nicht festgelegt, weil es eine
Fachentscheidung ist:

- **Gläubiger-Identifikationsnummer** (Creditor Identifier) — heute nimmt
  `direct_debits.py` sie pro Lauf im Formular entgegen (`glaeubiger_id`) und
  speichert sie nirgends.
- **Sequenztyp** `FRST` / `RCUR` / `OOFF` / `FNAL` — dito (`sequenz_typ`), und
  er ist eine Eigenschaft des Mandats, nicht des Laufs.
- **Verfahren** `CORE` / `B2B` — dito (`sepa_schema`).
- **Unterschriftsdatum** und **IBAN des Zahlungspflichtigen** — die
  Einzugsermächtigung selbst; ohne beides ist eine Lastschrift nicht
  nachweisbar.
- **Aufbewahrung und Widerruf** — wie lange ein widerrufenes Mandat bleibt, und
  ob `mandate_valid = false` ein Widerruf oder ein Ablauf ist.

Vier dieser Angaben nimmt die Maske heute **pro Lauf** entgegen und verwirft sie.
Solange sie nicht am Mandat hängen, ist jeder Lauf eine Behauptung.

## Abnahme

16 Verträge in `tests/test_lastschrift_mandant_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Eigentümer | eine Lastschrift ohne `tenant_id` ist nicht speicherbar; `sepa_mandates` trägt den Mandanten |
| Lesen | ein fremder Lauf ist 404 und **kein Bankdatum steht in der Antwort**; der eigene bleibt lesbar; die Liste zeigt nur eigene Läufe |
| Bewegen | Export, Storno, Freigabe und Ausführung eines fremden Laufs bewegen nichts — geprüft **in der Tabelle**, nicht am Statuscode |
| Anlegen | ein angelegter Lauf gehört dem anlegenden Haus |
| `sepa_ready` | ohne Mandat falsch, mit gültigem wahr, mit abgelaufenem falsch, mit **fremdem** Mandat falsch |
| Lauf | sammelt fällige Posten mit Mandat; ohne Mandat sammelt er nichts |
| Störung | die Spalte, nach der gefiltert wird, wird kurzzeitig umbenannt: 503, nicht leere Liste |

```bash
export TEST_DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe
python scripts/pruefstand_db.py
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/test_lastschrift_mandant_vertrag.py -q
```

**Ergebnis 2026-09-30:** 16 Verträge grün gegen den frischen Stand. Dazu 39
vorhandene Tests aus `test_finance_actions.py`, `test_finance_followup_api.py`,
`test_mask_frontend_bridges.py` und `test_mask_bridge_field_contracts.py` grün.
In `test_finance_followup_api.py` musste ein Stub nachgezogen werden: Er erkannte
die Mandatsabfrage an ihrem alten Wortlaut `COUNT(*) FILTER (WHERE
mandate_valid = true)` und jetzt an der Tabelle.

## Nachgezogen: Tabellen-Ratsche 25 → 24 lebend

`domain_shared.sepa_mandates` stand an einem lebenden Weg und existierte nicht.
Mit dieser Migration ist sie da; die Schwelle sinkt entsprechend.

**Hinweis an den parallel arbeitenden CRM-Slice:** Im gemeinsamen Arbeitsbaum
misst die Ratsche derzeit 26 statt 24, weil das noch nicht eingecheckte
`crm_360.py` zwei Tabellen anspricht, die es im Migrationsstand nicht gibt
(`domain_crm.contacts`, `domain_crm.crm_customers`). Gemessen wurde für diese
Schwelle gegen den Stand **ohne** diese unfertigen Dateien. Sobald sie eingecheckt
werden, blockiert die Ratsche sie — zu Recht: Beide Tabellen stehen auf der Liste
der 76 Tabellen ohne Migration.
