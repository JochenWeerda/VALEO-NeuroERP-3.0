# System, Administration & Konfiguration — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (637 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Nummernkreise/Zählkreise

Nummernkreise/Zählkreise
Beim Ziehen von Nummern aus einem Zählkreis [NKZ]
wurde bisher die als Obergrenze eingetragene Nummer nicht gezogen. Dies wurde
korrigiert. Die Obergrenze stellt jetzt die maximalste Nummer dar, die aus dem
Zählkreis gezogen werden kann. Ist ein Zählkreis übergelaufen wird jetzt in dem
Feld "Aktueller Zählerstand" eine Nummer angezeigt, die um 1 größer als die
Obergrenze ist. Diese Nummer wird nicht gezogen! Sie dient nur zu
Darstellungszwecken, um anzuzeigen, dass der Zählkreis übergelaufen ist.
Des Weiteren können jetzt Nummern, die sich nicht zwischen Unter- und Obergrenze
des entsprechenden Zählkreises befinden, nicht mehr in die Reserveliste
geschrieben werden.
Releasenote Kategorie:
Ticket: 713613[32752]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: NKZ
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32752, 713613

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

## Steuersätze

Steuersätze
Nach dem Ändern von Steuersätzen kann es vorkommen,
dass beim Import von Vorgängen in die Finanzbuchhaltung, nicht die neuen sondern
die alten Steuersätze gezogen werden. Um sicherzustellen, dass die aktuellsten
Steuersatz-Daten genommen werden, ist der Mandantenserver nach dem Ändern der
Steuersätze neu zu starten. Hierzu erscheint jetzt im Steuersatz-Pfleger ein
entsprechender Hinweis.
Releasenote Kategorie:
Ticket: 715611[33020]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: [STS]
Variante: -
Funktion/Report: Steuersätze F8
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33020, 715611

---

## Druck EPC-QR-Code

Druck EPC-QR-Code
Der EPC-QR-Code wurde nicht gedruckt wenn die
TSE-Lizenz fehlte. Dieses wurde nun behoben. Der EPC-QR-Code wird jetzt
auch ohne TSE-Lizenz gedruckt.
Releasenote Kategorie:
Ticket: 717262[33367]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2302.17, 33367, 717262

---

## Formulare Einrichtungsparameter Druck

Formulare Einrichtungsparameter Druck
In der Einrichtung der Formulare [FRM] wurden folgende
Parameter überarbeitet bzw. neu eingeführt:  Randtreue Anzeige Druckbereich
Druck-Größe (in Prozent)   Drucker, die einen gewissen Randbereich auf
Papier nicht bedrucken können, werden besser unterstützt, so das es
seltener vorkommt, dass Text abgeschnitten wird beim Druck. Im Archiv ist
der Text niemals abgeschnitten.  Drucker, die wie PDF drucken, erzeugen
Dokumente mit schmalen Rand rechts, damit ein optisch besserer Eindruck
entsteht.
Releasenote Kategorie:
Ticket: 715707[33408]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Formulare
Variante: Formularwesen
Funktion/Report: Windows-Druck
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33408, 715707

---

## Einrichtungshilfe: Benutzerformate

Einrichtungshilfe: Benutzerformate
Die Einrichtungshilfe wurde um Benutzerformate
erweitert.
Releasenote Kategorie:
Ticket: 718949[33413]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33413, 718949

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

## Fibu Belegerfassung USt-IdNr

Fibu Belegerfassung USt-IdNr
Der Steuerparameter 703
"Umsatzsteuer-Identifikationsnummern auf Mandanten und Belegebene" sorgt dafür,
dass die USTId Kunde und Mandant im Beleg erfasst werden kann. Hier wurde die
Feldreihenfolge korrigiert. Steht der SPA auf "mit Vorbelegung", so öffnet sich
sofort die F3-Auswahl, wenn man die Felder betritt. Hier wurde das Verhalten so
geändert, dass im Feld mit dem Label "UStIdNrKunde" die F3-Auswahl nur dann
geöffnet, wenn Daten für den Kunden existieren und im Feld "Ust-IdNr Mnd" nur
dann geöffnet wird, wenn auch zum Kunden eine Nummer eingetragen
wurde.
Releasenote Kategorie:
Ticket: 720286[33476]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33476, 720286

---

## OLE Steuerparameter

OLE Steuerparameter
Die OLE-Steuerparameter 373, 377 und 671 sind
deaktiviert worden, weil OLE in der 64-Bit-Version nicht mehr unterstützt wird
und inzwischen andere Techniken genutzt werden. Unter Anderem wird ein
Excel-Export seit 2009 mit .Net-Technologie angesteuert. Die SPA-Einstellungen
werden entsprechend abgeändert.
Releasenote Kategorie:
Ticket: 720756[33581]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Steuerparameter
Variante: Steuerparameter
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33581, 720756

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

## Replikation: Create von einzelnen Views

Replikation: Create von einzelnen Views
Bei aktiven Subscriptionen und gesetztem SPA 851
"Passthrough aktivieren" kam es beim "Create" von Admin-Views dazu, dass diese
auch mit Status "privat" zusätzlich angelegt wurden. Das gleichzeitige
Vorhandensein als Admin- und Privat-Ausprägung ist ein unerwünschtes Verhalten,
und wird im weiteren Verlauf von Referenz-ERP auch bemängelt. Das auslösende Feature
wurde ausgebaut und damit die Ursache beseitigt.
Releasenote Kategorie:
Ticket: 721124[33663]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: SQL-Texte
Variante: -
Funktion/Report: Create
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33663, 721124

---

## Erstellen einer neuen TSE-Einrichtung

Erstellen einer neuen TSE-Einrichtung
Es war nicht mehr möglich eine neue TSE in das System
zu integrieren. Das Problem wurde behoben.
Releasenote Kategorie:
Ticket: 723397[33824]
Version: 8.3.2305.26
Datum: 26.05.2023
Anwendung: TSE-Einstellungen
Variante: -
Funktion/Report: F8
Weitere
Informationen
Tags:
Releasenote, 8.3.2305.26, 33824, 723397

---

## Anpassung für Formulartyp 201

Anpassung für Formulartyp 201
Bei der Einrichtung des Formulartyps 201
("BankScheckSparkasse"), ist der Formularbereich 508 ("Zwischenabschluss
Scheck") nun optional.
Releasenote Kategorie:
Ticket: 723599[33923]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Formulareinrichtung [FRM]
Variante: -
Funktion/Report: Listendruck
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33923, 723599

---

## Branchen-ERP-Etikettendruck Profile

Branchen-ERP-Etikettendruck Profile
Wurden im Amic-Etikettendruck Reporte mit Profil im
Bearbeiten-Modus aufgerufen, gingen die Druckereinrichtungen verloren. Dies
wurde behoben.
Releasenote Kategorie:
Ticket: 0[33960]
Version: 8.3.2307.7
Datum: 07.07.2023
Anwendung: LiLa [ETIDR]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2307.7, 33960, 0

---

## Bezahlterminal: Neuer Parameter Authentifizierung

Bezahlterminal: Neuer Parameter Authentifizierung
Das Makro "AMIC_BZT_Muster.PAS" wurde um den Parameter
"AUTHENTIFIZIERUNG" erweitert. Damit wurde der Parameter "TERMINALNAME" ersetzt.
Eingabemöglichkeiten für den Parameter "AUTHENTIFIZIERUNG" sind: TRUE / FALSE
Standard: TRUE.Darüber wird gesteuert, ob das Bezahlterminal beim Start eine
Authentifizierung benötigt oder nicht. Bestehende Privatisierungen müssen nicht
angepasst werden.
Releasenote Kategorie:
Ticket: 710833[34054]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34054, 710833

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

## Archiv-Import über Mandantenserver

Archiv-Import über Mandantenserver
Für den Import von Dateien über [FAI] gibt es mehrere
Parameter, die nun über die Anwendung pflegbar sind.  Die
Parametrisierungen von "fa_import_minutes" (Standard-Zeit: 3 Minuten) und
"fa_import_max" (Standard-Anzahl: 1) in der amicconf.ini sind nicht länger
aktiv. Sie können ab nun in der Anwendung "Formulararchiv Importe verwalten" in
der Variante "Importe" im jeweiligen Profil gepflegt werden.Somit ist es möglich
verschiedene Profile im Mandantenserver mit eigenen Parametrisierungen
hinsichtlich Zeit und Anzahl festzulegen.Die weitere Parametrierung "MandserFa"
(Standard-Zeit: 2 Sekunden) ist ab nun pflegbar im "Formulararchiv-Manager"
[FAM] unterhalb der Registerkarte "Sonstiges" im Feld "Mandantenserver
Intervall" und gibt den Intervall des Archiv-Importes-Auftrags an.
Releasenote Kategorie:
Ticket: 726335[34186]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: [FAI] [FAM]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34186, 726335

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

## Nummernkreise mit Gültigkeit

Nummernkreise mit Gültigkeit
In der Anwendung Nummernkreise [NKS] wurde eine zweite
Variante "Nummernkreise mit Gültigkeit" implementiert.
Releasenote Kategorie:
Ticket: 727631[34535]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Nummernkreise [NKS]
Variante: Nummernkreise mit Gültigkeit
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34535, 727631

---

## Auswahlliste: Ansichten

Auswahlliste: Ansichten
In der Auswahlliste konnte es dazu kommen, dass unter
der Schaltfläche "Profile" Ansichten ausgewählt werden konnten, obwohl diese
nicht für andere Benutzer freigegeben wurde. Bisher wurde davon ausgegangen,
dass alle Bediener, die die Berechtigung für die Funktion "Ansichten verwalten"
haben, alle Ansichten (inklusive der nicht freigegebenen) auswählen dürfen.
Dieses Verhalten wurde geändert. Wird jetzt eine neue Ansicht erstellt, so kann
diese erstmal nur von dem Bediener bearbeitet und verwendet werden, der diese
Ansicht angelegt hat. Für andere Benutzer ist diese Ansicht gesperrt, solange
diese noch nicht freigegeben wurde. Bereits existierende Ansichten verhalten
sich genau so wie vor dem Update. Um dies zu ändern muss die Ansicht einmal
freigeben werden. Anschließend kann die Freigabe wieder entfernt werden.
Releasenote Kategorie:
Ticket: 731003[34739]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: -
Variante: -
Funktion/Report: Ansichten verwalten
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34739, 731003

---

## Private Nachlauf-Prozedur nach Update

Private Nachlauf-Prozedur nach Update
Es kann eine parameterlose private Prozedur im
Mandantstamm [MND] in Registerkarte "Allgemein" im Feld "Nachlaufprozedur"
hinterlegt werden. Diese Prozedur wird im Zuge des Referenz-ERP-Programm-Updates am
Ende aufgerufen.
Releasenote Kategorie:
Ticket: 731447[34806]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: -
Variante: -
Funktion/Report: Update/Nachlaufprozedur
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 34806, 731447

---

## Datenbankfunktion AMIC_FSTR

Datenbankfunktion AMIC_FSTR
Der erste Parameter der Funktion AMIC_FSTR wurde
von Numeric(15,4) auf Numeric(20,4) und der Rückgabewert wurde auf Varchar(30)
geändert .
Releasenote Kategorie:
Ticket: 731210[34809]
Version: 9.0.2402.3
Datum: 08.11.2024
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.3, 34809, 731210

---

## Veraltete DTA-Formate IN SPA [521] deaktiviert

Veraltete DTA-Formate IN SPA [521] deaktiviert
Steuerparameter "DTA Ausgabeformat" [521] angepasst,
veraltete Einstellungen (Österreich, Deutschland & Dänemark) wurden
entfernt.
Releasenote Kategorie:
Ticket: 732070[34919]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Steuerparameter [SPA]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 34919, 732070

---

## Es können mehr AIS-Einrichtungen gleichzeitig genutzt werden.

Es können mehr AIS-Einrichtungen gleichzeitig genutzt werden.
Man kann unter [FRZ] auf der Vorgangsunterklassenmaske
auf dem Tabreiter AIS AIS-Einrichtungen eintragen.Ab einer gewissen Anzahl/Länge
konnten diese nicht mehr geladen werden.Dies ist aufgefallen, wenn man beim
Unterklassenwechsel eine Unterklasse auswählt für diese viele AIS-Einrichtungen
existieren.Dies wurde behoben.
Releasenote Kategorie:
Ticket: 732524[34996]
Version: 9.0.2502.9
Datum:
Anwendung: Alle Belegerfassungsanwendungen
Variante: Die erste Maske bei der Belegerfassung
Funktion/Report: Ander Unterklasse
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 34996, 732524

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

## Testmandant

Testmandant
Bei der Generierung von Testmandanten [TMD] werden nun
Kassenseriennummern und TSEs aus dem System entfernt.
Releasenote Kategorie:
Ticket: 740040[36104]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: TSE & Kassenseriennummer
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36104, 740040

---

## Crystal: Druck über Makro

Crystal: Druck über Makro
Man kann Crystal Report über Makro aufrufen und mit
Parameter versorgen. Dabei wurde der Parameter für die Anzahl der Kopien nicht
korrekt ausgewertet.
Releasenote Kategorie:
Ticket: 743010[36231]
Version: 9.0.2501.5
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36231, 743010

---

## Dokumentenverwaltung: Archiv-Ansicht/Auswahlliste

Dokumentenverwaltung: Archiv-Ansicht/Auswahlliste
Im Rahmen der einrichtbaren Archiv-Vorschau in
Auswahllisten kam es bei Aufruf von z.B. Vorgangs-Pflegern dazu das der Splitter
rückgesetzt wurde. Das Verhalten ist geändert, der Splitter bleibt nun
erwartungsgemäß bestehen.
Releasenote Kategorie:
Ticket: 740504[36246]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36246, 740504

---

## TSE-Description für BSI-Zertifizierungs-ID hinzugefügt.

TSE-Description für BSI-Zertifizierungs-ID hinzugefügt.
Die "TSE-Description" (BSI-K-TR-nnnn) wird nun auf der
TSE-Einrichtungs Makse und in der AWL Kassenverwaltung - Variante:
Stamminfo angezeigt.  Feld in der Tabelle SteupaStammTSE hinzugefügt.
Bei bestehenden TSE-Einrichtungen wird das Datenbankfeld beim eröffnen der
Kassensitzung gefüllt.
Releasenote Kategorie:
Ticket: 743581[36342]
Version: 9.0.2501.5
Datum:
Anwendung: [TSE]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36342, 743581

---

## Mandantenserver-Störungen durch Belege mit Objekten(Baustellen)

Mandantenserver-Störungen durch Belege mit Objekten(Baustellen)
Bei der Bearbeitung von Belegen
mit Objekt(Baustelle) konnte der Mandantenserver abstürzen. Dieser
Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 741654[36410]
Version: 9.0.2501.5
Datum:
Anwendung: Alle Belegerfassungsanwendungen
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36410, 741654

---

## Abkündigung: Callback Dialog

Abkündigung: Callback Dialog
Es gab einen Hintergrundprozess namens
"CALLBACKDIALOG".  Dieser wurde durch den neuen "Referenz-ERP.Worker"
abgelöst.  Bestehende Einrichtungen müssen umgestellt werden.
Releasenote Kategorie:
Ticket: 0[36624]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36624, 0

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

## Belegfluss-Workflow

Belegfluss-Workflow
Um im Belegfluss festzustellen, aus welchem Postfach
die Prozedur aufgerufen worden ist, wird eine neue Datenbankvariable namens
DBVAR_BELEGFLUSS_POSTFACH eingeführt.  Diese Variable enthält die aktuelle
Postfach-ID und ermöglicht es, festzustellen, aus welchem Postfach die
Datenbankprozedur aufgerufen wurde.
Releasenote Kategorie:
Ticket: 746666[36958]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Archiv Belegfluss
Variante: Meine Postfächer
Funktion/Report: Belegfluss
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36958, 746666

---

## Belegflussmaske Kostenaufteilungsgrid zurücksetzen

Belegflussmaske Kostenaufteilungsgrid zurücksetzen
In der Anwendung "Archiv-Belegfluss" [BF] in
der Variante "Meine Postfächer" gibt es eine Auswahllistenfunktion mit dem
Namen "Kostenaufteilungsgrid zurücksetzen". Diese Funktion bewirkt, dass der
ausführende Benutzer eigenständig breiter gemachte und verschobene Felder auf
dem Kostenaufteilungsgrid auf der Belegflussmaske auf die Einrichtung aus
der Postfach-Einrichtung zurückgesetzt wird.
Releasenote Kategorie:
Ticket: 746963[37068]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Meine Postfächer
Funktion/Report: Kostenaufteilungsgrid
zurücksetzen
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37068, 746963

---

## Belegfluss: Postfach-Einrichtung teilt Einrichtung in Kopf und Kostenverteilungsgrid.

Belegfluss: Postfach-Einrichtung teilt Einrichtung in Kopf und
Kostenverteilungsgrid.
In der Anwendung
"Archiv-Belegfluss" [BF]  in der Variante
"Postfach-Einrichtung" auf der Maske "Postfach-Einrichtung" wird bei der
Neuanlage das Kopfgrid und Kostenverteilungsgrid vorbelegt.Im Kopfgrid werden
alle Felder gepflegt, die auf der Belegflussmaske im Kopfbereich der Maske
angezeigt werden sollen und alle AIS-Einrichtungen.Im Kostenverteilungsgrid
werden alle Felder gepflegt, die auf der Belegflussmaske im unteren Grid
angezeigt werden sollen. Es gibt jetzt auch eine neue Funktion auf der Maske mit
dem Namen "Standardsortierung/Zuweisung". Durch diese werden auf existierenden
Postfacheinrichtungen die Einrichtung auf den Standard zurückgesetzt.
Releasenote Kategorie:
Ticket: 746963[37065]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Postfach-Einrichtung
Funktion/Report: F8, Standardsortierung/Zuweisung
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37065, 746963

---

## Nummernkreis optional auf der Belegflusspostfach-Einrichtungsmaske

Nummernkreis optional auf der Belegflusspostfach-Einrichtungsmaske
In der Anwendung "Archiv-Belegfluss" [BF] in
der Variante "Postfach-Einrichtung" auf der
Maske "Postfach-Einrichtung" gibt es das Feld "Nummernkreis". Ist
das Feld gefüllt wird dieser Nummernkreis zum erstellen der
Finanzbuchhaltungsbelege herangezogen. Anderenfalls wird der
Standardnummernkreis der Finanzbuchhaltung genutzt.
Releasenote Kategorie:
Ticket: 746963[37091]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Postfach-Einrichtung
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37091, 746963

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

## Branchen-ERP-Etikettendruck über JPP aufrufen

Branchen-ERP-Etikettendruck über JPP aufrufen
Um den Branchen-ERP-Etikettendruck programmgesteuert
aufzurufen, existiert ein JPP-Objekt mit dem Namen
JEtikettendruck
.
Methode
Parameter
Bedeutung
Version
Liefert die aktuelle Version.
      Aufruf:
call
      JPP_NEW("AED","JEtikettenDruck")
call JPP_DO ("AED", "VERSION",
      "LDB_TRANSFER$VC")
call JPP_DEL("AED")
Dabei ist LDB_TRANSFER$VC das Feld
      auf der Maske, in der die Versionsnummer geschrieben werden
      soll.
Editieren
LILAID
Ruft
      den interaktiven Designer auf. Beispiel ( JPL-Syntax
      ):
call
      JPP_NEW("AED","JEtikettenDruck")
call JPP_IN(
      "AED", "
LILAID
", "EAN_ETIKETT" )
call JPP_EX(
      "AED", "Editieren" )
call JPP_DEL("AED")
Vorschau
LILAID
[procedurecall]
Öffnet den Report als Vorschau. Der
      optionale Parameter überschreibt den Viewnamen bzw. den Prozedurnamen, den
      man in der Definition angegeben hat.
call
      JPP_NEW("AED","JEtikettenDruck")
call JPP_IN(
      "AED", "
LILAID
", "EAN_ETIKETT" )
call JPP_IN( "AED",
      "procedurecall", "p_kontoblatt(10000,10000,2017,12)" )
call JPP_EX(
      "AED", "Vorschau" )
call JPP_DEL("AED")
Drucken
LILAID
Druck den Report.
      Beispiel:
call
      JPP_NEW("AED","JEtikettenDruck")
call JPP_IN(
      "AED", "
LILAID
", "EAN_ETIKETT" )
call JPP_IN( "AED",
      "procedurecall", "p_kontoblatt(10000,10000,2017,12)" )
call
      JPP_IN( "AED", "fa_KundNummer", "10000" )
call JPP_IN( "AED",
      "fa_BelegDatum", "30.12.2017" )
call JPP_IN( "AED",
      "fa_BelegTypText", "Kontoblatt" )
call JPP_IN( "AED", "ask", "0"
      )
call JPP_EX( "AED", "Drucken" )
call JPP_DEL("AED")
[ask]
0
      oder 1, je nachdem, ob vor dem Druck der Drucker bzw. das Ausgabeformat
      abgefragt werden soll(=1) oder nicht (=0). Standard ist Abfrage(also 1
      ).
[procedurecall]
Dieser Parameter gibt an, was
      überhaupt gedruckt werden soll. Das Format muss so sein, wie bei
      Prozeduren der
Aufruf für bearbeiten
einge
[...]


---

## Belegfluss-Workflow

Belegfluss-Workflow

---

## Belegfluss-Workflow

Belegfluss-Workflow

---

## Eingangsmappe (EPA EINMAPPE)

Eingangsmappe (EPA EINMAPPE)
Bezeichnung
Standardwert
Erklärung
Vorbel. Belegdat 0=Tagesdatum,
      1-…=Tage zurück, -1=leer, -2 wie 0 bei Einstieg
-2
Hier
      lässt sich einstellen, wie - und ob das Belegdatum vorbelegt werden
      soll.
Standard
      Nummernkreisvorbelegung
-1
Für
      die Eingangsmappe muss hier der Nummernkreis hinterlegt werden, da hier
      noch kein Fibuvorgang vorliegt und somit nicht die Vergabe nicht über NKF
      gesteuert wird.
Welchen Kundentyp in F3 Box
      zulassen
Alle
Bei
      der Eingabe der Kontonummer lässt sich einstellen, welche Kundentype (
      Lieferant/ Kontokorrent usw. ) zulässig sind.
Archivreferenz/Paginiernummer
      abfragen?
Ja
Wenn
      hier ein Nein eingetragen wird, ist die Paginiernummer nicht
      änderbar.
Archivanzeige auch ohne
      Archivreferenz oder Kontonummer?
Nein
Es
      wird bei „Ja“ geprüft, ob Kontonummer oder Archivreferenz eingegeben
      wurden. Ist dies nicht der Fall, erschein statt dem Archiv ein Hinweis,
      dass hier die Daten erst eingegeben werden müssen.
Archivreferenz/Paginiernummer muss
      Daten enthalten?
Ja
Bei
      „Ja“ sind leer Felder nicht erlaubt.
Referenznummer muss Daten
      enthalten
Nein
Bei
      „Ja“ sind leer Felder nicht erlaubt.

---

## Zinsabrechnung erstellen (EPA FIZINSV)

Zinsabrechnung erstellen (EPA FIZINSV)
Bezeichnung
Standardwert
Erklärung
Auch
      gelöschte Personenkonten verarbeiten?
Nein
Wird
      für Kunden, die als gelöscht gekennzeichnet sind, eine Zinsabrechnung
      benötigt, so muss man diesen Einrichterparameter auf
Ja
stellen
Alte
      Zinsrechnungen überprüfen?
Nein
Steht diese Option auf
Ja
, so
      werden beim Zinslauf automatisch alle alten Zinsabrechnungen dieses
      Kalenderjahres, die der Auswahl entsprechen nachgerechnet. Dabei wird der
      Eröffnungssaldo der ersten Zinsabrechnung inklusive aller Nachbuchungen
      als Eröffnung herangezogen und anschließend alle Zinsabrechnungen
      nachgerechnet. Nachträgliche Buchungen, die bisher nur in der folgenden
      Zinsabrechnung berücksichtigt wurden, werden beim „Nachrechnen“ der
      korrekten Periode zugewiesen. Das Ergebnis wird in den Feldern
      ZINSABRSOLLZRECALC, ZINSABRHABENZRECALC, ZINSABRSTARTSALDORECALC,
      ZINSABRSALDORECALC festgehalten.
Es steht auf dieser Maske dann
      auch eine weitere Funktion „
Nachrechnen
SF9
“ zur Verfügung, die die
      Zinsabrechnungen nachrechnet, ohne eine neue Zinsabrechnung zu
      erstellen.
Zinssaldo vor Neuerstellung
      testen
Warnung
Stellt man hier ein
Ja
ein,
      so wird der Saldo der letzten Zinsabrechnung mit dem fälligen Saldo
      überprüft und es erschein ggf. eine Fehlermeldung.

---

## Kassiererwechsel (EPA NEWUSER)

Kassiererwechsel (EPA NEWUSER)
Bezeichnung
Standardwert
Erklärung
Einrichterparameter um das
      Passwortfeld zu verstecken.
Ja

---

## Terres Positionaufteilen

Terres Positionaufteilen
Bezeichnung
Standardwert
Erklärung
Soll
      die Lagernummer aus der Position des Beleges vorbelegt werden?
Nein
Wird
      dieser Einrichterparameter auf Ja gestellt, so wird die Lagervorbelegung
      mit dem Referenz-ERP Lager vorbelegt welche dem Terres zugeordnet worden ist.

---

## Sachkontenstamm (EPA Sachkontenstamm)

Sachkontenstamm (EPA Sachkontenstamm)
Bezeichnung
Standardwert
Erklärung
Nummernkreiszuordnung
      ignorieren
Nein
Kontonummern sollten für die
      unterschiedlichen Kontoarten (Sach-, Personen- und Oberkonten ) in
      verschiedenen Bereichen liegen. Diese kann man in Referenz-ERP selber über
      Nummernkreise festlegen. Diese werden in der „Allgemeinen
      Nummernkreiszuordnung“
[MNDNK]
festgelegt. Ist dort kein Nummernkreis hinterlegt, so kann man auch kein
      neues Konto erfassen. Will man diesen Test ausschalten, so kann man hier
Ja
eintragen.

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

## Vieraugenprinzip Zahlungsverkehr (EPA ZAHLUNGEN_VIERAUGENPRINZIP)

Vieraugenprinzip Zahlungsverkehr
(EPA ZAHLUNGEN_VIERAUGENPRINZIP)
Bezeichnung
Standardwert
Erklärung
VBS
      Script welches die Zahlungen überträgt
Hier
      kann ein VBS Skript angeben werden, welches die DTAUS Datei überträgt.
Es
      werden folgende Parameter an das Skript übergeben:
/FILE=
      (Ausgabedatei)
/Id=
      (DTA-Laufnummer)
VBA
      Script welches die Zahlungen überträgt
Hier
      kann ein VBA Skript angeben werden, welches die DTAUS Datei
      überträgt.
Es
      werden folgende Parameter an das Skript übergeben:
/FILE=
      (Ausgabedatei)
/Id=
      (DTA-Laufnummer)
/DTAProzedur=(Unter Optionen
      DTA_PROZEDUR angegebene Prozedur)
Soll
      die Datei im Explorer angezeigt werden
Nein
Hier
      kann entschieden werden, ob die Datei im Explorer angezeigt werden
      soll.
Prozedur zum Beantragen des
      Rücksetzens der Zahlungsnummer
ZahlungRueckBeantragen
Hier
      kann eine private Datenbankprozedur hinterlegt werden, die eine Mail an
      die Bediener der einzurichtenden Bedienerklasse versendet. Dieser Prozedur
      werden drei Parameter übergeben:
•
DTA-Laufnummer
      (Zahllaufid)
•
Die
      Bedienerklasse, die das Kennzeichen zurücksetzen darf. Siehe nächsten
      EPA
•
SMTP Server.
      Siehe übernächsten EPA
Bedienerklasse, die das Kennzeichen
      zurücksetzten darf
Hier
      wird die Bedienerklasse eingetragen, die das Übertragungskennzeichen
      löschen darf. In der Standardprozedur bekommen alle Bediener dieser
      Bedienerklasse die Mail zugesendet.
SMTP
      Server
Mail-Server

---

## Zinsabrechnung neu erstellen (EPA ZIRECALC)

Zinsabrechnung neu erstellen (EPA
ZIRECALC)
Bezeichnung
Standardwert
Erklärung
Ausgezifferte Zinsbelege
      stornieren
Nein
Dieser Einrichterparameter steuert,
      ob die Verarbeitung bei bereits ausgezifferten Zinsbelegen für das Konto
      abgebrochen wird oder nicht.

---

## Externes Formulararchiv

Externes Formulararchiv
Wird das Formulararchiv z.B. Neben dem Archiv auch
extern verwaltet so lässt sich die Replikation relativ einfach für alle
Beteiligten synchron halten.
Das folgende Bild veranschaulicht die hierfür nötigen
Einrichtungsschritte:
Hier ist die Datenbank, in der die Tabelle
Formulararchiv liegt und verwaltet wird, für die Zentrale eine konsolidierte,
also
übergeordnete
Datenbank.
Die Zentrale ist wie bisher die konsolidierte, also
übergeordnete Datenbank für die Filialen BST2, BST3 und BST4.
In diesem Beispiel nutzen wir die Möglichkeit, dass
Artikel in den Publikationen durchaus mehrfach vorkommen können. Hier nun wird
in der Zentrale eine weitere Publikation mit dem Artikel (Tabelle)
Formulararchiv angelegt und für den Subskribenten BSTFA gestartet. Dieser muss
natürlich zunächst als SQL Remote Benutzer mit Nachrichtensystem „File“ in der
Zentrale angelegt werden.
Die Tabelle Formulararchiv ist weiterhin in einer der
Standardpublikationen enthalten und wird subskribiert für BST2, BST3 und BST4.
Welches ja die entfernten SQL Remote Benutzer der Zentrale sind.
In der der Zentrale übergeordneten
Formulararchiv-Datenbank wird ebenfalls eine Publikation mit dem Artikel
Formulararchiv erstellt und für BST1 (Zentrale) subskribiert. Der Publisher ist
hier BSTFA, und auch hier muss ein SQL Remote Benutzer BST1 mit
Nachrichtensystem „File“ angelegt werden.
Durch die Replikation der Daten der Tabelle
Formulararchiv sind diese in allen Datenbanken synchron.
HINWEIS:
Dies ist natürlich nicht nur mit dem Formulararchiv
möglich, sondern mit jeder gewünschten Tabelle.

---

## Bereichsauswahl über JPP Vorbelegen

Bereichsauswahl über JPP Vorbelegen
Wird eine Anwendung programmgesteuert (z.B. über
Makro) aufgerufen, so kann man die Bereichsauswahl vorbelegen. Dazu dient das
JPP-Objekt „JAnwCond“. Fett geschriebene Parameter sind Pflichtangaben.
Funktion
Parameter
Init
Profil
Diese Funktion muss zu Beginn
      aufgerufen werden. Die drei Pflicht-Parameter identifizieren die
      Bereichsauswahl. Wird der Parameter
WithLastCond
mit 1 übergeben, dann wird
      das angegeben Profil als Vorbelegung geladen, ansonsten wird jedes Mal die
      Standardeinstellung als Basis verwendet.
CondId
Besitzer
WithLastProf
Sollen die letzten Werte dieses
      Profils als Basis verwendet werden? Standardeinstellung ist
0
für
Nein
CondAktiv
Hier
      kann eingestellt werden, ob standardmäßig alle aktivierbaren Häkchen aus
      sind (Wert = 0) oder gesetzt sind (Wert = 1). Wird dieser Parameter nicht
      angegeben, werden die Häkchen so gesetzt, wie es in der Anwendung
      vorgegeben ist. Dies ist die Standardeinstellung.
Die
      Zeilen in der Bereichsauswahl, die mit den Funktionen
SetVon
und
SetBis
angegeben werden, sind immer
      aktiv.
SetVon
Idx
Der
      Index, wie er in der Einrichtung der Bereichsauswahl angegeben
      wurde.
Von
Der
      Wert, der in der Bereichsauswahl verwendet werden soll.
SetBis
Idx
Der
      Index, wie er in der Einrichtung der Bereichsauswahl angegeben
      wurde.
Bis
Der
      Wert, der in der Bereichsauswahl verwendet werden soll.
Finit
Der
      Aufruf erfolgt als letztes, bevor die Anwendung aufgerufen wird. Wird das
      JPP-Object vorher abgeräumt (JPP_DEL), dann wird diese Funktion
      automatisch aufgerufen, wenn dies noch nicht geschehen ist.
Beispiel:

---

## Einstellungen

Einstellungen
Einrichterparameter „HEDGE_ORDER_PATH“ in der
Kontraktstamm-Maske soll das Verzeichnis angeben, in dem die Hedge-Order-Dateien
gespeichert werden.
Einrichterparameter „ORDERPROZEDUR“ soll angeben,
welche Prozedur den Hedge-Order-String zusammenstellt.
Einrichterparameter „IMPORTPATH“ in der Maske „Hedge
Datei Import“ soll das Verzeichnis angeben aus dem die Return-Dateien importiert
werden.
SPA „Hedging benutzen“ gibt an, ob Hedging überhaupt
in Kontrakten ausgewertet werden soll.
SPA „Formatnummer für Hedge-Order Files“ gibt die
Nummer des im Anwenderformat „AF_FA_GRUPPE“ angegebenen Gruppentyps an, der für
Hedge-Order-Dateien steht.
SPA „Formatnummer für Hedge-Order-Return File“gibt die
Nummer des im Anwenderformat „AF_FA_GRUPPE“ angegebenen Gruppentyps an, der für
Hedge-Return-Dateien steht.

---

## Kommandozeile

Kommandozeile
Man kann einen auf einer Prozedur basierenden Branchen-ERP
Etikettendruck Report auch von der Kommandozeile aus starten. Der Aufruf muss
dann wie folgt aussehen:
aeins
welcome entw pda=lila ID1=LILAID ID2=1 ProcedureCall="...(...)"
[Printerprofil=...]
Parameter
Beschreibung
PDA
Weist Referenz-ERP an, die folgende Maske
      direkt zu starten. Wird als Maske ETIDR angegeben, so wird versucht, den
      unter ID1 ausgewählte Report direkt zu drucken.
ID1
Funktionsident des zu startenden
      Reports
ID2
Besitzer des Reports. Bei privaten
      Reporten immer 1
PrinterConfig
(veraltet)
Dieser Parameter wird nicht mehr
      unterstütz. Wird er noch verwendet, so führt er zu einem Eintrag im
      Fehlerprotokoll. Der Report/ das Etikett wird trotzdem
      gedruckt.
PrinterProfil
(Optional)
Löst
      den Parameter PrinterConfig ab. Man gibt hier einfach das
Profil
an, dass man bei der
      Bearbeitung der Definitionen in Referenz-ERP erstellt hat.
ProcedureCall
Dieser Parameter gibt an, was
      überhaupt gedruckt werden soll. Das Format muss so sein, wie bei
      Prozeduren der
Aufruf für bearbeiten
eingetragen wurde.
BelegVId
(Optional)
Mit
      diesem Parameter kann die „V_ID“ eines Vorgangs übergeben werden. Der
      Report wird dann erst gedruckt, wenn die Verarbeitung des Beleges durch
      den Mandantenserver erfolgt ist.
Der
      Parameter darf
nicht
verwendet werden, wenn der Aufruf durch den
      Mandantenserver erfolgt. Denn Mandantenserver würde sich selbst
      blockieren.
Beispiel:
Aeins
welcome entw PDA=LILA ID1=FUNCTEST ID2 =1 PrinterProfil=KyoseraSchacht2
Procedurecall=“DBProc(451)“
Treten hierbei Fehler auf, so werden diese in
Fehlerprotokoll (Direktsprung [FEHLP]) geschrieben.

---

## Einrichtung eines openTRANS-Imports

Einrichtung eines openTRANS-Imports
Externe Kommunikation
openTRANS
openTRANS
Direktsprung [OT]
In der Variante Importprofile finden Sie die
Einstellungsmöglichkeiten für die Importe.
Vorgangsimport-Profil
Ident
Fortlaufende Nummer zur internen
      Identifikation
Quelle
Textfeld zur Repräsentation der
      Quelle – dieses Feld wird nur für Datenanzeigen verwendet.
Aktiv
Gibt
      an, ob dieses Profil beim Import von Dateien verwendet werden soll.
Pfad
Dateipfad, der angibt, wo die zu
      importierenden Dateien zu finden sind.
Archivpfad
Dateipfad, der angibt, wohin die
      importierten Dateien abzulegen sind. Ist diese Angabe leer, werden die
      Dateien nach der Verarbeitung gelöscht.
Lagernummer
Nummer des Lagers, das als Vorgabe
      für den Import verwendet werden soll, wenn sich nicht durch die Verwendung
      eines Makros eine andere Semantik-basierte Lagernummer ergibt.
Kunde
Kundennummer, die für die
      Interpretation der Artikelnummern und anderer Absenderspezifischen
      Bezeichner im Mapping verwendet werden soll, wenn sich nicht durch ein
      Makro eine andere Semantik-basierte Kundennummer ergibt.
Präprozessor-Makro
C#-Makro, das der Interpretation der
      zu importierenden Daten dient.
Postprozessor-Makro
C#-Makro, das nach dem erfolgreichen
      Import aufgerufen wird.
Stylesheets
Liste von Stylesheets, deren
      Anwendung für den Import der Dateien dieses Profils in Frage kommt.
So
      können z.B. Bestellungen eines externen Systems in openTRANS-Aufträge,
      Rechnungen in Rechnungen und Lieferavise in Bestellungen gewandelt
      werden.

---

## Zeitgesteuerter Importprozess

Zeitgesteuerter Importprozess
Sie können Makros zeitgesteuert über die Einrichtung
eines Events starten. So können Sie auch mit einem Importmakro verfahren.
Bedingung ist allerdings, dass der Mandantenserver durchgehend oder zumindest
während der geplanten Ausführungszeit aktiv ist.
Mehr zum zeitgesteuerten Aufruf eines Makros erfahren
Sie unter dem Stichwort „Zyklischer Aufruf“ in der Abteilung C#-Makros.

---

## Variante Setup Filialsystem

Variante Setup Filialsystem
Felder
Publikation
Artikel
Subskribent
Subskription gestartet
Funktionen
Setup
Hiermit lässt sich das eingerichtete
      Filialsystem für die vorhandene Betriebsstätte konfigurieren.
Setup
      Filialsystem
Optionen bearbeiten
Ermöglicht das Setzen von
      Datenbank-Optionen von SQL-Remote für die aktuelle
      Betriebsstätte.
Event anlegen
Es
      wird ein Event angelegt, welches den
DBREMOTE-Agenten
steuert.
DBREMOTE-Event erstellen
Mandantenstamm
Öffnet den
      Mandantenstamm
Setup Bearbeitungsrechte
      Vorgang
Bearbeitungsrechte für
      Erstinstallation
Diese Funktion wird verwendet, wenn
      auf Filialsystem umgestellt werden soll. Hier wird festgelegt, wer die
      Bearbeitungsrechte erhalten soll ( Zentrale oder erzeugende Betriebsstätte
      ).
Bereiche/Profile
Suchen
Suche nach
      Textschnipseln
Publikation
Suche nach
      Publikationsbezeichnung
Artikel
Suche nach
      Artikelbezeichnung
Subskribent
Suche nach Subskribent
Subskription gestartet
Suche nach Ja / Nein /
      Egal

---

## Webportal-Lizenz(SPA1005)

Webportal-Lizenz(SPA1005)
Autorisiert die Verwendung des Branchen-ERP-Webportals.

---

## Sybase Umstellung (SPA 1008)

Sybase Umstellung (SPA 1008)
Vorbelegungen und Berechtigungen zur Sybase
Umstellung.

---

## Private Prozedur für Artikelkopie (SPA 1017)

Private Prozedur für Artikelkopie (SPA
1017)
In der Option dieses Steuerparameters kann eine
private Prozedur für die Behandlung einer Artikelkopie hinterlegt werden. Diese
kann nach der Kopie eines Artikels ggf. privatisierte Zusatzrelationen abseits
des Artikeladdon versorgen.
Als Parameter muss die Prozedur die zwei Parameter
„artikelalt“ und „artikelneu“ vom Typ „integer“ enthalten. Ist diese Bedingung
nicht erfüllt, findet sich eine entsprechende Fehlermeldung im Fehlerprotokoll.
Die Ausführung der Artikelkopie wird dadurch nicht verhindert.
Das Gleiche gilt auch für den Fall, dass die Prozedur,
die im Steuerparameter definiert wurde nicht vorhanden ist.

---

## GfK-Exportschnittstelle einrichten (SPA 1021)

GfK-Exportschnittstelle einrichten (SPA 1021)
Über diesen Steuerungsparameter können
Exporteinstellungen definiert werden.
Einstellung
Bedeutung
Exportintervall (1 = Monatlich / 2 =
      Wöchentlich)
Definiert beim Export, ob die Belege
      mindestens in dem Vormonat / VorWoche erstellt wurden und für den
      aktuellen Exportzeitraum berücksichtig werden.
Entscheidend ist das Einstelldatum
      in die Tabelle GfK_Uebertrag (Zeitpunkt)
Export ab  Jahr
Ab
      wann Belege (V_DATUM) berücksichtig werden
Export ab  Periode
Ab
      wann Belege (PERINUMMER) berücksichtig werden
Export Belegklassen
Als
      Standardwert sind die Belegklassen 700,790,800,890 eingerichtet. Die zu
      exportierenden Belegklassen sind (Komma) getrennt aufzuführen.

---

## PDF-Signierung-Lizenz (SPA 1024)

PDF-Signierung-Lizenz (SPA 1024)
Lizenz für die PDF-Signierung von Archiv-Dokumenten
mit Signotec-Systemen.

---

## Futter App-Lizenz (SPA 1025)

Futter App-Lizenz (SPA 1025)
Lizenz für die FutterApp.

---

## LVS-Workflow-Prozeduren(SPA 1029)

LVS-Workflow-Prozeduren(SPA 1029)
In diesem Steuerparameter können zweierlei Werte
festgelegt werden:
1.
LVS-Lokalitäten
Diese Funktion ermittelt aus
einem eingegebenen Scanwert eine LVS-Lokalität. Das kann hilfreich sein,. Wenn
die Lokalitäten im Barcode lesbar geschlüsselt sind, also z.B. H1-R2-S3-E4 für
Halle 1 Regal 2 Stellplatz 3 Ebene 4 und dieser Wert in eine Lokalitätsnummer
übersetzt werden soll.
2.
LVS-Kommandos
Diese Funktion wird in der
Standard-Funktion „AMIC_LVS_GETSCANTYPE“ ausgewertet. Die hier gesetzte Funktion
wird zusätzlich zum Standard einen Scantyp ermitteln.
Diese Funktion hat die
folgende Signatur:
---<summary>Gibt einen
Typ eines gescannten Codes aus </summary>
---<returns>Typ des
Scancodes</returns>
---<param name="in_tcpip_adresse">Adresse des
Scanners</param>
---<param name="in_Aktionswert">gescannter
Wert</param>
---<param name="in_returnwert">Typ aus der
Standard-Funktion</param>
create
function
P_DEMO_GetScanType
(
in
in_tcpip_adresse
char
(
40
)
default
'1.1.1.1'
,
in
in_Aktionswert long
varchar
default
''
,
in
in_returnwert long
varchar
default
''
)
returns
varchar
(
30
)

---

## Stoffstrom-Stapelpfleger-Lizenz (SPA 1030)

Stoffstrom-Stapelpfleger-Lizenz (SPA 1030)
Lizenz für Stapelpfleger – Stoffstrom.

---

## Anlagenbuchhaltung-Lizenz (SPA 1033)

Anlagenbuchhaltung-Lizenz (SPA 1033)
Lizenz für die Anlagenbuchhaltung.

---

## Scannersystem-Lizenz (SPA 1034)

Scannersystem-Lizenz (SPA 1034)
Lizenz für das Scannersystem.

---

## Allgemeiner Steuerparameter für die Reklamation (SPA 1036)

Allgemeiner Steuerp
arameter für die Reklamation (SPA
1036)
In diesem Steuerparameter können Einstellungen für die
Reklamation vorgenommen werden.
Wert
Bedeutung
-
Nummernkreis Reklamation
Die
      Reklamationsnummer wird über einen Nummernkreis bestimmt, welcher hier
      eingetragen wird.
Vorgangsunterklasse
      Reklamierer
Unterklasse des Vorgangs welcher
      beim Reklamierer erzeugt wird.
Makro Vorgang erzeugen
      Reklamierer
Makro zum erzeugen des Vorgangs beim
      Reklamierer. (Makro muss die komplette Neuanlage übernehmen und die V_Id
      in den Reklamationstamm eintragen.)
Angebotsunterklasse
Alt
Auftragsunterklasse
Alt
Vorgangsklasse
      Reklamierer
Vorgangsklasse des Vorgangs welcher
      beim Reklamierer erzeugt wird.
Vorgangsklasse
      Verursacher
Vorgangsklasse des Vorgangs welcher
      beim Verursacher erzeugt wird.
Vorgangsunterklasse
      Verursacher
Unterklasse des Vorgangs welcher
      beim Verursacher erzeugt wird.
Makro Vorgang erzeugen
      Verursacher
Makro zum erzeugen des Vorgangs beim
      Verursacher. (Makro muss die komplette Neuanlage übernehmen und die V_Id
      in den Reklamationstamm eintragen.)
SQL-Prozedur Vorgang
      Reklamierer
Prozedur welche vor dem Erzeugen des
      Vorgangs ausgeführt wird. Bei Rückgabe ungleich „“ wird der Vorgang nicht
      erzeugt. („Reklamation_SqlMuster“ dient als Muster)
SQL-Prozedur Vorgang
      Verursacher
Prozedur welche vor dem Erzeugen des
      Vorgangs ausgeführt wird. Bei Rückgabe ungleich „“ wird der Vorgang nicht
      erzeugt. („Reklamation_SqlMuster“ dient als Muster)

---

## App Steuerung(SPA 1039)

App Steuerung(SPA 1039)
Hiermit werden verschiedene Voreinstellungen für die
App vorgenommen. Nach vorgenommenen Änderungen empfiehlt sich ein Neustart des
Mandantenservers, sonst kann es passieren, dass Änderungen nicht direkt
übernommen werden.
Folgende Einstellungen können getroffen werden
(Format: AppSteuerung):
Aktiv
Schlüssel
Option
Ja/Nein
Order-Vorgangsklasse
Vorgangsklasse für Aufträge welche
      mit der Referenz-ERP-App erstellt wurden. Wenn nichts eingetragen ist, wird 400
      genutzt.
Ja/Nein
Order-Vorgangsunterklasse
Vorgangsunterklasse für Aufträge
      welche mit der Referenz-ERP-App erstellt wurden. Wenn nichts eingetragen ist,
      wird 0 genutzt.
Ja/Nein
Lagernummer
Hier
      steht die Lagernummer des Lagers, auf welches gebucht wird, wenn ein
      Vorgang über die Referenz-ERP-App angelegt wird. (Dieses Lager wird für alle
      Vorgangsklassen genutzt. Wenn nichts eingetragen ist, wird 0
      genutzt.
Ja/Nein
Import-Funktion
Prozedur, welche den Vorgangsimport
      übernimmt. Als Vorlage und als Default-Wert dient die Prozedur
      „amic_AeinsAppOrder2VIMP“.
Ja/Nein
Importierte Vorgänge direkt
      erstellen
Hier
      muss der Wert „1“ oder „Ja“ eingetragen werden, damit Vorgänge direkt
      erzeugt werden. Ansonsten wird ein Eintrag im VIMP angelegt, welcher
      händisch importiert werden kann.

---

## Reklamationsmaßnahme (SPA 1040)

Reklamationsmaßnahme (SPA 1040)
In diesem Steuerparameter werden die Texte für die
Reklamationsmaßnahmen hinterlegt, sowie das Verhalten der eingebbaren Felder
gesteuert.
Folgende Einstellungen sind möglich. Ist dieser
Steuerparameter nicht eingereicht, so wird ein Standard Profil gezogen,
Feld
Bedeutung
Datentyp
Auf
      diesem Feld wirkt das Anwenderformat AF_REKLMASS. Mit diesem Format wird
      das Verhalten der einzelnen Felder gesteuert.
0(keine): Das dazugehörige
      eingebbare Feld wird nicht angezeigt
1(Text): Das Feld ist ein
      Textfeld
2(Datum): Das Feld ist ein
      Datumsfeld
3(Integer): Das Feld ist ein ganz
      Zahl Feld
4(Numeric): Das Feld ist ein
      numerisches Feld
5(JaNein): Das Feld ist ein
      FS-Format mit den Werten Ja und Nein
Ab
      100: Hier können eigene FS- und AF-Formate genutzt werden. Eintrag erfolgt
      analog zu Nr. 5
Feldnummer
In
      diesem Feld wird die Feldnummer angeben.
Bislang werden die Zahlen von 1 bis
      45 unterstützt.
Text
In
      diesem Feld wird der anzuzeigende Text für die jeweilige Auswahlbox
      eingetragen.
Ansicht der Nummerierten Felder:
Auslieferung

---

## GLN (SPA 1042)

GL
N (SPA 1042)
In diesem Steuerparameter können Einstellungen für das
Switchboard vorgenommen werden.
Wert
Bedeutung
GLN
Die
      GLN des Unternehmens aus der die NVEs generiert werden
Basisnummer
Die
      Basisnummer der GLN
Reserveziffer NVE
Die
      erste Ziffer der NVE ist die Reserveziffer

---

## Allgemeiner Steuerparameter für das Labor (SPA 1043)

Allgemeiner Steuerparameter für das Labor
(SPA
1043)
In diesem Steuerparameter können Einstellungen aus dem
FS Format FS_SPALABOR ausgewählt werden.
Wert
Bedeutung /
Option
-
Kein
      Wert
ProzedurProbeTeilen
In
      dieser Option wird eine Datenbankprozedur hinterlegt, welche anstelle der
      Standarddatenbankprozedur „LaborProbeTeilen „bei der Funktionalität
      „Probeteilen“ und „ProbeteilenundDruck“ im Labor aufgerufen wird. Dabei
      ist zu beachten, dass die private Datenbankprozedur die gleichen Eingangs-
      sowie Ausgangsparameter der Standarddatenbankprozedur besitzt.
ProzedurKontrollanbauAuspraegung
In
      dieser Option wird eine Datenbankprozedur hinterlegt, welche anstelle der
      Standarddatenbankprozedur „KontrollanbauAuspraegung“ bei dem Verfahren
      Kontrollanbau aufgerufen wird. Dabei ist zu beachten, dass die private
      Datenbankprozedur die gleichen Eingangs- sowie Ausgangsparameter der
      Standarddatenbankprozedur besitzt.

---

## Kassensicherungsverordnung (SPA 1056)

Kassensicherungsverordnung (SPA 1056)
Hier befindet sich ein Einrichtungsdialog der
Parameter zur
Kassensicherungsverordnung
.

---

## TSE Kassensicherungsverordnung-Lizenz(SPA 1058)

TSE Kassensicherungsverordnung-Lizenz(SPA 1058)
Lizenz zur
Kassensicherungsverordnung
.

---

## MDE Prozeduren Einzelhandel (SPA 1059)

MDE Prozeduren Einzelhandel (SPA 1059)
Hier werden/ können alternative Prozeduren hinterlegt
werden, die im MDE-Workflowprozess Einzelhandel die Funktionalität der
Standard-Prozeduren überschreiben.
Für jede Art von Abarbeitungsart kann hier eine eigene
private Prozedur hinterlegt werden.

---

## Verbotslisten Prozeduren (SPA 1063)

Verbotslisten Prozeduren (SPA 1063)
Dieser Steuerparameter beinhaltet die Prozeduren und
Einstellungen für die Verbotslistenprüfung.
Siehe auch
Einrichtung Verbotslistenprüfung

---

## Kostenobjekt-Lizenz(SPA 1064)

Kostenobjekt-Lizenz(SPA 1064
)
Lizenz für das Kostenobjekt.

---

## Aufgabenplanung-Lizenz(SPA 1065)

Aufgabenplanung-Lizenz(SPA 1065)
Lizenz für die Aufgabenplanung.
[TODO]

---

## Reklamations-Lizenz(SPA 1066)

Reklamations-Lizenz(SPA 1066)
Lizenz für das Reklamationsmodul.
[REKLAM]

---

## Portal3-Portal-Lizenz(SPA1068)

Portal3-Portal-Lizenz(SPA1068)
Lizenz für die Anzahl der Portale.

---

## Portal3-App-Lizenz (SPA1069)

Portal3-App-Lizenz (SPA1069)
Lizenz für die Anzahl der Apps.

---

## UStId-Prüfung-Lizenz (SPA1076)

UStId-Prüfung-Lizenz (SPA1076)
Lizenz für die Umsatzsteuerid-Prüfung ausländischer
UStIds mit Hilfe des Webservices des Bundeszentralamts für Steuern

---

## Hausbanknummer für EPC-QRCODE (SPA 1079)

Hausbanknummer für EPC-QRCODE (SPA 1079)
Hier kann festgelegt werden, welche Hausbank bei der
Erzeugung eines EPC-QRCODEs im Fuß von Rechnungsformularen heranzuziehen ist.
Die Hausbank wird hier durch die Angabe der Hausbanknummer aus dem
Hausbankenstamm festgelegt. Bei Angabe der Nummer 0 wird die Hausbank mit der
niedrigsten Hausbanknummer herangezogen.

---

## EC-Cash-Lizenz (SPA1081)

EC-Cash-Lizenz (SPA1081)
Lizenz für die Anzahl der EC-Terminal.

---

## EPC-QR-Code-Lizenz (SPA1080)

EPC-QR-Code-Lizenz (SPA1080)
Lizenz für die Nutzung der EPC-QR-Code-Ausgabe im Fuß
von Rechnungsformularen.

---

## Brennstoff-Lizenz (SPA1085)

Brennstoff-Lizenz (SPA1085)
Lizenz für Brennstoffe (AIS).

---

## Quickbeleg-Lizenz (SPA1088)

Quickbeleg-Lizenz (SPA1088)
Lizenz für Quickbeleg.

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

## Fremdwährung-Lizenz (SPA1092)

Fremdwährung-Lizenz (SPA1092)
Lizenz für Fremdwährung.

---

## Warenrückvergütung-Lizenz (SPA1093)

Warenrückvergütung-Lizenz (SPA1093)
Lizenz für Warenrückvergütung.

---

## Terres „elektrischer Belegtausch“-Lizenz(SPA1096)

Terres „elektrischer Belegtausch“-Lizenz(SPA1096)
Lizenz für die Terres-Schnitstelle „elektrischer
Belegtausch“.

---

## Archivcontainer-Lizenz (SPA1097)

Archivcontainer-Lizenz (SPA1097)
Lizenz für den Archivcontainer.

---

## Workflow-Lizenz (SPA1098)

Workflow-Lizenz (SPA1098)
Lizenz für „Workflow-Management“.

---

## Sanktionslisten-Lizenz (SPA1104)

Sanktionslisten-Lizenz (SPA1104)
Lizenz für das Modul „Sanktionslisten“.

---

## Makro 1.0 Pascal-Lizenz (SPA1106)

Makro 1.0 Pascal-Lizenz (SPA1106)
Lizenz für Pascal-Makros.

---

## Halbautomatisches Bestellwesen-Lizenz (SPA1108)

Halbautomatisches Bestellwesen-Lizenz (SPA1108)
Lizenz für „Halbautomatisches Bestellwesen“.

---

## Etikettendruck-Lizenz (SPA1111)

Etikettendruck-Lizenz (SPA1111)
Lizenz für das Modul „Etikettendruck“.

---

## Spezifikation-Lizenz (SPA1110)

Spezifikation-Lizenz (SPA1110)
Lizenz für das Modul „Spezifikation“.

---

## Filiale-Offline-Lizenz (SPA1105)

Filiale-Offline-Lizenz (SPA1105)
Lizenz für „Filialanbindung Offline“.

---

## E-Mail-Connector-Lizenz (SPA1124)

E-Mail-Connector-Lizenz (SPA1124)
Lizenz für den E-mail-Connector

---

## PayPal-Lizenz (SPA1119)

P
ayPal-Lizenz (SPA1119)
Lizenz für das PayPal-Modul

---

## ScannerConnection-Lizenz (SPA 1122)

ScannerConnection-Lizenz (SPA 1122)
Lizenz mit der Anzahl der Datenbankzugriffe.

---

## Aeins-App-Lizenz (SPA1128)

Aeins-App-Lizenz (SPA1128)
Lizenz für die Anzahl der User mit der Referenz-ERP-App.

---

## Deutsche Texte mitschreiben(Sprache lernen)(SPA 1126)

Deutsche
Texte mitschreiben(Sprache lernen)(SPA 1126)
Mit diesem Steuerparameter weist man Referenz-ERP an, die
Deutschen Texte in der Sprachtabelle zu speichern. Dies geschieht immer dann,
wenn dieser Steuerparameter auf Ja steht und der Anwender Referenz-ERP in einer
anderen Sprache als Deutsch startet. Das Mitschreiben der deutschen Texte ist
dann notwendig, wenn man fehlende Texte in der Anwendung „Fremdsprachen pflegen“
(Direktsprung [SPRA]) nachtragen möchte. Dies kann u.a. dann notwendig sein,
wenn man mit AIS eigene Anwendungen AIS erstellt hat.

---

## Eingangsdatum muss hinter dem Belegdatum liegen(SPA 1130)

Eingangsdatum muss hinter dem Belegdatum liegen(SPA 1130)
Für Eingangsrechnungen und -gutschriften kann ein
Eingangsdatum erfasst werden. Dieser Steuerparameter legt fest, ob bei der
Erfassung oder beim Import – und zwar sowohl in der Warenwirtschaft als auch in
der Finanzbuchhaltung - getestet wird, ob das Eingangsdatum hinter dem
Belegdatum liegt.

---

## Scanner 2.0 Connection-Lizenz (SPA 1140)

Scanner 2.0 Connection-Lizenz (SPA 1140)
Lizenz mit der Anzahl der Verbindungen für den Scanner
2.0.

---

## Dashkacheln-Lizenz (SPA1142)

Dashkacheln-Lizenz (SPA1142)
Lizenz für die Kacheln des Dashboards.

---

## Datenlöschung-Lizenz (SPA1144)

Datenlöschung-Lizenz (SPA1144)
Lizenz für die Datenlöschung.

---

## Anybill Lizenz(SPA1154)

Anybill Lizenz(SPA1154)
Lizenz, um den ANYBILL-QR-Code auf dem externen
Kassendisplay anzuzeigen und zu verwenden.

---

## Bezahlterminal mit eigenem Drucker (SPA 1156)

Bezahlterminal mit eigenem Drucker (SPA 1156)
Standard ist Ja
Wird dieser SPA auf „Nein“ gestellt, so wird dem
Bezahlterminal der Drucker abgeschaltet. Dazu muss jedoch im Kassenbon-Formular
im Fuß letzte Seite die Position 8273 – EC-Karten-Beleg Text mit mind 30 Zeilen
eingerichtet werden.

---

## Verpostungstamm im Archivmailversand (SPA 1164)

Verpostungstamm im Archivmailversand (SPA
1164)
Standard ist Nein
Wird dieser SPA auf „Ja“ gestellt, so wird im
Formulararchiv-Mailversand der Absender zur Auswahl freigeschaltet. Im Standard
wird dieses Feld mit dem Wert aus dem Einrichterparameter (EPA) vorbelegt.
Sollte dieser Wert ungültig sein, so wird der ersetzt aus dem Standard des
Verpostungsstamms.
Wird der Steuerparameter auf „Ja“ eingestellt, kann
dieser Wert furch Auswahl aus dem Versandprofilstamm überschrieben werden.

---

## Stapel in Anwendungen anzeigen (SPA 1175)

Stapel in Anwendungen anzeigen (SPA 1175)
Die Anwendungen, in denen die Stapelverarbeitung des
Vorgangs angeschlossen ist, wurden so erweitert, dass sie mit einem Icon
anzeigen, ob ein Vorgang bereits in einem Stapel ist oder nicht.
Diese Anzeige lässt sich mithilfe dieses
Steuerparameter abschalten.

---

## Branchen-ERP-interne Serienverwaltung aktiv(SPA 127)

Branchen-ERP-interne Serienverwaltung aktiv(SPA 127)
Mit diesem Steuerparameter kann die Branchen-ERP-interne
Serienverwaltung aktiviert / deaktiviert werden.

---

## Kassen-Lizenz(SPA 128)

Kassen-Lizenz(SPA 128)
Lizenz für Kasse (wird beim Einstieg gesetzt)

---

## Warenbuchauswertung angeschlossen(SPA 129)

Warenbuchauswertung angeschlossen(SPA 129)
Mit diesem Steuerparameter kann die
Warenbuchauswertung aktiviert / deaktiviert werden.

---

## Warenwirtschaft angeschlossen(SPA 134)

Warenwirtschaft angeschlossen(SPA 134)
Mit diesem Steuerparameter kann die Warenwirtschaft
aktiviert / deaktiviert werden.

---

## Außendienst angeschlossen(SPA 137)

Außendienst angeschlossen(SPA 137)
Mit diesem Steuerparameter kann die Verwaltung des
Außendienstes aktiviert / deaktiviert werden.

---

## Seriennummern-Lizenz(SPA 139)

Seriennummern-Lizenz(SPA 139)
Lizenz für Seriennummern (wird beim Einstieg
gesetzt)

---

## Mehrfilialverwaltung-Lizenz(SPA 14)

Mehrfilialverwaltung-Lizenz(SPA 14)
Lizenz für Mehrfilialverwaltung (wird beim, Einstieg
gesetzt)

---

## Unterobjekte aktiv(SPA 172)

Unterobjekte aktiv(SPA 172)
Mit diesem Steuerparameter können Unterobjekte
aktiviert / deaktiviert werden.

---

## Sofortaktualisierung bei Vorgangsbearbeitung(SPA 195)

Sofortaktualisierung bei Vorgangsbearbeitung(SPA 195)
Bei ‚Ja‘ wird schon bei der Erfassung eines Vorgangs
die Menge auf dem Objekt aktualisiert. Bei Nein geschieht dies erst bei der
Verarbeitung durch den Mandantenserver. Wir empfehlen die Einstellung ‚Ja‘.

---

## Partieverwaltung angeschlossen (SPA 2)

Partieverwaltung angeschlossen (SPA 2)
Mit diesem Steuerparameter kann die Partieverwaltung
aktiviert / deaktiviert werden.

---

## Mitgliedsverwaltung aktiv(SPA 21)

Mitgliedsverwaltung aktiv(SPA 21)
Mit diesem Steuerparameter kann die
Mitgliedsverwaltung aktiviert / deaktiviert werden.

---

## Dokumentenverwaltung-Lizenz (SPA 226)

Dokumentenverwaltung-Lizenz (SPA 226)
Lizenz für die Dokumentenverwaltung.

---

## Artikeltext-Variante des Artikels(SPA 231)

Artikeltext-Variante des Artikels(SPA 231)
Dieser Steuerparameter beeinflusst die Wahl der
Artikeltext-Variante in einem Vorgang.
Einstellungen
Nein
Es
      wird der Artikeltext der Standard-Artikeltext-Variante
      herangezogen.
Alternativ
Bei
      dieser Einstellung wird statt der Standard-Artikeltext-Variante die im
Artikel
angegebene Variante,
      gegebenenfalls ersetzt durch die abweichende Angabe einer
      Artikeltext-Variante in der
Vorgangsunterklassen
,
      sofern diese nicht 0 ist und ein Artikeltext zu der Variante hinterlegt
      ist, zur Bestimmung des zu verwendenden Artikeltextes herangezogen.
Zusätzlich
Bei
      dieser Einstellung wird sowohl der Artikeltext der
      Standard-Artikeltext-Variante als auch, sofern vorhanden, der Artikeltext
      zur im
Artikel
beziehungsweise in der
Vorgangsunterklassen
angegebenen Artikeltext-Variante, sofern vorhanden,
      herangezogen.

---

## Vorbelegung Periodenauswahl Finanzbuchhaltung(SPA 236)

Vorbelegung Periodenauswahl Finanzbuchhaltung(SPA 236)
Mit diesem Steuerparameter wird in Umwandlungen die
Vorbelegung für die Periodenauswahl der Finanzbuchhaltung eingestellt. Die
möglichen Werte sind „manuelle Eingabe“ und „lt. SPA-Einstellung belegen“,
dessen Wirkung unter
Globale
Einstellungen
beschrieben wird.

---

## Vorbelegung Periodenauswahl Warenwirtschaft(SPA 235)

Vorbelegung Periodenauswahl Warenwirtschaft(SPA 235)
Mit diesem Steuerparameter wird in Umwandlungen die
Vorbelegung für die Periodenauswahl der Warenwirtschaft eingestellt. Die
möglichen Werte sind „manuelle Eingabe“ und „lt. SPA-Einstellung belegen“,
dessen Wirkung unter
Globale
Einstellungen
beschrieben wird.

---

## Gewogener EKP aus FAKTURIERTEN Beständen(SPA 240)

Gewogener EKP aus FAKTURIERTEN Beständen(SPA 240)
Dieser Steuerungsparameter wird nicht mehr
ausgewertet.

---

## Eindeutigkeit Vorgangsnummer je Klasse(SPA 244)

Eindeutigkeit Vorgangsnummer je Klasse(SPA 244)
Dieser Steuerparameter entscheidet, in welcher Form
Nummern im Reservierungssatz des Vorgangs abgespeichert werden. Ist der
Steuerparameter auf Gesamt eingestellt, wird in das Feld JahrNummer eine 0
eingetragen und dann die nächste freie Belegnummer gesucht - gemäß
Nummernkreiszuordnung dieser Vorgangsklasse. Ist der SPA auf Jahr eingestellt,
wird in das Feld JahrNummer das aktuelle Jahr eingetragen und dann die nächste
freie Belegnummer gesucht- gemäß Nummernkreiszuordnung dieser Vorgangsklasse;
dabei kann im folgenden Jahr wieder mit der ersten Nummer gemäß Nummernkreis
begonnen werden. Daher sollte dieser Steuerparameter möglichst nicht geändert
werden, nachdem man sich für eine Vorgehensweise entschieden hat.
ACHTUNG: Innerhalb einer Vorgangsklasse wird
jeweils die nächste freie Nummer gesucht. Es ist also nicht möglich, in einer
Vorgangsklasse für Vorgänge in verschiedenen Unterklassen dieselbe Belegnummer
zu vergeben. Man sollte durch Anlegen disjunkter Zählergrenzen sauber zwischen
Belegnummern verschiedener Vorgänge unterschiedlicher Vorgangsunterklassen
innerhalb einer Vorgangsklasse trennen.

---

## Nullmengen bei Umwandlung übernehmen(SPA 268)

Nullmengen bei Umwandlung übernehmen(SPA 268)
Dieser Parameter steuert, ob bei Umwandlungen
Warenpositionszeilen mit 0 Menge übernommen werden sollen („Ja“) oder nicht
(„Nein“).

---

## User-Lizenz (SPA 293)

User-Lizenz (SPA 293)
Lizenz für die User-Anzahl.

---

## Ausweichartikel aktiv(SPA 31)

Ausweichartikel aktiv(SPA 31)
Mit diesem Steuerparameter kann die
Artikel-Ausweichliste aktiviert / deaktiviert werden.

---

## Aut. Zu-/Abschläge bei Kasse aktiv(SPA 326)

Aut. Zu-/Abschläge bei Kasse aktiv(SPA 326)
Hier wird bei der Tresen Kasse entschieden, ob für die
augenblicklich gezogene Position die automatischen Zu-/Abschläge ziehen sollen.
Auch bei der POS-Kasse werden mit diesem
Steuerparameter die automatischen Zu-/Abschläge ausgeschaltet.

---

## Fiktivmenge direkt in Warenposition(SPA 335)

Fiktivmenge direkt in Warenposition(SPA 335)
Mit diesem Steuerungsparameter kann das Eingabefeld
‚Fiktive Menge‘ auf der Warenpositionsmaske aktiviert werden. Währen dieser SPA
eine allgemeine Einstellung darstellt, kann unter FRZ / SPA diese Einstellung
auch für jede Vorgangsunterklasse individuell eingestellt werden.
Bei Aktivierung der Fiktiven Menge wird der
Warenposition mitgeteilt, dass sich diese Position auf eine größere Menge
bezieht, von der nur ein Teil hier erfasst wird. Alle Mengenbezüge bezüglich
Zu/Abschlägen oder Frachten beziehen sich dann auf die fiktive Menge und nicht
auf die tatsächlich in dieser Warenposition erfassten Menge.
Beispiel:
Ein Kunde bekommt einen mengenbezogen Abschlag ab der
Menge 1000 kg, aktuell werden aber nur 300 kg geliefert. Trägt man in der
fiktiven Menge 1000 kg ein, wird der Abschlag trotz der nicht erfüllten realen
Mengengrenze gewährt. Das System überprüft jedoch nicht, ob die fiktive Menge
irgendwann erreicht wird. Es obliegt hier also der Verantwortung des Bedieners
über die korrekte Verwendung dieser Konstruktion.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Mehrsprachigkeit aktiv(SPA 34)

Mehrsprachigkeit aktiv(SPA 34)
Mit diesem Steuerparameter kann die Mehrsprachigkeit
aktiviert / deaktiviert werden.

---

## Währungsumrechnung aktiv(SPA 35)

Währungsumrechnung aktiv(SPA 35)
Mit diesem Steuerparameter
können Fremdwährungen aktiviert / deaktiviert werden.

---

## Aktuelle Buchwährung(SPA 353)

Aktuelle Buchwährung(SPA 353)
Währungsnummer der zentralen Währung.
Dieser Steuerparameter kann nur gesetzt werden, wenn
keine Einträge im Vorgangstamm existieren.

---

## Makroverarbeitung Referenz-ERP(SPA 374)

Makroverarbeitung Referenz-ERP(SPA 374)
Lizenz für Makros in Referenz-ERP

---

## Mahnwesen aktiv(SPA 37)

Mahnwesen aktiv(SPA 37)
Mit diesem Steuerparameter kann das Mahnwesen
aktiviert / deaktiviert werden.

---

## Referenz-ERP Dateninterface Makro(SPA 371)

Referenz-ERP Dateninterface Makro(SPA 371)
Lizenz für Makrointerface Vorgang

---

## Leergutverwaltung angeschlossen(SPA 382)

Leergutverwaltung angeschlossen(SPA 382)
Mit diesem Steuerparameter kann die Leergutverwaltung
aktiviert / deaktiviert werden.

---

## Gefahrgut-99-Lizenz(SPA 398)

Gefahrgut-99-Lizenz(SPA 398)
Lizenz für Gefahrgut-99.

---

## Leergutverwaltung-Lizenz(SPA 4)

Leergutverwaltung-Lizenz(SPA 4)
Lizenz für Leergutverwaltung (wird beim, Einstieg
gesetzt)

---

## Partie-Lizenz(SPA 435)

Partie-Lizenz(SPA 435)
Lizenz für Partie.

---

## Wechselbuchhaltung-Lizenz(SPA 437)

Wechselbuchhaltung-Lizenz(SPA 437)
Lizenz für Wechselbuchhaltung.

---

## Textverarbeitung-Lizenz(SPA 438)

Textverarbeitung-Lizenz(SPA 438)
Lizenz für Textverarbeitung.

---

## Warenbuchauswertung-Lizenz(SPA 440)

Warenbuchauswertung-Lizenz(SPA 440)
Lizenz für Warenbuchauswertung.

---

## Objekt-Lizenz(SPA 444)

Objekt-Lizenz(SPA 444)
Lizenz für Objektverwaltung.

---

## Stückliste-Lizenz(SPA 443)

Stückliste-Lizenz(SPA 443)
Lizenz für Stückliste.

---

## Kostenstellen-Lizenz(SPA 447)

Kostenstellen-Lizenz(SPA 447)
Lizenz für Kostenstellen.

---

## Kontokorrent-Lizenz(SPA 448)

Kontokorrent-Lizenz(SPA 448)
Lizenz für Kontokorrent.

---

## Warenwirtschaft-Lizenz(SPA 449)

Warenwirtschaft-Lizenz(SPA 449)
Lizenz für Warenwirtschaft.

---

## Finanzbuchhaltung-Lizenz(SPA 450)

Finanzbuchhaltung-Lizenz(SPA 450)
Lizenz für Finanzbuchhaltung.

---

## Storno-Belegnummern wieder reaktivieren(SPA 490)

Storno-Belegnummern wieder reaktivieren(SPA 490)
Wird dieser Steuerparameter auf „Ja“ gestellt, so
werden die Belegnummern stornierter Belege wieder in den Nummernkreis zurück
gestellt (sind also wieder verwendbar).
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Nummer der Währung DM(SPA 494)

Nummer der Währung DM(SPA 494)
Nummer der Währung, in der DM ( deutsche Mark)
eingerichtet ist. Die Formularsteuerung zieht diesen Steuerparameter, wenn
Beträge in DM ausgewiesen werden soll ( z.B. nach  einer Umstellung auf
EURO vor dem 1.1.2002 )

---

## Mitgliederverwaltung-Lizenz (SPA 502)

Mitgliederverwaltung-Lizenz (SPA 502)
Lizenz für Mitgliederverwaltung +
Gesellschafterverwaltung.

---

## Finanzbuchhaltung angeschlossen(SPA 5)

Finanzbuchhaltung angeschlossen(SPA 5)
Mit diesem Steuerparameter kann die Finanzbuchhaltung
aktiviert / deaktiviert werden.

---

## Archiv-Lizenz (SPA 508)

Archiv-Lizenz (SPA 508)
Lizenz für das Archiv.

---

## Beim Import von BV-Belegen Storno ?(SPA 507)

Beim Import von BV-Belegen Storno ?(SPA 507)
Wird dieser Steuerparameter auf „Nein“ gesetzt, wird
beim Import von Storno BV-Belegen die sonst übliche Behandlung (Erzeugen eines
Stornobeleges im Kassenbuch mit Defaultzahlungssätzen, aktualisieren der
Kassenbestände und anschließendem Druck) abgeschaltet. (Absturzverhinderer beim
Import von RAIKA-BV-Belegen Retour)
Ist dieser Steuerparameter auf „Ja“ gesetzt, ist die
Behandlung wie bisher.

---

## DTA Ausgabeformat(SPA 521)

DTA Ausgabeformat(SPA 521)
Mit diesem Steuerparameter kann eine Sonderbehandlung
bzgl. des
DTA
-Formates aktiviert werden.
Folgende Formate stehen zur Verfügung:
•
SEPA
•
Eigene Datenbankfunktion
•
Eigene Datenbankfunktion (
SEPA
)

---

## Bei Shift-F4 Direktsprungliste aufrufen(SPA 539)

Bei Shift-F4 Direktsprungliste aufrufen(SPA 539)
Im Normalfall ruft Shift-F4 die Maske zur Eingabe
eines Direktsprunges auf. Dort kann man dann mit F3 den Direktsprung in einer
Itembox auswählen. Ist dieser Steuerparameter auf „JA“ gesetzt, wird nur noch
diese Itembox aufgerufen, also ohne Umweg über die Maske.

---

## Belege mit Betrag 0 im Kontenblatt-Druck(SPA 540)

Belege mit Betrag 0 im Kontenblatt-Druck(SPA 540)
Mit diesem Steuerparameter
kann festgelegt werden, ob Belege im KOKORE mit dem Betrag 0 angezeigt werden
sollen. Der Steuerparameter wirkt nur bei neuen KOKOREs, bei bereits erstellten
hat es keinen Einfluss mehr.
Folgende Werte stehen hier
zur Verfügung.
Wert
Bedeutung
0 =
      Nein
Belege mit dem Betrag 0 werden nicht
      im KOKORE angezeigt.
1 =
      Ja
Es
      werden auch Belege mit dem Betrag 0 angezeigt.
2 =
      Ja (Keine Lieferungen zu Vorverkauf/-einkauf)
Es
      werden auch Belege mit dem Betrag 0 angezeigt. Desweiteren werden aber
      keine Lieferungen zu Vorverkaufs/-einkaufsbelegen angezeigt.

---

## Auslands-Zahlungsverkehr-Lizenz(SPA 546)

Auslands-Zahlungsverkehr-Lizenz(SPA 546)
Lizenz für Auslands-Zahlungsverkehr.

---

## Telefonie TAPI/CTI-Lizenz(SPA 548)

Telefonie TAPI/CTI-Lizenz(SPA 548)
Lizenz für Telefonie (TAPI/CTI).

---

## Periode/Jahr bei Sammelumwandlung(SPA 553)

Periode/Jahr bei Sammelumwandlung(SPA 553)
(Dieser Steuerparameter behandelt PERIODE und JAHR als
Einheit! Schreibvereinfachung:“Periode“ ident. mit „Periode und Jahr“)
Bei Sammelumwandlung werden Perioden wie folgt
behandelt:
Original nehmen, nach Quelle trennen:
Belege mit identischer Periode werden zusammengefasst
und behalten auch ihre Perioden
Neu, aber nach Quelle
trennen:
Belege mit identischen Perioden werden
zusammengefasst. Der Zielbeleg bekommt jedoch eine neue
Periode.
Keine Trennung + neue Perioden: Es wird nicht nach
Perioden getrennt!

---

## Vorbelegung Formulararchiv-Referenznummer(SPA 554)

Vorbelegung Formulararchiv-Referenznummer(SPA 554)
Bei „Ja“ wird die Formulararchivnummer automatisch
vorbelegt. Falls unter Optionen „FA_Rereferenz_SQL“ ein SQL-Statement hinterlegt
ist, wird dies zur Gestaltung genommen. Falls dieses nicht existiert wird eine
Standardvorbelegung erzeugt.

---

## Artikeltext-Feld-Länge(SPA 557)

Artikeltext-Feld-Länge(SPA 557)
Dieser Steuerparameter wird nicht mehr in
Referenz-ERP-Standardanwendungen ausgewertet. Um die maximale Länge von Artikeltexten
festzulegen, ist der
Steuerparameter
537
zu verwenden.

---

## Bei Kostenstellen Oberkonten bebuchen(SPA 563)

Bei Kostenstellen Oberkonten bebuchen(SPA 563)
Wenn Auswertungen über Oberkonten und Kostenstellen
erstellt werden sollen, kann man hier hinterlegen, dass auch bei Oberkonten die
Summenrelation der Kostenstellen gefüllt wird. Dieser Parameter steht
standardmäßig auf „Ja“. Da das Bebuchen durch die Verwendung von Oberoberkonten
und Verteilkostenstellen sehr Zeitintensiv sein kann, kann hier das bebuchen der
Kostenstellen für Oberkonten abgeschaltet werden. Es stehen dann jedoch für
einige Kostenstellenauswertungen (z.B. Kostenstellen-Abrechnungsübersicht) keine
Daten zur Verfügung.

---

## ELSTER-Lizenz (SPA 565)

ELSTER-Lizenz (SPA 565)
Lizenz für Elster.

---

## Gekennzeichnete EC Zahlung stornierbar(SPA 579)

Gekennzeichnete EC Zahlung stornierbar(SPA 579)
Gilt in Zusammenhang mit Steuerparameter „Manuelle
Erfassung von EC-Karten“, wenn dort „nur Kennzeichnung der Zahlungsart“
eingestellt ist. In diesem Modus wird die EC Karte von Referenz-ERP weder eingelesen
noch werden die Daten eingegeben. Benutzt man diese Einstellung, um die EC
Zahlung per PIN an einem separaten Bankterminal abzuwickeln, so muss die Zahlung
gegen Stornierung gesperrt werden, wenn man keine Möglichkeit hat, die
online-Zahlung selbst ebenfalls zu rückgängig machen zu können.

---

## Wechselbuchhaltung angeschlossen(SPA 6)

Wechselbuchhaltung angeschlossen(SPA 6)
Mit diesem Steuerparameter kann die Wechselbuchhaltung
aktiviert / deaktiviert werden.

---

## Nichteinger. Unternehmen bei Aktien(SPA 607)

Nichteinger. Unternehmen bei Aktien(SPA 607)
•
„
Nichteinger. Unternehmen bei Aktien
“ (Nr. 607) Dieser
Steuerparameter gibt das Verhalten von Referenz-ERP bei Verwenden der
Aktionärsverwaltung an, wenn noch keine Unternehmensdaten eingerichtet sind. Es
gibt folgenden Einstellungsmöglichkeiten:
o
Fehler (empfohlen) – Es lässt
sich nur das Unternehmen einrichten. Alle anderen Fenster schließen sich sofort
wieder mit dem Hinweis, dass keine Unternehmensdaten eingerichtet sind.
o
Warnung – Die
Aktionärsverwaltung lässt sich normal verwenden. Es erfolgt bei jedem öffnen
eines Fensters ein Warnhinweis, dass keine Unternehmensdaten eingerichtet
sind.
o
Ignorieren – Die
Aktionärsverwaltung lässt sich normal verwenden.
Achtung:
Bei nicht eingerichteten
Unternehmensdaten lässt sich keine Dividende abrechnen. Außerdem erfolgt die
Prüfung ob mehr Aktien im Umlauf sind als vom Unternehmen ausgegeben nicht
korrekt.

---

## Formatnummer für Hedge-Order Return-Files (SPA 634)

Formatnummer für Hedge-Order Return-Files (SPA 634)
Nummer des vom Benutzer festgelegten Anwenderformates
„AF_FA_GRUPPE“ für die Hedge-Order-Return-Files im Formulararchiv.

---

## Formatnummer für Hedge-Order-Files (SPA 633)

Formatnummer für Hedge-Order-Files (SPA 633)
Nummer des vom Benutzer festgelegten Anwenderformats
„AF_FA_GRUPPE“ für die Hedge-Order-Files im Formulararchiv.

---

## Automatische Abräumung VorgReservierung(SPA 630)

Automatische Abräumung VorgReservierung(SPA 630)
Behandlung von VorgReservierungsleichen durch den
Mandantenserver:
0=nicht löschen
1=Reservierungssatz entfernen, Belegnummer
bleibt verschwendet
2=Reservierungssatz entfernen und Belegnummer
zur Wiederverwendung freigeben

---

## Mehrmandant direkt speichern(SPA 650)

Mehrmandant direkt speichern(SPA 650)
Mit diesem Steuerparameter kann eingestellt werden, ob
im MMS System direkt in die Untermandanten gespeichert werden soll, oder ob ein
Event die Einspielung der Daten vornimmt.

---

## OLAP beim Druck automatisch archivieren(SPA 705)

OLAP beim Druck automatisch archivieren(SPA 705)
Wird dieser Steuerparameter auf aktiv gesetzt, so wird
ein Druck aus der OLAP-Anzeige automatisch archiviert.

---

## Verbotslistenprüfung-Lizenz(SPA 707)

Verbotslistenprüfung-Lizenz(SPA 707)
Lizenz für die Verbotslistenprüfung.

---

## Vieraugenprinzip Zahlungen(SPA 716)

Vieraugenprinzip Zahlungen(SPA 716)
Mit diesem Steuerparameter kann eingestellt werden, ob
für das DTA Verfahren das Vieraugenprinzip benutzt werden soll. Wird der
Steuerparameter auf
Ja
gestellt so gibt es unter Zahlungen bearbeiten
einen neue Variante.

---

## Nachhaltigkeit-Lizenz(SPA 715)

Nachhaltigkeit-Lizenz(SPA 715)
Lizenz für die Nachhaltigkeit.

---

## Warenposition auf Umbuchungen drucken (SPA 724)

Warenposition auf Umbuchungen drucken (SPA 724)
Wird dieser Steuerungsparameter auf „JA“ gesetzt, so
kann bei Umbuchungen die Warenpositionszeige gedruckt werden. Diese enthält u.U.
auch Gebindeinformationen. Da nicht bekannt ist, inwieweit die Einrichtung der
Warenpositionszeile auf den Formularen erfolgte, ohne dass diese druckbar ist,
wurde dieses Verhalten mit einem Steuerungsparameter geschützt.

---

## Datenbankserver im Hintergrund anpingen. (SPA 733)

Datenbankserver im Hintergrund anpingen. (SPA 733)
Der Steuerparameter gibt an ob die AeinsCE Software im
Hintergrund den Datenbank Server an pingen soll. Es gibt drei
Einstellungsmöglichkeiten
•
Auto:  Server IP automatisch beziehen
•
Manuell: Manuelle Server IP
•
Aus: Ping aus

---

## Kennwortabfrage beim Starten der Software. (SPA 734)

Kennwortabfrage beim Starten der
Software. (SPA 734)
Der Steuerparameter stellt ein, ob vorm Starten der
Aeins Software noch ein Kennwort abgefragt werden soll. Steht dieser
Steuerparameter auf Ja, so muss sich der Anwender mit seinem persönlichen
Kennwort, welches mit einem S für Scanner beginnt und im Bedienerstamm
hinterlegt wurde, am Scanner anmelden. Beim Anmelden muss das S aber nicht mit
angegeben werden.
Dann startet Aeins mit den Benutzerdaten des
Anwenders.

---

## Beeper. (SPA 742)

Beeper. (SPA 742)
Der Steuerparameter steuert, ob eine Scanmelodie bei
jedem Scanvorgang ertönen soll.
•
Datalogic für Datalogic Scanner ohne Soundkarte
•
Andere für alle anderen Scanner ohne Soundkarte
•
Aus der Beeper wird ausgestellt
•
Wave für alle Scanner mit einer Soundkarte

---

## Fehler Wave Sound. (SPA 744)

Fehler Wave Sound. (SPA 744)
Hier kann eine Wave Datei hinterlegt werden, die im
Fehlerfall auf dem Scanner abgespielt werden soll. Die Datei wird nur
abgespielt, wenn der Steuerparameter
Beeper
auf Wave steht.
Die Standardsounds befinden sich in der
Referenz-ERP.Scanner.Zusatz.dll.
Folgende Sounds sind vorhanden
1.
Alarm3.wav
2.
Ring.wav
3.
Ringout.wav
4.
ScanSuccess.wav
Soll ein Wave File abgespielt werden, welches nicht
den Standard Sounds entspricht, so muss dieses in den Referenz-ERP Ordner auf den
Scanner kopiert werden.
Wenn mehrere Wave Files abgespielt werden sollen,
können diese per Semikolon getrennt werden.

---

## Erfolg Wave Sound. (SPA 746)

Erfolg Wave Sound. (SPA 746)
Hier kann eine Wave Datei hinterlegt werden, die bei
einem Erfolgreichen Scann Vorgang  auf dem Scanner abgespielt werden soll.
Die Datei wird nur abgespielt, wenn der Steuerparameter
Beeper
auf Wave steht.
Die Standardsounds befinden sich in der
Referenz-ERP.Scanner.Zusatz.dll.
Folgende Sounds sind vorhanden
1.
Alarm3.wav
2.
Ring.wav
3.
Ringout.wav
4.
ScanSuccess.wav
Soll ein Wave File abgespielt werden, welches nicht
den Standard Sounds entspricht, so muss dieses in den Referenz-ERP Ordner auf den
Scanner kopiert werden.
Wenn mehrere Wave Files abgespielt werden sollen,
können diese per Semikolon getrennt werden.

---

## Excel-Export Referenz oder Kopie (SPA 768)

Excel-Export Referenz oder Kopie (SPA 768)
Wird dieser Steuerparameter auf Kopie gestellt, so
wird aus dem Tabellenblatt „Data01“ in das Tabellenblatt „Tabelle1“ per Kopie in
der Zwischenablage kopiert. Bei der Einstellung Referenz werden hier (diese
Standardeinstellung geht schneller) Datenreferenzen gesetzt.

---

## Sortierung Formularauswahl Lieblingsdrucker (SPA 776)

Sortierung Formularauswahl Lieblingsdrucker (SPA 776)
Hier kann eingestellt werden in welcher Reihenfolge
die Formulare in der Maske Lieblingsdruckerdruck angezeigt werden.
(VRGD/FRZ)

---

## Locking in der Vorgangsmappe (SPA 795)

Locking in der
Vorgangsmappe (SPA 795)
Wird dieser Steuerparameter auf „Ja“ gestellt, können
mehrere Benutzer nicht mehr gleichzeitig eine Vorgangsmappe öffnen.

---

## Löschverhalten bei Vorgangsmappen (SPA 796)

Löschverhalten bei Vorgangsmappen (SPA 796)
Mit diesem Steuerparameter kann das Löschverhalten für
Vorgangsmappen eingestellt werden. Steht der Steuerparameter „Locking in der
Vorgangsmappe“ (
SPA 795
) auf „Nein“ wird nur der
Stammsatz gelöscht, die Verbindungen an den Belegen bleiben dabei erhalten.
Für ein anderes Löschverhalten muss der
Steuerparameter „Locking in der Vorgangsmappe“ auf „Ja“ steht.
Zur Einstellung stehen dann verschiedene Typen zur
Verfügung.
Typ
Wert
EKKLASSE
Einkaufsklasse ab der kein Beleg
      mehr vorhanden sein darf.
Beispiel: Bei 1700 dürfen sich keine
      Belege in der Mappe befinden die eine Rechnung oder höher
      sind.
VKKLASSE
Verkaufsklasse ab der kein Beleg
      mehr vorhanden sein darf.
Beispiel: Bei 700 dürfen sich keine
      Belege in der Mappe befinden die eine Rechnung oder höher
      sind.
Wird bei beiden Werten nichts eingetragen, erfolgt
keine Stornierung der Belege. Es wird dann nur der Stammsatz gelöscht und die
Verbindung an den Belegen entfernt.

---

## Kostenstellenrechnung angeschlossen(SPA 8)

Kostenstellenrechnung angeschlossen(SPA 8)
Mit diesem Steuerparameter kann die,
Kostenstellenrechnung aktiviert / deaktiviert werden.

---

## Bei Umwandlung von Belegen auf Mandantenserververarbeitung warten (SPA 800)

Bei Umwandlung von Belegen auf
Mandantenserververarbeitung warten (SPA 800)
Hiermit kann gesteuert werden, dass vor dem Nachlauf
einer
Umwandlung
auf die Verarbeitung durch
den Mandantenserver gewartet werden soll.

---

## Sprach-Lizenz-Englisch (SPA 804)

Sprach-Lizenz-Englisch (SPA 804)
Lizenz für die Sprache Englisch.

---

## Sprach-Lizenz-Französisch (SPA 806)

Sprach-Lizenz-Französisch (SPA 806)
Lizenz für die Sprache Französisch.

---

## Sprach-Lizenz-Dänisch (SPA 805)

Sprach-Lizenz-Dänisch (SPA 805)
Lizenz für die Sprache Dänisch.

---

## Sprach-Lizenz-Niederländisch (SPA 807)

Sprach-Lizenz-Niederländisch (SPA 807)
Lizenz für die Sprache Niederländisch.

---

## Speichern der erfassten Daten mit dem Identass Scanner(SPA 810)

Speichern der erfassten Daten mit dem Identass Scanner(SPA 810)
Mit diesem Steuerparameter kann eingestellt werden in
welcher Relation der Scanner die erfassten Daten speichert.
•
Bei der Einstellung MDE Übernahme werden die Daten in die Relation
MDEUebergabe geschrieben.
•
Bei der Einstellung MDE Übernahme/ Inventurbeleg werden die Daten in der
Relation MDEUebergabe und in Inventurbeleg.gespeichert Die Daten aus
MDEUebergabe können nicht mehr eingespielt werden.
•
Bei der Einstellung Inventurbeleg werden die erfassten Daten Direkt in
den Inventurbeleg geschrieben,

---

## Reihenfolge der Datumsangaben bei Umwandlung muss stimmen (SPA 820)

Reihenfolge der Datumsangaben bei Umwandlung muss stimmen
(SPA 820)
Wird dieser Steuerparameter auf „Ja“ gestellt, dürfen
bei der Umwandlung nur Folgebelege erstellt werden, deren Vorgangsdatum größer
oder gleich dem Vorgangsdatum des Ursprungsbelegs liegt. Eine Rechnung, deren
Datum vor dem Datum des Lieferscheins liegt, wäre dann nicht möglich.
Diese Behandlung gilt nur für die Umwandlung von
Standardvorgängen – nicht jedoch für Rohware

---

## Fehlersound für keine Datenbankverbindung(SPA 831)

Fehlersound für keine Datenbankverbindung(SPA 831)
Mit diesem Steuerparameter kann hinterlegt werden,
welche Wave Datei abgespielt werden soll, wenn keine Datenbankverbindung
vorhanden ist.

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

## Vorbelegung der Anteils bei der Zeichnung von Anteilen bei der Mitgliedsverwaltung(SPA 843)

Vorbelegung der Anteils bei der Zeichnung von Anteilen
bei der Mitgliedsverwaltung(SPA 843)
Mit diesem Steuerparameter kann eingestellt werden wie
hoch die Vorbelegung beim Zeichnen von Anteilen sein soll. Mit F3 auswählbar
sind Zahlen von 1-20. Die Vorbelegung ist 1.

---

## HTML Anzeige beim Scanner(SPA 842)

HTML Anzeige beim Scanner(SPA 842)
Mit diesem Steuerparameter kann eingestellt werden, ob
der Scanner die Itembox als HTML Seite darstellt. Ab der Version 7.8.5.107
funktioniert nur noch die HTML Version

---

## Nachhaltigkeitseinstellungen (SPA 844)

Nachhaltigkeitseinstellungen (SPA 844)
In diesem Steuerparameter können Optionen für die
Nachhaltigkeit eingestellt werden.
Zur Einstellung stehen verschiedene Typen zur
Verfügung.
Typ
Wert
MANDSERREFRESH
Das
      Aktualisieren der Nachhaltigkeitswerte erfolgt durch den Mandantenserver.
      Standardmäßig erfolgt eine Abarbeitung, auch wenn kein Wert eingetragen
      ist. Nur wenn der Wert „0“ (deaktiviert) eingetragen wird, erfolgt
keine
Abarbeitung durch den Mandantenserver.
STATUSMANUELL
Hiermit kann eingestellt werden das
      beim reinitialisieren der Werte durch den Mandantenserver oder über das
      JPP-Objekt, der Status auch gesetzt werden soll, wenn er manuell gesetzt
      wurde.
Damit der manuelle Wert ersetzt
      wird, muss der Steuerparameterwert auf „0“ (deaktiviert) gesetzt
      werden.
THGMANUELL
Hiermit kann eingestellt werden,
      dass beim Reinitialisieren der Werte durch den Mandantenserver oder über
      das JPP-Objekt, die THG-Werte auch gesetzt werden soll, wenn sie manuell
      gesetzt wurden.
Damit die manuellen Werte ersetzt
      werden, muss der Steuerparameterwert auf „0“ (deaktiviert) gesetzt
      werden.
ANBAULANDMANUELL
Hiermit kann eingestellt werden,
      dass beim Reinitialisieren der Werte durch den Mandantenserver oder über
      das JPP-Objekt, das Anbauland auch gesetzt werden soll, wenn es manuell
      gesetzt wurde.
Damit der manuelle Wert ersetzt
      wird, muss der Steuerparameter auf „0“ (deaktiviert) gesetzt
      werden.
REFRESHZERTIFIKAT
Hiermit kann eingestellt werden,
      dass beim Reinitialisieren der Werte durch den Mandantenserver oder über
      das JPP-Objekt, das Zertifikat neu ermittelt wird. Standardmäßig werden
      die Zertifikatwerte nur aktualisiert.
Damit das Zertifikat neu ermittelt
      wird, muss der Steuerparameterwert auf „0“ (deaktiviert) gesetzt
      werden.
MANDSERREFRESHSECONDS
Hier
      kann eingetragen werden, in welchem Intervall der Mandantense
[...]


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

## Nur aktuelle Belege bereitstellen für openTRANS (SPA 854)

Nur aktuelle Belege bereitstellen für openTRANS (SPA
854)
Ist dieser Steuerparameter aktiviert, so werden im
Export-Dateiverzeichnis alle bisherigen Exporte eines Beleges bei der Erstellung
gelöscht, nachdem der Export gespeichert wurde.

---

## Gelangensbestätigung-Lizenz(SPA 865)

Gelangensbestätigung-Lizenz(SPA 865)
Lizenz für Gelangensbestätigungen und die zugehörigen
Verwaltungsfunktionen.

---

## Aufbewahrungszeit Mandser-Protokoll (SPA 869)

Aufbewahrungszeit Mandser-Protokoll (SPA 869)
Das Mandantenserverprotokoll wird vom Mandantenserver
geschrieben und enthält alle Einträge, die dieser normalerweise in einer
grafischen Benutzeroberfläche anzeigen würde. Dies kann mit Hilfe des
Direktsprungs [MPROT] eingesehen werden. Die Dauer der Tage, für die das
mandantenserverprotokoll aufbewahrt wird kann mit diesem Steuerparameter
festgelegt werden. Der Vorgabewert ist 10 Tage.
Der Mandantenserver löscht selbständig in regelmäßigen
Abständen ältere Einträge.

---

## TERRES-Artikelpool-Lizenz(SPA 872)

TERRES-Artikelpool-Lizenz(SPA 872)
Lizenz für die Datendrehscheibe / TERRES.

---

## SEPA Datenträgeraustausch Lizenz (SPA 871)

SEPA Datenträgeraustausch Lizenz (SPA 871)
Lizenz für den SEPA Datenträgeraustausch.

---

## Belegimport Positionsaufteilung Menge / Betragsprüfung (SPA877)

Belegimport Positionsaufteilung Menge / Betragsprüfung
(SPA877)
Mit diesem Steuerparameter kann das Verhalten
bezüglich der Mengen / Betragsprüfung der aufgeteilten Position zu der Position
im Terres Beleg geändert werden.
Einstellung
Bedeutung
Mengen und
      Betragsprüfung
Es
      wird überprüft, ob die Aufgeteilte Menge und der Aufgeteilte Betrag mit
      der Terres Position übereinstimmt.
Dies
      ist der Standard.
Nur
      Mengenprüfung
Hier
      wird nur die Menge überprüft, der Betrag kann Unterschiedlich zum Betrag
      der Terres Position sein
Nur
      Betragsprüfung
Hier
      wird nur der Betrag geprüft, die Menge kann unterschiedlich zu der Terres
      Position sein.
Keine Prüfung
Die
      Überprüfung ist ausgestellt. Menge und Betrag kann unterschiedlich zu der
      Position in dem Terres sein.

---

## WLAN Prüfung für Scanner deaktivieren (SPA 879)

WLAN Prüfung für Scanner deaktivieren (SPA 879)
Mit diesem Steuerparameter kann eingestellt werden, ob
die WLAN Überprüfung im Scanner deaktiviert werden soll.

---

## HTML Style Sheet (SPA 880)

HTML Style She
et (SPA 880)
An diesem Steuerparameter kann eine eigene Private
Prozedur hinterlegt werden, die das Layout der HTML Seite auf dem Scanner
übersteuert. Wird dieser Steuerparameter nicht gesetzt, so wird die
Standardprozedur verwendet.

---

## Belegdrucker(SPA 886)

Belegdrucker(SPA 886)
Nicht WebPortal 2.0
Komplexer Steuerparameter.
Festlegung des Druckers für Belege aus dem
Webportal.
(Zur Zeit nur für individuelle Webportal-Lösungen
vorgesehen)
-
Schlüssel
-
Option (Druckernummer)

---

## Private Prozedur zum Übersteuern der Standard Melodie(SPA 885)

Private Prozedur zum Übersteuern der Standard
Melodie(SPA 885)
An diesem Steuerparameter kann eine Private Prozedur
hinterlegt werden, die die Standardmelodie überschreibt.

---

## Volltextrecherche-Lizenz(SPA 914)

Volltextrecherche-Lizenz(SPA 914)
Lizenz für die Volltextrecherche.

---

## Kontierung per Archiv-Lizenz(SPA 915)

Kontierung per Archiv-Lizenz(SPA 915)
Lizenz für die Kontierung per Archiv.

---

## Kontierung aktiv(SPA 920)

Kontierung aktiv(SPA 920)
Mit diesem Steuerparameter kann die Kontierung
aktiviert / deaktiviert werden.

---

## Tammo Einstellungen(SPA 933)

Tammo Einstellungen(SPA 933)
In diesem Steuerparameter können die Optionen für das
Modul
Tammo
eingestellt werden. Die
folgenden Felder werden im Modul genauer beschrieben.
Wert
Text
Beschreibung
0
-
1
Mailplugin
Name
      des Mailplugins
2
Benutzername / E-Mail
Benutzername oder E-Mailadresse
3
Passwort
Passwort des Benutzers
4
Domain / Host
Domain des Benutzers oder Host des
      Providers
5
Webservice Exchange
      Version
Bezeichnung der Exchange
      Version
6
Webservice Autosicover
      Url
E-Mailadresse des
      Benutzers
7
Verarbeitungsfunktion durch
      Mandantenserver
Name
      der Datenbankfunktion, die zur Analyse der Daten aufgerufen werden
      soll.
8
Port
Hier
      kann der Port angegeben werden.
9
SSL
      verwenden
Hier
      kann angegeben werden, ob SSL verwendet werden soll oder
      nicht.
10
Abrechungsartikel
11
Excelimportprozedur
12
Excel -BI- Anwendung
13
Excel -BI- Variante
14
Tammo -BI- Einrichtung
15
Prozedur
      Abrechnungsartikel
16
Protokoll – Level
17
Anhang in PDF/A
      Umwandlung
Aktiviert mit dem Wert „TRUE“ die
      Umwandlung von Anhängen in das Format PDF/A. Standardmäßig ist die
      Umwandlung deaktiviert.
18
Anhang in PDF/A Umwandlung
      (Parameter)
Nicht aktiv!

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

## openTRANS Vorgangsimport-Lizenz(SPA 938)

openTRANS Vorgangsimport-Lizenz(SPA 938)
Lizenz für den openTRANS Vorgangsimport.

---

## Individuelle Settings für den Scanner(SPA 952)

Individuelle Settings f
ür den Scanner(SPA 952)
An diesem Steuerparameter können Private Einstellungen
hinterlegt werden. Dieser Steuerparameter wird in den Standard Modulen nicht
ausgewertet.

---

## Escapesteuerung im Scanner(SPA 963)

Escapesteue
rung im Scanner(SPA 963)
Mit diesem Steuerparameter kann eingestellt werden, ob
die Escape Taste das Programm nicht schließt, sondern das der verarbeitenden
Prozedur mitgeteilt als String „Escape“ wird, dass die Escape Taste gedrückt
wurde. Dies wird nicht im Standard ausgewertet.
Einstellung
Bedeutung
Nein
Escape schließt die
      Maske
Ja
Das
      Programm wird nicht geschlossen, es wird der verarbeitenden Datenbank
      Prozedur mitgeteilt, dass die Escape Taste gedrückt wurde. Kommt dann eine
      999 im Statusfeld zurück wird die Scannersoftware geschlossen.

---

## Beleganlage trotz fehlerhafte Position im Vorgangsimport(SPA 965)

Beleganlage trotz fehlerhafte Position im Vorgangsimport(SPA 965)
Mit diesem Steuerparameter kann eingestellt werden, ob
ein Beleg aus dem Vorgangsimport heraus erzeugt werden soll, obwohl eine
Position nicht in den Beleg übernommen wurde.
Einstellung
Bedeutung
Ja
Steht der Steuerparameter auf „Ja“
      so wird der Beleg erstellt ohne die Fehlerhafte Position. Dies ist der
      Standard Fall.
Nein
Steht der Steuerparameter auf „Nein“
      so wird der Beleg nicht erzeugt. Dieser wird dann im Vorgangsimport auf
      „Fehlerhaft“ gestellt.

---

## SEPA Testlauf (SPA 969)

SEPA Testlauf (SPA 969)
Muss zu Testzwecken eine Sepa- Übertragung zwar
ausgeführt werden, aber nicht an die Bank transferiert werden, dann kann dieser
Parameter gesetzt werden, um einen Test durchzuführen.

---

## ADR-Gefahrgutlisten Lizenz(SPA 972)

ADR-Gefahrgutlisten Lizenz(SPA 972)
Lizenz für die Verwendung des
ADR-Gefahrgutlisten-Importers sowie der weiteren Verwendung der ADR-Daten aus
Referenz-ERP heraus.

---

## Handelsstückliste bei Kasse aktiv (SPA 979)

Handelsstücklist
e bei Kasse aktiv (SPA 979)
Sollen Handelsstücklisten in der Kasse gezogen werden.
(Standard: Wie Spa)
Wert
Bedeutung
Wie
      Spa
Die
      Behandlung der Handelsstücklisten erfolgt wie bisher nach den vorgegebenen
      Steuerparametern (SPA 307: Handelsstückliste aktiv, SPA 534:
      Stücklistenmechanismus bei Kasse?).
Nein
Handelsstücklisten werden nicht
      gezogen.
Ja
Handelsstücklisten werden
      gezogen.

---

## EC-Überzahlung in der Marktkasse-Lizenz (SPA 988)

EC-Überzahlung in der Marktkasse-Lizenz (SPA 988)
Lizenz für die EC-Überzahlung in der Marktkasse.

---

## Makro 2.0 Lizenz(SPA993)

Makro 2.0 Lizenz(SPA993)
Lizenz für die Erstellung und von Makro 2.0 im Pfleger
[CSM] incl deren dortigen Ausführung. Die Ausführung über Controlstrings ist
nicht lizenzpflichtig.

---

## Tammo-Lizenz(SPA996)

Tammo-Lizenz(SPA996)
Lizenz für Tammo.

---

## Ausschalten der Referenz-ERP Scanner Kennwortabfrage beim Anschalten des Gerätes(SPA 998)

Ausschalten der Referenz-ERP Scanner Kennwortabfrage beim Anschalten des
Gerätes(SPA 998)
Dieser Steuerparameter wird nur in Abhängigkeit mit
dem Steuerparameter
„Kennwortabfrage
beim Starten der Software (734)“
ausgewertet.
Einstellung
Bedeutung
Nein
Die
      Kennwortabfrage wird angezeigt
Ja
Die
      Kennwortabfrage erscheint nur beim Starten der Referenz-ERP
      Scannersoftware

---

## Signature Pad und Software am Arbeitsplatz einrichten

Signature Pad und Software am Arbeitsplatz einrichten
Voraussetzungen und benötigte Software siehe Kapitel
Signature Pad
einrichten
.

---

## Signature Pad einrichten

S
ignature Pad
einrichten
Um PDF-Dokumente signieren zu können wird ein
Signature Pad benötigt. Dieses Kapitel beschreibt den Einrichtungsvorgang.
Es wird folgendes benötigt:
•
1 freier USB2-Steckplatz
•
Signature Pad „signotec Sigma“ mit FTDI-Chip
•
Treiber
•
Tools „signoPAD-Tools“
•
Software „SignoSign/2“
•
Lizenz für Software „SignoSign/2“
•
PDF-Vorlage „allgemein.pdf“ (Erzeugt aus Textdokument mit einem
Leerzeichen)
Der Treiber kann auf der Internetseite des Herstellers
heruntergeladen werden:
https://www.signotec.com/download/treiber/ftdi-treiber/
Es ist die ausführbare Exe-Datei zu verwenden.
Das Werkzeug „SignoPAD-Tools“ kann auf der
Internetseite des Herstellers heruntergeladen werden:
https://www.signotec.com/download/tools/signopad-tools/
Es ist die Version für 64 Bit zu verwenden.
Die Software „SignoSign/2“ kann auf der Internetseite
des Herstellers heruntergeladen werden:
https://www.signotec.com/portal/seiten/download-signosign-2-900000336-10002.html
Es handelt sich hierbei um ein kostenpflichtiges
Programm. Für den Download ist eine Registrierung notwendig.
Nach Bestellung und Bezahlung kann die Lizenz mittels
Email an
lizenz@signotec.de
angefordert
werden.

---

## Testmandant

Testmandant
Menü: Administration
Werkzeuge
Testmandant (Direktsprung: [TMD])
Dieses Werkzeug bietet die Möglichkeit, einen
Testmandanten zu erstellen. Dies ist eine Kopie des aktuellen Mandanten mit
sämtlichen Einrichtungen, die nötig sind, um Referenz-ERP auf einem Testmandanten zu
starten.
Voraussetzungen
Es müssen ausreichend Rechte und Speicherplatz auf dem
Server und dem Zielordner vorhanden sein.
Die „AmicConf.ini“ wird anhand des Profilnamens
angelegt, wenn der Eintrag noch nicht vorhanden ist. Ansonsten wird der Eintrag
nicht
aktualisiert. Es wird kein automatischer ODBC-Eintrag erzeugt.
Eine weitere Voraussetzung ist, dass die Einstellung
der „Serverlog.txt“ auf den Pfad „bin“ oder „bin64“ im Referenz-ERP Pfad eingestellt
ist.
Beim Erzeugen des Backups wird vorher versucht die
Testdatenbank runterzufahren, auch wenn noch Bediener angemeldet sind. Dabei
wird angenommen, dass sich die Testdatenbank auf dem gleichen Server befindet
und den Namen des Profils hat.
Erstellung
Für die Erstellung des Testmandanten stehen folgende
Felder zur Verfügung. Nachdem diese ausgefüllt wurden, kann über die Funktion
„Erstelle Testmandant“ die Erstellung begonnen werden.
Feldname
Beschreibung
Profil
Hier
      kann ein Profilname eingetragen oder ausgewählt werden. Mit diesem lassen
      sich gespeicherte Einstellungen schnell wieder laden.
Des
      Weiteren wird der Profilname auch für die „AmicConf.ini“ als Section und
      Datenbankname verwendet.
Aktueller Datenbankpfad
Hier
      wird der aktuelle Datenbankpfad angezeigt.
Zielverzeichnis
Hier
      kann das Zielverzeichnis des Testmandanten eingetragen werde.
Datenbankpräfix
Hier
      kann ein Präfix für die Datenbank eingetragen werden.
Verzeichnis leeren
Hiermit kann eingestellt werden, ob
      das Zielverzeichnis gelöscht werden soll.
Nachlaufprozedur
Hier
      kann eine Nachlaufprozedur eingetragen werden, mit der bestimmte
      Einstellungen geändert werden könnten. Standardmäßig wird die Prozedur

[...]


---

## Variante „Parameter-Übersicht“

Variante „Parameter-Übersicht“
Hauptmenü
Administration
Werkzeuge
Parameter-Übersicht
Direktsprung
[PARA]
Mit Hilfe dieser Variante lassen sich die aktuellen
Laufzeit-Parameter des Referenz-ERP-Clienten anzeigen.
Parameter haben diverse Quellen.
-
Einige werden beim Programmstart ermittelt.
-
Andere Parameter werden ermittelt entsprechende Programmabschnitte durchlaufen
werden.
Sie werden programmseitig
oft mit einem Default-Wert vorbelegt, somit muss nicht jeder Parameter explizit
angegeben werden.
So ermittelte Parameter werden gecached.
Felder
Auswahlliste
Parameter
Der
      Name des Parameters
Wert
Der
      Wert des Parameters
Zugriffe
Gibt
      die Anzahl der Ermittlungen des Parameters innerhalb der aktuellen
      Laufzeit vom Programm an.
Hinweis: Da die Parameter zwischengespeichert
      sind erfolgt nicht jedes Mal ein erneuter Zugriff auf externe Ressourcen.
HERKUNFT
Gibt an wo das Parameter den Wert für den Parameter
      gefunden hat:
DEFAULT: Es wurde keine explizite Parameterangabe
      gefunden und der übergebene Default-Wert genommen.
CMDLINE: Parameter
      wurde per Kommandozeile übergeben.
CALCULATED: Der Wert
      des Parameters wurde software-technisch ermittelt.
HKCU-MANDANT:
      Windows-Registrierung
AHOI-MANDANT: Mandant-Eintrag in
      `ahoi.ini`
Weitere können
      sein:
PH_CMDLINE          =
      0,
PH_HKLM_MANDANT     =  1,
PH_HKLM_Branchen-ERP        =
      2,
PH_AHOI_MANDANT     =  3,
PH_AHOI_Branchen-ERP        =
      4,
PH_AMICCONF_MANDANT =  5,
PH_AMICCONF_Branchen-ERP    =  6,
PH_HKCU_MANDANT     =  7,
PH_HKCU_Branchen-ERP        =
      8,
PH_DEFAULT          =
      9,
PH_DEFAULTSTARTUP   = 10,
PH_CALCULATED       = 11,
PH_DATABASECONNECT  = 12,
PH_UNBEKANNT
      = 99
(99 ist kein Fehler sondern bedeutet das der Parameter nicht
      aus den vorherigen Quellen stammt.)
Nr
Laufende Nummerierung
Auswahlbedingungen
Suchen
Führt eine Like-Suche in den Feldern
      Name und Wert durch
Funktionen
Keine

---

## Abkündigung: Mehrmandantensystem

Abkündigung: Mehrmandantensystem
Das Mehrmandantensystem wurde vor vielen Jahren im
System integriert. Zwischenzeitlich gibt es zuverlässige Methoden, mehrere
Datenbanken auf einem gleichen Stammdatenstand zu halten.  Inhaltlich
entwickeln wir das Mehrmandantensystem nicht mehr weiter. Um auf die neuen
Transfer umzustellen, müssen leider die eindeutigen Schlüssel in den
Datenbanktabellen in allen Datenbanken identisch sein. Das ist vom
Mehrmandantensystem nicht gewährleistet. Als Voraussetzung für die Integration
der Replikationslösung müssen Sie einen ihrer bisherigen Mandanten als
„Hauptmandanten“ definieren. Alle angeschlossen Mandanten müssen mit einem neuen
Wirtschaftsjahr quasi bei 0 mit der Vorgangserfassung beginnen. Es sind
Vorkehrungen zu treffen, dass gewisse Systemstammdaten unabhängig voneinander
geführt werden können. Im Einzelfall muss hier ein Gespräch stattfinden und ein
Lösungsansatz für die Umstellung der System erstellt werden.
Tags:
Abkündigung

---

## OLE Steuerparameter

OLE Steuerparameter
Die OLE-Steuerparameter 373, 377 und 671 sind
deaktiviert worden, weil OLE in der 64-Bit-Version nicht mehr unterstützt wird
und inzwischen andere Techniken genutzt werden. Unter Anderem wird ein
Excel-Export seit 2009 mit .Net-Technologie angesteuert. Die SPA-Einstellungen
werden entsprechend abgeändert.
Tags:
Abkündigung

---

## Abkündigung: Callback Dialog

Abkündigung: Callback Dialog
Es gab einen Hintergrundprozess namens
"CALLBACKDIALOG".  Dieser wurde durch den neuen "Referenz-ERP.Worker"
abgelöst.  Bestehende Einrichtungen müssen umgestellt werden.
Tags:
Abkündigung

---

## Abweisen ab

Abweisen ab
Wenn Sie denn nun Referenz-ERP so präpariert haben, dass es
die externe Darstellung zum Anzeigen der Belege verwendet und sie zu viele
Belege zur Ansicht markiert haben, dann laufen Sie Gefahr, den Speicher Ihres
Systems zu ruinieren. Mit diesem Parameter können Sie angeben, ab wie viel
Einheiten das Anzeigen verweigert werden soll.

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
in integrierter Form in Referenz-ERP (embedded) auf Terminalservern zu erheblichen
Anzeige-Updates führt, die ein flüssiges Arbeiten im herkömmlichen Sinne nicht
unterstützen.
Ein Problem stellt die so genannte eingebettete
Ansicht dar, am Beispiel eines PDF-Beleges sieht man, dass die zugrunde liegende
Applikation (bei PDF der Adobe Acrobat Reader) im Referenz-ERP-Fenster eingebettet ist
(das geht wie oben gesehen auch mit z.B. Word- und Excel-Dokumenten).
Mit Hilfe der Pfeil-Kontrollen lässt sich gerade bei
Mehrfachauswahl in der zugrundenliegenden Auswahlliste schön hin- und
herblättern.
Das funktioniert auf den allermeisten Arbeitsplätzen
einwandfrei.
Auf Terminalservern und einigen Notebooks hingegen
bekommt das System Refresh-Probleme und in diesen Fällen wird die Geduld des
Anwenders arg strapaziert. Leider enthebt sich diese Problematik meinen
Zugriffsmöglichkeiten, aber es gibt einen Ausweg. Man kann konfigurieren, dass
die Ansicht nicht integriert sein soll, dann wird ein extra Fenster aufgemacht
und der Beleg dort dargestellt. M
[...]


---

## Anwendungsbeispiel Outlook

Anwendungsbeispiel Outlook
Hier soll nun die Fähigkeit, einen externen Import ins
Formulararchiv mittels eingehender Mail via Outlook, demonstriert werden.
Dazu kopiert man sich unten folgendes Outlook-Script
in die VBAProjekt.OTM und passt in der Zeile 2 den Parameter auf sie Sektion an
mit seinem eigenen Mandanten/Sektion-Namen. In Zeile 3 kann – muss aber nicht –
der Arbeitspfad angepasst werden; er sollte aber auf jedem Falle vorhanden sein.
Bitte denken Sie daran in vorher anzulegen.
Wichtig ist die Zeile 3, in der die Ident des Imports
anzugeben ist. In meinem Beispiel ist es die 24.
Als weitere vorbereitende Maßnahme sollten Sie – falls
noch nicht geschehen – das COM-Objekt Referenz-ERP einmalig registrieren, das
geschieht durch den Aufruf / Kommandozeile im Bin-Verzeichnis von Referenz-ERP
Aeins.exe welcome ServerInstall=true
Public Sub Aeins_Export()
Dim Aeins_Verbindung As String: Aeins_Verbindung
= "section=ah"
Dim Aeins_ImportPfad As String: Aeins_ImportPfad
= "c:\temp\outlook"
Dim Aeins_ImportProfil As Integer:
Aeins_ImportProfil = 24
Dim myOlApp As Object: Set myOlApp =
CreateObject("Outlook.Application")
Dim myItem As Outlook.Inspector: Set myItem =
myOlApp.ActiveInspector
If TypeName(myItem) = "Nothing" Then
MsgBox "Kein aktives
Mailfenster!"
GoTo raus
End If
Dim objItem As Object: Set objItem =
myItem.CurrentItem
Dim SenderEmailAddress As String
If objItem.SenderEmailType = "SMTP" Then
SenderEmailAddress =
objItem.SenderEmailAddress
Else
SenderEmailAddress =
objItem.SenderName
End If
' ersetze @ durch .
SenderEmailAddress = Replace(SenderEmailAddress,
"@", ".")
Dim Aeins As Object: Set Aeins =
CreateObject("Branchen-ERP.Aeins")
If Aeins Is Nothing Then
MsgBox "Es besteht keine
Aeins-Verbindung!"
GoTo raus
End If
Dim Connect As Boolean: Connect =
Aeins.Connect(Aeins_Verbindung)
If Connect = False Then
MsgBox "Connect zur Datenbank
fehlgeschlagen!"
GoTo ende
End If
Dim hdl As String: hdl = "outlook is
calling"
Aeins.jpp_new hdl, "JFileSystem"
Aeins
[...]


---

## Archiv-Administration

Archiv-Administration
Hauptmenü
Administration
Archiv
Administration
Direktsprung
[FAAD]
In dieser Anwendung stehen für administrative Aufgaben
folgende Varianten zur Verfügung:
•
Formulararchiv-Administration
•
Technisch
•
Formulararchiv (
Belege ohne Basis )
•
Formulararchiv (
Belege ohne Archiv )
•
Formulararchiv ( Belege
mit NULL )
•
Formulararchiv
Gruppe
•
Archiv
Auslagerung
•
Gedruckte Vorgänge
ohne Archiv-Belege

---

## Archiv-Ansichten-Variante: Profile

Archiv-Ansichten-Variante
: Profile
Dokumentenverwaltung
Dokumentenverwaltung
Ansichten
Archiv – Profile
Direktsprung
[FAA]
Dokumentenverwaltung
Dokumentenverwaltung
Einrichtung Archiv-Profile
Archiv-Profile
Direktsprung
[ARPRO]
Hier werden die Archiv-Profile der
Dokumentenverwaltung gepflegt. Die Archiv-Profile steuern zunächst vornehmlich
im Belegfluss Filter, Funktionen, Direktsprung und weitere Parameter.
Felder
Profilname
Ansichtsprofil-Identifikation
Dieser Profilname wird an den
      betreffenden Stellen auf Masken und Funktionsbezeichnungen dargestellt.
Funktion
Funktions-Identifikation (siehe
      Erläuterungen zur Funktion und Optionbox)
Optionbox
Optionbox-Identifikation (siehe
      Erläuterungen zur Funktion und Optionbox)
Erläuterungen zur Funktion und
      Optionbox:
Funktion und Optionbox bestimmen den
      Kontext der durch das Profil aufgerufenen Aeins-Funktionalität, geben als
      auch die Berechtigungsrolle vor.
Die
      auslösende Funktion in der Dokumenten-Verwaltung ist
. Ihre „Sichtbarkeit“ wird durch die
      üblichen Rollen-Einstellungen gesteuert.
(der
      betreffende Kontext ist
      ah_archivbelegfluss/OB_ARCHIV.VIEWDIALOG)
Der
      Rollen-Kontext dieser
Funktion
und der angegebenen
Optionbox
bestimmt allerdings ob der Archiv-Editor – also die eigentliche
      Belegfluss-Aktivität - ausgeführt werden darf. (Somit ist es möglich die
      Daten des Belegflusses einerseits einzusehen, aber rollentechnisch zu
      verhindern, dass der Archiv-Editor auf diesen Daten aufgerufen werden
      kann)
Sql
      …
Der
      Sql-Schnipsel der an das Archiv-Sql angehängt wird der die Ermittlung der
      Daten durchführt.
Vorteil der Anzeige des
      Sql-Schnipsels:
Die
      Anzeige des Sql-Schnipsels ermöglicht die Suche nach bestimmten Kriterien.
Nachteil der Anzeige des
      Sql-Schnipsels:
1)   Der tatsächlich
      eingerichtete Sql-Schnipsel kann durchaus länger als die maximalmögliche
      Anzahl von
[...]


---

## Archiv Barcode

Archiv Barcode
Das Referenz-ERP-Archiv unterstützt nun direkt die zentrale
Erfassung von Belegen über Barcode-Systeme.
Zu diesem Zweck ist ein Feld „Barcode“ ins Archiv
eingeführt worden und steht somit in allen betreffenden Dialogen und Auswahlen
zur Verfügung.
Bei der Einrichtung des zentralen Imports der Belege
ist darauf zu achten, dass der ermittelte Barcode dem dafür zugewiesenen neuen
Feld zugeordnet wird (In FA-Spalte „Barcode“) und das die Belegklasse mit der
Konstanten 8019 (Belegklasse Barcode) ausgewiesen wird.
Die Zuordnung eines solchen integrierten
Barcode-Beleges kann dann kontextabhängig an allen Stellen, wo eine „Archiv
anzeigen“-Funktionalität verfügbar ist, über die dortige Funktion
Barcode zuweisen
durchgeführt werden. In
diesem Falle hat man idealerweise das Dokument zum Abscannen des Barcodes
vorliegen. Intern werden dann alle entsprechenden Archiv-Barcode-Belege – sofern
noch nicht geschehen – mit den Archiv-Kontextdaten (z.B. Referenz, Kundennummern
Belegnummer sofern verfügbar) angereichert und stehen somit direkt im jeweiligen
Kontext zur Verfügung.
Felder
Referenz
Referenz des
      Programm-Kontextes
Belegnummer
Belegnummer des
      Programm-Kontextes
KndNr.
Kundennummer des
      Programm-Kontextes
Barcode
Hier
      ist der zu suchende Barcode anzugeben bzw. einzuscannen
Funktionen
Hinzufügen [F9]
Versucht den angegebenen Barcode im
      Formulararchiv zu finden und gemäß obigen Vorgaben zu
      verschlagworten.

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

## Archivdatenbank Extern einrichten

Archivdatenbank Extern einrichten
Archivdatenbank Extern:
1.
Kleine Referenz-ERP Datenbank (Basis) als Archiv.db mit Archiv.log bereitstellen
(dblog –t archiv.log ..\daten\archiv.db)
2.
Service erweitern, im Parameter die Archiv.db -n archiv hinzufügen
3.
Odbc aufrufen und ODBC Verbindung unter System auf diese Datenbank wie auch die
laufende Datenbank anlegen (ODBC Name Archiv und testen!!)
Achtung bei 64 bit bitte zunächst die 64 bit Treiber
einrichten.
Scview Aufrufen und Datenbank wie auch Archivdatenbank
öffnen
Erfasster
Bildschirmausschnitt: 03.03.2009; 11:41
Jetzt bitte in der Archivdatenbank einen
Fremdserveranschluss an die aktuelle Datenbank einrichten (dieser wird nur
temporär genutzt für den Datentransfer.
Rechte Maustaste auf Fremdserver und dann Neu.
Zum Schluss mit Commit und dann Exit
abschließen
Jetzt im Archivserver den Fremdserver wieder entfernen (rechte
Maustaste auf proxytabelle und löschen und dann rechte Maustaste auf Server und
löschen.)
Danach in der aktuellen Datenbank die Tabelle Archiv
komplett löschen
Tabelle auswählen, Archiv suchen, rechte Maustaste und
Löschen.
Dann das ganze umgekehrt, in der aktuellen Datenbank
einen Proxyserver anlegen (wie oben) mit dem Namen Archiv, dann die Tabelle
Archiv unter dem Namen Archiv einbinden.
Im Bedienerstamm noch kurz die Rechte für alle
Bediener auf das Fremdarchiv aktivieren.
FERTIG

---

## Archivierung Dateisystem

Archivierung Dateisystem
Bei der Archivierung ins Dateisystem werden die Belege
samt Verwaltungsinformation ins Dateisystem geschrieben. Hierbei ist wichtig zu
wissen, dass die Anwendung „Formulararchiv“ dabei nicht Verwendung findet.
Recherche und Ansehen von Belegen wird dann über ein externes Programm (AMICAR)
abgewickelt.

---

## Archiv ohne Mandantenstammsätze

Archiv ohne Mandantenstammsätze
Hauptmenü
Administration
Archiv
Administration
Archiv ohne Mandanten-Stammsätze
Direktsprung
[FAAD]
Diese Variante bietet Unterstützung bei
Archiv-Einträgen die keine Formulararchiv-Einträge mehr besitzen.
Der Zusammenhang von Archiv und Formulararchiv wird
über eine Guid hergestellt.
Wenn dann ein zugehöriger Formulararchiv-Eintrag
fehlt, hat das System keinerlei Informationen mehr, worum es sich handelt. Mit
dieser Variante kann man aber versuchen, den eigentlichen Archiv-Inhalt zur
Ansicht zu bringen – um daraus dann die fehlenden Daten wiederzugewinnen und
einen neuen Formulararchiv-Eintrag zu erstellen, der wieder den Archiv-Eintrag
referenziert.
Als Funktion stehen
Bearbeiten
F5
und
Löschen
F7
zur Verfügung.
Mit
F7
löschen Sie den Archiv-Eintrag endgültig. Mit
F5
und anschließendem
Speichern
F9
können Sie einen rudimentären
Formulararchiv-Eintrag neuerstellen. Notwendig dafür ist aber mindestens die
Angabe einer Kundennummer bzw. Archiv-Referenz statt. Eine Mimetyp-Analyse
findet nicht statt, Sie müssen ihn bei Abweichung von PDF-Dateien selber
angeben.
Dies ist also eine sehr technische Angelegenheit und
im Normalfall sicher nicht Tagesgeschäft. Aber wenn der Fall eintreten sollte,
ist es sicherlich eine gute Unterstützung – alles manuell zu machen ist sehr
anspruchsvoll.

---

## Archiv-Manager

Archiv-Manager
Hauptmenü
Administration
Archiv
Verwaltung
oder Direktsprung
[FAM]
Im Archiv-Manager werden alle Einstellungen, Optionen,
Parameter bezüglich des Archivs eingerichtet.
Felder
Lizenz
Information
Gibt
      an, ob eine Lizenz für das Archiv installiert ist.
Archivieren
Pflichtfeld
Schalter, ob eine Archivierung
      stattfinden soll.
Diese Möglichkeit ist sollte nur in
      Ausnahmefällen auf NEIN gestellt werden.
Ziel
Pflichtfeld
Referenz-ERP unterstützt ausschließlich
      die Archivierung in die Datenbank.
EXTERN
Information
Ist
      die Relation ARCHIV extern angeschlossen, wird hier die Information
      gegeben, welche System-Bindungen vorliegen.
Zusätzlich wird noch der aktuelle
      Status, ob die Relation ARCHIV zugreifbar ist,
      bekanntgegeben.
Bedeutung der technischen
      Information:
remote-server-name;db-name;owner;object-name
`#`
srvname/srvclass/srvinfo
Es
      sind zur administrativen Unterstützung folgende Funktionen in der
      Optionbox verfügbar gemacht worden:
•
Sybase
      Central
•
ODBC
      Administrator
Erinnerung/Hinweis: Windows
      unterscheidet beim Datenquellennamen (DSN) Groß-/Kleinschreibung. Außerdem
      sind externe Anbindungen in aller Regel Systemdatenquellen, also solche
      die via „System-DSN“ eingerichtet sind.
Funktionen
Archiv-Fakte
SF9
Siehe
Archiv2.docx#ueb_Archivfakte
Ansichten
F6
Siehe
Archiv Anichten
Recherche-Funktionen …
F5
Erlaubt das direkte Pflegen der
      Datenbank-Recherche-Funktion (Datenbank-Recherche)
ODBC-Administrator …
SF10
Ruft
      den
ODBC-Datenquellen-Administrator
Ihres Systems auf.
Externes Archiv
      abkoppeln
Diese Funktion ist nur dann
      erreichbar, wenn das Archiv extern angebunden wurde.
Sie
      können mit dieser Funktion die Relation „Archiv“ wieder intern herstellen.
Die Relation Archiv ist dann leer
, so dass ein bestehendes
      Formulararchiv keine Dokumente auf diesem Wege erreichen kann.
Registerkarten
Container
Einstellungen zu
[...]


---

## Archiv: Privater Import

Archiv: Privater Import
Im Gegensatz zur zentralen Eingangsarchivierung
besteht hier die Möglichkeit, eine dezentrale Eingangsarchivierung einzurichten.
Man verwendet dies gerne wenn abzusehen ist, dass der Mandantenserver nicht
zeitnah genug reagieren kann.
Um eine Ansicht für den dezentralen Einsatz
einzurichten, reicht Referenz-ERP-seitig allein die Einstellung „Aktiviert“ = JA
Referenz-ERP arbeitet an dieser Stelle sehr intensiv mit dem
zugrunde liegenden Windows-Betriebssystem zusammen und ermittelt automatisch die
Lage des Windows-Ordners „Eigene Bilder“.
In meinem Falle (Windows XP Professional) ist es
auf meinem Vista-System
Sollte man sich unsicher sein, wo sich dieser Bereich
auf seinem Computer befindet, gibt es noch die Möglichkeit Referenz-ERP zu
befragen.
Dafür wechselt man in Referenz-ERP in die Anwendung „VBA“
und führt dort
das Script „AMIC_FOLDER_SETZEN“ aus.
Über die Anwendung „JVARS“ kann man nun den Wert
ablesen
Nun ist verabredet, dass man in diesem Ordner einen
Ordner „Aeins“ anlegt.
Führt man nun eine solche Ansicht aus („Privater
Import“, Aktiviert = JA), dann durchsucht Referenz-ERP diesen Ordner bevor es die
anzuzeigenden Belege recherchiert und fügt die gefunden Dateien vorher ins
Archiv ein, so dass diese dann im Moment der Recherche im Archiv zur Verfügung
stehen.
Werden Dokumente per Scanner zugeführt, dann muss man
das entsprechende Scanner-Programm anweisen, die Dokumente im jeweiligen Bereich
des Systems abzulegen.
Für das „Microsoft Office Document Scanning“ sehe es
exemplarisch so aus:
Scanner, die keine direkte Windows-Unterstützung
bieten, müssen entsprechend über die jeweilige Bedienungssoftware auf den
jeweiligen Ordner gelegt werden.
Bei Vista-Systemen wird das dortige
in zukünftigen Referenz-ERP-Versionen eine direkte
Unterstützung erfahren.
Vorerst lässt sich z.B.
C:\Users\ah\Documents\Scanned Documents\Documents im Bedienerstamm
hinterlegen.
Im Ansichts-Dialog lässt sich auch das Szenario
„Dezentraler Eingang von zentraler Ressource“
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

## Barcode/Bilderdruck-Druck: Weitere mögliche Vorgangs-Übergabe-Parameter

Barcode/Bilderdruck-Druck: Weitere mögliche Vorgangs-Übergabe-Parameter
Folgende Parameter können in der Form {...} als
Parameter an die dafür angepasste
private Prozedure
übergeben werden:
Parameter
Syntax
Typ
v_id
{v_id}
Zahl
wabewid
{wabewid}
Zahl
v_posizaehler
{v_posizaehler}
Zahl
DRUCKPARAM
{DRUCKPARAM}
Zeichenkette
Druckparameter
DEVICE
{DEVICE}
Zeichenkette
Druckerqueue
JVAR_BIN_PATH
{
      JVAR_BIN_PATH}
Zeichenkette
Pfad
      auf das Referenz-ERP-Bin-Verzeichnis
Instanz
{Instanz}
Zeichenkette
Eindeutige Kennung des zur Zeit
      aktiven Referenz-ERP.
DatenQuelle
{datenquelle}
Zeichenkette
Datenquelle des Drucks
Specials
{specials}
Zeichenkette
„Private“ Kennzeichen
Hinweis: Gross-Kleinschrift ist nicht relevant.
Erläuterungen zu “Specials”:
Die Methodik erlaubt es “private Daten” an die
private Prozedure
als Parameter gesammelt zu übergeben. Die “privaten
Daten” können über die JVars mit dem Owner
3568
von Vorläufen, Makros,
jegliche Makros im Formulardruck, Scripten, …bereitgestellt werden.  Neben
der eigentlichen Auswertung in der Datenbank-Prozedure sind Nutzer dieser
Möglichkeit auf für die Pflege der JVars 3568 verantwortlich, z.B. Abräumen.
Die Übergabe der Werte zu den Jvar berücksichtig
grundsätzlich die Möglichkeit in den Jvar „Stacks“ zu verwenden.
Das Beispiel wird demonstriert wie man auch nicht
alltägliche Jvar-Namen und „JVar-Stacks“ adressiert.
Folgende Beispiel-Vorbelegung in einem Makro-Auszug
sei gegeben:
// …
jvarsset( 3568 ,
"JVars Variablen
Key"
,
"JVars Variablen
Wert"
);
// …
Folgender Beispiel-Aufruf sei im Dokument im „Barcode“
hinterlegt:
p_barcode_specials_beispiel('{specials}')
Beispiel für “Specials”
CREATE PROCEDURE
p_barcode_specials_beispiel ( IN in_specials long varchar )
Result
(
code long varchar,
codetype long varchar
)
Begin
declare dc_code long varchar;
CALL sp_parse_json( 'dc_specials', in_specials
);
set dc_code = dc_specials ."JVars Variablen
Key"[[1]];
IF dc_code != 'JVars Variablen Wert' THEN
CALL amic_exce
[...]


---

## Bedienerstamm

Bedienerst
amm
Hauptmenü
Administration
Firmenkonstanten
Bediener
oder Direktsprung
[BD]
In dieser Variante können Sie Referenz-ERP-Bediener
definieren.
Felder des Bedienerstamm:
Felder
Beschreibung
Kurzname
Benutzerkennung
Referenz-ERP Login
ID
Eindeutige Bediener-Id
KlNr
Bedienerklasse
Mitglieder der
Controllerklasse
werden gelb
      hervorgehoben.
Bedienerklasse
Bezeichnung der
      Bedienerklasse
Name
Name
e-Mail
E-Mail-Adresse
KlAdmin
Bedienerklassenadministrator
Protokoll
Kennzeichen für
      Systemhinweise
Betrieb
Filialnummer
Mitglieder des aktuellen Mandanten
      werden grün hervorgehoben.
Bezeichnung
Bezeichnung des
      Betriebes
User
      in DB
Aktivitätskennzeichen des Users in
      der SQL-Anywhere Datenbank
Bei
      nicht-aktiven Bedienern wird der Kurzname rot hervorgehoben.
Sperre
Kennzeichen für logische
      Sperre
Verwendeter Name (Druck)
Angezeigter Name für externe
      Verwendung (z.B. Druck)
Windows Login Name
Name
      Sicherheit
Aktivierte „Name Sicherheiten“
      werden grün hervorgehoben.
Gelöscht
Kennzeichen für logische
      Löschung
Prüfer
Kennzeichen für Prüfangelegenheiten
      (z.B. Vieraugen-Prinzip)
Codepage
Selektionsmöglichkeit der Codepage
      des Bedieners.
Suchmöglichkeiten des Bedienerstamm:
Suchen
Beschreibung
Status
nach
      Kennzeichen für logische Löschung
-
Aktiv
-
Inaktiv
-
Gelöscht
-
Neu
Bedienerklasse
von
      … bis …
Kurzname
%
Bediener-Id
von
      … bis …
Betrieb/Filiale
von
      … bis …
Funktionen des Bedienerstamm:
Es stehen folgende Funktionen zur Verfügung:
Funktionen
Beschreibung
Ändern
(F5),
Ansehen
(F6),
Neu
(F8)
Ruft
      dem
Pfleger
des Bedieners
      auf.
Abgleichen mit Systemtabelle
(Shift + F10)
Replikation
Abgleich Systemtabelle
SysRemoteUser
mit Bedienerstamm/Filialstamm mit
      Bestätigungsabfrage
Fremdserver Rechte zuordnen
(Shift + F9)
Externes Login der Bediener
      überarbeiten
Bediener clonen…
Vervielfältigt ausgewählte Bediener
      (
Bediener clonen
)

---

## Behandlungsschema Lagernummernänderung

Behandlungsschema
Lagernummernänderung
Administration
Formulare/Abläufe
Behandlungsschema
Mit dem Direktsprung
[BEH]
Behandlungsschema können Sie den
Behandlungsschemapfleger aufrufen. Es wird eine Standardbehandlung ausgeliefert,
die Sie für Ihre Anwendung modifiziert ablegen können.
Administration
Formulare/Abläufe
Formularzuordnung/Vorgangsunterklasse
Welches Behandlungsschema für welche
Vorgangsunterklasse verwendet wird, legen Sie in der Formularzuordnung
[FRZ]
auf der Registerkarte Abwicklung fest.
Das Behandlungsschema gibt Ihnen die Möglichkeit,
bestimmte Vorgehensweisen bei der Lagernummernänderung auszuschließen, Meldungen
ein- oder auszuschalten und eine Behandlungsvorgabe für bestimmte Fälle
vorzugeben.
Da ein Behandlungsschema unter Umständen auch von
einem Makro aufgerufen wird, ist es stets möglich, Meldungen abzuschalten.
Behandlungsschemakriterien
Kriterium
Werte
Verfahrensweise
Artikelfindung
•
Identische
      Artikelnummer suchen – Verwenden Sie diese Option, wenn Sie in allen
      Lägern die gleichen Artikelnummern verwenden.
•
Identische
      Artikelnummer + Lagerstamm verproben – Wir empfehlen diese Option, wenn
      Sie in allen Lägern identische Artikelnummern verwenden und diese den
      gleichen Lagerstammeintrag haben
•
Über den
      Artikelstamm suchen – Verwenden Sie diese Option, wenn Sie
      unterschiedliche Artikelnummern pro Lager verwenden, die jedoch einen
      gemeinsamen Artikelstamm verwenden. Voraussetzung ist jedoch, dass zu
      einem Artikelstamm nur ein Eintrag pro Lager existiert.
Auf
      welche Weise sollen Artikel im neuen Lager gefunden werden
Kontraktbehandlung
Beibehalten/Entfernen mit und ohne
      Warnung
Sie
      bestimmen hier, ob ein ausgewählter Kontrakt beibehalten werden soll, wenn
      es möglich ist (Lagerspezifische Kontrakte werden entfernt) oder Kontrakte
      grundsätzlich beim Lagernummernwechsel entfernt werden.
Ungültige/abgewählte Kontrakte neu
      finden
Ja/N
[...]


---

## Behandlungsschema

Behandlungsschema
Administration
Formulare/Abläufe
Behandlungsschema
Mit dem Direktsprung
[BEH]
Behandlungsschema können Sie den
Behandlungsschemapfleger aufrufen. Es wird eine Standardbehandlung ausgeliefert,
die Sie für Ihre Anwendung modifiziert ablegen können.
Administration
Formulare/Abläufe
Formularzuordnung/Vorgangsunterklasse
Welches Behandlungsschema für welche
Vorgangsunterklasse verwendet wird, legen Sie in der Formularzuordnung
[FRZ]
auf der Registerkarte Abwicklung fest.
Das Behandlungsschema gibt Ihnen die Möglichkeit,
bestimmte Vorgehensweisen bei der Kundennummernänderung auszuschließen,
Meldungen ein- oder auszuschalten und eine Behandlungsvorgabe für bestimmte
Fälle vorzugeben.
Da ein Behandlungsschema unter Umständen auch von
einem Makro aufgerufen wird, ist es stets möglich, Meldungen abzuschalten.
Behandlungsschemakriterien
Kriterium
Werte
Verfahrensweise
Beteiligung von
      Kontrakten
Weiter oder Abbruch je mit oder ohne
      Meldung
Sie
      können hier grundsätzlich die Kundennummernänderung bei Beteiligung von
      Kontrakten verbieten oder zumindest zur Meldung bringen
Kundenwechsel unter Kunden gleicher
      Kontraktgruppe
Weiter oder Abbruch je mit oder ohne
      Meldung
Sie
      können hier grundsätzlich die Kundennummernänderung bei Beteiligung von
      Kontrakten verbieten oder nur zur Meldung bringen, wenn es sich im Kunden
      mit gleicher Kontraktgruppe handelt.
Kundenwechsel unter Kunden
      ungleicher Kontraktgruppe
Kontrakt entfernen oder Abbruch je
      mit oder ohne Meldung
Sie
      können hier bestimmen, ob ein Kontrakt im Fall ungleicher Kontraktgruppen
      der Kunden abgewählt wird, oder in diesem Fall der Kundenwechsel verboten
      ist.
Kontraktneufindung
      starten
Ja/Nein
Wird
      aus der vorherigen Einstellung ein Kontrakt abgewählt, so kann er mit
      dieser Einstellung neu für den neuen Kunden vorbelegt werden, sofern ein
      Kontrakt vorhanden ist
Beteiligung von Pa
[...]


---

## Besonderheiten der Formulareinrichtung

Besonderheiten der Formulareinrichtung
Bei den in
[PROE]
wie auch im Rahmen der Stückliste
erzeugten Buchungen handelt es sich sowohl bei Produkten wie Komponenten um
Artikelpositionen (Formularbereich 101). Um eine unterschiedliche Darstellung zu
erreichen, stelle man hier unterschiedliche Druckvarianten ein.
Hierzu mit
SF6
in die Variantenzuordnung

---

## ASCII Tabelle für WLAN Einrichtung

ASCII Tabelle für WLAN Einrichtung
Es kann sein, dass für die Einrichtung des WLAN eine
ASCII Code gebraucht wird, zum Eintragen der Verschlüsselung wird der hex Code
benutzt.
U
Dez:
85
Hex:
55
Okt:
125
;
Semikolon
Dez:
59
Hex:
3B
Okt:
73
Html: &semi;
dec  hex  char | dec  hex  char | dec  hex  char | dec  hex  char
---------------+----------------+----------------+---------------
000  00   NUL  | 032  20
    | 064  40   @    | 096  60   `
001  01   SOH  | 033  21   !    | 065  41   A    | 097  61   a
002  02   STX  | 034  22   "    | 066  42   B    | 098  62   b
003  03   ETX  | 035  23   #    | 067  43   C    | 099  63   c
004  04   EOT  | 036  24   $    | 068  44   D    | 100  64   d
005  05   ENQ  | 037  25   %    | 069  45   E    | 101  65   e
006  06   ACK  | 038  26   &    | 070  46   F    | 102  66   f
007  07   BEL  | 039  27   '    | 071  47   G    | 103  67   g
008  08   BS
  | 040  28   (    | 072  48   H    | 104  68   h
009  09   HT
  | 041  29   )    | 073  49   I    | 105  69   i
010  0A   LF
  | 042  2A   *    | 074  4A   J    | 106  6A   j
011  0B   VT
  | 043  2B   +    | 075  4B   K    | 107  6B   k
012  0C   FF
  | 044  2C   ,    | 076  4C   L    | 108  6C   l
013  0D   CR
  | 045  2D   -    | 077  4D   M    | 109  6D   m
014  0E   SO
  | 046  2E   .    | 078  4E   N    | 110  6E   n
015  0F   SI
  | 047  2F   /    | 079  4F   O    | 111  6F   o
016  10   DLE  | 048  30   0    | 080  50   P    | 112  70   p
017  11   DC1  | 049  31   1    | 081  51   Q    | 113  71   q
018  12   DC2  | 050  32   2    | 082  52   R    | 114  72   r
019  13   DC3  | 051  33   3    | 083  53   S    | 115  73   s
020  14   DC$  | 052  34   4    | 084  54   T    | 116  74   t
021  15   NAK  | 053  35   5    | 085  55   U    | 117  75   u
022  16   SYN  | 054  36   6    | 086  56   V    | 118  76   v
023  17   ETB  | 055  37   7    | 087  57   W    | 119  77   w
024  18   CAN  | 056  38   8    | 088  58   X    | 120  78   x
025  19   EM
  | 057  39   9
[...]


---

## Einrichterparameter im Scanner

Einrichterparameter im Scanner
Löschung von Nullmengen in Folgeaufträgen
Wird nach Kommissionierung mit dem Handscanner ein
Folgeauftrag erzeugt, so wurden bis jetzt die Nullmengen in den Folgeauftrag
geschrieben. Der Einrichterparameter gibt die Möglichkeit, dieses zu
unterbinden. Standardmäßig steht der Einrichterparameter auf
“Nein“
. Dieses bedeutet, dass die Nullmengen im
Folgeauftrag mit angezeigt werden. Wird der Einrichter auf
“Ja“
umgestellt, werden alle Warenpositionen mit
der Menge Null aus dem Folgeauftrag gelöscht.

---

## Private Prozeduren

Private Prozeduren
Eine Private Prozedur erhält diese Übergabe Parameter.
Der Kopf der Prozedur sieht so aus:
Create procedure
p_meine_procedure( in in_Aktionstyp
integer
,
in in_aktionswert
char
(255),
in in_ident
integer
,
in in_positionsIdent
integer
,
in in_scannernummer
char
(40),
in in_kommando_scanident
integer
,
in in_AnzahlImBlock
integer
,
in in_Blockzaehler
integer
,
in in_letzte_aktion
integer
,
in in_Aktionstext
char
(100),
in in_Kopftext1
char
(100),
in in_Kopftext2
char
(100),
in in_reaktionstyp
char
(5),
in in_lagernummer
integer
,
in in_bedienerid
integer
,
in in_protokoll
char
(100),
in in_feldid
integer
,
in in_scanident
integer
,
in in_klassnummer
integer
,
in in_nummer
integer
,
in in_testflag
integer
,
in in_diese_positionsnummer
integer
)
Parameter
Erklärung
in_Aktionstyp
Enthält dem von Scannerzurückgegeben
      AI Code
in_aktionswert
Enthält den gescannten
      Wert
in_ident
Enthält den Aktuellen Ident der
      Realtion DatenStromScanner
in_positionsident
in_scannernummer
Enthält die Aktuelle Scannernummer
      des Bearbeiters
in_kommando_scanident
in_kommando_scanident
in_AnzahlImBlock:
in_Blockzaehler:
in_letzte_aktion:
in_Aktionstext.
Enthält die erste Zeile die auf
      dem      Scannerdisplayangezeigt wird
in_Kopftext1:
Enthält die zweite Zeile die auf
      dem      Scannerdisplayangezeigt
      wird.
in_Kopftext2:
Enthält die dritte Zeile die auf
      dem      Scannerdisplayangezeigt wird
in_reaktionstyp
in_lagernummer:
Enthält die Lagernummer des
      Bedieners
in_bedienerid
Enthält die BedienerId des
      Bedieners
in_protokoll
in_feldid
in_scanident
in_klassnummer
Enthält die Klassennumer des
      Vorgangs
in_nummer
Enthält die Belegnummer
in_testflag
Tesflag
in_diese_positionsnummer
Enthält die Aktuelle Zeilennummer
      der Angezeigten Daten in der Anzeige des Scanners

---

## Einrichtung des Scanners an der Zentral-Datenbank

Einrichtung des Scanners an der
Zentral-Datenbank
Im Aeins System kann festgelegt werden, welche
Einleitungscodes welche Prozesse auslösen. Hier ist per Direktsprung [SCTCP] der
Bereich Scanner TCPIP anzuwählen. Innerhalb dieser Anwendung stehen acht
Varianten und fünf Anwendungen zur Verfügung.

---

## Schritt für Schritt Anleitung

Schritt für Schritt Anleitung
Im Folgenden wird Schritt für Schritt erklärt, wie man
eine Sanktionslistenprüfung in Referenz-ERP einrichtet.

---

## Schritt 2 Konfiguration

Schritt 2 Konfiguration
Schritt 2.1: Compliance im Vorgang
Mit dem Direktsprung
[FRZ]
gelangt man in die Vorgangsunterklassen
bzw. die Formularzuordnung. Hier kann man sich nun einen Vorgang aussuchen,
welcher die Compliance Abfrage tätigen soll (dies können auch mehrere Vorgänge
sein). Man wählt in der Auswahlliste den gewünschten Vorgang aus und bearbeitet
diesen mit
F5
oder
Bearbeiten
. Als nächstes wechselt man auf
das Register
„Zoll“
, und ändert das Feld
„Compliance prüfen“
mit
F3
auf
„Ja“
. Anschließend
speichert man mit
F9
den Datensatz
ab.
Schritt 2.2: Compliance manuell ausführen
Um eine Personen/Adressprüfung manuell auszuführen hat
man 2 Möglichkeiten:
1.
Im Kundenstamm: Direktsprung
[KU]
2.   Im
Lieferantenstamm: Direktsprung
[LF]
3.
Im Anschriftenstamm: Direktsprung
[Ansch]
(Das Ergebnis der
Prüfung hängt von dem SPA 1063 ab)
Diese 2 Stammdaten haben in ihrer jeweiligen
Auswahlliste die Funktion
„Verboslistenprüfung“
. Mit einem
Rechtsklick auf dem Datensatz befindet sich in der Funktionsliste der Reiter
„Verbotsliste“
und dort die genannte Funktion.
Führt man diese Funktion aus, so wird die Anfrage an
den Dienst von AEB manuell ausgeführt.
Die Funktion wird maßgeblich durch die Prozeduren des
SPA 1063 beeinflusst. Wenn das Ausführen nicht zum gewünschten Ergebnis führt,
muss eine Anpassung an der Prozedur vorgenommen werden.
Schritt 2.3: Ausnahmen hinzufügen
Um Daten der Ausnehmeregelung hinzuzzufügen (GoodGuy),
navigiert man in den Anschriftenstamm
[Ansch]
. Dort wählt man den Datensatz aus,
welcher als GoodGuy gelten soll und macht einen Rechtsklick. Anschließend, wie
in Schritt 2.2, wählt man in der Funktionsliste den Reiter
„Verbotsliste“
aus, um dort die Funktion
„Als GoodGuy
definieren“
auszuwählen. Danach öffnet sich eine Maske, in der man eine
Begründung für diesen Datensatz anlegt.
Am Ende mit
ESC
die Maske verlassen. Gespeichert wird
automatisch.

---

## Container

Container
Siehe auch:
Container einrichten
„Die Archivfunktion ist jetzt auf ein Containermodell
umgestellt worden. Ein Archiv kann aus beliebig vielen Containern bestehen, die
in schreibgeschützter Form zur Anzeige eingebunden sein müssen.“
Container
Pflichtfeld
Eindeutiger Name des
      Containers.
Container die keine
      Datenbank-Relationen im Aeins sind, dürfen nicht den Namen einer eben
      solchen haben.
Abstufung
Pflichtfeld
Die
      Abstufung impliziert ein Rangsystem und kann z.B. dazu verwendet werden,
      eine Recherche-Reihenfolge vorzugeben.
Status
Information
Im
      Falle von Datenbank-Relationen wird die momentane Verfügbarkeit
      ermittelt.
Verfügbarkeit
Information
Gibt
      Auskunft über den Status im Falle einer Datenbank-Relation.
Datenbank-Recherche
Optional
Anbindung einer privaten
      Datenbank-Funktion in der die Container-behandlung abgewickelt
      wird.
Hier
      ist z.B. frei definierbar, ob und wie die Namen der hinterlegten Container
      und Abstufungen behandelt werden.
Erste Schritte lassen sich mit Hilfe
      des Branchen-ERP-Templates „p_ArchivContainer“ erzielen; dieses wird über die
      Funktion „recherche-Funktion …“ bei leerem Datenbank-Recherche-Feld
      einmalig im System initiiert. Das Template ist als Vorschlag und erstes
      Grundgerüst für private Recherchen zu verstehen.
Die
      Datenbank-Recherche-Funktionen werden von Referenz-ERP im Rahmen der „Archiv
      anzeigen“-Funktionen aufgerufen, sobald Referenz-ERP mit internen Mitteln kein
      Dokument in der Relation Archiv finden kann. Archiv-Dokumente werden
      anhand ihrer GUID identifiziert. Die Rückgabe der Datenbank-Recherche muss
      die folgenden Felder enthalten:
archiv_status:0 = OK, 1=Information,
      2=Error, 3=keine Reaktion
archiv_blob: das recherchierte
      Dokument
archiv_message: ggf.
      User-Information, die via archiv_stati 2,3 zugestellt werden
      kann.

---

## Einrichten eines Containers

Einrichten eines Containers
1.
Backup der aktuellen Datenbank erzeugen.
2.
Das Backup auf dem Server ablegen, wo die Datenbank Zugriff hat.
3.
Das Programm „scjview.exe“ im Referenz-ERP-Verzeichnis „Aeins\bin64“ ausführen.
4.
An die DB anmelden.
5.
Ordner „Remote Servers“ auswählen.
6.
Im Popup-Menü den Eintrag „New“ -> „Remote Server“ wählen.
7.
Namen des Remoteservers angeben und Schaltfläche „Next >“ drücken
8.
Typ des Servers auswählen, hier „SQL Anywhere“ und Schaltfläche „Next >“
drücken.
9.
Verbindungs-Information für Datenbank-Verbindung erzeugen: „driver=sql anywhere
12;
eng=xxx;dbf=Pfad\DB.db; dbn=yyy;links=tcpip“ und Schaltfläche „Next >“
drücken.
•
Die Information „xxx“ und „yyy“ sind in den Systeminformationen [SYSIN]
im Feld „Verbindungsparameter“ zu finden.
•
Die Angabe „Pfad“ entspricht dem Verzeichnis aus Schritt 2.
•
Die Angabe „DB“ entspricht der Datenbankdatei aus Schritt 2.
10.  Den
im letzten Schritt erzeugte Verbindungsinformation in das Feld „Connection
Information“ eingeben und Schaltfläche „Next >“ drücken.
11.
Auswahlfeld „Make this remote server a read-only data source“ deaktivieren und
Schaltfläche
„Next >“ drücken.
12.
Auswahlfeld „Create an external login“ deaktivieren und Schaltfläche „Test
Connection“ drücken.
13.  Wenn
der Test fehlgeschlagen ist, wiederholen ab Schritt 5. Ansonsten Schaltfläche
„Next >“ drücken.
14.
Schaltfläche „Finish“ drücken.
15.  Bei
der Orginal-Datenbank die Tabelle Archiv leeren
(mittels OSQL-Befehl:
„truncate table archiv“).
16.
Prüfen, ob Dokumente im Archiv vorhanden sind.

---

## Einrichtung von Datalogic Scanner

Einrichtung von Datalogic Scanner
Tastatur
Öffnen
Um die Tastatur zu öffnen wird wie folgt
Vorgegangen.
1.
Klicken auf das Tastatur Symbol unten rechts auf der Taskleiste.
2.
Auf den Text Keyboard klicken. Jetzt öffnet sich das Input Panel
Schließen
Um die Tastatur zu schließen wird wie folgt
Vorgegangen.
1.
Klicken auf das Tastatur Symbol unten rechts auf der Taskleiste.
2.
Auf den Text Hide Input Panel klicken. Jetzt schließt sich das Input Panel

---

## Datenlöschung

Datenlöschung
Die Datenlöschung bietet als externes Programm die
Möglichkeit, schnell und einfach überflüssige Daten aus einer Aeins-Datenbank zu
entfernen.
Das Programm ist im bin-Verzeichnis unter dem Namen
„Referenz-ERP.Datenloeschung.exe“ zu finden.
Für dieses Programm ist eine Lizenz erforderlich.
Hinweise:
-     Die betroffenen Daten werden unwiderruflich gelöscht
und können auf normalen Wege nicht wiederhergestellt
werden.
Aus diesem Grund empfiehlt es sich vor einer
Löschung ein Backup von der Datenbank zu erstellen.
-
Die Löschung von Daten reicht allein nicht aus, um den verbrauchten
Speicherplatz einer Datenbank zu verringern.
Um dies zu erreichen ist die
Ent- und Beladung der Datenbank nach der Löschung notwendig.

---

## Automatische Löschung

Automatische Löschung
Neben den Parametern zur Verbindung mit der Datenbank,
kann ein weiterer hinzugefügt werden, um die Löschung zu automatisieren. Dieser
sieht wie folgt aus:
Profil=profil-ID
Dieses Profil kann in der Tabelle
Datenloeschung_Profile erstellt und angepasst werden. Dabei gibt es folgende
Spalten:
Spaltenname
Beschreibung
Dl_Profil_Id
Ist
      der Identifikator und muss im Startparameter angegeben werden.
Dl_LoescheBis
Gibt
      das Jahr an, bis zu welchem gelöscht werden soll.
Dl_LoeschZeit
Entspricht dem Timer in Minuten, wie
      lang dieser Löschprozess andauern soll.
Dl_LogVerzeichnis
Beinhaltet den Dateipfad, in welchem
      die Logdateien gespeichert werden sollen.
Ist
      der angegebene Pfad nicht vorhanden, so wird dieser automatisch
      angelegt.
Dl_ArchivTabelle
Falls eine der Kategorien Archiv,
      Archivanhänge, oder Formulararchiv ausgewählt ist, wird der Name dieser
      Tabelle hier verlangt.
Dl_Cb_**
Diese Felder entsprechen den
      Kategorien in der Anwendung. Wenn eine Kategorie gelöscht werden soll,
      wird in das jeweilige Feld eine 1 eingetragen, ansonsten bleibt es leer
      bzw. mit 0 gefüllt.
Falls ungültige Daten, wie unmögliche Jahre oder
falsche Archivtabellen, angegeben wurden, wird die Löschung nicht gestartet.

---

## Automatische Verbindung mit einer Datenbank

Automatische Verbindung mit einer Datenbank
Statt sich jedes Mal manuell mit einer Datenbank zu
verbinden, können auch Startparameter benutzt werden, um diesen Schritt zu
überspringen. Dabei müssen folgende Werte in beliebiger Reihenfolge angegeben
werden:
Benutzer=Benutzer Passwort=Passwort DBN=Datenbankname
ENG=Datenbank-Servername
Alternativ kann man auch nur einen Parameter zur
Datenbankverbindung nutzen:
Connectionstring=derConnectionstringZurDatenbank
Bei der Angabe von beiden Varianten, hat der
Controllstring als Datenbankquelle Vorrang.
Die Groß- und Kleinschreibung oder die Reihenfolge der
Parameter ist hierbei unerheblich. Wichtig ist die Rechtschreibung und das es
keine Leerzeichen innerhalb eines Parameters gibt (z.B. nicht „Benutzer
=  ich“).
Falls die automatische Verbindung fehlschlagen sollte, wird
darauf hingewiesen und es wird die Maske geöffnet zur manuellen Verbindung mit
der Datenbank
siehe Manuelle
Verbindung mit der Datenbank
.

---

## Manuelle Verbindung mit einer Datenbank

Manuelle Verbindung mit einer
Datenbank
Wenn die Datenlöschung ohne Startparameter ausgeführt
wird, öffnet sich eine Maske, in der die Verbindung zur Datenbank hergestellt
wird.
Hierbei ist der Datenbank-Servername gleichbedeutend
mit der ENG und der Datenbankname mit der DBN des Datenbankstrings.

---

## Default-Mandant

Default-Mandant
Damit auf Systemen mit Mandant-Herkunft „Sektion“ eine
Archivierung per Datenbank-Funktion amic_fa_set möglich ist, muss dem System
hier mitgeteilt werden, welcher Mandant in die Relation Formulararchiv
geschrieben wird.

---

## Die Übersicht

Die Übersicht
In der Anwendung „Formulararchiv Administration“ die
neue Variante „Archiv Auslagerung“. Dort wird eine jahrgangsweise Übersicht des
Archives präsentiert. Auf Systemen die mehrere Mandanten verwalten wird nochmals
nach Mandanten gegliedert.
Eine nicht ganz untypische Ansicht könnte sich in etwa
so darstellen:
Man sieht das Archiv dieser Datenbank hält die
entsprechende Anzahl von Belegen im jeweiligen Jahr mit entsprechenden Mandanten
vor – vorbehaltlich etwaiger schon getätigter Auslagerungen. Die schon
getätigten Auslagerungen erscheinen nicht mehr in dieser Statistik.
Um nun ein Jahr mit einem Mandanten auszulagern, wähle
man entsprechende Einträge an. Mehrfachselektion ist möglich und führe dann die
Funktion
Archiv auslagern
aus.
Führt man diese Funktion aus, legt der
Datenbank-Server unterhalb eines „Auslagerungspfades“ eine Archivauslagerung an.
Die Geschwindigkeit des Vorganges ist angemessen, bedenken Sie bitte dass je
nach Datenaufkommen einiges an Informationen transportiert werden muss.
Nach Durchführung wird die Übersicht aktualisiert und
es wurde eine Information ins Fehlerprotokoll von Referenz-ERP abgelegt.
Wechselt man z.B. mit dem Windows-Explorer in den
„Auslagerungspfad“ findet man eindeutige XML-Steuerdateien, deren Namen mit
Belegjahr_Mandant anfangen und Verzeichnisse die die Archivdaten enthalten.
In diesem Punkt ist die Auslagerung sehr stark
an den Archiv-Export angelehnt und kann auch als solcher verwendet
werden.
Darüber hinaus ist die Beleg-Recherche-Funktion von
Referenz-ERP so angepasst worden, dass sie im Falle, dass sich keine binäre
Beleg-Information mehr in der Datenbank befindet, Referenz-ERP nun versucht, diese
Information über obigen eingerichteten Auslagerungspfad zu ermitteln.
Die Auslagerungs-Funktion vermerkt den Export eines
Beleges in fa_progintern mit Wert -1.
Somit ist eine selektive Löschung der Relation Archiv
möglich, und die Datenbank kann nach einem „Rebuild“ wesentlich kleineren Umfang
aufweisen.

[...]


---

## Die Einrichtung

Die Einrichtung
Das Auslagerungssystem benötigt einen Dateibereich
(einen Pfad), in dem es ausgelagerte Archivinhalte ablegen kann. Dieser
Auslagerungspfad muss im Formulararchiv-Manager eingerichtet werden.
Beim „Auslagerungspfad“ ist durch die
System-Administration sicherzustellen, dass der Pfad auch durch den
Datenbank-Server erreichbar ist. In aller Regel werden hier „lokale“ Pfade des
Datenbank-Servers eingetragen werden. Beachten Sie, dass der Datenbank-Server in
sehr vielen Fällen als Windows-Service aktiv ist und Netzwerkzugriff für diesen
Service von der System-Administration gewährleistet werden muss. Eine Lösung
wäre eventuell – sofern nicht vorhanden – einen dedizierten User mit
entsprechenden Rechten im Windows-System anzulegen und den Datenbank-Service
dessen Identität annehmen zu lassen.

---

## Die Unternehmensdaten einrichten/verwalten

Die Unternehmensdaten
einrichten/verwalten
Die Unternehmensdaten bilden die Basis der
Aktionärsverwaltung und ohne eingerichtete Daten sollte sie nicht verwendet
werden [siehe
Globale
Einstellungen
]. Die Basisdaten eines Aktienunternehmens sind das
Stammkapital, die Aktienanzahl und der Nominalwert einer einzelnen Aktie. Als
Weiteres gehört zu einem Unternehmensdatensatz ein Datum, ab wann die Daten
gelten sollen („Aktiv Ab“), ein Beschlussdatum, wann diese Unternehmensdaten
beschlossen wurden und ein Dividendenkonto von dem die Buchungen der Dividenden
für die Aktionäre abgehen[siehe
Dividenden
abrechnen
]. Die Unternehmensdaten können in jeder Liste in der
Aktionärsverwaltung unter der Funktion
Unternehmen verwalten
SF5
eingerichtet werden. Nach Aufruf dieser
Funktion öffnet sich die Unternehmensdaten-Maske [siehe unten].
In einer Tabelle sind die bisherigen Unternehmensdaten
chronologisch dargestellt. Angewählte Datensätze können in den Editierfeldern
oberhalb der Tabelle geändert werden. Der erste Datensatz ist automatisch
angewählt. Durch Anwahl einer leeren Zeile oder mit der Funktion
Neu
F8
werden die Editierfelder geleert und es
kann ein neuer Unternehmensdatensatz eingetragen werden. Mit der Funktion
Speichern
F9
werden die eingegebenen oder geänderten
Daten gespeichert. Durch die Funktion
Löschen
F7
wird der gewählte Datensatz gelöscht.
Unternehmensdaten, die schon für die Abrechnung einer Dividende für ein
Wirtschaftsjahr verwendet wurden, dürfen nicht gelöscht werden. Ebenso darf bei
diesen Unternehmensdaten nicht mehr das „Aktiv Ab“-Datum geändert werden.
Änderungen an anderen Werten werden bei bereits abgerechneten Dividenden nicht
berücksichtigt. Deshalb sollte auch bei jeder Änderung der Unternehmensdaten wie
zum Beispiel einer Kapitalerhöhung ein neuer Unternehmensdatensatz angelegt
werden.

---

## Seitenlayout

Seitenlayout
Seite einrichten:
Funktion
Beschreibung
Seitenränder
Öffnet die Einstellungen der
      Seitenränder
Ausrichtung
Hochvormat
Querformat
Größe
Ändert das Layout
      (Größenverhältnisse) des Dokumentes
Spalte & Umbrüche:
Funktion
Beschreibung
Spalten
Fügt
      Spalten in das Dokument ein
Umbrüche
Seite
Spalte
Textumbruch
Nächste Seite
Fortlaufend
Seitenrahmen & -hintergrund:
Funktion
Beschreibung
Seitenfarbe
Setzt die Hintergrundfarbe des
      Dokumentes
Rahmen
Setzt einen Rahmen auf der aktuellen
      Seiten
Rahmenfarbe
Setzt die Rahmenfarbe
Rahmenbreite
Setzt die Rahmenbreite

---

## Schritt für Schritt

Schritt für Schritt
Einrichten eines dynamischen QR-Codes / laden
eines Bildes:
Schritt 1: Private Prozedur
Je nach gewünschtem Ergebnis erstellt man sich über
[SQLPP]
->
Neu
(F8)
eine private Prozedur. Beispiele
hierfür sind zu finden unter „
Beispiele für den Bilddruck
“ und „
QR-Code Beispiele zum
dynamischen laden
“.
Schritt 2: Formulareinrichtung
Zuerst in den Formularstamm
[FRM]
und dort einen Datensatz auswählen
und
Ändern
(F5)
. Im Formularstamm Pfleger nun in den
Tab “
Formularbereiche
” wechseln. Hier einen Bereich auswählen (in dem die
Position 464 hinterlegt ist, z.B: 101) und diese
Position Bearbeiten
(F6)
. Hier die Position 464 hinzufügen. In
dem Positions Pfleger mit
(ESC)
abspeichern und dann im Formularstamm
Pfleger Speichern
(F9)
.
Schritt 3: Dokumenten Editor im Vorgang
Zuerst einen Vorgang erfassen
[REE]
und
dort einen Kunden auswählen. Nun in die
Positionen
(F5)
und
dort eine
Textzeile
(F8)
erfassen. In den Textzeilen ein
Dokument laden
(F9)
.
Schritt 4: Prozedur im Dokument hinterlegen
Im Dokumenten Editor auf den Tab „
Einfügen
“
wechseln. Hier die Funktion „
Stichcode
“ wählen und „
QR-Code
“
auswählen. Den QR-Code markieren und mit Rechtsklick
Formatieren
. In dem Pfleger des QR-Codes
auf den Tab „
Typ und Farbe
“ wechseln. Unter der Kategorie „
Typ
“ im
Feld Text, die aus Schritt 1 erstellte Prozedur hinterlegen.

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

## Druckereinrichtung

Druckereinrichtung
Hauptmenü
Administration
Drucker
Hier erfolgt die Einrichtung und Zuordnung von
Druckern. Referenz-ERP kann den Vorgangs­druck über ASCII oder Windows
Druckertreiber durchführen; entsprechende Eintra­gungen sind dann
vorzunehmen.

---

## Schachtverwendung beim Druck

Schachtverwendung beim Druck
Moderne Drucker haben unter Umständen mehrere
Papierzufuhreinrichtungen mit Vorratsbehältern für Papier. Diese sogenannten
Schächte können dafür verwendet werden, Papier mit unterschiedlichen Maßen,
Farben oder Vordrucken aufzunehmen.
Das kann hilfreich sein, wenn z.B. für das erste Blatt
ein Papier mit vorgedrucktem Briefkopf verwendet werden soll oder der Zweitdruck
mit einem andersfarbigen Papier gekennzeichnet werden soll.
Hardwarevoraussetzungen
Für die Verwendung von Schächten ist es zunächst
notwendig, dass der Drucker mehrere Schächte hat und diese sich über den
Druckertreiber gezielt ansteuern lassen.
Einrichtung im Druckerstamm
Im
Druckerstamm [DRST]
kann eingestellt werden, dass und welche Schächte verwendet werden sollen und
welcher Schacht verwendet werden soll, wenn keine der Steuerungen dies angibt.
Schachtdefinition im Formular
Im
Formular [FRM]
kann
festgelegt werden, ob ein bestimmter (von der Druckerstammeinstellung
abweichender) Schacht verwendet werden soll.
Es kann sogar definiert werden, dass die erste Seite
auf einem von den folgenden Seiten abweichenden Schacht gedruckt werden soll.
Vorgangsdruckklassen-Einstellungen
In der
Vorgangsdruckklasse [VRGD]
kann festgelegt
werden, ob ein bestimmter (von der Druckerstammeinstellung abweichender) Schacht
verwendet werden soll.
Es kann sogar definiert werden, dass die erste Seite
auf einem von den folgenden Seiten abweichenden Schacht gedruckt werden soll.
Das kann hilfreich sein, wenn für das erste Blatt ein Papier mit vorgedrucktem
Briefkopf verwendet werden soll.
Reihenfolge der Entscheidungsfindung bei
widersprüchlichen Einstellungen
Zunächst ist zwingend notwendig, dass im Druckerstamm
[DRST] Schächte definiert sind und ein Standardschacht angegeben wurde. Ohne
diese Einstellung gibt es keine Schachtverwendung!
•
Beim Druck wird zunächst die Einstellung im Formular [FRM] gelesen.
•
Anschließend wird - wenn anwendbar – die Schachteinstellung der
ver
[...]


---

## Druckumleitung

Druckumleitung
Hauptmenü
Administration
Drucker
Druckerumleitung
oder Direktsprung
[DRM]
Im Standardfall wird je Bediener und Arbeitsplatz die
Einrichtung der dort zu verwendenden Drucker ausreichen. Sollen Bediener aber
häufig von verschiedenen Plätzen arbeiten, kann das mit virtuellen Druckern
(direkte Ansprache einer Queue) erreicht werden, die mittels Bediener
spezifischen Umleitungen zugeordnet werden können.

---

## eBilanz-Online

eBilanz-Online
In Referenz-ERP wird die Lösung
eBilanz-Online
des
Bundesanzeiger Verlags zur Erfüllung der aktuellen steuerlichen und
handelsrechtlichen Vorgaben unterstützt. Nach Registrierung und Einrichtung
eines Mandanten auf eBilanz-Online können die Kontensalden bestehend aus
Kontonummer, Kontobezeichnung und Saldo an das Portal übermittelt
werden.

---

## Einrichtung auf eBilanz-Online

Einrichtung auf eBilanz-Online
Nachdem man sich auf
www.ebilanzonline.de
registriert hat,
steht einem das Benutzerhandbuch für eBilanz-Online zur Verfügung. Daher
erhalten sie hier nur eine kurze Aufstellung der einzelnen Schritte, die
Notwendig sind bis man die Kontensalden zu übertragen kann.
1)
Registrierung
Die Registrierung findet man oben rechts auf der
Internetseite von eBilanz-Online. Diese ist kostenfrei. Nach Erfassung der
Registrierungsdaten hat man automatisch auch den ersten Benutzer angelegt.
Zusätzlich können später auch weitere Benutzer zu diesem erfasst/registriert
werden. Alle Benutzer, die Kontosalden übertragen sollen,
•
dürfen nicht deaktiviert sein,
•
müssen die E-Mail-Adresse nach Registrierung bestätigt haben,
•
müssen über Lese-und Schreibrechte für die Bearbeitung verfügen, d.h. der
Benutzer ist entweder der Periodenmandant oder kann diesen administrieren.
Benutzer und Passwort werden
später von Referenz-ERP abgefragt, wenn die Kontensalden übertragen werden sollen.
2)
Anlage eines Vorgangs
Bei der Anlage
des Vorgangs handelt es sich um die ersten Angaben, die für die eBilanz
notwendig sind. Hierbei sind folgende Daten besonders Wichtig:
•
Name
des Mandanten. Er wird später in Referenz-ERP bei der Übertragung
der Kontosalden abgefragt.
Achtung:
Groß- und Kleinschreibung
beachten.
•
Beginn und Ende.
Dies ist der Zeitraum der an die Finanzverwaltung
übertragen/offengelegt wird. In Referenz-ERP wird später die Periode abgefragt, bis zu
der die Salden ermittelt werden sollen. Es muss daher Beginn mit dem Beginn des
in Referenz-ERP eingerichteten Wirtschaftsjahres und Ende mit dem Periodenende der in
Referenz-ERP ausgewählten Periode übereinstimmen.
•
Version.
Dies ist ein beliebiges Kennzeichen (z. B. "Erstabgabe",
"Korrekturmeldung", "Abgabe nach Betriebsprüfung"). Dadurch können
unterschiedliche Versionen der gleichen Periode angelegt und bearbeitet werden.
Es wird auch in Referenz-ERP benötigt, damit die Salden dem korrekten Bereich
zugeordnet werden könne
[...]


---

## Geräte einrichten

Geräte einrichten
Schritt 1: Schublade
Zuerst gibt man der Schublade eine Bezeichnung (z.B
„Schublade Kasse 1“). Danach wählt man den Anschlusstyp. Hier ist wichtig, dass
i.d.R die Schubladen über den Drucker angesteuert werden. Für so ein Setup wählt
im Feld Anschlusstp „am Drucker“ aus. Im Feld Anschkluss ist muss man nun den
Port eintragen, an welchen der Drucker hängt (z.B LPT/COM). Für die folgenden
Einstellungen muss man in er Bedienungsanleitung des jeweiligen Gerätes gucken,
welche Einstellungen richtig sind.Standard sind hier die Werte:
Baud: 9600, Parity: N, Data: 8, Stop: 1, Buffer
In/Out: 1024
Sollten diese Werte abweichen, müssen die
Einstellungen angepasst werden. Auch in Windows selbst können diese
Einstellungen getätigt werden. Dazu „Windowstaste + R“, in das Feld „cmd“
eingeben und die Windows Konsole starten. In der Konsole nun folgenden Befehl
eintragen:
MODE COM1
BAUD=9600 DATA=8 PARITY=N STOP=1
(Im Fall, dass LPT genutzt wird auch folgenden Befehl
ausführen)
MODE
LPT1=COM1
Für den Druckertyp wählt man nun (Ab Windows 7)
spziell aus. Mit F3 auf dem ID Feld wählt man den eingerichteten Drucker aus, an
dem die Schublade angschlossen ist. Als letztes trägt man die Steuersequenz ein.
Diese kann ebenfalls der Bedienungsanleitung entnommen werden.
Schritt 2: Kassendisplay
Zum einrichten des Kassen Displays muss zuerst der
Displaytyp in das Feld eingetragen werden. Hier kann man z.B den Names des
Herstelles o.ä eintragen. Als zweites muss die Steuersequenz eingetragen werden.
Diese Parameter findet man i.d.R in der Bedienungsanleitung. Für den
Anschlusstyp kann man wählen zwischen TCP/IP und Generic. Bei TCP/IP muss im
Feld Display-Device lediglich die IP Adresse des Displays angegeben werden. Bei
Generic muss man wie bei der Schublade Sowohl den Port angeben (z.B COM1), als
auch die dazugehörigen Parameter).
Schritt 3: EC Gerät
Vorraussetzung:
Die Vorrausetzung, um ein EC-Gerät in Referenz-ERP
einzubinden sind folgende:
-
Lan An
[...]


---

## Einrichtung von openTRANS für FiBu

Einrichtung von openTRANS für FiBu
Zinsabrechnungen in der Finanzbuchhaltung können für
Kunden, bei denen das openTRANS-Kennzeichen aktiviert ist, auch beim Drucken als
openTRANS übertragen werden.
Die Einrichtung setzt die Einrichtung von openTRANS
für Vorgänge voraus.
Steuerparameter
Administration
Steuerung
Steuerparameter anzeigen
•
Der Steuerparameter
Steuerparameter 721 – openTRANS
(Lizenz)
muss aktiviert sein, um diese Option zu nutzen.
•
Der Steuerparameter
840 - FiBu
Zinsbelege mit openTRANS drucken
muss aktiviert sein, um diese Option zu
nutzen.
•
Der Steuerparameter
841 -
FRZ-Unterklasse für FiBu-Zinsbelege
(Default ist 0) muss festlegen, aus
welcher Unterklasse der Rechnung (Vorgangsklasse700) der Export seine
Einstellungen übernehmen soll.
Sachkontenstamm
Finanzbuchhaltung
Stammdaten
Sachkonten
In der Finanzbuchhaltung gibt es verschiedene
Sachkonten, auf die Teile der Abrechnung gebucht werden. Die Verwendung dafür
kann z.B. sein:
•
Soll-Zinsen
•
Haben-Zinsen
•
Zinsabschlagsteuer
•
Solidarzuschlag
•
Kirchensteuer
•
Gebühren
Im
Sachkontenstamm
können Sie auf der
Registerkarte weitere Optionen eine Artikelnummer festlegen. Dieser „künstliche“
Artikel beschreibt die Art der Buchung in der Zinsabrechnung. Der Artikel darf
keine Steuern, Zu-/Abschläge o.ä. haben.
FiBu-openTRANS-Optionen
In der Formularzuordnung für die Vorgangsklassen
werden openTRANS-Export-Optionen eingegeben. Der Steuerparameter
841 - FRZ-Unterklasse für
FiBu-Zinsbelege
legt fest, welche Unterklasse der Vorgangsklasse 700
(Rechnung) diese Einstellungen enthalten soll.
Zur Beschreibung der Felder lesen Sie dazu bitte den
Abschnitt: Vorgangsabwicklung
Formularzuordnung [FRZ]
openTRANS.

---

## Einrichterparameter

Einrichterparameter

---

## Einrichterparameter (Pfleger)

Einrichterparameter (Pfleger)
In allen Funktionsmenüs steht die Funktion
Einrichterparameter
zur Verfügung. Auf
dieser sind drei Registerkarten zur Einrichtung der jeweils aktuellen Maske.
Parameter
Auf dieser Registerkarte werden alle Parameter der
aktuellen Maske angezeigt. Änderungen werden nur für die angezeigte
Bedienerklasse übernommen. Eine Übersicht alle Masken kann auf der Seite
Einrichterparameter
gefunden werden. Dort werden auch die Parameter der jeweiligen Maske
beschrieben.
Bedienerklassenzuordnung
Auf dieser Registerkarte können die Parameter für
andere Bedienerklassen übernommen werden. Um die Parameter für eine
Bedienerklasse zu übernehmen, muss in der jeweiligen Zeile die Spalte
„Übernehmen“ den Wert „Ja“ erhalten.
Um die Parameter für alle Bedienerklassen zu
übernehmen, kann man die Funktion „Alle Bedienerklassen markieren“ aus der
Optionbox auswählen. Damit wird für jede Bedienerklasse der Wert auf „Ja“
gestellt.
Nachdem die Auswahl für die entsprechenden
Bedienerklassen auf „Ja“ gestellt wurde, können die Parameter mit der Funktion
„Für Bedienerklasse übernehmen“ endgültig übernommen werden.
Felder
Beschreibung
Übernehmen
Legt
      fest ob die Parameter für die Bedienerklasse übernommen werden
      sollen.
Bedienerklasse
Zeigt die Nummer der Bedienerklasse
      an.
Bezeichnung
Zeigt die Bezeichnung der
      Bedienerklasse an.
Benutzer
Zeigt eine Liste der Benutzer der
      Bedienerklasse an. (Liste ist auf 255 Zeichen gekürzt)
Maskenfelder
Zuweilen sind Begriffe in Referenz-ERP je nach
Arbeitsbereich oder Einsatzort der Firma abweichend zu benennen. Hier können
Bezeichnungen von Feldern individualisiert werden.
In der Spalte „Standard Feldbezeichnung“ wird der
Originaltext angezeigt, in der Spalte „Eigene Feldbezeichnung“ kann eine
individuelle Bezeichnung angegeben werden. Diese ist dann Systemweit, also für
alle Anwender gültig.
Dynamisch generierte Felder wie UFLD-Felder oder
AIS-Felder können hier nicht abgeändert werde
[...]


---

## Einrichtung des Informationssystems

Einrichtung des Informationssystems
Nach Auswahl eines Artikels und Aufruf der Anwendung
Artikelinformation
F10
wird die Information entsprechend der
hinterlegten Einrichtung aufbereitet und dargestellt. Beim Erstaufruf erscheint
also ein leerer Bildschirm. Unten ist eine eingerichtete Seite dargestellt, die
nachfolgend als Einrichtungsbeispiel dienen soll.
Prinzipiell gilt folgendes festzuhalten:
Die Informationen werden auf (Informations-) Seiten
gespeichert. Einrichtungen gelten immer für diese Seite. Zwischen den Seiten
kann gewechselt werden. Bearbeitungsfunktionen dieser Seite werden in der Option
- Box oben rechts angezeigt (Seitenwechsel mit
F5
; Speichern erfasster Information mit
F9
; Aufruf des Texteditors mit
SF8
)

---

## Einrichtung von Nummernkreisen

Einrichtung von Nummernkreisen
Zur allgemeinen Einrichtung der Nummernkreise gehört
die Einrichtung von Nummernkreisen und ihren Zählkreisen. Anschließend können
die Nummernkreise verschiedenen Vorgängen oder Stammdaten zugeordnet werden. Bei
einer Neueinrichtung bzw. Erweiterung der Nummernkreise empfiehlt sich folgende
Einrichtungsreihenfolge:
Direktsprung
Beschreibung
[NKZ]
Unter
[NKZ]
können Zählkreise gepflegt
      werden.
[NKS]
Unter
[NKS]
gibt es die
      Möglichkeit Nummernkreise zu pflegen. Hier können Zählkreise über einen
      Gültigkeitszeitraum zu einem Nummernkreis zugeordnet werden. Außerdem
      können hier neue Zählkreise angelegt werden.
[NKV]
Vorgangszuordnung
[NKF]
Unter
[NKF]
werden Nummernkreise zu
      FiBu-Vorgängen zugeordnet (siehe
Nummernkreiszuordnung
      Finanzbuchhaltung
).
[MND]
und
[MNDNK]
Festlegung der Nummernkreise bei
      Personenkonten im Mandantenstamm
Nummernkreis
Hauptmenü
Administration
Nummernkreise
Nummernkreise
oder Direktsprung
[NKS]
Kopfdaten
Feld
Beschreibung
Nummernkreis
Hier
      wird eine eindeutige Nummer für den Nummernkreis festgelegt. Neben der
      Nummer kann hier eine Bezeichnung für den Nummernkreis vergeben
      werden.
Gesperrt
Mit
      diesem Kennzeichen können Nummernkreise gesperrt werden. Aus gesperrten
      Nummernkreisen kann keine Nummer bereitgestellt werden.
Der
      Standardwert ist „Nein“.
Nur
      für Journal
Kennzeichen, ob es sich um ein
      Nummernkreis handelt, der nur für das Journal verwendet werden
      soll.
Der
      Standardwert ist „Nein“.
Nur
      für FiBu
Kennzeichen, ob es sich um ein
      Nummernkreis handelt, der nur für die FiBu verwendet werden
      soll.
Der
      Standardwert ist „Nein“.
Datentabelle
Über die Datentabelle können Zählkreise zu einen
Nummernkreis zugeordnet werden. Des Weiteren besteht die Möglichkeit hier direkt
neue Zählkreise anzulegen.
Einige Felder sind mit dem Hinweis „Eingabe ist nur
bei Neu-Anlage eines
[...]


---

## E-Mail Profil Verwaltung

E-Mail Profil Verwaltung
Direktsprung
[EMAIL]
Die Anwendung dient der Einrichtung und Pflege von
Profilen für die Anwendung E-Mail-Connector.

---

## Usage

Usage
Der Import wird über den Aufruf der Anwendung
EmailConnector.exe aus dem bin-Verzeichnis gestartet. Übergabeparameter sind ein
Connection-String und die Id des Profils.
Bsp.:
Referenz-ERP.EmailConnector.exe
connectionstring="eng=test;dbn=test;links=tcpip;uid=test;pwd=test"
id=2
Der Aufruf kann über die Windows-Aufgabenplanung in
regelmäßigen Abständen erfolgen.
Formulararchivgruppe
Die Mail und alle Anhänge werden im Formulararchiv in
einer Gruppe zusammengefasst. Anhand dieser kann man die Dokumente
zusammengehörenden Dokumente identifizieren.
Der Name der Gruppe ist ein vorangestelltes
„EmailConnector“ und eine GUID. Sie könnte wie folgt aussehen:
EmailConnector-{98cb6768-7fbd-477d-a4fa-1564fd46dc90}

---

## Erfasserstamm

Erfasserstamm
Hauptmenü
Administration
Firmenkonstanten
Erfasserstamm
oder Direktsprung
[ERF]
Zusätzlich zu Bedienern lassen sich Erfasser
einrichten. Im Gegensatz zu Bedienern können Erfasser ohne weiteres während des
Programmbetriebs gewechselt werden. Das kann vor allem im Kassenumfeld genutzt
werden, indem ein einzelner Kassen-Bediener als Sammel-Account genutzt wird und
die einzelnen Kassierer als Erfasser eingerichtet sind. Die Kassierer können
dann per
Erfasserwechsel
[ERFW]
/
[SERFW]
gewechselt werden.
Das Abmelden eines Erfassers fungiert gleichzeitig als
Sperrung von Referenz-ERP. Das Programm kann erst dann weiter benutzt werden, wenn
sich wieder ein Erfasser angemeldet hat.
Um sofort zu sehen, welcher Erfasser gerade angemeldet
ist, wird sein Kürzel neben dem Bedienerkürzel in der Titelzeile von Referenz-ERP
angezeigt. Die Erfasser-ID des aktuell angemeldeten Erfassers wird in der
LDB-Variable ERFASSERID gespeichert. Außerdem können Informationen zum
angemeldeten Erfasser über die Formularpositionen ID_ERFASSERID und
ID_ERFASSERKURZ abgerufen werden. Den Erfasser eines neuen Vorgangs erhält man
mit ID_ERFASSERNEU oder ID_NAMEERFASSERNEU. Sollten Vorgänge mit und ohne
Erfasser existieren, kann man die Formularpositionen
ID_ERFASSERNEU_ODER_BEDIENERNEU oder ID_NAME_ERFASSERNEU_ODER_BEDIENERNEU
verwenden. Wenn kein Erfasser bestimmt werden kann, zeigen diese Positionen die
Daten des Bedieners an, der den Vorgang erstellt hat. Bei allen Positionen, die
einen Namen ausgeben, wird der Parameter verarbeitet. Bei einer 0 wird der
Kurzname ausgegeben, sonst der volle Name.
Jedem Bediener müssen seine Erfasser explizit
zugewiesen werden. Diese Zuordnung kann entweder direkt im Erfasserstamm oder im
Register Erfasser
des Bedienerstamms
eingestellt werden. Dabei kann ein Erfasser aus mehreren Bedienern zugewiesen
werden. Zusätzlich kann im Bedienerstamm ein Standarderfasser eingestellt
werden, der beim Einloggen des Bedieners automatisch eingeloggt wird.

[...]


---

## Export einer Hedge-Order-Datei

Export einer Hedge-Order-Datei
Die Order-Datei wird in dem Verzeichnis erstellt, das
im
Einrichterparameter
eingetragen wird. Wurde kein Pfad festgelegt, so wird der Pfad „..\user\“
relativ zur Referenz-ERP-Applikation verwendet.
Der Order-String wird von einer Datenbankfunktion
erstellt, die
Einrichterparameter
eingetragen wird. Wurde dieser Parameter nicht festgelegt, so wird
„AMIC_HEDGE_GETORDERSTRING“ verwendet.
Zusätzlich wird die Datei im Formulararchiv mit der
Referenz auf diesen Kontrakt archiviert.

---

## Firmenstamm

Firmenstamm
Hier finden sich Themen um Einrichtung und Pflege von
organisatorischen Daten einer Aeins-Installation.

---

## Formulararchiv-Administration

Formulararchiv-Administration
Hauptmenü
Administration
Archiv
Administration
Formulararchiv-Administration
Direktsprung
[FAAD]
Folgende Punkte sind besonders hervorzuheben:
•
Diese Variante dient der allgemeinen Archiv-Recherche und bietet u.a.
Zugang auf den technischen Schlüssel des Formulararchivs ID
(
fa_id
), der bei bestimmten Fragestellungen im technischen Umfeld
des Archives sehr oft von Interesse ist.
•
Weiterhin steht in dieser Anwendung/Variante das Löschen von
Archiv-Einträgen zur Verfügung.
•
Gibt es in dieser Anwendung/Variante keine Abgrenzung durch das
Bedienerklassen-Sichtschutz-Konzept.
•
Stehen diverse Im- und Export-Funktionen zur Verfügung.
1
Funktionen der Variante
Funktionen
Referenzen anzeigen
Referenzen
      anzeigen
Löschen
F7
Löscht Archiv-Einträge.
Manager
F10
Archiv-Manager
Import
SF11
Archiv Import
Export
F11
Archivierung Datenbank –
      Export
Recherche
Recherche nach
      Referenznummern
Hinzufügen …
F8
Archiv – Dokumente
      hinzufügen
Barcode zuweisen
      …
SF8
Archiv Barcode
Referenzieren
Referenzieren
Drucken
Druckt Archiv-Einträge – insoweit
      das möglich ist.
Löschen
      rückgängig
SF7
Stellt gelöschte Archiv-Einträge
      wieder her.
Archiveinträge
      löschen
Volltext ansehen
Volltext
      Funktionen
Volltext
      aktualisieren
Volltext
      Funktionen
Volltext
      editieren
Volltext
      Funktionen
Volltext löschen
Volltext
      Funktionen

---

## Formulararchiv ( Belege ohne Basis )

Formulararchiv ( Belege ohne Basis )
Hauptmenü
Administration
Archiv
Administration
Formulararchiv ( Belege ohne Basis )
Direktsprung
[FAAD]
Diese Variante listet die Archiv-Belege für die es in
den
Archiv Fakt-Tabellen
keine Entsprechung bzgl. der Referenz gibt.
Da nicht jede Referenz eine Entsprechung in einer
Archiv-Fakt-Tabelle haben muss, lässt sich also nicht in jedem Falle von einem
„Überbleibsel“ ausgehen. Im Einzelfall kann es sich aber sehr wohl um eine
Information handeln, weswegen es auch diese Variante gibt.
Je nach Größe der zugrundeliegenden Archivs und
entsprechender Eingrenzung kann die Analyse der Referenzen einige Zeit in
Anspruch nehmen.
Folgende Möglichkeiten stehen auch hier zur Verfügung:
Funktionen der Variante.

---

## Formulararchiv ( Belege ohne Archiv )

Formulararchiv ( Belege ohne Archiv
)
Hauptmenü
Administration
Archiv
Administration
Formulararchiv ( Belege ohne Archiv )
Direktsprung
[FAAD]
In dieser Variante werden Archiv-Belege ohne
entsprechend auffindbares Dokument aufgelistet.
In System ohne
Container
– Anbindung ist das Indiz dafür dass die
Funktion
Archiv anzeigen
nicht
erfolgreich durchgeführt werden kann!
Bei Systemen mit Container-Anbindung erfolgt die
Beschaffung des Dokumentes über private Anpassungen. Es wird in solchen System
daher eher die Regel sein, das dann in dieser Variante mehr Einträge aufgelistet
werden.
Folgende Möglichkeiten stehen auch hier zur Verfügung:
Funktionen der Variante.

---

## Formulararchiv Gruppe

Formulararchiv Gruppe
Hauptmenü
Administration
Archiv
Administration
Formulararchiv Gruppe
Direktsprung
[FAAD]
Diese Variante hat zurzeit nur ausschließlich
informatorischen Charakter um Belange der Formulararchiv-Gruppen-Thematik
Für weitere führende Erläuterungen zu dem dortigen
Einsatz ist dann die entsprechende Dokumentation aufzusuchen.
Innerhalb der Formulararchiv-gruppen spielen folgende
Begrifflichkeiten eine Rolle:
2 Formulararchivgruppen-Begriffe
Begriffe
Gruppentyp
Abbildung des Anwenderformates
      „af_fa_gruppe“.
Diese bietet eine programmatische
      Klammerung von Archiv-Einträgen über die Belegreferenz hinaus und ist in
      einigen Referenz-ERP-Modulen im Einsatz.
Gruppentext
Ein
      bis zu 20 Zeichen langer Freitext.
Gruppennr
Eine
      Zahl
Sortierung
Sortierung

---

## Formularzuordnung

Formularzuordnung
Hauptmenü
Administration
Formulare / Abläufe
Formularzuordnung / Vorgangsunterklassen
Direktsprung
[FRZ]

---

## Formulare pflegen

Formulare pflegen
In diesen Dialog können alle Kassenformulare um
gesetzliche Informationen zur Kassenverordnung ergänzt werden.

---

## Datenbankfunktion für Gebindeparameter

Datenbankfunktion für
Gebindeparameter
Hier kann eine private Datenbankfunktion für die
Gebindeparameter eingetragen werden.
Die rechnet dann z.B. aus der Keimfähigkeit und dem
TausendKörnerGewicht aus wie viel schwerer ein Gebinde sein muss, damit man z.B.
tausend keimfähige Körner garantieren kann.
Parameter die unbedingt an diese Funktion übergeben
werden müssen sind
ArtikelId, MeNummer, LagerPlatzNummer, Menge. Wird mit
Partien gearbeitet, dann muss die temporäre Tabelle Temp_Partie_Uebergabe
genutzt werden. Hier muss für jeden Datensatz  die Menge entsprechend
angepasst werden. Wichtig ist dabei die Menge auf zwei Nachkommastellen zu
runden, sonst kann es zu Differenzen kommen. Zurückgegeben wird die Summe der
Menge über alle Partiedatensätze.
Wird ohne Partien gearbeitet reicht es wenn die
gerundete Gesamtmenge zurückgegeben wird.
Ein Beispiel findet man unter ‚Beispiele für
Datenbankfunktionen’
Die Software Company Branchen-ERP macht Ihnen gerne ein
Angebot für eine eigene Datenbankfunktion, speziell abgestimmt auf  Ihre
Bedürfnisse.
Man hat die Möglichkeit die private Datenbankfunktion
mit F3 auf dem Feld auszuwählen. Ist das Feld gefüllt erscheint in der Option
Box die Möglichkeit mit SHIFT+F7 die zu übergebenen Parameter an die Funktion
auszuwählen. Hier wird also festgelegt welche Informationen für die Funktion zur
weiteren Verarbeitung gebraucht werden. Da jeder Anwender andere Ansprüche hat
wurde hier die Möglichkeit geschaffen die Parameter variabel zu halten.
Beispiel hier

---

## Formulareinrichtung für den Kontraktdruck

Formulareinrichtung für den Kontraktdruck
Folgende Formulartypen sind derzeit innerhalb der
Kontraktverwaltung vorgesehen:
•
Kontrakt (auch Kontraktbestätigung genannt)
•
Kontrakt-Erledigungsschreiben
•
Kontrakt-Stornobeleg
•
Kontrakt-Erinnerung (oder -mahnung)
•
Andienung
•
Freistellung
•
Andienung und Freistellung zugleich
Momentan sind lediglich der Kontraktdruck, -erledigung
und -storno implementiert.
Des Weiteren sollte beachtet werden, dass der
Kontraktdruck auch an die „
Vorgangsdruckklassen
“ angeschlossen werden
kann.
Sinn der „Kontrakt-Varianten"
Da die optische Gestaltung eines Kontraktes nicht, wie
bei einem Vorgang, durch die Reihenfolge der Eingabe, sondern nach logischen
Gesichtspunkten gegliedert werden soll, muss dem System ebendiese Reihenfolge
mitgeteilt werden. Dies geschieht in der Kontrakt-Variante, der der Kontrakt
jeweils zu Druckzwecken zuzuordnen ist. Die Druckvariante steuert also nicht
nur, welche Formulareinrichtung verwendet werden soll, sondern auch die
Reihenfolge und den Umfang der „Bereiche", in die ein Kontrakt gegliedert werden
soll.
Innerhalb einer Kontrakt-Variante können folgende
Bereiche aktiviert werden:
•
Artikelposition (nur Artikeldaten mit Folgetextzeilen)
•
Artikel mit Mengenzeilen (je Artikel über alle Zeiträume)
•
Artikel mit Preiszeilen (je Artikel über alle Zeiträume)
•
Artikel mit Mengen- und Preiszeilen (jeweils je Artikel über alle
Zeiträume)
•
Abnahme- oder Mengenzeitraum (nur Gesamtmenge)
•
Abnahmezeitraum mit Artikelzeilen (je Zeitraum über alle Artikel)
•
Bepreisungszeitraum (nur Zeitraumgrenzen)
•
Bepreisungszeitraum mit Artikelzeilen (je Zeitraum über alle Artikel)
•
Abnahmekunden (nur bei Gruppenkontrakten sinnvoll)
•
Paritätsdaten
•
Zu-/Abschläge (noch nicht implementiert)
•
Kontraktpartien (noch nicht implementiert)
•
Bewegungszeile (z. B. für Erledigungsschreiben)
•
Festtext (Textbaustein)
•
Zahlungsbedingungen
•
Leerzeile
Folgende Formularbereiche (Direktsprung
[FRMB]
) können in der Formul
[...]


---

## Formate

Formate
Hauptmenü
Administration
Steuerung
Benutzer Feldsteuerung
Direktsprung
[FORMA]
In Referenz-ERP gibt es an vielen Stellen
Entscheidungsfelder, deren Wert sich aus einer vorgegebenen Liste auswählen
lässt. Diese Listen heißen in Referenz-ERP „FORMAT“. Oder „FSFormate“
In der Regel sind diese Listen in Form von
Systemformaten vorgegeben und für den Bediener nicht änderbar. Es gibt jedoch
zwei Formatgruppen, die auch oder ausschließlich vom Bediener gepflegt werden:
Benutzerformate und Anwendungsformate.
Systemformate
Diese Formate werden ausschließlich von der
Entwicklung erstellt und gepflegt.
Benutzerformate
Diese Formate werden ausschließlich in der
Installation lokal verwendet. Diese Formate werden zum Beispiel in AIS-Masken
verwendet. Die Inhalte dieser Formate werden vom Anwender bzw. Supporter
individuell eingetragen.
Die Namenskonvention gebietet hier den Präfix
„BF_“.
Anwendungsformate
Hier werden in der Regel einige Basiselemente der
Liste vorgegeben und deren Nummerierung ist bis zu einem bestimmten Wert für die
Verwendung den Entwicklern des Systems vorbehalten. Weitere Werte können
oberhalb des gesperrten Bereichs eingetragen werden.
Die Namenskonvention gebietet hier den Präfix
„AF_“.
Pfleger:
Bezeichnung
Inhalt
Eigentümer
Systemformat, Benutzerformat oder
      Anwendungsformat
Formatname
Name
      des Formats
Bezeichnung
Hinweis für den Verwender des
      Formats
Nicht
      übersetzen
Wenn
      hier „Ja“ angegeben wird, der Text dieses Formates nicht durch
      Übersetzungen überschrieben.
Nummern
      reservieren bis
Wird
      nur von Entwicklern von Anwendungsformaten angezeigt, um festzulegen,
      welche Nummern für die Entwicklung reserviert bleiben sollen.
Nr
Interne Nummer z.B. einer
      Enumeration (c#Enum)
Textersetzung
Dargestellter Text für diesen
      Wert
Kommentar,
      Schnipsel
Wird
      dieses Format in einem Auswahllistenfilter verwendet, so muss hier ein
      Schnipsel hinterlegt werden, der besti
[...]


---

## Funktion Staaten einspielen F10 (nur für Systemadministratoren)

Funktion Staaten einspielen F10 (nur für Systemadministratoren)
Die Funktion
Staaten einspielen
ergänzt Staaten in der
Relation Staatstamm mit Hilfe der Relation
Amic
_
Staatstamm
, die von
Amic
mit ausgeliefert wird.
Die
Funktion wird nur ausgeführt, wenn im Staatstamm für alle Staaten das Feld
ISO-Code gefüllt ist. Falls nicht erscheint eine Meldung, dass die Daten
zunächst gepflegt werden müssen. Es werden nur Staaten aus
Amic_Staatstamm
in den Staatstamm
übertragen deren ISO-Code noch nicht im Staatstamm vorkommt.
Existiert ein ISO-Code dort noch nicht wird geprüft,
ob es die Staatnummer schon gibt. Falls ja, wird eine neue Nummer vergeben.
Danach wird noch überprüft, ob der Inhalt des Feldes StaatPostKurz noch nicht
existiert, da auf dem Feld ein ‚unique index‘ liegt. Ist dies der Fall, dann
wird der Datensatz aus
Amic_Staatstamm
in Staatstamm
übernommen, falls nicht, dann erhält der Anwender eine Meldung, dass der
Datensatz nicht übernommen werden kann.
Nach dem Durchlauf aller Datensätze erhält der
Anwender eine Meldung, dass die Verarbeitung abgeschlossen ist.

---

## Globale Einstellungen

Globale Einstellungen
Für die Aktionärsverwaltung gibt es einen globalen
Steuerparameter, der das Verhalten bei nicht eingerichteten Unternehmensdaten
steuert und der in bekannter Weise unter dem Direktsprung
[SPA]
gepflegt werden kann:
•
Nichteinger. Unternehmen bei Aktien (607)
o
Fehler(Standard) – In der
Aktionärsverwaltung kann keine Funktion verwendet, die Unternehmensdaten
benötig. Es wird eine Fehlermeldung ausgegeben.
o
Warnung – Falls keine
Unternehmensdaten eingerichtet sind, erfolgt eine Warnmeldung mit einer Abfrage,
ob man mit der Aktion fortfahren möchte.
o
Ignorieren – Die
Aktionärsverwaltung kann ohne Meldung soweit verwendet werden, bis
Unternehmensdaten notwendig sind.

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

## Hinweise zum Hilfesystem

Hinweise zum Hilfesystem
Referenz-ERP öffnet bei Betätigen der F1-Taste die
Aeins-Hilfe.
Das Referenz-ERP-Arbeitstationssetup richtet standardmäßig
das Szenario „Standard“ ein.
Mögliche Szenarien
Bin-Verzeichnis
Referenz-ERP sucht im Bin-Verzeichnis nach
      der Datei
aeins.chm
und öffnet diese zur Ansicht.
Standard
Wird
      in dem durch Windows vorgesehenen Ordner für „C
ommonProgramFiles“
(*) und
      dort im Ordner Aeins eine Datei
aeins.chm
gefunden, so präferiert
      Referenz-ERP diese.
(*)
      der Ordner kann von Rechner zu Rechner anders lauten; ist abhängig vom
      Betriebssystem und etwaigen Updates der Systeme.
Weitere Programmunterstützung bzw.
      Hinweise sind unter Besondere Systemordner verfügbar.
Online
Durch den Steuerparameter 921
      („Onlinehilfe“) kann konfiguriert werden das die Referenz-ERP-Onlinehilfe unter
www.Branchen-ERP Hilfe
verwendet
      wird.
Die
      Szenarien „Standard“ und „Lokal“ sind nicht aktiv, wenn die Online-Hilfe
      aktiviert ist.

---

## Einrichtung der Inventur in Referenz-ERP

Einrichtung der Inventur in Referenz-ERP
Hauptmenü
Inventur
Grundsätzliches zur
Inventur
.
Als erstes muss die zu erfassende Inventur in Referenz-ERP
geöffnet werden.
Damit die Inventur richtig durchgeführt werden kann
müssen zwei Steuerparameter gesetzt werden und eine Zuordnung der ScannerID zu
einem Bediener hergestellt werden.
Es werden die Steuerparameter 809 und 810
ausgewertet.
Mit dem Steuerparameter 809 kann dem Scanner eine
Inventurgruppe zugeordnet werden. Wird keine Inventurgruppe zugeordnet so wird
die Inventurgruppe 0 als Standard gewählt.
Mit dem Steuerparameter 810 kann ausgewählt werden, in
welche Tabelle die erfassten Daten gespeichert werden sollen
1.
Nur MDEUebergabe
2.
MDEUebergabe und Inventurbeleg
3.
Inventurbeleg
Sollen die Daten in MDEUebergabe und Inventurbeleg
gespeichert werden, so werden alle Datensätze die in der Tabelle Inventurbeleg
geschrieben worden sind in der Tabelle MDEUebergabe als verarbeitet dargestellt.
Datensätze die einen Fehler erzeugt haben und nicht in
Inventurbeleg gelandet sind, können aus MDEUebergabe in die Inventur übertragen
werden.
Sollen die Daten nur im Inventurbeleg gespeichert
werden, werden fehlerhafte Datensätze in die Tabelle MDEUebergabe
geschrieben.
Die ScannerIP Adresse des Scanners wird im
Bedienerstamm im Feld
Name Extern
hinterlegt. Dadurch kann einem Scanner
ein Bediener zugwiesen werden.
Des Weiteren wird beim Einspielen der Daten die
Lagernummer aus [VKONS] des jeweiligen Bedieners gelesen. Dies bedeutet, dass
beim Lagerwechsel während der Inventur die Lagernummer unter VKONS neu für den
Bediener eingestellt werden muss.

---

## Tab individuelle Preise

Tab individuelle Preise
Allgemeine Hinweise zum Aufruf und zur Arbeitsweise
des Moduls sind
hier
zu finden.
Die Sortierung der Tabelle lässt sich in den
Einrichterparametern hinterlegen. Einige Felder müssen für das gleiche Gültig-Ab
Datum identisch sein. In diesen Fällen kann das Feld nur in der Zeile mit Menge
0 gepflegt werden. Die anderen Zeilen werden bei einer Änderung automatisch mit
angepasst.
Spalte
Erklärung
gültig ab
Gültig-Ab Datum des
      Indivivdualpreises. Sollte das aktuelle Datum in mehr als einem Zeitraum
      enthalten sein, wird immer der Preis mit dem größten Gültig-Ab Datum
      herangezogen.
Die
      Vorbelegung lässt sich in den Einrichterparametern pflegen. Entfernt man
      das Datum kommt eine Abfrage, ob alle Einträge mit diesem Ab-Datum
      entfernt werden sollen. Bei Bestätigung werden die Zeilen entfernt.
      Gelöscht werden sie aber erst beim Speichern.
bis
Gültig-Bis Datum des
      Individualpreises. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein. Die Vorbelegung lässt sich in den Einrichterparametern
      pflegen.
ab
      Menge
Menge ab der der Individualpreis
      gezogen wird. Es muss immer ein Eintrag mit Menge 0
      existieren.
ME-Nr. / ME
Mengeneinheitsnummer und Bezeichnung
      der ab-Menge. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein.
Preis
Individualpreis
pro
      Menge
Für
      diese Menge gilt der Preis. z.B. letzte Zeile 504€ pro 3kg des
      Artikels
ME-Nr. / ME
Mengeneinheitsnummer und Bezeichnung
      der pro-Menge. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein.
Brut
      (Brutto)
Es
      handelt sich um einen Bruttopreis. Das Feld kann nur für den ersten
      Eintrag eines Preiszeitraums – gekennzeichnet durch „ab Menge“ 0,00 –
      geändert werden. Es wird dann für den gesamten Zeitraum
      geändert.
Steuergruppe/Steuergruppenbezeichnung
Bei
      einem Bruttopreis k
[...]


---

## Interne und externe Anbindung des Imports

Interne und externe Anbindung des Imports
Die Import-Funktionalität steht selbstverständlich als
JPP-Objekt zur Verfügung.
JPP-Objekt:
•
JFA_Import
Methode:
•
Free_Import
Parameter:
•
fai_id
die Ident(!) des Imports , zwingend erforderlich
•
fai_pfad
optionale Überschreibung des Import-Pfades
•
receiver
optionale Angabe Mail-Empfänger (notwendiger Spezialfall)
Damit ist es insbesondere skriptfähig und steht intern
allen Anwender-Sprachen JPL, VBA und Makro zur Verfügung, extern findet es ohne
weitere Verwendung über das Referenz-ERP-COM-Objekt.

---

## TSE-Setup Schritt 1 Setup

TSE-Setup Schritt 1 Setup
Schritt 1.1: TSE als Laufwerk
Um die TSE einzurichten, muss diese entweder bereits
in dem Rechner eingesteckt sein, oder im Netzwerk
eingebunden
werden.
Schritt 1.2: TSE im Netzwerkrechner einrichten
(Man kann diesen Schritt überspringen, wenn die TSE
über USB an Ihrem physischen Rechner angeschlossen ist)
Um die TSE als Netzwerklaufwerk einzurichten, muss man
dies in Windows zuerst konfigurieren.
1.
Zuerst das USB-Laufwerk am Netzwerkrechner freigeben.
2.
Dafür am Netzwerkrechner in den Explorer navigieren und links an der Seite auf
Dieser PC
klicken.
3.
Die TSE auswählen und darauf rechtsklicken.
4.
Unter
Eigenschaften
im Register
Freigabe
auf
Erweiterte Freigabe
klicken.
5.
Diesen Ordner freigeben
aktivieren.
6.
Den Freigabenamen mit
TSE
benennen.
7.
Die
Zugelassene Benutzeranzahl
auf
1
setzen.
8.
Die Berechtigungen konfigurieren und gibt den Vollzugriff freigeben.
9.
Alle Einstellungen übernehmen.
Schritt 1.3: TSE im Rechner über Netzwerk
einrichten.
(Man kann diesen Schritt überspringen, wenn die TSE
über USB an Ihrem physischen Rechner angeschlossen ist)
Um die TSE als Netzwerklaufwerk einzurichten, muss man
dies in Windows zuerst konfigurieren.
1.
Den Windows Explorer öffnen.
2.
Links an der Seite auf
Dieser PC
rechtsklicken
3.
Auf
Netzwerklaufwerk verbinden
klicken.
Das Einrichtungsfenster
öffnet sich.
4.
Im Einrichtungsfenster den Laufwerksbuchstaben auswählen.
5.
In dem Textfeld
Ordner
nun in
folgender Codierung den Netzwerkpfad eingeben:
„\\
*die IP des Rechners
mit der TSE (z. B 192.168.2.66) *
\TSE“
.
6.
Verbindung bei Anmeldung
wiederherstellen
aktivieren, falls deaktiviert.
7.
Auf
Fertig stellen
klicken.
Weiter
zu Schritt 2

---

## Kassensicherungsverordnung Einrichtung

Kassensicherungsverordnung
Einrichtung
Hauptmenü
Barvorgänge
Stammdaten
Kassensicherungsverordnung Einrichtung
Dieser Dialog pflegt Einrichtungsdaten der
Kassensicherungsverordnung in Referenz-ERP.
Dies ist genauer eine Spezialisierung des
Steuerparameter-Pflegesystems in Referenz-ERP.
Der Steuerparameter
1056
(Kassensicherungsverordnung) in der
Gruppe
53
(Kasse / Barverkauf) ist
der Steuerparameter (SPA) der die Einrichtungsparameter vorhält.
Die
Einrichtungsparameter sind:
1.
TSE-relevante Daten
2.
Kassenbarcode-Ermittlungsprozeduren
3.
TSE-Kommunikationsprozeduren
Kopfdaten
Feld
Beschreibung
Steuerparameter
Nummer des SPA
Name
      des SPA
SPA-Gruppe
Nummer der SPA-Gruppe
Name
      der SPA-Gruppe
Lizenz
Nummer der Lizenz
Name
      der Lizenz
Register Prozeduren
Feld
Beschreibung
Gültig ab
Datum ab wann diese Steuerparameter,
      also die Kassensicherungsverordnungs-Einrichtungen, gültig
      sind
Kassenbarcode
Der
      Name der Prozedure, die die Daten für den Kassenbarcode
      liefert.
Get
      Finish
Der
      Name der Prozedure für den Get / Finish
Get
      Start
Der
      Name der Prozedure für den Get / Start
Set
      Finish
Der
      Name der Prozedure für den Set / Finish
Set
      Start
Der
      Name der Prozedure für den Set / Start
Bon-UStId
Ergibt sich aus den
      Anwendungsfunktionen unter
[Forma]
- Variante 2:
      Anwendungsfunktionen -
AF_KSV_UsId.
Hier können die
      Parameter angepasst werden.
Funktionen
Funktionen
Beschreibung
Neu
(F7)
Setzt ein neues Datum ab dem dieser
      Steuerparameter (SPA) aktiv ist.
Löschen
(F8)
Löscht den Eintrag des aktuellen
      Steuerparameter (SPA).
TSE
      pflegen
(F10)
Ruft
      die
Auswahlliste
mit
      allen eingerichteten TSE auf.
Formulare pflegen
Ruft
      die Maske zum
Formulare
      pflegen
auf.
Aufbereitungsstatus ändern
(F3)
Ändert das Feld in eine private
      Variante.
Aufbereitungsprozedur ändern
(F5)
Bearbeitet die private
      Variante.

---

## TSE-Setup Schritt 2 Konfiguration

TSE-Setup Schritt 2 Konfiguration
Schritt 2.1: TSE in Referenz-ERP konfigurieren
Zu Hauptmenü
Barvorgänge
Stammdaten
Kassensicherungsverordnung Einrichtung navigieren.
Hier wird eingestellt, ab wann die Prozedur aktiv
werden soll.
1.
Dafür mit
F3
in die jeweilige
Prozedur.
2.
Im Datumsfeld das passende Datum auswählen.
Schritt 2.2: TSE hinzufügen
Um die TSE in Referenz-ERP einzupflegen, wie folgt
vorgehen:
1.
Auf
TSE pflegen (F10)
klicken, um in
die Auswahlliste der TSE zu gelangen.
ODER:
Zu Hauptmenü
Barvorgänge
TSE Pflegen navigieren.
ODER
: Direktsprung
[TSE]
wählen.
2.
Um die TSE hinzuzufügen, entweder auf
Neu
oder
F8
klicken.
Der Pfleger öffnet
sich.
Der große Vorteil an der TSE-Implementierung in Referenz-ERP ist, dass die
TSE (wenn sie in Windows richtig eingebunden wurde) direkt erkannt wird.
Für den Fall, dass Sie
mehrere TSE im Betrieb haben und nicht die Richtige erkannt wird, wechseln auf
ein anderes Laufwerk.
3.
Eine Bezeichnung für die TSE eintragen.
4.
Auf
Aktivieren!
klicken.
5.
Ein paar Sekunden warten.
Der Pfleger schließt sich
mit einer Meldung, dass die TSE erfolgreich eingerichtet wurde.
Schritt 2.3: TSE einer Kasse zuweisen
Um die TSE einer Kasse zuzuweisen, zu Hauptmenü
Barvorgänge
Kassenverwaltung navigieren.
1.
Die zu bearbeitende Kasse auswählen.
2.
Pfleger
mit
(F5)
öffnen.
3.
In dem Feld
TSE-Id
mit
F3
-Auswahl die eingerichtete TSE
auswählen.
Weiter
zu Schritt 3

---

## Kontraktauszug auf Lieferschein/Rechnung

Kontraktauszug auf Lieferschein/Rechnung
Formulareinrichter Bereich 90
Formulareinrichter Bereich 91

---

## Kontraktunterklassen

Kontraktunterklassen
Hauptmenü
Kontraktverwaltung
Kontraktunterklassen
oder Direktsprung
[KTUK]
Für Kontraktklassen lassen sich unterschiedliche
Unterklassen einrichten. Dies ermöglicht einer Kontraktklasse unterschiedliche
Druckformulare, eigene Nummernkreise und andere Vorbelegungen zu geben.

---

## Kostenobjekte: Einrichtung

Kostenobjekte: Einrichtung
Einrichtungsschritte
1.
Um das Kostenobjekt verwenden zu können, ist die
Kostenobjekt-Lizenz
notwendig.
2.
In der allgemeinen Nummernkreiszuordnung
[MNDNK]
können Kostenobjekte einem
Nummernkreis zugeordnet werden.
3.
Die Kostenobjekte müssen im
Stammdatenpfleger „Kostenobjekte“
angelegt
werden.
4.
Im
Sachkontenstamm
[SKS]
kann in
den jeweiligen GuV-Konten im Feld „Sperre Kostenobjekt“ aus folgenden
Möglichkeiten gewählt werden:
•
Gesperrt:
Es wird
kein
Kostenobjekt abgefragt.
•
Kann:
Es
kann
ein Kostenobjekt eingeben werden.
•
Muss:
Es
muss
ein Kostenobjekt eingegeben werden.
•
Fest
Es
wird nur
das im Sachkontenstamm festgelegte Kostenobjekt
verwendet.
Im Feld „Kostenobjekt“
kann hier die Nummer eines Kostenobjektes eingegeben werden, das bei der
Belegerfassung automatisch vorgeschlagen wird.
5.
Damit auch Rechnungen aus der Warenwirtschaft beim Fibu -Übertrag automatisch in
die Kostenobjektrechnung eingetragen werden können, ist es nötig,
Kostenobjektgruppen
[KSOBG]
zu definieren, in denen die
Kostenobjekte des Artikels für Einkauf und Verkauf angegeben werden
können.
Diese werden dann im
Artikel
[AR]
über die Funktion
Kostenst./Statistik/Abteil
gepflegt. Wird
der Artikel im Vorgang angesprochen, so wird das entsprechende Kostenobjekt
bebucht.
6.
Im
Mandantenstamm
[MND]
sollte ein Fehlerkostenobjekt
eingerichtet werden. Dieses Kostenobjekt wird herangezogen, wenn zu einem
GuV-Konto versehentlich kein Kostenobjekt hinterlegt ist und die „Sperre
Kostenobjekt“ des angesprochenen Kontos nicht auf
Gesperrt
oder
Fest
steht.
Alternatives Label
In dem optionalen Parameter „Kostenobjekt_Label“
[OPT]
kann ein alternatives Label für das
Kostenobjekt eingetragen werden. Wird hier ein alternatives Label erfasst, so
wird in den Labeln der Masken anstelle „Kostenobjekt“ der in den Optionen
eingetragene Wert angezeigt. Das gleiche gilt für die Spaltenüberschriften in
den Auswahllisten. Hiervon ausgenommen sind die Be
[...]


---

## Kundenmapping

Kundenmapping
Wenn der Steuerparameter
938 – Lizenz openTRANS Vorgangsimport
eingeschaltet ist,
so ist dieser Tabreiter zu sehen.
Beim Vorgangsimport wird ein Kundenmapping verwendet.
So kann übersetzt werden, wenn die Gegenstelle, die hier als aktueller Kunde
geöffnet ist, eine Kundennummer in seiner Notation verwendet, welche eigene
Kundennummer im eigenen System gemeint ist. So können z.B. Logistik-Vorgänge
abgewickelt werden.

---

## Laborverfahren

Laborverfahren
Hauptmenü
Saatzucht
Saatenlabor
Verfahren
oder Direktsprung
[LABVE]
In diesem Stammdatenpfleger werden die Daten über
Laborverfahren gepflegt. Der Einrichterparameter „
Erweiterte Einstellungen
“ erlaubt weitere
Eingabemöglichkeiten auf der Maske.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
Verfahrensnummer
Eindeutige Nummer des
      Laborverfahrens.
Detailprüfung
Art
      des Verfahrens. Eine Auswahl der möglichen Verfahren ist mit F3 möglich.
      Bei Eingabe des Verfahrens wird die Karteikarte (Registerkarte des
      Pflegers für Labordaten) gleich korrekt vorbelegt.
Bezeichnung
Bezeichnung des Verfahrens. Dies
      wird als Überschrift der Box auf dem Pfleger der Labordaten
      verwendet.
Felder auf der Register
karte Allgemein
Name
Erweitere
Einstellung
Bedeutung
Druckoptionen
Ja
Hier
      werden Etikettennamen, die über den
Branchen-ERP-Etikettendruck
definiert werden müssen, und die
      Anzahl der Kopien eingetragen, die für dieses Verfahren gedruckt werden
      sollen. Der Druck dieser Etiketten geschieht in der Anwendung Labor über
      die Funktion „Drucke Untersuchungsetiketten“.
Im
      Referenz-ERP-System existieren keine Standardvorlagen für die Etiketten. Diese
      müssen vor Ort entwickelt werden. Um die Daten zu identifizieren wird die
      aktuelle Qualitaetsid vor dem Aufrufen des jeweiligen Etikettes der
      Variable „LDB_TRANSFER$I4“ zugewiesen. LDB_TRANSFER$N0 wird die Nummer des
      Verfahrens zugewiesen. Diese Variable kann dann beim Branchen-ERP Etikettendruck
      verwendet werden.
Beispiel(siehe Prozedur
      Name):
Die
      Prüfberichte werden in der Tabelle „Verfahrenetiketten“
      gespeichert.
Verfahrens Prozedur
Nein
Hier
      kann der Name einer zu hinterlegenden Prozedur angegeben
      werden.
Kartenbezeichnung
Die
      hier eingegebene Bezeichnung wird der Titel der Registerkarte.
Kurzbezeichnung
Die
      Kurze Bezeichnung d
[...]


---

## Lieferscheinnummer

Lieferscheinnummer
Ist der Steuerparameter
826 – Liefernummer auf Position eingeben
eingeschaltet
und das
Eingabefeld in der
Formularzuordnung
freigeschaltet, so kann auf der Warenposition ab Stufe Rechnung eine
Lieferscheinnummer manuell erfasst werden.
Es erfolgt keine Prüfung der Lieferscheinnummer auf
Plausibilität oder Existenz.

---

## Anwendung von LokalitätenGruppe

Anwendung von
LokalitätenGruppe
Eine Gruppe von Lokalitäten fasst Lokalitäten
zusammen.
Das findet in erster Linie Anwendung bei Regalfächern,
die mehrere Regalplätze haben. Die Regalplätze werden als Lokalitäten
eingerichtet, die Gruppe fasst dieses Regalfach zusammen.
Die Einrichtung ist optional!
Anwendungsgebiet kann zum Beispiel die Belegung von
Lagerplätzen mit übergroßen Ladeträgern sein:
Angenommen, das Lagerfach umfasst 3 Palettenplätze für
EUR1-Paletten 80x120cm. Nun soll in eines der Fächer ein Ladeträger des Typs
EUR3 120x120cm eingelagert werden. Dadurch ist der daneben liegende Lagerplatz
belegt.
Das Anfahren von Regalplätzen, die teilweise von
nebenstehenden Paletten genutzt werden, ist nicht möglich.
Damit diese Regeln beachtet werden, müssen in den
Ladeträgertypen die Breiten ebenso gepflegt sein, wie die Breite der
Lokalitätsgruppe und die Gruppe und Index in den Lokalitäten.

---

## Gruppe

Gruppe
Legt die Gruppe der Lokalität fest – Diese Einrichtung
ist optional. Siehe auch
Anwendung von Lokalitätengruppen

---

## Gruppenindex

Gruppenindex
Legt die Position der Lokalität in der Gruppe fest.
Diese Einrichtung ist optional. Es dürfen mehrere Lokalitäten mit Index 0, aber
nur jeweils eine mit einem Index > 0 existieren.
Nur Indizes >1 haben einen Effekt auf die Belegung
mit Gruppen.
Siehe auch
Anwendung von
Lokalitätengruppen

---

## Mail an Bediener (mit Wiedervorlage)

Mail an Bediener (mit Wiedervorlage)
Hier hat man die Möglichkeit an einen Bediener aus der
Datenbank eine Mitteilung zu senden und einen Eintrag in die Wiedervorlage
vorzunehmen.
Der Einrichterparameter ‚Wiedervorlage Häkchen beim
Öffnen des Fensters angewählt‘ steht standardmäßig auf Nein.
Möchte man
erreichen, dass beim Öffnen des Fensters schon das Häkchen bei Wiedervorlage
gesetzt wird, dann kann man dies hier einstellen.
Für die Mitteilung trägt man im Feld An z.B. über die
F3
-Auswahl oder direkt mit dem Kürzel
den Bediener ein, an den die Mitteilung gehen soll.
Des Weiteren kann man
einen Betreff und eine Notiz eingeben. Wählt man dann die Funktion
Senden
wird eine Mail an den Empfänger
verschickt.
Ist zusätzlich der Haken bei Wiedervorlage gesetzt und
ein Datum eingetragen wird vor dem Senden der Mail auch ein Eintrag in die
Wiedervorlage
[WIEDV]
vorgenommen.
Für die Wiedervorlage sind folgende Felder zu
füllen:
Das Häkchen für Wiedervorlage muss gesetzt sein und
ein Datum kann angegeben werden.
Außerdem wird ein Text, der im Feld Betreff
steht mit in die Wiedervorlage
[WIEDV]
eingetragen.
Über die Funktion Wiedervorlage trägt man die Wiedervorlage
ein.

---

## Service Referenz-ERP Mailversand

Service Referenz-ERP Mailversand
Service einrichten für den Referenz-ERP
Mailversand
Mit Hilfe des Steuerparameters „SPA 1019 Mailversand
per“ kann der Mailversand über „Datenbank“ oder „Dienst oder Exe“ ausgewählt
werden. Zum Versenden der Emails per Service ist hier „Dienst oder Exe“
auszuwählen.
Um den Service zu installieren, öffnen Sie die
„Eingabeaufforderung(Administrator)“. Mit Hilfe der „InstallUtil.exe“ wird jetzt
der Service installiert.
Beispiel: <Pfad zu
InstallUtil.exe>InstallUtil.exe <Pfad zu
Referenz-ERP.MailSvc.exe>Referenz-ERP.MailSvc.exe
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe
C:\Aeins\bin64\Referenz-ERP.mailsvc.exe
Der Service wird jetzt installiert und Sie werden
aufgefordert den Benutzernamen und das zugehörige Passwort einzugeben, über den
der Service gestartet werden soll.
In der Registrierung muss der Eintrag des
Referenz-ERP.Mailservice erweitert werden.
Beispiel:
Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Referenz-ERP.MailService\
Wählen Sie „neu“ und selektieren Sie „Schlüssel“.
Name: Parameters
Im Schlüssel „Parameters“ wieder „neu“ auswählen und
dieses Mal „Zeichenfolge“ selektieren.
Name: Parameters
Als Wert wird hier der Startparameter für den Service
hinterlegt. Dieses kann sein die Datenbankverbindung gefolgt vom Sendeintervall
in Minuten oder eine Pfadangabe zur Datei „Referenz-ERP.MailService.ini“.
Beispiel:
Datenbankverbindung mit Sendeintervall von 1
Minute;
eng=entw;dbn=entw;links=tcpip; 1
Pfadangabe zur Datei:
@C:\Aeins\bin64\Referenz-ERP.MailService.ini

---

## Einrichtung Mailversand

Einrichtung Mailversand
Einrichtung
•
Steuerparameter
•
Versandprofilstamm
[VPST]
•
Versand
über DB-Server, Dienst oder Exe
•
Synchron
oder Asynchron
•
Dateiname im
Mailversand
•
FRZ-Einstellungen
Einrichtung Ware
•
VRGD-Einstellung
Mailversand

---

## Versand-Funktionen

Versand-Funktionen
Administration
Formulars / Abläufe
Formularzuordnung / Vorgangsunterklassen
Sind alle Kennzeichen korrekt eingerichtet, so wird
beim ersten Druck des für Versand gekennzeichneten Beleges, die in der
Formularzuordnung [FRZ] definierte Versandprozedur aufgerufen. Diese übernimmt
den Versand.
Sofortiger Versand
Späterer Versand
Die E-Mail wird umgehend beim Druck an das
      Versandsystem übergeben und zum Versand freigegeben
Die E-Mail wird erst einmal vorgesehen, kann
      noch einmal gelöscht und erst später zum Versand freigegeben werden.
Ware
AMIC_BELEGVERSAND_WARE_SOFORT
AMIC_BELEGVERSAND_WARE_SPAETER
Rohware
AMIC_BELEGVERSAND_ROHWARE_SPAETER
AMIC_BELEGVERSAND_ROHWARE_SPAETER
Definition Parameter
Definition Parameter
FA_ID
enthält die FormulararchivId des zu
      versendenden Belegs
FA_MNDNR
enthält die Mandantennummer im
      Mehrmandantsystem in Referenz-ERP.
FA_EMPFAENGER
enthält eine kommagetrennte Liste
      der Empfängernmailadressen
FA_HTMLBODY
enthält den aus Referenz-ERP erzeugten
      HTML-Body. Dieser wird im Mailtext verwendet.
SUBJECT
enthält den Betreff der
      Mail
VPST
enthält die Nummer des
      heranzuziehenden Versandprofilstamms [VPST]
ANHAENGE
enthält in XML-Notation eine Liste
      von FormulararchivIds, die als Anhänge mit gesendet werden
      sollen.
Hinweis: Hier ist ggf. auch die Liste der zugehörigen
      eRechnungen enthalten

---

## Steuerparameter

Steuerparameter
Der Steuerparameter
870 - Belegversand Lizenz
ist ein
Lizenz-Steuerparameter, welcher automatisch mit Erwerb der Belegversandlizenz
aktiviert wird. Dies ist die Grundvoraussetzung für den Belegversand!
Der Steuerparameter
860 - Belegkorrektur bei Belegversand
regelt, welche
Korrektursperre für Belege mit Belegversand gilt.
Der Steuerparameter
822 - Belegversand Dateiname Funktion
ist im Kapitel
Dateiname im Mailversand
beschrieben
Der Steuerparameter
888 - Belegversand Empfänger
legt fest, wie der
Mailempfänger aus der Ware ermittelt werden soll.
Der Steuerparameter
889 - Belegversand Ausgabeart
legt fest, ob der Versand
mit oder ohne Druck erfolgt.
Der Steuerparameter
890 - Belegversand Betreff
legt fest, wie die
Betreffzeile im Belegversand Ware ermittelt werden soll.
Der Steuerparameter
1019 – Datenbankserver per
legt fest, ob Mails von
Datenbankserver oder einem externen
Dienst
erledigt werden sollen.

---

## Mandanten übergreifend

Mandanten übergreifend
Dieses Feature wird
nicht länger unterstützt.
Hiermit bestimmen Sie, ob Ansichten
mandanten-übergreifend sein sollen. Dieses Kriterium spielt vornämlich bei den
Recherchen aus diversen Standard-Auswahllisten eine Rolle und verhindert einen
gewissen ungewollten „fremden“ Mandanteneinblick.
Für Standard-Installationen mit einem Mandanten
unerheblich.

---

## Mandantenstamm

Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
oder Direktsprung
[MND]
Hier erfolgen die Benennung des Mandanten (Bezeichnung
der Firma), seine datenbanktechnische Anbindung sowie die Zuordnung von
Nummernkreisen zu wesentlichen Datenbereichen.
Felder:
Feld
Bedeutung
Kurztext
Kurzbezeichnung des Mandanten
      (erscheint in der Windowskopfleiste) in der Datenbank = Basis
Nummer
Laufende Nummer des Mandanten
      (1)
Aktiv
0:
      Nein
1:
      Ja
Name
Bezeichnung der Firma
Buchwährung
Zeigt die aktive Buchwährung des
      Mandanten an. Solange noch keine Belege erfasst wurden, wird im Menü eine
      Funktion zum Setzen der Buchwährung angeboten.
Testmandant
Zeigt an, ob der aktuelle Datensatz
      ein Testmandant ist.
Register:
Registerkarte Allgemein
Für die allgemeinen Informationen stehen folgende
Felder zur Verfügung
Feld
Bedeutung
Technische Version
(Wird in
      Aeins nicht mehr benutzt)
Daten Version
Gibt
      Version der Daten an, mehr Einsicht über Direktsprung
[sysin]
Versionsdatum
Gibt
      Datum der Version an, mehr Einsicht über Direktsprung
[sysin]
Nachlaufprozedur
Optionale private parameterlose
      Daten-Prozedure, welche bei Update vom Referenz-ERP automatisch nachgezogen (zum
      Ende des Updates) aufgerufen wird.
Empfänger
Semikolon getrennte Liste der
      Empfänger-E-Mail-Adressen, die im Fehlerprotokollierungsfall eine E-Mail
      erhalten sollen.
Empfängerprozedur
Name
      der privaten Prozedur für die Auswahl von Empfängern in speziellen Fällen.
      Standard-SQL-Funktion ist hier „FehlerprotokollAbweichendeEmpfaenger“.
      Private Ableitungen bitte von dieser Funktion! ([SQLP])
Selektionsprozedur
Name
      der privaten Prozedur zur Eingrenzung der zu meldenden Fehlernummern.
      Standard-SQL-Funktion ist hier „FehlerprotokollMailselektion“. Private
      Ableitungen bitte von dieser Funktion! ([SQLP])
Sende ILN
Nummer die beim EDIFACT
      Datenaustausch eingesetzt wird
Terre
[...]


---

## Pfleger für das Mandantenprofil

Pfleger für das Mandantenprofil
Administration
Firmenkonstanten
Mandantenprofil
[MPR]
Im Mandantenprofilpfleger lassen sich Einstellungen
pflegen, die z.B. in Makros verwendet werden und im Test- und Livesystem
unterschiedlich sind. So könnten zum Beispiel Ablageorte für Reporte, Meldungen,
Ergebnisse oder Exporte für Live- und Testsystem unterschiedlich sein. Damit im
Makro nach der Erstellung eines Testmandanten keine Änderung gemacht werden
muss, muss dieses nur die Daten in der im Bereich
Testmandantenparameter
beschriebenen
Weise gelesen werden.
Feld
Beschreibung
Profil
Hier
      wählen Sie, ob der Wert im Livesystem oder im Testsystem gültig sein soll.
      Die Einstellung Branchen-ERP-Testmandant ist dem Support vorbehalten. Die
      Einstellung wird verwendet, um ein lokales Testsystem zu betreiben, das
      aus einem Testsystem kopiert wurde.
Name
Name
      des Parameters
Wert
Wert, der dem gewählten Parameter in
      der angegebenen Umgebung zugewiesen werden soll.

---

## Mandantherkunft

Mandantherkunft
Das Formulararchiv arbeitet mandantenbasiert. Hier hat
man nun die Möglichkeit den Mandanteneintrag im Formulararchiv auszuprägen.
•
Sektion: Der Name des „Mandanten“ beim Programm-Start, also in aller
Regel der Eintrag nach welcome: aeins.exe welcome mandantenname
•
Kurztext: Eben der Kurztext, somit in diesem Beispiel „EntwAhoi“
•
Nummer: Die obige Nummer, also in diesem Beispiel „5“

---

## Mandantenserver – Prozesse

Mandantenserver – Prozesse
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver Protokoll
Variante „Prozesse im Mandantenserver“
Direktsprung
[MSP]
Diese Maske dient zur Einrichtung der
Mandantenserverprozesse.
Bezeichnung
Inhalt
Name
Name
      des Prozesses
Control
Controlstring, der ausgeführt wird
      (bei Typ Synchron und Asynchron (einfach))
Async-Control
Controlstring, der im Fall eines
      einfachen Asynchronen Prozesses ausgeführt wird
Versteckt
Wenn
      hier „Ja“ steht, wird die Ausführung im Protokoll nicht
      angezeigt
Sekunden
Intervall in
      Sekunden
Aktiv
JA
      bedeutet aktiv. Ein Mandantenserverprozess, der auf aktiv geschaltet wird,
      wird erstmals nach einem Mandantenserverneustart
      ausgeführt.
Nur
      im Wartemodus
Ist
      hier „Ja“ eingetragen, hat der Prozess niedrige Priorität.
Er wird nur
      während einer Ruhephase des Mandantenservers in regelmäßigen Abständen
      ausgeführt.
Synchronität
1 –
      Synchron – Der Mandantenserver selbst führt den Prozess aus und blockiert
      für die Dauer des Prozesses weitere Buchungen. Diese Prozesse sollten nie
      lange dauern!
2-
      Asynchron (einfach) – Der Mandantenserver führt ein Referenz-ERP aus, das den
      Controlstring abarbeitet. Dieser Prozess wird nicht beaufsichtigt. Ist das
      Intervall kürzer als die Abarbeitungszeit können eine Reihe von parallelen
      Prozessen entstehen, die auch die Lebenszeit des Mandantenservers
      überschreiten.
3.
      Asynchron (managed) – Der Mandantenserver startet ein Referenz-ERP mit einer
      gegebenen Maske und den gegebenen Parametern.
ACHTUNG! Hier ist der
      Eintrag im Feld „Controlstring“ kein solcher!
Dieser Maskenprozess
      muss selbst in der Tabelle Mandserprozessliste seine letzte Aktivität
      nachtragen und prüfen, ob das Stop-Zeichen vom Mandantenserver gesetzt
      wurde.
Diese Prozesse sind Dauerläufer und
      werden nur einmalig gestartet. Im gegebenen Intervall w
[...]


---

## Bezahlung per EC-Karte

Bezahlung per EC-Karte
Die Zahlung mit EC-Karte kann auf verschiedenste
Weisen abgewickelt werden. Diese werden in der Konfiguration der Kasse
beschrieben.
•
Im Fall der Lastschrift per Lastschriftformular und manueller Eingabe
werden Zusatzinformationen wie Kontonummer, Bankleitzahl, Bankname, Kundenname
etc. abgefragt. Es wird dann nach der Betragseingabe der Druck des
Lastschriftformulars ausgelöst.
•
Im Fall der Lastschrift per Lastschriftformular ohne Eingabe werden
Zusatzinformationen wie Kontonummer, Bankleitzahl, Bankname, Kundenname etc. aus
einer eingelesenen Karte genommen. Es wird dann nach der Betragseingabe der
Druck des Lastschriftformulars ausgelöst.
•
Im Fall der Zahlungskennzeichnung durch EC-Karte wird entweder eine
„Zahlung-Erfolgreich“-Abfrage oder der Aufruf der Bezahlterminal-Schnittstelle
ausgelöst.

---

## Gutschein-Zahlung

Gutschein-Zahlung
Für die Zahlung mit Gutschein kann die Abfrage
folgender Zusatzinformationen notwendig sein:
•
Gutscheinnummer
•
Bemerkungen
Welches der Felder abgefragt werden soll, kann im
Einrichterparameter (EPA) definiert werden.
Die Gutscheinzahlung erfolgt stets in Kassenwährung.
Der eingegebene Betrag wird in Kassenwährung verbucht. Es ist möglich, Tasten
einzurichten, die den Zahlbetrag mit einem bestimmten Betrag wie z.B. 5,10,20
oder 50 vorbelegen.
Es ist über den
Steuerparameter „Bei Gutscheinannahme Nummer verproben?“
einstellbar, ob die Gutscheinnummer verprobt werden soll.

---

## LVS / MDE-Workflow

LVS / MDE-Workflow
Hauptmenü
Stammdatenpflege
Lagerverwaltungssystem
XXXXXXXXXXXXXXXXXX
Direktsprung
[LVSWF]
Mit dem LVS-Workflow kann ein Arbeitsablauf
beschrieben werden, bei dem der Scanner Daten sammelt. Bedingung ist die
Einrichtung der Prozedur „AMIC_LVS_WORKFLOW_SCANNER“ im Steuerparameter
801 – private Scanenerprozedur
für die IP des Scanners.
Ausgehend vom Startzustand hat der Scanner den Status
„0“. In diesem Status kann ein Barcode gescannt werden. Diesen kategorisiert die
Prozedur „AMIC_LVS_GETSCANTYPE“ in eine Kategorie und schreibt Werte in die
Tabelle „TCPIP_SCANNER“.
Analog dazu kann in Steuerparameter
1029 – LVS Workflow Prozeduren
in der
Option „LVS-Kommandos“ eine private Workflow-Funktion hinterlegt werden, die
weitere Schlüsselwörter erkennt.
Wird also nun ein Kommandowort oder ein Zifferntyp
erkannt, so wird von der Prozedur ggf. der Wert in die Tabelle „TCPIP_SCANNER“
eingetragen und der Scantyp zurückgegeben.
So kann z.B. v#12345/500/0/2019 als der Ladeschein
12345 identifiziert werden. Der Scantyp ist „VORG“ und in „TCPIP_SCANNER“ steht
nun die V_NumNummer, die V_KlassNummer und die V_UKlassnummer und
Jahrnummer.
Es kann aber auch ein Kommandowort wie z.B.
„WARENEINGANENDE“ vom Scanner als solches erkennt werden.
Im Workflow wird nun für jeden Status der mögliche
Satz an Scantypes festgelegt und die Prozedur, die danach aufgerufen werden
soll.
So kann z.B. in Status 0 eine NVE (erkennbar an der
Länge 20, numerisch, beginnend mit der Ziffernfolge 00) eine
Informationsprozedur aufrufen.
Der Folgestatus bestimmt, welcher Status nach dem
Scannen dieses Typs gesetzt wird. So kann eine Reihenfolge der Eingabe
festgelegt werden.
Workflow Beispiel
WARENEINGANG – WARENBEWEGUNG – NVE +
    MENGE
Status
Sort
Feldtyp
Feldname
Feldbezeichnung
Prüf-u. Anzeigepr.
Folgest.
0
1
WARENEINGANG
<null>
<null>
P_WE
100
100
1
WARENBEWEGUNG
Letzter_Wert
Position
P_WE
100
100
2
NVE
Ladetraegernummer
Ladeträgernummer
P_WE
100
100
3
MENGE
Gewicht1
M
[...]


---

## Verfahrensanleitung

Verfahrensanleitung
Synchronisierung des
Datenbestandes
eines
Mehrmandantensystems im Bereich Saatgut
Voraussetzung:
Ein bestehendes lauffähiges Mehrmandantensystem.
Informationen zur Einrichtung eines
Mehrmandantensystems finden Sie gegebenenfalls in unserer Referenz-ERP Online-Hilfe
unter dem Punkt „
Mehrmandantensystem
mit zentralem Stamm
“.
Wir weisen Sie hier nochmal darauf hin, dass nur im
Hauptmandant eine Stammdatenpflege durchgeführt werden darf! Sämtliche
Datenbestände der Untermandanten werden vom Hauptmandanten überschrieben und
sind nicht wiederherstellbar! Um hier Probleme zu vermeiden sollten Sie in den
Stammdatenpflegern der Untermandaten, die entsprechenden Funktionalitäten
(„Löschen“, „Ändern“ und „Neu“) deaktivieren.
Vorgehensweise:
1.
Erstellung von Sicherungen („Backup“) der bestehenden Datenbanken sowohl vom
Hauptmandant als auch von den Untermandanten.
2.
Installieren des Referenz-ERP Updates und somit Umstellung der Teilnehmer im
Mehrmandantensystem (also Hauptmandant und Untermandanten) auf das neue
Datenmodell.
3.
Prüfen der bestehenden Konfiguration des Mehrmandantensystems auf den
beteiligten Systemen (Trigger usw.) nach dem Einspielen des Updates.
4.
In den Untermandanten
sämtliche Datenbestände aus den Tabellen
entfernen:
-
SaatFruchtArt
-
SaatFruchtSorte
-
SaatFruchtSorteAddon
-
SorteMaskeDaten
-
SaatFrSortPosit
-
SaatFrSortPositAddon
Dies erfolgt vorzugsweise
durch den Aufruf der SQL-Prozeduren
mms_
untermandant_loesche_saatgut
.sql
oder „per Hand“ durch den
SQL-Befehl
DELETE FROM
SAATFRUCHTART
In den der Tabelle
SaatFruchtArt untergeordneten Tabellen (siehe Auflistung oben) werden, durch die
in diesem Referenz-ERP Update zum Datenmodell hinzugefügten Fremdschlüsselbeziehungen
(„Foreign Keys“), automatisch alle Datenbestände aus den oben aufgelisteten
Tabellen gelöscht.
5.
Im Hauptmandant
ausführen der SQL-Prozedur
mms_matching_saatgut.sql
Hierdurch wird das
Verteilen via Mehrmandantensystem
[...]


---

## Checkliste

Checkliste
Wir fassen die Einrichtungsmaßnahmen nach erfolgtem
Update oder Einspielung des Nachhaltigkeitspatches in der empfohlenen
Bearbeitungsreihenfolge zusammen:
□  AF_NACHSTAT
□  AF_ZERTMETH
□  AF_NAHA_ZERT
□  AF_ZERTKATEG
□  SQLK_NACHALTIG: für Formulardruck
□  ggf. weitere SQLK für Bildschirmformulare,
Infofenster, etc.
□  Formulareinrichtungen Verkauf
□  Formulareinrichtungen Bildschirmformulare,
Erfassungseinrichtungen
□  Formulareinrichtungen Rohware, Selfbilling
□  Formulareinrichtungen Wiegescheine
□  Nachhaltigkeitsmenü->Mandantenstamm
□  Halterkonto Zertifikatstyp 5 (eigener Betrieb
als Kundenkonto)
□  Eigenes Zertifikat
□  Nummernkreis Massebilanz
□  Option NUMMERNKREIS_MASSEBILANZ
□  Ggf. FRZ-Verhalten bei ungültiger
Nachhaltigkeit
□  Nachhaltigkeitsmenü->Kunden/Zertifikate:
anliefernde Landwirte
□  Nachhaltigkeitsmenü->Kunden/Zertifikate:
zertifizierte Lieferanten
□  Nachhaltigkeitsmenü->Kunden/Zertifikate:
ggf. nachhaltig zu beliefernden Kunden
□
Nachhaltigkeitsmenü->Kunden/Nachhaltigkeit
□  Nachhaltigkeitsmenü->Nachhaltigkeitswerte
Tabellen anlegen
□
Nachhaltigkeitsmenü->Artikelstammübersicht
□  Artikelgewichte nachhaltiger Artikel
einrichten / überprüfen
□  Massebilanzen mit Artikelnummer + Nuts-Nummer
erstellen wie im Kunden/Zertifikate-Schritt

---

## Nummernkreis der exportierten Belege (Archiv)

Nummernkreis der exportierten Belege (Archiv)
Hier haben Sie die Möglichkeit, einen Nummernkreis für
die Benennung der exportierten Belege anzugeben.

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

## Optionale Parameter

Optionale Parameter
Hauptmenü
Administration
Steuerung
Optionen
oder Direktsprung
[OPT]
Hier befinden sich globale Einstellungen für
Referenz-ERP.

---

## Parameter

Parameter
Hier kann ein Parametername mit einem Wert belegt
werden, der zuvor im System-SQL oder im UserSQL verwendet wurde.

---

## Parameter der Gefahrgutabwicklung

Parameter der Gefahrgutabwicklung
Die für die Gefahrgutabwicklung erforderlichen
•
Gefahrgutklassen
[GFK]
•
Brandklassen
[GFBK]
•
Toxizitätsklassen
[GFTK]
können hier mit den gesetzlich vorgeschriebenen
Informationen angelegt werden.
Gefahrgutklasse
:
Toxizitätsklasse
:
Brandklasse
:
Diese Informationen werden bei Gefahrgutartikeln im
Artikelstamm ange­bun­den und ggf. dort noch mit weiteren Informationen
versehen. Für die Auswertungen ist zu­sätz­lich das Grundgewicht pro
Mengeneinheit im Artikelstamm erforderlich. Zusammen mit diesen
Infor­mationen erwachsen daraus folgende Möglichkeiten.

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

## Parameter Einstellungen in den Vorgangsunterklassen

Parameter Einstellungen in den Vorgangsunterklassen
Es gibt eine Reihe von Einstellungen, die jetzt nicht
mehr wie früher unter SPA vorgenommen werden, sondern speziell für
Vorgangsunterklassen hinterlegt werden.
HINWEIS: Man achte bitte darauf,
dass alle relevanten Unterklassen bezüglich ihrer Partieeinstellungen überprüft
werden.
Die genaue Erläuterung dazu finden Sie in dieser Hilfe
unter Vorgangsabwicklung, Formularzuordnung, Partie.

---

## Protokolleinrichtung im Archivimport

Protokolleinrichtung im Archivimport
Erzeugt Tätigkeitsberichte.
Möchte man die eben exportierten Belege wieder
importieren, dann stelle man als Import-Verzeichnis „..\export“ ein und im
Gegensatz zum Export erscheint aus historischen Gründen keine vorherige
Sicherheits-Abfrage und es erscheint nach kurzer Zeit der folgende
Tätigkeitsbericht.
Wie man unschwer erkennt, sind die Belege nun auch
erwartungsgemäß doppelt im Formulararchiv.
Einzig die Herkunft verrät bei diesen Belegen ihre
Herkunft aus externen Quellen; gemeint ist dann der Import.

---

## Registerkarte Vorgang

Registerkarte Vorgang
Bezeichnung
Bedeutung
Art
      der Vorgangserzeugung
Hier
      kann festgelegt werden was bei der Funktion
Vorgang erzeugen
ausgeführt werden
      soll.
0 =
      nicht aktiv / Einrichterparameter entscheidet
1 =
      Vorgangskopie
2 =
      Normalvorgang
Wählt man „nicht aktiv“, dann wird
      die Einstellung des Einrichterparameters
„
Teildisposition/Vorgangskopie aus
      Auftrag
“ überprüft. Diese kann Nein, Teildispo oder
      Vorgangskopie sein.
Für die
Vorgangskopie
muss auf dem Feld
      Kunde in der Waagenmaske über die
F3
-Auswahl ein Vorgang (z.B. ein
      Auftrag) ausgewählt worden sein, sonst tritt die normale Vorgangserzeugung
      in Kraft.
Druckkennzeichen bei
      Vorgangserzeugung setzen
wenn Archivierung aktiv
Default ist Ja.
Mit
      Hilfe dieses Feldes kann man bei aktivierter Archivierung' entscheiden, ob
      bei der Vorgangserzeugung in der Waage ein Druckkennzeichen für den
      Vorgang gesetzt wird (wenn sich im Archiv ein Dokument befindet). Will
      man dies abschalten wählt man in der Vorlage für dieses Feld Nein
      aus.
Zielbeleg gleiche
      Belegnr
Default ist Nein.
Hier kann man
      festlegen ob man für die Wiegung und den erzeugten Vorgang (z.B.
      Lieferschein) die gleiche Belegnummer verwenden möchte.
Beim Vorgang
      erzeugen und bei der Vorgangskopie wird dann die Belegnummer des
      Waagedatensatzes in den erzeugten Vorgang (z.B. Lieferschein)
      übertragen.
Wenn es die Belegnummer für den erzeugten Vorgang schon
      gibt, dann erscheint eine Fehlermeldung. Die Vorgangserzeugung wird
      abgebrochen.
Verhalten bei
      Vorgangstornierung
Kontrakt überziehen
Darf
      ein Kontrakt an der Waage überzogen werden.
Fremdkontrakt überziehen
Darf
      ein Fremdkontrakt an der Waage überzogen werden.
Kontraktprüfung bei Auftrag /
      Bestellung
Wird
      dieser Schalter auf „Ja“ gestellt, so wird die Kontraktprüfung
      ausgestellt. Der Ko
[...]


---

## Qualitätsmerkmale

Qualitätsmerkmale
Hauptmenü
Saatzucht
Saatenlabor
Qualitätsmerkmale
Direktsprung
[SAATR]
In diesem Stammdatenpfleger werden die
Qualitätsmerkmale gepflegt. Sie werden in
Laborverfahren
,
Labordaten
und
Fruchtarten
verwendet. Der Einrichterparameter „
Erweiterte Einstellungen
“
erlaubt weitere Eingabemöglichkeiten auf der Maske.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
Merkmalsnummer
Eindeutige Nummer des
      Merkmals.
Merkmalstyp
Hier
      wird der Typ des Merkmals angezeigt. Mit
F3
kann eine Auswahl
      getroffen werden. Zurzeit stehen folgende Typen zur Verfügung:
•
-

                  kein
      Typ
•
Fremdbesatz
•
Mutterkorn
•
Genotyp
      Merkmale dieses Typs können in den Laborverfahren in den Merkmalen für
      Markeranalyse verwendet werden.
•
Phänotyp
      Merkmale dieses Typs können in den Laborverfahren in den Merkmalen für
      Feldversuche verwendet werden.
Bezeichnung
Die
      Bezeichnung des Merkmals.
Formatauswahl
Mithilfe der Taste
F3
können
      hier Eingabeformate ausgewählt werden. Dieses Format wird verwendet, um in
      den Labordaten die Ausprägung des Merkmals anzuzeigen.
Einheit
Die
      Einheit des Merkmals.
Steht der
Einrichterparameter
„Erweiterte Einstellungen“ auf „Ja“,
      so kann mit der Taste
F3
eine Auswahl über die Mengeneinheiten
      aufgerufen werden.
Druckkennzeichen
Hier
      kann das Druckkennzeichen angegeben werden.

---

## Quick-Reporte mit archivieren

Quick-Reporte mit archivieren
Die grundsätzliche Aktivierung der Archivierung von
Quick-Reporten wird per
festgelegt.
Für den einzelnen Quick-Report lässt sich dann im
dortigen Einrichter-Dialog festlegen, ob eine Archivierung durchgeführt werden
soll.
Technisch ist eine Archivierung ins TIFF-Format noch
nicht realisiert.

---

## Referenzieren

Referenzieren
Behandelt die Thematik Formulararchiv-Einträge, um die
fehlende Referenznummer zu vervollständigen.
Es sind also Rahmendaten im Eintrag vorhanden, die
eine Generierung der Referenznummer ermöglichen.

---

## Qualitäten in Waage

Qualitäten in Waage
Erfassung der 20 Standard Qualitäten
Die Qualitäten 1 bis 20 werden auf der Registerkarte
Qualitäten gepflegt. Per
Einrichterparameter
„Soll die Registerkarte
Qualitäten ausgeblendet werden“ kann die Registerkarte angeschaltet werden. Des
Weiteren kann in den Einrichterparametern die Bezeichnung, das Format des Feldes
sowie die Verbindung auf die Rohwarenqualitäten hinterlegt werden.
Erfassung von Qualitäten per Tabelle
Um die Erfassung per Tabellenform zu aktivieren, muss
der
Steuerparameter 932
„Qualitätsverarbeitung in der Waage“ auf „1“ gestellt werden. Nach der
Umstellung wird dann anstelle der zwanzig Standardfelder für die Qualitäten eine
Tabelle angezeigt. Damit in der Tabelle die Qualitäten angezeigt werden, müssen
die Qualitäten als Artikelbetsandteile (
Bestandsteile
) angelegt werden.
Hauptmenü
Stammdaten
Konstanten Artikelstamm
Bestandteil oder Direktsprung [
ABST
].
Nach dem die Bestandsteile zugeordnet worden sind,
kann eine
Zuordnung
der
Bestandsteile im Artikelstamm erfolgen. Hier wird dann pro Artikelstamm
festgelegt, welche Qualitäten abgefragt werden sollen (hierbei reicht es aus,
wenn nur ein Repräsentant der Rohwarengruppe eine Zuordnung erhält). In den
Prozessbeschreibungsparametern der Waage kann noch zusätzlich eine private
Prozedur zur Anzeige angegeben werden. Die Zuordnung passiert mit der Funktion
Zusammensetzung
F2.
Hauptmenü
Stammdaten
Artikelstamm oder Direktsprung [
ARS
]
Die Qualitäten bei den Tabellen gestützten Erfassung
werden in eine eigene Relation geschrieben „Owaage_Qualitäten“ von dort aus
werden diese dann bei der Rohwarenbeleg Erzeugung in die Standard Tabelle
übernommen.

---

## Relation Formulararchivimport

Relation Formulararchivimport
Die „Hinzufügen“-Technologie bedient sich der Technik
eine interne Relation Formulararchivimport via ODBC-Methoden zu füllen. Diese
Relation wird entweder vom Mandantenserver oder per Funktion dazu benutzt die
Daten dann endgültig ins Formulararchiv zu stellen.
Per Funktion kann dieser Import per „^jpl fa_exec
externerimport“ ausgelöst werden.
Es handelt sich dabei dann um eine JPP-Methode
call JPP_NEW( "FAI" ,
"JFA_Import"  )
call JPP_EX ( "FAI" , "Auto_Import" )
call JPP_DELETE( "FAI"
)
Diese steht somit also auch „extern“ zur
Verfügung.

---

## Rohwareparameter einrichten

Rohwareparameter
einrichten
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[SPA]
Direktsprung
[RWPA]
Viele Funktionen innerhalb der
Module zur Bearbeitung von Rohwarebelegen werden von Rohwareparametern
beeinflusst. Alle Parameter können für unterschiedliche Zeiträume (Gültigkeiten)
mit unterschiedlichen Werten belegt werden. Diese Zeiträume sind, für jeden
Parameter einzeln, durch das jeweilige Datum gekennzeichnet, das den Beginn der
Gültigkeit markiert. Die in Referenz-ERP bereits vorhandenen Einstellungen aller
Parameter mit der Gültigkeit ‚ab 01.01.1901‘ können  nicht verändert
werden. Gewünschte abweichende Einstellungen können daher zunächst nur mit
Eintrag eines neuen Gültigkeitsbeginns festgelegt werden.
Die
Werte dieser Parameter werden grundsätzlich getrennt für die Bereiche Einkauf
und Verkauf festgelegt. Innerhalb dieser Bereiche können für die meisten
Parameter, die zunächst einmal mit Berücksichtigung Ihrer Gültigkeiten für alle
Rohwarenbelege im Einkauf beziehungsweise Verkauf gelten (globaler Wert),
spezielle von der globalen Bedeutung abweichende Einstellungen für einzelne
Rohwarengruppen wie auch einzelner Abrechnungsschemata vorgenommen werden. Die
einzelnen Programmfunktionen ermitteln den Wert eines benötigten Parameters
immer, indem zunächst nach der abrechnungsschemaspezifischen Einstellung gesucht
wird. Ist diese nicht vorhanden, so wird der rohwarengruppenspezifische Wert
gesucht, ist dieser ebenfalls nicht verfügbar, so ist der globale Parameterwert
maßgeblich.
Organisatorisch ist die Menge
der Rohwareparameter in Parametergruppen eingeteilt. Eine besondere Bedeutung
haben die Parameter der Gruppe ‚
globale Einstellungen
‘: Diese
können keine speziellen Einstellungen für  Rohwarengruppen und/oder
Abrechnungsschemata erhalten.
In
der Auswahlliste der Rohwareparametereinstellungen können die aktuellen Werte
der ausgewählten Parameter inklusive der auf Rohwarengruppen und/oder
Abrechnungsschemata a
[...]


---

## Rohwareparameter pflegen

Rohwareparameter
pflegen
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Rohwareparameter pflegen
Direktsprung
[SPA]
Direktsprung
[RWPA]
Im
Kopfbereich der Pflegemaske wird der Rohwareparameter mit Bezeichnung, Nummer
und Gruppe sowie der Bereich ‚
Einkauf
‘ beziehungsweise
‚
Verkauf
‘ zur Orientierung dargestellt. Die aktuell gültige
globale Einstellung des Parameters ist mit Beginn der Gültigkeit und dem
Parameterwert angegeben.
Im
Maskenbereich ‚
Rohwarengruppen mit spezieller Einstellung
‘ sind
alle Rohwarengruppen, die bezüglich des Parameters über eigene Einstellungen
verfügen, mit dem derzeit gültigen Wert und dem Beginn der zugehörigen
Gültigkeit in aufsteigender Reihenfolge der Rohwarengruppennummer
dargestellt.
Entsprechend werden
‚
Abrechnungsschemata mit spezieller Einstellung
‘ in der
Reihenfolge ihrer zugehörigen Rohwarengruppennummern und, innerhalb dieser, der
Abrechnungsschemanummern dargestellt.
Um
spezielle Einstellungen für eine Rohwarengruppe, die sich noch nicht in der
Liste befindet, hinzuzufügen, wird im Grid ‚
Rohwarengruppen mit spezieller
Einstellung
‘ die betreffende Rohwarengruppennummer in der Spalte
‚
Nummer
‘ eingetragen. Hierfür steht zur Unterstützung der Auswahl
eine Item-Box zur Verfügung, die die noch nicht berücksichtigten Rohwarengruppen
enthält. Es wird dann zunächst sowohl die aktuelle als auch die Grundeinstellung
aus der Gültigkeitsliste der globalen Werteinstellung des Parameters für diese
Rohwarengruppe übernommen.
Spezielle Einstellungen für
ein Abrechnungsschema werden im Grid ‚
Abrechnungsschemata mit spezieller
Einstellung
‘ durch Eingabe der Schemanummer, gegebenenfalls ebenfalls
mit Item-Box-Unterstützung, hinzugefügt. Gibt es bereits eine spezielle
Einstellung zur Rohwarengruppe des Abrechnungsschemas, so werden aktueller Wert
und Grundeinstellung aus dieser, sonst ebenfalls aus der globalen
Werteinstellung übernommen. Entgegen früherer Programmversionen ist es nicht
mehr erfo
[...]


---

## Rohwareparameter-Übersicht

Rohwareparameter-Übersicht
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Rohwareparameter pflegen
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Rohwareparameter ansehen
Direktsprung
[SPA]
Direktsprung
[RWPA]
Die
einzelnen Rohwareparameter und ihre Bedeutung werden nachfolgend
beschrieben.
Erfassungsst
art mit
Kontraktnummer
Parameternummer: 177
Einstellungen für
Rohwarengruppen und Abrechnungsschemata sind nicht möglich.
Optionen:
•
Ja
•
Nein
Für
die Erfassung von Rohwarebelegen wird mit diesem Parameter festgelegt, ob das
erste  zu bedienende Maskenfeld die Auswahl eines Kontrakts erlaubt, aus
dem dann Artikel-, Abrechnungsschema und Kundendaten vorbelegt werden.
Lager
Parameternummer: 2
Einstellungen für
Rohwarengruppen und Abrechnungsschemata sind nicht möglich.
Optionen:
•
keine Anzeige
•
mit Anzeige
•
Erfassung
Für
die Erfassung, Anzeige und Korrektur von Rohwarebelegen wird mit diesem
Parameter festgelegt, ob die Lagernummer auf der Bearbeitungsmaske unterdrückt,
nur dargestellt oder änderbar sein soll.
Rohware manuelle Werte – Qualitätsergebnis
änderbar
Parameternummer: 192
Einstellungen für
Rohwarengruppen und Abrechnungsschemata sind möglich.
Optionen:
•
Nein
•
Ja
Für
die Erfassung und Korrektur von Rohwarebelegen wird mit diesem Parameter
festgelegt, ob im Positionsteil die berechneten Werte der Qualitätspositionen
durch manuelle Werte überschrieben werden dürfen.
Rohware manuelle Werte –
Kostenergebnis änderbar
Parameternummer: 193
Einstellungen für
Rohwarengruppen und Abrechnungsschemata sind möglich.
Optionen:
•
Nein
•
Ja
Für
die Erfassung und Korrektur von Rohwarebelegen wird mit diesem Parameter
festgelegt, ob im Positionsteil die berechneten Beträge durch manuelle Werte
überschrieben werden dürfen.
Freigegebene Belege immer abrechnen
Parameternummer: 174
Einstellungen für
Rohwarengruppen und Abrechnungsschemata sind nicht möglich.
Optionen:
•
Nein
•
Ja
Ist
dieser Parameter mit dem Wert ‚
Ja
‘ belegt, so
[...]


---

## Scanner Konfiguration

Scanner Konfiguration
In dieser Variante wir das Verhalten des
Androids-Scanners oder Windows CE lösung eingestellt.
Maskenfelder
Bedeutung
IP-Adresse
Zur
      Identifikation des Scanners kann in der Konfiguration entweder die
      IP-Adresse oder ein benutzerdefinierter Bezeichner (z. B. Scanner1)
      eingetragen werden.
Sobald der Scanner einen Wert übermittelt, wird
      dieser zur Erkennung verwendet und die dazugehörige Konfiguration
      automatisch geladen.
Scannerprozedur
In
      diesem Feld wird die
Prozedur hinterlegt
, die beim
Scannen eines
      Befehls
automatisch aufgerufen wird.
So lassen sich gezielte
      Aktionen oder Abläufe direkt durch das Scannen auslösen.
Stylesheet-Prozedur
In
      diesem Feld kann eine benutzerdefinierte Stylesheet-Prozedur hinterlegt
      werden, um die HTML-Anzeige auf dem Scanner individuell zu gestalten und
      zu steuern.
EAN8
      Länge 8 akzeptieren
Hier
      kann festgelegt werden, ob 8-stellige EAN-Codes als EAN-8 erkannt werden
      sollen.
Diese Einstellung ist erforderlich, wenn eigene Scancodes im
      EAN-128-Format erstellt wurden, die als EAN-8 interpretiert werden
      sollen.
EAN8
      Länge 13 akzeptieren
Hier
      kann festgelegt werden, ob 13-stellige EAN-Codes als EAN-13 erkannt werden
      sollen.
Diese Einstellung ist erforderlich, wenn eigene Scancodes im
      EAN-128-Format erstellt wurden, die als EAN-13 interpretiert werden
      sollen.
Passwd nach IDLE
Diese Einstellung betrifft
      ausschließlich Windows CE Scanner.
Der Schalter steuert, ob beim
      Verlassen des Idle-Modus die Passworteingabe für den Bediener erneut
      erforderlich ist.
Dies dient der Sicherung des Zugriffs nach
      Inaktivität.
Max
      Länge der Menge
In
      diesem Feld kann eine
Zahl definiert
werden, die angibt,
wie
      viele Zeichen
bei der
Mengeneingabe über die Tastatur
maximal
      erlaubt sind.
Dies dient zur Begrenzung der Eingabelänge und zur

[...]


---

## Marktscanner einrichten

Marktscanner einrichten
In dieser Anwendung kann die Standard Einrichtung für
den Marktbereich für den jeweiligen ausgewählten Scanner eingerichtet werden.
Des Weiteren ist es möglich aus dieser Anwendung heraus den
Windowsscanner
zu starten. Dies kann durch zwei
Aktionen ausgelöst werden.
1.
Doppelklick auf die Zeile mit den Verbindungsparametern
2.
Markieren einer Zeile und mit
F9
oder
der Menüfunktion
Scannerprogramm
Starten
das Programm aufrufen.
Wird diese Anwendung zum ersten Mal gestartet und im
Referenz-ERP System befindet sich nicht die Datei dbconfig.xml welche die
Verbindungsparameter enthält, damit sich der Windows Scanner mit dem Referenz-ERP
System verbindet, werden die Felder mit den Verbindungsparameter der aktuellen
Verbindung vorbelegt.
Menüfunktionen
Menüfunktion
Bedeutung
Scannerprogramm Starten
Mit
      dieser Funktion wird der Windows Scanner gestartet. Es werden die
      Verbindungsparameter aus markierten Zeile genommen.
Marktscanner Standard
      Einspielen
Ist
      diese Menüfunktion aktiv, so kann für den ausgewählten Scanner den
      Marktstandard eingespielt werden. Der Standard kann nur für die aktuelle
      Datenbank eingespielt werden. Ist das Feld Permanente Inventur betretbar,
      so kann hier noch ausgewählt werden, ob beim Einspielen die Permanente
      Inventur berücksichtigt werden soll.
Maskenfelder
Feld
Bedeutung
Datei mit
      Verbindungsparameter
In
      diesem Feld kann per F3 Auswahl eine xml Datei ausgewählt werden, welche
      Verbindungsparameter für das Verbinden von der Scanner-Software zu einer
      Referenz-ERP System enthält. Wird per eine Datei ausgewählt, so werden die darin
      enthaltenen Verbindungsdaten in die Datentabelle geladen.
Standard mit Permanenten Inventur
      einspielen
Wird
      dieses Feld vorm Einspielen des Standards auf „Ja“ gestellt, so wird die
      Permanente Inventur für den Scanner mit eingespielt. Kann dieses Feld
      nicht betreten werden, dann wurde di
[...]


---

## Schritt 1 Setup

Schritt 1 Setup
Schritt 1.1: Voraussetzung
Das Belegfluss Modul basiert auf der Technologie
unseres Referenz-ERP Archives. Dem entsprechend muss sowohl eine Lizenz für das Referenz-ERP
Archiv, als auch dem Belegfluss vorliegen.
Schritt 1.2: SPA aktivieren
Workflow-Lizenz (SPA 1098) auf „ja“ setzten
Schritt 1.3: Postfächer einrichten
Zum Einrichten der Postfächer ist es nötig unter dem
Direktsprung [BF] und dort unter der Variante 4 (Postfach-Einrichtung),
Postfächer einzurichten (F5).
Hier sind bereits private Prozeduren hinterlegt. Die
Beispiele werden in
Schritt 3
näher erläutert.

---

## Schritt 2 Konfiguration

Schritt 2 Konfiguration
Schritt 2.1: Postfächer den Benutzern zuweisen
Damit Benutzer auf die Postfächer zugreifen können
müssen diese dem Benutzer zugewiesen werden. Dafür mit dem Direktsprung [BD] den
gewünschten Bediener auswählen, den Pfleger aufrufen (F5) und hier unter dem
Reiter „Belegfluss“ die Postfächer hinzufügen (F3)
Schritt 2.2: Test Import
Um nun einen Datensatz in den Belegfluss zu
importieren benutzt man den Direktsprung [FAI]. Im Archiv Import importiert man
nun mit (F5) einen Datensatz.
Hier ist zu beachten, dass ein Name vergeben muss und
der Pfad „..\import“ mit einem Testpfad ausgetauscht werden muss (in diesem Pfad
sollte sich eine Testdatei befinden). Ebenfalls muss man die Funktion
Sql-Ereignis nach Einfügung aufrufen und folgende Prozedur einfügen:
create procedure
"admin"."p_sqlAfterInsert" ( in in_fa_id integer , in in_fa_mndnr integer )
begin
insert into
formulararchivbelegfluss (fa_id, fa_mndnr, angefordert) values (in_fa_id,
in_fa_mndnr, 1)
end
Nachdem dies konfiguriert ist, speichert man den
Datensatz mit (F9) ab.

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

## Standardablauf

Standardablauf
Nach der Eingabe der Menge wird (sofern unter
[FRZ]
eingestellt, siehe später unter
Parameter der Partiezuordnung!) eine automatische Partiesuche durchgeführt.
Wurde mindestens eine passende Partie gefunden, so wird das Partiefenster
automatisch aufgeblendet und die zugeordneten Partien werden angezeigt. Der
Eingabefokus steht dann auf der ersten Partienummer:
Die ENTER ( Return ) Taste in der Spalte Partienummer
ohne Änderung an der Partienummer wird immer als Bestätigung aufgefasst und
bewirkt, dass wieder zur ‚normalen’ Warenerfassung zurückgesprungen wird.
Durch TAB oder Pfeiltasten kann in den Feldern
navigiert werden. Durch die Eingabe einer Partienummer in einer leeren Zeile
wird die noch verbliebene Differenz zur Gesamtmenge der Warenposition vorbelegt.

---

## Steuerparameter

Steuerparameter
Steuerparameter steuern bestimmte Vorgänge im Ablauf
von Anwendungen und anderen Programmen in Referenz-ERP. Durch die in den
Steuerparametern hinterlegten Werte können diese Anwendungen und Programme zu
einem bestimmten Verhalten veranlasst werden.
Steuerparameter lassen sich über die Auswahlliste in
zwei Darstellungen anzeigen.
1.
Einfach (ohne Schlüssel)
2.
Komplex (mit Schlüssel)
Die Ansicht wird bereits bei der Erstellung des
Steuerparameters gewählt.
Ist der Steuerparameter „einfach“, so zeigt die
Darstellung nur die Gültigkeitszeiträume und die Werte des verwendeten
Abfrageformats an.
Ist der Steuerparameter „komplex“, so ist auch die
Darstellung entsprechend:
Feld
Bezeichnung
Gültig ab
Das
      Datum ab dem der folgende Wert gültig ist
Einstellung /
      individuell
Zeigt die Werte des Abfrageformats
      zum gewählten Gültigkeitsdatums
Schlüssel / individuell
Der
      Schlüssel der Gültigkeit zum gewählten Gültigkeitsdatum
Option / individuell
Der
      Wert, der zum ggf. verwendeten Schlüssel und dem gewählten
      Gültigkeitsdatum gültig ist
Neu
Um einen neuen Steuerparameter einzurichten, verwendet
man in der Auswahlliste entweder die Funktion „SPA Ändern“ oder das Tastenkürzel
„Shift+F5“.
Über „Neu“ oder „F8“ lässt sich nun ein neuer
Steuerparameter erstellen.
Feld
Beschreibung
Nummer
Nummer des Steuerparameters wird
      automatisch gesetzt
Bezeichnung
Bezeichnung des
      Steuerparameters
Gruppe
F3
      Auswahl zur Wahl der Gruppe für den Steuerparameter
Sortierung in der Gruppe
ES
      wird eine Nummer vorgeschlagen, die der letzte stelle in der Gruppe
      entspricht. Diese kann angepasst werden.
Es ist nur eine Nummer
      zwischen 0 und 32767 gültig.
Ausprägung
F3
      Auswahl
einfach (ohne
      Schlüssel)
: Gibt
      an, das der Steuerparameter nur über das Gültigkeitsdatum und ein
      Abfrageformat verfügt
komplex(mit Schlüssel und
      Option)
: Gibt an,
      das auch ein Schlüssel
[...]


---

## Steuerungsparameter [SPA] Partieverwaltung

Steuerungsparameter [SPA] Partieverwaltung
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
oder Direktsprung
[SPA]
Nachfolgend die Beschreibung für SPA-Einstellung 1 bis
62:
SPA
Beschreibung
1
Globale Einstellung ob mit
      Partieverwaltung gearbeitet wird (Ja/Nein)
3
Anzahl Ziffern für eine Partienummer
      (1 bis 8)
4
Aktualisierung der Mengen und Werte
      bereits bei Vorgangserfassung (Ja/Nein)
9
Wahl
      der Voreinstellung für die Anlage der Partieartikel (Artikelstamm oder
      Artikel-Lager)
•
Artikelstamm:
      Zuordnung einer Artikelnummer aus dem Artikelstamm
•
Artikel/Lager:  Zuordnung eines
      Artikels aus einem Lager
10
Steuert die Artikelanzeige in der
      Partieverwaltung (Partien ändern + F2 Artikel)
•
Ja:
      Anzeige für Lager und Saldo
•
Nein:   Sollmengen Einkauf
      und Verkauf werden dargestellt
18
Steuert die autom. Partieauswahl nur
      für die Auftragserfassung
•
Nein:   Keine autom.
      Partieauswahl bei der Auftragserfassung
•
Verkauf: Autom.
      Partieauswahl nur bei der Auftragserfassung im Verkauf
•
Einkauf: Autom.
      Partieauswahl nur bei der Bestellerfassung im Einkauf
•
Ja:
      Autom. Partieauswahl bei der Auftragserfassung im Einkauf und
      Verkauf
20
Steuert die autom.Partieauswahl für
      die Vorgangserfassung (ab 2 Partien/generell/nie/auch ohne
      Partien)
•
ab 2 Partien:
      Autom. Anzeige der Partieauswahl, wenn mind. 2 Partien für diesen Artikel
      vorhanden
•
generell: Autom.
      Anzeige der Partieauswahl, wenn mind. 1 Partie für diesen Artikel
      vorhanden
•
nie: Keine
      autom. Anzeige der Partieauswahl
•
ohne Partien:
      Autom. Anzeige der Partieauswahl, auch wenn keine Partie für diesen
      Artikel vorh.
21
Steuert die autom. Partieauswahl nur
      für Vorgangsänderungen
•
Ja:
      Bei Änderung eines Vorgangs erfolgt eine autom. Anzeige der
      Partieauswahl
•
Nein:   Keine autom.
      Anzeige der Partiea
[...]


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

## Lizenzen

Lizenzen

---

## Vertreter / Provision (Einrichtung)

Vertreter / Provision (Einrichtung)

---

## Stoffstromdaten-Druckpositionen

Stoffstromdaten-Druckpositionen
Zur Darstellung von Stoffstromdaten auf
Vorgangsdruck-Formularen stehen im Modul zur
Formulareinrichtung
für den Druckbereich
‚
Warenposition‘
Formulardruckpositionen zur Verfügung.
-
6601 ID_STOFFSTROM_ART
Nummer der Stoffstromart aus dem
Anwendungsformat
‚af_stofstart‘
-
6602 ID_STOFFSTROM_TEXT
Bezeichnung des Bestandteils aus der
Artikelbestandteil-Liste
-
6603 ID_STOFFSTROM_ANTEIL
Anteil des Stoffstroms (Prozent oder
Menge/Grundmengeneinheit des Artikels)
-
6604 ID_STOFFSTROM_MENGE
Berechnete Stoff-Menge zur
Stoffstromart
-
6605 ID_STOFFSTROM_MEANTEIL
Mengeneinheitsnummer des Stoffstromanteils
(0 = %)
-
6606 ID_STOFFSTROM_METEXT_ANTEIL
Text zur Mengeneinheit des
Stoffstromanteils (%, kg/hl …)
-
6607 ID_STOFFSTROM_MEMENGE
Mengeneinheitsnummer der
Stoffstrom-Menge
-
6608 ID_STOFFSTROM_METEXT_MENGE
Kurztext zur Mengeneinheit der
Stoffstrom-Menge
-
6609 ID_STOFFSTROM_HERKUNFT
Herkunftskennzeichen der Stoffstrom-Werte
- 0: aus Artikelstamm
- 10: Anteil manuell
- 20: Menge
manuell
Wichtig bei der Einrichtung der Druckpositionen ist
die Angabe des Wertes für ‚
Parameter‘ in der
Detail-Maske
zur
Druckposition.
Der Parameter gibt an, für welchen
Stoffstrom-Bestandteil aus der
Artikelstamm-Zusammensetzungsliste
der zu
druckende Wert zu ermitteln ist. Dazu wird intern eine Liste der Teilmenge der
Bestandteile geführt, die als Stoffstrombestandteil gekennzeichnet sind. Auf
diese Liste bezieht sich der Wert des Parameters. Der Wert
‚1‘
bezieht
sich demnach auf den ersten in der Artikelzusammensetzung angegebenen
Stoffstrom-Bestandteil, der Wert
‚2‘
auf den zweiten und so weiter,
unabhängig davon, ob zwischen oder vor diesen Angaben in der
Artikelstamm-Zusammensetzung noch andere Bestandteile aufgeführt sind, die aber
keine Stoffstrom-Bestandteile sind.

---

## Parameter

Parameter
In der Parameter-Übersicht werden alle Parameter mit
Wert, Zugriffen und Herkunft angezeigt.
Felder
Beschreibung
Nr
Nummer des Parameters
Parameter
Name
      des Parameters
Wer
Wert
      des Parameters
Zugriffe
Anzahl der Zugriffe auf diesen
      Parameter
Herkunft

---

## Tammo

Tammo
Das Modul Tammo (Trusted Referenz-ERP Mail Message
Operation) dient der Verarbeitung und Archivierung ankommender Mails in
Zusammenarbeit mit Referenz-ERP.
Einrichtung
Die Einrichtung wird über den
Steuerparameter 933
gesteuert. Da die Einstellungen
jedoch vom Modul abhängig sind, werden sie hier genauer beschrieben.
IMAP
Webservice
Anhang Umwandlung
Fehlerbehandlung
Für die Fehleranalyse wird im „BIN“-Verzeichnis von
Referenz-ERP die Log-Datei „Tammo.log“ angelegt, wenn ein interner Fehler aufgetreten
ist.

---

## IMAP - Einrichtung

IMAP - Einrichtung
Folgende Steuerparameter Einstellungen müssen für das
Modul IMAP eingerichtet werden.
Text
Wert
Beschreibung
Mailplugin
IMAP
Benutzername / E-Mail
Die
      E-Mailadresse oder der Benutzername beim entsprechenden
      Provider.
Passwort
Hier
      muss das Passwort des Benutzers eingetragen werden.
Domain / Host
Der
      Hostname für den IMAP-Abruf beim Provider.
Port
Die
      Nummer des Ports.
SSL
      verwenden
Soll
      kein SSL verwendet werden, kann hier der Wert „FALSE“ eingetragen
      werden.
Beispiel GMX
Hier eine beispielhafte Einrichtung beim Anbieter
GMX.de
Text
Wert
Mailplugin
IMAP
Benutzername / E-Mail
example@gmx.de
Passwort
*****
Domain / Host
imap.gmx.net
Port
993
SSL
      verwenden
TRUE
Beispiel GMAIL
Hier eine beispielhafte Einrichtung beim Anbieter
GMAIL.com
Text
Wert
Mailplugin
IMAP
Benutzername / E-Mail
example@gmail.de
Passwort
*****
Domain / Host
imap.gmail.com
Port
993
SSL
      verwenden
TRUE
Für GMAIL sind eventuell noch folgende
Kontoeinstellungen nötig.
Einstellung
Wert
IMAP-Zugriff
Gmail -> Einstellungen ->
      Weiterleitung und POP/IMAP
Der
      Haken muss bei „IMAP aktivieren“ gesetzt sein.
Weniger sichere Apps
      zulassen
Mein Konto -> Verbundene Apps und
      Webseiten
Dort
      muss die Option „Weniger sichere Apps zulassen“ auf „An“
      stehen.
Beispiel KERIO
Hier eine beispielhafte Einrichtung für einen KERIO
Server
Text
Wert
Mailplugin
IMAP
Benutzername / E-Mail
test@Branchen-ERP
Passwort
*****
Domain / Host
192.168.241.33
Port
143
SSL
      verwenden
FALSE

---

## Webservice - Einrichtung

Webservice - Einrichtung
Folgende Steuerparameter Einstellungen müssen für das
Modul Webservice eingerichtet werden.
Text
Wert
Beschreibung
Mailplugin
Webservice
Benutzername / E-Mail
Benutzername des Benutzers für den
      die Mails abgerufen werden sollen.
Passwort
Hier
      muss das Passwort des Benutzers eingetragen werden, wenn es sich nicht um
      den gleichen Benutzer handelt unter dem der Dienst läuft.
Ansonsten kann der Wert frei
      bleiben.
Domain / Host
Domain des Benutzers
Webservice Exchange
      Version
Bezeichnung der Exchange Version,
      aktuell stehen folgende Versionen zur Verfügung.
•
Exchange2007_SP1
•
Exchange2010
•
Exchange2010_SP1
•
Exchange2010_SP2
Für SP3 wird
      auch diese Einstellung verwendet.
•
Exchange2013
•
Exchange2013_SP1
Webservice Autosicover
      Url
E-Mailadresse des
      Benutzers
Beispiel
Text
Wert
Mailplugin
Webservice
Benutzername / E-Mail
TAMMO
Passwort
*****
Domain / Host
Branchen-ERP
Webservice Exchange
      Version
Exchange2010_SP2
Webservice Autodiscover
      Url
TAMMO@Branchen-ERP

---

## Anhang Umwandlung

Anhang Umwandlung
In den
Steuerparametern
kann eingestellt werden, dass eine
Umwandlung der Anhänge in das Format PDF/A (
Format zur Langzeitarchivierung
digitaler Dokumente
) erfolgen soll.
Die Dokumente werden zusätzlich zu den ursprünglichen
Dokumenten im Archiv gespeichert.
Aktuell werden nur Excel-Dokumente in das Format PDF/A
umgewandelt.

---

## Usage

Usage
Nach der vollständigen Eintragung einer Mail, löst
Tammo einen Eintrag in den Datenstrom aus. Der Prozess dazu lautet TammoExecute.
Der Kommandoparameter „LOOPSLEEPTIME“ erlaubt eine Dauerschleife des
Tammo-Prozesses mit einer Wartezeit zwischen den Mailevents von
„LOOPSLEEPTIME“-Sekunden.
Heartbeat
Um eine Überwachung des Prozesses zu ermöglichen, kann
mit dem Parameter „HEARTBEATSECONDS“ festgelegt werden, in welchem Intervall ein
Timestamp Eintrag in die Tabelle „TammoInformation“ erfolgen soll.
Dadurch kann man mit Hilfe eines Datenbankevents
überprüfen, ob der Prozess schon länger nicht gelaufen ist.
Formulararchivgruppe
Die Mail und alle Anhänge werden im Formulararchiv in
einer Gruppe zusammengefasst. Anhand dieser kann man die Dokumente
zusammengehörenden Dokumente identifizieren.
Der Name der Gruppe ist ein vorangestelltes „Tammo“
und eine GUID. Sie könnte wie folgt aussehen:
Tammo-{98cb6768-7fbd-477d-a4fa-1564fd46dc90}

---

## Technische Erweiterungen

Technische Erweiterungen
Referenz-ERP stellt interne Funktionalitäten über die
Technik
ActiveX
und
COM
zur
Verfügung. Das Referenz-ERP-Setup stellt die dafür notwendigen technischen
Voraussetzungen auf den jeweiligen Referenz-ERP-Clienten her.
Die folgenden Hilfsprogramme werden zusätzlich zu
Test- und Analyse-Zwecken mit ausgeliefert.

---

## Technisch

Technisch
Hauptmenü
Administration
Archiv
Administration
Technisch
Direktsprung
[FAAD]
Diese Variante stellt im Gegensatz zu der Variante
Formulararchiv-Administration
mehr die
technischen Aspekte eines Archiv-Eintrages heraus:
Felder
FormularId
Die
      Formulararid des Formulars beim Vorgangsdruck.
FormularIdZ
Im
      Formularpfleger wird bei jeder Änderung des Formulars ein Zähler
      hochgezählt. Bei Vorgangsdruck wird neben der FormularId hier zusätzlich
      dieser Zähler gespeichert.
Inkarnation
In
Nur letzte Korrektur
      speichern
kann eingestellt werden, dass unter bestimmten Bedingungen
      kein neuer Archiv-Eintrag bei erneutem Vorgangsdruck erstellt wird. Dann
      wird der Archiv-Eintrag mit den aktuellen Daten „überschrieben“.
Hier
      kann man nun ablesen, wie oft eine solche Überschreibung stattgefunden
      hat.
Host
Der
      Hostname des Rechners auf dem die Archivierung stattgefunden
      hat.
Client
Der
      Hostname des Clients.
Dies
      ist zum Beispiel bei Terminalservern der Hostname des Rechners auf dem der
      Terminalserverclient läuft.
Queue
Der
      Druckerwarteschlangenname beim Vorgangsdruck.
Folgende Möglichkeiten stehen auch hier zur Verfügung:
Funktionen der Variante.

---

## Technisches zum Formulararchiv

Technisches zum
Formulararchiv

---

## Individualisierung

Individualisierung
Belege
erzeugen
Zum individualisieren der Belegerzeugung können am
Steuerparameter „
829
“ Makros
hinterlegt werden. Diese werden zu den angegebenen Zeiten aufgerufen.
Die Makros werden mit 4 Übergabeparametern
aufgerufen.
Parameter
Beschreibung
PARAM1
Dieser Parameter enthält den Modus,
      durch welchen das Makro aufgerufen wurde. Mögliche Werte stehen in der
      folgenden Tabelle.
Makrotyp
Wert
MAKRO_KOPF_START
KOPFSTART
MAKRO_KOPF_ENDE
KOPFENDE
MAKRO_POSI_START
POSISTART
MAKRO_POSI_ZWISCHEN
POSIZWISCHEN
MAKRO_POSI_ENDE
POSIENDE
MAKRO_BELEG_SPEICHERN
BELEGSPEICHERN
PARAM2
Dieser Parameter enthält den Namen
      des aktuellen „Vorgangshelper“ JPP-Objekts.
PARAM3
Dieser Parameter enthält den
      JVARS-Owner in dem die Vorgangskopfdaten liegen.
PARAM4
Dieser Parameter enthält den
      JVARS-Owner in dem die Positionsdaten der aktuellen Position
      liegen.
Die Daten für den Vorgang und die Positionen werden in
JVARS zwischengespeichert. Diese können im Makro über den entsprechenden
JVARS-Owner ausgelesen und geändert werden. Alternativ können über den Namen des
Vorgangshelper-Objekts eigene JPP-Funktionen aufgerufen werden, um die
Verarbeitung zu beeinflussen.
Vorgangskopf JVARS
JVAR Name
Beschreibung
VALUE_ID
ID des Beleges. Anhand dieser Nummer
      kann auf die XML-Daten zugegriffen werden.
VALUE_KundenNummer
Nummer des Kunden
VALUE_Klasse
Klasse des Beleges
VALUE_Unterklasse
Unterklasse des Beleges
VALUE_LagerNummer
Nummer des Lagers
VALUE_IstGutschrift
Wenn ist im Originalbeleg die Summe
      negativ, steht dieser Wert auf 1 und die Klasse auf 1800.
VALUE_BelegNummer
Belegnummer des Ursprungsbelegs.
      Dieser Wert wird in die Referenznummer geschrieben.
VALUE_Periode
Periode des Belegs
VALUE_BelegDatum
Datum des Belegs
VALUE_Jahr
Jahr des Belegs
VALUE_ValutaDatum
Valutatdatum des Belegs
Position JVARS
JVAR Name
Beschreibung
VALUE_PosZuAb
Zu/Abschlagskennzeichen
(wird
      nicht verwendet)
VALUE_Menge
Menge de
[...]


---

## Position aufteilen

Position aufteilen
Auf dieser Maske kann die ausgewählte Position auf
mehrere unterschiedliche Artikel aufgeteilt werden. Dabei muss die Menge und der
Wert komplett aufgeteilt werden. Die Lagervorbelegung kann per
Einrichterparameter an und ausgestellt werden. Im Standard wird die Lagernummer
nicht vorbelegt. Wenn die Lagernummer vorbelegt wird, so wird das
umgeschlüsselte Referenz-ERP Lager der ausgewählten Position genommen. Auch hier gilt
es, dass nur Artikel ausgewählt werden können, die auf dem gleichen Lager liegen
und den gleichen Steuersatz haben.
Um den gültigen Steuersatz eines Artikels aus dem
Referenz-ERP Pool zu finden wird die Steuergruppe des Lieferanten mit den
Steuerschlüsseln des Artikels auf dem ausgewählten Lager verprobt. Wird der
gewünschte Artikel nicht angezeigt, so konnte keine Zuordnung zwischen dem
Steuerschlüssel und der Steuergruppe gefunden werden. Summen Zeilen können nicht
aufgeteilt werden.
Aufgeteilte Positionen können hier auch wieder
Rückgängig gemacht werden, in dem die Datentabelle geleert wird.
Des Weiteren kann mit dem Steuerparameter
877
das Verhalten bezüglich der Mengen
/ Betragsprüfung der aufgeteilten Position zu der Position im Terres Beleg
geändert werden.

---

## Parameter für den Testmandanten im Mandantprofil

Parameter
für den Testmandanten im Mandantprofil
Im Testmandanten werden Verbindungen zu externen
Systemen, Events etc. unterbunden um zu verhindern, dass das Testsystem
unkontrolliert Kontakt zu Live-Systemen aufnimmt. Für private Funktionen lässt
sich die Funktion „AMIC_MandantProfilParameter“ aufrufen.
Diese wird mit einem Parameternamen (Private Parameter
haben den Präfix „P_“) und den Vorgabewert gefüllt.
Die Prozedur gibt folgende Möglichkeiten zurück:
System
Wert
Livesystem ohne definierten
      Parameter
Default-Wert
      (Vorgabewert)
Livesystem mit definierten
      Parameter
Für
      das Livesystem definierter Parameter aus der Tabelle
      MandantProfil
Testsystem ohne definierten
      Parameter
NULL
Testsystem mit definierten
      Parameter
Für
      das Testsystem definierter Parameter aus der Tabelle
      MandantProfil
Einrichtungsbeispiel:
Sie wollen in einer Prozedur eine Mailadresse
verwenden, die „live@me.xy“ heißt. Im Testsystem soll jedoch „test@me.xy“
verwendet werden.
Tragen Sie in der Tabelle Mandantprofil die folgenden
Werte ein:
INSERT INTO
MandantProfil (MandantProfilId, MandantParName, MandantParWert)
VALUES(1,'P_MAILADRESSE','test@me.xy')
Diese Werte können Sie bequem mit dem
Mandantenprofil-Pfleger
eintragen!
Verwenden Sie die Prozedur
„AMIC_MandantProfilParameter“ wie folgt:
Set
mailadresse =
AMIC_MandantProfilParameter
('P_MAILADRESSE',
'live@me.xy');
Mit dieser Einrichtung stellen Sie sicher, dass Sie im
Testsystem andere Parameter verwenden, als im Livesystem und dennoch nicht auf
Funktionalitäten verzichten müssen.

---

## Textzeilen (F8)

Textzeilen (F8)
In diesem Pfleger können benutzerdefinierte Textzeilen
für den Vorgang hinterlegt werden. Die Textzeilen können für einen bestimmten
Zeitpunkt in der Vorgangsverarbeitung bestimmt werden. Ebenfalls kann auch ein
Dokument geladen werden.
Feld
Beschreibung
Textfeld
Multiline Text, welcher später im
      Vorgangsdruck erscheint
Übernahme bis
Angabe zu welchem Zeitpunkt in der
      Vorgangsverarbeitung die Textzeile gedruckt werden soll
Funktion
Beschreibung
Text
      übernehmen
(F2)
Übernimmt den Text und schließt den
      Pfleger
Dokument laden
(F9)
Öffnet den
Referenz-ERP Dokumenten Editor
Abbruch
(F3)
Schließt den Pfleger ohne zu
      speichern
Beenden
(ESC)
Beendet den Pfleger mit einer
      Abfrage zum übernehmen (speichern)

---

## TSE Auswahlliste

TSE Auswahlliste
In der TSE-Auswahlliste, Hauptmenü
Barvorgänge
TSE Pflegen, oder Direktsprung
[TSE]
,
sind alle TSE-Konfigurationen der Technischen Sicherungs-Einrichtungen zu
sehen.
Felder der Auswahlliste
Feld
Beschreibung
TSE-ID
Gibt
      die TSE-ID an.
Ab
      Datum
Gibt
      an, ab wann die TSE-Einstellung gelten soll.
Es
      kann zu einer gleichen TSE-ID mehrere Einträge mit verschiedenen
Ab Datum
geben.
In
      Bezug auf das aktuelle Tagesdatum ergibt sich aber logischerweise immer
      eine einzige TSE-Einstellung, die dann
aktiv
ist. Diese wird auch im
      Standard
grün
gekennzeichnet.
      (Siehe auch Aktiv-Datum)
Mehrere
Ab Datum
-Konfigurationen können
      immer dann eingesetzt werden, wenn Einstellungen vom Datum
      abhängen.
(Erzeugen kann man eine TSE-ID mit
      mehreren
Ab Datum
über
F5
und
Speichern unter.
)
Bezeichnung
Zeigt die eingetragene Bezeichnung
      der TSE an, dient zur leichteren Identifizierung durch den
      Anwender.
TSE-Typ
Gibt
      an, um welche Art von TSE es sich handelt.
Client ID
Gibt
      die Client ID an, mit dem die TSE initialisiert wurde.
Laufwerk
Gibt
      das Laufwerk an, auf dem die TSE initialisiert wurde. (Dient auch als
      „Fallback“ für automatisches Mapping, falls die automatische Suche die TSE
      nicht „auffinden“ konnte)
Aktueller Fundort
Zeigt den aktuellen Fundort in der
      Form Rechner/Laufwerk
Hardware-Host
Gibt
      an, an welchem Rechner angeschlossen war, als die TSE initialisiert
      wurde.
Manueller-Host
Gibt
      an, welcher Host im Falle des automatischen Mappings herangezogen werden
      soll, also in aller Regel ein UNC-Pfad. Zum Beispiel:
\\
Rechnername\Freigabename
Kassen…
Gibt
      an, an welche Kasse die TSE gebunden ist.
Aktiv-Datum
Zeigt zu jeder TSE-Einstellung das
      Datum der TSE-Einstellung an, die am aktuellen Datum aktiv ist. (siehe
      auch
Ab Datum
)
Seriennummer
Die
      eindeutige Seriennummer der TSE
Referenz-ERP TSE-
[...]


---

## Versandprofilstamm

Versandprofilstamm
Administration
Firmenkonstanten
Versandprofilstamm
Direktsprung
[VPST]
Der Versandprofilstamm dient zum Hinterlegen von
Profilen für den Versand von zum Beispiel  E-Mail oder Fax zu
verschiedensten Zwecken in Referenz-ERP. Das Profil, welches im Mandantenstamm
hinterlegt wurde, wird hier mit grüner Farbe markiert und kann an dieser Stelle
auch nicht einfach gelöscht werden.
Im „Startmenü“ die Anwendung „Dienste“ aufrufen. Dort
den Referenz-ERP.Mailservice selektieren und „Eigenschaften“ aufrufen. Startyp auf
„Automatisch“ festlegen und den Dienst starten.
Eingabefelder
Feld
Beschreibung
Profil-Bezeichnung
Name
      des Profils
Typ
Dieser
Typ
gibt an, für
      welche Verwendung dieser Eintrag zuständig ist
Standard
Kennzeichnet den
      Versandprofilstammeintrag als Standard
Standard dieses Typs
Kennzeichnet diesen Eintrag ggf. als
      Standard des o.a. Typs
Sendeeinstellungen
Die Sendeeinstellungen enthalten die Informationen,
      welche zum Versenden der Daten erforderlich sind. Die mit einem
*
versehenen Felder sind hierbei die Angaben, welche mindestens zur
      Verfügung stehen müssen!
Registerkarten und Felder passen sich je nach
      Typ-Auswahl den entsprechenden Gegebenheiten an (E-Mail oder
      Fax).
Über den Knopf „Sendeeinstellungen testen“ wird
      versucht eine Verbindung zum SMTP-Server aufzubauen, je nach Status wird
      eine Meldung ausgegeben.
Bezeichnung *
Bezeichnung des
      Versandprofilstamms
Versandart *
Versandart
setzt die Technologie, mit der E-Mails versendet werden können.
Bitte verwenden Sie zur
      Neueinrichtung ausschließlich die Option 7 – Vermailung ! ! !
Versende-Server *
Der
      Name oder die IP-Adresse des verwendeten SMTP-Servers (smtp.gmail.com oder
      74.125.136.108)
Wichtig
: Wenn Microsoft Graph zur
      Versendung verwendet wird, müssen in die Felder Benutzername und Absender
      die bei Microsoft Graph eingerichtete Mailadresse eingetragen werden.
      Außerdem müsse
[...]


---

## Vorgangseinrichtung

Vorgangseinrichtung
In der
Formularzuordnung/Vorgangsunterklasse
[FRZ]
ist der entsprechende Vorgang für
die Produktion (Vorgangsklasse 5220 und entsprechende Vorgangsunterklasse) zu
definieren.
Im Register Formulare sind die zu verwendenden Formulare
anzugeben.
Die Registerkarte
Produktion
erlaubt diverse
Angaben zur Behandlung von Produktionsvorgängen der jeweiligen
Vorgangsunterklasse:
Direktsprung Hauptmaske Positionsteil
Bei Aufruf der Erfassung und/oder Korrektur eines
      Produktionsbelegs kann entsprechend der Einstellung dieses Wertes direkt
      zum Positionsteil verzweigt werden.
Nein: keine automatische
      Weiterschaltung
Erfassung: automatische Weiterschaltung bei
      Erfassung
Korrektur: automatische Weiterschaltung bei
      Korrektur
Erfassung +Korrektur: immer automatische
      Weiterschaltung
Direktsprung Positionsteil
      Produktionserfassung
Bei
      Aufruf der Erfassung und/oder Korrektur eines Produktionsbelegs kann
      entsprechend der Einstellung dieses Wertes bei Aufruf des Positionsteils
      direkt in die Produktionserfassungsmaske verzweigt werden.
Nein: keine automatische
      Weiterschaltung
Erfassung: automatische Weiterschaltung bei
      Erfassung
Korrektur: automatische Weiterschaltung bei
      Korrektur
Erfassung +Korrektur: immer automatische Weiterschaltung
Produktionslager aus
      Bedienerkonstanten
Legt
      fest, wie das Produktionslager zu bestimmen ist.
Ja =
      Lagernummer aus Bedienerkonstanten
Nein
      = Lagernummer wie im nächsten Feld angegeben
Produktionslager
Wird
      die Produktionslagernummer nicht aus den Bedienerkonstanten ermittelt, so
      wird die zu verwendende Produktionslagernummer hier angegeben.
Erlösklasse Produktion
Die
      Erlösklasse für Produktionen wird an dieser Stelle festgelegt.
Erlösklasse Vermahlung
Die
      Erlösklasse für Vermahlungen wird an dieser Stelle festgelegt.
Partieanzeigeprozedur
Parameterlose Datenbank-Prozedur zur
      Anzei
[...]


---

## Vorgangsklammer

Vorgangsklammer
Die Vorgangsklammer gilt als Stammsatz für die
Vorgangsmappe.
Das Löschverhalten einer Vorgangsklammer kann über den
Steuerparameter „Löschverhalten bei Vorgangsmappen“ (
SPA 796
) beeinflusst werden.
Kopffelder
Feld
Beschreibung
Klammernummer
Nummer der Klammer
Bezeichnung
Bezeichnung der Klammer
Container
Hier
      kann eine Containernummer hinterlegt werden.
Zusätzlich kann hier auch eine
      Itembox zur Verfügung stehen. Diese wird im
Streckenerfassungsprofil
unter
      „Itembox für Container“ eingetragen. Bei mehreren Profilen wird die erste
      gefundene Itembox verwendet.
Wenn
      in der Itembox ein Rückgabefeld mit dem Namen „retBezeichnung“
      zurückgegeben wird, so erscheint dieser Wert in dem Anzeigefeld hinter dem
      Containerfeld.
Abw.
      Adresse
Hier
      kann eine Abweichende Adresse angegeben werden.
Siehe
unten
für weitere
      Adressenpflege und Zuordnung.
Registerkarte „Vorgänge“
Feld
Beschreibung
Führende Elemente aus Grid
      1
Frei
      eingebbarer Text
Mengenabhängige Elemente aus Grid
      2
Frei
      eingebbarer Text
Weitere abhängige Elemente aus Grid
      3
Frei
      eingebbarer Text
Packer
Bediener dieser Klammer
Status
Status der Klammer, zulässige Werte
      können im Anwenderformat „AF_KLSTATUS“ gepflegt werden.
Lokalität
Lokalität aus dem
      Lagerverwaltungssystem
Abweichende Zieladresse
Über
      den zugehörigen Button mit dem Fragezeichen kann man eine alternative
      Adresse aus dem Anschriftstamm auswählen.
Wählt man den Button mit dem
      Stift kann man die abweichende Zieladresse neu eingeben oder
      ändern.
Abweichende
      Herkunftsadresse
Über
      den zugehörigen Button mit dem Fragezeichen kann man eine alternative
      Adresse aus dem Anschriftstamm auswählen.
Wählt man den Button mit dem
      Stift kann man die abweichende Herkunftsadresse neu eingeben oder
      ändern.
Spedition
Über
      den zugehörigen Button mit dem Fragezeichen
[...]


---

## RWWE und RWWV (EPA vorgrwue)

RWWE und RWWV (EPA vorgrwue)
Bezeichnung
Standardwert
Erklärung
Sollen nur Partien mit Bestand
      angezeigt werden.
Nein
Mit
      diesem Einrichterparameter kann Eingestellt werden, ob in der
      Partieauswahl nur Partien mit Bestand angezeigt werden sollen. Im Standard
      werden alle Partien angezeigt.

---

## Einrichterparameter in der Waage

Einrichterparameter in der Waage
Die Einrichterparameter der Waage sind an dieser
Stelle
beschrieben worden.

---

## Kontraktauswahl

Kontraktauswahl
Um Kontrakte in der Waage verwenden zu können, muss
der Einrichterparameter Kontrakt anschließen auf Ja stehen.
Man kann in dem Feld Kontrakt entweder eine
Kontraktnummer oder den Namen des Kontraktekunden eingeben. Die Angaben aus dem
Kontrakt (z.B. Artikel, Kunde) werden nach der Auswahl in die Waagenmaske
übernommen.
Beim Wiegetyp Warenausgang oder Rohwarenausgang werden
bei der
F3-
Auswahl im Feld Kontrakt
nur Kontrakte der Kontraktklassen < 10 angezeigt, beim Eingang nur Kontrakte
der Klassen > 10 und für Lohn/Schüttwiegung Kontrakte aller
Klassen.
Nach der Auswahl von Rohwarenkontrakten auf dem Feld
Kontrakt der Waagenmaske wird das Feld Wiegetyp entsprechend gesetzt, damit die
Rohwarenbelegerzeugung richtig funktioniert.
Bei einem Kontrakt der Kontraktklasse 3
(Verkaufskontrakt Rohware) auf Rohwarenausgang;
bei einem Kontrakt der Kontraktklasse 13
(Einkaufskontrakt Rohware) auf Rohwareneingang.
Anlage eines Kontraktes
Es besteht die Möglichkeit auf der Waagemaske einen
Kontrakt
neu anzulegen. Dazu wird der
Kunde / Lieferant ausgewählt dann muss noch ein Artikel ausgewählt werden und in
das Feld Dispo-Menge wird die Kontraktmenge eingetragen. Dann wird per Funktion
Kontraktauswahl
der Kontrakt als
gesamt Mengen Kontrakt angelegt. Der Kontrakt wird dann automatisch in das Feld
Kontraktnummer auf der Waagemaske übernommen und es wird die erste Zeile in dem
Grid
Kontraktverteilung
vorbelegt.
Hinzufügen eines Artikels zu einem
Kontrakt
Es besteht die Möglichkeit, den Artikel des Kontraktes
zu wechseln, dann wird an den Kontrakt der neue Artikel angefügt. Dazu muss der
Einrichterparameter „Alternativartikel im Kontrakt zulassen“ auf Ja gestellt.
Dann wird beim Speichern der Daten der Artikel in den Kontrakt übernommen.
Artikelauswahl bei Kontraktzuordnung
Im Standard wird die
Itembox 'IB_Kontrakt_Artikel_Waage' verwendet. Diese Itembox wirkt auf dem
Artikelfeld und zeigt alle Kontraktartikel und die Artikel aus der
Kontraktau
[...]


---

## Voreinstellungen

Voreinstellungen
Steuerparameter
Steuerparameter 267
Steuerparameter 379
Steuerparameter 402
Steuerparameter 610
Steuerparameter 615
Steuerparameter 620
Steuerparameter 667
Steuerparameter 690

---

## Ablauf Einrichtung Vorgangstext in Infobox:

Ablauf Einrichtung Vorgangstext in Infobox:
Ziel ist es in der Vorgangs-Info den eingegebenen
Zusatztext im Kopf / Fußbereich anzuzeigen:
Ablauf:
in [
FRM]
Formular ändern z.B. Rechnung 702
Bildschirmbereich = 3
Formulareinrichtung F6
Feld 180 = Vorgangstext Kopf/Fuß positionieren
unter Details als Parameter = interne Bereichsnummer =
Vorgangstextklasse z.B.1001 eintragen
in den SPA’s Vorgangsbearbeitung allgem.
Pos. 45 Vorgangstexte zwangsweise vor Hauptteil auf JA
Ergebnis:

---

## Ablauf Einrichtung Anschriftenfeld:

Ablauf Einrichtung Anschriftenfeld:
1. In den Vorgangsunterklassen
[FRZ]
die
Formular-Nr. für die
Bildschirmeinrichtung
ermitteln.  z.B. 602 Lieferschein
2. In
[FRM]
Formulareinrichtung 602
aufrufen
3. Formularbereich = 4 Bildschirmadresse dann --->
F6 Formulareinrichtung
Einrichtung = Anz = 1, Lg = 10, LR
= 1, Brt = 40
unter
Detail
bei
Hauptadresse eintragen: Dezimalstellen = 3
Varianten
Dezimalstellen:
1 = Lieferscheinadresse (kein Postfach, sondern Straße und PLZ)
2 = Postadresse (ist ein Postfach vorhanden, so wird es
berücksichtigt
3 = 3-zeilige Adresse (für Anzeige in Listen etc. wo einzeilig nicht
reicht
4 = 1-zeilige Adresse (für Listen)
und Varianten Blocklänge:        3
(3-zeilige)
4. SPA-Einstellung ändern
Option global
11 Kundenindividuelle Adressaufbereitung auf JA
5. In Adressmaskierung
[KUAN]
KdMaske-Variante entsprechend ändern
ins Adressfeld gehen und mit F3 die #-Felder
auswählen
Platzhalter $ = fester Platzhalter (es können Lücken
entstehen)
Platzhalter § = variabler Platzhalter (nächster Text
wird
angehängt)
Prüfen im Kundenstamm unter Anschriftenpflege in der
Adress-Maske muss Branchen-ERP default stehen

---

## Abschluss

Abschluss
Bei Abschluss der Kassensitzung werden die
aufgelaufenen Werte dieser Sitzung in die Datenbank übernommen.
Hierzu dient die Funktion (F9), mit der auch das
Display beendet wird.
Je nach Einstellung des Einrichterparameters Abschluss
ohne Zählung möglich muss bzw. kann eine Zählung vorgenommen werden.
Die Möglichkeit, hier Einstellungen vorzunehmen, ist
bedienerklassenindividuell.

---

## Abweichendes Firmenlogo

Abweichendes Firmenlogo
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register abweichendes Firmenlogo
Direktsprung
[ANWR]
.
In den Finanzbuchhaltungs-Reporten wird das im
Mandantenstamm hinterlegte Firmenlogo angezeigt. Zusätzlich kann für jeden
einzelnen Report eine vom Standard abweichende Grafik eingebunden werden. Wählt
man das Register „abweichendes Firmenlogo“ aus und es ist noch keine Grafik
hinterlegt, so öffnet sich ein Filedialog, in dem man die Grafik auswählen kann.
Auf diesem Register wird sie dann angezeigt. Mit der Funktion „Bild entfernen“
kann man das Bild wieder löschen, so dass wieder das Original aus dem
Mandantenstamm angezeigt wird. Sollten in den Reporten keine Grafiken angezeigt
werden liegt es wahrscheinlich daran, dass in den
Optionen
die Grafik abgeschaltet ist.

---

## Ahoi.INI

Ahoi.INI
Steuerdatei zum Aufbau der Datenverbindung und zur
Datenbank.
Die im Windows Verzeichnis hinterlegte Datei kann
verschiedenste Abschnitte enthalten. Jeder Abschnitt repräsentiert einen
„Mandanten“ also eine separate Zugriffsschiene zu einer Datenbank.
Abschnitte
AeinsRoot
Hier
      sollten nur zwei Punkte oder die AeinsRoot eingetragen sein, also
      ..
Database_Connect
Hier
      wird eingetragen, wo die Datenbank zu finden ist, im Mehrplatzfall
      als
eng=aeins;dbf=d:\aeins\daten\awed.db
oder im Einplatzfall
      als
dbf=c:\aeins\daten\xxx.db
User
Hier
      kann die Vorbelegung des Usernamens eingetragen sein
Passwort
Hier
      kann die Vorbelegung des Kennwortes eingetragen sein
Mandantenabschnitt :
[mandant]
Version
Versionsnummer des letzten Updates,
      hieran wird entschieden, ob es den losgehen soll mit einem
      Datenbankupdate.
Lizenznehmer
Lizenzinformationen
Seriennummer
Die
      Seriennummer
Lizenz
Die
      Lizenznummer

---

## Dashboard

Dashboard
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Auf AIS-Masken besteht die Möglichkeit ein oder
mehrere
Dashboards
[DASH]
darzustellen. Dabei können Dashboards
ausschließlich
auf AEZADDON…-Masken eingerichtet werden.
Voraussetzung:
Es wird eine Dashboard-Lizenz benötigt.
Einrichtung
Um ein Dashboard einzurichten, ist ein neues Feld mit
dem Feldtyp „Dashboard“ anzulegen. In dem Feld „Dashboard-Id“ wird angegeben,
welches Dashboard angezeigt werden soll. Hier kann über eine F3-Auswahl eine
Dashboard-Id ausgewählt werden. Alternativ kann hier statt einer Dashboard-Id
auch der Name eines Feldes eingetragen werden, aus dem die Dashboard-Id
ausgelesen werden soll. Wird in diesem Feld eine Dashboard-Id gesetzt bzw.
geändert, so wird direkt das entsprechende Dashboard aktualisiert.
Funktionen
Auf den Dashboards der AIS-Masken stehen die gleichen
Funktionalitäten wie auf den Dashboards im Hauptmenü zur Verfügung. So öffnet
sich beispielsweise beim Rechtsklick auf das Dashboard ein Menü, über das das
Dashboard und die Kacheln aktualisiert oder bearbeitet werden können.
Automatische Aktualisieren einer Kachel oder
eines Dashboards
Das Aktualisieren einer Kachel oder eines Dashboards
kann nicht nur über eine Menü-Funktion erfolgen, sondern auch von einem Makro
angestoßen werden. Hierzu stehen folgende Funktionen zur Verfügung:
Aktualisieren eines Dashboards:
^dbx_io("AISREFRESH_DASHBOARD",
"Dashboardfeldname")
Aktualisieren einer Kachel:
^dbx_io("AISREFRESH_KACHEL",
"Dashboardfeldname", "KachelId")

---

## AIS-Einrichtung

AIS-Einrichtung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Alle Felder des AIS werden in sogenannten Gruppen
zusammengefasst. Über diese Gruppen werden sie später den Erfassungsmasken bzw.
den Registern zugeordnet. Die Länge ist auf 30 Zeichen beschränkt, da das
Maskenwerkzeug für die Namensvergabe von Maskenfeldern eine maximale Länge von
31 Zeichen zulässt. Die externe Bezeichnung des Registers wird in der
Maskenzuordnung unter „Bezeichnung/Register“ angegeben.
Jeder dieser Gruppen kann ein Screen-Makro bzw. ein
Feld-Makro zugeordnet werden. Das Feld-Makro übernimmt die
Eingabeprüfung
auf Feldebene. Das
Screen-Makro kann für den Ändern- bzw. im Neu-Fall Vorlauffunktionen enthalten
sowie eine Funktion „Prüfung vor speichern“, die aufgerufen wird bevor die Daten
gespeichert werden und in der man den Speichervorgang noch abbrechen kann. Diese
werden in „
Ändern Vorlauf
“, „
Einfügen Vorlauf
“ bzw.
in „
Prüf. Vor Speichern
“ festgelegt.
Ist kein Screen-Makro angegeben werden diese Funktionen aus
kompatibilitätsgründen aus dem Feld-Makro gelesen.
ACHTUNG:
Wird die Refresh-Funktionalität
verwendet, so müssen die Funktionen für „
Ändern Vorlauf
“ und „
Einfügen
Vorlauf
“ immer im Screen-Makro enthalten sein.
Hinweis:
Wird ein Makro 2.0 (C#) als Screenmakro angegeben, so
entfällt die Angabe der Funktionsnamen („Ändern Vorlauf“, „Einfügen Vorlauf“,
„Prüf. Vor Speichern“).
Die Methoden ergeben sich aus dem AISMakro-Interface
Ändern Vorlauf:
Die hier angegebene Funktion wird im Ändern-Modus
immer dann aufgerufen, nachdem der nächste Datensatz auf dem Bildschirm
dargestellt wurde. Man kann dann diese Funktion nutzen, um z.B. um eigenständige
Werte zu errechnen. Die Funktion muss folgenden Aufbau haben. Der übergebene
Parameter ist der Maskenname:
function OnUpdateEntry
(Maskenname:string ):integer;
begin
MessageBox ( "Nach dem laden der Daten", "Ändern
Vorlauf", 1 );
OnUpdateEntry:=0;
end;
Einfügen Vorlauf:
Diese Funktion w
[...]


---

## Aktivitäten

Aktivitäten
In den Aktivitäten kann man die ToDos des Benutzers,
bezogen auf die Firma, einsehen.

---

## Amicconf.INI

Amicconf.INI
Diese Datei ist eine Zentrale INI Datei. Alle
Einrichtungen, die in der lokalen INI Datei (AHOI.INI) nicht gefunden werden,
werden aus dieser Datei "gelesen".

---

## Ansicht

Ansicht
Links an der Seite findet man eine Auflistung aller
Firmen und Personen, welche dem Benutzer über das App Portal freigegeben
wurden.
Ansicht Firma
Ansicht Person

---

## Arbeitsstation/Client - Einrichtung

Arbeitsstation/Client - Einrichtung
Das Setup-Programm stellt die technische Verfügbarkeit
auf den Clienten her.
Beim Start von Referenz-ERP wird die ODBC-Einrichtung des
Mandanten in HKEY_CURRENT_USER\Software\ODBC\ODBC.INI eingepflegt.
Damit wird der Einsatz von
1)
Aeins-Crystal-Report,
2)
Crystal-Report-Direktanwendungen
vorbereitet und unterstützt.
Der Name des Schlüssels für den ODBC-Eintrag ergibt
sich durch den Wert des Referenz-ERP-Parameters „
crw_login_info
“.
Ist
keine explizite Angabe dieses Parameters erfolgt, dann ist es in aller Regel der
Name des Mandanten aus den zugehörigen Inis (Stichwort: [Mandantenname]).
Folgende Setzungen erfolgen:
Registry-Schlüssel
Vorbelegung erfolgt durch
      Aeins-Parameter
Standard-Wert
Uid
odbc_admin_name
(**)
Pwd
odbc_admin_pass
(**)
Autostop
odbc_autostop
No
CommLinks
odbc_commlinks
Wert
      des Referenz-ERP-Parameters „Links“ (*)
Driver
odbc_driver
Wert
      des Referenz-ERP-Parameters „sybase_odbc“
DatabaseName
Dbn
(*)
DatabaseFile
Dbf
(*)
EngineName
Eng
(*)
Description(***)
Programm_name
(*)
Diese „Standard-Werte“ werden intern –
falls nicht extra vorgegeben – aus dem „Database_Connect“-Parameter
ermittelt.
(**)
a)
Das Einsatzgebiet 1) pflegt die Daten zur Laufzeit und ist nicht funktional
abhängig von diesen Einträgen.
b)
Das Einsatzgebiet 2) wird standardmäßig durch die Pflege der Registry-Schlüssel
mit Standardwerten unterstützt. Ist das aus sicherheitstechnischen Gründen
unerwünscht, kann das durch individuelle Steuerung der Referenz-ERP-Parameter
odbc_admin_name/odbc_admin_pass erreicht werden.
Durch geeignete
odbc_admin_pass - Vorgabe lässt sich administrativ erreichen, dass die von
Referenz-ERP erzeugte ODBC-Einrichtung nicht unmittelbar verwendet werden
kann!
Der Referenz-ERP-Parameter „
odbchelper
=FALSE“
schaltet die gesamte Pflege der ODBC-Einrichtung des Mandanten
grundsätzlich ab und sollte nur in Spezialfällen von Nöten sein.
(***)
Die Pflege der ODBC-Einrichtung erfolgt nur, wenn sich
die „Description“ im
[...]


---

## Arbeitsstations- Setup

Arbeitsstations- Setup
Die einzelnen Arbeitsstationen, welche auf das Referenz-ERP
System zugreifen, benötigen auch ein Versionsupdate, wenn eine neue Version in
das System eingespielt worden ist. Dieser Umstellungsprozess muss unter
Administratorrechten direkt auf dem Arbeitsplatz durchgeführt werden, dazu ist
das Standard Setup Programm aus dem Setup Verzeichnis aufzurufen.

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
      Archivierungsprobleme wird man nicht über eine Meldung hingewiesen,
      sondern sie werden ins Fehler-/Ereignisprotokoll eingetragen
Archivieren, jedoch nicht
      drucken
Das
      Formular wird im Formulararchiv abgelegt, jedoch nicht gedruckt.
Mailversand
      ohne Druck
Das
      Formular wird im Formulararchiv abgelegt und per E-Mail versandt, jedoch
      nicht gedruckt.
Mailversand
      muss eingerichtet sein!
Mailversand
      mit Druck
Das
      Formular wird im Formulararchiv abgelegt, per E-Mail und
      gedruckt.
Mailversand
      muss eingerichtet sein!

---

## Archiv-Import über JPP-Methode Free_Import

Archiv-Import über JPP-Methode Free_Import
Die Aufgabe der JPP-Methode Free_Import aus dem
JPP-Objekt JFA_Import ist es Dateien gemäß den in
FAI einrichtbaren Import-Profilen
in das Archiv zu
verbringen.
Diese Methode wird von diversen Aeins-internen
Applikationen aufgerufen, u.a. Mandantenserver (Profile mit
Automatik-Kennzeichnung), aber auch Abwicklungen in den „Bereichen“ FAI und
FAA.
Im Mandantenserver-Betrieb werden automatisch die
Schalter „Protokoll“  und „Start-Abfrage“ auf „Nein“ gesetzt.
Parameter:
fai_id
Pflichtfeld
„Schlüssel“ der Relation fa_import
fai_pfad
Optional
Standard: …
Ist
      dieser Pfad angegeben und ungleich …, so überschreibt dieser Wert die
      Profil-Vorgabe fai_pfad.
Unterstützt werden hier JVARS, d.h.
      es wird zur Laufzeit der Methode der Inhalt einer JVAR herangezogen. Ein
      Beispiel für die Syntax ist: @jvars(5004,userpath)
receiver
Optional
Standard: …
mandser
Optional
Standard: FALSE
olderas
Obsolete
Versorgung über das Feld „Wartezeit
      in Minuten“
Siehe im gleichen Zusammenhang auch die nun mögliche
      Parametrisierung „Max. Anzahl pro Durchlauf“

---

## Archiveinrichtung für Beleg-Mailversand

Archiveinrichtung für Beleg-Mailversand
Zum Versenden von Belegen per E-Mail muss das
Formulararchiv eingerichtet sein. Im
„Formulararchiv Manager“ [FAM]
muss der Wert
„Archivieren“ auf „Ja“ und das „Ziel“ auf „Datenbank“ stehen. Des Weiteren
sollte das Ausgabeformat für „Vorgangs-Druck“ auf „PDF“ stehen, da ansonsten
nicht „vermailt“ werden kann.
Der Beleg wird im Archiv als PDF abgelegt und kann
beim Versand von dort gelesen werden.

---

## ASK Statement

ASK Statement
Syntax
ASK
Beschreibung>VARIABLE[,Beschreibung>Variable[,….]];
Purpose
Interaktive Abfrage von Parametern.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
ASKJN, Parameter, Variablen , Envirenmentvariable
Beschreibung
Mit dem ASK Statement können Variablen für die
Benutzung innerhalb einer Kommandodatei abgefragt werden. Es sind maximal 10
Variablen erlaubt.
Ein zweites ASK Statement löscht alle bis zu diesem
Punkt existierenden
Variablen. Drück man den Abbruchbutton beim
ASK-Statement innerhalb einer Kommandodatei, wird diese beendet.
Beispiel
ASK
Belegnr>BNR,Jahrnummer>JNR;
MSG Suchen nach Belegnumer :BNR im Jahr
:JNR;
Select * from fibuvorgposition where
Jahrnummer=:JNR and FiBuV_Nummer=’:BNR’;

---

## ASKJN Statement

ASKJN Statement
Syntax
ASKJN Beschreibungstext;
Purpose
Interaktive Ja/Nein Abfrage.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
ASK
Beschreibung
Mit dem ASKJN Statement kann die Standartdialogbox
aufgerufen werden, um eine Benutzerabfrage durchzuführen.  Die Variable
LDB_JN enthält je nach Auswahl den Wert 1 für JA oder 2 für NEIN.  Drück
man den Abbruchbutton beim ASKJN-Statement innerhalb einer Kommandodatei, wird
diese beendet.
Beispiel
ASKJN Drück aufs Knöpfchen, Max;
if(val(LDB_JN)==1)
{
PAUSE Max hat Ja gedrückt!;
};
if(val(LDB_JN)==2)
{
PAUSE Max hat Nein
gedrückt!;
};
PAUSE Abbruch kommt hier nie
an;

---

## Aufbau eines automatischen DATA-Refresh Systems

Aufbau eines automatischen
DATA-Refresh Systems
Es ist sehr angenehm, wenn beim Öffnen einer BI
Anwendung diese auch sofort die Daten aktualisiert. Per Standard wird dieses
nicht eingestellt. Innerhalb des Verbindungsmanagers der Excel Anwendung kann
nun aber eine Einrichtung vorgenommen werden, die eine automatische
Aktualisierung erlaubt.
Es sind hier die Felder
•
Aktualisierung im Hintergrund zulassen
•
Aktualisierung alle … Minuten
•
Aktualisierung beim Öffnen der Datei
•
Daten vor dem Speichern entfernen
•
Bei „Alle Aktualisieren“ mit berücksichtigen
zu pflegen:
Im Anschluss an die Änderung dieser Werte ist die
Excel Datei auf jeden Fall wieder in die Datenbank
zurückzuspeichern
.

---

## Auslandzahlungsverkehr in Referenz-ERP

Auslandzahlungsverkehr in
Referenz-ERP
Der Auslandszahlungsverkehr wird wie der normale
Zahlungsverkehr gesteuert und wird per Lizenz aktiviert. Es sind jedoch ein paar
zusätzliche Stammdaten zu verwalten.
Änderungen gültig ab 1.05.2005
Der Weisungsschlüssel ‚01’ (=’BONL’) ist
entfallen
•
Die AWV-Meldung für Zahlungen über Wertpapiergeschäfte muss jetzt auf
Vordruck Z10 oder mit entsprechenden Datensätzen erfolgen.
•
Der Weisungsschlüssel ‚95’ ist entfallen. Die Beträge in den
Meldedatensätzen werden weiterhin stets in Auftragswährung, bei
Euro-Gegenwertzahlung in Euro angegeben.
•
Die Liste der zulässigen Länder für EU-Standardüberweisungen wurde
erweitert um Island, Lichtenstein und Norwegen.
Änderungen gültig ab 1.01.2006
•
Anhebung der Betragsgrenze für EU-Standardüberweisung von 12.500 Euro auf
50.000 Euro.
•
Änderung des Meldeverfahrens für EU-Standardüberweisungen

---

## Auswahlliste ScriptParameter

Auswahlliste ScriptParameter
Die Auswahlliste
ScriptParameter
zeigt die
Kopfsätze der Scriptparameter-Sätze an. Jede Gruppe von Scriptparametern (alle
Parameter für ein spezielles Script) wird durch einen Kopfsatz
repräsentiert.
Der Aufruf des Einstieges in die Anwendung
ScriptParameter
erfolgt durch den
Direktsprung [SCPA]
.
Die Varianten dieser Auswahlliste sind
Script-Parameter
und
*** System-Script-Parameter.
Letztere
Variante steht nur ENTWICKLERN zur Verfügung.
Die
Option-Box
stellt folgende Funktionalitäten
bereit:
Aufruf des
Pflegers
zur Neuerfassung, Änderung,
Ansicht und Löschung von Kopfsätzen (Löschen lässt sich ein Kopfsatz  nur,
wenn es keinen Detailsatz gibt. Zum Löschen inklusive aller Detailsätze steht
dem Support die unten beschriebene Funktion
** Mit Details löschen
zur
Verfügung.
PId:
ParameterId. Hier ist eine Eindeutige
Kurzbezeichnung anzugeben, anhand derer die Parametersätze von einem Script aus
angesprochen werden können. Diese PId muß bei privaten Parametersätzen immer mit
“p_” beginnen!
Bezeichnung:
Eine Klartextbeschreibung der
Parametersammlung
Besitzer:
0: allgemeiner öffentlicher
Parametersatz; 1: privater Parametersatz
(Anmerkung: Durch restriktive Sicherheitsvorkehrungen
können im Normalbetrieb nur private Parametersätze bearbeitet werden, und dies
auch nur durch besonders berechtigte Bediener)
BedKorr:
BedienerId desjenigen Bedieners, der
zuletzt Änderungen am Datensatz durchgeführt hat. (wird automatisch belegt).
System:
System-Kennzeichen, 0: nicht gesetzt;
1: gesetzt.
Datensätze mit gesetztem System-Kennzeichen können nur
herstellerseitig im Hause Branchen-ERP bearbeitet werden.
Verzweigung in die detaillierte Darstellung der
einzelnen Parameter-Datensätze zu einem markierten Kopfsatz (Auswahlliste
ScriptParameterDetails
) s. u.
Ausdruck
einer Crystal-Reports-Liste der
Script-Parameter
Reportdatei ist
SCPARAM.RPT
.
** Duplikat erzeugen.
Diese Funktion steht nur
Benutzern mit Mindestberechtigung Support zur Verfügung
[...]


---

## Auswahlliste ScriptParameterDetails

Auswahlliste ScriptParameterDetails
Die Auswahlliste
ScriptParameterDetails
zeigt
die Detailsätze der Scriptparameter zu einem markierten Kopfsatz an. Die Anzeige
erfolgt getrennt nach Typ der Parameter. Folgende Parametertypen sind z. Zt.
vorgesehen:
0: allgemeine Parameter
1: Konvertierungsparameter
2: Positionsparameter
Dieser Parametertypen werden in Zusammenhang mit dem
Pfleger (weiter unten) erläutert.
Jeder Datensatz repräsentiert einen Parameter. Genau
genommen können bis zu 3 Werte und zusätzlich ein Gültigkeitskennzeichen (Aktiv)
aus einem Datensatz gewonnen werden. Je nach Typ eines Datensatzes haben die 3
Werte konventionsmäßig unterschiedliche Bedeutung, dazu Näheres weiter
unten.
Die
Option-Box
stellt folgende Funktionalitäten
bereit:
Aufruf des
Pflegers
zur Neuerfassung, Änderung,
Ansicht und Löschung von Detailsätzen
Im Kopfteil werden Informationen aus dem Kopfsatz
angezeigt (nicht änderbar).
PPId:
Id des Detailsatzes. Hier ist eine
Eindeutige Kurzbezeichnung anzugeben anhand derer der Datensatz von einem Script
aus angesprochen werden kann.
PPBezeichnung:
Eine Klartextbeschreibung des
Parameters

---

## Automatische Rabatte

Automatische Rabatte
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Ein Rabatt errechnet sich aus einer Kombination aus
Artikel und Kunden.
Damit automatische Berechnung der Rabatte jedoch
erfolgt, muss diese im Steuerungsparameter
60 - Automatische Rabatte
eingeschaltet sein.

---

## Automatische Frachten

Automatische Frachten
Administration
Steuerung
Steuerungsparameter zeigen
[SPA]
Eine Fracht errechnet sich aus einer Kombination aus
Artikel und Kunden.
Damit automatische Berechnung der Rabatte jedoch
erfolgt, muss diese im Steuerungsparameter
184 – automatische Frachten
eingeschaltet sein.

---

## Automatische Zu-/Abschläge

Automatische Zu-/Abschläge
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Ein Zu-/Abschlag errechnet sich aus einer Kombination
aus Artikel und Kunden.
Damit automatische Berechnung der Rabatte jedoch
erfolgt, muss diese im Steuerungsparameter
33 – Automatische Zu-/Abschläge
eingeschaltet sein.

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
•
Datenträgernummer (VOL-Nummer)
•
Dateiname: DTAZV

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
insert into zt ( z, zt ) values ( 6, 'szesc'
);
insert into zt ( z, zt ) values ( 7, 'siedem' );
insert
into zt ( z, zt ) values ( 8, 'osiem' );
insert into zt ( z, zt )
values ( 9, 'dziewiec' );
insert into zt ( z, zt ) values ( 10,
'dziesiec' );
insert into zt ( z, zt ) values ( 11, 'jedenascie'
);
insert into zt ( z, zt ) values ( 12, 'dwanascie' );
insert
into zt ( z, zt ) values ( 13, 'trzynascie' );
insert into zt ( z, zt )
values ( 14, 'czternascie' );
insert into zt ( z, zt ) values ( 15,
'pietnascie' );
insert into zt ( z, zt ) values ( 16, 'szesnascie'
);
insert into zt ( z, zt ) values ( 17, 'siedemnascie'
);
insert into zt ( z, zt ) values ( 18, 'osiemnascie'
);
insert into zt ( z, zt ) values ( 19, 'dziewietnascie'
);
insert into zt ( z, zt ) values ( 20, 'dwadziescia'
);
insert into zt ( z, zt ) values ( 30, 'trzydziesci'
);
insert into zt ( z, zt ) values ( 40, 'czterdziesci'
);
insert into zt ( z, zt ) values ( 50, 'piecdziesiat'
);
insert into zt ( z, zt ) values ( 60, 'szescdziesiat'
);
ins
[...]


---

## Beispiel Darstellung eines Bildes

Beispiel Darstellung eines
Bildes
Hauptmenü
Administration
Werkzeuge
Informationssystem
Variante Informationssystem
Direktsprung
[AIS]
Man kann Bilder aus der Tabelle Bitimages einfach auf
einer Maske darstellen. Hier wird kurz gezeigt, wie man ein Feld einrichten
muss, damit auf dem Pfleger für Artikel das zugeordnete Bild auf einem der
Register zu sehen ist.
Im Referenz-ERP Informationssystem in der Variante
Informationssystem legt man sich einen neuen Eintrag (
F8
) an. Zuerst muss
die Gruppe angegeben werden. Hat man bereits ein oder mehrere Felder zu einer
Gruppe erfasst, kann man diese hier mit
F3
auswählen. Die Felder
„
Makro
“, „
Ändern Vorlauf
“ und „
Einfügen Vorlauf
“ werden
dann vorbelegt.
Um ein Bild des Artikels darzustellen, sind einige
Einträge Notwendig. Der Name der Gruppe soll
Artikelbild
lauten.
Register Feldbeschreibung:
Beschreibung
Feldname
Auch
      für Label, die nicht aus der Datenbank gefüllt werden, müssen Feldnamen
      vergeben werden. Hier muss der Label den Namen des Feldes aus der Tabelle
      Artikel erhalten, der die Imageid enthält:
Artikelimage
Feldtyp
Der
      Feldtyp für die Imageid muss natürlich
Label
sein.
Datenformat
Image
Zeile und Spalte
Die
      Position kann entweder über ein Raster oder pixelgenau angegeben werden.
      Sollen es Pixel sein, so ist ein kleines p an die Zahl anzuhängen (z.B.:
      125p). In unserem Beispiel sollen die Felder sich am Raster orientieren,
      also Spalte 1 und Zeile 1.
Länge
Wie
      viel Zeichen darf der Label lang sein. Die Länge ist relativ unwichtig, da
      das Bild immer so groß dargestellt wird, wie es ist.
Tipptext
Ist
      ein Hinweistext, der erscheint, wenn der Mauszeiger über diesem Feld
      steht. Wenn er leer gelassen wird, so wird der Text
„Mit Doppelklick zum Bild
      bearbeiten…“
eingeblendet.
Register Datenbeschreibung:
Beschreibung
Herkunftstyp
Relation
Relation/Prozedur
Artikel
Ident Feld
Artikelid
Zum lesen des Daten wird aus diesen Inf
[...]


---

## Beispiele für Datenbankfunktionen

Beispiele für
Datenbankfunktionen
Beispiel für eine Datenbankfunktion für die
Partieverteilung:
CREATE PROCEDURE
"admin"."p_PartieAutoSuche"
(
-- Die Parameter wurden
automatisch mit der  Einrichtung unter FRZ/Partie/DB Prozedur für
Verteilung
-- zusammengestellt( Cursor im
Feld DB Prozedur für Verteilung positionieren, SF8, Parameter auswählen /
Testfunktion ausführen)
in
in_Vorgangsklasse   integer
, in in_Unterklasse
integer
, in in_VerteilMenge   numeric
(15,6)
, in in_Mengeneinheit
integer
, in in_ArtikelId
integer
, in in_KundId   integer
, in in_EKVK_kennzeichen
integer
, in in_AbgrenzDatum   date
, in in_ArtikelStammId
integer
, in in_NurDiesePartie_Id
integer
, in in_LagerPLatzNummer
integer
)
-- Das Resultset muss mindestens die hier aufgeführten
Felder haben. Die Reihenfolge
-- ist nicht wichtig - die Namensgebung aber um so mehr
!
-- eine eine Zurückgegeben zeile entspricht einer
Partiezuordnung
-- es können mehrere, eine oder auch keine Zeilen
zurückgegeben werden
result
(
PartieId
integer,
-- Die Partieid ist absolut wichtig
PartieNummer integer,
PartieBezeich char(40),
PartieAbdatum date,
PartieEKP_Kennz
smallint,            --
wichtige Kennzeichen für die Partiepreisermittlung
PartieVKP_Kennz
smallint,            --
dito
WaehrNummer
smallint,
-- in welcher Währung wird die Partie geführt
Me_NummerPartie
integer,
-- die Mengeneinheit der Partiebestandsbuchführung
PartieArtiPosit
integer,
-- wichtig für die eindeutige Identifiziere des Artikels in der Partie
LagerplatzNummer
integer,            --
von welchem Lagerplatz soll abgebucht werden
sort_lagerplatz
integer,
-- Hilfsfeld zum Sortieren eigenen und fremden Lagerplätze ( zum Lagerplatz der
Warenposition)
RestMenge_VK numeric(15,4
)          -- Benennung dieses
Feldes ist historisch gewachsen. Es gibt sowohl bei Einkauf als auch
-- bei Verkauf die zugeordnete Menge dieser Pa
[...]


---

## Bekannte bzw. gelöste Problembereiche

Bekannte bzw. gelöste Problembereiche
Die bisher umgestellten Datenbanken haben folgende
Probleme gezeigt:
-
Benutzereinrichtungen im Rollenbereich der Sybase 12 besitzen
Fremdserverzuordnung.
o
Hier handelt es sich um
fehleingerichtete Zuordnungen zu Sybase Elementen, die nicht korrekt in der
Datenbankstruktur hinterlegt sind, diese Fehlstrukturen werden entfernt.
-
View Einrichtungen, die veraltet sind
o
Es kommt immer wieder vor,
dass eine Datenbankview auf veraltete Informationen zugreifen möchte, die eine
korrekte Ausführung der View nicht zulässt. View, die als „veraltet“ erkannt
werden, werden aus dem System entfernt. Es gibt hierzu entsprechende
Fehlerprotokolleinträge.

---

## Belegfluss Postfacheinrichtungspfleger

Belegfluss Postfacheinrichtungspfleger
Name
Beschreibung
Postfach
ID +
      Name des Postfachs
Nummernkreis
Der
      Nummernkreis für die Finanzbelegerfassung
Finanzbelegerfassung
Bestimmt, ob die OB-Funktion
      Finanzbelegerfassung zur Verfügung steht.
Anzahl Direktbuchungen
Gibt
      die Anzahl der Buchungen bei Direkt- Finanzbelegerfassung an. Die Funktion
      wird ausgeblendet, wenn die Anzahl gleich null ist.
Beleg-Freigabe erlaubt?
Steht das Feld „Beleg-Freigabe
      erlaubt?“ auf „Ja“, so kann im Belegfluss die Zuordnung eines Beleges zum
      Belegfluss entfernt werden (siehe
Belegzuordnung
      entfernen
)
.
Eingangslieferscheinklasse
      (Unterklasse)
Vorgangsnummer + Unterklasse
      (optional)
Sollte auf 1600 gestellt
      werden.
Eingangsrechnungsklasse
      (Unterklasse)
Vorgangsnummer + Unterklasse
      (optional)
Sollte auf 1700 gestellt
      werden.
Eingangsgutschriftsklasse
      (Unterklasse)
Vorgangsnummer + Unterklasse
      (optional)
Sollte auf 1800 gestellt
      werden.
Belegflusshistorie
Prozedur. Standard:
      BelegflussHistorie
Belegflussbemerkung
Prozedur. Standard:
      BelegflussBemerkung
Anforderung
Prozedur. Standard:
      BelegflussZeigeAnforderung
Wenn
      keine Prozedur angegeben ist, wird der Bereich ausgeblendet. Es wird
      empfohlen entweder Anforderung oder Genehmigung in einem Postfach zu
      nutzen.
Genehmigung
Prozedur. Standard:
      BelegflussZeigeGenehmigung
Wenn
      keine Prozedur angegeben ist, wird der Bereich ausgeblendet. Es wird
      empfohlen entweder Anforderung oder Genehmigung in einem Postfach zu
      nutzen.
Verarbeitung
Prozedur. Standard:
      BelegflussGenehmigung
In
      dieser Prozedur wird die Logik des Systems definiert.
(Unter welchen Bedingungen bewegt
      sich ein Dokument in welches Postfach weiter)
Direkt-Finanzbelegerfassung
Prozedur für die
      Direkt-Finanzbelegerfassung.
Standardprozedur:
      BelegFluss_Direktbuchung
cre
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

## Belegmappen

Belegmappen
Man kann Belege, die in der Belegerfassung erfasst
werden, sofort sogenannten Belegmappen zuordnen. Um dieses Feature zu benutzen,
muss in der
Belegerfassung
der
Einrichterparameter „Belegmappe abfragen“ gesetzt werden. Dieser
Einrichterparameter hat folgende Ausprägungen:
•
Nicht aktiv
. Belegmappe wird nicht abgefragt bzw. angezeigt. Dies
ist die Standardeinstellung.
•
Belegmappe einmal zentral abfragen
. Die Belegmappe wird nur einmal
im Periodenabfragefenster abgefragt.
•
Belegmappe in der Belegerfassung abfragen
. Man hat in der
Belegerfassungsmaske zusätzlich die Möglichkeit die Belegmappe zu ändern.
Eine Belegmappe bildet sich automatisch neu, sobald
mindestens ein Beleg in der Mappe existiert. Eine
F8
Funktion für NEU gibt es bewusst nicht.
Die Zuordnung zu einer Belegmappe kann zusätzlich
auf folgende Art und Weise geschehen:
•
durch nachträgliches zuordnen der Belege in der Einzelbeleganzeige. Dort
stehen die Funktionen „Belegmappe zuordnen“ und „Belegmappe entfernen“ zur
Verfügung. Es kann hier der Beleg nur einer existierenden Mappe zugeordnet
werden.
•
In der Anwendung „Standardvorgänge Fibu“ über die Funktion „Belegmappe
zuordnen“. Dort wird in einer Maske die Belegmappe abgefragt und alle
ausgewählten Belege werden dieser Mappe zugeordnet. Dies kann eine neue Mappe
oder eine bestehende Mappe sein. Vor der Zuordnung wird noch geprüft, ob die
Mappe existiert und man kann hier ggf. noch abbrechen. Da Belege nur einer Mappe
zugeordnet werden können, wird auch geprüft, ob Belege mit einer anderen
Mappenzuordnung ausgewählt wurden. Man hat dann die Möglichkeit abzubrechen oder
die Belege der neuen Mappe zuzuordnen.
•
Bei den
periodischen
Buchungen
.
•
in der Anwendung Währungsabgrenzung.
Ein Beleg kann nur einer Belegmappe zugeordnet werden.
In den Anwendungen „Standardvorgänge FIBU“, „Primanota“ und „Belegmappen“ kann
die Auswahl zusätzlich nach diesen Mappen erfolgen. Hier kann mit
F3
eine
der angelegten Mappen ausgewähl
[...]


---

## Belegnummer

Belegnummer
In diesem Feld steht die Rechnungsnummer. Sie wird
automatisch aus dem zugeordneten Nummernkreis übernommen.
Es gibt zwei Wege, die Vergabe der Rechnungsnummer zu
organisieren:
automatische Vergabe
Sinn ist es, die Nummern lückenlos vom Programm
hochzählen zu lassen. Jede Vorgangsart hat ihren eigenen Nummernkreis. Die
Pflege der Nummernkreise erfolgt in den Programmkonstanten.
manuelle Vergabe
Die Rechnungsnummer wird vom Anwender selbst vergeben,
um
Rechnungen nachträglich selbst zu erfassen,
Rechnungen nach vorbereiteten Unterlagen mit fertigen
Nummern zu erfassen.
Sowohl die vorgeschlagene Rechnungsnummer als auch das
Rechnungsdatum und die Periodenzuordnung können bei der Erfassung überschrieben
werden. Nach Erfassung des Kunden wird hierzu mittels ↑↓ in das Rechnungsnummer
- Feld positioniert und die gewünschte Nummer eingegeben.
Bitte beachten Sie, dass der Rechnungsnummer (neben
Kundennummer und Rech­nungsdatum) eine zentrale Bedeutung in der
Organisation zukommt. Innerhalb des Programms dient die Rechnungsnummer als
Auswahl- und Sortierkriterium.
Beispiele:
Der Ausdruck des Rechnungsausgangsbuches kann nach
Rechnungsnummern erfolgen.
In die Finanzbuchhaltung kann ein ausgewählter
Rechnungsnummernbereich übertragen werden.
Offene Posten werden anhand von Rechnungsnummern
verwaltet und bei Bezahlung ausgeziffert.
Rechts neben der Rechnungsnummer wird angezeigt,
welcher Belegnummernkreis zugrunde liegt (hier “Rechnungen”).
Die Belegnummern werden lückenlos vergeben. Werden
Nummern, z.B. durch Stor­nierung des Beleges, wieder frei, so werden sie in
einer Reserveliste vermerkt, und bei Bedarf wieder verwendet.
Periode/Jahr
Dies ist die aktuelle Buchungsperiode. Sie wird
entsprechend der Systemeinstellung vorgeschlagen. Wenn jedoch eine andere
Buchungsperiode gewünscht wird, so muss sie hier eingegeben werden.
Datum
Im Feld Datum wird das Rechnungsdatum erfragt. Es ist
vorbelegt mit dem Tagesdatum. Werden Rechnungen mit zeitlicher
[...]


---

## Benutzerschnittstelle (Waagen-Schnittstelle)

Benutzerschnittstelle (Waagen-Schnittstelle)
Die Benutzerschnittstelle ist realisiert durch die
Anwendungen
ScriptParameter
und
ScriptParameterDetails
.

---

## Benutzte Relation und Datenbankfunktionen

Benutzte Relation und Datenbankfunktionen
Eine kleine Übersicht und Beschreibung von den
benutzten Relationen und Prozeduren, die von unserem System ausgeliefert
werden.
Relationen
Kurzbeschreibung
Mandant
mms_transfer_speicher
Zwischenrelation für das Einspielen
      der Daten in die Untermandanten
Zentralmandant
mms_transfer
Proxy Tabelle für die zu
      Importierenden Daten
Untermandant
mms_transferzwischenspeicher
Speichert den Altertablebefehl ab,
      wenn das Ändern ein Tabelle nicht funktioniert hat
Untermandant
tabellenstruktur
Temporäre Tabelle für das öffnen und
      verarbeiten der XML Daten
Untermandant
mms_transfer_tabellen
Diese Relation enthält die Namen der
      Prozeduren oder Views, die auf eine der Relationen im MMS System wirkt.
Untermandant
Prozeduren
Kurzbeschreibung
Mandant
ArtikelExportXML
Sammelt die ganze Artikel
      Informationen aus den Relationen oder den Privaten Views und speichert die
      Daten als XML File in der Proxy Tabelle mms_transfer ab
Zentralmandant
ArtikelImportXML
Öffnet das XML Objekt welches in
      mms_transfer liegt, kümmert sich um die Umschlüsselung, sorgt dafür dass
      die Daten durch die XMLEinfügeprozedur in das System gespielt
      werden.
Untermandant
FruchtartExportXML.sql
Sammelt die ganze Artikel
      Informationen aus den Relationen oder den Privaten Views und speichert die
      Daten als XML File in der Proxy Tabelle mms_transfer ab
Zentralmandant
FruchtartImportXML.sql
Öffnet das XML Objekt welches in
      mms_transfer liegt, kümmert sich um die Umschlüsselung, sorgt dafür dass
      die Daten durch die XMLEinfügeprozedur in das System gespielt
      werden.
Untermandant
GruppenExportXML.sql
Sammelt die ganze Artikel
      Informationen aus den Relationen oder den Privaten Views und speichert die
      Daten als XML File in der Proxy Tabelle mms_transfer ab
Zentralmandant
GruppenImportXML.sql
Öffnet das XML Objekt welches in
      mms_transfer liegt, kümmert sich um die
[...]


---

## Überblick Mitgliederverwaltung

Überblick Mitgliederverwaltung
Das vorliegende Modul ist lizenzpflichtig und nur
aktivierbar, wenn die entsprechenden Lizenzen eingetragen sind.
Genossenschaften und andere Gesellschaften mit vielen
Mitgliedern sind zur Verwaltung der Geschäftsanteile verpflichtet. Hierzu dient
die im Folgenden beschriebene Gesellschafter- / Mitgliedsverwaltung.
Aufgrund der aktuellen Anforderungen wurde ein Modell
realisiert, welches über den Ansatz innerhalb der X-Com Familie hinausgeht. Der
wesentliche Unterschied besteht darin, dass die Verwaltung eines Kontos auf der
Basis der historischen Bewegungen erfolgen soll. Zudem soll auf die Führung von
eigenen GG – Konten aus Gründen der Übersichtlichkeit verzichtet werden.
Hieraus ergeben sich einige Grundüberlegungen:
Ein Bilanzkonto ( BK ) stellt den Wert der
eingezahlten Beträge dar.
GG – Transaktionen (Ein - / Auszahlungen) laufen über
Kundenkonto zu BK.
Die Verfolgung aus Sicht des Personenkontos stellt die
kompletten Einträge dar.
Die Verfolgung aus Sicht BK stellt alle Transaktionen
dar.
Hieraus ergibt sich, dass die Daten aus dem X-Com
System nicht automatisiert übernommen werden können, sondern entweder manuell in
die neue Struktur eingegeben werden müssen, oder ein individuelles
Übernahmescript erstellt werden muss.

---

## Übergabe an die RFS-Schnittstelle

Übergabe an  die RFS-Schnittstelle
Bei eingeschalteter RFS-Schnittstelle (die
Schnittstelle wird durch einen Lizenzparameter frei geschaltet )
wird   die Belegübergabe im Rahmen der im Aeins üblichen Übergabe an
die FIBU realisiert.  Organisatorische Abhängigkeiten ( Belegstatus,
Zusammenhang mit dem Mandentenserver etc ) und Eingrenzungsmöglichkeit des
FIBU-Übertrages entsprechen komplett der üblichen Aeins –Logik. Ein Beleg
befindet sich genau dann in der RFS-Schnitstelle, wenn er als ‚IN FIBU’
gekennzeichnet ist. So werden z.B.  Belege, die nicht übertragen werden
konnten ( fehlende Steuerzuordnungen / Erlöskennziffernprobleme etc ) in den für
den ‚normalen’ Fibuübertrag geführten Protokollen eingetragen ( z.B.
Direktsprung JOUR ). Das RFS System stellt diese Belege erst dann in die
RFS-Schnittstelle ein, wenn die sonst üblichen Vorraussetzungen für einen
ordnungsgemäßen Fibu-Übertrag erfüllt sind. Fehlermeldungen bezüglich
inkonsistenter Einstellung der RFS Parameter hingegen werden  in einer
gesonderten Protokolldatei notiert ( siehe  RFS Voreinstellungen RFSV
).

---

## Beschreibung der Vorgangsvorbelegungen

Beschreibung der Vorgangsvorbelegungen
Dieser Bereich umfasst alle Vorbelegungen und
Abwicklungseinrichtungen für den Bereich Vorgang.

---

## Betrag in Worten drucken

Betrag in Worten drucken
Beim Druck von Formularen können bisher Beträge auch
in Worten ausgedruckt werden. Dafür muss in den Details des Formulareinrichters
(Direktsprung FRM, Formulareinrichtung F6, Einrichtung F6 und dann der Knopf
„Detail“) der Schalter „In Worten darstellen“ angewählt werden. Dadurch werden
dann die einzelnen Ziffern des Betrages (ohne Nachkomma) in Wortdarstellung
gedruckt, z.B. „eins-acht-vier-sieben“.
Bei dieser Darstellung wird derzeit auch die intern
gewählte Systemsprache berücksichtigt. Es lassen sich also die Ziffern in die
entsprechende Systemsprache übersetzen.
Für den Fall, dass jedoch der Betragtext in
unterschiedlicher Sprache dargestellt werden soll, weil z.B. für ausländische
Kunden sprachgerechte Formulare eingerichtet werden müssen, kann das bisherige
Verfahren dafür nicht benutzt werden.
Daher wurde jetzt die Möglichkeit geschaffen, mit
einer privaten Datenbankfunktion die Textaufbereitung eines Betrages selbst zu
‚programmieren’.
Zu diesem Zweck wurde im Formularstamm das Feld ‚
DB Fkt. Num Text
’ hinzugefügt. Hier
muss der Name einer privaten Datenbankfunktion eingetragen werden (
Parametererklärung
siehe weiter unten
). Diese Datenbankfunktion erledigt dann die
Textaufbereitung aller Betragspositionen dieses Formulars, bei denen der
Detail-Schalter „In Worten darstellen“ angewählt wurde.

---

## Board einrichten

Board einrichten
Administration
Menü
Dashboard
Variante Dashboard
oder
Direktsprung
[DASH]
Variante
Dashboard
Bei bereits eingerichtetem Dashboard erreicht man die
Bearbeitungsmaske des Dashboards direkt über das Kontextmenü (rechte Maustaste)
des Dashboards.
Beschreibung
Titel
Der
      Titel ist ein Pflichtfeld. Er ist gleichzeitig die Bezeichnung auf dem
      Register im Hauptmenü. Ändert man den Titel des Boards, so wird diese
      Änderung erst nach Neustart von Referenz-ERP wirksam. Der Titel muss eindeutig
      sein.
Im
      Menü anzeigen?
Soll
      das Dashboard nicht im Menü angezeigt werden, da es bspw. nur für
      AIS-Masken angedacht ist, so kann man dieses Feld auf „Nein“
      stellen.
Die
      Standardeinstellung ist „Ja“.
Sortierung
Hat
      man mehrere Dashboards angelegt, kann mit der Sortierung deren Reihenfolge
      festgelegt werden, wie sie im Hauptmenü erscheinen. Dashboards können
      nicht vor die Standard-Registerkarten des Menüs platziert
      werden.
Schutzebene
Die
      Schutzebene kann „Bediener“ oder „Rolle“ sein. Legt man ein Dashboard neu
      an, so ist die Schutzebene auf „Bediener“ eingestellt und man selbst ist
      sofort zugeordnet. Auf einem Register, welches eingeblendet wird, können
      weitere Benutzer zugeordnet werden, die dieses Dashboard sehen dürfen.
Wählt man Rolle, so dürfen nur
      bestimmte einer Rolle zugewiesene Bedienerklassen dieses Board sehen. Es
      existiert dann im Menü eine Funktion
Rolle Festlegen
.
Hinweis:
Die Schutzebene hat nur Auswirkungen
      auf die Dashboards, die im Hauptmenü angezeigt werden.
View/Prozedur
      Überschrift
Für
      jedes Board kann eine Überschriftszeile bestehend aus einer Textzeile und
      einer Grafik (optional) eingerichtet werden. Die Werte werden wie bei den
      Kacheln über eine private View oder Prozedur angegeben. Mit der Funktion
View/Prozedur bearbeiten
kann
      die Funktion direkt bearbeitet oder neu angelegt wer
[...]


---

## CONNECT Statement

CONNECT Statement
Syntax
CONNECT userid IDENTIFIED BY password
Purpose
Verbindung zur aktiven Datenbank mit einem anderen
Benutzer herstellen.
Anwendung
Kommandodatei
Berechtigung
Branchen-ERP
Siehe auch
DISCONNECT
Beschreibung
Mit dem CONNECT Statement können sie sich unter einem
anderen Benutzer an die Datenbank anmelden. Ist die Kommandodatei beendet, wird
automatisch ein Connect auf den ursprünglichen Benutzer durchgeführt. Verwendung
findet dieses Statement vor allem beim anlegen von Views, Triggern, Funktionen
oder anderen Objekten, die einzelnen Benutzern zugeordnet werden sollen. Im
folgenden Beispiel wird die VIEW unter der Hoheit von Admin angelegt und ist
somit allgemein gültig. Ohne das vorangegangene CONNECT wäre es in diesem
Beispiel nur für den Benutzer zugänglich, der es angelegt hat.
Beispiel
CONNECT admin IDENTIFIED BY
*******;
Create view op as select * from
offenerposten;
DISCONNECT;
Create view admin.op1 as select * from
offenerposten;

---

## CONTINUE Statement

CONTINUE Statement
Syntax
CONTINUE;
Purpose
Beeinflussung des Abbruchs bei Fehlern.
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
SET
ERROR
Beschreibung
Mit CONTINUE könne Sie dafür sorgen, dass das folgende
Statement nicht zum beenden der Ausführung ihrer Kommandodatei führt. Dies ist
zum Beispiel praktisch beim Anlegen von Feldern oder Tabellen, bei denen es
möglich ist, das diese schon existieren. Nach der Ausführung des Folgestatements
wird wieder der alte Zustand hergestellt, der standardmäßig auf „Abbruch bei
Fehler“ steht.
Beispiel
CONTINUE;
Select * from
DIESERELATIONGIBTSNICH;
MSG Oh, hier geht’s ja weiter;
Select * from
DIESERELATIONGIBTSNICH;
MSG Hier komme ich nicht an;
CONTINUE ON ERROR;

---

## CREATE FROM Statement

CREATE FROM Statement
Syntax
CREATE FROM Dateiname;
Purpose
Löscht und legt Prozeduren, Views, Trigger und
Funktionen an.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
COMMAND_DELIMITER
Beschreibung
In Prozeduren, Funktionen und Triggern kann man davon
ausgehen, dass als Standard COMMAND_DELIMITER das Semikolon >;< gesetzt
ist. Dies führt beim Abarbeiten von Kommandodateien zu Problemen, da
standardmäßig auch hier jedes Statement mit >;< endet. Daher ist es
Sinnvoll in diesem Fall einen anderen COMMAND_DELIMTER zu setzen. Dies übernimmt
diese Funktion, und man vermeidet dadurch unnötige Fehler, weil man vergisst
diesen wieder zurückzusetzen. Sie übernimmt zusätzlich auch das löschen, falls
diese Prozedur... schon vorhanden war.
Beispiel
// Datei C:
\FIBUVORGSTAMM_AFTDEL.SQL;
CREATE TRIGGER FiBuVorgStamm_aftdel
AFTER DELETE ON FiBuVorgStamm
REFERENCING OLD AS alt
FOR EACH ROW
WHEN ( alt.FiBuV_BUCHSTAT!=3 )
BEGIN
delete from FiBuVorgUngebu
where
FibuV_id         = alt.FibuV_id;
END;
//Aufruf aus einer Kommandodatei
CREATE FROM
C:\FIBUVORGSTAMM_AFTDEL.SQL;

---

## CREATE PRIMARY KEY FROM Statement (ab Version 4.5 )

CREATE PRIMARY KEY
FROM Statement (ab Version 4.5 )
Syntax
CREATE PRIMARY KEY FROM Indexname;
Purpose
Legt einen Primary key an.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Branchen-ERP
Siehe auch
CREATE STRUCT
,
DBFCREATE
,
ALTER STRUCT
Beschreibung
Beim erstmaligen anlegen der Datenbank wurden anstatt
PRIMARY KEYS zu verwenden Unique Indexe verwendet. PRIMARY KEYS werden jedoch
benötigt um die referenzielle Integrität hinzubekommen ( FOREIGN-KEYS ). Um nun
nachträglich die PRIMARY KEYS verwenden zu können, sind mehrere Schritte nötig.
Die diese Funktion übernimmt:
Es wird geprüft, ob für diese Relation schon ein
PRIMARY KEY existiert. Ist dies der Fall wird die Funktion beendet.
Es wird versucht die Felder zu NOT NULL Feldern zu
machen, falls Sie noch keine sind. Funktioniert dies nicht, wird versucht alle
Datensätze zu löschen, die eines der Indexfelder NULL haben und danach noch mal
die Felder zu NOT NULL zu machen.
Es wird der PRIMARY KEY angelegt.
Der Index  wird gedropt.
Beispiel
CREATE PRIMARY KEY FROM
u0__Fibuv_id_offenerposten

---

## Crw/Vbs

Crw/Vbs
Hier hat man in der F3-Auswahl verschiedene
Möglichkeiten:
-------------------
Dies ist der Standardformulardruck.
CRW auf Basis Formular mit CRW Drucker
Man erstellt ein Formular und einen zugehörigen
Report. In dem Report werden die Zeilen aus der Formulareinrichtung angedruckt.
Man kann durch die Reportbearbeitung Dinge ändern (z.B. die Schrift im
Mittelteil der Zeilen) oder zufügen.
Dieser Report auf Basis eines Formulars
wird mit dieser Einstellung auf dem Drucker des Reports ausgedruckt. Unter dem
Direktsprung [lst] kann man den Listen/Reports mit Hilfe der Druckerauswahl
Drucker zuordnen.
CRW auf Basis Formular mit DRZ/VRGD Drucker
Man erstellt ein Formular und einen zugehörigen
Report. In dem Report werden die Zeilen aus der Formulareinrichtung angedruckt.
Man kann durch die Reportbearbeitung Dinge ändern (z.B. die Schrift im
Mittelteil der Zeilen) oder zufügen.
Dieser Report auf Basis eines Formulars
wird mit dieser Einstellung auf dem Drucker der Druckerzuordnung [DRZ] oder der
Vorgangsdruckklasse [VRGD] des Kunden gedruckt.
VBS Ausgabe
Es wird das unter Script angegebene VBS Script
verwendet.
Branchen-ERP Etikettendruck mit Druckerabfrage
Es wird ein unter dem Branchen-ERP Etikettendruck [etidr]
erstelltes Formular auf dem abgefragten Drucker gedruckt. Der Inhalt des Feldes
Funktionsident für das Etidr Formular muss hier als Name angegeben werden.
Branchen-ERP Etikettendruck auf dem im ETIDR-Formular
eingerichteten Drucker
Es wird ein unter dem Branchen-ERP Etikettendruck [etidr]
erstelltes Formular auf dem für dieses Formular dort angegebenem Drucker
gedruckt. Der Inhalt des Feldes Funktionsident für das Etidr Formular muss hier
als Name angegeben werden.
Branchen-ERP Etikettendruck auf dem DRZ/VRGD Drucker
Es wird ein unter dem Branchen-ERP Etikettendruck [etidr]
erstelltes Formular auf dem Drucker der Druckerzuordnung
[DRZ]
oder der Vorgangsdruckklasse
[VRGD]
des Kunden gedruckt.
Der Inhalt
des Feldes Funktionsident für das Etidr Formular muss hier als Name angegeben
we
[...]


---

## Crystal Report über JPP aufrufen

Crystal Report über JPP aufrufen
Um einen Report
programmgesteuert aufzurufen, existiert ein JPP Objekt mit dem Name
JAnwendReport.
Methoden,
ohne die es nicht geht, sind fett
geschrieben.
Methode
Parameter
Bedeutung
Read
m_AnwRptId
Die
      Reportdefinition des Reports mit der über m_AnwRptId angegebenen Ident
      wird gelesen. Liefert FALSE (0) wenn das Einlesen schiefgegangen ist. Muss
      als erste Anweisung erfolgen!
FeldFormat
Übergibt die Werte der Formelfelder
      an den Report.
CreatViews
Alle
      definierten Views werden angelegt
SetFileName
Filename
Dateinamen überschreiben. Parameter
      ist FILENAME. Dieser enthält Pfad und Dateiname des Reports.
SetPrinterByNumber
Printernumber
Holt
      sich anhand der Druckernummer den Drucker, auf dem der Report gedruckt
      werden soll
GetSelectedPrinter
Feldname
Liefert den Drucker in das durch
      Feldname bezeichnete Feld zurück.
SetVon
IDX
Überschreibt den Vonwert des
      Auswahlbereichs. IDX ist dabei der Index, der in der Spalte Idx des
      Auswahlbereichs steht.
SetBis
IDX
Überschreibt den Biswert des
      Auswahlbereichs. IDX ist dabei der Index.
SetWaehrung
Waehrung
Überschreibt die Währung, in der der
      Report ausgegeben wird. Dies gilt nur für bestimmte dafür vorgesehene
      Reporte.
SetExportPfad
Exportpfad
Überschreibt das in den Stammdaten
      hinterlegte
Export-Verzeichnis
.
ListenStart
Startet den Report.
Device
Siehe nächste Tabelle.
NurArchivieren
Der
      Parameter NurArchivieren ist optional. Gibt man hier eine 1 an, wird der
      Report nicht gedruckt, sondern sofort ins Archiv gestellt.
ASK
Dieser Parameter gibt an, ob vor dem
      Druck der Drucker abgefragt werden soll. Gibt man 0 an, so erscheint die
      Druckerabfrage nicht.
FA_Kundnummer
Kundennummer für das Formulararchiv.
HINWEIS:
Wird dieser oder einer der
      folgenden drei Parameter angegeben, so werden die CRW-Archivdefinitionen
      nicht mehr ausgewertet
FA_Belegnummer
Be
[...]


---

## Datenbank-Serveroptionen (dbsrv17)

Datenbank-Serveroptionen (dbsrv17)
Die verwendeten Serveroptionen:
Die Optionen sind
hier
nachzulesen.
Beispiel einer ServiceParameter-Datei:
-n Branchen-ERP
-ti 3600
-tl 1800
-c 4096M
-x tcpip
-gd all
-o C:\Aeins\bin\server.txt

---

## Datenträgererstellung

Datenträgererstellung
Wenn diese Einrichtungen durchgeführt wurden und
Barvorgänge durch Bezahlung über EC-Karten durchgeführt wurden, geht man zur
Erstellung der DTAUS-Datenträger für die unter 4. eingestellte Hausbank wie
folgt vor:
Im Menu Vorgänge/Barvorgänge ex. die Funktion
Lastschrift Abschluss. Diese ist aufzurufen und F9 zu betätigen.
Dann hat man in Referenz-ERP/Daten die Dateien Dtaus0.txt
und Begl.txt erstellt.
Während die erste Datei die DTAUS-Datei ist, handelt
es sich bei der zweiten um den sogenannten Begleitzettel.
Von dort können die erzeugten Dateien auf Datenträger
kopiert und an die Bank verschickt werden.
ACHTUNG:
Zurzeit werden diese Dateien bei Erstellung neuerer
Dateien überschrieben!

---

## Datumsreihenfolge

Datumsreihenfolge
Wird der Steuerparameter "
820 -
Reihenfolge der Datumsangaben bei Umwandlung muss stimmen
" auf „Ja“
gestellt, dürfen bei der Umwandlung nur Folgebelege erstellt werden, deren
Vorgangsdatum größer oder gleich dem Vorgangsdatum des Ursprungsbelegs liegt.
Eine Rechnung, deren Datum vor dem Datum des Lieferscheins liegt, wäre dann
nicht möglich.
Diese Behandlung gilt nur für die Umwandlung von
Standardvorgängen – nicht jedoch für Rohware.

---

## DBFCREATE Statement (Ab Version 5.0)

DBFCREATE Statement (Ab Version 5.0)
Syntax
DBFCREATE Dateiname.dbf [INTO Relationsname]
Purpose
Anlegen einer Tabelle anhand der Feldbeschreibung in
der DBASE Datei
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
DBFLOAD
,
LOAD
,
READ
,
IDENTLOAD
,
CREATE STRUCT
,
ALTER STRUCT
Beschreibung
Man kann mit dem Befehl DBFCREATE eine Tabelle
anlegen. Die Struktur der Tabelle wird aus eine Datei im dBASE Format ( Version
dBASE III+ und  dBase IV )ermittelt. Ist kein Relationsname angegeben wird
der Dateiname hierfür herangezogen. Es werden folgende Feldtypen ausgewertete:
Character, Numerisch, Logical, Datum, Gleitpunkt. Dbasedateien mit anderen
Feldtypen können nicht bearbeitet werden.
Beispiel
DBFCREATE FOP1.DBF into AMIC_OPS;

---

## DBFLOAD Statement

DBFLOAD Statement
Syntax
DBFLOAD [NOANSI] Dateiname.dbf [INTO
Relationsname]
Purpose
Einlesen einer DBASE Tabelle
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
LOAD
,
READ
,
IDENTLOAD
,
DBFCREATE
Beschreibung
Man kann mit dem Befehl DBFLOAD direkt Daten die im
dBASE Format ( Version dBASE III+ und  dBase IV )abgelegt sind, in
Relationen abspeichern. Existiert die angegebene Relation nicht wird sie anhand
der Datenbeschreibung innerhalb der Datei angelegt. Ist kein Relationsname
angegeben wird der Dateiname hierfür herangezogen. Es werden folgende Feldtypen
ausgewertete: Character, Numerisch, Logical, Datum, Gleitpunkt. Dbasedateien mit
anderen Feldtypen können nicht bearbeitet werden.
Ist in der DBF-Datei
nicht die Codepage 1252 (Windows ANSI-Code), so wird für die Umlautdarstellung
eine Codepagekonvertierung  von MSDos nach  Windows vorgenommen. Will
man diese Konvertierung nicht haben, so muss man NOANSI angeben. ACHTUNG :
NOANSI muss direkt hinter DBFLOAD stehen!
Beispiel
DBFLOAD FOP1.DBF into AMIC_OPS;

---

## Der Datenbankdienst

Der Datenbankdienst
Bei neuen Systemen muss der Datenbankdienst
eingerichtet werden, hierbei ist im Parameterbereich der Control Managers
folgendes zu beachten:
-n aeins -c80M -ti 240 -tl 3600
Parameter
Bedeutung
-n
gibt
      den Maschinennamen an (eng=....)
-c
gibt
      die Hauptspeicherbereich an, der genutzt werden darf
-ti
Ist
      die Zeit in Minuten bis ein User aus dem System geloggt wird
-tl
gibt
      die Lebenszeit an, die verstreichen muss, bis ein nicht mehr existenter
      User aus dem System geworfen wird.

---

## Die SQL Remote-Nachrichtenagent Konfigurationsdatei anlegen

Die SQL Remote-Nachrichtenagent Konfigurationsdatei
anlegen
1.
Starten Sie den Editor
2.
Klicken Sie nun auf Datei
à
Speichern unter
3.
Bewegen Sie sich im Dateiexplorer in das Verzeichnis „..\Aeins\config\“
4.
Speichern Sie die Datei unter dem Namen „serviceparameter_Datenbankname.txt“ ab.
ACHTUNG! Ersetzen Sie das Wort Datenbankname in der Dateibezeichnung auch
wirklich durch den Datenbanknamen!
5.
Zurück im Editor, müssen nun folgende
Optionen für den Start
des SQL Remote-Nachrichtenagenten
konfiguriert bzw. angegeben werden:
-c
"uid=admin;pwd=******;eng=<ServerName>;dbn=<DatenbankName>;links=tcpip"
-x
50m
-os
5m
-rd
30s
-v
-r
-s
-ro
C:\aeins\dbrexp\<RemoteUserName>_err.log
-o
C:\aeins\dbrexp\<PublisherName>.log
c:\aeins\daten\<DatenbankName>
6.
Ändern Sie die Werte in den Spitzen Klammern entsprechend!
7.
Speichern Sie die Konfigurationsdatei unter Datei
à
Speichern

---

## DISCONNECT Statement

DISCONNECT
Statement
Syntax
DISCONNECT;
Purpose
Stellt die ursprüngliche Verbindung zur Datenbank
wieder her.
Anwendung
Kommandodatei
Berechtigung
Branchen-ERP
Siehe auch
CONNECT
Beschreibung
Hat man sich per CONNECT als anderer Benutzer an die
Datenbank angemeldet, hebt DISCONNECT diese Verbindung wieder auf und meldet den
ursprünglichen Benutzer wieder an.
Beispiel
CONNECT admin IDENTIFIED BY
*******;
CREATE VIEW FIBUBELEG as select * from
fibuvorgstamm;
DISCONNECT;

---

## DOS2WIN Statement

DOS2WIN Statement
Syntax
DOS2WIN table-name [Dateiname der Umsetztabelle];
Purpose
Wandelt die Umlaute der DOS Codepage in Umlaute der
Windos-Codepage um.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
WIN2DOS
Beschreibung
Bei Datenübernahmen aus ehemaligen DOS/ Prolog –
Programmen tritt das Problem auf, dass die Deutschen Umlaute auf unterschiedlich
dargestellt werden. Dieser Befehl schnappt sich eine Tabelle(table-name) und
nimmt sich alle Textfelder vor um dort gegebenenfalls die Umlaute umzuwandeln.
Es erfolgt nur ein Update, wenn auch Umlaute in den Datensätzen vorhanden sind.
Wird keine Umsetztabelle angegeben, werden nur die gebräuchlichen Umlaute
umgewandelt. Diese wären ÄÖÜßäöü. Weiterhin kann es auch Probleme mit Hochkomma
in den Tabellen geben. Diese werden auch umgewandelt.
Die Umsetztabelle hat ein einfaches Format. In
jeder Zeile steht ein umzusetzendes Zeichen gefolgt vom Zeichen, wie es unter
Windows dargestellt werden soll. Um dies Datei zu erstellen, kann man den MSDOS
Editor aufrufen, dort die Zeichen eingeben um anschließend dieselbe Datei unter
Windows mit Notepad aufzurufen und dort noch mal die Zeichen in der
entsprechenden Zeile einzugeben.
Um nicht die Zeichen eingeben zu
müssen, was für die Dos-Umlaute doch etwas umständlich ist, kann man auch den
ASCII- Wert angeben. Dabei werden die ersten drei Stellen als ASCII-Wert als
umzusetzendes Zeichen und die folgenden  drei Stellen als Zeichen, in das
umgewandelt werden soll. Also würde die Zeile
065097
angeben, dass der n Buchstaben A in a umgewandelt
werden soll.
Beispiel
DOS2WIN ANSCHRIFTSTAMM
c:\AEINS\BIN\UMLAUT.TXT

---

## Druckbereich 81: Sammelformulareinrichtung QUER

Druckbereich 81:
Sammelformulareinrichtung QUER
Hauptmenü
Administration
Formulare/Abläufe
Formulare
Formulareinrichtung
Direktsprung
[FRM]
Mittels geschickt
parametrisierter spezieller Druckeinrichtungspositionen kann ein
Rohware-Sammeldruckformular auch ‚quer‘ eingerichtet werden, d.h. die relevanten
Informationen pro Einzelbeleg werden in einer Druckzeile dargestellt. Hierzu
wird von den unterschiedlichen Einzelbeleg-Druckbereichen lediglich der
Druckbereich 81 (Rohware-Sammeldr.-Einzelfussinfo) im Formular eingerichtet, der
beim Druck des Formulars genau einmal pro Einzelbeleg ausgegeben wird.
Der
Bezug zur jeweils heranzuziehenden Waren-/Qualitäts- oder Kostenposition wird
durch die Angabe eines bestimmten Wertes im Feld ‚Parameter‘ im Detail-Bereich
der Positionseinrichtung hergestellt. Dabei handelt es sich, je nach Gruppe der
Druckpositionen, um die feste Referenznummer (Rohwarengruppendefinition, nicht
änderbar, in Belegposition gespeichert), der variablen Ref2 (
Rohwarengruppendefinition, immer änderbar, nicht in Belegposition gespeichert)
oder der ebenfalls variable Ref3 (Abrechnungsschemadefinition, immer änderbar,
nicht in Belegposition gespeichert).
Die
dafür zur Verfügung stehenden Druckpositionen und die Bedeutung des jeweils
unter Detail angegebenen Wertes für Parameter sind nachfolgend aufgelistet.
ID_MASSNUMMER
Parameter: Referenznummer der
Waren-/Qualitäts- oder Kostenposition
Masseinheitsnummer der
Waren-/Qualitäts- oder Kostenposition zur Referenznummer.
ID_MASSEINHEIT
Parameter: Referenznummer der
Waren-/Qualitäts- oder Kostenposition
Masseinheit (Text) der
Waren-/Qualitäts- oder Kostenposition zur Referenznummer.
ID_ARTIKELNUMMER
Parameter: Referenznummer der
Waren- oder Kostenposition
Artikelnummer der  Waren-
oder Kostenposition zur Referenznummer.
ID_ARTISTAMMNUMMER
Parameter: Referenznummer der
Waren- oder Kostenposition
Artikelstammnummer der
Waren- oder Kostenposition zur Referenznummer.
ID_ME_BEZEICHNUNG
Par
[...]


---

## Druckfelder

Druckfelder
Einrichtung erfolgt über Variante Druckfelder in der
Anwendung Formularstamm. Hier kann zu einem definierten Wert ein Wert hinterlegt
werden.
Der Wert kann entweder durch einen festen Wert oder
als Ergebnis einer einrichtbaren privaten Datenbank-Funktion gewonnen
werden.
Bei den Datenbank-Funktionen werden folgende
Parametrisiermöglichkeiten unterstützt:
Keine Parameter
Ein String-Parameter
Und die vollständige Parametrierung:
--
Eingabe : in_pf_name
: Druckfeldname
--
in_bereich
:
Druck-Bereich
--
in_kundenid : optionale Kundenid
--
in_artikelid: optionale Artikelid
--
in_v_id
: optionale V_id
--
in_wabewid
:
optionale WabewId
--
Ausgabe : Druckfeld-Wert

---

## DUMP Statement

DUMP Statement
Syntax
DUMP INTO Dateiname [APPEND];
Purpose
Daten in Datei schreiben.
Anwendung
Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET
OUTPUT
,
SET
OUTFILE
Beschreibung
Dump into ... dient dazu, die aktuell angezeigten
Daten in eine Datei zu übernehmen. Der Vorteil ist hier, dass das Statement,
welches eventuell sehr lange gelaufen ist, nicht ein zweites mal ausgeführt
werden muss, da alle bereits gelesenen – und auch nur die bisher gelesenen -
Daten in die Datei geschrieben werden.
Dump into überschreibt standardmäßig die Datei. Das
Schlüsselwort APPEND sorgt dafür, dass die Daten an die bestehende Datei
angehängt werden
Beispiel
DUMP INTO c:\AEINS\BIN\output.TXT
APPEND

---

## Eindeutigkeit

Eindeutigkeit
Hauptmenü
Administration
Nummernkreise
Fibu-Vorgangszuordnung
Funktion
F6
Eindeutigkeit
Direktsprung
[NKF]
Es können hier pro Belegart für manuelle und für
automatische Belegerstellung unterschiedliche Werte angegeben werden.
Mögliche Werte sind:
•
manuelle Nummernvergabe
•
Nummernvorschlag
•
Eindeutiger Nummernvorschlag
•
Eindeutig pro Geschäftsjahr & Vorgang
•
Eindeutig je Vorgang
•
Eindeutig je Geschäftsjahr
•
Eindeutig im Gesamtsystem
Die Eindeutigkeit der Nummer wird immer im
Zusammenhang mit dem Nummernkreis geprüft. Bei "manueller Nummernvergabe",
"Nummernvorschlag" und "eindeutiger Nummernvorschlag" muss die Eindeutigkeit der
Belegnummer durch geeignete betriebliche Mittel gewährleistet werden.

---

## Einrichten über Aeins

Einrichten über Aeins
1.
Starten Sie Aeins mit der gewünschten Datenbank
2.
Gehen Sie über den Direktsprung [SFS] zur Anwendung Setup Filialsystem,
alternativ gehen Sie über „Hauptmenü
à
Filialsystem
à
Stammdaten
à
Setup Filialsystem“
3.
Wählen Sie in der Funktionsbox der Variante „Setup Filialsystem“ die Funktion
„Event anlegen“
4.
Geben Sie dort die abgefragten Daten an und verwenden die Funktion „Event
anlegen“ oder die Funktionstaste F9
5.
Das Ereignis kann nun über den Direktsprung [EVT] angesehen oder bearbeitet
werden

---

## Einrichten über Sybase Central

Einrichten über Sybase Central
1.
Nach dem Sie sich mit der gewünschten Datenbank verbunden haben, wählen Sie in
der Ordneransicht den Punkt „Ereignisse“
2.
Klicken Sie diesen mit der RECHTEN Maustaste und wählen „Neu
à
Ereignis“
3.
Im Assistenten zum Erstellen von Ereignissen geben Sie bitte zunächst den Namen
„
dbrexp_schedule
“ ein und klicken auf „Weiter“
4.
Dieses Ereignis wird „Geplant“ ausgelöst. Auswählen und „Weiter“
5.
Geben Sie nun einen Namen des Zeitplans an und klicken auf „Weiter“
6.
Geben Sie an, wann das Event ausgeführt werden soll
a.
…auslösen um:
b.
…auslösen zwischen
c.
Optionales Datum wird NICHT benötigt
7.
Geben Sie nun den gewünschten Wiederholungsintervall an
a.
Haken bei: Dieses Ereignis auslösen alle z.B. 1 Minuten
8.
Klicken Sie auf „Weiter“
9.
Je nachdem in welcher Datenbank Sie sich aktuell befinden geben Sie die
Option:
a.
Nur in der konsolidierten Datenbank ausführen
b.
Nur in entfernten Datenbanken ausführen
an und klicken auf „Fertig
stellen“
10.  Geben
Sie in der Registerkarte „SQL“ des Ereignisses „dbrexp_schedule“ folgendes
ein:
begin
call amic_remote_schedule()
exception
when others then
call amic_exception(ERRORMSG() ||
'\\x0A' || TRACEBACK(),sqlcode,sqlstate,'EVENT dbrexp_schedule',-19004)
end
11.
Speichern Sie die Änderungen über „Datei
à
Speichern“

---

## Einrichten der FTP-Verbindung

Einrichten der FTP-Verbindung
Wird der Datenaustausch innerhalb der Replikation über
verschiedene Standorte der Datenbankserver realisiert, der Austausch der
Nachrichten über FTP geregelt. Hierfür benötigen wir ein FTP-Skript (FTP.PS1),
welches die Verbindung zum FTP-Server aufbaut und den Datenaustausch intelligent
regelt.
!! WICHTIG
!!
Das Event „
dbrexp_schedule
“ darf nicht aktiviert sein!
Die Erstellung des FTP-Skriptes wird durch die
Datenbank Prozedur „
amic_remote_schedule_ftp()
“ durchgeführt.
Hierzu gehen Sich in Sybase Central wie folgt vor:
1.
Starten Sie Sybase Central unter: ..\Aeins\bin64\scjview.exe
2.
Verbinden Sie sich mit der gewünschten Datenbank
3.
Wählen Sie in der Ordneransicht den Punkt aus in dem der Datenbankname steht
(
4.
Klicken Sie diesen mit der RECHTEN Maustaste an und klicken anschließend auf
„Interactive SQL öffnen“
5.
Geben Sie nun im neuen Fenster die folgende SQL Befehlskette ein: „
call
amic_remote_schedule_ftp()
“ und drücken Sie die Funktionstaste F9
zum ausführen
6.
Schließen Sie das Fenster wieder
7.
Öffnen Sie den Dateiexplorer und bewegen sich in das Verzeichnis
„..\Aeins\dbrexp\“
8.
Suchen Sie hier die Datei FTP.PS1 , klicken diese mit der RECHTEN Maustaste an
und klicken anschließend auf „bearbeiten“
9.
Suchen Sie im jetzt geöffneten Editor / Notepad nach dem Stichwort „. Main“
(Dies sollte die letzte Zeile in dem Skript sein)
10.
Passen Sie die hier zu findenden Parameter an:
b.
–bstpath
Pfad zum lokalen dbrexp-Verzeichnis (z.B. c:\aeins\dbrexp)
c.
–bst
Remoteusername für den die Verbindung aufgebaut wird (z.B. BST2)
d.
–bstip
IP des FTP-Servers
e.
–bstuser
Benutzername zur Anmeldung am FTP-Server
f.
–bstpwd
Kennwort zur Anmeldung am FTP-Server
11.
Speichern Sie die Änderungen und schließen den Editor / Notepad
Die FTP Einrichtung ist damit abgeschlossen.
Hinweis:
Das
[...]


---

## Einrichterparameter

Einrichterparameter
Die Einrichterparameter umfassen momentan folgende
Bereiche:

---

## Einrichterparameter

Einrichterparameter

---

## Einrichterparameter für SEPA

Einrichterparameter für SEPA
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Funktion
DTA
F9
Direktsprung
[ZHB]
In der Dialogmaske, die den Datenträgeraustausch
zusammenstellt, existieren Einrichterparameter, die nur für SEPA zuständig
sind.
1)
Der Einrichterparameter „SEPA: Folgende Version verwenden:“ ist nicht mehr
aktiv. Die Version kann bzw. muss nun pro Hausbank eingerichtet
werden.
2)
SEPA: Nur eine Art des Lastschriftverfahrens zulassen?
Um eine Mischung
von Basis- und Firmenlastschriften zu vermeiden wird vor jedem Erstellen
geprüft, ob unterschiedliche Lastschriftverfahren in der Auswahl vorkommen und
dann ggf. die Verarbeitung abgebrochen. Wenn man diesen Einrichterparameter auf
nein
stellt, wird diese Prüfung nicht durchgeführt.
In der Dialogmaske zum Zusammenstellen der
Zahlungsvorschläge (Direktsprung
[ZHVE]
) existieren Einrichterparameter, die
nur für SEPA zuständig sind.
1)
SEPA Bankarbeitstage vor Fälligkeit bei Erstlastschrift. Standardeinstellung ist
5.
2)
SEPA Bankarbeitstage vor Fälligkeit bei Folgelastschrift. Standardeinstellung
ist 2.
3)
SEPA Bankarbeitstage vor Fälligkeit bei Firmenlastschrift. Standardeinstellung
ist 1.
4)
SEPA Bankarbeitstage vor Fälligkeit bei Eillastschrift. Standardeinstellung ist
1.
5)
SEPA Maximale Vordatierung des Ausführdatums(Kalendertage). Standardeinstellung
ist 14.
Achtung
:
Ab Version 3.0 wurde die Vorlauffrist für Erst-, Folge, Letzt – und
Einmallastschriften auf einen Bankarbeitstag verkürzt.

---

## Einrichterparameter Währung

Einrichterparameter Währung
Einrichterparameter Belegerfassung
Bezeichnung
Standardwert
Erklärung
Ankauf,
      Verkauf o. Mittelkurs bei Ausgangsgutschriften
Verkauf
In den Währungskursen kann
      man Kurse für Ankauf, Verkauf und Mittel Pflegen. Welcher Kurs bei
      Fremdwährungsbelegen herangezogen werden soll, wird hier
      hinterlegt.
Ankauf,
      Verkauf o. Mittelkurs bei Ausgangsrechnungen
Verkauf
s.o.
Ankauf,
      Verkauf o. Mittelkurs bei Eröffnungsbuchungen
Mittel
s.o.
Ankauf,
      Verkauf o. Mittelkurs bei Eingangsgutschriften
Ankauf
s.o.
Ankauf,
      Verkauf o. Mittelkurs bei Eingangsrechnungen
Ankauf
s.o.
Ankauf,
      Verkauf o. Mittelkurs bei sonstigen Belegen
Mittel
s.o.
Ankauf,
      Verkauf o. Mittelkurs bei Zahlungen
Mittel
s.o.

---

## Einrichterparameter zum Vorgang als Stapel

Einrichterparameter zum Vorgang als Stapel
Die Einrichterparameter umfassen momentan folgende
Bereiche:
Parameter
Druckauswahlfenster
Mit
      diesem EPA kann eingestellt werden, ob ein Druckauswahlfenster Ja/Nein
      angezeigt wird oder nicht.
Druckvorbelegung
Für
      die Knöpfe D1 und D2 kann festgelegt werden, ob der Fokus beim
      Druckfenster auf Ja oder auf Nein steht.
Vorgangsklasse
Mit
      diesem EPA wird eingestellt, welche Standardvorgangsklasse beim öffnen
      vorgegeben wird.
Zielvorgangsklasse bei automatischer
      Umwandlung
Die
      Zielvorgangsklasse steuert die Möglichkeit, aus einem Beleg der Klasse 400
      einen Belege der Klasse 600 zu machen, also einen Auftrag in einen
      Lieferschein umzuwandeln. Wird die Zielvorgangsklasse leer gelassen, so
      werden keine Umwandlungsbelege angezeigt.
Vorgangsunterklasse
Im
      Standardfall (Knopf OK) wird diese Unterklasse als Vorbelegung
      genommen.
Vorgangsklasse, bei der keine Preise
      gezogen werden
Preise nachladen aus der Liste bei
      Umwandlung und 0 Preisen
Itembox Kunde
In
      diesem EPA muss die ITEM Boxen festgelegt werden, die zum Anzeigen der
      Auswahlinformationen genutzt werden sollen.
IB_KU ist die Vorbelegungen den
      Kunden.
Itembox Artikel
In
      diesem EPA muss die ITEM Boxen festgelegt werden, die zum Anzeigen der
      Auswahlinformationen genutzt werden sollen.
IB_ARTIKEL_NU ist die Vorbelegungen
      den Artikelfall.
Itembox Zusatz
In
      diesem EPA muss die ITEM Boxen festgelegt werden, die zum Anzeigen der
      Auswahlinformationen genutzt werden sollen.
Listenpreisklassenliste 1 (mit Komma
      trennen)
An
      dieser Stelle wird mit Komma getrennt, eingetragen, welche
      Kundenpreisklassen welche Preise (1 bis 4) zu sehen bekommen.
Listenpreisklassenliste 2 (mit Komma
      trennen)
An
      dieser Stelle wird mit Komma getrennt, eingetragen, welche
      Kundenpreisklassen welche Preise (1 bis 4)
[...]


---

## Einrichtung

Einrichtung
•
Für die Verwendung dieses Moduls ist die Lizenz „Permanente Inventur (
Steuerparameter 902
) notwendig.
•
Im
SPA 1045 – Permanente
Inventur
muss eingerichtet werden:
o
Anzahl an Tagen für eine
Zählung (0= aktuelles Wirtschaftsjahr)
o
Anzahl von Artikelzeilen pro
Inventurbeleg (Vorgangsklasse 5055)
•
SPA 1072 – Bewertungsverhalten
permanente Inventur
Wir empfehlen, diesen Wert
auf 1 – keine Bewertung durch Bestandsbeleg einzustellen.
•
SPA 1118 – permanente Inventur
besuchte Lagerplätze
– wird für die LVS-Vollständigkeitsprüfung
gebraucht.
•
Die FiBu-Konten der FiBu-Buchungen müssen in der Erlöskennzifferzuordnung
eingerichtet werden.
•
Wird für die Erfassung von permanenten Inventuren ein Scannersystem
verwendet, so muss im Lagerstamm des zu zählenden Lagers der Wert „permanente
Inventur“ gesetzt werden. Mittels dieses Kennzeichens kann das LVS-Lager
ermittelt werden, dessen Regalbesuche auf Vollständigkeit geprüft werden.
•
Ggf. ist eine Anbindung des Scannersystems an die Makroschnittstelle zu
individualisieren.
•
Pflege des Kennzeichens „permanente Inventur“ im Artikel
Es wird dringend empfohlen
während einer laufenden Inventur dieses Kennzeichen nicht zu verändern.
•
Folgende AF-Formate sind zu ergänzen:
o
VorgKlXXXS
o
VorgKlXXS
o
VorgKlasseTx
o
VoKlasse
o
VorgKlasse
o
AF_Vorgang
Für die Vorgangsklassen
Klassen-nummer
Name
Kürzel
(Vorschlag)
Bedeutung
5055
Inventurdifferenzbeleg
IVD
Unter dieser Vorgangsklasse können
      Inventurbelege eingegeben werden. Diese enthalten sowohl eine Mengen- als
      auch eine Wertkorrekturen.

---

## Einrichtung

Einrichtung
•
Zunächst muss sichergestellt sein, dass der Lizenzsteuerparameter „Futter
App“ (SPA 1025) aktiv ist.
•
Im Steuerparameter „FutterApp Optionen und Ausprägungen“ (SPA 1047) muss
ein Dateipfad hinterlegt werden.
Hierfür muss der Punkt
„An/Aus“ auf „Ja“ (1), „Ausprägung“ auf „Dateipfad für Ordnerstruktur“(4) und
„Wert/Value“ auf „<gewünschter Dateipfad>“ gestellt werden.
•
Als nächstes unter
[OSQL]
den
Control-String „^jpl FutterAppEinrichter“ ausführen.
o
Die Ordnerstruktur unter dem
im Steuerparameter 1047 angegebenen Pfad wird angelegt.
o
Es werden die Exportprofile
für den
„DbExporter“,
in der Tabelle „H_GS_EXPORT_PROFIL“ angelegt.
o
Es werden die Transferprofile
für den
„Referenz-ERP.FtpTransfer“
, in der Tabelle „H_GS_TRANSFER_FTP“
angelegt.
o
Es wird die Batch-Datei
„FutterAppExporter.bat“ in der Ordnerstruktur (SPA 1047) erstellt.
o
Übergabeparameter
Referenz-ERP.FtpTransfer.exe: “CONNECTION=Mandantname TRANSFERID=TransferId“ aus
Tabelle H_GS_TRANSFER_FTP
•
Die Serverinformationen müssen in den Transferprofilen nachgepflegt
werden.
[FTPTRA]
•
Der Import der Bestellungen muss als Event eingetragen werden
[EVT]
. Es wird eine minütliche Wiederholung
empfohlen.
Verarbeitungsroutine:
begin
insert into "DATENSTROM"(
"ds_status","BedienerId","DS_DSC","DS_Id","DS_Parameter","ds_RefText" )
values
(
0,-1,12,"amic_func_dbxident"('Datenstrom',0),'^jpl FutterApp abc 400 0
1','FutterAppBelegImport' )
end
o
Der erste Parameter („abc“)
war ursprünglich der Dateipfad. Dieser wird noch gezogen, wenn kein Eintrag im
Steuerparameter eingetragen ist. Dies ist nicht mehr empfohlen.
•
Diese Batch-Datei „FutterAppExporter.bat“ muss nun im
Windows-Aufgabenplaner eingetragen werden. Es wird eine Wiederholung in
5-Minuten Intervallen empfohlen.
•
Im Lieferschein und in den Aufträgen muss das UFLD-Feld für
die Baustelle hinzugefügt werden. Hierfür zunächst mit
[UFLD]
auf die
zugehörige Auswahlliste springen. Und dort die
Datensätze mit passender Vorgangs-, Vorgan
[...]


---

## Einrichtung

Einrichtung
Referenz-ERP benötigt einen Lizenzschlüssel für das Modul
„DSGVO“. Ist diese Lizenz vorhanden, stehen im weiteren Verlauf folgende
Programmfunktionen zur individuellen Erweiterung und Einrichtung der DSGVO
relevanten Tabellen und Felder zur Verfügung.
Wenn keine privaten Felder oder Tabellen in Referenz-ERP
existieren, sind keine Änderungen an den Objekten nötig.
Anonymisieren Sie mit dem Modul „DSGVO“
personengebundene Daten. Somit sind solche Daten anschliessend nicht mehr
elektronisch auszuwerten.

---

## Einrichtung

Einrichtung

---

## Einrichtung Anschriftenfeld und Infofelder in der Vorgangsmaske:

Einrichtung Anschriftenfeld und Infofelder in der Vorgangsmaske:

---

## Einrichtung der AIS-Felder für die Marktkasse aus dem Branchen-ERP Muster

Einrichtung der AIS-Felder für die
Marktkasse aus dem Branchen-ERP Muster
Um aus dem Branchen-ERP Muster schnell die AIS Felder der
Marktkasse einzurichten, muss man nur folgende Schritt-für-Schritt Anleitung
befolgen:
1.
In
[FRZ]
die gewünschte Vorgangsklasse
und Unterklasse für die die Kasse eingerichtet werden soll öffnen /
anlegen.
In diesem Beispiel nehmen wir die 700 - Vorgang mit Unterklasse 9900
– Barverkauf.
2.
Auf dem Tabreiter „Kasse“ sollte das Feld „AIS Gruppe“ leer sein. Wenn das Feld
nämlich leer ist, wird der Bereich „Ersteinrichtung“ mit dem Feld „AIS-Muster“
angezeigt.
3.
In dem Feld „AIS-Muster“ wählt man nun das gewünschte Branchen-ERP Muster aus. In diesem
Beispiel „AMIC_Marktks_Maxi“
4.
Nun gibt es in der Optionbox die Funktion „
Muster Übernehmen
“. Beim
Ausführen dieser Funktion öffnet sich eine Maske, in der eine Vorbelegung für
die AIS Gruppen gemacht werden.
a.
Hier ist es
SEHR WICHTIG
, dass
diese Vorbelegung entweder beibehalten oder ganz konsequent angepasst wird. Das
erste Feld gibt hierbei die Namensgebung vor. Im Beispiel wurde „
Marktks_Maxi_3
“ vorgeschlagen, weil es schon 3
andere Einrichtungen gab.
b.
Will man diese Vorbelegung allerdings abändern, z.B. stattdessen „
Kasse_1
“, so müssen alle anderen Gruppen diesem
Schema folgen.
c.
Aus „
Marktks_Maxi
_Korr_Menge
_3
“
wird also „
Kasse
_Korr_Menge
_1“
Dieses Schema muss so konsequent
beibehalten werden, sonst wird die Einrichtung nicht funktionieren. Man kann
also nur den Anfang (das
Marktks_Maxi
) sowie
das Ende (die
_3
) abändern. Der Rest muss
bestehen bleiben!
5.
Nun klickt man auf F9 – Start bei der Maske „Muster / Import / Export“ und
bestätigt darauffolgende Meldung, ob denn die neuen Felder angelegt werden
sollen, mit „JA“.
6.
Zurück auf der FRZ-Maske wird nun das Feld „AIS Gruppe“ mit der neuen Gruppe
befüllt. In dem Beispiel wäre das „Marktks_Maxi_3“ bzw. „Kasse_1“, je nachdem
welcher Name bei Schritt 4 gewählt wurde.
7.
Wenn man das Feld „
[...]


---

## Einrichtung der Tresenkasse

Einrichtung der Tresenkasse

---

## Einrichtung des Druckbereichs 1100

Einrichtung des Druckbereichs 1100
Für die Beschreibung einer SQL-Liste wurde der neue
Druckbereich 1100 = ‚Sql-Zeilen‘ geschaffen. Man richtet hier (durch Verwendung
der Variante) unterschiedliche Listen ein. In allen anderen Druckbereichen und
im Formularstamm gibt man unter ‚Vorlauf Varianten‘ bzw. ‚Nachlauf Varianten‘
eine oder mehrere Variantennummern des Druckbereichs 1100 ein (durch Komma
getrennt). Man kann also im Vorlauf oder Nachlauf mehrere verschiedene Listen
hintereinander drucken.
In einer Variante des Druckbereichs 1100 wird das
SQL-Statement durch den Namen eines privaten SQL-Textes im Eingabefeld ‚SQLK für
Vor/Nachlauf‘ angegeben (Knopf >Bereich<). Die Parametrisierung des
SQL-Statements kann mit der ‚:‘-Logik erfolgen. Dabei kann auf alle ‚ID_...‘
Werte des Druckbereiches zugegriffen werden, der diese Liste druckt. Die
ID-Namen können im Formulareinrichter aus der F3-Box zur Auswahl der
Druckposition abgelesen werden.
Im Druckbereich einer Variante von 1100 greift man auf
den Wert einer Ergebnisspalte aus dem SQL-Statement mit der Druckposition 503
(Spalte aus einem Ergebnispuffer) zu. Der Name der Spalte wird in das Textfeld
eingetragen.
Beispiel: Lieferscheindruck (aus Auftrag) bei
Teildisposition
SQLK erstellen:
// Priv. SQL Text sqlk_Teildispo_Druck ---
with Auftragsmengen
( wabewid, wabewerfassid,menge,
liefermenge, restmenge, v_numnummer, v_datum )
as
( select  wb.wabewid,wabewerfassid,
if ( wabeworimenge != 0) then wabeworimenge else wabewmenge endif as menge,
if ( wabeworimenge != 0 ) then     Wabeworimenge -
wabewmenge   else
if ( vs.v_statusumwand >2 ) then
wabewmenge else wabewmengedisp + vp.VP_WareDispKorMe  endif
endif  as Liefermenge,
menge -liefermenge restmenge,
vs.v_numnummer,
vs.v_datum
from warenbewegung wb
join
v_posiware vp on vp.wabewid = wb.wabewid   join
vorgangstamm vs on vs.v_id = vp.v_id   join
vorgreservierung vr on vr.v_id = vs.v_id
where
wabewvorgklasse = 400)
select    am.wabewid,
wabewmenge as di
[...]


---

## Einrichtung des Nachrichtenagent dbremote

Einrichtung des Nachrichtenagent dbremote
Der SQL Remote-Nachrichtenagent dbremote wird auf dem
Datenbankserver eingerichtet, auf dem die zu replizierende Datenbank laufen
soll.
Es muss gewährleistet sein, dass bevor der dbremote
startet, immer auch der Datenbankserver und die Datenbank verfügbar und
gestartet sind.
Die Dienste können über Kommandozeile
(Eingabeaufforderung) oder Sybase Central angelegt werden. Die Start-Optionen
für die einzurichtenden Dienste werden vorzugsweise in einer Konfigurationsdatei
(.txt) im „config“-Verzeichnis von Referenz-ERP hinterlegt.

---

## Einrichtung einer allgemeinen Buchungsautomatik

Einrichtung einer allgemeinen
Buchungsautomatik
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver Protokoll
oder Direktsprung
[MSP]
Um einen allgemeinen automatischen Buchungslauf
einzurichten kann ein Mandantenserver-Prozess verwendet werden.
Hierzu dient der Menüpunkt „Mandantenserver Protokoll“
(Direktsprung MSP):
Über die erste Variante „Prozesse im Mandantenserver“
kann nun mit „F8 – Neu“ ein neuer Mandantenserver-Prozess eingerichtet
werden.
Dazu einfach einen
Namen
vergeben (z.B.:
„automatische Buchung“).
Das zu verwendende
Control
ist folgendes:
^jpl FIBUCH_EXTERN
Bei
Sekunden
wird ein Intervall eingetragen (in
Sekunden!), in dem der automatische Buchungslauf abgearbeitet werden soll.
Alle anderen Einstellungen bleiben unberührt. Nach dem
Speichern wird die automatische Buchung vom Mandantenserver in  dem
angegeben Intervall ausgeführt.
Was wird da überhaupt gebucht?
Die allgemeine Buchungsautomatik führt in dem
angegebenen Intervall eine Buchung Vergleichbar mit den Grundeinstellungen des
Pflegers für die
Buchung erfasster
Belege
:
-
Erfasser: Alle Vorgänge
-
Herkunft: Alle Vorgänge
Es werden jedoch
sämtliche erfassten Belege des
aktuellen Jahres und des vorangegangenen Jahres
gebucht.
Dies kann beim ersten Durchlauf ggf. etwas länger
dauern. Alle nachfolgenden Buchungen werden entsprechend schneller
abgearbeitet.

---

## Einrichtungen kopieren

Einrichtungen kopieren
Die Kopierfunktion kann grundsätzlich nur importieren.
Für das Kopierziel sind also die Angaben des zu bearbeitenden Bereiches und der
Variante maßgeblich.  Als Quellangabe ist nur das Formular erforderlich.
Den jeweiligen Kopierumfang bestimmt die gewählte Importfunktion:
Ganzes Formular importieren:
Ersetze die gesamte Einrichtung des aktuell
ausgewählten Formulars durch die des Quellformulars.
Ganzen Bereich importieren:
Ersetze die gesamte Bereicheinrichtung des angegebenen
Bereiches des aktuell ausgewählten Formulars durch die des Quellformulars.
Variante importieren:
Ersetze die Einrichtung der gewählten Variante des
gewählten Bereiches vom aktuell ausgewählten Formular durch die des
Quellformulars.
Einrichtung “wild”
importieren
Bei den normalen Importen können nur Bereiche auf
gleiche Bereiche kopiert werden.  Kopien zwischen unterschiedlichen
Bereichen sind i.a. nicht sinnvoll, weil sie in Bezug auf die druckbaren
Positionen nicht kompatibel sind. Nichts desto trotz kann es nützlich sein, etwa
den Kopf eines Rechnungsformulars auf den Kopf eines Kontraktformulars zu
kopieren. Genau diese eigentlich bereichsfremden Importe machen die “wilden”
Importe, die den gewählten Bereich nur mit ihren gemeinsamen Druckpositionen
kopieren. Man kann so zumindest alle Festtexte und vielleicht noch einige andere
Positionen übernehmen.

---

## Einrichtungen transportieren

Einrichtungen transportieren
Formulare inklusive ihrer Einrichtungen können
zwischen Systemen hin- und hertransportiert werden. Dazu ist der Name einer
Datei anzugeben, in der beliebig viele Formulareinrichtungen abgelegt werden
können.
Achtung:
bei mehreren Exporten hintereinander
werden die jeweils neuesten Exporte hinten angehängt. Vor dem ersten Export kann
ein Löschen dieser Datei nötig sein. (Datei editieren = Löschen)
Das Entladen
(Export Formular)
erzeugt
ein SQL-Script.
Das Beladen
(Import aus Datei
)
führt
dieses Script aus.
Stellen Sie dazu sicher, dass die zu importierenden
Formulare auf der Empfängerseite nicht existieren. Sonst wird die Ausführung
einiger Statements mit den entsprechenden Fehlermeldungen verweigert.

---

## Einrichtung in den Rohwareparametern

Einrichtung in den
Rohwareparametern
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[RWPA]
In
den Rohwareparametern hinterlegt man wie üblich global, pro Rohware oder pro
Abrechnungsschema fest, wie zwei neue Abfragepositionen auf der Rohwarenmaske
behandelt werden sollen (keine Behandlung, nur Anzeige, Eingabe). Dabei handelt
es sich um die Kennzeichen: Einlagerung (Ja/Nein) und Vereinnahmung (Ja/
Nein).
Diese Kennzeichen werden nur
im Einkauf ausgewertet. Werden beide Kennzeichen zusammen eingerichtet und sind
auch beide eingabefähig, dann stellt das Programm sicher, das nur höchstens ein
Kennzeichen auf ‚JA’ steht.
Einlagerung und Vereinnahmung
kann nicht auf einem Rohwarenbeleg parallel erfasst werden.

---

## Einrichtung F6

Einrichtung
F6
Der Aufruf dieser Funktion öffnet die Einrichtung für
den Bereich plus Variante, der aktuell auf der Maske ausgewählt wurde. In der
Einrichtung gibt man Position für Position an was man genau andrucken lassen
möchte. Ein Doppelklick auf eine betretbare Zelle der Zeile des gewünschten
Bereiches startet ebenfalls den Einrichter.
Spalte Pos: Formulardruckposition
Hier wählt man mit F3 die für den Bereich vorhandenen
Druckpositionen aus.
Mit deren Hilfe kann man z.B. Festtexte drucken (Pos 1),
Werte fest bestimmter Druckpositionen wie Kundennummer (106) oder Daten die ein
privater SQL-Text zurückliefert (7). Diese Beispiele wurden in der Grafik oben
verwendet.
Sie auch
Formulardruckpositionen
Spalte Zeile mm / Spalte mm
Die Werte in diesen Spalten haben – abhängig vom
Bereich – verschiedene Bedeutungen:
Bei gedruckten Formularen kann man die Positionen der
Felder millimetergenau ausrichten
Bei Bildschirminformationen können diese Werte auf 0
gelassen werden, dann werden die Felder in einem Textblock dargestellt. Wenn
aber kein Feld existiert, bei dem beide Werte 0 sind, werden die Felder durch
einzelne Textfelder (ähnlich den Userfeldern) dargestellt.
Um die Einrichtung der Position der
Bildschirminfofelder zu vereinfachen, gibt es die Funktion
Spalte mm / Zeile mm generieren
. Hier
können die Position der linken, oberen Ecke und der Zeilenabstand eingegeben
werden. Aus diesen Werten und den Spalten- und Zeilenangaben der Felder wird
dann die ungefähre Millimeter-Position berechnet.
Spalte Text
F3-Auswahl Unterstützung für Tabellenfelder. Aktiv ist
diese F3-Auswahl im Feld ‚Text’, wenn es sich um die folgenden Bereiche,
Idnummern und Tabellen handelt:
Bereich
Idnummer
Tabelle
105
443
PartieStamm
105
333
PartieAddon
105
445
PartieMaskeDaten
1000
453
OWaage
1000
454
OwaageAddon
47
425
WarenbewegungAddon
101
425
WarenbewegungAddon
902
425
WarenbewegungAddon
906
425
WarenbewegungAddon
Bei der Idnummer 22 („Bitmap aus Datei/Archiv“) wird
e
[...]


---

## Einrichtung Lastschrift-Formular

Einrichtung Lastschrift-Formular
Damit diese Funktionalität genutzt werden kann, ist
folgendes einzurichten:
1.
Im Formularwesen muss ein Lastschrift-Formular eingerichtet werden, das dann
später z.B. auf dem Schacht des Druckers gedruckt werden soll. Dabei stehen
folgende Druckpositionen zur Verfügung:
Variablenname
Druckposition
Druckbereich
Bedeutung
EC_Firma
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Mandanten / Firmenname
EC_Betrag
4
      Zahlvariable
950
      Hauptteil EC_Lastschrift
Betrag der Lastschrift in erfasster
      Währung
EC_Waehrung
3
      TextVariable
950
      Hauptteil EC_Lastschrift
Währungskürzel, in der Lastschrift
      erfasst wurde
EC_Datum
11
      Tagesdatum
950
      Hauptteil EC_Lastschrift
Tagesdatum, an dem Lastschrift
      erfasst wurde
EC_Zeit
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Uhrzeit, an der Lastschrift erfasst
      wurde
EC_KartNr
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Kartennummer der
      EC_Karte
EC_KontoNr
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Kontonummer der EC_Karte
EC_BLZ
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Bankleitzahl der
      EC_Karte
EC_GueltigBis
3
      Textvariable
950
      Hauptteil EC_Lastschrift
Gültigkeitsdatum der
      EC_Karte
EC_BelegNr
4
      Zahlvariable
950
      Hauptteil EC_Lastschrift
Referenz auf die Belegnummer, bei
      dem mit Karte bezahlt wurde
EC_BonNr
4
      Zahlvariable
950
      Hauptteil EC_Lastschrift
Laufende Ident-Nummer des
      Zahlungsmittelsatzes
EC_Kasse
4
      Zahlvariable
950
      Hauptteil EC_Lastschrift
Nummer der Kasse, an der mit dieser
      Karte gezahlt wurde
2.
Auf der Zahlungsmaske / Maske der POS-Kasse muss der EPA „Soll ein
Lastschrift-Formular gedruckt werden“ auf Ja gesetzt werden. Dann wird das unter
1. Angelegte Formular auf den in DRZ zugeordneten Drucker gedruckt.
3.
In den Kasseneinstellungen kann man der Kasse unt
[...]


---

## Einrichtung Outlook generell

Einrichtung Outlook generell
Mit dem Direktsprung WWW können die notwendigen
Einrichtungen des System vorgenommen werden.
Um sich die Arbeit zu erleichtern, kann mit dem Setup
Programm die komplette Beispiel Einrichtung per SQL übernommen werden (mit dem
OSQL Direktsprung die Datei \aeins\sql\AoutlookKontakte.sql einpielen).
In der Basiseinrichtung wird den Kundenstamm einer
bestimmten Vertretergruppe in das Outlook System übernommen. Zu den Stammdaten
werden die Offenen Posten, die Besuchsberichte, die letzten 6Rechnungen und die
letzten 3 Aufträge mit in den Notiz Bereich des Kontaktes übergeben. Im
einzelnen sieht die Einrichtung wie folgt aus :
Im Direktsprung www ist ein Satz mit dem F8 (Neu)
Knopf angelegt worden, der wie folgt eingerichtet ist:
Zu beachten ist hier lediglich, dass das Feld „WEB
Sperre“ mit der Kennzeichnung 3 = Outlook versehen werden muss. Im Anschluss an
die Anlage der Stammsatzes können die einzelnen Dateninterfaces mit der F9
Funktion (Einrichtung) eingerichtet werden.
Im folgenden Beispiel sind die Bereiche Kunden, Offene
Posten, Besuche, Rechnungen, Aufträge und Preisliste eingerichtet.

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

## Einrichtung von openTRANS

Einrichtung von openTRANS
Vor der Verwendung von openTRANS sind einige Dinge
einzurichten, um einen einwandfreien Ablauf zu gewährleisten.
Steuerparameter
Der
Steuerparameter 721 – openTRANS
(Lizenz)
muss eingeschaltet sein, um die notwendigen Funktionen,
Varianten und Eingabefelder freizuschalten.
Der
Steuerparameter 850 – Belegänderungssperre durch Beteiligung
von openTRANS
sollte definiert werden, wenn Belege nach Erstellung bzw.
Weiterversand an Drittsysteme nicht geändert werden dürfen.
Der
Steuerparameter 508 – Formulararchiv (Lizenz)
muss
eingeschaltet sein, um Dokumente zu verwalten, an die ein openTRANS angehängt
werden kann.
Der
Steuerparameter 854 – Nur aktuelle Belege bereitstellen für
openTRANS
kann eingestellt werden, wenn ins Dateisystem exportierte Dateien
transferiert werden sollen.
Der
Steuerparameter 855 – Nur aktuelle Belege bereitstellen für
Beleg-Mailversand
kann eingestellt werden, wenn mit openTRANS versehene
Belege aus dem Archiv gesammelt versendet werden sollen.
Der
Steuerparameter 866 - Preismengeneinheit im openTRANS
angeben
legt fest, ob abweichend vom Standard die Preismengeneinheit aus der
Warenposition im XML ausgegeben werden soll. Diese Funktion ist nicht möglich
bei Verwendung einer Mengeneinheitsumschlüsselungsprozedur.
Mengeneinheiten
Hauptmenü
Stammdaten
Konstanten Artikelstamm
Mengeneinheiten
Variante „internationale
Mengeneinheiten“
In der Variante „
internationale Mengeneinheiten
“ werden die
Zuordnungen von Referenz-ERP-eigenen Mengeneinheiten zu internationalen
Mengeneinheiten gepflegt. Dabei kann ein Umrechnungsfaktor und eine
Voreinstellung angegeben werden.
Internationale
      Mengeneinheiten
UN-Mengeneinheit
Auswahl aus Mengeneinheitsangaben
      der vereinten Nationen gemäß
Recommendation N°. 20 - Codes for Units of Measure Used in
      International Trade
Mengeneinheit Referenz-ERP
Mengeneinheit in Referenz-ERP
Faktor UN zu Referenz-ERP
Umrechnungsfaktor Beispiel: eine
      Tonne (Referenz-ERP zu Kilogramm/KGM internation
[...]


---

## Einrichtung von Vorgangsdruckklassen

Einrichtung von Vorgangsdruckklassen
Administration
Drucker
Vorgangsdruckklassen
Direktsprung
[VRGD]
Neben dem Standarddruck ist der Vorgangsdruck über die
Vorgangsdruckklassen
möglich.
Dort kann z.B. eingestellt werden, dass ein Beleg
mehrfach und/oder auf verschiedenen Druckern mit verschiedenen Formularen
ausgegeben wird. An dieser Stelle muss bei Verwendung von Vorgangsdruckklassen
ein Formular angegeben werden, das dem zu versendenden Beleg entspricht.
Bei „Anzahl“ kann die Anzahl der Drucke angeben die im
Falle des Formulardrucks tatsächlich gedruckt werden sollen. Im Fall der
Einstellung „
statt Rechnungsdruck
“ (Kundenstamm des jeweiligen Kunden)
wird einer der Drucke bzw. ggf. der einzige Druck dieses Formulars von dieser
Anzahl abgezogen.
Es findet sich unter
„Formulare/Drucker
zuordnen“
die Felder Belegversand und Mailtyp. Um den Belegversand für diese
Vorgangsdruckklasse zu aktivieren, stellt man den Wert auf „
Ja
“. Bei
„Mailtyp“ kann per F3 ein E-Mail-Bereich angeben werden. Beim Formulardruck wird
die E-Mail-Adresse des Kunden zu dem angegebenen Mailtyp/E-Mail-Bereich
ermittelt und verwendet. Hierbei hat diese Einstellung Vorrang zu einer
eventuellen FRZ-Einrichtung.
Will man einen Formulardruck beispielsweise an zwei
unterschiedliche Empfänger senden, so kann man sich eine weitere Zeile mit dem
gleichen Formular einrichten. Im Feld „Belegversand“ wählt man nun „Exclusiv“
aus. Dieses Formular wird ausschließlich über den Belegversand berücksichtigt.
Für diese Zeile findet kein physikalischer Druck statt, egal welcher Wert bei
Anzahl angegeben wurde.
Möchte man für eine bestimmte Vorgangsart (z.B.
Lieferscheine) grundsätzlich
keinen
Belegversand durchführen, so muss
dies ausdrücklich eingerichtet werden. In so einem Fall muss im Feld
„Belegversand“ ein „Nein“ eingetragen werden. Hierbei wird auch nicht auf die
FRZ-Einrichtung zurückgegriffen!

---

## Einrichtung zur Lieferscheinsignierung

Einrichtung zur Lieferscheinsignierung
Auf einer Einrichtungsmaske kann die
Unterschriftsposition auf dem Lieferschein festgelegt werden. Innerhalb der
Formulararchivabwicklung wird noch festgelegt, in welchem Importverfahren die
Signatur abgearbeitet werden soll. Die Unterschrift wird IMMER auf einer festen
Seite (z.B. 1) eingetragen, die Seitennummer kann eingerichtet werden.

---

## Environmentvariable

Environmentvariable
Syntax
%NAMEDERVARIABLEN%
Purpose
Zur Verwendung in Skripten als Variable
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
Parameter
, Variablen
Beschreibung
Man kann in den Kommandodateien auf
Envirenmentvariablen zugreifen. Diese werden genau wie Parameter und Variablen
gegen deren Inhalt ausgetauscht.
Beispiel
SET OUTFILE %TEMP%\outfile.txt
Select *....

---

## EPAs

EPAs
Folgende bedienerabhängige EPAS existieren auf der
POS-Maske:
Sie sind innerhalb der Option Box mit der Funktion EPA
Einrichter Parameter innerhalb der Maske aufrufbar
1.
Soll im Artikelfeld begonnen werden
(wie auf der bisher
bekannten Maske für Positionserfassungen): wenn er auf „Ja“ steht, wird bei der
Erfassung der einzelnen Positionen im Artikelfeld begonnen – die Menge kann dann
nur noch durch Richtungspfeil nach oben geändert werden. Wenn er auf „Nein“
steht, wird im Eingabefeld der Menge begonnen.
Dieser Parameter wird jetzt
auch bei Änderung der Kundennummer und der Lagernummer ausgewertet.
2.
Soll ein gefundener Preis bestätigt werden
(wie auf der bisher
bekannten Maske für Positionserfassungen): wenn er auf „Ja“ steht, gelangt man
nach Bestätigen des Artikels generell in das Preisfeld, wo dieser evtl.
korrigiert werden kann. Wenn er auf „Nein“ steht, wird der Artikel nach
gefundenem Preis sofort weggeschrieben. Allerdings hat man in diesem Fall noch
die Möglichkeit durch Auslösen der Funktion „Preis manuell ändern“ vor
Bestätigung des Artikels dennoch in das Preisfeld zu gelangen, um so eine
Preisänderung durchzuführen. Diese Funktion ist aber nur aktiv, wenn in der
Parametergruppe ‚Kasse/Barverkauf‘ der SPA „Manuelle Preiseingabe bei Kasse
möglich“ auf „Ja“ gesetzt ist. Wenn kein Preis bzw. ein Nullpreis durch die
Referenz-ERP-Preisfindung gefunden wurde, gelangt man automatisch ins Preisfeld.
3.
4.
Im Verkauf Verprobung mit Listenpreis
(wie auf der bisher
bekannten Maske für Positionserfassungen): wenn er auf „Ja“ steht, gibt es eine
Warnmeldung, wenn der gefundene Preis nach unten geändert wurde. Wenn er auf
„Nein“ eingestellt ist, wird ein nach unten geänderter Preis sofort
akzeptiert.
5.
Warnung bei Bestätigung eines Nullpreises
(Neu, wie auf der
bisher bekannten Maske für Positionserfassungen): wenn er auf „Ja“ steht, gibt
es eine Warnmeldung, wenn ein Nullpreis bestätigt wird, bei „Nein“ wird auch ein
Nullpreis sofort akzepti
[...]


---

## eRechnung - Export

eRechnung - Export
In den Auswahllisten folgenden Auswahllisten steht bei
entsprechender
Lizenzeinrichtung
die Funktion
eRechnung exportieren
zur Verfügung:
•
Rechnung
[REB]
•
Gutschrift
[GUB]
•
Eingangsrechnung
[ERB]
•
Eingangsgutschrift
[EGB]
•
Rohwarenbelege
[RWB]
•
Rohwarenverkaufsbelege
[RWBV]

---

## Ergänzungs-Werte und –Texte in Rohware-Formular-Einrichtungen

Ergänzungs-Werte und
–Texte in Rohware-Formular-Einrichtungen
Hauptmenü
Administration
Formulare/Abläufe
Formulare
Formulareinrichtung
Direktsprung
[FRM]
In
den Druck-Bereichen
•
1 Kopf erste Seite
•
2 Kopf Folgeseite
•
11 Kopf erste Seite RW-Sammeldruck
•
12 Kopf Folgeseiten RW-Sammedruck
•
70 Rohwaren Anieferungszeile
•
80 Rohware-Sammeldr. Einzelkopfinfo
•
81 Rohware-Sammeldr. Einzelfußinfo
•
901 Fuß bis vorletzte Seite
•
902 Fuß letzte Seite
•
911 Fuß bis vorletzte Seite RW-Sammeldruck
•
912 Fuß/Abschluß RW-Sammeldruck
können Positionen zur Ausgabe
von Rohware-Ergänzungsangaben eingerichtet werden.
Dazu
stehen folgende Einrichtungspositionen zur Verfügung:
Für
alle Positionen gilt: Im Detail-Bereich des Formulareinrichter-Moduls (FRM) muß
im Feld
‚Parameter’
die Zeilennummer der korrespondierenden
Definitionszeile aus der Rohwarengruppen-/Abrechnungsschemadefinition für den
Ergänzungs-Wert bzw. –Text angegeben werden.
Die
Position ‚Label...’ (1641,1644) erzeugt jeweils die Ausgabe der dort definierten
Bezeichnung.
Der
jeweilige Ergänzungs-Wert bzw. –Text selbst wird mit den Positionen 1640 bzw
1643 eingerichtet. Die Position 1642 für Ergänzungs-Werte erzeugt die Ausgabe
des Ergebnisses des in der korrespondierenden Definitionszeile angegebenen
privaten SQL-Textes.

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
Varianten des gesamten Formulars ersetzen.
„Ersetzen im Bereich“ gibt an, dass die Ersetzung nur
innerhalb des angegebenen Bereichs stattfinden soll
„In ALLEN Formularen“ kann zusätzlich angewählt
werden. Somit werden die Änderungen für alle Formulare übernommen. Auch hier ist
die Differenzierung des gewählten Bereichs möglich. D.h., dass die Änderung in
allen Formularen stattfindet, in denen der gewählte Bereich vorhanden ist.
Mit der Funktion „Ersetzen“ werden die gewünschten
Änderungen übernommen.

---

## Erstellen der EDI-Datei auf dem PC (ausgehend)

Erstellen der EDI-Datei auf dem PC (ausgehend)
Das Erstellen der Physischen EDI-Datei erfolgt durch
das Programm
Referenz-ERP.Rosi.
GscEdiExport.
Als Parameter wird der
DSN
der Datenbank
übergeben.
Das Programm ermittelt durch die Rosi Einrichtung am
Beleg den Exportordner und erstellt die Datei.
Wichtig ist, dass alle Ordner, die in der Rosi
Einrichtung eingetragen sind, von dem Tool erreichbar und mit Schreibrechten
versehen sind.
Im Profil kann festgelegt werden ob das Programm
direkt angestoßen werden soll, dies über den Mandantenserver läuft oder ein
externer Aufruf nötig ist.

---

## Erstdruck, Formulardruck

Erstdruck, Formulardruck
Mittels dieser Funktionen werden die selektierten
Vorgänge das erste Mal gedruckt und mit dem Druckmerker versehen. Formulardruck
ist ein Wiederholungsdruck. Bei entsprechender Formulareinrichtung kann ein
Vermerk mit ausgewiesen werden.

---

## Erstellung des Rosi-Profils (ausgehend)

Erstellung des Rosi-Profils (ausgehend)
Profil für EDI-Partner anlegen
In dem Profil EDI-Partner werden die Teilnehmer-ILN,
das Kommunikationsprofil, der EDI-Nachrichtentyp und die Nummernkreise
hinterlegt.
1.
Die Anwendung „Rosi Einrichtung“ mit dem Direktsprung [ROSIE] aufrufen.
2.
Die Variante „Rosi Einrichtung“ auswählen.
3.
Mit der Taste „F8“ die Maske zum Anlegen eines neuen EDI-Partners
aufrufen.
=> Die Maske zum Anlagen des EDI-Partners wird geöffnet.
4.
Die Zahl im Feld „ID“ wird vom Programm automatisch vergeben.
5.
Im Feld „Teilnehmer“ den Teilnehmer mit „F3“ auswählen. Sollte der Partner noch
nicht in der Liste stehen kann er im Anwenderformat „af_RosiTeiln“ eingepflegt
werden.
a.
Die Funktion „Itembox/Daten pflegen“ (oder Tastenkürzel
„Shift + F2“) auswählen.
=> Der Pfleger für den EDI-Partner wird
geöffnet.
b.
Im Feld „Nr.“ eine Zahl eintragen.
c.
Im Feld „Textersetzung“ die Bezeichnung „Rosi INVOICE Test“ eingeben.
d.
Im Feld „Kommentar, Schnipsel“ muss nichts mehr eingetragen werden. Dies
geschieht automatisiert.
e.
Im Feld „Aktiv“ die Taste „F3“ betätigen und den Eintrag „aktiv“ auswählen.
f.
Die Eingaben mit der Taste „F9“ speichern. Die Eingabemaske wird
geschlossen.
g.
Die Funktion „Liste aktualisieren“ (oder Taste „F2“) auswählen. Die Auswahl wird
aktualisiert.
6.
Im Feld „Teilnehmer ILN“ die ILN des Kunden eintragen. Diese Angabe steht im
Feld „GLN-Nr.“ im Kundenstamm für den betreffenden Kunden.
7.
Die Funktion „Nachrichtenprofil“ (Optionbox) ermöglicht es nun ein neues
Nachrichtenprofil anzulegen oder ein bereits bestehendes zu editieren (Hängt
davon ab ob im Feld „Nachrichten Profil ID“ ein Profil ausgewählt wurde). Wir
legen ein neues Nachrichtenprofil an.
a.
Die Zahl im Feld „ID“ wird vom Programm automatisch vergeben.
b.
Im Feld „Bezeichnung“ die Bezeichnung „Rosi INVOIC Test“ eingeben.
c.
Im Feld „feste Implemenntation“ die Taste „F3“ drücken und „Invoic D01B“
auswählen.
d.
[...]


---

## Erstellung eines Testmandanten auf einen entfernten Server

Erstellung eines Testmandanten auf einen
entfernten Server
Der Testmandant auf einen entfernten Server kann nur
erstellt werden, wenn eine entsprechende Prozedur erstellt und unter
Einrichterparameter eingetragen wurde.
Die Prozedur muss folgende Eingabeparameter
enthalten.
in_wer: wird ermittelt
in_wohin: Inhalt des Feldes Testdatenbank
in_anwen: Inhalt des Feldes Mailempfänger
in_farbe: Inhalt des Feldes Farbe
Mit „Weiter“ wird der Testmandant auf den entfernten
Server erstellt.

---

## Export Formular

Export Formular
Diese Funktion ist nur für Systemadministratoren frei
geschaltet.
Sie ermöglicht den Export eines markierten Formulars
in eine SQL-Datei z.B. für den Transfer in eine andere Datenbank. Man gibt den
Pfad- und Dateinamen an und wählt dann ok. Verwendet man eine schon vorhandene
Datei mit altem Inhalt für den Export, kann man diese durch die Option ‚Datei
leeren’ vorher leeren. Der Knopf ‚Datei bearbeiten’ öffnet die SQL-Datei im
Editor.

---

## Font Tabellen (Windowsdruck) F9

Font Tabellen (Windowsdruck) F9
Diese Funktion ist nur für Systemadministratoren frei
geschaltet. Sie öffnet die Auswahlliste der Fonttabellen in der man neue
Fonttabellen anlegen kann.
Mehr zu Fonttabellen steht unter
Fontverwaltung beim
Formulardruck
.

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

## Font Zuordnung zum Formular

Font Zuordnung zum Formular
Hier wird über die F3-Auswahl eine Fonttabelle
angegeben, wenn man eine verwenden möchte.
In der
Formulareinrichtung
kann man dann
für jede Position in der Spalte Font über eine F3-Auswahl einen Font aus der
festgelegten Fonttabelle auswählen.
Die Fonttabellen für die F3-Auswahl
müssen vorher mit Hilfe der Funktion
Font Tabellen (Windowsdruck)
vom
Systemadministrator angelegt worden sein.
Verwendet man keine Fonttabelle,
dann wird die Einstellung aus den Feldern Default Font Normal und Default Font
Compres des Druckerstammes [drst] verwendet. Dies aber auch nur, wenn dort das
Feld Windows Druck auf ja steht. In der
Formulareinrichtung
kann man dann
pro dargestellte Position in der Spalte Attribut bestimmen, ob man die normale
oder die kleinere Schrift verwenden möchte. Es ist auch möglich die Schrift
einem ganzen Bereich zuzuordnen.

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

## Formulareinrichtung

Formulareinrichtung
Das Register „Formularbereiche“, zeigt alle dem
Formular zugeordneten Bereiche mit den Varianten in einer Übersicht an.
Formularstamm – Register
      Formularbereiche
Feld
Beschreibung
Bereich
F3
      Auswahl der eingerichteten Formularbereiche
Bereich Bezeichnung
Bezeichnung des ausgewählten
      Bereichs
Variante
Variantennummer des
      Bereichs
Variante Bezeichnung
Bezeichnung der Variante
Anzahl
Anzahl der eingerichteten Positionen
      des ausgewählten Bereichs
Startzeile
Zeile der ersten eingerichteten
      Position im Bereich
Länge
Länge in Zeilen des
      Bereichs
Breite
Breite in Zeilen des
      Bereichs
SQL
      Variantenvorlauf
SQL
      – Vorlaufvariante des Bereichs
SQL
      Variantennachlauf
SQL
      – Nachlaufvariante des Bereichs
SQL
      Textvor-/-nachlauf
SQL
      Textvor- oder Textnachlauf des Bereichs
Funktionen - Register
      Formularbereiche
Funktion
Beschreibung
Hilfe
Öffnet die Hilfe zum Register
      „Formularbereiche“
Speichern
Speichert die vorgenommenen
      Änderungen
Einrichtung
Startet den Formulareinrichter für
      den ausgewählten Bereich und Variante
Variantenzuordnung
Zeigt die fürs Formular
      eingerichteten Varianten zu dem in der Maske angegebenem Bereich an. Hier
      hat man die Möglichkeit Varianten verschiedenen Kriterien
      zuzuweisen.
Die
      Funktion Variantenzuordnung löschen bietet die Möglichkeit die aktuelle
      Variantenzuordnung zu löschen
Bereich löschen
Löscht den gewählten Bereich mit all
      seinen Varianten
Variante löschen
Löscht die für den Bereich gewählte
      Variante
Archiv anzeigen
Öffnet das Archiv für das angegebene
      Formular
Die Gestaltung sämtlicher Formulare der WaWi und der
FIBU (vom Lieferschein bis zum Scheck) geschieht im Formulareinrichter. Hier
sollten die mitgelieferten Musterbeispiele den Anforderungen vor Ort angepasst
werden. (Firmenbezeichnung, Absender, Bankverbindung) .
Bei Vorgängen wird
auch die
[...]


---

## Formulareinrichtung und Zuordnung

Formulareinrichtung und Zuordnung
Hauptmenü
Administration
Formulare / Abläufe
Formulare
oder Direktsprung
[FRM]
Der Pfleger lässt sich mit Einfach- oder
Mehrfachauswahl von der Auswahlliste her über F5 oder F6 starten
Zum Erstellen eines neuen Formulars ist es nötig, über
„Neu“ oder F8 ein neues Formular anzulegen.
Nun besteht die Möglichkeit dieses neue Formular:
1.
Durch manuelle Eingabe aller Bereiche, Varianten und Positionen usw.
selbstständig zusammenzustellen.
2.
Durch Export in der Auswahlliste, das Quellformular in eine Datei zu exportieren
und innerhalb des neu erstellten Formulars über die „Import aus Datei“ Funktion
wieder einzufügen. Dies wird eher bei Transport des Formulars in eine weitere
Datenbank angewendet.
3.
Innerhalb der gleichen Datenbank können gewünschte Bereiche, Varianten oder das
gesamte Quellformular direkt in das neu erstellte Formular zu importieren.

---

## Formulare löschen

Formulare löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
FormularStamm unter der Bedingung: where FormularId
> 0
FormBerEinricht unter der Bedingung: where FormularId
> 0
FormEinrichtung unter der Bedingung: where FormularId
> 0

---

## Formular - Formularzuordnungen zum Vorgang/Unterklasse

Formular
- Formularzuordnungen zum Vorgang/Unterklasse
Diese Seite bestimmt die Formulare für die
Vorgangsunterklasse.
Druck, Vorschau und Bildschirm Formulare können
unabhängig voneinander definiert werden. Gleiches gilt auch für die
Archivierung.
Mit dem Parameter ‚Artikeltextvariante’ kann für eine
Vorgangsunterklasse IMMER eine bestimmte Artikeltextvariante gezogen werden.
Diese Einstellung übersteuert die lagerspezifische Textvariante!
Die Artikeltextvariante wird bei jedem
Vorgangsunterklassenwechsel neu ausgewertet und dem Artikel ggf. der neue
Variantentext zugeordnet.
-
Unterklassen wechseln
-
Belegumwandlungen
Außerdem lassen sich hier die Zuordnungen von
AIS-Gruppen zu Vorgangsunterklassen einstellen. Für genauere Informationen dazu
siehe
Beispiel
eines Informationsfeldes in Vorgängen
.
Einstellungen der Formulare
Formular
Beschreibung
Druck
Wird
      zum Druck des Beleges verwendet
Vorschau
Wird
      für die Anzeige einer Vorschau verwendet
Bildschirm
Wird
      zur Anzeige auf dem Bildschirm verwendet
Auftrag Formular
Angebot Formular
Archivierung
Dieses Formular wird verwendet, um
      ungedruckte Belege vor dem FiBu-Übertrag noch zu archivieren. Das Formular
      wird nicht verwendet, wenn ein regulärer Druck stattfindet!
Referenzdrucker (für
      Archivierung)
Im
      Zusammenhang mit dem obigen Formular sollte ein Drucker eingerichtet sein,
      der dessen Druckeinstellungen und Formatierungen für die Erstellung des
      Archiveintrags beinhaltet. Der Drucker wird physikalisch nicht verwendet,
      muss jedoch erreichbar sein. Deshalb kann hier auch ein virtueller Drucker
      angegeben werden.
Rechnungsformular im
      Barverkauf
Dieses Formular wird für den Druck
      einer Rechnung in der Marktkasse ab einem im Steuerparameter
867 .- Rechnungsdruck
bei Barverkauf festgelegten
      Grenzwert verwendet. Der zu verwendende Drucker wird in der
      Kassensystemverwaltung festgelegt.
Die
      Adresse
[...]


---

## Formulare für Kontoblätter (Typ 220) einrichten.

Formulare für Kontoblätter (Typ 220)
einrichten.
Hauptmenü
Administration
Formulare / Abläufe
Formulare
Direktsprung
[FRM]
Es existieren zu diesem Typ folgende
Formularbereiche:
•
182 Steuersummendruck Kopf für den Einkauf
•
183 Steuersummendetails für den Einkauf
•
184 Steuersummen Fuß für den Einkauf
•
185 Steuersummendruck Kopf für den Verkauf
•
186 Steuersummendetails für den Verkauf
•
187 Steuersummen Fuß für den Verkauf
•
195 Kontrakt-Restmengen-Hinweis Kontenblatt Zeilentyp
•
196 Kontrakt-Hinweis-Überschrift Kontenblatt Zeilentyp
•
197 Warenbewegungs-Hinweiszeile Zeilentyp
•
198 Warenbewegungs-Summenzeile Zeilentyp
•
199 Warenbewegungs-Überschrift Zeilentyp
•
600 Kopf Buchungsjournal/Kontoblatt Formkopf
•
601 Kopf Buchungsjournal/Kontoblatt(Folgekopf) Folgekopf
•
602 Hauptzeile Buchungsjournal/Kontoblatt Zeilentyp
•
603 Gegenzeile Buchungsjournal Zeilentyp
•
605 Textzeile Buchungsjournal/Kontoblatt Zeilentyp
•
606 Bjournal/Kontoblatt Belegartensummen Zeilentyp
•
607 Buchungsjournal Ford/Verb.-Summen Zeilentyp
•
608 Bjournal/Kontoblatt Steuersummen Zeilentyp
•
609 Fuß Buchungsjournal/Kontoblatt Abschluss
•
610 Fuß Bjournal/Koblatt Zwischenabschluss Fuß
•
612 BJ Summenzeile Einzelbewegungen Zeilentyp
•
616 BJ Belegsummen Einleitung Zeilentyp
•
617 BJ Fordersummen Einleitung Zeilentyp
•
618 BJ Steuersummen Einleitung Zeilentyp
•
619 Artikel-Folgetextzeile Kontenblatt Zeilentyp
•
620 Finanzbewegung-Summenzeile Zeilentyp
•
621 Finanzbewegung-Überschrift Zeilentyp
•
622 Finanzbewegung EK-Warebeleg
•
623 Finanzbewegung VK-Warebeleg
Variablen in Kopf und
Fußzeile
Folgende Variablen sind in allen Teilen (Kopf,
Folgekopf, Fuß und Abschluss) verfügbar. Formularbereiche, die nicht separat mit
aufgeführt werden, enthalten nur Festtext oder diese Felder!
ID
Bezeichnung
Typ
Nummer
Bedeutung
ID_KKD_KONTOBLZAEHLER
KontoBlZaehler
Numerisch
4
Nummer des aktuellen
      Kontoblattes
ID_KKD_KONTOBLDATUM
KontoBlDatum
Datum
5
Erstelldatum des
      KontoBlattes
ID_KKD_KONTOB
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
      öffnet Explorer-Fenster für den Pfad zur Importdatei
Wilde Importe
Quellformular
Formularnummer und Bezeichnung des
      Quellformulars
Quellbereich
Bereichnummer und Bezeichnung des
      Quellbereichs
Quellvariante
Variantennummer und Bezeichnung der
      Quellvariante
Zielbereich
Bereichnummer und Bezeichnung des
      Zielbereichs
Zielvariante
Variantennummer und Bezeichnung der
      Zielvariante
Funktionen - Register
      Importe
Funktion
Beschreibung
Hilfe
Öffnet die Hilfe zum Register
      Importe
Import Variante
Importiert die Quellvariante aus dem
      Quellbereich des Quellformulars.
Diese drei Werte müssen entsprechend
      bei „Quellformular für Funktion Import:“ angegeben sein!
Einrichtungen
      kopieren
Import Bereich
Importiert den Quellbereich des
      Quellformulars.
Diese zwei Werte müssen entsprechend
      bei „Quellformular für Funktion Import:“ angegeben sein!
Einrichtungen
      kopieren
Import Formular
Importiert alle Bereiche und
      Varianten des Quellbereichs.
Dieser Wer
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
      EC_Karte
EC_KontoNr
3
      TextVariable
6255
950
      Hauptteil EC_Lastschrift
Kontonummer der EC_Karte
EC_IBAN
3
      TextVariable
6263
950
      Hauptteil EC_Lastschrift
IBAN
      der EC_Karte
EC_BLZ
3
      TextVariable
6256
950
      Hauptteil EC_Lastschrift
Bankleitzahl der
      EC_Karte
EC_BIC
3
      TextVariable
6264
950
      Hauptteil EC_Lastschrift
BIC
      der EC_Karte
EC_GueltigBis
3
      TextVariable
6257
950
      Hauptteil EC_Lastschrift
Gültigkeitsdatum der
      EC_Karte
EC_BelegNr
4
      ZahlVariable
6258
950
      Hauptteil EC_Lastschrift
Referenz auf die Belegnummer, bei
      dem mit Karte bezahlt wurde
EC_BonNr
4
      ZahlVariable
6259
950
      Hauptteil EC_Lastschrift
Laufende Ident-Nummer des
      Zahlungsmittelsatzes
EC_Kasse
4
      ZahlVariable
6260
950
      Hauptteil EC_Lastschrift
Nummer der Kasse, an der mit dieser
      Karte gezahlt wurde
Typ 49 (Scheckdruck)
Formular -50 / Scheckdruck
(Bem.: die Nummer des Sche
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
verwendenden Formulars erfolgt hier nach den üblichen Mechanismen VRGD / FRZ
Die Umstellung des Drucks von Finanzbelegen in der
Kasse beinhaltet nun den Wegfall der fest programmierten Formularsteuerungen. An
ihre Stelle treten vordefinierte Basisformulare (Nummer -51 bis -57), deren
Einrichtungen zum Lieferumfang von Referenz-ERP gehören und die vom Anwender nicht
verändert werden können. Die Basisformulare entsprechen in ihrem Layout
wesentlich der bisher bekannten festen Programmierung und sind auf eine übliche
Bondruckbreite von 40 Zeichen ausgelegt. Der Anwender kann nun alle Formulare
auch für Finanzbelege selbst gestalten und ist dabei auch nicht mehr an
bestimmte Formularnummern gebunden. Die vorhandenen Basisformulare können
selbstverständlich als Vorlagen benutzt werden.
Die neuen Basisformulare sind auf einen höheren
Leistungsumfang ausgelegt, als man dieses von den bisherigen 50er Formularen
kennt. Dafür war es erforderlich, neue Formulartypen zu schaffen, die mit dem
Formulartyp 201 nicht mehr kompatibel sind
[...]


---

## Formularzuordnung

Formularzuordnung
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[RWPA]
In
den Rohwarenparametern sollten die entsprechenden Formulare den
Abrechnungsschritten zugeordnet werden.
In
der Basis-DB sind folgende Rohwarenformulare (RW) bereits eingerichtet
Siehe Muster - Gutschriften im
Anhang!

---

## Für Bedienerklasse kopieren

Für Bedienerklasse kopieren
Hauptmenü
Administration
Nummernkreise
Fibu-Vorgangszuordnung
Funktion
Bedienerklasse
kopieren
Direktsprung
[NKF]
Wenn man eine neue Bedienerklasse eingerichtet hat,
kann man die Nummernkreiszuordnung der Finanzbuchhaltung aus einer anderen
Bedienerklasse kopieren. Dazu steht in der Anwendung „Nummernkreise
Finanzbuchhaltung“ zur Verfügung.
In dem Feld „
Von Bedienerklasse
“ gibt man eine
bestehende Bedienerklasse an, die als Grundlage dienen soll. Hat man die
Bedienerklasse ausgewählt werden in der Tabelle im unteren Bildschirmteil die
dieser Bedienerklasse zugeordneten Einstellungen angezeigt. Das Feld „
nach
Bedienerklasse
“ ist die neue Bedienerklasse, für die man die Einrichtung
übernehmen will.
Wenn man die Funktion startet wird geprüft, ob für die
neue Bedienerklasse eventuell bereits Daten existieren und vor dem Kopiervorgang
darauf hingewiesen.
Ist der Kopiervorgang erfolgreich beendet worden, so
erscheint ein kurzer Hinweis.

---

## FTP Kommunikator

FTP Kommunikator
Die Einrichtung des FTP-Kommunikator sieht wie folgt
aus:

---

## GOTO und :LABEL Statement

GOTO und :LABEL Statement
Syntax
GOTO label;
.
.
.
:label;
Purpose
Befehlsfolgen in Kommandodateien überspringen.
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
EXIT
,
IF
Beschreibung
Eigentlich sind Kommandodateien dafür vorgesehen,
sequentiell abgearbeitet zu werden. Nun kann es aber sein, das man bestimmte
Befehle nicht oder mehrfach abarbeiten muss. Dazu dient GOTO. Da die
Kommandodateien nicht den Anspruch einer Programmiersprache erheben und es sonst
keine Befehle für Schleifen gibt, kann man darüber hinwegsehen, dass dies ein
unter Programmierern gemiedener Befehl ist.
Beispiel
:Nochmal
// Dies ist keine Endlosschleife,
da
// ASK bei Escape die Kommandodatei
beendet
ASK ID des zu reorganisierenden
Datensatzes>ID;
JPL REARG :ID;
GOTO Nochmal;

---

## Grundeinrichtung (ausgehend)

Grundeinrichtung (ausgehend)
Hier werden die grundlegenden Einstellungen für die
Verwendung von Rosi vorgenommen.
Steuerparameter anpassen
Mit dem Steuerparameter 1016 wird festgelegt, mit
welchen Vorgangsklassen Rosi benutzt werden soll.
1.
Die Anwendung „Steuerparameter“ mit dem Direktsprung [SPA] aufrufen.
2.
Den Parameter mit der „SPA_Nr.“ 1016 markieren und die Taste „F5“
betätigen.
=> Die Maske zum Ändern des Steuerparameters wird geöffnet.
3.
Im Feld „Gültig ab“ den Begriff „heute“ eingeben.
4.
Im Feld „EDI-Typ“ die Taste „F3“ drücken und den Eintrag „Rosi“ auswählen.
5.
Im Feld „Klasse“ die Zahl ‚700‘ eingeben.
6.
Das Feld „ggf. Unterklasse“ bleibt leer.
7.
Die Eingaben mit der Taste „F9“ speichern. Die erscheinende Frage „Sollen die
Daten übernommen werden?“ mit „Ja“ bestätigen.
=> Die Maske zum Ändern des
Steuerparameters wird geschlossen.
Allgemeine Rosi-Einrichtungen
Es werden die Ordner für die Archivierung von
fehlerbehaften und korrekten ausgehenden EDI-Nachrichten eingerichtet.
1.
Die Anwendung „Rosi Einrichtung“ mit dem Direktsprung [Rosie] aufrufen.
2.
Die Variante „Rosi Konfiguration“ auswählen.
3.
Mit der Taste „F8“ die Maske zum Anlegen eines Rosi Konfigurations-Parameters
aufrufen.
=> Die Maske zum Anlegen des Rosi Konfigurations-Parameters wird
geöffnet.
4.
Im Feld „Gruppe“ die Taste „F3“ drücken und den Eintrag „Ordner“ auswählen.
5.
Im Feld „Parameter“ die Taste „F3“ den Eintrag „ArchivAusgehende“ auswählen.
6.
Im Feld „Wert“ den Pfad „..\Export\Rosi“ eintragen.
7.
Die Eingaben mit der Taste „F9“ speichern.
=> Datensatz wird gespeichert.
Ein neuer Datensatz kann nun eingegeben werden.
8.
Im Feld „Gruppe“ die Taste „F3“ drücken und den Eintrag „Ordner“ auswählen.
9.
Im Feld „Parameter“ die Taste „F3“ den Eintrag „FehlerAusgehende“ auswählen.
10.  Im
Feld „Wert“ den Pfad „..\Export\Rosi“ eintragen.
11.  Die
Eingaben mit der Taste „F9“ speichern. Anschließend die Maske mit der Taste
„E
[...]


---

## Grundeinrichtung (eingehend)

Grundeinrichtung (eingehend)
Hier werden die grundlegenden Einstellungen für die
Verwendung von Rosi vorgenommen.
Steuerparameter anpassen
Mit dem Steuerparameter 1016 wird festgelegt, mit
welchen Vorgangsklassen Rosi benutzt werden soll.
1.
Die Anwendung „Steuerparameter“ mit dem Direktsprung [SPA] aufrufen.
2.
Den Parameter mit der „SPA_Nr.“ 1016 markieren und die Taste „F5“
betätigen.
=> Die Maske zum Ändern des Steuerparameters wird geöffnet.
3.
Im Feld „Gültig ab“ den Begriff „heute“ eingeben.
4.
Im Feld „EDI-Typ“ die Taste „F3“ drücken und den Eintrag „Rosi“ auswählen.
5.
Im Feld „Klasse“ die Zahl ‚400‘ eingeben.
6.
Das Feld „ggf. Unterklasse“ bleibt leer.
7.
Die Eingaben mit der Taste „F9“ speichern. Die erscheinende Frage „Sollen die
Daten übernommen werden?“ mit „Ja“ bestätigen.
=> Die Maske zum Ändern des
Steuerparameters wird geschlossen.
Allgemeine Rosi-Einrichtungen
Es werden die Ordner für die Archivierung von
fehlerbehaften und korrekten eingehenden EDI-Nachrichten eingerichtet.
1.
Die Anwendung „Rosi Einrichtung“ mit dem Direktsprung [Rosie]
aufrufen.
2.
Die Variante „Rosi Konfiguration“ auswählen.
3.
Mit der Taste „F8“ die Maske zum Anlegen eines Rosi Konfigurations-Parameters
aufrufen.
=> Die Maske zum Anlegen des Rosi Konfigurations-Parameters wird
geöffnet.
4.
Im Feld „Gruppe“ die Taste „F3“ drücken und den Eintrag „Ordner“ auswählen.
5.
Im Feld „Parameter“ die Taste „F3“ den Eintrag „ArchivEingehende“ auswählen.
6.
Im Feld „Wert“ den Pfad „..\Import\Rosi“ eintragen.
7.
Die Eingaben mit der Taste „F9“ speichern.
=> Datensatz wird gespeichert.
Ein neuer Datensatz kann nun eingegeben werden.
8.
Im Feld „Gruppe“ die Taste „F3“ drücken und den Eintrag „Ordner“ auswählen.
9.
Im Feld „Parameter“ die Taste „F3“ den Eintrag „FehlerEingehende“ auswählen.
10.  Im
Feld „Wert“ den Pfad „..\Import\Rosi“ eintragen.
11.  Die
Eingaben mit der Taste „F9“ speichern. Anschließend die Maske mit der Taste
„ESC
[...]


---

## Hinweise zur Entwicklung dieser Funktion

Hinweise zur Entwicklung dieser Funktion
Die Darstellung in Ziffernform (also
„eins-fünf-drei-acht“) ist aus den überlieferten Parametern relativ einfach.
Schwieriger wird es, wenn der Betrag verbal dargestellt werden soll (also
„eintausendfünfhundertachtunddreißig“). Hierfür gibt es kein allgemeingültiges
Verfahren – jede Sprache hat ihre Besonderheiten bei der Umsetzung:
Beispiele hierfür:
Zahlendreher:
deutsch einundfünfzig, englisch fiftyone
Addition von
Teilbereichen:
französisch 92 ist quatrevingtdouze (4 * 20 + 12)
Geschlechtsspezifische
Darstellung:      eine Million, aber eintausend
Mehrzahl:
zwei Millionen aber zweitausend

---

## IF Statement

IF Statement
Syntax
If (  |
DOMAIN(table-name,column-name[,[typ=nnn,len=nnn][,scale=nn]]) |
|
TAB(table-name) |
|
ROWS |
|
INDEX(index-name) |
|
DBERR |
|
VAL(field-name) )
{
...
}
ELSE
{
...
}
Purpose
Einfache Strukturierungsmöglichkeit;
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
GOTO
,
EXIT
Beschreibung
Logische Abfrage um auf bestimmte Ereignisse zu
reagieren. Hierfür gibt es bestimmte Schlüsselwörter:
DOMAIN(Tabelle,Feld)
Wenn das Feld in der Datenbank existiert ==>
TRUE
DOMAIN(Tabelle,Feld,typ=xxx,len=nnn)
Wenn das Feld in der Datenbank existiert und der Typ
und die Länge
stimmen==> TRUE. Typ kann sein:
integer, smallint, char,
long varchar, varchar, binary, time, timestamp, date, double, float, long
binary, var binary, tiny int, unsigned int, bit
DOMAINE(Tabelle,Feld,scale=nn)
Wenn das Feld existiert und die Anzahl
Nachkommastellen stimmt ==> TRUE
TABLE(table-name)
Wenn die Relation table-name existiert ==> TRUE
ROWS==nnn
Wobei nnn eine beliebige Zahl ist. Prüft ob das
vorangegangene Select - Statement die angegebene Zahl zurückliefert. Mögliche
Vergleichsoperatoren sind : ==, >=, <=, <> oder !=, >, <. Dies
sollte verwendet werden um zu prüfen, ob überhaupt Daten vorhanden sind ( If
ROWS==0 ). Es nützt nichts, den DBERR abzufragen, da dieser auch beim einem
Select, dass Daten zurückliefert, DBERR=100 liefert. Das liegt daran, dass alle
Sätze gelesen werden und nach dem letzten Satz natürlich der Fehler 100
auftritt.
DBERR==nnn
Wobei nnn eine beliebige Zahl ist. DBERR ist der von
SYBASE zurückgelieferte Fehler ( z.B. –196 für INDEX NOT UNIQUE). Mögliche
Vergleichsoperatoren sind : ==, >=, <=, <> oder !=, >, <.
INDEX(index-name)
Wenn der Index mit diesem
Namen existiert ==> TRUE.
VAL(maskenfeld)==Wert
Wenn ein Maskenfeld
oder LDB-Feld einen bestimmten Wert annimmt==> TRUE. Mögliche
Vergleichsoperatoren sind : ==, >=, <=, <> oder !=, >, <.
Beispiel
Select * from fibuvorgstamm where
fibuv_nummer is NULL;
IF (ROWS==
[...]


---

## Import per Controlstring

Import per Controlstring
Beispielsweise durch das Absetzen eines Controlstrings
als Anweisung für den mandantenserver kann folgendes JPL abgesetzt werden:
^jpl
vimperzeugebelege <VorgangsKlasse> <VorgangsArt> <Automatik>
<UebernahmeId> <SatzId> <Test> <Status> <Drucken>
<CallBackToken>
Parameter
Typ
Bemerkung
VorgangsKlasse
Integer
Die
      Vorgangsklasse, die importiert werden soll
VorgangsArt
integer
0 =
      Neu (Standard)
1=
      Bearbeitung
Dieser Wert hat bei useCS=1 keine
      Bedeutung
Automatik
integer
0 –
      manueller Aufruf mit GUI
1 –
      automatischer Aufruf ohne GUI (Empfohlen für Aufrufe aus dem
      Mandantenserver oder anderer Automatismen)
UebernahmeId
integer
Übernahmeid, die importiert werden
      soll
SatzId
integer
Satzid, die importiert werden
      soll
Test
Integer
Immer 0 – nur für interne
      Zwecke
Status
Integer
Der
      Status, in dem sich der zu importierende ImportStammsatz
      befindet
Drucken
Integer
NUR
      bei usecs=1 Vorgangsdruck auslösen, wenn Wert = 1
CallBackToken
string
Wenn
      gegeben, wird nach Abschluss dieses Token als Datenbank-Message an alle
      Clients mit dem Namensteil „(callback)“ gesendet.
Beispielaufruf:
^jpl
vimperzeugebelege ^400 0 1 123456 1 0 2

---

## Import per VIMP_Automat

Import per VIMP_Automat
Sie können auch einen asynchronen
Mandantenserverprozess mit der Maske „VIMP_Automat“ anlegen. Dieser verarbeitet
dann in definierten Zyklen die Importe bestimmter Vorgangsklassen.
Als Parameter kann dem VIMP_Automat eine
Vorgangsklasse mitgegeben werden.
Default ist 5150 (LVS)

---

## Inbetriebnahme des externen Displays

Inbetriebnahme des externen Displays
Starten Sie die Software „Referenz-ERP.KassenDisplay.exe“
mit einem Startparameter. Dieser soll den Pfad incl. des Namens der Datei
enthalten, die die Konfigurations- und Anzeigedaten enthält. Den Pfad entnehmen
Sie den Einstellungen „Client“ im Rahmen „Hardware externes Display“ auf der
Registerkarte „Geräte“ in der Kassenverwaltung.
Der Name der Datei setzt sich zusammen aus „Kasse00“+
der Kassennummer + „.kas“. Also für die Kasse 7 „kasse007.kas“.
Beispiel für Kasse 7:
Referenz-ERP.KassenDisplay.exe
\\rechnername\freigabe\kasse007.kas
Nach dem Start des Programms wird zunächst die
Konfiguration gelesen. Diese wird beim Start der Kasse in das gleiche
Verzeichnis wie die im Aufruf angegebene Datei mit der Endung „.kas“
geschrieben. Die Konfigurationsdatei endet auf „.cfg“.
Ist diese Datei noch nicht vorhanden, wird zunächst
die Meldung ausgegeben, dass diese noch nicht vorhanden ist und beim Start der
Kasse erstellt werden wird. Starten Sie einen Kassenvorgang oder die Funktion
„ext. Display testen“ in der Kassenverwaltung, um die Konfigurationsdatei zu
erzeugen.
Ist aus vorherigen Kassenvorgängen eine
Konfigurationsdatei vorhanden, so wird das externe Kassendisplay geöffnet und
zeigt die konfigurierten Felder an.
Hinweis zur Fenster- und Bildschirmgröße:
Ist das Fenster zu groß für den Bildschirm
eingerichtet oder ragt aufgrund der Einrichtung über die Grenzen des sichtbaren
Bildschirms hinaus, so wird dies automatisch korrigiert und eine Meldung
ausgegeben. Sie können mit Hilfe der Funktion „Positionen anzeigen“ aus dem
Icon-Tray der Anwendung die Position und Größe des Fensters abrufen, nachdem Sie
das Fenster auf den korrekten Bildschirm verschoben und in der Größe angepasst
haben. Diese Werte können Sie dann auch in die Kassenkonfiguration übertragen,
um die Meldung zukünftig zu umgehen und das Fenster an der gewünschten Stelle
darzustellen.

---

## JPL Statement

JPL Statement
Syntax
JPL namederprozedur
Purpose
Ruft eine  JPL – Prozedur auf.
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
MAKRO
,
^
Beschreibung
Wenn die einfachen SQL-Befehle nicht mehr ausreichen
um einen komplexen Sachverhalt abzubilden bzw. zu lösen, kann man auch auf
selbstgeschriebene JPL-Prozeduren zurückgreifen. Parameter können wie unter JPL
angegeben werden. Will man dann auf ein Ergebnis dieser Prozedur zurückgreifen,
kann dies zurzeit nur über LDB_Variablen geschehen und zwar in der Form : IF (
VAL(TRANSFER)==1 ).....
Beispiel
JPL zinsrecalc :KTO;
IF (VAL(TRANSFER)==0)
{
PAUSE Zinssaldo für Konto :KTO
erfolgreich errechnet!;
EXIT;
}
update fibuvorgposition ......

---

## Kachel einrichten

Kachel einrichten
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Auf einem bereits eingerichteten Dashboard erreicht
man die Bearbeitungsmaske der Kachel auch direkt über das Kontextmenü (rechte
Maustaste) des Dashboards, wenn man mit der Maus über der Kachel steht.
Feldbezeichnung
Beschreibung
Titel
Der
      Titel dient als Beschreibung der Kachel. Dieser muss eindeutig sein.
      Zusätzlich wird eine Kachel intern über eine eindeutige Ident
      identifiziert. Der Titel kann jederzeit geändert werden.
Darstellungsart
Art
      der Darstellung. Es existieren folgende Möglichkeiten:
•
Text
•
Tabelle
•
Fortschrittsbalken
•
Skala
•
Säulendiagramm
•
Flächendiagramm
•
Liniendiagramm
•
Tortendiagramm
•
Bild
•
Deutschlandkarte
•
Europakarte
•
Kombinationsdiagramm
•
Balkendiagramm
•
Kalender
View/Prozedur
Über
      die private Prozedur oder View werden alle Daten geliefert, die zur
      Erstellung einer Kachel benötigt werden. Dabei unterscheiden sich die
      benötigten Daten je nach Darstellungsart. Eine genaue Beschreibung der
      verschiedenen Darstellungsarten findet man unter „
Prozeduren oder Views für Kacheln
      einrichten
“.
Grundsätzlich werden Views bzw.
      Prozeduren ohne Parameter aufgerufen. Man der Prozedur jedoch eigene
      Parameter mitgeben. Dies können Konstanten, db_variablen oder
      LDB-Variablen (mit vorangestelltem Doppelpunkt) sein. Beispiel
Create procedure p_dash_kachel(in integer
      bedienerid)
.
Refresh aktiv
Hiermit wird gekennzeichnet, ob
      diese Kachel auf eine „Refresh-Prozedur“ reagieren soll (Refresh aktiv =
      Ja) oder nicht.
Bei Klick ausführen:
Die folgenden Felder sind
nur
      alternativ
zu belegen. Sind mehrere Felder belegt, so wird nur die
      erste belegte Funktion ausgeführt. Steht der Mauszeiger auf einer Kachel
      mit einer Funktion, so wird das Handsymbol als Mauszeiger
      verwendet.
Funktion
Hier
      kann eine private oder o
[...]


---

## Kasse

Kasse
Hauptmenü
Administration
Formulare / Abläufe
Formularzuordnung/Vorgansunterklasse
Register Kasse
Direktsprung
[FRZ]
Auf dem Register Kasse werden die AIS-Gruppen und
Felder dem Kassenmodul zugeordnet. Dabei ist zu beachten, dass hier nicht pro
Formularzuordnung, sondern pro AIS-Gruppe die Zuordnung erfolgt. Ändert man hier
also z.B. für die der Unterklasse 1 zugeordneten AIS-Gruppe die Feldzuordnung,
so gilt dies für alle Formularzuordnungen, die dieselbe AIS-Gruppe verwenden. Um
einen Überblick zu haben, wo diese Gruppe überall verwendet wird, existiert ein
Anzeigegrid, in der alle Klasse/Unterklassen angezeigt werden, in der die
AIS-Gruppen verwendet wird.
Da das System nicht weiß, wie die AIS-Feldnamen vom
Anwender vergeben wurden, es jedoch wissen muss, wo die zu verarbeitenden Daten
dargestellt werden sollen, muss eine Zuordnung erfolgen. Es wird dabei zwischen
Pflicht und Zusatzfeldern unterschieden. Die Pflichtfelder sind das Minimum,
welches angegeben werden muss.
Diese Zuordnung kann auch halb-automatisch
erfolgen.
Siehe:
Einrichtung der AIS-Felder für die
Marktkasse aus dem Branchen-ERP Muster
.
Feld
Beschreibung
AIS-Gruppe
Hier
      muss die AIS-Gruppe eingetragen werden, in der die Definition der Kasse
      steht oder zu der die Definition erstellt werden soll. Eine Auswahl aller
      AIS-Gruppen kann mit F3 aufgerufen werden. Wird eine Gruppe ausgewählt,
      für die bereits eine Kassen-Definition existiert, so wird diese sofort
      geladen.
Pflichtfeld
      Kassenfeldname
Es
      wird in der Kasseneinrichtung zwischen Pflichtfeldern und Zusatzfeldern
      unterschieden. Pflichtfelder sind z.B. Artikelnummer, Menge und Preis.
Pflichtfeld AIS-Feldname
Hier
      wird der frei wählbare AIS-Feldname eingetragen. Diese können mit F3
      ausgewählt werden. Zusätzlich werden dann noch – falls es ein Feld in
      einem Grid ist - das AIS-Grid und die tatsächliche Gruppe - falls die
      AIS-Gruppe aus mehreren Gruppen besteh
[...]


---

## Kassen-Einrichtung

Kassen-Einrichtung

---

## Barcode-Schema-Einrichter

Barcode-Schema-Einrichter
Barvorgänge
Stammdaten
Barcode Schema
oder Direktsprung
[BCS]
Feld
Inhalt
Ident
Interne laufende Nummer der
      Definition
Bezeichnung
Bezeichnung dieser
      Barcode-Schema-Definition
Kennung
Präfix des Barcodes. Dieser muss mit
      2 beginnen und kann zwischen 1 und 3 Ziffern lang sein. Bitte beachten
      Sie, dass es keine Überschneidungen geben darf. Richten Sie ausschließlich
      zweistellige Kennungen ein, so sind maximal 10 Kombinationen möglich.
Die
      Position der Kennung sollte immer 1 sein.
Artikelnummer
Geben Sie hier die Position und die
      Länge der Artikelnummer ein.
Menge
Geben Sie hier die Position, die
      Länge und die Anzahl der darin enthaltenen Nachkommastellen der Menge
      an.
Mengeneinheit
Geben Sie hier die Position und die
      Länge der Mengeneinheit an.
Preis
Geben Sie hier die Position, die
      Länge und die Anzahl der darin enthaltenen Nachkommastellen des Preises
      an.
Kommando
Geben Sie hier die Position und die
      Länge eines Kommandocodes ein. Dieser Code kann in einem Makro
      interpretiert und der restliche Barcode zu einem Funktionsaufruf gewandelt
      werden.
Diese Barcodes können nur in der
      Marktkasse ausgewertet werden.
Siehe auch
Kommandos in
      Barcodes
.
Wenn Sie eine Angabe nicht machen wollen, so setzen
Sie bitte die zugehörigen Werte auf 0.
Beispiel für einen Barcode, der eine vierstellige
Artikelnummer, einen vierstelligen Preis mit 2 Nachkommastellen enthält:
Kennung
221
Artikel
0815
Preis
12,34
Leerstelle
0
Prüfziffer
7
Kommandos in Barcodes
Barcodes mit Kommandos können nur in der Marktkasse
ausgewertet werden!
Wenn ein Bandscanner in Betrieb ist, so ist es unter
Umständen mühselig, diesen aus der Hand zu legen, um beispielsweise einen Rabatt
von 3,5% zu erfassen. Für diesen Zweck gibt es Kommandobarcodes. Diese werden
erkannt, wenn die Angabe der Position des Kommandos ungleich 0 und die Länge
größer 0 ist.
Der Gesamte Barc
[...]


---

## Kommentar

Kommentar
Syntax
// Einzeiliger kommentar
/*
Mehzeiliger Kommentar
*/
Purpose
Nicht benötigte Statements auskommentieren /
Befehlsfolgen Dokumentieren.
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Beschreibung
Um Kommandodateien auch später noch zu verstehen ist
es Sinnvoll entsprechende Kommentare einzufügen. Einzeilige Kommentare können
mit mehrzeiligen geschachtelt vorkommen. Ineinander verschachtelte mehrzeilige
Kommentare sind nicht möglich.
Beispiel
/* Entwickler
OH
Datum      20.06.2000-06-20
// Noch ein Kommentar!
*/
// RICHTIG
/* Entwickler
OH
Datum      20.06.2000-06-20
/* Noch ein Kommentar!*/
*/
//FLASCH, da der erste Kommentar hinter
dem ersten „*/„  aufhört!

---

## Konteninformation

Konteninformation
Hauptmenü
Finanzbuchhaltung
Information
Konteninformation
Direktsprung
[KOI]
bzw.
[KOIP]
Wenn der Steuerungsparameter „Anzeige Fremdwährung in
Auswahllisten“ auf
Ja
steht, dann steht eine weitere Variante „Konteninfo
mit Währungsauflösung“ zur Verfügung. Diese zeigt neben der Buchwährung weitere
Zeilen an, die die Beträge in der Währung darstellen, in der sie erfasst wurden.
Zusätzlich existieren noch zwei weiter Spalten. Eine Spalte „
zum
Stichtag
“ zeigt den Fremdwährungsbetrag zum Stichtag (Periodenende)  in
Buchwährung umgerechnet an. Die Spalte „Differenz“ zeigt die Differenz der
Spalte „zum Stichtag“ zu den Beträgen in Buchwährung an, wie sie zum Zeitpunkt
der Erfassung in  den Belegen festgehalten wurden.
Im folgenden Beispiel wird der Einfachheit halber in
Periode 1 eine Rechnung erfasst, in Periode 2 die Zahlung dazu und in Periode 3
die Ausbuchung der Kursdifferenz. Die hier verwendeten Kurse entsprechen nicht
den tatsächlichen Kursen.
Periode 1:
Fremdwährung(PLN)
Tageskurs
Buchwährung(Euro)
Kurs Stichtag(31.01.)
Zum Stichtag(Euro)
Differenz
(zum Stichtag - Buchwährung)
Rechnung
2.345,00
1,1725
2.000,00
Kumuliert(PLN)
2.345,00
2.000,00
1,345
1.743,49
-256,51
Darstellung in der Konteninformation:
Die
Spalte Buchwährung(Euro) wird nicht mit dargestellt.
Periode 2:
Fremdwährung(PLN)
Tageskurs
Buchwährung(Euro)
Kurs Stichtag(31.01.)
Zum Stichtag
Differenz
(zum Stichtag - Buchwährung)
Zahlung
-2.345,00
1,456
-1.610,58
Kumuliert(PLN)
0,00
389,42
1,543
0,00
-389,42
Darstellung in der Konteninformation:
Periode 3:
Die Ausbuchung des Kursverlustes erfolgt in
Buchwährung. Der Kurs ist daher 1.0000.
Fremdwährung(
Euro
)
Tageskurs
Buchwährung(Euro)
Kurs Stichtag(31.01.)
Zum Stichtag
Differenz
(zum Stichtag - Buchwährung)
Ausbuchung
-389,42
1,0000
-389,42
Kumuliert(Euro)
-389,42
-389,42
1,0000
-389,42
0,00
Darstellung in der Konteninformation:
Sobald ein Beleg in einer weiteren Währung (hier
Buchwährung = Euro) erfasst wurde, wird für je
[...]


---

## KUI - Konfigurierbare, universelle Informationsmasken

KUI - Konfigurierbare, universelle Informationsmasken
Dieser Bereich wird nicht mehr mit dieser Version
unterstützt. Zur Umstellung:
KUI -> AIS

---

## Laboreinrichtung löschen

Laboreinrichtung löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
Labormethoden
Laborverfahren
Laborverfahren_Feldname
LaborverfahrenTabcard
LaborverfahrenZuordnung

---

## Leergutverarbeitung

Leergutverarbeitung
Der Einrichterparameter
„Vorgangsklassenliste, für die zusätzlich
Leergut abgefragt werden soll“
steuert die Möglichkeit, dass nach den
regulären Artikeleingaben und Betätigen eines der möglichen Abschlussfunktionen
(mit Druck, ohne Druck, Korrektur) noch zusätzlich ein Leergutfenster aufgeht,
in dem für dieses Lager eingerichteten Leergutartikel (ARS Gruppenzuordnungen)
angezeigt und abgefragt werden.

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
Archiv unterdrücken
Zugehöriges Archiv
      unterdrücken-Kennzeichen aus Druckerstamm
Senden an
Zugehöriges Senden an-Kennzeichen
      aus Druckerstamm
Druck ohne FIBU-Übertrag
Druck mit FIBU-Übertrag
Einzelbeleg
Archivierung
      unterdrücken
VRGD
      Makros ausführen
Hiermit wird festgelegt, ob die
      Makros ausgeführt werden, die bei den
Vorgangsdruckklassen
hinterlegt sind.
      Die Standardvorbelegung lässt sich in den Steuerparametern (
SPA 907
) einstellen.
Nur
      drucken
Wenn
      aktiv werden die Formular-Daten nach VKNR  gerafft und es lässt sich
      ein Formular und ein Drucker auswählen auf welche dann gedruckt
      wird.
Es
      sei ausdrücklich darauf hingewiesen, dass nur ein „auf Papier bringen“
      durchgeführt wird, keine Sonderfunktionen.
Handelt es sich bei dem Drucker um
      einen „Senden an“ erfolgt eine Druckaufbereitung mittels „PDF-Erzeugung“
      die zur Ansicht gebracht wird – es erfolgt aber keine
      Archivierung.
Funktionen
Erwei
[...]


---

## Lizenz

Lizenz
Der Steuerparameter
870 - Belegversand Lizenz
ist ein
Lizenz-Steuerparameter, welcher automatisch mit Erwerb der Belegversandlizenz
aktiviert wird. Dies ist die Grundvoraussetzung für den Belegversand!

---

## Lizenz

Lizenz
Dieses Modul ist Lizenzpflichtig und wird nur über die
Freischaltung im Steuerparameter 1076 freigeschaltet.

---

## Lizenzparameter

Lizenzparameter
Während der Installation werden im Referenz-ERP System die
Lizenzparameter eingetragen, sowie in der Windows Registrierdatenbank. Weiterhin
werden die Lizenzparameter beim Setup in der Datenbank hinterleg, sowie bei den
einzelnen Mandanten in der AmicConf.INI eingetragen. Die Lizenzparameter müssen
vor der Installation bereitliegen, da nur mit gültigem Lizenzschlüssel und
gültiger Seriennummer die Software installierbar ist.

---

## Logdatei im Scanner schreiben(SPA 835)|

Logdatei im Scanner schreiben(SPA 835)|
Mit diesem Steuerparameter kann eingestellt werden, ob
in der neuen Scannersoftware eine Logdatei geschrieben werden soll.

---

## Lösung

Lösung
Die Pascal-Skripte (aber auch beliebige andere Module
in Aeins) können so aufgebaut werden, dass sie die individuell unterschiedlichen
Parameter aus der Datenbank lesen. Dadurch kann gewährleistet werden, dass ein
und dasselbe Skript durch dynamische Parametrisierung bei vielen verschiedenen
Kunden unter sehr unterschiedlichen Bedingungen funktioniert.
Beispiel: Soll eine ASCII-Datei eingelesen werden, so
ist durch das Skript nicht festgelegt, welche Daten an welcher Position im
Skript stehen. Dies ist „von außen“ durch spezielle Datenbankrelationen
steuerbar und somit individuell an jede Aeins-Installation anpassbar.

---

## Löschen einer Zeile in der Einrichtung fürs Protokoll

Löschen einer Zeile in der Einrichtung fürs Protokoll
Es kann eine aktuell markierte Einrichtungszeile des
Protokolls über Shift+Strg+Entf  oder Entfernen des Tabellennamens in der
Spalte Protokolltabellen gelöscht werden.
Es erscheint eine
Sicherheitsabfrage die wie folgt lautet:
Sollen der Tabellenname und die zugehörigen Trigger
‚
Name der Tabelle
‘ wirklich aus der Protokollierung entfernt
werden?
Für eine erneute Protokollierung müsste alles neu eingetragen
werden.
Bestätigt man diese Abfrage mit Ja werden
-
Alle Protokolltrigger (Insert, Update, Delete) der ausgewählten Tabelle
gelöscht.
-
Der Inhalt aus den Tabellen Protokoll_Einrichtung und Protokoll_Einrichtungstamm
für die ausgewählte Tabelle gelöscht.
Für den gelöschten Eintrag findet keine
Protokollierung mehr statt und es kann auch keine Überwachung über den
Funktionsaufruf gestartet werden.
Möchte man diese Tabelle zu einem späteren Zeitpunkt
wieder überwachen muss eine neue Einrichtung stattfinden.
Protokollierungen/Aufzeichnungen zu dieser Tabelle die
bis zu dem Zeitpunkt der Löschung vorgenommen wurden werden nicht aus der
Relation Protokoll entfernt.

---

## Mahnstamm

Mahnstamm
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Funktion Mahnstamm
F6
Direktsprung
[FIMSG]
.
Mahnstamm und Mahnsätze müssen immer gemeinsam
eingerichtet werden, d.h. Wenn es zu einer Mahngruppe und Mahnstufe einen
Datensatz im Mahnstamm existiert, muss für diese Kombination auch mindestens ein
Eintrag in den Mahnsätzen existieren. Der Pfleger „
Mahnsätze
einrichten
“ übernimmt dies automatisch und sollte diesem Pfleger
vorgezogen werden.
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
Buchungstext
Ist
      hier ein Text eingegeben, so wird dieser bei der Übernahme der
      Mahngebühren in die Primanota verwendet, sonst der als
Einrichterparameter
hinterlegte Buchungstext „Text
      Hauptzeile bei Übernahme der Mahnungen in die Primanota“
Formular-Id
Nummer des Mahnformulars, das
      ausgedruckt werden soll. Es kann somit für jede Kombination aus Mahngruppe
      und Mahnstufe ein eigenes Formular mit unterschiedlichem Aufbau bzw. Text
      hinterlegt werden. Man kann aber auch für jede Stufe dasselbe Formular
      hinterlegen und die unterschiedlichen Mahnstufen durch den Mahntext
      kenntlich machen.
Zinsgruppe
Falls Verzugszinsen berechnet werden
      sollen, wird hier die Zinsgruppe angegeben, deren Werte berücksichtigt
      werden sollen. Bei der Berechnung der Mahnzinsen wird nur der
      Soll-Zinssatz herangezogen.
Mahnabstand
Der
      Mahnabstand zwischen zwei Mahnungen. Häufig wird von der Fälligkeit bis
      zur ersten Mahnung noch eine Schonfrist gewährt. In diesem Fall muss hier
      bei Mahnstufe 1 ein Zeitraum von z.B. 14 Tagen eingetragen werden, für
      Mahnstufe 2 und höher wird dann z.B. 10 Tage eingetragen. Somit sind auch
      unterschiedliche Intervalle je Stufe möglich.
Alle folgenden Felder erscheinen nur
      bei a
ktiver

[...]


---

## Mahnsätze

Mahnsätze
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Funktion Mahnsätze
F5
Direktsprung
[FIMSG]
.
Mahnstamm und Mahnsätze müssen immer gemeinsam
eingerichtet werden, d.h. Wenn es zu einer Mahngruppe und Mahnstufe einen
Datensatz im Mahnstamm existiert, muss für diese Kombination auch mindestens ein
Eintrag in den Mahnsätzen existieren. Der Pfleger „
Mahnsätze
einrichten
“ übernimmt dies automatisch und sollte diesem Pfleger
vorgezogen werde.
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
Kontonummer
Mahngebühren werden auf dieses Konto
      gebucht.
Kostenstelle
Bei
      der Übernahme in die Primanota wird diese
Kostenstelle
verwendet.
Kostenträger
Bei
      der Übernahme in die Primanota wird dieser
Kostenträger
verwendet.
Kostenobjekt
Bei
      der Übernahme in die Primanota wird dieses
Kostenobjekt
verwendet.
Mahngebühr
Welche Mahngebühr soll gezogen
      werden? In der Mahngruppe ist hinterlegt, ob die Mahngebühr der kleinsten
      oder der größten Mahnstufe der Mahnung gezogen werden soll.
Kleinste Mahnsumme
Wenn
      beim automatischen Erstellen einer Mahnung die zu mahnende Summe kleiner
      als der hier eingetragene Betrag ist, werden für diesen Kunden keine
      Mahnvorschläge erstellt.

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

## MAKRO oder MAKROF Statement

MAKRO oder MAKROF Statement
Syntax
MAKRO macroname [PAR1 [PAR2 [PAR3 [PAR4]]]];
Purpose
Ausführen eine Pascalskripts
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
JPL
Beschreibung
Wenn die einfachen SQL-Befehle nicht mehr ausreichen,
um einen komplexen Sachverhalt abzubilden bzw. zu lösen, kann man auch auf
selbstgeschriebene PASCAL–Skripte zurückgreifen. Parameter können, wie unter JPL
bzw. dem Pascalinterpreter angegeben werden. MAKRO liest ein in der Datenbank
existierendes Skript, MAKROF liest aus einer Datei, die durch den macronamen
identifiziert wird.
Beispiel
MAKROF c:\copy.pas 100 200

---

## Mandantenserver

Mandantenserver

---

## Mandanten Server – Archiv-Import

Mandanten Server – Archiv-Import
Mittels der Einstellung „Automatik“ auf
JA
lassen sich Archiv-Importe durch den Mandantenserver durchführen.

---

## Mandantenserver-Startarten

Mandantenserver-Startarten
Startart
Direktsprung [MS]
Direktstart des Mandantenservers im
      aktuellen Aeins
User
      MAND
Einloggen des User MAND startet
      direkt in den Mandantenserver
Event
Aufruf über einzurichtendes
      Datenbank-Event
Hauptmenü
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver
Start des Mandantenservers im
      aktuellen Aeins

---

## Mandanten Server – Verwaltungs-Relationen

Mandanten Server – Verwaltungs-Relationen
Relation
MandserProzesse
Hier
      werden die Prozesse mit ID abgelegt, welche vom Mandanten Server
      verarbeitet werden.
MandserStatus
Diese Relation dient der Speicherung
      von statistischen Daten während eines Laufes des Mandantenservers (Fehler,
      Anzahl abgearbeiteter Vorgänge etc.).
Locker
Diese Relation vermerkt alle
      gelockten Datensätze des Systems mittels des Relationsnamens und des
      Schlüsselfeldes.
Der
      blockierende Eintrag wird über die Login-Identifikation
      identifiziert.
Datenstrom
Im
      Datenstrom findet sich ALLES wieder, was Datenaustausch zur Folge hat,
      beispielsweise alle Buchungs- oder Wertstellungs-Mechanismen,
      Stammdaten-Änderungen, wenn sie auch "extern" (in anderen Mandanten oder
      in Fremdprogrammen) Auswirkungen haben sollen. etc.
Der
      Datenstrom-Verteiler oder auch "Mandanten-Server" liest diese Sätze und
      verarbeitet sie mittels definierter Methoden.
MandserProzessliste
Liste der Prozesse, welche vom
      Mandantenserver gehandhabt werden.

---

## Mandantenupdate / -einrichtung

Mandantenupdate / -einrichtung
Das Setup Programm ist in der Lage, mehrere Mandanten
gleichzeitig mit einem Setup zu versehen, in der AeinsSetup.ini Datei braucht
nur vermerkt zu werden, welcher Mandant auch mit in den Automatikprozess mit
integriert werden soll.
Basisdatenbank:

---

## Setup Filialsystem

Setup Filialsystem
Felder
Betrieb
Nummer der Betriebsstätte, danach
      dessen Bezeichnung.
Einrichtung
      Filialsystem
Aktiv unter SQL
      Remote
Publikationen
Eingerichtete Publikationen die für
      die unter der im Feld Betrieb angegebenen Betriebsstätte.
Publikationen, die unter SQL Remote
      aktiv / eingetragen sind.
(
      Diese Informationen findet man in
scview
unter Publikationen
      ).
Remote User
Nummer und Bezeichnung der
      angeschlossenen Filialen, wie sie im Filialsystem von Referenz-ERP eingerichtet
      sind.
Zeigt die unter
scview
angegebenen SQL Remotebenutzer.
Subscriptions
Nummer und Bezeichnung der im
      Filialsystem von Referenz-ERP eingerichteten Subskriptionen.
SQL-Remote Benutzername und
      Subskription unter
scview
Auswahl Betrieb
Zeigt die Liste der angeschlossenen
      Betriebsstätten nach Nummer für die im Feld Betrieb angegebene
      Betriebsstätte.
Sie
      wird für einige Funktionen aus der Funktionsbox benötigt.
Funktionen
Neuaufbau Replikation
Eine
      bestehende Replikation zu einem Kommunikationspartner wird gestoppt und
      neu aufgebaut. Alle nicht übertragenen oder verarbeiteten Nachrichten
      gehen verloren. Notoperation, um eine Synchronisation zwischen 2
      Betriebsstätten unter Inkaufnahme von Datenverlust zu erzwingen.
Der
      Kommunikationspartner muss die gleiche Funktion ausführen.
Komplett Setup
Inkrementelles
      Setup auf alle Remote User und Publikationen. Alle Publikationen,
      Publisher, Remote User, Remote Subscriptions  werden wie in der
      Filialeinrichtung vereinbart dem SQL Remote System hinzugefügt, im SQL
      Remote System geändert oder aus SQL Remote System entfernt.
Komplett deinstallieren
Entfernt
      alle SQL Remote Objekte aus der Datenbank.
Setup Publikationen
Inkrementelles
      Setup auf alle Publikationen. Alle Publikationen  werden wie in der
      Filialeinrichtung vereinbart dem SQL Remote System hinzugefügt, im SQL
      Remot
[...]


---

## Masken für Zahlungsbedingungen

Masken für Zahlungsbedingungen
Direktsprung [ZBM]
Hier wird die Einrichtung der optischen Aufbereitung
für den Ausdruck der Zahlungsbedingung vorgenommen. Sie besteht aus Texten und
Platzhaltern für Parameter und errechnete Werte.
Feldname
Beschreibung
Nummer
Nummer der Aufbereitungsmaske für
      die Zahlungsbedingung
Bezeichnung
Name
      der Aufbereitungsmaske
Text
4
      Zeilen für den Text mit Platzhaltern
Aktuell existieren
folgende
Platzhalter
.

---

## Meldungen in der Aeins-Kasse (Hinweise auf Bedienungs-/Einrichtungsfehler)

Meldungen in der Aeins-Kasse (Hinweise auf
Bedienungs-/Einrichtungsfehler)
1. Bei Aufruf „Barverkaufssystem
Eröffnung/Abschluss
Ursache:
Diesem Arbeitsplatz ist nicht das
Recht zugestanden worden, das Gesamtsystem zu eröffnen.
Abhilfe:
In der Ahoi.ini-Datei muss in der
[ACASH2] – Sektion folgender Eintrag existieren: BVManager=Ja
ACHTUNG auf Groß/Kleinschreibung!
2. Beim Versuch, das Barverkaufssystem
abzuschließen
Ursache:
Um das Gesamtsystem abzuschließen,
müssen alle Kassensitzungen zuvor geschlossen worden sein.
Abhilfe:
Alle Kassen abschließen.
3. Beim Versuch, „Kasseneröffnung/Abschluss“
durchzuführen
Ursache:
Es wird versucht, eine Kasse zu
eröffnen, ohne vorher das Gesamtsystem eröffnet zu haben.
Abhilfe:
Das Barverkaufssystem eröffnen.
4. Beim Versuch, „Kasseneröffnung/Abschluss“
durchführen
Ursache:
In der Ahoi.ini-Datei existiert kein Eintrag fürs
Kassensystem oder für die in der Ahoi.ini-Datei eingetragene Nummer des
Kassensystems ist in der Datenbank keine Kasse in der Kassenverwaltung bzw.
Kassensystemverwaltung eingerichtet.
Abhilfe:
Überprüfen, ob folgender Eintrag in der
[ACASH2]-Sektion der Ahoi.ini-Datei vorhanden ist:
Kassensystem=1
Überprüfen, ob für die in der ACASH2-Sektion
eingetragene Nummer des Kassensystems entsprechende Kassen in der
Kassensystemverwaltung bzw. Kassenverwaltung mit gleicher Nummer eingerichtet
sind.
5. Beim Versuch, eine Kasse abzuschließen
Ursache:
Diese Kasse ist Hauptkasse und besitzt
noch Unterkassen, die noch nicht abgeschlossen sind. Dabei soll jedoch gemäß
SPA-Einstellung (Nummer 52 in der Gruppe Kasse/Barverkauf: Aut. Abschöpfung von
Unterks an Hauptks) die zu dieser Hauptkasse gehörigen Unterkassen automatisch
abgeschöpft werden, um dann z.B. nur auf der Hauptkasse eine Zählung durchführen
zu müssen. Diese Beziehung zwischen Hauptkassen und Unterkassen ist in der
Kassenverwaltung festgehalten. (Hauptkasse steht auf Nein)
Abhilfe:
Da diese Meldung nur bei gesetztem SPA
kommt (Versionen nach
[...]


---

## Mehrmandant Transfer

Mehrmandant Transfer
Zentralmandant
In der zweiten Variante “Mehrmandant Transfer“ werden
alle Datenbanktabellen angezeigt die von dem Mehrmandanten System unterstützt
werden. An dieser Stelle kann Einfluss auf die zu Exportierenden Daten genommen
werden. Durch die Erstellung einer Privaten View kann Einfluss darauf genommen
werden, welche Daten an den Untermandant weitergegeben werden soll. Durch das
Auswählen der Funktion
mms_transfer_stop
wird
die Relation aus der Export Bedingung entfernt.
Achtung:
Beim Erstellen einer Privaten View ist auf jedem
Fall darauf zu achten, dass nur die Daten der Hauptrelation zurückgegeben
werden. Die Privaten Views haben eine vom System her festgeschriebene
Namensgebung.
Diese Namensgebung lautet.:
„p_mmsxml_view_“Relationsname.
Für die Relation Artikel z.B.:
„p_mmsxml_view_Artikel“
Untermandant
Auf der Untermandant Seite stehen nur Prozeduren zur
Verfügung. Sollen übermittelte Daten nicht in eine Relation eingespielt werden,
so wählen Sie bitte die Funktion
mms_transfer_stop
aus.
Auswählen einer Privaten Prozedur oder View
Um einer Relation eine Prozedur oder View hinzuzufügen
wählen Sie bitte die Relation in der Auswahlliste aus und drücken dann die Taste
F5. Je nach dem auf welchen Mandanten sich kann dort eine Prozedur oder ein View
ausgewählt und bearbeitet werden. Mit der Taste F8 kann eine neue Relation
hinzugefügt werden ist nur für den Zentralmandanten wichtig. Dies ist für den
Fall besonders wichtig, wenn für Bestimmte Untermandanten nur bestimmte Artikel
transportiert werden dürfen. Das bedeutet, es kann auf der Senderseite mehrere
Views für eine Relation definieren und anlegen werden. Beim Export wird für
jedem Untermandaten die dementsprechende View aufgerufen.
Achtung:
Wenn ich über F8 eine neue Relation hinzufügen
möchte so ist darauf zu achten, dass der Tabellenname mit dem Alias Name für den
Untermandaten betitelt wird.
z.B.
Artikel p_mmsxml_view_Artikel für einen
Untermandaten
Artikel_UM1 p
[...]


---

## MSG Statement

MSG Statement
Syntax
MSG Text, der angezeigt werden soll;
Purpose
Öffnen einer Messagebox
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
PAUSE
Beschreibung
Hier kann ein Text angezeigt werden. Während die
Dialogbox offen ist, ist die Ausführung der Datei unterbrochen, bis sie mit OK
bestätigt werden. Innerhalb des Textes können auch Parameter bzw. mit ASK
abgefragte Variablen angezeigt werden.
Ist Identisch zum PAUSE Statement;
Beispiel
ASK Welche V_ID>ID;
MSG Es wurde :ID eingegeben!;

---

## Nummernkreise

Nummernkreise

---

## Nummernkreise rücksetzen auf Anfangsstand (inkl. Reservelisten)

Nummernkreise rücksetzen auf Anfangsstand (inkl.
Reservelisten)
Es werden die Daten in folgenden Tabellen
gelöscht:
NUMMERNKRRESERVE
Es werden die Daten in folgenden Tabellen
aktualisiert:
NUMMERNKREISPHYS mit Aktualisierung: set NumKrPhyNeu =
NumKrPhyMinimum

---

## Nummernkreiszuordnung Finanzbuchhaltung

Nummernkreiszuordnung Finanzbuchhaltung
Hauptmenü
Administration
Nummernkreise
Fibu-Vorgangszuordnung
Direktsprung
[NKF]
.
Die Belegnummernvergabe erfolgt in der Fibu analog zur
Ware über sogenannte Nummernkreise. Zur allgemeinen Einrichtung der
Nummernkreise gehört die Einrichtung der Nummernkreise, der Zählkreise und der
Gültigkeiten. Die Beschreibung zur Einrichtung dieser Stammdaten findet man im
allgemeinen Bereich
Stammdaten
. Für die Finanzbuchhaltung gibt es einen
weiteren Pfleger "Fibu-Vorgangszuordnung", in dem für die einzelnen Belegarten
pro Bedienerklasse Einstellungen vorgenommen werden können.
Beschreibung
Bedienerklasse
Hier
      muss eine Bedienerklasse eingetragen sein, wie sie in Referenz-ERP hinterlegt
      ist. Eine Auswahl mit
F3
ist möglich.
Belegart
Hier
      wird die Belegart eingetragen. Mögliche Belegarten sind.
•
ZA
      Zahlungsverkehr Banken
•
AR
      Ausgangsrechnung
•
AG
      Ausgangsgutschrift
•
ER
      Eingangsrechnung
•
EG
      Eingangsgutschrift
•
SO
      Sonstige Belege
•
RP
      Restposten
•
SK
      Skonto
•
AB
      Ausbuchungen
•
WE
      Wechselerfassung
•
KD
      Kursgewinn/Kursverlust
•
JW
      Jahreswechsel
•
EB
      Eröffnungsbuchung
•
IU
      Interne Umbuchung
•
KU
      Kostenträgerumbuchung
•
SE
      Scheckeinreicher
•
ZU
      Zinsumbuchung
•
KO
Kostenobjektumbuchung
Die
      Belegarten SK, KD, IU und ZU existieren nur als automatische
      Buchungen.
Erfassungsform
Man
      kann bei bestimmten Belegarten noch unterscheiden, ob die Einstellungen
      für die automatisch erzeugten Belege (z.B. bei gebuchten Mahngebühren oder
      die Zahlungsbelege beim automatischen Zahlungsverkehr) oder für die
      manuelle Erfassung gelten sollen.
Will man also z.B. im automatischen
      Zahlungsverkehr die Zahlungsbelege buchen, so muss ein Satz eingetragen
      sein, bei dem automatisch
[...]


---

## Nummernkreiszuordnung

Nummernkreiszuordnung
Hauptmenü
Administration
Nummernkreise
Vorgangszuordnung
Direktsprung
[NKV]
Hauptmenü
Administration
Nummernkreise
Nummernkreise
Direktsprung
[NKS]
Hauptmenü
Administration
Nummernkreise
Zählkreise
Direktsprung
[NKZ]
Für
die Belegarten müssen unter Vorgangszuordnung [NKV] Nummernkreise (siehe
Bedienerklasse) eingerichtet sein.
Entsprechende Einrichtungen
[NKS], [NKZ]
sind im Bereich Nummerkreise vorzunehmen.
In
der Basis-DB sind folgende Nummerkreise eingerichtet:
310
RW Anlieferung
315
RW Finalgutschrift
Die
Formulare Vorerfassung und Storno-Anlieferung laufen über Nr.-Kreis 310,
die
Formulare Abschlagsgutschrift, Folgeabschlag und die entsprechenden Storno -
Gutschriften laufen über den Nr. Kreis 315

---

## ODBC Anschluss zur Datenbank

ODBC Anschluss zur Datenbank
Der ODBC Anschluss des Benutzers zu seinen Mandanten
muss korrekt im ODBC Einrichtungsmodul eingetragen sein. Es muss weiterhin
darauf geachtet werden, dass NICHT der User ADMIN diese ODBC Verbindung steuert,
es muss IMMER der aktuelle User diese Verbindung steuern. Das BI Interface nimmt
von sich aus die Setzung der ODBC Verbindung vor, wird aber über einen Externen
CITRIX Applikation Zugriff oder einen SharePoint Zugriff eine Verbindung zur
Datenbank realisiert, so muss die ODBC Verbindung korrekt gepflegt sein.

---

## ODBC Einrichtung

ODBC Einrichtung

---

## PARAMETER beim Dateiaufruf (OSQL)

PARAMETER beim Dateiaufruf
(OSQL)
Syntax
@Datei CONTINUE ON ERROR
oder
@Datei FORMAT BINARY
oder
@Datei PAR1=wert[,PAR2=wert,…]
Purpose
Übergabe von Parametern an die Kommandodatei
Anwendung
Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
@
,
ASK
Beschreibung
CONTINUE ON ERROR
bewirkt, dass die Kommandodatei bei SQL-Felern nicht
abbricht. Siehe
SET
ERROR
.
FORMAT BINARY
öffnet die Datei im Binärmodus. Im Binärmodus werden
Sonderzeichen nicht als Steuerzeichen interpretiert.
PAR1=….
Um nicht für jede Situation eine neue Kommandodatei
schreiben zu müssen, kann man über Parameter diese Variabler gestallten.
Es gibt noch eine zusätzliche Art von Parameter, mit
deren Hilfe man die Kommandodatei in mehrere Bereiche unterteilen kann. Diese
Parameter beginnen mit  &, > oder < . Man kann in der
Kommandodatei Marken setzen die mit & beginnen, und über die Parameter diese
Bereche dann ausführen lassen:
&NAME
==> Nur das was zwischen &NAME und &NAME steht.
>NUMMER       ==>
Nummer sollten Numerisch sein. Alle ab der ersten Marke die kleiner als der
Parameter sind.
< NUMMER      ==>
Nummer sollten Numerisch sein. Alle ab der ersten Marke die größer als der
Parameter sind.
Beispiel1
@C:\SQL\KUNDUPD.SQL KONTOVON=10000
KONTOBIS=20000
//Die Datei könnte folgendermaßen
aussehen
select * from kundenstamm where
kontonummer
between :KONTOVON and
:KONTOBIS
Beispiel2
@C:\SQL\KUNDUPD.SQL &DROP
//Die Datei würde folgendermaßen
aussehen
&DROP;
//Begin
drop table
temp_fibu;
&DROP;
// Endet mit selber Marke
&CREATE;       // Nur
bis hierher wird die Datei ausgfeführt
create table temp_fibu.....

---

## Parameter beim Prozessaufruf

Parameter beim Prozessaufruf
Die Parameter des Webaccess.wsf Prozesses sind wie
folgt zu verstehen:
process
Name der EXE Datei, die überwacht werden soll, im
      Referenz-ERP Fall handelt es sich hier um die Aeins32.exe
Idleloops
Schleifenzähler, der angibt wie
      lange gewartet und geprüft werden soll, bis ein Prozess aus dem Speicher
      entfernt wird, wenn keine CPU Zeit verbraucht worden ist. Die Zeit, die
      der Prozess dann stillsteht, bevor er abgebrochen wird, berechnet sich aus
      :  Sleeptime * IdelLoops in Sekunden
Wait
Diese Zeit, gemessen in
      Sekunden,  gibt an, wie lange das System warten soll, bis mit der
      Prozessüberwachung begonnen wird. Hier handelt es sich um die vorzugebende
      Startzeit eines Prozesses, bis er im Speicher zur Verfügung steht.
      Standardmäßig sollte hier eine 5 angegeben werden
Forever
Es
      kann angegeben werden, das der Überwachungsprozess ewig läuft (/forever=1)
      oder aber nach Beendigung aller zu überwachender Objekte dann selber auch
      anhalten soll (/forever=0)
Sleeptime
Die
      Anzahl von Sekunden, die gewartet wird, bevor eine neue Zeitmessung
      erfolgen soll. Bei der Prozessüberwachung wird zunächst eine Zeit
      gemessen, dann wird gewartet (und zwar sleeptime in Sekunden) um wieder
      eine CPU Zeitmessung vorzunehmen. Ist während dieser beiden Messungen
      keine CPU Zeit verbraucht worden, so wird der Prozess zum ersten mal als
      "nicht arbeitend" gekennzeichnet, folgt nun eine <idleloops> malige
      Kennzeichnung dieses Prozesses als "nicht arbeitend" und zwar direkt
      hintereinander, dann wird der Prozess aus dem System entfernt.
Beispiel einer Mandantenserverüberwachung wäre:
Webaccess.wsf /process=aeins32.exe
/sleeptime=5 /wait=5 /idleloops=50 /forever=1
ACHTUNG:
die Leerzeichen zwischen den
Parametern sind zwingend vorgeschrieben!
Zur Kompletten Einrichtung einer
Mandantenserverumgebung muss zunächst der AeinsCrtrl Prozess gestarte
[...]


---

## Parameterdatei für das DTINT-Verfahren

Parameterdatei für das DTINT-Verfahren
Wenn Sie bei den RFS-Voreinstellungen den Schalter
‚DT-Int Verfahren benutzen‘ auf ‚Ja‘ gestellt haben, benötigt Aeins eine
zusätzliche Parameterdatei zum Einstellen verfahrensspezifischer Merkmale.
Das DT-Iint Verfahren  ist ein hausinternes
Spezialverfahren. Es bietet beim DTA-Austausch erweiterte Möglichkeiten zur
Steuerung  der Valuta. Es ist jedoch nur auf bankinterne Konten begrenzt.
Bei der Erzeugung der DTA Datenträger können keine bankfremden Bewegungen
( Lastschriften / Bankeinzüge ) außerhalb der hauseigenen Bank berücksichtigt
werden.
Legen Sie mit Notepad eine Datei ( z.B. DTINT.INI )
nach folgendem Muster an:
//4-stellige Institutsnummer
INSTITUT=9988
//4-stelliger Interner Textschlüssel
INTERNER_TEXT=1234
//6-stellige Primanota-Nummer (900990 bis 900999)
PN_NUMMER=900999
Für ein ordnungsgemäßes Funktionieren des
DT-Int-Verfahrens sind die Angaben zu  Institut, der internen Textnummer
und der Primanotanummer unbedingt erforderlich. Bitte erfragen Sie diese Werte
in der EDV-Abteilung Ihrer Bank!
Anschließend tragen Sie unter Optionen ( Direktsprung
OPT ) den Pfad und Dateinamen unter folgender Option ein  der Pfad steht
hier als Beispiel, es wird ein gültiges Verzeichnis auf der Festplatte
angenommen !):

---

## Parameter der Datenbankfunktion

Parameter der
Datenbankfunktion
Die Datenbank Funktion muss folgende Struktur
aufweisen:
CREATE FUNCTION p_DBFuncNumText (
in in_ZiffernVorkomma char(15),
in in_ZiffernNachkomma char(15),
in in_Vorzeichen integer,
     // 1 oder -1
in in_Dezimalstellen integer,
in in_Betrag numeric(15,6)
)
RETURNS char(500)
BEGIN
DECLARE text char(200);
// Text erzeugen mit der gewünschten
Darstellung
RETURN text;
END
Erläuterung:
in_ZiffernVorkomma: enthält alle Ziffern vor
dem Dezimalpunkt
in_ZiffernNachkomma: enthält alle Ziffern nach
dem Dezimalpunkt
in_Vorzeichen: ist 1 oder –1 je nach
Vorzeichen
in_Dezimalstellen: wie viel Dezimalstellen
sollen dargestellt werden
in_Betrag: der originale Betrag
Es wird eine Stringvariable (char) als Rückgabe
erwartet.

---

## Parameter für den Positionsteil

Parameter für den Positionsteil
Auch die Abläufe der Erfassung werden entscheidend
durch die Einstellung der Erfassungsparameter für den Positionsteil sowie der
Steuerungsparameter bestimmt.
Sortierreihenfolge beim Sortieren
Hier kann eingestellt werden, ob und wie die
Positionen eines Vorganges beim Abschluss automatisch neu sortiert werden
sollen. Folgende Möglichkeiten bestehen:
Ein entsprechend sortierter Lieferschein kann z.B. für
die Lagerentnahme hilfreich sein.
Ordersatzauswahl auch bei einem Ordersatz
Wenn für den Kunden nur ein Ordersatz vorliegt, kann
die Auswahl über eine Liste nur sinnvoll sein, wenn man auf die Liste anderer
Kunden oder einen Standardordersatz zugreifen will. Ist dies nicht der Fall,
entfällt dieser Schritt und der eine Ordersatz wird direkt gezogen.
Zeilenanzahl der Positionsanzeige
Hier kann eingestellt werden, wie viele erfasste
Positionszeilen angezeigt werden sollen.

---

## Parametrisierung von Pascal-Skripten - Technische Informationen

Parametrisierung von Pascal-Skripten - Technische Informationen
Die Skript-Parameter werden in 2 Relationen
ScriptParam
und
ScriptParamPar
gehalten.
ScriptParamPar
soll in Zukunft durch einen
Foreign-Key über das Attribut
ScriptPId
an die
Relation
S
criptParam
gebunden werden.

---

## PAUSE Statement

PAUSE Statement
Syntax
PAUSE Text, der angezeigt werden soll;
Purpose
Öffnen einer Messagebox
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
MSG
Beschreibung
Hier kann ein Text angezeigt werden. Während die
Dialogbox offen ist, ist die Ausführung der Datei unterbrochen, bis sie mit OK
bestätigt werden. Innerhalb des Textes können auch Parameter bzw. mit ASK
abgefragte Variablen angezeigt werden.
Ist identisch zum MSG Statement
Beispiel
ASK Welche V_ID>ID;
PAUSE Es wurde :ID eingegeben!;

---

## Pfleger für Einrichterparameter (EPA)

Pfleger für Einrichterparameter (EPA)
Hauptmenü
Administration
Steuerung
EPAs zeigen
oder Direktsprung
[EPAZ]
Aufgabe dieses Pflegers ist es, an zentraler Stelle
die bedienerklassenabhängigen EPA-Einstellungen komfortabel und übersichtlich zu
administrieren. Bisher war es nur möglich, die EPAs für Bediener derselben
Bedienerklasse zu setzen, mit der man sich angemeldet hat. Um die EPAs für jede
Bedienerklasse explizit abweichend von der Branchen-ERP-Vorbelegung zu setzen, musste
man sich als Bediener der Bedienerklasse anmelden, für die man den EPA umsetzen
wollte. Außerdem war dieses Umsetzen auch nur direkt auf der Maske möglich.
Wenn man in die Anwendung geht, sind in der dann
erscheinenden Auswahlliste alle im System vorhandenen Einrichtungsparameter
aufgelistet, diese sind nach Maskenname und Anlagedatum geordnet, d.h. die
zuletzt durch Branchen-ERP angelegten Einrichterparameter erscheinen in der Liste oben.
Als Profilbedingung steht der Maskenname zur Verfügung, ebenso das Anlagedatum
des EPAs sowie sein Name bzw. seine Kurzbezeichnung. Für die letzte Bedingung
steht ein Suchalgorithmus zur Verfügung, der z.B. bei Eingabe von „Löschen“ alle
Einrichtungsparameter anzeigt, in deren für den Anwender sichtbaren Beschreibung
die Zeichenkette „Löschen“ vorkommt.
Bem.: den Maskennamen ermittelt man durch Auslösen der
Taste SH+STRG+F5 auf der gewünschten
Maske
Als Profilbedingung ist es dann möglich, sich genau
die zu einer Maske gehörigen Einrichterparameter durch Eingabe des Maskennamens
anzeigen zu lassen, oder durch Abgrenzung des AnlageDatums sich nur die neuesten
Einrichterparameter anzeigen zu lassen.
In der Auswahlliste gibt es folgende Felder:
-
Maskenname, hier wird der Name der Maske angezeigt, für die dieser EPA definiert
ist.
-
EPAName, hier wird der Name des EPAs angezeigt, so wie sie für den Kunden
angezeigt wird.
-
AMIC_Vorbelegung, hier wird die von Branchen-ERP festgelegte Default-Einstellung
angezeigt.
-
Anlagedatum, hier wird das
[...]


---

## Planungsrezept

Planungsrezept
Administration
Werkzeuge
Elara Konfiguration
Mit dem Planungsrezept können Sie Ressourcen planen,
die Sie für die Erstellung eines oder mehrerer Artikel benötigen. So können Sie
beispielsweise Rohwaren einem oder mehreren Zielartikeln zuordnen und so eine
Datengrundlage für die Auswertung Ihrer Bedarfsplanung schaffen.
Achtung:
Trotz des Namensanteils „Rezept“ hat diese Anwendung
keinen direkten Zusammenhang mit den in der Produktion verwendeten Rezepten !

---

## Positionsteil: Anzeige und Erfassung

Positionsteil: Anzeige und Erfassung
Im Positionsteil werden die Positionen eines Vorganges
erfasst bzw. bearbeitet.
Achtung:
Nur vollständig eingerichtete
Formulare und Erfassungsbildschirme ermöglichen die Abwicklung aller Vorgänge.
Nachfolgende Beispiele beruhen auf der Standardeinrichtung von Referenz-ERP. In einer
konkreten Installation ergeben sich optische und inhaltliche Abweichungen.
Oberhalb des Erfassungsteiles wird in drei Zeilen
(einrichtbare) generelle Information zum Vorgang angezeigt (z.B. Kunde,
Vorgangsnummer, ...)
Der Erfassungsbildschirm gliedert sich in drei
Bereiche:
In der oberen Hälfte werden in 12 - 25 Zeilen die
bereits erfassten Positionen angezeigt. Die gerade bearbeitete Zeile wird dunkel
dargestellt.
Unten rechts werden in einer Auswahlbox die möglichen
Erfassungsalter­nativen bzw. Bearbeitungsfunktionen dargestellt.
In Abhängigkeit von der gewählten Funktion wird eine
Erfassungsbox geöffnet, die dann die Eingabe erlaubt.
Anzeige der Positionen
Im Anzeigebereich werden die Positionen so
dargestellt, wie es im Formulareinrichtungsprogramm festgelegt wurde. Häufig
richtet sich die Optik nach dem auszudruckenden Formular, um die visuelle
Kontrolle zu erleichtern. Bis zu 13 Zeilen werden dargestellt. Wenn mehr als 13
Positionen erfasst werden, ändert sich automatisch die Optik des
Anzeigebildschirmes insofern, als am rechten Bildschirmrand eine Bildlaufleiste
erscheint. Sie erlaubt es, ohne den Aufruf spezieller Funktionen mit Hilfe der
Maus im Positionsteil zu blättern.

---

## PPTyp 1: Konvertierungsparameter

PPTyp 1:
Konvertierungsparameter
Bei Datenkonvertierungen wird hinterlegt, welcher
Wert1 in welchen Wert2 umgesetzt wird. Folglich wird in PPWert1 der Wert vor der
Konvertierung und in PPWert2 der Wert nach der Konvertierung eingetragen.
PPWert3 bleibt im allgemeinen leer oder enthält einen Index, sofern vom
Pascalscript eine Verarbeitung mit Arrays erfolgt und die Anzahl der
Konvertierungsparameter nicht feststeht.

---

## PPTyp 2: Positionsparameter

PPTyp 2:
Positionsparameter
Beim Einlesen von ASCII-Dateien muss festgelegt
werden, an welcher Position einer Datenzeile wie viele Zeichen gelesen werden
müssen. So enthält PPWert1 die Position und PPWert2 die Anzahl der Stellen.
PPWert3 bleibt normalerweise leer. Wie bei PPTyp1 kann er aber auch einen Index
enthalten, sofern vom Pascalscript eine Verarbeitung mit Arrays erfolgt und die
Anzahl der Parameter nicht feststeht.
PPAktiv:
Kennzeichnet, ob ein Parameter aktiv
ist oder nicht. Nicht aktive Parameter werden von Pascal-Scripten nicht
eingelesen.
BedKorr:
BedienerId desjenigen Bedieners, der
zuletzt Änderungen am Datensatz durchgeführt hat. (wird automatisch belegt).
System:
System-Kennzeichen, 0: nicht gesetzt;
1: gesetzt.
Datensätze mit gesetztem System-Kennzeichen können nur
herstellerseitig im Hause Branchen-ERP bearbeitet werden.

---

## PPTyp: Typ des Parameters. Mögliche Werte s. unter der Überschrift Auswahlliste ScriptParameterDetails

PPTyp:
Typ des Parameters.
Mögliche Werte s. unter der Überschrift
Auswahlliste
ScriptParameterDetails
Weitere Informationen über die Bedeutung der Typen
unten unter der Beschreibung der Felder PPWert1 bis 3.
PPWert1, PPWert2, PPWert3:
Hier können bis zu 3
Werte angegeben werden, auch Zeichenketten (strings). Die Bedeutung der Werte
richtet sich nach dem
PPTyp
des Parameters. Die u. a. Konvention sollte
eingehalten werden.

---

## ^(prototyped Funktion)

^(prototyped Funktion)
Syntax
^(prototyped funktion)
Purpose
Ausführen einer Funktion C- Funktion
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
JPL
,
MAKRO
Beschreibung
Man kann mit einem ^ vorneweg jede prototyped Funktion
aufrufen. Dazu gehören alle smx_..., alle dbx_... und viele weiter
Funktionen.
Beispiel
^smx_pause "Und hier kommt der Text
hin"

---

## Prozesskontrolle

Prozesskontrolle
Da es ab und zu vorkommen kann, dass ein Prozess in
der Referenz-ERP Umgebung nicht mehr abeitet, und damit die Weiterverarbeitung
blockiert (speziell beim Mandantenserver), kann mit dem Prozessüberwachungsmodul
ein kontolliertes Beenden von Prozessen erreicht werden. Das Modul prüft in fest
vorgegebenen Abständen, ob ein zu überwachender Prozess Rechnerzeit verbraucht
oder nicht, und wenn dann dieser Prozess nach einer vorgegebenen Anzahl von
Schleifen keinen nennenswerte CPU Zeit verbraucht hat, diesen Prozess aus dem
System zu entfernen.

---

## QR-Code

QR-Code
Wenn Sie über die Lizenz AnyBill verfügen, können Sie
diesen in der Anzeige einrichten.
Das Kassendisplay zeigt dann nach dem Bezahlvorgang
einen QR-Code an, mit dessen Hilfe der Kunee seinen Bon auf dem Anybill-Portal
herunterladen kann. Die Verwendung von Anybill zieht weitere Kosten nach sich,
die mit AnyBill zu verhandeln sind.
In der Kassenverwaltung findet sich die Funktion
„AnyBill einrichten“. Wenn Sie diese aufrufen, werden Sie die Möglichkeit
bekommen, die Konfiguration vorzunehmen.
Richten Sie mit Hilfe der Standard-Funktion
„Standardprozeduren“ einen Standard ein. Sie müssen nun noch die Zugangsdaten
einrichten. Es besteht die Möglichkeit die Prozeduren zu individualisieren,
wenn  dies gewünscht wird. (z.B. bei abweichender Shop-Anschrift)
Konfiguration
    Allgemein
Username
Benutzername bei AnyBill
Passwort
Passwort des Benutzers bei
      Anybill
ClientId
ClientId bei Anybill
StoreId
StoreId bei Anybill
Timeout Web
Timeout beim Anruf des Websertvices
      von Anybill (Default 5 Sekunden)
Timeout QR
Länge der Anzeige des QR-Codes (0
      bedeutet kein Timeout) in Sekunden
Konfiguration
    Prozeduren
Verkäufer
Anschrift des Verkäufers für den
      Bonkopf incl Steuernummern.
Kopfdaten
Kopfdaten wie Kassierer,
      Belegnummer, u.ä.
Zeilen
Positions- und
      textzeilen
Summen
Summen mit
      Steuerbeträgen
Zahlung
Zahlungsangaben (Zahlungsmittel,
      Zahlbetrag, Rückgeld)
TSE
TSE-Daten
Fuß
Fußzeile des Belegs mit Grußformel
      und evtl. Coupons
Die Prozeduren lassen sich mit der Funktion „Private
Prozedur“ individualisieren.

---

## Quadriga Anlagenbuchhaltung

Quadriga Anlagenbuchhaltung
Der Import der Daten aus der
Quadriga-Anlagenbuchhaltung ist nicht in den Standardimport integriert.
Es existiert ein Hilfsprogramm, das man als private
Funktion einbinden kann. Dieses Programm hat zwei Parameter. Der erste Parameter
ist der Nummernkreis, der zur Belegnummernvergabe herangezogen wird. Die
Inventurnummer aus der Anlagebuchhaltung wird als Referenznummer übernommen. Der
zweite Parameter ist das Verzeichnis, auf das die Fileselectionbox zeigt.
Tipp
: Man kann sich eine private Funktion
einrichten, die als Controlstring  „^jpl quadriga nummer c::\verzeichnis“
enthält. Dabei ist zu beachten, dass der Doppeltpunkt beim Verzeichnis zweimal
angegeben werden muss und der Backslash (‚\’) nur einmal. Damit entfällt die
Einrichtung des Hilfsprogramms.
Stammdaten
Die von Quadriga übergebenen Sachkonten müssen in
Referenz-ERP eingerichtet sein
Die Kostenstellen müssen in Referenz-ERP eingerichtet sein.
Wird von der Quadriga-Software keine Kostenstelle übergeben, so wird die im
Sachkontenstamm hinterlegte Kostenstelle verwendet.
Im Mandantenstamm muss das Umbuchungskonto
eingerichtet sein.
Die in der Quadriga-Software vergebene Inventarnummer
darf nur numerisch sein. Diese Nummer kann auch alphanumerisch sein.
Vorgehensweise
Die Daten der Anlagenbuchhaltung werden über den
Menüpunkt „LISTEN“ / „Buchungen“ / „Finanzbuchhaltung“ exportiert, indem man
dort als Ausgabemedium „Datei“ wählt. Das Ausgabeformat muss dBase sein.
ACHTUNG:
Einmal ausgelagerte Werte werden von der
Quadriga-Anlagenbuchhaltung nicht gekennzeichnet, so dass ein versehentliches
doppeltes Übertragen der Daten möglich ist. Es muss also durch organisatorische
Maßnahmen sichergestellt werden, dass eine doppelte Übertragung nicht
vorkommt.
In Referenz-ERP wählt man nun das Hilfsprogramm an und wählt
die Datei aus. Die dann importierten Daten werden zuerst in der Relation
Quadriga zwischengespeichert von der sie anschließend in die Primanota
geschrieben werden. Alle Bel
[...]


---

## Rabatte im Barverkauf (SPA 325)

Rabatte im Barverkauf (SPA 325)
Administration
Steuerung
Steuerungsparameter zeigen
Oder Direktsprung
[SPA]
Eine Einstellung des Steuerparameters
325 - Automatische Rabatte bei Kasse
aktiv
kann Rabatte im Barverkauf verhindern.

---

## Rückspeicherung von Excel Mappen mit geänderten Einrichtungen

Rückspeicherung von Excel Mappen mit
geänderten Einrichtungen
Eine abgeänderte Excel-Datei sollte in jedem Falle aus
dem „TEMP“ Bereich in den Dokument Ordner des Anwenders zu speichern, um
ungewünschte Lösch- sowie Überschreibeffekte zu verhindern.
Um nun die Änderungen permanent auch in der Datenbank
abgelegt vorzuhalten, ist die BI Anwendung nicht per einfachem Mausklick
anzuwählen, sondern die SHIFT Taste muss festgehalten werden, um dann per Maus
auf die BI Anwendung im Menü zu klicken.
Beispiel:
Bei gedrückt gehaltener SHIFT Taste ist die Anwendung
Vorgangsübersicht (BI) angeklickt worden:
Es erscheint in der Taskleiste dann ein A1 Sysmbol.
Als nächstes muss nun per Explorer im Windows die Excelmappe angesteuert werden,
die zu dieser Anwendung passt:
Und per Drag and Drop auf der Anwendung A1 im
Orderfeld abgeladen werden. Es geht kurz die Excelmappe auf, wird überprüft um
dann in der Datenbank abgelegt. Vor nun an steht die Änderung den Anwendern zur
Verfügung.

---

## READ

READ
Syntax
READ Dateiname [COUNT]
Purpose
Liest eine Datei im DDS Format in eine
Datenbankrelation ein.
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
IDENTLOAD
,
LOAD
,
DBFLOAD
Beschreibung
Es werden anhand der Datenbeschreibung und der Angabe
der Dateinamen in der Datei die Daten für die Datenbankeinspielung Formatiert
und in die Datenbank eingespielt. COUNT ist die Anzahl Datensätze nach der ein
Vortschrittsmeldung ausgegeben werden soll.
Beispiel
READ c:\Daten\Beschreibung.DDS 50;

---

## Regeleinrichtung [REGEL]

Regeleinrichtung [REGEL]
Hauptmenü
Administration
Formulare / Abläufe
Arbeitsregeln verwalten
oder Direktsprung
[ARV]
oder
[REGEL]
Der Einrichtungsbildschirm einer Regel gliedert sich
in folgende Bereiche:
Arbeitsregel
Hier
      wird die Nummer der Arbeitsregel angegeben.
Nummer 0 darf nicht
      vergeben oder verändert werden.
Diese Nummer der Arbeitsregel wird
      beim Anlegen eines Vorgangs im Vorgangstamm gespeichert und ist unter
      [FRZ] für die entsprechende Vorgangsklasse einzurichten.
Name
Hier
      kann der Name für die Arbeitsregel festgelegt werden.
Kurzbezeichnung
Kurzname für die
      Arbeitsregel
Sperren
Code
Nummer der Funktionalität für die
      Belege mit dieser Arbeitsregel gesperrt werden können
Sperre für …
Belege, die diese Arbeitsregel
      enthalten, können für folgende Funktionalitäten gesperrt
      werden:
1 –
      Druck
2 – Fibu-Übertrag
3 – Korrektur
4 – Ansehen
5 –
      Storno
6 – Umwandlung
7 – Artikel löschen
8 – Artikel neu
      erfassen
9 – Menge korrigieren
10 – Preis korrigieren
11 – Regel
      setzen
12 – Regel korrigieren
Typ
Die
      Art wie der Beleg für die entsprechende Funktionalität behandelt werden
      soll, wenn er diese Arbeitsregel enthält
F3-
      Auswahl:
-keine
-Datenbank Funktion: Eine Funktion, deren Name im
      nächsten Feld anzugeben ist, regelt das Verhalten für den Beleg der diese
      Arbeitsregel enthält.
-SQL-Text: Ein SQL-Text regelt das Verhalten für
      den Beleg
-immer sperren: Belege die diese Arbeitsregel enthalten sind
      immer gesperrt für die jeweilige Funktionalität, z.B. Druck, wird trotzdem
      versucht den Beleg zu drucken erhält man eine entsprechende Fehlermeldung
      mit Hinweis auf die Arbeitsregel
SQL
      / Funktion
Hier
      wird der Name der Funktion angegeben die für die entsprechende
      Funktionalität wirken soll.
Gibt
      man hier einen Namen ein kann über die Funktion
Editieren/Neu F5
in den Pfleger
      gewechselt u
[...]


---

## Reklamation Auswahlliste

Reklamation Auswahlliste
Felder der Auswahlliste
Felder
Beschreibung
Reklamationsnummer
In
      diesem Feld wird die aktuelle Reklamationsnummer angezeigt. Diese wird
      sich automatisch aus dem Nummernkreis gezogen, welcher im
Steuerparameter 1036
zu geordnet
      ist.
Datum
Hier
      wird das Datum eingetragen, zu welchem Datum die Reklamation erfasst
      worden ist. Das Datum wird mit dem Tagesdatum vorbelegt.
Bearbeiter
Gibt
      den Benutzer an, welcher für Reklamation verantwortlich ist.
Geschäftsbereich
Hier
      wird Geschäftsbereich hinterlegt (af_gbereich in
Anwendungsformate
)
Grund 1 - 3
In
      diesen drei Feldern können bis zu drei Reklamationsgründe eingetragen
      werden. Die Reklamationsgründe sind im
Anwenderformat
„af_reklamati“
      hinterlegt, dieses kann um weitere Reklamationsgründe erweitert
      werden.
Beschreibung
In
      dieses Feld wird die Beschreibung zu dieser Reklamation
      eingetragen.
Erstellt von
Benutzer, welcher die Reklamation
      erstellt hat.
Text
      1 – 40
Hier
      werden die Daten angezeigt, welche im
Steuerparameter 1040
hinterlegt sind.
Suchmöglichkeiten der Auswahlliste
Suchen
Beschreibung
Rek-Nr
0…
      99999999999
Bearbeiter
Benutzer Kürzel
Geschäftsbereich
Geschäfts Bereich, welcher in
Anwendungsformate
hinterlegt
      ist (af_gbereich)
Reklamationsgrund
Reklamationsgrund, welcher in
Anwendungsformate
hinterlegt
      ist (af_reklamati)
Funktionen der Auswahlliste
Funktion
Beschreibung
Ändern (F5), Ansehen (F6), Löschen
      (F7), Neu (F8)

---

## Reklamation Pfleger

Reklamation Pfleger
Kasten Reklamation
Felder
Beschreibung
Nummer
In
      diesem Feld wird die aktuelle Reklamationsnummer angezeigt. Diese wird
      sich automatisch aus dem Nummernkreis gezogen, welcher im
Steuerparameter 1036
zu geordnet
      ist.
Datum
Hier
      wird das Datum eingetragen, zu welchem Datum die Reklamation erfasst
      worden ist. Das Datum wird mit dem Tagesdatum vorbelegt.
Bearbeiter
Gibt
      den Benutzer an, welcher für Reklamation verantwortlich ist.
Geschäftsbereich
Hier
      wird Geschäftsbereich hinterlegt
Grund 1 - 3
In
      diesen drei Feldern können bis zu drei Reklamationsgründe eingetragen
      werden. Die Reklamationsgründe sind im
Anwenderformat
„af_reklamati“
      hinterlegt, dieses kann um weitere Reklamationsgründe erweitert
      werden.
Beschreibung
In
      dieses Feld wird die Beschreibung zu dieser Reklamation
      eingetragen.
Erstellt von
Benutzer, welcher die Reklamation
      erstellt hat.
am
Datum der Erstellung
Reklamierer/Verursacher
Felder
Beschreibung
Konto-Nr.
Kunden/Lieferantennummer
Vorgang
Hier
      wird der betreffende Eingangslieferschein oder die betreffende
      Eingangsrechnung zu diesem Lieferanten / Verursacher
      ausgewählt.
Hier
      wird der betreffende Lieferschein oder die betreffende Rechnung zu diesem
      Kunden / Reklamierer ausgewählt.
Datum
Belegdatum
Vorgangsklasse
Vorgangsklasse des ausgewählten
      Vorgangs
Unterklasse
Unterklasse des ausgewählten
      Vorgangs
Ansprechpartner
Hier
      kann ein Ansprechpartner hinterlegt werden. Dieser muss bereits bei Kunden
      angelegt sein. Ansonsten empfiehlt sich das Bemerkungsfeld.
Bearbeiter
Hier
      kann ein Referenz-ERP-Bediener angegeben werden.
Bemerkung
Freitext für
      Zusatzinformationen.
Erledigt
Mit
      dem Schalter kann eine Reklamation auf erledigt gesetzt
      werden.
Erledigt von
Kürzel des Bedieners, der den
      Schalter gesetzt hat
am
Datum an dem der Schalter gesetzt
      wurd
[...]


---

## Rohwarentest Vorlauf

Rohwarentest Vorlauf
Die Vorlaufroutine des Rohwarentests prüft die
Usersetuproutine auf Funktionalität incl. der AktiverMandant Klausel -*
=========================================== und alles aus dem Speicher
rauswerfen =========================================== /d %VM_TESTINSTALL%\bin
====================================================================== Die
Installationsprozedur ändert das INI Verhalten, auf jeden Fall hier
zurückstellen
======================================================================
%vm_system%\bin\setini.exe Mandanten AktiverMandant %3 ahoi.ini

---

## Rollenpflege

Rollenpflege
Die Rollenpflege ist zur Unterstützung für
„Administratoren“ gedacht. Sie stellt die Funktionen und Möglichkeiten der
Variante „Rollenkontext“ zur Verfügung, schränkt die angezeigten
Referenz-ERP-Funktionen aber auf folgende Teilmenge ein:
1)
alle Funktionen der Optionboxen der Varianten unterhalb der Anwendung
„Rollenwesen“
2)
alle Funktionen die im Controlstring die Begriffe „Rollenwesen“,
„AnwendFunktion“ oder „find_key“ enthalten und Direktsprünge darstellen
(prominente Beispiele hierfür sind OSQL, ZUGF, ANWF)
3)
alle Haupt-Menüfunktionen die im Controlstring die Begriffe „Rollenwesen“,
„AnwendFunktion“ oder „find_key“ enthalten
4)
und Funktionen der Optionbox „ob_hauptmenu“ die im Hauptmenü bestimmte
Kontext-Funktionen rollentechnisch steuern.

---

## Sammlung der Kommandos

Sammlung der Kommandos
Syntax
@Dateiname [PARAMETER]
Purpose
Ausführung einer Kommandodatei, Import einer
XML-Datei
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
Parameter
Beschreibung
Um Dateien von OSQL auszuführen, stellt man dem
Dateinamen ein @ voran.
Ob die Datei als Kommandodatei ausgeführt oder als
XML-Import ausgeführt wird, wird an der Dateinamenserweiterung festgemacht. Ist
die Dateinamenserweiterung „XML“ dann wird der Import – wie unter
XMLIMPORT
beschrieben – durchgeführt,
ansonsten die Kommandodatei.
Kommandodateien werden geöffnet und es wird versucht
alle dort mit Semikolon getrennten Befehle (siehe
COMMAND_DELIMITER
) sequentiell
(siehe
GOTO
)
abzuarbeiten. Dateien können ineinander verschachtelt werden, das heißt eine
Datei kann auch eine andere Datei aufrufen. Unter OSQL können diese Dateien auch
per
F3
ausgeführt werden (Abfrage
Dateiname und Parameter per Dialogmaske).
Beispiel
@infile.sql

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
Wenn
      Betragbuchst nicht ausreicht, kann man hier eine zweite Zeile, in der dann
      der Rest steht, einrichten.
BetragbuchstOCX
Text
3
Wie
      Betragbuchst nur ohne Umlaute
BetragbuchstOCX1
Text
3
Wie
      Betragbuchst1 nur ohne Umlaute
AbsKontoNummer
Num.
4
Kontonummer des Absenders also der
      Hausbank
AbsKontoName
Text
3
Name
      des Absenders
AbsBLZ
Num.
4
Bankleitzahl des
      Absenders
AbsBezeichnung
Text
3
Bezeichnung des
      Absenders
AbsSwift
Text
3
Swift/BIC des Absenders
AbsIBAN
Text
3
IBAN
      des Absenders
Adresse
Block
6
Adressfeld
KundenNummer
Num.
4
Kundennummer wie im Kundenstamm
      hinterlegt
GegenNummer
Text
3
Kundennummer beim Kunden wie im
      Kundenstamm hinterlegt
KundUStStatKennz
Text
3
UST.-Ident  wie im Kundenstamm
      hinterlegt
EmpfKontoNummer
Text
3
Kontonummer des
      Empfängers
EmpfBankName
Text
3
Name
      der Bank des Empfängers
EmpfBLZ
Num.
4
Bankleitzahl des
      Empfängers
EmpfSwift
Text
3
Swift/BIC des
[...]


---

## Scheckdruck

Scheckdruck
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Drucken
Direktsprung
[ZHB]
Der Scheckdruck wird über mehrere Einrichterparameter
und Steuerparameter sowie über die eingerichteten Stammdaten gesteuert. Neben
den dieser Maske zugeordneten Einrichterparametern existiert in der Anwendung
DTA ein Einrichterparameter
„Ersteller der Zahlung darf DTA/Scheckdruck
ausführen?“
. Dieser gilt auch für den Scheckdruck. Es ist im Standardfall
hier ein
Ja
eingetragen, so dass keine Einschränkungen vorgenommen
werden. Wenn man hier ein
Nein
einträgt, kann niemals ein und dieselbe
Person die Zahlung erstellen und den Druck ausführen. Dieser Einrichterparameter
ist für das
Vieraugenprinzip
von Bedeutung.
Vor dem Ausdruck erscheint diese Dialogmaske, in der
die nötigen Angaben abgefragt werden. Das Belegdatum kann als
Datum
auf
das Scheckformular gedruckt werden. Ist ein Feld "Schecknummer" auf dem Formular
vorgesehen, kann die nächste Schecknummer hier eingegeben werden. Vorgeschlagen
wird die höchste bereits erstellte Schecknummer. Ist im Hausbankenstamm eine
Nummernkreisnummer für Scheckdruck hinterlegt, wird die Schecknummer aus dem
Nummernkreis gezogen. Dann ist ein Ändern der Schecknummer auch nur über ändern
des Zählerstandes der Zählkreise (Direktsprung
[NKZ]
) möglich.
Auf dem Formular kann ein Positionsteil (503)
eingerichtet werden. Die Sortierung der Zeilen kann unter „Sortierung
Positionsteil“ individuell eingestellt werden.
Im Inlandszahlungsverkehr sind nur Zahlungen in Euro
zugelassen. Hat man jedoch Belege, die noch in DM sind und will diese
begleichen, so können diese umgerechnet werden. Dazu muss bei „Zahlungsbetrag in
Euro umrechnen?“ der Haken gesetzt werden. Es wird nur der zu zahlende Betrag
umgerechnet. Die Beträge der einzelnen zu begleichenden Rechnungen, die im
Positionsteil erscheinen können, werden nicht umgerechnet.
Vor dem Druck werden noch einige Tests
durchgeführt:
•
Hat man die Option „Zahlungsbe
[...]


---

## Schnelleinrichtung der Schriftart für die Bereiche

Schnelleinrichtung der Schriftart für die Bereiche
Formularstamm – Register
      Fonts
Feld
Beschreibung
Bereich
F3
      Auswahl der eingerichteten Formularbereiche
Bereich Bezeichnung
Bezeichnung des ausgewählten
      Bereichs
Variante
Variantennummer des
      Bereichs
Variantenbezeichnung
Bezeichnung der Variante
Zeichensatz
F3
      Auswahl öffnet die Windows Schriftartauswahl
Fonts und Farbe Vorschau
Vorschaufenster des oben
      ausgewählten Bereichs
Funktionen - Register
      Formular
Funktion
Beschreibung
Hilfe
Ruft
      die Hilfe zum Register „Fonts“ auf
Speichern
F9
Speichert die vorgenommenen
      Änderungen.
Ersetze Font
F6
Öffnet einen Anwendungsdialog zum
      Ändern der Schriftart für das gesamte Formular oder nur für den
      Bereich.
Dort
      besteht auch die Möglich ALLEN Formularen die ausgewählte Schriftart
      zuzuweisen!
Archiv anzeigen
CTRL-F12
Öffnet das Archiv für das angegebene
      Formular

---

## Schritt 1: Einrichtung der Steuerparameter

Schritt 1: Einrichtung der Steuerparameter
1.1: Lizenz Steuerparameter
Um das Modul Reklamation zu aktivieren, ist eine
Lizenz erforderlich. (Steuerparameter 1066)
1.2: Reklamationsmaßnahmen Steuerparameter
Um die Maßnahmen (und den dazugehörigen Report)
anzupassen, navigiert man mit dem Direktsprung [SPA] in die Steuerparameter.
Hier sucht man den
Steuerparameter
1040
. Diese Felder können beliebig angepasst werden. Für das aktuelle
Beispiel wird ein Textfeld hinzugefügt, welches anzeigt, ob der Kunde eine
falsche Ware erhalten hat.
Achtung,
eine Änderung der Bezeichner der Felder für Maßnahmen ändert nicht die
Hinterlegung der Daten in der Datenbank.
Wenn
Sie ein Feld anders bezeichnen, bleiben die Inhalte von der vorherigen
Bezeichnung in der Datenbank an gleicher Stelle erhalten.
Eine
Umstellung von Feld 1 auf Feld 2 muss auch in der Datenbank über SQL nachgezogen
werden!
1.3: Reklamation Optionen Steuerparameter
Im
Steuerparameter 1036
werden die Optionen der
Reklamation fest gelegt. Hier wird der Nummernkreis für die Reklamation
festgelegt. Auch die Reporte des Reklamationsmodul können hier angepasst werden,
indem man eigene Reporte in die Anwendungsreporte 1-5 einträgt. Für die
Erstellung der Vorgänge können hier ebenfalls Einstellungen getroffen
werden:
-
Priorität 1 - Makro: Für die Nutzung eines Makros muss ein Makro erstellt
werden, welches den kompletten Erstellungsprozess eines Vorgangs abbildet und am
Ende die V_id (Vorgangs ID) in den Reklamationsstamm einträgt.
-
Priorität 2 - SQL-Prozedur: Wenn kein Makro eingerichtet ist, kann eine
SQL-Prozedur, Sachverhalte vor der Erstellung eines Vorgangs prüfen und ggf. in
den Erstellungsprozess eingreifen.
-
Priorität 3 - Vorgangs(unter)klassen: Nach der SQL-Prozedur wird der Vorgang, je
nach Einstellung der Vorgangs(unter)klasse, vom Standard erstellt.
Für dieses Beispiel wird die Standardeinstellungen des
Reports beibehalten. Als Nummernkreis wird der Standardnummernkrei
[...]


---

## Schritt 2: Report Einrichtung

Schritt 2: Report Einrichtung
2.1: Anwendungsformat Reklamationsgründe
Mit dem Direktsprung [FORMA] navigiert man in die
Formatliste (Variante 2:
Anwendungsformate
). Hier sucht man
nach „af_reklamati“ und bearbeitet den Datensatz. Die Nummern 0-99 sind
gesperrt, die Erstellung eigener Reklamationsgründe erfolgt also ab 100.
2.2: Anwendungsformat Geschäftsformate
In den
Anwendungsformate
n
kann man auch die Geschäftsbereich der Reklamation
erstellen. Hier sucht man nach „af_gbereich“ und bearbeitet den Datensatz. Die
Felder 0-10 sind gesperrt, die Erstellung eigener Geschäftsbereiche erfolgt also
ab 11.
2.3: AIS Felder im Reklamations-Modul
Im
AIS
gibt sowohl in dem Pfleger des
Reklamationsmodul, als auch in den Maßnahmen AIS-Felder. Die Felder des Pflegers
sind in der Gruppe „p_REKLA_Stamm“ und die der Maßnahme in der Gruppe
„p_REKLA_Massnahme“, zu finden.

---

## Schritt für Schritt

Schritt für Schritt
Diese Anleitung zeigt die Einrichtung und
Anpassungsmöglichkeiten des Reklamationsmoduls.

---

## SEPA-Kennzeichen im Mandantenstamm

SEPA-Kennzeichen im Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
Direktsprung
[MND]
Neu hinzugekommen ist eine
Gläubiger-Identifikationsnummer oder kurz Gläubiger-Id. Diese wird nur für das
SEPA-Lastschriftverfahren benötigt. Für Deutschland übernimmt die Deutsche
Bundesbank die Ausgabe der Gläubiger-Identifikationsnummer in Abstimmung mit dem
Zentralen Kreditausschuss. Nähere Informationen findet man auf der Internetseite
der
Deutschen Bundesbank
.
Da bei einer Änderung der Gläubiger-ID oder des Namens
des Auftraggebers bei der SEPA-Lastschrift die alten Werte einmalig mit
Übermittel werden müssen, können die Werte einem Gültigkeitsdatum zugeordnet
werden. Der Name des Auftraggebers wurde bisher aus den Hausbanken gezogen,
daher steht in der ersten Zeile automatisch der Hinweis „(laut Hausbank)“. Wird
eine weitere Zeile mit neuer Gläubiger-ID eingetragen oder wird die erste
Gläubiger-ID erfasst, so wird  der hier hinterlegte Name verwendet. Es ist
nicht
möglich hier „(laut Hausbank)“ einzutragen um dem System
mitzuteilen, dass der Auftraggeber aus den Stammdaten der Hausbank gezogen
werden soll.
Ist eine Zeile einmal gespeichert, kann das
Gültigkeitsdatum nicht mehr geändert werden. Man muss dann die Zeile löschen
(Strg+Shift+Entfernen) und neu erfassen. Ist eine Gläubiger-ID einmal verwendet
worden, so kann die Zeile weder geändert noch gelöscht werden.
Die Gläubiger-ID baut sich folgendermaßen auf:
# 1+2: ISO Ländercode
# 3+4: Prüfziffer
# 5-7 Gläubiger-Geschäftscode oder "ZZZ"
# 8-35 landspezifische Identifizierung
Die Gläubiger-ID wird mit einem Prüfziffernverfahren
auf korrekten Aufbau getestet. Sollte die Prüfung fehlschlagen, wird die Meldung
„Die Prüfziffernberechnung ergibt, dass die Gläubiger-ID nicht korrekt ist.“
ausgegeben. Man kann jedoch die Gläubiger-ID trotzdem speichern.

---

## Server

Server
In der vierten Varianten werden die Einrichtungen für
Server vorgenommen, dies gilt für den Zentral Mandant sowie für den Unter
Mandant. Die Anzeige in der Auswahlliste ist nur für den Zentral Mandant
wichtig. Jeder Server der Verbunden ist wird grün Angezeigt. Server die keine
Verbindung haben werden Rot angezeigt.
Funktionen für den Zentralmandanten
Dateivorbereitung Zentral: Mit der Funktion wird der
Untermandant angelegt der Server angelegt und die Proxy Tabelle
eingerichtet.
Event Anlagen: Mit der Funktion wird der Event
angelegt, der die Daten aus der zwischen Relation in die jeweiligen
Untermandanten verteilt. Das Ereignis ruft die Prozedur
mms_transfer_speicher_evt() auf. Der Name des Ereignisses ist
hole_mms_daten_aus_dem_speicher.
Private Trigger löschen: Mit der Funktion können alle
Trigger gelöscht werden, die auf den Artikel Tabellen wirken.
Trigger Anlegen: Mit der Funktion werden alle Trigger
angelegt, die auf den Artikel Tabellen wirken
Funktionen für den Untermandanten
Dateivorbereitung Zentral: Bereitet den Untermandanten
vor diese legt den Trigger an der auf der Relation MMS_Transfer wirkt.
Event Anlagen: Hier wird der Ereignis angelegt, der
das Abändern von einzelnen Relationen vornimmt. Das bedeutet fehlt eine Spalte
oder mehrere bei einer Tabelle in der Zieldatenbank, so ändert das Ereignis die
Tabelle ab und spielt danach die Daten neu ein.
Masken Felder
Bedeutung
Zentralmadant
Hier
      kann eingestellt werden, ob der Server der Zentral oder Untermandant
      ist
Remotelogin
Hier
      wird das Remote Login eingegeben
RemotePWD
Hier
      wird das Remote Passwort eingegeben
Klasse
Hier
      wird die ODBC Klasse eingegeben entweder SAODBC oder ASAODBC. SAODBC für
      einen Connection String oder die ASAODBC für eine ODBC Verbindung, die auf
      dem Server läuft.
Es ist
      zu empfehlen eine SAODBC Verbindung zu benutzen.
individuellername
Hier
      bitte mmsxml eintragen
Proxy Server
Hier
      wird
[...]


---

## SET APPEND Statement

SET APPEND
Statement
Syntax
SET APPEND [TRIMED] [Filename]
Purpose
Öffnet / schließt eine Ausgabedatei im Modus
„Anhängen“
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET
OUTFILE
,
SET OUTPUT
,
SET TITLE
Beschreibung
Ist ein Dateiname angegeben wird diese Datei geöffnet
und die Daten bzw. die Ausgaben in diese Datei umgelenkt. Die Datei wird nicht
überschrieben sondern die Daten werden an die bestehenden angehängt! Wird kein
Dateiname angegeben, wird die offenen Ausgabedatei geschlossen. Ist keine Datei
offen wird dieser Befehl ignoriert.
Der optionale Parameter TRIMED sorgt
dafür, dass in der Ausgabedatei Leerzeichen am Ende einer Zeile wegoptimiert
werden.
Beispiel
SET APPEND c:\ZINS.SQL;
Select * from fibuvorgstamm;
SET APPEND;

---

## SET DELIMITER Statement

SET
DELIMITER Statement
Syntax
SET DELIMITER [?]
Purpose
Legt das Trennzeichen in Ausgabedateien fest;
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET COMMAND_DELIMITER
Beschreibung
Im Normalfall ist das Trennsymbol zwischen den
Datenspalten das Leerzeichen> <. Will man dies umdefinieren so geschieht
dies durch diesen Befehl. Es wird erst durch erneutes setzen
zurückdefiniert;
Beispiel
SET DELIMITER ,;
Select * from fibuforgklasse;
SET DELIMITER;

---

## SET ERROR Statement

SET ERROR
Statement
Syntax
SET
ERROR  | CONTINUE |
| NOCONTINUE|
| DISPLAY |
| NODISPLAY |
Purpose
Beeinflussung des Verhaltens bei Fehlern.
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
CONTINUE
,
SET OUTERR
Beschreibung
Mit SET ERROR kann das allgemeine Verhalten bei SQL –
Fehlern eingestellt werden.
SET ERROR CONTINUE
         ==> Datei hält nicht bei
Fehlern an.
SET ERROR NOCONTINUE
==> Beendung der Kommandodatei bei
Fehlern. Dies ist die Standarteinstellung
SET ERROR
DISPLAY
==> Fehlerbildschirm wird angezeigt. Dies ist
die Standardeinstellung.
SET ERROR NODISPLAY
       ==> Keine Anzeige von
Fehlermeldungen.
Beispiel
SET ERROR CONTINUE;
SET ERROR NODISPLAY
Select * from
DIESERELATIONGIBTSNICH;
MSG Hier kam keine Fehlermeldung;
SET ERROR DISPLAY
Select * from
DIESERELATIONGIBTSNICH;
SET ERROR NOCONTINUE;

---

## SET KEYBOARDINTERRUPT Statement

SET KEYBOARDINTERRUPT Statement
Syntax
SET KEYBOARDINTERRUPT [OFF] | [ON]
Purpose
Unterbrechung per ESCAPE-Taste Programmweit ein und
ausschalten
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Beschreibung
Es gibt in Aeins bestimmte Anwendungen, die sich durch
das Drücken der ESCAPE-Taste abbrechen lassen – z.B. Dateneinspielungen,
Kommandodateien, usw. . Wenn dieses Verhalten nicht gewünscht ist, so kann man
diese Unterbrechungen abschalten mit SET KEYBOARDINTERRUPT OFF. Dies gilt dann
fürs gesamte Programm! Mit der Befehlsfolge SET KEYBOARDINTERRUPT ON wird die
Unterbrechungsmöglichkeit eingeschaltet.

---

## SET OUTFILE Statement

SET OUTFILE
Statement
Syntax
SET OUTFILE [TRIMED] [Filename]
Purpose
Öffnet / schließt eine Ausgabedatei im Modus
„Überschreiben“
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET
APPEND
,
SET OUTPUT
,
SET TITLE
Beschreibung
Ist ein Dateiname angegeben wird diese Datei geöffnet
und die Daten bzw. die Ausgaben in diese Datei umgelenkt. Die Datei wird
überschrieben! Wird kein Dateiname angegeben, wird die offene Ausgabedatei
geschlossen. Ist keine Datei offen wird dieser Befehl ignoriert.
Der
optionale Parameter TRIMED sorgt dafür, dass in der Ausgabedatei Leerzeichen am
Ende einer Zeile wegoptimiert werden.
Beispiel
SET OUTFILE c:\ZINS.SQL;
Select * from fibuvorgstamm;
SET OUTFILE;

---

## SET TITLE Statement

SET TITLE
Statement
Syntax
SET TITLE text;
Purpose
Schreibt Text in eine offene Ausgabedatei
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET
APPEND
,
SET OUTFILE
,
SET OUTPUT
Beschreibung
Um in eine Ausgabedatei Zusatzstatement oder
Beschreibungen zu schreiben, kann SET TITLE verwendet werden;
Beispiel
SET OUTFILE c:\FIBUKL.SQL;
SET COMMAND_DELIMITER #;
SET TITEL delete from
FiBuVorgKlasse;#
SET TITLE LOAD;#
SET TITLE insert into FiBuVorgKlasse
(…) values(%s)#
SET DELIMITER ,#
Select * from fibuvorgstamm#
SET TITLE LOAD;#
SET COMMAND_DELIMITER ;#
SET DELIMITER;
SET OUTFILE;

---

## SHOW BUFFER Statement

SHOW BUFFER
Statement
Syntax
SHOW BUFFER [buffer-name];
Purpose
Anzeige der/des Buffers
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW
CURSOR
,
SHOW TABLE
,
SHOW VIEW
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
SHOW BUFFER ohne Name des Buffers zeigt alle aktive
Datenbuffer an. Wird ein Name mit angegeben, werden die Daten, die von diesem
Buffer gehalten werden ausgegeben.
Beispiel
SHOW BUFFER KINFO;

---

## SHOW CURSOR

SHOW CURSOR
Syntax
SHOW CURSOR [cursor-name];
Purpose
Anzeige der/des Cursor
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW BUFFER
,
SHOW TABLE
,
SHOW VIEW
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
SHOW CURSOR ohne Name zeigt alle aktive
Datenbankcursor an. Wird ein Name mit angegeben, werden die Daten, die im
letzten gelesenen Satz enthalten sind angezeigt.
Beispiel
SHOW CURSOR CSQL;
//Csql ist der Cursor der von OSQL
verwendet wird

---

## SHOWERR Statement

SHOWERR Statement
Syntax
SHOWERR Feldname;
Purpose
Anzeige des letzten Datenbankfehlers in einem
Maskenfeld;
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW TABLE
,
SHOW VIEW
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
Werden die Dialoge die den Datenbankfehler anzeigen
unterdrückt, kann man mit diesem Befehl eventuelle Fehlermeldungen ausgeben.
Beispiel
// Statusline ist die Zeile unterhalb der
Eingabezeile
SET ERROR NODISPLAY;
SET ERROR CONTINUE;
Select * From fibuvorgstamm where FIID=10002;
IF(DBERR!=0)
{
SHOWERR STATUSLINE;
}
EXIT;

---

## SHOW PROCEDURE Statement

SHOW
PROCEDURE Statement
Syntax
SHOW PROC [[Creator.]procedurename];
Purpose
Anzeige aller Prozeduren unter admin oder einer
speziellen Prozedur.
Anwendung
Befehlszeile
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW TABLE
,
SHOW VIEW
,
SHOW TRIGGER
Beschreibung
SHOW PROCEDURE zeigt alle Prozeduren in der Datenbank
an. Will man nur die Prozeduren sehen, die unter einem bestimmten Benutzer
angelegt wurden, so muss man den Creator gefolgt von .* angeben.
SHOW PROC admin.*
Wird ein spezielle Prozedur angegeben, so wird die
Definition in eine Datei ausgegeben ( "SHOWPROC.TMP"), die gleich zur
Bearbeitung geöffnet wird. Hierbei ist es möglich, den Creator mit anzugeben, um
auch die Systemprozeduren anzeigen zu können, die ja bekannterweise nicht unter
Admin angelegt werden.
Beispiel
SHOW PROC dbo.sa_conn_info

---

## SET OUTPUT Statement

SET OUTPUT
Statement
Syntax
SET OUTPUT [TRIMED] [Filename]
Purpose
Öffnet / schließt eine Ausgabedatei im Modus
„Überschreiben“
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET
APPEND
,
SET OUTFILE
,
SET TITLE
Beschreibung
Ist ein Dateiname angegeben wird diese Datei geöffnet
und die Daten bzw. die Ausgaben werden zusätzlich in diese Datei geschrieben.
Die Datei wird überschrieben! Der unterschied zu SET APPEND und SET OUTFILE ist
die Genauigkeit und Menge der Ausgabe. SET OUTPUT gibt in die Datei nicht nur
die Daten aus, sonder zusätzlich die Überschriften und die abgegebenen
Statements. Es wird auch nur das ausgegeben, was angezeigt wurde. Daher ist es
nicht zu verwenden. Wird kein Dateiname angegeben, wird die offene Ausgabedatei
geschlossen. Ist keine Datei offen wird dieser Befehl ignoriert.
Der
optionale Parameter TRIMED sorgt dafür, dass in der Ausgabedatei Leerzeichen am
Ende einer Zeile wegoptimiert werden.
Beispiel
SET OUTPUT c:\ZINS.SQL;
Select * from fibuvorgstamm;
SET OUTPUT;

---

## Setup der Testumgebung

Setup der Testumgebung
Nach Feritgstellung des Installationsverzeichnisses
wird eine Testinstallation gestartet. Bei dieser Installation werden auf zwei
Rechnern mehrere datenbanken verschiedenster Größe mit einem Update versehen.
Die Basisdatenbank wird ebenfalls mit in die Installation einbezogen, um auch
auf einer leeren Datenbank test durchzuführen. -* 29.06.2001 ah Autoupdateflag
setzen 12.01.2003 BT Del Killjob aufgrund der ICA Sessions eliminiert.
---------------------------------------------------------------------
Basissetzungen
--------------------------------------------------------------------- O ON
exist %vm_system%\a1version\batch\VersionSetup.bat call
%vm_system%\a1version\batch\VersionSetup.bat "%vm_patch%" == "JA" echo Los
>%vm_system%\log\TM_TestSetup\go. m_system%\bin\setini.exe AeinsSetup
autosetup true %vm_setup%\user\aeinssetup.ini m_system%\bin\setini.exe
AeinsSetup Version 1 %vm_setup%\user\aeinssetup.ini /d %vm_setup%\bin
--------------------------------------------------------------------- Den
Server, und damit die DB's freigeben
--------------------------------------------------------------------- not exist
%vm_setup%\bin\dbstop.exe goto nostop m_setup%\bin\dbstop -c
"uid=dba;pwd=sql;eng=husum;links=tcpip" -y t stop ASANYe_Aeins t stop
ASANYs_Aeins6 t stop ASANYs_Aeins7 m_setup%\bin\sleep 2 ostop m hängt hier noch
eine alte Installation??? m_system%\bin\kill.exe %engine%
--------------------------------------------------------------------- Die Basis
Datenbank wird zur Kairo Datenbank
--------------------------------------------------------------------- /d
%vm_setup%\daten l kairo.* /f /q exist basis.log del basis.log /f /q py
%vm_system%\daten\basis\basis.db kairo.db /d %vm_setup%\bin not exist
%vm_setup%\bin\dblog.exe goto nolog m_setup%\bin\dblog -t kairo.log
..\daten\kairo.db m_setup%\bin\%engine% -f ..\daten\kairo.db olog
--------------------------------------------------------------------- Aufräumen
----
[...]


---

## SHOW Statement

SHOW Statement
Syntax
SHOW Feldname Text;
Purpose
Anzeige eines Textes in einem Maskenfeld;
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW TABLE
,
SHOW VIEW
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
Wenn es sich weder um SHOW BUFFER, SHOW CURSOR oder
SHOW TABLE handelt, wird versucht das zweite Argument als Feldnamen zu
interpretieren. Der Text der daraus folg wird in dieses Feld geschrieben.
Dadurch kann man z.B. Fortschrittsanzeigen innerhalb eines Skriptes
bewerkstelligen.
Beispiel
// Statusline ist die Zeile unterhalb der
Eingabezeile
SHOW STATUSLINE Ende des Skripts;

---

## SHOW TRIGGER Statement

SHOW TRIGGER
Statement
Syntax
SHOW TRIGGER | ON RELATION |
| TRIGGERNAME |
Purpose
Anzeige eines Triggers, aller Trigger oder aller
Trigger zu einer Relation
Anwendung
Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW TABLE
,
SHOW VIEW
,
SHOW PROC
Beschreibung
SHOW TRIGGER hat drei Ausprägungen. Die erste wäre
SHOW TRIGGER ohne irgendwelche sonstigen Parameter. Dadurch werden alle Trigger
mit dem zugehörigen Creator angezeigt.
Gibt man den Namen des Triggers an, wird die
Definition dieses Triggers in eine Datei ( "SHOWTRIG.TMP" ) geschrieben.
Verwendet man das Schlüsselwort ON mit einem
Relationsname, werden nur die Trigger zu dieser Relation angezeigt.
Beispiel
SHOW TRIGGER ON FiBuVorgPosition
// ERGEBNIS
Name

Relation
Event
FiBuVorgPosition_aftdel
fibuvorgposition       DELETE
fibuvorgposition_aftins
fibuvorgposition       INSERT
FiBuVorgPosition_aftupd_akz
fibuvorgposition       UPDATE
FiBuVorgPosition_aftupd_Konto
fibuvorgposition       UPDATE
FiBuVorgPosition_aftupd_opk
fibuvorgposition       UPDATE
FiBuVorgPosition_aftupd_VAL
fibuvorgposition       UPDATE

---

## SHOW TABLE Statement

SHOW TABLE
Statement
Syntax
SHOW TABEL [ALL] [[creator].table-name];
Purpose
Anzeige der Felder einer Relation
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW VIEW
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
SHOW TABLE oder kurz SHOW TAB zeigt die Felder der
angegeben Tabelle an, sowie die Felddefinitionen. Existiert die Relation nicht
bzw. ist sie unter einem anderen Benutzer angelegt, wird nichts ausgegeben. Es
ist möglich den Creator mit Punkt vom Tabellennamen getrennt mit anzugeben Gibt
man keinen Tabellennamen an, so werden alle Relationen die unter Admin angelegt
wurden angezeigt. Will man alle Relationen - also auch die Systemtabellen -
sehen verwendet man das Schlüsselwort ALL (SHOW TAB ALL).
Felder einer
Relation kann man sich auch über CTRL F1 ansehen!
Beispiel
SHOW TABLE FiBuVorgPosition

---

## SHOW VIEW Statement

SHOW VIEW
Statement
Syntax
SHOW VIEW [[Creator.]Viewname];
SHOW VIEWS ON
Tablename;
Purpose
Anzeige aller Views unter admin, eines speziellen
Views oder aller Views auf eine bestimmte Tabelle.
Anwendung
Befehlszeile
Siehe auch
SHOW BUFFER
,
SHOW CURSOR
,
SHOW TABLE
,
SHOW TRIGGER
,
SHOW PROC
Beschreibung
SHOW VIEW zeigt alle Views in der Datenbank an. Will
man nur die Views sehen, die unter einem bestimmten Bediener angelegt wurden, so
muss man den Creator gefolgt von .* mit angeben. Z.B.:
SHOW
VIEW ADMIN.*
Wird ein spezielles View angegeben, so wird die
Definition in eine Datei ausgegeben ( "SHOWVIEW.TMP"), die gleich zur
Bearbeitung geöffnet wird. Hierbei ist es möglich, den Creator mit anzugeben, um
auch die Crystalviews anzeigen zu können, die ja bekannterweise nicht unter
Admin angelegt werden. Will man alle VIEWS -also auch die Systemviews oder
Crystalviews - verwendet man das Schlüsselwort ALL (SHOW VIEW ALL).  Um
herauszubekommen, welche Views es zu einer bestimmten Tabelle gibt, so verwendet
man das Statement SHOW VIEW ON .... Es werden dann die Views mit dem Creator
angezeigt.
Beispiel
SHOW VIEW PS.AMIC_CRW_VERKAUSAUSWERTUNG_VR
SHOW
VIEWS ON Fibuvorgposition

---

## SKRIPT FALSCH PARAMETRISIERT!

SKRIPT FALSCH PARAMETRISIERT!
Beim Einlesen der Scriptparameter wurden Fehler
festgestellt, die dazu führen würden, dass die ASCII-Daten nicht korrekt gelesen
werden können. Nähere Informationen liefert das Fehlerprotokoll (Direktsprung:
[FEHLP]).
Mögliche Fehler sind:
Einer der Parameter MEN_SA1 .. MEN_SA4 enthält in
Wert1 oder Wert2 eine 0. Das könnte dazu führen, dass eine Mengenangabe nicht
gelesen wird. In allen benutzten Satzarten müssen Wert1 und Wert2 ungleich 0
sein, außerdem müssen die betreffenden Parameter aktiv geschaltet sein.
Die Parameter ART_AUS_SORTx und SORT_AUS_ARTx
derselben Satzart x stehen gleichzeitig auf 1. Dies führt zu dem unauflösbaren
Widerspruch, dass nämlich die Artikelnummer aus der Sortennummern und die
Sortennummer aus der Artikelnummer jeweils über eine Umsetztabelle ermittelt
werden sollen. Selbstverständlich darf nur eine Konvertierung je Satzart
erfolgen, so dass mindestens einer der Parameter auf 0 gesetzt werden muss.
Für eine Satzart x wurde folgende Konstellation
erkannt: Die Artikelnummer wird nicht gelesen, (ART_AUS_SORTx<>1)
gleichzeitig soll die Artikelnummer nicht aus der Sortennummer ermittelt werden
(im Parameter ART_SAx ist Wert1 oder Wert2 =0, oder der Parameter ist inaktiv
geschaltet). Dies ist nicht zulässig, da die Artikelnummer zwingend benötigt
wird – entweder eingelesen oder aus der Sortennummer konvertiert.

---

## SPA

SPA
Steuerparameter legen ein Verhalten fest, dass für
alle Vorgänge gilt. Zuweilen ergab sich im Nachhinein die Notwendigkeit, das
Verhalten bei ausgewählten Vorgangsklassen abweichend von der Einstellung im
Steuerparameter festzulegen.
Mit diesen Einstellungen können für die
Vorgangsklasse/Unterklasse einige der per Steuerparameter (SPA) eingestellten
Werte überlagert werden.
Die Voreinstellung ist stets „Wie SPA“.
Feld
SPA
Beschreibung
Aut.
      Formatierung für Zusatztext1
339
Aut.
      Formatierung für Zusatztext2
340
Lagernummer auf der
      Bearbeitungsmaske
163
Fiktivmenge direkt in
      Warenposition
335
Sperre Kontraktanschrift in
      Versandadr.
154
Variante Preis-Auswahl
      (F3)
180
Beim
      Betreten des Preises automatisch F3
213
Negative Einzelpreise
      zulässig
275
Negative Warenmengen
      zulässig
71
Negative Werte durch Rabatte
      zulässig
123
Menge der Folgeartikel
      korrigierbar
418
Warnung bei
      Bestandsüberschreitung
317
Warnung bei Änderung eines Vorgangs
      mit openTRANS
850
Die
      Funktion der Sperre von openTRANS-Belegen kann abweichend vom
      Steuerparameter hier eingestellt werden
Storno-Belegnummern wieder
      reaktivieren
490
Das
      Verhalten für die Stornobelegnummern kann abweichend vom Steuerparameter
      hier eingestellt werden.
Ein
      Auftrag je Warenposition
251
Ist
      nur sichtbar für die Vorgangsklasse 400 – Auftrag. Ermöglicht das
      Überschreiben des SPA-Werts für die gewählte Unterklasse.
Rabatte auch bei manuellem
      Preis
347
Druck Quellinformation
      einstufig
350

---

## Speichern der Daten

Speichern der Daten
Man kann sich für die Masken AEZADDON / AEZADDOND /
AEZADDONTnnn einen Speicherknopf einrichten, der die Speicherfunktion übernimmt.
Dort muss man dann als Aktion „Controlstring“ eintragen und dieser muss dann
„^smx_con_exec SDINTERFACE 1 12“ lauten.

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

## SQL Befehl an Datenbank absenden

SQL Befehl an Datenbank absenden
Die über den Standardhandle geöffnete Datenbank wird
mit diesem Aufruf angesprochen und es wird ein DynBranchen-ERP SQL Befehl an die
Datenbank abgegeben. Es sind alle SQL Befehle erlaubt, der erste parameter
dieser Methode legt den ggf. zu nutzenden Cursor fest.
Anfruf
call dbx_select ( cursor, sqlstatement, tempanzeiger,
option )
Parameter
t:2 Cursor Name des zu nutzenden Datenbankcursors,
hier ist ein eindutiger Text anzugeben. Schon benutzte oder noch in Benutzung
befindliche Cursor werden vor dem Einsatz in einem neuen dbx_select geschlossen
Ausdruck Es wird hier das SQL Statement erwartet, es sind select, Insert, delete
aber auch create Befehle erlaubt Temp optionaler Parameter, der angibt, ob der
cursor nur in diesem Befehl gültig sein soll. opt nicht freigegebener Parameter
Returnwert
In der Globalen Variablen DBERR wird der Fehlerzustand
dieses Befehls zurückübermittelt 0=OK, 1=Fehler,  (in diesem fall ist dann
die Globale Variable LDB_SQLERROR zur weiteren Verarbeitung auszuwerten.
Umfeld
Diese Routine ist im JPL und im COM Interface nutzbar.
Beispiel
call dbx_select ( "x", "insert
into a (a) values ('x')", "TMP" )
if ( DBERR != 0 )
{
call smx_warnung ( "SID",
"Der Inserbefehl (:LASTDBX_SELECT) ist mit dem Fehler (:LAST_SQLERRORTEXT)
schiefgegangen" )
}
call dbx_freecursor ( "x" )

---

## Stammdaten Auswertungspositionen

Stammdaten Auswertungspositionen
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Auswertungspositionen
Direktsprung
[FIAWP]
Bei der Einrichtung der Auswertungspositionen sollte
man das Formular der Umsatzsteuervoranmeldung immer vor Augen haben. Wenn
der zugelassene Vordruck verwendet werden soll, müssen für alle Kennzahlen (fett
gedruckte Zahlen auf dem Formular) Auswertungspositionen eingerichtet werden -
unabhängig davon, ob in Ihrem Betrieb diese Steuervorfälle stattfinden oder
nicht -, da vor dem Ausdruck ein
Testlauf
stattfindet, der die Stammdaten
auf Vollständigkeit prüft. Dieser Test kann auch jederzeit über den
Fibureorganisator
(Direktsprung
[FIREO]
) mit "Test Stammdaten" aufgerufen werden.
Die Sortierung gibt an, in welcher Reihenfolge die
Daten bei der Auswertung auf dem Bildschirm dargestellt werden. Wenn man sich
bei dem Feld Sortierung an die Positionsnummer links auf dem
Umsatzsteuervoranmeldungs-Formular hält, ist es leicht, die Reihenfolge so wie
sie auf dem Formular vorgegeben ist, einzurichten.
Der Text (Bezeichnung) ist für den Vordruck nicht von
Belang, jedoch erleichtert eine korrekte Bezeichnung die Übersicht über die
Einrichtung. In dem Menü "Umsatzsteuerwerte" (Direktsprung UVA) werden diese
Texte bei der Auswertung nach Auswertungspositionen mit angezeigt.
Die Oberposition dient zur Summierung der einzelnen
Zeilen für die Summenfelder in den Zeilen 53,62,65 und 67 (bezogen auf das
Umsatzsteuer-voranmeldungs- Formular 2007). Soll der zugelassene Vordruck
verwendet werden, braucht hier nichts eingetragen zu werden, da die Summen über
die Kennziffern automatisch gebildet werden. Ansonsten müssen dort für alle
Zeilen mit einem Feld für die Steuer eine existierende Auswertungsposition
eingetragen werden. Die Auswertungspositionen für die Zeilen 53 muss dann auch
wieder eine Oberposition eingetragen haben, die die Summe in der Zeile 62
darstellt. Die Zeile 67 (Kennzahl 83) weist somit das Ergebnis der
Umsatzsteuervoranmeldung au
[...]


---

## Stammdaten im Mandantenstamm

Stammdaten im Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
Register Finanzbuchhaltung
Direktsprung
[MND]
.
Im Mandantenstamm wird die unter der Funktion „
Ansprechpartner ZMDO
“ hinterlegte
Anschrift verwendet. Dabei werden folgende Felder verwendet:
•
Name bis zu einer Länge von 30 Zeichen.
•
Zusatz 1 (optional) mit einer Länge bis zu 40 Zeichen
•
Straße bis zu einer Länge von 30 Zeichen und Hausnummer bis zu 10
Zeichen
•
Postleitzahl bis zu 12 Zeichen. Bei Inländischen Adressen ist die Angabe
Pflicht und wird vor dem Versand der ZMDO geprüft, ob die Postleitzahl 5 Ziffern
enthält und diese im Bereich von 01001 bis 99999 liegt. Bei ausländischen
Adressen ist die Angabe optional.
•
Ort
•
Staat (
ISO-3166-Alpha-2-Code) wie er im
Staatstamm hinterlegt ist.
•
Telefon (optional) mit maximal 20 Zeichen.
Zulässige Zeichen sind die Ziffern 0-9, /, \, (, ), +, - und das
Leerzeichen.
Sind Name, Straße, PLZ, Ort oder Staat nicht korrekt
angegeben, dann kann die ZMDO nicht versendet werden.

---

## Stammdaten Jahreswechsel

Stammdaten Jahreswechsel
Steuerparameter
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[SPA]
.
Für die
Währungsbehandlung
in der
Finanzbuchhaltung existieren einige Steuerparameter. Der Steuerparameter
„Anzeige des Fremdwährungssaldos in der Fibu“ bewirkt unter anderem, dass beim
Jahreswechsel auch für Fremdwährung der Jahreswechsel durchgeführt wird.
Für den Jahreswechsel werden immer zwei Buchungen
erstellt, eine in der Abschlussperiode und eine in der Eröffnungsperiode. Damit
nicht aus Versehen nur eine der Buchungen gelöscht wird, wurde ein Verfahren
eingeführt, in dem Die Belege immer paarig betrachtet werden. Das bedeutet, wird
ein Beleg gelöscht, so wird auch der andere gelöscht, wird ein Beleg gebucht, so
wird auch der andere Beleg gebucht.
Mit dem Steuerparameter 1143
„Jahreswechsel: Abschluss und Eröffnung immer gemeinsam löschen/buchen.“ kann
dieses Verhalten wieder abgeschaltet werden.
Beim Jahreswechsel werden standardmäßig
Umbuchungen
durchgeführt, wenn im Kundenstamm Forderungsgruppen geändert wurden. Mit dem
Steuerparameter 968 „Forderungskonten umbuchen“ kann man diese Buchungen
deaktivieren, indem man ihn auf
Nein
stellt.
Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
Register Finanzbuchhaltung
Direktsprung
[MND]
.
Im Mandantenstamm können die Konten, die für den
Jahreswechsel verwendet werden sollen, hinterlegt werden. Sie werden dann als
Vorbelegung verwendet. Ist hier kein Konto eingetragen, so muss man beim
Jahreswechsel die Konten angeben.
Sachkontenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Direktsprung
[SKS]
Die Konten, die als Eröffnungs- bzw. als
Abschlussbilanzkonto verwendet werden, müssen im
Sachkontenstamm
als Vortragskonten
gekennzeichnet werden. Beim Jahreswechsel bzw. im Mandantenstamm werden nur die
Konten zugelassen, bei denen unter
Vortragskonto
„JA“ eingetragen
ist.
Zu den Abschlussarbeiten gehört unter anderem der
Abschluss der Unterkonten über d
[...]


---

## Stapelverarbeitung einrichten

Stapelverarbeitung einrichten
Hauptmenü
Administration
Firmenkonstanten
Bediener
oder Direktsprung
[BD]
Im Bedienerstamm kann pro Bediener hinterlegt werden,
ob und wie mit der Stapelfunktion gearbeitet werden darf. Die Einstellung wird
im Feld „Ausw. Stapel“ eingetragen. Es stehen drei Möglichkeiten zu Verfügung,
die mit F3 ausgewählt werden können:
1.
Globaler Stapel:
Der Stapel wird gespeichert
und bleibt so lange erhalten, bis er manuell gelöscht wird oder der Stapel älter
ist als der in den Einrichterparametern hinterlegte Zeitraum. Es stehen alle im
Folgenden beschriebenen Funktionen zur Verfügung.
2.
Temporärer Stapel:
Der Stapel bleibt nur so
lange bestehen, solange man in die Anwendung nicht verlässt. Es stehen nur die
Funktionen „Zu Stapel hinzufügen“, „aus Stapel entfernen“ und „Umschalten
Stapelverarbeitung“ zur Verfügung. Temporäre Stapel sind immer privat und man
kann auch nur die eigenen Stapel bearbeiten und nicht auf globale Stapel
zugreifen.
3.
Keine Stapelfunktionalität:
Es kann kein Stapel gebildet
werden und der entsprechende Bediener sieht das Register „Stapelverarbeitung“
nicht.
Es kann vorkommen, dass für bestimmte Anwendungen bzw.
Varianten keine Stapelverarbeitung angeboten wird. Dies kann neben der Lizenz
und Benutzereinstellung noch folgende Ursachen haben:
•
Die Anwendung/Variante enthält keine IDENT-Felder
•
In der Anwendung /Variante ist das Markieren von Zeilen nicht erlaubt
•
In der Anwendung /Variante wurde mit der Option „NOSTAPEL“ die
Stapelverarbeitung deaktiviert.
OPTIONS
NOSTAPEL

---

## Steuerparameter

Steuerparameter

---

## Steuerparameter der Wechselbuchhaltung

Steuerparameter der Wechselbuchhaltung
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[SPA]
.
In den Steuerparametern
muss die Wechselbuchhaltung angeschaltet werden
.

---

## Steuerparameter für SEPA

Steuerparameter für SEPA
Hauptmenü
Administration
Steuerung
Steuerparameter
zeigen
Direktsprung
[SPA]
.
In der Steupagruppe „Optionen Finanzwesen“ existiert
der Steuerparameter „DTA-Ausgabeformat“. Dieser muss auf
„SEPA“
eingestellt werden. Dieser Parameter sorgt unter anderem dafür, dass der
Reorganisator zusätzliche Tests ausführt.
•
Test der verwendeten Banken im Bankenstamm, ob der BIC eingetragen
ist.
•
Test der Kundenbanken, ob die IBAN eingetragen ist. Für Kundenbanken,
deren Bank sich in Deutschland befindet und für die eine gültige Kontonummer
bzw. eine gültige Bankleitzahl hinterlegt ist, wurde diese Nummer beim Update
der Datenbank automatisch anhand dieser Daten generiert. Gleichzeitig wird
getestet, ob die eingetragenen IBAN gültig ist. Dazu wird ein
Prüfziffernverfahren angewandt, das auch bei der Stammdatenerfassung der IBAN
eingesetzt wird.
Der Test der IBAN kann
entweder für jede
Bank
oder global per
Steuerparameter
abgeschaltet
werden.
•
Test der Hausbanken, ob die IBAN eingetragen worden ist. Die IBAN wird -
wie auch bei den Kundenbanken – beim Update einmal für deutsche Banken mit
eingetragener Kontonummer generiert. Bei eingetragenen IBANs wird  auf
Korrektheit nach dem Prüfziffernverfahren geprüft.
Der Test der IBAN kann
entweder für jede
Bank
oder global per
Steuerparameter
abgeschaltet
werden.
Es sollte also vor der ersten Überweisung mit dem
SEPA-Verfahren einmal der Test-Stammdaten durchgeführt werden.

---

## Steuerungsparameter Währung

Steuerungsparameter Währung
Hauptmenü
Administration
Steuerung
Steuerparameter
zeigen
Direktsprung
[SPA]
Parameter
Nummer
Beschreibung
Währungsumrechnung aktiv
35
Dieser SPA muss auf "aktiv"
      (
Ja
) stehen, damit in der Finanzbuchhaltung die Währungsumrechnung
      und OP-Führung in  Fremdwährung aktiv ist.
Anzeige Fremdwährung in
      Auswahllisten
673
Wird
      in der Finanzbuchhaltung Fremdwährung geführt, so werden im Beleg diverse
      Informationen (z.B. Währungskurs, Betrag in Fremdwährung, Steuer in
      Fremdwährung usw.) geführt. Diese werden in den Auswahllisten dargestellt,
      wenn hier
Ja
eingetragen wurde. In der Konteninfo steht dann auch
      eine weitere Variante „Konteninfo mit Währungsauflösung“ zu
      Verfügung.
Dieser Steuerparameter steuert
      gleichzeitig, ob beim Jahreswechsel zusätzlich ein Übertrag für
      Fremdwährung erstellt wird. Dieser Übertrag wird u.a. für die Variante
      „Konteninfo mit Währungsauflösung“ benötigt. Um nach der Umstellung dieses
      Steuerparameters die korrekten Daten angezeigt zu bekommen, muss einmalig
      eine „Reorganisation Währung“ ausgeführt werden.
Anzeige des Fremdwährungssaldo in
      der Fibu
794
Grundsätzlich wird der Kontosaldo
      nur in der Buchwährung angezeigt. Will man zusätzlich den Saldo in
      Fremdwährung sehen, so muss dieser Steuerungsparameter auf
Ja
stehe. Es werden dann bei allen Personenkonten mit Währungstyp ungleich
      Euro und allen Bilanzkonten mit „Vorbelegung Buchwährung“ gleich
Nein
und Währung ungleich Buchwährung der Saldo in der dort
      eingetragenen Währung angezeigt.
Gleichzeitig bewirkt dieser
      Parameter, dass beim Jahreswechsel auch der Jahreswechsel für Fremdwährung
      durchgeführt wird. Um nach der Umstellung dieses Steuerparameters die
      korrekten Daten angezeigt zu bekommen, muss einmalig eine „Reorganisation
      Währung“ ausgeführt werden.
Aktuell Buchwährung
353
Hier
      wird festgelegt, wel
[...]


---

## Tabelle benutzt in

Tabelle benutzt in
Hier werden die Formulare angezeigt, die die aktuell
in der Maske geöffnete Fonttabelle verwenden. Das ist hilfreich, falls man
vorhat eine Fonttabelle für ein bestimmtes Formular zu ändern. So weiß man
gleich welche Formulare von der Änderung noch betroffen sind.

---

## Tabelle zur Version: 9.0.2502.5

Tabelle zur Version: 9.0.2502.5
ID
Releasenote - Titel
Geprüft
36624
Abkündigung: Callback Dialog
36695
AIS Multilinefeler
37364
UserJpl OnsSaveValid
36958
Belegfluss-Workflow
37651
Belegfluss: Fibu-Belege
36675
Formulararchiv eRechnung Datenanzeige
36702
Aktualisierung Dokument-Engine
36956
Formularchivbelegdatum der eRechnung entspricht jetzt
      dem Belegdatum des Ursprungsbelegs.
37315
Belegversand zieht Daten aus eRechnungseinrichtung,
      wenn Prozedur AMIC_Belegversand_Ware_Spaeter  genutzt wird
37470
Importprobleme bei fehlendem BG-14 - Invoicing
      Period
37471
Auswahllisten der Anwendung eRechnung [XRE]
37640
eRechnung ID nur Ansicht
37671
eRechnung: Skonto
37343
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
37879
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
36710
OP-Verwaltung
37158
eClearing CAMT53 Zusatzinformationen
37421
SEPA Version 3.9
37533
Finanzbuchhaltung
37599
Report Verteilkostenträgerauswertung
37672
Ergänzung zur Paginiernummer
37833
SEPA - Empfänger und Zeichensatz
37862
Sepa erweiterter Zeichensatz mit Umlauten
36104
Testmandant
37461
DSFinV-K Export
37818
EC-Karten-Ansteuerung
36728
Rohware-Lieferscheinstornobeleg ohne Belegkopie.
      Lieferschein fälschlicherweise in Massebilanz
36915
Pascal-Makro-Funktionen JVarsGet und JVarsGet,
      Längenbeschränkung aufgehoben
35856
Rohwaresammeldruck-Mailversand
37195
Mailstatus in Rohware-Auswahllisten
37316
Feldreihenfolge Vermehrungsvertrag
37673
Vermehrungsvertrag
36639
Scanner Konfiguration
36541
Artikelstamm: Gefahrgut
36645
Individualpreispfleger [PRI] [PRIE]
36648
Funktion Belegdatum ändern zu AWL
36732
Sonderzeichen in Emailadresse
37121
Warnverhalten Permanente Inventur
37815
Stammdatenpfleger Tastenbelegung Shortcut
37342
Vertreterprovisionsgruppenpfleger modernisiert und
      Vertreterstaffelpfleger verbessert.
35616
Nachkommastellen bei der Restmengenkorrektur
37120
UFLD "Gültig bis"
37192
Steuerparameter 1046 SPA_TEILPRODUKTION
36731
Wiegen gegen einen Vorg
[...]


---

## Test aktivieren

Test aktivieren
Wenn man diesen Punkt aktiviert wird die
Formularstimmigkeit beim Druck überprüft. Dies ist dafür gut, um
Einrichtungsfehler und spezielle Endlos-Druck-Probleme zu erkennen. Dieser Test
ist optional einstellbar, da sehr viele Einrichtungen nicht den aufgestellten
Kriterien des Tests entsprechen (z.B. keine Überlappung Kopf/Fuß, Fuß ganz auf
der Seite, mindestens eine Zeile zwischen Kopf und Fuß), letztlich aber doch aus
verschiedenen Gründen „wie gewünscht“ funktionieren.
Dies verhindert, dass
der Anwender in diesen Fällen trotzdem per Fehlermeldung beim Druck auf diesen
Missstand hingewiesen wird.

---

## To Do

To Do
Der Reiter „ToDo“ ist Benutzer bezogen. Hier können
Planungsaufgaben erstellt werden. Diese sind dann auch in der Referenz-ERP-Software
einzusehen.

---

## Umwandeln und Kopieren

Umwandeln und Kopieren
Die Bereiche Umwandlung und Kopieren sind sowohl in
ihrer äußeren Gestaltung als auch im Funktionsumfang komplett überarbeitet
worden. Dem Anwender wird mehr Einfluss auf die verschiedenen Sonderfälle der
Umwandlung geboten. Obwohl es mehr Einstellparameter als früher gibt, kommt man
mit wenigen Tastenbefehlen zum Ziel.

---

## Update

Update
-11000
Fehler beim Login
-11001
Fehler beim Insert der Ergebnisse
-11002
Fehler beim Parsen Ergebnisse
-11003
Fehler beim Abruf eines Pakets
-11004
Fehler beim Erstellen der Login-Informationen
-11006
Fehler beim Abruf der Information aus dem
Webservice
-11007
Fehler beim Select der Mandantenversion

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
      Protokolleintrag.
Masken-Funktionen
Dialog „Fehlerprotokoll“
      Registerkarte „Fehlerprotokoll“
Löschen
Löscht den
      Protokolleintrag.

---

## Prozeduren oder Views für Kacheln einrichten

Prozeduren oder Views für Kacheln
einrichten
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Alle Darstellungsarten haben denselben Grundaufbau.
Die Überschrift, den Mittelteil und die Fußzeile sowie einen Tooltip. Alle
Bereiche erhalten ihre Daten über eine View.
Hinweis:
Trägt man eine nicht
existierende View ein, so wird man gefragt, ob die View neu angelegt werden
soll. Es wird dann je nach Darstellungsart ein Grundgerüst mit den möglichen
Feldern als Vorlage erstellt.
Jede Kachel hat den gleichen Grundaufbau. Überschrift
und Fußzeile sowie Hintergrundfarbe und Ausrichtung werden von der View als
Header, Headeralign
und als
Footer, Footeralign
bzw.
Backcolor
und
Backcolor2
sowie
Borderstyle
und
Bordercolor
geliefert. Die Werte, die der Mittelteil benötigt, hängen vom
verwendeten Control ab.

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

## Vorgehensweise

Vorgehensweise
Vorgehen, wenn man bei verschiedenen Kassen auf
unterschiedliche Kasseneinstellungen zurückgreifen will:
Vorgehen, wenn man bei verschiedenen Kassen auf
unterschiedliche Kasseneinstellungen zurückgreifen will:
1.
Es ist für Systemadministratoren möglich, in den Kasseneinstellungen über F8
Neuer Vorlagesatz einen neuen Satz von Kasseneinstellungen zu erzeugen, der eine
fortlaufende Vorlagenummer bekommt. Diesen kann man dann z.B. bei entsprechender
Profilierung bearbeiten. Dabei werden die Einstellungen der gewählten Vorlage
übernommen. In dieser Anwendung besteht auch die Möglichkeit über F7 Lösche
Vorlagesatz einen kompletten Satz von Kasseneinstellungen zu löschen, allerdings
nur dann, wenn auf diesen Satz in der Kassenverwaltung nicht verwiesen wird. Die
Auswahl, welcher Satz gelöscht werden soll, erfolgt über eine vorgeschaltete
Item-Box.
2.
Dieser neu erzeugte hat eine fortlaufende Nummer und man kann diesen Satz in den
Kasseneinstellungen bearbeiten, indem man in den Profilen die Vorlage auf die
Nummer der neuen Vorlage einstellt.
3.
In der Kassenverwaltung sucht man sich jetzt die Kasse aus, die nach den neuen
Einstellungen arbeiten soll. Dort gibt es ein zusätzliches Feld namens Vorlage.
In dieses trägt man die Vorlagenummer gemäß Kasseneinstellungen ein. Auf diesem
Feld ist die F3-Auswahl implementiert über alle bisher erzeugten Sätze von
Kasseneinstellungen, von denen genau eine zuzuordnen ist. Standardmäßig ist 0
eingestellt.
Die oben beschriebene Funktionalität kann man für
unterschiedliche Zwecke nutzen
(die aufgeführten Beispiele erheben keinen Anspruch
auf Vollständigkeit):
a)
Dadurch, dass pro Kasse unterschiedliche Standardkunden hinterlegt sind ist es
möglich, über die Vorgangsdruckklassen unterschiedliche Drucker anzusteuern
(OptiGruppe Kunden).
b)
Man kann je nach Kasse/Region unterschiedliche Displaytexte hinterlegen
(OptiGruppe Displaytext).
c)
Es ist möglich, verschiedenen Kassen eine unte
[...]


---

## Vorgreservier. HINZUFUEGEN

Vorgreservier. HINZUFUEGEN
Unter Berücksichtung des Steuerparameters ‚Eindeutigkeit
Vorgangsnummer per Klasse’ wird versucht, einen korrespondierenden Eintrag in
der Vorgreservierung zu erzeugen. Steht der SPA auf ‚JAHR’ so wird die
Jahrnummer aus dem Vorgangstamm übernommen, bei ‚GESAMT’ steht hier immer eine
‚0’ (jede Nummer kann also pro Vorgangsklasse nur einmal benutzt werden!).
Tip:
Hier kann es das Problem geben, dass (aus diversen
Gründen oder Fehlersituationen) zwei Belege mit derselben Belegnummer in einem
Jahr erzeugt worden sind, es aber bei Einstellung ‚JAHR’ eigentlich keine zwei
Nummern geben darf. Es wird dann also nicht möglich sein, für beide Belege eine
Vorgreservierung zu erzeugen. Da im eindeutigen Schlüssel der Vorgreservierung
die von uns bisher nicht benutzte ‚Unternummer’ vorhanden ist, kann durch
Vergabe einer anderen Unternummer dennoch eine Vorgreservierung erzeugt werden
(siehe auch weiter unter: ‚andere UNTERNUMMER’.)

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
      angeschlossen“ auf
Ja
, dann erscheint diese Spalte. Dort können die
      eingerichteten
Kostenträger
mit
F3
ausgewählt
      werden.
Kostenobjekt
Mit
      einer gültigen Kostenobjekt-Lizenz können hier die
Kostenobjekte
erfasst werden.
StSchl
Auswahl mit
F3
aus vorher eingerichteten
      Steuerschlüsseln um evtl. den Betrag um die gesetzliche Umsatzsteuer zu
      erhöhen

---

## Weitere Einstellungen

Weitere Einstellungen
Man kann die Farbgestaltung für Referenz-ERP per
Aufrufparameter ein- bzw. ausschalten:
FARBE = FALSE
Dies bewirkt, dass die Farbauswahl nicht mehr zu
Verfügung steht. Sämtliche Farbeinstellungen werden ignoriert. Der Reiter zur
Farbeinstellung erscheint nicht im Gestaltungsdialog.
FARBBALKEN =TRUE
Bisher werden markierte Zeilen immer mit einem „#“
versehen, um sie als ausgewählt zu kennzeichnen. Setzt man den Parameter auf
TRUE, so werden die Zeilen zusätzlich in blauer Schrift dargestellt.

---

## Währungsbehandlung in der Finanzbuchhaltung

Währungsbehandlung in der
Finanzbuchhaltung
Wie in allen Programmteilen von Referenz-ERP ist auch die in
die Referenz-ERP Finanzbuchhaltung integrierte Fremdwährungsbuchhaltung an vielen
Stellen parametrisierbar. Neben den hier beschriebenen Steuerungs- und
Einrichterparametern werden auch die Stammdaten für
Währungen
und
Währungskurse
gemeinsam mit der
Warenwirtschaft zentral gepflegt.

---

## WIN2DOS

WIN2DOS
Syntax
WIN2DOS table-name [Dateiname der Umsetztabelle];
Purpose
Wandelt die Umlaute der Windows Codepage in Umlaute
der DOS Codepage um.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
DOS2WIN
Beschreibung
Sollen Daten aus Aeins exportiert und in eine DOS
basierende Fremdsoftware eingebaut werden, tritt das Problem auf, dass die
Deutschen Umlaute hier unterschiedlich dargestellt werden. Dieser Befehl
schnappt sich eine Relation(table-name) und nimmt sich alle Textfelder vor um
dort gegebenenfalls die Umlaute umzuwandeln. Es erfolgt nur ein Update, wenn
auch Umlaute in den Datensätzen vorhanden sind. Die Umsetzungstabelle (Siehe
DOS2WIN) braucht nicht extra angepasst werden(darf nicht). Nach wie vor muss das
DOS Zeichen an stelle 1 stehen und das Windows Zeichen an stelle 2.
Beispiel
WIN2DOS ANSCHRIFTSTAMM c:\AEINS\BIN\UMLAUT.TXT

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

## Zahlungsverkehr

Zahlungsverkehr
Der Zahlungsverkehr im Ein- und Ausgang basiert auf
verschiedenen Parametern, die unter "Stammdaten" im Abschnitt "Zahlungsverkehr"
zu finden sind. Der Zahlungsverkehr selber ist eine Auswertung dieser Parameter
(Zahlungsabstand, Anschreiben, etc.) sowie der in den offenen Posten
hinterlegten Informationen (Fälligkeit, Betrag, Auslandskennzeichen etc.).
Zum Erstellen von Zahlungen über den automatischen
Zahlungsverkehr sind folgende Schritte notwendig:
•
Zahlungsvorschläge erstellen über Automatik, OP-Verwaltung oder
Zahlmappe
•
Zahlungsvorschläge bearbeiten
•
Zahlungen bearbeiten
Oder
•
Zahlungen erstellen
•
Zahlungen bearbeiten

---

## Zahlungsverkehrsstammdaten im Mandantenstamm

Zahlungsverkehrsstammdaten im Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
Registerkarte Finanzbuchhaltung
Direktsprung
[MND]
Im
Mandantenstamm
muss das Bundesland
hinterlegt sein. Dies wird benötigt, wenn die Meldedaten an die Bundesbank
weitergeleitet werden.

---

## Zentraleinrichtung

Zentraleinrichtung
Der Setup Prozess prüft bei der Installation, ob eine
ODBC-Setup der Microsoft Basisroutinen notwendig ist, oder nicht. Ist so ein
Basissetup notwendig, dann wird die Microsoft ODBC Setup Routine gestartet, die
nur einmal einfach durchlaufen werden muss.

---

## Zielansprache

Zielansprache
Die gelesene Zielansprache-Kennung wird in einen
internen Wert umgesetzt. Wird keine Zielansprache erkannt, so zieht der
Standard, der im Parameter ZI_DEFAULT hinterlegt ist. Ist im Parameter
ZI_DEFAULT der Wert 99 hinterlegt, so geht das Programm davon aus, dass es sich
bei dem Datensatz um eine Testwägung handelt und geht zum Schleifenanfang und
zum nächsten Datensatz über.
Wird auch der Parameter ZI_DEFAULT nicht gefunden, so
ist FAKTURA die Standard-Zielansprache.
(Zugehörige Positionsparameter: ZI_SAx)

---

## Zielaufruf

Zielaufruf
Der gezielte Aufruf einer Ansicht kann vom Support
vorgenommen werden. Dies ist eine sehr technische Einrichtung, die hier
beschrieben werden soll:
An die JPL namens OLAP.j werden folgende Parameter
übergeben:
JVAR 1975
COMMAND
Anzeigekommando
•
Sollen die Daten
      nur angezeigt werden ohne Designer, dann wird hier „SHOW“
      angegeben
Soll
      die Auswertung automatisiert gedruckt werden wird hier „PRINT“
      angegeben
ANWENDUNG
Die
      Anwendung, als der die Daten kommen sollen
VARIANTE
Die
      Variante aus der die Daten kommen sollen
PROFIL
Das
      Profil aus dem der Filter kommen soll
TITEL
Der
      anzuzeigende Titel (Default leer)
PRINTER
Drucker, auf dem die Auswertung
      gedruckt werden soll (COMMAND==PRINT)
PRINTAREA
Hier
      gibt es drei Bereiche:
•
RAW – die
      Rohdaten der Anwendung
•
CHART – die
      grafische Auswertung des Charts
•
PIVOT – die
      Pivottabelle

---

## Zinsmerkmale im Mandantenstamm

Zinsmerkmale im Mandantenstamm
Hauptmenü
Administration
Firmenkonstanten
Mandantenstamm
Direktsprung
[MND]
Im Mandantenstamm wird die Zinsbasis hinterlegt, d.h.
man entscheidet sich firmenweit, welche Monatseinteilung man bei der
Zinsabrechnung verwenden will. In Referenz-ERP gibt es drei Möglichkeiten
•
30 Tage im Monat beim 360 Tagen im Jahr
•
Monatstage (Jan=31;Feb=28;...) bei 365 Tagen im Jahr
•
Monatstage (Jan=31;Feb=28;...) bei 360 Tagen im Jahr

---

## ZOOM

ZOOM
Syntax
ZOOMb
Purpose
Vergrößert oder verkleinert die OSQL-Fenster
Anwendung
Befehlszeile, Optionen
Berechtigung
Alle Anwender
Siehe auch
---
Bschreibung
Im Standardfall ist OSQL eine Dialogmaske mit fest
eingestellter Größe, die nur einen Teil des Bildschirms nutzt.
Mit dem Befehl ZOOM wird die größe auf den
Gesammtbildschirm ausgedehnt. Um wieder zurück auf die kleine
Bildschirmgröße
zu gelagen führt man erneut ZOOM aus. Die Einstellung,
die man über die Befehlszeile eingibt wird nicht gespeichert und
OSQL startet immer wieder als kleine Dialogmaske. Will
man OSQL immer im Vollbidlmodus starten, kann man unter Optionen
F10
die Einstellung "Vollbild" auf TRUE ändern.
Beispiel
ZOOM

---

## Zuordnung der Qualitätsbezeichnungen

Zuordnung der Qualitätsbezeichnungen
Der
Steuerparameter 932
bestimmt, woher
die Bezeichnungen der Qualitätsmerkmale stammen.
Einstellung „Bis max 20 in der Waage
ausschließlich“
Hier werden die Bezeichnungen aus den
Einrichterparametern der Waage
geholt. Dadurch sind maximal 20 Qualitätsmerkmale möglich.
Einstellung „
Über den Bereich Artbestandteil,
beliebig viele Qualitäten“
In dieser Einstellung werden die Bezeichnungen in der
Anwendung
Bestandteile
[ABST]
gepflegt. Dabei werden nur die
Datensätze beachtet, deren Qualitätsnummer größer als Null ist.
Die Reihenfolge der Felder in der Auswahlliste wird
durch die Bestandteilnummer bestimmt. Soll bei der manuellen Erfassung der
Qualitätswerte eine andere Reihenfolge verwendet werden, kann sie über das Feld
Sortierung der Bestandteile eingestellt werden. Auf der Erfassungsmaske werden
dann als erstes die Qualitätsmerkmale mit einer Sortierung ungleich Null
aufsteigend und dahinter die Qualitätsmerkmale mit Sortierung gleich Null,
aufsteigend nach Bestandteilnummer, angezeigt.
Aufgrund dieser Systematik muss man vorsichtig mit dem
Erstellen und Löschen von Qualitätsmerkmalen sein, die aufgrund ihrer
Bestandteilnummer nicht am Ende sind. Denn dadurch würden sich die Bezeichnungen
der Qualitätsmerkmale verschieben, die Werte jedoch nicht.
Die Anzahl der verfügbaren Qualitätsmerkmale steigt
mit dieser Methode auf 30. Sollten mehr als 30 Bestandteile mit Qualitätsnummern
größer Null existieren, werden nur die ersten 30 Datensätze bei der Sortierung
nach Bestandteilnummer genutzt.

---

## Zusatzfelder in Vorgang selbst einrichten mit [SLQM oder SQLK]

Zusatzfelder in Vorgang
selbst einrichten mit [SLQM oder SQLK]
Es kann trotz aller Einrichtung nicht jeder Wunsch
nach Druckbarkeit von spezifischen Informationen in Vorgängen seitens Referenz-ERP
erfüllt sein. Um die Möglichkeit zu schaffen, zusätzliche Informationen im
Belegdruck darzustellen, kann mittels privater SQL-Texte ein zusätzlicher
Dateninhalt zum Druck im Bereich Warenwirtschaft herangezogen werden. Die
Parametrisierung der SQL-Anweisungen erfolgt über die Einbindung von
Identifikatoren versehen mit dem Erkennungssymbol‘:‘. Ursprünglich wurden nur
die folgenden 4 Identifkatoren vorgesehen:
V_ID (im Bereich Quellvorgang ist dies die V_ID der
Quelle)
KUNDID
ARTIKELID
WABEWID
In einer späteren Version hat man einen erweiterten
Mechanismus zur Parametrisierung der SQL Anweisungen geschaffen. Nach dem
Erkennungssymbol ‚:‘ können jetzt alle legalen Druckpositionen mit ihren
‚ID_...‘ Namen spezifiziert werden. Eine Liste aller Druckpositionen liefert die
Anwendung ‚Druckpositionen‘ (Direktsprung: FRMP).  Eine Übersicht, in
welchem Druckbereich welche Druckposition gültig ist, bekommt man beim
Formulareinrichter per F3-Box:
Beispielsweise könnte man in einem SQLK auf einem
Warenpositionsbereich mit folgender Konstruktion die Artikelnummer an eine
Datenbankfunktion Test_ArtikelNummer übergeben:
Select
Test_Artikelnummer(‚:ID_ARTIKELNUMMER‘) as Ergebnis from dummy
Einige ID_‘s erwarten einen numerischen Parameter,
wenn es für diese ID mehrere Werte gibt (z.B. mehrere Steuersätze). Man kann
diese Parameter durch ein unmittelbar anschließendes Komma und einer Zahl
übergeben:
Select :ID_STEUERSCHLUESSEL,3 as
Schluessel from …
Ähnliches gilt für zeichenhafte Parameter, wie etwa
den Spaltennamen eines Feldes aus der Ergänzungsrelation zur Warenbewegung. Bei
zeichenhaften Parametern wird als Trennzeichen das Symbol ‚@‘ erwartet.
Select :ID_WARENBEWEGUNG_ADDON@Herkunft
as  Herkunft from …
Um private SQL-Texte anzulegen, verwendet man den
Direktsprung
[...]


---

## Zusätzliche DSGVO-Information im Anschriftenstamm

Zusätzliche DSGVO-Information im Anschriftenstamm
Auf dem Anschriftenpfleger erscheint bei allen von der
DSGVO betroffenen Anschriften ein weiterer Reiter mit der Überschrift DSGVO.
Dieser Reiter lässt sich mit dem Einrichterparameter auf der Maske Anschriften
„Soll die Registerkarte DSGVO versteckt werden?“ ausblenden. Dieser
Einrichterparameter gilt auch für die Maske STDADR.
Bedeutung
Herkunft der Adresse
Hier
      steckt das Anwenderformat „AF_DSGVOHERK“ hinter, welches vom Anwender
      individuell gepflegt werden kann. Der Wert 0 ist mit „Aus Altanlage vor
      Mai 2018“ vorbelegt.
Grund der Anlage
Hier
      steckt das Anwenderformat „AF_DSGVOHERK“ hinter, welches vom Anwender
      individuell gepflegt werden kann. Der Wert 0 ist mit „nicht
      angegeben“.
Privatadresse
Hier
      kann hinterlegt werden, ob es sich bei dieser Adresse ggf. um eine private
      Adresse handelt. Der Wert ist mit „Nein“ vorbelegt.
Newsletter
In
      dieser Tabelle wird mit Historie eingetragen, ob der Kunde einen
      Newsletter haben möchte oder nicht. Einmal gespeicherte Daten können nicht
      mehr gelöscht werden. Es muss dann eine weitere Zeile mit der Änderung
      erfasst werden.
Genehmigung erteilt/widerrufen
      von
Hier
      kann der Namen desjenigen eingetragen werden, der die Genehmig erteilt
      bzw. widerrufen hat.
Position
Welche Position bekleidet derjenige.
      Eine Auswahl ist mit F3 möglich. Das Anwenderformat „AF_ZUSTAENDI“ kann
      individuell erweitert werden.
Am
Das
      Datum der Genehmigung/ des Widerrufs wird mit dem Tagesdatum
      vorbelegt
Referenzkunde
In
      dieser Tabelle wird mit Historie eingetragen, ob der Kunde zugestimmt hat
      als Referenzkunde geführt zu werden. Einmal gespeicherte Daten können
      nicht mehr gelöscht werden. Es muss dann eine weitere Zeile mit der
      Änderung erfasst werden.
Genehmigung erteilt von
Hier
      kann der Namen desjenigen eingetragen werden, der die Ge
[...]


---

