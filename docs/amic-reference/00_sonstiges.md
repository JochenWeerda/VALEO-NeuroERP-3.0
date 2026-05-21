# Sonstiges & Allgemein — Referenz-ERP Referenzwissen

> 1185 Seiten ohne Domänenzuordnung

## Allgemein

Allgemein
Auf diesem Tabs werden gezielt Änderungen eines
Attributs von Datensätzen gesucht, die durch Angabe von mindestens einem
Schlüsselattribut-Wert näher spezifiziert werden.
Die maximale Anzahl der Datensätze, die in die
Auswahlliste zu übernehmen sind, wie auch der zu untersuchende Zeitraum
bezüglich des Logfile-Archivierungsdatums kann angegeben werden. Die Suche
erfolgt grundsätzlich beginnend mit dem Bis-Datum hin zum Ab-Datum und bricht
bei Erreichen der Maximalzahl der Ergebnissätze ab.
Die Angabe des auszuwertenden Attributnamens wird
durch eine Itembox unterstützt, die auch über eine Auflistungsvariante nach
Relationsnamen verfügt und nach Auswahl des Attributs auch den zugehörigen
Relationsnamen in das entsprechende Maskenfeld schreibt.
Existieren Attribute mit dem angegeben Namen in
mehreren Relationen, so kann diese, ebenfalls unterstützt durch eine
entsprechende Itembox, angegeben werden.
Ist die Relation angegeben, so werden auf der Maske
die zugehörigen
[...]


---

## Struktur

Struktur

---

## Schlüsselwörter im SQL-Text

Schlüsselwörter im SQL-Text
Die hier aufgeführten Schüsselwörter gelten für die
Auswahlliste im alten Design(AW 1.0), die im neuen Design(AW 2.0) und die
F3-Auswahl(IB). Teilweise stehen Schlüsselwort nicht in jedem Teil zur Verfügung
(siehe Hinweis). Alle Schlüsselwörter müssen großgeschrieben werden.
Gütigkeitsbereich
Beschreibung
VAR
Mithilfe von VAR können
      zusammengesetzte Inhalte oder Formeln für das SQL-Statement vordefiniert
      werden.
VAR
Name
A.AdressName+', '+A.AdressVorname
FIELD
      Nummer,S.KundNummer,I4,8
FIELD Name,
Name
,char,20
SQL select :FIELDS from
      Kundenstamm s join Anschriftstamm a on
      a.adressid=s.adressidhauptadr
Das SQL wird erweitert
      auf:
Select S.KUNDNUMMER,A.AdressName+', '+A.AdressVorname
NAME
, from Kundenstamm s join
      Anschriftstamm a on a.adressid=s.adressidhauptadr
FIELD
Beschreibung einer Spalte. Die
      ersten vier Parameter müssen immer in einer festen Reihenfolge angegeben
      werden:
1)   Spaltenüber
[...]


---

## Tree-Eigenschaften

Tree-Eigenschaften
Frozen Columns
Dieser Eintrag kann in zwei verschiedenen
Zusammenhängen verwendet werden:
•
Der Wert Frozen Columns bedeutet im Regelfall, dass n Spalten
festgehalten werden, wenn man über die Spalten scrollt. Z.B. beim Eintrag von 2
wird werden die ersten beiden Spalten eingefroren so das sie bei der Betätigung
des Scroll Balkens sichtbar bleiben
So können Sie die
Übersichtlichkeit einer Anzeige erhöhen, wenn z.B. in der ersten Spalte ein Name
und in den weiteren Spalten scrollbar Adressen und weitere Daten stehen.
•
Der Wert Frozen Columns wird im Zusammenhang mit der Darstellung von
Baumstrukturen verwendet, um anzugeben, bis zu welchem Level der angezeigte Baum
geöffnet sein soll. Alle Werte eines höheren Levels werden als „eingerollte“
Information dargestellt. Enthält die Ergebnismenge der anzeigenden Prozedur ein
Feld des Namens „GDS_Frozen_Cols“, so wird diese Voreinstellung nicht verwendet,
sondern eine Zeilenindividuelle Darstellung benutzt.
NoCha
[...]


---

## Archiv: Drag- und Drop, Behandlung Anlagen und Images in der Mail

Archiv: Drag- und Drop, Behandlung Anlagen und Images in der Mail
1) Beim Drag- und Drop von Outlook-Anhängen werden nun
zusätzlich Bilder die mit "Image" anfangen, darauf folgend eine Zahl mit der
Extension ".Png" auch die Formate ".Jpg", ".Jpeg", ".Tif", ".Tiff" und ".Bmp"
vom Import ins Archiv ausgeschlossen. 2) Es ist uns zur Zeit technisch nicht
möglich bei mehreren Anlagen eventuelle Auswahlen in der Outlook-Gui durch den
User zu ermitteln. Outlook überträgt alle Anlagen und zusätzlich Bilder im
Mailbody (sonstige + Signatur-Bilder). Die Bilder aus der Mail sind unerwünscht
und werden daher durch Maßnahme 1 ausgeschlossen. 3) Diese Filterung wird nun
auch beim E-Mail Connector berücksichtigt.
Releasenote Kategorie:
Ticket: 714072[32781]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: alle Archiv-Varianten
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32781, 714072

---

## Makro: Checkbox "Profiler" von Maske entfernt

Makro: Checkbox "Profiler" von Maske entfernt
In der Anwendung [MAKRO] wurde die Checkbox "Profiler"
auf der Pascal-Script Maske entfernt.
Releasenote Kategorie:
Ticket: 715125[32787]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [MAKRO]
Variante: Makroprogramme
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32787, 715125

---

## Branchen-ERP-Etikettendruck Versionserhöhung

Branchen-ERP-Etikettendruck Versionserhöhung
Die Version des Reporting-Tools, das vom
Branchen-ERP-Etikettendruck verwendet wird, wurde auf Version 27 hochgezogen.  Der
Vertreiber dieser Software empfiehlt alle Vorlagen und Projekte sorgfältig
zu prüfen, da Verbesserungen zum Teil auch  bedeuten, dass bestimmte
Verfahren auf einem anderen Weg umgesetzt worden sind und  dann nur eine
hohe Annäherung aber keine 100%ige Identität erreicht werden kann.
Releasenote Kategorie:
Ticket: 0[32798]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: ETIDR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32798, 0

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.70.196 aktualisiert.
Releasenote Kategorie:
Ticket: 0[32797]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32797, 0

---

## Reaktivierung von Quellbelegen bei Erstellung des Stornobelegs

Reaktivierung von Quellbelegen bei Erstellung des Stornobelegs
In der Formularzuordnung [FRZ] auf dem Tab-Reiter
Allgemein gibt es jetzt die Einstellungsmöglichkeit: "Quellbeleg freigeben bei
Stornobeleg". Eingestellt werden kann: Ja - Der Quellbeleg wird immer
freigegeben Nein - Der Quellbeleg wird nie freigegeben Abfrage - Der Quellbeleg
wird freigegeben, wenn dies auf der Umwandelmaske eingestellt wird.
Achtung: Auf der Umwandelmaske ist die Einstellung immer zu sehen, auch wenn
diese nicht ausgewertet wird, da in [FRZ] ein festes Verhalten hinterlegt
ist.  Hinweis: Der SPA 987 ("Quellbelegreaktivierung bei Stornieren/Löschen
von Warebelegen (BA,AG,BS,AU,LI,RE)-") bleibt hiervon unberührt.
Releasenote Kategorie:
Ticket: 714299[32857]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Vorgangsbearbeitung
Variante: Vorgangsunterklassen
Funktion/Report: Storno mit Beleg
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 32857, 714299

---

## Großer HTML-Body eBeleg

Großer HTML-Body eBeleg
Es gab ein Problem mit größeren HTML-Body-Dateien im
eBeleg. Diese wurden ab einer Länge von 5kB abgeschnitten.  Dieses Problem
wurde behoben
Releasenote Kategorie:
Ticket: 714785[32856]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: Formularzuordnung
Variante: Standard
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2211.9, 32856, 714785

---

## Vorgangsansicht: Makros

Vorgangsansicht: Makros
Eröffnet man einen Beleg im Ansichtsmodus (F6), werden
die Makros nun auch bei der SPA-Einstellung ( SPA 862 "Makros bei
Ansicht eines Vorgangs ausführen") "Immer" ausgeführt.  Bisher wurden die
Makros nur bei der SPA-Einstellung "AIS" und "Vorgang" ausgeführt.
Releasenote Kategorie:
Ticket: 714214[32859]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: Ansehen
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 32859, 714214

---

## TSE-Ansteuerung

TSE-Ansteuerung
Die Ansteuerung der TSE zur Zeit-Setzung und des
inaktiven CTSS-Interface wurde überarbeitet. (Code: 4098,
4180)
Releasenote Kategorie:
Ticket: 714192[32886]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: BVVE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32886, 714192

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.70.198 aktualisiert.
Releasenote Kategorie:
Ticket: 0[32879]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32879, 0

---

## Excelimport [EXCELI]

Excelimport [EXCELI]
Seit der Version 8.3.2202.7 wurde beim Excelimport
[EXCELI] von .xlsx - und .xlsm- Dateien im SQL-Text der erstellten Variante ein
"SELECT :FIELDS" verwendet. Diese Änderung wurde zurückgebaut. Jetzt werden im
SQL-Text wieder alle Spalten einzeln selektiert. Des Weiteren werden
"long-varchar" - Spalten im SQL-Text als char(255) zurückgegeben.
Releasenote Kategorie:
Ticket: 714258[32891]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: Excel-Import
Variante: -
Funktion/Report: Variante aktualisieren
Weitere Informationen
Tags:
Releasenote, 8.3.2210.20, 32891, 714258

---

## Druck von Vorgangstexten basierend auf Dokumenten

Druck von Vorgangstexten basierend auf Dokumenten
Der Druck von Textzeilen erfolgt nun
seitengerecht.
Releasenote Kategorie:
Ticket: 712500[32927]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: -
Variante: -
Funktion/Report: Vorgangsdruck
Weitere Informationen
Tags:
Releasenote, 8.3.2211.9, 32927, 712500

---

## OLAP Funktion entfernt

OLAP Funktion entfernt
In OLAP wurde die Funktion "Titel exportieren"
entfernt.
Releasenote Kategorie:
Ticket: 715120[32979]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: -
Variante: -
Funktion/Report: OLAP
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32979, 715120

---

## Windows 11 /Windows Server 2022

Windows 11 /Windows Server 2022
Referenz-ERP ist nun für Windows 11 freigegeben. Referenz-ERP ist
nun für Windows Server 2022 freigegeben.
Releasenote Kategorie:
Ticket: 715832[33016]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33016, 715832

---

## Belegfluss

Belegfluss
Der Belegfluss wurde um ein Feld für die Belegart (nur
Finanzbuchhaltung) erweitert. Für die Belegart SO-Belege wird das
Soll/Haben-Kennzeichen ausgewertet.  Achtung: Der Datenbanktyp des Feldes
"SollHaben" wurde von "CHAR" auf "integer" geändert. Private Funktionen, die das
Feld "SollHaben" bereits verwenden, müssen angepasst werden.
Releasenote Kategorie:
Ticket: 715736[33022]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Archiv Belegfluss
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33022, 715736

---

## Referenz-ERP.Libary-Viewer

Referenz-ERP.Libary-Viewer
Patches können ab dieser Version über den
Referenz-ERP.Libary-Viewer eingespielt werden. Eine Anleitung befindet sich in der
verlinkten Hilfe.
Releasenote Kategorie:
Ticket: 716363[33086]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: -
Variante: -
Funktion/Report: [PATCH]
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33086, 716363

---

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

## Auswahlliste 2.0 im Dialogmodus

Auswahlliste 2.0 im Dialogmodus
Wurde die Auswahlliste im Dialogmodus aufgerufen, so
wurde die Breite immer auf die Gesamtbreite des Bildschirms festgelegt. Jetzt
wird sie auf die Referenz-ERP Standard-Breite begrenzt.
Releasenote Kategorie:
Ticket: 0[33156]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2212.23, 33156, 0

---

## Neue Elster-Version

Neue Elster-Version
Es wurde die Elster-Version 37.2.6 (gültig für
das Jahr 2023) in Referenz-ERP integriert. In dieser Version sind zwei neue Kennzahlen
(87 und 90) für den Nullsteuersatz für Photovoltaik-Anlagen enthalten.
Releasenote Kategorie:
Ticket: 717068[33219]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: UVA, UVZM
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33219, 717068

---

## Office 365 Online-Exchange-Authentifizierung

Office 365 Online-Exchange-Authentifizierung
Die Module E-Beleg, Tammo und Email-Connector wurde
auf das moderne Authentifizierungsverfahren Online-Exchange umgestellt.
Releasenote Kategorie:
Ticket: 716145[33235]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: E-Beleg und E-Mail-Connector
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33235, 716145

---

## CO2-Kostenaufteilung

CO2-Kostenaufteilung
Das neue Modul zur CO2-Kostenaufteilung wurde
fertiggestellt.
Releasenote Kategorie:
Ticket: 717732[33255]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: CO2-Kostenaufteilung
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33255, 717732

---

## Referenz-ERP Temporäre Dateien

Referenz-ERP Temporäre Dateien
Referenz-ERP schreibt seine temporären Daten jetzt gesammelt
in das Unterverzeichnis "Referenz-ERP" im Temp-Verzeichnis.
Releasenote Kategorie:
Ticket: 716156[33257]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Basis-Funktion
Variante: -
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33257, 716156

---

## FehlProtBereich erweitert

FehlProtBereich erweitert
Die Tabelle Fehlerprotokoll und die zuliefernden
Prozeduren lassen jetzt einen Fehlerprotokollbereich von 255 statt 30 Zeichen
zu
Releasenote Kategorie:
Ticket: 719179[33334]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Fehlerprotokoll
Variante: Systemhinweise
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33334, 719179

---

## Bankleitzahlen aktualisieren

Bankleitzahlen aktualisieren
Für die Funktion Banken aktualisieren stehen die Daten
der Deutschen Bundesbank gültig vom 05.12.2022 bis 04.03.2023 zur
Verfügung.
Releasenote Kategorie:
Ticket: 719823[33425]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: BNK
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2302.17, 33425, 719823

---

## Auswahlliste: Tastatursteuerung

Auswahlliste: Tastatursteuerung
Wenn der Fokus auf der Filterzeile steht und man geht
mit Pfeiltaste nach unten in den Auswahlbereich wird die erste Zeile nun nicht
mehr automatisch markiert.
Releasenote Kategorie:
Ticket: 719706[33426]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33426, 719706

---

## Umwandlung mit abweichender Belegnummer

Umwandlung mit abweichender Belegnummer
Bei Umwandlung von Belegen unter Angabe einer
abweichenden Belegnummer wurden die Informationen über den vorherigen Beleg u.U.
nicht korrekt mitgezogen. Dies ist nun behoben.
Releasenote Kategorie:
Ticket: 720096[33460]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: Umwandlung
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33460, 720096

---

## Druck Tse-QR-Code

Druck Tse-QR-Code
Der Tse-QR-Code wurde nicht in der gewünschten Größe
ausgedruckt. Die Größe des QR-Codes kann jetzt im Formular über das Feld Länge
skaliert werden.
Releasenote Kategorie:
Ticket: 715707[33463]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Marktkasse
Variante: BVVE
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2302.17, 33463, 715707

---

## Elsterpatch: Report

Elsterpatch: Report
Der Report im Elsterpatch wurde für die Kennzahl
50 angepasst.
Releasenote Kategorie:
Ticket: 720552[33471]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33471, 720552

---

## Vermailung: Email erneut versenden

Vermailung: Email erneut versenden
Unter [MAIL] wurde die Funktion "Email ändern"
umbenannt in "Email erneut versenden"
Releasenote Kategorie:
Ticket: 719301[33468]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Vermailung
Variante: -
Funktion/Report: Email erneut versenden
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33468, 719301

---

## Einzelbeleganzeige: Archiv

Einzelbeleganzeige: Archiv
In dem Archiv der Einzelbeleganzeige wurden seit der
Version 8.3.2211.30 die archivierten Warenwirtschaftsbelege beim
Zahlungspflichtigen nicht mehr angezeigt. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 719393[33473]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Einzelbeleganzeige
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33473, 719393

---

## AIS-Makro in C# neues Interface

AIS-Makro in C# neues Interface
Das CSMakro-Interface IAISMakro_V005 war nicht
nutzbar. Das ist nun behoben.
Releasenote Kategorie:
Ticket: 720492[33548]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: C#-Makro
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33548, 720492

---

## Archiv: Drag&Drop von Zustellungs- bzw. Fehlerberichten

Archiv: Drag&Drop von Zustellungs- bzw. Fehlerberichten
Beim Hinzufügen von Outlookelementen per Drag&Drop
kam es bei Zustellungs- bzw. Fehlerberichten zu Problemen.  Die
Ursache hierfür war, dass Outlook diese Elemente nicht als Mail sondern als
Report Items behandelt.   Nun ist es auch möglich, diese Elemente per
Drag&Drop zu archivieren.
Releasenote Kategorie:
Ticket: 720944[33590]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: Dokumentenverwaltung
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33590, 720944

---

## Archivanzeige: Einzelbeleganzeige

Archivanzeige: Einzelbeleganzeige
Die Performance des Archivs in der Einzelbeleganzeige
wurde verbessert.
Releasenote Kategorie:
Ticket: 718797[33593]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33593, 718797

---

## neues Modul: Dashboard

neues Modul: Dashboard
Es wurde das Modul "Dashboard" in Referenz-ERP
integriert.
Releasenote Kategorie:
Ticket: 716438[33598]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Dashboard
Variante: -
Funktion/Report: [DASH]
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33598, 716438

---

## ASCII-Druck deutsche Sonderzeichen

ASCII-Druck deutsche Sonderzeichen
Beim ASCII-Druck (speziell OKI-Nadeldrucker) werden
die deutschen Sonderzeichen (hier Umlaute und ß) dargestellt.
Releasenote Kategorie:
Ticket: 722009[33636]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: ASCII-Druck auf OKI-Nadeldrucker
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33636, 722009

---

## Auswahlliste Menüband

Auswahlliste Menüband
Auf dem Menüband werden jetzt die Funktionstasten mit
angezeigt. Auf dem Darstellungsregister kann man mit dem Button "Funktionstasten
An/Aus" die Anzeige der Tasten aktivieren und deaktivieren.  Bei einem
Rechtsklick mit der Maus (Kontextmenü) werden nun die Funktionen ausgegraut
angezeigt, welche nicht ausführbar sind, aber dem Anwender grundsätzlich zur
Verfügung stehen.
Releasenote Kategorie:
Ticket: 0[33652]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33652, 0

---

## Dashboard: Erweiterung

Dashboard: Erweiterung
Im Tortendiagramm besteht jetzt die Möglichkeit
kleinere Tortenstücke zu einem einzelnen Tortenstück ("Sonstige")
zusammenzufassen.
Releasenote Kategorie:
Ticket: 716438[33658]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: [DASH]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33658, 716438

---

## Dashboard: Erweiterung

Dashboard: Erweiterung
Das Dashboard wurde um die Darstellungsart
"Tachometer" erweitert.
Releasenote Kategorie:
Ticket: 716438[33660]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: [DASH]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33660, 716438

---

## Dashboard: Erweiterung

Dashboard: Erweiterung
Im Tortendiagramm besteht jetzt die Möglichkeit die
Klick-Funktion über die Legende auszuführen.
Releasenote Kategorie:
Ticket: 716438[33662]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: [DASH]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33662, 716438

---

## Auswahlliste 2.0

Auswahlliste 2.0
Die Tasten + und - auf dem Nummernblock werden in der
Auswahlliste zum auf- und zuklappen der Gruppen verwendet. Das führte dazu, dass
in der Filterzeile die Zeichen nicht über den Nummernblock eingebbar
waren.
Releasenote Kategorie:
Ticket: 722484[33689]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2304.28, 33689, 722484

---

## Quellbeleg-Freigabe bei Stornierung von kopierten Vorgängen

Quellbeleg-Freigabe bei Stornierung von kopierten Vorgängen
Beim Stornieren/Löschen (F7) bzw. beim Stornieren mit
Stornobeleg konnte es zu Problemen mit der Quellbeleg-Freigabe
kommen.  Dies wurde behoben.
Releasenote Kategorie:
Ticket: 720685[33713]
Version: 8.3.2305.26
Datum: 26.05.2023
Anwendung: ERB,REB,LIB,ELB,AUB,BSB
Variante: alle
Funktion/Report: Stornieren/Löschen, Erstellen von
Stornobelegen
Weitere Informationen
Tags:
Releasenote, 8.3.2305.26, 33713, 720685

---

## Wareo: Vorgangsleichen löschen

Wareo: Vorgangsleichen löschen
In der Anwendung Warenreorganisation [WAREO] wurde die
Funktion "Vorgangsleichen entfernen mit Nummernfreigabe" entfernt. Die Funktion
"Leichen in der Ware beseitigen" wurde umbenannt in "Fehlerhafte Vorgänge aus
der Ware entf.". Das Löschen von fehlerhaften Vorgängen wird jetzt in der
Tabelle WareoProtokoll protokolliert.
Releasenote Kategorie:
Ticket: 717902[33722]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Wareo
Variante: --
Funktion/Report: Problemfälle VorgReservierung,
Fehlerhafte Vorgänge aus der Ware entf.
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33722, 717902

---

## Rücklasten

Rücklasten
Es wurde ein vereinfachtes Verfahren bereitgestellt,
um Rücklastenschriften bei Nichteinlösung einer Zahlung von der Bank zu
erstellen. Dazu ruft man den Zahlungsbeleg in der Einzelbeleganzeige in der
Anwendung Kontoinformationen [KOI] auf, markiert die betreffende Position und
führt für die  Funktion Rücklastschrift aus.
Releasenote Kategorie:
Ticket: 723015[33741]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: KOI, OPV, FISV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33741, 723015

---

## Kassensystem: Marktkasse Arbeitsspeicher Auslastung

Kassensystem: Marktkasse Arbeitsspeicher Auslastung
Bei der 64-Bit Version kam es zur vollständigen
Auslastung des virtuellen Arbeitsspeichers, was zu Programmabstürzen führte.
Dieses wurde nun behoben.
Releasenote Kategorie:
Ticket: 722269[33823]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: BVVE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33823, 722269

---

## Währungskurse

Währungskurse
Die Erstellung des Events für die automatische
Aktualisierung der Währungskurse wurde auf eine neue Technologie umgestellt.
Bestehende Events müssen ggf. neu erstellt werden, wenn es Probleme bei der
Aktualisierung der Währungskurse geben sollte.
Releasenote Kategorie:
Ticket: 723138[33806]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Währungskurse
Variante: -
Funktion/Report: Währungskurse Event
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33806, 723138

---

## Gebindebehandlung bei Mengenkorrektursperre per Arbeitsregel

Gebindebehandlung bei Mengenkorrektursperre per Arbeitsregel
Bei der Korrektur von Vorgängen mit einer zugeordneten
Arbeitsregel, die eine Mengenkorrektur-Sperre enthält, konnten Gebinde-Angaben
der Warenpositionen geändert werden. Dieses wurde nun derart überarbeitet, dass
eine Änderung in diesem Fall nicht mehr möglich ist.
Releasenote Kategorie:
Ticket: 723393[33840]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Vorgangsbearbeitung
Variante: alle
Funktion/Report: Korrektur
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33840, 723393

---

## Vorgangsnachverfolgung: Datenanzeige

Vorgangsnachverfolgung: Datenanzeige
Die Verwendung der Vorgangsnachverfolgung [VNV]
funktionierte nur dann korrekt, wenn das Einstiegsverhalten der Variante im
Bereichsfilter auf "Daten sofort anzeigen" stand. Das Problem wurde
behoben.  Bis zur Installation der neuen Version bitte das zentrale
Einstiegsverhalten auf "Daten sofort anzeigen" stellen.
Releasenote Kategorie:
Ticket: 723328[33862]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Vorgangsnachverfolgung
Variante: -
Funktion/Report: VNV
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33862, 723328

---

## Neue Version Android-Scannerapp

Neue Version Android-Scannerapp
Es wurde eine neue Version der Android-Scannerapp
bereitgestellt.  Bitte vereinbaren Sie einen Update-Termin.
Releasenote Kategorie:
Ticket: 0[33865]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: Scannerapp
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33865, 0

---

## PDF-Verarbeitung

PDF-Verarbeitung
Die Bibliothek, die u.a. zur Erzeugung von
PDF-Dokumenten eingesetzt wird, ist auf Version DynaForms 4.0.74.217
Professional angehoben worden.  Diese Version erzeugt u.a. nicht länger
interne Links auf die Hersteller-URL, da diese u.U. zu Problemen mit
Viren-Scanner führen konnten.
Releasenote Kategorie:
Ticket: 724275[33909]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33909, 724275

---

## Vorgang senden an

Vorgang senden an
Die Funktion "Vorgang Senden an" wurde für die 64-Bit
Version reaktiviert.
Releasenote Kategorie:
Ticket: 723846[33899]
Version: 8.3.2306.23
Datum: 23.06.2023
Anwendung: REB
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2306.23, 33899, 723846

---

## Rosi-Export

Rosi-Export
Paralleles Bearbeiten des Rosi-Exports ist nicht mehr
möglich und die Fehlerprotokoll-Prüfung wird auf die Datenbank-Verbindung
beschränkt.
Releasenote Kategorie:
Ticket: 718777[33940]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33940, 718777

---

## Funktion Verpostung per Outlook entfernt

Funktion Verpostung per Outlook entfernt
Die Funktion "Verpostung per Outlook" stand in der
Rechnungsbearbeitung [REB] zur Verfügung. Diese Funktion wurde abgekündigt und
in diesem Release aus Referenz-ERP entfernt.
Releasenote Kategorie:
Ticket: 724679[33976]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [REB]
Variante: alle
Funktion/Report: Verpostung per Outlook
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33976, 724679

---

## Kirchensteuer

Kirchensteuer
Bei Blättern in den Kirchensteuersätzen wird das Grid
vor dem befüllen mit Daten einmal gelöscht.
Releasenote Kategorie:
Ticket: 725650[34034]
Version: 8.3.2308.4
Datum: 04.08.2023
Anwendung: ZKS
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2308.4, 34034, 725650

---

## Supportersitzung mit Teamviewer

Supportersitzung mit Teamviewer
Der Menüpunkt "Supportersitzung" (Direktsprung [SUSI])
ruft jetzt die Seite von Branchen-ERP (www.Branchen-ERP) auf. Dort kann man dann über den
blauen Button "Fernwartung" den Teamviewer herunterladen.
Releasenote Kategorie:
Ticket: 725958[34098]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34098, 725958

---

## Geschäftsjahr und Schaltjahr

Geschäftsjahr und Schaltjahr
Bei Neuanlage eines Geschäftsjahres mit Verwendung von
"Periodeneinteilung Vorjahr verwenden" werden jetzt Schaltjahre
berücksichtigt.
Releasenote Kategorie:
Ticket: 726032[34127]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: JAHR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34127, 726032

---

## Servicepack 27.005 für Branchen-ERP-Etikettendruck

Servicepack 27.005 für Branchen-ERP-Etikettendruck
Für den Branchen-ERP-Etikettendruck wurde das
Servicepack 27.005 eingespielt, womit Probleme mit dem Druck behoben
wurden.
Releasenote Kategorie:
Ticket: 725355[34132]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: ETIDR - Branchen-ERP-Etikettendruck
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34132, 725355

---

## Crystal Report Druckerauswahl

Crystal Report Druckerauswahl
Bei der Druckerauswahl des Crystal Reports Version 13
werden die Einstellungen des Standard-Windows-Druckers jetzt korrekt
übernommen.
Releasenote Kategorie:
Ticket: 726333[34171]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 34171, 726333

---

## Crystal Report: Datumsfilter

Crystal Report: Datumsfilter
In Crystal-Reports ist es nun wie in
Anwendungsvarianten möglich, Datumsfelder mit dem Schlüsselwort "heute" zu
hinterlegen.
Releasenote Kategorie:
Ticket: 727539[34298]
Version: 8.3.2310.27
Datum: 27.10.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2310.27, 34298, 727539

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.80.232 aktualisiert.
Releasenote Kategorie:
Ticket: 0[34307]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34307, 0

---

## Vorschau und Vorgangsdruck: Linker und oberer Rand

Vorschau und Vorgangsdruck: Linker und oberer Rand
Es gab ein Problem bei der Vorschau und dem
Vorgangsdruck bezüglich der mm-Angaben im Formular zum oberen und linken Rand.
Dies wurde nun behoben.
Releasenote Kategorie:
Ticket: 726910[34410]
Version: 8.3.2312.8
Datum: 08.12.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2312.8, 34410, 726910

---

## Anzeigen von Barvorgängen

Anzeigen von Barvorgängen
Das Anzeigen von Barvorgängen mit [F6] ist jetzt
möglich.
Releasenote Kategorie:
Ticket: 734403[33584]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Rechnungsbearbeitung [REB]
Variante: Standard
Funktion/Report: F6 Ansehen
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 33584, 734403

---

## Vorgangserfassung: Unerwartete Scrollbalken

Vorgangserfassung: Unerwartete Scrollbalken
Unter bestimmten Voraussetzungen wurde in der
Vorgangserfassung die Bildschirmabmessung falsch berechnet, sodass der
Bildschirm mit Scrollbalken versehen wurde. Dies wurde jetzt behoben.
Releasenote Kategorie:
Ticket: 723084[34073]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34073, 723084

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.77.288 aktualisiert.
Releasenote Kategorie:
Ticket: 0[34187]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34187, 0

---

## Auswahlliste 2.0 Spalten fixieren

Auswahlliste 2.0 Spalten fixieren
In der Auswahlliste 2.0 können Spalten mithilfe des
kleinen Pins in der Titelzeile fixiert werden. Diese Einstellung wird jetzt
gespeichert und beim erneuten Aufruf der Variante in der Auswahlliste 2.0 wieder
verwendet.
Releasenote Kategorie:
Ticket: 717376[34197]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34197, 717376

---

## Bereichsauswahl mit Häkchentechnik

Bereichsauswahl mit Häkchentechnik
Die Bereichsauswahl der Auswahllisten und der Crystal
Reporte kann so eingerichtet werden, dass einzelne Zeilen ein und ausgeblendet
werden können. Damit das korrekt funktioniert, muss man die Spalte Variable
füllen und auch im SQL-Text verwenden. Nach dem Ändern der Bereichsauswahl bzw.
nach dem Ändern des SQL-Textes wird geprüft, ob die verwendeten Variablen auch
im SQL-Text vorkommen und es wird ggf. ein Hinweis ausgegeben.
Releasenote Kategorie:
Ticket: 721017[34234]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34234, 721017

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.78.230 aktualisiert.
Releasenote Kategorie:
Ticket: 0[34250]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34250, 0

---

## Belegdatum ändern

Belegdatum ändern
Beim Ändern des Belegdatums wurde automatisch auch das
Lieferdatum auf Vorgangs- und Positionsebene geändert. Nun ist es möglich das
Lieferdatum ebenfalls auf der Maske festzulegen.
Releasenote Kategorie:
Ticket: 727344[34290]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: (Eingangs-)Rechnung bearbeiten
Variante: alle
Funktion/Report: Belegdatum ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34290, 727344

---

## AIS: Dashboards

AIS: Dashboards
Es besteht jetzt die Möglichkeit Dashboards [DASH] auf
AEZADDON-Masken [AIS] einzurichten.
Releasenote Kategorie:
Ticket: 727526[34299]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Informationssystem [AIS]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34299, 727526

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.81.236 aktualisiert.
Releasenote Kategorie:
Ticket: 0[34463]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34463, 0

---

## Excel-Export über AW2.0

Excel-Export über AW2.0
Werden Daten aus der Auswahlliste nach Excel
exportiert (Excel aus Datentabelle), existiert nun die Möglichkeit auszuwählen,
ob alle Daten oder nur die markierten Daten exportiert werden sollen.
Releasenote Kategorie:
Ticket: 0[34445]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Alle
Variante: Alle
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34445, 0

---

## Excel-Import: Excelimport aktualisieren

Excel-Import: Excelimport aktualisieren
Wird in einer unter EXCELI zugeordneten Anwendung die
Funktion "Excelimport aktualisieren" aufgerufen, wird die Variante jetzt direkt
mit den neuen Daten aufgebaut.
Releasenote Kategorie:
Ticket: 728348[34532]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Excel-Import [EXCELI]
Variante: Alle
Funktion/Report: Excelimport aktualisieren
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34532, 728348

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
Die PDF-Erzeugung wurde auf Version Dynaforms
4.0.80.239 aktualisiert.
Releasenote Kategorie:
Ticket: 0[34621]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34621, 0

---

## Elster Version für 2024

Elster Version für 2024
Es wurde die Elster-Version 39.2.4 (gültig für
das Jahr 2024) in Referenz-ERP integriert.
Releasenote Kategorie:
Ticket: 729124[34547]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: UVA, UVZM
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34547, 729124

---

## Excelimport von xls-Dateien

Excelimport von xls-Dateien
Excelimport von .xls-Dateien ausgebaut. Dies war nur
noch in der 32Bit-Version möglich. Beim Excelimport über dbx_import kommt jetzt
ein Fehlerprotokoll-Eintrag mit einem Hinweis, dass stattdessen die Funktion
^excelimport_execute verwendet werden soll.
Releasenote Kategorie:
Ticket: 0[34636]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Excelimport [EXCELI]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34636, 0

---

## Masken mit Ribboncontrol

Masken mit Ribboncontrol
Bei Masken mit dem neuen Menüband kam es vor, dass die
Eingabemarke nicht sofort im ersten Feld stand und man erst mit der Maus in das
Feld klicken musste. Jetzt ist sofort das erste Eingabefeld aktiv.
Releasenote Kategorie:
Ticket: 730276[34675]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34675, 730276

---

## F3-Auswahl 2.0 (Itembox)

F3-Auswahl 2.0 (Itembox)
In der F3-Auswahl 2.0 (Itembox) wird der
Vergleichsoperator der Filterzeile für das Abfragefeld anhand der Zeichen vor
dem Schlüsselwort :ITEMWAHL bestimmt. Dies lässt sich mit Hilfe des
Schlüsselwortes FilterComparision innerhalb der Itembox-Definition
übersteuern.
Releasenote Kategorie:
Ticket: 730794[34741]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34741, 730794

---

## C#-Makro: Fehlerbereinigung

C#-Makro: Fehlerbereinigung
Es wurden Fehler im C#-Makro, Direktsprung [CSM] unter
64bit gefunden. Diese wurden behoben.
Releasenote Kategorie:
Ticket: 731529[34770]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: C#-Makro [CSM]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34770, 731529

---

## Direktsprung [TSE] zu TSE Pflegen eingebaut

Direktsprung [TSE] zu TSE Pflegen eingebaut
Direktsprung [TSE] zu der Auswahlliste "TSE
Pflegen" unter dem Menüpunkt "Barvorgänge" eingebaut. Dokumentation bei
Kassensicherungsverordnung -> Schritt für Schritt Anleitung -> 2.2 und bei
TSE-Auswahlliste entsprechend erweitert.
Releasenote Kategorie:
Ticket: 732642[34949]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: TSE Pflegen [TSE]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34949, 732642

---

## MDE: Nachkommazahlen

MDE: Nachkommazahlen
Numerisches Eingabefeld akzeptiert jetzt auch
Fließkommazahlen. Es wird jeweils das regionsspezifische Trennzeichen betrachtet
- deutsch: Komma, englisch: Punkt.
Releasenote Kategorie:
Ticket: 0[35007]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: MDE Scanner
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 35007, 0

---

## Tron Tracer

Tron Tracer
Es wurde ein neues Tool zum verbesserten
Analysieren der Datenbank-Trace Datei erstellt. Die Anwendung kann über den
Direktsprung [TRON] in Referenz-ERP aufgerufen werden.
Releasenote Kategorie:
Ticket: 0[35067]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Tracefile [TRON]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35067, 0

---

## Dynaforms auf Version 4.0.87.250 aktualisiert

Dynaforms auf Version 4.0.87.250 aktualisiert
Die PDF-Erzeugung wurde auf die Dynaforms-Version
4.0.87.250 aktualisiert.
Releasenote Kategorie:
Ticket: 0[35069]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35069, 0

---

## MDE: Fokus

MDE: Fokus
Der Scanner Webdienst übergibt das Fokuskennzeichen an
die Android Scanner App.
Releasenote Kategorie:
Ticket: 0[35130]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: MDE Scanner
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35130, 0

---

## Warenpositionsmaske Cursor Fokus

Warenpositionsmaske Cursor Fokus
Bei der Korrektur der Warenposition war beim Betreten
der Maske der Fokus auf der Tab-Reiter Auswahl und nicht auf dem ersten
freigeschalteten Feld im Tab-Reiter Allgemein. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 734222[35147]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: -
Variante: -
Funktion/Report: F5
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 35147, 734222

---

## Multiline-Textfelder

Multiline-Textfelder
Die Problematik, dass in Multiline-Feldern unter
bestimmten Voraussetzungen die Eingabe von Zeichen nicht mehr möglich war, wurde
beseitigt.
Releasenote Kategorie:
Ticket: 734265[35166]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35166, 734265

---

## X-Rechnung Zahlungsweg

X-Rechnung Zahlungsweg
Der Zahlungsweg der X-Rechnung wird nun statt im
Profil in der Zahlungsart [FIZAH] festgelegt.
Releasenote Kategorie:
Ticket: 728333[35171]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: Zahlungsarten
Variante: Zahlungsarten erfassen/ändern
Funktion/Report: n/a
Weitere Informationen
Tags:
Releasenote, 9.0.2401.3, 35171, 728333

---

## Crytal Report druck

Crytal Report druck
Die Optionen "Druckknopf archiviert NICHT" und
"Druckknopf verwendet Branchen-ERP-Druck" wurde für die Crystal-Report Version 13 zu der
Option "Druckknopf verwendet Branchen-ERP-Druck und archiviert" zusammengefasst. Ist
dieser Hacken NICHT gesetzt, wird beim Druck die Mechanik von Crystal verwendet
und es ist dann möglich nur ausgewählte Bereiche zu drucken, jedoch wird der
Report nicht archiviert. Die Optionbox-Funktion Drucken F4 verwendet immer den
Branchen-ERP-Druck und archiviert ggf. den Report.
Releasenote Kategorie:
Ticket: 733093[35191]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35191, 733093

---

## Vorgangsauswahllisten haben "Neu drucken und neu versenden" und "Beleg erneut versenden" erhalten

Vorgangsauswahllisten haben "Neu drucken und neu versenden" und "Beleg
erneut versenden" erhalten
Die Vorgangsauswahllisten [AGB], [ELB], [GUB] und
[REB] haben die Funktionen "Neu drucken und neu versenden" und "Beleg erneut
versenden" unter dem Menüpunkt Merkmale erhalten.
Releasenote Kategorie:
Ticket: 734596[35207]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: AGB, ELB, GUB, REB
Variante: -
Funktion/Report: Neu drucken und neu versenden, Beleg
erneut versenden
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35207, 734596

---

## Bankleitzahlen aktualisieren

Bankleitzahlen aktualisieren
Für die Funktion Banken aktualisieren stehen die Daten
der Deutschen Bundesbank gültig vom 03.06.2024 bis 08.09.2024 zur
Verfügung.
Releasenote Kategorie:
Ticket: 733825[35218]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: BNK
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 35218, 733825

---

## aktuallisierung der SEPA Version

aktuallisierung der SEPA Version
Die SEPA-Versionen 3.7 (gültig ab 17.März 2024) und
3.8 (gültig ab 17. November 2024) wurden in Referenz-ERP Implementiert.
Releasenote Kategorie:
Ticket: 732383[35219]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Zahlungsverkehr
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35219, 732383

---

## Betragsfelder vergrößert

Betragsfelder vergrößert
In der Warenabstimmung nach Perioden [WABST] wurden
die Anzeigefelder für Beträge vergrößert
Releasenote Kategorie:
Ticket: 732033[35379]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Warenabstimmung nach Perioden
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 35379, 732033

---

## Crystal Report Version 13 - Performance

Crystal Report Version 13 - Performance
Die Performance beim Bereitstellen der Daten im Viewer
von Crystal Report wurde verbessert. Außerdem werden, wenn man den Export aus
dem Viewer heraus aufruft, die Daten nicht mehr erneut gelesen, was auch zu
einer weiteren Verbesserung der Performance führt.
Releasenote Kategorie:
Ticket: 736622[35470]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 35470, 736622

---

## Hilfelink gefixt

Hilfelink gefixt
Ein kaputter Link in der Hilfe zu Verbotslisten wurde
ersetzt.
Releasenote Kategorie:
Ticket: 736584[35497]
Version: 9.0.2501.5
Datum:
Anwendung: verbotslisten
Variante: n/a
Funktion/Report: Hilfe
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35497, 736584

---

## Itembox 2.0 Spalten verschieben

Itembox 2.0 Spalten verschieben
In der F3-Auswahl (Itembox 2.0) wurden die
verschobenen Spalten nach erneutem Aufruf nicht wieder korrekt dargestellt,
sondern immer in der Standardreihenfolge. Dieses Problem wurde behoben.
Releasenote Kategorie:
Ticket: 737812[35620]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35620, 737812

---

## Fehlende Unterscheidung zwischen Markt- und Tresen- Kasse bei Zahlungsabbruch hinzugefügt

Fehlende Unterscheidung zwischen Markt- und Tresen- Kasse bei
Zahlungsabbruch hinzugefügt
Fehlende Unterscheidung zwischen Markt- und Tresen-
Kasse bei Zahlungsabbruch hinzugefügt, welcher zu fälschlicher Löschung des
Datensatzes in der ACashBelg Tabelle geführt hat.
Releasenote Kategorie:
Ticket: 738111[35653]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: [BVVE]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 35653, 738111

---

## Fehler bei Neuanlage eines Mengenzeitraums

Fehler bei Neuanlage eines Mengenzeitraums
Bei der Erfassung eines neuen Mengenzeitraums konnte
es, bei Eingabe einer Menge oder Summe von mindestens 1.000 oder mehr, zu einem
Fehler bei der internen Verarbeitung des Tausender-Trennzeichens kommen. In
diesem Fall wurde der Punkt als das englische Dezimaltrennzeichen interpretiert,
wodurch die Summe um den Faktor 1000 zu niedrig in der Datenbank abgespeichert
wurde. Der Fehler wurde nun behoben.
Releasenote Kategorie:
Ticket: 737982[35655]
Version: 9.0.2402.3
Datum: 08.11.2024
Anwendung: Kontrakte [KTR]
Variante: Kontrakte
Funktion/Report: Mengenzeiträume
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.3, 35655, 737982

---

## Patch einspielen von SQL-Dateien

Patch einspielen von SQL-Dateien
Der Libraryviewer (Direktsprung [PATCH]) kann
SQL-Texte entpacken und in das laufende Referenz-ERP einspielen. Leider ist bei einer
Umstellung des Temp-Verzeichnisses von Referenz-ERP das Ausgabeverzeichnis des
Libraryviewers nicht angepasst worden, so dass das Einspielen nicht erfolgte.
Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 0[35763]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: [PATCH]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35763, 0

---

## Privater Crystal Report Daten anzeigen

Privater Crystal Report Daten anzeigen
Wurde im privaten Crystal Report die Vorschau mit
Daten gespeichert, dann hat dieser sich immer auf die gespeicherten Daten
bezogen und nicht die tatsächlich eingegrenzten Daten berücksichtigt. Dieser
Fehler wurde jetzt behoben.
Releasenote Kategorie:
Ticket: 739632[35815]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: CRW
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35815, 739632

---

## Elster 41.2.4 für 2025

Elster 41.2.4 für 2025
Es wurde die Elster-Version 41.2.4 (gültig für
das Jahr 2025) in Referenz-ERP integriert. Diese enthält folgende Änderungen:
USTVA:Kennziffer 70: Wechsel von der Kleinunternehmer-Regelung (§ 19 UStG)
zur Regelbesteuerung. Diese wird vor Aufruf des Übertragungsprogramms abgefragt.
Die Wirtschaftsidentifikationsnummer des Systemkunden aus dem Mandantenstamm
wird, soweit sie angegeben wurde, mit übertragen.  ZMDO:Die Straße des
Ansprechpartners ZMDO ist jetzt eine Pflichtangabe.
Releasenote Kategorie:
Ticket: 739914[35828]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: UVA,ZMDO
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 35828, 739914

---

## CS-Makro Funktion CompileAll

CS-Makro Funktion CompileAll
In der CS-Makro Anwendung [CSM] wurde in der Funktion
"CompileAll" ein Fehler gefunden, der die korrekte Ausführung dieser Funktion
verhinderte. Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 739946[35831]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: CS-Markro [CSM]
Variante: --
Funktion/Report: CompileAll
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35831, 739946

---

## Datenbank-Backup: AMIC_EVT_Backup_ARCHIV

Datenbank-Backup: AMIC_EVT_Backup_ARCHIV
AMIC_EVT_Backup_ARCHIV: Die Prozedure erkennt nun,
wenn es sich um ein Replikationssystem handelt, und führt dann weder TRUNCATE
noch RENAME mit dem LOG aus.
Releasenote Kategorie:
Ticket: 738252[35868]
Version: 9.0.2501.5
Datum:
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35868, 738252

---

## Auswahlliste 2.0 JPP-Zugriff

Auswahlliste 2.0 JPP-Zugriff
Die JPP-Methode Clickzeile aus CHelper wird jetzt auch
von der Auswahlliste 2.0 unterstützt
Releasenote Kategorie:
Ticket: 740529[35948]
Version: 9.0.2501.5
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35948, 740529

---

## Branchen-ERP Etikettendruck export Archivkennzeichen

Branchen-ERP Etikettendruck export Archivkennzeichen
Beim Export von Branchen-ERP-Etikettendruck Reporten
wurde das Archivierungskennzeichen grundsätzlich nicht mit exportiert. Jetzt
wird bei privat erstellten Reporten das Kennzeichen mit übertragen.
Releasenote Kategorie:
Ticket: 740495[35965]
Version: 9.0.2501.5
Datum:
Anwendung: ETIDR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35965, 740495

---

## Geschäftsjahr Prüfung Enddatum

Geschäftsjahr Prüfung Enddatum
Das Geschäftsjahr besitzt ein Anfangsdatum und ein
Enddatum. Es wird jetzt geprüft, ob das Enddatum größer ist als das
Anfangsdatum
Releasenote Kategorie:
Ticket: 740628[35966]
Version: 9.0.2501.5
Datum:
Anwendung: JAHR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35966, 740628

---

## Von Branchen-ERP reservierte Anwendungsformatbereiche weggeschützt

Von Branchen-ERP reservierte Anwendungsformatbereiche weggeschützt
Es war möglich in Anwendungsformaten unter [FORMA]
Variante Anwendungsformate, von uns reservierte Anwendungsformate zu nutzen.Dies
wurde behoben.
Releasenote Kategorie:
Ticket: 741244[36001]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Formatliste [FORMA]
Variante: Anwendungsformate
Funktion/Report: F5, F8
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36001, 741244

---

## Fälligkeitsdatum des Rechnungsbetrages in XRE

Fälligkeitsdatum des Rechnungsbetrages in XRE
Das Fälligkeitsdatum des Rechnungsbetrages wird nun
korrekt aus dem Vorgang (V_DatumValuta) belegt.
Releasenote Kategorie:
Ticket: 742113[36084]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: [XRE]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36084, 742113

---

## PDF: Merge von Pdf-Dateien

PDF: Merge von Pdf-Dateien
Es wurde das Problem behoben das beim Merge von
PDF-Dateien im Archiv leere Seiten generiert wurden.
Releasenote Kategorie:
Ticket: 740832[36109]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: -
Variante: -
Funktion/Report: JPP JFA_PdfMerge
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 36109, 740832

---

## Reklamation

Reklamation
Im Modul Reklamation [REKLAM] können Maßnahmen mit
mehrzeilige Eingabefelder enthalten sein. Hier wurde bisher nur die erste Zeile
abgespeichert. Dieses Verhalten wurde korrigiert.
Releasenote Kategorie:
Ticket: 742228[36156]
Version: 9.0.2501.5
Datum:
Anwendung: Reklamation
Variante: Maßnahmen
Funktion/Report: [REKLAM]
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36156, 742228

---

## Gefahrgut: UN-Nummer

Gefahrgut: UN-Nummer
Das Feld UN-Nummer ist nun frei pflegbar ohne einen
Eintrag in der Itembox auswählen zu müssen.
Releasenote Kategorie:
Ticket: 742117[36158]
Version: 9.0.2501.5
Datum:
Anwendung: Gefahrgut
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36158, 742117

---

## Windows-Druck: Archivierung A4-Format bei physikalischen Druckern

Windows-Druck: Archivierung A4-Format bei physikalischen Druckern
Bei Windows-Drucker die auf A4 drucken wird nun das
Archiv ebenfalls mit entsprechendem Rand versehen. Das Verhalten ist nicht
schalterbar.In zukünftigen Versionen werden umfangreiche Hilfen zur Verfügung
stehen, um Informationen zu den Druckereigenschaften im Umfeld Windows
Drucker-Treiber und System und Referenz-ERP zu erhalten.Schon jetzt sei nochmal
explizit darauf hingewiesen, das im Formularstamm unter "Windows
Druckeinstellungen" mit der Schalterstellung "Anzeige Druckbereich" auf "Ja"
effektive Druckbereiche durch ein Raster visualisiert werden. D.h. wenn
Druckinhalte "außerhalb" des Rasters liegen, können sie physikalisch nicht
dargestellt werden. In einem solchen Fall muss entweder das Formular angepasst
werden oder mit der Einstellung "Druck-Größe" experimentiert werden.
Releasenote Kategorie:
Ticket: 741641[36217]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere I
[...]


---

## Eingabe Multilinefelder über AIS

Eingabe Multilinefelder über AIS
Die Eingabe bei Multiline-Textfeldern, die über AIS
angelegt wurden, wurde überarbeitet. Damit ist die Problematik, dass man
eigenständig Zeilen einfügen musste behoben.
Releasenote Kategorie:
Ticket: 740200[36168]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 36168, 740200

---

## Archiv-Vorschau bei Variantenwechsel

Archiv-Vorschau bei Variantenwechsel
Nach dem Wechsel innerhalb einer Anwendung von einer
Variante mit Archiv-Vorschau zu einer Variante die keine Archiv-Vorschau hat
bleibt die Archiv-Vorschau nicht länger sichtbar.
Releasenote Kategorie:
Ticket: 740504[36274]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36274, 740504

---

## Abkündigung: Infocenter

Abkündigung: Infocenter
Die Möglichkeiten des Archivs und des Dashboards
machen eine weitere notwendige Software-Pflege des "Info-Center" im Haupt-Menü
obsolet. Dieser Programmteil wurde entfernt.
Releasenote Kategorie:
Ticket: 0[36368]
Version: 9.0.2501.5
Datum:
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36368, 0

---

## Vorgangsunterklassen Bezeichnung in Fremdsprache

Vorgangsunterklassen Bezeichnung in Fremdsprache
Für die Vorgangsunterklassen lassen sich die
Bezeichnungen jetzt auch in einer Fremdsprache Pflegen. Dazu muss man F3 auf dem
Bezeichnungsfeld drücken.
Releasenote Kategorie:
Ticket: 0[36487]
Version: 9.0.2501.5
Datum:
Anwendung: VUK
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36487, 0

---

## Aktualisierung Dokument-Engine

Aktualisierung Dokument-Engine
Im Rahmen der Pflege- und Wartung wurde die
Dokument-Engine auf den Stand 4.0.102.290 aktualisiert.
Releasenote Kategorie:
Ticket: 0[36702]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36702, 0

---

## Pascal-Makro-Funktionen JVarsGet und JVarsGet, Längenbeschränkung aufgehoben

Pascal-Makro-Funktionen JVarsGet und JVarsGet, Längenbeschränkung
aufgehoben
Bei den Pascal-Makro-Funktionen JVarsGet und JVarsSet
gab es eine Beschränkung auf maximal 255 Zeichen beim Austausch mit den System
Referenz-ERP-JVars. Diese Beschränkung ist aufgehoben.
Releasenote Kategorie:
Ticket: 745906[36915]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: -
Variante: -
Funktion/Report: Makro-Programme
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36915, 745906

---

## Belegfluss gelöschte Formulararchiveinträge wiederherstellen

Belegfluss gelöschte Formulararchiveinträge wiederherstellen
In der Anwendung Belegfluss [BF] werden gelöschte
Archiveinträge in der Auswahlliste mit roter ID dargestellt. Die Inhalte lassen
sich dann nur anzeigen, aber nicht bearbeiten. Mit der neuen Funktion "Löschen
rückgängig" können diese Einträge wiederhergestellt werden.
Releasenote Kategorie:
Ticket: 746665[36959]
Version: 9.0.2501.5
Datum:
Anwendung: Belegfluss [BF]
Variante: Meine Postfächer
Funktion/Report: Löschen rückgängig
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36959, 746665

---

## HTML-Dateien im Belegfluss im Browser anzeigen

HTML-Dateien im Belegfluss im Browser anzeigen
Wenn in der Anwendung Belegfluss der
Formulararchiveintrag eine HTML-Datei ist, öffnet sich nun der unter Windows
eingestellte Standardbrowser.
Releasenote Kategorie:
Ticket: 746694[36957]
Version: 9.0.2501.5
Datum:
Anwendung: [BF]
Variante: Meine Postfächer
Funktion/Report: Archiv Belegfluss
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36957, 746694

---

## Belegfluss: Daten aktualisieren als neue Refresh-Funktion über eine Prozedur

Belegfluss: Daten aktualisieren als neue Refresh-Funktion über eine
Prozedur
In der Anwendung "Archiv Belegfluss" [BF]  in der
Variante "Meine Postfächer" auf der Maske "Belegfluss" gibt es eine neue
Funktion mit dem Namen "Daten aktualisieren".Diese Funktion hat man nur zur
Verfügung, wenn man in der Variante "Postfacheinrichtung" auf der Maske
"Postfach-Einrichtung" eine Refreshprozedur angibt.Man kann die von Branchen-ERP
ausgelieferte Refreshprozedur, wie üblich auf der Maske, mit eigener Logik
ausstatten.
Releasenote Kategorie:
Ticket: 746984[37061]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Meine Postfächer, Postfach-Einrichtung
Funktion/Report: Daten aktualisieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37061, 746984

---

## Auswahlliste 2.0, Abbruch des Ladevorgangs

Auswahlliste 2.0, Abbruch des Ladevorgangs
Wenn man beim Laden der Daten zu früh Enter drückte
(Abbruch des Ladevorgangs), dann reagierte die Auswahlliste nicht mehr. Dieses
Problem wurde beseitigt.
Releasenote Kategorie:
Ticket: 744494[37151]
Version: 9.0.2501.6
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.6, 37151, 744494

---

## Feldreihenfolge Vermehrungsvertrag

Feldreihenfolge Vermehrungsvertrag
Die Maskensteuerung im Vermehrungsvertrag wurde
aktualisiert. Dabei wurde die ursprünglich im Standard ausgelieferte
Tabulator-Reihenfolge zurückgesetzt. Zusätzlich wurden die Felder Öko, OECD,
Private Feldbesichtigung und NoB innerhalb der Maske verschoben, um eine
vereinfachte und effizientere Dateneingabe zu ermöglichen. Die Lagerzuordnung
des Vermehrungsvertrags wird jetzt besser dargestellt.
Releasenote Kategorie:
Ticket: 747001[37316]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Vermehrungsvertrag
Variante: Vermehrungsvertrag
Funktion/Report: Neu
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37316, 747001

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.102.295- aktualisiert.
Releasenote Kategorie:
Ticket: 0[37343]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37343, 0

---

## SEPA Version 3.9

SEPA Version 3.9
Sepa-Version 3.9, die ab dem 05.10.2025 verwendet
werden kann, wurde in Referenz-ERP integriert.
Releasenote Kategorie:
Ticket: 747669[37421]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37421, 747669

---

## Itembox 2.0: Verhalten bei Verwendung ITEM1 und ITEM2

Itembox 2.0: Verhalten bei Verwendung ITEM1 und ITEM2
Wurde in der F3-Auswahl mit ITEM1 und ITEM2 gearbeitet
und ITEM2 blieb leer, dann wurde ITEM2 mit ITEM1 vorbelegt. Da dieses Verhalten
dazu führte, dass ungewollt Daten nicht gefunden wurden, bleibt ITEM2 in diesem
Fall jetzt leer.
Releasenote Kategorie:
Ticket: 748145[37460]
Version: 9.0.2501.8
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.8, 37460, 748145

---

## Report RLF

Report RLF
Der RLF-Report wurde wieder aktiviert.
Releasenote Kategorie:
Ticket: 748159[37462]
Version: 9.0.2501.8
Datum:
Anwendung: [RLF]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.8, 37462, 748159

---

## Feld Kassensitzungsnummer von wieder verfügbar

Feld Kassensitzungsnummer von wieder verfügbar
Aufgrund eines Fehlers war das Feld
Kassensitzungsnummer von auf der DSFinV-K Export-Maske nicht bearbeitbar.Deshalb
wurde immer 1 bis Bis-Wert exportiert. Dies wurde behoben und man kann jetzt
andere und kleinere Zeiträume exportieren.
Releasenote Kategorie:
Ticket: 748216[37497]
Version: 9.0.2501.8
Datum:
Anwendung: -
Variante: -
Funktion/Report: Export erzeugen
Weitere Informationen
Tags:
Releasenote, 9.0.2501.8, 37497, 748216

---

## Report Verteilkostenträgerauswertung

Report Verteilkostenträgerauswertung
Die Verteilkostenträgerauswertung zeigte auch in der
Spalte für die kumulativen Werte die Periodenwerte an.
Releasenote Kategorie:
Ticket: 748317[37599]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37599, 748317

---

## Aktuelle Warenbestände nicht aufrufbar aus der Warenpositionsmaske in einem Beleg

Aktuelle Warenbestände nicht aufrufbar aus der Warenpositionsmaske in einem
Beleg
Die Maske, die Bestände und Mengen aus der
Warenpositonsmaske anzeigt, konnte nicht korrekt geöffnet werden.Dies wurde
korrigiert.
Releasenote Kategorie:
Ticket: 748438[37605]
Version: 9.0.2501.8
Datum:
Anwendung: Alle Belegerfassungsanwendung
Variante: Alle Belegerfassungsvarianten
Funktion/Report: aktuelle Warenbestände
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.8, 37605, 748438

---

## EC-Karten-Ansteuerung

EC-Karten-Ansteuerung
Durch eine inzwischen veraltete Initialisierung der
EC-Karten-Ansteuerung kam es in der Version 9.0.2501.x zu Abbrüchen der
EC-Zahlung mit Timeout.  Dies wurde behoben.
Releasenote Kategorie:
Ticket: 748390[37818]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: EC-Cash
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37818, 748390

---

## Sepa erweiterter Zeichensatz mit Umlauten

Sepa erweiterter Zeichensatz mit Umlauten
In den Hausbanken kann man jetzt pro Hausbank
festlegen, ob der einfache oder der erweiterte Zeichensatz (mit Umlauten und den
Sonderzeichen &$%*) verwendet werden soll. Vorbelegung ist der erweiterte
Zeichensatz.
Releasenote Kategorie:
Ticket: 749003[37862]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Hausbankenstamm [BNKH]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37862, 749003

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.91.299 aktualisiert.Das Update ist von Hersteller als notwendig eingestuft
(mehrere kritische Sachen werden damit behoben)
Releasenote Kategorie:
Ticket: 0[37879]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37879, 0

---

## KOKORE-Druck - fälliger Saldo nach Datenlöschung

KOKORE-Druck - fälliger Saldo nach Datenlöschung
Der fällige Saldo auf dem Kokore wurde nach Verwendung
des Moduls Datenlöschung falsch ausgewiesen. Das Problem wurde beseitigt,
Releasenote Kategorie:
Ticket: 748651[38055]
Version: 9.0.2502.7
Datum:
Anwendung: KOKORE bearbeiten [KOK]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38055, 748651

---

## Outlook Drag and Drop

Outlook Drag and Drop
Beim Hinzufügen von E-Mail-Anhängen aus Outlook zum
Archiv per Drag and Drop wurden bei mehreren geöffneten Outlook Fenstern die
falschen Dateien importiert. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 0[38119]
Version: 9.0.2502.6
Datum:
Anwendung: Formulararchiv
Variante: -
Funktion/Report: Drag and Drop
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.6, 38119, 0

---

## Archiv-Vorschau "großer" Pdf-Inhalte

Archiv-Vorschau "großer" Pdf-Inhalte
Die Anzeige großer Pdf-Dateien aus dem Archiv heraus
ist ermöglicht worden. Das Phänomen das "Nichts" angezeigt wird soll nicht mehr
auftreten. Es lässt sich auch kein konkreter Wert angeben, ab dem die
beteiligten Systeme der Meinung sind so zu reagieren. Im Internet lassen sich
Größenordnungen zwischen 1 und 2 MB recherchieren, die Werte sind Browser- und
Versionsabhängig.Betroffen waren Kunden die "große" Pdf-Inhalte per
Import-Verfahren integriert haben. Beispiele wären Drag&Drop von
Pdf-Dateien, oder auch Scanner-Importe mit Grafiken in hoher Auflösung.
Releasenote Kategorie:
Ticket: 750526[38257]
Version: 9.0.2502.6
Datum:
Anwendung: alle Archivanwendungen
Variante: alle Archivvarianten
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.6, 38257, 750526

---

## Dokumentenverwaltung: Vorschau von Excel-Dateien

Dokumentenverwaltung: Vorschau von Excel-Dateien
Im Archiv werden Excel-Dokumente in HTML-Dateien
konvertiert und dann zur Ansicht gebracht. Da der Vorgang bei großen *.xslx -
Dateien sehr lange dauert, wird die Aufbereitung auf 30 Zeilen und 20 Spalten
beschränkt. Das wird in der Vorschau visuell mitgeteilt. Werden Informationen
über eine solche "Preview" hinaus benötigt, ist die Ansicht über die Funktion
"Dokument anzeigen (CF12)" zu verwenden.
Releasenote Kategorie:
Ticket: 0[38284]
Version: 9.0.2502.7
Datum:
Anwendung: Formulararchiv / Archiv
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38284, 0

---

## Dokumentenverwaltung: Vorschau von Word-Dokumenten

Dokumentenverwaltung: Vorschau von Word-Dokumenten
Im Archiv werden Word-Dokumente im "*.docx"-Format in
HTML-Dateien konvertiert und dann zur Ansicht gebracht. Da die Aufbereitung von
enthaltenen Bildern in diesen Dokumenten extrem lange dauert, wird die Vorschau
generell ohne enthaltene Bilder dargestellt. Dieses Vorgehen ist performant. Es
wird ein genereller Hinweis am Anfang der Vorschau gegeben. Da schon die
Ermittlung der Anzahl der möglichen Bilder sehr lange dauert wird der Hinweis
grundsätzlich angezeigt.Wird das Dokument  ganzheitlich benötigt, gibt es
den Weg über "Dokument anzeigen (CF12)".
Releasenote Kategorie:
Ticket: 0[38282]
Version: 9.0.2502.7
Datum:
Anwendung: Formulararchiv / Archiv
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38282, 0

---

## Kassensturz-Beleg

Kassensturz-Beleg
Beim Druck des Belegs für den Kassensturz wurde bei
„Zählung“ bisher immer der Text „Pari“ ausgegeben, auch wenn ein Manko
vorlag.Dieses Verhalten wurde korrigiert, sodass nun korrekt "Manko" ausgegeben
wird, wenn ein Fehlbetrag aufgrund der Zählung zu Stande kommt.
Releasenote Kategorie:
Ticket: 750717[38345]
Version: 9.0.2502.7
Datum:
Anwendung: Kassenabschluss
Variante: Kasseneröffnung
Funktion/Report: Abschluss
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38345, 750717

---

## Elster Version 43.2.6

Elster Version 43.2.6
Es wurde die Elster-Version 43.2.6 - gültig für das
Jahr 2026 - in Referenz-ERP integriert.
Releasenote Kategorie:
Ticket: 750043[38331]
Version: 9.0.2502.7
Datum:
Anwendung: UVA, UVZM
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38331, 750043

---

## PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.

PDF-Engine (PDF-Erzeugung-Bibliotheken) erneuert.
PDF-Erzeugung wurde auf Version Dynaforms
4.0.102.302 aktualisiert.
Releasenote Kategorie:
Ticket: 0[38709]
Version: 9.0.2502.9
Datum:
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38709, 0

---

## Menülogobereich (EPA A1NETMENU)

Menülogobereich (EPA A1NETMENU)
Bezeichnung
Standardwert
Erklärung
ArchivAnzeige
Ja
Wird
      hier Nein eingeben wird die Uhr dargestellt
ArchivAnzeigeFunktion
AMIC_MENU_ARCHIVANZEIGE
Diese Datenbank-Procedure gibt die
      fa_id, fa_mndnr zurück, dessen Bild-Dokument im Menülogobereich
      dargestellt werden soll.
Signatur ist
CREATE
      PROCEDURE AMIC_MENU_ARCHIVANZEIGE( IN in_bedienerklasse integer
      )
RESULT
(
fa_id    integer,
fa_mndnr integer
)

---

## AIS

AIS

---

## Abkündigung

Abkündigung

---

## Abkündigung

Abkündigung

---

## Abkündigung

Abkündigung

---

## Abkündigung

Abkündigung

---

## Abkündigung

Abkündigung

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Dokumentenverwaltung

Dokumentenverwaltung

---

## Referenz-ERP Patch Manager (EPA AEINSENTWUPDATE)

Referenz-ERP Patch Manager (EPA
AEINSENTWUPDATE)
Bezeichnung
Standardwert
Erklärung
Testlauf
Nein

---

## Aktionärsverwaltung - Aktientransaktionen (EPA AKTIENTRANSAKTION)

Aktionärsverwaltung - Aktientransaktionen
(EPA AKTIENTRANSAKTION)
Bezeichnung
Standardwert
Erklärung
Verhalten bei Überschreitung der
      ausgegebenen Aktienanzahl
Fehler
asdadasd

---

## Import Anlagenbuchhaltung (EPA ANKAIMPORT)

Import Anlagenbuchhaltung (EPA
ANKAIMPORT)
Bezeichnung
Standardwert
Erklärung
Importprozedur ist
      änderbar?
Nein
Im
      Normalfall ist die Prozedur zum Einspielen der Anlagedaten völlig
      ausreichend und muss nicht geändert werden. Wenn jedoch von fachkundiger
      Seite eine eigene Prozedur erstellt wurde, so kann man mit diesem Schalter
      es ermöglichen, die Datenbankprozedur änderbar zu machen.

---

## Auswahlliste (EPA AW_MASK)

Auswahlliste (EPA AW_MASK)
Bezeichnung
Standardwert
Erklärung
Infofenster kann aktiviert
      werden
Nicht aktivierbar

---

## MaskenTitel (EPA BTMBOX)

MaskenTitel (EPA BTMBOX)
Bezeichnung
Standardwert
Erklärung
Anzuzeigende Webseite (auch Datei
      mit file:) möglich

---

## MaskenTitel (EPA CEMAIN)

MaskenTitel (EPA CEMAIN)
Bezeichnung
Standardwert
Erklärung
Abfrage Sofortdruck
Ja
Vorbelegung
      Sofortdruckabfrage
Nein
Abfrage 'Angaben
      korrekt?'
Ja
Vorbelegung
      Korrektabfrage
Ja
Mehrbelegverarbeitung
Nein
Prozedurname für die freie
      Anzeige
Optional: Name einer privaten
      Datenbankfunktion zur Informationsanzeige im Maskenkopf des
      Rohwarebearbeitungsmoduls.
Siehe
      Beschreibung
Rohwarebelege
      ansehen
Kostensätze positiv
      eingeben/darstellen
Nein
Ist
      die Einstellung
Ja
, so werden Kostensätze ohne negatives Vorzeichen
      dargestellt und manuelle Kostensätze ohne negatives Vorzeichen
      eingegeben.

---

## Daten exportieren (EPA DATEVEXP)

Daten exportieren (EPA DATEVEXP)
Siehe Beschreibung
Datev-Export

---

## Aktionärsverwaltung - Dividende (EPA DIVIDENDE)

Aktionärsverwaltung - Dividende (EPA
DIVIDENDE)
Bezeichnung
Standardwert
Erklärung
Verhalten bei fehlender Verbindung
      zum Wirtschaftsjahr
Fehler
Hinweis bei Überschreitung des
      Zahltags
Nein

---

## Kontonummer nachtragen (EPA DTAKUAEN)

Kontonummer nachtragen (EPA DTAKUAEN)
Bezeichnung
Standardwert
Erklärung
Auf
      doppelte Konten bei Kontoaufteilung hinweisen
Ja
Bei
      der Kontenaufteilung wird normalerweise geprüft, ob das Konto bereits
      eingegeben wurde. Wenn man den Schalter auf
Nein
setzt, so entfällt
      diese Prüfung und man ein und dasselbe Konto mehrmals angeben.

---

## Signieren (EPA FA_SIGNIEREN)

Signieren (EPA FA_SIGNIEREN)
Bezeichnung
Standardwert
Erklärung
Sofort durchstarten ohne
      Dialog
Nein

---

## Kontoauszug / Saldenbestätigung (EPA FIAUSZUG)

Kontoauszug / Saldenbestätigung (EPA
FIAUSZUG)
Bezeichnung
Standardwert
Erklärung
Auch
      ungebuchte Belege drucken?
Nein
Im
      Standardfall müssen die Auszüge erst gebucht sein. Will man jedoch auch
      ungebuchte Belege drucken, so trägt man hier
Ja
ein
Darstellung des
      Sollhabenkennzeichens
MINUSPLUS
Im
      Normalfall wird an Stelle von S oder H hier für den Kunden + oder -
      ausgegeben. Möchte man jedoch lieber das Sollhabenkennzeichen auf dem
      Kontoauszug sehen, so trägt man hier SH ein. Auswahl mit
F3
ist möglich
Standarddruckformular für
      Kontoauszug
2200
Dieses Formular wird für den Druck
      vorgeschlagen.

---

## DATEV-Export erstellen (EPA FIDATEV)

DATEV-Export erstellen (EPA FIDATEV)
Bezeichnung
Standardwert
Erklärung
Bei
      Personenkonten Test auf 5 Stellen
Ja
Im
      Ausgabeformat OBE dürften Personenkonten nur fünfstellig sein. Die
      Abschaltung dieses Tests kann nur mit Rücksprache mit dem Steuerberater
      erfolgen. Siehe auch Dokumentation
Datev-Export

---

## Erstellen eines DTA-Datenträgers (EPA FIDTANEU)

Erstellen eines DTA-Datenträgers (EPA
FIDTANEU)
Siehe Dokumentation
Datenträgeraustausch
.

---

## Einzelbeleganzeige (EPA FIKINFOE)

Einzelbelega
nzeige (EPA FIKINFOE)
Bezeichnung
Standardwert
Erklärung
Darf
      ein Stornobeleg geändert werden?
Änderbar
Bei
      der Übergabe in die Primanota können die Belege mit einer
      Bearbeitungssperre versehen werden. Mögliche Werte sind:
•
Änderbar
•
Eingeschränkt
      änderbar
•
Nicht
      änderbar
•
Nicht
      änder-/löschbar
Textersetzung des Stornobelegs. Leer
      = Originaltext
Im
      Standardfall wird der Beleg 1 zu 1 kopiert und nur das Vorzeichen des
      Betrags wird umgedreht. Wenn man hier etwas eingibt, werden zusätzlich
      salle Textzeilen durch diese Zeichenfolge ersetzt.

---

## Kontoblattdruck (EPA FIKOBLDR)

Kontoblattdruck (EPA FIKOBLDR)
Bezeichnung
Standardwert
Erklärung
Druck nur zulassen, wenn nicht
      Gesamtauswahl
Nein
Um
      zu verhindern, dass durch versehentliches starten des Druck alle
      Kontoblätter gedruckt werden, kann man hier einstellen, dass die
      Druckfunktion nur startet, wenn die Kontoblättert individuell ausgewählt
      sind.
KoKoRe-Kennzeichen(Kundenstamm)
      Ignorieren?
Ja
Im
      Kundenstamm existiert ein Kennzeichen, das besagt, ob das Kokore für
      diesen Kunden gedruckt werden soll. Wenn dieses Kennzeichen nicht korrekt
      gepflegt wurde, kann man hier die Prüfung abschalten. Es werden dann immer
      alle Kunden zugelassen.

---

## Direct Database Access (EPA FIND_KEY)

Direct Database Access (EPA FIND_KEY)
Bezeichnung
Standardwert
Erklärung
(Deaktiviert, siehe Optionen) Max.
      Spalten (bis 200). Empfohlen 49.
49
Hier
      kann man einstellen, wie viele Spalten dargestellt werden. Eine
      Eingrenzung ist deswegen Sinnvoll, da die Performance deutlich nachlässt,
      je mehr Spalten angezeigt werden.
(Deaktiviert, siehe Optionen) Max.
      Zeilen (0=Bildschirm füllen, -1=alleslesen)
0
Unter OSQL ist es möglich alle Daten
      einlesen zu lassen. Dazu muss man hier -1 eintragen. Gibt man eine
      positive Zahl an, werden maximal so viele Zeilen eingelesen.

---

## Steuerinformation (EPA FISTEUA)

Steuerinformation (EPA FISTEUA)
Bezeichnung
Standardwert
Erklärung
Report für Auswertung nach
      Einzelkonten
fiustva
Es
      kann ein eigener privater Report hinterlegt werden. Den Namen gibt man
      dann hier an.
Report für Auswertung nach
      Klasse/Gruppe/Schlüssel
fiustva2
S.o.
Report für Ausw. nach
      Kl/Gruppe/Schl/Dat
fiustva1
S.o.
Report für Auswertung nach
      Klasse/Schlüssel
fiustva4
S.o.
Report für Auswertung nach
      Klasse/Schlüssel/Datum
fiustva3
S.o.
Report für
      Steuerverprobung
fiustva8
S.o.
Report für Auswertung nach
      Steuerkonten
fiustva7
S.o.
Report für
      Umsatzsteuerverprobung
fiustva9
S.o.
Umsatzsteuerformular anhand des
      Jahres festlegen
Ja
Das
      Umsatzsteuerformular ändert sich gewöhnlich Jahr für Jahr. Die verwendeten
      Reporte haben im Namen das Jahr stehen. Daran kann das System jeweils den
      aktuellen Report erkennen. Steht hier ein
Nein
, so wird immer der
      Report USTVA.rpt verwendet.

---

## Steuersätze pflegen(EPA NUMSTEU)

Steuersätze pflegen(EPA NUMSTEU)
Bezeichnung
Standardwert
Erklärung
Bei
      „Speichern unter“ alle Schlüsselfelder freigeben.
Nein
Nein:
Die Funktion
Speichern unter
Shift+F9
speichert den
      Steuersatz mit einem neu eingegebenen Steuerabdatum ab. Es ist nicht
      möglich die Steuerklasse, Steuergruppe und den Steuerschlüssel zu
      ändern.
Ja:
Es werden auch die Felder
      Steuerklasse, Steuergruppe und den Steuerschlüssel freigegeben, so dass
      man die Einrichtung für eine neue Kombination der Schlüsselfelder
      übernehmen kann.

---

## Zahlungen (EPA FIZAHLD)

Zahlungen (EPA FIZAHLD)
Bezeichnung
Standardwert
Erklärung
Bei
      Scheckdruck Banksammelliste drucken?
Nein
Wird
      hier ein
Ja
eingetragen, so wird nach dem Scheckdruck eine
      Banksammelliste gedruckt.
Vorbelegung des Belegdatums mit dem
      Tagesdatum?
Nein
Standardmäßig wird bei der Übernahme
      in die Primanota das Belegdatum mit dem Belegdatum des ersten markierten
      Datensatzes vorbelegt. Stellt man hier
Ja
ein, so wird das
      Tagesdatum als Vorbelegung verwendet.
Beleg darf nicht geändert
      werden?
Änderbar
Bei
      der Übergabe in die Primanota können die Belege mit einer
      Bearbeitungssperre versehen werden. Mögliche Werte sind:
•
Änderbar
•
Eingeschränkt
      änderbar
•
Nicht
      änderbar
•
Nicht
      änder-/löschbar
Datenbankfunktion zur Bestimmung des
      Belegtextes
Der
      Text, der bei der
Übernahme in die Primanota
gebildet wird, kann individuell
      durch eine Datenbankfunktion angepasst werden.

---

## Zahlvorschläge erstellen (EPA FIZAHLV)

Zahlvorschläge erstellen (EPA FIZAHLV)
Bezeichnung
Standardwert
Erklärung
Bei
      Zahlungsausgang Fehlerhinweis bei fehlender Bankverbindung
Ja
Für
      den DTA ist eine gültige Bankverbindung notwendig. Daher wird die
      Bankverbindung getestet und am Ende ein entsprechender Fehlerhinweis
      gebracht. Diesen Test kann man hier ausschalten.
Bei
      Zahlungseingang Fehlerhinweis bei fehlender Bankverbindung
Ja
Für
      den DTA ist eine gültige Bankverbindung notwendig. Daher wird die
      Bankverbindung getestet und am Ende ein entsprechender Fehlerhinweis
      gebracht. Diesen Test kann man hier ausschalten.
Bei
      Fremdwährung auf nicht verrechnete OP´S testen
Nein
Werden Zahlungsvorschläge für eine
      Fremdwährung erstellt, so werden nur die Belege in dieser Währung
      verrechnet. Existieren z.B. Belege in Buchwährung, so werden diese nicht
      mit verrechnet. Stellt man diesen EPA auf JA, so erscheint in diesem Fall
      am Ende ein Hinweise
Ma
[...]


---

## Individuelle Zinsgutschrift (EPA FIZIGUTSCHRIFT)

Individuelle Zinsgutschrift (EPA
FIZIGUTSCHRIFT)
Bezeichnung
Standardwert
Erklärung
Belege nach Erstellung sofort
      drucken
Nein
Man
      kann auf der Maske bei „Belege nach Erstellung sofort drucken“ einen Haken
      setzten, um nach der Erstellung sofort einen Beleg zu drucken. Setzt man
      diesen Einrichterparameter auf
Ja
, so ist der Haken automatisch
      gesetzt und kann nicht geändert werden.

---

## Zinsen Übernahme in die Primanota (EPA FIZINSD)

Zinsen Übernahme in die Primanota (EPA FIZINSD)
Bezeichnung
Standardwert
Erklärung
Beleg darf nicht geändert
      werden?
Änderbar
Bei
      der Übergabe in die Primanota können die Belege mit einer
      Bearbeitungssperre versehen werden. Mögliche Werte sind:
•
Änderbar
•
Eingeschränkt
      änderbar
•
Nicht
      änderbar
•
Nicht
      änder-/löschbar

---

## Hedge-Datei-Import (EPA HEDGE_IMPORT)

Hedge-Datei-Import (EPA HEDGE_IMPORT)
Bezeichnung
Standardwert
Erklärung
Hedge-Import-Pfad
c::\\
reg.
      Ausdruck für Importsuche
_([0-9]+)_
Hedge-Import-Skript
c::\\development\\aeins\\bin\\amic_hedge_import.vbs

---

## Kontoblätter (EPA KOBLCREATE)

Kontoblätter (EPA KOBLCREATE)
Bezeichnung
Standardwert
Erklärung
Belegdatum abfragen
Nein

---

## Mobile Datenerfassung (EPA KUI)

Mobile Datenerfassung (EPA KUI)
Bezeichnung
Standardwert
Erklärung
KUI
      Seitennummer

---

## MaskenTitel (EPA KUPWARE1)

MaskenTitel (EPA KUPWARE1)
Bezeichnung
Standardwert
Erklärung
Zusatztext 1
Nein

---

## MaskenTitel (EPA KUPWARE3)

MaskenTitel (EPA KUPWARE3)
Bezeichnung
Standardwert
Erklärung
Zusatztext 1
Nein

---

## MaskenTitel (EPA KUPWARE2)

MaskenTitel (EPA KUPWARE2)
Bezeichnung
Standardwert
Erklärung
Zusatztext 1
Nein

---

## Lokalitäten (EPA LVS_LOKALITAETEN)

Lokalitäten (EPA LVS_LOKALITAETEN)
Bezeichnung
Standardwert
Erklärung
Vorbelegung Dimension 1
--
Vorbelegung Dimension 2
--
Vorbelegung Dimension 3
--
Vorbelegung Dimension 4
--
Vorbelegung Dimension 5
--

---

## Proxy Server Bearbeiten (EPA MMS_SERVEREINSTELLUNGEN)

Proxy Server Bearbeiten (EPA
MMS_SERVEREINSTELLUNGEN)
Bezeichnung
Standardwert
Erklärung
Direktes speichern Ja
      Nein
Nein

---

## Mitgliedsnummer (EPA Mitgliedsnummern)

Mitgliedsnummer (EPA Mitgliedsnummern)
Bezeichnung
Standardwert
Erklärung
Sollen nur die Mitgliedsnummer
      geändert werden?
Ja
Hiermit kann Eingestellt werden ob
      nur die Mitgliedsnummer geändert werden.

---

## Ändern (EPA NUMAEND)

Ändern (EPA NUMAEND)
Bezeichnung
Standardwert
Erklärung
Belegdatum mit Periode
      prüfen?
kein
      Test
Folgende
      Einstellmöglichkeiten existieren:
•
Kein Test
•
Test und Warnung
•
Test und Fehler
•
Teste Jahr mit Warnung
•
Teste Jahr und Fehler
Beim Test Jahr muss das
      Belegdatum nur im aktuellen Jahr liegen. Bei Warnung wird nur ein Hinweis
      auf das inkorrekte Datum gegeben und man kann weiter
    erfassen.

---

## Belege erfassen (EPA NUMBE_01)

Belege erfassen (EPA NUMBE_01)
Bezeichnung
Standardwert
Erklärung
Belegkreise im Menü
      anzeigen
Ja
Man
      kann die Belegerfassung entweder über
Neu
F8
starten oder über die im Menü
      angezeigten Belegkreise. Wenn die Funktion
Neu
F8
ausreicht, kann man der
      Übersichtlichkeit die Belegkreise aus dem Menü entfernen, indem man hier
Nein
einträgt.
Ändern und Löschen über Itembox
      auswählen
Ja
Wenn
      man einen
Beleg ändern
F5
oder
löschen
F7
möchte, dann öffnet sich immer
      zuerst eine Itembox, in der man den Beleg auswählen kann. Möchte man dies
      nicht, so kann man dieses Verhalten abschalten. Es wird dann immer der
      gerade in der Auswahl ausgewählte Beleg verwendet.

---

## Belege verrechnen (EPA NUMOP_02)

Belege verrechnen (EPA NUMOP_02)
Bezeichnung
Standardwert
Erklärung
Belegdatum und Periode
      prüfen
Warnung
•
Ignorieren
. Es findet kein Test
      statt.
•
Fehler
. Man kann nur weiterarbeiten, wenn
      Datum und Periode übereinstimmen.
•
Warnung
. Datum und Periode werden
      gegeneinander geprüft und es wird eine Warnung ausgegeben. Es kann
      trotzdem weitergearbeitet werden.
Bei
      Ausbuchung Steuerschüssel aus Sachkontenstamm vorbelegen?
Nein
Steht hier ein „Ja“, so wird der
      Steuerschlüssel vorbelegt.
Vorbelegung Bankkonto
0
Bei
      Zahlung Bank wird dieses Konto vorbelegt.
Vorbelegung Kassenkonto
0
Bei
      Zahlung Kasse wird dieses Konto vorbelegt.

---

## Ändern (EPA NUMOP_03)

Ändern (EPA NUMOP_03)
Bezeichnung
Standardwert
Erklärung
Referenznummer bei allen Belegarten
      änderbar?
Nein
Hier kann eingestellt
      werden, dass die Referenznummer änderbar ist. Bei nein wird sie nur
      angezeigt.
Bei
      Änderung des Valutadatums die Mahnliste prüfen.
Warnung
•
Ignorieren
. Es findet kein Test statt.
•
Fehler
. Befindet sich der Beleg in einer
      Mahnvorschlagsliste, darf das Valutadatum nicht geändert werden
•
Warnung
. Es wird geprüft, ob der Beleg in einer
      Mahnvorschlagsliste existiert und ggf. die Meldung „
Dieser OP befindet
      sich zurzeit in einer Mahnvorschlagsliste. Das geänderte Valutadatum wird
      nicht berücksichtigt.
“ ausgegeben.
•
Zurücksetzen
. Man hat die Möglichkeit, diesen Beleg aus der
      Mahnvorschlagsliste zu löschen. Beantwortet man diese Frage mit nein, so
      wird wie bei
Warnung
verfahren.

---

## Steueränderung (EPA NUMSTEU)

Steueränderung (EPA NUMSTEU)
Bezeichnung
Standardwert
Erklärung
Erlaubte Abweichung in % ( 0 kein
      Test, kleiner 0 Warnung)
0.1000
Sollte der Steuerbetrag der Rechnung
      von dem errechneten Betrag abweichen, so kann man den Steuerbetrag manuell
      ändern. Trägt man hier einen Wert ungleich Null ein, so wird bei einer
      Abweichung um mehr als diesen Betrag eine Meldung ausgegeben.

---

## Option Box (EPA OPTBOX2)

Option Box (EPA OPTBOX2)
Bezeichnung
Standardwert
Erklärung
Bei
      Hilfezuordnung ohne Abfrage speichern
Nein

---

## Mobile Datenerfassung (EPA PDA_DISPONIEREN)

Mobile Datenerfassung (EPA
PDA_DISPONIEREN)
Bezeichnung
Standardwert
Erklärung
Überprüfung des
      Vorganges
600
Item
      Box der anzuzeigenden Vorgänge
IB_PDA_VORGAENGE
Name
      der Etikettenprozedur LILA

---

## Druckerstatus (EPA PRINTERVIEW)

Druckerstatus (EPA PRINTERVIEW)
Bezeichnung
Standardwert
Erklärung
Name
      der privaten Prozedur
Aufruf der zu startenden private
      Prozedur

---

## MaskenTitel (EPA PRODULP)

MaskenTitel (EPA PRODULP)
Bezeichnung
Standardwert
Erklärung
Mengenkontrolle
      an/abschaltbar
Nein

---

## Datenübernahme (EPA SCANNER_UEBERNAHME)

Datenübernahme (EPA
SCANNER_UEBERNAHME)
Bezeichnung
Standardwert
Erklärung
Vorbelegungen sperren
Nein

---

## MaskenTitel (EPA SD_MAIN2)

MaskenTitel (EPA SD_MAIN2)
Bezeichnung
Standardwert
Erklärung
Auswahl: 0
      =Multiselect,1=singleselect
0

---

## Stapelverarbeitung (EPA STAPELVERARBEITUNG)

Stapelverarbeitung (EPA
STAPELVERARBEITUNG)
Bezeichnung
Standardwert
Erklärung
Tage, nach denen der Stapel gelöscht
      wird
-1

---

## SEPA-Mandatsverwaltung (EPA SEPAMANDAT)

SEPA-Mandatsverwaltung (EPA SEPAMANDAT)
Bezeichnung
Standardwert
Erklärung
Vorbelegung
      Lastschriftverfahren
Verkürzte Vorlauffrist
Hier
      kann man einstellen, wie das Feld für Lastschriftverfahren im Neu-Fall
      vorbelegt wird:
•
Basislastschrift
•
Verkürzte
      Vorlauffrist
•
Firmenlastschrift

---

## Saatenunion Datenübernahme (EPA SU_ORACLERUN)

Saatenunion Datenübernahme (EPA
SU_ORACLERUN)
Bezeichnung
Standardwert
Erklärung
Oracle Transfertabelle
Oracletransfertabelle
Makro zur
      Datenverarbeitung
su-oracle

---

## Datenübergabe (EPA SU_ORACLE_UEBERGABE)

Datenübergabe (EPA
SU_ORACLE_UEBERGABE)
Bezeichnung
Standardwert
Erklärung
Oracle Tabelle
OracleTransfertabelle
Übergabemakro
su-oracle-in

---

## Ausprägung / Seriennummern (EPA SVAUSPR)

Ausprägung / Seriennummern (EPA SVAUSPR)
Bezeichnung
Standardwert
Erklärung
Prüfung des Ausgangs gegen
      Eingang
Nein
Wenn
      dieser EPA auf Ja gestellt wird. Können nur Ausprägungen ausgewählt werden
      die schon mit einem Eingangsbeleg erfasst worden sind. Steht der EPA auf
      Nein können Ausprägungen ohne Prüfung hinzugefügt werden.
Itembox für Vorgangsklasse
      100
Itembox für Vorgangsklasse
      200
Itembox für Vorgangsklasse
      300
Itembox für Vorgangsklasse
      400
Itembox für Vorgangsklasse
      500
Itembox für Vorgangsklasse
      600
Itembox für Vorgangsklasse
      700
Itembox für Vorgangsklasse
      800
Ohrmarken verarbeiten
Nein
Obsolet
Warnung wenn erfasste Anzahl größer
      Menge
Standard (bei jeder
      Einzeleingabe)

---

## MaskenTitel (EPA SVGEB1)

MaskenTitel (EPA SVGEB1)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Ja

---

## MaskenTitel (EPA SVGEB1A)

MaskenTitel (EPA SVGEB1A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Ja

---

## MaskenTitel (EPA SVGEB2A)

MaskenTitel (EPA SVGEB2A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB2)

MaskenTitel (EPA SVGEB2)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB3A)

MaskenTitel (EPA SVGEB3A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB3)

MaskenTitel (EPA SVGEB3)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB4)

MaskenTitel (EPA SVGEB4)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB4A)

MaskenTitel (EPA SVGEB4A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB5)

MaskenTitel (EPA SVGEB5)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB5A)

MaskenTitel (EPA SVGEB5A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB6)

MaskenTitel (EPA SVGEB6)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB6A)

MaskenTitel (EPA SVGEB6A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB7)

MaskenTitel (EPA SVGEB7)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVGEB8A)

MaskenTitel (EPA SVGEB8A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Ja

---

## MaskenTitel (EPA SVGEB8)

MaskenTitel (EPA SVGEB8)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Ja

---

## MaskenTitel (EPA SVGEB7A)

MaskenTitel (EPA SVGEB7A)
Bezeichnung
Standardwert
Erklärung
Gebinde ohne
      Folgeabfragen
Nein

---

## MaskenTitel (EPA SVHSTL)

MaskenTitel (EPA SVHSTL)
Bezeichnung
Standardwert
Erklärung
Einzug bei Gruppen
Ja
horiz. Rollbalken
Nein

---

## MaskenTitel (EPA SVPOSI)

MaskenTitel (EPA SVPOSI)
Bezeichnung
Standardwert
Erklärung
Automatische Sortierung beim
      Verlassen
Nein
Zeilenanzahl der Positionsanzeige
      (12..25)
12
Löschabfrage Vorbelegung
Nein
Ordersatzauswahl auch bei 1
      Ordersatz
Nein
Sortierreihenfolge beim
      Sortieren
Keine Sortierung
Zwischensumme ohne
      Abfrage
Nein

---

## Text erfassen (EPA SVTEXT)

Text erfassen (EPA SVTEXT)
Bezeichnung
Standardwert
Erklärung
Eingabebreite
80

---

## MaskenTitel (EPA SVUMWARE)

MaskenTitel (EPA SVUMWARE)
Bezeichnung
Standardwert
Erklärung
Bildschirm für Addon
      aufbauen
Nein
Zusatztext 1 abfragen
Nein
Zusatztext 2 abfragen
Nein

---

## MaskenTitel (EPA SVUMMAIN)

MaskenTitel (EPA SVUMMAIN)
Bezeichnung
Standardwert
Erklärung
Druck-Abfrage
Ja
Druck-Korrekt-Abfrage
Ja
Druck-Vorbelegung
Nein
Korrekt-Abfrage
Ja
Korrekt-Vorbelegung
Ja
Mehrbelegerfassung
Nein
Leerbelege in Datenbank
      speichern?
Ja

---

## MaskenTitel (EPA SVWALP)

MaskenTitel (EPA SVWALP)
Siehe
EPA SVWARE

---

## MaskenTitel (EPA SVWKTRNEU)

MaskenTitel (EPA SVWKTRNEU)
Bezeichnung
Standardwert
Erklärung
Maskenbreite
80
Maskenhöhe
20
Zeige Zusatzinformationen sofort
      an
Nein

---

## TCP/IP Scanner (EPA TCPIP_SCANNER)

TCP/IP Scanner (EPA TCPIP_SCANNER)
Bezeichnung
Standardwert
Erklärung
Löschung von Nullmengen in
      Folgeaufträgen
Nein

---

## MaskenTitel (EPA UEBERSETZUNGSABGLEICH)

MaskenTitel (EPA
UEBERSETZUNGSABGLEICH)
Bezeichnung
Standardwert
Erklärung
Name
      der Originaldatei, die zum Übersetzer ging
SpracheDE.txt
Name
      der übersetzten Datei
Sprachexx.txt

---

## Manuelle Kostenstellenverteilung (EPA VERTKOST)

Manuelle Kostenstellenverteilung (EPA
VERTKOST)
Bezeichnung
Standardwert
Erklärung
Kostenstelleneindeutigkeit
      prüfen?
Fehler
Hier
      kann festgelegt werden, wie reagiert werden soll, wenn in der Verteilung
      eine Kostenstelle mehrmals vorkommt:
•
Ignorieren:
Es erfolgt kein Test, ob die
      Kostenstelle bereits erfasst wurde.
•
Warnung:
Es erscheint lediglich ein Hinweis,
      dass die Kostenstelle bereits verwendet wurde.
•
Fehler:
Man kann eine Kostenstelle nicht
      doppelt erfassen.

---

## Manuelle Kostenträgerverteilung (EPA VERTKSTR)

Manuelle Kostenträgerverteilung (EPA
VERTKSTR)
Bezeichnung
Standardwert
Erklärung
Kostenträgergleichheit
      prüfen?
Fehler
Hier
      kann festgelegt werden, wie reagiert werden soll, wenn in der Verteilung
      ein Kostenträger mehrmals vorkommt:
•
Ignorieren:
Es erfolgt kein Test, ob der
      Kostenträger bereits erfasst wurde.
•
Warnung:
Es erscheint lediglich ein Hinweis,
      dass der Kostenträger bereits verwendet wurde.
•
Fehler:
Man kann einen Kostenträger nicht
      doppelt erfassen.

---

## Mengenkorrektur in Vorgängen (EPA VOKORR)

Mengenkorrektur in Vorgängen (EPA VOKORR)
Bezeichnung
Standardwert
Erklärung
Druckabfrage stellen
Ja
Vorbelegung Druckabfrage
Ja
Vorbelegung Abfrage
      Freigabevermerk
Ja
Abfrage Freigabevermerk
      stellen
Ja
Vorbelegung nicht geänderte
      Belege
Nein
Abfrage nicht geänderte Belege
      stellen
Nein
Einstieg mit Ergebnismenge bei
      Gebinden
Nein
Info1-Feld der Warenposition
      abfragen
Nein
Preise behandeln
Nein
Preiseinheit Feldstatus
passiv
Preismengeneinheit
      Feldstatus
passiv
Maximal proz. Abweichung der
      Sollmenge
5.00
Rabatte behandeln
Nein
Rabatttext Feldstatus
aktiv
Rabbattyp FeldStatus
aktiv
Vorbelegung mit einem Rabatttyp
      (0=nein)
0

---

## Mengen / Partieaufteilung (EPA VOKORRPV)

Mengen / Partieaufteilung (EPA VOKORRPV)
Bezeichnung
Standardwert
Erklärung
Partieverteilung immer
      Speichern
Nein

---

## Positionen Vorgang (EPA VORGANGPOSITIONEN)

Positionen Vorgang (EPA
VORGANGPOSITIONEN)
Bezeichnung
Standardwert
Erklärung
Behandlung des statistischen
      Wertes
Vorbelegen mit Warenwert

---

## MaskenTitel (EPA VORGANG_COPY)

MaskenTitel (EPA VORGANG_COPY)
Bezeichnung
Standardwert
Erklärung
Nachlaufprozedur, welche nach
      erfolgreicher Änderung ausgeführt wird

---

## MaskenTitel (EPA VorlagenAuswahl)

MaskenTitel (EPA VorlagenAuswahl)
Bezeichnung
Standardwert
Erklärung
Vorgabe Auswahl Anw/Var
Ja
Vorgabe Auswahl "Nur
      eigene"
Nein
Auswahl anderer Anw/Var
      freischalten
Nein
Auswahl "Nur eigene"
      freischalten
Nein
Borgabewert "Nur neuesten
      Eintrag"
Ja

---

## Warenflusskontrolle (EPA WAFLTEST)

Warenflusskontrolle (EPA WAFLTEST)
Bezeichnung
Standardwert
Erklärung
Protokolldatei vor jedem Test
      löschen?
Nein

---

## Verarbeitung von Finanz- und Kassenbelegen (EPA ZAHLSTO)

Verarbeitung von Finanz- und Kassenbelegen (EPA
ZAHLSTO)
Bezeichnung
Standardwert
Erklärung
Sollen Formulare auf Schacht
      gedruckt werden?
Nein

---

## MaskenTitel (EPA ZAMISTO)

MaskenTitel (EPA ZAMISTO)
Bezeichnung
Standardwert
Erklärung
Soll
      auf den Schacht gedruckt werden?
Nein

---

## Private Variante

Private
Variante
Herkunft und Aufbau dieser Variante basieren auf
Excel-Import
. Hat noch
keine Aktualisierung der Variante stattgefunden, verfügt die Variante über
folgende Funktionalitäten:
Felder
Information
„Excelimport starten mit F10
      …“
Funktionen
Variante aktualisieren
      [
F10
]
Führt den Excel-Import, der dieser
      Variante zugrunde liegt durch und aktualisiert diese Variante.

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Externe Anbindungen

Externe Anbindungen

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Feldtyp im SQL-Text

Feldtyp im SQL-Text
Die Auswahlliste stellt Felder je nach Feldtyp dar.
Dabei kann sich der Feldtyp in der Datenbank vom angezeigten Feldtypen
unterscheiden. Ein Typische Beispiel dafür wären die FS-Formate, die einen
„smallint“ oder „integer“ von der Datenbank erwarten und als anzeige erscheint
der zugehörige Text. Bei der Angabe des Feldtypen wird nicht zwschen Groß- und
Kleinschreibung unterschieden.
Feldtyp
Datenbanktyp
Gütigkeitsbereich
Beschreibung
CHAR
CHAR
VARCHAR
LONG
      VARCHAR
Alle
      möglichen Character-Typen, die in der alten AW mit bis zu 255 Zeichen
      Dargestellt werden. In der neuen AW 2.0 könnten die Texte komplett
      dargestellt werden. Es ist jedoch anzuraten, die Texte schon im
      SQL-Statement auf eine vernünftige Länge zu casten, da ansonsten unnötig
      Ressourcen verbraucht werden.
I2
I4
SMALLINT
INTEGER
Zahl
      ohne Nachkommastellen
N0
      bis N6
NUMERIC
Eine
      Numerische Zahl. Die Zahl hinter dem N bestimmt die Anzahl d
[...]


---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## Finanzbuchhaltung

Finanzbuchhaltung

---

## GeoDaten

GeoDaten
Wer zu seinen Anschriften GeoDaten ermitteln möchte,
kann dies mit Hilfe Google tun:
•
GoogleMaps
Der Datengigant hat vor
einiger Zeit ein Modell eingeführt, bei dem man einen Datenzugang registrieren
muss, auf dem man ein Freiguthaben erhält, das durch verschiedene Dienste
abgeschmolzen wird. Danach werden diese Dienste kostenpflichtig und führen zu
einer Bebuchung der hinterlegten Kreditkarte
•
Letztlich ist auch die manuelle Pflege der geografischen Daten möglich.
Dies kann u.U. aufwendig sein, ist aber in den meisten Fällen kostenfrei.
Die geografischen Daten werden im Anschriftstamm auf
der Registerkarte „Zusätze“ gepflegt.
Die Zugangsdaten zu den Webdiensten werden im
Mandantenstamm
eingepflegt

---

## Individuelle Textersetzung von Anwendungstexten

Individuelle Textersetzung
von Anwendungstexten
Hauptmenü
Systempflege
Individuelle Textersetzung
Direktsprung
[TEXTM]
Mit dieser Anwendung lassen sich Texte in Anwendungen
individuell durch alternative Texte ersetzen. Dies hat den Vorteil, dass
Anwendungstexte speziell an den Sprachgebrauch des Kunden angepasst werden
können.
Die Anwendung selbst besteht aus 2 Teilen. In dem
Ersten, werden die Module zur Textersetzung erstellt und eingerichtet. Im
zweiten Teil werden die Texte zu der Anwendung bearbeitet.
Die Pflege der individuellen Texte erfolgt über
Entwicklung / Support der Firma Branchen-ERP.

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Kassensystem

Kassensystem

---

## Makroanschluss in der Marktkasse

Makroanschluss in der Marktkasse
Neben den Info-Feldern in der Marktkasse können
weitere Felder in AIS eingerichtet werden, die Daten anzeigen sollen. Um diese
zu füllen können Makros verwendet werden. Diese werden analog zu
AIS im Vorgang
angesprochen
und stellen ähnliche Daten zur Verfügung.

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Nachhaltigkeit

Nachhaltigkeit

---

## Objektverwaltung

Objektverwaltung

---

## Pascal-Makro

Pascal-Makro

---

## Technisches zu Replikation mit und in Referenz-ERP

Technisches zu Replikation mit und in Referenz-ERP

---

## Verzeichnisstruktur des Filialsystems

Verzeichnisstruktur des Filialsystems
Aufbau der im Filialsystem verwendeten
Verzeichnisstruktur:
..\Aeins
|
|___ \dbrexp
|
|___ \Log
|            |
|            |___
\alte_DBRLogs
|

 |
|___ \BST1
|
|___ \BST2
So sieht die Verzeichnisstruktur in einem laufenden
Replikations-/Filialsystem aus. Die Ordner „
Log
“,
„
alte_DBRLogs
“ und die Ordner der Betriebsstätten (hier
„
BST1
“  und „
BST2
“), werden von der Prozedur
„
AMIC_remote_schedule()
“ auf ihre Existenz hin überprüft und ggf.
angelegt.
Der Ordner
„dbrexp“
muss als vorbereitender
Schritt manuell im Aeins-Verzeichnis wie o.a. angelegt werden.

---

## LVS Allokationsstrategie (SPA 1038)

LVS Allokationsstrategie (SPA 1038)
Allokationen werden nach einer vorgegebenen Strategie
erfolgen.
Es gibt drei Varianten der Kommissionierung als
globale Einstellung:
1.
Variante Kommissionierung zuerst
Hier
werden zunächst die abzupackenden Mengen kommissioniert und die Mischpalette
zurück ins Lager gestellt. Zu einem späteren Zeitpunkt werden dann Fahraufträge
zum Ziel festgelegt.
2.
Volle Ladeträger zuerst
Hier
werden zunächst die Vollpaletten ausgelagert und dann die Teilmengen auf
Mischpaletten zusammengestellt. Die Waren erhalten sofort einen Fahrauftrag in
den Warenausgang
3.
Alles zeitgleich
Ist im
Grund eine Variation von Variante 2 nur dass hier parallel zu der Abarbeitung
der Fahraufträge für die Vollpaletten die Kommissionierung von Teilmengen
stattfindet. Fahraufträge in die Kommi-Zone werden vorrangig abgearbeitet.

---

## Bezeichnung der SQL-Funktion oder -Prozedur für die Replikationsüberwachung(SPA 1044)

Bezeichnung der SQL-Funktion oder -Prozedur für die
Replikationsüberwachung(SPA 1044)
Bezeichnung der SQL-Funktion oder -Prozedur für die
Replikationsüberwachung. Schlüssel wir über Itembox gesetzt und entspricht den
eingerichteten Remoteusern. Damit können für die einzelnen Remoteuser
unterschiedliche Funktionen gespeichert werden.

---

## FutterApp-Optionen (SPA 1047)

FutterApp-Optionen (SPA 1047)
Legt Optionen zur Privatisierung fest.

---

## Signierung eines Beleges (SPA 1048)

Signierung eines Beleges (SPA 1048)
Bevor ein Beleg zum Sofortdruck aufgerufen wird, kann
diesem eine Unterschrift per Signotec (elektronische Unterschrift) zugeordnet
werden. Das Signotecc System wird im Program Files Ordner installiert, hier gibt
es dann eine SignoIManager 2.exe Datei, deren Pfad userspezifisch zugeordnet
werden muss.  Es ist jeweils der Merkmalstyp und das Bedienerkürzel
anzugeben, getrennt durch einen Schrägstrich (/).
Als zweites muss noch angegeben werden, in welches
Pfad (incl. Dateiname) die Unterschrift gespeichert werden soll. Es sind hier
NUR BMP Dateien zugelassen, siehe dazu auch die Signotec Einrichtung.
Zusätzlich muss dann im Formular der Bereich 22
(Bitmap) eingebaut werden, im Textschlüssel ist dann SignoBedid, 3566
einzutragen,
Es wird dann während der Laufzeit die an diesem
Arbeitsplatz gefundene (und als BMP gespeicherte) Unterschrift dem Formular
zugeordnet, und wenn gewünscht auch sofort archiviert.

---

## DATEV Festschreibungskennzeichen übertragen(SPA 1061)

DATEV Festschreibungskennzeichen übertragen(SPA 1061)
Das Festschreibungskennzeichen wird standardmäßig
gesetzt. Dies bewirkt, dass der Empfänger diese Daten nicht ändern kann. Es kann
jedoch wünschenswert und notwendig sein, dass die übertragenen Belege vom
Empfänger bearbeitet werden müssen.
0: ohne Festschreibungskennzeichen
1: mit Festschreibungskennzeichen
Achtung:
Beim DATEV-Übertrag werden nur
gebuchte Belege exportiert und diese sind bekanntlich in Referenz-ERP nicht änderbar.
Dieses Verhalten wird durch diesen SPA
nicht
beeinflusst.

---

## Bankleitzahl und Kontonummer anzeigen (SPA 1121)

Bankleitzahl und Kontonummer anzeigen (SPA
1121)
Bankleitzahl und Kontonummer wurden im Zuge der
Globalisierung von BIC und IBAN abgelöst. Daher wurde sowohl die Erfassung als
auch die Listen und Anwendungen auf diese Nummern umgestellt. Bankleitzahl und
Bankkontonummer werden nicht mehr angezeigt. Die Bankleitzahl lässt sich im
Bankenstamm und die Bankkontonummer im Hausbankenstamm nach wie vor erfassen.
Nur in den Kundenbanken ist eine Erfassung der Bankkontonummer nicht mehr
möglich, wenn dieser Steuerparameter auf
Nein
steht.
Sollte man die
Bankkontonummer außerhalb des Standards verwendet haben, so kann man mit diesem
SPA diese beiden Felder wieder aktivieren.

---

## Globale Prozedur fürs Maschinentagebuch (SPA 1129)

Globale
Prozedur fürs Maschinentagebuch (SPA 1129)
Hier kann eingestellt werden, ob das Maschinentagebuch
für alle Vorgangsklassen und Unterklassen aktiviert werden soll. Steht der
Schalter auf „Nein“ wird die Einstellung aus [FRZ] gezogen.
Zusätzlich hinterlegt man hier die private Prozedur
für das Maschinentagebuch. Diese wird nach der eigentlichen Abwicklung mit den
gleichen Parametern wie die Prozedur „MaschinenTagebuchVersorgung“
aufgerufen.
Die globale Prozedur wird auch aufgerufen, wenn der
Schalter aktiv auf „Nein“ steht und das Maschinentagebuch aufgrund der
[FRZ]-Einstellung aktiv ist.

---

## Bezahlterminal mit eigenem Drucker (SPA 1156)

Bezahlterminal mit eigenem Drucker (SPA 1156)
Standard ist Ja
Wird dieser SPA auf „Nein“ gestellt, so wird dem
Bezahlterminal der Drucker abgeschaltet. Dazu muss jedoch im Kassenbon-Formular
im Fuß letzte Seite die Position 8273 – EC-Karten-Beleg Text mit mind 30 Zeilen
eingerichtet werden.

---

## V_Referenz bei Stornobeibehalten (SPA 1166)

V_Referenz bei Stornobeibehalten (SPA 1166)
Wird ein Beleg storniert (mit Stornobeleg), so wird in
die Referenznummer des Belegs mit der Belegnummer des Ursprungsbelegs
beschrieben. Soll der ursprüngliche (evtl. manuell eingetragene Wert) erhalten
bleiben, so muss der SPA auf 1 gestellt werden.

---

## DATEV Sonderzeichen aus Belegnummer herausfiltern(SPA 1165)

DATEV Sonderzeichen aus Belegnummer herausfiltern(SPA 1165)
Die DATEV erlaubt nur die Sonderzeichen $ % & * +
- und /. Wenn Anstelle der Belegnummer die Referenznummer übertragen wird und
diese eines dieser Zeichen enthält, so wird die Referenznummer nur bis zum
ersten nicht erlaubten Zeichen übertragen (von letzten Zeichen aus). Dies
entspricht der standard SPA-Einstellung
Nein.
Ändert man die Einstellung
auf
Ja
, dann wird die Nummer komplett übertragen, jedoch ohne
Sonderzeichen.
Belegnummer „2025.10.05_D_1234“
Bei Einstellung
Nein
: „1234“
Bei Einstellung
Ja
: „20251005D1234“

---

## Außendienst Zentrale(SPA 138)

Außendienst Zentrale(SPA 138)

---

## Rechnung / Gutschrift nach Druck stornierbar(SPA 152)

Rechnung / Gutschrift nach Druck stornierbar(SPA
152)
Darf nach dem Druck die Funktion Stornieren noch
ausgeführt werden?

---

## Windows Druckersteuerung benutzen(SPA 145)

Windows Druckersteuerung benutzen(SPA 145)
Soll die Druckersteuerung von Windows benutzt
werden?

---

## Aut. Umbruch Textzeilen beim Drucken(SPA 155)

Aut. Umbruch Textzeilen beim Drucken(SPA 155)
Beim Ausdruck von Textzeilen, aber auch
Textbausteinen, etc. werden die Textzeilen automatisch umgebrochen, wenn das
Ausgabefeld im Vorgang eine geringere Länge in der Zeile aufweist als der
erfasste Text.
Bei „Nein“ wird der Text abgeschnitten.
Bei „Ja, wie Erfassung“ werden in der Erfassung
gesetzte Zeilenumbrüche im Formulardruck übernommen.

---

## Abweichender Zahlungspflichtiger aktiv(SPA 166)

Abweichender Zahlungspflichtiger aktiv(SPA 166)
Bei „Ja“ kann eine automatische Unterscheidung von
Rechnungsempfänger und Zahlungs- pflichtigen erfolgen.

---

## Rechnungsausgangsbuch aktiv(SPA 174)

Rechnungsausgangsbuch aktiv(SPA 174)

---

## Warenbewegungen im Kontenblatt-Druck(SPA 173)

Warenbewegungen im Kontenblatt-Druck(SPA 173)

---

## Vorzeichen in Kontenblatt-Warenposition(SPA 177)

Vorzeichen in Kontenblatt-Warenposition(SPA 177)

---

## Skontierung von Zu-/Abschlägen(SPA 186)

Skontierung von Zu-/Abschlägen(SPA 186)
Bei Zu-/Abschlägen gibt es Skonti wie folgt:
wie Ware: gemäß Warenposition
nie: es gibt keine Skonti bei Zu-/Abschlägen
immer: es werden immer Skonti auf Zu-/Abschläge
gewährt

---

## Ordersatz-Suche beim Rechnungsempfänger(SPA 191)

Ordersatz-Suche beim Rechnungsempfänger(SPA 191)
Ja: der Ordersatz wird beim Rechnungsempfänger
gesucht.
Nein: der Ordersatz wird beim Lieferempfänger
gesucht.

---

## Warenbewegung vor sonstigen im Kontenblatt(SPA 192)

Warenbewegung vor sonstigen im Kontenblatt(SPA 192)

---

## Kopieren von Klasse zu Klasse möglich (SPA 203)

Kopieren von Klasse zu Klasse möglich (SPA 203)

---

## Bei EK-Rg aut. nach Positionen in Steuer(SPA 206)

Bei EK-Rg aut. nach Positionen in Steuer(SPA 206)

---

## Maximale Steuerkorrektur (Cent)(SPA 209)

Maximale Steuerkorrektur (Cent)(SPA 209)
Hier wird angegeben, um welchen Centbetrag eine Steuer
maximal angepasst werden darf.
Der Wert 9999 führt dazu, dass eine Steuerkorrektur in
jedem Fall zulässig ist!

---

## Max. Steuer-Abweichung v. Vorgabe (Cent)(SPA 211)

Max. Steuer-Abweichung v. Vorgabe (Cent)(SPA 211)

---

## Zwischenergebnisse auf Gebinde-Masken(SPA 222)

Zwischenergebnisse auf Gebinde-Masken(SPA 222)

---

## Textzeilen im Kontenblatt zu vorh. Warenp.(SPA 269)

Textzeilen im Kontenblatt zu vorh. Warenp.(SPA 269)

---

## ReBuch-Sperre aus Quellvorgang übernehm.(SPA 273)

ReBuch-Sperre aus Quellvorgang übernehm.(SPA 273)
Bei Umwandlungen wird das Sperrkennzeichen für die
Übernahme des Vorgangs ins Rechnungsausgangsbuch bzw. Rechungseingangsbuch wie
folgt gesetzt (wenn es gesetzt ist, ist die Übernahme nicht
möglich):
gem. Unterklasse: das Kennzeichen wird aus der
Klasse/Unterklasse übernommen, wie es in der Zielklasse defaultmäßig vorbelegt
ist (FRZ/Formularzuordnung) aus der Quelle: das Kennzeichen wird aus dem
Quellvorgang in den Zielvorgang übernommen. setzen, n. löschen: das Kennzeichen
wird immer gesetzt für den Zielvorgang, in den umgewandelt wird.

---

## Druckmerker bei Korrektur zurücksetzen(SPA 276)

Druckmerker bei Korrektur zurücksetzen(SPA 276)

---

## Währungskurs bei Einzelumwandlung übern.(SPA 297)

Währungskurs bei Einzelumwandlung übern.(SPA 297)

---

## Objektverwaltung aktiv(SPA 3)

Objektverwaltung aktiv(SPA 3)
Ja: Das Modul Objektverwaltung ist, eingeschaltet.
Nein: Das Modul Objektverwaltung ist,
ausgeschaltet.

---

## Zu-/Abschläge bei Objekt-Bewegungen(SPA 323)

Zu-/Abschläge bei Objekt-Bewegungen(SPA 323)
Bei gezogenem Objekt werden allgemeine Zu/Abschläge
nur dann ausgewertet, wenn hier ein ‚Ja‘ ausgewählt wird.

---

## Istmengen zubuchen zur Sollmenge(SPA 328)

Istmengen zubuchen zur Sollmenge(SPA 328)

---

## Automatische Zu-/Abschläge(SPA 33)

Automatische Zu-/Abschläge(SPA 33)
Bei „Ja“ werden die automatischen Zu-/Abschläge
aktiviert.

---

## Separate Steuer auf Zu-/Abschl. möglich(SPA 330)

Separate Steuer auf Zu-/Abschl. möglich(SPA 330)

---

## Jahresgrenze Datumeingabe o. Jahrhundert(SPA 338)

Jahresgrenze Datumeingabe o. Jahrhundert(SPA 338)

---

## Aut. Formatierung für Zusatztext 1(SPA 339)

Aut. Formatierung für Zusatztext 1(SPA 339)
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Gutschrift aus Rechnung wie Stornorechnung(SPA 348)

Gutschrift aus Rechnung wie Stornorechnung(SPA
348)
Nein: Aus einer Rechnung können beliebig oft
Gutschriften (als Kopiervorlage) erstellt werden.
Ja: Es kann nur eine Gutschrift zu einer Rechnung
erstellt werden. Beide Belege sind gegen Weiterverarbeitung gesperrt. Ist die
Rechnung noch nicht in der FIBU, werden beide Belege für FIB als nn
gekennzeichnet.

---

## Aut. Formatierung für Zusatztext 2(SPA 340)

Aut. Formatierung für Zusatztext 2(SPA 340)
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Filiale in Vorgangskonstanten anpassen(SPA 351)

Filiale in Vorgangskonstanten anpassen(SPA 351)
Hier wird festgelegt, on die Vorgangskonstante für
Filiale [VKONS] durch Änderungen in der Vorgangserfassung vorbelegt werden soll.

---

## Trennung Gefahrgutsummen(SPA 352)

Trennung Gefahrgutsummen(SPA 352)

---

## Kursbezugswährung(SPA 360)

Kursbezugswährung(SPA 360)
Währungsnummer der Bezugswährung

---

## Vererbung AbteilungsId bei Umwandlung(SPA 378)

Vererbung AbteilungsId bei Umwandlung(SPA 378)
Die AbteilungsID / UnterabteilungsID wird bei
Umwandlung weitervererbt

---

## Kassenprotokoll in ASCII-Datei(SPA 383)

Kassenprotokoll in ASCII-Datei(SPA 383)
Hier wird entschieden, ob über die POS-Kasse erfasste
Vorgänge in einer Datei mitprotokolliert werden sollen, um auf einem
Ausfallsystem erfasste Vorgänge aus dieser Datei nachträglich einzuspielen. Die
Datei befindet sich in der Referenz-ERP-Root im Verzeichnis Export/kassprot. Dabei
wird pro Kasse, Bediener und Tag eine eigene Datei angelegt.

---

## Anbruch-Gebinde-Behandlung(SPA 39)

Anbruch-Gebinde-Behandlung(SPA 39)
Anbruch-Gebinde können unterschiedlich behandelt
werden: - normal - Anbruch - abrunden - aufrunden - aufrunden Stufe 2

---

## Rechnung trotz Liefersperre schreiben(SPA 391)

Rechnung trotz Liefersperre schreiben(SPA 391)
Für einen bestimmten Personenkreis ist es trotz
Liefersperre möglich, Rechnungen zu schreiben.

---

## Systemmakro-Anbindung(SPA 397)

Systemmakro-Anbindung(SPA 397)
Hier wird lizensiert, ob es möglich ist, Systemmakros
in Referenz-ERP einzubinden

---

## Kopfinformationen 1:1 bei Teildisp.Auftr(SPA 407)

Kopfinformationen 1:1 bei Teildisp.Auftr(SPA 407)

---

## Vorgangsnummer auf Zulässigkeit prüfen(SPA 431)

Vorgangsnummer auf Zulässigkeit prüfen(SPA 431)
Ja: bei manueller Eingabe einer Vorgangsnummer wird
überprüft, ob die manuell eingegebene Nummer innerhalb des zugehörigen
Zählkreises liegt. Wenn sie außerhalb liegt, wird die Eingabe verweigert.
Nein: Obige Überprüfung entfällt.

---

## Makro Fehlerlevel(SPA 432)

Makro Fehlerlevel(SPA 432)
0: Keine internen Fehler der Makroumgebung
ausgegeben.
1: nur schwere Fehler

---

## Steuer mit Defaultfindung(SPA 457)

Steuer mit Defaultfindung(SPA 457)
Wenn zu einer Steuerkombination kein Datensatz
gefunden wird, kann der Steuerkombination mit dem Schlüssel 0 gesucht
werden.
Es wird dringend empfohlen diesen Eintrag nicht auf Ja
zu setzen.

---

## Leergutverwaltung mit Jahresabgrenzung(SPA 487)

Leergutverwaltung mit Jahresabgrenzung(SPA 487)
Wird hier „Ja“ eingetragen, so wird für jedes Jahr ein
eigenes Konto geführt.

---

## DTINT-Verfahren aktiv(SPA 489)

DTINT-Verfahren aktiv(SPA 489)
Das DTINT Verfahren ist eine spezielle Variante des
DTA-Verfahrens. Es kann hier eingeschaltet werden, so dass beim DTA eine weitere
Funktion „DTINT“ zur Verfügung steht.

---

## Manuelle Erfassung von EC-Karten ?(SPA 505)

Manuelle Erfassung von EC-Karten ?(SPA 505)
SPA 505
1 –
      Eingabe möglich
EC-Karten-Daten dürfen manuell
      erfasst werden
2 –
      Eingabe unterbunden
EC-Karten dürfen nur über ein
      Lesegerät erfasst werden. Wenn das Lesegerät die EC-Karte nicht erkennt,
      wird automatisch in den Barzahlungsmodus zurückgeschaltet
3 –
      nur Kennzeichnung der Zahlungsart
wenn
      ein Zahlungssatz als EC-Karte gekennzeichnet ist, genügt diese
      Kennzeichnung bei manueller Erfassung, d.h. es müssen keine
      Zusatzinformationen wie BLZ, Kontonummer erfasst werden.

---

## Makrocache aktiv(SPA 513)

Makrocache aktiv(SPA 513)
Soll der Makrocache aktiv sein?

---

## Datum ltz.Korr. bei Umw.Sperr. J->N(SPA 514)

Datum ltz.Korr. bei Umw.Sperr. J->N(SPA 514)
Bei „Ja“ wird das Datum der letzten Korrektur (im
Vorgang)  nur bei einem Wechsel der Umwandelsperre von Ja auf Nein mit dem
aktuellen Tagesdatum belegt.

---

## Vorbelegung Partiewährung(SPA 517)

Vorbelegung Partiewährung(SPA 517)
Hier kann eingestellt werden, wie die Währung einer
neu angelegten Partie vorbelegt werden soll:
0: keine Vorbelegung, d.h. Währung 0
1: wie Belegwährung, d.h. gemäß der Währung des
Beleges
2: wie Buchwährung, d.h. entsprechend der
gewählten Buchwährung

---

## F1-Hilfe aktivieren(SPA 523)

F1-Hilfe aktivieren(SPA 523)
Ja: Die F1-Hilfe ist aktiviert.
Nein: Die F1-Hilfe ist deaktiviert.

---

## Gefahrgutmesszahl generiert Warnhinweis(SPA 519)

Gefahrgutmesszahl generiert Warnhinweis(SPA 519)
Ab diesem Wert wird beim Druck der Bereich 63:
Gefahrgutsummen Warnhinweis generiert.

---

## Referenz-ERP Mailsystem angeschlossen(SPA 527)

Referenz-ERP Mailsystem angeschlossen(SPA 527)
Ist das Referenz-ERP-Mailsystem angeschlossen?

---

## Periode/Jahr bei Einzelumwandlung(SPA 552)

Periode/Jahr bei Einzelumwandlung(SPA 552)
Bei Einzelumwandlungen werden Geschäftsjahr und
Periode wie folgt behandelt: „Original übernehmen“ = Jahr und Periode des
Quellbeleges werden übernommen „neu laut Belegdatum“ = Jahr und Periode werden
laut Belegdatum des neuen Beleges bestimmt.
Dieser Steuerparameter ist nicht wirksam für
Umwandlungen in Stornobelege.

---

## Warenflusskontrolle angeschlossen(SPA 551)

Warenflusskontrolle angeschlossen(SPA 551)

---

## Vorbelegung Formulararchiv-Referenznummer(SPA 554)

Vorbelegung Formulararchiv-Referenznummer(SPA 554)
Bei „Ja“ wird die Formulararchivnummer automatisch
vorbelegt. Falls unter Optionen „FA_Rereferenz_SQL“ ein SQL-Statement hinterlegt
ist, wird dies zur Gestaltung genommen. Falls dieses nicht existiert wird eine
Standardvorbelegung erzeugt.

---

## Eind. Rohw.Sa.Drucknr.<->Vorgangsnummern(SPA 560)

Eind. Rohw.Sa.Drucknr.<->Vorgangsnummern(SPA 560)

---

## Kostenträgerrechnung angeschlossen(SPA 569)

Kostenträgerrechnung angeschlossen(SPA 569)
Mit diesem SPA kann die Kostenträgerrechnung aktiviert
bzw. deaktiviert werden

---

## Bei Kostenträgern Oberkonten bebuchen?(SPA 570)

Bei Kostenträgern Oberkonten bebuchen?(SPA 570)
Wenn Auswertungen über Oberkonten und Kostenträger
erstellt werden sollen, kann man hier hinterlegen, dass auch bei Oberkonten die
Summenrelation der Kostenträger gefüllt wird. Da das Bebuchen durch die
Verwendung von Oberoberkonten und Verteilkostenträgern sehr Zeitintensiv sein
kann, steht dieser Parameter im Standard auf
Nein
.

---

## Gemeinsamer Zählkreis Finanzbelege(SPA 567)

Gemeinsamer Zählkreis Finanzbelege(SPA 567)
Nein (Standard): Finanzbelege Kasse erhalten je
Belegart (Einzahlung, Auszahlung, Einreichung, ...) einen eigenen aufsteigenden
Zählkreis. Die Nummer wird fortlaufend je Kasse bestimmt (ohne NK Zuordnung!).
Ja: Es wird nur ein gemeinsamer fortlaufender
Zählkreis für alle Finanzbelege einer Kasse geführt.

---

## Mehrere Partien pro Position zulässig(SPA 572)

Mehrere Partien pro Position zulässig(SPA 572)
Bei „Ja“ kann man einer Warenposition mehrere Partien
zuordnen, bei „Nein“ ist nur maximal eine Partiezuordnung möglich.

---

## Kostenstellen Dimensionen aktiv(SPA 582)

Kostenstellen Dimensionen aktiv(SPA 582)
Wenn man die Kostenstellen über die
Dimensionskriterien
ansprechen will,
muss man hier
Ja
eintragen.

---

## Protokoll abgebrochene Erfassungen Kasse(SPA 577)

Protokoll abgebrochene Erfassungen Kasse(SPA
577)
Abgebrochene Erfassungen von Kassenbelegen werden
elektronisch protokolliert. Maßgeblich für den Inhalt des Protokolls ist der
Status des Belegs zum Zeitprunkt des Abbruchs. Der Beleg ist in aller Regel
nicht vollständig erfasst gewesen, eine Zahlung ist nicht abgeschlossen
worden.

---

## Text erfassen mit Fixfont(SPA 585)

Text erfassen mit Fixfont(SPA 585)
Bei „Ja“ werden Texte wie Bemerkungen / Textbausteine
etc. wieder  wie bis zur 6. Version mit einem fixen Font erfasst
(gleichmäßige Breite der Zeichen). Bei „Nein“ wird eine proportionale Schriftart
verwendet.

---

## Überzahlung bei EC Cash zulässig(SPA 595)

Überzahlung bei EC Cash zulässig(SPA 595)

---

## Unterklasse für Fremdware ausbuchen (SPA 602)

Unterklasse für Fremdware ausbuchen (SPA 602)

---

## Aktionärsverwaltung aktiv(SPA 609)

Aktionärsverwaltung aktiv(SPA 609)

---

## DB-Serverdatum für Vorg-Neu-/-Korr.Datum(SPA 613)

DB-Serverdatum für Vorg-Neu-/-Korr.Datum(SPA 613)

---

## Unterschiedliche LGP in IVA(SPA 616)

Unterschiedliche LGP in IVA(SPA 616)

---

## Scanner Beibehaltung der Originalwerte(SPA 622)

Scanner Beibehaltung der Originalwerte(SPA 622)

---

## Buchstelle Belegdaten erstellen(SPA 624)

Buchstelle Belegdaten erstellen(SPA 624)

---

## Verpostung(SPA 625)

Verpostung(SPA 625)
Wird nicht mehr unterstützt.

---

## ESS-Anlagenbuchaltung angeschlossen(SPA 626)

ESS-Anlagenbuchaltung angeschlossen(SPA 626)
ESS Anlagenbuchhaltung ist ein externes System. Wenn
man hier
Ja
einträgt, wird bei Eingangsrechnungen direkt in diese
Anlagenbuchhaltung verzweigt.

---

## Kostenträger/ -stellen/ -arten bebuchen?(SPA 632)

Kostenträger/ -stellen/ -arten bebuchen?(SPA 632)
Wenn man mit Kostenstellen und Kostenträgern arbeitet,
dann will man evtl. auch Auswertungen über alle drei Kriterien erstellen. Dazu
dient die Summenrelation Kostensummen in der die Beträge pro Konto, Kostenstelle
und Kostenträger stehen. Diese Relation wird jedoch nur gefüllt, wenn hier ein
Ja
eingetragen ist.

---

## Auswahllisten keine NULL-Werte anzeigen(SPA 642)

Auswahllisten keine NULL-Werte anzeigen(SPA 642)
Felder aus Datenbanken ohne Ergebnis (technisch: Der
Wert des Feldes ist nicht besetzt!) werden  bei der Einstellung ‚Ja‘
mit  Punkten oder Leerstellen dargestellt. Bei ‚Nein‘ wird der logische
Ersatzwert  angezeigt (z.B. 0 bei einer Zahl, Leerstellen bei einem
Textfeld).

---

## Washout Unterklasse Eingangsrechnung (SPA 644)

Washout Unterklasse Eingangsrechnung (SPA 644)
Hier wird die Unterklasse für Eingangsrechnung beim
Washout-Circle angegeben.

---

## Washout Unterklasse Finalrechnung (SPA 646)

Washout Unterklasse Finalrechnung (SPA 646)
Hier wird die Unterklasse für Finalrechnung beim
Washout-Circle angegeben.

---

## Washout Unterklasse Ausgangsrechnung (SPA 645)

Washout Unterklasse Ausgangsrechnung (SPA 645)
Hier wird die Unterklasse für Ausgangsrechnung bei
Washout-Circle angegeben.

---

## Washout Unterklassen Gutschrift (SPA 647)

Washout Unterklassen Gutschrift (SPA 647)
Hier wird die Unterklasse für Gutschriften beim
Washout-Circle angegeben.

---

## Ware-Storno mit Quellbeleg-Kopie(SPA 656)

Ware-Storno mit Quellbeleg-Kopie(SPA 656)
Hier kann angegeben werden, ob die Option „Kopie nach
Storno“ bei der Umwandlung eines Beleges in einen Stornobeleg freigeschaltet
werden soll.

---

## Bezahlterminal Trace ins Fehlerprotokoll(SPA 671)

Bezahlterminal Trace ins Fehlerprotokoll(SPA 671)
Zur Klärung von Problemen in der Kommunikation
zwischen Referenz-ERP und dem Bezahlterminal kann die Kommunikation zwischen beiden
ins Fehlerprotokoll mitgeschnitten werden (Trace).
Diese Funktion sollte nicht dauerhaft eingeschaltet
bleiben, um die Übersichtlichkeit des Fehlerprotokolls nicht zu gefährden.

---

## Anzeige Fremdwährung in Auswahllisten(SPA 673)

Anzeige Fremdwährung in Auswahllisten(SPA 673)
Wird in der Finanzbuchhaltung Fremdwährung geführt, so
werden im Beleg diverse Informationen (z.B. Währungskurs, Betrag in
Fremdwährung, Steuer in Fremdwährung usw.) geführt. Diese werden in den
Auswahllisten dargestellt, wenn hier
Ja
eingetragen wurde. In der
Konteninfo steht dann auch eine weitere Variante „Konteninfo mit
Währungsauflösung“ zu Verfügung.
Dieser Steuerparameter steuert gleichzeitig, ob beim
Jahreswechsel zusätzlich ein Übertrag für Fremdwährung erstellt wird. Dieser
Übertrag wird u.a. für die Variante „Konteninfo mit Währungsauflösung“
benötigt.

---

## Währungskurs mit Webdaten überschreiben(SPA 675)

Währungskurs mit Webdaten überschreiben(SPA 675)

---

## Währungskurs x Tage zurück Web abrufen(SPA 676)

Währungskurs x Tage zurück Web abrufen(SPA
676)

---

## Ordersatz: WarenbewegungAddon übernehmen(SPA 686)

Ordersatz: WarenbewegungAddon übernehmen(SPA
686)
Bei „Ja“ werden alle Addon-Daten der Quellposition
übernommen.

---

## Storno ohne Stornobeleg (SPA 69)

Storno ohne Stornobeleg (SPA 69)
Bei „Ja“ wird auf ein Stornoschreiben verzichtet.

---

## Vorkasse Ladescheinunterklasse(SPA 693)

Vorkasse Ladescheinunterklasse(SPA 693)
Unterklassennummer für den Vorkasse Ladeschein

---

## Transaktionsnummer in Reporten/Auswahllisten anzeigen(SPA 700)

Transaktionsnummer in Reporten/Auswahllisten anzeigen(SPA 700)
Die Transaktionsnummer ist die interne Nummer des
Belegs. Diese ist eindeutig im Gesamtsystem und wird nur vom System vergeben.
Stellt man diese SPA auf
Ja
, so wird sie in Reporten, Auswahllisten und
der Einzelbeleganzeige mit angezeigt.

---

## Negative Rechnungs/Gutschriftssumme(SPA 70)

Negative Rechnungs/Gutschriftssumme(SPA 70)
Bei „Nein“ lässt Referenz-ERP keine negativen Endbeträge
zu.

---

## Vorgangsdatum bei Periodenabweichung aus offener Periode vorbelegen(SPA 708)

Vorgangsdatum bei Periodenabweichung aus offener Periode vorbelegen(SPA
708)
Üblicherweise wird das Belegdatum eines Vorgangs mit
dem aktuellen Tagesdatum vorbelegt. Wird bei einer Periodenabweichung (Periode
zum Tagesdatum ist gesperrt) eine Ersatzperiode bestimmt, so wurde bisher das
Belegdatum hierdurch nicht verändert. Bei der Einstellung „Ja“ wird jetzt das
Belegdatum in Vorgängen im Ein – und Verkauf mit dem Periodenanfang bei
nachfolgenden Perioden oder mit dem Periodenende bei vorangehenden Perioden
belegt. Mit den Optionen „Nur im Einkauf“ und „Nur im Verkauf“ erfolgt eine
getrennte Einstellung für den Ein- und Verkauf. So wird bei der
Auswahlmöglichkeit „Nur im Einkauf“ das Belegdatum für Vorgänge
nur
im
Einkauf anhand der Ersatzperiode vorbelegt, während für Vorgänge im Verkauf
weiterhin das Tagesdatum als Vorbelegung gilt.
Hinweis: Zum Einkauf werden auch die Umbuchung,
Produktion und weitere nicht verkaufsorientierte Vorgänge gezählt.

---

## Negative Warenmengen zulässig (SPA 71)

Negative Warenmengen zulässig (SPA 71)
Bei „Nein“ können keine negativen Mengen erfasst
werden.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Max. Vorkomma Mengen (0=ohne Prüfung)(SPA 73)

Max. Vorkomma Mengen (0=ohne Prüfung)(SPA 73)
Hier kann die maximal zulässige Vorkomma- Stellenzahl
für Mengen eingegeben werden. Der Wert wird bei der Erfassung geprüft. Bei 0
erfolgt keine Prüfung.

---

## UPCA Erkennung in der Scannersoftware ausschalten. (SPA 732)

UPCA Erkennung in der Scannersoftware ausschalten. (SPA 732)
Hiermit kann die UPCA Erkennung im AeinsCE ausgestellt
werden. Gescannte UPCA Codes werden mit einer -1 an die Datenbank übertragen und
zurückgewiesen.

---

## Ausblenden der Taskleiste auf dem Scanner. (SPA 736)

Ausblenden der Taskleiste auf dem Scanner. (SPA 736)
Blendet die Taskleiste aus.

---

## Codeverarbeitung ind er Scanner Software. (SPA 737)

Codeverarbeitung ind er Scanner Software. (SPA 737)
Soll die Scancode Ermittlung im Scanner durchgeführt
werden

---

## ILN nicht aus dem AI 01 ermitteln. (SPA 739)

ILN nicht aus dem AI 01 ermitteln. (SPA 739)
Hiermit wird die automatische ILN Ermittlung
ausgestellt.

---

## Trigger Verarbeitung oder speichern der Daten in der Relation (TCPIP_Scannerdatenuebergabe). (SPA 740)

Trigger Verarbeitung oder speichern der Daten in der Relation
(TCPIP_Scannerdatenuebergabe). (SPA 740)
Hier kann eingestellt werden, ob die über den Trigger
Datenstromscanner_ins verarbeitet werden oder in der Relation
Tcpip_Scannerdatenübergabe landen. Bei der Verarbeitung über die Relation
Tcpip_Scannerdatenübergabe muss auf der Maske Tcpip_Scanner der Server gestartet
werden. In diesem Modus lassen sich nur Eingangslieferscheine und Aufträge
bearbeiten

---

## Max. Vorkomma Werte (0=ohne Prüfung)(SPA 74)

Max. Vorkomma Werte (0=ohne Prüfung)(SPA 74)
Hier kann die maximal zulässige Vorkomma- Stellenzahl
für Werte eingetragen werden. Dieser wird bei der Erfassung überprüft. Wenn 0
eingetragen ist, erfolgt keine Prüfung

---

## Warten auf Antwort.(SPA 741)

Warten auf Antwort.(SPA 741)
Hier kann eingestellt werden, ob auf Rückantwort vom
Server gewartet werden soll, wenn die Daten in die Tabelle Tcpip
Scannerdatenübergabe gespeichert werden soll.

---

## Statusliste für Fehlerwave. (SPA 745)

Statusliste für Fehlerwave. (SPA 745)
Hier kann noch eingetragen werden welcher
Datenstromscanner Status ein Fehler ist.
Status 5,7

---

## Statusliste für Erfolgwave. (SPA 747)

Statusliste für Erfolgwave. (SPA 747)
Hier wird eingetragen, welcher Datenstromscanner
Status für einen Erfolgreichen Scann Vorgang steht.
Status 0,4,6

---

## Schriftgröße Aktionstext. (SPA 748)

Schriftgröße Aktionstext. (SPA 748)
Hier kann die Schriftgröße für den Aktionstext gesetzt
werden.

---

## Schriftname Aktionstext. (SPA 749)

Schriftname Aktionstext. (SPA 749)
Hier kann der Schriftname für den Aktionstext gesetzt
werden.

---

## Schriftname Kopftext1. (SPA 752)

Schriftname Kopftext1. (SPA 752)
Hier kann der Schriftname für den Kopftext1 gesetzt
werden.

---

## Schrifttyp Aktionstext. (SPA 750)

Schrifttyp Aktionstext. (SPA 750)
Hier kann der Schrifttyp für den Aktionstext gesetzt
werden.

---

## Schriftgröße Kopftext1. (SPA 751)

Schriftgröße Kopftext1. (SPA 751)
Hier kann die Schriftgröße für den Kopftext1 gesetzt
werden.

---

## Schrifttyp Kopftext1. (SPA 753)

Schrifttyp Kopftext1. (SPA 753)
Hier kann der Schrifttyp für den Kopftext1 gesetzt
werden.

---

## Schriftgröße Kopftext2. (SPA 754)

Schriftgröße Kopftext2. (SPA 754)
Hier kann die Schriftgröße für den Kopftext2 gesetzt
werden.

---

## Schriftname Kopftext2. (SPA 755)

Schriftname Kopftext2. (SPA 755)
Hier kann der Schriftname für den Kopftext2 gesetzt
werden.

---

## Schrifttyp Kopftext2 (SPA 756)

Schrifttyp Kopftext2 (SPA 756)
Hier kann der Schrifttyp für den Kopftext2 gesetzt
werden

---

## Schriftgröße Statustext. (SPA 757)

Schriftgröße Statustext. (SPA 757)
Hier kann die Schriftgröße für den Statustext gesetzt
werden.

---

## Schriftname Statustext. (SPA 758)

Schriftname Statustext. (SPA 758)
Hier kann der Schriftname für den Statustext gesetzt
werden.

---

## Max. Vorkomma Prozente (0=ohne Prüfung)(SPA 76)

Max. Vorkomma Prozente (0=ohne Prüfung)(SPA 76)
Hier kann die maximal zulässige Vorkomma- Stellenzahl
für Prozente eingetragen werden. Diese wird bei der Erfassung überprüft. Ist
hier 0 eingetragen, erfolgt keine Prüfung.

---

## Schrifttyp Statustext (SPA 759)

Schrifttyp Statustext (SPA 759)
Hier kann der Schrifttyp für den Statustext gesetzt
werden

---

## Schriftgröße Itembox. (SPA 760)

Schriftgröße Itembox. (SPA 760)
Hier kann die Schriftgröße für den Itembox gesetzt
werden.

---

## Vieraugenprinzip(SPA 763)

Vieraugenprinzip(SPA 763)
Dieser Steuerparamater wird nicht mehr benutzt und ist
in der Gruppe deaktiviert verschoben worden.

---

## Schrifttyp Itembox (SPA 762)

Schrifttyp Itembox (SPA 762)
Hier kann der Schrifttyp für den Itembox gesetzt
werden

---

## Schriftname Itembox. (SPA 761)

Schriftname Itembox. (SPA 761)
Hier kann der Schriftname für den Itembox gesetzt
werden.

---

## Itembox Gebinde(SPA 767)

Itembox Gebinde(SPA 767)
Hier kann eine private Itembox für die Gebinde Auswahl
für die eigene Scanner-Maske hinterlegt werden.

---

## Name des alternativen VBA-Scriptes für vde Update-Fall (SPA 775)

Name des alternativen VBA-Scriptes für vde Update-Fall (SPA 775)
Der im Feld Option eigetragene Wert (F3-Funktion) gibt
den Namen des zu verwendenden VBA-Skriptes für Vendor_Data_Extract im Fall von
Änderungen aus. Dieses sorgt dafür, das im Fall von bestimmten getätigten
Änderungen, wenn gewünsct per FTP transportiert werden.

---

## Sortierung Formularauswahl Lieblingsdrucker (SPA 776)

Sortierung Formularauswahl Lieblingsdrucker (SPA 776)
Hier kann eingestellt werden in welcher Reihenfolge
die Formulare in der Maske Lieblingsdruckerdruck angezeigt werden.
(VRGD/FRZ)

---

## Name des alternativen VBA-Scriptes für vde Kopier-Fall (SPA 779)

Name des alternativen VBA-Scriptes für vde Kopier-Fall (SPA 779)
Der im Feld Option eigetragene Wert (F3-Funktion) gibt
den Namen des zu verwendenden VBA-Skriptes für Vendor_Data_Extract aus. Dieses
sorgt dafür, dass die täglichen und monatlichen Reporte an die gewünschte Stelle
kopiert werden.

---

## Caches löschen (SPA 781)

Caches löschen (SPA 781)
Bestimmt ob die System-Caches bei Wiedereintritt in
die Referenz-ERP-Haupt-Menü-Maske zurückgesetzt werden.

---

## FNC1 Textersetzung für Datalogic Scanner (SPA 785)

FNC1 Textersetzung für Datalogic Scanner (SPA 785)
Hier kann eine Textersetzung des FNC1 Codes
eingetragen werden und zwar in dieser Form 126/29. Die erste Zahl ist für die
Ersetzung von FNC1 zu einem beliebigen Zeichen die zweite Zahl gibt an welches
nicht druckbare Zeichen als FNC1 genommen werden soll.

---

## Test SPA 2(SPA 787)

Test SPA 2(SPA 787)
Test SPA wurde in die Gruppe deaktiviert
verschoben.

---

## Archiv-Richtlinien auch in privaten Ansichten berücksichtigen (SPA 782)

Archiv-Richtlinien auch in privaten Ansichten berücksichtigen (SPA 782)
Ebendies.

---

## Test SPA1 (SPA 786)

Test SPA1 (SPA 786)
Test SPA wurde in die Gruppe deaktiviert
verschoben

---

## Test SPA 3(SPA 788)

Test SPA 3(SPA 788)
Test SPA wurde in die Gruppe deaktiviert
verschoben.

---

## Test SPA wurde in die Gruppe deaktiviert verschoben Scanner-Scanner Testmitschrift aktivieren (SPA 789)

Test SPA wurde in die Gruppe deaktiviert verschoben Scanner-Scanner
Testmitschrift aktivieren (SPA 789)
Die gescannten Befehle einer Sitzung (eines Scanners)
können in eine Testtabelle geschrieben werden, um sie später zu
Validierungszwecken wieder aufzurufen. Im Optionswert wird der Name der
Mitschrift gesetzt, der Schlüssel steuert die individuelle Scanner-Zuordnung (im
Regelfall die IP Adresse). Der Wert steuert den Start der Mitschrift
(Ja/Nein).

---

## Signatur aktiv (SPA 823)

Signatur aktiv (SPA 823)
Diese Einstellung legt fest, ob elektronische Signatur
eines Pdf aktiv sein soll. Signaturlösungen werden stets individuell angebunden
und sind in dieser Hilfe derzeit nicht beschrieben.

---

## Max Intervall für Verbotslistenprüfung in Tagen (SPA 824)

Max Intervall für Verbotslistenprüfung in Tagen (SPA
824)
Hier hinterlegen Sie für die Verwendung der
regelmäßigen Verbotslistenprüfung eine Anzahl von Tagen, die maximal zwischen
zwei Tagen verstreichen darf.

---

## Aktuelles Tagesdatum ändern erlaubt? [DAT] (SPA 838)

Aktuelles Tagesdatum ändern erlaubt? [DAT] (SPA
838)

---

## Automatischer Zahlungsverkehr ohne Formularzuordnung (SPA 845)

Automatischer Zahlungsverkehr ohne Formularzuordnung (SPA 845)
Im automatischen Zahlungsverkehr wird das Formular für
den Scheckdruck über die einer Bank zugeordneten Zahlungsformulare bestimmt.
Dies geschieht bereist bei der Freigabe der Zahlungsvorschläge unabhängig, ob
DTA oder Scheckdruck verwendet wird. Stellt man diesen Parameter auf
Ja
,
so erfolgt die Bestimmung des Formulars erst beim
Scheckdruck
.

---

## Passthrough Modus aktivieren (SPA 851)

Passthrough Modus aktivieren (SPA 851)
Passthrough-Modus zum Replizieren von Strukturbefehlen
deaktivieren oder aktivieren. Standardmäßig ist der Passthrough-Modus
aktiviert.

---

## Makros bei Ansicht eines Vorgangs ausführen (SPA 862)

Makros bei Ansicht eines Vorgangs ausführen (SPA 862)
Einstellungen
Immer
Es
      werden immer alle Makros ausgeführt
Nur
      AIS-Makros
Es
      werden im Ansehen-Modus nur AIS-Makros ausgeführt
Nur
      Vorgangsmakros
Es
      werden im Ansehen-Modus nur Vorgangs-Makros ausgeführt
Nie
Es
      werden im Ansehen-Modus keine Makros ausgeführt

---

## Felder bei Gutschein in der Marktkasse (SPA 863)

Felder bei Gutschein in der Marktkasse (SPA 863)
Hier wird festgelegt welche Felder bei
Gutscheinbehandlung in der Marktkasse abgefragt werden sollen.
Wert
Bedeutung
0
Keine Felder
1
Nur
      Gutscheinnummer
2
Gutscheinnummer und
      Bemerkungen

---

## Behandlung nicht aufgelöster Vorgangstexte (SPA 884)

Behandlung nicht aufgelöster Vorgangstexte (SPA
884)
Den Vorgangsklassen können Texte zugeordnet werden,
die Platzhalter enthalten, welche schließlich durch manuelle Eingabe aufgelöst
werden. Diese Auflösung findet je nach Einstellung vor Beginn der
Positionsteilerfassung oder vor dem Abschluss der Erfassung statt.
Bei der Umwandlung eines Vorgangs in einen neuen
Vorgang einer anderen Vorgangsklasse (z.B. von Angebot in Auftrag) findet keine
Erfassung statt und damit auch keine Auflösung dieser Texte. Aus diesem Grund
ist eine Behandlung der Texte erforderlich, damit im erstellten Beleg keine
Platzhalter dargestellt werden.
Mit Hilfe dieses Steuerparameters kann die Behandlung
der Vorgangstexte bei Umwandlung festgelegt werden.
Die gleiche Behandlung wird bei der Erstellung eines
Vorgangs mit Makro durchgeführt, da auch hier keine Auflösung durch manuelle
Eingabe erfolgen kann.
Einstellungen
0 –
      nichts ändern
Diese Einstellung ist die
      voreingestellte Behandlung
[...]


---

## Zentrale in Vorgangskonstanten anpassen (SPA 891)

Zentrale in Vorgangskonstanten anpassen (SPA
891)
Hier wird festgelegt, on die Vorgangskonstante für
Zentrale [VKONS] durch Änderungen in der Vorgangserfassung vorbelegt werden
soll.

---

## Abteilung in Vorgangskonstanten anpassen (SPA 892)

Abteilung in Vorgangskonstanten anpassen (SPA
892)
Hier wird festgelegt, on die Vorgangskonstante für
Abteilung [VKONS] durch Änderungen in der Vorgangserfassung vorbelegt werden
soll.

---

## IBAN Vorbelegung nach Standardverfahren (SPA 896)

IBAN Vorbelegung nach Standardverfahren (SPA
896)
Die IBAN wird für Belgien, Österreich und Deutschland
automatisch aus Bankleitzahl und Kontonummer gebildet. Dies geschieht nach dem
Standardverfahren. Es gibt jedoch Banken, die ein abweichendes Verfahren für
ihre IBAN’s verwenden. Daher müssen die hier vorgeschlagenen IBAN’s in jedem
Fall kontrolliert werden. Will man lieber gleich auf den Vorschlag verzichten
kann man hier die Vorbelegung ausschalten.

---

## Druckeinstellungen(SPA 907)

Druckeinstellungen(SPA 907)
Hier können allgemeine Druckeinstellungen für Referenz-ERP
festgelegt werden. Folgende Typen stehen zur Verfügung.
Typ
Wert
Lieblingsdrucker VRGD Makro
      ausführen
Hier
      kann eingestellt werden, wie die Vorbelegung für das Ausführen der
Vorgangsdruckklassen
Makros auf der
Lieblingsdrucker
Maske
      ist.

---

## Terres Belegexport Belegnummer (SPA 911)

Terres Belegexport Belegnummer (SPA 911)
Hier wird eine alternative Prozedur zur Bestimmung der
Terresbelegnummer hinterlegt.

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

## Onlinehilfe(SPA 921)

Onlinehilfe(SPA 921)
Legt fest ob die Aeins-Internet-Hilfe verwendet werden
soll.

---

## Archiv-Vorgänge mit Löschkennzeichen versehen?(SPA 937)

Archiv-Vorgänge mit Löschkennzeichen versehen?(SPA 937)
Standard : Nein
Damit werden u.a. beim Storno von Vorgängen die
zugehörigen Archiv-Vorgänge nicht mit Löschkennzeichen versehen, was praktisch
bedeutet, sie werden nicht gelöscht.

---

## openTRANS Position mit GUID (SPA 945)

openTRANS Position mit GUID (SPA 945)
Im openTRANS-Export wird die Position mit einer
laufenden Nummer aus dem Vorgang in der LINEID bezeichnet. Um eine Eindeutigkeit
zu erreichen, kann jedoch die GUID der Warenbewegung hier exportiert werden.
Dazu muss der SPA auf „JA“ gestellt werden.

---

## Formularinfo beim Drucken ganz unten (SPA 936)

Formularinfo beim Drucken ganz unten (SPA 936)
Man kann mit dieser Einstellung beim Formulardruck am
unteren Rand des Formulars auf dem letzten Blatt eine Kurzinformation ausgeben
lassen (nur im Windows-Druckmodus!):
0: keine Ausgabe (Standardeinstellung)
1: Ausgabe der Formularid
2: erweiterte Informationen: Mandant, Formularid,
Bediener, Datum, Uhrzeit

---

## CSMakro Debug-Besitzer (SPA 942)

CSMakro Debug-Besitzer (SPA 942)
Der Besitzer, der hier eingetragen ist, ist jener,
dessen Makro im Debug-Modus ausgeführt wird, wenn es mehrere Makros des gleichen
Namens aber unterschiedlicher Besitzer gibt. In der Regel wird für hier nur der
Besitzer 1 eingetragen. Die Verwendung abweichender Werte ist ausschließlich dem
erfahrenen Support in entsprechender Umgebung vorbehalten.
Bitte verstellen Sie diesen Parameter nicht,
wenn Sie nicht sicher sind, welche Auswirkungen dies hat!

---

## Gelangensbestätigung bei Belegkorrektur (SPA 948)

Gelangensbestätigung bei Belegkorrektur (SPA 948)
Die Einstellung „Ja“ bewirkt das nach Belegkorrektur
wieder eine neue Gelangensbestätigung gedruckt werden kann.

---

## Zahlungsart Scheck aktiv (SPA 955)

Zahlungsart Scheck aktiv (SPA 955)
Soll die Zahlungsart Scheck aktiviert sein (Standard:
Nein).
Die Zahlungsart Scheck steht bei Einstellung „Nein“
nicht zur Verfügung.

---

## Zahlungsart Bankeinzug aktiv (SPA 956)

Zahlungsart Bankeinzug aktiv (SPA 956)
Soll die Zahlungsart Scheck aktiviert sein (Standard:
Nein).
Die Zahlungsart Bankeinzug steht bei Einstellung
„Nein“ nicht zur Verfügung.

---

## LVS Standort Leerpaletten (SPA 978)

LVS Standort Leerpaletten (SPA 978)
Hier wird die LVS-Lokalität angegeben, auf die
leergebuchte Ladeträger versetzt werden können. Dieser SPA dient nur als
Speicherstelle für diese Lokalität. Die Verwendung muss manuell in Makros oder
Prozeduren implementiert werden.

---

## Mindestzahlbetrag EC-Überzahlung (SPA 983)

Mindestzahlbetrag EC-Überzahlung (SPA 983)
Hier kann ein Betrag eingetragen werden, der in der
Marktkasse ausgewertet wird, um bei Zahlungen mit EC-Karte auch Barauszahlungen
zu ermöglichen. Wird der Rechnungs/Zahlbetrag um den hier eingestellten Wert
überschritten, so wird bei Zahlung mit EC-Karte ein Dialog geöffnet, der die
Eingabe eines auszuzahlenden Betrags abfragt. Um diesen Betrag wird dann der
Rechnungsbetrag erhöht und an das EC-Gerät gesendet.
Ist der Wert 0, so wird diese Abfrage nie erfolgen.

---

## Port für TCPIP-Server (SPA 982)

Port für TCPIP-Server (SPA 982)
Für Remote-Debugging kann ein TCPIP-Server zur
Verfügung gestellt werden. Der Port dieses Servers kann hier abweichend
festgelegt werden.

---

## Projektverwaltung (SPA 989)

Projektverwaltung (SPA 989)
Im Bereich der Projektverwaltung können hier
Individualisierungen eingetragen werden. Bitte per F3 die entsprechenden
Ausprägungen einsehen.

---

## Saatzucht

Saatzucht

---

## Scanner

Scanner

---

## Scanner

Scanner

---

## Scanner

Scanner

---

## Scanner

Scanner

---

## Signature Pad benutzen

Signature Pad benutzen
Dieses Kapitel zeigt die beispielhafte Signatur eines
PDF-Dokuments in der Dokumentenverwaltung [ORDNER].

---

## Ausführen von Skripten zulassen

Ausführen von Skripten zulassen
Die Steuerung des Replikationssystems erfolgt
teilweise über Powershell-Skripte. Dies bedeutet dafür zu sorgen, dass diese
Skripte auf dem System auch ausgeführt werden dürfen. Dies erreicht man am
einfachsten durch das Setzen des „ExecutionPolicy“-Wertes über die
Powershell.
Dazu rufen Sie bitte eine Powershell mit
Administrator-Rechten auf und geben folgenden Befehl ein:
Set-ExecutionPolicy
unrestricted
Hiermit wird das Ausführen von Skripten erlaubt.

---

## Textersetzungsmodule

Textersetzungsmodule
Hauptmenü
Systempflege
Individuelle Textersetzung
Direktsprung
[TEXTM]
Hier lassen sich die Module erstellen, die für die
Verwendung der individuellen Textersetzung zuständig sind.
Feld
Beschreibung
Modulnummer
Nummer für das Modul
Bezeichnung
Bezeichnung des Moduls
Verwendung
Ja/Nein Auswahl
Entscheidet darüber, ob ein Modul
      und damit die individuelle Textersetzung verwendet werden soll.
Ja:
Hierbei werden bei einem Kunden ALLE
      Bediener mit der Sprachnummer 0 (Standard deutsch)  auf die
      Sprachnummer 1000 umgestellt.
Nein:
Soll
      kein Modul mehr verwendet werden, also auch keine individuellen Texte, so
      werden auch ALLE Bediener wieder zurück gestellt.
Das Programm prüft bei Verwendung eines Moduls ob die
Sprachnummer 1000 bereits existiert. Ist sie noch nicht vorhanden, wird sie
automatisch angelegt. Weiterhin werden die alternativen Texte die für dieses
Modul gespeichert sind in die Sprache 1000 – Alternativtexte übertragen. So
[...]


---

## Vorgangsbearbeitung

Vorgangsbearbeitung

---

## Vorgangsbearbeitung

Vorgangsbearbeitung

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Warenwirtschaft

Warenwirtschaft

---

## Problemfälle VorgReservierung

Problemfälle VorgReservierung
Hier können Problemfälle in der Vorgangsreservierung
korrigiert werden.
Beschriftung
Funktion
V_Klassnummer
Hier
      kann die Nummer der Vorgangsklasse eingegeben werden.
V_NumNummer
Hier
      kann die Belegnummer eingegeben werden.
Problemfälle laden!
Sucht fehlerhafte
      Vorgänge.
Mit
      V_Id = 0
Sucht fehlerhafte Vorgänge mit V_Id
      = 0
VorgReserv. Löschen
Löscht den ausgewählten Vorgang aus
      der VorgReservierung. Das Löschen der VorgReservierung wird in der
      Relation WareoProtokoll protokolliert.
Es werden fünf Problemfälle unterschieden:
Typ 1: Vorgang ist komplett mit der richtigen
Vorgreservierung verbunden
Typ 2: Eintrag in Vorgreservierung fehlt
Typ 3: VorgangStamm fehlt
Typ 4: Vorgreservierung mit V_Id != 0 nicht in
V_Position
Typ 5: Vorgreservierung mit V_Id != 0 nicht in
Vorgangstamm
Die Spalte „*“ zeigt Vorgänge mit gleicher ErfassId.
Diese sind wahrscheinlich durch Korrektur hervor gegangen.

---

## Warenwirtschaft

Warenwirtschaft

---

## Zahlungsverkehr

Zahlungsverkehr

---

## Zinswesen

Zinswesen

---

## Dokumentenverwaltung (EPA a1netarchiv.ViewDialog)

Dokumentenverwaltung (EPA a1netarchiv.ViewDialog)
Bezeichnung
Standardwert
Erklärung
TESTFUNKTION
Möglichkeit Funktionen zum Test
      freizuschalten.

---

## A1netCom.Tester.exe

A1netCom.Tester.exe
Dieses Programm kann über die
Kommandozeile
ausgeführt
werden und gibt Auskunft darüber, ob das Referenz-ERP-COM-Objekt verfügbar ist.

---

## Abkündigung: A1extern.dll

Abkündigung: A1extern.dll
Die A1extern.dll ist ein Programmierinterface, welches
hauptsächlich von unseren Systemhäusern verwendet wurden. Dies betrifft auch
Entwicklungen, die seinerzeit von der GS Computersysteme GmbH in Pleidelsheim
mit Programmierwerkzeugen wie Delphi getätigt wurden. Vielen Anwendern kennen
solche Lösungen unter dem Begriff Kratochwil-Anwendungen. Der Einsatz dieser
Lösungen ist mit der 64-Bit Version nicht mehr möglich. Sollten Sie wissentlich
solche Lösungen einsetzen, sprechen Sie uns an. Im Rahmen des Updates werden wir
solche Funktionalitäten prüfen. Ein Update auf die 64-Bit Version ist nur
möglich, wenn diese Individualentwicklungen auf neuere Technologien umgesetzt
wurden.Zu erkennen ist dies, in dem Sie unter MAKRO nach der A1extern.dll
suchen:[MAKRO] -> (F2) -> Makroname: "%a1extern.dll%"Wenn hier einige
MAKROS erscheinen, besteht das Risiko, dass Sie von der Abkündigung betroffen
sind. In dem Fall vereinbaren Sie bitte einen Termin mit einem
[...]


---

## Abkündigung: Wechselbuchhaltung

Abkündigung: Wechselbuchhaltung
Schon vor vielen Jahren verloren mit Wegfall der
Refinanzierungsmöglichkeit bei Banken Wechsel ihre Bedeutung. Mit der 64-Bit
Version wird die Wechselbuchhaltung ersatzlos gestrichen.
Tags:
Abkündigung

---

## Abkündigung: Tammo MAPI

Abkündigung: Tammo MAPI
In der Anwendung E-Mail-Connector wurde das
Mailplugin für MAPI entfernt.
Tags:
Abkündigung

---

## Excelimport von xls-Dateien

Excelimport von xls-Dateien
Excelimport von .xls-Dateien ausgebaut. Dies war nur
noch in der 32Bit-Version möglich. Beim Excelimport über dbx_import kommt jetzt
ein Fehlerprotokoll-Eintrag mit einem Hinweis, dass stattdessen die Funktion
^excelimport_execute verwendet werden soll.
Tags:
Abkündigung

---

## Abkündigung: Infocenter

Abkündigung: Infocenter
Die Möglichkeiten des Archivs und des Dashboards
machen eine weitere notwendige Software-Pflege des "Info-Center" im Haupt-Menü
obsolet. Dieser Programmteil wurde entfernt.
Tags:
Abkündigung

---

## Abgrenzung (Archiv)

Abgrenzung (Archiv)
Gilt das im Wesentlichen unter „Dateisystem –
Abgrenzung“ gesagte.

---

## Absetzung für außergewöhnliche Abnutzung / AfaA

Absetzung für außergewöhnliche
Abnutzung / AfaA
Die Absetzung für außergewöhnliche Abnutzung (AfaA)
entspricht der außerplanmäßigen Abschreibung des § 253 Abs2 HGB, wobei mit der
AfaA regelmäßig ein Substanzverlust einhergeht, der sich auf die
Restnutzungsdauer auswirkt. Man muss hier zusätzlich zum AfaA Betrag auch die
neue Lebensdauer – Achtung:
Nicht
die neue Restnutzungsdauer – erfassen.
AfaA wird in der Anlagenbuchhaltung in der Historie
über die Art
AfaA
erfasst. Es wird dabei automatisch ein Beleg in die
Primanota der Finanzbuchhaltung gestellt. Dazu werden beim Speichern des
Anlagegutes noch ein paar Werte abgefragt:
In dem folgenden Beispiel wurde ein Anlagegut mit
einer Nutzungsdauer von 8 Jahren für 10.000,00 Euro angeschafft. Nach 2 Jahren
wurde eine AfaA durchgeführt und die Nutzungsdauer mit 6 Jahren neu festgelegt.

---

## Referenz-ERP Hinweis

Referenz-ERP Hinweis

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
Einrichtung des AIS für die Vo
[...]


---

## Aktientransaktionen / Die Historische Tabelle

Aktientransaktionen / Die Historische Tabelle
In der Historischen Tabelle, die von den Listen
„Aktionärsübersicht“, „Gesamtliste“ und „Aktionärsdividende“ aus aufgerufen
werden kann, können die Aktientransaktionen für einen Aktionär erfasst und
gepflegt werden. Die Maske wird für den in der Liste angewählten Aktionär
gestartet. Dieser gilt als Hauptaktionär und seine Daten werden auf der linken
Seite dargestellt. Es ist allerdings auch möglich, im Feld der Aktionärsnummer
einen anderen Aktionär anzuwählen. In der unteren Tabelle werden die
Transaktionen für diesen Aktionär in chronologischer Reihenfolge angezeigt. Die
angewählt werden können. Die Daten für die gewählte Transaktion werden in der
Mitte der Maske dargestellt und können dort editiert werden. Die oberste
Transaktion wird automatisch beim Öffnen der Maske ausgewählt [vergleiche
Die Unternehmensdaten
einrichten/verwalten
].
Folgende Einstellungen können in dieser Maske per
Einrichterparameter vorgenommen werden:
•
[...]


---

## Aktionärsübersicht

Aktionärsübersicht
In der Aktionärsübersicht wird eine Übersicht über
alle Aktionäre angezeigt. Für jeden Aktionär wird die Aktionärsnummer, Nachname,
Vorname Geburtsdatum, Straße, Postleitzahl, Ort, Vertreter, Status,
Aktienanzahl, Nominalwert, Wert, Eintrittsdatum, Austrittsdatum angezeigt.
Näheres zu den angezeigten Eigenschaften finden Sie unter
Aktionäre verwalten
.
Über
Bereich/Profile
kann nach folgenden
Kriterien eingeschränkt werden: Name, Vorname, Aktionärsnummer (von, bis),
Geburtsdatum (von, bis), Straße (von, bis), Postleitzahl (von, bis), Ort,
Vertreter, Status von, Status bis, Aktienanzahl (von, bis), Eintrittsdatum (von,
bis), Austrittsdatum (von, bis) und Wirtschaftsjahr.
Das Datum, das bei der Berechnung des Bestandes
zugrunde liegt ist entweder das Tagesdatum oder falls unter „Bereich/Profile“
ein Wirtschaftsjahr angegeben wird das Enddatum dieses Wirtschaftsjahres. Zur
Berechnung des Nominalwertes und des Wertes werden die Unternehmensdaten, die an
diese
[...]


---

## Aktionärsverwaltung

Aktionärsverwaltung

---

## Aktionärsdividende

Aktionärsdividende
In der Ansicht „Aktionärsdividende“ sind die
Dividendenausschüttungen, die die Aktionäre für ein Wirtschaftsjahr erhalten
aufgelistet. Es können auch Daten für zukünftige Wirtschaftsjahre angesehen
werden, sobald Dividendendaten für den gewünschten Zeitraum eingetragen sind.
Dadurch, dass die Möglichkeit besteht, dass die ausgeschüttete Dividende für ein
Aktienpaket in einem Wirtschaftsjahr zwischen zwei Aktionären geteilt wird
[siehe
Aktientransaktionen / Die
Historische Tabelle
], kann ein Aktionär auch mehrfach in dieser Ansicht
auftauchen. Es werden folgende Daten für eine Zahlung angezeigt:
Aktionärsnummer, Nachname, Vorname, Geburtsdatum, Straße, Postleitzahl, Ort,
Vertreter, Status, Stückaktien, Zeitraum, Kapitalertragssteuer,
Solidaritätszuschlag, Nettodividende, Freistellung, Dividende, gebucht.
Dividende gibt an, welche Dividende für die Berechnung verwendet wurde. Zeitraum
gibt an für welche Zeit der Dividende die Zahlung erfolgt (1.Halbjahr,
[...]


---

## Aufräumen alter Log-Dateien

Aufräumen alter Log-Dateien
Um die Übersicht innerhalb der Log-Dateien zu
gewährleisten, werden die Log-Dateien nach Erreichen einer von uns vorher
festgelegten Speichergröße umbenannt und neu angelegt.
Durch das Umbenennen dieser Log-Dateien wird natürlich
Speicherplatz auf dem Datenträger belegt. Im ungünstigsten Fall kann zu Fehlern
und/oder Problemen kommen, da der Datenträger nicht mehr genügend Speicherplatz
zur Verfügung stellen kann.
Es ist also hier zwingend erforderlich, die alten
Log-Dateien von Zeit zu Zeit aufzuräumen und ggf. zu entfernen.
Alte, umbenannte Transaktionslogdateien mit der Endung
„.dbr“ befinden sich im Verzeichnis „..\Aeins\dbrexp\Log\alte_DBRLogs“.
Alte, umbenannte Datenbanklogdateien befinden sich im
Verzeichnis der Datenbank. Über den Direktsprung [RINFO] in Referenz-ERP, erhält man
unter anderem den Pfad zum Datenbanklogverzeichnis.
Mit der Datenbank-Replikationsoption „delete_old_logs“
werden alte, umbenannte Transaktionslogdateien behandelt. Der S
[...]


---

## Analysefunktionen

Analysefunktionen
Sollte eine Differenz festgestellt werden, kann über
die Anwahl der Funktion
Konsistenz
prüfen
möglicherweise die Ursache für die Abweichung gefunden werden.
Die durch "!!!" gekennzeichneten Einträge sind
„ausführbare SQL-Anweisungen“, sie führen also zu Veränderungen am
Datenmaterial. Sämtliche anderen Funktionen erzeugen eine Bildschirmübersicht,
die auch mit
F4
druckbar ist.
Eine Beschreibung ist jeweils unter Info
sichtbar.
Funktion
Beschreibung
Mand.Server mit defekten
      Vorgängen
Diese Einträge im Mandantenserver
      wurden von Branchen-ERP-Mitarbeitern zwischenzeitlich deaktiviert (DS_STATUS =
      2!!), da die zugehörigen Warenvorgänge unvollständig oder inkonsistent
      waren. Spalte SollP = so viele Positionen sollten da sein, Spalte MitP =
      so viele sind vorhanden
Mand.Server mit defekten Vorgängen
      (Komplett)
Diese Einträge im Mandantenserver
      wurden von Branchen-ERP-Mitarbeitern zwischenzeitlich deaktiviert (DS_STATUS =
      2!!), d
[...]


---

## Anlagenbuchhaltung

Anlagenbuchhaltung
Da man nicht für jedes Anlagengut ein eigenes Konto
anlegen möchte, auf dem die wertmäßigen Veränderungen – Anschaffungs- und
Herstellungskosten (AHK), Zu – und Abgänge und Abschreibung (AFA) – und somit
der aktuelle Buchwert geführt wird, werden diese in einer separaten
Anlagebuchhaltung geführt. Die Anlagenbuchhaltung ist in die Finanzbuchhaltung
von Referenz-ERP integriert. Es können diverse Informationen zu den Anlagegütern
hinterlegt werden, Zu- und Abgänge erfasst werden, Abschreibungsvorschläge
erstellt und diese direkt in die Finanzbuchhaltung übernommen werden.
Aus der Belegerfassung der Finanzbuchhaltung heraus
kann bei der Neuerfassung auch direkt ein Anlagegut erzeugt werden.
Voraussetzung dafür ist, dass das angesprochene Sachkonto im
Sachkontenstamm
als Anlagenkonto
gekennzeichnet ist. Es öffnet sich dann nach Abschluss der Position das
Erfassungsfenster des Anlagenstamms. Hier sind dann die Daten aus dem Beleg
vorbelegt, so dass nur noch die fehl
[...]


---

## Anlagenmappe

Anlagenmappe
Hauptmenü
Anlagenbuchhaltung
Anlagenbuchhaltung
Anlagenmappen
Direktsprung
[ANKAM]
Die Anlagenmappen dienen dazu, Anlagegüter, bei denen
Fragen zu klären sind bzw. die zur Vorlage bei einem Kollegen zusammengefasst
werden sollen, in Gruppen bzw. „Mappen“ zusammen zu stellen und sie für ein
bestimmtes Datum für den Kollegen auf Wiedervorlage zu setzen.
Um eine Mappe zu erstellen geht man wie folgt vor:
In der Auswahlliste für den
Anlagenstamm
markiert man die Anlagengüter, die zu
einer Mappe zusammengefasst werden sollen. Sind ein oder mehrere Anlagengüter
markiert steht eine Funktion „Zur Mappe hinzufügen“ zur Verfügung. Wenn man
diese Funktion auswählt öffnet sich eine Itembox, in der man entweder diese
Anlagenguter zu bestehenden Mappen hinzufügen kann oder eine Neue Mappe anlegen
kann.
Der Punkt NEU sorgt dafür, dass eine neue Mappe
angelegt wird. Es öffnet sich folgendes Fenster
Bedeutung
Bezeichnung
Hier
      trägt man einen eindeutigen Text ein, der die Id
[...]


---

## Anlagen Neu

Anlagen Neu
Die Anlagenverwaltung in den Besuchsberichten ist
veraltet. Bitte das Archiv verwenden.

---

## Registerkarten in Anschriften

Registerkarten in Anschriften

---

## Zusätze

Zusätze
Feld
Beschreibung
Vererben
ILN-Nr.
Titel
Zusatz
Kreis
Regbezirk
Bundesland
Gebietsnummer
Empfänger Zahlungsträger
Empfänger Teil 2
Geburtstag
Adressmaske für Druck
Hier
      kann die „Maske“ ausgewählt werden, die man im Menüpunkt
Maskenpflege
erstellt
      hat.
Bitte beachten Sie, dass
      „Branchen-ERP-Default“ hier immer die Maske „Kunden-Default (1) verwenden wird.
      Die o.g. Maske dient in der Maskenpflege nur als
      Kopiervorlage.
Geokoordinate (L/B)
Geografische Länge und Breite und
      die Herkunft der Daten
Diese Funktion ist nur im Rahmen der
      GeoDaten verfügbar.
Werden Daten hier manuell angegeben,
      werden sie nicht von einer automatisierten Datenermittlung
      überschrieben.
Der
      Abruf der geografischen Koordinaten kann mit der Funktion „GeoDaten
      abfragen“ jederzeit angestoßen werden und überschreibt manuell eingegebene
      Daten!
Adressprüfung
Siehe
Einrichtung der
      Verbotslistenprüfung
Zusatz 2-6
Reine Textfelder für
[...]


---

## Ansehen

Ansehen
Befinden sich die Belege im Formulararchiv, dann
möchte man sie auch hin- und wieder ansehen. Referenz-ERP beherrscht das Anzeigen der
Belege, muss sich aber gewissen Umständen beugen …
Hier finden sich vielfältige Einstellungsmöglichkeiten
die sich des Themas „Ansehen“ eines Beleges aus dem Archiv heraus annehmen.
Das Archiv kann neben der „normalen“
Vorgangserzeugung, also ASCII, PDF- und Tiff-Dateien inzwischen eine ganze Reihe
weiterer Formate behandeln und zur Ansicht bringen.
Die „Ansicht“ selber wird dabei den gemein gängigen
Programmen der Windows-Welt überlassen. Diese spezialisierten Programme bieten
in aller Regel neben der Ansicht noch weitere Funktionalitäten, so z.B. der
Adobe Mail-Versand etc. pp. Deshalb wird diese Methode von Referenz-ERP favorisiert.
Sie hat nur den kleinen Nachteil, dass diese externen Programme auf bestimmten
Systemen ihre Eigenheiten haben. So ist als Beispiel zu nennen, dass der Adobe
in integrierter Form in Referenz-ERP (embedded) auf Terminalse
[...]


---

## Anteile

Anteile
Für jeden Aktionär kann aus den Listen
„Aktionärsübersicht“, „Gesamtliste“ und „Aktionärsdividende“ über die Funktion
Anteile
CF6
der innerhalb eines Wirtschaftsjahres
explizit dargestellt werden. Die Maske wird automatisch mit dem aktuellen
Wirtschaftsjahr und dem angewählten Aktionär gestartet. Diese Daten können aber
auch noch in der Maske geändert werden, wobei über die Taste
F3
eine Auswahlliste für das jeweilige Feld
zur Verfügung steht. In der Maske werden weitere relevante Daten des Aktionärs
dargestellt. Darunter sind die Aktienanteile des Aktionärs für das
Wirtschaftsjahr zu sehen. Entweder ein Anteil für das komplette Wirtschaftsjahr,
oder falls eine Veränderung des Bestandes zur Hälfte des Wirtschaftsjahres
vorgenommen wurden zwei Anteile jeweils gültig für ein halbes Wirtschaftsjahr
[siehe
Aktientransaktionen / Die
Historische Tabelle
]. Nach Anwahl der Anteile werden weitere
Detailinformationen dazu im unteren Bereich dargestellt.

---

## Ansichten allgemein

Ansichten allgemein
Es gibt eine Reihe von Begrifflichkeiten im
Zusammenhang mit dem Archiv und den zur Verfügung stehenden
Visualisierungsmöglichkeiten. Damit verbunden sind folgende Aktionen:
Aktion
„
Archiv anzeigen
“ [
Strg
      F12
]
(Funktion in der jeweiligen
      Optionbox in der Anwendungsvariante oder dem Dialog.
Für
      eine Übersicht aller Vorkommen siehe
Archiv-Ansichten-Variante: Ansichten
      – Vorkommen)
Führt eine Recherche im
      Formulararchiv gemäß der in den Ansichtsdefinitionen hinterlegten Regeln
      (
Archiv-Ansicht-Definition
) durch und
      öffnet die Auswahlliste „
Formulararchiv Anzeige
“ mit
      den Recherche-Ergebnissen.
„Archiv anzeigen [
Strg
      F12
]
In
      der Auswahlliste „
Formulararchiv
      Anzeige
“
Öffnet den selektierten Eintrag zur
      Ansicht des damit verbundenen Dokumentes.

---

## Anwender-Spalten

Anwender-Spalten
Hier kann der Anwender zusätzliche Felder in der
Spaltenbeschreibung definieren. Die Angaben des Anwenders werden stets als
Ergänzung der vorgegebenen Systemspalten verwendet.
Zu den Inhalten der Tabelle und der Änderung im
Kapitel Spaltenbeschreibung.

---

## Referenz-ERP App

Referenz-ERP App
Um auch Arbeiten auf dem iPhone oder dem iPad in
Zusammenhang mit A. eins tätigen zu können, gibt es für diese Geräte eine App,
die sich aus dem App-Store von Apple kostenfrei herunterladen lässt.
Die App arbeitet autark, im Falle einer Verbindung zum
Internet wird per Replikation ein Datenabgleich mit dem Referenz-ERP Kernsystem
hergestellt.

---

## Archiv-Ansicht-Definition

Archiv-Ansicht-Definition
Ausgelöst wird eine Archiv-Ansicht über die Funktion
Archiv anzeigen
CF12
im jeweiligen Programm-Kontext in
Referenz-ERP. (
Ansichten
allgemein
)
Eine Archiv-Ansichts-Definition ist im einfachsten
Fall eine von Branchen-ERP vorkonfektionierte Beschreibung, mit deren Hilfe Referenz-ERP im
Archiv recherchiert.
Der Programm-Kontext in Referenz-ERP stellt automatisch
(fest vorgegebene) Kriterien zur Verfügung, die in der Archiv-Ansicht-Definition
zur Auswertung und Bestimmung, welche Archiv-Einträge in der Archiv-Ansicht
aufgelistet werden sollen, herangezogen werden können.
Alle ausgelieferten Archiv-Ansicht-Definitionen, die
von Branchen-ERP mitgeliefert und bei Programmupdate aktualisiert werden, finden sich in
der Variante Archiv-Ansichten-Variante: Ansichten ( nur Branchen-ERP – Auslieferung
).
Tabelle
5
Wichtige Archiv-Ansicht-Definitions-Begriffe
Name
Sammelbegriff für Archiv-Ansichten
      gleichen Typus.
Der
      Name des Ansichtsprofils.
Eine
      so zusätzlich angelegte Ansichts
[...]


---

## Archiv-Ansichten Details

Archiv-Ansichten Details
Eine Ansicht zeichnet sich dadurch aus, dass sie in
einem gewissen Kontext heraus aufgerufen wird. Dieser „Kontext“ wird mit Hilfe
der Details ausgewertet.
Per Funktion
Details…
erreicht man folgende
Auswahlliste
Und hier lässt sich detailliert sagen, wie die
Kerndaten ermittelt werden.
Im Beispiel der Kundenauswahl-Listen erfolgt die
Datenermittlung eben über diese Auswahllisten und das wird hier vermittelt.
Nr
Es werden also möglicherweise mehrere Rahmendaten
ermittelt. Per „Nr“ lässt sich die Reihenfolge der Ermittlung steuern.
Var
Hier gibt man das zu ermittelnde „Kerndatum“ an.
Hier gibt es die zu diesem Zeitpunkt die möglichen
Daten-Definitionen, die für eine erfolgreiche Abwicklung momentan verwendet
werden können.
Kernpunkte sind Referenznummer und Kundennummer.
ZW1 bis ZW5 können für „Zwischenwert“-Ermittlungen
herangezogen werden.
Jahrbeginn, Jahrende und Belegklasse für
themenbezogene Eingrenzungen.
Bei Bedarf können weitere zur Verfügung g
[...]


---

## Dokumentenverwaltung (Archiv anzeigen)

Dokumentenverwaltung (Archiv anzeigen)
Die Dokumentenverwaltung ist in mehrere Bereiche
gegliedert:
Bereich
Funktion
Dokumentenverwaltung-
      Multifunktionsleiste
Die
      Optionbox für diesen Dialog gibt die Funktionen in der
      Multifunktionsleiste wieder.
Dokumentenverwaltung- Ordner und
      Filter
Ordner- und
      Filterkriterien
Dokumentenverwaltung-
      Datentabelle
Die
      Sicht auf die ermittelten Daten.
Welche Daten wie dargestellt werden
      hängt im Standard von der Aeins-Variante
Dokumentenverwaltung-
      Vorschau
Für
      PDF-Dokumente und Bildelemente ist eine Vorschau vorhanden
Dokumentenverwaltung-
      Statuszeile
Enthält Zusatz-Informationen zur
      Datentabelle.

---

## Archiv-Ansichten-Variante: Ansichten – Variantenaufkommen

Archiv-Ansichten-Variante:
Ansichten – Variantenaufkommen
Hauptmenü
Dokumentenverwaltung
Ansichten
Ansichten-Variantenaufkommen
Direktsprung
[FAA]
Archiv-Ansichtsfunktionen sind Funktionen die ein
Ansichts-Profil (siehe
Archiv-Ansicht-Definition
) zur Ausführung
bringen.
In dieser Variante „Ansichten – Variantenaufkommen“
geht es um die Beantwortung der Frage: Wo überall befinden sich im Livesystem
Archiv-Ansichtsfunktionen in den Varianten?
Felder
Anwendung
Anwendungs-Identifikation
Variante
Varianten-Identifikation
„P“
      bedeutet „Privat“
Variante-Steupa
Steuerparameter der
      Variante
„!“
      bedeutet „Steuerparameter nicht aktiv“
Variante-Unsichtbar
Gibt
      an ob die Variante den Zustand „Hidden“ hat oder nicht.
„Hidden“-Varianten sind solche
      Varianten, die bei Bestandskunden weiterhin sichtbar bleiben, bei
      Neukunden allerdings nicht sichtbar sind. Gründe hierfür sind das die
      Varianten durch verbesserte Versionen abgelöst wurden bzw. die

[...]


---

## Belegfluss

Belegfluss
Hauptmenü
Dokumentenverwaltung
Belegfluss oder Direktsprung
[BF]
WICHTIGER
HINWEIS:
Für die Tabellen
FormulararchivKontierung und FormulararchivKontierungVorlage wurde eine
Strukturänderung durchgeführt. Das Feld „Sollhaben“ hat jetzt den Typen
INTEGER
. Stand in dem Feld „Haben“ wird es jetzt durch den Wert 2
dargestellt, „Soll“ wird durch den Wert 1 dargestellt. Andere Inhalte wurden
nicht übernommen.
Wurde bei der Postfach-Einrichtung eine
Datenbankprozedur für „Direkt-Finanzbelegerfassung“ hinterlegt, muss diese
angepasst werden.Vor dem Ausführen der Funktion wird geprüft, ob die
hinterlegten Prozeduren das Feld sollhaben auswerten und anschließend eine
Warnmeldung ausgegeben.

---

## Archiv – Dokumente hinzufügen Drag und Drop

Archiv – Dokumente hinzufügen Drag und Drop
Zurzeit können ausfolgenden Apps Dokumente per „Drag
und Drop“ mit der Maus ins Archiv „gezogen“ und damit übernommen werden. Es
erfolgt bei ausgewählten Archiv-Feldern eine Vorbelegung. Es kann nach dem
Hinzufügen ins Archiv optional der Archiv-Pflegedialog gestartet werden und die
„Verschlagwortung“ komplementiert werden.

---

## Archiv/Druck-Datum

Archiv/Druck-Datum
Mit den Möglichkeiten
bestimmen Sie das Archiv/Druck-Datum des zu
importierenden Beleges.
Mit den Auswahl-Möglichkeiten wird den Umständen
Rechnung getragen, dass sich zum einem das Archiv/Druck-Datum generell aus dem
Datei-Alter ergibt, oder eben dass eine Richtlinie existiert, nach der die
importierten Belege eben das Datum zum Zeitpunkt des Imports tragen sollen.

---

## Archiveinträge löschen

Archiveinträge löschen
Archiv-Einträge können gelöscht werden.
Die Löschung erfolgt über das Setzen eines
Kennzeichens in der Formulararchiv-Relation. Ein so gelöschter Archiv-Eintrag
ist in den gängigen Archiv-Auflistungen nicht sichtbar.
Eine Archiv-Löschung kann rückgängig gemacht werden,
und zwar nur in der Variante
Formulararchiv-Administration
.
Eine endgültige Löschung per Benutzeroberfläche ist
vorerst nicht vorgesehen.

---

## Archivierung Dateisystem

Archivierung Dateisystem
Bei der Archivierung ins Dateisystem werden die Belege
samt Verwaltungsinformation ins Dateisystem geschrieben. Hierbei ist wichtig zu
wissen, dass die Anwendung „Formulararchiv“ dabei nicht Verwendung findet.
Recherche und Ansehen von Belegen wird dann über ein externes Programm (AMICAR)
abgewickelt.

---

## Archiv Fakt-Tabellen

Archiv Fakt-Tabellen
Archiv-Fakte sind Tabellen, die in der Relation
fa_fakts definiert sind.
Select
faf_rel from fa_fakts where faf_rel<>’’

---

## Archivierung Datenbank – Export

Archivierung Datenbank – Export
Um die in der Datenbank befindlichen Belege ins
Dateisystem exportieren zu können, findet man an dieser Stelle die
Einstellungsmöglichkeiten, um diese Aufgabe durchzuführen.

---

## Archivierungsmerkmale der Dokumente

Archivierungsmerkmale der
Dokumente
Felder
Quick-Reporte
Ja/Nein
Gibt
      an, ob Quickreporte archiviert werden sollen.
Nur
      letzte Korrektur speichern
Beim
      erneuten Druck eines schon archivierten Vorgangs, der erneut zur
      Archivierung führen würde, wird anhand dieses Kennzeichens entschieden,
      wie die Archivierung durchgeführt wird:
•
Nein
Der erneute Druck erzeugt in jedem
      Falle einen neuen Archiv-Eintrag
•
Ja
Wenn die Belegnummer, Klassennummer,
      Unterklassennummer, Unternummer und die Jahrnummer des zu druckenden
      Beleges mit Belegen aus dem Formulararchiv übereinstimmen, dann wird
      derjenige Beleg von diesen Belegen mit dem jüngsten Änderungsdatum als
      Vergleichsbeleg herangezogen.
In diesem Falle wird kein neuer
      Formulararchiv-Eintrag erzeugt, sondern das Dokument in der Tabelle
      „Archiv“ aktualisiert.
Findet eine Aktualisierung des
      Dokumentes statt, wird die „Inkarnation“ aus dem Formulararchiv jewei
[...]


---

## Dokumentenverwaltung (Ordner)

Dokumentenverwaltung (Ordner)
Siehe
Dokumentenverwaltung (Archiv anzeigen)

---

## Archiv-Profile

Archiv-Profile
Hier werden die Profile gepflegt.
Felder
Name
Ansichtsprofil-Identifikation
Dieser Profilname wird an den
      betreffenden Stellen auf Masken und Funktionsbezeichnungen dargestellt.
Bezeichnung
Alternative Bezeichnung für
      Funktionen im Hauptmenü.
Funktion
Funktions-Identifikation
      (*)
F3-Auswahl auf
Freigegebene
      Archiv-Editoren
Optionbox
(*):
Funktion und Optionbox bestimmen den
      Kontext der durch das Profil aufgerufenen Referenz-ERP-Funktionalität. Somit
      geben Sie zusätzlich auch die Berechtigungsrolle vor.
Erläuterungen zu den
      Berechtigungen:
Der
      Rollen-Kontext ah_archivbelegfluss/OB_ARCHIV.VIEWDIALOG steuert ob die
      Funktion Belegfluss
überhaupt sichtbar ist.
Der
      Rollen-Kontext dieser
Funktion
der der angegebenen
Optionbox
bestimmt, ob der Archiv-Editor ausgeführt werden darf.
Somit ist es möglich die Daten des
      Belegflusses einzusehen, aber rollentechnisch zu verhindern, dass der
      Archiv-Editor auf
[...]


---

## Archiv - Vorschau

Archiv - Vorschau
Die Dokumentenverwaltung bietet in allen
Auswahllisten, in denen die Schlüsselbegriffe des Archivs (fa_id, fa_mndnr)
verfügbar sind, Vorschauen für die gängigen Mime-Typen resp. Formate.
Welche das genau sind entnehme man der Anwendung
„Mime“, Variante „Mime“ (
[MIME]
) der
dortigen Spalte „Archiv-Vorschau“.
Das Referenz-ERP-System unterstützt folgende Typen der
Vorschau, diese sind mit Kontext-Menüs ausgestattet, die speziell auf den Typen
ausgerichtete Funktionen anbieten.
Vorschau-Typ
Anmerkung
Bild-Anzeige
Die
      Bild-Anzeige bietet im Kontext-Menü folgende Darstellungsarten. Diese
      werden sich sitzungsübergreifend für den jeweiligen Referenz-ERP-Benutzer
      gemerkt.
•
Dehnen
Das Bild wird gestreckt oder
      verkleinert, damit es der Größe der Bild-Anzeige entspricht.
•
Originalgröße
Das Bild wird in Original-Größe
      dargestellt. Ist das Bild größer als die Bild-Anzeige, dann wird die
      Bild-Anzeige mit Rollbalken ausgestattet.
•
Skalieren
Das
[...]


---

## Aufgabenplanung

Aufgabenplanung
Hauptmenü
Büro und Internet
Büroumgebung
Aufgabenplanung
oder Direktsprung
[TODO]
Mit diesem Modul lassen
sich Termine und Aufgabenerstellungen realisieren.

---

## F3-Auswahl

F3-Auswahl
Bei der F3-Auswahl handelt es sich um einen
Bildschirm, in dem die Daten, die für die Eingabe zur Verfügung stehen
aufgelistet werden. Man erkennt Felder, in denen eine F3-Auswahl bereitgestellt
wird, daran, dass in der Statuszeile der Text „Eine Auswahl kann mit der Taste
F3 abgerufen werden“ eingeblendet wird. In der F2-Bereichsauswahl sind diese
Felder zusätzlich mit einem Button
versehen.
Der Einsatzbereich erstreckt sich über alle Bereiche
in Referenz-ERP. Das hat den mit dem Vorteil, dass auch die Bedienung immer gleich
ist. Der Bildschirm besteht aus einem
Anzeigebereich
, in dem die zur
Verfügung stehenden Daten angezeigt werden. Die möglichen Suchvarianten erreicht
man über die rechte Maustaste. Diese könne auch privatisiert werden. Man kann
zwischen den Varianten entweder mit der Maus wechseln oder über die Tastatur.
Dazu gibt man die Nummer ein, die vor der Variante steht, gefolgt von einem
Punkt. Will man also zur zweiten Variante wechseln, so gibt man „2.“
[...]


---

## Ausnahmen

Ausnahmen
Standardmäßig hat man es mit der bevorzugten
integrierten Ansicht zu tun. Man kann hier die Computernamen angeben, für die es
eine Abweichung von dieser Regel geben soll.

---

## Die Auswahlliste

Die Auswahlliste
Die
Auswahlliste
wurde auf eine neue Oberfläche
umgestellt.

---

## Auswahllisten-Legende

Auswahllisten-Legende
Bei der Auswahllisten-Legende handelt es sich um einen
Dialog, welcher die einzelnen Felder und Farben einer Auswahlliste beschreibt.
Die Funktion ist auf den Auswahllisten vorhanden, die Informationen für die
Legende bereitstellen. Diese Informationen für die Auswahlliste werden in jedem
SQL-Text der Auswahllistenvariante gepflegt. Dort werden diese per XML-Struktur
zur Verfügung gestellt. Die Tags und Attribute werden immer klein
geschrieben.
XML-Tag <auswahllistenbeschreibung>
Dieses Tag ist das Haupt-Tag der XML-Struktur. Unter
diesem kann sich ein Tag für die Beschreibung befinden und mehrere Tags für die
Felder.
<auswahllistenbeschreibung></auswahllistenbeschreibung>
XML-Tag <beschreibung>
Dieses Tag kann sich unter folgenden übergeordneten
Tags befinden.
Tag <auswahllistenbeschreibung>
Befindet sich das Tag unter diesem Tag, handelt es
sich um die Beschreibung der Auswahlliste.
<auswahllistenbeschreibung>
<beschreibung>Daten der
Variante</beschre
[...]


---

## Auswertungen Bildschirm/Dialog

Auswertungen Bildschirm/Dialog

---

## Auswertungen der Anlagenbuchhaltung

Auswertungen der Anlagenbuchhaltung
Hauptmenü
Anlagenbuchhaltung
Auswertungen
Um jederzeit einen Überblick über die Anlagen zu haben
stellt Referenz-ERP neben den Auswahllisten folgende Auswertungen zur Verfügung.
•
Anlagenspiegel.
(
Direktsprung
[ANKSP]
)
Dieser Anlagenspiegel entspricht den
gesetzlichen Vorgaben und wurde von einer
unabhängigen Wirtschaftsprüfungsgesellschaft in die Prüfung
mit eingeschlossen.
•
Anlagenspiegel II.
(Direktsprung
[ANKS2]
)
Dieser Anlagenspiegel
unterscheidet sich in drei Punkten von dem geprüften Anlagenspiegel:
o
Die sonstigen betrieblichen
Erträge/Aufwendungen werden nicht mit ausgewiesen, selbst wenn sie geführt
werden(siehe
Firmenstamm
).
o
Die Abschreibungen auf Abgänge
werden in der Spalte „Sonder-AfA, Teilwert-AfA, Außerg.-AfA“ aufgeführt und
nicht in der AfA-Spalte des aktuelles Jahres. Gleichzeitig werden bei
Angang/Verkauf eines Anlagegutes dann die Werte aus der Spalte „Sonder-AfA,
Teilwert-AfA, Außerg.-AfA“ der Spalte des aktuellen Jahr
[...]


---

## Automatische Privatisierung der Datenbank-Funktion

Automatische Privatisierung der Datenbank-Funktion
Der manuelle Vorgang eine private SQL-Funktion zu
erstellen ist mühselig. Es gibt deshalb die Möglichkeit diesen Vorgang per
Funktion „Referenzfunktion privatisieren“ zu automatisieren.
Für obiges Beispiel bedeutet dies
Damit ist automatisch eine private Kopie der
ursprünglichen Datenbank-Funktion angelegt worden. Diese kann nun per
„Referenzfunktion bearbeiten“ inhaltlich überarbeitet werden:

---

## Barcode/Bilderdruck-Druck: Die Behandlung von Codetyp Null

Barcode/Bilderdruck-Druck: Die Behandlung von Codetyp Null
Wird in der privaten Prozedure als "codetyp" eine NULL
zurückgegeben, dann wird der ausgewiesene Barcode visuell gelöscht.
Somit lässt sich ggf. ein Barcode/Bild ganz
unterdrücken.
Zu den "Barcode-Texten" (also "code") ist anzumerken,
dass die private Prozedure dafür zuständig ist, dass es sich um einen
normgerechten Strichcode-Text handelt. Ob und wie man das am besten
bewerkstelligt entnehme man am besten den jeweiligen Informationen, die es zum
Beispiel in Wikipedia zu finden gibt.

---

## Bearbeitungsmaske Registerkarten

Bearbeitungsmaske Registerkarten
Im unteren Bereich finden Sie 6 Registerkarten.

---

## Bearbeitungsmaske

Bearbeitungsmaske
Bei Ansicht oder Änderung erhalten Sie die
Bearbeitungsmaske. Beim Modus Ansicht können Sie darin keine Änderungen
vornehmen.

---

## Begründung

Begründung
Diese Begründung wird gespeichert. Sie ist auch
einsehbar, wenn Sie eine Anschrift auswählen und die Funktion
Ausnahmebegründung ansehen
auswählen.
Diese Begründung dient der Dokumentation der Prüfung
und damit letztlich dem Schutz Ihres Unternehmens vor Strafen. Dokumentieren Sie
also hier genau, welche Prüfungen Sie vorgenommen und welche Entschlüsse Sie
gemäß Ihren Arbeitsanweisungen getroffen haben.

---

## Beispiel 2 - Komplex

Beispiel 2 - Komplex
Dieses Beispiel demonstriert den binären Import aus
dem Pfad ..\Import\Serienbriefe.
Es erwartet Dateien, die intern eine Signatur
# LS#Referenz-ERP# tragen. Anschließend an diese Signatur sind lt. Beispiel der
Belegtyptext getrennt durch ein „/“ – Zeichen mit beliebig vielen Dezimalziffern
und Leerzeichen folgend.
In der Tabelle werden über die Gruppen-Zuweisungen G
(1 und 2) jeweils die zu erwartenden Kerndaten den regulären Gruppen zugeordnet.
Die Nachbearbeitung des Belegtyptextes führt ausgehend
von
\s*(\S*) ein $1 durch, was einfach nur eine
Eliminierung von führenden Leerzeichen bedeutet. Die Nachbearbeitung der
Belegnummer demonstriert das einfache Ersetzen; in diesem Falle wird einfach
jede 4 durch eine 5 ersetzt.
Die Parameter NBV und NBZ stellen nützliche kleine
Helferlein zur Verfügung will man nicht wesentlich umständlichere
Nachbearbeitungen im Nachhinein anstellen!

---

## Beleg-Datum

Beleg-Datum
Mit dieser Einstellmöglichkeit wird durch die
Auswahl
analog dem Archiv/Druckdatum bestimmt, welches
Belegdatum die importierten Dateien tragen sollen.

---

## Belegfluss Modul

Belegfluss Modul
Hauptmenü
Dokumentenverwaltung
Belegfluss oder Direktsprung
[BF]

---

## Benutzung Warenreorganisation

Benutzung W
arenreorganisation
Hauptmenü
Systempflege
Abstimmung
Warenreorganisation
oder Direktsprung
[WAREO]
Die Funktionen aus dem Bereich WAREO sollen die Folgen
außergewöhnlicher Zustände im Bereich der Warenwirtschaft prüfen und
gegebenenfalls richtigstellen. Im Einzelnen können dies unkontrollierte
Abbrüche, fehlerhafte Einrichtungen oder auch Fehlbedienungen sein.
Veranlassung zum Ausführen eines solchen
Reorganisationsvorganges kann zum Beispiel eine festgestellte Differenz im
Bereich „Ware abstimmen
[WABST]
“ sein.
Die Funktionen sollten grundsätzlich nur in Abstimmung mit den zuständigen
Supportern verwendet werden. Besonders gilt dies für die Funktionen im unteren
Bereich der Maske.
Im oberen Bereich des Bildschirmes wird der
Fortschritt einer laufenden Aktion dargestellt, im unteren Bereich erfolgt die
Funktionsauswahl.
Auswahl einer Funktion mit Richtungstasten oder
Mausklick. Nach Anwahl einer Funktion erscheint ein kurzes Beschreibungsfeld,
hier wird der eig
[...]


---

## Bereich/Profile F2

Bereich/Profile F2
Die Daten in der Auswahlliste können über die hier
angegebenen Kriterien eingegrenzt werden.
Zu erwähnen sind hier die 5 Merkmale. Hierbei ist es
so, dass man pro Merkmal nach 4 Werten suchen kann, die mit „oder“ verbunden
sind.

---

## Bewertung

Bewertung
Für die laufende Bewertung des Warengeschäftes stehen
verschiedene Verfahren zur Verfügung. Hierauf wird nachfolgend eingegangen.
Daneben spielen organi­satorische Faktoren eine wichtige Rolle; auf die
damit verbundenen Prinzipien wird im Anschluss eingegangen.

---

## Bewertung und Rohertragsermittlung in Referenz-ERP

Bewertung und Rohertragsermittlung in Referenz-ERP
Für die Interpretation der Bewertung in Referenz-ERP ist
folgendes zu beachten:
Bewertung in der Relation Artisummen
Die Bewertung in der Relation ArtiSummen ist Grundlage
der Rohertragsermittlung. Die dort abgelegten und in der
Periodenerfolgsauswertung ausgewerteten Daten sind zentraler Bestandteil der
Abstimmung zwischen Warenwirtschaft und Finanzbuchhaltung. Die Daten (Werte und
Mengen!) der Relation ArtiSummen ergeben sich aus den
fakturierten
Rechnungen und Gutschriften einer Periode. Entsprechend wird der gew. EK
innerhalb einer Periode aus den fakturierten Bewegungen ermittelt. Innerhalb
einer (offenen) Periode wird der Bewertungspreis permanent neu berechnet. Der
jeweils ermittelte gilt für die gesamte Periode. Der (abgespeicherte)
Bewertungspreis einer alten (ob abgeschlossen oder nicht) Periode ist also der
zuletzt ermittelte Wert. Der Einstiegswert in die Folgeperiode ist immer der
zuletzt ermittelte Wert der Vorperiode. Bei
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

## Ermittlung durch Datei

Ermittlung durch Datei
Inhalt von "codetype"
Inhalt von "codetype"
Beispiel
file
Enthält den Pfad auf die
      Bild-Datei
'\\amrum\aeins\bin\druck.jpg'
'C:\Users\beispiel\Pictures\butterfly.bmp'
Unterstützte Bild-Formate
      (Bild-Datei-Erweiterungen)
Alternative
Beschreibung
bmp
Windows Bitmap
jpg
jpeg
JPG
      oder JPEG ist das häufigste Format für Dateien mit digitalen Fotos. Ob
      eine Datei .jpg oder .jpeg heißt, ist egal; .jpg ist nur die bei
      Dateinamen übliche Verkürzung von .jpeg auf drei Buchstaben.
gif
Graphics Interchange
      Format
wmf
Windows Metafile
exif
Exchangeable Image File
      Format
emf
Windows Enhanced
      Metafile
png
Portable Network
      Graphics
ico
Windows-Format für Icons
tif
tiff
Tagged Image File Format
TIF
      und TIFF sind genau dasselbe. TIF wird in älteren Dateisystemen verwendet,
      die die 8.3-Namenskonvention verwenden, während TIFF in neueren
      Dateisystemen verwendet wird, die lange Dateinamen erlauben.
Bei
[...]


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

## Bitzer Datenstrukturen

Bitzer Datenstrukturen
Zur Befüllung der Bitzer Datenbank stehen folgende
vier Strukturen bereit, die einerseits per Export direkt aus dem Referenz-ERP
herausgeschrieben werden können, um dann direkt in das Bitzer System übernommen
zu werden. Folgende Bereiche werden dabei abgedeckt:
-
Adressdaten
-
Kontraktdaten
-
Artikeldaten
-
Qualitäten

---

## Büro-Organisation

Büro-Organisation

---

## Referenz-ERP Scannersoftware

Referenz-ERP Scannersoftware
Mit der Referenz-ERP Scannersoftware können Prozesse
abgearbeitet werden.
Folgende
Eine Mindestvoraussetzung an die Hardware finden Sie
in
Technische Daten
.
Unterstützte
  Prozesse
Erfassung von
      Eingangsbelegen
Erfassung von Labordaten
Erfassung von beliebigen
      Informationen (Private Prozeduren)
Erfassung von Teildisposition
      (Klammer)
Erfassung der Inventur inkl.
      Partiezuordnung (Online wie Offline )
Erfassung von Aufträgen
Abarbeitung
      von Lagerumbuchungen
Abarbeitung von
      Bestellungen

---

## Anwendung Scanner in Aeins

Anwendung Scanner in Aeins
Hauptmenü
Externe Kommunikation
Scanner Lösungen
Direktsprung
[SCTCP]
Varianten
1.
Scanner
Detailübersicht
2.
Scanner Scancode
3.
Status der Scanner
4.
Scanner Daten
bearbeiten
5.
Scanner
Originaldaten
6.
Vorgangsprotokoll

---

## ET Etikettendruck

ET Etikettendruck
Um ein Etikett zu erstellen welches dann diesen Sofort
druck auslöst, bitte den Direktsprung auf sctcp benutzen, dort finden Sie
Scanner Etikett Bearbeiten und Scanner Etikett Druck. Beide Funktionen greifen
auf den Branchen-ERP Etikettendruck zurück. Unter dem Direktsprung ETIDR finden Sie eine
Funktion die „Scanner_etikett“ heißt. Diese Stellt das Etikett zum Drucken über
den aus. Des Weiteren gibt es dort die Funktion „Scanner druck“ diese Funktion
ist dafür zuständig, dass die Gewünschte Seite ausgedruckt wird. Nach der Anwahl
der Funktion und das Auswählen zum Bearbeiten. Unter dem Prozedurname und
Funktion zum Aufrufen geben Sie bitte die Relation an. Dann klicken Sie bitte
auf „Reportbearbeiten“ Taste „F6“ und können dort die Seite Ihren Wünschen
anpassen. Beim Scancode ET können über den Scanner direkt Druckbefehle
ausgeführt werden
Wie wird ein Etikett unter dem Branchen-ERP
Etikettendruck eingerichtet und gedruckt
.
Beispiel Drucker TEC – B – SV4 Label Drucker
W
[...]


---

## Prozesse des Scanners

Prozesse des Scanners
Bei allen beschriebenen Funktionen muss eine aktive
Verbindung zur Zentral-Datenbank bestehen.
Es gibt drei verschiedene Möglichkeiten wie ein
Scanvorgang von der Software behandelt wird
•
Es besteht die Möglichkeit die gescannten Daten in die Zwischenablage zu
kopieren. Die AeinsCE Software liest die Daten der Zwischenablage aus.
•
Der Scanner hat die Möglichkeit ein Scan-Suffix anzugeben. Hier ist bitte
als Suffix das TAB Zeichen anzugeben.
•
Der Scan-Code muss per Hand abgesendet werden, hier stehen einmal die TAB
Taste und die F2 Taste zur Verfügung.
Variante Scanner Daten Übergabe
Über den Direktsprung [SCTCP] kann man die Variante
Scanner Daten Übergabe anwählen. Dort kann man alle Daten die vom Scanner
eingelesen und an die zentrale Datenbank übertragen wurden sehen.

---

## Beispiel Partiesperre

Beispiel Partiesperre
Hier finden Sie die Beispiel Prozedur für die Partie
Sperre. Die Prozedur besteht aus dem Header und eine Abfrage, ob das
Partiesperrkenz gesetzt ist. Die Funktion gibt 1 oder  0 zurück.
// Priv. Prozedur p_partie_sperre
//
// Beschreibung:
//
//
//
// Ausgabe 1 gescannte Partie wird gelöscht
// Ausgabe 0 Partie ist in Ordnung
CREATE PROCEDURE
p_partie_sperre (  in in_vklasse   integer,
in in_vuklasse
integer,
in in_menge   numeric (15,6),
in in_me   integer,
in in_ArtikelId    integer,
in in_KundId   integer,
in in_LagerNummer   integer,
in in_varengruppe    integer,
in
in_EKVK   integer,
in in_PeriodisDato   date,
in in_ArtiStammId
integer,
in in_partie   integer,
in in_KontraktId   integer,
in in_lagerplatz   integer,
in in_Belegnummer   integer,
out dc_out integer)
BEGIN
declare dc_partiesperrkenz integer;
set dc_partiesperrkenz = 0;
select partiesperrkennz into
dc_partiesperrkenz  from partiestamm
where Lagernummer =
in_LagerNummer   and Partieid
[...]


---

## Eintragen in SCTCP

Eintragen in SCTCP
Jetzt müssen nur noch die Daten unter SCTCP
eingetragen werden. Wie diese funktioniert entnehmen Sie bitte
hier
.

---

## Technische Daten

Technische Daten

---

## AeinsWindowsScanner

AeinsWindowsScanner
In dem Aeins\bin Verzeichnis finden Sie die
Referenz-ERP.Scanner Software. Dieses Programm ist ein Abbild von der Software, die
auf den MDE Geräten benutzt wird.
Die AeinsWindowsScanner Software hat noch ein paar
Besonderheiten. Da Desktop Rechner im normalen Fall keine Scaneinheit besitzen,
so wird der der Scancode über die Tastatur in das Eingabefeld gegeben
eingetragen z.B. AU 4711. Ein Scanvorgang wird mit F2 bestätigt. Das Eingeben
der Mengeneinheit wird wie auf dem MDE Gerät mit ENTER bestätigt.
Es besteht die Möglichkeit einen Scanner an den
Rechner anzuschließen, um mit diesem die Barcodes zu lesen. Der Scanner muss so
eingerichtet werden, dass als Präfix das Enterzeichen mit übermittelt wird.
Des Weiteren müssen auf jeden Fall die Steuerparameter
727
und
728
auf ja gestellt werden, da es keine Scaneinheit gibt
welche mir den erkannten Scancode mitteilt.
Starten der
Software aus dem Bin Verzeichniss
Wird die Scanner Software zum ersten Mal aus dem Bin
V
[...]


---

## WLAN Einstellung mit SCU

WLAN Einstellung mit SCU
Um das WLAN mit der integrierten
Installations-Software SCU einzurichten gehen Sie wie folgt vor:
Windowssymbol unten links auf der Taskleiste
Settings
Control Panel
SCU (Wi-Fi)
Automatische
Anlage eines WLAN Profils
1.
Als erstes wird die Registerkarte Profile ausgewählt. Mit dem Button Scan werden
alle verfügbaren WLAN Verbindungen angezeigt. Jetzt sollte das WLAN Netz
angezeigt werden mit dem sich der Scanner verbinden soll. Wird das WLAN nicht
angezeigt, ist das WLAN Netz nicht verfügbar oder die SSID ist versteckt
worden.
2.
Um sich mit dem gewünschten Netz zu verbinden, wird ein Doppelklick auf die SSID
gemacht. Danach erscheint eine Abfrage, ob für diese SSID ein Profil angelegt
werden soll. Dies wird mit Yes bestätigt. Danach fordert der Scanner den WLAN
Key an. Der Key kann per
Tastatur
eingegeben werden.
3.
Nach dem Key eingegeben worden ist, wird mit dem Button „commit“ die Daten
übernommen.
4.
Danach wird auf der Registerkarte
[...]


---

## Standard Einstellungen Scancodes

Standard Einstellungen
Scancodes
Über den Scanner Direktsprung [SCTCP], die Auswahl der
ersten Variante (Scanner Scancode) und der Funktion Standard Scancodes (SF8),
können Sie ganz einfach die benötigten Scancodes für die Vorgangserfassung so
wie die dazugehörige AI-Zuordnung (Application Identifier) anlegen. Sie wählen
aus, welche Erfassungsvorgänge mit dem Scanner erfasst werden sollen.
Bei den Erfassungsvorgängen von Aufträgen,
Bestellungen, Inventur und Eingangslieferscheinen können Sie noch optional
auswählen, ob Sie mit Partie arbeiten wollen oder nicht.
Danach klicken Sie auf Standard Einspielen (F9) und
die Scancodes werden samt der dazugehörigen AI-Zuordnung eingespielt.
Anhand des Scancodes weiß der Scanner welchen
Erfassungsmodus er starten soll.
Die Scancodes werden als EAN 128 Code verschlüsselt
eingescannt.
Standard System Scancodes
Die Standard System Scancodes sind für die Navigation
in der Anzeige auf dem MDE (
M
obile
D
aten
e
rfassung) Gerät.
Es werden fo
[...]


---

## Dateisystem-Pfad

Dateisystem-Pfad
Hier ist der zentrale Speicherort für die Archivierung
der Belege anzugeben. Achten Sie bei Mehrplatz-Installation vornehmlich darauf,
dass es sich um einen „allgemein“ zugänglichen Speicherort – am besten auf einem
Fileserver – handeln muss.
Vermeiden Sie am besten „lokale“ Pfade, da jedes
Referenz-ERP dann diesen Archivierungspfad lokal auffassen würde, und ein zentrales
Formulararchiv sich so nur schwer realisieren lässt.
Die Standardvorgabe „..\archiv“ ist eine geeignete
Stelle um die Belege im Referenz-ERP-Verzeichnis des Servers zu sichern.
Sie müssen dann im Falle, dass Sie das komplette
Referenz-ERP sichern, meistens auch keine Extra-Einstellungen im
Datensicherungs-Programm machen.

---

## Dateien löschen

Dateien löschen
Gibt an, ob die Dateien im Importpfad gelöscht werden
sollen.
Außerhalb einer Testphase ist dies ist sicherlich
sinnvoll, damit keine ungewollten Duplikate entstehen.

---

## Datenbereiche

Datenbereiche
Im Bereich der Waren
wirtschaft werden folgende Datenbereiche
unterschieden:
Belege
Die Gesamtsummen der Rechnungen (RE), Gutschriften
(GU) Eingangsrechnungen (ER), Eingangsgutschriften (EG) und der entsprechenden
Stornierungen
Warenbuch
Die Einzelzeilen der o.a. Belege (Warenpositionen mit
zugeh. Rabatten, Zu- / Abschlägen, Frachten etc.)
Artikelsummen
Die auf Artikel und Periodenebene aufsummierten
Ergebnisse der Einzelbewegungen
Fibu
Die durch den Fibuübertrag aus der Ware gebuchten
Belegwerte

---

## Log

Log
Es wird ebenfalls eine Logdatei am angegebenen Pfad
angelegt. Dort werden einige Daten protokolliert, um die Löschungen
nachzuvollziehen. Dabei geht es oft um die Datenbank, die gelöschten Bereiche
und die Anzahl der gelöschten Daten und gegebenenfalls um Fehler.

---

## Manuelle Löschung

Manuelle Löschung
Nach der Verbindung mit einer Datenbank wird die
Hauptmaske geöffnet.
Hier können die Werte angegeben werden, welche zur
Löschung benötigt werden.
Es wird ein Jahr angegeben und ein Verzeichnis,
wo die Logdateien hinterlegt werden sollen. Dann werden die Kategorien
ausgewählt, um sie zu löschen.
In den Bereichen Archiv, Formulararchiv oder
Archivanlage muss zusätzlich zu dem Haken auch noch ein Tabellenname in dem
Archivfeld angegeben werden. Dabei muss es sich um eine (Proxy-)Tabelle handeln,
welche als Container([FAM]) auch eingetragen ist. Dies wird benötigt, um die
Dateien in diese Tabelle zu verschieben. Im Anschluss kann diese Tabelle bei
Bedarf archiviert oder gelöscht werden.
Anschließend werden die
Bereiche geprüft
und falls möglich durch das
Betätigen des Löschen-Knopfes die Löschung gestartet.
Bei noch fehlenden
Eingaben werden die entsprechenden Maskenelemente nicht freigeschaltet, um
Fehler zu vermeiden, so kann bspw. das Löschen nicht vor der
[...]


---

## Protokoll

Protokoll
Hauptmenü
Systempflege
Abstimmung
Protokollauswertung
oder Direktsprung
[PROTO]
Mit der Anwendung Protokoll lassen sich leicht
Änderungen von Daten mitverfolgen. Dafür können für alle Tabellen
unterschiedliche Spalten mitprotokolliert werden.
Hierbei ist zu beachten, dass immer Protokolleinträge
für eine Tabelle mit aktivierter Protokollierung erfasst werden, selbst wenn die
Tabellenspalten, die Änderungen enthalten, nicht explizit in die
Erfassungsfeldliste eingetragen wurden.
Auf der Erfassungsmaske stehen zwei Datentabellen zum
Erfassen zur Verfügung und die Funktionen zum Anlegen der Protokolltrigger.
Tabellen
Spalten
Funktionen
Datentabelle zum Erfassen der Tabellen.
Feld
Bedeutung
Protokolltabellen
Name
      der Tabelle die protokolliert werden soll.
XML
Hiermit kann angegeben werden, ob
      die Daten in einer XML-Struktur gespeichert werden sollen oder ob die
      Daten einfach hintereinander weg geschrieben werden. (siehe
Beispiel
)
Änderung
Steht dieses
[...]


---

## Der Referenz-ERP Grundbildschirm

Der Referenz-ERP Grundbildschirm
Referenz-ERP unterstützt mehrere
Hauptmenü-Varianten

---

## Prüfung

Prüfung
Folgende Prüfungen werden vor dem Löschen
durchgeführt:
Bereich
Kriterien
Vorgänge
§
Ob das
      ausgewählte Jahr existiert
§
Ob das
      ausgewählte Jahr schon abgeschlossen ist
§
OB das
      Wirtschaftsjahr des ausgewählten Jahres schon abgeschlossen
      ist
§
Ob zwischen dem
      ausgewählten Jahr und dem aktuellen Geschäftsjahr mindestens 10 Jahre
      liegen
§
Ob es nach dem
      ausgewählten Jahr mindestens eine abgeschlossene Inventur
      gibt
Partien
§
Ob die Partie in
      den Zeitraum bis zum ausgewählten Jahr passt anhand des
      PartieVonDatums
§
Ob die Partie
      erledigt, gelöscht oder ein abgelaufenes BisDatum hat
§
Ob die Partie in
      keiner Warenposition vorhanden
§
Ob die Partie in
      keinem Inventurbeleg vorkommt
§
Ob die Partie in
      keinem LVS-System vorkommt
§
Ob die Partie in
      keinem OWaage-Beleg vorkommt
§
Ob die Partie in
      keinem Kontrakt vorkommt
Kontrakte
§
Ob der Kontrakt
      in den Zeitraum bis z
[...]


---

## Dieses Menü

Dieses Menü
In allen Funktionsmenüs findet man diese
Standardfunktion als letzten Eintrag.
Die Funktionalitäten dieser Anwendung ergeben sich aus
einer spezialisierten Anwendung des Rollenkontextes. Weitere Informationen unter
Rollenkontext/Dieses
Menü
.

---

## Direktsprung

Direktsprung
Beim Direktsprung handelt es sich um eine einfache und
schnelle Möglichkeit ohne die Verwendung der Menüs eine weitere Anwendung zu
öffnen. Bei dem Direktsprung handelt es sich um eine Kombination aus bis zu fünf
Buchstaben, die einer Funktion/Anwendung zugeordnet ist. z.B. seht die
Kombination
[LIE]
für „Lieferscheine
Erfassen“. Gibt man also im Direktsprung-Dialog
[LIE]
ein, so wird sofort in die Anwendung
„Lieferscheine erfassen“ verzweigt. Diese erreicht man ansonsten über das Menü
„Warenverkauf“ in dem dann die Funktion „Lieferschein erfassen“ ausgewählt
werden kann.
Wie gelangt man in den
Direktsprung-Dialog?
Je nachdem, wo man sich im Programm befindet,
existieren dafür unterschiedliche Möglichkeiten zu Verfügung. Die erste
Möglichkeit über
Shift+F4
hat sich
als die praktikabelste erwiesen.
Tastenkombination
Umschalttaste+F4
Kontextmenü und dann Funktion
Direktsprung
anwählen
Drück man im Menü sofort
F3
gelang man in den Direktsprung-Dialog
und von dort
[...]


---

## Dividenden abrechnen

Dividenden abrechnen
Nach dem für die Aktionäre die Transaktionen für das
Wirtschaftsjahr erfasst wurden und die Dividendendaten eingetragen wurden, kann
die Dividende abgeschlossen und ausgeschüttet werden. Dies geschieht aus der
Liste „Aktionärsdividende“ heraus durch die Funktion
Dividende abschließen
F9
. Nach Anwahl dieser Funktion öffnet sich
die Maske zum Abschließen der Dividende. In dieser Maske kann die Dividende
durch Anwahl des Knopfes
Abschließen
F8
kann die Dividende abgeschlossen
werden. Dies bedeutet, dass alle Werte wie Transaktionen, Unternehmensdaten,
Dividendendaten und die ausgerechneten Dividenden für die einzelnen Aktionäre
festgeschrieben werden und nicht mehr verändert werden können.
Dann können die Buchungen für die Aktionäre erzeugt
werden. Dazu müssen vorher in dieser Maske noch einigen Daten wie das Belegdatum
der zu erzeugenden Belege, die Belegkreisnummer aus denen die Belegnummern für
die zu erzeugenden Belege stammen und einen Buchungstext, d
[...]


---

## Dokumente mehrfach hinzufügen

Dokumente mehrfach hinzufügen
Referenz-ERP bietet die Möglichkeit, mehreren gleichartigen
Objekten (nämlich genau denen aus einer Auswahlliste mit zugehöriger
Ansichtsdefinition ein Dokument zuzuordnen, welches dann aber nur genau einmal
im Archiv existiert, die anderen Einträge sind nur Links/Verweise auf den
Ursprung!). Diese Funktionalität kann man sich per privater Funktion mit
gleichem Controlstring, erweitert um eine angehängte „1“, einrichten.
Also z.B.
^jpl fa_view AMIC_KUNDE
1
führt nach Auswahl von mehreren Kunden dazu, dass ein
Dateiauswahl-Dialog aufgeht, in dem man das zu archivierende Dokument angegeben
kann. Danach werden mit den einschlägigen Funktionen jeweilige Umgebungen
berechnet und die notwendigen Einträge im Formulararchiv veranlasst.

---

## Dividenden verwalten

Dividenden verwalten
Um eine Dividendenausschüttung am Ende eines
Wirtschaftsjahrs vornehmen zu können, müssen vorher die dafür notwendigen
Dividendendaten erfasst werden. Dazu gehören ein Startdatum, ein Enddatum, ein
Beschlussdatum, ein Zahldatum und eine Leistung je Aktie. Es ist ratsam, dass
die Dividendenzeiträume den Wirtschaftsjahren entsprechen.
Die Daten für eine Dividendenausschüttung werden in
der Liste „Dividenden verwalten“ gepflegt und gehören zu den Stammdaten. Das
heißt, dass wie die Aktionäre die Daten für die Dividenden durch die Funktionen
Neu
F8
,
Ändern
F5
,
Ansehen
F6
und
Löschen
F7
gepflegt werden können. Nach Anwahl
einer dieser Funktionen öffnet sich die Dividendenverwaltungsmaske.
In dieser Maske können durch Einrichterparameter
folgende Einstellungen vorgenommen werden:
•
Verhalten bei fehlender Verbindung zum Wirtschaftsjahr
o
FEHLER(Standard) – Es muss ein
Wirtschaftsjahr in Referenz-ERP geben, das den Start- und Enddaten der Dividende
entspricht.
o
WAR
[...]


---

## Tabs

Tabs
Im Folgenden werden alle Funktionen beschrieben.

---

## Doppelte Einträge

Doppelte Einträge
Bei der Archivierung in die Datenbank wird eine
Prüfsumme erstellt, die mit dem Beleg gehalten wird. Damit kann u. a.
festgestellt werden, ob ein Beleg schon physikalisch im Formulararchiv vorhanden
ist.
Dieser Schalter bewirkt also eine einfache Möglichkeit
physikalische Dubletten zu unterbinden. (Diese können z.B. durch gewollten oder
ungewollten Mehrfachdruck entstehen.)
Durch Verwendung des EDOC-PrintPro-Systems hat sich
aber herausgestellt, dass die verbesserte Detail-Treue eben durch eine
Abschwächung dieses Features erkauft wird.
Das System erstellt momentan nicht mehr identische
Binär-Dateien. Deshalb fällt diese Prüfung auf Gleichheit aus.

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
      können nur Belege eingereicht werden, die
[...]


---

## E-Mail-Connector

E-Mail-Connector
Das Modul Email-Connector dient der Verarbeitung und
Archivierung ankommender Mails in Zusammenarbeit mit Referenz-ERP.

---

## Anhang Umwandlung

Anhang Umwandlung
Im Profil kann eingestellt werden, dass eine
Umwandlung der Anhänge in das Format PDF/A (
Format zur Langzeitarchivierung
digitaler Dokumente
) erfolgen soll.
Die Dokumente werden zusätzlich zu den ursprünglichen
Dokumenten im Archiv gespeichert.
Aktuell werden nur Excel-Dokumente in das Format PDF/A
umgewandelt.

---

## Drucke Untersuchungsetiketten(EPA Labor_DruckeUEtiketten)

Drucke Untersuchungsetiketten(EPA Labor_DruckeUEtiketten)
Bezeichnung
Standardwert
Erklärung
Vorbelegung: Soll die Druckauswahl
      angezeigt werden
Nein
Wenn
      dieser Wert auf Nein steht, ist die Vorbelegung ohne Druckerauswahl.
Steht der Wert auf Ja, wird vorm
      Drucken, dass Auswahlfenster für den Drucker geöffnet.

---

## Labormethoden(EPA Labormethoden

Labormethod
en(EPA Labormethoden
Bezeichnung
Standardwert
Erklärung
Erweiterte Einstellungen
Nein
Zeigt neu hinzugefügte Felder
      an.

---

## Laborverfahren(EPA Laborverfahren)

Labor
verfahren(EPA Laborverfahren)
Bezeichnung
Standardwert
Erklärung
Erweiterte Einstellungen
Nein
Zeigt neu hinzugefügte Felder
      an.

---

## Ereignisbehandlung

Ereignisbehandlung
In den Fällen in denen die Komplexität den jetzigen
Rahmen sprengt, lässt sich nun noch die Verarbeitung oder auch Vervollständigung
mit Hilfe eines VBA-Skriptes nachbessern bzw. überhaupt durchführen.
Das System führt dabei auf Wunsch zu den 3
Zeitpunkten, nämlich bevor der Import startet, während jedes Datei-Importes und
nachdem der Import durchgeführt worden ist, 3 angebbare VBA-Skripte durch. Damit
man die Möglichkeit hat, einen Import-Vorgang in einem großen Skript zu
verarbeiten, ist die Möglichkeit Parameter zu übergeben, integriert worden.
Im obigen Beispiel wird das vba-Script fa_import
jeweils mit entsprechenden Parametern aufgerufen. Wie üblich und
vereinbarungsgemäß sollten dabei „private“ Parameter mit „p_“ anfangen. Das
garantiert keine Überschneidung mit vom System verwendeten Namen.
Fa_import_Test hat folgenden Inhalt:
option explicit
' Binärer Import ins Formulararchiv
dim owner
dim p_status
dim fam_ref_vorg
dim p_referenz
dim belegnummer
di
[...]


---

## Erfasserwechsel

Erfasserwechsel
Direktsprung
[ERFW]
Hier wird der Erfasserwechsel durchgeführt. Beim
Öffnen der Maske wird entweder erst der angemeldete Erfasser angezeigt oder es
kann – wenn kein Erfasser angemeldet ist – sofort ein neuer Erfasser angewählt
werden. Um einen Erfasser zu wechseln muss, der aktuell angemeldete Erfasser,
erst abgemeldet werden.
Schneller Erfasserwechsel
Direktsprung
[SERFW]
Zusätzlich gibt es noch einen schnellen
Erfasserwechsel. Wenn ein Erfasser angemeldet ist, wird er beim Öffnen der Maske
sofort abgemeldet. Danach kann ein neuer Erfasser allein durch die Eingabe
seines Passworts wieder eingeloggt werden. Deswegen kann diese Variante nur
verwendet werden, wenn die Erfasserpasswörter eindeutig sind. Um zu überprüfen,
ob die Passwörter eindeutig sind, werden mit der Funktion
Doppelte Passwörter anzeigen
im
Erfasserstamm die doppelten Passwörter angezeigt.

---

## Erfassung und Korrektur

Erfassung und Korrektur

---

## Erweiterte Eingabemöglichkeiten

Erweiterte Eingabemöglichkeiten
•
F8
(Neue Partie anlegen, nur
im Partiefenster!): Es wird eine neue Partie mit Standardvorbelegung erzeugt.
Bei Übernahme (
F9
) wird diese
zugeordnet.
•
SF8
(nur im Partiefenster) :
Die automatische Suche wird manuell ausgelöst, die bisherige Partieverteilung
wird überschrieben
•
Eingabe einer Partie, in der die Warenposition nicht vorhanden ist: Falls
in der Partie Fremdartikel zulässig eingestellt
und
unter
[FRZ]
Hinzufügen neuer Artikel erlaubt ist,
wird dieser Artikel nach Bestätigung automatisch in der Partie aufgenommen.
•
Änderung der Warenmenge: Bei der Ersterfassung wird die Partieautomatik
wieder aufgerufen, im Korrekturfall wird die Partiezuordnung nicht verändert.
Sie muss gegebenenfalls angepasst werden.
•
Partienummer = 0 oder Menge = 0: diese Zeile wird nicht berücksichtigt.
Löschen einer Zeile mit
Strg+Umschalt+Entf

---

## Ersetzungstexte

Ersetzungstexte
Hauptmenü
Systempflege
Individuelle Textersetzung
Direktsprung
[TEXTM]
Hier lassen sich die Texte von Anwendungen insofern
bearbeiten, dass für die jeweiligen Originaltexte Alternativen angegeben werden
können.
Eingrenzung bzw. Filterung erfolgt hier über die
Anwendungsbezeichnung, Anwendungs-Id, oder über die Modulnummer.
Die Übersicht enthält folgende Elemente:
Feld
Beschreibung
Nummer
Nummer des Moduls
Ist
      keine Nummer angegeben, ist der Text nicht für das Modul gespeichert. Es
      existiert dann auch kein Ersetzungstext.
Bezeichnung
Bezeichnung des Moduls
Siehe Modulnummer
Originaltext
Originaltext der ausgewählten
      Anwendung zu der Alternativtexte gespeichert werden sollen.
Ersetzungstext
Der
      alternative Ersetzungstext
Die Ersetzungstexte werden zu den angegebenen
Modulnummern gespeichert.
Die Daten lassen sich hier über das Funktionsmenü
ändern und ansehen.
Möchte man alternative Texte für die ausgewählte
Anwendung einrichten, so gelan
[...]


---

## Datendrehscheibe Statistikexport

Datendrehscheibe
Statistikexport
Mit diesem Event kann der Statistikexport
automatisiert werden, dazu wird auf der Registerkarte Vorlagen der Schalter
Statistikexport auf Ja gesetellt.
begin
call
Fehlerprotokoll
(
in_text
=
'Start Statistik
Export'
);
call
amic_evt_StatistikExport
(
0
,
0
);
call
Fehlerprotokoll
(
in_text
=
'Ende Statistik
Export'
)
exception
when
others
then call
fehlerprotokoll
(
in_text
=
'FEHLER Statistik
Export!'
)
end
Der Event erzeugt eine Statistikdatei von der letzten
geschlossen Periode die noch nicht Exportiert worden ist.

---

## Events

Events
Events sind Ereignisse, die zu bestimmten Zeiten an
allen oder definierten Tagen in der Datenbank stattfinden. Mit Events können
Reorganisationen, Backups und verschiedene andere Prozesse in Lastschwachen
Zeiten angestoßen werden.

---

## Export AMICAR-Verfahren

Export AMICAR-Verfahren
Die AMICAR-Methode ist unter „Dateisystem –
Abgrenzung“ beschrieben.
(Beachten Sie bitte dass es natürlich keinen Export
gibt, wenn man sich für die Archivierung ins Dateisystem entschieden haben
sollte)
Ist der Export durchgeführt dann bekommen Sie z.B.
folgendes Protokoll
welches über Status, Umfang und Vorkommnisse beim
Export berichtet.
Beim AMICAR-Verfahren können Sie zusätzlich über die
Einstellung
Volumen
eine gewünschte
Volumenaufteilung durchführen.

---

## Archiv-Manager Sonstiges

Archiv-Manager Sonstiges
Signieren durchstarten
JA/NEIN - Kennzeichen
Automatik-Profile
JA/NEIN - Kennzeichen
Automatik-Import
JA/NEIN - Kennzeichen
Anlagen-Zuordnung
Legt
      fest welche Gruppe den Anlagen zugeordnet wird.
Signatur-Importpfad
Legt
      den Pfad für Signatur-Importe fest.
Mandantenserver
      Intervall
Legt
      die Wartezeit in Sekunden fest in der Mandantenserver höchstens
      hintereinander Archiv-Importe ausführen soll. (Standard ist 2)

---

## Finanzbuchhaltung

Finanzbuchhaltung
Frage: Der Steuersatz hat
sich geändert, was muss ich berücksichtigen/einstellen?
Antwort:
Bei einer Steuersatzänderung müssen mehrere Faktoren
berücksichtigt werden. Dazu stehen 2 Anleitungen bereit:
-
Steuersatz (ändern)
-
Erlöskennziffer
Kontozuordnung
Information für alle Referenz-ERP-Nutzer, die ihre Daten
über die Datevschnittstelle exportieren:
https://apps.datev.de/dnlexka/document/1018040
Nach den Änderungen der Steuersätze muss der
Mandantenserver neugestartet werden. Dafür mit dem Direktsprung
[MSI]
in die Maske des Mandantenservers. Hier
die Funktion
Stop Mandantenserver
und danach die Funktion
Normale
Bearbeitung
ausführen.
Eine grobe Übersicht der wichtigsten Konten:
SKR04
Steuerkonten
Beschreibung
1403
Abziehbare Vorsteuer 5%
1405
Abziehbare Vorsteuer 16%
3803
Umsatzsteuer 5 %
3805
Umsatzsteuer 16 %
Skontikonten
Beschreibung
4732
Gewährte Skonti 5%
4735
Gewährte Skonti 16%
5732
Erhaltene Skonti 5%
5737
Erhaltene Skonti 16%
5747
Erhaltene Skonti innnerg
[...]


---

## Format af_regbezirk

Format af_regbezirk
Im Feld Regbezirk auf der Anschriftenmaske kann man
mit
F3
den Regierungsbezirk
auswählen, wenn dieser vorher bei den Formatlisten eingepflegt wurden.
Siehe
dazu auch Format
af_kreis.

---

## Format af_kreis

Format af_kreis
Im Feld Kreis bei den Anschriften kann über
F3
ein Kreis ausgewählt werden, wenn dieser
vorher bei den Formatlisten eingerichtet wurden. Die Kreise sind über die
Formatliste mit den Regierungsbezirken verknüpft, wenn man das Feld „Kommentar,
Schnipsel“ mit der Nummer des zugehörigen Regierungsbezirkes füllt. Dazu ist es
sinnvoll, erst die Regierungsbezirke und dann die Kreise zu pflegen.
Wenn man dann auf der Anschriftenmaske mit
F3
einen Kreis auswählt, füllt sich das
Feld Regbezirk mit dem zugehörigen Regierungsbezirk.

---

## Formulararchiv-Gruppen

Formulararchiv-Gruppen
Das Archiv ist um die Möglichkeit der Gruppierung
erweitert worden. Es können jetzt Archivelemente in einer Gruppe zusammengefasst
werden; diese Gruppe trägt eine Gruppennummer sowie zwei weitere Kennzeichen.
Das erste Kennzeichen steuert die Priorität des Beleges innerhalb dieser Gruppe
(Typ Zahl), das zweite Kennzeichen steuert eine Linie innerhalb dieser Gruppe
(Typ Zeichenkette).
Beispiel: Alle Belege einer Streckenverarbeitung
besitzen eine Streckennummer, diese Streckennummer ist die Gruppe. Innerhalb der
Strecke gibt es gewisse Zusammenhänge zwischen Belegen, wie z.B. der
Lieferschein 1000 mit seinem Touravis, dem Frachtpapier und dem Zolldokument.
Der Zusammenhalt dieser Belege wird über das Linienkennzeichen festgehalten. Des
Weiteren ist nun innerhalb so einer Linie ein Beleg als der führende Beleg
ausgezeichnet, dieser bekommt dann das Prioritätskennzeichen 1, alle anderen
z.B. 2. Wird nun die Linie Lieferschein mit Frachtbrief, Zollschein
[...]


---

## Formulare pflegen

Formulare pflegen
In diesen Dialog können alle Kassenformulare um
gesetzliche Informationen zur Kassenverordnung ergänzt werden.

---

## AIS

AIS
Auf der Registerkarte „AIS“  können eine oder
mehrere AIS-Gruppen den jeweiligen Vorgangsmasken zugeordnet werden. Dabei ist
zu beachten,
dass alle AIS-Gruppen
die einer Vorgangsmaske zugewiesen
worden sind auch beim Aktualisierungsaufruf des AIS aktualisiert werden.
Deswegen ist darauf zu achten, dass keine Zeitintensiven SQL Statements
ausgeführt werden, da diese den Erfassungsablauf massiv stören könnten
.
Gridfelder
Beschreibung
Gruppenname
In
      diesem Feld wird die AIS Gruppe hinterlegt
AIS
      Makro
Das
      AIS Makro wird aus der AIS-Gruppe gelesen. Ist kein Makro hinterlegt wird
      das AIS nur an den Standardpunkten im Vorgang aktualisiert z.B.
      Kundenwechsel auf der SVMAIN Maske.
Unit
      Name
Funktion des Makro welches
      aufgerufen werden soll, wenn eine Aktualisierung des AIS vorgenommen
      wird.
Eine Beispieleinrichtung und Beschreibung für im AIS
im Vorgang finden sie
hier.

---

## Eingabe - Eingabefelder

Eingabe
- Eingabefelder
Auf der Registerkarte „Eingabefelder“ stehen folgende
Felder zur Verfügung.
Feld
Beschreibung
1.
      Eingabefeld
Die
      Eingabefelder legen die Reihenfolge der Vorgangsfelder fest.
2.
      Eingabefeld
Siehe „1. Eingabefeld“
3.
      Eingabefeld
Siehe „1. Eingabefeld“
4.
      Eingabefeld
Siehe „1. Eingabefeld“
5.
      Eingabefeld
Siehe „1. Eingabefeld“
Startfeld
Das
      Startfeld legt fest, in welchem Feld man beim Starten eines neuen Beleges
      anfängt.
Liefer-/Plan-Datum pro
      Artikel
Festlegung ob das Liefer-/Plandatum
      pro Artikel änderbar sein soll.
Preisdatum pro Artikel
Festlegen, ob das Preisbezugsdatum
      pro Artikel änderbar sein soll.
…
      mit Warnung?
Gibt
      bei Änderungen am Preisdatum des Artikels eine entsprechende Meldung auf
      dem Bildschirm aus.
Abgrenzungsdatum pro
      Artikel
Festlegen, ob das Abgrenzungsdatum
      pro Artikel änderbar sein soll.
…
      mit Warnung?
Gibt
      bei Ände
[...]


---

## Partie

Partie
Es gibt eine Reihe von Einstellungen, die jetzt nicht
mehr wie früher unter SPA vorgenommen werden, sondern speziell für
Vorgangsunterklassen hinterlegt werden.
HINWEIS:
Man achte bitte darauf, dass alle relevanten
Unterklassen bezüglich ihrer Partieeinstellungen überprüft werden.
Folgende Felder stehen ihnen auf dieser Registerkarte
zur Verfügung.
Feld
Beschreibung
Alternative Itembox
Hier
      kann eine alternative Itembox zur Auswahl von Partien hinterlegt werden.
      Diese bietet mehr Flexibilität bezüglich der unterschiedlichen
      Unterklassen.
Wir
      raten immer ausgehend von der Standard Itembox auf  die korrekten
      Angaben der Returnwerte zu achten.
DB-Prozedur für
      Verteilung
Hier
      kann eine private Prozedur für die Verteilung eingetragen
      werden.
DB-Funktion für
      Gebindeparameter
Hier
      kann eine private Prozedur für die Gebindeparameter eingetragen
      werden.
DB-Prozedur für
      Neuanlage
Hier
      kann eine
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

## Funktionen in der Auswahlliste

Funktionen in der Auswahlliste

---

## Gedruckte Vorgänge ohne Archiv-Belege

Gedruckte Vorgänge ohne
Archiv-Belege
Hauptmenü
Systempflege
Abstimmung
Gedruckte Vorgänge ohne Archiv-Belege
Direktsprung
[FANAR]
Ein Vorgang gilt als archiviert, wenn er ein Dokument
im Archiv vorweisen kann, dessen Belegreferenz der Beleg-Referenz des Vorgangs
entspricht und dessen Belegklasse der Klasse des Vorgangs entspricht.
Diese Variante erlaubt das "Nacharchivieren".
Nacharchivieren bedeutet das ein Vorgang gedruckt
wurde, aber nicht archiviert wurde. Gründe hierfür können sein:
•
Archiv stand zum Zeitpunkt des Drucks nicht zur Verfügung.
•
Druck war nicht vorgesehen für Archivierung.
Die Variante bietet für die Nacharchivierung in Frage
kommenden Druck-Vorgänge an, d.h. solche Vorgänge die zwar gedruckt sind, aber
keine Archivierung vorweisen können, obwohl sie nach-archivierbar wären.
Die Nacharchivierung legt die Archiv-Dokumente mit dem
im Vorgang verzeichneten
1)
Druck-Datum als Archiv-/Druckdatum und
2)
Druck-Bediener als Anleger
an.
Auswahlliste
Kndnr.
„Ko
[...]


---

## Gelöschte Aktionäre

Gelöschte Aktionäre
Da die Daten eines gelöschten Aktionärs eventuell für
bereits abgerechnete Dividenden benötigt werden, bleibt dieser im System
gespeichert und wird unter der Ansicht „Gelöschte Aktionäre“ geführt. Von hier
aus kann der Aktionär auch wieder aktiviert werden[siehe
Aktionäre verwalten
].
Folgende Daten werden für einen gelöschten Aktionär
angezeigt: Aktionärsnummer, Nachname, Vorname, Straße, Postleitzahl, Ort,
Vertreter, Status, Eintrittsdatum, Austrittsdatum. Über diese Eigenschaften kann
auch unter
Bereich/Profile
F2
eine Einschränkung der angezeigten
Datensätze vorgenommen werden.

---

## Geschäftsvorfälle

Geschäftsvorfälle

---

## Scanner/Barcodeleser

Scanner/Barcodeleser
Ein Scanner wird vor die Tastatur geschaltet. Eine
Implementation von seriellen Scannern wird nicht unterstützt
Scanner:
Scanner DL 910-61 von DATALOGIC
Barcodeleser:
Jeder USB-Barcodeleser

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

## Hauptmenü

Hauptmenü

---

## Hinzufügen (Archiv)

Hinzufügen (Archiv)
Es werden keinerlei COM-Objekte mehr verwendet.

---

## Homepage anzeigen

Homepage anzeigen
Diese Funktion ruft den Standardbrowser auf und öffnet
die Seite, welche Sie im Feld Homepage unter dem Tabreiter „Zusätze“
 angegeben haben.
Wenn die Angabe inkorrekt ist, wird ein Eintrag im
Fehlerprotokoll geschrieben oder der Browser findet die Seite nicht. (Je nach
Art des Fehlers)
Bei einem leeren Homepage-Feld wird darauf hingewiesen
mit einer Warnung und dem Wechseln in das Homepage-Feld.

---

## Fehlercodes und deren Behebung

Fehlercodes und deren Behebung
Hier finden sich die Fehlercodes und eventuelle
Lösungsmöglichkeiten.
Fehlercode
Fehlertext
Behebung
ohne
Fehler beim Öffnen der Verbindung!
(An error message
      cannot be displayed because an optional resource assembly containing it
      cannot be found)
Dieser Fehler bezieht sich auf die
      IP-Verbindung WLAN/Netzwerk) zwischen dem MDE (Scanner) und
      Multilink.
Unter Umständen ist der Aufbau der
      TCP/IP-Verbindung fehlgeschlagen, weil gerade kein WLAN zur Verfügung
      stand.
Bei
      dauerhaftem auftreten sollte die Netzwerkverbindung zwischen MDE (Scanner)
      und Multilink-Rechner geprüft werden
      (WLAN-Einrichtung/Verschlüsselung/ggf. Router/Windows-Firewall auf
      Multilinkrechner).
Das
      Terminal sollte im eingeschalteten Zustand auf einen Ping reagieren,
      Multilink auf eine Telnet-verbindung auf Port 8591. Darüber lässt sich die
      Netzwerkverbindung mit Hilfe eines weiteren Rechners im Netzw
[...]


---

## Installation der Identass Software

Installation der Identass Software
Scanner:
Die Dateien aus der .zip werden auf die Speicherkarte
des Scanner entpackt. Es befinden sich nun 3 Ordner auf der Speicherkarte. Der
Inhalt des Ordners „
Windows
“ muss in das Verzeichnis
Windows
und
der Inhalt des Ordners „
Program Files
“ ebenso in das entsprechende
Verzeichnis
Program Files
kopiert werden. Der Ordner „
Application
“
verbleibt an Ort und Stelle.
Gehen Sie nun in den Ordner
Program Files
MDE
MDE.exe
Das Programm wird installiert und Sie finden
anschließend ein neues Icon mit dem Namen Identass auf dem Desktop des
Scanners.
PC
:
Entpacken Sie den Inhalt der .zip Datei in das
Verzeichnis
Program Files
auf der Festplatte ihres PC´s.

---

## Importpfad

Importpfad
Gibt den Pfad im Dateisystem an, wo die zu
importierenden Belege erwartet werden.

---

## Individuelle Textersetzung

Individuelle Textersetzung
Die Hilfe hierzu finden Sie unter
Zusatzprogramme > Individuelle Textersetzung
von Anwendungstexten

---

## OLAP

OLAP
OLAP steht für „Online-Analytical-Processing“. Es
steht auf jeder Auswahlliste zur Verfügung

---

## Auswahlliste Datei-Export (openTRANS)

Auswahlliste Datei-Export  (openTRANS)
Mit Hilfe der Variante Datei-Export erhalten Sie eine
Übersicht über im Dateisystem bereitgestellte Dateien und deren zugeordneten
Vorgänge. Doppelte Exporte werden farblich markiert.
Sie haben mit Hilfe der Funktion „Löschen“ die
Möglichkeit, gezielt Exporte aus dem Dateisystem zu entfernen.
Einrichtung
Aktivieren Sie die nachfolgenden Funktionen, um die
Auswahlliste zur Anzeige von exportierten Dateien zu aktualisieren bzw.
einzurichten.
Externe Kommunikation
openTRANS
Dateisystem Einrichtung
Administration
Firmenkonstanten
Bediener
Fremdserver Rechte zuordnen

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
auch diesen
[...]


---

## Ausgewählte JVARS

Ausgewählte JVARS
JVars
Die JVARS des Owners 6000 geben
      zur Laufzeit Auskunft über den aktuellen Kontext im
  Programm.
JVAR_KOMPETENZ_HELPER_BAG
Die
      JVAR der „obersten“ Anwendung.
JVAR_KOMPETENZ_IST_ANWENDUNG
1,
      wenn die aktuelle Position eine Anwendung ist, sonst 0.
JVAR_MASKE
Die
      JVAR der Maske
K_ANWENDUNG
Name
      der obersten Anwendung
K_ANZAHL_MARKIERT
die
      Anzahl der markierten Zeilen der obersten Anwendung.
K_FUNKTION
Der
      „letzte“ ausgeführte Controlstring über SHIFT-F4
K_FUNKTION_AKTUELL
Der
      „letzte“ ausgeführte Controlstring
K_MASKE
Der
      Name der Maske
K_MASKE_DIALOG
1
      wenn die Maske ein Dialog ist, 0 sonst
K_MENU_LINKS
Wert
      ermittelt durch das ActiveX-Menü
K_MENU_RECHTS
Wert
      ermittelt durch das ActiveX-Menü
K_OPTIONBOX
Optboxid der „letzten“
      Optionbox
K_VARIANTE
Variante der obersten
      Anwendung
K_VARIANTE_BESITZER
0
      Branchen-ERP, 1 sonst
JVars
Die JVARS des Owners 3561 geben zur

[...]


---

## JVARS

JVARS

---

## Verteilung der Owner

Verteilung der Owner
Kurz :
JVARS sind für alle da …, aber
Lang:
Es gibt JVARS für Branchen-ERP als Systemhaus und es gibt
JVARS für den Anwendungsprogrammierer – drinnen wie draußen.
Siehe
JVar-Bereich

---

## Kassenverwaltung (logische Kasse)

Kassenverwaltung (logische Kasse)
Funktionen
Kasse deaktivieren
ACHTUNG! Bitte verwenden Sie diese
      Funktion nur mit Bedacht. Eine einmal vergebene Kassenseriennummer sollte
      zugewiesen bleiben.
Wenn
      diese Seriennummer ausnahmsweise aus guten Gründen einer anderen Kasse
      zugewiesen werden soll, so wird diese Kasse fortan nicht wieder verwendet
      werden können und auch nicht mit einer neuen Seriennummer versehen werden
      dürfen.
Die
      Zuweisung der Seriennummer an eine neue Kasse müssen Sie in jedem Fall an
      die Finanzbehörden melden.
Kassensystem bearbeiten
ruft
      die
Bearbeitungsmaske des
      verbundenen Kassensystems
auf.
Standard Anzeigeschema
      einrichten
richtet ein Anzeigeschema für ein
externes
      Display
nach Branchen-ERP-Vorlage ein.
Ext.
      Display testen
Führt Sie durch den Test eines
externen
      Kassendisplay
AnyBill einrichten
Öffnet die Profil-Liste für
AnyBill-Profile
, in der diese
      eingerichtet werden
[...]


---

## Konstante

Konstante
Mit Hilfe dieser Technik wird es möglich, bestimmte
Kern-Daten konstant vor zu belegen. Anwendungsgebiet ist z.B. die Belegklasse
konstant vor zu belegen, wenn man sowieso nur Belege eines Typus verarbeitet und
deshalb eine sonstige Kodierung nicht vorgesehen ist.

---

## Labordaten

Labordate
n
Hauptmenü
Saatzucht
Saatenlabor
Labordaten
oder Direktsprung
[LABOR]
Funktionen der Anwendung Labor
Funktion
Bedeutung
Neue
      Probe
Öffnet die Labormaske zum Erfassen
      einer neuen Probe.
Probendaten bearbeiten
Öffnet die Ausgewählte Probe zum
      Bearbeiten.
Probenuntersuchung
      bearbeiten
Probenzusatzdaten
      bearbeiten
Probendaten ansehen
Öffnet die Ausgewählte Probe nur zum
      Ansehen.
Nachuntersuchung
Ermöglicht das Nacherfassen
      einzelner Verfahren.
Methoden
Öffnet die Anwendung zur Pflege der
Methoden
Verfahren
Öffnet die Anwendung zur Pflege der
Verfahren
Löschen
Drucke Prüfbericht
Druckt ein oder mehrere
Prüfberichte
aus, die
      an einer
Methode
hinterlegt worden sind.
Drucke Teilprobenetikett
Druckt alle
Teilprobenetiketten
aus, die an der
Methode
hinterlegt wurde
Drucke
      Untersuchungsetiketten
Druckt alle Etiketten, die im
Verfahren
auf der Registerkarte
Allgemein
hinterlegt
      wurden.
Archiv Ansehen
Öffnet die Archiv
[...]


---

## Ladeschein zusammenstellen

Ladeschein zusammenstel
len
Auf dieser Erfassungsmaske werden alle ausgewählten
Positionen in der Auswahlliste „Aufträge Bearbeiten“ angezeigt. Es ist möglich
einzelnen Positionen wieder zu löschen und die Menge an der Position zu ändern.
Das Einfügen von Positionen ist nicht gestattet und wird daher unterdrückt. Die
User Felder werden vom ersten gewählten Auftrag in den Ladeschein mit
übernommen.
Feld
Beschreibung
Kundennummer
Im
      Feld Kundennummer muss ein Kunde eingetragen werden. Bei unterschiedlichen
      Auftragskunden kann in diesem Feld ein Platzhalterkunde hinterlegt werden.
      Bei der Umwandlung des Ladescheins mit dem Modul „
Rechnung Lieferschein aus Ladeschein
“ in
      der Anwendung „
Ladeschein Bearbeiten
“ wird dann aus
      jedem Auftrag ein
Lieferschein
erzeugt.
Belegnummer
In
      dem Feld Belegnummer wird dann die erzeugte Nummer des Ladescheins
      angezeigt.
Mengenfeld
In
      dem Mengenfeld kann vor dem Erzeugen des Ladescheins noch ei
[...]


---

## Ladescheinbearbeitung

Ladescheinbearbeitung
Als erstes müssen die
Scancodes
„LAD“ und „LADENDE“ eingerichtet
werden. Diese können bequem auch mit der Funktion
Standard Einstellung Scancodes
eingerichtet
werden. Danach können die
Scancodes
noch bearbeitet werden.
Um eine Ladescheinliste auszudrucken wurde in der
Anwendung Branchen-ERP Etikettendruck in der Variante „Vorlagen Branchen-ERP Etikettendruck
Reporte“ eine Vorlage erstellt. Anhand dieser Vorlage kann dann eine Pickliste
erstellt werden. Auf dieser Liste können dann auch die erforderlichen Scancodes
für das Ladescheinstarten angedruckt werden.
Ablauf
Mit diesem Modul können
Aufträge
, die zu einem Ladeschein umgewandelt worden
sind, bearbeitet werden. Aus diesen Ladeschein wird dann ein
Lieferschein
erzeugt, und die Lieferscheinmenge wird
dann per Teildisposition vom Auftrag abgebucht.
Dabei ist zu beachten, dass der Scanner keine
Partieverteilung kennt. Dies bedeutet, dass es immer nur eine 1 zu1 Beziehung
geben kann. Sollen mehrere Partien eines Artikel
[...]


---

## Listen

Listen
Referenz-ERP stellt in der Aktionärsverwaltung verschiedene
Listen zur Verfügung, die wiederum verschiedene Funktionalitäten bieten und
deren Anzeige über
Bereich/Profile
F2
wie gewohnt weiter eingeschränkt
werden kann.

---

## Lokalitätsdimensionen

Lokalitätsdimensionen
Die Lokalitätsdimensionen stellen die Dimensionen dar,
aus welchem eine Lokalität bestehen kann. Zum erweitern der vorhandenen
Dimensionen existiert das Anwendungsformat „AF_LVS_DIMEN“.
Voraussetzung für das Anwendungsformat ist, das die
Dimension „0“ „--“ existiert. Diese ist jedoch bei der Auslieferung von Referenz-ERP
bereits angelegt.

---

## Lokalitätstyp

Lokali
tätstyp
Der Lokalitätstyp stellt den Typ der Lokalität dar.
Zum Anlegen von Typen gibt es das Anwendungsformat „AF_LVS_LOKTY“.
In diesem können die einzelnen Typen angelegt werden.
Eine Voraussetzung ist, dass mindestens das Format „0“ „--“ angelegt sein muss.
Dieses ist jedoch bei der Auslieferung von Referenz-ERP bereits angelegt.

---

## Aufladen

Aufladen
Sind alle Waren in den Warenausgang gebracht worden,
so kann aufgeladen werden.
Die Einzelnen Ladeträger können mit Hilfe der
Datenbankfunktion „AMIC_LVS_AUFLADEN“ dem aufzuladenden Vorgang zugeordnet
werden und es werden LVS-Vorgangsimporte der Vorgangsunterklasse 90 erzeugt.
Erst am Ende des Aufladens wird daraus ein
Lieferschein mit Hilfe der Datenbankfunktion „
AMIC_LVS_AUFLADENENDE
“
die Positionen und erstellt einen zweiten Satz mit den Importdaten des
Ladescheins.
Empfohlener Arbeitsablauf Scanner:
•
Scan „AUFLADEN
•
Scan Ladescheinnummer
•
Scan der NVE
o
Anzeige der NVE-Info
•
Scan AUFLADENENDE
o
Prüfung auf
Vollständigkeit
•
Erzeugen eines Belegs im VIMP

---

## LWK-Übertrage

LWK-Übertrage
Hauptmenü
Saatzucht
Saatenlabor
Labordaten
Variante LWK-Übertrag
Funktion
Übertrage an die LWK
oder Direktsprung
[LABOR]
Die Funktion
Übertrag an die LWK
findet man in der
Variante „LWK-Übertrag“. In dieser Variante werden die Daten bereits so
angezeigt, wie sie dann übertragen werden. In der F2-Bereichsauswahl wird neben
der Probenummer und der Partiebezeichnung auch die Freigabe abgefragt. Dieser
Wert wird auf der Labordatenmaske abgefragt und es werden nur die Daten
übertragen, bei denen die Freigabe auf
Ja
steht.
Sind alle Daten für die LWK erfasst, so kann man den
Übertrag mit der Funktion
Übertrage an die
LWK
starten. Es erscheint folgender Dialog, in dem man das
Versandprofil
, die
Mailadresse an die die Daten gesendet werden sollen und die Betreffzeile angeben
muss. Diese Daten werden gespeichert und beim nächsten Aufruf wieder
vorgeschlagen.

---

## Manuelle Privatisierung der Datenbank-Funktion

Manuelle Privatisierung der Datenbank-Funktion
Dazu kopiert man die am besten die ausgelieferte
Datenbank-Funktion und legt diese unter einem eigenen anderen Namen in der
Datenbank an. Den neuen Namen gibt man hier im Referenz-Dialog dem Referenz-ERP-System
bekannt. Updates von Referenz-ERP werden dann nicht wieder den Original-Zustand
herstellen.
CREATE FUNCTION
p_fa_ref_vorg
( IN  v_KlassNummer  integer,
IN  v_NumNummer
integer,
IN in_uklassnummer integer default 0,
IN in_jahrnummer   integer default
0,
IN in_unternummer  integer default 0
) returns char(20)
BEGIN
DECLARE fetch_fa_belegreferenz char(20);
select right('00'||mandnummer,2)
||
(
select left(formlstbezeich,2) from formatlist where formlstkennung='af_vorgang'
and formlstwert = v_KlassNummer )
||
right('00000000'|| v_NumNummer,8)
||
right('0000'|| in_jahrnummer,4)
into
fetch_fa_belegreferenz
from mandantstamm;
return fetch_fa_belegreferenz;
END
Und verändert die nach jeweiliger
Organisations-Vorgabe.
Nach Prüfung der Funk
[...]


---

## Parken von Belegen in der Marktkasse

Parken von Belegen in der Marktkasse
Ein Beleg kann in der Marktkasse geparkt werden. Das
bedeutet, dass der Beleg beiseite gelegt und gemerkt wird, um einen oder mehrere
Belege zwischenzeitlich abzuarbeiten. Der geparkte Beleg kann zu einem späteren
Zeitpunkt entparkt und weiter verarbeitet werden.
Einige Rahmenbedingungen gibt es jedoch:
•
Ein Beleg auf dem bereits Zahlungen geleistet wurden kann nicht geparkt
werden. Dazu müssen zunächst die Zahlungen storniert werden.
•
Solange ein Beleg geparkt wurde, kann die Kassenmaske nicht verlassen
werden, um z.B. eine Kundennummer oder Vorgangsunterklasse zu wechseln.
•
Es kann nur ein Beleg zur gleichen Zeit geparkt werden.

---

## Zahlung in der Marktkasse mit Touch-Funktion

Zahlung in der Marktkasse mit
Touch-Funktion
Sie wollen den offenen Beleg bezahlen.
•
Drücken Sie zunächst eine der Bezahlfunktionen wie „Bar“, „Gutschein“,
„EC-Karte“ o.ä.
•
Geben Sie im zweiten Schritt ggf. Zusatzinformationen ein, die für die
Abwicklung der Bezahlung notwendig sind.
•
Wählen Sie im Fall von Fremdwährung die Zahlwährung
•
Das Feld für den Zahlbetrag wird mit dem offenen Betrag in der aktuellen
Zahlwährung vorbelegt.
•
Geben Sie dann schließlich den Betrag des Zahlungsmittels ein
•
Schließen Sie die Eingabe mit „ENTER“ ab.
Es wird kurz die Zahlungsmaske geöffnet und wickelt
die Zahlung ab.
Es folgt ggf. der Bondruck.
Wurde im Steuerparameter
867 -
Rechnungsdruck bei
Barverkauf
eingestellt, dass ab einem bestimmten Betrag ein
Rechnungsdruck angeboten werden soll, so wird an dieser Stelle danach gefragt.

---

## Barzahlung

Barzahlung
Die Barzahlung erfolgt stets in Kassenwährung. Der
eingegebene Betrag wird in Kassenwährung verbucht. Es ist möglich, Tasten
einzurichten, die den Zahlbetrag mit einem bestimmten Betrag wie z.B. 5,10,20
oder 50 vorbelegen.

---

## Bezahlung per EC-Plus

Bezahlung per EC-Plus
Mit der EC-Plus Funktion ist es möglich einen
Auszahlungsbetrag bei EC-Zahlungen einzugeben.
EC-Plus Zahlung wird ausgelöst über den Button
"EC-Plus".
Es öffnet sich ein Dialog. In diesem Dialog ist es
möglich, den gewünschten Auszahlungsbetrag im Eingabefeld "Auszahlung"
einzugeben.
Der Dialog-Button "Übernehmen" löst die Zahlung
aus.
Der Dialog-Button "Abbruch" bricht die Zahlung ab und
es wird in den Erfassungsmodus gewechselt.
Über den Steuerparameter "Mindestzahlbetrag für
EC-Überzahlung" kann ein Mindestbetrag definiert werden, ab dem EC-Plus Zahlung
ausgelöst werden kann. Bei einem Steuerparameterwert von 0 wird die EC-Plus
Zahlung nicht ausgelöst. Standard Einstellung ist 0.

---

## Scheck / Bankeinzug

Scheck / Bankeinzug
Diese Zahlungsweisen werden nicht mehr unterstützt.

---

## Merkmale

Merkmale
Für Anschriften können mehrere Merkmale hinterlegt
werden. Man kann mit Hilfe dieser Merkmale über
Bereich/Profile
F2
Auswahllisten eingrenzen.
Für Merkmal 1-3 können in den Formaten „af_merkmal1“,
„af_merkmal2“ und „af_merkmal3“ beliebige Merkmale hinterlegt werden.
Merkmal 4 wird in Kombination mit einem numerischen
Datenfeld abgespeichert. Auch hier können wieder im Format „af_merkmal4“
Merkmale hinterlegt werden (z.B. Ackerfläche (ha), Rinder (Stück)) Entsprechend
müssen dann im Datenfeld z.B. 100,00 (für die Ackerfläche in ha) oder 50,00 (für
die Anzahl der Rinder) angegeben werden. Dadurch besteht die Möglichkeit, die
Anschriften z.B. nach der Größe der Betriebe einzuordnen.
Außerdem gibt es noch ein freies Merkmal, in welches
man beliebige Texte hineinschreiben kann, z.B. „Weihnachtspost 2005“ (Eine Art
Merker, an wen 2005 dieser Brief gesendet wurde).
Das Befüllen dieses Feldes soll später auch aus einem
Stapel möglich sein, an den man z.B. einen Serienbrief
[...]


---

## Modus

Modus
Wie schon erwähnt verwaltet das Archiv eine ganze
Reihe von verschiedenartigen Dokumenten. Über die gängigen Office-Dokumente über
PDF bis hin zu TIFF kann alles vertreten sein. Das Ansehen dieser Dokumente wird
nicht länger von Referenz-ERP übernommen, sondern eher den installierten Spezialisten
auf dem jeweiligen Computersystem bzw. den jeweiligen Vorlieben des
Anwenders.
Möchte nun der Referenz-ERP-Anwender ein Dokument anschauen,
so delegiert Referenz-ERP diese Aufgabe an das Windows-System. Dieses nämlich hat u.a.
hinterlegt welches Programm dafür zuständig sein soll. Auf einem Windows-XP
System kann man z.B. für PDF-Dateien folgendes recherchieren:
Somit ist der Adobe 7.0 auf meinem System der aktuelle
Viewer des PDF-Dokumentes.
Auch im Windows-Explorer unter ANSICHT/OPTIONEN erhält
man
Unter ÄNDERN die Möglichkeit evtl. ein
Alternativ-Programm zu wählen:
Und unter ERWEITERT
weitere
Diese Dinge sind zur Kenntnis wichtig, wenn es z.B.
darum geht, zur Ansicht den Adobe-Reader und n
[...]


---

## Muster

Muster
Das Muster beschreibt die zu erwartenden Daten mit
Hilfe eines regulären Ausdruckes. Die Beschreibungen innerhalb der Tabelle
beziehen sich deshalb in dem Falle auch auf dieses Muster – und nicht auf den
regulären Ausdruck in der Tabelle!

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

## Ermittlung des Nachhaltigkeitsstatus und der THG – Werte

Ermittlung des Nachhaltigkeitsstatus und der
THG – Werte
Ermittlung des Nachhaltigkeitsstatus
Die Ermittlung des Nachhaltigkeitsstatus erfolgt
aktuell über vier Ebenen. Wenn die jeweilig vorherige Ebene keinen Status
angegeben hat, folgt die nächste Ebene.
Ebene
Bezeichnung
Beschreibung
1
Artikelstamm Vorbelegung
      Warenbewegung
Auf
      der ersten Ebene gilt die Einstellung am Artikelstamm für die Vorbelegung
      der Warenbewegung. Dies gilt nur wenn man als Vorbelegung „Nicht
      Nachhaltig“ auswählt. Man kann also nur nachhaltige Waren künstlich zu
      „Nicht Nachhaltig“ machen und nicht andersherum
2
Kontrakt
Auf
      der zweiten Ebene gilt die Kontrakteinstellung.
3
Kunde / Mandant
Auf
      der dritten Ebene gilt die Einstellung des Kunden.
4
Auf
      der vierten Ebene gilt, wenn keine der vorherigen Ebenen einen Wert hat,
      so hat diese Bewegung keine Nachhaltigkeitsinformationen.
Ermittlung der THG – Werte
Die Ermittlung der THG – Werte ist abhängig
[...]


---

## Ändern F5

Ändern F5
Mit
F5
kann
man z.B. eine Hauptanschrift ändern.

---

## Neuzugang

Neuzugang
Neuzugänge können auf unterschiedliche Art und Weise
in die Anlagenbuchhaltung gelangen.
1.
Über die Belegerfassung der Finanzbuchhaltung. Wird ein Anlagenkonto bei der
Erfassung von Eingangsrechnungen angesprochen, so öffnet sich zuerst eine
Itembox mit den bereits erfassten Anlagegütern. Will man einen Zugang zu einem
bestehenden Anlagegut erfassen, so kann man dieses hier auswählen. Um ein neues
Anlagegut zu erfassen, wählt man den Punkt „—NEU—„ in der ersten Zeile der
Itembox. Soll der Betrag auf mehrere Anlagegüter verteilt werden so wählt man
den zweiten Punkt „—AUFTEILEN—". Es öffnet sich dann das Erfassungsfenster der
Anlagenbuchhaltung und man kann dort zusätzliche Angabe machen.
2.
Über die Variante „Eingangsrechnungen ohne Anlageneintrag“ im Anlagenstamm. Dort
erscheinen alle Eingangsrechnungen, bei denen ein Konto mit dem Kennzeichen
„Anlagekonto“ verwendet wurde und die nicht über die Belegerfassung direkt oder
nicht vollständig zugeordnet wurden
[...]


---

## Notfall Replikation

Notfall Replikation
Hauptmenü
Externe Kommunikation
Notfall
In der Maske Notfall kann ein Standortname angegeben
werden für den eine Notfall-Replikation erstellt werden soll. Es können auch
mehrere Standortnamen angegeben werden. Diese werden dann nacheinander erstellt.
Standortnamen dürfen nicht mit Sonderzeichen oder Zahlen beginnen, sondern
müssen mit einen Buchstaben beginnen.
Im Feld Name Datenbank werden vorhandenen
Notfall-Publikationen angezeigt. Ebenfalls wird dort vom System eingetragen, ob
die Notfall-Datenbank erstellt wurde.
Vor dem Ausführen der Prozedur müssen die
Einrichterparameter gesetzt werden.
Einrichterparameter:
Beschreibung
ReplikationsPfad:
Pfad
      in der die Datenbank der Notfall-Replikation angelegt wird. Zusätzlicher
      Ordner für den Standort wird angelegt.
PublisherName:
Name
      des Publishers der Original-Datenbank. Ist dieser nicht vorhanden wird er
      angelegt. Existiert bereits ein Publisher für die Original Datenbank wird

[...]


---

## Notizen

Notizen
Hier kann man viele Notizen zur Anschrift
eintragen.

---

## Arbeitsweise des Referenz-ERP-Nullsetzers

Arbeitsweise des Referenz-ERP-Nullsetzers
Die Inhalte aller im angewählten Bereich vorhandenen
Tabellen werden gelöscht. Bei einigen Tabellen unter besonderen
Vorbehalten/Einstellungen. Des Weiteren werden auf bestimmten Tabellen
Aktualisierungen durchgeführt.
Hier nun die genaue Auflistung der Aktionen in den
einzelnen Bereichen:

---

## Nur letzte Korrektur speichern

Nur letzte Korrektur speichern
Bei Vorgangsdrucken wird geprüft ob sich im
Formulararchiv schon Einträge mit
gleicher
Belegnummer, gleicher Vorgangsklasse
,
gleicher Vorgangs-Unternummer
und
gleicher Jahrnummer
befinden und wenn dies der
Fall sein sollte, dann wird kein neuer Formulararchiv-Eintrag angelegt, sondern
der jüngste dieser Belege erfährt ein Update.
Somit wird sichergestellt, dass sich immer nur die
letzte Korrektur eines Beleges im Archiv befindet.

---

## Partiebehandlung in MACROS

Partiebehandlung in MACROS
Zur Erzeugung von Partieverteilungen im MACRO werden
die folgenden Funktionen bereitgestellt:
Hinweis: Bitte bei der Korrektur einer Warenposition
nie
auf dem Original anwenden. Stets
positionausposition
und
replaceposition
benutzen!
function
StartPartieVerteilung
( pos_handle: integer ) : integer;
Einleitung einer Partieverteilung für eine
Warenposition (pos_handle). Vorher teilweise zu Ende geführte Verteilung wird
gelöscht.
Ergebnis : immer 1
function
AddPartieMenge
(
pos_handle: integer; partie_id: integer;
Partie_artiposit: integer;
menge: real;
artikel_hinzufuegen : integer) : integer;
Hinzufügen einer neuen Partie per (genauere)
Identifikation über die PartieId und der PartieArtiPosit. Die Menge muss in der
Mengeneinheit des Artikels (Ergebnismenge bei Gebinden!) übergeben werden. Bei
artikel_hinzufuegen = 1 wird der Artikel der Partie hinzugefügt, falls noch
nicht vorhanden.
Ergebnis 1, wenn erfolgreich
function
AddPartieMengeNummer
( pos_han
[...]


---

## Partien nachtragen

Partien nachtragen
In vielen vorgangsorientierten Auswahllisten wurde in
der Optionbox die Funktion’ Partien nachtragen’ hinzugefügt. Hiermit kann man in
Vorgangsbelegen auch noch nachträglich den Warenpositionen des Beleges Partien
hinzufügen oder abwählen, auch wenn der Beleg selbst nicht mehr bearbeitet
werden kann. Aus technischen Gründen gibt es allerdings einige
Einschränkungen:
•
Weiterverarbeitete Belege können nicht berücksichtigt werden (z.B.
umgewandelte Lieferscheine)
•
Warenpositionen, die durch Teilumwandlung entstanden sind, werden
ebenfalls nicht bearbeitet
•
Die Funktion ‚automatische Partiezuordnung’ steht nicht zur Verfügung
•
Eine Übernahme von Preisen findet nicht statt
Belege mit diesen Partienachträgen werden vom
Mandantenserver abgearbeitet. Sie sind bis zur vollständigen Abarbeitung im
Mandantenserver nicht korrigierbar!

---

## Private Sortierung/Tasten

Private
Sortierung/Tasten
Jedes Funktionsmenü
Dieses Menü
Private Sortierung/Tasten
Es öffnet sich ein Dialog, in dem die in blau
hinterlegten Feldern die Standardeinstellungen von Referenz-ERP angezeigt werden.
Zusätzlich gibt es Spalten, in denen man die Gestaltung der Funktionsmenüs
teilweise individuell anpassen kann. Damit die Änderungen wirksam werden, ist
nach dem Speichern die entsprechende Auswahlliste oder Maske neu aufzurufen.
Felder
Beschreibung
Sortierung
Die
      Sortierung wird mit Hilfe einer aufsteigenden Zahl festgelegt. Ändert man
      die Sortierung wird diese sofort im unteren Bereich
      dargestellt.
Funktionstaste
Die
      zulässigen Funktionstasten können mittels der F3-Auswahl ausgewählt
      werden. Wird eine Funktionstaste, die bereits in diesem Menü verwendet
      wurde, vergeben, so überschreibt die private Funktionstaste die
      Standardfunktionstaste.
Doppelklick (nur für die
      Auswahlliste)
In
      Auswahllisten kann man eine Zeile
[...]


---

## F2-Bereichsauswahl

F2-Bereichsauswahl
Die vorhandenen Profile werden in der linken Oben im
Menü-Band der Auswahlliste angezeigt. Bei Profilen handelt es sich um fest
eingestellte Bereichseingrenzungen des Datenmaterials, die in Verbindung mit
einer Variante ausgewertet werden sollen. Für unterschiedliche immer
wiederkehrende Anfragen an das System kann man einmal vorgenommene
Bereichseingrenzungen unter einem Namen speichern. Um Eingrenzungen vorzunehmen
und Profile zu bearbeiten, steht in Auswahllisten die Funktion
Bereichsauswahl
F2
zur Verfügung. Wenn man diese Funktion
betätig öffnet sich ein Dialog, in dem die möglichen Eingrenzungen des
Datenmaterials abgefragt werden.
Am linken Rand kann man das Schnellauswahlkriterium
markieren. Im Beispiel oben ist es die Lagernummer, die dann in der Auswahlliste
direkt abgefragt werden kann. Dazu muss man als Einstiegsverhalten „Daten nicht
sofort Anzeigen“ eingetragen haben, oder mit
Strg+Y
die Schnellabfrage aktivieren.
Rechts von der Bezeichnung k
[...]


---

## Programmhinweise

Programmhinweise
Dieser Bildschirm erscheint nach dem Anmelden an
Referenz-ERP, wenn für den Anwender noch ungelesene Informationen existieren.
Durch Klicken auf das Informationsicon (Priorität
Normal) oder das Achtungsicon (Priorität hoch) vor dem Informationstext gelangt
man in die zugeordnete Hilfe. Wenn man die Hilfe gelesen hat – also auf das Icon
geklickt hat – erscheint hinter der Zeile die Abfrage „Gelesen?“. Um die
Information oder der Hinweis beim nächsten Programmstart nicht mehr angezeigt zu
bekommen, setzt man hier einen Haken.

---

## Programmende

Programmende
Um das Programm zu verlassen muss man alle Funktionen,
Auswallisten und andere Dialoge verlassen. Dies geschieht in der Regel mit
ESCAPE. Drück man anschließend m Menü von Referenz-ERP erneut die ESCAPE-Taste, so
öffnet sich eine Dialogmaske mit der Abfrage „Wollen Sie das Programm beenden?“.
Bestätigt man dies mit OK, wird Referenz-ERP beendet.

---

## Protokoll des Archivdaten Imports

Protokoll des Archivdaten Imports
Erzeugt die schon abgebildeten Zusammenfassungen.

---

## Quick-Reporte im Dateisystem (Archiv)

Quick-Reporte im Dateisystem (Archiv)
Bei der Archivierung ins Dateisystem ist eine
Archivierung von Quick-Reporten nicht vorgesehen.

---

## 8.3.2210.20

8.3.2210.20
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2211.30

8.3.2211.30
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2211.9

8.3.2211.9
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2212.23

8.3.2212.23
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2302.17

8.3.2302.17
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2304.28

8.3.2304.28
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2303.31

8.3.2303.31
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2305.26

8.3.2305.26
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2306.23

8.3.2306.23
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2307.7

8.3.2307.7
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2306.9

8.3.2306.9
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2308.18

8.3.2308.18
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2308.4

8.3.2308.4
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2309.1

8.3.2309.1
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2310.27

8.3.2310.27
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2312.22

8.3.2312.22
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2311.10

8.3.2311.10
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 8.3.2312.8

8.3.2312.8
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2401.1

9.0.2401.1
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2401.3

9.0.2401.3
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2401.2

9.0.2401.2
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.1

9.0.2402.1
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2401.4

9.0.2401.4
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.10

9.0.2402.10
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.2

9.0.2402.2
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.4

9.0.2402.4
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.3

9.0.2402.3
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2402.8

9.0.2402.8
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2501.5

9.0.2501.5
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2501.6

9.0.2501.6
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2501.8

9.0.2501.8
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2502.5

9.0.2502.5
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2502.6

9.0.2502.6
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2502.8

9.0.2502.8
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2502.7

9.0.2502.7
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## 9.0.2502.9

9.0.2502.9
Zusammenfassung aller in diesem Release vorgenommenen
Softwareveränderungen.

---

## Referenzieren

Referenzieren
Behandelt die Thematik Formulararchiv-Einträge, um die
fehlende Referenznummer zu vervollständigen.
Es sind also Rahmendaten im Eintrag vorhanden, die
eine Generierung der Referenznummer ermöglichen.

---

## Reorganisation

Reorganisation
Im Referenz-ERP – System werden im Bereich der
Warenwirtschaft 4 zentrale Datenbereiche mit Daten gefüllt. Diese Datenbereiche
sollten unter gewissen Voraussetzungen gleiche Periodenwerte enthalten.
Die hier beschriebenen Abstimmwerkzeuge stellen eine
Werkzeugsammlung zu Bearbeitung uns bekannt gewordener Probleme dar und
ermöglichen einen vergleichenden Überblick und sollen bei der Lokalisierung und
Bereinigung von etwaigen Abweichungen unterstützen.
Die Abstimmung der Datenbestände sollte zum Standard
im Verfahren des Periodenabschlusses
[PERAW]
, in jedem Fall aber zum Verfahren
Jahresabschluss zählen. Zu spät erkannte Unstimmigkeiten vergrößern den Aufwand
zur Bereinigung enorm.
Falls Unsicherheit in der Bedienung oder dem
generellen Umgang mit den beschriebenen Werkzeugen besteht, ist die
Rückversicherung bei dem zuständigen Supporter angeraten.

---

## Remote-Sitzungen

Remote-Sitzungen
Die angesprochene Terminalserver-Problematik kann man
hier besänftigen.
Referenz-ERP erkennt, ob es sich um eine
Terminalserver-Sitzung handelt, und mit aktivem Schalter wird das Ansehen dann
in einem extra Fenster durchgeführt. Somit hat man den Komfort bei lokalen
Sitzungen die integrierte Ansicht zu genießen und kann gleichzeitig auf
Terminalservern arbeiten.

---

## Reportarchivierung ein/ausschalten

Reportarchivierung ein/ausschalten
Die Archivierung der Reporte lässt sich per
einstellen.
•
NEIN: Es werden grundsätzlich keine Reporte archiviert.
•
PDF: Wenn Reporte archiviert werden, dann im PDF-Format.
Die Auswahl, welcher Report archiviert wird, hängt
auch davon ab, was in der Anwendung „LISTEN“
und dort bei „Archivierung?“ eingerichtet ist.

---

## Reportarchivierung im Dateisystem

Reportarchivierung im Dateisystem
Bei der Archivierung ins Dateisystem ist eine
Archivierung von Reporten nicht vorgesehen.

---

## Rollenantragsmailabfrage(EPA Rollenantragsmailabfrage

Rollenantragsmailabfrage(EPA Rollenantragsmailabfrage
Bezeichnung
Standardwert
Erklärung
Rollenantragsmail
      abfragen
Nein
Dadurch erfolgt keine Abfrage mehr
      ob Mail versendet werden soll oder nicht. Es wird keine Mail versendet,
      aber der Rollenantrag ins System eingestellt.

---

## Funktionsarten

Funktionsarten
Die Funktionen in Referenz-ERP
werden anhand ihrer Controlstrings in folgende Funktionsarten klassifiziert:
Auflistung der Funktionsarten:
Funktionsarten
Ändern
Zusätzlich Ändern (R)
Ansehen
Zusätzlich Ansehen (R)
Löschen
Neu
Bereich/Profile
Anwendung
Liste
Crystal Report
Makro
VBA
Dialog
Hilfeaufruf
Systemaufrufe
Menü-Überschrift
Menü-Aufruf
Drucker
Archiv anzeigen
Ändern (R)
Ansehen (R)
Ausgeben (R)
Webportal
Ändern, Löschen oder Neu
Umfasst „Ändern“, „Ändern (R)“,
      „Löschen“ und „Neu“
Sicht
Umfasst „Ansehen“, „Liste“, „Crystal
      Report“, „Archiv anzeigen“, „Ansehen (R)“, „Ausgeben (R)“ und
      „Webportal“
Script
Umfasst „VBA“ und
      „Makro“
Alle
Alle
      Funktionsarten

---

## Dieses Hauptmenü

Dieses Hauptmenü
Eine spezialisierte Anwendung des Rollenkontextes ist
„Dieses Hauptmenü“.
Man erreicht diese Anwendung, wenn man im Hauptmenü
mit der Maus auf einen Menü-Punkt der rechten Seite zeigt (der Menü-Punkt wird
dabei hervorgehoben und der Mauszeiger ändert sich in ein Finger/Hand-Symbol).
Nun Maus nicht mehr bewegen und die Tastenkombination SHIFT+F2 ausführen.
Dann öffnet sich für diesen Menü-Punkt die Anwendung
„Dieses Hauptmenü“ und man sieht optionale „Zwischenfunktionen“ auf den Weg
durchs Menü zu der eigentlichen Funktion hin (die Funktion selber lokalisiert am
leichtesten über die „Beschriftung“). Ruft die Funktion eine Anwendung, Variante
oder einen Dialog auf, so wird auch gleich der zugehörige Rollenkontextes des
verwendeten Kontextes aufgelistet.
Selektiert man keinen Menüpunkt der rechten Seite im
Hauptmenü und betätigt SHIFT+F2 dann gelangt man in „Dieses Menü“ für die linke
hauptmenü-Seite (das sogenannte „MENU_2“)

---

## Dieses Menü

Dieses Menü
Eine spezialisierte Anwendung des Rollenkontextes ist
„Dieses Menü“.
Über die in jedem Kontext zugängige Funktion „Dieses
Menü“ wird der Rollenkontext der Umgebung aufgerufen.
Der Rollenkontext der aufrufenden Umgebung ist
farblich abgehoben und ist sortiermäßig am Anfang eingereiht. Optionale
System-Kontexte folgen danach.

---

## Stapelzuordnung aus Optionbox

Stapelzuordnung aus Optionbox
Felder
Die
      Funktionen aus der Ziel-Optionbox
Die
      Optionbox in der die „neuen“ Funktionen sind, die die „alten“ Rechte
      übernehmen sollen
erben die rechte aus der
      Quell-Optionbox
Die
      Optionbox die die Rechte zum Mapping zur Verfügung stellt
Gridanzeige
Listet die in Frage kommenden
      Funktionen an.
Das
      sind genau diejenigen nicht-privaten Funktionen aus der Ziel-Optionbox,
      die es auch in der Quell-Optionbox gibt
und
für die es keinen
      Eintrag in Rollenkontextmapping gibt.
Funktionen
Rollenmapping durchführen …
      (
F10
)
Erzeugt für jeden Eintrag aus dem
      Grid einen Standard-Eintrag im Rollenkontextmapping.

---

## Funktion Ändern

Funktion Ändern
Mit dieser Funktion können die Importierten Daten,
bevor eine Lieferung erzeugt wird noch einmal korrigiert werden. Die Maske hat
vier Registerkarten
Registerkarte Allgemein
Auf dieser Registerkarte die Allgemeinen Einstellung
vorgenommen oder abgeändert werden.
Registerkarte Waage
Auf dieser Registerkarte befinden sich spezifische
Felder von der Waage
Registerkarte Analysewerte
Hier können die Analysewerte eine Anlieferung
eingetragen werden. Die Einrichtung der Analysewerte finden Sie
hier
.
Registerkarte Ergänzungswerte
Hier können die Ergänzungswerte der Anlieferung in
Abhängigkeit zur Sorte eingetragen werden. Wird die Sorte geändert so ändern
sich auch die zu erfassenden Ergänzungswerte. Die Einrichtung der Ergänzungswert
finden Sie
hier
.

---

## Saatzucht

Saatzucht

---

## Scanner Daten bearbeiten

Scanner Daten bearbeiten
In dieser Variante werden alle erfassten Positionen zu
einem Scanvorgang angezeigt. Wird im Feld ein D ein * angezeigt wird, so wird
diese Position beim nächsten Scann mit dem dazugehörigen Scanner gelöscht.

---

## Vorgangsprotokoll

Vorgangsprotokoll
In dieser Variante werden mit protokollierte Daten von
Scanvorgängen angezeigt. Dazu muss der Schalter
Vorgangsprotokoll
auf Ja gestellt
werden.

---

## Scanner Detailübersicht

Scanner Detailübersicht
In dieser Variante werden alle erfassten Positionen zu
einem Scanner angezeigt. Die Spalte D zeigt an welche Informationen angezeigt
werden.
Status D Feld
Bedeutung des D Feldes
Leer
Hat
      die Zeile keine Markierung, so ist diese noch aktiv
*
Ist
      eine Zeile mit einem * markiert, so wird diese beim nächsten Scanvorgang
      mit dem Scanner gelöscht.
M
Ist
      die Zeile mit einem M markiert, so werden Informationen zu einer
      Produktionsmaschinen angezeigt, welche gerade mit diesem Scanner
      bearbeitet wird.
Spalte
Beduetung
Artikel
Artikelnummer
G.
Maschinennummer
Wert
Status der
            Maschine
1.   Maschinen befindet sich im
            ersten Lauf
2.   Maschine befindet sich im
            zweiten Lauf
DatenstromIdent
Mischstatus der Maschine
0 Reinigen, Trocknen
1 Mischen
Scanident
Zeigt an auf
            den dementsprechenden Scandatensatz
AI
Belegnummer des Produktionsbeleges welcher
            abgearbeitet wird
I
Is
[...]


---

## Senden-An-Vorlagen

Senden-An-Vorlagen
Mit Hilfe der Senden-An-Vorlagen lassen sich die
Felder Empfänger, Betreff und Kurztext mit einer Vorlage füllen.
Eine neue
Vorlage kann angelegt werden.
Eine Auswahl
der gespeicherten Vorlagen. Dies ist auch über die Taste F3 im Feld „Betreff“
möglich.
Vorlagen lassen sich über die Variante
„E-Mail-Vorlagen“ unter [FA] neu anlegen/löschen/ändern.

---

## Schritt für Schritt

Schritt für Schritt

---

## Sicherheitsabfragen

Sicherheitsabfragen
Alle Eingaben in das Referenz-ERP-System werden automatisch
auf Korrektheit geprüft bzw. es wird abgefragt, ob die Erfassung so korrekt war.
Wird eine Anwendung mit ESCAPE verlassen, wird unter anderem geprüft, ob die
Daten bereits gespeichert wurden. Ist dies nicht der Fall wird noch abgefragt,
ob gespeichert werden soll. Es erscheint dann folgender Dialog:
Bei
Ja
werden die Daten gespeichert und die
Anwendung verlassen.
Bei
Nein
wird die Anwendung ohne Speichern
verlassen.
Bei
Abbruch
wird in die Erfassung
zurückgesprungen
,
damit ggf. Werte korrigiert werden können.
Es können jedoch auch Abfragen in anderer Form
erscheinen. Z.B. werden auch Test vor Auswertungen vorgenommen, ob Daten bereits
so in korrekter Form vorliegen. Beispiel:
Bei
OK
wird die Liste gedruckt, bei
Abbruch
wird der Vorgang beendet.
Diese und ähnliche Abfragen kommen an allen Stellen in
Referenz-ERP vor. Aus diesen Dialogen herraus sind keine Direktsprünge
möglich.

---

## Source-Template

Source-Template
Folgend die Felder des Tabreiters Source-Template
Felder
Modul Name
Der
      Modulname wird der Prozedur vorweggestellt um eine Eindeutigkeit zu
      bekommen.
Grid
      Name
Der
      Grid Name der im Panter verwendet wird.
JPP
      Handle
Der
      Handle-Name, der von JPP verwendet werden soll
System Handle
Handle-Name der beim SYSTEM SQL für
      die Felder verwendet wird
User
      Handle
Handle-Name der beim User SQL für
      die Felder verwendet wird, um nicht mit dem SYSTEM SQL denselben Feldnamen
      zu verwenden.
Entrys anlegen
Diese CheckBox legt in dem Source
      Template für jede Spalte eine Methode an, die beim Betreten durchgeführt
      wird.
Exits anlegen
Diese CheckBox legt in dem Source
      Template für jede Spalte eine Methode an, die beim Verlassen der Spalte
      ausgeführt wird.
Valids anlegen
Checks anlegen
Row
      Entry
Diese Methode wird beim Betreten
      einer Zeile ausgeführt.
Row
      Exit
Diese Methode wir
[...]


---

## Status der Scanner

Status der Scanner
In dieser Variante werden die aktuellen Werte, Statien
des Scanners angezeigt
.

---

## Objektverwaltungswesen

Objektverwaltungswesen

---

## Bestände und Bewertung

Bestände und Bewertung

---

## Hilfsprozeduren

Hilfsprozeduren

---

## Kontenblatt

Kontenblatt

---

## Kasse / Daten aus Strichcode

Kasse / Daten aus
Strichcode

---

## Optionen Finanzwesen

Optionen Finanzwesen

---

## Optionen global

Optionen global

---

## Optionen Warenwirtschaft

Optionen Warenwirtschaft

---

## Partiewesen

Partiewesen

---

## Scanner

Scanner

---

## Trennkriterien Umwandlung

Trennkriterien Umwandlung

---

## Vorbelegungen ME / Gebinde

Vorbelegungen ME / Gebinde

---

## Vorgangsbearbeitung allg.

Vorgangsbearbeitung allg.

---

## Vorgangsbearbeitung Positionen

Vorgangsbearbeitung Positionen

---

## Vorgangsbearbeitung Umwandlung

Vorgangsbearbeitung Umwandlung

---

## Vorgangsbearbeitung Spezialitäten

Vorgangsbearbeitung Spezialitäten

---

## Vorgangsbearbeitung Warenposition

Vorgangsbearbeitung Warenposition

---

## allgemeine Programmsteuerung

allgemeine Programmsteuerung

---

## WebPortal

WebPortal

---

## Reklamationen

Reklamati
onen
Direktsprung
[REKLAM]
Um die Erstellung von Reklamationen zu vereinfachen,
bietet Referenz-ERP das Reklamationsmodul an.

---

## Stornobelege

Stornobelege
Bereits weiter verarbeitete Belege (und ggf. gedruckte
Belege) können mit der Funktion
Stornobeleg
ausgebucht
werden. Es wird ein Stornobeleg mit der Belegnummer des Originalbeleges
erstellt. Stornobelege sind Belege einer Stornovorgangsklasse. Wie für die
Vorgangsklassen/-unterklassen der Originalbelege müssen auch für die
entsprechenden Stornovorgangsklassen/-unterklassen die notwendigen Einrichtungen
vorgenommen werden (Nummernkreiszuordnungen, Formularzuordnungen etc.).
Stornobelege werden anschließend wie Originalbelege an die Finanzbuchhaltung
übergeben.
Es gibt zwei zusätzliche Parameter für die
Stornobelegerstellung:
1.
Kopie erstellen
– Wird eine Stornorechnung mit dieser Einstellung
erstellt, so muss die Rechnung nicht erneut erfasst werden. Es wird eine
bearbeitbare Kopie des stornierten Beleges erzeugt.
Die Standardeinstellung ist
Nein
2.
Stornobeleg erstellen
- Diese Bedingung kennt 3 Fälle:
a.
Immer
– Es wird in jedem Fall ein Stornobeleg erstellt.
[...]


---

## System-Grid Eigenschaften

System-Grid Eigenschaften
In den System-Grid-Eigenschaften werden Eigenschaften
der Griddefinition vom Entwickler vorgegeben, die vom Anwender nicht änderbar
sind:
System
      Eigenschaftsfelder
fld_scroll aktivieren
Fügt
      eine neue Zeile ein, wenn man am Ende der letzten Zeile ist und Enter
      drückt.
Gridpositionen merken
Bei
      Aktivieren dieser CheckBox merkt sich das Grid die Positionen seiner
      Felder und deren Größen.
Summen zulässig
Bei
      Aktivierung dieser CheckBox lässt man die Möglichkeit zu, dass man über
      bestimmten Spalten eine Summenbildung laufen lassen kann.
Einfügen Zeilen erlauben
Einfügen einer Zeile wird mit
Strg
+
Umschalten
+
Einfg
ausgelöst. Die Speicherung der
      Daten in die Datenbank erfolgt jedoch nicht automatisch. Es ist eine
      manuelle Speicherung notwendig
Löschen Zeilen erlauben
Lässt das Zeilen Löschen mit
Strg
+
Umschalten
+
Entf
zu. Die Daten werden jedoch nur
      im Grid gelöscht. Eine Löschung in der Da
[...]


---

## Systeminformationen

Systeminformationen
Hauptmenü
Systempflege
Update
Systeminformationen
oder Direktsprung
[SYSIN]
oder das Fragezeichen (?) in der oberen Leiste
anklicken und dann Systeminformationen auswählen
Hier findet man alle notwendigen Informationen zum
System z.B. wer mit der Datenbank verbunden ist, welche Lizenz und welche
Versionen verwendet werden, die Größe der Datenbank und vieles weiteres.
Kopfdaten
Feldname
Beschreibung
Kunden-Bezeichnung
Name
      des Kunden / Mandanten.
Entspricht dem Feld Name aus dem
Mandantenstamm
(Direktsprung
[MND]
)
Bediener
Hier
      werden das Kürzel und der Name des aktuellen Bedieners
      angezeigt.
Entspricht den Feldern Kurzname und
      Bedienername aus dem
Bedienerstamm
(Direktsprung
[BD]
)
Mandant
Hier
      sieht man welcher Mandant ausgewählt wurde
Entspricht dem Feld Kurztext aus dem
Mandantenstamm
(Direktsprung
[MND]
)
Register
Allgemein
Felder
Beschreibung
Datenbankserver
Hier
      wird angezeigt welche Datenbank auf welchem Rechner v
[...]


---

## Serverinfo

Serverinfo
Hier erhält man eine Übersicht mit Informationen zum
Server.
Felder
Beschreibung
Property
Name
      der Property
Wert
Wert
      der Property
Beschreibung
Beschreibung der
      Property

---

## System-Spalten

System-Spalten
Hier werden die vom Entwickler vorgegebenen
Spaltenbeschreibungen angezeigt. Der Anwender hat keine Möglichkeit, diese
Definitionen zu ändern.
Zu den Inhalten der Tabelle und der Änderung im
Kapitel Spaltenbeschreibung.

---

## Tastenfunktionen

Tastenfunktionen
Ansehen
Zum Ansehen der Definition drücken Sie nach der
Auswahl einer Zeile
F6
.
Ändern
Zum Ändern der Definition drücken nach der Auswahl
einer Zeile die Taste
F5
.

---

## Ehemalige AddIns Übersicht

Ehemalige AddIns Übersicht

---

## Technisches zum Formulararchiv

Technisches zum
Formulararchiv

---

## Teilwert-AfA

Teilwert-AfA
Voraussetzung für die Inanspruchnahme der
Teilwertabschreibung ist, dass die Wertminderung von Dauer und nicht nur
vorübergehend ist. Die Teilwertabschreibung kann dann vorgenommen werden, wenn
der Teilwert niedriger ist als der auf Grund der planmäßig vorgenommenen
Abschreibung sich ergebende Restbuchwert. Bei Vornahme einer Teilwert-AfA ist
sowohl der Restwert der Anlage als auch die Restnutzungsdauer neu zu
schätzen.
Teilwert-AfA wird in der Anlagenbuchhaltung in der
Historie über die Art
Teilwert-AfA
erfasst. Es wird dabei automatisch ein
Beleg in die Primanota der Finanzbuchhaltung gestellt. Dazu werden beim
Speichern des Anlagegutes noch ein paar Werte abgefragt:
Bei Erfassung der Teilwert-AfA kann man zusätzlich
eine neue Lebensdauer – Achtung:
Nicht
die neue Restnutzungsdauer –
erfassen. In dem folgenden Beispiel wurde ein Anlagegut mit einer Nutzungsdauer
von 8 Jahren für 10.000,00 Euro angeschafft. Nach 2 Jahren wurde eine
Teilwert-AfA durchgeführt.
[...]


---

## Auswahlliste

Auswahlliste
Nach dem erfolgreichen Import der Eingangsbeleg in das
Referenz-ERP System werden diese in der Anwendung Terres Belegimport angezeigt. In der
Auswahlliste können folgende Felder farblich nach dem Import dargestellt sein.
Die Zusammenfassung eines Beleges wird in einer gelb Markierten Zeile
dargestellt.
Rechnung
Farbe
Bedeutung
Rot
In dem Beleg kommen unterschiedliche
      Lagerort vor
Weiß
Der Beleg enthält nur ein
      Lagerort.
Aeins-Art.
Farbe
Bedeutung
Rot
Der Artikel ist Referenz-ERP Pool nicht
      vorhanden
Gelb
Der Artikel ist nicht auf dem Referenz-ERP
      Lager vorhanden.
Weiß
1.   Der Artikel ist auf
      dem Lager vorhanden.
2.   Der Terres Artikel
      ist nicht im Referenz-ERP Artikelpool(Gruppenartikel) vorhanden wurde aber in
      diverse Referenz-ERP Artikel aufgeteilt.
3.   Der Artikel ist im
      Referenz-ERP Artikelpool oder nicht vorhanden wurde aber einem andern Artikel
      zugeordnet.
Referenz-ERP
Lager
Farbe
Bedeutung
Rot
Es existiert keine Zuordnung eines
      La
[...]


---

## Datendrehscheibe Statistik Export

Datendrehscheibe Statistik Export
Hauptmenü
Externe Kommunikation
Datendrehscheibe
Statistikexport [
TERRS
]
In dieser Anwendung kann die Statistik für die
einzelnen Perioden an Terres übermittelt werden.
Dazu wird in der Variante „Terresstatistik Export“ der
Statisikexport
[
F9
] aufgerufen. Die Statistik wird als csv
exportiert. Der Name der Datei enthält die Periode und das Jahr z.B.
TerresStatistikExport_2012_12.csv.
Bevor die Statistik übermittelt werden kann, müssen
auf der Registerkarte Optionen folgende Einstellungen vorgenommen werden.
Registerkarte
Statistikexport
Wenn die Statistik manuell exportiert werden soll, so
kann in das Feld manuell das Jahr und die Periode eingetragen werden. Es ist
möglich eine Statistik für eine Periode mehrfach zu übertragen.
In der unteren Tabelle wird angezeigt welche Statistik
für welche Periode schon übermittelt worden ist.
Registerkarte Optionen
In dem Feld „Statistik Export“ die Prozedur angegeben,
die die Statistik erstellt. Diese
[...]


---

## Textbaustein (Shift + F8)

Textbaustein (Shift + F8)
Öffnet eine F3-Auswahl zum Auswählen eines
Textbausteins(
Vorgangstext
).

---

## Umsatzsteuer-Identifikationsnummern

Umsatzsteuer-Identifikationsnummern
Eine Umsatzsteuer-Identifikationsnummer (abgekürzt
USt-IdNr) dient zur Kennzeichnung von Umsatzsteuerpflichtigen. Sie besteht aus
einem Länderkürzel, bestehend aus zwei Großbuchstaben, gefolgt von höchstens 12
weiteren alphanumerischen Zeichen.
Für jeden Umsatzsteuerpflichtigen kann es pro Land nur
eine USt-IdNr geben.
In der Maske lassen sich folgende Werte eintragen
Informationen
USt-IdNr
In
      dieser Spalte können alle Umsatzsteuer-Identifikationsnummern des Kunden
      eingetragen werden, wobei jede USt-IdNr nur einmal eingetragen werden
      kann.
Bemerkung
Eine
      Bemerkung zu der USt-IdNr, dieser Eintrag ist optional.
Staatnummer
Die
      Nummer des Staates, zu der diese USt-IdNr gehört. Dieser Eintrag ist
      notwendig.
Die
      Staatnummer der Haupt-USt-IdNr muss der Staatnummer der Hauptanschrift des
      Mandanten / des Kunden entsprechen. Diese Anschrift muss also erst
      eingerichtet werden, bevor die Haupt-U
[...]


---

## Untersuchungsetiketten-Druck

Unter
suchungsetiketten-Druck
Hauptmenü
Saatzucht
Saatenlabor
Labordaten
Funktion
Drucke
Untersuchungsetiketten
oder Direktsprung
[LABOR]
Funktion
Drucke Untersuchungsetiketten
Auf dieser Maske können die Untersuchungsetiketten
gedruckt werden, die zu den
Laborverfahren
definiert wurden.
Folgende Funktionalitäten stehen zur Verfügung.
1.
Mit einem Doppelklick auf Nachdrucken werden alle Etiketten des jeweiligen
Verfahrens ausgedruckt. Der Schalter Nachdrucken wird dabei nicht
ausgewertet.
2.
Mit einem Doppelklick auf die Felder Verfahren oder Verfahren Kurzbezeichnung
öffnet sich die Verfahrensmaske mit dem jeweiligen Verfahren.
3.
Mit der Funktion „Alle Drucken“ werden alle Etiketten der jeweiligen Verfahren
ausgedruckt. Der Schalter Nachdrucken wird nicht berücksichtigt.
4.
Mit der Funktion „Auswahl Drucken“ werden nur die Etiketten des jeweiligen
Verfahrens ausgedruckt, bei denen der Schalter Nachdrucken auf „Ja“ steht.
Ist das Feld Druckanzahl gelb markiert, so i
[...]


---

## Verbotslisten

Verbotslisten
Verschiedene Staaten haben Embargos oder
Handelsbeschränkungen gegen einzelne Personen, Organisationen oder gar gegen
Länder erlassen. Die Nicht-Einhaltung der Sanktionen kann empfindliche Strafen
u.a. zum Ausschluss vom Handelsverkehr mit einem Land oder einer
Staatengemeinschaft führen.
Deshalb sollten Sie Ihre Geschäftspartner regelmäßig
gegen diese Listen prüfen.
Es gibt zwei wesentliche Listen, die geprüft werden.
Die eine ist die der EU und die andere die der USA.
Zum
Compliance Modul

---

## Vorgangsimport Anwendung

Vorgangsimport Anwendung
Folgende Standard Varianten stehen zur
Auswahl
1.
Vorgangsimport
2.
Importierte Positionen bearbeiten
3.
Vorgangsimportstatistik
Varianten
„Vorgangsimport“ und „Importierte Positionen bearbeiten“
Da sich die beiden Varianten „Vorgangsimport“ und
„Importierte Positionen bearbeiten“ sich nicht wesentlich unterscheiden werden
diese beiden Varianten unter diesem Punkt beschrieben.
Der Unterschied zwischen der Variante „Vorgansimport“
und „Importiert Vorgänge bearbeiten“ liegt im wesentliche darin, dass bestimmte
Felder in der Auswahlliste farblich markiert werden, wenn diese zu einem nicht
erfolgreichem Anlegen des Vorgangs führen würden. Des Weiteren besteht die
Möglichkeit in dieser Variante einzelne Position zu Bearbeiten.
Automatik
In der
Automatikschnittstelle
könne automatisierte Importprozesse realisiert werden, wie z.B. nächtliche
Übernahmen von Tankbelegen oder automatisierte Übernahmen von EDI
Ordersätzen.
Auswahlliste
In der Auswahllis
[...]


---

## Volumen

Volumen
Bei Großen zu erwartendem Datenaufkommen können Sie
die Menge der Dateien (Belege und Steuerdateien) aufteilen.
Sie finden dann nach dem Export im Export-Verzeichnis
Unterordner 1, 2, 3, … und
dessen
Inhalt überschreitet nicht die in der
Volumenaufteilung vorgegebene Maximalgröße.
Die AMICAR-Dateien sind dabei gepflegt. Eine Arbeit,
die bei vielen Dateien unmöglich bis nicht rentabel erscheint.
Wenn Belege größer seien sollten, das die vorgegebene
Maximalgröße, dann greift das Verfahren nicht. Diese Belege müssten Sie dann per
Hand anpassen.

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
      ‚Schnelle Teildispositi
[...]


---

## Vorgangs-Druck

Vorgangs-Druck
Beim Vorgangsdruck wird zwischen ASCII- und
Windowsdruck unterschieden.
ASCII-Druck wendet sich vornehmlich an Nadeldrucker
und besticht durch geringe Datenmengen, die zur Aufbereitung notwendig sind.
Entscheidend ist der Drucker, auf den gedruckt wird.
Beachten Sie hier die Einstellung unter „Windows
Druck“. Damit ist der obige Drucker als Windows-Drucker ausgewiesen und kann
sich der Möglichkeiten des Formulararchivs bedienen.
Im Formulararchiv-Manager können Sie bestimmen, wie
der Druck im Falle eines Windows-Druckers ins Archiv gelangen soll.
Es gibt dabei grundsätzlich 2 Ausprägungen: Entweder
als „ASCII-Druck“ oder im aufwändigeren Binärformat, welches dann aber
pixelgenau jedes Detail erfasst. Von letzterem sind 2 Varianten verfügbar,
nämlich die gängigen Zielformate PDF und TIFF. Hat man die Wahl zwischen den
Beiden, so ist Referenz-ERP-seitig PDF vorzuziehen, da es im Falle von Farbbeigaben
der Originale effizienter ist und bei Verwendung von TIFF diesbezügl
[...]


---

## Allgemein

Allgemein
Im der folgenden Beschreibung werden die Synonyme
•
GFV
für „Grid führende Vorgänge“

(Grid 1)
•
GMV
für „Grid mengenabhängige Vorgänge“  (Grid
2)
•
GWV
für „Grid weitere abhängige Vorgänge“
(Grid 3)
verwendet
Die Erfassungsmaske gliedert sich in zwei
Bereiche.
Kopfbereich
Datentabellen
Highlights
•
Spaltenposition und –breite individuell per Maus einstellbar.
•
Vorbelegung div. Spalten über die Profileinstellungen
•
Ein- oder ausblenden div. Spalten über die Profileinstellungen
•
Maskengröße und Zeilenanzahl der Grids einstellbar
•
Nachkommastellen einstellbar
•
Umfangreiche Funktionalität aus der Maske heraus z.B. durch Doppelklick
auf div. Spalten oder dem (teilweise Vorgangs oder Feld gebunden)
Kontextmenüeinträgen
•
Farbliche Markierung der zusammengehörigen Vorgänge (wird z.B. ein
Vorgang im GFV angeklickt wird dieser rot markiert, seine zugehörigen Vorgänge
im GMV werden aut. blau markiert)
•
Individuelle Auswertungen lassen sich einrichten
•
et
[...]


---

## Reporte

Reporte
Im System lassen sich „Crystal Report“ und Branchen-ERP
Etikettendruck einbinden. Diese können über das
Profile aktiviert
werden. Die Reporte
lassen sich dann über das Kontextmenü aufrufen.
Für die eingebundenen Reporte gibt es auf der Maske
verschiedene Buttons.
Die Vorschau (Button Symbol Lupe) zeigt den Inhalt des
jeweiligen Reports an.
Die
Bearbeitung der Streckentexte
für den
jeweiligen Report erfolgt über den Button mit dem Symbol Stift.
Drucken der Reports / Archiv Mail Versand erfolgt über
den Button mit dem Drucker

---

## Anwendung: Vorgangstexte

Anwendung: Vorgangstexte
Auswahlliste der Vorgangstexte:
Feld
Beschreibung
Textklasse
Wo
      soll der Text eingesetzt werden
Textnummer
ID
      in der Textklasse
Bezeichnung
Bezeichnung des
      Vorgangstextes
MaxStufe
Zu
      welchem Zeitpunkt in der Vorgangsverabeitung soll der Vorgangstext
      übernommen werden
Vorgangsklasse
Für
      welche Vorgangsklasse soll der Text anwendbar sein
Suchmöglichkeiten der Vorgangstexte:
Feld
Beschreibung
Textklasse
Von…
      bis…
Textnummer
Von…
      bis…
Funktionen der Vorganstexte:
Funktion
Beschreibung
Ändern (F5), Ansehen (F6), Löschen
      (F7), Neu (F8)
Öffnet den Pfleger der
      Vorgangstexte

---

## Schritt für Schritt

Schritt für Schritt
Textbausteine im Vorgang:
Schritt 1: Textbaustein anlegen
Direktsprung [TBS] -> Neu (F8) -> Feld:
Vorgangstextklasse -> F3-Auswahl -> „Textbaustein“ -> Feld:
Vorgangstextnummer -> neue ID, welche noch nicht vergeben ist eintragen->
Text-Zuordnung (F10) -> hier kann nun der gewünschte Text eingetragen werden
-> Speichern (F9) -> Speichern (F9)
Schritt 2: Textbaustein im Vorgang hinzufügen
[REE] -> Feld: Kunde -> F3-Auswahl -> Kunde
auswählen -> Positionen (F5) -> Textbaustein hinzufügen (Shift + F8) ->
in der F3 Auswahl den in Schritt 1 erstellten Textbaustein auswählen ->
Verlassen (ESC) -> Abschluss
Schritt 3: Vorgang drucken
[REB] -> erstellten Vorgang suchen ->
Formulardruck (F10) oder Vorschau (F11)

---

## Vorgangsimport

Vorgangsimport
Vorgänge können auf verschiedenen Wegen erstellt
werden:

---

## Vorgangsimport Kontrollmakros

Vorgangsimport Kontrollmakros
Während des laufenden Vorgangsimports können an
verschiedenen Stellen Kontrollmakros angeschlossen werden, die einen Eingriff in
den laufenden Import ermöglichen.
Dazu kann ein Vorgangsimportkontrollmakro als Makro
2.0
[CSM]
oder als Pascal Makro
erstellt werden.
In der Vorgangsunterklassendefinition der zu
importierenden Vorgangs(unter)klasse kann nun dieses Makro als „Vorgangsimport
Kontrollmakro“ eingetragen werden.
Es gibt folgende Einsprungpunkte im C# Makro:
Vorgangs-Methoden:
vimp_Vorgang_vor_Neu
Wird vor der Erstellung eines neuen Vorgangs
aufgerufen. Als Parameter wird hier nur die IVS_GUID aus der Tabelle
ImportVorgStamm gegeben.
vimp_Vorgang_vor_Speichern
Wird direkt vor dem Speichern des Vorgangs aufgerufen.
Als Parameter wird die ivs_guid aus der Tabelle Importvorgstamm und das Handle
des instanziierten Vorgangs gegeben.
Zusätzlich wird angegeben, ob es sich um eine
Neuanlage oder eine Änderung handelt.
vimp_Vorgang_nach_Speichern
W
[...]


---

## Feldreihenfolge festlegen

Feldreihenfolge festlegen
Diese Funktion ist ab der Version 8.1.2.682 obsolet.
Die Feldreihenfolge wird jetzt mit der Shift-F3 Mechanik gesteuert. Wurde für
die Maskensteuerung ein Profil erstellt, so wird das erste gefunden Profil in
die Shift-F3 Mechanik übernommen.
Über
CF3
kann die Feldreihenfolge auf der Waagenmaske für die Bediener festgelegt werden.
Das ist die Reihenfolge, die der Cursor auf der Maske wählt, damit man die
wichtigen Eingaben möglichst zügig machen kann.
Um diese Funktion in der
OptionBox anwählen zu können, muss man die Maske im Neufall geöffnet
haben.
Es erscheint eine Meldung, dass man die Felder mit Doppelklick in
der gewünschten Reihenfolge anwählen möchte und eine Abfrage, für wen diese
Reihenfolge gespeichert werden soll.
Ja = für alle Bediener
Nein = für
aktuellen Bediener
Abbrechen = bricht die Funktion
Feldreihenfolge festlegen
ab
Danach
wählt man die Felder in der gewünschten Reihenfolge an. In doppelgeklickte
Felder wird eine laufende Numm
[...]


---

## Terminal ändern

Terminal ändern
Mit dieser Funktion kann das Terminal geändert werden,
wenn das Feld deaktiviert ist.

---

## Vorlage ändern

Vorlage ändern
Mit dieser Funktion kann der Prozess geändert werden,
wenn das Feld gegen Eingabe gesperrt worden ist.

---

## Registerkarte Ergebnis

Registerkarte Ergebnis
Ergebnis
Regulärer Ausdruck
Siehe
Regulärer
      Ausdruck
G
Siehe
G
Rückgabe als
Siehe
Rückgabe
      als
NBV
Siehe
NBV/NBZ
NBZ
Siehe
NBV/NBZ
Zuordnung
Siehe
Zuordnung
Pos
Hier
      kann man einfach die Reihenfolge festlegen, in der die regulären Ausdrücke
      abgearbeitet werden sollen
Beispiel
siehe
Beispiel
…
Wiegung
Mit
      F11 können Sie eine Testwiegung durchführen
Übernahme von Terminal
Hier
      können Einstellungen von anderen Terminals  via F3-Auswahl übernommen
      werden.
Beispiel
Der eigentliche Arbeitsbereich, in dem man sich an
Hand eines Wiegebeispiels, also einer möglichen Rückgabe einer GA, an die
Interpretation bzw. Zuordnung der Daten heranmachen kann. Die Beispieldaten
gewinnt man durch Dokumentation, einer Wiegung(!) oder …
Obiger Inhalt möge vorerst als „Beispiel“ dienen. Man
erkennt bei näherem Hinsehen Datenfragmente für Gewichtsdaten, einer IP. Geübte
Waagenprofil-Hersteller erkennen auch noch eine Datumsangabe. Nun
[...]


---

## Variante Aktive Arbeitsprofile

Variante Aktive Arbeitsprofile
In dieser Variante werden alle Aktiven Arbeitsprofile
angezeigt.

---

## Ware abstimmen

Ware abstimmen
Hauptmenü
Systempflege
Ware abstimmen
oder Direktsprung
[WABST]
Zum Einlesen der Werte wird die Funktion
Periodenwerte einlesen
gewählt. Je nach
Datenvolumen und Rechnerleistung kann dieser Vorgang einige Zeit in Anspruch
nehmen. Danach werden zeilenweise die Ergebnisse nach gewählter Einstellung
dargestellt.
Sollten Differenzen auftreten, stehen unter
Konsistenz prüfen
Analysefunktionen
zur Verfügung, mit
denen die Ursache gefunden werden kann.
Funktionsknöpfe
Beschriftung
Funktion
Belegtyp wechseln
Wechsel der
      Datenbereiche:
Die
      Spaltenwerte werden je Einstellung mit den unterschiedlichen
      Datenbereichen gefüllt. Es ist also eine Vergleichsmöglichkeit je
      erwarteter Fragestellung möglich.
+
/
-
Blättern Jahre und
      Perioden:
Es
      kann hiermit zwischen den jeweiligen Zeiträumen gewechselt
      werden.
Einzelsumme
/
kumulierte Summe
Einzelsumme stellt den Wert der oben
      angezeigten Periode, kumulierte Summe den Wert bis ein
[...]


---

## Neues Kennzeichen in der Warenbewegung

Neues Kennzeichen in der Warenbewegung
Es wurde ein neues Kennzeichen in der Warenbewegung
WabewKtrBuchkorr
angelegt. Dieses Kennzeichen wird im Moment nur in
Vorgängen gesetzt die beim Washout oder Circle Geschäft erstellt werden. Dies
bedeutet, es werden keine Vorgänge mehr  mit Menge > 0  und Wert =
0 zum ausbuchen der Mengen erstellt. Es werden jetzt Vorgänge mit Wertartikel
angelegt. Das Kennzeichen wird dabei auf 1 gesetzt ist. Damit können Vorgänge
mit einem Wertartikel in den Kontraktbewegungen angezeigt werden.
Private Auswertung die die
ktrbewmenge
und
wabewsignimengen
berücksichtigen müssen abgeändert werden. Damit die
privaten Auswertungen weiterhin ordnungsgemäß funktionieren.
Beispiel aus der Prozedur
amic_func_ktr_calc_all_ratierlich
sum
((
isnull
(kb.ktrbewmenge,0) -
isnull
(kb.ktrbewdispmenge,0)) * wb.wabewVorzeichen *
if
isnull
(wb.WabewKtrBuchkorr,0) = 1
then
1
else
wb.wabewSigniMengen endif )

---

## Wichtige Funktionstasten

Wichtige Funktionstasten
Achtung:
In bestimmten Anwendungen (z.B. der
Vorgangserfassung) werden, um die Arbeit zu beschleunigen, die Funktionstasten
zum Aufruf von Fakturierfunktionen sehr intensiv genutzt. Sie besitzen in diesen
Fällen teilweise eine abweichende Bedeutung.
Folgende Funktionstasten werden in Referenz-ERP
eingesetzt:
Allgemeine
Bedienungsfunktionen
Taste
Beschreibung
ESC
Abbruch eines Vorganges
ALT
Umschalten zwischen
      Bildschirmarbeitsbereich und Menüzeile
F1
Aufruf der Online-Hilfe
F2
Mit
F2
lässt sich in der
      Auswahlliste die Bereichsauswahl aktivieren.
F3
Hier
      wird eine
Liste der
      Daten
, die für das Feld, in dem die Schreibmarke steht, möglich sind
      aufgerufen.
Eingabe / ENTER
Bestätigung einer Eingabe und
      springt in das nächste Feld.
Shift+F4
Ermöglicht die Direkteingabe eines
      Direktsprunges.
Shift+F2
Anzeige und Änderungsmöglichkeit für
      die dieser Maske zugrunde liegenden Erfassungsparameter (EPA, siehe dort)

[...]


---

## Winword / Rtf

Winword / Rtf
Produktpflege, Wartung, interne
Modernisierungen sowie Anpassungen an geltende Sicherheitsmaßnahmen machen es
notwendig, die bisherige interne Verarbeitung von Word-Dokumenten (.doc) auf die
Verwendung von RTF-Dokumenten (.rtf) zurückzuführen.
Da sich eine Umstellung während
des Programm-Updates verbietet (mögliche große Anzahl von Dokumenten (Zeit!),
Nacharbeitung von möglichen Problemen) verfährt das Programm so, dass eine
Konvertierung automatisch ("on the fly") dann durchgeführt wird, wenn die Daten
überhaupt benötigt werden ("on demand"). Auftretende Probleme werden per
Benutzeroberfläche und Systemprotokoll kundgetan, und sollten dann mit
Unterstützung dieser Anwendung zu beheben sein.
Da die Umstellung ein komplexer
Prozess ist, der in mehreren Stufen / Phasen durchgeführt wird, bedarf es einer
zentralen Verwaltungsstelle in der ggf. bestimmte Tätigkeiten durch- bzw.
nachgeführt werden können. Ohne so ein Werkzeug bliebe auf Systemen nur die
Verwendung
[...]


---

## Abgekündigte Programm Module

Abgekündigte Programm Module

---

## Abkürzungen

Abkürzungen
I2
smallint
I4
integer
N4
numeric(15,4)
TS
timestamp
Char(?)
character-string mit ? vielen Zeichen
D4
Datum
Feld ohne Erklärung bedeutet, dass es zurzeit nicht
benutzt / versorgt wird
Benutzte Relationen:
AcashBelg:
Diese Tabelle beinhaltet das Kassenbuch und ist eine Liste über alle
an der Kasse erfassten Vorgänge.
Schlüsselfelder:
BelegId
(I4)
bei Vorgängen handelt es sich um die V_Id, bei Finanzvorgängen
(Belegarten 10-20) um einen fortlaufend kleiner
werdenden negativen Integerwert.
BelegKs(I4)
Kassennummer, an der dieser Beleg erfasst wurde (entspricht Eintrag
in Kassenverwaltung)
FilialNummer(I4)
Nummer der Filiale, zu der der Beleg gehört (aus Mandantenstamm)
Weitere Felder:
BelegArt(I2)
die Belegart des Beleges (s.o.)
BelegBedNr(I4)
die Bedienernummer des Bedieners, der d
[...]


---

## Referenz-ERP.CE Scannersoftware

Referenz-ERP.CE Scannersoftware
Die Scannersoftware Referenz-ERP vor der Version 7.8.6..xxx
ist nicht an die Hardware gebunden und benötigt daher andere
Einstellungsmöglichkeiten
Die Referenz-ERP.CE Scannersoftware kann ab der
Version 7.8.6.xxx
nur auf CE Geräten von bestimmten Herstellern
installiert werden.
Folgende Scanner werden mit folgende Plattformen
unterstützt.
1.
Datalogic mit Windows CE
2.
Motorola Symbol mit Windows CE
3.
Intermec mit Windows Mobile 6.5
Installation der Software
Die Installation der Software ist an dieser Stelle
beschrieben
.
Starten der Software
Nach dem die Scannersoftware
Installiert
worden ist kann diese gestartet
werden. Beim ersten Start der Software müssen die Verbindungsdaten eingetragen
werden. Ab der Version 8.1.2.xxx werden die Verbindungsdaten Kundenspezifisch
mit der Software ausgeliefert. Dies bedeutet, dass nach der ersten Installation
die Verbindungsdaten nicht eingetragen werden müssen.
Ab Version
8.1.2.xxx
Erscheint beim Starten der Softwa
[...]


---

## Abstimmung des Kassensystems

Abstimmung des Kassensystems

---

## Abwicklung

Abwicklung
Prozess
Abwicklung
Feld
Beschreibung
Datenbereitstellung
Die
      Datenbereitstellung ist eine Prozedur, die aus der Datenbank jene Werte in
      die Tabelle “Datenstrom_ExternerProzess” lädt, die für die Anzeige im Baum
      wichtig sein können. Hierbei berücksichtigt die Prozedur die aktuelle
      connect-id und somit auch die vom Anwender in der Maske ausgewählten
      Einträge.
Datenprozedur
Die
      Datenprozedur gibt an, welche Prozedur den Quellbaum darstellt. (Hier:
      „SendeAuftragsDaten“) Diese Prozedur hat nur einen Parameter, nämlich die
      Connection-ID des rufenden Referenz-ERP-Programms mit Namen „connect_id“. Die
      Prozedur muss ein Feld mit dem Namen „ident“ in der Ergebnismenge
      beinhalten, das eindeutig den Datensatz beschreibt.
Beschreibungsstruktur
Die
      Beschreibungsstruktur beschreibt den Aufbau und die Darstellung der Daten
      im Programm.
Schriftgröße
Mit
      der Schriftgröße der Vorgangsklasse bestimmen Sie die
[...]


---

## Abwicklungsregister

Abwicklungsregister

---

## AddOn

AddOn
Auch für die Vorgangsbearbeitung können individuelle
Datenbankfelder geschaffen werden, die auch bei Umwandlungen mit übergeben
werden. Hier können die Felder mit Werten belegt werden.

---

## af_Status

af_Status
Dieses Format sollte gepflegt werden bevor die
Anwendung Lieferbeleg genutzt wird.
Hier legt man fest wie der Status der
Lieferbelegpositionen sein kann. Z.B. verloren
Für die Abgrenzung der Auswahlliste nach dem Status
mit Hilfe der Funktion Bereich/Profile F2 ist es notwendig das Feld
Kommentar,Schnipsel in diesen Format wie folgt zu pflegen:
AND (lbp.lbp_status = Nummer des Formatausdruckes der
aktuellen Zeile )
z.B. für die Nummer 1
AND (lbp.lbp_status = 1)

---

## Referenz-ERP - Nullsetzer

Referenz-ERP - Nullsetzer
Direktsprung
[NULL]
Dies ist eine Referenz-ERP-Funktion für Branchen-ERP-Support!!!
Wichtiger HINWEIS: Wer diese Dokumentation NICHT
versteht, der sollte diese Referenz-ERP-Funktion auf KEINEN FALL benutzen oder
ausführen!
Durch „Klicken“ auf die Kästchen vor den einzelnen
Nullsetz-Routinen werden diese aktiviert und durch erneutes „Klicken“
deaktiviert. Alternativ kann das „Klicken“ ersetzt werden durch Drücken der
Leertaste.
Einige Routinen können nur in Zusammenhang mit anderen
Routinen ausgeführt werden (in Klammern sind die Auswahlpunkte aufgeführt).
Sollten einige Routinen noch mit einem Stern (*)
gekennzeichnet sein, so befinden sich diese Routinen noch in der
Entwicklungsphase. Durchgeführte Löschungen/Aktualisierungen werden mittels
eines „ROLLBACK“ wieder rückgängig gemacht.
Ein Protokoll über den Ablauf wird in der Relation
NullsetzerProtokoll gespeichert. Das Protokoll wird in einer Auswahlliste
dargestellt die man über die Funktion ‚Protokoll ansehen F6‘ öffnen
[...]


---

## ADM Account Receivables Export aktiv (SPA 958)

ADM Account Recei
vables Export aktiv (SPA 958)
Einstellung
Bedeutung
0 –
      Nein
Die
      Exportfunktionalität ist deaktiviert.
1 –
      Ja
Die
      Exportfunktionalität ist aktiviert.

---

## Aeins.INI

Aeins.INI
Diese INI Datei des Windows Verzeichnisses steuert das
generelle Erscheinungsbild der Referenz-ERP Software. Farben, Schriftart etc., sowie
die Pfadangaben zu den weiteren zentralen Steuerdateien sind hier angegeben.
Die im Folgenden erklärten Einträge sind die
wichtigsten:
SMVARS
..\config\aeins.bin
Hiermit wird angezeigt, wo sich in Ihrem System die
Steuerdatei für alle fest vergebenen Funktionstasten und alle fest verdrahteten
Dateizuordnungen befinden
SMBASE
Diese Angabe zeigt auf des Referenz-ERP Verzeichnis
„selber“, zu beachten ist, dass dieser Eintrag nicht mit einem \ abgeschlossen
sein darf.
FrameTitel
In diesem Bereich kann angegeben werden, wie die
Anzeige im Kopfteil (Titelleiste) gestaltet sein soll und was hier angezeigt
werden soll.

---

## AH-Testbereich

AH-Testbereich
-500000
Checkout, Checkin-Test

---

## AIS – Referenz-ERP Informationssystem

AIS – Referenz-ERP Informationssystem
Bei AIS handelt es sich um ein intelligentes
Spezialisten-System, welches eine Weiterentwicklung basierend auf Addon und KUI
darstellt und diese Systeme ablöst. Es ist hier möglich vom Anwender individuell
zusammengestellte Informationen entweder auf eigenen Bildschirmseiten oder auf
Registern bestehender Erfassungsmasken darzustellen bzw. zu erfassen. Dabei ist
es möglich zu allen Stammdaten Zusatzinformationen zu erfassen bzw.
eigenständige Datenbanktabellen zu verwalten. Die zu bearbeitenden
Datenbanktabellen sind nicht wie die vorherigen Systeme auf einzelne
vordefinierte Tabellen – wie z.B. KundenstammAddon bzw. Artikelmaskedaten
beschränkt – sondern es kann auf (fast) beliebigen
privaten Tabellen
arbeiten. Es gilt als einzige
Einschränkung bei der Erfassung von eigenen Stammdateninformationen, dass es in
den Tabellen ein Feld vom Typen Integer geben muss, welches den Primärschlüssel
darstellt. Bei der Erfassung von Zusatzinformationen z
[...]


---

## AIS Anschluss Mitgliederverwaltung

AIS Anschluss Mitgliederverwaltung
Die Mitgliedsbearbeitung ist AIS-fähig; als Ident wird
die h.KundId$ benötigt.

---

## AIS-Wizard

AIS-Wizard
Um die Arbeit mit AIS zu erleichtern und schnell
Informationen auf dem Bildschirm darzustellen bzw. zu bestehenden AIS-Gruppen
Felder hinzuzufügen oder zu ändern, existiert ein Werkzeug, dass schnell alle
benötigten Daten abfragt. Um diesen Wizard zu erreichen, positioniert man die
Maus an die Stelle, an der man das neue Feld haben will. Wenn man dann mit
gedrückter Strg-Taste die rechte Maustaste drückt, erscheint folgende Maske.
Hinweis: Steht man mit der Maus auf einem bereits
existierenden AIS-Feld, so geht die bekannte
Einrichtungsmaske
auf und man kann
dort sämtliche Einstellungen vornehmen.
In dem Wizard werden nacheinander die benötigten Daten
angezeigt. Welche Daten abgefragt werden, hängt auch unter anderem von den
gemachten Eingaben ab:
Gruppe
Die Gruppe wird vorbelegt und ist nicht änderbar. Ist
der Maske bzw. dem Register bereits eine Gruppe zugeordnet, so wird diese
genommen. Ansonsten wird automatisch ein Name generiert.
Zeile / Spalte
Jedes Objekt
[...]


---

## Aktiv Passivsetzung

Aktiv Passivsetzung
Es können ALLE in der Auswahlliste angewählten
Aktiv-Passiv Kennzeichen umgewandelt werden, steht ein Kennzeichen auf aktiv, so
wird es passiv und umgekehrt.

---

## Allgemeine Bemerkungen

Allgemeine Bemerkungen
Durch die POS-Kasse werden dieselben Relationen
befüllt wie beim Erfassen durch die Tresenkasse, so dass die Übersichten für
beide Systeme gelten.
Da parallel gedruckt wird, sollte man auf diesen
Drucker nichts umleiten, da der Druckkanal von dem zugehörigen Arbeitsplatz
solange „besetzt“ ist wie man sich auf der POS-Maske befindet (die ja nicht
verlassen werden muss, um den nächsten Barverkaufsvorgang zu beginnen!).
Wenn in FRZ bei der Klasse Rechnung und der
Unterklasse Barverkauf erfassen bei Brutto-Vorgänge „Ja“ eingetragen ist, wird
der eingetragene Preis als Bruttopreis interpretiert, wenn dort „Nein“
eingetragen ist, wird der eingetragene Preis als Nettopreis interpretiert.
Natürlich ist beim Barverkauf eine Bruttoerfassung zu
bevorzugen und auch ein Zurückgreifen auf Bruttopreislisten.
Um einen Vorgang mit einem Minimum an
Tastenkombinationen zu erfassen, sind folgende Einstellungen nötig:
Einrichterparameter EPA
Soll im Artikelfeld
begonnen we
[...]


---

## Allgemeiner Ablauf

Allgemeiner
Ablauf
Der Auslandszahlungsverkehr läuft genau wie der
Inlandszahlungsverkehr ab, also Zahlungsvorschläge erstellen dort ist unter
Regulierung der Wert "
Zahlungsausgang Ausland
" einzutragen-,
Zahlungsvorschläge bearbeiten und freigeben, Zahlungen bearbeiten. Es werden für
den Auslandszahlungsverkehr jedoch nur die OP's herangezogen, die als
Auslandszahlung gekennzeichnet sind. Dies kann man manuell überall dort machen,
wo man sich OP-Infos (
Shift F8
) ansehen kann (z.B. in der
OP-Verwaltung).
Für Kunden, die als Auslandskunden erfasst sind,
werden die OP's grundsätzlich als Auslands-OP gekennzeichnet. Akonto-Zahlungen,
die über "
Zahlungen erstellen
" erfasst werden,
werden für Auslandskunden als Auslandszahlungen gekennzeichnet.

---

## ALTER STRUCT Statement

ALTER STRUCT
Statement
Syntax
ALTER STRUCT table-name [INTO Dateiname]
Purpose
Erstellt für eine Tabelle die Beschreibung. Im
Gegensatz zu
CREATE
STRUCT
wird die Tabelle nur mit den Primäschlüsselfeldern angelegt und alle
anderen Felder werden mit ALTER TABLE hinzugefügt.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
DBFCREATE
,
CREATE PRIMARY KEY
,
XMLImport
,
XMLExport
,
DBFCREATE
,
CREATE STRUCT
Beschreibung
Um die Beschreibung ( das create table Statement) für
eine Tabelle zu erhalten, steht dieses Statement zur Verfügung. Es erstellt eine
Datei ( Achtung immer „Overwrite“ ) in der das Create-Statement zuzüglich der
Indexe enthalten ist. Wird „INTO Dateiname“ nicht angegeben, wird der table-name
mit der Endung „.SQL“ als Dateiname verwendet.
Beispiel
ALTER STRUCT FIBUVORGKLASSE INTO
c:\FIBUKL.SQL;

---

## Altteilsteuer

Altteilsteuer
Allgemein
Die Umsätze beim Austauschverfahren in der
Kraftfahrzeugwirtschaft sind in der Regel Tauschlieferungen mit Baraufgabe. Der
Lieferung eines aufbereiteten funktionsfähigen Austauschteils (z.B. Motor,
Aggregat,...) durch den Unternehmer der Kraftfahrzeugwirtschaft stehen eine
Geldzahlung und eine Lieferung des reparaturbedürftigen Kraftfahrzeugteils
(Altteils) durch den Kunden gegenüber. Als Entgelt für die Lieferung des
Austauchteils sind demnach die vereinbarte Geldzahlung und der gemeine Wert des
Altteils anzusetzen. Dabei könne Altteile mit einem Durchschnittswert von
10.v.H. des Bruttoaustauschentgeldes bewertet werden. Als Bruttoaustauschentgeld
ist der Betrag anzusehen, den der Endabnehmer für den Erwerb eines dem
zurückgegebenen Altteil entsprechenden Austauschteil abzüglich Umsatzsteuer,
jedoch ohne Abzug eines Rabattes zu zahlen hat. Setzt ein Unternehmer bei der
Abrechnung an Stelle des Durchschnittswerts andere Werte an, so sind die
tatsäch
[...]


---

## Branchen-ERP Etikettendruck

Branchen-ERP Etikettendruck
In Referenz-ERP ist das Reporttool „
Branchen-ERP Etikettendruck
“
integriert, mit dessen Hilfe man Etiketten, Karteikarten und Listen erstellen
kann. Neben der Ausgabe von Balkengrafiken und der Einbindung von Grafiken
können mit dem Branchen-ERP Etikettendruck auch diverse
Barcodeformate
dargestellt werden.

---

## Anbindung an das Referenz-ERP

Anbindung an das Referenz-ERP
Per Ereignissteuerung kann eine automatisierte
Verarbeitung der Ausgehenden wie auch eingehenden Datenstrukturen gewährleistet
werden. Hierzu steht die Funktion Bitzer_Vorgang zur Verfügung. Diese Funktion
bildet über ein Importverzeichnis die Übernahme der Daten in die Offline-
Waagedaten Tabelle ab.

---

## Anlegen der Relationen

Anlegen der Relationen
create table ScriptParam (
ScriptPBedKorr INTEGER NOT NULL DEFAULT 0,
ScriptPBesitzer smallint NOT NULL DEFAULT 0,
ScriptPBezeich char(50) NOT NULL,
ScriptPId char(20) NOT NULL UNIQUE,
ScriptSystem smallint NOT NULL DEFAULT 0,
primary key (ScriptPId )
);
create table tScriptParamPar (
ScriptPId char(20) NOT NULL,
ScriptPPAktiv smallint NOT NULL DEFAULT 1,
ScriptPPBedKorr INTEGER NOT NULL DEFAULT 0,
ScriptPPBezeich char(50) NOT NULL,
ScriptPPId char(30) NOT NULL,
ScriptPPTyp smallint NOT NULL DEFAULT 0,
ScriptPPWert1 char(50) NOT NULL DEFAULT '',
ScriptPPWert2 char(50) NOT NULL DEFAULT '',
ScriptPPWert3 char(50) NOT NULL DEFAULT '',
ScriptSystem smallint NOT NULL DEFAULT 0,
primary key (ScriptPId ,ScriptPPId )
);

---

## Ansichten verwalten

Ansichten ve
rwalten
Die Funktion „Ansichten verwalten“ dient zum Erstellen
von systemweiten individuell angepassten Darstellungen, die für alle Anwender,
für die sie freigegeben wurden, gleich sind. Dort werden die Einstellungen der
Funktionen „Sortierung“, „Farben“, „Spalten“, „SQL-Variablen“, „Summen“, die
Position der Spalten sowie Reporte festgelegt. Nur wer Zugriffsrecht auf die
Funktion „Ansicht verwalten“ hat, kann Änderung über die oben genannten
Funktionen vornehmen. Die Spaltenposition und Spaltenbreite können für
freigegebene Ansichten zwar noch geändert werden, werden aber nicht
gespeichert.
Wählt man für eine Variante die Funktion das erste Mal
aus, so erscheint der folgende Bildschirm. Die „Standard“-Ansicht ist die von
Branchen-ERP ausgelieferte Variante und für diese sind die Zusatzfunktionen nicht
aktiv.
Um nun eine eingen Ansicht zu generieren, wählt man
„speichern als
“. Man wird dann nach
dem neuen Namen gefragt, unter dem diese Ansicht gespeichert werden soll.
[...]


---

## Anwendung Serienbriefe

Anwendung Serienbriefe
Hauptmenü
Büro und Internet
Büroumgebung
Serienbrief
Direktsprung
[BRIEF]
.
Diese Anwendung ist eine Sammelanwendung, in der sich
alle Variante befinden, zu denen Serienbriefe existieren. Sie kann also erst
aufgerufen werden, wenn man bereits in irgendeiner anderen Anwendung einen
Serienbrief erstellt hat. Diese Variante erscheint dann zusätzlich in der
Sammelanwendung Serienbriefe.
Die Verarbeitung erfolgt hier wie gewohnt.

---

## Anwendungsregister

Anwendungsregister
Fast alle Funktionen des Anwendungsregisters lassen
sich auch über eine Funktionstaste aufrufen. Welche Tasten sich hinter den
Schaltflächen verbergen, wird in Referenz-ERP in einem Tooltipp angezeigt, wenn man
mit dem Mauszeiger über der Schaltfläche stehen bleibt.
Funktionstaste
Bedeutung
Varianten
Strg+1
bis ggf.
Strg+9
Hier
      lassen sich die Varianten der Auswahlliste auswählen. Die Auswahl erfolgt
      entweder per Maustaste oder – wenn die Varianten bekannt sind – über die
      Tasten
Strg+1
bis ggf.
Strg+9
Profile
Die
      Profile lassen sich nur mit der Maustaste ändern.
Ansicht
Hierüber kann eine
Ansicht
ausgewählt
      werden. Diese Schaltfläche wird ausgeblendet, wenn für den Bediener nur
      die Standardansicht verfügbar ist.
Die
      Ansichten lassen sich nur mit der Maustaste ändern-
Bereich
F2
Durch Klicken auf die Schaltfläche
öffnet sich die
      bekannte Bereichsauswahl. Der Aufruf kann auch mit der Funktionstaste
F2
erfolgen. Diese
[...]


---

## Anzahl

Anzahl
Im Feld Anzahl wird die Menge angegeben.

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
Selektionswirksame JVARS werden zur Konstru
[...]


---

## Archiv – Dokumente hinzufügen Drag und Drop aus Explorer

Archiv – Dokumente hinzufügen Drag und Drop aus Explorer
Nach erfolgter Übernahme in das Archiv wurden folgende
zusätzliche Felder wie folgt automatisch vorbelegt:
Feld-Beschriftung
Vorbelegung
Titel
Dateiname (*)
Dateiname
Dateiname (*)
(*) ohne Pfad und Dateinamen-Erweiterung

---

## Archiv – Dokumente hinzufügen Drag und Drop aus Outlook

Archiv – Dokumente hinzufügen Drag und Drop aus Outlook
Es können sowohl Mails als auch nur eventuell
vorhandene Anhänge importiert werden.
Nach erfolgter Übernahme in das Archiv wurden folgende
zusätzliche Felder wie folgt automatisch vorbelegt:
Feld-Beschriftung
Vorbelegung
Betreff
Der
      Betreff der Mail (1)
Autor
Die
      E-Mail-Adresse des Senders (1,2)
Dateiname
Die
      technische Message-ID der E-Mail. Diese könnte für weitere datentechnische
      Verarbeitungen genutzt werden.
(1)  Auch
bei „Nur-Anhänge“-Importen.
(2)  Bei
„lokalen“ Exchange-Servern die Exchange-E-Mail-Adressen, bei externen E-Mails
die „normale“ E-Mail-Adresse.

---

## Archivierung setzen

Archivierung setzen
Hier kann man für mehrere Formulare gleichzeitig die
Einstellung für die
Archivierung
setzen.
Die
Einstellung wird beim Starten der Funktion vorbelegt mit ‚archivieren und
Nachricht im Fehler-/Ereignisprotokoll’. Dies kann man aber durch die F3-Auswahl
wie gewünscht anpassen. Durch die Funktion Ausführen F9 wird diese Einstellung
dann für alle markierten Formulare übernommen.

---

## Archivierung aktivieren für das Formular

Archivierung aktivieren für das
Formular
Hier hat man in der F3-Auswahl verschiedene
      Möglichkeiten:
Name
Bedeutung
nicht archivieren
Das
      Formular wird beim Druck nicht im Formulararchiv abgelegt.
archivieren
      und Probleme immer melden
Das
      Formular wird beim Druck im Formulararchiv abgelegt. Archivierungsprobleme
      (z.B. Archiv liegt auf einer anderen Datenbank und die Verknüpfung dorthin
      ist nicht okay oder die Datenbank läuft gar nicht; die Festplatte ist voll
      oder defekt) werden bei jedem Druck gemeldet.
archivieren
      und Probleme nur einmal melden
Das
      Formular wird beim Druck im Formulararchiv abgelegt. Archivierungsprobleme
      werden nur einmal gemeldet. Das ist sinnvoll, wenn man z.B. sehr viele
      Rechnungen am Stück druckt.
archivieren
      und Nachricht im Fehler-/Ereignisprotokoll
Das
      Formular wird beim Druck im Formulararchiv abgelegt. Auf
      Archivierungsprobleme wird man nicht über eine Meldung
[...]


---

## Archiv ändern (Ansehen)

Archiv ändern (Ansehen)
In diesem Dialog besteht die Möglichkeit folgende
Daten zu ändern bzw. einzusehen:
Felder
Belegreferenz
Die
      Kern-Identität des Archives.
Die
      Beleg-Referenz verknüpft u.a. den Archiv – Eintrag mit einem Archiv-Fakt
      (siehe auch
Archiv
      Fakt-Tabellen
)
Die
      Beleg-Referenz kann eine Art Klammer für „gleiche“ Archiv-Belege
      darstellen. Dieses Vorgehen wird auch empfohlen.
Für
      die Archiv – Fakten stehen Beleg-Generatoren (privatisierbare
      Datenbank-Funktionen) zur Verfügung (siehe
Referenz
).
Obwohl die Beleg-Referenz im
      Einzelfall frei wählbar ist, ist aber auch zum Beispiel in Hinblick auf
      die Funktion
Archiv anzeigen
(siehe
Archiv Ansehen
)
      eine gewisse Organisation der Referenzen anzuraten. Auch nehmen einige
      Programm-Module sehr wohl auf die konkrete Beleg-Referenz Bezug, so dass
      im Einzelfall von einer zu freizügigen Abänderung der Beleg-Referenz
      abgeraten wird.
Belegn
[...]


---

## ASQL Texte löschen

ASQL Texte löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
ASQL_Texte

---

## Aufbau der Datenbank-Tracedatei

Aufbau der
Datenbank-Tracedatei
Die erzeugte Datenbank-Tracedatei ist als
OSQL-Einspielscript formuliert.
LOADTUETTEL;
insert into amic_tracefile
(TraceZeit,TraceCursorNo,TraceMaske,TraceVerbrauch,
TraceError,TraceCursor,TracePlan,TraceSelect,TraceUser,TraceStatus,TraceTrace)
values (%s)
Felder der Datenbank-Tracedatei
Tracezeit
Zeitstempel
TraceCursorNo
TraceMaske
Diese Maske war zum Zeitpunkt
      aktiv
TraceVerbrauch
Zeitverbrauch in
      Millisekunden
TraceError
Rückgabe-Status des
      Datenbank-Servers auf die Datenbank-Anweisung
TraceCursor
TraceSelect
Datenbank-Anweisung
TraceUser
TraceStatus
Stati die das technische Umfeld
      beschreiben
TraceTrace

---

## Aufbau des Grundbildschirms

Aufbau des Gr
undbildschirms
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Im unteren Bereich des Bildschirms werden die
erfassten Belege dargestellt, von hier können sie zur Bearbeitung, z.B. zur
Korrektur, auch wieder aufgerufen werden. Über die Funktion
Auswahl
F2
kann man aus verschiedenen
Darstellungsmöglichkeiten (Varianten) wählen oder sich private Varianten
ableiten.
Rechts oben werden die Buchungsarten und die
Bearbeitungsfunktionen bereitgestellt. Bearbeitungsfunktionen sind z.B. Änderung
der Buchungsperiode, Korrektur der Belege etc... Diese Funktionen können über
Funktionstasten, Mausklick oder Cursorpositionierung aufgerufen werden.
Das Buchen in Belegarten ist das zentrale
Erfassungskonzept der Finanzbuchhaltung. Dahinter steht der Ansatz, dass sich
der Buchungsstoff der Finanzbuchhaltung durch standardisierbare
Erfassungsabläufe auszeichnet, innerhalb derer bestimmte Abläufe immer gleich
erfolgen. So wird z.B. ein Zahlungseingang von
[...]


---

## Aufgabenplaner für Reporte

Aufgabenplaner für Reporte
Die Erstellung eines Reports kann einige Zeit in
Anspruch nehmen. Unter Umständen ist eine Menge an Daten zu sammeln und die Last
der Datensuche behindert Anwender bei der Arbeit mit Referenz-ERP. Der Aufgabenplaner
erstellt für die Windows-Aufgabenplanung einen Eintrag. Voraussetzung dafür,
dass der Report zu der angegebenen Zeit ausgeführt wird, ist daher, dass der
eigene Rechner zu dem Zeitpunkt läuft und der Anwender angemeldet ist – der
Rechner kann natürlich trotzdem gesperrt sein.
Den Aufgabenplaner erreicht man, indem man von der
Bereichsauswahl des Reports - oder direkt in der Vorschau des Crystal Reports -
die Funktion „
Aufgabenplaner für
Reporte
“
F8
aufruft.
Daraufhin öffnet sich ein weiterer Dialog, in dem man
angibt, wann der Report erstellt werden soll.
Feld
Bedeutung
Name
Der
      Name der Aufgabe wird mit der Bezeichnung des Reports vorbelegt. Dieser
      Name erscheint in Aufgabenplanung von Windows im Ordner Referenz-ERP. Damit
      di
[...]


---

## Auflistung aller Vorgänge dieser Klasse

Auflistung aller Vorgänge dieser Klasse
Im Knopf Klasse ist hinterlegt, in welcher
Vorgangsklasse sich der Anwender bewegt. Soll nun ein Beleg dieser Klasse zur
Schnellkorrektur (incl. den oben erwähnten Einschränkungen) herangezogen werden,
so lässt sich mit dem Knopf Liste eine Liste der für diesen Kunden vorhandenen
Belege dieser Klasse anzeigen.
Jetzt kann durch Anwahl der Vorgangsnummer (per Maus)
der Vorgang in die Schnellkorrektur geladen werden, aber ACHTUNG, diese
Schnellkorrektur ist nur für einfach strukturierte Belege gedacht, alle oben
erwähnten Belegelement gehen mit dieser Korrektur verloren.

---

## Aufruf einer BI Anwendung

Aufruf einer BI Anwendung
Durch Anklicken des Menüpunktes in der Abteilung
BI-Anwendungen im Bereich Information kann nun direkt die Anwendung gestartet
werden, hierzu wird der Anwender zunächst gefragt, für welchen Bereich(Filter)
die Daten im Excel-Blatt bereitgestellt werden sollen. Es können hierbei
verschiedene Profile genutzt werden, nach Betätigung der Auswahl durch die F9
Taste wird die Excel Anwendung gestartet. Hierbei gilt nun folgende Regel:
Befindet sich im „TEMP“-Verzeichnis des Anwenders eine
BI Datei mit dem entsprechenden Namen, mit einem vorangestellten
Mandantenkurzbezeichnungs-Precode, und ist das Datum dieser Datei größer oder
gleich dem in der Datenbank gemerkten Erstelldatum dieser BI Excel-Tabelle, so
wird sofort diese Excel Mappe gestartet.
Ist das Datum im „TEMP“ Bereich < oder existiert
keine Datei, so wird aus der Datenbank die Vorlage in das TEMP-Verzeichnis
kopiert und dann gestartet.
Die BI Anwendung reagiert jetzt wie eine eigenständige
Excel
[...]


---

## Aufruf ohne Auswahlliste

Aufruf ohne Auswahlliste
Die JVAR mit dem Owner 1977 kann mit einer Liste
kommaseparierter Adressid gefüttert werden. Dann wird die Anzeige des Browsers
aufgerufen:
Mit diesem JPL-Code
call JVARS_SET(1977,
"AdressIds", "1478,1480,1482,1484,1486")
call CS
("GoogleMapsPoints")
wird der Browser mit den markierten Adressen
geöffnet.
(1478,1480 usw. stehen für die AdressIds)
Im Pascal-Makro wird der Controlstring aufgerufen
StrCpy(Adress,"294,299,300");
JVarsSet( 1977, "AdressIds", Adress );
if( JPPNEW ( "PFF" , "JExec" ) = 1 ) then
begin
sprintf(buf,"^CS GoogleMapsPoints" );
JPPIN ( "PFF"
,"ctrl"       ,
buf       );
JPPDO ( "PFF", "CtrlString" , " " ,2048 );
JPPDELETE ( "PFF" )
End

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

## Ausführen

Ausführen
Durch Betätigung dieses Knopfes wird die Erstellung
der DTA Datei gestartet. Es werden die Daten erzeugt, eine Banksammelliste und
die entsprechen Begleitzettel auf dem Aeins Standdarddrucker (DRZ) gedruckt.

---

## Ausgabedatum

Ausgabedatum
Das Ausgabedatum wird mit dem aktuellen Datum
vorbelegt.

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
Par
[...]


---

## Ausgehende Telefonie über smx_call 1100

Ausgehende Telefonie über smx_call 1100
Um ein ausgehendes Telefonat einzuleiten muss die
Software mitgeteilt bekommen wo und wie sie die zu wählende Telefonnummer
bekommen kann.
Dazu ist es in den meisten Fällen notwendig an den
betreffenden Stellen eine private Funktion anzulegen die per Controlstring die
Referenz-ERP-Programmfunktionalität ^smx_call 1100 mit geeigneten weiteren Parametern
aufruft. Die Referenz-ERP-Methode verwendet Standard-Windows-Methoden für den
Telefonanruf. Spezielle Systeme müssen über die unten aufgeführte
Script-Methodik angesprochen werden.
Parameter ^smx_call 1100 Modus
      Param1 Param2
Modus=0 („Auswahlliste“)
Wenn
      Param1  angeben ist, dann dieser als Name der Auswahllisten-Spalte
      interpretiert und der dortige Wert als
Telefonnummer
verwendet.
Wenn
      Param1 nicht angeben ist, dann wird die
Telefonnummer
vom System
      wie folgt ermittelt:
Es
      wird die KundId aus der Returnliste gesucht, sollte das nicht gehen wird
      die Kun
[...]


---

## Auswahlliste 2.0

Auswahlliste 2.0
Das Design der Auswahlliste wurde komplett
überarbeitet. Es wurde ein Menüband (Ribbon), wie man es von Word oder Excel
kennt, verwendet. Dieses enthält zwei Register, das Anwendungsregister und das
Darstellungsregister, auf denen die Funktionen dargestellt werden:
Anwendungsregister
:
Stapelverarbeitungsregister
: Dieses
Register ist nur zu sehen, wenn für den Anwender Stapelverarbeitung aktiviert
wurde und wenn die Auswahlliste eine IDENT-Verarbeitung zuläßt.
Darstellungsregister
:
Alle hier verwendeten Funktionen befinden sich auch im
Optionbox-Menü, das über die rechte Maustaste zu erreichen ist. Werden
Funktionen im Optionbox-Menü weggeschützt, so sind sie im Menü-Band auch nicht
mehr zugänglich.

---

## aus Stapel entfernen

aus Stapel entfernen
Die Funktion „
aus
Stapel entfernen
“
Strg+F7
steht dann zur Verfügung, wenn man mit der Funktion „Umschalten
Stapelverarbeitung“ in die Stapelverarbeitung gewechselt hat. Diese ist aktiv,
wenn man Datensätze ausgewählt hat und entfern – ohne Rückfrage – die Datensätze
aus dem Stapel. Der Staple wird
nicht
automatisch gelöscht, wenn er leer
ist.
Sind Vorgänge der Warenwirtschaft in einem Stapel
zusammengefast und wird für einen Vorgang ein technischer Storno erstellt, so
werden diese Vorgänge aus allen Stapeln entfernt.

---

## Auswertungen Mitgliederverwaltung

Auswertungen Mitgliederverwaltung

---

## Automation

Automat
ion
Um sicher zu stellen, dass man sofort auf eventuell
aufgetretene Fehler hingewiesen wird, kann man Referenz-ERP so starten, dass sofort
der Reorganisator aufgerufen wird und die Testfunktionen ausgeführt werden. Das
automatische Ausführen der Reorganisation selbst wird nicht unterstützt.
Referenz-ERP muss mit folgender Syntax gestartet werden:
Aeins
welcome section
DIR=FIREO USER=????
PASSWORT=????
Referenz-ERP wird gestartet und der Direktsprung FIREO wird
direkt ausgeführt. Es werden dann der „
Test Stammdaten
“ und der
„
Test Bewegungsdaten
“ ausgeführt. Anschließend wird Referenz-ERP
verlassen. Das Ergebnis der Tests befindet sich in der Datei, die unter OPT
unter der globalen Option FIREO_EVENT_DATEINAME eingetragen ist.
Ist diese Option nicht gesetzt dann wird der Dateiname
verwendet, der unter
Optionen
für den Benutzer eingetragen
ist, mit dem Referenz-ERP gestartet wird. Wird die Reorganisation als Event gestartet
ist zu beachten, dass das Event auf dem Datenbankserver läuft und dort
[...]


---

## Auszahlung

Auszahlung
Eine Auszahlung kann nur auf Basis einer bestehenden
Kündigung erfolgen.
Der eingegebene Betrag wird gegen die Einlagesumme
abzüglich Pflichteinzahlungen der etwaigen. verbleibenden Anteile geprüft.
Hiermit wird verhindert, dass ein unzulässiger Auszahlungsbetrag eingegeben
wird.
Werden diese Einträge gespeichert, erfolgt sofort der
Eintrag der resultierenden Buchung in die Primanota. Der erfolgreiche Eintrag
wird mit dem Status <gebucht> quittiert. Sollte der Buchungseintrag
fehlschlagen, sind die Einträge im Gesellschaftsstamm sowie die Berechtigungen
des ausführenden Bedieners zu prüfen.
Um Anteile zu kündigen wird ein Gesellschafter in der
Auswahlliste ausgewählt mit
F5
zum
Bearbeiten
geöffnet und die Funktion
Auszahlung
F6
ausgewählt.
Die Funktion
Auszahlung
F6
öffnet folgende Eingabefelder:
Felder
Wert
      der Auszahlung
In
      dieses Feld wird der Wert der Auszahlung eingetragen
Auszahlungsdatum
Hier
      wird das Auszahlungsdatum hinterlegt.
Bemerkun
[...]


---

## Automatisches Refresh beim Pivotelement.

Automatisches Refresh beim
Pivotelement.
Das Automatische Refresh der Pivot-elemente ist keine
Standardfunktion des Excel System, hierzu muss ein kleines VBA Script
geschrieben werden. Dieses VBA Script wird dann an das Ereignis
„AfterQueryDataRefresh“ gebunden, so dass immer nach erfolgtem Datenlesen sofort
die Pivot-Tabelle auf einen richtigen Stand gebracht wird.
Hierzu ist zunächst in den Menüoptionen die Menüleiste
„Entwicklertools“ einzuschalten, um dann den Bereich VBA anzuwählen.
Als nächstes ist per INSERT (Einfügen) eine neue
Klasse zu bilden. Diese Klasse MUSS sofort umbenannt werden, in meinem Beispiel
in clsQuery. Folgender Inhalt muss in diese Klasse eingetragen werden:
Option Explicit
Public WithEvents MyQuery As QueryTable
Private Sub MyQuery_AfterRefresh(ByVal Success As
Boolean)
If Success Then Call RefreshAllPivotTables
End Sub
Private Sub MyQuery_BeforeRefresh(Cancel As
Boolean)
End Sub
Sub RefreshAllPivotTables()
Dim PT As PivotTable
Dim WS As Worksheet
O
[...]


---

## Automation von Prozessen

Automation von Prozessen

---

## Automatische Umrechnung

Automatische Umrechnung
Bei einer Rechnung in Fremdwährung werden die
eingegebenen Beträge automatisch umgerechnet. Dabei kann es durch Rundungen zu
einer Besonderheit kommen. Hat eine Rechnung mehrere Positionen und rechnet man
jede einzelne Position von Fremdwährung in Euro um, so kann der Saldo dieses
Beleges unter Umständen nicht auf null aufgehen. Beispiel:
USD
Kurs
EUR
Euro Gerundet
Position 1
1.000,00
1,269300
787,8358…
787,84
Position 2
2.000,00
1.575,6716…
1.575,67
Position 3
1.000,00
787,8358…
787,84
Summe
4.000,00
3.151,35
Rechnet man jedoch 4.000,00 USD zu dem Kurs um, so
ergibt sich ein gerundeter Wert von 3.151,34. Diese Differenz wird dann auf das
im Währungsstamm hinterlegte Ausgleichskonto gebucht. Es ergibt sich dann
folgenden Buchungssatz:
USD
EUR
USD
EUR
Personenkonto
4.000,00
3.151,34
an
      Erlöskonto
1.000,00
787,84
an
      Erlöskonto
2.000,00
1.575,67
an
      Erlöskonto
1.000,00
787,84
an
      Ausgleichskonto
0,00
-0,01
Diese Ausgleichsbuchung wi
[...]


---

## Automatisierter Vorgangsimport

Automatisierter Vorgangsimport
Vorgangsimporte können regelmäßig importiert
werden.
Dazu gibt es verschiedene Wege:

---

## Basisfont

Basisfont
Mit F3 auf diesem Feld öffnet sich der Schriftart
Dialog, indem man die gewünschte Schriftart auswählen kann. Das ermöglicht die
fehlerfreie Eingabe des gewünschten Fonts in dieses Feld.
Die Größe des
Basisfont bestimmt die Zeilen- und Spaltenanzahl des Formulars.

---

## Begleitzettel und Kennzeichnung des Datenträgers

Begleitzettel und Kennzeichnung des Datenträgers
Für den Begleitzettel wird ein neuer Formulartyp "272
Begleitzettel DTA-Ausland" bereitgestellt. Der einem Datenträger beizufügende
Begleitzettel muss nachfolgende Mindestangaben enthalten:
•
Begleitzettel
•
Belegloser Datenträgeraustausch DTAZV
•
AWV-Meldung durch Kreditinstitut oder AWV-Meldung ist beigefügt
•
Sammelauftrag für Auslandszahlungen
•
Datenträger-Nummer
•
Erstellungsdatum
•
Erster Ausführungstermin
•
Anzahl der Datensätze T (Kontrollsumme aus Feld Z 4)
•
Summe der Beträge über alle Währungen der Datensätze T
(Kontrollsumme
aus Feld Z 3)
•
Auftragswährung / Betragssumme / Kontonummer/  Kontowährung /
Ausführungstermin / zu zahlende Währung
•
Name und Anschrift Auftraggeber
•
Ort, Datum
•
Firma, Unterschrift(en)
Kennzeichnung des Datenträgers im
Auslandszahlungsverkehr
Die Datenträger sind durch Klebezettel mit folgenden
Angaben zu kennzeichnen:
•
Name und IBAN oder Bankleitzahl / Kontonummer des
Datenträgerabsenders

[...]


---

## Begriffsdefinitionen

Begriffsdefinitionen

---

## Beispiel Betrag in Worten im Formular

Beispiel Betrag in Worten im Formular
// Priv. Prozedur p_BetragInPolnisch --- BT
10.08.2005
//
// Beschreibung:
//
//
//
CREATE Function p_BetragInPolnisch (
in
in_ZiffernVorkomma char(15),
in in_ZiffernNachkomma
char(15),
in in_Vorzeichen integer,
in in_Dezimalstellen
integer,
in in_Betrag numeric(15,6)
)
RETURNS
char(500)
BEGIN
DECLARE text char(200);
declare hilf_text
char(500);
declare hunderttausender char(1);
declare zehntausender
char(1);
declare tausender char(1);
declare hunderter char(3);
declare
zehner char(2);
declare einer char(1);
declare nachkomma
char(500);
declare local temporary table zt
( zt
char(40),
z integer
) on commit delete rows
;
insert into zt ( z, zt ) values ( 0, '' );
insert into zt (
z, zt ) values ( 1, 'jeden' );
insert into zt ( z, zt ) values ( 2,
'dwa' );
insert into zt ( z, zt ) values ( 3, 'trzy' );
insert
into zt ( z, zt ) values ( 4, 'cztery' );
insert into zt ( z, zt )
values ( 5, 'plec' );
insert into zt ( z, zt ) values ( 6, 'sz
[...]


---

## Beispiel einer Pie Chart Einbindung

Beispiel einer Pie Chart Einbindung

---

## Beispiel eines „erweiterten Filters“

Beispiel eines „erweiterten Filters“

---

## Beispiel eines Lookup Befehls

Beispiel eines Lookup Befehls

---

## Beispiel für Gruppe 0 (Schema)

Beispiel für Gruppe 0 (Schema)

---

## Beispiel für Gruppe 15 (Schema)

Beispiel für Gruppe 15 (Schema)

---

## Beispiel Positionen zusammenführen

Beispiel
Positionen zusammenführen
Nur wenn alle einzelnen Schritte ohne Fehler verlaufen
sind wird der Vorgang verändert.
Auch hier ist die Schachtelungstiefe sehr gut zu
erkennen
1.
JPP-Objekt erzeugen, füllen, beenden (siehe Beispiel vorher)
2.
Vorgang laden, speichern und beenden
3.
alle Warenpositionen des Vorgangs durchlaufen
4.
Die ArtikelID der aktuellen Warenposition holen (wird intern zum Vergleichen
benötigt)
5.
Die WABEWID der aktuellen Warenposition holen (s.o.)
6.
Mittels SQL-Staement prüfen ob Partie in der Position vorhanden ist
7.
Warenposition laden, bearbeiten, speichern
8.
Menge der aktuellen Warenposition holen
9.
Neue Menge der Warenposition setzen
10.
Partie um die neue Menge erhöhen
Die gesamte Programmlogik wurde hier weggelassen da
sie sehr umfangreich ist und die Bestandeile der JPP-Objekte somit nicht mehr
klar erkennbar wären.
Es werden alle Warenpositionen (kurz WaPo) des
Vorgangs durchlaufen. Zu jeder WaPo wird geprüft
[...]


---

## Beispiel zur Verwendung von JPP-Objekten

Beispiel zur
Verwendung von JPP-Objekten
Wir gehen hier davon aus das ein Objekt Namens „aeins“
im Script korrekt instanziert wurde.
Im Beispiel wird ein „JDBX“-Objekt verwendet
Option Explicit
dim aeins
set aeins = createobject("Branchen-ERP.Aeins")
aeins.connect(...
sub xyz
dim sql
dim hdl
hdl = “xyz”
sql = “SELECT irgendwas FROM
irgendwo”
if aeins.jpp_new (hdl, "JDBX") then
aeins.jpp_in hdl, "sql"  ,
sql
aeins.jpp_do hdl , "exec"
if aeins.jpp_do (hdl, "DBERR") = 0
then
tu was
…
End if
aeins.jpp_delete hdl
end if
end sub

---

## Belege

Belege
In den Belegen kann man alle erstellten Aufträge im
Bezug auf die ausgewählte Firma ansehen.

---

## Belegerzeugung aus importierten Vorgangsdaten

Belegerzeugung aus importierten Vorgangsdaten
Weiterverarbeitung der einem Datenträger importierten
Vorgangsdaten
Mit dem Direktsprung [VUEB] (Vorgang-Übergabe) wird
eine Auswahlliste geöffnet.
Variante 1 - Belegerzeugung
In Variante 1 (Belegerzeugung) werden die importierten
Datensätze (z.B. aus dem Datenträger von der Waage), die in die Vorgänge
importiert werden sollen, angezeigt. In der Option-Box steht die Funktion zur
Belegerzeugung zur Verfügung.
Belege erzeugen
Mit Hilfe des Pascal-Scriptes „VorgangEinspielung“
werden die Vorgänge aus der Zwischentabelle in das Vorgangswesen von Aeins
importiert. Fehlerhafte Sätze werden entsprechend markiert. Treten Fehler auf,
so enthält das Fehlerprotokoll die zugehörigen Angaben.
Falls nacheinanderfolgende Roh-Belege in den
erforderlichen Details übereinstimmen (Kunde, Datum, Belegnummer etc.), wird
daraus nur ein Vorgang mit mehreren Warenpositionen erzeugt.
Die Belegnummer des erzeugten Beleges wird in die
Roh-Daten zurückgesch
[...]


---

## Belegfluss Variante 1 Meine Postfächer

Belegfluss Variante 1 Meine Postfächer
Auswahlliste
Name
Beschreibung
Id
ID
      des Belegfluss
Postfach
ID
      des Postfachs
Postfach-Bezeichnung
Bezeichnung des
      Postfachs
Dokumentenstatus
Status des Belegs im Archiv
      (Hinweis: Anwendungsformat af_GENEHMI muss gesetzt sein, um Status richtig
      anzuzeigen)
Belegtyp
Typ
      des Belegs (ohne Beleg, Ware oder Fibu)
Archiv/Druck-Datum
Datum an dem der Beleg gedruckt
      wurde
Beleg-Referenz
Zeigt die Belegreferenz im Archiv
      an
Beleg-Klasse
Zeigt die Belegklasse an
Belegnummer
Zeigt die Belegnummer an
Vorgangsklasse
Zeigt die Vorgangsklasse bei
      Ware-Belegen an
Belegdatum
Zeigt das Belegdatum an
Inhalt
Zeigt den technischen Typ des Belegs
      gemäß MIME-Spezifikation an
Suchoption
Name
Beschreibung
Postfach
Postfachbezeichnung
Fa-Id
Formular Archiv Id
FA-MndNr
Formular Archiv -
      Mandantennummer
Belegtyp
Filtert, ob Beleg schon existiert
      sowie nach Typ des Belegs
Funktionen
Name
Besch
[...]


---

## Belegfluss Variante 2 Alle Dokumente

Belegfluss Variante 2 Alle Dokumente
Auswahlliste
Name
Beschreibung
Id
Id
      des Belegfluss
Postfach
Postfach ID
Postfach-Bezeichnung
Postfach Bezeichnung
Status
Status des Beleges
Archiv/Druck-Datum
Datum an dem der Beleg gedruckt
      wurde
Beleg-Referenz
Zeigt die Belegreferenz im Archiv
      an
Beleg-Klasse
Zeigt die Belegklasse an
Inhalt
Zeigt den Typ des Belegs
      an
Suchoption
Name
Beschreibung
Postfach
Postfachbezeichnung
Fa-Id
Formular Archiv Id
FA-MndNr
Formular Archiv -
      Mandantennummer
Funktionen
Name
Beschreibung
Anlagen
Öffnet einen Archiv-Pfleger zum
      Hinzufügen eines Datensatzes

---

## Belegfluss Variante 3 Historie

Belegfluss Variante 3 Historie
Auswahlliste
Name
Beschreibung
Id
ID
      der Historie
Postfach Id
Id
      des Postfachs
Postfach Bezeichnung
Postfachbezeichnung
Änderung Postfach
Datum der Änderung am Beleg im
      Postfach
Status
Status des Belegs
Änderung Status
Datum der Änderung des
      Belegstatus
Archiv/Druck-Datum
Datum an dem der Beleg gedruckt
      wurde
Beleg-Referenz
Zeigt die Belegreferenz im Archiv
      an
Beleg-Klasse
Zeigt die Belegklasse an
Inhalt
Zeigt den Typ des Belegs
      an
Suchoption
Name
Beschreibung
Postfach
Fa-Id
FA-MndNr
Funktionen
Name
Beschreibung
Anlagen
Fügt
      dem Datensatz einen Anhang hinzu

---

## Belegkopie (Speichern unter)

Belegkopie (Speichern unter)
Die „Speichern unter“ Funktion nutzt die
Schnellerfassung, um bequem Belege, die schon einmal erfasst worden sind, als
Vorlage für einen anderen Beleg zu nutzen. In den obigen Beschreibungen ist
mehrfach darauf hingewiesen worden, dass es sich nicht um eine Vorgangskopie
handelt, sondern nur um eine Vorlage für einen neuen Beleg.

---

## Benutzbare Fonts

Benutzbare Fonts
Hier legt man die Schriftarten an, die bei Verwendung
der Fonttabelle zur Verfügung stehen sollen. Die Bezeichnung sollte so gewählt
sein, dass man die Schriftart bei der späteren Auswahl sofort erkennt. Den Font
sollte man auch hier über die F3 Auswahl, die den Schriftart Dialog öffnet,
auswählen.

---

## Bereiche in OLAP

Bereiche in OLAP
Nach dem Start des AddIns finden Sie alle Felder der
Auswahlliste in einer Sammlung nicht zugeordneter Felder. Sie können diese nun
zu Anzeige in einen der vier Bereiche ziehen oder an die Bereichsposition in der
Pivottabelle.
Es gibt 4 Bereiche an denen sich Ihr Feld befinden
kann:
Filterbereich
Dieser Bereich gibt den Filter für die Anzeige an.
Neben den in der Auswahlliste vordefinierten Filtern der Daten können hier
zusätzliche Einschränkungen für die Anzeige vorgenommen werden.
Spaltenbereich
Dieser Bereich enthält alle Felder, die in den Spalten
dargestellt werden.
Hinweis: Sie sollten darauf achten hier Felder zu
wählen, die nicht zu übermäßig vielen Spalten führen, da solche Ansichten
gewöhnlich durch die horizontale Darstellung der Überschrift unleserlich werden.
Zeilenbereich
Im Zeilenbereich finden sich die Felder, die in den
Zeilen dargestellt werden.
Datenbereich / Summenbereich
Im Datenbereich finden Sie Felder, die die
eigentlichen Daten entha
[...]


---

## Bereichsauswahl / Filter

Bereichsauswahl / Filter
Umfasst Tabelle, Rtf-Spalte, Pk-Wert und
"Konvertiert?".

---

## Übersicht

Übersicht
In der Übersicht finden sie, ähnlich wie bei dem
Dashboard, eine verbilderung der firmenbezogenen Daten. Man kann hier die
Auswertung der Daten selber festlegen.

---

## Beschreibung der POS- Kassenfunktionen

Beschreibung der POS- Kassenfunktionen
Innerhalb eines POS- Erfassungsvorgang stehen weniger
Funktionalitäten/Module als bei der Tresenkasse zur Verfügung.
Das Modul selbst befindet sich im Hauptauswahlmenü:
Warenwirtschaftssystem/Barvorgänge/POS-Kasse.
Die Funktionen zur Bearbeitung stehen in der Option
Box zur Verfügung.
Hier werden abhängig vom Fortgang der
Vorgangsbearbeitung die Funktionen unterdrückt oder angezeigt.
So kann es vorkommen, dass nicht alle Funktionen, die
unten beschrieben werden, auch aktuell auf Ihrem Bildschirm angezeigt
werden.
Kundennummer ändern (SF2),
d.h. es ist zu Beginn eines Vorgangs möglich, diesen
Vorgang verschiedenen Kunden zuzuordnen. Standardmäßig wird der Barverkaufskunde
vorbelegt (dieser ist in den Kasseneinstellungen hinterlegt).
Belegwährung ändern (SF5),
d.h. es ist möglich, zu Beginn eines Vorgangs die
Währung festzulegen, in der die Positionen erfasst werden sollen. Diese ist
standardmäßig mit der Währung des Kunden identisch.
Die
[...]


---

## Besondere Fehlerursachen

Besonde
r
e Fehlerursachen

---

## Besonderheiten beim Kopieren:

Besonderheiten beim Kopieren:
Es können mehrere Belege in einem Durchgang kopiert
werden, bei mehr als einem Quellbeleg kann dann aber keine Belegnummer
vorgegeben werden.
Hinweis:
Nur beim Kopieren werden die Originalbelege schon vor
dem Starten mit F9 vorsortiert. Bei einer umfangreichen Auswahl kann diese
Vorsortierung bei Bedarf mit der ESC Taste abgebrochen werden.
Stornobelege
Stornobelege sollen den Originalbeleg umkehren, daher
wird bei dieser Umwandlungsfunktion das Häkchen ‚1 zu 1’ stets aktiviert, es
kann nicht abgeschaltet werden.
Bei Problemen mit dem Lieferdatum und der Periode
benutzen sie die Zusatzseite zur Problemlösung.

---

## Besonderheiten der Periodenbehandlung

Besonderheiten der Periodenbehandlung
Bei einigen Umwandlungsfunktionen wird eine weitere
Dialogseite angezeigt („Prüfe Lieferdatum / Perioden). Es handelt sich hierbei
um Funktionen, die im Hinblick auf die Perioden- und Datumszuordnung Belege
weitgehend identisch zum Original erzeugen (Kopieren / Stornobelege /
Gutschriften). Da es bei dieser Art Umwandlung häufig zu Problemen mit
abgeschlossenen Perioden als auch Inventuren kommt, kann man mit dieser
Zusatzseite Lösungen für die Problemfälle bereitstellen:
Achtung: Die Einstellungen dieser Seite werden nicht
gespeichert!
Die Behandlung von Problemen mit dem Lieferdatum sowie
von Perioden ist standardmäßig derart eingestellt, dass die entsprechende
Funktion den Beleg nicht bearbeitet und in einem zusammenfassenden Protokoll die
Unstimmigkeiten festgehalten werden. Mit der jeweils mittleren Einstellung kann,
nur bei Problemfällen, ein Ersatzwert festgelegt werden.
Die jeweils dritte Einstellung (immer... nehmen) setzt
für
[...]


---

## Bewegungscode (wbc_BewCode)

Bewegungscode (wbc_BewCode)
Das Feld wbc_BewCode findet sich in der View
AMIC_V_Warenbewegung_info
.
Bewegungscode
Der wbc_BewCode beschreibt die Herkunft der
      Warenbewegung. Während Codes kleiner 10 die eigentliche Tätigkeit
      beschreiben, kennzeichnen Codes zwischen 11 und 19 die jeweiligen
      Folgeschritte. Die Codes zwischen 21 und 29 sind für die Rückabwicklungen
      reserviert. Die Codes 10 und 20 stehen für Einkauf bzw. Verkauf.
1
Vorverkauf
2
Voreinkauf
3
Einlagerung
4
Kommission
10
Einkauf
11
Vorverkauf Abholung
12
Voreinkauf Anlieferung
13
Einlagerung
      Vereinnahmung
14
Kommission Verkauf
20
Verkauf
21
Vorverkauf Rücknahme
22
Voreinkauf Rückgabe
23
Einlagerung Abholung
24
Kommission Rücknahme

---

## Bruch-Ware buchen

Bruch-Ware buchen

---

## Buchstellen

Buchstellen
Das Buchstellenexportsystem unterstützt die
Möglichkeit, Bewegungsdaten von Personenkonten an eine übergeordnete Stelle zur
Verarbeitung weiter zu leiten.
Es werden hierbei warenwirtschaftliche wie auch
finanztechnische Belege des Personenkontos verarbeitet, wobei jeweils in einer
privaten Einrichtung festgelegt werden kann ob und welche Belege mit
berücksichtigt werden sollen.
Die Verarbeitung ist an bestimmte Kennzeichen im
Kundenstamm gebunden, und wird nur auf Wunsch angestoßen.
Alle Buchstellenexportobjekte werden direkt nach der
Erzeugung an ein Buchstellenrelaissystem abgegeben, dieser Vorgang läuft
vollständig automatisch ab, und wird über einen Webservice abgewickelt. Eine
Internetverbindung ist hierzu aber notwendig.
Im Referenz-ERP System kann beim Kunden hinterlegt werden,
unter welcher Buchstelle der Kunde geführt wird (siehe dazu Kundenstamm). Im
zugehörigen Buchstellenstamm kann pro Buchstelle eingestellt werden, ob ein
Buchstellenexport erfolgen soll u
[...]


---

## Cache Informationen

Cache Informationen
Hauptmenü
Systempflege
Sonstige
Cache Informationen
oder Direktsprung
[
CACHE
]
Diese Auswahlliste hat ausschließlich informatorischen
Charakter. Da Referenz-ERP vollautomatisch die Client-Caches organisiert stehen somit
auch keine Bearbeitungsmöglichkeiten zur Verfügung.
Felder
Bedeutung
Bemerkung
Cache
Der
      numerische Define
Cache-Define
Die
      textuelle Entsprechung des numerischen Defines
Externe
      Modifizierung
Zeitpunkt
      der Aktualisierungs-Anforderung durch einen externen
      Referenz-ERP-Clienten
Eigene
      Abgleichung
Zeitpunkt
      der Abgleichung der Cache-Aktualisierung durch den eigenen laufenden
      Referenz-ERP-Clienten
Ist
      der Zeitpunkt ROT eingefärbt bedeutet dies das der eigene Client die
      angeforderte Cache-Aktualisierung noch nicht vollzogen hat.
Kurzname
Der
      Kurzname des anfordernden Referenz-ERP-Bedieners.
Anwendung
Siehe
      Bemerkung
Der
      anfordernde Client befand sich in der  Programmumgebung Anwendung,
[...]


---

## Chefcockpit / Kennzahlenanalyse

Chefcockpit / Kennzahlenanalyse
Kennzahlen werden eingesetzt, um Geschäftsprozesse
messbar und damit verbesserungsfähig zu machen. Sie dienen zur Beurteilung von
Unternehmen sowie der Festlegung von Unternehmenszielen.
In Referenz-ERP kann man sich über ein Kennzahlensystem
sogenannte Chefcockpitauswertungen definieren, die anhand der in Referenz-ERP
existierenden Daten die Kennzahlen errechnen und in Spalten mit Vorjahres- oder
Periodenvergleich oder mit konstanten Vergleichszahlen ausgeben. Es ist möglich
sich Chefcockpitauswertungen wie
oder
zu definieren. Bei der Definition müssen zuerst die
Spalten definiert, anschließend die Kontenlisten bzw. die externen Kontenlisten
und am Ende die Zeilen.

---

## CONTINUE ON ERROR

CONTINUE ON ERROR
Purpose
Veraltet. Siehe:
SET ERROR CONTINUE
Siehe auch
CONTINUE, SET ERROR

---

## Crystal Report

Crystal Report
Crystal Report ist ein voll in Referenz-ERP integriertes
Analysewerkzeug. Datenbereitstellung und Archivierung werden von Referenz-ERP
übernommen. Neben den Standard-Reporten können auch eigene Reporte in das System
integriert werden.

---

## Darstellung der Blätterbuttons

Darstellung der Blätterbuttons
Will man Blätterbuttons in dieser Form
darstellen und keine Bitmaps auf die Buttons
legen, lässt sich dies mit einem einfachen Trick lösen: Man wählt als Schriftart
„Webdings“ aus. Dort werden dann kleine Grafiken als Zeichen ausgeben.
Die Zeichen für die Buttons sind:
9 für Anfang
3 für Links
4 für Rechts
: für Ende
Diese müssen dann einfach unter Beschriftung
eingetragen werden.

---

## Darstellung mit HTML Anlagen

Darstellung mit HTML Anlagen
Sollen nun die im Notiz Bereich eingetragenen
Informationen in schöner Tabellenform dargestellt werden, so kann dieses per
HTML Anlage erfolgen. Das Ergebnis sieht dann wie folgt aus:
Und eine Rechnungsanzeige dann :
Einzurichten ist dieses wie folgt :
Der Tabreiter 3 einer Unterdatendarstellung oder eines
Darstellung von mehreren Datensätzen in einem Kontakt muss dann mit einem HTML
Dateiname versehen werden.
Des weiteren muss in dem Tabreiter 4 der Select
Bereich als Einzelnamenbereich angelegt werden, also ohne Notiz Alias.
Im zugehörigen Feldzuordnungsbereich ist nun eine
genaue Angabe der Felder vorzunehmen, die in die HTML Anlage eingespeist werden
sollen.
Hierbei ist nun der Datenbankname der Orginal
Datenbankname, Label ist die Überschrift in der HTML Tabelle, die Sortierung ist
größer 100 zu wählen, um von den anderen Einrichtungen unterschieden zu werden
und die Ausrichtung ist entsprechend der Ausrichtung in der HTML Tabelle zu
wählen,
[...]


---

## Darstellungsregister

Darstellungsregister
Das Darstellungsregister ist in zwei große Blöcke und
einen Block mit der Hilfe-Funktion eingeteilt. Der linke Block mit den
Funktionen
Sortierung
,
Farben
, usw. bezieht sich jeweils auf eine
Anwendungsvariante, der zweite Block gilt für die Auswahlliste allgemein. Diese
Einstellungen werden gespeichert und stehen immer wieder so zur Verfügung. Die
Funktionen zum Sortieren, Gruppieren und Filtern in der
Datentabelle
werden hingegen nicht
gespeichert und bleiben nur so lange aktiv, solang man in der Variante
steht.
Bedeutung
Sortierung
Siehe „
Sortierung der
      Auswahlliste
“
Farben
Siehe „
Farbgestaltung der
      Auswahlliste
“
Spalten
Siehe „
Feldauswahl der
      Auswahlliste
“
SQL-Variablen
Siehe „
SQL-Variablen in der Auswahlliste
      verwenden
“
Summen
Siehe „
Summierung in der
      Auswahlliste
“
Vorbelegungen
Die
      Funktionalität „
Vorbelegungen
“ steht bisher nur
      für das auf der neuen Auswahlliste basierende Archiv und den au
[...]


---

## Das Export-Excel wird generiert, abgespeichert und geöffnet.

Das Export-Excel wird generiert, abgespeichert und geöffnet.

---

## Datenbank-Proceduren

Datenbank-Proceduren
In eigenen Anwendungen können Sie die
Datenbank-Funktion
Fehlerprotokoll
einsetzen.
In Datenbank-Verwendungen bietet sich die
Datenbank-Funktion
amic_exception
an.

---

## Datenbankrelationen

Datenbankrelationen

---

## Datenbankumstellungen

Datenbankumstellungen
Es kann vorkommen, dass das Datenbanksystem einen
neuen Versionsstand benötigt, dazu werden in diesem Bereich die notwendigen
Schritte erläutert und ein Kochrezept zur Umstellung angegeben.
Die Funktion überprüft dabei die folgenden Bereiche
auf Konsistenz und korrekter Einrichtung:
-
Vergleich von Hauptspeicher zu Datenbankgröße
-
Vergleich von lizensierten Benutzer zur Prozessorarchitektur
-
Vergleich von Plattenplatzausnutzung zur Datenbankgröße.
Weiterhin bietet das System dann die Möglichkeit der
Umstellung aller Datenbanken auf die Sybase 17 Struktur, hierzu ist immer ein
entladen und erneutes beladen der Datenbank notwendig.
In diesem Bereich kann über die Methoden:
-
In-Memory Umwandlung
-
Umwandlung mit Auslagerungsdateien
gearbeitet werden, wobei der In – Memory Bereich als
Standard genutzt wird.

---

## Datenbankzugriffe

Datenbankzugriffe
Routinensammlung aller Datenbankzugriffsroutinen.

---

## Datenherkunft SQL oder Relation

Datenherkunft SQL oder Relation
Wenn man in AIS diverse Felder informatorisch anzeigt,
kann man sich überlegen, ob man diese per Datenherkunft SQL ausliest oder per
Datenherkunft Relation. Wird die Datenherkunft SQL gewählt, so wird für jedes
Feld dieses Typs ein SQL ausgeführt. Wählt man als Datenherkunft Relation aus,
wird nur einmal pro Relation das SQL ausgeführt. Man kann sich also vorstellen,
dass dann bei vielen Feldern die Datenherkunft Relation besser und schneller
ist.
Selbst wenn ein SQL die Daten erst zusammen baut
„select trim(a.AdressVorname + '  '  a.AdressName) as InfoKundName
from“, so kann man dies auch geschickt lösen, indem man sich vorher ein View
aufbaut, das alle Informationsfelder enthält. Als Relation trägt man dann den
Namen des Views ein.

---

## Datenpflege

Datenpflege
Daten müssen in Referenz-ERP korrekt gepflegt sein, damit
diese auf der App angezeigt werden können. Die folgenden Punkte sind zu
beachten:

---

## Datentabelle

Datentabelle
Die Datentabelle enthält zusätzliche Funktionen:
Gruppieren:
Um die Daten eben schnell mal zu gruppieren, kann man
in die Titelzeile klicken und die so ausgewählte Spalte in den Bereich ziehen,
der mit „
Zur Gruppierung Spalte hier ablegen“
gekennzeichnet ist. Dann
ändert sich das Erscheinungsbild wie folgt:
In diesem Beispiel wurde der Kontotyp „Typ“ in die
Gruppierungsleiste gezogen. Man kann nun durch einen Mausklick auf das Kreuz
ganz links (oder durch drücker der Plus/Minus Tasten auf dem Nummernpad) die
Bereiche aufklappen.
Um die Gruppierung wieder zu entfernen, zieht man die
Spalte wieder zurück in die Datentabelle.
Hinweis:
Wird die Funktion
„Gruppieren-Bereich“ weggeschützt, so wird der Bereich „Zur Gruppierung Spalte
hier ablegen“ für diese Bedienerklasse nicht mehr angezeigt.
Spalten fixieren:
Mit dem Schlüsselwort FIXCOL können bereits die Anzahl
der Spalten im SQL-Text festgelegt werden, die beim horizontalen Scrollen nicht
bewegt werden, also imme
[...]


---

## Deaktivieren von allen Events (nur für Entwickler)

Deaktivieren von allen Events (nur für Entwickler)
Diese Funktion deaktiviert alle aktivierten
Events.

---

## Den SQL Remote-Nachrichtenagent als Dienst in Sybase Central anlegen

Den SQL Remote-Nachrichtenagent als Dienst in Sybase Central anlegen
Zum Anlegen des Nachrichtenagenten dbremote als
Service / Dienst unter Windows gehen Sie bitte wie folgt vor:
1.
Starten Sie Sybase Central unter: ..\Aeins\bin64\scjview.exe
2.
Verbinden Sie sich mit der gewünschten Datenbank
3.
Doppelklicken Sie auf SQL Anywhere 17
4.
Wählen Sie die Registerkarte „Dienste“
5.
Klicken Sie auf einer freien Stelle auf der Registerkarte „Dienste“ mit der
RECHTEN Maustaste
6.
Wählen Sie „Neu“
à
„Dienst“. Es
öffnet sich der Assistent zum Erstellen eines neuen Dienstes
7.
Geben Sie einen Namen für Dienst an der gestartet werden soll und gehen
anschließend auf „Weiter“
8.
Markieren Sie nun „SQL Remote-Nachrichtenagent“ in der Liste aus und gehen
anschließend auf „Weiter“
9.
Klicken Sie nun auf durchsuchen, wählen die Datei „dbremote.exe“ aus dem
„..\Aeins\bin\“ Verzeichnis aus und gehen anschließend auf „Weiter“
10.  Als
Parameter wird dem Dienst der Speiche
[...]


---

## Dialog „Traceeintrag“

Dialog „Traceeintrag“
Mit Hilfe des Dialoges können Trace-Einträge gesondert
in Augenschein genommen werden, insbesondere lange „SQL-Ausdrücke“ können so
inspiziert werden.
Maskenfeld
SQL
      Ausdruck
Plan
Wer
Zeit
Maske
Verbrauch
Err
Status
CurNo
Id
Die Maskenfelder entsprechen den
Auswahllisten-Feldern.

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

[...]


---

## Die Grundmaske

Die Grundmaske
Das Aussehen der Maske hängt sehr stark von der
angewählten Umwandlungsfunktion ab. Daher wird zur Orientierung die aktuelle
Funktion in der Überschrift in großer Schrift dargestellt.
Darunter, oben auf dem Register „Allgemein“, steht
immer die Anzahl der aktuell ausgewählten Vorgänge. Zusätzlich kann über die
Einrichterparameter
Bedienerklassenabhängiges Verhalten beeinflusst werden.
Wir unterscheiden Eingabefelder und
Einstellfelder:
In Eingabefeldern werden variable Daten erfasst (z.B.
das Belegdatum). Sie werden dynamisch vorbelegt.
Einstellfelder (‚Häkchen’ und Knöpfe) modifizieren das
Verhalten bei der Umwandlung oder wählen zusätzliche Funktionen aus. Diese
Einstellungen werden bedienerspezifisch und für
jede Umwandlungsfunktion
gespeichert.
Hinweis:
Da die Einstellungen für jede Funktion extra
gespeichert werden, wird man anfänglich häufiger Änderungen der Einstellungen
vornehmen und sollte daher verstärkt die Richtigkeit der Angaben überprüfen.
Einstell
[...]


---

## Die Installationsprozedur

Die Installationsprozedur
Die Installationsprozedur umfasst folgende
Bereiche:
•
Analysieren des Zielsystems auf die Installationsfähigkeit
•
Vorbereiten des Zielsystems
•
Kopieren der Programme und Dateien
•
Anpassen der Registrierungsinformationen
•
Umstellen der Datenbanken
•
Eintragen von Referenz-ERP Systeminformationen
•
Vorbereiten der Client-Arbeitsplätze
•
Installationsüberprüfungslauf
•
ODBC Abgleich

---

## Directoryaufbau

Directoryaufbau

---

## Die wesentlichen Einstellungen im Detail

Die wesentlichen Einstellungen im Detail
Belegdatum:
Das Belegdatum ist bei den meisten Umwandlungen
eingebbar.
Unterklasse:
Bei Belegumwandlung in dem Zielvorgang die
Vorgangsunterklasse 0 gewählt. Bei gesetztem Häkchen kann eine abweichende
Vorgangsunterklasse angegeben werden. Löscht man das Häkchen, so bleibt bei der
Umwandlung die Unterklasse des Quellbelegs erhalten (sofern für die Zielklasse
eine entsprechende Unterklasse eingerichtet ist!). Die hierfür früher zuständige
Einstellung unter SPA (‚Erhalten der Unterklasse bei Umwandlung’) wird nur noch
als Vorbelegung beim ersten Anwenden einer Umwandlungsfunktion herangezogen.
Nachlauf:
Bei sehr vielen Umwandlungsfunktionen wird eine
Nachlauffunktion angeboten, mit deren Hilfe die umgewandelten Zielbelege bequem
weiterverarbeitet werden können. Um Blockierungsprobleme mit dem Mandantenserver
zu verhindern kann die Einstellung des
Steuerparameters
800
geändert werden.
Korrektur:
Nach der Umwandlung werden alle Zielbelege
[...]


---

## Dokumentenverwaltung- Datentabelle

Dokumentenverwaltung-
Datentabelle
Aufbau der Datentabelle wird im Standard durch die
Variante AW_FA_VIEW.VIEWDIALOG (*) vorgegeben. Durch das Konzept der Ableitung
besteht die einfache Möglichkeit Privatisierungen vorzunehmen.
Die Datentabelle unterstützt den Import von Mails aus
den aktuellen Desktop-Outlook-Versionen per „Drag&Drop“.
Die Datentabelle unterstützt den Import von Dateien
aus dem Windows-Explorer; soweit es sich um Dateien handelt die den
Mime-Anforderungen von Referenz-ERP genügen.
(*)Variante AW_FA_VIEW.VIEWDIALOG
<?xml version="1.0"
encoding="utf-8" standalone="yes"?>
<Description Name="AW_FA_VIEW.VIEWDIALOG"
RowHeight="22" Version="">
<Field Name="fa.fa_mime" Caption=" "
Mime="true" WidthDisplay="22" />
<Field Name="fa.fa_kundennummer"
Caption="Kundennummer" />
<Field Name="fa.fa_klasse"
Caption="Klassifizierung" Format="af_fa_klasse" Sql="isnull(fa.fa_klasse,0)"
/>
<Field Name="fa.fa_belegtyptext"
Caption="Belegtyp" />
<Field Name="fa.fa_belegnummer"
Captio
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
[...]


---

## Dokumentenverwaltung- Multifunktionsleiste

Dokumentenverwaltung-
Multifunktionsleiste
Das Kontext-Menü und die Multifunktionsleiste ersetzen
die sonst übliche Funktionsübersicht in A:eins.
Die Multifunktionsleiste ist in Abschnitte unterteilt,
denen im Standard Funktionen wie folgt zugeordnet sind:
Abschnitt
Funktion/[Tastatur]/Icon
Beschreibung
Dokument
Rücktaste [ESC]
Unterstützung verlassen der Maske
      auf Touchscreens
Anzeigen [CF12]
Ruft
      den externen Viewer auf, den Windows für die Anzeige vorgesehen
      hat.
Anhänge … [CF11]
Sucht die zugehörigen Anhänge
      heraus, und stellt diese in einem extra Fenster dar.
Senden an… [F9]
Formulararchiv Senden
      An-Dialog
Archiv Mail
      Versand
PDF
      Signieren
Unterstützt PDF-Signierung durch
      Signotect-System.
Hinzufügen [F8]
Formulararchiv-Stammdatenpfleger-Funktion
      Neu/Einfügen
Archiv – Dokumente
      hinzufügen
Drucken
PDF-Dokument drucken
Übergibt die selektierten Dokumente
      zum
PDF-Drucken
.
Funktion
Stammänderung [F5]
Form
[...]


---

## Dokumentenverwaltung- Ordner und Filter

Dokumentenverwaltung- Ordner
und Filter

---

## Dokumentenverwaltung- Ordner

Dokumentenverwaltung- Ordner
Unter der Rubrik „Ordner“ befinden sich die
„Archiv-Belegklassen“ wiederum jeweils unterteilt nach
„Archiv-Klassifizierungen“.
Durch Aktivierung einer Belegklasse werden nun die
Daten neu geladen - unter der Einschränkung dass es sich dabei nur um solche
handelt die das Kriterium der Belegklasse erfüllen.
Somit es schnell und einfach möglich bestimmte
Belegklassen zu recherchieren.
Das funktioniert ganz genauso mit einer unterhalb
einer Belegklasse ausgewählten Klassifizierung. Die automatische Eingrenzung
berücksichtigt dann Belegklasse UND Klassifizierung.
Dass eine Ordner-Eingrenzung „aktiv“ ist wird in der
Dokumentenverwaltung- Statuszeile
signalisiert.
Ordner-Eingrenzungen werden nicht sitzungsübergreifend
gespeichert. Wird die Dokumentenverwaltung beendet, werden die Selektionen
zurückgesetzt.
Mittels
lässt sich die Ordner-Auswahl
rücksetzen.

---

## Dokumentenverwaltung- Statuszeile

Dokumentenverwaltung-
Statuszeile
In der Statuszeile finden sich Informationen darüber
a)
welche Archiv-Ansicht für diesen Dialog datentechnisch maßgeblich ist.
b)
Wie viele Einträge sich in der Datentabelle befinden
c)
Ein Fortschrittsbalken der über aktive Datentabellen-Ladeprozesse informiert
d)
Während eines unter c) erwähnten Ladeprozesses – die je nach Datenaufkommen bzw.
Datenkomplexität andauern können – besteht für den Anwender die Möglichkeit den
Vorgang abzubrechen und ggf. anderweitig fortzufahren.
Wenn sich die Datenbank noch
in der Aufbereitungsphase befindet, also noch keine Daten abliefert, dann kann
es ein paar Sekunden dauern, bis die Software reagiert.
Wurde abgebrochen dann
wechselt die Anzeige unter b) zu „xxxx Einträge von?“

---

## Dokumentenverwaltung- Vorschau

Dokumentenverwaltung-
Vorschau
In der Vorschau werden Archiv-Dokumente
dargestellt.
Die für die Vorschau vorgesehenen Elemente sind über
Mimetypen in Referenz-ERP
einsehbar.
Zurzeit ist es möglich
-
PDF-Dokumente,
-
Referenz-ERP-ASCII-Drucke
-
Bildelemente
-
Word- und Excel-Dokumente (außer *.doc)
-
Html-Dokumente
-
sowie Markdown-Dokumente
des Referenz-ERP-Archivs zu visualisieren.
Die Vorschau ist von der Datentabelle durch einen
Teiler getrennt, welcher mit der Maus auf die gewünschte Position verschoben
werden kann.
Die Vorschau kann mittels der Funktion „Vorschau“
aktiviert und deaktiviert werden.
Für nicht visualisierbare Dokumente wird in der
Vorschau ein Hinweis ausgegeben.
Bei Problemen mit dem Schieber der Vorschau lässt
sich die Standard-Darstellung dadurch erreichen, dass man mit gedrückter
Shift-Taste die Funktion „Vorschau“ ausführt.

---

## DrillDown

DrillDown
Drilldown ist die Möglichkeit mit einem Click mit der
rechten Maustaste auf einem Datenfeld in der Tabelle Details anzusehen. So
können Sie sich in einer zusammengefassten Ansicht die Herkunft der Summen auf
einen Blick anzeigen lassen oder Felder sehen, die Sie der Übersichtlichkeit
halber nicht als Datenfelder bestimmt haben.

---

## Drucker

Drucker
Über
[OSQL]
können Drucker eingerichtet werden:
Epson_bon.sql
für den Bondruckkanal eines EPSON TM930
      Models.
Epson_schacht.sql
für
      den Bonschachtkanal eines EPSON TM930 Models.
Oki_bon_sql
für
      den Bondruckkanal eines OKI POS90 Bondruckers.
Oki_schacht.sql
für
      den Bonschachtkanal eines OKI POS90 Bondruckers.
Sni_bon.sql
für
      den Bondruckkanal eines SNI ND69 Bondruckers.
Sni_schacht.sql
für
      den Bonschachtkanal eines SNI ND69 Bondruckers.
Star.sql
für
      den Bondruckkanal eines Star-Druckers (dort gibt es keinen
      Schacht).
Dabei ist dann nur eine freie Druckernummer
einzugeben. So entspricht der bon.sql dem Drucker für die Bonrolle und der
schacht.sql dem Drucker für den Schacht.
Bemerkung: Auf der Basisdatenbank existieren die
Einrichtungen für EPSON und SNI-Drucker.
Wenn auch der Bonschacht für Scheckdruck,... genutzt
werden soll, empfiehlt sich folgende Vorgehensweise: in der Druckerzuordnung
muss der Schacht ausgewählt s
[...]


---

## DTA-Archiv

DTA-Archiv
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
DTA-Archiv
Direktsprung
[DTA]
Beim Erstellen einer DTA-Datei werden die Daten in ein
Archiv gestellt, um es zu ermöglichen, den Datenträgeraustausch zu wiederholen,
ohne den gesamten Zahlungsvorgang zu wiederholen. In der  Bereichsauswahl
kann man auswählen, für welchen DTA-Bereich man die Ausgabe wiederholen möchte.
Es wird unterschieden zwischen DTA, DTINT, DTA-Kasse, Auslandszahlungsverkehr
und SEPA-Überweisung.
Vor dem Start des DTA's muss ausgewählt werden, welche
Bereiche wiederholt werden sollen.
Man kann angeben, wann diese hier
zwischengespeicherten Daten wieder aus dem System entfernt werden sollen. Dazu
muss man unter Optionen (Direktsprung
[OPT]
) die Option DTA_Archivwochen
setzen. Trägt man hier eine 0 ein, werden die Daten nicht automatisch gelöscht.
Ansonsten wird nach jedem DTA-Lauf geprüft, ob noch „alte“ Daten vorhanden sind
und diese werden dann nach Ablauf der eingestellten Wochen - ab Erstellda
[...]


---

## DTA Konto / BLZ / Empfänger

DTA Konto / BLZ / Empfänger
Hier bitte die hauseigene Bankverbindung sowie der
Kurzbezeichnung der Bank hinterlegen.

---

## Dta Ausgabe Pfad

Dta Ausgabe Pfad
Hier wird das Verzeichnis hinterlegt, in dem die
DTA-Daten erzeugt werden soll. Das kann z.B.  ‚a:’ ‚ sein, wenn die Daten
direkt auf einem Datenträger erstellt werden sollen. Es darf aber auch durchaus
ein Verzeichnis auf einer Festplatte sein, falls die Ergebnisdateien (
DTAUS1.TXT bzw. DTINT1.TXT ) von anderen Programmen ( DFÜ etc )
weiterverarbeitet werden sollen.

---

## DT- Int Verfahren benutzen

DT- Int Verfahren benutzen
Das DT-Int Verfahren  bietet beim DTA-Austausch
erweiterte Möglichkeiten zur Steuerung  der Valuta. Es ist jedoch nur auf
bankinterne Konten begrenzt. Bei der Erzeugung der DTA Datenträger können keine
bankfremden Bewegungen  ( Lastschriften / Bankeinzüge ) außerhalb der
hauseigenen Bank berücksichtigt werden.

---

## Durchführung der Umwandlung

Durchführung der Umwandlung
Nach Auslösen der Startfunktion und Bestätigung der
Startabfrage wird die Umwandlung durchgeführt. Die Umwandlung kann zu jeder Zeit
mit der ESC – Taste unterbrochen werden. Die Forschrittsanzeige in Prozent der
Gesamtanzahl der (Quell) – Belege hilft Ihnen bei der Abschätzung der
Gesamtzeit!

---

## Eingaben in der Zahlungsmaske

Eingaben in der Zahlungsmaske
In der Eingabemaske der Zahlungsmaske, werden je nach
ausgewählter Funktion die Maskenfelder zur Eingabe freigegeben, in denen eine
Eingabe erwartet wird.
Die übrigen Felder sind invertiert dargestellt; eine
Eingabe ist also nicht möglich.

---

## Eingangsmappe

Eingangsmappe
Hauptmenü
Finanzbuchhaltung
Erfassung
Eingangsmappe
Direktsprung
[EMA]
Hierbei handelt es sich um eine Vorerfassung von
Finanzbuchhaltungsbelegen vom Typ Eingangsrechnung oder -gutschrift. Diese
vorerfassten Belege sind im Allgemeinen Vorgänge, die inhaltlich noch zu klären
sind (z.B. vom Sachbearbeiter noch abzuzeichnen) und deshalb noch nicht in der
Primanote erfasst werden können. Hierauf kann sowohl in der Belegerfassung der
Finanzbuchhaltung als auch in der Vorgangserfassung für Klasse 1700
(Eingangsrechnung) bzw. 1800 (Eingangsgutschrift) zugegriffen werden.
In der Belegerfassung der Fibu kann man auf der
Position „Belegdatum“ mit
F3
die Eingangsmappe aufblättern. Dort kann der
gewünschte Beleg ausgewählt werden. Die Felder werden entsprechend der
Vorerfassung vorbelegt; im Betragsfeld muss jedoch die Eingabe wiederholt
werden.
Im Bereich der Vorgangserfassung lässt sich die
Eingangsmappe auf dem Feld „Liefer./Bez.“ aufrufen. Nach Auswahl des Beleges aus
[...]


---

## Eingegangene Post löschen

Eingegangene Post löschen
Hauptmenü
Büro und Internet
Büroumgebung
Referenz-ERP Post
Direktsprung
[POST]
Nach Aufruf der Funktion „
Löschen
“
F7
erscheint folgende Maske:
Beim „
Löschen
“
F7
wird der Datensatz physikalisch gelöscht
und kann nicht wieder hergestellt werden.

---

## Eingehende Telefonie

Eingehende Telefonie
Wesentlich dabei ist, dass das Telefonie-System die
eingehende Nummer auf Wunsch veröffentlich. So besitzen fast alle Systeme eine
Möglichkeit, die Nummer z.B. in eine Datei wegzuschreiben. Diese Nummer muss nun
Referenz-ERP mitgeteilt werden.
Durch dieses Verfahren benötigt Referenz-ERP selber keine
spezielle Unterstützung der Telefonie-Systeme mehr.
Es muss eine j-Datei geschrieben werden die die Nummer
ermittelt und diese in der Variablen LDB_TRANSFER$VC zur Verfügung stellt.
Dieses lässt sich auch ohne Telefonie-System
bewerkstelligen, man erhält somit die Möglichkeit, das sonstige System
Referenz-ERP-seitig zu testen.
Exemplarisch erstellt man also mit dem Notepad eine
Datei namens nummerholen.j im Referenz-ERP-Bin-Verzeichnis mit folgendem Inhalt
cat LDB_TRANSFER$VC "0170111222333444"
Weiterhin wird an Hand dieser Nummer von Referenz-ERP mit
dem SQL
CREATE PROCEDURE
AMIC_TAPI_KUNDID(
IN
in_Telefonnummer
varchar
(64) )
result
(
kundid
integer
)
BEGIN
select distinct
ks.kundid
from
[...]


---

## Einstellung eines Statements in die Replikation

Einstellung eines Statements in die Replikation
Grundsätzlich muss man hier unterscheiden, ob es sich
um strukturverändernde Befehle ( alter | create | drop) oder um datenverändernde
Statements handelt. Strukturverändernde Befehle müssen immer auf allen
Datenbanken der Replikation ausgeführt werden. Dafür existieren zwei
Möglichkeiten dies der Replikation mitzuteilen:
1)
Wenn der Steuerungsparameter 851 „Passthrough aktivieren“ auf
Ja
steht
wird mit der Datenbankfunktionalität
Passthrough
der Befehl automatisch von Referenz-ERP
weitergereicht.
2)
Wenn der Steuerungsparameter auf
Nein
steht, werden strukturverändernde
Befehle nicht mehr direkt ausgeführt und zwar auch nicht auf der initiierenden
Datenbank. Soll ein Befehl trotzdem weitergeleitet werden, so kann man in Referenz-ERP
(z.B. unter OSQL)  dem Befehl ein Sternchen
*
voranstellen. Dann wird dieser Befehl so
verarbeitet, als ob der Steuerungsparameter auf
Ja
steht. Beispiel:
*
create table admin.MusterTabelle
(Musterspalte1
[...]


---

## Einstellung hier

Einstellung hier
Diese Standardeinstellung grenzt die zu übertragenden
Belege nur nach Fälligkeit und / oder Konto ein.
Hinweis:
Die drunter liegende Auswahlliste wird hierfür
nicht ausgewertet
!!! Diese Eingrenzung ist immer dann ratsam, wenn man
sämtliche aktuellen Belege auswählen möchte. Eine zu enge ( unbeabsichtigte)
Eingrenzung  durch die vielfältigen Möglichkeiten der Auswahlliste birgt
auch das Risiko der Ausgrenzung bestimmter Belege von der Übertragung !

---

## Einzahlung

Einzahlung
Um eine Einzahlung vorzunehmen wird ein Gesellschafter
in der Auswahlliste ausgewählt mit
F5
zum
Bearbeiten
geöffnet und die
Funktion
Einzahlung
F8
ausgewählt.
Die Funktion
Einzahlung
F8
öffnet folgende Eingabefelder:
Felder
Wert
      der Einzahlung
In
      dieses Feld wird der Wert der Einzahlung eingetragen
Einzahlungsdatum
Hier
      wird das Einzahlungsdatum hinterlegt.
Bemerkung zum Vorgang
Hier
      kann eine Bemerkung zum Vorgang eingetragen werden. (60
      Zeichen)
Werden diese Einträge gespeichert, erfolgt sofort der
Eintrag der resultierenden Buchung in die Primanota
[PRIMA
]. Der erfolgreiche Eintrag wird mit
dem Status <gebucht> quittiert.
Sollte der Buchungseintrag fehlschlagen, so sind die
Einträge im Gesellschaftsstamm sowie die Berechtigungen des ausführenden
Bedieners zu prüfen.

---

## Erlöskennziffer Kontozuordnung bei Steuersatzänderung

Erlöskennziffer Kontozuordnung bei
Steuersatzänderung
Die zum 01.07.2020 anstehende Änderung des
Steuersatzes von 19% auf 16% (bzw. 7% auf 5%) hat zur Folge, dass auch die
Erlöskennziffer Kontozuordnungen in Referenz-ERP geändert werden müssen.
Schritt 1: Konten Anlegen:
Wenn die nötigen Sachkontennummern (i.d.R. Erlöskonto
16% und 5% und Wareneingangskonto 16% und 5%) vorliegen:
Mit dem Direktsprung
[SKS]
mit dem in die Sachkonten. In diesen
sucht man nun nach den Konten, welche angepasst werden müssen (in diesem Fall
19% Erlöskonto). Mit
F5
bearbeitet
man diesen Datensatz nun. Mit der Funktion
„Speichern unter…“
(Shift + F9)
legt man nun eine Kopie des
Datensatzes an. Hier muss lediglich die Kontonummer und die Bezeichnung
angepasst werden. Am Ende speichert man dann mit
F9
.
Schritt 2: Erlöskennziffer Kontozuordnung
anlegen
Nachdem die Konten angelegt wurden navigiert man in
die Erlöskennziffer Kontozuordnung mit dem Direktsprung
[EKZZ]
. Hier wird nun ein neuer Datensatz
ange
[...]


---

## Empfänger für Lieferbelege

Empfänger für Lieferbelege
Hier kann man einen beliebigen Text eintragen.

---

## Entfernungmatrix

Entfer
nungmatrix
Die Entfernungsmatrix ist eine Matrix von Entfernungen
von Anschriften. Diese wird in Referenz-ERP nur von Google implementiert.
Google bietet (Stand Juli 2023) einen Account mit 200$
monatlichem Grundguthaben an, wobei dieses durch Anfragen an den Webservice bis
zu 1000 Stück 10$ kosten.
Dieser API-Key lässt sich mit dem Geodatendienst
kombinieren.
Mehr unter
https://mapsplatform.google.com/pricing/
Die Zugangsdaten zu den Webdiensten werden im
Mandantenstamm
eingepflegt.

---

## EPA der Zahlungsmaske

EPA der Zahlungsmaske
Auf der Zahlungsmaske ziehen folgende EPAs, die auch
für andere Finanzvorgänge ziehen, die über diese Maske abgewickelt werden:
Auf der Zahlungsmaske ziehen folgende EPAs, die auch
      für andere Finanzvorgänge ziehen, die über diese Maske abgewickelt
      werden:
EPA
Beschreibung
Abfrage beim Abschluss der
      Zahlung?
Ist
      dieser EPA auf Ja gesetzt, wird beim Validieren des Zahlungsbetrages bei
      Barvorgängen noch eine Abfrage geschaltet; bei Finanzvorgängen, die auf
      derselben Maske operieren, erfolgt keine Abfrage, da dort der Vorgang
      explizit mit F9 erfolgt.
Soll
      Zahlungsart Scheck aktiv sein?
Durch diesen EPA kann die
      Zahlungsart Scheck deaktiviert werden.
Soll
      Zahlungsart Gutschein aktiv sein?
Durch diesen EPA kann die
      Zahlungsart Gutschein deaktiviert werden
Soll
      Zahlungsart Kreditkarte aktiv sein?
Durch diesen EPA kann die
      Zahlungsart Kreditkarte deaktiviert werden.
Soll
      Zah
[...]


---

## EPAs

EPAs
Folgende EPAs werden bei den verschiedenen Masken der
Tresenkasse ausgewertet:
•
Auf der Hauptmaske der Vorgangserfassung ziehen folgende EPAs:
o
Durch entsprechende
Einstellung kann man alle Abfragen abstellen, so dass sofort nach Validierung
des Zahlungsbetrages der Vorgang ohne weitere Bestätigung abgeschlossen werden
kann. Im Barverkauf gibt es folgende Sonderbehandlungen:
o
befindet man sich im
Barverkauf, ist automatisch die Mehrbelegerfassung angeschaltet, nur über F10
gelangt man aus der Erfassungsroutine
o
befindet man sich im
Bareinkauf / Barverkauf-Gutschrift, ist die Mehrbelegerfassung grundsätzlich
deaktiviert; d.h. nach Abschluss des Beleges wird die Maske automatisch
verlassen
o
wenn der EPA
Im Barverkauf
sofort in Positionsteil
auf Ja gesetzt ist, wird man beim Barverkauf
automatisch in den Erfassungsteil durchgeschaltet.
Auf der Maske Barverkauf/Rechnungen erfassen empfiehlt
es sich, für die Bedienerklasse der Kassierer folgende EPA zu setzen
(Verbess
[...]


---

## Erfassungs- und Bearbeitungsfunktionen

Erfassungs- und Bearbeitungsfunktionen
Umfangreiche Erfassungs- und Bearbeitungsfunktionen
stehen dem Anwender zur Verfügung. Sie werden nachfolgend beschrieben.

---

## Ersetze Font F6

Ersetze Font F6
Mit dieser Funktion lassen sich Schriftarten durch
andere ersetzen. Hierbei kann unterschieden werden, ob man die Ersetzung nur im
Bereich oder im Formular oder aber auch in ALLEN Formularen durchführen
will.
Für die Felder „Suchen nach:“ und „Ersetzen durch:“
stehen jeweils F3 Funktionen zur Verfügung. Für „Suchen nach:“ öffnet die
Funktion eine Itembox mit allen im Formular vorhandenen Bereichen und Varianten
für die bereits Schriftarten festgelegt sind.
Für „Ersetzen durch:“ öffnet die Funktion die Auswahl
der installierten Schriftarten.
Wird das Feld „Suche nach:“ frei gelassen, also leer,
so werden alle leeren Zeilen durch die gewählte Schriftart ersetzt.
Um nun zu entscheiden, wo die Ersetzung durchgeführt
werden soll, werden im unteren Bereich der Maske verschiedene Möglichkeiten
angeboten.
„Ersetzen im Formular“ gibt an das die Schriftart im
Formular stattfinden soll. D.h zum Beispiel leere Zeilen aller Bereiche und
Varianten des gesamten Formulars e
[...]


---

## Erstellung der DTA-Daten

Erstellung der DTA-Daten
In der Funktionsauswahl befindet sich schließlich auch
die auslösende Funktion für die Erstellung der DTA-Dateien:
Hier wird zunächst einer Unterscheidung zwischen der
üblichen Erstellung der Daten und eines eventuellen Wiederholungslaufes
getroffen.
Für die Erstellung der Daten werden zwei Varianten der
Bereichsauswahl  angeboten:

---

## Eventprozeduren

Eventprozeduren
Wenn ein Event einen unerwartet langen Lauf hat, so
dass gleich nach Beendigung das nächste Event startet, dann kann dies zu großer
Last auf der Datenbank führen. Unglücklicherweise lassen sich laufende Events
nicht deaktivieren.
Deshalb gibt es eine Sollbruch-Stelle. In
Eventprozeduren wird zu Beginn eine Abfrage eingebaut, die bestätigt, ob die
Prozedur überhaupt ausgeführt werden soll. So kann sichergestellt werden, dass
der nächste Lauf des Events nur kurz ist und eine Abbruchmöglichkeit vorliegt.
Der Code in der Prozedur sollte in etwa so
aussehen:
DECLARE
NOGO
char
(255);
--Pruefen
ob diese Prozedur laufen darf –
--wenn
dieser Prozedurname nicht in der AMIC_EVT_STOP-Tabelle steht
select
Eventprocedurename
INTO
NOGO
from
AMIC_EVT_STOP
where
Eventprocedurename=
'AMIC_EVT_Backup_Database'
;
if
(SQLSTATE = err_notfound)
THEN
--eigentliche Bearbeitung
END IF
;
In der Eventeinrichtung kann eine Eventprozedur in der
Registerkarte „Sonstiges“ getoppt werden. Die
[...]


---

## F3-Auswahl 2.0 (Itembox)

F3-Auswahl 2.0 (Itembox)
Das Design und der Funktionsumfang der F3-Auswahl
wurden für die 64Bit-Version von Referenz-ERP überarbeitet. Dazu wurde die bereits von
der Auswahlliste 2.0 bekannte Datentabelle mit Filterzeile, die das Suchen in
allen Spalten ermöglicht, verwendet. Um diese Funktionalität zu erhalten, muss
im Bedienerstamm im Feld „Version F3-Auswahl“ der Wert „Feste Fensterposition,
neues Design“ eingetragen werden.
Aufruf:
1)
Bei F3-Auswahlen auf Stammdaten:
In den Feldern, bei denen der
Informationstext „Eine Auswahlliste kann mit F3 aufgerufen werden“, kann man die
Auswahl direkt mit F3 starten. Man kann jedoch auch vorher eine Eingrenzung
eingeben, die dann in der F3-Auswahl sofort angewendet wird. Stellt man der
Auswahl eine Zahl gefolgt von einem Punkt (Z.B. „
2.
Meyer“) vorweg, wird
sofort die entsprechende Variante aufgerufen und der zusätzliche Wert wird
sofort verwendet.
Es gibt zwei Möglichkeiten
die Daten einzugrenzen. Einmal über die Filterzeile, dabei
[...]


---

## Farbe über den Gestaltungsdialog

Farbe über den Gestaltungsdialog
Um zum Beispiel zu vermeiden, dass man jedes Mal eine
private Variante erstellen muss, nur um eine Spalte einzufärben, existiert die
Möglichkeit über den Gestaltungsdialog pro Spalte die Farbe festzulegen. Den
Gestaltungsdialog erreicht man, indem man in der Tabelle in die Überschriftzeile
klickt oder die Funktion „Farbeinstellung“ im Menü der Auswahlliste aufruft. Der
Farbdialog kann für bestimmte Benutzergruppe weggeschützt bzw. freigegeben
werden, indem man der Funktion „Farbeinstellung“ im Menü der Auswahlliste
bestimmte Benutzergruppen zuordnet. Die hier getroffene Einstellung überschreibt
die Einstellung im SQL-Text. Diese Einstellungen werde Systemweit gespeichert,
d.h. sie ist nicht Benutzer bzw. Benutzergruppenabhängig. Wenn im Bedienerstamm
der Schalter „Auswahllistenadministrator“ auf „Temporär“ steht, kann man für die
aktive Referenz-ERP-Sitzung die Einstellungen vornehmen, die jedoch nicht gespeichert
werden.
Wenn zu einer Variante ei
[...]


---

## Farbe im SQL-Text

Farbe im SQL-Text
Im SQL-Text kann pro FIELD – Zeile die Farbe angeben.
Dabei gibt es verscheiden Schlüsselwörter, die alle gleichzeitig in einer FIELD
- Zeile stehen können
STYLE=ITALIC
Die gesamte Spalte wird kursive
dargestellt.
STYLE=BOLD
Die gesamte Spalte wird in
Fettschrift dargestellt. Soll eine Spalte sowohl Fett als auch Kursiv
dargestellt werden, so muss man die FIELD - Zeile wie folgt darstellen:
FIELD
ZahlBankZEmpf,ZahlBankZEmpf,char,20,STYLE=BOLD,STYLE=ITALIC
FGCOLOR=RED
Die Vordergrundfarbe der Spalte
wird rot. Man kann folgende Farben verwenden:
BLAU
GRÜN
TÜRKIS
ROT
MAGENTA
GELB
WEISS
SCHWARZ
GRAU
Ist der Name der Farbe nicht bekannt, so erscheint
diese Farbe nicht.
BGCOLOR=MAGENTA
Die Hintergrundfarbe wird mit diesem Schlüsselwort
gesetzt. Die möglichen Farben sind dieselben wie für die Vordergrundfarben.
COLOR=(bankcolor,1=ROT/WEISS,2=GELB/SCHWARZ,...,9=BLAU/TÜRKIS)
Dies
ist das Schlüsselwort, dass dafür sorgt, dass einzelne Zellen farblich
unterschieden we
[...]


---

## Farbgestaltung der Auswahlliste

Farbgestaltung der
Auswahlliste
Die Spalten der Auswahllisten können farblich
gestaltet werden. Die Farbgestaltung kann auf zwei verschiedene Arten hinterlegt
werden. Farbgestaltung über den Gestaltungsdialog ist nur dann möglich, wenn das
zugrundeliegende SQL-Statement kein UNION und kein GROUP BY enthält. Es wird
dann ggf. der Gestaltungsdialog für Farben ausgeblendet.

---

## Farben per Makro setzen

Farben per Makro setzen
Es ist möglich die Farben von Feldern vom Makro aus
programmgesteuert zu setzen. Dazu gibt es zwei Funktionen.
1.
Setzen der Farbe
dbx_io("SETCOLOR", "Feldname",
"Vordergrundfarbe", "Hintergrundfarbe" )
Dabei muss unterschieden
werden, ob es sich bei dem Feld um ein einzelnes Eingabefeld oder um eine Zelle
in einem Array handelt. Dies wird über den Feldnamen angegeben. Bei einer Zelle
muss man die Zeile in eckigen Klammern direkt hinter dem Feldname angeben.
Beispiel:
dbx_io("SETCOLOR",
"h.KontoNummer$
[5]
", "12", "14" )
Es wir hier die fünfte Zeile
des Feldes h.Kontonummer$ auf die Vordergrundfarbe Rot und Hintergrundfarbe Gelb
gesetzt. Die Nummern sind die Nummern der Basisfarben (Siehe Farbtabelle). Für
einzelne Eingabefelder kann man – im Gegensatz zu Zellen eines Arrays - die
Farbe in dieser Form angeben oder als Kombination der RGB-Werte:
dbx_io("SETCOLOR", "h.KontoNummer$",
"255/0/0", "255/255/128" )
2.
Zurücksetzen der Farbe
dbx_io("RE
[...]


---

## Fehler- & Ereignisprotokoll löschen

Fehler- & Ereignisprotokoll löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
Fehlerliste
Fehlerprotokoll
Event
ArchivEreignis
AnwVarinBenutzung
Protokoll
AeinsBackup

---

## Fehlerkonto Vorsteuer / Mehrwertsteuer

Fehlerkonto Vorsteuer / Mehrwertsteuer
Diese Konten werden als Ersatzkonten gezogen, falls
keine eindeutige Steuerzuordnung gefunden wurde !

---

## Felder der Variante

Felder der Variante
Bezeichnung
Beschreibung
Konvertiert?
Ja/Nein
Gibt
      an ob zu dem Winword ein RTF vorliegt.
Tabelle
Der
      Name der Tabellen-Relation, die die entsprechenden Daten
      vorhält.
Winword-Spalte
Der
      Name der Tabellen-Spalte, die die Winword-Daten vorhält.
Winword-Länge
Länge der Winword-Daten in
      Bytes.
RTF-Spalte
Der
      Name der Tabellen-Spalte, die die RTF-Daten vorhält.
RTF-Länge
Länge der RTF-Daten in
      Bytes.
PK-Spalte
Der
      Name der Primary-Key-Spalte der Tabellen-Relation.
PK-Wert
Der
      Wert des Primary-Key (eindeutig innerhalb der
      Tabellen-Relation)
Feld-Schnipsel
Für
      die Konvertierung notweniger Ausdruck zur internen
      Datenerhebung.
Where-Schnipsel
Der
      Where-Ausdruck für die Ermittlung der beteiligten Daten.
Anmerkung:
Tabelle, RTF-Spalte und Where-Schnipsel sind zusammen
eindeutiger Schlüssel und werden auch so in der Konvertierung verwendet.

---

## Feldzuordnung

Feldzuordnung
Zusätzlich zu dem SQL Befehl muss nun angegeben
werden, welches Outlook Feld mit welchem Referenz-ERP feld „verbunden“ werden soll,
hierzu ist in der F5 Maske Feldzuordnung folgendes einzugeben :
Ist noch nichts angegeben, so muss im Neu Fall das
Feld Name mit einem Sinnvollen Namen belegt werden, der dann in der oben
erwähnten Maske UNBEDINGT eingetragen werden muss, sonst werden keine Felder
zugeordnet.
Das Feld View kann  freigelassen werden.
Jetzt sind nacheinander die Felder Datenbankname,
Label und Sortierung einzugeben.
Datenbankname
In diesem Feld ist der Orginalname des Outlook Kontakt
Ordners anzugeben. Dieser Orginalname ist per Outlook Objektmodell leicht
abfragbar, dazu ist im Outlook der bereich Makro anzuwählen, und hier die Visual
Basic Editor Variante. Innerhalb dieses Bereiches kann dann das Outlook Objekt
Modell geöffnet werden, und in diesem Bereich ist der Contact Bereich anwählbar,
der eine Auflistung aller Orginalnamen der Outlook Kontaktordner
[...]


---

## Filialsystem

Filialsystem
Hauptmenü
Filialsystem
Was ist Replikation?
Die Erläuterung und Definition des Begriffes
Replikation finden sich ausführlich beschrieben in der
SQL-Remote
Hilfe
.

---

## Finanzbuchhaltungsbelege aus der Eingangsmappe

Finanzbuchhaltungsbelege aus der Eingangsmappe
Hauptmenü
Finanzbuchhaltung
Erfassung
Eingangsmappe
Funktion
Auswahlliste
F10
Direktsprung
[EMAA]
Zusätzlich zur Eingangsmappen-Erfassung existiert eine
Auswahlliste, in der alle Daten laut Filter/Bereichsauswahl Einstellungen
angezeigt werden. Hier stehen dann alle Funktionen der Auswahlliste zur
Verfügung.
Die Funktion
Ansehen
F6
verzweigt für die aus der Eingangsmappe
entstandenen Finanzbuchhaltungsbeleg in die
Einzelbeleganzeige
.
Mit der Funktion
Ändern
F5
können diese Finanzbuchhaltungsbelege
bearbeitet werden, jedoch nur solange sie nicht verbucht wurden.

---

## Fällig ...

Fällig ...
Hier kann relativ zum aktuellen Tagesdatum die Anzeige
nach Fälligkeit begrenz werden ( 0 = heute, + n = n Tage voraus, -n = n Tage
zurück ).

---

## Font Tabellennummer

Font Tabellennummer
Hier gibt man eine Nummer und eine Bezeichnung an. Die
Nummer wird im Neufall vorbelegt mit der nächsten freien Nummer. Man kann aber
auch eine andere noch nicht vergebene Nummer eintragen.

---

## Formate in Anschriften

Formate in Anschriften
Folgende Formate werden in den Anschriften
verwendet:

---

## Formelfelder im Crystal Report

Formelfelder im Crystal Report
Referenz-ERP versorgt bestimmte Formelfelder des Reports
automatisch mit Daten. Diese sind:
Formelfeld
Bedeutung
LABEL1 … n
Wenn
      die Kommunikation des Auswahlbereichs über Referenzvariablen erfolgt,
      stehen hier nur die Bezeichnungen der aktiven Abfragen.
AUSWAHLVON1…n
Wenn
      die Kommunikation des Auswahlbereichs über Referenzvariablen erfolgt,
      stehen hier nur die Von-Eingaben der aktiven Abfragen.
AUSWAHLBIS1…n
Wenn
      die Kommunikation des Auswahlbereichs über Referenzvariablen erfolgt,
      stehen hier nur die Bis-Eingaben der aktiven Abfragen.
VON1…N
Vonwert, wie er eingegeben wurde.
      Bei FS Formaten der Wert, der unter Schnipsel steht
BIS1…N
Biswert.
VONWERT1…N
Vonwert, wie er eingegeben wurde.
      Bei FS-Formaten immer die textliche Darstellung.
BISWERT1…N
Biswert.
WAEHRUNG
Die
      Währung, in der der Report dargestellt wird. In der Finanzbuchhaltung gibt
      es bei diversen Reporten die Möglichkeit das Ergeb
[...]


---

## Formular Begleitzettel

Formular Begleitzettel
Auch für den DTA-Begleitzettel gibt es ein
vorgefertigtes  Standardformular ( -20 ) . Ein alternatives Firmalur kann
hier hinterlegt werden.
Hinweis:
Das Formular muss mit dem Formulartyp 270
(Begleitzettel) angelegt werden.

---

## Formulare

Formulare

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
      soll helfen durch optisch
[...]


---

## Formular Importe

Formular Importe
Bei den normalen Importen können nur Bereiche auf
gleiche Bereiche kopiert werden.  Kopien zwischen unterschiedlichen
Bereichen sind i.a. nicht sinnvoll, weil sie in Bezug auf die druckbaren
Positionen nicht kompatibel sind. Nichts desto trotz kann es nützlich sein, etwa
den Kopf eines Rechnungsformulars auf den Kopf eines Kontraktformulars zu
kopieren. Genau diese eigentlich bereichsfremden Importe machen die “wilden”
Importe, die den gewählten Bereich nur mit ihren gemeinsamen Druckpositionen
kopieren. Man kann so zumindest alle Festtexte und vielleicht noch einige andere
Positionen übernehmen.
Formularstamm – Register
      Importe
Feld
Beschreibung
Quellformular für Funktion
      Import:
Formular
Formularnummer und Bezeichnung des
      Quellformulars
Bereich
Bereichnummer und Bezeichnung des
      Quellbereichs
Variante
Variantennummer und Bezeichnung der
      Quellvariante
Import aus Datei:
Dateipfad
F3
      öffnet Explorer-Fenster für den Pfad z
[...]


---

## Formular RFS Banksammelliste

Formular RFS Banksammelliste
Mit Aeins wird ein Standardformular ( -23 ) zum
Erstellen der Banksammelliste ausgeliefert. Falls eine eigene Gestaltung dieses
Formulars gewünscht wird, kann hier ein abweichendes Formular angegeben
werden.
Hinweis:
Das Formular muss mit dem  Formulartyp 281 (RFS
Banksammelliste) angelegt werden.

---

## Formulartypen

Formulartypen
Typ 10 (EC Lastschrift)
Lastschriftbestätigung
Formular 30 (Druck der EC-Lastschrift auf dem Schacht des
Bondruckers)
(Bem.: die Nummer des Lastschriftformulars ist
flexibel und wird in den Kasseneinstellungen in der Gruppe „Formulare“, Nummer 2
zugeordnet)
Variablenname
Druckposition
Druckbereich
Bedeutung
EC_Firma
3
      TextVariable
950
      Hauptteil EC_Lastschrift
Mandanten / Firmenname
EC_Betrag
4
      ZahlVariable
6250
950
      Hauptteil EC_Lastschrift
Betrag der Lastschrift in erfaßter
      Währung
EC_Waehrung
3
      TextVariable
6251
950
      Hauptteil EC_Lastschrift
Währungskürzel, in der Lastschrift
      erfaßt wurde
EC_Datum
11
      Tagesdatum
6252
950
      Hauptteil EC_Lastschrift
Tagesdatum, an dem Lastschrift
      erfaßt wurde
EC_Zeit
3
      TextVariable
6253
950
      Hauptteil EC_Lastschrift
Uhrzeit, an der Lastschrift erfaßt
      wurde
EC_KartNr
3
      TextVariable
6254
950
      Hauptteil EC_Lastschrift
Kartennummer der
[...]


---

## Formulartypen und Standardformulare für Finanzbelege

Formulartypen und Standardformulare für Finanzbelege
Seit Referenz-ERP 7.1 ist der Formulardruck für Finanzbelege
teilweise umgestellt. Bis dahin galt:
Wenn kein Formular eingerichtet war, so erfolgte der
Druck nach einer fest programmierten Formularsteuerung. Diese griff immer bei
Übernahmen, Übergaben und Zählberichten. Jeglicher Wiederholungsdruck erfolgte
stets auf diese Art und Weise. Die anderen Belegarten von Finanzbelegen konnten
im Erstdruck über Formularsteuerung erstellt werden, sofern ein entsprechender
EPA gesetzt (Zahlungsmaske, Formulardruck für …)  und die entsprechenden
Formulare eingerichtet waren. Diese Formulare (alle vom Formulartyp 201)
sind:
51: Ein- und Auszahlungen, Entnahmen
52: Einreichungen
53: Sortenwechsel
54: Zahlungsmeldungen
Andere Formulare konnten nicht zugeordnet werden.
Die Formularsteuerung von Barverkaufsvorgängen erfolgt
unabhängig davon analog den Standardvorgängen in der Ware. Die Zuordnung des zu
verwendenden Formulars erfolgt hier nach de
[...]


---

## Freigeben / Sperren

Freigeben / Sperren
Belege können für bestimmte Bearbeitungsschritte
gesperrt bzw. wieder freigegeben werden. Dies kann im Einzelfall für einen noch
zu prüfenden Beleg erfolgen, oder aber eine generelle Belegflusssteuerung als
Begründung haben. Hierzu ist dann auch die Möglichkeit zu beachten, bei der
Formularzuordnung eine generelle Weiterverarbeitungssperre für eine
Vorgangsklasse / -unterklasse einzuführen.

---

## Funktion "Ansehen"

Funktion "Ansehen"
Stellt den Winword-Eintrag in einem Fenster dar, und
den RTF-Eintrag im Windows-Programm "Wordpad".
Dient der Sichtkontrolle, und kann in Fehlerfällen
helfen ggf. Hinweise auf Ursachen liefern.

---

## Funktion "Dokumente exportieren"

Funktion "Dokumente exportieren"
Probleme für die die Funktion "Ansehen" keine Hinweise
liefert, kann es hilfreich sein die Winword- und RTF-Dokumenten in das
Datei-System zu verbringen umso mehr Möglichkeiten zu haben die entsprechenden
Dateien zu untersuchen.
Nach dem Export wird das Export-Verzeichnis im
Windows-Explorer geöffnet.
Das Export-Verzeichnis befindet sich im
Referenz-ERP-Verzeichnis unter Export\word2rtf erweitert um den jeweiligen
Tabellen-Namen.
Der Export legt die benötigten Verzeichnisse
automatisch an.
Der Export spielt keine RTF-Dateien aus die Null oder
die Länge 0 haben.
Der Export löscht keine Dateien.
Exportierte Dateien folgen der Namenskonvention
{Tabelle}_{Pk_Wert}_{Name der
Spalte}.{Extension}
wobei "Name der Spalte" entweder der Inhalt
"Winword-Spalte" oder "Rtf-Spalte" ist und "Extension" jeweils analog entweder
"doc" oder "rtf".

---

## Funktion Arbeitsregel ändern im Vorgang

Funktion Arbeitsregel ändern im Vorgang
In den einfachen Auswahllisten für Vorgänge, in denen
die Arbeitsregel in der Spalte Rg angezeigt wird, gibt es eine Funktion
Arbeitsregel ändern
mit der man für
markierte Datensätze die Arbeitsregel neu setzen kann.
In die sich öffnende
Maske gibt man die Nummer der Arbeitsregel ein die ab sofort für die markierten
Belege verwendet werden soll.
Wählt man die Arbeitsregel 0 aus, kommt eine
Meldung: Sie haben keine Regel ausgewählt. Aus den ausgewählten Vorgängen wird
die Regelzuordnung entfernt. Sind sie sicher?
Ist für das Kästchen
‚Regeln anwenden‘ der Haken gesetzt, dann werden für die neu zu setzende Regel
die hinterlegten Regeln (z.B. die Nachfolgeregel) aktiv. Wenn z.B. die
Arbeitsregel 699 durch diese Funktion eingetragen werden soll, eine
Nachfolgeregel aber sagt, dass Belege mit Kontrakt die Regel 610 erhalten
sollen, dann würde genau diese eingetragen werden, wenn ein Kontrakt enthalten
ist.
Will man dies nicht, sondern es s
[...]


---

## Funktionen

Funktionen
Neu
Löscht alle Eingabefelder und ermöglicht die Erfassung
einer neuen Vorgangsklasse/-Unterklasse.
Speichern
Speichert die Einstellungen
Speichern unter …
Nach Aufruf dieser Funktion werden die Felder
Vorgangsklasse und –Unterklasse für die Eingabe geöffnet. Sie können die
aktuellen Einstellungen für eine neue Vorgangsklasse/Unterklasse verwenden.
Hinweis:
Bitte beachten Sie, dass einige Einstellungen nicht in
allen Vorgangsklassen zur Verfügung stehen. Sie müssen nach dem Speichern diese
Einstellungen erneut laden und nachbearbeiten, da sie nicht während der
Erfassung angezeigt werden.
Text-Zuordnung
Zuordnung der Textbausteine zu dieser Vorgangsklasse.
Dabei dient die Zuordnung der Vorgangsunterklasse 0 für jede Vorgangsklasse als
Standardzuordnung. Das bedeutet, dass für jede Text-Zuordnung einer Unterklasse
zusätzlich die Text-Zuordnung der Unterklasse 0 geladen wird.
Formulare einrichten
Funktion erstellen
Hier können Sie Funktionen für den Aufruf dieser
Vorg
[...]


---

## Funktionen

Funktionen
Funktion
Taste
Ansehen
F6
Genau ein Eintrag
      auswählbar.
Konvertieren
F10
Mehrfachauswahl
      möglich
RTF nullsetzen
F7
Mehrfachauswahl
      möglich
Dokumente
      exportieren
F9
Mehrfachauswahl
      möglich.

---

## Funktionen

Funktionen
In der App kann man sowohl neue Personen als auch neue
Firmen hinzufügen. Zudem haben die Icons der Firmen/Personen-bezogenen Daten
Funktionen.
Icon Funktionen
-
Telefon / Handy:
Ruft die gespeicherte Rufnummer an
-
Webseite:
Öffnet die gespeicherte Webseite
-
E-Mail:
Öffnet das standard E-Mail Programm mit der gespeicherten E-Mail als
Empfänger
-
Karte:
Öffnet eine Karte mit dem gespeicherten Standort
Firma hinzufügen
Firmen die in der Referenz-ERP App hinzugefügt werden,
werden aus Organisationsgründen in der Referenz-ERP Software als Interessenten
hinzugefügt.
Person hinzufügen
Eine Person wird in der Referenz-ERP App als Ansprechpartner
in der Referenz-ERP Software angelegt.

---

## Funktionen der Belegerfassung

Funktionen der Belegerfassung
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Anzeige Primanota aktualisieren
F9
Die Anzeige wird
aktualisiert, so dass eventuell neu hinzugekommene Beleg mit angezeigt
werden.
Primanota drucken
F11
Für den Druck stehen vier
Reporte zur Verfügung, die Primanota in unterschiedlicher Form
darstellen:
1.   Primanota nach
Belegart
2.   Primanota
chronologisch
3.   Primanota nach
Konten
4.
Primanota
Fremdwährung
Bediener Korrektur
F3
In der Belegerfassung werden
nur die Belege angezeigt, die von einem Bediener erfasst wurden. Mit der
Funktion
Bediener Korrektur
lässt
sich der Bediener auswählen, dessen Belege korrigiert werden sollen
Neuen Beleg erstellen
F8
Aufruf der Erfassungsmaske
der Belegarten:
ZA Zahlungsverkehr Kasse/Bank
AR
Ausgangsrechnung
AG Ausgangsgutschrift
ER Eingangsrechnung
EG
Eingangsgutschrift
SO Sonstige Belege
EB Eröffnungsbuchungen
KU
Kostenstellen-Umbuchungen
SE Scheckeinreichen
KT
Kostenträger-
[...]


---

## Funktion "Konvertieren"

Funktion "Konvertieren"
Führt eine nicht-visuelle Konvertierung des
Winword-Dokumentes in ein RTF-Dokument durch. Ein bestehendes RTF-Dokument wird
dabei überschrieben.

---

## Funktion "RTF nullsetzen"

Funktion "RTF nullsetzen"
Setzt den Eintrag der RTF-Spalte auf Null. Das hat den
Effekt das eine Konvertierung im Programm durchgeführt wird, sobald die Software
den Inhalt benötigt.

---

## Generelle Hinweise

Generelle Hinweise
Die ‚Problemliste’ wird während der Abarbeitung der Belege
nicht ständig neu aufgebaut (da das Einlesen lange dauern kann). Ratsam ist,
nach kompletter Abarbeitung den zugehörigen Button noch einmal zu drücken, es
sollten dann keine Problemfälle mehr vorhanden sein!
Dieses Tool ist nur ein Hilfswerkzeug, es sollte auf keinen
Fall zur Standardanwendung der Anwender werden!

---

## Genereller Ablauf der Kontokorrentzinsen

Genereller Ablauf der
Kontokorrentzinsen
Kontokorrentzinsen werden durch Verzinsung des
fälligen Saldos errechnet – nicht durch Verzinsung der offenen Posten. Der
fällige Saldo ergibt sich anhand des Valuta/Fälligkeitsdatums. Dieses Datum
ergibt sich bei Warenwirtschafts-Belegen oder Finanzbuchhaltungs-Belegen durch
die im Kundenstamm hinterlegte Zahlungsbedingung bzw. durch manuelle Eingabe.
Bei den Belegarten, für die keine Zahlungsbedingung vorgesehen ist (Zahlungen,
Scheckeinreicher, Sonstige Belege) kann ebenfalls ein Wertstellungsdatum erfasst
werden. Vorbelegt wird dieses Datum mit dem Belegdatum. Man kann diese
Vorbelegung aber mit Hilfe eines Einrichtungsparameters ändern:
Belegdatum +
nnn Tage = Valutadatum
. Dann wird zu dem Belegdatum jeweils diese Anzahl
Tage hinzugerechnet und als Fälligkeits-/Wertstellungsdatum vorgeschlagen
Es gibt in der Belegerfassung noch einen weiteren
Einrichtungsparameter, der für das Fälligkeits-/Wertstellungsdatum wichtig ist:
Valuta
[...]


---

## GeoDatendienste

GeoDatendienste
Die Geodaten sind für die Abfrage von geografischen
Koordinaten zu einer Anschrift notwendig. Referenz-ERP unterstützt hier den Anbieter
Google:
Google
Google bietet (Stand Juli 2023) einen Account mit 200$
monatlichem Grundguthaben an, wobei dieses durch Anfragen an den Webservice bis
zu 1000 Stück 5$ kosten.
Dieser API-Key lässt sich mit der Entfernungsmatrix
kombinieren.
Mehr unter
https://mapsplatform.google.com/pricing/
Die Zugangsdaten zu den Webdiensten werden im
Mandantenstamm
eingepflegt

---

## Geschäftsjahr falsch

Geschäftsjahr falsch
Nach dem Wechsel von 1999 zu 2000 kann dieser Fehler
auftreten. Man prüfe unter Direktsprung [OSQL] das folgende Statement:
SELECT AMIC_Jahrnummer_zu_Datum(‘01.01.00‘)
wird jetzt nicht „2000“ ausgegeben sondern „.....“, so
muss folgendes Statement abgesetzt werden:
SET OPTION nearest_century=50.
Anschließend sollte das erste Statement den
gewünschten Wert liefern. Andernfalls muss ein dbupgrade durchgeführt werden
-> Hotline.

---

## Gebindemenge

Gebindemenge
Es kann aber auch statt des Gebindefaktors die
Gebindemenge eingegeben werden, dann wird der Gebindefaktor 1
rückgerechnet.

---

## Gesellschafter-Mitgliederverwaltung

Gesellschafter-Mitgliederverwaltung

---

## Globale Einstellungen

Globale Einstellungen
Da die Umwandlung von Belegen (intern) eine
komplizierte Angelegenheit ist, kommt man auch hier nicht ohne globale
Einstellungen aus. Es handelt sich hierbei um die ehemaligen SPA Einstellungen:
Trennen nach Geschäftsjahr und Trennen nach Perioden.
Die SPA Einstellungen behandeln Geschäftsjahr und
Periode als eine Einheit, da eine getrennte Einstellung kaum Sinn macht. Ferner
wird unterschieden nach Einzelumwandlung und Sammelumwandlung, da bei der
Sammelumwandlung etwas unterschiedliche Bedingungen vorliegen als im
Einzelumwandlungsmodus:
Für den SPA ‚Periode / Jahr bei Einzelumwandlung’ gibt
es folgende Einstellung:
0 = Original übernehmen
Diese Einstellung haben wir lediglich aus Gründen der
Kompatibilität beibehalten – wir empfehlen die Einstellung ausdrücklich
NICHT
. Bei der Umwandlung wird die Originalperiode beibehalten (bei den
Umwandelarten Storno / Kopie / Gutschrift aus Rechnung ist das Beibehalten
inhaltlich bedingt mit dem Häkchen ‚1 zu 1’
[...]


---

## Google Maps anzeigen

Google Maps a
nzeigen
Aus einer Auswahlliste heraus kann Google-Maps die
Anschriften in der markierten Reihenfolge anzeigen. Voraussetzung dafür ist,
dass die Auswahlliste eine adressId – ersatzweise eine kundid in den
Returnwerten hat. Bei der Verwendung der kundId wird die Hauptanschrift des
Kunden ermittelt und als Anschrift für die Anzeige verwendet.
Funktion
Google_Maps_AdressId

---

## Grundsätzliches zur Verwendung von JPP-Objekten

Grundsätzliches
zur Verwendung von JPP-Objekten
Jedes JPP-Objekt muss instanziiert werden, dabei wird
ein Zugriffs-Handle „hdl“ festgelegt.
Alle Methoden und Funktionen werden nun über dieses
Handle referenziert.
Nach Abarbeitung der Aktionen muss das Zugriffs-Handel
wieder freigegeben werden.
Vor der Ausführung einer Funktion erfolgt meistens
eine Parameterzuweisung, deren Inhalt und Anzahl von der auszuführenden Funktion
abhängt.
Die JPP-Objektnamen sowie die der auszuführenden
Funktionen/Methoden sind in Hochkommatar einzugeben.
Viele der Funktionen liefern einen Rückgabewert
(true/false) der in der Programmlogik verwendet werden kann.
Die wichtigsten
JPP-Befehle (anhand eines „JDBX“-Objektes)
jpp_new hdl,
"JDBX"
neues „JDBX“ JPP-Objekt
instanziieren
jpp_in hdl, "sql"  ,
sql
Parameter eingeben
jpp_do hdl ,
"exec"
Methode ausführen
jpp_delete
hdl
H
[...]


---

## Gutschriften und Belegkopien

Gutschriften und Belegkopien
Referenz-ERP bietet jetzt die Möglichkeit, sowohl
Gutschriften als auch Belegkopien in zwei Varianten zu erstellen. Zu diesem
Zweck gibt es die Einstellung:
Mit dem Häkchen ‚(1 zu 1 (Perioden / Lieferdatum
erhalten)’ wird festgelegt, ob Perioden und Lieferdaten des Ursprungsbeleges
erhalten werden sollen. Die Gutschrift wirkt dann wie ein Stornobeleg. Die
Einstellungen für Perioden sind dann deaktiviert, Belegdatum und Unterklasse
können nach eigenem Ermessen abgeschaltet werden (die Daten des Quellbeleges
werden übernommen), die Zusatzseite für Problemfälle erscheint aktiviert.
Ist das Häkchen nicht gesetzt, handelt es sich eher um
eine Neuerfassung des Beleges.
Auf ähnliche Weise kann auch bei der Belegkopie
verfahren werden. Auch hier gibt es das ‚1 zu 1’ Häkchen:

---

## Unterstütze Hardware

Unterstütze Hardware
Die unten stehende Hardware wird z.Zt.
unterstützt.
Andere Geräte sind durchaus anschließbar, es besteht
aber keine Gewähr, da diese nicht getestet wurden.

---

## Hauptmenü-Menülogobereich

Hauptmenü-Menülogobereich
Im Standardfall wird in diesem Bereich eine analoge
Uhr(*) angezeigt. Im Falle von Archiv-Anschluss können hier aber auch
Bild-Elemente des Archivs darstellt werden.
Der Menülogo-Bereich ist durch einen Schieber in der
Höhe verstellbar und kann durch Mausklick auf den Schieber ganz minimiert
werden.
Belegklasssen
Firmenlogo
8021
Firmenlogo - BDKL
8022
Firmenlogo – BD
8023
Bei mehreren Einträgen werden diese rückwärts nach
Belegklasse und dann nach Änderungsdatum sortiert und davon der erste genommen.
Für die Zuordnung 8023 ist das Feld
fa_aenderungsbediener im Formulararchiv zuständig.
Die Ausmasse des Grafik-Elementes betragen 260x120
Bildpunkte.
(*) Um die Anzahl der Bildschirmübertragungen zu
minimieren wird in Sitzungen die gemäß ausgewiesen sind der Sekundenzeiger
ausgeblendet.
Durch die EPA-Einstellungen in der Hauptmenü-Maske
lassen sich Privatisierungen der Ermittlung der anzuzeigenenden Bild-Dokumente
durchführen.

---

## Hauptmenü-Rollenpflege

Hauptmenü-Rollenpflege
Die Rollenrechte der Kontext-Menüfunktionen (siehe
Rollenkontext
sind wie
folgt an den Rollenkontext und können auch dort gepflegt werden.
Funktionsbeschriftung im
      Kontextmenü
Zugeordnete
      Referenz-ERP-Funktion
Zugeordnete
      Referenz-ERP-Optionbox
Zugriffsrechte
hm_zugriffsrecht
ob_hauptmenu
Zugriffsrechte Hauptmenu
hm_zugriffsrecht_hauptmenu
ob_hauptmenu
Hinweis: Weder die Sortierung, noch die
Funktionstasten können dieser Funktionen können geändert werden.

---

## Hauptmenü-Tastenkombinationen

Hauptmenü-Tastenkombinationen
Tastenkombination
SHIFT+Strg+F3
Telefonnummerneingang
ALT+1
Telefonnummerneingang
SHIFT+F4
Öffnet den
      Referenz-ERP-Direktsprung-Dialog
F3
Öffnet den
      Referenz-ERP-Direktsprung-Dialog
a-z
      bzw.A-Z
Öffnet den
      Referenz-ERP-Direktsprung-Dialog und belegt die gedrückte Taste dort vor. Der
      Tastendruck gibt somit den ersten „Buchstaben“ des Direktsprunges
      vor.
Somit kann man „einfach“ im
      Hauptmenü einen Direktsprung eingeben, ohne vorher SHIFT-F4 oder F3
      tätigen zu müssen.
Zusätzlich zu den „Buchstaben“ sind
      die Sonderzeichen +, - und das Ausrufezeichen als erstes Zeichen
      zugelassen.
Wenn
      Sie Direktsprünge  eingerichtet haben, die andere Zeichen als als
      erstes Zeichen haben als die hier beschriebenen, dann müssen Sie SHIFT-F4
      bzw. F3 verwenden!
F1
Hauptmenü-Hilfe
Weitere Tastaturbelegungen sind kontextabhängig, siehe
Kontextmenüs der
Menüpunkte
.

---

## Hinzufügen von weiteren Feldern auf Basis dieser BI

Hinzufügen von weiteren Feldern auf Basis dieser BI
Es kann nun vorkommen, dass zusätzlich zu den in der
Query vorhandenen Felder noch weitere definiert werden sollen, die in
Auswertungen wie z.B. Pivot zur Verfügung stehen sollen. Hierbei soll es sich um
Felder handeln, die als „berechnete“ Felder von vorhandenen Feldern oder
Informationen arbeiten sollen.
Hierzu wird einfach der Befehlstext in den
Verbindungseigenschaften um besagte Felder erweitert. In folgendem Beispiel soll
alles was zur Vorgangsklasse < 1000 gehört mit dem Text Verkauf und alles
andere mit dem Text Einkauf versehen werden, um ein Pivot Einkauf/Verkauf zu
gestalten. Dazu wird einfach der Befehlstext wie folgt angepasst:
SELECT
*,if v_klassnummer in (400,600,690,700,790,800,890) then 'Verkauf' else if
v_klassnummer in (1400,1600,1690,1700,1790,1800,1890) then 'Einkauf' else
'Intern' endif endif as VkEk
from
admin.bi_SV_UEBERSICHT_Status_0

---

## HTML-Body

HTML-Body
E-Mails werden schon lange nicht mehr als reiner
ASCII-Text versendet, sondern oftmals im HTML-Format. Damit der E-Mail-Body in
HTML darstellen lässt und so die Auswahl von Schriftarten, Schriftstilen oder
Schriftgrößen ebenso darstellen wie digitale Grafiken.
Damit Inhalte des Belegs in das HTML eingefügt werden
können, erstellen Sie eine Datenbankfunktion, die aus dem zu versendenden Beleg
Daten herauskristallisiert und in ein HTML einsetzt.
Das „ROH“-HTML wird als Eintrag ins Archiv gestellt
und seine Eintrags-ID wird in der
Formulararchivzuordnung
hinterlegt.
Als Beispiel verwenden Sie dazu die Datenbankfunktion
AMIC_DEMO_HTMLBODY
---<class
name="AMIC_DEMO_HTMLBODY"/>
---<summary>AMIC_DEMO_HTMLBODY</summary>
---<returns>HTMLBody</returns>
---<param name="in_fa_id">fa_id des zu
versendenden Ware-Beleges</param>
---<param name="in_fa_mndNr">Mandantnummer des zu
versendenden Ware-Beleges</param>
CREATE FUNCTION AMIC_DEMO_HTMLBODY(in_fa_id integer,
in_fa_mndNr inte
[...]


---

## IDENTLOAD Statement

IDENTLOAD
Statement

---

## ImportVorgPosiAddon

ImportVorgPosiAddon
Addon
Daten
In dieser Relation werden Daten gespeichert, die
später in der Tabelle WarenbewegungAddon zur Position hinterlegt werden sollen.
Der Name des gegebenen AddOn-Feldes muss mit dem
Feldnamen in der Tabelle übereinstimmen, da sonst keine Daten gespeichert werden
können.
Die Verknüpfung zur Position wird über das Feld
IVP_GUID hergestellt.
Feld
Bedeutung
IVP_GUID
Guid
      der Position
AddonTyp
AddonTyp
AddonName
Name
      des Addonfeldes
AddonWert
Inhalt des Feldes

---

## ImportVorgPositionLVS

ImportVorgPositionLVS
Diese Relation beherbergt Informationen zu
LVS-Ladeträgern, die zu dieser Position gehören.
Feld
Bedeutung
UebernahmeID
Uebernahmeid der zugehörigen
      Position der Relation ImportVorgPosition
SatzID
SatzId der zugehörigen Position der
      Relation ImportVorgPosition
PositionID
Positions-ID der zugehörigen
      Position der Relation ImportVorgPosition
PositionZaehler
Laufender Zähler der
      LVS-Informationen zu der gegebenen Position
LokalitaetsNr
Nummer des
      Ladeträgerstandorts
LadetraegerNr
Nummer des Ladeträgers
LadeeinheitsNr
Nummer der Ladeeinheit
LadeeinheitsPosition
Nummer der Ladeeinheitsposition auf
      dem Ladeträger
BewegungsId
LadetraegerExtNummer
Externe Nummer des Ladeträgers (z.B.
      eine NVE)
Menge
Menge auf dem Ladeträger
ME_Nummer
Mengeneinheit der Menge auf dem
      Ladeträger
IVP_GUID
Guid
      der dazugehörigen Position der Relation
ImportVorgPosition

---

## ImportVorgPositionPartie

ImportVorgPositionPartie
In dieser Relation werden Informationen der Partie(n)
einer Position abgelegt. Eine Partie, die hier eingetragen ist, jedoch im System
noch nicht existiert, wird angelegt werden.
Feld
Bedeutung
IVP_GUID
Guid
      der dazugehörigen Position der Relation
ImportVorgPosition
Zaehler
Partiezähler
PartieId
PartieId
PartieNummer
Partienummer
Ist
      die Partienummer gesetzt und die Partiebezeichnung wird mit der
      Kombination
Partienummer und Partiebezeichnung
      nach der Partie gesucht. Wenn nur die Partienummer gesetzt worden ist wird
      nach der Partienummer gesucht
Existiert mehr als eine Partie zu
      einer Partienummer wird immer die erste Partie gewählt
PartieBezeichnung
Ist
      nur die Partiebezeichnung angegeben worden, und zu dieser Partie wurde
      keine aktive Partie gefunden, so wird eine neue Partie
      angelegt.
Sind
      Partienummer und Partiebezeichnung angegeben, so wird die Partie nach
      dieser Kombination ges
[...]


---

## ImportVorgTextPosition

ImportVorgTextPosition
Positionstext
In dieser Relation werden Textpositionen hinterlegt,
die entweder vor oder nach einer Position in den Beleg eingefügt werden können.
Feld
Bedeutung
UebernahmeID
Übernahmeid aus der Relation
      ImportVorgPosition
SatzId
SatzId aus
      ImportVorgPosition
PositionId
Positionsid aus
      ImportVorgPosition
Zeilenzaehler
Zähler der Textzeile
Texttyp
Texttyp
0.  Positionstext
TextPosition
Beim
      TextTyp 0 (Positionstext) an welche Stelle soll der Text geschrieben
      werden
0
      Vor der Position
1
      Nach der Position
VorgText
Inhalt des Textes
IVP_GUID
Guid
      der Position aus der Relation ImportVorgPosition
Hier muss als Schlüssel Beziehung zur Tabell
ImportVorgPosition die ÜbernahmeId, SatzId und PositionId genommen werden

---

## INI-Dateien

INI-Dateien

---

## Inkompatibilitätsprobleme

Inkompatibilitätsprobleme
•
Es kann bei einem schlecht formulierten SQL Befehl dazu führen, dass
Feldnamen doppelt vergeben worden sind. Diese unsaubere Programmierung hat schon
jetzt zu der Situation geführt, dass niemand weiß, welchen der beiden Felder das
System auf den Bildschirm bringt. In einer BI Umgebung sind aber doppelte Felder
nicht mehr erlaubt, hierzu ist die Anwendung zu korrigieren und alle doppelten
Felder sind zu entfernen.
•
In eine Bereichsauswahl war es bisher möglich auf interne
Strukturvariablen zuzugreifen, dieser Zugriff ist ab jetzt nicht mehr möglich
und alle entsprechend formulierten Bereichsauswahlen (:*) sind zu korrigieren
und auf Datenbankvariablen (z.B. USER) umzustellen.
•
Achtung: Nur weil eine Auswahlliste funktioniert, heißt es nicht, dass
diese mit Business Intelligence funktioniert. Die Auswahlliste korrigiert
teilweise inkorrektes SQL während Excel das SQL-Statement unkorrigiert ausführt.
Beliebte Fehler sind zum Beispiel ein Komma vor
[...]


---

## Installation der Testumgebung

Installation der Testumgebung
Nach Feritgstellung des Installationsverzeichnisses
wird eine Testinstallation gestartet. Bei dieser Installation werden auf zwei
Rechnern mehrere datenbanken verschiedenster Größe mit einem Update versehen.
Die Basisdatenbank wird ebenfalls mit in die Installation einbezogen, um auch
auf einer leeren Datenbank test durchzuführen. -*
--------------------------------------------------------------------- Für den
Test eine Basisinstallation vorbereiten
--------------------------------------------------------------------- 29.06.2001
ah Autoupdateflag setzen 12.01.2003 BT Del Killjob aufgrund der ICA Sessions
eliminiert.  system%\bin\setini.exe AeinsSetup autosetup true
%vm_testinstall%\user\aeinssetup.ini  XIST f:\system\aeins\user\kairo*.txt
del f:\system\aeins\user\kairo*.txt /f /q OT EXIST \\husum\cd\setup\*.ini goto
:EOF d f:\system\aeins\bin
--------------------------------------------------------------------- Den
Server, und damit die DB's
[...]


---

## Installation

Installation

---

## Installation von ICON-Zuordnungen

Installation von ICON-Zuordnungen
Standardmäßig werden alle in der AMICCONF.INI
vorgegebenen Abschnitte […] bei der Installation auf dem Desktop des
Installationsrechners als ICON’s angelegt.
Dieses Verhalten kann mit dem Eintrag
„IconInstall=FALSE“ in der Amicconf.ini Datei unterdrückt werden. Sinnvoll ist
dieser Eintrag nur in dem [Branchen-ERP] Abschnitt, da dies eine globale Einstellung
ist.
Einzelne ICON’s (Mandanten) können damit nicht
ausgeblendet werden.

---

## Jahr / Periode

Jahr / Periode
Hierbei wird ein Eingrenzung nach der im Aeins
üblichen Periodisierung ermöglicht!

---

## Kasse

Kasse
Referenz-ERP bietet Ihnen verschiedene Kassenoberflächen,
die aus unterschiedlichen Anwendungen zum Teil historisch erwachsen sind.
Die Marktkasse
Die Marktkasse ist eine sehr dynamische
Kassenoberfläche, die zudem die Möglichkeit bietet, auf berührungsempfindlichen
Bildschirmen, sog. Touch-Screens bedient zu werden.
Die Tresenkasse
Die Tresenkasse ist eine alternative Kasse zur
Marktkasse.
Die POS-Kasse
Die POS-Kasse wird nicht weiter gepflegt. Jegliche
Dokumentationen dazu sind als historisch zu betrachten und werden nicht weiter
gepflegt werden.

---

## Kasse und Währungen

Kasse und Währungen
Begriffsklärung:
Kassenwährung:
In den Kasseneinstellungen kann in der Gruppe Kasse
eine Kassenwährung hinterlegt werden. Diese Einstellung bewirkt, dass der
Bargeldzahlungssatz mit dieser Währung vorbelegt wird und man bei Bezahlung in
einer anderen Währung über die Taste F12 explizit eine andere Währung auswählen
muss. Diese Vorbelegung gilt auch für die Währung des Rückgeldsatzes. Wenn die
Kassenwährung in den Kasseneinstellungen geändert wird, wird automatisch auch
die Belegwährung der Standardkunden auf die Kassenwährung gesetzt. (Die
Umkehrung gilt nicht!)
Belegwährung:
In dieser Währung wird der Beleg erfasst (diese
Währung kommt aus dem Kundenstamm und kann bei Vorgängen über UFLD-Felder bzw.
an der POS-Kasse über eine Funktion zu Beginn des Vorgangs auf eine beliebige
Währung gesetzt werden), d.h. auch die gefundenen Preise, ... verstehen sich in
Belegwährung.
Buchwährung:
Hierbei handelt es sich um die aktuell gültige
Buchwährung. Diese wird in
[...]


---

## Klassenwechsel

Klassenwechsel
Zu jeder Zeit besteht die Möglichkeit, die
Vorgangsklasse zu wechseln. Durch Anwahl der entsprechenden Funktion oder des
zugehörigen Knopfes steht ein Eingabefeld zur Verfügung, um die Klasse
auszuwählen, welche auch über eine F3 Auswahl aus einer Liste abgefragt werden
kann.

---

## Kündigung

Kündigung
Um Anteile zu kündigen wird ein Gesellschafter in der
Auswahlliste ausgewählt mit
F5
zum
Bearbeiten
geöffnet und die Funktion
Kündigung
F7
ausgewählt.
Die Funktion
Kündigen
F7
öffnet folgende Eingabefelder:
Felder
Anzahl
Hier
      wird die Anzahl der Anteile eingetragen.
Anteilstyp
Hier
      wird der Anteilstyp
F3
Freiwillig oder Pflicht eingetragen.
Zeichnungsdatum
Das
      Zieldatum ist satzungsabhängig das geplante Auszahlungsdatum.
Bemerkung zum Vorgang
Hier
      kann eine Bemerkung zum Vorgang eingetragen werden. (60
      Zeichen)
Belegdatum
In
      diesem Feld wird das Eingangsdatum der Kündigung eingetragen.
Es wird vom Programm verhindert, dass die Anzahl der
gekündigten Anteile die der gezeichneten Anteile je Typ überschreitet.

---

## Konteninformationen

Konteninformationen
Hauptmenü
Finanzbuchhaltung
Information
Konteninformation
Direktsprung
[KOI]
.
Die Konteninformation existiert in zwei Ausprägungen:
1.
Konteninformation nur für Personenkonten
2.
Konteninformation für Sach-, Ober- und Personenkonten
Hier können Informationen über die Buchungen auf Sach-
und Personenkonten mit unterschiedlichem Verdichtungsniveau abgerufen werden.
Nach Eingabe des gewünschten Jahres und des Kontos erscheint folgende
Anzeige:
Mit Hilfe der Buttons mit den Pfeilen kann zwischen
den Jahren und den Konten geblättert werden. Beim Blättern zwischen den Konten
wird zum nächsten oder vorangegangene Konto desselben Kontotyp – Sachkonto,
Personenkonto oder Oberkonto – geblättert. Dabei wird zusätzlich geprüft, ob
dieses Konto den Einschränkungen in der F3-Auswahl entspricht, so dass man ggf.
die Möglichkeit hat, durch private Varianten bestimmte Kontobereiche
auszublenden.
Unterhalb des Abfragefeldes befindet sich ein
Informationsfenster, das
[...]


---

## Kontextmenüs der Menü-Hauptpunkte

Kontextmenüs der
Menü-Hauptpunkte
Kontextmenü
      Menü-Hauptpunkt
Tastatur
Beschreibung
Zugriffsrechte
Umschalttaste + F2
Ermöglicht die Rollenpflege des
      Menü-Hauptpunktes.
Für
      die Pflege der Funktion „Zugriffsrechte“ selber siehe
Rollenpflege
Zugriffsrechte Hauptmenü
Ermöglicht die Rollenpflege aller
      Menü-Hauptpunkte.
Für
      die Pflege der Funktion „Zugriffsrechte Hauptmenü“ selber siehe
Rollenpflege
Direktsprung
Umschalttaste + F4
„Aeins-Direktsprung“
Funktionspfleger (nur für
      Entwickler)
Direkt-Aufruf des
      Funktionspflegers
Icon
      zuordnen (vorerst nur für Entwickler)
Direkt-Aufruf des
      Icon-Zuordnungspflegers

---

## Kontextmenüs der Menüpunkte

Kontextmenüs der Menüpunkte
Kontextmenü eines Menüpunkts im
      Menüpunktbereichs
Tastatur
Beschreibung
Zu
      Favoriten hinzufügen
F2
Fügt
      den Menüpunkt den Favoriten hinzu und wechselt gleichzeitig auf den
      Favoritenbereich.
Zugriffsrechte
Umschalttaste + F2
Ermöglicht die Rollenpflege des
      Menüpunktes.
Für
      die Pflege der Funktion „Zugriffsrechte“ selber siehe
Rollenpflege
Direktsprung
Umschalttaste + F4
„Aeins-Direktsprung“
Funktionspfleger (nur für
      Entwickler)
Direkt-Aufruf des
      Funktionspflegers
Icon
      zuordnen (vorerst nur für Entwickler)
Direkt-Aufruf des
      Icon-Zuordnungspflegers
Kontextmenü eines Menüpunkts im
      Menüpunktbereichs
Tastatur
Beschreibung
Von
      Favoriten entfernen
F2
Entfernt den Menüpunkt den Favoriten
      hinzu
Direktsprung
Umschalttaste + F4
„Aeins-Direktsprung“
Funktionspfleger (nur für
      Entwickler)
Direkt-Aufruf des
      Funktionspflegers
Icon
      zuordnen (vorerst nur für Entwickl
[...]


---

## Kopie oder Ersatzfunktion

Kopie oder Ersatzfunktion
Noch nicht implementiert: hier kann im Falle der
Speichern unter Funktion entschieden werden, ob es sich um eine Kopie des
Beleges handelt, oder um einen Ersatz, im Falle des Ersatzes werden dann zu
allen vorher angewählten Belegen Stornobelege geschrieben oder
Teilrücknahmen.

---

## Korrektur

Korrektur
Nicht weiter verarbeitete Belege können korrigiert
werden. Nach Auswahl des Beleges wird in den Beleg verzweigt; die Bearbeitung
entspricht dann der der Belegerfassung.

---

## Kostenrechnung

Kostenrechnung

---

## Lieblingsdruckerdruck

Lieblingsdruckerdruck
Diese Funktion ermöglicht es, ausgewählten Vorgängen
für den Druck einen anderen als den Standarddrucker zuzuordnen.
Zusätzlich kann zum Ausdruck ein anderes Formular
durch Markieren der Unterklasse gewählt werden.
Felder
Erweiterte
    Druckoptionen
Kontonr.
Kontonummer
Kunde
Kunde
Belegnummer
Belegnummer
Datum
Datum
Formulare gedruckt
Anzeige laufendendes Formular von
      Gesamt-Formularen
Nr.
Formularnummer
Formular
Formularbezeichnung
Unter
Vorgangsunterklasse
Unterklasse
Vorgangsunterklassenbezeichnung
VKNR.
Vorgangsklasse
Vorgangsklasse
Vorgangsklassenbezeichnung
Makro
Der
      Name des Makros, welches bei einer Vorgangsdruckklasse hinterlegt
      ist.
Druckernummer
Druckernummer
Druckerbezeichnung
Zugehörige Druckerbezeichnung aus
      Druckerstamm
In
      der Spalte danach bedeutet ein „Stern“, das der Drucker der momentane
      Referenz-ERP-Standard-Drucker ist.
Nulldrucker
Zugehöriges Nulldrucker-Kennzeichen
      aus Druckerstamm
Archiv unter
[...]


---

## Liste der ISO-Codes

Liste der ISO-Codes
Hier eine englischsprachige Liste der Weltwährungen
mit den zugehörigen ISO-Codes 4217 auf dem Stand Nov 2007.
AED
UAE Dirham
AFA
Afghanistan Afghani
ALL
Albanian Lek
ANG
Neth
      Antilles Guilder
ARS
Argentine Peso
AUD
Australian Dollar
AWG
Aruba Florin
BBD
Barbados Dollar
BDT
Bangladesh Taka
BHD
Bahraini Dinar
BIF
Burundi Franc
BMD
Bermuda Dollar
BND
Brunei Dollar
BOB
Bolivian Boliviano
BRL
Brazilian Real
BSD
Bahamian Dollar
BTN
Bhutan Ngultrum
BWP
Botswana Pula
BZD
Belize Dollar
CAD
Canadian Dollar
CHF
Swiss Franc
CLP
Chilean Peso
CNY
Chinese Yuan
COP
Colombian Peso
CRC
Costa Rica Colon
CUP
Cuban Peso
CVE
Cape
      Verde Escudo
CYP
Cyprus Pound
CZK
Czech Koruna
DJF
Dijibouti Franc
DKK
Danish Krone
DOP
Dominican Peso
DZD
Algerian Dinar
EEK
Estonian Kroon
EGP
Egyptian Pound
ETB
Ethiopian Birr
EUR
Euro
FKP
Falkland Islands Pound
GBP
British Pound
GHC
Ghanian Cedi
GIP
Gibraltar Pound
GMD
Gambian Dalasi
GNF
Guinea Franc
GTQ
Guatemala Quetzal
GYD
Guyana Dollar
HK
[...]


---

## Löschen von Events

Löschen von Events
Sie erhalten eine für Eingaben und Änderungen
gesperrte Ansicht des Events, das Sie zum Löschen markiert haben. Wenn Sie nun
die Funktion „Löschen“ wählen, wird dieser Event aus der Eventliste
gelöscht.

---

## Löschen ungebuchter Belege

Löschen ungebuchter Belege
Es können nur Belege gelöscht werden, die noch nicht
verbucht wurden. Für bereits gebuchte Belege muss ein Stornobeleg erstellt
werden. Es gibt mehrere Stellen im Programm, an denen die Belege wieder gelöscht
werden können:
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
oder
Hauptmenü
Finanzbuchhaltung
Primanota
Primanota
Direktsprung
[PRIMA]
oder
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Standardvorgänge Fibu
Variante „ungebuchte
Belege“
Direktsprung
[FISV]
und überall dort, wo die
Einzelbeleganzeige
aufgerufen werden kann.
Bereits erfasste oder aus der Warenwirtschaft
übertragene Belege können wieder gelöscht werden, falls festgestellt wird, dass
diese falsch oder doppelt erfasst wurden. Vor dem Löschen werden folgende
Prüfungen durchgeführt.
1.
Wird der Datensatz bearbeitet? Wenn dies der Fall ist, so erscheint folgende
Meldung und der Datensatz wird nicht gelöscht.
„Satz kann nicht gelöscht
werden, da von <Bedie
[...]


---

## Mahnvorschläge bearbeiten

Mahnvorschläge bearbeiten
Hauptmenü
Mahn-, Zahl-, Zinswesen
Mahnwesen
Mahnvorschläge bearbeiten
Direktsprung
[MHVB]
.
Die automatisch und manuell erstellten Mahnvorschläge
können dann bearbeitet werden.
Im Auswahlbildschirm stehen die Vorschläge
nach Listennummern und Kontonummer geordnet zur Verfügung. Nach Anwahl eines
Vorschlags bestehen u.a. folgenden Möglichkeiten:
Löschen
F7
Der komplette Mahnvorschlag kann gelöscht werden.
Freigabe
F6
Der Mahnvorschlag wird zur Mahnung übernommen
Mahnvorschlagsliste
F10
Drucken einer Crystal-Liste sämtlicher Mahnvorschläge.
Dort wird in der letzten Spalte die Mahnstufe angedruckt. Dies ist entweder die
neue Mahnstufe oder die Mahnstufe die im OP steht, falls diese Rechnung nur der
Vollständigkeit halber mit angedruckt wird (Einstellmöglichkeit in Mahngruppen
"Wie Mahnen“). Dann steht hinter der Mahnstufe ein Stern "*".  Ist die
Rechnung noch nicht fällig, ist also der Mahnstichtag kleiner als das
Fälligkeitsdatum, so werden diese Belege
[...]


---

## Mailverkehr

Mailverkehr
Der zugehörige Mail Verkehr wird über eine
Standardprozedur (di privatisiert werden kann) abgewickelt.

---

## Makro - Standardmakros zur Vorgangsverarbeitung

Makro
- Standardmakros zur Vorgangsverarbeitung
Feld
Beschreibung
Nachlaufmakro
Kontrollmakro
Test/Nachlauf – Unit
Test
      – SVMAIN
Test
      – SVWARE
Nachlauf – SVWARE
Expo
      Makroname
VIMP
      Kontrollmakro
Auswahl des Kontrollmakros für
Vorgangsimport
.

---

## Marktkasse

Marktkasse

---

## DBREXP-Event erstellen

DBREXP-Event erstellen
Felder
Start am / um
Datum und Uhrzeit, zu dem / der den
      Event das erste Mal ausgelöst werden soll
Start am / zwischen
Datum und Uhrzeit, wann das Event
      starten soll und zwischen welchen Uhrzeiten es ausgeführt werden
      soll
Wiederholung alle
Zeit-Zyklus in dem das Event
      wiederholt ausgelöst werden soll
Status
Aktiviert / Deaktiviert
Funtionen
Event anlegen F9
Richtet den Event zur Steuerung des
      SQL Remote-Nachrichtenagenten
dbremote
ein.

---

## Mein Tracefile in der Datenbank

Mein Tracefile in der Datenbank
Direktsprung
[
TRAW
]
Mit Hilfe dieser Variante lassen sich auf
übersichtliche Weise Recherchen innerhalb eines eingelesenen Tracefile
anstellen.
Zum jetzigen Zeitpunkt muss dazu über [OSQL] das
entsprechende Tracefile eingelesen werden. Der Inhalt wird dann in dieser
Variante zur Ansicht und Auswahl bereitgestellt.
Felder
Auswahlliste
wer
Bediener
Zeit
Zeitstempel
CurNo
Maske
Aeins-Maske
Verbrauch
Anweisungsdauer in
      Millisekunden
Err
Rückgabe-Status der
      Anweisung
So
      bedeutet „100“ z.B. dass der selektierte Datensatz nicht gefunden wurde.
      Es kommt sehr auf den jeweiligen Kontext an um zu beurteilen ob das ein
      Fehler ist oder nicht!
SQL
      Ausdruck
Informatorisch die
      SQL-Anweisung
Achtung, die wirkliche SQL-Anweisung
      kann wesentlich länger sein als das was in der Auswahlliste aus
      technischen Gründen maximal angezeigt werden kann!
Plan
Datenbank-Ausführungsplan der
      Anweisung
Status
Tech
[...]


---

## Menü-Hauptpunkte-Bereich

Menü-Hauptpunkte-Bereich
In diesem Bereich befinden sich die Menü-Hauptpunkte
und dienen der Gliederung und Strukturierung der zugeordneten
Hauptmenü - Menüpunkte
.
Die Menü-Hauptpunkte sind mit einem Icon und Tipptext
ausgestattet worden. Damit sollen sie optisch schneller erfassbar sein und somit
ein angenehmeres Arbeiten ermöglichen.
Durch einen Mausklick auf einen Menü-Hauptpunkt
wechselt der
Arbeitsbereich
jeweils auf die dem
Menü-Hauptpunkt zugeordneten
Menüpunkte
und im Menüpunktbereich wird die
Anzeige gemäß dem aktivierten Menü-Hauptpunkt angepasst.
Über die rechte Maustaste steht ein
Kontext-Menü
zur
Verfügung, dafür muss die Maus auf einem solchen Haupt-Menü-Punkt stehen, es ist
somit nicht notwendig ihn zu aktivieren.

---

## Mitglied Teilübertragung

Mitglied Teilübertragung
Mit dieser Funktion können einzelne Anteile an andere
Mitglieder übertragen werden.
Abgang:
Es werden zunächst die freiwilligen Anteile zum
Übertragen herangezogen. Übersteigt die ‚Anzahl Übertrag‘ die vorhandenen
freiwilligen Anteile wird für die Differenz von den Pflichtanteilen
genommen.
Zugang:
Für den Anteilstyp beim Zielmitglied der zu
übertragenen Anteile gibt es jetzt zwei Felder mit denen festgelegt werden kann
wie viele Pflichtanteile und freiwillige Anteile es beim Zielmitglied werden
sollen.
Diese Felder werden auf der Maske freigeschaltet, sobald eine ‚Anzahl
Übertrag‘ eingegeben wurde.
Die Funktion
Mitglied Teilübertragung SF5
öffnet
folgende Eingabefelder:
Felder
Zielmitgl. KndNr.
Hier
      wird die Kundennummer des Zielkunden angegeben.
Zieldatum
Das
      Datum zu dem die Anteile übertragen werden sollen.
Anzahl Übertrag
Hier
      gibt man die Zahl der zu übertragenen Anteile an.
Beim
      Bestätigen der eingetragenen Anzahl öff
[...]


---

## n/a

n/a

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

## Neue Post erstellen

Neue Post
erstellen
Hauptmenü
Büro und Internet
Büroumgebung
Referenz-ERP Post
Direktsprung
[POST]
In der Anwendung „A,eins Post“ erscheint nach Aufruf
der Funktion „
Neu
“
F8
folgender Bildschirm:
Mit der Funktion „
Senden
“
F9
erhalten alle ausgewählten Anwender die
unter Text erfasste Nachricht. Sollte der ausgewählte Anwender im System
angemeldet sein, so erhält dieser eine Mitteilung, dass eine Nachricht
eingegangen ist. Ist der Benutzer nicht im System angemeldet, wird ein für den
Anwender sichtbaren Eintrag in die Favoritenliste gesetzt. Dieser Eintrag wird
beim nächsten Anmelden in Referenz-ERP dargestellt.

---

## Newsticker

Newsticker
Informationen einmalig bereitstellen.
Die Idee ist, eine Information zu hinterlegen, und dem
Anwender zu signalisieren, dass es eine Information gibt.
Dabei soll das System nach Ansicht der Informationen
durch den Anwender diese Benachrichtung zurücknehmen.
Das Newsticker-System in Referenz-ERP bietet eben dies.
Ausgelöst wird das Verhalten durch die Referenz-ERP-Option
Newsticker.
Als Werte für die Option stehen folgende 3
Möglichkeiten zur Verfügung:
Keine Angabe. Dann wird standardmäßig die Dateiangabe
archivhinweis.html
verwendet!
Die Angabe „ARCHIV“. Dann werden die Informationen aus
dem Formulararchiv verwendet. Bitte beachten Sie, dass dies nur möglich ist,
wenn das Formulararchiv in der Datenbank ist.
Eine Dateianschrift. Also der Pfad und Name auf eine
zu behandelnde Datei.
Administriert wird über die Anwendung Newsticker mit
Direktsprung NEWS
Die Funktion „Reset“ erlaubt die unmittelbare
„Wiedervorlage“ der Dokumente.
Die Funktion Ändern ( F5 ) öffnet im Dateifalle di
[...]


---

## Notwendige Einstellungen

Notwendige
Einstellungen

---

## Nützliche Controlstrings für Buttons

Nützliche Controlstrings für Buttons
Funktion
Controlstring
Blätter an den Anfang der
      Ergebnistabelle
^smx_con_exec SDINTERFACE 1
      10
Blätter an das Ende der
      Ergebnistabelle
^smx_con_exec SDINTERFACE 1
      11
Einen Datensatz weiter Blättern
^smx_con_exec SDINTERFACE 1
      9
Einen Datensatz zurück
      Blättern
^smx_con_exec SDINTERFACE 1
      8
Speichern und nächster
      Datensatz
^smx_con_exec SDINTERFACE 1
      12
Zwischenspeichern
^smx_con_exec SDINTERFACE 6
      0
Aufruf Konteninformation
^jpl
      koi_call :Kontonummer [[[:Jahrnummer] :Bereich]
      :Kontogesperrt]
Wobei:
•
Wird als
Jahrnummer
0 übergeben, so wird das aktuelle Jahr
      verwendet.
•
Bereich
= „PK“ bedeutet nur Personenkonten
      in der Auswahl zulassen.
•
Kontogesperrt
=1 bedeutet, dass das Konto nicht
      geändert werden kann. Es stehen dann auch nicht die Blätterbuttons zur
      Verfügung.
Aufruf OP-Verwaltung
^jpl
      opv_call [:
Kontonummer [ :Perdatum

[...]


---

## Nützliche Controlstrings für Funktionen in einer F3-Auswahl (Itembox)

Nützliche Controlstrings für Funktionen in einer F3-Auswahl (Itembox)
Zu jeder F3-Auswahl kann eine eigene Optionbox mit
angegeben sein oder eine private Optionbox mit angehängt werden. An diese können
private Funktionen angehängt werden.
Funktion
Controlstring
Aufruf einer AIS-Maske mit Übergabe
      einer Ident.
^jpl
      ais_itemcall RETURNWERT AUFRUFART AISGRUPPE
Wobei:
•
RETURNWERT: Dies
      ist der Name des Datenbankfeldes, aus dem die an AIS übergebene Ident
      versorgt wird. Dieses Feld muss in der F3-Auswahl enthalten
      sein.
•
AUFRUFART: 5 für
      Ändern, 6 für Ansehen.
•
AISGRUPPE: Name
      der Gruppe
Aufruf eine Makros mit Übergabe
      einer Ident
^jpl
      ais_itemmakrocall MAKRO RETURNWERT PARAMETER1 PARAMETER2
Mit
      Hilfe des RETURNWERTS wird die an AIS zu übergebende Ident aus der
      F3.-Auswahl bestimmt. Dann wird das Makro mit folgenden Parametern
      aufgerufen:
call
      makro( ":MAKRO" , ":Ident aus RETURNWERT" , ":PARAMET
[...]


---

## Oberfläche - Prozeduren

Oberfläche - Prozeduren
BG
BT

---

## Oberfläche - Test

Oberfläche - Test
Die Registerkarte
Test
steht nur im Modus
Ändern
zur Verfügung.
Hier können die Ergebnisse eingesehen werden, welche
bei der Funktion
Prozedur testen
gesammelt werden.
Auf dem Register
Test
sind folgende Felder zu sehen:
Felder
Feldname
Der
      Feldname, des in der Prozedur befüllten Feld
Inhalt
Der
      Inhalt des entsprechenden Feldes
Aktuelle Prozedur
Die
      getestete Prozedur
Vorgangs Id
Die
      Id eines Vorgangs, auf welcher die Prozedur angewendet werden
      soll.
Wabew Id
Die
      id einer Warenbewegung, auf welcher die Prozedur angewendet werden
      soll

---

## Oberkonten zuweisen

Oberkonten zuweisen
Um ein Oberkonto einem vorhandenen Gesellschafter
zuzuordnen wird der Gesellschafter in der Auswahlliste ausgewählt mit
F5
zum
Bearbeiten
geöffnet und die Funktion
Oberkonto zuweisen
SCF7
ausgewählt.
Jetzt kann dem Gesellschafter ein Oberkonto zugewiesen
werden. Bei der Zuweisung werden alle Anteile und Bewegungen von diesem Konto
entfernt. Diese sind im neuen Oberkonto nachzutragen.

---

## Optionen (F10)

Optionen (F10)
Wenn man unter OSQL die Funktion
Optionen
F10
auswählt, so öffnet sich folgender
Dialog mit zwei Reitern:
Anwendung:
(F3)
      Arbeitsverzeichnis
(F3)
      Dateinamenserweiterung
(F3)
      Zuletzt verwendete Datei
Diese Einstellungen beziehen sich
      auf die Dialogmaske, die man über die Funktion
SQL ausführen
F3
erreicht.
(F9)
      Arbeitsverzeichnis
(F9)
      Datei
(F9)
      Dateinamenserweiterung
Diese Einstellungen beziehen sich
      auf die Dialogmaske, die man über die Funktionen
Sichern Eingabe
SCF9,
Ausführen Statement
CF9
und
Editieren Statement
SF9
erreicht.
Ausgabedatei
Dieser Dateiname wird dort als
      Vorbelegung verwendet, wo OSQL Daten  in eine Datei schreiben
      soll.
Bei
      TAB Tabellennamen ergänzen
Es
      wird, wenn man die TAB-Taste drückt, der nächste Tabellenname – bei
      Shift-TAB der vorherige – ergänzt.
Beispiel:
Select * from Waehr
<TAB>
Ergibt
Select * from WaehrIsoList
Beim
      erneuten drücken von Tab

[...]


---

## OP Saldo

OP Saldo
Der OP Saldo wird per Prozedur bestimmt, die
privatisiert hinterlegt werden kann

---

## PDF-Dokument signieren:

PDF-Dokument signieren:
1.
Das PDF-Dokument wird geöffnet und das Signatur Pad zum Signieren
vorbereitet.
Die Dauer dieses Vorgangs ist abhängig von der Größe des
Dokuments. Im Standardfall wird durch Sh+F8 die Unterschriftsfläche
aktiviert.
2.
Es kann jetzt auf dem Signatur Pad unterschrieben werden.
o
Mit der Schaltfläche
„Wiederholen“ (Bild: 2 Pfeile) auf dem Signatur Pad wird die Unterschrift
verworfen und es kann erneut unterschrieben werden.
3.
Mit der Schaltfläche „Bestätigen“ (Bild: Haken) auf dem Signatur Pad wird die
Unterschrift bestätigt und in das PDF-Dokument eingefügt. (Nicht auf dem
PC-Bildschirm bestätigen)
4.
In dem PDF-Anzeigeprogramm die Schaltfläche „Speichern unter …“ (Bild: Diskette
und Bleistift) drücken.
5.
Als Verzeichnis das „Signatur-Importverzeichnis“ auswählen/eingeben. (siehe
Anweisung „
Speicher-Pfad für signierte
PDF-Dokumente ermitteln
“).
6.
Schaltfläche „Speichern“ drücken und PDF-Anzeigeprogramm beenden.
7.
Das PDF-Dokume
[...]


---

## PDF-Dokument auswählen:

PDF-Dokument auswählen:
1.
Direktsprung [ORDNER] in die Dokumentenverwaltung ausführen.
2.
Zu signierendes PDF-Dokument selektieren und die Schaltfläche „PDF signieren“
drücken.

---

## Pflege der Vorgangsklassen

Pflege der Vorgangsklassen

---

## Plandaten

Plandaten
Plandaten lassen sich auf verschiedene Ebenen
erfassen:
1)
Für Konten
und Kostenstelle.
2)
Für Konten
und Kostenträger
.
3)
Für Konten, Kostenstellen und Kostenträger.
Die Erfassung der Planzahlen für die Kombination aus
Konto, Kostenstelle und Kostenträger erreicht man über den Direktsprung
[PLAN]
.
Neben der einfachen Erfassung stehen noch folgende
Funktionen zur Verfügung
•
Vorjahresplandaten: Die zu diesem Kostenträger und Konto im Vorjahr
erfassten Werte werden automatisch in die Soll und Habenspalte übernommen.
•
Plandaten aus 1.Periode: Die Werte, die in Periode 1 eingetragen wurden,
werden in alle anderen Perioden übernommen.
•
Übernahme Plandaten: Es öffnet sich eine weiter Maske, in der der Bereich
abgefragt wird, aus dem die Planzahlen übernommen werden sollen.

---

## Portefeuille

Portefeuille
Hauptmenü
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Portefeuille
Direktsprung
[
WEP
]
Der Bereich Portefeuille dient dazu, bei großen
Wechselbeständen die Wechsel in Bereiche einzuteilen.
Hier kann festgelegt
werden, ob der Wechsel diskontierfähig ist.
Beschreibung
Portefeuille Nr
Laufende Nummer, die als Verweis in
      anderen Tabellen verwendet wird.
Diskontierbar
Ob
      für einen Wechsel dieser Gruppe eine Diskontabrechnung erstellt werden
      darf.
Bezeichnung
Ausführliche Bezeichnung

---

## Positionsteil

Positionsteil

---

## POS-Kasse

POS-Kasse
Die POS-Kasse und Tresenkasse unterscheiden sich im
Wesentlichen nur in ihrer Handhabung.
Während die Tresenkasse ein Modul ist, bei dem in
verschiedenen Masken umfangreiche Funktionen zur Behandlung von Barvorgängen zur
Verfügung stehen, ist die POS-Kasse ein Modul, das einen zügigeren Ablauf bei
der Erfassung von Barverkäufen bietet. Dieses wird durch einen Druck ermöglicht,
der parallel zur Erfassung abläuft und außerdem den Erfassungsmodus für
Artikelerfassung und Bezahlung auf einer Maske zulässt sowie das Anlegen und
Abschließen des Vorgangs.
Diese Art der Erfassung bezieht sich ausschließlich
auf Barverkäufe, d.h. Bareinkäufe und Bargutschriften müssen über die
Tresenkasse abgewickelt werden; für Einzahlungen, Abschöpfungen,
Zahlungsmeldungen,... steht das Zahlungsmodul zur Verfügung;
Kasseneröffnungen/Abschlüsse müssen wie gewohnt durchgeführt werden.
Es wird auf denselben Tabellen (Daten) gearbeitet, so
dass auch die Übersichten nutzbar sind.
Bemerkungen:
[...]


---

## Prüfung im Vorgang:

Prüfung im Vorgang:
Prüfung
Während der Vorgangserfassung kann in Abhängigkeit der
Einstellung im
SPA 1062 – UstId Prüfung
im Vorgang
die Umsatzsteuer-Id auch asynchron im Vorgang geprüft werden.
Auswertung
Die Auswertung dieser Prüfung muss wegen der
Vielfältigkeit der daraus abzuleitenden Konsequenten jedoch individualisiert
erfolgen.
Dazu kann zum einen aus dem Vorgang ermittelt werden,
ob eine Prüfung vorgesehen war:
select amic_func_bit_test(
V_VorgBits1, 4)
from amic_v_vorgaenge
where v_id = ???;
Anschließend kann, sofern eine Prüfung vorgesehen war
(Ergebnis 1) das Ergebnis aus der Auftragstabelle abgelesen werden:
select *
from UmsatzSteuerIdPruefAuftrag PA
join amic_v_vorgaenge vs on vs.v_guid = PA.v_guid and
vs.UstId_Kunde = PA.UstId
where v_id = ???;

---

## Printer

Printer
-500001
keine Details verfügbar
-500002
keine Details verfügbar
-500003
keine Details verfügbar

---

## Private Tabellen

Private Tabellen
Man kann in AIS eigene private Tabellen definieren und
ist nicht mehr auf die vorgegebenen eingeschränkt. Will man für diese Tabellen
mit Hilfe der Maske
Aezaddon
(und
Varianten von dieser Maske) Daten erfassen, so muss diese Tabelle mindestens das
Feld
ident
haben und in der Tabelle
ident
muss ein Eintrag für diese
Tabelle existieren. Will man also z.B. eine Tabelle für Geschäftsvorfallkodes
erstellen, in der ein Feld für den Kode (integer) und ein Feld für den
Beschreibungstext (char(255)) enthalten sein soll, so müsste das Statement für
die Tabelle wie folgt aussehen:
create table
admin.p_Geschaeftsvorfaelle
( Ident integer,
Kode integer,
Beschreibgung
char(255),
primary key (ident)
)
Zusätzlich muss dann noch ein Eintrag in der Tabelle
ident
erzeugt werden:
insert into ident
( IdentTableName, IdentColumnName, IdentIdent,
IdentAktivKont, IdentAngefKont)
Values
( ' p_Geschaeftsvorfaelle ', 'Ident', 0, 1,
0)
Hinweis:
Hat man vergessen einen Eintrag in
der
[...]


---

## Problembehandlung

Problembehandlung
Leider kann es vorkommen, dass bei der Ausführung von
Crystal Report Probleme auftreten. Je nach Schwere des Fehlers muss entschieden
werden, was zu unternehmen ist. Hier folgen einige Tipps, wo man nachsehen kann,
was nicht stimmt.
1.
Nachsehen in der Systeminformation. Direktsprung
[SYSIN]
In der Systeminformation im
Register Umgebung wird im Feld
Version Crystal Report
die Version des
installierten Reports angezeigt.
Wenn die Version, die auf dem Rechner
gefunden wurde, nicht der erwarteten Version entspricht, so wird das Feld rot
eingefärbt und im Tiptext steht die erwartete Version.
Ist dies der Fall, so
muss herausgefunden werden, welches Programm diese Crystal-Version installiert
hat. Es muss dann deinstalliert werden. Anschliessend muss lediglich die Crystal
Engine vom Aeins-Setup neu installiert werden. Dazu kann man einfach im
benutzerdefinierten Setup alle Punkte bis auf Crystal Report abwählen, damit nur
dieser Schritt wiederholt wird.
Danach k
[...]


---

## Projektkontrolle

Projektkontrolle
Zur Projektkontrolle stehen folgende Möglichkeiten
bereit:
Zeitgestützte Bildschirmanzeige
Ereignisgestützte Wiedervorlage
Mailbasierende Ereignisse
Die schnellste und einfachste Möglichkeit zur
Überwachung von Projekten ist die automatische Auswahlliste. Hier lässt sich per
einfachem Schalter im SPA Bereich sofort eine kontrollierte Übersicht
möglich.

---

## Projektbearbeitung

Projektbearbeitung
Zu jeder Zeit kann das Projekt wieder geöffnet werden,
als Besonderheit ist zu beachten, dass ein Projekt immer einem Mitarbeiter
zugeordnet ist, ist es noch nicht zugeordnet, so wird der Mitarbeiter beim
Öffnen eingetragen, der es öffnet, diese Zuordnung kann aber auch abgelehnt
werden.

---

## Properties anzeigen

Properties anzeigen
Zeigt die Eigenschaftswerte eines Feldes an.

---

## Prolongation / Verlängerung eines Wechsels bei nicht weitergebebenen Wechseln

Prolongation / Verlängerung eines Wechsels bei nicht weitergebebenen
Wechseln
Hauptmenü
Finanzbuchhaltung
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechsel bearbeiten
Direktsprung
[
WEB
]
Kann der Bezogene am Verfalltag die Wechselsumme nicht
bezahlen, dann besteht die Möglichkeit der Prolongation, also der Verlängerung
der Zahlungsfrist. Dazu muss man in der Anwendung
Wechsel bearbeiten
den
Wechsel auswählen und mit F5 ändern. Dort steht einem die Funktion
F9
für
Prolongation
zur Verfügung
Es wird im Wechselstamm ein neuer Wechsel mit dem
ehemaligen Verfallsdatum als Ausstellungsdatum hinterlegt. Es erfolgt jedoch
keine Buchung in der FiBu
!
Der alte Wechsel wird als verlängert gekennzeichnet.
Folgende Prolongationsstati sind implementiert:
0
Originalwechsel nicht verlängert
Gültig
1
Originalwechsel verlängert
Verfallener Wechsel aus Status 0
2
Verlängerter (neuer) Wechsel
(folgt auf Status 0 oder 3)
3
Erneut verlängert
Verfallener Wechsel aus Status
  2

---

## Protokoll ansehen

Protokoll ansehen
Die aktuelle Protokolldatei wird angezeigt ( mit
NOTEPAD, anschließend wieder schließen !)

---

## Protokollwesen

Protokollwesen
Direktsprung
[PW]
Im Fehlerprotokoll werden Systemhinweise gesammelt. Im
Zusammenhang zum Beispiel mit Archiv-Import-Problemen wird auf weitere
Informationen auf Protokolleinträge in dieser Anwendung verwiesen.

---

## Prozeduren

Prozeduren

---

## Radio-Button und Check-Box per Makro abfragen/setzen

Radio-Button und Check-Box per Makro abfragen/setzen
Der Zugriff auf den Inhalt von Radio-Button und
Check-Boxen funktioniert nicht so, wie bei einfachen Eingabefeldern. Um von
einem Makro aus auf den Inhalt von Radio-Buttons bzw. von Check-Boxen zugreifen
zu können, muss man mit den Funktionen SM_PROP_ID und SM_PROP_GET_X_INT
arbeiten. Es folgen zwei Hilfsfunktionen zum Abfragen und Setzen der Haken:
function BoxStatus(NameBox : String; Zeile :
integer):integer;
var
CheckBox_ObjId:
integer;
begin
CheckBox_ObjId
:= sm_prop_id(NameBox );
BoxStatus      := sm_prop_get_x_int(CheckBox_ObjId,
zeile, 125);
end;
Die Hilfsfunktionen „BoxStatus“ – gültig für Check-Box
und Radio-Button – liefert für den Name und die Zeile 0 für nicht ausgewählt und
1 für ausgewählt zurück.
Procedure SetBoxStatus(NameBox : String; Zeile :
integer; Status : integer);
var
CheckBox_ObjId:
integer;
begin
CheckBox_ObjId
:= sm_prop_id(NameBox );
sm_prop_set_x_int(CheckBox_ObjId, zeile, 125, Status);
end;
D
[...]


---

## Rechnung erfassen

Rechnung erfassen
Hiermit wird die Vorgangserfassung aktiviert.

---

## Registerkarte Gruppen

Registerkarte Gruppen

---

## Registerkarten in OLAP

Registerkarten in OLAP
Sie sehen im rechten Bereich der Anzeige drei
Registerkarten:
Pivot
Hier wird die Pivottabelle angezeigt
(Standardeinstellung)
Grafik
Hier wird die grafische Auswertung, das Chart
angezeigt.
Rohdaten
Hier werden nur die Rohdaten angezeigt, wie sie mit
dem Auswahllisten-SQL ausgewählt werden.
Filter
Hier werden die Filtereinstellungen der zu Grunde
liegenden Auswahlliste angezeigt.

---

## Reisekosten

Reisekosten
Für Reisekosten gibt es eine extra Steuerformel, da
die Vorsteuer hier "im Hundert" gerechnet wurde. Diese Regelung ist jedoch
mittlerweile überholt
. Bekanntlich gelten seit 01.04.1999 normale
Steuermethoden, die keine "in Hundert" Rechnung erfordern.
Vorsteuer auf Reisekosten müssen "in Hundert"
gerechnet werden. So enthalten € 100,-- Reisekosten z.Zt. 9,80 Vorsteuer. Bei
der Einrichtung des Steuersatzes für die Steuerklasse 102 (Vorsteuer Brutto) ist
folgendes zu beachten:
Feld
Beschreibung
Steuergruppe
0
      (Sachkonten)
Steuerformel
Reisekosten (in Hundert)
AW-Kennz. Umsatz
0,
      da nicht auszuweisen auf der USTVA
Steuer
In
      der Beispielliste oben wäre es Zeile 47 und somit Kennziffer 66. In der
      USTVA 2002 findet man die Einfuhrumsatzsteuer in Zeile 55.

---

## Relationsbeschreibung

Relationsbeschreibung
Relation ScriptParam
Attribut
Typ             Länge,
...Defaultwert
NULL  PKey
ScriptPPBedKorr
integer     4 0
0
N  N
ScriptPBesitzer
integer     4 0 .................... N  N
ScriptPBezeich
char       50 0 .................... N
N
ScriptPId
char       20 0 .................... N
Y
ScriptSystem
smallint    2 0 .................... N  N
Relation ScriptParamPar
Attribut
Typ             Länge,
...Defaultwert
NULL  PKey
ScriptPId
char       20 0 .................... N
Y
ScriptPPAktiv
smallint    2 0
0
N  N
ScriptPPBedKorr
integer     4 0
0
N  N
ScriptPPBezeich
char       50 0 .................... N
N
ScriptPPId
[...]


---

## Release Notes

Release Notes
Die Releasenotes können
auf unserer Hilfe
Seite
angesehen werden.

---

## Reporte exportieren

Reporte exportieren
Hat man einen Report zu einer Auswahlliste erstellt,
so kann man diesen nicht nur drucken, sondern auch in vielfacher Form
exportieren. Dieser Export lässt sich auch automatisieren um ggf. nachts die
Daten zur Analyse vorzubereiten. Die geschieht mit folgendem Controlstring:
^jpl AWEport (Anwendung, Variante, Profil, Ansicht,
Reportbezeichnung, Ausgabeformat, Ausgabedatei)
Bedeutung
Anwendung, Variante
Hiermit wird beschrieben, welche
      Anwendungsvariante die Daten liefert
Profil
In
      diesem Profil hat man die Eingrenzung festgelegt.
Ansicht
Die
      Ansicht ist Optional. Wenn man hier einen Leerstring übergibt, so wird die
      Standardansicht verwendet.
Reportbezeichnung
Die
      Bezeichnung des Reports, den man unter
Report bearbeiten
angegeben hat und
      der unter
Report drucken
zu
      sehen ist.
Ausgabeformat
Hier
      muss eine Zahl angegeben werden. Es stehen folgende Formate zur
      Verfügung:
Pdf =
      0,
Html =
      1,

[...]


---

## Reporte verwalten

Reporte verwalten
Wenn man Reporte (Listen, Etiketten, Karteikarten)
erstellt, so erscheint als erstes folgender Dialog.
Die Funktionen
„speichern als“
,
„umbenennen“
, und
„löschen“
sind erst aktiv, wenn man einen
bereits erstellten Report erneut bearbeitet. Die Funktion
„mit Template weiter“
erscheint nur wenn
man eine neue Liste erstellen möchte.
Bedeutung
speichern als
Hier
      kann man den Report kopieren. Dazu wird die Ansicht – diese muss für die
      Variante existieren – und der Reportname abgefragt.
umbenennen
Hat
      man sich in der Bezeichnung vertan oder möchte sie aus anderen Gründen
      ändern, so kann man dies hier tun.
löschen
Funktion zum Löschen eines
      Reports.
mit
      Template weiter
Diese Funktion steht nur für den
      Projekttypen „Liste“ zur Verfügung. Es wird eine einfache Liste erstellt,
      in der alle sichtbaren Felder der Auswahlliste in einer Datentabelle
      aufgelistet werden. Man gelangt in den Branchen-ERP-Etikettendruck, in dem
[...]


---

## Reporte zu Vorgängen

Reporte zu Vorgängen

---

## Report Leergutbestätigung

Report Leergutbestätigung
Hauptmenü
Nebenbuchhaltungen
Leergut
Leergutbestätigung
Dieser Report wurde nicht für den allgemeinen Gebrauch
entworfen, sondern für eine sehr spezielle Arbeitsweise ausgelegt.
Normalerweise ist die Auswahl eines Wirtschaftsjahres
vorgesehen. Der ausgewiesene Alt-Saldo bezieht sich dann auf das Vorjahr.
Steuerparameter 487
muss eingeschaltet sein.

---

## Sammelbereich

Sammelbereich
-10001
keine Details verfügbar
-10002
keine Details verfügbar
-10003
keine Details verfügbar
-10004
keine Details verfügbar
-10005
keine Details verfügbar
-10006
keine Details verfügbar
-10007
keine Details verfügbar
-10008
keine Details verfügbar
-10009
keine Details verfügbar
-10010
keine Details verfügbar
-10011
keine Details verfügbar
-10012
keine Details verfügbar
-10013
keine Details verfügbar
-10014
keine Details verfügbar
-10015
keine Details verfügbar
-10020
keine Details verfügbar
-10021
keine Details verfügbar
-10022
keine Details verfügbar
-10023
keine Details verfügbar
-10024
keine Details verfügbar
-10025
keine Details verfügbar
-10026
keine Details verfügbar
-10027
keine Details verfügbar
-10028
keine Details verfügbar
-10029
keine Details verfügbar
-10030
keine Details verfügbar
-10031
keine Details verfügbar
-10032
keine Details verfügbar
-10033
keine Details verfügbar
-10034
keine Details verfügbar
-10035
keine Details verfügbar
-10036
keine Details verf
[...]


---

## Schecks über Formulartyp 201 drucken

Schecks über Formulartyp 201
drucken
Es existieren zu diesem Typ folgende
Formularbereiche:
•
500 Kopf Scheckschreibung

Formularkopf
•
502 Folgekopf Scheck

Folgekopf
•
503 Positionszeile Scheck

Zeilentyp
•
504 Alternativteil Scheckdruck

Zeilentyp
•
508 Zwischenabschluss Scheck
           Fuß
•
510 Abschluss Scheck

Abschluss
Folgende Variablen sind in allen Teilen (Kopf, Fuß und
Zeilentyp) verfügbar. Formularbereiche, die nicht separat mit aufgeführt werden,
enthalten nur Festtext oder diese Felder!
Bezeichnung
Typ
Nr.
Bedeutung
Datum
5
Datum der
      Scheckschreibung.
Schecknummer
Num.
4
Fortlaufende Nummer des Schecks, die
      in der Maske erfasst wird.
Betrag
Num.
4
Gesamtbetrag in der Form
      1.000,00
Betragstern
Text
3
Gesamtbetrag in der Form
      ******1.000,00*
Betragbuchst
Text
3
Gesamtbetrag in der Form
/Eins/Null/Null/Null//Null/Null
Betragbuchst1
Text
3

[...]


---

## Scannerrücksetzung

Scannerrücksetzung
Mit der Eingabe von „9999“ werden alle Scannungen
rückgäng gemacht.

---

## Schnellkorrektur

Schnellkorrektur
Die Schnellkorrektur ermöglicht die Positionen
ausgewählter Belege mengenmäßig zu korrigieren, Restbelege zu erstellen und
Partien zuzuordnen. Nach Auswahl der Belege werden die Positionen in einem
Bearbeitungsfenster dargestellt. In diesem Fenster können die Mengenangaben
durch Überschreiben im Vorgang verändert werden.
Funktionen
Restbeleg bilden
[F8]
Ein Eintrag in der Spalte „Rest“ zusammen mit der
Funktion
Restbeleg bilden
führt zu
einem zusätzlichen (Rest-)Beleg mit dieser Position und Menge. Die Belege sind
anschließend nicht miteinander verknüpft; der (Rest-)Beleg entspricht einem neu
erfassten.
Geb.Anzahl wechseln
[F9]
Bei einer Gebindeposition kann zwischen der
Gebindeanzahl und der Ergebnismenge gewechselt und der Mengeneintrag vorgenommen
werden. Nach der Änderung der Gebindeanzahl / Ergebnismenge kann diese Funktion
nicht erneut ausgeführt werden.
Partieverteilung
[F6]
Einer Position können eine oder mehrere Partien durch
Eingabe von Menge und
[...]


---

## Schriftart auswählen (nur Auswahlliste 2.0)

Schriftart auswählen (nur Auswahlliste 2.0)
Die Funktion Schriftart auswählen steht mit der
Auswahlliste 2.0 zur Verfügung. Wird diese Funktion ausgewählt, so öffnet sich
ein Dialogfenster, in dem eine Schriftart sowie Schriftschnitt und Schriftgrad
auswählen kann.
Die hier ausgewält Schriftart wird pro Anwender
gespeichert. Sie bezieht sich auf den gersammten anzeigebereich des Datengrids.
Die Menüs werden nach wie vor in der Standardgröße von Referenz-ERP angezeigt.

---

## Schritt 3: Reklamation erstellen

Schritt 3: Reklamation erstellen
3.1: Vorgang erzeugen
Mit dem Direktsprung [REKLAM] navigiert man in das
Reklamationsmodul. Hier kann ein neuer Datensatz mit (F8) erstellt werden.
In der Kaste „Reklamation“ kann das Datum, der
Bearbeiter, der Geschäftsbereich des Bearbeiters, die Gründe und die
Beschreibung der Reklamation, hinterlegt werden.
Die Kaste Reklamierer ist i.d.R. für den Kunden. Hier
werden auch alle relevanten Daten in Bezug auf den Reklamierer hinterlegt.
Sowohl die Kunden-Nr. als auch der jeweilige Vorgang in Bezug auf den Kunden
müssen hier eingetragen werden. Für die Reklamation ist es außerdem wichtig,
dass die Kaste „Artikel-Reklamierer“ mit der Ware (und Menge) gefüllt wird,
welche im Vorgang angegeben ist.
Die Kaste Verursacher ist gedacht für z.B. Lieferanten
oder andere Verursacher der Reklamation. Die Datenfelder sind die gleichen, wie
in der Reklamierer Kaste. Hier müssen in der Kaste „Artikel-Verursacher“ die
Artikel eingetragen werden, welche im V
[...]


---

## Scripting

Scripting
-300000
angefordertes Script nicht in der Datenbank

---

## Serienbrief

Serienbrief
Die Serienbrieffunktionalität wurde für die
Auswahlliste 2.0 neu entwickelt. Sie beruht auf einer Excel-Datei (*.xls) als
Datenquelle und arbeitet ohne Word-Vorlagen. Die vorherigen Methoden zum
Erstellen von Serienbriefen findet man weiterhin unter „Druck /
Quickreport“.

---

## Serienbrief bearbeiten

Serienbrief bearbeiten
Um einen bestehenden Serienbrief zu bearbeiten, wählt
man im Menüband die Funktion
„Word /
Serienbrief“
auf. In dem sich öffnenden Menü erscheinen nun neben der
Funktion „(Neu)“ auch die neu erstellten Serienbriefe.
Wählt man einen der Serienbrief aus, so öffnet sich
der Bearbeitungsdialog, in dem man ggf. die Beschreibung ändern kann.
Die Funktion
„löschen“
löscht den Eintrag aus dem Menü.
Das Dokument selbst bleibt im Archiv erhalten.
Bei
„speichern unter“
wird nach einer neuen
Bezeichnung gefragt unter der dieser Serienbrief gespeichrt werden soll.
Existieren noch ungespeicherte Änderungen am Original, so wird man ggf. noch
gefragt, ob man diese vorher speichern möchte.
Mit
„bearbeiten“
wird das Dokument wieder
geöffnet. Um wieder auf die Seriendruckfelder zugreifen zu können, muss die
Frage, ob man den SQL-Befehl ausführen möchte, mit Ja beantwortet werden.
ACHTUNG:
Beim Beenden des
„Serienbrief verwalten“- Dialogs wird gefragt, ob man die Änderung
[...]


---

## Serienbrief neu verknüpfen

Serienbrief neu verknüpfen
Um Serienbriefe mit einer Variante zu verknüpfen,
wählt man im Menüband die Funktion „Word / Serienbrief“ auf. Ist diese Funktion
deaktiviert, so liegt es entweder daran, dass keine Daten ausgewählt wurden oder
daran, dass die Daten gruppiert dargestellt werden.
Es öffnet sich das Menü, bei der in der ersten Zeile
die Funktion „Neu“ erscheint.
Wählt man diese Funktion aus, so öffnet sich folgender
Dialog.
Schritt 1:
Word Dokument auswählen. Dazu klickt
man auf das Ordner-Symbol links oben oder verwendet die Funktionstaste
F3
. Es öffnet sich ein Dialog, in dem man
eine existierende Datei auswählen kann oder eine neuen Dateinamen angeben kann.
Wird ein nicht existierendes Document ohne Extension angegeben, so wird
automatisch „docx“ verwendet. Der Name des Word-Dokumts erscheint später im Menü
als Auswahlpunkt. Pro Variante muss der Name des Dokuments eindeutig sein.
Hinweis:
Der Name des Dokuments kann
später nicht mehr geändert werden.
Schritt 2:

[...]


---

## Sicherheitsrelevante Einstellungen im EXCEL Umfeld

Sicherheitsrelevante
Einstellungen im EXCEL Umfeld
Standardmäßig wird Excel System ein Zugriff auf
externe datenquellen unterbunden. Um bequem und ohne Zwischenfragen auf die
Datenquellen zugreifen zu können, sollten folgende sicherheitstechnische
Einstellungen verändert werden:
Es kann natürlich eine digitale Signatur der
eingebetteten Makros vorgenommen werden, ist aber nur mit viel Aufwand machbar.
Sinvoller erscheint die Frage, ob der Anwender ein Verbot auf „Download Makros“
bekommt, um dem Risiko der Virus Infizierung zu begegnen.

---

## SKR03 / SKR04 Übernehmen

SKR03 / SKR04
Übernehmen
Referenz-ERP
bietet die Möglichkeit, die DATEV – Kontenpläne SKR03 und SKR04 zu
übernehmen. Man erreicht den Programmpunkt über die Direktsprünge
[SKR03]
bzw.
[SKR04]
.
Beim Einspielen müssen folgende Punkte beachtet
werden:
1.
Die Einspielung  kann nur dann geschehen, wenn noch keine Buchungen in der
Fibu erfolgt sind. Eventuell alte Testdaten müssen vorher gelöscht werden. Die
kann mit dem
Nullsetzer
geschehen.
2.
Durch die Einspielung werden die Sachkonten, ggf. Oberkonten, Druckpositionen,
Forderungsgruppen, Erlöskennziffern und Steuersätze gelöscht und neu
eingetragen.  Einige Stammdaten müssen eventuell angepasst werden:
•
Hausbanken
•
Zinsgruppen / Zinsabschlag Stammdaten
•
Mahnsätze
•
Währungskurse
•
Wechselbuchhaltung
•
Mandantenstamm
•
Erlöszuordnungen
•
Forderungsgruppen
•
Steuern
3.
Überprüfen Sie die Zählkreise.
Der Oberkontenzählkreis liegt nach der
Einspielung im Bereich 900.000 - 999.999, der Sachkonten-Zählkreis im Bereich 1
- 9999.
[...]


---

## SMTP-Basis

SMTP-Basis
-13000
Es ist ein Fehler bei der Vorbereitung zur Versendung
einer E-Mail über das Datenbankmailsystem aufgetreten. Nähere Informationen
werden im Fehlertext beschrieben.
-13001
Es ist ein Fehler bei der Versendung einer E-Mail über
das Datenbankmailsystem aufgetreten. Nähere Informationen werden im Fehlertext
beschrieben.

---

## Sonstiges

Sonstiges

---

## Sortierung der Auswahlliste

Sortierung der Auswahlliste
Referenz-ERP bietet die Möglichkeit Auswahlliste oder
F3-Auswahl nach mehreren Spalten in beliebiger Reihenfolge auf- oder absteigend
zu sortieren. Eine Sortierung für Auswahllisten oder F3-Auswahl, deren
Select-Statement aus einer Vereinigung (UNION) besteht, ist nicht möglich.
In der Auswahlliste 2.0 wird diese Maske über das
Darstellungsregister aufgerufen. Sortierungen in der F3-Auswahl 2.0 werden
direkt durch Klicken in die Titelzeile angegeben. Die Gruppierung wird nur in
der Auswahlliste 2.0 ausgewertet.
Um eine Auswahlliste oder eine F3-Auswahl im alten
Design zu sortieren, kann über einen Mausklick auf eine Spaltenüberschrift die
Sortierungsmaske aufgerufen und dort die Sortierung festgelegt werden. Hier wird
die angewählte Spalte automatisch der Sortierung/Gruppierung in aufsteigender
Richtung mit dem maximalen Index +1 hinzugefügt.
Folgende Felder werden in der Sortierungsmaske
angezeigt:
Bedeutung
Spaltenname
Titel der Spalte in der
      A
[...]


---

## Speichern unter auf Positionsebene

Speichern unter auf Positionsebene
Sofern eine Auswahlliste mit Vorgängen auch die
Einzelpositionen mit anzeigt, ist es möglich, mit der „Speichern unter“ Funktion
einzelne Warenpositionen verschiedener Belege auf einen neuen Beleg zu kopieren,
z.B. auf einen Bestellbeleg.
Im obigen Beispiel sind alle Basisweizen Lieferungen
angewählt worden, um hieraus eine Bestellung an den Saatgutlieferanten erstellen
zu können.
Wird bei der Schnellerfassung mit der Maus auf die
Spalte Anz positioniert, so zeigt das System auch die Gesamtmenge an, um ggf.
aus mehreren Einzelpositionen eine Gesamtposition zu machen.
Positionen, die als Anz eine 0 eingetragen haben, und
aus dem Modul „Speichern unter“ kommen, werden trotzdem im Zielbeleg mit
aufgeführt, um ggf. später bei der Verteilung auf den Ursprung zurückgreifen zu
können.
Nbb.: Das Feld WabewErfassId wird mitgeführt, d.h. es
kann nachvollzogen werden, welche Bestellposition zu welchem Lieferschein
gehörte.

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

## Spezialfelder

Spezialfelder
Es existieren einige Feldbezeichnungen, die eine
spezielle Bedeutung haben.
LILAANZAHLKOPIEN
Der Wert, der im ersten Satz für dieses Feld
zurückgeliefert wird, bestimmt die Anzahl der Kopien, die für diesen und alle
folgenden Datensätze verwendet wird. Dieses Feld wird ignoriert, wenn in den
Druckerprofilen
der Reportdefinition
eine feste Anzahl eingetragen wurde.
LILAANZAHLVARKOPIEN
Mit diesem Wert wird festgelegt, wie viele Kopien
gedruckt werden sollen, und zwar pro Datensatz. D.h. Es ist möglich zu sagen,
dass der erste Datensatz 4-mal, der zweite 3-mal, der dritte 5-mal usw. gedruckt
werden soll. Dieses Feld übersteuert LILAANZAHLKOPIEN, wird jedoch ignoriert,
wenn in den
Druckerprofilen
der Reportdefinition
eine feste Anzahl eingetragen wurde.
BARCODE
Wenn als Feldbezeichnung BARCODE gefunden wird, so
wird der Wert in allen Barcode-Formaten an den Designer/Listengenerator
übergeben.  Von Referenz-ERP werden dann folgende Variablen erzeugt. Eine
vollständige Li
[...]


---

## Spezielle Tastenschlüssel

Spezielle Tastenschlüssel
Remarks
Use the
SendKeys
method to send keystrokes to
applications that have no automation interface. Most keyboard characters are
represented by a single keystroke. Some keyboard characters are made up of
combinations of keystrokes (CTRL+SHIFT+HOME, for example). To send a single
keyboard character, send the character itself as the
string
argument. For example, to
send the letter x, send the
string
argument "x".
Note
To send a
space, send the string " ".
You can use
SendKeys
to send more than one
keystroke at a time. To do this, create a compound string argument that
represents a sequence of keystrokes by appending each keystroke in the sequence
to the one before it. For example, to send the keystrokes a, b, and c, you would
send the string argument "abc". The
SendKeys
method uses some characters
as modifiers of characters (instead of using their face-values). This set of
special characters consists of parentheses, brackets, braces, and the:
plus
[...]


---

## Spezielle Systemhinweise

Spezielle Systemhinweise
Die System-Routinen zum Einstellen von Systemhinweisen
ins Fehlerprotokoll reichern den Hinweis um folgende zusätzliche
Umgebungs-Informationen zum Zeitpunkt der Auslösung an:
Zusatz
Anwendung
Referenz-ERP-Anwendung
Variante
Referenz-ERP-Variante
Maske
Maske
Optionbox
Optionbox
Funktion
Funktion
Formularid
Im
      Druckumfeld die Nummer des Formulars
Damit kann es u.U. leichter sein den Systemhinweis
zuzuordnen.

---

## Spezielle Vorlauf-Funktion

Spezielle Vorlauf-Funktion
Es gibt von Branchen-ERP eine mitausgelieferte
Vorlauffunktion. Diese sucht die Daten aus der zugrundeliegenden Auswahlliste
zusammen und schreibt die Werte der Felder die hinter dem Schlüsselwort IDENT
angegeben worden sind, in die Tabelle Crystaldaten. Dabei wird ID1 In
crw_datestring1, ID2 in crw_datstring2, usw. geschrieben. Es gibt bis zu vier
IDENT-Felder. Der Name der Funktion lautet:
Anwrpt_al_vorlauf
Sie hat einen String-Parameter, über den die Daten
identifiziert werden können. Dieser kann beliebig vergeben werden. Man trägt
also z.B. folgendes in das Feld Vorlauf-Funktion ein:
Dabei ist hier TourSpeditionen der Parameter. In der
View selber muss man dann die Tabelle Crystaldaten mit den anderen Tabellen
joinen:
Create view p_TourSpedition as
select
…
From VorgStamm vs
join Crystaldaten cr
on vs.V_ID = cast(
cr.CRW_DatString
1 as int)
and
cr.loginid
=:LDB_LOGINID
and
crw_datanwendung
='TourSpeditionen')
Da Crystaldaten eine Tabelle ist, die von
v
[...]


---

## SQL Anywhere-Dienstprogramm für Dienste (dbsvc)

SQL Anywhere-Dienstprogramm für Dienste (dbsvc)
Syntax:
dbsvc [Optionen] -d
<Dienst>      Dienst löschen
dbsvc [Optionen] -g
<Dienst>      Details abrufen
dbsvc [Optionen]
-l
Alle SQL Anywhere-Dienste auflisten
dbsvc [Optionen] -u
<Dienst>      Dienst starten
dbsvc [Optionen] -x
<Dienst>      Dienst stoppen
dbsvc [Erst.-Optionen] -w <Dienst>
<Details> Dienst erstellen
@<data> erweitert <data> aus Umgebungsvariable
<data> oder Datei <data>
Optionen (Groß- und Kleinschreibung wie
angezeigt verwenden):
-cm
Diensterstellungsbefehl anzeigen (mit -g oder -l)
-o <Datei>
Ausgabenachrichten in Datei protokollieren
-q

Meldungen nicht anzeigen
-y
            Dienst ohne
Bestätigung löschen oder überschreiben
Erstellungsoptionen (Groß- und Kleinschreibung
wie angezeigt verwenden):
-a
<Konto>        Zu benutzender Kontoname
-as
       Konto "LocalSystem" verwenden
-i
         Interaktion
[...]


---

## SQL Remote-Nachrichtenagent Optionen

SQL Remote-Nachrichtenagent Optionen
(Version 12.0.1.3851)
Optionen (genau in der gezeigten Schreibweise
eingeben):
-a
Empfangene Transaktionen nicht anwenden
-b
Stapelverarbeitung
-c "Schlüsselwort=Wert; ..."
Datenbank-Verbindungsparameter angeben
-dl
Lognachrichten auf dem Bildschirm anzeigen
-ek
<Schlüssel>
Datenbank-Chiffrierschlüssel angeben
-ep
Eingabeaufforderung für Chiffrierschlüssel der
Datenbank
-g
<n>
Gruppentransaktionen weniger als <n> Vorgänge (Standard 20)
-l
<Länge>
Maximale Nachrichtenlänge (Minimum 10000, Standard 50000)
-m
<Größe>
Speicher für Nachrichten- und Datei-IO-Caching (Standard 2048 kB)
-ml
<Verz>
Verzeichnis für umbenannte Logspiegel
-o
<Datei>
Ausgabenachrichten in Datei protokollieren
-os
<Größe>
[...]


---

## Standardvorbelegung in der Auswahlliste definieren (nur Auswahlliste 2.0)

Standardvorbelegung in der
Auswahlliste definieren (nur Auswahlliste 2.0)
Diese Funktion steht nur in der neuen Auswahlliste und
dort zurzeit nur für das auf der Auswahlliste basierende Archiv zur Verfügung.
Hierbei handelt es sich um die Möglichkeit selber Vorbelegungen für den
„Neu“-Fall festzulegen. Es existiert zwar die Möglichkeit diese
DEFAULT
-Werte im SQL-Text zu hinterlegen, sollte jedoch nicht von
Anwendern verwendet werden, da dann private Ableitungen der Variante gebildet
werden müssten, die dann leider von Weiterentwicklungen ausgeschlossen sind.

---

## Stapelauswahl

Stapelauswahl
Beim Betreten einer Anwendung ist erst einmal kein
Stapel aktiv. Man kann einen Stapel anlegen, indem man Zeilen einem Stapel
hinzufügt – dann wird entweder automatisch ein Stapel gebildet oder es öffnet
sich eine Auswahl, wenn mehrere vorhanden sind – oder über die Stapelauswahl.
Das Menü „Stapelauswahl“ steht nur zur Verfügung, wenn mit globalem Stapel
gearbeitet wird, bei temporären Stapeln wird immer automaisch ein privater
Stapel angelegt.
In diesem Menü befindet sich mindestens die Funktion
„
(Neu)
“ und später dann die
angelegten Stapel. Wähl man
Neu
oder
einen angelegten Stapel aus, so öffnet sich dieser Dialog:
Bedeutung
aktivieren (
F9
)
Die
      Änderungen werden gespeichert, der Stapel wird zum aktiven Stapel und er
      wird links im Menüband angezeigt (statt „Kein Stapel ausgewählt“). Die
      Funktionen „
zu Stapel
      hinzufügen
“
Strg+F8
und
      „
aus Stapel entfernen
“
Strg+F7
beziehen sich dann auf diesen
      Stapel.
löschen (
F7
[...]


---

## Statistische Merkmale

Statistische Merkmale
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Funktion
Statistische Merkmale
SF5
Direktsprung
[ZHB]
Sind die Zahlungen erstellt, müssen mit der Funktion
Statistische Merkmale
SF5 weitere Informationen für den
Auslandszahlungsverkehr hinterlegt werden.
Beschreibung
Ausführungstermin
Er
      darf nicht kleiner als das Erstelldatum des DTA's sein und höchstens 15
      Kalendertage nach dem Erstelldatum liegen. Der Ausführtermin wird bei der
      Freigabe der Zahlungsvorschläge mit dem kleinsten Fälligkeitstag
      vorbelegt. Ist dieses Datum kleiner als das Tagesdatum, so wird es mit
      diesem vorbelegt. Bei der Freigabe der Zahlungsvorschläge kann man
      festlegen, dass immer das Tagesdatum als Ausführtermin verwendet werden
      soll. Dazu trägt man bei „Bei Auslandszahlungen Ausführdatum immer auf
      Tagesdatum setzen“ ein
Ja
ein.
Verwendungszweck
frei
      zu vergebender Text. Dieser wird mit den Belegnummern – bei
[...]


---

## Status einer E-Mail

Status einer E-Mail
Das Mailing-Kennzeichen hat folgende Ausprägungen:
Wert
Bezeichnung
Bedeutung
0
Wartet auf Freigabe
Der
      Beleg befindet sich in der Warteschleife und soll versendet werden. Die
      E-Mail kann jetzt manuell Freigegeben/Versendet werden. Die
Standard-Eventmail
      Funktion
versendet diese E-Mails ebenfalls, sobald das Event
      startet.
1
Freigegeben
Der
      Beleg ist zum Versand freigegeben. Diesen Status haben E-Mails die manuell
      versendet werden sollen oder von einem
Dienst oder Exe
verschickt werden.
2
Versendet
Der
      Beleg wurde erfolgreich versendet.
10
Zurückgestellt
Dieser Beleg wurde zurückgestellt.
      Die E-Mail wird erst nach erneuter Freigabe versendet.
95
Unzustellbar
Der
      Beleg kann nicht zugestellt werden.
99
fehlerhaft
Der
      Beleg konnte auf Grund eines Problems nicht versendet werden.
Im Fall einer fehlerhaften E-Mail kann der Fehlercode
Aufschluss über die Ursache geben. Zusätzlich finden sich Einträge i
[...]


---

## Stapelverarbeitung

Stapelverarbeitung
Unter Stapelverarbeitung versteht man die
Funktionalität der Auswahlliste, verschieden Datensätze in einer Anwendung
aufzusammeln, um später nur diese ausgewählten Datensätze zu bearbeiten.
Die
Stapelverarbeitung unterscheidet zwischen Vorgangsstapeln und allgemeinen
Stapeln.
•
Um Vorgangsstapel handelt es sich immer dann, wenn in der IDENT-Liste das
Feld V_ID vorhanden ist. Eine V_ID kann nur einmal in einem Stapel existieren.
Vorgänge, die so zu einem Stapel hinzugefügt wurden, können nur bearbeitet
werden, wenn diese Stapel aktiviert ist.
•
Der allgemeine Stapel bezieht sich immer auf alle Varianten mit derselben
IDENT-Kombination. Dies bedeutet zum Beispiel, dass man sich aus allen
Varianten, die für Kunden und Lieferanten existieren und als IDENT die Kundid
haben, Datensätze zum selben Stapel hinzufügen kann. Dieser Stapel sammelt die
Datensätze nicht exklusiv auf, d.h. ein Datensatz kann in unterschiedlichen
Stapeln existieren.

---

## Start des Tools

Start des Tools
Entweder bindet man eine private Funktion ein mit dem
ControlString:
&VorgResKorr
oder man startet dieses Tool unter OSQL ebenfalls mit dem
oben genannten Befehl!

---

## Status Lieferbelege

Status Lieferbelege
Auf diesem Feld steht eine F3 Auswahl zum Format
af_Status
zur Verfügung. Dieses Format
kann von jeder Firma unterschiedlich gepflegt werden.

---

## Statuszeile

Statuszeile
In der Statuszeile werden folgende Informationen
angezeigt:
1)
Wie viele Datensätze wurden gelesen. In den Beispielen sind es 107764, 15 bzw
265.
2)
Wie viele Datensätze wurden markiert. In den Beispielen unten gelten ALLE
Datensätze als markiert.
3)
Wurde das Laden der Daten abgebrochen? Es wird ein rotes Kreuz und zusätzlich,
wenn man mit der Maus über die Anzeige geht, der Tipp-Text „Das Laden der Daten
wurde vom Benutzer abgebrochen.“ angezeigt.
4)
Wie lange hat das Laden der Daten gedauert. Die Anzeige zeigt Stunden – Minuten
– Sekunden und tausendstel Sekunden an. Im Beispiel ganz unten hat es 0,1700
Sekunden gedauert die Daten zu laden. Zwischen dem Laden der Daten und der
Anzeige kann je nach Aufbau der Auswahlliste und der Datenmenge auch noch etwas
Zeit vergehen, die hier nicht berücksichtigt wird.
5)
Wenn der Steuerparameter „Auswahllisten-Refesh“ für die Anwendung aktiv ist, so
erscheint nach dem ersten Refresh eine kleine Timer-Grafik,
[...]


---

## Steuerschlüssel

Steuerschlüssel
Nach dem Einlesen wird der Steuerschlüssel zunächst
über eine Umsetztabelle in einen Aeins-Steuerschlüssel konvertiert. Kann der
Steuerschlüssel nicht gelesen werden, so zieht der in STC_DEFAULT hinterlegte
Steuerschlüssel, der mit 0 belegt ist, falls nicht anders angegeben.
Eine Validierung findet nicht statt.
(Konvertierungsparameter: STEUERx, Positionsparameter:
SCT_SAx, weitere Parameter STC_DEFAULT).

---

## Stornieren

Stornieren

---

## Stornieren gebuchter Belege

Stornieren gebuchter Belege
Ist ein Beleg, der Fehlerhaft ist, bereits gebucht, so
kann er nicht mehr gelöscht werden.  Er muss dann storniert werden. Es gibt
verschieden Stellen im Programm, an denen für einen Beleg automatisch ein
Stornobeleg erstellt werden kann.
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Standardvorgänge Fibu
Variante „gebuchte
Belege“
Direktsprung
[FISV]
und überall dort, wo die
Einzelbeleganzeige
aufgerufen werden kann.
Dort lässt sich für den Stornobeleg unter dem
Einrichterparameter
„Darf ein Stornobeleg geändert
werden?“ einstellen, ob er im Nachhinein geändert bzw. gelöscht werden darf. Die
stornierten Belege werden als storniert gekennzeichnet, damit sie nicht
versehentlich ein zweites Mal storniert werden.
Vor der automatischen Erstellung der Stornobelege
werden vom Programm einige Tests durchgeführt.
1.
Es können nur bestimmte Belegarten storniert werden. Technische Belegarten, die
durch die Auszifferung entstehen (z.B. Interne Umbuchunge
[...]


---

## Stornoprotokoll

Stornoprotokoll
Hauptmenü
Stornoprotokoll
oder Direktsprung
[STOPO]
Im Stornoprotokoll kann man nachsehen, wer wann
welchen Beleg storniert hat.

---

## Subskriptionen verwalten

Subskriptionen verwalten
Sie können über Sybase Central Subskriptionen
verwalten.
1.
Starten Sie Sybase Central unter: ..\Aeins\bin64\scjview.exe
2.
Verbinden Sie sich mit der gewünschten Datenbank
3.
Klicken Sie nun auf der Registerkarte „Inhalt“ oder in der Ordnerübersicht auf
SQL Remote-Subskriptionen
Eine neue Subskription anlegen:
1.
Wählen Sie in der Ordnerliste SQL Remote-Subskriptionen
2.
Klicken Sie auf einer freien Stelle der Registerkarte „SQL
Remote-Subskriptionen“ mit der RECHTEN Maustaste und wählen Neu
à
SQL Remote-Subskriptionen
3.
Folgen Sie den Anweisungen des Assistenten zum Erstellen von SQL
Remote-Subskriptionen
Eine Subskription bearbeiten:
1.
Wählen Sie in der Ordnerliste SQL Remote-Subskriptionen
2.
Zum Bearbeiten wählen Sie die gewünschte Subskription auf der Registerkarte SQL
Remote-Subskriptionen aus und klicken diesen mit der RECHTEN Maustaste an
3.
Sie können über die Registerkarte „Erweitert“ diese Subskription starten,
sto
[...]


---

## Summe über die Summierungsmaske

Summe über die Summierungsmaske
Hier können die Einstellungen für die Summierungen
vorgenommen werden, um keine privaten Ableitungen erstellen zu müssen. Die Maske
kann entweder über die Funktion „Spaltensummierungen“ im Menü der Auswahlliste
oder durch einen Klick auf die Spalten „Summenfeld“ und „Summenwert“ aufgerufen
werden. Die Summierungsmaske kann für bestimmte Benutzergruppe weggeschützt bzw.
freigegeben werden, indem man der Funktion „Spaltensummierungen“ im Menü der
Auswahlliste bestimmte Benutzergruppen zuordnet. Wenn im Bedienerstamm der
Schalter „Auswahllistenadministrator“ auf „Temporär“ steht, kann man für die
aktive Referenz-ERP-Sitzung die Einstellungen vornehmen, die jedoch nicht gespeichert
werden.
Bedeutung
Spaltenname
Die
      Überschrift der Spalten, zu der die Summe gebildet werden
      soll.
Summierung
Soll
      diese Spalte summiert werden?
Formel
Wenn
      die Summe der Spalte mit einer anderen Formel berechnet werden soll, so
      kann diese hier
[...]


---

## Summierung in der Auswahlliste

Summierung in der Auswahlliste
Es ist möglich, über ausgewählte Spalten eine Summe zu
bilden und diese zusätzlich zum TIPTEXT auszugeben.

---

## SVPOSI

SVPOSI
Die AIS-Aktualisierung findet nur dann statt, wenn
eine Position ausgewählt oder ein Positionswechsel vollzogen wird. Das AIS wird
beim Zurückkommen von einer darüberlegenden Maske noch einmal aktualisiert.
Alle AIS-Aktualisierungspunkte auf der SVPOSI Maske
können per Makro gesteuert werden. Es gibt keine Punkte, die im Standard das
ganze AIS auf der Maske aktualisiert wird.
Bei folgenden Ereignissen wird das AIS
aktualisiert.
1.
Navigieren nach oben
2.
Navigieren nach unten
3.
Sprung zum Positionsanfang
4.
Sprung zum Positionsende
5.
Anwählen einer Positionszeile mit der Maus
6.
Rückkehr von einer darüber liegenden Maske auf die SVPOSI Maske
Benötigte JVARS
JAVR
Funktion
Bedeutung
VORGANGHANDLE
Lesend
Mit
      dieser JVAR wird der Vorgangshandel des aktiven Vorgangs
      übergeben.
POSITIONHANDLE
Lesend
Mit
      dieser JVAR wird das aktuelle Positionshandle übergeben. Über den
      Positionshandle kann der Typ der Positionszeile bestimmt werden.

[...]


---

## Tabelle benutzt in

Tabelle benutzt in
Hier werden die Formulare angezeigt, die die aktuell
in der Maske geöffnete Fonttabelle verwenden. Das ist hilfreich, falls man
vorhat eine Fonttabelle für ein bestimmtes Formular zu ändern. So weiß man
gleich welche Formulare von der Änderung noch betroffen sind.

---

## Tabellen AeinsZusatz 1 – 40 löschen

Tabellen AeinsZusatz 1 – 40 löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
AeinsZusatz1
AeinsZusatz2
AeinsZusatz3
AeinsZusatz4
AeinsZusatz5
AeinsZusatz6
AeinsZusatz7
AeinsZusatz8
AeinsZusatz9
AeinsZusatz10
AeinsZusatz11
AeinsZusatz12
AeinsZusatz13
AeinsZusatz14
AeinsZusatz15
AeinsZusatz16
AeinsZusatz17
AeinsZusatz18
AeinsZusatz19
AeinsZusatz20
AeinsZusatz21
AeinsZusatz22
AeinsZusatz23
AeinsZusatz24
AeinsZusatz25
AeinsZusatz26
AeinsZusatz27
AeinsZusatz28
AeinsZusatz29
AeinsZusatz30
AeinsZusatz30
AeinsZusatz31
AeinsZusatz32
AeinsZusatz33
AeinsZusatz34
AeinsZusatz35
AeinsZusatz36
AeinsZusatz37
AeinsZusatz38
AeinsZusatz39
AeinsZusatz40

---

## Tabellen deren Inhalt nicht mit dem Nullsetzer gelöscht werden kann

Tabellen deren Inhalt nicht mit dem Nullsetzer gelöscht werden kann
Es gibt Tabellen die nicht mit dem Nullsetzer gelöscht
werden können, da zu viele Abhängigkeiten bestehen, so dass eine Zuordnung zu
einem Unterpunkt nicht möglich ist.
Diese Tabellen sollten dann manuell gelöscht werden,
wenn der Inhalt nicht mehr benötigt wird.
Darunter fallen z.B. folgende Tabellen:
PREISKLASSE

---

## Tabelle zur Version: 8.3.2212.23

Tabelle zur Version: 8.3.2212.23
ID
Releasenote - Titel
Geprüft
33155
Windows11-Anpassung: Asynchrones Anzeigen von
      Informationen
33156
Auswahlliste 2.0 im Dialogmodus
33157
Belegfluss erstellen Finanzbeleg
33255
CO2-Kostenaufteilung
33257
Referenz-ERP Temporäre Dateien
33235
Office 365 Online-Exchange-Authentifizierung
33280
Geodaten Lizenz
33209
DATEV Übertrag erstellen. Verbesserte
    Fehlermeldung.
33219
Neue Elster-Version
33181
Artikelpfleger: Inventurgruppe
33223
Kundenpfleger: Speichernabfrage
33283
Preiskalkulation Excel auf Artikelebene nicht mehr
      möglich.
33292
Artikelstamm: SQL-Fehler
32857
Reaktivierung von Quellbelegen bei Erstellung des
      Stornobelegs
33004
Stoffstromanteil pflegen
33282
Stoffstrom Kundenreport
33324
Teildisposition v_statusWeiter

---

## Tabelle zur Version: 8.3.2304.28

Tabelle zur Version: 8.3.2304.28
ID
Releasenote - Titel
Geprüft
33652
Auswahlliste Menüband
33658
Dashboard: Erweiterung
33659
Dashboard: Erweiterung
33660
Dashboard: Erweiterung
33662
Dashboard: Erweiterung
33663
Replikation: Create von einzelnen Views
33689
Auswahlliste 2.0
33694
Vermehrungsvertrag
33719
Mailversand: Dateizuordnung von Mail-Anhängen
33465
Dokumentenverwaltung: Gelegentliche
      Komplikationen  im Archiv-Betrieb
33590
Archiv: Drag&Drop von Zustellungs- bzw.
      Fehlerberichten
33593
Archivanzeige: Einzelbeleganzeige
33636
ASCII-Druck deutsche Sonderzeichen
33655
e.Clearing Format CAMT.053
33692
Permanente Inventur und Belege am Erfassungstag
33525
Rohware Manuelle Werte
33697
Auftragskorrektur: Brutto-Belege

---

## Tabelle zur Version: 8.3.2306.23

Tabelle zur Version: 8.3.2306.23
ID
Releasenote - Titel
Geprüft
33899
Vorgang senden an

---

## Tabelle zur Version: 8.3.2307.7

Tabelle zur Version: 8.3.2307.7
ID
Releasenote - Titel
Geprüft
33960
Branchen-ERP-Etikettendruck Profile

---

## Tabelle zur Version: 9.0.2501.5

Tabelle zur Version: 9.0.2501.5
ID
Releasenote - Titel
Geprüft
36368
Abkündigung: Infocenter
35868
Datenbank-Backup: AMIC_EVT_Backup_ARCHIV
35948
Auswahlliste 2.0 JPP-Zugriff
35965
Branchen-ERP Etikettendruck export Archivkennzeichen
35966
Geschäftsjahr Prüfung Enddatum
35973
Reporte
35977
Standard F3-Auswahl und Auswahlliste
36231
Crystal: Druck über Makro
36522
IBMSK nicht existierendes Feld
36573
Referenz-ERP Passwortrichtlinien
36957
HTML-Dateien im Belegfluss im Browser anzeigen
36959
Belegfluss gelöschte Formulararchiveinträge
      wiederherstellen
37055
Pfleger individuelle Artikelnummern aus der
      Belegflussmaske öffnen
37061
Belegfluss: Daten aktualisieren als neue
      Refresh-Funktion über eine Prozedur
37062
Fibudirektverbuchungprozedur für Belegfluss um eine
      Parameter erweitert
37065
Belegfluss: Postfach-Einrichtung teilt Einrichtung in
      Kopf und Kostenverteilungsgrid.
37068
Belegflussmaske Kostenaufteilungsgrid
    zurücksetzen
37091
Nummernkreis optional auf der
[...]


---

## Technische Informationen

Technische Informationen

---

## Tabulatorreihenfolge löschen

Tabulatorreihenfolge löschen
Löscht die selbsterstellte Tabulatorreihenfolge auf
der Maske

---

## Tabulatorreihenfolge

Tabulatorreihenfolge
Funktionen bei der Tabulatorreihenfolge.
Wenn man auf ein Eingabefeld klickt, so öffnet sich
eine Maske mit folgenden Feldern. In „
Aktives Feld
“ wird das Feld
angezeigt, dass man gerade ausgewählt hat. Klick man dann auf eine der
Funktionen „
Next Tabstop, PrevTabstop, Alter Next Tabstop, Alter Prev
Tabstop
“, so schließt sich diese Maske und man kann dann in das Feld
klicken, dass dann das nächste, vorherige,… in der Tabulatorreihenfolge werden
soll.
Funktion
Bedeutung
Next
      Tabstop
Prev
      Tabstop
Alter Next Tabstop
Alter Prev Tabstop
Aktives Feld
Anzeige des aktuellen
      Feldnamens
Feldeinstellungen
      löschen
Setzt die Feldeinstellungen
      zurück
Eingabezwang
Kann
      Ja und Nein annehmen,
Tastaturfilter
Die
      Werte des Feldes werde durch das Anklicken der Zeile gesetzt. Diese Werte
      werden unterstützt.
•
Unfiltered
•
Digits
      only
•
Yes-no
•
Alphabetic
•
Numeric
•
Alphanumeric
•
Regular
      Expression
•
Edit
[...]


---

## Technischer Ablauf

Technischer Ablauf
Schematische Darstellung anhand des Vorgangs „neuer
Vorgang“

---

## Technischer Hintergrund

Technischer Hintergrund

---

## Telefonie-Systeme

Telefonie-Systeme

---

## Testumgebung

Testumgebung
In jede Nacht wird die Referenz-ERP Software automatisch
getestet.

---

## Text 1 und Text 2

Text 1 und Text 2
Hier kann ein beliebiger Text eingegeben werden.

---

## Tipps und Tricks

Tipps und Tricks
Hier werden ein paar Tipps zu Lösung von Problemen aus
der täglichen Praxis aufgeführt.

---

## Tipps und Tricks

Tipps und Tricks
Hier werden ein paar Tipps zu Lösung von Problemen aus
der täglichen Praxis aufgeführt.
Mehrseitige Karteikarten
Es ist mit dem Werkzeug Branchen-ERP Etikettendruck möglich,
auch mehrseitige Karteikarten zu erstellen. Folgendes Beispiel erstellt einen
Report mit zwei unterschiedlichen Seiten. Dazu muss man zwei Dinge beachten:
1)
Im Editor vom Branchen-ERP Etikettendruck im Menü unter
Projekt
muss man den
Punkt „
Ebenen bearbeiten
“ aufrufen.
Bei der Bearbeitung von
Reporten mit mehreren Seiten muss man in der Spalte „
Sichtbar
“ immer nur
in der Zeile einen Haken setzen, die man bearbeiten will.
Im obigen Beispiel
sind zwei unterschiedliche Seiten definiert und in der Spalte Bedingung wird
angegeben, wann welche Ebene zu sehen sein soll.
Die hier abgebildeten
Formel „Page()/2<>floor(page()/2“ liefert bei allen ungeraden Seiten true
zurück und die Formel „Page()/2<>floor(page()/2“ bei allen geraden Seiten.
2)
Die Datenbereitstellung muss jetzt entsprechend angepasst we
[...]


---

## Tron Tracer – Programm zum Auslesen der Trace-Datei

Tron Tracer – Programm zum Auslesen der Trace-Datei
Der Tron-Tracer ist ein externes Programm, welches es
erlaubt eine Trace Datei einzulesen und in einer Tabelle anzeigen zu lassen.

---

## Umsatzsteuer

Umsatzsteuer

---

## Umschalten Stapelverarbeitung

Umschalten
Stapelverarbeitung
Die Stapelverarbeitung hat im Prinzip zwei Modi,
zwischen denen einfach mit der Funktion „Umschalten Stapelverarbeitung“ hin und
her gewechselt werden kann:
1)
Hinzufügen zu einem Stapel:
2)
Bearbeiten eines Stapels:
Beim Umschalten in den Bearbeitungsmodus werden nur
die aufgesammelten Datensätze angezeigt. Um möglichst alle ausgewählten
Datensätze anzuzeigen, werden alle Häckchen in der F2-Bereichsauswahl
automatisch deaktiviert. Um die letzte Eingrenzung wieder zu aktivieren muss
lediglich die Bereichseingrenzung einmal aufgerufen werden. Diese wird dann mit
den vorherigen Werten angezeigt.
Im Bearbeitungsmodus kann die Variante nicht
gewechselt werden.
Den Bearbeitungsmodus verläßt man wieder, indem man
erneut „Umschalten Stapelverarbeitung“ auswählt oder indem man Escape
drückt.

---

## Umstellungslevel erreichen.

Umstellungslevel erreichen.

---

## Umstellung starten.

Umstellung starten.

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
      BelegKs, Za
[...]


---

## Variante Replikation

Variante Replikation
Hier werden die gleichen Informationen geboten wie in
Variante
Systemhinweise
.
Die Daten sind aber eingeschränkt auf die Belange des
Replikationsumfeldes. Die Ermittlung dieser zugrundeliegenden Daten erfolgt über
die View amic_v_fehlerprotokoll_recherche.

---

## Variante Protokollwesen

Variante Protokollwesen
Felder
Nr
Die
      laufende Protokollnummer.
Titel
Themenbereich z.B. „Formulararchiv
      Dokumentenimport“
Anwendung
Zugeordnete Anwendung z.B.
      „Formulararchiv“
Fehler
Anzahl der Fehlerhinweise im
      Protokoll.
Warnungen
Anzahl der Warnungen im
      Protokoll.
Vom
Zeitpunkt des
      Protokoll-Eintrages.
Wer
Bediener der den Protokoll-Eintrag
      verursacht hat.
gelesen am
Zeitpunkt der Kenntnisnahme des
      Protokolls.
gelesen von
Der
      Kurzname des Referenz-ERP-Bedieners der das Protokoll angeschaut, aber nicht
      gelöscht hat.
Funktionen
F2
Löschen
Pfleger zum Löschen von
      Protokoll-Einträgen.
Wird
      der Eintrag nicht gelöscht dann wird Leser und Zeitpunkt in „gelesen wer“
      und „gelesen von“ vermerkt.
Bereich/Profile
Nr
Protokollnummer
Titel
Anwendung
Fehler
Warnungen
Vom
Wer
Gelesen am
Gelesen von
Masken-Felder
Dialog „Fehlerprotokoll“
      Registerkarte „Fehlerprotokoll“
Löschen
Löscht den
      Protokolleint
[...]


---

## Programmupdates und Releaseänderungen Versionen 64bit

Programmupdates und Releaseänderungen Versionen 64bit
Eine Zusammenfassung der in den Releaseupgrades
enthaltenen Änderungen wird in diesem Bereich zusammengefasst.

---

## Programmupdates und Releaseänderungen Versionen 32bit

Programmupdates und Releaseänderungen Versionen 32bit
Eine Zusammenfassung der in den Releaseupgrades
enthaltenen Änderungen wird in diesem Bereich zusammengefasst.

---

## Verwaltung von OLAP-Anzeigen

Verwaltung von OLAP-Anzeigen
Auf den gleichen Daten lassen sich unterschiedliche
Ansichten erstellen. Diese werden im weiteren Verlauf Titel genannt.
Erstellen / Speichern
Im Menu „Datei“ finden Sie die Funktion „Neue
Auswertung“. Diese Funktion setzt alle Einstellungen zurück. Erstellen Sie nun
Ihre Auswertung.
Betätigen Sie zum Speichern die Funktion „Speichern“
im Menu „Datei“. Da Sie dieser Auswertung noch keinen Titel gegeben haben,
werden Sie nun um die Angabe eines Titels gefragt.
Weitere Änderungen können Sie fortan ohne Angabe des
Titels mit der Speichern-Funktion sichern.
Wollen Sie eine bestehende Auswertung unter einem
neuen Titel speichern, so verwenden Sie die Funktion „Speichern unter“. Sie
werden nun nach einem neuen Titel für diese Auswertung gefragt. Die Weiteren
Änderungen können nun mit der Speichern-Funktion unter diesem Namen gesichert
werden.
Verwenden bestehender Titel
Im Menu Titel finden Sie eine Auflistung aller bisher
gespeicherten Titel. Wählen S
[...]


---

## View AMIC_V_Warenbewegung_Info

View AMIC_V_Warenbewegung_Info
Zuweilen wollen Sie sicher zusätzliche Informationen
zu den Warenbewegungen bekommen. Diese bietet Ihnen die View Warenbewegung_Info.
Diese View kann mit dem Feld wabew_id an die Tabelle
Warenbewegung oder andere Views gejoint werden, die die wabew_id enthalten.
AMIC_V_Warenbewegung_Info
Gibt zusätzliche Informationen zu
      Warenbewegungen
Feld
Typ
Bezeichnung
wabew_id
Integer
ID
      der Warenbewegung
tmp_ist
Integer
temporäre
      Zwischenergebnise
tmp_fremd
Numeric(15,4)
temporäre
      Zwischenergebnise
tmp_ktrdiff
Numeric(15,4)
temporäre
      Zwischenergebnise
tmp_wert
Numeric(15,4)
temporäre
      Zwischenergebnise
wbc_Typ_EKVK
smallint
Einkauf/Verkaufskennzeichen (EK=1,
      VK=2)
wbc_SigniEigenware
Numeric(15,4)
Vorzeichen Eigenware
wbc_SigniEigenwareKtrDiff
Numeric(15,4)
Vorzeichen Eigenware
      Kontraktdifferenz
wbc_SigniFremdware_VVK
Numeric(15,4)
Vorzeichen Fremdware
      Vorverkauf
wbc_SigniFremdlager_VEK
Numeric(15,4)
Vo
[...]


---

## View Amic_V_Word2Rtf

View Amic_V_Word2Rtf
Die View dient als Grundlage der Datengewinnung und
wird bei weiteren Tabellen entsprechend über "Union" erweitert.
CREATE VIEW amic_v_word2rtf
AS
SELECT
'Anschriftnotizen'  AS tabelle,
'winword'           AS
winwordspalte,
'textblob'          AS
rtfspalte,
'adressid'          AS
pkspalte,
adressid            AS
pkwert,
len(winword)        AS
winworddatalen,
len(textblob)       AS rtfdatalen,
'cast(winword as long binary)' AS
feld_schnipsel,
'where adressid=' || adressid  AS
where_schnipsel,
ifnull(textblob,0,1)
AS konvert_status
FROM
anschriftnotizen;

---

## Vorbelegung im Gestaltungsdialog

Vorbelegung im
Gestaltungsdialog
Für Archivanwendungen steht die Funktion „Vorbelegung“
zur Verfügung. Wählt man diese an, so öffnet sich der Gestaltungsdialog und man
steht sofort auf dem Reiter „Vorbelegung“:
Dort werden die selbst definierten Vorbelegungen
angezeigt. Diese Vorbelegungen überschreiben ggf. die von Branchen-ERP vorgegebenen
Werte. Um eine Vorbelegung zu ändern, klickt man in die Zeile, um eine neue
Vorbelegung anzulegen, klickt man auf „
(Neu)
“. In dem sich dort öffnenden Dialog
kann man folgende Werte eingeben:
Bedeutung
Feld
Name
      des Feldes, welches vorbelegt werden kann. Eine Auswahl ist mit
F3
möglich.
Aktiv
Wenn
      ein Feld momentan nicht verwendet werden soll, aber die Arbeit, die in die
      Formulierung gesteckt wurde, nicht über den Haufen geworfen werden soll,
      so kann man hier die Vorbelegung für das Feld einfach deaktivieren. Sie
      wird dann komplett ignoriert.
Vorbelegung
Hier
      steht der Wert, der auf der Erfassungsmaske bei
[...]


---

## Voraussetzungen Outlook

Voraussetzungen Outlook
Um dieses Modul nutzen zu können, ist ein Outlook 2000
System oder höher notwendig, Mindestvoraussetzung an den Arbeitsplatzrechner ist
Windows 2000/2003 oder Windows XP. Das Windows Scripting Host System muss
installiert sein (Standard in Windows 2000/2003 und XP).
Um die Rückübermittlung von Daten (z.B.
Besuchsberichte) nutzen zu können, sollte auch ein Exchange Server in Betrieb
sein, es ist aber auch möglich über externe e-Mail Dienstanbieter wie z.B. gmx
oder hotmail eine Datenrückübermittlung zu gewährleisten. In jedem Falle ist ein
Internetanschluss notwendig.

---

## Vorbelegung im SQL-Text

Vorbelegung im SQL-Text
Um die Vorbelegung zu definieren verwendet man das
Schlüsselwort DEFAULT. Hinter diesem Schlüsselwort folgt dann der Feldname den
man vorbelegen will und durch ein Gleichheitszeichen „=“ getrennt der Wert. Bei
diesem Wert kann es sich auch um einen Select-Befehl handeln.
DEFAULT fa_info_autor=“select bedienername from
bedienerstamm where bedienerid=db_bedienerid“, fa_belegklasse=1400
Mehr Informationen dazu unter „
Default im Gestaltungsdialog
“

---

## Vorgang DROP

Vorgang DROP
Der Vorgang wird ‚hart’ entfernt . Nach einem Vorgangdrop
ist ein anschließendes WAREO unerlässlich, da Bestände und andere
Summenrelationen durch das Entfernen nicht korrigiert werden.

---

## Vorgangsbearbeitung

Vorgangsbearbeitung
Zur Bearbeitung von Vorgängen stehen zahlreiche
Funktionen innerhalb der Auswahllisten der einzelnen Vorgangsklassen zur
Verfügung.

---

## Vorgang senden

Vorgang senden
Übergibt einen ausgewählten Beleg zum Senden als
E-Mail an Outlook. Diese Referenz-ERP Funktion muss im Einzelfall speziell eingebunden
werden.

---

## Vorgangsklassen in Referenz-ERP

Vorgangsklassen in Referenz-ERP
Die Erfassung der verschiedenen Vorgangsarten ist
hinsichtlich des Funktionsumfangs im Prinzip identisch. Im konkreten Unternehmen
ergeben sich hinsichtlich der Erfassungsabläufe, Informationsinhalte, etc.
natürlich erhebliche Unterschiede. Ein ausgeklügeltes Parametersystem sorgt
dafür, den Erfassungsaufwand je Vorgangklasse für den Betrieb zu optimieren.
Hiermit wird u.a. folgendes festgelegt:
die Befugnis der Anwender: über Bedienerklassen und
Bediener
die Gestaltung von Formularen: über den
Formulareinrichter und die Formularzuordnung
die erfassten Positionen: über Bedienerfelder,
Erfassungsparameter und Steuerungsparameter
die Reihenfolge der Erfassung: über Bedienerfelder und
die Formularzuordnung
interne Logiken: über Steuerungsparameter und
Verschlüsselungen im Kunden- und Artikelstamm
die Gestaltung der Erfassung am Bildschirm: über den
Formulareinrichter
Belegdurchlauf im Verkauf und Einkauf: über
Arbeitsregeln und Variantensteuerung
Für j
[...]


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

## Vorgang Speichern mit Druck auf Unterklasse 1 und 2

Vorgang Speichern mit Druck auf Unterklasse 1 und 2
Unter der EPA Einstellung dieser Maske können zwei
Unterklassen festgelegt werden, unter denen die Belege abgespeichert werden.
Diese Unterklassen sind dann den beiden Köpfen D1 und D2 zugeordnet, nach
betätigen einer dieser Knöpfe wird der Beleg gespeichert, und unter der
angegebene Unterklasse (also auch auf dem entsprechenden Formular) gedruckt.
Hiermit kann erreicht werden, dass wahlweise eine Ladeliste oder ein kompletter
Lieferschein ausgegeben wird. Im Rechnungsfall könnte hier auch die Rechnung
gedruckt oder ein Bondrucker angesteuert werden.

---

## Vorgang Speichern und sofort zur Korrektur aufrufen

Vorgang Speichern und sofort zur Korrektur aufrufen
Der Knopf K speichert den Vorgang und öffnet ihn
sofort mit den normalen Methoden zur Vorgangskorrektur, um ggf. Ergänzungen und
Zusätze im Vorgang einzutragen, die mit der Schnellerfassung nicht angegeben
werden können.

---

## Vorgang ZEIGEN

Vorgang  ZEIGEN
Der Beleg wird im Vorschaumodus angezeigt. Dies geht aus
technischen Gründen derzeit nur dann, wenn dazu auch eine Vorgreservierung
vorhanden ist (wird später noch geändert)!

---

## Vorgänge allgemein

Vorgänge allgemein
Vorgang
teildisponieren
Vorgänge können Positionen aus anderen Vorgängen
teildisponieren. Dazu wird im Feld interneReferenz der Position die WabewGuid
der Vorgängerposition eingetragen. Aus dieser Position wird dann in diese neue
teildisponiert.
Vorgang
ändern
Vorgänge können auf zweierlei Weisen geändert werden:
1.
Changing
Hier werden nur die im
Import gegebenen Komponenten geändert.
Nicht vorhandene Positionen
werden hinzugefügt.
Nicht gegebene Positionen
werden unverändert bleiben.
Zu diesem Zweck wird der
ImportTyp im Vorgangstamm auf 10 gesetzt.
2.
Explizit –
Jede Komponente muss gegeben
werden. Jede nicht gegebene Komponente wird entfernt.
Nicht vorhandene Positionen
werden hinzugefügt.
Zu diesem Zweck wird der
ImportTyp im Vorgangstamm auf 11 gesetzt.
Als Referenz für die im Beleg zu ändernder Position
gilt die WabewGuid des aktuellen Beleges.
Daten
Manipulation vorm Erzeugen eines Vorgangs:
Es besteht die Möglichkeit mittels einer private
[...]


---

## Ware für Eigenverbrauch

Ware für Eigenverbrauch

---

## Vorschau

Vorschau
Zeigt einen ausgewählten Beleg im Vorschaumodus an.

---

## Warenbuch

Warenbuch
Hauptmenü
Informationen
Warenbuch
Warenbuch Anzeige
Direktsprung
[WBA]
Das Warenbuch ist die zentrale Bezugs- und
Absatzstatistik. Es ist nach Lieferbezügen aufgebaut. Es stellt Warenbewegungen
für einen frei abgrenzbaren Lieferzeitraum gemäß der Lieferchronologie dar. Das
Warenbuch enthält alle Rechnungen und Gutschriften in Ein- und Verkauf sowie
Umbuchungen, Produktionsbuchungen und Inventuren. Lieferscheine sind enthalten,
solange sie nicht fakturiert sind.
Man beachte, dass eine zusätzliche Abgrenzung nach
Buchungsperioden möglich ist. Wenn Lieferbezüge und Buchungsperioden dahingehend
abweichen, dass das Lieferdatum nicht in ihm entsprechende Buchungsperiode fällt
(etwa Buchungsperiode war bereits abgeschlossen), können je nach Abgrenzung
unterschiedliche Aussagen entstehen.
Durch die integrierte Auswahl von Kunden kann das
Warenbuch auch etwa als Kundenstatistik verwendet werden.

---

## Wareo

Wareo
Die Reorganisation kann jetzt einfach per Event
gestartet werden.
Zunächst ist der
Eventname
auf dem Tabreiter
Allgemein
anzugeben. Wird kein Name angegeben, so wird bei der
Generierung des Events automatisch der Eventname
Wareo
zugewiesen. Ein
Zeitplan wird nur generiert, wenn der Eventname
Wareo
lautet, da
unterschiedlich Wareo-Events sich zeitlich nicht überschneiden sollten.
Grundsätzlich muss der Zeitplan auf dem Tabreiter
Bedingungen
an die
Gegebenheiten angepasst werden.
Auf dem Tabreiter
Vorlagen
können nun zunächst
die gewünschten Reorganisationsmaßnahmen ausgewählt werden. Wird keine Auswahl
der Wareo-Funktionen getroffen, so wird bei der Erzeugung der
Verarbeitungsroutine als auszuführende Wareo-Funktion die
Gesamte
Reorganisation (Standard)
eingesetzt. Die Erzeugung der Verarbeitungsroutine
wird mit Betätigung des Buttons
Wareo-Event erzeugen
ausgelöst und
generiert einen Prozeduraufruf, dessen Syntax auf dem Tabreiter
Verarbeitungsroutine
dargestellt wird
[...]


---

## Wechsel bearbeiten

Wechsel bearbeiten
Die Bearbeitung der Wechsel kann unter Zugrundelegung
folgender Geschäftsvorfälle erfolgen.

---

## Wechselbuchhaltung

Wechselbuchhaltung
Zielsetzung
Ein großer Teil aller Warengeschäfte wird durch
Wechsel finanziert. Der Wechsel ist ein Wertpapier, in dem sich der Schuldner
(Bezogener) verpflichtet, einen bestimmten Betrag an einem festgelegten Termin
(Verfalltag) an den auf dem Wechsel angegebenen Empfänger (Remittent) zu
bezahlen.

---

## Wechselgruppen

Wechselgruppen
Hauptmenü
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechselgruppen
Direktsprung
[
WEGR
]
Wechselgruppen dienen der Festlegung, ob es sich um
einen Besitz- oder Schuldwechsel handelt. Ferner kann man über die Wechselgruppe
die Wechselkosten zuordnen.
Beschreibung
Wechselgruppe
lfd.
      Nummer
Bezeichnung
ausführliche Bezeichnung
Wechselart
Auswahl mit
F3
zwischen
      Besitz- und Schuldwechsel
Wechselkl. Abr.
Auswahl mit F3 aus vorher
      eingerichteten
Wechselkosten
für die Abrechnung
Wechselkl. Einr.
Auswahl mit F3 aus vorher
      eingerichteten
Wechselkosten
für die Weitergabe

---

## Wechselkosten

Wechselkosten
Hauptmenü
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechselkosten
Direktsprung
[
WEKO
]
Beschreibung
Abr.
      Gruppe
Laufende Nummer
Bezeichnung
Ausführliche Bezeichnung
Sprache
Auswahl mit
F3
aus vorher
      eingerichteten Sprachen
Formularid
Auswahl mit
F3
aus vorher
      eingerichteten Wechselformularen
Zinsgruppe
Auswahl mit
F3
aus vorher
      eingerichteten Zinsgruppen
Pos
Laufende Nummer der
      Position.
Text
Text
      der Position
Vorbelegung
Betrag in Buchwährung oder
      Prozent
Bezug
Kann
Betr
sein, wenn es
      sich bei der Vorbelegung um einen festen Betrag handelt oder
PRZ
wenn unter Vorbelegung die
      Prozentzahl steht, mit der später gerechnet werden soll.
Konto
Auswahl mit
F3
aus dem
Sachkontenstamm
um den Betrag
      auf ein Sachkonto verbuchen zu können
Kostenstelle
Auswahl mit
F3
aus den
      Kostenstellen um den Betrag auf eine
Kostenstelle
verbuchen zu können
Kostenträger
Steht der SPA „Kostenträgerrechnung
      angeschlos
[...]


---

## Wechselprotest durch Nichteinlösen

Wechselprotest durch Nichteinlösen
Ist der Bezogene am Verfalltag nicht in der Lage, die
Wechselsumme zu bezahlen, dann wird der Wechselbesitzer
Protest mangels Zahlung
erheben. Der Besitzwechsel wird zum Protestwechsel. Jetzt kann der
Wechselbesitzer beliebig jeden früheren Vorbesitzer des Wechsels zur Zahlung der
Wechselsumme verpflichten. Handelt es sich um weitergereichte Wechsel, die sich
auf dem Obligokonto befinden, kann die entsprechende Bankbuchung (Rückbelastung
der Bank) auf zwei Arten durchgeführt werden. Nicht weitergereichte Wechsel
können nur über "Wechsel bearbeiten" zum Protestwechsel werden (siehe
Möglichkeit 2).
Möglichkeit 1:
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[
FIBE
]
Belegart Zahlungsverkehr Bank anwählen und Buchung
erfassen, wobei als Gegenkonto das Wechselobligokonto angegeben werden muss. Da
diese Konten als Wechselkonto gekennzeichnet sind, werden bei Eingabe des
Gegenkontos die weitergereichten Wechsel in einem Auswah
[...]


---

## Weitere Anwendungsmöglichkeit Kasse

Weitere Anwendungsmöglichkeit Kasse
Es gab den Wunsch, dass mehrere Kassenarbeitsplätze
auf denselben Drucker im Netz drucken sollen.
Um dieses zu realisieren, kann man auf oben
beschriebene Vorgehensweise zurückgreifen. Der Drucker, auf den die
Arbeitsplätze drucken sollen ist als Windows-Drucker im Netz freizugeben. Für
die Barvorgänge muss dieser Drucker durch Eintrag in den Vorgangsdruckklassen
(evtl. mit individueller Druckumleitung) angesprochen werden. Für
Einzahlungen,... muss in der Kassensystemverwaltung dieser Drucker über seine
IP-Adresse und dem Freigabenamen angesprochen werden (siehe oben).
ACHTUNG: Ich bin mir nicht sicher, ob in dieser
Konstellation mit mehreren Kassen an einem Drucker der POS-Abverkauf möglich ist
(denn hier muss der komplette Beleg hintereinander gedruckt werden, was nur über
BVVE sichergestellt ist, damit keine andere Kasse mal eine Zeile „dazwischen
druckt“).
Aber das Erfassen an der POS-Kasse mit zeilenweisem
Druck funktioniert durchau
[...]


---

## Weitergabe an Bank zur Refinanzierung (nur bei Besitzwechsel)

Weitergabe an Bank zur Refinanzierung (nur bei Besitzwechsel)
Der Inhaber des Besitzwechsels gibt den Wechsel zur
vorzeitigen Diskontierung (Einlösung) einer Bank. Die Bank zahlt nicht die volle
Wechselsumme aus, sondern zieht Diskont und Spesen ab. Dabei gibt es 2
Abwicklungsmöglichkeiten dieser Obligoverbuchung. Der Buchungssatz lautet in
beiden Fällen:
Bank an Besitzwechselobligo
Möglichkeit 1:
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[
FIBE
]
Belegart Zahlungsverkehr Bank anwählen und Buchung
erfassen. Die Buchung erfolgt, wenn die Gutschrift auf dem Bankauszug steht. Da
Besitzwechselobligo als Wechselkonto gekennzeichnet ist, werden bei Eingabe des
Obligokontos die zur Refinanzierung fähigen Wechsel in einem Auswahlbildschirm
aufgelistet.
Nach Auswahl werden der Betrag und das
S/H
-Kennzeichen richtig vorbelegt.
Möglichkeit 2:
Hauptmenü
Finanzbuchhaltung
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechsel bearbeiten
Direktsprung
[
WEB
]
Im Bereich
Wec
[...]


---

## Welche Zeile in einem Grid wurde ausgewählt?

Welche Zeile in einem Grid wurde ausgewählt?
Man hat in AIS die Möglichkeit Controlstrings in Grids
zu definieren, so dass man eine Zeile anwählen kann und von dort aus Makros
(ais_makro) oder VBA-Scripte (ais_vba) ausführen kann. Nun muss man wissen,
welche Zeile in diesem Grid angewählt wurde. Diese Zeile wird in die JVAR
AIS_V_GRIDZEILE geschrieben, unter VBA wäre der Syntax folgender:
Zeile =
Aeins.JVARS_GET(7100, "AIS_V_GRIDZEILE " )

---

## Wertanalyse

Wertanalyse
Um gezielt die berechneten Werte verifizieren und
abgleichen zu können, gibt es für die Bereiche Inventory, Contract und Future
eigene Analysebereiche. Durch Anwahl eines Datensatzes auf dem Bildschirm kann
dann direkt passend die Analyse aufgerufen werden, um per „Drilldown“ direkt die
Einzelpositionen dieser Summarischen Darstellung wieder aufzulösen.

---

## Wiederholen

Wiederholen
Es besteht die Möglichkeit, einen DTA-Datensatz
nachträglich zu erzeugen:
Zur Auswahl stehen:
Die Erstellung der Daten und der Begleitzettel
die Banksammelliste
In dem Feld ‚LaufNummer’ gibt man die Laufnummer an (
Auswahl per F3 möglich !), die sowohl in der Auswahlliste als auch auf der
Banksammelliste ausgewiesen wird.

---

## Wiedervorlage

Wiedervorlage
Hiermit kann einem ausgewählten Vorgang ein
Wiedervorlagevermerk für ein Datum mit einer Bemerkung gegeben werden. Dieser
Vorgang erscheint dann automatisch zu diesem Datum beim Programmstart in einem
Auswahlfenster. Dieses Fenster kann auch jederzeit mit dem Direktsprung WIEDV
oder über die Funktion
Wiedervorlage
bearbeiten
aufgerufen werden.

---

## WRV Belege

WRV Belege
In der Dieser Variante können die Belege dargestellt
und gedruckt werden.

---

## x-Skalierung

x-Skalierung
Horizontaler Skalierungsfaktor zur
Spaltenpositionierung. Vorbelegt mit 1.
Das Raster für die Positionierung
wird mit Hilfe des Basisfonts und der Auflösung des Druckers berechnet. Wenn man
alte ASCII Formulare auf Windows Druck umstellen will, kann es passieren, dass
sich Formularpositionen überlappen. Man könnte im Einrichter jede Position neu
anpassen oder man stellt hier den Faktor entsprechend ein. Der Faktor zwei würde
hier die Rastergröße in der Horizontalen verdoppeln.

---

## y-Skalierung

y-Skalierung
Vertikaler Skalierungsfaktor zur Zeilenpositionierung.
Vorbelegt mit 1.
Das Raster für die Positionierung wird mit Hilfe des
Basisfonts und der Auflösung des Druckers berechnet. Wenn man alte ASCII
Formulare auf Windows Druck umstellen will, kann es passieren, dass sich
Formularpositionen überlappen. Man könnte im Einrichter jede Position neu
anpassen oder man stellt hier den Faktor entsprechend ein. Der Faktor zwei würde
hier die Rastergröße in der Vertikalen verdoppeln.

---

## Zahlmappe

Zahlmappe
Hauptmenü
Mahn-, Zahl-, Zinswesen
Zahlungsverkehr
Zahlmappe
Direktsprung
[ZHMA]
Die Zahlmappe ist eine weitere Möglichkeit,
Zahlungsvorschläge manuell zu erstellen.
Beschreibung
Zahldatum
Datum, dem diese Zahlungsvorschläge
      zugeordnet werden soll. Nach Bestätigung dieses Feldes wird gesucht, ob zu
      diesem Benutzer und diesem Datum bereits eine Liste existiert und diese
      wird dann gegebenenfalls angezeigt. Es besteht auch die Möglichkeit mit
Strg+F3
eine andere existierende Zahlmappe/Zahlungsvorschlagsliste
      auszuwählen.
Bezeichnung
Dies
      ist lediglich ein Text für den Vorschlag. Hat man die Bezeichnung
      verlassen, so werden die Felder
Zahldatum
und
Bezeichnung
deaktiviert und man beginnt mit der Erfassung der Zu bezahlenden OP’s. Man
      kann jederzeit mit der Funktion „
Neue Mappe
“
F5
wieder die
      Felder
Zahldatum
und
Bezeichnung
aktivieren und eine
neue Mappe
beginnen.
Kontonummer
Die
      Nummer des Kunden/Lieferanten, bei d
[...]


---

## Zahlungen bearbeiten

Zahlungen
bearbeiten
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Direktsprung
[ZHB]
Hier erfolgt die endgültige Verarbeitung der
Zahlungsbelege. Es stehen hierfür diverse Funktionen zur Verfügung.
Zahlungsliste
(Druck)
Ein Report kann als Protokoll gedruckt werden:
Formularänderung
(F5)
Hier kann für die
einzelnen Zahlungsbelege die Hausbank, (bei nicht verarbeiteten Zahlungsbelegen)
der Empfänger oder das Formular, mit dem der Scheck gedruckt wird, geändert
werden. Handelt es sich um SEPA-Zahlungen, so kann auch das Ausführungsdatum
hier geändert werden.
Hinweis:
Bei SEPA-Zahlungen
gelten je nach Lastschriftverfahren (Erstlastschrift, Folgelastschrift,
Basislastschrift, Firmenlastschrift) unterschiedliche Fristen. Diese können im
Modul „Zahlungsvorschläge erstellen“ (Direktsprung
[ZHVE]
) eingestellt
werden. Wird hier ein Wert eingetragen, der diese Frist unterschreitet, so wird
automatisch das korrekte Datum (Erstelldatum + Frist) beim DTA ermitt
[...]


---

## Zahlungen mit Karte

Zahlungen mit Karte
Relevante SPA-Einstellungen
SPA 505 -
Manuelle Erfassung von EC-Karten ?:
SPA 579 -
Gekennzeichnete EC Zahlung stornierbar
Die Kombination dieser beiden SPA Einstellungen kann
relevant werden, wenn zum Einzug der Zahlung ein separates Bankterminal benutzt
wird. Wenn mittels dieses Terminals nicht die Möglichkeit besteht, erfolgte
Zahlungen wieder rückgängig zu machen, so soll unbedingt in Referenz-ERP auch der SPA
576 -„Gekennzeichnete EC Zahlung stornierbar“ auf nein gestellt sein.
Dann nämlich gibt es in Referenz-ERP keine Möglichkeit,
diese Zahlung zu revidieren (Funktion „Zahlungsweg stornieren“) oder den Beleg
abzubrechen.
Bei Verwendung dieser SPA Kombination wird die
Belegverarbeitung für die online –Transaktion am Bankterminal unterbrochen und
wird erst nach Bestätigung, dass die Zahlung korrekt erfolgt ist, fortgesetzt.
Wird die Bestätigung verweigert, so wird der
Zahlungsweg storniert und die Zahlung kann erneut eingegeben oder der Beleg
abgebrochen werden
[...]


---

## Zahlungen erstellen

Zahlungen erstellen
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen erstellen
Direktsprung
[ZHE]
Die Aufgabe dieser Programmfunktion besteht darin,
zügig Einzelzahlungen zu erstellen. Auch können hier Akontozahlungen, also
Zahlungen, die sich nicht auf einen offenen Posten beziehen durchgeführt werden.
Mit Anwahl dieses Menüpunktes erscheint folgende Erfassungsmaske:
Der
Stichtag
ist der Tag, auf den sich die sich
der Skonto und bei arbeiten mit Fremdwährung die Währungskurse beziehen.
Nach Anwahl der
Hausbank
, für die der Beleg erstellt werden soll,
werden Saldo, maximaler Überweisungsbetrag und Kreditlimit
angezeigt.
Anschließend können die vorgeschlagenen
Zahlungsformulare
für Zahlungseingang
bzw. Zahlungsausgang geändert werden. Sind diese Angaben gemacht worden werden
diese Felder blau eingefärbt und sind nicht mehr zu ändern.
Man kann die
Kontonummer
angeben, für die die
Zahlung erstellt werden soll. Ist diese nicht bekannt, so kann nach Belegnummer
bzw. Ref
[...]


---

## Zahlung in den verschiedenen Kassensystemen

Zahlung in den verschiedenen Kassensystemen
In Referenz-ERP gibt es verschiedene Arten, eine Zahlung
vorzunehmen.
Die
klassische Zahlungsmaske
steht in allen drei
Kassenarten zur Verfügung.
Die
Touch-fähige Zahlung
steht
ausschließlich in der Marktkasse zur Verfügung.

---

## Zahlungsvorschläge bearbeiten

Zahlungsvorschläge
bearbeiten
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungsvorschläge bearbeiten
Direktsprung
[ZHVB]
In der Anwendung „Zahlungsvorschläge bearbeiten“
werden automatisch und manuell erstellte Zahlungsvorschläge aufgelistet. Für die
mögliche Weiterverarbeitung geben die Spalten Verfahren und Hinweistext
Auskunft. Eventuelle Probleme der Bankverbindung werden in der Spalte
Hinweistext ausgegeben und können so gezielt abgearbeitet werden.
In der Spalte Verfahren können folgende Werte
stehen:
•
Auslandszahlungsverkehr: Die OP’S werden über den Auslandszahlungsverkehr
beglichen. Im Hinweistext kann noch ein Problem in der Bankverbindung
aufgelistet sein.
•
SEPA: Wenn alle für SEPA erforderlichen Daten korrekt sind, werden die
OP‘s im SEPA-Verfahren abgewickelt.
•
Leer: Die OP’s können im DTA-, DTINT-Verfahren oder zum Scheckdruck
freigegeben werden. Im Hinweistext stehen dann Hinweise, warum diese nicht mit
dem SEPA-Verfahren abgewickelt werden können.

[...]


---

## Zeichnung neuer Anteile

Zeichnung neuer Anteile
Um neue Anteile zu zeichnen wird der
Gesellschafter(Mitglied) in der Auswahlliste markiert und mit
Bearbeiten
F5
wird die Erfassungsmaske geöffnet. Jetzt
können mit
Zeichnen F5
neue Anteile
gezeichnet werden.
Die Funktion
Zeichnen
F5
aktiviert folgende Eingabefelder:
Felder
Anzahl
Hier
      wird die Anzahl der Anteile eingetragen die gezeichnet werden
      soll.
Anteilstyp
Hier
      wird der Anteilstyp
F3
freiwillig oder pflicht eingetragen.
Zeichnungsdatum
Hier
      wird das Zeichnungsdatum hinterlegt.
Bemerkung zum Vorgang
Hier
      kann eine Bemerkung zum Vorgang eingetragen werden. (60
      Zeichen)

---

## Zeilenumbruch in Multiline Texten

Zeilenumbruch in Multiline Texten
Will man die Darstellung in Multiline-Textfeldern
formatieren, so kann man die einen Zeilenumbruch dadurch erzwingen, indem man
‚\n‘ in den Text einfügt:
Select
‘Zeile1\nZeile2\nZeile3 und jetzt kommt erst Zeile4\nZeile4‘ as
Ergebnis
Das Ergebnis sieht dann folgendermaßen aus:

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

## Zielbank bzw. Währung

Zielbank bzw. Währung
Diese Filter sind immer aktiv . Sie stellen sicher,
das die DTA-Dateien den Vorschriften entsprechend erstellt werden. ACHTUNG:
DTINT-Datenträger können nur erstellt werden, wenn als Zielbank ‚eigene Bank’
eingestellt ist.

---

## zu Stapel hinzufügen

zu Stapel hinzufügen
Durch Aufruf der Funktion „
zu Stapel hinzufügen
“
Strg+F8
werden automatisch die ausgewählten
Datensätze zu einem Stapel hinzugefügt. Es ist dazu nicht zwingend notwendig,
vorher einen Stapel anzulegen. Dabei wird nach folgender Logik der Stapel
bestimmt:
1.
Existiert noch kein Stapel, so wird automatisch ein Stapel mit dem Namen
„Stapel_1“ angelegt.
2.
Existiert genau ein Stapel, so wird dieser verwendet.
3.
Ansonsten öffnet sich eine F3-Auswahl, aus der man einen der Stapel auswählen
kann.
Sind Vorgänge der Warenwirtschaft in einem Stapel
zusammengefast, so werden bei bestimmten Aktionen – z.B. Umwandeln Rechnung aus
Lieferschein – automatisch Vorgänge dem Stapel hinzugefügt Wenn man also aus der
Stapelverarbeitung heraus einen Lieferschein in eine Rechnung umwandelt, so wird
die Rechnung automatisch dem ausgewählten Stapel zugeordnet. Ist ein Stapel
aktiv – unabhängig, ob man im Bearbeitungsmodus der Stapelverarbeitung ist oder
nicht - und m
[...]


---

## Zusätze

Zusätze

---

## Zwischensummen

Zwischensummen
Es ist möglich, auf allen Spalten und allen Zeilen
Zwischensummen anzuzeigen. Dies lässt sich im Menu Tabelle > Gesamtsumme von
Zeilen bzw Spalten > Teilergebnisse einschalten.
Wenn einzelne Teilergebnisse nicht gewünscht sind, so
können diese in der Übersicht „Zwischensummen“ im Menu abgewählt werden.
Die Angaben zu gewählten bzw. abgewählten
Zwischensummen werden mit dem Titel gespeichert.

---

