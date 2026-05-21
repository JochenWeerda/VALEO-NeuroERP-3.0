# Warenwirtschaft & Auftragsabwicklung — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (405 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Darstellung der Stoffstrom-Mengen in der Vorgangsübersicht

Darstellung der Stoffstrom-Mengen in der Vorgangsübersicht
In der Auswahlliste der Anwendungsvariante 'Stoffstrom
Positionen' der Anwendung 'Vorgangsübersicht' [VRUE] werden die
Stoffstrom-Mengen für Gutschriften sowie Stornobelegen zu Aufträgen,
Bestellungen, Lieferscheinen und Rechnungen analog zur Darstellung der
zugehörigen Positionsmenge negativ dargestellt.
Releasenote Kategorie:
Ticket: 716861[33203]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: Vorgangsübersicht [VRUE]
Variante: Stoffstrom Positionen
Funktion/Report: Auswahlliste
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33203, 716861

---

## Bestandsbuchungen bei Quellbeleg-Freigabe in Storno-Funktionen

Bestandsbuchungen bei Quellbeleg-Freigabe in Storno-Funktionen
Bei der Quellbeleg-Freigabe der Funktion
Storno/Löschen sowie der Erstellung von Stornobelegen mit
Quellbeleg-Freigabe konnte es vorkommen, dass der Quellbeleg (z.B. Lieferschein)
in der Bestandsführung zum Beispiel im zugehörigen Kontrakt doppelt
berücksichtigt wurde. Dieses wurde bisher durch WAREO automatisch korrigiert.
Die Ursache für die doppelte Berücksichtigung wurde nun behoben.
Releasenote Kategorie:
Ticket: 723007[33805]
Version: 8.3.2305.26
Datum: 26.05.2023
Anwendung: REB,ERB,LIB,ELB
Variante: alle
Funktion/Report: Stornieren/Löschen,
Stornobeleg-Erstellung
Weitere Informationen
Tags:
Releasenote, 8.3.2305.26, 33805, 723007

---

## Betreff-Zeile bei Mailversand von Vorgängen

Betreff-Zeile bei Mailversand von Vorgängen
Im Modul Belegmailversand wird für die Setzung des
Betreffs unter anderem das Anwendungsformat 'MAILVERSAND' verwendet. Hier wurde
nun der Formattext zur Vorgangsklasse 1400 (Bestellung) von 'Ihre Bestellung' in
'Unsere Bestellung' geändert.  Es gibt über den Steuerparameter 890
'Belegversand Betreff' für den Bereich 'Standard' die Möglichkeit eine
abweichende privatisierte Prozedur anzugeben.
Releasenote Kategorie:
Ticket: 723416[33839]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Belegmailversand
Variante: alle
Funktion/Report: Druck
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33839, 723416

---

## Auftragserfassung trotz harter Liefersperre

Auftragserfassung trotz harter Liefersperre
Der Steuerparameter 'Auftrag trotz Liefersperre
schreiben' (SPA 488) wurde bei der Auftragserfassung nicht korrekt
berücksichtigt. Bei Vorliegen einer harten Liefersperre eines Kunden konnte
trotz Einstellung 'Ja' kein Auftrag für den Kunden erfasst werden. Nun ist die
Erfassung eines Auftrages möglich, jedoch erscheint ein Warnhinweis für den
Fall, dass eine Liefersperre gesetzt ist.
Releasenote Kategorie:
Ticket: 724928[34006]
Version: 8.3.2308.4
Datum: 04.08.2023
Anwendung: AUE, AUB
Variante: alle
Funktion/Report: Auftrag erfassen
Weitere Informationen
Tags:
Releasenote, 8.3.2308.4, 34006, 724928

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

## Preiskalkulation Excel: Standardprozeduren

Preiskalkulation Excel: Standardprozeduren
In den Optionen für die Preiskalkulation Excel [PKX]
können jetzt auch die Standardprozeduren "AMIC_Excel_Preisimport_EK" (Einkauf)
und "AMIC_Excel_Preisimport_VK" (Verkauf) ausgewählt werden.  Diese beiden
Prozeduren sind nur mit den Standardvarianten unter [PKX] kompatibel. Wurde noch
keine Prozedur in den Optionen hinterlegt, so wird das Feld "Datenbankprozedur"
mit der jeweiligen Standardprozedur vorbelegt.
Releasenote Kategorie:
Ticket: 0[34620]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Preiskalkulation mit Excel [PKX]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.22, 34620, 0

---

## Kontraktbewegung zu Aufträgen und Bestellungen mit Belegnummer

Kontraktbewegung zu Aufträgen und Bestellungen mit Belegnummer
In den Kontraktbewegungen werden ab jetzt bei
Aufträgen und Bestellungen die Auftragsnummer und Bestellnummer angezeigt.
Releasenote Kategorie:
Ticket: 714314[32861]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Kontrakte [KTR]
Variante: Alle
Funktion/Report: Bewegungen, Ändern->Bewegungen
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 32861, 714314

---

## Streckenerfassungsprofil Kopiervorlagen

Streckenerfassungsprofil Kopiervorlagen
In den Streckenerfassungsprofilen können nun neben
Vorgangsfeldern auch Warenbewegungsaddon- und UFLD-Felder in der Kopiervorlage
definiert werden.
Releasenote Kategorie:
Ticket: 726427[34181]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Strecke
Variante: Erfassung / Profile
Funktion/Report: n/a
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34181, 726427

---

## Streckendisposition - Funktion "Position kopieren"

Streckendisposition - Funktion "Position kopieren"
In der Streckenerfassung werden nun im jeweiligen Grid
beim Ausführen der Funktion "Position kopieren" nicht nur die Standardfelder,
sondern zusätzlich die UFLD- und ADDON-Felder kopiert.
Releasenote Kategorie:
Ticket: 726427[34180]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Streckendisposition [DISPV]
Variante: Streckendisposition
Funktion/Report: Ändern/Neu
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34180, 726427

---

## Teildisposition mit Restausbuchung durch Stornobeleg

Teildisposition mit Restausbuchung durch Stornobeleg
Mit Hilfe des Steuerparameters "Schnelle Teildispo mit
Stornobeleg" (1147) ist es nun möglich bei der "Teildisposition aus Auftrag in
Lieferschein" die Restausbuchung mittels Stornoauftrag zu erstellen.
Releasenote Kategorie:
Ticket: 725304[34201]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Lieferschein [LIB]
Variante: Standard
Funktion/Report: F8 Lieferschein erfassen
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34201, 725304

---

## Maintenance

Maintenance
In der Belegerfassung kann zum Hauptkunden ein
Rechnungsempfänger und ein Zahlungspflichtiger in den Beleg eingetragen werden.
Ob dies nur in Einkauf oder Verkauf oder in beiden Fällen möglich ist regeln die
Steuerparameter 151 und 166. Bisher wurde bei einem Kundenwechsel der
Rechnungsempfänger/Zahlungspflichtiger nicht korrekt eingetragen.  Dies
wurde behoben.
Releasenote Kategorie:
Ticket: 727117[34263]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Belege
Variante: Erfassung
Funktion/Report: Erfassung
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34263, 727117

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

## Steuerparameter 791 umbenannt

Steuerparameter 791 umbenannt
Der Steuerparameter [SPA] 791 ist so umbenannt worden,
dass die Bezeichnung eindeutiger ist. Die neue Bezeichnung
lautet: "Sperr-Kennzeichnung für Einkauf/Verkauf aus dem Artikel auswerten
lassen".
Releasenote Kategorie:
Ticket: 732390[34889]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: ARTIKEL [AR]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34889, 732390

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

## Teildispo bei harter Liefersperre

Teildispo bei harter Liefersperre
Bei eingestellter harter Liefersperre im Kunden wurde
die Meldung dazu im Rahmen der Teildisposition nicht korrekt angezeigt. Dies
wurde behoben.
Releasenote Kategorie:
Ticket: 731498[34897]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Auftrag
Variante: Standard
Funktion/Report: Teildisposition Lieferschein
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 34897, 731498

---

## VKA Anzeige von alphanumerischen Belegnummern

VKA Anzeige von alphanumerischen Belegnummern
In der Anwendung Kunden-Verkaufsauswertung [VKA] in
der Variante "Basis für QuickReport (VKA)" werden jetzt auch alphanumerische
Belegnummern angezeigt.
Releasenote Kategorie:
Ticket: 733649[35113]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Kunden-Verkaufsauswertung [VKA]
Variante: Basis für QuickReport (VKA)
Funktion/Report: Auswahlliste
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 35113, 733649

---

## Waage mit Auftrags-Teildisposition

Waage mit Auftrags-Teildisposition
Wird in der Online-Waage eine Wiegung für einen
Lieferschein gegen einen Auftrag mit Teildisponierung erzeugt, so konnte es bei
der internen Berechnung der Teildispositions-Menge zu einem falschen Wert
kommen, wenn die Mengeneinheit der Wiegung nicht mit der Mengeneinheit der
referenzierten Auftragsposition übereinstimmt. Dieses Verhalten wurde nun
korrigiert.
Releasenote Kategorie:
Ticket: 731918[35441]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Waage
Variante: Hofliste
Funktion/Report: Wiegen
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 35441, 731918

---

## Nachkommastellen bei der Restmengenkorrektur

Nachkommastellen bei der Restmengenkorrektur
Die Restmengenkorrektur in den Anwendungen
"Auftrag-Mengenkorrektur" [AUK], "Bestellbearbeitung" [BSB],
"Auftragsbearbeitung" [AUB] ist in den Mengenfeldern von 2 auf 4
Nachkommerstellen angehoben worden.
Releasenote Kategorie:
Ticket: 737482[35616]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Vorgangsbearbeitung [AUK][BSB][AUB]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 35616, 737482

---

## Fehlermeldungen im Barverkauf mit der Herbstversion 9.0.2402.2

Fehlermeldungen im Barverkauf mit der Herbstversion 9.0.2402.2
In der Tresenkasse ist ein Fehler beim Barverkauf
aufgetreten: Wenn der EPA "Im Barverkauf sofort in Positionsteil" auf "Ja"
gesetzt ist, kam es bei jedem zweiten Barverkauf zu einem Fehler bei der Zahlung
mit anschließendem Belegabbruch. Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 739144[35732]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Barverkauf Tresen-/Marktkasse [BVVE]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.4, 35732, 739144

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

## Storno Lagerumbuchung bei Aufträgen zu Vorverkäufen

Storno Lagerumbuchung bei Aufträgen zu Vorverkäufen
Wenn bei vorverkaufter Ware die Abholung von einem
anderen Lager als dem ursprünglich vereinbarten Lager erfolgen soll, so erzeugt
Referenz-ERP automatisch eine Lagerumbuchung auf das zu verwendende Abhollager. Diese
Umbuchung kann durch unterschiedliche Vorgänge getriggert werden, die vorrangig
verwendeten sind Auftrag und Lieferschein. Wird dieser Abholvorgang allerdings
storniert, so muss auch die Lagerumbuchung storniert werden. Für die Stufe
Auftrag funktionierte dieser Lagerumbuchungsstorno nicht korrekt und führte zu
einer Verdoppelung der Bestände. Dieser Fehler wurde korrigiert.
Releasenote Kategorie:
Ticket: 743189[36297]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Auftragsbearbeitung
Variante: -
Funktion/Report: Storno Auftrag bei Vorverkauf
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36297, 743189

---

## Funktion Belegdatum ändern zu AWL

Funktion Belegdatum ändern zu AWL
In der Auswahlliste von Eingangsgutschriften [EGB] und
Verkaufsgutschriften [GUB] steht jetzt die Funktion Belegdatum ändern, analog
zur Rechnungsbearbeitung, zur Verfügung.
Releasenote Kategorie:
Ticket: 745347[36648]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Gutschrift bearbeiten
Variante: -
Funktion/Report: [GUB][EGB]
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36648, 745347

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

## Warenerfassung manuelle EK-Preise

Warenerfassung manuelle EK-Preise
Bei Verkaufsbelegen wurde die Maske für manuelle
EK-Preise zu früh geöffnet. Dies hat dazu geführt, dass der Rest der Warenmaske
nicht geladen wurde. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 745390[36733]
Version: 9.0.2501.5
Datum:
Anwendung: Vorgangserfassung - Verkaufsbelege
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36733, 745390

---

## UFLD "Gültig bis"

UFLD "Gültig bis"
Ein neues UFLD-Feld "Gültig bis" wurde erstellt. Es
kann z.B. für Angebote eingerichtet werden.
Releasenote Kategorie:
Ticket: 745194[37120]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Userfelder
Variante: Benutzerfelder
Funktion/Report: Bearbeiten
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37120, 745194

---

## Mailstatus in Rohware-Auswahllisten

Mailstatus in Rohware-Auswahllisten
In den passenden Auswahlvarianten der Anwendungen
Rohwarebearbeitung Einkauf und Verkauf wurden die Auswahllisten um die Spalten
'Mail versendet' und 'Versand' zur Darstellung des Mailstatus und ggf. des
Zeitpunktes des Versandereignisses erweitert.
Releasenote Kategorie:
Ticket: 747508[37195]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: RWB, RWBV
Variante: Lieferungen, Belege mit Gesamtwerten,
Kontraktlieferungen, Partielieferungen, Lieferungen nach Artikelnummern, Eine
Rohwarengruppe
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37195, 747508

---

## Vertreterprovisionsgruppenpfleger modernisiert und Vertreterstaffelpfleger verbessert.

Vertreterprovisionsgruppenpfleger modernisiert und Vertreterstaffelpfleger
verbessert.
In der Anwendung Vertreterprovisionsgruppen [VEPGR]
wurde der Pfleger für Vertreterprovisionsgruppen modernisiert. Man kann jetzt
aus diesem Pfleger, wenn als Provisionstyp in Provisionstyp VERKAUF und oder
Provisionstyp EINKAUF der Provisionstyp Staffelprovision (OPT-Preis) und
oder Staffelprovision (Preis+ZuAB) eingerichtet wurde, mit Hilfe der neuen
Funktion "Provisionsgruppenstaffel bearbeiten" die Auswahlliste zum Anlegen und
Bearbeiten der Provisonsstaffel öffnen.Es wird dadurch in den Filter der
Auswahlliste die Provisionsgruppennummer und ob es für Einkauf, Verkauf oder
beides im Filter eingetragen.Früher wurde bei der Auswahl vom
Provisionstyp Staffelprovision (OPT-Preis) und oder Staffelprovision
(Preis+ZuAB) auf dem Provisionsgruppenpfleger eine Maske automatisch geöffnet in
der man die Staffelprovision pflegen kann.Aufgrund von Redundanz gibt es jetzt
nur noch den anderen Pfleger in der
Anwendung Vertreterprovisionsstaffel  in der Variante Staffelprovision
pro Vertreterklasse.In der Anwendung Vertreterprovisionsstaffel wurde der
Pfleger für Provisionsstaffeln im Grid angepasst. Dort werden die einzelnen
Datensätze jetzt korrekt gespeichert.
Releasenote Kategorie:
Ticket: 0[37342]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: [VEPGR]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37342, 0

---

## Fehler bei Fibu-Übertrag von Barverkaufsbelegen mit Gruppenrabatt

Fehler bei Fibu-Übertrag von Barverkaufsbelegen mit Gruppenrabatt
Für den Fibu-Übertrag von Barverkaufsbelegen mit
Gruppenrabatten konnte es vorkommen, dass Einträge nicht übertragen werden
konnten.  Dies wurde behoben.
Releasenote Kategorie:
Ticket: 752268[39519]
Version: 9.0.2502.9
Datum:
Anwendung: Fibu Übertrag
Variante: Standard
Funktion/Report: Fibu Übertrag (F5)
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39519, 752268

---

## Chefauswertung

Chefauswertung
Hauptmenü
Informationen
Management Information
Chefauswertung
Direktsprung
[CHEF]
Chefauswertung (Individuell gestaltbare BWA) Warenein-
und -verkauf sowie die Bestandswertung werden aus der Warenwirtschaft
herangezogen. Zudem werden die Kostenpositionen aus der Finanzbuchhaltung
abgebildet für all jene GuV-Konten, die im
Sachkontenstamm [SKS]
die
Druckpositionen im Feld
Chefauswertung
eingerichtet haben.
Danach kann der Report für ein gewünschtes
Wirtschaftsjahr gestartet werden. Auswählbar ist außerdem bis zu welcher Periode
die Werte berücksichtigt werden sollen.
Beim Starten des Reports wird geprüft, ob die
Einrichtung der Druckpositionen für GuV-Konten unvollständig ist. Ist dies der
Fall kommt eine Meldung. Möchte man die Meldung nicht bekommen, dann kann dies
unter Optionen [OPT] Chefliste_VollstEinrNichtPruefen für den jeweiligen
Benutzer eingerichtet werden. Dafür reicht es, wenn man das Feld Wert mit einem
beliebigen Text füllt. Ist das Feld Wert leer, dann läuft die Prüfung beim Start
des Reports.

---

## Disposition von Bestellungen und Aufträgen

Disposition von Bestellungen und Aufträgen
Hauptmenü
Vorgang
Warenverkauf
Aufträge
Streckendisposition
Direktsprung
[DISP]
Die Anwendung dient der Unterstützung bei der
Beantwortung von Fragen wie:
•
Welcher Bestand eines Artikels steht zu einem zukünftigen Termin
zur Verfügung, um ein Plandatum (Liefertermin) für einen neuen Auftrag
festzulegen.
•
Welche Menge eines Artikels muss zu wann bestellt oder produziert werden,
um offene Aufträge mit festgelegtem Plandatum erfüllen zu können.
Die Varianten der Auswahllisten der Anwendung
unterscheiden sich hinsichtlich der Ausgabe:
•
Disposition täglich bis Stichtag
Eine Zeile pro ausgewähltem Artikel
für jeden Kalendertag ab ausgewähltem Von-Plandatum ( aber mindestens Datum des
aktuellen Tages) bis zum ausgewählten Bis-Plandatum
•
Disposition täglich und Stichtag
Eine Zeile pro ausgewähltem Artikel
für das ausgewählte Bis-Plandatum und pro Plandatum der offenen Aufträge
•
Disposition täglich nach Kalenderwoche
Eine Zeile pro ausgewähltem
Artikel für jede Kalenderwoche ab ausgewählter Ab-Kalenderwoche ( aber
mindestens die aktuelle Kalenderwoche) bis zur ausgewählten
Bis-Kalenderwoche
•
Disposition täglich nach Kalenderwoche und Endwoche
Eine Zeile pro
ausgewähltem Artikel für die ausgewählte End-Kalenderwoche und pro Planwoche der
offenen Aufträge
•
Disposition täglich nach Planperiode
Eine Zeile pro ausgewähltem
Artikel für jede Periode ab ausgewählter Ab-Periode ( aber mindestens der
aktuelle Periode) bis zur ausgewählten End-Periode der offenen Aufträge
•
Disposition täglich nach Planperiode und Endperiode
Eine Zeile pro
ausgewähltem Artikel für die ausgewählte End-Periode und pro Planperiode der
offenen Aufträge
Dargestellt wird in einer Zeile neben der Angabe des
Datums, der Kalenderwoche oder der Periode jeweilige Artikelnummer und
Artikelbezeichnung, die laut jeweiligem Plandatum kumulierte Bestellmenge,
Auftragsmenge, zu produzierende Menge aus Produktionsaufträgen. Eine weitere
Spalte zeigt
[...]


---

## Dauerauftrag: Anschrift aktualisieren

Dauerauftrag: Anschrift
aktualisieren
Hauptmenü
Warenverkauf
Auftrag
Dauerauftrag bearbeiten
oder Direktsprung
[DAB]
Steht der Steuerparameter
„Anschriften archivieren?“
auf „Ja“, so werden in
Vorgängen die Anschriften zum Zeitpunkt der Erfassung festgehalten. Wird die
Kundenhauptanschrift nach der Erfassung des Dauerauftrags geändert, so wird die
Anschrift im Dauerauftrag nicht aktualisiert. Die alte Anschrift bleibt im
Dauerauftrag bestehen. Das gleiche gilt auch für Rechnungen, die aus dem
Dauerauftrag erstellt werden. Sie enthalten auch die alte Anschrift.
In dem Dialog „Dauerauftrag: Anschriften
aktualisieren“ kann die Hauptanschrift einzelner oder mehrerer Daueraufträge
aktualisiert werden. In der Datentabelle werden alle Daueraufträge aufgelistet,
die über eine veraltete Hauptanschrift oder eine manuelle Vorgangsanschrift
verfügen. In dem Feld „Aktualisieren?“ können die jeweiligen Daueraufträge
ausgewählt und mithilfe der Funktion
Anschriften aktualisieren
aktualisiert
werden.
Hinweis: Die Anschrift eines Dauerauftrags kann auch
während seiner Korrektur aktualisiert werden (siehe
Hauptanschrift
aktualisieren
). Außerdem besteht für Daueraufträge die
Möglichkeit, dass die Hauptanschriften automatisch aktualisiert werden (siehe
Steuerparameter
Anschrift im Dauerauftrag automatisch
aktualisieren
).
Feld
Beschreibung
Kundennummer
Der
      Kunde des Dauerauftrags.
Belegnummer
Die
      Belegnummer des Dauerauftrags.
AdressId des Vorgangs
Die
      ID der Hauptanschrift, die im Dauerauftrag hinterlegt ist.
Manuell
Kennzeichen, ob es sich bei der
      Hauptanschrift des Dauerauftrags um eine manuelle Vorgangsanschrift
      handelt.
•
„Ja“:
      Hauptanschrift des Vorgangs ist eine manuelle
      Vorgangsanschrift.
•
„Nein“:
      Hauptanschrift des Vorgangs ist keine manuelle
      Vorgangsanschrift.
Name
Name
      und Vorname, die in der Hauptanschrift des Dauerauftrags angegeben
      sind.
AdressId des Kunden
Die
      ID der Ku
[...]


---

## Vorgangserfassung nach Artikelliste (EPA ANGEBOTSLISTE)

Vorgangserfassung nach Artikelliste (EPA
ANGEBOTSLISTE)
Bezeichnung
Standardwert
Erklärung
Bestellte Menge abfragen in Klassen
      (mit Komma trennen)
0
Gebindefaktor -1- abfragen in
      folgenden Klassen (s.o.)
0
Gebindefaktor -2- abfragen in
      folgenden Klassen (z.B. 200,300)
0
Gebindemengenfeld abfragen in
      folgenden Klassen (s.o.)
0
Preismengeneinheit abfragen in
      folgenden Klassen (s.o.)
0
Preis abfragen in folgenden Klassen
      (s.o.)
0
Preis pro abfragen in folgenden
      Klassen (s.o.)
0
Zusatz abfragen in folgenden Klassen
      (s.o.)
0
Name
      des Addonfeldes, in dem der Auftragsbestand im Lieferschein eingetragen
      wer
Artikelgruppe, für die doppelte
      Erfassung erlaubt ist (muss > 0 sein)
0
Artikel in die MSA-Liste
      übernehmen
Abfragen
Liste der Artikelnummern für
      Textänderungen zugelassen
Soll
      die Artikelliste bei einer neuen Zeile automatisch aufgerufen
      werden?
Nein
Druckauswahlfenster
Nein
Druckvorbelegung
Nein
Artikelnummer anzeigen in folgenden
      Klassen (s.o.)
0
Bestellte Menge anzeigen in Klassen
      (mit Komma trennen)
0
Gebindefaktor -1- anzeigen in
      folgenden Klassen (s.o.)
0
Gebindefaktor -2- anzeigen in
      folgenden Klassen (z.B. 200,300)
0
Gebindemengenfeld anzeigen in
      folgenden Klassen (s.o.)
0
Letzter VK Maskenfeld anzeigen in
      folgenden Klassen (s.o.)
0
Mengeneinheit anzeigen in folgenden
      Klassen (s.o.)
0
Mengeneinheitsnr. anzeigen in
      folgenden Klassen (s.o.)
0
Preismengeneinheit anzeigen in
      folgenden Klassen (s.o.)
0
Position anzeigen in folgenden
      Klassen (s.o.)
0
Preis anzeigen in folgenden Klassen
      (s.o.)
0
Preis pro anzeigen in folgenden
      Klassen (s.o.)
0
Zusatz anzeigen in folgenden Klassen
      (s.o.)
0
Itembox Artikel
IB_ARTIKEL_NU
Itembox Kunde
IB_KU
Itembox Zusatz
Vorgangsklasse, bei der keine Preise
      gezogen werden
0
Im
      Umwandlungsfall eine ¨polnische¨ Korrekturrechnung ers
[...]


---

## Marktstand Angebote (EPA MARKTSTANDANGEBOTE)

Marktstand Angebote (EPA
MARKTSTANDANGEBOTE)
Bezeichnung
Standardwert
Erklärung
Itembox auf das Nr. Feld als
      Kundenzuordnung
Itembox auf Zusatzinfo
Preislistennummer des Artikels, dem
      Preis 1 entspricht (0=kein Update)
0
Preislistennummer des Artikels, dem
      Preis 2 entspricht (0=kein Update)
0
Preislistennummer des Artikels, dem
      Preis 3 entspricht (0=kein Update)
0
Preislistennummer des Artikels, dem
      Preis 4 entspricht (0=kein Update)
0
Vererbung der Artikelsortierung aus
      Liste 0 heraus?
Ja
Vorbelegung des aktiv/passiv
      Feldes
Nein
Vorbelegung vererbt aus Liste für
      Preis 1 (leer keine Vererbung)
Vorbelegung vererbt aus Liste für
      Preis 2 (leer keine Vererbung)
Vorbelegung vererbt aus Liste für
      Preis 3 (leer keine Vererbung)
Vorbelegung vererbt aus Liste für
      Preis 4 (leer keine Vererbung)

---

## Miet-Lieferschein (EPA Mietvertraege_Lieferschein)

Miet-Lieferschein (EPA
Mietvertraege_Lieferschein)
Bezeichnung
Standardwert
Erklärung
Druckauswahlfenster
Nein
Druckvorbelegung
Nein
Itembox Artikel
IB_ARTIKEL_NU
Itembox Kunde
IB_KU
Itembox Zusatz
Listenpreisklassenliste 1 (mit Komma
      trennen)
0
Listenpreisklassenliste 2 (mit Komma
      trennen)
0
Listenpreisklassenliste 3 (mit Komma
      trennen)
0
Listenpreisklassenliste 4 (mit Komma
      trennen)
0
Letzten VK Preis mit
      anzeigen
Nein
Unterklasse für D1 Knopf
      (Default)
0
Unterklasse für D2 Knopf
0
Vorgangsklasse
600
Vorgangsunterklasse
0
Zielvorgangsklasse bei automatischer
      Umwandlung
0

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

## Partiestamm (EPA PARSTAM)

Partiestamm (EPA PARSTAM)
Bezeichnung
Standardwert
Erklärung
Fixpreise im Einkauf
      (J/N)
Nein
Fixpreise im Verkauf
      (J/N)
Nein
Fremdartikel zulassen
      (J/N)
Ja
Kundenbereich (Verkauf)
      (alle/Liste)
alle
Lieferantenbereich (Einkauf)
      (alle/Liste)
alle
Anzahl Nachkommastellen
      (0-4)
0
Benutzerformat für
      Qualitätsstatus
Benutzerformat für
      Sperrkennzeichen
Warengruppenbereich
      (alle/Liste)
alle

---

## (EPA PVSTRNEU)

(EPA PVSTRNEU)
Bezeichnung
Standardwert
Erklärung
Vorgangs-Klasse
      Gegenvorgänge
600
Vorgangs-Klasse Gegenvorg. im
      Verkauf
1600
Vorgangs-Unterklasse
      Gegenvorgänge
0
Vorgangs-Unterklasse Gegenvorg. im
      Verkauf
0

---

## Streckenerfassung (EPA STRECKENERFASSUNG)

Streckenerfassung (EPA
STRECKENERFASSUNG)
Bezeichnung
Standardwert
Erklärung
aktiver Tab bei Start der Maske
      (1-4)
4
Vorbelegung des Vorgangs im Tab
      Lieferant (1-8)
1

---

## Streckenstamm (EPA STRSTAM)

Streckenstamm (EPA STRSTAM)
Bezeichnung
Standardwert
Erklärung
Fixpreise im Einkauf
      (J/N)
Nein
Fixpreise im Verkauf
      (J/N)
Nein
Fremdartikel zulassen
      (J/N)
Ja
Kundenbereich (Verkauf)
      (alle/Liste)
alle
Lieferantenbereich (Einkauf)
      (alle/Liste)
alle
Anzahl Nachkommastellen
      (0-4)
0
Warengruppenbereich
      (alle/Liste)
alle

---

## MaskenTitel (EPA STRECKENERFASSUNG_LE_LVS)

MaskenTitel (EPA
STRECKENERFASSUNG_LE_LVS)
Bezeichnung
Standardwert
Erklärung
Standardladeträger, welcher zum
      Anlegen von neuen Ladeträgern verwendet wird

---

## MaskenTitel (EPA SVMAIN)

MaskenTitel (EPA SVMAIN)
Bezeichnung
Standardwert
Erklärung
Im
      Barverkauf sofort in Positionsteil
Nein
Sofortdruck Abfrage
Ja
'Druck korrekt ' Abfrage bei
      Sofortdruck
Ja
Sofortdruck Vorbelegung
Ja
Lagervorbelegung
      (leer:VKONS)
Kennzeichenabfrage
      unterdrücken
Nein
Korrekt Abfrage
Ja
Korrekt Vorbelegung
Ja
Leerbelege in Datenbank
      speichern?
Nein
Mehrbelegerfassung
Nein
Nach
      Kundeneingabe sofort in Positionsteil ?
Nein
Umwandelsperre abfragen
Nein
Versandadresse immer manuell
      auswählen
Nein
Versandart ( Vorbelegung, wenn im
      Kundenstamm= 0 )
0
Wochentagsformat
Wochentag(lang)

---

## Kostenverteilung Strecke (EPA SVWAREKLAMMER)

Kostenverteilung Strecke (EPA
SVWAREKLAMMER)
Bezeichnung
Standardwert
Erklärung
private Itembox für
      Klammerfindung
Standardmäßig wird nicht auf dem
      Feld Klammernummer (Dispositionsnummer) auf Vorhandensein geprüft, wird
      aber eine Itembox angegeben, so wird eine Prüfung
      durchgeführt.

---

## Transportauftrag zuordnen (EPA TRANSPO)

Transportauftrag zuordnen (EPA TRANSPO)
Bezeichnung
Standardwert
Erklärung
Lieferdatum wird
      Transportdatum
Nein

---

## Listenauswahl (EPA VDCRYST)

Listenauswahl (EPA VDCRYST)
Bezeichnung
Standardwert
Erklärung
Automatisch ohne Abfrage starten
      (EPA per BDKL ggf. zurücksetzen)
Nein
Default Crystalreportnummer (Format
      : AF_CRW100) Angebote
0
Default Crystalreportnummer (Format
      : AF_CRW1400) Bestellungen
0
Default Crystalreportnummer (Format
      : AF_CRW1600) Eingangslieferscheine
0
Default Crystalreportnummer (Format
      : AF_CRW1700) Eingangsrechnung
0
Default Crystalreportnummer (Format
      : AF_CRW1800) Eingangsgutschrift
0
Default Crystalreportnummer (Format
      : AF_CRW400) Aufträge
0
Default Crystalreportnummer (Format
      : AF_CRW5220) Produktion
0
Default Crystalreportnummer (Format
      : AF_CRW600) Lieferscheine
0
Default Crystalreportnummer (Format
      : AF_CRW700) Rechnungen
0
Default Crystalreportnummer (Format
      : AF_CRW800) Gutschriften
0
Druckmerker im Vorgang
      setzen
Nein
Ausgabemedium (WINDOW oder
      PRINTER)
WINDOW
Reportvorlage eingebbar (Ja: Vorlage
      kann gewählt werden)
Nein

---

## Vorgangsklammer (EPA VORGANGSKLAMMER)

Vorgangsklammer (EPA
VORGANGSKLAMMER)
Bezeichnung
Standardwert
Erklärung
Profilname der Strecke für
      Einkauf
Standardprofil für den Einkauf, wenn
      die Vorgangsmappe von Andere Stelle als der Vorgangsmappenauswahlliste
      aufgerufen wird. (z.B. aus den Aufträgen)
Profilname der Strecke für
      Verkauf
Standardprofil für den Verkauf, wenn
      die Vorgangsmappe von Andere Stelle als der Vorgangsmappenauswahlliste
      aufgerufen wird. (z.B. aus den Aufträgen)
Soll
      die Registerkarte Vorgänge versteckt werden?
Nein
Verstecken der Registerkarte
      Vorgänge
Soll
      die Registerkarte Tour versteckt werden?
Nein
Verstecken der Registerkarte
      Tour
Soll
      die Registerkarte Ladetermine versteckt werden?
Nein
Verstecken der Registerkarte
      Ladetermine
Soll
      die Registerkarte Positionsstammsatz versteckt werden?
Nein
Verstecken der Registerkarte
      Positionsstammsatz
(derzeit nicht aktiv)
Soll
      das Feld Klammerbezeichnung versteckt werden?
Nein
Verstecken des Feldes
      Klammerbezeichnung
Soll
      das Feld Bediener versteckt werden?
Nein
Verstecken des Feldes
      Bediener
Soll
      das Feld Container versteckt werden?
Nein
Verstecken des Feldes
      Container
Soll
      das Feld Abw. Adresse versteckt werden?
Nein
Verstecken des Feldes Abw.
      Adresse

---

## Frachtgruppe

Frachtgruppe
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Frachtgruppen
[FRAG]
Artikel können eine Frachtgruppe und/oder eine
individuelle Frachtgruppe sowohl im Einkauf als auch im Verkauf zugeordnet
bekommen. Diese beschreibt jeweils die Zugehörigkeit zu einer Gruppe von
Artikeln, für die für Kunden und Lieferanten mit einer dort zugeordneten
Frachtklasse beziehungsweise individuellen Frachtklasse zugeordnete Fracht
berechnet wird.
Frachtgruppen werden für Einkauf und Verkauf separat
eingerichtet. Sie werden im Artikelpfleger mit der Funktion
Gruppenzuordnungen
zugeordnet. Dabei kann eine Frachtgruppe sowohl als
normale wie auch als individuelle Frachtgruppe verwendet werden.

---

## Frachtklasse

Frachtklasse
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Frachtklassen
Kunden/Lieferanten können eine Frachtklasse und/oder
eine individuelle Frachtklasse sowohl im Einkauf als auch im Verkauf zugeordnet
bekommen. Diese beschreiben jeweils die Zugehörigkeit zu einer Gruppe von
Kunden/Lieferanten, für die für Artikel mit einer dort zugeordneten Frachtgruppe
beziehungsweise individuellen Frachtgruppe eine zugeordnete Fracht berechnet
wird.
Frachtklassen werden für Einkauf und Verkauf getrennt
angelegt. Sie werden im Kundenstamm auf der Registerkarte Klassen zugeordnet.
Dabei kann eine Frachtklasse sowohl als normale wie auch als individuelle
Frachtklasse verwendet werden.

---

## Storno innerhalb des Kassenmoduls

Storno innerhalb des Kassenmoduls
Im Pulldown-Menü Vorgang/Barvorgänge/Gesamtbarverkauf
gibt es 3 neue Varianten:
Die Auswahl der Belege ist beschränkt auf von Kassen
erzeugte Belege.
In diesen Varianten stehen Funktionen zur Verfügung,
die sonst nur unter REB, GUB, bzw. ERB zur Verfügung stehen. Dabei ist die
Profilierung abgrenzbar nach Belegnummer, Kassennummer, Datum, Kundennummer und
Bearbeiter. Außerdem kann eingestellt werden, ob stornierte Belege mit
umgekehrten Vorzeichen dargestellt werden sollen.
Neu sind die Funktionen Storno…
Wenn diese Funktion aufgerufen wird, passiert
Folgendes (nachdem die Abfrage bzgl. Umwandeln mit Ja bestätigt wurde):
Bei angeschlossener Schublade geht diese auf
Die Folgemasken werden automatisch vorbelegt und
durchlaufen
Es wird überprüft, ob der Arbeitsplatz, an dem der
Storno durchgeführt wird, eine Kasse ist
Es wird überprüft, ob die Kasse eröffnet ist
Es wird überprüft, ob bei Storno von Barverkäufen
genug Rückgeld vorhanden ist
Wenn c)-e) erfüllt sind, wird wie folgt
weitergemacht:
Es wird ein Stornobeleg erzeugt, der auch im
Belegüberblick zu sehen ist.
Es wird ein Zahlungssatz in Kassenwährung über den
Betrag des Urbeleges erzeugt, den der Kassierer auszugleichen hat durch
Geldbewegung innerhalb der Schublade
Die Kassenbestände werden gemäß diesen Betrag
angepasst
Es erscheint eine Meldung, die den Kassierer auf den
Betrag hinweist
Wenn c)-e) nicht erfüllt sind, wird mit einer
Hinweismeldung abgeschlossen.
Auf dem Kassenbericht sind weitere Felder
hinzugekommen, die Anzahl und Betrag bzgl. Storno Barverkauf,... anzeigen.
Der Kassenbestand wird immer an der Kasse angepasst,
an der der Storno erzeugt wird.
Das Ganze ist unabhängig vom FiBu-Übertrag. Wenn der
Urbeleg noch nicht übertragen ist, wird auch der erzeugte Stornobeleg nicht
übertragen. Wenn der Urbeleg schon übertragen ist, wird auch der erzeugte
Stornobeleg mit umgekehrtem Vorzeichen übertragen.
Vorbereitende Maßnahmen, um Storno-Barverkäufe,
[...]


---

## Sachkundenachweis Auswertung(SPA 1001)

Sachkundenachweis Auswertung(SPA 1001)
Mit diesem Steuerparameter wird festgelegt, wie in der
Vorgangserfassung (nicht in der Kasse!) das nicht-Vorliegen eines
Verkaufsbeschränkungszertifikats behandelt wird.
Einstellung
Bedeutung
Abfrage in der GUI
Wie
      bisher wird in dem Fall, dass ein Sachkundezertifikat im Artikelstamm
      eingetragen ist dieses auch im Kunden erwartet. Ist dies dort nicht
      eingetragen, so wird abgefragt, ob dies zum Zeitpunkt der Erfassung
      geprüft wurde.
Erfassung abweisen (nicht in der
      Kasse)
Ist
      im Artikelstamm ein Zertifikatstyp zugewiesen worden, so muss dieses
      Zertifikat im Kunden zu hinterlegen, sonst kann dieser Artikel im Vorgang
      nicht erfasst werden.
Ausnahme bilden hier nur diejenigen
      Artikel für die zwar eine Verkaufsbeschränkung vorliegt, aber kein
      Zertifikatstyp eingetragen ist. Darunter fällt z.B. Alkohol. Für diesen
      gibt es die Verkaufsbeschränkung ab 16 bzw. ab 18 Jahren, aber keinen
      Sachkundenachweis. Hier würde auch bei dieser SPA-Einstellung eine
      Prüfungsabfrage angezeigt werden.

---

## Partien auf Ladeschein-Ebene teildisponieren(SPA 1009)

Partien auf Ladeschein-Ebene teildisponieren(SPA 1009)
Wird eine Bestellung/ein Auftrag zu einem
Entladeschein/Ladeschein gewandelt ohne dass Partien darauf zugeordnet wurden,
so können diese nun im (Ent-)Ladeschein erfasst und bei der Teildispo in den
(Eingangs-)Lieferschein übernommen werden.
Damit werden bei aktivem Steuerparameter auch
bestehende Partiezuordnungen aus Bestellung/Auftrag durch den (Ent-)Ladeschein
im (Eingangs)-Lieferschein überschrieben. Enthält der Quellbeleg
(Bestellung/Auftrag) bereits Partien, so werden diese zunächst in den
(Ent-)Ladeschein übernommen, können aber dort nun abgeändert werden.

---

## Stornierung einer Ladescheinposition im Modul Ladeschein zu Lieferschein(SPA 1026)

Stornierung einer Ladescheinposition im Modul Ladeschein
zu Lieferschein(SPA 1026)
Mit diesem Steuerparameter kann eingestellt werden, ob
eine Ladescheinposition innerhalb des Moduls Ladeschein zu Lieferschein
storniert werden soll, wenn diese Position nur teilweise geliefert wurde. Dieser
Steuerparameter wirkt nur dann, wenn das Modul Ladeschein zu Lieferschein aus
dem Vorgangsimport aus aufgerufen wird.
Einstellung
Verhalten
Ja
      (Standard)
Position wird gelöscht.
Nein
Position wird nicht
      gelöscht.

---

## Angebot auf Sortimentslager zulassen (SPA 1051)

Angebot auf Sortimentslager zulassen (SPA 1051)
Einstellung
Bedeutung
Nein
Es kann kein Angebot gegen das
      Sortimentslager erfasst werden
.
Ja
Es
      kann ein Angebot gegen das Sortimentslager erfasst werden.

---

## Anzeige der Korrekturmengen und -werte (SPA 1073)

Anzeige der Ko
rrekturmengen und -werte (SPA
1073)
Mit diesem Steuerparameter kann die Anzeige der
Korrekturmengen und -werte in den Varianten „Aufträge mit Positionen“
[AUB]
und „Bestellungen mit Positionen“
[BSB]
aktiviert werden. Bei den
Korrekturmengen - und werten handelt es sich um technische Informationen, die
ausschließlich der Fehleranalyse dienen. Für den Endanwender wird die
Standardeinstellung „Nein“ empfohlen.

---

## Portal3-Optionen (SPA 1070)

Portal3-Optionen
(SPA 1070)
Option
Wert
Lagernummer
Hier
      ist die Lagernummer anzugeben.
Importmethode
0 =
      Beleg anlegen, 1 = Beleg nur in VIMP erzeugen
Vorgangsunterklasse Auftrag Import
      VIMP
Vorgangsunterklasse Auftrag für den
      Import in VIMP.
Vorgangsunterklasse Angebot Import
      VIMP
Vorgangsunterklasse Angebot für den
      Import in VIMP.
Kontraktunterklasse Import
      VIMP
Kontraktunterklasse für den Import
      in VIMP.
Pfad
      Archiv Dokumente
Pfad
      zum Speichern der Archiv Dokumente, welche per FTP Transport ans Webportal
      übergeben werden.

---

## Anschrift im Dauerauftrag automatisch aktualisieren (SPA 1082)

Anschrift im Dauerauftrag automatisch aktualisieren
(SPA 1082)
Mit der Einstellung „Ja“ wird die Hauptanschrift im
Dauerauftrag aktualisiert, sobald die Hauptanschrift des Kunden geändert wird.
Die Anschrift des Rechnungsempfängers und die Anschrift des Zahlungspflichtigen
im Vorgang werden nur dann aktualisiert, wenn diese mit der Hauptanschrift im
Vorgang übereinstimmen. Ansonsten werden diese nicht geändert.
Versandanschriften und manuelle Vorgangsanschriften werden nicht
aktualisiert.
Die Standardeinstellung ist „Nein“.
Hinweis:
Die Änderung der Anschrift im Dauerauftrag erfolgt bei
der Änderung der Hauptanschrift im Kunden- oder im Anschriftstamm, spätestens
bei der Umwandlung des Dauerauftrags in eine Rechnung. Die Aktualisierung findet
automatisch ohne vorherige Abfrage statt. Sie kann weder abgebrochen noch
rückgängig gemacht werden.

---

## Strecke(STR)-Lizenz (SPA1089)

Strecke(STR)-Lizenz (SPA1089)
Lizenz für Strecke(STR).

---

## Strecke(1zu1)-Lizenz (SPA1090)

Strecke(1zu1)-Lizenz (SPA1090)
Lizenz für Strecke(1zu1).

---

## Strecke(DISPV)-Lizenz (SPA1091)

Strecke(DISPV)-Lizenz (SPA1091)
Lizenz für Strecke(DISPV).

---

## Aktionspreis Verkauf (0: ohne)(SPA 11)

Aktionspreis Verkauf (0: ohne)(SPA 11)
Preisliste für Aktionspreise im Verkauf

---

## Vorbelegung Trennung bei Eingangslieferschein zu Sammelrechnungs-Umwandlung (SPA 1123)

Vorbelegung Trennung bei Eingangslieferschein zu
Sammelrechnungs-Umwandlung (SPA 1123)
Für die Maske zur Steuerung der Umwandlung von
Eingangslieferscheinen zu Sammelrechnungen im Einkauf legt dieser
Steuerparameter fest, wie das Optionsfeld
Einstellbare Trennungen einmalig
ausschalten
vorbelegt wird.
Mögliche Optionen sind:
-
mit Trennung
-
ohne Trennung

---

## Waage-Verkaufsbeschränkung-Lizenz (SPA1120)

Waage-Verkaufsbeschränkung-Lizenz (SPA1120)
Lizenz für die Verkaufsbeschränkung in der Waage

---

## Vorbelegung Trennung bei Sammelumwandlung von Bestellungen zu Lieferscheinen SPA 1137)

Vorbelegung Trennung bei Sammelumwandlung von Bestellungen zu Lieferscheinen
SPA 1137)
Für die Maske zur Steuerung der Umwandlung von
Bestellungen zu Sammellieferscheinen legt dieser Steuerparameter fest, wie die
Checkbox
Einstellbare Trennungen einmalig ausschalten
vorbelegt wird.
Mögliche Optionen sind:
-
mit Trennung
-
ohne Trennung

---

## Vorbelegung Trennung bei Sammelumwandlung von Bestellungen zu Eingangsrechnungen (SPA 1138)

Vorbelegung Trennung bei Sammelumwandlung von Bestellungen zu
Eingangsrechnungen (SPA 1138)
Für die Maske zur Steuerung der Umwandlung von
Bestellungen zu Sammelrechnungen legt dieser Steuerparameter fest, wie die
Checkbox
Einstellbare Trennungen einmalig ausschalten
vorbelegt wird.
Mögliche Optionen sind:
-
mit Trennung
-
ohne Trennung

---

## Schnelle Teildispo mit Stornobeleg (SPA 1147)

Schnelle Teildispo mit Stornobeleg (SPA 1147)
Wird dieser Steuerparameter auf „Ja“ gesetzt, so wird
bei der Teildisposition aus Auftrag mit Restausbuchung in der Positionserfassung
gleich ein Stornoauftrag über die auszubuchende Menge erstellt, der zusammen mit
dem Lieferschein erstellt wird.

---

## Rechnungstrennung durch Zahlungsbed.(SPA 126)

Rechnungstrennung durch Zahlungsbed.(SPA 126)
Ja: sind mehrere Lieferscheine mit verschiedenen
Zahlungsbedingungen markiert und man will diese in eine Sammelrechnung
umwandeln, so wird für jede Zahlungsbedingung eine Rechnung erstellt.
Nein: sind mehrere Lieferscheine mit verschiedenen
Zahlungsbedingungen markiert und man will diese in eine Sammelrechnung
umwandeln, so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden
den Zahlungsbedingungen der Lieferscheine zugeordnet.

---

## Vorgangsklasse änderbar bei Verkauf(SPA 148)

Vorgangsklasse änderbar bei Verkauf(SPA 148)
Bei „Ja“ kann während der Vorgangserfassung von der
aktuellen Vorgangsklasse in eine andere umgeschaltet werden.

---

## Fibu-Übertragung auch ungedruckt(SPA 149)

Fibu-Übertragung auch ungedruckt(SPA 149)
Dürfen auch ungedruckte Vorgänge an die Fibu
übertragen werden?
Einstellung
Bedeutung
Nein
Ungedruckte Belege dürfen nie in die
      FiBu übertragen werden.
Ja
Ungedruckte Belege dürfen immer in
      die FiBu übertragen werden.
Verkauf
Es
      dürfen nur ungedruckte Belege aus dem Verkauf in die FiBu übertragen
      werden.
Einkauf
Es
      dürfen nur ungedruckte Belege aus dem Einkauf in die FiBu übertragen
      werden.
Wenn
      mind. Archiviert
Belege müssen mindestens archiviert
      sein, müssen jedoch nicht gedruckt sein. Zu diesem Zweck kann in der
Vorgangsunterklasse
ein
      Formular eingetragen werden, das zur Archivierung beim FiBu-Übertrag
      verwendet wird.
EK
      immer und VK wenn mind. archiviert
Wie
      oben, jedoch dürfen Einkaufs-Belege immer ohne Druck in die FiBu
      übertragen werden.

---

## Negative Restmengen übern. b. Umwandlung(SPA 156)

Negative Restmengen übern. b. Umwandlung(SPA 156)
Bei „Nein“ werden negative Mengen nicht angeboten.

---

## Angebots-Unterklasse für Ordersätze(SPA 160)

Angebots-Unterklasse für Ordersätze(SPA 160)

---

## Rechnungstrennung durch Währungskurs(SPA 169)

Rechnungstrennung durch Währungskurs(SPA 169)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Währungskursen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jeden Währungskurs eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Währungskursen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden dem
Währungskurs der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Währungskursen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden dem Währungskurs
der Lieferscheine zugeordnet.

---

## Variante Haupt-Buchungstext Einkauf(SPA 170)

Variante Haupt-Buchungstext Einkauf(SPA 170)

---

## Variante Haupt-Buchungstext Verkauf(SPA 171)

Variante Haupt-Buchungstext Verkauf(SPA 171)

---

## Variante Preis-Auswahl (F3)(SPA 180)

Variante Preis-Auswahl (F3)(SPA 180)
In der Vorgangsbearbeitung kann im Feld mittels F3
Preisinformation abgerufen
0 - Standard: Anzeige der gültigen Preismatrix
1 - Auftrag/Angebot: Anzeige der in gültigen Aufträgen
/ Angeboten für diesen Artikel gespeicherten Preise
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Rechnungstrennung durch Parität(SPA 181)

Rechnungstrennung durch Parität(SPA 181)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Paritäten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jede Parität eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Paritäten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden der Parität der
Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Paritäten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden den Paritäten der
Lieferscheine zugeordnet.

---

## Preisklasse (Verkauf) aus der Versandart(SPA 190)

Preisklasse (Verkauf) aus der Versandart(SPA 190)
Soll im Verkauf die Versandart die Preisklasse
auslösen? Es kann in den Versandarten eine Preisklasse eingetragen werden, die
die des Kunden übersteuert. Die Preislistenfindung wird damit
versandartabhängig.

---

## Objekt(e) bei Lieferschein vorschlagen(SPA 202)

Objekt(e) bei Lieferschein vorschlagen(SPA 202)
Ja: Bei LS-Erfassung wird das erste Objekt das zum
Kunden gehört, vorgeschlagen
Nein: Es wird kein Objekt vorgeschlagen, es muss
manuell erfasst werden.

---

## Summenprüfung Wareneingang mit Vorgaben(SPA 212)

Summenprüfung Wareneingang mit Vorgaben(SPA 212)

---

## Rechnungstrennung durch Objekt(SPA 218)

Rechnungstrennung durch Objekt(SPA 218)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Objekten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jedes Objekt eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Objekten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden dem Objekt der
Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Objekten markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden den Objekten der
Lieferscheine zugeordnet.

---

## Vorgangsdatum änderbar bis Lieferschein(SPA 219)

Vorgangsdatum änderbar bis Lieferschein(SPA 219)

---

## Rechnungstrennung durch Strecke(SPA 230)

Rechnungstrennung durch Strecke(SPA 230)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Strecken markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jede Strecke eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Strecken markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden der Strecke der
Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Strecken markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden den Strecken der
Lieferscheine zugeordnet.

---

## Kreditlimit-Prüfung(SPA 233)

Kreditlimit-Prüfung(SPA 233)
Abhängig vom Wert dieses Steuerparameters wird
innerhalb eines Vorganges folgendes überprüft:
Nein
: es erfolgt keine Überprüfung
Warnung
: nach Eingabe der Kundennummer wird bei
Ladescheinen, Ausgangslieferscheinen, Ausgangsrechnungen, Ausgangsgutschriften,
Eingangsrechnungen und Aufträgen (
Achtung: Steuerparameter 22 in dieser
Gruppe
) und deren Stornos eine Meldung ausgegeben, wenn das Kreditlimit
des Kunden überschritten ist.
Sperrung
: Neben der Warnmeldung zu Beginn, wird
der Beleg gegen Abschluss gesperrt, wenn das Kreditlimit überschritten ist; man
besitzt jedoch noch die sofortige Möglichkeit zur Korrektur des Beleges.
Abweisung
: Neben der Warnmeldung bei
Überschreitung zu Beginn, wird ein Abschluss grundsätzlich verhindert, wenn
das  Kreditlimit überschritten ist.

---

## Kreditlimit-Prüfung mit Auftrag/Bestellg(SPA 234)

Kreditlimit-Prüfung mit Auftrag/Bestellg(SPA
234)
Nein
: die Kreditlimitprüfung gemäß
Steuerparameter 21 dieser Gruppe berücksichtig offene Aufträge und Bestellungen
(+Storno) nicht.
Ja
: die Kreditlimitprüfung berücksichtigt auch
offene Aufträge und Bestellungen.

---

## Gewogener Einkaufspreis in Warenposition(SPA 238)

Gewogener Einkaufspreis in Warenposition(SPA 238)

---

## Streckenverwaltung aktiv(SPA 248)

Streckenverwaltung aktiv(SPA 248)
Mit diesem Steuerparameter kann die Streckenverwaltung
aktiviert / deaktiviert werden.

---

## 1 Auftrag je Warenposition abspeichern(SPA 251)

1 Auftrag je Warenposition
abspeichern(SPA 251)
Dieser Steuerparameter entscheidet, ob ein Auftrag mit
mehreren Warenpositionen beim Speichern automatisch in weitere Aufträge
aufgesplittet wird. Hierbei wird pro Warenposition ein Auftrag erzeugt. Die
Einstellung kann über [
FRZ
] für die
einzelnen Unterklassen überschrieben werden.
Wurden einzelne Warepositionen bereits teildisponiert,
so ist ein Auftragssplitting nicht mehr möglich!
Folgende Werte können im Steuerparameter gespeichert
werden:
Wert
Beschreibung
Nein
Es
      wird kein Auftragssplitting durchgeführt.
Ja
Auftragssplitting wird
      durchgeführt.
Abfrage
Es
      wird beim Beenden des Vorgangs abgefragt, ob ein Auftragssplitting
      durchgeführt werden soll.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## unbepreiste Lieferscheine = Umwandelsperre(SPA 253)

unbepreiste Lieferscheine = Umwandelsperre(SPA
253)
Für unbepreiste Lieferscheine (Vorgangsklasse 600 und
690) kann man hier einstellen, ob eine Umwandelsperre gesetzt werden soll oder
nicht.
Als unbepreist gelten die Lieferscheine, wenn sie in mindestens einer
Warenposition einen Artikel haben für den noch kein Preis ermittelt wurde
(WaBewPreisWoher = 0).
SPA-Einstellungen
0 –
      Nein
Es
      wird keine Umwandelsperre gesetzt.
1 –
      Ja
Es
      soll für unbepreiste Lieferscheine eine Umwandelsperre gesetzt
      werden.
2 –
      mit Meldung
Es
      soll für unbepreiste Lieferscheine eine Umwandelsperre gesetzt und eine
      Meldung ausgegeben werden, dass der Beleg für die Umwandlung gesperrt
      wurde.

---

## Kontrakte bereits ab Auftrag/Bestellungen ziehen (SPA 254)

Kontrakte bereits ab Auftrag/Bestellungen ziehen (SPA 254)
Es wird schon ab Auftrag bzw. Bestellung mit
Kontrakten gearbeitet.

---

## Partien bereits ab Auftrag (SPA 255)

Partien bereits ab Auftrag (SPA 255)
Dieser Steuerparameter schaltet in der
Warenpositionserfassungen die Funktionen für die Partiezuordnung ein, wenn es
sich um die Erfassung eines Auftrags handelt, bzw. die Funktionen werden im
Auftrag ausgeblendet.

---

## Typ-Vorbelegung bei Streckenartikel-Anlage(SPA 278)

Typ-Vorbelegung bei Streckenartikel-Anlage(SPA 278)

---

## Variante Strecken-Auswahl(SPA 279)

Variante Strecken-Auswahl(SPA 279)

---

## Mengeneinheitvorbelegung bei Streckenanlage(SPA 280)

Mengeneinheitvorbelegung bei Streckenanlage(SPA 280)

---

## Folgeartikel aktiv(SPA 288)

Folgeartikel aktiv(SPA 288)
Hier wird entschieden, wann Folgeartikel aktiviert
sein sollen.
Wert
Bedeutung
Nein
Folgeartikel werden nicht
      behandelt.
Einkauf
Folgeartikel werden nur im Einkauf
      behandelt.
Verkauf
Folgeartikel werden nur im Verkauf
      behandelt.
Einkauf und Verkauf
Folgeartikel werden nur im Einkauf
      und Verkauf behandelt.
Lagerumbuchung
Folgeartikel werden nur bei
      Lagerumbuchung behandelt.
Alle
Folgeartikel werden im Einkauf,
      Verkauf und bei Lagerumbuchung behandelt.

---

## Skonto bei Barverkauf generell gewähren(SPA 300)

Skonto bei Barverkauf generell gewähren(SPA 300)
(wenn der Vorgang als Barverkauf deklariert ist, aber
kein Kassenvorgang ist). Hier wird entschieden ob beim Barverkauf eine Abfrage
eingeschaltet ist, die abfragt, ob der Skontobetrag gewährt werden soll oder
nicht. Wenn diese Abfrage nicht geschaltet ist, wird automatisch gewährt.

---

## Streckendruck(SPA 304)

Streckendruck(SPA 304)

---

## Aktionspreis Verkauf = Maximalpreis(SPA 313)

Aktionspreis Verkauf = Maximalpreis(SPA 313)
Dieser Steuerparameter regelt die Behandlung von
Aktionspreisen im Zusammenspiel mit Partie- und/ oder Objektpreisen.
Bei Einstellung Ja: der kleinste Preis zieht
Bei Einstellung nein: es gilt der
Aktionspreis

---

## Restmengen b. Teildisposition ausbuchbar(SPA 320)

Restmengen b. Teildisposition ausbuchbar(SPA 320)
Bei „Ja“ wird auf der Teilumwandlungsmaske ein Knopf
angeboten mit dem der Rest bei einer echten Teilumwandlung auf dem Originalbeleg
ausgebucht wird.  Dieser Knopf ist  steht nur dann zur Verfügung, wenn
der Quellbeleg die Stufe Auftrag hat.
Ferner gibt es noch einen Einrichterparameter
Freischaltung dieses Knopfes auf der Maske.

---

## Warenbewegung auch bei Einkauf im Kontoblatt(SPA 343)

Warenbewegung auch bei Einkauf im Kontoblatt(SPA 343)

---

## Druck Quellinformationen einstufig(SPA 350)

Druck Quellinformationen einstufig(SPA 350)
Beim Umwandeln eines Vorgangs in eine höhere Stufe
(z.B. vom Auftrag zum Lieferschein) wird im Zielbeleg ein Informationsdatensatz
des Quellbeleges hinterlegt. Diese Daten lassen sich beim Formulardruck auch
darstellen. Bei Einstellung ‚Ja‘  werden nur die Daten der unmittelbar
voranliegenden Stufe angezeigt. Bei ‚Nein‘ werden alle Verweise auf
Vorgängerstufen angezeigt. Zu mehreren Verweisen kommt es, wenn man z.B. einen
Auftrag in einen Lieferschein wandelt, diesen Lieferschein dann in eine Rechnung
wandelt. Bei Einstellung ‚Ja‘  wird in diesem Beispiel der Verweis auf den
Auftrag nicht gedruckt.
Hinweis: Im Fall einer Gutschrift wird neben der
Rechnung trotz Einstellung „Ja“ noch ein weiterer Vorgängerbeleg angezeigt, da
Gutschrift und Rechnung technisch auf der gleichen Stufe stehen.

---

## manuelle EK-Preiseingabe(SPA 364)

manuelle EK-Preiseingabe(SPA 364)
Bei bestimmten Artikeln wird in der Relation „Artikel“
ein Kennzeichen für „manuelle EK-Preiseingabe im Verkauf“ hinterlegt. Bei
solchen Artikeln soll dann automatisch eine Eingabemaske kommen.

---

## Restmengenanzeige bei Streckenauswahl(SPA 381)

Restmengenanzeige bei Streckenauswahl(SPA 381)
Nein: Restmengen in der Partieauswahl nicht anzeigen
Ja: Restmengen anzeigen

---

## Auftrag trotz Liefersperre schreiben(SPA 488)

Auftrag trotz Liefersperre schreiben(SPA 488)
Dürfen trotz harter Liefersperre des Kunden Aufträge
erfasst werden?

---

## Vorbelegung Rabattgruppe Verkauf(SPA 50)

Vorbelegung Rabattgruppe Verkauf(SPA 50)
Welche Rabattgruppe soll im Verkauf vorbelegt
werden?

---

## Vorbelegung Skontierfähigkeit im Einkauf(SPA 511)

Vorbelegung Skontierfähigkeit im Einkauf(SPA 511)
Wie soll die Skontierfähigkeit des Artikels im Verkauf
vorbelegt werden?

---

## Vorbelegung Rabattgruppe Einkauf(SPA 51)

Vorbelegung Rabattgruppe Einkauf(SPA 51)
Welche Rabattgruppe soll im Einkauf vorbelegt
werden?

---

## Vorbelegung Skontierfähigkeit im Verkauf(SPA 510)

Vorbelegung Skontierfähigkeit im Verkauf(SPA 510)
Wie soll die Skontierfähigkeit des Artikels im Verkauf
vorbelegt werden?

---

## Auswerten des KundSammel-Kennzeichens(SPA 516)

Auswerten des KundSammel-Kennzeichens(SPA 516)
Im Kundenstamm gibt es das Kennzeichen
KundsammelKennz. Dieses wird wie folgt ausgewertet:
2 Einzelrechnungen, d.h. für diesen Kunden sind nur
die Funktionen Rechnung aus Lieferschein, Rechnung aus Angebot und Rechnung aus
Auftrag möglich
1 Sammelrechnung, d.h. für diesen Kunden sind nur die
Funktionen Sammelrechnung aus Angebot, Sammelrechnung aus Auftrag
und      Sammelauftrag aus Lieferschein
möglich
0: alles ist möglich.
Dieser Steuerparameter steuert, wie dieses Kennzeichen
ermittelt wird:
0: es wird nicht ausgewertet
1: aus dem Kunden der Vorgangszuordnung
2: aus dem Kunden des Rechnungsempfängers
3: aus dem Kunden des Zahlungspflichtigen

---

## Vorbelegung Listenpreisgruppe(SPA 522)

Vorbelegung Listenpreisgruppe(SPA 522)
Hier kann eingestellt werden, wie die
Listenpreisgruppe im neuen Artikelpfleger beim Kopieren/Speichern unter
übernommen   werden soll:
0: Listenpreisgruppe wird mit kopiert.
1: neue Listenpreisgruppe (nur Einkauf)
2: neue Listenpreisgruppe (nur Verkauf)
3: neue Listenpreisgruppe (Einkauf + Verkauf)

---

## Vorbelegung Zu/Abschlagsgruppe Verkauf(SPA 52)

Vorbelegung Zu/Abschlagsgruppe Verkauf(SPA 52)
Welche Zu/Abschlagsgruppe soll im Verkauf vorbelegt
werden?

---

## Vorbelegung Zu/Abschlagsgruppe Einkauf(SPA 53)

Vorbelegung Zu/Abschlagsgruppe Einkauf(SPA 53)
Welche Zu/Abschlagsgruppe soll im Einkauf vorbelegt
werden?

---

## Vorbelegung Frachtgruppe Verkauf(SPA 54)

Vorbelegung Frachtgruppe Verkauf(SPA 54)
Welche Frachtgruppe soll im Verkauf vorbelegt
werden?

---

## Vorbelegung Frachtgruppe Einkauf(SPA 55)

Vorbelegung Frachtgruppe Einkauf(SPA 55)
Welche Frachtgruppe soll im Einkauf vorbelegt
werden?

---

## Lieferscheinkorrektur in geschlossenen Perioden(SPA 556)

Lieferscheinkorrektur in geschlossenen Perioden(SPA 556)
Dürfen Lieferscheine in geschlossenen  Perioden
noch korrigiert werden (Ja / Nein).

---

## Vorbelegung Ladegruppe Verkauf(SPA 56)

Vorbelegung Ladegruppe Verkauf(SPA 56)
Welche Ladegruppe soll im Verkauf vorbelegt
werden?

---

## Vorbelegung Ladegruppe Einkauf(SPA 57)

Vorbelegung Ladegruppe Einkauf(SPA 57)
Welche Ladegruppe soll im Einkauf vorbelegt
werden?

---

## Vorbelegung Bonusgruppe Verkauf(SPA 58)

Vorbelegung Bonusgruppe Verkauf(SPA 58)
Welc
he Bonusgruppe soll im Verkauf vorbelegt werden?

---

## Erfassungsabbruch an POS Kasse erlaubt(SPA 581)

Erfassungsabbruch an POS Kasse erlaubt(SPA 581)
Standard: Ja. Im Fall Nein: Barverkauf POS kann nicht
abgebrochen werden, es sei denn Beleg ist leer oder alle Positionen sind
storniert.

---

## Vorbelegung Bonusgruppe Einkauf(SPA 59)

Vorbelegung Bonusgruppe Einkauf(SPA 59)
Welche Bonusgruppe soll im Einkauf vorbelegt
werden?

---

## Lagerumbuchung bei Lieferung Voreinkauf / Vorverkauf (SPA 603)

Lagerumbuchung bei Lieferung Voreinkauf / Vorverkauf (SPA 603)
Steht der Steuerparameter auf „Ja“, wird bei der
Fremdwareabholung oder bei der Fremdlagereinbringung eine automatische Umbuchung
des Fremdbestandes erzeugt, falls der entsprechende Vorverkauf / Voreinkauf auf
einem anderen Lager stattfand.

---

## Unterklasse automatische Lagerumbuchung bei Voreinkauf / Vorverkauf (SPA 604)

Unterklasse automatische Lagerumbuchung bei Voreinkauf / Vorverkauf (SPA
604)
Für
SPA
603
(automatische Umbuchung Fremdbestand) kann hier die Unterklasse
angegeben werden.

---

## Waage, Korrektur von Lieferscheinbelegen(SPA 610)

Waage, Korrektur von Lieferscheinbelegen(SPA
610)
Ja: Korrektur der Menge bei Lieferscheinbelegen, die
aus der Waage erzeugt wurden, erlaubt.

---

## Aktionspreis Einkauf (0: ohne)(SPA 63)

Aktionspreis Einkauf (0: ohne)(SPA 63)
Preisliste für Aktionspreise im Einkauf

---

## Plandatum unverändert bei Datumswechsel(SPA 682)

Plandatum unverändert bei Datumswechsel(SPA 682)
Bei „Nein“ wird das Plandatum (bei Angeboten,
Aufträgen und Lieferscheinen) nach jeder Änderung des Belegdatums angepasst. Bei
„Ja“ wird das Plandatum nur bei der ersten Belegung mit dem Belegdatum vorbelegt
- nachfolgende Änderungen am Belegdatum lassen das Plandatum unberührt.

---

## Vorkasse Auftragsunterklasse(SPA 694)

Vorkasse Auftragsunterklasse(SPA 694)
Unterklassennummer für den Vorkasse Auftrag

---

## Spezialfunktion Transportauftrag zuordnen(SPA 704)

Spezialfunktion Transportauftrag zuordnen(SPA 704)
J/n Schalter zur Freischaltung der Funktion
Transportauftrag. Eine sehr spezielle Funktion zur zusammenfassenden Darstellung
von Aufträgen zu einem gemeinsamen Spediteur.

---

## Auftragszusammenführungen erlauben (SPA 723)

Auftragszusammenführungen erlauben (SPA 723)
Dieser Steuerungsparameter aktiviert eine
Spezialfunktion „Aufträge zusammenführen“ in der Anwendung „Aufträge bearbeiten
[AUB]“.
Diese Funktion ermöglicht es, aus mehreren Aufträgen
einen Zusammenfassungsauftrag zu erstellen und dabei gleichzeitig das Lager auf
ein gemeinsames Lager zu setzen.
Zusammenfassungskriterien sind:
1.
Kundennummer
2.
Artikel
3.
Rechnungsempfänger
4.
Lieferadresse
5.
Lagerplatz
Da es sich hierbei, wie beschrieben, um eine
Spezialfunktion handelt, ist der Standardwert für diesen Steuerparameter „Nein“
und die Funktion somit in der Funktionsbox der Anwendung deaktiviert und nicht
sichtbar.

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

## Barverkaufsformulare bei Lieblingsdruckerdruck (SPA 777)

Barverkaufsformulare bei Lieblingsdruckerdruck (SPA 777)
Hier kann eingestellt werden, ob Barverkaufsformulare
(Vorgangsunterkasse 9900) in der Liste der Lieblingsdruckerformulare angezeigt
werden sollen

---

## Rechnungstrennung durch Filialnummer(SPA 78)

Rechnungstrennung durch Filialnummer(SPA 78)
Trennen: sind mehrere Lieferscheine aus verschiedenen
Filialen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jede Filiale eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine aus verschiedenen
Filialen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden der Filiale der
Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine aus verschiedenen
Filialen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden der Filiale der
Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Zentralenummer(SPA 79)

Rechnungstrennung durch Zentralenummer(SPA 79)
Trennen: sind mehrere Lieferscheine aus verschiedenen
Zentralen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jede Zentrale eine Rechnung erstellt. Neu: sind mehrere Lieferscheine aus
verschiedenen Zentralen markiert und man will diese in eine Sammelrechnung
umwandeln, so wird eine Sammelrechnung erstellt und die Warenbewegungen werden
der Zentrale der Rechnung zugeordnet. Nein: sind mehrere Lieferscheine aus
verschiedenen Zentralen markiert und man will diese in eine Sammelrechnung
umwandeln, so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden
der Zentrale der Lieferscheine zugeordnet.

---

## Sperr-Kennzeichnung für Einkauf/Verkauf aus dem Artikel auswerten lassen (SPA 791)

Sperr-Kennzeichnung für Einkauf/Verkauf aus dem Artikel
auswerten lassen (SPA 791)
Im Artikel lässt sich einstellen, ob dieser für den
Einkauf/Verkauf gesperrt ist. Das Kennzeichen wird mit Aktivierung (Einstellung
„Ja“) dieses Steuerungsparameters ausgewertet.
Ist die Einstellung des Steuerungsparameters „Nein“,
ist dieses Feld ohne Effekt.

---

## Bei 1zu1 Umwandlung Reihenfolge (SPA 799)

Bei 1zu1 Umwandlung Reihenfolge (SPA 799)
In der Standardeinstellung „wie Trennkriterien“ wird
die Reihenfolge der Umwandlung von Vorgängen in jeweils einen anderen Vorgang
(z.B. Lieferschein in Rechnung) wie bei Sammelrechnungen auch behandelt. Das
bedeutet, dass mindestens zunächst nach Kunden sortiert umgewandelt wird.
Bei der Einstellung „wie Quelle“ werden die Belege in
der Reihenfolge der Auswahl in der Auswahlliste umgewandelt.

---

## Rechnungstrennung durch Abteilung(SPA 80)

Rechnungstrennung durch Abteilung(SPA 80)
Trennen: sind mehrere Lieferscheine aus verschiedenen
Abteilungen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Abteilung eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine aus verschiedenen
Abteilungen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der Abteilung
der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine aus verschiedenen
Abteilungen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden der Abteilung
der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Unterabteilung(SPA 81)

Rechnungstrennung durch Unterabteilung(SPA 81)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Unterabteilungen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jede Unterabteilung eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Unterabteilungen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Unterabteilung der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine aus verschiedenen
Unterabteilungen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Unterabteilungen der Lieferscheine zugeordnet.

---

## Bediener aus Auftrag bei Teildisposition (SPA 811)

Bediener aus Auftrag bei Teildisposition (SPA 811)
Hier kann festgelegt werden, ob bei der
Teildisposition eines Lieferscheins aus der Auftragsbearbeitung der Bediener
beibehalten werden soll. So soll sichergestellt werden, dass der Ansprechpartner
der Auftragsannahme auch auf dem Lieferschein erscheint.

---

## Liefernummer auf Position eingeben (SPA 826)

Liefernummer auf Position eingeben (
SPA 826
)
Einstellungen
Nein
Diese Einstellung bietet keinerlei
      Erfassungsmöglichkeiten für Lieferscheinnummern auf der
      Warenposition
Immer
Bei
      Einstellung „Immer“ bietet sich auf der Warenpositionsmaske die
      Möglichkeit die Nummer des zugehörigen Lieferscheins (sofern dies in der
      Unterklasse zugelassen ist manuell zu erfassen.
Nur
      bei fehlendem Lieferschein
Bei
      dieser Einstellung wird die Möglichkeit zur Erfassung einer Liefernummer
      nur dann freigegeben, wenn dies in der Unterklasse freigegeben wurde und
      es zu dieser Positionszeile keine Positionszeile eines Lieferscheins in
      Referenz-ERP gibt. So sind Manipulationen bestehender belege ausgeschlossen. Das
      Eingabefeld wird nur bei direkter Erfassung eines Beleges freigegeben.

---

## Steuergruppen Gelangensbestätigung (SPA 830)

Steuergruppen Gelangensbestätigung (SPA 830)
Hier kann eine Liste von Steuergruppen hinterlegt
werden, für die die Gelangensbestätigung im Lieferschein automatisch erstellt
werden soll.

---

## Rechnungstrennung durch Sprache(SPA 84)

Rechnungstrennung durch Sprache(SPA 84)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Sprachen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
für jede Sprache eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Sprachen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden der Sprache der
Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Sprachen markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden der Sprache der
Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Steuergruppe(SPA 85)

Rechnungstrennung durch Steuergruppe(SPA 85)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Steuergruppen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Steuergruppe eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Steuergruppen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Steuergruppe der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Steuergruppen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden der Steuergruppe
der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Vertretergruppe(SPA 86)

Rechnungstrennung durch Vertretergruppe(SPA 86)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Vertretergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jede Vertretergruppe eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Vertretergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Vertretergruppe der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Vertretergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden der
Vertretergruppe der Lieferscheine zugeordnet.

---

## Rechnungsdruck bei Barverkauf (SPA 867)

Rechnungsdruck bei Barverkauf (SPA 867)
Hier können zwei Einstellungen vorgenommen werden:
1.
Ist der Druck von Rechnungsformularen im Barverkauf überhaupt möglich
2.
Ab welchem Betrag soll der Bediener gefragt werden, ob ein Rechnungsdruck
gewünscht ist. Vorgabe sollte hier 150 (Kassenwährungseinheiten z.B. „€“)
sein.

---

## Artikeltext übernehmen bei Strecke, wenn diverser Artikel(SPA 875)

Artikeltext übernehmen bei Strecke, wenn diverser Artikel(SPA 875)
Dieser Steuerungsparameter regelt bei der
Streckenerfassung die Übernahme des Artikeltextes eines diversen Artikels in die
Gegenbelege. Man achte darauf, dass der Text des Artikels vor der Verteilung auf
die Gegenpositionen geändert wird.

---

## Rechnungstrennung durch Verkaufsgebiet(SPA 87)

Rechnungstrennung durch Verkaufsgebiet(SPA 87)
Trennen: sind mehrere Lieferscheine aus verschiedenen
Verkaufsgebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jedes Verkaufsgebiet eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine aus verschiedenen
Verkaufsgebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden dem
Verkaufsgebiet der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine aus verschiedenen
Verkaufsgebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden dem
Verkaufsgebiet der Lieferscheine zugeordnet.

---

## Prozedur für Testbestellung(SPA 874)

Prozedur für Testbestellung(SPA 874)
Nicht WebPortal 2.0
Komplexer Steuerparameter.
Hier kann der Prozedur- oder Funktionsname hinterlegt
werden, welche/r bei Testbestellungen aus dem Webportal eingreifen soll.
-
Schlüssel
-
Option (Prozedur- oder Funktionsname)

---

## Rechnungstrennung durch Absendergebiet(SPA 88)

Rechnungstrennung durch Absendergebiet(SPA 88)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Absendergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jedes Absendergebiet eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Absendergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden dem
Absendergebiet der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Absendergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Absendergebieten der Lieferscheine zugeordnet.

---

## Automatische Artikellieferanten Zuordnung beim Vorgangsimport von Bestellungen (SPA 883)

Automatische Artikellief
eranten Zuordnung beim
Vorgangsimport von Bestellungen (SPA 883)
Mit diesem Steuerparameter kann eingestellt werden, ob
bei der Belegerzeugung einer Bestellung in der Anwendung Vorgangimport
[VIMP]
über die Funktion „Standarvorgang
erzeugen“ der Hauptlieferant eines Artikels gezogen werden soll.
Ausprägung
Bedeutung
Ja
Wird
      der Steuerparameter auf „Ja“ gestellt, so wird vor der Belegerzeugung
      geprüft, ob für diesen Artikel ein Lieferant in Referenz-ERP hinterlegt worden
      ist. Ist der Lieferant unterschiedlich zu dem im Stammsatz hinterlegten
      Lieferanten, so wird für diese Position ein neuer Stammsatz und eine neue
      Positionszeile erzeugt. Existiert zu diesem Lieferanten eine noch nicht
      eingespielte Bestellung, so wird diese Position dem noch nicht
      eingespielten Stammsatz zugeordnet.
Existiert kein Lieferant zu diesem
      Artikel, so wird der Lieferant aus dem originalen Stammsatz
      beibehalten.
Soll
      die Lieferantensuche trotz aktiven Steuerparameter für die Artikelposition
      nicht durchgeführt werden, so muss das Kennzeichen
      „KundenAenderungManuell“ im Stammsatz auf 1 gesetzt werden.
Nein
Bei
      der Vorgangserzeugung wird immer der Lieferant aus dem Stammsatz
      gewählt.

---

## Liste Empfänger Bestätigungsmail(SPA 887)

Liste Empfänger Bestätigungsmail(SPA 887)
Nicht WebPortal 2.0
Komplexer Steuerparameter.
Hier kann festgelegt werden, wer zusätzlich bei
Eingang einer Bestellung aus dem WebPortal per E-Mail benachrichtigt werden
soll. S.h., eine Liste, durch Semikolon getrennt, von E-Mail Adressen.
-
Schlüssel
-
Option (Liste von E-Mail Adressen, durch Semikolon getrennt)

---

## Rechnungstrennung durch Empfängergebiet(SPA 89)

Rechnungstrennung durch Empfängergebiet(SPA 89)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Empfängergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jedes Empfängergebiet eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Empfängergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden dem
Empfängergebiet der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Empfängergebieten markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Empfängergebieten der Lieferscheine zugeordnet.

---

## Verkaufsbeschränkung (SPA 900)

Verkaufsbeschränkung (SPA 900)
Mit dieser Einstellung wird die Zusatzoption
Verkaufsbeschränkungen für die Verwendung eingeschaltet. Die
Verkaufsbeschränkungen können zum Beispiel Altersbeschränkungen oder
Sachkundenachweise sein, die beim Verkauf vorliegen müssen.

---

## Rechnungstrennung durch Zahlungsart(SPA 91)

Rechnungstrennung durch Zahlungsart(SPA 91)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Zahlungsarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Zahlungsart eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Zahlungsarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der Zahlungsart
der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Zahlungsarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden der Zahlungsart
der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Fakturiergruppe(SPA 93)

Rechnungstrennung durch Fakturiergruppe(SPA 93)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Fakturiergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jede Fakturiergruppe eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Fakturiergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Fakturiergruppe der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Fakturiergruppen markiert und man will diese in eine Sammelrechnung umwandeln,
so wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Fakturiergruppen der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch LKW (Motorwagen)(SPA 94)

Rechnungstrennung durch LKW (Motorwagen)(SPA 94)
Trennen: sind mehrere Lieferscheine mit verschiedenen
LKW (Motorwagen) markiert und man will diese in eine Sammelrechnung umwandeln,
so wird für jeden LKW (Motorwagen) eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen LKW
(Motorwagen) markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden dem LKW
(Motorwagen) der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen LKW
(Motorwagen) markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den LKW
(Motorwagen) der Lieferscheine zugeordnet.

---

## LVS Fahrauftrag verwenden (SPA 947)

LVS Fahrauftrag verwenden (SPA 947)
In diesem Steuerparameter kann in der Option mit
leerem Schlüssel eine Datenbankfunktion hinterlegt werden, die beim Speichern
einer Ladeträgerbewegung aufgerufen wird.
Als Eingangsparameter erhält die Funktion die Nummern
des Ladeträgers und der Lokalität auf den der Ladeträger soeben bewegt wurde. Es
ist nun an der Datenbankfunktion zu entscheiden, ob eine exakte Übereinstimmung
oder ein anderes Regalfach des gleichen Regals o.ä. dem Anspruch genügt, den
Fahrauftrag als beendet zu kennzeichnen.
Eine Vorlage für diese Funktion finden Sie unter dem
Namen „AMIC_DEMO_ErledigeLVSFahrauftrag“.
Der Rückgabewert der Datenbankfunktion ist 1, wenn die
Bewegung gültig ist. Dies sollte auch der Standard-Fall sein. Wird 0
zurückgegeben, so wird die eingegebene Bewegung nicht gespeichert!

---

## Rechnungstrennung durch LKW (Anhänger)(SPA 95)

Rechnungstrennung durch LKW (Anhänger)(SPA 95)
Trennen: sind mehrere Lieferscheine mit verschiedenen
LKW (Anhänger) markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jeden LKW (Anhänger) eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen LKW
(Anhänger) markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erstellt und die Warenbewegungen werden dem LKW (Anhänger)
der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen LKW
(Anhänger) markiert und man will diese in eine Sammelrechnung umwandeln, so wird
eine Sammelrechnung erzeugt und die Warenbewegungen werden den LKW (Anhänger)
der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Fahrernummer(SPA 96)

Rechnungstrennung durch Fahrernummer(SPA 96)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Fahrernummern markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Fahrernummer eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Fahrernummern markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Fahrernummer der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Fahrernummern markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Fahrernummern der Lieferscheine zugeordnet.

---

## Quellbelegreaktivierung bei Stornieren/Löschen von Warebelegen (BA,AG,BS,AU,LI,RE) (SPA 987)

Quellbelegreaktivierung bei Stornieren/Löschen von
Warebelegen (BA,AG,BS,AU,LI,RE) (SPA 987)
Mit den Einstellungen
Nein
,
im Verkauf
,
im Einkauf
bzw.
im Einkauf und Verkauf
regelt dieser
Steuerparameter die Reaktivierung von Quellbelegen des zu löschenden Vorgangs
bei Durchführung der Funktion
Stornieren
für Vorgänge des
Warenwirtschaftssystems, die keine Rohwarevorgänge sind. Bei entsprechender
Einstellung werden die Vorgänge, aus denen der stornierte Vorgang per Umwandlung
hervorgegangen ist, wieder in den bearbeitbaren Zustand zurückgesetzt und
gegebenenfalls durch den Mandantenserver wieder in das Warenwirtschaftssystem
gebucht. Somit erscheint zum Beispiel ein Lieferschein nach Löschen der
zugehörigen Rechnung durch die Funktion
Stornieren
wieder im
Warenbuch und kann korrigiert und erneut zur Rechnung umgewandelt
werden.
Auch das Löschen von Gutschriften, die aus Rechnungen per Umwandlung
entstanden sind und mittels des Steuerparameters
[SPA]
Gutschrift aus Rechnung wie Stornorechnung (SPA348)
die
Rechnung gegen Weiterverarbeitung sperren, löst dann die Reaktivierung der
Rechnung aus.
Grundsätzlich können nur Bestellanfragen, Angebote,
Bestellungen, Aufträge, Lieferscheine und Rechnungen reaktiviert werden.

---

## openTRANS Parties EK/VK korrekt trennen (SPA 990)

openTRANS Parties EK/VK korrekt trennen (SPA 990)
Im openTRANS-Export von Einkaufs-Vorgängen gab es
Ausgaben der Wirtschaftsbeteiligten (PARTIES), die aus Sicht des Verkaufs
abgebildet wurden. So wurde z.B. der Lieferant als Rechnungsempfänger angegeben.
Um dies zu korrigieren, hat man sich in der
Vergangenheit zum Teil Kundenumschlüsselungsprozeduren bedient. Um diese
kompatiblen weiter bedienen zu können wurde der Steuerparameter 990 -
„openTRANS Parties EK/VK korrekt trennen“ erstellt.
Wird dieser aktiviert, so werden die Beteiligten
korrekt exportiert. Bei Neuinstallationen oder bestehenden Installationen, die
bisher die Beteiligten noch nicht nutzen, ist dieser Steuerparameter dringend zu
empfehlen.

---

## Ladeschein zu Lieferschein/Rechnung trennt nach Ursprungsbeleg (SPA 991)

Ladeschein zu Lieferschein/Rechnung trennt nach Ursprungsbeleg (SPA
991)
Der Steuerparameter gibt an, ob bei der Umwandlung von
Ladeschein zu Lieferschein oder Rechnung die Belege trotz der gebotenen
Zusammenfassung zu einem Sammelbeleg pro Lieferschein/Rechnung dennoch nach
Ursprungsbeleg getrennt werden soll.
Dies kann nützlich sein, wenn der Ladeschein als
Speditionspapier oder Dispositionsklammer für verschiedene Aufträge eines Kunden
genutzt wird, dieser jedoch für jede seiner Bestellungen eine separate
Rechnung/einen separaten Lieferschein wünscht.

---

## Streckenverwaltung

Streckenverwaltung

---

## Zu-/Abschlagklasse

Zu-/Abschlagklasse
Preise / Konditionen
Zu-/Abschläge
Zu-/Abschlagklassen
Oder Direktsprung
[ZABK]
Kunden/Lieferanten können eine Zu-/Abschlagklasse
und/oder eine individuelle Zu-/Abschlagklasse sowohl im Einkauf als auch im
Verkauf zugeordnet bekommen. Diese beschreiben jeweils die Zugehörigkeit zu
einer Gruppe von Kunden/Lieferanten, die alle für Artikel mit einer dort
zugeordneten Zu-/Abschlaggruppe beziehungsweise individuellen Zu-/Abschlaggruppe
einen oder mehrere zu der Gruppen-Klassen-Kombination festgelegten Zu- und
Abschläge bekommen.
Zu-/Abschlagklassen werden für Einkauf und Verkauf
getrennt angelegt. Sie werden im Kundenstamm auf der Registerkarte Klassen
zugeordnet. Dabei kann eine Zu-/Abschlagklasse sowohl als normale wie auch als
individuelle Zu-/Abschlagklasse verwendet werden.
Wenn eine neue Zu-/Abschlagklasse manuell angelegt
oder automatisch generiert wird, wird eine eindeutige Identnummer aus dem
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
Zu-/Abschlag-Zuordnungen für Kunden/Lieferanten erfasst werden, denen noch keine
individuelle Zu-/Abschlagklasse im Verkauf beziehungsweise Einkauf zugeordnet
wurde. In diesem Fall wird eine neue Zu-/Abschlagklasse erzeugt und automatisch
zugeordnet.

---

## Zu-/Abschlaggruppe

Zu-/Abschlaggruppe
Preise / Konditionen
Zu-/Abschläge
Zu-/Abschlaggruppe
Oder Direktsprung
[ZAGR]
Artikel können eine Zu-/Abschlaggruppe und/oder eine
individuelle Zu-/Abschlaggruppe sowohl im Einkauf als auch im Verkauf zugeordnet
bekommen. Diese beschreibt jeweils die Zugehörigkeit zu einer Gruppe von
Artikeln, die alle für Kunden und Lieferanten mit einer dort zugeordneten
Zu-/Abschlagklasse beziehungsweise individuellen Zu-/Abschlagklasse einen oder
mehrere zu der Gruppen-Klassen-Kombination festgelegten Zu- und Abschläge
bekommen.
Zu-/Abschlaggruppen werden für Einkauf und Verkauf
separat eingerichtet. Sie werden im Artikelpfleger mit der Funktion
Gruppenzuordnungen
zugeordnet. Dabei kann eine Zu-/Abschlaggruppe sowohl
als normale wie auch als individuelle Zu-/Abschlaggruppe verwendet werden.
Im Pflegemodul
individuelle Preise/Rabatte
im Verkauf
[PRI]
und Einkauf
[PRIE]
können auch individuelle
Zu-/Abschlagzuordnungen für Artikel erfasst werden, denen noch keine
individuelle Zu-/Abschlaggruppe im Verkauf beziehungsweise Einkauf zugeordnet
wurde. In diesem Fall wird eine neue Zu-/Abschlaggruppe erzeugt und automatisch
zugeordnet.

---

## Hinweis Auswahlliste

Hinweis Auswahlliste
Die
Auswahllisten
wird in einem neuen Design
angeboten. Die Vorgehensweise auf dem Selektionsbildschirm hat sich jedoch nicht
geändert und entspricht dem Windows-Standard.
Eine Zeile wird markiert mit der Maus oder der
RETURN-
Taste
Erneutes anklicken einer markierten Zeile hebt die
Markierung auf
Markierte Zeilen werden farblich gekennzeichnet.
Mehrfachmarkierungen können durch Drücken der
STRG-
Taste
für selektives markieren
SHIFT-
Taste
für blockweises markieren erreicht werden
Der Rollbalken vertikal zeigt jetzt die gesamte
gelesene Datenmenge an.
Es werden immer alle Daten in den Darstellungsbereich
geladen.
Doppelklick auf einem Datensatz löst die
Standardfunktion (meistens
Ändern
)
aus.
Die Doppelklickfunktion kann privatisiert werden.
Es kann nur noch mit der Stapelfunktion ein
übergreifendes Markieren realisiert werden.
Markieren und Entmarkieren ALLER Datensätze kann mit
STRG+A
vorgenommen werden.

---

## Anlegen einer Partie über die Vorgangserfassung

Anlegen einer Partie über die Vorgangserfassung
Am Beispiel „erfassen Lieferscheine“ wird im Folgenden
beschrieben, wie ein Partiestamm in der Vorgangserfassung angelegt wird. Diese
Funktion steht im Einkauf, Verkauf sowie in Umbuchung zur Verfügung.
Steuerungsparameter
[SPA]
erlauben
diese Neuanlage in der Vorgangserfassung (siehe
Steuerungsparameter [SPA]
Partieverwaltung
)
Aufruf z.B. mit:
Hauptauswahlmenü
Wareneinkauf
Eingangslieferschein
Eingangslieferschein erfassen
oder Direktsprung
[ELE]
Wenn mit
Positionsteil
F5
und dann
Artikel
F4
die Erfassung einer Artikelposition
gewechselt wird, steht (bei entsprechender SPA-Einstellung (20,21)) die Funktion
Partieauswahl
CF7
zur Verfügung.
Über diese Funktion können bestehende Partien dieser
Position zugeordnet (F3) und neue Partien angelegt (F8) werden. Dieses
Partieauswahlgitter zeigt sich automatisch auf der Maske, wenn für den in der
Position erfassten Artikel bereits Partien existieren. Somit wird der Benutzer
automatisch darauf hingewiesen, dieser Position Partien zuzuordnen (Einkauf
sowie auch Verkauf).
Über die Funktion
neue Partie F8
wird ein neuer Partiestamm
angelegt. Es öffnet sich die Partiestammdatenmaske. Für die Erläuterung der
Felder siehe
Anlegen einer
Partie über die Partiestammdatenverwaltung.
Nachdem die notwendigen Eingaben
erfolgt sind, kann diese Partie mit
Speichern
F9
abgespeichert werden.
Der Artikel mit dem erfassten Lieferscheingewicht wird
dieser Partie automatisch zugeordnet.
Diese Vorgehensweise der Partieanlage steht für
Lieferscheine und Rechnungen im Einkauf sowie im Verkauf zur Verfügung.

---

## Personendaten

Personendaten
An dieser Stelle werden für den Fall, dass diese
Anschrift eine Person (z.B. einen Ansprechpartner) identifiziert die Möglichkeit
angeboten personenbezogene Daten für die
Verbotslistenprüfung
zu hinterlegen.
Feld
Beschreibung
IN-Number
Sozialversicherungsnummer
Nationalität
Nationalität
Geburtsort
Geburtsort
Geburtsland
Geburtsland
Reisepassdaten
Reisepassdaten (Nummer,
      Ausstellungsdatum und -Ort)

---

## Anwendung Formulararchiv

Anwendung Formulararchiv
Hauptmenü
Warenverkauf
Archiv
Archiv
Hauptmenü
Wareneinkauf
Archiv
Archiv
Hauptmenü
Büro und Internet
Büroumgebung
Archiv
Hauptmenü
CRM
Archiv
Archiv
Direktsprung
[FA]
Hier findet sich die einzige Variante
„Formulararchiv“.
Im Gegensatz zu
Formulararchiv-Administration
handelt es
sich bei dieser Variante um die mehr anwenderorientierte Präsentation des
Formulararchivs.
Felder
KndNr.
Zuordnung des Beleges zu einer
      Kundennummer.
Die
      Versorgung der Kundennummer erfolgt je nach Ursprung des Beleges durch das
      System bzw. den Anwender.
Dabei können je nach Zulieferung
      (Druck, Import, Manuell, sonstige Programmteile, Fremdsoftware) eine 0
      bzw. eine datentechnische NULL ins System eingestellt werden.
Die KndNr. wird nicht länger durch
      fa_kundennummer (char 10) abgebildet, sondern intern durch fa_kundnummer
      (int).
Fa_kundnummer kann technisch die -1
      annehmen im Sinne von „Dokument hat keine Kundenzuordnung“. Dieses wird
      sowohl in den Auswahllisten als auch in Strg-F12 „Archiv anzeigen“ als
      Null dargestellt.
Somit ist es nun möglich in Strg-F12
      bei der Spalteneingrenzung nach „null“ zu selektieren, die Auswahllisten
      haben eine Extra-Möglichkeit bekommen nach Dokumenten zu suchen denen
      keine Kundennummer zugeordnet ist.
Klassifizierung
Vom
      Anwender vorgegebene Klassifizierung des Beleges.
Beleg-Typ
Beleg-Typ
Beleg-Nr
Beleg-Nummer
Beleg-Datum
Beleg-Datum
Archiv/Druck-Datum
Zeitpunkt der Einstellung ins
      Archiv
Beleg-Referenz
Die
      Referenz die zusammengehörige Archiv-Einträge ausweist.
Herkunft
Ursprung des Beleges
Anleger
Der
      Kurzname des Anlegers des Archiv-Eintrages.
Beleg-Klasse
Vom
      System oder dem Anwender vorgegebene Typisierung des Beleges.
Inhalt
Technische Qualifizierung des
      Inhalts über den Mimetyp des Beleges
Mnd
Mandant
Autor, Betreff, Titel, Kommentar,
      Stichwörter
Unterstützende Felder zwecks
      Kat
[...]


---

## Archiv Import

Archiv Import
Zusätzlich zur internen Belegerzeugung durch den Druck
von Warenwirtschaftsvorgängen und –auswertungen gibt es immer wieder
verschiedenste Dokumente, die ins Referenz-ERP-Formulararchiv integriert sein
wollen:
•
Kunden-Korrespondenz
•
Email
•
Eingangslieferscheine – und Rechnungen
•
und weitere mehr
Sie profitieren dann von den vielfältigen
Recherche-Möglichkeiten und stehen immer zur Ansicht und weiteren Verarbeitung
bereit.
Der Mandantenserver ist in der Lage,
Archiv-Import-Profile abzuarbeiten.
Es hat eine Änderung im Verhalten der „Trefferauswahl“
gegeben. Bisher war es so, dass nicht „passende“ Dateien als irgend gearteter
Fehler angesehen worden. Das ist nun nicht mehr so. Dieses Verhalten birgt nun
den großen Vorteil, dass man einen Pfad zur Einstellung von Daten verschiedener
Herkunft verwenden kann.

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

## Aufträge zusammenführen

Aufträge zusammenführen
Hauptmenü
Warenverkauf
Auftrag
Auftragsbearbeitung
oder Direktsprung
[AUB]
Die Freischaltung dieser Spezialfunktion unterliegt
dem
Steuerparameter „723 – Aufträge
zusammenführen erlauben?“
.
Mit dieser Spezialfunktion lassen sich ausgewählte
Aufträge in denen Kunden mehrfach gleiche Artikel mit unterschiedlichen Mengen
erstellt haben (nach Artikelnummern) zusammenfassen. Hierbei werden folgende
Kriterien berücksichtigt:
•
Kunde
•
Artikel
•
Lager und Lagerplatz
•
Versandadresse
•
Rechnungsempfänger
•
Plan-/Lieferdatum
So werden Aufträge, in denen der gleiche Kunde den
gleichen Artikel bestellt, aber beispielsweise unterschiedliche Läger verwendet
zusammengefasst. Aufträge in denen der gleiche Kunde den gleichen Artikel unter
Angabe verschiedener Plan-/Lieferdaten aufgibt werden zusammengefasst und zum
spätesten Datum zur Lieferung geplant.
Zusammengefasste Aufträge werden auf unterschiedliche
Arten behandelt. So ist es nicht immer notwendig Aufträge neu zu erstellen
sondern nur zu ändern. Weiterhin kann über einen Einrichtungsparameter
entschieden werden, ob die Originalaufträge storniert oder in
Auftrags-Storno-Belege umgewandelt werden sollen.
Der Aufbau gliedert sich wie folgt und wird
anschließend beschrieben:
Im oberen Teil wird das Abgangslager bestimmt. Weiter
rechts befinden sich die einzelnen Funktionen, über die die Anwendung gesteuert
wird.
Anschließend folgen die Reiter „Aufträge“,
„Artikelübersicht“ und „Zusammengeführt“.
Das Abgangslager legt fest, aus welchem Lager die
bestellten Artikel kommen sollen. Die Nummer des Lagers wird angegeben und
bestätigt. Anschließend kann der Name des Lagers hinter der Nummer zur Prüfung
eingesehen werden.
Die Funktionen in der Übersicht:
•
Starten
F9
startet den Vorgang der Zusammenführung
der ausgewählten Vorgänge
•
Einrichtungsparameter
(folg)
•
Dieses Menü
– wird unter
diesem
Link
genauer
beschrieben
Auf dem Reiter „Aufträge“ ist eine Übersicht der
ausgewählten Aufträg
[...]


---

## Auftrag-Restmengenkorrektur

Auftrag-Restmengenkorrektur
Hauptmenü
Warenverkauf
Auftrag
Auftrag: Mengenkorrektur
Oder Direktsprung
[AUK]
Mit der Auftrag-Restmengenkorrektur können in
Aufträgen und Bestellungen die Restmengen und das Plandatum bearbeitet
werden.
Aufgrund von technischen Einschränkungen kann diese
Korrektur jedoch nicht mit Aufträgen und Bestellungen durchgeführt werden, wenn
eine Position, die aus einer Stückliste stammt, eine Gebinde-Mengeneinheit
verwendet.

---

## Ausbuchen Fremdware/-lager SF5

Ausbuchen Fremdware/-lager
SF5
Diese Funktion im Kontraktstamm
[KTR]
macht es möglich, Verkaufskontrakte
Fremdware oder Einkaufskontrakte Fremdlager, die genau einen Kontraktartikel
beinhalten, auszubuchen.
Dafür müssen zuerst alle Kontrakte, die ausgebucht
werden sollen, in der Auswahlliste markiert werden. Nach Aufruf der Funktion
Ausbuchen Fremdware/-lager
SF5
öffnet sich eine Maske, in die alle
markierten Fremdware/-lager Kontrakte übernommen werden. Kontrakte, die nicht
ausgebucht werden können, werden im unteren Teil der Maske gesondert in einem
Grid ausgewiesen. Anschließend wird für jeden gültigen Kontrakt der
Ausbuchungspreis ermittelt. Die Art der Preisermittlung ist auf der Maske
einstellbar, die Vorbelegung erfolgt aus den Einrichterparametern. Folgende
Preisvorbelegungen sind möglich:
Ohne Preis
Der Preis wird auf 0 gesetzt
Vom Beleg
Der Ausbuchungspreis wird mit dem Preis aus dem
zugehörigen Voreinkauf / Vorverkauf vorbelegt.
Aus Preisliste
Bei dieser Variante ist es notwendig in den
Einrichterparametern eine Preislistennummer zu hinterlegen. Diese Preisliste
wird dann zur Preisermittlung aus artikelspezifischen Preisen herangezogen.
Die ermittelten Preise können manuell geändert werden.
Ferner stehen zwei Funktionen zur Verfügung, mit denen alle Preise oder der
Preis der aktiven Zeile neu ermittelt werden können. Dabei wird jeweils der
aktuelle Stand in ‚Art der Preisermittlung‘ ausgewertet.
Für Kontrollzwecke steht eine Belegvorschau zur
Verfügung, die den zugehörigen Beleg der aktiven Zeile präsentiert.
Das Ausbuchen erfolgt dann anschließend durch
den Aufruf der Funktion
Start
Ausbuchen
F9
. Dabei wird für
jeden einzelnen Kontrakt eine Rechnung mit entsprechender Vorgangsklasse und
einer Positionszeilen erzeugt. Die Unterklasse wird über die Steuerparameter 601
(Unterklasse für Fremdlager ausbuchen) und 602 (Unterklasse für Fremdware
ausbuchen) aus der Parametergruppe Kontraktwesen festgelegt.
Das mit dem
aktuellen Tagesdatu
[...]


---

## Auswahl einer Griddefinition

Auswahl einer Griddefinition
Wählen Sie eine bestehende Griddefinition aus der
Liste aus. Sie können nach dem Namen in der Liste suchen, indem Sie die
Filterfunktion benutzen und mit den in Referenz-ERP üblichen Suchkriterien den Namen
eingeben (z.B. ‚Auftrag%‘ für alle Definitionen, die mit ‚Auftrag‘ beginnen).

---

## Bearbeitung von Kassenbelegen

Bearbeitung von Kassenbelegen
In der AW Gesamtbarverkauf unter
Warenwirtschaftssystem/Barvorgänge gibt es die Möglichkeit, Kassenbelege
nachträglich zu bearbeiten:
Dabei besteht die Möglichkeit des Stornierens und
Druckens von Belegen für Finanz- und Kassenvorgängen. Während der Druck
grundsätzlich möglich ist, muss an dem Arbeitsplatz, an dem storniert werden
soll, die zugehörige Kasse eröffnet sein. Kassenstürze sind dabei nicht
stornierbar (nur wiederholt druckbar).
Die Bearbeitung ist in der Variante Belegüberblick
möglich.
1. Drucken:
Hier kann der Kassenbeleg nochmals gedruckt werden in
der Form wie auch schon während der "Echterfassung". Um ein solches Formular auf
den Schacht zu drucken, muss auf dieser Maske der EPA "Sollen Formulare auf den
Schacht gedruckt werden" auf Ja gesetzt sein. Dann wird auch auf die
eingerichteten Formulare 51-54 zurückgegriffen.
2. Stornieren:
Ein Beleg kann nur einmal storniert werden, eine
Stornierung ist nicht mehr rückgängig zu machen.
a) Der Beleg erhält ein Stornokennzeichen.
b) Es wird ein Stornobeleg gedruckt, wobei
EPA-abhängig auf die Formulare 51-54 zurückgegriffen wird. In diesen Formularen
ist an entsprechender Position im Kopfteil die TextVariable Storno zu
hinterlegen, in der
nur
bei Stornobelegen der Text "Storno-" gedruckt
wird.
c) Es werden die Stornobeträge je nach Belegart in
Storno-Feldern der Relation AcashBelgKsiz verwaltet bzgl. der Kasse/Sitzung, die
diesen Stornovorgang auslöst (nicht auf die Kasse/Sitzung, die den Urbeleg
erzeugt hat!!!). Diese Beträge werden in den entsprechenden Varianten im
Gesamtbarverkauf unter den "Sto"-Feldern angezeigt.
d) Mit der Stornierung ist eine
Barauszahlung/Bareinzahlung verbunden, diese wird auf die Soll/Umsätze der Kasse
angerechnet, die die Stornierung durchführt.
e) Wenn der SPA 50 "Aut. Buchung von Kassenvorg. in
FiBu" gesetzt ist, wird zusätzlich eine Gegenbuchung zur Buchung erzeugt, die
automatisch beim ursprünglichen Finanzvorgang erzeugt
[...]


---

## Belegdatum ändern

Belegdatum ändern
Hauptmenü
Warenverkauf
Rechnung
Rechnungsbearbeitung
oder Direktsprung
[REB]
Hauptmenü
Wareneinkauf
Eingangsrechnung
Eingangsrechnungen bearbeiten
oder Direktsprung
[ERB]
Mithilfe dieser Funktion ist es möglich das Beleg- und
Lieferdatum von Eingangs- und Ausgangsrechnungen nachträglich zu ändern.
Dies ist nur möglich, wenn die Rechnung nicht durch
eine Umwandlung entstanden ist.
Ebenso zu beachten ist, dass beim Ändern des Datums
Preise, Rabatte, Pariezuordnungen, Kontraktzuordnungen nicht neu bestimmt
werden. Es wird lediglich eine zusätzliche Abfrage ausgegeben.

---

## Überwachung des Kreditlimits

Überwachung des Kreditlimits
Innerhalb der Vorgangserfassung erfolgt die
Überprüfung der Limitüberschreitung sowohl vor als auch nach der
Warenpositionserfassung. Voraussetzung ist, dass in den Steuerparametern 233
„Kreditlimit-Prüfung“
und 234
„Kreditlimit-Prüfung  mit
Auftrag/Bestellg“
die Überwachung aktiviert wurde.
Gegen das eingetragene Limit wird der OP-Bestand
zuzüglich nicht verbuchter Lieferscheine und Rechnungen verprobt. Mittels SPA
234 kann auch der Auftragsbestand mit einbezogen werden. Wird das Kreditlimit
überschritten, erfolgt
Eine Warnung
Eine Speicherung aber Sperre des Belegs
Eine Abweisung des Belegs
Die Überwachung erfolgt nicht im Ansehen-Fall
(F6).

---

## Scanncodes für die Bestellung

Scanncodes für die Bestellung
Bestellung
Start
BSE
Bestellung Ende
BSE
Storno
ILN Nummer
Beispiel

---

## Aufträge (Kommissionierung / Retoure )

Aufträge (Kommissionierung /
Retoure )
Vorgangsfunktions Übersicht
Kommissionierung Start
Daten einscannen
Kommissionierung Ende
Besonderheiten des Aufträge welcher mit einem
Scanner bearbeitet werden soll.
In einem Auftrag welcher mit einem Scanner bearbeitet
wird, darf es keine Partieverteilung geben. Dies bedeutet, wenn ein Artikel
mehrere Partien in dem Auftrag, muss für jede Artikel/Partie Kombination eine
eigene Warenposition angelegt werden.
Erstellen eines Branchen-ERP Etikettendruck Dokuments
für den Auftrag
Um eine Kommissionierung mit dem Scanner
durchzuführen, kann in der ersten Variante der Auftragsbearbeitung ein Branchen-ERP
Etikettendruck Dokument ausgedruckt und bearbeitet werden, welches die
benötigten Scancodes und eine Liste der Artikel enthält.
Auf dem Report befinden sich drei feste EAN 128 Codes.
Es existiert eine Vorlage für den Branchen-ERP Etikettendruck (Scanner
Auftragsbearbeitung) wenn diese Vorlage in die privaten Branchen-ERP Etikettendruck
Dokumente übernommen werden soll, so muss die Branchen-ERP Etikettendruck Dokumente ID
gleich bleiben, da ansonsten das Branchen-ERP Etikettendruck Dokument nicht aufgerufen
werden kann.
Die benötigten Scancodes
•
Der erste mit der Auftragsnummer ist der Start Code
•
Mit dem Scan Code „STORNO“ kann die zuletzt gescannte Position gelöscht
werden.
•
Mit „AUENDE“ wird die Auftragsbearbeitung abgeschlossen.
Ablauf
•
Als erstes wird der Startscancode erfasst wie z.B. AU 55. Beim
Startscancode muss immer zwischen dem AU und der Vorgangsnummer ein Leerzeichen
stehen. Nach dem der Startscancode erfasst worden ist, werden im unteren Teil
des Scanner Bildschirmes alle Position des Auftrags angezeigt. Enthält der
Auftrag mehr als neun Positionen so kann mit den Pfeil hoch und runter Tasten
geblättert werden.
•
Jetzt kann eine Position aus dem Auftrag eingescannt werden. Die Suche,
der Position im Auftrag funktioniert so. Wird nur der Artikel erfasst, so wird
der erste Artikel mit dem erfassten EAN Code genommen, dies bedeute, dass wen
[...]


---

## Beispiel Scancodes

Beispiel Scancodes
Hier finden Sie Beispiel Scancodes für die
Implementierten Funktionen.
Scancode für einen Auftrag(Kommissionierung)
Scancode für einen Eingangslieferschein
Scancode für die Inventur

---

## Eingangslieferscheine \ Bestellung \Lieferschein erfassen

Eingangslieferscheine \
Bestellung \Lieferschein erfassen
Vorgangsfunktion Übersicht
Eingang Start
Kundenauswahl
Daten einscannen
Eingang Ende
Erstellen eines neuen Beleges.
•
Als erstes wird der Start Scan Code EL der im EAN 128 verschlüsselt ist
eingescannt.
•
Danach kann entweder über die Kundensuchmaske auf dem Scanner oder das
Einscannen des ILN Codes der Kunde bestimmt werden. Die Kunden ILN muss im
Kundenstamm dafür richtig hinterlegt sein. Die ILN kann auch in der NVE
verschlüsselt sein z.B. (0034006900000010048). Wichtig dabei ist nur, dass nach
der 00 eine 3 folgt. Wenn der Kunde richtig erkannt worden ist, so steht dieser
in der zweiten Zeile des Scanners.
•
Jetzt kann der Artikel oder die Partie oder  das MHD oder Lagerplatz
eingescannt werden. Der Artikel kann im EAN 8, EAN13, UPCA, UPCE, oder  im
EAN 128 Code als AI 01 verschlüsselt werden. Die Partie wird mit dem AI-Code 10
verschlüsselt, das MHD wird mit dem AI-Code 15 und der Lagerplatz wird mit dem
AI-Code 97 des EAN 128 Codes verschlüsselt.
•
Dann kann die Menge eingegeben oder eingescannt werden. Die AI sind -30
für Handeingabe und 30, 37, 3100, 3101, 3102 … für die eingescannten Mengen
•
Als letztes wird ELENDE der im EAN 128 verschlüsselt ist eingescannt.
Gruppenzuordnung in der AI-Liste
•
Der Artikel hat immer die Gruppennummer 1
•
Die Menge hat immer die Gruppennummer 2
•
Die Partie hat immer die Gruppennummer 3
•
Das MHD hat die Gruppennummer 4
•
Für den Lagerplatz und das Speichern von Feldern im AO eine beliebige
Gruppe verwendet werden.
Preise
Damit die Preise gezogen werden muss im Kundenstamm
eine Preisklasse eingerichtet werden im Artikel muss die richtige Preismatrix
hinterlegt werden, die die Preisklasse des Kunden enthält.
Partie
Wird eine Partiebezeichnung mit dem AI-Code 10 erfasst
und diese existiert noch nicht, dann wird einen neue Partie mit dieser
Bezeichnung angelegt.
Gebinde

---

## Aufträge (Teildisponierung, Strecke)

Aufträge (Teildisponierung, Strecke)
Vorgangsfunktions
      Übersicht
Starten der
      Teildisponierung
Daten einscannen
Beenden der
      Teildisponierung
Erklärung der
    Kopfzeilen
Die
      erste Zeile im Kopftext zeigt die Auftragsnummer an.
Die
      zweite Zeile im Kopftext zeigt die Artikelstammbezeichnung an.
Die
      dritte Zeile im Kopftext zeigt die benötigte Gesamtmenge und die
      eingegebene Menge an.
Diese Funktion erlaubt mehrere Aufträge, die zu einem
Kunden gehören zu klammern und als einen Auftrag abzuarbeiten. Es können auch
einzelne Positionen aus verschiedenen Aufträgen zu einer Klammer
zusammengefasst  werden. Dieser Auftrag kann dann über den Online Scanner
abgearbeitet werden. Nach erfolgreicher Bearbeitung erstellt der Mandanten
Server einen Lieferschein aus dem geklammerten Auftrag.
Es sind aber noch ein paar Einstellungen im Aeins
vorzunehmen. Unter [FRZ] kann für die Klasse und die Unterklasse eingestellt
werden, ob die Klammernummer gleich der Belegnummer ist. Wird diese nicht
angegeben, so erhält die Klammernummer den Default Wert von 0. Um einen Auftrag
oder Positionen eines Auftrages Klammernummer zuzuordnen, gehen Sie bitte unter
[AUB] in die Variante „Aufträge mit Position“. Unter dem Direktsprung [Forma]
muss das Format af_klstatus gefüllt werden. Es gibt bislang 7 unterschiedliche
Status.
Status
Wann
1
Wenn
      der Auftrag neu erfasst worden ist.
2
Nach
      der Zuweisung der Klammernummer
3
In
      Bearbeitung
4
Wenn
      die Auftragsabarbeitung auf einen Fehler gelaufen ist.
5
Wenn
      der Lieferschein in Erstellung ist
6
Wenn
      der Lieferschein automatisch gedruckt wurde
7
Wenn
      der Lieferschein unterschrieben im Formular Archiv liegt
Die unterschiedlichen Werte des Status werden farblich
in der Auswahlliste dargestellt.
Hier können einzelne Positionen einer oder mehrerer
Aufträge ausgewählt werden. Dann klicken Sie auf „Streckennummer zuordnen“.
Jetzt öffnet sich die Pflege
[...]


---

## Druckbare Positionen der Formulareinrichtung

Druckbare Positionen der Formulareinrichtung
Format Typ
Typ Bezeichnung
Bereich
Feld Nr.
Feld Bezeichnung
1+3
1
      Standard Vorgang
101
      Warenpositionszeile
1886
Gesamt-Restmenge-Einkauf
1+3
3
      int. Warenbeleg
101
      Warenpositionszeile
1885
Gesamt-Restmenge-Verkauf
1+3
101
      Warenpositionszeile
1888
Gesamt-Restwert-Einkauf
1+3
101
      Warenpositionszeile
1887
Gesamt-Restwert-Verkauf
1+3
101
      Warenpositionszeile
1472
Identifikation
1+3
101
      Warenpositionszeile
1485
Restmenge-Einkauf
1+3
101
      Warenpositionszeile
1484
Restmenge-Verkauf
1+3
101
      Warenpositionszeile
1483
Restwert-Einkauf
1+3
101
      Warenpositionszeile
1482
Restwert-Verkauf
1+3
101
      Warenpositionszeile
1489
Sollmenge-Einkauf
1+3
101
      Warenpositionszeile
1488
Sollmenge-Verkauf
1+3
101
      Warenpositionszeile
1487
Sollwert-Einkauf
1+3
101
      Warenpositionszeile
1486
Sollwert-Verkauf
1+3
101
      (WPZ) +109 (WPZ Bildsch.)
1474
Partiebezeichnung
1+3
101
      (WPZ) +109 (WPZ Bildsch.)
1898
Partiegruppennummer
1+3
101
      (WPZ) +109 (WPZ Bildsch.)
1473
Partienummer

---

## Dynamisches Informationssystem (Artikel)

Dynamisches Informationssystem (Artikel)
Ein dynamisches Informationssystem kann folgende
Informationen enthalten:
•
Daten, die direkt aus dem operativen System gelesen werden (VK-Umsatz,
EK-Umsatz, Auftragsbestand, Bestand)
•
Daten, die im Artikelinformationssystem erfasst werden: Lieferzeit,
Einsatz­men­gen, etc.
•
Beschreibende Texte, wie Verwendungszweck, etc.
Nachfolgend wird die Einrichtung dieser Informationen
beschrieben.
Beispiel:
Einrichtung von Abfragefeldern
Auf der KUI - Seite 1003
Wird der Kui Typ Abfragefeld bestimmt
Die Darstellung erfolgt ganzzahlig
Das in Zeile 1, Spalte 15 mit der Länge 10 angezeigt
wird
In der Relation "ArtikelMaskeDaten" ist dies das Feld
"wbz"
Die Bezeichnung in der Erfassungsmaske ist
"Wiederbeschaffung:"
Die Darstellung erfolgt dann folgendermaßen:

---

## Einrichtung als Notizblatt (Artikel)

Einrichtung als Notizblatt (Artikel)
Mit Aufruf wird immer die erste Seite angeboten.
F8
ermöglicht die Einrichtung einer neuen
Seite. Nach Vergabe einer Seitennummer (im Artikelinformationssystem sind es die
Seiten 1000-1999) wird dieser Seite ein Name vergeben und die somit
eingerichtete Seite mit
F9
gespeichert. Manuelle Einträge können jetzt direkt in das Textfeld eingetragen
werden. Eleganter jedoch ist der Aufruf des Texteditors, da hier einfache
Textbearbeitungsmöglichkeiten angeboten werden. In der Ansicht erhält man z.B.
folgende Darstellung:

---

## Erfassung Stückliste

Erfassung Stückliste
Für die Erfassung einer Stücklistenauflösung innerhalb
eines Verkaufsbeleges müssen folgende Bedingungen vorliegen:
•
Steuerparameter
•
Zum gezogenen Artikel muss eine
Rezepturgruppe
mit
Rezeptur
vorliegen
•
In der Rezeptur muss die Verwendung Stückliste zugelassen sein.
Die Ziehung der Stückliste erfolgt dann automatisch,
falls mehrere gültige Stücklisten vorhanden sind, öffnet sich ein
Auswahlbildschirm.
Es werden während der Erfassung dargestellt:
•
Produkt (Verkaufsartikel)
•
Produkt (Stücklistenergebnis)
•
Komponenten
Die Korrektur der Stücklistenauflösung erfolgt über
die Produktionsmenge und kann auch auf Ebene der Einzelkomponenten erfolgen, was
dann wiederum Einfluss auf das Produkt hat.

---

## Artikel

Artikel
Frage: Wie kann ich
während des Jahres Artikelbestände korrigieren?
Antwort:
Wenn während des Jahres Ware
auszubuchen ist, kann pro forma eine Einkaufs-Rechnung erfasst werden auf einen
fiktiven Lieferanten. Der entsprechende Artikel wird mit der zu korrigierenden
Menge mit negativem Vorzeichen und ohne Preis eingegeben. Es erfolgt kein
Fibu
-Übertrag!
Im Zuge der nächsten Inventur wird der Hilfsbeleg storniert.
Frage:
Wenn ich eine Rechnung kopiere und in dem Zuge die
Kundennummer ändern möchte, erscheint folgende Meldung: Es ist kein
Behandlungsschema eingerichtet …" Warum funktioniert die Änderung der
Kundennummer nicht?
Antwort:
Für die Kundenänderung im
direkten Zusammenhang mit der Umwandlung ist das Behandlungsschema fest zu
hinterlegen. Suchen Sie in der Formularzuordnung
[FRZ]
die
Vorgangsklasse 700 und die entsprechende Unterklasse und wählen Sie
Ändern (F5)
.
Auf dem Reiter ¨Abwicklung¨
tragen Sie dann unten im Block ¨Behandlungsschema¨ bei Kundenänderung über F3
ein Schema ein oder erstellen ein neues.
Weitere Hilfe:
-
Abwicklung
-
Behandlungsschema

---

## Felder der Maske

Felder der Maske
Felder
Kundennummer
      (Produktionsmaske)
Hier
      kann man als Information den Kunden hinterlegen für den man z.B. ein
      Produktionsangebot gemacht hat.
Buchungstyp
      (Produktionsmaske)
Buchungstyp
Bedeutung
Angebot Produktion
Diese Einstellung verwendet man, wenn man
            ein Produktionsangebot machen möchte.
Auftrag Produktion
Für die Produktionsplanung, Bestellungen
            und Aufträge.
Produktion
Um für die Produktion eine normale
            Bestandsbuchung durchzuführen.
Der
      Buchungstyp kann auch schon im Vorgangskopf im Userfeld „Prod.Buchtyp“
      (Nummer 4204) eingetragen werden.
Eine
      Vorbelegung für den Buchungstyp ist in den Optionen
[OPT]
unter dem Wert
      „VorbelegungBuchungsTypProduktion“ einstellbar.
Verwendung
Plan/Lieferdatum
Mit
      dem Plan/Lieferdatum kann das Lieferdatum (Ausführungsdatum) einer
      Produktion abweichend vom Vorgangsdatum bestimmt werden. Dieses kann auf
      der Startseite des Vorgangs angegeben werden, es dient dann allerdings nur
      zur Vorbelegung für neu erzeugte Produktionen. Wird dort zum Beispiel
      zunächst unbemerkt ein falsches Datum angegeben, so lässt es sich dieses
      nach Erfassung einer oder gar mehrerer Produktionen zwar vorgangsseitig
      ändern. Die bereits erfassten Produktionen behalten aber das ursprüngliche
      Datum bei. Daher lässt sich per Einrichterparameter
Plan-/Lieferdatum auf
      Produktionsmaske
das Maskenfeld
Plan/Lieferdatum
aktivieren. Hier kann, auch bei der Belegkorrektur, ein vom
      Vorgangstamm abweichendes Datum für die aktuelle Produktion angegeben
      werden.
Produktnummer
Hier
      wählt man den Artikel aus, den man produzieren will. Es werden alle
      Artikel in der
F3
-Auswahl
      angezeigt, die zu dem Lager gehören und eine Rezepturgruppe hinterlegt
      haben.
Lagerplatz
Hier
      kann man den Lagerplatz angeben
Rezeptur
Hier
      wählt man die Rezeptur an, die man
[...]


---

## Auswahllistenvariante Fibu Übertrag Rohware-Sammelbelege

Auswahllistenvariante Fibu Übertrag Rohware-Sammelbelege
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Rohware-Sammelbelege
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Rohware-Sammelbelege
Oder
Direktsprung
[FIB]
In dieser Variante werden
Rohware-Sammeldruck-Abrechnungen und Rohware-Sammeldruck-Stornoabrechnungen
dargestellt.
Aufgrund der notwendigen Trennkriterien für den Fibu-Übertrag
kann es vorkommen, das ein Sammeldruckbeleg hier für die Übertragung in mehrere
Teilbelege zergliedert wird (z.B. bei unterschiedlichem Valutadatum der
Einzelbelege).
Felder der Auswahlliste
Feld
Beschreibung
Kl.
Vorgangsklassenkürzel des
      Belegs
SBel.Datum
Druckdatum (Belegdatum) des
      Sammeldruckbelegs
Drucknr.
Sammeldrucknummer (Belegnummer) des
      Sammeldruckbelegs
Dru
--:  Beleg ist nicht gedruckt
Ja:  Beleg ist gedruckt
Fib
--:  Beleg ist noch
      nicht übertragen
i.B.: Übertragungsauftrag an Mandantenserver
      erteilt
Ja: Beleg ist an Fibu übertragen
NN: Beleg ist nicht
      übertragbar (z.B. Stornobeleg zu nicht übertragenem
      Originalbeleg)
Kontonr.
Kunden-/Lieferantennummer =
      Kontonummer
Kunde/Lieferant
Bezeichnung des
      Kunden/Lieferanten
Kontrakt
Hier
      wird eine Liste der Kontraktnummern aller Anlieferungspositionen der
      Einzelbelege des Sammeldruckbelegs dargestellt
Filiale
Nummer der Filiale des
      Sammeldruckbelegs
Status
Abrechnungsstufe:
Abschlag,
      F-Abschlag, Finale
Belege
Anzahl der zugehörigen
      Einzelabrechnungen
VFKtr.
Anzahl der beteiligten
      Vorverkaufs-/Voreinkaufs-Kontrakte
Währung
Währungsnummer zum
      Sammeldruckbeleg
Netto
Nettobetrag des
      Sammeldruckbelegs
Valuta
Valutadatum des
      Sammeldruckbelegs
StGrp.
Steuergruppe zum
      Sammeldruckbeleg
Jahr
Warenwirtschaftsjahr des
      Sammeldruckbelegs
Übertragungsdatum.
Datum des Fibu Übertrags
PeriodeFibu
Fibuperiode des Vorgangs
JahrFibu
Fibujahr des Vorgangs
[...]


---

## Auswahllistenvariante Fibu Übertrag mit Positionszeilen

Auswahllistenvariante Fibu Übertrag mit Positionszeilen
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag mit Positionszeilen
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag mit Positionszeilen
Oder
Direktsprung
[FIB]
In dieser Variante werden Rechnungen,
Stornorechnungen, Gutschriften, Stornogutschriften, Rohware-Einzelabrechnungen,
Rohware-Einzelstornoabrechnungen und Inventurbelege mit Waren-Positionszeilen
dargestellt
Felder der Auswahlliste
Feld
Beschreibung
Kontonr.
Kunden-/Lieferantennummer =
      Kontonummer
Kunde
Bezeichnung des
      Kunden/Lieferanten
Belegnr.
Nummer des Vorgangs
Typ
Vorgangsklassenkürzel des
      Belegs
Unterklasse
Nummer der
      Vorgangsunterklasse
Datum
Belegdatum
Dru
--:  Beleg ist nicht
      gedruckt
Ja:  Beleg ist gedruckt
Fib
--:  Beleg ist noch
      nicht übertragen
i.B.: Übertragungsauftrag an Mandantenserver
      erteilt
Ja: Beleg ist an Fibu übertragen
NN: Beleg ist nicht
      übertragbar (z.B. Stornobeleg zu nicht übertragenem
      Originalbeleg)
RAB
--:  Beleg ist noch
      nicht im Rechnungsaugangsbuch
i.B.: Übertragungsauftrag an
      Mandantenserver erteilt
Ja: Beleg ist im
      Rechnungsausgangsbuch
Verarb.
--:  Beleg ist nicht
      weiterverarbeitet
teilweise:  Beleg ist teildisponiert
ganz:
      Beleg ist weiterverarbeitet
Warenwert
Netto-Warenwert des
      Vorgangs
Netto.
Netto-Betrag des
      Vorgangs
Steuer
Steuer-Betrag des
      Vorgangs
Periode.
Warenwirtschaftsperiode des
      Vorgangs
Jahr
Warenwirtschaftsjahr des
      Vorgangs
Übertragungsdatum.
Datum des Fibu Übertrags
PeriodeFibu
Fibuperiode des Vorgangs
JahrFibu
Fibujahr des Vorgangs
Erstbediener
Erster Bediener
Zustimmungsbediener
Zweiter Bediener beim
      Vieraugenprinzip
Erfasser
Erfasser/Ersteller des
      Vorgangs
Bereichsauswahl
Filter
Beschreibung
Belegnummer
Selektion der Belege mit Belegnummer
      (von/bis)
Datum
Selektion der Belege mit Belegdatum

[...]


---

## Auswahllistenvariante Fibu Übertrag incl. Rohware

Auswahllistenvariante Fibu Übertrag incl. Rohware
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag incl. Rohware
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag incl. Rohware
Oder
Direktsprung
[FIB]
In dieser Variante werden Rechnungen,
Stornorechnungen, Gutschriften, Stornogutschriften, Rohware-Einzelabrechnungen,
Rohware-Einzelstornoabrechnungen und Inventurbelege ohne Produktion und
Umbuchungen dargestellt
Felder der Auswahlliste
Feld
Beschreibung
Kontonr.
Kunden-/Lieferantennummer =
      Kontonummer
Kunde
Bezeichnung des
      Kunden/Lieferanten
Belegnr.
Nummer des Vorgangs
Typ
Vorgangsklassenkürzel des
      Belegs
Unterklasse
Nummer der
      Vorgangsunterklasse
Datum
Belegdatum
Druckkennzeichen
--:  Beleg ist nicht
      gedruckt
Ja:  Beleg ist gedruckt
Fib
--:  Beleg ist noch
      nicht übertragen
i.B.: Übertragungsauftrag an Mandantenserver
      erteilt
Ja: Beleg ist an Fibu übertragen
NN: Beleg ist nicht
      übertragbar (z.B. Stornobeleg zu nicht übertragenem
      Originalbeleg)
RAB
--:  Beleg ist noch
      nicht im Rechnungsaugangsbuch
i.B.: Übertragungsauftrag an
      Mandantenserver erteilt
Ja: Beleg ist im
      Rechnungsausgangsbuch
Verarb.
--:  Beleg ist nicht
      weiterverarbeitet
teilweise:  Beleg ist teildisponiert
ganz:
      Beleg ist weiterverarbeitet
Warenwert
Netto-Warenwert des
      Vorgangs
Netto.
Netto-Betrag des
      Vorgangs
Steuer
Steuer-Betrag des
      Vorgangs
Periode.
Warenwirtschaftsperiode des
      Vorgangs
Jahr
Warenwirtschaftsjahr des
      Vorgangs
Übertragungsdatum.
Datum des Fibu Übertrags
PeriodeFibu
Fibuperiode des Vorgangs
JahrFibu
Fibujahr des Vorgangs
Erstbediener
Erster Bediener
Zustimmungsbediener
Zweiter Bediener beim
      Vieraugenprinzip
Erfasser
Erfasser/Ersteller des
      Vorgangs
Id
ID
      des zugehörigen bereits erzeugten Fibu-Belegs
Bereichsauswahl
Filter
Beschreibung
Belegnummer
Selektion der Belege mit Belegnummer

[...]


---

## Auswahllistenvariante Fibu Übertrag abgebrochen

Auswahllistenvariante Fibu Übertrag abgebrochen
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag abgebrochen
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag abgebrochen
Oder
Direktsprung
[FIB]
In dieser Variante werden Vorgänge mit Fibu Status
‚i.B.‘
dargestellt, für die ein begonnener aber nicht beendeter
Fibu-Übertrag-Auftrag im Datenstrom des Mandantenservers existiert und nicht
mehr aktuell vom Mandantenserver bearbeitet wird.
Derartige Konstellationen
können neben Hardware-Problemen (z.B. Stromausfall) auch dadurch entstehen, dass
der Mandantenserver eventgesteuert nach einer im Event eingestellten Zeit bei
Ausbleiben einer Rückmeldung des Mandantenservers, die nach Beendigung jedes
Mandantenserverauftrags erfolgt, in der Zeitspanne gestoppt und neu gestartet
wird. Die Ursache ist häufig ein zu kurz eingestelltes Zeitintervall im Event,
da insbesondere die Übertragung größerer Belege bei gleichzeitig starker
Belastung des Datenbankservers möglicherweise in diesem Zeitintervall noch nicht
beendet werden kann.
Die Funktion ‚
Fibu-Kennzeichen zurücksetzen‘
setzt, wenn möglich, den Fibu Status des Vorgangs auf
‚—‘
zurück, wenn
der Beleg nicht in der Fibu gefunden wird. Ist der Beleg bereits in der Fibu, so
wird der Fibu Status auf
‚Ja‘
gesetzt.
Felder der Auswahlliste
Feld
Beschreibung
Belegnr.
Vorgangsnummer,
bei
      Rohwaresammeldruck die Sammeldrucknummer
Belegdatum
Belegdatum des Vorgang,
bei
      Rohwaresammeldruck die Sammeldrucknummer
Datum Buchungsauftrag
Datum der Erstellung des
      Übertragungsauftrags für den Mandantenserver
Kontonr.
Kunden-/Lieferantennummer =
      Kontonummer
Kunde
Bezeichnung des
      Kunden/Lieferanten
Typ
Vorgangsklassenkürzel des
      Belegs
Unterklasse
Nummer der
      Vorgangsunterklasse
Rohware
Rohware-Kennung:
--: kein
      Rohwarevorgang
RW-Beleg:
      Rohware-Einzelbeleg
..RW-Sammeldruck: Rohware-Sammeldruck
RW-Stufe
Rohware-Abrechnungsstufe:
Absch
[...]


---

## Auswahllistenvariante Fibu Übertrag Standard

Auswahllistenvariante Fibu Übertrag Standard
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Standard
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Standard
Oder
Direktsprung
[FIB]
In dieser Variante werden Rechnungen,
Stornorechnungen, Gutschriften, Stornogutschriften und Inventurbelege ohne
Rohware, Produktion und Umbuchungen dargestellt
Felder der Auswahlliste
Feld
Beschreibung
Kontonr.
Kunden-/Lieferantennummer =
      Kontonummer
Kunde
Bezeichnung des
      Kunden/Lieferanten
Belegnr.
Nummer des Vorgangs
Typ
Vorgangsklassenkürzel des
      Belegs
Unterklasse
Nummer der
      Vorgangsunterklasse
Datum
Belegdatum
Druckkennzeichen
--:  Beleg ist nicht
      gedruckt
Ja:  Beleg ist gedruckt
Fib
--:  Beleg ist noch
      nicht übertragen
i.B.: Übertragungsauftrag an Mandantenserver
      erteilt
Ja: Beleg ist an Fibu übertragen
NN: Beleg ist nicht
      übertragbar (z.B. Stornobeleg zu nicht übertragenem
      Originalbeleg)
RAB
--:  Beleg ist noch
      nicht im Rechnungsaugangsbuch
i.B.: Übertragungsauftrag an
      Mandantenserver erteilt
Ja: Beleg ist im
      Rechnungsausgangsbuch
Verarb.
--:  Beleg ist nicht
      weiterverarbeitet
teilweise:  Beleg ist teildisponiert
ganz:
      Beleg ist weiterverarbeitet
Warenwert
Netto-Warenwert des
      Vorgangs
Netto.
Netto-Betrag des
      Vorgangs
Steuer
Steuer-Betrag des
      Vorgangs
Periode.
Warenwirtschaftsperiode des
      Vorgangs
Jahr
Warenwirtschaftsjahr des
      Vorgangs
Übertragungsdatum.
Datum des Fibu Übertrags
PeriodeFibu
Fibuperiode des Vorgangs
JahrFibu
Fibujahr des Vorgangs
Erstbediener
Erster Bediener
Zustimmungsbediener
Zweiter Bediener beim
      Vieraugenprinzip
Erfasser
Erfasser/Ersteller des
      Vorgangs
Bereichsauswahl
Filter
Beschreibung
Belegnummer
Selektion der Belege mit Belegnummer
      (von/bis)
Datum
Selektion der Belege mit Belegdatum
      (von/bis)
Kunde
Selektion der Belege mit
      Kunden-/Lieferantenn
[...]


---

## Export Mandantenübernahme

Export Mandantenübernahme
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Export
Variante Mandantenübernahme
Direktsprung
[FIEX]
In dieser Variante ist es möglich, Belege aus der
Warenwirtschaft (Einkaufsrechnungen, Einkaufsgutschriften, Ausgangsrechnungen,
Ausgangsgutschriften,…), die bereits in die Fibu übertragen und
gebucht
worden sind von einem Referenz-ERP System(Quell-Mandant) in einen oder mehrere Referenz-ERP
Mandanten(Ziel-Mandanten) zu übertragen. Die Daten werden durch den
Quell-Mandant direkt in die Tabelle FiBuImport der Ziel-Mandanten geschrieben.
Das Übertragen funktioniert nur dann, wenn die Relation FibuImport des
Ziel-Mandanten als Proxy-Tabelle im Quell-Mandanten eingerichtet ist. Wie sie
die Einrichtung vornehmen, ist an dieser
Stelle
beschrieben.
Bei diesem Verfahren findet kein Dateiaustausch
statt.
Voraussetzungen
Dieses Verfahren setzt voraus, dass die FiBu auf dem
Quell-Mandanten und den Ziel-Mandanten gleich eingerichtet sind. Dies bedeutet
auch, dass neue Konten die neu auf dem Quell-Mandanten hinzugefügt wurden, auch
auf den Zielmandaten neu eingerichtet werden müssen.
Einrichtung des Exportes
Über die Funktion
Einrichten
F5
kann eine andere Prozedur ausgewählt
werden. Die Prozedur muss die gleichen Eingangs-, sowie Ausgangsparameter wie
die Standardprozedur haben. Des Weiteren müssen hier die Proxy-Tabellen
eingetragen werden. Für jede Proxy-Tabelle wird der Export durchgeführt.
Start
Mit der Funktion
„Start“
wird der Export der Ausgewählten
Daten gestartet. Die Export Daten werden nur an die Mandanten verteilt, bei
denen die Verbindung vorhanden ist und das Kennzeichen Übertragen auf „Ja“
gestellt ist.
Export Wiederholen
Mit der Funktion Export Wiederholen, können
übertragenen Daten erneut in die Ziel Mandanten verteilt werden. Dabei ist zu
beachten, dass in den Zielmandanten die Buchung des zu wiederholenden Exports
zurückgesetzt worden sind. Beim Ausführen der Funktion öffnet sich eine Auswahl
aus dieser Auswahl kann dan
[...]


---

## Fibu Übertrag aus Ware

Fibu Übertrag aus Ware
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Oder
Direktsprung
[FIB]
In dieser Anwendung können in Vorgänge sowohl in die
Finanzbuchhaltung übertragen werden als auch kontrolliert werden, welche
Vorgänge bereits übertragen wurden und welche nicht.
Mittels der Funktion
‚Fibu-Übertrag‘
werden für
die selektierten und markierten Vorgänge Übertragungsaufträge an den
Mandantenserver übermittelt. Der eigentliche Übertrag wird dann durch den
Mandantenserver durchgeführt.
Die zur Verfügung stehenden Auswahllisten-Varianten
unterscheiden sich vor allem hinsichtlich der heranzuziehenden
Vorgangsarten.
So können in der Variante
‚Fibu Übertrag Standard‘
nur Rechnungen, Stornorechnungen, Gutschriften, Stornogutschriften und
Inventurbelege ohne Rohware, Produktion und Umbuchungen berücksichtigt werden.
In den Varianten
‚Fibu Übertrag incl. Rohware‘
und
‚Fibu Übertrag
mit Positionszeilen‘
sind zusätzlich auch Rohware-Einzelabrechnungen
darstellbar.
Rohware-Sammeldruck-Belege können nur in der Variante
‚Fibu
Übertrag Rohware-Sammelbelege‘
und Umbuchungs- und Produktionsbelege in der
Variante
‚Fibu Übertrag Umbuchungen und Produktion‘
ausgewählt
werden.
Die Variante
‚Fibu Übertrag abgebrochen‘
werden
Vorgänge zu bereits erteilten Übertragungsaufträgen des Mandantenservers
dargestellt, die einen nicht konsistenten Verarbeitungsstatus haben.

---

## Folgeartikel verwalten

Folgeartikel verwalten
Mit der Folgeartikelverwaltung lassen sich
verschiedene inhaltliche Fragestellungen lösen und über die
Steuerparametergruppe „
Folgeartikel
“ individualisieren.
Die Möglichkeiten sollen an zwei Beispielen
beschrieben werden.
•
Verkauf zusammenhängender Artikel
•
Leergutverwaltung
Verkauf zusammenhängender Artikel
Häufig hängen an einem Produkt Folgeprodukte, die mit
verkauft oder angeboten werden. (z.B. Regenrinne mit zwei Halterungen und
Schrauben)
Für diese Fragestellung werden an den Hauptartikel
Folgeartikel gehängt und über den Folgetyp festgelegt, ob alle Artikel der
Liste, mehrere oder nur einer zulässig ist.
Feld
Beschreibung
Alle
Alle
      Folgeartikel werden angeboten
Einen
Nur
      ein Folgeartikel ist zulässig
Mehrere
Mehrere Folgeartikel sind
      zulässig
Hierfür stehen folgende Felder auf der
Folgeartikelmaske zur Verfügung.
Feld
Beschreibung
Folgezähler
Laufende Nummer
Artikelstammnummer
Artikelstamm des
      Folgeartikels
Gültig ab
Folgeartikel werden nur dann
      gezogen, wenn das Abgrenzdatum (in der Regel das Lieferdatum) in der
      Vorgangserfassung innerhalb des durch
gültig ab
und
gültig
      bis
bestimmten Zeitraums liegt.
Gültig bis
Folgeartikel werden nur dann
      gezogen, wenn das Abgrenzdatum (in der Regel das Lieferdatum) in der
      Vorgangserfassung innerhalb des durch
gültig ab
und
gültig
      bis
bestimmten Zeitraums liegt.
EK /
      VK
Hier
      kann festgelegt werden, ob der Folgeartikel in den Bereichen Einkauf /
      Verkauf / Lagerumbuchung heranzuziehen ist.
Mengenkennzeichen
Das
      Mengenkennzeichen bestimmt, ob sich anschließend die Menge des
      Folgeartikels mittels eines Faktors oder Divisors aus der Menge des
      Hauptartikels ergibt oder aber der Wert hier festgelegt wird.
Beispiel:
Faktor, Wert = 2
⇨
Menge
des Hauptartikels = 1 so ist die
      Menge des Folgeartikels = 2
Divisor, Wert = 2
⇨
Menge des Hauptartikels = 1 so ist
      die Menge des Fol
[...]


---

## Gelangensbestätigung

Gelangensbestätigung
Warenverkauf
Übergreifend
Gelangensbestätigung
Gesetzeslage
Die steuerrechtliche Lage seit 2012: Wird Ware an
einen Kunden im Ausland verkauft, so geschieht dies steuerfrei. Wird dem
Finanzamt jedoch bei einer Prüfung nicht nachgewiesen, dass die Ware auch
tatsächlich ins Ausland geliefert wurde, so kann eine Nachbesteuerung angeordnet
werden.
Zu diesem Zwecke ist mit den Lieferpapieren eine
Gelangensbestätigung auszuliefern, die vom Empfänger quittiert und zurückgesandt
wird. Diese ist dann zu archivieren.
Seitens des Finanzamtes könnte im Fall einer Prüfung
die Nachbesteuerung unbelegter Lieferungen angeordnet werden. In diesem Fall
wenden Sie sich an die Steuerberater bzw. die zuständigen Finanzbehörden zur
Klärung des Vorgehens.
Einrichtung der Gelangensbestätigung
SPA
Es ist der
Lizenz-SPA 865 – Gelangensbestätigung
notwendig.
Die Gelangensbestätigung wird in der Regel mit dem
Lieferschein im Vorgangsdruck mittels eines eigenen Formulars erstellt. Jene
Steuergruppen für die eine Steuerfreiheit gilt, weil die Lieferung ins Ausland
erfolgt, können im Steuerparameter
SPA
830
eingetragen werden.
Wird ein Lieferschein mit dieser Steuergruppe
erstellt, so wird für diesen Vorgang beim Formulardruck das Erstellungsdatum der
Gelangensbestätigung festgehalten.
SPA 948 –
Gelangensbestätigung bei Belegkorrektur
.
Der Steuerparameter SPA 948 entscheidet, ob nach
Belegkorrektur eine neue Gelangensbestätigung gedruckt wird. Der Standardwert
ist „Nein“. Wenn nach der Korrektur eines Beleges eine neue Gelangensbestätigung
gedruckt werden muss, ist im Steuerparameter SPA 948 der Wert „Ja“ einzutragen.
Formular und Makro
Der Anschluss des Drucks wird über die
Vorgangsdruckklassen
(VRGD) geregelt. Wir liefern ein
Muster-Formular (-100)
mit aus, das
nötigenfalls sogar ohne Kopie und Anpassung derselben direkt zu verwenden ist.
Als Rücksendeadresse wird hier die Mandantenanschrift benutzt.
Ferner fungiert  das Mustermakro
AMIC_GelangensBest_
[...]


---

## Individuelle Preisklasse

Individuelle Preisklasse
Preise / Konditionen
Konstanten der Preispflege
Individualpreisklassen
Oder Direktsprung
[PRIK]
Kunden und Lieferanten können eine
Individualpreisklasse sowohl im Einkauf als auch im Verkauf zugeordnet bekommen.
Diese beschreibt die Zugehörigkeit zu einer Gruppe von Kunden/Lieferanten, für
die für Artikel mit einer dort zugeordneten Individualpreisgruppe zu einem
Zeitraum ein bestimmter gegebenenfalls mengenabhängiger individueller vom
Listenpreis abweichender Preis gilt. Neben einer Bezeichnung der Preisklasse
wird hier auch die Währung der Individualpreise zu dieser Klasse festgelegt.
Wenn eine neue individuelle Preisklasse manuell
angelegt oder automatisch generiert wird, wird eine eindeutige Identnummer aus
dem Wertebereich oberhalb von 100.000.000 vorgeschlagen bzw. verwendet. Der
Ident wird in einer internen Tabelle gespeichert und ist somit verbraucht.
Allerdings können Sie bei manueller Anlage statt dem vorgeschlagenen Ident auch
einen eigenen Wert vergeben. Sobald sie das Feld verlassen, wird der
eingetragene Wert festgeschrieben und kann nicht mehr geändert werden.
Im Pflegemodul
individuelle Preise/Rabatte
im
Verkauf
[PRI]
und Einkauf
[PRIE]
können auch individuelle Preise
für Kunden/Lieferanten erfasst werden, denen noch keine individuelle Preisklasse
im Verkauf beziehungsweise Einkauf zugeordnet wurde. In diesem Fall wird eine
neue individuelle Preisklasse erzeugt und automatisch zugeordnet.

---

## openTRANS (Thebe)

openTRANS (Thebe)
•
Das AddIn bietet die Möglichkeit, die Daten eines Beleges wie Angebot,
Lieferschein oder Rechnung mit Hilfe eines openTRANS-XML zu exportieren. Das
AddIn arbeitet im Rahmen eines Belegdrucks.
•
Das AddIn extrahiert Dateien aus dem Formulararchiv für den
Import
so dass sie weiter
verarbeitet werden können. Mögliche Dateitypen sind:
•
XML-Dateien – werden nicht verarbeitet
•
PDF mit angehängtem Attachment
•
Outlook-Mails mit PDF mit angehängtem Attachment

---

## openTRANS-Import

openTRANS-Import
Der Import von openTRANS ist vielfältig. Deshalb wird
dieser durch Makros individuell gestaltet. Das AddIn Thebe bereitet lediglich
die Bearbeitung vor. Im Folgenden ist die Einrichtung und die Verarbeitung
beschrieben.
Einrichtung
Warenverkauf
openTRANS Import
Variante „Profile für den
Importbereich“
Pfleger des
      openTRANS-Importprofils
Profilname
Name
      des Profile
Klasse
Vorgangsklasse
Unterklasse
Vorgangsunterklasse
Absendertyp
Welchen Typ hat der im Dokument
      beschriebene Absender
Importlager
Lager auf das importiert
      wird
Makro
Makro, das zum Import aufgerufen
      wird Das Makro wird von einer Funktion in der Variante
      „Dokumentenverarbeitung“ benutzt. (siehe
Import per
      Makro
)
Gebinde nicht
      exportieren
Beim Speichern eines neuen Profils wird eine Funktion
in der Optionbox der Variante „Dokumentenverarbeitung“ angelegt, die den Import
von Dokumenten mit Hilfe dieses Profils startet.
Verarbeitung
Quellen
Die openTRANS-Dokumente können aus verschiedenen
Quellen gewonnen werden. Je nach Typ können sie erst nach Extrakt oder sofort
weiterverarbeitet werden. In jedem Fall werden die Dateien zunächst ins
Formulararchiv importiert und mit einer entsprechenden Belegklasse versehen.
Belegklassen für openTRANS im
      Formulararchiv
Typ
Belegklasse
Verarbeitung
E-Mail mit Anhang
8031
      – openTRANS unbearbeitet
Mit
      Extraktion
PDF
      mit openTRANS-Anhang
openTRANS-XML-Datei
8032
      – openTRANS extrahiert
Warenverkauf
openTRANS Import
Variante „Dokumentenverarbeitung“
Schritt 1 : Extraktion
Beginnen Sie zunächst mit dem Status „extrahierbare“
Dokumente.
Hier sehen Sie im Formulararchiv abgelegte
(importierte Dokumente) mit der Vorgangsklasse „8031 – openTRANS unbearbeitet“.
Dies können eMails oder PDF-Dokumente mit eingeschlossenen Anhängen sein. Diese
müssen zunächst ins Archiv extrahiert werden.
Verwenden Sie die Funktion „Extrahieren“, um die
markierten Einträge zu entpack
[...]


---

## Steuerparameter

Steuerparameter
Eine Liste der Steuerparameter für die Kasse finden
Sie unter
Firmenstamm /
Steuerparameter / Kasse/Barverkauf
.

---

## Kasseneinstellungen

Kasseneinstellungen
Die Kasseneinstellungen werden in Vorlagen gegliedert,
die wiederum in der Kassenverwaltung den einzelnen Kassenstandorten zugeordnet
werden können.
Aeins
Lagernummer Markt
Lagernummer des Marktes bei
      Barverkauf
Abgleich mit Preisliste
Bei
      Preisänderung wird dieser mit dieser EK-Liste verprobt
Allgemein
EC-Karte manuell
      erfassen
Nein=EC-Kartenleser ist aktiv, nur
      dort Eingabe möglich
Ja=Keine Steuerung über EC
      Kartenleser. Siehe auch
Zahlungen mit Karte
BV-Abschluss erzwingen
Tagesabschluss erzwingen
Eine
      Erfassung kann bei Einstellung „Ja“ nur erfolgen, wenn die Kassensitzung
      am gleichen Tag eröffnet wurde. Ggf. Muss die laufende Sitzung erst
      geschlossen und dann neu eröffnet werden.
Barverkauf
Nicht in POS-Kasse
Max
      Skontosatz
Maximaler Skontosatz in Prozent, der
      in der Kasse mit dieser Vorlage verwendet werden kann.
Displaytext
01:Displaytext Eröffnung
Text, der bei Eröffnung der Kasse
      angezeigt wird.
02:Displaytext Abschluß
Text, der bei Abschluss der Kasse
      angezeigt wird.
03:Displaytext
      Unterbrechung
Text, der bei Pause der Kasse
      angezeigt wird.
04:Displaytext nach
      Vorgang
Text, der bei Abschluss der
      Abschluss eines Vorgangs angezeigt wird.
05:Displaytext nach
      Parken
Text, der nach Entparken eines
      Vorgangs angezeigt wird.
06:Displaytext Kunde zahlt
      noch
Text, der auf dem Display bei
      Verkauf Zame angezeigt wird.
07:Displaytext Kasse zahlt
      noch
Text, der auf dem Display bei
      Einkauf/Retoure angezeigt wird.
08:Displaytext Kasse zahlt
      zurück
Text, der auf dem Display bei
      Rückgeld bei Verkauf/Zame angezeigt wird.
09:Displaytext Kasse zahlt
      zurück
Text, der auf dem Display bei
      Rückgeld beim Sortenwechsel angezeigt wird.
10:Displaytext Passend
      gezahlt
Text, der auf dem Display bei
      Passend gezahlt angezeigt wird.
11:Displaytext
      Einzahlungssumme
Text
[...]


---

## Kontraktklassen

Kontraktklassen
Hauptmenü
Kontraktverwaltung
Kontraktklassen
oder Direktsprung
[KTKL]
Kontraktklassen werden bei der Neuerfassung eines
Kontraktes angegeben.
Die üblichen Kontraktklassen sind Verkaufs- und
Einkaufskontrakte.
Mit Fremdlagerkontrakten ist die Verwaltung von
Vereinbarungen möglich, bei denen die Ware in Fremdbesitz ist.
Rohwarenkontrakte unterliegen insofern speziellen
Bedingungen, als qualitative Merkmale der Rohwarenabrechnung zur Verfügung
gestellt werden und kalkulatorische Bestände geführt werden.

---

## Kontrakt „Washout and Circle“

Kontrakt „Washout and Circle“
Hauptmenü
Kontraktverwaltung
Kontrakt Stammdaten
oder den Direktsprung
[KTR]
Allgemein
Ein Washout oder Circle Geschäft wird in der
Kontraktverwaltung durchgeführt. Washout und Circle Geschäfte funktionieren nur
mit Kontrakten, die den Typ Einkauf und Verkauf besitzen. Um ein Washout oder
ein Circle durchzuführen müssen diverse Voraussetzungen erfüllt sein. Bei dieser
Geschäftsart wird keine Ware zwischen den Geschäftspartnern bewegt sondern nur
der Rest Warenwert. Der Rest Warenwert ermittelt sich aus der Differenz der
Kontraktwerte über die fiktiv bewegte Menge. Diese Geschäfte sind in Deutschland
steuerfrei.
Washout
Was ist ein Washout:
Existieren für einen Kunden ein Einkaufskontrakt und
ein Verkaufskontrakt über den gleichen Artikel, so kann ein Washout durchgeführt
werden. Die Washout Menge ist entweder die gesamte Kontraktrestmenge, oder die
Kontraktrestmenge meines aktuellen Zeitraumes je nach Einstellung meines
Einrichterparameters
oder eine
manuell Eingegebene Menge.
Wenn keine Kontokorrenten Kunden verwendet werden
sondern nur Kreditoren und Debitoren so muss der
Einrichterparameter
„Unterschiedliche Kunden bei Washout“ auf „Ja“ gesetzt werden.
Circle
Was ist ein Circle:
Ein Circle Geschäft kann dann durchgeführt werden,
wenn ein Lieferant und ein Kunde mit einer dritten Firma ein Kontrakt über den
gleichen Artikel abgeschlossen haben.
Dritt Firma
Verkaufskontrakt
Einkaufskontrakt
Lieferant
Kunde
Einkaufskontrakt
Verkaufskontrakt
Meine Firma
Hierbei ist festzuhalten, dass nicht mehr der
eigentliche Kontraktpreis gültig ist, sondern der kleinste bezahlte
Kontraktpreis in der Kette. Dieser ist beim Circle Geschäft einzutragen.
Die Circle Menge ist entweder die gesamte
Kontraktrestmenge, oder die Kontraktrestmenge meines aktuellen Zeitraumes je
nach Einstellung meines
Einrichterparameters
oder eine
manuell Eingegebene Menge.
Bei dem Circle Geschäft werden zwei Finale Belege
erzeugt. Einmal für den Einkauf und
[...]


---

## Kopfdaten (Kontrakt)

Kopfdaten (Kontrakt)
Folgende Felder stehen in den Kopfdaten eines
Kontrakts zur Verfügung.
Kopfdaten
Kontraktklasse
Üblich sind:

       1         =
      Verkaufskontrakt
11        =
      Einkaufskontrakt
Kontraktunterklasse
Festlegung des Nr. Kreises und der
      Druckformulare für bestimmte Kontraktarten
(Getreide, Futtermittel, Dünger,
      Sonstiges usw.)
Kontraktgruppe/-kunde
Ein
      Kontrakt wird nicht für einen Kunden abgeschlossen, sondern für eine
Kontraktgruppe
. Diese Gruppe
      kann in diesem Feld eingetragen werden.
Hauptkunde (HK)
Ist
      die Kontraktgruppe, der ein neuer Kontrakt zugeordnet werden soll, noch
      nicht vorhanden, so kann auf dem Feld Kundennummer nicht nur per F3 ein
      Kunde ausgewählt werden, sondern auch direkt durch Eingabe einer
      Kundennummer, wenn diese bekannt ist.
Kreditüberwachung
Hier
      steht das Saldo und das Kreditlimit des Kunden. Sollte das Kreditlimit
      nicht 0,00 sein, so wird anhand des Saldos und des Kreditlimits ermittelt
      ob dieses überschritte ist.
Kontraktnummer
Der
      Wertebereich der Kontraktnummer ist in der Nummernkreisverwaltung
      festgelegt. Hier wird die nächste freie vorgeschlagen; sie kann
      überschrieben werden.
Bezeichnung/Kennzeichnung
Hierbei handelt es sich um einen
      frei eingebbaren Text zur näheren Kennzeichnung des
      Kontraktes.

---

## Kostenobjektgruppe

Kostenobjektgruppe
Hauptmenü
Kostenrechnung
Kostenobjektstamm
Kostenobjektgruppe
Direktsprung
[KSOBG]
Dieses Modul ist nur bei aktivierter
Kostenobjekt-Lizenz verfügbar.
Über die Kostenobjektgruppe werden die Verkaufs- und
Einkaufsbuchungen der Warenwirtschaft automatisch auf den Kostenobjekten
verbucht. Eine Kostenobjektgruppe wird dem Artikel zugeordnet. Sie enthält
jeweils ein Kostenobjekt für den Verkauf und den Einkauf.

---

## Kostenstellengruppe

Kostenstellengruppe
Hauptmenü
Kostenrechnung
Kostenstellenstamm
Kostenstellengruppe
Direktsprung
[KSTG]
Über die Kostenstellengruppe werden die Verkaufs- und
Einkaufsbuchungen der Warenwirtschaft automatisch auf den Kostenstellen
verbucht. Eine Kostenstellengruppe wird dem Artikel zugeordnet. Sie enthält
jeweils eine Kostenstelle für den Verkauf und den Einkauf.

---

## Kostenträgergruppe

Kostenträgergruppe
Hauptmenü
Kostenrechnung
Kostenträgerstamm
Kostenträgergruppe
Direktsprung
[KSTRG]
Über die Kostenträgergruppe werden die Verkaufs- und
Einkaufsbuchungen der Warenwirtschaft automatisch auf den Kostenträgern
verbucht. Eine Kostenträgergruppe wird dem Artikel zugeordnet. Sie enthält
jeweils einen Kostenträger für den Verkauf und den Einkauf.

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

## Preismatrix für Listenpreise

Preismatrix für Listenpreise
Preise / Konditionen
Konstanten der Preispflege
Preismatrixpflege
Oder Direktsprung
[PRM]
Einem Artikel wird im Einkauf und im Verkauf jeweils
eine Preismatrix zugeordnet, die an dieser Stelle gepflegt wird. Neben der
identifizierenden Matrixnummer kann eine aussagekräftige Bezeichnung vergeben
werden. Eine Preismatrix dient dazu, Kunden/Lieferanten mittels der dort
zugeordneten
Preisklassen
eine
Listenpreisdefinition
zuzuordnen, mit deren Hilfe
Listenpreise
zum Artikel und Kunden/Lieferanten bestimmt
werden können.
Es können mehrere Listenpreisdefinitionen angegeben werden und
jeder Preisdefinition mehrere Preisklassen zugeordnet werden. Dabei darf jede
Preisklasse jedoch nur einmal in der gesamten Matrix vorkommen. Eine besondere
Bedeutung hat die Zuordnung der Preisklasse 0 zu einer Listenpreisdefinition:
Wird während der Preisfindung in der Preismatrix keine Zuordnung der Preisklasse
x (ungleich 0!)  eines Kunden/Lieferanten zu einer Listenpreisdefinition
gefunden, so wird, falls in der Matrix definiert, die Listenpreisdefinition mit
der Zuordnung der Preisklasse 0 herangezogen. In diesem Fall bedeutet diese
Zuordnung also etwa „alle Kunden/Lieferanten, deren Preisklasse nicht in der
Matrix anders zugeordnet sind“. Daher darf die Preisklasse 0 auch nur alleine
und nicht mit weiteren Preisklassen einer Listenpreisdefinition zugeordnet
werden.
Zur jeweils aktuellen Listenpreisdefinitionszeile in der oberen
Tabelle wird die Zuordnung der Preisklassen in der unteren Tabelle
vorgenommen.
Die Reihenfolge der
Listenpreisdefinitionen
einer Preismatrix bestimmt auch deren Reihenfolge im
Listenpreispfleger
. Diese
Reihenfolge kann zu jeder Zeit durch Änderung der Sortierungsnummer angepasst
werden.
Tabelle Listenpreise
Spaltenname
Bedeutung
Position
Sortierungsnummer zur Festlegung der
      Reihenfolge
Nummer
Nummer der
      Listenpreisdefinition
Bezeichnung
Bezeichnung der
      Listenpreisdefinition
Währung
Währungsk
[...]


---

## Preisklasse für Listenpreise

Preisklasse für Listenpreise
Preise / Konditionen
Konstanten der Preispflege
Oder Direktsprung Preisklassen
[PRK]
Kunden und Lieferanten wird im Einkauf und im Verkauf
jeweils eine Preisklasse zugeordnet. Die an dieser Stelle pflegbaren
Preisklassen sollten neben der Preisklassennummer über eine aussagekräftige
Bezeichnung verfügen. Mit Hilfe der jeweiligen Preisklasse werden
Listenpreise
zum
Kunden/Lieferanten bestimmt. Die Preisklasse mit der Nummer 0 bedeutet, dass ein
Kunde oder Lieferant mit dieser Preisklasse kein Listenpreis zuzuordnen ist.

---

## Listenpreise Verkauf und Einkauf

Listenpreise Verkauf und Einkauf
Listenpreise stellen in vielen Fällen das zentrale
Preisfindungssystem dar. Es beruht darauf, dass von Kunden (-klassen)
unterschiedlich kalkulierte Preise au­to­­­matisch vom Programm
gezogen werden. Dies ist auch in Referenz-ERP realisiert: Pro Arti­kel können im
Prinzip beliebig viele Preise vergeben und Kunden zugeordnet wer­den.
Grundlage des Verfahrens ist die Einrichtung einer oder mehrerer
Preis­ma­trizen, die Zuordnung von Listenpreisklassen zu Kunden und die
Eingabe von Listen­preisen beim Artikel. Auf die Einrichtung von
Preismatrizen und ihrer Bedeutung wird im Rahmen der Preispflege eingegangen.
Nachfolgend wird unterstellt, dass sie vor­handen ist und die Preise
gepflegt werden sollen.
Sowohl in der Preisübersicht der Artikelmaske als auch
im Preispflegemodul ist es möglich, mittels einer Datenbankprozedur die
Sichtbarkeit und Pflegbarkeit von vorhandenen Preisen zu bestimmten
Preislistennummern (Listenpreisbezeichnungen) für ausgewählte Bediener zu
erlauben oder zu verbieten. Der Name der Datenbankprozedur wird dazu in der
globalen Option ‚Listenpreispflegefilterprozedur‘ ohne Parameterangaben
festgelegt. Die verwendeten Datenbankprozeduren müssen ein RESULT mit einem
Attribut zurückliefern, dass praktischerweise vom Typ ‚integer‘ oder ‚smallint‘
sein sollte und den Wert 0 (Preis NICHT sichtbar/pflegbar) oder 1 (Preis
sichtbar/pflegbar) enthält. Der Name des Ergebnisfeldes ist beliebig wählbar.
Die Parameter der DB-Prozedur werden mittels
festgelegter Parameternamen bestimmt. Diese sind mit DEFAULT-Werten in der
Parameterliste zu versehen. Aus der Liste der möglichen Parameter müssen nur die
tatsächlich benötigten deklariert werden.
Die Parameter, die zur Laufzeit versorgt werden
sind:
Parameter
Typ
Beschreibung
PAR_BEDIENERID
INTEGER
Dieser Parameter übergibt die ID des
      Referenz-ERP-Bedieners.
PAR_BEDIENERKLASSE
INTEGER
Dieser Parameter übergibt die
      Bedienerklasse des Referenz-ERP-Bedieners.
PAR_ART
[...]


---

## Inventur

Inventur
Die folgenden Arbeitsschritte halten die LVS-Bestände
mit denen der Warenwirtschaft stets analog:
1.
Wareneingang – die Materialaufnahme ergibt summiert einen
Eingangs-Lieferschein
2.
Warenausgang – die Aufladung ergibt summiert einen Lieferschein
3.
Lagerumbuchung die Aufladung ergibt summiert einen Eingangs- und
Ausgangs-Lieferschein
4.
Produktion – Die Ende-Meldung ergibt eine Korrektur der Produktion mit den
gegebenen Mengen
Gründe für Abweichungen
Somit sollten die Bestände in LVS und Warenwirtschaft
stets analog sein. Es gibt jedoch Gründe für Abweichungen:
•
Fehler bei der Erstaufnahme
•
Bruch/Verderb
•
Schwund
Begriffe Inventur
Für eine Bestandskorrektur gibt es zwei Anlässe:
1.
Geplante Inventur
mit Korrektur des gebuchten Bestandes mit dem physisch
gezählten Bestand
2.
Ungeplante Inventur
- Bestandskorrektur beim Feststellen von Schwund,
Bruch oder dergleichen.
Die geplante Inventur ist für alle Waren an einem
Stichtag machbar, an dem keinerlei sonstige Bewegung auf den Warenbeständen
stattfindet.
Alternativ kann man eine „
permanente Inventur
“
machen. Dabei werden einzelne Artikel(Artikelgruppen) zu einem Zeitpunkt
gezählt, zu dem geringe Bestände und kaum Bewegung auf dem Artikel ist. Diese
Art der Inventur ist gesetzlich auf bestimmte Artikelarten beschränkt und muss
jeweils in einem engen zeitlichen Zusammenhang gezählt werden. Dieser Zeitraum
wird in
SPA 1045 – Permanente
Inventur
festgelegt.

---

## Allokation

Allokation
In der Vorgangsunterklasse des Auftrags &
Ladescheins muss eine Auslagerstrategie festgelegt werden. Auch die Produktion
(Hier ausschließlich die Unterklasse 0) muss eine solche Prozedur bekommen.
Dies ist eine Prozedur der folgenden Signatur:
---<summary>Gibt
Auslagerstrategien aus</summary>
---<returns>Auslagerstrategie und Mindest oder
Maximalliefermengen</returns>
---<param name="in_listennr">ListNr aus der
MatrialOrder</param>
---<param name="in_listenpos">ListenPosition aus
der MatrialOrder</param>
create
procedure
P_BUK_Auslagerstrategie_Warenausgang
(
in
in_listennr
integer
,
in
in_listenpos
integer
)
result
(
AuslagerStrategie
integer
,
ueberlieferung
numeric
(
15
,
4
),
unterlieferung
numeric
(
15
,
4
)
)
Die Prozedur ermittelt anhand der Vorgangsdaten der
Materialorder, in welchen Prozentsätzen eine Über- bzw. Unterlieferung
stattfinden darf, bevor kommissioniert werden muss. So soll verhindert werden,
dass wegen geringer Mengen eigens eine Kommissionierung stattfindet.
Es empfiehlt sich bei Lagerumbuchungen und
Produktionen diese Sätze so hoch anzusetzen, dass keine Kommissionierung
stattfindet, sondern stets ganze Ladeträger ausgeliefert werden.
(MIN=99,MAX=9900)
Allokation im Regal-Lager
Im regal-Lager wird ab dem Zeitpunkt der Allokation
die Ware reserviert. Das bedeutet, dass nach einer Allokationsstrategie Paletten
ausgewählt werden, die in voller Menge ins Ziel gebracht werden sollen und
solche, von denen eine Teilmenge gebraucht wird, die also noch kommissioniert
werden müssen. Je nach Auslagerstrategie werden dann Fahraufträge
geschrieben.
Allokation im Blocklagerallokation
In einem Blocklager kann nicht gezielt auf eine
bestimmte Palette zugegriffen werden, Oft stehen diese in Reihen hintereinander
zuweilen sogar in mehreren Ebenen.
In diesem Fall findet eine Allokation nicht statt.
Stattdessen wird dem Bediener angezeigt, dass es sich im Blocklagerware handelt.
Wird nun die erste Palette gescannt, so wird die
not
[...]


---

## Einlagerung

Einlagerung
Es gibt verschiedene Einlagerungsmöglichkeiten:
1.
Manuell – Hier bestimmt der Lagermitarbeiter selbst, wohin die Ware eingelagert
wird
2.
Nach Vorschlag – Hier wird bei der Erstellung eines Ladeträgers im Wareneingang
durch Vorgangsimport im LVS-Kontrollmakro ein Fahrauftrag zu einer Lokalität
erzeugt.
public
void
After_Import(ImportVorgStamm ivs)
{
ImportVorgPosition ivp =
ivs._ImportVorgPosition[0];
int
lokTyp =
D.GetExecuteScalar(0,
"select lokalitaetstyp from
lvs_lokalitaeten lk where lokalitaetsnr = ? "
,
ivp._ImportVorgPositionLVS[0].LokalitaetsNr);
if
(lokTyp ==
44)
// Produktion Fertigware
{
D.ExecuteNonQuery(
"call p_DEMO_Einlagerstrategie(?,?,7000);"
,
ivp.UebernahmeId, ivp.SatzId);
}
if
(lokTyp ==
10)
// Wareneingang
{
D.ExecuteNonQuery(
"call p_DEMO_Einlagerstrategie(?,?,7000);"
,
ivp.UebernahmeId, ivp.SatzId);
}
}
Eine private Einlagerungsstrategie (Hier
p_DEMO_Einlagerstrategie) optimiert hier Wege oder Befüllungsgrad des
Lagers.
Empfohlener Arbeitsablauf Scanner:
•
Scan der NVE
o
Anzeige der NVE-Info ggf. mit
Fahrauftrags-Vorschlag
•
Scan der neuen Lokalität
o
Erzeugen einer
Ladeträgerbewegung im VIMP

---

## Wareneingang

Wareneingang
Im Wareneingang geht es darum, die in Referenz-ERP erfassten
Daten mit den Ladeträgern zu verknüpfen. In der Bestellung werden in der Regel
noch keine Partien festgelegt. Dies geschieht erst bei Anlieferung im
Entladeschein.
Die Ladepapiere werden also dazu verwendet, einen
Entladeschein zu erstellen, der die angelieferten Mengen aus den
Bestellpositionen zusammenfasst. Dabei können auch Anlieferungen aus
verschiedenen Bestellungen unter Umständen sogar von verschiedenen Lieferanten
zusammengefasst werden.
Hier werden nun auch Partien zugeordnet.
Der Entladeschein wird gedruckt und kann im Lager
abgearbeitet werden.
Empfohlener Arbeitsablauf Scanner:
1.
Scan der Entladescheinposition (ggf. mit Partie)
2.
Scan der NVE (Ladeträgeridentifikation)
3.
Eingabe der Menge auf dem Ladeträger
Somit sind Ladeträger, der Artikel, die Partie und die
Menge miteinander verbunden.
Beim Abschluss des Wareneingangs wird eine Summe über
die einzelnen Positionen gebildet und der Eingangslieferschein aus der
Bestellung teildisponiert. Dabei werden Partie-Informationen und Mengen aus dem
Entladeschein verwendet.
Die Datenbank-Funktion „AMIC_LVS_WE_Abschluss“ sorgt
dafür, dass die gesammelten Vorgangsimporte (LVS) in eine Teildispo umgewandelt
werden.
Beide Sätze müssen anschließend in einen
Verarbeitungsstatus gesetzt werden. (2 für LVS, 5 für Ladeschein)
Die eigentliche Belegerstellung erfolgt durch die
Verarbeitung im Vorgangsimport.
Achtung! Um die Partieinformationen aus dem Ladeschein
zu verwenden, muss das Vorgangsimportkontrollmakro des Eingangslieferscheins
dies unterstützen.
Der folgende Code macht dies beispielsweise:
public
void
WPos_Nach_Ladeschein_zu_ReLi(IVorgang vorg,
int
modus,
int
wabewId_SRC = 0,
int
wabewid_LD = 0,
bool
teilUmwandlung =
false
)
{
if
(wabewid_LD
!= 0)
{
//
Partien nachpflegen
DataTable dt = D.GetSql(
@"select distinct ivp.PartieId,isnull(vp.PartieArtiPosit,
pa.PartieArtiPosit) as PartieArtiPosit, vp.V_PosiParMenge
fr
[...]


---

## Eingangsbuchung

Eingangsbuchung
Hauptmenü
Wareneinkauf
Eingangslieferschein
Eingangslieferscheine bearbeiten
oder Direktsprung
[ELB]
I
n der ersten
Variante befindet sich die Funktion „
Ladeträgerzuordnen
“. Alternativ kann die
Funktion mit
SHIFT+F9
aufgerufen
werden.
Es öffnet sich jetzt eine Maske, die alle Positionen
des Lieferscheins enthält.
Allgemeine Info
Mit dieser Funktion können die Warenpositionen eines
Eingangslieferscheins in das Lagerverwaltungssystem eingebucht werden. Es ist
möglich eine Warenposition auf einen oder mehrere Ladeträger zu verteilen. Des
Weiteren ist möglich eine Position von einem Ladeträger auf einen anderen
Ladeträger umzubuchen oder zu löschen.
Zuordnen von Positionen zum Ladeträger
Um einer Position des Lieferscheins ein Ladeträger
zuzuordnen wird in das Feld Ladeträger die Ladeträgernummer eingetragen. Die
Lokalität wird mit der Lokalität des Ladeträgers vorbelegt.
Soll der Ladeträger auf eine andere Lokalität
transportiert werden, so ist in das Feld Lokalität eine andere Lokalitätsnummer
einzutragen. Das System bucht dann den Ladeträger automatisch von A nach B.
Soll eine Position nicht in auf einen Ladeträger
gebucht werden, so wird das Feld Ladeträger einfach leergelassen.
Mit Starte
Ladeträgerzuordnen
“
SHIFT+F9
wird die Position auf den
Ladeträger gebucht.
Mengenverteilung auf unterschiedliche Ladeträger
Soll eine Position auf mehrere Ladeträger verteilt
werden, so wird die Positionsmenge in das Mengenfeld eingetragen. Es wird
automatisch eine neue Position mit der Restmenge erzeugt. Der neuen Position
kann dann ein Ladeträger zugeordnet werden. Wenn eine Position gelöscht wird,
die aus einer anderen Position entstanden ist, so wird die Menge wieder auf die
Ursprungsposition addiert.
Löschen von Positionen
Mit der Tastenkombination
STRG+ALT+ENTF
kann eine Zeile aus dem Grid
entfernt werden. Wurde die zu löschende Position schon auf einen Ladeträger
gebucht, so wird diese wieder vom Ladeträger entfernt. Durch das Löschen
[...]


---

## Aktivität des Mandantenserver

Aktivität des Mandantenserver
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver-Info
Direktsprung
[MSI]
Dialog-Felder
Mandantenserver
Zustand
Mögliche Zustände:
0
      nicht aktiv
1
      wartet
2
      arbeitet
3
      Fehler
Arbeitsmodus
0
      Alle Aufträge
1
      Ein Auftrag und Stopp
2
      Pause
3
      Stopp
Anzahl Aufträge
Anzahl der noch zu bearbeitenden
      Aufträge
Zähler
Wird
      mit jeder Aktivierung des MS gezählt
ltz.
      Aktion
Zeitstempel der letzten
      Aktion
Seit
      Serverstart
Überschrift
Erledigte Aufträge
Anzahl erledigter Aufträge seit
      Serverstart
Fehlerhafte Aufträge
Anzahl fehlerhafter Aufträge seit
      Serverstart
insgesamt
Überschrift
Erledigte Aufträge
Anzahl erledigter Aufträge
      insgesamt
Fehlerhafte Aufträge
Anzahl fehlerhafter Aufträge
      insgesamt
Unvollständige Buchungen
Anzahl unvollständiger Buchungen
      insgesamt
Automatik eingeschaltet
Der
      Status, ob das
Event
für den Mandantenserver
      eingeschaltet ist.
Wiederholungsintervall
Das
      Zeitintervall des
Events
in dem geprüft wird, ob der
      Mandantenserver noch aktiv ist.
Zähler
Wird
      mit jeder Aktivierung des MS gezählt
Verarbeitungsroutine
Verarbeitungsroutine des
      Mandantenservers
Dialog-Funktionen
Mandantenserver
Neu
      Anzeigen
Aktualisiert die Anzeige
      (refresh)
Daueranzeige
Funktion zur Dauerhaften
      Anzeige
Statistik zurücksetzen
Setzt die Statistik
      zurück
unvollständige Aufträge
      zurücksetzen
Setzt die Unvollständigen Aufträge
      zurück
Auf
      Pause stellen
Pausiert den
      Mandantenserver‘
Einzelschritt
Einen einzelnen Schritt
      durchführen
Normale Bearbeitung
Stellt den Mandantenserver auf
      normale Bearbeitung
Stop
      Mandantenserver
Stopp den
      Mandantenserver
Event Manager
Ruft
      die Auswahlliste aller
Events
auf.
Event ändern
Ruft
      den Dialog zum Ändern des
Events
auf.
Event Zeitplan ändern
Ruft
      den Dial
[...]


---

## Manueller Einkaufspreis(EPA svmanuek

Manueller Einkaufspreis(EPA svmanuek
Bezeichnung
Standardwert
Erklärung
Soll
      das Feld EK-Preis festhalten im Standard angewählt sein.
Ja
Mit
      der Einstellung Ja wird das Kontrollfeld EK-Preis festhalten im Standard
      markiert.
Mit
      der Einstellung Nein ist das Kontrollfeld EP-Preis nicht
      markiert.

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

## Mengeneinheiten mit Gebinde

Mengeneinheiten mit Gebinde
Wenn Kartoffeln im 50 kg Sack verkauft werden und die
Grundmengeneinheit "kg" ist, die Bestände in "kg" geführt werden, der Preis sich
jedoch auf den "Sack" bezieht, dann muss die Gebindeumrechnung aktiviert werden.
Hierzu werden in der Eingabemaske folgende Daten erfasst.
Die Maske ist in folgende Bereiche aufgeteilt:
Kopfdaten
Tabreiter
– Allgemein
Tabreiter – Zusatz
Kopfdaten
Nummer
Nummer der zu definierenden
      Mengeneinheit.
Kurztext
Kurztext der Mengeneinheit (z. B.
      für Ausdrucke), z.B. "Sack".
Langtext
Langtext der Mengeneinheit (z.B. für
      Ausdrucke)
Bezeichnung
Ausführliche Bezeichnung der
      Mengeneinheit, z. B. für Auswahllisten. In diesem Fall z.B. "Sack 50
      kg".
Grundmengeneinheit
Nummer der Grundeinheit, auf die
      zurückgerechnet werden soll, z.B. „kg“.
Ergebniseinheit
Diejenige Mengeneinheit, in der das
      Ergebnis der Gebindeberechnung zurückgegeben wird.
Beispiel:
Es
      wird eine Palette mit Dosen à x Liter bearbeitet, dann ist das Ergebnis
      der Gebindeberechnung "Liter";
Handelt es sich um eine Palette mit
      Säcken à x kg, so kommen kg dabei heraus.
Das
      Ergebnis eines Volumengebindes sind dann z.B. Liter oder m³
      sein
Gebindetyp
Hier
      ist eine Angabe erforderlich, wenn ein Gebinde abgerechnet werden
      soll:
1    lineares Gebinde
      (Anzahl)
2    Gebinde 2. Stufe
      (Fläche)
3    Gebinde 3. Stufe
      (Volumen)
4    Addition (Gebi1
      + Gebi2)
5    Subtraktion
      (Geb1 - Geb2)
6    Faktor1 *
      Faktor2 / Faktor3
7    Faktor1 *
      Faktor2 * Faktor3 * Faktor4
Faktorherkunft
Kennzeichnung, woher die
      Gebinde-Faktoren für die Berechnung kommen. Es ist hier ein dreistufiges
      System implementiert, es können bei den Artikeln, beim Artikelstamm aber
      auch beim Gebinde selbst die Faktoren hinterlegt werden.
Tabreiter
Hier ist eine Auflistung der einzelnen Felder auf den
Tabreitern der Maske.
Allgemein
e

[...]


---

## Reports Massebilanz

Reports Massebilanz
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Massebilanz (Kompakt)
Direktsprung
[NAMAK]
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Massebilanz (Detail)
Direktsprung
[NAMAD]
Die Reports für die Massebilanz enthalten alle
Warenbewegungen, die der ausgewählten Massebilanz zugeordnet wurden. Ausgewiesen
werden dabei die Zugangs- und Abgangswerte, sowie die CO2 Werte.

---

## Aktualisierungsübersicht

Aktualisierungsübersicht
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Aktualisierungsübersicht
Direktsprung
[NAART]
Diese Variante zeigt die Vorgangspositionen an, die
bezüglich der Massebilanzverarbeitung noch nicht durch den
Mandantenserverprozess verarbeitet worden sind.
Folgende Funktionen stehen hier zur Verfügung.
Funktion
Beschreibung
Belege aktualisieren
Hiermit kann man die markierten
      Positionen unabhängig vom Mandantenserver aktualisieren.
Belegaktualisierung
      löschen
Hiermit kann für alle markierten
      Positionen die Belegaktualisierung entfernt werden.
Aktualisierungseinstellungen
Hiermit wird die Maske der
Aktualisierungseinstellungen
geöffnet.

---

## Artikelsummen

Artikelsummen
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Artikelsummen
Direktsprung
[NAART]
Diese Variante zeigt die Vortragsinformationen der
zugehörigen Artikel der Massebilanzen an. Zusätzlich werden die Summen für
Zugangs- und Abgangsmenge der Bewegungen zu den Artikeln angezeigt, die der
jeweiligen Massebilanz schon zugeordnet worden sind.

---

## Nachhaltigkeit

Nachhaltigkeit
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Die für die Nachhaltigkeitsverordnung erforderlichen
Programmmodule werden im Programmbereich „Nachhaltigkeit“ zusammengefasst.
Generell wird bei der Abwicklung davon ausgegangen,
dass überwiegend nach­haltige Ware gehandelt wird. Aus den Kombinationen
•
nachhaltiger Artikel
•
Lieferant nachhaltig / nicht nachhaltig
•
Kontrakt nachhaltig / nicht nachhaltig
ergibt sich dann eine automatische Vorbelegung. Diese
kann im Bedarfsfall bei der Belegerfassung auf einer Bearbeitungsmaske
überschrieben werden.
In den Stamm- und Bewegungsdaten können individuelle
THG-Werte verwaltet werden. Zukünftig ist damit zu rechnen, dass sich am Markt
solche Werte durchsetzen; sie sind dann einzutragen. Derzeit kann davon
ausgegangen werden, dass mit Standardwerten gearbeitet wird.
Die Programmfunktionen finden sich unter
•
Stammdaten
o
Kundenstamm
o
Artikelstamm
o
Kontraktstamm
•
Programmbereich „Wareneinkauf
o
Nachhaltigkeitswerte
o
Kundenübersicht
o
Artikelstammübersicht
o
Kontraktstammdaten
o
Bewegungsübersicht
o
Massebilanz (Kompakt)
o
Massebilanz (Detail)
•
Lieferscheinerfassung im Ein- und Verkauf
•
Interne Buchungen: Lagerumbuchung, Artikelumbuchung,
Produktionsumbuchung
•
Einstellungen des
Steuerparameters 844

---

## Bewegungsübersicht

Bewegungsübersicht
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Bewegungsübersicht
Direktsprung
[NAART]
In dieser Auswahlliste werden alle Bewegungen im Ein -
und Verkauf angezeigt. Diese kann man zum Beispiel nach nachhaltig und nicht
nachhaltiger Ware filtern.
Bei Rohwarebewegungen wird jeweils nur die für die
Massebilanz relevante Bewegung einer Rohwarenkette angezeigt.
Die Bewegungen kann man, falls diese in keiner
festgeschriebenen Massebilanz sind und die Bewegungen nachhaltig sind, einer
Massebilanz zuordnen.
Durch das Zuordnen einer Massebilanz zur letzten für
die Massebilanz relevanten Bewegung werden die zugehörigen Bewegungen der
Rohwarebelegkette (Lieferschein - > Abschlag -> Folgeabschlag - >
Finale) auch intern zugeordnet.
Die Spalte der Auswahlliste Nachhaltig gibt den Status
zurück, nachfolgend die Bedeutung der Farben dazu.
Farbe
Beschreibung
grün
Bewegung ist nachhaltig
rot
Bewegung ist nicht
      nachhaltig
Weiß
Bewegung hat keine
      Nachhaltigkeitsinformationen
Erläuterung speziellerer Selektionskriterien.
Kriterium
Beschreibung
Massebilanz zulässig
Einstellung ob nur Warenbewegungen
      angezeigt werden sollen, die zulässig für eine Massebilanz wären oder
      nicht.
Ohne
      Nachhaltigkeitsbewegung
Einstellung ob nur Warenbewegungen
      angezeigt werden sollen, die keine Nachhaltigkeitsinformationen enthalten.
      (
gelöschte Positionen
)
Schwellenwertprobleme
Hiermit kann man einstellen, ob
      Positionen mit oder ohne Schwellenwertprobleme angezeigt werden
      sollen.
THG / Massebilanz ändern
Auf dieser Maske lassen sich für die Warenbewegungen
die Nachhaltigkeitswerte pflegen. Einzelne Werte lassen sich dadurch einfach
ändern, wenn diese nicht bereits einer Massebilanz zugeordnet sind. Falls eine
Massebilanz schon zugeordnet wurde, kann nur noch die Massebilanzzuordnung
geändert/entfernt werden.
Möchte man die normalerweise nicht mehr änderbaren
Werte ändern, dann muss man die zuge
[...]


---

## Auswertungen

Auswertungen
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Mit den Funktionen
•
Mengenbilanz nachhaltig gruppiert
•
Massebilanz(Kompakt)
•
Massebilanz(Details)
können CRW-Reports generiert werden.

---

## Massenbilanz Kompakt

Massenbilanz Kompakt
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Massenbilanz Kompakt
Direktsprung
[NAART]
Diese Variante zeigt die Artikel mit ihrer zugehörigen
Massebilanzen und den Zu – und Abgängen. Diese können hier auch nach Anbauland
gruppiert werden.

---

## Massebilanzbewegungen

Massebilanzbewegungen
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Massebilanzbewegungen
Direktsprung
[NAART]
Diese Variante zeigt eine schnelle Ansicht der
Massebilanzen und den zugeordneten Bewegungen.
Mit der Funktion THG/ Massebilanz ändern lassen sich
alle nicht festgeschriebenen Warenbewegungen in die Maske Nachhaltigkeit THG
Positionsänderung laden und dort massenweise schnell korrigieren. Die
Massebilanz kann immer aktualisiert werden. Alle anderen Werte auf der Maske
können nur aktualisiert werden, wenn die Massebilanz noch nicht zugeordnet
wurde.
Es können aber gleichzeitig bei noch nicht
zugeordneter Massebilanz, die Werte geändert werden und dann eine Massebilanz
zugeordnet werden. Möchte man die normalerweise nicht mehr änderbaren Werte
ändern, dann muss man die zugeordnete Massebilanz zunächst entfernen.

---

## Faktor / THG-Wert / Anbauland

Faktor / THG-Wert / Anbauland
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Nachhaltigkeitswerte
Direktsprung
[NAWER]
Faktor
Für die THG-Werte können Faktoren hinterlegt werden,
dafür stehen im Pfleger folgende Felder zu Verfügung. Der Faktor ist aktuell
rein informativ und wird an keiner Stelle ausgewertet.
Feld
Beschreibung
Nummer
Nummer des Faktors
Bezeichnung
Bezeichnung des Faktors
Einheit
Textliche Beschreibung der
      Einheit
(Z.B. kg CO2-eq/kg
      N-Dünger)
Quelle
Herkunft der
      Informationen
(Z.B. IFEU / TREMOD)
Wert
Wert
      des Faktors
THG-Werte
In den THG-Werten werden für jede Fruchtart die
Teilstandardwerte für Anbau, Verarbeitung und Lieferung verwaltet. Des Weiteren
werden dort die Umrechnungsfaktoren von Standardwerten auf massebezogene Werte
für Zwischenprodukte gepflegt.
Im Artikelstamm wird dann auf diese Werte Bezug
genommen. Dadurch kann man für mehrere Artikelstämme die Informationen eines
THG-Wertes verwenden.
Feld
Beschreibung
Nummer
Nummer des THG-Wertes
Bezeichnung
Bezeichnung des
      THG-Wertes
Faktor
Zugrundeliegender Faktor des
      THG-Wertes
Allokationsfaktor
Fruchtartspezifische Konstante laut
      BLE
Konversionsfaktor
Fruchtartspezifische Konstante laut
      BLE
Teilstandardwert
Fruchtartspezifische Konstante laut
      BLE
Texte aktiv
Aktiviert die individuellen Texte
      für alle Artikel, die diesen THG-Wert hinterlegt haben.
Label
Individueller Text für den
      LABEL
(Ursprünglicher Text: „aus nachhaltigem Anbau.“)
Text1
Individueller Text für den
      TEXT1
(Ursprünglicher Text: „Zertifizierungssystem für Nachhaltigkeit:
      <ZERTIFIZIERUNGSMETHODETEXT>“)
Text2
Individueller Text für den
      TEXT2
(Ursprünglicher Text: „<ZERTIFIZIERUNGSMETHODETEXT>,
      Zertifikatsnummer: <ZERTIFIKATBEMERKUNG>“)
Text3
Individueller Text für den
      TEXT3
(Ursprünglicher Text: „Die Ware entspricht den
      Nachhaltigkeitsverordnungen (BioSt-NachV u. Biokraft-NachV)!“)
Text4
Individueller Text für den
[...]


---

## Massebilanz

Massebilanz
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Bewegungsübersicht
Variante Massebilanz
Direktsprung
[NAART]
Die Massebilanz enthält die zugeordneten
Warenbewegungen, den jeweiligen Vortrag und CO2-Wert, welche in den jeweiligen
Report angezeigt werden.
Für die Massebilanz muss ein eigenständiger
Nummernkreis zur Verfügung gestellt werden. Dieser muss dann in die Option
„NUMMERNKREIS_MASSEBILANZ“ eingetragen werden.
Dafür wechselt man zum Direktsprung [OPT] und richtet
mit F8 einen neuen Eintrag ein. Auf der Maske Optionen wählt man per F3 den
Eintrag NUMMERNKREIS_MASSEBILAN aus und in das Feld Wert trägt man den
gewünschten Nummernkreis ein.
Die vorhandenen Nummernkreis kann man unter dem
Direktsprung [NKS] einsehen und auch neue Nummernkreise einrichten.
Damit die Bewegungen von Nichtrohware -  oder
Rohwarebelegen einer Massebilanz zugeordnet werden können, müssen die Artikel
und Nuts-Nummer der jeweiligen Bewegung in der Massebilanz eingerichtet sein.
Dafür benötigt man die Lagernummer, die Nuts-Nummer und die Artikelnummer. Bei
fehlender Einrichtung einer Artikel- Lager- Nutsnummer in der gewünschten
Massebilanz findet diese bei der Zuordnung der Massebilanz zu einer Bewegung
automatisch statt und wird im Fehlerprotokoll als Ereignis protokolliert.
Des Weiteren muss beim Artikel das Gewicht
eingerichtet sein. Dies richtet man auf der Artikelstammmaske unter [ARS] ein,
indem man auf dem Tabreiter Allgemein in Gewich/Grundmengeneinheit das Feld
ausfüllt. Zuletzt muss der zugehörige Kunde ein Nachhaltigkeitszertifikat
besitzen, oder in der Bewegung muss ein passendes  Zertifikat angegeben
werden. In dem Zertifikat muss der Artikelnummer und die Nuts-Nummer
eingerichtet sein. Ohne diese Angaben ist der Massebilanzabgang bzw.
Massebilanzzugang immer mit dem Wert 0 angegeben.
Feld
Beschreibung
Nummer
Nummer der Massebilanz
Bezeichnung
Bezeichnung für die
      Massebilanz
Festgeschrieben
Solange die Massebilanz nicht
      festgeschrieben ist,
[...]


---

## Parameter der DSD-Abwicklung

Parameter der DSD-Abwicklung
Das Duale System ist eine privatwirtschaftliche
Initiative, welche die Produktverantwortung im Bereich der Verkaufsverpackungen
wahrnimmt. Der Begriff "dual" steht für ein zweites, zur kommunalen
Abfallentsorgung hinzukommendes System. Denn die Verpackungsverordnung fordert,
dass die Verwertung von Verkaufsverpackungen über ein flächendeckendes "duales"
System organisiert werden soll. Das Kreislaufwirtschaftsgesetz von 1994
überträgt auch in anderen Wirtschaftsbereichen der privaten
Entsorgungswirtschaft die Verantwortung für "Abfälle zur Verwertung", während
die kommunalwirtschaftliche Restmüllentsorgung für "Abfälle zur Beseitigung"
durch Deponieren und Verbrennen verantwortlich ist.
Grüner Punkt
Der Grüne Punkt ist das
Lizenzzeichen der Gesellschaft Duales System Deutschland (DSD). Das Zeichen
dokumentiert, dass die Verpackung, auf der es abgebildet ist, laut Hersteller
wieder verwertbar ist. Der Grüne Punkt sagt nichts über die Umweltfreundlichkeit
der Verpackung aus.
Um nun mit Hilfe von Referenz-ERP die Anforderungen zu
erfüllen, die an ein Wirtschaftsunternehmen gestellt werden sind in den
folgenden Bereichen Eintragungen notwendig:
Materialgewichtsabhängige Sätze
[DSDM]
Die Materialgruppen des Dualen Systems Deutschland DSD
werden in Referenz-ERP mitgeliefert. Sie können bei Bedarf erweitert werden. In jedem
Fall müssen die Preise eingegeben werden. Hierbei können die nachfolgenden
Felder erfasst werden.
Material
Nummer
Nummer der Materialgruppe.
Bezeichnung
Beschreibung Bezeichnung der Materialgruppe.
Einträge ab Datum
Beginn der Gültigkeit des Gewichtssatzes.
Preis
Gewichtssatz = Einzelpreis je Gewichtseinheit Des
abgesetzten Grüner-Punkt-Materials.
pro Anzahl
Preiseinheit zum Gewichtssatz des abgesetzten
Grüner-Punkt-Materials.
Mengeneinheit
Beschreibung Preis-Mengeneinheit zum Gewichtssatz.
Volumen / Stückabhängige Sätze
[DSDV]
Die Volumengruppen des Dualen Systems Deutschland DSD
werden in Referenz-ERP ebenfalls mitgelie
[...]


---

## Partiebewegung

Partiebewegung
Nachfolgend wird beschrieben, wie Partien im Einkauf
und im Verkauf mit den Artikeln der Vorgänge verknüpft werden. Hierbei sind
maßgeblich die Einstellungen der Steuerungsparameter hinsichtlich der
automatischen Partieauswahl verantwortlich (siehe
Steuerungsparameter [SPA]
Partieverwaltung
).

---

## Partiebewegung im Einkauf und im Verkauf

Partiebewegung im Einkauf und im Verkauf
Bei der Erfassung einer Bestellung/Auftrag, eines
Eingangs-/ Ausgangslieferscheines oder einer Eingangs-/ Ausgangsrechnung kann je
nach SPA-Einstellung einer Artikelposition eine Partie zugeordnet werden. In der
Positionserfassungsmaske, nach Erfassung der Artikelmengen und der Mengeneinheit
wird entweder automatisch das Partieauswahlfenster geöffnet (SPA 20,21) oder in
der Optionbox die Funktion
Partieauswahl
CF7
bereitgestellt.
Die Darstellung dieser Partieauswahl wird über SPA 10
und SPA 23 gesteuert. Durch Auswahl mit der Maus oder den Pfeiltasten kann eine
Partie angesteuert und mit RETURN (Enter) dieser Position zugeordnet werden.
ESC
:    Abbruch der
Partieauswahl
F8
:
Anlegen einer neuen Partie (siehe 9.2.1.)
F7
:
dieser Position wird keine Partie zugeordnet

---

## Partie-Nachweis (DRUCK)

Partie-Nachweis (DRUCK)
Hauptmenü
Partieverwaltung
Auswertung
Partie-Nachweis
Diese Auswertung informiert über die Mengenbewegungen
einer Partie. Dies bezogen auf Einkauf, Verkauf und Umbuchungen.
Die weiteren Inhalte dieser Druckvarianten entnehmen
Sie bitte der Anlage 1 und 2.

---

## Herkunft und Verbleib von Partiepositionen

Herkunft und Verbleib von Partiepositionen
Hauptmenü
Warenverkauf
Lieferscheinbearbeitung oder Direktsprung
[LIB]
Hauptmenü
Warenverkauf
Rechnungsbearbeitung oder Direktsprung
[REB]
Hauptmenü
Wareneinkauf
Eingangslieferscheine bearbeiten oder
Direktsprung
[ELB]
Hauptmenü
Wareneinkauf
Eingangsrechnungen bearbeiten oder
Direktsprung
[ERE]
Hauptmenü
Rohwarenabrechnung
EK-Rohwarenbearbeitung oder Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
VK-Rohwarenbearbeitung oder Direktsprung
[RWBV]
Hauptmenü
Produktion/Abwicklung
Produktion oder Direktsprung
[PROB]
Hauptmenü
Produktion/Abwicklung
Lager-Umbuchung oder Direktsprung
[LGU]
Hauptmenü
Produktion/Abwicklung
Artikel-Umbuchung oder Direktsprung
[ARU]
In den positionsorientierten Anwendungsvarianten der
Anwendungen zur Bearbeitung von Eingangs- und Ausgangs-Lieferscheinen, Eingangs-
und Ausgangs-Rechnungen, Produktionsbelegen sowie Artikel- und
Lagerumbuchungs-Belegen steht jeweils eine Funktion zur Bestimmung des Verbleibs
beziehungsweise der Herkunft der zur gewählten Belegposition zugehörigen
Partiepositionen zur Verfügung. In den Anwendungsvarianten zur Erfassung und
Korrektur von Rohwarebelegen bezieht sich die Herkunfts- beziehungsweise
Verbleib-Funktion auf die gegebenenfalls zugeordnete Partie der Lieferposition
des gewählten Belegs.
Ausgehend von den der gewählten Position zugeordneten
Partien werden bei der
Herkunfts-Funktion
alle Zugänge des Artikels zur
jeweiligen Partie unter Berücksichtigung von Artikel, Lager und Lagerplatz aus
anderen Partien und Eingangslieferscheinen und Eingangsrechnungen ermittelt,
wobei jeweils nur Bewegungen betrachtet werden, deren Bewegungsdatum kleiner
oder gleich dem der Ausgangsbewegung ist. Bei Zugängen aus anderen Partien
werden diese wiederum auf deren Herkunft untersucht.
Bei der
Verbleib-Funktion
werden, ausgehend von
den der gewählten Position zugeordneten Partien, alle Abgänge des Artikels zur
jeweiligen Partie unter Berücksichtigung von Artikel, Lager
[...]


---

## Partie und Teildisposition

Partie und Teildisposition
Hauptmenü
Wareneinkauf
Bestellung
Bestellungen bearbeiten
oder Direktsprung
[ELB]
Nachfolgend wird beschrieben, wie Partien bei einer
Teildisposition (Übernahme einer Teilmenge aus der Vorstufe (z.B. Bestellung))
bebucht werden.
Bei Erfassung der Bestellung (Nr.5) wurde die Partie
(Nr. 16) neu angelegt. Bei der Erfassung des Eingangslieferscheines wird, im
Positionsbereich mit der Funktion
Teildisposition
F6
, eine Auswahl aller nicht erledigten
Bestellungen für diesen Lieferanten angezeigt.
Nach Auswahl der Bestellung wird die gesamte
Positionsmenge übernommen und kann an dieser Stelle nicht korrigiert werden. Es
besteht lediglich Einfluss auf den Preis.
Nachdem diese Maske mit
F9
übernommen wurde, ist die Position der
Bestellung in den Eingangslieferschein übernommen. Somit ist auch die
Partiezuordnung der Bestellung in den Eingangslieferschein übernommen. Über die
Funktion
Korrektur Zeile
F5
kann nun die Menge und die Partie dieser
Eingangslieferscheinposition abgeändert werden.
Bei Betrachtung der Partie wird deutlich, dass im
Einkauf 1000 kg disponiert wurden und bereits 700 kg mit dem
Eingangslieferschein Nr. 5 eingetroffen sind.

---

## Registerkarte F3-Auswahlen

Registerkarte F3-Auswahlen
Feld
Bedeutung
Itembox für
      Vorgangskopie
Hier
      kann man Klasse, Unterklasse und eine Itembox für Einkauf,Verkauf und Lohn
      bzw. Klasse und Unterklasse für die Umbuchung (erscheint nur, wenn
      Wiegetyp Lagerumbuchung ist) angeben.
Die Itembox wird auf dem Feld
      Kunde wirksam, wenn der Einrichterparameter
„
Teildisposition/Vorgangskopie aus
      Auftrag
“ auf Teildispo oder Vorgangskopie bzw. das Feld
„
Art
      der Vorgangserzeugung
“
auf
Vorgangskopie
steht. Wird in
      der Vorlage keine Itembox angegeben ist die Itembox aus dem
      Einrichterparameter
Itembox für Teildispo aus
      Auftrag
für die Vorgangskopie/Teildispo aktiv, wenn der
      Einrichterparameter
Teildisposition/Vorgangskopie aus
      Auftrag
nicht auf Nein steht.
Sollte dies doch der Fall
      sein, dann werden die Standarditemboxen herangezogen. Dazu Genaueres
unter
Vorgangskopie
!
Itembox für
      Kontraktauswahl
Itembox für
      Kontrakt-Artikel

---

## Prüfaufträge bearbeiten

Prüfaufträge bearbeiten
Hauptmenü
Saatzucht
Saatenlabor
Prüfaufträge
oder Direktsprung
[PRUEA]
Nachdem ein
Prüfauftrag erstellt
wurde, können die
Aufträge in dieser Anwendung weiterbearbeitet werden.
Die mit * gekennzeichneten Felder sind Pflichtfelder
und müssen ausgefüllt werden, bevor der en Prüfauftrag freigegeben werden
kann.

---

## Prüfaufträge erstellen

Prüfaufträge erstellen
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Prüfaufträge werden über den
Partiestamm
erstellt. Dort existiert eine
Funktion „Prüfauftrag erstellen“, die zu den ausgewählten Partien die
Prüfaufträge erstellt:
Name
Bedeutung
Prüfungsart
Hier
      können aus dem Anwenderformat „AF_QUALART“ Prüfungsarten mir F3 ausgewählt
      werden
Datentabelle
In
      der Datentabelle werden alle ausgewählten Partien angezeigt.
Report
Ein
      Report, der über den Branchen-ERP-Etikettendruck erstellt wurde. Beim erstellen
      eines Prüfauftrages wird dieser Report/dieses Etikett sofort gedruckt.
Ohne
      Druckerauswahl
Mit
      Druckerauswahl
Hier
      kann ausgewählt werden, ob vor dem Druck eine Abfrage nach dem Drucker
      kommen soll.
Ist ein Prüfauftrag erstellt worden, kann man ihn
in der Anwendung
Prüfaufträge
bearbeiten.

---

## Rechnung Lieferschein aus Ladeschein

Rechnu
ng Lieferschein aus
Ladeschein
Mit diesem Modul lässt sich ein Ladeschein in ein
Lieferschein oder in eine Rechnung wandeln. Dazu werden die einzelnen
Ladescheinpositionen in der Auswahlliste markiert.
Dann wird die Funktion
Re./Lie. Aus Ladeschein
aufgerufen.
Bedeutung der Felder auf der  Maske Ladeschein
zu Rechnung oder Lieferschein.
Informationsfeld
In diesem Feld werden Ausgaben angezeigt, die während
der Konvertierung des Ladescheins zu einem Lieferschein oder einer Rechnung
auftreten, wie z.B. „Es wurden n Aufträge zu den gewählten Ladescheinen
gefunden“.
Box Aufträge
In der Box Aufträge werden alle Aufträge Angezeigt,
die zu den ausgewählten Ladescheinen gehören. In der linken Tabelle werden die
Auftragskopfdaten angezeigt. In der rechten Tabelle werden die Positionen zu dem
ausgewählten Auftrag angezeigt. Beim Einstieg in die Maske werden immer die
Positionen des ersten Auftrages angezeigt. Durch klicken auf einen anderen
Auftrag werden die Positionen des Auftrage aktualisiert.
Wenn in dem Feld Auftrag eine 0 steht, so existiert zu
diesem Ladeschein kein Auftrag.
Box Ladescheine
In der Box Ladescheine werden alle Ausgewählten
Ladeschein samt aller Positionen angezeigt.
Funktionen
Die Funktionen Ladeschein zu Lieferschein und
Ladeschein zu Rechnung haben die gleiche Funktionalität, außer das in
Abhängigkeit der Funktion eine Rechnung oder ein Lieferschien erstellt wird.
Mit der Funktion Abbruch wird die Maske verlassen ohne
eine Aktion durchzuführen.
Ablauf
Sind an einem Ladeschein unterschiedliche Aufträge
beteiligt, so wird zu jedem Auftrag ein Lieferschein erzeugt. Die Positionen
werden von dem jeweiligen Auftrag per Teildisposition in den Lieferschein
übertragen. Konnten einzelne Positionen des Auftrages nicht komplett geliefert
werden, so wird die Menge im Auftrag um die gelieferte Menge reduziert.
Besonderheiten
In der Anwendung
Vorgangsunterklasse
[FRZ]
für die Klasse 500 „Ladeschein“ auf der
Registerkarte „
Sperren
“ wird
[...]


---

## Rohwareparameter ansehen

Rohwareparameter
ansehen
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Rohwareparameter ansehen
Direktsprung
[SPA]
Direktsprung
[RWPA]
Im
Kopfbereich der Maske wird der Rohwareparameter mit Bezeichnung, Nummer und
Gruppe sowie der Bereich ‚
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
Nach
Positionierung des Cursors auf ein ‚
Wert
‘-Feld, kann mit der
Funktion ‚
Gültigkeiten
‘ die zu
diesem Parameterwert vorhandene Gültigkeitsliste zur Ansicht aufgerufen
werden.

---

## Beispiel Scancodes für den Eingangslieferschein

Beispiel Scancodes für den
Eingangslieferschein
In den Beispiel Scancodes für den Eingangslieferschein
befindet sich kein Scancode für einen Artikel. Hier ist ein Artikel aus dem
Sortiment zu wählen.
Eingangslieferschein Start
Eingangslieferschein Ende
Storno
Lieferant
Damit der gescannte Lieferant gefunden wird muss einem
Lieferanten aus dem Lieferantenstamm die ILN 12345 zugwiesen werden.
Lagerplatz
Damit der gescannte Lagerplatz im System gefunden wird
muss ein Lagerplatz mit der Nummer 1234 auf dem Lager des Scanners eingerichtet
werden.

---

## Auftrag zu Ladeschein zu Lieferschein

Auftrag zu Ladeschein zu
Lieferschein
Ladescheinliste
Vorbereitung
Um die Abarbeitung des Ladescheins mit dem Scanner zu
ermöglichen, wurde eine Vorlage für eine Ladescheinliste im System hinterlegt.
Diese Ladescheinliste befindet sich in der Anwendung
„Branchen-ERP Etikettendruck“ in der Variante „Vorlagen Branchen-ERP Etikettendruck Reporte“.
Diese Vorlage muss in den privaten Bereich übernommen werden. Wurde die Vorlage
erfolgreich in den privaten Bereich übernommen, so muss diese Vorlage mit der
Anwendung Ladeschein verbunden werden.
Anhand dieser Vorlage kann dann eine Individuelle
Ladescheinliste erstellt werden. Folgende Scancodes müssen sich auf der
Ladescheinliste befinden, damit die Ladescheinliste mit dem Scanner abgearbeitet
werden kann.
Scancode
Bedeutung
LAB
      + Ladescheinnummer
Startet die Erfassung des
      Ladeschein
LABENDE
Beendet die Erfassung des
      Ladescheins
AUFLADEN +
      Ladescheinnummer
Starten das Aufladen
AUFLADENENDE
Beendet die Erfassung des
      Aufladens.
STORNO
Mit
      diesem Befehl ist es möglich, eine erfasste Scannerposition aus dem
      Ladeschein zu stornieren.
Achtung:
Die privaten Funktion zur Erstellung
des Ladescheins und drucken des Ladescheins müssen angepasst werden. Dies gilt,
wenn anstelle eines Formulars ein Branchen-ERP Etikettendruck Dokument ausgedruckt
werden soll. Des Weiteren ist im Branchen-ERP Etikettendruck Dokument dann die Vorlauf
Funktion zu entfernen.
Private
      Funktion
Bedeutung
^jpl
      VorlaufScannerLadeschein 1
Drucken des Ladescheins
^jpl
      VorlaufScannerLadeschein 0
Editieren des
      Ladescheins
Ablauf
Mit diesem Modul können
Aufträge
, die zu einem Ladeschein umgewandelt worden
sind, bearbeitet werden. Aus diesen Ladeschein wird dann ein
Lieferschein
erzeugt, und die Lieferscheinmenge wird
dann per Teildisposition vom Auftrag abgebucht.
Als erstes muss ein Auftrag mit den aufzuladenden
Positionen erfasst werden. Es können auch mehrere Aufträge sein. In der
Anwendung „
Aufträge
[...]


---

## Scanner im Marktbereich

Scanner im Marktbereich
Folgende Module sind für den Marktbereich verfügbar.
•
Eingangslieferschein
•
Bestellung
•
Inventur
•
Permanente
Inventur
Starten eines Vorganges mit dem Scanner
Die Scannervorgänge können per Menü auf dem Scanner
aufgerufen werden. Dazu wird bei aktiver  Scanner Software die Taste F1
gedrückt.
Folgende Punkte können ausgewählt werden
Menü Punkt
Bedeutung
1.   Inventur
Startet ein Inventurerfassung
2.
      Bestellung
Startet eine
      Bestellerfassung
3.
      Eingangslieferschein
Startet ein
      Eingangslieferschein
4.   Permanente
      Inventur
Startet die Erfassung für einen
      Beleg der Permanenten Inventur
5.   Abbruch
Damit wird das Menü
      verlassen
6.   Reset
Damit wird der Scanner
      zurückgesetzt. Die erfassten Daten im Vorgangsimport werden für den
      Scanner auf gelöscht gesetzt
Um einen dieser Vorgänge zu starten kann entweder die
Zahl eingegeben werden, oder mit den Pfeiltasten Hoch oder Runter wird im Menü
der jeweilige Punkt ausgewählt und mit Enter bestätigt.
Die einzelnen Vorgänge des Scanners können natürlich
auch per Scancode gestartet werden.
Beenden eines Vorganges mit dem Scanner
Um ein Scanvorgang abzuschließen kann die Taste F2 des
Scanners gedrückt werden. Dadurch wird der aktuelle Scanvorgang geschlossen.
Auch hier können die einzelnen Vorgänge mit per
Scancode beendet werden.
Meldungen die beim Starten oder Beenden eines
Vorgangs auf dem Scanner erscheinen können
Meldung
Bedeutung
Der
      erfasste Befehl:
z.B.
      Inventur Ende
passt nicht zum aktuellem Vorgang
      des Scanners: Bestellung
Scannung wird verworfen
Dies
      bedeutet, dass mittels Scancode probiert wurde eine Inventur zu beenden,
      obwohl der sich der Scanner in der Bestellerfassung befindet. Mit den
      Pfeil Tasten nach oben oder unten wird die eigentliche Ansicht wieder
      geladen.
Es
      existiert kein offener Vorgang am Scanner. Der erfasste Befehl z.B.
      Bestellung Enden kann
[...]


---

## Terres-Markt Bestellung

Terres-Markt Bestellung
Die Markt Bestellung funktioniert zurzeit nur Online,
dies bedeutet der Scanner braucht eine ständige WLAN Verbindung.
Mit diesem Modul wird eine Bestellung erfasst, die
dann an einem oder mehreren Lieferanten zugeordnet werden kann. Die mit dem
Scanner erfassten Daten können in der
Vorgangimportschnittstelle
noch
bearbeitet
werden, bevor
aus den Daten eine
Bestellung
erzeugt
wird.
Hauptmenü
Externe Kommunikation
Stammdatenimport
Vorgangsimport
Um eine Bestellung mit einem Scanner aufzunehmen muss
wie folgt vorgegangen werden.
1.
Der
Steuerparameter 801
muss für den
Scanner eingerichtet werden.
2.
Einrichtung des
Moduls
3.
Der Scancode
BSE
muss im EAN 128
Verschlüsselt ausgedruckt werden.
4.
Der Scancode
BSENDE
muss in EAN 128
Verschlüsselt ausgedruckt werden.
5.
Der Scancode
STORNO
muss im EAN 128
Verschlüsselt ausgedruckt werden.
6.
Optional ILN Nummer des
Lieferanten
.
7.
Der Scanner muss auf das jeweilige
Lager
eingestellt sein.
8.
Einrichten des
Steuerparameters
883
Ablauf
Um eine Bestellung zu starten muss als erstes der
Scancode
BSE
mit dem
Scanner erfasst werden. Nach dem Starten der Bestellung besteht die Möglichkeit,
der Bestellung einen Lieferanten zuzuweisen. Der Lieferant ist wie folgt
einzugeben
00+ILN Nummer des Lieferanten
. Die ILN Nummer
wird im Lieferantenstamm gepflegt. Die
ILN Nummer
kann aber
auch eingescannt werden, wenn diese als Scancode vorhanden ist.
Der Lieferant kann aber auch nach dem Erfassen der
Bestellung in der
Vorgangimportschnittstelle
den erfassten
Positionen manuell zugewiesen werden.
Als nächstes werden die einzelnen Positionen erfasst,
dazu wird der Artikel mit dem Scanner erfasst. Dies geschieht über die EAN
Nummer des Artikels. Kann die Artikel EAN von dem Scanner nicht gelesen werden,
oder der EAN Code ist nicht vorhanden, so kann entweder die EAN Nummer oder die
Artikelnummer des Artikels im Eingabefeld des Scanners eingegeben werden. Die
Eingabe ist mi
[...]


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

## Kasse / Barverkauf

Kasse / Barverkauf

---

## Streckenwesen

Streckenwesen

---

## Stoffstromdatenbearbeitung auf der Warenpositions-Bearbeitungsmaske

Stoffstromdatenbearbeitung auf der Warenpositions-Bearbeitungsmaske
Bei der Erfassung und Korrektur von
Standardvorgängen im Einkauf und Verkauf
werden die zur Position
gehörenden Stoffstromdaten auf der zusätzlichen Registerkarte
‚Stoffstromwerte‘
dargestellt und können hier wie im
Stoffstrom-Editor
bearbeitet werden.
Dargestellt werden auf der Maske die zur angezeigten
Position aktuell gespeicherten Stoffstromdaten (Anteil, Anteiltyp und
Stoffstrommenge) sowie
für Verkaufsbelege der (optional) anzugebende
Lieferant
der Position.
Sind diesem Lieferanten im zugehörigen
Artikelstammsatz der Position individuelle Stoffstromparameter zugeordnet, so
ersetzen diese diejenigen aus der Artikelzusammensetzung. Für
Einkaufsbelege
ist dieses Maskenfeld nicht vorhanden, da der gesamte
Vorgang einem Lieferanten zugeordnet ist.
Wurde dem
Artikelstamm seit der Berechnung der Daten der Position in seiner
Zusammensetzung
ein weiterer
Stoffstrombestandteil hinzugefügt, so wird dieser bei der Vorgangsbearbeitung
mit den  definierten Stoffstromparametern ebenfalls dargestellt.
Die
Angabe
‚Herkunft der Werte‘
gibt an, ob der dargestellte Anteilwert der
Artikelstamm-Zusammensetzung entnommen wird, der Anteilwert und/oder der
Anteiltyp manuell angegeben wurde oder die berechnete Menge manuell erfasst
wurde. Bei Änderung des Anteil-Wertes und/oder des Anteiltyp (Spalte ‚in‘)
springt diese Anzeige automatisch auf den Wert
Anteil manuell
um. Wird
die Menge geändert, so wird hier
Menge manuell
ausgewiesen. Die
Einstellung kann auch manuell auf jeden der drei Werte geändert werden:
-
aus Artikelstamm
der Anteilwert und Anteiltyp wird neu aus der
Artikelstamm-Zusammensetzung gelesen
und die Berechnung der Menge wird
durchgeführt
-
Anteil manuell
die Berechnung der Menge wird mit dem gegebenen Anteil
durchgeführt
-
Menge manuell
der Anteilwert und die Menge bleiben wie dargestellt
auch bei zukünftigen Neuberechnungen erhalten.
Zu beachten:
Die Berechnungsfunktion wird
grund
[...]


---

## Outlook Terminplanung

Outlook Terminplanung
Die im Outlook gepflegten Terminelemente können mit
dem Tammo Modul bequem mit dem Auftragsmodul (ggf. auch anderen Vorgängen)
verbunden werden. Es sind hierbei 4 Einrichtungselemente zu beachten:
Einrichtung eines e-Mail Accounts der immer als
Teilnehmer in dem Termin eingetragen wird, damit Tammo dem entsprechenden
Terminplanungseintrag zugeordnet ist
Im Tammo Einrichtungsbereich muss angegeben werden,
welche Vorgangsklasse / Unterklasse für diese Funktionalität genutzt werden
soll.
Im Anschriftenpfleger muss hinterlegt sein, dass der
eintragende Terminplaner auch die Erlaubnis hat, das Tammo Modul nutzen zu
dürfen.
Im Tammo Einrichtungsbereich ist festzulegen, welche
Artikel / Lager Kombination  im Vorgang die Zeitspanne abrechnen soll.
Im Tammo Einrichtungsbereich ist festzulegen, ob die
Berechnung nach Stunden oder Minuten erfolgen soll.
Wird nun ein Terminelement im Outlook erfasst, und
wird diesem der Tammo – Teilnehmer zugeordnet (am besten
TammoTermin@domain.de
), so wird auf
Basis der im Termin eingetragenen Werte ein Vorgang erzeugt. Dieser Vorgang
enthält in den Zeitstempeln der Warenposition die Terminelement
(Startzeit/Endzeit und Dauer) und es wird eine Zuordnung des Termins zu dem
Initiator dieses Termins über die Vertretergruppenzuordnung hergestellt (Es ist
dabei darauf zu achten, dass die Vertreter in Ihren Adresszuordnungen korrekt
die passenden E-Mail Einträge enthalten).
Die Kundenzuordnung wird auf verschiedene Weisen
abgearbeitet:
Ist im Termin ein Terminteilnehmer eingetragen, der
eine Kundenadresse repräsentiert, so wird dieser  Kundeneintrag als Kunden
des Vorgangs zugeordnet.
Ist in der Betreffzeile die E-Mail-Adresse des
Terminteilnehmers der eine Kundenadresse repräsentiert eingetragen, so wird
dieser Kundeneintrag als Kunden des Vorgangs zugeordnet (wenn nicht sofort der
Kunde über die Terminplanung informiert werden soll).
Ist in der Betreffzeile ein Vermerk der Form K:nr oder
K:<Name>,<Or
[...]


---

## Technische Änderungen

Technische Änderungen
Die Tabelle PartieArtiMenIst wird für Partien nicht
mehr befüllt – sie ist allerdings weiterhin für das Streckenmodul aktiv! Private
Auswahllistenwahllisten oder MAKROS müssen daraufhin überprüft werden.
In der Tabelle V_Posiware sind neue Felder für die
interne Verwaltung bei der Teildisposition hinzugekommen. Das Feld V_PosiParWert
enthält nicht immer korrekte Werte.
Die bisherige Tabelle PartieBestand gibt es nicht
mehr, sie ist durch eine ‚baugleiche’ VIEW gleichen Namens ersetzt worden.
Ehemalige Trigger auf Partiebestand wurden entfernt.
Die Partiebestände werden jetzt in der Relation
PARTIEBESTANDPUR geführt. ACHTUNG: Das Feld REMENGE in dieser Relation wird
nicht immer versorgt, es wird demnächst entfernt!
Für die Ermittlung des Partiebestandes ist folgen
Datenbankfunktion geschaffen worden:
// Ermittele den Partiebestand
aus
// Relation PartiebestandPur
// Korrekturmengen fließen mit ein!
// bei Lagerplatz_in = -1 wird nicht
lagerplatzspezifisch ermittelt
// bei artikelid_ist_stammid = 1 werden Summen über
alle Artikel des gleichen Stamms gemacht
// bei mit_dispo = 1 werden Bestellungen und Aufträge
mitgezählt
//
---------------------------------------------------------------------
create
function
AMIC_FUNC_PARTIEBESTAND
(
in
partieid_in
integer
,
in
artikelid_in
integer
,
in
lagerplatz_in
integer default
-1,
in
artikelid_ist_stammid
integer default
0,
in
mit_dispo
integer default
0)
returns
decimal
(20,8)

---

## Teildisposition mit Vorlauf

Teildisposition mit Vorlauf
Eine besondere Art der Teildisposition ist die
„Teildisposition mit Vorlauf“, die über den
Steuerparameter 986
(„Teildisposition mit Vorlauf“ aktiv)
aktiviert werden kann. Sie kann
an den folgenden Stellen aufgerufen werden:
•
Angebotsbearbeitung
[AGB]
, Funktion
Teildisposition Auftrag
•
Angebotsbearbeitung
[AGB]
,
Funktion
Teildisposition
Lieferschein
•
Auftragsbearbeitung
[AUB]
,
Funktion
Teildisposition
Lieferschein
•
Auftragsbearbeitung
[BSB]
,
Funktion
Teildispo in
Eingangslieferschein
•
Auftragsbearbeitung
[BSB]
,
Funktion
Teildispo in
Eingangsrechnung
•
Auftragsbearbeitung
[BSB]
,
Funktion
Teildispo in Ladeschein
•
Auftragsbearbeitung
[LIB]
, Funktion
Teildisposition Rechnung
Bei der Teildisposition mit Vorlauf wird ein neuer
Ziel-Vorgang angelegt, bei dem die Daten aus dem Quell-Vorgang übernommen
werden, die auch im neuen Vorgang Sinn ergeben. Andere Daten wie erfassender
Bediener und Erfassungsdatum werden dagegen neu gesetzt. Ist die Lagernummerfehl
ein Sortimentslager, so wird die Lagernummerfehl auf die Lagernummer aus den
Vorgangskonstanten gesetzt.

---

## Teilproduktion

Teilproduktion
Startbedingungen
Die Funktionalität der Teilproduktion ist sowohl von einem
Produktionsauftrag, wie auch von einem Produktionsangebot aus möglich. Der
Auftrag (bzw. das Angebot) muss folgende Kriterien erfüllen:
•
Der Beleg darf nur eine Produktionsposition enthalten.
•
Pro Position ist maximal eine Partie eingetragen.
•
Es darf nur ein Element ausgewählt sein um es umzuwandeln.
•
Die Mengenkontrolle wird
dringend empfohlen
. Ansonsten werden die
Komponenten nicht mitkalkuliert.
Funktionalität
Ausgehend von einem Produktionsauftrag/-angebot gibt es den
Schalter Teilproduktion melden. Es wird die folgende Maske geöffnet.
Hier können nun folgende Felder gepflegt werden:
•
Menge: Dies ist die Menge die vom Angebot/Auftrag abgebucht wird. Die
Komponenten werden nach der Rezeptur berechnet.
•
Produktionskunde
•
Unterklasse der erzeugten Produktion
•
Auswahlbox-Box: Soll die neue Produktion zum Pflegen direkt geöffnet
werden?
Zum Abschließen mit [F9] speichern.
Storno
Wird eine per Teilproduktion erzeugte Produktion storniert,
so wird diese standardmäßig auf den Auftrag beziehungsweise das Angebot
zurückgebucht. Die Rückbuchung geht jedoch nur solange, wie die
Ausgangsproduktion (Angebot/Auftrag) noch nicht selbst in eine Produktion
umgewandelt wurde.
UFLD
Es gibt die Möglichkeit beim Angebot/Auftrag das
Buchverhalten einzurichten. Die Optionen sind:
•
Rückbuchung beim Storno aktivieren
•
Abbuchen vom Auftrag/Angebot aktivieren
Beide sind standardmäßig auf „Ja“ gesetzt. Auf diese Weiße
können Musterproduktionen vorerfasst werden welche immer wieder als Basis
herangezogen werden können. Hierbei sollte man sich bewusst sein, dass auf
Aufträgen Dispobestände geführt werden.

---

## Teilverkauf

Teilverkauf
Man kann Anlagegüter nur vollständig verkaufen. Jetzt
sind aber Geschäftsvorfälle, bei denen nur ein Teil des Anlagegutes verkauft
wird durchaus denkbar.
Beispiel: Von einem Grundstück (4000 qm), dass mit
300.000,00 Euro geführt wird, sollen 1000 qm verkauft werden.
Um diesen Geschäftsvorfall abzubilden muss man zuerst
¼ des Wertes umbuchen. Anschließend kann dieser Teil dann voll verkauft werden.
Auch können dann die sonstige betriebliche Erträge / Aufwendungen erfasst
werden. Verkauft man also das Anlagengut mit einem s.b.Ertrag von 45.000,00 Euro
so sieht der Anlagenspiegel wie folgt aus.

---

## Bestellung von Artikeln per Datendrehscheibe

Bestellung von Artikeln per Datendrehscheibe
Hier gibt es die Möglichkeit der Übermittlung von
Bestellungen an die Terres Zentrale. Eine entsprechende Umschlüsselung gemäß
Umschlüsselwerk (Querverweis Bereich Importumsetzer) wird vorgenommen
Vorgehensweise
Um eine Bestellung für Terres auszulösen, wird wie
folgt vorgegangen:
1.
Eine Bestellung wird wie im Referenz-ERP Standard erfasst.
Manuell ist darauf
zuachten, dass ein Lieferrant ausgewählt wird, der für Terres gelistet ist,
außerdem müssen die gewählten Artikel ebenfalls bei Terrres gelistet sein.
2.
Bestellung über
OpenTrans
drucken.
In diesem Vorgang wird
mittels einem dazugehörigem Konverter, der auf das
Umschlüsselwerk zugreift, die Bestellung in eine von Terres lesbare XML
Struktur gewandelt. Abschließend wird die Bestellung inklusive dem XML als
Anhang in das Archiv geschrieben und in den Ausgabepfad der
OpenTrans
Schnittstelle gespeichert.
3.
Bestellung an Terres senden
Die erstellte Bestellung aus der
OpenTrans
Schnittstelle
kann per
Belegversand
an Terres übermittelt
werden.
4.
Die erfassten Bestellungen können unter dem Terres Bestellexport angesehen
werden.
Hauptmenü
Externe Kommunikation
Datendrehscheibe
Bestellexport [
TERRX
]
Besonderheiten
Wird eine Bestellung erfasst, und diese ist noch nicht
an Terres übermittelt worden, und in der zwischenzeit erhält ein Artikel das
Kennzeichen „Bestellung-zulassen“ 0 so wird in den Standard Varianten der
Anwendung Bestellexport [
TERRX
] die
Bestellung rot markiert.
Vorher müssen einige Einstellungen im Referenz-ERP System
vorgenommen sein.
Einrichtungen
1.
Die
Dokumentenverwaltung
muss
aktiviert sein. Eventuell muss eine Lizenz für die Dokumentenverwaltung erworben
werden.
2.
OpenTrans
muss
Eingerichtet werden. (Lizenz erforderlich)
3.
Für das
Bestellformular
muss das
Archivierungskennzeichen
gesetzt
worden sein.
4.
In der
Formularzuordnung /
Vorgangsklasse
muss für die Bestellung und der dazugehörigen Unterklasse das
OpenTrans
[...]


---

## Spezialität bei Angeboten

Spezialität bei Angeboten
Ist der Steuerparameter
Angebot auf dem Sortimentslager zulassen (1051)
auf
„Ja“ gestellt und das Angebot ist gegen das Sortimentslager geschrieben worden,
so kann vor der Umwandlung eines Angebotes noch ein
Behandlungsschema
für den
Lagernummerwechsel
angegeben
werden. Wurde kein Behandlungsschema angegeben, so wird das Standard
Behandlungsschema gezogen. Des Weiteren muss das Ziellager im Feld Lagernummer
eingetragen werden. Angebote die eine Kombination von einem Sortimentslager und
einem anderen Lagertyp, wie z.B. Bestandslager haben, können im Moment nicht
umgewandelt werden.
Achtung
Werden in der Auswahlliste mehrere Angebote
ausgewählt, so wird die Einstellung des Behandlungsschema sowie des Ziellagers
für alle Umwandlungen verwendet.

---

## Verkauf/Verschrottung (Abgang)

Verkauf/Verschrottung
(Abgang)
Um ein Anlagegut aus dem Anlagenspiegel zu entfernen,
gibt man in der Historie eine Zeile vom Typen
Abgang/Verkauf
ein. Es wird
immer nur das gesamte Anlagengut verkauft.
Wird für ein Anlagegut der Abschreibungsverlauf
handels- und steuerrechtlich getrennt behandelt, so betreffen Umbuchungen immer
sowohl den steuerrechtlichen als auch den handelsrechtlichen Verlauf.
Wie beim Verkauf eines Anlagegutes verfahren wird,
hängt mit der Option „sonstige betriebliche Erträge / Aufwendungen führen“ im
Firmenstamm
zusammen. Steht diese
Option auf „Nein“, so wird beim Abgang/Verkauf der Restbuchwert als Betrag
eingetragen. Dieser kann auch nicht geändert werden. Beim Erstellen der
Abschreibungsvorschläge wird dieses Anlagegut bis zum Datum des Verkaufs/der
Verschrottung berücksichtigt.
Will man die Erträge bzw. Aufwendungen aus
Anlagenabgängen in der Anlagenbuchhaltung führen (Option muss dann auf Ja
stehen), so wird als Betrag zunächst der Restbuchwert vorgeschlagen. Dieser
lässt sich jedoch auf den echten Verkaufswert – auch auf 0,00 Euro – ändern. Es
bleibt dann gewöhnlich eine Differenz auf dem Anlagenkonto stehen. Bevor man
diese als sonstiger betrieblicher Aufwand sbA oder als sonstiger betrieblicher
Ertrag sbE ausbucht, muss man natürlich noch die Abschreibung bis zum Tag des
Verkaufs vornehmen. Die Historie kann z.B. wie folg aussehen:
Im Anlagenspiegel findet man für dieses Anlagengut
dann in der Spalte
Abgänge
den Wert und daneben die Ertragsbuchung, die
mit einem „E“ gekennzeichnet ist. Werden sbA und sbE nicht geführt, so
erscheinen diese natürlich nicht in der Auswertung.
Nachdem eine Zeile mit sbE oder sbA erfasst worden
ist, ist es nicht mehr möglich Abschreibungen für dieses Anlagengut
vorzunehmen!
Um für ein Anlagegut den Abgang zu erfassen, gibt es
folgende Möglichkeiten:
•
Man geht in der Historie und trägt in der letzten Zeile „Abgang“ ein -
eine Auswahl sämtlicher möglichen Arten ist mit
F3
möglich.
•

[...]


---

## Vertretergruppen Variante 2 (Offene Aufträge nach Vertretergruppen)

Vertretergruppen Variante 2 (Offene Aufträge nach Vertretergruppen)
Felder:
Feld
Bedeutung
Vertreter
Nummer der
      Vertretergruppe
Bezeichnung
Name
      der Vertretergruppe
Restwert
Zeigt den offenen Rest eines
      Auftrags, an die Vertretergruppe, in Euro an
Suchmöglichkeiten
Feld
Bedeutung
Warengruppe
Von…
      Bis…
Artikelnummer
Von…
      Bis…
Belegnummer
Von…
      Bis…
Datum
Von…
      Bis…
Lieferzeitraum
Von…
      Bis…
Kundennummer
Von…
      Bis…
Namesanfang
%
Vertreter
Von…
      Bis…
Fakturiergruppe
Von…
      Bis…
Druckstatus
0:
      ungedruckt
1: gedruckt
2: egal
Erledigung
0:
      unbearbeitet
1: teilerledigt
2: abgeschlossen
3: egal
4: nicht
      abgeschlossen
Dispositionsstatus
0:
      undisponiert
2: disponiert
3: egal
Bepreisung
0:
      vollständig
1: unvollständig
2: egal
Umwandlungssperre
0:
      ungesperrt
1: gesperrt
2: egal
Bearbeiterwahl
0:
      alle Belege
1: nur eigene Belege
Formular
0:
      alle Formulare … Nummer
1: nur Formular Nr … Nummer
Aufträge/Storno
0:
      Aufträge
1: Storno-Aufträge
2: egal
Funktionen:
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
Ruft
      den
Pfleger
der Vertretergruppen auf.

---

## Vertreterprovisionsgruppen: Pfleger

Vertreterprovisionsgruppen:
Pfleger
Kopfdaten
Provisionsgruppe
Nummer der
      Provisionsgruppe
Bezeichnung
Bezeichnung der
      Provisionsgruppe
Provisionstyp VERKAUF
Mittels F3 kann dort aus dem Format
VERTPROVFORM
ein Provisionstyp für den Verkauf eingerichtet
      werden
Provisionstyp EINKAUF
Mittels F3 kann dort aus dem Format
VERTPROVFORM
ein Provisionstyp für den Einkauf eingerichtet
      werden
Bezugsgröße VK: pro
Wenn
      man den Provisionstyp im Verkauf
Prov. Mit variablen Mengenbezeug
auswählt, dann ist dieses Feld bearbeitbar. Dort kann man einrichten bei
      welcher Menge in welcher Mengeneinheit die Provisionsgruppe die Provision
      bestimmt.
Bezugsgröße EK: pro
Wenn
      man den Provisionstyp im Einkauf
Prov. Mit variablen Mengenbezeug
auswählt, dann ist dieses Feld bearbeitbar. Dort kann man einrichten bei
      welcher Menge in welcher Mengeneinheit die Provisionsgruppe die Provision
      bestimmt.
Funktionen:
Funktion
Beschreibung
Speichern (F9)
Versucht den Datensatz zu
      speichern
Provisionsgruppenstaffel
      bearbeiten
Wenn
      man im Einkauf oder im Verkauf den Provisionstyp
Staffelprovision
      (OPT-Preis)
oder
Staffelprovision (Preis+ZuAB)
dann kann man
      diese Funktion aufrufen, um in der Auswahlliste der zum Bearbeiten der
      Vertreterprovisionsstaffeln.

---

## Vertreterprovisionsstaffeln

Vertreterprovisionsstaffeln
Wenn man im Einkauf oder im Verkauf auf dem
Vertreterprvovisionsgruppenpfleger
den Provisionstyp
Staffelprovision (OPT-Preis)
oder
Staffelprovision
(Preis+ZuAB)
eingerichtet hat
,
dann kann hier eine
Vertreterprovisionsstaffel angelegt und bearbeitet werden

---

## Vertreterprovisionsstaffeln: Pfleger

Vertreterprovisionsstaffeln:
Pfleger
Kopfdaten
Provisionsgruppe
Nummer der
      Provisionsgruppe
Einkauf / Verkauf
Gibt
      an, ob die Provisionsstaffel für den Einkauf oder Verkauf gültig sein
      soll.
Vertreterklasse
Nummer der
      Vertreterklasse
Rechenart
Mittels F3 kann dort aus dem Format
VERTPR_RECH
eine Rechenart auswählen.
Stufe
Nicht pflegbarer Wert. Zeigt einem
      auf welcher Stufe welche Provision bei welchem Preisabschlag
      gilt.
Provision
Provisionswert der
      Staffel
Preisabschlag
Preisabschlag der
      Staffel
Funktionen:
Funktion
Beschreibung
Speichern (F9)
Versucht den Datensatz zu
      speichern

---

## Vertreterprovisionsgruppen Variante 1

Vertreterprovisionsgruppen
Variante 1
Felder:
Feld
Bedeutung
Nummer
Nummer
      Vertreterprovisionsgruppe
Bezeichnung
Bezeichnung der
      Vertreterprovisionsgruppe
Prov.Formel VK
Provisionsformel im
      Verkauf
Prov.Formel EK
Provisionsformel im
      Einkauf
Suchmöglichkeiten
Feld
Bedeutung
Nummer
      (Provisionsgruppennummer)
Dieser Filter erlaubt einem die
      Auswahlliste nach bestimmten Provisionsgruppen zu durchsuchen
Funktionen:
Funktion
Beschreibung
Ändern
(F5)
Ruft
      den
Pfleger
der
      Vertreterprovisionsgruppen auf im Ändernmodus auf.
Ansehen
(F6)
Ruft
      den
Pfleger
der
      Vertreterprovisionsgruppen auf im Ansehenmodus auf.
Löschen
(F7)
Ruft
      den
Pfleger
der
      Vertreterprovisionsgruppen auf im Löschenmodus auf.
Neu
(F8)
Ruft
      den
Pfleger
der
      Vertreterprovisionsgruppen auf im Neumodus auf.
Vertreter-Provisionsstaffeln
Öffnet die Anwendung
      Vertreterprovisionsstaffeln auf.
Referenz-Preise
      Vert.Prov.
Öffnet die Anwendung
      Referenz-Preislisten auf.

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

## Importierbare Vorgänge

Importierbare Vorgänge
Folgende
Vorgänge können zurzeit angelegt oder bearbeitet werden.
Hinweis:
Einige davon sind ausschließlich lesbar, wenn das
Kennzeichen „useCS“ im ImportVorgStamm auf 1 steht.
Vorgang
Vorgangs-
klasse
Anlegen
Bearbeiten
Angebot
100
ü
ü
Dauerauftrag
300
ü
*
û
Auftrag
400
ü
ü
Auftrag zu Ladeschein
      zu Lieferschein oder Rechnung
500
ü
û
Mit Ladeschein aus Auftrag zu
      Rechnung/Lieferschein
500
ü
û
Ladeschein
500
ü
ü
Lieferschein
600
ü
ü
Rechnung
700
ü
ü
Storno-Rechnung
790
ü
*
û
Gutschrift
800
ü
ü
Storno-Gutschrift
890
ü
*
û
Bestellanfrage
1100
ü
ü
Bestellung
1400
ü
ü
Bestellstorno
1490
ü
*
û
Bestellung zu Eingangsladeschein
      oder Eingangsrechnung
1500
ü
ü
Eingangsladeschein
1500
ü
ü
Eingangslieferschein
1600
ü
ü
Eingangsrechnung
1700
ü
?
Eingangsrechnung-Storno
1790
ü
*
û
Eingangsgutschrift
1800
û
ü
Permanente Inventur
5055
ü
û
Inventurbeleg
n/a
ü
û
Lagerplatzumbuchung
5100
ü
û
Lagerumbuchung
5110
ü
û
Artikelumbuchung
5120
ü
û
LVS
5150
ü
*
ü
*
Produktion
5220
ü
ü
*
*
= ausschließlich mit
useCS=1

---

## Ladeschein

Ladeschein
Ladescheine können per Neuerfassung angelegt werden.
Dem Ladeschein können per Teildisposition Auftragspositionen hinzugefügt
werden.
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      Ladescheins
Erstdruck
F9
Erstdruck eines
      Auftrages
Formulardruck
F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
F5
Korrektur eines
      Ladescheins
Kopieren
CF8
Kopieren des Ladescheins für einen
      auszuwählenden Kunden
Vorschau
F11
Druckvorschau
Stornieren
F7
Stornieren (Löschen) des
      Ladescheins
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Re./ Lie. aus Ladeschein
Umwandeln in eine Rechnung oder in
      ein Lieferschein
Scanner Ladeschein zu
      Lieferschein
Wandelt eine Ladeschein, der mit dem
      Scanner erfasst worden ist, in ein Lieferschein um
Wiedervorlage
CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Wiedervorlage bearbeiten
Wiedervorlagevermerk
      bearbeiten
Arbeitsregel ändern
manuelle Änderung von
      Weiterverarbeitungsparametern

---

## Vorgangsdruckklassen

Vorgangsdruckklassen
Hauptmenü
Administration
Drucker
Vorgangdruckklassen
oder Direktsprung
[VRGD]
Zuordnung der Vorgangsdruckerklassen zu den einzelnen
Vorgangsklassen, wie z.B. Nr. 600 für Lieferschein
Definieren Sie zu welcher Vorgangsklasse/Unterklasse
diese Druckklasse gültig sein soll.
Spalte
Beschreibung
Vorgangsklasse
Vorgangsklasse
Nummer der Unterklasse
Unterklasse
Unterklassenbezeichnung
RohwareAbr.Typ
Rohwaren-Abrechnungstyp
Verwendung
Verwendung des Drucks
Gültig ab
Gültigkeitsdatum dieser
      Definition
Funktion Formulare
/ Drucker zuordnen
Hauptmenü
Administration
Drucker
Vorgangdruckklassen
oder Direktsprung
[VRGD]
Mit Hilfe der Funktion
Formulare / Drucker zuordnen F5
definieren
Sie, auf welchem Drucker, mit welchem Schacht, mit welchem Formular der Druck
mit/ohne openTRANS mit/ohne Mailversand wie oft gedruckt werden soll.
Spalte
Beschreibung
Nr
Laufende Nummer
Formular
Formularnummer
Formularbezeichnung
Schacht
Druckerschacht. Dieser kann z.B. zur
      Verwendung von Papieren unterschiedlicher Farben oder Briefköpfe verwendet
      werden.
0)   Keine
      Schachtauswahl
1)   Schacht 1
2)   Schacht 2
3)   Erste Seite auf
      Schacht 1 weitere auf Schacht 2
4)   Erste Seite auf
      Schacht 2 weitere auf Schacht 1
Drucker
Druckernummer
Druckerbezeichnung
Effektsteuerung
Es
      stehen drei Möglichkeiten zur Auswahl:
1
      keine Effektsteuerung
2 Ladeliste (im Standard keine Auswertung)
3
      Lagerabholschein
„keine Effektsteuerung“ ist hier die
      Vorbelegung für das Feld.
Lagerabholschein bewirkt, dass
      dieses Formular nur dann gedruckt wird, wenn es unter den Artikeln
      mindestens einen Artikel gibt, der als Lagerartikel gekennzeichnet ist.
      Siehe dazu
weitere Funktionen der
      Tresenkasse
.
Raffung
Makro
Makro welches vor dem Druck
      ausgeführt wird. Übergabe von bis zu 4 Parameter. Makroname und Parameter
      müssen mit einem Leerzeichen getrennt sein.
Beispiel: Makroname Parameter1

[...]


---

## Streckenerfassung

Streckenerfassung
Menü: Warenverkauf
Übergreifend
Vorgangsmappe (Direktsprung: [VGKL])
Mit der Streckenerfassung des Referenz-ERP-Systems können
Streckengeschäfte schnell und effizient abgewickelt sowie nachvollzogen werden.
Durch die sehr flexiblen
Profileinstellungen
sind die
Funktionalitäten sowie die Optik der Streckenerfassung individuell einstellbar
und damit für viele Bereiche verwendbar.
Generell kann eine Strecke von mehreren Personen
aufgerufen werden, soll dies unterbunden werden, muss der Steuerparameter „
795
“ angepasst werden.

---

## UFLD-Feldliste

UFLD-Feldliste
Zum Laden der UFLD-Felder in der
Streckenerfassungsmaske müssen die Felder nur im Profil eingetragen werden. Alle
unter „
Verwendbare UFLD-Felder
“ angegebenen
Felder werden zurzeit automatisch mit geladen.
Sollen weitere UFLD-Felder in der Streckenerfassung
angezeigt werden, so kann dies über eine private Prozedur geschehen. Die Felder
müssen dabei nach folgendem Schema aufgebaut sein „ufld_“ + Nummer des
UFLD-Feldes.
z.B. für das Feld 1101
vs.FahrerNummer as
ufld_1101
In diesem Fall hat das Feld 1101 auch eine Itembox,
aus diesem Grund wird noch ein weiteres Feld auf der Streckenerfassungsmaske
angelegt. Um dieses beim Laden der Daten auch zu befüllen muss die Ladeprozedur
ein weiteres Feld zurückgeben, welches folgendermaßen aufgebaut ist „ufld_“ +
Nummer des UFLD-Feldes + „_“ + Name des Returnfeldes.
z.B. für das Feld 1101
fahrer.fahrerbezeich as
ufld_1101_fahrerbezeich
Verwendbare
UFLD-Felder
Hier ist eine Liste aller bisher verwendbaren
UFLD-Felder. Der Alias „vs“ im Select-Statement wird für den Vorgangstamm
verwendet. In der Spalte Itemboxfeld steht der Name des Returnfeldes der
dazugehörigen Itembox.
Nr.
Name
Select-Statement
Itemboxfeld
17
Sprache
vs.SprachNummer as
      ufld_17
SprachBezeich
108
VersandAdr.
vs.V_VersAdressId as
      ufld_108
110
Wiegenummer
vs.V_WiegeNummer as
      ufld_110
117
DA
      Anfang
vs.V_DauerAnfDat as
      ufld_117
118
DA
      nächtst.Termin
vs.V_DauerNaeDat as
      ufld_118
119
DA
      Periode
vs.V_DauerPeriode as
      ufld_119
150
Umwandl.Sperre
vs.V_SperrUmwand as
      ufld_150
175
KuAuftrDatum
vs.V_EDIKuAuftragsDatum as
      ufld_175
176
KuAuftrNummer
vs.V_EDIKuAuftragsNummer as
      ufld_176
404
Einzelz Kokore
vs.V_KennzDrRechKokore as
      ufld_404
435
Arbeitsregel
vs.ArbeitsRegel as
      ufld_435
wfs_name
456
Transportweg
vs.V_TransportWeg as
      ufld_456
457
Verfahrensart
vs.V_VerfahrensArt as
      ufld_457
470
Vorbel. Ziel Herkunft
      Land
vs.HerkunftZie
[...]


---

## Allgemeine Informationen

Allgemeine Informationen
Hier werden weitere allgemeine Informationen
dargestellt.
Itemboxparameter
Itemboxparameter
Es gibt zurzeit einen Itemboxparameter der
standardmäßig bei jeder Itembox gesetzt wird
Parameter
Beschreibung
STRECKE_ANWENDUNGSTYP
Dieser Parameter gibt an um was für
      einen Anwendungstyp es sich handelt. Dies ist Abhängig von der aufrufenden
      Auswahlliste.
Die
      Kodierung des Wertes ist
10 – Unbekannt, die Maske wurde von
      keiner bekannten Auswahlliste aufgerufen.
20 – Einkauf, die Maske wurde von
      der „Streckenerfassung – Einkauf“ aus aufgerufen.
30 – Verkauf, die Maske wurde von
      der „Streckenerfassung – Verkauf“ aus aufgerufen.

---

## Beispiele

Beispiele
Hier werden Beispiele für Einstellungen des
Streckenprofils dargestellt.
Gültigkeit
Gültigkeit
Bei den
Gültigkeiten
gilt
generell, ein eingetragener Wert hat eine höhere Priorität als ein nicht
vorhandener Wert. Ausschlaggebend dafür sind die Felder „Klasse“, „Unterklasse“
und „Grid“. Zu beachten ist dabei, dass die Unterklasse vor dem Grid zählt
Beispiel 1:
Klasse
Unterklasse
Grid
700
In diesem Beispiel befinden sich nur zwei
Gültigkeiten. Da bei beiden Einträgen keine Unterklassen und kein Grid‘s
eingetragen wurden, sind diese in diesem Beispiel uninteressant.
Klasse 400
Klasse
700
Da kein Eintrag zur Klasse 400 existiert, wird der
      Eintrag ohne Klasse verwendet.
Klasse 700
Klasse
700
Der Eintrag zur Klasse 700 existiert, deswegen wird
      dieser verwendet.
Beispiel 2:
Klasse
Unterklasse
Grid
3
700
700
3
Dieses Beispiel behandelt die Klasse und das Grid.
Damit kann für bestimmte Klassen in bestimmten Grids eine Gültigkeit eingetragen
werden.
Klasse 800, Grid 1
Klasse
Grid
3
700
700
3
Da kein Klasseneintrag existiert und das Grid nicht
      passt, wird der erste Eintrag verwendet.
Klasse 800, Grid 3
Klasse
Grid
3
700
700
3
Hier passt wiederrum das Grid, die Klasse ist beim
      zweiten Eintrag egal, deswegen wird dieser Eintrag verwendet.
Klasse 700, Grid
      1
Klasse
Grid
3
700
700
3
In
      diesem Fall existiert ein Eintrag mit der passenden Klasse, fürs Grid
      jedoch nicht. Aus diesem Grund wird der dritte Eintrag
      verwendet.
Klasse 700, Grid
      3
Klasse
Grid
3
700
700
3
Hier
      passen sowohl die Klasse als auch das Grid, aus diesem Grund wird der
      vierte Eintrag verwendet.
Beispiel 3:
Zeile
Klasse
Unterklasse
Grid
1
2
700
2
3
700
17
4
700
17
3
5
800
6
800
9900
Dieses Beispiel verwendet alle Felder, die für die
Bestimmung der Gültigkeit gebraucht werden.
Klasse 700, Unterklasse 0, Grid 1
Klasse
Unterklasse
Grid
700
2
700
17
700
17
3
800
800
9900
Hier wird die erste Gültigkeit verwendet, da die

[...]


---

## Vorbelegung

Vorbelegung
Für die Vorbelegung innerhalb der Strecke wird eine
private Prozedur benötigt. Dabei müssen jedoch einige Richtlinien beachtet
werden.
IN-Parameter
Übergabefelder
RESULT-Klausel
Beispielprozedur
IN-Parameter
Folgende IN-Parameter werden beim Aufruf der Prozedur
übergeben.
Parameter
Beschreibung
in_KlammerNr
Klammernummer der
      Strecke.
in_Grid
Nummer der Datentabelle.
in_Occ
Zeile innerhalb der
      Datentabelle.
in_Profil
Name
      des aktuell verwendeten Profils.
in_Spalte
Name
      der Spalte, durch die die Prozedur aufgerufen wird.
in_Wert
Wert
      der übergebenen Spalte.
in_OccChange
0    Die Prozedur
      wurde durch ein „Ausführungsfeld aufgerufen.
1    Die Prozedur
      wurde durch eine neue Zeile aufgerufen.
Übergabefelder
Die
Übergabefelder
können innerhalb des Profils festgelegt werden. Diese werden vor dem Aufruf der
Prozedur in eine globale Tabelle geschrieben. Aus dieser Tabelle können dann die
übergebenen Werte innerhalb der Prozedur wieder ausgelesen werden.
Die verwendete Tabelle für die Übergabeparameter nennt
sich „GTT_AMIC_IDENT“. Folgende Spalten werden für die Übergabe verwendet.
Spalte
Beschreibung
TYP
Da
      die Tabelle nicht nur in der Streckenerfassung verwendet wird, gibt dieses
      Feld den Datensatztyp an. Für die Übergabewerte wird der Typ
      "STRECKENERFASSUNG_VORBELEGUNGSPARAMETER" verwendet.
TEXT1
In
      dieser Spalte befindet sich der Spaltenname des übergebenen
      Feldes.
TEXT2
In
      dieser Spalte befindet sich der Wert des übergebenen Feldes.
Zum Auslesen aus der Tabelle kann dann folgendes
Statement verwendet werden.
Select cast(text2 as
char(255))
Into dc_ArtikelNummer
from gtt_amic_ident
where typ = 'STRECKENERFASSUNG_VORBELEGUNGSPARAMETER'
and text1 =
'Artikelnummer'
Dabei sollte nicht vergessen werden, den Wert in den
richtigen Datentypen umzuwandeln (CAST).
RESULT-Klausel
Die „RESULT-Klausel“ ist die Beschreibung, welche
Daten zurückgegeben werden.
Parameter
Besc
[...]


---

## Auswahllisten

Auswahllisten
Für die Streckenerfassung stehen unterschiedliche
Standardauswahllisten zur Verfügung.
Streckendisposition (Liste)
Diese Auswahlliste zeigt für jede Strecke nur eine
Zeile an, dabei werden unter anderem die Kunden, Belegnummern und Artikel als
zusammengesetzte Liste angezeigt.
In den Allgemeinen muss beachtet werden, dass diese
Auswahlliste nicht die schnellste ist, da sie intern viele Berechnungen machen
muss. Dadurch können aber unter anderem alle Kunden, Belege und Artikel
angezeigt werden.
Bei der Auswahl sollte deswegen beachtet werden, dass
möglichst kleine Streckenbereiche ausgewählt werden, möglichst nicht mehr als 10
Strecken gleichzeitig.
Kriterium
Beschreibung
Strecke
Streckennummernliste
Enthält Kunde
Die
      Strecke muss den angegebenen Kunden enthalten.
Enthält Artikelnummer
Die
      Strecke muss die angegebene Artikelnummer enthalten.
Enthält
      Artikelbezeichnung
Die
      Strecke muss die angegebene Artikelbezeichnung enthalten.
Enthält Jahr
Die
      Strecke muss das angegebene Jahr enthalten.
Enthält Periode
Die
      Strecke muss die angegebene Periode enthalten.
Enthält Vorgangsklasse
Die
      Strecke muss die angegebene Vorgangsklasse enthalten.
Enthält Kontrakt
Die
      Strecke muss den angegebenen Kontrakt enthalten.
Enthält Lager
Die
      Strecke muss das angegebene Lager enthalten.
Enthält ausschließlich
      Lager
Die
      Strecke darf
ausschließlich
das angegebene Lager
      enthalten.
Container
Streckentext
Mengendifferenz
Enthält Belegdatum
Die
      Strecke muss das angegebene Belegdatum enthalten.
Nur
      eigene Belege
Von
      Streckenstatus
Bis Streckenstatus
Hiermit kann die Strecke nach dem
Status
eingegrenzt
      werden. Wird dabei nur der „Von“ oder „Bis“ Status angegeben gilt nur der
      angegebene Status.
Werden beide Felder angegeben, wird
      eine Bereichsauswahl ausgeführt. (z.B. vom Status 1 bis zum Status
      5)
Bei
      nicht funktionieren dieser Kriterien
[...]


---

## Datentabellen

Datentabellen
Das Referenz-ERP-System bietet dem Bediener durch diverse
Zeilen- oder Zellenorientierte Funktionen größtmögliche Effizienz bei der
Bearbeitung der Streckengeschäfte.
Informationen zu Feldern mit Doppelklick
Funktionen
Spalte
Beschreibung
Typ
Belegnr
Öffnen des ausgewählten Beleges zur
      Bearbeitung (s.
Vorgang
      korrigieren
)
Kunde
Öffnen der Kundenstammmaske, hier
      können nähere Informationen über den Kunden nachgelesen oder die Daten
      aktualisiert werden. Änderungen werden automatisch
      übernommen.
Name
Öffnen der im Profil definierten
      AIS-Maske (AIS Gruppe Kunden).
Ort
Durch Doppelklick auf das Feld Ort
      wird dieses farblich markiert. Hier wird entsprechend der
      Auswahlreihenfolge eine Liste von Orten und Adressen zusammengestellt, die
      über den Kontextmenüpunkt „Route anzeigen“ die  Routenplanung in MS
      MapPoint öffnet
Artikelnr
Öffnen der Artikelstammmaske, hier
      können nähere Informationen über den Artikel nachgelesen oder die Daten
      aktualisiert werden. Änderungen werden automatisch übernommen.
Artikel
Öffnen der im Profil definierten
      AIS-Maske (AIS Gruppe Artikel).
P.Anz
Öffnen der Maske
Partiemengenverteilung
, in der
      die Gesamtmenge des jeweiligen Vorgangs auf entsprechende Partien verteilt
      werden kann. Sind diesem Vorgang Partien zugordnet steht die die Anzahl
      der Partien in der Spalte P.Anz.
Partienr
Öffnen der Partiestammmaske, hier
      können nähere Informationen über die Partie nachgelesen oder die Daten
      aktualisiert werden. Änderungen werden automatisch übernommen.
Partie
Öffnen der im Profil definierten
      AIS-Maske (AIS Gruppe Partien).
Menge
Durch Doppelklick auf das Feld Menge
      wird dieses farblich markiert. Es werden die Summen der Felder
      Gebindeanzahl, Gewicht und Menge für die markierten Felder aller drei
      Vorgangsgrids berechnet und als MousOverEreignis der Spalte Menge
      angezeigt. Sind Felder de
[...]


---

## Formulararchiv

Formulararchiv
Die Funktionalität „
Formulararchivgruppe
“ findet in der
Streckenerfassung Anwendung. Im Allgemeinen gilt dabei, wird etwas innerhalb der
Streckenerfassung archiviert, bekommt der Archiveintrag eine Gruppenzuordnung
zur Strecke.
Das findet zurzeit bei folgenden Funktionen statt:
-
Druck von Reporten
-
Druck von Vorgängen
-
Import aus der Formulararchivanzeige (Strg + F12)

---

## Kontextmenüs

Kontextmenüs
Über das Kontextmenü der Streckenerfassung sind
diverse Funktionen ausführbar. Sie ermöglichen aus der Streckenerfassung heraus
eine schnelle und komfortable Bedienung diverser Funktionen. Im Zusammenspiel
mit den
Events der Grids
ergibt sich eine
sehr hohe Bedienerperformance durch die sehr flexiblen Funktionsstrukturen aus
der Streckenerfassung heraus.
Speichern
Vorgang
korrigieren
Vorgang drucken
Sammeldrucken
Position
stornieren
aus der Strecke
nehmen
Avis markierte
Zeilen
Neuer Kontrakt
Archiv anzeigen
Lademittel
zuordnen
Route zurücksetzen
Route anzeigen
Position als
Ladeeinheit
Kontraktartikelausweichliste
bearbeiten
Strecke
vervielfältigen
Rohware
Einige der Kontextmenüpunkte sind sehr speziell,
teilweise Vorgangs- und/oder Feldgebunden.
So wird z.B. der Menüpunkt
Kontraktartikelausweichliste
bearbeiten
nur angezeigt wenn es sich um einen Kontrakt handelt, für
diesen eine Kontraktartikelausweichliste hinterlegt ist (Feld Artikelnummer wird
farblich angezeigt) und der Cursor über dem markierten Feld im
GFV
positioniert wird während man mit der rechten Maustaste das Kontextmenü
öffnet.
Speichern
Alle Änderungen in den Grids werden gespeichert
Vorgang korrigieren
Über diesen Kontextmenüpunkt wird die
Vorgangsbearbeitungsmaske (je nach Vorgangstyps) des gerade aktiven Vorgangs
geladen. Je nach
Gültigkeit
wird der
Vorgang dann zum Bearbeiten oder Ansehen geöffnet ohne die
Streckenerfassungsmaske zu verlassen.
Im Korrekturmodus lässt sich der betreffende Vorgang
dann korrigieren. Die gemachten Änderungen werden dann automatisch
übernommen.
Vorgang drucken
Aus der Maske  Streckengeschäft kann der Druck
des jeweils gerade aktiven Vorgangs gestartet werden.
Sammeldrucken
Das Sammeldrucken dient dem Drucken mehrerer
Auswertungen hintereinander. Bevor das Sammeldrucken gestartet werden kann,
müssen alle Daten gespeichert werden.
Danach wird eine zusätzliche Registerkarte geöffnet.
Auf dieser finden sich alle Auswertungen des akt
[...]


---

## Kopfbereich

Kopfbereich
Im Kopfbereich wird als Registerkartenbezeichnung der
Profilname
angezeigt.
Des Weiteren stehen Informationen aus dem
Streckenstammsatz
(Container, Streckennummer, Streckenbezeichnung) zur Verfügung. Die
Werte sind jedoch nur bei der Neuerfassung eingebbar.
Sollen die Werte des Streckenstammsatz gepflegt
werden, steht im Kopfbereich ein Button zur Verfügung (
Profileinstellung
) über
denn der Streckenstammsatz aufgerufen werden kann.

---

## Positionsbeziehungsübersicht

Positionsbeziehungsübersicht
Die Übersicht dient der vereinfachten Darstellung
innerhalb einer Strecke. Die Daten werden dabei in den Datentabellen nicht mehr
komplett angezeigt, sondern entsprechend der Beziehung zur ersten
Datentabelle.
Wird in der ersten Datentabelle ein Datensatz
ausgewählt, aktualisieren sich die Datensätze in den beiden unteren
Datentabellen und zeigen nur die Positionen, welche mit dem entsprechenden
Datensatz in der ersten Datentabelle verknüpft sind.

---

## Positionsstammsatz

Positionsstammsatz
Neben dem Streckenstammsatz können auch für einzelne
Positionen Stammsätze hinterlegt werden. Dadurch lassen sich für jeden Vorgang
unterschiedliche Informationen gegenüber dem Streckenstammsatz
speichern.
Es lässt sich dabei ein einzelner oder eine Liste von
Positionsstammsätzen öffnen. Über die Funktion  „
Sonderfunktionen ->
Positionsstammsatz
“ öffnet man den Positionsstammsatz für die aktuell aktive
Zeile. Mit der Funktion „
Sonderfunktionen -> Markierte
Positionsstammsätze
“ wird eine Liste von Stammsätzen erstellt und geöffnet,
die die aktuell markierten Elemente enthält.
In beiden Fällen wird ein neuer Positionssatz für jede
Zeile angelegt, bei der bisher noch kein Positionssatz existierte.
Wenn eine Zeile mit einem Positionsstammsatz betreten
wird, besteht die Möglichkeit diesen Datensatz über einen Button aufzurufen.
Dieser Button erscheint neben dem Button der Vorgangsklammer, wenn dies im
Profil eingestellt ist.

---

## Private Streckenerfassungsaufrufe

Private Streckenerfassungsaufrufe
Um die Streckenerfassung aufzurufen kann eine
private Funktion eingerichtet werden. Dabei hat der Controlstring folgende Form:
jpl
streckenerfassung_auftragaufruf ":pEinkaufVerkauf" ":h.klammernr$"
":pProfil"
Diese jpl-Funktion hat 3 Parameter:
Parameterbezeichnung
Beschreibung
EINKAUFVERKAUF
1
      => Einkauf
2
      => Verkauf
MODUS
"KONTRAKTSTAMM" => Mit diesem
      Parameter wird die Streckenerfassung mit der ersten gefundenen
      Streckennummer des Kontrakts aufgerufen. Die Kontrakt ID wird dafür aus
      dem ersten Feld (ID1) der Auswahlliste geholt. Zu dem Kontrakt wird dann
      die Streckennummer ermittelt, wird keine Nummer gefunden wird die
      Streckenmaske nicht geöffnet.
"AUFTRAGMITMAPPE" => Mit diesem
      Parameter kann die Streckenerfassung für einen Vorgang geöffnet werden.
      Befindet sich der Vorgang bereits in einer Strecke, wird diese aufgerufen.
      Ansonsten wird der Vorgang einer Strecke mit der Nummer des Vorgangs
      zugeordnet und aufgerufen.
Leerstring, ID1, ID2, ID3, ID4 =>
      Die Streckennummer wird aus dem angegebenen ID Feld der Auswahlliste
      ermittelt. Bei einem Leerstring wird die ID1 verwendet.
Numerischer Wert => Die
      Streckenerfassung wird mit der übergebenen Nummer aufgerufen.
PROFIL
Hier
      wird das zu verwendende Streckenerfassungsprofil festgelegt.
Wird
      keins übergeben, wird versucht dieses über die Einrichteparameter
      STRECKENPROFIL_EINKAUF für Einkauf bzw. STRECKENPROFIL_VERKAUF für Verkauf
      zu bestimmen.

---

## Profile

Profile
Die Maske dient zur Konfiguration der
Streckenerfassung
. Es können
diverse Einstellungen pro Profil in den Registerkarten der Maske konfiguriert
werden.
Neben den Einstellungen des optischen
Erscheinungsbildes der Maske (Breite, Anzahl der Zeilen der einzelnen Grids,
etc.) sind viele spezielle Einstellungen möglich.
So können diverse Einstellungen gesetzt werden, die
die Verarbeitung der Streckenerfassung beeinflussen. Dies ermöglicht ein
Zusammenspiel mit anderen Programmen wie Microsoft MapPoint, Branchen-ERP
Etikettendruck, Crystal Reports etc.
Folgende Registerkarten stehen für die Einstellungen
zur Verfügung.
Allgemein
Allgemein 2
Griddefinition
Auswertungen
Kontrakte
Kopiervorlagen
Benutzerfelder
Addonfelder
Buttons
Registerkarte Allgemein
Hier können allgemeine Einstellungen der
Streckenerfassung definiert werden.
Feld
Beschreibung
Profil
Bezeichnung des Profils (Wird im
      Kopfbereich der Streckenerfassungsmaske angezeigt)
Standardprofil
Ein
      Profil kann als Standardprofil gekennzeichnet werden. Dieses wird unter
      anderem in Auswahllisten verwendet.
Maskenbreite
Die
      Breite der Maske Streckenerfassung
AIS
      – Breite
Befindet sich die Maske nicht im
      Vollbildmodus, kann hiermit die Breite der Maske vergrößert werden.
      Dadurch ist es möglich zusätzliche Informationen über das
AIS-System
anzuzeigen.
Vollbild
Hiermit kann eingestellt werden,
      dass die Maske im Vollbildmodus angezeigt wird.
Registerkarte (Zeile /
      Spalte)
Hiermit kann die Position der
      Registerkarte festgelegt werden. Default mäßig stehen die beiden Wert auf
      0.
Nur
      wenn in
beiden
Feldern ein Wert größer 0 eingetragen ist, wird die
      Registerkarte verschoben.
Abhängigkeit
Hier
      kann die Abhängigkeit der Daten festgelegt werden.
-
Artikelabhängig
Die
      Daten werden bei dieser Einstellung abhängig von der ersten Datentabelle
      ermittelt. D.h. für die zweite und dritte Datentabelle sind die Artikel

[...]


---

## Planungsregister

Planungsregister
Im Planungsregister können n:m Einkauf-Verkauf -
Zuordnungen verwaltet werden. Wie auch in den anderen Bereichen steht an dieser
Stelle zunächst die Streckennummer und die Streckenbezeichnung im oberen Bereich
bereit. Auf der Streckennummer können per F3 Auswahl die vorhandenen Strecken
ausgewählt werden.
Dier Bildschirm ist hier in einen separaten Einkauf
und Verkauf Bereich getrennt. Zusätzlich dazu gibt es den Bereich der Reporte,
einen individuell einrichtbaren Bereich für spezifische Kundenrelevante
Informationen und einen Übersichtsbereich der Gesamtstrecke.
Im Einkauf-/Verkaufsbereich stehen folgende Auswahl-,
wie auch Anzeigeelemente bereit:
Icon
Feld/Knopf
Information
Blätterknopf
vorwärts/rückwärts
Mit
      diesen Blätterknöpfen kann individuell im Einkaufs- wie auch
      Verkaufsbereich zwischen den Elementen dieses Bereiches hin und her
      geblättert werden. Es gibt hier eine farbliche Trennung zwischen den
      Kontraktelementen und den Lieferelementen.
Auswahlknopf
(beziffert mit der
      Position)
Zwischen den Blätterknöpfen gibt es
      dann noch die Möglichkeit per F3 Auswahl auf die Elemente des Ver- bzw.
      Einkauf direkt zuzugreifen.
Kontrakt Knopf
Der
      Kontraktknopf erlaubt es auf schnelle Weise direkt aus dem Kontraktstamm
      einen  Kontrakt in die Strecke zu ziehen. Dieser Knopf liefert im
      Einkauf alle Einkauf und im Verkauf alle Verkaufskontrakte.
Knopf Engagement
Der
      durch eine Einrichtung im Profil automatisch erscheinende Knopf Engagement
      ruft eine Kontrakt (bzw. Vorgangs) Übersicht zur Darstellung der
      jeweiligen Gegenposition auf.
Hinzufügen Knopf
Dieser Bereich erlaubt eine direkte
      Neueingabe oder Hinzufügung eines beliebigen Vorgangs, der dann in der
      aufgehenden Auswahl zugeordnet werden kann.
Duplizierknopf
Mit
      diesem Knopf kann der komplette Vorgang dupliziert und anschließend
      angepasst werden.
Bearbeitungsknopf
Dieser Knopf st
[...]


---

## Einrichtung

Einrichtung
Einrichtung der Vorkasse
Steuerparameter die von der Vorkasse ausgewertet und
Benutzt werden.
•
Kreditlimit-Prüfung mit
Auftrag/Bestellung(SPA 234)
•
Vorkasse
Ladescheinunterklasse(SPA 693)
•
Vorkasse Auftragsunterklasse(SPA
694)
•
Ladeschein ins Kreditlimit einberechnen(SPA 695)
Einrichterparameter auf der Vorkasse
Erfassungsmaske
•
Preisaufschlag/Abschlag für die Lieferungssorte
Bei Rohwarenlieferungen kann
hier schon ein Aufschlag für die Qualitäten eingetragen werden. Dieser wird auf
der Maske angezeigt und kann dort abgeändert werden.
Benötigte Vorgangsklassen und Unterklassen
Vorgangsklasse
Unterklasse
Bedeutung
100
egal
Angebot
400
Siehe SPA Einstellung
      694
Auftrag
500
Siehe SPA Einstellung
      693
Ladeschein
600
9999
Rohwarelieferschein
660
egal
Kontrakt

---

## Beispiel einer Abwicklung im Modul Strecke (Mappe)

Beispiel einer Abwicklung im Modul Strecke (Mappe)
Um die Vorkasse in der Strecke zu benutzen sollten Sie
sich erstmals mit der
Streckenerfassung
generell auseinandersetzten. Die
für die Vorkasse benötigten Funktionen der Streckenerfassung sind [STRECKE] für
die Strecke und [VMAPP] für das
Streckenprofil
.
Formulare oder Reporte die ausgedruckt werden
sollen werden im Streckenprofil hinterlegt.
Um mit der Vorkasse in der Strecke[STRECKE] zu starten
wird mit der Taste F8 eine neue Strecke angelegt.
Als erstes wird ein Angebot in der
Streckenerfassungsmaske angelegt. Dies passiert in der obersten Tabelle. Hier
kann das Angebot direkt erfasst werden, oder es wird in der Datentabelle im Feld
Belegnummer ausgewählt wobei das Feld Klasse auf 100 gesetzt werden muss.
Als nächstes wird der Kontrakt der Strecke
hinzugefügt, dazu wird in das Feld Klasse  660 eingetragen sowie die
Unterklasse und die Belegnummer eingetragen. Jetzt ist der Kontrakt der Strecke
hinzugefügt worden.
Als nächstes wird in der Strecke ein Auftrag über die
Kontraktmenge erzeugt.
Nachdem der Auftrag erstellt worden ist kann jetzt der
Ladeschein erstellt werden. Dazu klicken Sie bitte den Auftrag an drücken dann
wieder die rechte Maustaste jetzt wählen Sie Vorkasse/ Auftrag aus jetzt können
Sie den Ladeschein erstellen. Nachdem der Ladeschein erstellt worden ist, wird
dieser auch in der Strecke zu sehen sein.
Ladeschein Erzeugung
Maskenfelder
Bedeutung
Kontrakt
Gewählter Kontrakt
Kunde
Kontraktkunde
Artikel
Kontraktartikel
Kreditlimit
Hier
      wird das aktuelle Kreditlimit aufgeteilt nach den einzelnen Faktoren
      angezeigt. Des Weiteren wird die Belastung des Kreditlimits durch den neu
      zu erstellenden Lieferschein mit einberechnet und angezeigt.
Abw.
      Lieferanschrift
Hier
      kann eine abweichende Lieferanschrift angegeben werden.
Kontraktpreis
Preis des Kontraktes
Auftrag
Nummer des gewählten
      Auftrages
Auftrags Menge
Auftrags Menge
Offene Menge
Noch

[...]


---

## Auftragsauswahl

Auftragsauswahl
In der Waage kann man auf dem Feld Kunde Vorgänge
(z.B. Aufträge oder auch Bestellungen) auswählen, je nachdem welche IB auf dem
Feld aktiv ist (siehe
Vorlage
und
Einrichterparameter
). Diese IB ist
auch individuell einrichtbar.
Um zu verhindern, dass gesperrte Aufträge ausgewählt
werden, wurde eine Prüfung eingebaut.
Ist im ausgewählten Vorgang eines der
Sperrkennzeichen für die Weiterverarbeitung, Bearbeitung oder Umwandlung
gesetzt, dann erscheint eine Fehlermeldung und man ist gezwungen was anderes
auszuwählen. Ist dem Auftrag ein Kontrakt zugeordnet, so wird dieser im
Kontraktfeld mit angezeigt. Es ist möglich das Feld gegen eine Eingabe zu
sperren. Das Verhalten kann im Waagenprofil auf der
Registerkarte Vorgang
geändert werden. Das
Ändern des Kontraktes führt zur Abwahl des Auftrages.

---

## Verkaufskontrakt (1) / Einkaufskontrakt (11)

Verkaufskontrakt (1) / Einkaufskontrakt (11)
In der Anwendung Kontrakte kann man z.B.
Verkaufskontrakte mit F8 anlegen, wenn man als Kontraktklasse den
Verkaufskontrakt (Klasse 1) auswählt.
Man gibt danach die wichtigen Informationen zu diesem
Kontrakt ein, wie Kunde, Kontraktnummer, Standardkontrakt-Variante, Laufzeiten.
Wenn diese Maske gefüllt ist, kann über
F2
die Kontraktartikelmaske für die
Artikelangaben zum Kontrakt geöffnet werden. Dort werden Artikelnummer,
Kontraktmenge und Kontraktpreis angegeben.
Nachdem nun ein Verkaufskontrakt angelegt wurde, kann
man in der Waage z.B. mit
F7
eine
Warenausgangswiegung starten. Der neu angelegte Kontrakt ist nun in der
F3-
Auswahl des Feldes Kontrakt enthalten.
Die Angaben wie Kunde und Artikel werden aus dem Kontrakt in die Waagenmaske
übernommen.
Nachdem beide Wiegungen durchgeführt und die Wiegung
abgeschlossen (
F11
) wurde, kann nun
ein Vorgang (
F6
) erzeugt werden. Es
wird dabei z.B. ein Lieferschein erzeugt, wenn auf der Maske in dem Feld für die
Lohnklasse des Warenausganges eine 600 steht.
Über
Vorgang editieren
F5
kann man sich den erzeugten Vorgang (in
diesem Beispiel den Lieferschein) direkt nach der Erzeugung ansehen und evtl.
korrigieren.
Dort ist im Positionsteil nun die verwendete
Kontraktnummer mit angegeben.
Die gewogene Menge wurde vom Kontrakt runtergebucht.
Dies kann man sich beim entsprechenden Kontrakt über die Funktionen in der
OptionBox Bewegung (
SF9
) oder Artikel
(
F2
) anschauen.

---

## Verkaufskontrakt Fremdlager (2) / Einkaufskontrakt Fremdlager (12)

Verkaufskontrakt Fremdlager (2) / Einkaufskontrakt Fremdlager (12)
Diese Kontrakte können nicht unter der Anwendung
Kontrakte angelegt werden, sondern müssen z.B. über eine Rechnung oder einen
Lieferschein erzeugt werden.

---

## Vorgangskopie

Vorgangskopie
Mit der Funktionalität der Vorgangskopie wird gegen
einen bestehenden Vorgang wie z.B.Auftrag oder Bestellung gewogen. Die
Vorgangskopie kann an zwei verschiedenen Stellen Aktiviert werden.
1.
Mit dem Einrichterparameter
Teildisposition/Vorgangskopie aus Auftrag
der
Waage
2.
In den Waage-
Prozessen
auf
der
Registerkarte
Vorgang
Folgende weitere
Einrichterparameter
sind für die Vorgangskopie
entscheidend:
1.
Itembox für Teildispo aus Auftrag
2.
Abfrage, ob Auftrag storniert werden soll
3.
Vorgangskopie: Prozentzahl der Menge bei deren Unterschreiten Auftrag Storno
4.
Vorgang erzeugen: Belegdatum als Lieferdatum anstatt des Tagesdatums
Hat man sich im
Waagenprozess
auf der
Registerkarte Vorgang
bei „Art der
Vorgangserzeugung“ für „nicht aktiv / Einrichterparameter entscheidet“
entschieden und trotzdem Itemboxes angegeben, dann werden diese aktiv, wenn der
Einrichterparameter
Teildisposition/Vorgangskopie aus
Auftrag
auf Vorgangskopie oder Teildispo steht. Die Itembox aus der
Vorlage wird der Itembox aus dem Einrichterparameter
Itembox für Teildispo aus Auftrag
dann vorgezogen.
Bei der Vorgangskopie wird z. B. ein Auftrag in einen
Lieferschein kopiert. Die gewogene Menge und andere wichtige Daten (wie z.B.
Datum, Versandart, LKW) aus der Waage werden in den Lieferschein
übernommen.
Welcher Vorgang erzeugt wird ist abhängig von der Einstellung der
Vorgangsklasse auf der Waagenmaske.
Die gewogene Menge wird vom Auftrag abgebucht. Der
Auftrag kann nach der Vorgangskopie storniert werden. Dieses lässt sich über die
Einrichterparameter steuern.
Bei einer Vorgangskopie wird die durch den
Einrichterparameter eingestellte IB auf dem Feld Kunde aktiv. Diese sollte eine
V_Id z. B. für einen Auftrag zurückliefern, damit klar ist, aus welchem Vorgang
eine Vorgangskopie erstellt werden soll. Wählt man z.B. einen Auftrag aus, dann
werden u.a. Artikelnummer und Versandart aus dem Auftrag übernommen und die
Felder auf der Maske dea
[...]


---

## Rohertrag-Anzeige im Vorgang

Rohertrag-Anzeige im Vorgang
Mit Hilfe der Funktion „Rohertrag“ lässt sich eine
Übersicht aller erfassten Positionen anzeigen. Diese beinhaltet neben der
Artikelinformation eine Aufstellung von Einkaufs-und Verkaufspreis sowie der Zu-
und Abschläge, Frachten und Rabatte. Diese werden auch jeweils als Summen
angezeigt. Es lassen sich verschiedene Spalten über Einrichterparameter ein- und
ausblenden, um die Ansicht übersichtlicher oder detaillierter zu gestalten.
Als wichtigste Spalten sind die des Rohertrags zu
nennen. Dieser gibt die Differenz zwischen dem Verkaufspreis und dem
Einkaufspreis an und den Anteil am Verkaufspreis.
Mit Hilfe eines Einrichterparameters ist es möglich
Werte, deren prozentualer Anteil unterhalb eines Schwellenwertes liegt rot
einzufärben.

---

## Zu- / Abschläge Verkauf und Einkauf

Zu- / Abschläge Verkauf und Einkauf
Hier werden alle Kunden / Lieferanten angezeigt, für
die Zu- / Abschlags­verein­ba­run­gen bestehen. Bestehende
Vereinbarungen können überarbeitet werden. Zur Ein­rich­­tung siehe
„Hauptmenü
Preise /
Konditionen“.

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

## af_typ

af_typ
Dieses Format sollte gepflegt werden bevor die
Anwendung Lieferbeleg genutzt wird.
Hier legt man fest welche Art von
Lieferbelegen man in der Firma verwendet z.B. Lieferscheinblöcke.
Für die Abgrenzung der Auswahlliste nach dem Typ mit
Hilfe der Funktion Bereich/Profile F2 ist es notwendig das Feld Kommentar,
Schnipsel in diesen Format wie folgt zu pflegen:
AND (lbs_typ = Nummer des Formatausdruckes der
aktuellen Zeile )
z.B. für die Nummer 1
AND (lbs_typ = 1 )

---

## Referenz-ERP App-Dashboard

Referenz-ERP App-Dashboard
In diesem Bereich werden die wichtigsten statistischen
Informationen angezeigt.
Folgende Auswertungen werden im Standard in
Tabellenform mitgeliefert:
-
Letzte Angebote
-
Angebote pro Monat
-
Letzte Aufträge
-
Aufträge pro Monat
-
Letzte Rechnungen
-
Rechnungen pro Monat
-
Karte (Kunden um den aktuellen Standort)
-
Meist verkaufte Artikel
-
Meist verkaufte Artikel aktuelles Jahr
-
Top 100 Kunden
Folgende Auswertungen werden im Standard als Grafik
mitgeliefert:
-
Top 10 Kunden (aktuell und Vorjahr)
-
Top 10 Artikel (aktuell und Vorjahr)
-
Umsatz pro Land (aktuell und Vorjahr)
-
Umsatz pro Jahr
-
Umsatz pro Monat (aktuelles Jahr)
-
Umsatz pro Monat (Vorjahr)

---

## Allgemeines zu OLAP

Allgemeines zu OLAP
Viele Daten lassen sich als Listen nicht einfach
erfassen. Hier sei ein Beispiel genannt, welche Daten in einer OLAP-Auswertung
besser als in einer Datenliste dargestellt werden können:
Beispiel Verkaufsauswertung
Die Liste enthält Daten zu Land, Stadt, Anzahl der
verkauften Artikel, Preis pro Artikel und ein Verkaufsdatum.
Diese lassen sich als OLAP-Pivot-Tabelle darstellen,
indem die Daten gruppiert nach Land und Stadt aufgetragen auf die Vertikale und
Artikel auf der Horizontalen mit den Datenangaben in Datenfeldern angezeigt
werden.

---

## Allgemeines zur Streckenabwicklung

Allgemeines zur Streckenabwicklung
Ziel der Streckenabwicklung ist:
Arbeitserleichterung durch Erfassung von Ein- und
Verkaufsbeleg in einem Arbeitsgang
Überwachung der Streckengeschäfte auf Erfüllung: Sind
zu den Eingangsbelegen die Ausgangsbelege erfasst worden und umgekehrt? Gehen
Mengen und Werte auf? Was habe ich an der Strecke verdient?
Streckengeschäfte sollen statistisch vom Lagergeschäft
getrennt werden: Geringere Spannen aber auch Kostenbelastungen; kein Lager,
etc.
Streckenabwicklung kann bei der Abwicklung unter
folgenden Aspekten betrachtet werden:
Es steht ein Eingangsbeleg im Vordergrund, dieser
Beleg soll inhaltlich ganz oder teilweise sofort auf einen oder mehrere
Ausgangsbelege verteilt werden.
Der Eingangsbeleg kann auf mehreren Ebenen (
Bestellung, Eingangs­liefer­schein, Eingangsrechnung ) vorliegen.
ein geplantes Streckengeschäft wird erfasst. Hierzu
werden die entsprechen­den Belege mit ihrem Anfall schrittweise erfasst.
Systemtechnische Voraussetzungen
In
[MNDNK]
sollten die Nummernkreise für
Strecken ( Anlage aus STR ) und automatische Streckenanlage ( Anlage aus
Einkaufsvorgang ) eingerichtet werden.
Die Steuerparameter (SPA) im Bereich Strecken /
Partien sollten überprüft werden;
Nachfolgende Darstellung zeigt mögliche
Einrichtungen:
Nr.1: Mit dem Parameter 1 wird die
Streckenverwaltung aktiviert bzw. deaktiviert
Nr. 8: Bei der Neuanlage eines Streckengeschäftes wird
es vorbelegt mit dem hier eingetragenen Wert: Wenn Streckengeschäfte z.B.
überwiegend im Schüttgutbereich ablaufen und diese z.B. mit der Mengeneinheit kg
abgewickelt werden, dann führt die Eingabe der Mengeneinheitsnummer hier zu
dieser Vorbelegung. Sie kann natürlich überschrieben werden.
Nr. 9: Eine Streckenanlage kann mit und ohne
Lagerzuordnung erfolgen. Eine Zuordnung von Artikelschlüssel und Lager führt
später zu einer Prüfung hierauf; wird dagegen Artikelstamm eingetragen, erfolgt
kein Lagerprüfung
Nr. 21: Offene Streckengeschäfte werden beim Zuor
[...]


---

## Angebot

Angebot
Hauptmenü
Warenverkauf
Angebot
Angebotsbearbeitung
oder Direktsprung
[AGB]
Die Vorgangsklasse „Angebot“ dient zur Erfassung,
Bearbeitung, Verwaltung und Druck von Angeboten.
Angebote werden als Vorgang gespeichert. Auf sie kann
in Nachfolgevorgängen zugegriffen werden; Bestandsbuchungen nach Menge und Wert
erfolgen nicht. Referenz-ERP stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      Angebotes
Stapelverarbeitung
Übernahme eines oder mehrerer
      Angebote in einen Bearbeitungsstapel
Erstdruck
F9
Erstdruck eines
      Angebotes
Formulardruck
F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
F5
Korrektur eines
      Angebotes
Ansicht
F6
Angebot im Ansicht-Modus
      öffnen
Kopieren
CF8
Kopieren des Angebotes für einen
      auszuwählenden Kunden
Vorschau
F11
Druckvorschau
Stornieren
F7
D
      Stornieren (Löschen) des Angebotes
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Auftrag aus
      Angebot
Umwandeln in einen
      Auftrag
LS aus Angebot
Umwandeln in einen
      Lieferschein
Rech. aus Angebot
Umwandeln in eine
      Rechnung
Sammelauftr. aus
      Angeb.
Umwandeln mehrerer Angebote in einen
      Auftrag
Sammel-Li aus
      Angeb.
Umwandeln mehrerer Angebote in einen
      Lieferschein
Sammel-Re aus
      Angeb.
Umwandeln mehrerer Angebote in eine
      Rechnung
Archiv ansehen
Anzeige archivierter
      Angebote
Wiedervorlage
CF9
Angebot mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel
      ändern
manuelle Änderung von
      Weiterverarbeitungsparametern
Die Funktionen werden im Detail am Beispiel der
Rechnungserfassung beschrieben.
Besonderheiten
Angebote können gegen das Sortimentslager geschrieben
werden, wenn der Steuerparameter
Angebot auf dem
Sortimentslager zulassen (
SPA 1051
) auf „Ja“ gestellt ist. Bei der
Umwandlung
des Angebotes
muss dann das Zie
[...]


---

## Anmerkung:

Anmerkung:
Für die Weiterverarbeitung ist auf Vorgangsebene das
Pascal-Script
VorgangEinspielung
zuständig, das von der Funktion
VorgangUebergabeBelErz aufgerufen wird.
Auf Rohwarenebene rufen die Funktionen CWLU_EK (für
Einkauf) und CWLU_VK (für Verkauf) die JPL-Prozedur
cwegvorb
auf.
Dabei werden sowohl Vorgangsdaten als auch
Rohwarendaten importiert. Je nach Bestimmung werden unterschiedliche
Zwischenrelationen für die Speicherung der importierten Daten verwendet:
Vorgangsdaten werden in die Relation
VorgangUebergabe
importiert.
Rohwarendaten stehen nach dem Import in der Relation
RohwareHauptsatz_Waage
und die zugehörigen Analysewerte in der Relation
RohwareZusatzQualitet_Waage
.
Die Waagenschnittstelle in Form des Pascal-Scriptes
WaagenImport ist einheitlich. Beim Start konfiguriert sie sich aus den Daten der
Relationen ScriptParam und ScriptParamPar. Die Standard-Waage benutzt dazu die
Datensätze mit der ScriptPId = „WaagenImport“. Bei Verwendung mehrerer Waagen
oder Importschnittstellen, die unterschiedlich zu konfigurieren sind, kann immer
wieder das gleiche Pascal-Script verwendet werden. Die unterschiedliche
Konfiguration wird durch weitere Gruppen von Scriptparametern erreicht. Der
Aufruf des Pascalscriptes muss dann ebenfalls angepasst werden (s. Spezielle
Fragestellungen).

---

## Artikelstapel (Einrichtung)

Artikelstapel (Einrichtung)
Hauptmenü
Warenverkauf
Übergreifend
Artikelstapel (Marktstandangebote)
Direktsprung
[MSA]
Im Modul Artikelstapel, welches im Kontextmenü der
Vorgangstabelle (Direktsprung MAG) unter dem Menüpunkt Artikelstapel
zu erreichen ist (UMSCHALT F5), können freie
Artikelstapel oder aber auch Kundenindividuelle Artikelstapel angelegt
werden.
Ein Element eines Artikelstapels besteht aus folgenden
Eigenschaften:

---

## Aufbau der XML Datei „autom_bestellung.xml“

Aufbau der XML Datei „autom_bestellung.xml“
Die Datei gliedert sich zurzeit in die folgenden drei
Abschnitte
<neuerVorgang>
<positionHinzufuegen>
<positionZusammenfuehren>
Die Bedeutung der Abschnitte ist selbsterklärend. In
diesen Abschnitten werden die einzelnen Vorgangsattribute zu den jeweiligen
Vorgängen definiert. Obwohl eine Überprüfung der hier eingegebenen Daten im
lesenden Script (bestellung_start.vbs) durchgeführt wird, ist eine sorgsame
Dateneingabe für die automatische Durchführung der Vorgänge notwendig. So sollte
darauf geachtet werden das die eingegebenen Daten (wie z.B. Kundenummer, Partie,
Artikel etc.) im System enthalten sind und sie korrekt eingegeben werden.
Zu beachten sind die folgenden Attribute
<d_artikelid>
<d_partieid>
<s_artikelid>
<s_partieid>
Hier muss entgegen der Attributbezeichnung nicht die
ID sondern die jeweilige Nummer eingegeben werden.
Außerdem müssen Mengen mit einem Dezimalpunkt als
Trennzeichen eingegeben werden.
Beispiel:
<
neuerVorgang
>
<
bewegungsstatus
>
1
</
bewegungsstatus
>
<
d_artikelid
>
2100
</
d_artikelid
>
<
d_kundnummer
>
300005
</
d_kundnummer
>
<
d_v_klassnummer
>
1400
</
d_v_klassnummer
>
<
prozessid
>
3780
</
prozessid
>
<
s_artikelid
>
2100
</
s_artikelid
>
<
s_jahrnummer
>
2007
</
s_jahrnummer
>
<
s_menge
>
8.88
</
s_menge
>
<
s_partieid
>
95
</
s_partieid
>
<
s_v_klassnummer
>
400
</
s_v_klassnummer
>
<
wer
>
HA
</
wer
>
...
</
neuerVorgang
>
<
positionHinzufuegen
>
<
bewegungsstatus
>
1
</
bewegungsstatus
>
<
d_artikelid
>
2100
</
d_artikelid
>
<
d_jahrnummer
>
2007
</
d_jahrnummer
>
<
d_kundnummer
>
300005
</
d_kundnummer
>
<
d_v_klassnummer
>
1400
</
d_v_klassnummer
>
<
prozessid
>
3780
</
prozessid
>
<
s_artikelid
>
2100
</
s_artikelid
>
<
s_jahrnummer
>
2007
</
s_jahrnummer
>
<
s_menge
>
3.33
</
s_menge
>
<
s_partieid
>
97
</
s_partieid
>
<
s_v_klassnummer
>
400
</
s_v_klassnummer
>
<
wer
>
HA
</
wer
>
...
</
positionHinzufuegen
>
<
positionZusammenfuehren
>
<
bewegungsstatus
>
1
</
bewegu
[...]


---

## Auftrag

Auftrag
Aufträge entstehen durch Neuerfassung oder Umwandlung
aus Angeboten. Aufträge werden als Vorgang gespeichert, auf sie kann in
Nachfolgevorgängen zugegriffen werden; die disponierte Menge wird verbucht;
Wertbuchungen erfolgen nicht. Referenz-ERP stellt folgende Bearbeitungsfunktionen zur
Verfügung:
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      Auftrags
Stapelverarbeitung
Übernahme eines oder mehrerer
      Aufträge in einen Bearbeitungsstapel
Erstdruck
F9
Erstdruck eines Auftrags
Formulardruck
F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
F5
Korrektur eines Auftrags
Ansicht
F6
Angebot im Ansicht-Modus
      öffnen
Kopieren
CF8
Kopieren des Auftrages für einen
      auszuwählenden Kunden
Vorschau
F11
Druckvorschau
Stornieren
F7
Stornieren (Löschen) des
      Auftrags
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
LS aus Auftrag
Umwandeln in einen
      Lieferschein
Rech. aus Auftrag
Umwandeln in eine
      Rechnung
Sammel-Li aus Aufträgen
Umwandeln mehrerer Aufträge in einen
      Lieferschein
Sammel-Re aus Aufträgen
Umwandeln mehrerer Aufträge in eine
      Rechnung
Teildispo aus Aufträgen
Aufruf eines Auftrages zur
      Teildisposition
Rückauftrag erfassen
Ausbuchen eines
      Restauftrags
Transportauftrag
Auftrag einer Spedition
      zuordnen
Schnellkorrektur
Plandatum und Menge
      ändern
Archiv ansehen
Anzeige archivierter
      Vorgänge
Wiedervorlage
CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel
      ändern
manuelle Änderung von
      Weiterverarbeitungsparametern
PDF-Signieren SH-F12
Den
      ausgewählten Auftrag
elektronisch
      unterschreiben
Ladeschein zusammenstellen
Mit dieser Funktion können einzelne Position aus
unterschiedliche Aufträge und Unterschiedlichen Kunden schnell und bequem in ein
Ladeschein übernommen werden. Dazu werden die Positionen in der Auswahlliste
markiert und
[...]


---

## Auftragserteilung

Auftragserteilung
Aus dem Projekt heraus kann jederzeit ein Auftrag
erzeugt werden, dabei wird die eingegebene Zeit als Menge dem im
Einrichtungsbereich zugeordneten Artikels hinzugefügt.
Für die drei verschiedenen Zeitangaben werden drei
Artikelzeilen erzeugt.

---

## Auftragsrückmeldungen

Auftragsrückmeldungen
Die gleiche Methodik wie oben kann genutzt werden, um
Aufträge in das Referenz-ERP System per e-Mail einzuspielen.

---

## Auftragsumwandlung

Auftragsumwandlung
Wird per EPA Auftragsumwandlung (Zielklasse)
eingeschaltet, so wird nach Eingabe des Kunden sofort eine Liste mit den offenen
Belegen angezeigt.
Dort kann durch Anklicken einer Vorgangsnummer dieser
zur Bearbeitung und Umwandlung in einen Lieferschein herangezogen oder durch
Klicken mit der Maus auf das Wort Vorgang eine leere Artikelstapelliste
angezeigt werden.
Wird ein Vorgang angewählt, so erscheint die Abfrage,
ob dieser Vorgang umgewandelt werden soll. Hier kann nun entschieden werden, ob
der Originalbeleg ergänzt werden soll, oder ob es sich um eine Umwandlung
handelt.

---

## Aufträge und Kommissionierplatz verknüpfen

Aufträge und Kommissionierplatz
verknüpfen
Möchte man einen Auftrag mit einem Kommissionierplatz
verknüpfen, scanne den Barcode der Kunden-Packliste (siehe unten)
Danach scanne den Kommissionierplatz. Damit ist die
Verknüpfung vom Auftrag zum Kommissionierplatz geschaffen worden.
Farbbedeutung:
Menge
Partie
Regal
Artikel
Bedeutung
rot
leer
Nicht im Lager
rot
Ø
0
Für
      den Auftrag nicht genügend vorhanden
weiß
weiß
Kann
      aus dem Regal geholt werden
weiß
gelb
Andere Partie als im
      Auftrag
magenta
Nichts von diesem Artikel im
      Lager
Verknüpfung von Auftrag und Lagerplatz aufheben
Durch Scannen eines Regalplatzes und anschließender
Eingabe von „9999“ kann die Verbindung von Regalplatz und Auftrag aufgehoben
werden.
Automatische Zuordnung von Auftrag und Regalplatz
Durch Scannen eines Auftrages und anschließendem
Betätigen der Taste „F2“ wird dem Auftrag der höchste noch freie Regalplatz
zugeordnet.
Zur Produktionsvorplanung müssen einige Artikel aus
dem Lager zur Produktion bereitgestellt werden. Dazu gibt man im Scanner die
Produktionsnummer ein oder scannt den Barcode auf dem Vorplanungslaufzettel:
Nach der Scannung erscheint folgendes Bild auf dem
Scanner, wenn die Komponenten dieser Produktion folgende Bedingungen
erfüllt:
1.
Es dürfen keine halbfertige Komponenten enthalten sein
2.
Sie müssen Partiezuordnungen mit einer 8 – stellige Partienummer haben
3.
Die Komponenten müssen im Lager vorrätig sein
4.
Nicht genügend Ware im Vorplanungsregal liegt
Die für die Produktion benötigte Menge ist grün
hinterlegt. Zusätzlich zur Regalnummer wird unter Regal in der runden Klammer
die im Regal vorhandene Menge angezeigt, in der eckigen wird die Artikelnummer
abgebildet. Scannt man nun die Regalnummer und gibt die Entnahmemenge ein, ist
in dem Scanner dann folgendes zu sehen:

---

## Automatismus, was passiert?

Automatismus, was passiert?
Bei der automatisierten Vorgangserstellung werden 3
Vorgänge hintereinander generiert bzw. verändert
Es wird ein neuer Vorgang generiert
Daten aus der XML-Datei lesen
Daten prüfen
Vorgangsbearbeitung anstoßen (start_bestellung in
bestellung.vbs)
Dem Vorgang wird eine neue Warenposition
hinzugefügt
Daten aus der XML-Datei lesen
Daten prüfen
Vorgangsbearbeitung anstoßen (start_bestellung in
bestellung.vbs)
Einer Warenposition des Vorgangs wir eine neue Partie
hinzugefügt
Daten aus der XML-Datei lesen
Daten prüfen
Vorgangsbearbeitung anstoßen (start_bestellung in
bestellung.vbs)

---

## Bearbeiten der Streckentexte

Bearbeiten der Streckentexte
Über den Button mit dem Stift-Symbol neben dem
jeweiligen Report kann man eine Maske zur Bearbeitung der Streckentexte
öffnen.
Die Felder die angezeigt werden stammen aus der Anwendung
Vorgangsklammer
und dort aus
den Registern
Drucktexte
und
Bemerkungen
.
Es werden
hier im Register Allgemein immer nur die Felder angezeigt, die vom jeweiligen
Report verwendet werden.

---

## Beispielanwendung Einkauf Verkauf

Beispielanwendung Einkauf
Verkauf
Folgende Bespielanwendung stellt den Einkauf
periodenweise dem Verkauf gegenüber:
Grundlage dieser Auswertung ist die Auswahlliste
Vorgangsübersicht, Variante 1. Diese Variante wird einmal in ein Tabellenblatt
„SV_UBERSICHT_Status“ als Komplettdatenbereich geladen, des Weiteren wird die BI
View noch mit der Eingrenzung für den Verkauf und der Eingrenzung für den
Einkauf in die Tabellenblätter Einkauf und  Verkauf geladen. Als Auswertung
darauf sind 4 Pivot-Auswertungen gestaltet worden, die zusätzlich noch mit eine
Pivot-Graphik verbunden worden sind.

---

## Belegarten

Belegarten
Belegarten
2
Barverkauf
4
Barverkauf Gutschrift
1
Bareinkauf
10
Zahlungsmeldung
11
Einzahlung
12
Geldübernahme von einer anderen
      Kasse
14
Geldentnahme mit Zuordnung
      Sachkonto
15
Auszahlung
16
Geldübergabe an eine andere
      Kasse
17
Abschöpfung /
      Einreichung
18
Sortenwechsel
20
Kassensturz
23
Storno Barverkauf
24
Storno
      Barverkauf-Gutschrift
23
Storno Bareinkauf
Hinweis:
Die Belegarten zwischen 10 und 20 werden auch als
Finanzvorgänge bezeichnet.

---

## Belegfluss Variante 4 Postfacheinrichtung

Belegfluss Variante 4 Postfacheinrichtung
Auswahlliste
Name
Beschreibung
Postfach Id
Id
      des Postfachs
Postfach Bezeichnung
Bezeichnung des
      Postfachs
EL-Klasse
Lieferscheinklasse
El-uKlasse
Lieferscheinunterklasse
ER-Klasse
Eingangsrechnungsklasse
ER-uKlasse
Eingangsrechnungsunterklasse
Suchoption
Name
Beschreibung
Postfach
Id
      des Postfachs
Bezeichnung
Bezeichnung des
      Postfachs
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
      den Pfleger der Postfacheinrichtung auf.

---

## Belegzuordnung

Belegzuordnung
Zum Zeitpunkt der Anlieferung gibt es noch keine
Belege. Dennoch können Laborergebnisse vor Erfassung der Belege wie
Eingangslieferschein etc. vorliegen. Um diese Belege später zu den
Laborergebnissen zuordnen zu können, müssen zwei Voraussetzungen gegeben sein:
1.
Die Nummer des Lieferscheins muss aus der Liefernummer der Online-Waage erzeugt
werden.
2.
Das Belegdatum aus der Waage muss mit dem Datum der Erfassung des Beleges
übereinstimmen.

---

## Benachrichtigung bei Kreditlimitüberschreitung

Benachrichtigung bei
Kreditlimitüberschreitung
Es gibt die Möglichkeit sich benachrichtigen zu
lassen, sobald mit dem Speichern eines Vorganges (z.B. Auftrag) das Kreditlimit
eines Kunden überschritten wird.
Dazu sind folgende Einstellungen nötig:
1.
Das Kreditlimit beim jeweiligen Kunden muss gepflegt sein. (siehe auch
Kreditvergabe
)
2.
Der
Steuerparameter 233
sollte dazu
so eingestellt sein, dass er ein Speichern des Beleges nicht verhindert. Mehr
dazu finden Sie auch weiter oben unter
Überwachung des Kreditlimits
.
3.
Das Feld der Vorgangsunterklasse ‚
Fehlerprotokolleintrag bei
Kreditlimitüberschreitung
‘ muss auf Ja stehen.
4.
Im Mandantenstamm
[MND]
muss dafür im
Register Allgemein Abschnitt Fehlerprotokoll-Meldewesen die Empfänger-Prozedur
entsprechend hinterlegt werden.
Es gibt eine Prozedur, die von Branchen-ERP angelegt
wurde, die einfach in eine private Prozedur kopiert und angepasst werden kann:
FehlerprotokollAbweichendeEmpfaenger (zu finden unter [SQLP]). Dazu muss die
Abfrage auf ‚%Kreditlimit%‘ geändert und die E-Mail-Adresse entsprechend
angepasst werden.
http://www.Branchen-ERP/ihilfe/index.html?turl=XMLDocuments%2FiAeins%2Fhtml%2FM_SQL_FehlerprotokollMeldewesen_FehlerprotokollAbweichendeEmpfaenger.htm

---

## Überblick Vorgänge

Überblick Vorgänge
Vorgang
bestellung.vbs
bestellung_start.vbs
autom_bestellung.xml
Automat
Parameter
Neuer Vorgang
X
X
X
X
Neue
      Position
X
X
X
X
Position zusammenführen
X
X
X
X
Mengenänderung
X
Umverteilung
X

---

## Übersicht Bewertungsmethoden

Übersicht Bewertungsmethoden
Bewertungsmethode
Beschreibung
Durchschnittlicher
      Jahres-Einkaufspreis
Der
      durchschnittliche Jahreseinkaufspreis wird als arithmetisches Mittel aller
      Einkäufe des betreffenden Wirtschaftsjahres ermittelt. In das Mittel geht
      der eine Jahreswechselinventur als Vortrag ein.
Ist
      der Jahreswechsel ohne Inventur erfolgt oder die Inventur noch nicht
      eingespielt, so geht der Endbestand des Vorjahres als Vortrag ein. Die
      Bewertung der Jahresendmenge ergibt sich dann wiederum aus dem
      durchschnittlichen Einkaufspreis des vorangehenden Wirtschaftsjahres,
      usw.
Zwischeninventuren wirken sich
      ebenfalls auf den durchschnittlichen Einkaufspreis aus:
Der
      durchschnittliche Jahreseinkaufspreis wird stets per Periode im
      Wirtschaftsjahr bestimmt. Will man etwa die Bewertung per Periode 5/2000
      bestimmen, so werden wie oben beschrieben die Einkäufe der ersten 5
      Perioden sowie der Vortrag herangezogen. Es sei denn, etwa in Periode 3
      sei eine Zwischeninventur durchgeführt worden. Dann ergibt sich der
      Durchschnittspreis per 5/2000 aus dem Inventurbestand per Ende 3/2000 plus
      der Einkäufe der Perioden 4 und 5.
Die
      Bestimmung des durchschnittlichen Jahreseinkaufspreise reicht also
      grundsätzlich bis zur letzten eingspielten Stichtags-Inventur vor der
      Stich-Periode zurück.
Durchschnittlicher
      Jahres-Einkaufspreis ABSOLUT
Berechnung wie beim
durchschnittlichen
      Jahreseinkaufspreis
,
      jedoch gehen negative Periodensummen von Einkaufswert und Einkaufsmenge
      positiv (Absolutwert-Verfahren) in die Berechnungssummen von
      Gesamteinkaufswert und Gesamteinkaufsmenge zur
      Durchschnittspreisberechnung ein. Dadurch werden zwar mathematisch
      korrekte aber semantisch schwer erklärbare (sehr große oder
      negative)
Werte
      vermieden. Somit liefert diese Methode bei Vorliegen von Perioden, die

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

## Bestellung

Bestellung
Bestellungen entstehen durch Neuerfassung oder
Umwandlung aus Bestellanfragen. Bestellungen werden als Vorgang gespeichert, auf
sie kann in Nachfolgevorgängen zugegriffen werden; die bestellte Menge wird
verbucht; Wertbuchungen erfolgen nicht. Referenz-ERP stellt folgende
Bearbeitungsfunktionen zur Verfügung:
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      Vorgangs
Stapelverarbeitung
Übernahme eines oder mehrerer
      Vorgänge in einen Bearbeitungsstapel
Erstdruck
F9
Erstdruck eines Auftrags
Formulardruck
F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
F5
Korrektur eines Vorgangs
Ansicht
F6
Vorgang im Ansicht-Modus
      öffnen
Kopieren
CF8
Kopieren des Vorgangs für einen
      auszuwählenden Kunden
Vorschau
F11
Druckvorschau
Stornieren
F7
Stornieren (Löschen) des
      Vorgangs
Storno
      Bestellung
Erfassung eines Storno
      Vorgangs
Rückbestellung
      erfassen
Ausbuchen einer
      Restbestellung
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
E-Lieferschein aus
      Bestellung
Umwandeln in einen
      Eingangs-Lieferschein
E-Rech. aus Bestellung
Umwandeln in eine
      Eingangs-Rechnung
Sammel-ELi aus
      Bestellungen
Umwandeln mehrerer Vorgänge in einen
      Eingangs - Lieferschein
Sammel-ERe aus
      Bestellungen
Umwandeln mehrerer Vorgänge in eine
      Eingangs-Rechnung
Archiv ansehen
Anzeige archivierter
      Vorgänge
Wiedervorlage
CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel
      ändern
manuelle Änderung von
      Weiterverarbeitungsparametern

---

## Bewegungsart (wbc_BewArt)

Bewegungsart (wbc_BewArt)
Das Feld wbc_BewArt findet sich in der View
AMIC_V_Warenbewegung_info
.
Bewegungsart
Ist wbc_BewArt gleich 0, so handelt es sich um eine
      reine buchhalterische Buchung, bei der keine Ware physisch bewegt wird
      (Ausnahme reiner Einkauf, reiner Verkauf). Dies kann das bisherige
      Kennzeichen WaBewBestTyp der Warenbewegung ersetzen.
0
Alle
      Buchungen, die buchhalterisch relevante Bestände berühren (EK, VK,
      Vereinnahmung und Kommissionsverkauf)
Diese Bewegungsart wurde in früheren
      Versionen auch als Eigenbewegung bezeichnet.
1
Buchung, die nur einen
      physikalischen Bestand berührt – Vorverkauf Abholung
Diese Bewegungsart wurde in früheren
      Versionen auch als FremdwareVerkauf bezeichnet
2
Buchung, die nur einen
      physikalischen Bestand berührt – Voreinkauf Anlieferung
Diese Bewegungsart wurde in früheren
      Versionen auch als Fremdlager Einkauf bezeichnet
3
Buchung, die nur einen
      physikalischen Bestand berührt – Einlagerung und Abholung
4
Buchung, die nur einen
      physikalischen Bestand berührt – Kommission und Rücknahme

---

## Buchungstyp eines Kontrakts

Buchungstyp eines Kontrakts
Wird bei Vorverkauf, Voreinkauf, Einlagerung oder
Kommission ein Kontrakt zur Abwicklung der Nebenbuchhaltung verwendet, so hat
dieser neben einer Kontraktklasse einen Buchungstyp.
Die Sonderkontraktklassen 2 und 12, die in vorherigen
Versionen Voreinkauf (Fremdlager Einkauf) und Vorverkauf (Fremdware Verkauf)
kennzeichneten laufen aus.
Bitte beachten Sie, dass bei der Verwendung
bestehender privater Auswahllisten, und Itemboxen diese Änderung berücksichtigt
werden muss.
Der Buchungstyp ist im Kontraktstamm auf der
Registerkarte „Zusätze“ eingetragen. Er wird jedoch nur durch Setzen des EPA
sichtbar.
Buchungstypen
0
Eigenwarebuchung
Diese Buchung verändert nur die
      Bestände der Eigenware
1
Vorverkauf
Diese Buchung verändert
      Fremdware
2
Voreinkauf
Diese Buchung verändert
      Fremdlager
3
Einlagerung
Diese Buchung verändert
      Fremdware
4
Kommission
Diese Buchung verändert
      Fremdlager

---

## Datumsbezüge

Datumsbezüge
Auf diesem Tabreiter können drei wichtige
Datumsangaben gepflegt werden:
Feld
Beschreibung
Liefertag
Auf
      Stufe Angebot/ Auftrag  wird hier das Plandatum gepflegt.
Ab
      Stufe Lieferschein handelt es sich um das Lieferdatum. Dieses Datum
      wird bei der Einordnung der Warenbewegung in den zeitlichen Verlauf
      herangezogen.
Besonderheit: Dieses Datum wird auch
      auf dem Haupt-Tabreiter gepflegt. Beide Eingabefelder werden
      synchronisiert.
Preisdatum
Dieses  Datum wird bei
      Preisfindung und der Ermittlung von preisbeeinflussenden Konditionen (Zu
      -Abschläge, Rabatte, Frachten)  herangezogen. Es wird üblicherweise
      mit dem Belegdatum  oder dem optionalen Preisdatum des Vorgangs
      vorbelegt, wenn die Warenposition neu erfasst wird.
Abgrenzdatum
Dient zur zeitlichen Abgrenzung von
      Nebenbuchhaltungen (Kontrakte, Partien, Objekte)
Bei der Bestimmung von Preisen, Konditionen und
Nebenbuchhaltungen (Kontrakte, Partien, Objekte etc.) werden die  Objekte
überwiegend nach Datumsangaben abgegrenzt (Zeiträume oder
Gültigkeitsbereiche).

---

## Dauerauftrag

Dauerauftrag
Hierbei handelt es sich um einen spezielle Form des
Auftrages: Im Vorgangskopf wird der Turnus des Dauerauftrages eingestellt.
Feld
Beschreibung
DA
      Anfang
Startdatum für den
      Dauerauftrag
DA
      nächster Termin
nächste Fälligkeit
Nächster Termin an dem der
      Dauerauftrag ausgeführt werden soll
DA
      Periode
Angabe der Periodizität:
1,2..,12 – alle ..
      Monate
(z.B. 1 = monatlich, 3 = vierteljährlich, 12 =
      jährlich)
mehrfach im Monat
Angabe der Termintage per Funktion ‚Dauerauftrag-Fälligkeit‘
wöchentlich
einmal
      pro Woche am Wochentag des Startdatums
alle
      2 Wochen
am Wochentag des Startdatums
alle
      3 Wochen
am Wochentag des Startdatums
alle
      4 Wochen
am Wochentag des Startdatums
mehrfach pro Woche
Angabe der Wochentage per Funktion ‚Dauerauftrag-Fälligkeit‘
DA
      Ende
Datum an dem der Dauerauftrag nicht
      mehr wirksam sein soll
Funktion
Bedeutung
Dauerauftrag
      erfassen
F8
Erfassung eines neuen
      Dauerauftrages
Dauerauftrag
      starten
SF9
Erstellt eine Rechnung aus dem
      Dauerauftrag.
Es
      öffnet sich die Maske ‚Rechnung aus Dauerauftrag‘. Zur Erläuterung der
      Felder auf dieser Maske siehe
Umwandeln und Kopieren
.
Umwandlung starten F9 erzeugt dann
      die Rechnung und setzt die nächste Fälligkeit des Dauerauftrages
      neu.
Dauerauftrag
      ändern
F5
Ändern der markierten von
      Daueraufträge, z.B. um den als nächstes vorgeschlagenen Fälligkeitstermin
      zu ändern
Anschriften
      aktualisieren
Anschriften im
      Dauerauftrag manuell aktualisieren
.
Dauerauftrag-Termine
Bei den Dauerauftrag-Periodentypen ‚mehrfach im Monat‘
und ‚mehrfach pro Woche‘ können die Termine, an denen der Dauerauftrag
ausgeführt werden soll, in einer Liste von Monatstagen beziehungsweise
Wochentagen markiert werde.
Ausgehend von dem aktuellen Fälligkeitsdatum
wird bei diesen Periodentypen der jeweils nächste markierte Tag bei der
Rechnungserstellung
[...]


---

## Druckpositionen auf der Warenposition

Druckpositionen auf der Warenposition
Auf der Warenposition gibt es weitere Druckpositionen.
Mit ihnen kann markiert werden, ob es sich um Vorverkauf, Voreinkauf,
Einlagerung, Vereinnahmung, Einlagerungs-Abholung, Kommission,
Kommissionsverkauf, Kommissionsrücknahme oder Wertartikel handelt. Da alle diese
Markierungen exklusiv, also nicht parallel verwendet werden, können diese
Druckpositionen einander überlagern, also auf der gleichen Stelle eingerichtet
werden. Der zu druckende Text ist frei definierbar.
Ist die keine Markierungen zutreffend und ist die
Markierung einzige auf der Druckzeile, so wird diese Druckzeile ignoriert und
nicht gedruckt.

---

## Drucksteuerung

Drucksteuerung
Barverkaufsbelege gehen über Drucker und Formular laut
Einstellung
[VRGD]
, falls dort nicht
eingerichtet über
[DRZ]
/
[FRZ]
.
Zahlungsbelege gehen über die Formulare 51 bis 55,
falls in der Zahlungsmaske der EPA Formulardruck auf ja geschaltet ist.
Anderenfalls werden fest programmierte Formulare (für Kassensturz gibt es
derzeit nur ein solches!) über die in der Einrichtung des Kassensystems
eingestellten Drucker gedruckt.
In welcher Weise nun die Einstellungen aus den
Kassensystemeinstellungen bzgl. LPT oder COM Schnittstelle, zugeordnetem
Druckertyp und seiner Steuerzeichen in dieser Mechanik Verwendung finden, bleibt
zu erforschen. Wie es scheint, kann man in den Steuerzeichen eintragen was man
will, sie werden beim Drucken nur dann ausgewertet, wenn feste Zahlungsformulare
gedruckt werden. In allen anderen Fällen scheint darauf gar nicht zugegriffen zu
werden. Veränderung des Partial Cut jedenfalls haben keine Verhaltensänderung
beim Drucker gezeigt. Es sieht so aus, als würden nur die Steuerzeichen für
ASCII Druck, die dem Druckertyp zugeordnet sind, gezogen. Die speziellen
Steuerzeichen lt. Einstellung des Kassensystems jedenfalls scheinen nicht
benutzt zu werden.
Wer druckt also wo hin:
1.
BV über VRGD, wenn nicht vorhanden über FRZ Ascii Druck
2.
Finanzbelege Kasse über FRZ wenn Formular zugeordnet ist. Auf fest codiertes
Formular auf dem im Kassenstamm eingetragenen Schnittstelle, wenn kein Formular
zugeordnet ist.
3.
Die Journalrolle im Bondrucker wird nur und ausschließlich über fest codierte
Einrichtung auf den eingetragen Schnittstelle ausgegeben.
4.
Wiederholungsdruck von Finanzbelegen erfolgt nur auf feste Formulare auf der im
Kassenstamm eingetragenen Schnittstelle.
5.
Der Zählbericht beim Kassensturz ist nur über ein internes Formular und nur auf
der im Kassenstamm eingetragenen Schnittstelle druckbar.
6.
Kassensysteme über Terminalserver nur mit CITRIX, damit lokale LPT
Schnittstellen freigege
[...]


---

## Einkaufs-/Verkaufskennzeichen

Einkaufs-/Verkaufskennzeichen
Das Einkaufs-/Verkaufskennzeichen wird nur bei
CEREA-Datensätzen benötigt und hat keine Auswirkung auf Daten anderer
Zielansprache. Letzter werden genauer über die Vorgangsklassen definiert.
Entspricht der eingelesene Wert keinem der in den
Parametern EK_KENNUNG und VK_KENNUNG vorgegebenen Werte, so wir der in
EKVK_DEFAULT eingestellte Wert angenommen. Ist auch dieser nicht auswertbar, so
wird „Einkauf“ angenommen.
(Zugehörige
Positionsparameter: EV_SAx)
Lieferscheindatum
Das Datum wird an
späterer Stelle validiert und zuvor durch eine Konvertierung, die mit
DATUMFORMAT parametrisiert wird, geschickt. In DATUMFORMAT ist hinterlegt, in
welcher Form das Datum vorliegt (Mögliche Werte sind: TT.MM.JJ., TT.MM.JJJJ,
JJJJ.MM.TT, JJ.MM.TT, TTMMJJ, TTMMJJJJ, JJMMTT, JJMMTT, JJJJMMTT, auf Groß- und
Kleinschreibung kommt es bei diesen Werten nicht an. Stehen in den Importdaten
statt der Trennpunkte andere Zeichen, so wird das Datum dennoch richtig
erkannt.) Falls das Datumformat nicht explizit über die Scriptparameter
angegeben ist, wird von dem Format TT.MM.JJ ausgegangen.
Kann das
Lieferscheindatum nicht ermittelt werden, wird das Tagesdatum eingesetzt.
Innerhalb der
Datumsvalidierung wird u. U. ein Datenbankfehler angezeigt, wenn sich das Datum
nicht lesen lässt. („Cannot convert to a date ...“). Weiteres zu den
Validierungen am Ende der Programmschleife.
(Zugehörige Positionsparameter: LD_SAx)

---

## Einkauf/Verkauf Typ (wbc_Typ_EKVK)

Einkauf/Verkauf Typ (
wbc_Typ_EKVK)
Der Einkauf/Verkauf Typ findet sich in der View
AMIC_V_Warenbewegung_info
als Feld
wbc_Typ_EKVK.
Einkauf/Verkauf Typ
Mit dem Kennzeichen für den Typ Einkauf oder Verkauf
      soll gekennzeichnet werden, welche Buchungen buchhalterisch auf Bestände
      des eigenen Eigentums (Eigene Ware) wirken. So wirkt z.B. ein Vorverkauf
      auf das Konto Eigenware und das Konto Fremdware. Eine Anlieferung des
      Voreinkaufs hingegen bewirkt nur eine Bewegung zwischen dem Fremdlager und
      der Eigenware.
Verkäufe werden mit dem Typ 2, Einkäufe mit dem Typ 1
      gekennzeichnet.
Verkauf
2
Vorverkauf
2
Vorverkauf Abholung
0
Vorverkauf Rücknahme
2
Kommission
0
Kommission Verkauf
2
Kommission Rücknahme
0
Einkauf
1
Voreinkauf
1
Voreinkauf Anlieferung
0
Voreinkauf Rückgabe
1
Einlagerung
0
Einlagerung
      Vereinnahmung
1
Einlagerung Abholung
0

---

## Einrichtung Abfragefelder „UFLD“ - Block

Einrichtung Abfragefelder „UFLD“ - Block
Direktsprung [UFLD]
Bedienerklasse (-1 = Default)
Vorgang (Lieferschein, Rechnung, .......)
Unterklasse = 0 VK
in Pos. Feld = F3- Taste = Auswahlliste

---

## Einschränkungen der Marktkasse

Einschränkungen der Marktkasse
Die Marktkasse ist ein Barverkaufssystem, das auf die
Verwendung von Berührungsempfindlichen Bildschirmen hin optimiert wurde.
Aus diesem Grund fehlen der Marktkasse einige
Funktionen, die im Bereich der Belegerfassung möglich sind.
Gebindebehandlung
Gebindeartikel sorgen in der allgemeinen
Belegerfassung dafür, dass ein Gebindedialog geöffnet wird, der die
Gebindefaktoren erfasst und daraus eine Menge errechnet.
In der Marktkasse sind hier die Endmengen anzugeben.
Also statt 6 Kanister à 10 Liter müssen hier 60 Liter angegeben werden.
Merkmal-Leiste
Die Merkmalleiste aus der allgemeinen Belegerfassung
ist hier nicht verfügbar
AddOn
AddOn-Felder, die zur Erfassung weiterer Informationen
zur Warenbewegung in VorgangAddOn oder WarenbewegungAddOn dienen werden hier
nicht unterstützt. Als Workaround siehe auch AIS.
AIS
AIS-Felder, die der Erfassung eigener Daten dienen,
werden hier ebenfalls nicht unterstützt. AIS wird als Werkzeug zur dynamischen
Erzeugung der Erfassungsmaske verwendet. Sie können an drei Stellen während der
Erfassung einen selbst definierten Dialog öffnen, um Daten zu erfassen. Hier
können Eingabefelder, jedoch keine Tabellen (Grids) verwendet werden.
Mengenstaffeln
Mengenstaffeln dienen in der allgemeinen
Belegerfassung dazu, Preise für unterschiedliche Mengen in Staffeln festzulegen.
Diese sind in der Marktkasse derzeit nicht möglich.
Partien
Partien werden in der Standardeinstellung in der
Marktkasse im Gegensatz zur allgemeinen Belegererfassung nicht zugeordnet.
•
Partien können gemäß Behandlungsschema bei einem Kundenwechsel zugeordnet
werden, jedoch wird nach einem Kundenwechsel für nachfolgend erfasste Positionen
keine Partiezuordnung vorgenommen.
Kontrakte
Kontrakte sind an Kunden gebundene Vereinbarungen über
Artikelmengen und deren Preise. Während der Erfassung in der Marktkasse werden
Kontrakte in der Standard-Einstellung nicht berücksichtigt.
•
Kontrakte können gemäß Behandlungsschema bei e
[...]


---

## EK-Lieferschein

EK-Lieferschein
Einkauf-Lieferscheine entstehen durch Neuerfassung
oder Umwandlung aus Anfragen / Bestellungen. EK-Lieferscheine werden als Vorgang
gespeichert, auf sie kann in Nachfolgevorgängen zugegriffen werden; die Menge
wird verbucht und erhöht den Bestand; Wertbuchungen erfolgen nicht. Referenz-ERP
stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      EK-Lieferscheins
Stapelverarbeitung
Übernahme eines oder mehrerer
      EK-Lieferscheine in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck eines
      EK-Lieferscheins
Formulardruck F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur F5
Korrektur eines
      EK-Lieferscheins
Ansicht
F6
EK-Lieferschein im Ansicht-Modus
      öffnen
Schnellkorrektur
Stapelkorrektur von Datum und
      Menge
Kopieren
      CF8
Kopieren des EK-Lieferscheins für
      einen auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren
      F7
Stornieren (Löschen) des
      EK-Lieferscheins
Storno
      EK-Lieferschein
Erfassung eines
      Stornobeleges
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
E-RE aus
      EK-Lieferschein
Umwandeln in eine
      Eingangs-Rechnung
Sammel-ERe aus
      EK-Lieferscheinen
Umwandeln mehrerer EK-Lieferscheine
      in eine Eingangs-Rechnung
Rücklieferung
      erfassen
Ausbuchen eines
      Restlieferscheins
Erfassung Strecke
Aufruf der
      Streckenerfassung
Rohware-Wandlung
Lieferschein in einen
      Rohwarelieferschein wandeln
Partien
      nachtragen
nachträgliche Zuordnung von
      Partien
Transportauftrag
Auftrag einer Spedition
      zuordnen
Archiv
      ansehen
Anzeige archivierter
      Vorgänge
Wiedervorlage
      CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel ändern
manuelle Änderung von
      Weiterverarbeitungsparametern

---

## EK-Rechnung

EK-Rechnung
EK-Rechnungen entstehen durch Neuerfassung oder
Umwandlung aus Anfragen / Bestellungen / EK-Lieferscheinen. EK-Rechnungen werden
als Vorgang gespeichert, auf sie kann in Nachfolgevorgängen zugegriffen werden;
die Menge wird verbucht und erhöht den Bestand; der EK-Umsatz erhöht sich.
Referenz-ERP stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktionsname
Funktion
Erfassen F
      8
Erfassung einer neuen
      EK-Rechnung
Stapelverarbeitung
Übernahme eines oder mehrerer
      EK-Rechnungen in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck einer
      EK-Rechnung
Formulardruck
      F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
      F5
Korrektur einer
      EK-Rechnung
Ansicht F6
EK-Rechnung im Ansicht-Modus
      öffnen
Schnellkorrektur
Plandatum und Menge
      ändern
Kopieren
      CF8
Kopieren der EK-Rechnung für einen
      auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren
      F7
Stornieren (Löschen) der
      EK-Rechnung
Storno
      EK-Rechnung
Erfassung eines
      Stornobeleges
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Gutschrift aus
      EK-Rechnung
Umwandeln in eine
      Gutschrift
Sammel-EGU aus
      E-Rechnungen
Umwandeln mehrerer EK-Rechnungen in
      eine EK-Gutschrift
Transportauftrag
Auftrag einer Spedition
      zuordnen
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

## EPA

EPA
Auf den folgenden Masken befinden sich EPAs für jede
Bedienerklasse, die Kassenarbeiten durchführt:
•
POS-Kasse
•
Zahlung
•
Positionserfassung im Barverkauf
(Tresenkasse)
•
Kasseneröffnung/Abschluss.

---

## EPAs der Marktkasse

EPAs der Marktkasse
EPA
Beschreibung
Im
      Verkauf Verprobung mit Listenpreis (Warnmeldung)
Vorbelegt mit Nein.
Abfrage vor Abspeichern einer
      Position?
Vorbelegt mit Nein.
Soll
      schnellerfasst werden?
Vorbelegt mit Ja.
Soll
      im Artikelfeld begonnen werden?
Vorbelegt mit Ja.
Bei
      Ja wird mit der Eingabe im Feld Artikel gestartet.
Soll
      ein gefundener Preis bestätigt werden?
Vorbelegt mit Nein.
Bei
      Ja muss ein gefundener Preis bestätigt werden.
Warnung bei Bestätigen eines
      Nullpreises
Vorbelegt mit Ja.
Bei
      Ja erhält man eine Warnung, wenn ein Nullpreis bestätigt wird.
Soll
      Menge * Preis auf dem Display angezeigt werden?
Vorbelegt mit Nein.
Bei
      Ja wird der Betrag auf dem Kassendisplay für den Kunden
      angezeigt.
Soll
      die letzte erfasste Position stehen bleiben?
Vorbelegt mit Ja.
Warnung bei Bestätigen der Menge
      null
Vorbelegt mit Nein.
Bei
      Ja erhält man eine Warnung, wenn die Menge null bestätigt
      wird.
Rest-Zahlbetrag
      vorbelegen
Vorbelegt mit Ja.
Bei
      Ja wird der restliche Zahlbetrag vorbelegt.
Meldung anzeigen, wenn noch Leergut
      vorhanden ist?
Vorbelegt mit Ja.
Bei
      Ja wird eine Meldung angezeigt, wenn noch Leergut vorhanden
      ist.
Leergutübernahme ohne
      Leergutdialog?
Vorbelegt mit Nein.
Wird
      hier Ja eingestellt, dann wird das Leergut übernommen ohne, dass sich der
      Leergutdialog öffnet.
Warnung bei Bestätigen eines
      Nullbetrages
Vorbelegung mit Nein
Wird
      hier Ja eingestellt, muss ein Nullbetrag bestätigt werden.
Warnung vor Betreten des
      Leergutdialoges
Vorbelegt mit Ja. Bei Ja wird eine
      Meldung
angezeigt, ob die Leerguterfassung
      gestartet werden soll.
Diese Meldung erscheint nur, wenn
      bereits Leergut über den Leergutdialog erfasst wurde.
Dialog „Betrag änder“: Vorzeichen
      positiv?
Vorbelegung mit „Positiv oder
      negativ“: Der Betrag kann sowohl positiv als auch neg
[...]


---

## Erfassung

Erfassung
Die Erfassung
einer Fremdware- oder Fremdlagerrechnung also eines Vorverkaufs oder Voreinkaufs
erfolgt in Referenz-ERP über die Standardbelegerfassung. Im Falle des Vorverkaufs über
die Rechnungserfassung [REE] und im Falle des Voreinkaufs über die
Eingangsrechnungserfassung [ERE]. Im Positionsteil muss dann die Funktion
„Vorverkauf“ oder „Voreinkauf“ (STR-F11) angewählt werden. Es öffnet sich das
Warenerfassungsfenster und die Angaben zur Ware können eingegeben werden. Falls
noch kein Fremdware- bzw. Fremdlagerkontrakt für die erfasste Ware existiert,
das heißt ein Kontrakt, der in Kunde, Artikel, Lager und Lagerplatz mit der
erfassten Position übereinstimmt, der
Steuerparameter
„
Neuer Fremdwarekontrakt je Vorverkauf
(306)
“
bzw. „
Neuer Fremdlagerkontrakt je Voreinkauf (580)
“
oder es sich um einen Rohwareartikel handelt, öffnet sich nach Erfassung der
Warenposition ein Fenster, in dem Angaben zu dem Fremdware- bzw.
Fremdlagerkontrakt gemacht werden können, der für diese erfasste Position
angelegt wird. Dieser Kontrakt übernimmt automatisch die Angaben zum Kunden,
Artikel, Lager und Lagerplatz aus der Warenposition. Ansonsten wird der bereits
bestehende Kontrakt um die Menge der erfassten Warenposition erhöht. In diesem
Fall wird das Kontraktfenster nicht angezeigt.
Nach Abschluss
der Rechnung und Behandlung durch den Mandantenserver, wird der so erfasste
Fremdlager- bzw. Fremdwarebestand im Artikelbestand angezeigt. Fremdbestände
werden unter „Fremdware“ angezeigt und werden und gehören mit zum Istbestand,
nicht aber zum Eigenbestand. Fremdlagerbestände werden unter „Fremdlager“
angezeigt und gehören mit zum Eigenbestand, nicht aber zum Istbestand.
Der erzeugte
Kontrakt kann in der Kontraktübersicht [KTR] bearbeitet werden. Die
Artikelangaben in diesem Kontrakt sind allerdings nicht direkt änderbar, sondern
können nur durch Änderung der dazugehörigen Vorverkaufs- bzw.
Voreinkaufsrechnung modifiziert werden.
Auf diese Art
und Weise
[...]


---

## Erfassung mit den verschiedenen Kassensystemen

Erfassung mit den verschiedenen Kassensystemen
In Referenz-ERP gibt es verschiedene Arten, einen Barvorgang
zu bearbeiten.
Die Unterscheidung wird hier getroffen zwischen:
POS Kasse
(veraltet – wird nicht mehr gepflegt)
Tresenkasse
Marktkasse
Zahlung
Achtung:
Ein Wechsel des Barverkaufs in eine Rechnung ist nur
sinnvoll, wenn vor der Erfassung des Positionsteiles die Kundennummer angegeben
wurde.

---

## Fehlerbericht

Fehlerbericht
Das Kassenbuch wird auf typische Unstimmigkeiten
untersucht. Alle Problemfälle werden Fehlerbericht aufgelistet. Weiter gehende
Hilfen werden in den jeweiligen Abschnitten angeboten.

---

## FIREO

FIREO
Für die Finanzbuchhaltung kann der Test der
Bewegungsdaten einfach per Event gestartet werden. Die Reorganisation wird
bewusst nicht angeboten, da eventuell auftretende Fehler korrekt abgearbeitet
werden sollen und zur Not der Branchen-ERP-Hotline gemeldet werden sollen. Um die
Vorlage für dieses Event zu aktivieren, muss auf dem Register „Vorlagen“
Fireo
auf
Ja
gestellt werden.
Der Prozeduraufruf, der auf dem Register „Verarbeitungsroutine“ zu finden ist,
muss noch ein wenig angepasst werden.
Für diese Automation kann die
Ausgabedatei
unter Optionen
[OPT]
festgelegt werden
Funktionsweise des
Fireo
:
Das Referenz-ERP Programmstart.vbs Skript kopiert die
Aeins.exe und benennt diese dann in den Wert des Übergabeparameters um. Danach
werden alle aktiven Referenz-ERP-Prozesse auf dem Datenbank Server gekillt. Erst
danach startet das Referenz-ERP Programm mit der ausgewählten Reorganisation.
Achtung der Parameter
„Kill“ beendet alle Referenz-ERP-Prozesse die auf dem Datenbankserver
laufen.
Deswegen wird der Parameter nicht
Vorbelegt. Um zu testen, ob der FIREO Aufruf funktioniert, kann dieser unter
OSQL getestet werden. Aber beim Test muss der Kill Parameter leer sein.
Aufruf der Fireo Prozedur
begin
call
fireo_automatisch(
in_systempfad   =
'c:\\aeins\\bin\\aeins_programmstart.vbs'
,
in_section
=
'entw'
,
in_schema       =
''
,
in_schemadatei  =
''
,
in_user         =
'<User>'
,
in_passwort     =
'<Password>'
,
in_kill         =
''
,
in_exe          =
'A1entw'
,
in_dsn          =
'entw'
,
in_dauer        =
0
,
in_fireo_aufruf =
''
)
end
Parameter Übersicht
Bedeutung
in_systempfad
Pfad
      zum VBS Script Referenz-ERP Programmstart. Da das Event auf dem Datenbankserver
      läuft, muss dies das Referenz-ERP-Verzeichnis sein, auf das man vom
      Datenbankserver zugreifen kann.
in_section
Section der amicconf.ini
in_schema
Schema des Datenbank
      Servers
in_schemadatei
Schemadatei des Datenbank
      Servers
in_user
Anmeldungs Benutzer
in_passwort
Anmeldungs Passwort
in_kill
Been
[...]


---

## Formulare in der Basis-DB

Formulare in der Basis-DB
Formular
Bezeichnung
Formulartyp
100
Angebot Druck
Standardvorgang
101
Angebot Vorschau
Standardvorgang
102
Angebot Erfassung
Standardvorgang
111
Formular für
      Itembox-Druck
Listen
112
Formular ITEM-Box
      HP-Drucker
Listen
190
Storno Angebot Druck
Standardvorgang
191
Storno Angebot Vors.
Standardvorgang
192
Storno Angebot Erf.
Standardvorgang
400
Auftrag Druck
Standardvorgang
401
Auftrag Vorschau
Standardvorgang
402
Auftrag Erfassung
Standardvorgang
490
Storno Auftrag Druck
Standardvorgang
491
Storno Auftrag
      Vorschau
Standardvorgang
492
Storno Auftrag
      Erfassung
Standardvorgang
600
Lieferschein Druck
Standardvorgang
601
Lieferschein Vorschau
Standardvorgang
602
Lieferschein
      Erfassung
Standardvorgang
690
Storno Lieferschein
      Druck
Standardvorgang
691
Storno Lieferschein
      Vorschau
Standardvorgang
692
Storno Lieferschein
      Erfassung
Standardvorgang
700
Rechnung Druck
Standardvorgang
701
Rechnung Vorschau
Standardvorgang
702
Rechnung Erfassung
Standardvorgang
Im Programmteil
Formularzuordnung
[FRZ]
werden die WaWi - Formulare an
Vorgänge gebunden.
FIBU - Formulare werden entweder direkt vor Druck
abgefragt
(Buchungsjournal, Kontenblatt) oder als Konstanten des
jeweiligen Programmteils
(Zahlungsverkehr, Mahnen) verwaltet.
Vorg.-Klasse
Ukl-Nr
U-Klasse
Druck
Vorschau
Bildschirm
Angebot
0
Angebot
100
101
102
Angebot
1
Bestätigung
400
401
402
Angebot
9998
Ordersatz
100
101
102
Storno Angebot
0
Storno Angebot
190
191
192
Auftrag
0
Auftrag
400
401
402
Auftrag
9998
Objekt
400
401
402
Storno Auftrag
0
Storno Auftrag
490
491
492
Ladeschein
0
VK-Ladeschein
600
601
602
Lieferschein
0
VK-Lieferschein
600
601
602
Lieferschein
1
Tresen-Lieferschein
600
601
602
Storno Lieferschein
0
Storno Lieferschein
690
691
692
Rechnung
0
VK-Rechnung
750
701
702
Rechnung
9900
Barverkauf
710
711
712
Storno Rechnung
0
Storno Rechnung
790
791
792
Gutschrift
0
VK-Gutschrift
800
801
802
Gutschrift
9900
Gutschrift Barverkauf
810
8
[...]


---

## Fremdware/ Fremdlager

Fremdware/ Fremdlager
Für die
Begriffsdefinition
Fremdware / Fremdlager
tauchen regional
unterschiedliche Interpretationen auf.
Im Folgenden
eine Begriffsbestimmung für die Verwendung in Referenz-ERP:
Fremdware
-
ist eine aus einem
Verkauf (im Sinne von Referenz-ERP einem Vorverkauf ) entstandene Ware, die in meinem
Lager liegt, mir aber nicht mehr gehört und auch nicht zu meinem IST- Bestand
zählt und meinen Eigenbestand vermindert.
Fremdlager
-
ist eine Ware, die von
mir bereits erworben wurde (im Sinne von Referenz-ERP Voreinkauf), aber noch beim
Lieferanten liegt. Sie gehört nicht zu meinem IST- Bestand, wohl aber zu meinem
Eigenbestand.
In Referenz-ERP wird
Fremdware oder Fremdlager durch Fremdware- und Fremdlagerkontrakte behandelt.
Bei
Erfassung
einer Fremdlager- oder
Fremdwarerechnung wird dieser Rechnung ein Fremdlager- oder Fremdwarekontrakt
zugeordnet, über den dann die
Lieferungen
abgewickelt werden. Die Erfassung der
Fremdware- oder Fremdlagerrechnung erfolgt in Referenz-ERP stets vor Erfassung der
ersten Lieferung. In der Bestandsführung sind Fremdware- oder Fremdlagerbestände
extra aufgeführt.

---

## Funktionalität

Funktionalität
Mit Hilfe der FutterApp können:
Bestellungen erfasst werden. Diese kommen als
XML-Datei im Verzeichnis (SPA 1047) an. Im Anschluss werden diese Dateien von
der im Event hinterlegten Routine verarbeitet. Die XML-Datei wird nun in das
Verzeichnis „\Import\Archiv“ oder bei einer Fehlermeldung in das Verzeichnis
„\Import\Fehler“ verschoben. Wenn der Import funktioniert hat, wird im
Verzeichnis „\Export\OrderConfirm“ eine Auftragsbestätigung geschrieben. In
Abhängigkeit des Parameters „Buchen“ (eingerichtet im Event“ findet sich der
Auftrag nun entweder im Vorgangsimport (
[VIMP]
) oder direkt bei den Aufträgen (
[AUB]
).
Silos bearbeitet oder gelöscht werden. Diese kommen
als XML-Datei im Verzeichnis (SPA 1047) an. Im Anschluss werden diese Dateien
von der im Event hinterlegten Routine verarbeitet. Die XML-Datei wird nun in das
Verzeichnis „\Import\Archiv“ oder bei einer Fehlermeldung in das Verzeichnis
„\Import\Fehler“ verschoben.
Nach der Einrichtung wird bei jeder Änderung von
FutterApp-relevanten Daten im Kundenstamm oder beim Erstellen von Aufträgen
(FutterApp-Kunde) ein Eintrag in der Tabelle „AMIC_AenderungsProtokoll“ mit dem
Status „0“ erzeugt. Beim nächsten Aufruf der Batchdatei durch die
Aufgabenplanung wird für jeden dieser Einträge (mit Status „0“) im zugehörigen
Ordner im Export-Verzeichnis eine XML-Datei geschrieben. Der Status wird auf „1“
gesetzt.
Um nachträglich noch Aufträge in die App zu
exportieren gibt es im Kundenstamm den Button „Historische Daten“. Es werden nun
alle Aufträge der letzten 365 Tage ins „AMIC_AenderungsProtokoll“
geschrieben.
Bei jedem Storno eines Auftrags (echtes Storno und
Gegenbeleg) wird im Verzeichnis „\Export\StornoAuftrag“ eine XML-Datei mit den
Stornoinformationen erzeugt.

---

## Funktion: Kasseneröffnung

Funktion: Kasseneröffnung
Dabei werden die Vortragswerte der Bargeldbestände der
letzten Sitzung an dieser Kasse übernommen und die Kasse bekommt eine eigene
neue Sitzungsnummer.
Ebenso wird eine Verbindung zum Display hergestellt,
falls es vorhanden ist.
Innerhalb eines Barverkaufssystems können an einer
Kasse mehrere Sitzungen abgehalten werden, jedoch ist höchstens eine aktiv. Dies
ist auch durch die dem Zustand entsprechenden möglichen Funktionalitäten
sichergestellt, es kann keine zweite Sitzung an dieser Kasse aktiv geschaltet
werden.

---

## Auswertungsanwendung Gesamtbarverkauf

Auswertungsanwendung Gesamtbarverkauf
(Auswertungen des Kassensystems)
Im Auswahlbildschirm lässt sich jederzeit ein
Überblick über die Werte des Kassensystems gewinnen. Mit den hier vorhandenen
Funktionen und Varianten kann ein Überblick über das Barverkaufssystem erreicht
werden.
Möglichkeiten hierzu bestehen u.a. innerhalb der
folgenden Varianten:
Varianten
Kasseneröffnung
Übersicht über die einzelnen
      Kassensitzungen. (Kasse, Sitzungen, Eröffnungs-Abschlusswerte u.a. ).
      Dabei handelt es sich in dieser Variante um die Bargeldbestände. Von hier
      sind auch CRW-Berichte aufrufbar.
Gutscheinbestand
Überblick über den aufsummierten
      Bestand an Gutscheinen nach Kassen und Sitzungen
Gutscheinüberblick
Hier
      sind alle Gutscheine einzeln aufgelistet
Scheckbestand
Überblick über den aufsummierten
      Bestand an Schecks nach Kassen und Sitzungen
Schecküberblick
Hier
      sind alle Schecks einzeln aufgelistet
Kreditkartenbestand
Überblick über den aufsummierten
      Bestand an Kreditkarten nach Kassen und Sitzungen
Transaktionssätze
      Kreditkarten
Hier
      sind alle Kreditkarten aufgelistet. In den Profilbedingungen gibt es
      zusätzlich den Transaktionsstatus, d.h. es können z.B. nur Kreditkarten
      angezeigt werden, die noch nicht per EC-Lastschrift-Verfahren exportiert
      wurden
Bankeinzugbestand
Überblick über den aufsummierten
      Bestand an Bankeinzügen nach Kassen und Sitzungen
Bankeinzugüberblick
Hier
      sind alle Bankeinzüge aufgelistet
Bemerkung: In den Überblicken ist es
      möglich, über F5 die Zahlungsmittelsätze nachträglich zu bearbeiten. So
      kann ein Systemadministrator die Kontonummer / Bankleitzahl ergänzen bzw.
      korrigieren. Außerdem kann man Zahlungsmittel unter gewissen
      Randbedingungen Stornieren / Drucken / Umwandeln.
Verkäufe/Einkäufe
Hier
      werden die Anzahl und Summe der Barvorgänge (Verkauf und Einkauf) nach
      Kasse und Sitzung angezeigt
Ein/Auszahlu
[...]


---

## Gesamtbarverkaufssystem (BVS) eröffnen/abschließen

Gesamtbarverkaufssystem (BVS) eröffnen/abschließen
Die Funktionen für das Barverkaufsystem sind u.a. in
der Anwendung Gesamtbarverkauf (Pulldown-Menu: Vorgang / Barvorgänge /
Gesamtbarverkauf, Hauptauswahlmenu: Warenwirtschaftssystem / Barvorgänge /
Gesamtbarverkauf) zu finden.
Bevor Kassenfunktionen ausgeführt werden können, muss
zuerst das Gesamtbarverkaufssystem eröffnet werden (F8).
Das Gesamtbarverkaufssystem selbst ist allerdings nur
zu eröffnen, wenn es noch kein geöffnetes Gesamtbarverkaufssystem gibt, d.h., es
gibt höchstens ein aktives System (BVS) pro Filiale.
Ebenso ist es nur möglich das Gesamtsystem
abzuschließen, wenn dieses System bereits eröffnet ist und es keine noch offenen
Kassensitzungen gibt. (F9)
Das Recht, das Gesamtbarverkaufssystem zu eröffnen,
liegt bei dem Benutzer, der in der Ahoi.ini unter [Acash2] den Eintrag
BVManager=Ja aufweisen kann.
Um zu ermitteln, welche Kassen noch offen sind, wird
eine Tabelle angezeigt, die über den Zustand der einzelnen Kassen
informiert.
Jede Barverkaufssystemeröffnung bekommt eine eigene
fortlaufende Sitzungsnummer.
Beim Abschluss des Barverkaufs werden die Werte aller
innerhalb der im Gesamtbarverkaufssystem durchgeführten Kassensitzungen mit der
Sitzungsnummer dieses Barverkaufs in die Zeile der Datenbank verprobt, die als
noch aktives Barverkaufssystem gekennzeichnet ist.
Weiter besteht die Möglichkeit, Zahlungsmittel
(Scheck, Kreditkarte, Bargeld, ...) automatisch beim Tagesabschluss auf
Kostenkonten zu verteilen.
Hierzu erforderliche Einstellungen sind:
Der
SPA 355 -
Buchung der Zahlungsmittel auf Kostenkto
in der Gruppe
Kasse/Barverkauf ist auf Ja zu setzen.
In den
Kasseneinstellungen
in der Gruppe Konten sind
für die Zahlungsmittel Kostenkonten aus der FiBu zuzuweisen.
Der Einrichterparameter Einzelbuchung pro
Zahlungsmittel auf der Maske des Kassenabschlusses steuert, ob jedes
Zahlungsmittel (z.B. jede EC-Karte) einzeln gebucht werden soll (Ja) oder nur
die Summe der Zahlung
[...]


---

## Google Maps Anzeige

Google Maps Anzeige
Wer auf eine Aufwendige Tourenplanung mit
Streckenoptimierung verzichtet, der kann die Wegpunkte an Google übertragen und
dort die Planung zurechtschieben.
Zu diesem Zweck gibt es zwei Aufrufe, die Daten aus
unterschiedlichen Quellen anzeigen:

---

## Hinzufügen von Bedingungen auf Basis dieser BI

Hinzufügen von Bedingungen auf Basis dieser BI
Es kann auch sinnvoll sein, innerhalb eine Mappe
mehrfach auf eine BI zuzugreifen, wobei jeweils andere Filterkriterien wirken,
soll z.B. einmal eine Verkaufsübersicht und gleichzeitig daneben eine
Einkaufsübersicht gebaut werden, so kann per einfachem kopieren des gesamten
Tabellenblattes und einfügen einer where Bedingung eine Filterung der Daten
erreicht werden.
Hierzu wird einfach der Befehlstext in den
Verbindungseigenschaften um die Bedingung erweitert, auch kann hier wie im
Beispiel zu sehen ist eine Sortiervorgabe angegeben werden:
SELECT *
from
admin.bi_SV_UEBERSICHT_Status_0
where v_klassnummer in
(400,490,600,690,700,790,800,890)
order by
Jahrnummer, Perinummer

---

## Informationen über Buchungen

Informationen über Buchungen
Buchungen in der Tabelle Warenbewegung werden an
verschiedenen Stellen dazu verwendet, Summen zu bilden. Kennzeichen
signalisieren, um welche Art von Buchung es sich handelt.
Vorgang
VorFakKennz
BestTyp
BestTyp
Reverse
Typ EKVK
Bew Art
Bew Code
Inv
Verkauf
0
0
0
2
0
20
1
Vorverkauf
0
0
0
2
0
1
1
Vorverkauf Abholung
0
1
0
0
1
11
1
Vorverkauf Rücknahme
0
0
1
2
0
21
1
Kommission
4
0
0
0
4
4
1
Kommission Verkauf
0
4
0
2
0
14
0
Kommission Rücknahme
0
0
4
0
4
24
1
Einkauf
0
0
0
1
0
10
1
Voreinkauf
1
0
0
1
0
2
0
Voreinkauf Anlieferung
0
2
0
0
2
12
0
Voreinkauf Rückgabe
0
0
2
1
0
22
1
Einlagerung
3
0
0
0
3
3
1
Einlagerung
      Vereinnahmung
0
3
0
1
0
13
1
Einlagerung Abholung
0
0
3
0
3
23

---

## Kasse/n eröffnen/abschließen

Kasse/n eröffnen/abschließen
Bevor an einer Kasse einzelne Barvorgänge erfasst
werden können, muss diese eröffnet werden (F9 in der Anwendung Gesamtbarverkauf,
dann F8).
Für die Kasseneröffnung / Abschluss ist unter Vorgang
/ Barvorgänge / Kasse Eröffnung/Abschluss ein Pulldown-Menu eingerichtet.
Über das Hauptauswahlmenu gelangt man über
Warenwirtschaft / Barvorgänge / Kasseneröffnung Abschluss.
Je nach Status der Kasse stehen die Abschluss- oder
die Eröffnungsfunktionen zur Verfügung.
So wird der Status der Kasse (eröffnet / abgeschlossen
/ unterbrochen) leicht erkennbar.

---

## Kommission aus Lager

Kommission aus Lager
Scanne den Auftrag (siehe Aufträge und
Kommissionierplatz verknüpfen), der kommissioniert werden soll. Anschließend
scanne den Regalplatz, wird dieser grün angezeigt, stimmt gewünschter Artikel
und angegebene Partie überein. Nach Eingabe der zu entnehmenden Menge wird die
Menge gelb unterlegt Als nächstes wird die im Regal verbleibende Restmenge
eingegeben. Stimmt die gezählte Restmenge mit der Menge im System überein, wird
die Menge grün. Ist das nicht der Fall wird eine Fehlermeldung ausgegeben, in
der die Menge aus dem System erscheint. Hat man die Restmenge im Regal geprüft
und gibt die ermittelte Menge erneut ein, wird diese als korrekte Restmenge
akzeptiert und gebucht. Die Fehlmenge wird im Fehlmengenregal des Benutzers
gebucht. Nach Eingabe der Prüfziffer verschwindet die Zeile aus dem Auftrag, da
dieser Artikel nun kommissioniert ist. Unten ist der Ablauf grafisch
beschrieben:
Wenn nicht genügt Ware für den Auftrag im Lager
vorhanden ist, so erscheint folgende Anzeige:
Im System sieht es dann folgendermaßen aus:
Hinzu kommt dann noch die Liste der Fehlmengen des
Benutzers:
Die Fehlmengenliste wird regelmäßig geleert.
Auftragsfreigabe zum Lieferschein
Sind alle Artikel im Auftrag vollständig kommisioniert
(richtige Partie und vollständige Menge), so kann eine Lieferscheinfreigabe
erfolgen (siehe Bild).
Mit der Taste „F2“ wird ein Lieferschein erzeugt. Es
erscheint folgende Anzeige:
In der Anwendung „Auftragsbearbeitung“ in der Variante
„Aufträge mit Positionen“ wird bei dem entsprechenden Auftrag, die
Auftragsnummer grün unterlegt.

---

## Kompatibilität

Kompatibilität
Die Angabe des Buchungstyps löst die alten
Kontraktklassen 2 und 12 (Fremdlager VK, Fremdlager EK) ab. Aus
Kompatibilitätsgründen können in der Übersicht auch alte Vorverkaufs- bzw.
Voreinkaufskontrakte der Kontraktklassen 2 und 12 angezeigt werden. Neu erzeugt
werden diese Kontraktklassen jedoch nicht mehr.
Bisher war die Definition eines Kontrakts über die
Kontraktklasse möglich. Die Kontraktklassen 2 bzw. 12 zeigten an, dass es sich
um Fremdware bzw. Fremdlagerkontrakte handelte.
Mit Beginn der Einlagerung laufen diese Kontrakte aus.
Es wird ein zusätzliches Kennzeichen, der KtrBuchTyp eingeführt. Dieser
Buchungstyp gibt bei Einkaufs- und Verkaufskontrakten künftig an, um welche Art
von Kontrakt es sich handelt.
Felder aus der Tabelle
      Kontraktstamm
Kontraktklasse
KtrKlasse
Buchungstyp
KtrBuchTyp
Alte
Kontraktklasse
Beschreibung
1
0
1
Verkaufskontrakt
1
1
2
Vorverkaufskontrakt (Fremdware
      Verkauf)
1
4
---
Kommission Verkauf
11
0
11
Einkaufskontrakt
11
2
12
Voreinkaufskontrakt (Fremdlager
      Einkauf)
11
3
---
Einlagerungskontrakt
Bei allen Reporten und Auswertungen muss also künftig
diese neue Konstellation parallel zu der auslaufenden alten Konstellation
berücksichtigt werden. Bestehende privater Reports müssen angepasst werden.
Die ausgelieferten Reports, Auswahllisten und
Itemboxen sind bereits angepasst worden, zeigen jedoch zum Teil nur die bisher
verfügbaren Informationen an. Für Wünsche zur Ergänzung oder Hinweise zu
unbearbeiteten Listen sind wir dankbar. Kontaktieren Sie bitte den Support.

---

## Kommissionierung im Ernährungsmittelbereich

Kommissionierung im Ernährungsmittelbereich
„Best Practice“ Beispiel Ernährung
Grundlagen :
-
In einer Produktionsstrecke werden Halbfertig- und Fertigprodukte
produziert.
-
Diese Produkte sollen direkt kommissioniert werden.
-
Die Produkte sollen eingelagert werden
-
Die Kommissionsaufträge sollen direkt zugeordnet werden
-
Während der Arbeit im Lager soll per permanenter Inventur der Bestand
gepflegt werden.

---

## Kostenstellenauswertung

Kostenstellenauswertung
Hauptmenü
Kostenrechnung
Kostenstellen
In der Anwendung „
Kostenstellenauswertung“
werden verschiedene Auswertungsvarianten angeboten. Alle Varianten bis auf die
Variante Kostenstellenbewegung stellen die Werte so dar, wie sie am Ende nach
Verteilung aussehen. Die Variante
Kostenstellenbewegung
zeigt die Werte
sowohl so an, wie sie erfasst wurden, als auch die Kostenstellen und Beträge,
wie sie nach der Verteilung aussehen. Hier kann sowohl nach der erfassten
Kostenstelle (Kostenstelle Quelle) als auch nach der Kostenstell, auf der der
Wert im Endeffekt landet (Kostenstelle Ziel) eingegrenzt werden.
Die Anwendung „
Verteilkst.Auswertung“
zeigt
die
Werte aus dem Beleg ohne die manuelle Verteilung an. Es wird je Jahr
und  Buchungsperiode der Saldo der Kostenstelle nach Konten ausgegeben.
Ausgewählt werden die Daten nach Jahr, Kostenstelle, Konto, Periode.
Weiterhin stehen noch diverse Reporte zur
Verfügung:
•
Kostenstellen-Periodenauswertung:
Hier werden pro Kostenstell
die Periodenwerte dargestellt, wie sie sich nach der Verteilung
ergeben.
•
Kst-Auswertung n. Auswertungspositionen:
Hier werden pro
Kostenstell die Periodenwerte gruppiert nach den externen Auswertungspositionen
dargestellt, wie sie sich nach der Verteilung ergeben.
•
Kostenstellen-Konto-Auswertung:
Eine einfach Liste, bei die
Kostenstelle mit allen bebuchten Konten dargestellt wird. Hierbei handelt es
sich um die Werte, so wie sie nach der Verteilung aussehen.
•
Konto-Kostenstellen-Auswertung:
Analog zu
Kostenstellen-Konten-Auswertung werden hier die Konten mit allen bebuchten
Kostenstellen dargestellt wird. Hierbei handelt es sich um die Werte, so wie sie
nach der Verteilung aussehen.
•
Verteilkostenstellenauswertung:
Hier werden pro Kostenstellen,
auf der die Beträge letztendlich gelandet sind, alle bebuchten Konten und die
Ursprungs-Kostenstelle dargestellt. Die Zahlen werden
mit manueller
Verteilung
,
direkter Erfassung
und
automatischer Verteilung
dar
[...]


---

## Kostenträgerauswertung

Kostenträgerauswertung
Hauptmenü
Kostenrechnung
Kostenträger
Kostenträgerauswertung
Direktsprung
[KSTRA]
Es werden verschiedene Auswertungsvarianten
angeboten:
•
Kostenträger
•
Kostenträger nach Konten
•
Kostenträger nach Perioden
•
BAB Einzel-Kostenträger
•
BAB Kostenträger Verdichtet / BAB Kostenträger Verdichtet mit GuV
Struktur
Selektiert werden die Daten nach Jahr, Kostenträger,
Konto, Periode

---

## Kurzbeschreibung der Dateien

Kurzbeschreibung der Dateien
bestellung_include.vbs
Diese Datei dient als Funktionssammlung sowie
Klassendefinition die von den beiden anderen VBS-Dateien verwendet werden. Sie
ist auch für später folgende VB-Skripte oder Projekte zu vorgesehen.
bestellung.vbs
Sie beinhaltet die Erzeugung der Vorgänge. Sie kann
auch ohne Automatismus über Parameter Vorgänge zu Testzwecken
(Fehlersuche/Entwicklung) erzeugen.
bestellung_start.vbs
Diese Datei liest aus den XML-Dateien die zu
generierenden Vorgänge, überprüft die Daten und stößt die
Vorgangserstellung/-bearbeitung in bestellung.vbs an.
autom_bestellung.xml
In dieser Datei sind zurzeit die zusammenhängen
Vorgänge „Neuer Vorgang“, „Neue Position“ und „Position zusammenführen“
beschrieben. Sie wird von dem Script bestellung_start.vbs eingelesen.
auftrag.xml
Wird zurzeit nicht verwendet. Sie dient zur
dynamischen Erzeugung von Aufträgen mit x-Warenpositionen und jeweils y-Partien
sowie deren Mengen. Ihre Auswertung ist ebenfalls in bestellung_start.vbs
implementiert.

---

## Ladeschein – aus Auftrag zu Lieferschein/Rechnung

Ladeschein – aus Auftrag
zu Lieferschein/Rechnung
Eine oder mehrere Auftragspositionen aus einem oder
mehreren Aufträgen können zu einem Ladeschein zusammengestellt werden. Dies ist
dort angezeigt, wo gemeinsam verladen werden soll.
Aber auch auf der Wareneingangsseite besteht die
Möglichkeit eine oder mehrere Positionen aus einer oder mehreren Bestellungen zu
einem Eingangs-Ladeschein (oder Entladeschein) zusammenzufassen.
In beiden Fällen soll im Vorgangsimport die Position
des Ladescheins zu einem (Eingangs/Ausgangs)-Lieferschein bzw. eine
(Eingangs/Ausgangs)-Rechnung gewandelt werden.
Dafür sind einige Voraussetzungen notwendig:
ImportTyp
Importtyp im
      ImportVorgStamm
NULL
Beleg wird in einen Lieferschein
      umgewandelt
0
Beleg wird in einen Lieferschein
      umgewandelt
1
ACHTUNG !!! Ladeschein wird erstellt
      !!!
2
Beleg wird in eine Rechnung
      umgewandelt
*
Wabewerfassid in der ImportVorgPosition
Um klarzustellen welche der ursprünglichen
Auftrags/Bestell-Positionen umgewandelt werden soll, muss die WaBewErfassId aus
der Warenposition des Ladescheins angegeben werden.
RestAusbuchKennz in der ImportVorgPosition
Zusätzlich ist es möglich das Feld „RestAusbuchKennz“
auf 1 zu setzen, um bei Mindermengen-Lieferung die Reste des Quell-Vorgangs
(Auftrag/Bestellung) auszubuchen.
*
* Hinweis:
Diese Funktion ist nur bei gleichzeitiger Verwendung des UseCS=1 im
ImportVorgstamm verwendbar!

---

## Lagerumb. Bei Lieferung Voreink.-Vorverk. (603)

Lagerumb.
Bei Lieferung Voreink.-Vorverk. (603)
Ja:     Bei Lieferungen für einen Voreinkaufs- oder
Vorverkaufskontrakt, die nicht auf oder von dem Lager erfolgen, auf dem die
Voreinkaufs- oder Vorverkaufsrechnung erfasst wurde, wird automatisch eine
Lagerumbuchung auf dieses Lager erstellt.
Nein:  Bei Lieferungen für einen Voreinkaufs- oder Vorverkaufskontrakt, die
nicht auf oder von dem Lager erfolgen, auf dem die Voreinkaufs- oder
Vorverkaufsrechnung erfasst wurde, wird keine Lagerumbuchung auf dieses Lager
erstellt. Dieses muss im Bedarfsfall per Hand erfolgen.

---

## Laufende Nummer von bis

Laufende Nummer von bis
Hier trägt man die Nummern der Belege ein.
Ein
Block mit Lieferscheinen der ausgegeben wird enthält z.B. 10 Seiten mit den
Nummern 1001 bis 1010.  Dann werden genau diese Nummern hier
eingetragen.
Aus dieser laufenden Nummer werden beim Speichern des
Datensatzes die Positionen erzeugt.
Wenn eine Nummer aus dem angegebenen
Bereich für den ausgewählten Typ schon in den Positionen vorhanden ist, dann
erhält man eine Warnmeldung in der man aufgefordert wird seine Angaben zu
überprüfen. Man kann den Datensatz nicht abspeichern, wenn eine Nummer schon
existiert.
Außerdem kann man keine ‚bis’ Eingabe machen die
kleiner als die ‚von’ Angabe ist.
Man erhält eine Warnmeldung und kann den
Datensatz nicht abspeichern.

---

## Lieferbelege

Lieferbelege
Lieferbelege sind dafür da um z.B. manuell ausgegebene
Lieferscheinblöcke zu verwalten und zu kontrollieren.
Man erreicht sie über den Direktsprung [liebe].
Sie bestehen aus dem Lieferbelegstamm und den
Lieferbelegpositionen.

---

## Liefermengen und fakturierte Mengen

Liefermengen und fakturierte Mengen
Es wird zwischen Liefermengen und fakturierten
Liefermengen unterschieden:
Mengenart
Beschreibung
Liefermengen
Die
      Bestandsführung auf Basis von Liefermengen ergibt sich aus
-
Lieferscheinen in
      Einkauf und Verkauf
-
Rechnungen/Gutschriften
      in Einkauf und Verkauf
-
Umbuchungen und
      Produktionsbuchungen
-
Inventuren
Auf
      der Bestandsführung von Liefermengen bauen solche Bestandsauswertungen
      auf, die den physikalisch vorhandenen Lagerbestand zu einem bestimmten
      Stichtag ausweisen.
Fakturierte Mengen
Die
      Bestandsführung auf Basis fakturierter Liefermengen ergibt sich
      aus
-
      Rechnungen/Gutschriften in Einkauf und Verkauf
-
      Umbuchungen und Produktionsbuchungen
-
      Inventuren
Auf
      der Bestandsführung fakturierter Liefermengen fußt die Bestandsbewertung.
      Um nämlich die Entwicklung dynamische Bewertungspreise wie etwa dem
      gewogenen und dem durchschnittlichen Einkaufspreis nicht durch „Ausreißer“
      zu belasten, berücksichtigen diese stets nur fakturierte Mengen. Auf
      fakturierten Beständen arbeiten im Übrigen alle
      Erfolgsauswertungen.
Die
      fakturierten Bestände werden im Übrigen stets nach Buchungsperioden, nicht
      nach Datums-bezogenen Lieferzeiträumen geführt.
Daneben existieren auch verbundene Auswertungen, die
auf Liefermengen aufsetzen und den Bestandswert der daraus resultierenden
Bestandsmenge ermitteln. Hierbei ist zu beachten, dass die Bestandsbewertung
stets auf Basis des fakturierten Anteils hochgerechnet wird.

---

## Lieferschein

Lieferschein
Lieferscheine entstehen durch Neuerfassung oder
Umwandlung aus Angeboten / Aufträgen. Lieferscheine werden als Vorgang
gespeichert, auf sie kann in Nachfolgevorgängen zugegriffen werden; die Menge
wird verbucht und vermindert den Bestand; Wertbuchungen erfolgen nicht. Referenz-ERP
stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktion
Bedeutung
Erfassen
F8
Erfassung eines neuen
      Lieferscheins
Stapelverarbeitung
Übernahme eines oder mehrerer
      Lieferscheine in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck eines
      Lieferscheins
Formulardruck
      F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur F5
Korrektur eines
      Lieferscheins
Ansicht
F6
Lieferschein im Ansicht-Modus
      öffnen
Kopieren
      CF8
Kopieren des Lieferscheins für einen
      auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren F7
Stornieren (Löschen) des
      Lieferscheins
Storno Lieferschein
Erfassung eines
      Stornobeleges
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
RE aus
      Lieferschein
Umwandeln in eine
      Rechnung
Sammel-Re aus
      Lieferscheinen
Umwandeln mehrerer Lieferscheine in
      eine Rechnung
Rücklieferung
      erfassen
Ausbuchen eines
      Restlieferscheins
Transportauftrag
Auftrag einer Spedition
      zuordnen
Rohware-Wandlung
Lieferschein in einen
      Rohwarelieferschein wandeln
Partien
      nachtragen
nachträgliche Zuordnung von
      Partien
Archiv
      ansehen
Anzeige archivierter
      Vorgänge
Wiedervorlage
      CF9
Vorgang mit einem
      Wiedervorlagevermerk versehen
Arbeitsregel ändern
manuelle Änderung von
      Weiterverarbeitungsparametern
PDF-Signieren
      SH-F12
Den
      ausgewählten Lieferschein
elektronisch
      unterschreiben

---

## Liste offene Aufträge/Bestellungen – auftrli.rpt

Liste offene Aufträge/Bestellungen – auftrli.rpt
Mit diesem Report kann man sich alle offenen
Aufträge/Bestellungen anzeigen lassen.
Im Auswahlbereich kann man die
Kundennummer/Lieferantennummer., die Auftragsnummer/Bestellnummer, das
Auftragsdatum/Bestelldatum, das geplante Lieferdatum und den Vertreter
eingrenzen.
Die Datensätze werden dem Vorgangstamm entnommen und
erst nach der Kundennummer (Feld Kundnummer) und dann nach der Auftragsnummer
(Feld V_NumNummer) sortiert ausgegeben.
Hinter der Kundennummer wird in einem
Feld die zur Kundennummer (über KundIdZuord) gehörige Bezeichnung aus dem
Kundenstamm angegeben. Dahinter werden, wenn gefüllt, noch die Felder
AdressVorname, AdressZeile1 und AdressStrasse zur Versandadresse aus dem
Vorgangstamm (V_VersAdressId) angezeigt. Dabei handelt es sich immer um die
Versandadresse des ersten Datensatzes aus dem Vorgangstamm der zu diesem Kunden
gefunden wurde.

---

## Optionen

Optionen
Sprache
Hier kann man die Sprache von der
Artikel Beschreibung festlegen.
Anzeige Journal
Datenübertragung
Zeigt das Journal der übertragenen Daten an
(CSV/PDF/Auftrag). Erlaubt Wiederholung der
Übertragung.
FTP
Erlaubt Backup, Import/Export von CSV, Bilder,
Dokumenten von einem FTP Server.
iTunes
Erlaubt Backup nach
iTunes.
Lagerbestände aktualisieren
Aktualisiert alle
Lagerbestände (funktioniert nur mit MobiSync Server).
GPS Daten
ermitteln
Fügt zu allen Adressen GPS Positionen hinzu. Lange
Laufzeit.
Lösche Bilder/Dokumente
Löscht alle auf dem Gerät
gespeicherten Bilder zu den Artikeln.
Beleg Konfiguration
Hier
können Sie Ihr Beleg frei konfigurieren. Diese Funktion wird erst ab 4.2
angeboten.
Systemtabellen bearbeiten
Erlaubt Redaktion von
Zustellungsarten, ebenfalls wird erst ab 4.2 angeboten.
Lösche
Datenbank
Löscht die Datenbank (Bilder bleiben erhalten).
Nutzen Sie
diese Funktion, wenn Sie z.B. von der Demo Datenbank zu FTP Import wechseln
wollen.
Support
Sendet Datenbank, Gerätennummer und
Fehlerprotokoll an nexti gmbh.
Einstellungen
Import-Pfade, FTP
Einstellungen, Systemeinstellungen, etc.
Mandant ändern
Erlaubt
zwischen mehreren Mandanten zu wählen.

---

## Ordersatz

Ordersatz
Hauptmenü
Warenverkauf
Angebot
Ordersätze
oder Direktsprung
[OSB]
In Ordersätzen werden für einen Kunden Artikellisten
mit Preisen zusammengestellt, auf die bei der eigentlichen Vorgangserfassung,
z.B. beim Telefonverkauf, unterstützend zurückgegriffen werden soll (Funktion
Ordersatz
bei der
Vorgangserfassung). Ordersätze werden verwaltet und anderen Vorgangsklassen
bereitgestellt; Bestandsbuchungen nach Menge und Wert erfolgen nicht.
Funktion
Bedeutung
Ordersatz
      erfassen
F8
Erfassung eines neuen
      Ordersatzes
Ansicht
F6
Ansicht eines
      Ordersatzes
Stapelverarbeitung
Übernahme eines oder mehrerer
      Ordersätze in einen Bearbeitungsstapel
Erstdruck
F9
Erstdruck eines
      Ordersatzes
Formulardruck
F10
Wiederholungsdruck
Korrektur
F5
Korrektur eines
      Ordersatzes
Kopieren
CF8
Kopieren des Ordersatzes für einen
      auszuwählenden Kunden
Vorschau
F11
Druckvorschau
Archiv anzeigen
CF12
Anzeige archivierter
      Vorgänge

---

## PDF-Drucken

PDF-Drucken
Diese Funktion ist über
Dokumentenverwaltung-
Multifunktionsleiste
und über die Anwendung
Anwendung Formulararchiv
verfügbar.
Nach Auswahl von Dokumenten werden die PDF-Dokumente
gefiltert und zum Druck angeboten.
Felder:
Drucker
Pflichtfeld
Angabe des
      Windows-Druckers
Die
      Online-Verfügbarkeit wird geprüft und optisch durch einen grünen Haken
      belegt.
Mausklick auf dieses Sysmbol oder
      betätigen der F3-Taste ruft den „Windows-Drucker-Auswahl-Dialog“
      auf.
Die
      Angabe des Druckers wird sich für den erneuten Aufruf gemerkt und ist bei
      Ersteintritt der Windows-Standard-Drucker.
PDF-Dokumente
Anzeige
Anzahl der zu druckenden
      Dokumente
Funktionen:
Drucken
F9
Druckt die vorgesehenen Dokumente
      auf den ausgewählten Drucker
Der PDF-Druck ist programmatisch durchführbar.
1)
Für Makro2 siehe IArchiv.PrintPDF.
2)
Für andere Scriptsprachen steht die JPP-Methode „PrintPdf“ im JPP-Objekt
„JFA_View“ zur Verfügung.
Parameter:
fa_id
Schlüssel
fa_mndnr
Schlüssel (Angabe
      optional)
printer
Drucker

---

## Pivot Tabellen erstellen

Pivot Tabellen erstellen
Eine einfache Pivot-Tabelle lasst sich nun bequem auf
dem Template der BI Anwendung erstellen, dazu wird zunächst ein neues
Tabellenblatt geöffnet, und der Name des Blattes wird an den Inhalt angepasst,
wie z.B.: Verkaufspivot.
Jetzt wird einfach auf den kleinen roten Pfeil im
Bereichsauswahlknopf gedrückt, um dann das Blatt Verkauf anzusteuern:
um hier dann ALLE Spalten des Datenbereiches
auszuwählen. Es ist wichtig, dass hier $A:$V und nicht $A1:$V45987 steht, da bei
nicht spaltenorientierten Bereichseingrenzungen dann leider bei mehr als z.B.
45987 Datensätzen Fehlberechnungen entstehen.
Durch auslösen der RETURN Taste und dem Bestätigen des
OK Felder in der Pivotbereichsmaske kann nun bequem die Pivoauswertung
zusammengestellt werden.
Wichtig hierbei ist wieder, dass nach Abschluss der
Designarbeiten die Excel Datei in der Datenbank abgelagert wird. Ein weiterer
Hinweis bezieht sich auf den
automatischen Refresh
teil der
Excel Pivot Anwendung, die Daten werden nicht in jedem Falle neu aus dem
Datenbereich gelesen, hierzu muss dem Excel System mitgeteilt werden, dass nach
erfolgreichem Lesen der Daten aus der Datenbank die Pivotabelle (oder Tabellen)
automatisch neu berechnet werden sollen, hierzu ist der entsprechende
Absatz
zu
lesen.

---

## Preislistennummern 1 bis 4

Preislistennummern 1 bis 4
Wird in einer Angebotsliste ein Preis verändert, so
kann dieser auch gleichzeitig als Listenpreis beim Artikel nachgetragen werden,
diese Parameter geben die zugehörigen Listenpreisnummern an.

---

## Privatisierung

Privatisierung
Für den Import von Bestellungen kann die Prozedur
„AMIC_FutterApp_BelegImport“ angepasst werden (z.B. können hier Informationen in
UFLD-Felder geschrieben werden). Die Prozedur ist im Steuerparameter „FutterApp
Optionen und Ausprägungen“ (SPA 1047) unter dem Punkt „SQL-Prozedur zum
Beleg-Import“ (2) eingetragen werden. Ohne Eintrag wird die Standardprozedur
gezogen.
Für den Import von Siloinformationen kann die Prozedur
„AMIC_FutterApp_Siloverwaltung“ angepasst werden. Die Prozedur ist im
Steuerparameter „FutterApp Optionen und Ausprägungen“ (SPA 1047) unter dem Punkt
„SQL-Prozedur zur Siloverarbeitung“ (3) eingetragen werden. Ohne Eintrag wird
die Standardprozedur gezogen.
Für das Maschinentagebuch, welches die Einträge in der
Tabelle „AMIC_AenderungsProtokoll“ vornimmt, kann die Prozedur
„AMIC_FutterApp_MaschinentagebuchVersorgung“ angepasst werden. Die Prozedur ist
im Steuerparameter „FutterApp Optionen und Ausprägungen“ (SPA 1047) unter dem
Punkt „Privater Abschnitt des Maschinentagebuch“ (1) eingetragen werden. Ohne
Eintrag wird die Standardprozedur gezogen.
Zum vereinfachten Finden von fehlerhaft importierten
Dateien wird die Warningfunction „FutterAppWarnungAuftrag“ zur Verfügung
gestellt. Diese kann in der Auswahlliste
[AUB]
hinterlegt werden und blendet ein
gelbes Ausrufezeichen im Hintergrund der neuen Auswahlliste ein, sollten sich
Dateien im Verzeichnis „\Import\Fehler“ befinden (Auf Zugriffsrechte muss
geachtet werden).

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

## Rechnung

Rechnung
Rechnungen entstehen durch Neuerfassung oder
Umwandlung aus Angeboten / Aufträgen / Lieferscheinen. Rechnungen werden als
Vorgang gespeichert, auf sie kann in Nachfolgevorgängen zugegriffen werden; die
Menge wird verbucht und vermindert den Bestand; der Umsatz erhöht sich. Referenz-ERP
stellt folgende Bearbeitungsfunktionen zur Verfügung:
Funktionsname
Funktion
Erfassen F
      8
Erfassung einer neuen
      Rechnung
Stapelverarbeitung
Übernahme einer oder mehrerer
      Rechnungen in einen Bearbeitungsstapel
Erstdruck
      F9
Erstdruck einer Rechnung
Formulardruck
      F10
Wiederholungsdruck
Lieblingsdruckerdruck
Auswahl eines anderen Druckers /
      Zuordnung eines anderen Formulars
Korrektur
      F5
Korrektur einer Rechnung
Ansicht F6
Rechnung im Ansicht-Modus
      öffnen
Schnellkorrektur
Plandatum und Menge
      ändern
Kopieren
      CF8
Kopieren der Rechnung für einen
      auszuwählenden Kunden
Vorschau
      F11
Druckvorschau
Stornieren
      F7
Stornieren (Löschen) der
      Rechnung
Storno
      Rechnung
Erfassung eines
      Stornobeleges
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Gutschrift aus
      Rechnung
Umwandeln in eine
      Gutschrift
Sammel-GU aus
      Rechnungen
Umwandeln mehrerer Rechnungen in
      eine Gutschrift
Transportauftrag
Auftrag einer Spedition
      zuordnen
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
EDI-Datentransfer
Bearbeitet den ausgewählten Beleg
      nach dem Profil des im Kunden hinterlegten EDI-Partners. Dabei werden die
      Felder „EDI-Partner“ und „Export“ in der Auswahlliste bewi
[...]


---

## Rechnungsausgangsbuch (RAB)

Rechnungsausgangsbuch (RAB)
Im Rechnungsausgangsbuch
[RBUA]
können die gedruckten Verkaufsvorgänge
(Rechnungen, Storno Rechnungen, Gutschriften, Storno Gutschriften) – nach
Geschäftsjahr getrennt – abgelegt werden. Somit erhalten Sie eine Übersicht über
die an Ihre Kunden geschickten Belege. Es können nur gedruckte Vorgänge ins RAB
übernommen werden. Im RAB abgelegte Vorgänge stehen der Vorgangsbearbeitung
nicht mehr zur Verfügung.
Das RAB besteht aus fortlaufend durchnummerierten
Drucklisten (s. Nummernkreis). Eine RAB-Liste wird über die Funktion
Erstdruck RAB
erzeugt. Es erscheint ein
Auswahlmenü mit weitgehenden Selektions-, Sortier- und Gruppierungsfunktionen.
So ist z.B. denkbar, dass für jeden Monat eine RAB- Liste gedruckt wird.
Nach dem Erstdruck erscheint die RAB-Liste in der
Auswahlliste Rechnungsausgangsbuch. Dort sind wichtige Grunddaten des
Listeninhalts, wie z.B. Anzahl der enthaltenen Belege, jüngstes/ältestes
Belegdatum, sowie Umsatzwerte (Summe).
Funktionen
Nummernkreis setzen
Vor Eröffnung des Rechnungsausgangsbuches sollte unter
NUK ein eigener Nummernkreis eingerichtet werden. Der Nummernkreis kann unter
Nummernkreis setzten
F8
per
F3
ausgewählt werden. Die nächste Nummer
lässt sich hier setzen, sowie Text und Ober-/Untergrenze.
ACHTUNG! Wird die nächste Nummer geändert, wenn schon
RAB-Listen erstellt wurden, werden u.U. die vorhandenen Listennummern
automatisch angepasst!
Löschen RAB
Löschen der RAB- Listen für das in der Auswahlliste
unter Bereich eingetragene Jahr.
Erstdruck RAB
Erstellung einer RAB-Liste nach Selektionskriterien.
Vor der Erstellung wird zunächst geprüft, ob alle Belege im Selektionsbereich
freigegeben sind. Falls noch Belege bearbeitet werden, erscheint eine
Abfrage:
HINWEIS: Ein(ige) Beleg(e) im Auswahlbereich noch in
Bearbeitung! RAB- Liste trotzdem starten?
Eine Bejahung der Frage erstellt eine RAB-Liste mit
den freigegebenen Belegen. Auf dem Listendeckblatt ist in diesem Fall ein
deutlicher Hinweis
[...]


---

## Relation RohwareHauptsatz_Waage

Relation RohwareHauptsatz_Waage
Die Relation RohwareHauptsatz_Waage nimmt die
Rohwarendaten auf.
Aus dieser Zwischenrelation werden über die
Aeins-Funktionen CWLU_EK (für Einkauf) und CWLU_VK (für Verkauf) (Aufruf der
JPL-Prozedur
cwegvorb
) die Lieferscheine erzeugt.
Anmerkung:
Die zugehörigen Qualitäten werden in einer
Unterrelation
RohwareZusatzQualitaet_Waage
gespeichert (s. unten).
Artikelnummer
char       20 0 .................... N
N
BedKennz_InVorgang
integer     4 0 .................... Y  N
BedKennz_VonWaage
integer     4 0 .................... Y  N
BelDatum_InVorgang
date        4 0 .................... Y
N
BelNummer_InVorgang
integer     4 0 .................... Y  N
CreateTime_VonWaage
integer     4 0 .................... Y  N
Datum_InVorgang
date        4 0 .................... Y
N
Datum_VonWaage
date        4 0 .................... Y
N
EKVK_Kennzeichen
integer     4 0
0
N  N
Fakturiergruppe
integer     4 0
0
Y  N
Filialnummer
integer     4 0
-1
N  N
FilName_VonWaage
char       12 0 .................... Y
N
Haupt_Kontraktnummer
integer     4 0
0
N  N
Haupt_Partienummer
integer     4 0
0
N  N
Kundennummer
integer     4 0 .................... N  N
Lagernummer
integer     4 0 .................... N  N
Lagerplatznummer
integer     4 0
0
Y  N
LfdNummer_VonWaage
integer     4 0 .................... Y  N
Lieferscheindatum
date        4 0
today(*)
N  N
Lieferscheinnummer
integer     4 0
0
N  N
LKW_Nummer
integer     4 0 .................... N  N
Menge
[...]


---

## Sammelumwandlung

Sammelumwandlung
Bei der Sammelumwandlung (nur bei
Verkaufslieferscheinen!) ist die zusätzliche Option ‚mittlere Valuta’
hinzugekommen. Die Valutierung der Rechnung wird aus der nach Belegwert
gewichteten Valutierung der zusammengefassten Lieferscheine gemittelt.
Achtung:
Dieses Verfahren ist nur sinnvoll, wenn in den
Lieferscheinen folgende Bedingungen erfüllt sind:
In der Zahlungsbedingung muss ‚Bezug auf Lieferdatum’
eingestellt sein.
Es darf nur der Zahlungsbedingungstyp ‚1 = fällig in n
Tagen’ benutzt werden
Mit angeschalteter Option ‚Einstellbare Trennungen
einmalig ausschalten‘ wird bei der Umwandlung von Eingangslieferscheinen in
Sammelrechnungen, Bestellungen in Sammellieferscheinen oder Sammelrechnungen die
Prüfung der per Steuerparameter aktivierbaren Umwandlungs-Trennkriterien
unterdrückt. Das kann zum Beispiel sinnvoll sein, wenn eine eingegangene
Sammelrechnung zu bereits erfassten Eingangslieferscheinen per Umwandlung
‚Nacherzeugt‘ werden soll, die eingeschalteten Trennkriterien dieses aber
verhindern würden.
Die Einstellung für die Vorbelegung bei Umwandlung von
Eingangslieferscheinen in Sammelrechnungen wird mit dem Steuerparameter
SPA1123
vorbelegt und wird aus
Sicherheitsgründen nicht gespeichert. Sie gilt somit nur für den aktuellen
Umwandlungsprozess!
Mit den Steuerparametern 1137 wird bei Umwandlung von
Bestellungen in Eingangslieferscheinen entschieden, wie die Checkbox
Einstellbare Trennung einmalig ausschalten
, vorbelegt ist. Siehe.
SPA1137
Mit den Steuerparametern 1138 wird bei Umwandlung von
Bestellungen in Sammelrechnungen entschieden, wie die Checkbox
Einstellbare
Trennung einmalig ausschalten
, vorbelegt ist. Siehe.
SPA1138

---

## SEPA in den Zahlungsarten

SEPA in den Zahlungsarten
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Zahlungsarten
Direktsprung
[FIZAH]
.
1)
DTA-Typ
Im Zuge der
SEPA-Einführung wurden die DTA-Typen Einzugsermächtigung und Abbuchungsauftrag
durch Basislastschrift, Basislastschrift mit verkürzter Vorlauffrist und
Firmenlastschrift ersetzt. Diese werden nicht mehr in den Stammdaten für
Zahlungsarten
gepflegt sondern im
Mandat
. Die Basislastschrift mit
verkürzter Vorlauffrist steht erst ab SEPA-Version 2.7 zur Verfügung. Diese
wurde zum 4.November 2013 deutschlandweit eingeführt, wird aber aller
Voraussicht nach erst zum 01.Februar 2014 von den Banken umgesetzt. Außerdem ist
es möglich, dass die Kreditinstitute auch über diesen Zeitraum hinaus die
Version 2.5 annehmen.
2)
Echtzeitüberweisung
Bei Zahlungsarten mit
Formularklasse
Zahlungsausgang
kann man Echtzeitüberweisung auf Ja
stellen. Es werden dann im automatischen Zahlungsverkehr beim Erstellen der
Zahlungsvorschläge (Direktsprung [ZHVE]) alle Belege gezogen, deren Fälligkeit
vor dem
nächsten Stichtag
liegt und als Ausführungsdatum wird der
Stichtag
verwendet.

---

## Shop

Shop
Im Shop sind können die, in der Referenz-ERP Software
existierenden Artikel, angezeigt werden.
Der Shop bietet die Möglichkeit vor Ort einen Auftrag
für den Kunden zu erstellen. Hierfür wählt man den/die gewünschten Artikel, mit
dem „Plus“-Symbol, aus und fügt diesen dem Warenkorb hinzu. Danach navigiert man
in den Warenkorb um den Auftrag zu erstellen.

---

## Signieren von Lieferscheinen

Signieren von Lieferscheinen
In Zusammenhang mit dem Formulararchiv können jetzt
auch archivierte Lieferscheine (PDF und TIFF) mit einer per PAD erfassten
digitalen Unterschrift versehen werden. Hierzu wird per USB das StepOver
Signierpad (
http://www.stepover.de
) an
den Rechner angeschlossen, der Lieferschein wird in der Auswahlliste markiert
und mit der Funktion Signieren dem Unterschriftspad bereitgestellt.
Nach erfolgter Unterschrift auf dem Lieferschein wird
der Signiervorgang abgeschlossen und der so unterschriebene Lieferschein wird
zusätzlich zu dem schon (nicht unterschriebenen) Lieferschein im Archiv
abgelegt.

---

## Speichern unter auf Vorgangsebene

Speichern unter auf Vorgangsebene
In den Auswahllisten der Bereiche Bestellung,
Eingangslieferschein, Eingangsrechnung und Eingangsgutschrift sowie Angebot,
Auftrag, Lieferschein, Rechnung und Gutschrift gibt es die Möglichkeit, einen
oder mehrere Belege anzuwählen, um dann aus diesem oder diesen Belegen einen
neuen Beleg zu erstellen.

---

## Spezialität bei Aufträgen

Spezialität bei Aufträgen
Bei der Umwandlung gibt es das Häkchen ‚Nimm
Plandatum’. Ist dieses gesetzt, so wird die Eingabe des Belegdatums ausgeblendet
und das Plan / Lieferdatum des Auftrags wird als Belegdatum des Lieferscheins
herangezogen.

---

## Sprache der Reporte

Sprache der Reporte
Die Festtexte der Reporte für die Streckenerfassung
können in verschiedenen Sprachen dargestellt werden.
Pflege Anwendungsformat
Dazu muss zunächst das Anwendungsformat
AF_VMAPVREP (Vorgangsmappe Reportoptionen) gepflegt werden. Hier kann man z.B. 0
– Deutsch, 1 – Englisch  usw. eingeben.
Zur Pflege des Formates gelangt
man
entweder über die Maske der Strecke, Register Planung, im Feld oberhalb
der Reporte F3 wählen dann Rechtsklick-Funktionen-Stammdatenpflege
oder
Direktsprung [forma], Variante Anwendungsformate, dort Formatname AF_VMAPVREP
eingeben und über Ändern F5 pflegen.
Pflege Druckfelder
Danach müssen die Druckfelder für die
unterschiedlichen Sprachen hinterlegt werden.
Dies geschieht unter
Direktsprung  [FRM], Variante Druckfelder, F8 für die Neuanlage.
Im Feld
Name muss der Name des Druckfelder angegeben werden (so wie er im Report
verwendet wird). Die genauen Bezeichnungen entnimmt man der Hilfe für den
jeweiligen Report.
Im Feld Ausprägung wird dann die gewünschte Sprache
ausgewählt (die zuvor im Format angelegt wurde).
Im Feld Inhalt wird dann
der Text eingegeben der gedruckt werden soll.
Druckfelder können in mehreren Reporten der
Streckenerfassung vorkommen!!!

---

## Starten der automatischen Vorgangserzeugung

Starten der automatischen Vorgangserzeugung
Zum Starten der automatisierten Vorgangserzeugung ist
der einfache Aufruf des VB-Skripts bestellung_start.vbs mittels doppelklick oder
per Kommandozeile notwendig. Parameter sind nicht erforderlich.
Für die Zeitdauer des Skriptlaufes (kann je nach
Rechner etwas dauern) ist das Referenz-ERP Icon in der Taskleiste sichtbar.
Falls dieses Icon nicht mehr verschwindet ist ein
unerwarteter Fehler aufgetreten!
Im Normalfall ist das Icon nach kurzer Zeit
verschwunden und die automatische Vorgangserzeugung erfolgreich beendet.
Voraussetzung der Vorgangserzeugung per VB-Skript ist
die Registrierung des Referenz-ERP COM-Objekt auf dem Client.

---

## Stornierung von Zahlungsmitteln

Stornierung von Zahlungsmitteln
In der AW Gesamtbarverkauf unter
Warenwirtschaftssystem/Barvorgänge gibt es die Möglichkeit, Zahlungsmittel
nachträglich zu bearbeiten:
Dabei besteht die Möglichkeit des Stornieren,
Umwandeln und Drucken (bei Zahlungsmittel Scheck kann auch ein Scheck erneut
gedruckt werden).
Diese Bearbeitung ist in den Varianten ...Überblick
des entsprechenden Zahlungsmittel sowie in der Variante Zahlungsmittelsätze
möglich.
1. Stornieren:
Ein Stornieren eines Zahlungsmittels mit dem Status
‚inKasse’ (d.h. das Zahlungsmittel ist physikalisch noch in der Kasse)
bewirkt:
a) Das Zahlungsmittel bekommt ein Stornokennzeichen
„storniert“.
b) Es gibt einen Eintrag in ein
Zahlungsmittel-Stornierungsprotokoll (AcashStoZamiProto).
c) Die Bestände des Zahlungsmittels in dieser Kasse
werden vermindert.
d) Wenn der SPA 51 "Automatische Buchung der
Zahlungsmittel in FiBu" gesetzt ist, wird von dem Zahlungsmittelkonto auf ein
Stornokonto gebucht.
e) Über diesen Vorgang wird ein Beleg gedruckt.
Hierbei besteht die Möglichkeit, durch EPA-Umstellung "Soll auf den Schacht
gedruckt werden", sich selbst ein Formular zu definieren (s.u.). Ansonsten wird
ein festes Formular auf dem Bon ausgedruckt.
2. Nachstornieren:
Ein Stornieren eines Zahlungsmittels mit dem Status
‚entnommen’ (d.h. das Zahlungsmittel ist physikalisch schon entnommen)
bewirkt:
a) Das Zahlungsmittel bekommt das Stornokennzeichen
„nachstorniert“.
b) Es gibt einen Eintrag in ein
Zahlungsmittelstornierungsprotokoll (AcashStoZamiProto).
c) Die Stornosumme/Anzahl des Zahlungsmittels wird in
die Relation AcashStoKsiz aufaddiert, die alle Nachstornierungen auf allen
Kassen je Barverkaufssystemsitzung aufkumuliert.
d) Wenn der SPA 51 "Automatische Buchung der
Zahlungsmittel in FiBu" gesetzt ist, wird von dem Zahlungsmittelkonto auf ein
Stornokonto gebucht.
e) Über diesen Vorgang wird ein Beleg gedruckt.
3. Drucken:
Es besteht die Möglichkeit, für obige Vorgänge ein
entsprechendes Formul
[...]


---

## Strecke

Strecke

---

## Streckenerfassung Report Einladekontrolle

Streckenerfassung Report Einladekontrolle
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Einladekontrolle
Kontrollauftrag Nr.:
an
an:
Bitte_Kontrolle
wir
      bitten um Einladekontrolle wie folgt:
Anrede
Sehr
      geehrte Damen und Herren,
Warenart
Warenart
Qualitaet
Qualität
Menge2
Menge
Kontrollsatz
Kontrollsatz
Ladestelle
Ladestelle
Absprache2
(Bitte sprechen Sie sich vorher mit
      der Ladestelle ab!)
Termin
Termin
BL_Datum
B/L
      Datum
Transportmittel
Transportmittel
Befrachter
Befrachter
Kontrolle
Kontrolle/Probenahme (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
Kontrolle_gemaess
Kontrolle gemäß
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Rechnungsempfaenger
Rechnungsempfänger (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Andienung

Streckenerfassung Report Andienung
(Im Speditionsgeschäft ist es die Mitteilung, dass die
Ware angekommen ist und bereitgehalten wird.)
(Die Andienung ist die physische Lieferung der
Ware
aus einem Warentermingeschäft.)
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Andienung
Andienung
Kontrakt
Kontrakt
vom
vom
via
via
an
an:
Textinfo_Andienung1
Hiermit dienen wir u.ü.V. in
1
(dazwischen liegt Text3 / Erfüllung
      aus den Streckentexten)
Textinfo_Andienung2
1
des oben genannten Kontraktes wie
      folgt an :
Ladestelle
Ladestelle
Loeschstelle
Löschstelle
Mfg
Mit
      freundlichen Grüßen
Menge2
Menge
BL_Datum
B/L
      Datum
Termin
Termin
Bitte_arrangieren
Bitte arrangieren Sie alles für eine
      ordnungsgemäße Entladung.
(wird nur angezeigt, wenn es in den
      Streckentexten angehakt wurde)
Hiermit_garantieren
Hiermit garantieren wir, dass die
      Fracht für o.g. Kontrakt bezahlt wird und dass die Charter Party den
      Kontraktbedingungen nicht widerspricht.
(wird nur angezeigt, wenn es in den
      Streckentexten angehakt wurde)
Befrachter
Befrachter (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Kontrolle_Andienung
Kontrolle (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
S
[...]


---

## Streckenerfassung Report Anlieferavis

Streckenerfassung Report Anlieferavis
Ein Lieferavis ist die Ankündigung eines
Lager
-
bzw. Warenzugangs. Der Lieferavis wird vom Lieferanten an den Empfänger der Ware
gesendet, bevor die Ware geliefert wird.
Mitteilung über die voraussichtliche Ankunft der Ware
beim Empfänger. Das Lieferavis enthält den voraussichtlichen Ankunftstermin, die
Mengen und die Materialien bzw. Dienstleistungen.
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Anlieferavis
Anlieferavis
an
an:
Info_disponiert
folgende Partie wurde für die
      Belieferung des u.g. Kontraktes auf Ihr Werk disponiert:
Anrede
Sehr
      geehrte Damen und Herren,
Transport_durch
Transport durch:
von_Ladestelle
von
      Ladestelle:
Termin
Termin
Absprache
(in
      Absprache mit allen Beteiligten)
circa
ca.
Kontrakt
Kontrakt
Menge2
Menge
Anliefernummer
Anliefernummer
Kontrolle
Kontrolle/Probenahme (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Freistellung

Streckenerfassung Report Freistellung
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Freistellung
Freistellung
An
an:
Kontrakt_Nr
Kontrakt Nr.:
via
via
mt
Anrede
Sehr
      geehrte Damen und Herren,
Info_Freistellung
gegen oben genannten Kontrakt
      stellen wir wie folgt zur Abnahme frei:
circa
ca.
Termin
Termin
Beladeort
Beladeort
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Nummer_Abholung
Bei
      Abholung bitte folgende Nummer angeben:
Avisieren
Bitte vor Abholung rechtzeitig
      avisieren
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Lade/Löschkontrolle

Streckenerfassung Report Lade/Löschkontrolle
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Kontrolle
Kontrollauftrag Nr.:
An
an:
Anrede
Sehr
      geehrte Damen und Herren,
Bitte_KontrolleLadeLoesch
wir
      bitten um Einlade/Löschkontrolle wie folgt:
Warenart
Warenart
Menge2
Menge
Kontrollsatz
Kontrollsatz
Ladestelle
Ladestelle
Loeschstelle
Löschstelle
Kontakt
Kontakt
Absprache3
(Bitte sprechen Sie sich vorher mit
      der Lade/Löschstelle ab!)
Termin
Termin
Transportmittel
Transportmittel
Befrachter
Befrachter
Kontrolle
Kontrolle/Probenahme (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
Kontrolle_gemaess
Kontrolle gemäß
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Rechnungsempfaenger
Rechnungsempfänger (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
MFG
Mit
      freundlichen Grüßen
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Löschkontrolle

Streckenerfassung Report Löschkontrolle
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_LoeschKontrolle
Kontrollauftrag Nr.:
An
an:
Anrede
Sehr
      geehrte Damen und Herren,
Bitte_LoeschKontrolle
wir
      bitten um Löschkontrolle wie folgt:
Warenart
Warenart
Menge2
Menge
Kontrollsatz
Kontrollsatz
Loeschstelle
Löschstelle
Absprache4
(Bitte sprechen Sie sich vorher mit
      der Löschstelle ab!)
Termin
Termin
BL_Datum
B/L
      Datum
Anliefernummer
Anliefernummer
Transportmittel
Transportmittel
Befrachter
Befrachter
Kontrolle
Kontrolle/Probenahme (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Rechnungsempfaenger
Rechnungsempfänger (wird
      ausgeblendet, wenn in den Streckentexten nichts eingegeben
      wurde)
MFG
Mit
      freundlichen Grüßen
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Nominierung

Streckenerfassung Report Nominierung
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Nominierung
Nominierung
An
an:
Kontrakt
Kontrakt
vom
vom
via
via
Textinfo_Nominierung1
Hiermit nominieren wir u.ü.V. in
(dazwischen liegt Text3 / Erfüllung
      aus den Streckentexten)
Textinfo_Nominierung2
des
      oben genannten Kontraktes wie folgt:
Menge2
Menge
Ladestelle
Ladestelle
BL_Datum
B/L
      Datum
Loeschstelle
Löschstelle
Befrachter
Befrachter (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Kontrolle_Nominierung
Kontrolle (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Bitte_arrangieren
Bitte arrangieren Sie alles für eine
      ordnungsgemäße Entladung.
(wird nur angezeigt, wenn es in den
      Streckentexten angehakt wurde)
Hiermit_garantieren
Hiermit garantieren wir, dass die
      Fracht für o.g. Kontrakt bezahlt wird und dass die Charter Party den
      Kontraktbedingungen nicht widerspricht.
(wird nur angezeigt, wenn es in den
      Streckentexten angehakt wurde)
MFG
Mit
      freundlichen Grüßen
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Transportauftrag

Streckenerfassung Report Transportauftrag
Der Transportauftrag ist die Anweisung an den
Spediteur, zu einem bestimmten Zeitpunkt Materialien von einem
Lagerort/Lagerplatz zu einem anderen zu transportieren.
Die Adresse an die der Transportauftrag geht ist die
Adresse des Spediteurs die für die Strecke angegeben wurde.
Im
Transportauftrag sind eine Lade- und eine Lieferadresse angegeben.
Die Anzeige dieser Adressen erfolgt in einer
bestimmten Reihenfolge je nachdem was gefüllt ist:
Adressfolge Lieferadresse :
1.
abweichende Ziel-Adresse
2.
Adresse des VK Lagers, wenn man den Transportauftrag für den EK Ladeschein
drucken will und auch ein VK Ladeschein existiert. (VK Lagertyp ungleich
Streckenlager)
Lagertyp
Streckenlager:
n
Versandadresse des Ladescheins
n
Versandanschrift des VK Kontraktes
n
Adresse des Kunden aus dem VK
Ladeschein
n
Adresse des VK Kontraktes
3. Versandadresse des Ladescheins
4. Versandanschrift des VK Kontraktes
5. Adresse des VK Kontraktes
1. abweichende Ziel-Adresse
Es gibt einen VK-Ladeschein zum
      EK-Ladeschein
VK Lagertyp ungleich
      Streckenlager
VK Lagertyp
      Streckenlager
2.
      Versandadresse des Ladescheins
2.
      Adresse des VK Lagers
2.
      Versandadresse des Ladescheins
3.
      Versandanschrift des VK Kontraktes
3.
      Versandanschrift des VK Kontraktes
4.
      Adresse des VK Kontraktes
4.
      Adresse des Kunden aus dem VK Ladeschein
5.
      Adresse des VK Kontraktes
Adressfolge Ladeadresse :
1.
abweichende Herkunfts-Adresse
2.
Adresse des EK Lagers, wenn man den Transportauftrag für den VK Ladeschein
drucken will und auch ein EK Ladeschein existiert. (EK Lagertyp ungleich
Streckenlager)
Lagertyp Streckenlager:
n
Versandanschrift des EK Kontraktes
n
Adresse des Kunden aus dem EK
Ladeschein
n
Adresse des EK Kontraktes
3. Versandanschrift des EK Kontraktes
4. Adresse des EK Kontraktes
5. Adresse des Lagers
1. abweichende Herkunfts-Adresse
Es gibt einen EK-Ladeschein zum
      V
[...]


---

## Streckenerfassung Report Verladeinfo

Streckenerfassung Report Verladeinfo
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Verladeinfo
Verladeauftrag
Anrede
Sehr
      geehrte Damen und Herren,
an
an:
Text_Verladeinfo
hiermit stellen wir wie folgt frei
      und bitten um Auslieferung:
Abholer
Abholer
Info_Abholer
Der
      Abholer wird sich zwecks Terminabsprache mit Ihnen in Verbindung
      setzen.
Warensorte
Warensorte
Schiff
Schiff
Menge
Menge ca.
Kontrakt
Kontrakt
Absprache
(in
      Absprache mit allen Beteiligten)
Termin
Termin
Mfg
Mit
      freundlichen Grüßen
BL_Datum
B/L
      Datum
Bemerkungen
Bemerkungen (wird ausgeblendet, wenn
      in den Streckentexten nichts eingegeben wurde)
Bitte_unbedingt
Bitte unbedingt den beigefügten
      Lieferschein bei jeder Lieferung verwenden!
(wird nur angezeigt, wenn
      es in den Streckentexten angehakt wurde)
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Standort
Standort, den

---

## Streckenerfassung Report Warenbegleitschein

Streckenerfassung Report Warenbegleitschein
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Warenbegleitschein
An-/Auslieferungsbegleitschein
      (Warenbegleitpapier)
Zertifizierung
Zertifizierung
ISCC
ISCC
Ladestelle
Ladestelle
Lieferadresse
Lieferadresse
nachhaltig
Zertifizierung
      (Nachhaltigkeit)
System
System:
Nummer
Nummer
Kontrakt
Kontrakt
Warensorte
Warensorte
istnachhaltig
(nachhaltig)
LKW
LKW-Nr.
Termin
Termin
Menge3
Menge (kg)
Lieferdatum
Lieferdatum
Zugmaschine
Zugmaschine
Haenger
Hänger/
Auflieger
Auflieger
THG
THG-Wert
ankreuzen
bitte ankreuzen oder angeben (ohne
      Transport)
Standard
Standard
Standardtext
(Standard - 688 kg CO2 eq/to
      Raps)
oder
oder
Einheit
kg
      CO2 eq/to Raps
Unterschrift
Unterschrift:
Datum
Datum:
Sitz1
Sitz1
Sitz2
Sitz2
Sitz3
Sitz3 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
Sitz4
Sitz4 (wird ausgeblendet, wenn das
      Druckfeld nicht gepflegt wird)
HR1
hr1
HR2
hr2
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR3
hr3
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
HR4
hr4
      (wird ausgeblendet, wenn das Druckfeld nicht gepflegt wird)
Zusätzlich zum Standardersetzungssystem im
Warenbegleitschein kann noch das Druckfeld TextStandardText sowie das Feld
TextStandardTextWG genutzt werden.
Von der reportspezifischen Zuordnungsmaske
können dann die Felder THG Text wie auch abweichendes
THG im Report genutzt werden.
Als Standardersetzungen werden hierbei die Platzhalter
<thg>, <tsw>, <anbauland> und <nutsnummer> ersetzt.
Es gilt die Regel, dass der Standardtext aus
TextStandardTextWG genommen wird, wenn kein Warenbegleitschein spezifischer Wert
in der Zusatzmaske angegeben ist, ansonsten der Text aus der Zusatzmaske
genommen wird.
Die Texte in der Zu
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

## Technische Hilfestellung

Tec
hnische Hilfestellung
Die Dokumentation zu den Business-Terms finden Sie
hier:
https://xeinkauf.de/dokumente/#xrechnung
.
Darin finden sich Business-Groups (BG), nach denen die Daten in der Datenbank in
Tabellen mit dem Präfix „XRE_“ abgelegt sind. Die Business-Terms (BT)
beschreiben einzelne Felder. Diese sind von 1-163 durchnummeriert.
Diese BT-Nummern finden sich auch in den
Standard-Prozeduren zur Ermittlung von Daten für den erechnungs-Export wieder.
Aus den Tabellen werden die Daten in das Format der Universial Business-Language
(UBL) übertragen und als XMl exportiert. Sollte ein Wert an einer bestimmten
Stelle erwartet werden, so kann diese im UBL identifiziert und mit Hilfe der
Spezifikation
für UBL
oder mit Hilfe der entsprechenden
Stylesheetdefinition
gefunden und einem Business-Term zugeordnet werden. Dann lässt sich die Herkunft
des Feldes in der Tabelle über die entsprechenden prozeduren bestimmen und der
Export durch Individualisierung der Exportprozeduren ergänzen.

---

## Teildisposition ändern/stornieren

Teildisposition
ändern/stornieren
Rückabwicklung für die
Standard-Teildisposition
und
Mehrfachteildisposition
.
Um Mengen aus Aufträgen, Lieferscheinen und
Bestellungen auszubuchen, die teildisponiert wurden, gibt es je nach Vorgang
unterschiedliche Korrekturmöglichkeiten.
Nach der Teildisposition hat man die
Möglichkeit, den übernommenen Artikel zu korrigieren, früher gab es als
Korrektur nur die Alternative, die Position komplett zu löschen und neu zu
erfassen.
So lassen sich bei diesen Positionen evtl.
Nebenbuchhaltungen wie Kontrakte, Partien und sonstige Infos nachtragen.
Hierbei gelten folgende
Grundsätze
:
Bei Rücklieferungen teildisponierter Mengen wird immer
auf der Ebene des jeweiligen Beleges
"ausgebucht"
(Bei "
Rückauftrag
erfassen"
z.B. ist die Ebene Auftrag)
Wird eine Restmenge
"ausgebucht"
,
so bleibt der Urbeleg erhalten und es wird ein neuer "Storno Beleg"
erstellt, da innerhalb der Urbelege die Positionszeilen, von denen
teildisponiert wurde, nicht mehr änderbar sind.
(Bsp.: Bei einem Auftrag wird
die Restmenge nicht mehr benötigt)
Soll bei einem Beleg z.B. bei einem bereits
teilumgewandelten Auftrag die Menge erhöht werden, so ist dies in der
Positionszeile aus der umgewandelt wurde nicht mehr möglich. Diese Änderung kann
durch Eingabe einer neuen Positionszeile im Auftrag erfolgen.
Mit den folgenden Funktionen lassen sich die
teilumgewandelten Vorgänge verändern bzw. ausbuchen bei den aus der
Teilumwandlung entstandenen Belegen z.B. Lieferscheinen mit den bekannten
Möglichkeiten wie Korrektur in der Positionszeile des Belegs, oder der
Stornierung des Beleges Änderungen vorzunehmen.
Rückauftrag erfassen
Mit der Funktion Rückauftrag erfassen kann auf der
Ebene des Auftrages entweder die Menge des Auftrages nach einer Teildisposition
geändert oder ganz ausgebucht werden.
Hierzu wird die Funktion
Rückauftrag erfassen
im Auswahlbildschirm
Aufträge bearbeiten aufgerufen.
Im Erfassungsbildschirm wird der Kunde gewählt und in
den
[...]


---

## Transportauftrag

Transportauftrag
Hierbei handelt es sich um eine spezielle Variante zur
Zusammenstellung von Aufträgen für die Zusammenarbeit mit Transportunternehmen.
Der konkrete Einsatz muss im Einzelfall abgestimmt werden.

---

## Tresenkasse

Tresenkasse
Hier stehen die Möglichkeiten des Bareinkaufs
[BVEE]
,
des Barverkaufs
[BVVE]
und der
Barverkaufsgutschrift
[BVG]
unter " Barvorgänge " zur
Verfügung.
Generell werden alle Funktionalitäten des Kreditverkaufs auch bei
Barvorgängen zur Verfügung gestellt. Von Bedeutung sind hier insbesondere die
Preisfindungsfunktionen.
Die Erfassung beginnt mit der Bestimmung des
Barverkaufskunden.
Dies ist ein Kunde/Lieferant des
Kunden-/Lieferantenstamms, es werden die für den Kunden/Lieferanten hinterlegten
Konditionen angewandt. (Dieser ist vorbelegt mit dem Eintrag in den
Kasseneinstellungen)
Für EK- bzw. VK können zwei verschieden
Standardkunden/-lieferanten eingestellt werden. Außerdem kann für den
Tresenverkauf und den Abverkauf an der POS-Kasse ebenfalls verschiedene
Standardkunden hinterlegt werden.
Für den anonymen Barverkauf wird jedem Barverkauf bzw.
Einkauf oder Gutschrift automatisch ein Standardkunde vorbelegt, der aus der
entsprechenden Eintragung in den Kasseneinstellungen stammt, hier ist auch die
Änderung des vorbelegten Kunden möglich. Die Konditionen dieses Standardkunden
müssen im Kundenstamm hinterlegt sein. Diese Nummernvorbelegung ist nachträglich
änderbar, solange noch keine Artikel erfasst wurden.
In Abhängigkeit von der Struktur des Barverkaufs
werden zwei unterschiedliche Positionserfassungsmasken zur Verfügung gestellt.
Unternehmen, die bei Barvorgängen auf Nebenbuchhaltungen wie Kontrakte, Partien,
Baustellen zugreifen müssen, werden die bekannte Erfassungsmaske des
Kreditverkaufs einsetzen.
Von der Kopfinformation wird auf sie mit
F5
,
F4
verzweigt.
Die Artikel werden über Artikelnummer / EAN - Nummer
per Hand oder mit Hilfe eines Scanners eingelesen.
Bei der Artikelerfassung ist es möglich, mit
F3
die
Artikelmaske aufzurufen. Unten links werden die zugelassenen Suchkriterien
angezeigt. Das Hauptkriterium kann nun dadurch festgelegt werden, dass zuerst
das Kriterium bestimmt wird und danach aus der Box unten links
[...]


---

## Uhrzeit auf dem Bon ausdrucken

Uhrzeit auf dem Bon ausdrucken
Durch folgendes SQLK besteht die Möglichkeit, sich die
Uhrzeit auf dem Bon ausdrucken zu lassen:
select SUBSTR(BelegDatum, 10)
Uhrzeit
from AcashBelg
where
BelegId=:V_Id
Dieses ist ein privates SQLK mit Namen XYZ. Im
entsprechenden Barverkaufsformular ist dann an entsprechender Position die
Druckposition 7 SQL Zugriff auf Daten einzutragen mit Festtext XYZ, Uhrzeit.
Dieses zieht zurzeit allerdings nur bei der Tresenkasse.

---

## Typ

Typ
Auf diesem Feld hat man eine F3 Auswahl für die Art
der Belege z.B. Lieferscheinblöcke. Die F3 Auswahl greift auf ein Anwenderformat
(
af_typ
) zurück, was von jeder Firma
selbst gepflegt werden kann.

---

## Unterklassen

Unterklassen
In den folgenden Vorgangsklassen können
Kasseneinrichtungen vorgenommen werden:
Vorgangsklassen
Klasse
Beschreibung
700
Verkaufsrechnung
790
Verkaufsstornierung
800
Verkaufsgutschrift
1700
Einkaufsrechnung
1790
Einkaufsstornierung
1800
Einkaufsgutschrift
Definition der Unterklasse
Die Standard-Unterklasse ist 9900. Es können jedoch
seit Version 8 auch andere Unterklassen für Kasse genutzt werden. Diese werden
in der
Formularzuordnung[FRZ] auf der
Registerkarte Allgemein
im Feld „Kassen-Vorgang“ als Kassen-Unterklassen
definiert.
Zuordnung Nummernkreise und Zählkreise
In den Unterklassen der Klassen 700,1700, 800 und 1800
müssen Nummernkreise und Zählkreise zugeordnet sein
Dabei ist insbesondere darauf zu achten, dass für jede
Bedienerklasse, die Kassenvorgänge durchführen soll, eigene Einträge gemacht
werden müssen (
[FRZ]
bzw.
[NKF]
)
Formulare
In der
Formularzuordnung
müssen für Barverkauf /
Bareinkauf / Barverkauf Gutschrift die Zuordnungen der Formulare für Druck /
Vorschau / Bildschirm gemacht werden.
Ebenso wird festgelegt, ob es sich um Brutto /
Nettoerfassung handelt und welche Preisliste herangezogen werden soll.
Wenn bei der Preisliste 0 eingetragen ist, werden
Preislisten gemäß Kunde / Artikel gezogen.
Als Kasse für Barverkauf zieht das für diesen
Arbeitsplatz hinterlegte Konto in der Kassenverwaltung.
Storno-Formulare
Um die Belege stornieren zu können, sind die
entsprechenden Storno Formulare zuzuordnen.
Diese sind: VK (790,9900), Gutschrift (880,9900),
EK(1790,9900).

---

## Verbuchung im Warenwirtschaftssystem

Verbuchung im Warenwirtschaftssystem
In Abhängigkeit von der Vorgangsklasse erfolgen die
Verbuchungen im Warenwirtschaftssystem:
Warenverkauf
Angebot
keine Buchung
Auftrag
disponierte Menge,
      Dispositionsbestand, Auftragsbestand
Lieferschein
IstBestand, gelieferte Menge bei
      Übernahme aus Auftrag,
Auftragsbestand, disponierte
      Menge
Rechnung
IstBestand, gelieferte Menge,
      fakturierte Menge, Umsatz,
Rohertrag, bei Übernahme aus
      Lieferschein keine IstBestandsbuchung
Gutschrift
IstBestand, gelieferte Menge,
      fakturierte Menge, Umsatz, Rohertrag
Sonstige
Bei
      der Abbuchung aus Vorgängen, Kontrakten, Partien und anderen
Nebenbuchhaltungen erfolgen auch
      dort entsprechende Buchungen
Wareneinkauf
Bestellanfrage
keine Buchung
Bestellung
disponierte Menge,
      Dispositionsbestand, Bestellbestand
E-Lieferschein
IstBestand, eingegangene Menge bei
      Übernahme aus Bestellung,
Bestellbestand, disponierte
      Menge
E-Rechnung
IstBestand, eingegangene Menge,
      fakturierte Menge, Einkaufsumsatz, Bewertungspreis, bei Übernahme aus
      Lieferschein keine IstBestandsbuchung
E-Gutschrift
IstBestand, gelieferte Menge,
      fakturierte Menge, Einkaufsumsatz, Rohertrag
Sonstige
Bei
      der Abbuchung aus Vorgängen, Kontrakten, Partien und anderen
      Nebenbuchhaltungen erfolgen auch dort entsprechende Buchungen
Interne Buchungen
Je nach Typ mengen- und wertmäßige Buchungen. Hierbei
handelt es sich um Warenumbuchungen, Stücklistenauflösungen etc.
Zeitpunkt der Aktualisierung
Die Buchungen werden zentral vom Mandantenserver
durchgeführt. Vom Arbeitsplatz werden diesem Server abgeschlossene Vorgänge,
z.B. fertig gestellte Rechnungen, übermittelt. Mit der weiteren Verbuchung hat
der Arbeitsplatz also nichts zu tun. In sehr zeitkritischen Umgebungen, so z.B.
beim Telefonverkauf, wo die verfügbaren Mengen immer aktuell sein müssen, können
aus folgenden Gründen Verzögerungen bei der Bestandsaktualisierung
auftreten
[...]


---

## Vererbungsvorbelegung

Vererbungsvorbelegung
Es kann ein Angebotsliste als Vorlage gepflegt werden
(Preise und Sortierung), auf die im individuellen Listenfall Bezug genommen
werden soll, und zwar für die Preisvorbelegungen. An dieser Stelle kann
angegeben werden, welcher Preis von welcher Liste vererbt werden soll. Mit
dieser Möglichkeit kann die Preispflege vereinfacht werden.

---

## Vokabeln

Vokabeln
Gesamtbarverkaufsystem:
Alle Kassen die angeschlossen sind
"Kasse 0"
Kassensystem:
Hardware-Arbeitsplatz
gemäß
      Kassensystemverwaltung
Kasse
logischer Arbeitsplatz
gemäß Kassenverwaltung
Kassenkonto:
Anwendung für Kostenkonten bei
      Verteilung je nach Zahlungsart Kassenkonto in der Kassenverwaltung, auf
      das gebucht wird
Finanzvorgang
Folgende Belegarten werden
      Finanzvorgänge genannt:
10
      Zahlungsmeldung
11
      Einzahlung
12   Geldübernahme von
      einer anderen Kasse
14   Geldentnahme mit
      Zuordnung Sachkonto
15
      Auszahlung
16   Geldübergabe an eine
      andere Kasse
17   Abschöpfung /
      Einreichung
18
      Sortenwechsel
20
      Kassensturz
Barvorgang
Folgende Belegarten werden
      Barvorgang genannt:
2
      Barverkauf
4    Barverkauf
      Gutschrift
6
      Bareinkauf
23  Storno
      Barverkauf
24  Storno
      Barverkauf-Gutschrift
25  Storno
      Bareinkauf

---

## Vorfakturierung

Vorfakturierung
Prinzip: Erst die Rechnung, dann die Lieferung(en),
sowohl im Einkauf wie auch im Verkauf möglich.
Vorfakturierte Positionen
können in Referenz-ERP in der Eingangs- bzw, Ausgangsrechnungserfassung erzeugt
werden. Auch vorfakturierte Positionen, die für die Abwicklung mittels des
Rohwarenbearbeitungsmoduls vorgesehen sind, erfolgen mit dieser Methode.

---

## Vorfakturierungskennzeichen (WaBewVorFakKennz)

Vorfakturierungskennzeichen
(WaBewVorFakKennz)
Das Vorfakturierungskennzeichen findet sich in der
Tabelle Warenbewegung als Feld WaBewVorFakKennz.
Vor Einführung von Einlagerung gab es neben Einkauf
und Verkauf bereits Voreinkauf und VorVerkauf mit ihren zugehörigen
Anlieferungen bzw. Abholungen.
Die Buchungen des Vorverkaufs und Voreinkaufs waren
keinen physikalischen Bewegungen zugeordnet und wurden mit dem Flag VorFakKennz
= 1 gekennzeichnet.
Die Einlagerung, wird fortan mit VorFakKennz = 3 und
die Kommission mit VorFalKennz = 4 gekennzeichnet.

---

## Vorgang als Tabelle bearbeiten

Vorgang als Tabelle bearbeiten
Hauptmenü
Warenverkauf
Übergreifend
Marktstandangebote
Direktsprung
[MSA]
Direktsprung
[MAG]
Mit dieser Funktion kann ein Vorgang “tabellenartig”
bearbeitet, erfasst und/oder umgewandelt werden. Im ersten Schritt ist diese
tabellenorientierte Erfassung für die Verarbeitung von Belegen auf Tablett PCs
oder auf Pocket PCs vorgesehen gewesen, im weiteren aber für die allgemeine
Verarbeitung weiterentwickelt worden.
Es existieren zwei verschiedenartige
Vorgehensweisen
-
Aufruf als eigenständige Anwendung
-
Aufruf innerhalb
eines Vorganges
Zunächst wird der Bereich eigenständige Anwendung
beschrieben.

---

## Vorgangsdefinition prüfen [FRZ]

Vorgangsdefinition prüfen
[FRZ]
Hauptmenü
Administration
Formulare/Abläufe
Formularzuordnung/Vorgangsunterklassen
Direktsprung
[FRZ]
Es
muss für die gewünschten Belegarten (1600,1690, 1700,1790 im Einkauf und 600,
690, 700, 790 im Verkauf) eine Unterklasse 9999 eingerichtet sein. Es ist darauf
zu achten, dass in den Formularzuordnungen der Unterklasse für Druck-, Vorschau-
und Bildschirmformular jeweils gültige Formulare zugewiesen sind, auch wenn
diese gegebenenfalls durch anderslautende Formularzuordnungen in
Rohwareparametern
[RWPA]
, Vorgangsdruckklassen
[VRGD]
nicht
zum Tragen kommen.

---

## Vorgangsbearbeitung allgemein

Vorgangsbearbeitung allgemein
Unter Vorgangsbearbeitung werden sämtliche
Buchungsvorgänge innerhalb der Warenwirtschaft verstanden, also Buchungsvorfälle
des Warenausgangs, -eingangs und interne Bewegungen incl. Storno:
Warenausgang
Wareneingang
Angebot
Bestellanfrage
Auftrag
Bestellung
Lieferschein
Eingangslieferschein
Rechnung
Eingangsrechnung
Gutschrift
Eingangsgutschrift
Umlagerungen
Umlagerungen
etc.
etc.
Darüber hinaus ist es möglich, eigene
Vorgangsunterklassen zu definieren und in den Datenfluss des Referenz-ERP – Systems zu
integrieren. Vorgangsunterklassen sind z.B. optische Varianten (Rechnung in
englischer Sprache, Lieferschein als Alternative mit Preisen,
Lagerentnahmeschein, Barverkauf etc.). Die Abarbeitung der Vorgänge erfolgt
automatisch laut der organisatorischen Vorgabe des Unternehmens.
Sämtliche Vorgänge sind miteinander verkoppelt.
Erfassungen erfolgen nur einmal, nachfolgende Vorgangsarten werden automatisch
erzeugt. Selbstverständlich können notwendige Korrekturen, falls zulässig, im
Vorfeld oder im Nachhinein vorgenommen werden.

---

## Vorgangserzeugung per VBScript

Vorgangserzeugung per VBScript
Zur automatisierten Erzeugung von Vorgängen per
VBScript werden die folgenden Dateien
benötigt:
•
bestellung.vbs
•
bestellung_include.vbs
•
bestellung_start.vbs
•
autom_bestellung.xml
•
auftrag.xml
Die Namen sowie der Speicherort sind nicht zu
verändern.

---

## Vorgangsklasse

Vorgangsklasse
Die Vorgangsklasse wird anhand der in den Parametern
BELARTKZ_xxx hinterlegten Kennungen ermittelt. Kann die Vorgangsklasse nicht
ermittelt werden, zieht die BELART_DEFAULT abgelegte Vorgangsklasse. Ist auch
diese nicht auswertbar, wird Lieferschein (v_klassnummer = 600) angenommen.
Wurde ein Wert aus den Importdaten gelesen, der jedoch keiner Vorgangsklasse
zugeordnet werden kann, oder handelt es sich um einen Rohwarenbeleg , wird die
Vorgangsklasse auf 0 gesetzt. Belege, die unberechtigt mit der Vorgangsklasse 0
belegt werden, können später nicht in Vorgänge umgewandelt werden!
Lager- bzw. Lagerplatzumbuchungen werden automatisch
unterschieden.
(Zugehörige Positionsparameter: BELART_SAx, weitere
Parameter: BELARTKZ_xxx, BELART_DEFAULT)

---

## Vorgangsstapel / Stapel verwalten

Vorgangsstapel
/ Stapel verwalten
Hauptmenü
Warenverkauf
Übergreifend
Vorgangstapel
oder Direktsprung
[VRS]
Der Vorgangsstapel wir über die Stapelmechanik der
Auswahlliste 2.0 verwaltet. Mit dem Direktsprung [VRS] gelangt man in die
Anwendung „Vorgangsstapel“. Dort existieren zwei Varianten;
1.
Vorgansstapel
. Alle Stapel inclusive der Vorgänge, die zu diesem Stapel
gehören, und zwar alle eigenen Stapel und alle Stapel, die nicht
privat
sind.
In dieser Variante
ist man automatisch im Stapelmodus und bearbeitet immer den Stapel zur Gruppe.
Die Funktionen
Hinzufügen zu einem Stapel
und
Umschalten
Stapelverarbeitung
werden hier nicht angeboten.
2.
Stapel -Liste
. Eine Liste aller vorhandene Staple. Dort finden sich auch
die allgemeinen Stapel. Hier besteht die Möglichkeit ausgewählte Stapel komplett
zu löschen.

---

## Vorgänge, die Waren bewegen

Vorgänge, die Waren bewegen
Einkauf /
      Verkauf
Einkauf
Beim
      klassischen Einkauf wird die Ware bei Bezahlung oder gegen Quittung
      übergeben. Die Ware wird sofort dem Bestand
Eigenware
hinzugefügt.
Verkauf
Beim
      klassischen Verkauf wird die Ware bei Bezahlung übergeben. Die Rechnung
      wird ebenso zu diesem Zeitpunkt erstellt. Unabhängig von der Art der
      Bezahlung gilt hier immer:
Die
      Ware wird sofort aus dem Bestand
Eigenware
ausgebucht.
Voreinkauf
Voreinkauf
Ein
      Voreinkauf wird getätigt, wenn z.B. der Preis günstig ist, die Anlieferung
      jedoch aus Kapazitäts-, logistischen oder anderen Gründen erst später
      erfolgt. Bei einem Voreinkauf wird Ware eigenes Eigentum. Es liegt jedoch
      bis zur Anlieferung auf dem
Fremdlager
.
Voreinkauf
      Anlieferung
Bei
      der Anlieferung des Vorverkaufs wird die bereits bezahlte Ware vom fremden
      Lager zum eigenen Lager transportiert. Die Ware wird also vom
Fremdlager
zur
Eigenware
transferiert.
Voreinkauf
      Rückabwicklung
Vorverkauf
Vorverkauf
Bei
      einem Vorverkauf bezahlt der Kunde seine Ware sofort, holt diese jedoch
      erst zu einem späteren Zeitpunkt ab (Gegenstück zu Voreinkauf). Die Ware
      ist bereits Eigentum des Dritten, liegt jedoch im
eigenen Lager
und wird
      als
Fremdware
deklariert.
Vorverkauf Abholung
Der
      Kunde holt seine bereits bezahlte Ware ab. Diese wird also aus dem
Fremdware
-Bestand
      ausgebucht.
Vorverkauf
      Rückabwicklung
Einlagerung
Einlagerung
Bei
      der Einlagerung wird die Ware eines Dritten in das
eigene Lager
eingelagert. Die Ware wird als
Fremdware
deklariert.
Einlagerung Abholung
Wird
      die Ware, die ein Dritter im Lager eingelagert hatte wieder abgeholt, so
      wird diese aus dem
Fremdware
bestand
      ausgebucht.
Einlagerung
      Vereinnahmung
Im
      Bereich Rohware kommt es zuweilen vor, dass eingelagerte Ware zu einem
      späteren Zeitpunkt aufgekauft wird. D
[...]


---

## Warteschleife und Historie

Warteschleife und Historie
Warenverkauf
Übergreifend
Mailversand [MAIL]
Alle Belege, ob sofort oder später zu versenden gleich
welcher Quelle kommen durch eine gemeinsame Schnittstelle. Dies ist die Prozedur
„SMTP_ARCHIVMAIL_FUNC“. Diese schreibt die Daten in Tabellen, die wiederum mit
der Auswahlliste unter dem Direktsprung [MAIL] angezeigt werden.

---

## Weiterverarbeitung der eingelesenen Daten

Weiterverarbeitung der eingelesenen Daten
Es folgen einige Schritte zur Validierung der
Daten.
Schlägt die Validierung des Lieferscheindatums (bei
der nur die kalendarische Gültigkeit und Lesbarkeit des Datums geprüft wird)
fehl, wird der Datensatz mit folgender Meldung im Fehlerprotokoll abgewiesen:
„LiefDat ungült. [...], Datei [...], Übern, #..., Zl. #...“
Ansonsten wird auch das Geschäftsjahr dahingehend
überprüft, ob es sich im Geschäftsjahrstamm befindet. Ein Fehler bewirkt
folgenden Eintrag ins Fehlerprotokoll: „Geschäftsjahr falsch [...], Datei [...],
Übern. #..., Zl. #...“ und die Abweisung des Datensatzes.
Anschließend wird die Menge auf 0 getestet. Trifft
dies zu, wird folgender Satz ins Fehlerprotokoll geschrieben: „Menge 0 [...],
Datei [...], Übern. #..., Zl. #...“ und der Datensatz abgewiesen.
Hat bis hierhin alles geklappt werden bei
Zielansprache ungleich UMLAGERUNG die Zugangslagernummer und der
Zugangslagerplatz auf 0 gesetzt.
Nun wird eine eindeutige SatzId vergeben.
Bei Zielansprache <> CEREA wird ein Datensatz in
die Relation VorgangUebergabe eingefügt (Status: SKRIPT_LAEUFT (0)).
Bei Zielansprache = CEREA werden zusätzlich die
Qualitäten eingelesen und in die Relation RohwareZusatzQualitaet_Waage
eingefügt.
Ist in einem der Parameter QUALxx der Wert1 oder Wert2
=0 oder der Parameter inaktiv geschaltet, so wird die entsprechende Qualität
nicht ausgewertet. In Wert3 steht die laufende Nummer der Qualität. Es darf
keine 2 aktiven QUALxx-Parameter geben, bei denen die Wert3-Inhalte
übereinstimmen! Sonst erfolgt folgende Fehlermeldung: DB-Error #...:
PutQualitaeten, [...], Übern. #..., SatzId #..., Zl. #...
(Positionsparameter QUAL01 ... QUAL15)
Dann wird ein Datensatz in die Relation
RohwareHauptsatz_Waage eingefügt (Status: SKRIPT_LAEUFT (0)).
Schleifenende – zurück zum Schleifenanfang – weiter
mit dem nächsten Datensatz
Hat bis hierhin alles geklappt, wird der Status
umgesetzt. Dies ist abhängig vom Parameter UEB_NUR_KOMLETT
[...]


---

## Zweiter Schritt: Halbautomatische Zuordnung

Zweiter Schritt: Halbautomatische Zuordnung
Gibt es nur eine mehrdeutige Zuordnung, so müssen die
Mehrdeutigkeiten bei der ersten Kassenabstimmung aufgelöst werden.
Wenn Sie ersten Mal die Funktion Kassenabstimmung im
Barverkaufsmenü aufrufen, präsentiert sich der Bildschirm mit folgender
Meldung.
Als einzige Funktion wird Ihnen „Mehrdeutige
Zuordnungen bereinigen“ angeboten.
Dieser Vorgang muss nicht notwendig in einem Stück
abgehandelt werden. Sie können jederzeit unterbrechen. Beim nächsten Aufruf der
Abstimmung fahren Sie fort.
Ihnen werden nun nacheinander je ein Kassenbeleg und
die jeweiligen Kandidaten von Fibu-Belegen vorgelegt, die zu diesem Kassenbeleg
passen könnten. In aller Regel haben Sie nicht allzu viele Belege zur Auswahl,
denn je nach Belegart müssen mindestens Datum, Betrag und Kassenkonto passen.
In der Maske erkennen Sie nun die angebotenen
Alternativen. Anhand der Angaben können Sie nun (etwa über eine zweite
Verbindung) genauere Nachforschungen in der Kasse oder in der Fibu anstellen,
welcher der beiden Fibu-Belege der richtige ist. In der Funktionswahl sehen Sie
nun 2 neue Funktionen, nämlich zur Durchführung der Zuordnung des gewünschten
Belegs und zum Weiterblättern auf den nächsten Problemfall.
Die Zuordnungsauswahl erfolgt über eine Itembox:
Wir haben zur Zuordnung gezielt die Itembox als Medium
gewählt, weil Sie dort nötigenfalls auf dem Weg einer privaten Ableitung
zusätzliche Information einbinden können, die ggf. für eine Entscheidung
nützlich ist.
Im vorliegenden Beispiel wird einem die Entscheidung
über den Buchungstext leicht gemacht.
Danach wird auf den nächsten Problemfall weiter
geblättert.

---

