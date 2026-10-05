# Kontrakt-Disposition (Slice KONTRAKT-DISPOSITION-20261005)

Stand: 2026-10-05 · Welle 2, Slice 14

## Der Befund

`domain_agrar.kontrakt_dispositionen` existierte in keiner Datenbank. Angelegt
wurde sie vom **Anwendungscode** beim ersten Schreibzugriff:

```python
def ensure_disposition_table(db):
    try:
        db.execute(_sql_text("CREATE TABLE IF NOT EXISTS domain_agrar.kontrakt_dispositionen (...)"))
        db.commit()
    except Exception:
        db.rollback()
```

Vor dem ersten POST gab es die Tabelle nicht, und das Auflisten fing den
Lesefehler ab:

```python
except Exception as e:
    err = str(e).lower()
    if "relation" in err or "does not exist" in err:
        return []
```

Ein Kontrakt ohne sichtbare Abrufe sieht aus wie ein Kontrakt, der noch ganz
offen ist — und genau danach würde disponiert. Scheiterte das DDL selbst, wurde
der Fehlschlag verschluckt, und der folgende INSERT scheiterte mit einer Meldung,
die den Grund nicht nannte.

### Die fachlichen Befunde

**1. Niemand prüfte die Kontraktmenge.** Eine Disposition ist der Abruf einer
kontrahierten Menge. Nichts verglich die Summe der Abrufe mit
`kon_contract_line.qty_contract`. Es ließ sich mehr abrufen als kontrahiert ist,
beliebig oft.

Dabei **stand die Regel schon im Modell**: `kon_contract.allow_overdelivery` sagt
je Kontrakt, ob überliefert werden darf. Das Feld wurde nie gelesen. Ein Kontrakt
ohne wirksame Mengenbindung ist eine Notiz.

**2. Kein `tenant_id`** — nicht in der Tabelle, nicht in einer Abfrage. Gefiltert
wurde ausschließlich nach `kontrakt_id`. Wer eine Kontraktkennung kannte, las und
änderte fremde Abrufe.

**3. `freigabe` und `status` sagten dasselbe.** Die Freigabe stand als Boolean
**und** als `status = 'FREIGEGEBEN'`; der Freigabeweg setzte beides, der
Lieferweg nur den Status. Zwei Wahrheiten über denselben Umstand, von denen eine
veraltete.

**4. Keine Zustandsregeln.** Jeder Weg schrieb per `UPDATE … SET status = '…'`
ohne den alten Zustand anzusehen:

* eine stornierte Disposition ließ sich als geliefert melden,
* eine gelieferte stornieren,
* und geliefert werden konnte auch ohne Freigabe — die Freigabe war damit kein
  Tor, sondern eine Notiz.

**5. Der Wiegeschein war freier Text.** `wiegeschein_nr` ohne Bezug auf eine
Wiegetabelle. Eine Lieferung, die sich auf einen Wiegeschein beruft, den es nicht
gibt, ist nicht belegt.

Dazu: Datumsfelder als `TEXT`, Status ohne Wörterbuch, `uuid4`, und `KontraktOut`
mit `extra="allow"` an allen fünf Wegen.

## Was jetzt gilt

### Migration `kontrakt_disposition_20261005`

`tenant_id NOT NULL`, `ux_dispo_nummer` auf
`(tenant_id, kontrakt_id, disposition_nr)`, `ix_dispo_position` für die
Mengenprüfung, FK `wiegeschein_id → domain_inventory.weighing_tickets`
mit `ON DELETE RESTRICT`.

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_dispo_status` | Ein Zustand außerhalb von OFFEN/FREIGEGEBEN/GELIEFERT/STORNIERT. |
| `ck_dispo_menge_positiv` | Ein Abruf von null oder weniger. |
| `ck_dispo_nummer_positiv` | Eine Abrufnummer ohne Wert. |
| `ck_dispo_lieferdatum_bei_lieferung` | Ein Lieferdatum ohne Lieferung — und eine Lieferung ohne Datum. |
| `ck_dispo_wiegeschein_nur_bei_lieferung` | Ein Beleg für etwas, das nicht geschehen ist. |

**`freigabe` ist keine Spalte.** Sie ist abgeleitet
(`status in ('FREIGEGEBEN', 'GELIEFERT')`). Das Eingabeschema kennt das Feld
nicht und trägt `extra="forbid"` — ein `POST {"freigabe": true}` ist ein 422 und
keine stille Nichtwirkung. `wiegeschein_nr` fehlt im Anlegeschema aus demselben
Grund: Der Beleg kommt mit der Lieferung.

### Die Mengenprüfung

```
Summe der bindenden Abrufe + neuer Abruf ≤ qty_contract
```

Bindend sind `OFFEN`, `FREIGEGEBEN` und `GELIEFERT`. Ein **stornierter** Abruf
bindet nichts — sonst hätte eine Fehlbuchung die Kontraktmenge dauerhaft
blockiert.

Die Ausnahme ist `allow_overdelivery` am Kontrakt. Fehlt `qty_contract` ganz, ist
das ein 409 und keine Freigabe für beliebige Mengen: „keine kontrahierte Menge"
heißt nicht „unbegrenzt".

Dazu ein neuer Weg `GET /kontrakte/{id}/abrufstand`: kontrahierte, abgerufene und
offene Menge je Position. Die offene Menge ist abgeleitet; sie zu speichern hieße,
eine zweite Wahrheit neben den Abrufen zu führen.

### Die Zustände

```
OFFEN ──▶ FREIGEGEBEN ──▶ GELIEFERT
  │            │
  └────────────┴──▶ STORNIERT
```

`GELIEFERT` und `STORNIERT` sind endgültig. Jeder Wechsel läuft über **eine**
Stelle (`zustand_wechseln`) mit `SELECT … FOR UPDATE` auf der Zeile, damit zwei
gleichzeitige Wechsel nicht beide vom alten Zustand ausgehen. Ein verbotener
Wechsel ist ein 409 mit der Begründung und den erlaubten Zielen.

**Dass die Lieferung jetzt eine Freigabe voraussetzt, ist eine fachliche
Verschärfung** gegenüber dem Bestand (dort war geliefert aus `OFFEN` möglich).
Begründung: Sonst ist die Freigabe kein Tor. Die Abnahme gehört dem
Kontrakt-Owner; als offener Punkt notiert.

### Der Lieferbeleg

Die Wiegescheinnummer wird gegen `domain_inventory.weighing_tickets` des
**eigenen** Mandanten aufgelöst — den kanonischen Wiegeschein aus
`wiegung_kanonisch_20261005`. Eine Nummer, die sich nicht auflösen lässt, ist ein
422: „eine Nummer ohne Schein ist kein Beleg." Der Schein eines anderen Hauses
löst sich nicht auf.

Eine Lieferung **ohne** Wiegescheinnummer bleibt möglich — nicht jede Lieferung
wird gewogen. Dann steht auch kein Schein da, und das ist sichtbar.

### Godfile

`kontrakte.py` stand mit 1099 Zeilen in der Ratsche. Die Fachlogik ist in
`app/services/kontrakt_disposition_service.py` gewandert; die Endpunkte sind
dünn. Datei jetzt **1088** Zeilen, Baseline nachgezogen (down-only).
`kontrakte_service.py` verliert die drei alten Helfer samt Laufzeit-DDL.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_kontrakt_disposition_vertrag.py   → 35 passed
  tests/test_dual_weighing_disposition.py      → zusammen 83 passed
  + Kontraktumfeld (9 Dateien)                 → 105 passed, 3 skipped
```

Die 35 Verträge prüfen unter anderem: die Tabelle kommt aus der Migration und
kein `CREATE TABLE` steht mehr im Anwendungscode; `freigabe` und `wiegeschein_nr`
sind keine Spalten; die fünf Prüfbedingungen greifen auch bei direktem SQL; ein
Abruf über die Kontraktmenge wird abgewiesen und nennt `allow_overdelivery`; mit
erlaubter Überlieferung geht er durch; ein stornierter Abruf gibt seine Menge
frei; der Abrufstand nennt die offene Menge; Lieferung nur aus der Freigabe;
gelieferte und stornierte Abrufe sind endgültig; eine unbekannte oder fremde
Wiegescheinnummer ist kein Beleg; fremde Abrufe sind nicht lesbar, nicht
freigebbar und nicht erzeugbar.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen. Gates: Tabellenverweise **9 → 8** an lebenden Wegen,
Baseline-Integrität OK, keine neue tote Transaktion, Godfile OK.

### Ein Fund beim Prüfen

Der erste Freigabe-Aufruf antwortete 503 mit
`column "lieferdatum" is of type date but expression is of type text`: Ein
ungebundenes `NULL` in einem `CASE` leitet Postgres als `text` ab. Die
Umwandlung ist jetzt ausgeschrieben (`CAST(:lieferdatum AS date)`). Erwähnt, weil
der 503 genau gesagt hat, was fehlt — das ist der Unterschied zu einem
verschluckten Fehler.

## Altlasttests, die den Fehler festschrieben

`tests/test_dual_weighing_disposition.py` enthielt
`test_disposition_list_returns_empty_on_missing_table` — „GET Dispositionen muss
`[]` zurückgeben wenn Tabelle fehlt". Die Tabelle fehlte in **jeder** Datenbank.

Die vier anderen prüften Antwortformen gegen `fetchone()`-Doubles, also die Form
und nicht die Regel: Keiner hätte bemerkt, dass niemand die Kontraktmenge prüft,
dass `freigabe` und `status` dasselbe zweimal sagen oder dass eine stornierte
Disposition als geliefert gemeldet werden kann. Ersetzt durch acht Tests auf das
Wörterbuch, die Übergänge und die Mengenregel.

## Offene Punkte (Handshake)

1. **Lieferung setzt Freigabe voraus** — fachliche Verschärfung, Abnahme beim
   Kontrakt-Owner.
2. Eine Fremdwiegung ohne Schein im System kann nicht als belegte Lieferung
   gemeldet werden (nur als Lieferung ohne Beleg). Beabsichtigt.
3. `DispositionCreate`/`DispositionOut` in `kontrakte_schemas.py` sind nach
   diesem Slice ungenutzt; sie stehen noch für ältere OpenAPI-Verweise. Aufräumen
   gehört in den nächsten Durchgang über die Kontraktschemata.
4. `bank_accounts.py::list_ledger_options` bricht weiter die Paginierungsratsche
   — Bank-Slice. Einziger roter Eintrag.
5. `tests/test_bank_reconciliation_proof.py` weiter 31 Fehler
   (`DuplicateColumn` im eigenen Fixture) — Bank-Slice.
6. `journal_entries_entry_number_key UNIQUE (entry_number)` systemweit statt je
   Mandant — Finanz-Owner.
7. Führendes Wiegemodell: `domain_agrar.weighing_tickets` und
   `domain_ops.ops_wiegungen` bestehen weiter (beide leer) — ADR offen.
