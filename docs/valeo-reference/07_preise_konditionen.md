# Preise, Konditionen & Kalkulation — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (250 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Individuelle Preiskonditionen

Individuelle Preiskonditionen
Bei der Erfassung von individuellen Preiskonditionen
(z.B. Direktsprung [PRI] oder [PRIE]) konnte nicht mit der Tab-Taste oder den
Cursor-Tasten vom Register zurück in den Eingabereich für Artikel-  bzw.
Kundennummer gesprungen werden. Dieses Problem wurde behoben.
Releasenote Kategorie:
Ticket: 713901[32734]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32734, 713901

---

## Preiskalkulation

Preiskalkulation
Aus der Anwendung Artikel wurde die Funktion "VK
Preise kalkulieren" entfernt. Zur Preiskalkulation empfehlen wir weiterhin den
bekannten Weg unter "Preise/Kondition->Preiskalkulation Excel
(Auswahlliste)".
Releasenote Kategorie:
Ticket: 0[33065]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Artikel
Variante: Artikel
Funktion/Report: VK Preise kalkulieren
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33065, 0

---

## Preiskalkulation Excel auf Artikelebene nicht mehr möglich.

Preiskalkulation Excel auf Artikelebene nicht mehr möglich.
In der Anwendung Artikel steht die Funktion
"Preiskalkulation mit Excel" nicht mehr zur Verfügung.  Das
Standardverfahren läuft über die Anwendung "Preiskalkulation mit Excel"
Menüpunkt: Preiskalkulation mit Excel(Auswahlliste)
Direktsprung: [PKX]
Releasenote Kategorie:
Ticket: 717577[33283]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Artikel
Variante: Artikel mit Lager
Funktion/Report: Preiskalkulation Excel
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33283, 717577

---

## Rabatte bei manuellem Preis Vorgangsklassenabhängig

Rabatte bei manuellem Preis Vorgangsklassenabhängig
Der Steuerparameter 347 (Rabatte auch bei manuellem
Preis) kann nun Vorgangsunterklassenabhängig in [FRZ] überschrieben
werden.
Releasenote Kategorie:
Ticket: 721024[33578]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Formularzuordnung
Variante: Vorgangsunterklassen
Funktion/Report: Registerkarte SPA
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33578, 721024

---

## Interne Änderung bei den Stammdaten für die Preisfindung

Interne Änderung bei den Stammdaten für die Preisfindung
Die automatische Vorbelegung der Nummern für
individuelle Preisklassen, individuelle Rabattklassen, individuelle
Zu-/Abschlagsklassen und individuelle Preisgruppen wurde auf das Ident-Verfahren
umgestellt. Bisher wurde für die Klassen die Nummer des Kunden und für die
Gruppe die Id des Artikels genommen. Dieser wurde dann entweder eine 0 oder 1
angehangen. Dies konnte unter Umständen zu Fehlern führen, weswegen das
Verfahren umgestellt wurde.  Wenn eine der genannten Klassen oder die
Gruppe automatisiert angelegt wird, wird eine eindeutige Nummer jenseits des
Wertebereichs von 100.000.000 verwendet und in einer entsprechenden Tabelle der
Datenbank gespeichert. Wenn Sie die Klassen/Gruppe manuell anlegen, wird der
Wert analog dem zuvor beschriebenen Verfahren vorgeschlagen. Sie können diese
Nummer aber auch ändern und eine eigene eindeutige Nummer verwenden. Wir raten
hierbei unterhalb des Werts von 100.000.000 zu bleiben. Sobald Sie das Feld
verlassen haben, wird die eingetragene Nummer festgeschrieben und kann
nachträglich nicht mehr geändert werden. Sollten Sie sich für eine eigene Nummer
entschieden haben, wird die zuvor vorgeschlagene Nummer bei dem nächsten Objekt
gleichen Typs nicht mehr wiederverwendet! Die Nummer gilt intern als verbraucht,
auch wenn sie nicht verwendet wurde. Da der mögliche Wertebereich jedoch bis ca.
2,4 Milliarden geht, sind ausreichend Nummern für die Zukunft vorhanden.
Releasenote Kategorie:
Ticket: 722744[33716]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [PRIK], [PRI], [PRIE], [RAK], [ZABK]
Variante: Individualpreisklasse
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33716, 722744

---

## Rabattanzeige auf dem externen Kassendisplay

Rabattanzeige auf dem externen Kassendisplay
Das externe Display der Marktkasse zeigt jetzt auch
direkt bei Rabatteingabe diesen Rabatt auf dem Bon des externen Displays an,
ohne dass dazu ein weiterer Artikel erfasst werden muss.
Releasenote Kategorie:
Ticket: 725490[34124]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Kasse
Variante: Stamminfo logischer kassen
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34124, 725490

---

## Preiskalkulation mit Excel [PKX]

Preiskalkulation mit Excel [PKX]
Die Standardvarianten und Prozeduren wurden
überarbeitet und es wurde eine Protokollvariante ergänzt.
Releasenote Kategorie:
Ticket: 727894[34488]
Version: 8.3.2312.8
Datum: 08.12.2023
Anwendung: Preiskalkulation mit Excel [PKX]
Variante: Alle
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.8, 34488, 727894

---

## Bewertungspreise für Artikel mit Bewertungsgruppe 0

Bewertungspreise für Artikel mit Bewertungsgruppe 0
Die Kalkulation der Bewertungspreise funktioniert
jetzt auch, wenn keine der Optionen für die Kalkulation angehakt sind.
Releasenote Kategorie:
Ticket: 741773[34222]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Inventur Bewertungspreise
Variante: Bewertungspreise kalkulieren
Funktion/Report: F9 Kalkulation
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34222, 741773

---

## Fehlerbereinigung Ermittlung der Bewertungspreise

Fehlerbereinigung Ermittlung der Bewertungspreise
In der Prozedur zur Ermittlung der Bewertungspreise
hat sich im Rahmen der Einführung der permanenten Inventur ein Fehler
eingeschlichen. Dieser wurde behoben.
Releasenote Kategorie:
Ticket: 730019[35015]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Warenwirtschaft
Variante: -
Funktion/Report: Ermittlung der Bewertungspreise
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 35015, 730019

---

## Neue Listenpreisgruppe bei bereits vergebener Nummer

Neue Listenpreisgruppe bei bereits vergebener Nummer
Bei der Neuanlage einer Listenpreisgruppe über
die Funktion 'Neu' konnte es in seltenen Fällen vorkommen,  das die
automatisch erzeugte Listenpreisgruppennummer bereits in der Relation
existierte. Dieses führte zu einer Fehlermeldung. Das Verfahren wurde nun
dahingehend geändert, dass nach der Bestimmung einer neuen Nummer geprüft wird,
ob eine Listenpreisgruppe mit dieser Nummer bereits existiert. Ist das der Fall,
so wird solange eine neue Nummer bestimmt, bis diese passt.
Releasenote Kategorie:
Ticket: 733441[35049]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Listenpreisgruppen [PRLG]
Variante: alle
Funktion/Report: Neu [F8]
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35049, 733441

---

## Preiskonditionen

Preiskonditionen
Wurde in den Individuellen Preisen versucht die letzte
Zeile zu löschen, wurde diese Änderungen nicht gespeichert.
Releasenote Kategorie:
Ticket: 736791[35485]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35485, 736791

---

## Individuelle Preiskonditionen

Individuelle Preiskonditionen
Es wurden fälschlicher Weise auch gelöschte Artikel
angezeigt, was insbesondere wenn die Artikelnummer neu vergeben wurde, zu
Irritationen führte. Gelöschte Artikel werden nun nicht mehr
berücksichtigt.
Releasenote Kategorie:
Ticket: 734329[35499]
Version: 9.0.2501.5
Datum:
Anwendung: Information Individualpreise
Variante: -
Funktion/Report: [PIB]
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35499, 734329

---

## Bearbeiten von EK- und VK-Preisen

Bearbeiten von EK- und VK-Preisen
In der Anwendung 'Artikel' [AR] wurden bei mehreren
markierten Einträgen in der Auswahlliste in den Funktionen 'VK-Preise
bearbeiten' und 'EK-Preise bearbeiten' beim Blättern auf den nächsten oder
vorhergehenden Artikel die Preise des ersten vorhandenen Preiszeitraums des
Artikels dargestellt. Dieses Verhalten wurde nun geändert. Soweit vorhanden,
wird nun zunächst immer der Preiszeitraum zum aktuellen Tagesdatum
dargestellt.
Releasenote Kategorie:
Ticket: 732390[35531]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Artikel [AR]
Variante: alle
Funktion/Report: VK-Preise bearbeiten, EL-Preise
bearbeiten
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35531, 732390

---

## F2-Suche

F2-Suche
In [PKX] EK und VK fürte die F2-Suche über die
Lieferantennummer ohne Lieferentenbezeichnung zu einem Fehler in der
Auswahlliste. Dieser wurde behoben.
Releasenote Kategorie:
Ticket: 741007[36020]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Preiskalkulation Excel
Variante: Einkauf / Verkauf
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 36020, 741007

---

## Individualpreispfleger [PRI] [PRIE]

Individualpreispfleger [PRI] [PRIE]
Bei der Preispflege in der Maske Individuelle Preise
[PRI] [PRIE] ist es möglich durch Angabe einer anderen Artikelnummer ohne
Verlassen der Maske einen weiteren Artikel zu bearbeiten.   Leider
wurde nach Eingabe der neuen Artikelnummer die Daten nicht aktualisiert. In der
Maske blieben die Daten des zuvor bearbeiteten Artikels stehen.
Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 745257[36645]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Preise/Konditionen
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36645, 745257

---

## Behebung Locking-Fehler Maske Preiskonditionen

Behebung Locking-Fehler Maske Preiskonditionen
Bei Änderungen innerhalb der Maske [PRI] wird eine
Datenbanksperre für die Kombination aus Individueller Preisklasse und
Artikelpreisgruppe gesetzt, um so ungewollte Änderungen im Mehrbenutzerbetrieb
zu verhindern. Bei bestimmten Konstellationen blieb die Datenbanksperre auch
nach Schließen der Maske erhalten, so dass nach erneutem Aufruf der Maske für
die gleiche Daten-Kombination der Datensatz fälschlicherweise als gesperrt
angezeigt wurde. Der Fehler wurde behoben - beim Schließen der Maske werden alle
Sperren freigegeben.
Releasenote Kategorie:
Ticket: 741454[36656]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Individualpreispfleger [PRI] [PRIE]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36656, 741454

---

## Individualpreispfleger EKZ-Nummer

Individualpreispfleger EKZ-Nummer
Im Individualpreispfleger [PRI],[PRIE] auf
dem Tab "Allgemein" wurde unter Umständen die EKZ-Nummer in den
Tabellenzeilen fälschlicherweise mit 0 anstelle des in der Datenbank korrekt
gespeicherten Werts belegt. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 746104[36859]
Version: 9.0.2501.5
Datum:
Anwendung: Individualpreispfleger [PRI],[PRIE]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36859, 746104

---

## Mengeneinheiten in Objekt-/Baustellenartikeln

Mengeneinheiten in Objekt-/Baustellenartikeln
Der Objekt-/Baustellen-Artikelpreispfleger ist nur für
Artikel aufrufbar. Pflegt man einen neuen Preis, so wird dieer nun mit den
korrekten Mengeneinheiten aus dem Artikel vorbelegt und die
Mengeneinheitsbezeichnungen für Preise & Mengen werden je Einkauf und
Verkauf zusätzlich angezeigt.
Releasenote Kategorie:
Ticket: 751485[38548]
Version: 9.0.2502.8
Datum:
Anwendung: Objekt-/Baustellenartikeln [OBJ] [BAU]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.8, 38548, 751485

---

## Fehler in Variante Preiskalkulation Protokoll bei Dokument anzeigen behoben

Fehler in Variante Preiskalkulation Protokoll bei Dokument anzeigen
behoben
In der Anwendung Preiskalkulation mit Excel [PKX] ist
ein Fehler in der Variante Preiskalkulation Protokoll aufgetreten. Für einen
ausgewählten Protokoll-Eintrag konnte die zugehörige Excel-Datei der
importierten Preisliste mit der Funktion Dokument anzeigen nicht geöffnet
werden. Dies wurde nun behoben und die Variante mit ihrer Auswahlliste
entsprechend angepasst.
Releasenote Kategorie:
Ticket: 746065[38898]
Version: 9.0.2502.9
Datum:
Anwendung: Preiskalkulation mit Excel
Variante: Preiskalkulation Protokoll
Funktion/Report: Dokument anzeigen (F11)
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38898, 746065

---

## ARTIKEL (EPA ARTIKEL)

ARTIKEL (EPA ARTIKEL)
Bezeichnung
Standardwert
Erklärung
Vorbelegung der Antwort auf die
      Frage
Ja
Länge EAN-Code ( 0 = ohne Prüfung
      )
0
Frage Preise der alten
      Listenpreisgruppe übernehmen
Nein
Startfeld im Ändern-Fall
h.Artikelbezeich
Startfeld im
      Ansehen-Fall
LISTENPREISMATRIX
Startfeld im Neu-Fall
h.Artikelnummer
Artikeltextzeile1/Stammkurzbezeichnung/Artikelkurzbezeichnung
      immer gleich
Ja

---

## Preis-/Rabatt-/Frachtgruppen (EPA DHARTKPG)

Preis-/Rabatt-/Frachtgruppen (EPA DHARTKPG)
Bezeichnung
Standardwert
Erklärung
Vorbelegung der Antwort auf die
      Frage
Ja
Frage Preise der alten
      Listenpreisgruppe übernehmen
Ja

---

## Artikel (EPA DHARTNEU)

Artikel (EPA DHARTNEU)
Bezeichnung
Standardwert
Erklärung
Startfeld Ändern
h.ArtikelBezeich
Startfeld Ansehen
LISTENPREISMATRIX
Startfeld Neu
h.ArtikelNummer

---

## Rabatt- und Zu-/Abschlag-Konditionen (EPA DHIPRRB2)

Rabatt- und Zu-/Abschlag-Konditionen (EPA
DHIPRRB2)
Bezeichnung
Standardwert
Erklärung
Ab-Datum bei
      Individualpreisneuanlage
Anfang Geschäftsjahr
Zur
      Bestimmung des Zeitraumbeginns bei automatischer Anlage eines noch nicht
      vorhandenen Zeitraums zum aktuellen Datum für einen individuellen
      Preis
Bis-Datum bei
      Individualpreisneuanlage
Ende
      des Geschäftsjahres zum Ab-Datum
Zur
      Bestimmung des Zeitraumendes bei automatischer Anlage eines noch nicht
      vorhandenen Zeitraums zum aktuellen Datum für einen individuellen
      Preis
Anzahl Tage (Bis-Datum = Ab-Datum +
      Tage)
30
Preisreihenfolge aufsteigend nach
      Ab-Datum
Nein
Standardsortierung der individuellen
      Preiszeiträume von ‚absteigend‘ in ‚aufsteigend‘ ändern. Wirkt erst bei
      der nächsten Lese-Operation (z.B. Blättern)!

---

## Marktstand - Preis-Pfleger+Kalkulation (EPA MARKTSTANDTABELLE)

Marktstand - Preis-Pfleger+Kalkulation
(EPA MARKTSTANDTABELLE)
Bezeichnung
Standardwert
Erklärung
Markiert die ganze Zeile bei
      Anklicken
Ja

---

## MaskenTitel (EPA SVPOSBAR)

MaskenTitel (EPA SVPOSBAR)
Bezeichnung
Standardwert
Erklärung
Soll
      Menge*Preis auf dem Display angezeigt werden?
Nein
Abfrage vor Abspeichern einer
      Position?
Nein
Soll
      die letzte erfasste Position stehen bleiben?
Ja
Warnung bei Bestätigen der Menge
      null
Nein
Warnung bei Bestätigen eines
      Nullpreises
Ja
Soll
      ein gefundener Preis bestätigt werden?
Nein
Soll
      schnellerfasst werden?
Ja
Soll
      im Artikelfeld begonnen werden?
Ja
Im
      Verkauf Verprobung mit Listenpreis (Warnmeldung)
Nein

---

## Excel-Datei importieren

Excel-Datei importieren
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Funktion
Individualpreiskalkulation
Einkauf/Verkauf
Direktsprung
[PKXI]
Funktion
Individualpreiskalkulation
Einkauf/Verkauf
Um die neuen Individualpreise in Referenz-ERP zu
importieren, müssen folgende Schritte ausgeführt werden:
1.
Im Menüband die Funktion
Individualpreiskalkulation Einkauf
bzw
.
Individualpreiskalkulation
Verkauf
auswählen oder
F9
drücken
.
2.
Es öffnet sich der Datei-Explorer an dem zuvor definierten Import-Pfad. Es
sollte die Datei
IndividualpreisKalkEK
bzw.
IndividualpreisKalkVK,
wie im Screenshot abgebildet, zu sehen sein.
5.
Die Datei auswählen und auf „Öffnen“ klicken. Der Import wird nun durchgeführt.
Je nach Größe der Preisliste kann dies einige Minuten dauern. Sobald die
folgende Meldung nicht mehr am unteren linken Rand vom Referenz-ERP-Fenster zu sehen
ist, ist der Import abgeschlossen. Die Datei wird abschließend gelöscht, kann
aber im
Import-Protokoll
erneut aufgerufen werden.
6.
Sollte beim Import ein Fehler aufgetreten sein, erscheint eine Nachrichtenbox
mit einer Fehlermeldung. Ist dies der Fall, sollte direkt der Schritt
Import-Protokoll prüfen
ausgeführt
werden, um Näheres über den Fehler zu erfahren. Erscheint keine Nachricht, so
verlief der Import fehlerfrei.
7.
Als Letztes sollten die neuen Preise einmal überprüft werden. Dafür mit
Strg+R
die Auswahlliste aktualisieren und
kontrollieren, ob die neuen Individualpreise korrekt importiert wurden.
Hinweis!
Um den neuen Wert für
Preis
zu überprüfen, ist
das Feld
Preis alt
zu beachten. Dort steht der aktuelle Preis aus der
Datenbank. Wenn der Import erfolgreich war, steht hier also der importierte
Preis.
Auch für den Gültigkeitszeitraum sind die Felder
Preis ab alt
und
Preis bis alt
entscheidend. Wie bei den Preisen
stehen hier, bei erfolgreichem Import, die neuen Werte.

---

## Export konfigurieren

Export konfigurieren
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Funktion
Optionen Einkauf/Verkauf
Direktsprung
[PKXI]
Funktion
Optionen Einkauf/Verkauf
Um die Einrichtung der Individualpreiskalkulation
Excel zu starten, müssen die folgenden Schritte ausgeführt werden:
1.
Die Variante
Individualpreise Excel Einkauf
oder
Individualpreise
Excel Verkauf
für die Einkaufs – oder Verkaufspreise auswählen.
2.
Auf
Optionen Einkauf
bzw.
Optionen Verkauf
klicken oder
F10
drücken.
3.
Im Feld Pfad angeben, an welcher Stelle im Dateisystem die exportierte
Excel-Datei gespeichert werden soll (z. B. ..\import\EK oder
..\import\VK).
4.
im Feld
Datenbankprozedur
F3
drücken, um
die Standardprozedur
AMIC_Excel_Individualpreis_Import_EK
bzw.
AMIC_Excel_Individualpreis_Import_VK
(EK für Einkauf, VK für Verkauf) einzutragen, wenn diese nicht bereits gesetzt
ist. Wenn alternativ eine private Prozedur verwendet werden soll, kann diese
hier hinterlegt werden.
Hinweis!
Die Felder „Filter“ und „Datenbank-Dateiname“ sind
bereits durch die in Referenz-ERP konfigurierten Filter sowie die hinterlegte
Datenbank vorbelegt.
Optional: Private Datenbankprozedur anlegen
Für den Import können auch private Datenbankprozeduren
verwendet werden. Um diese anzulegen, muss im Feld
Datenbankprozedur
der Name der neuen Prozedur
eingetragen werden.
Hinweis!
Private Datenbankprozeduren müssen immer mit einem
vorangestellten
P_
anfangen.
Die private Datenbankprozedur wird nun anhand der
Standardprozedur
AMIC_Excel_Individualpreis_Import_EK
bzw.
AMIC_Excel_Individualpreis_Import_VK
angelegt und kann direkt im hinterlegten Editor bearbeitet werden.

---

## Exportprofil einrichten

Exportprofil einrichten
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Direktsprung
[PKXI]
Um den Export der Individualpreise durchzuführen, muss
zuerst das Exportprofil bestimmt werden. Dafür den nächsten Schritten
folgen:
1.
In der Variante
Individualpreise Excel Einkauf
bzw.
Verkauf
über
das
Fernglas-Symbol
im oberen Bereich oder mit
F2
den Dialog
Individualpreise Excel
Einkauf
bzw.
Verkauf
aufrufen, um die Individualpreise zu filtern und
eine Vorbelegung durchzuführen.
2.
Für das Kriterium
Preis gültig am
kann
ein Datum über den
interaktiven Kalender, der sich mit Doppelklick im Feld öffnet, ausgewählt
werden. Alternativ kann ein Datum, oder der Wert „heute“
eingetragen
werden.
3.
Mit dem Kriterium
Preisauswahl
kann festgelegt werden, ob ausschließlich
zu dem zuvor definierten Zeitpunkt gültige, alle, oder gültige und zukünftig
gültige Individualpreise angezeigt werden.
4.
Optional können weitere Filterkriterien für die Individualpreise ausgewählt
werden, indem vor dem jeweiligen Kriterium das Optionsfeld aktiviert und ein
Wert zum Filtern eintragen wird. Mit dem Druck von
F3
in einem Feld, kann
eine Auswahl aller möglichen Ausprägungen angezeigt werden.
5.
Eine mögliche Vorbelegung für den Gültigkeitszeitraum der Individualpreise kann
über die Kriterien
Vorbelegung Preis-ab
und
Vorbelegung Preis-bis
vorgenommen werden. Für diese Felder kann über Doppelklick im Feld eine
Auswahl über den Kalender getroffen oder direkt ein Datum eingetragen
werden.
6.
Die Einstellungen können durch den Druck von
F9
oder die Wahl von
Speichern und
zurück
in der Optionsbox am rechten unteren Rand des Dialogs übernommen
werden. Die Auswahlliste wird aktualisiert und nach den ausgewählten Kriterien
gefiltert.
7.
Die Auswahl sollte noch einmal überprüft werden. Die Excel-Datei wird auf dieser
Basis im nächsten Schritt generiert.

---

## Import-Protokoll prüfen

Import-Protokoll prüfen
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Direktsprung
[PKXI]
In der Variante
Individualpreise Protokoll
werden alle durchgeführten Importe gesammelt und können nachträglich noch einmal
überprüft werden. Dafür die folgenden Schritte ausführen:
1.
Mit dem Klick auf das
Fernglas-Symbol
im oberen Bereich oder das
Drücken der Taste
F2
kommt man
in den Dialog
Individualpreise Protokoll
. Hier kann nach dem Zeitpunkt
des Imports gefiltert werden. Dafür das Optionsfeld
Zeitpunkt
aktvieren
und einen gültigen Zeitraum eintragen. Über Doppelklick öffnet sich der
interaktive Kalender. Alternativ kann ein Datum oder der Wert „heute“
eingetragen werden.
Speichern und zurück
wählen oder
F9
drücken
, um den Dialog zu schließen
und die Auswahlliste zu aktualisieren.
2.
In der Auswahlliste werden nun alle Importe aus dem gewählten Zeitraum
angezeigt. Neben dem
Zeitpunkt
des Imports gibt es das Feld
Typ
,
das kennzeichnet, ob es sich um einen Import von Einkaufs- oder Verkaufspreisen
handelt sowie das Feld
Bediener
mit dem Kürzel des ausführenden
Bedieners.
3.
Um mehr über einen Import zu erfahren, kann auf das
Plus-Symbol
an
der linken Seite des Eintrags geklickt werden. Die Gruppierung wird für diesen
Eintrag aufgehoben.
4.
In der Auswahlliste sind jetzt Informationen zu dem Import jeder Zeile der
Excel-Datei zu finden.
5.
Pro Zeile wird eine Auswahl an Werten aus der Excel-Datei aufgelistet.
Wichtig sind vor allem die Felder
Fehler
und
Info.
a.
Fehler:
Sollte ein Fehler beim Import der Zeile aufgetreten sein, steht hier
als Ausprägung „Ja“. Ohne Fehler hält das Feld den Wert „Nein“.
b.
Info:
Bei einem Fehler beim Import der Zeile sind hier mehr Informationen
über den Fehler zu finden. Ansonsten meldet das Feld, dass die Zeile erfolgreich
verarbeitet, übersprungen oder gelöscht wurde.
Dokument anzeigen
Neben der Überprüfung des Imports auf Fehler bietet
sich Ihnen im Protokoll auch
[...]


---

## Individualpreise exportieren

Individualpreise exportieren
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation
Funktion
Excelblatt Einkauf/Verkauf
Direktsprung
[PKXI]
Funktion
Excelblatt Einkauf/Verkauf
Um die Individualpreise zu exportieren und die
Excel-Datei zu erstellen, im Menüband auf
Excelblatt Einkauf
bzw.
Excelblatt Verkauf
klicken oder
F8
drücken
. Die gefilterten
Individualpreise aus der Auswahlliste werden nun exportiert.
Die Excel-Datei wird im zuvor hinterlegten Pfad unter
dem Namen
IndividualpreisKalkEK
bzw.
IndividualpreisKalkVK
gespeichert und dann geöffnet.

---

## Individualpreiskalkulation Excel

Individualpreiskalkulation Excel
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Direktsprung
[PKXI]
Mit der Anwendung
Individualpreiskalkulation
Excel
können Individualpreise vom Typ Einkauf oder Verkauf in Excel
bearbeitet und anschließend in Referenz-ERP importiert werden.
Voraussetzung für die Nutzung der Funktionen ist eine
Excel-Individualpreiskalkulation-Lizenz.
Initial werden dazu die Individualpreisdaten in eine
Excel-Datei exportiert und können dann mit Excel oder einer alternativen
Anwendung gepflegt werden. Der anschließende Import der Excel-Datei geschieht
über den Excel-Archivimport, der die Preise dem Archiv hinzufügt und als XML in
Referenz-ERP importiert. Die neuen Individualpreise gelangen so direkt via
Datenbankprozedur in die Referenz-ERP Stammdaten. Über eine Protokollfunktion in der
Variante
Individualpreise Protokoll
können die kalkulierten Preise
jederzeit wieder aufgerufen und erneut importiert werden.
Neue Individualpreise in Referenz-ERP®
Voraussetzungen:
•
Der Steuerparameter
1167
ist aktiviert.
•
Der Steuerparameter
508
ist aktiviert.
•
Eine Referenz-ERP-Version ab
9.0.2601.1
ist installiert.
Der Import über die Anwendung
Individualpreiskalkulation Excel
setzt sich aus den folgenden Schritten
zusammen:
•
Export
konfigurieren
•
Exportprofil einrichten
•
Individualpreise exportieren
•
Excel-Datei
bearbeiten
•
Excel-Datei
importieren
•
Import-Protokoll prüfen
Weitere Funktionen in der
Individualpreiskalkulation
Zudem kann die Individualpreiskalkulation gedruckt
oder weitergeleitet werden.
Folgende Formate stehen dafür zur Verfügung:
•
E-Mail
•
PDF
•
CSV
•
Excel

---

## Kunden-Artikel Preisliste

Kunden-Artikel Preisliste
Hauptmenü
Preise/Konditionen
Preise
Preisliste EK/VK
Oder Direktsprung
[PL]
In der Auswahlliste für Preisliste EK/VK gibt es eine
Variante Kunden-Artikel Preisliste.
In dieser kann man sich für einen oder
mehrere Kunden und einen oder mehrere Artikel den jeweiligen aktuellen Preis für
den per Datum angegebenen Tag anzeigen lassen. Im Auswahlbereich können die
Artikelnummer, Lagernummer und Kundennummer sowie das Tagesdatum festgelegt
werden. Aus Performancegründen sind in der Standardeinstellung die Kundennummer
mit 10000 und die Artikelnummer mit 100 vorbelegt. Die Angabe des Tagesdatums
kann auch relativ, zum Beispiel durch die Eingabe von ‚heute‘ oder ‚heute+1‘
etc., erfolgen. Die Daten werden nach Kundennummer, Artikelnummer, Lagernummer
und, falls vorhanden, Kontraktnummer sortiert angezeigt.
Mit Hilfe des
Reports KundenArtikelPreisliste kann die gewünschte Selektion auch ausgedruckt
werden.
Sowohl die Auswahlliste als auch der Report arbeiten
mit der Prozedur aw_preis.
Diese ermittelt die Preise aus den Kontrakten,
die für den Kunden und Artikel existieren, sowie mit Hilfe der Prozedur
PreisVektor den Grundpreis
für den ausgewählten Tag.
Handelt es
sich um einen Kontraktpreis werden die Kontraktnummer und die
Kontraktbezeichnung angezeigt, ansonsten bleiben diese beiden Felder leer.
Der ausgewiesene Preis für einen Artikel ohne
Kontraktberücksichtigung wird ermittelt, indem zunächst geprüft wird, ob ein
individueller Preis
für den Artikel mit dem Kunden vereinbart ist.
Andernfalls wird der für den Kunden gültige
Listenpreis
ausgewiesen.
Andere bei der Preisfindung in Vorgängen ermittelbaren Preise, wie zum Beispiel
Partiepreise
oder
mengenabhängige Preise
und
Aktionspreise,
können in dieser Auswahlliste nicht ausgewiesen werden.
Die Inhalte der Felder werden aus folgenden Relationen
geholt:
Feld
Relation
Artikel
Artikel
Artikelbezeichnung
Artikel
Lagernummer
Artikel
Kundennummer
Kundenstamm
Kundenname
Kundenstamm
P
[...]


---

## Nullpreis / ohne Preis / vorläufiger Preis

Nullpreis / ohne Preis / vorläufiger Preis
In der Artikelerfassung der Vorgangsbearbeitung hat
man die Möglichkeit über Signalfelder eine Warenposition ohne Preis oder mit
einem vorläufigen Preis zu kennzeichnen. Am Signalfeld „
Nullpreis OK
“
kann man dann in der Maske der Warenposition erkennen, dass ein Preis 0
absichtlich eingegeben wurde und seine Berechtigung hat. Am Signalfeld „
Nicht Endpreis
“
erkennt man, dass der Preis noch nicht der endgültige ist und weiterer Pflege
bedarf.
Wichtig zu wissen
: Diese beiden Signalfelder
haben keine direkten Auswirkungen auf Umwandlungen. Sie dienen dem Anwender nur
als Hinweis in der Artikelerfassungsmaske.
Diese Signalfelder können über die Funktionen „
Nullpreis Okay an/aus
“
und „
Vorläufiger Preis an/aus
“ vom
Anwender jederzeit an- und ausgeschaltet werden. Hat man beide Merkmale für eine
Warenposition angewählt, dann wird nur das Signal „Nicht Endpreis“
angezeigt.
Das Label hinter dem Feld für den Gesamtpreis in der
Maske der Artikelerfassung zeigt an, woher der eingegebene Preis (
Preisherkunft
) kommt. Der
angezeigte Text kommt aus dem Format PR_HERKUNFT. Steht z.B. im Preisfeld der
Wert 0, dann erscheint im Label der Text „ohne Preis“. Bei manueller Eingabe
eines Preises steht in diesem Label der Text „manuelle Eingabe“.
Der
Steuerparameter 253
(unbepreiste Lieferscheine =
Umwandelsperre) bietet die Möglichkeit Lieferscheine in denen eine Warenposition
ohne Preis vorhanden ist für die Umwandlung zu sperren.
Wichtig zu
wissen
: Das Signalfeld „Nullpreis OK“ hat keine Auswirkung auf diese
Sperre!
­

---

## Pflegefunktion für Rabatte, Zu-/Abschläge, individuelle Preise, Individuelle Rabatte und individuelle Zu-/Abschläge

Pflegefunktion für Rabatte, Zu-/Abschläge,
individuelle Preise, Individuelle Rabatte und individuelle Zu-/Abschläge
Preise / Konditionen
Rabatte
allgemeine Rabatte
[RAV]
Preise / Konditionen
Zu- und Abschläge
allgemeine Zu-/Abschläge
[ZAVA]
Preise / Konditionen
Individualvereinbarungen
individuelle Preise/Rabatte VK
[PRI]
Preise / Konditionen
Individualvereinbarungen
individuelle Preise/Rabatte EK
[PRIE]
Preise / Konditionen
Individualvereinbarungen
Individualpreise bearbeiten
[PI]
Preise / Konditionen
Individualvereinbarungen
individuelle Rabatte VK
[RAI]
Preise / Konditionen
Individualvereinbarungen
individuelle Rabatte EK
[RAIEK]
Preise / Konditionen
Individualvereinbarungen
individueller Zu-/Abschlag VK
[ZAI]
Preise / Konditionen
Individualvereinbarungen
individueller Zu-/Abschlag EK
[ZAIEK]
Die Pflege von individuellen Preisen, individuellen
Rabatten, individuellen Zu-/Abschlägen, Rabatten und Zu/-Abschlägen erfolgt über
den Pfleger Preiskonditionen. Hierbei muss jeweils Einkauf und Verkauf
unterschieden werden.
­
Die Pflege erfolgt in allen fünf Bereichen jeweils
über die Kombination einer Klasse und einer Gruppe. Die Klassen können hierbei
im Kundenstamm hinterlegt werden, die Gruppen im Artikel.
Die Auswahl eines Kunden bzw. eines Artikels (mit
Lagernummer) dient hierbei der schnellauswahl für die entsprechenden
Klassen/Gruppen. Wenn kein Kunde/Artikel ausgewählt ist, können aber auch die
Klassen/Gruppen direkt ausgewählt werden.
Wenn ein ausgewählter Kunde (bzw. ausgewählter
Artikel) noch nicht alle Klassen (Gruppen) zugeordnet hat, kann über eine
Optionboxfunktion eine neue Klasse (Gruppe) angelegt werden, welche dem Kunden
(Artikel) direkt zugeordnet wird.
Da jede Klasse (Gruppe) auch mehreren Kunden (Artikel)
zugeordnet sein kann, sieht man im rechten Bereich nochmal alle beteiligten
Kunden (Artikel), welche von der aktuellen Pflege betroffen sind. Es wird also
nicht nur der oben ausgewählte Kunde (Artikel) gepflegt, sondern alle Kunden
(
[...]


---

## Preise/Konditionen

Preise/Konditionen

---

## Preise/Konditionen

Preise/Konditionen

---

## Preiskalkulation Excel

Preiskalkulation Excel
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Preiskalkulation Excel
Direktsprung
[PKX]
.
Voraussetzung für die Nutzung der Funktionen ist eine
Excel-Preiskalkulations-Lizenz.
Die Anwendung
Preiskalkulation Excel
importiert Ihre Verkaufs- oder Einkaufs-Preisdaten aus einer Excelliste in
Referenz-ERP. Kalkulieren Sie mit Excel Ihre Preise und importieren Sie anschließend
die Daten Ihre neuen Preise in Referenz-ERP.
Initial werden dazu die Preisdaten in ein Excel
exportiert und dann die Preise in Excel oder in einem anderen Programm
kalkuliert. Der anschließende Import der Exceldatei geschieht über den
Excel-Archivimport, der die Preise dem Archiv hinzufügt als auch als XML in
Referenz-ERP importiert. Die neuen Preise hinterlegen Sie so direkt an Ihren
Stammdaten in Referenz-ERP per zuvor erstellten Datenbankprozedur. Über eine
Protokollfunktion in der Variante
Preiskalkulation Protokoll
können Sie die Preiskalkulationsdaten jederzeit erneut aufrufen oder erneut
importieren.
Neue Preise in Referenz-ERP®
Voraussetzungen:
•
Der Steuerparameter
1145
ist aktiviert.
•
Der Steuerparameter
508
ist aktiviert.
•
Eine Referenz-ERP-Version ab
9.0.2305.01
ist installiert.
Das Importieren über die Anwendung
Preiskalkulation Excel
geschieht in folgenden Schritten:
•
Preisdatenexport einrichten
(F10)
•
Excelexport Datei generieren
(F8)
•
Datenexportprofil_einrichten
•
Exceldatei
_
bearbeiten
•
Neue Preis-Exceldatei in
Referenz-ERP importieren (F9)
Weitere Funktionen in der Preiskalkulation
Preiskalkulationen drucken oder weiterleiten.
Mit dieser Anwendung können Sie die Daten weiterleiten z. B.
in folgenden Formaten:
•
E-Mail
•
PDF
•
CSV
•
Excel

---

## Excelexportdatei generieren F8

Excelexportdatei generieren F8
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Preiskalkulation Excel
Funktion
Excelblatt Einkauf/Verkauf
Direktsprung
[PKX]
.
Funktion
Excelblatt Einkauf/Verkauf
Um die Exceldatei für den Export zu generieren und zu
abzuspeichern, wie folgt vorgehen:
1.
Klicken Sie im Menüband auf
Excelblatt
Verkauf
bzw.
Excelblatt
Einkauf
oder drücken Sie
F8
.

---

## Preisdatenexport einrichten F10

Preisdatenexport einrichten F10
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Preiskalkulation Excel
Funktion
Optionen Einkauf/Verkauf
Direktsprung
[PKX]
.
Funktion
Optionen Einkauf/Verkauf
Um die Einrichtung des Preiskalkulationsexcels zu
starten, wie folgt vorgehen:
1.
Wählen Sie eine Variante der Liste
Preiskalkulation
(VK für Verkaufspreise
oder EK für Einkaufspreise).
2.
Setzen Sie genaue Filter, um die zu kalkulierenden Preisdaten zu
exportieren.
3.
Klicken Sie auf
Optionen Verkauf
bzw.
Optionen Einkauf
oder drücken Sie
F10
.
4.
Geben Sie im
Pfad
an, wo die zu exportierenden Daten als Excel
Arbeitsblatt abgespeichert werden sollen (z. B.:„..
\import\vk“).
Hinweis!
Die Felder
Filter
und
Datenbank-Dateiname
sind bereits vorbelegt
durch Ihre gesetzten Filter sowie die in Ihrem Referenz-ERP hinterlegte Datenbank.
5.
Drücken Sie
F3
im Feld
Datenbandprozedur
, um die Standardprozedur
amic_excel_Preisimport_VK
bzw.
amic_excel_Preisimport_EK
einzutragen.
Optional
:
Private Datenbankprozedur
anlegen
Sie können Private Prozeduren anlegen, die sowohl
fa_id
(Formulararchiv ID) als auch
fa_mndnr
(Formulararchiv
Mandantennummer) übergeben können.
Hinweis!
Legen Sie private Prozeduren immer mit einem
vorangestellten
P
an, sodass diese nur für Sie als private Prozedur in
Referenz-ERP vorhanden sind.
Um eine private Prozedur anzulegen, wie folgt
vorgehen:
1.
Tragen Sie im Feld
Datenbankprozedur
einen Namen beginnend mit
P_
für die neue Prozedur ein.
Die private Datenbankprozedur wird nun anhand der
Standardprozedur
amic_excel_Preisimport_VK
bzw.
amic_excel_Preisimport_EK
mit notwendigen
Parametern angelegt.

---

## Neue Preis-Exceldatei in Referenz-ERP importieren F9

Neue Preis-Exceldatei in Referenz-ERP
importieren F9
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Preiskalkulation Excel
Funktion
Preiskalkulation Einkauf/Verkauf
Direktsprung
[PKX]
.
Funktion
Preiskalkulation Einkauf/Verkauf
Um die neue Preis-Exceldatei zu importieren, wie folgt
vorgehen:
1.
Prüfen Sie die Exceldatei mit den neuen Preisen oder leiten Sie die Kalkulation
zur Freigabe weiter.
2.
Klicken Sie auf
Preiskalkulation Verkauf bzw. Einkauf
oder drücken
Sie
F9
.
3.
Die Auswahlliste
Preiskalkulation
Dateiauswahl
öffnet sich.
4.
Wählen Sie die Datei aus, die importiert werden soll.
Die neuen Preise sind in
den Artikel und Ihren Preislisten hinterlegt.
Wenn die Übermittelung
einen Fehler ergab, wird eine Fehlermeldung aufgerufen.
Tipp!
Überprüfung der Preise prüfen!
Sie können die neue Preise über den Bereich Profile
prüfen:
•
Setzen Sie unter
Preise gültig am
ein Datum, das
>=
dem Datum Vorbelegung Preis ab aus ist.
Die neuen Preise werden nun in der Auswahlliste
bereits angezeigt und können abgeglichen werden.

---

## Rabatte

Rabatte
Definition lt. Wikipedia:
Ein Rabatt (von ital.: rabbattere = abschlagen,
abziehen) ist ein Nachlass vom Listenpreis einer Ware oder Dienstleistung oder
von dem Preis, den der Unternehmer in sonstiger Weise allgemein ankündigt oder
fordert (Netto-Verkaufspreis) oder ein Sonderpreis, der wegen der Zugehörigkeit
zu bestimmten Verbraucherkreisen, Berufen, Vereinen oder Gesellschaften
eingeräumt wird.
Verwendung in Referenz-ERP
Rabatte lassen sich in Referenz-ERP als automatische
Berechnung einrichten. Ebenso können Rabatte manuell im Anschluss an die
Erfassung einer Warenposition erfasst werden.
Die Berechnung eines Rabatts kann pro Warenposition
oder für eine Gruppe von Warenpositionen einer Gruppe (Rabattgruppe) als
Gruppenrabatt berechnet werden.

---

## Rabattgruppe

Rabattgruppe
Preise / Konditionen
Rabatte
Rabattgruppe
Oder Direktsprung
[RAG]
Artikel können eine Rabattgruppe und/oder eine
individuelle Rabattgruppe sowohl im Einkauf als auch im Verkauf zugeordnet
bekommen. Diese beschreibt jeweils die Zugehörigkeit zu einer Gruppe von
Artikeln, die alle für Kunden und Lieferanten mit einer dort zugeordneten
Rabattklasse beziehungsweise individuellen Rabattklasse einen Rabatt (einfach
oder gestaffelt) bekommen.
Rabattgruppen werden für Einkauf und Verkauf separat
eingerichtet. Sie werden im Artikelpfleger mit der Funktion
Gruppenzuordnungen
zugeordnet. Dabei kann eine Rabattgruppe sowohl als
normale wie auch als individuelle Rabattgruppe verwendet werden.
Im Pflegemodul
individuelle Preise/Rabatte
im Verkauf
[PRI]
und Einkauf
[PRIE]
können auch individuelle
Rabattzuordnungen für Artikel erfasst werden, denen noch keine individuelle
Rabattgruppe im Verkauf beziehungsweise Einkauf zugeordnet wurde. In diesem Fall
wird eine neue Rabattgruppe erzeugt und automatisch zugeordnet.

---

## Rabattklasse

Rabattklasse
Preise / Konditionen
Rabatte
Rabattklassen
[RAK]
Kunden/Lieferanten können eine Rabattklasse und/oder
eine individuelle Rabattklasse sowohl im Einkauf als auch im Verkauf zugeordnet
bekommen. Diese beschreiben jeweils die Zugehörigkeit zu einer Gruppe von
Kunden/Lieferanten, die alle für Artikel mit einer dort zugeordneten
Rabattgruppe beziehungsweise individuellen Rabattgruppe einen Rabatt (einfach
oder gestaffelt) bekommen.
Rabattklassen werden für Einkauf und Verkauf getrennt
angelegt. Sie werden im Kundenstamm auf der Registerkarte Klassen zugeordnet.
Dabei kann eine Rabattklasse sowohl als normale wie auch als individuelle
Rabattklasse verwendet werden.
Wenn eine neue Rabattklasse manuell angelegt oder
automatisch generiert wird, wird eine eindeutige Identnummer aus dem
Wertebereich oberhalb von 100.000.000 vorgeschlagen bzw. verwendet. Der Ident
wird in einer internen Tabelle gespeichert und ist somit verbraucht. Allerdings
können Sie bei manueller Anlage statt dem vorgeschlagenen Ident auch einen
eigenen Wert vergeben. Sobald sie das Feld verlassen, wird der eingetragene Wert
festgeschrieben und kann nicht mehr geändert werden.
Im Pflegemodul
individuelle Preise/Rabatte
im Verkauf
[PRI]
und Einkauf
[PRIE]
können auch individuelle
Rabattzuordnungen für Kunden/Lieferanten erfasst werden, denen noch keine
individuelle Rabattklasse im Verkauf beziehungsweise Einkauf zugeordnet wurde.
In diesem Fall wird eine neue  Rabattklasse erzeugt und automatisch
zugeordnet.

---

## Rabatt-Texte

Rabatt-Texte
Preise / Konditionen
Rabatte
Rabatt-Texte
Oder Direktsprung
[RAT]
Für die Standardsprache in Referenz-ERP kann hier ein
beliebiger Text angegeben werden, der für die Anzeige des Rabatts auf Belegen
verwendet werden soll.
Für die verschiedenen Sprachen in Referenz-ERP können hier
auch deren Übersetzungen eingegeben werden.
Es können bis zu 100 Texten hinterlegt werden.

---

## Rabattsätze

Rabattsätze
Preise / Konditionen
Rabatte
Rabattsätze
Oder Direktsprung
[RAS]
Es gibt für Rabatte bestimmte Rabattsätze, die in
bestimmten Zeiträumen gültig sind und in einer zu definierenden Formel zu
berechnen sind.
Rabattbezeichnung
Bezeichnung für den Rabatt
Steuerschlüssel
Steuerschlüssel für diesen Rabatt
Zu/Abschlagstyp (nur für
openTRANS
)
Hier wird die Art des Rabatts für openTRANS
eingestellt. Dieser sollte als „Rabatt“ eingestellt werden. Andere Werte machen
hier kaum Sinn.
Ab Datum
Beginn der Gültigkeit des Rabattsatzes
Bis Datum
Letzter Tag der Gültigkeit dieses Rabattsatzes
Zu-/Abschlagsformel
Formel
Bedeutung
proz. v. Warenw. Abz. Vorh.
      Rabatte
Hier
      wird der Rabatt als prozentualer Wert des Warenwerts berechnet. Vorhandene
      Rabatte werden abgezogen, damit sich nicht beide Rabatte
      addieren
proz. v. reinen
      Warenwert
Wie
      oben, Vorhandene Rabatte werden jedoch NICHT abgezogen. Es kann zu einer
      Addition von Rabatten kommen.
proz. m. Preisrundung abz. Vorh.
      Rabatte
Hier
      wird der Rabatt als prozentualer Wert des Warenwerts berechnet.
Hier
      findet nach der Rabattberechnung eine Rundung der Einzelbeträge statt, so
      dass diese stimmig sind.
Vorhandene Rabatte werden abgezogen,
      damit sich nicht beide Rabatte addieren
proz. mit Preisrundung
Wie
      oben, Vorhandene Rabatte werden jedoch NICHT abgezogen. Es kann zu einer
      Addition von Rabatten kommen
Satz
      entspricht Einzelpreis
Es
      wird ein fester Rabatt auf die Warenposition gegeben. Z.B. 5€ für jeden
      Kauf eines Gerätes
Satz
      je Mengeneinheit
Es
      wird ein fester Rabattbetrag pro Mengeneinheit gegeben. Wird z.B. in
      Tonnen fakturiert, so wird der Rabatt pro Tonne berechnet.
Satz
      je Gebindeeinheit
Es
      wird ein fester Rabattbetrag pro Gebindeeinheit gegeben. Werden also z.B.
      10 Paletten Steine gekauft, so wird 10x der Rabattbetrag
      berechnet.
Satz
      je Gewi
[...]


---

## Allgemeine Rabatte (Zuordnung von Rabattgruppen und Rabattklassen)

Allgemeine Rabatte (Zuordnung von Rabattgruppen und
Rabattklassen)
Preise / Konditionen
Rabatte
allgemeine Rabatte
Oder Direktsprung
[RAV]
In der Kombination von Kunden und Artikeln entstehen
automatische Rabattberechnungen. Diese Zuordnung erfolgt in dieser Anwendung.
Für Einkauf und Verkauf getrennt können hier Rabatte für die Kombination von
Rabattklasse
und
Rabattgruppe
eingerichtet werden.
Der Pfleger ermöglicht die Erfassung eines oder
mehrerer Rabatte, die in einer definierten Rangfolge eingetragen werden können.
So könnte z.B. grundsätzlich ein Rabatt von 2% gegeben
werden, jedoch vorrangig ein Rabatt ab einem Einkaufswert von 100€ (für die
Artikelgruppe) ein Rabatt von 5% gelten.
Rang
Rangfolge in der dieser Rabatt zu berücksichtigen ist.
Ein Rabatt, der bereits gegebene Rabatte berücksichtigt, sollte nicht an
oberster Stelle stehen, da andere Rabatte bei seiner Berechnung noch nicht
existieren.
Text-Nr.
Hier kann ein Text aus den
Rabatt-Texten
gewählt werden
Prfkt.
Preisfaktor (Anzahl der Mengeneinheiten) für Rabatte,
die nicht prozentual berechnet werden. So kann z.B. ein Rabatt pro 2 oder 10
Stück(ME) gegeben werden.
EKZ-Nr.
Erlöskennziffer des Rabatts. (0 = wie Artikel) siehe
auch „kalk“
Rab-Tab.
Hier wählen Sie einen der
Rabattsätze
aus, der gelten soll.
InZl
Ja/Nein-Entscheidung, ob dieser Rabatt auf dem
Ausdruck unterdrückt werden soll (JA), weil er lediglich zur internen
Preisermittlung dient oder dem Belegempfänger sichtbar ausgedruckt werden sill
(Nein).
GrpR
Einstellung
Bedeutung
Zeile
Zeilenrabatt – wirkt auf eine
      Warenposition
Gruppe
Gruppenrabatt – wirkt auf alle
      Artikel dieser Warengruppe
Preis
Dieser Rabatt wirkt zunächst auf den
      Einzelpreis, bevor dieser mit der Menge multipliziert wird.
kalk
Ja/Nein-Entscheidung, ob dieser Rabatt ein
kalkulatorischer Rabatt sein soll, der als Teil des Preises berechnet und nicht
gesondert ausgewiesen werden soll.
Kalkulatorische Rabatte werden im Gegensatz zu
kalkulat
[...]


---

## Individualpreise aktiv(SPA 10)

Individualpreise aktiv(SPA 10)
Bei „Ja“ sind individuelle Preise zulässig

---

## Entfernung von Preismatrizen zulässig(SPA 105)

Entfernung von Preismatrizen zulässig(SPA 105)

---

## Permanente Inventur Bewertungsverhalten (SPA 1072)

Permanente Inventur Bewertungsverhalten (SPA
1072)
Hier kann eingestellt werden, ob die Bewertungspreise
in den Inventurbelegen der permanenten Inventur Auswirkungen auf die Bewertung
eines Artikels haben können.

---

## Erweiterte Preisfindung im Barverkauf (SPA 1074)

Erweiterte
Preisfindung im Barverkauf (SPA 1074)
Einstellung
Bedeutung
Ja
Aktiviert die Referenz-ERP-Preisfindung
      außer Kontraktauswahl.
Nein
Standardpreisfindung im Barverkauf
      (Standard).

---

## Excel-Preiskalkulation-Lizenz (SPA1145)

Excel-Preiskalkulation-Lizenz
(SPA1145)
Lizenz für die
Excel-Preiskalkulation
.

---

## Individuelle Artikelpreisgruppen lagerübergreifend (SPA 1168)

Individuelle Artikelpreisgruppen lagerübergreifend (SPA 1168)
Parameter betrifft individuelle Preisgruppen,
individuelle Rabattgruppen und individuelle Zu-/Abschlagsgruppen am Artikel,
jeweils getrennt nach den Seiten Einkauf oder Verkauf.
Wird die individuelle Preispflege für einen Artikel
geöffnet, dem eine oder mehrere dieser Gruppen fehlen, so werden fehlende
Gruppen nunmehr vom System automatisch erzeugt. Das Verhalten wird dabei durch
den neuen Steuerparameter gesteuert:
Bei „Ja“: Alle Artikel mit identischer
Artikelstamm-ID, unabhängig von ihrem konkreten Lagerort, werden durchsucht und
die maximal zugewiesene individuelle Preisgruppe wird auch dem neuen Artikel
zugewiesen. Annahmegemäß ist dies auch die zuletzt verwendete Preisgruppe, was
zu einer lagerübergreifenden, einheitlichen Gruppenzuordnung bei allen Artikeln
führen wird. Wird diese maximale Gruppe nicht gefunden, wird automatisch eine
neue Gruppe erzeugt und dem Artikel zugewiesen.
Bei „Nein“ (Default-Wert): Insofern eine individuelle
Gruppenzuordnung fehlt, wird automatisch eine neue erzeugt und dem Artikel
zugewiesen.
Bei „Fragen“: pro Sachverhalt wird nachgefragt, ob
eine maximale individuelle Gruppe gesucht und zugewiesen werden soll (Ja-Fall)
oder ob eine neue Gruppe generiert wird (Nein-Fall):
Hinweis:
die automatische Zuweisung erfolgt
zukünftig immer
, nur noch die hierfür zu verwendende Preisgruppe kann über
diesen SPA gesteuert werden.

---

## Excel-Individualpreiskalkulation-Lizenz (SPA1167)

Excel-Individualpreiskalkulation-Lizenz (SPA1167)
Lizenz für die
Excel-Individualpreiskalkulation

---

## Position gilt als unbepreist(SPA 118)

Position gilt als unbepreist(SPA 118)
Hier wird festgelegt, wie der Parameter zu
interpretieren ist:
- manuelle Preiseingabe
- Einzelpreis 0,00
- Preis o. Wert 0
Diese Angabe hat Konsequenzen wenn z.B. unbepreiste
Positionen ausgewiesen werden sollen!

---

## Partiepreise aktiv(SPA 12)

Partiepreise aktiv(SPA 12)
Bei „Ja“ sind Partiepreise zulässig.

---

## Negative Werte durch Rabatte zulässig(SPA 123)

Negative Werte durch Rabatte zulässig(SPA 123)
Bei „Nein“ wird ausgeschlossen, dass Rabatte zu
negativen Beträgen führen.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Preisfindung angeschlossen(SPA 130)

Preisfindung angeschlossen(SPA 130)
Mit diesem Steuerparameter kann die Preisfindung
aktiviert / deaktiviert werden.

---

## Objektpreise aktiv(SPA 13)

Objektpreise aktiv(SPA 13)
Bei „Ja“ sind Objektpreise aktiv.

---

## Zu-/Abschläge auch bei manuellem Preis(SPA 143)

Zu-/Abschläge auch bei manuellem Preis(SPA 143)
Bei „Ja“ wird auch bei manueller Preiseingabe ein
automatischer Zu-/Abschlag gezogen

---

## Preisfindung bei Umwandlung zur Rechnung(SPA 147)

Preisfindung bei Umwandlung zur Rechnung(SPA 147)
Bei der Umwandlung eines Vorgangs zur Rechnung kann
eine automatische Preisfindung durchgeführt werden. Bei „Nein“ erfolgt dies
nicht, es gelten die im Ursprungsvorgang erfassten Preise und Konditionen.

---

## Fiktive Liefermenge aktiv(SPA 178)

Fiktive Liefermenge aktiv(SPA 178)
Für die Preisfindung bei mengenabhängigen Preisen kann
die fiktive Liefermenge aktiviert werden. Sie ist wichtig, wenn ein von der
Liefermenge abweichender Mengenbezug berücksichtigt werden muss.

---

## Bepreisungsdatum identisch Plandatum(SPA 183)

Bepreisungsdatum identisch Plandatum(SPA 183)
Ja: Es wird der zum Plandatum gültige Preis gezogen.
Nein: Der Preis hängt vom Preisdatum ab, das im
Vorgang eingegeben wurde. Dazu muss das entsprechende Eingabefeld per UFLD
aktiviert sein

---

## Preise aus Ordersatz übernehmen(SPA 204)

Preise aus Ordersatz übernehmen(SPA 204)
Ja: Der Preis aus dem Ordersatz wird in die
Zielwarenposition übernommen. Das Preisherkunftskennzeichen wird auf „Preis aus
Ordersatz“ gesetzt. Auch bei späteren Korrekturen findet keine erneute
Preisfindung statt.
Nein: Preisbehandlung in der Zielwarenposition wie bei
einer Neuerfassung.

---

## Preisfindung mit Objekt-Anfangsdatum(SPA 208)

Preisfindung mit Objekt-Anfangsdatum(SPA 208)
Bei ‚Ja‘ bezieht sich die Preisfindung auf das
Anfangsdatum des Objektes. Unabhängig von diesem Steuerungsparameter wird das
Preisbezugsdatum ebenfalls von der Preisgültigkeit im Objektstamm übernommen,
sofern dies dort so eingestellt wird.

---

## Objekt(e) mit Dreifach-Rabatten(SPA 215)

Objekt(e) mit Dreifach-Rabatten(SPA 215)
Ja: Es können bis zu drei (multiplikative) Rabatte pro
Artikel, Warengruppe, etc. vergeben werden. Nein: Es kann pro Artikel,
Warengruppe, etc. eine Rabattgruppe vergeben werden.

---

## Skontierung von Rabatten(SPA 228)

Skontierung von Rabatten(SPA 228)

---

## Belegte Referenznummer -> Vorgangsnummer(SPA 232)

Belegte Referenznummer -> Vorgangsnummer(SPA 232)
Der Steuerparameter bewirkt, dass die Referenznummer
des Warenwirtschaftsbelegs konditional in die Referenznummer in der
Finanzbuchhaltung übernommen wird.
Im Fall von Sammelbelegen wird dies durch die Nummer
des Sammelbelegs überschrieben.
Werte
0 –
      Nein
Keine Übernahme
1 -
      Ja
Übernahme erfolgt immer
2 -
      Einkauf
Übernahme erfolgt nur bei
      Einkaufsbelegen
3 -
      Verkauf
Übernahme erfolgt nur bei
      Verkaufsbelegen

---

## Listenpreise als Staffelpreise(SPA 266)

Listenpreise als Staffelpreise(SPA 266)

---

## Negative Einzelpreise zulässig(SPA 275)

Negative Einzelpreise zulässig(SPA 275)
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Preis und Zu-/Abschlag Schnellkorrektur(SPA 284)

Preis und Zu-/Abschlag Schnellkorrektur(SPA 284)

---

## Bewertung im Produktionsmodul(SPA 285)

Bewertung im Produktionsmodul(SPA 285)
Bestimmt die Preisfindung im Produktionsmodul. Im
Falle von „Listenpreis“ ist zusätzlich noch der Parameter 286 mit der
gewünschten Preisklasse festzulegen.

---

## Rabatte bei Partiepreisen aktiv(SPA 294)

Rabatte bei Partiepreisen aktiv(SPA 294)
Nein: Wenn bei der Preisfindung ein Partiepreis
gefunden wird, werden auf den so  gefundenen Preis keine automatischen
Rabatte gezogen.
Ja: Auch bei Partiepreisen sind automatische Rabatte
möglich.

---

## Zu-/Abschläge bei Partiepreisen aktiv(SPA 295)

Zu-/Abschläge bei Partiepreisen aktiv(SPA 295)

---

## Reihenfolge Zu-/Abschlags-Ermittlung(SPA 298)

Reihenfolge Zu-/Abschlags-Ermittlung(SPA 298)
Mit diesem Parameter wird bei der automatischen
Erzeugung von Rabatten, Zu- und Abschlägen, Frachten und anderen automatisch
generierten Zu- und Abschlag-Zeilen die Reihenfolge der Berücksichtigung nach
der Art der Positionszeilen festgelegt.

---

## Frachten bei Partiepreisen aktiv(SPA 296)

Frachten bei Partiepreisen aktiv(SPA 296)

---

## Zu-/Abschläge/Rabatte auf Aktionspreise(SPA 310)

Zu-/Abschläge/Rabatte auf Aktionspreise(SPA 310)
Nein: Wenn bei der Preisfindung ein Aktionspreis
gefunden wird, werden auf den so  gefundenen Preis keine automatischen
Zu-Abschläge und keine automatischen Rabatte gezogen.
Ja: Auch bei Aktionspreisen sind automatische
Zu-/Abschläge und automatische Rabatte
möglich.

---

## Rabattierung bei Objekt-Bewegungen(SPA 314)

Rabattierung bei Objekt-Bewegungen(SPA 314)
Dieser SPA steuert die Berücksichtigung der in dem
Objekt hinterlegten Rabatte:
Einstellung
Bedeutung
0 =
      Objekt
ACHTUNG: wirkt derzeit wie unter
      2
1 =
      Normal
Nur
      Standardrabatte ziehen, Objektrabatte  bleiben
      deaktiviert
2 =
      Alternativ
Es
      werden Standard und Objektrabatte gezogen

---

## Manuelle Preiseingabe bei Kasse möglich(SPA 324)

Manuelle Preiseingabe bei Kasse möglich(SPA 324)
Hier wird entschieden, ob man beim Kassieren auf der
Tresenkasse bzw. der POS-Kasse die Möglichkeit besitzen darf, auch gefunden
Preise zu ändern; d.h. es kann verboten werden, dass ein gefundener Preis
geändert werden kann.

---

## Automatische Rabatte bei Kasse aktiv(SPA 325)

Automatische Rabatte bei Kasse aktiv(SPA 325)
Hier wird bei der Tresen Kasse entschieden, ob für die
augenblicklich gezogene Position die automatischen Rabatte ziehen sollen.
Auch bei der POS-Kasse werden mit diesem
Steuerparameter die automatischen Rabatte ausgeschaltet.

---

## Separate Steuer auf Rabatte möglich(SPA 329)

Separate Steuer auf Rabatte möglich(SPA 329)

---

## Rabatte auch bei manuellem Preis(SPA 347)

Rabatte auch bei manuellem Preis(SPA 347)
Ja: Bei der Preisfindung ziehen die automatischen
Rabatte auch, wenn der Preis manuell erfasst bzw. manuell verändert wurde.
Nein: Es werden keine automatischen Rabatte gezogen,
wenn es sich um einen manuell erfassten / veränderten Preis handelt.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!
Hinweis: Steht der SPA zum Zeitpunkt der Erfassung
einer Quellposition auf „Nein“, so kann bei der Teildisposition dieser Position
kein Rabatt erfasst werden.

---

## Rabattgruppe bei manuellen eingebbar(SPA 344)

Rabattgruppe bei manuellen eingebbar(SPA 344)
Ja: wenn ein manueller Gruppenrabatt erfasst wird,
kann auch die Rabattgruppe erfasst werden.
Nein: die Rabattgruppe kann bei manuellen
Gruppenrabatten nicht verändert werden.

---

## Währungsnummer für ZuAbschläge etc. Ware(SPA 361)

Währungsnummer für ZuAbschläge etc. Ware(SPA 361)
Hier wird eingetragen, mit welcher Währungsnummer Zu-
/ Abschlagspreise geführt werden.

---

## Währungsbehandlung Zu- /Abschläge etc. Ware(SPA 363)

Währungsbehandlung Zu- /Abschläge etc. Ware(SPA 363)
Keine Umrechnung:
Zu-/Abschläge, Rabatte und Frachten werden nicht
umgerechnet, sie gelten explizit wie in den Tabellen hinterlegt.
Umrechnung laut Steuerparameter:
Die Werte der Tabellen verstehen sich in der Währung,
die unter Steuerparameter Nummer 12 und 13 in dieser Gruppe eingetragen
wurden.

---

## Preisanzeigefenster mit 0-Preisen(SPA 395)

Preisanzeigefenster mit 0-Preisen(SPA 395)
Dieser Parameter gibt an, ob Preise mit dem Wert 0 auf
der Hauptseite des Artikels sichtbar sind.

---

## Preiskalkulation: Default-Steuergruppe(SPA 404)

Preiskalkulation: Default-Steuergruppe(SPA 404)
Default-Steuergruppe bei Standardpreiskalkulation

---

## Preiskalkulation: Kalkulationsgrundlage(SPA 405)

Preiskalkulation: Kalkulationsgrundlage(SPA 405)

---

## Preiskalkulation: Makro-Unterstützung(SPA 406)

Preiskalkulation: Makro-Unterstützung(SPA 406)

---

## Preiskalkulation: zugelassene Artikel(SPA 408)

Preiskalkulation: zugelassene Artikel(SPA 408)

---

## Listenpreisänderungsprotokoll im VK(SPA 413)

Listenpreisänderungsprotokoll im VK(SPA 413)

---

## Listenpreisänderungsprotokoll im EK(SPA 414)

Listenpreisänderungsprotokoll im EK(SPA 414)

---

## Preiskalkulation: angezeigte Mengeneinheit(SPA 417)

Preiskalkulation: angezeigte Mengeneinheit(SPA 417)
Angezeigte Mengeneinheit bei manueller
Preiskalkulation

---

## Listenpreise optimiert speichern(SPA 420)

Listenpreise optimiert speichern(SPA 420)

---

## Preiskalk.: Original-Preise übernehmbar(SPA 421)

Preiskalk.: Original-Preise übernehmbar(SPA 421)

---

## Preiskalk.: Aktuelle Preise übernehmbar(SPA 422)

Preiskalk.: Aktuelle Preise übernehmbar(SPA 422)

---

## Originalpreisübernahme: KalkListenPreis löschen(SPA 423)

Originalpreisübernahme: KalkListenPreis löschen(SPA 423)

---

## Kalkpr.Übern.: KalkListenPreis löschen(SPA 425)

Kalkpr.Übern.: KalkListenPreis löschen(SPA 425)

---

## Aktpr.Übern.: KalkListenPreis löschen(SPA 424)

Aktpr.Übern.: KalkListenPreis löschen(SPA 424)

---

## Preiskalk.: Stapelkalkulation erlaubt(SPA 427)

Preiskalk.: Stapelkalkulation erlaubt(SPA 427)

---

## Preiskalk.: manuelle Kalkulation erlaubt(SPA 426)

Preiskalk.: manuelle Kalkulation erlaubt(SPA 426)

---

## Preiskalk.: EK-Listenpreisgruppen(SPA 428)

Preiskalk.: EK-Listenpreisgruppen(SPA 428)

---

## Nachkalkulation ohne KalkListenPreis(SPA 430)

Nachkalkulation ohne KalkListenPreis(SPA 430)

---

## Preisfindung-Lizenz(SPA 439)

Preisfindung-Lizenz(SPA 439)
Lizenz für Preisfindung.

---

## Preise im Preisanzeigefenster(SPA 463)

Preise im Preisanzeigefenster(SPA 463)
Dieser Parameter gibt an, welche Preise auf der
Hauptseite des Artikelpflegers sichtbar sind.

---

## Datenübernahme an Kasse aus Etikett(SPA 472)

Datenübernahme an Kasse aus Etikett(SPA 472)
Sollen Daten aus einem Strichcode, der z.B. an einer
Waage erzeugt wurde, an der Kasse übernommen werden? (Artikel, Menge und Preis
möglich)

---

## Inzeile Rab/ZuAb immer mit Preisrundung(SPA 495)

Inzeile Rab/ZuAb immer mit Preisrundung(SPA 495)
Es geht hierbei um die Preisrundung bei
Inzeilerabatten/ ZuAbschlägen:
Nein - nur bei Formeltyp mit Preisrundung
Ja - bei allen Formeltypen

---

## FRZ-Preis schlägt Aktionspreis(SPA 501)

FRZ-Preis schlägt Aktionspreis(SPA 501)
Ja: Wenn der Steuerparameter 20 bzw. 21 in dieser
Gruppe auf eine Preisliste verweist (d.h.  Aktionspreise angesprochen
werden) und wenn  es einen Eintrag in der fixen Preisliste in  FRZ
gibt, wird der so ermittelte Listenpreis gezogen. (wie
bisher)
Nein: Trotz des FRZ-Eintrages wird der Aktionspreis
gemäß Preisliste aus Steuerparameter 20 bzw. 21 dieser Gruppe gezogen.

---

## Kalkulatorische Rabatte zulässig(SPA 509)

Kalkulatorische Rabatte zulässig(SPA 509)
Hierdurch können kalkulatorische Rabatte
freigeschaltet werden. Bisher konnten nur Zu- / Abschläge kalkulatorisch
behandelt werden.
Einstellungen
Nicht behandeln
(Voreinstellung) kalkulatorische
      Rabatte werden wie gewöhnliche Rabatte behandelt.
verwenden
Kalkulatorische Rabatte werden
      verwendet (kalkulatorische Rabatte sind freigeschaltet)
ignorieren
Kalkulatorische Rabatte, so sie denn
      eingerichtet sind (z.B. als Vorbereitung auf eine Umstellung) werden nicht
      berücksichtigt und auch im Gegensatz zur Voreinstellung nicht als
      gewöhnliche Rabatte berechnet.

---

## Sonderpreise in Belegwährung umrechnen(SPA 512)

Sonderpreise in Belegwährung umrechnen(SPA 512)
Sonderpreise werden in dem Objekt immer in Buchwährung
geführt. Bei „Ja“ werden diese Preise in die Währung des Beleges umgerechnet,
bei „Nein“ werden die Preise ohne Umrechnung übernommen.

---

## Absolute Bezugsgröße bei Staffelzu-/Ab ?(SPA 524)

Absolute Bezugsgröße bei Staffelzu-/Ab ?(SPA
524)
Absolute Bezugsgröße für Staffelermittlung bei Zu- /
Abschlägen.
Bei „Ja“ wird bei negativen Werten mit dem positiven
Wert in der entsprechenden Staffel gesucht.

---

## Rabatte / Zu- /Abschläge mit 0 Wert drucken(SPA 536)

Rabatte / Zu- /Abschläge mit 0 Wert drucken(SPA 536)
Dieser Steuerparameter steuert das Druckverhalten von
Rabatten / Zu- / Abschlägen / Frachten, wenn der resultierende Betrag 0 ist.

---

## Mengenänderung setzt Einzelpreiseingabe(SPA 566)

Mengenänderung setzt Einzelpreiseingabe(SPA 566)
Bei „Nein“, bleibt ein manuell erfasster Gesamtbetrag
auch nach Änderung der Menge erhalten (der Preis wird angepasst!). Bei „Ja“ wird
nach jeder Mengenänderung die  Gesamtpreiseingabe wieder ausgeschaltet,
wenn sie vorher aktiv war.

---

## Preisliste für ext Bewertung Typ 10(SPA 573)

Preisliste für ext Bewertung Typ 10(SPA 573)

---

## Absolute Bezugsgröße Frachtermittlung(SPA 596)

Absolute Bezugsgröße  Frachtermittlung(SPA
596)
Absolute Bezugsgröße für Staffelermittlung bei
Frachtermittlung.
Bei „Ja“ wird bei negativen Werten mit dem positiven
Wert in der entsprechenden Staffel gesucht.

---

## Absolute Bezugsgröße Individualpreis(SPA 597)

Absolute Bezugsgröße Individualpreis(SPA 597)
Absolute Bezugsgröße für Staffelermittlung bei
gestaffelten Individualpreisen.
Bei „Ja“ wird bei negativen Werten mit dem
positiven Wert in der entsprechenden Staffel gesucht.

---

## Absolute Bezugsgröße Staffelpreis(SPA 598)

Absolute Bezugsgröße Staffelpreis(SPA 598)
Absolute Bezugsgröße für Staffelermittlung bei der
Preisermittlung Listenpreis.
Bei „Ja“ wird bei negativen Werten mit dem positiven
Wert in der entsprechenden Staffel gesucht.

---

## Automatische Rabatte(SPA 60)

Automatische Rabatte(SPA 60)
Bei „Ja“ werden die automatischen Rabatte
aktiviert.

---

## POS: letzte Artikelposition korrigierbar(SPA 608)

POS: letzte Artikelposition korrigierbar(SPA
608)
Standard: nein. Ja: Bis die Erfassung der
Folgeposition begonnen wird, sind Menge oder Preis oder Gesamtwert der
vorangegangenen Position korrigierbar.

---

## Produktion mit Partiepreisfindung(SPA 621)

Produktion mit Partiepreisfindung(SPA 621)
Bei „Ja“ wird bei der Preisfindung der Komponenten
zunächst geprüft, ob ein Partiepreis vorhanden ist. Falls ja, wird dieser
genommen, sonst findet die übliche Preisfindung der Produktion statt.

---

## Circle-Vorbelegung der Mengeneinheit (SPA 648)

Circle-Vorbelegung der Mengeneinheit (SPA 648)
Hier wird die Mengeneinheit für die manuelle
Preiseingabe bei einem Circle Geschäft vorbelegt.

---

## Rechnungen ohne Preis druckbar(SPA 72)

Rechnungen ohne Preis druckbar(SPA 72)
Teilweise oder vollständig unbepreiste Rechnungen
können vom Druck ausgenommen werden.

---

## Max. Vorkomma Preise (0=ohne Prüfung)(SPA 75)

Max. Vorkomma Preise (0=ohne Prüfung)(SPA 75)
Hier kann die maximal zulässige Vorkomma- Stellenzahl
für Preise eingetragen werden. Dieser Wert wird bei der Erfassung über- prüft.
Ist 0 eingetragen, erfolgt keine Prüfung.

---

## Preismengeneinheit aus Mengeneinheit übernehmen(SPA 772)

Preismengeneinheit aus
Mengeneinheit übernehmen(SPA 772)
Hier kann eingestellt werden, ob die
Preismengeneinheit aus der Mengeneinheit übernommen werden soll. Dies erfolgt
nur, wenn im Barcode eine Mengeneinheit eingerichtet wurde.

---

## Preismengeneinheit im openTRANS angeben (SPA 866)

Preismengeneinheit im openTRANS angeben (SPA
866)
Hier legen Sie fest, ob bei Verwendung von openTRANS
die Preismengeneinheit berücksichtigt (ja) oder der Preis in der Mengeneinheit
der Warenposition angegeben werden soll.
Bei Verwendung einer
Mengeneinheitsumschlüsselungsprozedur wird diese Option nicht ausgewertet.

---

## Listenpreise aktiv(SPA 9)

Listenpreise aktiv(SPA 9)

---

## Ordersatz: Automatische Zeilen Zu-/Abschläge bei Ordersatz(SPA 974)

Ordersatz: Automatische Zeilen Zu-/Abschläge bei
Ordersatz(SPA 974)
Ja: Es werden in der Zielwarenposition automatisch
eingerichtete Zeilen Zu-/Abschläge gezogen, wenn der Preis aus dem Ordersatz
übernommen wurde.
Nein: Automatische Zeilen Zu-/Abschläge werden in der
Zielwarenposition unterdrückt, wenn der Preis aus dem Ordersatz übernommen
wurde.
Genereller Hinweis: Automatische und manuelle Zeilen
Zu-/Abschläge werden nicht aus dem Ordersatz übernommen, sondern immer durch
eine Neuermittlung in der Zielwarenposition erstellt.
Zur Klarstellung: Bei der Erfassung des Ordersatzes
spielt dieser Steuerparameter keine Rolle.

---

## Ordersatz: Automatische Zeilen Rabatte bei Ordersatz(SPA 973)

Ordersatz: Automatische Zeilen Rabatte bei Ordersatz(SPA
973)
Ja: Es werden in der Zielwarenposition automatisch
eingerichtete Zeilen Rabatte gezogen, wenn der Preis aus dem Ordersatz
übernommen wurde.
Nein: Automatische Zeilen Rabatte werden in der
Zielwarenposition unterdrückt, wenn der Preis aus dem Ordersatz übernommen
wurde.
Genereller Hinweis: Automatische und manuelle Zeilen
Rabatte werden nicht aus dem Ordersatz übernommen, sondern immer durch eine
Neuermittlung in der Zielwarenposition erstellt.
Zur Klarstellung: Bei der Erfassung des Ordersatzes
spielt dieser Steuerparameter keine Rolle.

---

## Ordersatz: Automatische Zeilen Frachten bei Ordersatz(SPA 975)

Ordersatz: Automatische Zeilen Frachten bei Ordersatz(SPA
975)
Ja: Es werden in der Zielwarenposition automatisch
eingerichtete Zeilen Frachten gezogen, wenn der Preis aus dem Ordersatz
übernommen wurde.
Nein: Automatische Zeilen Frachten werden in der
Zielwarenposition unterdrückt, wenn der Preis aus dem Ordersatz übernommen
wurde.
Genereller Hinweis: Automatische und manuelle Zeilen
Frachten werden nicht aus dem Ordersatz übernommen, sondern immer durch eine
Neuermittlung in der Zielwarenposition erstellt.
Zur Klarstellung: Bei der Erfassung des Ordersatzes
spielt dieser Steuerparameter keine Rolle.

---

## Bezugsgrößenabhängige Zu-/Abschläge

Bezugsgrößenabhängige
Zu-/Abschläge
Preise / Konditionen
Zu-/Abschläge
Bezugsgrößenabhängige Zu-/Abschläge
Oder Direktsprung
[ZABZ]
Hier werden bestimmte Sätze, die in bestimmten
Zeiträumen gültig sind und in einer zu definierenden Formel zu berechnen sind
festgelegt.
Diese sind zusätzlich abhängig von definierten
Bezugsgrößen. Diese werden in der Spalte „Ab Bezugsgröße“ eingetragen.
Wird also ein Zuschlag pro Mengeneinheit definiert, so
kann dieser z.B. erst ab 100 Kg gelten.

---

## Generelle Zu-/Abschläge

Generelle
Zu-/Abschläge
Preise / Konditionen
Zu-/Abschläge
generelle Zu-/Abschläge
Oder Direktsprung
[ZAGE]
Es gibt für Zu-/Abschläge bestimmte Sätze, die in
bestimmten Zeiträumen gültig sind und in einer zu definierenden Formel zu
berechnen sind.
Zu-/Abschlag Bezeichnung
Bezeichnung für den Rabatt
Steuerschlüssel
Steuerschlüssel für diesen Rabatt
Zu/Abschlagstyp (nur für
openTRANS
)
Hier wird die Art des Zu-/Abschlags für openTRANS
eingestellt.
Ab Datum
Beginn der Gültigkeit des Satzes
Bis Datum
Letzter Tag der Gültigkeit dieses Satzes
Zu-/Abschlagsformel
Formel
Bedeutung
proz. v. Warenw. Abz. Vorh.
      Zu-Abschläge
Hier
      wird der Zu-Abschlag als prozentualer Wert des Warenwerts berechnet.
      Vorhandene Zu-Abschläge werden abgezogen, damit sich nicht beide
      Zu-Abschläge addieren
proz. v. reinen
      Warenwert
Wie
      oben, Vorhandene Zu-Abschläge werden jedoch NICHT abgezogen. Es kann zu
      einer Addition von Rabatten kommen.
proz. m. Preisrundung abz. Vorh.
      Zu-Abschläge
Hier
      wird der Zu-Abschlag als prozentualer Wert des Warenwerts berechnet.
Hier
      findet nach der Zu-Abschlagsberechnung eine Rundung der Einzelbeträge
      statt, so dass diese stimmig sind.
Vorhandene Zu-Abschläge werden
      abgezogen, damit sich nicht beide Zu-Abschläge addieren
proz. mit Preisrundung
Wie
      oben, Vorhandene Zu-Abschläg werden jedoch NICHT abgezogen. Es kann zu
      einer Addition von Zu-Abschlägen kommen
Satz
      entspricht Einzelpreis
Es
      wird ein fester Rabatt auf die Warenposition gegeben. Z.B. 5€ für jeden
      Kauf eines Gerätes
Satz
      je Mengeneinheit
Es
      wird ein fester Zu-Abschlagsbetrag pro Mengeneinheit gegeben. Wird z.B. in
      Tonnen fakturiert, so wird der Zu-Abschlag pro Tonne
      berechnet.
Satz
      je Gebindeeinheit
Es
      wird ein fester Rabattbetrag pro Gebindeeinheit gegeben. Werden also z.B.
      10 Paletten Steine gekauft, so wird 10x der Zu-Abschlagsbetrag

[...]


---

## Allgemeine Zu-/Abschläge (Zuordnung von Zu-/Abschlaggruppen und Zu-/Abschlagklassen)

Allgemeine Zu-/Abschläge (Zuordnung von Zu-/Abschlaggruppen und
Zu-/Abschlagklassen)
Preise / Konditionen
Zu-/Abschläge
allgemeine Zu-/Abschläge
Oder Direktsprung
[ZAVA]
In der Kombination von Kunden und Artikeln entstehen
automatische Zu-/Abschlagsberechnungen. Diese Zuordnung erfolgt in dieser
Anwendung. Für Einkauf und Verkauf getrennt können hier Zu-/Abschläge für die
Kombination von
Zu-/Abschlagklasse
und
Zu-/Abschlagklasse
eingerichtet werden.
Der Pfleger ermöglicht die Erfassung eines oder
mehrerer Zu-/Abschläge, die in einer definierten Rangfolge eingetragen werden
können.
So könnte z.B. grundsätzlich ein Zu-/Abschlag von 2%
gegeben werden, jedoch vorrangig ein Zu-/Abschlag ab einem Einkaufswert von 100€
(für die Artikelgruppe) ein Zu-/Abschlag von 5% gelten.
Rang
Rangfolge in der dieser Zu-/Abschlag zu
berücksichtigen ist. Ein Zu-/Abschlag, der bereits gegebene Zu-/Abschlag
berücksichtigt, sollte nicht an oberster Stelle stehen, da andere Zu-/Abschläge
bei seiner Berechnung noch nicht existieren.
Text-Nr.
Hier kann ein Text aus den
Zu-/Abschlagtexten
gewählt werden
Prfkt.
Preisfaktor (Anzahl der Mengeneinheiten) für
Zu-Abschläge, die nicht prozentual berechnet werden. So kann z.B. ein
Zu-Abschlag pro 2 oder 10 Stück(ME) gegeben werden.
EKZ-Nr.
Erlöskennziffer des Zu-Abschlags. (0 = wie Artikel)
siehe auch „kalk“
ZuAb-Art
Wählen Sie hier aus, aus welchem Bereich Ihr Zu-/Abschlag
kommen soll.
Zur Auswahl stehen
Generelle Zu-/Abschläge
,
Bezugsgrößenabhängige Zu-/Abschläge
,
Versandartabhängige
Zu-/Abschläge
,
Zahlungsartabhängige Zu-/Abschläge
.
ZuAb-Tab.
Hier wählen Sie einen der Sätze aus, der gelten soll.
InZl
Ja/Nein-Entscheidung, ob dieser Zu-Abschlag auf dem
Ausdruck unterdrückt werden soll (JA), weil er lediglich zur internen
Preisermittlung dient oder dem Belegempfänger sichtbar ausgedruckt werden soll
(Nein).
GrpR
Einstellung
Bedeutung
Zeile
Zeilenrabatt – wirkt auf eine
      Warenposition
Gruppe
Gruppenrabatt – wirkt auf alle

[...]


---

## Zu-/Abschlag-Texte

Zu-/Abschlag-Texte
Preise / Konditionen
Zu-/Abschläge
Zu-/Abschlag-Texte
Oder DIrektsprung
[ZATX]
Für die Standardsprache in Referenz-ERP kann hier ein
beliebiger Text angegeben werden, der für die Anzeige des Zu-/Abschlags auf
Belegen verwendet werden soll.
Für die verschiedenen Sprachen in Referenz-ERP können hier
auch deren Übersetzungen eingegeben werden.
Es können bis zu 100 Texten hinterlegt werden.

---

## Versandartabhängige Zu-/Abschläge

Versandartabhängige
Zu-/Abschläge
Preise / Konditionen
Zu-/Abschläge
Versandartabhängige Zu-/Abschläge
Oder Direktsprung
[ZAVS]
Hier werden bestimmte Sätze, die in bestimmten
Zeiträumen gültig sind und in einer zu definierenden Formel zu berechnen sind
festgelegt.
Diese sind zusätzlich abhängig von einer definierten
Versandart. Diese wird in der Zeile „Versandart“ eingetragen.
Der Zu-/Abschlag gilt also nur, wenn die definierte
Versandart verwendet wird. So lassen sich z.B. bestimmte Formate wie Rollen bei
bestimmten Versendern mit einem Zuschlag versehen.

---

## Zahlungsartabhängige Zu-/Abschläge

Zahlungsartabhängige
Zu-/Abschläge
Preise / Konditionen
Zu-/Abschläge
Zahlungsartabhängige Zu-/Abschläge
Oder Direktsprung
[ZAZA]
Hier werden bestimmte Sätze, die in bestimmten
Zeiträumen gültig sind und in einer zu definierenden Formel zu berechnen sind
festgelegt.
Diese sind zusätzlich abhängig von einer definierten
Zahlungsart. Diese wird in der Zeile „Zahlungsart“ eingetragen.
Der Zu-/Abschlag gilt also nur, wenn eine definierte
Zahlungsart verwendet wird. So kann z.B. bei Barzahlung oder Vorkasse ein
Abschlag berechnet werden.

---

## Preiskalkulation

Preiskalkulation
Aus der Anwendung Artikel wurde die Funktion "VK
Preise kalkulieren" entfernt. Zur Preiskalkulation empfehlen wir weiterhin den
bekannten Weg unter "Preise/Kondition->Preiskalkulation Excel
(Auswahlliste)".
Tags:
Abkündigung

---

## Tab: Allgemein

Tab: Allgemein
Allgemeine Hinweise zum Aufruf und zur Arbeitsweise
des Moduls sind
hier
zu finden.
Der Tabreiter „Allgemein“ ist eine Art
Schnellerfassung, die die aktuellen individuellen Preise, (individuelle) Rabatte
und (individuelle) Zu-/Abschläge auf einen Blick darstellt. Die einzelnen Blöcke
sind nur zu sehen, wenn die zugehörige Klasse und Gruppe ungleich Null sind.
Individueller
Preis
Hier wird der aktuelle Individualpreis angezeigt. Bei
einer hinterlegten Mengenstaffelung auf dem Reiter „ind. Preise“ wird immer der
Preis ab Menge 0 angezeigt.
Ist kein aktueller Individualpreis angelgt, kann man
diesen hier eintragen, die Vorbelegung für die Datumsgrenzen werden aus den
Einrichterparametern herangezogen. Sollte das Tagesdatum außerhalb dieses
Zeitraums liegen, wird sich das Grid bei verlassen und wieder betreten des
Reiters leeren, da es sich nicht um einen aktuellen Individualpreis handelt. Auf
dem Reiter „ind. Preise“ ist dann der Eintrag für diese Datumsgrenzen
vorhanden.
Das Feld Brutto wird aus dem Feld Bruttorechnung aus
dem Kundenstamm - Register „Kennzeichen“ - vorbelegt.
Für die Beschreibung der Einzelfelder vergleich
Tabreiter „ind. Preise“.
(Individueller)
Rabatt
Hier wird der (individuelle) Rabatt mit dem höchsten
Rang angezeigt.
Für die Beschreibung der Einzelfelder vergleich
Tabreiter „ind. Rabatt“/“Rabatt“.
(Individueller)
Zu-/Abschlag
Hier wird der (individuelle) Zu-/Abschlag mit dem
höchsten Rang angezeigt.
Für die Beschreibung der Einzelfelder vergleich
Tabreiter „ind. Zu-/Abschlag“/“ Zu-/Abschlag“.

---

## Artikelstamm und Artikel — Übersicht

Artikelstamm und Artikel — Übersicht
In den Artikelstammdaten werden alle Informationen
über einen Artikel zusammengefasst, auf die für eine weitgehend automatisierte
Verarbeitung zugegriffen werden muss. Dies sind z.B. Mengeneinheiten, Preise,
Gebindegröße etc. Da zur Vereinfachung der Erfassung bei der Anlage eines
Artikels auf vorerfasste Informationen zugegriffen wird, müssen diese natürlich
vorher angelegt worden sein. So wird sicherlich häufig die Mengeneinheit "Stück"
benötigt. Diese muss also zuvor in der Tabelle "Mengeneinheiten" erfasst
werden.
Vor der Erfassung der Artikelkonten sollten also
verschiedene Konstanten vorher eingegeben sein, da auf sie bei der
Stammdatenerfassung zugegriffen wird.
Aus der Sicht des Artikelstamms sind
dies:
•
Mengeneinheitsgruppen und Mengeneinheiten
•
Warengruppen
•
Steuersätze
•
Erlöskennziffern
Darüber hinaus können weitere Konstanten in
Abhängigkeit von der Anwendung hinzukommen. So sind die Gefahrgutkennzeichen zu
erfassen, wenn die Gefahrgutabwicklung aktiviert werden soll.
Bei den Artikeln wird unterschieden zwischen
Artikelstamm
[ARS]
und Artikel
[AR]
.
Der Artikel stellt die bebuchbare Einheit dar, z.B.
das Konto „Flasche Weißwein“ auf einem Lager. Lagerübergreifend weisen
bebuchbare Artikel jedoch zwingend Gemeinsamkeiten auf: Für eine gemeinsame
Bestandsführung müssen sie die gleiche Mengeneinheit besitzen und der gleichen
Warengruppe angehören; auch das Ge­wicht ist natürlich gleich. Diese Daten
werden im Artikelstamm zusammengefasst. Für die Erfassung ergeben sich dadurch
folgende Abläufe:
Wenn nur ein Lager vorhanden ist, erfolgt die
Stammdatenerfassung über den Anwahlpunkt Artikel
[AR]
, wo dann alle Informationen in einem
Ablauf erfasst werden
Sind Artikel auf mehreren Lagern vorhanden, ist es
sinnvoll über die Artikelstammerfassung zu arbeiten. Es werden dann zuerst die
übergreifenden Informationen eingegeben und dann aus der Erfassungsmaske heraus
die individuellen Daten pro Artikel
Ü
[...]


---

## Bewertungspreise

Bewertungspreise
Hauptmenü
Inventur
Bewertungspreise
Direktsprung
[IVP]
Es besteht die Möglichkeit Bewertungspreise getrennt
von Inventurbelegen zu erfassen.
Innerhalb dieser Anwendung stehen 3 Varianten zur
Verfügung:
1.
Die erfassten Bewertungspreise.
2.
Alle Artikel, die zum Inventurstichtag einen Buchbestand haben und die
Bewertungspreise, die für diese Artikel eingegeben wurden.
3.
Eine Gegenüberstellung von gewogenem, durchschnittlichem und letztem
Einkaufspreis und des Bewertungspreises laut Bewertungsgruppe des Artikels. Die
Auswahl umfasst ebenfalls alle Artikel, die zum Inventurstichtag einen
Buchbestand aufweisen.
Alle Varianten können nach Artikelnummer, Lagernummer,
Warengruppe zu einem Stichtag eingegrenzt werden.
An diese unterschiedlichen Varianten sind
unterschiedliche Funktionalitäten gekoppelt:
1.
dient zur manuellen Pflege von Bewertungspreisen
2.
dient zur Kalkulation von Bewertungspreisen
3.         ist
eine reine Übersichtsfunktion
Kalkulation von Bewertungspreisen F9
Die Kalkulation erfolgt auf Basis der maschinell
verfügbaren Preise:
-
gewogener Einkaufspreis
-
durchschnittlicher Jahreseinkaufspreis
-
letzter Einkaufspreis
-
Bewertungspreis des Artikels gemäß der vereinbarten Bewertungsgruppe
-
Niederstwertprinzip des kleinsten Preises aus
o
letztem und gewogenem
Einkaufspreis
o
letztem und durchschnittlichem
Einkaufspreis
o
letztem Einkaufspreis und
Bewertungspreis
Gemäß der gewählten Kalkulationsmethode werden die
entsprechenden Bewertungspreise ermittelt und in die Erfassungstabelle
eingetragen. Dort erhalten die Preise ein Kennzeichen „automatisch bewertet“.
Durch wiederholte Anwendungen der Kalkulation werden die jeweils aktuellen
Preise eingetragen. Dabei kann entschieden werden, ob die Kalkulation nur auf
automatisch kalkulierte Preise (erneut) angewendet wird oder sich die
Kalkulation nur auf Preis 0 bezieht
Damit wird verhindert, dass z.B. manue
[...]


---

## Datenexportprofil einrichten

Datenexportprofil einrichten
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Preiskalkulation Excel
Direktsprung
[PKX]
.
1.
Über das
Fernglas-Symbol
im Bereich Auswahl den Dialog
Preiskalkulation Excel VK
bzw. EK aufrufen.
2.
Wählen Sie die
Preisliste
aus, aus welcher die gefilterten Preise
gezogen werden sollen.
3.
Wählen Sie unter
Preis gültig am
ein Datum über den Kalender und
bestätigen Sie dies per Doppelklick.
ODER:
Tragen Sie ein
Gültigkeitsdatum
ein oder den Wert
heute
.
Hinweis!
Wenn sich in der Preisliste
auch Artikel befinden, die keinen Preis für den Tag hinterlegt haben, werden
auch diese in die Exceldatei exportiert.
Beachten Sie dies Verhalten
bei der Einstellung Ihrer Filterkriterien.
4.
Wählen Sie weitere Filterkriterien Ihrer Preise, indem vor dem Kriterium die
Optionsfelder aktivieren.
5.
Wählen Sie unter
Vorbelegung Preisliste
die Preisliste, in welche
die neuen Preise in Referenz-ERP importiert werden.
6.
Geben Sie unter
Vorbelegung Preis ab
und
Vorbelegung Preis
bis
den Gültigkeitszeitraum der neuen Preise für die Artikel ein.
7.
Speichern Sie die Einstellungen, indem Sie
F9
drücken oder
Speichern und zurück
in Optionsbox auswählen.
Die Auswahlliste wird
angezeigt Ihnen in Gruppierung der Preislistengruppe der gefilterten Artikel
an.
Hinweis!
Liste zeigt Gruppierung einer Preisliste
Die Liste zeigt
NICHT
die einzelnen Artikel an, sondern die
Gruppierungen und die Preislistengruppe an.
Selbst bei Filterung in Profilen explizit nach einem
oder mehreren Artikelnummern werden Gruppierungen und Preislistengruppen
angezeigt.
Dadurch können Sie bei der Kalkulation für Artikel mit
gleicher Preislistengruppe die Preise komfortabel einmal pflegen.
Wenn Sie den einzelnen Artikel anzeigen möchten, heben
Sie im Bereich Auswahl die Gruppierung auf.

---

## Default-Preismatrix, Kalkulations-Schema

Default-Preismatrix, Kalkulations-Schema
Im Artikel wird hinterlegt, welche Preismatrix aktiv
ist; dies könnten in Abhängigkeit vom Lager unterschiedliche sein. Hier im
Artikelstamm kann eine Vorbelegung vorgenommen werden, so dass die Eingabe im
Artikel nicht mehr erforderlich ist.
Für die Kalkulation von Listenpreisen steht ein
mächtiges System zur Verfügung. Die Verfahren werden innerhalb der
Preiskalkulation festgelegt; hier kann das für diesen Artikel gewünschte
zugeordnet werden.

---

## Default-Preisfaktoren, Preislimit

Default-Preisfaktoren, Preislimit
Default Preisfaktoren:
Der Preis eines Artikels bezieht sich auf eine Anzahl
Mengeneinheiten: z.B. pro 1000 Stück. Hier wird er seitens des Artikelstamms
voreingestellt für die Artikel.
Preisunter- und Preisüberschreitung:
Hier kann eine Sicherung zur Vermeidung fehlerhafter
Preiseingaben eingebaut werden. Geprüft wird der manuell eingegebene Preis bei
der Vorgangserfassung gegen den maschinell ermittelten. Wird die erste Schwelle
überschritten erfolgt eine Warnmeldung, bei der zweiten wird die Speicherung
verweigert. Bei der Prüfung werden auch Rabatte etc. berücksichtigt.

---

## Detaillierter Kontrakt

Detaillierter Kontrakt
Vom Standardkontrakt unterscheidet sich diese Variante
vor allem dadurch, dass innerhalb der generellen Kontraktlaufzeit (Laufzeit von
- bis) Zeitstaffeln für Mengen und Preise bestimmt werden können. So kann man
z.B. festlegen, dass innerhalb einer Gesamtlaufzeit von sechs Monaten monatliche
Mengen zu bestimmten Preisen abzunehmen sind. Der Erfassungsablauf ist
folgendermaßen:
1.
Zeiträume festlegen
2.
Artikeleingabe
Nach Ende der Artikelerfassung wird auf den
Ausgangsbildschirm zurückverzweigt, wo die erfassten Warenpositionen angezeigt
werden. Von hier aus werden Mengen und Preise den Zeiträumen zugeordnet.
Mengen
F10
Es werden die Zeitintervalle angezeigt. Mit
F5
können die Mengen im ausgewählten
Zeitraum eingetragen bzw. geändert werden.
Preise
F11
Die Zeitintervalle werden angezeigt. Mit
F5
können die Preise im ausgewählten
Zeitraum eingetragen bzw. geändert werden.
Nach Beendigung der Mengen- und Preiserfassung gelangt
man wieder in den Ausgangsbildschirm zurück.
Neben der Neuerfassungsfunktion
F8
kann von hier aus durch Markieren der
entsprechenden Position ein Artikel geändert
F5
oder gelöscht werden. Darüber hinaus
gibt die Funktion
Bewegungen
die
Möglichkeit, sich die Buchungen im Kontrakt anzeigen zu lassen.

---

## Dividenden verwalten

Dividenden verwalten
In dieser Liste sind die eingetragen Daten für die
Dividendenausschüttungen eingetragen. Folgende Daten werden angezeigt: Nummer,
Startdatum, Enddatum, Name, Beschlussdatum, Zahldatum, Leistung je Aktie,
Kapitalertragssteuer, Solidaritätszuschlag, Abgeschlossen, Gebucht,
Abrechnungsdatum.
Die Kapitalertragssteuer und der Solidaritätszuschlag
werden aus den Daten, die unter der Anwendung „Zinsabschlag“
[ZAS]
gepflegt werden berechnet und sind die
für den Zeitraum der Dividende geltende Kapitalertragsteuer und
Solidaritätszuschlag.
Nähere Angaben zu den anderen Daten sind
Dividenden verwalten
zu finden.
Über
Bereich
/Profile
kann nach folgenden Kriterien eingeschränkt werden: Startdatum
(von, bis), Enddatum (von, bis), Dividende (von, bis), Beschlussdatum (von,
bis), Zahldatum (von, bis), Leistung je Aktie (von, bis), Kapitalertragsteuer
(von, bis), Solidaritätszuschlag (von, bis). Bei dem Kriterium Dividende kann
über die Nummer der Dividende die Auswahl eingeschränkt werden.
Dem Benutzer stehen in dieser Ansicht folgende
Funktionen zur Verfügung:
•
(Dividende)
Neu
[siehe
Dividenden verwalten
]
•
(Dividende)
Ändern
[siehe
Dividenden verwalten
]
•
(Dividende)
Ansehen
[siehe
Dividenden verwalten
]
•
(Dividende)
Löschen
[siehe
Dividenden verwalten
]
•
Unternehmen verwalten
[siehe
Die Unternehmensdaten
einrichten/verwalten
]

---

## Exceldatei bearbeiten

Exceldatei bearbeiten
Die Kalkulation in Excel oder in einem anderen Programm kann
beginnen.
Beachten Sie nur die folgenden Hinweise dazu:
Hinweise!
1 Mit jeder Bearbeitung wird eine Exceldatei
angelegt
Damit es zu keinem Datenverlust kommt, wird
automatisch mit jedem Verlassen des Excelblatt angelegt unter dem eingerichteten
Dateipfad.
So können Sie jederzeit die Arbeit unterbrechen ohne
Datenverlust.
2 Abruf auf Referenz-ERP® Preiskalkulation überschreibt aktuelle
Auswahlliste in der Anwendung.
Damit Ihre aktuelle Auswahl nicht von einem anderen
Abruf einer Excelliste überschrieben wird, raten wir, sich im Team vor jedem
Import einer Preiskalkulation abzustimmen.
3 Nur die Spalte Preise bearbeiten
Damit die Übertragung der Preise fehlerfrei geschieht
und die Daten gematcht werden können,
DARF NUR
die Spalte Preise
bearbeitet werden.
Auch das Löschen einzelner Spalten ist zu vermeiden,
da eine Prüfung auf Vollständigkeit durchgeführt wird.

---

## Gruppen / Klassen

Grup
pen / Klassen
Folgende Eingaben sind möglich, wobei die
Klassenzuordnungen für Ein- und Verkauf unterschiedlich angelegt werden
können:
Listenpreisklasse
Gibt an, welcher Preisklasse der Kunde zugeordnet ist.
In Zusammenhang mit der
"Preisfindung auf
der Grundlage von Preislisten"
wird dann die dieser Preisklasse
zugeordnete Preisliste gezogen.
Mindestpreisklasse
Hier kann dem Kunden eine Mindest-Preisklasse
zugeordnet werden.
In Zusammenhang mit der Preisfindung auf der Grundlage von
Preislisten wird dann die dieser Preisklasse zugeordnete Preisliste
gezogen.
Abschlagspreisklasse
Innerhalb der Rohwarenabrechnung besteht die
Möglichkeit der Abschlagzahlungen. Hier kann der Kunde / Lieferant einer
Abschlagklasse zugeordnet werden.
WM – Preisklasse
Spezielle Abrechnungen in der Rohware benötigen
Weltmarktpreise. Hier erfolgt die Zuordnung von Kunden / Lieferanten und der
entsprechenden Preisklasse.
Individuelle Preisklasse
Für einzelne Kunden oder Kundenklassen können im
Artikelstamm Individualpreise hinterlegt werden. An der hier eingetragenen Nr.
erkennt Referenz-ERP, ob und welcher Preis gegriffen werden soll.
Rabattklasse
Wenn in Abhängigkeit vom Kunden Rabatte gewährt werden
sollen, so ist hier die Rabattklasse einzugeben. Sie kann sich individuell auf
diesen Kunden oder eine Klasse von Kunden beziehen. Bei der Anlage des Rabattes
(siehe "Rabatt") wird die Klasse eingetragen sowie die Artikelgruppe (die im
Artikelstamm hinterlegt ist), so dass die Beziehung zwischen Kunden und Artikel
eindeutig ist.
Individuelle Rabattklasse
Bei der Vergabe von Individualrabatten wird hier
automatisch die Zuordnung angelegt.
Zu- / Abschlagsklasse
Wenn in Abhängigkeit vom Kunden Zu- und Abschläge
gewährt werden sollen, so ist hier die Zu- / Abschlagsklasse einzugeben. Sie
kann sich individuell auf diesen Kunden oder eine Klasse von Kunden beziehen.
Bei der Anlage des Zu- / Abschlags
(siehe "Zu- /
Abschläge")
wird die Klasse eingetragen sowie die Artikelgrupp
[...]


---

## Gruppenzuordnungen

Gruppenzuordnungen
In den Konstanten und im allgemeinen Stammdatenbereich
wurde ausführlich auf die automatische Abwicklung bei Kunden- und
artikelabhängigen Ermittlung von Preisen, Rabatten, Zu-/Abschlägen, Frachten
etc. eingegangen. Die einzelnen Varianten der Wertermittlung werden in den
jeweiligen Abschnitten beschrieben. Auch wenn es mög­lich ist, sie
unmittelbar bei der Erfassung der Artikel einzurichten, so ist es für ei­nen
zügigen Ablauf wesentlich sinnvoller, dies im Voraus zu tun. Im Artikel wird
dann nur noch auf das entsprechende Verfahren Bezug genommen und die jeweilige
(Arti­kel-) Gruppe zugeordnet. Auf die Bedeutung u.a. Parameter wird in den
ent­sprechen­den Abschnitten eingegangen.

---

## Individuelle Preisgruppe

Individuelle Preisgruppe
Preise / Konditionen
Konstanten der Preispflege
Individualpreisgruppen
Oder Direktsprung
[PIG]
Artikel können eine Individualpreisgruppe sowohl im
Einkauf als auch im Verkauf zugeordnet bekommen. Diese beschreibt die
Zugehörigkeit zu einer Gruppe von Artikeln, für die für Kunden/Lieferanten mit
einer dort zugeordneten Individualpreisklasse zu einem Zeitraum ein bestimmter
gegebenenfalls mengenabhängiger individueller vom Listenpreis abweichender Preis
gilt.
Wenn eine neue individuelle Preisgruppe manuell
angelegt oder automatisch generiert wird, wird eine eindeutige Identnummer aus
dem Wertebereich oberhalb von 100.000.000 vorgeschlagen bzw. verwendet. Der
Ident wird in einer internen Tabelle gespeichert und ist somit verbraucht.
Allerdings können Sie bei manueller Anlage statt dem vorgeschlagenen Ident auch
einen eigenen Wert vergeben. Sobald sie das Feld verlassen, wird der
eingetragene Wert festgeschrieben und kann nicht mehr geändert werden.
Im Pflegemodul
individuelle Preise/Rabatte
im Verkauf
[PRI]
und Einkauf
[PRIE]
können auch individuelle
Preise für Artikel erfasst werden, denen noch keine individuelle Preisgruppe im
Verkauf beziehungsweise Einkauf zugeordnet wurde. In diesem Fall wird eine neue
individuelle Preisgruppe erzeugt und automatisch zugeordnet.

---

## (Individuelle) Rabatte

(Individuelle) Rabatte
Allgemeine Hinweise zum Aufruf und zur Arbeitsweise
des Moduls sind
hier
zu finden.
Spalte
Erklärung
Rang
Sortierung bei mehreren Rabatten.
      Wird dieser rausgenommen, kann der Rabatt entfernt werden.
Rabatt-Tabelle
Nummer der Rabatttabelle. In dieser
      sind die eigentlichen Rabatte zeitbezogen hinterlegt.
Rabatt-Bezeichnung
Bezeichnung der
      Rabatttabelle
Text-Nr.
Text
      der beispielsweise im Formular eingerichtet werden kann.
Text
Text, der zur Text-Nr. hinterlegt
      ist. Wenn ein Text mit einem * versehen ist, ist dieser nicht in der
      Hauptsprache eingerichtet.
Preisfaktor
Menge auf die sich der Rabatt
      bezieht. Nicht bei %-Rabatten relevant.
EKZ-Nr.
      (Erlöskennziffer)
Nummer der Erlöskennziffer beim
      Ziehen des Rabattes. Wenn eine 0 eingetragen wird, wird die
      Erlöskennziffer des Artikels gezogen.
EKZ-Bezeichnung
Bezeichnung der ausgewählten
      EKZ-Nummer
InZl. (In Zeile)
Kennzeichen, ob der Rabatt in der
      Artikelzeile oder als eigene Zeile erzeugt werden soll.
GrpR
      (Gruppenrabatt)
Kennzeichen, ob es sich hierbei um
      einen Gruppenrabatt handelt.
kalk.
      (Kalkulationskennzeichen)
Kennzeichen, ob es sich um einen
      kalkulatorischen Rabatt handelt, ob dieser also direkt im Preis enthalten
      ist.
Sp.
      (Sperrkennzeichen)
Möglichkeit der (vorübergehenden)
      Sperrung des Rabattes.
Schlüssel
Steuerschlüssel, hinterlegt im
      Rabattsatz. Wenn eine 0 eingetragen wird, wird der Steuerschlüssel der
      Warenposition gezogen). Sichtbar in Abhängigkeit von Steuerparameter 329
      („Separate Steuer auf Rabatte möglich“)
Schlüssel-Bezeichnung
Bezeichnung des Steuerschlüssels.
      Sichtbar in Abhängigkeit von Steuerparameter 329 („Separate Steuer auf
      Rabatte möglich“)
Die untere Tabelle bezieht sich immer auf die in der
oberen Tabelle ausgewählte Zeile und enthält die Informationen zur ausgewählten
Rabatttabelle.
Spalte
Erklärung
ab
[...]


---

## Lieferscheinerfassung

Lieferscheinerfassung
Bei angeschlossener Kontraktverwaltung werden die
Kontraktbedingungen bei der Vorgangserfassung automatisch berücksichtigt. Mit
Eingabe des Kunden, des Artikels und der Menge sind alle Informationen für die
Preisfindung über den Kontrakt vorhanden.
Erfassung
Der Rechnungserfassungsbildschirm (wie auch alle
anderen Vorgänge) hat dann zum Beispiel folgenden Aufbau:
Rechts neben dem Gesamtpreis wird angezeigt, dass es
sich um einen Kontraktpreis handelt. In den beiden letzten Zeilen werden
Kontraktnummer und -bezeichnung angezeigt
Über die Funktion
Kontraktauswahl
werden weitere
Informationen über Laufzeit, Restmenge, etc. angezeigt.
Wenn mehr als ein zulässiger Kontrakt im Zeitraum zur
Verfügung steht, zeigt Referenz-ERP, in Abhängigkeit von der Parametereinstellung und
insbesondere bei Überziehung von vereinbarten Zeitraummengen, die Alternativen
an:
Aus diesen Alternativen wird dann der gewünschte
mittels Cursorpositionierung ausgewählt.
Ist im
Steuerungsparameter
s
846 die Option
“
Variable Kontraktzeitraumzuordnung
“ mit dem Wert 1
eingestellt, so erscheint eine erweiterte Maske mit Darstellung der Zeiträume
der Kontraktposition.
Hier kann auf der Zeitraumtabelle unabhängig vom
Lieferdatum ein beliebiger Zeitraum durch Positionierung in der Zeitraum-Tabelle
gewählt werden. Zu beachten ist, das bei Einstellung der Option „MENGEUEBER“ im
Steuerungsparameter
s
846 mit dem Wert „1“ nicht die
tatsächlichen Restmengen der einzelnen Zeiträume dargestellt werden. Stattdessen
werden in einem Zeitraum auftretende negative Restmengen im jeweils folgenden
Zeitraum verrechnet.
Die Handlungsalternativen werden angezeigt. Eine
dieser Alternativen muss gewählt werden, da eine Übernahme von nicht möglichen
Angaben nicht zugelassen wird.
Bei den Handlungsalternativen handelt es sich um die,
die auch tatsächlich in diesem Augenblick bestehen. Wenn z.B. keine Restmenge
mehr verfügbar ist, wird die Alternative „Rest bis zum aktuellen Zeitraum
abb
[...]


---

## Definition von Listenpreisen

Definition von Listenpreisen
Preise / Konditionen
Konstanten der Preispflege
Preilistenbezeichnungen
Oder Direktsprung
[PRLB]
Artikel zu einer
Listenpreisgruppe
können mehrere
Listenpreise haben, die durch Listenpreisdefinitionen zu unterscheiden sind.
Verschiedene Listenpreise werden mittels der
Preismatrix
des Artikels und den
Preisklasse
Gruppen von Kunden oder Lieferanten
zugeordnet.
Neben der identifizierenden Preislistennummer sollte
die Listenpreisdefinition mit einer aussagekräftigen Bezeichnung versehen
werden. Die Kennzeichnung als Bruttopreis bewirkt in Anwendungen mit
Nettopreisen ein Herausrechnen des jeweiligen Steueranteils. Ist die
Preiskorrektursperre gesetzt, so können Preise dieser Listenpreisdefinition
nicht im Modul zur
Listenpreispflege
geändert werden. Auch ist an dieser Stelle
die Währung festgelegt, in der Preise dieser Preisdefinition zu verstehen sind.
Für die
Standard-Preiskalkulation
wichtig sind die Angaben, ob ein
durch diese Listenpreisdefinition definierter Listenpreis „kalkuliert“ werden
darf, also als Ergebnis einer Kalkulationsformel „linksseitig“ auftreten darf,
sowie die Sortierung für die Auswahl beim Aufbau von Kalkulationsformeln. Ist
letzterer Wert = 0, so soll kein Preis dieser Listenpreisdefinition zur
Kalkulation herangezogen werden. Außerdem erfolgt die Angabe, wie Preise dieser
Preisdefinition zu runden sind.

---

## Preisgruppe für Listenpreise

Preisgruppe für Listenpreise
Preise / Konditionen
Konstanten der Preispflege
Oder Direktsprung Listenpreisgruppen
[PRLG]
Einem Artikel wird im Einkauf und im Verkauf jeweils
eine Listenpreisgruppe zugeordnet. Mit Hilfe der jeweiligen Preisgruppe werden
Listenpreise
zum
Artikel bestimmt. Bei Neuanlage eines Artikelstamm-Satzes werden bereits
automatisch je eine solche Preisgruppe im Einkauf und Verkauf erzeugt, die
Artikeln zu diesem Artikelstamm bei deren Anlage automatisch zugeordnet werden.
Neben der identifizierenden Preisgruppennummer und dem Kennzeichen, ob diese
Gruppe im Einkauf oder Verkauf zu nutzen ist, wird als Bezeichnung der Gruppe
die Artikelstammnummer generiert.
Sollen für Artikel, die eine bestimmte
Listenpreisgruppe zugeordnet haben, mengenabhängige Listenpreise vergeben
werden, so wird an dieser Stelle in der Listenpreisgruppe die Staffelpreisnummer
einer
Listenpreis-Staffel
festgelegt.

---

## Definition von Listenpreis-Staffeln

Definition von
Listenpreis-Staffeln
Preise / Konditionen
Konstanten der Preispflege
Listenpreis-Staffeln
Oder Direktsprung
[PRLS]
Eine Listenpreis-Staffel kann in
Listenpreisgruppen
zugeordnet
werden und dient dem Zweck, einen Listenpreis mengenabhängig gestalten zu
können. Dazu wird in einer Listenpreisstaffel jedem mengenabhängig
einzurichtenden
Grundpreis
, repräsentiert per
Listenpreisdefinition
in
Preismatrizen
,
eine Mengenstaffel definiert, die für Mengenuntergrenzen eine andere
Listenpreisdefinition festlegt, unter deren Nummer der dann relevante Preis zu
führen ist.
Die Pflege der Staffelpreise können so im Modul zur
Listenpreispflege
bearbeitet werden.

---

## Lagerarten

Lagerarten
Blocklager
Ein Blocklager ist die preiswerteste und Platz
sparende Lagermöglichkeit. Sie eignet sich für Waren, die gut stapelbar sind.
Ladeträger mit Waren werden in Reihen hintereinander oder in Reihen von Stapeln
hinter einander gestellt. Dadurch ist der Zugriff auf einen spezifischen
Ladeträger nicht möglich.
Typischerweise werden Waren im Blocklager Sorten- und
Partierein in einen Block gestellt, damit zumindest eine Auswahl des Blocks nach
FIFO gewährleistet sein kann.
Das Blocklager verfügt über eine implizite Kapazität.
Die Anzahl verfügbarer Lagerplätze richtet sich nach der Stapelbarkeit der Ware,
der maximalen Stapelhöhe (evtl. durch Gewicht limitiert) und dem zur Verfügung
stehenden Platz. Eine Verwaltung freier Plätze findet hier nicht statt.
Regal-Lager
Ein Regallager zeichnet sich durch Regale aus, die
einzeln erreichbar sind und bei denen jeder Regalplatz eine eigene Nummer
bekommt. Die Ladeträger werden bei der Einlagerung einem spezifischen Lagerplatz
zugewiesen und können hier auch gezielt abgeholt oder einem Auftrag zugewiesen
werden. Die Anzahl freier Lagerplätze ist bekannt und der Realisierung von FIFO
steht kaum etwas entgegen.

---

## Navigation in der Marktkasse

Navigation in der Marktkasse
Wird eine Funktion wie „Preis ändern“, „Menge ändern“,
„Position nochmal“ oder eine der Rabatt-Funktionen aufgerufen, so bezieht sich
die nachfolgende Bearbeitung stets auf die markierte Position. Es ist möglich im
Bon-Fenster eine beliebige Position anzuklicken und damit für die Bearbeitung
auszuwählen.
Wurde keine Position explizit ausgewählt, so ist die
letzte Artikel-/Warenposition markiert.
Hinweise:
•
Abweichend vom Verhalten der „normalen“ Vorgangserfassung wird der Cursor
(Markierung) nach dem kurzzeitigen Verlassen der Maske für Eingaben im
Vorgangskopf, nicht auf die erste, sondern auf die letzte Artikel-/Warenposition
gesetzt. Funktionsaufrufe betreffen also die letzte Artikel-/Warenposition.
•
Erfassungen finden unabhängig von der aktuellen Cursorposition immer
unterhalb der letzten Artikel-/Warenposition statt.

---

## Mengeneinheiten mit Umrechnungen (Ergebnismengeneinheit)

Mengeneinheiten mit Umrechnungen (Ergebnismengeneinheit)
Wenn im Ein- und Verkauf, der Bestandsführung und der
Preisfindung bei einem Artikel unterschiedliche Mengenbezüge erforderlich sind,
müssen, um die erforderlichen Umrechnungen automatisch durchführen zu können,
Umrechnungsfaktoren und -formeln festgelegt werden. Zuvor müssen jedoch die
Grundeinheiten bestimmt sein. In einem einfachen Beispiel (Bestand in kg, Preis
pro 100 kg) sind dann folgende Angaben erforderlich:
Nummer:
Nummer der zu definierenden Mengeneinheit
Grundeinheit:
Nummer der Grundeinheit, auf die zurückgerechnet
werden soll, z.B. "kg".
Kurztext:
Kurzbezeichnung der Mengeneinheit (z. B. für
Ausdrucke), z.B,"dt".
Bezeichnung:
Ausführliche Bezeichnung der Mengeneinheit, z. B. für
Auswahllisten.
Umrechnung:
Umrechnungsfaktor für die Ermittlung der Anzahl
Grundmengeneinheiten je Mengeneinheit. In diesem Fall "100", denn 1 dt
entspricht 100 kg.

---

## Preislisten

Preislisten
Hauptmenü
Preise/Konditionen
Preise
Preisliste oder Preisliste n. WGr., Lg …
Es gibt folgende Preislisten:
Preisliste (für eine Preisklasse):
Hier werden die Preise für Artikel auf dem
entsprechenden Lager und der zugehörigen Warengruppe  zu einem bestimmten
Datum angezeigt.
Die Datumauswahl wird mit dem aktuellen Tagesdatum
vorbelegt; kann aber geändert werden.
Preisliste n. WGr, Lager, Artikel:
Hier werden die Preise für Artikel nach Lager und
Warengruppe gruppiert zu einem bestimmten Datum angezeigt.
Die Datumauswahl
wird mit dem aktuellen Tagesdatum vorbelegt; kann aber geändert werden.

---

## Preiszeiträume in der Partie

Preiszeiträume in der Partie
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Mit dieser Funktion wird eine Information über die
hinterlegten Partiepreise gebracht.

---

## Produktpreise F11

Produktpreise F11
Hier kann man die Preise für das Hauptprodukt in
Abhängigkeit von Zeiträumen und Mengeneinheiten festlegen.

---

## Provisionsstaffelungen

Provisionsstaffelungen
Die Provisionsstaffelung funktioniert wie folgt:
Aus einer Preisliste, die den Vertretern als
Referenzpreisliste zugeordnet ist, werden Preise zugrunde gelegt. Hierzu muss
unter
[OPT]
(Optionen) eine Preisliste
als Referenzpreisliste ausgewählt werden:
(Im Anwahlpunkt OPT mit
F8
eine neue Option anlegen;
F3
in „Option Name“, dort
„Vertref_Preisliste“ auswählen; Bediener zuordnen; unter Wert die
Preislisten-Nr. eintragen.)
Der Vertreter hat nun die Möglichkeit, von dieser
Preisliste nach
oben
bzw. nach
unten
abzuweichen. Um die Provision
anzupassen, können hier nun die Provisionen den erzielten Preisen angepasst
werden.
Dies ist für die Bereiche Einkauf
(EK)
und
Verkauf
(VK)
realisiert.
Gruppe
Gruppennummer der Vertreter
Bezeichnung
Ausführliche Bezeichnung.
Rechenart
1 = prozentuale Provision bei prozentualen
Abschlägen
2 = prozentuale Provision bei DM/EUR Abschlägen
3 = DM/EUR Provision bei prozentualen Abschlägen
4 = DM/EUR Provision bei DM/EUR Abschlägen
Stufen 1 – 100
Hier können je nach Differenzwert zu der
Referenzpreisliste in % oder DM/EUR (je nach Rechenart) die zur Berechnung
kommenden Provisionswerte eingegeben werden.
Hierbei ist zu beachten, dass
ein Wert bei Wertdifferenz 0 oder, wenn zulässig bei einem höheren Preis als in
der Referenzpreisliste angegeben ein Höchstwert mit - Vorzeichen eingegeben
werden muss (hier -1.000). Ansonsten würde keine Provision berechnet werden.

---

## Rabatte / Zu-/Abschläge / Preise

Rabatte / Zu-/Abschläge / Preise
Wenn für diesen Kunden allgemeine oder individuelle
Rabatte und Zu-/Abschläge sowie individuelle Preise eingetragen sind, wird in
der Funktionsbox die Bearbeitungsmöglichkeit dieser Werte angeboten. Sie
entspricht den im Abschnitt „Preise / Konditionen“ dargestellten Abläufen.

---

## Preisfindung

Preisfindung

---

## Preiskalkulation (generelle Einrichtung)

Preiskalkulation (generelle Einrichtung)

---

## Vertreterprovisionsstaffeln Variante 2

Vertreterprovisionsstaffeln
Variante 2
Felder:
Feld
Bedeutung
Klasse
Nummer der
      Vertreterklasse
Bezeich
Bezeichnung der
      Vertreterklasse
ProvGruppe
Nummer der
      Vertreterprovisionsgruppe
Bezeich
Bezeichnung der
      Vertreterprovisionsgruppe
EK-VK
Gibt
      an, ob die Staffel für den Einkauf oder Verkauf eingerichtet
      wurde.
Suchmöglichkeiten
Feld
Bedeutung
VertrProvGruppe
Dieser Filter erlaubt einem die
      Auswahlliste nach bestimmten Provisionsgruppen zu durchsuchen
Klasse
Dieser Filter erlaubt einem die
      Auswahlliste nach bestimmten Vertreterklassen zu durchsuchen
Einkauf/Verkauf
Dieser Filter erlaubt einem die
      Auswahlliste nach Provisionsstaffeleinrichtung für den Einkauf oder
      Verkauf zu durchsuchen
Funktionen:
Funktion
Beschreibung
Ändern
(F5)
Ruft
      den
Pfleger
der
      Vertreterprovisionsstaffeln auf im Ändernmodus auf.
Ansehen
(F6)
Ruft
      den
Pfleger
der
      Vertreterprovisionsstaffeln auf im Ansehenmodus auf.
Löschen
(F7)
Ruft
      den
Pfleger
der
      Vertreterprovisionsstaffeln auf im Löschenmodus auf.
Neu
(F8)
Ruft
      den
Pfleger
der
      Vertreterprovisionsstaffeln auf im Neumodus auf. TODO Pflegerverlinkung
      anpassen

---

## Gebindebearbeitung

Gebindebearbeitung
Änderung Gebindemengeneinheit
Das Ändern der Gebindemengeneinheit ist auf der
Gebindemaske möglich. Dort steht das Feld „Gebinde“ zur Verfügung. Nachdem die
Einheit geändert wurde, werden die Faktoren aus der entsprechenden
Faktorherkunft
der Gebindeeinheit
befüllt.
Preismengenbezugsübernahme
Als Voraussetzung für die Preismengenbezugsübernahme
gilt, dass in der
Formularzuordnung
die
„Gebinde Preismengenbezugsübernahme“ auf „Ja“ steht, in der
Gebindeeinheit
die Einheiten für die
Faktoren und eine Mengeneinheit in „Mengeneinheit Preisbezug“ eingetragen sind.
Des Weiteren erfolgt die Mengenübernahme nur, wenn es sich um ein Einzelgebinde
handelt.
Die Mengenbezugsübernahme erfolgt immer, wenn sich das
Gebinde oder die Preismengeneinheit ändert. Welche Menge übernommen wird,
entscheidet die Preismengeneinheit. Es wird das „Zwischenergebnis“ übernommen,
wo der Faktor die gleiche Mengeneinheit hat wie die Preismengeneinheit. Sollte
keine Menge gefunden werden, wird die Menge nicht geändert.
Beispiel:
Es handelt sich um 5 Gebinde bestehend aus 10
„Kartons“ mal 7 „Schalen“ mal 0,750 „Kg“.
Die Preismengeneinheit ist „Kartons“. Als Menge würde
in diesem Fall 50 „Kartons“ übernommen werden. Sollte die Preismengeneinheit auf
„Schalen“ geändert werden, würde als Menge 350 „Schalen“ übernommen werden.

---

## Preisinformation F11

Preisinformation F11
Das Werkzeug „Preisinformation“ hat seinen Ursprung in
der Entwicklung von Referenz-ERP. Um zu erfahren, welche Funktionen mit welchen
Parametern in welcher Reihenfolge zu dem ermittelten Preis geführt haben, wird
ein Protokoll beim Einstieg in die einzelnen Methoden geführt, das mit dieser
Funktion angezeigt werden kann. Es zeigt die durchlaufenden Funktionen von oben
nach unten an.
Die Informationen werden nicht gespeichert, stehen
also nur im Verlauf der Erfassung zur Verfügung. Das Protokoll beinhaltet alle
Einträge der Preisermittlung von Beginn der Erfassung an, also auch alle
Schritte, die sich durch Änderungen ergeben.
Die Anzeige wendet sich in erster Linie an Entwickler
und ist deshalb zum Teil sehr technisch geprägt.

---

## Weitere Kennzeichen

Weitere Kennzeichen
Hierüber werden verschiedene Abläufe gesteuert:
Rabattsperre:
Im Artikel kann das Rabattsperrkennzeichen gesetzt
werden, um zu verhindern, dass dieser rabattiert wird.
Siehe
Rabattsperre im Artikel
.
Bonussperre:
Trotz Bonusgruppen sollen keine automatischen
Ermittlungen erfolgen.
Fakturiersperre:
Dieser Artikel kann bei der Vorgangsbearbeitung im
Verkauf nicht mehr erfasst werden.
Diverser Artikel:
Hierunter ist ein Artikel-Sammelkonto zu verstehen.
Bei „Ja“ wird bei der Positionserfassung automatisch
die Artikeltextmaske zur Vergabe des Textes für diese Position geöffnet.
WEB-Artikel:
Dieser Artikel ist ein Web-Artikel.
Partiezuordnung:
Artikel können Partien zugeordnet werden.
Dabei wird, sollte die Zuordnung notwendig sein, der
Eintrag einer Partie gefordert.
Ausprägung
Bedeutung
Egal
Dem
      Artikel können Partien zugeordnet werden, es ist jedoch nicht
      notwendig.
Immer mit Partie
Partien werden immer
      berücksichtigt.
Ohne
      Partie
Partien werden nicht
      berücksichtigt.
Keine Automatische Partie im
      Beleg
Siehe Ausprägung.
Skontierfähigkeit im Ein-, und Verkauf:
Kennzeichnet, ob der Artikel bei Ein-, bzw. Verkauf
Skontierfähig ist.
Lagerabholschein:
Ausprägung
Bedeutung
Kein
      Abholschein / änderbar
Es
      wird von sich aus kein Abholschein gedruckt. Es kann jedoch gedruckt
      werden.
Abholschein / änderbar
Es
      wird Abholschein gedruckt. Dieser muss jedoch nicht gedruckt
      werden.
Immer Abholschein
Es
      wird
immer
ein Abholschein für diesen Artikel gedruckt.
Nie
      Abholschein
Es
      wird
niemals
ein Abholschein für diesen Artikel
      gedruckt.
Gruppenzuordnung:
Hier wird der Artikel den verschiedenen Gruppen
zugeordnet.
Dieser kann z.B. einer Rezepturgruppe für die
Produktion, einer Provisionsgruppe für die Vertreterabrechnung, einer
Rohwarengruppe für die Rohwarenabwicklung.
Näheres dazu in den jeweiligen Themengebieten.
Rabatt direkt erfassen:
Bei ‚Ja‘ wird im V
[...]


---

## Aktueller Preis

Aktueller Preis
Im Bereich ‚Aktueller Preis‘ werden die zur Zeit
gültigen Preise des Artikels gezeigt, sortiert durch den im Feld ‚Sortierung
(Kalkulation)‘ der Preislistenbezeichnung eingetragenen Wert; ist dieser 0, so
wird die Preisliste nicht angezeigt.

---

## Alle Artikel mit ArtiListenPreis

Alle Artikel mit ArtiListenPreis
Hier können Artikel mit folgender Bereichsauswahl
selektiert werden:
Artikelnummer:
Auswahl von Unter- und Obergrenze der zu
berücksichtigenden Artikelnummern.
ACHTUNG: Die Artikelnummer ist alphanumerisch, d.h.
die Auswahl ist lexikographisch!
Artikel gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Gültigkeits-AbDatum im angegebenen Bereich liegt!
Warengruppe:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Warengruppe im angegebenen Bereich liegt!
Lagernummer:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Lagernummer im angegebenen Bereich liegt!
Zusätzliche Einschränkungen:
Es werden nur Artikel in die Auswahlliste übernommen,
die über eine Kalkulationsschemanummer größer 0 verfügen.
Es werden nur Artikel in die Auswahlliste übernommen,
die keine Grundartikel sind.
Es werden nur Artikel in die Auswahlliste übernommen,
deren Kalkulationsschema als Kalkulationsgrundlage die Relation ArtiListenpreis
verwendet.
Die Auswahlliste zeigt für jeden Artikel folgende
Werte:
Befinden sich Artikel in der Auswahlliste, so können
diese bzw. die hierfür markierten Artikel kalkuliert werden. Hierfür stehen zwei
Funktionen zur Verfügung:
Einzelkalkulation      F5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: manuelle Kalkulation erlaubt‘
mit dem Wert ‚Ja‘ eingestellt ist.
Stapelkalkulation     SF5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: Stapelkalkulation erlaubt ‘
mit dem Wert ‚Ja‘ eingestellt ist.

---

## Alle Artikel mit KalkListenPreis

Alle Artikel mit KalkListenPreis
Hier können Artikel mit folgender Bereichsauswahl
selektiert werden:
Artikelnummer:
Auswahl von Unter- und Obergrenze der zu
berücksichtigenden Artikelnummern.
ACHTUNG: Die Artikelnummer ist alphanumerisch, d.h.
die Auswahl ist lexikographisch!
Artikel gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Gültigkeits-AbDatum im angegebenen Bereich liegt!
Kalk.Pr. gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
zu deren VK-Listenpreisgruppe zur eigenen Filialnummer Preise in der Relation
KalkListenPreis vorhanden sind, deren AbDatum im angegebenen Bereich liegen!
Warengruppe:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Warengruppe im angegebenen Bereich liegt!
Lagernummer:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Lagernummer im angegebenen Bereich liegt!
Zusätzliche Einschränkungen:
Es werden nur Artikel in die Auswahlliste übernommen,
zu deren VK-Listenpreisgruppe zur eigenen Filialnummer in der Relation
KalkListenPreis mindestens ein Preis vorhanden ist.
Es werden nur Artikel in die Auswahlliste übernommen,
die über eine Kalkulationsschemanummer größer 0 verfügen.
Es werden nur Artikel in die Auswahlliste übernommen,
die keine Grundartikel sind.
Es werden nur Artikel in die Auswahlliste übernommen,
deren Kalkulationsschema als Kalkulationsgrundlage die Relation KalkListenpreis
verwendet.
Die Auswahlliste zeigt für jeden Artikel folgende
Werte:
Befinden sich Artikel in der Auswahlliste, so können
diese bzw. die hierfür markierten Artikel kalkuliert werden. Hierfür stehen zwei
Funktionen zur Verfügung:
Einzelkalkulation      F5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: manuelle Kalkulation erlaubt‘
mit dem Wert ‚Ja‘ eingestellt ist.
Stapelkalkulation     SF5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: Stapelkalkulation erlaubt ‘
mit dem Wert ‚Ja‘ eingestellt ist.

---

## Allgemeine Hinweise

Allgemeine Hinweise
Dienstleistungen
Werden in einem Beleg Dienstleistungen des
Warenempfängers gegengerechnet (typischer Weise Trocknung bei
Getreideanlieferungen), so wird dies in Referenz-ERP® mit einer positiven Menge und
einem negativen Preis dargestellt.
Aufgrund der Bestimmungen zur Erstellung einer
eRechnung, wird dies jedoch im eRechnungs-Beleg genau umgekehrt dargestellt,
also mit negativer Menge und positivem Preis.
Fallen Steuern für diese beiden Positionen mit dem
gleichen Steuersatz an, so werden diese gegeneinander aufgerechnet. Die
eRechnung sieht keine separate Ausweisung von Vorsteuer und Umsatzsteuer vor.

---

## Artikelerfassung (F4)

Artikelerfassung (F4)
Mit Eingabe von
F4
wird die Artikelerfassung aktiviert. Mit
der Artikelerfassung können sehr komplexe Funktionen, wie z.B. Preisfindung,
Objektverwaltung, Leergutverwaltung etc. ablaufen. Hierauf soll an dieser Stelle
nicht näher eingegangen werden. Hier soll nur die prinzipielle Bedienung der
Erfassungsmaske erläutert werden.
Vorab ein wichtiger
Hinweis
:
Wird eine
Artikelposition im Korrekturmodus bearbeitet, so wird die ursprüngliche Menge
(vor der Korrektur) aus den Beständen des Artikels und von bereits zugeordneten
Partien, Kontrakten usw. zunächst herausgerechnet. Nur so ist es möglich, mit
einer nun gegebenenfalls geänderten Menge zu prüfen, ob noch genügend Bestand
für die neue Menge vorhanden ist. So ist zum Beispiel der Ausweis des
Partiebestands bei der Partieauswahl oder des Kontraktbestands bei der
Kontraktauswahl immer so zu verstehen, dass die ursprüngliche Positionsmenge
hierin nicht berücksichtigt ist.
Im Prinzip läuft die Erfassung einer Artikelposition
in
drei Schritten
ab:
1.
Artikel suchen
2.
Menge eingeben
3.
Preis eingeben

---

## Artikel löschen (inkl. 1+2+7+8+16)

Artikel löschen (inkl. 1+2+7+8+16)
Es werden die Daten in folgenden Tabellen
gelöscht:
artikel
artikelstamm
artikeltext
ARTILISTENPREIS
ARTILPREISGRUPPE
ARTIstamgebinde
ARTIGEBINDE
ARTISTUECKKOMP
ARTIKELADDON
ARTIKELMASKEDATEN
ARTILPRPROTOKOLL
ArchivArtikelAuftrag
WAREOANALYSE
ARTIHERSTPREIS
ARTIAUSPRAEG
ARTIGEFAHRKLASSE
ARTIKELINFOSEITE
ARTILIEFERANT
ARTIGEFAHRKLASSE
ARTISUCHBEGR
ARTIAUSWEICH
ARTISEKUNDSCHL
ARTIBESTAUSPR
ARTIHERSTELL
ARTIAUSPGEBINDE
WAGRUSPEZARTIKEL
EZG_ARTIKELLISTE
ARTIINTRASTAT
ARTIZUSAMMENSETZ
ARTIKELSTAMMADDON
ARTIKUNDARNR
ARTIFOLGEARTIKEL
kalklistenpreis
kalkliprschema
repllistenpreis
preiskalkrefliste
artiindivpreis
ARTIIPREISGRUPPE
Bemerkung unter der Bedingung: where (BemerkTyp = 11)
or (BemerkTyp = 12) or (BemerkTyp = 13) or (BemerkTyp = 15) or (BemerkTyp =
17)
SekundSchluessel unter der Bedingung: where
SekuRelation = 'Artikelstamm'
nachhaltigkeit_artikelstammvorbelegung
nachhaltigkeit_massebilanzArtikelsummen
disposition
MarktStandTexte
marktstandangebote
ArtiMerkmal
ArbeitsBuchungen
KTRDISPOSITION
o_satzneu
SaatgutSaatentnahme
RohSorteKosten
RohSorteArtikel
BAUSTPREIS
BAUSTARTIMENGE
BAUSTARTIKEL
LVS_Ladetraegertyp
StreckenerfassungArtiStammID
sinfos1
ArtikelTextBlob
ogznb
ARTISTUECKLISTE
HANDELSSTUECKLISTE
REZEPTURGRUPPE
ARTISTUECKPREIS
Es werden die Daten in folgenden Tabellen
aktualisiert:
RohSorteArtikel mit Aktualisierung: set
ArtikelId=0
RohSorteKosten mit Aktualisierung: set ArtikelId=0
Beim Löschen der Artikel werden automatisch die
Vorgänge Ware
,
Vorgänge
Finanzbuchhaltung
,
Kontrakte
,
Partien
und
Saatgut
mit gelöscht.

---

## Artikel-Sekundärmaske

Artikel-Sekundärmaske
Das Kalkulationsschema, die
Default-Preismatrix-Einträge des Artikelstamms sowie die im Artikel hinterlegten
Preismatrix-Einträge sind nun auch vom Artikelpfleger erreichbar. Hierzu gibt es
eine neue Artikel-Sekundärmaske, die über den OB-Eintrag „Preismat./Kalk.Schema“
aufgerufen wird. Im Falle der Neuanlage eines Artikelstammes können hier auch
die stammspezifischen Felder gepflegt werden.

---

## Artikelstamm-Sekundärmaske

Artikelstamm-Sekundärmaske
In der zum Artikelstamm-Pfleger gehörigen
Sekundär-Maske „Zusatzinfos“ wird das für das ZG-Preiskalkulationsmodul
benötigte Artikelstammfeld
ArtiStamGrundArt
Ja-/Nein-Feld zur Bestimmung von Grundartikeln, deren
Preise nicht dezentral gepflegt werden können.
aufgenommen.

---

## Artikelstamm-Sekundärmaske „Default-Preismatrix“

Artikelstamm-Sekundärmaske „Default-Preismatrix“
Im Artikelstamm-Pfleger gibt es eine neue
Sekundär-Maske, zum Pflegen folgender Artikelstammfelder:
PreisMatNummerVK
Vorbelegung für VK-Preismatrix-Feld im Artikel bei
Artikelneuanlage zum Artikel (ist somit jetzt pflegbar!).
PreisMatNummerEK
Vorbelegung für EK-Preismatrix-Feld im Artikel bei
Artikelneuanlage zum Artikel (ist somit jetzt pflegbar!).
Diese Felder geben es bereits im Artikelstamm, wurden
aber bisher nicht offengelegt. Bei manueller Neuanlage eines Artikels einem
Artikelstamm, werden die Artikelfelder PreisMatNummerVK und PreisMatNummerEK mit
den entsprechenden Artikelstammfeldern vorbelegt.
PrKalkSchema
Neues Artikelstammfeld zum Einstellen des im
Kalkulationsmodul für Artikel dieses Artikelstamms gültigen Schemas.

---

## Aufruf aus Artikel [AR]

Aufruf aus Artikel [AR]
Nach Auswahl eines Artikels kann der
Preisstapelpfleger über das Kontextmenü, Menüpunkt „Preise
à
individuelle Preispflege“, oder mit der
Tastenkombination Umschalt F5 gestartet werden:
Wie bereits erwähnt, erfolgt die Datenbereitstellung
über die Ladeprozedur
HoleIndividuellePreiseArtikel
. Die Ergebnismenge
wird entsprechend in einem Gitter dargestellt:
Gezeigt werden die Daten des zuvor ausgewählten
Artikels „005“ mit den Attributen Lager und Warengruppe wie oben dargestellt.
Dargestellt werden ferner alle Kunden, ausgedrückt über ihre individuelle
Preisklasse, zu denen individuelle Preise vorliegen. Hier im Beispiel wurde die
individuelle Preisklasse „123456791“ zugewiesen. Da der Kunde 10042 als
Kontokorrentkunde angelegt wurde, besitz er neben Verkaufs- auch Einkaufspreise.
Die entsprechenden Preisgruppen/Preisklassen werden nach Verschieben des Cursors
im Preisstapelpfleger aktualisiert:
Da nun Einkaufspreise gezeigt werden, ändern sich auch
die zugrundeliegende Preisgruppe für den Artikel auf „100000035“ und die
individuelle Preisklasse auf „100000042“ für die Einkaufsseite. Zusammenhängende
Einträge sollen durch eine Markierung „X“ in der Spalte „Gruppierung“ gezeigt
werden. Am Kreuzungspunkt dieser Dimensionen stehen die eigentlichen
individuellen Preisdaten, sortiert nach „gültig ab“, „gültig bis“ und der „ab
Menge“. Beim Aufrufen der Anwendung Individuelle Preise über die Auswahlliste
Artikel [AR] ist aktuell ein
Standardprofil
vorgesehen, welches nicht
verändert werden kann, für die gängigen Anwendungsfälle aber völlig ausreichend
ist. Dieses Standardprofil unterstützt keine diskreten Preispunkte, sondern
zeigt lediglich eine Ab-Menge und eine Preisinformation für den
Gültigkeitszeitraum „gültig ab“ und „gültig bis“. ACHTUNG: von der Ladeprozedur
HoleIndividuellePreiseArtikel
werden grundsätzlich die
heute
gültigen Einträge bereitgestellt. Ihr gültig-ab Datum ist
kleiner oder
gleich
dem heutigen Tagesdatum
[...]


---

## Auswahllistenvarianten (Preiskalkulation)

Auswahllistenvarianten (Preiskalkulation)
Die Anwendung ‚Standard-Preiskalkulation‘ verfügt über
mehrere Auswahlvarianten:
A) Per Ref.Liste und KalkListenPreis
B) Per Ref.Liste und ArtiListenPreis
C) Alle Artikel mit KalkListenPreis
D) Alle Artikel mit ArtiListenPreis
Es werden jedoch nur die per nachfolgend beschriebenen
SPA-Einstellungen möglichen Varianten in der Anwendung zur Verfügung
gestellt:
Liste der herangezogenen SPA’s:
Preiskalkulation: Kalkulationsgrundlage
Werte:
0: Grundpreise aus <KALKLISTENPREIS> zu letztem
Zeitraum
1: Zeitraum manuell, Grundpreise=Listenpreise des
aktuellen Zeitraums
2: In Kalkulationsschema anzugeben
Preiskalkulation: zugelassene Artikel
0: alle Artikel
1: nur Artikel aus Referenzliste
Variante A steht zur Verfügung bei den
SPA-Einstellungen
Kalkulationsgrundlage = 0 oder 2
zugelassene Artikel = 1
Variante B steht zur Verfügung bei den
SPA-Einstellungen
Kalkulationsgrundlage = 0 oder 1
zugelassene Artikel = 1
Variante C steht zur Verfügung bei den
SPA-Einstellungen
Kalkulationsgrundlage = 0 oder 2
zugelassene Artikel = 0
Variante D steht zur Verfügung bei den
SPA-Einstellungen
Kalkulationsgrundlage = 0 oder 1
zugelassene Artikel = 0

---

## Auswahllistenvarianten (Preisnachkalkulation)

Auswahllistenvarianten (Preisnachkalkulation)
Die Anwendung ‚Standard-Preiskalkulation‘ verfügt über
zwei Auswahlvarianten:
A) Per Ref.Liste
C) Alle Artikel
Es ist steht jedoch nur diejenige Variante zur
Verfügung, die sich aus der Einstellung des SPA’s ‚Preiskalkulation: zugelassene
Artikel‘ ergibt:
1: nur Artikel aus Referenzliste : Variante A
0: alle Artikel : Variante B
In beiden Varianten können Artikel mit folgender
Bereichsauswahl selektiert werden:
Artikelnummer:
Auswahl von Unter- und Obergrenze der zu
berücksichtigenden Artikelnummern.
ACHTUNG: Die Artikelnummer ist alphanumerisch, d.h.
die Auswahl ist lexikographisch!
Artikel gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Gültigkeits-AbDatum im angegebenen Bereich liegt!
Warengruppe:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Warengruppe im angegebenen Bereich liegt!
Lagernummer:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Lagernummer im angegebenen Bereich liegt!
Zusätzliche Einschränkungen:
Es werden in der Variante A nur Artikel in die
Auswahlliste übernommen, deren VK-Listenpreisgruppe sich in der Referenzliste
befinden.
Es werden nur Artikel in die Auswahlliste übernommen,
die über eine Kalkulationsschemanummer größer 0 verfügen.
Es werden nur Artikel in die Auswahlliste übernommen,
die keine Grundartikel sind.
Es werden nur Artikel in die Auswahlliste übernommen,
deren Kalkulationsschema als Kalkulationsgrundlage die Relation KalkListenpreis
verwendet.
Die Auswahlliste zeigt für jeden Artikel folgende
Werte:
Befinden sich Artikel in der Auswahlliste, so können
diese bzw. die hierfür markierten Artikel kalkuliert werden. Hierfür stehen zwei
Funktionen zur Verfügung:
Einzelkalkulation      F5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: manuelle Kalkulation erlaubt‘
mit dem Wert ‚Ja‘ eingestellt ist.
Stapelkalkulation     SF5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: Stapelkalkul
[...]


---

## Bedeutung des indiv. Gültig-bis-Feldes

Bedeutung des indiv. Gültig-bis-Feldes
Ausgangssituation: Anwender arbeitet mit zwei
Preispunkten 01.10.2025 und 01.11.2025. Für das gültig-bis Datum wurde der
30.11.2025 gewählt: der Preisstapelpfleger funktioniert noch wie gewünscht:
Preispunkte können gepflegt werden. Von der Datenstruktur her wird das Datum
30.11.2025 an die Preisdatensätze geschrieben –
das gültig-bis Feld kann
nicht leer sein
!
Nun wird über das Profil (Funktionstaste F6) ein
weiterer Preispunkt aktiviert: 01.12.2025. ACHTUNG: der eben gezeigte Artikel
005 FEHLT nun in der Ergebnismenge, es gibt keine Preisbänder die an ALLEN
Preispunkten gültig sind
à
Einträge
mit gültig-bis 30.11.2025 fehlen, da sie zum 01.12.2025 nicht mehr gültig sind,
wir diesen Preispunkt aber zusätzlich aktiviert haben!
Die Lösung ist nun, über das Feld „indiv. Gültig-bis“
die Gültigkeit des Preisbandes zu erweitern,
BEVOR
ein Preispunkt
aktiviert wird, welcher zeitlich
NACH
dem letzten Preispunkt liegt.
In der Zeile für ab-Menge „0“ den 31.12.2025 in der
Spalte indiv. Gültig-bis eintragen und mit der Eingabetaste bestätigen: Die
Eingabe wird vom System in alle relevanten Zeilen kopiert:
Dann den aktuellen Stapelpfleger mit Taste F9
speichern: das gültig-bis Datum wird so aktualisiert und gespeichert:
Wird nun das zusätzliche Preisband ab dem 01.12.2025
aktiviert, können Preise über den 30.11.2025 hinaus für alle drei Preisbänder
erfasst und gespeichert werden:
Alternativ hierzu könnte man von Anfang an mit
Gültigkeiten bis zum
Jahresultimo
arbeiten, so dass alle nachgelagerten
Preispunkte immer in den Gültigkeitszeitraum fallen und bearbeitet werden
können! Möchte man hingegen mit diskreten, überschneidungsfreien Preisbändern
arbeiten, muss man sich stets oben beschriebener Problematik bewusst sein.

---

## Beispiele:

Beispiele:
Vom Vorgangsdatum abweichendes Bepreisungsdatum
Um die Preisermittlung vom Vorgangsdatum
(Rechnungsdatum) unabhängig zu machen, gibt es die Möglichkeit, ein separates
Bepreisungsdatum mittels
UFLD
einzurichten, das ggf. auf
der Hauptmaske des Vorgangs abgefragt wird und bei einer Eingabe die Grundlage
für das Suchen nach Listen- und Individualpreisen sowie Rabatten und
Zu-/Abschlägen liefert. Wurde kein separates Datum eingegeben, so gilt weiterhin
das Vorgangsdatum als Grundlage.
Das Bepreisungsdatum wird aber selbstverständlich bei
Umwandlungen an den Folgevorgang weitergereicht, so dass beispielsweise die
Eingabe eines Bepreisungsdatums beim Auftrag oder Lieferschein in der Rechnung
erhalten bleibt.
Bonität
Es ist eine reine Anzeige aus dem Kundenstamm.
Änderungsmöglichkeiten bestehen nicht.
Steuergruppe
Anzeige der Steuergruppe des Kunden. Änderungen können
sinnvoll sein, wenn es sich (im Ausnahmefall!) um eine Rechnung aus dem Ausland
handelt, obwohl der Kunde im Inland sitzt. Sinnvoller ist es jedoch, die
Standardeinstellung nicht zu verändern, sondern das Kundenkonto zusätzlich mit
der anderen Steuereinstellung anzulegen.
Fakturiergruppe
Hierbei handelt es sich um ein Auswertungskennzeichen,
dessen Bedeutung im Unternehmen selbst festgelegt wird. Entsprechend sinnvoll
können hier manuelle Änderungen sein.
Zahlungsart
Vorbelegt mit der Standardzahlungsart des Kunden. Für
einen konkreten Fall kann man jedoch hiervon abweichen, z.B., um einem Kunden,
der normalerweise per Scheck bezahlt eine Nachnahmerechnung zu schicken.
Der Steuerparameter “Zahlungsart maximal wie im
Kundenstamm” (Parametergruppe: Vorgangsbearbeitung allg.) hat folgende
Bedeutung:
“Ja” (Default):
Es kann nur eine kleinere Zahlungsart als
vorgeschlagen eingegeben werden (z.B. Kundenstammeintrag 4 kann nur auf 1..3
geändert werden, nicht aber auf 5.
“Nein”:
keine Einschränkung bei der Vergabe
Versandart
Vorbelegt aus dem Kundenstamm. Kann hier entsprechend
der k
[...]


---

## Beispiel für Gruppe 16 (Schema)

Beispiel für Gruppe 16 (Schema)
Es können hier Gruppen für jeden in der Relation
PREISLISTE enthaltenen Preisbezeichnungseintrag ohne
Preiskorrektursperrkennzeichen und mit einer Kalkulationssortierung > 0.00
angelegt werden, im Kalkulationsmodul werden jedoch nur diejenigen
berücksichtigt, deren Preise auch manuell änderbar und im Preismatrixaufbau
vorhanden sind.
Die Bedingungen gelten global für das gesamte Schema,
also gruppenunabhängig. Sie werden erst angewandt, bevor die Preise nach der
Kalkulation gespeichert werden.

---

## Das Barverkaufssystem

Das Barverkaufssystem
Das Barverkaufssystem ermöglicht innerhalb von Referenz-ERP
die Abwicklung von Bargeschäften. Hierbei stehen die vielfältigen Möglichkeiten
der Belegerfassung und der Preisfindung von Referenz-ERP zur Verfügung.
Referenz-ERP nutzt zur Abwicklung dieser Aufgaben
verschiedene Kassenarten:
•
Die POS-Kasse (veraltet – wird nicht mehr gepflegt)
•
Die Tresenkasse
•
Die Marktkasse
Diesen Kassen ist ein Zahlungsmodul nachgeschaltet,
das unterschiedlich gestaltet ist.
Das Zahlungsmodul der Tresenkasse wird dann auch bei
Abschöpfung, Einzahlung etc. benutzt.
Hierbei handelt es sich aber nicht um verschiedene
Kassen, sondern lediglich um unterschiedliche Formen der Erfassung.
Die Einrichtungs- und Eröffnungs- sowie die
Abschlussabläufe sind daher gleich.
Zu einem exemplarischen Kassentag gehören so folgende
Abläufe:
•
Gesamtbarverkaufssystem eröffnen
(Systembetreuer/Administrator)(optional)
•
Kasse/n eröffnen (Kassenbenutzer)
•
Barvorgänge erfassen an den unterschiedlichen Kassen (Kassenbenutzer)
•
Kassen abschließen (Kassenbenutzer)
•
Gesamtbarverkaufssystem abschließen
(Systembetreuer/Administrator)(optional)
Die Eröffnungen und Abschlüsse werden über die
gleichen Funktionsaufrufe gestartet, wobei die zur Verfügung stehenden
Funktionen je nach Status der Kasse (offen/abgeschlossen/unterbrochen)
freigeschaltet werden.

---

## Eingabe zu großer Zahlen mit Scanner:

Eingabe zu großer Zahlen mit Scanner:
Der
SPA max. Vorkommastellen Wert. Menge, Preis
begrenzt die Eingabe zu großer Zahlen.Diese ist in dem Fall hilfreich, wenn
versehntlich Scannereingaben im falschen Eingabefeld landen. Zu bedenken ist,
dass die Einstellung für die ganze Vorgangserfassung gilt! Dann ist auch der
Zahlungsbetrag begrenzt

---

## Einrichtung des Frachtwesens

Einrichtung des Frachtwesens
Sie finden Details zu der Einrichtung und Wirkung des
Frachtwesens auch in
Preise / Konditionen
Frachten

---

## Einzelkalkulation

Einzelkalkulation
Die Einzelkalkulation ist eine Kalkulationsform mit
manuellen Eingreifmöglichkeiten.
Die Kalkulationsmaske hat folgendes Aussehen:

---

## Endbehandlung

Endbehandlung
Zum beenden der Kalkulation zu einem Artikel stehen
die folgenden Funktionen zur Verfügung:
Blättern auf einen anderen Artikel:
Es werden keine Daten gespeichert oder gelöscht,
sondern die Daten des ersten / vorhergehenden / nächsten / oder letzten
Datensatzes aufgerufen und kalkuliert.
Ende
Verlassen des Kalkulationsmoduls ohne Speichern oder
Löschen weiterer Daten
kalk. Preise übernehmen
Die Preise der Spalte ‚Neuer Preis‘ werden mit dem
angegebenen Zeitraum in ArtiListenpreis übernommen. Je nach SPA-Einstellung
(‚Kalkpr.Übern.: KalkListenPreis löschen‘) werden bei den auf KalkListenPreis
basierenden Varianten  die zugrundeliegenden Preise aus KakListenPreis
gelöscht.
Orig.-Preise übernehmen
Diese Funktion steht nur zur Verfügung, wenn der SPA
Preiskalk.: Original-Preise übernehmbar
eingeschaltet ist.
Die Preise der Spalte ‚Originalpreis‘ werden mit dem
unter ‚Neuer Preis‘ angegebenen Zeitraum in ArtiListenpreis übernommen. Je nach
SPA-Einstellung (‚Origpr.Übern.: KalkListenPreis löschen‘) werden bei den auf
KalkListenPreis basierenden Varianten  die zugrundeliegenden Preise aus
KakListenPreis gelöscht.
Akt.Preise übernehmen
Diese Funktion steht nur zur Verfügung, wenn der SPA
Preiskalk.: Aktuelle Preise übernehmbar
eingeschaltet ist.
Die Preise der Spalte ‚Aktueller Preis‘ werden mit dem
unter ‚Neuer Preis‘ angegebenen Zeitraum in ArtiListenpreis übernommen. Je nach
SPA-Einstellung (‚Aktpr.Übern.: KalkListenPreis löschen‘) werden bei den auf
KalkListenPreis basierenden Varianten  die zugrundeliegenden Preise aus
KakListenPreis gelöscht.
Die SPA’s ‚... KalkListenPreis löschen‘ verfügen über
die Einstellungen:
Nein
Ja
Mit Abfrage
Bevor die Preise gespeichert werden, werden die
Bedingungen des Kalkulationsschemas zur Prüfung auf die zu speichernden Preise
herangezogen. Sind diese verletzt, so wird in den Bearbeitungsmodus
zurückgeschaltet.

---

## Erfassungsparameter der Artikelerfassung

Erfassungsparameter der Artikelerfassung
Über Erfassungsparameter wird eine Anpassung des
Erfassungsablaufes ermöglicht:
Sofortige Preisfindung durchführen
Mit “Ja”, der üblichen Einstellung, erfolgt die
Preisfindung sofort. Wenn Preisfindung jedoch in Form einer Nachbepreisung
erfolgt, kann “Nein” sinnvoll sein.
Folgezeilen sofort rekalkulieren
Innerhalb des Preisfindungssystems können preisliche
Abhängigkeiten zwischen aufeinander folgenden Positionen bestehen. Mit “Ja”
werden die Folgezeilen bei Änderung der vorhergehenden Zeilen sofort neu
berechnet. Ansonsten geschieht dieses erst bei der Verbuchung mit dem
Mandantenserver.
Zusatztext 1 / 2 abfragen
Bis zu zwei zusätzliche auswertbare Informationen
können eingegeben werden, wenn diese Parameter auf “Ja” gesetzt werden.
Gebindemaske ohne Abfrage weiterschalten
Bei der Gebindeerfassung wird repetierend abgefragt
(Holzliste), so dass sich die Gesamtmenge schrittweise erhöht. Die Gesamtmenge
ist Preisgrundlage; die einzelnen Gebindezeilen werden wahlweise angedruckt.
Die Zusatztexte können formatiert werden:
Bezeichnung Zusatztext
In der Positionsmaske werden die Zusatztexte mit
dieser Bezeichnung angezeigt.
Zusatztext Länge
Die maximale Eingabegröße des Feldes.
Zusatztext mit F3- Auswahl
Hiermit kann man eine Auswahlbox (Item-Box) zur
überprüften Eingabe anbinden.
Feldname für Zusatz mit F3 Auswahl
Eingabe der Bezeichnung der gewünschten F3- Box.
Zusätzlich ist es möglich, den Zusatzfeldern eine
Formatierung mitzugeben. Dies geschieht innerhalb der Steuerungsparameter
(Vorgangsbearbeitung Warenpos.) unter „Autom. Formatierung für Zusatztext“.
Verschiebung der Warenerfassung

---

## Excel-Datei bearbeiten

Excel-Datei bearbeiten
Hauptmenü
Preise / Konditionen
Preiskalkulation tabellarisch
Individualpreiskalkulation Excel
Direktsprung
[PKXI]
Die Excel-Datei mit den Individualpreisen kann nun
bearbeitet werden. Da es eine größere Auswahl an Feldern gibt, die bearbeitet
werden können, werden diese im Folgenden aufgeschlüsselt.
Grundfunktionen
Diese Felder können editiert werden:
Feldname
Funktion
Ab
      Menge
Die
      Menge, ab der der Individualpreis gilt. Bei Veränderung des Feldes wird
      dem ausgewählten Individualpreis keine neue Menge zugewiesen, sondern ein
      neuer Individualpreis als Kopie des ausgewählten Preises mit der neuen
      Menge erstellt. Der ausgewählte Individualpreis mit seiner Menge bleibt
      bestehen.
Preis
Der
      Individualpreis, der ab der Menge
pro Mengeneinheit gilt. Dieser
      kann hier gepflegt werden.
Je
Faktor zwischen Individualpreis und
      Mengeneinheit. Dieser kann hier gepflegt werden.
Preis ab
Definiert den Beginn des
      Gültigkeitszeitraums für den Individualpreis. Bei Veränderung des Feldes
      wird dem ausgewählten Individualpreis kein neuer Beginn des
      Gültigkeitszeitraums zugewiesen, sondern ein neuer Individualpreis als
      Kopie des ausgewählten Preises mit dem neuen Datum erstellt.
Wichtig
: Unabhängig davon, bei welchem
      Individualpreis das Feld bearbeitet wird, ist stets auch der Datensatz mit
      der Menge 0 mit einzubeziehen. Das Feld kann auch als Teil der Vorbelegung
      (
Exportprofil einrichten
)
      gepflegt werden.
Preis bis
Definiert das Ende des
      Gültigkeitszeitraums für den Individualpreis. Dieses gilt für alle Mengen
      des Preises. Es kann hier oder als Teil der Vorbelegung (
Exportprofil einrichten
)
      gepflegt werden.
Löschen
Ein
      Individualpreis kann gelöscht werden. Hierfür muss dieses Feld auf „Ja“
      gesetzt werden.
Wichtig
: wenn die Menge 0 gelöscht wird,
      werden auch alle anderen Mengen im selben Gültigkeitszei
[...]


---

## Fehlerhafte Artikel

Fehlerhafte Artikel
Diese Anwendungsvariante steht auch bei
SPA-Einstellung „alle Artikel“ für den SPA „Preiskalkulation: zugelassene
Artikel“ zur Verfügung, um bzgl. der Preiskalkulation fehlerhafte
Artikeleinrichtungen feststellen zu können.
Die Auswahlliste entspricht der unter 1.6.1.1 mit dem
Unterschied, dass sie nicht mit der Referenzliste abgestimmt wird.
Mit der Funktion „zugeh. Artikel“ kann die unter
1.6.1.1 vorgestellte Maske aufgerufen werden.

---

## Frachtwesen

Frachtwesen
Sie finden Details zu der Einrichtung und Wirkung des
Frachtwesens auch in
Preise / Konditionen
Frachten

---

## Gelöschte Artikel entfernen (inkl. 1)

Gelöschte Artikel entfernen (inkl. 1)
Artikel mit einem Löschkennzeichen ungleich 0 werden
in folgenden Tabellen entfernt:
Artikel
artiladeartilink
artigebinde
baustpreis
artikeladdon
artilprprotokoll
artimerkmal
WAREOANALYSE
Zuvor werden folgende Tabellen überprüft, ob der
gelöschte Artikel entfernt werden darf:
Warenbewegung
v_posiware
artibestauspr
artibestand
Artisummextra
artisummen
artibestandsumme
lagerplatzsummen
artibewertung
artibewerttempo
artibewertfibu
artiwarenkonto
inventurbestand
invbestauspr
inventurbelegpartie
inventurbewpreise
arbeitsbuchungen
partiepreis
partieartikel
v_posipartie
partiebestand
kontrauswarti
kontraktartikel
ktrdisposition
baustbewegung
baustartikel
v_posibaustelle
baustartimensumm
leergrupartilink
leergutstamm
leergut
leergutkonto
rohsorteartikel
rohsortekosten
v_rohwarenachverg
feldanerkennung
saatgutbearbeitung
saatgutsaatentnahme
vermehrungsvertrag
anerkennungschlagposition
vorgvorerfposit
amic_edeart
artikelmaskedaten
bedarf
bepool
reisestationartikel
WARENBUCH
WARENBUCHAKTIV
INVENTURBELEG
BAUSTARTIMENGE
MARKTSTANDANGEBOTE
SAP_BUSINESSCONNECTOR_POSITION
Artikelstämme mit einem Löschkennzeichen ungleich 0
werden in folgenden Tabellen entfernt:
Artikelstamm
artiherstpreis
artigefahrklasse
artistamgebinde
artikelinfoseite
artilieferant
artisuchbegr
artisekundschl
artikeltext
artiherstell
artiauspgebinde
wagruspezartikel
artiintrastat
artizusammensetz
artikelstammaddon
artikundarnr
artisekundschl
Zuvor werden folgende Tabellen überprüft, ob der
gelöschte Artikelstamm entfernt werden darf:
artiauspraeg
artikel
v_posiartiauspr
invbestauspr
ezg_artikelliste
partiebestand
ktrdisposition
WARENBEWEGUNG
ARTIBESTAUSPR
AMIC_ARTILIEFERANT
Beim Entfernen der gelöschten Artikel werden
automatisch die
Vorgänge Ware
mit gelöscht.

---

## Gruppenzuordnung:

Gruppenzuordnung:
Diverse und individuelle Gruppen für Preise, Rabatt,
Abschlag, Fracht usw.

---

## Haupt-Bereich

Haupt-Bereich
Der Hauptbereich der Maske zerfällt in  3
Teile:
Aktueller Preis
Neuer Preis
Originalpreis
Gemeinsam für alle drei Bereiche gelten die
Spalten
Nr = Nummer der Preisliste
Bezeichnung = Bezeichnung der Preisliste
Währungstext
Preiseinheit (Preisfaktor)
Kurztext der Preismengeneinheit.
Währen sich die ersten drei aus der
Preislistendefinition ergeben, werden für Preiseinheit und Preis-Mengeneinheit
immer die Angaben zu den Preisen der Spalte ‚Aktueller Preis‘
herangezogen.

---

## Hinzufügen (Preiskalkulation)

Hinzufügen (Preiskalkulation)
Diese Funktion ist für Bediener mit
Administrator-Status reserviert. Es wird die erwähnte Maske genutzt, siehe unter
1.6.1.1.2

---

## ImportVorgZuAbDef

ImportVorgZuAbDef
Definition Zu-Abschläge
In dieser Relation werden Zu- und definiert
Feld
Bedeutung
IVZ_Guid
Guid
      der Definition
IVZ_Typ
1 =
      Rabatt,
2 =
      ZuAbschlag
3 =
      Fracht
IVZ_Nummer
0
IVZ_Bezeich
Bezeichnung
IVZ_Formel
Formel
IVZ_EKZ_Nummer
Erlöskennziffer
IVZ_KostStellNummer
Kostenstellennummer
IVZ_KSTRNummmer
Kostenträgernummer
IVZ_FraFormNummer
Frachtformel (bei
      Fracht)
IVZ_FraZoneNummer
Frachtzone (bei Fracht)
IVZ_Entfern
Entfernung (bei Fracht)
IVZ_Preiswirksam
Wirkt der ZuAbschlag auf den Wert
      der Warenposition (0) oder auf den Preis (1)
IVZ_Prozent
Prozentualer Anteil
IVZ_Preis
Preis
IVZ_PrEinh
Preiseinheit
IVZ_BezMenge
Bezugsmenge
IVZ:BezWert
Bezugswert
IVZ_Netto
Nettowert des
      ZuAbschlags
IVZ_SkoKennz
Skontierfähig
0 –
      wie Ware
1 –
      Nein
2 -
      Ja
IVZ_InZeile
InZeile-Berechnung
IVZ_Inclusiv
Kalkulatorisch (bei
      Frachten)
IVZ_ErfolglosWeiter
Wenn
      ein Wert nicht gesetzt werden konnte, soll abgebrochen (0) oder
      fortgefahren (1) werden.
IVZ_AutoOverride
Überschreibt (1) die vorhandenen
      automatischen ZuAbschläge und Rabatte

---

## Info-Bereiche

Info-Bereiche
In der oberen Zeile werden nähere Angaben zum
ausgewählten Artikel angezeigt:
Artikelnummer und Bezeichnung
Gebinde:
Hier wird die Bezeichnung einer der Mengeneinheiten
aus der Mengeneinheitsgruppe des Artikelstamms des Artikels gezeigt. Der SPA ‚
Preiskalkulation: angezeigte Mengeneinheit‘ Bestimmt, welche Einheit der
Mengeneinheitsgruppe gezogen wird.
VK-/EK-Matrix
Hier werden die VK- und EK-Preismatrixnummern des
ausgewählten Artikels zur Info angezeigt.
Im unteren linken Kasten der Maske werden sämtliche
zugehörige Artikel per Artikel- und Lagernummer aufgelistet, also diejenigen,
die die VK-Listenpreisgruppe des ausgewählten Artikels selbst auch als
VK-Listenpreisgruppe eingetragen haben. Da alle diese Artikel auf die gleiche
Listenpreisgruppe zeigen, gelten die hier neu kalkulierten Preise auch für alle
diese Artikel, gefiltert durch die jeweiligen Preismatrix-Vereinbarungen.

---

## Kalkulation

Kalkulation
Die Kalkulationsformeln der Gruppe 0 des zugeh.
Schemas werden aufgerufen:
bei Blättern zu einem neuen Artikel
bei Blättern auf einen anderen Zeitraum der Spalte
‚Aktuelle Preise‘
(Die Werte für ‚alter Preis‘ in Formeln ändern
sich)
Bei Änderung der Datumsgrenzen des
Neu-Preis-Zeitraumes
(Die Steuersätze könnten sich
ändern)
Wird ein Preis der Spalte ‚Neuer Preis‘ manuell
überschrieben, ( dieses ist nur möglich, wenn die Preisliste über keine
Korrektursperre verfügt), so werden anschließend die Kalkulationsformeln des
Schemas mit der Gruppe ausgeführt (sofern vorhanden), deren Gruppennummer gleich
der Preislistennummer des geänderten Preises ist.
In beiden Fällen wird das Ergebnis dem Betrage nach
‚kaufmännisch‘ entsprechend der Angabe im Feld ‚Rundungseinheiten‘ der
Preislistenbezeichnung auf ein Vielfaches dieses Wertes gerundet.
Ist dieser z.B. 0,5  so wird
bis x,24 auf x,00
bis x,74 auf x,50
darüber auf x+1,00
gerundet.
Grundsätzlich werden alle Werte für Preisvariablen der
Formeln während der Ausführung vor Übergabe an den Formel-Interpreter in die
Formel-Zielpreis-Einheiten (Preiseinheit und Preismengeneinheit)
umgerechnet.
Dabei werden die Werte der Formelvariablen Nx (neuer
Preis x) den Werten aus ‚Neuer Preis‘, diejenigen der Formelvariablen Ax (alter
Preis x) den Werten aus ‚Aktueller Preis‘ des dort gewählten Zeitraumes
entnommen.
Kalkuliert werden nur die in der Spalte ‚Neuer Preis‘
sichtbaren Preislisten (Sortierung > 0);
Sind in Formeln Bezüge ‚alter Preis‘ auf Preislisten
vorhanden, die zwar nicht auf der Maske erscheinen (Sortierung = 0), aber
dennoch mit Preisen für die Listenpreisgruppe existieren, so werden diese
gezogen und können somit ‚verdeckt‘ in die Kalkulation einfließen.
Es werden alle VK- und EK.Preise der zum Artikel
gehörigen VK- und EK- Listenpreisgruppen eingelesen und ggf. nach Kalkulation
auch gespeichert. Daher kann es vorkommen, dass mehr Preise auf der
Kalkulationsmaske erscheinen, als aus EK- u
[...]


---

## Barcode-Etiketten

Barcode-Etiketten
Es besteht die Möglichkeit, an der Referenz-ERP-Kasse über
einen Strichcode neben der Artikelerkennung auch den Preis sowie die Menge
direkt ins Referenz-ERP-System zu übernehmen.
Solche Barcodes werden „InStoreBarcodes“ genannt und
sind ausschließlich zur hausinternen Verwendung gedacht.
Anwendungsbeispiele:
•
Etikett einer Waage mit Artikelnummer und Gewicht
•
Etikett eines Warenausgabeautomaten
•
Barcode eines Warenlieferscheins
Der Aufbau eins solchen Etiketts könnte so aussehen:
Position
Beschreibung
1 -
      2
21
      (Konstante, die dem System mitteilt, dass hier eine Sonderbehandlung
      erfolgen soll; nämlich, dass es sich um einen Waagenartikel
      handelt.)
3 –
      7
Artikelnummer (wie in den Stammdaten
      hinterlegt)
8 –
      12
Gesamtpreis   (Hier steht
      der durch die Waage ermittelte Preis drin, der durch Referenz-ERP übernommen
      werden soll.)
13
Prüfziffer
Voraussetzungen:
Einige Voraussetzungen müssen jedoch alle
erfüllen:
•
Der Barcode darf nicht als EAN-Barcode in der Datenbank enthalten sein.
Dies sollte in der Regel der Fall sein, wenn der InStoreBarcode mit der Ziffer 2
beginnt. Es findet keine programmatische Prüfung auf Kollisionen statt.
•
Die Artikelnummer im Barcode muss im System pro Lager eindeutig sein
(d.h. in unserem Beispiel müssen alle Artikelnummern von Barcodeartikeln
5-stellig sein)
•
Der EAN-Code für Nicht-In-Store-Artikel muss im System eindeutig sein (im
Artikelstamm)
Steuerparameter:
Der Steuerparameter
472 - Datenübernahme an Kasse aus Etikett
muss
eingeschaltet sein.
Soll eine gegebene Mengeneinheit auch als
Preismengeneinheit übernommen werden, so muss der Steuerparameter
772 –
Preismengeneinheit aus Mengeneinheit übernehmen
gesetzt sein.

---

## Kennziffern für Ergänzende Angaben

Kennziffern für Ergänzende Angaben
Ab 2021 sind neue Kennziffern für Ergänzende Angaben
zu Minderungen nach§ 17 Abs. 1 Sätze 1 und 2 i.V.m. Abs. 2 Nr. 1 Satz 1 UstG
hinzugekommen.
Hat sich die Bemessungsgrundlage für den
Vorsteuerabzug bei dem Unternehmer, an den dieser Umsatz ausgeführt wurde,
geändert, ist der Vorsteuerabzug nach § 17 Abs. 1 Satz 2 UStG zu berichtigen.
Erfolgt die Änderung nach § 17 Abs. 1 Satz 2 i. V. m. Abs. 2 Nr. 1 Satz 1 UStG,
weil das vereinbarte Entgelt für einen steuerpflichtigen Umsatz uneinbringlich
geworden ist, ist die Minderung der abziehbaren Vorsteuerbeträge zusätzlich im
Vordruckmuster USt 1 A in Zeile 74 (Kz 37) einzutragen.
Um diese Kennziffern für Elster und das
Umsatzsteuervoranmeldungsformular zu versorgen, müssen neue
Auswertungspositionen, neue Steuerschlüssel und zusätzliche Steuersätze
eingerichtet werden.
Schritt 1: Auswertungspositionen
Es müssen zwei Auswertungspositionen angelegt werden,
eine für Kennziffer 50 und eine für Kennziffer 37. Dazu gibt man den
Direktsprung
[FIAWP]
ein und gelangt so
in die Anwendung zur Pflege der Auswertungspositionen.
Vorgehen:
•
Sachkonto mit der Funktion
F8
für
„Neu“
-Erfassung aufrufen
•
Es müssen mindestens die Felder Nummer und
für die Kennziffer 50 das
Feld Bemessungsgrundlage und
für die Kennziffer 37 das Feld Steuer
eingetragen werden
•
Anschließend die Daten mit
F9
oder
„Speichern“
übernehmen.
Kennziffer 50
Da nur die Minderung der Bemessungsgrundlage relevant
ist, muss das Feld hinter Steuer leer bleiben.
Kennziffer 37
Im Bereich Vorsteuer wird die Bemessungsgrundlage
nicht benötigt. Dieses Feld bleibt also leer.
Schritt 2: Zusätzliche Steuerschlüssel anlegen
Dazu ruft man den Direktsprung
[STS]
auf und
geht am besten direkt in die Auswahlliste für
Steuerschlüssel
F7
. Hier ruft
man den Pfleger mit mit
Neu
F8
auf und vergibt eine neue
Steuerschlüssel-Nummer und eine dazu passende Bezeichnung. Anschließend
speichert man die Änderungen mit der Funktion
„Speiche
[...]


---

## Manuelle Rabatte

Manuelle Rabatte
Rabatte können manuell im Anschluss an die Erfassung
einer Warenposition erfasst werden. Siehe dazu auch
Rabatte in
den Erfassungsmöglichkeiten des Vorgangs
.
Nummer oder Text
Auswahl eines
Rabattsatzes
. Wählen Sie hier den für diesen Rabatt
gültigen Satz aus. 0 ist die Standardeinstellung für einen komplett manuell
erfassten Rabatt.
Rabattgruppe
Wird nur angezeigt – die Rabattgruppe des Artikels
EKZ-Nummer
Erlöskennziffer auf die der Rabatt gebucht werden soll
– 0 = die gleiche Erlöskennziffer wie die zugehörige Warenposition.
Kostenstelle
Hier kann eine von der Warenposition abweichende
Kostenstellennummer für den Rabatt angegeben werden.
0 = es wird die
Kostenstellennummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenstellen-Lizenz
aktiviert ist.
Kostenträger
Hier kann eine von der Warenposition abweichende
Kostenträgernummer für den Rabatt angegeben werden.
0 = es wird die
Kostenträgernummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenträgerrechnung
angeschlossen
aktiviert ist.
Kostenobjekt
Hier kann eine von der Warenposition abweichende
Kostenobjektnummer für den Rabatt angegeben werden.
0 = es wird die
Kostenobjektnummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenobjekt-Lizenz
aktiviert
ist.
Die Bezeichnung dieses Feldes ist in der
OPTION
Kostenobjekt_Label
einrichtbar!
Wirkt auf Preis
Ja – Rabatt wirkt auf den Einzelpreis des Artikels pro
Mengeneinheit und wird dann erst mit der Menge multipliziert
Formel
Zu-Abschlagsformel siehe auch
in den automatischen Rabatten
Prozentsatz
Prozentsatz des Rabattes (bei prozentualen
Rabatten)
Preis/Satz
Rabattbetrag (bei Rabattsatz, der nicht prozentual
ist)
Preiseinheit
Ebendies
Bezugsmenge
Ebendies
Bezugswert
Wert auf den sich der Rabatt beziehen wird
Betrag
Wird nur angezeigt: Rabattbetrag
Steuer

[...]


---

## Marktpreiszuordnung

Marktpreiszuordnung
Über eine Exceldatei kann die Marktpreiszuordnung in
das System übernommen werden.

---

## Marktpreispflege

Marktpreispflege
In der Abteilung Marktpreise können die Marktpreise
den einzelnen Artikeln zugeordnet werden, und zwar auf Basis eines Stichtages
und dann für die nächsten 12 Monate. Da eine Eingabe über ein Excel
Tabellenblatt in diesem Falle am einfachsten ist, wird hier direkt der
Excelimport aufgerufen. Über den Pflegeknopf kann bequem das Excelblatt
angepasst werden und per einfachem Mausklick dann sofort wieder eingespielt
werden.

---

## Nachkalkulation Rohertrag

Nachkalkulation Rohertrag
Für ausgewählte Vorgänge kann hiermit jederzeit eine
Nachkalkulation des Rohertrages durchgeführt werden, wobei einstellbar ist, wie
die Bewertung erfolgen soll:
Dies erfolgt in der Zeile „Bewertungsmethode“, wobei
die Belegung aus dem Artikel als Standardeinstellung vorbelegt ist. Auf diese
Art ist es dann z.B. möglich, einen Auftrag mit aktuellen EK-Preisen zu
bewerten. Als Ergebnis wird folgende Darstellung ausgegeben:

---

## Neue Preise und Übermittlung im Protokoll prüfen

Neue Preise und Übermittlung im Protokoll prüfen
Um die neuen Preise und die Übermittlung zu
überprüfen, wie folgt vorgehen:
1.
Wählen Sie in der Auswahlliste die Variante
Preiskalkulation
Protokoll
aus.
2.
Prüfen Sie in der Liste die Preise oder ggf. die Fehlermeldungen, die
aufgetreten sind.

---

## Neuer Preis

Neuer Preis
Im Bereich ‚Neuer Preis‘ werden die Preise der Spalte
„Originalpreis“, auf die bereits die Formeln der Gruppe 0 des
Kalkulationsschemas angewendet wurden, angezeigt, ggf. nach Umrechnung auf die
Preiseinheit und Preismengeneinheit des Preises der Spalte ‚Aktueller
Preis‘.

---

## Nicht referenzierte Artikel

Nicht referenzierte Artikel
Hier wird nach Angabe des  Auswahlbereiches
Artikelnummer
von...    bis...
Lagernummer
von...    bis...
Eine Liste Aufgebaut, in der alle Artikel des
gewählten Bereiches gelistet werden, die eine ListenpreisgruppeVK > 0, ein
Kalkulationsschema > 0 haben, keine Grundartikel sind und deren
ListenpreisgruppeVK sich nicht in der Referenzliste befinden.
Zu jedem Artikel wird angezeigt:
Die Artikelnummer
Die Lagernummer
Die zugehörige Artikelstammnummer
Die Listenpreisgruppennummer VK
Die Listenpreisgruppennummer EK
Die Anzahl der Artikel mit derselben
VK-Listenpreisgruppennummer, diese umfasst auch die korrespondierenden Artikel
außerhalb des Selektionsbereiches
Einen Hinweis auf evtl. bezgl. der Preiskalkulation
fehlerhaft eingerichtete Artikel (Fehler: ja/nein)
Der Fehlerhinweis ist genau dann ‚ja’, wenn
einer der folgenden Fälle besteht:
es gibt Artikel, die zwar die gleiche
VK-Listenpreisgruppennummer aber eine andere EK-Listenpreisgruppennummer als der
gelistete Artikel haben und die SPA-Einstellung für ‚ Preiskalk.:
EK-Listenpreisgruppen‘ ist ‚ Lesen, Kalkul., KEINE SPEICHERUNG‘ oder ‚ volle
Berücksichtigung‘.
es gibt Artikel, die zwar die gleiche
EK-Listenpreisgruppennummer aber eine andere VK-Listenpreisgruppennummer als der
gelistete Artikel haben, es sei denn, die  EK- Listenpreisgruppennummer ist
0 oder die SPA-Einstellung für ‚‚ Preiskalk.: EK-Listenpreisgruppen‘ ist ‚keine
Berücksichtigung‘
es gibt Artikel, die zwar die gleiche
VK-Listenpreisgruppennummer aber ein anderes Kalkulationsschema als der
gelistete Artikel haben.
Derartige Einrichtungen würden insbesondere bei der
Preiskalkulation zu zufälligen Ergebnissen führen, da ja ein und dieselben
Preise je nach Artikelauswahl entweder aus anderen EK-Preisen oder mit anderen
Formeln berechnet würden.
In dieser Auswahllistenvariante gibt es, wenn Einträge
gelistet sind, zwei wesentliche Funktionen:
zugeh. Artikel
* Hinzufügen
Die zweite Funktion steht
[...]


---

## Original-Preis

Original-Preis
Im Bereich ‚Originalpreis‘ werden die ggf. auf
Preiseinheit und Preismengeneinheit umgerechneten Originalpreise angezeigt.
Dieses sind, je nach Variante, die Preise aus Kalklistenpreis bzw. die zum
Zeitraum mit aktuellem Tagesdatum gehörigen Preise aus ArtiListenPreis.

---

## Partien löschen

Partien löschen
Es dürfen keine Daten in PARTIEBEWEGUNG vorhanden
sein, sonst wird nicht gelöscht!
Es werden die Daten in folgenden Tabellen
gelöscht:
PartieStamm
PartieStammAddon
PartieGruppe
PartieMengeZR
PartieArtikel
PartieKontrLink
PartieArtiMenge
PartiePreisZR
PartiePreis
PartieWaGruList
PartieKundListe
PartieLiefListe
StreckenErfassungPartieverteilung
SiloPartie
PartieAnalyse
PartieQualitaet
SaatgutSaatentnahme
PartieMaskeDaten
PartieArtiMenIst

---

## Per Ref.Liste und ArtiListenPreis

Per Ref.Liste und ArtiListenPreis
Hier können Artikel mit folgender Bereichsauswahl
selektiert werden:
Artikelnummer:
Auswahl von Unter- und Obergrenze der zu
berücksichtigenden Artikelnummern.
ACHTUNG: Die Artikelnummer ist alphanumerisch, d.h.
die Auswahl ist lexikographisch!
Artikel gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Gültigkeits-AbDatum im angegebenen Bereich liegt!
Warengruppe:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Warengruppe im angegebenen Bereich liegt!
Lagernummer:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Lagernummer im angegebenen Bereich liegt!
Zusätzliche Einschränkungen:
Es werden nur Artikel in die Auswahlliste übernommen,
deren VK-Listenpreisgruppe sich in der Referenzliste befinden.
Es werden nur Artikel in die Auswahlliste übernommen,
die über eine Kalkulationsschemanummer größer 0 verfügen.
Es werden nur Artikel in die Auswahlliste übernommen,
die keine Grundartikel sind.
Es werden nur Artikel in die Auswahlliste übernommen,
deren Kalkulationsschema als Kalkulationsgrundlage die Relation ArtiListenpreis
verwendet.
Die Auswahlliste zeigt für jeden Artikel folgende
Werte:
Befinden sich Artikel in der Auswahlliste, so können
diese bzw. die hierfür markierten Artikel kalkuliert werden. Hierfür stehen zwei
Funktionen zur Verfügung:
Einzelkalkulation      F5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: manuelle Kalkulation erlaubt‘
mit dem Wert ‚Ja‘ eingestellt ist.
Stapelkalkulation     SF5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: Stapelkalkulation erlaubt ‘
mit dem Wert ‚Ja‘ eingestellt ist.

---

## Per Ref.Liste und KalkListenPreis

Per Ref.Liste und KalkListenPreis
Hier können Artikel mit folgender Bereichsauswahl
selektiert werden:
Artikelnummer:
Auswahl von Unter- und Obergrenze der zu
berücksichtigenden Artikelnummern.
ACHTUNG: Die Artikelnummer ist alphanumerisch, d.h.
die Auswahl ist lexikographisch!
Artikel gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Gültigkeits-AbDatum im angegebenen Bereich liegt!
Kalk.Pr. gültig ab:
Es werden nur Artikel in die Auswahlliste übernommen,
zu deren VK-Listenpreisgruppe zur eigenen Filialnummer Preise in der Relation
KalkListenPreis vorhanden sind, deren AbDatum im angegebenen Bereich liegen!
Warengruppe:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Warengruppe im angegebenen Bereich liegt!
Lagernummer:
Es werden nur Artikel in die Auswahlliste übernommen,
deren Lagernummer im angegebenen Bereich liegt!
Zusätzliche Einschränkungen:
Es werden nur Artikel in die Auswahlliste übernommen,
deren VK-Listenpreisgruppe sich in der Referenzliste befinden.
Es werden nur Artikel in die Auswahlliste übernommen,
zu deren VK-Listenpreisgruppe zur eigenen Filialnummer in der Relation
KalkListenPreis mindestens ein Preis vorhanden ist.
Es werden nur Artikel in die Auswahlliste übernommen,
die über eine Kalkulationsschemanummer größer 0 verfügen.
Es werden nur Artikel in die Auswahlliste übernommen,
die keine Grundartikel sind.
Es werden nur Artikel in die Auswahlliste übernommen,
deren Kalkulationsschema als Kalkulationsgrundlage die Relation KalkListenpreis
verwendet.
Die Auswahlliste zeigt für jeden Artikel folgende
Werte:
Befinden sich Artikel in der Auswahlliste, so können
diese bzw. die hierfür markierten Artikel kalkuliert werden. Hierfür stehen zwei
Funktionen zur Verfügung:
Einzelkalkulation      F5
Diese Funktion ist nur dann verfügbar, wenn der
SPA
‚ Preiskalk.: manuelle Kalkulation erlaubt‘
mit dem Wert ‚Ja‘ eingestellt ist.
Stapelkalkulation     SF5
Diese Funktion ist nur dann verfügbar, wenn der

[...]


---

## Position

Position
Feld
Beschreibung
Datenladeroutine
Bestellte Menge abfragen
Gebindefaktor 1 abfragen
Gebindefaktor 2
Gebindemenge
Preis ME
Preis abfragen
Preis pro
Zusatz 1 abfragen
Zusatz 2 abfragen
Addonfeldname für Auf
Doppelerfassungsartik
IB-Artikel in Menge
Artikel in MSA J/N/F
Druckauswahlfenster
Druckvorbelegung
Artikelnummer verstecken
Bestellte Menge anz
Letzter VK anz.
Offene Belegeprozedur
ME
      anzeigen
MENR
      Verhalten
IB
      Zusatz2
Ohne
      Preise
Leergut
Wertartikel
Ltz.
      VK Prozedur
Partieitembox
Entryprozedur Preisbezug
Hier
      wird der Name einer Prozedur angegeben, die anhand der gegebenen Werte
      eine Vorbelegung für den Preisbezug errechnet (sofern
      relevant)
Beispiel:
CREATE PROCEDURE p_mas_testteildispo(
in in_wabewid integer,
in
      in_DestKlassNummer integer,
in
      in_DestUKlassNummer integer,
in
      in_MengeGesamt numeric(15,4),
in in_MengeDisp
      numeric(15,4),
in in_MengeCurr
      numeric(15,4),
in in_MengeRest
      numeric(15,4),
in
      in_PreisBezugGesamt numeric(15,4),
in
      in_PreisBezugDisp numeric(15,4),
in
      in_PreisBezugCurr numeric(15,4),
in in_PreisBezugRest numeric(15,4) )
result( Result
      numeric(15,4) )
begin
select
      in_PreisBezugCurr  from dummy
end
Als
      Vorbelegung bekommt die Prozedur über eine Dreisatzberechnung den
      Wert  „in_PreisBezugCurr„  gegeben.
Ltz.
      VK Bezeichnung
Folgeartikel Prozedur
Wertberechnungsprozedur
Knopfbelegung D1/D1

---

## Preisfaktor

Preisfaktor
Per EPA kann noch der Preisfaktor eingebbar gemacht
werden, normalerweise zieht das System den Preisfaktor aus dem Artikel (stamm),
hier handelt es sich um den „Default Preisfaktor“

---

## Preis Info System

Preis Info System
Hauptmenü
Preise/Konditionen
Preise
Preis Info System
oder Direktsprung
[PIN]
Das Preis Info System zeigt für einen Musterkunden und
für bis zu 4 Referenz-/Vergleichskunden die Preise eines Artikels an.
Die Auswahl eines Musterkunden erfolgt im Feld
(Muster-)Kunde mit F3 oder manuell.
Die Daten des Kunden wie z.B.
Zahlungsart, Preisklasse und Versandart werden zunächst übernommen können aber
geändert werden.
Danach wählt man den Artikel aus für den man die Preise der
Kunden vergleichen möchte.
Vergleichskunden können mit der Funktion
Vergleichskunden ändern F10 angegeben werden. Die angegebenen Vergleichskunden
werden für den Bediener gespeichert, so dass sie für den nächsten Start des
Preis Info System schon eingegeben sind.
Sie können jederzeit mit einem Klick
in das Feld mit der Kundennummer, einer Auswahl mit F3 oder manuelle Eingabe und
danach einer Bestätigung durch die Enter-Taste geändert werden.
Die Knöpfe über den Spalten der Kunden (mit dem
entsprechenden Namen) sind zum Aktualisieren der Werte.
Den zugehörigen Einrichterparameter (Vergl.kunden nach
Artikel-Eingabe autom. anzeigen) findet man
hier.
Dieser ist vorbelegt mit Ja. So
werden für die gespeicherten Vergleichskunden eines Bedieners gleich die Preise
mit angezeigt.

---

## Preiskalkulation durchführen

Preiskalkulation durchführen

---

## Preiskalkulation per Auswahlliste

Preiskalkulation per Auswahlliste

---

## Preis

Preis
Die Eingabe des Preises zieht ggf. noch eine Nachfrage
nach sich, ob dieser Preis auch in dem Artikelstapel fest hinterlegt werden
soll.

---

## Preis 1 bis 4

Preis 1 bis 4
Die Preise 1 bis 4 werden hier festgelegt, innerhalb
der Schnellkorrektur können dann diese Preise zur Anzeige gebracht werden, und
zwar wird per EPA festgelegt, welcher Preis zu welcher / welchen Preisklassen
gehört (s.u.). Die Preise können auch direkt in den Artikel zurück geschrieben
werden, wenn das Preisübernahmefeld angeschaltet ist.

---

## Preisübernahme

Preisübernahme
Die Preisübernahme in den Artikel wird entweder
ausgeschaltet, oder sie kann hier auf Listenpreisübernahme gesetzt
werden.

---

## Preise - Preisfindungseinstellungen pro Vorgang

Preise
- Preisfindungseinstellungen pro Vorgang
Auf der Registerkarte „Preisfindung“ stehen folgende
Felder zur Verfügung
Feld
Beschreibung
Fixe
      Preisliste
Steht hier eine gültige
      Preislistennummer, wird die zugehörige Preisliste  zur
      Preisermittlung herangezogen.
Fixe
      Steuergruppe
---- nicht mehr verwenden
      ----
Brutto-Vorgänge
Vorbelegung  bei ‚Ja‘ als
      Bruttobeleg
Preis laut Bewertung
Bei
      der Preisvorbelegung per Bewertungspreis ( zum Beispiel bei
      Lagerumbuchungen) gibt man hier das Verfahren zur Ermittlung des
      Bewertungspreises ein.
Preisfindungsprozedur
Der
      Name Datenbankprozedur, die zur Preisermittlung aufgerufen werden
      soll.  Ein Beispiel für die (möglichen) Parameterübergaben findet
      sich in der Datenbank in der Prozedur ‚Amic_MusterPreisAusDatenbank“. Der
      Prozedur werden diverse Informationen übergeben, wobei einige Parameter
      nur bei bestimmten Vorgangsklassen sinnvoll belegt sind. Die Rückgabe der
      Werte erfolgt über eine (optionale) Ergebnismenge. Liefert die Prozedur
      keine Ergebnismenge, wird die übliche Preisfindung aktiviert. Die
      Ergebnismenge muss mindestens folgende Datenbankfelder enthalten:
Preis numeric(15,6) // der Preis (
      bei Währung in der Währung)
Einheit numeric(15,4) //
      Einheit = per 1, per 100 oder ähnlich
ME_Nummer integer) //
      Mengeneinheit des Preises
Die
      Prozedur kann für alle Vorgangsklassen außer Rohware hinterlegt
      werden.
Aufrufebene
Preislimit
      berücksichtigen
Hier
      kann angegeben werden, ob das Preislimit aus dem Artikelstamm bei der
      Eingabe eines Preises bei der Erfassung geprüft werden soll.

---

## Preiskalkulations-Schema

Preiskalkulations-Schema
Mit dem Modul „Preiskalkulationsschema“ können
Kalkulationsschemata für das Preiskalkulationsmodul angelegt und gepflegt
werden.
Ein Schema besteht aus
•
einer dem Schema eindeutig zugeordneten Schemanummer
•
einer Bezeichnung des Schemas
•
der Angabe der Kalkulationsgrundlage
•
optional die Angabe eines Makros mit Prozeduren zur Kalkulation
•
einer Sammlung von Preisberechnungsformeln
•
einer Sammlung von Preisbezugsbedingungen.
Der Wert der Kalkulationsgrundlage gibt an, auf
welcher Basis Preise kalkuliert werden sollen.
0: Grundpreise aus <KALKLISTENPREIS> zu letztem
Zeitraum
1: Zeitraum manuell, Grundpreise=Listenpreise des
vorherigen Zeitraumes
Ist dieser Wert 0, so werden bei der Kalkulation die
Preise der Spalte „Originalpreis“ aus der Relation „KalkListenPreis“ genommen.
Insbesondere können dann auch Artikel kalkuliert werden, die über Preise in
dieser Relation verfügen.
Ist der Wert hingegen 1, so entsprechen bei der
Kalkulation die Preise der Spalte „Originalpreis“ den  aktuellen
Listenpreisen aus „ArtiListenPreis“.
Soll für alle Kalkulationsschemata die gleiche
Kalkulationsgrundlage gelten, so kann der Wert auch per SPA eingestellt werden.
Dann erscheint das Feld nicht mehr auf dieser Maske.
SPA-Bezeichnung: „Preiskalkulation:
Kalkulationsgrundlage“ in der Gruppe „Preisfindung“
Werte:  0: Grundpreise aus
<KALKLISTENPREIS> zu letztem Zeitraum
1: Zeitraum manuell, Grundpreise=Listenpreise des vorherigen Zeitraumes
2: In Kalkulationsschema anzugeben
Die Angabe eines Makro-Namens ist optional. Per SPA
kann dieses Feld der Maske unterdrückt werden, wenn generell keine Makros bei
der Preiskalkulation verwendet werden sollen.
SPA-Bezeichnung: „Preiskalkulation:
Makro-Unterstützung“
Werte:  0: Nein
1: Ja
Wird hier hingegen ein Makroname angegeben, so muss
der entsprechende Makro existieren.
Ein solcher Makro muss dann zu mindestens über die
Prozedur
procedure PreisKalkInit(
artikelid,lpgvk,lpgek,pmvk,pmek,ksnr : intege
[...]


---

## Preiskonditionen (EPA PREISKOND)

Preiskonditionen (EPA PREISKOND)
Bezeichnung
Standardwert
Erklärung
Ab-Datum bei
      Individualpreisneuanlage
Anfangsdatum des laufenden
      Geschäftsjahres
Mit
      welchem Datum soll das Gültig-Ab Eingabefeld vorbelegt werden. Weitere
      Auswahlmöglichkeiten können mit F3 abgerufen werden.
Bis-Datum bei
      Individualpreisneuanlage
Enddatum des laufenden
      Geschäftsjahres
Mit
      welchem Datum soll das Gültig-Bis Eingabefeld vorbelegt
      werden.
Anzahl Tage (Bis-Datum = Ab-Datum +
      Tage)
30
Insofern die Bestimmung des
      Bis-Datums auf „Ab-Datum plus Anzahl Tage“ gesetzt wurde, wird die hier
      erfasste Ganzzahl zum Ab-Datum addiert, um das Bis-Datum zu
      ermitteln.
Fixes Bis-Datum bei
      Individualpreisneuanlage
Keine Vorbelegung
Insofern die Bestimmung des
      Bis-Datums auf „Fixes Bis-Datum“ gesetzt wurde, wird das hier erfasste
      Datum zum Bis-Datum.
Preisreihenfolge absteigend nach
      Ab-Datum sortiert.
Nein
Bei
      „Ja“ werden die Preisinformationen absteigend nach dem Ab-Datum sortiert,
      das am weitesten in der Zukunft liegende Datum zuerst. Bei „Nein“ erfolgt
      die Sortierung aufsteigend, das früheste Ab-Datum zuerst.
Vorbelegung Individuelle Fracht bei
      Individualpreis-Neuanlage (jeweils für EINKAUF und VERKAUF)
Nein
Bei
      „Nein“ wird für die individuellen Preise per Vorbelegung keine
      individuelle Fracht berechnet.
Vorbelegung. Individueller Rabatt
      bei Individualpreis-Neuanlage (jeweils für EINKAUF und
      VERKAUF)
Nein
Bei
      „Nein“ wird für die individuellen Preise per Vorbelegung kein
      individueller Rabatt berechnet.
Vorbelegung Individuelle Verpackung
      bei Individual-Preisneuanlage (jeweils für EINKAUF und
      VERKAUF)
Nein
Bei
      „Nein“ wird für die individuellen Preise per Vorbelegung keine
      individuelle Verpackung berechnet.
Vorbelegung Individueller
      Zu-/Abschlag bei Individual-Preisneuanlage (jeweils für EINKA
[...]


---

## Preismengeneinheit

Preismengeneinheit
Die Artikelpreismengeneinheit kann auf diesem
Eingabebildschirm festgelegt werden, hier ist vorstellbar, dass der Artikel in
kg geführt wird, der Preis sich aber auf eine Steige oder einen Kolli bezieht.

---

## Preispflege

Preispflege
Eine tabellenorientierte Preispflege erlaubt es
schnell und einfach die Preise in das System einzugeben. Es wird zusätzlich auch
das Sortierkriterium der Liste mit abgefragt, dass ggf. hier auch sofort und
einfach nachgepflegt werden kann.

---

## Preisnachkalkulation PKLN

Preisnachkalkulation PKLN
Mit dieser Anwendung können Preise zu Artikeln
kalkuliert werden, die laut zugehörigem Kalkulationsschema in der
Preiskalkulation via KalkListenPreis (Originalpreis) bearbeitet werden.
Genau diese Artikel können in der Preisnachkalkulation
jedoch entgegen der Kalkulationsgrundlagenangabe im Kalkulationsschema auf Basis
ArtiListenPreis bearbeitet werden! Die Originalpreise sind dann jeweils die
Preise des Zeitraums, in dem das aktuelle Tagesdatum liegt, ist dieser nicht
vorhanden, der Zeitraum davor.
Die Anwendung steht nur zur Verfügung, wenn
der zugehörige SPA ‚ Nachkalkulation ohne
KalkListenPreis‘ mit dem Wert ‚Ja‘ eingestellt ist
der SPA ‚ Preiskalkulation:
Kalkulationsgrundlage‘  mit einem der Werte
Grundpreise aus <KALKLISTENPREIS> zu letztem
Zeitraum
In Kalkulationsschema anzugeben
eingestellt ist.

---

## Preis, Preiseinheit

Preis, Preiseinheit
Kann der Preis nicht gelesen werden, so wird er auf 0
gesetzt.
Konnte keine Preismengeneinheit gelesen werden, so
wird sie mit der Mengeneinheit der default-Preismengeneinheit aus PRM_DEFAULT
belegt. Eine ggf. nicht lesbare Preiseinheit wird standardmäßig auf den Wert
voreingestellt, der aus dem Parameter PRE_DEFAULT gelesen wurde. Wenn nicht
lesbar, wird 1.0 eingestellt.
(Zugehörige
Positionsparameter: PR_SAx, PRE_SAx, PRM_SAx)
Preismengeneinheit
Die Preisengeneinheit
wird nach dem Einlesen in gleicher Weise wie die Mengeneinheit konvertiert.
Falls keine Mengeneinheit eingelesen werden kann oder eine Konvertierung durch
die Parameter MEM_1 bis MEM_5 nicht möglich ist, z. B. wegen Fehlwert oder
Inaktivschaltung des betreffenden Parameters, wird diejenige Aeins-Mengeneinheit
vorgegeben, die im Parameter PRM_DEFAULT abgelegt ist.
Eine Validierung
findet nicht statt.
(Zugehörige
Positionsparameter: PRM_SAx)

---

## Rabatt auf manuellen Preis (SPA 347)

Rabatt auf manuellen Preis (SPA 347)
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Wird ein ermittelter Preis manuell verändert, so kann
dies die Berechnung eines Rabattes verhindern. Dies wird im Steuerparameter
347 - Rabatte auch bei manuellem Preis
eingestellt.
Wenn die manuelle Eingabe eines Preises stets bedeuten
soll, dass hier bereits ein abweichender Rabatt eingerechnet ist, so wird diese
Einstellung sicher auf „Nein“ gestellt sein müssen.

---

## Rabatte bei Partiepreisen (SPA 294)

Rabatte bei Partiepreisen (SPA 294)
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Eine Einstellung des Steuerparameters
294 - Rabatte bei Partiepreisen aktiv
kann dafür sorgen, dass bei Partiepreisen kein Rabatt berechnet wird.

---

## Rabatte löschen (inkl. 1)

Rabatte löschen (inkl. 1)
In folgenden Relationen werden die Datensätze
entfernt:
Rabattklasse (ohne die 0 (ohne Rabatt) zu
entfernen)
Artirabattgruppe (ohne die 0 (kein Rabatt) zu entfernen)
ArtiRabattArt
ArtiRabattTyp
ArtiRabattSatz
ArtiRabattText
In folgenden Relationen wird die 0 für ‚ohne Rabatt‘
eingetragen:
Kundenstamm (Felder RabKlNummerEK, RabKlNummerEKI,
RabKlNummerVK, RabKlNummerVKI)
Artikel (Felder ArtiRabGrupEK, ArtiRabGrupEKI,
ArtiRabGrupVK, ArtiRabGrupVKI)
BaustArtikel (Felder ArtiRabGruppeVK,
ArtiRabGruppeEK)
Beim Löschen der Rabatte  werden automatisch die
Vorgänge
Ware
mit gelöscht.

---

## Rabattsperre durch Aktionspreis (SPA 310)

Rabattsperre durch Aktionspreis (SPA 310)
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Wird ein Aktionspreis verwendet, so ist unter
Umständen die Marge so gering, dass ein zusätzlicher Rabatt hier nicht gewünscht
wird.
Aus diesem Grunde gibt es mit Steuerparameter
310 - Zu-/Abschläge/Rabatte auf
Aktionspreise
die Möglichkeit, dies zu unterbinden.

---

## Rabattsperre im Rabatt

Rabattsperre im Rabatt
Eine Rabattsperre kann auch im Rabatt selbst
eingerichtet werden. So lassen sich eingerichtete Rabatte vorübergehend
abschalten.
Siehe Allgemeine Rabatte
.

---

## Rabattsperren

Rabattsperren
Es gibt mehrere Gründe, die dazu führen können, dass
ein Rabatt abweichend vom Standard nicht berechnet wird. Zumeist wird dies die
geringe Marge sein, die im Einzelfall nicht durch Zugabe bestimmter Rabatte
geschmälert werden soll.

---

## Ref. entfernen (Preiskalk.) PKRFL

Ref. entfernen (Preiskalk.)     PKRFL
Mit dieser Anwendung können Referenzen aus der
Referenzliste entfernt werden.
Die Auswahlliste ist analog der unter 1.6.1,
allerdings erscheinen hier nur Artikel deren VK-Listenpreisgruppe sich in der
Referenzliste befinden.
Mit der Funktion „zugeh. Artikel“  mit
Administratorrechten ausgestatteten Bedienern vorbehaltenen Funktion ‚Entfernen‘
kann die unter 1.6.1 vorgestellte Maske aufgerufen werden.

---

## Referenzliste

Referenzliste
Zur Pflege der Referenzliste gibt es einen SPA, der
angibt, ob alle Artikel oder nur Artikel, die in einer Referenzliste
‚referenziert‘ sind, zur Preiskalkulation herangezogen werden können.
SPA-Bezeichnung: „Preiskalkulation: zugelassene
Artikel“
Werte:  0: alle Artikel
1: nur Artikel aus Referenzliste
Es gibt bezüglich der Pflege der Referenzliste zwei
Anwendungen:
Ref.Liste (Preiskalkulation)   PKRF
Ref. entfernen (Preiskalk.)
PKRFL

---

## Ref.Liste (Preiskalkulation) PKRF

Ref.Liste (Preiskalkulation)   PKRF
Mit dieser Anwendung können zum einen der
Referenzliste neue Referenzen hinzugefügt werden, zum anderen aber auch bzgl.
der Preiskalkulation fehlerhaft eingerichtete Artikel aufgespürt werden.
Die Auswahlliste der Anwendung verfügt daher über die
beiden Standard-Varianten
Nicht referenzierte Artikel
Fehlerhafte Artikel
Erstere ist nicht aktiv, wenn der 0.a. SPA den Wert
„alle Artikel“ hat, denn dann wird die Referenzliste selbst nicht genutzt.

---

## Registerkarte Markt

Registerkarte
Markt
Alle Felder auf dieser Registerkarte werden nicht von
Referenz-ERP ausgewertet oder verwendet. Diese Felder stehen der
Datendrehscheibe
oder Privaten Anwendungen zur
Verfügung.
Feld
Bedeutung
Grundpreiseinheit
In
      diesem Feld wird die Grundpreiseinheit wie z.B. Kg
      eingetragen.
Grundpreis Faktor
In
      diesem Feld wird der Faktor eingetragen mit dem der Preis multipliziert
      wird.
Mit
      dem Faktor lässt sich dann der Grundpreis des Artikels berechnen. Mit
      diesen Informationen kann dann auf ein Etikett der Grundpreis gedruckt
      werden.
Wird
      die Datendrehscheibe verwendet so werden diese beiden Felder von Terres
      versorgt.
Preispflege per
      Datendrehscheibe
Wird
      dieser Schalter auf  „unterdrücken“ gestellt so wird ein neuer Preis
      der über die Datendrehscheibe importiert wird nicht übernommen.
Innerhalb von privaten Prozeduren
      oder Anwendungen muss dieser Schalter berücksichtigt werden, wenn dieser
      ausgewertet werden soll. Da Referenz-ERP dies nicht automatisch
      macht.
Artikelpflege per
      Datendrehscheibe
Wird
      dieser Schalter auf „unterdrücken“ gestellt, so wird der Artikel nicht
      durch den Import über die Datendrehscheibe verändert.
Innerhalb von privaten Prozeduren
      oder Anwendungen muss dieser Schalter berücksichtigt werden, wenn dieser
      ausgewertet werden soll. Da Referenz-ERP dies nicht automatisch
      macht.
Warengruppenpflege per
      Datendrehscheibe
Wird
      dieser Schalter auf „unterdrücken“ gestellt, so wird die Warengruppe nicht
      durch den Import per Datendrehscheibe geändert. Alle anderen Änderungen
      werden übernommen.
Innerhalb von privaten Prozeduren
      oder Anwendungen muss dieser Schalter berücksichtigt werden, wenn dieser
      ausgewertet werden soll. Da Referenz-ERP dies nicht automatisch
      macht.
Mengeinheitsgruppenpflege per
      Datendrehscheib
Wird
      dieser Schalter auf „unterdrücken“ gestellt
[...]


---

## Registerkarte Preise

Registerkarte Preise

---

## Sortierung der Schnellerfassung

Sortierung der Schnellerfassung
Die Sortierung steuert die Anzeige in der
Schnellerfassung. Es gibt noch zwei weitere Punkte, um die Sortierung
anzupassen, siehe dazu EPA Vererbung, Funktion Sortierung setzen und der
Preiseingabebereich Tabelle.

---

## Stapelkalkulation ausführen

Stapelkalkulation ausführen
Die Stapelkalkulation ist eine Kalkulationsform ohne
manuelle Eingreifmöglichkeiten.
Die aufgerufene Maske hat folgendes Aussehen:
In Auswahllisten-Varianten mit Originalpreisen aus
Kalklistenpreis wird zunächst bestimmt, ob die Ziel-Zeiträume der neuen Preise
aus Kalklistenpreis oder per  Datumseingabe manuell bestimmt wird.
In Auswahllisten-Varianten mit Originalpreisen aus
ArtiListenPreis ist lediglich die Zeitraumbestimmung per Datumseingabe
möglich.
Bei auf KalkListenPreis basierenden Varianten kann
SPA-abhängig bestimmt werden, ob die korrespondierenden Daten aus
KalkListenpreis gelöscht werden sollen. Diese Eingabemöglichkeit besteht nur
dann, wenn der SPA ‚Kalkpr.Übern.: KalkListenPreis löschen‘ mit dem Wert ‚mit
Abfrage‘ eingestellt ist.
Mit dem der Funktion ‚Kalkulation‘ wird die
Kalkulation gestartet. Die Artikelnummern und Bezeichnungen werden während der
Kalkulation auf der Maske angezeigt. Fehlermeldungen und Hinweise werden ins
Fehlerprotokoll (FEHLP) geschrieben.
Die Kalkulation erfolgt entsprechend der
Einzelkalkulation, übernommen werden immer die kalkulierten Preise.

---

## Stapelkalkulation Originalpreis

Stapelkalkulation Originalpreis
Die Funktion entspricht der unter 1.7.3 beschriebenen
Funktion, mit der Ausnahme, dass die Preise der Spalte ‚Originalpreise‘ hier
immer den unter 1.8 beschriebenen aus ArtiListenPreis entsprechen.
Der Zeittraum für die neuen Preise wird hier immer
manuell bestimmt.

---

## Tabelle zur Version: 8.3.2211.30

Tabelle zur Version: 8.3.2211.30
ID
Releasenote - Titel
Geprüft
33065
Preiskalkulation
33016
Windows 11 /Windows Server 2022
33086
Referenz-ERP.Libary-Viewer
33091
Geodaten anfragen
33022
Belegfluss
32988
Mail-Funktionen in der Ware
33099
Spalten für permanente Inventur in
      Warenbuch/Auswertung
33020
Steuersätze
33083
Hersteller bei individuellen Artikelnummern
32077
Editieren teildisponierter Positionen
33031
Teildisposition Erledigung bei Übererfüllung
33117
Vorzeichen bei rechnungebearbeitung

---

## Tabelle zur Version: 8.3.2303.31

Tabelle zur Version: 8.3.2303.31
ID
Releasenote - Titel
Geprüft
33581
OLE Steuerparameter
33278
SPA350 Druck Quellinfo einstufig in [FRZ]
33475
Bediener Deaktivieren/Aktivieren
33578
Rabatte bei manuellem Preis
    Vorgangsklassenabhängig
33598
neues Modul: Dashboard
33614
Rollenkontext (Bediener)
33620
Auswahlliste Funktionen
33454
Belegfluss
32085
Homepage anzeigen überarbeitet
33468
Vermailung: Email erneut versenden
33486
Complianceprüfung Webanbindung
33548
AIS-Makro in C# neues Interface
33645
Intrastat: Werte und Mengen
33473
Einzelbeleganzeige: Archiv
33476
Fibu Belegerfassung USt-IdNr
33537
e-Clearing Hausbank
33538
Finanzbuchhaltung: Jahreswechsel
33595
Elster: Kennzeichen 87 und 90
33650
Infoblattdruck für Forderungskonten
33574
Permanente Inventur mit Lagerplätzen
33215
Filter in Kontraktauswahlliste
33216
Lagerspezifischer Kontraktartikel
32613
Massebilanzeinrichtung
33418
Rohware: Behandlung bei Storno mit Kopie
33489
Massebilanz
33579
Rohwarenbelege in der Streckendisposition
33408
Formulare Einrichtungsparameter Druck
33459
Zollwarennummern einspielen
33470
Folgeartikel/indiv. Artikelnummer verschoben
33563
Geodaten bei Kundenanschriftänderung
33591
Druckfelder-Pfleger
33644
Bedienerstamm: Neuanlagedatum
32859
Vorgangsansicht: Makros
33460
Umwandlung mit abweichender Belegnummer
33461
Folgeartikel
33862
Vorgangsnachverfolgung: Datenanzeige

---

## Tabelle zur Version: 8.3.2312.8

Tabelle zur Version: 8.3.2312.8
ID
Releasenote - Titel
Geprüft
34410
Vorschau und Vorgangsdruck: Linker und oberer
    Rand
34533
Partiestamm: Funktion "Qualitäten"
34488
Preiskalkulation mit Excel [PKX]
34553
Artikelstammtexte Zeile/Spalte
34520
Ermittlung der Werte in der
      Perioden-Erfolgsauswertung

---

## Tabelle zur Version: 8.3.2312.22

Tabelle zur Version: 8.3.2312.22
ID
Releasenote - Titel
Geprüft
34620
Preiskalkulation Excel: Standardprozeduren
33201
Vorzeichenabhängige Mengendarstellung in der
      Kontraktauswahlliste
34541
Massebilanzzuordnung/entfernung Anzahl betroffener
      Belege
34570
Individuelle Artikelnummern
34571
Artikel Gebinde anzeigen
34573
Ändern eines Rechungsempfängers oder
      Zahlungspflichtigen

---

## techn. Informationen für Makro-Implementationen

techn. Informationen für
Makro-Implementationen
Folgende ID`s können im Rahmen einer Vorgangserzeugung
gesetzt werden, um den Ausbuchpreis zu setzen.
Wert
ID
Bedeutung
566
ID_AUSBUCH_PREIS
Preis mit dem die Ware ausgebucht
      wird.
567
ID_AUSBUCH_PREISEINHEIT
Preiseinheit mit der die Ware
      ausgebucht wird.
568
ID_AUSBUCH_ME
Mengeneinheit des Preises mit dem
      die Ware ausgebucht wird.
571
ID_INVENTUR_PREISTYP
Preistyp des Ausbuchpreises als
      Kennzeichen (s.u.)
572
ID_VORGLINKID
Gibt
      die Link-ID des Vorgangs aus.
573
ID_SETLINKID
Setzt die Link-ID des verlinkten
      Vorgangs als Linktyp
Mögliche Werte für einen Preistyp
Wert
ID
Bedeutung
0
INVENTUR_PREISTYP_UNBEPREIST
Unbepreist – Hier liegt kein
      Ausbuchpreis vor.
1
INVENTUR_PREISTYP_MANUELL
Manuell erfasster
      Ausbuchpreis
5
INVENTUR_PREISTYP_AUTO_TEMP
Hier
      wurde der zum Zeitpunkt der Erstellung gültige Bewertungspreis der Ware
      temporär festgelegt.
10
INVENTUR_PREISTYP_AUTOMATIK
Dieser Preis wurde automatisch
      eingefügt.
Mögliche Werte für den Linktyp
Wert
ID
Bedeutung
0
VORGLINKTYP_NIX
Kein
      gültiger Linktyp
1
VORGLINKTYP_PROD_INVENTUR
Hier
      werden Produktionen und Inventuren verknüpft. Diese Art der Verknüpfung
      bedeutet:
•
Die Stornierung
      einer der beiden Belege verursacht automatisch die Stornierung des
      anderen.
•
Die Korrektur
      beider Belege ist jeweils gesperrt.
Verknüpfung Produktion und Inventur
Es ist möglich, Produktionsbelege mit Inventuren zu
verknüpfen.
Der Hintergrund ist der, dass ein Teil der
aufgefundenen Ware zu einem anderen (meist minderwertigen) Verwendungszweck
umdeklariert werden soll (Produktion) und der Rest der Ware nunmehr
inventarisiert werden soll.
Dazu ist vom zuerst erstellten Beleg die eigene LinkID
festzustellen und beim zweiten Beleg mit der entsprechenden ID und den Linktyp 1
einzutragen.

---

## Vorgangs-Steuerungsparameter

Vorgangs-Steuerungsparameter
Steuerungsparameter werden systemübergreifend
festgelegt.
Max. Sicherheit (Checkpoint je Vorgang)
Ja/Nein
Eindeutige Vorgangsnummer je Klasse
Jahr
Rechnungen ohne Preis druckbar
Wirkungsweise:
Teilweise
oder vollständig unbepreiste Rechnungen können vom Druck ausgeschlossen
werden.
Wertemöglichkeiten:
Ja/Nein
Vorgangsklasse änderbar bei Verkauf
Wirkungsweise:
Mit
diesem Steuerparameter wird gesteuert, ob die aktuelle Vorgangsklasse in der
Vorgangserfassung geändert werden darf.
Wertemöglichkeiten:
Bei
"Ja" kann während der Vorgangserfassung von der aktuellen Vorgangsklasse in eine
andere umgeschaltet werden.
Vorgangsdatum änderbar bis Lieferschein
Ja/Nein
Abweichender Oberkunde aktiv
Wirkungsweise:
Mit
diesem Steuerparameter wird die Unterscheidung der Liefer- und
Rechnungsempfänger gesteuert.
Wertemöglichkeiten:
Bei
"Ja" kann eine automatische Unterscheidung von Lieferempfänger und
Rechnungsempfänger erfolgen.
Abweichender Zahlungspflichtiger aktiv
Wirkungsweise:
Mit
diesem Steuerparameter wird die Unterscheidung von Rechnungsempfänger und
Zahlungspflichtigen gesteuert.
Wertemöglichkeiten:
Bei
"Ja" kann eine automatische Unterscheidung von Rechnungsempfänger und
Zahlungspflichtigen erfolgen.
Negative Rechnung/Gutschriftsumme
Wirkungsweise:
Mit
diesem Steuerparameter wird gesteuert, ob ein negativer Endbetrag zulässig
ist.
Wertemöglichkeiten:
Bei
"Nein" lässt Referenz-ERP keine negativen Endbeträge zu.
Kreditlimit-Prüfung
Wirkungsweise:
Dieser
Steuerparameter regelt, ob die Limitverwaltung aktiv ist, und wie bei einer
Überschreitung mit dem betreffenden Beleg zu verfahren ist.
Wertemöglichkeiten:
0
= Nein die Kreditlimitüberwachung ist ausgeschaltet
1 = Warnung Es wird nur
ein Warnhinweis ausgegeben
2 = Sperrung Der Beleg wird wegen
Kreditlimitüberschreitung gesperrt und kann auch nicht gedruckt werden.
3 =
Abweisung Ein erfasster Beleg kann nur abgebrochen werden
Wechselwirkungen mit andern
SPAs:
Der Steuerparameter "
[...]


---

## Weitere Funktionen des Stapelpflegers aus Kundensicht

Weitere Funktionen des Stapelpflegers aus Kundensicht
Funktionen
Bedeutung
Ab Menge hinzufügen (Umschalt + Strg
      + Einfügen)
Fügt
      für die aktuell selektierte Preisgruppe (und damit für den aktuell
      selektierten Artikel) eine weitere Zeile ein. Die aktuelle Zeile fungiert
      hierbei als Kopiervorlage: alle Werte werden übernommen, lediglich die Ab
      Menge wird um Eins erhöht. Achtung: die neue Zeile wird automatisch
      gespeichert und wird auch nicht entfernt, sollte der Stapelpfleger über
      Abbrechen verlassen werden. Die Zeile muss in diesem Falle explizit mit
      dem im Folgenden beschriebenen Kommando „Ab Menge löschen“ entfernt
      werden.
Ab Menge löschen (Umschalt + Strg +
      Entfernen)
Nach
      entsprechender Rückfrage wird die aktuell selektierte Zeile entfernt.
      Achtung: die Ansicht wird automatisch gespeichert, der Löschvorgang wird
      auch nicht rückgängig gemacht, sollte der Stapelpfleger über Abbrechen
      verlassen werden. Die Zeile muss in diesem Falle explizit mit dem Kommando
      „Ab Menge hinzufügen“ wieder hinzugefügt werden.
Ansicht wechseln (Funktionstaste
      F6)
Wechselt die Ansicht in die
      Profileinstellungen mit entsprechenden Filter- und
      Anzeigeoptionen.
PRI aufrufen (Umschalt +
      Funktionstaste F6)
Ruft
      den
Einzelsatzpfleger
für die aktuell eingestellte Preisgruppe/Preisklasse auf: die im
      Preisstapelpfleger freie Dimension Preisgruppe wird damit
      fixiert.
Speichern (Funktionstaste
      F9)
Die
      vorgenommenen Änderungen werden dauerhaft gespeichert. Sollte der
      Stapelpfleger versehentlich über ESC verlassen werden, fragt das System
      vorsorglich nach, ob vorgenommene Änderungen gespeichert oder verworfen
      werden sollen.

---

## Wertbestimmung

Wertbestimmung
Manueller EK
Diese Funktion unterstützt bei der Kalkulation von
Preisen:
Über Basis kann ein Bewertungspreis in das Fenster
eingelesen werden: letzter, gewogener, etc., der Grundlage der Kalkulation
werden soll. Der VK wird durch Eingabe in „Aufschlag“ oder „Marge“ kalkuliert.
Der EK kann wahlweise festgehalten werden.
Ein ggf. kalkulierter EK wird im System mit der Notiz
„M“ gespeichert und kann ausgewertet werden.
Für Artikel, die immer kalkuliert werden müssen
(Projekte), wird im Artikel unter „weitere Kennzeichen“, „automatische Maske für
Preisbestimmung“ hinterlegt, dass sie immer geöffnet wird.
Im Einrichterparameter kann hinterlegt werden, dass
beim Einstieg in die Maske das Kontrollfeld „EK-Preis festhalten“ markiert
ist.
Brutto/Netto-Preis
Diese Funktion ist eine Rechenhilfe für die Eingabe.
Befindet man sich in einem Brutto-Beleg, gibt jedoch
den Netto-Preis ein, so kann zu diesem Betrag mit Hilfe dieser Funktion die
Steuer addiert werden.
In Netto-Belegen bewirkt die Funktion die Subtraktion
des Steueranteils von dem aktuellen Preis-Betrag.
Die Funktion wird nach der Verwendung ausgeblendet, um
versehentliche mehrfach-Nutzung zu verhindern. Eine „Zurück“-Möglichkeit gibt es
an dieser Stelle nicht.

---

## Zu-/Abschlagsperre durch Aktionspreis (SPA 310)

Zu-/Abschlagsperre durch Aktionspreis (SPA 310)
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Wird ein Aktionspreis verwendet, so ist unter
Umständen die Marge so gering, dass ein zusätzlicher Zu-/Abschlag hier nicht
gewünscht wird.
Aus diesem Grunde gibt es mit Steuerparameter
310 - Zu-/Abschläge/Rabatte auf
Aktionspreise
die Möglichkeit, dies zu unterbinden.

---

## Zu-/Abschlagsperren

Zu-/Abschlagsperren
Es gibt mehrere Gründe, die dazu führen können, dass
ein Zu-/Abschlag abweichend vom Standard nicht berechnet wird. Zumeist wird dies
die geringe Marge sein, die im Einzelfall nicht durch Zugabe bestimmter
Zu-/Abschläge geschmälert werden soll.

---

## Zugeh. Artikel

Zugeh. Artikel
Die hier genutzte Maske ist dieselbe, wie in den
Funktion ‚Hinzufügen‘ dieser Variante, der Funktion ‚zugeh. Artikel‘ der
Variante ‚Fehlerhafte Artikel‘ und der Funktionen ‚ zugeh. Artikel‘ und
‚Entfernen‘ der Anwendung
‚Ref. entfernen (Preiskalk.)     PKRFL‘.
Unterscheidungen gibt es hinsichtlich der dort
vorhandenen Funktionen.
Der obere Teil der Maske bleibt nach Einstieg bzw.
Blättern zunächst leer.
Darunter sind etwas genauere Angaben zum Artikel
angegeben:
Insbesondere wird zu den beiden Listenpreisgruppen die
Anzahl der Artikel mit jeweils gleicher Gruppe, sowie SPA-abhängig der darin
enthaltene Anteil von Artikeln mit Unterscheidung bei der jeweils anderen Gruppe
angegeben. Auch die Anzahl der Artikel mit gleicher VK-Listenpreisgruppe aber
anderem Preiskalkulationsschema ist hier zu sehen.
Je nach Inhalt dieser Felder enthält die Optionbox der
Maske folgende Einträge:
* Hinzufügen zur Referenzliste
Mit dieser Funktion wird die VK-Listenpreisgruppe des
Artikels in die Referenzliste eingetragen. Diese Funktion ist aber nur in der
Funktion ‚Hinzufügen‘ der Anwendungsvariante ‚ Nicht referenzierte Artikel‘
vorhanden, wenn der Artikel nicht fehlerhaft bzgl. der Preiskalkulation ist.
Ende
Verlassen der Maske
* Entfernen aus Referenzliste
Mit dieser Funktion
wird die VK-Listenpreisgruppe des Artikels aus der  Referenzliste
entfernt.    Diese Funktion ist aber nur in der Funktion
‚Entfernen‘ der Anwendung ‚ Ref. entfernen (Preiskalk.)
PKRFL ‘ vorhanden.
zugeh. Artikel (VK-LpGr.)
Diese Funktion ist immer vorhanden und bewirkt das
Füllen des oberen Anzeige-Arrays der Maske mit den Daten aller Artikel mit der
VK-Listenpreisgruppe.
Artikel anderer VK-LpGr.
Diese Funktion ist immer dann vorhanden, wenn es
Artikel zur EK-Listenpreisgruppe mit abweichender VK-Listenpreisgruppe gibt und
die SPA-Einstellung für ‚ Preiskalk.: EK-Listenpreisgruppen‘ nicht ‚ keine
Berücksichtigung‘ ist. Sie bewirkt das Füllen des oberen Anzeige-Arrays d
[...]


---

