# Doppelwiegung auf dem kanonischen Wiegeschein (Slice WIEGUNG-KANONISCH-20261005)

Stand: 2026-10-05 · Welle 2, Slice 13

## Der Befund

Vier Tabellen für **einen** Begriff, und die, die der Doppelwiegungsweg benutzt,
existiert in keiner Datenbank:

| Tabelle | Spalten | Zeilen (Dev) | Wer schreibt/liest |
| --- | --- | --- | --- |
| `domain_inventory.weighing_tickets` | 28 | 49 | kanonisches Rückgrat, `supply_chain_trace_service` |
| `domain_agrar.weighing_tickets` | 10 | 0 | nur `waage_mobile.py` (Quittierung) |
| `domain_ops.ops_wiegungen` | 14 | 0 | `WaageRepository`/`WiegungRepository` (ORM-CRUD) |
| `domain_agrar.wiegungen` | — | **existiert nicht** | `waage.py` Doppelwiegung |

Diese Migration legt die fehlende Tabelle **nicht** an. Eine fünfte Wahrheit über
ein Wiegeergebnis wäre das Gegenteil von Rückverfolgbarkeit, und das kanonische
Rückgrat hat alle Felder, die der Weg braucht: Brutto, Tara, Netto, Kennzeichen,
Waage, Richtung, erste und zweite Wägung.

### Drei Fehler im Weg selbst

**1. `netto = abs(wiegung1 - wiegung2)`.** Der Absolutbetrag verdeckt den
Vorzeichenfehler. Eine Tara schwerer als das Brutto ist ein Messfehler oder eine
Verwechslung der beiden Eingaben — und wurde zu einem plausiblen positiven
Nettogewicht. Das Nettogewicht ist die abgerechnete Menge; hier wurde auf einem
Messfehler abgerechnet, und der Beleg sah einwandfrei aus.

Ein bestehender Test forderte das sogar ein:

```python
def test_dual_weighing_netto_computed_reverse():
    """Reihenfolge der Wiegungen darf kein negatives Netto erzeugen."""
    netto = abs(5000.0 - 32500.0)
    assert netto == pytest.approx(27500.0)
```

Die Reihenfolge *hat* eine fachliche Bedeutung. Deshalb heißen die Felder jetzt
`brutto_kg` und `tara_kg` statt `wiegung1`/`wiegung2`.

**2. Der JSONB-Rückfall.** Schlug der erste INSERT fehl und enthielt die
Fehlermeldung „column", „does not exist" oder „relation", schrieb der Weg die
ganze Wiegung als undurchsichtigen Klumpen in eine `extended_data`-Spalte — ohne
`netto_kg`, ohne `waage_id` — und antwortete `201 created`. Ein Wiegeschein,
dessen Gewicht in keiner Spalte steht, ist nicht abrechenbar und nicht prüfbar.
Der Rückfall ist entfallen.

**3. Kein `tenant_id`.** Weder beim Schreiben noch beim Lesen.
`get_wiegung_extended` hatte die Abhängigkeit nicht einmal: Jedes Haus konnte
jeden Wiegeschein lesen, wenn es die Kennung kannte.

### Und: drei Tests waren dauerhaft rot

`tests/test_dual_weighing_disposition.py` rief `create_dual_wiegung(payload, db)`
positionell auf und traf damit den Parameter `tenant_id`. Die drei Tests waren
rot, seit der Weg eine Mandantenabhängigkeit bekam. Der Weg war kaputt **und**
nur scheinbar geprüft.

## Was jetzt gilt

### Migration `wiegung_kanonisch_20261005`

Sechs Spalten auf `domain_inventory.weighing_tickets`: `gosse`, `muster_nr`,
`handwiegung`, `ident_nr`, `disposition_nr`, `charge_nr` — bisher lagen sie im
JSONB-Klumpen.

**Warum `handwiegung` eine Spalte ist.** Nach MessEG ist eine von Hand
eingetragene Masse keine geeichte Messung. Der Beleg muss sagen, was er ist. In
einem JSONB-Feld ist das nicht auswertbar — und genau dort stand es.

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_wiegung_netto_stimmt` | Ein Nettogewicht, das nicht Brutto minus Tara ist — die abgerechnete Menge muss der Messung entsprechen. |
| `ck_wiegung_tara_unter_brutto` | Eine Tara schwerer als das Brutto. |
| `ck_wiegung_gewichte_nicht_negativ` | Eine negative Masse. |
| `ck_wiegung_richtung` | Eine dritte Richtung, die die Rückverfolgbarkeit nicht kennt — die Wiegung fiele aus der Kette. |

Vor dem Anlegen zählt die Migration die Verstöße im Bestand und **bricht ab**,
wenn es welche gibt: Eine Bedingung zu überspringen, weil die Daten sie nicht
tragen, würde den Fehler dauerhaft verdecken. In beiden Datenbanken war der
Bestand sauber (49 Zeilen, 0 Verstöße in allen vier).

Das Downgrade baut die Spalten nur zurück, wenn nichts darin steht: Eine
Handwiegung oder eine Gosse ist Teil des Belegs.

### Der Weg

* `netto = brutto - tara`, ohne Absolutbetrag. `tara >= brutto` ist ein 422 mit
  dem Hinweis auf die wahrscheinliche Ursache („sind die beiden Wägungen
  vertauscht?").
* Ein ausgewiesenes Netto **ohne** zwei Wägungen ist erlaubt (Handwiegung,
  Fremdwaage) — dann gibt es keine zwei Messungen zum Nachrechnen. Ohne jedes
  Gewicht ist es ein 422: „Ohne Gewicht ist der Wiegeschein kein Beleg."
* `EL` → `in`, `VL` → `out`. Ein unbekannter Zielscheintyp ist ein 422 und kein
  stillschweigendes `in` — das hätte eine Verkaufslieferung als Zugang in die
  Rückverfolgbarkeit gestellt.
* Scheinnummer `WS-JJJJ-NNNNNN` je Mandant, gezählt über die höchste vergebene
  Nummer des Jahres, nicht über die Zeilenanzahl.
* Beide Antwortmodelle sind typisiert. Vorher hingen beide Wege an `WaageOut` mit
  `extra="allow"` — das Anlegen gab `{id, netto, gosse, zielschein_typ, status}`
  zurück, das Lesen eine ganz andere Form, und beides galt als dasselbe.
* Die Eingabeschemata tragen `extra="forbid"`: `wiegung1` wird jetzt abgewiesen
  statt stillschweigend verschluckt.

## Nachgezogen: die Paginierungsratsche

Beim Gate-Durchlauf fiel auf, dass ich sie in den beiden EUDR-Slices an der
Summenzeile gelesen hatte statt am Exit-Code. Sie war rot, und vier Einträge
waren meine: `eudr_register::auflisten`, `eudr_register::abrufen` (2),
`eudr_chargen::offene_chargen`, `eudr_anbindung::ungepruefte_vorgelagerte`.

Alle vier waren in SQL begrenzt (`LIMIT :limit` bzw. `LIMIT 5000`) — der
AST-Prüfer sieht eine Grenze in einer Zeichenkette nicht. Statt den Prüfer zu
beschwichtigen ist die Grenze jetzt im Code sichtbar: `.mappings().fetchmany(limit)`.
Und bei den beiden Kindlisten einer Erklärung kam die Antwort auf die Frage
hinzu, was passiert, wenn die Grenze greift: ein 503. Art. 9 verlangt **alle**
Flurstücke; eine Erklärung, die nur die ersten 5000 zeigt, wäre ein
unvollständiger Nachweis, der vollständig wirkt.

Summe 292 → 286. Rot bleibt `bank_accounts.py::list_ledger_options` aus
`bank_gl_binding_20261001` — Bank-Slice, als Handshake notiert.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_wiegung_kanonisch_vertrag.py          → 30 passed
  tests/test_dual_weighing_disposition.py
  tests/test_waage_api.py
  + EUDR + Genossenschaft                          → 232 passed
```

Die 30 Verträge prüfen unter anderem: die Waagenspalten stehen auf dem
kanonischen Schein; `domain_agrar.wiegungen` wird **nicht** angelegt und kommt im
Code nicht mehr vor; die vier Prüfbedingungen greifen auch bei direktem SQL;
`netto = brutto - tara` landet in der Datenbank; vertauschte Wägungen sind ein
422 und erzeugen keinen Schein; ohne Gewicht entsteht kein Schein; fremde Scheine
sind nicht lesbar; `EL`/`VL` werden auf `in`/`out` abgebildet; ein unbekannter
Zielscheintyp wird abgewiesen; die Rückverfolgbarkeit findet die neue Wiegung in
derselben Tabelle, auf die sie zeigt.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen. Gates: Tabellenverweise **10 → 9** an lebenden Wegen,
Baseline-Integrität OK, keine neue tote Transaktion, Godfile OK.

## Offene Punkte (Handshake)

1. **Das führende Wiegemodell** ist noch nicht entschieden.
   `domain_agrar.weighing_tickets` (Quittierung, `waage_mobile.py`) und
   `domain_ops.ops_wiegungen` (ORM-CRUD unter `/waage/wiegungen`) bleiben
   bestehen. Beide sind leer; die Zusammenführung gehört in einen ADR und war
   nicht Teil dieses Slices.
2. **Die Zuordnung der Ausgangswägung zum Frachtbrief** läuft über das
   Kennzeichen (`finalize_menge_from_outbound_weighing`) und ist mehrdeutig,
   wenn derselbe Lkw mehrere offene Frachtbriefe hat. Benannt, nicht geändert.
3. `bank_accounts.py::list_ledger_options` bricht die Paginierungsratsche —
   Bank-Slice.
4. `tests/test_bank_reconciliation_proof.py` ist weiter mit 31 Fehlern rot
   (`DuplicateColumn` im eigenen Fixture) — Bank-Slice.
5. `journal_entries_entry_number_key UNIQUE (entry_number)` ist systemweit statt
   je Mandant — Finanz-Owner.
