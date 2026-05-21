# Pflanzenschutz & PSM-Dokumentation — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (37 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Geodaten anfragen

Geodaten anfragen
Die Ermittlung von Geodaten wurde wiederhergestellt,
nachdem der Webservice seine Abfragestrukturen geändert hat.
Releasenote Kategorie:
Ticket: 716215[33091]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Anschriften
Variante: Standard
Funktion/Report: Geodaten ermitteln
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33091, 716215

---

## ILN nicht aus dem AI 01 ermitteln. (SPA 739)

ILN nicht aus dem AI 01 ermitteln. (SPA 739)
Hiermit wird die automatische ILN Ermittlung
ausgestellt.

---

## Gefahrgutmesszahl auf Basis Grundmengeneinheit (SPA 913)

Gefahrgutmesszahl auf Basis Grundmengeneinheit (SPA 913)
Die Gefahrgutmesszahl wird aus dem Gewicht einer
Warenposition errechnet. Bei Einstellung ‚Ja‘ wird die ermittelte Menge der
Warenposition immer in die entsprechende Grundmengeneinheit gewandelt um dann
mit dem Gewicht pro Grundmengeneinheit multipliziert zu werden. Ist dieser SPA
auf ‚nein‘ gesetzt, wird zur Berechnung die in der Warenposition erfasste Menge
herangezogen.

---

## DTA – Optionen (SPA 919)

DTA – Optionen (SPA 919)
Hier können Optionen für
DTA
gepflegt
werden.
Typ
Wert
CSATZ Name Herkunft
Hier
      kann eingestellt werden wie der CSATZ_NAME ermittelt wird.
Wert
Bedeutung
Standardmäßig
            wird der CSATZ_NAME wie folgt gebildet:
•
Empfänger /
            Zahlungspflichtiger aus der Kundenbank
•
Wenn in der Kundenbank kein
            Zahlungspflichtiger eingetragen ist, dann der Empfänger /
            Zahlungspflichtige aus dem Kundenstamm (Fibu-Merkmale)
•
Wenn auch dieser Wert leer
            ist dann Kundenbezeichnung
1
Ermittlung des CSATZ_NAME
nur
aus
            dem Namen der Hauptanschrift.

---

## Signature Pad am Arbeitsplatz und Software auf Remoteserver einrichten

Signature Pad am Arbeitsplatz und Software auf Remoteserver einrichten
Diese Kapitel beschreibt die Einrichtung des Signature
Pads an einer Workstation und dem Einrichten der Applikationssoftware auf dem
Remoteserver.
Voraussetzungen und benötigte Software siehe Kapitel
Signature Pad
einrichten
.
Einrichtung der Treiber auf der
Workstation:
1.
Signature Pad an einen freien USB-Steckplatz anschließen.
2.
Treiber (Zip-Datei) entpacken.
3.
Die im vorigen Schritt entpackte Exe-Datei ausführen.
4.
Nach Abschluss der Installation erscheint das Logo von Signotec auf dem Display
des Signatur Pads.
Einrichten der Remotedesktopverbindung:
1.
Dialog für „Remotedesktopverbindung“ öffnen.
2.
Schaltfläche „Optionen einblenden“
drücken.
3.
Feld „Computer“ ausfüllen.
4.
Feld „Benutzername“
ausfüllen.
5.
Reiter „Lokale Ressourcen“
auswählen.
6.
Schaltfläche „Weitere …“ im
Bereich „Lokale Geräte und Ressourcen“ drücken.
7.
Auswahlfeld „Ports“
aktivieren.
8.
Schaltfläche „OK“ drücken.
9.
Schaltfläche „Verbinden“
drücken.
10.
Am Remoterechner anmelden.
Einrichtung der Werkzeug-Software auf dem
Remoteserver:
1.
Setup-Datei der Werkzeug-Software
ausführen.
2.
Sprache auswählen.
3.
Lizenzvereinbarung annehmen.
4.
Pfad übernehmen (hier „C:\Program
Files\signotec\“).
5.
Installation „Vollständig“
auswählen.
6.
Funktionsweise: 1. Option
auswählen.
7.
Treiber „Signotec_WinUSB_64Bit“ +
„Signotec_HID_64Bit“ nicht installieren.
Einrichtung der Software „SignoSign/2“ auf dem
Remoteserver:
1.
Setup-Datei der Software „SignoSign/2“ ausführen.
2.
Sprache auswählen.
3.
Lizenzvereinbarung annehmen.
4.
Pfad übernehmen (hier C:\Programme\signotec).
5.
Setup-Option „Angepasst“ und alle Programmteile auswählen.
6.
Treiber „Signotec_WinUSB_64Bit“ + „Signotec_HID_64Bit“ nicht installieren.
7.
Das Programm „SignoSign/2“ starten.
8.
Im Fenster „Wichtige Informationen“ das Auswahlfeld „Nicht mehr anzeigen“
deaktivieren und die Schaltfläche „OK“ drücken.
[...]


---

## AIS im Vorgang

AIS im Vorgang
Mit diesem Modul können bestimmte oder alle AIS-Felder
auf den Vorgangserfassungsmasken in Abhängigkeit von bestimmten Feldern und
Events mittels eines Makros aktualisiert werden. Das aktualisieren der einzelnen
AIS Felder wird generell über ein Makro gesteuert, welches in
[FRZ]
auf der Registerkarte AIS einzutragen
ist.
Es gibt aber einige Ausnahmen, hier sind die
Aktualisierungspunkte fest vergeben und aktualisieren das komplette AIS auf der
Maske. Die Ausnahmen werden in den Einrichtungshilfen zu den jeweiligen Masken
erklärt.
Folgende Vorgangsmasken unterstützen bislang das
dynamische Aktualisieren von AIS Feldern:
1.
SVMAIN
2.
SVPOSI
3.
SVWARE
4.
SVUMMAIN
5.
SVUMWARE
6.
SVPOSBAR2
Einrichtung
1.
Einrichtung des
AIS
Hauptmenü
Administration
Werkzeuge
Informationssystem
oder Direktsprung
[AIS]
2.
Erstellen eines Makro
Hauptmenü
Administration
Makroverarbeitung
Makro-Programme
oder Direktsprung
[MAKRO]
3.
Einrichtung des AIS für die Vorgangsmasken auf der
Registerkarte AIS
Hauptmenü
Administration
Formulare / Abläufe
Formularzuordnung/Vorgangsunterklasse
oder Direktsprung
[FRZ]
Es empfiehlt sich für jede Vorgangsmaske eine eigene
Funktion in dem Makro anzulegen. In der Vorgangsunterklassen Zuordnung wird die
gewünschte Funktion des Makros der AIS-Gruppe zugeordnet. Der Makro-Name in dem
Feld „Screen-Makro“ kommt aus der jeweiligen AIS-Gruppe. Für jede Vorgangsmaske
können mehrere AIS-Gruppen in FRZ hinterlegt werden. Dabei ist zu beachten, dass
alle Gruppen, die in FRZ einer Maske zugeordnet worden sind, nacheinander
aufgerufen werden.
Hinweis zu dem Makro
Das Makro, welches das Aktualisieren des AIS steuert,
darf
nicht zur Wertveränderung
im Vorgang benutzt werden. Da nicht
sichergestellt werden kann, dass die Änderungen mit in den Vorgang übernommen
werden. Um Änderungen am Vorgang vorzunehmen, ist dies weiterhin per
Kontrollmakro zu realisieren.
Außerdem ist darauf zu achten, dass das
Zusammenstellen d
[...]


---

## SQL Beispiele für den Bilddruck

SQL Beispiele für den Bilddruck
Im Dokument wird ein Strichcode vom Typ "Qrcode"
eingefügt.
Über das Kontextmenü "Formatieren..."  lässt sich
mittels der Register "Layout und Position" und "Größe und Abstand" die
gewünschte Ziel-Position und Größe festlegen.
Im Register "Typ und Farbe" läßt sich im Abschnitt
"Typ" im Feld "Text" die Anbindung einer privaten Sql-Prozedure durchführen.
Die private Sql-Procedure muss folgende Spalten
zurückgeben:
Parameter-Name
Parameter-Name
code
long
      varchar
codetype
long
      varchar
Der Inhalt des Parameters "codetype" steuert wie der
Inhalt von "code" interpretiert wird.

---

## Ermittlung durch Archiv

Ermittlung durch Archiv
Bei diesen Codetypen ermittelt das Programm die
zugehörigen Mimetypen automatisch.
Inhalt von
"codetype"
Bedeutung von
  "code"
archiv
Enthält den Primary Key der Relation
      "Formulararchiv" Fa_Id, Fa_MndNr als Zeichenkette durch Komma
      getrennt.
Beispiel für Codetype "Archiv"
procedure p_beispiel_file()
result (code long varchar, codetype long varchar)
begin
select '17494,1' as code, 'archiv' as
codetype
end
Einrichtung in Strichcode im Feld "Text":
p_beispiel_archiv()

---

## Ermittlung durch Sql-Statement

Ermittlung durch Sql-Statement
Wird ein unterstützter Mimeytp in "codetyp"
übermittelt dann wird der Wert in "code" als Sql-Statement zur Ermittlung des
Bild-Inhaltes interpretiert.
Unterstützte Mimetypen in
      "codetyp"
image/bmp
image/ jpeg
image/png
image/tiff
image/gif
image/x-icon
Beispiel-Prozedur für den Fall Mimetyp
procedure p_beispiel_mime()
result (code long varchar, codetype long varchar)
begin
select 'select i_image from bitimages where
imageid=117' as code,
(select i_mime from bitimages where imageid=117)
as codetype
end
Einrichtung in Strichcode im Feld "Text":
p_beispiel_mime()

---

## Druckerstatus-Etikettendruck

Druckerstatus-Etikettendruck
Mittels der Funktion
Druckerstatus
kann der „Etikettendruck“
gestartet werden. Der Vorteil dieser Funktion liegt in der automatischen
Vorschau der Druckaufträge. Es werden alle Druckaufträge des für den
Etikettendruck eingestellten Druckers angezeigt.
Sind Druckaufträge vorhanden, können diese mittels der
Funktion
Alle Druckaufträge löschen
F7
gelöscht werden. Direkt im
Anschluss daran wird automatisch die Maske für den Etikettendruck geöffnet. Über
die Funktion
Partieetikett drucken
kann aber auch manuell in die Etikettendruck Maske gewechselt werden.
Sind keine Druckaufträge vorhanden wird sofort
automatisch die Maske für den Etikettendruck aufgerufen.

---

## Abschöpfung (Einreichung) an Bank/zugehörige Hauptkasse

Abschöpfung (Einreichung) an Bank/zugehörige
Hauptkasse
Hauptmenü
Barvorgäng
Zahlung
Abschöpfung / Einreichung
Manuelle Einreichungen können mit Hilfe der Maske
„Einreichungen“ eingereicht werden.
Es werden die noch einzureichenden Zahlungsmittel
angezeigt. Bargeldbeträge können über das Eingabefeld „Bargeldeinreichung“
abgeschöpft werden. Der Betrag der Bargeldeinreichung darf nicht größer sein als
der Bargeldbestand.
Beschreibung
Bank
Die
      Nummer der Hausbank
Bankbezeichnung
Der
      Name der Bank
Kasse
Die
      Kassennummer an der die Einreichung erfolgt
Sitzung
Die
      Sitzungsnummer der Kasse
BelegNr
Die
      Belegnummer
ZamiIdNr
Die
      Zahlungsmittel-Identifikations-Nummer
Zahlungsart
EC
      Karte oder Gutschein
Betrag
Der
      eingezahlte Betrag zu dem Zahlungsmittel
Sitzung
Die
      Kassensitzungsnummer in der der Beleg erstellt wurde
Kasse
Die
      Kassennummer an der der Beleg erfasst wurde.
Es
      können nur Belege eingereicht werden, die zu der geöffneten Kasse
      gehören.
Einreichen
Ja /
      Nein: Auswahl, ob dieser Beleg eingereicht werden soll.
Datum
Erstellungsdatum des
      Zahlungsmittelbeleges
KartenNr / GutscheinNr
Die
      EC Kartennummer bzw. die Gutscheinnummer
Konto
Kontonummer des Kunden
BLZ
Die
      Bankleitzahl
Bank
Name
      der Bank / Bemerkungstexr von dem Gutschein
Kunde
Die
      Kundennummer
Bargeldbestand
Der
      Bargeldbestand ohne Wechselgeld der Kasse
Summe Zahlungsmittel
Die
      Summe der Beträge von den einzureichenden Zahlungsmitteln.
Bargeldeinreichung
Der
      Betrag der an Bargeld abgeschöpft werden soll.
Gesamtbetrag Einreichung
Die
      Summe aller Beträge die eingreicht werden.
Einreichung Ausführen F9
Alle
      markierten Zahlungsmittel und Bargeldbeträge werden
      eingereicht.
Alle
      Zami einreichen
Alle
      Zahlungsmittel werden markiert
Sitzung Zami einreichen
Alle
      Zahlungsmittel dieser Kassensitzung werden markiert.
Vorgänger Zami

[...]


---

## Datenbankprozedur für Neuanlage

Datenbankprozedur für Neuanlage
Ermöglicht bei der Neuanlage von Partien die
individuelle Vorbelegung diverser Felder mittels einer privaten
Datenbankfunktion:
Einrichtung der Prozedur
Diese Prozedur wird in der Vorgangsunterklasse [FRZ]
eingerichtet (DB-Prozedur für Neuanlage). Nach Eingabe des Prozedurnamens und
anschließender Rückpositionierung auf dieses Feld können die entsprechenden
Übergabeparameter eingestellt werden, die der Anwender für seine Prozedur
wünscht. Auf der rechten Seite kann ein hieraus erzeugtes Muster für die
Datenbankprozedur durch Kopieren übernommen werden.
Ablauf der Neuanlage der Partie
Zunächst werden Standardvorbelegungen durchgeführt.
Anschließend werden die Vorbelegungen aus bisherigen Einrichterparametern oder
-Einstellungen übernommen. Danach wird der Partiestamm in der Datenbank
angelegt. Es werden aber noch keine Partieartikel hinzugefügt!
Anschließend wird dann, sofern eingerichtet, die
individuelle Datenbankprozedur aufgerufen.
Bitte beachten
: Wenn innerhalb
dieser Prozedur eine Änderung erfolgt, muss diese mit einem ‚COMMIT’
abgeschlossen werden.
Abschließend wird dieser Partiestamm wieder eingelesen
und auf der Erfassungsmaske präsentiert (es gibt allerdings auch Situationen, in
denen Partien nur im Hintergrund erzeugt werden, wie z.B. bei der automatischen
Belegpartie!).
Parameterübergabe an die Prozedur
An die Prozedur wird eine Reihe von Parametern
übergeben, die bei der Vorbelegung hilfreich sein können. Es können aus
technischen Gründen nicht immer alle Parameter mit Werten übergeben werden.
Folgende Parameter stehen zur Verfügung:
PartieId:
Die neu erzeugte Partie kann durch
die PartieId eindeutig identifiziert werden
Vorgangsklasse
: Die Vorgangsklasse des
aktuellen Beleges (im Fall ‚Waage’ handelt es sich hierbei um die
Vorgangsklasse, mit der später der Vorgang erzeugt wird)
Vorgangsunterklasse
: Wie Vorgangsklasse
Belegnummer
: Soweit vorhanden, die Belegnummer
des Beleges
Aufruftyp
: Mit die
[...]


---

## Funktion anlegen

Funktion anlegen
Damit können Sie in der Anwendung „Formulararchiv“
automatisch eine private Funktion anlegen lassen, die das spezifizierte Profil
aufruft und durchführt. Aus technischen Gründen steht diese Funktion nicht
unmittelbar zur Verfügung. Nach einem Neustart von Referenz-ERP soll sie aber
vorhanden sein.
Durch die Funktionalität
Funktion anlegen
werden Funktionen in der
Anwendung Formulararchiv integriert um den Aufruf komfortabel zu gestalten.

---

## Serial-Device-Server

Serial-Device-Server
Ein Serial-Device-Server ist eine relativ kleine
Hardware, die an ein Netzwerkkabel angeschlossen wird und einen oder mehrere
serielle Anschlüsse (RS232 / V.24) zur Verfügung stellt. Diese Geräte können
mittels eines Treibers als virtueller COM-Port auf einem oder mehreren Rechnern
eingerichtet werden. Die Verbindungsparameter der seriellen Schnittstelle werden
direkt im Gerät mittels Software oder Treibereinstellungen konfiguriert.
Die Daten selbst werden vom Treiber oder von einer
Software an eine Netzwerkadresse und einen zugehörigen Netzwerkport gesendet, so
dass diese dann seriell ausgegeben werden.
In Referenz-ERP sind beide Verwendungsmöglichkeiten
(virtueller COM-Port und Netzwerk-Port) möglich. Siehe
Kassensystemeinstellung
Displayeinstellungen
MOXA NPort 5110/EU V2.0
Ist bei uns für die Entwicklung der Ansteuerung per IP
verwendet worden. Netzwerkport ist 950.

---

## Interaktion während des Importvorgangs Archiv

Interaktion während des Importvorgangs Archiv
Nach Ermittlung der Kriterien durch reguläre Ausdrücke
und optionalen Script, besteht nun noch die Möglichkeit, das trotz alledem keine
entsprechenden Daten ermittelt worden konnten.
Im Normalfall wird der Import vereinbarungsgemäß nicht
durchgeführt.
Oftmals kann und sollte diese fehlende Information
aber vom Bediener ggf. nachgefragt und nachgetragen werden. Per Interview lässt
sich das somit gleich durchführen.
Aktiviert wird das Verfahren über den Schalter
„Interaktiv“.
Das System wird bei fehlenden Daten, das sind genau
solche die einen reguläres Kriterium haben und zu keinem Ergebnis führen eine
Dialogmaske öffnen und den Benutzer fragen.
Eine beispielhafte Interview-Maske sei die
folgende:
Die Fragezeichen weisen die Kriterien „Kundennummer“
und „Belegreferenz“ als nicht gültig bzw. als nicht ermittelbar aus und es ist
am Bediener diese Daten zu ermitteln.
Der Bediener kann nun den Import „übernehmen“, er kann
auch diesen aktuellen einzelnen Beleg „nicht übernehmen“ und er kann den
gesamten „Import abbrechen“.
Bis dato importierte Daten bleiben importiert!

---

## Nachbearbeitung

Nachbearbeitung
Auf Grund der möglichen Komplexität der vorliegenden
Daten kann es durchaus Fälle geben, in dem das sehr flexible System der
regulären Ausdrücke nicht im ersten Schritt reicht, um die gewünschte
Daten-Repräsentation und damit unmittelbar das Kern-Datum zu gewinnen. Deshalb
lässt sich jedes Ergebnis noch mal durch einfache reguläre Methoden nach- bzw.
aufbereiten.
Hierbei ist es möglich, störende Leerzeichen zu
eliminieren, Umstellungen und Umformatierungen zu erreichen. Die Beispiele
sollen hinreichend Anschauungsmaterial bieten.

---

## Scanner Original Daten

Scanner Original Daten
In dieser Variante werden die vom Scanner
übermittelten Rohdaten, sowie die Informationen welcher der Scanner darstellen
soll angezeigt. Eine Zeile entspricht einem Scanvorgang.
Folgende Menüfunktionen stehen zur Verfügung:
1.
AI-Stammdaten
2.
Server starten
3.
Ausgewählte Daten löschen.
Mit dieser Funktion können
markierte Datensätze gelöscht werden
4.
Mit dieser Funktion können erfasste Inventurdaten nachgespielt werden.

---

## Stapelkorrektur Artikel

Stapelkorrektur Artikel
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel-Stapelkorrektur
oder Direktsprung
[ARK]
Nach Eingabe neuer Parameterwerte und dem Starten
mittels
F9
werden die neuen Werte
eingetragen.

---

## Vorgang Nachverfolgung

Vorgang Nachverfolgung
Direktsprung
[VNV]
Mit dem Modul Vorgang Nachverfolgung werden zu einer
Vorgangsposition alle zugehörigen Positionen anderer Vorgänge dargestellt. Dazu
wird in einer positionsorientierten Vorgangsbearbeitungsauswahlliste eine
Position ausgewählt und mittels der Tastenkombination
SHIFT F4
und der
Eingabe des Direktsprungs
VNV
die Nachverfolgung dieser Position
aufgerufen.
Die daraufhin dargestellte Auswahlliste zeigt
Informationen zu allen aus der gewählten Position resultierenden Positionen von
Ziel- und Quellvorgängen.
Feld
Beschreibung
Nummer
Die
      Belegnummer des Vorgangs.
Datum
Das
      Vorgangsdatum des Vorgangs.
Kontonr.
Die
      Kunden- oder Lieferantennummer (Kontonummer) des Vorgangs.
Kunde
Die
      Bezeichnung des Kunden oder Lieferanten
Artikel
Die
      Artikelnummer der Position.
Lg.
Die
      Lagernummer der Position.
Menge
Die
      ursprüngliche Menge der Position (abzüglich der Abgänge durch die
      ‚Schnelle Teildisposition‘).
Restmenge
Die
      noch zu verarbeitende Menge der Position.
Wert
Der
      ursprüngliche Wert der Position.
Restmenge
Der
      noch zu verarbeitende Wert der Position.
Dru
Das
      Kennzeichen, ob der Vorgang gedruckt wurde.
Fib
Das
      Kennzeichen, ob der Vorgang an die Finanzbuchhaltung übergeben
      wurde.
RAB
Das
      Kennzeichen, ob der Vorgang an das Rechnungsausgangsbuch übergeben
      wurde.
v_id
Die
      Vorgangs-Id des Vorgangs.
V_idquelle
Die
      Vorgangs-Id des Vorgangs, der zur Nachverfolgung gewählt wurde. In der
      Auswahlliste ist dieser durch die Übereinstimmung von v_id und v_idquelle
      leicht zu identifizieren

---

## Maske Lademittelzuordnung

Maske Lademittelzuordnung
Die markierten Mengen aus dem
GFV
werden in
diese Maske übernommen. Hier kann das gewünschte Lademittel ausgewählt und die
Mengen der einzelnen Positionen verändert werden. Das Gewicht wird aut.
berechnet, es können daher Rundungsfehler in Nachkommastellenbereich auftreten.
Beim Verlassen der Maske (Taste <ESC>) erscheint eine Abfrage ob
gespeichert werden soll. Werden keine Änderungen in der Maske vorgenommen und
die Abfrage mit ja bestätigt so werden die im
GFV
ausgewählten Mengen dem
Lademittel zugewiesen.

---

## Maske Partiemengenverteilung

Maske Partiemengenverteilung
In dieser Maske kann die Gesamtmenge des Artikels auf
verschiedene Partien auf gesplittet werden. Dazu wird in der Spalte „Partienr.“
die Partienummer eingegeben oder mittels Taste <F3> eine zugehörige Partie
ausgewählt und anschließend kann die Menge verändert werden. Das System erzeugt
aut. einen neuen Eintrag mit der noch nicht zugeordneten Restmenge.

---

## Archiv

Archiv
-41000
Generierung des Archiv-Dokumentes
-41001
FAAStatus konnte nicht ermittelt werden.

---

## Archiv ansehen (JVARS)

Archiv ansehen (JVARS)
Beim Ausführen einer Archiv-Ansicht werden
Datenermittlungen gemäß der in der zugehörigen
Archiv-Ansichts-Definition
und in den
Archiv-Ansichten Details
hinterlegten Regeln und Vorschriften erhoben. Die so ermittelten Daten werden in
speziellen JVARS hinterlegt. Die Kenntnis dieser JVARS erlaubt es diese z.B. in
Ableitungen
zu nutzen.
Parameter-JVars des Owners
      5001
Informatorisch favv_id aus
      fa_view_vars
REFERENZ
0
KUNDNUMMER
1
ZW1
2
ZW2
3
ZW3
4
ZW4
5
ZW5
6
JahrBeginn
100
JahrEnde
101
Belegtyptext
102
Belegklasse
103
Belegnummer
104
GRUPPE
200
LINIE
201
freies ODER
300
freies UND
301
freies JOIN
302
Die obigen JVARS sind dann belegt, wenn sie in den
Archiv-Ansichten Details
angegeben wurden. Zudem existiert zusätzlich eine paarige JVAR mit fast gleichem
Namen (um ein Ausrufezeichen erweitert). Diese JVAR hat 0 oder 1 als Inhalt, je
nachdem  ob es sich um einen „selektionswirksamen“ Parameter handelt.
Selektionswirksame JVARS werden zur Konstruktion des Where-Statements
herangezogen.
Sql-JVars des Owners
      5001
FAA_JOIN
FAA_AUSWAHL
Im Standard sowie im „Vorschau-Modus“ der
Archiv-Anzeige ist die zugeordnete Variante im Ansichts-Profil hinsichtlich der
SQL-Statement-Gewinnung maßgeblich. (siehe
Hauptmenü
Administration/Archiv/Archiv-Ansichten
, Auslieferungsvariante ist
„fa_anzeige“)
In der Auslieferungsvariante ist der Zusammenhang mit
den Sql-JVars des Owners 5001 zu erkennen:
SQL
select :FIELDS from formulararchiv fa
:!JVARS_5001_FAA_JOIN
where ( 1=1 )
:!JVARS_5001_FAA_AUSWAHL
order by
fa.FA_Druckdatum desc
Somit werden mit Hilfe der
Archiv-Ansichts-Definition
die Inhalte der
obigen JVARS ermittelt.
Weitere JVars des Owners 5001 zwecks
      Where-Ermittlung.
JVAR_FAARCHIV_VIEW_AND
Summierungsergebnisse der „freies
      UND“
JVAR_FAARCHIV_VIEW_OR
Summierungsergebnisse der „freies
      ODER“
Administrative Sql-JVars des Owners
      5001
JVAR_FAARCHIV_VIEW_FAVP_ANWID
Technische ID der
Archiv-Ansichts-Def
[...]


---

## Aus Auswahlliste

Aus Auswahlliste
In diesem Modus zieht die Eingrenzung  der
Auswahlliste. Natürlich werden  keine schon gebuchten Belege nochmals
übertragen. Zur Sicherheit werden  Belege mit Fälligkeit größer als 3 Tage
voraus nicht übertragen. Dies Begrenzung lässt sich jedoch mittels einer in
diesem Modus erscheinenden Option einstellen !
(Option: ‚Fällig größer 3Tage abweisen’).

---

## Ausgehende Telefonie

Ausgehende Telefonie
Ausgehende Telefonie wurde bisher von Referenz-ERP an das
Windows-System delegiert und von diesem weiterverarbeitet. Diese
Weiterverarbeitung basiert darauf das Windows eine Liste registrierter
TAPI-Anwendungen hat und dem Standard-TAPI-Programm die übermittelte
Telefonnummer überreicht.
Auf den meisten Windows-Systemen kommt dann der
sogenannte Windows-Dialer zum Einsatz und führt den Anruf letztendlich
durch.
Die Konfigurierung des Windows-Dialers gestaltet sich
ja nach verwendetem Telefonie-Produkt entsprechend, in letzter Zeit stellten
sich dabei schier unlösbare Probleme da im Zusammenhang mit Windows 2008 und
entsprechenden Umgebungen. Um diese Probleme nicht auf den End-Anwender
abzuwälzen und somit zu entschärfen geht Referenz-ERP nun eine optionale Strategie. Es
setzt mit Hilfe eines extra dafür entwickelten Programmes den Anruf direkt auf
der entsprechenden sogenannten Telefonie-Line ab.
Erste Tests in Echtumgebungen ergaben durchweg gute
Ergebnisse.
Parametrisiert wird diese Funktionalität über
Optionen. Dieses Feature ist bis zur Verwendung und Auswertung
Referenz-ERP-Versionsabhängig, die eigentliche Telefonie-Applikation ist dann
Referenz-ERP-Versions-unabhängig und kann somit zeitnah auf etwaige neue Erkenntnisse
in dem Telefoniebereich reagieren.
Die Einrichtung erfolgt über Optionen in Referenz-ERP.
Hier wird entschieden das bei ausgehenden Anrufen das
Referenz-ERP-System nicht Windows beauftragt sondert ein internes Referenz-ERP-VBA-Script
aufruft welches die Weiterverarbeitung übernimmt. Im Standardfalle ist dieses
wie oben zu sehen das Script AMIC_TAPI_CALL.
Der Kern des Scriptes sieht so aus:
'
--------------------------------------------------------------------
' Zusammenstellen der Aufruf-Parameter
'
--------------------------------------------------------------------
dim aufrufparameter
dim
linename
dim
linename2
dim
linenumber
dim automodus
linename = "ProCall"
linename2 = "TapiServer"
linenumber = Aeins.JVARS_Get( 9001 , "JVAR_TAPI_CALL
[...]


---

## Datenbank Trace

Datenbank Trace
Die Aeins-Trace-Funktionalitäten unterstützen eine
Analyse der aeins-seitig gegen die Datenbank verbrachten Datenbank-Anweisungen.
Zwar sind nicht durchgängig in allen Fällen alle tatsächlich verwendeten
Parameter ermittelbar, aber für einen ersten Überblick sind detaillierte Angaben
über Art und Beschaffenheit, sowie Laufzeitverhalten - auch ohne weitere
Entwicklungswerkzeuge – gegeben.

---

## Die Auswahlliste Formulararchiv-Anzeige

Die Auswahlliste
Formulararchiv-Anzeige
Diese Auswahlliste wird nach Auslösen der Aktion
"Archiv
anzeigen"
geöffnet.
Archiv-Anzeige ohne Vorschau
Die Felder sind mittels
"Variante"
in
den
Archiv-Ansicht-Definitionen
gegebenen
Möglichkeiten einzurichten.
Die Felder in der Standard-Auslieferung der
Archiv-Anzeige ohne Vorschau sind wie folgt:
Felder
KndNr
Zugeordnete Kundennummer
Beleg-Typ
Zugeordneter Textueller
      Beleg-Typ
Beleg-Nr
Zugeordnete Belegnummer
Beleg-Datum
Zugeordnetes Beleg-Datum
Archiv/Druck-Datum
Zugeordnetes Archivierungsdatum bzw.
      Druck-Datum
Beleg-Referenz
Zugeordnete
      Archiv-Referenz
Mnd
Zugeordneter Mandant
Herkunft
Zugeordnete Herkunft
Betreff
Zugeordneter Betreff
Autor
Zugeordneter Autor
Barcode
Zugeordneter Barcode
Bedienerklasse
Zugeordnete
      Bedienerklasse
Formularid
Zugeordnete Formularid
Fa-Id
Zugewiesene technische
      Formulararchiv-Id
Dateiname
Zugewiesener Dateiname
Funktionen
Senden an …
Senden an
Archiv anzeigen [
Strg
      F12
]
Archiv anzeigen
Ändern
Archiv-Stammdatenpfleger
Ansehen
Archiv-Stammdatenpfleger
Hinzufügen
Archiv – Dokumente
      hinzufügen
Barcode zuweisen …
Archiv Barcode
Drucken
Es
      wird ein Druck des Archiv-Inhaltes über das Windows-System
      eingeleitet.
Technische Erläuterung:
Dabei wird von Referenz-ERP eine temporäre
      Datei im Temp-Verzeichnis erstellt und diese dem Windows-System zum
      Drucken über die Methode „print“ übergeben.
Über
      Systemsteuerung > Programme > Standardprogramme können Sie mittels
auf
      Ihrem System nachverfolgen welche Applikation mit der Extension verbunden
      ist.
Ansicht Information
Diese Funktion teilt in einem Dialog
      mit, welche
Archiv-Ansicht-Definition
zum Aufbau
      dieser Auswahlliste verwendet wurde.
Archiv Eintrag löschen
Archiveinträge
      löschen
Neue Archiv-Anzeige mit Vorschau
Ist für die Ansicht der „Vorschau“-Modus aktiviert,
dann gestaltet sich die „Archiv-Anzeige“ als Dialog in neuer Optik mit n
[...]


---

## Dokumentenverwaltung Filter

Dokumentenverwaltung Filter
Mit Hilfe der Filter lassen sich gängige Recherchen
durchführen und sitzungsübergreifend speichern.
Jeder Filter wird mit entsprechendem „Abhack-Kästchen“
aktiviert bzw. deaktiviert.
Der Filter selber wird mittels
aktiviert.
Filter
Volltextrecherche
Siehe
Volltext
      Recherche
Die
      Dokumente werden zusätzlich hinsichtlich der
      Volltext-Recherche-Möglichkeiten geprüft.
Kundennummer
Von
      – Bis
Wird
      ein Feld nicht ausgefüllt wird jeweils die kleinste bzw. größte
      Kundennummer angenommen.
Möchte man z.B. ausschließlich nach
      dem Kunden 12000 suchen müssen beide Felder mit 12000 gefüllt
      sein.
Archivdatum Tage zurück
Es
      werden dann nur die Archiv-Einträge berücksichtigt deren Archiv/Druckdatum
      um so viele Tage zurückliegt.
Datum
Von
      - Bis
Man
      kann Monat bzw. Jahr weglassen, dann wird dafür das aktuelle
      angenommen.
Für
      das jeweils aktuelle Tagesdatum kann man HEUTE bzw TODAY
      einsetzen.

---

## Formulardruckpositionen

Formulardruckpositionen
Nummer
Bezeichnung
1
Festtext
2
SQL
      Statement
3
Text-Variable
22
Bitmap aus Datei/Archiv
Angabe eines Pfades auf eine
      bmp-Datei.
Angabe einer JVAR aus der zur
      Laufzeit der Pfad ermittelt wird. Die Angabe erfolgt über JVAR,
      Owner.
Achten Sie hierbei das der Pfad so
      gewählt sein muss das die in Frage kommenden Referenz-ERP-Clienten diesen auch
      erreichen können.
In
      jedem Falle wird die Extension des so erhaltenen „Pfades“ bestimmt.
Ist
      diese nicht „bmp“, dann wird die Angabe aus „Beleg-Referenz“ des Archives
      interpretiert und dort mit der Belegklasse 8800 recherchiert
. Das dort
      hinterlegte bmp-Dokument wird dann gedruckt.
Kommt es im Rahmen der
      Druckaufbereitung der Bitmap zu Problemen, dann erfolgt ein
      Fehlerprotokoll/Systemmeldungs-Eintrag und es wird eine Ersatzgrafik aus
      dem Aeins\bin-Verzeichnis bitmapnotavailable.bmp gezogen. Dieses Verfahren
      soll helfen durch optische Kontrolle der Belege solche Umstände
      aufzudecken.
In
      der Spalte „Text“ ist F3 möglich, dieses öffnet die Dokumenten Verwaltung
      für Dokumente mit der Belegklasse 8800. Sie können dort einen Eintrag
      auswählen und die Belegreferenz wird dann in das Feld
      übernommen.
Sie haben innerhalb der
      Dokumenten-Verwaltung die Möglichkeit eine Bitmap z.B. per Drag&Drop
      hinzufügen und auch die Referenz-Nummer entsprechend zu gestalten. Im
      Idealfall ist diese Referenznummer angegeben und eindeutig innerhalb der
      Belegklasse 8800.
36
JVars-Text-Variable
Bietet die Möglichkeit den Inhalt
      von JVARS ausdrucken.
Angabe ist
NameDerJVar,OwnerDerJVar
(Angabe also durch Komma
      getrennt)
41
Bitmap aus Etidr
Übernimmt eine durch den Branchen-ERP
      Etikettendruck erzeugte Bitmap in den Windowsdruck.
Der
      Name des Branchen-ERP Etikettendruck ist unter Text einzutragen.
Unter Direktsprung ETIDR ist ein
      gleichlautender Branchen-ERP Etikettendruck e
[...]


---

## Funktionen in Anschriften

Funktionen in Anschriften
Bei der Erfassung der Postleitzahl wird automatisch
geprüft, ob sie bereits vorhanden ist. Wenn ja, wird der Ort vorgeschlagen.
Darüber hinaus besteht die Möglichkeit, mittels
F3
nach Postleitzahl oder Ort zu
suchen.

---

## Interne Fehlercodes vom Branchen-ERP Etikettendruck

Interne
Fehlercodes vom Branchen-ERP Etikettendruck
-1
Es wurde eine Funktion mit einem Jobhandle als
      Parameter aufgerufen, das nicht mit
LlJob-Open
() erzeugt
      wurde.
-2
Pro
      Applikation darf nur ein Designerfenster geöffnet sein,
Sie haben versucht, ein zweites zu
      öffnen
-3
Einer Funktion, die den Objekttyp
      als Parameter benötigt, wurde ein ungültiger Typ übergeben.
-4
Es
      wurde eine Druckfunktion aufgerufen, obwohl noch kein Druckjob gestartet
      wurde.
-5
LlPrintSetBoxText()
wurde aufgerufen, obwohl der
      Druckjob nicht mit
LlPrintWithBoxStart12()
geöffnet
      wurde.
-7
LlPrint[G|S]etOption[String](),
      LlPrintResetProjectState()
.
Der Druckjob ist noch nicht
      gestartet
-10
LlPrint[WithBox]Start()
: Es existiert kein Objekt mit dem
      angegebenen Dateinamen.
-11
LlPrint[WithBox]Start()
: Druckerjob konnte nicht gestartet
      werden, da kein Drucker-Device geöffnet werden konnte.
-12
Während des Druckens trat ein Fehler
      auf. Häufigste Ursache:
Druckspooler voll, bzw. der vom
      Druckspooler benötigte Platz ist auf dem Laufwerk auf das TEMP zeigt nicht
      mehr vorhanden (Pro Seite kann je nach Druckauflösung und verwendeter
      Grafik ein Platzbedarf von einigen MB entstehen. Abhilfe schafft meist
      auch die Einstellung des Direktdrucks ohne Spooler). Mögliche Ursache bei
      Direktdruck: allg. Druckerfehler, Papierstau, etc.
-13
Beim
      Exportieren ist ein Fehler aufgetreten (z.B. keine Zugriffsrechte auf
      Zielpfad, zu exportierende Datei schon vorhanden und
      schreibgeschützt,...)
-14
Diese DLL-Version benötigt Visual
      Basic.
-15
Bei
      Druckoptionen: kein Drucker verfügbar.
-16
Preview-Funktionen: bei
LlPrint[WithBox]Start()
wurde kein Preview-Mode
      eingestellt.
-17
LlPreviewDisplay()
: Keine Preview-Dateien
      gefunden.
-18
NULL
      Zeiger als Parameter ist hier nicht gestattet, möglicherweise auch andere
      Parameter-Fehler. Bitte
[...]


---

## Mittelwert bilden

Mittelwert bilden
Wählen Sie mehrere Laborsätze einer Partie aus, deren
Mittelwert Sie bilden möchten und wählen Sie die Funktion „Mittelwert“ an.
Es wird mit Hilfe der hinterlegten Prozedur ein
Mittelwert gebildet, der in einen neuen Datensatz geschrieben wird, der Ihnen
dann angezeigt wird.
Sie haben nun noch die Möglichkeit, manuelle
Korrekturen an den Werten vorzunehmen.
Verlassen Sie die Erfassungsmaske mit der ESC-Taste.
Wenn Sie die Daten speichern wollen, beantworten Sie
den nachfolgenden Dialog mit „Ja“.

---

## Speicher-Pfad für signierte PDF-Dokumente ermitteln:

Speicher-Pfad für signierte
PDF-Dokumente ermitteln:
1.
Referenz-ERP starten.
2.
Direktsprung [FAM] ausführen und danach Reiter „Sonstiges“ auswählen.
3.
Das im Feld „Signatur-Importpfad“ genannte Verzeichnis ist der Speicherpfad für
die signierten PDF-Dokumente.

---

## Unstimmigkeit zwischen Zahlungssätzen und Zahlungsmitteln

Unstimmigkeit zwischen Zahlungssätzen und Zahlungsmitteln
Zu jedem Zahlungssatz (AcashBelgZhlg) einer unbaren
Zahlungsart (Zahlungsarten 2, 3, 4, 5) muss ein Zahlungsmittelsatz
(AcashBelgZami) existieren.
Zur Bereinigung gibt es keine maschinelle
Unterstützung. Nachfolgende SQL Ausdrücke helfen, Fehlern auf die Spur zu
kommen. Fehler werden individuell berichtigt.
Fehlende oder abweichende Zahlungsmittel:
select
ZahlKs, ZahlKsi,
today(*)
      Belegdatumdatum, ZahlBelegNr,
(select zamibetrag from
      acashbelgzami where zamiidnr = zahlzamiidnr) zamibetrag,
(select
      FormLstBezeich from Formatlist
where FormLstKennung = 'AcashBelegAr' and FormLstWert = zahlBelegart
and SprachNummer =0) BelegArtBez,
zahlbelegart
      Belegart,
zahlbetrag
      BelegSummeBrutto, filialnummer, Zahlkonto , *
from acashbelgzhlg z
where zahlart in (2,3,4,5) and
      (zamibetrag is null or zamibetrag != zahlbetrag)
Fehlende Zahlungssätze zu Zahlungsmitteln:
select
ZamiKs as
      BelegKs, ZamiKsi as BelegKsi,
Zamidatum as BelegDatumDatum,ZamiBelegNr as BelegNr,
(select
      FormLstBezeich from Formatlist
where FormLstKennung = 'ZamiArt' and FormLstWert = ZamiArt
and SprachNummer =0) BelegArtBez,
ZamiArt as
      Belegart,
zamibetrag
      BelegSummeBrutto, filialnummer
from acashbelgzami z
where zamiidnr not in
      (select zahlzamiidnr from acashbelgzhlg)
order by FilialNummer, BelegKs,
      BelegKsi, Belegart

---

## Verwendungszweck definieren

Verwendungszweck definieren
Für den Verwendungszweck im SEPA-Verfahren stehen nur
noch maximal 140 Zeichen zur Verfügung. Diese können mittels einer
Datenbankprozedur, die pro
Zahlungsart
unterschiedlich sein
kann, individuell gestaltet werden. Wird im Pfleger für Zahlungsarten keine
Datenbankprozedur hinterlegt, so wird der Verwendungszweck sowie von Branchen-ERP
vorgegeben generiert. Dabei wird die Belegnummer - bei Eingangsrechnung,
Eingangsgutschrift, Rohwarenzugängen sowie allen Zahlungsausgängen die
Referenznummer -, das Belegdatum und der Rechnungsbetrag ausgegeben. Werden die
140 Zeichen überschritten, so erscheint der Text „Ausgl. nnn Belege laut Avise
zzz“ und eine Avise wird für diesen Zahlungsbeleg gedruckt. Dabei ist nnn die
Anzahl der Belege und zzz eine eindeutige Nummer (die ZAHLUNGSID) auf die man
sich beziehen kann.
Die von Branchen-ERP vorgegebene Art und Weise der
Verarbeitung des Verwendungszwecks kann bei aktivem Steuerungsparameter
„DTA-Textänderung aktiv“ geringfügig beeinflusst werden. Es steht dann die
Funktion „
Text/Avise erfassen
“ im
DTA zur Verfügung. Dort kann man einen Festtext hinterlegen, der entweder an
Stelle des Verwendungszwecks genommen werden kann oder als Überschrift vor dem
erzeugten Text erscheinen kann. Hier kann auch beeinflusst werden, wie die Avise
gedruckt werden soll: „Nie“, „immer“ oder „bei Bedarf“. Standarteinstellung ist
„bei Bedarf“.

---

## Vorgangskopf

Vorgangskopf
Die Vorgangserfassung am Beispiel der Rechnung wird
entweder über das Menüsystem, hier über den Anwahlpunkt Rechnungserfassung,
mittels Direktsprung
[REE]
oder über den Anwahlpunkt
Rechnungsbearbeitung
[REB]
und dann mit Taste
F8
aufgerufen. Es erscheint eine Erfassungsmaske, in deren linker Hälfte die
erforderlichen Informationen des Vorgangs abgefragt werden, oben rechts werden
Informationen zum Kunden angezeigt, unten rechts werden
Bearbeitungsfunktionen
zur
Verfügung gestellt, um die weitere Verarbeitung des Vorgangs zu steuern.
Hervorzuheben sind hier insbesondere Funktionen zur Aktualisierung von
Anschriften oder zur Verzweigung in den Positionsteil.
Zusätzlich sei hier noch einmal darauf hingewiesen,
dass das Parametersystem in Referenz-ERP es erlaubt,
Abläufe zu verändern
optische Darstellungen anzupassen
abweichende Logiken zu verwenden.
Deshalb kann sich der Ablauf einer konkreten Anwendung
vom nachfolgend beschriebenen Ablauf unterscheiden!

---

## Zählung

Zählung
Bei der Zählung ist in der Erfassungsmaske zu jedem
Zahlungsmittel die vorhandene Menge einzugeben.
Die Mengenstückelung ist in der Basisdatenbank in Euro
Stückelung vorgegeben. Sie kann in den
Kasseneinstellungen
verändert werden.

---

