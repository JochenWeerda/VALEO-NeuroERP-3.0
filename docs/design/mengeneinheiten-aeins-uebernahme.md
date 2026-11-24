---
title: Mengeneinheiten nach a.eins - Uebernahme in VALEO
type: reference
audience: [entwickler, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.1.0
description: Fachliche Vorgaben der a.eins-Hilfe zu Mengeneinheiten (Grundmengeneinheit, Gebinde, Gebindetypen, Faktorherkunft, LVS) und ihre Uebernahme in VALEO.
---

# Mengeneinheiten nach a.eins - Uebernahme in VALEO

Nutzerauftrag 24.11.2026: "Uebernehme Vorschlaege zu Mengeneinheiten von https://www.amic.de/hilfe/ und den weiteren
Erklaerseiten fuer Mengeneinheiten im Landhandelsprogramm a.eins." Die Detailseiten der Hilfe sind nur ueber das
JavaScript-Menue erreichbar; ihr Inhalt wurde vom Nutzer eingefuegt. Diese Datei haelt die Vorgaben fest (sinngemaess,
mit den Feldnamen von a.eins) und ordnet sie VALEO zu.

Ergaenzt `docs/design/agrar-mengen-gebinde-modell.md` (Masse/Volumen global, Zaehleinheiten nur je Artikel, keine
Umrechnung ohne belegten Faktor) - beide Dokumente gelten zusammen.

## 1. Begriffe

| a.eins | Bedeutung | VALEO |
|---|---|---|
| Mengeneinheit | Daten zur Mengenermittlung: Text, Faktoren oder Rechenformel | `domain_shared.artikel_mengeneinheiten` |
| Grundmengeneinheit | kleinste, nicht weiter teilbare Einheit, auf die zurueckgerechnet wird (kg, Ltr., Stueck) | Zeile ohne Basiseinheit; `GRUNDEINHEITEN` in `app/services/mengeneinheiten_grund.py` |
| Ergebnismengeneinheit / Ergebniseinheit | Einheit, in der das Ergebnis einer Gebindeberechnung zurueckgegeben wird (Palette Dosen -> Liter) | offen (Schritt 2) |
| Mengeneinheitsgruppe | am Artikel: Mengengrundlage fuer Einkauf, Verkauf, Bestand, Preisfindung | `domain_shared.artikel_mengeneinheitengruppen` (bestand/ek/vk/preis) |

Erfassungsreihenfolge: erst Mengeneinheiten, dann die Gruppe am Artikel. Vor dem Speichern wird geprueft, ob die
benoetigten Grundeinheiten vorhanden sind.

## 2. Grundmengeneinheit - Felder (umgesetzt 24.11.2026)

| a.eins-Feld | Regel | VALEO-Spalte |
|---|---|---|
| Nummer | hoechstens 4 Stellen | `nummer` (1-9999, je Mandant eindeutig) |
| Kurztext | Druckbezeichnung (kg, Stueck, Ltr.) | `einheit_kuerzel` |
| ISO Name | - | `iso_name` |
| Langtext | statt Kurztext druckbar | `langtext` |
| Bezeichnung | fuer Auswahllisten | `bezeichnung` |
| DataNormKurz | fuer DataNorm-Datenaustausch | `datanorm_kurz` |
| Statistikkennzeichen | - | `statistikkennzeichen` |
| Rundung bei Umrechnung | 0 bis 4; bei aktiven Einheiten nur nach oben aenderbar (geschriebene Belege bleiben) | `dezimalstellen` (0-4, Regel im PUT: 409) |
| Mengeneinheit Preisbezug | Bestand in kg, Preis je 100 kg -> Preisbezug 100 | `preisbezug_einheit`, `preisbezug_menge` |
| UN-Mengeneinheit | UN/ECE Recommendation 20, fuer openTRANS und eRechnung | `un_code`; eRechnung liest zuerst den Stamm (`beleg_erechnung.einheit_code`) |

Mitgeliefert werden die gaengigen Grundeinheiten (a.eins: "werden als Grundeinheit mit ausgeliefert"):
`POST /api/v1/artikel/mengeneinheiten/stamm/grundeinheiten` legt fehlende an (Stueck C62, kg KGM, dt DTN, t TNE,
g GRM, l LTR, hl HLT, ml MLT, m MTR, m2 MTK, m3 MTQ, ha HAR, h HUR, Sack SA, Palette PF). Zaehleinheiten ohne Faktor.

## 3. Mengeneinheiten mit Gebinde (Schritt 2, offen)

Beispiel a.eins: Kartoffeln im 50-kg-Sack, Grundeinheit kg, Bestand in kg, Preis je Sack -> Gebindeumrechnung.

Kopfdaten: Nummer, Kurztext ("Sack"), Langtext, Bezeichnung ("Sack 50 kg"), **Grundmengeneinheit** (Rueckrechnung,
z. B. kg), **Ergebniseinheit** (Ergebnis der Gebindeberechnung), **Gebindetyp**, **Faktorherkunft**.

### 3.1 Gebindetypen

| Typ | Bedeutung | Rechnung | Beispiel |
|---|---|---|---|
| 0 | kein Gebinde | Anzahl Liefereinheiten = Anzahl Mengeneinheiten | - |
| 1 | lineares Gebinde (Anzahl) | Anzahl x Gebindemass 1 | 10 Sack a 25 kg = 250 kg |
| 2 | Gebinde 2. Stufe (Flaeche) | Anzahl x Mass 1 x Mass 2 | 10 Paletten a 24 Kartons a 6 Flaschen |
| 3 | Gebinde 3. Stufe (Volumen) | Anzahl x Mass 1 x Mass 2 x Mass 3 | 10 Behaelter a 5 x 3 x 2 m = 300 m3 |
| 4 | Addition | Anzahl x (Mass 1 + Mass 2) | - |
| 5 | Subtraktion | Anzahl x (Mass 1 - Mass 2) | Zaehlerstand alt - neu |
| 6 | Anbruch, aufgerundet (deaktiv) | ganzzahlig aufgerundetes Vielfaches von Faktor 1 (Packungsgroesse) | - |
| 7 | Anbruch, abgerundet (deaktiv) | ganzzahliges Vielfaches von Faktor 1 abzueglich Restmenge | - |
| 8 | Faktor1 x Faktor2 / Faktor3 | - | - |
| 9 | Faktor1 x Faktor2 x Faktor3 x Faktor4 | - | Paletten mit Lagen mit Kartons mit Dosen, artikelspezifisches Gewicht je Dose |

### 3.2 Faktorherkunft (Fachentscheid 24.11.2026, verbindlich)

Die Faktorherkunft ist die **konfigurierbare Einstiegsstufe** der Faktorsuche, keine globale Prioritaet. Gesucht wird
ab der eingestellten Stufe; bei "nicht gefunden" stets weiter unten. Speziellere Stufen oberhalb der eingestellten
werden nie beruecksichtigt:

| Faktorherkunft | Suchpfad |
|---|---|
| 1 Mengeneinheit | Mengeneinheit |
| 2 Artikelstamm | Artikelstamm -> Mengeneinheit |
| 3 Artikel | Artikel -> Artikelstamm -> Mengeneinheit |
| 4 Artikel-Auspraegung | Auspraegung -> Artikel -> Artikelstamm -> Mengeneinheit |

Beispiel Pflanzenschutzmittel mit Faktoren auf allen Stufen (ME 10 l, Stamm 20 l, Artikel 5 l, Auspraegung 1 l):
3 Kanister ergeben je nach Faktorherkunft 30, 60, 15 oder 3 Liter.

Faktorpflege nur auf Stufen im Suchpfad (a.eins: bei Herkunft Mengeneinheit sind die Faktoren im Artikel nicht
aenderbar) - `pruefe_faktorpflege` im Rechenkern, serverseitig anzuwenden, sobald die Stufen Faktorfelder haben.

Weitere Regeln des Rechenkerns `app/core/gebinde_rechnung.py`:

- Fehlend (`FaktorFehlt`, `FaktorsatzUnvollstaendig`) und ungueltig (`FaktorUngueltig`: keine Zahl, 0, negativ)
  sind getrennte Fehler. Ein fehlender Faktor wird nie durch 1 ersetzt.
- Der Faktorsatz wird als Ganzes von **einer** Stufe genommen; Faktoren verschiedener Stufen werden nicht gemischt.
  Ist der Satz der gefundenen Stufe unvollstaendig, wird das gemeldet, nicht weitergesucht. **Offen:** ob a.eins
  einzeln oder satzweise aufloest, ist in der Hilfe nicht belegt; die strenge Regel gilt, bis das geklaert ist.
- `berechne_gebinde` ist der eine Einstieg fuer Einkauf, Verkauf, Lager, Waage, Fakturierung und Bewertung und
  liefert ein Abbild (Typ, eingestellte und verwendete Herkunft, Faktoren, Anzahl, Rundung, Ergebnis) zum Festhalten
  im Beleg.

### 3.3 Weitere Felder (Tabreiter Allgemein/Zusatz)

Gebinde auf Stufe 2 eingebbar; effektive Menge eingebbar (Liter eingeben -> Anzahl Kartons); Anbruch-Behandlung
(normal, Anbruch, abrunden, aufrunden, aufrunden Stufe 2); Anzahlermittlung angebrochener Gebinde (mitzaehlen/nicht);
Preis unabhaengig von Faktoren (ja = Preis je Gebindeanzahl, nein = je Ergebnismenge); bei Mengeneingabe ersten Faktor
errechnen; Zwischenergebnis auf der Gebindemaske (nein/anzeigen/eingebbar); Rundungsstellen Menge/Gebinde;
Mengeneinheit Preisbezug (zusaetzliches Mengenfeld, wenn die gemessene von der berechneten Menge abweicht);
Gebindefaktoren 1-4 mit Einheit; Gebindetext; Gebinde aenderbar; Statistikkennzeichen; LVS-relevant; LVS-Default-
Lokalitaet.

### 3.4 LVS-relevant (eigene Eigenschaft, unabhaengig von der Faktorherkunft)

0 nicht relevant, 1 relevant, 2 buchend (relevant im Zusammenhang mit Buchen). Bei "buchend" darf eine Menge nur
einmal bestandswirksam werden - entweder ueber die ERP-Bestandsfuehrung oder ueber das LVS, nie ueber beide.

## 4. Stufenzuordnung zum VALEO-Artikelmodell (Stand 24.11.2026)

Analyse des Modells: VALEO fuehrt **eine** Artikelebene, `domain_inventory.articles` (Schluessel `(id, tenant_id)`).
Eine Artikelfamilie bzw. ein Artikelstamm darueber gibt es nicht, ebenso keine Varianten-/Auspraegungstabelle;
Warengruppen (`domain_shared.warengruppen` usw.) und Sorten (`agrar_sorten`) sind fachlich etwas anderes und keine
Gebindestufe.

| a.eins-Stufe | VALEO | Pflege |
|---|---|---|
| 1 Mengeneinheit | `domain_shared.artikel_mengeneinheiten` (Faktoren am Stammsatz) | ja |
| 2 Artikelstamm | kein Gegenstueck | **nein** - 422, bis fachlich zugeordnet |
| 3 Artikel | `domain_inventory.articles`, Fremdschluessel `(artikel_id, tenant_id)` | ja |
| 4 Artikel-Auspraegung | kein Gegenstueck | **nein** - 422, bis fachlich zugeordnet |

Keine parallele Stammdatenstruktur und kein freier Bezug: Faktoren der Stufe 3 haengen per zusammengesetztem
Fremdschluessel am Artikel und an der Mengeneinheit desselben Mandanten. Faktorherkunft 2 und 4 bleiben einstellbar;
ihr Suchpfad laeuft ueber die vorhandenen Stufen nach unten. **Offen:** Bedeutung von Artikelstamm und Auspraegung
in a.eins (Hilfeseite "Artikelstamm und Artikel - Uebersicht" angefragt), danach Zuordnung oder bewusster Verzicht.

## 5. Berechnungsabbild je Belegposition (Nutzervorgabe 24.11.2026)

- Jede geaenderte Berechnung einer Position ist eine **neue, unveraenderliche Version**
  (`domain_docflow.document_item_gebinde_abbilder`, nur anfuegen). `document_items.gebinde_berechnung` traegt die
  geltende Version.
- Bearbeitbar, solange der Beleg nicht verbindlich gebucht ist (z. B. Verwiegung aendert die Liefermenge). Ab Status
  `posted`, `completed`, `reversed`, `cancelled` sperrt die Datenbank (Trigger) - Korrektur nur ueber Storno.
- Gleiches Abbild erneut schreiben erzeugt keine Version (Wiederholung harmlos); parallele Schreiber laufen ueber die
  Zeilensperre der Position nacheinander.
- Storno und Retoure rechnen aus dem geltenden Abbild, nicht aus dem spaeter geaenderten Stamm.

## 6. Zuordnung VALEO und naechste Schritte

1. **Grundmengeneinheit** - umgesetzt (Migration `mengeneinheit_aeins_felder_20261124`, Stamm-Endpunkt, Studio-Maske
   `stammdaten/mengeneinheit`, Grundeinheiten, eRechnung aus dem Stamm).
2. **Gebinde-Rechenkern** - umgesetzt (`app/core/gebinde_rechnung.py`, PR #187): Gebindetypen 0-9, Suchpfade der
   Faktorherkunft, Fehlerarten, Pflegepruefung, Abbild fuer den Beleg.
   **Offen (Schnitt 2b):** Gebindefelder am Stamm (Gebindetyp, Ergebniseinheit, Faktoren 1-4, Faktorherkunft) mit
   serverseitiger Pflegepruefung; Abbild je Belegposition persistieren, damit historische Belege gegen spaetere
   Stammaenderungen geschuetzt sind; Anbruch- und Preisregeln.
3. **Mengeneinheitsgruppe** am Artikel an die Gebinde-Einheiten binden (Einkauf/Verkauf/Bestand/Preis).
4. **Offen:** LVS-Relevanz 0/1/2 als eigenes Feld der Gebinde-Mengeneinheit, Default-Lokalitaet; Ausschluss von
   Doppelbuchungen zwischen ERP-Bestand und LVS bei "buchend".
