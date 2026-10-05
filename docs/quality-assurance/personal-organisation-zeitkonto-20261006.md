# Organigramm und Arbeitszeitkonto (Slice PERSONAL-ORGANISATION-ZEITKONTO-20261006)

Stand: 2026-10-06 · Welle 2, Slice 17

## Der Befund

Drei Verweise ins Leere in `personal.py`, an zwei nachweispflichtigen Fächern.

| Verweis | Lage |
| --- | --- |
| `domain_hr.org_units` | existierte in keiner Datenbank — alle vier Wege des Organigramms antworteten 503 |
| `domain_hr.time_account_adjustments` | ebenso — jede Saldokorrektur antwortete 503 |
| `domain_hr.schichten` | existiert nicht, **aber `domain_hr.shifts` gibt es**: eine deutsche Dublette desselben Begriffs |

### Die Dublette war zweifach falsch

```sql
SELECT COALESCE(SUM(planned_hours), 0) FROM domain_hr.schichten
WHERE employee_ref = :employee_ref AND tenant_id = :tenant_id
```

Die vorhandene Tabelle heißt `shifts` und hat **keine** dieser Spalten. Sie führt
`shift_date`, `starts_at` und `ends_at` als Uhrzeiten und
`assigned_employee_refs` als JSONB-Liste. Falsch waren also der Tabellenname
*und* alle drei gelesenen Spalten.

Weil die drei Abfragen des Zeitkontos in **einem** `try` standen, antwortete
`/time-accounts/{ref}` ausnahmslos 503: **Das Arbeitszeitkonto hat nie
funktioniert.**

### Und die Formel darunter stimmte nicht

```python
transferred = sum(b["actual_hours"] for b in prev_breakdown) + total_adj
saldo = total_actual - total_planned + total_adj
```

`total_adj` geht **zweimal** ein. Und `transferred_from_prev_period` summiert die
*Ist-Stunden aller Vorjahre* — das ist kein Übertrag, sondern eine Lebenssumme.
Ein Arbeitszeitkonto trägt die Grundlage der Überstundenabrechnung und der
Aufzeichnung nach § 16 Abs. 2 ArbZG; eine falsche Zahl dort ist kein
Anzeigefehler.

## Was jetzt gilt

### Migration `personal_organisation_zeitkonto_20261006`

`domain_hr.org_units` mit `tenant_id`, `ux_orgeinheit_code` auf
`(tenant_id, unit_code)`, Selbstverweis `parent_id` und Fremdschlüssel auf
`domain_finance.kostenstellen`, beide `ON DELETE RESTRICT`.

`domain_hr.time_account_adjustments` mit `tenant_id`, `employee_ref`,
`delta_hours`, `reason`, `adjustment_date`, `erfasst_durch`.

| Prüfbedingung | Was sie verhindert |
| --- | --- |
| `ck_orgeinheit_art` | Eine Einheitenart außerhalb des Wörterbuchs. |
| `ck_orgeinheit_nicht_sich` | Der triviale Zyklus: eine Einheit als ihr eigener Elternteil. |
| `ck_orgeinheit_name_gefuellt` | Eine Einheit ohne Namen. |
| `fk_orgeinheit_eltern` (RESTRICT) | Eine Einheit mit Untereinheiten verschwindet nicht einfach. |
| `fk_orgeinheit_kostenstelle` (RESTRICT) | Eine Kostenstelle, die im Organigramm hängt, wird nicht gelöscht. |
| `ck_zeitkorrektur_wirksam` | Eine Korrektur um null Stunden — das ist keine. |
| `ck_zeitkorrektur_begruendet` | Eine Korrektur am Zeitkonto ohne Grund (§ 16 Abs. 2 ArbZG, GoBD Rz. 30 ff.). |

### Der Zyklenschutz, dreifach

Die Lesewege sind rekursive CTEs; ein Zyklus läuft endlos.

1. **Prüfbedingung** für den trivialen Fall (`parent_id <> id`).
2. **Beim Umhängen** prüft `wuerde_zyklus()`, ob die Einheit im Aufwärtspfad des
   neuen Elternteils liegt — der Zyklus wird abgewiesen, *bevor* er entsteht
   (409 mit Begründung).
3. **Beim Lesen** eine Tiefengrenze (`MAX_TIEFE = 50`). Wird sie erreicht, ist das
   ein **409**, kein gekürzter Baum. Ein Organigramm, das Teile stillschweigend
   wegläßt, ist schlimmer als eines, das sich beschwert.

### Die Kostenstelle ist eine Beziehung

Fremdschlüssel plus eine Prüfung beim Schreiben, dass sie dem **eigenen**
Mandanten gehört. Der Fremdschlüssel allein kann das nicht sagen, und eine fremde
Kostenstelle im Organigramm wäre ein Auswertungsfehler, der wie eine Zuordnung
aussieht.

### Die Planstunden kommen aus den Schichten

Gerechnet aus `starts_at`/`ends_at`, und nur für Schichten, in deren
`assigned_employee_refs` der Mitarbeiter steht. Eine abgesagte Schicht plant
keine Stunden — und das Statuswörterbuch der vorhandenen Tabelle ist **englisch**
(`shifts_status_ck`: planned, warning, blocked, cancelled); es steht jetzt einmal
im Dienst.

Eine Nachtschicht zählt bis zum nächsten Tag. **Dabei ist mir ein Fehler
unterlaufen, den der Prüfstand gefangen hat:** Die erste Fassung rechnete
`(ends_at + INTERVAL '24 hours') - starts_at`. Addition auf einen `time`-Wert
rechnet modulo 24 Stunden, 06:00 blieb 06:00, und eine Nachtschicht ergab
**−16 Stunden**. Richtig ist, die 24 Stunden auf das **Intervall** zu addieren:
`(ends_at - starts_at) + INTERVAL '24 hours'`.

### Die Saldoformel

* **Übertrag** = (Ist − Plan + Korrekturen) **aller Vorperioden**
* **laufende Periode** = (Ist − Plan + Korrekturen) des betrachteten Jahres
* **Saldo** = Übertrag + laufende Periode + Folgeperioden

Damit ist der Saldo die Summe der ausgewiesenen Zahlen, und jede Stunde steckt in
genau einer von ihnen. Ein Vertrag prüft genau diese Gleichung.

Die Antwort nennt außerdem je Monat Ist, Plan, Korrektur und Monatssaldo — statt
nur Ist-Stunden wie vorher.

### Godfile

`personal.py` stand mit 3345 Zeilen in der Ratsche. Die Logik liegt in
`app/services/personal_organisation_service.py`; die Datei ist auf **3315**
Zeilen geschrumpft, Baseline nachgezogen (down-only).

### Maske

`pages/personal/organigramm.tsx` las `data.units` — ein Feld, das die Antwort
nie hatte (sie heißt `org_chart`). Die Maske hätte also auch nach der Migration
„Keine Organisationseinheiten vorhanden" gezeigt. Sie liest jetzt den Baum, den
der Endpunkt schon verschachtelt liefert, statt ihn aus einer flachen Liste noch
einmal zu bauen.

## Nachweis

```
DATABASE_URL=…/valeo_probe python -m pytest \
  tests/test_personal_organisation_zeitkonto_vertrag.py  → 44 passed
  tests/test_personal_major_gap_extensions.py            → zusammen 48 passed
```

Die 44 Verträge prüfen unter anderem: beide Tabellen vorhanden;
`domain_hr.schichten` wird nicht nachgebaut und im Code nicht mehr gelesen; alle
sieben Prüfbedingungen greifen auch bei direktem SQL; das Organigramm liefert
einen Baum statt 503; der Einheitenschlüssel ist je Mandant eindeutig; ein
fremdes Organigramm ist unsichtbar; eine fremde Elterneinheit und eine fremde
Kostenstelle werden abgewiesen; das Umhängen in den eigenen Teilbaum ist ein 409;
die Tiefengrenze ist ein Fehler und kein gekürzter Baum; die Planstunden kommen
aus `shifts` und nur für zugeordnete, nicht abgesagte Schichten des eigenen
Hauses; die Nachtschicht zählt acht Stunden; die Korrektur zählt genau einmal;
der Saldo ist die Summe der ausgewiesenen Zahlen; der Übertrag ist kein
Lebenssummenwert; eine Korrektur ohne Grund oder um null Stunden wird abgewiesen.

Migration gegen die frische `valeo_probe` und die gewachsene `valeo_neuro_erp`
hochgezogen. Gates: Tabellenverweise **7 → 4** an lebenden Wegen, alle vier
Ratschen grün.

### Zwei Funde des Prüfstands

* `time_entries` hat eine Bereichsprüfung (`ck_hr_time_entries_hours_range`) und
  wies meinen Testwert von 40 Stunden an einem Tag zu Recht ab. Die Datenbank
  verteidigt sich hier richtig; der Test war unrealistisch.
* Die Nachtschichtrechnung (siehe oben).

## Altlasttest

`test_time_account_uses_canonical_time_entries_columns` **mockte
`domain_hr.schichten` in die Welt** und bestätigte damit eine Saldoformel, die
die Korrektur doppelt zählte. Ein Test, der eine fehlende Tabelle mockt, prüft
die Abfrage gegen eine Welt, die es nicht gibt. Ersetzt durch drei Tests auf das
kanonische Tabellenziel, die Saldogleichung und den Zyklenschutz.
`test_org_subtree_uses_actual_root_parent` zeigt jetzt auf den Dienst.

## Offene Punkte (Handshake)

1. **Die Bedeutung von `transferred_from_prev_period` hat sich geändert** (vorher
   Lebenssumme plus Korrektur, jetzt Übertrag) und das Feld heißt
   `uebertrag_vorperioden`. Masken, die die Zahl anzeigen, zeigen danach etwas
   anderes — richtiger, aber anderes. Abnahme der Saldodefinition beim
   Personal-Owner.
2. `shifts.assigned_employee_refs` ist eine JSONB-Liste ohne Fremdschlüssel auf
   die Person. Das bleibt vorerst so; eine Zuordnungstabelle wäre der nächste
   Schritt, wenn Schichten je Mitarbeiter ausgewertet werden sollen.
3. Die Einheitenart `GESCHAEFTSBEREICH` ist neu gegenüber dem alten Muster
   (`ABTEILUNG|TEAM|STANDORT|KOSTENSTELLE`). Falls im Haus eine andere Gliederung
   gilt, gehört das Wörterbuch angepasst — es steht an einer Stelle.
