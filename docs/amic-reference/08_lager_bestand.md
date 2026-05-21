# Lager, Bestände & Inventur — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (228 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Spalten für permanente Inventur in Warenbuch/Auswertung

Spalten für permanente Inventur in Warenbuch/Auswertung
Bei [WBAD] in der Variante ¨Warenbuchdetails für
Artikel¨ und in der Variante  ¨Warenbuchauswertung¨ in [WBA] sind
jeweils Spalten für Inventurmengen Plus und Minus für Mengen und Werte
eingetragen worden, die nur bei permanenten Inventur allgemein sichtbar und nur
bei PIV-Belegen gefüllt werden.
Releasenote Kategorie:
Ticket: 716520[33099]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Warenbuch
Variante: Warenbuchdetails für Artikel
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2211.30, 33099, 716520

---

## Artikelpfleger: Inventurgruppe

Artikelpfleger: Inventurgruppe
Mit der Umstellung auf den neuen Artikelpfleger wurde
die Inventurgruppe unter Umständen nicht richtig übernommen. Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 717098[33181]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Artikel
Variante: -
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33181, 717098

---

## Inventurstamm

Inventurstamm
Bei einem Inventurstammsatz vom Typ "Erhebung und
Stichtag versetzt" war es möglich das Feld Erhebungstag leer zu lassen. Dies
wurde unterbunden. Und rückliegende Inventuren werden korrekt behandelt.
Releasenote Kategorie:
Ticket: 717267[33277]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [IVS]
Variante: Inventurstamm
Funktion/Report: F8,F5
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 33277, 717267

---

## PIV-Belege Partien

PIV-Belege Partien
In Inventurbelegen der permanenten Inventur mit LVS
gibt es folgende Änderungen bei der Auflistung der Partien:  Es werden nur
Partien mit 0-Menge gelistet, wenn im LVS die Menge 0 gezählt, aber in der Ware
eine Menge ungleich 0 steht. Steht in beiden die Menge 0, so wird diese Partie
nicht mehr in den Beleg aufgenommen, da dadurch ohnehin keine Änderung
erfolgt.  Erledigte Partien werden jetzt auch mit der LVS-Menge (ggf. auch
0) gelistet, wenn in der Ware eine Menge ungleich 0 steht.   0-Mengen
werden jedoch nur eingetragen, wenn im SPA 1045 auch 0-Mengen erstellt werden
sollen. Dazu ist der Wert 1 zu setzen.
Releasenote Kategorie:
Ticket: 717473[33347]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Permanente Inventur Prüfungen
Variante: LVS ungezählte Artikel
Funktion/Report: Inventurbelege LVS erzeugen
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33347, 717473

---

## Permanente Inventur mit Lagerplätzen

Permanente Inventur mit Lagerplätzen
Bei der Nutzung der permanenten Inventur im
Zusammenspiel mit Lagerplätzen wurden die Bestände auf den Lagerplätzen nicht
korrekt aktualisiert.  Bei einem späteren WAREO wurden dann wieder die
korrekten Stände auf den Lagerplätzen hergestellt. Die Behandlung wurde nun
korrigiert.
Releasenote Kategorie:
Ticket: 716368[33574]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: PiV
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33574, 716368

---

## Dashboard: Erweiterung

Dashboard: Erweiterung
Im Balken- und Säulendiagramm besteht jetzt die
Möglichkeit, die einzelnen Serien zu überlagern.
Releasenote Kategorie:
Ticket: 716438[33659]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: [DASH]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2304.28, 33659, 716438

---

## Permanente Inventur und Belege am Erfassungstag

Permanente Inventur und Belege am Erfassungstag
Wird eine permanente Inventur auf einem Artikel
durchgeführt, so stellt der PIV-Beleg stets den letzten Stand des Tages dar. Aus
diesem Grund ist es nicht empfehlenswert nach Eingabe des Bestandsbeleges noch
Warenein- oder Ausgänge mit einem Lieferdatum vor oder am Inventurtag zu
erfassen. Dies sollte lediglich dann geschehen, wenn sichergestellt ist, dass
die genannte Ware tatsächlich vor der Zählung an-oder ausgeliefert wurde.
Bisher war dies sehr stringent geregelt. Die Änderung sieht folgende Szenarien
vor:  Anlieferung von Waren vor oder am Inventurtag erzeugen eine Warnung,
die dem Bediener die Möglichkeit gibt, das Lieferdatum zu ändern oder bewusst
beizubehalten mit dem Effekt, dass der Bestand nach Inventur nicht geändert
wird. In Nicht-Bestandsbelegen wie Angebot und Auftrag wird diese Warnung nicht
ausgegeben.  Die Meldung bezieht sich fortan auf das Lieferdatum der
Position - nicht mehr auf den Erfassungstag.
Releasenote Kategorie:
Ticket: 722169[33692]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33692, 722169

---

## Zählmenge wird auch vor der Bewertung angezeigt

Zählmenge wird auch vor der Bewertung angezeigt
Bei der Kalkulation werden nun auch Artikel
berücksichtigt wenn keine Zählmenge in der Inventur vorhanden ist.
Releasenote Kategorie:
Ticket: 722455[34004]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: Inventur Bestand
Variante: Zählbestand
Funktion/Report: Auswahlliste
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34004, 722455

---

## Anzeige Inventuraufnahme

Anzeige Inventuraufnahme
In der Anwendung Inventur-Aufnahme [IVA] wurde in der
Variante "Inventuraufnahme Artikel/Partie/LVS" die Darstellung der
Bewertung bei Gebindeartikeln berichtigt.
Releasenote Kategorie:
Ticket: 726126[34131]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Inventuraufnahme
Variante: Inventuraufnahme Artikel/Partie/LVS
Funktion/Report: Auswahlliste
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34131, 726126

---

## Erlöskennziffer bei Lagernummernwechsel

Erlöskennziffer bei Lagernummernwechsel
Bei Lagernummernwechsel auf einen Artikel mit
Erlöskennziffer 0 (Aus Artikelstamm) wurde die Erlöskennziffer bisher nicht
korrekt gezogen. Dies wurde nun behoben.
Releasenote Kategorie:
Ticket: 736743[35496]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: n/a
Variante: n/a
Funktion/Report: Lagernummernwechsel
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35496, 736743

---

## Wareo: Mengeneinheit

Wareo: Mengeneinheit
Beim Durchführen eines Wareo kam es zu einer
fehlerhaften Berechnung des Partiebestands, wenn ein Artikel in seiner
Mengeneinheitsgruppe keine Grundmengeneinheit als Lagermengeneinheit hatte. In
diesem Fall wurde der Partiebestand fälschlicherweise in die Grundmengeneinheit
der Lagermengeinheit umgerechnet. Dieses Verhalten wurde korrigiert: Nach einem
Wareo wird nun korrekt die in der Mengeneinheitsgruppe definierte
Lagermengeneinheit verwendet.
Releasenote Kategorie:
Ticket: 737555[35857]
Version: 9.0.2501.5
Datum:
Anwendung: Wareo
Variante: Wareo
Funktion/Report: Partiebestände reorganisieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35857, 737555

---

## Permanente Inventur angezeigte Menge

Permanente Inventur angezeigte Menge
Beim Vortrag der Permanenten Inventur in den
Inventurbeleg wurde das Feld, welches zur Anzeige der Menge verwendet wird,
nicht korrekt versorgt. Dies führte dazu, dass in der Inventurbewertung zwar die
richtige Zählmenge angezeigt wurde, jedoch nicht die korrekte Positionsmenge.
Dieses Verhalten wurde nun korrigiert. Das richtige Feld wird jetzt versorgt,
sodass die Menge der einzelnen Positionen der Zählmenge bzw. der
Bewertungszählmenge entspricht.
Releasenote Kategorie:
Ticket: 745118[36861]
Version: 9.0.2501.5
Datum:
Anwendung: Inventuraufnahme/-bewertung [IVA] [IVB]
Variante: Inventuraufnahme / Zählbestand
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36861, 745118

---

## Warnverhalten Permanente Inventur

Warnverhalten Permanente Inventur
Unter FRZ ist nun im Allgemeinen Tabreiter das PIV
Warnungsverhalten zu steuern.  Standartmäßig mit Einstellung 0 = Warnung
auf dem Bildschirm. (wie vorher) Neue Einstellungen:  1 = Warnung nur im
Fehlerprotokoll  2 = Warnung Ignorieren
Releasenote Kategorie:
Ticket: 741129[37121]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: FRZ
Variante: STD
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37121, 741129

---

## Anzeige von erfassten Permanenten Inventur Belege

Anzeige von erfassten Permanenten Inventur Belege
Wurden Inventurbelege in der Anwendung "Laufende
Inventur" [PIVB] erfasst und der Steuerparameter "1072-Bewertungsverhalten
permanente Inventur" auf "Keine Bewertung durch Bestandsbeleg"
gestellt, so wurden die erfassten Positionen der Inventurbelege nicht in den
Varianten "Partien" und "Artikel" angezeigt. Dieses Verhalten wurde jetzt
so korrigiert, dass die erfassten Positionen auch in den jeweiligen Varianten
angezeigt werden.
Releasenote Kategorie:
Ticket: 742234[37138]
Version: 9.0.2501.6
Datum:
Anwendung: Laufende Inventur [PIVB]
Variante: Artikel, Partien
Funktion/Report: Differenzbeleg erfassen
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.6, 37138, 742234

---

## Silo / Silobestand

Silo / Silobestand
In den Varianten „Silo“ und „Silobestand“ werden die
vorhandenen Silos angezeigt. Die beiden Varianten unterscheiden sich unter
anderem dadurch, dass unter „Silo“ die einzelnen Positionen der Silos angezeigt
werden, während unter „Silobestand“ die summierte Gesamtmenge pro Silo seit der
letzten Leermeldung angezeigt wird. Des Weiteren werden hier die aktuellen
durchschnittlichen Qualitätswerte und Netto- und Sekundärmengen zur jeweiligen
Gesamtmenge dargestellt.
Um Silos neu zu erfassen, muss – wie bei Ladeträgern –
erst ein Silotyp bzw.
Ladeträgertyp
erzeugt werden. Im
Artikelstamm muss dafür ein Silo-Eintrag erzeugt werden. Das Bruttogewicht
dieses Artikelstamms entspricht dann der Kapazität des Silos.
Durchschnittliche
Qualitätswerte und Netto-/Sekundärmengen zum Silobestand
Die in der Variante „Silobestand“ zu jedem Silo
dargestellten Qualitätswerte werden aus den einzelnen Zugängen, mit der
jeweiligen Bewegungsmenge gewichtet, in der Reihenfolge des Bewegungszeitpunkts
berechnet. Abgänge reduzieren dabei jeweils die für folgende Berechnungen
nötigen Mengen, ändern aber die zu ihrem Bewegungszeitpunkt berechneten
Qualitäten nicht. Gibt es für eine Zugangsbewegung zu einer Qualität keinen
erfassten oder bestimmten Wert, so geht die Menge dieses Zugangs in die
Berechnung nicht ein. Diesem Verfahren liegt die Annahme zu Grunde, dass für
einen ‚unbekannten‘ Qualitätswert einer Bewegung der bisher berechnete
Durchschnitt als Näherung angenommen wird. Dadurch wird ein statistisch
möglichst geringer Fehler impliziert. Für Zugänge aus einem anderen Silo wird
die Berechnung der Qualitäten der Bewegung per Rekursiv-Aufruf der
Berechnungsfunktion zum Bewegungszeitpunkt mit dem Quellsilo durchgeführt.
Als Start-Zeitpunkt zur Berechnung der
durchschnittlichen Siloqualitäten (zu einem Ziel-Zeitpunkt) wird grundsätzlich
die neueste vor dem Ziel-Zeitpunkt liegende Leermeldung zum Silo herangezogen,
es sei denn, es gibt mindestens eine
[...]


---

## Belege zum Bestellbestand

Belege zum Bestellbestand
Hauptmenü
Bestand
Artikel-Bestand
oder Direktsprung
[ARB]
In der Anwendung
Artikel-Bestand
wird diese
Auswahlliste zu einer markierten Zeile mit der Funktion
Belege zum
Bestellbestand
aufgerufen.
Hier werden, ausgehen vom aktuellen Wert des
Bestellbestandes, die einzelnen Belegpositionen dargestellt, die zum offenen
Bestellbestand beitragen. Die Darstellung erfolgt in zeitlich absteigender
Reihenfolge. Der darzustellende Zeitraum kann in der Bereichsauswahl im Feld
Ab Datum
angegeben werden.
Achtung:
Bei großen Datenmengen kann die
Einschränkung auf ein
weit zurückliegendes Datum
zu
langen
Laufzeiten
bei der Datenzusammenstellung führen.
Spalte
Erläuterung
Artikel-Nr
Artikelnummer des betrachteten
      Artikels
Lager
Lagernummer des betrachteten
      Artikels
VKL
Vorgangsklassennummer des zur
      Position gehörigen Vorgangs
VKlasse
Kurzbezeichnung der
      Vorgangsklasse
UKLf
Unterklassennummer des zur Position
      gehörigen Vorgangs
Ku/Lf
Kunden-/Lieferantennummer des
      Belegs
Datum
Vorgangsdatum
Belegnummer
Belegnummer des Vorgangs
Pos
Positionsnummer der
      Vorgangsposition
Offen
Menge, die zum offenen
      Bestellbestand beiträgt
Offen gesamt
Offene Bestelmenge bis
      einschließlich dieser Belegposition
ME
Mengeneinheit der dargestellten
      Bestellbestandswerte
Bereichsauswahl
Artikelnummer
Artikelnummer, wird bei Aufruf aus
      der markierten Zeile vorbelegt
Lagernummer
Lagernummer, wird bei Aufruf aus der
      markierten Zeile vorbelegt.
Ab Datum
Datum zur Eingrenzung des zu
      betrachtenden Zeitraums.
Funktionen
Bereichsauswahl/Filter
Öffnet die
      Bereichsauswahl-Maske
Archiv anzeigen
Handelt es sich in der markierten
      Zeile um einen archivierten Beleg, so kann mit dieser Funktion die Anzeige
      des Belegs im Archiv erfolgen.

---

## Artikel-Bestand

Artikel-Bestand
Hauptmenü
Bestand
Artikel-Bestand
oder Direktsprung
[ARB]
In der Anwendung
Artikel-Bestand
werden in
unterschiedlichen Auswahllisten-Varianten die aktuellen Bestände von Artikeln
dargestellt.
Die Hauptvariante
Artikelbestände
weist
pro Artikel und Lager alle wesentlichen aktuellen Bestandswerte aus:
Spalte
Erläuterung
Eigenware
Siehe
Definition von
      Eigenware
Verfügbar
Eigenware + bestellte Menge –
      disponierte Menge
Disp
Offene disponierte Menge
Bestellt
Offene bestellte Menge
Soll-Bestand
Sollbestand des Artikels
Voreinkauf
Offener Mengen aus
Voreinkauf
Vorverkauf
Offener Mengen aus
Vorverkäufen
Einlagerung
Definition von Kommission
Ware
Kommission
Siehe
Definition von
      Kommission
FremdeWare
Siehe Definition von
Fremdware
FremdesLager
Siehe Definition von
Fremdlager
EigeneWare
Siehe Definition von
Eigene
      Ware
EigenesLager
Siehe Definition von
Eigenes
      Lager
Nachhaltig
Nur
      bei gültiger Nachhaltigkeit-Lizenz:
nachhaltige Menge
Nicht Nachhaltig
Nur
      bei gültiger Nachhaltigkeit-Lizenz:
nicht nachhaltige Menge
Bereichsauswahl
Artikelnummer
Hier
      kann der Bereich der berücksichtigten Artikelnummern eingeschränkt
      werden.
Lagernummer
Hier
      kann der Bereich der berücksichtigten Läger eingeschränkt
      werden.
Artikel-Pool
Hier
      kann die Auswahl auf einen Artikel-Pool-Bereich eingeschränkt
      werden.
Warengruppe
Hier
      kann die Auswahl auf einen Warengruppenbereich eingeschränkt
      werden.
Fremdbestand
Optionen:
-
Alle
      Artikel
-
Artikel mit
      Fremdlagerbestand
-
Artikel mit
      Fremdwarebestand
-
Artikel mit Fremdlager-
      oder Fremdwarebestand
Ohne 0-Mengen
Bei
      dem Wert
‚Ja‘
in diesem Auswahlfeld werden nur Artikel
      berücksichtigt, die einen Eigenbestand aufweisen, der nicht 0 ist.
      .
Funktionen
Bereichsauswahl/Filter
Öffnet die
      Bereichsauswahl-Maske
Lagerplatzbestand
Ruft
      zum ausgewählten Artikel und Lager eine Auswahll
[...]


---

## Belege zum Dispobestand

Belege zum Dispobestand
Hauptmenü
Bestand
Artikel-Bestand
oder Direktsprung
[ARB]
In der Anwendung
Artikel-Bestand
wird diese
Auswahlliste zu einer markierten Zeile mit der Funktion
Belege zum
Dispobestand
aufgerufen.
Hier werden, ausgehen vom aktuellen Wert des
Dispobestandes, die einzelnen Belegpositionen dargestellt, die zum offenen
Dispobestand beitragen. Die Darstellung erfolgt in zeitlich absteigender
Reihenfolge. Der darzustellende Zeitraum kann in der Bereichsauswahl im Feld
Ab Datum
angegeben werden.
Achtung:
Bei großen Datenmengen kann die
Einschränkung auf ein
weit zurückliegendes Datum
zu
langen
Laufzeiten
bei der Datenzusammenstellung führen.
Spalte
Erläuterung
Artikel-Nr
Artikelnummer des betrachteten
      Artikels
Lager
Lagernummer des betrachteten
      Artikels
VKL
Vorgangsklassennummer des zur
      Position gehörigen Vorgangs
VKlasse
Kurzbezeichnung der
      Vorgangsklasse
UKLf
Unterklassennummer des zur Position
      gehörigen Vorgangs
Ku/Lf
Kunden-/Lieferantennummer des
      Belegs
Datum
Vorgangsdatum
Belegnummer
Belegnummer des Vorgangs
Pos
Positionsnummer der
      Vorgangsposition
Offen
Menge, die zum offenen Dispobestand
      beiträgt
Offen gesamt
Offene Dispomenge bis einschließlich
      dieser Belegposition
ME
Mengeneinheit der dargestellten
      Dispobestandswerte
Bereichsauswahl
Artikelnummer
Artikelnummer, wird bei Aufruf aus
      der markierten Zeile vorbelegt
Lagernummer
Lagernummer, wird bei Aufruf aus der
      markierten Zeile vorbelegt.
Ab Datum
Datum zur Eingrenzung des zu
      betrachtenden Zeitraums.
Funktionen
Bereichsauswahl/Filter
Öffnet die
      Bereichsauswahl-Maske
Archiv anzeigen
Handelt es sich in der markierten
      Zeile um einen archivierten Beleg, so kann mit dieser Funktion die Anzeige
      des Belegs im Archiv erfolgen.

---

## Partieumbuchung (EPA AUFBEREITUNG)

Partieumbuchung (EPA AUFBEREITUNG)
Bezeichnung
Standardwert
Erklärung
Abgangsartikel wertlos
zzzzz0
Abgangspartieanzeige
Rohware
Zielpartieartikel aktiv
      abfragen
Nein
Basislagerplatz
0
Bewertungstyp bei
      Produktionsbuchungen
ohne
      Verprobung
Bezeichnung der Mengeneinheit
      entnommene Menge
Lagerplatzverarbeitung
Nein
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein
Makroprozedur zur Buchung der
      Bewegungen
Aufbereitungsaatware
Mengeneinheiten aktiv
      abfragen
Nein
Mischungen zulassen
Nein
Buchungen erfolgen in
      Mengeneinheiten ohne Umrechnung
Nein
Nachkommastellen bei den
      Abgangsmenge
0
Nachkommastellen der übrigen
      Mengenfelder
2
Preisabfrage aktiv
Nein
Preisliste zur Vorbelegung des
      Saatartikels
0
Preisliste zur Vorbelegung des verw.
      Abgangs
0
Preisliste zur Vorbelegung des
      wertlosen Abgangs
0
Prozedur zur Bestimmung der
      Abgangszeilen
Aufbereitung_Abgang
Qualitätsdaten mit
      übernehmen
Nein
Bezeichnung der entnommenen
      Menge
Rezeptnummer dieser
      Produktion
0
Saatwarenartikel ________ oder
      AUSWEICH
2________
Saatwarenabfrage aktiv
      abfragen
Nein
Bezeichnung des
      Zielartikels
Maschinennummer für
      Scannerbetrieb
Erstes Feld ist die
      Zielpartienummer
Nein
Unterklassennummer bei
      Produktionsbuchungen
0
Bezeichnung des
      Lieferanten
Vorbelegung der Artikelnummer
      Abgang
Artikelzeile wertloser Abgang aktiv
      abfragen
Nein

---

## MaskenTitel (EPA Aufbereitung1)

MaskenTitel (EPA Aufbereitung1)
Bezeichnung
Standardwert
Erklärung
Abgangsartikel wertlos
zzzzz0
Abgangspartieanzeige
Rohware
Zielpartieartikel aktiv
      abfragen
Nein
Basislagerplatz
0
Bewertungstyp bei
      Produktionsbuchungen
ohne
      Verprobung
Bezeichnung der Mengeneinheit
      entnommene Menge
Lagerplatzverarbeitung
Nein
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein
Makroprozedur zur Buchung der
      Bewegungen
Aufbereitungsaatware
Mengeneinheiten aktiv
      abfragen
Nein
Mischungen zulassen
Nein
Buchungen erfolgen in
      Mengeneinheiten ohne Umrechnung
Nein
Nachkommastellen bei den
      Abgangsmenge
0
Nachkommastellen der übrigen
      Mengenfelder
2
Preisabfrage aktiv
Nein
Preisliste zur Vorbelegung des
      Saatartikels
0
Preisliste zur Vorbelegung des verw.
      Abgangs
0
Preisliste zur Vorbelegung des
      wertlosen Abgangs
0
Prozedur zur Bestimmung der
      Abgangszeilen
Aufbereitung_Abgang
Qualitätsdaten mit
      übernehmen
Nein
Bezeichnung der entnommenen
      Menge
Saatwarenartikel ________ oder
      AUSWEICH
2________
Saatwarenabfrage aktiv
      abfragen
Nein
Bezeichnung des
      Zielartikels
Erstes Feld ist die
      Zielpartienummer
Nein
Unterklassennummer bei
      Produktionsbuchungen
0
Bezeichnung des
      Lieferanten
Vorbelegung der Artikelnummer
      Abgang
Artikelzeile wertloser Abgang aktiv
      abfragen
Nein

---

## MaskenTitel (EPA DHINVERH)

MaskenTitel (EPA DHINVERH)
Bezeichnung
Standardwert
Erklärung
Addonfeld 1 (leer nein)
Addonformat 1
Addonfeld 2 (leer nein)
Addonformat 2
Addon in den Bewegungen
      speichern
Nein
Artikelnummer vorbelegt
Nein
Kennzeichen (Halle, Silo)
      aktiv?
Nein
Kontrollwert anzeigen
Nein
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein
mit
      Partieerfassung
Nein
vorhandene Partien
      anzeigen
Ja
Partiegültigkeitsdatum (TT.MM.JJJJ)
      oder leer
Neuanlage Partie erlauben (immer Typ
      4 = Artikelstamm)
Ja
Hinweis bei Neuanlage von
      Partien
Ja
Bei
      Neuanlage Partie Matchcode aus Bezeichnung vorbelegen
Ja
Partienummer immer mit 0 vorbelegen
      (=Neuerfassung)
Nein
Bei
      Neupartien ist der Matchcode die Partienummer
Nein

---

## Lager (EPA DHLAGST)

Lager (EPA DHLAGST)
Bezeichnung
Standardwert
Erklärung
Bezeichnung Anredefeld
Bezeichnung Name
Bezeichnung Straße
Bezeichnung Vorname

---

## Kontozuordnung Erlöskennziffer (EPA EKZZ)

Kontozuordnung Erlöskennziffer (EPA EKZZ)
Bezeichnung
Standardwert
Erklärung
Autofüllen
Nein
Sollen die Bestandsbewertungskonten
      auch angezeigt werden?
Nein
Auf
      der Maske können neben den Bestandskonten auch Bestandsbewertungskonten
      angezeigt werden.

---

## MaskenTitel (EPA INVERF)

MaskenTitel (EPA INVERF)
Bezeichnung
Standardwert
Erklärung
Automatische
      Belegnummernerzeugung
Ja
Automatische
      Belegzeilennummerierung
Ja
Belegnummernkreis
8000
Abfrage der Bewertung
Nein
Fremdbestand erlaubt
Nein

---

## Bargeldzählung (EPA KASSTURZ)

Bargeldzählung (EPA KASSTURZ)
Bezeichnung
Standardwert
Erklärung
Fremdwährungsbestand separat
      aufschlüsseln
Nein

---

## MaskenTitel (EPA PARTIEVERTEILDLG)

MaskenTitel (EPA PARTIEVERTEILDLG)
Bezeichnung
Standardwert
Erklärung
Beim
      Drücken von RETURN im Feld Menge wird in die nächste Spalte
      gesprungen
Nein
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein

---

## MaskenTitel (EPA POSITIONS_UMBU)

MaskenTitel (EPA POSITIONS_UMBU)
Bezeichnung
Standardwert
Erklärung
Buchungstyp der
      Produktion
2
Lagerplatzvorbelegung des
      Produktes
0
Mengenprüfung zur
      Warenposition
Ja
Unterklasse der
      Produktion
40
Nummer des zugehörigen
      Rezeptes
1

---

## Identass Inventur Test (EPA SCANNERID)

Identass Inventur Test (EPA SCANNERID)
Bezeichnung
Standardwert
Erklärung
SCANNER-ID
Maske simuliert einen Scanner mit
      Indentass Scanner Software. Der EPA soll die Scanner-IP darstellen und
      wiedergeben. Kann individuell eingerichtet werden.

---

## MaskenTitel (EPA UMPACKEN)

MaskenTitel (EPA UMPACKEN)
Bezeichnung
Standardwert
Erklärung
Abgangsartikel wertlos
000000000
Abgangspartieanzeige
Rohware
Basislagerplatz
0
Bezeichnung der Mengeneinheit
      entnommene Menge
Lagerplatzverarbeitung
Nein
Mischungen zulassen
Nein
Qualitätsdaten in Zielpartien mit
      übernehmen!
Nein
Bezeichnung der entnommenen
      Menge
Saatwarenartikel ________ oder
      AUSWEICH
2________
Saatwarenabfrage aktiv
      abfragen
Nein
Bezeichnung des
      Zielartikels
Bezeichnung des
      Lieferanten

---

## Waage Boxmanagement (EPA WAAGE_BOXMA)

Waage Boxmanagement (EPA WAAGE_BOXMA)
Bezeichnung
Standardwert
Erklärung
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Inventur

Inventur

---

## Lagerverwaltungssystem

Lagerverwaltungssystem

---

## Lagernummernänderung bei Standard-Teildisposition

Lagernummernänderung bei Standard-Teildisposition
Für die Teildisposition kann man eine automatische
Lageränderung unter [FRZ] im Register Abwicklung im Feld
‚Lageränderung bei
Teildisposition automatisch aus Vorgangslagernummer‘
aktivieren.
Setzt
man dieses für den Zielvorgang auf Ja, dann wir bei der Standard-Teildisposition
automatisch eine Lageränderung vorgenommen, wenn das Quelllager nicht dem Lager
des Vorgangs entspricht.
SPA 316
‚Teildisposition nur aus aktivem Lager‘
sollte auf Nein gesetzt sein, damit
das Auswahlfenster bei der Standard-Teildisposition alles Verfügbare anzeigt.
Das zugehörige
Behandlungsschema
wird unter [FRZ] im Register
Abwicklung eingegeben. Wurde dort keines ausgewählt, dann wird als Standard das
ausgelieferte Behandlungsschema Lagernummernwechsel verwendet.

---

## Permanente Inventur

Permanente Inventur
Die Permanente Inventur ist eine Form der
Bestandsaufnahme, die das HGB in engen Grenzen zulässt.
Bei einer permanenten Inventur ist es zulässig, Teile
eines Lagers aufzunehmen. Dabei muss sichergestellt sein, dass einmal im
Wirtschaftsjahr der gesamte Bestand erfasst und durch eine ordnungsgemäße
Buchführung fortgeschrieben wird.
Diese Vereinfachung ist besonders für Betriebe mit
hohen Beständen geeignet, die sich im Rahmen einer Jahresinventur nur schlecht
zählen lassen.
So wäre es z.B. möglich, je Monat jeweils 1/12 des
Lagerbestandes zu zählen.
Eine permanente Inventur setzt die „ordentliche
Bestandsfortschreibung mit elektronischen Mitteln“ ab dem Zeitpunkt der Zählung
bis zum Geschäftsjahresende voraus. Aus diesem Grunde ist eine permanente
Inventur abseits eines Lagerverwaltungssystems kaum denkbar.
Hinweis
Das Gesetz sieht jedoch auch Einschränkungen für Waren
vor, die einem erheblichen Schwund z.B. durch Verderb, Zerbrechlichkeit oder
Gewichtsverlust unterliegen oder von besonderem Wert sind.
Zu den gesetzlichen Rahmenbedingungen soll es an
dieser Stelle keine weitere Einlassung geben. Diese sind im Einzelfall selbst zu
prüfen.

---

## Verschieben einer Siloposition mit Lagerprüfung(SPA 1027)

Verschieben einer Siloposition mit Lagerprüfung(SPA 1027)
Mit diesem Steuerparameter kann eingestellt werden, ob
beim Verschieben einer Siloposition die Lagernummer des Zielsilos für den
Artikel maßgeblich ist.
Einstellung
Bedeutung
Ja
      (Standard)
Es
      wird immer das Lager des Zielsilos gewählt. D.h. Hat die zu verschiebende
      Artikelposition eine andere Lagerzuordnung als das Zielsilo, so findet ein
      Lagerwechsel statt. Die verschobene Position erhält die Lagernummer des
      Ziels.
Nein
Der
      zu verschiebende Artikel bleibt auf seinem Lager.

---

## Siloverarbeitung-Lizenz (SPA 1031)

Siloverarbeitung-Lizenz (SPA 1031)
Lizenz für die Siloverarbeitung.

---

## Ladeträgertyp Produktionssilo (SPA 1037)

Ladeträgertyp Produktionssilo (SPA 1037)
Wird die Produktion mit LVS in der Art geführt, dass
der Verbrauch aus Silos statt aus konkreten Ladeträgern abgebucht werden soll,
so ist pro Linie ein Sammel-Ladeträger eines Typs Produktionssilo zu erstellen.
Dieser Ladeträgertyp ist hier zu hinterlegen, damit exakt dieser Ladeträger (der
pro Lokalität eindeutig sein sollte) gefunden wird, um von dort den
Linienverbrauch abzubuchen.

---

## Lagerkopierer zulässig(SPA 104)

Lagerkopierer zulässig(SPA 104)

---

## Permanente Inventur mit LVS (SPA 1045)

Permanente Inventur mit LVS (SPA 1045)
Es gilt hier zwei Optionen einzustellen:
1.
Zählzeitraum in Tagen: Bei der permanenten Inventur schreibt der Gesetzgeber
vor, dass ein Artikel in einem eng begrenzten zeitlichen Zusammenhang zu zählen
ist. Dieser wird hier in Tagen definiert. Die Empfehlung ist, diesen Wert auf 1
zu setzen.
Wird dieser Wert auf 0
gesetzt, so gilt das Wirtschaftsjahr als Zählzeitraum.
2.
Anzahl der Zeilen im Inventurbeleg: Wird ein Inventurbeleg erstellt, so werden
pro Lager alle Zählprotokolle zusammengefasst, die noch nicht in einen Zählbeleg
eingeflossen sind. Damit dieser Beleg nicht unendlich groß wird, ist hier die
Möglichkeit gegeben, den Beleg auf eine definierte Zahl von Zeilen zu begrenzen.
Wir empfehlen einen Wert von max. 50.

---

## LVS Bay-Allokation (SPA 1050)

LVS Bay-Allokation (SPA 1050)
Dieser Steuerparameter legt fest, ob bei der
Allokation von Waren aus einem LVS-Blocklager vom Typ Lagerbucht (Bay) nur
allokiert werden soll, wenn die Ware ganz vorn erreichbar steht oder ob auch
allokiert werden soll, wenn die Ware von anderen Paletten verdeckt steht (In
diesem Fall müsste diese Ware zunächst umgelagert werden).

---

## LVS Bestandsbelege Vorgangsunterklasse (SPA 1057)

LVS Bestandsbelege Vorgangsunterklasse (SPA
1057)
Im LVS können Lagerumbuchungen in Ein- und
Ausgangsrechnungen als technische Bestandsbelege abgebildet werden. Wenn diese
erstellt werden, kann eine hier definierte Unterklasse verwendet werden.
Die gleiche Unterklasse wird für Belege der spontanen
Bestandskorrektur verwendet.

---

## Permanente Inventur Bewertungsmakro (SPA 1071)

Permanente Inventur Bewertungsmakro (SPA 1071)
Hier wird ein Makro definiert, das die Nachbewertung
der Inventurbelege der permanenten Inventur vornimmt und parametrisiert
dies.

---

## Tankdatenübernahme-Lizenz (SPA1102)

Tankdatenübernahme-Lizenz (SPA1102)
Lizenz für die Tankendatenübernahme.

---

## Fremdlager bei Inventur berücksichtigen (SPA 1117)

Fremdlager bei Inventur berücksichtigen (SPA 1117)
Bisher war bei der Inventur keine Möglichkeit
Fremdlagerware berücksichtig worden. Damit wurden bestände aus Voreinkauf und
Kommission nicht in den Anfangsbestand des neuen Jahres übernommen.
Um dies künftig zu machen, muss der SPA 1117 gesetzt
werden.

---

## Permanente Inventur besuchte Lagerplätze (SPA 1118)

Permanente Inventur besuchte
Lagerplätze (SPA 1118)
Dieser SPA entscheidet, welche Lokalitäten im
Wirtschaftsjahr als besucht gelten sollen.
•
Alle Lokalitäten, die im Wirtschaftsjahr im Rahmen einer permanenten
Inventuraufnahme besucht wurden
•
Alle Lokalitäten, auf denen im Verlauf des Wirtschaftsjahres Ware bewegt
oder inventarisiert wurde.

---

## Lagerplatzverwaltung aktiv(SPA 16)

Lagerplatzverwaltung aktiv(SPA 16)
Mit diesem Steuerparameter kann die
Lagerplatzverwaltung aktiviert / deaktiviert werden.

---

## Lagernummer auf der Bearbeitungs-Maske(SPA 163)

Lagernummer auf der Bearbeitungs-Maske(SPA 163)
Wenn Mehrlagerverwaltung aktiviert ist und einem
Vorgang von unterschiedlichen Lagern gebucht werden kann, hat er Bedeutung:
0 -ohne Lager
1 -nur Anzeige des Lagers (evtl. im Kopf erfassen)
2 -eingebbar, vorbelegt mit Standardwert
Vorgangskopf
3 -Einstieg in Positionsteil
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Lagerplatz-Automatik (ab Lieferschein)(SPA 196)

Lagerplatz-Automatik (ab Lieferschein)(SPA 196)
Hierbei handelt es sich um einen Schalter für einen
speziellen Kunden mit spezifischer Organisationsform. Es geht dabei um eine
Möglichkeit der automatischen Lagerplatzfindung, wenn noch kein Lagerplatz
zugeordnet war. Wenn eingeschaltet wird entweder der Lagerplatz mit dem größten
Bestand oder der Lagerplatz mit dem kleinsten Bestand, der noch in der Lage ist,
die geforderte Liefermenge zu bedienen, gewählt. Funktioniert nicht im
Zusammenhang mit Partie.

---

## Lagernummervorbelegung (SPA 260)

Lagernummervorbelegung (SPA 260)
SPA-Einstellungen
0 –
      nie vorbelegen
Die
      Lagernummer wird nie vorbelegt
1 –
      wie letzte Auswahl
Die
      Lagernummer wird aus den Vorgangskonstanten vorbelegt. Eine Änderung der
      Lagernummer ändert auch die Vorgangskonstanten (nicht empfohlen)
      **
2 –
      aus Vorgangskonstanten
Die
      Lagernummer wird bei jedem neuen Vorgang aus den Vorgangskonstanten
      vorbelegt. **
3 –
      aus VKONS b. Mehrbeleg wie vorheriger Vorg.
Die
      Lagernummer wird bei der ersten Erfassung aus den Vorgangskonstanten
      vorbelegt. Im Fall der Mehrbelegserfassung wird die letzte verwendete
      Lagernummer weiterverwendet. Eine Änderung der Vorgangskonstanten wie in
      Einstellung 2 findet jedoch nicht statt. **
** Bei Einstellung 1-3 – Es wird die Vorbelegung in
Abhängigkeit folgender Einstellungen vorgenommen, die einander (von oben nach
unten) überlagern können:
Einstellungen
Vorgangskonstanten
Die
      in [VKONS] eingetragene Lagernummer wird vorbelegt
WWW-Konstante des
      Bedieners
Im
      Bedienerstamm können sog. WWW-Konstanten definiert werden. Diese
      überlagern bei dem aktuellen Bediener die Einstellung in den
      Vorgangskonstanten
UFLD-Feld
Eingaben in einem UFLD-Feld
      überlagern sowohl die Vorgangskonstanten als auch die WWW-Kontante des
      Bedieners

---

## Typ-Vorbelegung bei Partieartikel-Anlage(SPA 277)

Typ-Vorbelegung bei Partieartikel-Anlage(SPA
277)
Zur Auswahl für die Vorbelegung des Feldes „Typ der
Zuordnung“ bei der Anlage von Partie-Artikeln stehen:
Artikel/Lager: Partien die mit diesem Typ der
Zuordnung angelegt werden sind an das angegebene Lager gebunden.
Artikelstamm: Partien die mit diesem Typ der Zuordnung
angelegt werden sind an kein Lager gebunden.

---

## Teildisposition nur aus aktivem Lager(SPA 316)

Teildisposition nur aus aktivem Lager(SPA 316)
Ja: Bei der Teildisposition zeigt das Auswahlfenster
nur Vorgänge mit dem gleichen Lager wie im Belegkopf an.

---

## Über-Disposition zulässig(SPA 32)

Über-Disposition zulässig(SPA 32)
Sollen Bestandsüberschreitungen bei Disposition
erlaubt sein?

---

## Warnung bei Bestandsüberschreitung(SPA 317)

Warnung bei Bestandsüberschreitung(SPA 317)
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Nullmenge bei Inventur zulässig(SPA 366)

Nullmenge bei Inventur zulässig(SPA 366)
Ist bei Inventur eine Nullmenge zulässig (J/N)?

---

## Lagerplatzumbuchung ohne Bewertung ab Jahr(SPA 389)

Lagerplatzumbuchung ohne Bewertung ab Jahr(SPA 389)
Tragen Sie hier bitte das Geschäftsjahr ein, ab dem
Lagerplatzumbuchungen nicht die Bewertung des Artikels verändern sollen.

---

## Vorbelegung Lagernummer in Objekt(SPA 390)

Vorbelegung Lagernummer in Objekt(SPA 390)
Wenn in diesem SPA eine Zahl verschieden von 0
eingetragen wird, ist das die Vorbelegung der Lagernummer in dem Objekt. Diese
Lagernummer des Objektes wiederum wird bei der Vorgangserfassung als Vorschlag
der Lagernummer der fakturieren Warenpositionen herangezogen.

---

## LGU und LGPU : Partien immer identisch(SPA 499)

LGU und LGPU : Partien immer identisch(SPA 499)
Bei „Ja“ wird bei Lagerumbuchungen und bei
Lagerplatzumbuchungen für Abgang und Zugang immer die identische Partie
eingetragen.

---

## Partiebehandlung bei Inventurerfassung(SPA 529)

Partiebehandlung bei Inventurerfassung(SPA 529)
ACHTUNG: Die Partieerfassung innerhalb der Inventur
darf zurzeit nur in Absprache mit Branchen-ERP aktiviert werden!!!
0 - Partien werden nicht behandelt
1 - Erfassung pro Artikel eine
Partieposition
2 - Mehrere Partien pro Artikel als Liste

---

## Nicht erhobene Partien bei Inventur prüf(SPA 543)

Nicht erhobene Partien bei Inventur prüf(SPA 543)
Nein: Bestände nicht erhobener Partien werden durch
Inventur nicht verändert.
Ja: Partiebestände werden hinsichtlich der Inventur
einer Vollständigkeitsprüfung unterworfen. Nicht erhobene Partien werden in
einer Differenzenliste nach Partien ausgewiesen. Die vollständige Erhebung aller
Partien wird bei Inventurabschluss sichergestellt und auch im
Periodenabstimmprotokoll ausgewiesen. Per Sonderfunktion (Inventureröffnung oder
Inventurabschluss) werden analog zur Nullsetzung in der Bestandsführung alle
nicht erhobenen Partien auf 0 gesetzt.

---

## Ordersatz-Artikel: Lager beibehalten(SPA 561)

Ordersatz-Artikel: Lager beibehalten(SPA 561)
Bei „Ja“ wird das Lager des Ordersatzes übernommen.
Bei „Nein“ wird nur die Artikelnummer übernommen, das Lager wird durch die
Lagernummerneinstellung des aktuellen Beleges ersetzt.

---

## Unterklasse aut. Lagerplatzumbuchung Partie(SPA 576)

Unterklasse aut. Lagerplatzumbuchung Partie(SPA 576)
Wenn die Lagerplatzverwaltung aktiv ist, wird bei
Partiezuordnungen mit abweichenden Lagerplätzen automatisch eine interne
Lagerplatz-Umbuchung erzeugt. Hier kann man die Unterklasse für diese Umbuchung
hinterlegen. Bitte dringend darauf achten, dass für alle Bedienerklassen
entsprechende Nummernkreis-Zuordnungen existieren.

---

## Automatische Lagerplatzumbuchung bei Partien(SPA 588)

Automatische Lagerplatzumbuchung bei Partien(SPA 588)
„Ja“ Bei der Partiezuordnung wird eine automatische
Lagerplatzumbuchung vom Lagerplatz der Partie zum Lagerplatz des fakturierten
Artikels erzeugt, falls diese sich unterscheiden.
„Nein“ diese Automatik entfällt

---

## Unterklasse für Fremdlager ausbuchen (SPA 601)

Unterklasse für Fremdlager ausbuchen (SPA 601)

---

## Bestandsführung mit STAMM ME(SPA 606)

Bestandsführung mit STAMM ME(SPA 606)
Ab Version 7 wurde der Partiebestand nur noch in
Lagermengeneinheiten geführt. Bei „Ja“ wird der Bestand jetzt laut Mengeneinheit
im Partiestamm geführt. Ist diese 0 so wird weiterhin die Lagermengeneinheit
benutzt.
ACHTUNG: Nach Umstellung dieses Steuerparameters
per WAREO der Partiebestand neu aufgebaut werden!

---

## Lagerplatzort aktiv(SPA 614)

Lagerplatzort aktiv(SPA 614)

---

## Bei Artikel-Auswahl Lagernummer prüfen (SPA 62)

Bei Artikel-Auswahl Lagernummer prüfen (SPA 62)
Ja: in der F3-Auswahlbox erscheinen bei Vorgängen nur
die Artikel auf dem gewählten Lager.
Nein: in der F3-Box erscheinen alle Artikel auf den
unterschiedlichen Lägern.

---

## Lagerverwaltungssystem(SPA 636)

Lagerverwaltungssystem(SPA 636)
Mit diesem Steuerparameter wird die LVS/Siloverwaltung
angestellt.

---

## Beleginfos bei aut.LPU Partie(SPA 665)

Beleginfos bei aut.LPU Partie(SPA 665)
Dieser Parameter regelt die Aufbereitung von
Beleginformationen bei automatisch erzeugten Lagerplatzumbuchungen bei Partien
Fremdlageranlieferung. Bei „Nein“ wird nur die Belegnummer des Originalbeleges
in die Referenznummer der Lagerplatzumbuchung eingetragen. Bei „Ja“ werden
zusätzliche  Informationen zur Kundennummer und der Vorgangsklasse
aufbereitet.

---

## Partiebestand mit Prod/LGU Dispo(SPA 674)

Partiebestand mit Prod/LGU Dispo(SPA 674)

---

## Unterklasse für Lief. Rech. Einlagerung(SPA 679)

Unterklasse für Lief. Rech. Einlagerung(SPA 679)
Hier kann eingetragen werden, welche Unterklasse die
Rechnung oder der Lieferschein bei der Einlagerung haben soll.

---

## Ordersatz: Lagerplatz übernehmen(SPA 685)

Ordersatz: Lagerplatz übernehmen(SPA 685)
Bei „Ja“ wird der Lagerplatz aus der Quellposition
übernommen, sofern dieser Lagerplatz im Ziellager vorhanden ist.

---

## Zuordnung eines Identass Scanner zur Inventurgruppe(SPA 809)

Zuordnung eines Identass Scanner zur Inventurgruppe(SPA 809)
Mit diesem Steuerparameter kann eingestellt werden,
welcher Scanner welche Inventurgruppe bearbeiteten darf.

---

## Lagernummer bei Washout oder Circle(SPA 837)

Lagernummer bei Washout oder Circle(SPA 837)
Mit diesem Steuerparameter kann eingestellt werden auf
welches Lager die Washout und Circle Vorgänge gebucht werden soll. Um ein
bestimmtes Lager auszuwählen muss der Parameter „Bestimmtes Lager verwenden“ auf
ja gestellt werden in das Feld „Lagernummer“ wird dann das Lager
eingetragen.

---

## Ausschalten der Silo / Ladeträgerverwaltung in der Waage(SPA 864)

Auss
chalten der Silo / Ladeträgerverwaltung in der
Waage(SPA 864)
Mit diesem Steuerparameter kann eingestellt werden, ob
der Ladeträger / Silo in der Waage mit dem Letzten erfassten Ladeträger / Silo
vorbelegt werden soll.

---

## Permanente Inventur Blockgröße (SPA 898)

Permanente Inventur Blockgröße (SPA 898)
Hier wird festgelegt, wie viele Positionen ein im
Rahmen der permanenten Inventur automatisch generierter Beleg maximal haben
darf. Vorschlag ist 20.

---

## Permanente Inventur-Lizenz(SPA 902)

Permanente Inventur-Lizenz(SPA 902)
Lizenz für die permanente Inventur.

---

## Automatische Artikelkopie in Ziellager (SPA 926)

Automatische Artikelkopie in Ziellager (SPA 926)
Sollen Artikel z.B. aus Vorgängen in ein Lager
aufgenommen werden, in dem diese nicht existieren, steuert dieser SPA, ob dies
automatisch passieren soll oder nicht.
•
Nein     = Keine automatische Übernahme
•
Ja        = Automatische Übernahme

---

## HTML-Seite als Vollbild(SPA 953)

H
TML-Seite als Vollbild(SPA 953)
Mit diesem Steuerparameter kann eingestellt werden, ob
die HTML-Seite die drei Kopfzeilen überlagert.
Einstellung
Bedeutung
Nein
Die
      Anzeige bleibt wie bisher
Ja
Die
      drei Kopfzeilen werden ausgeblendet und die HTML-Seite wird als Vollbild
      dargestellt.

---

## Anzeige des Silo trotz aktivem Steuerparameter Lagerverwaltungssystem(SPA 636) bei der Inventuraufnahme(SPA 950)

Anzeige des Silo tr
otz aktivem Steuerparameter
Lagerverwaltungssystem(SPA 636) bei der Inventuraufnahme(SPA 950)
Mit diesem Steuerparameter kann eingestellt werden, ob
das Feld zum Erfassen eines Silos / Ladeträgers auf der Inventuraufnahme Maske
angezeigt werden soll. Dies passiert nur in Abhängigkeit mit dem Steuerparameter
Lagerverwaltungssystem(SPA 636)
. Ist
dieser nicht auf „Ja“ gestellt, so hat dieser Steuerparameter keine Wirkung.

---

## Zahlungen mit der klassischen Zahlungsmaske

Zahlungen mit der klassischen
Zahlungsmaske
Dieses Modul wird in allen Kassen verwendet. In der
Marktkasse kann dieses Modul jedoch durch eine berührungsempfindliche
Zahlungssteuerung überlagert werden.
Hierzu kann nach Aufruf der Funktion aus den
unterschiedlichen unten angeführten Funktionen die für die Vorgangsbearbeitung
benötigte Belegart ausgewählt werden.

---

## Anlegen einer Partie über Partiestammdatenverwaltung

Anlegen einer Partie über
Partiestammdatenverwaltung
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Über die Funktion
Neu
F8
wird eine neue Partie angelegt.
Felder
Partienummer
Vorschlag einer automatischen
      Systemnummer, die überschrieben werden kann (über Mandantennummernkreis
[MNDNK]
wird ein Zählkreis den
      Partien zugeordnet)
Bezeichnung
Bezeichnung der Partie
Matchcode
Matchcode der Partie
Laufzeit
Zeitraum, in dem die Partie bebucht
      werden kann
Gesperrt
Gesperrte Partien können nicht
      bebucht werden. Durch private Varianten ist es möglich, gesperrte Partien
      zu selektieren.
Bestandsprüfung
      aussetzen
Wird
      die Bestandsprüfung ausgesetzt, dann wird beim Zuordnen der Partie nicht
      überprüft ob genügend Bestand vorhanden ist.
Qualitaetsstatus
Hier
      wird festgelegt, ob noch eine Qualitätsuntersuchung der Partie sinnvoll
      ist oder nicht.
Erledigung
Die
      Partie wird nicht zur Auswahl angeboten bzw. berücksichtigt.
Kundenbereich (Verkauf)
alle: alle Kunden können aus dieser
      Partie beliefert werden
Liste: Es kann eine Liste derjenigen
      Kunden aufgebaut werden die aus dieser Partie beliefert werden dürfen.
      Diese Eingabemaske wird per Knopf
Kunden
in der Optionbox
      geöffnet.
Lieferantenbereich
      (Eink)
alle: alle Lieferanten können dieser
      Partie liefern
Liste: Es kann eine Liste derjenigen
      Lieferanten aufgebaut werden die diese Partie liefern dürfen. Diese
      Eingabemaske wird per Knopf
Lieferanten
in der Optionbox
      geöffnet.
Warengruppenbereich
Es
      können Warengruppen dieser Partie zugeordnet werden, deren Artikel aus
      dieser Partie beliefert werden dürfen.
Fremdartikel zulässig
deaktiv
Fixpreise im Verk./Eink.
Es
      können Preise in den Partien hinterlegt werden, die bei der
      Vorgangserfassung für den Einkauf sowie den Verkauf automatisch
      vorgeschlagen werden.
Währung
Währung der
[...]


---

## Archiv Auslagerung

Archiv Auslagerung
Hauptmenü
Administration
Archiv
Administration
Archiv Auslagerung
Direktsprung
[FAAD]
Wie auch unter
Auslagerung Archiv
beschrieben befindet sich
eine Übersicht der entsprechenden Auslagerungen.
Das System ist ein Vorläufer der Container-Technik.
Letztere ist aber wesentlich umfangreicher und flexibler in der Handhabung und
Leistung und daher sollte die
Container
- Technik immer Vorrang
haben!

---

## Artikelstamm-Stoffstromdaten-Anpassung

Artikelstamm-Stoffstromdaten-Anpassung
Zum schnellen Einfügen von Bestandteilen mit
Stoffstrom-Kennung in die Zusammensetzungen mehrerer Artikelstamm-Einträge gibt
es eine lizensierte Funktion, die nach Auswahl betroffener Einträge in der
Standardauswahllistenvariante des Artikelstamm-Pflegemoduls zur Verfügung
steht.
Die gewünschten Bestandteile werden per Angabe der
Bestandteilnummer oder F3-Auswahl in der Spalte eingetragen und der jeweilige
Anteil nebst des Anteiltyps (0= ‚%‘ oder Mengeneinheitsnummer pro
Grundmengeneinheit der zum jeweiligen Artikelstamm gehörenden
Mengeneinheitsgruppe) angegeben. Möglich ist hier die Angabe von mehreren
Bestandteilen aus der Artikelbestandteil-Liste, die als Stoffstrombestandteil
gekennzeichnet sind.
Sollen für Artikelstamm-Zusammensetzungen, die bereits
den einen oder anderen hier angegebenen Bestandteil zugeordnet haben, die dort
bereits eingetragenen Werte für Anteil und Anteiltyp geändert werden, so ist im
Feld ‚
Ersetzen vorhandener Artikelstamm-Werte?‘
der Wert
Ja
anzugeben.
Bei Auslösen der Funktion durch Betätigen des Buttons
Bestandteile nachtragen
werden für alle in der Auswahlliste gewählten
Artikelstamm-Einträge die Zusammensetzung ergänzt beziehungsweise
geändert.

---

## Artikel löschen

Artikel löschen
Ein Artikel kann gelöscht werden, wenn er
•
Keinen Bestand hat
•
Nicht in einem nicht abgeschlossenen Geschäftsjahr bebucht wurde
•
Keine Inventurbestände hat
In diesem Fall kann der Artikel in der Auswahlliste
ausgewählt und mit F7 gelöscht werden.

---

## Registerkarte Bestand

Registerkarte Bestand
Bestandsinformation
Bedeutung
Inventurgruppe
Artikel können für Inventuren in
      Inventurgruppen gruppiert werden, um zum Beispiel die Jahresendinventur
      zum Inventur-Stichtag an unterschiedlichen Tagen (Erhebungstag) zu zählen.
      Dazu wird für jede Inventurgruppe zum Stichtag ein eigener Inventurstamm
      angelegt.
Bewertungsgruppe
Die
      Bewertungsgruppe legt die Bewertungsmethode zum Beispiel für die
      automatische Bewertung von Inventurpositionen fest.
Inventurabweichungsgr.
Permanente Inventur
Dieser Artikel wird mit einer
      permanenten Inventur erfasst.
Bestellpool kumuliert
Aufnahme Bestellpool
Aufnahme Bestellpool bei
      Makroeinspielung
Die Inventurgruppe eines Artikels kann mit der
Funktion
Inventurgruppenzuordnung
geändert werden. Hierzu wird auf der
Inventurgruppenmaske das Geschäftsjahr, ab dem die Änderung gelten soll, mit der
neuem Inventurgruppe eingetragen.
Ein Artikel lässt sich nur aus einer Inventurgruppe
entfernen und zu einer neuen hinzufügen, wenn:
1:         das
ausgewählte Geschäftsjahr noch nicht gesperrt oder abgeschlossen ist und
2:         es
noch keine Inventur-Bestandseinträge zum Artikel nach Jahresbeginn des
ausgewählten Geschäftsjahres gibt und
3a:       die
Inventurgruppe für einen Zeitraum ab Beginn des ausgewählten Geschäftsjahres
noch nicht eröffnet wurde oder
3b:       noch keine
Warenbewegungen für den Artikel vorhanden sind.
In Fall 3b) findet kein Inventurvortrag statt, da dies
für Artikel ohne Warenbewegungen im Allgemeinen nicht vorgesehen ist.

---

## Auslagerung Archiv

Auslagerung Archiv
Das Referenz-ERP-Archiv befindet sich bekanntermaßen
wohlbehalten im Referenz-ERP-Mandanten in der jeweiligen Datenbank. Gemäß keiner Regel
ohne Ausnahme kann es Umstände geben, die eine externe Haltung der binären Daten
notwendig machen:
1.
Das Aufkommen der Daten wird so groß, dass eine interne Haltung aller Daten im
Rahmen der Datenbank nicht länger sinnvoll erscheint.
2.
Belege können verjähren und müssen nicht fortwährend in der Datenbank gehalten
werden.
3.
Die Belege sollen Fremd-Systemen zur weiteren Verwendung übergeben werden.
4.
…

---

## Auswertung nach Gefahrgut

Auswertung nach Gefahrgut
Im Abschnitt Artikellisten kann gezielt nach
Gefahrgütern selektiert werden. So ist es z.B. möglich, die Gefahrgüter nach
Lagern auszuwerten.

---

## Übersicht Lager und Lagerplatz

Übersicht Lager und Lagerplatz
Referenz-ERP verwaltet Artikel auf unterschiedlichen Lagern
und Lagerplätzen. Lagerorte werden bei den Artikeln hinterlegt und stehen
hierarchisch über den Lagerplätzen. Zu einem Lager können mehrere Lagerplätze
gehören.
Bei der Vorgangserfassung lässt sich einstellen, ob
der Lagerort generell auf der Kopfseite abgefragt wird (UFLD-Feld) oder im
Warenpositionsteil zu jeder Artikelposition.
(SPA Vorgangsbearbeitung Warenposition
⇨
Lagernummer auf
Bearbeitungsmaske auf „JA“)
Das gleiche gilt für den Lagerplatz
(SPA Option
Warenwirtschaft
⇨
Lagerplatz aktiv auf „JA“)

---

## Bestanddaten referenzieren

Bestanddaten referenzieren
Hiernach und nicht früher ist es an der Zeit zu
überlegen, was mit den „Alt-Beständen“ in der Datenbank passieren soll. Vorgänge
die z.B. vor Einführung des Archivs erzeugt worden sind haben noch keine
Belegreferenznummer hinterlegt! Man hat mit der Funktion „Bestanddaten
referenzieren“ diese Alt-Bestände „nachreferenzieren“. Das Referenz-ERP-System nimmt
also für jede solche Identität obige jeweilige Datenbank-Funktion her, und
stellt sie mit dann ordnungsgemäßer Referenz-Nummer wieder ins System ein.
Der Schalter unter „Bestandsdaten“ entscheidet ob Sie
die tatsächliche Anpassung durchführen möchten oder nicht. Steht er auf „NEIN“
so wird nur die Anzahl der möglichen Datensätze ermittelt.
Für das obige Beispiel bedeutet dies nach Aufrufen der
Funktion „Bestanddaten referenzieren“ 30 Baustellen mit einer Referenznummer
gemäß den Regeln aus amic_fa_ref_bau versehen worden und das z.B. 253
Partiestammdaten darauf warten noch mit einer Referenznummer ausgestattet zu
werden.
Diese Anzahl hat einen vorgestellten Bindestrich um
sie von der tatsächlichen abgearbeiteten Anzahl abzuheben. Dieser Schalter wird
gespeichert damit man den Überblick behält welche Bestandsdaten man schon
abgearbeitet hat.

---

## Bestandsmeldung

Bestandsmeldung
Mit der Funktion
Bestandsmeldung
F10
können die Bestände überwacht und
verändert werden. Die Funktion stellt dafür drei Betriebsmodi zur Verfügung.
Bestandsübersicht
Wenn keine einzelnen Silos angewählt wurden, werden
die Füllstände der Silos graphisch dargestellt.
Bestandsmeldung
Wenn nur ein Silo angewählt wird, kann eine
Bestandsmeldung durchgeführt werden. Die Differenzmenge zu dem Alten Silobestand
wird als neue Position angefügt. Es wird der Artikel der ersten Position
gewählt. Wird ein Bestand von 0 angegeben so wird automatisch eine
Leermeldung
erzeugt.
Umbuchung
Wenn zwei oder mehr Silos angewählt werden, kann eine
Umbuchung durchgeführt werden. Die Umbuchung wird dabei vom ersten angewählten
auf das zweite angewählte Silo durchgeführt. Alle späteren angewählten Silos
werden ignoriert.
Bei der Umbuchung wird eine Position mit der
abzubuchenden Menge angefügt. Auch hier wird die erste Artikelposition
gewählt.
Des Weiteren besteht die Möglichkeit eine oder mehrere
Positionen von einem Silo auf ein anderes zu verschieben. Dazu werden die zu
verschiebenden Positionen per Doppelklick selektiert, und per Funktion
„Verschieben“ dann im Zeitverlauf ordnungsgemäß eingebucht.
Wird die komplette Menge von einem Silo auf ein
anderes Silo gebucht, so wird automatisch das Silo
leergemeldet
ohne das Waagenbelege angelegt
werden.
Verschieben
Um eine Position von einem Silo auf ein anderes Silo
zu Verschieben muss im linken Silo mindestens eine Position mit einem
Doppelklick markiert werden. Nach dem mindestens eine Position ausgewählt worden
ist, kann die Funktion
Verschieben
[F10]
ausgewählt werden. Dann werden
die markierten Positionen von dem ersten Silo auf das zweite Silo verschoben.
Auf dem zweiten Silo wird die Position als neue
Position an die Positionsliste angefügt. Ist noch keine Ladeeinheit auf dem Silo
vorhanden, so wird eine neue angelegt.
Position löschen
Es ist jetzt möglich eine Position vom Silo zu
löschen. Die Positi
[...]


---

## Bestände / Bewertung

Bestände / Bewertung
Der Artikel wird einer Inventurgruppe (s. dazu
Inventur
) sowie einer Bewertungsgruppe
zur Bestimmung des Bewertungsverfahrens für die laufende Bewertung zugeordnet.
Außerdem kann eine Inventurmengenabweichungsgruppe (s. dazu
Inventur
) zugeordnet werden.
Bestandsinformation
Bedeutung
Eigenbestand
Der
      Eigenbestand weist den im Eigentum befindlichen Bestand aus. Der Wert
      ergibt sich aus dem physisch anwesenden Bestand abzüglich der Fremdware
      (eingelagerte Ware, vorverkaufte noch nicht ausgelieferte Ware) zuzüglich
      externer Bestände (ausgelagerte Ware bzw. Kommisionsware, voreingekaufte
      aber noch nicht angelieferte Ware).
Fremd-Bestand EK
Summe der externen Bestände
      (Fremdlager), die durch Voreinkaufsvorgänge entstanden sind und noch nicht
      angeliefert wurden.
Kommission/Auslagerung
Summe der externen Bestände
      (Fremdlager), die durch Auslagerung z.B. als Kommissionsware entstanden
      sind.
Ist-Bestand
Der
      physisch anwesende Bestand im eigenen Lager inclusive der Fremdware
      (eingelagerte Ware, vorverkaufte noch nicht ausgelieferte
      Ware).
Fremd-Bestand VK
Summe der Bestände (Fremdware), die
      durch Vorverkaufsvorgänge entstanden sind und noch nicht ausgeliefert
      wurden.
Einlagerungen
Summe der Bestände (Fremdware), die
      durch Einlagerung entstanden sind.
disponierter Bestand
Summe der bereits disponierten
      Mengen (z.B. durch bestehende noch nicht ausgeführte Aufträge).
Die jeweils zugehörigen Korrekturmengen enthalten
Mengen, die bereits in Vorgängen erfasst, aber noch nicht durch den
Mandantenserver gebucht sind.
Neben der Anzeige der verschiedenen
Bestandsinformationen können Soll-, Mindest- und Meldebestand sowie
Bestellpoolangaben eingegeben werden (s. dazu
Bestellwesen
). In Bestellungen wird daraus nach
folgendem Algorithmus die zu bestellende Menge ermittelt:
Verfügbarer Bestand > Meldebestand: keine
Bestellung
Verfügbarer Bestand < M
[...]


---

## Bewegungen in der Partie

Bewegungen in der Partie
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Über diese Funktionen erhalten Sie eine detaillierte
Information über den Stand der einzelnen Partien. Bewegungen mit SOLL- und
IST-Zahlen, Laufzeiten, Status, Zeiträume für Mengen und Preise getrennt.
Weiterhin besteht die Möglichkeit, individuelle Listen
zu definieren und zu hinterlegen.

---

## Auswahlliste: Scanner Inventur Abgleicher

Auswahlliste: Scanner Inventur Abgleicher
Nach dem die Daten mit dem Scanner erfasst worden
sind, werden die Daten hier visualisiert. Fehlerhafte oder nicht übernommene
Daten werden in der Auswahlliste rot Markiert. Sind die Felder Belegnummer und
Belegposition nicht befüllt, so sind die Daten noch nicht in die Inventur
übertragen worden.
Artikelnummer
Farbe
Bedeutung
Rot
Der
      Artikel ist nicht auf dem Inventurlager
Weiß
Der
      Artikel ist Ordnungsgemäß erfasst worden.
Partienummer
Das Feld Partienummer hat noch weitere
Bedeutungen.
1.
Ist das Feld Partienummer leer, aber es wurde ein Partie mit dem Scanner
erfasst, so existiert zu der Partiebezeichnung keine gültige Partie.
2.
Ist das Feld Partienummer rot, und es existiert zu dem Artikel ein Eintrag in
der Inventur, so muss in dem dazugehörigen Inventurbeleg die Partie nach
getragen werden.
Farbe
Bedeutung
Rot
Die
      Partie ist nicht mit in den Inventurbeleg übernommen worden, obwohl diese
      mit dem Scanner erfasst worden ist und ein Eintrag im Inventurbeleg für
      diese Position existiert.
Weiß
1.   Die Partie ist
      Ordnungsgemäß erfasst worden und im Inventurbeleg vorhanden.
2.   Die Position ist noch
      nicht komplett in die Inventur eingespielt worden.
Inventurgruppe
Farbe
Bedeutung
Rot
Die
      eingetragene Inventurgruppe im Artikel existiert nicht.
Weiß
Die
      Inventurgruppe existiert.
Inventurstichtag
Farbe
Bedeutung
Rot
Es
      existiert keine offene Inventur zu der Inventurgruppe des
      Artikels
Weiß
Die
      Inventur ist offen.
Inventurdaten Nachspielen
Mit der Funktion „Inventurdaten Nachspielen“ können
noch nicht übertragene Positionen in die Inventur eingespielt werden. Es können
mehrere Einträge in der Auswahlliste ausgewählt werden. Befindet sich in der
Auswahl ein bereits übertragener Datensatz, so wird dieser nicht noch einmal
übertragen.

---

## Lagerverwaltungssystem

Lagerverwaltungssystem
Mit diesem Modul kann per Scanner Ware in das
Lagerverwaltungssystem
Ein- und Ausgebucht werden. Das
Lagerverwaltungssystem
ist an spezielle
Scannerprozesse angeschlossen worden. Das
Lagerverwaltungssystem
wird mit dem
Steuerparamter 636 eingeschaltet.
Als erstes müssen die
Scancodes
für das
Lagerverwaltungssystem
im Referenz-ERP System
eingerichtet werden.
Nach dem die Scancodes eingerichtet worden sind müssen
noch folgenden Einrichtungen vorgenommen werden.
Da die Abarbeitung der Lagerverwaltungsbefehle direkt
nach dem Erfassen muss, muss für jeden Scanner ein Worker gestartet werden. Der
Worker ist ein Referenz-ERP welches aus dem Bin Verzeichnis des Referenz-ERP gestartet
werden muss. Am besten wird sich zum Starten des Prozesses eine Batch Datei
angelegt. Der Aufbau der Batch Datei sieht wie folgt aus:
start aeins
welcome „sectionname“ -c eng=“Name des DB Servers“;dbn=“Name der
Datenbank“;uid=SCANNER1;pwd=Branchen-ERP;links=tcpip pda=lvs_verarbeitungsmodul
ScannerNummer=192.168.241.50
Wichtig dabei ist, das die Parameter pda auf
lvs_verarbeitungsmodul steht und der Parameter  Scannernummer hat den Wert
der IP-Adresse des Scanners der mit diesem Prozess kommunizieren soll. Bei n
Scanner müssen auch n Prozesse gestartet werden.
Als nächste muss auf jeden Fall der Pfad zur Datei
Aeins_Programmstart.vbs eingerichtet werden, dies passiert auf der
Registerkarte LVS
unter
dem Punkt
Serverstarten
.
In folgenden Modulen ist das Lagerverwaltungssystem
integriert worden
1.
Eingangslieferschein
2.
Auftrag /
Bestellung
3.
Produktion
4.
Inventur
5.
Lagerumbuchung
6.
Ladescheinbearbeitung
Damit die Scancodes in einem diesen Modulen zugelassen
werden, müssen auf der Registerkarte
Zugelassene
Scancodes
in der Variante Scancodes die Lagerverwaltungsmodule zugelassen
werden.
Folgende Scancodes sind auf jeden Fall zu
erschaffen.
1.
Ein Scancode für den Ladeträger. Für den Ladeträger wird der AI-Code 97 aus dem
Code 128 genommen. Beispiel 97001 97 ist der
[...]


---

## Fertig

Fertig
Jetzt starten wir die Scanner Software und erneuern
das Menü. Danach klicken wir auf „Artikel Info An“ und Scannen einen Artikel nun
erscheint die Lagernummer, Artikelnummer und die Bezeichnung auf dem Bildschirm.
Danach klicken wir auf „Artikel Info Aus“

---

## Inventur

Inventur
Vorbereitungsschritte
•
Als erstes müssen die Scancodes für die Inventur mit dem
Lagerverwaltungssystem eingerichtet werden. Dies sind IV [-106] für Inventur
Start undIVENDE[-107] für Inventur Ende. Des Weiteren sind die AI-Zuordnungen
für den Scancode einzutragen. (Beispiel mit Partie) Soll die Inventur ohne
Partie erfasst werden, so kann die Zeile mit dem AI-Code 10 weggelassen werden.
Mit dem Feld „Optional“ kann gesteuert werden, ob die AI in einem
Erfassungsblock erfasst werden muss.
•
Eine
Inventur
muss eröffnet
worden sein.
•
Es müssen zwei Scancodes im EAN 128 Codiert erstellt werden IV und
IVENDE
•
Aus den Scannertabellen sollten die Daten abgeschlossener Inventuren
gelöscht werden bevor die Erfassung einer neuen Inventur gestartet wird.
AI
Application
    Identifier
Gruppe
Typ
Optional
-30
Mengeneingabe per Hand
2
Nein
-6
UPC-A Code
1
Nein
-5
EAN-Code 8
1
Nein
-4
EAN-Code 13
1
Nein
1
EAN
      Nummer der Handelseinheit
1
Nein
10
Partie(Charge)
3
Nein
      / Ja
30
Menge in Stück (EAN128)
2
Nein
3100
Nettogewicht in Kilogramm (0
      Nachkomma) (EAN128)
2
Nein
3101
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
3102
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
3103
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
Abarbeitung der Inventur
Nachdem die Scancodes für die Inventur angelegt und
die AI-Zuordnung eigerichtet worden sind kann jetzt die Erfassung mit dem
Scanner erfolgen.
Erfassung
IV
      für den Beginn einer Inventur
Artikel mittels Scancode
Menge per Hand
Eventuell eine Partie mittels
      Scancode
IVENDE für das Ende eines
      Inventurblockes.
In einem Inventurblock können mehrere Positionen
erfasst werden.
Sind alle Daten erfasst worden, so wird die Aufnahme
der Inventur mit IVENDE beendet. Es empfiehlt sich die komplette
Inventuraufnahme mit dem Scanner in mehrere Blöcke aufzuteilen.
Nach dem Scannen des Befehls IVENDE werden die Daten
in die Inventur übernommen. Sobald das System anfängt die Daten zu ü
[...]


---

## IB_Box

IB_Box
FIELD Beschreibung
Was ist es genau
Lagernummer
Bezeichnung einer Spalte auf der
      Maske
Lagernummer
Ausgabewert des Select
      Statements
I4
Format des Feldes
2
Breite der Angezeigten Spalte auf
      der Maske
// Priv. SQL Text
IB_SCANNER_ANZEIGE
TITLE Vorgang auf dem CE Scanner-3
FIELD Lagernummer,Lagernummer,I4,2
FIELD Artikelnummer,artikelid,I4,8
FIELD Artikelbezeich,artikelbezeich,
char
,20
SQL
select TOP
:TOP start
at
:ZEILENNUMMER ar.Lagernummer,ar.artikelid,
ar.artikelbezeich
from
artikel ar
join
sekundschluessel sek
on
( ar.artistammid =
sek.sekudatenid
where
sek.sekugruppe = 2
and
sek.sekubegriff =
':SEKUNDS'
order by
ar.lagernummer
asc

---

## Labor

Labor
Vorgangsfunktions
      Übersicht
Starten der
      Laboranwendung
Daten eingeben
Beenden der
      Laboranwendung
Erklärung der
    Kopfzeilen
Die
      erste Zeile im Kopftext zeigt Inventur Anfang an
Die
      zweite Zeile zeigt die Probennummer an
Die
      dritte Zeile zeigt den Probensatz an
Unter dem Direktsprung Labor ein Verfahren anwählen
und dann „Labor Petrischale
Drucken“ auswählen. Dieser Ausdruck wird dann auf die
dazugehörige Petrischale
gedruckt. Mit dem Scanner lässt sich dann dieser
Scanncode einscannen und
auf dem Display erscheinen dann die Probennummer,
Satznummer und alle
dazugehörigen Wiederholungszählungen. Der Scanner
zeigt den erst
einzugebende Wert mit einem Sternchen an. Durch
Eingabe über die Tastatur
und bestätigen mit der „Eingabetaste“ wird der Wert an
das Labor Programm
übermittelt, und das Sternchen springt weiter zum
nächsten Wert der eingegeben
werden muss.
Befehle
Bedeutung
„.2“
eine
      Zeile nach oben
„.6“
ein
      Schritt nach rechts
„.8“
eine
      Zeile nach unten
„.4“
ein
      Schritt nach links
durch die Werte Tabelle navigiert werden.

---

## Einrichtung der Inventur mit dem Lagerverwaltungssystem

Einrichtung der Inventur mit dem Lagerverwaltungssystem
Bedingungen für die Inventur
1.
Alle Inventurgruppen mit einem Artikel im LVS müssen den gleichen Stichtag und
das gleiche Erfassungsdatum haben.
2.
Alle Artikel im LVS müssen einer Inventurgruppe zugeordnet sein.
3.
Es muss im Inventurstamm ein Nummernkreis für die Inventur hinterlegt worden
sein.
4.
Es muss ein LVS Verarbeitungsmodul je Scanner gestartet sein
Vorbereitungsschritte
•
Als erstes müssen die Scancodes für die Inventur mit dem
Lagerverwaltungssystem eingerichtet werden. Dies sind LVSIV [-147] für Inventur
Start und LVSIVENDE[-148] für Inventur Ende. Des Weiteren sind die
AI-Zuordnungen für den Scancode einzutragen.
AI
Application
    Identifier
Gruppe
Typ
Optional
-30
Mengeneingabe per Hand
2
Nein
-6
UPC-A Code
1
Nein
-5
EAN-Code 8
1
Nein
-4
EAN-Code 13
1
Nein
1
EAN
      Nummer der Handelseinheit
1
Nein
10
Partie(Charge)
3
Nein
30
Menge in Stück (EAN128)
2
Nein
3100
Nettogewicht in Kilogramm (0
      Nachkomma) (EAN128)
2
Nein
3101
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
3102
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
3103
Nettogewicht in Kilogramm
      (EAN128)
2
Nein
•
Um die Inventur zu beginnen werden im Inventurstamm [IVS]  neue
Inventuren für die einzelnen Inventurgruppen eröffnet.
•
Danach werden alle Inventuren unter Inventurvorbereitung ausgewählt und
der Haken bei Vortrag der Ladeträger mit Bestand gesetzt.
•
Jetzt  prüft das System ob die Bedingungen für alle Inventurgruppen
eingehalten worden sind. Ist dies der Fall, so werden die Daten in die Inventur
eingespielt. Es werden dabei die Tabellen InventurBeleg, InventurBelegPartie,
InventurBelegPartieLVS  gefüllt.  Des Weiteren werden in der
Protokolltabelle LVS_LE_PositionBewegung zwei Einträge je Ladeeinheit,
LadeeinheitsPosition  gemacht, die den Bewegungsstatus 1 für Menge
herunternehmen und den Bewegungsstatus 2 für den Inventurvortag bekommen. Wird
die Inventur gelöscht, so bekommt das
[...]


---

## Scanner Scancodes bearbeiten Modus

Scanner Scancodes bearbeiten
Modus
In der ersten Variante in [SCTCP] können die Standard
Einstellungen der Scancodes bearbeitet werden. Dazu wählen Sie den zu
bearbeitenden Scancode aus und drücken F5. In diesem Beispiel werden die
Funktionen anhand der Inventur erklärt.
Maskenfelder
Inhalt
Bedeutung
Scancode
IV
Dies
      ist der Scancodetext, der als EAN 128 verschlüsselt wird und zum Starten
      des Moduls eingescannt werden muss.
Scantyp
Inventur-Start
Dies
      ist das FS Format SCANAITYP. Dieses beschreibt um was für einen Scantyp es
      sich handelt.
Scancode Numerisch
-106
Die
      numerische Funktion die hinter dem Scancode 106 steht.
Registerkarte Allgemein
Maskenfelder
Inhalt
Bedeutung
AI
      Start
Ja
Ist
      der erste Scancode der eingescannt wird um die Inventur zu
      starten.
Vorgangserzeugung
Ja
Inventur ist eine
      Vorgangsklasse
Vorgangs Klasse
Inventur Aufnahme
Vorgangs Klasse 5001
Vorgangs Unterklasse
0
Vorgangsunterklasse
Füllen ohne Änderung
Nein
Wird
      nur im Zusammenhang mit dem LVS System gebraucht. Bedeutet wenn beim
      Auftrag erfassen eine Kiste gefüllt wird, dass das Füllen keine Änderung
      an der Position macht.
Startet Maschine
Nein
Wird
      nur im Zusammenhang mit dem LVS System gebraucht. Bedeutet dass der
      Vorgang, Kisten Füllen, Leeren und Wiegen darf.
Menüeintrag
Inventur Start
Eintrag für das Kontext Menü auf der
      Scanner Software
Benutzer
Hier
      können einzelne Benutzer eingetragen werden, die dieses Modul starten
      dürfen z.B. Scanner1
Private Itembox
Hier
      kann eine Private Itembox eingetragen werden, die die Daten auf dem
      Scanner anzeigt.
Lila
      Id
Wird
      nur bei der Vorgangs Erzeugung benötigt. Im Falle eines Lieferscheins,
      Auftrag kann noch ein Etikett ausgedruckt werden.
Druckerprofi Branchen-ERP
      Etikettendruck
An
      dieser Stelle kann das Druckerprofil für den Branchen-ERP Etikettendruck
      hinterlegt werden. Beim Drucken über
[...]


---

## Externe Relation Archiv erstellen

Externe Relation Archiv erstellen
Etwaige Massendaten der Relation Archiv machen eine
Auslagerung dieser Daten in eine extra dafür vorgesehene Datenbank von
Nöten.
Bevor Sie weitermachen kommen Sie bitte Ihrer
Sorgfaltspflicht nach und überzeugen sich, dass sie eine lauffähige Sicherung
der beteiligten Datenbanken haben, um im Bedarfsfalle möglicherweise auftretende
Problemfälle notfalls dadurch rückgängig machen zu können, dass Sie die
Sicherung einspielen können.
Schritt 1:
Dazu nehme man eine Kopie der aktuellen Datenbank.
Letztere sollte man mit dem „Nullsetzer“ bearbeiten (Nicht Archiv!),
anschließende Reorganisation wird auch hier empfohlen.
Schritt 2:
Richten Sie auf dem Datenbankserver eine System-ODBC
Verbindung zur Archiv-Datenbank ein.
Schritt 3:
Damit befindet sich die Relation Archiv schon in der
Zieldatenbank und kann somit abgebaut werden.
Drop table
archiv
Create
existing table admin.archiv at ‘archiv;;admin;Archiv’
Schritt4:
Führen Sie im Bedienerstamm die Funktion
Fremdserver Rechte zuordnen
aus.

---

## Fahraufträge

Fahraufträge
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Fahraufträge
Direktsprung
[LVSFA]
Es ist möglich, programmatisch Fahraufträge für einen
Ladeträger in die Tabelle „LVS_Ladetraeger“ einzutragen. Diese können dann die
Notwendigkeit eines Transports eines Ladeträgers zu einem bestimmten Ort
dokumentieren. Die Erledigung von Fahraufträgen geschieht durch eine
Datenbankfunktion im Rahmen einer Ladeträgerbewegung.
Die Datenbankfunktion kann im
Steuerparameter 947
als Option für einen leeren
Schlüssel angegeben werden. Eine Vorlage für diese Funktion finden Sie unter dem
Namen „AMIC_DEMO_ErledigeLVSFahrauftrag“.
Als Eingangsparameter erhält die Funktion die Nummern
des Ladeträgers und der Lokalität auf den der Ladeträger soeben bewegt wurde. Es
ist nun an der Datenbankfunktion zu entscheiden, ob eine exakte Übereinstimmung
oder ein anderes Regalfach des gleichen Regals o.ä. dem Anspruch genügt, den
Fahrauftrag als beendet zu kennzeichnen.
In regelmäßigen Abständen sollten Sie per Event die
Tabelle „LVS_Ladetraeger“ aufräumen lassen, um alte erledigte Aufträge nicht
unnötig lange zu sammeln. Als Vorlage für eine Aufräumenprozedur können Sie
„AMIC_DEMO_LVS_CLEANUPFAHRAUFTRAG“ ansehen.
Mit der Hilfe der Auswahliste können Sie sich die
anstehenden Fahraufträge ansehen und ggf. auch manuell auf erledigt setzen.

---

## Gesamtliste

Gesamtliste
Die Gesamtliste zeigt die Aktienbestandsentwicklung
der Aktionäre in einem Wirtschaftsjahr an. Hier kann man auf einen Blick sehen
welcher Aktionär wie viele Aktien über welchen Zeitraum in einem Wirtschaftsjahr
besessen hat. Aus diesem Grund können Aktionäre auch mehrfach angezeigt werden.
Folgende Daten zur Anzahl werden angezeigt: Aktionärsnummer, Nachname, Vorname,
Geburtsort, Straße, Postleitzahl, Ort, Stückaktien(Anzahl), Nominalwert, Wert,
Datum Eintritt, Datum Austritt. „Datum Eintritt“ gibt an, ab wann der Aktionär
dieses Aktienpaket besessen hat und das „Datum Austritt“ gibt an bis wann der
Aktionär dieses Aktienpaket besessen hat. Näheres zu den angezeigten
Eigenschaften finden Sie unter
Aktionäre
verwalten
.
Über
Bereich
/Profile
kann nach folgenden Kriterien eingeschränkt werden: Name,
Vorname, Aktionärsnummer (von, bis), Geburtsdatum (von, bis), Straße (von, bis),
Postleitzahl (von, bis), Ort, Vertreter, Status von, Status bis, Aktienanzahl
(von, bis), Wirtschaftsjahr.
Wird kein Wirtschaftsjahr als Selektionskriterium
angegeben, dann wird das aktuelle Wirtschaftsjahr für die Berechnungen
verwendet.
Dem Benutzer stehen hier folgende Funktionen zur
Verfügung:
•
(Aktionär)
Neu
[siehe
Aktionäre verwalten
]
•
(Aktionär)
Ändern
[siehe
Aktionäre verwalten
]
•
(Aktionär)
Ansehen
[siehe
Aktionäre verwalten
]
•
(Aktionär)
Löschen
[siehe
Aktionäre verwalten
]
•
Historische Tabelle
[siehe
Aktientransaktionen / Die
Historische Tabelle
]
•
Anteile
•
Kundenbescheinigung
•
Unternehmen verwalten
[siehe
Die Unternehmensdaten
einrichten/verwalten
]

---

## Hofliste-Details

Hofliste-Details
Diese Spezielle Auswahlliste kann zurzeit nur über die
Siloverwaltung
angezeigt
werden. Dazu muss in der Auswahlliste
Silo oder Silobestand
ein Datensatz markiert
werden. Es werden alle dazugehörigen Waagenbelege zu dem ausgewählten Silosatz
angezeigt. In dieser Variante stehen dann die gewohnten Waagen Funktionen zur
Verfügung

---

## Der Identass Inventur Test

Der Identass Inventur Test
Für die Identass Inventur ist es möglich eine private
Ableitung der Standard Scanner Prozedur einzurichten oder eine eigene private
Prozedur zu verwenden.
Um diese zu testen, oder auch um überhaupt zu testen,
besteht die Möglichkeit in der Mobilen Datenerfassung (MDE) mit der Funktion
Identass Inventur Test
Erfassungen vorzunehmen, ohne die Identass
Software zu verwenden. Hier ist einzig Referenz-ERP aktiv.
Im Vorfeld richten Sie die Steuerparameter 809 und 810
sowie den Externen Namen des Bedieners wie bereits beschrieben ein. Gleiches
gilt für die Einrichtung der Inventur und die Zuweisung über [VKONS].
Anschließend müssen Sie noch einen weiteren
Steuerparameter einrichten. Im Steuerparameter 801 halten Sie fest, welche
Prozedur verwendet werden soll. Hier haben Sie folgende Möglichkeiten:
-
Nein
-
Private Prozedur
-
Indentass Inventur
Wählen Sie die gewünschte Einstellung und weisen Sie
dieser dann die Scanner IP zu. Wird eine private Prozedur verwendet, so tragen
Sie den Namen der Prozedur in das vorgesehene Feld des Steuerparameters ein.
Mit dem Funktionsaufruf für den Identass Inventur Test
starten Sie eine neue Maske. Diese Maske simuliert den Scanner. Sie erkennen
mehrere Felder.
Feld
Wert
Zeit
      in ms
Benötigte Zeit in Millisekunden für
      Bearbeitung des Scann Vorgangs.
Artikel EAN
Eingabe einer Artikel EAN über ein
      geeignetes Eingabegerät (Scanner, Tastatur, usw.).
Menge
Angegebene Menge
Fehlercode
Zeigt eine Fehlernummer an. Die Null
      (0) steht für OK.
Fehlertext
Zeigt den Fehlertext zur
      Fehlernummer an. Bei Fehlercode Null (0) erscheint hier die Artikelnummer
      und dessen Bezeichnung.
Diese Daten können je nach
      Verwendung privater Prozeduren abweichen!
Öffnen Sie nun zunächst die Einrichterparameter und
geben für den Parameter „Scanner-ID“ den passenden Wert ein, den Sie auch in das
Feld
Externer Name
und in den Steuerparametern verwenden.
Nun ist die Testmaske für Ihre Tests ei
[...]


---

## Das Inventur Programm auf dem Scanner

Das Inventur Programm auf dem Scanner
Auf dem Desktop des Scanners befindet sich ein Icon
mit dem Namen Inventur. Das Programm verlangt nach Eingabe von Benutzernamen und
Passwort. Im Anschluss gelangen Sie in das Hauptmenü. Hier wählen Sie Inventur
aus.
Inventur:
Feld
Wert
Artikel
Hier
      wird nach dem Scan die Artikelbezeichnung des gescannten Artikels
      angezeigt.
Menge
Über
      die Eingabe muss die entsprechende Menge angegeben und bestätigt
      werden.
Freifeld
Ausgabe von
      Fehlermeldungen
Weiter
Führt den angegebenen
Datenbankbefehl
aus
Um das Programm zu verlassen, wählen Sie im Hauptmenü
„CLR-Abbruch“. Wählen Sie nun bei Benutzer „Beenden“ aus und verwenden Sie das
Passwort: 95159. Nach dem bestätigen der Daten wird das Programm verlassen.

---

## Nachbearbeiten von fehlerhaften Scans

Nachbearbeiten von fehlerhaften Scans
Hauptmenü
Inventur
Inventuraufnahme
Funktionsmenü: Mobile Datenerfassung
Direktsprung
[IVA]
oder
Hauptmenü
Externe Kommunikation
Mobile Datenerfassung
Direktsprung
[MDE]
Beim Scannen mit der Identass Inventur Software und
mit der Einstellung im Steuerparameter 810 die MDEUebergabe mit zu verwenden,
landen fehlerhafte Scans in der Mobilen Datenerfassung [MDE].
Diese können in der Auswahlliste markiert und mit F5
oder der Funktion „Ändern“ im Funktionsmenü bearbeitet werden. Die Funktionen
„Ansehen“ und „Löschen“ erklären sich selbst.
Feld
Wert
Beleg
Enthält die Belegnummer der
      Auswahl.
Artikelnummer
F3
      Feld.
Enthält die Artikelnummer des
      gescannten Artikels. Fehlt dieser Wert, so kann er über F3, welches eine
      Eingrenzung auf die Artikel-EAN vornimmt, ausgewählt werden.
Menge
Enthält die gescannte oder
      angegebene Menge. Kann an dieser Stelle auch korrigiert
      werden.
Status
Enthält den Status der
      Auswahl.
Wird
      ein Datensatz mit dem Status „verarbeitet“ ausgewählt, so können keine
      Änderungen vorgenommen werden.
Der
      Status wird beim Speichern und bei korrekter Angabe der Daten von
      „fehlerhaft“ auf „unverarbeitet“ gesetzt.
EAN
Enthält die gescannte
      Artikel-EAN.
Lager
Enthält die Lagernummer. Fehlt diese
      in der Auswahl, wird sie bei der Auswahl der Artikelnummer vom
      ausgewählten Artikel übernommen.
Wenn Sie die Anpassungen an den fehlerhaften Daten
vorgenommen haben können Sie diese über die „Übernahme MDE“ in die Inventur
übernehmen.

---

## Inventur

Inventur
Hauptmenü
Inventur
Allgemeines
Referenz-ERP bietet vielfältige Möglichkeiten, die Inventur
organisatorisch zu unterstützen. Von der Gesamtinventur zu einem festen Stichtag
über abschnittsweise Teilinventuren reicht die Vielfalt dieses Systems.
Es gibt im Moment 2 Inventurarten:
-
Hauptinventur zum Jahreswechsel
-
Zwischeninventur
Für jede Inventur können Erhebungstag und Stichtag
versetzt sein. Die am Erhebungstag festgestellte Differenz wird auf den Stichtag
fortgeschrieben.
Durch eine Eintragung der Inventurgruppe im Artikel
(Hauptmenü
Stammdatenpflege
Artikel oder Direktsprung
[AR]
, dann
Ansehen
F5
Bestände
/ Bewertung
) kann bestimmt werden, welcher Artikel zur Inventur
herangezogen werden soll.
Standardmäßig ist bei allen Artikeln die “
0
” vorbelegt (bedeutet in der
Basisdatenbank = “Standardinventur“).
Bevor mit der Inventur begonnen werden kann, müssen
einige organisatorische Maßnahmen durchgeführt werden und alle Artikel mit einer
gültigen Inventurgruppe
belegt werden.
Ein Ändern der Inventurgruppe ist nicht sinnvoll und
kann nur durchgeführt werden, wenn alle Hauptinventuren gelöscht wurden oder
wenn noch keine Inventur eröffnet wurde.

---

## Beispiel Scancodes für die Inventur

Beispiel Scancodes für die
Inventur

---

## Inventur im Scanner

Inventur im Scanner
Zu diesem Bereich gehören die Offline und die Online
Inventur. In beiden Fällen ist darauf zu achten, dass es eine gültige Inventur
gibt. Es ist darauf zu achten, dass dem Bediener auch das richtige Lager unter
[vkons] zugewiesen wurde.

---

## Inventurstamm

Inventurstamm
Hauptmenü
Inventur
Inventurstamm
Direktsprung
[IVS]
Beschreibung
Im Inventurstamm wird die Inventur im Detail
definiert.
Auswahlliste Inventurstamm
Feld
Beschreibung
Vorläufig eingespielt
Kennzeichnung für Inventuren, die
      bereits vorläufig eingespielt worden sind. Dies ist auch für noch nicht
      abgeschlossene Inventuren möglich.
Stichtag
Stichtag der Inventur, also der
      letzte Tag des abzuschließenden Zeitraums.
Inventur
Bezeichnung der Inventur
Gruppen-Nummer
Die
      Nummer der Inventurgruppe, wie im Artikel hinterlegt.
Gruppen-Bezeichnung
Bezeichnung der
      Inventurgruppen
Aufnahmedatum
Erhebungstag der Inventur, wenn es
      sich nicht um eine permanente Inventur handelt, bei der der Erhebungstag
      je Artikelbestand variieren kann. Bei permanenter Inventur erster Tag der
      Erhebung.
Eröffnungsvortrag
Kennzeichen, ob Eröffnungsvortrag
      gelaufen ist.
Permanente Inventur
      vorgetragen
Vortrag durch die permanente
      Inventur
Abgeschlossen
Kennzeichnung, ob die Inventur
      abgeschlossen ist. Nur als abgeschlossene, gekennzeichnete Inventuren
      können endgültig eingespielt oder (bei Zwischeninventuren) gelöscht
      werden.
Vorläufig eingespielt
Kennzeichnung für Inventuren, die
      bereits vorläufig eingespielt worden sind. Dies ist auch für noch nicht
      abgeschlossene Inventuren möglich.
Löschkennzeichen
Kennzeichnung für gelöschte
      Inventuren; Sämtliche Inventurbelege sind dann beseitigt, nur der
      Inventur-Stammsatz bleibt als Nachweis, dass es diese Inventur mal gegeben
      hat, erhalten.
Typ
Typ
      der Inventur:
1 =
      Hauptinventur mit Jahreswechsel
2 =
      nicht aktiv
3 =
      Zwischeninventur
4 =
      Kontrollinventur (ohne Buchung)
Suchmöglichkeiten Inventurstamm
Feld
Beschreibung
Inventuren
Von…
      Bis…
Inventurgruppe
Id
Funktionen Inventurstamm
Funktion
Beschreibung
Ändern
(F5)
, Ansehen
(F6)
, Löschen
(F7)
, Neu
(F8)
Öffnet den
      Inv
[...]


---

## Inventurstamm - Pfleger

Inventurstamm - Pfleger
Hinweis
Folgende Angaben sind wichtig:
Inventurgruppe:
1
Inventurstichtag:
Erhebungsdatum
Bezeichnung:
Freier Text
Typ der
Inventur:           1
(Hauptinventur mit Jahreswechsel)
Art der
Inventur:            1
(oder 2)
Erhebung
am:
Erhebungsdatum
Felder des Inventurstamm-Pflegers
Identifikation
Feld
Beschreibung
Gruppe
Hier
      wird bestimmt, für welche Inventurgruppe die Inventur erfolgen
      soll.
Z.
      B. 1 = Hauptinventur JW, 10 = Teilinventur WG 10, 20 = Teilinventur WG
      20
Stichtag
Datum, zu dem die Inventur erfolgen
      soll.
Information
Feld
Beschreibung
Eröffnungsvortrag
Das
      Auswahlfeld gibt an, ob Eröffnungsvortrag gelaufen ist.
Vorläufig eingespielt
Das
      Auswahlfeld für Inventuren gibt an, ob die bereits vorläufig eingespielt
      worden sind. Dies ist auch für noch nicht abgeschlossene Inventuren
      möglich.
Abgeschlossen
Die
      Kennzeichnung, ob die Inventur abgeschlossen ist. Nur als abgeschlossene,
      gekennzeichnete Inventuren können endgültig eingespielt oder (bei
      Zwischeninventuren) gelöscht werden.
Eingespielt
Das
      Auswahlfeld, ob die Inventur bereits endgültig eingespielt worden ist. Das
      kann nur bei abgeschlossenen Inventuren der Fall sein.
Eingespielt am
Tag
      der Inventureinspielung
Gelöscht
Kennzeichnung für gelöschte
      Inventuren; Sämtliche Inventurbelege sind dann beseitigt, nur der
      Inventur-Stammsatz bleibt als Nachweis, dass es diese Inventur mal gegeben
      hat, erhalten.
Allgemein
Feld
Beschreibung
Bezeichnung
Freier Text für die Beschreibung der
      Inventur
Typ
      der Inventur
1
– Jahreswechselinventur
Es
      werden Bestandsbuchungen (mengen u. wertmäßige Ein- / Ausbuchungen)
      erzeugt, und für das neue Wirtschaftsjahr vorgetragen.
2
– Zwischeninventur
Durch die Aufnahme kann der
      Inventurbestand mit dem Buchbestand abgeglichen und eventuelle Diff
[...]


---

## Ladeeinheiten

Ladeeinheiten
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Ladeeinheiten
Direktsprung
[LVSLE]
Eine Ladeeinheit wird immer
dann angelegt wenn eine Position auf einen
Ladeträger
/ Silo gebucht werden soll, wenn dieser
noch keine Ladeeinheit hat.
Zurzeit kann einem
Ladeträger nur eine Ladeeinheit zugewiesen werden. Aber eine Ladeeinheit kann
mehrere Positionen haben.

---

## Ladeträger Buchungen

Ladeträ
ger
Buchungen
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Ladeträger
Direktsprung
[LVSLT]
Mit dieser Erfassungsmaske
können einzelne Positionen von einem Silo/Ladeträger gelöscht werden. Ein
Silo/Ladeträger kann auf eine Lokalität gefahren werden. Des Weiteren kann die
Menge an einer Position auf dem Ladeträger geändert werden.
Datentabelle Ladeträgerübersicht
Erfassungsfeld
Bedeutung
Ladeträgernummer/Silo
In diesem Feld wird die
      Ladeträgernummer/Silo angezeigt. Per F3 Auswahl kann zwar ein neuer
      Ladeträger/Silo hinzugefügt werden, da in der Positionsübersicht nicht die
      einzelne Position angezeigt werden, sollte man immer den Ladeträger/ Silo
      in der Auswahlliste auswählen und dann per F9 diese Maske starten.
Menge
In diesem Feld kann eine Menge
      angegeben werden, diese kann dann per Funktion auf die ausgewählte
      Position in der Positionsübersicht gebucht werden. Hierbei ist zum
      Empfehlen nur ein Silo/Ladeträger in der Auswahlliste
      auszuwählen.
Gewicht
In diesem Feld wir das Bruttogewicht
      des Ladeträgers aus dem Artikelstamm angezeigt.
Lokalität/Silostand
In diesem Feld wird die
      Lokalität/Silostand angezeigt auf welchem sich der Ladeträger oder das
      Silo gerade befindet. Die Lokalität/Silostand kann in diesem Feld
      verändert werden und mit der Funktion Ladeträgerbewegung / Silobewegung
      wird dann der Ladeträger / Silo auf diese Lokalität / diesen Silostand
      umgebucht.
Positionsübersicht
Feld
Bedeutung
Ladeträger
Silo/Ladeträger zur
Ladeeinheit
Ladenr.
Aktuelle
Ladeeinheitsnummer
des
      Silo/Ladeträgers
Position
Position in der
      Ladeeinheit
Artikelnr.
Artikelnummer der Position auf der
Ladeeinheit
Artikelbezeichnung
Bezeichnung des Artikels
Partienummer
Partienummer der Position auf der
Ladeeinheit
Partiebezeichnung
Bezeichnung der Partie
Menge
Menge der Position auf der
Ladeeinheit
ME
Mengeneinheit
Owaage Nummer
Waagennummer zu einer
      Ladeeinh
[...]


---

## Ladeträgertyp

Ladeträger
typ
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Ladeträgertyp
Direktsprung
[LVLTT]
In dieser Anwendung werden die Typen eines Ladeträgers
angelegt. Ein Ladeträgertyp beschreibt den Ladeträger. Ein Ladeträgertyp kann
eine Palette, ein Silo oder ein Big Bag sein. Um ein Ladeträgertyp einzurichten
muss dieser erst im Artikelstamm angelegt werden. Dies ist Notwendig, da in
einer Spezial Anwendung des Lagerverwaltungssystems das Bruttogewicht des
Ladeträgers benutzt wird um die Nettomenge auf einem Ladeträger zu bestimmen. Es
kann aber auch vorkommen, dass ein Ladeträger in einer Produktion als Komponente
benutzt wird.
Ladeträgertyp-Felder
Ladeträgertyp
Nummer des
      Ladeträgertyps
Bezeichnung
Bezeichnung des
      Ladeträgertyps
Artikelstamm
Artikelstamm dem der Ladeträger
      zugrunde liegt.
Artikelstammbezeichnung
Anzeigefeld der
      Artikelstammbezeichnung
Bruttogewicht
Anzeigefeld des Bruttogewichts des
      Artikelstamms
Breite
Breite des Ladeträgers – Siehe auch
Anwendung von
      Lokalitätengruppen
Im Ändern-Modus kann über die Funktion
Artikelstamm
F10
in die Bearbeitungsmaske des aktuellen
Artikelstamms gesprungen werden.

---

## Ladeträger

Ladeträ
ger
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Ladeträger
Direktsprung
[LVSLT]
In dieser Anwendung werden neue Ladeträger angelegt.
Ein Ladeträger kann ein Silo, Big Bag, Palette … sein. Es können mehrere
Ladeträger von einem Ladeträgertyp angelegt werden.
Die Ladeträger Anlage kann in der Variante
Silo/Ladeträger und in der Variante Silo/Ladeträger vorgenommen werden. Nach der
Anlage eines Ladeträgers muss dieser erst auf eine
Lokalität
mittels der Funktion „
Buchungen
“ gebucht werden.
Anlage eines Ladeträgers
Zur Anlage eines Ladeträgers wird in den beiden
Varianten die Funktion „Neu“ [F8] ausgewählt. In der Erfassungsmaske müssen
folgende Felder gepflegt werden.
Erfassungsfeld
Bedeutung
Ladeträgernummer
Hier
      kann eine frei vergebbare Nummer eingetragen werden. Das Feld wir mit
      einer neuen Nummer vorgelegt. Diese Nummer wird durch die Letzt höchste
      Ladeträgernummer bestimmt. Auf diese Ladeträgernummer wird der Wert 1
      summiert.
Ladeträgertyp
Hier
      wird der Typ des Ladeträgers hinterlegt z.B. Silo, Big Bag, Palette
      …
Bezeichnung des
      Ladeträgers
Hier
      wird die Bezeichnung des Ladeträgers angegeben.
Ext.
      Nummer
Frei
      vergebbare Nummer zur Externen Identifikation
Aktiv
Kennzeichen, ob der Ladeträger aktiv
      ist. Wenn das Kennzeichen auf nein steht, so kann dieser Ladeträger nicht
      bebucht werden.
Registerkarte Lokalitätszustand
Feldname
Bedeutung
Lokalität
Anzeige auf welcher Lokalität sich
      der Ladeträger gerade befindet.
Einlagerungszeit
Zeit
      der ersten Bewegung des Ladeträgers auf eine Lokalität.
Einlagerer
Bediener der den Ladeträger auf eine
      Lokalität geschoben hat
Transportmittel
Ladeeinheitsnummer
Aktuelle Ladeeinheitsnummer auf dem
      Ladeträger.
Reinigungsstatus
Varianten
Silo/Ladeträger
In dieser Variante werden neue Ladeträger angelegt,
bearbeitet und gelöscht. Des Weiteren kann sich mit der Funktion
Ladeträgerbewegung ein Report geöf
[...]


---

## Lagerkopierer (LAKO)

Lagerkopierer (LAKO)
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Lagerkopierer
Direktsprung
[LAKO]
Mit Hilfe des Lagerkopierers können Artikel auf neu
angelegte Lagerorte kopiert werden. Dies dient nur zur Erstanlage der Artikel,
vorhandene Artikel bleiben erhalten!
Es können Artikel von einem auf ein oder mehrere Läger
kopiert werden.
Einstellungen
nur
      Artikelnummer wie
Es
      wird nur ein Artikel kopiert
Artikelnummer von/bis:
nur
      Artikelanlage seit
Kopiert Artikel ab einem
      Anlagedatum
nur
      Warengruppe von/bis
Bestätigung vor Start
      abfragen
Eintrag Fehlerprotokoll im Bereich
      ‘Lako’
Erklärung siehe Hinweise!
Besonderheit
In dem Einrichterparameter „
Folgenden Bediener dürfen nur das
Sortimentslager bearbeiten
“ kann als Liste hinterlegt werden, welcher
Bediener nur das Sortimentslager bearbeiten darf. Dieser Bediener kann dann kein
anderes Lager auswählen.

---

## Lagerplatzorte ändern

Lagerplatzorte ändern
Das Ändern der Lagerplatzorte ist in verschiedenen
Masken möglich:
•
In der Produktion, bei der Belegkorrektur
•
In den Lieferscheinen, bei der Warenposition
•
In der Aufbereitung, bei der Partieumbuchung
•
In der Onlinewaage, beim Boxmanagement
•
Allgemein in der Maske Partie Verteilung (PartieVerteilDlg)
Die Änderungen werden sofort gespeichert, wenn das
Feld für den Lagerplatzort verlassen wird. Dies gilt nicht im Boxmanagement für
die Onlinewaage, dort werden erst beim speichern der Daten die Lagerplatzorte
gespeichert.

---

## Lagerplatz (LGP)

Lagerplatz (LGP)
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Lagerplätze
Direktsprung
[LGP]
Lagerplätze sind Lagern direkt zugeordnet; nicht
jedoch Artikeln. Die Artikel legen sich also quasi durch das Buchen auf einen
Lagerplatz an. Aus der Artikelbestandsanzeige
[ARB]
heraus kann auf den Lagerplatznachweis
verzweigt werden.
Fürs Boxmanagement können über den SPA „Lagerplatzort
aktiv“ die Felder Lagerplatzort und Leergewicht freigeschaltet werden. Die
Lagerplatzorte können nicht nur an dieser Stelle geändert werden, sondern auch
an anderen Stellen.

---

## Lagerplatzort (LGPO)

Lagerplatzort (LGPO)
Direktsprung
[LGPO]
Der Stammdatenpfleger für den Lagerplatzort ist durch
den SPA „Lagerplatzort aktiv“ geschützt. In dem Pfleger können die einzelnen
Lagerplatzorte fürs Boxmanagement gepflegt werden.

---

## Lagerstamm (LGS)

Lagerst
amm (LGS)
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Lagerstamm
Direktsprung
[LGS]
Folgende Informationen können im Lagerstamm auf dem
hinterlegt werden.
Registerkarten
Kopfdaten und Registerkarte
  „Allgemein“
Lager-Nummer
Nummer des Lagers
Lager gesperrt
Einstellung „Nein“:
      Lagerlöschkennzeichen wird auf „0“ gesetzt. Lager nicht
      gesperrt.
Einstellung „Ja“:
      Lagerlöschkennzeichen wird auf „1“ gesetzt. Lager ist
      gesperrt.
Bezeichnung
Bezeichnung des Lagers
Lagertyp
In
      dem Feld Lagertyp kann über die
F3
-Auswahl angegeben werden, ob es
      sich um ein Bestandslager, Streckenlager, Pufferlager, Kundenlager oder
      Sortimentslager handelt.
Betriebsstätte
      Filialsystem
Zuordnung zu einer Filiale (nur im
      Zusammenhang mit dem Filialsystem)
Preisklasse Zugang
Preisklasse für den Lagerzugang
      (dient bei Lagerumbuchung als Vorschlagswert)
Preisklasse Abgang
Preisklasse für den Lagerabgang
      (dient bei Lagerumbuchung als Vorschlagswert)
Vorbelegung Kostenstellen
      Gruppe
Kostenstellengruppe gilt als
      Vorschlagswert bei Artikelanlage
Dieses Erfassungsfeld steht nur zur
      Verfügung, wenn der Steuerparameter
Kostenstellen-Lizenz
aktiviert
      ist.
Kostenträger Gruppe
Kostenträgergruppe gilt als
      Vorschlagswert bei Artikelanlage
Dieses Erfassungsfeld steht nur zur
      Verfügung, wenn der Steuerparameter
Kostenträgerrechnung
      angeschlossen
aktiviert ist.
Kostenobjekt Gruppe
Kostenobjektgruppe gilt als
      Vorschlagswert bei Artikelanlage
Dieses Erfassungsfeld steht nur zur
      Verfügung, wenn der Steuerparameter
Kostenobjekt-Lizenz
aktiviert
      ist.
Kundezuordnung
In
      dem Feld Kundenzuordnung kann angegeben werden, wo sich das Lager
      befindet. Das Lager kann einem bestimmten Kunden gehören und hier kann die
      Zuordnung festgehalten werden.
Telefon
.
Fax
Anrede
Vornam
Name
Straße
Anschrift des Lagers
PLZ
Anschrift des Lagers
Ort
Anschrift des
[...]


---

## Lagerverwaltungssystem

Lagerve
rwaltungssystem
Um das Lagerverwaltungssystem zu verwenden muss der
Steuerparameter 636
auf Ja gestellt
werden.
Das Lagerverwaltungssystem wird als Grundlage für zwei
Spezial Anwendung benutzt.
1.
Siloverwaltung
2.
Lagerverwaltungssystem per Scanner
Mit diesem Modul kann Ware auf einen Ladeträger
gebucht und abgebucht werden z.B. das Beladen und Entladen von Paletten. Diese
Paletten können dann von einer Lokalität auf eine andere Lokalität verschoben
werden z.B. Von einem Regalplatz XY zu einem Kommissionierungsplatz oder
Produktionsplatz. Das Beladen und Entladen von Ladeträgern, sowie umbuchen auf
eine andere Lokalität funktioniert zurzeit nur per Online Waage, Siloverwaltung
oder per Scannermodul. Wobei das Scannermodul eine Spezial Anwendung ist und
nicht im Standard funktioniert.
Vorgehensweise zur Einrichtung des
Lagerverwaltungssystems.
1.
Anlage des
Ladeträgertyps
2.
Anlage eines
Ladeträgers
3.
Anlage von Lokalitätengruppen
4.
Anlage einer
Lokalität

---

## LokalitätenGruppe

LokalitätenGruppe
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
LokalitätenGruppe
Direktsprung
[LVSLKG]
Eine Lokalität ist ein Ort, auf dem sich ein oder
mehrere Ladeträger befinden können. Eine Gruppe von Lokalitäten fasst
Lokalitäten zusammen.
Das findet in erster Linie Anwendung bei Regalfächern,
die mehrere Regalplätze haben. Die Regalplätze werden als Lokalitäten
eingerichtet, die Gruppe fasst dieses regalfach zusammen.
Diese Einrichtung ist optional !
Feldnamen
Bedeutung
Gruppennummer
Nummer der gruppe, die dann in der
      Lokalität eingetragen wird
Breite
Breite der Lokalitätsgruppe. Nur
      Werte > 0 werden bei der Belegung berücksichtigt.
Status
Belegung als binärzahl und in
      pseudografischer Aufbereitung.
Siehe auch
Anwendung von Lokalitätengruppen

---

## Lokalitäten

Loka
litäten
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Lokalitäten
Direktsprung
[LVSLK]
Eine Lokalität ist ein Ort, auf dem sich ein oder
mehrere Ladeträger befinden können. Ein Lokalität kann ein Lager, ein
Lagerplatz, eine Maschine oder eine Waage sein. Die Lokalität ist an ein Lager
gebunden.
In der Auswahlliste werden die Daten der Lokalitäten
angezeigt. Zusätzlich werden in der Auswahlliste die aktuelle Anzahl von
Ladeträgern und eine Liste der Ladeträger auf der Lokalität angezeigt.
Die Bearbeitungsmaske ist in folgende Bereiche
aufgeteilt.
Kopfd
aten
Feldname
Bedeutung
Lokalitätsnummer
Nummer der Lokalität
Bezeichnung
Bezeichnung der
      Lokalität
Lokalitätstyp
Typ
      der Lokalität
Lager
Lagernummer der
      Lokalität
Registerkarte Dimension
Die Dimensionsfelder können per Einrichterparameter
vorbelegt werden. Sollte für eine/mehrere Dimensionen eine Vorbelegung vorhanden
sein, so kann diese auf der Maske nicht geändert werden.
Feldname
Bedeutung
Dimension 1
      / Wert
Die
      Dimension wird entweder durch den EPA vorbelegt oder kann eingegeben
      werde.
Als
      Wert für die Dimension kann ein Text eingegeben werden.
Dimension 2 / Wert
s.
      Dimension 1
Dimension 3 / Wert
s.
      Dimension 1
Dimension 4 / Wert
s.
      Dimension 1
Dimension 5 / Wert
s.
      Dimension 1
Wertigkeit
Arbeitsregelnummer
Koordinate X
Koordinate Y
Koordinate Z
Volumen in l/kg
Länge / Mengeneinheit
Breite / Mengeneinheit
Höhe
      / Mengeneinheit
Registerkarte
Definitio
n
Die Einstellungen auf dieser Registerkarte sind nur
für Spezialanwendungen im Lagerverwaltungssystem und werden im Standard nicht
ausgewertet.
Feldnamen
Bedeutung
Drucker Nummer
In
      diesem Feld kann ein Drucker hinterlegt werden, welcher der Lokalität
      zugeordnet werden soll.
Tara
      Berechnung
In
      diesem Feld kann eingestellt werden, ob an der Lokalität eine Brutto oder
      Netto Wiegung durchgeführt werden soll.
Mehrfach LPP
Hier
      k
[...]


---

## Auswertung / Buchung

Auswertung / Buchung
Hauptmenü
Inventur
Permanente Inventur
Permanente Inventur Prüfungen
Geplante Inventur
Unabhängig davon, ob eine Bestandskorrektur notwendig
war, wird im Bewegungsprotokoll des Ladeträgers festgehalten, dass eine Inventur
stattgefunden hat.
So kann im Fall den (permanenten) Inventur zu einem
Zeitpunkt festgestellt werden:
•
Alle Ladeträger des Artikels
•
Sind im Zeitraum von x Tagen (
SPA 1045 – Permanente Inventur
) gezählt worden
Diese Tatsache bei jeder Erfassung geprüft und bei
Erfüllung aller Bedingungen wird dies in der Tabelle „LVS_PermInventurProtokoll“
festgehalten. Die Bestände in LVS und Warenwirtschaft müssen jetzt noch nicht
zwingend übereinstimmen.
Jede Bestandsänderung ab diesem Zeitpunkt gilt als
Bestandsfortschreibung. Die Differenz bleibt aber die Gleiche.
Nullmengen-Erfassung
Hauptmenü
Inventur
Permanente Inventur
Permanente Inventur Prüfungen
Es liegt in der Natur der Sache, dass man Bestände mit
einem Bestand von 0 nicht aufzufinden vermag. Sollte nach intensiver Prüfung der
Bestand tatsächlich nicht vorhanden sein, so kann dieser Null-Bestand mit der
Funktion „Nullzählung LVS erzeugen“ bestätigt werden. Es wird dann die
Null-Zählung ins Protokoll eingetragen und in den nächsten Beleg übernommen.
Funktionen
Report erzeugen
Hier wird ein Report aufgerufen, der alle in der
Auswahlliste angezeigten Artikel und Lokalitäten enthält. Zusätzlich ist der
Barcode „INVENTUR“ aufgebracht.
Inventurbelege LVS erzeugen
Hier wird ein Inventurdifferenzbelege (Vorgangsklasse
5055) erstellt. Dieser beseitigt alle Differenzen der Artikel zwischen LVS und
Warenwirtschaft. Es wird wie folgt gerechnet:
Bestandsdifferenz zum
Zeitpunkt der Zählung = D
Warenbestand zum Zeitpunkt
der Belegerstellung = W
Zählung = Z
Z = W - D
Bewertung
Hauptmenü
Inventur
Permanente Inventur
Laufende Inventur
Dieser Belegmuss dann im Nachgang in der Variante
Vorgänge bewertet werden.
Ungeplante Inventur
Im Bewegungsprotokoll des Ladeträgers wird
fest
[...]


---

## Einrichtung

Einrichtung
Im
SPA 1045 –
Permanente Inventur
werden zwei Werte
festgelegt:
1.
Die Anzahl der Tage für eine zusammenhängende Zählung in der permanenten
Inventur
2.
Die Anzahl von Zeilen in einem einzelnen Inventurbeleg
In der Vorgansunterklasse 5055 im Direktsprung
[FRZ]
wird ein
Kreditor festgelegt, der für Inventurbelege verwendet wird. Diese Einstellung
gilt ebenso für ungeplante Inventuren, muss also in jedem Fall eingerichtet
werden. Dieser Kreditor ist als steuerfrei zu konfigurieren!
Für die permanente Inventur muss ein Nummernkreis für
Belege der Vorgangsklasse eingerichtet sein.

---

## Durchführung

Durchführung
Die Vorgehensweise bei einer spontanen Inventur
unterscheidet sich nur in dem Startbarcode dieses Vorgangs und in der
Kennzeichnung im Bewegungsprotokoll.
Empfohlener Arbeitsablauf Scanner:
Geplant
Spontan
INVENTUR
KORRBESTAND
•
Scan der NVE
o
Anzeige der NVE-Info ohne
Menge
o
Prüfung und Zählung
•
Eingabe der Menge
o
Erzeugung des
Buchungssatzes
Reicht die Menge auf einem Ladeträger (z.B. in der
Kommissionierzone) nicht mehr aus, um den allokierten Bedarf zu decken, so wird
nachallokiert, das bedeutet, ein weiterer Ladeträger erhält den Fahrauftrag in
den Kommissionierbereich und von dort kann die fehlende Menge entnommen werden.
Zählung bei Befüllung des
Ladeträgers
Darüber hinaus gibt es die Möglichkeit die geplante
Inventur im Rahmen einer geeichten Befüllung eines Ladeträgers durchzuführen.
Wird die Befüllung eines Ladeträgers mittels Vorgangsimport vorgenommen, so wird
die
Unterklasse 21
verwendet,
womit zeitgleich zur Befüllung des Ladeträgers die eingebuchte Menge als gezählt
notiert wird.

---

## Auslagerung

Auslagerung
Die Einstellung des Steuerparameters
1038 – LVS-Allokationsstrategie
gibt
an, welche Fahraufträge im Rahmen der Allokation geschrieben werden. Ggf. müssen
weitere durch einen zweiten Schritt erstellt werden.

---

## Auslageroptionen

Auslageroptionen
GFO
Greatest First Out – ist eine Option der
Auslagerstrategien. Hier werden innerhalb der durch die Auslagerstrategien
bestimmten Reihenfolgen Ladeträger ermittelt, die eine möglichst große Menge der
Ware haben. Diese Option wird verwendet, um möglichst wenige Ladeträger zur
Auslieferung zu bringen.
SFO
Smallest First Out - ist eine Option der
Auslagerstrategien. Hier werden innerhalb der durch die Auslagerstrategien
bestimmten Reihenfolgen Ladeträger mit möglichst kleinen Mengen ermittelt. Diese
Option ist geeignet, um die Menge der Anbruchpaletten möglichst gering zu
halten.

---

## Auslagerstrategien

Auslagerstrategien
FIFO
First In First Out – Hier soll die Ware, die zuerst
ins Lager gekommen ist, dieses auch als erste wieder verlassen. Eine solche
Strategie, die man auch bei einem Durchlauf-Regal verwendet, wird oft dort
angewendet, wo keine andere Strategie greifen muss.
FEFO
First Expire First Out – Verderbliche Ware soll
möglichst nicht nach Eingang, sondern nach Verfallsdatum das Lager
schnellstmöglich verlassen. Hier verwendet man FEFO. Die Strategie ist eine
Spezifikation von FIFO und findet nur bei Waren mit Partien eine Anwendung
LIFO
Last In First Out – Bei steigenden Preisen wird diese
Lagerart gern verwendet, da somit der Lagerwert möglichst gering gehalten werden
kann. Diese Strategie ist nicht für verderbliche Waren geeignet. Auch Waren,
deren Wert mit der Zeit sinkt, ist nicht für LIFO-geeignet.

---

## Auslagerstrategien

Auslagerstrategien
Je Vorgangsunterklasse lässt sich eine
Auslagerstrategie festlegen. In der zugehörigen Prozedur werden auch die Mengen
für mögliche Über- bzw. Unterlieferungen festgelegt. Durch diese „Kulanz“ bei
der Auslieferung kann eine unnötig häufige Kommissionierung verhindert
werden.
Hier gibt es mehrere Möglichkeiten, die allesamt mehr
oder weniger streng das Prinzip FIFO (First In First Out) bzw. bei Beteiligung
von Partien mit Gültigkeitsdatum FEFO (First Expire First Out) berücksichtigen.
Auslagerstrategien
Wert
Bezeichnung
Beschreibung
1 -
      FIFO Only
Strenges FIFO
Hier
      wird die Ware streng nach FIFO ausgelagert. Dabei entstehen unter
      Umständen viele Kommissionierungen.
2 -
      FIFO GFO
Greatest First out
Bei
      der Allokation werden die größten Paletten zuerst allokiert. Es entsteht
      nur noch am Ende der Liste ein Kommissionierungsbedarf.
3 -
      One Charge Only
Die
      ganze Lieferung darf nur aus einer Charge bestehen
Die
      Lieferung der Position darf nur aus einer Charge bestehen. Ist also die
      eigentlich nach FIFO höher priorisierte Partie nicht in der gewünschten
      menge verfügbar, so wird die nächste gesucht, die in ganzer Menge
      verfügbar ist.
4 -
      FIFO GFO/SFO
Greatest First out Smallest First
      Out
Wie
      2, jedoch wird für die Kommissionierung darauf geachtet, dass möglichst
      Anbruchpaletten zuerst aufgebraucht werden. Das spart Platz, bedeutet aber
      u.U. einen höheren Kommissionierungsaufwand.

---

## Begriffe der Lagerverwaltung 2.0

Begriffe der Lagerverwaltung 2.0
Da in dieser Dokumentation immer wieder Begriffe
verwendet werden und erfahrungsgemäß darüber unterschiedliche Erwartungen
herrschen, hier eine kleine Begriffsdefinition.
Die Begriffe unterscheiden sich nicht von LVS, so dass
an dieser Stelle auf die dortigen Definitionen verwiesen werden kann.
Ladeträgertyp
Ladeträger
Lokalitäten
LokalitätenGruppe
Ladeeinheit
Fahraufträge
Anwendung von LokalitätenGruppe

---

## Einrichtung LVS

Einrichtung LVS
Ladeträgertypen
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Ladeträgertypen
oder Direktsprung [
LVLTT
]
Es müssen Ladeträgertypen eingerichtet werden. Es
empfiehlt sich folgende Einrichtung vorzunehmen bzw. zu ergänzen:
Ladeträgertypen
Typ
Typ
Breite
2
EUR1
2 –
      80x120 (für EURO-Paletten)
3
EUR3
3 –
      120x120 (für BigBags)
99
Linie
(siehe auch
Einrichtung SPA
      1037
)
undefiniert
Lokalitäten
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
Regale (Lokalitäten)
oder Direktsprung [
LVSLK
]
Die Lokalitäten sind die Stellplätze in einem Lager.
Sie können manuell mit [
LVSLK
]
eingerichtet werden. Lokalitäten im Regal können zu einer Lokalitäten-Gruppe [
LVLKG
] zusammengefasst
werden.
Es empfiehlt sich, die Lokalitäten mit einem Skript
einzurichten.
Die Lokalitätsnummer 999.999 ist als
Leerpaletten-Lokalität anzulegen!
Lokalitätstyp
Lokalitätstyp
Bei der Anlage der Lokalitäten muss ein Typ angegeben
      werden.
Die folgende
      Enumeration ist dabei zu verwenden:
Nr
Bezeichnung
Bemerkung
10
Wareneingang
Ankommende Waren
20
Warenausgang
Ausgehende Waren
30
Kommissionierbereich
Angebrochene Paletten – Lokalität
40
Produktionslager
Material, das an der Linie
      lagert
42
Linie Bereitstellung
Bereitstellungsbereich für die
      Produktion
44
Linie Fertigware
Bereich der fertiggestellten
      Waren
46
Linie
50
Regalplatz
Regalplatz in einem
      (Hochregal)-Lager
52
Blocklager-Bereich
Lagerfläche mit wahlfreiem
      Zugriff
54
Gefahrstofflager
70
Pufferbereich
Zwischenlager /
      Abstellbereich
80
Sperrlager
90
Außenlager
Lager ohne LVS-Kontrolle
96
Scanner
97
Schwundlager
Buchungsplatz für nicht auffindbare
      Waren
98
LKW/Trecker/In Transit
Waren, die derzeit transportiert
      werden
99
Scanner
Mit Ausnahme des Regal-Lagerplatzes sind alle
Lokalitäten groß genug unendlich viele Ladeträger aufzunehmen. Die Größe wird
nicht begrenzt. Nur ein Regal-Lagerplatz ist ausschließlich mit einem Ladeträger
zu
[...]


---

## Umlagerung

Umlagerung
Muss ein Ladeträger aus welchem Grund auch immer an
einen anderen Ort gelagert werden, so kann hier ein einfacher Vorgangsimport der
Unterklasse 10 erzeugt werden, um die Lokalität nach erfolgter Umlagerung neu
festzulegen.
Empfohlener Arbeitsablauf Scanner:
•
Scan der NVE
o
Anzeige der NVE-Info
•
Scan der neuen Lokalität
o
Erzeugen einer
Ladeträgerbewegung im VIMP

---

## LVS-relevant

LVS-relevant
Es gibt folgende Lagerverwaltungssystem-Relevanzen
LVS-relevant
0
nicht relevant
Ist
      nicht fürs Lagerverwaltungssystem relevant
1
relevant
Ist
      fürs Lagerverwaltungssystem relevant
2
buchend
Ist
      fürs Lagerverwaltungssystem relevant im Zusammenhang mit
      Buchen

---

## Mengenzeiträume

Mengenzeiträume
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Mit dieser Funktion wird eine Information über die
Laufzeit der Partie gebracht. Anschließend sind weitere Verzweigungen
möglich.

---

## Merkmalsleiste

Merkmalsleiste
Zur Vereinfachung der Artikelneuanlage bei ähnlichen
Artikelstamm und Artikelinformationen ist es möglich, auf Basis einer fest
vorgegebenen Artikelnummerstruktur den Artikelstamm und den lagerabhängigen
Artikelteil automatisch anlegen zu lassen. Hierzu ist es notwendig, mit einem
festen Artikelnummernaufbau zu arbeiten, der während der Dateneingabe nach
festen Vorgaben mit
F3
Bereichsprüfungen abgefragt wird.

---

## Partieumbuchung

Partieumbuchung
Hauptmenü
Produktion / Umbuchung
Umbuchungen
Artikel-Umbuchung
oder Direktsprung
[ARU]
Auflösung von Partierestbeständen, falsche Partieein-
oder Ausbuchung sowie Neustrukturierung der Artikel und Umlagerungen können
mögliche Gründe für eine Partieumbuchung sein. Die Partieumbuchung erfolgt über
die Artikelumbuchung.
Zunächst erscheint eine Übersicht der bereits
getätigten Artikelumbuchungen. Mit der Funktion
Artikelumbuchung
F8
wird die Partieumbuchung
eingeleitet.
Die Abwicklung dieser Artikel- bzw. Partieumbuchung
ist ähnlich wie die der Vorgangserfassung.
Felder
Belegnummer
Vorschlag einer automatisch
      Systemnummer aus dem Zählkreis
Belegdatum
Vorschlag des
      Tagesdatums
Periode/Jahr
Zum
      Belegdatum gehörende Periode/Jahr
Lagernummer
Lager, in dem diese Partieumbuchung
      erfolgt
Versandart
Hat
      für die Partieumbuchung keine Bedeutung
Über die Funktion
Positionsteil
F5
wird in die Positionsmaske gewechselt.
Die Funktion
Umbuchung
F4
erlaubt Ihnen dann die
Positionserfassung.
Felder
Lagernummer
Vorschlag aus der
      Umbuchungs-Kopfmaske
Artikelnummer Abg.
Artikelnummer Abgang der
      Partie
Artikelnummer Zug.
Artikelnummer Zugang der
      Partie
Menge/Einheit
Partieumbuchungsmenge und
      Mengeneinheit
Einzelpreis.PE/ME
Einzelpreis je Preiseinheit und
      Mengeneinheit
Nach Erfassung der Menge und Mengeneinheit erscheint
die automatische Partieauswahl für die Abgangspartie und anschließend (nach
Auswahl der Partie) die Partieauswahl für die Zugangspartie.
Der Abschluss dieser Umbuchung ist mit dem Abschluss
der Vorgangserfassung identisch. Nachdem für diese Position ein Preis eingegeben
und die Position abgeschlossen wurde, wird diese Umbuchung mit dreimal
ESC
abgeschlossen. Bei Bedarf kann für
diese Umbuchungen eigene Nummern- bzw. Zählkreise sowie Formulare hinterlegt
werden.

---

## Partiegruppen

Partiegruppen
Hauptmenü
Partieverwaltung
Chargen / Partien
Partiegruppen
oder Direktsprung
[PGR]
Die Partiegruppe ermöglicht es, Partien sachlich
besser zu ordnen bzw. in getrennten Nummernkreisen zu verwalten. Um eine Partie
einer Partiegruppe zuzuordnen ist es notwendig, die Partiegruppe im Vorwege zu
erfassen.
In der Menüanwahl „Partiegruppen“ kann unter der
Funktion
Neu
F8
eine Partiegruppe angelegt werden.
Folgende Felder stehen dabei zur Verfügung.
Felder
Nummer
Vorschlag einer automatischen
      Systemnummer, die überschrieben werden kann.
Bezeichnung
Bezeichnung der
      Partiegruppe
Matchcode
Matchcode der
      Partiegruppe
Nummernkreis
Bei
      einer Verwaltung der Partien über Partiegruppen können die Partienummern
      aus dem hier hinterlegten Nummernkreis geholt werden (zur Einrichtung
      siehe
[NKS]
,
[NKZ]
). Bei Eingabe Null, werden die
      Partienummern aus einem allgemeinen Partienummernkreis
[MNDNK]
geladen.
•
51 = Partien
      manuelle Anlage
•
– 56 = Partien
      automatisch

---

## Partiestammsatz löschen

Partiestammsatz löschen
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Über die Funktion
Löschen
F7
wird das Löschen einer Partie
eingeleitet. In dem Anschlussmenü wird damit die Funktion
Löschen
F7
frei geschaltet und kann somit für das
endgültige Löschen verwendet werden.
Grundsätzlich wird über diese Funktion eine Partie
nicht vollständig aus dem System gelöscht. Gelöschte Partien können weiterhin
zur Anzeige gebracht werden, die Nutzung einer gelöschten Partie wird aber nicht
mehr möglich sein.

---

## Partiestamm

Partiestamm
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
In der Variante Partieübersicht ist bei
artikel-spezifischen Partien die zugeordnete Lagernummer nicht sichtbar, wenn
noch kein Partiebestand gebucht ist.
Die
zugewiesenen Lager leben in dieser Fassung erst auf, wenn auch Bestände gebucht
sind.
Partien können auf Basis
Artikelstamm oder auf Basis Artikel/Lager angelegt werden. Der
Steuerparameter 277
„Typ-Vorbelegung bei Partieartikel-Anlage“ legt fest wie das Feld „Typ der
Zuordnung“ vorbelegt werden soll. Zur Auswahl stehen Artikelstamm oder
Artikel/Lager. Die Standardeinstellung des Steuerparameters 277 ist
Artikelstamm.
Partien werden in der
Praxis hauptsächlich während der Belegerfassung selbst angelegt. Dies kann aber
auch über die Partiestammdatenverwaltung erfolgen.
Der
Steuerparameter 1084
„Artikel mehrfach in Partie erlaubt“ legt fest, ob im Partiestamm-Pflegemodul
ein Artikel oder Artikelstamm mehreren Artikelposition der Partie zugeordnet
werden kann (Einstellung:
Ja
).
Bei der Einstellung
Nein
kann ein Artikel oder
Artikelstamm nur einer Partieartikelposition zugeordnet werden. Es ist dann auch
nicht möglich, einer Position einen Artikel zuzuordnen, dessen Artikelstamm
bereits einer anderen Position zugeordnet wurde und umgekehrt.
Die Unterschiede dieser zwei Möglichkeiten werden
nachfolgend dargestellt.

---

## Produktionslinien

Produktionslinien
Hauptmenü
Produktion / Abwicklung
Produktionslinien
Direktsprung
[PRODL]
Im Produktionslinien-Pfleger können Sie
Produktionslinien definieren, die im Lagerverwaltungssystem (LVS) mit Material
versorgt werden sollen bzw. wo produzierte Materialien abgeholt werden sollen.
Pfleger:
Bezeichnung
Inhalt
Nummer
Laufende Nummer in
      Referenz-ERP
Bezeichnung
Bezeichnung im Klartext
Interface
      Name
Name
      der Linie in der Kommunikation mit externen Systemen
Bereitstellung LVS
LVS-Lokalität vom Typ
      Bereitstellung, die zur Bereitstellung von Komponenten-Waren für diese
      Linie verwendet wird.
Abholung
      LVS
LVS-Lokalität vom Typ Abholung
      Linie, die zur Erstellung von Waren von dieser Linie verwendet
      wird.

---

## Registerkarte Allgemein

Registerkarte Allgemein
Feld
Bedeutung
Belegerzeugung ohne Abschließen
      möglich
Mit
      diesem Schalter kann eingestellt werden, ob ein Vorgang ohne
Abschließen
erzeugt werden kann. Das
Abschließen
der Wiegung wird
      automatisch durchgeführt.
Lagernummer des Profils
Hier
      kann das Lager für das Profil eingestellt werden. Dieses Lager wird auch
      für die Siloauswahl herangezogen. Dieses Lager wird zur Vorbelegung des
      Lagers der Waage genommen. Aber wenn nur dann, wenn der Schalter Festen
      Wert erzwingen auf Ja steht
Festen Wert erzwingen
Wenn
      hier ein Ja eingetragen wird, wird das Lager aus dem Prozess als
      Vorbelegung des Waagenlagers genommen.
Klasse
Die
      Vorgangsklasse kann nur in Abhängigkeit des Wiegetyps gesetzt
      werden.
Unterklasse
Unterklasse der
      Vorgangsklasse
Warenausgang (Kunde)
automatische Zuordnung
      Kunde/Lieferant zur Partie:
Beim
      Abschließen einer Wiegung im Warenausgang wird bei einer ausgewählten
      Partie, der Kunde im Partiestamm eingetragen. Dieses Verhalten kann hier
      ein-/ausgeschaltet werden.
Wareneingang (Lieferant)
automatische Zuordnung
      Kunde/Lieferant zur Partie:
Beim
      Abschließen einer Wiegung im Wareneingang wird bei einer ausgewählten
      Partie, der Lieferant im Partiestamm eingetragen. Dieses Verhalten kann
      hier ein-/ausgeschaltet werden.

---

## Registerkarte Silo

Registerkarte
Silo
Auf dieser Registerkarte werden die Einstellungen für
das Silo in der Waage vorgenommen.
Feldname
Bedeutung
Silostandort Festhalten
Mit
      diesem Schalter kann eingestellt werden, ob das Silo / Ladeträger auf eine
      andere Lokalität umgebucht werden soll, wenn in der Wiegung eine andere
      Lokalität als die Lokalität des Silos / Ladeträgers ausgewählt worden
      ist.
Aktivitätstyp
Hier
      kann ein Aktivitätstyp für die LVS / Silo Buchung ausgewählt werden. Das
      Format für den Aktivitätstyp ist ein Anwenderformat
      „AF_LVSAKTTYP“.
Dabei ist zu beachten, dass die
      ersten 100 Einträge seitens der Firma Branchen-ERP gepflegt werden.
Prozesstyp
Hier
      kann eingestellt werden um welchen Prozesstyp es sich handelt. Diese
      Prozesse werden benötigt, um bestimmte Silobuchungen über Waage
      abzubilden. Wie z.B. die Leermeldung. Der jeweilige Prozesstyp gilt für
      das Lager, welches im Prozess eingetragen worden ist. Dies heißt bei n
      Läger müssen auch n Prozesse eingerichtet werden.
Prozesstyp
Bedeutung
--
Kein
            Prozess
Leermeldung Eingangsbuchung
Dieser Prozess muss vorhanden sein, um ein
            Silo von einer negativen Menge auf 0 zu bringen. Dies bedeutet, es
            muss als Wiegetyp ein Wareneingang gewählt werden
Leermeldung
            Ausgangsbuchung
Dieser Prozess
            muss vorhanden sein, um die restliche Menge von einem Silo auf 0 zu
            bringen. Dies bedeutet, es muss als Wiegetyp ein Warenausgang
            gewählt werden.
Leermeldung Schwundsilobuchung
Dieser Prozess muss vorhanden sein, wenn
            die Leermeldungsmenge auf ein Schwundsilo gebucht werden soll. Ist
            einem anderen Prozess ein Schwundsilo zugeordnet, und es existiert
            kein Prozess mit diesem Typ, so wird die Leermeldung nicht
            durchgeführt.
Artikelumbuchung Abgang
Um eine
            Artikelumbuchung durchzuführen, muss ein Prozess für di
[...]


---

## Saatgutetiketten

Saatgutetiketten
Hauptmenü
Saatzucht
Saatgutabwicklung
Saatgutetiketten
oder Direktsprung
[SAATE]
Felder
Lager
PartieId
Partie-ID
Partienummer
Nummer der Partie
Partiebezeichnung
Bezeichnung der Partie
ETID
Etiketten-ID
Typ
Etikettentyp
Etikett Nr.
Etiketten-Nummer
Anerkennungs-Nr.
Anerkennungs-Nummer
Art
Fruchtart
Botanisch
Botanische Bezeichnung
Sorte
Saatsorte
Gewicht
Probenahme
Text
      1 - 6
Hier
      kann ein beliebiger Text eingegeben werden
Wirkstoffe
KF
Keimfähigkeit
TKG
Tausendkorngewicht
Wiederverschluss
Fehldruck
Wer
Ersteller der Etiketten
Wann
Wann
      wurden die Etiketten erstellt?
Bemerkung
EAN
Globale
      Artikelidentifikationsnummer
Beize
Matrix 1
Inhalt des QR-Codes
Logistikscan1
Probendatum
Datum der Probe aus dem
      Laborsatz
Probenstecher
Probennummer
Laborprobennummer
Branchen-ERP-Etikettenid
Ident des
Etiketts
Branchen-ERP-Etikettenbezeichnung
Bezeichnung des
Etiketts
Folgende Funktionen stehen in der Auswahlliste
zur Verfügung
Funktion
Taste
Bedeutung
Ändern
F5
Ruft
      die Maske Etikettendruck zum Bearbeiten auf. Auf dieser Maske ist es
      möglich Individuelle Texte zu pflegen, diese abzuspeichern und den
      Datensatz zu drucken.
Ansehen
F6
Ruft
      die Maske Etikettendruck im Ansehen Modus auf.
Wiederhohldruck
STRG+F9
Mit
      dieser Funktion können die Etiketten der ausgewählten Datensätze erneut
      ausgedruckt werden. Es können nur Etiketten mit einer Zuweisung zu einem
      Probensatz ausgedruckt werden.
Maske Etikettendruck
Mit der Funktion Ändern F5 wird der Pfleger
Etikettendruck aufgerufen. Auf diesem Pfleger ist es möglich die Textfelder 1-3
zu befüllen.
Feld
Bedeutung
Probennummer
Nummer der Probe aus dem
      Labor
Probennehmer
Probennehmer aus der
      Probe
Probenstecher
Probennehmer aus der
      Probe
Probendatum
Datum der Probe.
Probengewicht
Das
      Gewicht der Probe
Artikel
Artikelbezeichnung
Sorte
Sorte des Artikels
Kategorie
Kurzbezeichnung der
      Kategorie
Anerkennungsnummer
Anerkennu
[...]


---

## Beispiel Scancodes für die Lagerplatzumbuchung

Beispiel
Scancodes für die Lagerplatzumbuchung
In den Beispiel Scancodes für die Lagerplatzumbuchung
befindet sich kein Scancode für einen Artikel. Hier ist ein Artikel aus dem
Sortiment zu wählen.
Lagerplatzumbuchung Start
Lagerplatzumbuchung Ende
Storno
Lagerplatz
Damit der gescannte Lagerplatz im System gefunden wird
muss ein Lagerplatz mit der Nummer 1234 auf dem Lager des Scanners eingerichtet
werden.

---

## Eingangslieferschein

Eingangslieferschein
Mit diesem Modul ist es möglich ein
Eingangslieferschein mittels eines Scanners zu erfassen. Bei der Erfassung eines
Eingangslieferscheins besteht die Möglichkeit den erfassten Artikel einem
bestimmten Lagerplatz zu zuweisen.
Das Erfassen von Partien ist bislang noch nicht
berücksichtigt worden.
Itembox zur Darstellung der Daten auf dem
Scanner
IB_CE_VIMP_Eingangslieferschein
Voraussetzungen
Als erstes müssen folgende
Einrichtungen
vorgenommen werden.
Des Weiteren müssen folgende Texte im EAN 128
Konvertiert werden um eine Lagerplatzumbuchung auf dem Scanner zu starten. . An
dieser
Stelle
sind die
Beispiel Scancodes für die Eingangslieferscheine hinterlegt worden.
1.
EL
2.
ELENDE
3.
STORNO
4.
Etiketten für die einzelnen Lagerplätze. Der Lagerplatznummer muss der
AI-Code
91 vorangestellt werden.
z.B. 9112345 wobei 12345 der Lagerplatz ist
5.
Die Lieferanten ILN. Der Lieferanten ILN muss der
AI-Code
00 und eine 3 Vorangestellt werden
 z.B. 003123456
Der Scanner muss auf das aktuelle Lager eingestellt
sein.
Ablauf
Als erstes wird der Startscancode
EL
mittels
Scanner erfasst.
Lieferanteneingabe
Die Lieferanteneingabe erfolgt nach der Erfassung des
Startscancodes. Die Eingabe des Lieferanten kann auch übersprungen werden, denn
der Lieferant kann im Nachlauf unter
Vorgangsimport
[
VIMP
] hinzugefügt werden kann. Die ILN Nummer
wird im
Lieferanten- /
Kundenstamm
im Feld ILN hinterlegt
Artikeleingabe
Als nächstes wird der Artikel erfasst. Hier kann der
EAN-Code entweder per Scanner gescannt werden, oder per Hand eingegeben werden.
Des Weiteren ist es möglich die Artikelnummer per Hand zu erfassen. Sollte der
erfasste Artikel nicht gefunden werden, so wird in der Relation
ImportVorgPosition auch ein neuer Datensatz angelegt. Diesem kann im Nachlauf
unter
Vorgangsimport
[
VIMP
] bearbeitet werden ein Artikel
hinzugefügt werden.
Hauptmenü
Externe Kommunikation
Stammdatenimport
Vorgangsimport
Wenn ein Artikel nicht gefun
[...]


---

## Lagerplatzumbuchung

Lagerplatzumbuchung
Bei der Lagerplatzumbuchung können einzelne Artikel
vom Lagerplatz A zum Lagerplatz B in einem Lager umgebucht werden.
Es kann zurzeit pro Lagerplatzumbuchungsblock auf
dem Scanner nur ein Artikel umgebucht werden.
Partien werden bislang noch nicht
berücksichtigt.
Itembox zur Darstellung der Daten auf dem
Scanner
IB_CE_Lagerplatzumbuchung
Voraussetzungen
Als erstes müssen folgende
Einrichtungen
vorgenommen werden.
Des Weiteren müssen folgende Texte im EAN 128
Konvertiert werden um eine Lagerplatzumbuchung auf dem Scanner zu starten. An
dieser
Stelle
sind die
Beispiel Scancodes für die Lagerplatzumbuchung hinterlegt worden.
1.
LGPU
2.
LGPUENDE
3.
STORNO
4.
Etiketten für die einzelnen Lagerplätze. Der Lagerplatznummer muss der
AI-Code
91 vorangestellt werden.
z.B. 9112345 wobei 12345 der Lagerplatz ist
Ablauf
Als erstes wird der Startscancode
LGPU
mittels
Scanner erfasst.
Artikeleingabe
Nach dem der Scancode erfolgreich verarbeitet worden
ist, muss als nächstes der Artikel erfasst werden. Hier kann der EAN-Code
entweder per Scanner gescannt werden, oder per Hand eingegeben werden. Des
Weiteren ist es möglich die Artikelnummer per Hand zu erfassen. Sollte der
erfasste Artikel nicht gefunden werden, so wird in der Relation
ImportVorgPosition auch ein neuer Datensatz angelegt. Dieser kann im Nachlauf
unter
Vorgangsimport
[
VIMP
]bearbeitet werden.
Wenn ein Artikel nicht gefunden worden ist, kann
dies folgende Ursachen haben.
1.
Der Artikel befindet sich nicht auf dem Aktuellen Lager des
Scannerbedieners.
2.
Der Artikel ist nicht mehr gültig
3.
Der Artikel existiert nicht im System
4.
Die EAN-Nummer ist nicht im Sekundschlüssel hinter legt worden.
Mengeneingabe
Nach dem Artikel erfasst worden ist wird die Eingabe
der Menge erwartet. Es ist möglich eine 0 Menge einzugeben.
Gebindebehandlung
Die Gebindefaktoren werden über zwei Unterschiedliche
Wege bestimmt.
1.
Der erste Weg ist per EAN Code des erfassten Ar
[...]


---

## Permanente Inventur

Permanente Inventur
Einrichtung der Permanenten Inventur
1.
Manuelle Einrichtung
Die Permanente Inventur kann auf zwei Arten
durchgeführt werden.
1.
Der Scanner befindet sich in keinem Vorgangsmodus, so wird per erfassten Artikel
mit Menge ein Differenzbeleg für die Permanente Inventur erfasst.
2.
Es wird ein Differenzbeleg für die Permanente Inventur mit dem Scanner eröffnet.
Es wird ein Differenzbeleg mit allen erfassten Artikel erzeugt.
Die erfassten Differenzbelege werden automatisch
angelegt.
Besonderheiten:
Bei der Permanenten Inventur ist darauf zu achten,
dass Artikel immer Partie weise und oder Lagerplatz weise gezählt werden wenn
diese vorhanden sind. Existieren Lagerplätze und oder Partien und der Artikel
wird ohne Partien oder Lagerplätze gezählt, so wird der Artikelbestand erhöht,
ohne dass eine richtige Zuordnung zur Partie oder zu dem Lagerplatz möglich
ist.
Beispiel:
Der Artikel A befindet sich auf den Lagerplätzen LP1
und LP2. Jetzt wird der Artikel ohne Lagerplatz Zuweisung gezählt, dadurch wird
die Menge des Artikels auf die erfasste Menge am Scanner korrigiert. Die
korrigiert Menge wird nun dem Standardlagerplatz 0 zugewiesen und nicht dem zu
zählenden Lagerplatz. Dadurch ändert sich die Artikelmenge auf dem Lagerplatz 0
um die eingegebene Menge.
Der Artikel B hat eine Partie Zuordnung von Partie1
und Partie2. Jetzt wird der Artikel ohne Partie gezählt. In diesem Fall wird die
Partiemenge nicht mit korrigiert. Sondern nur die Artikelmenge. Partien können
nur einzeln erfasst werden. Es existiert keine Partieverteilung.
Erfassung eines
Artikels für die Permanente Inventur
1.
Als erstes muss der zu zählende Artikel gescannt werden.
2.
Jetzt kann zusätzlich eine Partie oder ein Lagerplatz angegeben werden
3.
Als letztes wird die Menge angegeben. Nach der Mengenangabe wird ein
Positionswechsel vorgenommen. Wurde am Scanner kein Block für die Permanente
Inventur gestartet, so wird nach der Erfassung ein Vorgang für di
[...]


---

## Silobehandlung

Silobehandlung
Mit der Funktion
Silobehandlung
lassen sich Behandlungen
des Silos, wie z.B. Reinigungen oder Begasungen, durchführen. Als Behandlung
lässt sich ein beliebiger Text eingeben. Mit
F3
öffnet sich eine Itembox, mit der man
auch eine Behandlung aus den bisher verwendeten Behandlungen auswählen kann.
Die Behandlungen werden im Silobewegungsprotokoll
dokumentiert. Sie werden mit dem Bewegungstyp „Behandlung“ gekennzeichnet. Die
durchgeführte Behandlung wird in der Spalte „Behandlung“ festgehalten.

---

## Hofliste-Details

Hofliste-Details
Diese Funktion kann nur ausgeführt werden, wenn ein
Datensatz in der jeweiligen Auswahlliste markiert worden ist. Die Funktion ruft
die Auswahlliste
Hofliste-Details
auf.
Wird diese Funktion in der Variante Silo ausgewählt,
so werden zu der angewählten Siloposition alle dazu gehörigen Waagenbelege
angezeigt.
Wird diese Funktion in der Variante Silobestand
ausgewählt, so werden alle Waagenbelege zu diesem Silo angezeigt.

---

## Siloverwaltung

Siloverw
altung
Hauptmenü
Nebenbuchhaltungen
Siloverwaltung
Silo
Direktsprung
[SILO]
Die Siloverwaltung wurde als Spezialfall des
Lagerverwaltungssystems entwickelt. Die Ladeträger entsprechen dabei den
Silos.

---

## Vorgang-Details

Vorgang-Details
Diese Funktion kann nur ausgeführt werden, wenn ein
Datensatz in der jeweiligen Auswahlliste markiert worden ist. Die Funktion ruft
die Auswahlliste
Vorgangsübersicht
auf
Wird diese Funktion in der Variante Silo ausgewählt,
so werden zu der angewählten Siloposition die dazugehörigen Vorgänge
angezeigt.
Wird diese Funktion in der Variante Silobestand
ausgewählt, so werden alle Vorgänge zu diesem Silo angezeigt.

---

## Ware abstimmen

Ware abstimmen
Die Hilfe hierzu finden Sie unter
Abschlüsse/Inventur > Reorganisation > Ware
abstimmen

---

## Warenreorganisation

Warenreorganisation
Die Hilfe hierzu finden Sie unter
Abschlüsse/Inventur > Reorganisation > Benutzung
Warenreorganisation

---

## Position umbuchen

Position umbuchen
Auf dieser Maske kann für jede Position ein Artikel
aus dem Referenz-ERP Pool eingetragen werden, welcher anstelle des TERRES Artikels
verwendet werden soll. Es können nur Artikel des gleichen Lagers und mit
gleichem Steuersatz ausgewählt werden, andere Artikel stehen nicht zur
Verfügung. Um den gültigen Steuersatz eines Artikels aus dem Referenz-ERP Pool zu
finden wird die Steuergruppe des Lieferanten mit den Steuerschlüsseln des
Artikels auf dem ausgewählten Lager verprobt. Wird der gewünschte Artikel nicht
angezeigt, so konnte keine Zuordnung zwischen dem Steuerschlüssel und der
Steuergruppe gefunden werden. Summen Zeilen können nicht umgebucht werden.

---

## Lagerumbuchung

Lagerumbuchung
Um einen Lagerumbuchung / Lagerplatzumbuchung mit dem
Vorgangsimport in das Referenz-ERP System einzuspielen müssen folgende Regeln beachtet
werden und mindestens folgende Felder gefüllt werden.
Besonderheiten
Für eine Positionszeile in der Lagerumbuchung müssen
zwei Zeilen in der Relation ImportVorgPosition angelegt werden. Damit das System
weiß, welches die Abgangs- und welches die Zugangszeile ist, werden die Zeilen
per Positionsklammer und „TypAbgangZugang“ geklammert.
Die Positionsklammer beschreibt die Stelle der
Warenposition in der Lagerumbuchung. Es empfiehlt sich in diesem Feld die
PositionId der Abgangsposition einzutragen. Mit dem Feld TypAbgangZugang wird
beschreiben, ob es sich um eine Zugangs- oder Abgangszeile handelt.
1 ist die AbgangsZeile
2 ist die ZugangsZeile
Gebinde
Um eine Gebinde Position anzulegen muss die
Gebindemengeneinheit in dem Feld „ME“ und die Gebindeanzahl muss im Feld „Menge“
in der Relation ImportVorgPosition gespeichert werden.
Partie
Existiert zu einer Warenposition nur eine Partie so
kann diese direkt mit in der Relation ImportVorgPosition gespeichert werden.
Es werden bislang nur die Kombination aus
Partiebezeichnung und oder Partienummer geprüft.
Wird nur die Partiebezeichnung gespeichert, so wird
mit dieser Partiebezeichnung eine neue Partie angelegt, wenn diese nicht
vorhanden ist.
Sollen mehrere Partien zu einer Warenposition angelegt
werden, so müssen diese Partien in der Tabelle
ImportVorgPositionPartie
gespeichert werden. Auch hier gilt die Kombination zwischen Partienummern und
Partiebezeichnung. Eine Verprobung zwischen der Partiemenge und der
Positionsmenge findet nicht statt.

---

## Qualitäten

Qualitäten
Im Qualitätsgrid werden die Qualitäten für den
jeweiligen Artikel mit dem jeweiligen Lager angezeigt. Dort lässt sich dann noch
der Analysewert für die jeweiligen Qualitäten eintragen.

---

## Ladeträgerverwaltung an der Waage

Ladeträgerverwaltung an der
Waage
Um die
Lagerverwaltung
bzw. die
Siloverwaltung
zu verwenden muss
der
Steuerparameter 636
Lagerverwaltungssystem auf „Ja“ gestellt werden. Ist die Lager/Siloverwaltung
auf aktiv gestellt worden, so wird auf der Registerkarte LVS/Silo/Kontrakt der
Bereich Silo-/Lagerverwaltung angezeigt. Auf der Registerkarte Wiegung wird ein
Schnellerfassungsfeld für das Silo bzw. für den Ladeträger eingeblendet.
Bevor das
Lagerverwaltungssystem
bzw. die
Siloverwaltung
an der Waage
benutzt werden kann, muss diese Eingerichtet werden.
1.
Anlage von ein oder mehrere
Ladeträgertypen
.
2.
Anlage von
Ladeträger
bzw.
Silos
3.
Anlage von einer oder mehreren
Lokalitäten
4.
Buchen
eins Silos /
Ladeträgers auf eine
Lokalität
Vorbelegung des Ladeträgers / Silos und der
Lokalität / Standort
Nach der ersten erfolgreichen Bebuchung eines
Ladeträgers / Silo werden sich diese Daten gemerkt. Diese Felder werden dann
beim Erstellen einer neuen Wiegung mit den zuletzt Erfassten Daten
vorbelegt.
Ablauf
Mit einer
Eingangswiegung
wird die gewogene Menge auf
ein oder mehrere Ladeträger gebucht. Mit einer
Ausgangswiegung
wird die gewogene Menge von
einem oder mehreren Ladeträgern abgebucht. Dabei wird keine Prüfung gemacht, ob
der Artikel sich auf dem Ladeträger befindet.
Es ist jetzt möglich eine Silo Buchung an der Waage zu
einem bestimmten Zeitpunkt zu buchen. Dazu muss der
Einrichterparameter
„Belegnr bearbeiten“ auf „Ja“
gestellt werden. Wird in dem Feld Uhrzeit nicht eingetragen, so wird die Buchung
um 0:01 des eingetragenen Datums durchgeführt. Die Bewegungszeit im Protokoll
wird dann auf das entsprechende Datum gesetzt.
Mit der Funktion „Silo nachbuchen“ in der Auswahlliste
ist es möglich Wiegungen, die nicht mehr rückgängig abgeschlossen werden können,
da aus diesen schon ein Vorgang erzeugt worden ist, nachträglich in das Silo /
den Ladeträger einzubuchen. Als Buchungszeit wird dann die Zeit der zweiten
Wiegung genommen. Auch hier wi
[...]


---

## Zusätzliche Erfassung bei Umbuchungen

Zusätzliche
Erfassung bei Umbuchungen
Wenn Sie diese Erfassung für einen Umbuchungsvorgang
wie Artikelumbuchung, Lagerumbuchung oder Lagerplatzumbuchung angewählt haben,
so ist eine umfangreichere Erfassung möglich.
Schließlich können sich Mengen, Mengeneinheiten oder
Gebinde bei der Umbuchung von einem in ein anderes Lager ändern.
Für diesen Fall steht Ihnen die Funktion
Separat erfassen
zur Verfügung. Wenn Sie
diese Funktion nicht anwählen, sind Zugang und Abgang gleich.
Wollen Sie für eine bestimmte Vorgangsklasse immer die
Erfassung separat erfassen, so können Sie dies in der Vorgangsklasse mit dem
Pfleger
Formularzuordnung [FRZ]
einstellen.
Nachhaltigkeit
Für die
Nachhaltigkeit
steht hier jeweils eine Seite für
die Abgangs- und Zugangsposition zur Verfügung. Eine genaue Beschreibung der
Felder findet man auf der
Nachhaltigkeitsseite
der Artikelerfassung.

---

## Wichtiger Hinweis zu den Partiebeständen

Wichtiger Hinweis zu den Partiebeständen
Die interne Bestandsführung ist überarbeitet worden.
Daher muss möglichst gleich nach der Installation unter
[WAREO]
der Punkt
Partiereorganisation
ausgeführt
werden!

---

## Zuordnung der Rezepturgruppe zum Artikel

Zuordnung der Rezepturgruppe zum Artikel
Im Artikel
[AR]
(nicht Artikel
stamm
, denn je
Lager können unterschiedliche Rezepturzuordnungen wirksam sein!) wird unter
„weitere Kennzeichen“ die Rezepturgruppe zugeordnet. Hier ist mit
F3
eine Auswahl der vorhandenen Einträge
verfügbar, mit
F8
sind die Stammdaten
zu pflegen.

---

## Ablauf einer permanenten Inventur

Ablauf einer permanenten Inventur
•
Artikel, die das Kennzeichen „permanente Inventur“ tragen, werden im
Verlauf des Jahres gezählt.
•
Ist die Zählung abgeschlossen, so wird ein Inventurbestandbeleg (5055)
erstellt.
o
Die Warenbestände werden
korrigiert
o
Eine Bewertung solle hier
erfolgen
o
Im Anschluss erfolgt eine
Bearbeitungssperre der Belege
•
Die Bestandsfortschreibung findet bis zum Wirtschaftsjahresende mit
geeigneten Mitteln statt.
•
Die Inventur wird eröffnet.
•
Die Bestände der Artikel ohne PIV werden zum Erhebungstag erfasst.
•
Die Bestände der Artikel mit PIV werden zum Erhebungstag vorgetragen (
Inventurende-Funktion
)
•
Am Jahresende wird sichergestellt,
o
dass alle Artikel gezählt
wurden
o
dass alle Lagerplätze
aufgesucht wurden
o
alle Inventurbelege (5055)
gesperrt und in die FiBu übertragen wurden

---

## Abwicklung

Abwicklung
Schnelle Teildisposition(F6)
Siehe Schnelle Teildisposition
Artikel kopieren (CF11)
Ein Artikel, der auf einem anderen Lager angelegt ist,
kann in das ausgewählte kopiert werden.
Partieauswahl (SF7)
Manuelle Zuordnung zu einer Partie.
Artikel/Lager wechseln
Öffnet die Maske der Artikel Änderung (
Lagerumbuchung
).

---

## Aktivkennzeichen

Aktivkennzeichen
Das Aktivkennzeichen steuert das erscheinen dieses
Artikels in der Schnellerfassung, ein auf inaktiv gesetzter Artikel wird bei der
Vorgangserfassung nicht angezeigt.
Hiermit können kurzfristig nicht lieferbare oder nicht
im Lager vorhandene Artikel schnell aus der aktive Verarbeitung genommen
werden.

---

## Allgemein – Allgemeine und generelle Vorgangszuordnungen

Allgemein – Allgemeine und generelle Vorgangszuordnungen
Feld
Beschreibung
Periodenbehandlung
F3
      Funktion zur Periodenbehandlung
•
Jahresgrenzen/Inventurgrenzen
•
Lieferdatum nie
      in geschlossener Periode
Lager / Strecke
F3
      Funktion zur Auswahl Lager oder Strecke
Barabwicklung Vorgang (ohne
      Kassensystem)
F3
      Auswahl Ja oder Nein
(Kassen)Konto für
      Barabwicklung
F3
      Auswahl für Konto Barabwicklung
Eigener Nummernkreis bei
      Stornobelegen
Auswahl Nummernkreis bei
      Stornobelegen
Arbeitsregelnummer
Auswahl für
      Arbeitsregeln
Rohware Vorerfassung
Kennzeichen für Lieferscheine im
      Ein- und Verkauf:
-
ohne: Keine
Rohware-Wandlung
möglich
-
möglich:
Rohware-Wandlung
möglich kann erfolgen,
wenn bestimmte Voraussetzungen vorhanden
      sind
-
geprüft: Der Beleg wird
      bei Belegabschluss auf Einhaltung der Voraussetzung für die
Rohware-Wandlung
geprüft.
Kokore Druckverhalten
Kokore Druckverhalten
Artikel Itembox
Angabe einer alternativen
      Itembox
Kunden Itembox
Hier
      kann eine alternative Itembox angegeben werden, die in der
      Vorgangserfassung zur Verfügung stehen soll, um Kunden auszuwählen. So
      kann z.B. eingerichtet werden, dass bei Angeboten eine
      Interessenten-Auswahlliste, bei Rechnungen nur eine Liste der Kunden
      angezeigt wird, die Ware erhalten haben.
Nach
      Druck korrigierbar
Hier
      kann pro Vorgangsklasse und Unterklasse eingestellt werden ob der Vorgang
      nach dem Druck korrigierbar ist.
Diese Funktionalität wurde aus dem
      Steuerparameter 67 ‚Rechn./Gutschr. nach Druck korrigierbar’ hierher
      übertragen und der Steuerparameter wurde deaktiviert.
Die Einstellung
      aus dem Steuerparameter wurde für die Vorgangsklassen 700-890, 1700-1890
      und >5000 übernommen.
Vorbelegung ist Nein.
Sofort Fibu Übertrag beim Drucken
      (nur für Druckmodul)
Hier
      wird entschieden, ob beim Drucken sofort ein Fibu Übertrag
      sta
[...]


---

## Allgemeine Varianten

Allgemeine Varianten
In diesen Varianten kann bewusst nur nach
Geschäftsjahr abgegrenzt werden, da diese Varianten dazu dienen sollen noch
offene Inventuren zu vervollständigen. Die Filterung würde unserer Ansicht nach
eine unzulässige Einschränkung bedeuten.
Die Varianten nach Artikel und Partie haben jeweils
eine Funktion, die es erlaubt die markierten Einträge mit der Menge 0 zu einem
definierten Erfassungstag auszubuchen.
Dazu werden Inventurdifferenzbelege erstellt, deren
Umfang mit Hilfe des Steuerparameters
1045 - Permanente Inventur Blockgröße
festgelegt
werden. Auch für Artikel bzw. Partien, die keinen Buchbestand haben, wird der
Vollständigkeit halber ein solcher Eintrag erstellt werden.
Soweit in den folgenden Varianten der Begriff
„Lagerplatz“ verwendet wird, so ist damit der Referenz-ERP-Lagerplatz gemeint, der in
der Verwendung zweckmäßiger Weise dem überschaubaren physikalischen Lagerplatz
entsprechen sollte.

---

## Archiv-Auslagerung

Archiv-Auslagerung
-40000
Parameter
-40001
Device nicht verfügbar

---

## Artikel

Artikel
Die Artikelvarianten richten sich an Benutzer, die
ihre Bestände ausschließlich auf Artikelbasis zählen. Hier werden (ggf. unter
Angabe eines Lagerplatzes) jene Artikel angezeigt, die im gewählten
Geschäftsjahr noch nicht mit einer Inventur erfasst wurden.
Dabei werden auch jene Artikel angezeigt, die einen
Bestand von 0 haben, jedoch im Geschäftsjahr bewegt wurden. Hier gilt es
sicherzustellen, dass diese tatsächlich keinen Bestand haben.
Hinweis
Um diese Auswahl aussagekräftig zu machen, ist
Voraussetzung, dass hier stets gesamte Artikelmengen (ggf. pro Lagerplatz)
inventarisiert werden.

---

## Artikel

Artikel
Der Artikel wird Lagerbezogen angewählt, es können in
einer Liste mehrere Artikel aus mehreren Lagern geführt werden, es wird bei der
aktiven Auswahl in der Schnellerfassung aber nur das unter VKONS vorgegebene
Lager bearbeitet.

---

## Artikelkopie aus Sortimentslager

Artikelkopie aus Sortimentslager
Wenn der gewünschte Artikel im aktuellen Lager nicht
angelegt ist, jedoch im Sortimentslager definiert wurde, so kann der Artikel von
dort kopiert werden. Rufen Sie dazu die Funktion „Kopie von Sortimentslager“
auf. Sie können dann einen Artikel aus dem Sortimentslager auswählen und auf das
aktuelle Lager kopieren. Eine Nachbearbeitung des gerade kopierten Artikels
können Sie dort vornehmen.
Nach dem Verlassen der Artikelkopie wird der Artikel
in die Erfassungsmaske übernommen.

---

## Artikel / Sorte / Lager

Artikel / Sorte / Lager
Zuerst wird versucht, eine Sortennummer zu lesen.
Klappt dies, so wird daraus in Abhängigkeit vom Parameter ART_AUS_SORTx eine
Artikelnummer per Umsetztabelle ermittelt (ART_AUS_SORT=1) oder auch nicht
(ART_AUS_SORT=0). Der Fehlwert des Artikels für die Umsetzung ist im Parameter
ART_DEFAULT hinterlegbar. Kann dieser Parameter nicht ausgewertet werden, so ist
ART_DEFAULT = „###“, was sicher einen Fehler herbeiführt. ART_AUS_SORTx steht,
wenn nicht anders bestimmt defaultmäßig auf 0.
Schlägt das Lesen der Sortennummer jedoch fehl, so
wird in jedem Falle versucht, eine Artikelnummer einzulesen.
(Konvertierungsparameter für die Umsetzung von Sorte
nach Artikel: SORTARTxx, weitere Parameter: ART_DEFAULT, ART_AUS_SORTx,
Positionsparameter: SOR_SAx, ART_SAx)
Anschließend wird die Lagernummer gelesen. Schlägt
dies fehl, wird die Lagernummer aus dem 2. Scriptaufrufparameter verwendet. Ist
auch diese leer, zieht der Wert aus LAGER_DEFAULT. Ist dieser leer, wird die
Lagernummer mit der kleinsten im Artikelstamm vorgefundenen Lagernummer für den
betreffenden Artikel belegt. Die Paarung Artikel – Lager wird validiert. Bei
einem Fehler wird folgender Satz ins Fehlerprotokoll geschrieben: „ART. [...] o.
LG. [...] falsch, Datei [...], Übern. #..., Zl. #...“
Der Satz wird dann nicht importiert.
(Positionsparameter: LG_SAx, weitere Parameter:
LAGER_DEFAULT)
Abhängig vom Parameter SORT_AUS_ARTx wird nun aus
einer Umsetztabelle aus der Artikelnummer eine Sortennummer ermittelt
(SORT_AUS_ARTx=1) oder auch nicht (SORT_AUS_ARTx=0). SORT_AUS_ARTx und
ART_AUS_SORTx einer Satzart x können nicht gleichzeitig auf 1 gesetzt
werden.
SORT_AUS_ARTx steht, wenn nicht anders bestimmt
defaultmäßig auf 0.
Falls SORT_AUS_ART = 0, folgt das Einlesen der
Sortennummer. Falls dies nicht klappt, wird die in Parameter SORTE_DEFAULT
eingestellte Sorte vorgegeben, die auf 0 steht, wenn nicht anders definiert.
(Parameter: SORT_AUS_ARTx, SORTE_DEFAULT)
Über den Par
[...]


---

## Begriffsdefinitionen

Begriffsdefinitionen
Namen der Ware
Je nachdem wo sich Ware rechnerisch befindet, hat sie
      in Referenz-ERP unterschiedliche Namen.
Eigenware
Als
      Eigenware wird Ware bezeichnet, die
eigenes Eigentum
ist und
      auf dem
eigenen Lager
liegt.
      Diese Ware ist für den Zugriff, die Verarbeitung und die physikalische
      Überprüfung sofort verfügbar.
Fremdlager
Mit
      Fremdlager bezeichnet man Ware, die zum
eigenen Eigentum
zählt,
      jedoch (noch) auf einem fremden Lager liegt. Dies ist unmittelbar nach
      einem Voreinkauf und vor Anlieferung der Ware der Fall. Diese Ware ist
      physikalisch nicht verfügbar.
Fremdware
Als
      Fremdware bezeichnet man Ware, die einem Dritten gehört, jedoch (noch) auf
      dem
eigenen Lager
liegt.
      Dies kann unmittelbar nach dem Vorverkauf und vor der Abholung der Fall
      sein. Diese Ware ist physikalisch vorhanden, muss u.U. auch versichert
      werden, wird bei einer Inventur auch gezählt, jedoch schließlich aus dem
      Bestand herausgerechnet.
Läger
Je nachdem, wessen Lager es zu beschreiben gilt, gibt
      es auch hier unterschiedliche Begriffe.
Eigenes Lager
Dieses Lager enthält
Eigenware
und
Fremdware
. Die Ware ist
      u.U. physikalisch im gleichen Lager (Gebäude) untergebracht.
Fremdes Lager
Dieses Lager gehört einem Dritten,
      der Ware, die zum
eigenen Eigentum
zählt in
      seinem Lager u.U. neben seiner eigenen Ware stehen hat.
Eigentum
Je nachdem, wessen Ware es zu beschreiben gilt, gibt
      es auch hier unterschiedliche Begriffe.
Eigene Ware
Eigene Ware kann entweder als
Eigenware
physikalisch verfügbar sein oder als
Fremdlager
-Ware in einem
      fremden Lager stehen. Dieser Begriff darf auf keinen Fall mit dem Wort
Eigenware
verwechselt werden, da diese nur einen Teil des Begriffs darstellt.
Fremde Ware
Fremde Ware steht im eigenen Lager,
      gehört jedoch einem Dritten.

---

## Übersicht über permanente Inventuren

Übersicht über permanente Inventuren
Inventur
Permanente Inventur
Inventurbelege und Bewertungen
In der o.g. Anwendung gibt es Varianten,
inventarisierte Artikel und Partien anzusehen und auch eine Variante, die
Inventurvorgänge des Typs Differenzbelege anzeigt.
Diese Belege können an dieser Stelle angesehen,
gedruckt, storniert, ggf. bearbeitet und auch an die FiBu übertragen werden.

---

## Übertragung Anteile

Übertragung Anteile
Bei der Übertragung
von Mitgliedskonten ( Geschäftsübergabe oder Todesfall ) handelt es sich um
einen Sonderfall, der satzungsgemäß häufig einen Sonderstatus erlangt. Es wird
bei der
Funktion Übertragen davon ausgegangen, dass Übertragungen immer
den kompletten Bestand des Quellkontos behandeln.
Im Grunde ist dieser Vorgang aber eine Kombination
mehrerer Arbeitsschritte:
Das abgebende Konto (Q) überträgt Anteile an das
empfangende Konto (Z)
Kündigung
Q
Zeichnung         Z
Auszahlung
Z
Einzahlung        Z
Die entstehenden Posten auf Q ( Haben ) und Z ( Soll )
sind über ein geeignetes Durchgangskonto auszugleichen.
Die Funktion
Übertragen CF7
öffnet folgende
Eingabefelder:
Felder
Zielmitgl. KndNr.
Hier
      wird die Kundennummer des Zielkunden angegeben.
Zieldatum
Bemerkung zum Vorgang
Hier
      kann eine Bemerkung zum Vorgang eingetragen werden. (60
      Zeichen)
Achtung
Es sind hier nur solche Konten zugelassen, die einer
Mitgliedsnummer zugeordnet sind.
Ggfs. ist also zunächst eine
Mitgliedsnummer auf dem Zielkonto zuzuordnen.
Es wird in der Bearbeitungsmaske das jeweilige
Gegenkonto vermerkt, um die Verfolgung zu erleichtern.
Es können keine Anteile übertragen werden, wenn der
Zielkunde nicht als Gesellschafter eingerichtet worden ist.

---

## Besonderheiten der Artikelerfassung

Besonderheiten der Artikelerfassung
Lager, Lagerplatz, Zusatzinformation, Rabatt
Bei Einschaltung weiterer Optionen kann sich der
Erfassungsbildschirm folgender­maßen darstellen:
Durch Steuerungsparameter (im Bereich
“Vorgangsbearbeitung Warenpos.”) kann eingestellt werden, ob und in welcher
Weise eine Lagernummer-Eingabe inner­halb der einzelnen Warenposition
(natürlich nur bei Neuerfassung) und eine Lagerplatzzuordnung möglich ist. Es
kann zwischen “ohne Lager” (wie bisher), “nur Anzeige”, “änderbar” (nur nach
Artikel­nummer-Eingabe mittels Pfeil-nach-oben-Taste) und “Einstieg” (die
Lagernummer ist das erste Eingabefeld) gewählt werden.
Die Eingabe der Zusatzinfo wie auch die Skontieingabe
wird über die EPA- Steuerung ermöglicht; die Rabattabfrage steuert der Parameter
“manuelle Rabatte zu­lässig” im Artikel.
Kontrakte, Partien
Artikel mit Partiezwang oder vorliegende Kontrakte für
den Kunden und Artikel erfordern manuelle bzw. automatische Zuordnungen. Auf die
Abläufe wird im Abschnitt Kontrakte bzw. Partien eingegangen.
Anlegen nicht vorhandener Artikel in
Standard-Vorgängen
Analog zur Umbuchung kann man auch während der
normalen Standardvorgänge (insbesondere wohl sinnvoll im Einkauf und bei
Lagerumbuchungen) Artikel in einem Lager anlegen, in dem sie bisher fehlen.
Die Vorgehensweise ist hier aber etwas komplizierter,
weil ja noch kein Artikel (im Abgangslager) selektiert worden ist, den man auf
das (Zugangs-)Lager kopieren könnte.
Daher muss man zu diesem Zweck (z. B. nach
fehlgeschlagener und mit
ESC
abgebrochener Suche des Artikels)
SF11
betätigen. Es öffnet sich ein
Minifenster für die Auswahl des zu kopierenden Artikels, ggf. bereits mit einer
Auswahlmaske (Itembox) obendrauf. Nach erfolgter Auswahl des Artikels und
Bestätigung der Korrekt-Abfrage wird der selektierte Artikel in das zuvor
eingestellte Lager kopiert und ist damit bebuchbar.

---

## Bestandsauswertungen

Bestandsauswertungen

---

## Bestandsbewertung

Bestandsbewertung
Jeder Artikel wird einer Bewertungsgruppe zugeordnet.
Jede Bewertungsgruppe ist mit einer Bewertungsmethode verbunden. Die Formen der
Bewertung sind somit je Artikel einstellbar.

---

## Bestandsführung und Inventur

Bestandsführung und Inventur
Stichworte:
körperliche Aufnahme
Eigenbestand
Fremdbestand
Inventurbestand
Inventurbewertung
Mit der körperlichen Aufnahme wird der tatsächlich
vorhandene Lagerbestand am Erhebungstag festgehalten. Die Zählmenge umfasst also
stets Eigen- und Fremdmengen. Auf den Eigenbestandsanteil bezogen wird die
Inventurdifferenz am Erhebungstag festgestellt und auf den Inventurstichtag als
Inventurmenge fortgeschrieben. Die Bewertung erfolgt per Inventurstichtag.

---

## Bestandstyp für Rücknahmen (WaBewBestTypReverse)

Bestandstyp für Rücknahmen
(WaBewBestTypReverse)
Der Bestandstyp für Rücknahmen findet sich in der
Tabelle Warenbewegung als Feld WaBewBestTypReverse.
Neu eingeführt wurden mit Einlagerung und Kommission
auch die Rücknahmen / Rückgaben.
Für diesen Zweck ist das Kennzeichen
WaBewBestTypReverse eingeführt worden. Dieses wird jeweils bei einer
Rückabwicklung von Vorverkauf auf 1, bei Voreinkaufs-Rückabwicklung auf 2, bei
Abholung eingelagerter Ware auf 3 und bei Kommissions-Rücknahme auf 4
gesetzt.

---

## Bestandstyp (WaBewBestTyp)

Bestandstyp (WaBewBestTyp)
Der Bestandstyp findet sich in der Tabelle
Warenbewegung als Feld WaBewBestTyp.
Vor Einführung von Einlagerung gab es neben Einkauf
und Verkauf bereits Voreinkauf und VorVerkauf mit ihren zugehörigen
Anlieferungen bzw. Abholungen.
Die Buchungen der Anlieferung und Abholung waren
Bestandsrelevant, wurden also mit dem Kennzeichen WaBewBestTyp = 1 für
Vorverkaufsanlieferung und WaBewBestTyp = 2 für Voreinkauf gekennzeichnet.
Kommt es bei einer Kommission zu einem Verkauf der
Ware, so wird dies eigentlich erst Bestandsrelevant. Deshalb wird hier der
Bestandstyp auf 4 gesetzt. Bei der Vereeinahmung einer eingelagerten Ware wird
der Bestandstyp mit 3 gekennzeichnet.

---

## Bestellwesen

Bestellwesen
Mehr Transparenz im Unternehmen.
Optimieren Sie Ihre täglichen Abläufe im Bestellwesen
und sparen Sie dadurch wertvolle Zeit und Geld.
Eine optimale Steuerung Ihrer Lagerbestände erreichen
sie durch automatische Bestellvorschläge
anhand von Soll-, Melde- und Mindestbeständen.
Engpässe in der Bestandführung werden erkannt und
verhindert, somit wird gewährleistet das Kundenaufträge termingerecht bedient
werden können.
Nachfolgend wird die Einrichtung und Abwicklung in
Referenz-ERP beschrieben.

---

## Einlagerung

Einlagerung
-12000
Einlagerung: Kontrakt konnte nicht angelegt werden
-12001
Einlagerung: Fehler beim Setzen der Kontraktklasse
-12002
Einlagerung: Fehler beim Setzen der
Kontraktunterklasse
-12003
Einlagerung: Fehler beim Setzen der Kontraktnummer
-12004
Einlagerung: Fehler beim Setzen der
Kontrakteinzeltyps
-12005
Einlagerung: Fehler beim Setzen der
Kontraktmengentyps
-12006
Einlagerung: Fehler beim Setzen der Kontraktart
-12007
Einlagerung: Fehler beim Setzen des Startdatums für
den Kontrakt
-12008
Einlagerung: Fehler beim Setzen des Enddatums für den
Kontrakt
-12009
Einlagerung: Fehler beim Setzen des Fixbisdatums für
den Kontrakt
-12010
Einlagerung: Fehler beim Setzen der
Kontraktbezeichnung
-12011
Einlagerung: Fehler beim Setzen der
Mengeneinheitsnummer im Kontrakt
-12012
Einlagerung: Fehler beim Erstellen der
Kontraktzeiträume
-12013
Einlagerung: Fehler beim Hinzuügen des Artikels
-12014
Einlagerung: Fehler beim Beenden und Speichern des
Kontrakts
-12015
Einlagerung: Fehler Initialisieren des
Vorgangshelpers
-12016
Einlagerung: Fehler beim Erstellen der
Ausgangsrechnung
-12017
Einlagerung: Fehler beim Anlegen der Position in der
Rechnung
-12018
Einlagerung: Fehler beim Erstellen der
Artikelposition
-12019
Einlagerung: Fehler beim Wandeln des Kontrakts von
Normal zu Fremdwarenkontrakt
-12020
Einlagerung: Fehler beim Setzen der
Mengeneinheitsnummer
-12021
Einlagerung: Fehler beim Setzen der Mengeneinheit
Preis
-12022
Einlagerung: Fehler beim Setzen des FiBu Status 4
-12023
Einlagerung: Fehler beim Setzen des Preises
-12024
Einlagerung: Fehler beim Setzen der Preiseinheit
-12025
Einlagerung: Fehler beim Setzen des
Nicht-Bewerten-Merkers
-12026
Einlagerung: Abrechnungsparameter konnte nicht
ermittelt werden
-12027
Einlagerung: Datum ist nicht berechenbar
-12028
Einlagerung: Fehler beim Ermitteln eines INT-Eintrags
im Vorgang mit der ID
-12029
Einlagerung: Fehler beim Ermitteln eines INT-Eintrags
in der Vorgangsposition mit der ID
-12030
Einla
[...]


---

## Einlagerung / Vereinnahmung in der Rohware

Einlagerung /
Vereinnahmung in der Rohware
Das
Rohwaresystem ist für den Einkaufsbereich um die Buchungsarten Einlagerung und
(Einlagerungs-) Vereinnahmung ergänzt worden.
Grundsätzlich gilt das
Einlagerungskennzeichen wie auch das Vereinnahmungskennzeichen eines
Rohwarebeleges zunächst einmal nur für die Hauptwarenposition
(Lieferwarenposition). Für eine Sekundärwarenposition kann im zugehörigen
Abrechnungsschema jedoch festgelegt werden, ob diese das Einlagerungskennzeichen
bzw. Vereinnahmungskennzeichen der Hauptwarenposition übernehmen soll. Preise
und qualitätsbedingte Preis-Zu-/Abschläge werden für Einlagerungspositionen mit
dem Wert 0,00 belegt.
In
Qualitätsdefinitionen kann in den Feldern ‚Berechnung erfolgt‘ und ‚Ausdruck‘
erfolgt auch für Qualitäten, die sich nicht auf Einlagerungspositionen beziehen,
eingestellt werden, ob die Qualität in Abhängigkeit von Einlagerungs- und
Vereinnahmungskennzeichen (der Hauptposition) abzurechnen bzw. zu drucken ist
oder nicht. Eine entsprechende Einstellungsmöglichkeit zur Anwendung einer
Kosten-/Vergütungspositions-Berechnung befindet sich auf der Maske zur
Kosten-/Vergütungs-Merkmaldefinition.

---

## Einlagerung, Kommission, Vorein-/verkauf

Einlagerung, Kommission, Vorein-/verkauf
Im Zusammenhang mit Einlagerung und den zeitgleich
eingeführten Änderungen in Buchungsmechanismen gibt es einige technische
Hintergründe, die zu verstehen notwendig ist, um fehlerfreie Reports,
Auswahllisten und Itemboxen auch weiterhin gewährleisten zu können.
Solange die vier in der Überschrift genannten
Vorgangsarten bisher nicht angewendet wurden, so ist die Wahrscheinlichkeit
gleich null, dass unangepasste Teile der Software wie z.B. private Varianten,
Reports, Prozeduren, Views oder Itemboxen auffallen.
Spätestens mit Beginn der neuen Prozesse sollten diese
dennoch überprüft werden.

---

## EK Gutschrift

EK Gutschrift
EK-Gutschriften entstehen durch Neuerfassung oder
Umwandlung aus EK-Rechnungen. EK-Gutschriften werden als Vorgang gespeichert;
die Menge wird verbucht und vermindert den Bestand; der EK-Umsatz vermindert
sich. Referenz-ERP stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktionsname
Funktion
Erfassen F
      8
Erfassung einer neuen
      EK-Gutschrift
Stapelverarbeitung
Übernahme einer oder mehrerer
      EK-Gutschriften in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck einer
      EK-Gutschrift
Formulardruck
      F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
      F5
Korrektur einer
      EK-Gutschrift
Ansicht F6
EK-Gutschrift im Ansicht-Modus
      öffnen
Kopieren
      CF8
Kopieren der EK-Gutschrift für einen
      auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren
      F7
Stornieren (Löschen) der
      EK-Gutschrift
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Archiv
      ansehen
Anzeige archivierter
      Vorgänge
Partien
      nachtragen
nachträgliche Zuordnung von
      Partien
Wiedervorlage
      CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel
      ändern
manuelle Änderung von
      Weiterverarbeitungsparametern
FiBu
      Übertrag
Übergabe an die
      Finanzbuchhaltung

---

## Erfassung der permanenten Inventur

Erfassung der permanenten
Inventur
Wie die
normale
Inventur muss die permanente
Inventur zum Jahresende an einem Stichtag abgeschlossen werden. Da eine
Inventurgruppe sowohl Artikel mit als auch ohne Kennzeichen „permanente
Inventur“ enthalten kann, werden Inventurgruppen
normal
gepflegt.
Voraussetzung für die Artikelstichtagsinventur ist,
dass an einem Tag der gesamte Bestand eines Artikels gezählt wird. Zum
Jahresabschluss ist sicherzustellen, dass Lagerplätze, die im Rahmen dieser
Zählungen nicht besucht wurden, noch erfasst werden, um
verwaiste
Ware
aufzufinden. (Siehe auch
Prüfungen permanente
Inventur
.)

---

## FutterApp

FutterApp
Bei der FutterApp handelt es sich um eine App für
Android und iOS mit deren Hilfe Vorgänge in Referenz-ERP erfasst werden können.
Außerdem ermöglicht sie die Siloverwaltung.

---

## Gutschrift

Gutschrift
Gutschriften entstehen durch Neuerfassung oder
Umwandlung aus Rechnungen. Gutschriften werden als Vorgang gespeichert; die
Menge wird verbucht und erhöht den Bestand; der Umsatz vermindert sich. Referenz-ERP
stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktionsname
Funktion
Erfassen F
      8
Erfassung einer neuen
      Gutschrift
Stapelverarbeitung
Übernahme einer oder mehrerer
      Gutschriften in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck einer
      Gutschrift
Formulardruck
      F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
      F5
Korrektur einer
      Gutschrift
Ansicht F6
Gutschrift im Ansicht-Modus
      öffnen
Kopieren
      CF8
Kopieren der Gutschrift für einen
      auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren
      F7
Stornieren (Löschen) der
      Gutschrift
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Archiv
      ansehen
Anzeige archivierter
      Vorgänge
Partien
      nachtragen
nachträgliche Zuordnung von
      Partien
Wiedervorlage
      CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel
      ändern
manuelle Änderung von
      Weiterverarbeitungsparametern
FiBu
      Übertrag
Übergabe an die
      Finanzbuchhaltung
FiBu-Eintrag
      zurücknehmen
Siehe
FiBu – Eintrag
      zurücknehmen

---

## Inventuraufnahme

Inventuraufnahme
Hauptmenü
Inventur
Inventuraufnahme
Direktsprung
[IVA]
Erfassung
Zunächst wird per
Stichtag und Inventurgruppe der zugehörige Inventurstamm bestimmt.
Erfassungsrelevante Informationen werden
angezeigt. Hier kann auch festgelegt werden, ob der Lagerplatz erfasst werden
soll und bei welchem Startfeld ab der 2. Belegzeile begonnen werden
soll.
Je nach
Einstellungen im Inventurstamm werden Belegnummer und Positionsnummer
automatisch erzeugt oder müssen erfasst werden.
Lagernummer,
Lagerplatz und Artikelnummer können je Position wechseln.
Vor Eingabe der
Menge muss die Erfassungsmengeneinheit angegeben werden, aus der sich dann die
weiteren mengenrelevanten Erfassungsfelder ergeben (Gebindefaktoren).
Es werden demnach
entweder die Menge oder die Gebindeanzahl und Gebindefaktoren eingegeben.
Die daraus
resultierende Menge wird dabei angezeigt.
Zusätzlich kann
ein %-Satz im Feld
'Restwert'
angegeben werden, der z.B. bei beschädigter
Ware zur Bewertung herangezogen wird. Anzugeben ist der Restwert als
Prozentsatz. Für eine 40%ige Abwertung wird also ein Restwert von 60 %
angegeben.
Außerdem kann
angegeben werden, dass die Bewertung zum Buchbestand erfolgen soll, die
angegebenen Werte sind dann als Schätzwerte anzusehen. Geprüft wird ob ein so
markierter Artikel in einer Zwischeninventur bereits aufgenommen
wurde.
Bei
entsprechender Einstellung im Inventurstamm, kann der Bewertungspreis mit
Preiseinheit und
Preis -
Mengeneinheit angegeben werden.
Grundsätzlich
können Inventurpositionen nicht gelöscht werden. Es kann jedoch ein
Löschkennzeichen gesetzt werden. Die Position ist dann als nicht gültig
gekennzeichnet.
Die Eingabe einer
Aufnahmemenge 0 und einer Minusmenge ist möglich. Zugelassen wird diese Eingabe
aber nur durch Freischaltung eines Steuerparameters
[SPA]
„Nullmenge bei Inventur
zulässig“.
Zusätzlich wird
ein Kennzeichen für die Art der Inventurbewertung geführt. Es kennzeichnet, ob
Bewertungen manuell oder automatisc
[...]


---

## Inventurbestand

Inventurbestand
Hauptmenü
Inventur
Inventurbestand
Direktsprung
[IVB]
Diff.-Liste (Druck)
Übersicht: Inventurabgrenzung
Beispiel 1:
Erhebungstag

Stichtag
25.12.

31.12.
gezählt =
30.000
Buchbestand: 34.000

= Differenz = -4.000
gezählt =
30.000
Zugang: 10.000 Buchbestand:
34.000
= Differenz = 6.000
Inventurbest: 40.000
Beispiel 2:
Stichtag
Erhebungstag
31.12.
10.01.
= Differenz =
-4.000
Buchbestand:
34.000
gezählt = 30.000
= Differenz = 6.000

Buchbestand:
34.000
Abgang: 10.000 gezählt = 30.000
Inventurbest: 40.000
Folgende Funktionen der Bewertung sind noch beim
Inventurbestand möglich:
Einzelbewertung (Artikelebene) F5
Alle oder einzelne Artikel können mit Hilfe dieser
Funktion individuell bewertet werden. Hierzu können die einzelnen Positionen per
Stern markiert werden und ein neuer Bewertungspreis eingetragen werden.
Die Funktion „Einzelbewertung“ kennzeichnet
Inventurpositionen stets als manuell bewertet. Nur die Funktion automatische
Bewertung, mit der Inventurpositionen der Bewertungspreis laut Bewertungsgruppe
des Artikels zugewiesen werden kann, kennzeichnet die Inventurpositionen als
automatisch bewertet.
Automatische Bewertung F9
Die Bewertung wird auf Grundlage der im Artikel
hinterlegten Bewertungsparameter für alle oder den vorher markierten Artikeln
automatisch durchgeführt.
Achtung
:
Die automatische
Bewertung überschreibt die manuellen Bewertungen.
Folgende Auswahlmöglichkeiten stehen zur
Verfügung:
-
Die automatische Bewertung kann man beziehen:
o
auf die gesamte Inventur
(unabhängig vom Auswahlbereich)
o
[...]


---

## Inventurende

Inventurende
Hauptmenü
Inventur
Inventurende
Direktsprung
[IVE]
Inventur prüfen F6
Hier wird die Inventur auf Einspielfähigkeit
geprüft:
Vortrag permanente Inventur
Wird permanente Inventur verwendet, so muss vor dem
Abschluss der Inventur ein Bestandsvortrag gemacht werden. Dies kann aber nur am
Ende des oder nach dem Erhebungstag des Inventurstammsatzes erfolgen.
Die Sonderfunktion kann hier ausgeführt werden.
Zur Bedeutung der
Sonderfunktionen
:
Alle Artikel, die
zum Inventurstichtag Bestand haben, müssen aufgenommen sein. Nun kann es
durchaus sein, dass Artikel bei der körperlichen Aufnahme nicht erhoben wurden,
weil sie tatsächlich nicht am Lager sind. Hierzu erfassen Sie entweder eine
Aufnahme mit der Menge 0 oder Sie wenden die Sonderfunktion an, mit der Sie für
derartige Artikel einen
Inventurbestand 0
zuordnen (ohne einen konkreten
Beleg dafür zu erzeugen). Die Wirkung ist in beiden Fällen dieselbe: Sie
erreichen bei der Einspielung eine Ausbuchung des Bestandes.
Alle Aufnahmen
müssen bewertet sein. Insbesondere durch den Inventurvortrag oder durch obige
Funktion erzeugte Inventurbestände können als nicht bewertet gelten. Mit der
entsprechenden Sonderfunktion definieren Sie alle
Aufnahmen als
bewertet
.
Inventur abschließen F5
Mit dem Inventurabschluss ist eine umfassende Prüfung
verbunden:
Sind die Punkte 1 – 9 nicht erfüllt, kann der
Abschluss
nicht
durchgeführt werden!
Bei den Punkten 10 – 14 erfolgt nur ein
Warnhinweis!
Folgende Varianten sollten zur Kontrolle aufgerufen
werden:
Bewegte Artikel ohne Aufnahme
Artikel mit Bestand ohne Aufnahme
Mit der Funktion
Inventur abschließen
F5
wird die Inventuraufnahme abgeschlossen.
Weitere Erfassungen oder Änderungen sind nicht mehr möglich!
Bitte wählen Sie die Option „Permanente
Inventurprüfung unterdrücken“ nur aus, wenn Sie sicher sind, dass an der
Inventur keine Artikel mit permanenter Inventur beteiligt sind. Das wird in der
Regel nur der Fall sein, wenn alte Inventuren abgeschlossen w
[...]


---

## Inventurerfassung im Lager

Inventurerfassung im Lager
Bei der Lagerplatzkennzeichnung kann es folgende
Warenauszeichnungen geben:
-
Waren - EAN auf der Ware
-
Karton – EAN auf dem Karton(GS1-Code128)
-
Partiekennung am Karton / Ware
-
Artikelnummer
Zuordnung von Lagerplätzen
Das Addon-Feld „Lagerplatz“ wird beim Scannen des
Artikels und des Regals automatisch aufgefüllt, wenn dieser unterschiedlich
ist.
Artikeleingabe
Im folgenden Beispiel gehen wir davon aus, dass die
Artikelnummer in einer Länge von 5 bis 8 Stellen vorliegt. Die Kennzeichnung
einer Partie wird über die Partieidentifikation als Code128 Barcode dargestellt
(als Precode den Textkürzel PID), die Karton als GS1-Code128 oder
Warenkennzeichnung als EAN 13.
Wird die Artikelnummer „00095“ im Scanner eingegeben,
so wird der aktuelle Bestand im Lager gezeigt:
Hier ist zu erkennen, dass die Partie 16052309
produziert worden ist, aber keine Menge dieser Partie in ein Regal „verbracht“
worden ist. Die Partie 16072101 ist im Regal 11403 mit 87 Eimern eingelagert
Per Pfeiltaste kann zwischen den einzelnen Partien
gewechselt werden. Wird nun im obigen Fall die Menge der einzulagernden Ware
angegeben, so erscheint folgendes Informationsbild:
Es ist hierbei eine Menge von 14 Eimern angegeben
worden, alternativ kann auch ein 4.2 angegeben werden, für 4 Kartons plus 2
Becher (das Zeichen „.“ ist auf der Scannertastatur besser zu erreichen als eine
Leertaste, deshalb wird zwischen Kartons und Eimern als Trennzeichen der Punkt
genutzt).
In der zweiten Zeile ist jetzt noch angegeben, dass
noch das Regal zu „Scannen“ oder einzugeben (Beachte: „R Regalnummer“) sowie die
regalspezifische Prüfziffer. Nach Scannung des Regals und Eingabe der
Prüfziffer, die am Regal vermerkt ist, sieht die Buchung dann wie folgt aus:
Lager leeren
Soll ein Lagerfach komplett geleert werden, muss die
Menge 0 des Artkels gebucht werden.
Kommt die Partienummer zu dem Artikel in der Liste
nicht vor, gibt man die 8-stellige Partienummer ein.
Weiterer Art
[...]


---

## Inventurgruppe

Inventurgruppe
Hauptmenü
Inventur
Inventurgruppen
Direktsprung
[IVG]
Die Inventurgruppe verbindet die Artikel mit der Art
der durchzuführenden Inventur, die im Detail im Inventurstamm beschrieben wird.
Für den Standardfall, dass die Inventur zum Stichtag über alle Artikel mit der
gleichen Methode durchgeführt wird, ist nur eine Inventurgruppe erforderlich.
Diese ist als “Inventurgruppe Nr.
1
” mit dem Text “
Hauptinventur JW
” in der Basis-DB
eingerichtet. Sollen jedoch Teilinventuren für Artikelgruppen zu
unterschiedlichen Zeitpunkten erhoben werden, so sind so viele Inventurgruppen
wie es Artikelgruppen gibt anzulegen. Dazu muss eine laufende Nr. sowie ein
Text, z.B. “Bezeichnung der WG ......”, vergeben werden (Zwischeninventur).
Hinweis:
Die Inventurgruppe innerhalb eines
Artikels kann nur gepflegt werden, wenn
•
Das ausgewählte Geschäftsjahr weder geschlossen noch gesperrt ist.
•
Es im ausgewählten Jahr Inventur-Bestandseinträge zum Artikel gibt.
•
Im angegebenen Zeitraum bereits eine Inventur eröffnet wurde.

---

## Inventurmengenabweichungsgruppe

Inventurmengenabweichungsgruppe
Hauptmenü
Inventur
Inventurmengenabweichungsgruppe
Direktsprung
[IVMAG]
„5 % Klausel für Inventurdifferenzen“
Speziell erdacht für Schüttgüter kann eine
Sonderregelung für Inventurdifferenzen aktiviert werden. Häufig werden hier
Aufnahmemengen nur geschätzt. Weicht die Aufnahmemenge nur gering von der
Buchmenge ab (Sprich: Schafft die Inventurdifferenz die 5% Hürde nicht), so wird
statt der Zählung die Buchmenge als Inventurmenge verwendet.
Zur Realisierung wird das Artikelmerkmal
„Inventurmengenabweichungsgruppe“ eingeführt. In einer solchen Gruppe wird die
Höhe der „Hürden“ in Form eines Prozentsatzes definiert. Weicht die Zählung von
der Buchmenge um weniger als diesen Prozentanteil nach unten oder nach oben ab,
so wird die Zählung als zu vernachlässigen erkannt und die Buchmenge geht in die
Inventur ein.
Diese Sonderregelung greift dann für solche Artikel,
denen eine entsprechende Inventurmengenabweichungsgruppe zugeordnet wurde.
Standardmäßig ist diese Sonderregel abgeschaltet.
Anmerkung 1
: Die Aufnahmemengen werden durch
Anwendung der Sonderregelung  nicht verändert. Die abweichende
Interpretation wirkt sich auf Auswertungen bezüglich des Inventurbestands, auf
Differenzlisten und natürlich auf die Inventurbuchung aus.
Anmerkung 2
: Die Sonderregel ist nicht
anwendbar, wenn die Inventur über Partien aufgenommen wurde.

---

## Inventur / Mobile Datenerfassung MDE

Inventur / Mobile Datenerfassung MDE
Übersicht
Die Übernahme per MDE-Gerät wird im Fehlerprotokoll
[FEHLP]
protokolliert.
Ansicht
MDE-Datei
Inventuraufnahmen per mobiler
Datenerfassung
Bei der mobilen
Datenerfassung wird der Inventur-Stichtag zu einer Aufnahme nicht mitgeliefert.
Es wird die älteste offene Inventur als Inventurstichtag vorbelegt, jedoch kann
alternativ auch ein anderer Stichtag gewählt werden.
Falls aus der MDE
ein Bewertungspreis übergeben wird, so gilt die Aufnahme als manuell
bewertet.
Löschen von
Belegen der Mobilen Datenerfassung
Unverarbeitete
Belege lassen sich nur über die Einzellöschung entfernen. Eine
Sammel-Löschfunktion kann auf alle fehlerhaften bzw. verarbeiteten MDE Belege
angewandt werden.
Auf
Spezialitäten sei hier noch einmal hingewiesen:
Die MDE
Schnittstelle enthält keine Mengen- oder Preisbezüge. Die Mengen werden in der
vereinbarten Lager-Mengeneinheit erwartet, Bewertungspreise bezogen auf die
EK-Preismengeneinheit und in dem für den Artikel vereinbarten Preisfaktor
EK.
Die
erforderlichen Optionen für die MDE Übernahme müssen eingerichtet
sein.
Die MDE Übergabe
erfolgt nicht nach Inventurgruppen getrennt. Die Inventurgruppen für die
einzuspielenden Artikel müssen angelegt und eröffnet sein, ansonsten laufen
diese Artikel ins Fehlerprotokoll.
Inventuraufnahme
in Filialen
Wenn nicht
Branchen-ERP-Standards benutzt werden:
die Tabellen
Inventurstamm, Inventurgruppe, Inventurbeleg replizieren, nicht aber
Inventurbestand.
Zur Organisation:
Inventurgruppen müssen filial-spezifisch abgegrenzt werden. Auf diese Weise wird
sichergestellt, dass alle Betriebsstätten ihre eigenen Nummernkreise (Anlegen
nicht vergessen) für Inventurbelege erhalten.
Filialen haben
nur Zugriff auf die Anwendung „Inventuraufnahme
[IVA]
“.
Alternativ:
Inventurbeleg nicht replizieren. Nach Fertigstellung der Aufnahme in den
Filialen Tabelle entladen und in Zentrale beladen.
Inventurbewertung
Die Bewertung der Inventur kann auf unterschied
[...]


---

## Inventurvorbereitung

Inventurvorbereitung
Hauptmenü
Inventur
Inventurvorbereitung
Direktsprung
[IVV]
Die Inventurvorbereitung besteht aus zwei wesentlichen
Punkten.
Inventureröffnung:
Der Eröffnungsvortrag kennzeichnet alle Artikel, die
zum Eröffnungszeitpunkt einen Buchbestand und die entsprechende Inventurgruppe
haben. Die Inventureröffnung (
F5
) kann
aus der Auswahl gestartet werden, wenn der entsprechende Inventur-Stichtag
eingegeben wird.
Optional können alle Artikel mit Erhebungsmenge 0
(Null) in den Inventurbestand vorgetragen werden, die zum Zeitpunkt der
Inventureröffnung Bestand haben. Auf diese Weise hat man schon während der
Inventuraufnahme eine gewisse Kontrolle über die Vollständigkeit der Aufnahmen.
Vorläufige Differenzlisten weisen dann auch Inventurdifferenzen für noch nicht
aufgenommene Artikel aus. Die endgültige Vollständigkeitskontrolle kann
natürlich erst beim Inventurabschluss erfolgen.
Druck der Zähllisten:
Die Zähllisten können ebenfalls aus der Auswahlliste
heraus gestartet werden und dienen lediglich zur Unterstützung der Zählung.
Es gibt
3 Arten
von Zähllisten:
1.
Inventurzählliste vor der Inventureröffnung (über alle Artikel)
2.
Inventurzählliste nach der Inventureröffnung (über alle Artikel, die eröffnet
wurden)
3.
Blankozählliste (ohne Artikel)

---

## Lagerplatzumbuchung

Lagerplatzumbuchung
Lagerplatzumbuchungen werden unter dem Direktsprung
[LGPU] verwaltet. Sie werden als Vorgänge gespeichert. Referenz-ERP stellt folgende
Bearbeitungsfunktionen zur Verfügung:
•
Lagerplatzumbuchung F 8
Erfassung einer neuen Lagerplatzumbuchung
•
Erstdruck
F2
Erstdruck einer Lagerplatzumbuchung.
•
Formulardruck
F10
Wiederholungsdruck
•
Korrektur
F5
Korrektur einer Lagerplatzumbuchung
•
Vorschau
F11
Druckvorschau
•
Stornieren
F7
Stornieren (Löschen) der Lagerplatzumbuchung
Siehe auch Erfassung des
Positionsteils bei Umbuchungen

---

## Lager

Lager
Auf diesem Feld steht eine F3 Auswahl zum Lagerstamm
zur Verfügung.

---

## Lagerplatz (Waagendatenimport-/-export)

Lagerplatz (Waagendatenimport-/-export)
Kann die Lagerplatznummer nicht ermittelt werden, wird
sie mit 0 belegt. Eine Validierung findet nicht statt.
(Positionsparameter: LP_SAx)

---

## Lagerplätze

Lagerplätze
Für jene Benutzer, die „Lagerplatz“ als physikalischen
und zudem überschaubaren Lagerplatz definieren, ist die Variante Lagerplätze
gedacht. Durch fehlerhafte Einlagerung kann es vorkommen, dass Ware auf einem
Lagerplatz eingestellt wird, dieser jedoch im Verlauf des Jahres nicht durch
eine Inventur erfasst wird. Werden nun zum Jahresende die nicht besuchten
Lagerplätze aufgesucht, so kann diese „verwaiste Ware“ gefunden oder die Leere
des Lagerplatzes bestätigt werden.
Die Variante enthält eine Funktion, die es erlaubt,
die markierten Lagerplätze mit einem definierten Datum als besucht zu
kennzeichnen.
Hinweis
Um diese Auswahl aussagekräftig zu machen, ist
Voraussetzung, dass hier stets alle Artikel bzw. Partien des Lagerplatzes
aufgenommen werden.

---

## LVS unbesuchte Lagerplätze

LVS unbesuchte Lagerplätze
Da zur Vollständigkeitsprüfung ein Besuch des
Lagerplatzes im LVS notwendig ist, muss dieser im Verlauf des Wirtschaftsjahres
aufgesucht werden. Ist auf einem Lagerplatz ein Artikel inventarisiert worden,
so gilt dieser Lagerplatz als besucht. Auch der Besuch des Lagerplatzes mittels
LVS-Funktion „Lagerplatzvisite“ erledigt dies.
Alle noch nicht besuchten Lagerplätze müssen manuell
aufgesucht und ihr Inhalt kontrolliert werden.
Dies gilt für alle Lagerplätze in einem Lager, das
im Lagerstamm
das Kennzeichen
„Bei Inventurabschluss als perm. Inventur prüfen“ trägt.

---

## LVS-Varianten

LVS-Varianten
Bei einer permanenten Inventur mit dem
Lagerverwaltungssystem LVS gibt es die folgenden Varianten:

---

## Nebenbuchhaltung mit und ohne Kontrakt

Nebenbuchhaltung mit und ohne Kontrakt
Werden Waren vorverkauft, voreingekauft, eingelagert
oder als Kommissionsware ausgelagert, so muss die Bestandsführung nicht
zwangsweise über einen Kontrakt als Nebenbuchhaltungswerkzeug abgewickelt
werden. Für Einlagerung und Rohware werden keine Nebenbuchhaltungskontrakte mehr
angeboten.
Es werden bei fehlendem Kontrakt Nebenbuchhaltungen
für nicht kontraktierte Mengen geführt.
Die Tabelle „ArtibestandFremdkonto“ führt die Bestände
von Vorein-/Vorverkaufsbuchungen sowie Einlagerung und Kommission incl. der
AdHoc-Updates, also Bestandsänderungen, die der Mandantenserver noch nicht
verbucht hat pro Kunde und Artikel.
So kann z.B. bei der Abholung vorverkaufter Ware nur
die Menge abgeholt werden, die als nicht kontraktierte Menge für diesen Kunden
und diesen Artikel vorverkauft wurde.

---

## Nicht unterstützte Features

Nicht unterstützte Features
Derzeit werden von der Waagen-Schnittstelle nicht
offiziell unterstützt:
Rohwarenbelege mit mehreren Warenpositionen
Satzart Umlagerung und Produktion
Einlesen von Jahrnummer und Perinummer

---

## Parameter an F3-Auswahlen (Itemboxen) übergeben

Parameter an F3-Auswahlen (Itemboxen) übergeben
Ab und an steht man vor der Aufgabe, dass man in einer
Itembox die Auswahl schon über bereits erfasst Werte einschränken möchte. Ein
typisches Beispiel wäre, dass man bereits die Lagernummer erfasst hat und
anschließend in der Itembox für Artikel nur noch die Artikel dieses Lagers sehen
möchte. Zur Lösung dieses Problems steht die Anwendung „Itembox-Parameter“
(Direktsprung AIP) zur Verfügung. Dort kann man dann Angeben, dass zu einer
Itembox ein Parameter gesetzt wird, wie es von ITEM_PAR bekannt ist.
Hier wird für die Itembox die man auf das Feld
„ais1.ArtikelNummer$“ (auch hier auf Groß- und Kleinschreibung achten!) gelegt
hat der Parameter AND_LAGERNUMMER – dieser muss entsprechend in der Itembox
vorhanden sein – der Wert „and (Lagernummer=:ais1.LagerNummer$)“ hinterlegt.

---

## Partien

Partien
Die Partievarianten richten sich an Benutzer, die ihre
Bestände ausschließlich auf Partiebasis zählen. Hier werden (ggf. unter Angabe
eines Lagerplatzes) jene Partien angezeigt, die im gewählten Geschäftsjahr noch
nicht mit einer Inventur erfasst wurden.
Dabei werden auch jene Partien angezeigt, die einen
Bestand von 0 haben, jedoch im Geschäftsjahr bewegt wurden. Hier gilt es
sicherzustellen, dass diese tatsächlich keinen Bestand haben.
Ob bei der Auswahl auch bereits erledigte Partien
berücksichtigt werden sollen kann separat gewählt werden.
Hinweis
Um diese Auswahl aussagekräftig zu machen, ist
Voraussetzung, dass hier stets gesamte Partiemengen (ggf. pro Lagerplatz)
inventarisiert werden.

---

## Permanente Inventur mit Hilfe des Lagerverwaltungssystems

Permanente Inventur
mit
Hilfe des Lagerverwaltungssystems
Für die Erfassung soll die
Vorgangsimport-Schnittstelle LVS
verwendet werden. Dort
finden sich mit den Unterklassen
21
und
61
zwei Möglichkeiten einer
inventurfähigen Zählung.
Durch geeignete organisatorische Maßnahmen
(Inventurlisten) wird der Bestand eines Artikels und aller seiner Partien
sukzessiv aufgenommen.
Nach der Erfassung einer Ladeträgermenge wird die
Tatsache, dass dieser Ladeträger gezählt wurde, in den Ladeträgerbewegungen
mittels Kennzeichen geplante Inventur festgehalten.
Zugleich wird jeweils geprüft, ob zu diesem Zeitpunkt
alle Ladeträger im System, die diesen Artikel beinhalten, innerhalb des
Zählzeitraums (SPA
1045
) bzw. im
Wirtschaftsjahr gezählt wurden.
Ist dies der Fall, so wird dieser Artikel für die
Erstellung eines Bestandsbelegs vorgemerkt. Weitere bestandsverändernde Zu- oder
Abgänge sind möglich. Die Änderung der Buchbestände erfolgt erst bei der
Erstellung eines Inventurbestandsbeleges (
5055
).
Die Erstellung des Bestandsbuchungsbeleges (
5055
) kann manuell in der Variante
Inventur
Permanente Inventur
Permanente Inventur Prüfungen
LVS
ungezählte Artikel erstellt werden oder
automatisch
über ein Event
.

---

## Permanente Inventur ohne LVS

Permanente Inventur ohne
LVS
Es ist denkbar, die Bestandsfortschreibung durch
andere Mittel als mit LVS sicherzustellen. In diesem Fall kann in den
Inventurbestandsbeleg (Vorgangsklasse
5055
) nur die Summe der Artikel- und
zugehörigen Partiemengen eingetragen werden.
Ein Hilfsmittel zur Addition einzelner Zählungen wie
der Inventurbeleg der Stichtagsinventur gibt es hier nicht!
Es muss der Artikel stets mit all seinen Partien
erfasst werden, damit die Bestände auf Artikel und Partien durch den Beleg
korrigiert werden.
Darüber hinaus muss sichergestellt werden, dass
zwischen Beginn der Zählung und Buchung des Beleges keine weiteren
Bestandsveränderungen stattfinden, die von der Zählung nicht erfasst werden.
Hinweis:
Auf dem Lager stehen unter Umständen drei Arten von
Ware:
•
Einlagerung – Fremde Ware, die im eigenen Lager eingelagert und als
Einlagerung gebucht wurde.
•
Vorverkauf – Fremde Ware, die bereits verkauft, jedoch vom Käufer noch
nicht abgeholt worden ist.
•
Eigenware – Ware, die im eigenen Lager steht und zu diesem Betrieb
gehört.
Die Soll-Menge einer Zählung wird stets mit der Summe
dieser drei Bestände verglichen. Ergibt sich daraus eine Differenz, so wird
diese stets nur in der Eigenware korrigiert. Das kann dazu führen, dass der
Bestand der Eigenware negativ angezeigt wird.

---

## Physikalischer Bestand

Physikalischer Bestand
Der Lieferbestand kann zum einem vorzugebenden
Stichtag abgefragt werden. Die Auswertung berücksichtigt sowohl fakturierte wie
gelieferte Mengen, wahlweise auch getrennt nach Eigen- und Fremdbestand.
Spezielle Anwendung als Feuerversicherungsliste.
Kumulierter Bestand

---

## Sortiervariante der Warenpositionen (Format VORGPOSSORT)

Sortiervariante der
Warenpositionen (Format VORGPOSSORT)
Liste des Sortierformats „VORGPOSSORT“.
Wert
Bezeichnung
0
Keine Sortierung
1
Artikelnummer
2
Matchcode
3
EAN
      1
4
Bezeichnung
5
Textzeile 1
6
Gewicht
7
Nettowert
8
Mengeneinheit
9
Warengruppe,
      Artikelnummer
10
Lager, Lagerplatz,
      Artikelnummer
101
Abst. Artikelnummer
102
Abst. Matchcode
103
Abst. EAN 1
104
Abst. Bezeichnung
105
Abst. Textzeile1
106
Abst. Gewicht
107
Abst. Nettowert
108
Abst. Mengeneinheit
109
Abst. Warengrupe,
      Artikelnummer
110
Abst. Lager, Lagerplatz,
      Artikelnummer

---

## Steuerparameter

Steuerparameter
Durch folgende
Steuerparamenter können Einstellungen zum Thema Fremdware/Fremdlager vorgenommen
werden.:

---

## SVPOSBAR2

SVPOSBAR2
Auf der SVPOSBAR2 Maske wird nach jeder Eingabe eines
Wertes das zu aktualisieren AIS aufgerufen. Folgende IDs werden in Abhängigkeit
des Feldes an das Makro übergeben werden.
*Die Maskenfelder werden hier in FRZ zugeordnet.
Maskenfeld
Übergebene IDs
Nummer
Typ
FN_LagerNummer*
ID_LAGERNUMMER
Maskenfeld
FN_Menge*
ID_MENGE
Maskenfeld
FN_ArtikelNummer*
ID_ARTIKELNUMMER
Maskenfeld
FN_Preis*
ID_PREIS
Maskenfeld
FN_RabattEingabe*
ID_RABATT
Maskenfeld
Benötigte JVARS
JAVR
Funktion
Bedeutung
VORGANGHANDLE
Lesend
Mit
      dieser JAVR wird der aktuelle Handle des Vorgangs übergeben
WAPOSITIONHANDLE
Lesend
Mit
      dieser JVAR wird der Handle der Warenposition übergeben.
ID
Lesend
Mit
      dieser JVAR wird die Nummer der ID übergeben
FELDNAME
Lesend
Diese JVAR enthält den Namen des
      aufrufenden Feldes. Das Feld kann aber auch eine Funktion sein. Es wird
      der Feldname aus der Spalte Maskenfeld von der Tabelle drüber an das Makro
      übermittelt.

---

## SVUMWARE

SVUMWARE
Auf der SVWARE Maske wird nach jeder Eingabe eines
Wertes das zu aktualisieren AIS aufgerufen. Folgende IDs werden in Abhängigkeit
des Feldes an das Makro übergeben werden.
Maskenfeld
Übergebene IDs
Nummer
Typ
LagerNummerAbg$
ID_LAGERNUMMER_ABG
1801
Maskenfeld
ArtikelIdAbg$
ID_ARTIKELID_ABG
1807
Maskenfeld
LagerPlatzAbg$
ID_LAGERPLATZ_ABG
1802
Maskenfeld
LagerNummerZug$
ID_LAGERNUMMER_ZUG
1804
Maskenfeld
ArtikelIdZug$
ID_ARTIKELID_ZUG
1808
Maskenfeld
LagerPlatzZug$
ID_LAGERPLATZ_ZUG
1805
Maskenfeld
PreisEinh$
ID_PREISEINHEIT
1078
Maskenfeld
PreisEinh_Z$
ID_PREISEINHEIT
1078
Maskenfeld
ME_Nummer$
ID_ME_NUMMER
1108
Maskenfeld
ME_Nummer_Z$
ID_ME_NUMMER
1108
Maskenfeld
ME_NummerPreis$
ID_ME_NUMMERPREIS
1077
Maskenfeld
ME_NummerPreis_Z$
ID_ME_NUMMERPREIS
1077
Maskenfeld
ZusatzInfos$
ID_ZUSATZINFO
1353
Maskenfeld
ZusatzInfo_Z$
ID_ZUSATZINFO
1353
Maskenfeld
ZusatzInfos2$
ID_ZUSATZINFO2
1358
Maskenfeld
ZusatzInfo2_Z$
ID_ZUSATZINFO2
1358
Maskenfeld
Preis$
ID_PREIS
1000
Maskenfeld
Preis_Z$
ID_PREIS
1000
Maskenfeld
Menge$
ID_MENGE
1001
Maskenfeld
Menge_Z$
ID_MENGE
1001
Maskenfeld
Netto$
ID_NETTO
1003
Maskenfeld
Netto_Z$
ID_NETTO
1003
Maskenfeld
V_LGUBuchTyp$
ID_LGU_BUCHTYP
4500
Maskenfeld
Benötigte JVARS
JAVR
Funktion
Bedeutung
VORGANGHANDLE
Lesend
Mit
      dieser JAVR wird der aktuelle Handle des Vorgangs übergeben
UMBUCHUNGHANDLE
Lesend
Mit
      dieser JVAR wird der Handle der Umbuchung übergeben.
ID
Lesend
Mit
      dieser JVAR wird die Nummer der ID übergeben
FELDNAME
Lesend
Diese JVAR enthält den Namen des
      aufrufenden Feldes. Das Feld kann aber auch eine Funktion sein. Es wird
      der Feldname aus der Spalte Maskenfeld von der Tabelle drüber an das Makro
      übermittelt.

---

## techn. Informationen Buchungen

techn. Informationen
Buchungen
Artikelzählungen
Wird ein Artikel ohne Partien gezählt, so ist stets
der gesamte Artikelbestand (des Lagerplatzes wenn verwendet) anzugeben. Dieser
wird dann dem aktuellen Buchbestand (des Lagerplatzes) gegenübergestellt und die
Differenz wird im Inventurbeleg ein- bzw. ausgebucht.
Wertseitig wird der Buchbestand vollends mit dem
Ausbuchpreis ausgebucht und der Zählbestand wiederum mit dem Einbuchpreis
eingebucht.
Partiezählungen
Wird eine Partie gezählt, so ist der gesamte
Partiebestand (des Lagerplatzes wenn verwendet) anzugeben. Dieser wird dann dem
aktuellen Buchbestand der Partie (des Lagerplatzes) gegenübergestellt und die
Differenz wird im Inventurbeleg ein- bzw. ausgebucht.
Die Differenz verändert jedoch zusätzlich den
Artikelbestand.
Dabei wird die Differenz zwischen Partiebuchbestand
und Partiezählung mit dem Buchbestand des Artikels verrechnet.
Werden mehrere Partien des gleichen Artikels in einer
Warenposition erfasst, so wird die Summe der Differenzen aus den
Partiepositionen mit dem Buchbestand des Artikels verrechnet.
Wertseitig wird der Buchbestand des Artikels vollends
mit dem Ausbuchpreis ausgebucht und der Zählbestand des Artikels wiederum mit
dem Einbuchpreis eingebucht.
Beispiel:
Artikelbestand sei 1000, Partie No101 und Partie No102 haben
jeweils einen Buchbestand von 500.
Partie No101 wird mit Menge 499, Partie No102 wird mit Menge
498 gezählt.
Die Partiebestände entsprechen nach Buchung der Zählung
denen der Zählung.
Der Artikelbestand wird um 3 auf 997 reduziert.
Hinweis:
Es ist dringend empfohlen, dass Artikel nur mit Partie
oder komplett ohne Partie geführt werden.
Die Eingabe einer Zählung ohne Partieangabe würde dazu
führen, dass diese als Artikelkomplettzählung interpretiert würde und den
Artikelbestand auf den der Zählung des partielosen Artikelanteils reduziert.
Differenzen zwischen Artikel- und Partiebeständen
Differenzen zwischen Artikelbestand und der Summe der
Partiebestände kön
[...]


---

## Vollständigkeitsprüfung der permanenten Inventur

Vollständigkeitsprüfung der
permanenten Inventur
Inventur
Permanente Inventur
Permanente Inventur Prüfungen
Zum Geschäftsjahresende sollen alle Inventuren auf
ihre Vollständigkeit hin überprüft worden sein. Zu diesem Zweck wurden
verschiedene Varianten der Anwendung „Permanente Inventur Prüfungen“
eingerichtet.

---

## Waren- Lager und Eigentumsbegriffe

Waren- Lager und Eigentumsbegriffe
Nicht jede Ware, die im Lager liegt gehört zur eigenen
Ware und nicht alles, was einem selbst gehört, muss auch im eigenen Lager
liegen. Dieser Abschnitt klärt Begriffe, die im Bereich der Lagerung verwendet
werden.

---

## Weitere Module

Weitere Module
Bisher Unterstützte Module
Modul
Produktion mit
      Seriennummern
Ladeschein zu
      Lieferschein
Bestellaufnahme
Inventur
Lagerplatzumbuchung
Eingangslieferschein
Profiltypen für den Aufruf einer privaten
Prozedur
Typ
Bedeutung
1
Markt(Terres) Bestellung
2
Inventur
3
Produktion
4
Ladeschein
5
Ladescheinaufladen
6
Lagerplatzumbuchung
7
Eingangslieferschein
Um die Vorhandenden Module zu individualisieren
besteht die Möglichkeit an Vorgegebenen Stellen eine Private Prozedur
aufzurufen.

---

## Zugangslagerplatz bei Umbuchung

Zugangslagerplatz bei Umbuchung
Kann die Lagerplatznummer nicht ermittelt werden, wird
sie mit 0 belegt. Eine Validierung findet nicht statt.
(Positionsparameter: LPUMB_SAx)

---

