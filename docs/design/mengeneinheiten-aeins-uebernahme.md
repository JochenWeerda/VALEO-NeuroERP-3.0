---
title: Mengeneinheiten nach a.eins - Uebernahme in VALEO
type: reference
audience: [entwickler, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
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

### 3.2 Faktorherkunft

Gibt an, auf welcher Stufe die Suche nach den Gebindefaktoren beginnt; bei "nicht gefunden" wird stets weiter unten
gesucht: 1 aus Mengeneinheit, 2 aus Artikelstamm, 3 aus dem Artikel, 4 aus Artikel-Auspraegung. Faktor in der
Mengeneinheit, wenn er oft wiederverwendet wird; Faktoren im Artikel, wenn das Rechenschema gleich, die Faktoren aber
verschieden sind. Im Artikel sind Gebindefaktoren nur eingebbar, wenn die Mengeneinheit das vorsieht.

### 3.3 Weitere Felder (Tabreiter Allgemein/Zusatz)

Gebinde auf Stufe 2 eingebbar; effektive Menge eingebbar (Liter eingeben -> Anzahl Kartons); Anbruch-Behandlung
(normal, Anbruch, abrunden, aufrunden, aufrunden Stufe 2); Anzahlermittlung angebrochener Gebinde (mitzaehlen/nicht);
Preis unabhaengig von Faktoren (ja = Preis je Gebindeanzahl, nein = je Ergebnismenge); bei Mengeneingabe ersten Faktor
errechnen; Zwischenergebnis auf der Gebindemaske (nein/anzeigen/eingebbar); Rundungsstellen Menge/Gebinde;
Mengeneinheit Preisbezug (zusaetzliches Mengenfeld, wenn die gemessene von der berechneten Menge abweicht);
Gebindefaktoren 1-4 mit Einheit; Gebindetext; Gebinde aenderbar; Statistikkennzeichen; LVS-relevant; LVS-Default-
Lokalitaet.

### 3.4 LVS-relevant

0 nicht relevant, 1 relevant, 2 buchend (relevant im Zusammenhang mit Buchen).

## 4. Zuordnung VALEO und naechste Schritte

1. **Grundmengeneinheit** - umgesetzt (Migration `mengeneinheit_aeins_felder_20261124`, Stamm-Endpunkt, Studio-Maske
   `stammdaten/mengeneinheit`, Grundeinheiten, eRechnung aus dem Stamm).
2. **Gebinde-Mengeneinheit**: Gebindetyp 0-9, Ergebniseinheit, Faktoren 1-4, Faktorherkunft (Mengeneinheit ->
   Artikelstamm -> Artikel -> Auspraegung) als Rechenkern in `app/core/agrar_units.py` (bisher nur lineare Gebindeleiter
   = Typ 1/2), Felder am Stamm, Anbruch- und Preisregeln. Die Disziplin "keine Umrechnung ohne belegten Faktor" bleibt.
3. **Mengeneinheitsgruppe** am Artikel an die Gebinde-Einheiten binden (Einkauf/Verkauf/Bestand/Preis).
4. LVS-Relevanz und Default-Lokalitaet mit dem WMS verbinden.
