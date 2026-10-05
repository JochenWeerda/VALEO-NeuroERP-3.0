# Genossenschaft-Mitgliederregister (Slice GENOSSENSCHAFT-MITGLIEDERREGISTER-20261005)

Stand: 2026-10-05 · Welle 2, Slice 12

## Der Befund

`domain_shared.genossenschaft_mitglieder` und
`domain_shared.genossenschaft_anteilsbewegungen` existierten in **keiner**
Datenbank — nicht in der frischen `valeo_probe`, nicht in der gewachsenen
`valeo_neuro_erp`. Keine Migration legte sie an. Die sechs Wege unter
`/genossenschaft` haben damit nie funktioniert, und niemand hat es erfahren:

| Weg | Was er bei jedem Aufruf antwortete |
| --- | --- |
| `GET /mitglieder` | `[]` — „keine Mitglieder" |
| `GET /kapitaluebersicht` | 0 Mitglieder, 0 Anteile, **0,00 € Kapital** |
| `GET /mitglieder/{id}` | 503 (hier war der Fehler wenigstens sichtbar) |
| `GET /mitglieder/{id}` → `anteilsbewegungen` | `[]`, auch bei Lesefehler |

Für eine eingetragene Genossenschaft ist keine dieser Antworten je wahr. § 30
GenG verpflichtet die eG zur Mitgliederliste; das Geschäftsguthaben der
Mitglieder ist eine Bilanzposition (§ 337 HGB). „Keine Mitglieder" und
„0,00 € Kapital" sind keine leeren Zustände, sondern Befunde.

Die Maske verdoppelte das: `pages/genossenschaft/mitglieder.tsx` las `vorname`,
`geschaeftsanteile` und `gesamtkapital` — drei Felder, die der Endpunkt nie
geliefert hat. In der Namensspalte stand „undefined, undefined", und
`reduce((s, m) => s + m.gesamtkapital, 0)` ergab `NaN €`.

**Zweiter Befund:** Keine einzige Abfrage trug den Mandanten, obwohl
`get_tenant_id` als Abhängigkeit hing. Hätten die Tabellen existiert, hätte
Genossenschaft A die Mitgliederliste und die Bankverbindungen von
Genossenschaft B gesehen.

## Was jetzt gilt

### Migration `genossenschaft_mitgliederregister_20261005`

Beide Tabellen mit `tenant_id NOT NULL`, `ux_geno_mitglied_nr` auf
`(tenant_id, mitglieds_nr)`, FK `mitglieds_id → genossenschaft_mitglieder
ON DELETE RESTRICT`.

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_geno_mitglied_status` | Ein Stand außerhalb von AKTIV/RUHEND/AUSGETRETEN. |
| `ck_geno_austritt_datiert` | Ein Austritt ohne Datum oder ein Datum ohne Austritt (§ 30 Abs. 2 GenG). |
| `ck_geno_austritt_nach_eintritt` | Ein Austritt vor dem Eintritt. |
| `ck_geno_bewegungstyp` | Ein freies Wort als Bewegungstyp. |
| `ck_geno_anzahl_positiv` | Eine negative Anzahl — die Richtung steckt im Typ, sonst gäbe es zwei Wege, einen Abgang auszudrücken, und nur einer würde geprüft. |
| `ck_geno_uebertragung_gegenseite` | Eine Übertragung ohne Gegenseite. |
| `ck_geno_uebertragung_nicht_an_sich` | Eine Übertragung an sich selbst. |

### Der Anteilsbestand ist keine Spalte

Vorher trug das Mitglied `genossenschaftsanteile` und wurde bei jeder Bewegung
per `SET genossenschaftsanteile = genossenschaftsanteile + :delta`
fortgeschrieben — **neben** dem Bewegungsjournal, das dasselbe sagt. Zwei
Wahrheiten über denselben Bestand laufen auseinander, sobald eine Bewegung
fehlschlägt oder korrigiert wird, und der Fehler ist dann von außen nicht mehr
erkennbar: Beide Zahlen sehen plausibel aus.

Jetzt ist der Bestand die Summe der Bewegungen
(`genossenschaft_service.BESTANDSAUSDRUCK`), und die Spalte ist weg. Die
Rechnung steht **einmal**: Die Vorzeichen-Abbildung `VORZEICHEN` und der
SQL-`CASE` werden beide aus der Menge `ZUGANG` erzeugt. Wer die Richtung eines
Typs ändern will, ändert eine Menge, nicht zwei Codestellen.

`MitgliedPatch` kennt das Feld nicht mehr, und das Schema trägt
`extra="forbid"` — ein `PATCH {"genossenschaftsanteile": 99}` ist ein 422 und
nicht eine stille Nichtänderung. Eine Anteilsänderung ohne Bewegung ist genau
die unbelegte Änderung, die GoBD Rz. 107 ff. ausschließt.

Auch die **Erstzeichnung** beim Beitritt wird als Bewegung `ZEICHNUNG`
geschrieben, nicht als Zahl gespeichert: Damit hat auch der erste Anteil einen
Beleg.

### Das Vokabular ist festgelegt

`ZEICHNUNG`, `ERHOEHUNG`, `TEILRUECKZAHLUNG`, `VOLLRUECKZAHLUNG`,
`UEBERTRAGUNG_AB`, `UEBERTRAGUNG_AN`.

**`TRANSFER` ist nicht übernommen.** Der alte Code rechnete
`sign = -1 if typ in ("TEILRUECKZAHLUNG", "VOLLRUECKZAHLUNG") else 1` — ein
`TRANSFER` bekam also `+1` und hätte Anteile aus nichts geschaffen. Eine
Übertragung hat zwei Seiten; deshalb zwei gerichtete Typen und eine Gegenseite
als Pflichtfeld, und beide Seiten werden in einer Transaktion geschrieben oder
keine. Eine Übertragung wird **nicht** ins Hauptbuch gebucht: Die Anteile
wechseln das Mitglied, die Bilanzposition bleibt gleich.

### Kein negativer Bestand

Geprüft wird gegen den abgeleiteten Bestand unter `SELECT … FOR UPDATE` auf der
Mitgliedszeile. Ohne die Sperre könnten zwei gleichzeitige Rückzahlungen
denselben Bestand sehen und gemeinsam mehr abziehen, als da ist. Eine
`VOLLRUECKZAHLUNG` muss den ganzen Bestand treffen — sonst ließe sie einen Rest
stehen und hieße trotzdem „voll".

Ein Austritt mit Restbestand wird abgewiesen: Das Auseinandersetzungsguthaben
nach § 73 GenG ist zuerst zu buchen. `AUSGETRETEN` ist dabei kein Löschen; die
Zeile bleibt in der Liste, und die Mitgliedsnummer wird nicht wiederverwendet.

### Die Hauptbuchbuchung ist verbindlich

Vorher:

```python
except Exception:  # noqa: BLE001 — GL-Buchung nicht kritisch für Anteilsbewegung
    pass
```

— unter einem Kommentar, der behauptete, den Belegbruch zu schließen
(`GENO-ANTEILE-JE-001: GL-Buchung für Anteilsbewegung (Belegbruch schliessen)`).
Fällt die Buchung aus, weicht das gezeichnete Kapital im Hauptbuch dauerhaft von
der Mitgliederliste ab (§ 238 HGB, GoBD Rz. 30 ff.), und niemand erfährt es.

Jetzt läuft sie in derselben Transaktion; scheitert sie, ist die Bewegung nicht
gebucht, und die Antwort nennt den Grund samt der benötigten Konten. Dass ein
Konto fehlt oder eine Periode geschlossen ist, ist eine Entscheidung des Hauses
und keine Störung, die man wegloggt.

`_is_test_double_session()` ist entfallen: Produktionscode darf nicht nach
Testdoubles verzweigen — sonst prüft der Test einen anderen Weg als den, der
läuft.

### Belegnummer

`GENO-{bewegung_id[:8]}` war falsch: `uuid7` ist zeitgeordnet, die vorderen
Stellen sind der Zeitstempel. Alle Bewegungen desselben Zeitfensters bekamen
dieselbe Nummer, und weil `journal_entries.entry_number` systemweit eindeutig
ist, scheiterte jede zweite Buchung. Jetzt stammt die Nummer aus dem Zufallsteil
der Kennung.

### Antwortmodelle

Alle sechs Wege hingen an **einem** Modell `GenossenschaftOut` mit
`extra="allow"` — auch die Kapitalübersicht, die Aggregatzahlen liefert. Ein
Modell, das alles erlaubt, dokumentiert nichts. Jetzt hat jeder Weg sein Modell;
`GenossenschaftOut` bleibt nur für ältere OpenAPI-Verweise stehen.

## Der Fund außerhalb des Slices: `chart_of_accounts`

Beim Aufbau des Prüfstands fiel auf, dass zwei Mandanten **nicht** beide ein
Konto 1200 führen können:

```
chart_of_accounts_account_number_key UNIQUE (account_number)
```

Angelegt in `001_initial_schema.py:125`, ohne Mandant. Systemweit eindeutig.
Daneben steht im Code, dass es je Mandant gemeint war:
`FinanceTransactionService._bookable_account` sucht
`WHERE tenant_id = :t AND account_number = :n`. Und der SKR03-Bestand liegt
unter `tenant_id = 'system'`, wo ihn kein echter Mandant buchen darf.

Die Folge: In einer frischen Installation hätte die Hauptbuchbuchung einer
Anteilszeichnung für **keinen** echten Mandanten gelingen können — die zweite
Genossenschaft im System kann ihren Kontenrahmen nicht anlegen. Weil dieser
Slice die Buchung verbindlich macht, wäre das Register damit unbenutzbar
geworden.

Deshalb tauscht die Migration die Bedingung:

```sql
DROP CONSTRAINT IF EXISTS chart_of_accounts_account_number_key;
ADD CONSTRAINT uq_coa_mandant_kontonummer UNIQUE (tenant_id, account_number);
```

Vor dem Umbau wird geprüft, ob eine Nummer je Mandant mehrfach vorkommt; wenn
ja, bricht die Migration ab, statt die Lage zu überschreiben. In beiden
Datenbanken war das nicht der Fall. Der Rückbau stellt die systemweite
Eindeutigkeit **nicht** wieder her: Sie war ein Fehler und wäre nach dem Anlegen
zweiter Kontenrahmen ohnehin nicht mehr erfüllbar.

`uq_coa_id_tenant_bank_gl` aus `bank_gl_binding_20261001` bleibt unberührt.

**Nicht angefasst, aber derselbe Fehler:**
`journal_entries_entry_number_key UNIQUE (entry_number)` ist ebenfalls
systemweit — zwei Genossenschaften können nicht beide eine Buchung „RE-001"
führen. Das gehört dem Finanz-Owner, der gerade in dieser Datei arbeitet, und
ist als Handshake notiert.

## Maske

`pages/genossenschaft/mitglieder.tsx` liest jetzt die Felder, die es gibt, zeigt
den Stand als Badge, nimmt die Summen aus der Kapitalübersicht (und zeigt bei
einem Lesefehler **keine** 0,00 €, sondern sagt, dass sie fehlen), und hat zwei
Dialoge mit Pending-Guard und Toast: Mitglied aufnehmen und Anteilsbewegung
buchen. Die Zeilenaktion ist je Mitglied gesperrt, nicht global. `tsc` und
`eslint` sauber.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_genossenschaft_register_vertrag.py        → 59 passed
  tests/test_sanctions_genossenschaft_intrastat.py     → 24 passed
  + Journal/GoBD/Kontenrahmen/Bank                     → 226 passed, 1 skipped
```

Die 59 Verträge prüfen unter anderem: beide Tabellen vorhanden; `tenant_id` in
jeder Abfrage; ein Lesefehler ist ein 503 mit `migration_hint`; der Bestand
stimmt mit der nachgerechneten Summe der Bewegungen überein; `TRANSFER` wird
abgewiesen; ein Abgang über den Bestand wird abgewiesen; eine Übertragung ohne
Gegenseite, an sich selbst oder über den Bestand wird abgewiesen und schreibt
keine Seite; ein Austritt mit Restbestand wird abgewiesen; ohne Kontenrahmen
entsteht **keine** Bewegung; Belegnummern kollidieren nicht; zwei Häuser dürfen
dasselbe Konto führen.

Migration gegen die frische `valeo_probe` (inkl. `downgrade` und erneutem
`upgrade`) **und** die gewachsene `valeo_neuro_erp` hochgezogen. Gates:
Tabellenverweise **12 → 10** an lebenden Wegen (Schwelle nachgezogen),
Baseline-Integrität OK, keine neue tote Transaktion.

## Altlasttests, die den Fehler festschrieben

`tests/test_sanctions_genossenschaft_intrastat.py` enthielt
`test_kapitaluebersicht_db_error_returns_empty` — „DB error → returns zero dict,
does not raise" — und `assert db.execute.call_count == 2`, was das
Fortschreiben der zweiten Zahl festhielt. Beide sind durch Tests ersetzt, die
das Gegenteil verlangen: 503 statt 0,00 €, und ein Vokabular, dessen Vorzeichen
aus einer Menge stammt.

## Offene Punkte (Handshake)

1. `journal_entries_entry_number_key` ist systemweit eindeutig (siehe oben) —
   Finanz-Owner.
2. `tests/test_bank_reconciliation_proof.py` ist mit 31 Fehlern rot, seit
   `bank_gl_binding_20261001` `bank_accounts.gl_account_id` anlegt: Das
   Testfixture kopiert die Tabelle mit `INCLUDING ALL` und fügt die Spalte
   danach noch einmal hinzu (`DuplicateColumn`). Bestand vor diesem Slice,
   gehört dem Bank-Slice.
3. `app/api/v1/endpoints/logistics_tours.py` bricht die Godfile- **und** die
   Paginierungs-Ratsche (1033 → 1059 Zeilen, `list_tours` 2 → 3 Abfragen),
   committet in `dec0dfd1b` — Tourenplanungs-Agent.
4. Satzungsgrößen nach § 7/§ 7a GenG (Höhe des Geschäftsanteils,
   Mindestbeteiligung, Nachschusspflicht) sind **nicht** modelliert;
   `anteilswert_eur` steht weiter am Mitglied. Benannte Lücke.
5. Die Kontenzuordnung 1200/0900/1600 folgt dem Bestandscode und gehört
   fachlich dem Finanz-Owner; dieser Slice hat sie verbindlich gemacht, nicht
   erweitert.
