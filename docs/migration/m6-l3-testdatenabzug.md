---
title: L3-Testdatenabzug (Firebird, SQL-Maske, Calc)
type: runbook
audience: [fachbereich, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-25
version: 1.0.0
description: Stichproben aus der L3-Firebird-Datenbank ueber die SQL-Maske und Calc ziehen, pseudonymisieren und lokal in VALEO einlesen - DSGVO-konform, ohne Weitergabe an Dritte.
---

# L3-Testdatenabzug (fruehe Testphase M6)

Nutzerangabe 25.11.2026: L3 laeuft auf **Firebird**. Eine L3-Maske fuehrt SQL-Abfragen aus und uebergibt das Ergebnis
an **Calc**. Fuer fruehe Testlaeufe ziehen wir Stichproben: je Artikelgruppe drei Beispielartikel, dazu sonstige
Stammdaten und Geschaeftsvorfaelle. Es wird **nur gelesen**; L3 bleibt fuehrend und unveraendert.

## 1. DSGVO und Weitergabe - verbindlich

1. **Datensparsam:** nur Stichproben, nur Spalten, die der Test braucht.
2. **Pseudonymisiert schon in der Abfrage.** Kunden und Lieferanten sind oft natuerliche Personen (Landwirte).
   - Name, Strasse, Telefon, Fax, E-Mail und Bankdaten verlassen L3 nie im Klartext.
   - Kunden-, Lieferanten- und Kontonummern bleiben erhalten; sie sind die Schluessel des Abgleichs.
   - PLZ wird auf zwei Stellen gekuerzt, der Ort entfaellt.
   - Belege tragen nur Nummern und Betraege, keine Freitexte.
3. **Nur lokal.**
   - Ablage ausschliesslich auf dem Entwicklungsrechner unter `C:\VALEO-Testdaten\l3\`, ausserhalb des Repositorys.
   - Nie in Git oder GitHub, nie in die CI, kein Cloud-Speicher, kein Mailversand.
   - `.gitignore` sperrt zusaetzlich `**/l3-testdaten/**` und `l3_abzug_*.csv`.
4. **Nicht an KI-Dienste.** Die Dateien werden nicht in Chats eingefuegt und nicht von KI-Agenten geoeffnet; jede
   Uebertragung an einen solchen Dienst ist eine Weitergabe an Dritte.
   - Das Einlese-Skript gibt deshalb nur Zaehlwerte und Fehlerarten aus, keine Feldinhalte.
   - Den Differenzbericht mit Inhalten sieht nur die Person am Rechner.
5. **Eigener Testmandant** `l3-test` in der Entwicklungsdatenbank. Der Mandant ist RLS-getrennt von den anderen
   Mandanten und vollstaendig loeschbar (Abschnitt 5).
6. **Loeschen** spaetestens zum Ende der fruehen Testphase, mit Protokoll.
   - Dazu gehoeren die Dateien und der Mandant.
   - Gleiches gilt fuer jeden Abzug, der versehentlich Klartext enthaelt: sofort loeschen, nicht einlesen.

Das Einlese-Skript prueft jede Datei vor der Annahme auf erkennbaren Klartext: E-Mail-Adressen, Telefonnummern, IBAN
und Strassenangaben. Findet es etwas, liest es nichts ein.

## 2. Abfragen fuer die SQL-Maske (Firebird)

Die Abfragen setzen Firebird 3 oder neuer voraus (Fensterfunktion `ROW_NUMBER`); fuer Firebird 2.5 steht je eine
Variante dabei. Die Spaltennamen stammen aus `L3_Uebersicht Tabellen und Spalten.csv`. Ihre Bedeutung ist am Ergebnis
zu bestaetigen.

### 2.1 Artikelgruppen

```sql
SELECT GRUPPE, BEZEICHNUNG, ARTNRVON, ARTNRBIS, UMSATZGRP FROM WWS_ARTIKELGRP ORDER BY GRUPPE
```

### 2.2 Drei Beispielartikel je Artikelgruppe

```sql
SELECT 'artikel' AS TYP, ARTIKELNR AS QUELLE, ARTIKELNR AS ARTNR, BEZEICHN1, BEZEICHN2, ARTIKELGRP, ME1, GESPERRT
FROM (SELECT a.*, ROW_NUMBER() OVER (PARTITION BY a.ARTIKELGRP ORDER BY a.ARTIKELNR) AS RN
      FROM WWS_ARTIKEL a WHERE COALESCE(a.GESPERRT, 0) = 0) x
WHERE RN <= 3
```

Firebird 2.5:

```sql
SELECT 'artikel' AS TYP, a.ARTIKELNR AS QUELLE, a.ARTIKELNR AS ARTNR, a.BEZEICHN1, a.BEZEICHN2, a.ARTIKELGRP, a.ME1,
       a.GESPERRT
FROM WWS_ARTIKEL a
WHERE COALESCE(a.GESPERRT, 0) = 0
  AND (SELECT COUNT(*) FROM WWS_ARTIKEL b WHERE b.ARTIKELGRP = a.ARTIKELGRP AND b.ARTIKELNR < a.ARTIKELNR
       AND COALESCE(b.GESPERRT, 0) = 0) < 3
```

### 2.3 Bestand der Beispielartikel

```sql
SELECT 'bestand' AS TYP, l.ARTIKELNR || '@' || l.LAGER AS QUELLE, l.ARTIKELNR AS ARTNR, l.LAGER, l.BUCHBESTAND AS BESTAND
FROM WWS_LAGERBESTAND l
WHERE l.ARTIKELNR IN (/* Artikelnummern aus 2.2 */)
```

### 2.4 Kunden (pseudonymisiert)

Nur Kunden, die in den gezogenen Geschaeftsvorfaellen vorkommen, hoechstens 20:

```sql
SELECT FIRST 20 'kunde' AS TYP, k.KUNDENNR AS QUELLE, k.KUNDENNR, 'Testkunde ' || k.KUNDENNR AS KUNDNAME,
       SUBSTRING(a.PLZ FROM 1 FOR 2) || '000' AS PLZ, k.STAAT, k.DEBITORKTO, k.SPERRE
FROM KUNDEN k LEFT JOIN ADRESSEN a ON a.NUMMER = k.ADRNR1
WHERE k.DEBITORKTO IS NOT NULL AND k.DEBITORKTO <> ''
```

Nicht ausgegeben: NAME1/2, STRASSE, ORT, TELEFON1/2, TELEFAX, EMAIL, USTID, Bankverbindung, Bemerkungen, Freifelder.

### 2.4a Lieferanten (pseudonymisiert)

```sql
SELECT FIRST 20 'lieferant' AS TYP, 'L' || k.KUNDENNR AS QUELLE, k.KUNDENNR AS LIEFERANTENNR,
       'Testlieferant ' || k.KUNDENNR AS KUNDNAME, SUBSTRING(a.PLZ FROM 1 FOR 2) || '000' AS PLZ, k.STAAT,
       k.KREDITORKTO, k.SPERRE
FROM KUNDEN k LEFT JOIN ADRESSEN a ON a.NUMMER = k.ADRNR1
WHERE k.KREDITORKTO IS NOT NULL AND k.KREDITORKTO <> ''
```

Ein Landwirt, der Kunde und Lieferant ist, erscheint in beiden Abzuegen. In VALEO wird er ein Geschaeftspartner mit
Debitoren- und Kreditorenkonto, wenn USt-IdNr. und Name uebereinstimmen. Weil die Abfrage den Namen pseudonymisiert
("Testkunde"/"Testlieferant") und keine USt-IdNr. zieht, bleiben es im Testabzug zwei Partner.

### 2.4b Preise der Beispielartikel

```sql
SELECT 'preisliste' AS TYP, PREISTABNR AS QUELLE, PREISTABNR, BEZEICHNUNG FROM WWS_PREISTAB1
```

```sql
SELECT 'artikelpreis' AS TYP,
       p.ARTIKELNR || '|' || p.PREISTABNR || '|' || p.DATUMVON || '|' || COALESCE(p.ABMENGE, 0) AS QUELLE,
       p.ARTIKELNR AS ARTNR, p.PREISTABNR, p.PREIS, a.PE1 AS PREISJE, p.ABMENGE, p.DATUMVON, p.DATUMBIS
FROM WWS_ARTPREIS2 p JOIN WWS_ARTIKEL a ON a.ARTIKELNR = p.ARTIKELNR
WHERE p.ARTIKELNR IN (/* Artikelnummern aus 2.2 */)
```

`PREISJE` ist der Preisbezug (z. B. 100 fuer "je 100 kg"); ob `PE1` ihn traegt, zeigt das erste Ergebnis.
Kundenpreise: `WWS_KUNDEN_PREISE` mit `TYP 'kundenpreis'`, `QUELLE = KUNDENNR || '|' || ARTIKELNR`, nur fuer gezogene
Kunden und Beispielartikel, ohne `BEMERKUNG` und `BEDIENER`.

### 2.4c Kundenrabatte (nur Prozent)

```sql
SELECT 'kundenrabatt' AS TYP, r.KUNDENNR || '|' || r.ARTIKELNR AS QUELLE, r.KUNDENNR, r.ARTIKELNR AS ARTNR,
       r.RABATT AS RABATTPROZ, r.GUELTIGAB AS DATUMVON, r.GUELTIGBIS AS DATUMBIS, r.LISTENR
FROM WWS_KUNDRABATT r
WHERE r.RABATTART = /* Code fuer Prozentrabatt, am ersten Ergebnis bestimmen */ AND r.KUNDENNR IN (/* aus 2.4 */)
```

### 2.4d Aktionen der Beispielartikel

```sql
SELECT DISTINCT 'aktion' AS TYP, AKTIONNR AS QUELLE, AKTIONNR, MIN(DATUMVON) AS DATUMVON, MAX(DATUMBIS) AS DATUMBIS
FROM WWS_AKTIONSPREISE WHERE ARTIKELNR IN (/* aus 2.2 */) GROUP BY AKTIONNR
```

```sql
SELECT 'aktionspreis' AS TYP, AKTIONNR || '|' || ARTIKELNR AS QUELLE, AKTIONNR, ARTIKELNR AS ARTNR, PREISNETTO,
       1 AS PREISJE, LAGER, KUNDENSELEKTION
FROM WWS_AKTIONSPREISE WHERE ARTIKELNR IN (/* aus 2.2 */)
```

Ob `PREISNETTO` je Grundeinheit oder je Preiseinheit gilt, zeigt das erste Ergebnis (dann `PREISJE` anpassen).

### 2.5 Offene Posten der gezogenen Kunden

```sql
SELECT 'offener_posten' AS TYP, o.KONTONR || '/' || o.RECHNNR AS QUELLE, o.KONTONR, o.RECHNNR, o.RECHNBETRAG,
       o.KZSH, o.OFFEN, o.RECHNDATUM, o.MAHNSTUFE
FROM FIBU_OP1 o
WHERE o.KONTONR IN (/* DEBITORKTO aus 2.4 */)
```

Ob `OFFEN` den offenen Betrag oder ein Kennzeichen fuehrt, zeigt das erste Ergebnis. Danach wird das Profil-Mapping
(`OFFENBETRAG` -> `offener_betrag`) festgelegt. `BUCHUNGSTEXT`, `INFOTEXT` und `CMAHNTEXT` werden nicht gezogen.

### 2.6 Geschaeftsvorfaelle

Fuer den Belegabgleich je Belegkopf eine Zeile mit `TYP 'beleg'`. Die Abfrage setzt die VALEO-Belegart, z. B. fuer
Ausgangsrechnungen:

```sql
SELECT 'beleg' AS TYP, 'sales_invoice:' || r.RECHNUNGNR AS QUELLE, 'sales_invoice' AS BELEGART,
       r.RECHNUNGNR AS BELEGNR, r.RECHNDATUM AS DATUM, r.NETTO, r.BRUTTO
FROM WWS_ARECHNUNG1 r WHERE r.RECHNDATUM BETWEEN '2026-11-01' AND '2026-11-30'
```

Die Spaltennamen von `WWS_ARECHNUNG1` sind am Ergebnis zu bestaetigen; fuer die uebrigen Belegarten gilt dasselbe
Muster. In VALEO nachvollzogene Belege tragen `source_system = 'l3'` und `source_ref = <L3-Belegnummer>`.

Belegkoepfe und Positionen (`WWS_VERKAUF1/2`, `WWS_VLIEFER1/2`, `WWS_ARECHNUNG1-5`, `WWS_BESTELLUNG1-3`) werden nach
denselben Regeln gezogen: nur Belege der Beispielartikel und gezogenen Kunden, nur Nummern, Daten, Mengen und Betraege.
Die Uebernahme der Belege ist in VALEO noch nicht gebaut; die Abzuege werden bis dahin lokal aufbewahrt.

## 3. Ablage

Jede Abfrage einzeln in Calc oeffnen. Speichern als **CSV**: Zeichensatz UTF-8, Trenner Semikolon, Kopfzeile mit den
Spaltennamen. Dateiname `l3_abzug_<objektart>_<JJJJMMTT>.csv`, Ablage in `C:\VALEO-Testdaten\l3\`.

## 4. Einlesen

```bash
python scripts/l3_testdaten_import.py C:/VALEO-Testdaten/l3 --mandant l3-test
```

Das Skript prueft jede Datei auf Klartext. Danach legt es den Testmandanten und das Adapterprofil `l3_spiegel` an, nimmt
je Datei einen Batch an und durchlaeuft Staging, Abgleich und Freigabe. Am Ende ruft es Uebernahme bzw. OP-Abgleich auf.
Ausgegeben werden nur Zaehlwerte je Objektart (neu, geaendert, unveraendert, fehler) und die Fehlerarten. Feldinhalte
erscheinen nicht.

## 5. Loeschen

```bash
python scripts/l3_testdaten_import.py --loeschen --mandant l3-test
```

Das Skript entfernt alle Daten des Testmandanten aus Artikeln, Kunden, Partnern, Bestaenden und Adapterstrecke und
schreibt ein Loeschprotokoll mit Zaehlwerten. Die CSV-Dateien loescht die Person am Rechner.
