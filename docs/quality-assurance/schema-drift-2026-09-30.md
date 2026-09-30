---
title: Schema-Abgleich — 881 Abweichungen zwischen Dev-Datenbank und Migrationsstand
type: reference
audience: [entwickler, agent, betrieb, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Was der erste Lauf von check_schema_drift.py ergab, wie die Funde eingeordnet sind, und welche Maßnahme je Gruppe folgt.
---

# Schema-Abgleich

## Das Ergebnis in einem Satz

**Die Entwicklungsdatenbank ist nie das gewesen, was die Migrationen
beschreiben.** `scripts/check_schema_drift.py` stellt `valeo_neuro_erp` dem
frisch migrierten Stand gegenüber und findet **881 Abweichungen**.

| Befund | Anzahl | bedeutet |
|---|---|---|
| **fehlt** | 484 | der Migrationsstand hat es, die Dev-Datenbank nicht |
| **anders** | 213 | beide haben es, aber verschieden |
| **zusätzlich** | 184 | die Dev-Datenbank hat es, keine Migration legt es an |

Nach Art:

| Art | fehlt | zusätzlich | anders |
|---|---|---|---|
| Index | 219 | 55 | — |
| Spalte | 77 | 28 | 213 |
| Fremdschlüssel | 62 | 23 | — |
| CHECK | 57 | 1 | — |
| Tabelle | 46 | 74 | — |
| UNIQUE | 23 | 3 | — |

## Erst geprüft, dann berichtet

Eine Liste von 881 Funden ist nur so gut wie ihr Werkzeug. Vier Stichproben,
je eine pro Art, wurden von Hand in beiden Datenbanken nachgezählt:

| Stichprobe | dev | probe |
|---|---|---|
| Index `(schlag_id, datum)` auf `domain_agrar.feldbuch_massnahmen` | 0 | 1 |
| `attestations_approved_by_fkey` | 0 | 1 |
| Spalte `domain_agrar.feeding_actual_measures.version` | 0 | 1 |
| Tabelle `crm_subdomains.ai_assist_requests` | 0 | 1 |

Alle vier bestätigt. Der Vergleich erfindet nichts.

## Die Einordnung je Gruppe

Ein Fund ist keine Fehlermeldung, sondern eine Frage mit drei möglichen
Antworten. 881 einzeln zu beantworten wäre Beschäftigung; entscheidend ist die
Gruppe, und innerhalb der Gruppe die Stellen, die der Code wirklich benutzt.

### (b) 484 „fehlt" — die Dev-Datenbank ist verbastelt

Was im Migrationsstand steht und in der Dev-Datenbank fehlt, kann keine
fehlende Migration sein: Die Migration **gibt es**, sie ist auf dieser
Datenbank nur nie vollständig angekommen. 219 Indizes, 62 Fremdschlüssel, 57
Prüfbedingungen, 46 Tabellen, 23 UNIQUE-Bedingungen und 77 Spalten.

**Maßnahme: keine Migration.** Eine Migration würde eine Störung der
Entwicklungsumgebung in jede Installation tragen. Der Weg ist, die
Dev-Datenbank neu aufzusetzen:

```bash
python scripts/pruefstand_db.py          # der Prüfstand, immer frisch
# und für die Entwicklungsdatenbank, wenn die Daten nicht gebraucht werden:
#   dropdb valeo_neuro_erp && createdb valeo_neuro_erp && alembic upgrade head
```

Die Entscheidung, ob die gewachsenen Daten erhalten bleiben müssen, gehört dem
Haus. Solange sie erhalten bleiben, gilt: **Schema frisch prüfen, Daten
gewachsen** (`pruefstand-datenbank.md`).

### (a) 76 „zusätzlich" mit Codebezug — die Migration fehlt wirklich

102 zusätzliche Tabellen und Spalten wurden gegen den Code geprüft: Wird der
Name in `app/` oder `modules/` erwähnt? **76 ja.** Diese existieren nur auf
diesem Rechner, und der Code greift darauf zu — auf einer frischen
Installation läuft er ins Leere.

Das deckt sich mit dem, was die Tabellen-Ratsche
(`scripts/check_table_references.py`) am 29.09. unabhängig davon fand. Zwei
Werkzeuge, dieselbe Menge:

`domain_crm.contacts`, `domain_crm.crm_customers`, `domain_crm.crm_activities`,
`domain_crm.crm_contacts`, `domain_crm.crm_visit_reports`,
`domain_compliance.whistleblower_reports`, `domain_einkauf.ers_invoices`,
`domain_einkauf.ers_suppliers`, `domain_finance.ebilanz_exports`,
`domain_futtermittel.feed_raw_materials`, `.feed_recipes`,
`.raw_material_analyses`, `.recipe_ingredients`,
`domain_inventory.article_alternative_eans`, `.article_analyses`,
`.article_print_settings`, `.article_units`, `.nawaro_area_sheet_rows`,
`.nawaro_contract_sheet_rows`, `.nawaro_raps_balances`,
`.nawaro_raps_certificates`, `domain_pos.payment_methods`,
`domain_pos.promotions`, `domain_shared.process_projection_cursors`,
`.process_projection_registry` — und 51 weitere.

**Maßnahme: Migration schreiben, je Fachdomäne durch den Owner.** Genau so
entstanden am 29.09. `verkauf_fehlende_spalten_20260929` (fünf Spalten in
Angebot und Auftrag) und `lieferschein_status_bedingung_20260929`. Die Funde
liegen in CRM, Einkauf, Finanzen, Futtermittel, Lager, POS und Shared — also
in fremden Slices. **Handshake, nicht selbst reparieren:** Welche Form die
Tabelle haben soll, weiß der Owner; ein Nachbau aus dem lokalen Stand würde
einen gewachsenen Zufall zur Migration erheben.

Die vollständige Liste:

```bash
python scripts/check_schema_drift.py --json > drift.json
```

### (c) 26 „zusätzlich" ohne Codebezug — dokumentieren, nicht löschen

26 zusätzliche Tabellen und Spalten werden nirgends im Code erwähnt.
**Maßnahme: dokumentieren, nicht still löschen.** Ein stilles `DROP` verliert
Daten, deren Zweck niemand mehr kennt; und die Prüfung „wird der Name im Code
erwähnt" ist eine Heuristik, kein Beweis — ein Name kann auch dynamisch
zusammengesetzt werden.

### (b) 213 „anders" — vor allem gelockerte Bedingungen

| unterscheidet sich | Anzahl |
|---|---|
| nur Nullbarkeit | 64 (davon **31 in dev gelockert**) |
| nur Länge | 56 |
| nur Typ | 21 |
| Länge + Nullbarkeit | 17 |
| Nullbarkeit + Typ | 14 |
| Länge + Skala | 14 |
| übrige Kombinationen | 27 |

Die **31 gelockerten NOT-NULL-Regeln** sind genau das Muster vom 29.09.: Die
Dev-Datenbank verlangt nicht, was eine frische verlangt, und Testfixtures ohne
Pflichtfelder laufen deshalb lokal grün und in CI gegen einen 500er.

Die **21 reinen Typunterschiede** sind die unangenehmsten: Wo eine Spalte
lokal `text` und im Migrationsstand `varchar(50)` ist, schreibt der Code
lokal Werte, die eine frische Installation abweist. Sie gehören einzeln
angesehen — ebenfalls je Fachdomäne.

## Was das Skript nicht tut

Es läuft **nicht in CI** und hat **keine Ratsche.** Der Abstand zwischen einer
gewachsenen und einer frischen Datenbank ist eine Bestandsaufnahme, keine
Regressionsschwelle: Er hängt davon ab, auf welchem Rechner man ihn misst. Eine
Ratsche darauf würde den Rechner messen, nicht die Anwendung — derselbe Fehler,
der die Tabellen-Ratsche auf einen nie erfüllbaren Wert gesetzt hatte.

Was **wohl** in CI gehört, ist die Gegenprobe aus der anderen Richtung: ob der
Code Tabellen liest, die es im Migrationsstand nicht gibt. Das prüft
`scripts/check_table_references.py` mit einer Ratsche, und die läuft dort
schon.

## Aufruf

```bash
export TEST_DATABASE_URL=postgresql://…/valeo_probe
python scripts/pruefstand_db.py             # die Referenz muss frisch sein
python scripts/check_schema_drift.py        # DATABASE_URL gegen TEST_DATABASE_URL
python scripts/check_schema_drift.py --schema domain_crm domain_sales
python scripts/check_schema_drift.py --json
```

Verglichen werden Tabellen, Spalten (Typ, Länge, Skala, Nullbarkeit),
Fremdschlüssel, CHECK- und UNIQUE-Bedingungen und Indizes. Bewusst **nicht**
verglichen wird der Vorgabewert einer Spalte: Er unterscheidet sich zwischen
Ständen auch dann, wenn beide richtig sind (`nextval` mit verschiedenen
Sequenznamen), und ändert am Vertrag der Spalte nichts. Bedingungen und Indizes
werden über ihre **Definition** verglichen, nicht über den Namen — ein
automatisch erzeugter Name wie `customers_pkey1` ist kein Unterschied.

Fehlt eine ganze Tabelle, sind ihre Spalten kein eigener Fund. Sonst wäre eine
fehlende Tabelle mit dreißig Spalten lauter als alles andere.
