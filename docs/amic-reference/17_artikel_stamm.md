# Artikelstamm & Warengruppen — Referenz-ERP Referenzwissen

> 437 Seiten

## Artikel

Artikel
Auf diesem Tabs werden gezielt Änderungen eines
Attributs von Datensätzen in Relationen gesucht, die bestimmten Artikeln
und/oder Artikelstämmen zuzuordnen sind. Die Angaben in den Feldern
Artikelstammnummer, ArtiStammId, Artikelnummer
und A
rtikelId
sind
optional, es muss aber mindestens zu einem dieser Felder eine Eingabe erfolgen.
Die Angabe einer Lagernummer ist ebenfalls optional. Alle genannten
Eingabefelder verfügen über eine unterstützende Itembox-Anbindung.
Wird lediglich ein Artikelstamm durch Angabe der
Artikelstammnummer oder ArtiStammId spezifiziert, so ist die Basis für
artikelbasierte Suchanfragen die Menge aller Artikel, die zu diesem Artikelstamm
gehört. Die Angabe einer Lagernummer schränkt die Basis auf die Artikel des
spezifizierten Lagers ein.
Wird ein Artikel per Artikelnummer spezifiziert, so
ist die Basis für artikelbasierte Suchanfragen die Menge aller Artikel, die
diese Artikelnummer haben. Die Angabe einer Lagernummer schränkt die Basis auf
die Artikel des spezifizierten Lagers ein.
Wird ein Artikel per ArtikelId spezifiziert, so ist
die Basis für artikelbasierte Suchanfragen nur der angegebene Artikel.
Zu beachten ist, dass gegebenenfalls auch Artikel mit
Löschkennzeichen berücksichtigt werden.
Die Angabe des auszuwertenden Attributnamens wird
durch eine Itembox unterstützt, die auch über eine Auflistungsvariante nach den
hier erlaubten Relationsnamen verfügt und nach Auswahl des Attributs auch den
zugehörigen Relationsnamen in das entsprechende Maskenfeld schreibt.
Existieren Attribute mit dem angegeben Namen in
mehreren Relationen, so kann diese, ebenfalls unterstützt durch eine
entsprechende Itembox, angegeben werden.
Der zu untersuchende Zeitraum bezüglich des
Logfile-Archivierungsdatums, wie auch die maximale Anzahl der Datensätze, die in
die Auswahlliste zu übernehmen sind, können angegeben werden. Die Suche erfolgt
grundsätzlich beginnend mit dem Bis-Datum hin zum Ab-Datum und bricht bei
Erreichen der
[...]


---

## Intrastat Export Anpassung

Intrastat Export Anpassung
Im Intrastatstammdaten-Pfleger ("Intrastat
einrichten") kann nun eine private View für den Export angegeben werden.
Releasenote Kategorie:
Ticket: 713532[32748]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: Intrastat
Variante: alle
Funktion/Report: Stammdaten (F10)
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32748, 713532

---

## Staatstamm "Staaten einspielen" entfernt

Staatstamm "Staaten einspielen" entfernt
In der Anwendung "Staatstamm" [STAAT] wurde die
Funktion "Staaten einspielen" entfernt.
Releasenote Kategorie:
Ticket: 712249[32786]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [STAAT]
Variante: Staatstamm
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2210.20, 32786, 712249

---

## Pfleger: Artikel & Artikelstamm

Pfleger: Artikel & Artikelstamm
Die Pfleger für den Artikel und den Artikelstamm
wurden überarbeitet. Dies dient der Vorbereitung auf die 64bit Version.
Releasenote Kategorie:
Ticket: 0[32795]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: Artikel/Artikelstamm
Variante: Alle
Funktion/Report: SDI (F5,F6,F7,F8)
Weitere Informationen
Tags:
Releasenote, 8.3.2210.20, 32795, 0

---

## Anschrift im Objektstamm

Anschrift im Objektstamm
Die Erfassung der Objektanschrift ist nun auch im
"Neu"-Fall möglich.
Releasenote Kategorie:
Ticket: 714385[32840]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [OBJ]
Variante: --
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2210.20, 32840, 714385

---

## Automatischer Zahlungsverkehr/ SEPA-Version

Automatischer Zahlungsverkehr/ SEPA-Version
Die SEPA-Formate für die Version 3.5 (gültig ab
21.11.2021) und Version 3.6 (gültig ab 20.11.2022) wurden in Referenz-ERP integriert.
Dies kann im Hausbankenstamm [HBNK] eingerichtet werden.
Releasenote Kategorie:
Ticket: 700323[32958]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32958, 700323

---

## Makro-Programme

Makro-Programme
Der Pflege-Unterbau der Makro-Programme hat eine
Überarbeitung erfahren. Dabei wurde  1) die bisherige Funktion "ansehen" in
der Auswahlliste mit Taste "F6" zu "Makro-Text ansehen" mit Taste "ShF6". 2) die
bisherige Funktion "ausführen" im Pfleger mit Taste "F9" zu "ausführen" mit
Taste "ShF6". 3) der Neu-Modus fehlerbereinigt und unterstützt u.a. das
Vorlage-System. 4) im "Neu"-Modus automatisch ein funktionierendes
Vorlagen-Makro zugewiesen. 5) die Variante "Schnipselsuche" entfernt, die
Funktionalität übernimmt die Variante "Makro-Programme",
Releasenote Kategorie:
Ticket: 0[32968]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: ScriptStamm
Variante: ScriptStamm
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2211.9, 32968, 0

---

## Paginiernummer (Archivreferenz)

Paginiernummer (Archivreferenz)
Der Pfleger "Paginiernummer" [FISV] wurde
entfernt.  Stattdessen kann die Paginiernummer (Archivreferenz) in der
Einzelbeleganzeige (Funktion: "Ansehen Beleg") über die Funktion "Archivreferenz
ändern" angepasst werden.
Releasenote Kategorie:
Ticket: 0[32997]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: -
Variante: -
Funktion/Report: Archivreferenz ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32997, 0

---

## Stoffstromanteil pflegen

Stoffstromanteil pflegen
Im Pfleger für individuelle Artikelnummern wird jetzt
nur bei Anteilen mit Stoffstrom der Tabreiter zur Stoffstrompflege
dargestellt.
Releasenote Kategorie:
Ticket: 715405[33004]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Artikelstamm
Variante: Individuelle Artikelnummern
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33004, 715405

---

## Hersteller bei individuellen Artikelnummern

Hersteller bei individuellen Artikelnummern
In der Anwendung Artikelstamm Variante "Individuelle
Artikelnummern" werden jetzt die Hersteller korrekt angezeigt.
Releasenote Kategorie:
Ticket: 715634[33083]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Artikelstamm [ARS]
Variante: Individuelle Artikelnummern
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33083, 715634

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

## Artikelstamm: SQL-Fehler

Artikelstamm: SQL-Fehler
Bei der Neuanlage von Artikelstammdaten gab es einen
SQL-Fehler, wenn keine Mengeneinheitsgruppe mit der Nummer 1 eingerichtet war.
Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 717422[33292]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Artikelstamm
Variante: -
Funktion/Report: Neu
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33292, 717422

---

## Folgeartikel

Folgeartikel
Ein Folgeartikel wurde unter Umständen nicht korrekt
gezogen. Dies wurde behoben
Releasenote Kategorie:
Ticket: 720339[33461]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33461, 720339

---

## Folgeartikel/indiv. Artikelnummer verschoben

Folgeartikel/indiv. Artikelnummer verschoben
Die Varianten für Folgeartikel und individuelle
Artikelnummern wurden in eigene Anwendungen verschoben. Sie sind über die
Direktsprünge [ARSF] bzw. [ARSI] aufrufbar
Releasenote Kategorie:
Ticket: 720569[33470]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Artikelstamm
Variante: Folgeartikel/indiv. Artikelnummer
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33470, 720569

---

## Druckfelder-Pfleger

Druckfelder-Pfleger
Bei der Funktion "Speichern unter" kam es vor, dass
der Wert nicht gespeichert wurde. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 720536[33591]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Formularwesen
Variante: Druckfelder
Funktion/Report: Speichern unter
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33591, 720536

---

## Auswahlliste 'Kontrakte auch ohne Artikel'

Auswahlliste 'Kontrakte auch ohne Artikel'
In der Auswahlliste 'Kontrakte auch ohne Artikel' der
Anwendung 'Kontrakt Stammdaten' [KTR] wurde ein Filterkriterium zur Anzeige von
Musterkontrakten hinzugefügt.
Releasenote Kategorie:
Ticket: 723233[33807]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: Kontrakt Stammdaten [Ktr]
Variante: Kontrakte auch ohne Artikel
Funktion/Report: alle
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33807, 723233

---

## Protokoll FIBU-Übertrag erweitert um Artikelnummer

Protokoll FIBU-Übertrag erweitert um Artikelnummer
Beim Protokoll Fibuübertrag [FIBF] in
der Variante "Protokoll Fibuübertrag" werden, sofern sinnvoll, die
Artikelnummern mit angezeigt.
Releasenote Kategorie:
Ticket: 724205[33973]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Protokoll FIBU-Übertrag
Variante: Protokoll FIBU-Übertrag
Funktion/Report: [FIBF]
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33973, 724205

---

## Artikelstammtext speichern.

Artikelstammtext speichern.
Bei längeren Artikeltexten (mehr als 10 Zeilen) konnte
es beim Speichern zu einem Fehlverhalten kommen. Der Artikelstammtext wird nun
in jedem Fall beim ersten Speicherversuch korrekt gespeichert.
Releasenote Kategorie:
Ticket: 725583[34019]
Version: 8.3.2308.4
Datum: 04.08.2023
Anwendung: Artikelstamm [ARS]
Variante: Artikelstamm
Funktion/Report: Textzeilen(F5)
Weitere Informationen
Tags:
Releasenote, 8.3.2308.4, 34019, 725583

---

## Stammdatenpflege Funktionalität "Alle Ändern"

Stammdatenpflege Funktionalität "Alle Ändern"
Die Funktion "Alle Ändern", die bei einigen
Stammdatenpflegern angeboten wird, hat bisher nur mit Singelline-Texten
gearbeitet. Jetzt werden auch Multilinetexte, die als Wordwrap-Array
gekennzeichnet sind, verarbeitet.
Releasenote Kategorie:
Ticket: 725889[34088]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34088, 725889

---

## Artikelverpackung

Artikelverpackung
Bisher wurde beim Löschen eines
Artikelverpackung-Stammdatensatzes [AVP] nur ein Löschkennzeichen gesetzt. Jetzt
wird kein Löschkennzeichen mehr gesetzt, sondern der Datensatz wird direkt aus
der Datenbank entfernt.
Releasenote Kategorie:
Ticket: 0[34095]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [AVP]
Variante: -
Funktion/Report: F7 - Löschen
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34095, 0

---

## CO2 Artikelstammpflege

CO2 Artikelstammpflege
Im Artikelstammpfleger wurde im Modul
CO2-Kostenaufteilungsgesetz die Feldbezeichnung zum Feld "Gewicht pro ME" für
die CO2-Angabe korrigiert. Statt "t/(Mengeneinheit)" lautet er jetzt
"kg/(Mengeneinheit)", da intern mit "kg/(Mengeneinheit)" gerechnet wird.
Releasenote Kategorie:
Ticket: 719616[34121]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [ARS]
Variante: n/a
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34121, 719616

---

## Artikelstammtexte

Artikelstammtexte
Die Artikelstammtexte können für andere Sprachen oder
andere Varianten angelegt werden. Unter Umständen wurde nach Änderung
der Variante/Sprache der falsche Artikeltext angezeigt.
Releasenote Kategorie:
Ticket: 726842[34202]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Artikelstamm [ARS]
Variante: --
Funktion/Report: F5
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34202, 726842

---

## Artikelstamm: Mengeneinheitengruppe

Artikelstamm: Mengeneinheitengruppe
Beim Artikelstammpfleger war es möglich eine
Mengeneinheitsgruppe auszuwählen, die nicht kompatibel zur aktuellen
Mengeneinheitsgruppe war.  Dies wurde behoben.
Releasenote Kategorie:
Ticket: 728095[34447]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: Artikelstamm [ARS]
Variante: -
Funktion/Report: F5 Ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34447, 728095

---

## Tastatursteuerung: Warenbewegung-Addon

Tastatursteuerung: Warenbewegung-Addon
Bei Warenbewegung-Addonfeldern, die bei der
Artikelerfassung im Vorgang unterhalb des Tab Reiters "Allgemein" angeordnet
waren, gab es Probleme bei der Tastatursteuerung. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 728753[34509]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: Vorgangserfassung
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2311.10, 34509, 728753

---

## Ermittlung der Werte in der Perioden-Erfolgsauswertung

Ermittlung der Werte in der Perioden-Erfolgsauswertung
Es kam bei einigen Artikeln zu fehlerhaften
Ermittlungen der Werte in der Perioden-Erfolgsauswertung. Das Problem wurde nun
korrigiert.  Wichtig: Eine Korrektur der fehlerhaften Einträge erfolgt erst
durch eine Gesamtreorganisation mit [WAREO].
Releasenote Kategorie:
Ticket: 729146[34520]
Version: 8.3.2312.8
Datum: 08.12.2023
Anwendung: Periodenerfolgsauswertung
Variante: Alle
Funktion/Report: Perioden-Erfolgsauswertung
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.8, 34520, 729146

---

## Individuelle Artikelnummern

Individuelle Artikelnummern
In der Anwendung Individuelle Artikelnummern [ARSI]
können jetzt unterschiedliche Datensätze von mehreren Bedienern gleichzeitig
bearbeitet werden.
Releasenote Kategorie:
Ticket: 729122[34570]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Individuelle Artikelnummern
Variante: alle
Funktion/Report: [ARSI]
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.22, 34570, 729122

---

## Artikelstammtexte Zeile/Spalte

Artikelstammtexte Zeile/Spalte
Die Anzeige der aktuellen Zeile und Spalte in der
Artikeltexterfassung wurde überarbeitet und wieder aktiviert.
Releasenote Kategorie:
Ticket: 728919[34553]
Version: 8.3.2312.8
Datum: 08.12.2023
Anwendung: ARS
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2312.8, 34553, 728919

---

## Artikel Gebinde anzeigen

Artikel Gebinde anzeigen
Hatte man sich im Artikelpfleger [AR] die Gebinde
angesehen (Funktionstaste F6), wurden diese bei folgenden Aufrufen nicht mehr
angezeigt, obwohl sie weiterhin korrekt vorhanden waren.
Releasenote Kategorie:
Ticket: 729311[34571]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Artikel
Variante: alle
Funktion/Report: [AR] -F6 Ansehen
Weitere Informationen
Tags:
Releasenote, 8.3.2312.22, 34571, 729311

---

## Mengeneinheit und Gebinde bei individuellen Artikelnummern

Mengeneinheit und Gebinde bei individuellen Artikelnummern
In der Anwendung
"Formularzuordnung/Vorgangsunterklasse" [FRZ] steht auf der Registerkarte
"Eingabe" nun ein Feld zur Regelung der Vorbelegung von Mengeneinheit und
gegebenenfalls Gebindefaktoren aus den Zuordnungsdaten von "individuellen
Artikelnummern" [ARSI] zu Artikelstämmen bei der Erfassung von Warenpositionen
in der Vorgangserfassung und Vorgangskorrektur zur Verfügung.  Bei der
Einstellung "Ja" werden optionale Mengeneinheiten,
Mengen-/Gebindeneinheitsbezeichnungen und Gebindefaktoren sowie deren
Änderbarkeitskennzeichen zur Vorbelegung bei der Erfassung einer Warenpositionen
herangezogen, wenn dem Artikel eine kunden-/lieferantenspezifische Mengeneinheit
zugeordnet ist. Bei Folgeartikeln, Komponenten von Handelsstücklisten sowie
Produktions- und Rohwarevorgängen ist diese Option nicht wirksam. Näheres
ist der Hilfe zu "Formularzuordnung/Vorgangsunterklasse" [FRZ] und "individuelle
Artikelnummern" [ARSI] zu entnehmen.
Releasenote Kategorie:
Ticket: 710307[32321]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Individuelle Artikelnummern [ARSI]
Variante: alle
Funktion/Report: F5 Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 32321, 710307

---

## Nummernkreisgültigkeiten

Nummernkreisgültigkeiten
Seit längerer Zeit ist es möglich die
Nummernkreisgültigkeiten direkt im Nummernkreisstamm [NKS] zu pflegen. Um
Doppelungen zu vermeiden wurde der Pfleger Nummernkreisgültigkeiten [NKG]
ausgebaut.
Releasenote Kategorie:
Ticket: 727631[34477]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Nummernkreisstamm [NKS]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34477, 727631

---

## Excelimport [EXCELI]: Import an Offsetposition

Excelimport [EXCELI]: Import an Offsetposition
Im Excelimport-Pfleger [EXCELI] wurde die Funktion
"Import an Offsetposition" entfernt. Stattdessen kann jetzt im Pfleger eine
private Datenbankprozedur angegeben werden. Über diese Prozedur kann die beim
Import angelegte Tabelle zeilenweise ausgelesen und weiterverarbeitet
werden.
Releasenote Kategorie:
Ticket: 731079[34729]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: [EXCELI]
Variante: -
Funktion/Report: Import an Offsetposition
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34729, 731079

---

## Artikelstamm THG-Werte wurden ausgebaut. Im Artikelstamm kann ein Artikel für Einkauf und Verkauf künstlich als nicht nachhaltig vorbelegt werden.

Artikelstamm THG-Werte wurden ausgebaut. Im Artikelstamm kann ein Artikel
für Einkauf und Verkauf künstlich als nicht nachhaltig vorbelegt werden.
Unter [NAWER] der Variante THG-Werte können auf der
Maske Nachhaltigkeit - THG-Werte keine Anbau -, Lieferung -, und Verarbeitung
THG-Werte angelegt oder gepflegt werden. Diese Werte werden auch bei der
THG-Wert-Bestimmung und Vorbelegung nicht mehr berücksichtigt. Des Weiteren kann
man auf dem Artikelstamm einen Artikel "künstlich" als nicht nachhaltig für den
Einkauf oder Verkauf einrichten. [ARS] Auf der Artikelstammmaske auf dem
Tabreiter Konstanten kann man im Nachhaltigkeitsblock, wenn der
Nachhaltigkeitsartikel auf Ja steht, im Vorbelegung Warenbewegungsgrid ein Datum
eintragen ab dem die Vorbelegungs-Einrichtung gilt, wie für den Artikel der
Einkauf und Verkauf vorbelegt sein soll. Achtung: Es wird dort nur Nicht
Nachhaltig in dem Grid beachtet, weil man nachhaltige Ware nur mit einem
gültigen Zertifikat hat.
Releasenote Kategorie:
Ticket: 727580[34757]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: [NAWER] [ARS] [REB] [ERB] [LIB] [AUB]
Variante: THG-Werte
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34757, 727580

---

## Nachhaltigkeit: Anbauländer

Nachhaltigkeit: Anbauländer
Kunden, die einem Artikel aus mehreren Anbauländer
handeln/erzeugen, müssen mehrere Kundenzertifikate auf dem Kundenstammpfleger im
Nachhaltigkeitsgrid hinterlegen. Früher wurde das erstbeste Kundenzertifikat für
den Artikel gezogen.  Dies kann man verhindern, wenn man explizit für den
Einkauf in der Kundenversandanschrift[KUVS] auf dem Pfleger ein Anbauland angibt
und dann bei der Belegerfassung die Kundenversandanschrift auswählt. Des
Weiteren kann man in der Hauptanschrift des Kunden ein Anbauland angeben. Das
Kunden-Anbauland wird gezogen wenn keine Versandanschrift mit Anbauland
ausgewählt wurde.  Für den Verkauf geht man in den Lagerstamm [LGS] und
trägt im Lagerstamm das Anbauland ein. Unter Verkauf im Kontext der
Nachhaltigkeit fallen auch die Umbuchungs- und Produktions-Vorgangsklassen
(5100, 5110, 5120, 5200, 5210, 5220).  Falls in der Hauptanschrift,
Kundenversandanschrift oder Lageranschrift ein Anbauland eingetragen wurde, für
das der Belegkunde (Einkauf) oder Mandantkunde (Verkauf + die oberen
Vorgangsklassen) kein Zertifikat besitzt, wird das Anbauland über das erste
gültige Zertifikat des Kunden für diesen Artikel bestimmt.  Daher gibt es
auf dem Nachhaltigkeitsreiter der Warenerfassungsmaske die zusätzlichen Felder
Hauptanschrift / Versandanschrift. Ebenso ist es möglich auf der
Warenerfassungsmaske per Knopfdruck den nachhaltigen Bestand des Artikels zu
ermitteln.  Der Beleg aus dem diese Funktion aufgerufen wird, wird bei der
Berechnung des Bestandes nicht berücksichtigt.
Releasenote Kategorie:
Ticket: 727580[34758]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Anschriften [ANSCH], Kundenversandanschrift
[KUVS], Lagerstamm [LGS]
Variante: Anschriften, Kundenversandanschrift,
Läger
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34758, 727580

---

## Veränderung bei Artikel Ein- und Verkaufssperre

Veränderung bei Artikel Ein- und Verkaufssperre
Im Artikelpfleger wurden auf dem Tab-Reiter
"Weitere Kennzeichen" die Eingabefelder für Ein- und Verkaufssperre in
Abhängigkeit vom Steuerparameter 791 änderbar gemacht. Die Felder lassen sich,
wenn der Steuerparameter 791 auf "Ja" steht, nicht ändern. Sie sind gesperrt
(hellblau hinterlegt).
Releasenote Kategorie:
Ticket: 732390[34891]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Artikelpfleger [AR]
Variante: -
Funktion/Report: Standartfunktionen (F5, F6, F7,
F8...)
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34891, 732390

---

## Nach Kunden-indiv. Artikelnummer verbessert und auf den aktuellen Kunden begrenzt

Nach Kunden-indiv. Artikelnummer verbessert und auf den aktuellen Kunden
begrenzt
Auf der SVWare Maske (Belegartikelerfassung wurde die
ItemBox) IB_Artikel_KundenIndivNummer mit dem Namen "Nach Kunden-indiv.
Artikelnummer" so umgebaut, dass diese sich auf den aktuellen Kunden bezieht und
für Performance sorgt. Kunden, die diese ItemBox privatisiert haben, müssen sich
diese Änderungen selber einrichten.
Releasenote Kategorie:
Ticket: 731753[34899]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: Belegerfassung
Variante: SVWare
Funktion/Report: F5, F4
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.3, 34899, 731753

---

## Artikel F3-Auswahl auf Warenposition optimiert

Artikel F3-Auswahl auf Warenposition optimiert
In der Belegerfassung/Bearbeitung wurde auf der
Warenpositionsmaske die F3-Auswahl auf dem Feld Artikel optimiert, für den Fall
das mit Objekt (Baustelle) gearbeitet wird.  Der EPA auf der SVWARE-Maske
mit der Beschreibung "Bei Baustelle nur Baustellenartikel in IB
anzeigen" sorgt dafür, dass in allen Artikel F3-Auswahlen nur Artikel
angezeigt werden, die für das Objekt (Baustelle) auch gültig sind. Mit der
EPA-Einstellung "Nein" werden wie bisher alle Artikel angezeigt für das
ausgewählte Lager. Sofern aus historischen oder individuellen Gründen die
F3-Auswahl "Nur Objektartikel" auf dem Artikelfeld angebunden ist, wird der EPA
nicht ausgewertet.
Releasenote Kategorie:
Ticket: 732902[35000]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: -
Variante: -
Funktion/Report: F3-Auswahl
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 35000, 732902

---

## Baustellenartikellogik in den Itemboxen und somit für jeden privatisierbar

Baustellenartikellogik in den Itemboxen und somit für jeden
privatisierbar
In der Vorgangserfassung können bei Verwendung
eines Objektes Fremdartikel wieder eingefügt werden, sofern der
Parameter "Fremdartikel Zulässig" im Objektstamm auf "Ja" gesetzt wurde.
Releasenote Kategorie:
Ticket: 735165[35275]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: Objekt [OBJ]
Variante: Objektstamm nach Nummer
Funktion/Report: F8, F5
Weitere Informationen
Tags:
Releasenote, 9.0.2401.3, 35275, 735165

---

## Stammdatenfunktion "Alle Ändern"

Stammdatenfunktion "Alle Ändern"
Zum ändern von Stammdaten existiert eine Funktion
"Alle Ändern". Diese zeigt jetzt die Anzahl der Felder an, die von der Änderung
betroffen sind:"Sollen die 12 eingefärbten Felder für alle ausgewählten Daten
übernommen werden?"
Releasenote Kategorie:
Ticket: 734584[35469]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35469, 734584

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

## Onlinewaage Versandanschrift

Onlinewaage Versandanschrift
In der Waagemaske kann in dem Feld Versandadresse eine
F3-Auswahl aufgerufen werden. Dort hatte die Funktion "Stammdaten" F8 keine
Wirkung. Jetzt wird dort der Pfleger zur Neuanlage einer Versandanschrift
aufgerufen.
Releasenote Kategorie:
Ticket: 736953[35519]
Version: 9.0.2402.2
Datum: 22.10.2024
Anwendung: WAAGE
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2402.2, 35519, 736953

---

## Rollenpflegerstamm Aktualisierung

Rollenpflegerstamm Aktualisierung
Die ausgelieferte Relation "Rollenpflegerstamm" wurde
aktualisiert. Dadurch sind Fehlermeldungen hinsichtlich einer leeren Rolle in
Pfleger-Kontexten nicht länger zu erwarten.
Releasenote Kategorie:
Ticket: 739219[35848]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Pflegerstamm/Rolle
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35848, 739219

---

## Formularstamm - Pfleger

Formularstamm - Pfleger
Die Register-Karte "Importe" wurde reaktiviert.
Releasenote Kategorie:
Ticket: 738433[35849]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Formularstamm
Variante: STD
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35849, 738433

---

## Druckerstamm: Kennzeichen "Ohne ASCII Konvert."

Druckerstamm: Kennzeichen "Ohne ASCII Konvert."
Im Zusammenhang mit dem Feature "Queue / Datei" und
dem Druck in eine Datei wurde offenbar das Kennzeichen "Ohne ASCII Konvert."
nicht berücksichtigt. Das führte dazu das die Umlaute der üblichen
Sonderbehandlung im ASCII-Druck-Umfeld unterlagen, was aber im "Datei-Druck" zu
Fehlern führt, da dieser die Umlaute schon richtig erzeugt. Durch den nun
funktionierenden Schalter lässt sich die "Sonderbehandlung" abstellen, mit dem
Effekt das die Umlaute unverändert und richtig durchgeleitet werden. Zusätzliche
Erläuterung sei erwähnt:Wenn z.B. in eine Spool-Datei (Notepad) / auf ein Fax
gedruckt wurde, wurden gewisse Zeichen (z.B. Umlaute) nicht korrekt dargestellt.
Hierfür ist dieses Kennzeichen eingerichtet. Wird dieses auf "Ja" gestellt,
wird die zusätzliche Zeichenkonvertierung ausgeschaltet und auch diese
Sonderzeichen werden korrekt dargestellt. Die "Defaulteinstellung" ist
"Nein", das Verhalten bleibt wie bisher. Bei normalen Druckern sollte die
Voreinstellung "Nein" beibehalten bleiben.
Releasenote Kategorie:
Ticket: 740321[35876]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Druckerstamm
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35876, 740321

---

## Reporte

Reporte
Die Reporte Verkaufsauswertung nach Kunde/Vertreter
"verausw.rpt" Warenbuchsummen über Warengruppen "wbulg2.rpt"  wurden
überarbeitet Der Report Artikel-Umsatzliste "verkart.rpt" wird nicht mehr
ausgeliefert.
Releasenote Kategorie:
Ticket: 739676[35973]
Version: 9.0.2501.5
Datum:
Anwendung: ANWR, LST
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35973, 739676

---

## Kontraktdruck: Artikelzeile mit Sollmenge

Kontraktdruck: Artikelzeile mit Sollmenge
In der Funktion "Kontraktdruck" der Anwendung
"Kontrakt Stammdaten" konnte es zuletzt vorkommen, dass bei eingerichteter
Position "Zahl-Variable" (4) mit dem Eintrag "SollMenge" in der Spalte "Text" im
Druckbereich "Kontrakt-Artikelposition" (204) für die erste Artikelposition
keine Sollmenge und für folgende Artikelpositionen jeweils die Sollmenge der
vorhergehenden Artikelposition ausgegeben wurde. Dieses Verhalten wurde nun
überarbeitet.
Releasenote Kategorie:
Ticket: 740699[35994]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Kontrakt Stammdaten [KTR]
Variante: Kontrakte
Funktion/Report: Kontraktdruck F10
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 35994, 740699

---

## Archiv-Stammdatenpfleger Funktion "Belegreferenz erzeugen"

Archiv-Stammdatenpfleger Funktion "Belegreferenz erzeugen"
Die Funktion "Beleg-Referenz erzeugen" verwendet nun
das Belegdatum. Damit ist gewährleistet das man nach Pflege der entsprechenden
Eingabefelder die gewünschte Jahrnummer erhält. Somit besteht die Möglichkeit
ein Dokument mit dem anvisierten Vorgang zu referenzieren.
Releasenote Kategorie:
Ticket: 741264[36248]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: Archiv
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36248, 741264

---

## Artikelstamm: Gefahrgut

Artikelstamm: Gefahrgut
Im Artikelstamm [ARS] werden Artikel nun auch als
Gefahrgut gekennzeichnet, wenn in der Zusammensetzung, in der Gefahrgutmaske,
andere Artikel hinterlegt wurden.
Releasenote Kategorie:
Ticket: 742052[36541]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Artikelstamm
Variante: STD
Funktion/Report: [ARS]
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36541, 742052

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

## Objektstamm: Zahlungsbedingung

Objektstamm: Zahlungsbedingung
Der Pfleger "Objektstamm" [BAU]/[OBJ] hatte die
hinterlegte Zahlungsbedingung immer wieder mit der Zahlungsbedingung des
hinterlegten Kunden überschrieben.   Das Verhalten wurde
korrigiert.
Releasenote Kategorie:
Ticket: 745693[36691]
Version: 9.0.2501.5
Datum:
Anwendung: Objektstamm
Variante: -
Funktion/Report: [OBJ] - Ändern
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36691, 745693

---

## Wiegen gegen einen Vorgang

Wiegen gegen einen Vorgang
Wenn zwei Artikel mit identischem Artikelstamm im
selben Lager existieren und für einen dieser Artikel ein Auftrag erfasst wurde,
konnte es in bestimmten Fällen vorkommen, dass bei einer Verwiegung gegen den
Auftrag fälschlicherweise der andere Artikel (ohne Auftrag) verwendet wurde.
Dieses Verhalten wurde nun korrigiert: Das System zieht bei der Verwiegung nun
zuverlässig denjenigen Artikel, für den auch tatsächlich ein Auftrag
vorliegt.
Releasenote Kategorie:
Ticket: 739549[36731]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Waage
Variante: Hofliste
Funktion/Report: Vorgänge erzeugen
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36731, 739549

---

## Vermehrungsvertrag Owaage

Vermehrungsvertrag Owaage
Wenn in der Online-Waage ein Artikel per
Vermehrungsvertrag bestimmt und gesucht wurde, so wurde bislang das
Löschkennzeichen des Artikelstamm nicht berücksichtigt. Dies Verhalten ist nun
abgeändert worden.  Des Weiteren ist die Itembox IB_KU_Vertrag_Nu um die
ArtikelId und Anerkid in der Returnliste erweitert worden.
Releasenote Kategorie:
Ticket: 739549[36878]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Owaage
Variante: Hofliste
Funktion/Report: Vermehrungsvertrag Auswahl
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36878, 739549

---

## Pfleger individuelle Artikelnummern aus der Belegflussmaske öffnen

Pfleger individuelle Artikelnummern aus der Belegflussmaske öffnen
In der Anwendung "Archiv Belegfluss"
[BF] auf der Variante "Meine Postfächer" gibt es auf der Maske
"Archivbelegfluss" eine neue Funktion mit dem Namen "Individuelle Artikelnummern
pflegen". Diese Funktion öffnet die Maske mit dem Namen "individuelle
Artikelnummern" mit dem Kunden und dem Artikel aus der Archivbelegflussmaske zu
öffnen. Dort kann man dann unter anderem die Mengeneinheiten schneller und
einfacher pflegen.
Releasenote Kategorie:
Ticket: 746956[37055]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Meine Postfächer
Funktion/Report: Individuelle Artikelnummern
pflegen
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37055, 746956

---

## UserJpl OnsSaveValid

UserJpl OnsSaveValid
Es ist jetzt auch möglich, bei der Maskensteuerung
durch den Anwender bei Masken mit Stammdateninterface auch eine Prüfung
einzubauen, ob überhaupt gespeichert werden darf. Dies auszuführende Funktion
trägt man unter "OnSaveValid" im Dialog für die Tabulatoren-Reihenfolge
ein. HINWEIS: Bei Pflegern, die bereits in der Valid speichern ist ein
Abbruch nicht mehr möglich
Releasenote Kategorie:
Ticket: 0[37364]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37364, 0

---

## Stammdatenpfleger Tastenbelegung Shortcut

Stammdatenpfleger Tastenbelegung Shortcut
Artikelstamm-Pfleger doppelte Tastenbelegung entfernt.
Textzeilen haben nun den Tastaturshortcut Strg+F5
Releasenote Kategorie:
Ticket: 748785[37815]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Artikelstamm
Variante: Artikelstamm
Funktion/Report: Ändern F5
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37815, 748785

---

## Dokumentenverwaltung - Hinzufügen von Dokumenten über [F8] Neu

Dokumentenverwaltung - Hinzufügen von Dokumenten über [F8] Neu
Im Archiv wurde der letzte Pfad für das Hinzufügen
neuer Dokumente (F8) nach dem Schließen der Maske nicht gespeichert. Der Pfleger
wurde so angepasst, dass der Pfad nun auch nach Verlassen der Maske gespeichert
bleibt und beim nächsten Hinzufügen eines Dokumentes über (F8) Neu vorgeschlagen
wird. Beim Speichern des Datensatzes wird die Maske nun wieder geschlossen.
Releasenote Kategorie:
Ticket: 750167[38271]
Version: 9.0.2502.7
Datum:
Anwendung: Dokumentenverwaltung
Variante: -
Funktion/Report: Neu
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38271, 750167

---

## AnyBill Mengeneinheiten

AnyBill Mengeneinheiten
Zur Übertragung an AnyBill müssen die Mengeneinheiten
umgeschlüsselt werden. Neu hinzugekommen sind die AnyBill-Mengeneinheiten m², m³
und KWh. Unbekannte Mengeneinheiten werden stets nur als C64 (Stück) übertragen.
Einen Hinweis gibt es ggf. ins Fehlerprotokoll.
Releasenote Kategorie:
Ticket: 751140[38495]
Version: 9.0.2502.8
Datum:
Anwendung: Mengeneinheiten [ME]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.8, 38495, 751140

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

## Druckerstamm Löschen

Druckerstamm Löschen
Beim Löschen im Druckerstamm wurde das Ergebnis der
Abfrage nicht korrekt ausgewertet. Dieses Problem wurde beseitigt.
Releasenote Kategorie:
Ticket: 752756[39135]
Version: 9.0.2502.9
Datum:
Anwendung: DRST
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39135, 752756

---

## Anlagenbuchhaltung (EPA ANLAGENKARTEI)

Anlagenbuchhaltung (EPA
ANLAGENKARTEI)
Bezeichnung
Standardwert
Erklärung
Stornierte/gelöschte Zeilen
      anzeigen?
Ja
Normalerweise werden gelöschte
      Zeilen weiterhin grau hinterlegt angezeigt. Man kann mit diesem Schalter
      diese Zeilen ausblenden. Auf dem Stammblatt erscheinen sie jedoch
      ungeachtet dieser Einstellung.

---

## Anschriftstamm (EPA ANSCHRIFTEN)

Anschriftstamm (EPA ANSCHRIFTEN)
Bezeichnung
Standardwert
Erklärung
Beim
      Speichern eines Interessenten den Kundenpfleger aufrufen
Ja
Kundennummer eines Musterkunden für
      neue Interessenten
Merkmal 1/2
      Tabkartenbezeichnung
Merkmal 3/4
      Tabkartenbezeichnung
freies Merkmal
      Tabkartenbezeichnung
Überschrift Merkmal 1
Überschrift Merkmal 2
Überschrift Merkmal 3
Überschrift Merkmal 4
Überschrift Daten
Überschrift freies
      Merkmal
Hauptadresse verliert Merkmal, wenn
      für mind. einen Ansprechpartner hinterlegt
Nein
Soll
      die Registerkarte Allgemein versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Zusätze versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Merkmale 1/2 versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Merkmale 3/4 versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte freies Merkmal versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Homepage versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Personendaten versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht
Soll
      die Registerkarte Notizen versteckt werden?
Nein
Registerkarte anzeigen oder
      nicht

---

## Artikelverpackung (EPA ARTIKELVERPACKUNG)

Artikelverpackung (EPA
ARTIKELVERPACKUNG)
Bezeichnung
Standardwert
Erklärung
Name
      des Makros zur individuellen Feldbearbeitung

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

## Bankenstamm (EPA BANKSTAM)

Bankenstamm (EPA BANKSTAM)
Bezeichnung
Standardwert
Erklärung
Bankleitzahl auf Eindeutigkeit
      prüfen?
Fehler
Die
      Bankleitzahl ist in Deutschland ein eindeutiges Kriterium und wird daher
      geprüft. Pflegt man jedoch auch Banken aus dem Ausland, so können durchaus
      Bankleitzahlen doppelt vorkommen. Die Prüfung lässt sich hier
      abschalten.

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

## Feldbesichtigung (EPA BTFELDBE)

Feldbesichtigung (EPA BTFELDBE)
Bezeichnung
Standardwert
Erklärung
Soll
      die private Prozedur p_PartieArtikelAuto aufgerufen werden ?
Nein

---

## Vermehrungsvertrag (EPA BTVERMV)

Vermehrungsvertrag (EPA BTVERMV)
Bezeichnung
Standardwert
Erklärung
Teil
      der Artikelnummer
%
Hier kann
      ein konstanter Teil der Artikelnummer angegeben werden, wenn alle für
      Vermehrungsverträge heranzuziehende Artikelnummern diesen enthalten.
      Beispiele:
VM% - Artikelnummer beginnt mit `VM´,
%VM - Artikelnummer
      endet mit `VM´,
%VM% - Artikelnummer enthält `VM´
Eingabe Aussaatmonat prüfen, nur im
      Pfleger vorhandene Aussaattermine zulassen
Ja
Lagerabfrage aktiv
Nein
Vorbelegung Lager als in
      (.,.,.,...), leer VKONS
Für die
      Auswahl der Artikel, Sorten und Kategorien kann eine Liste von
      Lagernummern angegeben werden. Wird hier nichts eingetragen, so wird die
      in den Vorgangskonstanten gesetzte Lagernummer herangezogen.
oberste Vermehrernummer
399999
unterste Vermehrernummer
300000
Nur
      Sorte/Kategorie erlaubt, ohne Artikel
Nein
Nein: Es
      werden nur Sorten und Kategorien zugelassen, für die bereits Artikel in
      den unter ‚Vorbelegung Lager als …‘ angegebenen Lägern
      existieren.
Ja: Es
      werden alle Sorten und Kategorien zugelassen, auch wenn noch keine Artikel
      dafür gefunden werden. Im letzteren Fall bleibt die Artikelnummer leer.
      Artikel sind dann gegebenenfalls später zu erfassen und zuzuordnen.
      Solange noch keine Artikelnummer angegeben ist, kann keine Schlagzuordnung
      vorgenommen werden.
Sorte/Kategorie änderbar
Nein
Pro
      Schlag mehrere Sorten zulassen!
Nein
VO
      und Aufbereiterfeld aktiv
Nein
Aktuelles Jahr als Erntejahr
      verwenden, sonst Geschäftsjahr.
Ja
Ist der
      Parameter auf Ja gesetzt, wird das Erntejahr standardmäßig mit dem
      aktuellen Jahr vorbelegt (bisheriger Standard).
Ist der
      Parameter auf Nein gesetzt, wird das Erntejahr mit dem Geschäftsjahr
      vorbelegt.

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

## Artikelstamm (EPA DHARTST)

Artikelstamm (EPA DHARTST)
Bezeichnung
Standardwert
Erklärung
Länge EAN-Code ( 0 = ohne Prüfung
      )
0

---

## Pflege der Kostenstellen (EPA KOSTSTAM)

Pflege der Kostenstellen (EPA KOSTSTAM)
Bezeichnung
Standardwert
Erklärung
Itembox für externe
      Auswertungsposition 1
Für die Externen
      Auswertungspositionen lassen sich Itemboxen auf eigene Stammdaten
      hinterlegen.
Bezeichnungsfeld für ext.
      Auswertungsposition 1
Hier muss man angeben, wie
      das Bezeichnungsfeld in der Itembox heißt. Z.B. würde bei der Itembox
      IB_LAGERSTAMM das Bezeichnungsfeld „LagerBezeich“ heißen.
Label für externe
      Auswertungsposition 1
Hier kann man angeben, was
      als Text vor dem Eingabefeld der externen Auswertungsposition stehen soll
      ( z.B. Lager )
Itembox für externe
      Auswertungsposition 2
S.o.
Bezeichnungsfeld für ext.
      Auswertungsposition 2
S.o.
Label für externe
      Auswertungsposition 2
S.o.
Itembox für externe
      Auswertungsposition 3
S.o.
Bezeichnungsfeld für ext.
      Auswertungsposition 3
S.o.
Label für externe
      Auswertungsposition 3
S.o.

---

## Kostenträger (EPA KSTRSTAM)

Kostenträger (EPA KSTRSTAM)
Bezeichnung
Standardwert
Erklärung
Itembox zur externer AWPOS
      1
Für
      die Externen Auswertungspositionen lassen sich Itemboxen auf eigene
      Stammdaten hinterlegen.
Bezeichnungsfeld der Itembox
      AWPOS1
Hier
      muss man angeben, wie das Bezeichnungsfeld in der Itembox heißt. Z.B.
      würde bei der Itembox IB_LAGERSTAMM das Bezeichnungsfeld
      „Lagerbezeichnung“ heißen.
Label zur externer AWPOS
      1
Hier
      kann man angeben, was als Text vor dem Eingabefeld der externen
      Auswertungsposition stehen soll ( z.B. Lager )
Itembox zur externer AWPOS
      2
S.o.
Bezeichnungsfeld der Itembox
      AWPOS2
S.o.
Label zur externer AWPOS
      2
S.o.
Itembox zur externer AWPOS
      3
S.o.
Bezeichnungsfeld der Itembox
      AWPOS3
S.o.
Label zur externer AWPOS
      3
S.o.

---

## Kontraktstamm (EPA KTRSTAM2)

Kontraktstamm (EPA KTRSTAM2)
Bezeichnung
Standardwert
Erklärung
Vorbelegung, ob Artikel
      Zu-/Abschläge erlaubt sind
Nein
Vorbelegung, ob Artikel
      lagerspezifisch sind
Nein

---

## Kontraktstamm (EPA KTRSTAM)

Kontraktstamm (EPA KTRSTAM)
Bezeichnung
Standardwert
Erklärung
Startreiter im
      Änderungsmodus
--
Hier
      kann die Registerkarte festgelegt werden, auf der man im Änderungsmodus
      steht.
Vorbelegung, ob Artikel
      Zu-/Abschläge erlaubt sind
Nein
Hier
      kann die Vorbelegung für das Feld „Artikel-Zu-/Ab“ festgelegt
      werden.
Vorbelegung Ausgangsrechnung oder
      Ausgangsgutschrift
Ausgangsrechnung
Dieser Einrichterparameter steht im
      Zusammenhang mit Einrichterparameter „
Umwandlung nach
      Fremdware/Fremdlager
“.
Mit
      diesem Parameter wird festgelegt, was für ein Beleg bei der Umwandlung von
      einem Verkaufskontrakt erzeugt wird.
Vorbelegung Eingangsrechnung oder
      Eingangsgutschrift
Eingangsrechnung
Dieser Einrichterparameter steht im
      Zusammenhang mit Einrichterparameter „
Umwandlung nach
      Fremdware/Fremdlager
“.
Mit
      diesem Parameter wird festgelegt, was für ein Beleg bei der Umwandlung von
      einem Einkaufskontrakt erzeugt wird.
Vorbelegung für die Abbuchungsmengen
      bei Rohwarekontrakten
---
Hier
      kann die Vorbelegung für das Feld Abbuchungsmenge angegeben werden. Bei 0
      (---) wird der Standardwert „Netto“ verwendet.
Bausteine im Korrekturmodus
      automatisch auflösen?
Nein
Name
      der Funktion für die Bezeichnung
Hier
      kann eine Funktion hinterlegt werden, in der die Bezeichnung des
      Kontraktes geändert werden kann.
Übergabeparameter sind
-
Kontraktklasse
-
Kontraktunterklasse
-
Kundennummer
-
Kontraktnummer
-
Kontrakt ID
Sollen die Kontraktdatumfelder auf
      dem Reiter Konditionen angezeigt werden?
Nein
Hiermit kann festgelegt werde auf
      welcher Registerkarte sich die Kontraktdatumsfelder befinden.
Dispokennzeichen
      Feldstatus
aktiv
Benutzer des
      Hedgeaccounts
TESTACC
Wird
      benötigt für VAX
Hedge Felder anzeigen
Nein
Sollen die Hedge-relevanten Felder
      auf der Kontraktmaske angezeigt werden.
Server - IP wohin der
[...]


---

## Ladeträgerbuchungen (EPA LVS_SCHWUNDARTIKEL)

Ladeträgerbuchungen (EPA LVS_SCHWUNDARTIKEL)
Bezeichnung
Standardwert
Erklärung
Schwundkonto für
      Partieausbuchungen
Hier
      wird die Artikelnummer des Artikels für Schwundbuchengen o.a.
      Leermeldungen angegeben. Diese Artikelnummer muss natürlich auch angelegt
      worden sein. Ob der EPA Verwendung findet oder nicht, wird im
      Steuerparameter 803 geregelt. Wenn dort keine aktiven oder passenden
      Schwundkonten gefunden werden wird der Artikel aus dem EPA
      ermittelt.

---

## Oberkundenzuweissung(EPA Rechnungenverschieben)

Oberkundenzuweissung(EPA Rechnungenverschieben)
Bezeichnung
Standardwert
Erklärung
Artikelnummer
Auf
      diesen Artikel wird der Zu-Abschlag für den Gruppenrabat
      gebucht.
Prozedur die Informationen des
      Lieferscheins als Textbaustein bereitstellt
GetLieferTexte
Mit
      der Prozedur kann das Aussehen der Liefertexte beeinflusst werden. Im
      Standard wird die Versanadresse genommen. Ist diese nicht vorhanden so
      wird die Adresse des Kunden verwendet. Die Ausgabe erfolgt
      zeilenweise.

---

## Partiestammdaten (EPA PVPARTIE)

Partiestammdaten (EPA PVPARTIE)
Bezeichnung
Standardwert
Erklärung
Partiebis-datum
01.01.2000

---

## Trockengewicht (EPA SAATTROCKNUNG)

Trockengewicht (EPA SAATTROCKNUNG)
Bezeichnung
Standardwert
Erklärung
Addon Feldname

---

## Sorten-/Kundenänderung (EPA RWBKORREKTUR)

Sorten-/Kundenänderung (EPA
RWBKORREKTUR)
Bezeichnung
Standardwert
Erklärung
Rohwarebeleg danach zur normalen
      Korrektur öffnen
Nein
Artikelauswahl auf Rohwarengruppe
      des Beleges beschränkt
Ja
Vorgangsunterklasse des
      Zwischenbeleges
0

---

## Sprachtexte (EPA SPRACHTEXTPFLEGER)

Sprachtexte (EPA SPRACHTEXTPFLEGER)
Bezeichnung
Standardwert
Erklärung
zweite anzuzeigende
      Sprache
0
Es
      können gleichzeitig mehrere Sprechen angezeigt werden. Sprache 0 ist immer
      Deutsch. Wenn man nun für eine weitere Sprache (z.B. Polnisch) die Daten
      erfassen will, so kann es hilfreich sein den Text zusätzlich noch in
      Englisch oder einer andere Sprache zu sehen
dritte anzuzeigende
      Sprache
0
S.o.

---

## Sinfosdaten (EPA SINFOS)

Sinfosdaten (EPA SINFOS)
Bezeichnung
Standardwert
Erklärung
Prozedurname der Datensatzanlage
      (Par=ArtiStammId)
sinfos
Der
      Name der Prozedur, welche beim Laden eines Datensatzes aufgerufen
      wird.
Sekundärschlüsselgruppe für
      EAN-Ermittlung
2
Die
      Gruppe des Sekundärschlüssels mit dem die EAN ermittelt wird.
Sekundärschlüsselzeile für
      EAN-Ermittlung
2
Die
      Zeile des Sekundärschlüssels mit dem die EAN ermittelt wird.
Lagernummer für Prüfung der
      Artikelsperre
2
Die
      Lagernummer mit der geprüft wird, ob der Artikel dort eine Sperre
      hat.
Artikeltext Variantennummer
      1
1
Nummer der Variante aus dem die
      erste Artikeltextzeile geladen werden soll.
Artikeltext Zeile 1
1
Nummer der Zeile aus der die erste
      Artikeltextzeile gelesen werden soll.
Artikeltext Variantennummer
      2
1
Nummer der Variante aus dem die
      zweite Artikeltextzeile geladen werden soll.
Artikeltext Zeile 2
2
Nummer der Zeile aus der die zweite
      Artikeltextzeile gelesen werden soll.

---

## MaskenTitel (EPA SVWARE)

MaskenTitel
(EPA SVWARE)
Bezeichnung
Standardwert
Erklärung
Bildschirm für Addon
      aufbauen
Nein
Artikel/Artikelstamm immer im
      Zusammenhang anlegen
Ja
Bei
      Baustelle nur Baustellenartikel in IB anzeigen
Nein
Bei
      NEIN steigt man in die Itembox „Nach Nummern“ intern
      „IB_ARTIKEL_BAUSTELLE“ ein.
Bei JA steigt man in die Itembox „nur
      Objektartikel“ intern „IB_ARTIKEL_BAUSTELLE_LANGSAM“ ein.
Die Itembox
      „IB_ARTIKEL_BAUSTELLE_LANGSAM“ zeigt nur die Artikel an, welche in dem
      Objektstamm eingetragen wurden.
Beim
      Drücken von RETURN im Feld Menge wird in die nächste Spalte
      gesprungen
Nein
Folgezeilen sofort
      rekalkulieren
Ja
Gebindemaske ohne Abfrage
      weiterschalten
Ja
Geschäftsart abfragen
Nein
Label Geschäftsart
Gesch.Art
Länge des Anzeigefeldes
      Geschäftsart
10
Stückliste: F3-Auswahl ab 1
      Stückliste
Nein
Stückliste: F3-Auswahl ESC =
      keine
Nein
Die
      Artikelnummer wird im NEU Fall IMMER mit dem letzten Artikel
      vorbelegt
Nein
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein
Nachkommastellen der
      Warenmenge(höchstens 4)
3
Merkmalsleisten
      Neuartikelprozedur
Wird
      ein Artikel über die
Merkmalsleiste
neu angelegt, so
      wird bei gesetztem EPA (Prozedurname) diese Prozedur vor Aufruf der
      eigentlichen Artikelanlage gestartet. Signatur der Prozedur
      ist:
(
      ':ArtikelNummer$', :LagerNummer$ )
Gebinde ohne
      Folgeabfragen
Ja
Verschiebung der
      Warenerfassung
12
Preisänderungen verbieten, F3
      Auswahl ist aber erlaubt.
Nein
Auto.F3 im Preisfeld bei
      Korrektur
Ja
sofortige Preisfindung
      durchführen
Ja
Bei
      F9 Abschluss sofort in Belegabschluss
Nein
Zusatz 1 mit F3-Auswahl
Nein
Feldname für Zusatz1 in
      F3-Auswahl
Bezeichnung Zusatztext 1
Info
      1
Zusatztext 1 Länge
40
Vorbelegung Zusatz1
Zusatz 2 mit F3-Auswahl
Nein
Feldname für Zusatz2 in
      F3-Auswahl
Bezeichnung
[...]


---

## Artikeltext korrigieren (EPA SVWTEXT)

Artikeltext korrigieren (EPA SVWTEXT)
Bezeichnung
Standardwert
Erklärung
Eingabebreite

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

## Excel-Import

Excel-Import
Stammdatenpflege
Stammdatenpfleger
Excel-Import
oder Direktsprung
[EXCELI]
Dieses Modul bietet die Möglichkeit gesamte
Arbeitsblätter aus Excel-Dateien nach Referenz-ERP zu importieren. Dabei wird anhand
des Excel-Arbeitsblattes in Referenz-ERP eine Tabelle und eine Variante angelegt. Es
können .xlsx und .xlsm-Dateien importiert werden. Das Dateiformat .xls wird nur
noch in der 32Bit-Version unterstützt.
Für den Excel-Import ist keine Excel-Installation
notwendig.

---

## Stammdaten

Stammdaten
Hauptmenü
Filialsystem
Stammdaten

---

## Tourenplanung-Profil

Tourenpl
anung-Profil
Stammdatenpflege
Anschriften
Maps Tourenplanung Profil
[MTPP]
Die Tourenplanung stellt je nach Profil verschiedene
Ansichten bereit. Mit dem Aufruf dieses Profils werden diese beim Start bereits
aktiviert.
Im Pfleger MapsTourenPlanungProfil
[MTPP]
können die Parameter eingestellt
werden:
Maps Tourenplanung
      Profil
Feld
Bedeutung
Id
Laufende ID des Profils – diese ist
      wichtig für den Aufruf
Startadresse
Soll
      jede geplante Tour an einem bestimmten Punkt (z.b. dem eigenen Standort
      oder dem Auslieferungslager starten, so kann hier die Startadresse
      hinterlegt werden.
Startadresse verwenden
Wird
      hier „Ja“ angegeben, wird die o.a. Startadresse aus Start der Reise
      angegeben.
Start gleich Ziel
Soll
      die Rundreise auch am Ausgangspunkt enden, so muss diese Option gewählt
      werden.
Ziel
      festlegen
Soll
      eine Reise beim letzten gewählten Punkt enden unabhängig von den weiteren
      Streckenpunkten, so wird dies hier angegeben.
Beim
      Start optimieren
Ist
      „Ja“ gewählt, so werden beim Start die Wegpunkte zu der kürzesten zu
      ermittelnden Kette verbunden.
Nur
      Verteilung anzeigen
Wird
      hier „Ja“ angegeben, so wird keine Entfernungsermittlung eingeschaltet.
      Dies spart einen Aufruf des kostenpflichtigen Webservices von Google Maps.
      Es werden lediglich die Punkte auf der Karte als Verteilung angezeigt.
Geodaten ermitteln
Wenn
      „Ja“ angegeben ist, wird Referenz-ERP versuchen fehlende Geodaten beim Einlesen
      der Daten zu ermitteln. Dies kann u.U. Kosten verursachen.
Private Datenprozedur
Hier
      kann eine private Datenprozedur für den Druck-Report angegeben
      werden
Privater Report
Hier
      kann ein privater Report angegeben werden

---

## Artikelzusatzrelationen bei Kopie (SPA 1018)

Artikelzusatzrelationen bei Kopie (SPA 1018)
Es gibt zwei Anwendungsfälle für Trigger, die
Artikelzusatzrelationen wie ArtikelAddon vorbelegen, wenn ein Artikel angelegt
wird:
1.
Vorbelegung zum Zweck der Performance-Verbesserung – In diesem Fall existiert
stets ein Dummy-Datensatz zum Artikel, was die Suche von Artikeln mit bestimmten
Addon-Feldern beschleunigt, da kein LEFT OUTER JOIN notwendig ist.
2.
Intelligente Vorbelegung aufgrund kalkulierter Werte
Im Fall1 kann es sinnvoll sein, die Daten aus dem
Quell-Artikel zu überschreiben. In diesem Fall wird der Steuerparameter auf
„überschreiben“ gestellt.
Im Fall 2 sollen vermutlich die Daten des
Quell-Artikels nicht übernommen werden. In diesem Fall wird der Steuerparameter
auf „beibehalten“ gestellt.

---

## Artikel-Übernahme (HG-Artikel) zulässig(SPA 103)

Artikel-Übernahme (HG-Artikel) zulässig(SPA 103)

---

## Hausbanknummer für EPC-QRCODE (SPA 1079)

Hausbanknummer für EPC-QRCODE (SPA 1079)
Hier kann festgelegt werden, welche Hausbank bei der
Erzeugung eines EPC-QRCODEs im Fuß von Rechnungsformularen heranzuziehen ist.
Die Hausbank wird hier durch die Angabe der Hausbanknummer aus dem
Hausbankenstamm festgelegt. Bei Angabe der Nummer 0 wird die Hausbank mit der
niedrigsten Hausbanknummer herangezogen.

---

## Artikel-Übernahme (ZG-Artikel) zulässig(SPA 108)

Artikel-Übernahme (ZG-Artikel) zulässig(SPA 108)

---

## Artikel mehrfach in Partie erlaubt(SPA 1084)

Artikel mehrfach in Partie erlaubt(SPA 1084)
Der Steuerparameter legt fest, ob im
Partiestamm-Pflegemodul ein Artikel oder Artikelstamm mehreren Artikelposition
der Partie zugeordnet werden kann (Einstellung:
Ja
).
Bei der Einstellung
Nein
kann ein Artikel oder
Artikelstamm nur einer Artikelposition zugeordnet werden. Es ist dann auch nicht
möglich, einer Position einen Artikel zuzuordnen, dessen Artikelstamm bereits
einer anderen Position zugeordnet wurde und umgekehrt.

---

## Artikel-Tabellen-Übernahme (ZG) zulässig(SPA 109)

Artikel-Tabellen-Übernahme (ZG) zulässig(SPA 109)

---

## Folgeartikel automatisch erfassen (SPA 1133)

Folgeartikel
automatisch erfassen (SPA 1133)
Einstellung
Bedeutung
Ja
Aktiviert automatische Erfassung von
      Folgeartikeln in der Marktkasse außer Leergutartikel.
Nein
Keine automatische Erfassung von
      Folgeartikeln in der Marktkasse.

---

## Aut. Umbruch Artikeltext beim Drucken(SPA 144)

Aut. Umbruch Artikeltext beim Drucken(SPA 144)
Beim Ausdruck von Artikeltexten werden die Textzeilen
automatisch umgebrochen, wenn das Ausgabefeld im Vorgang eine geringere Länge in
der Zeile aufweist, als der erfasste.
Bei „Nein“ wird der Text abgeschnitten.
Die Erfassung erfolgt in den ersten beiden Fällen
zeilenweise. Ein Textumbruch kann bei Einstellung „ja“ mit der Eingabe von „\N“
forciert werden.
Bei der Einstellung „Ja, wie Erfassung“ wird ein
Zeilenumbruch bei der Erfassung in der Texteingabe erfasst.

---

## Vorgangstexte zwangsweise vor Hauptteil(SPA 146)

Vorgangstexte zwangsweise vor Hauptteil(SPA 146)
Bei „Ja“ werden Texte des Rechnungskopfes (Kommentar,
etc.) vor dem Einstieg in die Artikelpositionserfassung abgefragt.

---

## Artikel mit inkompatiblen Mengeneinheiten (SPA 153)

Artikel mit inkompatiblen Mengeneinheiten (SPA 153)
Mit diesem Steuerparameter kann festgelegt werden,
dass die Artikel eines Kontrakts unterschiedliche Mengeneinheiten haben können.
Dabei ist zu beachten, dass bestimmte
Auswertungen (z.B. mengenmäßiges Engagement) nicht sinnvoll sind.

---

## Automatische Verpackungs-/Bruttogewicht(SPA 158)

Automatische Verpackungs-/Bruttogewicht(SPA 158)

---

## Standard-Mengeneinheit Gewichte (0=ohne)(SPA 157)

Standard-Mengeneinheit Gewichte (0=ohne)(SPA 157)
Mit dieser Einstellung wird die Mengeneinheit des
Gewichtes eines Artikels vorbeleget.

---

## Anzahl-Ermittlung angebrochener Gebinde(SPA 189)

Anzahl-Ermittlung angebrochener Gebinde(SPA 189)
Standardmäßig wird ein angebrochenes Gebinde intern
mit 0 ausgegeben, so dass ein angebrochenes Gebinde als 0 Gebinde a x Einheiten
in der Gebindeinformation ausgewiesen wird

---

## Dienstleistungen nur als Wertartikel(SPA 197)

Dienstleistungen nur als Wertartikel(SPA 197)
egal = Dienstleistungsartikel werden nicht gesondert
behandelt.
nur = Dienstleistungsartikel können nur als
Wertartikel fakturiert werden
immer = Dienstleistungsartikel werden immer als
Wertartikel behandelt, man braucht nicht explizit die Funktion Wertartikel
aufrufen.

---

## Objekt(e) mit Dreifach-Rabatten(SPA 215)

Objekt(e) mit Dreifach-Rabatten(SPA 215)
Ja: Es können bis zu drei (multiplikative) Rabatte pro
Artikel, Warengruppe, etc. vergeben werden. Nein: Es kann pro Artikel,
Warengruppe, etc. eine Rabattgruppe vergeben werden.

---

## Rundungsstellen Mengenumrechnung(SPA 243)

Rundungsstellen Mengenumrechnung(SPA 243)
Diese Größe wird als Vorbelegung  sowohl bei der
Erfassung von normalen Mengeneinheiten für das Feld „Rundung bei Umrechnung“ als
auch für Gebinde für das Feld „Rundungsstellen bei Umrechnung Menge / Gebinde“
genommen.

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

## Bezugsgröße zur Mengenbest. Folgeartikel(SPA 385)

Bezugsgröße zur Mengenbest. Folgeartikel(SPA 385)
Hier wird entschieden, ob bei der Mengenbestimmung des
Folgeartikels die Menge oder die Gebindeanzahl der führenden Warenpositionen
herangezogen werden soll.
Wert
Bedeutung
Je
      Menge
Bei
      Hauptartikeln mit Gebinde wird die Gesamtmenge als Bezugsgröße für die
      Mengenberechnung des Folgeartikels verwendet.
Je
      Gebinde
Bei
      Hauptartikeln mit Gebinde wird die Gebindemenge als Bezugsgröße für die
      Mengenberechnung des Folgeartikels verwendet.
Bei Folgeartikeln in Lagerumbuchungen wird immer die
Gesamtmenge des Hauptartikels als Bezugsgröße für die Mengenberechnung der
Folgeartikel verwendet, da Lagerumbuchungen keine Gebinde unterstützen.

---

## Vorbelegung Artikelgültigkeit: BisDatum(SPA 388)

Vorbelegung Artikelgültigkeit: BisDatum(SPA 388)
Vorbelegung der Gültigkeitsdauer von Artikeln: - bis
31.12.2099 - bis 31.12 laufendes Kalenderjahr - Beginn des laufenden
Geschäftsjahres

---

## Vorbelegung Artikelgültigkeit: AbDatum(SPA 387)

Vorbelegung Artikelgültigkeit: AbDatum(SPA 387)
Vorbelegung des Beginns der Gültigkeitsdauer von
Artikeln: - ab 01.01.1901 - ab 01.01. laufendes Kalenderjahr - Beginn des
laufenden Geschäftsjahres

---

## Menge der Folgeartikel korrigierbar(SPA 418)

Menge der Folgeartikel korrigierbar(SPA 418)
Wert
Bedeutung
Ja
Die
      Menge in einem Folgeartikel kann abgeändert werden.
Nein
Die
      Menge in einem Folgeartikel kann nicht abgeändert werden.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Folgeartikel aus Liste löschbar(SPA 419)

Folgeartikel aus Liste löschbar(SPA 419)
Steuert die Möglichkeit aus Folgeartikel-Listen
einzelne Positionen entfernen zu können.
Wert
Bedeutung
Ja
Folgeartikel können in der
      Positionsübersicht gelöscht werden.
Nein
Folgeartikel können in der
      Positionsübersicht nicht gelöscht werden.
Nur
      in n:m Folgelisten
Folgeartikel dürfen in der
      Positionsübersicht nur gelöscht werden, wenn „einen“ als Folgetyp im
      Hauptartikel eingestellt ist.

---

## Preise im Preisanzeigefenster(SPA 463)

Preise im Preisanzeigefenster(SPA 463)
Dieser Parameter gibt an, welche Preise auf der
Hauptseite des Artikelpflegers sichtbar sind.

---

## Mengeneinheit aus Ordersatz ?(SPA 467)

Mengeneinheit aus Ordersatz ?(SPA
467)
Soll beim Ordersatz die Mengeneinheit übernommen
werden?

---

## Gewichtsberechnung komplett(SPA 469)

Gewichtsberechnung komplett(SPA 469)
Bei Einstellung „Ja“ wird die Berechnung des Gewichtes
in den Warenposition mit kompletter Umrechnung der Menge in die zugehörige
Grundmengeneinheit durchgeführt. Bei „Nein“ wird lediglich die erfasste Menge
mit dem Gewicht aus dem Artikelstamm multipliziert.

---

## Soll EKZ-Nummer geprüft werden ?(SPA 485)

Soll EKZ-Nummer geprüft werden ?(SPA 485)
Hier wird eingestellt, ob während der Artikelerfassung
überprüft werden soll ob für den gewählten Artikel eine EKZ-Nummer <> 0
hinterlegt ist.
Wenn die Überprüfung auf „Ja“ gesetzt wurde, werden
Artikel ohne Erlöskennziffer schon bei der Erfassung abgewiesen.

---

## Eindeutige EAN-Nummer im Artikel ?(SPA 486)

Eindeutige EAN-Nummer im Artikel ?(SPA 486)
Hier kann eingestellt werden, ob während der
Artikelerfassung die Eindeutigkeit der erfassten EAN-Nummer überprüft werden
soll.

---

## Datum-Bis-Vorbelegung in Monaten(SPA 528)

Datum-Bis-Vorbelegung in Monaten(SPA 528)
Für Partiestamm: Das BIS-Datum der Partie um n-Monate
vorbelegen. Ein Beispiel: Das VON-Datum ist der 01.06.2002. Die Vorbelegung der
Monate ist auf 12 gesetzt. Also wird das BIS-Datum vorbelegt auf den
01.06.2003.
Gültiger Bereich: 0 bis 99 Monate.

---

## Länge Artikeltext(SPA 537)

Länge Artikeltext(SPA 537)
Hier wird die maximale Länge von Artikeltexten pro
Zeile festgelegt. Grundsätzlich sind nicht mehr als 100 Zeichen pro Zeile
möglich.

---

## Folgeartikelmechanismus bei Kasse (SPA 533)

Folgeartikelmechanismus bei Kasse (SPA 533)
Einstellungen
Nicht aktiv
In
      der Marktkasse wird die Hinweislampe „Leergut“ nicht angezeigt. Leergut
      kann optional über die Taste Leergut hinzugefügt werden.
In
      der Tresenkasse werden Folgeartikel nicht angezeigt und können auch nicht
      gezogen werden.
Nur
      bei Tresen- oder Marktkasse
In
      der Marktkasse wird die Hinweislampe „Leergut“ angezeigt. Leergut muss
      über die Taste Leergut hinzugefügt werden.
In
      der Tresenkasse wird die Hinweislampe „Folgeartikel“ angezeigt, wenn
      Folgeartikel für den Hauptartikel eingerichtet sind. Diese werden analog
      der Lieferschein oder Rechnungspositionsbearbeitung behandelt.

---

## Ordersatz-Artikel: Lager beibehalten(SPA 561)

Ordersatz-Artikel: Lager beibehalten(SPA 561)
Bei „Ja“ wird das Lager des Ordersatzes übernommen.
Bei „Nein“ wird nur die Artikelnummer übernommen, das Lager wird durch die
Lagernummerneinstellung des aktuellen Beleges ersetzt.

---

## Ordersatz: Artikeltext übernehmen(SPA 562)

Ordersatz: Artikeltext übernehmen(SPA 562)
Bei „Ja“ wird der Artikeltext aus dem Ordersatz
übernommen, bei „Nein“ wird der Artikeltext so wie im Artikel hinterlegt
gezogen.

---

## Partiegruppe bei PartieAuswahl(SPA 571)

Partiegruppe bei PartieAuswahl(SPA 571)
Hier wird festgelegt, wie die Partiegrupe des Artikels
bei der Auswahl von Partien berücksichtigt wird.
0 = egal: Die Partiegruppe wird nicht
geprüft
1 = eigene oder 0: Nur Partien mit der Gruppe 0
oder  zum Artikel passender Gruppe sind zulässig
2 = passend: strikte Prüfung ob Partiegruppe im
Artikel mit der  Gruppe in der Partie übereinstimmt.

---

## Artikelverpackung 1-stuf. Gebinde(SPA 591)

Artikelverpackung 1-stuf. Gebinde(SPA 591)
Vorbelegung der Gebindenummern in einer
Artikelverpackung, wenn ein einstufiges Gebinde erforderlich ist.

---

## Artikelverpackung aktiv(SPA 590)

Artikelverpackung aktiv(SPA 590)
Bei „Ja“ werden Verpackungsinformationen
ausgewertet

---

## Artikelverpackung 2-stuf. Gebinde(SPA 592)

Artikelverpackung 2-stuf. Gebinde(SPA 592)
Vorbelegung der Gebindenummern in einer
Artikelverpackung, wenn ein zweistufiges Gebinde erforderlich ist.

---

## Artikelverpackung 3-stuf. Gebinde(SPA 593)

Artikelverpackung 3-stuf. Gebinde(SPA 593)
Vorbelegung der Gebindenummern in einer
Artikelverpackung, wenn ein dreistufiges Gebinde erforderlich ist.

---

## Automatische Artikel-Neuanlage bei Warenposition(SPA 61)

Automatische Artikel-Neuanlage bei Warenposition(SPA 61)
Diese Einstellung wird nicht mehr unterstützt.

---

## Artikelverpackung Gebinde immer änderbar(SPA 639)

Artikelverpackung Gebinde immer änderbar(SPA 639)
Arbeitet man mit dem Artikelverpackungssystem, so
lassen sich Gebindefaktoren nur ändern, wenn die Gebindeanzahl = 1 ist.
Bei „Ja“ kann man die Gebindefaktoren immer ändern. ACHTUNG: die mit der
Artikelverpackung einhergehende automatische Palettenverteilung funktioniert
dann nicht korrekt.

---

## EAN8 Code wird als solcher Erkannt, auch wenn dieser nicht gültig ist. (SPA 727)

EAN8 Cod
e wird als solcher Erkannt, auch wenn dieser
nicht gültig ist. (SPA 727)
Muss eingestellt werden, wenn ein eigener EAN 8 Codes
gescannt werden sollen, der keine korrekte Prüfkennziffer hat. Oder wenn der
Windows Scanner benutzt wird, da dieser keine Scaneinheit enthält.

---

## EAN13 Code wird als solcher Erkannt, auch wenn dieser nicht gültig ist. (SPA 728)

EAN13
Code wird als solcher Erkannt, auch wenn dieser
nicht gültig ist. (SPA 728)
Muss eingestellt werden, wenn ein eigener EAN 13 Codes
gescannt werden sollen, der keine korrekte Prüfkennziffer hat. Oder wenn der
Windows Scanner benutzt wird, da dieser keine Scaneinheit enthält.

---

## EAN13 Erkennung in der Scannersoftware ausschalten. (SPA 730)

EAN13 Erkennung in der Scannersoftware ausschalten. (SPA 730)
Hiermit kann die EAN 13 Erkennung im AeinsCE
ausgestellt werden. Gescannte EAN 13 Codes werden mit einer -1 an die Datenbank
übertragen und zurückgewiesen.

---

## EAN128 Erkennung in der Scannersoftware ausschalten.(SPA 729)

EAN128 Erkennung in der Scannersoftware ausschalten.(SPA 729)
Hiermit kann die EAN 128 Erkennung im AeinsCE
ausgestellt werden. Gescannte EAN 128 Codes werden mit einer -1 an die Datenbank
übertragen und zurückgewiesen.

---

## EAN8 Erkennung in der Scannersoftware ausschalten. (SPA 731)

EAN8 Erkennung in der Scannersoftware ausschalten. (SPA 731)
Hiermit kann die EAN 8 Erkennung im AeinsCE
ausgestellt werden. Gescannte EAN 8 Codes werden mit einer -1 an die Datenbank
übertragen und zurückgewiesen.

---

## Länge der Menge.(SPA 738)

Länge der Menge.(SPA 738)
Gibt die maximale Anzahl der Zeichen für die Menge im
Scanner an. Damit bei der Eingabe von EAN Codes, die mit der Eingabetaste
übertragen werden, nicht als Menge mit der AI -30 in der Datenbank
auftauchen.  Die  Standard  länge für die Menge ist 5.

---

## Standardgebindefaktoren auf Artikelmaske (SPA 764)

Standardgebindefaktoren auf Artikelmaske (SPA 764)
Sind in der dem Artikelstamm eines Artikels
zugeordneten Mengeneinheitsgruppe die Mengeneinheiten für Verkauf und Einkauf
identisch und vom Typ Gebinde, so bewirkt die Einstellung ‚Ja‘ dieses
Steuerparameters, dass die Gebinde-Faktoren jener Gebinde-Mengeneinheit auf der
Artikel-Bearbeitungsmaske angezeigt und, in Abhängigkeit von der im
Gebinde-Stamm eingestellten Herkunft der Faktoren,  auch erfasst bzw.
geändert werden können. Ist die Faktor-Herkunft mit ‚aus Mengeneinheit‘
angegeben, so können diese hier nicht geändert werden. Bei der Einstellung ‚aus
Artikelstamm‘ ist eine Erfassung nur bei der Anlage eines neuen
Artikelstammsatzes möglich. Bei eingestellter Variante ‚aus dem Artikel‘ können
die Faktoren hier auch im Änderungs-Modus bearbeitet werden. Die hier angegeben
Faktoren gelten dann für alle Bereiche (Einkauf, Verkauf und Lager) und werden
entsprechend in den Relationen für Artikel-Gebinde-Faktoren bzw.
Artikelstamm-Gebinde-Faktoren eingetragen.

---

## Itembox Artikel (SPA 766)

Itembox Artikel (SPA 766)
Hier kann eine private Itembox für die Artikel Auswahl
in für die eigene Scanner-Maske hinterlegt werden.

---

## Ratierliche Berechnung in Lagermengeneinheit des ersten Artikels (SPA 815)

Ratierliche Berechnung in Lagermengeneinheit des ersten
Artikels (SPA 815)
Die Mengeneinheit der verteilten Mengen ist
standardmäßig die Mengeneinheit des Kontrakts. Mit diesem Steuerparameter kann
eingestellt werden, dass die Berechnung der Lagermengeneinheit auf Basis des
ersten Artikels erfolgen soll.
Dabei muss beachtet werden, dass die Protokolle der
ratierlichen Berechnung erneuert werden müssen.

---

## Marktkasse: Eingabe bis n Stellen ist Menge statt Artikelnummer(SPA 834)

Marktkasse: Eingabe bis n Stellen ist Menge statt
Artikelnummer(SPA 834)
Bei einem Wert größer 0 wird bei der Marktkasse eine
Mengenautomatik im Artikelnummernfeld aktiviert. Gibt man maximal die in diesem
Steuerungsparameter festgelegten Zeichen ein, so wird die Eingabe als Menge
angesehen sofern nur numerischen Zeichen verwendet werden (0 – 9, + - und
Komma). Die ermittelte Menge wird ins Mengenfeld übertragen. Das Artikelfeld
wird anschließend gelöscht. Diese Automatik ist dann sinnvoll, wenn die
Artikelnummern eine Mindestlänge von n+1 Zeichen aufweisen.

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

## Artikel-Erstübernahme (Faktura) zulässig(SPA 97)

Artikel-Erstübernahme (Faktura) zulässig(SPA 97)

---

## ADR-GefahrgutMakro-Eigenschaften (SPA976)

ADR-GefahrgutMakro-Eigenschaften (SPA976)
Hier können die Eigenschaften des zu verwendenden
ADR-GefahrgutMakros hinterlegt werden, welches den Anwender in der
Gefahrgutmaske des Artikelstammes unterstützen soll.
•
MakroName = Name des zu verwendenden Makros
•
MakroMethode = Name der zu verwendenden Makro 2.0 Methode
Wird
KEINE MakroMethode
angegeben, geht die
Anwendung davon aus, dass es sich beim angegebenen Makronamen um ein
PASCAL-Makro
handelt. Ist diese Eigenschaft angegeben, wird von einem
Makro 2.0 ausgegangen.

---

## Artikel-Rücksetzung zulässig(SPA 98)

Artikel-Rücksetzung zulässig(SPA 98)

---

## Rollen für Pflegerstamm deaktivieren (SPA 985)

Rollen für Pflegerstamm deaktivieren (SPA 985)
Um Kontext-Entscheidungen zu unterstützen ist es
möglich hier die rein technische Rollenüberprüfung zu deaktivieren.

---

## Setup Filialsystem

Setup Filialsystem
Hauptmenü
Filialsystem
Stammdaten
Setup Filialsystem
oder Direktsprung
[SFS]
Die hier vorliegende Auswahlliste zeigt die
vorhandenen
Publikationen
,
deren
Artikel
und
Subskribenten
an. Ebenso ob eine
Subskription
gestartet ist oder nicht.

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Stammdatenanpassungen

Stammdatenanpassungen

---

## Abbruch einer Funktion, Rückkehr aus einem Menü

Abbruch einer Funktion, Rückkehr aus einem Menü
Die Taste
ESC
erlaubt es auf Menüebene jederzeit, auf
die Ebene zurück zu gelangen, von der diese Funktion aufgerufen wurde.
Auf
Funktionsebene, z.B. Stammdatenerfassung, bewirkt
ESC
das Überspringen weiterer Abfragefelder
mit der Möglichkeit, die Erfassung anschließend komplett abzubrechen oder die
Daten der Standardvorbelegung zu speichern.

---

## Abschreibungen, AfA

Abschreibungen, AfA
Abschreibungen kommen über das Erstellen von
Abschreibungsvorschlägen
und die
Freigabe dieser in den Anlagenstamm. Dabei wird automatisch ein Beleg in der
Finanzbuchhaltung erstellt. Ob der Beleg aus den handels- oder steuerrechtlich
geführten Daten erzeugt wird, wird im
Firmenstamm
festgelegt. Stornieren der
AfA-Zeilen des Anlagegutes führt dazu, dass zu diesem Belege automatisch ein
Stornobeleg erstellt wird.
Man kann AfA Zeilen jedoch auch manuell erfassen, wenn
das Anlagegut die AfA-Methode manuell hat oder bei der Neuerfassung eines
Anlagegutes. Die Erfassung der AfA bei Neuerfassung dient dazu, bei
Systemwechsel bestehende bereits teilabgeschrieben Güter so erfassen zu können,
dass sowohl die Anschaffungs- und Herstellungskosten als auch der Restbuchwert
stimmen und somit die folgenden Abschreibungen die richtigen Werte ausweisen
können.
Manuell erfasste AfA-Zeilen lassen sich - mit Ausnahme
des Textes und des Datums - nachträglich nicht ändern. Für neu erfasste Zeilen
wir eine Buchung in der FiBu erstellt. Dazu werden Nummernkreis, Belegdatum und
Fälligkeit und das AfA-Konto – vorbelegt aus dem Anlagenstamm - in einer
separaten Maske abgefragt. Um keinen Beleg in der Primanota zu erzeugen, kann
man hier diese Abfragemaske mit „Ohne Buchung weiter“ verlassen.
Wird der Beleg in der Primanota gelöscht,
so wird geprüft, ob das Anlagegut bereits weiter verarbeitet wurde, d.h. weiter
Zeilen existieren. Der Beleg kann nur gelöscht werden, wenn dies nicht der Fall
ist, ansonsten muss man einen Stornobeleg erstellen.

---

## Adobe-Vorstart

Adobe-Vorstart
Der Adobe-Acrobat-Reader benötigt – gerade in neuen
Versionen – einiges an Ressourcen und Zeit beim ersten Start. Beim Ansehen von
PDF-Dateien aus dem Formulararchiv fällt das nun besonders negativ ins
Gewicht.
Da dieses lange Laden nun in aller Regel nur beim
ersten Start auftritt, kann man einfach den Adobe-Acrobat-Reader vorab einmal in
den Speicher laden. Für die Anwender, die nicht wissen wie das geht oder einfach
keine Lust haben das zu tun, gibt es diesen Schalter, der genau diese Arbeit den
Leuten abnimmt.
Im Internet gibt es auch ein kleiner freies Zusatztool
um den Start des Adobe-Arcrobat-Readers generell zu beschleunigen. Googeln Sie
nach „adobe acrobat start beschleunigen“. Dieses können Sie gerne einsetzen,
Branchen-ERP kann aber nicht den Support für dieses Tool übernehmen.

---

## Add-On für Artikel und Artikelstamm

Add-On für Artikel und Artikelstamm
Es besteht die Möglichkeit, folgende Datenbereiche um
eigene Felder zu erweitern:
Artikel
in der Relation
„Artikeladdon“
über Artikelid

---

## ADR-Gefahrgutlisten-Import

ADR-Gefahrgutlisten-Import
Hauptmenü
Stammdatenpflege
Artikelstamm
ADR-Gefahrgutliste
oder Direktsprung
[ADR]
Die Anwendung ADR-Gefahrgutliste stellt eine
Schnittstelle zum Importieren der von der Bundesanstalt für Materialforschung
und –prüfung (BAM) herausgegebenen, lizenzpflichtigen BAM-Liste für das
europäische Übereinkommen über die internationale Beförderung gefährlicher Güter
auf der Straße (Abkürzung: ADR) zur Verfügung.
Auch die Verwendung dieser Import-Schnittstelle
unterliegt einer Lizenz. Zur Verwendung muss der
Steuerparameter „972 – ADR-Gefahrgutlisten
Lizenz“
auf
„Ja“
gestellt sein.
Hat man von benannter Bundesanstalt eine BAM-Listen
Lizenz erworben, hat man mit dieser Schnittstelle die Möglichkeit, die Daten
dieser BAM-Liste nach Referenz-ERP zu importieren.
Feld
Beschreibung
UN-Nummer
Kennnummer, für alle gefährlichen
      Stoffe, die gleichzeitig als gefährliche Güter gelten. Mit ggf.
      vorangestellten Nullen.
Lfd.-Nummer
Laufende Nummer, bezogen auf die
      UN-Nummer
Name
Benennung und
      Beschreibung
Klasse
Gefahrgutklasse
Klassifizierungscode
Eigenschaften der einzelnen Stoffe
      bzw. Gegenstände sind in Klassifizierungscodes unterteilt
Verpackungsgruppe
Nummern der Verpackungsgruppe(n),
      die dem gefährlichen Stoff zugeordnet sind
Gefahrzettel
Nummer des Musters der
      Gefahrzettel/Großzettel
Sondervorschriften
Numerische Codes der einzuhaltenden
      Sondervorschriften
Begrenzte und freigestellte
      Mengen
Begrenzte Menge | freigestellte
      Menge
Höchstmenge des Stoffes je
      Innenverpackung oder Gegenstand für die Beförderung gefährlicher Güter in
      begrenzten Mengen.
|
Alphanumerischer Code für die
      Freistellung von den Vorschriften des ADR
Verpackungen
Anweisung
      (Verpackungsanweisung):
Alphanumerischer Code der
      anwendbaren Verpackungsanweisungen.
Sondervorschrift:
Alphanumerischer Code der
      anwendbaren Sondervorschriften für die Verpackung.
Zusammenpackung:
Mit

[...]


---

## Allgemeines (Artikel-Informationsmaske)

Allgemeines (Artikel-Informationsmaske)
Das Informationssystem wurde mit dem Ziel entwickelt,
artikelspezifische Infor­ma­tionen für den Anwender individuell
gestaltbar auf Informationsbildschirmen (=Seiten) zusammenfassen zu können. Dies
sollte zum einen die Daten des Referenz-ERP Systems umfassen, als auch die Eingabe
eigener Daten erlauben. Mit dem Artikelinfor­mati­ons­system ist der
Anwender in der Lage:
•
Textliche Informationen zu erfassen
•
Über SQL Statements Daten der Datenbank einzulesen
•
Eigene Datenbankfelder anzulegen und mit Werten zu versehen
•
Weitergehende Informationen aus anderen Bereichen des Systems
einzusehen
•
O.a. Informationen auf frei definierbaren Seiten darzustellen
•
O.a. Informationen auszudrucken
Obige Funktionalitäten stehen darüber hinaus für
Kunden, Partien, Kontrakte und Vorgänge zur Verfügung.
Im Abschnitt Kundenstamm werden die Funktionen und
Einrichtungsvarianten ausführlich beschrieben; sie können analog auf
Artikelstamm und Artikel übertragen werden, so dass hier ein kurzer Abriss
genügen soll.

---

## Anlagengruppen

Anlagengruppen
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Anlagengruppen
Direktsprung
[ANKAG]
Die einzelnen Gegenstände des Anlagevermögens können
zu verschiedenen Gruppen zusammengestellt werden. Diese Gruppen können sich z.B.
aus der Gliederung des Anlagevermögens in Sachanlagen, Finanzanlagen usw. oder
nach anderen betrieblichen Gesichtspunkten ergeben.
Die Anlagengruppen können zur Eingrenzung und
Sortierung in den Auswahllisten verwendet werden. Die
Gruppierung
dient
dazu in den Reporten eine weitere Möglichkeit der Gliederung oberhalb der
Anlagengruppe zu haben. Das Feld hinter der Nummer ist die Bezeichnung der
Gruppierung und erscheint als Gruppenüberschrift in den Reporten. Hat man zu
einer Gruppierung bereits einmal Bezeichnung hinterlegt, erscheint diese dann
automatisch bei Wiederverwendung der Gruppierung. Die Reporte der
Anlagenbuchhaltung bieten die Möglichkeit nach dem Anlagenkonto, Standort und
Kostenstelle, Anlagengruppe mit Gruppierung oder nur nach der Anlagengruppe zu
gruppieren.
Gleichzeitig dienen die Anlagengruppen als
Eingabehilfe. Man kann jeder Anlagengruppe folgende Kriterien zuordnen:
•
Standort
•
Abschreibungsart
•
AfA-Satz
•
Nutzungsdauer
•
Schrottwert
•
Anlagekonto
•
AfA-Konto
•
Kostenstelle
•
Kostenträger
•
Kostenobjekt
Wählt man dann bei der Neuerfassung von Anlagegütern
eine Gruppe aus, werden die hier hinterlegten Werte als Vorbelegung
herangezogen.

---

## Anlagenstamm

Anlagenstamm
Hauptmenü
Anlagenbuchhaltung
Anlagenbuchhaltung
Anlagenstamm
Direktsprung
[ANKAS]
Der Anlagestamm wird über die Anwendung
Anlagenstamm
verwaltet. Hier werden alle relevanten Geschäftsvorfälle
erfasst. Auch können für einzelne Anlagegüter AfA-Vorschläge erfasst, gelöscht
oder freigegeben werden. Bevor man in diese Auswahlliste gelangt muss zuerst der
Firmenstamm
eingerichtet werden. Ist
der Firmenstamm noch nicht eingerichtet, so erscheint eine Meldung und die
Auswahlliste wird sofort wieder verlassen.
Bedeutung
Anlagengruppe
Die
      einzelnen Gegenstände des Anlagevermögens können zu verschiedenen Gruppen
      zusammengestellt werden. Diese Gruppen können sich z.B. aus der Gliederung
      des Anlagevermögens in Sachanlagen, Finanzanlagen usw. oder nach anderen
      betrieblichen Gesichtspunkten ergeben. Die Anlagengruppen werden in einer
      separaten Anwendung gepflegt und sind z.B. über den Direktsprung
[ANKAG]
zu erreichen.
Inventarnummer
Eindeutige Nummer zur Identifikation
      des Anlagegutes. Die Belegung bleibt dem Anwender überlassen, es ist
      jedoch möglich eine Funktion im Firmenstamm zu hinterlegen, die eine
      Vorbelegung vornimmt. Diese Nummer ist auch nachträglich änderbar, dazu
      muss man jedoch erst die Funktion
Inventarnummer ändern
auswählen.
      Dann wird das Feld Inventarnummer freigegeben und die Schreibmarke springt
      in das Feld. So wird ein versehentliches Ändern verhindert und die
      Funktion kann ggf. weggeschützt werden.
Die Prüfung der
      Inventarnummer kann mit einer eigenen Datenbankfunktion durchgeführt
      werden. Der Name der Datenbankfunktion wird im
Firmenstamm
hinterlegt.
Anlagenkonto
Dies
      ist das Konto, mit dem der Anlagewert in der Finanzbuchhaltung
      korrespondiert. Es ist das Bestand (direkte Abschreibung) bzw. das
      Bestandsveränderungskonto (indirekte Abschreibung) der Bilanz.
AfA-Konto
Dies
      ist das Aufwandskonto aus dem GuV-Bereich, wel
[...]


---

## Archiv – Dokumente hinzufügen

Archiv –
Dokumente hinzufügen
Aufruf über die Dokumentenverwaltung und die
Stammdatenpfleger-Funktion.
Beim Erststart wird ein Dateiauswahl-Dialog zum
Auswählen des hinzuzufügenden Dokumentes geöffnet. Erfolgt keine Auswahl wird
der „Dokument hinzufügen“-Dialog wieder geschlossen.
Folgende Felder stehen zusätzlich
      zur Eingabe zur Verfügung:
Datei
Pflichtfeld
Wählen Sie per
F3
mit Hilfe des Dateiauswahldialoges
      das hinzuzufügende Dokument aus.
Datei löschen nach
      Import
Bestimmt ob die importierte Datei
      gelöscht werden soll.
Die
      Einstellung wird sich sitzungsübergreifend gemerkt.
Dokument als Anlage
      hinzufügen
Bestimmt ob beim Hinzufügen das
      Dokument als Anlage hinzugefügt wird. Damit verbunden ist eine
      Eingruppierung.
Nach
      der Auswahl der Datei lässt sich die Einstellung noch vor dem Speichern
      ändern.
Die
      Einstellung wird sich sitzungsübergreifend gemerkt.
Die Funktion
Speichern
löst das Hinzufügen aus.
Bei erfolgtem „Hinzufügen“ wird eine Rückmeldung vom
System ausgegeben welcher Dokumentenname verarbeitet wurde, und unter welcher
technischen FA_ID die Speicherung im Archiv erfolgte.
Ferner wird das hinzugefügte Dokument gelöscht –
sofern es möglich ist. Erfolg dieser Aktion wird ebenfalls kundgetan.
Hinweise:
1)
Das Referenz-ERP-System belegt je nach zugrundeliegenden Kontext folgende Felder
automatisch vor:
Referenz, Kundennummer,
Belegklasse, Belegnummer
Falls der zugrundeliegende
selektierte Eintrag eine Gruppenzuordnung besitzt wird diese automatisch
vorbelegt (siehe Registerkarte „
Gruppe
“)
2)
Das Feld „Dateiname“ im Archiv wird automatisch mit dem Dokumentennamen
versorgt. Der Dokumentenname ist der Dateiname des Dokumentes ohne die
Extension.

---

## Archiv-Stammdatenpfleger

Archiv-Stammdatenpfleger
Sie erreichen den Stammdaten-Pfleger in den
Anwendungen und Varianten des Archivs. Außerdem ist er über die „
Archiv
anzeigen
“ verfügbar.
Felder
Beleg-Referenz
Referenz
Die
      Referenz stellt eine Art „Klammer“ dar, die über das Archiv hinweg
      „zusammengehörige“ Dokumente strukturiert.
Sie
      wird bei der Neuanlage von Objekten (z.B. Vorgänge, Artikel, usw.) mittels
      der „Archiv-Fakte“ ermittelt und im Laufe der Operationen – wie zum
      Beispiel beim Archivieren von Drucken – dem so entstandenen Dokument im
      Archiv zugeordnet. Die „Archiv anzeigen“-Methodiken erlauben dann in
      diesem Kontext diese Archiv-Einträge zu recherchieren.
Grundsätzlich ist aber hier die
      „Beleg-Referenz“ frei wählbar.
Belegnummer
Eine
      Beleg-Nummer.
Diese wird standardmäßig beim Druck
      von Vorgängen die Beleg-Nummer sein, es können aber je nach Kontext auch
      z.B. externe Beleg-Nummern sein.
Belegdatum
Das
      Beleg-Datum.
Im
      Falle von Hinzufügungen (Belegklasse „Hinzufügung“, 9003) kann dieses
      Datum geändert werden.
Kundennummer
Die
      zugeordnete Kundennummer.
In
      aller Regel eine Referenz-ERP-Kundennummer.
Belegklasse
Eine
      Dokument-Typisierung gemäß des Branchen-ERP-Formates FAKLASSE.
Die
      Beleg-Klasse ergibt sich immer aus dem aktuellen Workflow und Entstehung
      des Archiv-Dokuments.
Kontierung
Verarbeitungskennzeichen im Rahmen
      der Vorkontierung (in Entwicklung)
Klassifizierung
Auf
      Basis des Anwendungsformates AF_FA_KLASSE mögliche individuelle
      Klassifizierung eines Beleges.
Barcode
Archiv
      Barcode
Mandant
Mandant
Bedienerklasse
Jedes Dokument ist einer
      Bedienerklasse zugeordnet.
Bei
      Neuanlage ist es die Bedienerklasse des anlegenden Bedieners. Über das
      Sichtschutz-Konzept des Formulararchivs steuern Sie welche Bedienerklassen
      welche Dokumente anderer Bedienerklassen-Zuordnungen in den jeweiligen
      „Archiv anze
[...]


---

## Artikel

Artikel
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel
oder Direktsprung
[AR]
Der Artikel ist die bebuchbare Einheit; i.d.R. das
Verkaufsprodukt in einem Lager bei Mehrlagerverwaltung; im Einlagerfall das
Verkaufsprodukt. Im letzten Fall hat sicher­lich die Trennung zwischen
Artikelstamm und Artikel wenig Relevanz. Hier ist von Fall zu Fall zu
entscheiden, ob die Erfassung der Artikel ausschließlich über den Be­reich
Artikel oder den Einstieg Artikelstamm erfolgen sollte. Der Ablauf entspricht
dann dem beim Artikelstamm beschriebenen und wird automatisch ausgelöst, wenn
Referenz-ERP bei der Neuerfassung des Artikels feststellt, dass noch kein Artikelstamm
vorhanden ist.
Da viele Merkmale, wie Preise, Zuordnung zu
Kostenstellen, etc. lagerabhängig sein können, werden solche Größen am Artikel
festgemacht.
Alles, was in verschiedenen Lagern unterschiedlich
sein
KÖNNTE
, muss im Artikel hinterlegt werden!
Dies schafft die Möglichkeit, in einem
Artikelstammsatz mehrere Varianten zu führen
Stellt Referenz-ERP bei der Neuanlage fest, dass der
Artikelstamm vorhanden ist, werden noch die Informationen, die für eine
Ausprägung wichtig sind, abgefragt.
Zuerst wird deshalb bei der Neuanlage nach der
Artikelstammnummer gefragt. Ist sie nicht vorhanden wird darauf hingewiesen und
die Anlage des Artikelstamms ermög­licht.
Der dabei beteiligte obere Teil des Eingabebildschirms
ist identisch mit dem des Artikelstamms.
Ist sie vorhanden, verzweigt Referenz-ERP auf die Erfassung
der Ausprägung: im mittleren Bereich des Bildschirms
Folgenden Funktionen kommen hierbei zum Einsatz.
Unveränderbar werden aus dem Artikelstamm die Felder
der oberen Hälfte über­nommen; vorbelegt aus dem Artikelstamm aber
überschreibbar sind die Felder Arti­kel­nummer, Kurzbezeichnung und
Erlöskennziffer.
Eine Besonderheit ist bei der Erlöskennziffer zu beachten:
Ist diese im Artikel mit dem Wert
‚0‘
belegt, so wird bei der Verwendung
des Artikels in Vorgängen die Erlöskennziffer des zugehörigen Artikels
[...]


---

## Artikel-Bemerkungen

Artikel-Bemerkungen
Analog zum Artikelstamm können auch für den Artikel
individuelle Informationen für den internen Gebrauch erfasst werden.

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

## Individuelle Artikelnummern

Individuelle Artikelnummern
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikelstamm
oder Direktsprung
[ARSI]
In der Anwendung „Individuelle Artikelnummern“ kann
man zu einem Kunden/Lieferanten einen oder mehreren Hersteller eines Artikels
auswählen.
Dem ausgewählten Artikel können einem
Kunden/Lieferanten einige abweichende Daten zugewiesen werden, neben einer
individuellen Artikelnummer zum Beispiel auch die für den Artikel im Standard
festgelegten Stoffstromanteile und einer von der Default-Mengeneinheit des
Artikels abweichenden Mengeneinheit zur Vorbelegung bei der
Warenpositionserfassung in der Vorgangserfassung und Vorgangskorrektur inklusive
individueller Gebindefaktoren bei Gebindemengeneinheiten.
Tabreiterübergreifende Felder
Es gibt folgende Felder:
Feld
Beschreibung
Kunde/Lieferant
Kunden/Lieferantennummer des
      Datensatzes. Mittels F3 ist eine Auswahlhilfe verfügbar.
Artikel-Stamm
Artikel-Stammnummer des Artikels.
      Mittels F3 ist eine Auswahlhilfe verfügbar.
Sofern ein Artikel Stoffstromwerte hinterlegt hat, ist
der Tabreiter Lieferanten-Stoffstromdaten aktiv.
Artikel
Es gibt folgende Felder:
Feld
Beschreibung
Artikelfremdnummer
Nummer des Artikels beim Kunden bzw.
      Lieferanten
Artikel EAN
Spezielle EAN-Nummer des Artikels
      beim Kunden bzw. Lieferanten
Edi
      gültig ab
Gültigkeitsbeginn des Artikels im
      EDI-Bereich
Edi
      gültig bis
Gültigkeitsende des Artikels im
      EDI-Bereich
Hersteller
Ja/Nein Feld. Zeigt an, ob für den
      Artikel ein Hersteller existiert.
Hauptlieferant
Ja/Nein Feld. Zeigt an, ob der
      ausgewählte Kunde/Lieferant ein Hauptlieferant ist.
Bestellsperre
Ja/Nein Feld. Zeigt an, ob für den
      Artikel eine Bestellsperre existiert.
Bestellgröße
Menge einer Liefereinheit (lediglich
      informativ)
Mengeneinheit
Optionale Mengeneinheit zur
      Vorbelegung bei der Erfassung einer Warenpositionen mit diesem Artikel bei
      der Vorgangserfassung und Vorgangskorrektur. Diese Op
[...]


---

## Zuordnung von Bildern

Zuordnung von Bildern
Sowohl einem Artikelstammeintrag wie auch einem
Artikeleintrag kann ein Bild in Form einer Bilddatei zugeordnet werden (zum
Beispiel Bilddateien vom Typ JPEG, JPG, PNG, GIF, BMP).
Mit der Funktion
Bilddatei…
wird eine Maske
geöffnet, die ein bereits zugeordnetes Bild darstellt. Ist noch keine Bilddatei
zugeordnet, so wird der Text „es ist keine Graphik zugeordnet…“ auf der Maske
ausgegeben.
Mit den Maskenfunktionen
aus Datei laden…
und
bearbeiten…
kann eine Bilddatei zugeordnet beziehungsweise ein bereits
zugeordnetes Bild mit dem unter Windows dem jeweiligen Dateityp zugeordneten
Bildbearbeitungsprogramm bearbeitet werden.
Achtung:
Hier vorgenommene Änderungen werden
erst beim Speichern des Artikelstamms beziehungsweise Artikels wirksam.

---

## Artikeleingabe in der Vorgangserfassung

Artikeleingabe in der Vorgangserfassung
Bei der Vorgangserfassung kann nun der Basisartikel
angegeben werden, automatisch ändert sich die Erfassungsmaske, und es werden
noch weitere Felder, je nachdem wie viele
Merkmale
eingerichtet sind, abgefragt.
Nach Eingabe der Basisartikelnummer werden im obigen
Beispiel zwei neue Felder bereitgestellt, und es wird die Artikelnummer auf die
in der Merkmalsleiste festgelegte Länge gekürzt.
Die neuen Felder sind mit den entsprechenden
Auswahlboxen versehen, so dass eine bequeme Eingabe und Überprüfung möglich
ist.
Nach Eingabe der beiden Merkmalsfelder wechselt die
Maske wieder zurück auf die Originaldarstellung, und es wird die neu
zusammengesetzte Artikelbezeichnung angezeigt, und es kann eine Fakturierung auf
diesen Artikel vorgenommen werden.
Ist dieser Artikel noch nicht im System vorhanden, so
wird eine kurze Hinweismeldung ausgegeben, und der Artikel wird angelegt.
Ist der Artikel im System wird er wie gewohnt
bereitgestellt, es ist auch nicht notwendig die einzelnen Artikelnummern sich zu
merken, es kann per Basisartikel incl. Eingabe der einzelnen
Artikelnummernpositionen der gewünschte Artikel angesprochen werden.
Die Neu-Anlage der per Merkmalsleiste verarbeiteten
Artikel kann durch passende Angabe eines
Einrichterparameters
auch in allen Läger oder in
ausgewählten Lägern des Systems vorgenommen werden. Zusätzlich besteht die
Möglichkeit per individueller Regel die Neuanlage der Artikel zu
beeinflussen.

---

## Artikelstamm duplizieren

Artikelstamm duplizieren
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel
Duplizieren
Direktsprung
[AR]
Mit der Funktion
Duplizieren
können die
zu den in der Auswahlliste markierten Artikeln gehörenden Artikelstamm-Einträge
mit dem jeweils ausgewählten oder allen zugehörigen Artikeln unter Vergabe einer
neuen Artikelstammnummer dupliziert werden.
Zunächst wird im Feld
Zielartikelstamm
die neue
Artikelstamm-/Artikelnummer und im Feld
Bezeichnung
die neue
Artikelstamm-/Artikelbezeichnung angegeben. Das Feld
Artikelanlage
dient
zur Festlegung, ob nur der ausgewählte Artikel oder alle zum Quell-Artikelstamm
existierenden Artikel kopiert werden sollen. Die Einstellungen in den Feldern
VK-Preise
und
EK-Preise
geben an, ob die jeweiligen Listenpreise
im Verkauf beziehungsweise Einkauf ebenfalls zu duplizieren sind.
Die
eingerichteten Sekundärschlüssel wie Matchcode und EAN-Code können in der
Datentabelle
Allgemein
, Artikelstamm-Bemerkung und Artikel-Bemerkung in
der Datentabelle
Bemerkungen
angepasst werden. Zur Anpassung der
Artikeltexte in allen zum Quell-Artikelstamm gefundenen Sprachen und
Textvarianten gibt es den Bereich
Artikeltexte
.
Bezüglich der
K
ostenstellengruppe
,
Kostenträgergruppe
und
Kostenobjektgruppe
kann jwewils festgelegt werden, ob der Wert für die
neuen Artikel aus dem Quell-Artikel oder aus den jeweiligen Einträgen des
Lagerstamms entnommen werden soll. Diese Felder sind nur dann verfügbar, wenn
die zugehörigen Steuerparameter
Kostenstellen-Lizenz
,
Kostenträgerrechnung angeschlossen
beziehungsweise
Kostenobjekt-Lizenz
aktiviert sind.
Die änderbaren Daten sind aus dem
jeweiligen Quell-Artikelstamm und Quell-Artikel vorbelegt.
Nachdem der Artikelstamm und der beziehungsweise die
Artikel dupliziert wurden, kann mit den Funktionen
Neuen Artikelstamm
ändern
und
Neue Artikel ändern
das jeweilige Pflegemodul
zum Ändern des Artikelstamms und des oder der Artikel aufgerufen werden, um
zusätzliche Korrekturen der neuen Stammdaten vorzun
[...]


---

## Artikelgruppen

Artikelgruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Artikelgruppen
oder Direktsprung
[ARG]
Artikelgruppen können unabhängig von Warengruppen und
dergleichen. je Artikelstamm vergeben werden, um Artikel in anderer,
selbstdefinierter Weise zu gruppieren (für Selektionen und Sortierungen).
In Standardauswertungen ist die Artikelgruppe derzeit
nicht eingebunden; sollte dies erforderlich sein, ist es über private
Auswertungen in Auswahllisten integrierbar.
Artikelgruppe
Artikelgruppe
Nummer der Artikelgruppe
Bezeichnung
Bezeichnung der
      Artikelgruppe
Zahlungsbedingung
      Verkauf
Zahlungsbedingung für den Verkauf,
      nur wenn der
Steuerparameter 40
„Zahlungsbedingungs-Abhängigkeit“ entsprechend eingestellt
      ist.
Zahlungsbedingung
      Einkauf
Zahlungsbedingung für den Einkauf,
      nur wenn der
Steuerparameter 40
„Zahlungsbedingungs-Abhängigkeit“ entsprechend eingestellt
      ist.

---

## Artikel-Info-Gruppen

Artikel-Info-Gruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Artikel-Info-Gruppen
oder Direktsprung
[ARI]
Artikel-Info-Gruppen können unabhängig von
Warengruppen und dgl. je Artikelstamm vergeben werden, um Artikel in anderer,
selbstdefinierter Weise zu gruppieren (für Selektionen und Sortierungen).
In Standardauswertungen ist die Artikelgruppe derzeit
nicht eingebunden; sollte dies erforderlich sein, ist es über private
Auswertungen in Auswahllisten integrierbar.

---

## Artikelpool

Artikelpool
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Artikel-Pool
oder Direktsprung
[ARP]
Der Artikelpool dient dazu, mehrere Artikelstämme
gemeinsam in Statistiken be­tracht­bar zu machen, wenn die Ein- und
Verkäufe nicht unbedingt auf demselben Artikel stattfinden.
Er kann auch als 4. Stufe, neben den Warengruppen, als
Zusammenfassung von Artikeln betrachtet werden
Der Begriff des Artikel-Pools dient ausschließlich der
Zusammenfassung mehrerer Artikel in der Statistik, und zwar für den Fall, dass
Ein- und Verkauf auf getrennten Artikeln stattfinden.
Durch die Zuordnung zu derselben Poolnummer kann man
ohne Umbuchungen die Ein- und Verkäufe einander gegenüberstellen. Da zweifellos
Auswertungen in die­sem Fall deutlich komplizierter werden, sollte, wenn
immer möglich, Ein- und Verkauf über ein Konto laufen.
Auswertungen auf Poolebene finden sich bei der
Bestandsanzeige
[ARB]
.
Für die Anlage eines Pools müssen eine Nummer und eine
Beschreibung zur Erklärung des Verfahrens vergeben werden.

---

## Registerkarte Allgemein

Registerkarte Allgemein
Feld
Bedeutung
Warengruppe
Dieses Feld ist ein Merkmal des zum
      Artikel gehörenden Artikelstamms. Der Wert ist daher nur im Erfassungsfall
      des Artikels pflegbar, wenn hier auch gleichzeitig ein neuer Artikelstamm
      angelegt wird.
Steuerschlüssel
Dieses Feld ist ein Merkmal des zum
      Artikel gehörenden Artikelstamms. Der Wert ist daher nur im Erfassungsfall
      des Artikels pflegbar, wenn hier auch gleichzeitig ein neuer Artikelstamm
      angelegt wird.
Mengeneinheiten-Gruppe
Die
      Mengeneinheitsgruppe ist ein Feld des Artikelstamms. Der Wert ist daher
      nur im Erfassungsfall des Artikels pflegbar, wenn hier auch gleichzeitig
      ein neuer Artikelstamm angelegt wird.
Die Mengeneinheitsgruppe legt
      fest, in welcher Mengeneinheit der Artikel im Lager geführt wird.
      Zusätzlich werden in der Mengeneinheitsgruppe auch Default-Mengeneinheiten
      für Vorbelegung von Mengeneinheit und Preismengeneinheit bei der
      Verwendung des Artikels in der Belegerfassung festgelegt.
Preisauszeichnung
      Grundeinheit
Dieses Feld ist ein Merkmal des zum
      Artikel gehörenden Artikelstamms. Der Wert ist daher nur im Erfassungsfall
      des Artikels pflegbar, wenn hier auch gleichzeitig ein neuer Artikelstamm
      angelegt wird. Hier wird die Mengeneinheit eingetragen, in der der
      Grund-Preis für die Preisauszeichnung auszugeben ist. Passt die
      Preismengeneinheit nicht zur Grundpreisauszeichungsmengeneinheit (die
      Grundmengeneinheit der beiden Mengeneinheiten sind unterschiedlich und
      können daher nicht ohne weiteres umgerechnet werden), so ist auf mit den
      dann folgenden beiden Feldern der Umrechnungsfaktor
      anzugeben.
Beispiel: Preis in Preis pro dt, Grundpreis soll in Preis
      pro Liter ausgewiesen werden:
Liter = 1,15 pro
      kg
oder   Liter = 115 pro dt
wenn ein Liter der Ware 1,15
      kg wiegt.
Lagernummer
Die
      Nummer des Lagers, auf dem
[...]


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

## Artikelstamm in der Relation „Artikelstammaddon“ über Artikelstammid

Artikelstamm in der Relation
„Artikelstammaddon“ über Artikelstammid
Hauptmenü
Administration
Formular / Abläufe
Tabellen/Anwendungserweiterungen
oder Direktsprung
[AO]
Diese Felder stehen in eigenen Relationen
(Artikeladdon, etc.) s.o. und sind über die id verknüpft (s.o.).
Am Beispiel des Artikelstamms wird nachfolgend die
Einrichtung eigener Felder behandelt. Das Verfahren kann natürlich auf den
Artikel übertragen werden.
Erweiterung des Artikelstamms
Der Artikelstamm soll um zwei Felder erweitert werden:
Werbekostenzuschuss und Wiederbeschaffungszeit. Im Pfleger für AddOn-Daten (AO)
werden die Eintragungen vorgenommen:
Mit
F8
wird
die Neuanlage gestartet. Im Feld Tabellenname wird mittels
F3
„Artikelstammaddon“ ausgewählt. Die
Feldbezeichnung ist der Darstellungstext während der Feldname den Namen in der
Datenbank ergibt. Dieser muss also syntaktisch korrekt sein: keine Sonderzeichen
etc.
Der Feldtyp wird wieder mit
F3
ausgesucht, in diesem Fall ein Feld mit
zwei Nachkommastellen.
Die Eingabe von Zeile und Spalte wird derzeit noch
nicht ausgewertet; die Anzeige erfolgt immer nach der Eingabereihenfolge.
Im Feld Item Box kann eine bestehende Item Box
angegeben werden, die bei der Datenerfassung als Grundlage dienen soll (z.B.
ib_ku wenn auf die Kunden Bezug genommen werden soll). In diesem Beispiel ist
dies jedoch ohne Belang.
Nach Anlage beider Felder steht in der Auswahlliste
Artikelstamm nach Anwahl von AddOn folgende Eingabemaske zur Verfügung:
Auswertungen
Die hier abgespeicherten Werte können natürlich
ausgewertet werden:
Exkurs: Definition eines Reports
Grundlage des obigen Reports ist nachfolgendes SQL –
Statement, das aus der Standardvariante „nach Nummern“ abgeleitet wurde. Die
entscheidenden Zeilen wurden hervorgehoben:
// Auswahllistenfunktion :
ARTIKELSTAMM
TITLE Artikelstammauswahl
INFO Artikelstammauswahl
MASK AW_MASK
FIELD Artikelstammnummer,ArtiStamNummer,char,15
FIELD Bezeichnung,ArtiStamBezeich,char,40
FIELD
WKZ,Werbekosten
[...]


---

## Artikelstamm mit Bezeichnung

Artikelstamm mit Bezeichnung
Mit dem Report Artikelstamm mit Bezeichnung kann man
sich die gewünschten Artikelstämme mit Bezeichnung, Warengruppe und
Steuerschlüssel ausdrucken.
Über den Auswahlbereich
F2
(siehe auch
Generelle Programmbedienung
) kann man die
Datenmenge mit Hilfe der Angabe von Artikelnummern und/oder Warengruppen nach
Wunsch begrenzen.
Das Aussehen des Reports kann man über die Funktion
CRW-Optionen
Shift+F11
etwas
variieren. Da gibt es Einstellmöglichkeiten für z.B. das Anzeigen des
Firmenlogos oder dem grau Hinterlegen jeder zweiten Zeile.
Alle verfügbaren
Einstellungen findet man unter
Crystal Report Optionen
.

---

## Registerkarte Zertifiakte

Registerkarte Zertifiakte
Auf der Registerkarte Zertifikate werden jetzt die
Nachhaltigkeitszertifikate, sowie die Angabe, ob ein Artikel EUDR Pflichtig ist
hinterlegt.
Nachhaltigkeit
Um einen Artikelstamm als
Nachhaltig
zu markieren, gibt es auf dem Pfleger
den Bereich Nachhaltigkeit.
Feld
Beschreibung
Nachhaltigkeitsartikel
Ja/Nein Feld. Festlegung ob es sich
      um einen Nachhaltigkeitsartikel handelt.
Nachhaltigkeit – THG
Nummer des THG – Wertes
Wenn Nachhaltigkeitsartikel auf Nein gesetzt wird,
dann wird der Wert aus Nachhaltigkeit – THG gelöscht und es werden die
Einrichtungen im Grid Vorbelegung Warenbewegung entfernt.
In der Datentabelle „Vorbelegung Warenbewegung“ können
Vorbelegungen für die Nachhaltigkeit eingetragen werden. Diese sind dann für die
Warenbewegung gültig und können nur durch einen Eintrag an der Warenbewegung
übersteuert werden.
Feld
Beschreibung
Ab
      Datum
Datum ab wann die Vorbelegung gelten
      soll
Einkauf
Vorbelegung für Warenbewegungen im
      Einkauf
Verkauf
Vorbelegung für Warenbewegungen im
      Verkauf
Des Weiteren ist es wichtig, dass das Artikelgewicht
pro Grundmengeneinheit gepflegt wird, da über diesen Wert die Werte auf den
Auswertungen berechnen werden.
Bei Einkauf und Verkauf können „Nicht Nachhaltig“ oder
„Nachhaltig“ eingetragen werden. Es wird aber nur „Nicht Nachhaltig“ beachtet,
da man nicht nachhaltige Ware nicht als nachhaltig künstlich verkaufen darf.
EUDR-Pflichtig
EUDR-pflichtig bedeutet, dass ein Produkt unter die
EU-Verordnung gegen Entwaldung fällt. Unternehmen müssen dafür entwaldungsfreie
Lieferketten nachweisen, Herkunftsdaten dokumentieren und eine
Sorgfaltserklärung im EU-System abgeben.
Folgende Ausprägungen können ausgewählt werden.
Ausprägung
Bedeutung
Ja
Der
      Artikel ist EUDR-pflichtig.
Nein
Der Artikel fällt nicht unter die
      EUDR.
Vielleicht
Die
      Relevanz muss geprüft werden, z. B. aufgrund unklarer Herkunft oder
      Materialzusammensetzung

---

## Artikelverpackung

Artikelverpackung
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikelverpackung
oder Direktsprung
[AVP]
Die Pflege der Stammdaten wird in dem Abschnitt
Artikelverpackung
[AVP]
abgewickelt. Es
können hier zu einem Kunden und einem Artikel (lagerspezifisch) ein oder mehrere
Artikelverpackungssätze in das Referenz-ERP-System eingetragen werden.
Zu jedem Kunde/Artikel/Satzpaar können bis zu drei
verschiedene Verpackungsformen erfasst werden, die zugehörige Grundmengeneinheit
muss angegeben werden, und es ist noch die dieser Verpackung zugrunde liegende
Gebindemengeeinheit anzugeben.
Grundsätzlich wird pro Artikel ein individueller
Datensatz geführt (also kann in jedem Lager mit unterschiedlichen
Verpackungsgrößen gearbeitet werden), es gibt aber die Möglichkeit per
Auswahlschalter auf der Maske festzulegen, ob lagerübergreifend (also immer alle
Verpackungssätze und Preissätze) über alle Läger gleichlaufend einzurichten.
Pro Verpackungssatz können dann noch zusätzlich
mehrere Preisdatensätze geführt werden, untergliedert nach dem
gültig-ab-Datum.

---

## Artikeltext-Varianten

Artikeltext-Varianten
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Artikel-Text-Varianten
oder Direktsprung
[ARTX]
Artikeltexte zu einem Artikelstamm können in mehreren
Varianten erfasst werden, so dass zum Beispiel auf einem Ladeschein ein anderer
Text zum Artikel als auf einer Rechnung ausgegeben werden kann.
Eine Artikeltext-Variante wird mit einer
identifizierenden Variantennummer und einer Bezeichnung erfasst.
Artikeltext-Varianten werden im
Artikel
als Standardtextvariante für diesen angegeben.
Daneben können aber für
Vorgangsunterklassen
zu verwendende abweichende Artikeltext-Varianten bestimmt werden.
Zu beachten ist jedoch der Steuerparameter (SPA)
Artikeltext-Variante des Artikels (231)
der Steuerparametergruppe „Vorgangsbearbeitung Warenposition“.

---

## Ausweichliste

Ausweichliste
In der Auswahlliste werden Alternativartikel rein
informatorisch zu diesem Artikel angeführt, welche aber nicht automatisch
hinzugefügt werden.
Feld
Beschreibung
Priorität
Nicht weiter spezifizierbar.
Wird
      befüllt mit der Itembox IB_FS_AF_LVSAKTTYP.
Bezeichnung (Priorität)
Zugehörige Bezeichnung der
      Priorität.
Artikelnummer
Nummer des Artikels.
Bezeichnung (Artikel)
Bezeichnung des
      Artikels.
Gültig ab
Ab
      wann der Ausweichartikel gültig ist.
Gültig bis
Bis
wann der Ausweichartikel
      gültig ist.
Sperre
Hier
      kann z.B. vorübergehend die Verwendung des Ausweichartikels gesperrt
      werden.

---

## Auswertungen Druck

Auswertungen Druck
Hauptmenü
Partieverwaltung
Auswertung
In der Partiestammdatenverwaltung besteht die
Möglichkeit, zwei fest definierte Partieauswertungen zu drucken:
•
Partie-Bewegung (DRUCK)
•
Partie-Nachweis (DRUCK)

---

## Basisartikel

Basisartikel
Um dieses System nutzen zu können, müssen zunächst die
so genannten „Basisartikel“ als Artikel im System eingegeben werden. Diese
Basisartikel enthalten die Kerninformationen zu allen weiteren per
Merkmalsleiste angelegten Artikel. Während der Vorgangserfassung können dann
Artikel auf Basis dieses Artikels angelegt werden, die in folgenden Feldern von
dem Basisartikel ggf. abweichen:
•
Artikelnummer
•
Mengeneinheitsgruppe
•
Artikelbezeichnung
Es müssen dann für jedes Lager entsprechende
Basisartikel angelegt werden.

---

## Bereiche

Bereiche
In einem Kontraktschreiben bestehen verschiedene
Bereiche, so z.B. ein Abschnitt, in dem textlich die Qualitäten beschrieben
werden, ein anderer, in dem auf Stammdaten zugegriffen wird (Artikeltext), ein
weiterer, in dem andere Parameter mit Rechenfunktionen (z.B. Paritäten)
ausgedruckt werden sollen.
Die Reihenfolge des Ausdrucks und z.T. auch der Umfang
werden hier bestimmt.
Auf der Maske werden alle Bereiche einer
Kontraktvariante dargestellt. Folgende Funktionen stehen zur Verfügung, wobei
die Funktionen teilweise nur beim Variantentyp „Festtext“ zur Verfügung
stehen.
Variantenbereich
Textbaustein
Private Itembox
Standardwerte
Textbausteinwerte
Variantenbereich
Im Variantenbereich werden alle allgemeinen
Informationen zum Bereich hinterlegt.
Variantenbereich
Lfd.
      Nummer in Variante
Die
      lfd. Nummer bestimmt die Reihenfolge (aufsteigend nach Nummer) im
      Ausdruck.
Formularbereich
Hier
      wird der Bezug zum Formular (siehe “Formulareinrichter”) hergestellt.
Damit wird im Programmablauf
      sichergestellt, dass die hier gemachten Angaben sich (z.B.) auf die
      “Artikelposition” des Formulars beziehen. Welche Informationen aus der
      “Artikelposition” ausgedruckt werden, ist im Formular selbst
      hinterlegt.
Bezeichnung
Dies
      ist wieder ein freier Text zur besseren Beschreibung eines
      Bereiches.
Maximale Anzahl im Druck
Gibt
      an, wie oft der Bereich maximal gedruckt werden soll. Wenn eine 0
      eingegeben wird, so wird der Bereich bis zu maximal 50 Zeilen
      gedruckt.
Wird
      eine Zahl größer als 0 eingegeben, so wird der Bereich genauso oft
      gedruckt, wie die eingegebene Anzahl vorgibt.
Maximale Anzahl
      Folgezeilen
Maximale Anzahl von Folgezeilen, bei
      der Eingabe von 0 wird auch keine Folgezeile gedruckt.
Bereichsüberschrift
Der
      auszudruckende Bereich kann eine Überschrift erhalten.
Beschriftung 1. Zeile
Beschriftung für die erste Zeile des
      Bereiches
[...]


---

## Bestandteile

Bestandteile
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Bestandteile
oder Direktsprung
[ABST]
Häufig sollen zum Artikel zusätzliche
Qualitätsmerkmale und/oder Bestandteile wie zum Beispiel Inhaltsstoffe (unter
anderen auch Nähr- und Schadstoffe) erfasst werden. Hier können mittels Nr. und
Bezeichnung Bestandteile grundsätzlich definiert werden. Die Zuordnung erfolgt
im Artikel­stamm mit der Funktion
Zusammensetzung
(s. dort) unter Angabe
spezifischer Werte.
Maskenfeld
Bedeutung
Bestandteilnummer
Nummer des Bestandteils. Die Nummer
      kann eigenständig vergeben werden.
Bezeichnung
Bezeichnung des
      Bestandteils
Grenzwert
Format
Einheit
Nutzung in
Folgendes Auswahlmöglichkeiten
      stehen zur Verfügung
1.   egal
2.
      Ackerschlagkartei
3.
      Qualitätsdaten
4.
      Partieartikelanalyse
Typ
      Schad/Nährstoff
Folgendes Auswahlmöglichkeiten
      stehen zur Verfügung
1.   beides
2.
      Schadstoff
3.   Nährstoff
4.   Keins von
      beiden
Sortierung
Feldname(Analyse)
Feldtyp(Analyse)
Qualitätsnummer Waage
Hier
      wird die Nummer des Feldes Waagenqualität in dem Qualitätsmerkmal des
      Abrechnungsschemas der Sorte eingetragen.
Stoffstrom-Art
(nur
      bei gültiger Stoffstromdaten-Lizenz)
Art des Stoffs für die
      Berücksichtigung in Stoffstromdaten (per F3-Auswahl)
ME-Nummer
(nur
      bei gültiger Stoffstromdaten-Lizenz)
Nummer der Mengeneinheit für die
      Berechnung von Stoffstrom-Mengen
Stoffstrom-DB-Prozedur
(nur
      bei gültiger Stoffstromdaten-Lizenz)
Für die stoffartspezifische
      Berechnung der Stoffstrommenge einer Position kann an dieser Stelle eine
      private Datenbankprozedur angegeben werden.
Für die Gewinnung von Daten zur Unterstützung
stromstoffbilanzpflichtiger Betriebe (siehe
Stoffstrom-Bilanz-Daten
) sind die
bilanzierungspflichtigen Stoffe in dieser Liste einzutragen und den jeweiligen
Artikelstamm-Einträgen unter Angabe der jeweiligen Anteile nach Bedarf über
deren
Z
[...]


---

## Bestellgruppen

Bestellgruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Bestellgruppen
oder Direktsprung
[BSG]
Die Daten dieses Stammdatenpflegers werden noch nicht
ausgewertet, ein möglicher Verwendungszweck ist jedoch die Auswertung bezüglich
des automatischen Bestellwesens o.ä.
Jeder Artikel kann einer Bestellgruppe zugeordnet
werden, über die das Bestellwesen gesteuert werden kann. Die Zuordnung des
Artikels erfolgt im Artikelstamm in den Optionen "weitere Kennzeichen".
Für die Bestellgruppe selber sind lediglich die Nummer
der Gruppe und Bezeichnung der Gruppe einzutragen.

---

## Bewertungsgruppen

Bewertungsgruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Bewertungsgruppen
oder Direktsprung
[BWG]
Verschiedene Verfahren zur Bestandsbewertung stehen
zur Verfügung. Die Bewertungsgruppen dienen nun lediglich dazu, die im
Unternehmen eingesetzten Methoden zu aktivieren und ihnen einen „Namen“ zu
geben.
Bei der jeweiligen Bewertungsmethode sind jedoch die
Prinzipien der kaufmännischen Vorsicht (Imparitätsprinzip) zu beachten.
In der mitgelieferten Basisdatenbank sind folgende
Bewertungsgruppen bereits eingetragen:
•
gewogener Einkaufspreis
•
durchschnittlicher Jahreseinkaufspreis
•
durchschnittlicher Periodeneinkaufspreis
•
fixer Einkaufspreis
•
letzter Einkaufspreis
Verschiedene Verfahren zur Bestandsbewertung stehen
zur Verfügung. Und können in folgender Erfassungsmaske bearbeitet werden.
Die gewünschten Verfahren werden vom Anwender
durchnummeriert und mit einem Text versehen, und die Bewertungsmethode
zugeordnet. Für den Fall, dass das Ergebnis der Bewertungsmethode den Wert 0
ergibt, wird eine Ersatzbewertung mit einem hier festzulegenden Prozentsatz vom
durchschnittlichen Jahres-Verkaufspreises durchgeführt, sofern der Prozentsatz
nicht 0 und die Bewertungsmethode nicht mit
keine Bewertung
angegeben
ist.
Die zur Verfügung stehenden Bewertungsmethoden
sind:
keine Bewertung:
Der EK wird nicht bewertet
gewogener Einkaufspreis:
Er ergibt sich aus (alter Bestand x altem GEK)
+(Zugang x EK)}dividiert durch den neuen Bestand
durchschnittlicher
Jahreseinkaufspreis:
Die gesamten wertmäßigen Einkäufe dividiert durch die
Gesamtmenge des laufenden Geschäftsjahres
Durchschnittlicher
Periodeneinkaufpreis:
wie oben, jedoch bezogen auf einen eingegrenzten
Zeitraum
durchschnittlicher Jahreseinkaufspreis
ABSOLUT:
Berechnung wie beim
durchschnittlichen
Jahreseinkaufspreis
, jedoch gehen
negative Periodensummen von Einkaufswert und Einkaufsmenge positiv
(Absolutwert-Verfahren) in die Berechnungssummen von Gesamteinkaufswert und
Gesamteinkaufsmeng
[...]


---

## Bitzer Artikeldaten

Bitzer Artikeldaten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten des Artikelstamms gefüllt.
Die hier angefügten Qualitäten werden aus der
Bestandteil Abteilung des Artikelstamms gelesen. Min und Max Werte sind in dem
Bestandteilbereich pflegbar

---

## Bitzer Kontraktdaten

Bitzer Kontraktdaten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten des Kontraktstamm gefüllt.
Die hier angefügten Qualitäten werden aus der
Bestandteil Abteilung des Artikelstamms gelesen. Min und Max Werte sind in dem
Bestandteilbereich pflegbar

---

## Application Identifier des EAN-128 / UCC-128

Application Identifier des EAN-128 /
UCC-128
Liste der Application Identifier
AI
Beschreibung
Länge AI
Länge Daten
FNC1
00
Serial Shipping Container
      Code
2
numerisch 18-stellig
-
01
EAN
      Nummer der Handelseinheit
2
numerisch 14-stellig
-
02
EAN
      Nummer der in der Transporteinheit enthaltenen Waren
2
numerisch 14-stellig
-
10
Losnummer bzw.
      Chargennummer
2
alphanumerisch bis zu
      20-stellig
ja
11
Herstellungsdatum JJMMTT
2
numerisch 6-stellig
-
12
Fälligkeitsdatum JJMMTT
2
numerisch 6-stellig
-
13
Packdatum JJMMTT
2
numerisch 6-stellig
-
15
Mindesthaltbarkeitsdatum
      JJMMTT
2
numerisch 6-stellig
-
17
Verfalldatum JJMMTT
2
numerisch 6-stellig
-
20
Produktvariante
2
numerisch 2-stellig
-
21
Seriennummer
2
alphanumerisch bis zu
      20-stellig
ja
22
HIBCC Nummer
2
alphanumerisch bis zu
      29-stellig
-
23n
Chargennummer
3
numerisch bis zu
      19-stellig
ja
240
zus.
      Produktidentifikation vom Hersteller
3
alphanumerisch bis zu
      30-stellig
ja
241
Kundenteilenummer
3
alphanumerisch bis zu
      30-stellig
ja
250
Seriennummer eines integrierten
      Bauteils
3
alphanumerisch bis zu
      30-stellig
ja
251
Bezug auf die
      Grundeinheit
3
alphanumerisch bis zu
      30-stellig
ja
252
Global Identifier Serialised for
      Trade
3
numerisch 2-stellig
-
30
Menge in Stück
2
numerisch bis zu
      8-stellig
ja
310d
Nettogewicht in
      Kilogramm
4
numerisch 6-stellig
-
311d
Länge, Meter
4
numerisch 6-stellig
-
312d
Breite, Meter
4
numerisch 6-stellig
-
313d
Höhe, Meter
4
numerisch 6-stellig
-
314d
Fläche, Quadratmeter
4
numerisch 6-stellig
-
315d
Nettovolumen, Liter
4
numerisch 6-stellig
-
316d
Nettovolumen, Kubikmeter
4
numerisch 6-stellig
-
320d
Nettogewicht, Pounds
4
numerisch 6-stellig
-
321d
Länge, Inches
4
numerisch 6-stellig
-
322d
Länge, Feet
4
numerisch 6-stellig
-
323d
Länge, Yards
4
numerisch 6-stellig
-
324d
Breite oder Durchmesser,
      Inches
4
numerisch 6-stellig
-
325d
Breite oder Durchmesser,
[...]


---

## Fertig

Fertig
Jetzt starten wir die Scanner Software und erneuern
das Menü. Danach klicken wir auf „Artikel Info An“ und Scannen einen Artikel nun
erscheint die Lagernummer, Artikelnummer und die Bezeichnung auf dem Bildschirm.
Danach klicken wir auf „Artikel Info Aus“

---

## Beispiel für eine Private Anwendung

Beispiel für eine Private Anwendung
In diesem Beispiel erklären wir, wie Sie die
Möglichkeit haben, eine eigene Anwendung für unser Aeins Scanner System zu
entwickeln. In diesem einfachen Beispiel zeigen wir, wie Artikel Information
unten in die Anzeige geschrieben werden.
Was wird für eine Private Anwendung benötigt.
Eine
      IB_Box, die die Anzeige auf dem Scanner steuert
Eine
      Private Prozedur, die die Daten zusammensammelt und an den Scanner
      überträgt
Die
      Private Anwendung muss unter sctcp eingetragen sein

---

## Private Procedure

Private Procedure
//
Priv. Procedure p_artikelanzeige
//
// Beschreibung: Diese
Funktion übergibt den gescannten wert an die IB_Box
//
Create procedure
p_artikelanzeige (
in
in_Aktionstyp
integer
,
in
in_aktionswert
char
(255),
in
in_ident
integer
,
in
in_positionsIdent
integer
,
in
in_scannernummer
char
(40),
in
in_kommando_scanident
integer
,
in
in_AnzahlImBlock
integer
,
in
in_Blockzaehler
integer
,
in
in_letzte_aktion
integer
,
in
in_Aktionstext
char
(100),
in
in_Kopftext1
char
(100),
in
in_Kopftext2
char
(100),
in
in_reaktionstyp
char
(5),
in
in_lagernummer
integer
,
in
in_bedienerid
integer
,
in
in_protokoll
char
(100),
in
in_feldid
integer
,
in
in_scanident
integer
,
in
in_klassnummer
integer
,
in
in_nummer
integer
,
in
in_testflag
integer
,
in
in_diese_positionsnummer
integer
)
BEGIN
declare
dc_scrollbar
integer
;
declare
dc_neuzeilennummer
integer
;
declare
dc_statustext
char
(1024);
declare
dc_Aktionstext
char
(100);
declare
dc_status
integer
;
set
dc_neuzeilennummer = 1;
set
dc_statustext =
''
;
set
dc_Aktionstext  =
''
;
set
dc_status =
0;
if
(
isnull
(dc_neuzeilennummer,0)) = 0
then
set
dc_neuzeilennummer = 1;
end if
;
select
ALSWert
into
dc_scrollbar
from
AeinsLastSetting
where
ALSAnwendung=
'Tcpip_Scanner'
and
ALSEintrag =
'scanner_scrollbar'
and
BedienerKurz=
'0'
;
if
( in_Aktionstyp =
-4
or
in_Aktionstyp = -6
or
in_Aktionstyp = -7
or
in_Aktionstyp = 1)
then
set
dc_status = 4;
if
dc_scrollbar = 1
then
set
dc_statustext=
'IB_SCANNER_ANZEIGE;TOP=9&SEKUNDS='
||in_aktionswert||
'&ZEILENNUMMER='
||dc_neuzeilennummer;
else
set
dc_statustext =
'IB_SCANNER_ANZEIGE;TOP=50&SEKUNDS=
'
||in_aktionswert||
'&ZEILENNUMMER='
||dc_neuzeilennummer;
end
if
;
end if
;
// Berechnen der
Zeilennummer
if
dc_scrollbar
= 1
then
If
( in_Aktionstyp = -1
and
in_aktionswert
=
'KEYUP'
)
then
if
in_disp_zeilennummer >= 9
then
set
dc_neuzeilennummer = in_disp_zeilennummer -
9;
end if
;
update
datenstromscanner
set
statustext =
'IB_SCANNER_ANZEIGE;TOP=9&SEKUNDS='
||in_aktion
[...]


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

## Drop Down Menü

Drop Down Menü
Die Menüzeile am oberen Bildschirmrand bietet die
Möglichkeit, eine Programmfunktion aufzurufen, ohne die bisherige Arbeit
abbrechen zu müssen.
So kann z.B. während der Belegerfassung aus dem
Auswahlbildschirm heraus durch Anwahl von
Stammdaten
Artikel
ein Artikel neu erfasst
werden, ohne dass der Auswahlbildschirm Belegerfassung verlassen werden muss.
Auch dieses Menü kann sowohl mit der Maus als auch der Tastatur bedient
werden:
Mit der Maus den gewünschten Programmpunkt, z.B.
Stammdaten
anklicken, es öffnet sich ein
Untermenü, das entsprechend bedient wird
Mit der Taste
ALT
auf die Menüzeile umschalten, dort mit
↓↑ und
Eingabe
den Programmpunkt
anwählen oder
Mit der
ALT
-Taste auf die Menüzeile umschalten und
mit
S
den Punkt
Stammdaten
auswählen.
Mit der Maus, bei Markieren eines mit
gekennzeichnetem Feld wird das Untermenü
angezeigt. (hier
S
tammdaten,
F
irma,
F
irmenkonstanten
F
ilialstamm
FLST)
Mit den Pfeiltasten rauf/runter innerhalb eines Menüs
Und mit rechts/links zu den Untermenüs, wenn ein
davor steht und zum nächsten Menü
nur wenn
kein
vor dem Menüpunkt steht.
Mit den unterstrichenen Anfangsbuchstaben innerhalb
des Menüs, ohne zusätzlich die
Alt
-Taste zu drücken.

---

## Druckerstamm: Pfleger

Druckerstamm: Pfleger
Einrichtung
Druckerstamm – Register Einrichtung
Beschreibung
Druckernummer
Druckernummer, Ident des
      Druckerstammes
Kurzname
Kurzbezeichnung
Bezeichnung
Druckerbezeichnung
Queue/Datei
Kann
      entweder die verfügbare LPTx Schnittstelle sein, welche im Capture
      zugeordnet wurde oder die Direktansprache für eine Queue in der Syntax
      \\{Druckserver}\{Druckername}\
Bei
      Windows-Druck die Bezeichnung der Druckerwarteschlange.
Im
      Windows-System zu finden unter
Systemsteuerung\Hardware und
      Sound\Geräte und Drucker
bzw. Funktion
      „Druckerdialog“
Mit
      [F3] können Sie einen Drucker auswählen.
Druckertyp
Auswahl mit
F3
aus vorher eingerichteten Druckern
      (Nadel, Laser usw.), Direktsprung
[DRT]
Einzelblatteinz
0:
      Fortlaufender Druck
1:
      anhalten bei Blattwechsel
2:
      anhalten und Meldung
Drucker gesperrt
Kennzeichen um Drucker zu
      sperren
Bei
      JA kann auf diesem Drucker nicht gedruckt werden.
Zusatz-Funktionen
Kennzeichen für
      Zusatz-Funktionen
Datei Append
Falls unter QUEUE/Datei eine Datei
      spezifiziert wurde, bewirkt ein ‚Ja‘, dass die Ausgabe stets an das Ende
      der Datei angefügt wird, ‚nein‘ löscht die Datei vor der Ausgabe.
Achtung: Bei der Ausgabe auf
      Druckerwarteschlangen von Novell-Servern diesen Parameter immer auf ‚Nein‘
      stellen!
Schließfunktion
Angabe einer
      Schließfunktion
Ruft
      eine Programmfunktion auf, z.B. „notepad“. In Kombination mit der Angabe
      eines Dateinamens (z.B. Print.txt) in „Queue“ wird dann hier
      hineingedruckt und der Notepad geöffnet.
Seitenlänge
Vorgabe einer
      Seitenlänge
Nummernkreis (Datei)
Bei
      „Spooldruck“ kann hier ein Nummernkreis zugeordnet werden, der die
      „Ausdrucke“ nummeriert
Windows Druck
Kennzeichen, ob Drucker ein
      Windows-Drucker ist
Default Font Normal
Optionale Angabe eines
      Default-Fonts
Default Font Compress
Optionale Angabe eines

[...]


---

## DSFinV-K Export

DSFinV-K Export
Hauptmenü
Barvorgänge
Stammdaten
DSFinV-K Export
Allgemein
DSFinV-K ist die Digitale Schnittstelle der
Finanzverwaltung für Kassensysteme.
Dies ist die Taxonomie, nach der die Transaktionsdaten
der Kassen und Aufzeichnungssysteme einheitlich gespeichert werden müssen. Die
einheitliche Speicherung ermöglicht den Finanzbehörden eine tiefergehende und
strukturierte Prüfung der Kassenvorgänge, als dies in der Vergangenheit der Fall
war. Dies impliziert, dass das Finanzamt nicht lediglich die manipulationsfreie
Nutzung der Registrierkasse überprüfen kann, sondern durch die im DSFinV-K
Format strukturierten Daten auch die korrekte Verbuchung von Geschäftsvorfällen,
wie z. B. Trinkgeld, überprüfen kann. Insofern geht die
Kassensicherungsverordnung weit über die Absicherung von Bargeldumsätzen hinaus.
+
Der Steuerpflichtige muss einen DSFinV-K Export
jederzeit für eine Prüfung durch die Finanzbehörde zur Verfügung stellen. Der
DSFinV-K Export knüpft an den GoBD-Export an, ist jedoch einheitlich
strukturiert und deutlich umfangreicher. Der GoBD-Export reicht also ab dem
1.1.2020 nicht mehr aus, um die steuerlichen Anforderungen zu erfüllen.
Ziele der DSFinV-K
Ziel der Standardisierung ist die Definition einer
Struktur für Daten aus Kassensystemen, für die ab dem 01.01.2020 die Nutzung der
gesetzlich geforderten einheitlichen digitalen Schnittstelle (§ 146a Abs. 1 S. 4
AO) gilt. Durch die Standardisierung sollen folgende Ziele abgedeckt werden:
•
Einheitliche Datenbereitstellung für die Außenprüfung sowie für
Kassen-Nachschauen durch definierte Kasseneinzelbewegungen, Stammdaten und
Kassenabschlüsse, so dass eine progressive und retrograde Prüfbarkeit zwischen
den Grundaufzeichnungen und der Erfassung im Hauptbuch (Finanzbuchhaltung)
gewährleistet ist.
•
Ermöglicht die Auslagerung aller im jeweiligen System erfassten Daten in
ein Archivsystem.
•
Ermöglicht eine vereinfachte Überprüfung der in die Finanzbuchhaltung
übertragenen strukturie
[...]


---

## Einstellungen Anlagenbuchhaltung

Einstellungen Anlagenbuchhaltung
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Firmenstamm
Direktsprung
[ANKFS]
Im Firmenstamm werden verschiedene Einstellungen für
die Anlagenbuchhaltung vorgenommen. Bevor man Anlagegüter erfassen kann, müssen
diese Daten einmal eingerichtet werden.
Option
Bedeutung
Neue
      Anlagegüter immer als Zugänge übernehmen?
Im
      Standard wird bei der Neuerfassung aus der Finanzbuchhaltung die erste
      Zeile in der Historie immer als AHK geführt. Trägt man hier ein JA ein, so
      wird diese Zeile mit Zugang vorbelegt. Diese Einstellung hat keine
      Auswirkung auf die Auswertungen, da im Jahr der Anschaffung AHK und Zugang
      als Zugang ausgewiesen werden.
Eingangsgutschriften als negative
      Zugänge führen?
Wenn
      in der Belegerfassungen Eingangsgutschriften erfasst werden und bei dem
      Gegenkonto handelt es sich um ein Anlagenkonto, so kann man diese Werte -
      wie bei Eingangsrechnungen - direkt in die Anlagenbuchhaltung übernehmen.
      Eingangsgutschriften führen zu einer Verminderung der Anschaffung- und
      Herstellungskosten und werden als Teilabgang in die Historie eingetragen.
      Wenn man die Eingangsgutschriften lieber als Zugänge mit negativem Betrag
      führen möchte, so muss man hier JA eintragen. An den Rechenoperationen
      ändert dies nichts.
Zugänge im Folgejahr (Stammblatt)
      als AHK ausweisen?
Im
      Anlagenstammblatt werden Zugänge
als AHK ausgegeben, wenn sie im
      Anschaffungsjahr liegen und bereits für Folgejahre Daten erfasst
      wurden.
GWG
      sofort bei Erfassung abschreiben?
Wenn
      hier ein Ja eingetragen wird, so wird gleich bei der Erfassung des GWG
      eine weitere Zeile mit der AfA über den Betrag des GWG abzüglich des
      Anhaltewertes in die Historie geschrieben.
Sonstige betriebliche Erträge /
      Aufwendungen führen?
Es
      ist möglich, beim
Verkauf
den Verkaufsbetrag
      einzugeben. Über die Differenz können dann Ze
[...]


---

## Ergebnismengeneinheiten

Ergebnismengeneinheiten
Diese Anwendung dient in erster Linie der Ansicht und
Auswertung der Mengen­ein­heiten eine weitere Bearbeitungsmöglichkeit
besteht nicht.
Die Felder sind nicht zu Bearbeitung
freigeschaltet.
Die Maske entspricht nicht der der Mengeneinheiten

---

## Erlöskennziffer Stamm

Erlöskennziffer Stamm
Hauptmenü
Administration
Erlöskennziffern
Erlöskennziffer Stamm
oder Direktsprung
[EKZS]
Eine Erlöskennziffer besteht aus einer fortlaufenden
Nummer und der Bezeichnung. Per Erlöskennziffer ist es möglich, zusammengehörige
Artikel (z.B. Warengruppen) auf identische Erlös- und Aufwandskonten zu buchen.
Die Erlöskennziffer wird beim Artikel bzw. beim Artikelstamm hinterlegt.
Hierbei gelten folgende Regeln:
•
Die Erlöskennziffer 0 (Null) übernimmt DEFAULT-Funktion
•
Ist beim Artikel eine Erlöskennziffer größer als (>) 0 eingetragen, so
hat dieser Vorrang vor derjenigen im Artikelstamm (Beispiel: Erlöskonten je
Lager)
•
Ist beim Artikel eine Erlöskennziffer 0 eingetragen, so wird die EKZ des
Artikelstamms verwendet
Werden Artikel über
Neu
F8
erfasst, so erfolgt die Abfrage der
Erlöskennziffern im Artikelbereich. Der automatisch angelegte Artikelstamm
erhält die identische Erlöskennziffer.

---

## Datendrehscheibe

Datendrehscheibe
Will man den Artikelimport für die Datendrehscheibe
automatisieren, kann man auf dem Register Vorlagen hinter Datendrehscheibe ein
Ja eintragen. Es wird dann eine von Branchen-ERP entwickelte Prozedur in die
Verarbeitungsroutine eingetragen. Mit dem Schalter  „Mit Artikelimport“
kann entschieden werden, ob  beim Einspielen der Terres Dateien die neuen
Artikel oder Änderungen mit in den Referenz-ERP Artikelstamm übernommen werden sollen.
Wird der Schalter auf „Ja“ gestellt, so wird dem Parameter „in_Artikelimport“
eine 1 zugewiesen, bei „Nein“ wird dem Parameter die 0 zugewiesen. Der
Standardwert ist 0 .
begin
call
Fehlerprotokoll
(
in_text
=
'Start
Datendrehscheibe'
);
call
amic_evt_datendrehscheibe
(in_Artikelimport=0);
call
Fehlerprotokoll
(
in_text
=
'Ende
Datendrehscheibe'
);
exception
when
others
then call
fehlerprotokoll
(
in_text
=
'FEHLER
DatenDrehscheibe!'
)
end
Neben einigen Systemprüfungen, geschieht hier
folgendes:
Die Dateien, die sich in dem Verzeichnis befinden, das
man unter Datendrehscheibe angegeben hat, werden eingelesen.
Wurden Dateien erfolgreich eingespielt, so werden sie
- wie unter Datendrehscheibe definiert  - weiter verarbeitet.
Eventuell auftretende Probleme findet man im
Fehlerprotokoll.

---

## Faktorherkunft

Faktorherkunft
Diese Festlegung gibt an, auf welcher Stufe mit der
Suche nach Gebindefaktoren begonnen wird, bei „nicht gefunden“ wird stets weiter
„unten“ weitergesucht. In diesem Beispiel soll der Faktor aus der Mengeneinheit
kommen. Dies ist immer dann sinnvoll, wenn dieser Faktor und die
Umrechnungsdefinition häufig wieder verwendet werden kann. Man erspart sich dann
immer wiederkehrende Eintragungen im Artikelstamm Wenn jedoch das Rechenschema
immer wieder verwendet werden soll, die Faktoren sich jedoch unterscheiden, dann
ist es natürlich sinnvoll, die Mengeneinheit einmal anzulegen und die Faktoren
im Artikel zu hinterlegen.
Achtung: Im Artikel können die Gebindefaktoren nur
eingegeben werden, wenn in der Mengeneinheit der Eintrag vorgenommen wurde.
Ansonsten wird die Option nicht angeboten.
Faktorherkunft
1
aus
      Mengeneinheit
2
aus
      Artikelstamm
3
aus
      dem Artikel
4
aus
      Artikel- Ausprägung

---

## Festlegung der Artikelnummernstruktur

Festlegung der
Artikelnummernstruktur
Innerhalb des Artikelpflegers kann eine
Artikelnummernstruktur für den Warenerfassungsteil vorgegeben werden. Zur
genauen Festlegung dieser Struktur muss angegeben werden, wie lang jeder
einzelne Teil einer Artikelnummer sein soll, mit welcher Itembox dieser Teil
überprüft werden soll, welcher Textersetzungsteil aus der Überprüfungsmechanik
in den Artikeltext übernommen werden soll, und ob ggf. ein Teil dieser Nummer
die Mengeneinheitsgruppe steuern soll.
Die Eingabemaske sieht wie folgt aus:
In diesem Beispiel wird die Artikelnummer aus 3 Teilen
zusammengesetzt, und zwar einem festen Anteil von 3 Stellen der
Basisartikelnummer ( den ersten drei Stellen ), von einem weiteren dreistelligen
Teil der die Mengeneinheitsgruppe darstellt und einem abschließenden 4stelligen
Teil, in dem das Herkunftsland verschlüsselt ist.
Die Artikelbezeichnung dieses Artikels setzt sich
zusammen aus der Artikelbezeichnung des Basisartikels, aus der
Mengeneinheitsgruppenbezeichnung und aus der Staatsbezeichnung (die einzelnen
Blöcke werden jeweils durch einen Bindestrich voneinander getrennt).
Im obigen Beispiel ist das zweite Feld gekennzeichnet
als ein Mengeneinheitsgruppenfeld, was zu Folge hat, dass bei der Neuanlage des
Artikelstamms sofort diese Mengeneinheitsgruppe in den neuen Artikel eingetragen
wird. Der Verkaufspreis wird entsprechend mit der Mengeneinheit VK dieser Gruppe
vorbelegt.
Die Merkmalsleiste kann nur bis zu 8 Merkmale pro
Artikelnummer spezifizieren.

---

## Sachkonten

Sachkonten
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Direktsprung
[SKS]
Die Sachkonten sind die eigentlich zu bebuchenden
Konten. Nach Anwahl der Auswahlliste werden die erfassten Konten angezeigt. Es
bestehen folgende Bearbeitungsmöglichkeiten:
•
Neu erfassen
•
Ändern / Ansehen
•
Löschen
•
Plandaten erfassen
•
Drucken
•
Sachkonten Importieren
Bei Anwahl der Funktionen „
Neu
“,
„
Ändern
“ oder „
Ansehen
“ öffnet sich die
Erfassungsmaske. Unterhalb des Kopfbereichs, in dem die Kontonummer, der
Kontotyp und die Bezeichnung abgefragt werden, befinden sich drei Register, auf
denen dann detailliertere Informationen erfasst werden können.
Beschreibung
Kontonummer
Die
      Kontonummer des Sachkontos mit maximal 8 Stellen. Sie ist ein eindeutiger
      Suchschlüssel. Hat man einmal die Kontonummer vergeben, kann diese nicht
      mehr geändert werden. Man kann jedoch über die Funktion „
Speichern
      unter
“ alle Einstellungen unter einer anderen Kontonummer
      speichern und dann ggf. die alte Kontonummer löschen.
In
      der Finanzbuchhaltung ist es Sinnvoll, die Nummern für Sach-, Personen-
      und Oberkonten in getrennten Bereichen zu haben. Diese Bereiche können in
      Referenz-ERP selber festgelegt werden. Dies geschieht über Nummernkreise und
      deren Ober- und Untergrenzen. Die Nummernkreise für die Kontogruppen
      werden in der „
Allgemeinen Nummernkreiszuordnung
“ (Direktsprung
[MNDNK])
festgelegt.
Ist
      kein Nummernkreis in der
Allgemeinen Nummernkreiszuordnung
“
      festgelegt, können keine Sachkonten erfasst werden. Dieses Verhalten lässt
      sich per Einrichterparameter „
Nummernkreiszuordnung ignorieren
“
      ändern, indem man den Wert auf
Ja
ändert. Es findet dann kein
      Bereichstest statt.
Kontotyp
Hier
      wird angegeben, ob es sich um ein Bilanz-, GuV – oder Statistikkonto
      handelt. Dieses Kennzeichen wird später in den Auswertungen behandelt
      (Bilanzerstellung u.a.) und wird bei der Bele
[...]


---

## Firmenkonstanten

Firmenkonstanten
Im Firmenstamm werden übergreifende
Steuerungsinformationen verwaltet:

---

## Format pflegen SF5

Format pflegen SF5
Hier kann man den Formatpfleger zu den Merkmalen 1-4
aufrufen. Dafür muss man vorher ein Merkmalfeld betreten haben. Danach wird
immer das Format für das zuletzt betretene Merkmal aufgerufen.

---

## Der Formular-Pfleger

Der Formular-Pfleger
Formularstamm – Register
      Formular
FELD
Beschreibung
Formularnummer
Nummer und Bezeichnung des
      Formulars
FormularBezeichn.
Formularbezeichnung
Formulartyp
F3
      Auswahl -
Typenangabe des
      Formulars
Der
      Formulartyp legt fest, welche Bereiche für das neue Formular zur
      Verwendung frei geschaltet werden.
Vorlage-Formular
F3 Auswahl:
Möglichkeit ein schon vorhandenes
      Formular als Vorlage für ein neues zu verwenden
Drucktext
Länge, Breite
Zahlenwertangaben für beide
      Werte.
Formularlänge und –breite lt.
      Einrichtung oder Druckerstamm benutzen.
Es
      wird nur herangezogen, wenn das folgende Feld auf „Formularlänge lt.
      Einrichtung“ gestellt wird.
Bei Einstellung auf „Formularlänge lt.
      Druckerstamm“ wird die Einstellung für die Seitenlänge des Druckers im
      Druckerstamm
[DRST]
verwendet.
      Dies gilt aber auch nur für einen ASCII Druck. Ist in den
      Druckereinstellungen das Feld Windows Druck auf Ja gestellt worden, dann
      sind die Seitenlängenangaben insofern unwichtig, als dass die Auflösung
      des zu erreichenden Druckers  ermittelt wird und die Seitenlänge
      bestimmt.
Seitensteuerung
Angabe ob Seitenumbruch oder Endlos
      ohne Seitensteuerung innerhalb des Formulars
Seitenumbruch
-
Kopf und Fuß werden
      immer auf jeder Seite gedruckt
Endlos ohne
      Seitensteuerung
-
Kopf und Fuß werden
      je nur einmal gedruckt. Zwischen den beiden können mehrere Seiten mit
      vielen Informationen liegen.
Archivierung
F3 Auswahl:
0 =
      nicht archivieren
1 =
      archivieren und Probleme immer melden
2 =
      archivieren und Probleme nur einmal melden
3 =
      archivieren und Nachricht im Fehler-/Ereignisprotokoll
4 =
      archivieren, jedoch nicht drucken!
7 =
      Mailversand ohne Druck (veraltet)
8 =
      Mailversand mit Druck (veraltet)
Crw/Vbs
F3 Auswahl:
0 =
      Keine Auswahl
1 =
      CRW auf Basis Formular mit CRW Druc
[...]


---

## Funktionen

Funktionen
Sie können im Gridstammpfleger
•
Griddefinitionen auswählen
•
Neue Griddefinitionen anlegen
•
Griddefinitionen bearbeiten

---

## Funktionsaufruf (Artikel-Informationssystem)

Funktionsaufruf (Artikel-Informationssystem)
Das Informationssystem kann aus verschiedenen
Anwendungen (Artikel­stamm, Artikel, etc.) aufgerufen werden; nach Anwahl
des Artikels wird in die Anwendung verzweigt.

---

## Gebindetypen

Gebindetypen
Die Gebindetypen werden folgendermaßen
interpretiert:
Gebindetypen
0
kein
      Gebinde
Anzahl Liefereinheiten = Anzahl
      Mengeneinheiten
1
lineares Gebinde
      (Anzahl)
Anzahl mal Gebindemaß 1
z.B.
      10 Sack à 25 kg = 250 kg
2
Gebinde 2. Stufe
      (Fläche)
Anzahl mal Gebindemaß 1 mal
      Gebindemaß 2
z.B. 10 Paletten à 24 Kartons
      a´ 6 Flaschen
3
Gebinde 3. Stufe
      (Volumen)
Anzahl mal Gebinde 1 mal Gebinde 2
      mal Gebinde 3
z.B.10 Behälter à 5 x 3 x 2 m = 300
      cbm
4
Addition (Gebi1 + Gebi2)
Anzahl mal (Gebinde 1 + Gebinde
      2)
5
Subtraktion (Geb1 -
      Geb2)
Anzahl mal (Gebinde 1 - Gebinde 2)
z.B.
      Alter Zählerstand - neuer Zählerstand
6
Anbruch,
      aufgerundet(deaktiv)
Das
      Ergebnis einer Gebindeberechnung ist immer ein ganzzahlig aufgerundetes
      Vielfaches des ersten Gebindefaktors, also der
      "Packungsgröße".
7
Anbruch,
      abgerundet(deaktiv)
Das
      Ergebnis einer Gebindeberechnung ist immer ein ganzzahlig Vielfaches des
      ersten Gebindefaktors, also der "Packungsgröße" abzüglich einer
      Restmenge.
8
Faktor1 * Faktor2 /
      Faktor3
9
Faktor1 * Faktor2 * Faktor3 *
      Faktor4
Ein
      Gebindetyp, der es z.B. erlaubt Paletten zu fakturieren, die Lagen mit
      Kartons und diese wiederum in Dosen gepackt sind, aber artikelspezifische
      Gewichte pro Dose führen.

---

## Registerkarte Gebinde

Registerkarte Gebinde
Wenn in der Mengeneinheit (Gebinde) eingetragen wurde,
dass die Gebinde­ein­hei­ten im Artikelstamm und/oder Artikel
abgelegt sind, dann ist hier eine Eintragung möglich:
Dies sollte immer erfolgen, wenn Gebindefaktoren
unterschiedlich sind, es sich jedoch immer um die gleiche Gebindeformel handelt.
Die Gebindefaktoren werden für die Bestandsführung (Lager), Einkauf und Verkauf
abgelegt. Es sind jeweils mehrere unterschiedliche Faktoren je Mengeneinheit
möglich: Eine Bestandsführung und die Preisführung könnte in cbm erfolgen, die
Volumenermittlung jedoch auf unterschiedlichen Standardmaßen beruhen!

---

## Gebäude-AfA Stammdaten

Gebäude-AfA Stammdaten
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Gebäude-AfA
Direktsprung
[ANKGE]
Auf Gebäude ist grundsätzlich sowohl lineare als auch
degressive AfA möglich. Für ein nach dem 31.12.2005 hergestelltes oder
angeschafftes Gebäude ist nur noch lineare AfA zulässig.
HINWEIS
:
Bei der Verwendung der
Gebäude-AfA werden zur Bestimmung der bereits errechneten AfA-Zeiträume die
Geschäftsjahresstammdaten herangezogen, daher ist es notwendig, dass alle
Geschäftsjahre eingerichtet sind.
Die Gebäude-AfA ist sowohl für Lineare als auch für
degressive AfA implementiert. Das besondere an der degressiven Gebäude-AfA ist,
dass sich die AfA – Sätze im Laufe der Lebensdauer ändern. Bei Linearer AfA kann
jedoch nur ein Prozentsatz angegeben werden.
Diese Staffel wird unter dem Menüpunkt „Gebäude-AfA“
erfasst. In dem folgenden Beispiel sieht man die AfA-Sätze, die laut § 7 Abs. 5
Nr. 1 EStG für Gebäude, die vor dem 01.01.1994 angeschafft wurden gelten.
Die 10% gelten für das Jahr der Fertigstellung sowie
für die folgenden drei Jahren, also trägt man hier eine 4 ein.
Ab dem 5. bis zum 7. Jahr gilt der Satz 5%,
Bis zum Ende der Nutzungsdauer - also bis zum 25. Jahr
- gilt dann nur noch ein Satz von 2,5 %
Im Anlagegut hinterlegt man nur noch
die „AfA-Nummer“ und die Prozentsätze werden dann automatisch gezogen.

---

## Gefahrgut

Gefahrgut
Für die Gefahrgutabwicklung können im
Artikelstamm-Pflege-Modul diverse Angaben mit der Funktion
Gefahrgut
hinterlegt werden. Diese Funktion ist sowohl von der
Artikelstamm-Pflege-Maske als auch direkt von der Artikelstamm-Auswahlliste aus
aufrufbar und ermöglicht die Pflege von Gefahrgutdaten,  die in
Formulareinrichtungen gemäß der Vorschriften des ADR (
A
ccord
européen relatif au transport international des marchandises
D
angereuses
par
R
oute,
Europäische Übereinkommen über die internationale
Beförderung gefährlicher Güter auf der Straße ) berücksichtigt werden
können.
Feld
Bedeutung
UN-Nummer
UN-Nummer nach ADR Teil 3 Tabelle
      A
Verpackungsgruppe
Verpackungsgruppe nach ADR Teil 3
      Tabelle A
Gefahrgut-Klasse
Nummer der
Gefahrgut-Klassen-Definition
Brand-Klasse
Nummer der
Brand-Klassen-Definition
Die
      Brand-Klasse ist entgegen früheren Verordnungen nach ADR nicht mehr
      erforderlich. Aus historischen Gründen wird diese in Referenz-ERP jedoch zur
      individuellen Nutzung weiterhin angeboten.
Toxizitäts-Klasse
Nummer der
Toxizitäts-Klassen-Definition
Die
      Toxizitäts-Klasse ist entgegen früheren Verordnungen nach ADR nicht mehr
      erforderlich. Aus historischen Gründen wird diese in Referenz-ERP jedoch zur
      individuellen Nutzung weiterhin angeboten.
Postversand zulässig
Kennzeichen (Ja/Nein): Hinweis für
      die Zulässigkeit des Gefahrgut-Versands per Post.
Merkblatt
Der
      UN-Merkblatt-Verweis ist entgegen früheren Verordnungen nach ADR nicht
      mehr erforderlich. Aus historischen Gründen wird diese in Referenz-ERP jedoch
      zur individuellen Nutzung weiterhin angeboten.
Gefahrgutmenge pro einer Anzahl von
      Grundmengeneinheiten
Zur
      Berechnung von Volumen beziehungsweise der Bruttomasse oder Nettomasse
      nach ADR ist es erforderlich, diesen Bezug in Grundmengeneinheiten der
      Mengeneinheitsgruppe des Artikelstamms zu hinterlegen. Die Interpretation
      in Litern oder Kilogramm ergib
[...]


---

## gelöschte Mengeneinheiten

gelöschte Mengeneinheiten
Hier bestehen innerhalb der aus der Gebindeerfassung
bekannten Maske keine Eingabemöglichkeiten. (Die Felder sind blau
hinterlegt)
Die wird in der unteren Zeile angezeigt
In der Funktionsbox besteht allerdings die Möglichkeit
mit der Funktion UNDELETE die jeweilige Mengeneinheit wieder zu
reaktivieren.

---

## Gridstammdatenpfleger

Gridstammdatenpfleger
Direktsprung
[GDS]
Der Gridstammpfleger dient zur Pflege des Aufbaus von
Grids, also Datentabellen, die in Referenz-ERP verwendet werden. Griddefinitionen
können auch Beschreibungsstrukturen für den externen Prozess sein.

---

## Gruppenzuordnung

Gruppenzuordnung
Hier erfolgt die Zuordnung von
Artikelgruppe
,
Artikel-Info-Gruppe
,
Verpackungsgruppe
und
Pool
. Auf die Parameter wurde weiter oben
eingegangen.
Ein weiteres sehr wichtiges Element ist die
Artikelklasse. Folgende Eintragungen sind möglich:
Normalartikel:
Der fakturierfähige Artikel;
dies ist der Standardwert
Transportkosten:
für Erweiterungen des
Frachtwesens vorgesehen; z.Z. nicht aktiv
Gefährliche Güter
: für Erweiterungen der
Gefahrgutabwicklung vorgesehen; z.Z. nicht aktiv
Dienstleistungen
: Zusammen mit dem
Steuerungsparameter (21,25) „Dienst­leistungen nur als Wertartikel“ kann
erreicht werden, dass Dienstleistungen aus­schließlich wertmäßig gebucht
werden können; für die normale Warenerfassung bleibt der Artikel gesperrt.
Leergut:
Hiermit wird der Artikel als Leergut
gekennzeichnet. Dies ist Voraus­setzung für den Druck von Nachweisen beim
Vorgangsdruck und der Führung des Leergutkontos. Näheres dazu im Bereich
„Leergutverwaltung“.
Verpackung
:
Bezug auf Hauptartikel
:
Dieser Parameter ist in Verbindung mit der Option
Folgeartikel und bei eingerichteten Gruppenzu-/abschlägen und Gruppenrabatten
aktiv:
So beziehen sich die Gruppenzuabschläge/Gruppenrabatte
nicht auf den Artikel selbst sondern auf den Hauptartikel der Folgeliste.
Hierüber kann z.B. das Problem von Verlustver­packungen gelöst werden, deren
Erlösschmälerungen direkt auf das Artikelkonto fließen sollen.
Anmerkung für den Formulardruck: Eine
Verlustverpackung innerhalb einer Folgeartikelliste bekommt die Artikelvariante
308.
Muster – diverse
: Z.Z. nicht aktiv
Saatgutartikel:
In Zusammenhang mit dem Modul Saatgut wird hier
festgelegt, ob es sich um einen Saatgutartikel handelt. Danach sind dann
Fruchtart und Sorte festzule­gen. Näheres hierzu im Abschnitt Saatgut.

---

## Hersteller

Hersteller
Hauptmenü
Stammdaten
Hersteller
Direktsprung
[HST]
Hier werden die Daten der Hersteller der Waren, die
sich im Artikelstamm befinden, bearbeitet.
Zu jedem Lieferanten kann es natürlich mehrere
Hersteller geben, oder aber der Hersteller kann auch der Lieferant sein.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Lieferant
Mit der Taste
F3
kann hier eine Auswahl aus dem Kunden/Lieferantenstamm abgerufen
werden. Nach erfolgter Auswahl erfolgt eine Abfrage, ob die Daten in den
Herstellerstamm übernommen werden sollen.
Herstellernummer
Nummer, unter der der Hersteller im System geführt
wird.
Bezeichnung
Freier Text
Kürzel
Matchcode
Kurzbezeichnung des Herstellers.
Anrede
Wie bekannt; mit der Taste
F3
kann eine Auswahl aus Frau, Herr, Firma, Dr., Prof. aufgerufen
werden.
Zusatz
Zusatzfeld für die Anrede.
Straße
Adresse des Herstellers, wird bei entsprechender
obiger Auswahl aus den Stammdaten des Kunden/Lieferantenstammes übernommen.
PLZ- Ort
Postleitzahl des Herstellers; wird bei entsprechender
obiger Auswahl aus den Stammdaten des Kunden/Lieferantenstammes übernommen.
Ortsteil
Wenn der Hersteller in einem Ort seinen Sitz hat, der
über mehrere Ortsteile verfügt, kann hier der Ortsteil des Herstellers
eingegeben werden (z.B. Ortsteil Altona in Hamburg)
Telefon / Fax
Telefonnummer oder Fax kann eingegeben werden oder
wird aus der oben getroffenen Auswahl versorgt.
Adresse Kurz
Kurzfassung der Adresse.
Partner 1,2
Eingabe der/des Ansprechpartner/s in der Firma des
Herstellers.
Auf den Hersteller kann im Artikelstamm im Abschnitt
„Lieferant / Hersteller“ Bezug genommen werden. Weitere Auswertungen bestehen
derzeit nicht.

---

## Hauptwarengruppen / Oberwarengruppen / Warengruppen

Hauptwarengruppen / Oberwarengruppen / Warengruppen
Warengruppen dienen der inhaltlichen Gliederung des
Artikelstamms in Auswer­tun­gen und Selektionen. In Referenz-ERP ist ein
dreistufiges hierarchisches Waren­gruppenkonzept realisiert worden, das
sowohl schrittweise verdichtende oder auf­lösen­de Analysen des
Waren­ge­schäf­tes zulässt, als auch die Betrachtung der
Einzelebenen.
Die Ebenen werden bezeichnet mit:
Hauptwarengruppe
Oberwarengruppe
Warengruppe
Die Beziehungen zwischen den Ebenen sind eindeutig,
d.h., ein Artikel ist eindeutig einer Warengruppe zugeordnet, diese einer
Oberwarengruppe und diese einer Haupt­­warengruppe. Aus dieser Struktur
heraus ergibt sich, dass die Erfassung in der Reihenfolge Hauptwarengruppe,
Oberwarengruppe, Warengruppe erfolgt.
Der Erfassungsablauf ist jeweils
gleich, nur dass bei der Oberwaren- und Waren­gruppenerfassung die jeweils
zugehörige Haupt- bzw. Oberwarengruppe anzugeben ist
Es ist möglich, auf das
Warengruppensystem ganz oder in der Anfangsphase der Installation zu verzichten
(Eintrag WG 0 im Artikelstamm) und später nachzutragen; dementsprechend sind
auch Änderungen möglich.
Ein Beispiel für die Warengruppenstaffelung könnte
sein:
Innerhalb der Warengruppeneingabe / -änderung stehen
nachfolgende Felder zur Verfügung.
Nach Vergabe der Warengruppennummer sind die
Bezeichnung und die Zuordnung zur Oberwarengruppe einzugeben. Die Felder
Raffungsstufe und Summenfortschreibung sind für spätere Erweiterungen
reserviert.
Nach Anlegen des Warengruppenkonzeptes werden die
Warengruppen bei der Artikelstammerfassung den Artikeln zugeordnet.
Maske zur Erfassung / Änderung der
Oberwarengruppe.
Maske zur Erfassung / Änderung der
Hauptwarengruppe.

---

## Import in die Anlagenbuchhaltung

Import in die Anlagenbuchhaltung
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Anlagenstamm importieren
Direktsprung
[ANKAI]
Es ist möglich Anlagengüter in die Anlagenbuchhaltung
aus zu importieren. Vor dem Start des Imports wird geprüft ob Daten in der
Anlagenbuchhaltung existieren. Ist dies der Fall, werden keine Daten
importiert.
Der Anlagenspiegel liefert anschließend den aktuellen
Stand.
Bedeutung
Name
      der Importdatei
Dort
      muss der Name der zu importierenden Datei angegeben werden.
Name
      der Importprozedur
hier
      steht der Name der verwendeten Prozedur. Die Prozedur
      AMIC_ANKA_QUADRIGA_IMPORT wird von Branchen-ERP zur Verfügung gestellt. Sie kann
      jedoch durch eine Private Prozedur ersetzt werden. Dieser Prozedur werden
      zwei Parameter übergeben, das Konto und das Datum der letzten
      AfA:
create procedure
AMIC_ANKA_QUADRIGA_IMPORT(
in
in_AfaKonto
integer
,
in
in_AfaDatum
date
)
begin
.
.
.
AfA-Konto
Dieses Konto wird als AfA-Konto in
      den Stammsatz eingetragen.
Datum letzte AfA
Die
      kumulierte AfA sowie Zugänge und Abgänge werden diesem Datum und der sich
      daraus ergebenden Periode zugeordnet.
Arbeitsschritt
Hier
      werden die Arbeitsschritte, die gerade durchgeführt werden,
      angezeigt.
Als Datengrundlage wird eine Excel-Datei (*.xls)
erwartet. Die Daten werden erst ab Zeile drei eingelesen. Folgenden Spalten
werden ausgewertet:
Spalte
Bedeutung
A
Inventarnummer. Diese muss eindeutig
      sein!
A
B
Bezeichnung des
      Anlagengutes
A
C
Anschaffungsdatum.
D
      (tt.mm.jjjj)
E
Lebensdauer in Jahren.
N
F
Dies
      gibt die AFA-Art wieder. Es werden die Buchstaben „L“ „R“ „S“ „G“ „K“ und
      „D“ ausgewertet.
L,R,S
⇨
Lineare Abschreibung
G
⇨
GWG
K
⇨
Manuelle Abschreibung
D
⇨
Degressive Abschreibung
A
G
Anfangsbestand in Euro. Steht hier
      ein Wert ungleich 0 wird eine Zeile des Typs AHK generiert.
N
      (15,4)
H
Zugänge. Steht hier ein Wert
      ungleich 0, so wird eine Zeile d
[...]


---

## Importumsetzer

Importumsetzer
Hauptmenü
Externe Kommunikation
Stammdatenimport
Importumsetzer [
IMPUM
]
Mit dem Importumsetzer können Kennzeichen von einem
Fremdsystem wie z.B. Terres bequem auf Referenz-ERP Kennzeichen umgeschlüsselt werden.
Dies gilt natürlch auch in die andere Richtung.
Es wird zu jedem Fremdkennzeichen (Eingangsschlüssel)
ein Referenz-ERP Kennzeichen (Umsetzung) innerhalb einer Schlüsselklasse
zugeordnet.
Variante
Import-Umsetzer
In dieser Variante können neue Umschlüsselungen
angelegt werden.
Funktionen: Neu [F8] -  Ändern [F5] -
Löschen [F7
]
Mit der Funktion Neu, Ändern oder Löschen wir die
Maske Import Umsetzer geöffnet.
Maske
Feld
Bedeutung
Schlüsselklasse
In diesem Feld wird die Klasse
      angegeben in dem sich das Umschlüsselungpaar befindet.
Eingangsschlüssel
Der Wert welcher Umgeschlüsselt
      werden soll.
Umsetzung
Zugewiesenner
      Umschlüsselungswert
Info-Text
Informationstext
Besondere
Funktionen
Im Änderfall steht die Funktion
Alle Ändern
[
F5
] zur Verfügung, wenn in der Auswahlliste
mehr als ein Datensatz markiert worden ist. Dies bedeutet, falls die Änderung
gemacht wird, wird dies für alle Datenstätze mitübernommen werden. Des Weiteren
kann mit
Speichern unter…
[
SF9
] eine neue Umsetzung angelegt werden.
Im Löschenfall steht die Löschfunktion
Alle
Lösche [SF7]
zur Verfügung, wenn in der Auswahlliste mehr als ein
Datensatz markiert worden ist. Damit werden alle ausgewählten Datensätze
gelöscht.
Funktion Ändern(Tabellarisch) [SF5]
Diese Funktion steht nur zur Verfügung, wenn in der
Variante „Import-Umsetzer Itemboxzuordnung“ eine Zuordnung zu der
Schlüsselklasse existiert. Die umzuschlüsselnden Werte werden in einer Prozedur
bestimmt. Diese werden in die Maske geladen. Diesen Werten können dann die
Referenz-ERP Kennzeichen zugeordnet werden. Wurde eine Itembox eingerichtet, so kann
der Wert darüber ausgewählt werden. Beim Verlassen der Maske werden die Daten,
die ein Umschlüsselungspaar darstellen abgespeichert.
Variante Import Sch
[...]


---

## Preis Profile

Preis Profile
Der Umfang der vom Preisstapelpfleger gezeigten Daten
kann über ein
Preisprofil
beeinflusst werden. Achtung: in der aktuellen
Ausbaustufe des Preisstapelpflegers können Profile nur in der Kundensicht
verwendet werden – die Artikelsicht verwendet zurzeit noch ein Standard-Profil
ohne weitere Einstellmöglichkeiten. Die Profileinstellungen können aus dem
Anwendungsfenster heraus über mehrere Wege erreicht werden: Mausklick auf einen
Spaltenkopf, Kontextmenü und Auswahl von „Ansicht wechseln“ oder mittels
Funktionstaste F6:
Der Preisprofilpfleger bietet die folgenden
Einstellmöglichkeiten, wobei nicht farblich unterlegte Felder aktuell
veränderbar sind:
Folgende Parameter stehen zur Auswahl:
Feld
Beschreibung
Profilname
Name
      des für den Kunden gespeicherten Profils. Wurde dem Kunden bislang noch
      kein Profil zugeordnet, wird Profil „Standard“ gezeigt.
Kunde
Kundennummer und Bezeichnung des
      Kunden.
Warengruppe von / bis
F3
      Auswahl
Von:
      ab welcher Warengruppe die individuellen Preise bearbeitet werden
      sollen.
Bis:
      bis zu welcher Warengruppe die individuellen Preise bearbeitet werden
      sollen.
Standardeinstellung ist „0“ ohne
      Warengruppe
Lager von / bis
F3
      Auswahl
Von:
      ab welcher Lagernummer sollen Artikel verwendet werden.
Bis:
      bis zu welchem Lager sollen Artikel verwendet werden
Verwendete
      Daten-Prozedur
F3
      Auswahl privater Prozeduren
Die
      Prozedur, welche für das Laden der Daten in die Preisbearbeitungsmaske
      verwendet werden soll.
Standard-Prozedur ist die
      „HoleIndividuellePreiseKunde“.
Kalkulations-Prozedur
F3
      Auswahl privater Prozeduren
Die
      Prozedur, welche eine Preiskalkulation durchführen kann oder
      soll.
Standard-Prozedur ist die
      „Beispiel_Einstieg_IndiPrKalk“.
Button Edit
Bietet die Möglichkeit zum
      Bearbeiten der im Feld
Verwendete Prozedur
angegebenen
      Prozedur.
Kalkulations-Prozedur
F3

[...]


---

## Individuelle Stammdaten

Individuelle Stammdaten

---

## inplausible Gebinde

inplausible Gebinde
Im Pfleger für Mengeneinheiten
[ME]
existiert die Variante „inplausible
Gebinde“. In dieser Variante sind die unkorrekt/unvollständig eingerichteten
Gebinde aufgeführt. Um diese jetzt zu korrigieren (Setzen des Löschkennzeichens
natürlich auch möglich), ist folgendes Vorgehen erforderlich:
Fall 1: Grundmengeneinheit und Ergebnismengeneinheit
sind inkompatibel
Lösung:
man geht ins Feld Ergebnismengeneinheit und führt eine
F3-Box aus → man kann die Ergebnismengeneinheit nur auf eine zur Grundeinheit
kompatible Men­geneinheit setzen
man validiert ohne F3 einfach die
Ergebnismengeneinheit und die Grund­einheit wird automatisch auf die
Grundeinheit der Ergebniseinheit gesetzt
Fall 2: Als Grundmengeneinheit/Ergebnismengeneinheit
ist ein Gebinde eingetragen
Lösung:
Man validiert das Feld Ergebnismengeneinheit und es
wird als Grundeinheit die Grund­einheit des Gebindes eingetragen, das als
Ergebnismengeneinheit eingetragen war. Dann kann man über F3 im Feld
Ergebnismengeneinheit passend zur ge­änderten Grundmengeneinheit auch die
Ergebnismengeneinheit anpassen.
Fall 3: Es ist keine Grundmengeneinheit eingetragen,
aber eine Ergebnismengen­einheit
Lösung:
man validiert das Feld Ergebnismengeneinheit und die
Grundeinheit wird auto­matisch auf die Grundeinheit der Ergebniseinheit
gesetzt
man führt ein F3 auf dem Feld Ergebnismengeneinheit
aus und hat die Wahl aus allen Mengeneinheiten. Wenn diese Wahl vollzogen wurde,
wird die Grundeinheit der gewählten Ergebnismengeneinheit automatisch in die
Grund­einheit des in Bearbeitung befindlichen Gebindes eingetragen
Fall 4: Es ist weder eine Grundmengeneinheit noch eine
Ergebnismengeneinheit ein­getragen
Lösung:
Man kann vorgehen wie bei einer Neuanlage einer
Mengeneinheit.

---

## Informationsmaske für Artikel und Artikelstamm

Informationsmaske für Artikel und
Artikelstamm

---

## inplausible Mengeneinheiten

inplausible Mengeneinheiten
Im Pfleger für Mengeneinheiten
[ME]
existiert die Variante "inplausible
Mengeneinheiten". In diesen Varianten sind die unkorrekt/unvollständig
einge­rich­teten Mengeneinheiten aufgeführt. Um diese jetzt zu
korrigieren (Setzen des Lösch­kennzeichens ist natürlich auch möglich), ist
folgendes Vorgehen erforderlich:
Es reicht, die nicht eingetragene Grundmengeneinheit
über
F5
im Pfleger
nach­zutragen.

---

## Internationale Mengeneinheit (UN)

Internationale Mengeneinheit
(UN)
Diese Mengeneinheiten sind im internationalen
Warenverkehr von der UN definierte Maße. Diese werden u.a. im Modul
openTRANS
-Export
verwendet.
Sie können u.U. nicht immer 1:1 zu einer bestehenden
Mengeneinheit umgerechnet werden. Deshalb ist hier eine Zuweisung der einzelnen
Mengeneinheiten mit Angabe eines Faktors notwendig.
Definition internationale
      Mengeneinheit
UN-Mengeneinheit
Bis
      zu 3-stelliges Kürzel für den internationalen Warenverkehr
Mengeneinheit Referenz-ERP
Mengeneinheit in Referenz-ERP
Faktor UN zu Referenz-ERP
Umrechnungsfaktor zwischen der
      internationalen und der internen Mengeneinheit.
So
      ist z.B. das internationale CMT (Zentimeter) 100fach in der lokalen
      Mengeneinheit „meter“ enthalten.

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

## TSE-Austausch Schritt 5-7

TSE-Austausch Schritt 5-7
TSE-Austausch Schritt 5 TSE aktivieren
Hauptmenü
Barvorgänge
TSE Pflegen
Direktsprung
[TSE]
TSE-Stick aktivieren
Um die TSE hinzufügen, wie folgt vorgehen:
1.
Zum
TSE-Pfleger
[TSE]
navigieren.
2.
Mit
Neu
F8
neue
TSE
mit
Bezeichnung anlegen.
3.
Eine Bezeichnung für die TSE eintragen.
4.
Laufwerkbuchstaben für den neuen Stick eintragen bzw. kontrollieren.
Hinweis!
Der große Vorteil an der
TSE-Implementierung in Referenz-ERP ist, dass die TSE (wenn sie in Windows richtig
eingebunden wurde) direkt erkannt wird.
Für den Fall, dass Sie
mehrere TSE im Betrieb haben und nicht die Richtige erkannt wird, wechseln auf
ein anderes Laufwerk.
5.
Auf
Aktivieren!
klicken.
-> Der TSE-Stick wurde
aktiviert.
TSE-Austausch Schritt 6 TSE Kasse zuweisen
Hauptmenü
Barvorgänge
Kassenverwaltung
Direktsprung:
[KA]
TSE einer Kasse ändern
1.
Zur Kassenverwaltung
[KA]
navigieren.
2.
Neue
TSE-ID
bzw. mit der Auswahl
über
F3
auswählen.
TSE-Austausch Schritt 7
Kasse eröffnen und testen
Hauptmenü
Barvorgänge
Stammdaten
Kasseneröffnung / Kassenabschluss
Die Kasse kann jetzt wie gewohnt eröffnet werden.
Um die Kasse zu eröffnen, wie folgt vorgehen:
1.
Zu Barvorgänge
Stammdaten
Kasseneröffnung / Kassenabschluss
navigieren.
2.
Betreffende Kasse auswählen.
3.
Kasse eröffnen.
4.
Alle Funktionen der Kasse testen.
Zurück

---

## Konstanten der Artikelverwaltung

Konstanten der Artikelverwaltung
Folgende Konstanten stehen in Abhängigkeit vom Einsatz
des Programms zur Verfügung:
Artikelstamm
Artikel
Artikelstamm
Warengruppe
Oberwarengruppe
Hauptwarengruppe
Artikelstapelkorrektur
Artikelstammstapelkorrektur
Fremdeinspielung
      sequentiell
Artikelverpackung
Konstanten
    Artikelstamm
Mengeneinheiten
Mengeneinheitsgruppen
Bonusklasse
Artikelbonussätze
Artikelinfogruppe
Artikelgruppen
Artikelpool
Artikeltextvarianten
Verpackungsgruppen
Bestellgruppe
Ladegruppe
Bewertungsgruppen
Bestandteile
Sekundärschlüsselgruppe
Textbausteine

---

## Kontraktengagement

Kontraktengagement
Hauptmenü
Kontraktverwaltung
Kontraktengagement
Es gibt hier zwei verschiedene Sichtweisen:
-
Position gruppiert nach Warengruppen
-
Position gruppiert nach Artikelnummern (lagerübergreifend)

---

## Kostenobjekte

Kostenobjekte
Hauptmenü
Kostenrechnung
Kostenobjektstamm
Kostenobjekte
Direktsprung
[KSOBJ]
Neben den
Kostenstellen
und
Kostenträgern
können Kosten einem Kostenobjekt
zugeordnet werden. Diese unterscheiden sich in folgenden Punkten von den
Kostenstellen  und Kostenträgern:
•
Es existiert nicht die Möglichkeit der Verteilung. Es gibt weder
Verteilkostenobjekte für die automatische Verteilung noch existiert bei der
Erfassung die Möglichkeit den Betrag einer Position auf verschiedene
Kostenobjekte aufzuteilen.
•
Zu Kostenobjekten existiert – im Gegensatz zur Kostenstellen und
Kostenträgern - keine Tabelle, in der die Summen geführt werden. Diese können
direkt aus der View AMIC_V_FIBUBELEG gelesen werden.
•
Die Kostenobjekte sind für individuelle Auswertungen von Referenz-ERP Anwendern
gedacht. Daher existieren keine Standard-Auswertungen.
Für Kostenobjekte wird eine Lizenz benötigt.
Felder der
Kostenobjekte
Feld
Nummer
Die
      Nummer des Kostenobjektes.
Matchcode
Die
      Kurzbezeichnung des Kostenobjektes.
Bezeichnung
Die
      Bezeichnung des Kostenobjektes.
Gesperrt
Gibt
      an, ob das Kostenobjekt für die Belegerfassung in der Finanzbuchhaltung
      gesperrt ist.
Suchmöglichkeiten
der Kostenobjekte
Feld
Nummer
Von
      … Bis …
Funktionen in der
Auswahlliste
Funktion
Ändern
(F5)
Ändern des
      Kostenobjektes.
Ansehen
(F6)
Ansehen des
      Kostenobjektes.
Löschen
(F7)
Mit
      der
Löschen
-Funktion werden
      Kostenobjekte nicht physikalisch gelöscht, sondern sie werden mit einem
      Löschkennzeichen versehen. Gelöschte Kostenobjekte sind für weitere
      Belegerfassungen gesperrt bis sie wiederhergestellt werden.
Alle
      gelöschten Kostenobjekte werden in der 2.Variante „Gelöschte
      Kostenobjekte“ angezeigt.
Bedingung: Bevor ein Kostenobjekt
      gelöscht werden kann, wird überprüft, ob dieses noch verwendet wird.
      Solange Einträge des Kostenobjektes in den folgenden Punkten vorhanden
      sind, kann die Löschung n
[...]


---

## Kostenobjekte: Pfleger

Kostenobjekte: Pfleger
Felder des Kostenobjekt-Pflegers
Feld
Nummer
Die
      Nummer des Kostenobjektes.
Ein
      Kostenobjekt mit der Nummer „0“ wird ausgeliefert. Es wird jedoch nicht
      als Kostenobjekt ausgewertet, denn „0“ bedeutet immer „kein
      Kostenobjekt“.
Wurde in der allgemeinen
      Nummernkreiszuordnung
[MNDNK]
den Kostenobjekten ein Nummernkreis zugeordnet, so findet hier nach
      der Eingabe der Kostenobjekt-Nummer eine Bereichsüberprüfung
      statt.
Bezeichnung
Die
      Bezeichnung des Kostenobjektes.
Ist
      der SPA 34 (Mehrsprachigkeit aktiv) gesetzt, so kann hier mithilfe der
F3
-Taste eine
sprachabhängige
      Bezeichnung
eingepflegt werden.
Matchcode
Die
      Kurzbezeichnung des Kostenobjektes.
Im
Neu
-Fall wird der Matchcode
      nach dem Setzen der Bezeichnung mit den ersten 20 Zeichen der Bezeichnung
      vorbelegt, solange kein Matchcode eingetragen war.
Erfassungssperre
Diese Sperre gilt für die
      Belegerfassung in der Finanzbuchhaltung. Steht diese auf
Ja
, so kann das Kostenobjekt dort
      nicht mehr verwendet werden.
Bedingung: Die Erfassungssperre kann
      auf
Ja
gesetzt werden, wenn
      kein Eintrag für das Kostenobjekt im
Sachkontenstamm
existiert.
      Existiert ein Eintrag, so muss zunächst das Kostenobjekt aus den
      entsprechenden Sachkonten entfernt werden, um die Erfassungssperre auf
Ja
setzen zu
      können.
Bemerkung
Hier
      kann ein wahlfreier Text zu dem jeweiligen Kostenobjekt erfasst
      werden.
Mit
      einem
Doppelklick
auf das
      Bemerkungs-Feld öffnet sich der Text-Editor.

---

## Artikelmengen

Artikelmengen
Diese Maske steht nur für kontrakte mit mehreren
Zeiträumen zur Verfügung.
Im oberen Bereich der Maske werden allgemeine Angaben
dargestellt:
•
Kontraktklasse
•
Kontraktgruppe
•
Hauptkunde
•
Kontraktnummer
•
Artikelnummer
Die Datentabelle weist für den Artikel die Mengen und
die aktuellen Restmengen aller Kontrakt-Zeiträume des Artikels aus. Bei
Einzelmengen-Kontrakten sind die Sollmengen in dieser Tabelle änderbar.
Änderungen von Soll-Mengen werden in einem
Änderungsprotokoll dokumentiert.
Zu Kontroll-Zwecken werden im unteren Bereich der
Maske die aktuelle Gesamtsumme, die Restsumme und die ursprüngliche Gesamtsumme
und Restsumme (vor Beginn der Kontraktänderung) sowie die jeweiligen Differenzen
ausgewiesen.
Feld
Beschreibung
Zeitraum
Beginn des
      Kontraktmengen-Zeitraums
Gesamtmenge
Sollmenge des Artikels im
      Kontrakt-Zeitraum.
Bei Gesamtmengen-Kontrakten wird hier die gesamte
      Sollmenge des Kontrakt-Zeitraums dargestellt.
Bei Freimengen-Kontrakten
      ist die Sollmenge immer mit 0 dargestellt.
Restmenge
Aktuelle Restmenge des Artikels im
      Kontrakt-Zeitraum
Bei Gesamtmengen-Kontrakten wird hier die gesamte
      Restmenge des Kontrakt-Zeitraums dargestellt.
Bei Freimengen-Kontrakten
      ist die Restmenge immer mit 0 dargestellt.
Rest>0
Negativer Rest wird mit 0
      dargestellt, aktueller Rest ist um negativen Rest des vorhergehenden
      Zeitraums reduziert.
(Nur bei eingestellter Option
Steuerungsparameter
846
      „Ratierliche Einstellungen“ „Ktr-Anzeige Minusrest in
      Folgezeitraum“
mit dem Wert
Ja
).
Rest
      kumuliert
Summe der Werte aus vorhergehender
      Restspalte (Restmenge, Rest>0) bis einschließlich dem aktuellen
      Zeitraum
(Nur bei eingestellter Option
Steuerungsparameter
846
      „Ratierliche Einstellungen“ „Ktr-Anzeige Kumulierte
      Zeitraum-Reste“
mit dem Wert
Ja
).

---

## Kundenindividuelle Artikelnummern

Kundenindividuelle Artikelnummern
Wenn für bestimmte Abnehmer eigene Artikelnummern
hinterlegt werden, so können diese hier gepflegt werden. Diese Nummern können im
Vorgang z.B. mit ausgedruckt werden.

---

## Bedienerstamm: Pfleger

Bedienerstamm: Pfleger
Dieser Pfleger dient zur Änderung und Erstellung von
Bedienern
Kopfdaten:
Kopfdaten
Nummer
Bedienernummer. Diese wird händisch
      vergeben und muss eindeutig sein.
Kurzname
Eindeutiger Login–Name beim
      Programmstart.
Status
Aktiv
: Bediener ist im Bedienerstamm und
      in der Datenbank angelegt. Mit diesem Bediener ist  eine
      Referenz-ERP-Anmeldung möglich.
Inaktiv
: Bediener ist im Bedienerstamm und
      in der Datenbank angelegt. Jedoch ist eine Referenz-ERP-Anmeldung nicht
      möglich.
Gelöscht
: Bediener ist nur noch im
      Bedienerstamm aber nicht mehr in der Datenbank. Eine Referenz-ERP-Anmeldung ist
      nicht möglich.
Neu
: Neuanlage des Bedieners. Nach dem
      Speichern wird dieser auf aktiv gesetzt.
Register:
Allgemein
Allgemein
Bedienerklasse
F3
Zuordnung einer übergeordneten
      Abteilung; der Bediener erhält damit die Rechte der
Bedienerklasse
.
Betriebsstätte
Betriebsstätte des Bedieners, so wie
      er auf Listen und Ausdrucken erscheint.
Name
Name
      des Bedieners.
Name
      extern
Für
      Listen, Ausdrucke, etc.
Windows Login
Ein
      in einem Windows Umfeld gestartetes Referenz-ERP fragt bisher immer noch einmal
      Bedienername und Kennwort ab, obwohl ja schon bei der Windows Anmeldung
      alle notwendigen Sicherheitsüberprüfungen abgewickelt worden
      sind.
Durch das einfache Setzen der Feldes
      „Windows Login“ innerhalb des Bedienerstammes auf den Windows – Kontonamen
      (also den Windows Anmeldenamen) des entsprechenden Bedieners kann jetzt
      erreicht werden, dass dieser angemeldete Windows Bediener direkt auf den
      entsprechenden Referenz-ERP Bediener innerhalb von Referenz-ERP angemeldet wird, wenn
      Referenz-ERP gestartet wird. Es gibt nur eine 1 zu 1 Zuordnung zwischen einem
      Windows Benutzer und einem Referenz-ERP Bediener.
Bei
      dieser Verwendung der Windows Authentifizierung wird Referenz-ERP sofort
      durchgestartet. Die Referenz-ERP Anmeldung müssen Sie in jedem Fall dann

[...]


---

## Labormethoden

Labormethoden
Hauptmenü
Saatzucht
Saatenlabor
Methoden
oder Direktsprung
[LABME]
In diesem Stammdatenpfleger werden die Labormethoden
gepflegt. Labormethoden dienen dazu, verschieden Laborverfahren zusammenzufassen
um.
Name
Bedeutung
Nummer
Eindeutige Nummer dieser Methode,
      wie sie in den Labordaten verwendet wird.
Bezeichnung
Die
      Methodenbezeichnung
Fruchtart
Zweck (Probentyp)
Hier
      wird die Norm angezeigt. Aus dem Format „AF_QUALART“
kann
eine Auswahl
via Taste
F3
aufgerufen
      werden
.
Ist
      hier der Einrichterparameter ‚Methodenauswahl auf Probentyp eingeschränkt‘
      der Labordaten-Maske (Probensatzbearbeitung) mit dem Wert ‚Ja‘ versehen,
      so wird die Methodenauswahl im LABOR-Modul bei der Erstellung eines
      Probensatzes nach dem dort angegebenen Probentyp (Satzart, Zweck)
      eingeschränkt.
Nummernkreis
Die
      Nummer des Nummernkreis, der für die Vergabe der Probenummer in den
      Labordaten verwendet wird.
Verfahren (Grid)
Hier
      werden alle
Verfahren
die zu einer Methode gehören
      eingetragen. Die Verfahren werden einer Probe im Labor zugeordnet, sobald
      die Methode ausgewählt wurde.
Folgende Felder werden zusätzlich angezeigt, sobald
der Einrichterparameter „
Erweiterte Einstellungen
“ auf „Ja“ gestellt
wird.
Name
Bedeutung
Norm
Hier
      wird die Norm angezeigt. Aus dem Format „BF_QUALKL“
kann
eine Auswahl
mit
F3
aufgerufen
      werden
.
Ist
      hier ein Eintrag vorhanden, so wird die Methodenauswahl im LABOR-Modul bei
      der Erstellung eines Probensatzes nach der dort angegebenen Norm
      eingeschränkt.
Kategorie
Hier
      wird die Kategorie angezeigt. Aus dem Saatgutstammdatenbereich Kategorien
      kann mit
F3
eine Auswahl
      aufgerufen werden
.
Ist
      hier ein Eintrag vorhanden, so wird die Methodenauswahl im LABOR-Modul bei
      der Erstellung eines Probensatzes nach der dort angegebenen Kategorie
      eingeschränkt, wenn diese größer 0 ist.
Anbauart
[...]


---

## Ladegruppen

Ladegruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Ladegruppen
oder Direktsprung
[LDG]
Jedem Artikel kann eine Ladegruppe im Einkauf sowie im
Verkauf zugeordnet werden.
Eine Bedeutung der Ladegruppe kann sich durch
Gruppierungen in individuellen Artikel-Auswahllisten ergeben.

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

## Materialorder [LVSMO]

Materialorder [LVSMO]
Es gibt zwei Arten der Materialorder.
1.
Vorgangsgebundene Materialordern
Diese Materialordern bilden
1:1 einen Vorgang und dessen Materialbedarf ab. Artikel und Partien befinden
sich nebst den Referenzen zu den Vorgangspositionen in dieser Materialorder.
2.
Ungebundene Materialordern
Diese Materialordern werden
manuell oder über die Produktionsschnittstellle erstellt und enthalten in der
Regel keine Referenzen auf Vorgangspositionen. Sie lassen sich mit dem
Materialorder-Pfleger [LVSMO] erstellen.
Kopfdaten
Feld
Beschreibung
Nummer
Wird
      automatisch vom System vergeben
Ziel
Hier
      kann eine LVS-Lokalität ausgewählt werden (nicht empfohlen).
Linie
Auswahl einer Produktionslinie – In
      diesem Fall wird „ziel“ deaktiviert und mit dem Bereitstellungsbereich der
      Produktionslinie belegt.
Es ist zu empfehlen, die EPA-Einstellung „Linie als
Default-Quelle“ auf „ja“ eingestellt zu lassen. In diesem Fall wird der Cursor
bei Start dieser Maske sofort in das Feld „Linie“ gesetzt.
Zeilendaten
Wert
Anzeige
Beschreibung
Liste
Ja
ListenNr
Position
Ja
Laufende Positionsnummer
Artikel
Nein
Artikelnummer aus dem Lager der im
      Kopf gewählten Lokalität
Artikelbezeichnung
Ja
Bezeichnung des Artikels
Partie
Nein
Partienummer
Partiebezeichnung
Ja
Bezeichnung der Partie
Menge/Anzahl
Ja
ME
Nein
Mengeneinheit. Hier sollte eine
      LVS-Mengeneinheit gegeben werden. In der EPA-Einstellung „Mengeneinheit
      aus“ sollte LVS stehen.
Bezeichnung
      Mengeneinheit
Ja

---

## Makro-Pfleger

Makro-Pfleger
Der Makro-Pfleger ermöglicht Ansehen, Bearbeiten,
Löschen und Neuanlage eines Makro-Programmes.
Über „F8“ neu-angelegte Makro-Programme erhalten
automatisch:
1)
den Besitzer Privat“
2)
wird ihnen ein syntaktisch richtiger Makro-Text zugeordnet. Dieser Makro-Text
kann dann weiterverarbeitet werden.
Felder
Makroname
„Bezeichner“ des Makros. Über diesen
      Identifier werden Makros gestartet.
Typ
ID
Informatorisch die interne
      Identifikations-ID (diese ID ist mit dem Besitzer systemweit
      eindeutig)
Parameter 1
Im
      Pfleger vorgebbare Parameter
Parameter 2
Parameter 3
Parameter 4
Resultat
Optionale Ergebnis-Rückgabe des
      Makro-Programmes
Debugger
Status eines ggf. verbundenen
      „Debugger“ (Extra-Software zum Überprüfen von
      Laufzeitverhalten)
Vorgang, Zähler,
      Datensatz
Weitere optionale Ergebnis-Rückgaben
      des Makro-Programmes.
Scriptausgaben
Weitere optionale
      Laufzeit-Mitteilungen des Makro-Programmes.
Neben den Pflegerfunktionen „Speichern“, „Neu“ usw.
sind noch folgende Funktion möglich:
Funktionen
aus Datei laden
Lädt
      aus einer angebbaren *.pas-Datei den ASCII-Text als
      Makro-Programm-Text.
übersetzen
Kompiliert den zugeordneten
      Makro-Programm-Text in eine durch Referenz-ERP ausführbare
      Informationseinheit.
Script
      vergleichen
Version speichern
Version
      wiederherstellen
Editor aufrufen
Ruft
      den einstellbaren Editor zum Bearbeiten des Makro-Programm-Textes
      auf.
ausführen
Führt das Makro-Programm mit den
      unter Parameter 1-4 angegebenen Parametern aus dem Pfleger heraus
      aus.
Debugger
      umschalten
Debugger
      aktualisieren
Fehlermeldungen
Die
      Funktion „übersetzen“ kann feststellen das es syntaktische Probleme mit
      dem Makro-Programm-Text gibt. Mit dieser Funktion werden detaillierte
      Hinweise abgerufen um die Möglichkeit zu bekommen, die Probleme zu
      beheben.
SQL-Auslagerung
Schreibt ein Sql-Skrip
[...]


---

## Folgeartikel in der Marktkasse

Folgeartikel in der Marktkasse
In
der Marktkasse können Folgeartikel (außer Leergut) automatisch zugeordnet
werden. Hierfür werden die Methoden der normalen Warenerfassung herangezogen.
Bei eventuellen Eingriffen über Makro oder ähnlichen externe Methoden können
nicht automatisierbare Behandlungen zu Störungen im Ablauf führen.
Dieses
Verhalten ist mit dem Steuerparameter "Folgeartikel automatisch erfassen" zu
aktivieren.

---

## Leergutverarbeitung in der Marktkasse

Leergutverarbeitung in der Marktkasse
Wird Leergut als
Folgeartikel
eines Artikels eingerichtet,
so fällt bei der Erfassung in der Marktkasse auf, dass der Leergutartikel
zunächst nicht angezeigt wird.
Leergutartikel dürfen nur am Ende der Erfassung
zusammenfassend erfolgen. Zu diesem Zweck wird die Leergutmaske geöffnet und es
wird eine Liste der Leergutartikel angezeigt.
Dabei gibt es drei Einstellungen in der
Formularzuordnung auf der Registerkarte
Kasse
. Hier kann im Feld „Leergutverarbeitung“ festgelegt werden, ob nur die
Leergutartikel der fakturierten Artikel oder alle Leergutartikel des Lagers
angezeigt werden sollen.
Die Menge des Leergutartikels wird aus der Menge des
fakturierten Artikels und der Berechnungsformel für den Folgeartikel berechnet
und vorgeschlagen. Abweichungen können dann im Leergutdialog eingegeben
werden.
Der Button „Verwerfen“ ermöglicht es die offenen
Leerguteingaben zu ignorieren. Dadurch ist es möglich die Zahlung auszulösen,
ohne vorher offenen Leerguteingabe zu bestätigen.
Hinweis:
Es ist notwendig, Leergutabweichungen am Ende der
Erfassung einzugeben, da bei jedem Aufruf des Leergutdialogs, dieser mit den
Grundberechnungen gefüllt wird und bisherige Eingaben gelöscht werden. Es werden
ebenfalls alle über den Leergutdialog erfassten Leergutartikel gelöscht. Vor
Beginn der Zahlung werden offene Leerguteingaben ohnehin eingefordert.

---

## Fremdwährungszahlung

Fremdwährungszahlung
Haben Sie Fremdwährung gewählt, so wird das
Eingabefeld der Zahlwährung aktiviert. Sie können hier aus dem Währungsstamm
eine Währung auswählen oder das Währungskürzel (z.B. DKK für dänische Kronen)
über eine Tastatur eingeben oder die Nummer der Währung im Währungsstamm über
die Touch-Tasten eingeben.
Es gibt die Möglichkeit bei der Einrichtung eines
Funktions-Buttons in AIS einen Funktionscode einzutragen, der die Fremdwährung
enthält. In diesem Fall entfällt die Eingabe der Währung. Es erfolgt sofort die
Aktivierung des Eingabefeldes. Das kann besonders nützlich sein, wenn es ohnehin
nur eine akzeptierte Fremdwährung in einer Grenzregion gibt.
Bei Aktivierung des Betragsfeldes wird dieser Betrag
wenn gewünscht vorbelegt. Bei Fremdwährung wird der Betrag in der aktiven
Zahlwährung vorbelegt. Der Betrag kann durch Eingaben über die Touch-Tastatur
überschrieben werden.

---

## Mengeneinheit als Grundeinheit (Grundmengeneinheit)

Mengeneinheit als Grundeinheit (
Grundmengeneinheit
)
Die Grundeinheit ist die einfachste Form einer
Mengeneinheit. Wenn in einem Unternehmen keine Umrechnungen erforderlich werden,
dann sind auch nur diese Grundeinheiten zu erfassen.
Ein typisches Beispiel hierfür sind Artikel, die in
der Einheit Stück eingekauft und verkauft werden, deren Lagerbestand in Stück
geführt wird und deren Preis in Ein- und Verkauf sich auf die Einheit Stück
bezieht. Hier gibt es also nur den Fall Mengeneinheit = Grundeinheit.
In der Grundversion von Referenz-ERP werden die gängigsten
Mengeneinheiten, wie Stück, Liter, kg, etc. eingerichtet als Grundeinheit mit
ausgeliefert. Falls im konkreten Fall keine weiteren Mengeneinheiten benötigt
werden, kann auf die Erfassung verzichtet werden.
Für die Anlage der (Grund
-) Mengeneinheiten werden praktisch lediglich die Texte der gepflegt, also kg,
Ltr., Stück usw.. Es sind dies die jeweils kleinsten, nicht mehr teilbaren,
Mengeneinheiten des Systems. Häufig sind es ohnehin nur diese Einheiten mit
denen in einem Unternehmen gearbeitet wird. Wenn nämlich mit konstanten
Mengenbezügen (Einkaufs-/Verkaufs-/Preiseinheit identisch) und ohne Gebinde
gearbeitet wird sind keine Umrechnungen erforderlich und es genügt die Erfassung
der Grundeinheiten:
Folgende Felder stehen hier zu Erfassung.
Grundmengeneinheit –
      Felder
Nummer
Nummer der zu definierenden
      Mengeneinheit. Die Eingabe der Nummern ist aus technischen Gründen auf 4
      Stellen begrenzt
Kurztext
Kurzbezeichnung der Mengeneinheit,
      wie sie ausgedruckt werden sollen; also z.B. kg, Stück, Ltr.
      etc.
ISO
      Name
Langtext
Langtext, welcher anstelle des
      Kurztext ausgedruckt werden kann
Bezeichnung
Ausführliche Bezeichnung der
      Mengeneinheit, z. B. für Auswahllisten
DataNormKurz
Die
      Kurzbezeichnung des DataNorm Verfahrens. Erforderlich, wenn Datenaustausch
      mit anderen Unternehmen auf Grundlage dieses Verfahrens erfolgen
      soll.
St
[...]


---

## Mengeneinheiten — Übersicht

Mengeneinheiten — Übersicht
Die Mengeneinheiten im Referenz-ERP System spielen eine
entscheidende Rolle bei der Festlegung und der Arbeitsweise mit Artikeln. Dieser
Bereich sollte sehr genau vor Anlage des ersten Artikels durchgearbeitet werden,
um nicht schon in den Grundstrukturen mögliche Stolpersteine einzubauen.

---

## Mengeneinheiten

Mengeneinheiten
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Mengeneinheiten
oder Direktsprung
[ME]
Mit der Mengeneinheit wird bestimmt, welche
Mengengrundlage bei Einkauf, Verkauf, Lager, etc. zugrunde gelegt wird.
Hierbei kann es sich um einen einfache Einheit mit
Text, z.B.
kg
,
Stück
oder auch um eine komplexe Rechenformel
handeln, wenn zur Mengenermittlung eine Gebindeberechnung zugrunde gelegt werden
soll.
Im häufigen Fall, wenn z.B. Reifen in Stück eingekauft
und verkauft werden, die Bestände in Stück geführt werden sollen und der
Preisbezug
Stück
ist, genügt die Eintragung
Stück
für die Mengenbezüge im
Artikelstamm.
Aufwändiger ist jedoch folgendes Beispiel: Wenn z.B.
Kartoffeln in
kg
eingekauft werden, sie in verschiedenen
Verpackungsgrößen verkauft werden (z.B. in 25 kg und 50 kg Säcken), der
Einkaufpreis sich auf
100 kg
bezieht, der Verkaufspreis sich auf die
Verpackungsgröße
bezieht und der Bestand in
kg
geführt wird,
müssen Umrechnungsformeln zwischen den verschiedenen Mengenbezügen eingeführt
werden.
Die hier vorliegende Form der
Mengeneinheitendefinition ermöglicht die automatische Umrechnung der
verschiedenen Größenklassen.
Im Programm wird dabei unterschieden zwischen
Mengeneinheitengruppen
, die im Artikelstamm eingetragen werden und steuern,
auf welcher (Mengeneinheiten-) Grundlage die Mengenberechnung im Einkauf,
Verkauf, der Bestandsführung und der Preisfindung erfolgt. Hier wird also nur
Bezug genommen auf die im Bereich "Mengeneinheiten" festgelegten
Umrechnungsschlüssel. In einer Mengeneinheitsgruppe werden also (möglicherweise)
unterschiedliche Mengeneinheiten für die Abwicklung des Artikels in Ein- und
Verkauf zusammengefasst.
Mengeneinheiten
, in denen die Daten für die
Ermittlung der jeweiligen Mengen festgelegt sind. Dies sind Formeln (z.B. Länge
x Breite x Höhe) und Faktoren (z.B. Karton mit
6
Flaschen).
Mengengrundeinheiten
, in denen bestimmt wird,
auf welche Einheiten zurückgerechnet wird. Hierbei handelt
[...]


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

## Abwicklung

Abwicklung
Behandlung auf einem
Artikelkonto
•
Nachhaltige und nicht nachhaltige Ware wird auf einem Artikelkonto
geführt
•
Das Nachhaltigkeitskennzeichen j/n wird je Warenbewegung mitgeführt
•
Je Warenbewegung werden die individuellen (Teil-) Standardwerte geführt,
wenn sie über Stammdaten bzw. individuell je Bewegung erfasst, werden
Erfassungsunterstützung
•
Ausgegangen wird davon, dass über die eingetragenen Stammdaten eine
weitgehende Automatisierung durchgeführt werden kann.
•
Für den Sonderfall sind individuelle Eingaben möglich
•
Eine Nachbearbeitung ist möglich
•
Abweichungen vom „Standard“ werden ausgewiesen
•
Die Zuordnung des Merkmals „Nachhaltigkeit“ erfolgt mit der physischen
Bewegung
Die Bearbeitung im Ein- und Verkauf (Funktionen ELE
und LIE) erfolgt auf der Erfassungsmaske Eingangslieferschein und Lieferschein
über den Tabreiter „Nachhaltig“ zur Übersteuerung der Defaultwerte.
Bei Rohwarevorgängen erfolgt die Bearbeitung
Nachhaltigkeitsangaben direkt auf der Bearbeitungsmaske entsprechend der
Einstellungen der zugehörigen Rohwarenparameter.
Interne Warenbewegungen
Lagerumbuchungen, Artikelumbuchungen und
Produktionsumbuchungen werden ebenfalls über o.a. Tabreiter „Nachhaltig“ mit dem
Kennzeichen versorgt. Vorbelegt werden die Umbuchungen über die Systematik
„Eintragung im Mandantenstamm“ und „Artikelstamm“, also als „nachhaltig“. Nicht
nachhaltige Umbuchungen sind also (wie auch oben) zu kennzeichnen.
Online Waage
Bei der Erfassung über die online Waage wird immer
davon ausgegangen, dass die Standardvorbelegungen ziehen. Änderungen sind im
Einzelfall entsprechend der Beschreibung in Abschnitt 4 vorzunehmen.
Abwicklung im Verkauf
Prinzipiell kann nachhaltige und nicht nachhaltige
Ware gehandelt werden. Kunden, für die die Vorbelegung „nachhaltige Ware“
aktiviert werden soll, sind also wie unter „
Kunden /
Mandant
“ beschrieben zu behandeln.
Berücksichtigung eigener Ware und
Fremdware
Differenzierung auf dem Artikelkonto je
Warenbew
[...]


---

## Stammdaten

Stammdaten
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Die Pflege der Stammdaten erfolgt in
unterschiedlichsten Bereichen von Referenz-ERP. Folgend eine Liste, die zu den
einzelnen Bereichen führt.
Faktor / THG-Wert
/ Anbauland
Artikelstamm
Kundenstamm
Mandantenstamm
Kontrakt
Massebilanz
Spezielle
Auswahllisten
Formate
Hinweis
Zu beachten ist, dass die Bearbeitung der Stammdaten
teilweise einige Zeit in Anspruch nehmen kann. Das liegt daran, dass eine
Nachkalkulation der Werte durch den
Mandantenserver
erfolgen muss.

---

## Nummernkreise für Ware und FiBu

Nummernkreise für Ware und FiBu
Hauptmenü
Administration
Nummernkreise
Oder Direktsprung:
[NKS]
Unter dem einheitlichen Dach des Nummernkreispflegers
sind zwei grundsätzliche Funktionen vereint:
Festlegung und Kontrolle von Nummernkreisen für
Stammdaten und Belege
(z.B. Kunden zwischen 10000 und 69999; siehe Eintrag
im Mandantenstamm
[MND]
)
Bereitstellung der nächsten Beleg- oder
Stammdatennummer bei der Beleg- bzw. Vorgangserfassung
Für alle Bereiche in Referenz-ERP liegen in der
Auslieferungsversion eingerichtete Nummernkreise vor. In Abhängigkeit von den
betrieblichen Organisationsformen können jedoch Anpassungen und Erweiterungen
erforderlich werden, z.B.:
•
Unterschiedliche Nummernkreise je Standort
•
Vorgangsunterklassen („die Heizölrechnung“) je Sparte mit jeweils eigenen
Nummernkreisen

---

## Parameter der Bonusabwicklung

Parameter der Bonusabwicklung
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Bonusgruppen / Bonusklassen /
Artikel-Bonus-Sätze
Referenz-ERP ist auf die Umsetzung von Bonusabrechnungen
vorbereitet. Die Stammdaten werden innerhalb der Artikelkonstanten verwaltet. Es
handelt sich dabei um:
•
Bonusgruppen
[BOG]
, die die
Zuordnung der Artikel bestimmen
•
Bonusklassen
[BOKL]
, die die
Zuordnung der Kunden bestimmen
•
Bonussätze
[ARBO]
, die das
Abrechnungsverfahren bestimmen
Z.Z. sind weitergehende Abwicklungsverfahren nicht
implementiert; nachfolgend wird deshalb lediglich das vorgesehen Verfahren
beschrieben.
Innerhalb von Referenz-ERP können Kunden Bonusklassen
zugeordnet werden. Hierbei kann es "beliebig" viele Bonusklassen geben, denen
die Kunden für die Bonusermittlung zugeordnet werden.
Diese Bonusklassen können mit einem Sperrkennzeichen
versehen werden, das (temporär) den Bonus für alle Kunden bzw. Lieferanten der
Bonusklasse sperrt.
Hierzu müssen folgende Felder erfasst werden.
Bonusklasse:
Identifikation der Bonusklasse.
Bezeichnung:
Bezeichnung der Bonusklasse für Auswahllisten etc.
Sperrkennzeichen:
Sperrkennzeichen, das (temporär) den Bonus für alle
Kunden bzw. Lieferanten der Bonusklasse sperrt.
Die Artikel werden Bonusgruppen zugeordnet:
Ebenso können die Boni nach Zeiträumen der Gültigkeit
erfasst werden.
Im Eingabebildschirm zum Artikelbonussatz können die
nachfolgenden Felder bearbeitet werden.
Bonusklasse:
Identifikation Nummer und Text der Bonusklasse der
Bonusklasse
Bonusgruppe:
Identifikation der Bonusgruppe.
Ab Datum:
Erster Tag der Gültigkeit. Datum auf das die Einträge
bezogen sind
Bis Datum:
Letzter Tag der Gültigkeit.
Formel:
Art und Weise, wie sich der Bonusbetrag
errechnet:
1 = prozentual vom Warenwert abzüglich Rabatte
2 = prozentual vom reinen Warenwert
11 = Rabattsatz je Mengeneinheit
12 = Rabattsatz je Grundeinheit
Prozent:
Bonussatz bei prozentualer Berechnung.
Preis:
Beschreibung Bonussatz bei preisähnlicher
Bonusermittlung

---

## Parameter des Artikelstamms

Parameter des Artikelstamms
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikelstamm
oder Direktsprung
[ARS]
In den Artikelstammdaten werden alle Informationen
über einen Artikel zusammen­ge­fasst, auf die für eine weitgehend
automatisierte Verarbeitung zugegriffen werden muss. Dies sind z.B.
Mengeneinheiten, Preise,
Gebindegröße etc.
Da zur Verein­fachung der Erfassung bei
der Anlage eines Artikels auf vorerfasste Informationen zugegriffen wird, müssen
diese natürlich vorhanden sein. So wird sicherlich häufig die Mengeneinheit
"Stück"
benötigt. Diese muss also zuvor in der Tabelle
"Men­geneinheiten"
erfasst werden.
Vor der Erfassung der Artikel- und Kundenstammdaten
genauso wie der Finanz­buch­haltungskonten, müssen also verschiedene
Konstanten eingegeben, da auf sie bei der Stammdatenerfassung zugegriffen wird.
Darüber hinaus können weitere Kon­stanten in Abhängigkeit von der Anwendung
hinzu­kommen. So sind die Gefahr­gut­kennzeichen zu erfassen, wenn
die Gefahr­gutabwicklung aktiviert werden muss.
Im Artikelstamm werden nur diejenigen Daten eines
Artikels vermerkt, die ent­weder völlig lagerunabhängig sind, das sind
globale Dinge wie Gefahrgut, Ge­binde­größen, Mengeneinheiten usw., oder
häufig globalen Charakter haben.
Dies sind z.B. die Gruppierungs- oder
Statistikkennzeichen. Im letzten Fall werden im Artikelstamm also Vorbelegungen
vorgenommen, die ggf. jedoch in der Ausprägung überschrieben werden können.
Alles, was in verschiedenen Lagern unterschiedlich
sein
KÖNNTE
, muss im Artikel
hinterlegt werden!
Folgende Felder stehen zur Verfügung:
Feld
Bedeutung
Artikelstammnummer
Dies
      ist die logische, also für den Anwender sichtbare und durch ihn zu
      pflegende, Artikelstamm-Identifikation.
Je nach Auslegung des Systems
      handelt es sich hierbei um einen alphanumerischen oder numerischen
      Schlüssel.
Auf Organisationsprinzipien zur Vergabe von Artikelnummern
      wird an anderer Stelle eingegangen.
Wichtig ist hier jedoch, das
[...]


---

## Partieetiketten

Partieetiketten
Auswahlliste
Felder
Artikel-Nummer
Artikelstamm-Nummer
Nummer
Partienummer, vom Benutzer vergebene
      Identifikation der Partie
Anerkennung
Anerkennungsnummer
Code
Fruchtart
Bezeichnung der
      Fruchtart
Botanisch
Botanische Bezeichnung
Sorte
Saatsorte
Probenahme
Datum der Probenahme
Attest
Datum
KF
Keimfähigkeit
TKG
Tausendkorngewicht
PID
Partie-ID
Dialog „Etiketten erstellen“
Felder
Anzahl
Anzahl der zu erstellenden
      Etiketten
Jahr
Anerkennungsstelle
Nummer und Name der
      Anerkennungsstelle
Type
Lager
Art
Fruchtart
Botanisch
Botanische Bezeichnung
Sorte
Saatsorte
Probenahme
Datum der Probenahme
Gewicht
TKG
Tausendkorngewicht
KF
Keimfähigkeit
Beize
Name
      des Pflanzenschutzmittels
Zulassungs-Nummer
Zulassungs-Nummer des
      Pflanzenschutzmittels
Wirkstoff
Wirkstoff des
      Pflanzenschutzmittels
Verpackungseinheit
Qualitätsbemerkung
Bescheid
Herkunft
Wiederverschluß
Dazu
      Probedatum

---

## Partieverwaltung

Partieverwaltung
Hauptmenü
Partieverwaltung
Das Modul Partie in Referenz-ERP ermöglicht eine
Nebenbuchhaltung innerhalb der Warenwirtschaft mit folgenden
Leistungsmerkmalen:
•
Anlegen eines Partiestammes (Partienummer) unter Festlegung von
Sollzahlen (Menge und Wert) im WE und WV, sowie Hinterlegung von Partiepreisen
für die Partieartikel.
•
Die Partie kann während der Vorgangserfassung bequem per
Partieauswahlfenster angesprochen oder auch angelegt werden.
•
Führen von IST-Zahlen (Mengen und Werte) im WE und WV, sowie Ermittlung
des Partiebestandes und des Partierohertrages.
•
Eine Rückverfolgbarkeit der Ware wird ermöglicht (Einkauf über Produktion
zum Verkauf).
Die Partieverwaltung der Saatgutabwicklung und
Rohwarenabwicklung wird hier nicht näher beschrieben, diese werden in einer
gesonderten Beschreibung behandelt.

---

## Herkunftspartien und Verbleibverfolgung

Herkunftspartien und Verbleibverfolgung
Hauptmenü
Partieverwaltung
Partie-Stammdaten oder Direktsprung
[PAR]
In der Anwendung zur Bearbeitung von Partiestammdaten
stehen Funktionen zur Bestimmung des Verbleibs beziehungsweise der Herkunft von
Partiemengen zum gewählten Partiestamm zur Verfügung. Ausgehend von den der
gewählten Partie werden bei der
Herkunfts-Funktion
alle Zugänge zur
jeweiligen Partie unter Berücksichtigung von Artikel, Lager und Lagerplatz aus
anderen Partien und Eingangslieferscheinen und Eingangsrechnungen sowie
Umbuchungen und Produktionszugängen ermittelt. Entsprechend werden bei der
Verbleib-Funktion
die Abgänge der Partie unter Berücksichtigung von
Artikel, Lager und Lagerplatz aus anderen Partien und Ausgangslieferscheinen und
Ausgangsrechnungen sowie Umbuchungen und Produktionsabgängen ermittelt.
Achtung:
Bei Nutzung von Artikel-, Lager- und
Lagerplatzumbuchungen sowie des Produktionsmoduls muss für die entsprechenden
Vorgangsklassen und Vorgangsunterklassen unbedingt im Modul
Formularzuordnung/Vorgangsunterklassen
im Register
Partie
das Maschinentagebuch durch den Eintrag ‚
Ja
‘ im Feld
Maschinentagebuch führen
aktiviert sein. Nur dann können derartige
Herkunfts- und Verbleib-Bezüge ausgewertet werden!
Im angezeigten Beispiel der Herkunft der Partie 1249)
erfolgen sämtliche Zugänge zur Partie 1249 aus Eingangsbelegen, die im unteren
Bereich aufgeführt sind.
Die Funktion Verbleibverfolgung der Partie 1249 ergibt
die angezeigte Darstellung: Bei dem unter ‚Umbuchungen‘ ausgewiesenem Beleg 334
handelt es sich um einen Produktionsvorgang mit einer Abgangs-Komponente, der
zwei Partien (1249 und 1251) zugeordnet wurden und daher beide im Bereich
‚Herkunftspartien‘ dargestellt werden, sowie einer Zugangsposition
(Produktionsergebnis), der ebenfalls zwei Partien zugeordnet wurden (1252 und
1222), dargestellt im Bereich ‚Partieverfolgung Zielpartien‘.
Ein Mausklick in eine Partienummer in einem der oberen
beiden Bereiche ermöglic
[...]


---

## Besatzarten

Besatzarten
Hauptmenü
Saatzucht
Saatgutstammdaten
Besatzarten
Direktsprung
[SAATA]
In diesem Stammdatenpfleger werden Besatzarten
gepflegt, diese werden in Fruchtarten verwendet.   Kulturbesatzarten
wiederum können auf eine andere Fruchtart verweisen (Fremdbesatz).
Im Labormodul werden Besatzarten bei einigen
Labor-Verfahren angewandt.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
Nummer
Die
      Nummer der Besatzart. Bei Neu-Erfassung wird diese mit der bisher
      erfassten um 1 erhöhten Nummer vorgeschlagen, kann aber überschrieben
      werden.
Fruchtart
Hier
      kann bei Kultur-Besatzarten als Fremdbesatz die zugehörige
Fruchtart
angegeben werden. Eine Auswahl ist
      mit
F3
möglich. Hinter der Fruchtart wird dann die Bezeichnung
      angezeigt.
Besatz
Bezeichnung der Besatzart, wie sie
      dann in Listen erscheint
Botanische Bezeichnung
Botanische Bezeichnung bei
      Kulturbesatzarten.
Matchcode
Hier
      kann ein Matchcode eingetragen werden.
Gruppe
Die
      zugehörige Besatzartgruppe. Eine Auswahl über das Anwenderformat
      „AF_BESATZART“ ist
mit
F3
möglich.
Kategorie
Hier
      kann eine Saatgut-Kategorie angegeben werden. Eine Auswahl der Kategorien
      ist
mit
F3
möglich.
Typ
      (BesatzartTyp)
An
      dieser Stelle ist die Eintragung eines Besatzart-Typs aus dem
      Anwenderformat „AF_BESARTTYP“ per
F3
möglich.
AkSt
      Nr. FB (BesatzArtAkStNrFB)
Hier
      kann die bundeseinheitliche Schlüsselnummer der Anerkennungsstelle des
      Kriteriums ‚Feldbestandsprüfung‘ eingetragen werden.
AkSt
      Nr. BP (BesatzArtAkStNrBP)
Hier
      kann die bundeseinheitliche Schlüsselnummer der Anerkennungsstelle des
      Kriteriums ‚Beschaffenheitsprüfung‘ eingetragen werden.

---

## Pfleger Publikationen

Pfleger Publikationen
Felder
Eigenschaft
Zeigt die Eigenschaft einer
      Publikation:
-
Amic-Standard
-
benutzerdefiniert
Publikation
Angabe des gewünschten
      Publikationsnamens.
Vorbelegt mit:
AMIC_
Artikel
Zeigt die in der Publikation
      enthaltenen Artikel.
Funktionen
Speichern
Speichert die Angaben

---

## Fruchtarten

Fruchtarten
Hauptmenü
Saatzucht
Fruchtarten
Direktsprung
[SGF]
In diesem Stammdatenpfleger werden die Daten über
Fruchtarten gepflegt.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
Fruchtart-Nummer
Hier
      wird die Identifikationsnummer der Fruchtart eingetragen. Bei Neuanlage
      wird die nächste freie Nummer vorgeschlagen
Kurz-Bezeichnung
Hier
      wird die Kurzbezeichnung für die Fruchtart eingetragen. Die
      Kurzbezeichnung darf maximal aus vier Zeichen bestehen.
BSS-Fruchtart
Dieses
      Maskenfeld enthält die namentliche Bezeichnung für diese Fruchtart. Zu
      diesem Feld kann mit F3 die Bezeichnung in einer anderen Sprache erfasst
      werden.
Art
      + Unterart botanisch
Die
      botanische Art + Unterart Bezeichnung dieser Fruchtart kann hier
      eingetragen werden.
Art
      / Familie botanisch
Die
      botanische Art / Familie Bezeichnung dieser Fruchtart kann hier
      eingetragen werden.
Lizenz-Abrechnungsart
Mit
F3
stehen folgende Auswahlmöglichkeiten zur
      Verfügung:
•
sortenspezifisch
•
Betrag pro
      Anzahl Mengeneinheiten
•
% vom
      Nettobetrag
Basis-Zuschlag-Abrechnungsart
Mit
F3
stehen folgende Auswahlmöglichkeiten zur
      Verfügung:
•
sortenspezifisch
•
Betrag pro
      Anzahl Mengeneinheiten
•
% vom
      Nettobetrag
Gattung
Die
      Gattung dieser Fruchtart kann hier eingetragen
      werden.
Gewicht in kg/hl
Das
      Gewicht in kg/hl dieser Fruchtart kann hier eingetragen
      werden.
Sortiermerkmal
Hier
      kann die Sortierreihenfolge für diese Fruchtart innerhalb der Ausdrucke
      festgelegt werden.
Anerkennungspflichtig
Die
      Fruchtart kann hier als anerkennungspflichtig gekennzeichnet
      werden.
Fließeigenschaft
Die
      Fließeigenschaft dieser Fruchtart kann hier eingetragen werden.
      Vorbelegung aus Anwendungsformat AF_FRUFLIES.
Standardmenge
Die
      Standardmenge bei Laboranalysen
Standardunters.
[...]


---

## Postleitzahlen

Postleitzahlen
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Postleitzahlen
Direktsprung
[PLZ]
Postleitzahlen können hier zentral erfasst und
gepflegt werden. Im Auslieferungsumfang ist das offizielle Verzeichnis für
Deutschland enthalten.

---

## Registerkarte Markt

Registerkarte Markt
Auf dieser Registerkarte werden alle Marktseitigen
Einstellungen vorgenommen.
Bestell und Fakturiersperre per
Datendrehscheibe
In diesem Feld kann hinterlegt werden, ob die
Fakturier- oder Bestellsperre des Artikels per Einspielung von Artikeldaten
einer Datendrehscheibe verändert werden darf.
Das Feld kann mehrere Ausprägungen annehmen:
Ausprägung
Bedeutung
Aus
      dem Artikelstamm
Im
Artikelstamm
wird entschieden, ob die Bestell- oder Fakturiersperre aller Artikel des
      Artikelstamms überschrieben werden darf oder nicht. Ist im Artikel der
      Standardfall.
Durchführen
Mit
      dieser Einstellung werden die Kennzeichen Bestell- und Fakturiersperre
      durch die Datendrehscheibe abgeändert.
Fakturiersperre
      unterdrücken
Mit
      dieser Einstellung wird nur das Kennzeichen Bestellsperre durch die
      Datendrehscheibe abgeändert. Das Kennzeichen Fakturiersperre wird nicht
      durch die Datendrehscheibe verändert:
Bestellsperre
      unterdrücken
Mit
      dieser Einstellung wird nur das Kennzeichen Fakturiersperre durch die
      Datendrehscheibe abgeändert. Das Kennzeichen Bestellsperre wird nicht
      durch die Datendrehscheibe verändert.
Beide unterdrücken
Mit
      dieser Einstellung werden die Kennzeichen Bestell- und Fakturiersperre
      nicht durch die Datendrehscheibe abgeändert.

---

## Reporte Artikelstamm

Reporte Artikelstamm

---

## Rollenmapping: Pfleger

Rollenmapping: Pfleger
Felder:
Felder
Optionbox
Die
      Optionbox des Zielkontextes.
Auswahl per Funktion „Optionbox
      wählen … (F3)“
Funktion
Die
      Funktion des Zielkontextes.
Auswahl per Funktion „Funktion
      wählen … (F3)“
Rolle
Die
      Rolle des Zielkontextes (informatorisch).
Quelle-Optionbox
Die
      Optionbox des Quell-Kontextes.
Auswahl per Funktion „Optionbox
      wählen … (F3)“
Quelle-Funktion
Die
      Funktion des Quell-Kontextes.
Auswahl per Funktion „Funktion
      wählen … (F3)“
Quelle-Rolle
Die
      Rolle des Quellkontextes (informatorisch).
Quelle sichtbar
Bestimmt ob der Quellen-Kontext
      „sichtbar“ beleibt, d.h. ob die Quellen-Funktion in der Quellen-Optionbox
      aufgelistet wird.
Bei
      „Nein“ ist der Inhalt der Quellen-Rolle unerheblich.
Funktionen:
Funktionen
Funktion wählen …
      (
F3
)
Auf
      den Feldern „Funktion“ und „Quelle-Funktion“ steht eine Funktionsauswahl
      innerhalb des Kontextes zur Verfügung.
Optionbox wählen …
      (
F3
)
Auf
      den Feldern „Optionbox“ und „Quelle-Optionbox“ steht eine Optionboxauswahl
      innerhalb des Kontextes zur Verfügung.

---

## Rollenstamm: Pfleger

Rollenstamm:
Pfleger
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenstamm
oder Direktsprung
[ROLLE]
Hier kann hauptsächlich die Zuordnung der Rolle zu den
Bedienerklassen
gepflegt werden.
Die Bedienerklassen und ihre Zustände bzgl. der Rolle
werden vollständig im Grid gelistet und es kann zu jeder Bedienerklassen jeweils
einzeln der Soll-Status (darf, darf nicht) festgelegt werden.
Felder des Rollenstamm Pfleger:
Felder
Rolle
Eindeutiger bis zu 255 Zeichen
      langer Bezeichner.
Ist
Ja/Nein
Gibt
      die Zugehörigkeit der Bedienerklasse zur Rolle an.
Bedienerklasse
Bedienerklasse
Soll
Ja/Nein
Änderungen zu „Ist“ werden farblich
      abgegrenzt, um die Übersichtlichkeit zu unterstützen.
Bedienerklassen-Bezeichnung
Die
      Bezeichnung der Bedienerklassen.
Ein
      vorangestellter Stern (*) bedeutet das die Bedienerklasse eine
      Controller-Klasse ist, somit die Bedienerklasse Mitglied der
      Controller-Rolle ist.
Bediener
Informatorische auf max. 255 Zeichen
      begrenzte Liste der Bediener der Bedienerklasse.
Funktionen des Rollenstamm Pfleger:
Funktionen
Rolle umbenennen
(F5)
Rolle umbenennen.
Neu
(F8)
, Speichern
(F9)
, Speichern unter…
(shift + F9)
, Löschen
(F7)
Rolle tauschen
Ruft
      die Funktion für das
Rollen tauschen
auf.
Rolle vereinigen
Bietet die Möglichkeit
Rollen zu
      vereinigen

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

## Produktion mit Seriennummern

Produktion
mit Seriennummern
Bei der Produktion wird die Produktartikelnummer
gescannt und oder die dazu gehörige Seriennummer. Anhand des Produktartikels
wird dann das Rezept gezogen und entsprechend aufgelöst. Erfasste Seriennummern
werden in der Ausprägung des Artikels gespeichert. Bei der Erstellung der
Produktion wird dann die Seriennummer dem Produktionsbeleg zugeordnet.
Um die Produktion auf dem Scanner zu starten werden
zwei Scancodes benötigt. Diese müssen per Etikettendruck bereitgestellt werden.
Dazu wird der Text „PRODSTART“ und „PRODENDE“ im EAN 128 Verschlüsselt
ausgedruckt.
Um eine Produktion zu starten wird als erstes der
Befehl „
PRODSTART
“ eingescannt. Danach wird der Artikel und oder die
dazugehörige Seriennummer erfasst. Da es sich bei dieser Produktion um eine
Produktion für Stückartikel handelt muss bei der Menge immer eine 1 eingegeben
werden. Wird eine Zahl größer 1 eingegeben, so wird zwar die Produktmenge erhöht
aber nicht die Komponentenmenge.
Mit dem Befehl „
PRODENDE
“ wird die Produktion
abgeschlossen.
Währen der Erfassung der Produktion kann diese neu
gestartet werden, durch zweimaliges Scannen von „
PRODSTART
“
Die erfasste Produktion wird in der
Vorgangsimport
[
VIMP
] Hauptmenü
Externe Kommunikation
Stammdatenimport
Vorgangsimport
gespeichert. Von dort aus kann mit der Funktion „
Standardvorgang erzeugen
“ eine Produktion
aus den erfassten Daten erstellt werden.
Stornierung einer Position
Eine erfasste Position kann  wie folgt storniert
werden. Dazu wird der Stornobefehl gescannt. Danach kann entweder per Scannung
des Artikels oder der Seriennummer die letzte erfasste Position des Artikels
gelöscht werden. Des Weiteren gibt es die Möglichkeit die zu löschende
Positionsnummer manuell über die Tastatur einzugeben. Es wird immer die
komplette Position gelöscht.
Folgende Itembox Stellt die Daten für die
Anzeige auf dem Scanner zusammen.
IB_CE_PRODUKTION

---

## Sekundärschlüsselgruppe

Sekundärschlüsselgruppe
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Sekundärschlüssel Gruppe
oder Direktsprung
[SEKK]
Die Standard-Artikelsekundärschlüssel sind
Matchcode(s)
,
EAN-Nummer(n), Verpackungs-EAN-Nummer(n)
und für die
Streckenerfassung
bedeutungsvolle(n)
Referenzartikel
.
Der Anwender kann sich weitere eigenständig
definieren:
Hierzu ist die Relation einzutragen (hier immer
ARTIKELSTAMM) und eine Bezeich­nung zu vergeben. In der Option Box des
Artikelstamms erscheint dann unter Sekun­där­schlüssel die neue Gruppe,
wo dann ein weiterer Suchbegriff eintragbar ist. Auch bei der Artikelauswahl im
Vorgang kann auf diese neue Gruppe zugegriffen werden. Mit jeweils bis zu 99
Einträgen pro Schlüsselgruppe stehen sicherlich genügend Suchbegriffe zur
Verfügung. Mit dieser Methode besteht allerdings die Möglichkeit, Suchbegriffe
zusätzlich, z.B. nach inhalt­lichen Merkmalen, zu strukturieren.

---

## Sekundärschlüssel

Sekundärschlüssel
Der eindeutige Suchbegriff für den Anwender ist die
Artikelnummer. Als weitere se­kundäre Suchschlüssel stehen jeweils 99
Matchcodes, EAN-Nummern und Verpackungs-EAN-Nummern zur Verfügung, die über
folgende Maske erfasst werden.
Die Ausnutzung dieser Möglichkeiten ist auch
angesichts der textlichen Suchmöglichkeiten in das Ermessen des Anwenders
gelegt. Vor Anlage der Suchbegriffe sollte auch überlegt werden, die
Suchbegriffe in eine Abteilung zu legen: So könnte bei Hinterlegung in z.B. der
Abteilung Matchcode hier sowohl nach Matchcode und nach EAN-Code gesucht
werden!
Für die
Streckenerfassung
hat der Schlüsseltyp
„Referenzartikel“ eine besondere Bedeutung im Zusammenhang mit der
Planungsbelegeingabe
.
Faktoren bei EAN-Codes
Wird bei EAN-Codes als Sekundärschlüssel ein Faktor
eingegeben, so wird bei der Erfassung in der Kasse dieser Faktor beim Scan
berücksichtigt.
Auf diese Weise kann eine EAN für die Umverpackung
definiert werden, die z.B. die EAN für einen 10er Pack darstellt, so dass der
Bediener nicht zehn einzelne Artikel scannen oder den Faktor manuell eingeben
muss.
Die vorbelegte Menge wird mit dem Faktor 10
automatisch multipliziert.

---

## Sonder-AfA Stammdaten

Sonder-AfA Stammdaten
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Sonder-AfA
Direktsprung
[ANKSA]
Sonder-AfA ermöglicht zurzeit nur § 7g EstG; diese ist
neben der Regel-AfA nach § 7 EstG zulässig. Bei Sonder-AfA ist zunächst der
Begünstigungszeitraum festzustellen. Im Falle des § 7g Abs. 5 EstG beginnt der
Begünstigungszeitraum im Jahr der Anschaffung und endet vier Jahre später. Am
Ende des Begünstigungszeitraums erfolgt die Umstellung auf die Restwert AfA.
In Referenz-ERP werden der Begünstigungszeitraum und der
AfA-Satz in einem separaten Pfleger erfasst.
Bedeutung
Nummer
Nummer, die die Sonder-AfA eindeutig
      kennzeichnet. Diese Nummer wird im Anlagenstamm eingetragen
Bezeichnung
Bezeichnung zur Identifikation des
      Sonder-AfA
AfA-Konto
Die
      Sonder-AfA muss auf einem Separaten AfA-Konto vermerkt werden. Ist hier
      kein Konto angegeben, so wird beim Buchen der AfA das AfA-Konto verwendet,
      welches in den Stammdaten des Anlagegutes hinterlegt ist.
Begünstigungszeitraum
Zeitraum in Jahren, für den sich die
      Bemessungsgrundlage nicht ändert. In diesem Beispiel wird erst nach
      weiteren vier Jahren ( Jahr der Anschaffung nicht mitgerechnet ) auf
      Restwert-AfA umgestellt.
AfA-Satz
Hier
      erfasst man den Prozentsatz zur Berechnung der Sonder-AfA

---

## Spezielle Mengeneinheiten

Spezielle Mengeneinheiten
Anbruchgebinde
Sie sind als Mengeneinheiten mit dem Gebindetypen
Anbruch Gebinde, aufgerundet
Anbruch Gebinde, abgerundet
einrichtbar.
Anbruchgebinde aufgerundet:
Es wird eine bestimmte Anzahl von Einheiten eingeben,
die Gebindeanzahl.
Die resultierende Menge ist nur ein Vielfaches des
ersten Gebindefaktors
Es wird hierbei davon ausgegangen, dass nur Mengen
fakturiert werden dürfen, die voll in einer Packungsgröße aufgehen, sozusagen
untrennbar sind.
Beispiel:
Es sind 15 Fliesen in einem Karton.
Es sollen nur volle Kartons in Rechnung gestellt
werden
Bei Eingabe von 1490 Stück kann wird dann automatisch
auf 1500 aufgerundet
Dabei wird nicht im kaufmännischen Verfahren auf- bzw.
abgerundet, sondern immer auf volle Packungsgrößen aufgerundet, sobald eine
neue Packung angefangen wird.
Darüber hinaus ist es dann möglich, die Einheiten in
Bezug zu weiteren Größen zu stellen. Bei diesem Beispiel wäre es interessant,
wie viele Quadratmeter, wie viel Kisten oder wie viel Paletten die gewünschte
Menge ergeben werden. (Siehe dazu Packungsgröße. weiter unten) Denkbar wäre bei
der Fakturierung auch eine Mengeneingabe in Quadratmetern, wobei aber auch nur
immer volle Kartons bewegt werden sollen.
Anbruchgebinde aufrunden Stufe 2:
Bei dieser Einstellung wird nicht auf volle Gebinde
(z.B. Paletten) aufgerundet, sondern eine Stufe weiter unten, also z.B. Kartons.
Das eigentliche Gebinde darf also angebrochen werden, die nächstniedrigere Ebene
nicht. Natürlich ist diese Einstellung nur bei Verwendung mehrstufiger Gebinde
sinnvoll
Anbruchgebinde, abgerundet
Dieses Berechnungsverfahren läuft analog zum
aufgerundeten Anbruchgebinde, wobei jedoch die Eingabemenge im Anbruchfall immer
auf die nächste kleinere Packungsgröße zurückgerechnet wird.
Packungsgröße:
In dem Feld Gebindemaß 1 wird die Anzahl bzw. der
Faktor hinterlegt, der als fester Rundungswert gelten soll. Dieses Maß
kann in der Mengeneinheit selbst hinterlegt werden (Faktorherkun
[...]


---

## Sprachabhängige Bezeichnung in den Stammdaten

Sprachabhängige Bezeichnung in den
Stammdaten
Wenn man in einer Datenbank Anwender mit
unterschiedlichen Sprachen führt, so ist es Sinnvoll, dass diese Anwender die
Bezeichnungen der Stammdaten auch in Ihrer Sprache sehen können. Dazu muss man
im Stammdatenpfleger, wenn man auf dem Bezeichnungsfeld steht, die Taste F3
drücken und gelang dann in einen Dialog zur Pflege der sprachabhängigen
Texte:
Die deutschen Texte werden weiterhin direkt auf der
Maske gepflegt. Wobei es hier folgendes zu beachten gibt: Wenn ein Anwender, der
nicht
mit der Sprache Deutsch arbeitet, den Text direkt auf dem
Stammdatenpfleger ändert, so ändert er ihn direkt für sein Sprache und nicht für
die Sprache Deutsch. Dieses Verhalten erleichtert die Pflege der fremdsprachigen
Texte erheblich. Gleichzeitig folgt daraus jedoch, dass nur Anwender, die mit
der Sprache Deutsch arbeiten auch deutsche Texte ändern können.
Die hier gepflegten Texte werden dann in allen
Auswahllisten und F3-Auswahlen für fremdsprachige Anwender angezeigt. Will man
die Funktionalität in eigenen privaten F3-Auswahlen (Itemboxen) verwenden, so
muss man die Bezeichnung mit der Funktion AMIC_FUNC_SPRACHBEZEICH bestimmen.
Hier ein Beispiel, wie man die Sprachbezeichnung für den Sachkontenstamm
bestimmen kann:
select Kontonummer,
AMIC_FUNC_SPRACHBEZEICH('SachKontStamm',
trim(cast(KontoNummer as char(10))),
SachKontBezeich ) as SachKontBezeich,
from SachKontstamm
Der erste Parameter ist - meistens – der Tabellenname.
Er kann auch einen anderern Wert haben, wenn z.B. in einer Tabelle mehrere
pflegbare Bezeichnungsfelder existieren.
Der zweite Parameter ist der eindeutige Schlüssel.
Der dritte Parameter ist der Originalwert. Wenn als
Sprache Deutsch verwendet wird, wird erst gar nicht in der Datenbank nach einer
anderen Bezeichnung gesucht, sondern sofort dieser Wert zurückgeliefert.

---

## Stammdatenimport

Stammdatenimport
Hauptmenü
Externe Kommunikation
Stammdatenimport
Stammdatenimport
Mit dieser Anwendung können Importe für Kunde, Artikel
und Artikelpreise durchgeführt werden. Die Import Dateien müssen im dbf Format
vorliegen. Anhand eines Scripts werden die Daten dann in die jeweilige Branchen-ERP
Tabelle geschrieben. Beim Artikel ist es die Tabelle AMC_Artikel. Aus dieser
Tabelle werden dann im zweiten Schritt die Daten in die richtigen Relationen
verteilt.
Felder des Stammdatenimport
Felder
Bedeutung
Bezeichnung
Bezeichnung des Imports
Import Typ
Art
      des Importes
Datei
Pfad
      zur Datei, welche die zu Importierenden Daten enthält.
Funktionen des Stammdatenimport
Funktionen
Bedeutung
Ändern
(F5)
, Ansicht
(F6)
, Neu
(F7)
, Löschen
(F8)
Ruft
      den Pfleger auf
Ausführen
(F9)
Führt den Import aus
Neuanlage eines Imports
Mit
Neu
oder
F8
kann ein neuer Import
angelegt werden.
Es gibt drei Arten des Imports
1.
Artikelimport
2.
Artikelpreisimport
3.
Kundenimport
Eingabefelder
Bedeutung
Name
Hier
      wird der Name des Imports hinterlegt z.B. Artikelimport
Import Typ
Art
      des Importes
Datei
Pfad
      zur Datei welche die zu Importierenden Daten enthält.
Scriptdatei
Die
      Scriptdatei wird in Abhängigkeit des Importtyps gesetzt. Soll nicht die
      Standard-Importdatei genutzt werden, so kann hier ein eigenes SQL oder
      Makro eingetragen werden.
Scripttyp
Hier
      wird der Scripttyp eingetragen zur Auswahl stehen.
1.   SQL
      Script
2.   Referenz-ERP
      Makro
Importdatei löschen
Soll
      die Importdatei nach dem erfolgreichen Import gelöscht werden.
Endkontrolle für den Stammdatenimport
Hauptmenü
Externe Kommunikation
Stammdatenimport
Endkontrolle/Einspielung Artikel
Hauptmenü
Externe Kommunikation
Stammdatenimport
Endkontrolle/Einspielung Preise
Hauptmenü
Externe Kommunikation
Stammdatenimport
Endkontrolle/Einspielung Kunden

---

## Stammdatenpflege

Stammdatenpflege
Zunächst müssen Sie die bestehenden Anschriften
bearbeiten. Es ist eine Unterscheidung notwendig, ob es sich bei der Anschrift
um eine Person oder um eine Firma/Organisation handelt. Setzen Sie dazu im
Anschriftenstammpfleger das Kennzeichen Person/Firma.
Handelt es sich bei der Anschrift um eine Person, so
kann es sinnvoll sein, bei Auslandskontakten weitere Daten wie z.B. die
Sozialversicherungsnummer oder Reisepassdaten, Geburtsdaten etc. abzufragen.
Diese Daten sind streng vertraulich, und deshalb auch
nur einem eingeschränkten Personenkreis zugänglich.

---

## Standort Stammdaten

Standort Stammdaten
Hauptmenü
Anlagenbuchhaltung
Stammdaten
Standorte
Direktsprung
[ANKAO]
Die Standorte dienen neben der Beschreibung des
Anlagegutes auch zur Eingrenzung innerhalb der Auswahllisten und
Auswertungen.

---

## Stapelkorrektur Artikelstamm

Stapelkorrektur Artikelstamm
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel-Stamm-Stapelkorrektur
oder Direktsprung
[ARSK]
Nach Anwahl des Programmteiles erscheint der bekannte
Auswahlbildschirm. Hier wird festgelegt, welcher Artikelstammabschnitt geändert
werden soll, also z.B. alle Artikel, die einer Warengruppe angehören oder auch
einzeln ausgewählte.
Danach wird
Ändern
F5
aus der Funktionsbox unten rechts
ange­wählt. Es wird dann eine Auswahl änderbarer Parameter angeboten:
In der linken Spalte werden Stammdatenparameter
angezeigt, z.B. "Warengruppe".
In der Spalte rechts daneben kann nun der neue
Parameter eingetragen werden.
Wenn der Programmlauf mit
F9
gestartet wird, sind in allen vorher
bestimmten Artikelstammdaten die Warengruppennummern auf diesen neuen Wert
gesetzt worden:

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

## Stapelkorrekturverfahren

Stapelkorrekturverfahren
Diese Programmfunktion ermöglicht es, über Artikel und
Artikelstammbereiche automatische Änderungen der Stammdaten vorzunehmen.

---

## Steuerungsparameter für Artikelstamm und Artikel

Steuerungsparameter für Artikelstamm und Artikel
In den Steuerungsparametern können zentrale
Grundeinstellungen für Artikelstamm und Artikel vorgenommen werden. Die
wesentlichen finden sich in den Abschnitten 21 und 22, auf die hier eingegangen
werden soll.
Artikel – Stammdaten (Parametergruppe 21)
Länge Artikelstamm- und Artikelnummer:
Hiermit
wird die maximale Länge der Nummern bestimmt.
Variante Artikelnummer:
Gültigkeit ab:
Der Beginn der
Gültigkeitsdauer kann sein:
1.1.1901
1.1. des laufenden Kalenderjahres
Beginn des laufenden Geschäftsjahres
Gültigkeit bis:
Die Gültigkeit läuft ab
Am 31.12.2099
31.12. des laufenden Kalenderjahres
Ende des laufenden Geschäftsjahres
Artikelstamm prüfen:
Bei Eingabe von Ja werden die Artikelstammdaten bei
der Einspielung überprüft.
Standard Mengeneinheit Gewichte:
Die
Mengeneinheit für das Ver­packungsgewicht im Artikelstamm wird entsprechend
dieser Eintragung vorbelegt.
Preiseinheit und Mengeneinheit fix je
Artikel:
Autom. Verpackungs- / Bruttogewicht:
Ohne:
Netto-, Verpackungs- und Bruttogewicht werden
manuell erfasst
Verpackung ergibt sich automatisch aus Brutto und
Netto
Brutto
ergibt sich automatisch aus Netto und Verpackung
Preisanzeigefenster mit 0-Preisen
Dieser Parameter gibt an. Ob Preise mit dem Wert 0 auf
der Hauptseite sichtbar sind.
Preise im Anzeigenfenster
Dieser Parameter
gibt an, welche Preise im Anzeigefenster dargestellt werden können.
Aut. Artikel-Neuanlage bei Warenpos.
Wenn
dieser Parameter gesetzt ist, so können Artikel, die in dem aktuellen Lager
nicht angelegt ist mit der Funktion Artikelkopierer aus der Funktionsbox in das
aktuelle Lager kopiert werden.
Mit einer Option kann auch ein Lager als
Sortimentslager angegeben werden von dem dann in einem solchen Fall die Artikel
kopiert werden.
Dienstleistungen nur als Wertartikel
Wenn dieser Parameter gesetzt ist, werden nur die
Werte geführt, es werden keine Mengen geführt.
Vorgangs-Nr. in Artikel-Info ab Stelle
Folgeartikel aktiv
Hier ka
[...]


---

## Artikel und Artikelstammdaten

Artikel und Artikelstammdaten

---

## Artikelvorbelegungen

Artikelvorbelegungen

---

## Folgeartikel

Folgeartikel

---

## Stoffstromdaten in Produktionsbelegen

Stoffstromdaten in
Produktionsbelegen
Auch bei der Erfassung, Erzeugung und Bearbeitung von
Produktionsvorgängen werden für alle Vorgangspositionen mit denjenigen Artikeln,
denen per Artikelstamm-Zusammensetzung Stoffstrompositionen zugeordnet sind,
Stoffstromdaten berechnet.
Sofern bei Produktionen mit individuellen Rezeptdaten
und/oder Verfahren, bei denen die Stoffstromanteile bei identischem
Produkt-Artikelstamm unterschiedlich ausfallen können, müssen die
Stoffstromdaten mittels des
Stoffstromdaten-Editors
gegebenenfalls
angepasst werden. Dieses kann, ebenso wie die
Nachberechnung/Neuberechnung
von
Stoffstrom-Mengen zu Positionen von Produktionsvorgängen  in der
Auswahllistenvariante
‚Produktion mit Positionen‘
des Produktionsmoduls
geschehen.

---

## Stoffstromdaten in Rohwarebelegen

Stoffstromdaten in
Rohwarebelegen
Auch bei der Erfassung, Erzeugung und Bearbeitung von
Rohwarevorgängen werden für alle Vorgangspositionen mit denjenigen Artikeln,
denen per Artikelstamm-Zusammensetzung Stoffstrompositionen zugeordnet sind,
Stoffstromdaten berechnet.
In den Rohwarebearbeitungs-Modulen sind die
vorgangsbezogenen Auswahlvarianten nicht positionsorientiert. Dennoch kann hier
der
Stoffstromdaten-Editor
zur Ansicht oder Korrektur genutzt werden, pro Vorgang kann hier durch die
einzelnen Positionen geblättert werden.
Zur automatischen
Nachberechnung/Neuberechnung
von
Stoffstrom-Mengen zu Positionen von Rohwarevorgängen steht in diesen
Auswahlvarianten keine Funktion zur Verfügung. Diese Aufgabe kann aber in der
Auswahllistenvariante
‚Stoffstrom-Positionen‘
des Moduls
‚Vorgangsübersicht‘
nach Selektion der gewünschten Vorgänge
erfolgen.

---

## Szenario

Szenario
Definition der Packelemente
Hier müssen die möglichen Abpackungselemente erfasst
werden.
Name Buchungskennzeichen
Falls Ja, Artikelstammnummer für die
Leergutbuchung
Zusammenstellung der Abpackungen
Hier werden je Kombination Artikel / Kunde folgende
Werte hinterlegt: Abpackungselemente 1 bis 3 (siehe 1.) Multiplikatoren dazu EAN
Ware EAN Umverpackung Etikett drucken (J/N) Preis Kennzeichen Preis hat
Priorität, Vorbelegung mit Ja
Ablauf Lieferschein
In der Artikelerfassung wird nach Abpackvorschriften
in der gegebenen Kombination Kunde/Artikel gesucht. Falls Eintrag vorhanden,
wird der Gebindedialog mit den Faktoren geöffnet; hier wird die Anzahl der
obersten Ebene (Paletten) abgefragt. Bei Verlassen des Positionsteils wird je
nach Einstellung die kumulierte Menge der Verpackungsartikel (siehe 1.) dem
Beleg zugefügt.
Druck NVE-Etiketten
Bei Verlassen des Beleges wird der Druck der NVE -
Etiketten gemäß den Einstellungen unter 2. ausgelöst. Hierfür ist unter OPT eine
Vorschrift Drucker / Etikettname zu hinterlegen.
Korrektur des Beleges
Es wird hinterlegt, für welche Palette bereits ein
Etikett gedruckt wurde. Wird die Menge in der Korrektur verkleinert, werden
diejenigen nicht verwendeten NVE zum Löschen markiert. Wird die Menge in der
Korrektur vergrößert, werden die zugefügten NVE-Etiketten nachgedruckt.

---

## Privatisierbare Prozeduren für die Datendrehscheibe Import

Privatisierbare Prozeduren für die Datendrehscheibe Import
Name
Link zu der iHilfe
Artikel-Importprozedur
Datendrehscheibe_Import
E
AN-Prozedur
DatendrehscheibeEAN
Artikelnummerfunktion
Artikellieferant-Prozedur
DatendrehscheibeArtikelLieferant
Preis-Prozedur
DatendrehscheibePreis
Gefahrgut-Prozedur
Noch nicht Implementiert
Prozedur vor der Einspielung der
      Daten
Hier kann eine Private Prozedur
      hinterlegt werden, die nach dem Abgleich mit der Musterartikel und vor der
      Einspielung in Referenz-ERP Artikelstamm aufgerufen wird. Die Prozedur hat
      keinen Übergabeparameter. Es wird vom aufrufenden System auch kein
      Rückgabewert erwartet.
Importumsetzter Prozedur für die
      Warengruppe
ImpumDatendrehscheibeWarengruppe
Importumsetzter Prozedur für die
      Erlöskennziffer
ImpumDatendrehscheibeEKZ
Importumsetzter Prozedur für den
      Steuer Schlüssel
ImpumDatendrehscheibeSteuerSchluessel
Importumsetzter Prozedur für die
      Mengeinheit
ImpumDatendrehscheibeMENummer
Importumsetzter Prozedur für die
      Mengeinheitsgruppe
ImpumDatendrehscheibeMEGruppe
Importumsetzter Prozedur für den
      Artikellieferanten
ImpumDatendrehscheibeLieferanten
Importumsetzter Prozedur für die
      Lagernummer
ImpumDatendrehscheibeLager

---

## Textbaustein-Pfleger

Textbaustein-Pfleger
Funktionen des Textbaustein-Pflegers:
Funktion
Beschreibung
Bemerktyp (Texttyp)
Bemerk-/texttyp
Bemerknummer
      (Textnummer/Bausteinnummer)
Nummer des Typs
Texteingabe
Bei Textersetzung:
Vorgangstexte mit Stoppposition und
      fester Länge:
Der
      Start eines Platzhalters wird mit „#0“ definiert. Die Länge wird dann mit
      der Anzahl „$“ festgelegt, die Startposition zählt dabei dazu.
-
Definierter Text:
      “Es bediente Sie #0$$$$$$$$$$$$$$$$$$. Vielen Dank!”
Vorgangstexte mit Stoppposition und
      variabler Länge
-
Definierter Text:
      “Es bediente Sie #0§§§§§§§§§§§§§§§§§§. Vielen Dank!”
Des
      Weiteren ist es möglich einen Platzhalter als Pflichtfeld zu kennzeichnen.
      Dafür wird statt den „#0“ ein „#1“ verwendet.
Funktionen des Textbaustein-Pflegers:
Funktion
Beschreibung
Speichern (F9)
Speichert den aktuellen Datensatz
      ab
Editor öffnen (F3)
Öffnet Notepad mit dem aktuellen
      Text
Dokument laden (F11)
Öffnet den Referenz-ERP Dokumenten
      Editor

---

## Verpackungsgruppen

Verpackungsgruppen
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Verpack-Gruppen
oder Direktsprung
[VPKG]
Derzeit nicht aktiv; vorgesehen ist jedoch:
Um Artikel auch nach ihrer Verpackung gruppieren zu
können, z. B. für Listen­selektionen etc., besteht die Möglichkeit,
Verpackungsgruppen zu erfassen.
So können auch Auswertungen nach Verpackung erstellt
werden und so der „Erfolg“ einer Verpackung / Verpackungsgruppe ermittelt
werden.
Verweis auf die angelegte Verpackungsgruppe des
Artikels.

---

## Vertreterklassen: Pfleger

Vertreterklassen: Pfleger
Felder:
Feld
Bedeutung
Vertreterklasse.
Gibt
      die Klassennummer an.
Bezeichnung
Gibt
      den Klassennamen an.
Funktionen:
Feld
Bedeutung
Löschen (F7),
      Speichern(F9)

---

## Vertreterstamm Variante 1

Vertreterstamm Variante 1
Hier werden alle erfassten Vertreter aufgelistet.
Felder:
Feld
Bedeutung
Nummer
Nummer des Vertreters
Name
Name
      des Vertreters
Matchcode
Klasse
Zeigt an, welche
Vertreterklasse
hinterlegt ist,
      anhand der Nummer
Suchmöglichkeiten des Vertreterstamm
Feld
Bedeutung
Vertreter
Von…
      Bis…
Funktionen: des Vertreterstamm
Feld
Bedeutung
Ändern (F5), Ansicht (F6), Löschen
      (F7), Neu (F8)
Ruft
      den Pfleger des Vertreterstamm auf.
Vertreterabrechnung (F9)
Öffnet die
Vertreterabrechnung
.

---

## Vertreterstamm: Pfleger

Vertreterstamm: Pfleger
Kopfdaten:
Feld
Bedeutung
Vert. Nr.
Gibt
      die Vertreternummer an
Klasse
Zeigt die Vertreternummer an und
      gibt den dazugehörigen Namen der
Klasse
aus
Register:
Allgemein
Feld
Bedeutung
Verkaufsgebiet
Verkaufsgebiet des
      Vertreters
Abrechart(*)
Periode der Provisionsabrechnung als
      numerischer Schlüssel:
0   =
      keine Vertreterabrechnung
1
        =     monatlich
2   =
      zweimonatlich
12 =
          jährlich
14 =
          wöchentlich
15 =
          vierzehntägig
Anrede
Anrede des Vertreters
Vorname
Vorname des Vertreters
Name
Nachname des Vertreters
Zusatz1
Zusatz zum Vertreter
      Namen
Straße
Straße des Vertreters
Land -PLZ
Land
      + Postleitzahl des Vertreters
Ort
Ort
      (bezogen auf Land + Postleitzahl) des Vertreters
Ortsteil
Ortsteil (bezogen auf den Ort) des
      Vertreters
Telefon
Telefonnummer des
      Vertreters
Fax
Faxnummer des Vertreters
Matchcode
Partner 1
Erster Partner des
      Vertreters
Partner 2
Zweiter Partner des
      Vertreters
Bemerkung
Hier können Bemerkungen für den Vertreter eingetragen
und gespeichert werden.
Funktionen:
Funktionen des Vertreterstamm Pfleger:
Feld
Bedeutung
DSGVO-Liste
Zeigt die
DSGVO
Liste zu dem ausgewählten
      Vertreter an.
Gruppenanteile (F6)
Öffnet eine Liste in der dem
      Vertreter ein, oder mehrere
Vertretergruppen
, zugeordnet werden
      können.
Provisionsmerkmale (F10)
Öffnet
Vertreterprovisionstabelle
Anschriften (Shift + F7)
Ruft
      den
Anschriften-Pfleger
für den Vertreter auf.

---

## Vertreterstamm Variante 2 (Fehlerhafte / unvollständige Vertreter)

Vertreterstamm Variante 2 (Fehlerhafte / unvollständige Vertreter
)
Hier werden alle Vertreter aufgelistet, welche keinen
Eintrag in den Provisionsmerkmalen besitzen, bei denen jedoch auf
Einzelprovision gestellt ist. (das heißt, dass dieser Vertreter einer
Vertretergruppe zugeordnet ist, welche die Konfiguration „Einzelprovision = Ja“
hat)
Felder:
Feld
Bedeutung
Nummer
Nummer des Vertreters
Name
Name
      des Vertreters
Matchcode
Suchmöglichkeiten des Vertreterstamm
Feld
Bedeutung
Vertreter
Von…
      Bis…
Funktionen des Vertreterstamm:
Feld
Bedeutung
Ändern (F5), Ansicht (F6), Löschen
      (F7), Neu (F8)
Ruft
      den Pfleger des Vertreterstamm auf.
Vertreterabrechnung (F9)
Öffnet die
Vertreterabrechnung
.

---

## Funktionen des VIMP-Pflegers

Funktionen des VIMP-Pflegers
In der Optionbox der Masken und der Auswahlliste
existieren folgende Funktionen:
Funktionen des VIMP-Pflegers
Funktion
Beschreibung
Status
      zurücksetzen.
(STRG+F5)
Mit dieser
      Funktion wird auf der Auswahlliste der markierte Datensatz, wenn der
      Status 3 bis 7 oder 9 ist, auf 2 zurückgesetzt. Bei Problemen werden diese
      im Fehlerprotokoll angezeigt.
Datensatz
      als gelöscht markieren.
(STRG+F7)
Mit dieser
      Funktion wird der Status auf 9 gesetzt.
Löschen
(F7)
Öffnet die
      VIMP-Pfleger-Maske für den markierten Datensatz im Löschmodus. Es kann nur
      gelöscht werden, wenn der Status vorher auf 9 gesetzt wurde.
Standardvorgang erzeugen
Es wird aus
      den Daten des markierten Vorgangsimportes ein Vorgang erzeugt. Bei
      Problemen werden diese im Fehlerprotokoll angezeigt.
Für die Funktion Status zurücksetzen gibt es einen
Sonderfall. Vorgangsimport mit Vorgangsklasse 500(Ladeschein) und
1500(Eingangsladschein) werden mit der Funktion immer auf Status 5 gesetzt.
Standardvorgang erzeugen
Allgemein
Mit dieser Funktion kann ein Vorgang aus den
Importieren Daten erzeugt werden. Es müssen die Positionen in der Auswahlliste
markiert werden, aus denen dann ein Vorgang erzeugt werden soll und diese dürfen
keine rotmarkierten Felder mehr in der Auswahlliste besitzen.
Kann ein Vorgang bei der Vorgangserzeugung nicht
angelegt werden, so wird der Status für den Stammsatz und allen dazugehörigen
Positionen auf „Fehlerhaft“ gesetzt.
Kann eine Position bei der Vorgangserzeugung im
Vorgang nicht angelegt werden, so wird der Status für diese Position auf
Fehlerhaft gesetzt. Ansonsten wird nach erfolgreicher Erstellung des Vorgangs
der Status für beide Kennzeichen auf „Erledigt“ gesetzt. Des Weiteren wird die
Vorgangsnummer und die Vorgangsid in des Stammsatz geschrieben, so hat man den
Überblick darüber, welcher Vorgang aus diesem Satz erzeugt worden ist.
Folgende Felder werden in den Vorgang
üb
[...]


---

## Artikelausprägung Seriennummer

Artikelausprägung Serienn
ummer
Mit der Funktionstaste
Shift+F6
oder der Funktion
Ausprägung
können Ausprägungen an der
Warenposition hinterlegt werden. Eine Ausprägung eines Artikels ist z.B. eine
Seriennummer.
Es ist möglich mehrere Ausprägungen an einer Position
zu hinterlegen. Des Weiteren wird nicht geprüft, ob diese Ausprägung schon in
einer anderen Warenposition verwendet wird.
Folgende
Einrichterparameter
haben Einfluss auf die Erfassung
der Ausprägung.

---

## Kontrakte

Kontrakte
Kontraktartikelausweichliste
Ist für einen Kontrakt eine
Kontraktartikelausweichliste hinterlegt, so wird im
GFV
das Feld
Artikelnummer farblich hinterlegt. Zusätzlich werden im
GMV
die
Artikelnummern der Ausweichliste in neu hinzugefügten Zeilen angehängt, auch
diese sind farblich hinterlegt. So hat der Bediener sofortigen Überblick über
die vorhandenen Ausweichartikel.
Die Kontraktartikelausweichliste kann jetzt direkt
bearbeitet werden, indem
der Cursor über dem markierten Feld Artikelnummer im
GFV
positioniert, das Kontextmenü geöffnet und der Kontextmenüpunkt
Kontraktartikelausweichliste
bearbeiten
ausgewählt wird.
Auswahl eines
Kontraktes in der Strecke
Ist in dem
Profil
für die
Strecke der Schalter „Erweiterte Kontraktanzeige“ auf der Registerkarte
Griddefinition
auf
„Ja“ gestellt, so werden die möglichen Kontrakte mit ihren Artikeln und so wie
den Artikeln der
Kontraktausweichliste
angezeigt. Bei einer
nachträglichen Artikelauswahl werden nur die Artikel angezeigt, welche dem
Kontrakt zugeordnet worden sind. Wird ein Artikel aus der zugewiesenen
Ausweichliste
ausgewählt, so
wird dieser bei der Vorgangserzeugung mit in die
Kontraktartikelliste
übernommen. Ist der
Schalter „Fixpreis“ in der
Ausweichliste
auf „Nein“ gestellt, so wird als
Kontraktpreis, der Preis des ersten Artikels aus
Kontraktartikelliste
genommen. Steht der
Schalter auf „Ja“, so wird als Kontraktpreis, der Preis aus der
Ausweichliste
für den
gewählten Artikel übernommen.
Ist der Schalter „Erweiterte Kontraktanzeige“ auf der
Registerkarte
Griddefintion
auf
„Nein“ gestellt, erfolgt die Standard Kontraktauswahl.
Folgende Felder werden durch die Auswahl eines
Kontraktes vorbelegt.
Kontrakt, Artikel, Menge und Preis.

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

## Maske Position auf Ladeträger

Maske Position auf Ladeträger
Die Maske ermöglicht die Zuordnung von Artikeln zu
unterschiedlichen Ladeträgern, die wiederum verschiedenen Lokalitäten zugeordnet
werden können.

---

## Vorgangstexte

Vorgangstexte
Stammdatenpflege
Konstanten Artikelstamm
Textbausteine
Oder Direktsprung [TBS]

---

## Vorgangstext-Pfleger

Vorgangstext-Pfleger
Felder des Vorgangstext-Pflegers:
Feld
Beschreibung
Vorgangstextklasse
Wo
      soll der Text eingesetzt werden:
-
Allgemein
      verwendbarer Text
:
immer auswählbar
-
Textbaustein
:
z.B. als Textbaustein im
      Vorgangshauptteil
-
Kopkommentar
      1 – 10
:
als
      Kommentartext im Formularkopf
-
Fußkommentar
      1 – 10
:
als
      Kommentartext im Formularfuß
-
Rohwarentext
:
Text für
      Rohwarenabrechnung
-
Ihr
      Zeichen
:
-
Unser
      Zeichen
:
-
Bestelltext
:
Textnummer
ID
      in der Textklasse (muss eindeutig sein)
Bezeichnung
Bezeichnung des
      Vorgangstextes
Textersetzung
Hier
      wird festgelegt, wie der Text später bearbeitbar ist:
-
Zu
      ersetzender Text
:
Dieser Text enthält
      Platzhalter, die im Vorgang durch manuelle Eingabe gefüllt
      werden
-
Text
      kopieren
:
Der Text wird vollständig
      übernommen
-
Nur als
      Verweis
:
speichert den Text nur einmal
      und zwar immer den letzten Änderungsstand
Maximale Vorgangsstufe
Zu
      welchem Zeitpunkt in der Vorgangsverabeitung soll der Vorgangstext
      übernommen werden
Vorgangsklasse
Für
      welche Vorgangsklasse soll der Text anwendbar sein
Vorgangsunterklasse
Für
      welche Vorgangsunterklasse soll der Text anwendbar sein
Funktionen des Vorgangstext-Pflegers:
Funktion
Beschreibung
Speichern (F9)
Speichert den aktuellen Datensatz
      ab
Text-Zuordnung (F10)
Öffnet den Pfleger der
      Textbausteine

---

## Vorkommen Ansichten sichten

Vorkommen Ansichten sichten
Die Variante „Ansichten – Vorkommen“ dient dazu, sich
einen Überblick zu verschaffen, wo im Programm welche Ansicht aufgerufen
wird.
Für Entwickler und für „Private Funktionen“ steht der
Anwendungsfunktionspfleger im Bearbeiten-Modus zur Verfügung, in allen anderen
Fällen im Ansehen-Modus.

---

## Weitere Kopiermöglichkeiten

Weitere Kopiermöglichkeiten
Bei der Vorgangserfassung besteht in der
Warenpositionsmaske die Möglichkeit der Kopie von einem Lager, vorausgesetzt,
der Steuerungsparameter ist gesetzt.
(SPA
⇨
Artikelstammdaten
⇨
Artikel-Neuanlage bei Warenposition auf „JA“)
Ist während einer Lagerumbuchung der Artikel auf dem
Ziellager nicht vorhanden, erhält man die Möglichkeit, diesen dort automatisch
anlegen zu lassen.

---

## Workflow Verbuchungsregeln Pfleger

Workflow Verbuchungsregeln Pfleger
Name
Beschreibung
Kunde
Kundennummer des Kunden und Name des
      Kunden
Fremdartikel
Alternative Artikelnummer zu einem
      eigenen Artikel und Bezeichnung des Fremdartikels
Gültig ab
Zeitpunkt ab dem die
      Verbuchungsregel gültig ist.
Sachkonto
Eigene Kontonummer (Quelle ist der
      Kontenplan aus dem Mandantenstamm)
Kostenstelle
Nummer der Kostenstelle
Kostenobjekt
Nummer des
      Kostenstellenobjektes
Kostenträger
Nummer des Kostenträgers
Dieser Pfleger
ermöglicht die Abbildung eines Fremdartikels, angegeben durch eine
Fremdartikelnummer, auf interne Sachkonten, Kostenstellen, Kostenobjekte und
Kostenträger.
Diese
Abbildungsvorschrift kann durch die Angabe eines Datums im Zeitverlauf geändert
werden.

---

## Workflow Verbuchungsregeln Variante 1 WorkflowVerbuchungsregeln

Workflow Verbuchungsregeln Variante 1
WorkflowVerbuchungsregeln
Auswahlliste
Name
Beschreibung
KundenNummer
Kundennummer des Kunden
Name
Name
      des Kunden
Fremdartikelnummer
Alternative Artikelnummer zu einem
      eigenen Artikel
Fremdartikelbezeichnung
Bezeichnung des
      Fremdartikels
Kontonummer
Eigene Kontonummer (Quelle ist der
      Kontenplan aus dem Mandantenstamm)
Kontobezeichnung
Name
      des Kontos
Kostenstelle
Nummer der Kostenstelle
Kostenstellenobjekt
Nummer des
      Kostenstellenobjektes
Kostenträger
Nummer des Kostenträgers
Gültig
Zeitpunkt ab dem die
      Verbuchungsregel gültig ist.
Suchoption
Name
Beschreibung
Kundennummer
Kundennummer des Kunden
Kontonummer
Eigene Kontonummer (Quelle ist der
      Kontenplan aus dem Mandantenstamm)
Gültig ab
Zeitpunkt ab dem die
      Verbuchungsregel gültig ist.
Funktionen
Name
Beschreibung
Ändern
(F5)
Öffnet den Pfleger für
      Workflow-Verbuchungsregel im Ändernmodus
Ansehen
(F6)
Öffnet den Pfleger für
      Workflow-Verbuchungsregel im Ansehenmodus
Löschen
(F7)
Öffnet den Pfleger für
      Workflow-Verbuchungsregel im Löschmodus
Neu
(F8)
Öffnet den Pfleger für
      Workflow-Verbuchungsregel im Neumodus

---

## Zollcode

Zollcode
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Zollcode
oder Direktsprung
[ZOC]
Hierbei handelt es sich um Stammdaten für eine
spezielle Lösung des Lebens­mittelimports. Bitte fordern Sie hierzu das
Spezialdokument an.

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

## Zusammensetzung

Zusammensetzung
Häufig ist es erforderlich, zum Artikel zusätzliche
qualitative Informationen sowie Bestandteilangaben zu führen und auszuwerten.
Die für einen Artikelstamm zu berücksichtigenden Merkmale werden aus der Liste
der definierten
Bestandteile
entnommen (F3-Auswahl) und um die benötigten Angaben vervollständigt.
Die Merkmale können werden mit eine Anteilswert
versehen werden. Bei stoffstrombilanzpflichtigen Bestandteilen (siehe
Stoffstrom-Bilanz-Daten
)
wird die für den Anteil zu verwendende Mengeneinheit angegeben: Der Wert 0
bedeutet dabei immer, dass der Anteilwert eine prozentuale Angabe ist.
Alternativ kann eine zur Stoffstrom-Ausweis-Mengeneinheit kompatiblen
Mengeneinheit gewählt werden mit der Bedeutung ‚Anteil in Mengeneinheiten pro
Grundmengeneinheit der Mengeneinheitsgruppe des Artikelstamms‘. Diese
Möglichkeit kommt insbesondere bei inkompatiblen Mengeneinheiten von
Stoffstrom-Komponente und Artikelstamm in Betracht (kg/hl).
Die Angabe in der Spalte
‚Nutzung in‘
legt die
Berücksichtigung der Merkmale in diversen Anwendungen fest. So werden zum
Beispiel in der Qualitätsauswertung (QAA) die Warenbewegungen hinsichtlich der
Merkmalswerte ausgewertet, die an dieser Stelle den Wert
‚
Qualitätserfassung‘
tragen.

---

## Zuordnung zum Artikel – Mengeneinheitsgruppe

Zuordnung zum Artikel – Mengeneinheitsgruppe
Hauptmenü
Stammdatenpflege
Konstanten Artikelstamm
Mengeneinheitsgruppen
oder Direktsprung
[MEG]
Im Artikelstamm wird eingetragen, welche
Mengeneinheiten im Einkauf und Verkauf für Menge und Preis bestimmend sind und
in welcher Mengeneinheit der Bestand geführt wird. Die Zusammenbindung der
Mengeneinheiten erfolgt in Mengeneinheitsgruppen:
Mengeneinheitsgruppe
      Felder
Nummer
Nummer der zu definierenden
      Mengeneinheitsgruppe.
Bezeichnung
Bezeichnung der
      Mengeneinheitsgruppe
Einheit Lager
Einheit in der der Bestand geführt
      wird
Einheit Verkauf
Einheit der Menge im
      Verkauf
Einheit Einkauf
Einheit der Menge im
      Einkauf
Einheit VKPreis
Einheit des Preises im
      Verkauf
Einheit EKPreis
Einheit des Preises im
      Einkauf
Bei
      LVS
Mengeneinheit LVS
Mengeneinheit, in der im
      Lagerverwaltungssystem (LVS) Mengen vereinnahmt, kommissioniert,
      umgepackt, gezählt und allokiert werden.
Optional:
Einheit Barverkauf
Einheit der Menge im Barverkauf.
      Dieses Feld ist optional und wird mit 0 vorbelegt. Bei der Einstellung 0
      wird die gleiche Einheit wie beim Verkauf verwendet.
Einheit BarVKPreis
Einheit des Preises im Barverkauf.
      Dieses Feld ist optional und wird mit 0 vorbelegt. Bei der Einstellung 0
      wird die gleiche Einheit wie beim VKPreis verwendet.

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

## Andere UNTERNUMMER

Andere UNTERNUMMER
Wie schon oben erwähnt, ist es manchmal notwendig, dem
Beleg eine andere Unternummer zu verpassen. Die Unternummer (V_Unternummer im
Vorgangstamm UND in der Vorgreservierung). Diese Nummer wird von uns derzeit
nicht vergeben oder erfragt – sie ist aber Teil des eindeutigen Schlüssels der
Vorgreservierung. Durch Vergabe einer anderen Unternummer (z.B. 1) kann man also
erreichen, dass dieselbe Belegnummer in einem Bereich vergeben wird, was sonst
nicht möglich wäre.
Bedienung: Erst im Masken Feld ‚V_UnterNummerim
Vorgangstamm’ die neue Nummer eintragen und dann auf den Button drücken.

---

## Anlagenkartei Stammdaten löschen (inkl. 29)

Anlagenkartei Stammdaten löschen (inkl. 29)
Zu den Stammdaten der Anlagenbuchhaltung gehören:
Anlagengruppen
FirmenstammGebäude-AfA
Sonder-AfA
Standorte
Beim Löschen der Stammdaten werden automatisch die
Bewegungsdaten
mit gelöscht.

---

## Anlagenkartei Bewegungsdaten löschen

Anlagenkartei Bewegungsdaten löschen
Zu den Bewegungsdaten der Anlagenbuchhaltung
gehören:
Die Anlagenmappe
Der Anlagenstamm
Nach Löschen der Bewegungsdaten ist die
Analagenbuchhaltung so bereinigt, dass keine Daten, also auch keine bereits
vergebenen Inventarnummern mehr vorhanden sind. Danach kann man z.B. den Import
wiederholen.

---

## Artikelaufnahme

Artikelaufnahme
Zusätzlich zu der Artikelliste (Stapel) können noch
weitere Artikel aufgenommen werden, die ggf. auch direkt in den Stapel
übernommen werden können. Bei der „Speichern unter“ Funktion stehen ja
normalerweise keine Artikelstapel zur Verfügung, so dass mit dieser Funktion
direkt Artikel zu dem Zielbeleg hinzugefügt werden können.

---

## Artikelausprägungen

Artikelausprägungen

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

## ARTIKELSTAMM [ARS]

ARTIKELSTAMM   [ARS]
Lieferant (F3 – Auswahl)
EAN (nur für Formulardruck)
Artikelnummer (des Lieferanten)
Mengeneinheit (der Bestellgröße)
Bestellgröße
Die Mengeneinheit muss passend zur Grundmengeneinheit
des Artikels gewählt werden, da sonst dieser Lieferant in der
Bestellvorschlagsliste nicht erscheint.
Artikel mit Gebinde werden in den Bestellvorschlägen
z.Zt. nicht unterstützt. Der Bedarf dieser Artikel kann bei den
Bestellvorschlägen gesondert betrachtet werden, muss aber manuell erfasst
werden.

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

## Artikelsuche

Artikelsuche
Generell wird davon ausgegangen, dass ausschließlich
über Artikelkonten gebucht wird (zum Problem der “Diversen Artikel” siehe weiter
unten).
In den Stammdaten hinterlegt sind verschiedene
Suchkriterien, anhand derer ein Artikel gefunden werden kann; dies sind z.B.
•
Artikelnummer
•
Artikelmatchcode(s)
•
Strichcodenummer(n)
•
Artikelbezeichnung
Am Beispiel der Artikelnummer ergibt sich folgender
Ablauf:
Wenn die Artikelnummer korrekt eingegeben wird,
erscheint rechts davon die erste Artikeltextzeile. Als nächstes Eingabefeld wird
das Mengenfeld abgefragt. Falls es sich nicht um den gewünschten Artikel
handelt, kann mit der Pfeil-Taste wieder in das Feld “Artikelnummer”
zurückpositioniert und die Eingabe wiederholt werden.
Bei unvollständiger oder falscher Eingabe der
Artikelnummer öffnet sich automatisch das Artikelauswahlfenster und es besteht
die Möglichkeit, mit alternativen Suchkriterien den Artikel zu finden, indem
eine andere Variante gewählt wird.
Im Auswahlfenster ist jedoch auch eine schrittweise
Suche möglich. Bei Eingabe der Nummer wird Ziffer für Ziffer geprüft. Wenn eine
Eingabe falsch ist, wird sie zurückgewiesen. Mit jeder Eingabe wird eine neue
Auswahlliste in der Box dargestellt. Wenn noch nicht alle Stellen eingegeben
wurden, die ersten Stellen aber bereits eindeutig sind, wird automatisch eine
Liste der Artikel angezeigt, für die diese Ziffern stimmen.
Bei Eingabe von Buchstaben muss vorher auf die
Variante Matchcode - Suche geschaltet werden. Für die Suche nach
Strichcodenummer muss auf die Variante EAN umgeschaltet werden. Die Bedienung
erfolgt analog zur Eingabe der Artikelnummer.
Auch ist es möglich, eine Auswahlvariante direkt im
Feld “Artikelnr.” aufzurufen: Mit
“3.ge”
werden alle Artikel
aufgerufen, in denen
“ge”
enthalten ist.
Eine Suchvariante kann auch als Standardvariante
gesetzt werden; dann wird immer im Eingabefeld „Artikel“ die Suche nach dem
gesetzten Kriterium gestartet. Die „Setzung“ wird durch
[...]


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

## Belegfluss - Pfleger

Belegfluss - Pfleger
Postfach
Hier werden abhängig von
der
Prozedur
die Postfächer
angezeigt.
Status
Hier werden abhängig von
der
Prozedur
die Weiterleitungen
angezeigt.
Stammdaten
Name
Beschreibung
Aktuelles Postfach
Die
      Bezeichnung des aktuellen Postfachs
Fa-Id
Formulararchiv - ID
FA-MndNr
Formulararchiv - Mandantennummer
Zugehöriger Beleg
Name
Beschreibung
Typ
Hier
      wird angezeigt, ob es sich bei dem Beleg um einen Warenwirtschafts- oder
      Finanzbuchhaltungsbeleg handelt.
Nummer
Hier
      wird die Belegnummer angezeigt.
Buttons
Ändern/Ansehen/Löschen des
      Belegs
Kontierung
Name
Beschreibung
Belegtyp
Hier
      kann zwischen Ware und FiBu gewählt und damit können jeweils unnötige
      Felder ausgeblendet werden.
Belegart (Fibu)
Hier
      kann für die Finanzbuchhaltung eine Belegart (ER, EG, SO-Beleg) angegeben
      werden. Nur bei SO-Belegen kann das Sollhabenkennzeichen angegeben werden,
      bei Eingangsrechnungen und Eingangsgutschriften nicht. Ist keine Belegart
      hinterlegt, kann man zwar das Sollhabenkennzeichen angeben, es wird jedoch
      nicht in der Finanzbelegerfassung ausgewertet.
Lieferant/Kreditor
Nummer und Bezeichnung des
      Lieferanten/Kreditor
Mailadresse Kreditor
E-Mailadresse des Kunden in Bezug
      auf den Beleg
Belegnummer
Hier
      kann die Belegnummer des eingegangenen Beleges eingepflegt werden.
Belegdatum
Hier
      kann das Belegdatum eingepflegt werden.
Sind
      neben dem Belegdatum, die Felder für die FiBu-Buchungsperiode ausgefüllt,
      so wird das Belegdatum je nach Einstellung des Einrichterparameters „
Belegdatum mit Periode
      prüfen?
“ geprüft.
FiBu-Buchungsperiode
      (Periode/Jahr)
Hier
      kann eine Buchungsperiode für die
Finanzbuchhaltung
eingeben
      werden. Es dürfen nur offene Perioden und keine Abschlussperioden
      ausgewählt werden.
Hinweis
: Die Prüfungen, ob die eingebende
      Periode gültig ist, beziehen sich immer auf die FiBu-Periode.
[...]


---

## Belegfluss Variante 5 Belegfluss-Vorlage

Belegfluss Variante 5 Belegfluss-Vorlage
Funktionen
Name
Beschreibung
Ändern
(F5),
Ansehen
(F6),
Löschen
(F7),
Neu
(F8)
Ruft
      den Pfleger der Belegfluss-Vorlagen auf.

---

## Belegfluss-Vorlage

Belegfluss-Vorlage
Der Pfleger ist analog zur Kontierung auf der
Belegflussmaske aufgebaut. Die hier eingetragenen Vorlagen können anschließend
im Belegfluss einfach übernommen werden. Dies erspart Arbeit, wenn
beispielsweise monatliche Rechnungen mit immer dem gleichen Betrag eingetragen
werden.
Kontierung
Name
Beschreibung
Belegart (Fibu)
Hier
      kann für die Finanzbuchhaltung eine Belegart (ER, EG, SO-Beleg) angegeben
      werden. Nur bei SO-Belegen kann das Sollhabenkennzeichen angegeben werden,
      bei Eingangsrechnungen und Eingangsgutschriften nicht. Ist keine Belegart
      hinterlegt, kann man zwar das Sollhabenkennzeichen angeben, es wird jedoch
      nicht in der Finanzbelegerfassung ausgewertet.
Lieferant/Kreditor
Nummer und Bezeichnung des
      Lieferanten/Kreditor
Mailadresse Kreditor
Mailadresse für den Kunden in Bezug
      auf den Beleg
Belegnummer
Belegnummer
Zahlungsbedingung
Mit
      der
F3
-Taste kann hier eine
      Zahlungsbedingung ausgewählt werden. Die Zahlungsbedingung wird mit der
      Zahlungsbedingung EK aus dem Kundenstamm vorbelegt, sofern ein
      Lieferant/Kreditor angegeben wurde.
Bei
      der Auswahl einer Zahlungsbedingung wird das Feld „Skontosatz“ mit dem
      Skontosatz aus der Zahlungsbedingung gefüllt.
Skontosatz
Hier
      kann ein Skontosatz eingetragen werden. Bei der Auswahl einer
      Zahlungsbedingung wird das Feld „Skontosatz“ mit dem Skontosatz aus der
      Zahlungsbedingung gefüllt.
Brutto des Beleges
Bruttobetrag des Beleges
Steuerbetrag
Steuerbetrag des Beleges
Skontobetrag
Hier
      kann die Skontosumme des Beleges angegeben werden.
Kostenaufteilung
Name
Beschreibung
Betrag
Hier
      kann der Rechnungsbetrag eingegeben werden.
Skonto
Hier
      kann der Skonto-Betrag eingegeben werden.
Gegenkonto
Mit
      der
F3
-Taste kann hier ein
      Sachkonto ausgewählt werden.
Handelt es sich bei dem Sachkonto um
      ein Forderungs- oder Steuerkonto, so kann dieses nicht ausgewä
[...]


---

## Übernahme eines Excel-Arbeitsblattes in eine private Variante

Übernahme eines
Excel-Arbeitsblattes in eine private Variante
Stammdatenpflege
Stammdatenpfleger
Excel-Import
oder Direktsprung
[
EXCELI
]
Mithilfe des Excel-Importes kann ein
Excel-Arbeitsblatt in Referenz-ERP als private Variante integriert werden.
Schritt 1: Stammdaten anlegen
Mit dem Direktsprung
[EXCELI]
gelangt man in die Anwendung
„Excel-Import“. Dort kann mit der Funktion
Neu
[F8]
ein neuer Excel-Import-Stammdatensatz
angelegt werden.
Hier sind folgende Felder zu pflegen:
•
Name
: Name des
Excelimportes. Der Name ist gleichzeitig der Name der privaten Variante.
•
Speicherort
: Pfad der Excel-Datei,
die importiert werden soll.
•
Blatt-Name
: Name des
Excel-Arbeitsblattes, das importiert werden soll.
•
Anwendung
: Name der Anwendung, unter
der sich die private Variante befinden soll.
•
Offset
Zeile
/
Offset Spalte
: Ggf. kann hier
ein Wert ungleich Null eingetragen werden, wenn der Import nicht ab der ersten
Zeile/Spalte erfolgen soll.
Schritt 2: Excel-Import ausführen
Um den Excel-Import auszuführen, wird in der Anwendung
„Excel-Import“
[EXCELI]
der
entsprechende Stammdatensatz ausgewählt und anschließend die Funktion
Variante aktualisieren
F10
aufgerufen.
Beim Excel-Import wird eine Relation basierend auf dem
angegebenen Excel-Arbeitsblatt in der Datenbank angelegt und mit Daten des
Excel-Blattes gefüllt. Dabei werden die Spaltenüberschriften aus Excel in die
Datenbankrelation als Felder übernommen. Man beachte, dass aus technischen
Gründen die Namen der Datenbankfelder auf maximal 29 Zeichen verkürzt werden
müssen. Der Datentyp der Datenbankfelder hängt von dem „Datentyp“ von Excel ab
(siehe
Umschlüsselungen Excel zu Aeins
).
Zusätzlich zu den in der Excel-Datei angegebenen Spalten wird die Relation um
das Feld „xlsident“ erweitert. Dieses Feld fungiert als Primärschlüssel und kann
zur eindeutigen Identifizierung eines Datensatzes verwendet werden. Da der Name
des Primärschlüssels festgelegt ist, darf in dem Excel-Blatt keine Spalte mit
de
[...]


---

## Bestellung

Bestellung
Bei der Bestellung gibt es eine Besonderheit. Wenn in
der Relation
ImportVorgStamm
kein Lieferant zugeordnet worden ist und der Steuerparameter 883 auf „Ja“ steht,
so wird bei der Belegerzeugung sofern für den Artikel ein Lieferant eingerichtet
worden ist, der erste Lieferant automatisch zugeordnet. Bei der Zuordnung wird
die Aktuelle Position als gelöscht gekennzeichnet und es wird eine neue Position
mit der gleichen ÜbernahmeId und einer neuen SatzId erzeugt. Ist für den
Lieferanten noch eine nicht verarbeitete Bestellung offen, so wird diese
Position zu der anderen Bestellung hinzugefügt.

---

## Daten aktualisieren (Refresh)

Daten aktualisieren (Refresh)
Wenn man sich in einer AIS-Anwendung befindet, von
dort einen Pfleger aufruft, der die Daten verändert, und in die
darrunterliegende Maske zurückkehrt, kann es wünschenswert sein, dass die
Anzeige mit den geänderten Daten neu aufgebaut werden soll. Bei der
Datenherkunft SQL kann man einen Schalter „Refresh“ setzen. Es werden dann bei
allen Feldern, bei denen der Schalter auf
Ja
steht, beim wiederbetreten
der Maske die Daten neu eingelesen und angezeigt.
Zusätzlich steht eine Funktion
dbx_io
("AISREFRESH")
zur Verfügung, die das Aktualisieren der Felder auslöst.
Diese kann z.B. auf Pusch-Button als Controlstring eingetragen werden oder in
einem Makro verwendet werden. Diese Funktion hat als zusätzlichen Optionalen
zweiten Parameter den Feldname. Hat man viele Felder in AIS – darunter eventuell
viele Datentabellen - mit dem Refresh-Flag versehen, kann es Sinnvoll sein, nur
einzelne dieser Felder mit der Funktion AISREFRESH anzusprechen. Der Feldname
muss dabei so lauten, wie er auf der Maske steht, also ggf. mit Handel, Punkt
und $.
HINWEIS:
So einzeln angesprochene Felder
müssen nicht den Schalter Refresh auf
Ja
stehen haben.

---

## DB.Fkt.Num Text

DB.Fkt.Num Text
Hier gibt man den Namen einer privaten Prozedur ein,
wenn man Zahlen in Text ausgeschrieben haben möchte. Da dies von Sprache zu
Sprache unterschiedlich ist, kann man keine einheitliche Prozedur
verwenden.
Für die deutsche Sprache wird in Referenz-ERP eine
spezielle Prozedur
mitgeliefert. Um
diese zu verwenden macht man in diesem Feld die Eingabe Deutsch,Euro,Cent .
Näheres dazu auch unter dem Punkt
Betrag in Worten drucken
.

---

## Dialog ADR-Gefahrgutlisten Import

Dialog ADR-Gefahrgutlisten Import
Hauptmenü
Stammdatenpflege
Artikelstamm
ADR-Gefahrgutliste
oder Direktsprung
[ADR]
In der Anwendung ADR-Gefahrgutliste kann über die
Funktion „
Import aus ADR-Datei – F9“
der Dialog ADR-Gefahrgutlisten
Import gestartet werden. Die Verwendung unterliegt einer Lizenz und wird über
den
Steuerparameter „972 –
ADR-Gefahrgutlisten Lizenz“
gesteuert.
Feld
Beschreibung
ADR-Listen Datei
      …
F3
Auswahl öffnet den
      Datei-Explorer.
Pfadangabe zur ADR-Importdatei.
Diese Datei MUSS eine durch Tab-Stopp getrennte Textdatei sein
. Sie
      wird entweder beim Erwerb der BAM-Lizenz von der Bundesanstalt für
      Materialforschung und –Prüfung in dieser Form oder als Excel-Datei
      geliefert.
Im
      Falle einer Excel-Datei kann Excel aus den enthaltenen Daten eine
      Tab-Stopp getrennte Datei erzeugen.
Schaltfläche
      „Ordner“
Hierüber kann der Datei-Explorer
      geöffnet und zur Suche nach der entsprechenden Datei verwendet
      werden.
Importieren
Wenn
      eine Datei angegeben wurde, können die Daten über diese Schaltfläche nach
      Referenz-ERP importiert werden. Dabei werden auch bereits vorhandene Daten
      gelöscht, bevor die neuen eingefügt werden.

---

## Diensteanbieter

Dienstea
nbieter
Für verschiedene Geodatendienste gibt es verschiedene
Dienstanbieter, die jeweils einen sog. API-Key zur Identifikation zur Verfügung
stellen:

---

## DSGVO-Ansicht / DSGVO-Liste

DSGVO-Ansicht / DSGVO-Liste
In den Stammdatenpflegern der DSGVO-Objekte existiert
eine Funktion „DSGVO-Liste“. Diese verzweigt in eine Auswahlliste, in der alle
relevanten Daten dieses DSGVO-Objekts angezeigt werden. Hier hat man die
Möglichkeit über die Funktion „Report bearbeiten“ eine eigene Liste zu
erstellen. Dieser Report kann wie alle Reporte
archiviert
werden. Die
Anwendung ist so eingerichtet, dass beim Archivieren die Belegklasse, der
Belegtyptext, die Kontierung(dsgvo_ident) und ggf. die Kundennummer zum
Archiveintrag vermerkt werden.
Nach Beendigung eines Druckes wird in den Anschriften
dieses Objekts automatisch vermerkt, dass die Informationen gedruckt wurden.

---

## Einen Stammdatenpfleger aus einem MAKRO heraus aufrufen

Einen Stammdatenpfleger aus einem MAKRO heraus aufrufen
Es kann wünschenswert sein, einen Bestehenden
Stammdatenpfleger direkt aus einem Makro heraus aufzurufen. Dies kann z.B.
Notwendig sein, wenn vorher bestimmte Bedingungen geprüft oder Vorbelegungen
gemacht werden müssen. Dazu dient das JPP-Objekt „
JPfleger
“. Dieses
verwendet für den Aufruf der Maske Daten, die im Pflegerstamm (Direktsprung
[PST]
) hinterlegt sind.
Beispiel für Besuchsberichte:
Aufruf Bebericht für einen neuen Besuchsbericht:
SetLDB("TRANSFERS[1]",cKundId);
// Die KUNDID muss im Einfügemodus über
TRANSFERS[1] übergeben warden. Spezialität bei Besuchsberichten.
if(
JPPNEW ( "PFF" , "JPfleger" ) = 1 ) then
{
JPPIN
( "PFF", "PST_STAMM", "Besuchsberichte" )
// Zu
finden in der Anwendung „Pflegerstamm“ Direktsprung
[PST]
JPPEX
( "PFF", "
Einfuegen
"
)
// „Einfuegen“ legt einen neuen Datensatz
an
JPPDELETE
( "PFF"
)
}
Aufruf Bebericht für einen bestehenden
Besuchsbericht:
if(
JPPNEW ( "PFF" , "JPfleger" ) = 1 ) then
{
JPPIN
( "PFF", "PST_STAMM", "Besuchsberichte" )
// Zu
finden in der Anwendung „Pflegerstamm“ Direktsprung
[PST]
JPPIN ( "PFF", "KundId",     cKundId
)
// Siehe Idents im Pflegerstamm
JPPIN ( "PFF", "BeBerichtId", cBEbeId
)
// Siehe Idents im Pflegerstamm
JPPEX
( "PFF", "
Aendern
"
)
// „Aendern“ Ruft einen bestehenden Besuchsberich
ab. Für
// bestehende Besuchsberichte müssen alle Idents,
also KundID und
Beberichtid
// angeben werden
JPPDELETE
( "PFF"
)
}
Will man einen Besuchsbericht nur ansehen, so ist der
Syntax wie bei dem Aufruf des bestehenden Besuchsberichts, nur ersetzt man das
Schlüsselwort
„Aendern“
durch
„Ansehen“
.

---

## Eingegangene Post Bearbeiten/Beantworten

Eingegangene Post
Bearbeiten/Beantworten
Hauptmenü
Büro und Internet
Büroumgebung
Referenz-ERP Post
Direktsprung
[POST]
Mit der Funktion „Bearbeiten/Antworten“ F5 können sie
eingegangene Post bearbeiten,
Auf dieser Maske kann eine Notiz oder Antwort erfasst
werden. Mit der Funktion „
Antworten
“
F10
wird diese Antwort wieder
demjenigen zugeordnet, der die Nachricht erstellt hatte, so dass dieser dann die
Notiz dazu einsehen kann.
Der Haken bei „als gelesen markieren“ steht beim
Betreten einer Nachricht immer auf aktiv. Beim Verlassen der Nachricht wird
gefragt, ob die Daten gespeichert werden sollen. Wenn diese Frage mit
nein
beantwortet wird, dann wird weder der eventuell geänderte Notiztext
noch das Kennzeichen gespeichert.
Durch Deaktivieren des Hakens kann der Lesestatus
wieder zurückgesetzt werden.

---

## Einrichtung:

Einrichtung:
Im Artikelstamm werden die jeweiligen Lieferanten des
Artikels hinterlegt. Ist kein Lieferant im Artikelstamm hinterlegt, so erscheint
dieser Artikel nicht in der Bestellvorschlagsliste.

---

## Einrichtungsanweisungen

Einrichtungsanweisungen
Die Einstellungen in den Stammdatenpflegern
Kassenverwaltung, Kassensystemverwaltung, Kasseneinstellungen werden für
Erfassungen über POS gemäß Tresenkasse übernommen.
Außerdem werden auch alle Einrichtungen in Bezug auf
Formulareinrichtung übernommen.
Zur Ansteuerung über Vorgangsdruckklassen:
Für den Barverkauf (Klasse: Rechnung, Unterklasse:
Barverkauf erfassen) können mehrere Drucker und Formulare hinterlegt sein.
Für die Nutzung der POS-Kasse gilt folgende
Konvention:
Auf dem ersten dort hinterlegten Formular wird
parallel zur Artikelerfassung gedruckt, also sollte hier als erstes ein
40-Zeichen Formular hinterlegt sein, der die Bonrolle als Drucker auswählt; ein
Mitdruck auf einem Journal ist durch die Steuersequenz 1B 7A 31 am Druck Anfang
des zugeordneten Druckers in den Druckertypen gewährleistet (dieser Eintrag
müsste bei Nutzung des entsprechenden Druckers für die Tresenkasse schon
hinterlegt sein).
Achtung:
Bei anderen Druckern können diese Werte abweichen.
Wenn für verschiedene Kunden verschiedene
Vorgangsdruckklassen eingerichtet sind, muss dafür gesorgt werden, dass für den
Barverkaufsvorgang der Bondrucker mit zugehörigem Formular als erstes Formular
in der Zuordnung steht, denn es wird ja nur das erste Formular während der
POS-Erfassung gezogen.
Wenn in den Vorgangsdruckklassen kein spezielles
Formular für den Barverkauf hinterlegt/eingerichtet ist, wird das in FRZ als
Druckformular hinterlegte Formular auf dem in der Druckerzuordnung hinterlegten
Drucker ausgedruckt. (wenn keine Druckerumleitung eingerichtet ist, auch keine
LPT-Umleitung in der AHOI.INI).
In beiden Fällen wird der Positionsteil des
Bildschirmformulars aus FRZ für die Anzeige der Artikel im Fenster der POS-Kasse
herangezogen, allerdings ist dort die Breite auf 75 Zeichen beschränkt.
Hier ein Beispielformular:
WICHTIG:
Wie auch bei der Tresenkasse so muss auch jede
aktivierte POS-Kasse mit einem  in der Ahoi.ini in der Sektion ACASH[2] mi
[...]


---

## Engagement nach Artikelnummer

Engagement nach Artikelnummer
Das Kontraktengagement nach Artikelnummern ist allein
schon von der Wortwahl konträr zu diskutieren, Einzelartikel haben wenig mit
Engagement zu tun. Werden verschiedene Weizensorten kontraktiert, dann bezieht
sich das Engagement auf eine einzelne Weizensorte, was aber keine Information
über eine long/short Position innerhalb des Artikel spiegelt.

---

## Excel-Import: Anwendung

Excel-Import: Anwendung
Stammdatenpflege
Stammdatenpfleger
Excel-Import
oder Direktsprung
[
EXCELI
]
Feld
Name
Der
      Name des Excel-Importes und der privaten Variante.
Speicherort
Der
      Pfad der Excel-Datei.
Blatt-Name
Der
      Name des zu importierenden Excel-Arbeitsblattes.
Anwendung
Der
      Name der Anwendung, unter der sich die private Variante
      befindet.
Offset Zeile;Spalte
Siehe
Offset Zeile
und
Offset
      Spalte
Erstellt von
Benutzer, der den
      Excelimport-Stammsatz angelegt hat.
Erstellt am
Zeitpunkt, zu dem der
      Excelimport-Stammsatz angelegt wurde.
Spalten als Text
Siehe
Spalten als
      Text
Funktionen
Ändern
[F5]
, Ansehen
[F6]
, Neu
[F8]
, Löschen
[F7]
siehe
Excel-Import: Pfleger
Variante aktualisieren
[F10]
Führt den Excel-Import aus und
      aktualisiert die Variante.
Variante starten
[F9]
Wechselt in die betreffende
      Variante.
Exceldatei öffnen
[SF9]
Öffnet die Excel-Datei.
F2-Bereichsauswahl
Suchen
Sucht in den Feldern
•
Name
•
Speicherort
•
Blatt-Name
•
Anwendung

---

## Excel-Import: Pfleger

Excel-Import: Pfleger
Stammdatenpflege
Stammdatenpfleger
Excel-Import
oder Direktsprung
[
EXCELI
]
Feld
Name
Die
      eindeutige Bezeichnung des Excelimportes. Der Name dient gleichzeitig als
      Beschriftung der privaten Variante.
Register
„Allgemein“
Feld
Speicherort
Der
      Pfad der Excel-Datei. Mit der
F3
-Taste öffnet sich der
      Datei-Explorer.
Blatt-Name
Der
      Name des Excel-Arbeitsblattes, das nach Referenz-ERP importiert werden soll. Der
      Blatt-Name wird mit „Tabelle1“ vorbelegt.
Anwendung
Hier
      wird der Name der Anwendung angegeben, unter der sich die zu erstellende
      Variante befinden soll. Mithilfe der
F3
-Taste kann eine Anwendung
      ausgewählt werden.
Offset Zeile
Mit
      dem „Offset Zeile“ wird die Anzahl an Zeilen angegeben, die beim Import
      übersprungen werden. Befinden sich die Überschriften in dem Excel-Blatt
      nicht in der ersten Zeile, so kann hier ein alternativer Wert eingetragen
      werden. Handelt es sich bei der ersten Zeile des Arbeitsblattes um die
      Überschriftenzeile, so ist hier eine „0“ einzutragen.
Der
      Standardwert ist „0“.
Beispiel:
Befinden sich die
      Spaltenüberschriften in Zeile „3“, so ist hier ein Offset von „2“
      einzutragen. Die ersten zwei Zeilen werden übersprungen.
Offset Spalte
Mit
      dem „Offset Spalte“ wird die Anzahl an Spalten angegeben, die beim Import
      übersprungen werden. Soll der Import nicht ab der ersten Spalte erfolgen,
      so kann hier ein Wert ungleich „0“ eingetragen werden. Ein Wert von „0“
      bedeutet, dass der Import ab der ersten Spalte erfolgen soll.
Der
      Standardwert ist „0“.
Beispiel:
Beginnen die Daten in Spalte „3“
      („C“), so ist hier ein Offset von „2“ anzugeben. Damit werden die ersten
      beiden Spalten übersprungen.
Spalten als Text
Standardmäßig hängt der Datentyp der
      Datenbankfelder von dem Format der Excel-Spalten ab (siehe
Umschlüsselungen
      Excel zu Aeins
). Dieses Verhalten l
[...]


---

## Führung von Devisenkonten.

Führung von Devisenkonten.
Devisenkonten sind Bankkonten, die in einer anderen
als der Buchwährung geführt werden. Um ein Konto als Devisenkonto zu führen,
sollte man in den
Sachkonten
-Stammdaten (Direktsprung
[
SKS]
) den Schalter „Buchwährung vorbelegen“ auf
Nein
stellen und
die Währung auf die Währung des Kontos einstellen. Dies bewirkt
folgendes:
1.
In der Belegerfassung der Finanzbuchhaltung wird, wenn als Hauptkonto dieses
Sachkonto verwendet wird, sofort die Währung für jede Position mit dieser
Währung vorbelegt.
2.
Wenn der Steuerungsparameter „Anzeige des Fremdwährungssaldo in der Fibu“ auf
Ja
steht, so wird zusätzlich der Saldo des Kontos in der im
Sachkontostamm angegebene Währung angezeigt.
3.
In der Konteninformation wird im Informationsbereich der Saldo zusätzlich in
dieser Währung angezeigt. Das Standardformular ( -99 ) ist darauf angepasst. In
privaten Formularen können folgende Druckpositionen verwendet
werden:
•
Saldotext
Fremdwährung (2478)
•
Saldo erfasst
Fremdwährung (2481)
•
SaldoSH erfasst in
Fremdwährung (2482)
Diese Felder werden
nur angezeigt, wenn die oben beschriebenen Bedingungen erfüllt sind, ansonsten
werden diese Felder automatisch ausgeblendet.
Die Besonderheit der Devisenkonten sind die
entstehenden Kursdifferenzen und das Buchen dieser. Beim Einkauf der Devisen
liegt ein bestimmter Währungskurs zum Tage X zugrunde. Zum Zeitpunkt der
Verwendung der eingekauften Devisen hat sich der Kurs jedoch sehr wahrscheinlich
verändert. Die Differenz muss dann als Kursdifferenz ausgebucht werden:
EUR
Kurs
PLN
Deviseneinkauf
100.000,00
3,9646
396.460,00
Zahlung einer Rechnung
47.939,79
4,1719
200.000,00
Zahlung einer Rechnung
36.035,17
4,1626
150.000,00
Differenz
16.025,04
46.460,00
Bewertung Perioden
11.127,61
ç
4,1752
46.460,00
Kursdifferenz
4.897,43
0,00
Am Ende der Periode befinden sich also noch 46.460,00
PLN auf dem Devisenkonto. Diese werden dann mit dem Tageskurs laut den in Referenz-ERP
eingetragenen Währungsku
[...]


---

## Fontverwaltung beim Formulardruck

Fontverwaltung beim
Formulardruck
Bisher standen beim Formulardruck im Windows-Modus nur
zwei Fonts zur Verfügung, die im Druckerstamm hinterlegt werden. Aus diesen
Fonts wurden die im Asciidruck möglichen Attribute (normal, compress, fett,
gesperrt) nachgebildet. Es ist nun möglich, in einem Formular beliebig viele
Fonts zu benutzen! Fonts werden in einer
Fonttabelle
hinterlegt und im
Formularstamm kann dann
eine Fontabelle
ausgewählt werden. In den Druckpositionen kann unter Details
in einem neuen Feld ein Font aus der zugeordneten Fonttabelle gezogen werden. Da
die bisherige Windowsdruckvariante weiterhin bestehen bleibt, wird die
Druckvariante nach Folgendem Schema bestimmt.
1. Druckerstamm nicht
auf Windowsdruck:
- es wird im ASCII Druckmodus gearbeitet
2.
Druckerstamm auf Windowsdruck gestellt:
- Formularstamm hat
Fonttabellennummer 0 -> alter Windowsdruck
- Formularstamm hat
Fonttabellennummer ungleich 0 -> neuer Windowsdruck.
Beim
Druck mit einer Fonttabelle werden die im Druckerstamm hinterlegten Fonts NICHT
ausgewertet; nur die Fontangaben aus der Fonttabelle sind maßgeblich!
Komponenten der Fonttabelle
Basisfont:
Dieser Font wird zunächst zur Bestimmung des
Positionierungsrasters bestimmt, d.h. die Größe dieses Fonts legt fest, wie
viele Spalten und Zeilen auf dem Formular bedruckt werden können (großer Font =
weniger Spalten / Zeilen, kleiner Font = mehr Spalten / Zeilen).
Die
Positionierung eine Druckposition (wie im Formulareinrichter unter Spalte /
Zeile hinterlegt) richtet sich also nach diesem Raster, gleichgültig, mit
welchem Font eine Druckposition tatsächlich gedruckt wird!  Der Basisfont
dient ferner auch als Ersatzfont für alle Druckpositionen, denen kein Font
zugeordnet wurde.
X-Skalierung / Y-Skalierung:
Es hat sich gezeigt, dass das aus dem Basisfont
bestimmte Raster manchmal zu eng oder zu groß ist. Mit diesen Faktoren kann das
Raster in feineren Schritten gestaucht (kleiner 1) oder gestreckt (> 1)
werden.
Reduzier
[...]


---

## Geschäftsjahre und Perioden löschen

Geschäftsjahre und Perioden löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
GESCHJAHRSTAMM
PERISTAMM

---

## Gesellschaftsstamm

Gesellschaftsstamm
Über den Direktsprung
[GESEL]
gelangt man in die
Gesellschafterverwaltung. In der Variante Gesellschaftsstamm sind hier die
Stammdaten zu pflegen.
Je nach Satzung sind hier die grundlegenden Daten
einzugeben. Die Eintragungen sind je Geschäftsjahr zu hinterlegen, es wird
jeweils nur ein Geschäftsjahr als aktiv ( Einstellungen sind heranzuziehen )
gekennzeichnet.
Maskenfeld
Bedeutung
Pflichteinzahlung
Hier
      wird der Prozentsatz der Pflichteinzahlung von der Anteilshöhe angegeben.
      Auf dieser Basis errechnet sich die Größe fehlende
      Pflichteinzahlung.
Pflichtanteilsbezug
Bezieht sich der Prozentsatz
      Pflichteinzahlung auf Pflichtanteile [Ja] oder auf alle Anteile
      [Nein].
Bilanzkonto Einlagen
Hier
      ist dasjenige Bilanzkonto einzutragen, welches die Summe der eingezahlten
      Geschäftsguthaben darstellen soll.
Kapitalertrag -
      Gegenkonto
Im
      Fall Genossenschaft unerheblich, bei Personengesellschaften ist hier das
      Gegenkonto Kapitalertrag einzutragen.
Höhe
      der Anteile
Hier
      wird bei Genossenschaften der feststehende Wert eines Anteils in
      Buchwährung eingetragen.
WRV
      – Absatz %
Prozentwert zur Bestimmung des WRV –
      Betrages im Absatzgeschäft ( Einkauf )
WRV
      Verw. Guthaben
Anteil des über die fehlende
      Pflichteinzahlung hinausgehenden WRV – Betrages, der für die Erhöhung des
      Geschäftsguthabens verwendet wird.
Beschlussdatum
Beschlussdatum der
      Gesellschafterversammlung zur Ergebnisverwendung.
Anteilszeichnung ( Auto
      )
Bei
      [Ja] können aus dem WRV – Betrag neue freiwillige Anteile gezeichnet
      werden.
Kapitalertragssteuer
In
      entsprechenden Rechtsformen ist hier die Höhe der Kapitalertragssteuer in
      % des Jahres anzugeben.
Jahr
Wirtschaftsjahr, auf die sich die
      Einstellungen beziehen.
WRV
      Bezug %
Prozentwert zur Bestimmung des WRV –
      Betrages im Bezugsgeschäft
( Verkauf )
WRV
      Mi
[...]


---

## ImportVorgPosition

ImportVorgPosition
In dieser Relation werden Daten der
Vorgangswarenposition gespeichert.
Feld
Pflicht
Bedeutung
UebernahmeId
Ja
Übernahemid des
      Stammsatzes
SatzId
Ja
SatzId wie im Stammsatz(
      1)
PositionId
Ja
Positionszähler dieser muss manuell
      erhöht werden.
Status
Ja
Der
      Status der Position muss auf zwei gesetzt werden, ansonsten wird der Beleg
      nicht verarbeitet.
ArtikelNummer, ArtikelId,
      ArtiStammId
Ja
Artikel des Umzubuchende Artikels,
      wenn die ArtikelId übergegeben wird, dann muss in der Abgangszeile der
      Artikel des Abganglagers stehen und in der Zugangszeile die ArtikelId des
      Zugangslagers.
Bei
      Lagerumbuchung gilt:
•
In der
      Abgangszeile wird hier der Artikel des Abgangs eingetragen
•
In der
      Zugangszeile wird hier der Artikel des Zugangs eingetragen
LagerNummer
Wenn
      nicht Artikelid
Lagernummer der Position
Bei
      Lagerumbuchung gilt:
•
In der
      Abgangszeile wird hier die Lagernummer des Abgangslagers
      eingetragen
•
In der
      Zugangszeile wird hier die Lagernummer des ZugangsLagers
      eingetragen
LagerplatzNummer
Nein
Lagerplatz der Position
Menge
Ja
Hier
      wird die Menge eingetragen, bei einem Gebinde muss hier die Gebindeanzahl
      eingetragen werden
ME
Ja
Mengeneinheit der
      Position
ME_Preis
Nein
Mengeneinheit des
      Preises
Preiseinheit
Nein
Einheit des Preise
Preis
Nein
Preis der Position
Preisgesamt
Nein
•
0 Der Preis wird
      als Preis genommen
•
1 Der Preis der
      Warenposition als   Gesamtpreis gesetzt werden.
KontraktNummer
Nein
Nummer des Kontraktes
ZusatzInfo
Zusatzinfo begrenzt auf 40
      Zeichen
ZusatzInfo2
ZusatzInfo2 begrenzt auf 40
      Zeichen
PartieId, PartieNummer,
      PartieBezeich
Legt
      die Partie zu einer Zeile an. Die suche passiert zurzeit per Partienummer
      und oder Partiebezeichnung. Sollen mehrere Partiepositionen an eine
      Positionszeile übergeben werden, so muss die Tabel
[...]


---

## ImportVorgStammAddon

ImportVorgStammAddon
Vorgangs Addon
Aus dieser Relation werden Vorgangsaddon-Felder des
Vorgangs befüllt.
Der AddOnName muss dem des Feldes in der Tabelle
VorgangAddOn entsprechen. Anderenfalls werden die Daten nicht geschrieben.
Feld
Bedeutung
IVS_GUID
Guid
      des Stammsatzes
AddonName
Name
      des Addonfeldes
AddonWert
Inhalt des Feldes

---

## Importvorgstamm

Importvorgstamm
In dieser Relation werden Kopfdaten des Vorgangs
hinterlegt.
Feld
Pflicht
Bedeutung
UebernahmeId
Ja
Ident des Stammsatzes dieser muss
      mit in die Tabelle ImportVorgPosition für die dazugehörigen Positionen
      geschrieben werden.
Der
      Ident wird mit der Prozedur
Amic_dbx_ident(‘ImportVorgStamm‘,1)
      gezogen
SatzId
Ja
In
      diesem Feld ist eine 1 einzutragen.
Status
Ja
Der
      Status des Stammsatzes muss auf 2 gesetzt werden, ansonsten wird der Beleg
      nicht verarbeitet.
Ausnahme bildet hier die Umwandlung
      eines Ladescheins zu einem Lieferschein. Hier muss der Status 5 sein !
V_KlassNummer
Ja
Klassennummer des Typs
Siehe
Vorgangsklassen
V_UKlassNummer
Ja
Unterklasse des Vorgangs
V_Unternummer
Ja –
      sonst 0
0
Jahrnummer
Ja
Jahr
      des Beleges
ImportTyp
Ja
Dies
      wird nur bislang beim Ladeschein und Produktion ausgewertet.
•
0 Ist Auftrag
      -> Ladeschein -> Lieferschein / Rechnung
•
1 Normaler
      Ladeschein
•
10 Ändern einer
      Produktion
•
11 Explizite
      Änderung einer Produktion
Belegdatum
Ja –
      sonst aktuelles Datum
Wird
      das Datum des Beleges
Bedieneridneu
Ja
Erfasser des Beleges
IVS_GUID
Auto
Wird
      automatisch pro Satz erzeugt wird als Primary Key für abhängige Relation
      vom Stammsatz benötigt wie z.B. bei der Relation ImportVorgStammUFLD. Dies
      bedeutet, dass beim Einspielen der Daten das Feld ausgelesen werden
      muss.
KundNummer
Bei
      EK/VK
Kundennummer –
      Kunde/Lieferanten-Nummer des Vorgangs alternativ zur KundId
KundId
Bei
      EK/VK
KundID – Kunde/Lieferanten-ID des
      Vorgangs alternativ zur Kundennummer
ExterneReferenz
Nein
Wird
      als EDI_KU_Auftragsnummer im Beleg geführt – So kann die externe
      Belegreferenz im Beleg angezeigt werden.
V_NumNummer
Nein
Belegnummer – ist die gegebene
      Belegnummer bereits vorhanden und handelt es sich nicht um den Importtyp 1
      – (Umwandlung Ladeschein zu Liefersch
[...]


---

## ImportVorgStammZusatzTexte

ImportVorgStammZusatzTexte
Die Zusatztexte sind Texte, die nicht im Vorgang
direkt verwendet werden. Sie werden also im Gegensatz zum Vorgangs- oder
Positionstext nicht auf dem Beleg angezeigt und an einen umgewandelten Vorgang
weitergegeben. Vielmehr dient diese Relation zur Aufnahme von Texten, die für
spezielle Verwendungen wie z.B. Speditionspapiere herangezogen werden, die in
Verbindung mit dem Beleg gedruckt werden. So können hier Verladehinweise oder
dergleichen mitgegeben werden, die später in privatisierten Prozeduren angezeigt
und gedruckt werden können
Feld
Bedeutung
IVS_GUID
GUID des
      korrespondierenden Eintrags in der Relation
  ImportVorgStamm
TextTyp
Typ der Textzeile
      (Header/Line)
LineNo
Zeilennummer
Language
Sprache des
      Textes
TextZeile
Text dieser
      Zeile
Use
Verwendung z.B. für
      Packanweisung, Spedition, Lieferpapier o.ä.

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

## Informationen

Informationen
Warenbuchanzeige (SF2)
Verzweig in den Bereich Warenbuchauswertung
[WBA]
. Übergeben werden die Parameter Kunden-
und Artikelnummer.

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

## Itembox auf Zusatzinfo

Itembox auf Zusatzinfo
Das Zusatzinfofeld kann mit einer Itembox versehen
werden, die Itembox kann hier angegeben werden, z.B. kann es sein, dass das
Zusatzinfofeld immer das Herkunftsland einer Ware festlegt, dann kann an dieser
Stelle die Itembox des Staatstammes IB_STAASTAMM eingetragen werden.

---

## Kennzahlen für DTAZV

Kennzahlen für DTAZV
Hauptmenü
Mahn-,Zahl-, Zinswesen
Stammdaten
Kennzahlen für DTAZV
Direktsprung
[FIZVK]
Dies sind Stammdaten für
den Auslandzahlungsverkehr. Siehe
Auslandszahlungsverkehr in
Referenz-ERP
.

---

## Kirchensteuer

Kirchensteuer
Hauptmenü
Mahn-/Zahl-/Zinswesen
Stammdaten
Kirchensteuer Stammdaten
Direktsprung
[ZKS]
Beim Buchen des Zinsabschlages muss ggf. auch
Kirchensteuer berechnet werden. Diese wird in einem separaten Stammdatenpfleger
erfasst.
Damit die Kirchensteuer für bestimmte Kunden berechnet
wird, muss in der
Zinsgruppe
des Kunden die
Zinsabschlagssteuer aktiviert sein, ein Prozentsatz größer 0,0 in der
Kirchensteuer hinterlegt sein, im
Kundenstamm
unter Fibu-Merkmale die
Kirchensteuer hinterlegt sein.
Beschreibung
Nummer
Die
      Nummer wird selber vergeben. Sie muss eindeutig sein. Sie wird als
      Referenz im Kundenstamm unter den Fibumerkmalen hinterlegt.
Bemerkung
Hier
      kann textlich hinterlegt werden, für welches Bundesland oder welche
      Religionsgemeinschaft diese Kirchensteuer gilt.
Gültig ab
Ändert sich der Prozentsatz oder di
      Kontenzuordnung kann man hier hinterlegen, ab wann die neuen Werte gelten
      sollen. Alte Datensätze sollten beibehalten werden und neue zu einem neuen
      Gültigkeitsdatum erfasst werden.
Konto
Dies
      ist das Konto, auf das die Kirchensteuer gebucht wird.
Satz
Hier
      wird der Prozentsatz der Kirchensteuerhinterlegt. Der Kirchensteuersatz
      beträgt derzeit (2009) in Bayern und Baden-Württemberg 8 %, in den
      übrigen Bundesländern 9 %. Buchungen bei der Zinsberechnung erflogen
      nur, wenn hier ein Prozentsatz größer 0,0% eingetragen ist.
Text
Dieser Text wird beim Erstellen des
      Beleges unter „Übernahme in die Primanota“ verwendet. Gemäß § 45a Absatz 2
      und 3 EStG muss bei einer Bescheinigung über Kapitalertragsteuer neben dem
      Kirchensteuerbetrag nach § 51a Abs. 2c Satz 6 EStG die
      steuererhebende Religionsgemeinschaft im Klartext (z. B. Bistum
      Essen, Evangelische Landeskirche in Baden) erscheinen.
HINWEIS:
Damit dieser Text auf der
Steuerbescheinigung
, die als
      Formularvorlage -1200 zur Verfügung steht, erscheint, darf für das hier

[...]


---

## Kostenstellendimensionen

Kostenstellendimensionen
Hauptmenü
Kostenrechnung
Kostenstellenstamm
Kostenstellen
Funktion
Kostenstellendimensionen
Direktsprung
[KST]
Als Dimension bezeichnen wir ein frei wählbares
Kriterium, das für die Kostenrechnung einer Firma von Belang ist. Dimensionen
sind frei definierbar und ihre konkreten Inhalte pflegbar.
Wenn man sich dafür entschieden hat, die Kostenstellen
über das Dimensionsmodel zu verwalten, so muss man den Steuerungsparameter
„
Kostenstellen Dimensionen aktiv
“ auf
Ja
stellen, um dem System
mitzuteilen, dass der Zugriff auf die Kostenstellen jetzt über eine Kombination
aus bis zu 10 Dimensionen erfolgt. Es steht dann in der Anwendung zum Pflegen
der
Kostenstellen
(Direktsprung
[KST]
) eine weitere Funktion
Kostenstellendimensionen
zur Verfügung.
Hier kann man nun die Dimensionen erfassen. Dabei
sollte man aber von vornherein festlegen, wie diese auszusehen haben. Man kann
zwar später noch Änderungen vornehmen, jedoch werden bereits erfasste Daten
davon nicht mehr berührt.
Beschreibung
Label
Vor
      den eigentlichen Eingabefeldern muss zur Identifikation der Dimension eine
      Bezeichnung stehen. Diese wird hier eingetragen
Tabelle
Auf
      welche Tabelle soll sich diese Dimension beziehen. Es ist hier auch
      möglich, private Tabellen anzugeben. Diese Tabellen müssen eine Integer
      Feld zur eindeutigen Identifikation und ein Bezeichnungsfeld
      besitzen.
Feldname
Der
      Name des Integerfeldes zur eindeutigen Identifikation des Datensatzes.
      Eine Auswahl der Felder vom Typ Integer ist mit
F3
möglich.
Name
      Bezeichnungsfeld
Hier
      muss man den Namen des Feldes aus der Tabelle angeben, das die Bezeichnung
      enthält. Eine Auswahl der Felder vom Typ Character ist mit
F3
möglich. Dieses Feld wird in allen zugehörigen Erfassungsbildschirmen
      als Bezeichnung neben der Nummer angezeigt.
Itembox
Dem
      Feld muss eine Itembox zugeordnet werden.
Parameter
Bei
      den Dimensionen kann es s
[...]


---

## Lieferbelegpositionen SF8

Lieferbelegpositionen SF8
Über diesen Aufruf öffnet sich die Auswahlliste der
Lieferbelegpositionen.
Man kann 3 Felder für über den Lieferbelegstamm
angelegte Positionen verändern.

---

## LVS Stammdaten löschen (inkl. 26)

LVS Stammdaten löschen (inkl. 26)
Es werden die Daten in folgenden Tabellen
gelöscht:
LVS_Ladetraegertyp
LVS_Ladetraeger
LVS_Lokalitaeten
LVS_Lok_Maschinenartikel
Beim Löschen der LVS Stammdaten  werden
automatisch die
Bewegungsdaten
mit gelöscht.

---

## LVS Bewegungsdaten löschen

LVS Bewegungsdaten löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
LVS_LT_Lokalitaetszustand
LVS_LT_Lokalitaetsbewegung
LVS_Ladeeinheitstamm
LVS_LadeeinheitsPosition
LVS_LE_PositionBewegung
lvs_artikeltransfer_wabew

---

## LVS ungezählte Artikel

LVS ungezählte Artikel
In dieser Variante können alle gezählten und
ungezählten Artikel eines Geschäftsjahres oder eines Zeitraums angezeigt werden.

---

## Mahnsätze einrichten

Mahnsätze einrichten
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Direktsprung
[FIMSG]
.
Dieser Pfleger fasst alle vorherigen Pfleger für die
Mahnstammdaten zusammen. Es werden die einzelnen Mahngruppen untereinander und
die Mahnstufen nebeneinander dargestellt.
Über Anzeige lässt sich einstellen, welcher Wert in
der Kreuztabelle angezeigt werden soll.
Der Text der Mahnstufe lässt sich ändern, indem man
auf das Feld klickt oder mit ENTER bestätigt: Neue Mahnstufen lassen sich
über
(Neu)
eintragen.
Die linke Spalte mit den
Mahngruppen
funktioniert analog. Man
gelang also direkt von der Kreuztabelle in den Stammdatenpfleger.
Wenn man nun in die Kreuztabelle klickt oder mit ENTER
ein Feld auswählt, erscheint ein Pfleger, der sowohl den Mahnstamm als auch den
Mahnsatz beinhaltet. Es wir dort immer der aktive Datensatz, also der mit dem
größten "
Ab Datum
", angezeigt. Will man ab einem bestimmten Datum einen
neuen Mahnsatz einrichten, so erreicht man dies über "
Neuer Satz
F8
". Die
Texte
für diese Kombination lassen
sich über "
Texte
F5
"
erfassen.
Beschreibung
Mahngruppe
Angabe der Mahngruppe, für die die
      Bedingungen gelten
Mahnstufe
Angabe der Mahnstufe, für die die
      Bedingungen gelten sollen, z.B.
"1"
für
"Mahnstufe
      1"
Währung
Währung, für die die Mahngebühr
      gilt.
Ab
      Datum
Ab
      wann gelten diese Einstellungen.
Buchungstext
Ist
      hier ein Text eingegeben, so wird dieser bei der Übernahme der
      Mahngebühren in die Primanota verwendet, sonst der bei „
Übernahme in die
      Primanota
“
      als Einrichterparameter hinterlegte Buchungstext „Text Hauptzeile bei
      Übernahme der Mahnungen in die Primanota“
Formular-Id
Nummer des Mahnformulars, das
      ausgedruckt werden soll. Es kann somit für jede Kombination aus Mahngruppe
      und Mahnstufe ein eigenes Formular mit unterschiedlichem Aufbau bzw. Text
      hinterlegt werden. Man kann aber auch für jede Stufe dasselbe Formular
[...]


---

## Mahnvorschläge erstellen

Mahnvorschläge erstellen
Hauptmenü
Mahn-, Zahl-, Zinswesen
Mahnwesen
Mahnvorschläge erstellen
Direktsprung
[MHVE]
.
Nach Anwahl des Programmpunktes öffnet sich folgenden
Bildschirm:
Der
Mahnstichtag
steuert, welche Positionen auf
welcher Mahnstufe einbezogen werden. In den Stammdaten des Mahnwesens ist
hinterlegt, wie groß der Mahnabstand in Tagen von der Fälligkeit zur 1. Mahnung,
von der ersten Mahnung zur zweiten, etc. ist. In Abhängigkeit vom Mahnstichtag
und dem Mahnabstand werden also Belege einbezogen oder nicht.
Bemerkung
ist lediglich ein Text für den
Vorschlag.
Danach wird der
Kontobereich
bestimmt, für den
die Vorschlagsliste erstellt werden soll.
In der
automatischen Selektion
werden dann alle
mahnbaren Belege je Konto laut Einstellung in den Mahngruppen in die
Vorschlagsliste übernommen. Ausgeschlossen bleiben hier alle Kunden, die mit
Mahnsperre versehen sind oder deren Mahngruppe 0 ist, sowie alle Belege die mit
einer Mahnsperre versehen sind.
Bei der
manuellen Selektion
werden dagegen alle
mahnbaren Belege ohne Mahnsperre je Konto – ohne Kunden mit Mahngruppe 0 -
interaktiv vorgeschlagen:
Die ausgewählten Belege werden dunkel dargestellt. In
der Rechenzeile unterhalb des Anschriftenfeldes wird links der Gesamtbetrag der
ausgewählten Positionen inkl. Nebenkosten angezeigt. Die Summe setzt sich
zusammen aus den ausgewählten Positionen, der Mahngebühr (z.B. € 10.-) und den
aufgelaufenen Zinsen (z.B. bei 10 % Zinsen und dem angegebenen Zeitraum €
101,92.-).
Mit Betätigung von
F9
werden die Positionen
in den Mahnvorschlag übernommen.
Der zu mahnende Betrag ergibt sich als Summe aus allen
fälligen Belegen, die laut Einstellung in der Mahngruppe auf der Mahngruppe
erscheinen sollen. Also werden gegebenenfalls auch Habenbeträge mit verrechnet.
Dasselbe gilt für die Mahnzinsen. Ist der Mahnbetrag kleiner als der im Mahnsatz
hinterlegte kleinste Mahnbetrag, wird kein Mahnvorschlag erstellt.
Hat ein offener Posten bereits eine Mahnstufe

[...]


---

## Mahnzinsen

Mahnzinsen
Neben den Kontokorrentzinsen gibt es auch die
Möglichkeit Mahnzinsen zu berechnen. Mahnzinsen werden nur in Buchwährung
geführt. Diese werden Tag genau nach einem individuellen Zinssatz, der in den
Stammdaten(Zinsgruppen) hinterlegt ist, errechnet. Bitte beachten Sie, dass ein
Mixen von Kontokorrent- und Mahnzinsen für einen Kunden unsinnig ist.
Folgende Stammdaten müssen dabei berücksichtig
werden:
•
Im
Mandantenstamm
wird die Zinsbasis
hinterlegt, d.h. man entscheidet sich Firmenweit, welche Monatseinteilung man
bei der Zinsabrechnung verwenden will. In Referenz-ERP gibt es drei Möglichkeiten:
o
30 Tage im Monat beim 360
Tagen im Jahr
o
Monatstage (Jan=31;Feb=28;...)
bei 365 Tagen im Jahr
o
Monatstage (Jan=31;Feb=28;...)
bei 360 Tagen im Jahr
•
In der Zinsgruppe sollte mindestens ein Eintrag für Verzugszinsen aus
Mahnungen existieren. Bei der Einrichtung dieser Zinsgruppe ist zu beachten,
dass bei der Berechnung der Mahnzinsen nur der Soll-Zinssatz herangezogen
wird.
•
Diese Zinsgruppe muss dann für die Mahngruppe im
Mahnstamm
hinterlegt werden. Man kann
dort für jede Mahnstufe eine eigene Zinsgruppe hinterlegen
•
Es gibt zwei Möglichkeiten, wie die Mahnzinsen behandelt werden können.
Entweder man bucht bei jeder Mahnung die Zinsen, dann dürfen die Zinsen nur von
einer Mahnung bis zur nächsten Mahnung berechnet werden. Oder man bucht die
Zinsen erst, wenn die Mahnung inklusive Zinsen gezahlt bzw. die Forderung dem
Anwalt übergeben wurde. Dann muss die Mahnung den gesamten Zinsbetrag ausweisen,
also Berechnung ab Fälligkeitsdatum. Dies wird in den
Mahngruppen
unter „
Zinsen immer ab
Fälligkeit“
hinterlegt
Sind alle Stammdaten korrekt eingerichtet, werden beim
Erstellen der Mahnvorschläge die Zinsen berechnet. Bei der Berechnung der Zinsen
werden nur die Positionen herangezogen, die laut der Einstellung „
Wie
mahnen
“ in den
Mahngruppen
auf der Mahnung
erscheinen sollen. Dann werden auch nur die Positionen verzinst, die fällig
sind. Bei
[...]


---

## Mehrmandantensystem mit zentralem Stamm

Mehrmandantensystem mit zentralem Stamm
Das Referenz-ERP System erlaubt es mehrere Mandanten
parallel arbeiten zu lassen.
Mit Hilfe der Datenbank Proxy Technologie ist es
möglich, einen Mandanten als Basissystem zu kennzeichnen, in dem die Stammdaten
Kundenstamm und Artikelstamm gepflegt werden, um diese dann "online", also
direkt nach dem Neueintrag oder dem Änderungsdienst auf den angeschlossenen
Mandanten abzubilden. Des Weiteren gibt es zwei Übertragungsarten für  das
Mehrmandantensystem. Die erste Übertragungsart schreibt, die zu übertragenden
Dateien in die Untermandanten Direkt ein. Bei der zweiten Übertragungsart, die
per EPA einrichtbar ist, werden die Daten auf dem Zentralen System erst in eine
Zwischenrelation gespeichert. Ein Ereignis verteilt die Daten, dann auf die
passenden Untermandanten. Von unserer Seite aus empfehlen wir die Möglichkeit
des direkten Übertragens zu benutzen. Die Einrichtung finden Sie
hier
.
Zwei Begrifflichkeiten sind hierbei festzuhalten:
Begrifflichkeiten
Bedeutung
Zentralmandant
einer der Datenbanken muss als
      Zentralmandant festgelegt werden, von diesem Mandanten aus werden, die
      Untermandanten mit den Änderungen versorgt
Untermandant
Der
      Untermandant ist Nutznießer der zentral gepflegten Informationen, und zwar
      auf Basis der Kundennummer und/oder auf Basis der Kombination
      Lagernummer/Artikelnummer.
Untermandanten können selbstverständlich abweichende
Kundenstämme oder Artikelstämme führen, nur die im Zentralmandanten als
gemeinsam genutzte Kunden oder Artikel werden an die Untermandanten
abgegeben.
Es ist sogar auf Relationsbasis möglich, in den
Untermandanten "Überschreibungsschutz" festzulegen, und auch Default
Vorbelegungen für den Neufall festzulegen.

---

## Optionbox-Pfleger

Optionbox-Pfleger
Felder
Dialog „Option Box“
Option Box
Identifikation der
      Optionbox
Tabelle 1
Siehe
Übersicht der
      zugehörigen Funktionen
Zu
      bearbeitende Funktion
Gibt
      die jeweils zu bearbeitende Funktion an
Hilfetitel
Eingabehilfe zur Festlegung der
      Hilfe
Hilfetextmarke
Eingabehilfe zur Festlegung der
      Hilfe
Tabelle 2
Vorkommen der Optionbox
Tabelle 1
Übersicht der zugehörigen
      Funktionen
Funktion
Identifikation der
      Funktion
Label
Beschriftung
Bezeichnung
FT
Feste definierte Funktionstaste,
      übersteuert Eintrag „Taste“
Taste
Taste die dieser Funktion in dieser
      Optionbox zugewiesen wird.
Mit
      [
F3
] erhält man die Auswahl der möglichen Zuordnungen.
Gruppe
Gruppierungsmerkmal für Funktionen
      in der Optionbox.
Gängige Gruppen sind
      0,1,2,3.
Die
      Gruppe 0 und 1 stellen in aller Regel Basisfunktionalitäten zur
      Verfügung.
Gruppe 2 und Gruppe 3 erlangen
      besondere Bedeutung in Auswahllisten.
Gruppen wie z.B. 100 oder 1000
      werden beispielsweise oft per Software (OB_ADD, OB_REMOVE) zur Laufzeit
      dazu addiert bzw. entfernt.
EA
Einzelauswahl
Nur
      für „Gruppe 3-Funktionen“ in Auswahllisten
(Funktion wird nur aufgeführt, wenn
      mindestens eine Zeile markiert wurde)
Maus
Bestimmt ob die Funktion bei
      Doppelklick auf einen Auswahllisteneintrag ausgeführt werden
      soll.
Untermenü
Bestimmt das Untermenü in das die
      Funktion einsortiert werden soll.
Sort.
Bestimmt die Sortierung innerhalb
      der Optionbox.
Tabelle 2
Vorkommen der
  Optionbox
Anwendung
Ist
      keine Variante angegeben, dann ist die Optionbox dieser Anwendung
      zugeordnet.
Zusätzlich werden hier alle
      Source-Fundstellen der Optionbox angelistet.
Variante
Ist
      die Variante angegeben dann ist die Optionbox dieser Variante zugeordnet,
      die wiederum der obigen Anwendung untergeordnet ist
Funktionen
Hilfe zuordnen
      [
F10
]
Zuweisung einer Hilfe
[...]


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

## Passiv-Aktiv Vorbelegung

Passiv-Aktiv Vorbelegung
Die Vorbelegung für das Artikel Aktiv/Passiv Feld kann
hier hinterlegt werden.

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

## Pfleger

Pfleger
Der Pfleger wird durch folgende JPL-Prozeduren und
JAM-Masken realisiert:
SKRIPTPA.JPL, SCRIPTDE.JPL
SKRIPTPA.JAM,
SCRIPTDE.JAM         (erstellt von NW
29.7.98)
Aufruf in Aeins-Funktionen:
Die JPL-Funktionen werden als Anwendfunktionen in
unten dargestellter Weise eingerichtet.
Bearbeitungsrechte
Der Systemadministrator darf alles.
Die Bearbeitungsrechte an Script-Parameter werden
restriktiv gehandhabt.
Folgende Rechte
werden ausgewertet:
ENTWICKLER
darf:
Alles
Otto
Normalbenutzer mit OPT* darf:
ScriptPBesitzer=0: Ändern ScriptPPWert1-3,
ScriptPPAktiv
ScriptPBesitzer=1: alles
Allgemein
gilt:
Bei ScriptPId
beginnend mit "p_" wird automatisch ScriptPBesitzer=1 (privat) und
ScriptSystem=0,
Bei ScriptPId
nicht beginnend mit "p_" wird automatisch ScriptPBesitzer=0.
Bei
Berechtigungsstufe
Otto Normalbenutzer
wird automatisch ScriptPBesitzer=1
und ScriptPId nur beginnend mit"p_" zugelassen.
Bei ScriptPId
beginnend mit"p_" ist ScriptSystem=1 verboten.
Anmerkung:
ScriptSystem=1 wird aus dem
gewähltem Kopf geerbt und ist im Detailbereich nur bearbeitbar, wenn es im
Kopfsatz nicht gesetzt ist. Wenn man keine Bearbeitungsrechte besitzt, besteht
mindestens die Möglichkeit, die Daten anzusehen.
*„Normale“
Bediener, die das Recht erhalten sollen, private Script-Parameter zu bearbeiten,
müssen unter Direktsprung [OPT] einen Eintrag der nachstehenden Art
erhalten.
Auslesen von Parametern in Pascal-Scripten
Das Einlesen der Parameter geschieht mit folgender
Funktion:
ReadScriptParam
(ScriptPPId, ScriptPId,
ScriptPPWert1, ScriptPPWert2, ScriptPPWert3 : string) : integer;
Die Stringvariablen sollten mit mindestens 51 Stellen
deklariert und mit Leerstrings initialisiert werden.

---

## Pfleger

Pfleger
Datum
Das Gültigkeitsdatum des Planungsrezepts
Zielartikel
Setzen Sie hier die Artikel ein, für die Sie eine
Ressourcenplanung vornehmen wollen.
Komponentenartikel
Setzen Sie hier Artikel wie Rohwaren, Dienstleistungen
o.ä. ein, die Sie zur Erstellung der Zielartikel benötigen.
Sie können hier auch eine Partie für den Artikel
festlegen.
Geben Sie unbedingt eine Menge für diesen Artikel an.
Die Menge bezieht sich stets auf die Basismengeneinheit des Zielartikels. Wird
dieser also in Kilogramm (0.25, 0.5 oder 1.5Kg) erfasst, so beziehen sich die
Komponentenmengenangaben auf 1 Kg.

---

## Pflegerstamm

Pflegerstamm
Administration
Werkzeuge
Pflegerstamm verwalten
Stammdatenpflege
Stammdatenpfleger
Pflegerstamm verwalten
oder Direktsprung
[
PST
]
Der Pflegerstamm verwaltet Metadaten zum
automatisieren Aufruf von Stammdatenpflegern. Die bereitgestellten Informationen
zu einem Pfleger ermöglichen es,
-
die zugehörige Anwendung zu starten
-
den Pfleger für Testdatensätze zu begutachten
-
mit Hilfe des JPP-Objekts "JPfleger" den Stammdatenpfleger programmatisch aus
JPL, MAKRO oder VBA  aufzurufen
Funktionen der
      Auswahlliste
Pflege-Funktionen
Neu,
      Ändern, Ansehen, Löschen
Außer „Ansehen“ nur
      Entwicklung!
Test
Test-Aufruf des Stammdaten-Pflegers
      mit dem unter ‚Test Select‘ zugeordneten SQL Statement ( nur Entwicklung)
Anwendung
Start der Anwendung ( nur
      Entwicklung )
Erzeuge
      Quelltext-Snippet
Öffnet Editor mit Snippet für
      Pflegerstamm-Aufruf (Copy&Paste Verwendung) zur Verwendung in JPL (
      bei MAKRO Verwendung: ähnlicher Aufbau)
Suchen
Name
      wie
Suche in „Name“
Maske wie
Suche in „Maske“
Interface
Auswahl nach Interface
Rollen zugeordnet?
Ja/Nein
Entwickler
Suche in „Entwickler“
Felder des
Pflegers
Name
Pflegerstamm-Name, eindeutiger
      Bezeichner
Bezeichnung
Weiteres Feld für
      Erläuterungen.
Maske
Name
      der Maske
Anwendung
In
      welcher Anwendung ist dieser Pfleger eingebettet
zugehörige Optionbox
Optionbox des Pflegers
zuständiger Entwickler
Ansprechpartner für Branchen-ERP
Version
Festlegung welches
      Stammdaten-Verfahren intern verwendet wird.
•
Jpl_Interface
•
Kontext-Interface
Ident Select
Mit
      diesem SQL-Statement wird der zu pflegende Datensatz eindeutig bestimmt.
      Die Versorgung der optional 4 möglichen Identifizierungsparameter
      (ID1!..ID4) erfolgt  beim Aufruf über das JPP Objekt  mit den
       unter ‚interne Idents‘ festgelegen Parametern
Extern Select
Für
      Relationen, deren Primärschlüssel  von der  sichtbaren
      Identifizierung  abwe
[...]


---

## Preisfaktor

Preisfaktor
Per EPA kann noch der Preisfaktor eingebbar gemacht
werden, normalerweise zieht das System den Preisfaktor aus dem Artikel (stamm),
hier handelt es sich um den „Default Preisfaktor“

---

## Preismengeneinheit

Preismengeneinheit
Die Artikelpreismengeneinheit kann auf diesem
Eingabebildschirm festgelegt werden, hier ist vorstellbar, dass der Artikel in
kg geführt wird, der Preis sich aber auf eine Steige oder einen Kolli bezieht.

---

## Qualitätskriterien

Qualitätskriterien
Es werden alle Qualitätsmerkmale angezeigt, die in der
Rohwarengruppe dieses Artikels als Analysewert aus Waage zur Verfügung stehen.
Da zum Zeitpunkt der Erfassung u.U. noch keine Sorte
definiert ist, werden alle Qualitätskriterien angegeben.
Berücksichtigung finden später nur jene, die für die
Sorte relevant sind.

---

## Rabattsperre im Artikel

Rabattsperre im Artikel
Stammdatenpflege
Artikelstamm
Artikel
Oder Direktsprung
[AR]
Im Artikel kann das Rabattsperrkennzeichen gesetzt
werden, um zu verhindern, dass dieser Artikel rabattiert wird.
Es wird zwischen Rabattsperren im Einkauf und
Rabattsperren im Verkauf unterschieden. Somit können für den Verkauf und Einkauf
verschiedene Kennzeichen für die Sperrung des Rabatts vergeben werden.
Hier lassen sich verschiedene Einstellungen
vornehmen:
Einstellung
Bedeutung
Keine
Keine Rabattsperre (Voreinstellung)
Automatik
Automatische Rabatte werden
      gesperrt. Es erfolgt keine automatische Berechnung eines Rabatts aufgrund
      der Kombination von Rabattgruppe und Rabattklasse
Automatik + manuelle
Für
      eine Warenposition mit diesem Artikel erfolgt keine automatische
      Berechnung eines Rabatts aufgrund der Kombination von Rabattgruppe und
      Rabattklasse und es können auch keine Rabatte manuell erfasst werden.
manuelle
Für
      eine Warenposition mit diesem Artikel können keine Rabatte erfasst
      werden

---

## Registerkarte Steuern

Registe
rkarte Steuern
Auf der Registerkarte Allgemein steht der
Steuerschlüssel für diesen Artikel eingetragen. Soll bei Verwendung bestimmter
Steuergruppen ein abweichender Steuerschlüssel verwendet werden, so kann dieser
hier eingetragen werden.

---

## Relation VorgangUebergabe

Relation VorgangUebergabe
Die Relation VorgangUebergabe nimmt die
Vorgangsrohdaten auf, die nicht für die Rohware bestimmt sind.
Aus dieser Zwischenrelation werden über die
Aeins-Funktion VorgangUebergabeBelErz (Aufruf des Pascal-Scripts
VorgangEinspielung
) die Vorgänge erzeugt.
ArtikelNummer
char       20 0 .................... Y
N
BedienerIdKorr
integer     4 0
0
Y  N
BedienerIdNeu
integer     4 0 current
user         Y  N
BelegDatum
date        4 0
today(*)
Y  N
BelegNummer
integer     4 0
0
Y  N
CreateTime
integer     4 0 .................... Y  N
Datum
date        4 0
today(*)
Y  N
FilialNummer
integer     4 0
0
Y  N
JahrNummer
integer     4 0
0
Y  N
KontraktNummer
integer     4 0
0
Y  N
KundNummer
integer     4 0
0
Y  N
LagerNummer
integer     4 0
0
Y  N
LagerNummerZug
integer     4 0
0
Y  N
LagerPlatzNrZug
integer     4 0
0
Y  N
LagerPlatzNummer
integer     4 0
0
Y  N
Lfd_Nummer
integer     4 0 .................... N  N
LKW_Nummer
integer     4 0 .................... N  N
ME_Nummer
integer     4 0
0
Y  N
ME_NummerPreis
integer     4 0
0
Y  N
Menge
numeric    15 6
0.0
Y  N
PartieNummer
integer     4 0
0
Y  N
PeriNummer
integer     4 0
0
Y  N
Preis
numeric    15 6
0.0
[...]


---

## Rohwarensorten löschen

Rohwarensorten löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
RohWareSorte
RohSorteArtiZuAb
RohSorteQualBed
RohSorteAnKorPar
RohSorteStafFolge
RohSorteArtikel
RohSorteQualit
RohSorteKosten
RohSorKriterium
RWWaagenSorParamWert
RohWareParamWert unter der Bedingung: where RohSorteId
> 0
RWWaagenSorParameter

---

## Rollenpflegerstamm

Rollenpflegerstamm
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rollenpflegerstamm
oder
Hauptmenü
Stammdatenpflege
Stammdatenpfleger
Zugriffsrechte Rollenpflegerstamm
oder Direktsprung
[ROPST]
Die Zugriffsrechte der jeweiligen Pfleger ergeben sich
aus den Zugriffsrechten jeweiliger dedizierter Kontexte, den sogenannten
„bestimmenden Kontexten“ oder auch der „Pfleger-Rollenbindung“.
Wird zur Laufzeit ein Pfleger angefordert, so
entscheidet der zugeordnete Kontext, ob eine Anforderung erlaubt ist.
Besteht keine Autorisierung durch den bestimmenden
Rollenkontext wird das Laufzeitsystem den Anwender informieren und zwecks
administrativer Unterstützung eine Warnung ins Fehlerprotokoll eingestellt.
Felder des Rollenpflegerstamm
Felder
Pflegerstamm
Pflegerstamm
Besitzer
Dieses Feld wird z.Z. nicht
      angezeigt.
Momentan sind keine anderen Besitzer
      von Pflegerstämmen als Branchen-ERP vorgesehen.
Methode
Pflegerstamm-Methode
Mögliche Ausprägungen sind
•
Neu
•
Ändern
•
Ansehen
•
Löschen
Optionbox
Die
      Optionbox des bestimmenden Kontextes
Funktion
Die
      Funktion des bestimmenden Kontextes
Rolle
Die
      Rolle des bestimmenden Kontextes
Suchmöglichkeiten Rollenpflegerstamm
Suchkriterien
Suchen
Sucht in den Feldern
•
Pflegerstamm
•
Optionbox
•
Funktion
•
Rolle
Methode
Sucht im Feld „Methode“
Funktionen:
Funktionen
Funktion Informationen
      (
F9
)
Aufruf eines
Informationsdialoges zur
      Funktion
.
Funktion ansehen/bearbeiten
      (
F11
)
Aufruf des
      Anwendfunktions-Pflegers.
Kontext … (
F10
)
Aufruf des Optionbox-Pflegers (steht
      ausschließlich der Entwicklung zur Verfügung)

---

## Sachkonten importieren

Sachkonten importieren
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Funktion
Sachkonten
importieren
Direktsprung
[SKS]
In der Auswahlliste Sachkonten, existiert die Funktion
Sachkonten importieren.
Wählt man sie aus, so erscheint folgender
Bildschirm:
Die Importdatei muss eine Exceldatei sein. Die erste
Zeile wird nicht mit importiert, da sie für gewöhnlich die Überschrift enthält.
Welche Informationen in den Spalten zu finden sind, ist nicht fest vorgegeben,
da man sich eine eigene Datenbankprozedur schreiben kann, die die Zuweisung zur
Tabelle Sachkontstamm macht. Die Kontonummer und die Kontobezeichnung sollten
jedoch existieren. Startet man den Import, so werden folgende Schritte
ausgeführt:
•
Prüfen, ob die Tabelle SachKontstamm leer ist. Ist dies nicht der Fall,
so wird eine entsprechende Meldung ausgegeben und der Import nicht
gestartet.
•
Die Datei, die unter „Name der Importdatei“ angegeben wurde, wird in eine
Zwischentabelle mit dem Namen temp_xls_import eingespielt. Diese Tabelle enthält
die Felder col_A char(255) bis col_V(255).
•
Anschließend wird die unter „Name der Importprozedur“ eingetragene
Prozedur aufgerufen. Der verwendeter Aufrufsyntax ist: „call procedurename()“.
Die Prozedur hat also keine Parameter.
•
Am Ende wird gezählt, wie viele Datensätze importiert wurden und als
Ergebnis ausgegeben.
In der folgenden Beispielprozedur wird davon
ausgegangen, dass in col_B die Kontonummer steht, und col_C enthält die
Kontobezeichnung:
create
procedure
AMIC_SACHKONTSTAMM_IMPORT()
begin
declare
de_err_notfound exception
for
sqlstate value '02000';
declare
dc_konto
integer
;
select
first
KontoNummer
into
dc_konto
from
SachKontStamm;
--
Nur was machen, wenn SachKontstamm leer!
if
sqlstate = de_err_notfound
then
--
SachKontenStamm
insert into
SACHKONTSTAMM (
ChefDruGruppe,
ChefDruNummer,
KontoNummer,
KontoNummerHaupt,
KontoNummerOber,
KontoNummerOberHaben,
KostStelVorbel,
KSTRVorbel,
LiquidGrupNummer,
SachKontAnlaKennz,
sachkontbeake
[...]


---

## Schnittstellendaten löschen

Schnittstellendaten löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
RohwareZusatzQualitaet_Waage
RohwareZusatzWare_Waage
RohwareHauptSatz_Waage
CRWLiGenListe
Crystaldaten
SortList
ArchivWbImport
AMIC_RAIKA_akpreis
AMIC_RAIKA_artikel
AMIC_RAIKA_ean
AMIC_RAIKA_kunden
AMIC_RAIKA_preisp
AMIC_Artikel
AMIC_Artikel_addon
AMIC_Artikel_lief
AMIC_Artikel_preise
AMIC_Artikel_seku
AMIC_Artikel_text
AMIC_Artikeltx
AMIC_Kunden
AMIC_Kunden_import
AMIC_KUTMP
AMIC_Datanorm_asatz
AMIC_Datanorm_esatz
AMIC_Datanorm_vsatz
AMIC_DTAUS_asatz
AMIC_DTAUS_csatz
AMIC_DTAUS_esatz
AMIC_ARTMP
AMIC_KUTMP
AMIC_PRETMP

---

## SEPA-Kennzeichen im Hausbankenstamm

SEPA-Kennzeichen im
Hausbankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Hausbanken
Direktsprung
[BNKH]
2)
Das SEPA-Verfahren unterliegt einer ständigen Weiterentwicklung. So kann es
vorkommen, dass unterschiedliche Banken auch unterschiedliche Versionen
verwenden. In Referenz-ERP ist die Übertragung für folgende Versionen implementiert
und kann im Hausbankenstamm hinterlegt werden:
Format
Gültig ab
Gültig bis
Version 2.5
01.11.2010
11.2021
Version 2.7
04.11.2013
11.2022
Hierbei handelt es sich um dasselbe
      Format wie „Version 2.7 pain.001.003.03 / 008.003.02 gültig ab November
      2013“, nur dass bei Bankverbindungen, bei denen die IBAN mit DE beginnt,
      die BIC grundsätzlich nicht mit übertragen wird, da die Identifikation der
      Bank innerhalb Deutschlands bereits mit der IBAN erfolgen
      kann.
Version 3.0
20.11.2016
11.2023
Es
      gibt folgende Änderungen zur Vorgängerversion:
•
Die
      Vorlauffristen sind jetzt für Erst-, Folge-, Letzt- und
      Einmallastschriften bei Basislastschriften einheitlich 1 Tag lang. Sobald
      bei einer Hausbank die neue Version eingetragen ist, wird beim
      automatischen Zahlungsverkehr bei Basislastschriften die Einstellung der
      Eillastschrift gezogen.
•
Es wird nicht
      mehr zwischen „Basislastschrift“ und „Basislastschrift mit Verkürzter
      Laufzeit“ („Eillastschrift“) unterschieden. Es ist nicht notwendig die
      Stammdaten zu ändern, da bei Verwendung der Version 3.0 die eingestellten
      Werte vom Programm gleich richtig interpretiert werden.
Die
      Mandatsreferenz darf jetzt theoretisch Leerzeichen enthalten, es wird aber
      von den Kreditinstituten empfohlen, keine Leerzeichen zu verwenden, da sie
      auf papierhaften Mandat nicht immer eindeutige dargestellt werden
      können
Version 3.1 bis 3.2
19.11.2017
11.2023
pain.001.001.03_GBIC_2 /
      008.001.02_GBIC_2
Version 3.3 bis 3.6
17.11.2019
11.2025
pain.001.001.03_GBIC_3 /
      008.001.02_GBIC_3
[...]


---

## SEPA-Kennzeichen im Staatstamm

SEPA-Kennzeichen im Staatstamm
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Staatstamm
Direktsprung
[STAAT]
Im Staatstamm wurde ein neues Kennzeichen eingeführt.
Dieses besagt, ob der Staat am SEPA-Verfahren
teilnimmt oder nicht. Dieses Kennzeichen wird einmal automatisch für die 32
bisher am SEPA-Verfahren teilnehmenden Länder gesetzt. Voraussetzung für dieses
automatische Update ist, dass der ISO-Code korrekt gepflegt ist.
Beim Zusammenstellen der Zahlungen bzw. der
Zahlungsvorschläge wird für alle Banken mit einem Staat bei dem „SEPA
Teilnahmestaat“ auf
Ja
steht, ein Kennzeichen in den Zahlungsvorgängen
gesetzt, dass hier das SEPA-Verfahren anzuwenden ist. Eine Änderung des
Kennzeichens bewirkt sofort eine Anpassung der Zahlungsvorschläge. Freigegebene
Zahlungen werden nicht mehr verändert.
Hinweis:
Will man das SEPA-Verfahren
vorläufig lediglich für ausländische Lieferanten bzw. genauer: Lieferanten deren
Bank im Ausland sitzt durchführen, so kann man das Kennzeichen „SEPA
Teilnahmestaat“ für Deutschland auf Nein stellen. Dies ist eventuell deswegen
hilfreich, weil es unter Umständen sehr lange dauern kann, bevor man von allen
Lieferanten die IBAN-Nummern hat.

---

## SEPA-Purpose- Code

SEPA-Purpose- Code
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
SEPA-Purpose-Code
Direktsprung
[PURPOSE]
.
Der Purpose-Code entspricht dem aus dem DTA-Verfahren
bekannten Textschlüssel, um Überweisungen und Lastschriften automatisiert
klassifizieren zu können. Zahler und Zahlungsempfänger sowie die an der
Zahlungsabwicklung beteiligten Zahlungsdienstleister können anhand eines Purpose
Code Zahlungen (z. B. Gehaltszahlungen) automatisiert identifizieren und bspw.
die Information zur automatisierten Berechnung von Kontoführungsentgelten oder
Einräumung von Dispositionskrediten nutzen. Regelmäßige Zahlungen, wie Gehälter
oder vermögenswirksame Leistungen, sollten daher immer unter Belegung von
Purpose Code ausgeführt werden.
Es dürfen nur Purpose-Codes erfasst bzw. verwendet
werden, welche laut SEPA-Regelwerk bei SEPA-Überweisungen gemäß ISO 20022
verwendet werden dürfen.
Verwendet wird vom
Programm lediglich der Purpose-Code. Die beiden zusätzlichen Textzeilen dienen
der Information.

---

## Archiv-Import-Stammdatenpfleger: Formulararchiv Importe

Archiv-Import-Stamm
datenpfleger: Formulararchiv
Importe
Der Import beschreibt nun, wo die zu importierenden
Daten erwartet werden dürfen, wie sie aussehen können, und wie aus ihnen
geeignet die Verschlagwortung für das Formulararchiv gewonnen werden kann.
Anmerkung: Diese Profile können vom Mandantenserver
abgewickelt werden. In der nachfolgenden Beschreibung als MSM
(Mandantenservermodus) betitelt.
Felder
Name
Eindeutiger Name des
      Dokumenten-Import-Profils.
Pfad
Legt
      den Pfad fast, an dem die Daten bereitgestellt werden.
Eine
      Besonderheit ist, dass System-Umgebungsvariablen wie %TEMP%, etc. pp.
      ausgewertet werden. Zu beachten ist, dass der Pfad erwartungsgemäß aus
      Sicht des importdurchführenden Referenz-ERP-Clienten zu sehen ist.
Für
      den Einsatz im Batch-Betrieb bietet das unter anderem die Möglichkeit, mit
      wechselnden Pfaden zu operieren.
Filter
Regulärer Ausdruck der auf die zu
      verarbeitenden Dateinamen reagiert. Damit besteht die Möglichkeit ein
      Profil nur auf ganz bestimmte Dateien eines Pfades arbeiten zu lassen.
      Nämlich genau denen die dem regulären Ausdruck entsprechen.
Standardmäßig werden alle Dateien
      des Pfades bearbeitet.
Beispiel: ^01.* verarbeitet nur die
      Dateien, die genau mit 01 beginnen.
Anwendungsbeispiel ist
einen
Pfad zu haben in denen mehrere Mitarbeiter ihre Dokumente ablegen. Die
      jeweiligen Profile können dann alle auf diesem Pfad operieren.
Protokoll anzeigen
Es
      wird ein Protokoll über den Import nach Beendigung
      dargestellt.
Im
      MSM wird diese Einstellung nicht beachtet, also immer als NEIN
      behandelt.
Importierte Dateien
      löschen
Dateien werden nach erfolgreichem
      Import gelöscht.
Für
      die Testphase kann es nützlich sein, diesen Schalter vorerst auf NEIN zu
      lassen.
Im
      Produktionseinsatz ist angeraten ein JA in Erwägung zu ziehen!
Mandantherkunft
0 =
      Sektion ( Sektionsname des Mandanten, z
[...]


---

## Sonderfunktionen

Sonderfunktionen
Es stehen im Artikellistenbereich noch drei weitere
Sonderfunktionen zur Verfügung, und zwar die Bereiche

---

## Sortierung aus Liste 0

Sortierung aus Liste 0
Es wird hiermit festgelegt, ob die Liste 0 die
Sortierungen vererben soll, und zwar auf Artikelbasis, also der Artikel, der an
Position 5 in der Liste 0 steht, soll auch an Position 5 in der Liste 10719
stehen.

---

## Sortierung - Nachbearbeitung

Sortierung - Nachbearbeitung
Die in einer bestimmten Reihenfolge angewählten
Artikelpositionen einer Artikelliste werden durch diese Funktion neu sortiert,
und zwar in genau der Reihenfolge, wie sie nacheinander per Mausklick auf der
Auswahlliste angewählt worden sind.

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

## Spezielle deutsche Version

Spezielle deutsche Version
Zu Testzwecken wurde eine intern fest verdrahtete
deutsche Verbalversion zur Verfügung gestellt. Hierzu kann man im Formularstamm
unter ‚
DB Fkt. Num Text
’
folgendes angeben:
Deutsch,Euro,Cent
Es wird der Betrag ohne Vorzeichen dargestellt. Wird
„Cent“ nicht angegeben, werden nur volle Beträge gedruckt.

---

## Stammdaten des Auslandszahlungsverkehrs

Stammdaten des Auslandszahlungsverkehrs
Neben den allgemeinen Stammdaten des Zahlungsverkehrs
sind für den Auslandszahlungsverkehr folgende Stammdaten zu pflegen bzw. zu
überprüfen.
Bankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Bankenstamm
Direktsprung
[BNK]
.
Im Bankenstamm müssen die Felder
Staat
und
Swift/BIC
gepflegt werden. Der Staat ist eine im Staatstamm geführte
Nummer. Die Swift/BIC (Bank Identifier Code) ist die Internationale Banknummer
entsprechend der Bankleitzahl in Deutschland mit 8 oder 11 Stellen. Diese
Kennung setzt sich wie folgt zusammen:
•
Bank code
: 4 Stellen
Alphazeichen frei gewählt (Bundesbank z.B. MARK)
•
country code
: 2 Stellen
Alphazeichen, ISO-Code des Landes (in Deutschland also DE)
•
location code:
2 Stellen
alphanumerisch zur Ortsangabe (z.B. FF für Frankfurt)
•
branch code
: Wahlweise 3
Stellen alphanumerisch zur Bezeichnung von Filialen
Die im Bankenstamm existierende Funktion "
Banken
aktualisieren
" trägt den BIC nach. Sollte der BIC für Auslandsbanken nicht
bekannt sein, erfragen Sie diese beim Zahlungsempfänger. Bei Auslandsbanken
existiert für gewöhnlich keine Bankleitzahl. Da die Bankleitzahl jedoch als
Schlüssel dient, muss hier ein erdachter Wert eingetragen werden.
Währungsstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Währungsstamm
Direktsprung
[WAE]
Die dreistellige ISO-Währungsbezeichnung muss
eingetragen sein. Von der "International Standardization Organisation" wird eine
aus drei Buchstaben bestehende Kennung für die verschiedenen internationalen
Währungen festgesetzt.
Die beiden ersten Buchstaben stehen für das
Länderkürzel (beispielsweise DE für Deutschland, NL für Niederlande, IT für
Italien, etc.) und der dritte Buchstabe für die Landeswährung (M für Mark, G für
Gulden, L für Lira, etc.), woraus sich z. B. für Deutschland DEM, für Holland
NLG und für Italien ITL zusammensetzt.
Staatstamm
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Staatstamm
Direktsprung
[STAAT]
Der zweistellige ISO-CO
[...]


---

## Stammdaten Steuergruppen

Stammdaten Steuergruppen
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuern
Funktion Steuergruppe
F6
Direktsprung
[STS].
Hierbei handelt es sich um eine Klassifizierung der
Steuerbehandlung. In der Fakturierung können dies z.B. Inlands- und
Auslandskunden sein, die bei gleichen Artikeln unterschiedlich belastet werden.
Darüber hinaus möchte man die Auslandskunden trotz gleicher steuerlicher
Behandlung in der Umsatzsteueranmeldung nach Ländern voneinander unterscheiden
können. Ein weiterer Fall ist die Behandlung des innerbetrieblichen
Warenverkehrs, der separat dokumentiert werden soll. Andere Beispiele sind
optierende Landwirte oder die Behandlung von Pauschalsteuersätzen in
Reisekostenabrechnungen in der Buchhaltung. Die Verknüpfung von Kunden /
Lieferanten an die Steuersätze bei der Fakturierung erfolgt über den Eintrag der
Steuergruppe in den Kunden / Lieferantenstamm.
Der Pfleger sieht nur die Erfassung einer Nummer und
der Bezeichnung - die zur leichteren Identifizierung dient - vor. Wichtig ist
hier, dass die Steuergruppe 0 für Sachkontenbuchungen der Fibu exklusiv
vorgesehen ist. Eine einfache Einrichtung könnte so aussehen:
Gruppe
Beschreibung
0
Sachkonten (Fibu)
1
Inland
2
EU
      innergemeinschaftliche Lieferungen
3
Drittland
Weiterhin kann zu jeder Steuergruppe eine Erlösklasse
hinterlegt werden. Wenn eine Erlösklasse ungleich 0 eingetragen wird, so wird
bei der Bestimmung der Erlös-/Aufwandskonten diese Erlösklasse herangezogen.
Ebenfalls kann im Pfleger das Feld „Intrastat“
gepflegt werden. Dieses Feld gibt an, ob Vorgänge mit dieser Steuergruppe zum
Intrastat Export freigegeben sind oder nicht.

---

## Stammdaten Steuerklassen

Stammdaten
Steuerklassen
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuern
Funktion Steuerklasse
F5
Direktsprung
[STS]
.
Die Steuerklassen sind nicht vom Anwender zu pflegen,
sondern von Branchen-ERP fest vergeben. Es gibt folgende Einteilungen, die man sich im
Pfleger für Steuerklassen ansehen kann:
Klasse
Beschreibung
Netto
0
Steuerfrei
Ja
1
Umsatzsteuer
Ja
2
Umsatzsteuer
      (Brutto)
Nein
101
Vorsteuer
Ja
102
Vorsteuer
      (Brutto)
Nein
9999
Steuerfrei
Ja
Ob ein Betrag als Brutto oder Netto erfasst wird, wird
durch die Steuerklasse angegeben. Für steuerfreie Buchungen (z.B. Sachkonto an
Sachkonto) ist die Steuerklasse 0 vorgesehen. Es ist möglich, bestimmten
Sachkonten feste Steuerklassen zuzuordnen, um Fehler im Bereich der Mehrwert-
bzw. Vorsteuer zu vermeiden. Siehe dazu Sachkontenstamm pflegen.

---

## Stammdaten Steuerschlüssel

Stammdaten
Steuerschlüssel
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuern
Funktion Steuerschlüssel
F7
Direktsprung
[STS]
.
Es ist möglich, Erlöse nach steuerlichen
Gesichtspunkten zu differenzieren (Verprobung Umsatzsteuervoranmeldung). Der
Steuerschlüssel wird entweder im Artikelstamm oder für Buchungen in der
Finanzbuchhaltung im Sachkontenstamm hinterlegt. Der Pfleger für die
Steuerschlüssel sieht lediglich die Eingabe einer Nummer und eines
beschreibenden Textes vor. Eine Einrichtung der Steuerschlüssel könnte so
aussehen:
Schlüssel
Beschreibung
0
Systemsteuersatz
      Null
1
Voller Steuersatz z.Zt. 19
      %
2
Halber Steuersatz z.Zt. 7
      %
Das Feld
Steuertyp
wird von der
Finanzbuchhaltung nicht ausgewertet. Es dient der Einordnung der Steuerschlüssel
in die Klassifikationen der OpenTRANS®-Standards. Das Feld wird nur angezeigt,
wenn Sie OpenTRANS® verwenden und den Steuerparameter
721 –
OpenTRANS®
eingeschaltet haben.

---

## Stammdaten Steuersätze

Stammdaten Steuersätze
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuern
Direktsprung
[STS]
.
Die Pflege der Steuersätze kann an zwei
unterschiedlichen Stellen erfolgen. Ruft man den Steuersatzpfleger auf, so
erreicht man einen Kreuzpfleger, der die einzelnen Bestandteile eines Satzes
gruppiert ausgibt und so versucht, eine übersichtlichere Darstellung zu bieten.
Durch Anklicken der entsprechenden Spalte kann man die dazugehörigen Daten
pflegen. Es existiert dazu noch ein Pfleger, der über die bekannte
Auswahllistenmechanik die Daten anzeigt. Dieser ist von hier aus über das Menü
zu erreichen (
Steuersätze
F8
).
Das System bestimmt den passenden Satz über eine
Kombination von 4 Elementen:
•
Steuerklasse. Umsatzsteuer oder Vorsteuer, Brutto oder Netto.
•
Steuergruppe. Inlandskunde, Auslandskunde...
•
Steuerschlüssel. Steuerfrei, Voller Steuersatz, verminderter
Steuersatz...
•
Steuerabdatum. Ab und an ändert sich der Steuersatz. Letztes Beispiel war
die Erhöhung des vollen Steuersatzes auf 19% zum 01.01.2007. Dann ist es nur
nötig, für das Änderungsdatum einen neuen Satz zu hinterlegen, damit das System
weiß, welcher Steuersatz gültig ist. Dazu gibt es im Kreuzpfleger eine Funktion
"
Speichern unter
Shift+F9
"
Zu den oben genannten Kombinationen müssen jetzt noch
weitere Daten hinterlegt werden.
Beschreibung
Steuerformel
Hier
      gibt es vier Möglichkeiten:
Normale Steuer
. Hier wird die
      Steuer nach der gebräuchlichen Formel für Vorsteuer bzw. Umsatzsteuer
      berechnet.
Steuer 100%.
Mit dieser Einstellung können
      Steuerkonten in der Finanzbuchhaltung direkt bebucht werden. Es bedeutet,
      dass der gesamte eingegebene Betrag dem Steuerkonto zugeordnet wird. Siehe
      dazu "Steuerkonten bebuchen
"
Reisekosten
: Die Angabe der Steuersätze für
      Reisekosten erfolgt "in Hundert". Das bedeutet, dass nicht die normale
      Steuerformel verwendet werden kann.
Innergemeinschaftlicher Erwerb:
Wird ein Beleg mit
      einem Steuers
[...]


---

## Stammdaten Zinswesen

Stammdaten Zinswesen

---

## Steuerkonten

Steuerkonten
Angaben zur Bestimmung von RFS-Steuerkonten werden im
Aeins-Pfleger für Steuersätze hinterlegt (Direktsprung FISTS):

---

## Steuersatzänderung

Steuersatzänderung
Es kommt hin und wieder vor, dass sich die Steuersätze
ändern und es somit notwendig wird, die Stammdaten daraufhin anzupassen. Anhand
der zum 01.07.2020 anstehenden Änderung des Steuersatzes von 19% auf 16 % werden
hier beispielhaft die einzelnen Schritte gezeigt, die für die Änderung der
Steuer notwendig sind, damit sie auf den Umsatzsteuerformularen erscheinen. Da
die Vordruckkommissionssitzung entschieden hat, dass die Umsätze zu den neuen
Steuersätzen (16 % und 5 %) gesammelt in den Kennzahlen für Umsätze zu anderen
Steuersätzen eingetragen werden, werden keine neuen Auswertungspositionen
benötigt. Es wird daher auch keine neue Version von Elster geben.
Die zum 01.07.2020 anstehende Änderung des
Steuersatzes von 7% auf 5% muss analog geschehen.
Schritt 1: Auswertungspositionen bearbeiten
Die neuen Steuersätze sollen in unter dem Bereich
„Umsätze, die anderen Steuersätzen unterliegen“ (Kennziffer 35/36) bzw. beim
innergemeinschaftlichen Erwerb unter „zu anderen Steuersätzen“ (Kennziffer
95/98) erscheinen. Hier ist zu prüfen ob für diese Bereiche
Auswertungspositionen eingerichtet sind.
Dazu gibt man den Direktsprung
[FIAWP]
ein und gelangt so in die Anwendung
zur Pflege der Auswertungspositionen. Dort sucht man nach der Kennziffern 35 in
der Spalte Bemessungsgrundlage.
Wichtig ist hier, dass zu der
Kennziffer 35 bei Bemessungsgrundlage die 36 bei Steuer eingetragen ist.
Und anschließende sucht man nach der Kennzahl 95.
Hier muss in der Kennziffer für Steuer die 98
zugeordnet sein. Sind beide Auswertungsposition vorhanden kann man mit Schritt 2
weiter machen, ansonsten muss man sie mit
Neu
F8
anlegen. Für die
Umsatzstzsteuervoranmeldung und für Elster ist nur die korrekte Zuordnung der
Kennziffern Bessungsgrundlage bzw. Steuer wichtig.
Schritt 2: Kontostamm anpassen
Für die neuen Steuersätze werden ggf. auch neue
Sachkonten (Steuerkonto, Erlös-/Aufwandskonten und Skontokonten) benötigt. Mit
dem Direktsprung
[SKS]
gelangt m
[...]


---

## Tabelle zur Version: 8.3.2308.4

Tabelle zur Version: 8.3.2308.4
ID
Releasenote - Titel
Geprüft
34034
Kirchensteuer
34019
Artikelstammtext speichern.
34006
Auftragserfassung trotz harter Liefersperre

---

## Tabelle zur Version: 8.3.2311.10

Tabelle zur Version: 8.3.2311.10
ID
Releasenote - Titel
Geprüft
34413
Auswahlliste Vermailung
34430
Drucker-Schachtsteuerung
34499
Mailversand
34307
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34004
Zählmenge wird auch vor der Bewertung angezeigt
34447
Artikelstamm: Mengeneinheitengruppe
34509
Tastatursteuerung: Warenbewegung-Addon

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

## Tabelle zur Version: 9.0.2402.1

Tabelle zur Version: 9.0.2402.1
ID
Releasenote - Titel
Geprüft
34806
Private Nachlauf-Prozedur nach Update
35067
Tron Tracer
35166
Multiline-Textfelder
35191
Crytal Report druck
35469
Stammdatenfunktion "Alle Ändern"
35470
Crystal Report Version 13 - Performance
35571
Zugriffschutz auf Varianten
35620
Itembox 2.0 Spalten verschieben
35069
Dynaforms auf Version 4.0.87.250 aktualisiert
35219
aktuallisierung der SEPA Version
35246
e-Clearing Anzeige Adressblocj
35286
eClearing CAMT.053
34735
Irritierende Fehlermeldung entfernt
34936
Kundenstammpfleger für Nachhaltigkeit angepasst.
35291
Komponenten-Artikelauswahl in Produktionsvorgängen
      [FRZ]
34730
Belegdatum bei der Erzeugung von
      Rohware-Stornobelegen
35315
Nachhaltigkeitswerte auf Rohwarebelegen, die nicht mehr
      massebilanzwirksam sind, können nicht mehr verändert werden
35130
MDE: Fokus
35049
Neue Listenpreisgruppe bei bereits vergebener
    Nummer
35207
Vorgangsauswahllisten haben "Neu drucken und neu
      versenden" und "Beleg erneut versenden" erhalten
35213
Abweichende Steuerschlüssel im EU-Ausland
35218
Bankleitzahlen aktualisieren
35485
Preiskonditionen
35531
Bearbeiten von EK- und VK-Preisen
35328
Waage: AeinsWiege-UDP-Protokoll-Erweiterung
34897
Teildispo bei harter Liefersperre
34908
Archiveintrag für HTMLBody im Belegversand nicht mehr
      zwingend
35441
Waage mit Auftrags-Teildisposition
35452
Preiskonditionen
35496
Erlöskennziffer bei Lagernummernwechsel

---

## Tabelle zur Version: 9.0.2402.10

Tabelle zur Version: 9.0.2402.10
ID
Releasenote - Titel
Geprüft
36217
Windows-Druck: Archivierung A4-Format bei
      physikalischen Druckern
36246
Dokumentenverwaltung:
Archiv-Ansicht/Auswahlliste
36248
Archiv-Stammdatenpfleger Funktion "Belegreferenz
      erzeugen"
36274
Archiv-Vorschau bei Variantenwechsel
36122
Steuerkategorien für eRechnung
36257
Felder im eRechnungs-Export
36285
Kundenreferenz in der eRechnung
36286
GLN in der eRechnung

---

## Tabelle zur Version: 9.0.2402.4

Tabelle zur Version: 9.0.2402.4
ID
Releasenote - Titel
Geprüft
35763
Patch einspielen von SQL-Dateien
35815
Privater Crystal Report Daten anzeigen
35831
CS-Makro Funktion CompileAll
35848
Rollenpflegerstamm Aktualisierung
35849
Formularstamm - Pfleger
35876
Druckerstamm: Kennzeichen "Ohne ASCII Konvert."
35742
Neue Auswahllistenvariante im Archiv
35732
Fehlermeldungen im Barverkauf mit der Herbstversion
      9.0.2402.2
35765
Kontraktmengenzeitraum
35867
Kontraktabwahl bei Nachhaltigkeit im Verkauf
35788
Archiv-Verlinkung von eRechnungsexporten bei
      privatisierten Belegreferenzen
35814
Kundentypwechsel

---

## Tabelle zur Version: 9.0.2502.8

Tabelle zur Version: 9.0.2502.8
ID
Releasenote - Titel
Geprüft
38544
eRechnung
38545
eRechnung Artikelbeschreibung
38548
Mengeneinheiten in Objekt-/Baustellenartikeln
38495
AnyBill Mengeneinheiten

---

## Textvorbelegungen

Textvorbelegungen
Hauptmenü
Finanzbuchhaltung
Stammdaten
Textvorbelegung
Direktsprung
[FITXT]
In dieser Anwendung existieren zwei Varianten:
Belegtexte:
Man kann in der Belegerfassung und in der
Eingangsmappe auf fertige Texte zugreifen. Diese immer wiederkehrenden
Erfassungstexte können in der Anwendung Textvorbelegung abgelegt und bei der
Erfassung mittels
F3
im Textfeld abgerufen werden. Ist die Nummer
bekannt, kann man auch die Nummer direkt in das Textfeld eingeben und durch
Drücken der
F2
Taste wird dann der Text zu dieser Nummer in das Textfeld
übernommen.
Kontotexte:
Hier kann zu einem Sachkonto ein Text erfasst werden,
der dann beim Formular-Belegdruck in der Finanzbuchhaltung verwendet werden
kann. Hierfür ist dir Druckposition ID_FIBU_DRUCKTEXT vorgesehen. Wird diese
Druckposition verwendet und es ist kein Kontotext angegeben wird stattdessen der
Text aus dem Beleg verwendet.

---

## Umfang der bereitgestellten Daten

Umfang der bereitgestellten Daten
Von der mitgelieferten Ladeprozedur
HoleIndividuellePreiseKunde
werden nachfolgende Daten
bereitgestellt:
Tabellenspalte
Prozedurfeld
Feldtyp
Beschreibung
Artikel
ArtikelNummer
char(30)
Artikelnummer des
      Artikels
Artikelbezeichnung
ArtikelBezeich
char(255)
Bezeichnung des Artikels
Lager
lagernummer
integer
Lagernummer des Artikels
Warengruppe
Warengruppe
integer
Nummer der Warengruppe des
      Artikels
gültig ab
Datum
date
Gültig-Ab Datum des
      Individualpreises. Sollte das aktuelle Datum in mehr als einem Zeitraum
      enthalten sein, wird immer der Preis mit dem größten Gültig-Ab Datum
      herangezogen.
gültig bis
ArtiIndPrBisDat
date
Gültig-Bis Datum des
      Individualpreises. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein. Die Vorbelegung lässt sich in den Einrichterparametern
      pflegen.
ab
      Menge
ArtiIndAbMenge
numeric(15,4)
Ab
      welcher Menge der Preis für den Artikel gilt
pro
      Menge
PreisEinheit
numeric(15,4)
Preiseinheit: für wie viele
      Einheiten des Artikels der Preis gilt
Preis zum Datum 1 (individuelles
      Datum)
Preis1
numeric(15,4)
Preis zum im Spaltenkopf angegebenen
      Datum
Preis zum Datum 2 (individuelles
      Datum)
Preis2
numeric(15,4)
Preis zum im Spaltenkopf angegebenen
      Datum
Standard: nächster folgender
      Montag
Kann
      individuell eingerichtet werden.
Preis zum Datum 3 (individuelles
      Datum)
Preis3
numeric(15,4)
Preis zum im Spaltenkopf angegebenen
      Datum
Standard: übernächster folgender
      Montag
Kann
      individuell eingerichtet werden.
individuelles gültig bis
      Datum
IndivPrBisDatum
date
Erlaubt das Gültig-Bis Datum für
      einen kompletten Gültigkeitszeitraum in Form eines Mengenänderns zu
      überschreiben. Wird hier ein neues gültig bis Datum eingetragen, ersetzt
      es das gültig bis Datum des kompletten Preisbandes. So können Preisbänder
      verlängert werden,
[...]


---

## Umsätze

Umsätze
Die Umsatz Details-Anzeige kann:
-
Sortieren
-
Artikel gruppiert oder flach ohne jede Gruppierung anzeigen
-
Menge und Umsatz gleichzeitig anzeigen.
Außerdem wird eine Summenzeile ausgewiesen.

---

## Verteilkostenstellen

Verteilkostenstellen
Hauptmenü
Kostenrechnung
Kostenstellenstamm
Verteilkostenstellen
Direktsprung
[VKST]
Die Kosten einer Verteilkostenstelle verteilen sich
auf verschiedene andere Kostenstellen. In diesem Pfleger kann nun die
Verteil-Kostenstelle den einzelnen Kostenstellen prozentual zugeordnet werden.
Dies kann bestimmten Zeiträumen zugeordnet werden, so dass die prozentuale
Einteilung sich im Geschäftsjahresverlauf ändern kann (mit den Funktionen Neuer
Gültigkeitsbereich, Neue Periode).
Um eine Kostenstelle als Verteilkostenstelle
einzurichten, müssen folgende Eingaben gemacht werden:
Beschreibung
Verteilkostenstellen
Nummer der Verteilkostenstelle
Bezeichnung
Bezeichnung der Kostenstelle
      (sprechende und eindeutige Namen erleichtern hier die spätere Suche (Bsp.:
      KFZ-KI-QM-12345).
Matchcode
Kurzbezeichnung der
      Kostenstelle
Erfassungssperre
Diese Sperre gilt für die
      Belegerfassung der Finanzbuchhaltung. Steht diese auf „Ja“, so kann diese
      Verteilkostenstelle dort nicht mehr verwendet werden. Auch ist es nicht
      mehr möglich diese Kostenstelle erneut in einer Verteilkostenstelle oder
      in den Kostenstellengruppen zu verwenden. Ist sie bereits in irgendeiner
      Verteilkostenstelle eingetragen, so erscheint die Meldung:
Die
      hier angesprochenen Arbeitsschritte müssen manuell durchgeführt
      werden.
Wird
      in einem Beleg eine gesperrte Kostenstelle verwendet - dies ist z.B. dann
      möglich, wenn die Sperre erst nach der Verwendung der Kostenstelle gesetzt
      wurde -,  so wird der Beleg nicht gebucht. Es erscheint die Meldung
      „
Kostenstelle … ist gesperrt!
“ im Buchungsprotokoll.
Verteilung 100%
Bei
      Anwahl dieses Punktes wird überprüft, ob die hier eingegebene Verteilung
      100% ergibt. Ist das Kennzeichen „Manuell änderbar“ gesetzt, so wird auch
      bei Änderung der Werte in der Belegerfassung auf 100% geprüft.
Manuell änderbar
Bei
      Einstellung dieser Option könne
[...]


---

## Verteilkostenträger

Verteilkostenträger
Hauptmenü
Kostenrechnung
Kostenträgerstamm
Verteilkostenträger
Direktsprung
[KSTRV]
Die Kosten eines Verteilkostenträgers verteilen sich
auf verschiedene andere Kostenträger. In diesem Pfleger kann nun der
Verteil-Kostenträger den einzelnen Kostenträgern prozentual zugeordnet werden.
Dies kann bestimmten Zeiträumen zugeordnet werden, so dass die prozentuale
Einteilung sich im Geschäftsjahresverlauf ändern kann. Dies geschieht über die
Funktionen
Neuer Gültigkeitsbereich
und
Neue
Periode
.
Um einen Kostenträger als Verteilkostenträger
einzurichten, müssen folgende Eingaben gemacht werden:
Beschreibung
Verteilkostenträger
Nummer des
      Verteilkostenträgers
Bezeichnung
Ausführliche Bezeichnung des
      Kostenträgers
Matchcode
Kurzbezeichnung des
      Kostenträgers
Erfassungssperre
Diese Sperre gilt für die
      Belegerfassung der Finanzbuchhaltung. Steht diese auf Ja, so kann der
      Kostenträger dort nicht mehr verwendet werden. Auch ist es nicht mehr
      möglich diesen Kostenträger als Verteilkostenträger bzw. in den
      Kostenträgergruppen zu verwenden. Ist sie bereits in irgendeinem
      Verteilkostenträger eingetragen, so erscheint die Meldung:
Die
      hier angesprochenen Arbeitsschritte müssen manuell durchgeführt
      werden.
Wird
      in einem Beleg ein gesperrter Kostenträger verwendet - dies ist z.B. dann
      möglich, wenn die Sperre erst nach der Verwendung des Kostenträgers
      gesetzt wurde-,  so wird der Beleg nicht gebucht. Es erscheint die
      Meldung „
Kostenträger … ist gesperrt!
“ im
      Buchungsprotokoll.
Gültig ab
Nur
      bei Neuerfassung: Datum, ab dem die Kostenträgereinstellungen gelten
      sollen. Dies wird in den Gültigkeitsbereich übernommen.
Verteilung 100%
Bei
      Anwahl dieses Punktes wird überprüft, ob die hier eingegebene Verteilung
      100% ergibt. Ist das Kennzeichen „Manuell änderbar“ gesetzt, so wird auch
      bei Änderung der Werte in der Belegerfassung
[...]


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

## Vorgangsunterklassen bearbeiten SF5

Vorgangsunterklassen bearbeiten SF5
In der Auswahlliste des Formularstammes existiert eine
Funktion, die den Pfleger für die Vorgangsklassen öffnet: „Vorgangsklassen
bearbeiten“ (SHIFT+F5). Dafür muss genau ein Datensatz markiert sein, dem
mindestens eine Vorgangsklasse zugeordnet ist. Sind diesem mehrere
Vorgangsklassen zugeordnet, kann im Pfleger durch diese verschiedenen
Vorgangsklassen geblättert werden.
Um in der Auswahlliste zu erkennen, welche Klassen das
jeweilige Formular verwenden, werden in der Variante ‚Formularwesen’ zwei neue
Spalten angezeigt: Vorgangsklasse und Vorgangsunterklasse.
Die Auswahlbedingungen unter F2 (Bereich/Profile) sind
um eine weitere Eingrenzungsmöglichkeit erweitert worden. Aktiviert man das Feld
„VorgangsklasseNummer“ durch Setzen eines Häkchens, werden anschließend nur die
Formulare angezeigt, die von der ausgewählten Vorgangsklasse verwendet
werden.

---

## Vorgreservier. LOESCHEN

Vorgreservier. LOESCHEN
Die Vorgreservierung wird gelöscht. In Kombination mit
HINZUFUEGEN kann eine klassische Situation behoben werden: Der Vorgangstamm ist
schon komplett geschrieben, die Vorgreservierung hat aber in der V_ID noch eine
‚0’ und des Neu-Kennzeichen steht auf ‚1’, die Verbindung zum Vorgang hat also
nicht funktioniert. Man behebt dies durch Löschen der Vorgreservierung und
HINZUEGEN beim unvollständigen Beleg.
Die typische Situation: Aeins ist während der Erfassung
eines Beleges abgestürzt (es existiert nur die Vorgreservierung mit V_ID = ‚0’
und Neu-Kennzeichen = ‚1’ wird durch Löschen dieses Eintrages behoben. ABER
VORSICHT: Solche Einträge wird man im laufenden Betrieb natürlich häufig
finden!!!!! Also immer vergewissern, dass kein Bediener in der Erfassung
ist!

---

## Wechselkennzeichen im Hausbankenstamm

Wechselkennzeichen im Hausbankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Hausbanken
Direktsprung
[
bnkh
]
Im Hausbankenstamm müssen das Wechselkonto, das
Wechselobligokonto und das Schuldwechselkonto eingerichtet werden.
Das
Wechselkonto enthält alle erhaltenen Wechsel, das Obligokonto alle an die
Hausbank weitergereichten Wechsel bis zum Verfall, und das Schuldwechselkonto
enthält alle selbst ausgegebenen Wechsel!

---

## Wechselkennzeichen im Sachkontenstamm

Wechselkennzeichen im Sachkontenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Direktsprung
[SKS]
Im Sachkontenstamm gibt es das Feld
Wechselkonto
das auf
"JA"
gestellt werden muss. Wechselkonten
müssen
im Sachkontenstamm als Wechselkonto gekennzeichnet werden! Von
diesem Kennzeichen hängt ab, wie diese Konten in der Belegerfassung
interpretiert werden.
In der Basisdatenbank sind davon folgende Konten
betroffen:
Besitzwechsel Kontonummer 1370
Besitzwechselobligo Kontonummer 1371
Schuldwechsel Kontonummer 1660

---

## Weitere Erfassungsmöglichkeiten im Vorgang

Weitere
Erfassungsmöglichkeiten im Vorgang
Zur Erfassung und Gestaltung der Rechnung stehen
weitere Funktionen zur Verfü­gung:
Wertartikel (F11)
Alle Möglichkeiten der Artikelerfassung bestehen auch
beim Wertartikel. Im Gegensatz zur Artikelerfassung werden hier jedoch
ausschließlich wertmäßige Buchungen durchgeführt. Die Mengeneingabe dient
lediglich als Rechenhilfe. Mit WA ist es somit möglich, ein Artikelkonto
wertmäßig (Boni, Frachten, etc.) zu be- und entlasten, ohne dass
Bestandsbuchungen durchgeführt werden.
Texteingabe (F8)
Die Eingabe von Texteingabe erlaubt die Eingabe von
Texten. Es öffnet sich ein Erfassungsbildschirm mit maximal 10 Zeilen. Der Text
wird direkt erfasst.
Folgende Editiermöglichkeiten bestehen:
Mit der Taste
Einfg
kann zwischen der Funktion “Text in
einen bestehenden Text einfügen”, zu erkennen durch den schmalen Cursor, und der
Funktion “Text überschreiben” (breiter Cursor) gewechselt werden. Mit
Entf
wird Text zeichenweise von rechts
gelöscht. Mit den Cursortasten wie auch der Maus wird innerhalb des Textes
positioniert. Die
Enter
-Taste bewirkt
einen Zeilenumbruch am Ende des Textes. Sollen zusammenhängende Textbereiche
gelöscht werden, so kann dieser zuerst mit der Maus markiert und dann mit
Betätigung von
Entf
komplett gelöscht
werden.
Die Übernahme in den Positionsteil erfolgt durch
Eingabe von
ESC
und anschließender
Bestätigung oder durch Betätigung des “OK”-Feldes. Der Abbruch erfolgt analog
hierzu. Sollen mehr als 10 Textzeilen erfasst werden, so wird noch einmal die
Funktion Texteingabe aufgerufen.
In der Position “Übernahme bis” wird angegeben, ob bei
Umwandlung eines Vorgangs der Text “immer übernommen” werden soll oder ob er nur
bei einem bestimmten Vorgangstyp (Angebot, Auftrag, etc.) wirksam werden
soll.
Textbaustein
Hiermit kann auf fertig eingerichtete Textbausteine
zugegriffen werden. Die zu­lässigen werden nach Aufruf der Funktion
angezeigt, von wo sie abgerufen werden können:
In den Textbaustei
[...]


---

## Weitere Funktionen bei der Artikelerfassung

Weitere Funktionen bei der Artikelerfassung
Während der Positionserfassung stehen weitere
Bearbeitungsfunktionen zur Verfügung:
Artikeltext ändern (F6)
Der Artikeltext des bearbeiteten Artikels kann
verändert und ergänzt werden. Mit Auslösung der Funktion wird im
Texterfassungsfenster (siehe dort) der Artikeltext angezeigt. Hier kann er
geändert werden. Der geänderte Text wird in den Anzeigebereich mit Abschluss der
Erfassung des Artikels übernommen. Dieser Text bleibt über alle Vorgangsstufen
erhalten. Der Originaltext wird jedoch nicht verändert. In Warenbuchauswertungen
wird auf den veränderten Text zurückgegriffen!
aktuelle Warenbestände (SF9)
Zeigt die Bestände des aufgerufenen Artikels an. Es
sind alle Erfassungen bis auf die laufende berücksichtigt.
Abbruch (F10)
Abbruch der aktuellen Artikelpositionserfassung.
Abschluss/nächster Artikel (F9)
Falls alle Erfassungswerte korrekt vorbelegt sind,
kann die Erfassung hierdurch beschleunigt werden. Es wirkt ebenso wie die
ESC
-Taste.
Kontraktauswahl (SF7)
Aufruf der Kontrakte des Kunden und ggf. Zuordnung des
Artikels. In diesem Fall muss der Artikel im Kontrakt enthalten sein!
Preis- Informationen (F11)
Hier wird angezeigt, welche Mechanismen der
Preisfindung zur Bildung des angezeigten Preises beigetragen haben.
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
Bei der Korrektur einer Warenposition steht diese
Information dahe
[...]


---

## Weitere Funktionen des Stapelpflegers aus Artikelsicht

Weitere Funktionen des Stapelpflegers aus Artikelsicht
Funktionen
Bedeutung
Ab Menge hinzufügen (Umschalt + Strg
      + Einfügen)
Fügt
      für die aktuell selektierte Preisklasse (und damit für den aktuell
      selektierten Kunden) eine weitere Zeile ein. Die aktuelle Zeile fungiert
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
      „Ab Menge hinzufügen“ wieder hinzugefügt werden. Wird das Kommando auf
      einer Zeile mit Ab Menge = 0 aufgerufen, wird der gesamte Block aus
      [Gültig Ab, Gültig Bis] für alle Ab Mengen gelöscht.
Zeitraum einfügen (Umschalt +
      Funktionstaste F8)
Fügt
      dem aktuell selektierten Zeitraum einen neuen Zeitraum hinzu. Zu diesem
      Zweck wird das aktuelle gültig ab Datum um einen Tag fortgeschrieben und
      der Satz gespeichert. Im Stapelpfleger aus Artikelsicht können gültig ab
      und gültig bis Datum überschrieben und somit verändert werden.
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
      Preisstapelpfleger freie Dimension
[...]


---

## Weitere Stammdaten

Weitere Stammdaten

---

## Währungskurse automatisch einstellen

Währungskurse automatisch
einstellen
Sind die ISO-Bezeichnungen der von Ihnen verwendeten
Währungen im Währungsstamm korrekt eingegeben worden, wurde das Feld Kursdienst
mit
Ja
belegt und wurde die Währung nicht mit einer Kurssperre versehen,
so können Sie die aktuellen Kurse der Währungen über einen Webservice erfragen
und automatisch eintragen lassen. Dabei werden alle drei Multiplikator-Felder
auf den Wert des aktuellen Bankenwechselkurses gesetzt, der im Internet erfragt
wurde.
Zur Verfügung stehen Wechselkurse von derzeit 31
Währungen, die von der Europäischen Zentralbank (EZB) auch auf der Webseite
http://www.ecb.int/stats/exchange/eurofxref/html/index.en.html#latest
zur Verfügung gestellt werden.
Die Daten werden am Nachmittag des Handelstages ab ca.
15:00 Uhr bereitgestellt. An Samstagen und Sonntagen findet wie auch an
Feiertagen kein Handel statt. An diesen Tagen werden keine Daten veröffentlicht.
Mit den Daten aus dem Internet werden Ankauf-,
Verkauf- und Mittlerer Kurs gleichermaßen belegt.
Einstellungen
Mit dem
Steuerparameter  675
(Währungskurs mit Webdaten
überschreiben) stellen Sie ein, ob es erlaubt sein soll, dass bestehende Kurse
mit den Daten aus dem Internet überschrieben werden.
Mit dem
Steuerparameter  676
(Währungskurs x Tage zurück Web
abrufen) stellen Sie ein, wie viele Tage in die Vergangenheit die Daten
abgerufen werden sollen.
Bitte beachten Sie hierbei, dass für den Samstag und
Sonntag keine Daten ausgegeben werden, da an diesen Tagen kein Handel
stattfindet. An einem Montag ist also der jüngste Kurs 3 Tage alt.
Die historischen Daten der EZB werden sich nicht
ändern. Ausgenommen einer unwahrscheinlichen Korrektur eines falsch
ausgewiesenen Kurses werden diese Daten gleich bleiben. Wenn Sie also regelmäßig
Kurse abrufen, ist die Historie für viele Tage (max. 90) nicht sinnvoll.
Bestehende Kurse werden auch nur bei eingeschaltetem
Steuerparameter 675
überschrieben.
GGf. muss die Webseite
https://www.ecb.europa.eu/stat
[...]


---

## Währungskurse

Währungskurse
Hauptmenü
Finanzbuchhaltung
Stammdaten
Währungskurse
Direktsprung
[WAK]
Da eine Währung zu verschiedenen Terminen verschiedene
Kurse hat, müssen diese natürlich separat geführt werden. Das geschieht in der
Anwendung Währungskurse.
In den Vorgängen der Warenwirtschaft und der
Finanzbuchhaltung wird der zum Vorgangsdatum gültige Währungskurs immer extra
mitgeführt, damit sich bei einer nachträglichen Kursänderung die Roherträge etc.
nicht mit verändern.
Da sich die Multiplikatoren von der Standardwährung zur
Fremdwährung in Abhängigkeit von Ein- und Verkauf unterscheiden, können sie hier
getrennt erfasst werden.
Für gesperrte Währungen lassen sich keine
Währungskurse erfassen.
Beschreibung
Währung
Identifikation der Währung.
      Eingegeben wird die Nummer der Währung, wie sie im Währungsstamm
      hinterlegt ist. Eine Auswahl ist mit
F3
möglich.
Faktor
ab
      Datum
Erster Tag der Gültigkeit des
      Umrechnungskurses.
Kurs
      bezieht sich auf
Kurse pro einer
      Kursbezugswährung
Hier
      wird eingetragen ob der eingegebene Kurs sich auf die Kursbezugswährung
      bezieht oder auf die Währung, für die man die Daten erfassen will. Ist der
      Haken gesetzt, so bezieht sich der Kurs immer auf eine Einheit der
      Kursbezugswährung. Der Text darunter ändert sich dann auf
1 € kostet im Ankauf.....
      $
Im
      Neu-Fall wird dieses Feld mit der letzten Einstellung vorbelegt. Für alle
      Währungen, bei denen in der Kurssperre ein
Ja
eingetragen ist, wird
      dieses Feld immer aktiviert und ist nicht änderbar.
Multiplikator Ankauf
Multiplikator von der Fremdwährung
      in Standardwährung bei Ankauf: Fremdwährung * Multiplikator =
      Standardwährung.
Multiplikator Verkauf
Multiplikator von der Fremdwährung
      in Standardwährung bei Verkauf: Fremdwährung * Multiplikator =
      Standardwährung.
Multiplikator Mittel
Multiplikator von der Fremdwährung
      in Standardwährung (Mittelwert, z. B. für Umbuc
[...]


---

## Währungsstamm

Währungsstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Währungsstamm
Direktsprung
[WAE]
In diesem Eingabebildschirm können die nachfolgenden
Felder bearbeitet werden:
Beschreibung
Nummer
Dies
      ist die Identifikation für die Währung in anderen Tabellen, der als
      Verweis auf die Währungstabelle zeigt.
Bezeichnung
Ausführliche Bezeichnung der
      Währung, z. B.
"Norwegische
      Kronen"
,
"Euro"
.
Kurztext
Hier
      kann ein von der ISO-Währungsbezeichnung abweichender Text eingetragen
      werden wie z.B. € statt EUR oder $ statt USD.
ISO-Währungscode
      (4217)
Hier
      muss die ISO-Währungsbezeichnung in standardisierter Form der ISO 4217
      hinterlegt werden. Die ersten zwei Stellen stehen dabei nach ISO 3166 für
      das Land, die letzte Stelle für den Anfangsbuchstaben der Währung. So
      steht zum Beispiel:
USD für das ISO-Land United States = Kennzeichen
      US
und die Währung Dollar =Kennzeichen D
INFO: Die
      ISO-Währungsbezeichnung ist immer 3-stellig.
Hedgeteiler
Für
      die Arbeit mit Hedge ist für einige Währungen ein Teiler vorgesehen.
      Dieser ist bei Hedge-Währungen in der Regel 1000. Bei  Isländischen
      Kronen (ISK) oder Indonesischen Rupien (IDR) wird der Teiler 100000
      verwendet.
Ist
      der Hedgeteiler = 0, so werden für Kontrakte mit dieser Währung keine
      Hedge-Ordern geschrieben.
Hedgelocation
Die
      Hedgelocation bestimmt den Ort, an dem die Order dieser Gegenfinanzierung
      für ein Geschäft mit dieser Währung platziert wird.
Kurs
faktor
Angabe der Wechselkurse je x
      Einheiten der Währung. Beispielsweise wurden Lire-Kurse üblicherweise in
      DM/1000 Lit, Dollar in DM/1$ und die meisten Währungen in DM/100 Einheiten
      angegeben.
Sperre
Kennzeichen, dass eine Währung nicht
      mehr benutzt werden darf
(z. B. Im Falle einer Währungsreform
      hinfällig geworden, oder wenn der Euro alleinige Währung ist, kann hier
      die Währung
DEM
gesperrt werden
[...]


---

## Währungsstammdaten

Währungsstammdaten
Referenz-ERP
erlaubt die Abwicklung der Geschäftsvorfälle in unterschiedlichen Währungen.
Alle vom Anwender oder vom System benutzten Währungen müssen in den
Währungsstammdaten hinterlegt sein, um die gleichzeitige Verwendung mehrerer
Währungen zu ermöglichen. Eine Währung ist als Steuerparameter in der
Parametergruppe "
Optionen Global“
als
„Aktuelle Buchwährung“
hinterlegt. Dieser Eintrag kann nur geändert werden solange keine Einträge im
Vorgangstamm existieren.
Andere Währungen können beispielsweise in Vorgängen
und in Belegen der Finanzbuchhaltung vermerkt sein, intern wird aber zum Zweck
der Vermeidung von Rundungsdifferenzen stets die Standardwährung – also die
aktuelle Buchwährung - mitgeführt! Die Konten in der Finanzbuchhaltung werden
stets in Standardwährung geführt.

---

## ZollPositionen in Zollausfuhr

ZollPositionen in Zollausfuhr
Hierbei handelt es sich um das Fenster zur Bearbeitung
der, in der Ausfuhr enthaltenen, Positionen, die keine Leergutartikel sind
(Artikelstamm.Artistamtyp ungleich 5).
Im unteren Teil der Ansicht befindet sich eine Tabelle
zur Anzeige und Bearbeitung aller zur Position gehörigen Packstücke. Die
Packstück-Zeilen werden beim Anlegen des Ausfuhrvorgangs durch die im Modul
„Formularzuordnung/Vorgangsunterklasse“ [FRZ] der Unterklasse des Quellbelegs
zugeordnete Datenbankprozedur im Feld „DB-Prozedur für Packstücke“ vorbelegt.
Ist dort keine Prozedur hinterlegt, so wird die Vorbelegung durch die
exemplarische Datenbankprozedur „Zoll_Packstuecke“ vorgenommen.
Die einzelnen Zeilen können hier auch manuell
überschrieben werden.
Parameter
Bedeutung
Artikel
Artikelnummer und Artikelbezeichnung
      der Position.
Lager
Lagernummer und Lagerbezeichnung der
      Position.
Warennummer
Zollwarennummer, vorbelegt aus dem
      Artikelstamm.
Ursprungsbundesland
Das
      Ursprungsbundesland gibt an, aus welchem Bundesland stammt oder ob der
      Artikel seinen Ursprung im Ausland hat.
Verfahren
Der
      Verfahrenscode gibt an unter welchen Voraussetzungen der ausgewählte
      Artikel versendet wird. Der Verfahrenscode wird mit ‚10‘  (Endgültige
      Ausfuhr) vorbelegt.
Vorgang. Verfahren
Der
      Code für das vorangehende Verfahren ist hier zu erfassen. Das vorangehende
      Verfahren wird mit ‚00‘ (ohne vorrangehendes Verfahren) vorbelegt.
Nat.
      Zusatzverfahren
Optionales nationales
      Zusatzverfahren
Eigenmasse
Hierbei handelt es sich um das
      Eigengewicht der Position in kg. Der Wert wird aus dem Positionsgewicht
      der zugehörigen Warenposition mittels der Angaben „Gewicht pro
      Grundmengeneinheit“ im zugehörigen Artikelstamm vorbelegt.
Statistische Menge
Nur
      bei dafür laut Zollwarennummer vorgesehenen Artikeln: Anzugebende
      statistische Menge in der geforderten Mengeneinheit.
Rohmasse
[...]


---

## Zuordnung Artikel zu Rohwarengruppen

Zuordnung Artikel zu
Rohwarengruppen
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel
Direktsprung
[RWPA]
Innerhalb des Artikels
[AR]
wird unter
> weitere Kennzeichen <
die Zuordnung des Artikels
zu den eingerichteten Rohwarengruppen
[RWG]
vorgenommen.

---

## Zusatzinfo

Zusatzinfo
Das Feld Zusatzinfo kann mit einer ITEM-BOX belegt
werden (EPA), der Inhalt des Feldes wird in der Warenbewegung im Zusatzfeld1
gespeichert.

---

## Zusatzvorbelegung Warenposition

Zusatzvorbelegung Warenposition
Eine Vorbelegung der in der Schnellerfassung angezeigt
Zusatzfeld kann hier vorgenommen werden.

---

