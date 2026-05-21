# Finanzbuchhaltung & Rechnungswesen — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (390 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Massebilanzeinrichtung

Massebilanzeinrichtung
Beim Zuordnen einer Bewegung zu einer Massebilanz
([NABEW], Variante Bewegungsübersicht) wird der betreffende Artikel mit Lager-
und Nutsnummer in die Massebilanz eingetragen, sofern dieser dort noch nicht
vorhanden ist. Dies ist als Ereignis im Fehlerprotokoll [FEHLP] nachzulesen. Der
Eintrag der Artikel inkl. der Summe der Zu- und Abgänge der zugeordneten
Bewegungen ist ersichtlich in der Massebilanz ([NABEW], Variante Massebilanz).
Auf der Kundenmaske werden die Nachhaltigkeitseinrichtungen zu den Zertifikaten
korrekt ausgewertet bezüglich der Kombination Artikelnummer + Nuts-Nummer.
Releasenote Kategorie:
Ticket: 711866[32613]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Nachhaltigkeit
Variante: Massebilanz
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 32613, 711866

---

## SEPA Lastschrifteinzug und Skonto

SEPA Lastschrifteinzug und Skonto
Im automatischen Zahlungsverkehr wurden beim
SEPA-Bankeinzug die Bankarbeitstage nicht korrekt berücksichtigt, wenn Skonto
gewährt wurde. Beim automatischen Erstellen der Zahlungsvorschläge wird nun
der nächste Stichtag mit dem nächsten Bankarbeitstag vor belegt.
Releasenote Kategorie:
Ticket: 714375[32842]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: ZHVE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32842, 714375

---

## Jahreswechsel bei Wechsel der Forderungsgruppe im Kundenstamm

Jahreswechsel bei Wechsel der Forderungsgruppe im Kundenstamm
Beim Jahreswechsel wurden bei Forderungs- und
Verbindlichkeitskonten immer die Jahresverkehrszahlen vorgetragen und daraus der
Saldo gebildet.  Dies führte zu unübersichtlichen Zahlen. Jetzt wird der
Saldo übertragen.   Wird im Kunden-/Lieferantenstamm die Forderungsgruppe
geändert, erfolgt beim Jahreswechsel eine Umbuchung der betroffenen Forderungs-
und Verbindlichkeitskonten. Diese Umbuchung wird jetzt immer vor dem
Jahreswechsel für Personenkonten durchgeführt (vorher beim Jahreswechsel
Bilanzkonten).
Releasenote Kategorie:
Ticket: 712049[32898]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: -
Variante: -
Funktion/Report: JAHRW
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32898, 712049

---

## Datenübernahme: FiBu-XML-Import

Datenübernahme: FiBu-XML-Import
Der Datenübernahme [DUEB] wurde die Option
"Fehlerhafte Daten überschreiben?" hinzugefügt. Hierüber kann eingestellt
werden, ob der Import von fehlerhaften Daten wiederholt werden darf. Diese
Option ist nur für den FiBu-XML-Import verfügbar.
Releasenote Kategorie:
Ticket: 715354[32965]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: Datenübernahme [DUEB]
Variante: Datenübernahme
Funktion/Report: Starten
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32965, 715354

---

## DUEB: FiBu-XML-Import

DUEB: FiBu-XML-Import
Beim FiBu-XML-Import über [DUEB] werden jetzt
UNC-Pfade (\\Servername\..) korrekt ausgewertet.
Releasenote Kategorie:
Ticket: 0[33032]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: [DUEB] Datenübernahme
Variante: Datenübernahme
Funktion/Report: Starten...
Weitere Informationen
Tags:
Releasenote, 8.3.2211.9, 33032, 0

---

## Geschäftsjahr/Fibuperioden

Geschäftsjahr/Fibuperioden
Bei der Neuanlage eines Geschäftsjahres [JAHR], in dem
mehr als 12 Normalperioden verwendet werden, wird der Datumsbereich für die
zusätzlichen Perioden mit dem Jahresenddatum und der Text mit "man.Abschluss"
vorbelegt.
Releasenote Kategorie:
Ticket: 717508[33291]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: JAHR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33291, 717508

---

## Lagerumbuchung: Tastensteuerung

Lagerumbuchung: Tastensteuerung
In der Lagerumbuchung konnten die Felder für den
Abgang nicht mit der Tastatur angesteuert werden. Die Tab-Reihenfolge wurde
angepasst, sodass dies nun möglich ist.
Releasenote Kategorie:
Ticket: 718700[33382]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Lagerumbuchung
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33382, 718700

---

## Periode ändern mit Tagesdatum

Periode ändern mit Tagesdatum
In der Anwendung Fibu-Übertrag [FIB], bei der Funktion
"Periode ändern", wurde die Itembox auf dem Feld "Periode" um eine weitere
Such-Variante "Offene Perioden vom Tagesdatum" erweitert.
Releasenote Kategorie:
Ticket: 719519[33394]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [FIB]
Variante: Fibu Übertrag Standard
Funktion/Report: Periode ändern
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33394, 719519

---

## Belegfluss

Belegfluss
Für die Belegart SO-Belege kann jetzt als Gegenkonto
auch ein Personenkonto angegeben werden. Dabei ist zu beachten, dass sobald ein
Personenkonto als Gegenkonto eingetragen wird, die Erfassung eines FiBu-Beleges
nur noch über die Funktion "Direkt-Finanzbelegerfassung" erfolgen kann.  Da
eine direkte Buchung von Personenkonto an Personenkonto nicht zulässig ist, ist
in der Prozedur für die "Direkt-Finanzbelegerfassung" ein Sachkonto anzugeben,
über das die Umbuchung erfolgen soll.
Releasenote Kategorie:
Ticket: 720082[33399]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Belegfluss
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33399, 720082

---

## Belegfluss

Belegfluss
Die Zuordnung eines Beleges zum Belegfluss verlief
bisher über die Belegreferenz. Jetzt wird der Beleg direkt (über die V_Id bzw.
FibuV_Id) mit dem Belegfluss verknüpft.  Für bereits angelegte
Belegfluss-Datensätze erfolgt die Zuordnung weiterhin über die Belegreferenz.
Für diese Datensätze kann mithilfe der Funktion "Belegzuordnung entfernen", die
Zuordnung rückgängig gemacht werden. Diese Funktion ist nur verfügbar, wenn im
Postfach das Feld "Beleg-Freigabe erlaubt?" auf "Ja" steht. Das Ausführen dieser
Funktion sowie das Anlegen eines Beleges im Belegfluss werden jetzt
protokolliert und unter dem Register "Historie" im Belegfluss angezeigt.
Releasenote Kategorie:
Ticket: 720082[33454]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Archiv Belegfluss
Variante: Meine Postfächer
Funktion/Report: [BF]
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33454, 720082

---

## Finanzbuchhaltung: Jahreswechsel

Finanzbuchhaltung: Jahreswechsel
Es wurde der Steuerparameter 1143 "Jahreswechsel:
Abschluss und Eröffnung immer gemeinsam löschen/buchen" eingeführt.  Dieser
steht standardmäßig auf "Ja", und sorgt für eine Verhaltensänderung beim
Löschen/Buchen von Finanzbuchhaltungsbelegen.  Sobald ein Jahreswechsel
gelöscht/gebucht wird, wird der dazugehörige Jahreswechselbeleg auch gelöscht
bzw. gebucht.  Bei der Einstellung "Nein" können die Jahreswechselbelege
wie bisher einzeln gelöscht oder gebucht werden.
Releasenote Kategorie:
Ticket: 720619[33538]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33538, 720619

---

## Infoblattdruck für Forderungskonten

Infoblattdruck für Forderungskonten
Das Infoblatt für Forderungs- und
Verbindlichkeitskonten wurde um die Umbuchungen, die bei Wechsel der
Forderungsgruppe erstellt werden, erweitert.
Releasenote Kategorie:
Ticket: 721386[33650]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33650, 721386

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

## FiBu Datenübernahmen im Excel XLSX-Format

FiBu Datenübernahmen im Excel XLSX-Format
Für die Datenübernahme [DUEB] wurde eine Möglichkeit
geschaffen Daten im Excel XLSX-Format (*.xslx) in die Finanzbuchhaltung zu
importieren.
Releasenote Kategorie:
Ticket: 726193[34139]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Datenübernahme [DUEB]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 34139, 726193

---

## Fibu Datenübernahme im Excel CSV-Format

Fibu Datenübernahme im Excel CSV-Format
Für die Datenübernahme [DUEB] wurde eine Möglichkeit
geschaffen Daten im Excel CSV-Format (*.csv) in die Finanzbuchhaltung zu
importieren.
Releasenote Kategorie:
Ticket: 0[34140]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Datenübernahme [DUEB]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 34140, 0

---

## Datenübernahme Ustid

Datenübernahme Ustid
Der FIBU-Import (Datenübernahme [DUEB]) wurde um die
UstId des Kunden und des Mandanten erweitert.
Releasenote Kategorie:
Ticket: 727102[34254]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Datenübernahme [DUEB]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34254, 727102

---

## OPVerwaltung Teilzahlung

OPVerwaltung Teilzahlung
Man kann in der OP-Verwaltung mehrere Rechnungen gegen
eine Zahlung ausziffern und dazu dann eine Teilzahlung bilden. Waren die
erstellten Teilzahlungen in Buchwährung, kam es fälschlicherweise zu
Kursdifferenzbuchungen. Diese Auszifferung wird vom Reorganisator als fehlerhaft
ausgewiesen.  Außerdem hatten die Teilzahlungsbelege das Belegdatum der
Zahlung und nicht das der Rechnung bekommen.  Die Probleme sind jetzt
behoben.
Releasenote Kategorie:
Ticket: 727960[34337]
Version: 8.3.2310.27
Datum: 27.10.2023
Anwendung: OPV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2310.27, 34337, 727960

---

## Auswahlliste Vermailung

Auswahlliste Vermailung
Unter [MAIL] wurde die Auswahlliste angepasst. In
allen Varianten gibt es nun die Spalte "Typ-Original", um bei einem erneuten
verschicken zu erkennen, von welchem Typ die Originalmail war.  Die
Varianten "Ware-Beleg" und "Fibu-Beleg" wurden so angepasst, dass nun auch die
Kopien der entsprechenden Typen angezeigt werden.
Releasenote Kategorie:
Ticket: 726932[34413]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: Vermailung [MAIL]
Variante: alle
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34413, 726932

---

## Massebilanzzuordnung/entfernung Anzahl betroffener Belege

Massebilanzzuordnung/entfernung Anzahl betroffener Belege
Die Anzahl der markierten Belege wird nun angegeben,
um sicherzustellen, dass man die korrekte Anzahl an Belegen mit der
Massebilanzänderung verändert.
Releasenote Kategorie:
Ticket: 0[34541]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Nachhaltigkeit Bewegungsübersicht
Variante: Bewegungsübersicht
Funktion/Report: Massebilanz ändern.
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.22, 34541, 0

---

## FiBu-Übertrag nicht notwendig

FiBu-Übertrag nicht notwendig
Belege, die nicht in die Fibu übertragen werden
müssen, z.B. weil sie mittels Storno-Beleg storniert wurden, erzeugten bisher
die Meldung "Der Beleg ist bereits an FiBu übertragen".  Das führte zu
Verwirrung. Deshalb wird nun die Meldung "Beleg muss nicht an die Fibu
übertragen werden" ausgegeben.
Releasenote Kategorie:
Ticket: 726369[34183]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Rechnungsbearbeitung [REB]
Variante: Standard
Funktion/Report: FiBu Übertrag
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34183, 726369

---

## Kundentypwechsel

Kundentypwechsel
Wird der Kundentyp gewechselt (z.B. von Debitor zu
Kontokorrent, so ist dafür erforderlich, dass die gleichen Zählkreise für diese
Kundentypen eingerichtet sind, oder noch keine Belege für den Kunden erfasst
worden sind.
Releasenote Kategorie:
Ticket: 737497[35628]
Version: 9.0.2501.5
Datum:
Anwendung: Kunden [KU]
Variante: Standard
Funktion/Report: Editieren
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35628, 737497

---

## Belegfluss

Belegfluss
Im Belegfluss wurde bei der direkten Erstellung des
Finanzbelegs statt des Valutadatums Falscherweise das Skontodatum verwendet.
Releasenote Kategorie:
Ticket: 737462[35635]
Version: 9.0.2402.2
Datum: 22.10.2024
Anwendung: [BF]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.2, 35635, 737462

---

## GuV mit Vorvorjahreswerten

GuV mit Vorvorjahreswerten
Es wurde ein neuer Report "G u V mit
Vorvorjahreswerten" erstellt. Dieser ist wie die G u V aufgebaut, nur dass er
zwei weitere Spalten für ein weiteres Vergleichsjahr hat.
Releasenote Kategorie:
Ticket: 737359[35636]
Version: 9.0.2501.5
Datum:
Anwendung: FIGVV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35636, 737359

---

## Vermailung von Mahnungen

Vermailung von Mahnungen
Die Variante "Mahnungen bearbeiten" wurde erweitert.
Es werden zusätzlich die Spalten "Mailempfänger", "Sendetatus", "OPSaldo" und
"Mahnsaldo ohne verrechnung" angezeigt.
Releasenote Kategorie:
Ticket: 738373[35665]
Version: 9.0.2501.5
Datum:
Anwendung: MHB
Variante: Mahnungen bearbeitenh
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35665, 738373

---

## Steuerung Kassenabschluss

Steuerung Kassenabschluss
Erfassungsreihenfolge bei Bedienung über die Tastatur
der Kassenabschluss-Zählmaske wurde korrigiert.
Releasenote Kategorie:
Ticket: 738680[35734]
Version: 9.0.2501.5
Datum:
Anwendung: Kassenabschluss
Variante: -
Funktion/Report: [GBV]
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35734, 738680

---

## Kundentypwechsel

Kundentypwechsel
Wird der Kundentyp gewechselt (z.B. von Debitor zu
Kontokorrent, so ist dafür erforderlich, dass die gleichen Zählkreise für diese
Kundentypen eingerichtet sind, oder noch keine Belege für den Kunden erfasst
worden sind.
Releasenote Kategorie:
Ticket: 737497[35814]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Kunden [KU]
Variante: Standard
Funktion/Report: Editieren
Weitere Informationen
Tags:
Releasenote, 9.0.2402.4, 35814, 737497

---

## Kundentypwechsel

Kundentypwechsel
Wird der Kundentyp gewechselt (z.B. von Debitor zu
Kontokorrent, so ist dafür erforderlich, dass die gleichen Zählkreise für diese
Kundentypen eingerichtet sind, oder noch keine Belege für den Kunden erfasst
worden sind.
Releasenote Kategorie:
Ticket: 737497[35813]
Version: 9.0.2501.5
Datum:
Anwendung: Kunden [KU]
Variante: Standard
Funktion/Report: Editieren
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35813, 737497

---

## Skonto Basisbetrag korrekt herangezogen

Skonto Basisbetrag korrekt herangezogen
Es wurde als Basisbetrag für Skonto der Bruttobetrag
anstelle des skontier fähigen Betrags hinterlegt.  Dies wurde
angepasst.
Releasenote Kategorie:
Ticket: 742134[36121]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: [XRE][REB][ERB][RWB][RWBV][GUB]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36121, 742134

---

## Inventurabschluss PIV ignorieren

Inventurabschluss PIV ignorieren
Beim Inventurende [IVE] kann die Prüfung auf
permanente Inventur unterdrückt werden.  Das ist allerdings nur sinnvoll,
wenn in dem Jahr tatsächlich keine Artikel der permanenten Inventur
unterlagen.
Releasenote Kategorie:
Ticket: 734378[36542]
Version: 9.0.2501.5
Datum:
Anwendung: Inventurende
Variante: Inventurende Abschlussarbeiten
Funktion/Report: Inventur abschließen
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36542, 734378

---

## CAMT053 Anfangs- bzw. Abschlusssaldo aus Sicht des Kunden

CAMT053 Anfangs- bzw. Abschlusssaldo aus Sicht des Kunden
Beim Einspielen der Daten im CAMT053 Format wurde der
Anfangs- bzw. Abschlusssaldo aus Sicht der Bank importiert. Dies kann man nun
unter Optionen einstellen. Standard ist jetzt "Saldo aus Sicht des Kunden"
Releasenote Kategorie:
Ticket: 744003[36711]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36711, 744003

---

## OP-Verwaltung

OP-Verwaltung
In der OP-Verwaltung [OPV] existiert ein Bereich, in
dem Kundeninformation angezeigt wurde. Wenn aus Versehen in der untersten Zeile
dieses Bereichs ein Doppelklick ausgeführt wurde, wurden alle Zeilen nach oben
verschoben. Das geschieht nun nicht mehr.
Releasenote Kategorie:
Ticket: 742742[36710]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: OPV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36710, 742742

---

## Fibudirektverbuchungprozedur für Belegfluss um eine Parameter erweitert

Fibudirektverbuchungprozedur für Belegfluss um eine Parameter erweitert
In der Anwendung "Archiv Belegfluss"
[BF]  in der Variante "Postfach-Einrichtung " auf der Maske
"Postfach-Einrichtung" gibt es das Feld "Direkt-Finanzbelegerfassung". Die
Standardprozedur BelegFluss_Direktbuchung wurde um den Parameter
"in_kompress" erweitert. Nun ist es möglich die Direkterfassung mit der Funktion
"Direkt-Finanzbelegerfassung komprimiert" zu gruppieren, also alle Positionen
als eine gebündelte Position in der Finanzbuchhaltung zu erfassen.
Releasenote Kategorie:
Ticket: 746982[37062]
Version: 9.0.2501.5
Datum:
Anwendung: Archiv-Belegfluss [BF]
Variante: Postfach-Einrichtung, Meine Postfächer
Funktion/Report: Direkt-Finanzbelegerfassung,
Direkt-Finanzbelegerfassung komprimiert
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 37062, 746982

---

## DSFinV-K Export

DSFinV-K Export
Beim Export der Kassendaten gemäß DSFinV-K kam es
bislang zu einem Fehler im Bereich Referenzen, wenn mehrere offene Posten in
einer einzigen Zahlung mit der Option „Zahlungsmeldung für Kreditrechnungen“
verarbeitet wurden. Dieses wurde nun korrigiert.  Der REF_TYP wird beim
Erzeugen der Daten berücksichtigt.  Es wird nur noch ein Eintrag pro
REF_TYP erzeugt unabhängig von der Anzahl der Offenen Posten in der
Zahlung.  Das REF_DATUM wird ausschließlich eingetragen, wenn der REF_TYP
auf Transaktion steht.
Releasenote Kategorie:
Ticket: 747791[37461]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: DSFinV-K Export
Variante: DSFinV-K Export
Funktion/Report: Export erzeugen
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37461, 747791

---

## Finanzbuchhaltung

Finanzbuchhaltung
In den Zahlungsarten kann für Zahlungsausgang
eingestellt werden, dass die Überweisung als Echtzeitüberweisungen ausgeführt
werden soll. Es werden dann alle Rechnungen, die vor dem nächsten Stichtag bzw.
deren Skonto vor dem nächsten Stichtag fällig ist und zwar ohne  Versatz
von einem Tag wie es bei der Standardüberweisung der Fall ist. Um dies zu
gewährleisten musste die Logik der Fälligkeitsbestimmung im automatischen
Zahlungsverkehr komplett überarbeitet werden.Weiterhin ist dabei zu beachten,
dass Standardüberweisungen und Echtzeitüberweisung beim DTA nicht gemischt
übertragen werden können. Daher wurde die Anwendung "Zahlungen bearbeiten
(Direktsprung [ZHB]) um ein Spalte "Echtzeitueberweisung" (Ja/Nein)
erweitert.
Releasenote Kategorie:
Ticket: 747665[37533]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: ZHVE,ZHVB,ZHB
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37533, 747665

---

## Ergänzung zur Paginiernummer

Ergänzung zur Paginiernummer
Zur Sicherstellung der Eindeutigkeit der automatisch
generierten Paginiernummer bei der Erfassung eines FiBu-Vorgangs wird diese nun
um die FibuV_ID ergänzt.
Releasenote Kategorie:
Ticket: 746311[37672]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Belege erfassen
Variante: Belege erfassen
Funktion/Report: Eingangsrechnung
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37672, 746311

---

## eRechnung: Skonto

eRechnung: Skonto
Die Skontodarstellung in der eRechnung wurde für die
Skontobeträge < 1€ richtig gestellt.
Releasenote Kategorie:
Ticket: 748101[37671]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: eRechnung
Variante: -
Funktion/Report: Erzeugen
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37671, 748101

---

## Belegfluss: Fibu-Belege

Belegfluss: Fibu-Belege
Im Belegfluss [BF] steht für das Erzeugen von
Finanzbuchhaltungsbelegen nur noch die Fibu-Direktverbuchung zur Verfügung.
Releasenote Kategorie:
Ticket: 748306[37651]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Belegfluss
Variante: meine Postfächer
Funktion/Report: Fibu-Beleg erzeugen
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37651, 748306

---

## XRE - Fibuerfassung - Kontonummer nun korrekt

XRE - Fibuerfassung - Kontonummer nun korrekt
Beim Einspielen der eRechnung unter [XRE] wird
die Kontonummer jetzt auch bei den Finanzbuchhaltungsbelegen ermittelt und
versorgt.
Releasenote Kategorie:
Ticket: 749761[38074]
Version: 9.0.2502.6
Datum:
Anwendung: eRechnung
Variante: Import-Vorgänge
Funktion/Report: Fibu-Erfassung
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.6, 38074, 749761

---

## Auszifferung mit Skonto aufteilen

Auszifferung mit Skonto aufteilen
Wurde in der Finanzbuchhaltung bei Buchung einer
Zahlung ein Beleg zur Auszifferung ausgewählt und Skonto automatisch aufgeteilt,
dann kam es bei Zeilen mit Betrag 0.00 zu einem Nullteilungsfehler. Dies ist
behoben.
Releasenote Kategorie:
Ticket: 750891[38403]
Version: 9.0.2502.7
Datum:
Anwendung: Fibu Belegerfassung [FIBE]
Variante: --
Funktion/Report: Zahlungsverkehr Kasse/Bank
Weitere Informationen
Tags:
Releasenote, 9.0.2502.7, 38403, 750891

---

## Aus [OPV] die Konteninformation [KOI] aufrufen

Aus [OPV] die Konteninformation [KOI] aufrufen
Beim Aufruf der Konteninformation aus der
OP-Verwaltung heraus wurde die Jahrnummer nicht korrekt übergeben. Dies ist
behoben.
Releasenote Kategorie:
Ticket: 751075[38462]
Version: 9.0.2502.7
Datum:
Anwendung: Offene Posten Verwaltung [OPV]
Variante: -
Funktion/Report: Konteninformation
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38462, 751075

---

## Periodische Buchungen Valutatdatum

Periodische Buchungen Valutatdatum
Bei Periodischen Buchungen wurde das Valutadatum
falscherweise auf das Belegdatum gesetzt. Dies wurde korrigiert.
Releasenote Kategorie:
Ticket: 753606[39717]
Version: 9.0.2502.9
Datum:
Anwendung: WZA
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39717, 753606

---

## Anlagenbuchhaltung:: Freigabe (EPA ANKAVORSCHFREIGABE)

Anlagenbuchhaltung:: Freigabe (EPA
ANKAVORSCHFREIGABE)
Bezeichnung
Standardwert
Erklärung
KEINEN Beleg für die Primanota
      erzeugen?
Nein
Will
      man keine automatischen AfA – Buchungen für die Primanota bei der Freigabe
      der Vorschläge erstellen, so muss dieser Schalter auf
Ja
gestellt
      werden.

---

## Belegerfassung (EPA FIBUERF)

Belegerfassung (EPA FIBUERF)
Bezeichnung
Standardwert
Erklärung
Belegmappe abfragen
Nicht aktiv
Es
      existieren drei Ausprägungen:
•
Nicht
      aktiv
. Belegmappe
      wird nicht abgefragt bzw. angezeigt
•
Belegmappe
      einmal zentral abfragen
. Die Belegmappe wird nur einmal im
      Periodenabfragefenster abgefragt.
•
Belegmappe in
      der Belegerfassung abfragen
. Man hat in der
      Belegerfassungsmaske zusätzlich die Möglichkeit die Belegmappe zu
      ändern.
•
Saldo nur aus den letzten zwei
      Geschäftsjahren ermitteln
Ja
Zur
      Performancesteigerung existiert die Möglichkeit, den Saldo eines Kontos
      nur aus den letzten zwei Jahren bestimmen. Dies setzt jedoch voraus, dass
      der Jahreswechsel ordentlich durchgeführt worden ist.
Bei
      Eingangsrechnungen Anlagenstamm automatisch aufrufen
Ja
Bei
      Erfassung von Eingangsrechnungen, die als Gegenkonto ein als Anlagekonto
      gekennzeichnetes Konto verwenden, kann direkt in die Anlagenbuchhaltung
      verzweigt werden. Dazu muss hier ein „Ja“ eingetragen werden
Bei
      Zahlungen automatisch F6 ?
Nein
Es
      ist möglich bei der Erfassung von Zahlungsbelegen direkt in die
      OP-Verwaltung zu springen um die Zahlung sofort zu
      verrechnen/auszuziffern. Dazu muss hier ein „Ja“ eingetragen
      werden.
Bei
      Zahlungsverkehr Bank (ZB) Verrechnungskonto aus Hausbank
      vorbelegen?
Ja
Folgende Einstellmöglichkeiten
      existieren:
•
Ja: Es wird das
      Verrechnungskonto verwendet
•
Nein: Es wird
      das Finanzbuchhaltungskonto verwendet
Belegdatum mit Periode
      prüfen?
Test
      und Warnung
Folgende Einstellmöglichkeiten
      existieren:
•
Kein
      Test
•
Test und
      Warnung
•
Test und Fehler
•
Teste Jahr mit
      Warnung
•
Teste Jahr und
      Fehler
Beim
      Test Jahr muss das Belegdatum nur im aktuellen Jahr liegen. Bei Warnung
      wird nur ein Hinweis auf das inkorrekte Datum gegeben und man kann weiter

[...]


---

## Buchung erfasster Belege (EPA FIBUCH)

Buchung erfasster Belege (EPA FIBUCH)
Bezeichnung
Standardwert
Erklärung
Buchen ohne
      Mandantenserver
Nein
Steht hier ein „Ja“, so werden die
      Belege direkt an diesem Arbeitsplatz gebucht, ohne dass der
      Mandantenserver gestartet sein muss.
Bediener darf nur eigene Belege
      buchen
Nein
Bei
      Ja kann man nur die Belege Buchen, die man selber erfasst hat. Die
      Auswahlmöglichkeit auf dem Bildschirm entfällt.

---

## Jahreswechselbuchungen (EPA FIJAHRW)

Jahreswechselbuchungen (EPA FIJAHRW)
Bezeichnung
Standardwert
Erklärung
Währungen führen?
Nein
Wir
      hier „Ja“ eingetragen, so wird zusätzlich die Tabelle
FiBuWaehrInfo
beim Jahreswechsel
      gefüllt. Dies ist nur dann notwendig, wenn man mit Fremdwährung
      arbeitet.

---

## Mahnungen buchen (EPA FIMAHND)

Mahnungen buchen (EPA FIMAHND)
Bezeichnung
Standardwert
Erklärung
Text
      Hauptzeile bei Übernahme der Mahnungen in die Primanota
Hier
      kann man einen Festen Text hinterlegen, der beim Erstellen des
      Fibu-Beleges als Text für die Hauptzeile verwendet wird.

---

## Mahnungen drucken (EPA FIMAHNDR)

Mahnungen drucken (EPA FIMAHNDR)
Bezeichnung
Standardwert
Erklärung
Darstellung des
      Sollhabenkennzeichens
SH
Hier
      stehen die Werte „
SH
“ für die Darstellung des Vorzeichens als Soll
      oder Haben oder „
Minusplus
“ für die Darstellung der negativen
      Salden als “-„. Bei positiven Salden entfällt dann das Vorzeichen.
Restposten auflösen?
Nein
Ein
      Restposten ist ein technischer Beleg, der dem Kunden so nicht bekannt ist.
      Er entspricht dem Saldo mehrerer Belege (kommt häufig bei Ratenzahlungen
      vor). Trägt man hier ein Ja ein, werden an Stelle des einen Restpostens
      alle hier verrechneten Belege aufgelistet.

---

## Periodische Buchungen (EPA FIWIEBU)

Periodische Buchungen (EPA FIWIEBU)
Bezeichnung
Standardwert
Erklärung
Alle
      Belege in diesem Zeitraum erzeugen?
Nein
Es
      kann vorkommen, dass es bis zum Abgrenzungsdatum mehrere Belege erzeugt
      werden müssten. Ein Beispiel ist, dass man als Intervall einen Monat
      gewählt hat und dann bereit im Januar all Belege fürs gesamte Jahr
      erstellen will. Im Standardfall müsste man dann 12 Mal die Funktion
„Beleg erstellen“
aufrufen. Stellt
      man diesen Parameter auf Ja, so werden alle Belege in einem Lauf
      erzeugt.

---

## Zahlungsmeldungen (EPA KASSZAME)

Zahlungsmeldungen (EPA KASSZAME)
Bezeichnung
Standardwert
Erklärung
Gewährung zusätzlicher Skonto
      erlaubt
Nein
Teilzahlungen zugelassen
Nein
Auch
      Ausgangsrechnungen aus der Finanzbuchhaltung verwenden
Nein
Steht dieser Schalter auf
Nein
, dann werden nur Ausgangsrechnungen aus der Warenwirtschaft
      angeboten, bei
Ja
werden alle offenen Ausgangsrechnungen
      angeboten.

---

## Washout und Circle (EPA Kontraktstamm_Washout_Circle)

Washout und Circle
(EPA
Kontraktstamm_Washout_Circle)
Bezeichnung
Standardwert
Erklärung
Die
      Kundennummer darf bei einem Washout unterschiedlich sein.
Nein
Wenn
      der Kunde ein Debitor und Kreditor ist, gibt es zwei Kundennummern. In
      diesem Fall muss der Einrichterparameter auf „Ja“ gestellt werden, da ein
      Washout in der Standardeinstellung nur mit der gleichen Kundennummer
      zulässig ist.
Es
      darf nur der Aktuelle Mengenzeitraum betrachtet werden.
Nein
Mit
      diesem Einrichterparameter kann eingestellt werden, ob nur der aktuelle
      Mengenzeitraum beim Washout oder Circle berücksichtigt werden soll. Im
      Standard wird die komplette Restmenge (Menge) des Kontraktes
      genommen.

---

## Ladeträgerbuchungen (EPA LVS_BUCHELADEEINHEIT)

Ladeträgerbuchungen (EPA
LVS_BUCHELADEEINHEIT)
Bezeichnung
Standardwert
Erklärung
Standard Waage Lokalität
Vorbelegung der Ladeträger in der
      Waage
Ja

---

## Buchungssatz Import XML (EPA LEDGERIMPORT)

Buchungssatz Import XML (EPA
LEDGERIMPORT)
Bezeichnung
Standardwert
Erklärung
Script darf geändert
      werden
Nein
VBA
      Script welches mir die Datei holt
Hier
      kann ein VBA Script angegeben werden, welches mir die XML von einem FTP
      Server lokal auf meinen Rechner speichert.
VBS
      Script welches mir die Datei holt
Hier
      kann ein VBS Script angegeben werden, welches mir die XML von einem FTP
      Server lokal auf meinen Rechner speichert.
Schlüsselklasse des
      Importumsetzers
Wenn
      das Hauptkonto in der XML Struktur Alphanumerisch ist so muss diese noch
      in eine numerische Kontozahl umgeschlüsselt werden. Hier wird die
      Schlüsselklasse eingetragen.
Dateiprüfung und Einspielung
      passiert im privaten VBA oder VBS Script
Mit
      diesem Parameter kann eingeschaltet werden, ob eine private Behandlung zum
      Holen, prüfen und einspielen der Dateien in dem privaten Skript vorhanden
      ist. Wird dies ausgeschaltet, so brauch in das Maskenfeld nur der
      Speicherort angegeben werden. Existiert keine private Prüfung kann immer
      nur eine Datei heruntergeladen und verarbeitet werden.

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

## Buchungsperioden (EPA NUMBE_02)

Buchungsperioden (EPA NUMBE_02)
Bezeichnung
Standardwert
Erklärung
Datum muss innerhalb der Periode
      liegen?
Fehler
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
Kostenstellenvorbelegung
      abfragen?
Nein
Die
      hier abgefragte Kostenstelle wird in der Belegerfassung vorbelegt, wenn im
      Sachkontenstamm keine Vorbelegung hinterlegt ist.

---

## Offene Posten (EPA NUMOPSKO)

Offene Posten (EPA NUMOPSKO)
Bezeichnung
Standardwert
Erklärung
Speichern nach
      Skontoaufteilung
Nein
Wählt man die Funktion
Skonto ausbuchen
, so wird
      automatisch gespeichert und die Zahlung ausgeziffert.

---

## Offene Posten (EPA OPVERWALTUNG)

Offene Posten (EPA OPVERWALTUNG)
Bezeichnung
Standardwert
Erklärung
Obligokunden in einer Itembox
      abfragen?
Nein
Bei
      der Abfrage eines Obligokunden geht eine Auswahlliste auf, in der man den
      Kunden Auswählt und mit
F9
bestätigt. Wenn man jedoch die Auswahl mit
ENTER
bestätigen möchte, dann
      kann man hier Ja einstellen.
Bei
      Obligokunden bei ESC in die Auswahl springen?
Nein
Dies
      ist eine spezielle ESCAPE-Behandlung. Wenn man im OP-Verwaltung
Esc
drückt, dann wird nicht die
      OP-Verwaltung verlassen, sondern erst ein weiterer Obligokunde abgefragt.
      Erst wenn man auch bei der Abfrage des Obligokunden
Esc
gedrückt hat, wird die
      OP-Verwaltung verlassen.
¨eClearing¨ und ¨Kasse¨ beim
      Ausziffern überprüfen?
Warnung
Wenn
      Belege bereits in den Modulen eClearing bzw. Kasse verrechnet wurden,
      kommt es zu Konflikten. Wie man mit diesen Konflikten umgehen will, kann
      man hier einstellen:
•
Ignorieren
: Es findet keine Prüfung
      statt
•
Fehler:
Ist der OP bereits in dem Modul
      eClearing oder Kasse verwendet, kann er hier nicht ausgeziffert
      werden.
•
Warnung:
Es wird geprüft, ob der OP-bereits
      verrechnet wurde und man wird vor dem Ausziffern gefragt, ob der OP
      trotzdem verwendet werden soll.
Auszifferungsdatum beim Ausziffern
      mit Belegperioden prüfen?
Warnung
Um
      auch im Nachhinein feststellen zu können, wann ein OP noch offen war, wird
      ein Auszifferungsdatum im Beleg hinterlegt. Wenn die ausgewählte
      Buchungsperiode hinter dem Auszifferungsdatum liegt, kann es zu
      Unstimmigkeiten in der historischen OP-Liste kommen. Es existieren
      folgende Einstellungsmöglichkeiten:
•
Ignorieren
: Es findet keine Prüfung
      statt
•
Fehler:
Liegt die Periode hinter dem vor
      dem Belegdatum, kann nicht ausgeziffert werden.
•
Warnung:
Man wir bei fehlerhaftem Test
      gefragt, ob der OP trotzdem verwendet werden soll.
Periodenfenster
[...]


---

## MaskenTitel (EPA PARTIEVERTEILUNG)

MaskenTitel (EPA PARTIEVERTEILUNG)
Bezeichnung
Standardwert
Erklärung
auch
      nichtfibubelege zulassen (ACHTUNG: Fehlbuchungen!)
Nein

---

## POS-Kasse (EPA POSCASH)

POS-Kasse (EPA POSCASH)
Bezeichnung
Standardwert
Erklärung
Abschlussbestätigung beim
      Belegabschluss
nein
Soll
      der Artikeltext für ´Diverse´ Artikel änderbar sein
Nein
Vorbelegung auf Bruttoerfassung
      ?
Ja
Soll
      Menge mal Preis auf dem Display angezeigt werden?
Nein
Rückgeldbetrag im Display
      anzeigen
Ja
Soll
      ein Lastschrift-Formular gedruckt werden
Nein
Soll
      die letzte erfasste Position stehen bleiben ?
Ja
Warnung bei Bestätigen der Menge
      null
Nein
Warnung bei Bestätigen eines
      Nullpreises
Ja
Soll
      ein gefundener Preis bestätigt werden
Ja
Ist
      die Eingabe negativer Preise erlaubt?
nie
Soll
      Funktion Zeilen-Rabatt aktiviert werden?
Ja
Soll
      ein Scheck gedruckt werden
Nein
Soll
      im Artikelfeld begonnen werden
Nein
Im
      Verkauf Verprobung mit Listenpreis (Warnmeldung)
Nein
Ja:
      Rückgeld in Kassenwährung Nein: wie Zahlungssatz
Ja

---

## MaskenTitel (EPA UMWANDLUNG)

MaskenTitel (EPA UMWANDLUNG)
Bezeichnung
Standardwert
Erklärung
Periodenbehandlung Ware
      einstellen
Nein
Nachlauf Fibu + Druck
      erlaubt
Nein

---

## Kasseneröffnung/Abschluss (EPA VORGKSER)

Kasseneröffnung/Abschluss (EPA VORGKSER)
Bezeichnung
Standardwert
Erklärung
Abschluss ohne Zählung
      möglich?
Ja
Bei
      Einstellung
ja
wird abgefragt, ob eine Zählung erfolgen soll. Bei
nein
immer Zählung, es sei denn durch SPA abgewählt.
Einzelbuchung pro Zahlungsmittel
      ?
Nein
Bei
      Einstellung
ja
wird je Zahlungsmittel ein Einreichungsbeleg
      erzeugt. Das kann für Abstimmungszwecke ganz sinnvoll sein, erhöht aber
      das Belegvolumen. Bei Einstellung
nein
wird ein Sammelbeleg je
      Zahlungsart erstellt.

---

## Zahlungen bearbeiten (EPA ZAHLUNG)

Zahlungen bearbeiten (EPA ZAHLUNG)
Bezeichnung
Standardwert
Erklärung
Abfrage beim Abschluss der Zahlung
      ?
Ja
Soll
      Zahlungsart Bankeinzug aktiv sein?
Ja
Reduzierte
      Displayanzeige
Nein
Automatische Steuer bei
      Entnahmen?
Ja
Sollen Einzahlungen,... über
      Formularsteuerung gedruckt werden?
Nein
Soll
      Zahlungsart Gutschein aktiv sein?
Ja
Soll
      Journal bei Kassenvorgängen gedruckt werden?
Ja
Soll
      ein Lastschrift-Formular gedruckt werden?
Nein
Soll
      Zahlungsart Kreditkarte aktiv sein?
Ja
Soll
      Zahlungsart Scheck aktiv sein?
Ja
Soll
      ein Scheck gedruckt werden?
Nein
Funktion Schublade öffnen auf Maske
      laden?
Ja
Darf
      Skonto gewährt werden?
Ja
Soll
      bei Geldentnahme Steuersatz wählbar sein?
Ja
Zahlungswege auf Maske
      anzeigen?
Nein
Eine
      Rechnung pro Zahlungsmeldung?
Ja
Kassenbericht vor Zahlung
      reorganisieren?
Ja
Der
      aktuelle Kassenbericht wird bei betreten der Zahlungsmaske
      reorganisiert.

---

## Obersachkonten (EPA obersachkonto)

Obersachkonten (EPA obersachkonto)
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

## Entfernungswerk

Entfernungswerk
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Entfernungswerk
Um Kilometerabhängige Frachten zu berechnen, benötigen
Sie für die Entfernungen zwischen den Zonen eine pauschale Entfernungsangabe
Entfernungen
Frachtvariante
Frachtvariante
Gebiet von
Ausgangsgebiet
Gebiet nach
Zielgebiet
Entfernung
Entfernung nach
      Kilometer
Frachtzone
Frachtzone

---

## Frachtvariante

Frachtvariante
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Frachtvariante
[FRAV]
Frachtvarianten geben an, auf welche Weise Waren
verschickt werden. Hier kann z.B. Brief, Päckchen, Paket oder Bahn, Schiff,
Flugzeug o.ä. eingerichtet sein.

---

## Frachttabellen

Frachttabellen
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
In einer Frachttabelle werden für Frachtberechnungen
notwendige Festlegungen getroffen.
Bezeichnung
Bezeichnung für die Fracht
Frachttext
Frachttext
Fracht Formel
Formel
Bedeutung
%
      vom Warenwert
Prozentualer Anteil vom
      Warenwert
Pausch. / Lieferung
Pauschale pro Lieferung
Pausch. / Position
Pauschale pro Warenposition auf der
      Lieferung
Pausch. / km
Pauschale pro Kilometer
      Entfernung
Satz
      / Mengeneinheit
Es
      wird ein fester Betrag pro Mengeneinheit berechnet. Wird z.B. in Tonnen
      fakturiert, so wird die Fracht pro Tonne berechnet.
Satz
      / ME + km
Wie
      oben jedoch unter zusätzlicher Berechnung mit dem entfernungsabhängigen
      Formeltyp
Satz
      / Gewichtseinheiten
Es
      wird ein fester Betrag pro Gewichtseinheit des Artikels
      berechnet
Satz
      / GE + km
Wie
      oben jedoch unter zusätzlicher Berechnung mit dem entfernungsabhängigen
      Formeltyp
Satz
      / Bruttogewichtseinheiten
Es
      wird ein fester Betrag pro Brutto-Gewichtseinheit des Artikels
      berechnet
Satz
      / BruttoGE + km
Wie
      oben jedoch unter zusätzlicher Berechnung mit dem entfernungsabhängigen
      Formeltyp
Satz
      / Verpackungseinheiten
Es
      wird ein fester Betrag pro Verpackungseinheit des Artikels
      berechnet
Satz
      / VE + km
Wie
      oben jedoch unter zusätzlicher Berechnung mit dem entfernungsabhängigen
      Formeltyp
Offene Frachtberechnung
Gibt an, ob die Fracht auf dem Beleg sichtbar
ausgewiesen werden soll (nicht bei Gruppenfracht).
Gruppenfracht im Belegdruck
Gibt bei einer Gruppenfracht an, ob bei der
Belegerfassung das Kennzeichen zur Druckbarkeit der Gruppenfrachtposition
gesetzt werden soll oder nicht. Diese Einstellmöglichkeit ist nur verfügbar,
wenn es sich nicht um eine kalkulatorische Frachtermittlung handelt (diese wird
nie gedruckt) und der Steuerparameter
SPA 980
die Unterd
[...]


---

## Fracht-Texte

Fracht-Texte
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Frachttexte
Für die Standardsprache in Referenz-ERP kann hier ein
beliebiger Text angegeben werden, der für die Anzeige der Fracht auf Belegen
verwendet werden soll.
Für die verschiedenen Sprachen in Referenz-ERP können hier
auch deren Übersetzungen eingegeben werden.
Es können bis zu 100 Texten hinterlegt werden.

---

## Fracht-Zonen

Fracht-Zonen
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Frachtzonen
Frachtzonen
Zone
Nummer der Zone
Variante
Frachtvariante
Bezeichnung
Bezeichnung der
      Frachtzone
Matchcode
Matchcode der Frachtzone
Richten Sie hier Frachtzonen ein. Dies können z.B.
Zonen wie „Nahbereich Bote“, „Nahbereich LKW“, „100km Spedition“ oder ähnliches
sein.

---

## SEPA-Einrichtung überprüfen

SEPA-Einrichtung überprüfen
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Funktion SEPA Einrichtung prüfen
Direktsprung
[SEPAT]
Da SEPA Teilweise parallel zum DTA-Verfahren laufen
muss, ist es von vielen Umständen abhängig, wann das SEPA-Verfahren und wann das
DTA-Verfahren angewendet wird. Da es aufwendig ist, immer alle Punkt
(Steuerparameter, Einrichtung Bankenstamm, Einrichtung Kundenbank usw.) zu
kontrollieren, wurde eine Funktion geschaffen, die diese Daten überprüft. Sie
versucht die Fragestellung zu beantworten: „Warum werden die OP’S dieses Kunden
nicht zum Zahlungseingang/-ausgang SEPA herangezogen?“.
Als einzige optionale Eingabemöglichkeit existiert die
Kontonummer. Wird keine Kontonummer angegeben, dann werden nur Steuerparameter,
Mandantenstamm, Staatstamm und der Bankenstamm überprüft. Gibt man ein Konto an,
erfolgt noch die Überprüfung der Kundenbank und der OP´s des Kunden. Es wird
dabei nur die Bank überprüft, die auch beim automatischen Zahlungsverkehr
verwendet werden würde.
Die OP’s werden daraufhin getestet, ob sie evtl.
gesperrt sind oder für den Auslandszahlungsverkehr gekennzeichnet sind. Es
werden nur die OP’S aufgelistet, die ein Problem haben.
Fehler werden
rot
markiert und Warnungen
gelb
. Bei der
Prüfung der Version wird die Version 2.7 bis zum 01.Februar noch als Warnung
ausgegeben, danach als Fehler. Dieser Fehler führt jedoch nicht dazu, dass die
Datei nicht erstellt wird. Es können von Bank zu Bank und je nach
Übertragungssoftware noch unterschiedliche Versionen zugelassen sein.
Mit STRG+E lässt sich das Ergebnis in Excel laden.

---

## Gesamt-Nullsetzung FiBu zulässig(SPA 102)

Gesamt-Nullsetzung FiBu zulässig(SPA 102)

---

## Shop-Schnittstelle-Lizenz (SPA1103)

Shop-Schnittstelle-Lizenz (SPA1103)
Lizenz für die Shop-Schnittstelle.

---

## Sachkontensperren für Kosten beim Fibuübertrag testen (SPA 1132)

Sachkontensperren für Kosten beim Fibuübertrag testen (SPA 1132)
Wenn Belege aus der Warenwirtschaft in die
Finanzbuchhaltung übertragen werden, so werden die Kostenstellen, Kostenträger
und Kostenobjekte über Gruppen bestimmt, die dem Artikel zugeordnet sind. Dabei
kann es vorkommen, dass Kosten einem Sachkonto zugewiesen werden, in dem eine
Sperre hinterlegt wurde. Dieser Umstand wird jetzt beim Fibuübertrag getestet
und es wird im
Protokoll
Fibuübertrag
ein Eintrag mit einem Hinweis erzeugt,
die Belege gehen
jedoch trotzdem in die Fibu.
Mit diesem SPA kann diese Prüfung abgestellt
werden.

---

## Bei automatischen Stornobelegen Perioden mit Buchungsschluss zulassen (SPA 1134)

Bei automatischen Stornobelegen Perioden mit
Buchungsschluss zulassen (SPA 1134)
Beim Zurücksetzen von Auszifferungen werden für einige
Belegarten (z.B. Restposten, Skonto) automatisch Stornobelege erstellt. Steht
die Periode auf Buchungsschluss oder ist sie bereits abgeschlossen, dann wird
die Periode abgefragt, in die der Stornobeleg gebucht werden soll. Dieser SPA
steuert, wie bei Perioden mit Buchungsschluss behandelt werden sollen.
Hinweis:
Da
Buchungsadministratoren
in Perioden mit
Buchungsschluss buchen dürfen, hat dieser SPA für sie keine
Auswirkung.
Ja
Das Periodenabfragefenster öffnet sich und
      die Periode ist vorbelegt. In dem Hinweistext steht, dass die Periode des
      Ursprungsbeleges bereits auf Buchungsschluss gesetzt wurde, man sie aber
      trotzdem verwenden kann. Ansonsten muss man sie auf eine noch offene
      Periode ändern.
Nein
Das Periodenabfragefenster öffnet sich und die
      nächste mögliche Periode wird vorbelegt. Im Hinweistext steht, dass die
      Periode des Urspungsbelegs nicht mehr verwendet werden darf.

---

## FiBu-Xml-Import-Lizenz (SPA1139)

FiBu-Xml-Import-Lizenz (SPA1139)
Lizenz für den FiBu-Xml-Import.

---

## Jahreswechsel: Abschluss und Eröffnung immer gemeinsam löschen/buchen (SPA 1143)

Jahreswechsel: Abschluss und Eröffnung immer gemeinsam löschen/buchen (SPA
1143)
Wenn ein Jahreswechsel durchgeführt wird, wird in der
Abschlussperiode und in der Eröffnungsperiode jeweils ein Beleg erstellt. Dieser
Steuerparameter legt fest, wie beim Löschen der Belege verfahren wird:
Nein
Es ist möglich die Belege einzeln zu betrachten.
      Beim Löschen erscheint die Meldung:
Sie wollen einen
      Jahreswechselbeleg löschen!
Beachten sie unbedingt, dass zu diesem
      Beleg
ein weiterer Beleg in der
      Abschluss-/Eröffnungsperiode existiert!
Wollen Sie den Beleg wirklich
      löschen?
Ja
Neue Standardeinstellung:
•
Wenn Sie einen Beleg eines Jahreswechsels buchen, so wird immer der
      zweite Beleg mitgebucht.
•
Wenn Sie einen Jahreswechselbeleg löschen, so wird immer auch der
      dazugehörige zweite Jahreswechsel gelöscht.
•
Wenn der zweite Jahreswechsel bereits gebucht ist oder eine
      Löschsperre hat, ist Löschen nicht mehr
möglich.

---

## Worker beendet mit Mainworker (SPA 1149)

Worker beendet mit Mainworker (SPA 1149)
•
Einstellung JA: Wird der Main-Worker (Worker 0) beendet, so erhalten alle
anderen Worker eine Aufforderung sich zu beenden und schließen sich zu Beginn
des nächsten Intervalls.
•
Einstellung NEIN: Wird der Main-Worker (Worker 0) beendet, so bleiben die
anderen Worker aktiv.

---

## Sperre Belegfluss-Belege bei Abweichungen (SPA 1159)

Sperre Belegfluss-Belege bei Abweichungen (SPA 1159)
Wird bei der Erstellung eines Beleges aus Belegfluss
eine Abweichung in den Bruttosummen einer oder mehrerer Positionen festgestellt,
so wird der Beleg gegen FiBu-Übertrag gesperrt, wenn dieser Steuerparameter
gesetzt wurde.

---

## OP-Verwaltung aktiv(SPA 140)

OP-Verwaltung aktiv(SPA 140)
Mit diesem Steuerparameter kann die OP-Verwaltung
aktiviert / deaktiviert werden.

---

## Variante Periodenermittlung für Fibu(SPA 182)

Variante Periodenermittlung für Fibu(SPA 182)

---

## Raffung je Erlöskonto(SPA 185)

Raffung je Erlöskonto(SPA 185)

---

## Objekt(e) nach Ablaufdatum bebuchbar(SPA 201)

Objekt(e) nach Ablaufdatum bebuchbar(SPA 201)
Ja: Nach Überschreiten des Ablaufdatums dürfen LS, RE,
etc. das Objekt geschrieben werden. Nein: Es sind keine Buchungen auf das Objekt
möglich, wenn das Ablaufdatum überschritten wurde.

---

## Artikelumbuchung mit abweichendem Lager(SPA 221)

Artikelumbuchung mit abweichendem Lager(SPA 221)

---

## Methode der Forderungs-Verb.-Zuordnung(SPA 223)

Methode der Forderungs-Verb.-Zuordnung(SPA 223)
Wie die
Forderungen
und Verbindlichkeiten
ermittelt werden hängt von diesem SPA ab. Er
hat zurzeit zwei Ausprägungen:
•
Standard: Ob es sich um Forderungen oder Verbindlichkeiten handelt, ist
vom  Belegtypen abhängig (ER sind immer Verbindlichkeiten, AG sind
Verminderungen der Forderungen, ZA ergibt sich aus den Belegen, die Bezahlt
werden, usw.).
•
Saldo Stichtag: Je nach Saldo des Kunden/Lieferanten wird der Betrag
entweder dem Forderungs- oder dem Verbindlichkeitskonto zugewiesen.
Dieser SPA wirkt für alle nicht abgeschlossenen
Perioden, hat also kein „Gültig ab Datum“. Als Datum wird immer das Tagesdatum
eingetragen und dient nur der Nachverfolgbarkeit.
ACHTUNG:
Man sollte von vornherein
Festlegen, mit welcher Methode man arbeiten will. Ein Wechsel währen des
laufenden Betriebes bringt viele Probleme mit sich ( z.B. stimmen Kontoblätter
wahrscheinlich nicht mehr ) und sollte nur mit Rücksprache mit dem
Systembetreuer erfolgen.
Wird dieser SPA im laufenden Betrieb umgestellt, so
erscheint eine Warnmeldung. Es ist in jedem Fall eine
Reorganisation
der Fibu notwendig und
anschließend müssen die
Bewegungsdaten
getestet werden. Bei
der Umstellung von „
Saldo Stichtag
“ auf „
Standard
“ kann es dazu
kommen, dass trotz Reorganisation nicht alle Werte korrekt sind. Es ist dann
eine Sichtung der Daten von Branchen-ERP notwendig.

---

## Stoffstrombilanz-Lizenz(SPA 225)

Stoffstrombilanz-Lizenz(SPA 225)
Lizenz für die Stoffstrombilanz.

---

## Offene Posten berücksichtigen(SPA 249)

Offene Posten berücksichtigen(SPA 249)
Ja: markierte Belege werden nur dann provisioniert,
wenn der Beleg komplett an die Fibu übergeben ist und keine Offenen Posten mehr
auf diesen Beleg existieren.
Nein: es werden alle markierten Belege provisioniert,
die zumindest im Warenbuch eingetragen wurden.

---

## Fibu-Sperre aus Quellvorgang übernehmen(SPA 272)

Fibu-Sperre aus Quellvorgang übernehmen(SPA 272)
Bei Umwandlungen wird das Sperrkennzeichen für die
Übertragung des Vorgangs in die Fibu wie folgt gesetzt (wenn es gesetzt ist, ist
der Fibu-Übertrag nicht möglich):
gem. Unterklasse: das Kennzeichen wird aus der
Klasse/Unterklasse übernommen, wie es in der Zielklasse defaultmäßig vorbelegt
ist (FRZ/Formularzuordnung)
aus der Quelle: das Kennzeichen wird aus dem
Quellvorgang in den Zielvorgang übernommen. setzen,
n. löschen: das Kennzeichen wird immer gesetzt für den
Zielvorgang, in den umgewandelt wird.

---

## Lagerumbuchungen in Finanzbuchhaltung(SPA 282)

Lagerumbuchungen in Finanzbuchhaltung(SPA 282)

---

## Fremdlager/Vorfakturierung aktiv(SPA 301)

Fremdlager/Vorfakturierung aktiv(SPA 301)
Dieser SPA ist
nicht
mehr ausschlaggebend für
die Behandlung von Fremdlager und Vorfakturierung – hierfür gibt es in dem
Warenerfassungsdialog eigenständige Funktionen. Man aktiviert hier nur noch, ob
bei Lagerumbuchungen eine direkte Umbuchung von Fremdlager- oder
Vorfakturierbeständen freigeschaltet werden soll.

---

## Aut. Buchung von Finanzvorg. in FiBu(SPA 333)

Aut. Buchung von Finanzvorg. in FiBu(SPA 333)
(wenn Kassenvorgänge durchgeführt werden) Hier wird
entschieden, ob jeder Kassenvorgang in die Fibu übertragen wird (ist überhaupt
eine Fibu angeschlossen)

---

## Rechnungsdruck m. Fibu-Übertrag-Abfrage(SPA 337)

Rechnungsdruck m. Fibu-Übertrag-Abfrage(SPA 337)

---

## Bewertungspreise aktiv bei Umbuchungen(SPA 346)

Bewertungspreise aktiv bei Umbuchungen(SPA 346)

---

## Stornovorgänge (Unübertragene) in FiBu (SPA 349)

Stornovorgänge (Unübertragene) in FiBu (SPA 349)
Wird ein Beleg storniert, der noch nicht in die FiBu
übertragen wurde, so muss bei Einstellung „Nein“ kein Übertrag des Belegs und
des Stornobelegs in die FiBu erfolgen.
Bei Einstellung „Ja“ werden beide Belege in die FiBu
übertragen.

---

## Umbuchung der Zahlungsmittel auf Konten(SPA 355)

Umbuchung der Zahlungsmittel auf Konten(SPA 355)
Hier wird entschieden, ob die Zahlungen an der Kasse
gruppiert nach Zahlungsarten auf entsprechend vorbereitete Konten gebucht werden
sollen (geschieht beim Kassenabschluss). Im Einzelnen handelt es sich um in den
Kasseneinstellungen hinterlegten Bargeldkonto, Scheckkonto,
Kreditkartenkonto,...

---

## Automatische Abschöpfung von Unterkasse an Hauptkasse(SPA 356)

Automatische Abschöpfung von Unterkasse an Hauptkasse(SPA
356)
Hier wird entschieden, ob beim Kassenabschluss einer
Unterkasse eine Zählung durchgeführt wird („Nein“) oder ob alle kassenseitig
erfassten Zahlungen der zugehörigen Hauptkasse automatisch gutgeschrieben werden
und so nur eine Zählung nötig ist („Ja“).

---

## Druck der Zamis beim Kassenabschluss(SPA 365)

Druck der Zamis beim Kassenabschluss(SPA 365)
Hier wird entschieden, ob beim Druck des Bons mit der
Information über Details und Stückelung der Bestände einer Kassensitzung alle
fakturierten Zahlungsmittel einzeln gedruckt werden mit Betrag oder summiert
nach Währung und Art gruppiert (Scheck, Kreditkarte,...)

---

## Variante des Fibuübertrags(SPA 41)

Variante des Fibuübertrags(SPA 41)

---

## OP-Verwaltung-Lizenz(SPA 446)

OP-Verwaltung-Lizenz(SPA 446)
Lizenz für OP-Verwaltung.

---

## Stornobelege automatisch ausziffern(SPA 460)

Stornobelege automatisch ausziffern(SPA 460)
Wenn beim Fibu-Übertrag von Gutschriften automatisch
eine Auszifferung des Urbeleges (der Originalrechnung) durchgeführt werden soll,
muss hier ein „Ja“ eingetragen werden.

---

## FIB-Druckstatusprüf. bei Internbelegen(SPA 459)

FIB-Druckstatusprüf. bei Internbelegen(SPA 459)
Interne Belege (Umbuchungen etc.) können beim
Fibu-Übertrag bezüglich ihres Druckstatus wie andere Belege behandelt werden
oder immer auch ungedruckt übertragen werden.

---

## Kunden mit OPs löschen?(SPA 504)

Kunden mit OPs löschen?(SPA 504)
Ja: (wie bisher) es dürfen Kunden mit OPs gelöscht
werden, es kommt vorher noch eine Löschabfrage, allerdings beinhaltet das
Löschen nur ein Setzen des Löschkennzeichens (hat Auswirkungen in Auswertungen,
Listen,...)
Nein: Wenn ein Kunde noch Offene Posten besitzt, darf
der Kunden nicht gelöscht werden, d.h. auch das Löschkennzeichen kann nicht
gesetzt werden.

---

## Fibuübertrag ohne Währungsinformation(SPA 545)

Fibuübertrag ohne Währungsinformation(SPA 545)

---

## Verrechnung offener Posten(SPA 558)

Verrechnung offener Posten(SPA 558)
Beschreibt die Art und Weise, ob und wenn ja wie Fibu
Belege automatisch ausgeziffert werden, wenn die Rechnungen an der Kasse per
Zahlungsmeldung beglichen werden. Möglichkeiten: OPs nie automatisch Ausziffern,
OPs bei passender Zahlung sofort Ausziffern, bei Teilzahlungen nie Ausziffern,
OPs auch bei Teilzahlung Ausziffern und Restposten über den Differenzbetrag
bilden.

---

## Zinsabschlagsteuer berechnen(SPA 555)

Zinsabschlagsteuer berechnen(SPA 555)
Steht dieser Parameter auf
Ja
, werden die
Zinsbuchungen mit
Zinsabschlagsteuer
, wie sie in den
Stammdaten hinterlegt ist, erstellt.

---

## Unterkasse mit Abschöpfung ohne Zählung abschließen(SPA 578)

Unterkasse mit Abschöpfung ohne Zählung abschließen(SPA
578)
Eine Unterkasse mit automatischer Abschöpfung beim
Kassenabschluss kommt standardmäßig ohne Zählung aus. Abgeschöpft wird dann
stets das Bargeldsoll. Umschaltung auf „Nein“ ermöglicht eine Zählung der
Unterkasse mit entsprechender Behandlung einer ggf. aufgetretenen
Zähldifferenz.

---

## Reaktion bei Fremdlagerüberbuchung (SPA 605)

Reaktion bei Fremdlagerüberbuchung (SPA 605)

---

## Automatischer Artikelnachtrag Inventur(SPA 617)

Automatischer Artikelnachtrag Inventur(SPA 617)
Bei „Ja“ wird bei einer Artikelbuchung überprüft, ob
dieser Artikel in einer offenen Inventur liegt. Falls dieser Artikel bisher noch
nicht aufgenommen oder bei der Inventureröffnung nicht vorgetragen wurde, wird
ein Eintrag in den Inventurbestand mit Menge 0 erzeugt. Der Eintrag erfolgt nur,
wenn das Lieferdatum vor dem Inventurstichtag liegt.

---

## Warestorno mit Alternative bez Fibstatus(SPA 657)

Warestorno mit Alternative bez Fibstatus(SPA
657)
Hier kann festgelegt werden, ob die Option
„Stornobeleg erzeugen“ bei der Umwandlung eines Beleges in einen Stornobeleg
freigeschaltet werden soll. Diese bietet die Erzeugung einer Belegkopie für die
Fälle „Immer“, „Nur bei FiBu-Übertrag“ oder „bei FiBu-Buchung“ an.

---

## FIBU-Besonderheiten berücksichtigen für(SPA 663)

FIBU-Besonderheiten berücksichtigen für(SPA 663)
Es kann vorkommen, dass in anderen Ländern als der BRD
die Vorschriften für die Finanzbuchhaltung doch etwas anders sind. Um dem
Programm mitzuteilen, um welches Land es sich handelt, existiert dieser
Steuerparameter. Bisher gibt es nur die Möglichkeit dort Österreich einzutragen.
Das Programm verhält sich dann in folgenden Punkten anders:
•
In der Umsatzsteuervoranmeldung werden die Beträge mit Nachkommastellen
ausgegeben
•
In der Anlagenbuchhaltung wir eine weiter Abschreibungsart „Lineare AfA
Halbjahresregel“ angeboten.

---

## Beleginfos bei automatischer Lagerumbuchung Fremdware (SPA 664)

Beleginfos bei automatischer Lagerumbuchung Fremdware (SPA 664)
Dieser Parameter regelt die Aufbereitung von
Beleginformationen bei automatisch erzeugten Lagerumbuchungen bei
Fremdwareabholung / Fremdlageranlieferung.
Bei „Nein“ wird nur die Belegnummer des
Originalbeleges in die Referenznummer der Lagerumbuchung eingetragen.
Bei „Ja“ werden zusätzlich Informationen zur
Kundennummer und der Vorgangsklasse aufbereitet.

---

## Positionsumbuchung Mengenbehandlung(SPA 666)

Positionsumbuchung Mengenbehandlung(SPA 666)
Berechnung des Komponentenanteils in der Maske
Positionskalkulation. 0 bedeutet der Anteil wird wie in der Komponente angegeben
berechnet. 1 bedeutet Menge wird wie im Rezept angegeben berechnet.

---

## Kein Fibuübertrag (Vieraugenprinzip) mit Mitarbeitern aus zwei Abteilungen(SPA 677)

Kein Fibuübertrag (Vieraugenprinzip)  mit
Mitarbeitern aus zwei Abteilungen(SPA 677)
Mit diesem Steuerparameter kann eingestellt werden,
dass Belege die in die Fibu übertragen werden sollen, erst von einem zweiten
Mitarbeiter Kontrolliert werden müssen.

---

## Privater Fibu Buchungstext(SPA 683)

Privater Fibu Buchungstext(SPA 683)
Mit diesem Steuerparameter kann eingestellt werden, ob
ein privater Buchungstext für die Buchungstextzeile genommen werden soll. Der
private Buchungstext kann über die Private Funktion p_BuchungsText_Hauptzeile
bestimmt werden. Als IN Paramater werden die V_ID und der eigentliche
Buchungstext übergeben. Die Steuerparameter 170 und 171 verlieren nicht Ihre
Gültigkeit.

---

## Auswahllisten ohne Sollhabendarstellung(SPA 687)

Auswahllisten ohne Sollhabendarstellung(SPA 687)
Hier kann man die Sollhabendarstellung in
Auswahllisten abschalten. Sollbuchungen werden dann negativ, Habenbuchungen
positiv dargestellt.

---

## Gruppenanfänge immer druckbar machen(SPA 702)

Gruppenanfänge immer druckbar machen(SPA 702)
Gruppenanfänge  - dies gilt für die Gruppe, die
Umbuchung und die Gruppe aufgrund einer Sammelumwandlung) - werden bei „Ja“
immer mit gedruckt (sofern im Formular eingerichtet). Bei „Nein“ erfolgt der
Druck wegen eines Softwareproblems eher zufällig.

---

## Mengenbuchung bei FiBu_Übertrag(SPA 720)

Mengenbuchung bei
FiBu_Übertrag(SPA 720)
Bei ‚Ja‘ wird beim FiBu-Übertrag ausgewertet, ob in
der Kontozuordnung der Erlöskennziffern Konten für die Mengenbuchung in der FiBu
vorhanden sind. Ist das der Fall, so wird ein Mengenbeleg in der FiBu erstellt.
Bei ‚Nein‘ wird auch bei vorhandener Kontozuordnung kein Beleg erstellt. Durch
die Aktivierung dieses Steuerungsparameters müssen Rohware-Abschläge vor der
Umwandlung zur Finale zwingend an die FiBu übertragen werden, da sonst eventuell
auftretende Mengenänderungen nicht erkannt werden können.

---

## Betrag oder Preisbuchung bei der Wertrechnung/Gutschrift beim Washout oder Circle(SPA 821)

Betrag oder Preisbuchung bei der Wertrechnung/Gutschrift beim Washout oder
Circle(SPA 821)
Mit diesem Steuerparameter kann eingestellt werden, ob
mit Preis * Preiseinheit in der Abschluss Rechnung/Gutschrift gerechnet werden
soll, oder ob der Differenz Betrag gebucht werden soll.

---

## FiBu Zinsbelege mit openTRANS drucken (SPA 840)

FiBu Zinsbelege mit openTRANS drucken (SPA 840)
Ist dieser Steuerparameter aktiviert, so wird in der
Finanzbuchhaltung die Möglichkeit eröffnet für openTRANS-Kunden einen Zinsbeleg
zu drucken und auf diesem Weg mit openTRANS zu versehen und zu versenden.

---

## FRZ-Unterklasse für FiBu-Zinsbelege (SPA 841)

FRZ-Unterklasse für FiBu-Zinsbelege (SPA 841)
(Standard ist 0) Hier kann festgelegt werden, aus
welcher Unterklasse der Rechnung (Vorgangsklasse700) der FiBu-openTRANS-Export
seine Einstellungen übernehmen soll.

---

## FiBu-Buchungstext in Kassenbuchungen analog halten (SPA 847)

FiBu-Buchungstext in Kassenbuchungen analog halten (SPA
847)
Wird in der Kasse eine Zahlung vorgenommen, so wird
der Buchungstext der FiBu mit dem Namen der Kasse identisch sein. Wird dieser
Steuerparameter eingeschaltet, so wird der Buchungstext aus dem angegebenen
Buchungstext der Kasse übernommen.

---

## LVS Ladeträger Umbuchung aktiv(SPA 946)

LVS Ladeträger Umbuchung aktiv(SPA 946)
Mit diesem Steuerparameter kann die automatische
Erstellung von Umbuchungen ein- und ausgeschaltet werden, die geschieht, wenn
z.B. ein Artikel des Lagers B auf einen Ladeträger gebucht werden, der auf einer
Lokalität des Lagers A steht. Dieses Verhalten wurde nachträglich in Referenz-ERP
eingeführt und wird in der Standardeinstellung des SPA auch so gebucht.
Der Steuerparameter bietet die Chance, dieses
Verhalten bewusst zu unterbinden.

---

## eBilanz aktiv (SPA 949)

eBilanz aktiv (SPA 949)
In Referenz-ERP existiert die Möglichkeit die eBilanz bis
zur Taxonomie-Version 5.2 zu pflegen. Diese SPA steht standardmäßig auf
Nein
und muss erst aktiviert werden, damit die Funktionen aktiv sind.
Dieses Verfahren ist abgekündigt. Referenz-ERP unterstützt jetzt
eBilanz-Online
.

---

## FiBu Export mit Mengeninfos versorgen (SPA 961)

FiBu Export mit Mengeninfos versorgen (SPA 961)
Bei Einstellung auf ‚Ja‘ werden erweiterte
Informationen der Ware an den erzeugten FiBuBeleg übergeben. Diese sind für
spezielle Exporte an externe Schnittstellen notwendig.
ACHTUNG: Dieser SPA darf nur in Absprache mit einem
Branchen-ERP-Mitarbeiter verändert werden.

---

## HWG Auswertung aktiv (SPA 966)

HWG Auswertung aktiv (SPA 966)
Dieser Steuerparameter deaktiviert das
Managementinformationssystem [MIS] / HWG Auswertung. Es wird nicht weiter
unterstützt. Die inhaltlichen Anforderungen sind abgedeckt durch die
Periodenerfolgsauswertung und das Warenbuch [WBA].

---

## Forderungskonten umbuchen(SPA 968)

Forderungskonten umbuchen(SPA 968)
Wenn für Personenkonten im laufenden Betrieb die
Forderungsgruppe geändert wird, muss der aus diesem Personenkonto resultierende
Forderungs- bzw. Verbindlichkeitsbetrag von den Konten der alten
Forderungsgruppe auf die Konten der neuen Forderungsgruppe umgebucht werden.
Dies geschieht beim Jahreswechsel, wenn dieser Parameter auf
Ja
steht.

---

## 9-stellige Sachkontonummern(SPA 981)

9-stellige Sachkontonummern(SPA 981)
Wenn bei diesem Steuerungsparameter Ja eingetragen
wird, so können Sachkontonummern mit bis zu 9 Stellen verwendet werden.

---

## Vorsteuerabzug

Vorsteuerabzug
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Abzugsfähige Vorsteuer
Ein Vorsteuerabzug ist dann möglich, wenn entweder
•
eine Rechnung vorliegt und die Leistung empfangen worden ist oder
•
eine Rechnung vorliegt und die Zahlung bereits erfolgt ist.
Für
den Vorsteuerabzug ist also in jedem Fall der Eingang der Rechnung zwingend
erforderlich, was wiederum bedeutet, dass die Vorsteuer erst der Periode
zugeordnet werden darf, in der die Rechnung vorliegt.
Wird
z.B. eine Rechnung am Jahresende erfasst, so kann es vorkommen, dass Rechnung
erst im darauffolgenden Jahr eingeht.
Um diesen Sachverhalt gerecht zu werden, kann in
Referenz-ERP für Eingangsrechnungen, Eingangsgutschriften sowie für Sonstige Belege
ein Eingangsdatum erfasst werden. Die Erfassung eines Eingangsdatums ist nur
dann notwendig, wenn die Periode des Eingangsdatums sich von der Periode des
Beleges unterscheidet. Bei der Erfassung wird geprüft, ob das Eingangsdatum
hinter dem Belegdatum liegt. Diese Prüfung lässt sich mit dem
SPA 1130
„Eingangsdatum muss hinter dem Belegdatum liegen“ abstellen.
Vor dem Erstellen einer Umsatzsteuervoranmeldung sind
folgende Punkte zu beachten:
In der Anwendung „Abzugsfähige Vorsteuer“ werden alle
Belege aufsummiert, bei denen sich die Periode des Eingangsdatums hinter der
Periode des Belegs liegt. In dieser Anwendung sind folgende Varianten
vorhanden:
•
Variante „Nach Kennziffer Steuer“: Die Steuer wird nach der Kennziffer
auf dem Umsatzsteueranmeldeformular gruppiert.
•
Variante „Nach Klasse/Schlüssel/Gruppe“: Die Steuer wird nach den
Steuersätzen gruppiert.
In beiden Varianten kann man sich mithilfe der
Funktion
Einzelbelege
F6
die entsprechenden Belege ansehen.
Für die in der Anwendung „Abzugsfähige Vorsteuer“
aufgeführten Beträge/Steuerpositionen müssen jeweils zwei Steuer-Direktbuchungen
erstellt werden:
1.
Eine Buchung in die Periode des Beleges, die die Steuer auf ein Konto
"abweichende Periode" umbucht.
2.
Eine Buchung, die die Steuer
[...]


---

## A1netActiveX.Registry.Tester.exe

A1netActiveX.Registry.Tester.exe
Dieses Programm kann über die
Kommandozeile
ausgeführt
werden und gibt Auskunft darüber, ob bestimmte Anforderungen hinsichtlich des
Referenz-ERP-Hauptmenüs. des Referenz-ERP-Clienten an das Umfeld gegeben bzw. erfüllt
sind.
Dabei bedient es sich der gleichen Methodiken die der
Referenz-ERP-Client beim Start der Referenz-ERP-Anwendung auch durchführt. Wenn dabei
Anforderungen an die Umgebung nicht gegeben sind, vermerkt Referenz-ERP das als
System-Hinweis.
Somit ist das Kommandozeilen-Programm als reines
Service-Programm zu verstehen.

---

## Abkündigung: JRCON-Belegversand

Abkündigung: JRCON-Belegversand
Seit vielen Jahren verfügt Referenz-ERP über eine
Möglichkeit Warenwirtschaftsvorgänge sowie Mahnungen und Zinsen via Mail zu
Versenden. Auch hier gilt das gleiche, wie für die JRCON-Online Waage. Sollten
Sie diesen Versand noch nutzen, sprechen Sie unseren Vertrieb an.
Tags:
Abkündigung

---

## Anlegen eines neuen Wirtschaftsjahres (WJ) am Beispiel 2012:

Anlegen eines neuen Wirtschaftsjahres (WJ) am Beispiel
2012:
Zur Einrichtung eines Geschäftsjahres sind folgende
Eintragungen erforderlich:
•
sinnvolle Bezeichnung, z.B. Wirtschaftsjahr 20xx
•
Datumsvorgaben zum Abprüfen der Gültigkeit eines Datums in der DB
•
Nr.-Kreis des Buchungsjournals für dieses Wirtschaftsjahr
•
Periodeneinteilung Ware = 12 Normalperioden
•
Periodeneinteilung Fibu = 12
(12 Normalperioden + Eröffnung +
Abschluss)
Direktsprung
[JAHR]
, dann
Neu
F8
Geschäftsjahr = 2012
Ausführliche Bezeichnung = Geschäftsjahr 2012
Datum Beginn - Datum Ende = 01.01.2012 /
31.12.2012
Periodeneinteilung Vorjahr kopieren = Nein (nur in
Spezialfällen auf Ja setzen; siehe dazu
‚Hinweis zum Feld Periodeneinteilung Vorjahr kopieren‘
)
Anzahl Perioden Ware = 12
Anzahl Perioden FiBu = 12
Journalnummernkreis = das entsprechende
Buchungsjournal mit F3 auswählen
Kleinstes / größtes Datum = möglichst weit fassen für
die Stammdatenerfassung, da hiergegen die Eingabe von Gültigkeitszeiträumen etc.
geprüft wird. Eine Eingabe außerhalb dieses Datumsbereichs ist nicht zugelassen
und wird mit einer Fehlermeldung abgewiesen.
Warndatum = dies kann z.B. das laufende Jahr sein; bei
Eingabe eines Datums außerhalb dieses Bereichs wird eine Warnmeldung ausgegeben
und man muss diese mit Ja bestätigen, wenn man dieses Datum wirklich eingeben
möchte.
F10
Perioden Fibu
F11
Perioden Ware
ESC
und
Speichern
F9
Hinweis zum Feld Periodeneinteilung Vorjahr
kopieren
Das Kopieren der Perioden ist nur bei speziellen
Einteilungen wie etwa Dekaden als Einrichtungshilfe zu verwenden. Die Perioden
werden
ohne Plausibilitätsprüfung
unter Ersetzung des Jahres
dupliziert (Achtung für diesen Fall auch bei Schaltjahren).
Für
Monatsperioden (was sehr häufig der Fall ist) genügt es in den Feldern ‚Anzahl
Perioden‘ die Zahl 12 einzutragen. Dann werden die Perioden automatisch
angelegt.
Das Feld Periodeneinteilung Vorjahr kopieren bleibt dafür auf
‚Nein‘ stehen.

---

## Dokumentenverwaltung

Dokumentenverwaltung
Mit der zunehmenden Fülle an Informationen und den
Anforderungen, diese auf Knopfdruck zur Verfügung zu stellen, wird die digitale
Dokumentenverarbeitung zu einer zentralen Leistung der Unternehmens-EDV:
Selbsterstellte Dokumente werden direkt archiviert, Eingangsbelege werden
eingescannt, Dateien oder E-Mails werden abgelegt. Nach allen Informationen kann
unter einer einheitlichen Oberfläche recherchiert werden.
Das
Referenz-ERP Archiv
bietet Ihnen in zwei
Ausbaustufen die elektronische Ablage für alle Dokumente Ihres Unternehmens:
Stufe I
Belege laut Abgabenordnung, wie Rechnungen,
Gutschriften, ...
Alle in Referenz-ERP erstellten Dokumente und Auswertungen:
Aufträge, Angebote, Kontrakte, Mahnungen, …
Übergabe von Dokumenten aus Word, Excel, Outlook an
Referenz-ERP: Briefe, Kalkulationen, E-Mail
Übernahme von Dateien und Verknüpfung mit Referenz-ERP
Elementen: Sicherheitsdatenblatt zum Artikel, Bauanleitung., ..
Stufe II
Im Stapel eingescannte Belege
Online eingescannte Belege
Das Archiv ist vollständig in Referenz-ERP integriert und
bietet gegenüber externen Archiven damit entscheidende Vorteile:
Integrierte Funktionalität mit einheitlicher
Oberfläche in einem Programm
Direkte Verknüpfung von Archiv, Stammdaten und
Bewegungsdaten
Zugriffsmöglichkeit aus allen Referenz-ERP
Programmbereichen
Einfache Installation und Handhabung
Zur einfachen Bedienbarkeit gehört auch, dass alle
internen Dokumente im einheitlichen PDF- bzw. TIFF-Format gespeichert werden.
Diese weltweiten Standards bieten aus sich selbst heraus hohe Sicherheit und
leistungsfähige Betrachtungswerkzeuge. Arbeitsplätze, die auf das Archiv
zugreifen sollen, müssen lediglich zusätzlich zu Referenz-ERP über einen geeigneten
Viewer verfügen; dieser wird mit Referenz-ERP ausgeliefert. Dies alles stellt sicher,
dass der
Einführungsaufwand
gering bleibt.
Die
Sicherheit
wird großgeschrieben:
Alle Unterlagen werden im Archiv verschlüsselt
abgelegt und sind somit gegen Veränderungen ge­schützt.
Archivierungspflicht!
S
[...]


---

## Buchungsadministratoren

Buchungsadministratoren
Hauptmenü
Administration
Geschäftsjahr / Perioden
oder Direktsprung
[PERBA]
In gesperrte Perioden kann nicht mehr gebucht werden.
Um nachträglich Buchungen in bereits gesperrte Perioden durchzuführen, müssen
diese erneut geöffnet werden. Dabei werden die Perioden für alle Bediener
freigegeben.
In dem Modul “Buchungsadministratoren“ können gezielt
Bediener bestimmt werden (sog. Buchungsadministratoren), die in eine gesperrte
Periode buchen dürfen. Die Periode muss dazu nicht wiedereröffnet werden. Für
Buchungsadministratoren verhält sich die gesperrte Periode wie eine geöffnete
Periode. Für alle anderen Bediener bleibt die Periode weiterhin bis zur
Wiedereröffnung für jegliche Buchungen gesperrt.
Buchungsadministratoren werden für eine spezielle
Periode angelegt. Das bedeutet, dass der Buchungsadministrator nur in die
gesperrte Periode buchen kann, für die er angelegt wurde. Soll ein Bediener die
Berechtigung für mehrere Perioden haben, so muss er für jede einzelne Periode
als Buchungsadministrator eingetragen werden.
Felder der Buchungsadministratoren
Bezeichnung
Beschreibung
Periodenbereich
Gibt
      an, ob die Periode für die Ware oder für Fibu ist.
Wirtschaftsjahr
Das
      Wirtschaftsjahr, auf das sich diese Periode bezieht.
Periode
Gibt
      die Periode als Monatszahl aus
Bezeichnung
Gibt
      die Periode als Monatsnamen aus
Bedienerkurzname
Zeigt an, welcher Bediener der
      Periode als Buchungsadministrator zugewiesen wurde. (Kürzel)
Bedienername
Zeigt an, welcher Bediener der
      Periode als Buchungsadministrator zugewiesen wurde. (Ganzer
      Name)
BedienerId
Zeigt an, welcher Bediener der
      Periode als Buchungsadministrator zugewiesen wurde. (Bediener
      ID)
Tipp:
Wenn man Bediener bei der Neuanlage nicht immer
wieder neu eingeben möchte, so kann man mit der Funktion
Speichern unter
einen bereits
bestehenden Datensatz als Vorlage nehmen.
Hinweis zu abgeschlossenen Perioden:
Man beachte, dass es
[...]


---

## Buchungsadministratoren: Pfleger

Buchungsadministratoren: Pfleger
Kopfdaten
Im Kopfbereich findet man alle Daten vor, um die
Buchungsadministratoren einer eindeutigen Periode zuzuordnen.
Um bei der Neuanlage eine Periode auszuwählen, wird
zuvor den Periodenbereich und das Wirtschaftsjahr bestimmt. Um den Datensatz zu
speichern, müssen alle drei Felder ausgefüllt sein. Nach dem Speichern können
diese nicht mehr verändert werden.
Bezeichnung
Beschreibung
Periodenbereich
Hier
      wird festgelegt, ob eine Periode aus der Warenbuchhaltung (Ware) oder aus
      der Finanzbuchhaltung (FiBu) gewählt werden soll. Der Bereich kann
      mithilfe von
F3
bestimmt
      werden.
Wirtschaftsjahr
In
      diesem Feld wird das Wirtschaftsjahr eingetragen, auf das sich die Periode
      bezieht.
Via
F3
- Taste kann hier eine
      Auswahl über alle Wirtschaftsjahre getroffen werden.
Im
Neu
-Fall wird das Feld mit dem
      aktuellen Wirtschaftsjahr vorbelegt.
Periode
Hier
      wird die Periode eingetragen.
Mit
      der Taste
F3
werden alle
      geöffneten und gesperrten Perioden angezeigt, die zu dem gewählten
      Periodenbereich und dem Wirtschaftsjahr gehören.
Datentabelle
In der Datentabelle können der Periode ein oder
mehrere Buchungsadministratoren zugeordnet werden.
Um einen Bediener zu einem Buchungsadministrator zu
ernennen, klickt man in ein leeres Feld der Datentabelle und wählt mit der
F3
-Taste den entsprechenden Bediener aus.
Die Berechtigung können einem Bediener wieder genommen werden, indem mit
STRG+SHIFT+ENTF
die Zeile mit dem
jeweiligen Bediener gelöscht oder indem sein Kürzel entfernt wird.
Befinden sich in der Datentabelle keine Bediener, so
gibt es keine Buchungsadministratoren für die Periode.
Bezeichnung
Beschreibung
Bedienerkürzel
Kurzbezeichnung des Bedieners. Die
      Auswahl kann mithilfe von
F3
erfolgen.
Bedienername
Name
      des Bedieners

---

## Lagerumbuchung

Lagerumbuchung
Eine Lagerumbuchung kann nur dann erfolgreich mit dem
Scanner abgearbeitet werden, wenn diese im System erfasst worden ist. Eine
Lagerumbuchung wird unter
[LGU]
angelegt.
Des Weiteren ist zu beachten, dass der Scanner auf dem
Ziellager arbeitet. Das Lager kann unter
[VKONS]
eingerichtet werden. Dazu muss man
sich mit dem Bediener des Scanners in Referenz-ERP anmelden und das Lager
umstellen.
Es muss ein Branchen-ERP Etikettendruck Dokument eingerichtet
werden, welcher die Scancodes in EAN 128 Codiert für die Lagerumbuchung
enthält.
Folgende Scancodes werden für die Lagerumbuchung
benötigt.
1.
LGU + V_numnummer + eventuell die Lokalitätsnummer  z.B. LGU 4711 123
2.
STORNO um den letzten abgesetzten Befehl zu stornieren
3.
LGUENDE um die Lagerumbuchung abzuschließen
Folgende
Einrichtungen
haben direkten Einfluss auf
die Bearbeitung einer Lagerumbuchung mit dem Scanner.
Felder auf Registerkarte
      Vorgangseinstellungen
Bedeutung
Warenbewegungsaddonfeld
Als
      Sonderfunktion steht die Möglichkeit bereit, die Originalmenge des Beleges
      vor Korrektur zu sichern, hierbei kann ein beliebiges Feld in dem
      Warenbewegungsaddon definiert werden.
Unbearbeitete Position auf 0
      setzen
Mit
      diesem Parameter kann eingestellt werden, ob alle nicht bearbeiteten
      Positionen auf 0 gesetzt werden sollen. Dies ist nur für den Fall
      Interessant wenn keine Teildisposition gemacht wird.
Teildisposition
      Lagerumbuchung
Mit
      dieser Einstellung kann eingestellt werden, ob der Beleg der mit dem
      Scanner bearbeitet wird korrigiert werden soll, oder ob eine
      Teildisposition vorgenommen werden soll. Dies bedeutet, dass ein neuer
      Vorgang mit der nicht gelieferten Ware erstellt wird.
Buchungstyp
      Lagerumbuchung
Hier
      kann hinterlegt werden, welcher Buchungstyp der Lagerumbuchung zugeordnet
      werden soll, nach dem diese erfolgreich Bearbeitet worden ist.
Lagerumbuchung Addon
      Speichern

[...]


---

## AI-Stammdaten

AI-Stammdaten
Sollte ein Scancode einmal nicht in der Liste
enthalten sein, so kann der Scancode unter der Funktion Neu eingetragen
werden.
AI
AI-Bezeichnung
KurzBezeich
AI-Typ
Breite
-201
Minderwertigkeits
      Kennzeichen
MDW
-
20
-200
Löschanforderung Scanner
LOE
-
0
-127
Teildispo Druck
AT-D
-
0
-126
Lagerplatz Ausgang Ende
LPA-E
-
0
-125
Lagerplatz Ausgang
LPA-S
-
0
-124
Produktion Ausgang Ende
PA-E
-
0
-123
Produktion Ausgang
PA-S
-
0
-122
Produktions Eingang Ende
PE-E
-
0
-121
Produktions Eingang
PE-S
-
0
-120
Waage Ende
WA-E
-
0
-119
Waage Anfang
WA-S
-
0
-118
Felddaten
FLD
-
0
-117
Felddaten Laden
FLD-L
-
0
-116
Laborwaage Abschluss
LABWE
-
0
-115
Laborwaagenanschluss mit
      Waagennummer
LABW
-
0
-114
Teildispo Ende
AT-E
-
0
-113
Teildispo Start
AT-S
-
0
-112
Lagerplatz Ende
LP-E
-
0
-111
Lagerplatz Start
LP-S
-
0
-110
-
0
-109
-
0
-108
Etiketten Druck
ET
-
0
-107
Inventuraufnahme Ende
IV-E
-
0
-106
Inventuraufnahme Start
IV-S
-
0
-105
Labordaten Ende
LAB-E
-
0
-104
Labordaten Start
LAB-A
-
0
-103
Kommission Ende
AU-E
-
0
-102
Kommission Start
AU-S
-
0
-101
Eingangsvorgang Ende
EV-E
-
0
-100
Eingangsvorgang Start
EV-S
-
0
-30
Mengeneingabe per Hand
MPH
Menge
0
-7
Scanner Originalwerte
Origi
Artikel
0
-6
UPC-A Code
UPCA
Artikel
0
-5
EAN
      8 Barcode
EAN8
Artikel
0
-4
EAN
      13 Barcode
EAN13
Artikel
0
-3
Nationale
      Verpackungseinheit
NVE
-
0
-2
Internationale
      Liefernummer
ILN
-
0
-1
undefiniert
?
-
0
0
Serial Shipping Container
      Code
NVE
-
0
1
EAN
      Nummer der Handelseinheit
EAN
Artikel
0
2
EAN
      der Verpackung
EAN
Artikel
0
10
Charge / Partie
Charge
Partie
0
15
Mindesthaltbarkeitsdatum
MHD
MHD
50
21
Seriennummer
SN
-
25
30
Menge in Stück
Mng
Menge
0
37
Menge in Stück
Stck
Menge
0
91
Ladeträgereinheit
LTR
-
0
92
LokalitätsNummer
LOK
-
0
97
Box
Bo
-
98
Lager
LG
-
0
99
Lagerplatz
LP
-
0
231
Chargennummer
CNr
-
0
3100
Nettogewicht in
      Kilogramm
Mng
Menge
0
3101
Nettogewicht in
      Kilogramm
Mng
Menge
0
3102
N
[...]


---

## Mindestanforderung für die Scanner-Hardware

Mindestanforderung für die Scanner-Hardware
Die Spefikationswerte unten in der Tabelle sind aus
den Spezifikationsdaten des  Datalogic Memor Scanner entnommen worden. Die
sind als Referenz Daten zu sehen.
Hardware
    Anforderungen
Expansion Slots: Secure Digital
      (user accessible)
System Ram Memory: 64 MB
Operating System: Windows CE
      5.0
Microprocessor: Intel® XScale PXA255
      @ 200 MHz
System Flash Memory: 128 MB
Local Area Network: IEEE 802.11b/g
      (WLAN)
Interfaces: USB
      Connector

---

## Schritt 3 Abschluss

Schritt 3 Abschluss
Schritt 3.1: Statistik einsehen
Unter Hauptmenü
Informationen
Sonstiges
Compliance Statistik kann man die Statistiken
der Prüfungen einsehen. Diese helfen dabei, bei ggf. zu vielen oder zu wenigen
Prüfungen, das Dienstleistungspaket bei AEB anzupassen.
Schritt 3.2: Prozessergebnisse einsehen
Um einzusehen, wo die Prozesse der
Verbotslistenprüfung ausgeführt wurden, gibt es mehrere Auswahllisten (hier kann
mit
F2
ein Filter für die Compliance
Ergebnisse gesetzt werden):
-
[AGB]
Angebotsbearbeitung
-
[AUB]
Auftragsbearbeitung
-
[LIB]
(Variante 2: komplexe
Auswahlliste) Lieferscheinbearbeitung
-
[REB]
Rechnungen
-
[BAB]
Bestellanfragen
-
[BSB]
Bestellungen
-
[ELB]
Eingangslieferscheine
-
[ERB]
Eingangsrechnungen

---

## e-Clearing

e-Clearing
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Direktsprung
[ECL]
In der Finanzbuchhaltung Referenz-ERP besteht die
Möglichkeit Bankbelege (Zahlungseingang oder Ausgang) maschinell einzulesen und
gegebenenfalls die Kontierung und Auszifferung automatisch vornehmen zu lassen
im strukturierten MT940(Swift) Format. Pro physische Datei können beliebig viele
logische Dateien bzw. Kontoauszüge existieren.
Die Währung des Bankkontos muss mit der Zentralwährung
des Mandanten übereinstimmen bzw. muss im Kontoauszug die Zentralwährung des
Mandanten mit angegeben sein.

---

## eBilanz-Online Kontensalden übertragen

eBilanz-Online Kontensalden
übertragen
Hauptmenü
Abschlussarbeiten
e-Bilanz
eBilanz-Online Kontensalden
Direktsprung
[EBOK]
.
Feld
Beschreibung
Periode / Jahr
Hier
      gibt man die Periode an, bis zu der die Salden übertragen werden sollen.
      Die Salden werden immer für alle Normalperioden und die Eröffnungsperiode
      des angegebenen Jahres bis zu der hier angegebenen Periode gebildet. Der
      Zeitraum ergibt sich aus dem Anfangsdatum und Enddatum aus dem
      Periodenstamm.
Der
      Zeitraum muss mit dem Start-und Enddatum der periodenbezogenen Stammdaten
      in ebilanz-Online übereinstimmen.
Bilanzart
Es
      können Sachkonten so gekennzeichnet werden, dass sie nur für eine
      Bilanzart (Handels-, Steuerbilanz bzw. für alle Bilanzarten) gelten. Hier
      kann man nun auswählen, aufgrund welcher Konten zusammengestellt
      werden.
Steuerbilanz: Alle Konten, die im
      Sachkontenstamm mit „Steuerbilanz“ oder  „alle Bilanzarten“
      gekennzeichnet sind.
Handelsbilanz: Alle Konten, die im
      Sachkontenstamm mit „Handelsbilanz“ oder  „alle Bilanzarten“
      gekennzeichnet sind.
Mandant
Hier
      wird die Mandantenbezeichnung aus dem Mandantenstamm vorgeschlagen. Diese
      Bezeichnung muss mit dem Mandantennamen der periodenbezogenen Stammdaten
      in eBilanz-Online übereinstimmen.
Version
Die
      Bezeichnung der Version. Diese muss mit der Version der periodenbezogenen
      Stammdaten in eBilanz-Online übereinstimmen.
Benutzer
Name
      eines unter eBilanz-Online eingerichteten Benutzers.
Passwort
Passwort des Benutzers.
Sind alle Daten erfasst, können die ermittelten
Kontensalden mit der Funktion
„Kontensalden
übertragen“
F9
direkt über
einen Webservice an das eBilanz-Online übertragen werden. Mögliche Fehler wie
z.B.:
•
„Die periodenbezogenen Stammdaten wurden
nicht gefunden (Zeitraum, Mandant oder Version überprüfen)
.“
Mögliche Ursachen sind:
1.
Der Zeitraum, Mandant oder die Version stimmen nicht
[...]


---

## Erlöskennziffern

Erlöskennziffern
Hauptmenü
Administration
Erlöskennziffern
Mit dem Erlöskennziffernsystem wird die automatische
Verbuchung von WaWi-Vor­gängen in die FIBU gesteuert.
Der relevante GuV-Bereich kann prinzipiell auf 2
Weisen strukturiert sein
1.
Wareneinkaufs- und Warenverkaufskonten lt. Steuersatz
2.
Wareneinkaufs- und Warenverkaufskonten nach Artikel / Warengruppe / etc.
Für den letzten Fall sind entsprechende
Erlöskennziffern einzupflegen, die im Artikel­stamm hinterlegt werden
können. (z.B. EKZ 1 → WG01, EKZ 2 → WG02 usw.)
Funktion der Elemente
Über das Erlöskennziffer-System wird die Schnittstelle
zwischen Warenwirtschaft und Finanzbuchhaltung in Referenz-ERP definiert. Die Elemente
beeinflussen, welche Erlös- und Aufwandskonten (Warenverkauf / Wareneinkauf)
automatisch bebucht werden.
Folgende Elemente sind beteiligt:
Erlösklassen
[ERLK]
Erlöskennziffern
[EKZS]
Erlöskontenzuordnung
[EKZZ]

---

## Erlöskennziffer / Kontozuordnung

Erlöskennziffer / Kontozuordnung
Hauptmenü
Administration
Erlöskennziffern
Erlöskennziffer/Kontozuordnung
oder Direktsprung
[EKZZ]
Hier erfolgt die Verknüpfung der Elemente
•
Erlöskennziffer
•
Gültigkeit der Eintragungen
•
Steuerschlüssel
•
Erlösklasse
•
Steuergruppe
•
Buchungsklasse
mit den Konten der Finanzbuchhaltung. Hier kann man
die Bearbeitung wie bei der normalen Stammdatenpflege Datensatz für Datensatz
vornehmen oder aber ganze Gruppen von Datensätzen gleichzeitig ändern. Für die
gleichzeitige Bearbeitung der Datensätze kann man unter „gültig ab“ in den
Feldern Steuerschlüssel, Erlösklasse bzw. Steuergruppe einen Haken setzen.
Setzt man z.B. beim Steuerschlüssel den Haken, so
werden in der Datentabelle alle möglichen Kombinationen für Erlösklasse und
Steuergruppe angezeigt. In der so entsehenden Übersicht kann man schnell
erkennen, wenn Konten falsch zugeordnet sind. Die Felder rechts von den Haken
geben die Sortierungsreihenfolge an. Sie wird immer in der Reihenfolge gesetzt,
in der man die Haken setzt.
Die Schlüsselfelder Steuerschlüssel, Erlösklasse und
Steuergruppe links sind auch im Ändern-Fall aktiv, wobei man jedoch nicht die
Werte ändert, sondern die anzuzeigenden Daten auswählen kann.
Felder der Erlöskennziffer / Kontozuordnung:
Felder
EKZ
      Nummer
Die
      Erlöskennziffer, die im Artikel hinterlegt ist.
Gültig ab
Mit
      Hilfe der Angabe eines Datums hat man die Möglichkeit zukünftige
      Änderungen der Konten für die Kombination aus EKZ Nummer, Erlösklasse,
      Steuerschlüssel und Buchklasse vorab in die Datenbank einzupflegen um dann
      zum entsprechenden Datum Buchungen auf den richtigen Konten zu
      erhalten.
Steuerschlüssel
Es
      ist möglich, Erlöse nach steuerlichen Gesichtspunkten zu differenzieren
      (Verprobung Umsatzsteuervoranmeldung). Die Definition der Steuerschlüssel
      erfolgt bekannt­lich im Rahmen der Firmenkonstanten unter dem Punkt
      Steuerschlüssel. Der Steuerschlüssel wird im
[...]


---

## FiBu-Übertrag und EKZ

FiBu-Übertrag und EKZ
Der Programmteil FiBu-Übertrag
[FIB]
trägt die selektierten Vorgänge in die
Rela­­­tion Datenstrom ein. In der AW-Box erscheint bei
[FIB]
der Status
„i.B.“
für in
Bear­beitung.
Die Verbuchung wird aus den folgenden Elementen
zusammengestellt:
•
Erlösklasse aus dem Kundenstamm
•
Erlöskennziffer aus Artikel / Artikelstamm
•
Steuerschlüssel aus Artikelstamm
•
Steuergruppe
•
Buchklasse aus Vorgang
•
Datum aus Vorgang
•
Typ Erlös oder Aufwand aus Vorgangsklasse
Findet der Mandantenserver — evtl. unter Ausnutzung
der DEFAULT Mechanismen — einen gültigen Eintrag aus
[EKZZ]
, so erfolgt der Eintrag in die FiBu.
Der Vorgang ist nun in der Auswahl-Box bei
[FIB]
mit JA gekennzeichnet. Findet der
Mandanten­ser­ver keinen gültigen Eintrag unter
[EKZZ]
, so schreibt er den Beleg in das
Fehler­pro­to­­koll. Der Status FiBu-Übertrag steht auf
NEIN.
Fehler-Handling nach dem Fibu-Übertrag
Je nach sachlicher Fehlerursache sind verschiedene
Maßnahmen denkbar:
Fehlende Einträge in
[EKZZ]
nachholen.
Richtige Erlösklasse, Erlöskennziffer oder
Steuerschlüssel im jeweiligen Stammpfleger eintragen.
Referenz-ERP verlassen (bis Startsymbol), erneut starten und
den FiBu-Über­trag wiederholen.

---

## Auswahllistenvariante Fibu Übertrag Umbuchungen und Produktion

Auswahllistenvariante Fibu Übertrag Umbuchungen und Produktion
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Umbuchungen und Produktion
Oder
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Fibu Übertrag Umbuchungen und Produktion
Oder
Direktsprung
[FIB]
In dieser Variante werden Produktions- und
Umbuchungs-Vorgänge dargestellt
Felder der Auswahlliste
Feld
Beschreibung
Belegnr.
Nummer des Vorgangs
Typ
Vorgangsklassenkürzel des
      Belegs
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
PeriodeFibu
Fibuperiode des Vorgangs
JahrFibu
Fibujahr des Vorgangs
Bereichsauswahl
Filter
Beschreibung
Belegnummer
Selektion der Belege mit Belegnummer
      (von/bis)
Datum
Selektion der Belege mit Belegdatum
      (von/bis)
Vorgangsklasse
Selektion der Belege mit
      Vorgangsklassen:
alle Umbuchungen:
Lagerumbuchungen
      (5110),
Artikelumbuchungen (5120),
Produktion
      (5220)
Lagerplatzumbuchungen (5100)
Lagerumbuchungen
      (5110)
Artikelumbuchungen (5120)
Produktion (5220)
Funktionen der Auswahlliste
Funktion
Beschreibung
Fibu-Übertrag
Die
      Funktion erstellt für jeden ausgewählten Vorgang einen Eintrag im
      Datenstrom für den Mandante
[...]


---

## FIBU – Merkmale

FIBU – Merkmale
Hier werden die erforderlichen Parameter zur
Behandlung des Kunden in der Finanzbuchhaltung gepflegt.
Verbuchungsmerkmale
Beschreibung
Forderungsgruppe
Die
Forderungsgruppe
, so
      wie sie in den Stammdaten hinterlegt wurde. In der ersten Zeile steht die
      Forderungsgruppe, wie sie allgemein für dieses Konto gültig ist. Sobald
      für dieses Konto Belege in endgültig abgeschlossen Perioden existieren ist
      diese Forderungsgruppe nicht mehr änderbar. Man muss dann in der
      Folgezeile eine neue Forderungsgruppe angeben. Dabei werden Jahr und
      Periode abgefragt, die angeben ab wann die neue Forderungsgruppe gültig
      ist.
Der
      Bestimmung der Forderungsgruppe eines Personenkontos hat mit der Funktion
      „getForGrupNummer“ zu geschehen. Diese Funktion hat als ersten Parameter
      die Kontonummer. Gibt man keinen weiteren Parameter an, wird die zum
      Tagesdatum gültige Forderungsgruppe geliefert. Der zweite und dritte
      Parameter ist optional. Es sind die Jahrnummer und Periode. Folgender
      Aufruf liefert die Forderungsgruppe, die in der Periode 1/2015 gültig
      ist:
Select getForGrupNummer(10000 , 2015 , 1
      )
Beim
      Ändern der Forderungsgruppe ist immer zu beachten, dass die diesem
      Personenkonto zugeordneten Werte vor dem Zeitpunkt auf den „alten“
      Forderungs-/Verbindlichkeitskonten bleiben. Es erfolgt keine automatische
      Umbuchung. Erst beim Jahreswechsel der Sachkonten werden die Umbuchungen
      auf den Forderungs- und Verbindlichkeitskonten durchgeführt. Dazu muss die
      letzte Normalperiode offen sein. Diese Mechanik kann mit dem
      Steuerungsparameter 968 („Forderungskonten umbuchen“) deaktiviert
      werden.
Erlösklasse
Es
      besteht die Möglichkeit, die Erlöse einer bestimmten Klasse von Kunden auf
      speziellen Erlöskonten zu buchen (z.B. Erlöse Inland auf 8100, Erlöse
      Ausland auf 8200). Hier ist die Erlösklasse einzutragen. I
[...]


---

## EPC-QR-CODE im Formularfuß

EPC-QR-CODE im Formularfuß
Allgemeines
Im Formularfuß (Bereich 902: Abschluss und Fuß letzte
Seite) von Standardformularen kann die Druckposition ‚EPC-QR-CODE‘ (Position 45)
eingerichtet werden, die aber nur bei Vorgängen der Vorgangsklasse 700
(Rechnung) beim Druck berücksichtigt wird.
Bei vorhandener EPC-QR-CODE-Lizenz wird an der
eingerichteten Stelle ein EPC-QR-CODE erzeugt, der durch ein
Onlinebanking-Programm oder eine Mobile-Banking-App decodiert werden kann, um
mit diesen Daten automatisch ein Online-Überweisungsformular auszufüllen.
Die enthaltenen Daten sind:
-
Empfängerbezeichnung der Überweisung
-
BIC und IBAN des Empfängerkontos
-
Überweisungsbetrag in EUR
-
Verwendungszweck
Im ausgelieferten Standard wird die
Empfängerbezeichnung dem Feld ‚Auftraggeber DTA‘ des Hausbankstamms
entnommen.
Auch die IBAN wird dem Hausbankstamm entnommen.
Der BIC wird aus dem Bankenstamm, der der Hausbank
zugeordnet ist entnommen.
Der Überweisungsbetrag ist der Rechnungsbetrag.
Als Verwendungszweck wird ein Text mit dem Aufbau
-
‚Rechnung‘
-
Rechnungsnummer
-
‚vom‘
-
Belegdatum
-
‚KuNr‘
-
Kundennummer
generiert.
Bei Vorhandensein mehrerer Hausbanken kann mit dem
Steuerparameter
Hausbanknummer für EPC-QRCODE (SPA1079)
durch Angabe der
Hausbanknummer die heranzuziehende Hausbank festgelegt werden. Ist der Wert des
Steuerparameters 0 oder mit der dort angegebenen Nummer keine (nicht gelöschte)
Hausbank gefunden, so wird die (nicht gelöschte) Hausbank mit der niedrigsten
Nummer herangezogen.
Einrichtungsdetails
Die
Einrichtung der Position
erfolgt durch Angabe von
Zeile und Spalte für die linke obere Ecke des QR-CODEs im Formularbereich
Bereich 902 für die Position ‚EPC-QR-CODE‘ (45) und die Angabe des
Namens der
Etikettendruck-Definition
( im Standard:
AMIC_EPC_QRCODE
)
in der Spalte
Text
.
Die Größe des QR-CODEs ergibt sich aus der dort
hinterlegten Report-Definition.
Grundsätzlich kann die Vorlage
AMIC_EPC_Q
[...]


---

## Geschäftsjahre / Buchungsperioden

Geschäftsjahre / Buchungsperioden
Hauptmenü
Administration
Geschäftsjahr / Perioden
Geschäftsjahre/-perioden
oder Direktsprung
[JAHR]
Felder der Geschäftsjahre / Buchungsperioden
Felder
Beschreibung
Jahr
Zeigt das Jahr an, in für das das
      Geschäftsjahr erstellt wurde.
Bezeichnung
Zeigt die Bezeichnung an, welche bei
      der Erstellung des Geschäftsjahres gesetzt wurde.
Begin
Gibt
      das Datum des Beginns des Geschäftsjahres an.
Ende
Gibt
      das Datum des Endes des Geschäftsjahres an.
Status
Zeigt den aktuellen Buchungsstatus
      an.
Journalkreis
Gibt
      den festgelegten Nummernkreis für das Geschäftsjahr an
Perioden
Zeigt die Perioden, welche in dem
      Geschäftsjahr hinterlegt wurden.
Suchmöglichkeiten der Geschäftsjahre /
Buchungsperioden
Felder
Beschreibung
Jahr
Von…Bis....
Funktionen der Geschäftsjahre /
Buchungsperioden
Felder
Beschreibung
Bearbeiten(F5), Ansicht(F6),
      Löschen(F7), Neu(F8)
Perioden
      Abstimmprotokoll
Öffnet das Perioden
      Abstimmprotokoll

---

## Häufig vorkommende Abweichungen / mögliche Ursachen

Häufig vorkommende Abweichungen / mögliche Ursachen
•
Warenbelege sind noch nicht an die FIBU übertragen
Es kommt leider häufiger
vor, dass in den üblichen Auswahllisten die Bereichseingrenzungen nicht korrekt
eingestellt werden. Das kann dann dazu führen, dass einige Belege beim
FIBU-Übertrag übersehen wurden.
Mit
Konsistenzprüfungen
kann man sich einen
Überblick über sämtliche noch nicht in der FIBU vorhandenen Belege verschaffen
(Funktion:
Belege ohne
Fibuübertrag
).
•
Unterschiedliche Periodenführung
[WABST]
ist eine streng nach Buchungsperioden
abgegrenzte Auswertung. In Referenz-ERP gibt es mehrere SPA-Einstellungen bezüglich
der Periodenzuordnung. Sie sollten auf jeden Fall darauf achten, dass Fibu- und
Warenperioden gleichlaufen. Beachten Sie bitte, dass es bei der Erstellung von
Sammelrechnungen auch zu unterschiedlichen Perioden der einzelnen
Warenpositionen kommen kann, wenn der SPA
Rechnungstrennung durch Periode
auf
nein
steht (Empfehlung: auf
neu
stellen, das heißt alle
Warenpositionen erhalten die Periode des neu erstellten Beleges!).
Die Konsistenz-Funktion
Belege mit abweichenden Perioden
erstellt hierfür eine Übersicht. Sollten Periodenunstimmigkeiten auftreten, so
können Sie mit der WAREO-Funktion,
Perioden
angleichen
eine Periodenstimmigkeit erzeugen. Dabei wird folgendermaßen
vorgegangen:
1.
Belege, die schon an die FIBU übertragen wurden, werden periodenmäßig an die
FIBU angeglichen (d.h. die FIBU-Periode wird nicht verändert, jedoch die
Periodenzugehörigkeit in der Ware!).
2.
Unstimmigkeiten der Perioden der Warenpositionen innerhalb eines Beleges werden
durch Anpassung an die Periode des Gesamtbeleges aufgelöst.
ACHTUNG:
Nach diesem
Lauf ist auf jeden Fall auch wieder eine Gesamtreorganisation fällig, da die
internen Periodenstatistiken angepasst werden müssen.
•
Fehlerhafte Einträge im Mandantenserver
Im Mandantenserver können
sich noch Einträge befinden, die von Branchen-ERP-Mitarbeitern zwischenzeitlich
deaktiviert wurden (DS
[...]


---

## Bezahlterminal (Metis)

Bezahlterminal (Metis)
Kasse
Erfassung Abschluss
EC-Karte
Dieses Addin ist für die Ansteuerung eines
Bezahlterminals mit ZVT700-Standard-Schnittstelle  zuständig.
Ob in der Kasse oder an anderen Stellen werden
      Bezahlvorgänge mit einem Bezahlterminal benötigt. Dieses AddIn steuert das
      Bezahlterminal an und wickelt eine Kartenzahlung ab.
Dabei benötigt das Terminal eine Verbindung zum
      Bankenrechenzentrum, die je nach Terminal und Konfiguration bei Bedarf
      über eine Telefonleitung oder per Internet hergestellt werden kann. Diese
      Kommunikation ist Teil der Konfiguration des Terminals und liegt außerhalb
      der Zuständigkeit von Referenz-ERP.
Die Aufgabe dieses AddIns ist es, dem Terminal die
Anforderung eines definierten Betrages zwischen 0,01 und 9999,99 € zu übergeben
und dafür zu sorgen, dass der Bediener zur Zahlung des Betrages mit Karte
aufgefordert wird. Am Ende der Zahlung gibt das AddIn die Information aus, ob
die Bezahlung erfolgreich war oder nicht.
Hinweise zu Fragen:
Eine gute Webseite für Fragen rund um den
Zahlungsverkehr findet sich unter
http://www.zahlungsverkehrsfragen.de
(Stand November 2012)

---

## Kassensturz und Kassenabschluss

Kassensturz und Kassenabschluss
Hauptmenü
Barvorgäng
Kasseneröffnung/Abschluss
Relevante SPA-Einstellungen
Aut. Buchung Finanzvorgänge in Fibu
: Falls
nein, so erfolgen überhaupt keine Übergaben an Fibu. Die Nein-Einstellung ist
normalerweise nur gedacht für Anschluss Fremdfibu.
Aut. Abschöpfung Unterkasse
an Hauptkasse, im
Folgenden genannt SPA Abschöpfung: Unterkasse kann in diesem Fall Bargeldbestand
im Zuge des Kassenabschluss an die Hauptkasse übergeben. Übergabe der
Zahlungsmittel je nach SPA Zami
Umbuchung Zahlungsmittel auf Konten
: Umbuchung
Zahlungsmittel auf die in den Kasseneinstellungen vorgesehenen Konten. Umbuchung
des Bargeldes auf das Bargeldkonto, falls eingerichtet.
Unterkasse mit Abschöpfung ohne Zählung
abschließen
: Im Standardfall (ja) wird an der Unterkasse keine Zählung
durchgeführt, es wird also immer das Kassensoll an die Hauptkasse transferiert
und nur dort werden Kassendifferenzen festgestellt. Per SPA Freischaltung kann
man auch eine Zählung an der Unterkasse aktivieren.
Kasseneinstellungen „Konten“:
Bargeld
: Auf dieses Konto wird der
Bargeldbestand bei eingeschaltetem SPA Zami umgebucht. Auf das Bargeldkonto
werden alle Barzahlungssummen ohne Berücksichtigung von BV-Stornobelegen der
Sitzung unterschieden nach Bargeldeingang und Bargeldausgang umgebucht. Dadurch
Fibu-seitig automatische Entlastung des Kassenkontos beim Kassenabschluss.
Kassenseitig ist durch diese Umbuchung keine Entnahme des Bargeldes
verbunden!
Umbuchungskonten für unbare Zahlungsmittel
im
Rahmen des Kassenabschluss bei Verwendung SPA Zami (Scheck, Gutschein, EC Cash,
Bankeinzug).
Differenzkonto
: Umbuchung einer evtl.
Zähldifferenz beim Kassenabschluss.
Stornokonto
: Separate Umbuchung von
Stornobelegen saldiert je Sitzung auf dieses Konto. Nur im Zusammenhang mit
Bargeldumbuchung zu behandeln: Wenn das Bargeldkonto nicht oder identisch dem
Kassenkonto eingerichtet ist, erfolgt keine Stornoumbuchung. Wenn ein
Bargeldkonto eingerichtet wurde,
[...]


---

## Setup Erstinbetriebnahme Schritt-für-Schritt-Anleitung

Setup Erstinbetriebnahme
Schritt-für-Schritt-Anleitung
Ziel der Kassensicherungsverordnung ist, nachträgliche
Manipulationen an Umsatzdaten herausfinden zu können. Die Überprüfung erfolgt in
einem exportierbaren Journal, das durch das Finanzamt mit einer Prüfsoftware auf
Veränderungen und Lücken geprüft werden kann.
Jede Kassenbuchung wird mit einer elektronischen
Signatur versehen. Die Signatur funktioniert nach dem Blockchain Prinzip. Bei
der Generierung der Signatur werden nicht nur Bestandteile des aktuellen
Verkaufsbelegs herangezogen, sondern auch die Signatur des vorherigen Belegs.
Weiterhin ist die externe, durch die Kassensoftware nicht manipulierbare,
Sicherheitseinrichtung in die Signaturerstellung eingebunden. Die Signatur wird
verschlüsselt im Journal gespeichert.
Wenn Transaktionen im Journal manipuliert werden, ist
die Kette der Signaturen nicht mehr konsistent. Es kann mit einer Prüfsoftware
auf Knopfdruck herausgefunden werden, an welcher Stelle die Manipulation
stattgefunden hat.

---

## TSE-Austausch Schritte 1 bis 4

TSE-Austausch Schritte 1 bis 4
TSE-Austausch Schritt 1 Kassenabschluss durchführen
Hauptmenü
Barvorgänge
Stammdaten
Kasseneröffnung / Kassenabschluss
Vor jeder Installation der neuen TSE-Version bei einem
Update müssen die Kassenabschlüsse aller betreffenden Kassen durchgeführt
werden.
Um einen Kassenabschluss der betreffenden Kassen
durchzuführen, wie folgt vorgehen:
1.
Zu Barvorgänge
Stammdaten
Kasseneröffnung / Kassenabschluss
navigieren.
2.
Betreffende Kasse auswählen.
3.
Auf
Abschluss
klicken oder
F8
drücken.
TSE-Austausch Schritt 2
Daten sichern per Export
Hauptmenü
Barvorgänge
Kassensicherungsverordnung
Direktsprung
[KSVO]
Hinweis!
Die Datensicherung ist wichtig für Ihre
Betriebsprüfung und die erstellten Dateien müssen gut aufbewahrt werden.
Der Betriebsprüfer könnte bei der Prüfung nach den
Dateien fragen.
Weitere Informationen zum DSFinV-K Export finden Sie
unter:
DSFinVK_Export
DSFinV-K Export erzeugen
1.
Zum Direktsprung
[KSVO]
navigieren.
2.
Mit der Funktion
Export erzeugen
die Dateien exportieren.
3.
Dateien speichern/ablegen.
TAR-Export erzeugen
1.
Zum Direktsprung
[KSVO]
navigieren.
2.
Mit der Funktion
Export TAR
Zeitraum
mit Datumseingrenzung
den Export erstellen.
3.
Dateien speichern/ablegen.
ODER
(
ohne Datumseingrenzung):
1.
Zum Direktsprung
[TSE]
navigieren.
2.
Datensatz markieren.
3.
Dateien ansehen
(F6)
.
4.
Mit der Funktion
Export TAR
die
Dateien exportieren.
A.Eins beenden
1.
A.Eins Client beenden.
TSE-Austausch Schritt 3 Neue Referenz-ERP Lizenz
(ahoi2.xml) einspielen
Damit die Lizenz zum TSE-Stick passt, muss zunächst
die aktuelle Referenz-ERP-Lizenz eingespielt werden.
Dazu wie folgt vorgehen:
1.
Im Ordner
Aeins\Config
die aktive
ahoi2.xml
umbenennen z. B. in
ahoi2_OLD
So ist sichergestellt, dass
sie im Notfall reaktiviert werden kann.
2.
Lizenzdatei aus der E-Mail unter den genau folgender gekürzten Bezeichnung:
ahoi2.xml
auf allen Servern und
Clients ins Verzeichnis
Aeins\Config
speichern.
[...]


---

## TSE-Setup Schritt 3 Abschluss

TSE-Setup Schritt 3 Abschluss
Schritt 3.1: Der Kasse eine TSE zuweisen
Um die TSE nun in Betrieb zu nehmen, müssen die Kassen
die TSE hinzufügen.
Zu Hauptmenü
Barvorgänge
Stammdaten
Kassenverwaltung navigieren.
1.
In der Auswahlliste der Kassen die gewünschte Kasse auswählen.
2.
Kasse mit
F5
bearbeiten.
3.
Im Feld TSE-ID mit
F3
die gewünschte
TSE auswählen.
4.
Einstellungen speichern.
Schritt 3.2: Anmerkung
Die Kasse kann jetzt wie gewohnt eröffnet werden.
Hinweis:
Beachten Sie, dass wir bis jetzt keine parallele
Nutzung, von mehreren Clients auf einer TSE, supporten.
Beispiel des Aufbaus
Auf diesem Bild sehen Sie einen Beispielaufbau der TSE
am Arbeitsplatz:

---

## TSE-Austausch Schritt-für-Schritt-Anleitung

TSE-Austausch Schritt-für-Schritt-Anleitung
Ziel der Kassensicherungsverordnung ist, nachträgliche
Manipulationen an Umsatzdaten herausfinden zu können. Die Überprüfung erfolgt in
einem exportierbaren Journal, das durch das Finanzamt mit einer Prüfsoftware auf
Veränderungen und Lücken geprüft werden kann.
Jede Kassenbuchung wird mit einer elektronischen
Signatur versehen. Die Signatur funktioniert nach dem Blockchain Prinzip.
Bei der Generierung der Signatur werden nicht nur
Bestandteile des aktuellen Verkaufsbelegs herangezogen, sondern auch die
Signatur des vorherigen Belegs.
Weiterhin ist die externe, durch die Kassensoftware
nicht manipulierbare, Sicherheitseinrichtung in die Signaturerstellung
eingebunden.
Die Signatur wird verschlüsselt im Journal
gespeichert.
Wenn Transaktionen im Journal manipuliert werden, ist
die Kette der Signaturen nicht mehr konsistent. Es kann mit einer Prüfsoftware
auf Knopfdruck herausgefunden werden, an welcher Stelle die Manipulation
stattgefunden hat.
Voraussetzungen:
•
Der neue TSE-Stick liegt vor.
•
Die Lizenzdatei liegt vor.
Tipp!
Um zu jederzeit sicherzustellen, dass der Betrieb
gewährleistet ist, empfiehlt es sich mehr als einen TSE-Stick vorrätig zu
haben.
Wenn es zu Ausfällen kommen sollte, können Sie so
schnell agieren. Dies schafft insbesondere beim Betrieb von mehreren Kassen
Sicherheit.
Hinweis!
Voraussetzung für die Installation über das Netzwerk
ist, dass der TSE-Stick von Ihrem IT-Betreuer im Netzwerk freigegeben wird sowie
einem Laufwerk zugeordnet wird.
Der Tausch besteht aus den
folgenden Schritten:
è
Schritt 1
Kassenabschluss durchführen
.
è
Schritt 2
Daten sichern per Export
è
Schritt 3
Neue Referenz-ERP Lizenz (ahoi2.xml)
einspielen
è
Schritt 4
TSE-Sticks tauschen und
Kassenarbeitsplatz Referenz-ERP® starten
è
Schritt 5
TSE aktivieren
.
è
Schritt 6
TSE der Kasse zuweisen
.
è
Schritt 7
Kasse eröffnen
.

---

## Kontoblätter erstellen

Kontoblätter erstellen
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Funktion
Kontoblätter erstellen
F9
Direktsprung
[KOD]
Innerhalb des Eingabebildschirms werden die
Eingrenzungen vorgenommen, mit deren Hilfe die Kontoblätter erstellt werden.
Beschreibung
Kontoart
Sachkonto, Personenkonto, Debitoren,
      Kreditoren oder Kontokorrent
bis
      Periode/Jahr
Eingabe Periode Jahr bis zu der/den
      Buchungen berücksichtigt werden
bis
      Belegdatum
Eingabe des Datums bis zu den
      Buchungen berücksichtigt werden Bei der Erstellung von Kontoblättern für
      Forderungs-/Verbindlichkeitskonten für die Methode „Saldo Stichtag“ wird
      das Belegdatum nicht berücksichtig.
Bemerkung
Eingabe Wahlfreier Text
Kontobereich
      von ... bis ...
Eingrenzung der Konten
Ist als Kontoart Personenkonto bzw. Debitor/Kreditor
oder Kontokorrent angewählt, so kann man auch die auf der Abbildung
deaktivierten Felder zur Eingrenzung verwenden.
Wird dieser Vorgang mit
F9
gestartet werden
alle noch in keinem Kontoblatt enthaltenen Belege zusammengesucht. Vor dem
Erstellen der Kontenblätter wird noch geprüft, ob noch ungebuchte Belege in
diesen Bereichen vorkommen. Außerdem wird pro Konto geprüft, ob für das Konto
bereits ein Kontoblatt für eine spätere Periode existiert. Nach dem Durchlauf
wird dann die Meldung „Kontoblatt für Konto ….. nicht erstellt, da bereits
Kontoauszüge einer späteren Periode existieren!“
Will man Kontoblätter für
Forderungs-/Verbindlichkeitskonten bei Verwendung der Methode „Saldo Stichtag“
erstellen, so geht dies nur, wenn die Perioden bereits abgeschlossen
(Direktsprung PERAF) wurden.
ACHTUNG:
Sollte das Erstellen der
Kontoblätter abgebrochen werden, so müssen die teilweise bearbeiteten Belege
wieder freigeschaltet werden. Dazu muss im
Fibureorganisator
(Direktsprung FIREO) der Funktion „
Reorg. Fragmente
“ angewählt
werden.

---

## Kostenstellen / Statistik / Abteilung

Kostenstellen / Statistik / Abteilung
Dem Artikel kann hier ein Statistik-Schlüssel, die
Buchungsklasse, eine Abteilungsgruppe sowie eine Kostenstellen-Gruppe,
Kostenträger-Gruppe und Kostenobjekt-Gruppe zugeordnet werden.
Der Statistik-Schlüssel dient Auswertungszwecken. Z.Z.
existiert keine Standard­aus­wertung, so dass ggf. eine private Variante
zu gestalten ist.
In Zusammenhang mit den Erlöskennziffern (die dem
Artikel zugeordnet wurde) bewirkt die Buchungsklasse bei der
Erlöskennziffernzuordnung
[EKZZ]
folgende Variations­mög­lichkeiten: Bei gleicher Erlöskennziffer werden
die Erlöse in Abhängigkeit der Buchungsklasse unterschiedlichen Erlöskonten
zugeordnet.
Bei Eintragung einer Abteilungsnummer wird dieser
Artikel nur dieser zugeordnet. Vor Einrichtung solcher Varianten muss wegen der
Komplexität mit dem System­betreuer Rücksprache gehalten werden.
Die Kostenstellen-Gruppe enthält je eine
Kostenstellennummer für den Einkauf und eine für den Verkauf und steht hier nur
bei vorhandener Kostenstellen-Lizenz als pflegbares Feld zur Verfügung.
Die Kostenträger-Gruppe enthält je eine
Kostenträgernummer für den Einkauf und eine für den Verkauf und steht hier nur
bei eingeschaltetem Steuerparameter
Kostenträgerrechnung angeschlossen
als pflegbares Feld zur Verfügung.
Die Kostenobjekt-Gruppe enthält je eine
Kostenobjektnummer für den Einkauf und eine für den Verkauf und steht hier nur
bei vorhandener Kostenobjekt-Lizenz als pflegbares Feld zur Verfügung.

---

## Konzepte in der Lagerverwaltung 2.0

Konzepte in der Lagerverwaltung 2.0
In der Lagerverwaltung 2.0 werden Daten zunächst
aufgenommen und mit Standard-Routinen des Vorgangsimports gebucht. Damit lässt
sich die Erfassungsreihenfolge und ggf. der Umfang der erfassten Daten erweitern
und ändern, während die Buchungsmechanismen einem Referenz-ERP-Standard entsprechen,
der ausgiebig getestet sind und von der Kernentwicklung supportet werden können.
Das minimiert den Aufwand der Individualentwicklung
auf ein Mindestmaß.

---

## Lagerumbuchung mit Teildispo

Lagerumbuchung mit Teildispo
Eine klassische Lagerumbuchung in Referenz-ERP ist ein „Ganz
oder gar nicht“-Prozess. Das bedeutet, dass die teilweise Ausführung einer
Planung damit nicht möglich ist.
Um dennoch die Lagerumbuchung mit Teildisposition im
LVS zu vollziehen, wendet man die folgende Strategie an:
Einrichtung
1.
Jedes Lager bekommt einen Kontokorrentkunden, der als steuerfreier Kunde
eingerichtet sein muss.
2.
Im Lagerstamm [LGS] wird dieser Kunde im jeweiligen Lager hinterlegt.
3.
In der Vorgangsunterklasse der Bestellung wird in Kontrollmakro folgender Code
eingetragen:
//INCLUDEMAKRO
AMIC_LVS_Lagerumbuchung
public
void
Vorgang_Nach_Speichern(IVorgang vorg,
int
modus)
{
int
v_id =
0;
vorg.GetValue(VORGANG.ID_V_ID,
out
v_id);
int
techBeleg =
0;
vorg.GetValue(VORGANG.ID_TECHNISCHERBESTAND,
out
techBeleg);
if
(techBeleg
== 1)
{
return
;
}
int
cnt =
D.GetExecuteScalar(0,
@"select count(*)
from amic_v_vorgaenge vs
join lagerstamm lgs on lgs.KundIdGegenBeleg = kundidzuord
where vs.v_id = ?"
, v_id);
if
(cnt >
0)
{
AMIC_LVS_Lagerumbuchung.AMIC_LVS_LGU
lgu =
new
AMIC_LVS_Lagerumbuchung.AMIC_LVS_LGU();
lgu.Gegenbeleg_erstellen(v_id,
10);
}
}
Ausführung
1.
Es wird eine Bestellung erfasst mit dem Kunden des Quell-Lagers und den Artikeln
des Ziel-Lagers. Dieser beleg bekommt das Kennzeichen technischer Bestand und
wird alle Preise aus dem Bewertungspreis des Quell-Artikels vorschlagen.
2.
Beim Speichern wird über das Kontrollmakro ein Aufruf der Lagerumbuchung aus
„AMIC_LVS_Lagerumbuchung“ gemacht. Es entsteht ein Auftrag für den Kunden des
Ziel-Lagers mit Artikeln des Quell-Lagers.
3.
Dieser Auftrag kann nun mittels Ladeschein teilweise ausgeliefert werden.
4.
Ladeschein wird wie alle anderen Aufträge abgearbeitet. Erst beim Abschluss wird
statt der Löschung der Ladeträger eine Artikelumbuchung im LVS vorgenommen.
5.
Es entstehen ein Lieferschein und ein Eingangslieferschein.

---

## Vorgangsimport (LVS)

Vorgangsimport (LVS)
Hauptmenü
Systempflege
Mandantenserver
Mandantenserverprozesse
oder Direktsprung
[MSP]
Alle LVS-Buchungen werden als Vorgangsimport mit der
Vorgangsklasse 5150 geschrieben. Diese können je nach Bedarf in mehr oder
weniger kurzen aber regelmäßigen Abständen gebucht werden.
Regelmäßige Buchungen können über
Mandantenserverprozesse
erreicht werden.
Mandantenserver LVS Buchungsprozess
Der Mandantenserver kann LVS-Buchungen in kurzen
Zeitabständen für alle LVS-Buchungen vornehmen. Dazu ist es notwendig, ein Makro
2.0 auszuführen, das alle LVS-Vorgangsimporte im Status 2 abarbeitet.
Nachteil des synchronen Mandantenserverprozesses:
Läuft eine andere Buchung des Mandantenservers längere Zeit, so werden erst
danach die LVS-Buchungssätze abgearbeitet.
Asynchroner Mandantenserverprozess
Der Asynchrone Mandantenserverprozess (Typ 2 –
Asynchron (Managed)) prüft in regelmäßigen Abständen, ob ein asynchroner Prozess
läuft, der LVS-Buchungen vollzieht. Dazu ist im Controlstring
Folgendes einzugeben:
VIMP_Automat 5150 -1 1
Nun wird im Sekunden-Rhythmus nach zu verarbeitenden
Buchungssätzen des Typs LVS geguckt und diese werden abgearbeitet.

---

## Synchron oder Asynchron

Synchron oder Asynchron
•
Synchron
Wenn der Datenbankserver
selbst E-Mails versenden darf, muss der Steuerparameter 1019 – Mailversand per
auf „Datenbank“ stehen. Die E-Mails gehen dann in dem Moment zum Mailserver,
wenn die Anforderung dazu erstellt wird.
•
Asynchron mit Dienst
Nicht immer ist der
Datenbankserver mit dem Internet verbunden und kann somit synchron selbst
E-Mails versenden.
In diesem Fall ist der
Steuerparameter 1019 – Mailversand per auf „Dienst/Exe“ einzustellen. Ein Dienst
muss nun auf einem Rechner installiert werden, der Zugang zum Internet hat und
zugleich den Datenbankserver erreichen kann. Dieser Dienst startet aus dem
Referenz-ERP-Unterverzeichnis „Bin64“ die Anwendung „Referenz-ERP.MailSvc.exe“ und übergibt
folgende Parameter:
•
Connectionstring z.B. eng=myengine;dbn=mydbname:links=tcpip;
•
Anzahl an Minuten, die zwischen zwei Sendezyklen liegen (default ist 5
min)
•
Asynchron mit Exe
Ist die Einrichtung eines
Dienstes nicht möglich, oder soll testweise ein Mailversand mit Hilfe einer
Exe-Datei versendet werden, so kann das Programm „Referenz-ERP.Mailer.exe“ aus dem
Referenz-ERP-Unterverzeichnis „Bin64“ aufgerufen werden. Die Parameter sind dabei die
gleichen wie beim Dienst.
•
Connectionstring z.B. eng=myengine;dbn=mydbname:links=tcpip;
•
Anzahl an Minuten, die zwischen zwei Sendezyklen liegen (default ist 5
min)

---

## Skonto in der Marktkasse

Skonto in der Marktkasse
Sie haben die Möglichkeit, wenn die entsprechenden
Felder und Funktionen eingerichtet sind, einen Skontosatz zu erfassen. Dies kann
frühestens nach der Erfassung der ersten Warenposition und spätestens vor
vollständiger Zahlung des Beleges geschehen.
Der Skontobetrag wird dann von der Belegsumme
abgezogen und bei der Zahlung berücksichtigt.

---

## Bezahlung per EC-Lastschrift

Bezahlung per EC-Lastschrift
Ein Bezahlterminal verlangt in der Regel eine PIN bei
der Authorisierung der Zahlung. Dies kann dennoch im Einzelfall je nach Vertrag
mit dem Anbieter variieren. Diese PIN-Anforderung ist in Referenz-ERP als Standard im
Ablauf des Bezahlvorgangs mit Bezahlterminal vorgesehen und wird wegen der
Sicherheit gegen Zahlungsausfall auch empfohlen, wenn auch die Gebühren i.d.R.
wenige Cents pro Zahlung höher sind als beim Lastschriftverfahren.
Im Einzelfall kann nun von diesem PIN-Verfahren
bewusst abgewichen werden, indem in der Marktkasse die Funktion EC-Lastschrift
zur Zahlung aufgerufen wird. In diesem Fall druckt das EC-Terminal einen Beleg
zur Unterschrift. In den Kassenjournalen ist der Unterschied zwischen EC-PIN und
EC-Lastschrift nicht sichtbar!
Eine Kombination der Auszahlung (EC-Plus) mit
Lastschrift ist nicht möglich.

---

## Nachhaltige Bestände

Nachhaltige Bestände
Unabhängig von der Tatsache, dass die Nachhaltigkeit
in Form einer Massebilanz nachgewiesen wird und somit keine Auszeichnung
nachhaltiger Ware erforderlich ist und damit auch keine Führung von Beständen
vorgegeben ist, taucht dennoch in der praktischen Abwicklung die Frage auf,
wieviel nachhaltige Ware noch zur Verfügung steht. Weil man nun während eines
Verkaufsgesprächs nicht schnell mal eine Massebilanz erstellen kann, haben wir
uns entschlossen, innerhalb der Bestandsübersicht in ARB nachhaltige Bewegungen
saldiert anzuzeigen.

---

## Formate

Formate
Die Nachhaltigkeit hat einige spezielle AF – Formate,
die gepflegt werden müssen.
Nachhaltigkeitsstatus (Format
AF_NACHHSTAT)
Auf Anforderung wurde das Nachhaltigkeitskennzeichen
am Kunden nicht als ja/nein-Kennung eingebaut. Stattdessen ist untenstehendes
Anwenderformat einzurichten, das an folgende feste Bedeutung gebunden ist.
Wert
Beschreibung
0
undefiniert
1-9
nicht nachhaltig
>=10
nachhaltig
Zertifikatstyp (Format  AF_NAHA_ZERT)
Relevant sind hier die Typen 4 und 5, deren numerische
Repräsentation als verbindlich anzusehen ist im Hinblick auf die
Standard-Zulieferfunktionen für die Nachhaltigkeitsinformation.
Wert
Beschreibung
4
Alle
      Warenlieferanten, die eine Selbsterklärung abgegeben haben oder selbst
      zertifiziert sind.
5
Das
      eigene Zertifikat, das bei Warenausgängen auszuweisen ist. Der Typ 5 kann
      systemweit nur einmal vorkommen bei einem Konto, das als Platzhalter für
      die eigene Firma steht.
Alle
      anderen
Werden für die Nachhaltigkeit nicht
      gebraucht.
Die Nummernangaben im Kommentarfeld
müssen
mit
angegeben werden!
Zertifikate vom Typ 4 gelten für den Einkauf und
müssen für den im Beleg angegebenen Kunden auf der Kundenstammmaske auf dem
Tabreiter Zertifikate als Zertifikat eingerichtet sein.
Das Zertifikat mit dem Typ 5 wird nur in dem
Systemkunden eingetragen. Diesen findet man heraus oder richtet diesen ein auf
der Mandantenstammmaske unter dem Direktsprung [MND] im Feld
Systemkundennnummer. Die Zertifikateinrichtungen für den Systemkunden regeln den
gesamten Verkauf und Belege mit den Vorgangsklassen 5100, 5110, 5120, 5200, 5210
und 5220.
Zertifizierungsmethode (Format
AF_ZERTMETH)
Angegeben werden die Zertifizierungsinstitutionen.
(z.B. ISCC, REDcert, Selbsterklärung)
Kategorie des Zertifikats (Format
AF_ZERTKATEG)
Dieses Format dient der Kategorie des Zertifikats,
aktuell wird die Kategorie nur zur Auswertung in der
Bewegungsübersicht
verwendet.

---

## Vorgänge Ware & Warenstatistiken löschen (einschl. Kassenbewegungsdaten)

Vorgänge Ware & Warenstatistiken löschen (einschl.
Kassenbewegungsdaten)
Es werden die Daten in folgenden Tabellen
gelöscht:
V_PosiUebertrag
V_PosiRohQualiZw
TourStation
WLZ_TempFeuProt
FAKtoWLZ_Report
WLZ_V_Addon
V_PosiGrZuAbWaeh
FAKtoWLZExport
WLZ_verify
VorgStornoProto
V_PosiWareGefahr
Vorganguebergabe
VorgangMaskeDaten
Reklam
ArchivWBAuftrag
ArchivBelegAuftrag
ImportVorgStamm
VorgReservierung
VorgangUngebu
VorgangUngedru
VorgangUnerled
VorgGlobalZuab
V_Markier
VorgangDropProt
KontraktSoftLock
V_PosiArtiAuspr
ArtiAusPraeg
V_PosiArtiText
V_PosiBauBeginn
V_PosiBauEnde
V_PosiBaustein
V_PosiBaustelle
V_PosiBeginn
V_PosiDispo
V_PosiEnde
V_PosiGebDispo
V_PosiGebQuDispo
V_PosiGebinde
V_PosiPreisGebindeFaktoren
V_PosiGefaGut
V_PosiGrupAlter
V_PosiGrupBegin
V_PosiGrupEnde
V_PosiGrZuAb
V_PosiGrZuAbSt
V_PosiGrZuAbWaeh
V_PosiKontrakt
V_PosiLeerZeile
V_PosiPartie
V_PosiKlammer
V_PosiPartieNachtrag
V_PosiQuellDispo
V_PosiRohKosten
V_PosiRohLiefer
V_PosiRohLiefWS
V_PosiRohQuali
V_PosiRohQualiZw
V_PosiRohSortier
V_PosiRohSortWS
V_PosiStLiKomp
V_PosiStListe
V_PosiText
v_positextblob
V_Position
V_PosiUmbuBeginn
V_PosiUmbuEnde
V_PosiUebertrag
V_PosiUV_Ansch
V_PosiUV_Beginn
V_PosiUV_Ende
V_PosiUV_Kunde
V_PosiWaehrung
V_PosiWare
V_PosiWareRes
V_PosiZ_Waeh
V_PosiFolgeArtikel
V_PosiZ_Zuab
V_PosiZw_Summe
V_RohWare
V_RohWAreAbsch
RohWareHauptsatz_Waage
RohWareZusatzQualitaet_Waage
RohWareZusatzWare_Waage
V_RohwareNachVerg
V_RohwareNachVText
vorgfibulink
fibuvorgposwabew
V_Waehrung
V_ZahlBeding
V_KassenInfo
V_ProdVorgang
VorgAktivStatus
Vorgangaddon
VorgangStamm
VorgGelangensBest
Vorgbemerkung
VorgFibuProto
VorgInkassoBeleg
VorgStammUmbuch
VorgStapel
VorgStapelPosit
VorgSteuer
v_vieraugenprinzip
stapel_content
KontraktDispoVorgang
SaatgutSaatentnahme
MaschinenTagebuchPosition
Rohware_Qual_Nachtrag
VorgText (
where
isnull(v_id,0) != 0)
// Datensätze in der Relation Vorgtext mit
Verknüpfungen zu Textbausteinen (bemerkstamm) nicht mitlöschen
VorgTransAuftrag
VorgVersAdresse
BemerkPositio
[...]


---

## Partieumbuchung

Partieumbuchung
Hauptmenü
Partieverwaltung
Partie-Stammdaten
Partiegruppen
oder Direktsprung
[PAR]
Allgemein
In der Variante „Partiebestand Details“ kann die
Partieumbuchung durchgeführt werden. Dabei wird eine Partie in der Auswahlliste
ausgewählt und mit der Funktion „
Partie
Umbuchung
“ öffnet sich dann die Maske für die Partieumbuchung.
Maskenfelder
Die meisten Maskenfelder zeigen nur die
Partieinformationen der Original Partie an.
Folgende Felder sind veränderbar
:
Maskenfelder
Bedeutung
Partiebezeichnung
In
      diesem Feld wird die neue Partiebezeichnung eingetragen. Wird das Feld
      nicht geändert und er Einrichterparameter „“ steht auf „Nein“, so kann
      keine neue Partie mit der gleichen Bezeichnung angelegt
      werden.
Menge
In
      das Feld wird die Menge eingetragen, die Umgebucht werden
      soll.
Ablauf
Neue Partie mit gleicher Partiebezeichnung
Um eine neue Partie mit gleicher Bezeichnung
anzulegen, muss nur die Menge in das Mengenfeld Eingetragen werden. Es darauf zu
achten, dass der Einrichterparameter „“ auf „Ja“ steht.
Neue Partie anlegen mit ungleicher
Partiebezeichnung
Um eine Partie mit neuer Partiebezeichnung anzulegen,
wird einfach eine neue Partiebezeichnung eingetragen.
Folgende Felder werden übernommen
.
Der Partiematchcode, die Belegreferenz, der
Gültigkeitszeitraum und die Mengeneinheitsnummer werden mit in die neue Partie
übernommen. Des Weiteren wird der das PartieStammAddon mit kopiert.
Als erstes wird eine neue Partie angelegt mit den
Eingegebenen und den vorgegebenen Parametern. Danach wird eine Artikelumbuchung
erstellt.
Es ist aber auch Möglich eine eigene
Partieumbuchung(Artikelumbuchung) im Makro zu Implementieren. Dem Makro werden
drei Parameter übergeben.
1.
Die Vorgangsunterklasse
2.
Die Partieid der neuen Partie
3.
Die Partienummer der neuen Partie
Addon
Um AIS auf der Maske anzuzeigen gibt es zwei Felder
für die Partieid auf der Maske
1.
PartieIDORIG
2.
n.PartieId$
Makrobeispi
[...]


---

## Partieinformation

Partieinformation
Hauptmenü
Partieverwaltung
Chargen / Partien
Partie-Stammdaten
oder Direktsprung
[PAR]
Die Funktion
Partieinformation
F10
wird grundsätzlich individuell den
Anforderungen entsprechend angepasst.

---

## Partie Artikel Umbuchung(EPA uh_par_aru_um

Partie Artikel Umbuchung(EPA uh_par_aru_um
Bezeichnung
Standardwert
Erklärung
Unterklasse für die
      Partieumbuchung
0
Hier
      wird die Unterklasse für die Partieumbuchung eingetragen.
Makro für eine private
      Partieumbuchung.
leer
Hier
      kann ein Makro hinterlegt werden, in dem eine private Partieumbuchung
      durchgeführt wird.
Das
      Makro hat zwei Parameter
1.
      Unterklasse
2.   PartieId
      (Neu)
Darf
      eine Partiebezeichnung mehrmals vorkommen.
Nein
Wenn
      Partiebezeichnung mehr als einmal vorkommen dürfen kann dieser Schalter
      auf Ja gesetzt werden.

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

## Qualitätsübersicht

Qualitätsübersicht
Hauptmenü
Nebenbuchhaltungen
Siloverwaltung
Silo
Direktsprung
[SILO]
In der Variante „Qualitätsübersicht“ können die
Qualitätsmerkmale von Siloinhalten überwacht und bearbeitet werden. Die
einzelnen Qualitätsdatensätze können dabei
automatisch
oder
manuell
erzeugt werden.

---

## Schritt 4 Benutzeroberfläche

Schritt 4 Benutzeroberfläche
Abhängig, wie das Postfach eingerichtet ist, werden
die Postfachzuordnung und Status angezeigt, oder ausgeblendet.
1.
Postfachzuordnung
Wird nur angezeigt, wenn im Postfach die
Prozedur
Anforderung hinterlegt ist. Hier kann unter den in der Prozedur vorselektierten
Postfächer frei ausgewählt werden, wo das Dokument landen soll.
Dies ist meist in der Poststelle Sinnvoll, welche den
Beleg beispielsweise einer Abteilung zuordnet.
2. Status
Wird nur angezeigt, wenn im Postfach die
Prozedur
Genehmigung hinterlegt ist. Hier wird der Status eines Dokuments aktualisiert.
In der Weiterverarbeitung ist dann hinterlegt, wo das Dokument als nächstes
landet.
Wenn ein Abteilungsleiter ein Dokument genehmigt,
könnte dies beispielsweise an die Buchhaltung weitergeleitet werden.
Es wird empfohlen sich bei jedem Postfach zu
entscheiden, ob die Postfachzuordnung oder der Status für die Weiterleitung
genutzt wird.
3 & 4. Bemerkung
In Fenster 3 werden alle Bemerkungen, welche in
Fenster 4 erfasst wurden, dargestellt. Die Formatierung der Darstellung kann in
der Prozedur „Belegflussbemerkung“ angepasst werden
5 & 7. Kontierung
Hier können Daten für die Kontierung erfasst werden.
Diese werden bei der Erzeugung von Warenbelegen bzw. Fibubelegen als Grundlage
genutzt. Hierbei handelt es sich lediglich um eine Erfassungshilfe.
Nachträgliche Änderungen in den Belegen werden nicht übertragen. Nach dem
Erzeugen eines Belegs ist es nicht mehr möglich die Felder zu editieren.
6. Kontierung-Vorlage
Mit dem i-Button lassen sich gespeicherte Vorlagen
auswählen. Sollte bereits ein Kunde ausgewählt sein, werden auch nur die
Vorlagen des entsprechenden Kunden angezeigt.
Mit dem +-Button lässt sich der Vorlagen-Pfleger
öffnen. Die aktuelle Belegung wird übernommen. Auf diese Weise lassen sich
Vorlagen schnell erfassen. Die Verwaltung der Vorlagen läuft über Variante
5.
8. Datensatz
Eindeutige Identifikation des Datensatzes. Fa-Id und
Fa-MndNr definieren h
[...]


---

## Silobuch

Silobuch
Hauptmenü
Nebenbuchhaltungen
Siloverwaltung
Silo
Direktsprung
[SILO]
Im Silobuch werden alle
Änderungen auf dem ausgewählten Silo dargestellt. Dies beinhaltet auch
stornierte Buchungen.
Bedeutung von ausgewählten
Felder im Silobuch
Feld
Bedeutung
Bemerkung
Dieses Feld kann bislang folgende
      Ausprägung annehmen
Ausprägung
Bedeutung
Silobuchung
Summierte Menge einer
          Bestandsmeldung
Leermeldung
Das Silo wurde
            Leer gemeldet.
Qualitätswerte manuell gesetzt
Die Qualitätswerte des Silos wurden
            gesetzt
Des Weiteren werden in diesem Feld
      Behandlungsmethoden für das Silo angezeigt.
Ausbuchungsmenge
Wird ein Silo Leergemeldet, und es
      existiert einen Mengen Differenz zwischen Eingang und Ausgang so wird
      diese Menge hier angezeigt. (Dies betrifft nur die Leermeldungen in dem
      eine Bestandsmeldung gemacht wurde)
Aktivität
In diesem Feld wird die Aktivität
      der Silobuchung angezeigt. Diese kann im Waagenprozess hinterlegt werden.
      Des Weiteren können in dem Anwenderformat AF_LVSAKTTYP eigene Aktivitäten
      hinterlegt werden. Die ersten 100 Einträge werden seitens des Systems
      gepflegt.
Gegen Silo
Existiert zu einer Aktivität /
      Silobuchung ein Gegensilo, so wird dies hier angezeigt.
Folgenden Aktivitäten können ein
      gegen Silo haben.
1.
      Bestandsübertragung
2.   Position
      verschieben
3.   Position
      kopieren
4.   Menge
      umbuchen
Waagen Belegnummer
Nummer der Wiegung in der
      Hofliste(Waage)
Art
Art der Wiegung
Art
Bedeutung
WE
Wareneingang
WA
Warenausgang
RWE
Rohwareneingang
RWA
Rohwarenausgang
LGU
Lagerumbuchung
LW
Lohnwiegung
Bewegungstatus
1.   Inventur
      Austrag
2.   Inventur
      Vortrag
3.   Inventur Austrag
      gelöscht
4.   Inventur Vortrag
      gelöscht
Besonderheit
Wird eine Position von einem Silo auf ein anderes Silo
kopiert wird die Information der Waage mit kopiert aber nicht im Silobuch
angezeigt. Da der Wieg
[...]


---

## Spedition

Spedition
Hauptmenü
Nebenbuchhaltungen
LKW-Verwaltung
Speditionsstamm
Direktsprung
[SPED]
Für eine Spedition muss eine Nummer (es wird eine
Nummer vorgeschlagen die um 1 größer ist als die größte vorhandene Nummer)
vergeben werden und es können ein Matchcode und eine Bezeichnung angegeben
werden.
Über eine
F3
-Auswahl kann
man den entsprechenden Lieferanten auswählen.
Funktion
Anschrift
:
Mit dieser Funktion kann eine manuelle Anschrift
gepflegt werden auch wenn keine Lieferantennummer/ Kundennummer angegeben ist.
Wenn schon eine Kunden/Lieferanten Zuordnung existiert aber noch keine manuelle
Adresse so kann eine manuelle Adresse nachgepflegt werden.
Eine manuell zugeordnete Anschrift kann nach
erfolgreicher Zuordnung eines Kunden/Lieferanten auch wieder gelöscht werden.
Um die manuelle Zuordnung zu löschen gehen Sie wie
folgt vor.
Drücken Sie die Taste
F10
oder klicken Sie auf die Funktion
Anschrift
in der Optionbox.
Bei der Abfrage „Die Spedition hat eine
Kunden/Lieferanten Zuordnung und eine manuelle Anschrift“ auf „Nein“ klicken.
Jetzt kommt die Abfrage, ob die Zuordnung zu manuellen Adresse gelöscht werden
soll. Bei der Bejahung der Frage wird nicht die Adresse gelöscht sondern nur die
Zuordnung zwischen der Spedition und der Adresse.

---

## Fibu-Übertrag Warenwirtschaft

Fibu-Übertrag Warenwirtschaft

---

## Stoffstrom-Bilanz-Daten

Stoffstrom-Bilanz-Daten
Übersicht
Das Lizenz-Modul zur Ermittlung von
Stoffstrom-Bilanz-Daten ermöglicht die Erfassung, Verwaltung und Ausweisung von
Daten zur Unterstützung bei der Informationsbeschaffung
stoffstrombilanzpflichtiger Betriebe.
Das grundsätzliche Verfahren beruht
darauf, zunächst jedem betroffenen Artikelstamm über seine
Zusammensetzung
die individuellen
Stoffstrom-Komponenten zuzuordnen und dabei die jeweiligen Anteilwerte
festzulegen. Alle zu verwendenden Stoffstrom-Komponenten sind dafür zunächst in
die allgemeine Artikelbestandteil-Liste mit Angabe der Stoffstromart aufzunehmen
(siehe
Bestandteile
).
Die
Stoffstromarten sind im
Anwendungsformat
‚af_stofstart‘
aufgeführt und können bei Bedarf ergänzt werden.
Bei der Erfassung, Erzeugung und Bearbeitung von
Vorgängen werden für Positionen mit Artikeln, denen Stoffstrom-Komponenten
zugeordnet sind, beim Speichern des Vorgangs aus der Positionsmenge und den
Anteilen aus der Zusammensetzung die Stoffstrommengen berechnet und gespeichert.
Bei Standardvorgängen im
Verkauf
kann auf der Warenpositionsmaske in der
Registerkarte
Stoffstromwerte
der Lieferant aus dem Lieferantenstamm
angegeben werden. Sind diesem Lieferanten im Artikelstamm der Position
individuelle Stoffstromparameter zugeordnet, so ersetzen diese diejenigen aus
der Artikelzusammensetzung. Im
Einkauf
werden diese Werte bei der
Erzeugung oder Erfassung einer Belegposition bezüglich der
Kunden-/Lieferantennummer des Vorgangs herangezogen.
Zu beachten ist,
dass bei Änderung der Anteil-Angabe eines Stoffstrombestandteils in der
Artikelstamm-Zusammensetzung nachfolgende Änderungen an Vorgängen automatisch
die entsprechenden Stoffstrommengen neu berechnen, sofern der im Vorgang bereits
festgehaltene Wert nicht per Stoffstrom-Editor oder bei Standardvorgängen in der
Warenerfassungsmaske manuell geändert wurde.
Positionsorientierte
Auswahlvarianten der diversen Vorgangsbearbeitungs-Module ermöglichen die
manuelle Korrektur
[...]


---

## Stornieren/Löschen

Stornieren/Löschen
Ein erfasster Beleg kann, solange er noch nicht zum
Beispiel per Umwandlung oder Fibu-Übertrag weiterverarbeitet wurde, durch die
Funktion
Stornieren
gelöscht werden. Der Beleg ist anschließend im
System nicht mehr enthalten. Für gedruckte Rechnungen und Gutschriften ist dabei
die Einstellung des Steuerungsparameters
[SPA]
Rechnung/Gutschrift nach Druck stornierbar (SPA152)
zu
berücksichtigen, der bei Bedarf sicherstellt, dass, mit der Einstellung
Nein,
gedruckte Belege nicht mehr storniert werden können.
Der Steuerparameter
[SPA]
Quellbelegreaktivierung bei Stornieren/Löschen von
Warebelegen (BA,AG,BS,AU,LI,RE) (SPA987)
mit den Einstellungen
Nein
,
im Verkauf
,
im Einkauf
bzw.
im Einkauf und Verkauf
regelt
die Reaktivierung von Quellbelegen des stornierten Vorgangs. Bei entsprechender
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

## Benutzerinformation

Benutzerinformation
Server
Feldname
Beschreibung
Name
Name
      des Datenbankservers
RequestLogFile
Hier
      wird der Name der Datei zur Anforderungsprotokollierung angezeigt, wenn
      eine existiert.
Technische Verbindungen
Anzahl aller technischen
      Verbindungen die zurzeit zur Datenbank bestehen
Unterschiedliche
      Benutzer
Anzahl der unterschiedlichen
      Benutzer (ein Benutzer kann mehrere Verbindungen zu Datenbank haben wird
      hier aber nur einmal gezählt)
Benutzerinformation
Kopfdaten
Beschreibung
Name
Kürzel des aktuellen
      Bedieners
Eigene Id
Die
      Id des aktuellen Bedieners
Hier erhält man Informationen zu den Benutzern in der
Datenbank. Man kann die Verbindung eines Benutzers durch Doppelklick trennen
oder allen Benutzern eine Meldung schicken.
Felder
Name
Kürzel des aktuellen
      Bedieners
Eigene Id
Die
      Id über die der aktuelle Bediener zurzeit verbunden ist
Id
Id
      über die der Bediener verbunden ist
Benutzer
Kürzel des Bedieners
DBName
Name
      der Datenbank
Nodeadress
IP-Adresse des Rechners über den der
      Benutzer mit der Datenbank verbunden ist.
Commlink
Verbindungsart z.B.
      TCPIP
LastRegTime
Registrierte Zeit der letzten
      Anforderung durch den Benutzer
Schreib
Anzahl der
      Schreibanforderungen
Lese
Anzahl der
      Leseanforderungen
Blocknr.
Falls die aktuelle Verbindung nicht
      blockiert ist, wird der Wert Null angezeigt. Sonst entspricht der Wert der
      Verbindungsnummer der Verbindung, die aufgrund eines Sperrenkonflikts
      blockiert ist.
Connection
Art
      der Verbindung / Programm mit dem man sich mit der Datenbank verbunden
      hat

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

## Datendrehscheibe (TERRES)

Datendrehscheibe (TERRES)
Hauptmenü
Externe Kommunikation
Datendrehscheibe [
TERRE
]
Informationen
Aus dem Terres System können Artikel, Preise,
Lieferanten und Buchungsdaten in  Referenz-ERP eingespielt werden. Die von Terres
bereitgestellten Daten werden auf einem Download Server bereitgestellt. Der
Datenaustausch findet bei Terres über XML statt. Die Struktur der Dateien ist
anhand dieser XML Datei ersichtlich.
Bei der Ersteinrichtung eines Marktes werden ca.
300000 Artikel nebst Preisen und Lieferanten in XML bereitgestellt und in das
Referenz-ERP System eingespielt.
Importieren der Daten in das Referenz-ERP System
Sind alle von Terres stammende XML Dateien mit den
Artikeln und Preisen von dem Download Server kopiert worden, können diese in das
Referenz-ERP System eingespielt werden. Es gibt zwei Wege wie die Terres Dateien in
das System Referenz-ERP eingespielt werden können. Durch einen
Automatisch
en
Nachtlauf welcher per Event gesteuert wird,
oder  durch einen manuellen Lauf der per Hand ausgelöst wird.
Bevor die XML
Datei in das Referenz-ERP System eingespielt werden, müssen noch einige Einstellungen
berücksichtig werden.
Hauptmenü
Externe Kommunikation
Datendrehschreibe
Artikelimportverfahren Direktsprung
[TERRE]
In dieser Auswahlliste sind nach einer erfolgreichen
Einspielung die Terres Artikel zu sehen.
Um den Import zu starten wird die Funktion
Datendrehscheibe
[
F9
] aufgerufen. Wird das Anzeigefenster zum
ersten Mal geöffnet, so öffnet sich ein Dialog in dem das Verzeichnis ausgewählt
wird, in dem sich die zu importierenden Daten befinden. Es muss dabei beachtet
werden, dass das Verzeichnis sich relative zum Datenbankserver befindet. Dieses
Verzeichnis kann jederzeit geändert werden.
Auch wenn das Importieren der Daten per Event läuft
ist darauf zu achten, dass das Verzeichnis angegeben wird.
Nach dem der Pfad richtig eingetragen worden ist,
existiert noch die Möglichkeit ein Trace einzuschalten. Das Trace protokolliert
wie viele Datensätze bei dem Import eingespielt
[...]


---

## Tourverwaltung

Tourverwaltung
Hauptmenü
Nebenbuchhaltungen
Tourverwaltung
Tourverwaltung
Direktsprung
[TOUR]
Funktionen
Funktionsname
Funktion
Tourenplanung
(F9)
Ruft
      die Tourenplanung auf
Ladeliste n. Tag
Über
      die Funktion
Ladeliste n. Tag
kann man sich eine Liste nach
      Stationsnummer sortiert anzeigen lassen. Auf ihr befinden sich die Adresse
      des Kunden, sowie die einzelnen Positionen der Lieferung.
Ladeliste 2
Eine
      alternative Form der Ladeliste
Tourliste nach Tag
Zeigt eine Liste aller Touren an
      einem ausgewählten Liefertag an.
Tourliste nach Tour-Nr.
Zeigt eine Liste aller Touren in
      einem ausgewählten Bereich an.
Tourliste nach Kunden
Zeigt eine Liste aller Kunden mit
      den dazugehörigen Touren in einem ausgewählten Bereich an.
Tourenliste incl.
      Belegen
Zeigt eine Liste aller Touren einer
      ausgewählten Tour-Nr. inklusive aller Belegnummern der Tour
      an.

---

## Umbuchung

Umbuchung
Umbuchen sind entweder dann notwendig, wenn im Bau
befindliche Anlagen fertiggestellt sind und nun abgeschrieben werden sollen (
Änderung der AfA – Methode ) oder bestimmte Daten wie z.B.: Nutzungsdauer,
Anlagenkonto,
Kostenstelle
,
Kostenträger
oder
Kostenobjekt
sich ändern. Im
Anlagenspiegel erscheinen im Jahr der Umbuchung beide Anlagegüter.
Wichtig:
Vor
der
Umbuchung müssen ggf. die Abschreibungen vorgenommen
werden.
Wird für ein Anlagegut der Abschreibungsverlauf
handels- und steuerrechtlich getrennt behandelt, so betreffen Umbuchungen immer
sowohl den steuerrechtlichen als auch den handelsrechtlichen Verlauf. Für den
handelsrechtlichen Verlauf werden keine automatischen Buchungen erstellt.
Um ein Anlagegut umzubuchen, gibt es drei
Möglichkeiten:
•
Man geht in der Historie und trägt in der letzten Zeile „Umbuchung“ ein
(eine Auswahl sämtlicher möglichen Arten ist mit
F3
möglich).
•
Man markiert einen oder mehrere Datensätze in der Variante
„Anlagenkartei“ der Auswahlliste zum Anlagenstamm und wählt die Funktion
Umbuchen aus (siehe
Anzahlung
).
•
Man markiert in der Variante „Fibubeleg ohne Anlageneintrag“ einen
SO-Beleg, bei dem als Anka-Typ „Umbuchung“ steht. Die hier angezeigten SO-Belege
haben als Haupt und als Gegenkonto ein Anlagenkonto.
Bei den ersten beiden Varianten öffnet sich dann ein
weiteres Eingabefenster, auf dem dann die notwendigen Informationen abgefragt
werden. Bei der dritten Variante ist dies nicht nötig, da hier ja bereits der
Beleg existiert und somit nur eine Zuweisung zu dem Anlagegut geschieht.
Es sind also die neue Inventarnummer, das Datum, an
dem die Umbuchung durchgeführt wird, Fälligkeit, Nummernkreis für den Fibubeleg
sowie das ggf. neue Anlagenkonto und eine Text einzutragen. Wählt man als
Inventarnummer die Nummer eines bestehenden Anlagegutes, so erscheint eine
Abfrage, in der man bestätigen muss, dass man die Umbuchung auf ein
existierendes Anlagegut vornehmen will.
Anschließend öffnet sich sof
[...]


---

## Verbuchung (Produktion)

Verbuchung (Produktion)
Nach Abschluss des Beleges kann dieser in die
Finanzbuchhaltung überstellt werden. Hier erfolgt eine echte Buchung dann, wenn
Produkt und Komponenten unterschiedliche EKZ oder
Kostenstellengruppenzuordnungen eingetragen haben.
Insbesondere bei Einstellungen im Rezept, die nicht
geschlossene Buchungen erzwingen empfiehlt es sich, die Buchung in der Fibu
durchzuführen.

---

## Verspätete Anschaffungs- und Herstellungskosten

Verspätete Anschaffungs- und
Herstellungskosten
Verspätete Anschaffungs- und Herstellungskosten werden
in der Anlagenbuchhaltung als Zugang (z.B. Anschaffung einer Plane für einen
LKW), als Teilabgang (z.B. bei Gutschrift) oder als negativer Zugang(bei Skonto)
gekennzeichnet. Diese können - wie bereits die Neuzugänge - auf unterschiedliche
Art und Weise in die Anlagenbuchhaltung gelangen.
1.
Über die Belegerfassung der Finanzbuchhaltung. Bei den Belegtypen
Eingangsrechnung und Eingangsgutschrift öffnet sich eine Itembox, in der ein
bestehendes Anlagegut ausgewählt werden kann. Wählt man ein bestehendes
Anlagegut aus, so wird sofort eine Zeile vom Typen Zugang bzw. Teilabgang in die
Historie geschrieben. Dies kann noch geändert werden.
Bei Eingangsrechnungen
kann auch ein neues Anlagegut erfasst werden. In der Itembox steht dafür in der
ersten Zeile „—NEU—„. Wählt man diese Zeile aus, wird ein neues Anlagengut
erstellt. . Soll der Betrag auf mehrere Anlagegüter verteilt werden so wählt man
den zweiten Punkt „—AUFTEILEN—„
2.
Über die Variante „Eingangsrechnungen ohne Anlageneintrag“ bzw. „Fibubeleg ohne
Anlageneintrag“ im Anlagenstamm. Wie bei der direkten Erfassung in der
Finanzbuchhaltung kann man in einer Itembox bestehende Anlagegüter auswählen
oder ein neues Anlagegut erfassen. Die Funktion „„Verteilung/Zuordnung“
ermöglicht bei Belegen vom Typ Eingangsrechnung und bzw. in der Variante
„Fibubeleg ohne Anlageneintrag“ für Eingangsgutschrift das Verteilen des Betrags
auf mehrere Anlagegüter. Bei der Erfassung über diese Variante wird der Zugang
dem Fibubeleg zugeordnet.
Skontobelege können nur über die Variante
„Fibubeleg ohne Anlageneintrag“ einem bestehenden Anlagegut zugeordnet werden.
Sie werden als negativer Zugang gekennzeichnet.
3.
Direkt im Anlagenstamm. Diese Methode erzeugt keinen Verweis zu einem
bestehenden Fibubeleg und sollte nur angewendet werden, wenn man die
Anlagenbuchhaltung nach Systemwechsel neu einsetzt und Zu-
[...]


---

## Vertretergruppen: Pfleger

Vertretergruppen: Pfleger
Kopfdaten
Vertretergruppe
Schlüssel für die Zuordnung
      provisionsrelevanter Buchungen (z. B. Warenverkäufe) zu den
      Provisionsempfängern. Im Normalfall besteht eine Vertretergruppe nur aus
      einem Vertreter, der 100 Prozent der Provision erhält.
Bezeichnung
Bezeichnung für die
      Vertretergruppe
Matchcode
Register Allgemein
Felder
Beschreibung
Einzelprovision
Kennzeichen, ob die Provisionssätze
      in dieser Vertretergruppe von Vertreter zu Vertreter verschieden sein
      können. Normalerweise ist die Ermittlung der Provision lediglich von der
      Vertretergruppe abhängig, also identisch innerhalb einer
      Gruppe.
Ja –
      Es ziehen Provisionsmerkmale aus dem Vertreterstamm
Nein
      – Es ziehen Provisionsmerkmal aus der Vertretergruppe
Berechnungsvariante
Es
      sind verschiedene Berechnungsvarianten für die Provision denkbar:
1 -
      Berechnung vor der Verteilung = Die Provisionsermittlung erfolgt vorweg
      entsprechend der Provisionstabelle, danach wird die Provision anhand des
      Schlüssels auf die Vertreter verteilt. Bei gleichen Provisionssätzen
      innerhalb einer Gruppe ist dies sinnvoll.
2 -
      Berechnung nach der Verteilung = Zunächst werden die Umsätze anhand des
      Verteilungsschlüssels auf die Vertreter der Gruppe aufgeteilt, dann wird
      die Provision je Vertreter anhand seiner Provisionstabelle errechnet. Dies
      ist relevant, wenn in einer Gruppe unterschiedliche Provisionssätze
      bestehen.
Anteilsausschöpfung
Summe der Anteile aller Vertreter in
      einer Gruppe.
Vertreternummer
Nummer des Vertreters in der
      Vertretergruppe
Funktionen:
Funktion
Beschreibung
Neu
      (F8), Speichern (F9)
Provisionsmerkmale
Hier
      ändert man die Provisionsmerkmale der Vertretergruppe, wenn die
      Einzelprovision im Pfleger auf „Nein“ steht.

---

## Voraussetzungen zur Reorganisation

Voraussetzungen zur Reorganisation
Um Datenbestände zwischen den 4 genannten Bereichen
abgleichen zu können müssen folgende Voraussetzungen erfüllt sein:
Mandantenserver
Der im Hintergrund wirkende Buchungsprozess
Mandantenserver muss alle relevanten (zu prüfender Zeitraum) Belege erfolgreich
abgearbeitet haben
Belegumwandlung
Die relevanten Belege müssen in den jeweiligen
Endzustand umgewandelt worden sein (Lieferscheine E / V)
Fibuübertrag
Belegsummen und Fibusummen können erst nach dem
erfolgreichen Übertrag übereinstimmen.
Periodenverfahren
Warenbelege müssen beim Übertrag der gleichlautenden
Fibuperiode zugeordnet werden. Dies kann im Einzelfall nicht gewollt sein.
Hieraus ergibt sich eine Periodenverschiebung, die Ergebnisse können dann nur
auf Jahresebene abgestimmt werden. Siehe hierzu auch entsprechende
Steuerparameter.

---

## Ansicht

Ansicht
Mit der Funktion werden Vorgänge wie bei der Korrektur
geladen, können aber nicht geändert werden und werden daher auch beim Abschluss
nicht gespeichert. Zudem wird ein zur Ansicht geladener Vorgang nicht gelockt,
so dass er von mehreren Benutzern gleichzeitig zur Ansicht geöffnet werden kann.
Zudem kann er durch einen anderen Benutzer auch im Korrektur-Modus oder zur
Umwandlung geöffnet werden.
Hinweis:
Je
nach Einstellung des Steuerparameters
Makros bei Ansicht eines Vorgangs
ausführen
(SPA 862)
kann es insbesondere im Ansicht-Modus bei
gleichzeitiger Korrektur des Vorgangs durch einen anderen Benutzer zu Konflikten
kommen, wenn die Implementation der beteiligten Makros diese Situation nicht
vorsehen.

---

## Informationen zur Verteilung von Gruppen-Zu-/Abschlägen

Informationen zur Verteilung von Gruppen-Zu-/Abschlägen
Die Datenbankrelation
VorgGruppenZuAbInfo
enthält nach Abschluss eines Vorgangs Informationen über die Verteilung der
Gruppen-Zu- und Abschläge inklusive Gruppen-Rabatte, Gruppen-Fachten und
Gruppen-Verpackungssätzen. Sie dient der Informationsfindung, welche Beträge
eines Gruppen-Zu-/Abschlags auf welche Warenpositionen mit welchem
Steuerschlüssel in welcher Höhe verteilt wurden.
Die einzelnen Datenbankfelder der Relation sind:
Feld
Beschreibung
V_Id
Die
      ID des Vorgangs.
V_PosiZaehler_GrZuAb
Positionsnummer des zugehörigen
      Gruppen-Zu/Abschlagsatzes.
V_PosiZaehler_Ware.
Positionsnummer des zugehörigen
      Warenpositionssatzes.
V_GrZuAbInf_Typ
Der
      Typ des Zu-/Abschlags:
1  - Rabatt
11 – individueller
      Rabatt
2  – Zu-/Abschlag
12 – infividueller
      Zu-/Abschlag
3  – Fracht
13 – individuelle
      Fracht
4  – Verpackung
V_GrZuAbInf_Kalk
1:
      kalkulatorischer Zu-/Abschlag
Sonst: nicht
      kalkulatorisch
V_GrZuABInf_Anteil
Der
      auf die Warenposition entfallende Nettobetrag.
V_GrZuABInf_SAnteil l
Der
      auf die Warenposition entfallende Steuerbetrag.
V_GrZuABInf_Bezug.
Die
      Bezugsgröße der Warenposition für diesen Zu-/Abschlag.
V_GrZuABInf_WaehrAnteilert
Der
      auf die Warenposition entfallende Nettobetrag in Währung.
V_GrZuABInf_WaehrSAnteil
Der
      auf die Warenposition entfallende Steuerbetrag in Währung.
V_GrZuAbInf_WaehrBezug
Die
      Bezugsgröße der Warenposition für diesen Zu-/Abschlag in
      Währung.
V_GrZuAbInf_StSchluessel
Der
      zugehörige Steuerschlüssel.
V_GrZuAbInf_StKlasse
Die
      zugehörige Steuerklasse.
V_GrZuAbInf_StSatz
Der
      zugehörige Steuersatz.
Hinweis:
Für ältere Vorgänge, für die diese
Einträge noch nicht erzeugt wurden, werden diese auch beim Öffnen des jeweiligen
Vorgangs im
Ansehen-Modus
nachgetragen.

---

## Doppelbuchung Silo / LVS

Doppelbuchung Silo / LVS
Bucht die
LVS Daten
noch einmal in das Silo
oder auf den Ladeträger, ohne zu prüfen, ob die Wiegedaten sich schon auf dem
Ladeträger befinden.

---

## Silo nachbuchen

Silo nachbuchen
Mit der Funktion „Silo nachbuchen“ in der Auswahlliste
ist es möglich Wiegungen, die nicht mehr rückgängig abgeschlossen werden können,
da aus diesen schon ein Vorgang erzeugt worden ist, nachträglich in das Silo /
den Ladeträger einzubuchen. Als Buchungszeit wird dann die Zeit der zweiten
Wiegung genommen. Auch hier wird berücksichtigt, ob auf diesem Silo / Ladeträger
schon eine
Leermeldung
erfolgt
ist. Die Wiegung wird dann zeitlich richtig eingeordnet. Mit dieser Funktion
können auch Wiegungen doppelt in das System eingebucht werden.

---

## Registerkarte Anforderung

Registerkarte Anforderung
Anforderung
ID
Art
Folgende Arten gibt es:
0 =
      GA (Gewichtsanforderung)
1 =
      VL
Senden
Hiermit kann man einstellen, ob eine
      GA oder VL auch wirklich gesendet werden soll.
Sehr
      interessant für Entwicklungs- und Debug-Zwecke. Andernfalls müsste man
      evtl. ein schwer erarbeitetes VL löschen …
Anforderung
Hier
      gilt das im Wesentlichen schon unter „
Art
“
      Gesagte.
<WAIT> wartet eine Sekunde,
      bevor es fortfährt. Dieses Feature ist für „träge“ Waagen-Systeme
      unverzichtbar. Eventuell muss man mehre <WAIT>-Sequenzen
      absenden
Antwort
???
Wandlung
Beeinflusst mögliche
      Transformationen der Anforderungszeichenketten
Wartezeit
Vorgabe einer Zeit in Millisekunden,
      nach dessen Ablauf die Übertragung der Anforderungszeichenkette als
      gescheitert gelten darf. Es sind in aller Regel kurze Zeiten zu erwarten
      (>= 100 Millisekunden); man sollte mit kleineren Zeiten vorsichtig
      umgehen, und sich diese durch die Praxis bestätigen lassen …
Pos
Sortierungskriterium für die
      Reigenfolge der VL.
Da
      es höchstens eine GA geben darf, wird diese wenn auch immer erst am Ende
      der VL verschickt. Sollte es in Zukunft Waagensysteme geben, die noch
      einen „Nachlauf“ benötigen, muss das noch implementiert
      werden!
Art
GA: Gewichtsanforderung
Das Kommando, das die Waage benötigt, um die
Gewichtsdaten zu übertragen.
Im obigen Beispiel benötigt die Waage das Kommando
„<ENQ>“.
Hierbei ist eine Besonderheit zu beachten: Die so
genannten „Nicht-Druckbaren-Zeichen“ werden durch
„<Nicht-Druckbares-Zeichen>“ verklauseliert.
Konkret bedeutet dies, dass der Wage nicht die Zeichen
„<“, „E“, „N“, „Q“, „>“ geschickt werden, sondern das hinterlegte
Nicht-Druckbare-Zeichen.
Das ganze Manöver deshalb, um die Kommunikation in
einer übersichtlichen Repräsentation zu halten.
Die Umschlüsselung erfolgt über das Format
„COMBITHELPER“.
Ist keine GA angegeben, dan
[...]


---

## Signalfelder

Signalfelder
Es gibt Zustände einer Warenposition, die verschiedene
buchungstechnische Folgen haben oder Informationen, die dem Erfasser deutlich
sichtbar gemacht werden sollen. Diese werden mit farbigen Signalfeldern
angezeigt. Bisher z.T. auf der Maske angezeigte Hinweistexte wurden durch diese
Signalfelder ersetzt.
Allgemeine Signalfelder
Name
Beschreibung
Wertartikel
Dieses Signal wird angezeigt, wenn
      es sich bei der Artikelposition um einen Wertartikel handelt.
Dieser Status konnte bisher nur
      durch Anwahl einer Funktion analog zur Artikelerfassung angegeben werden.
      Nun ist auch während der Artikelerfassung das Ein-/Ausschalten dieser
      Information möglich.
Stückl. Hauptartikel
(nur
      geplant) Dieser Artikel ist ein Hauptartikel einer Stückliste
Stückl. Folgeartikel
(nur
      geplant) Dieser Artikel ist ein Folgeartikel einer Stückliste
Hauptartikel
(nur
      geplant) Dieser Artikel ist Hauptartikel einer Artikelfolge
Folgeartikel
(nur
      geplant) Dieser Artikel ist ein Folgeartikel einer
      Artikelfolge
(kein) Kontraktartikel
(nur
      geplant) Dieses Signal gibt an, dass dieser Artikel einem Kontrakt
      zugeordnet ist
(kein) Partieartikel
(nur
      geplant) Dieses Signal zeigt an, dass diesem Artikel eine Partie
      zuzuordnen ist
(keine) Lagerabholung
Hier
      wird angezeigt, dass dieser Artikel zu denen gehören soll, die auf der
      Lieferung als Abholung im Lager gekennzeichnet werden sollen.
Ausbuchen
Hier
      wird angezeigt, ob bei der „
Schnellen
      Teildisposition
“ die Position ausgebucht werden soll
Signalfelder aus Voreinkauf, Vorverkauf, Einlagerung
und Kommission
Alle diese Felder lassen sich zum Zeitpunkt der
(Erst-)Erfassung mit Hilfe von Menüfunktionen ein- und ausschalten
(toggeln).
Anzeige
Seite
Beschreibung
Vorverkauf
Verkauf
Vorverkauf.
Dieser Status konnte bisher nur
      durch Anwahl einer Funktion analog zur Artikelerfassung angegeben werden.
      Nun ist auch w
[...]


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

## Wichtige Information zu den Mengen:

Wichtige Information zu den Mengen:
Es gibt nur die vollständige Mengenzuordnung zu einer
oder mehrere Partien oder keine Partiezuordnung – Teilmengen sind nicht erlaubt
(es erfolgt dann stets ein Fehleingabe-Hinweis, spätestens beim Abschluss der
Warenposition!). Ferner ist es nicht möglich, mit unterschiedlichen
Mengenvorzeichen zu arbeiten (Beispiel: Artikelmenge 60, Partie 1: 150, Partie
2: -90).

---

## Wirtschaftsjahre und Perioden

Wirtschaftsjahre und Perioden
Hier geht es um die zeitliche Organisation von
Abschlüssen, oder anders formuliert um die Einteilung der Wirtschaftsjahre in
(Abschluss-) Perioden für die WaWi und die FIBU.
In allen wichtigen Bereichen werden Periodenzahlen
vorgehalten, die per Liste oder Bildschirm abrufbar sind.
Folgende Programmteile sind einzurichten:

---

## Workflowverbuchungsregeln

Workflowverbuchungsregeln
Hauptmenü
Dokumentenverwaltung
Workflow Verbuchungsregeln oder Direktsprung
[WFVR]
Durch diese Anwendung kann man für
den Belegfluss Verbuchungsregeln für Fremdartikel definieren.

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

## Abfrage der Buchungsperiode

Abfrage der Buchungsperiode
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Der Einstieg in die Belegerfassung beginnt mit der
Eingabe der Buchungsperiode (Periode/Jahr).
Die aktuelle Periode und das Jahr werden vorbelegt:
Periode 11 und Jahr 2011. Die Periode wird anschließend im Grundbildschirm als
„Aktive Periode“ angezeigt.
Ob diese Kostenstelle abgefragt wird, kann in dieser
Maske mit dem Einrichterparameter „Kostenstellenvorbelegung abfragen?“ ab- bzw.
angeschaltet werden.
Die Kostenstelle wird abgefragt und als Vorbelegung in
der Belegerfassung verwendet, wenn zu diesem Sachkonto keine Kostenstelle im
Sachkontenstamm als Vorbelegung hinterlegt ist.
Ob und wie die Belegmappe abgefragt wird, wird in dem
darunterliegenden Bildschirm mit dem Einrichterparameter „Belegmappe abfragen“
eingestellt. Hier existieren drei Ausprägungen:
•
Nicht aktiv. Es wird ohne Belegmappe gearbeitet. Dies ist die
Vorbelegung
•
Belegmappe einmal zentral abfragen. Die Belegmappe wird nur in diesem
Abfragefenster abgefragt und ansonsten im Grundbildschirm und in der
Belegerfassung nur angezeigt.
•
Belegmappe in der Belegerfassung abfragen. Die Belegmappe kann zusätzlich
in der Belegerfassung noch geändert werden. Vorbelegt wird sie mit der in diesem
Abfragefenster angegeben Mappe.
Näheres zum Thema Periodeneinteilung befindet sich im
Abschnitt "Firmenstamm". Wenn dort eine andere Einteilung als Monat vorgenommen
wurde, bezieht sich die Eingabe natürlich auf diese Einteilung.
Sämtliche erfassten Bewegungen werden für diese
Periode abgespeichert und für diese Periode ausgewertet (USt- Voranmeldung,
Bilanz, GuV, Saldenlisten...).
Während der Belegerfassung besteht jedoch jederzeit
die Möglichkeit über die Funktion
Periode Ändern
F10
die
Buchungsperiode für einen Beleg zu verändern.
Nach Eingabe der Buchungsperiode wird in den
eigentlichen Erfassungsbildschirm verzweigt.

---

## Ablauf ZMDO

Ablauf ZMDO
Hauptmenü
Abschlussarbeiten
Zusammenfassende Meldung
Variante ZM nach AW.Position
Direktsprung
[UVZM]
In dieser Auswahlliste werden die Daten, die für den
Versand vorgesehen sind dargestellt. Für die ZMDO werden die Steuersätze
herangezogen, für die die Auswertungspositionen mit den Kennzahlen für
"Innergemeinschaftliche Lieferung "(bisher 41) bzw. "Lieferungen des ersten
Abnehmers bei innergemeinschaftlichen Dreiecksgeschäften" (bisher 42) und – seit
Januar 2010 – „Nicht  steuerbare sonstige Leistungen gem. § 18b Satz 1
Nr.  2 UStG“ ( 21 ) eingetragen sind. Diese Kennzahlen sowie der Zeitraum
werden in der zugrundeliegenden F2-Bereichsauswahl abgefragt.
Für die Art, wie die Daten aufbereitet werden,
existiert der Steuerungsparameter „ZMDO mehrere Kunden mit gleicher USTID
akzeptieren“ (SPA 934). Die Auswahlliste generiert pro Konto die Daten. Dies ist
die Standardeinstellung dieses Steuerungsparameters. Wenn zu unterschiedlichen
Konten dieselbe UDTID hinterlegt ist – weil es sich z.B. um verschiedene
Filialen handelt – kommt es bei der Übertragung zu Problemen, da dieselbe USTID
nicht mehrfach ( es sei denn mit anderen Kennzeichen für Dreiecksgeschäft /
Sonstige Leistung) vorkommen darf. Stellt man den Steuerungsparameter auf
Ja
, so
werden die Daten nach der USTID gruppiert. Die Konten
werden dann nur noch Informatorisch angezeigt.
Wurden Daten angezeigt, so kann mit der Funktion „ZMDO
via ELSTER“  der Versand vorbereitet werden.
Berichtigte Anmeldung
Handelt es sich um eine Erstmeldung, so ist hier
Nein
einzutragen. Bei einer berichtigten Anmeldung muss hier
Ja
stehen.
Abgabe der ZMDO Monatlich
Bei Abgabe einer
Monatsmeldung in Meldezeiträumen ab 01.07.2010 kann der Benutzer anzeigen, dass
er zukünftig monatlich seine Zusammenfassende Meldung abgeben möchte.
Widerruf der monatlichen Abgabe
Bei Abgabe einer
Monatsmeldung in Meldezeiträumen ab 01.07.2010 kann der Benutzer die monatliche
Abgabe seiner Zusammenfassenden Meldung widerru
[...]


---

## Abschöpfung von Unterkasse an Hauptkasse (Einreichung bei Unterkassen)

Abschöpfung von Unterkasse an Hauptkasse (Einreichung bei Unterkassen)
Es gibt den
SPA 356 - Aut. Abschöpfung von Unterks an Hauptks
. Ist
dieser auf Ja gestellt, werden beim Kassenabschluss einer Unterkasse automatisch
alle Bestände an die zugeordnete Hauptkasse übergeben (so wie sie in der
Kassenverwaltung zugeordnet ist). Diese Funktion ermöglicht es, ohne Zählung
Barmittel an eine andere Kassenebene zu überführen.
Eine Zählung erfolgt dann dort.
Hierbei wird gleichzeitig zur Fortschreibung der
Einreichungssumme bei der Unterkasse auch die Übernahmesumme der Hauptkasse
fortgeschrieben
Diese Weiterreichung an die übergeordnete Kassenebene
ist auch durch die Belegart Abschöpfung bei Unterkassen möglich. Diese manuelle
Funktion bewirkt dabei, dass die angegebene Abschöpfungssumme einer Unterkasse
an seine zugeordnete Hauptkasse übergeben wird.

---

## Abstimmung Kasse – FiBu

Abstimmung Kasse – FiBu
Die Abstimmung Kasse – FiBu wird durch den
Minimalismus auf der Kassenseite erschwert. Der Kassenabschluss beschränkt sich
darauf, einen einzigen automatischen Einreichungsbeleg für die Zahlungsmittel zu
erstellen. Fibu-seitig können hier bis zu 8 Belege entstehen (4 Zahlungsarten
jeweils Soll und Haben). Die oben angesprochene Bargeldumbuchung ist für das
Kassenbuch nicht relevant, weil nur die Einreichung den Kassenbestand
tatsächlich mindert. Also hat sich die Kasse hierfür einen internen Beleg ganz
gespart.
Durch die automatische Verteilung der Zahlungsmittel
auf die vorgesehenen Konten steht ggf. in einem Einreichungsbeleg der Kasse, was
in der Fibu nicht nur auf mehrere Belege, sondern auch auf verschiedene Konten
verteilt wird.
Zum Beispiel wird eine Sicherheitslücke offenbar:
Abschöpfung UK an HK: eine einzige Umbuchung des Kassensolls an die Hauptkasse
(Kassenbeleg). Bei SPA autom. Verteilung Zahlungsmittel auf Konten wird stets
nur der Kassenumsatz umgebucht (Fibu). Hat die Kasse aus welchem Grund auch
immer einen Vortrag gehabt, dann haben jetzt Kasse und Fibu eine
Abstimmungsdifferenz.

---

## Anschluss Fibu:

Anschluss Fibu:
Die RFS Schnittstelle kann wahlweise mit oder ohne
Fibu-Anschluss betrieben werden. Bei ‚Ja’ wird die Fibu als zusätzliche
Verwaltung ausstehender Zahlungsvorgänge herangezogen.

---

## Artikelumbuchung

Artikelumbuchung
Artikelumbuchungen werden unter dem Direktsprung [ARU]
verwaltet. Sie werden als Vorgänge gespeichert. Referenz-ERP stellt folgende
Bearbeitungsfunktionen zur Verfügung:
•
Artikelumbuchung F
8
Erfassung einer neuen Artikelumbuchung
•
Erstdruck
F10
Erstdruck einer Artikelumbuchung.
•
Formulardruck
Wiederholungsdruck
•
Korrektur
F5
Korrektur einer Artikelumbuchung
•
Vorschau
F11
Druckvorschau
•
Stornieren
F7
Stornieren (Löschen) der Artikelumbuchung
•
Freigabe/Sperren
Freigabe / Sperren für weitere Bearbeitung
Siehe auch Erfassung des
Positionsteils bei Umbuchungen

---

## Private Varianten und SQL-Texte

Private Varianten und SQL-Texte
Auswahllisten sind eine in Referenz-ERP integrierte
Technologie um verschiedene Anwendungen zur Auswahl von Belegen, Kunden,
Anschriften Buchungen etc. in Listenform anzuzeigen. Eine Reihe von Anwendungen
sind vom System vorgegeben. Innerhalb einer Anwendung kann es verschieden
Varianten geben. Als Beispiel hierfür wird die Anwendung Kundenstamm
(Direktsprung
[KU]
) verwendet:
Von den Varianten können private Ableitungen erstellt
werden, die dann abgeänderte Inhalte enthalten. Private Ableitungen haben immer
den Nachteil, dass Änderungen von Branchen-ERP nach einem Programmupdate dort nicht mit
enthalten sind.
Um eine private Ableitung einer bestehenden Variante
zu erstellen, startet man die Anwendung und wählt dort die Variante aus, die
privatisiert werden soll. Dann führt man die Funktion „
private Variante
“
Strg+F2
aus. Mit dieser Funktion können
später auch schon existierende Varianten bearbeitet werden. Dann stehen
zusätzlich noch die Funktionen „
Bearbeiten
“
F5
und „
Löschen
“
F7
zur Verfügung.
Nach ausführen der Funktion „Private Ableitung“ öffnet
sich ein weiterer Dialog:
Beschreibung
Bezeichnung
Die
      Bezeichnung, wie sie später in der Anwendung zu sehen ist.
Sortierung
Hier
      kann man angeben, an welcher Stelle in der Varianten-Auswahl diese private
      Variante stehen soll. Vorbelegt wird der Wert immer so, dass die private
      Variante am Ende einsortiert wird,
Markieren erlaubt
Wenn
      hier ein
Nein
eingetragen wird, dann ist das Markieren einzelner
      Zeilen nicht mehr möglich und es gilt für alle Funktionen immer die
      Gesamtauswahl.
Option Box
Sollen in dieser Variante andere
      Funktionen angeboten werden, so kann man eine eigen Optionbox hinterlegen,
      in der man die Funktionen zur Verfügung stellen kann.
Funktionen:
Beschreibung
Speichern
Speichert die
      Änderungen.
Zugehöriger SQL-Text
Hier
      kann der SQL-Text bearbeitet werden. Eine Liste der Schlüsselwörter findet
[...]


---

## Automation/Aufgabenplaner

Automation/Aufgabenplaner
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datenübernahme
Direktsprung
[DUEB]
Im Pfleger, in dem man die Schnittstelle für die
Datenübernahme definiert, existiert eine Funktion „Aufgabenplaner für
Datenübernahme“. Der
Aufgabenplaner
erstellt
für die Windows-Aufgabenplanung einen Eintrag. Voraussetzung dafür, dass der
Auftrag zu der angegebenen Zeit ausgeführt wird, ist daher, dass der Rechner,
auf dem dieser Job erstellt wurde zu dem Zeitpunkt läuft und der Anwender
angemeldet ist – der Rechner kann natürlich trotzdem gesperrt sein.
Feld
Bedeutung
Name
      der Datenübernahme
Der
      Name der Aufgabe ist die Bezeichnung der Datenübernahme-Schnittstelle.
      Dieser Name erscheint in Aufgabenplanung von Windows im Ordner Referenz-ERP.
      Damit dieser Name auf jeden Fall eindeutig ist, wird noch „Task 123“ an
      den Text angerhängt, wobei die Nummer der Datenübernahme ist (die
      DuebId).
Planungsintervall
•
einmalig
•
täglich
•
wöchentlich
•
monatlich
•
stündlich
•
alle 5
      Minuten
•
alle 10
      Minuten
•
alle 15
      Minuten
•
alle 30
      Minuten
Startzeit
Hier
      wird angegeben, an welchem Tag und um wieviel Uhr diese Aufgabe ausgeführt
      werden soll.
Erweiterte Optionen
Unter den erweiterten Optionen kann
      noch der Wochentag ausgewählt werden, an dem die Aufgabe laufen soll.
      Diese Option steht nur zur Verfügung, wenn als Planungsintervall
      „wöchentlich“ oder „monatlich“ ausgewählt wurde.
Beim Speichern der Daten wird dann eine Batch-Datei
ins Bin-Verzeichnis geschrieben und eine Aufgabe angelegt. Der Name der
Batchdatei setzt sich aus dem Namen und der Ident der Schnittstellendefinition
zusammen. Pro Schnittstellendefinition kann nur eine Aufgabe angelegt werden. Es
erscheint folgender Dialog, in dem man kontrollieren kann, ob das Anlegen der
Aufgabe funktioniert hat.
Anschließend findet man diese Aufgabe in der
Aufgabenplanung
von Windows in der Planungsbibliothek
[...]


---

## Automatische Belege zur Abstimmung Kasse – Fibu

Automatische Belege zur Abstimmung Kasse – Fibu
Per Update bzw. Kassenreorganisation können im
Kassensystem maschinelle Belege hinzugefügt werden. In den allermeisten Fällen
hängen diese mit automatischen Abschöpfungen im Rahmen von Kassenabschlüssen
zusammen.
Wenn etwa Zahlungsmittel als mit dem Kassenabschluss
automatisch abzuschöpfen eingestellt waren, so wurde dafür gesorgt, dass im
Vortrag der folgenden Kassensitzung diese Zahlungsmittel heraus gerechnet
wurden. Gleichzeitig wurde an die Fibu ein Buchungsauftrag übergeben, die
Zahlungsmittel vom Kassenkonto auf das eingerichtete Konto umzubuchen. An dem
Verfahren ist nichts auszusetzen: die Kassenbelege spiegeln die Vorgänge an der
Kasse richtig wieder, der Kassenbericht wird korrekt fortgeschrieben, in der
Fibu werden Entnahmen beim Abschluss auf die richtigen Konten weiter geleitet.
Es gibt somit Fibu Belege, zu denen es keine korrespondierenden Kassenbelege
geben muss.
Wird etwa an der Kasse eine Einreichung vorgenommen,
so ist damit eine entsprechende Fibu Buchung verbunden. Nun gibt es durchaus
Einrichtungen des Kontenrahmens, die auf eine detaillierte Aufschlüsselung
verzichten. Statt auf ein Transitkonto umzubuchen verbleibt das Geld auf dem
Kassenkonto. In diesem Fall gibt es einen Einreichungsbeleg in der Kasse, ohne
dass es einen korrespondierenden Fibu Beleg geben muss.
Die Tatsache, dass es auf beiden Seiten Belege geben
kann, zu denen man auf der Gegenseite keine Entsprechung findet, macht die
Abstimmung der Kasse mit der Fibu nicht eben leichter. Insbesondere kann es
keine technische „Auszifferungshilfe“ geben, die allein durch Belegabgleich
mögliche Problemfälle erkennen kann.
Ein zweites Problem ergab sich im Zusammenhang mit der
Kassenreorganisation. Da etwa für automatische Abschöpfungen keine Belege
existieren mussten, konnte man wohl die Umsätze je Sitzung aus den Belegen
heraus verifizieren, nicht aber den Vortrag in die Folgesitzung.
Daher ist das Verfahren derart g
[...]


---

## Automatisierung der Erstellung von Bestandsbuchungen

Automatisierung der Erstellung
von Bestandsbuchungen
Da es vorkommen kann, dass die letzten
Ein-/Ausgangsbuchungen des Tages auf einen Zeitpunkt fallen, zu dem die
Buchhaltung nicht mehr besetzt ist, um die Bestandsbuchungen vorzunehmen kann
der Wunsch danach bestehen, dies zu automatisieren.
Mit Hilfe eines Eintrags in die Tabelle „Datenstrom“
ist die Erstellung dieser Belege durch den Mandantenserver möglich. Dieser
Eintrag kann wiederum in einem Event geschehen.
INSERT INTO
DATENSTROM
(
ds_status,
BedienerId,
DS_DSC,
DS_Id,
DS_Parameter,
ds_RefText
)
VALUES
(
0,
(select first Bedienerid from bedienerstamm where bedienername like
'%MAND%'),
12,
amic_func_dbxident('Datenstrom', 0),
'^CS LVSPermInv_BelegCreator',
'Erstellung PIV-Belege'
);

---

## Bedienung

Bedienung
Alle Aktionen, die den Status eines Mitgliedskontos
direkt verändern sollen, erfolgen auf der im Folgenden beschriebenen
Bearbeitungs- und Ansichtsmaske.
Da es sich bei den im Folgenden beschriebenen Aktionen
um buchhalterisch relevante Vorgänge handelt, ist eine Korrektur über
Veränderung einmal gespeicherter (gebuchter) Daten grundsätzlich nicht möglich.
Falscheingaben sind durch eine entsprechende Korrektur / Stornierung (
Vorzeichen ) zu berichtigen.
Mit dem
Steuerparameter 843
kann die Vorbelegung für die zu
zeichnenden Anteile eingestellt werden. Die Standardeinstellung ist 1.

---

## Beispielablauf bzw. Beispielbuchungen

Beispielablauf bzw. Beispielbuchungen
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[
FIBE
]
Die Erfassung eines Wechsels in die Finanzbuchhaltung
erfolgt über die Belegerfassung. Dort wählt man die Belegart
WE (
Wechsel
erfassen)
aus. Als Besitzwechsel stellt er eine Forderung für den
jeweiligen Remittenten dar. Wir als Remittent buchen daher:
Besitzwechsel an Kunde
oder
Lieferant an Schuldwechsel
Da ein Wechsel im Wirtschaftsleben als Zahlungs- bzw.
als Kreditmittel Verwendung findet, wird er auch vom Programm ähnlich wie ein
Zahlungsbeleg behandelt. Man gelangt somit wie unter ZA auch direkt in die
OP-Verwaltung und kann dort die mit dem Wechsel beglichenen OPs direkt
ausziffern.
In der OP-Verwaltung
[OPV]
und
Konteninformation
[KOI]
steht der Wechsel als Summe im Infofenster.

---

## Beispiel AR Ausgangsrechnung

Beispiel AR Ausgangsrechnung
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Erfassung
Der Belegkreis dient der Erfassung
von Ausgangsrechnungen, die lediglich finanzbuchhalterisch gebucht werden
sollen. Diese Buchungen haben keinen Einfluss auf die Warenwirtschaft. Bei
angeschlossener Warenwirtschaft handelt es sich dann in der Regel um
Kostenrechnungen, in die die Daten einfließen sollen.
Es können folgende Daten erfasst werden.
Belegdatum
Hierbei handelt es sich um das
Belegdatum der Ausgangsrechnung. Das Feld ist vorbelegt mit dem Tagesdatum, kann
jedoch überschrieben werden. Für das Belegdatum spielen drei Einrichterparameter
eine Rolle:
1.
Belegdatum und Text löschen
Das Belegdatum wird beim ersten Einstieg mit dem
Tagesdatum bzw. – falls das Tagesdatum nicht in der aktiven Periode liegt - dem
Enddatum der aktiven Periode vorbelegt. Wenn dieser Einrichterparameter auf JA
steht, wird das Belegdatum bei jedem Datensatz so vorbelegt.
2.
Vorbel. Belegdat 0=Tagesdatum; 1-…=Tage zurück; -1=leer
Wenn das Belegdatum
vorbelegt werden soll (s.o.)  dann kann man hier noch genauer definieren,
nach welcher Regel dies geschehen soll.
3.
Belegdatum mit Periode prüfen?
Man kann hier hinterlegen, wie nach der
Eingabe des Belegdatums die Prüfung mit der zugeordneten Periode zu erfolgen
hat:
0 = Kein Test.
1 (Test und Warnung)= Testet, ob das Belegdatum in
der Periode liegt und gibt ggf. eine entsprechende Meldung aus. Man kann
weiterarbeiten.
2 (Test und Fehler) = Testet, ob das Belegdatum in der
Periode liegt und erlaubt das Weiterarbeiten nur, wenn das Datum in der aktiver
Periode liegt.
3 (Test Jahr und Warnung)= Testet, ob das Belegdatum in dem
Jahr liegt und gibt ggf. eine Meldung aus. Man kann trotz Meldung
weiterarbeiten.
4 (Test Jahr und Fehler)= Testet, ob das Belegdatum in dem
Jahr liegt. Weiterarbeiten ist nur dann möglich, wenn das Datum im Jahr
liegt
Belegkreisnummer
Die Ausgangsrechnungen
werden über einen B
[...]


---

## Beispiel zum Anlegen einer Arbeitsregel

Beispiel zum Anlegen einer Arbeitsregel
In diesem Beispiel aus der Praxis soll folgende
organisatorische Anforderung umgesetzt werden: Es soll sichergestellt sein, dass
Fremdwährungsbelege stets zu tagesaktuellen Kursen gerechnet werden. Im
Unternehmen ist ein Mitarbeiter für die Pflege der Kurse zuständig. Nicht
akzeptabel ist dabei, dass Rechnungen erst danach erfasst werden dürfen.
Ich benutze hier die Regeln 10 und 11.
Regel 10
ist die Startregel, die unter FRZ
eingetragen wird. Sie besagt inhaltlich: der Fremdwährungskurs stimmt mit dem
Kurs überein, der exakt für das Belegdatum hinterlegt ist. Belege ohne
Fremdwährung gelten immer als regelkonform. In dieser Regel sind keine Sperren
etc. eingebaut. Die Nachfolgeregel wird mit der privaten Prozedur p_ARegel_Kurs
bestimmt.
Arbeitsregel: 10
Name:
Währungskontrolle
Kurzbezeichnung:WKO
Register Nachfolgeregel
Typ:
Datenbank Funktion
SQL / Funktion: p_ARegel_Kurs
Regel 11
ist der Fehlerzustand: Der Kurs
entspricht nicht dem Tageskurs. Auch in Regel 11 wird die Prozedur p_ARegel_Kurs
zur Bestimmung der Folgeregel aktiviert. Bei Belegkorrektur wird dann ebenfalls
auf  den korrekten Kurs geprüft und ggf. wieder Regel 10 zugeordnet.
In Regel 11 schaltet man diverse Sperren ein, die das Weiterverarbeiten des
Vorgangs verhindern.
Arbeitsregel: 11
Name: Währungskurs
inkorrekt
Kurzbezeichnung: wk err
Register Sperren
Druck – immer
sperren
Fibu-Übertrag – immer sperren
Umwandlung – immer
sperren
Register Nachfolgeregel
Typ: Datenbank Funktion
SQL / Funktion:
p_ARegel_Kurs
Nachfolgende Funktion ermittelt die korrekte
Folgeregel ( 10 oder 11 )
-- private Datenbankfunktion zur
Ermittlung einer Nachfolgeregel
--    angelegt am :
dd.mm.yyyy  für Regel 10 und 11  : Währungskontrolle
--
--  Regel 10 = Währung ist
ok
--  Regel 11 = Währung ist nicht
ok
CREATE FUNCTION
p_ARegel_Kurs
(
in
in_V_ID         integer ,  -- V_Id
des Vorgangs
in in_REGEL_NUMMER integer
,  -- Nummer der aktiven Regel
in in_BEDIEN
[...]


---

## Belegerfassung

Beleg
erfassung
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Die Belege können über diverse Wege in die
Finanzbuchhaltung gelangen:
- Automatische Übergabe aus der Warenwirtschaft
- Automatische Buchung (Zahlungsbelege / Mahngebühren
/ …)
- Diverse Importschnittstellen
- Manuelle Erfassung in der Finanzbuchhaltung
Die in der Belegerfassung erfassten Belege werden
sofort
vorläufig
verbucht, d.h., sie befinden sich auf den Erlös- und
Aufwandskonten, den OP-Konten, etc. Der Status der Vorläufigkeit bedeutet jedoch
auch, dass sie noch bearbeitet werden können (zu Ausnahmen siehe
OP-Verrechnung). Erst mit dem Vorgang "Buchen" werden die Belege
endgültig
verbucht.
Für Eingangsrechnungen, Eingangsgutschriften und
Sonstige Belege besteht die Möglichkeit zusätzlich ein Eingangsdatum zu erfassen
(siehe
Vorsteuerabzug
).
Das Feld
eRechnung
zeigt falls vorhanden die
ID, der zugrunde liegenden eRechnung.
Eine Erfassung der eRechnung-ID ist auf diesem Wege
nicht
möglich.

---

## Bereichsaufteilung

Bereichsaufteilung
In der Basis-DB ist eine Aufteilung nach Bereichen
vorgenommen worden.
Die Nummern sind identisch mit den Formularklassen.
Einteilung:
Nummer
100
      - 1999
Vorgangsabwicklung
  WaWi
111
      -   115
Ausnahme für Listen
    (F4)
2000
      - 2999
Fibuformulare
3000
      - 3999
Modul Kontrakte
5000
      - 5999
Interne Belege WaWi
9999
Einspielformular

---

## Überschriftszeile

Überschriftszeile
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Überschriftszeile
Direktsprung
[CCD]
Bei Überschriftszeilen wird lediglich die Bezeichnung
in der ersten Spalte der Auswertung angezeigt. Dies dient zur Abgrenzung von
Bereichen.
Davor neue Seite
und
Zeile
hervorheben
sowie
Schriftart
und
Schrift-/Hintergrundfarbe
dienen zur optischen Abgrenzung im
mitgelieferten Crystal Report.
Dabei bedeutet:
Davor neue Seite
Bevor diese Zeile
gedruckt wird, wird ein Seitenwechsel erzwungen.
Zeile hervorheben
Wenn man hier Ja
einträgt, wird die Schriftfarbe mit 0/0/0 und die Hintergrundfarbe mit
233/233/233 ( Grau ) vorbelegt. Zusätzlich wird diese Zeile mit einem
horizontalen Linien umrandet.
Schriftart
Die Schriftart,
Schriftschnitt und Schriftgrad können hier festgelegt werden.
Schrift-/Hintergrundfarbe
Die Zeile
kann beliebig farblich gestaltet werden.
In diesem Beispiel ist bei der Überschrift
„Erfolgsdaten“ individuell formatiert und bei der Zeile „2. Personalaufwand in %
zum Umsatz“ für
Zeile hervorheben
JA eingetragen.

---

## Übertragung Einlage

Übertragung Einlage
Die Übertragung der Einlage erfolgt nicht zeitgleich
mit der Übertragung der Anteile. Soll die Einlage übertragen werden, ist die
Übertragsposition durch Doppelklick zu aktivieren.
Es entstehen durch die Übertragung der Einlage die
oben beschriebenen Buchungen:

---

## Besonderheiten

Besonderheiten
Besonderheiten bei den Personenkonten
Unter den Fibumerkmalen kann man eine abweichende
Kontonummer für den DATEV-Export angeben. Diese wird dann an Stelle der
Kontonummer des Personenkontos für die Übergabe der Stamm- und der
Bewegungsdaten verwendet. Dies ist immer dann Sinnvoll bzw. sogar unumgänglich,
wenn man die Personenkonten so eingerichtet hat, dass sie nicht den
Anforderungen der DATEV entsprechen.
Besonderheiten im Sachkontenstamm
Im Sachkontenstamm existieren zwei für die DATEV
relevante Felder:
Abweichende
DATEV-
Kontonummer:
Wenn es vorkommt, dass man
bereits mit einem Kontenrahmen gearbeitet hat und sich irgendwann entschließt
die DATEV-Schnittstelle zu verwenden, hat man die Schwierigkeit, dass nur die
DATEV-Kontenrahmen erlaubt sind.  Dann hatte man bisher nur die Möglichkeit
die Fibu neu aufzusetzen oder zu versuchen, während des laufenden Betriebs die
Sachkonten für bestehende Belege zu ändern.
Um hier ein einfacheres
Verfahren anzubieten, gibt es im Sachkontenstamm jetzt ein weiteres Feld
"Abweichendes DATEV-Konto". Steht hier eine 0, wird nach wie vor die Kontonummer
des Sachkontos verwendet. Steht hier eine abweichende Nummer, wird diese Nummer
bei der Übertragung in die Datei geschrieben.
DATEV
Automatik:
Bei der DATEV existieren sogenannte
Automatikkonten. Für diese Konten wird von der DATEV automatisch die Steuer
errechnet. Es darf also keine Steuer von der Schnittstelle übertragen werden. Um
dies der Schnittstelle mitzuteilen gibt es das Feld DATEV Automatik, das für
diese Konten auf
Ja
gesetzt werden muss. Eine Liste der Automatikkonten
kann Ihnen der Steuerberater zur Verfügung  stellen. In den ausgelieferten
Kontenplänen SKR03 und SKR04 sind die entsprechenden Konten bereits korrekt
gekennzeichnet.
HINWEIS:
Treten zwischen den Steuerkonten beim
Steuerberater und denen in Referenz-ERP Differenzen auf, so liegt dies mit großer
Wahrscheinlichkeit an falsch hinterlegten Automatikkennzeichen!
Besonderheiten St
[...]


---

## Bestandsbuchungen Vorgangsklasse 5055

Bestandsbuchungen Vorgangsklasse 5055
Es ist sicherzustellen, dass nach dem Zeitpunkt der
Erstellung dieses Beleges keine weiteren Zu- oder Abgangsbuchungen an dem
aktuellen Tag erstellt werden.
Hinweis:
Voraussetzung für die Anwendung dieser
Differenzkorrektur ist, dass alle offenen Belege zum Zeitpunkt der Inventur
gebucht wurden. Eine spätere Erfassung oder Veränderung von Lieferungen vor dem
Inventurzeitpunkt ist nicht erlaubt.
Ausnahmen bedeuten eine definierte Handlungsanweisung:
1.
Ware wird zurückgeliefert – Beleg darf storniert / die Position darf gelöscht
werden, wenn die Menge der Rücklieferung mit der Belegmenge identisch ist.
2.
Ware wird teilweise zurückgeliefert – Die Position darf korrigiert werden, wenn
die Menge der Rücklieferung mit der Änderung der Belegmenge identisch ist.
3.
Es wurde eine falsche Menge im Beleg eingetragen – Die Position darf nur
korrigiert werden, wenn zugleich die zusammenhängende Zählung in der Inventur
korrigiert wurde. Alternativ muss die Ware nach Korrektur des Beleges neu
gezählt werden.
4.
Es muss ein Beleg nach der Zählung erfasst werden – Die zum erfassten Beleg
gehörenden Artikel müssen in der Inventurzählung entsprechend korrigiert oder
erneut gezählt werden.
Hinweis:
Es ist dringend empfohlen, dass Artikel nur mit Partie
oder komplett ohne Partie geführt werden. Differenzmengenerfassungen für Artikel
ohne Partieangabe werden zu Fehlinterpretationen des Systems führen, wenn es zu
dem Artikel parallel Partiebestände gibt!
Nähere Informationen zum technischen Ablauf von
Buchungen von Artikeln und Partien entnehmen Sie dem Abschnitt
techn. Informationen
Buchungen
Mengenbuchung
Die erfasste Menge wird dem zum Zeitpunkt der
Erfassung festgestellten Soll-Bestand gegenübergestellt.
Wertbuchung
In Abhängigkeit des
SPA 1072 – Bewertungsverhalten permanente Inventur
wird
die Inventur an dieser Stelle bewertet (
0
) oder die Bewertung wird erst am
Jahresende (
1
) vorgenommen werden.
Die Ware wi
[...]


---

## Bestellanfrage

Bestellanfrage
Die Vorgangsklasse „Bestellanfrage“ dient zur
Erfassung, Bearbeitung, Verwaltung und Druck von Bestellanfragen.
Bestellanfragen werden als Vorgang gespeichert, auf
sie kann in Nachfolgevorgängen zugegriffen werden; Bestandsbuchungen nach Menge
und Wert erfolgen nicht. Referenz-ERP stellt folgende Bearbeitungsfunktionen zur
Verfügung:
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
Erstdruck eines Vorgangs
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
Freigabe/Sperren
Freigabe / Sperren für weitere
      Bearbeitung
Bestellung aus Anfrage
Umwandeln in eine
      Bestellung
E-LS aus Anfrage
Umwandeln in einen Eingangs-
      Lieferschein
E-Rech. aus Anfrage
Umwandeln in eine Eingangs -
      Rechnung
Sammelbest. aus Anfragen
Umwandeln mehrerer Vorgänge in eine
      Bestellung
Sammel-ELi aus Anfragen
Umwandeln mehrerer Vorgänge in einen
      Eingangs - Lieferschein
Sammel-ERe aus Anfragen
Umwandeln mehrerer Vorgänge in eine
      Eingangs -  Rechnung
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

## Buchen

Buchen
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Buchungen Fibu
Direktsprung
[BUC]
Um nun die Belege endgültig in der Finanzbuchhaltung
festzuschreiben, müssen sie „gebucht“ werden.
Dazu dient der Menüpunkt „Buchungen Fibu“
(Direktsprung BUC) oder die
Einrichtung einer allgemeinen
Buchungsautomatik
:
Es kann nun entschieden werden, welche Belege verbucht
werden sollen. Entsprechend dieser Einstellung werden die Belege
zusammengestellt, verbucht und journalisiert:
•
Angabe des Zeitraumes, über den verbucht werden soll
•
Angabe, ob alle Belege im Zeitraum oder nur die des aktuellen
Bedieners
•
Selektion der Belege nach Warenwirtschaft, Finanzbuchhaltung oder
alle.
•
Eröffnungs- und Abschlussperioden grundsätzlich mitbuchen.
Wenn man den Buchungslauf startet, werden alle Belege,
die den angegebenen Kriterien entsprechen und bei denen das Kennzeichen „
Buchungssperre
“ nicht gesetzt
ist, gekennzeichnet, damit sie anschließend vom Mandantenserver verarbeitet
werden können. Je nach Organisation der EDV läuft er im Hintergrund mit, so dass
die technische Verbuchung zeitgleich abläuft, oder wird periodisch aktiviert. In
diesem Fall besteht eine zeitliche Differenz zwischen inhaltlicher und
technischer Verbuchung.
HINWEIS:
Wenn man auf die
Verarbeitung über den Mandantenserver verzichten will, kann man per
Einrichterparameter „Buchen ohne Mandantenserver“ das System so einstellen, dass
die Buchung direkt ausgeführt wird. Der Arbeitsplatz, auf dem das Buchen
gestartet wird, ist dann natürlich länger belastet.
Unabhängig davon, ob die Belege bereits vom
Mandantenserver verarbeitet wurden oder nicht, stehen sie nach diesem
Buchungslauf nicht mehr in der Primanota und können nicht mehr verändert
werden.
Wenn beim Buchen der Belege keine Probleme aufgetreten
sind, können die Journale gedruckt werden. In der Anwendung
Journal/Ereignisprotokoll
(Direktsprung
[JOUR]
) werden alle Journale aufgelistet. Zum Druck dieser Journale
stehen zum einen fest defini
[...]


---

## Buchungen Finanzbuchhaltung

Buchungen
Finanzbuchhaltung

---

## Buchungen in der Mitgliederverwaltung

Buchungen in der Mitgliederverwaltung
In der Anwendung GESEL stehen die Varianten
Warenrückvergütung und Warenrückvergütungsbuchungen zur Erstellung der
notwendigen  Buchungen zur Verfügung.

---

## Buchung in die FiBu

Buchung in die FiBu
Es gibt verschiedene Arten von Buchungen in die FiBu,
die nachfolgend näher beschrieben werden:
•
Vorgänge, die an der Tresenkasse / POS-Kasse erfasst werden, werden wie
normale Vorgänge verbucht, d.h. es erfolgt eine zweistufige Abarbeitung der
Vorgänge. Nach der Erfassung werden die Vorgänge über den Mandantenserver
endgültig in die Bestandsverwaltung integriert. Danach müssen die Vorgänge durch
die Funktion FiBu-Übertrag (z.B. in der Anwendung Gesamtbarverkauf, Variante
Liste der Barverkäufe) an die FiBu übertragen werden. Ihren endgültigen
FiBu-Status bekommen sie dann erst, wenn erneut der Mandantenserver gelaufen
ist. Die FiBu-Buchung erfolgt zwischen Kassenkonto aus der Kassenverwaltung und
Konto des Kunden (im Normalfall das Konto des Barverkaufskunden wie in den
Kasseneinstellungen hinterlegt; Ausnahme: man hat zur Erfassungszeit einen
anderen Kunden zugeordnet); d.h. nach dieser Buchung gilt dieser Vorgang als
automatisch beglichen. Neben dieser Buchung wird auch eine Buchung auf das
passender Steuerkonto sowie das zugeordnete Erlöskonto durchgeführt.
•
Finanzvorgänge wie Zahlungsmeldung, Geldeinzahlung (siehe Belegarten
10-20 von unten) werden nur gebucht, wenn der
SPA 333 - Aut. Buchung von Finanzvorg. in FiBu
auf Ja
gesetzt ist. Dann wird bei der Erfassung ein Eintrag in den Datenstrom erzeugt,
der beim nächsten Durchlauf des Mandantenservers einen FiBu-Eintrag erzeugt. Je
nach Belegart wird dann eine Buchung zwischen dem Kassenkonto aus der
Kassenverwaltung und einem entsprechenden Gegenkonto durchgeführt (Bei
Zahlungsmeldungen, Einzahlungen vom Kunden und Auszahlungen an Kunden handelt es
sich um das gewählte Kundenkonto; bei Abschöpfung an Bank handelt es sich um das
Verrechnungskonto der gewählten Bank; bei Geldentnahmen, Einzahlungen von
Kostenkonto handelt es sich um das gewählte Verrechnungskonto; bei
Geldübergaben, Geldübernahmen, Abschöpfung von Unterkasse an Hauptkasse um das
Kassenkonto der Gegenkas
[...]


---

## Buchungsdatum und Buchungsperioden

Buchungsdatum und Buchungsperioden
Referenz-ERP beinhaltet 2 Konzepte zur Wertstellung in der
Ware:
Konzept
Beschreibung
Lieferdatum
Für
      die Chronologie des Warenbuches ist das Lieferdatum relevant. Auch
      wenn  etwa das Rechnungsdatum vom Lieferdatum abweicht, findet man im
      Warenbuch die Rechnung unter dem Lieferdatum. Über den Lieferbezug wird
      etwa die Fortschreibung des gewogenen Einkaufspreises organisiert.
      Stichtags-bezogene Lagerbestände werden stets über das Lieferdatum
      ermittelt.
Buchungsperioden
Zusätzlich zum Lieferdatum wird die
      Buchungsperiode eines Beleges geführt. Standardmäßig wird bei der
      Vorgangserfassung die Buchungsperiode passend zum Lieferdatum vorbelegt.
      Für Ausnahmefälle lässt Referenz-ERP zu, dass Lieferdatum und Buchungsperiode
      abweichen. Das kann etwa dann notwendig sein, wenn ein Lieferbeleg
      nacherfasst wird, obwohl für die zum Lieferdatum passende Periode bereits
      Buchungsschluss ist. Es soll aber die absolute Ausnahme bleiben, denn man
      macht sich die Abstimmung der Ware nur schwer, weil die gleichen Zeiträume
      nach Lieferdatum und nach Buchungsperioden betrachtet unterschiedliche
      Ergebnisse liefern.
Über
      einen Jahreswechsel hinaus ist die Abweichung grundsätzlich unzulässig,
      weil eine ordnungsgemäße Durchführung einer Jahreswechselinventur nicht
      gegeben ist. Entsprechendes gilt für unterjährige Zwischeninventuren, die
      per ultimo einer Buchungsperiode durchgeführt werden: Über den
      Inventurstichtag hinweg dürfen keine Abweichungen von Lieferdatum und
      Periode vorkommen.

---

## Buchungslauf

Buchungslauf
Bei jeder neuen DTA-Erstellung wird eine
Buchungslaufnummer generiert. Diese wird auf der Banksammelliste
ausgegeben.

---

## Buchungssatz XML Import

Buchungssatz XML Import
Über diese Schnittstelle können Buchungssätze, die in
einer
XML
Datei
enthalten sind, importiert werden. Die Daten werden in die Tabelle
FIBUIMPORT
geschrieben.
Auswahlliste
Die einzuspielenden und eingespielten Dateien werden
in der Tabelle Buchungssatzimport gespeichert, diese Dateien können unter
[BSSIX] oder Finanzbuchhaltung -> Abschlussarbeiten ->
DATEV/Import/Export
-> Buchungssatz XML Import  angezeigt
werden.
In der Variante „Buchungssatzimport“ können
importierte Dateien gelöscht werden. Das Löschen hier hat keinen Einfluss auf
bereits erfolgreich in die Finanzbuchhaltung eingespielte Belege oder Daten die
noch im FIBUIMPORT stehen.
Des Weiteren wird angezeigt, ob eine Datei erfolgreich
in den FIBUIMPORT eingespielt wurde. Ist eine Datei nicht erfolgreich in die
FIBUIMPORT eingespielt worden, da z.B. die Kontonummer oder die Gegenkontonummer
nicht im System eingerichtet sind, wird beim nächsten Importlauf noch einmal
versucht diese Datei einzuspielen.
Um einen Import durchzuführen, klicken Sie bitte auf
Buchungssatz Import XML
F9
.
Bereitstellung der XML Datei
Die zu importierende Datei mit den Buchungsätzen muss
auf dem Rechner vorhanden sein, damit diese in die Tabelle Buchungssatzimport
gespeichert werden können.
Ist die Datei nicht auf dem Rechner vorhanden, so kann
diese per VBA, VBS Skript geladen und gespeichert werden, oder per Explorer
kopiert werden.
Den Namen des VBA oder VBS Skriptes wird in den
Einrichterparameter
der Maske
hinterlegt.
Privates VBS oder VBA
Ein Beispiel für das Laden und Speichern einer Datei
von einem FTP Server finden Sie unter dem Direktsprung [VBA]. Der Name des VBA
Skriptes lautet AMIC_FTP_LEDGERIMPORT. Als Parameter werden folgende Werte
übergeben:
1. /GUID=Die ID des Import ( Siehe Auswahlliste )
2. /File=Der Dateiname oder Dateipfad. Bei Pfadangabe
werden alle nicht eingespielten XML-Dateien Importiert.
Fehlerbehandlung im Skript:
Um der Import Schnittstelle mitzuteilen, das
[...]


---

## Buchungstyp (KtrBuchTyp)

Buchungstyp (KtrBuchTyp)
Wird eine Ware gebucht, so wirkt diese Buchung auf
einen bestimmten Bestand.
Um unterscheiden zu können, auf welche Bestände eine
Buchung wirken soll, gibt es den Buchungstyp.
Der Buchungstyp findet sich in der Tabelle
Warenbewegung als Feld KtrBuchTyp.
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
Buchungstyp im Kontrakt
Der Buchungstyp eines Kontrakts bestimmt Quelle und
Ziel einer Buchung (z.B. Eigenware zu Fremdware). Eine nachträgliche Änderung
des Buchungstyps ist deshalb nicht möglich, da damit alle bereits erfolgten
Buchungen und Bestände im Zusammenhang mit diesem Kontrakt ebenfalls geändert
werden müssten, die Zusammenhänge aber nicht überall ersichtlich sind.

---

## Buchungstypen

Buchungstypen
Wird eine Ware gebucht, so wirkt diese Buchung auf
einen bestimmten Bestand.
Um unterscheiden zu können, auf welche Bestände eine
Buchung wirken soll, gibt es den Buchungstyp.
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
Buchungstyp eines Kontrakts
Beim Vorverkauf und Voreinkauf wurde bei der Erfassung
stets ein Kontrakt (oder Sammelkontrakt) angelegt – die Anlage des Kontraktes
war verbindlich. Mit Einführung der Buchungstypen Einlagerung und
Kommission  kann man nun optional auch auf die  Führung solcher
Bestandskontrakte verzichten. Insbesondere im Kommissionsgeschäft kann damit auf
eine Vielzahl von zusätzlichen Kontrakten verzichtet werden. In den
Steuerungsparametern findet man unter den Nummern 96,97 und 99 die Einstellung
zu Kontraktbehandlung für die Buchungstypen Vorverkauf, Voreinkauf und
Kommission. Der Buchungstyp Einlagerung wird derzeit immer ohne
Kontraktbuchführung abgewickelt.
Es wird in einer späteren Version auch möglich sein,
normale Einkaufs und Verkaufskontrakte für die Bestandsführung der Vorverkäufe,
Voreinkäufe und Kommissionen heranzuziehen. Hierfür wurde im Kontraktstamm
eine Kennzeichnung geschaffen ( KtrBuchTyp!). In unseren Auswertungen und
Auswahllisten wurde die Selektion  auch nach diesem Kennzeichen schon
integriert.

---

## BWG-Schnittstelle

BWG-Schnittstelle
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Funktion
F9
Import Starten
Funktion
F4
Importdatei lesen
Direktsprung
[FIIM]
Bei dieser Schnittstelle handelt es sich um den Import
der Lohndaten aus der BWG-Software. Es handelt sich hierbei um reine
Sachkontenbuchungen.
Beim Einspielen der Daten wird die Periode anhand des
Belegdatums bestimmt.
Sind für das Gegenkonto in den Stammdaten die
Steuerklasse und der Steuerschlüssel hinterlegt und bei „Sperre Steuerschlüssel“
der Wert „Fest“ hinterlegt, so werden diese Werte für diesen Buchungssatz
herangezogen und die Steuer wird errechnet. Dabei hängt es von der Steuerklasse
ab, ob der Betrag in der Exportdatei als Nettobetrag (bei Steuerklasse 1 oder
101) oder als Bruttobetrag (bei Steuerklasse 2 oder 102) interpretiert wird.
Beispiel:
Für das Konto 1755 ist die Steuerklasse 2
hinterlegt.  In der Importdatei steht der Betrag 14,06 €. Es wird folgender
Buchungssatz gebildet:
4100
an
1755
14,06
12,12
1775
1.94
Satzaufbau der Datei
Jede Zeile ist 128 Bytes lang und endet mit CR/LF. Die
Daten stehen mit einer festen Länge hintereinander.
Stelle
Länge
Format
Bedeutung
1
8
Rechts/vorl. Null
Übergabekonto
9
15
Rechts/vorl. Null
Betrag Soll in Cent
24
15
Rechts/vorl. Null
Betrag Haben in Cent
39
8
Rechts/vorl. Null
Gegenkonto
47
8
TTMMJJJJ
Übergabedatum
55
10
Links
Kostenstelle
65
4
Rechts/vorl. Null
Personalnummer
69
11
Links
Projektnummer
80
8
Rechts/vorl. Null
Stunden
88
1
Rechts/vorl. Null
Sollhaben immer 1
89
38
Filler
127
2
CR/LF
Die Felder Personalnummer, Projektnummer und Stunden
werden nicht übernommen. Das Übergabedatum wird als Belegdatum verwendet.

---

## Checkliste Jahreswechsel

Checkliste Jahreswechsel
1.
Belegerfassung und Fibuübertrag abschließen.
2.
Evtl. Zinswesen abwickeln.
3.
alle Belege buchen und gegebenenfalls das Protokoll auf  Buchungsfehler
bzw. Übertragungsfehler hin kontrollieren. Der Mandantenserver muss laufen.
4.
Drucken der Journale
5.
Perioden überprüfen. Die Abschlussperiode des abzuschließenden Jahres muss
eröffnet sein.
6.
Gegebenenfalls das neue Jahr anlegen und die Eröffnungsperiode eröffnen.
7.
Auswertungen drucken bzw. anzeigen lassen:
- Umsatzsteuervoranmeldung
-
Bilanz
-GuV
- Summen und Saldenlisten
8.
Kontoblätter erstellen und evtl. drucken.
9.
Eventuell neuen Nummernkreis für die Jahreswechselbuchungen anlegen.
10.
Steuerkonten ausbuchen

---

## Datenübernahme-Schnittstelle

Datenübernahme-Schnittstelle
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datenübernahme
Direktsprung
[DUEB]
Diese Schnittstelle ist eine allgemeine technische
Lösung um Dateien gesichert einzulesen. In dieser Auswahlliste kann man die
Schnittstelle definieren und ausführen.
Einrichtung
Feld
Besonderheiten
Name
Dies
      ist die eindeutige Bezeichnung des Übernahmeverfahrens, über die dann auf
      die Definition zugegriffen wird.
Verzeichnisse
Es
      müssen vier Verzeichnisse eingetragen werden:
In:
Die einzulesenden Dateien
      werden in dieses Verzeichnis gestellt. Der Name der Dateien ist dabei
      nicht wichtig, da alle Dateien in dem Verzeichnis verarbeitet werden. Er
      kann aber unter „Eingrenzung“ näher definiert werden.
Run:
Wenn eine Datei in Arbeit ist,
      steht sie in diesem Verzeichnis.
Done:
Ist
die Verarbeitung
      Fehlerfrei abgelaufen, dann wird die Datei in dieses Verzeichnis
      verschoben.
Fail:
Im Fehlerfall kommt die Datei in
      dieses Verzeichnis.
Existieren die Verzeichnisse noch
      nicht, wird vom Programm versucht diese anzulegen.
Programm 1
Dieses Programm ist eine
      JPL-Funktion. Wenn man als Parameter %F angibt, so wird dort der Dateiname
      übergeben. Die Funktion muss den Wert 0 (S_OK) zurückliefern, wenn die
      Verarbeitung fehlerfrei war. Ein Wert größer 0 beendet das Einlesen aller
      Dateien, egal ob noch Dateien im
In-
Verzeichnis stehen oder nicht.
      Ein Wert kleiner 0 beendet nur das Einspielen der aktuellen
      Datei.
Von
      Branchen-ERP stehen mehrere Programme bereit, die hier per F3 ausgewählt werden
      können.
Programm 2
Eine
      zweite optionale Prozedur, die nur aufgerufen wird, wenn die Funktion
      unter Progamm 1 fehlerfrei ausgeführt wurde. Die Funktion muss den Wert 0
      (S_OK) zurückliefern, wenn die Verarbeitung fehlerfrei war. Ein Wert
      ungleich 0 bricht nur die Verarbeitung dieser Daten ab.
Prozedur
Für
      den
CSV-Import
und
[...]


---

## DATEV

DATEV
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datev-Export
In der Finanzbuchhaltung steht eine Schnittstelle zum
Export der Belege in die Daten-Programme FIBU und OPOS zur Verfügung. Um die
DATEV-Schnittstelle einsetzen zu können ist es erforderlich, dass man die
DATEV-Kontenrahmen SKR03 bzw. SKR04 oder einen davon abgeleiteten
(Kontonummernerweiterung) verwendet. In Referenz-ERP stehen zwei Skripte bereit, mit
deren Hilfe man den Kontenrahmen einspielen kann. Diese können über die
Direktsprünge SKR03 bzw. SKR04 aufgerufen werden. Ein nachträgliches Einspielen
- wenn bereits Belege erfasst worden sind - ist nicht möglich.
Bei Verwendung der DATEV-Schnittstelle ist darauf zu
achten, dass die Stammdaten (Sachkontenstamm und Steuersätze) von Referenz-ERP in
enger Zusammenarbeit mit dem Steuerberater eingerichtet werden. Dabei sind unter
anderem die Regeln der DATEV zur Vergabe der Kontonummern zu beachten. Mehr
Informationen sind weiter unten unter
DATEV – Firmenstamm
zu finden.
Der Ablauf ist ähnlich wie das schon vom Mahnwesen
bzw. automatischem Zahlungsverkehr bekannte Verfahren. Erst werden die Daten
zusammengestellt (
DATEV-Export erstellen
) und können
anschließend weiter verarbeitet werden (
Daten-Export bearbeiten
).
HINWEIS:
Die
bisher bekannten Formate OBE und KNE wurden von der DATEV zum Jahreswechsel
2017/2018 abgekündigt und werden ab diesem Zeitpunkt nicht mehr einzulesen
sein.

---

## DATEV-Export bearbeiten

DATEV-Export bearbeiten
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datev-Export bearbeiten
Direktsprung
[DATEV]
Hier stehen Funktionalitäten zur Verfügung:
Ansehen
: Eine Auswahlliste mit allen in
der DATEV-Datei enthaltener Belege wird geöffnet. Diese könnte z.B. als
zusätzliches Protokoll verwendet werden.
Löschen
: Es wird der Datensatz gelöscht
und die in dem Export enthaltenen Belege werden wieder als nicht in die DATEV
exportiert gekennzeichnet. Wurden die Daten bereits zum Steuerberater gesandt,
bleibt ein Vermerk bestehen, dass dieser Satz gelöscht wurde. Auch hier werden
die Daten als nicht übertragen gekennzeichnet, so dass die Belege beim nächsten
Erstellen wieder mit herangezogen werden.
Datei erstellen
: hier befindet sich die
Funktion, die die Daten in die Datei schreibt. Wird ein Datensatz ausgewählt,
der bereits übertragen wurde, wird man darauf hingewiesen. Bevor die Datei
erstellt wird, wird bei Übermittlung der Steuer über den DATEV-Steuerschlüssel
noch geprüft, ob bei den verwendeten Steuersätzen ein gültiger
DATEV-Steuerschlüssel eingetragen ist.
Wenn der SPA „
DATEV
Festschreibungskennzeichen
“ auf „Ohne Festschreibungskennzeichen“ steht,
wird dies über der Optionbox angezeigt.
Zusätzlich zum Export der Bewegungsdaten ist ein
Export der Kundendaten möglich. Wie und ob sie exportiert werden sollen, wird
hier eingestellt. Welche Daten über die Schnittstelle übermittelt werden sollen,
kann individuell
definiert
werden. Werden zu den
Bewegungsdaten auch Kundendaten exportiert, wird eine weitere Datei geschrieben.
Es müssen immer alle Dateien dem Steuerberater übermittelt werden.
Zu dem Export
existieren diverse Einrichtungsparameter:
DATEV-Steuerschlüssel
in Textfeld mit übergeben?
Steht dieser Parameter auf
Ja
wird
vor den Text im Beleg die Nummer des DATEV-Steuerschlüssels geschrieben. Dieser
muss für diesen Fall im Steuersatz hinterlegt sein.
Bei Eingangsrechnungen Referenznummer
übergeben?
Mit diesem Parameter w
[...]


---

## DATEV ASCII-Schnittstelle

DATEV ASCII-Schnittstelle
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Funktion
F9
Import Starten
Funktion
F4
Importdatei lesen
Diese Schnittstelle steht zur Verfügung, wenn eine
DATEV Lizenz vorhanden ist.
Es existiert im DATEV-Lohnprogramm die Möglichkeit
Daten im einfachen CSV-Format auszugeben. Dabei werden die Daten nicht in den
üblichen DATEV-Formaten
KNE
(Kontonummernerweiterung) bzw.
OBE
(Ordnungsbegriffserweiterung) geliefert, sonder in einem einfachen ASCII-Format.
Beim Einspielen der Daten wird die Periode anhand des
Belegdatums bestimmt.
Sind für das Gegenkonto in den Stammdaten die
Steuerklasse und der Steuerschlüssel hinterlegt und bei „Sperre Steuerschlüssel“
der Wert „Fest“ hinterlegt, so werden diese Werte für diesen Buchungssatz
herangezogen und die Steuer wird errechnet. Dabei hängt es von der Steuerklasse
ab, ob der Betrag in der Exportdatei als Nettobetrag (bei Steuerklasse 1 oder
101) oder als Bruttobetrag (bei Steuerklasse 2 oder 102) interpretiert wird.
Beispiel:
Für das Konto 1755 ist die Steuerklasse 2
hinterlegt.  In der Importdatei steht der Betrag 14,06 €. Es wird folgender
Buchungssatz gebildet:
4100
an
1755
14,06
12,12
1775
1.94
Satzaufbau
Jede Zeile enthält einen Datensatz und die einzelnen
Werte sind durch Semikolon getrennt. Abgeschlossen werden die Zeilen mit
CR/LF:
Beispieldaten:
40000 H;;4001;200607;;3007;1711;;;;;"Aushilfslohn"
800 H;;4012;200607;;3007;1711;;;;;"Pausch.Lohnsteuer"
11200
H;;4031;200607;;3007;1711;;;;;"Gesetzl.Soz.Abgaben AG"
Die Felder haben folgende Bedeutung:
Feld
Besonderheiten
Umsatz
Beinhaltet zwei nachkommastellen
      ohne Dezimalpunkt. Enthält S bzw. H also:
800
      H
⇨
8,00 Haben
Frei
Gegenkonto
Belegfeld1
Hier
      steht Jahr und Periode in der Form YYYYPP.
Die
      Jahrnummer wird ins Datum übernommen.
Beispiel: 200607
Frei
Datum
Belegdatum in der Form TTMM.
      Beispiel: 3007
Konto
Hauptkonto
KostFeld1
Kostenstelle. Muss in Referenz-ERP so
      existieren.
KostFeld2
[...]


---

## DATEV-Export erstellen

DATEV-Export erstellen
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
DATEV-Export erstellen
Bei der Erstellung werden die Daten laut Eingrenzung
zusammengesucht. Einmal übertragene Belege erhalten ein Kennzeichen und können
somit nicht ein zweites Mal übertragen werden. Es finden auch einige Tests
statt, ob die Daten im korrekt sind und dem von DATEV geforderten Format
entsprechen.
Es wird nur der Export erstellt, wenn alle Belege in
dem angewählten Bereich fehlerfrei gebucht sind.
Anzahl der Stellen des Betrages.
Anzahl der Stellen der Kontonummern.
Anzahl der Stellen der Kostenstellen.
Feldname
Beschreibung
Bezeichnung
Hier
      kann eine Bezeichnung zur besseren Wiedererkennung des DATEV_Exports
      eingegeben werden. Diese Bezeichnung wird nicht mit übertragen und ist
      somit nicht relevant für das Exportverfahren.
DFV-Kz
Dies
      ist das Namenskürzel. Es wird hier die Kurzbezeichnung des Benutzers
      vorgeschlagen, der den Export erstellt. Diese Information wird mit
      übertragen.
Von/bis Datum
Dieses Datum dient zur Abgrenzung
      des Zeitraums. Es werden alle Belege mit einem Belegdatum kleiner als das
      „bis Datum“ zusammengesucht, die noch nicht übertragen wurden. „Von Datum“
      ist somit nur informatorisch zu sehen, da Referenz-ERP sicherstellen muss, dass
      nicht aus Versehen Belege nicht mit übertragen werden.
Von/bis Periode und
      Abrechnungsjahr
Die
      Periode und das Jahr werden wie das Datum zur Abgrenzung des Zeitraumes
      verwendet.
Abrechn.Nummer
Die
      Abrechnungsnummer ist eine laufende Nummer, die automatisch vom Programm
      hochgezählt wird, so dass man sich nicht darum kümmern muss. Sie kann
      jedoch überschrieben werden. Wird nur für die Formate OBE und KNE benötig
      und bei Verwendung der Formate 3.0 bzw. 7.0 nicht mehr
      abgefragt.
Beim Erstellen einer Datei für Buchungsstapel gilt
folgende Empfehlung der DATEV: Erstellen Sie pro Buchungsperiode eine eigene
Te
[...]


---

## DATEV-Firmenstamm

DATEV-Firmenstamm
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
DATEV Firmenstamm
Hier werden einmalig Daten erfasst, die für die
Erkennung der Datei erforderlich sind.
Feldname
Beschreibung
Datei-Format
Es
      stehen drei Dateiformate zur Verfügung
(OBE)
      Ordnungsbegriffserweiterung
Es gelten für dieses Format
      folgende Einschränkungen:
Referenznummern dürfen nur Numerisch
      sein.
Belegnummer/Referenznummer darf nur
      maximal 6 Stellen haben.
Kostenstellennummer darf maximal 4
      Stellen haben
Sachkonten dürfen nur 4 Stellen und
      Personenkonten nur 5 Stellen haben. Der Bereich der Debitoren ist auf
      10000 bis 69999 und der der Kreditoren auf 70000 bis 99999
      festgelegt.
(KNE)
      Kontonummernerweiterung.
Das
      Format KNE ist seit 08.2000 gültig. Es kann nur von den aktuellen
      DATEV-Windows-Programmen mit Schnittstelle importiert werden. Es ist hier
      eine Absprache mit dem Steuerberater notwendig. Dieses Format
      unterscheidet sich in folgenden Punkten von dem Aufzeichnungsverfahren
      OBE:
Referenznummern können auch
      Alphanumerisch sein.
Belegnummer/Referenznummer können
      bis zu 12 Stellen haben.
Umsatz kann statt 10 Stellen bis zu
      12 Stellen (incl. Nachkommastellen) haben.
Kostenstellen können bis zu 8
      Stellen haben (OBE nur 4).
Sachkonten können bis zu 8 Stellen
      haben. Hier gelten die von der DATEV vorgegebenen Regeln (Nummer der
      Personenkonten muss eine Stelle mehr haben als die der
      Sachkonten)
Die
      Namen der zu übertragenden Dateien werden statt DV01 bzw. DE001/DE002 zu
      EV01 und ED00001/ED00002.
Format 3.0
Dieses Format ist seit 2012 gültig
      und soll die bisherigen Postversandverfahren OBE und KNE ablösen. Zum
      Jahreswechsel  2017/2018 wurden diese Formate von DATEV abgekündigt.
Die
      Namen der zu übertagenden Dateien lauten:
EXTF_BUCHUNGSSTAPEL_ID_JJJJPP.csv
Und
EXTF_STAMMDATEN_ID_JJJJPP.csv
ID

[...]


---

## DATEV-Kundenexport einrichten

DATEV-Kundenexport einrichten
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
DATEV Kundenexport einrichten
Direktsprung
[DATEVK]
Bei der Übergabe der Stammdaten werden die Daten der
Personenkonten an die DATEV übermittelt. Diese können frei eingerichtet werden.
Für die Formate OBE und KNE ist die Einrichtung Identisch, für die neueren
Formate 3.0 und 7.0 müssen andere Kennziffern zugeordnet werden.
In diesem Pfleger kann man den Kennzahlen der DATEV
die Werte aus Referenz-ERP zuordnen. Welche Werte aus Referenz-ERP zugelassen sind lässt
sich in einer F3-Auswahl auswählen. Die Werte für die Kennzahl 101
„Änderungskennzeichen“ und 102 „Kontonummer“ für die Formate OBE und KNE sind
Pflichtangaben und lassen sich nicht ändern. Für das Format 3.0/7.0 ist nur das
Konto Pflicht. Alle anderen Angaben sind Optional.
Bei der Zuweisung der Felder kann man auch mehrere
Felder miteinander verbinden (siehe Kennziffer 103 „Name1“) oder
Datenbankfunktionen einbinden. Auch Subselects wie unter Kennziffer 731
„Vertreter“ sind möglich. Die komplette Zeile lautet in diesem Beispiel:
select VertGrBezeich from VertGruppe where
vertGruppe.vertgrnummer=DATEVSTAMMDATEN.VertGrNummer
Der Syntax entspricht dem SQL-Syntax. Um sicher zu
stellen, dass nicht erst beim Export ein Syntax-Fehler gemeldet wird, wird im
Rechte-Maustaste-Menü die Funktion „
Syntax-Test
“
F6
angeboten. Diese baut das Statement
zusammen und führt es einmal aus. Es erscheint ggf. ein Fehlermeldung oder ein
Hinweis, dass der Syntax korrekt ist.
Die Funktion „
Standard wiederherstellen
“
F7
löscht alle Einrichtungen und trägt die
einfachen Vorgaben von Branchen-ERP wieder ein.

---

## DATEV-Import Lohndaten

DATEV-Import Lohndaten
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datev
-Import Lohndaten
Der Import der Daten im DATEV-Format ist nicht in den
Standardimport integriert. Man findet diesen im Menü Abschlussarbeiten.
Voraussetzungen sind:
Bei dem Import der Lohndaten wird davon ausgegangen,
dass es sich nur um Sachkontenbuchungen ohne Steuerbuchungen handelt.
Die in der Datei übergebenen Sachkonten müssen in
Referenz-ERP eingerichtet sein. Eine Prüfung findet vor der Einspielung nicht
statt.
Die Kostenstelle muss in Referenz-ERP eingerichtet sein.
Wird keine Kostenstelle übergeben, so wird die im Sachkontenstamm hinterlegte
Kostenstelle verwendet.
Wird eine Belegnummer übergeben, wird diese in der
Referenznummer (FiBuV_FremdNr) gespeichert.
Im Feld
Name der Importdatei
muss der Dateiname der DATEV-Datei angegeben werden. Es wird davon ausgegangen,
dass nicht die Steuerungsdatei, sondern die Datei mit den Buchungsdaten
angegeben wird (zur Info: die Daten der DATEV bestehen jeweils aus einer
Steuerdatei und einer bzw. mehreren Dateien mit Daten). Die Datei kann mit F3
ausgewählt werden. Pfad und Dateiname werden sich gemerkt und beim nächsten
Aufruf erneut vorgeschlagen. Über den Dateinamen wird gleichzeitig das Format
erkannt. Mögliche Formate/Dateinamen sind:
•
DATEV-Format 3.0
hierbei handelt es sich um eine Datei im
CSV.Format. Die Standardreinrichtung für das DATEV-Format 3.0 ist vorgegeben,
kann jedoch mit der Funktion „
Format 3.0
einrichten
“
F10
individuell
angepasst werden.
DATEV-Format mit Ordnungsbegriffserweiterung
(OBE)
Dateiformat DV01 – hierbei handelt es sich um die Steuerungsdatei,
die Informationen zum Einlesen der Dateien DE001 bis DE0** enthält. Jede dieser
Datei kann Stammdaten oder Bewegungsdaten enthalten. Zum Import sind sowohl
Steuerungs- als auch Datendateien notwendig.
DATEV-Format mit Kontonummernerweiterung
(KNE)
Dateiformat EV01 – hierbei handelt es sich um die Steuerungsdatei,
die Informationen zum Einlesen der Datei
[...]


---

## Dauerfristverlängerung/Sondervorauszahlung

Dauerfristverlängerung/Sondervorauszahlung
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Umsatzsteuerwerte
Direktsprung
[UVA]
Der Antrag der Dauerfristverlängerung und die
Anmeldung der Sondervorauszahlung können in Referenz-ERP über das Programmmodul ELSTER
vorgenommen werden. Für die Sondervorauszahlung muss eine
Auswertungsposition
mit der
Kennziffer 39 (nicht 38 wie auf dem Formular für die Dauerfristverlängerung
/Sondervorauszahlung wegen der gleichzeitigen Verwendung im Formular der
Umsatzsteuervoranmeldung) für Steuer eingerichtet sein:
Diese Auswertungsposition muss dann in einem
Steuersatz mit der Steuerformel 100% hinterlegt sein und eine entsprechende
Buchung – in der Regel im Februar - vorgenommen werden. Dieser Wert wird dann im
Modul Elster ermittelt. Dabei werden alle Normalperioden des angegebenen
Kalenderjahres nach Belegen des Steuersatzes mit dieser Auswertungsposition
durchsucht.
Im Umsatzsteuervoranmeldungsformular wird nur dann die
Kennzahl 39 ermittelt, wenn der Voranmeldezeitraum das letzte Quartal bzw. der
letzte Monat des Kalenderjahres ist.

---

## Deckblatt

Deckblatt
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Überschriftszeile
Direktsprung
[CCD]
Um sich z.B. fertige Bankmappen zu erstellen, kann es
wünschenswert sein, zu den Daten gleich ein Deckblatt zu definieren. Hierfür
dient der Definitionstyp „
Deckblatt
“. Deckblätter erscheinen nur beim
Ausdruck des Reports.
Bei dem Typen Deckblatt ist die Bezeichnung nur
informatorisch. Sie erscheint nicht auf dem Crystal-Report.
Die
Kopfzeile
und die
Fußzeile
kann
rechtsbündig, zentriert oder linksbündig ausgegeben werden. Die Schriftart und
Schriftfarbe gelten jeweils für Fuß- bzw. Kopfzeile, da der Haupttext einzeln
formatiert werden kann. Weiterhin können Informationen aus der Datenbank
variabel hinterlegt werden. Dazu steht in eine Itembox zur Verfügung. Die
Ausgewählten Felder werden an die Stellen im Text eingefügt, an der die
Schreibmarker gerade steht.
In dem Textfeld für das Deckblatt kann dann ein
beliebiger Text eingerichtet werden. Es ist möglich dort die Schriftarten per
Windows-Systemdialog einzurichten.
Desweiteren sind umfassende Gestaltungsmöglichkeiten
über den Windows-Standard-RTF-Editor WordPad möglich.

---

## Definition des Chefcockpits

Definition des Chefcockpits
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Direktsprung
[CCD]
Die Auswertungen des Chefcockpits werden in
sogenannten Kennzahlengruppen zusammengefasst.
Jeder Eintrag in einer Kennzahlengruppe muss ein
eindeutiges Kürzel (
Abkürzung
) haben. Auf dieses Kürzel kann dann
ggf. in den Formeln zugegriffen werden.
Die Bezeichnung dient zur textlichen Identifikation
einer Zeile und steht in den Auswertungen des Chefcockpits  (Direktsprung
[CCA]
) in der ersten Spalte.
Zur Definition von
Chefcockpitauswertungen können verschiedene Bereiche definiert werden
1.
Spaltendefinition.
2.
Kontendefinition und externe Kontendefinition.
3.
Kostenstellendefinition und externe Kostenstellendefinition
4.
Kostenträgerdefinition und externe Kostenträgerdefinition
5.
Zeilendefinition.
6.
Überschriftszeilen.
7.
Deckblatt
Über die Sortierung wird zum einen die Reihenfolge auf
den Auswertungen festgelegt, zum anderen werden auch der Abkürzungen in dieser
Reihenfolge angelegt. Man kann sich in einer Formel also nur auf die Formeln
beziehen, die in der Sortierung vorn liegen!

---

## Den SQL Remote-Nachrichtenagent als Dienst über Eingabeaufforderung anlegen

Den SQL Remote-Nachrichtenagent als Dienst über Eingabeaufforderung
anlegen
1.
Öffnen Sie eine Windows-Eingabeaufforderung im Verzeichnis „..\Aeins\bin\“
2.
Geben Sie nun folgende Befehlszeilen ein:
dbsvc -as
-s auto -t network -w <Anzeigename> "<Pfad zur dbsrv12.exe>"
@<Pfad zur KonfigDateiDBsrv12>
dbsvc -as
-s auto -t DBRemote -rs <AnzeigenameAbhängigkeit> -w <Anzeigename>
"<Pfad zur dbremote.exe>" @<Pfad zur KonfigDateiDBRemote>
Werte in den spitzen Klammern bitte entsprechend
ersetzen!
Legen Sie die Dienste in der angegebenen Reihenfolge
an. In der Zweiten Befehlskette wird mit der
Option –rs
auf den
Anzeigenamen des ersten Dienstes verwiesen und bedeutet, dass dieser Dienst erst
ausgeführt wird, wenn der abhängige Dienst gestartet ist und läuft.
Die verwendeten Optionen (dbsvc):
-as

Konto "LocalSystem" verwenden
-s
<Start>

Startoption Automatic, Manual, Disabled
-t
<Typ>

Diensttyp Network, Personal, DBRemote, MobiLink, DBMLSync,
dbns,
dblsn, dbvss, rshost, rsoe, mlagent
-rs
<Abh>,...

Dienstabhängigkeiten
-w <Dienst>
<Details>   Dienst erstellen
Die verwendeten Optionen (dbsrv):
@<Pfad zur KonfigDateiDBsrv12>        Pfad
zur Konfigurationsdatei
Zur
Übersicht
Die verwendeten Optionen (dbremote):
@<Pfad zur KonfigDateiDBRemote>     Pfad zur
Konfigurationsdatei
Zur Übersicht

---

## Die Abstimmhilfe

Die Abstimmhilfe
Nach erfolgreicher Bereinigung der Mehrdeutigkeiten
steht Ihnen dieselbe Maske als Abstimmhilfe in folgender Form zur Verfügung:
Die Abstimmungen nach Sitzung, Datum und Belegnummer
beginnen aus der Sicht des Kassenbuchs und suchen die passenden Verbindungen in
Ware und Fibu. Die Abstimmung nach Kontonummer (gemeint ist hier immer ein
Kassenkonto) setzt in der Fibu auf und versucht von dort aus die Verbindungen zu
Kassenbuch und Ware aufzuspüren.
Die Funktion „Anzeige drucken“ schreibt den gesamten
Bildschirminhalt in eine Textdatei. Von dort aus können Sie drucken. Der
Zwischenschritt über die Textdatei eröffnet mehr Möglichkeiten, wie etwa die
Markierung von Teilbereichen oder die Suchfunktion.
Der Fehlerbericht schreibt ebenfalls Daten in eine
Textdatei. Dabei werden Daten auf verschiedenste Anomalien untersucht, die durch
Abbrüche entstanden sein können. Die Analyse der Daten kann in Teilen sehr
aufwendig sein.

---

## Eingabe/Auswahl offene Posten

Eingabe/Auswahl offene Posten
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
.
Im unteren Teil des Bildschirmes werden die offenen
Posten des Kunden / Lieferanten oder des Sachkontos angezeigt. Die offenen
Posten die man bearbeiten will, werden mit der Maus oder mit den Cursortasten
und ENTER ausgewählt. Bei der Bearbeitung mit der Maus oder der Tastatur können
mit der Umschalt- oder der Strg-Taste mehrere OP’s markiert werden. Bei der
Mausbedienung würde man immer beide Hände benötigen. Daher kann man im
Bedienerstamm die Option „Ausw.Strg fest“ auf
Ja
stellen. Das wirkt dann
so, als ob man immer die Strg-Taste gedrückt hält. Zusätzlich gibt es eine
einfache Möglichkeit mehrere OP’s nacheinander zu markieren. Man hält die
Leertaste einfach gedrückt; dadurch wird die aktuelle Zeile markiert (oder
entmarkiert) und der Cursor wandert in die nächste Zeile.
Diese Darstellung kann sich in Abhängigkeit von der
Fragestellung verändern. Für unterschiedliche Fragestellungen gibt es
verschiedene Darstellungsformen der offenen Posten. Sie können mittels
"
F2
- Auswahl" abgerufen werden.
Zusätzlich hängt die Darstellung der von Branchen-ERP
ausgelieferten Varianten noch von einigen weiteren Kriterien ab:
•
Steuerparameter
[SPA]
„Transaktionsnummer in
Reporten/Auswahllisten anzeigen“.  Die Transaktionsnummer ist eine
Eindeutige vom System vergebene Nummer, die zusätzlich zur Identifikation von
Belegen Herangezogen werden kann. Ist diese Nummer bekannt, kann man diesen
Beleg jederzeit in der
Einzelbeleganzeige
ansehen, indem man
über den Direktsprung
[ID]
diese Transaktionsnummer eingibt.
•
Steuerparameter
[SPA]
„Anzeige Fremdwährung in Auswahllisten“.
Wenn das Unternehmung mit Fremdwährung arbeitet, ist es Sinnvoll diesen
Steuerparameter auf
Ja
zu setzten
.
Es werden dann neben der
Buchwährung auch die Fremdwährungsbeträge und die Währung angezeigt. Ist die
Währung ungleich der Buchwährung, werden die Felder
Blau
dargestellt.
•
Der Skontob
[...]


---

## Einreichung des Bargeldes:

Einreichung des Bargeldes:
Das Bargeld wird nur durch eine Einreichung bei einer
Hausbank aus einer Hauptkasse entnommen. Dabei wird eine Fibu Buchung des
Einreichungsbetrags von der Kasse an das Verrechnungskonto der gewählten Bank
durchgeführt. Zusammen mit der Umbuchung des Bargeldes vom Kassenkonto an das
Bargeldkonto und der Einreichung an die Bank ist dann das Kassenkonto
ausgeglichen, vorausgesetzt der ganze Bargeldbestand wird eingereicht.

---

## Einrichtung Buchstellen

Einrichtung Buchstellen
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Buchstellen Firmenstamm
Direktspring
[BSFS]
Bevor die XML-Daten erzeugt und versendet werden,
bedarf es noch einiger Einstellungen im Referenz-ERP.
Buchstelle Firmenstamm
Bevor die Daten übermittelt werden können, bedarf es
einiger Einstellungen im „Buchstellen Firmenstamm“ (BSFS). Dort kann die
XML-Kopfstruktur und die Sendeeinstellungen hinterlegt werden.
Allgemein
Feldname
Beschreibung
Nummer
Identifizierende Nummer die der
      Buchstellenstamm haben soll.
Bezeichnung
Bezeichnung für den
      Buchstellenstamm
Nummernkreis
Hier
      muss ein Nummernkreis eingetragen werden, der
nur
von diesem
      Buchstellenstamm aus verwendet wird.
Der
      Grund dafür ist, dass beim Versenden der Daten eine fortlaufende Nummer
      gesendet wird. Anhand dieser kann erkannt werden, ob beim übertragen Daten
      verloren gegangen sind.
Verschlüsselungscode
Der
      Verschlüsselungscode wird zum verschlüsseln der Daten verwendet. Dieser
      Code muss bei Branchen-ERP bekannt sein, damit die Daten wieder entschlüsselt
      werden.
Sendeeinstellungen
Feldname
Beschreibung
Ausgabepfad
In
      diesem Feld muss ein Pfad hinterlegt werden, in den die Dateien exportiert
      werden. Von dort aus müssen die exportierten Daten an die Buchstelle z.B.
      per FTP übermittelt werden. (siehe „
Export der
      Daten
“)
XML-Struktur
Im Bereich XML-Struktur lassen sich XML – spezifische
Daten eintragen, welche später im XML – Dokument verwendet werden.
Feldname
Beschreibung
Mandant
Name
      der Firma/Betriebs
Empfängername
Name
      der Buchstellenfirma
Nachrichtentyp
Typ
      der Nachricht (Standard „invoice“)
Testübertragung
Handelt es sich um eine
      Testübertragung
Externe Referenz
Hier
      kann eine externe Referenz eingetragen werden
Bez.
      Branchen-ERP Kundennr.
TAG
      – Name des XML – Tags, bei keinem Eintrag wird
      „
Buchstellennummer
“ verwendet
Branchen-ERP
      Kundennummer
K
[...]


---

## Einrichtung der Abstimmung Kasse / Fibu

Einrichtung der Abstimmung Kasse / Fibu

---

## Einstellung Datentransfer ZMDO

Einstellung Datentransfer
ZMDO
Hauptmenü
Abschlussarbeiten
Zusammenfassende Meldung
Einstellungen ZMDO.
Direktsprung
[ZMDOO]
Arbeitsverzeichnis ZMDO
Bei der Bearbeitung der Daten müssen Dateien
zwischengespeichert werden. Dies geschieht auf dem hier eingetragenen
Arbeitsverzeichnis. Dort finden sich auch alle LOG-Dateien, falls es zu
Problemen bei der Übertragung kommt.
Zertifikat für den
authentifizierten Versand
Die ZMDO kann nur mit Authentifizierung übertragen
werden. Informationen zur Authentifizierung findet man unter
www.elster.de
.
Es existieren drei verschiedene Möglichkeiten der
Authentifizierung:
•
Software-Zertifikat:
Angabe des Dateiname - inklusive des vollständigen
Verzeichnisses  - des Software-Zertifikats (i.d.R. mit der Endung
.pfx).
•
Sicherheitsstick:
Angabe des Dateinamens des Treibers. Bitte beachten,
dass der Treiber betriebssystemabhängig sein kann. Aktuell werden folgende
Sticks von Elster unterstützt:
o
G&D
StarSign USB Token für ELSTER. Hier heißt die Treiber-DLL
starsignpkcs11_w32.dll
o
G&D
StarSign Crypto USB Token für ELSTER. Hier heißt die Treiber-DLL
aetpkss1.dll
Weitere Informationen in der Anleitung zum
Sicherheitsstick stehen unter
www.sicherheitsstick.de
.
•
Signaturkarte:
Angabe des Dateinamens des Treibers, welcher
einen Zugriff auf die Signaturkarte ermöglicht. Weitere Informationen in der
Anleitung zur Signaturkarte.
Übertragungsprotokoll archivieren
Diese Möglichkeit erscheint dann, wenn eine
Archiv-Lizenz vorliegt. Die Standardeinstellung ist
Ja
. Ist diese Option
aktiviert, wird nach der erfolgreichen Datenübermittlung das PDF-Dokument sofort
in das Archiv gestellt und anschließend das Dokument sofort aus dem Archiv
heraus geöffnet. Die zugehörige Belegklasse im Archiv ist „ELSTER-ZMDO“.
Konfiguration des Proxy-Servers für die
Datenübermittlung:
Sollte die Verbindung zum Internet über einen
Proxyserver laufen, so können hier die Einstellungen vorgenommen werden.
ACHTUNG:
Die FIREWALL muss die Verbindun
[...]


---

## Einzelbeleganzeige

Einzelbeleganzeige
Hiermit wird der einem OP zugrundeliegende
vollständige Buchungssatz angezeigt. Dieser Bildschirm ist der zentrale
Informationsbildschirm, der überall zur Anzeige von Belegen verwendet wird.
Im Informationsbereich oben rechts stehen
in der ersten Zeile die Belegart, die Belegnummer, das Belegdatum, die
Referenznummer und die Archivreferenz (Paginiernummer). In der zweiten Zeile
stehen Informationen darüber, wann und von wem der Beleg erfasst wurde sowie die
Bezeichnung der Belegmappe. Die dritte Zeile ist nur zu sehen, wenn der Beleg
bereits gebucht worden ist. Sie enthält das Datum, an dem der Beleg gebucht
wurde, die Nummer des Buchungsjournals und den Bediener, von dem der Beleg
gebucht worden ist.
Unter diesen Zeilen werden noch weitere Informationen
angezeigt.
1.
Der Zahlungsstatus:
Wenn ein
OP über den automatischen Zahlungsverkehr beglichen wird so kann man hier
verfolgen, in welchem Status er sich gerade befindet.
Mögliche Stati sind:
•
**Zahlsperre gesetzt**
Die Zahlsperre kann hier über die Funktion
OP-Info oder direkt in der OP-Verwaltung gesetzt werden. Wird die Zahlsperre
gesetzt, wird der OP ggf. aus den Zahlungsvorschlägen entfernt.
•
in Zahlungsvorschlag
•
zur Zahlung freigegeben
•
Scheckdruck / DTA ausgeführt
•
**Scheckdruck / DTA abgewiesen**
Dieser Status besagt, dass versucht
wurde einen Scheck zu drucken oder einen DTA auszuführen, jedoch die
Informationen in den Stammdaten nicht ausreichend waren (z.B. fehlende
Bankverbindung). Die genaue Fehlerursache wurde beim, Scheckdruck bzw. beim DTA
ausgegeben. Nach Behebung des Problems kann der Scheckdruck / DTA wiederholt
werden.
•
**Zahlung unvollständig**
Dieser Status besagt, dass zwar der Scheck
gedruckt wurde bzw. der DTA ausgeführt wurde, aber der Zahlungsbeleg gelöscht
wurde, bevor er in die Primanota geschrieben worden ist. Dadurch bleibt der
Beleg als OP stehen, darf aber nicht ohne weiteres wieder im automatischen
Zahlungsverkehr einfließen. Belege,
[...]


---

## Einzelkontosummen

Einzelkontosummen
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorg. Oberkonten
Direktsprung
[FIREO]
Der letzte Punkt der Reorganisation
Einzelkontosummen
ermöglicht es Ihnen, für ein einzelnes Konto (bis auf
alle Forderungs- und Verbindlichkeitskonten) die Kontosummen für eine Periode in
einem Jahr zu reorganisieren. Dies kann sinnvoll sein, wenn Sie bereits einen
Test Bewegungsdaten durchgeführt haben und nur ein oder zwei Konten Fehler beim
Test der Kontosummen aufgewiesen haben. So muss nicht der gesamte
Reorganisationslauf durchgeführt werden. Forderungskonten können hier nicht
reorganisiert werden.

---

## ELSTER

ELSTER
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Umsatzsteuerwerte
Direktsprung
[UVA]
Wichtiger Hinweis zum Sicherheitsstick:
Der Sicherheitsstick
"G&D Starsign USB Token" wird nur noch bis 28.02.2019 unterstützt. Sollten
Sie diesen Sicherheitsstick nutzen, achten Sie bitte darauf, rechtzeitig einen
neuen Sicherheitsstick zu beschaffen (
www.sicherheitsstick.de
), um bei der Verlängerung Ihres Zugangs im Februar
2019 auf diesen neuen Sicherheitsstick wechseln zu können. Im Rahmen der
Verlängerung Ihres Zugangs ist daher ein Stickwechsel durchzuführen. Eine
Verlängerung Ihres Zugangs mit dem aktuell eingesetzten Sicherheitsstick ist
nicht möglich.
Wichtiger Hinweis zur Datenschutz-Grundverordnung:
ELSTER schreibt
vor, dass vor dem Versand der Daten die Informationen zur
Datenschutz-Grundverordnung
einmal akzeptiert werden. Um
dies zu gewährleisten, wird jeder ELSTER-Anwender vor dem Versand einer
Umsatzsteuervoranmeldung oder der Zusammenfassenden Meldung einmal aufgefordert
aktiv zu bestätigen, dass er die Datenschutzgrundverordnung gelesen und
akzeptiert hat.
Elster
ist die Abkürzung für
El
ektronische
St
euer
Er
klärung.
Die von Ihnen erstandene Software enthält
Programm-Module, die von der bayerischen Steuerverwaltung entwickelt wurden.
Diese Module ermöglichen Ihnen die Abgabe von
Umsatzsteuer-Voranmeldungen
,
Anträgen auf Dauerfristverlängerung
und
Anmeldungen von Sondervorauszahlungen
per Datenfernübertragung via
Internet.
Mit der Datenübermittlung ersparen Sie sich das
Übersenden der amtlichen Vordrucke an das zuständige Finanzamt.
Jeder Steuerbürger, für den Daten übermittelt werden,
hat vor der ersten Datenübermittlung eine eigenhändig unterschriebene
Teilnahmeerklärung bei dem für ihn zuständigen Finanzamt abzugeben. Diese ist
nur einmalig zu stellen; auch bei einem Wechsel des zuständigen Finanzamtes ist
kein erneuter Antrag einzureichen. Nach Abgabe einer Teilnahmeerklärung, können
die o.g. Steueranmeldungen wahlweise per Datenfernübe
[...]


---

## Erfassungsabschluss

Erfassungsabschluss
Nach Beendigung der Erfassung gelangt man mit
ESC
wieder in den Kopfteil der
Vorgangserfassung zurück, von wo aus je nach Parametereinstellung die
Weiterverarbeitung erfolgt.
Vorschau Druck (SF5)
Diese Funktion ermöglicht es, sich den erfassten
Vorgang so wie er ausgedruckt wird, auf dem Bildschirm anzeigen zu lassen. (In
der Regel wird die Optik genau wie der Ausdruck gestaltet sein, es ist jedoch
auch möglich, ihn völlig anders zu gestalten!) Somit wird vor dem Ausdruck noch
einmal eine visuelle Kontrolle ermöglicht. Wenn ein Fehler festgestellt wird,
kann über die Funktion
Positionsteil
F5
wieder zur Erfassung
zurückgekehrt werden.
Gesamtsummen (SF10)
Diese Funktion zeigt die Gesamtsummen (Nettobetrag,
Warenwert, Zu- Abschlag, Rabatt, Fracht, Mehrwertsteuer, Skonti, Gesamtbetrag,
Gewicht, Mengeneinheiten, Verpackung) an.
Es handelt sich um eine reine Anzeigefunktion,
Änderungsmöglichkeiten bestehen nicht.
Mit dem Knopf ‚Steuern‘ gelangt man in einen Dialog
zur Übersicht aller im Beleg aufgelaufenen Steuerbeträge. Bei Eingangsbelegen ab
Stufe Rechnung gibt es hier die Möglichkeit, die Steuerbeträge geringfügig zu
ändern, falls auf den Originalbelegen von Referenz-ERP abweichend errechnete
Steuerbeträge ausgewiesen werden.
Steuer (F11)
Die Rechnungsbeträge werden aufgelöst nach
Steuersätzen angezeigt:
Die automatisch berechneten Steuerbeträge je
Steuersumme können bei Rechnungsbelegen manuell angepasst werden, um zum
Beispiel für nacherfasste Rechnungen, die anderweitig erstellt wurden, etwaige
Rundungsdifferenzen zu berücksichtigen.
Zahlungsbedingung (F8)
Entsprechend der Eintragung im Kundenstamm sowie der
Parameter des Artikelstamms werden die Zahlungsbedingungen ermittelt. Sie können
hier angezeigt und ggf. korrigiert werden:
Allgemeine Zuordnung (F9)
Diese Funktionsbox enthält weitere Parameter,
vorbelegt aus dem Kundenstamm, die für die Preisfindung, statistische Analysen,
etc. von Bedeutung sind. Diese Informationen könne
[...]


---

## Eröffnung der Mitgliederverwaltung

Eröffnung der Mitgliederverwaltung
Es empfiehlt sich folgende Buchungslogik zur Eröffnung
des Systems:
Nach Eintrag der Parameter im Gesellschaftsstamm
werden vom Kunden / Gesellschafter her die bestehenden Anteile als Zeichnung
eingegeben. Es ist zwischen Pflichtanteilen und freiwilligen Anteilen zu
unterscheiden. Der eingezahlte Betrag ( Stand des GG-Kontos X-COM ) wird als
Einzahlung eingegeben. (Eventuell noch nicht ausgezahlte Kündigungen werden
ebenfalls eingetragen)
Hiermit entsteht ein entsprechender Saldo auf dem
Kundenkonto. Dieser ist mit entsprechender Auszifferung gegen ein
Bilanzeröffnungskonto auszugleichen.
Mit diesem Verfahren werden ein korrekter Einstieg und
die Verfolgung eines Kontos in der Zukunft gewährleistet.

---

## Erlöskontenzuordnung bei Anschluss FiBu

Erlöskontenzuordnung bei Anschluss FiBu
In der Variante mit FIBU-Anschluss  werden die
Daten neben der Übernahme in die RFS-Schnittstelle zum Teil auch in der FIBU
verwaltet. Abweichend von der XCOM-Version von RFS muss unter Aeins die
Zuordnung der Gegenkonten  über den  Mechanismus Erlöskennziffer
<-> Erlöskonten Zuordnung erfolgen.

---

## Erster Schritt: Automatik bei Versionsupdate

Erster Schritt: Automatik bei Versionsupdate
Um eine Abstimmung zwischen Kasse und Fibu technisch
überhaupt möglich zu machen, waren weitere Vorkehrungen notwendig. Ab der
Version 6.3 wird eine definierte Verbindungstabelle namens AcashFibuLink
geführt, die die Beziehungen zwischen Kassenbelegen und ihren zugehörigen
Fibu-Belegen definiert. Da diese Tabelle neu eingeführt wurde, müssen die
Beziehungen bereits bestehender Objekte erstmalig hergestellt werden. Das
leistet ein Umstellprogramm, das in den Update Prozess eingebettet ist. Dieses
Programm versucht, aufgrund im Kassensystem vorhandener Daten (Zahlungsbetrag,
Datum, Belegart, Kundennummer, Kassenkonto, Gegenkonto, Buchungstexte usw.)
einen passenden Fibu-Beleg zu finden. Nur wenn ein eindeutig passender Beleg
gefunden wird, kann dieser automatisch zugewiesen werden.

---

## Export Diamant-Finanzbuchhaltung

Export Diamant-Finanzbuchhaltung
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Export
Variante Diamant
Direktsprung
[FIEX]
Diese Variante „Diamant“ ist ein „nicht
freigeschaltete Variante“ und daher erst dann zu sehen, wenn sie in der
Anwendungsadministration ( Direktsprung ANW ) freigeschaltet wird.
Dem Export von Belegen aus der
Referenz-ERP-Finanzbuchhaltung in die Diamant-Finanzbuchhaltung liegt eine
Datenbankprozedur zugrunde, die die Daten in der Form bereitstellt, wie sie von
der Importschnittstelle der Diamant-Finanzbuchhaltung  erwartet werden.
Dies hat den Vorteil, dass Änderungen kurzfristig nachgearbeitet werden
können.
Es handelt sich um einen Belegexport - also nicht nur
Offene Posten. Beim Belegexport werden alle Belege aus der Warenwirtschaft (
Einkaufsrechnungen, Einkaufsgutschriften, Ausgangsrechnungen,
Ausgangsgutschriften, …), die bereits in die Fibu übertragen worden und
gebucht
worden sind, in eine Datei auf dem angegebenen Verzeichnis
geschrieben. Es wird dabei der Fibu-Satz und der Gegenkontosatz erzeugt.
Kostenrechnungsdaten werden nicht übergeben.
Das Verzeichnis lässt sich mit der Funktion
Verzeichnis ändern
F5
angeben. Es öffnet sich dann ein
Dateiauswahl-Dialog, mit dessen Hilfe das  Verzeichnis ausgewählt werden
kann.
Wenn man den Schalter „Exportsteuerschlüssel mit
übertragen“ auf
Ja
setzt,
dann werden die im Steuersatz gepflegten
Exportschlüssel übergeben, ansonsten bleibt das Feld leer und es wird nur der
Steuersatz übertragen.
Bevor der eigentliche Export gestartet wird, werden
eventuell vorhandene Dateien umbenannt. Sie bekommen als zusätzliche Endung die
interne Nummer des letzten Exports. Diese Nummer findet man auch in der Relation
Fibuvorgstamm und der Relation FibuvorgExport im Feld Fibuv_ExportIdent wieder,
um eine Verbindung zwischen Daten und der Datei zu haben.
Nach dem Belegexport werden die exportierten Daten mit
einem Merker und einem Eintrag in der Relation FibuvorgExport versehen, damit
ein vers
[...]


---

## EXIT Statement

EXIT Statement
Syntax
EXIT;
Purpose
Beendet eine Kommandodatei;
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
GOTO
,
IF
Beschreibung
Es kann wünschenswert sein, eine Kommandodatei vor dem
Dateiende zu verlassen. Hierzu dient der Befehl EXIT;
Beispiel
Select * from fibuvorgstamm where
fibuv_nummer is NULL;
IF (VAL(DBERR)!=0) // Keine Daten
gefunden
{
EXIT;
}

---

## Export IBM-Finanzwesen

Export IBM-Finanzwesen
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Export
Variante Belegexport IBM Finanzwesen
Direktsprung
[FIEX]
Dem Export von Belegen aus der
Referenz-ERP-Finanzbuchhaltung in das IBM-Finanzwesen (kurz FW) liegt eine
Auswahlliste zugrunde, die die Daten in der Form bereitstellt, in der sie von
der Importschnittstelle des FW erwartet werden. Dies hat den Vorteil, dass
Änderungen im FW kurzfristig nachgearbeitet werden können. Zusätzlich zu den
reinen OPs können auch noch die Kunden- bzw. Lieferantendaten und deren
Anschriften exportiert werden. Dazu müssen folgende private SQLK’s eingerichtet
werden:
DumpLiefData
DumpLiefAdrData
DumpKundData
DumpKundAdrData
Ob das Personenkonto als Kundenkonto oder als
Lieferantenkonto betrachtet wird, geschieht über das Feld Kundtyp der
Auswahlliste. Kundtyp=2 ist dann Kunde und alles andere ist Lieferant. Genauer
Beschreibung zu den SQLK’s siehe Satzaufbau
Startet man den Export wird zuerst der Pfad und
Dateiname abgefragt Vorgeschlagen wird bei ersten Mal das Verzeichnis
„..\Export“ und der Dateiname „FibuExport.txt“. Der Ausgewählte Pfad und
Dateiname wird zwischengespeichert und bei der nächsten Verwendung dieses
Programmteils wieder vorgeschlagen.
Achtung:
Der Dateiname wird zusätzlich mit der Nummer versehen,
die im Fibuvorgstamm im Feld FiBuV_ExportIdent hinterlegt wird. Wenn man also
EXPORT.TXT als Dateinamen angibt, wird der Name um die Nummer (z.B. 4377)
erweitert, so dass der Dateiname EXPORT_4377.TXT lautet.
Nach erfolgreichem Export erscheint folgende
Meldung:
Satzaufbau
Die Daten sind durch Komma getrennt und stehen in
Hochkomma. Die Daten bestehen aus einem Vorsatz  gefolgt von den
eigentlichen Daten. Sie haben zurzeit folgende Struktur:
Vorsatz:
Nr.
Name
Typ
Max. Länge
NK
Hinweis
0
Satzart
A
7
AF1BA1
1
Firmennummer
N
2
Aus
      Mandantenstamm
2
Satzidentifikation
A
20
Leer
3
Kurzbezeichnung
A
20
Fest
      ‚Export’
4
Belegdatum
D
Datum VSBDATUM aus der
      Auswahlliste

[...]


---

## Export KHK-Finanzbuchhaltung

Export KHK-Finanzbuchhaltung
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Export
Variante Belegexport KHK
Finanzbuchhaltung
Direktsprung
[FIEX]
Dem Export von Belegen aus der
Referenz-ERP-Finanzbuchhaltung in die KHK-Finanzbuchhaltung  liegen vier
Datenbankprozeduren zugrunde, die die Daten in der Form bereitstellt, in der sie
von der Importschnittstelle der KHK-Finanzbuchhaltung  erwartet werden.
Dies hat den Vorteil, dass Änderungen kurzfristig nachgearbeitet werden können.
Es handelt sich hier um einen Belegexport (also nicht nur OPs) und um einen
Export der geänderten bzw. neu angelegten Personenkonten. Beim Belegexport
werden alle Belege aus der Warenwirtschaft ( Einkaufsrechnungen,
Einkaufsgutschriften, Stornorechnungen, Ausgangsrechnungen,
Ausgangsgutschriften, Rohwarenzu- und Abgang), die bereits in die Fibu
übertragen und gebucht worden sind in eine Daten „Export.DIF“ geschrieben.
Wenn man den Export das erste Mal startet, wird
automatisch „..\export\khk“ als Verzeichnis für den Export vorgeschlagen.
Existiert dieses Verzeichnis nicht, wird es automatisch angelegt. Es kann mit
der Funktion
Verzeichnis ändern
F5
geändert werden.
Der ausgewählte Pfad wird zwischengespeichert und bei der nächsten Verwendung
dieses Programmteils wieder vorgeschlagen.
Die Schnittstelle kann die Daten in der Version 3.2
und 4.0 übertragen. Zusätzlich lässt sich auswählen, ob die Personenkonten mit
übertragen werden und ob immer sämtlich Stammdaten oder nur geänderte Stammdaten
übertragen werden sollen. Wenn man diesen Export das erste Mal startet sind
natürlich alle Personenkonten als noch nicht übertragen gekennzeichnet. Beim
nächsten Export werden dann nur die Personenkonten übertragen, die sich seither
geändert haben.
Man startet den Export mit
F9
. Vor dem Start
des Exports wird vom Programm geprüft, ob die benötigten Addonfelder angelegt
wurden. Hierfür existiert in der Auswahlliste eine Funktion
Addonfelder
anlegen
F10
.
Sind die Felder noch nicht
[...]


---

## Export und Verarbeitung

Export und Verarbeitung
Export der Daten
Das Exportieren der Daten erfolgt beim Buchen der
Belege. Die Buchungsdaten werden dabei in eine XML-Struktur umgewandelt und mit
der XML-Kopfstruktur aus dem „
Buchstellen Firmenstamm
“ zusammengeführt.
Danach wird die komplette XML-Datei in den festgelegten Pfad abgelegt.
Von dort aus muss die Datei z.B. per FTP an die
Buchstelle übermittelt werden.
Verarbeitung
Nachdem die Daten vom Webservice empfangen wurden,
erfolgt eine Prüfung des Passworts und der Sender-E-Mailadresse. Sind die Daten
korrekt erfolgt eine weitere Verarbeitung der Daten, die Daten werden
entschlüsselt und auf einem Server bereitgestellt.
Dort können die Daten von den entsprechenden
Buchstellen abgeholt werden.

---

## Externe Kontendefinition

Externe Kontendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Externe
Kontendefinition
Direktsprung
[CCD]
Bei der externen Kontendefinition handelt es sich
lediglich um einen Verweis auf eine bestehende Kontendefinition. Man muss so
nicht für jede Kennzahlengruppe immer wieder Kontenlisten neu erfassen. Auch
erspart man sich so die Pflege verschiedener Listen, die eigentlich denselben
Inhalt haben sollen, da nur die Originalliste gepflegt werden muss. In dem Feld
Externe Definition
kann man mit
F3
eine bestehende
Kontenliste aus einer beliebigen Kennzahlengruppe auswählen. Will man auf die
Planzahlen dieser Definition zugreifen, so muss man keine neue Liste definieren.
Man stellt dem Kürzel einfach PLAN_ vorweg  - also PLAN_AKZ für die
Plandaten Siehe auch
Externe Kostenstellendefinition
bzw.
Externe
Kostenträgerdefinition
.

---

## Exportverfahren der Finanzbuchhaltung

Exportverfahren der  Finanzbuchhaltung
Für den Export von Belegen der Finanzbuchhaltung
stehen mehrere Verfahren zur Verfügung. Die Verfahren
OP-Export, Export
IBM-Finanzwesen
und
Export KHK-Finanzbuchhaltung
verwenden alle das
gleiche Exportkennzeichen und sind somit nur alternativ zu verwenden. Über die
Funktion
Exportprotokoll
, die man
über den Direktsprung FIEXP erreicht, kann eine Auswahlliste mit allen Belegen
eines Laufes aufgerufen werden. Dort können einzelne Belege in der
Einzelbeleganzeige
als
„nicht ins Fremdsystem einlesbar“ gekennzeichnet werden.

---

## Externe Kostenstellendefinition

Externe
Kostenstellendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Externe
Kostenstellendefinition
Direktsprung
[CCD]
Bei der externen Kostenstellendefinition handelt es
sich lediglich um einen Verweis auf eine bestehende Kostenstellendefinition. Man
muss so nicht für jede Kennzahlengruppe immer wieder Kostenstellenlisten neu
erfassen. Auch erspart man sich so die Pflege verschiedener Listen, die
eigentlich denselben Inhalt haben sollen, da nur die Originalliste gepflegt
werden muss. In dem Feld
Externe Definition
kann man mit
F3
eine bestehende Kostenstellenliste aus einer beliebigen Kennzahlengruppe
auswählen. Will man auf die Planzahlen dieser Definition zugreifen, so muss man
keine neue Liste definieren. Man stellt dem Kürzel einfach PLAN_ vorweg  -
also PLAN_AKZ für die Plandaten. Siehe auch
Externe Kontendefinition
bzw.
Externe
Kostenträgerdefinition.

---

## Externe Kostenträgerdefinition

Externe
Kostenträgerdefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Externe
Kostenträgerdefinition
Direktsprung
[CCD]
Bei der externen Kostenträgerdefinition handelt es
sich lediglich um einen Verweis auf eine bestehende Kostenträgerdefinition. Man
muss so nicht für jede Kennzahlengruppe immer wieder Kostenträgerlisten neu
erfassen. Auch erspart man sich so die Pflege verschiedener Listen, die
eigentlich denselben Inhalt haben sollen, da nur die Originalliste gepflegt
werden muss. In dem Feld
Externe Definition
kann man mit
F3
eine bestehende Kostenträgerliste aus einer beliebigen Kennzahlengruppe
auswählen. Will man auf die Planzahlen dieser Definition zugreifen, so muss man
keine neue Liste definieren. Man stellt dem Kürzel einfach PLAN_ vorweg - also
PLAN_AKZ für die Plandaten. Siehe auch
Externe Kontendefinition
bzw.
Externe
Kostenstellendefinition
.

---

## Fehlbuchungen

Fehlbuchungen
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Journal/Ereignisprotokoll
Variante
Fehlerliste Buchungen
Direktsprung
[JOUR]
Leider läuft nicht immer alles so glatt, wie man es
sich wünscht und es kommt dazu, dass beim Buchen Fehler auftreten. Diese Fehler
werden in der Anwendung „
Journal/Ereignisprotokoll
“ in der Variante
„
Fehlerliste Buchungen
“ aufgelistet. Es können folgende Fehler
auftreten:
•
Beleg unvollständig!
Bedeutung
:
            Es fehlt der
Abschlusssatz eines Beleges (Fibuvorgstamm).
Ursache/Abhilfe
: Ein
solcher Beleg kann theoretisch nicht im Buchungslauf erscheinen, da nur
vollständige Belege zum Buchen herangezogen werden. Also kann nur zwischen
„Buchungen Fibu“ und dem Lauf des Mandantenservers der Abschlusssatz
verschwunden sein. Dieses wäre also ein harter Fehler und unbedingt Branchen-ERP zu
melden. Eine Überprüfung der Datenbank ist nötig.
•
Beleg gesperrt, weil in Benutzung!
Bedeutung
: Es existiert ein
Eintrag für diesen Beleg in der Lockingrelation.
Ursache/Abhilfe
: In
dem Moment, in dem der Mandantenserver den Beleg verarbeiten will, wird er
gerade anderweitig bearbeitet.
Anschließend Fehlbuchungen zurücksetzen und
neu buchen.
•
Beleg hat falschen Buchungsstatus!
Bedeutung
: Der Wert des
Feldes Fibuv_Buchstat ist nicht 1.
Ursache/Abhilfe
: Bei „Buchungen
Fibu“ wird der Status auf  1 (zum Buchen vorgesehen) gesetzt und es ein
Eintrag im Datenstrom vorgenommen, damit der Mandantenserver diesen Beleg
verarbeitet. Beim Verarbeiten wird dieser Wert dann auf 2 (in Bearbeitung) und
anschließend auf 3 (gebucht) oder auf 4 (nicht buchbar) gesetzt. Dabei muss ein
Fehler aufgetreten sein.
Fehlbuchungen zurücksetzen und erneut buchen.
•
Periode %d / %d nicht offen oder nicht vorhanden!
Bedeutung
:
Die Periode, der dieser Beleg zugeordnet hat nicht den Status „offen“ (Status=1)
oder „Buchungsschluss“(Status=2) oder sie existiert
nicht.
Ursache/Abhilfe
: Der Belege wurde für eine nicht existierende
oder nicht offen P
[...]


---

## FiBu

FiBu
Für Finanzvorgänge (Einzahlungen, Auszahlungen, ...
auch Differenzen beim Kassenabschluss) muss pro Bedienerklasse, die Arbeiten an
der Kasse durchführt, über
[NKF]
folgendes eingerichtet sein. (Direktverbuchung in die FiBu)
Existiert in der FiBu-Vorgangszuordnung für die
Kassenbedienerklassen eine Nummernkreiszuordnung für Zahlungsverkehr Bank (für
Geldeinzahlungen, Entnahmen und andere Zahlungen an der Kasse)?

---

## FiBu – Übertrag

FiBu – Übertrag
Die selektierten Vorgänge werden hiermit zur
Übertragung an die Finanzbuchhaltung gekennzeichnet (Kennzeichen
i.B.
in
der Spalte
FIB)
. Die Übertragung selbst wird durch den Mandantenserver
ausgeführt.
Vieraugenprinzip
(Kein Finanzbuchhaltungsübertrag mit Mitarbeitern aus
zwei Abteilungen)
Mit dem
SPA
677
kann eingestellt werden ob Belege sofort in die Finanzbuchhaltung
übertragen werden dürfen, oder ob zwei Bediener dafür nötig sind. Der SPA steht
Standard mäßig auf JA, wird dieser auf Nein gestellt, so müssen zwei Bediener
aus zwei unterschiedlichen Abteilungen den Beleg in die Finanzbuchhaltung
übertragen.
Beim ersten Bediener wird das Kennzeichen
Erstbetrachter gesetzt und der zweite Bediener setzt das Zustimmungskennzeichen.
Wenn der zweite Bediener das Zustimmungskennzeichen gesetzt hat, so wird der
Beleg in die Finanzbuchhaltung übertragen.

---

## FiBu-Buchung der permanenten Inventuren

FiBu-Buchung der permanenten
Inventuren
Bei der Buchung einer Inventur in die
Finanzbuchhaltung wird entweder ein Wertstellungsbeleg der
Artikel-Stichtagsinventur oder ein
Differenzbeleg
z.B. aus der
Erfassung mit einem Scannersystem in die Finanzbuchhaltung (FiBu) übertragen.
Die FiBu-Konten der Buchungen werden bei der
../Stammdaten/Firmenstamm.docx#EKZZ_Bestandsbewertung
eingerichtet.
Nr
Bezeichnung
Beschreibung
0
Hauptzeile
Diese Zeile bleibt bei dieser Art
      der Buchungen stets leer.
1
Abgangskonto
Der
      Wert des Soll-Bestandes der Ware wird auf die Haben-Seite des
      Abgangskontos gebucht.
2
Zugangskonto
Der
      Wert des gezählten Bestandes der Ware wird auf die Soll-Seite des
      Zugangskontos gebucht.
3
Inventurdifferenzenkonto
Die
      Differenz der beiden obigen Buchungen wird je nach Vorzeichen auf die
      Soll-Seite (Wertverlust) oder Haben-Seite (Wertsteigerung) des
      Inventurdifferenzenkontos gebucht.

---

## FiBu – Eintrag zurücknehmen

FiBu – Eintrag zurücknehmen
Die selektierten Vorgänge werden geprüft, ob sie in
der FiBu verarbeitet wurden. Wenn dort nur ein Primanota-Eintrag existiert, so
kann dieser entfernt werden.

---

## FIBU-CSV-Import

FIBU-CSV-Import
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datenübernahme
Direktsprung
[DUEB]
Um für CSV-Dateien einen Datenimport in die
Finanzbuchhaltung zu definieren, kann eine Datenübernahme definiert werden. Es
finden hier keine Tests statt, ob eine Datei bereits eingelesen wurde. Dies muss
durch geeignete betriebliche Maßnahmen sichergestellt werden.
Um die CSV-Verarbeitung zu aktivieren, müssen im Block
„Prozeduren“ folgende Werte eingetragen werden:
Steht man im Feld „Programm 1“, so können mit F3 auch
die hier einzutragenden Werte ausgewählt werden. „Programm 1“ und „Programm 2“
sind von Branchen-ERP bereitgestellte Funktionen, die die Verarbeitung steuern.
Das Programm „dueb_import2db_csv“ importiert die
Dateien in das Formulararchiv. Dort sind sie unter dem Belegtypen
„Fibu-Datenübername CSV“ wiederzufinden. Gleichzeitig wird in der Tabelle
„dueb_import“ die Fa_id und die Fa_mndnr des Archiveintrags vermerkt.
Das Programm „dueb_import_csv“ versucht mithilfe der
unter Prozedur eingetragenen privaten Datenbankprozedur die Daten zu
verarbeiten. Dabei werden vor der Belegerstellung erst alle Daten auf Konsistenz
geprüft und erst danach werden die Belege erstellt. Dadurch ist sichergestellt,
dass nicht nur Teile aus der Datei verarbeitet werden.
In das Feld Prozedur muss eine private Prozedur
eingetragen werden, die ein Resultset mit den erforderlichen Daten zurückliefern
muss. Mit der Funktion
Prozedur
bearbeiten
kann die Funktion direkt bearbeitet oder neu angelegt werden.
Bei der Neuanlage wird ein Gerüst mit dem benötigten Resultset vorgegeben.
Beispieldaten:
ident;telefon;mail;klasse;referenznr;beledatum;hauptkonto;gegenkonto;betrag;sh
1;0431
99020;Support@Branchen-ERP;ZA;ABC;20.09.2023;1010;10111;500;S
1;0431
99020;Support@Branchen-ERP;ZA;ABC;20.09.2023;1010;10123;200;S
1;0431
99020;Support@Branchen-ERP;ZA;ABC;20.09.2023;1010;10000;300;H
Beispiel Prozedur zum Einlesen der Beispieldaten. Zu
bearbeiten ist in den meisten Fällen nur der
individuelle
[...]


---

## Fibu Reorganisator

Fibu Reorganisator
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Direktsprung
[FIREO]

---

## Fibu Reorganisator allgemein

Fibu Reorganisator allgemein
Um sicher zu stellen, dass man sofort auf eventuell
aufgetretene Fehler hingewiesen wird, kann man Referenz-ERP so starten, dass sofort
der Reorganisator aufgerufen wird und die Testfunktionen ausgeführt werden. Das
automatische Ausführen der Reorganisation selber wird nicht unterstützt.
Referenz-ERP muss mit folgender Syntax gestartet werden:
Der Fibu Reorganisator ist ein Hilfsprogramm, mit
dessen Hilfe Sie Probleme innerhalb Ihrer Datenbestände aufdecken können.
Hierfür stehen Ihnen diverse Optionen und Menüpunkte zu Verfügung.
Bei allen Tests gibt es zwei mögliche Überschriften,
die Sie darauf hinweisen, wie kritisch dieser Fehler ist.
************************ A C H T U N G
***********************
Dies ist eine Meldung, dass etwas in Ihrem System
nicht in Ordnung ist, sich aber ohne Komplikationen beheben lässt, oder
eventuell nur als Hinweis verstanden werden soll.
************************* F E H L E R
************************
Hierbei handelt es sich um Fehler, die schnell
behoben werden sollten, damit es beim Weiterarbeiten keine unnötigen weiteren
Folgefehler gibt.

---

## Fibu Testlauf (Nachlauf)

Fibu Testlauf (Nachlauf)
-*
========================================================================== Hier
Startet die Test Nachlaufroutine
artietest
Anlage einer neuen Partie wird in diesem Bereich
getestet.

---

## Fibu Schnittstellen

Fibu Schnittstellen

---

## FIBU-XLSX-Import

FIBU-XLSX-Import
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datenübernahme
Direktsprung
[DUEB]
Um für Excel-Dateien im xlsx-Format einen Datenimport
in die Finanzbuchhaltung durchzuführen, kann eine Datenübernahme definiert
werden. Es finden hier keine Tests statt, ob eine Datei bereits eingelesen
wurde. Dies muss durch geeignete betriebliche Maßnahmen sichergestellt
werden.
Um die Excel-Verarbeitung zu aktivieren, müssen im
Block Prozeduren folgende Werte eingetragen werden:
Steht man im Feld „Programm 1“, so können mit F3 auch
die hier einzutragenden Werte ausgewählt werden. „Programm 1“ und „Programm 2“
sind von Branchen-ERP bereitgestellte Funktionen, die die Verarbeitung steuern.
Das Programm „dueb_import2db_xlsx“ importiert die
Dateien in das Formulararchiv. Gleichzeitig wird jede .xlsx-Datei in ein XML
umgewandelt und in der Spalte „FA_XMLErweiterung“ der Tabelle Formulararchiv
gespeichert. Im Archiv sind die importierten Dateien unter dem Belegtypen
„Fibu-Datenübername XLSX“ wieder zu finden. Außerdem wird in der Tabelle
„dueb_import“ die Fa_id und die Fa_mndnr des Archiveintrags vermerkt.
Das Programm „dueb_import_xlsx“ versucht mithilfe der
unter „Prozedur“ eingetragenen privaten Datenbankprozedur die Daten zu
verarbeiten. Dabei werden vor der Belegerstellung erst alle Daten auf Konsistenz
geprüft und erst danach werden die Belege erstellt. Dadurch ist sichergestellt,
dass nicht nur Teile aus der Datei verarbeitet werden.
In das Feld Prozedur muss eine private Prozedur
eingetragen werden, die das XML aus der Spalte „FA_XMLErweiterung“ ausliest und
alle erforderlichen Daten zurückliefert (siehe Resultset der Beispiel-Prozedur).
Mit der Funktion
Prozedur bearbeiten
kann die Funktion direkt bearbeitet oder neu angelegt werden. Bei der Neuanlage
wird ein Gerüst mit dem benötigten Resultset vorgegeben.
Beispieldaten:
ident;telefon;mail;klasse;referenznr;beledatum;hauptkonto;gegenkonto;betrag;sh
1;0431
99020;Support@Branchen-ERP;ZA;ABC;20.09.202
[...]


---

## FIBU-XML-Import

FIBU-XML-Import
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datenübernahme
Direktsprung
[DUEB]
Der Import von XML-Daten wie sie unter
www.Branchen-ERP/schema/finanzbuchhaltung
beschrieben sind, kann auch über die
Datenübernahme-Schnittstelle
eingespielt werden.
Dazu muss unter „Programm 1“
fibu_xml2db %F
eingetragen werden. Diese
Funktion prüft, ob der Aufbau des Dokuments den Vorgaben entspricht. Eventuell
auftretende Fehler werden anschließend in einem Textdokument ausgegeben. Ist das
Dokument formal in Ordnung, werden die Daten in der Tabelle FIBUXMLIMPORT
gespeichert, um dort dann weiter verarbeitet zu werden. Zur Prüfung der formalen
Richtigkeit gehört auch die Validierung des XML-Dokumentes gegen die
Schemadefinition. Ist diese nicht im XML-Dokument selbst angegeben, so kann sie
in der Einrichtung unter „Schemalocation“ eingetragen werden. Für das hier
verwendete Schema muss sie folgendermaßen lauten:
https://www.Branchen-ERP/schema/finanzbuchhaltung/fibu-import-schema.xsd
Unter „Programm 2“ muss dann
fibu_xml_import
eingetragen werden. Die
Daten werden hier erst auf Inhaltliche Richtigkeit geprüft (Existieren die
Konten? Ist der Steuersatz gültig usw.) und am Ende in einem Textdokument
aufgelistet. Nur wenn alle Daten in Ordnung sind, werden die Belege
erstellt.
Das Angeben der Prozedur ist hier optional. Wird keine
private Prozedur angegeben, dann wird die Standard-Datenbankprozedur von Branchen-ERP
verwendet. Gibt man hier eine nicht existierende Prozedur an, so wird die
Branchen-ERP-Datenbankprozedur als Vorlage verwendet und als Template zur Verfügung
gestellt.
Ist der Aufbau der zu importierenden Daten fehlerhaft,
so ist es
nicht
notwendig eine neue Datei mit neuer Übertragungsnummer zu
generieren, um erneut importiert zu werden. Über die Option „
Fehlerhaften Daten überschreiben?
“
kann eingestellt werden, ob die Datei erneut eingespielt werden darf.
Sind nur die Daten fehlerhaft, weil z.B. die Periode
nicht offen war oder ein Konto nicht angelegt war
[...]


---

## Forderungsgruppen

Forderungsgruppen
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Forderungsgruppe
Direktsprung
[FORG]
Die aus den einzelnen Rechnungen / Offenen Posten
eines Personenkontos resultierenden Forderungen bzw. Verbindlichkeiten müssen
auf den Bestandskonten verbucht und bei Bezahlung wieder ausgebucht werden. In
Referenz-ERP ist es möglich die Kunden in verschiedene Gruppen einzuteilen z.B.
"Großkunden",
"Landwirte", "Baustoffhändler"
und diesen Gruppen auch
unterschiedliche Bestandskonten zuzuordnen. Hierzu dienen die Forderungsgruppen.
Feld
Beschreibung
Nummer
Identifikation der Forderungsgruppe.
      Diese wird als Verweis im Kunden-/Lieferantenstamm hinterlegt.
Bezeichnung
Die
      Bezeichnung dient lediglich zur textlichen Beschreibung der
      Forderungsgruppe und hat keine Programmfunktion. Sie wird in Auswahllisten
      bzw. Reporten zur Anzeige verwendet.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Konto Forderungen/ Konto
      Verbindlichkeiten
In
      Referenz-ERP können Personenkonten sowohl Forderungen als auch Verbindlichkeiten
      ausweisen (Kontokorrent- Kunden). Daher ist es notwendig in der
      Forderungsgruppe sowohl ein Forderungs- als auch Verbindlichkeitskonto
      anzugeben. Die Konten können mit
F3
ausgewählt werden. In dieser
      F3-Auswahl werden nur Bilanzkonten angeboten, deren Erfassungssperre
      gesetzt ist, die kein Steuerkonto sind und die nicht als Erlöskonto
      verwendet werden.
ACHTUNG: Forderungs- und
      Verbindlichkeitskonten dürfen nicht direkt bebucht
      werden.
Wie
      die Forderungs- und Verbindlichkeitskonten eingerichtet werden sollten,
      hängt zum einen von der Firmeneigenen Struktur und zum anderen von dem
      Steuerungsparameter „Methode der Forderungs-Verb-Zuordnung“
      ab.
Ersatzkonto DATEV
Dieses Feld erscheint nur, wenn das
      DATEV-M
[...]


---

## Format 3.0 einrichten

Format 3.0 einrichten
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Datev
-Import Lohndaten
Funktion „Format 3.0 einrichten“
Bei dem Format3.0 handelt es sich um eine Datei im
CSV-Format (Comma Separated Values). Im DATEV-Standard werden Textfelder in
Doppelt Hochkomma gesetzt und die Daten mit Semikolon getrennt, Die Daten haben
eine feste Position innerhalb einer Zeile. Diese Werte sind bereits von Branchen-ERP
vorgegeben, können jedoch angepasst werden:
Die Funktion „
Original wiederherstellen
“
F6
setzt die Werte wieder auf die Vorgaben
zurück.

---

## Formular Fibu-Infofenster

Formular Fibu-Infofenster
In der Finanzbuchhaltung ist es oft notwendig
zusätzlich Informationen – z.B. Kontosaldo, Telefonnummer, … - zu einem Konto
anzuzeigen. Diese Informationen werden in einem blau eingefärbten Bereich –
Fenster -  angezeigt, der selber eingerichtet und pro Bedienerklasse
hinterlegt werden kann. Dieses Fenster findet man unter anderem in der
Konteninformation oder der OP-Verwaltung.
Die Informationen werden über ein Formular vom Typ 240
„Fibu-Bildschirm-Konteninfo“ zusammengestellt. Zu diesem Formular existieren
vier Bereiche:
•
625 Bildschirm-Personenkonten
•
626 Bildschirm-Bilanzkonten
•
627 Bildschirm-GuV-Konten
•
628 Bildschirm-Oberkonten
Es kann also pro Kontotyp eine andere Darstellung der
Information hinterlegt werden. Von Branchen-ERP wird eine Standardeinrichtung mit der
Formularnummer -99 ausgeliefert.
Für Kurzlisten, die dort gedruckt werden, wo
Fibu-Infofenster aktiv sind, kann dieser Bereich auch mit angedruckt werden.
Dazu müssen zwei Einrichtungen vorgenommen werden:
1.
In dem verwendeten Kurzlistenformular muss die Druckposition ID_FIBU_INFO
eingerichtet werden.
2.
In dem SQL-Text der betroffenen Auswahllisten und F3-Auswahlen muss das
Schüsselwort FIBU_INFO gefolgt von den Feldern, die das Konto bzw. das Jahr
bestimmen, eingerichtet sein. Beispiel:
FIBU_INFO :KONTO,
:JAHR
Für die Standard-Auswahllisten ist dieses Schlüsselwort bereits in
den SQL-Texten enthalten, so dass ggf. nur das Kurzlistenformular angepasste
werden muss.

---

## Formularklassen

Formularklassen
Die Formularklassen geben wieder, ob es sich um
Zahlungsausgang
oder um
Zahlungseingang
handelt. Eigene
Formularklassen zu erfassen ist nicht möglich.

---

## Frachtsätze

Frachtsätze
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Ändern
Frachtsätze
Innerhalb einer Frachttabelle kann es mehrere
Frachtsätze für unterschiedliche Frachtzonen definiert werden.
Feld
Bedeutung
Frachtzone
Frachtzone
für die diese
      Berechnung gelten soll.
Gültig ab
Gültigkeitsdatum des
      Frachtsatzes
Ab
      Menge
Mindestmenge, ab der die Berechnung
      gelten soll.
Prozent/Preis
Prozentualer Wert oder Betrag der
      gelten soll.
Einheit
Einheit (für entfernungsabhängige
      Berechnungen)
Formel
Frachtformel,
die hier
      gelten soll

---

## Sperren

Sperren
Manche Felder auf der Registerkarte Sperren sind von
der gewählten Vorgangsklasse abhängig.
Vorbelegungen
Maskenfeld
Vorbelegung
Bedeutung
Vorbel. Fibu-Sperre
Nein
Beleg wird nach der Erzeugung gegen
      den Übertrag in die Fibu gesperrt. Beleg muss manuell Freigegeben
      werden.
Vorbel. Umw-Sperre
Nein
Der
      Beleg kann nach der Erzeugung nicht Umgewandelt werden. Beleg muss manuell
      Freigegeben werden.
Vorbel. RAB-Sperre
Nein
Der
      Beleg kann nach der Erzeugung nicht in das rechnungsausgangsbuch
      übernommen werden. Beleg muss manuell Freigegeben werden.
Vorbel. Filia-Sperre
Nein
Wirkungslos
Behandlungen exportierter Vorgänge
Hier kann eingestellt werden, ob bei einem Beleg der
das Kennzeichen V_StatusExport im Vorgangstamm ungleich 0 hat folgenden
Funktionen zu gelassen werden.
Maskenfeld
Vorbelegung
Löschen erlaubt
Nein
Stornieren erlaubt
Nein
Umwandeln erlaubt
Nein
Korrigieren erlaubt
Nein
Kennzeichen bei Erfassungen
Maskenfeld
Vorbelegung
Bedeutung
Persönliches Kennzeichen
      abfragen
Nein
Hier
      kann eingestellt werden, ob der Bediener beim Erfassen eines Vorgangs sein
      Persönliches Kennzeichen eingeben muss. Das persönliche Kennzeichen wird
      im Bedienerstamm festgelegt. Der Vorgang wird dann unter dem Bediener
      erfasst, der sein Kennzeichen angegeben hat. Dies kann zur Kontrolle
      eingesetzt werden, wenn mehrere Bediener sich ein Arbeitsplatz
      teilen.
EPA
      hebt Kennzeichenabfrage auf
Nein
Hier
      kann eingestellt werden dass die Kennzeichenabfrage per EPA für eine
      bestimmte Bedienerklasse ausgestellt werden kann.
Sonstige Sperren
Maskenfeld
Vorbelegung
Bedeutung
Bearbeitungssperre auch bei
      Folgebelegen
Nein
Die
      Sperre legt fest, ob Folgebelege aus einem Quellbeleg dieser
      Vorgangsklasse geändert oder gelöscht werden können, wenn der Quellbeleg
      eine Bearbeitungssperre gesetzt hat.
Korrektur mit Doppelklick
      verbieten
Nein
Die
      Sp
[...]


---

## Funktionen in der OP-Verwaltung

Funktionen in der OP-Verwaltung
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
.
Um mit der OP Verwaltung zu arbeiten gibt es
verschiedene Funktionen. Diese sind im Einzelnen:
Darstellung der Offenen Posten - F2
Für unterschiedliche Fragestellungen gibt es
verschiedene Darstellungsformen der Offenen Posten. Sie können mittels
F2
-
Auswahl abgerufen werden:
Es werden die für den Benutzer / das Unternehmen
zugelassenen Varianten angezeigt. Alle mit „OP’s“ beginnenden Varianten beziehen
sich auf noch nicht verrechnete Belege, alle anderen Varianten beinhalten auch
bereits verrechnete Belege. Bei diesen Varianten ist zu beachten, dass in der
OP-Verwaltung keine weitere Eingrenzung – außer nach Kontonummer – vorgesehen
ist.
Wechsel der Kontos – F3
Mit Betätigung von
F3
wird in das Feld zur
Eingabe der Kontonummer gewechselt und es kann ein neues Konto angewählt
werden.
Ändern eines OP –
F5
Die Skonto- und Valutadaten eines OP können verändert
werden. Nach Auswahl des OP wird die Funktion mit
F5
ausgelöst:
Die Eingabe von Skontobetrag oder -satz löst eine
Berechnung des Skontosatzes bzw.  Skontobetrages aus. Die Zahlungsbedingung
kann eingetragen werden und Skonto- sowie Valutadatum überschrieben werden.
HINWEIS
:
Das Valutadatum ist nicht
änderbar, wenn der Beleg bereits zur Zinsberechnung herangezogen wurde. Es
erscheint dann ein Hinweis auf der Maske:
Dann wird noch ggf. bei Änderung des Valutadatums
geprüft, ob der Beleg sich bereits in einer Mahnliste befindet. Wie reagiert
werden soll kann per Einrichterparameter eingestellt werden. Es stehen folgende
Einstellungen zur Auswahl:
•
Ignorieren
: Es wird kein Test durchgeführt (dies ist das alte
Verhalten)
•
Fehler
: Das Datum kann nicht geändert werden, wenn der OP bereits
in einem Mahnvorschlag existiert
•
Warnung
: Es wird geprüft, ob der OP bereits in einer
Mahnvorschlagsliste existiert. Es erfolgt ein entsprechender Hinweis. Eine
Änderung des Datums ist jedoch möglich
[...]


---

## Funktionen Vorgangserfassung Kopf

Funktionen Vorgangserfassung
Kopf
Abbruch (F10)
Abbruch der Erfassung, zurück zum Ausgangsmenü.
Abschluss
Vorgang wird gespeichert. Zusätzlich besteht die
Möglichkeit zur Durchführung eines Sofortdrucks.
Abschluss mit Signatur (UMSCHALT+STRG+F8)
Vorgang wird unter Verwendung einer integrierten
Signatur abgeschlossen. Zusätzlich besteht die Möglichkeit zur Durchführung
eines Sofortdrucks
Abschluss / Lieblingsdruckerdruck (STRG+F5)
Diese Funktion ermöglicht es, ausgewählten Vorgängen
für den Druck einen anderen als den Standarddrucker zuzuordnen. Zusätzlich kann
zum Ausdruck ein anderes Formular durch Markieren der Unterklasse gewählt
werden.
Abschluss / Nächster Beleg (F6)
Vorgang wird zunächst gespeichert. Zusätzlich besteht
die Möglichkeit zur Durchführung eines Sofortdrucks. Waren in der übergeordneten
Auswahlliste weitere Belege markiert, so erfolgt ein Wechsel zum nächsten Beleg
in der Auswahl.
Allgemeine Zuordnung (F9)
Abfrage von Informationen zu diesem Bereich (siehe
unten).
Hier werden sowohl generelle, nicht mehr änderbare,
sowie änderbare Einstellungen angezeigt. Da Veränderung von Einstellungen auf
dieser Maske möglicherweise Preis- und Wertänderungen auslösen können, müssen
Änderungen hier mit Bedacht durchgeführt werden.
Andere Unterklasse / Andere Vorgangsklasse
(UMSCHALT+F11)
Hier kann auf eine andere als die gerade verwendete
Vorgangsklasse / Vorgangsunterklasse umgeschaltet werden: Mit einem
Vorgangsklassenwechsel von Rechnung zu Angebot wird aus einer Rechnungserfassung
ein erfasstes Angebot unter Mitnahme aller Werte; dabei wird der Nummernkreis
des Angebotes gezogen. Nach dem Vorgangsklassenwechsel befindet man sich in der
Zielvorgangsklasse. Will man weiter Rechnungen erfassen, muss man dahin
zurückkehren.
Mit dem Unterklassenwechsel kann z.B. ein anderes
Formular gezogen werden. Mit dem Wechsel von Rechnung auf Barverkauf werden
allerdings auch Funktionen und Buchungsabläufe, wie Zahlungsverkehr
aufgerufen.
Anschriften

[...]


---

## Funktion Kassenabschluss

Funktion Kassenabschluss
Der Kassenabschluss ist auf 2 Arten möglich:

---

## GDI-Fibu

GDI-Fibu
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Funktion
F9
Import Starten
Funktion
F4
Importdatei lesen
Direktsprung
[FIIM]
Beim Import aus der GDI-Fibu handelt es sich um echte
Finanzbuchhaltungsbelege, also um Eingangsrechnungen, Ausgangsrechnung sowie
Zahlungsbelege. Der Satzaufbau der zu importierenden Datei hat wie folgt
auszusehen:
Satzaufbau
Es werden nur die mit [Bu] beginnenden Datensätze
ausgewertet.
Kennzeichen
Feldinhalt
<Art>=
Belegart
<BNr>=
Belegnummer
<Dat>=
Buchungsdatum
<Txt>=
Buchungstext
<Btr>=
Buchungsbetrag (incl. S/H falls
      vorgegeben)
<StS>=
Steuerschlüssel (falls ein
      Steuerbetrag angegeben ist und der Steuerschlüssel nicht beim Sachkonto
      hinterlegt ist)
<StB>=
Steuerbetrag (nur bei
      Sachkontenbuchungen)
<ZBd>=
Zahlungsbedingung
<RBt>=
Rechnungsbetrag
<BDa>=
Belegdatum
<BlL>=
Belegnummer Lieferant (Nur bei
      Kreditoren)
<ZaV>=
Zahlvermerk (L/E/V)
<VDa>=
Valutadatum (nur Debitoren)
<SpV>=
Sperrvermerk
<ZDa>=
Zahldatum (nur bei Kreditoren)
<WKz>=
Währung Kennzeichen
<WBt>=
Fremdwährungsbetrag
<Kst>=
Kostenstelle
<Ktr>=
Kostenträger
<KtO>=
Kostenträger Originärbuchung
<Skt>=
Skonto
<ZAr>=
Zahlartnummer
<ISO>=
ISO-Währungscode
<SkW>=
Skonto in Fremdwährung
<SKf>=
Skontofähiger Betrag
<GKt>=
Gegenkonto
Die Gegenbuchungen werden jeweils mit
‘
<GKt>=’
eingeleitet. Es muss mindestens eine Gegenbuchung
angegeben werden. Die Mindestangaben hierbei sind die Kontonummer und der
Buchungsbetrag. Das Buchungsdatum wird immer aus der Buchung herangezogen. Die
Felder Belegart, Belegnummer und Buchungstext werden aus der Buchung übernommen,
falls sie nicht für die Gegenbuchung angegeben wurden. Die Summe aus den
Buchungsbeträgen ‘
<Btr>=’
und den Steuerbeträgen ‘
<StB>=’
der Buchung und aller Gegenbuchungen müssen 0.00 DM ergeben.
Alle in
Buchungssätzen angegebenen Konten müssen in der Fibu angelegt sein bzw. vor der
Buchung als Stammsatz übergeben worden sein.
Beispieldaten
[GDI-Fibu]:[GDI-FACTUR
[...]


---

## Gutschrift aus Rechnung / Sammel- GU aus Rechnung

Gutschrift aus Rechnung / Sammel- GU aus Rechnung
Erstellt aus selektierten Rechnungen Einzel- oder
Sammelgutschriften, die dann in der Anwendung „Gutschriftbearbeitung“ zu finden
sind. In der Finanzbuchhaltung erfolgt eine Buchung auf der Gegenseite des
Originalbeleges oder, falls über die Buchungsklasse umgesteuert, eine Buchung
auf anderen Konten (z.B. Erlösschmälerung).

---

## Importierte Vorgänge

Importierte Vorgänge
In der Anwendung
eRechnung
[XRE]
gibt die Variante
Import Vorgänge
. In dieser sind
importierte eRechnungen aufgelistet. Haben diese den Status „Import
abgeschlossen“, so können daraus Waren- bzw. FiBu-Vorgänge erstellt werden.
Dazu können Sie die Funktion
Im Browser anzeigen
aufrufen, um die
eRechnung in einem visualisierten Format zu sehen.
Dann können Sie die Funktionen
Eingangsrechnung erfassen
bzw.
Eingangsgutschrift erfassen
aufrufen, um
die entsprechenden Belege manuell zu erfassen. Dabei werden wenn möglich
Kundennummer und die ID der eRechnung vorbelegt.
eRechnungen, zu denen ein Beleg erfasst wurde,
bekommen den Status „Beleg erstellt“.

---

## Importverfahren der Finanzbuchhaltung

Importverfahren der
Finanzbuchhaltung
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Direktsprung
[FIIM]
Bei der Verwendung der Standardimportschnittstelle
muss die Relation Fibuimport gefüllt werden. Das Füllen kann über eine bereits
im korrekten Format vorliegende DBF-Datei geschehen, über eine JPL-Prozedur oder
über ein vorgeschaltetes Makroskript. Die Daten dieser Relation werden
anschließend auf ihre Gültigkeit getestet. Bei erfolgreichem Test werden sie
dann in Belege umgewandelt, die in der Primanota kontrolliert werden können.
Alle Optionen für den Import findet man unter
F9
"Und
los...."
Feldbeschreibung
Feld
Beschreibung
IDENT
Integer Zahl zur eindeutigen
      Identifizierung. Interne Verwendung. Es genügt eine einfache
      Durchnummerierung. Es ist auch möglich, Belege mit mehreren
      Gegenpositionen zu erfassen. Dabei müssen zusammengehörende Zeilen in
      IDENT, BELKALSSE, BELDATUM, HAUPTKONTO, (SOLLHABEN) JAHR und PERIODE
      übereinstimmen.
POSZAEHLER
Zähler für die Positionen, falls
      Belege mit mehreren Gegenpositionen verwendet werden. Wenn nicht
      angegeben, dann wird er standardmäßig auf 1. gesetzt. Dies bedeutet dann
      aber gleichzeitig, dass das Feld IDENT nur eindeutige Werte annehmen darf,
      da der Primarschlüssel auf den Feldern
IDENT
und
POSZAEHLER
liegt.
FIIMPART
Hiermit wird gesteuert, welche Werte
      aus den Stammdaten von Referenz-ERP vorbelegt bzw. errechnet werden sollen.
      Mögliche Ausprägungen
      sind:
0
      Standardmethode: Steuerwert wird nicht berechnet
1
      Lagerlandmethode: Einspielung mit Neuberechnung der Steuer
2
      Nur Sachkontenbuchungen
3
      Nur Sachkontenbuchungen mit Verarbeitung der Kostenstelle
4
      Import GDI-FIBU
BELKLASSE
Integer Zahl. Die Belegklasse, so
      wie sie von Referenz-ERP vergeben wird. Belegklasse und Sollhaben sind für AR,
      AG, ER und EG eng miteinander verknüpft. Siehe
SOLL
[...]


---

## Info

Info
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register Info
Direktsprung
[ANWR]
.
Hier befindet sich ein Feld „Kommentar“. In diesem
Feld stehen einige Schlüsselwörter, die den Report beschreiben. Zum einen wird
hier klassifiziert, in welchen Bereich (FIBU, Warenwirtschaft, Stammdaten,
Inventur, Rohwarenauswertung, Rohwarestamm oder Planung) die Reporte gehören.
Zum anderen besteht die Möglichkeit mit
F3
eine Auswahl aufzurufen, die
weitere Schlüsselwörter enthält, die eine Bedeutung haben.
Text
Bedeutung
NEWDESIGN
Die
      Finanzbuchhaltungsreporte wurden auf ein Design umgestellt, das sich über
      die
Crystal Report Optionen
steuern lässt. Steht dieses
      Schüsselwort im Kommentar, so steuert das Programm das Erscheinungsbild
      (Einfärben des Titels, Darstellung der Grafik, …) des Reports.
NOGROUPTREE
Auf
      der linken Seite der Reportvorschau erscheint grundsätzlich ein
      Gruppenbaum, in dem man die Gruppe des Reports aufblättern kann. Soll
      dieser Baum nicht erscheinen, so trägt man NOGROUPTREE ein. Reporte ohne
      Gruppen werden standardmäßig ohne Gruppenbaum dargestellt.
NOLIST
Dieser Report erscheint nicht in der
      Anwendung
[LST]
BITMAP
Nur
      informatorisch. Diesem Report wurde eine Graphik zugewiesen.
SHADOWLINE
Dies
      ist nur informatorisch und besagt, dass der Report auf die
CRW-Optionen
reagiert und je
      nach Einstellung jede zweite Zeile grau einfärbt.

---

## Infoblätter drucken

Infoblätter drucken
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Funktion
Infoblätter drucken
F8
Direktsprung
[KOD]
Bei Infoblättern wird der aktuelle Stand der
ausgewählten Konten herausgesucht und über den Formulardruck ausgegeben.
Infoblätter basieren
nicht
auf einmal festgeschriebenen Daten so wie es
Kontoblätter tun, sondern geben jeweils den aktuellen Stand des Buchungsstoffs
wieder. Sie können daher jedes Mal anders aussehen.
Neben dem Formulardruck können Infoblätter auch über
einen Crystal Report gedruckt werden. Diesen findet man im Menü unter
Hauptmenü
Abschlussarbeiten
Kontoblätter
Infoblattdruck
Direktsprung
[KOID]

---

## Inventur in Kurzform

Inventur in Kurzform
Das Wirtschaftsjahr für das neue Jahr muss
eingerichtet sein
[JAHR]
:
Direktsprung
[JAHR]
, dann
Neu
(F8)
Geschäftsjahr = XXXX
Ausführliche Bezeichnung =
„Wirtschaftsjahr
XXXX“
Datum Beginn - Datum Ende
Periodeneinteilung wie Vorjahr = JA
Buchungsjournal Nr.  für den Nr.-Kreis oder
F3
Kleinstes / größtes Datum = wird bei Datumseingaben in
der DB geprüft!
Warndatum Unter- / Überschreit. = 01.01. bzw. 31.12.
neues Jahr
F10 / F11 Perioden Fibu / Ware aufrufen und prüfen
(Schaltjahr!!)
ESC
und
Speichern
(F9)
Periode 1 in der WAWI des neuen Wirtschaftsjahres muss
eröffnet werden
[PERER]
.
Der Inventur-Belegnummern - Zählkreis muss
eingerichtet sein
[NKS]
[NKZ]
.
Unterschiedliche Inventuren müssen in Gruppen
eingeteilt werden
[IVG]
,
z.B. Hauptinventur mit JW (1),  Zwischeninventuren
unterschiedlicher Warengruppen (2).
Über die
Artikelstapelkorrektur
muss die
entsprechende Inventurgruppe
(z.B. 1 = Hauptinventur JW) in die Artikel
eingetragen werden.
Achtung
!
Fehlt die Inventurgruppe in den Artikeln bei der Inventurvorbereitung,
dann
werden keine Artikel eröffnet. Inventurgruppen dürfen nach Inventureröffnung
innerhalb
eines Inventurjahres nicht geändert werden!
Ein Inventurstamm pro Inventurgruppe
muss
angelegt werden
[IVS]
.
Bitte beachten:
Typ der
Inventur:
Hauptinventur JW oder Zwischeninventur
Art der
Inventur:
Stichtag oder Stichtag versetzt
Inventurvorbereitung starten
[IVV]
Inventureröffnung
F5
Zählliste alle
Artikel
ausdrucken (Vorbelegung beachten!!)
Zählliste
Blanko
Blankoliste mit Artikel / Menge über alle Artikel
Inventuraufnahme
[IVA]
(Erfassen der Inventurbestände
lt. Zählliste)
mit Bewertungspreis (Voreinstellung lt.
Inventurstamm)
automatische Bewertung lt. Bewertungsgruppe im
Artikelstamm
folgende Optionen bestehen:
Einzelkorrektur
F5
Erfassung
F8
Erfassungsprotokoll
(Druck)
Mobile Datenerfassung
folgende Prüf - Auswahllisten können aufgerufen
werden:
Artikel ohne Inventureröffnung
Bestan
[...]


---

## Jahreswechsel

Jahreswechsel
Der Jahreswechsel in der Finanzbuchhaltung
(Direktsprung JAHRW) kann für Sach- und/oder Personenkonten durchgeführt werden
und kann beliebig oft – falls noch Nachbuchungen durchgeführt wurden –
wiederholt werden. Bevor der Jahreswechsel durchgeführt wird, sollte jedoch die
Checkliste durchgegangen werden.

---

## Jahreswechsel durchführen

Jahreswechsel durchführen
Hauptmenü
Abschlussarbeiten
Jahreswechsel
Jahreswechsel
Direktsprung
[JAHRW]
Beschreibung
Abschlussjahr
Hier
      werden die Informationen für den Beleg, der die Abschlussbuchungen enthält
      hinterlegt. Hat man das Jahr angegeben, werden die Abschlussperiode und
      das Belegdatum laut Stammdaten vorgeschlagen.
Eröffnungsjahr
Das
      Jahr wird als Abschlussjahr + 1 vorgeschlagen. Eröffnungsperiode und
      Belegdatum ergeben sich aus den Stammdaten.
BK/Belegnummer
Hier
      wird der Nummernkreis vorgeschlagen wie er unter „
Fibu-Vorgangszuordnung
“
      (Direktsprung NKF) hinterlegt ist.
Eröffnungsbilanzkonto
Kontonummer des zu verwendenden
      Kontos für die Eröffnungsbuchung. Wird aus dem
Mandantenstamm
vorbelegt.
Schlussbilanzkonto
Kontonummer des zu verwendenden
      Kontos für die Abschlussbuchung. Wird aus dem
Mandantenstamm
vorbelegt.
Kontenbereich
Hier
      kann man den Bereich angeben, für den der Jahreswechsel durchgeführt
      werden soll. Folgende Bereiche sind möglich:
•
Bilanzkonten
•
Debitoren
•
Kreditoren
•
Kontokorrent
•
Personen- und
      Bilanzkonten
Hat man alle Angaben gemacht, kann man mit
F9
den Jahreswechsel starten. Es werden vor dem Start noch Test vom Programm
vorgenommen, damit nicht versehentlich Fehler beim Jahreswechsel auftreten:
•
Die Abschlussperiode muss existieren und offen sein.
•
Das Eröffnungsjahr muss hinter dem Abschlussjahr liegen.
•
Die Eröffnungsperiode muss existieren und offen sein.
•
Eröffnungs- und Abschlussbilanzkonto muss existieren und als
Vortragskonto gekennzeichnet sein.
•
Es dürfen keine ungebuchten Belege im abzuschließenden Jahr
existieren.
•
Wenn man im Sachkontenstamm die Option „
Ist Unterkonto von
“
verwendet, muss die letzte Normalperiode offen sein.
•
Wenn der Steuerungsparameter 968 „Forderungskonten umbuchen“ auf
Ja
steht, dann dürfen keine Änderungen an Forderungsgruppen existieren,
die noch nicht durch die Reorganisation gelaufen sind.
•
We
[...]


---

## Journal / Ereignisprotokoll

Journal / Ereignisprotokoll
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Journal/Ereignisprotokoll
Direktsprung
[JOUR]
Hier stehen insgesamt fünf Varianten zur Verfügung,
die einen Überblick über den Stand der Buchungen geben. Die ersten drei
Varianten zeigen je Buchungsjahr die erstellten, gedruckten und ungedruckten
Journale mit ihrem Status an. Von hier aus können die Journale gedruckt werden.
Neben dem frei einrichtbaren Formulardruck
Druck Journal
F9
stehen
auch fest definierte Reporte „
Journal chronologisch
“ und „
Journal nach
Belegnummer
“ zur Verfügung.
In der Variante
Fehlerliste Buchungen
werden
eventuell auftretende Fehlbuchungen angezeigt. In dieser Variante steht ein
Report zur Verfügung, der die Fehlbuchungen auflistet.

---

## Kassenabschluss

Kassenabschluss
1.
AcashUeb fügt „hängende“ Geldübergaben oder Abschöpfungen als Geldübernahmen in
die noch offene Sitzung ein.
2.
Abgebrochenen Beleg (BelegId=0) dieser Kasse bereinigen
3.
Nur bei SPA_ABSCHOEPFUNG_AUTOMATISCH:
a.
Wechselgeld entnehmen
b.
Ggf. Zählung durchführen, bei Unterkasse mit automatischer Abschöpfung wird so
getan, als wäre eine Zählung erfolgt.
Nur bei Abschluss mit Zählung bzw. Zählung nn passiert
all dieses
•
Kassenbericht abgeschlossen setzen
•
Bei Unterkasse: Bargeldabschöpfung an Hauptkasse
•
Umbuchung des Bargeldes vom Kassenkonto auf das eingerichtete
Bargeldkonto
•
Umbuchung des Manko vom Bargeldkonto auf das Differenzenkonto bzw. des
Überschuss vom Differenzenkonto auf das Bargeldkonto
•
Umbuchung der Stornos auf Stornokonto
•
Umbuchung der Zahlungsmittel auf die jeweils zugeordneten Konten je nach
EPA Einstellung EINZELBUCHUNG als eine eben solche oder als Sammelbuchung je
Zahlungsmittel
Nur bei Hauptkassen oder bei Unterkassen, die nicht
automatisch an Hauptkassen abschöpfen: Erstellung eines maschinellen
Abschöpfungsbeleges über alle unbaren Zahlungsmittel. Dieser Beleg wird nicht im
Kassenbericht gebucht, damit die Verteilung der Zahlungsmittel nicht verloren
geht.
Ohne Zählung passiert folgendes:
•
Prüfung ob Abschluss ohne Zählung erlaubt (EPA)
•
Kassenbericht abgeschlossen setzen
•
Autoabschöpfung und Autobuchung genau wie oben

---

## Kassenabschluss Hauptkasse, automatische Einreichung

Kassenabschluss Hauptkasse, automatische Einreichung
Betroffene SPA-Einstellungen:
„Aut. Buchung von Finanzvorgängen in Fibu“, wird
üblicherweise nur abgeschaltet, wenn keine Referenz-ERP Fibu angeschlossen ist.
„Umbuchung der Zahlungsmittel auf Konten“= ja bewirkt,
dass Zahlungen automatisch beim Kassenabschluss auf definierte Konten umgebucht
werden. Barzahlungen werden immer vom Kassenkonto auf das angegebene
Bargeldkonto umgebucht. Die Einstellung „nein“ bedeutet im Übrigen, dass die
Zahlungsmittel vorgetragen werden und in den folgenden Sitzungen nur einzeln
eingereicht werden können. Die automatische Umbuchung bezieht sich stets nur auf
die Zahlungsmittel der jeweiligen Sitzung.
Folgende Fibu Konten sind beteiligt:
Kassenkonto Fibu lt. Kassenverwaltung
Kassenverrechnungskonto lt. Kassenverwaltung
Bargeldkonto lt. Kasseneinstellung
Scheckkonto lt. Kasseneinstellung
Gutscheinkonto lt. Kasseneinstellung
Kreditkartenkonto lt. Kasseneinstellung
Bankeinzugskonto lt. Kasseneinstellung
Differenzkonto Zählung lt. Kasseneinstellung
Stornokonto lt. Kasseneinstellung
Verrechnungskonten der Hausbanken (Einreichungen)
Bisheriges Verfahren Kassenabschluss
Unterkasse mit Abschöpfung an Hauptkasse:
Bargeld:
1.
Unterkasse erzeugt einen Einreichungsbeleg über die Höhe des Bargeldsolls laut
Fortschreibung des Kassenbestands.
2.
Bar-Soll der Unterkasse wird um Einreichung gemindert, Einreichungssumme
erhöht.
3.
Falls automatische Umbuchung von Zahlungsmitteln eingestellt ist, so werden bis
zu 4 Fibu-Belege erstellt:
a.
Bargeldeingang (Kasse an Bargeldkonto)
b.
Bargeldausgang (Kasse an Bargeld)
c.
Zähldifferenz (Differenzenkonto an Bargeld)
d.
BV Storno Saldo (Kasse an Storno)
4.
Falls keine automatische Umbuchung von Zahlungsmitteln vorgesehen ist, so
erfolgt eine Umbuchung des Bargeldsaldo (Unterkasse an Hauptkasse).
5.
Für die Hauptkasse wird ein Einreichungsvermerk eingerichtet. Bei der nächsten
Gelegenheit (Bearbeitung einer Zahlung, Kasseneröffnung od
[...]


---

## Kontendefinition

Kontendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Kontendefinition
Direktsprung
[CCD]
Hier legt man eine Liste von Konten an, auf die man
bei der Berechnung später zugreifen will. Im unten gezeigten Beispiel kann man
später über das Kürzel AKZ auf die Summe der Wechselverbindlichkeiten in einem
bestimmten Zeitraum, der sich später in einer Auswahlliste (Direktsprung
[CCA]
) angeben lässt, zugreifen. Die hier eingegebenen Konten können
Sach- oder Oberkonten sein. In einer Kontendefinition kann ein Konto nur einmal
erscheinen. Doppelt angegebene Konten werden nur einmal gespeichert.
Im Normalfall werden Sollsalden positiv und
Habensalden negativ dargestellt. Bei der Betrachtung von GuV-Konten müsste man
also das Ergebnis der Kennzahlengruppe mit -1,00 multiplizieren um Erträge
positiv und Aufwendungen negativ darzustellen. Um bereits das Ergebnis in der
gewünschten Form zu erhalten kann man von vornherein einen Faktor -1,00 angeben,
der für die einzelnen Salden das Vorzeichen automatisch dreht.
Will man auf die Planzahlen dieser Definition
zugreifen, so muss man keine neue Liste definieren. Man stellt dem Kürzel
einfach PLAN_ vorweg  - also PLAN_AKZ für die Plandaten. Siehe auch
Kostenstellendefinition
bzw.
Kostenträgerdefinition
.

---

## Kontoblattdruck

Kontoblattdruck
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Direktsprung
[KOD]
Hier können die Kontoblätter für Sach- und
Personenkonten ausgedruckt werden. In der Handhabung wird zwischen der
technischen Erstellung und dem Druck unterschieden.
Der Vorgang beginnt mit
"Kontoblatt
erstellen"
Nach erfolgreichem Abschluss wird im Anzeigebereich
des Auswahlbildschirms angezeigt, dass dieser Job ausgeführt wurde.
Die
erstellten Kontoblätter können jetzt weiterbearbeitet werden, indem sie
insgesamt (Kontoblätter drucken) oder teilweise (Kontoblätter Einzelkonten)
gedruckt werden.
Achtung:
Ein Beleg kann nur in einem Kontoblatt stehen. Bei
der Kontoblatterstellung wird im Beleg die Nummer des Kontoblattes
gespeichert.

---

## Kontoauszug drucken

Kontoauszug drucken
Hauptmenü
OP-Verwaltung
Information und Abstimmung
Kontoauszug
Direktsprung
[KOAZ]
Der Kontoauszug liefert den aktuellen Stand der noch
offenen Posten. Ihm liegt ein Formular vom Typ Mahnung zugrunde. Es werden auch
Konten mit Saldo 0 gedruckt, solange noch offene Posten existieren.

---

## Kontoblätter anzeigen

Kontoblätter anzeigen
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Funktion
Kontoblätter anzeigen
SF6
Direktsprung
[KOD]
Wählt man diese Funktion aus, erschein eine weitere
Auswahlliste, die alle Konten, die zu dem Kontenblattlauf mit Anfangssaldo,
Summe der Bewegungen und Endsaldo anzeigt. Hier stehen dann weitere Funktionen
zur Verfügung.
Kontoblätter drucken
Es werden nur die ausgewählten Konten gedruckt.
Löschen
Hier können einzelne Konten aus einem Kontoblattlauf
herausgelöscht werden. Jedoch nur, wenn dieses Konto nicht bereits in einem
Kontoblattlauf einer späteren Periode enthalten ist. Dies würde auf dem
Bildschirm angezeigt werden.
Beleganzeige
Es wird eine weitere Auswahlliste mit sämtlichen
Belegen des Kontos, die in diesem Kontoblatt zusammengefasst wurden,
geöffnet.

---

## Kontoblätter drucken

Kontoblätter drucken
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Funktion
Kontoblätter
drucken
Direktsprung
[KOD]
oder
[KOK]
Für den Druck des Kontoblattes stehen verschiedene
Möglichkeiten zur Verfügung, die sich letztlich nur durch die Möglichkeit der
Eingrenzung unterscheiden:
Kontoblätter drucken:
Man kann hier die Konten eingrenzen, die zu diesem
Kontoblatt gehören.
Kontoblätter Einzelkonten:
Im Gegensatz zum Druck über "Kontenblätter drucken"
werden hier zu einem Konto aus allen Kontoblattläufen die Daten herausgesucht.
Eine zusätzliche Eingrenzungsmöglichkeit ist hier die Seite des
Kontoblattes.
Diese beiden Möglichkeiten basieren auf dem
Formulardruck. Für den Kokore und den Konto- / Infoblattdruck existieren
Formularvorlagen. Man kann sich jedoch die
Kontoblätter
selber im
Formulareinrichter gestalten.
Neben dem Formulardruck existiert auch ein fest
vorgegebener Crystal Report. Diesen Findet man im Menü unter
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblattdruck
Direktsprung
[KODD]
Hierbei handelt es sich um einen vordefinierten
Crystal-Report, der auf Basis der erstellten Kontoblätter die Informationen zu
den Buchungen ausgibt. Man kann hier nach der Laufnummer (KontoBlDruckId) – dann
werden nur die Daten dieses Kontoblatts ausgedruckt - oder nach der Jahrnummer
eingrenzen – hier werden dann alle Kontoblätter, die in dem ausgewählten Jahr
aufgelaufen sind, gedruckt. Wird eine Laufnummer (KontoBlDruckId) angegeben, so
wird die eingegebene Jahrnummer ignoriert.
Dieser Report kann auch direkt aus den Auswahllisten
„Kontoblätter bearbeiten“ oder „KoKoRe bearbeiten“ über die Funktion
Kontoblattdruck
SF8
aufgerufen werden.

---

## Kontoblätter zurücksetzen

Kontoblätter zurücksetzen
Hauptmenü
Abschlussarbeiten
Kontoblätter
Kontoblätter bearbeiten
Funktion
Kontoblätter zurücksetzen
F7
Direktsprung
[KOD]
Bei Anwahl dieses Punktes erscheint folgender
Bildschirm:
Hier ist ganz wichtig zu beachten, dass nicht das
ausgewählte, sondern immer das zuletzt erstellte Kontoblatt gelöscht wird.

---

## Konto Druckpositionen

Konto Druckpositionen
Hauptmenü
Finanzbuchhaltung
Stammdaten
Konto-Druckpositionen
Direktsprung
[FIDRU]
Die Druckposition ist ein Hilfsmittel zur Gliederung
des Kontoplans beim Ausdruck der Bilanz, der GuV, der Saldenlisten, usw.
Sachkonten, die mit der gleichen Druckposition versehen werden, werden im
Ausdruck unabhängig von der Kontonummer zusammenhängend mit einer voranstehenden
Überschrift und einer anhängenden Summenzeile ausgedruckt. Vor der Anlage von
Sachkonten sollten deshalb die Druckpositionen festgelegt werden.
In dem Erfassungsbildschirm können die nachfolgenden
Felder bearbeitet werden.
Feld
Beschreibung
Nummer
Identifikation der Druckposition.
      Diese wird im Sachkontenstamm bzw. bei den Obersachkonten abgefragt. Sie
      dient gleichzeitig als Sortierungskriterium auf den Listen.
Gruppe
Dieses Feld kann dazu dienen, die
      Druckpositionsbereiche zu gliedern. Hinter der Gruppe steht das
      Anwenderformat AF_SAKOPOGRU. Es kann direkt über
F3
und dort
F8
(Stammdatenpflege) erweitert werden. Es wird von Referenz-ERP nicht
      für Auswertungen  herangezogen.
Bezeichnung
Bezeichnung der Druckposition für
      Auswahllisten etc.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Überschrift
Text
      für den Druck einer Überschrift in Standardsprache.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Summenzeile
Beschreibung Text für die
      Beschriftung einer Summenzeile in Standardsprache.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Ober-Position
Die
      Ergebnisse einer Summenzeile können in eine übergeordnete Position, die
"Oberpositio
[...]


---

## Kopieren

Kopieren
Ein ausgewählter Vorgang kann hiermit unter
Beibehaltung der Vorgangsklasse kopiert werden, dabei bleibt der Quellvorgang
unverändert erhalten. Der Zielvorgang kann einen anderen Kunden betreffen und
anderen Buchungsperioden zugeordnet werden.
Ein SPA im Bereich „Vorgangsbearbeitung allgemein“
sichert auf Wunsch ab, dass Vorgänge mit Partien, Kontrakten und Strecken nicht
kopiert werden können.

---

## Kostenstellendefinition

Kostenstellendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Kostenstellendefinition
Direktsprung
[CCD]
Hier legt man eine Liste von Kostenstellen an, auf die
man bei der Berechnung später zugreifen will. In einer Kostenstellendefinition
kann eine Kostenstelle nur einmal erscheinen. Doppelt angegebene Kostenstellen
werden nur einmal gespeichert.
Im Normalfall werden Sollsalden positiv und
Habensalden negativ dargestellt. Man müsste man also das Ergebnis der
Kennzahlengruppe mit -1,00 multiplizieren um Erträge positiv und Aufwendungen
negativ darzustellen. Um bereits das Ergebnis in der gewünschten Form zu
erhalten kann man von vornherein einen Faktor -1,00 angeben, der für die
einzelnen Salden das Vorzeichen automatisch dreht.
Will man auf die Planzahlen dieser Definition
zugreifen, so muss man keine neue Liste definieren. Man stellt dem Kürzel
einfach PLAN_ vorweg  - also PLAN_AKZ für die Plandaten. Siehe auch
Kontendefinition
oder
Kostenträgerdefinition
.

---

## Kostenstelleninformation

Kostenstelleninformation
Hauptmenü
Kostenrechnung
Kostenstellen
Kostenstelleninformation
Direktsprung
[KSI]
Für eine Kostenstelle und ein Buchungsjahr werden die
Periodensalden ausgegeben. Ein Klick auf eine Zeile liefert in einem weiteren
Bildschirm die einzelnen Belege, die zu diesen Summen führen. Für die
Darstellung dieser Informationen existieren drei Varianten:
•
Kostenstelleninformation
In dieser Variante werden
die Belege, aus denen sich die Summen Bilden so angezeigt, wie sie sind. Bei
Verteilkostenstellen kann die  Summe über alle Belege also nicht mit der
über aus der Periode übereinstimmen.
•
Alle Perioden
Wie die Variante
Kostenstelleninformation, nur das nicht nur die Belege aus der ausgewählten
Periode sondern alle Belege des ausgewählten Jahres angezeigt
werden.
•
Verteilinformation
Hier werden die Beträge so
angezeigt, wie sie auch gebucht wurden. Die Summe über die Betragsspalte ergibt
also den Periodensaldo. Zusätzlich existiert eine Spalte
Prozent
, die
angibt, wie viel Prozent vom erfassten Betrag der Kostenstelle zugeordnet
wurde.
Ein Klick auf einen der hier aufgeführten Belege
verzweigt weiter in die
Einzelbeleganzeige
.

---

## Kostenträgerdefinition

Kostenträgerdefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Kostenträgerdefinition
Direktsprung
[CCD]
Hier legt man eine Liste von Kostenträger an, auf die
man bei der Berechnung später zugreifen will. In einer Kostenträgerdefinition
kann ein Kostenträger nur einmal erscheinen. Doppelt angegebene Kostenträger
werden nur einmal gespeichert.
Im Normalfall werden Sollsalden positiv und
Habensalden negativ dargestellt. Man müsste man also das Ergebnis der
Kennzahlengruppe mit -1,00 multiplizieren um Erträge positiv und Aufwendungen
negativ darzustellen. Um bereits das Ergebnis in der gewünschten Form zu
erhalten kann man von vornherein einen Faktor -1,00 angeben, der für die
einzelnen Salden das Vorzeichen automatisch dreht.
Will man auf die Planzahlen dieser Definition
zugreifen, so muss man keine neue Liste definieren. Man stellt dem Kürzel
einfach PLAN_ vorweg  - also PLAN_AKZ für die Plandaten. Siehe auch
Kontendefinition
oder
Kostenstellendefinition
.

---

## Kostenträgerinformation

Kostenträgerinformation
Hauptmenü
Kostenrechnung
Kostenträger
Kostenträgerinformation
Direktsprung
[KSTRI]
Für einen Kostenträger und ein Buchungsjahr werden die
Monatssalden ausgegeben. Ein Doppelklick auf eine (Monats-) Zeile löst die Summe
auf die darunter liegenden Bewegungen auf. Ein Doppelklick hierauf zeigt den
Buchungssatz an mit der Möglichkeit, den zugrunde liegenden Beleg aus dem Archiv
zu lesen.

---

## Lagerumbuchung

Lagerumbuchung
Lagerumbuchungen werden unter dem Direktsprung [LGU]
verwaltet. Sie werden als Vorgänge gespeichert. Referenz-ERP stellt folgende
Bearbeitungsfunktionen zur Verfügung:
•
Erfassen F
8
Erfassung einer neuen Lagerumbuchung
•
Erstdruck
F9
Erstdruck einer Lagerumbuchung.
•
Formulardruck
F10
Wiederholungsdruck
•
Korrektur
F5
Korrektur einer Lagerumbuchung
•
Vorschau
F11
Druckvorschau
•
Stornieren
F7
Stornieren (Löschen) der Lagerumbuchung
•
Freigabe/Sperren
Freigabe / Sperren für weitere Bearbeitung
•
FiBu
Übertrag
Übergabe an die Finanzbuchhaltung
Lagerumbuchungen können in drei verschiedenen
Buchungstypen erfasst werden.
Stufe
Kurz
Lang
Buchungstyp
Angebot
AG
ohne
      Best.Buchung
Die
      Umbuchung ist Bestandsunwirksam
Auftrag
AU
disp.Best.Buchung
Die
      Umbuchung ist dispositiv.
Rechnung
RE
norm.Best.Buchung
Die
      Umbuchung ist Bestandswirksam.
Der Buchungstyp kann im Vorgangskopf als UFLD (Feld 4501)
oder in der Umbuchungsposition gepflegt werden.
Im Kopfteil:
Oder im Positionsteil:
Siehe auch Erfassung des
Positionsteils bei Umbuchungen
Hinweise:
Durch die Option "maxBuchuntstypUmbuchung - Maximaler
Buchungstyp bei Umbuchung" kann für den Bediener eingeschränkt werden, welchen
maximalen Buchungstyp der Bediener verwenden darf.
Der Erfassungsparameter 'Beim Verlassen
Zugangs-/Abgangs-Menge und -Betrag verproben' mit der Standardeinstellung 'Ja'
der Lagerumbuchungsmaske bewirkt bei dieser Einstellung eine
Übereinstimmungsprüfung der Beträge und Mengen von Zugang und Abgang bei
Verlassen der Umbuchungsmaske. Bei Abweichungen wird eine Warnmeldung erzeugt.
Ist die Abweichung ungewollt, so muss die Position zur Korrektur aufgerufen
werden.

---

## Leergutverwaltung

Leergutverwaltung
Hauptmenü
Nebenbuchhaltungen
Leergut
Leergutverwaltung
Oder Direktsprung [leer]
Bei der Leergutverwaltung werden u.a. folgende
Anforderungen gestellt:
•
Mit dem Hauptartikel soll Leergut automatisch oder manuell fakturiert
werden
•
Ggf. existieren verschiedene zuordnungsbare Leergutarten
•
Das Konto des Kunden soll auf dem Vorgangsbeleg angedruckt werden
•
Ein Leergutinformationssystem soll entstehen
Zur Realisation dieser Anforderungen sind folgende
Bereiche einzurichten:
•
Alle Artikel, die Leergut auslösen sollen, werden mit einer
Folgeartikelliste, wie oben beschrieben, versehen
•
Die Artikel dieser Liste sind in der Artikelklasse (im Artikelstamm unter
Artikelgruppen) als Leergut gekennzeichnet
•
Das Vorgangsformular ist entsprechend eingerichtet
Zugehöriger
Steuerparameter 487
.
In der Leergutverwaltung gibt es folgende 3
Varianten:
Variante Leergutkonto – zeigt alle Leergutkonten
an.
Variante Leergutbewegungen – zeigt alle Bewegungen mit
Leergut an.
Variante Leergut Artikelstamm - zeigt alle Artikel mit
der Artikelklasse „Leergut“ an.
Folgende Funktionen gibt es in den Optionboxen dieser
Varianten:
WBU-Details f. Artikel – zeigt die
Warenbewegungsauswertung für den Artikel des aktuell ausgewählten Datensatzes
an.
Artikel-Bestand – zeigt den Artikelbestand für den
Artikel des aktuell ausgewählten Datensatzes an.

---

## Lexware Lohn & Gehalt Plus

Lexware Lohn & Gehalt Plus
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Funktion
F9
Import Starten
Funktion
F4
Importdatei lesen
Direktsprung
[FIIM]
Bei dieser Schnittstelle handelt es sich um den Import
der Lohndaten aus der Software "Lexware Lohn und Gehalt Plus". Es handelt sich
hierbei um reine Sachkontenbuchungen. Den Export der Buchungsdaten findet man in
dieser Software im Menü unter:
Datei -> Exportieren -> ASCII ->
Buchungsliste
Dort kann man noch einige Optionen einstellen. Da die
in Referenz-ERP vorgegebene Schnittstelle davon ausgeht, dass die Kostenstellen mit
importiert werden sollen, so muss bei Buchungsliste "Aufgeteilt nach
Kostenstellen" eingetragen sein.
Beim Einspielen der Daten wird die Periode anhand des
Belegdatums bestimmt.
Sind für das Gegenkonto in den Stammdaten die
Steuerklasse und der Steuerschlüssel hinterlegt und bei „Sperre Steuerschlüssel“
der Wert „Fest“ hinterlegt, so werden diese Werte für diesen Buchungssatz
herangezogen und die Steuer wird errechnet. Dabei hängt es von der Steuerklasse
ab, ob der Betrag in der Exportdatei als Nettobetrag (bei Steuerklasse 1 oder
101) oder als Bruttobetrag (bei Steuerklasse 2 oder 102) interpretiert wird.
Beispiel:
Für das Konto 1755 ist die Steuerklasse 2
hinterlegt.  In der Importdatei steht der Betrag 14,06 €. Es wird folgender
Buchungssatz gebildet:
4100
An
1755
14,06
12,12
1775
1.94
Satzaufbau
In der Ersten Zeile der zu importierenden Datei stehen
die Feldbezeichnungen getrennt durch ein Semikolon. Abgeschlossen ist die Zeile
mit CR/LF:
Belegdatum;Belegnummer;Buchungstext;Buchungsbetrag;Währung;Sollkonto;Habenkonto;Kostenstelle
1
Diese Zeile wird ignoriert. Danach kommen die Daten
getrennt durch Semikolon:
31.01.2003;LG03030001;Lohn;2.208,00;EUR;4110;1755;
31.01.2003;LG03030002;Gehalt;16.600,00;EUR;4120;1755;
31.01.2003;LG03030003;Auszubildendenvergütung;285,00;EUR;4120;1755;

---

## LKW Fahrer Stammdaten

LKW Fahrer Stammdaten
Hauptmenü
Nebenbuchhaltungen
LKW-Verwaltung
Fahrer Stammdaten
Direktsprung
[LKWF]
Felder
Fahrer
Fahrernummer. Wird vorbelegt mit der
      nächstmöglichen Nummer (letzte Nummer + 1)
Matchcode
Matchcode
Bezeichnung
Bezeichnung / Name des
      Fahrers

---

## LKW Gruppen

LKW Gruppen
Hauptmenü
Nebenbuchhaltungen
LKW-Verwaltung
LKW Gruppen
Direktsprung
[LKWG]
Felder
Nummer
Wird
      vorbelegt mit der nächstmöglichen Nummer (letzte Nummer + 1)
Bezeichnung
Matchcode

---

## LKW Verwaltung

LKW Verwaltung
Hauptmenü
Nebenbuchhaltungen
LKW-Verwaltung
LKW Verwaltung
Direktsprung
[LKW]
Kopfdaten und Registerkarte
      „Allgemein“
Nummer
Wird
      vorbelegt mit der nächstmöglichen Nummer (letzte Nummer + 1)
Bezeichnung
Matchcode
LKW
      Klasse
Wird
      vorbelegt mit „egal“
F3-Auswahl aus dem Format
      LKW_Klasse:
Egal
LKW
      ohne Anhänger
PKW
      ohne Anhänger
LKW
      mit Anhänger
PKW
      mit Anhänger
LKW-Anhänger
PKW-Anhänger
Alle
      PKW
Alle
      LKW
LKW
      Gruppe
Vorbelegung mit 0-ohne
      Gruppe
LKW-Gruppen
können angelegt werden unter [LKWG].
Spedition
Wird
      vorbelegt mit 0 – kein Spediteur
F3-
      Auswahl über die unter
[SPED]
angelegten
Speditionen
.
Leergewicht in kg
Vorbelegung mit 0
Nutzlast in kg
Vorbelegung mit 0
Volumen in m3
Vorbelegung mit 0
Anmeldung
Wird
      vorbelegt mit dem heutigen Datum
Abmeldung
Wird
      vorbelegt mit 31.12.2099

---

## LVS

LVS
In Abhängigkeit von Unterklassen wird im
Vorgangsimport der Vorgangsklasse 5150 (LVS) eine Buchung im LVS vorgenommen.
Der Vorgangsimport von LVS-Einträgen erfolgte früher
über ein Vorgangsimportmakro für LVS. Dieses wird nicht mehr gepflegt.
Es muss für die Verarbeitung im ImportVorgstamm das
Feld „useCS“ auf „1“ gesetzt sein.
Unterklasse
Bedeutung
Bemerkungen
Pflichtfelder
10
Ladeträgerlokalität
Hier
      wird ein Ladeträger erstellt, oder wenn er bereits vorhanden ist, wird
      seine Lokalität verändert.
LadetraegerNr o.ext.Nr.
      LokalitaetsNr
Bediener
20
Beladung
Hier
      wird ein Ladeträger mit der gegebenen Ware beladen.
LadetraegerNr o.ext.Nr.
LokalitaetsNr
Menge
Mengeneinheit
Bediener
21
Beladen mit Inventur
Hier
      wird ein Ladeträger mit der gegebenen Ware beladen.
Eintrag ins Bewegungsprotokoll als
      geplante Inventur
Diese Art der Beladung erfolgt an
      Maschinen oder geeichten Waagen.
LadetraegerNr o.ext.Nr.
LokalitaetsNr
Menge
Mengeneinheit
Bediener
30
Umpacken
Hier
      wird von einem Ladeträger auf einen anderen umgepackt. Es müssen also zwei
      korrespondierende Sätze in der Tabelle ImportVorgPositionLVS vorhanden
      sein. Die jeweils erste Zeile ist die Abgangs-, die zweite die
      Zugangszeile.
Bediener
Artikelid
Quell-Ladetraegernummer bzw.
      ext.Nr
Ziel-Ladetraegernummer bzw.
      ext.Nr
Quell-Ladeeinheitsnummer
Quell-Ladeeinheitsposition
Menge
Mengeneinheit
40
Umbuchung
Hier
      wird eine Artikelumbuchung vorgenommen. Dazu sind zwei korrespondierende
      Zeilen notwendig. Die Abgangszeile wird mit TypZuAbgang = 1, die
      Zugangszeile mit TypZuAbgang=2 gekennzeichnet.
Der
      Ladeträger bleibt erhalten.
Bediener
Quell- und
      Ziel-ArtikelId
Quell-Ladeeinheitsnummer
Quell-Ladeeinheitsposition
Menge
Mengeneinheit
50
Fahrauftrag
Hier
      wird ein Fahrauftrag für einen Ladeträger generiert
Bediener
LadetraegerNr o. ext.Nr
LokalitaetsNr
(Optional) ListenNr
60
Geplante Inventur
M
[...]


---

## Mahntexte

Mahntexte
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Funktion Mahntexte
F8
Direktsprung
[FIMSG]
.
Für Mahnungen können Texte hinterlegt werden, die beim
Druck verwendet werden. Diese Texte werden nach Mahngruppe, Mahnstufe und
Sprache – diese bezieht sich auf die im Kundenstamm hinterlegte Sprache -
getrennt erfasst.
Zu jeder dieser Kombinationen können mehrere Texte,
die durch Angabe einer Nummer voneinander unterschieden werden, mit der Funktion
Texterfassung
F5
erfasst werden. Diese Texte werden dann
später im
Formulardruck
verwendet und in
Reihenfolge der Nummer ausgegeben.
Innerhalb des Textes ist es möglich, die Werte der vor
dem Druck abgefragten Datumsangaben mit in den Mahntext einzubauen. Dabei ist zu
beachten, dass folgende Variablen mit Doppelpunkt vor dem Wort in den Text
eingebaut werden:
Zahldatum$
und
Zahlfristdatum$
Achtung
:
Groß- und Kleinschreibung
beachten!!!
Beispiel
:
Bitte zahlen Sie bis zum :Zahlfristdatum$ den
angegebenen Betrag.

---

## Mahnungen bearbeiten

Mahnungen bearbeiten
Hauptmenü
Mahn-, Zahl-, Zinswesen
Mahnwesen
Mahnungen bearbeiten
Direktsprung
[MHB]
.
Die eigentliche Aufgabe besteht darin, die Mahnungen
zu drucken. Auch auf dieser Ebene gibt es weitere Bearbeitungsfunktionen:
Mahnliste Druck
Die Mahnliste wird als Protokoll gedruckt
Bei den Varianten (Mahnungen bearbeiten, Mahnungen
gedruckt, Mahnungen ungebucht, Mahnungen ungedruckt) stehen zusätzlich die
folgenden Funktionen zur Verfügung
Ansehen
F6
Eine Auswahlliste mit den Daten der markierten
Mahnungen wird auf dem Bildschirm angezeigt. Eine weitere
Bearbeitungsmöglichkeit besteht hier nicht mehr.
Formularänderung
F5
Unter Formularänderung können noch verschiedene
Parameter geändert werden. Dazu gehören das Formular, mit dem diese Mahnung
gedruckt werden soll, die Mahngruppe und Stufe, der die Mahnung zugeordnet ist
sowie die Mahngebühr. Zinsen lassen sich hier nicht mehr ändern. Dies ist nur
unter Mahnvorschläge bearbeiten möglich.
Drucken
F9
Die Mahnschreiben werden ausgedruckt. Welches Formular
herangezogen wird, wurde zuvor in den Mahn-Stammdaten festgelegt
(Mahnstamm).
Nach Eingabe von Zahlungsdatum und Zahlungsfrist, die
lediglich als Hinweistext für das Mahnschreiben gedacht sind, und nach
Festlegung der Sortierung beginnt der Ausdruck. Im Mahnschreiben besteht auch
die Möglichkeit, auf das letzte Zahlungsdatum des Kunden hinzuweisen. Unter
Einrichtungsparameter (
Shift F2
)
lässt sich zusätzlich einstellen, wie die Darstellung des Sollhabenkennzeichens
sein soll und ob die Restposten aufgelöst dargestellt werden sollen.
ACHTUNG:
Sobald die Mahnung gedruckt wird,
werden die Mahnstufen in den Belegen hochgesetzt und es wird das Datum der
letzten Mahnung vermerkt.
Eine Mahnung wird nicht gedruckt, wenn der fällige zu
mahnende Saldo, der fällige Saldo oder der gesamt auf dem Mahnschreiben
ausgegebene Saldo im Haben steht.
Die hier hinterlegten Mahnungen können nicht als
Archiv betrachtet werden, da bezahlte Rechnungen nicht meh
[...]


---

## Mahnungen über Mahnformulare drucken

Mahnungen über Mahnformulare
drucken
Das Formular ist, wenn nicht anders eingerichtet 2200.
Es existieren zu diesem Typ folgende Formularbereiche:
•
301
Mahnkopf

Formularkopf
•
302
Mahntexte
Zeilentyp
•
303
Mahnabschluss
Abschluss
•
304
Mahnposition

Zeilentyp
•
305
Mahnfolgekopf
Folgekopf
•
306
Mahnfuß
Fuß
•
307
Mahnsummenzeile         Zeilentyp
•
308
Mahnsummenkopf        Zeilentyp
•
309
Mahnsummenfuß
Zeilentyp
•
310
Mahnung Betreffzeile    Mail Betreff
Folgende Variablen sind in allen Teilen (Kopf, Fuß und
Zeilentyp) verfügbar. Formularbereiche, die nicht separat mit aufgeführt werden,
enthalten nur Festtext oder diese Felder!
Bezeichnung
Typ
Nr
Beschreibung
AdressId
Block
6
Hauptanschrift wie im Kundenstamm
      hinterlegt
AdressAnrede
Normal
3
Anrede wie im Anschriftenstamm
      hinterlegt
AdressName
Normal
3
Name
      wie im Anschriftenstamm hinterlegt
AdressKurzName
Normal
3
Kurzname wie im Anschriftenstamm
      hinterlegt
AdressBezeich
Normal
3
Bezeichnung wie im Anschriftenstamm
      hinterlegt
AdressTelefon
Normal
3
Telefon wie im Anschriftenstamm
      hinterlegt
AdressTelefax
Normal
3
Telefax wie im Anschriftenstamm
      hinterlegt
KundenNummer
Numerisch
4
Nummer des Kunden wie im Kundenstamm
      hinterlegt
KundNummer
S.o.
GegenNummer
Numerisch
4
Gegennummer wie im Kundenstamm
      hinterlegt
KundGegenNummer
S.o.
FilialNummer
Numerisch
4
VerkGebNummer
Numerisch
4
Verkaufsgebiet wie im Kundenstamm
      hinterlegt
VertGrNummer
Numerisch
4
Vertretergruppe wie im Kundenstamm
      hinterlegt
VertGrBezeich
Normal
3
Vertretergruppenbezeichnung wie in
      Stammdaten Vertretergruppe hinterlegt
LetzteZahlung
Normal
5
Belegdatum der letzten eingegangenen
      Zahlung
Datum
Normal
5
Datum der M
[...]


---

## Mahnungen Mailversand

Mahnungen Mailversand
Mahnungen können so eingerichtet werden, dass
zusätzlich zum Druck oder an Stelle des Drucks per Mail versendet werden können.
Dazu müssen folgen Voraussetzungen gegeben sein:
1)
Der Belegversand-Lizenz muss aktiv sein.
2)
Ein
Versandprofil
muss eingerichtet
sein.
3)
In den Stammdaten des
Mahnstamm
müssen zusätzliche Felder
gepflegt werden.
•
Ein abweichendes Formular für den Mailversand. Dieses Formular kann z.B.
zusätzliche Grafiken enthalten, die bei der Druckversion nicht enthalten sind.
In der F3-Auswahl werden nur Formulare angeboten, bei denen die Archivierung
aktiviert ist. Wird hier kein Formular hinterlegt, dann wird das beim Druck
angegebene verwendet.
•
Zur Steuerung des Mailbodys für die eigentliche Mail kann entweder ein
HTML-Formular oder eine
Datenbankfunktion
, die den
HTML-Aufbau übernimmt, verwendet werden. In dem Formular müssen HTML-Tags für
die Formatierung verwendet werden. Hier existiert ein Formular mit der Nummer
-1120, das so wie es ist verwendet werden kann oder als Vorlage benutzt werden
kann. In diesem Formular stehen alle Felder und Bereiche der Standard Mahnung
zur Verfügung. Zusätzlich existiert auch ein Bereich „Mahnung Betreffzeile“, in
dem man die Betreff-Zeile der Mail einrichten kann. Ist kein Formular
eingerichtet, erscheint als Betreff und als Mailinhalt lediglich der Text
„Mahnung“.
HINWEIS:
Um Grafiken in das Formular mit
einzubinden, kann man den bekannten HTML-Syntax <img src="cid:XXXXXX"
alt="mein bild" /> verwenden. Für XXXXXX muss die GUID aus dem
Formulararchiv, in dem die Grafik hinterlegt sein muss, angegeben
werden.
•
Ist das Versandprofil nicht eingerichtet, wird für alle Personenkonten
mit diesem Mahnsatz kein Mailversand durchgeführt.
4)
In den Hauptanschriften oder den Ansprechpartnern muss eine Mailadresse für
Mahnungen eingerichtet sein. Dazu wählt man in der Auswahlliste „Anschriften“
[ANSCH]
in der Variante
„Ansprechpartner“ die Anschrift des Kunden,
[...]


---

## Merkmale

Merkmale
Gebindeinfo erweitern (CF8)
Nach Beendigung einer Gebindeerfassung können über
diese Funktion zum Artikel weitere Teilmengen nacherfasst werden. Der Artikel
muss hierzu natürlich in Bearbeitung sein.
FiBu – Information (F4)
Anzeige und ggf. Korrekturmöglichkeit der
FiBu-Parameter des Artikels.
Einzel / Gesamtpreiseingabe (F8)
Im Normalfall errechnet sich der Gesamtpreis aus Menge
und Einzelpreis. Diese Funktion erlaubt es, zwischen Einzel- und Gesamtpreis zu
wechseln. Aus dem Gesamtpreis errechnet sich dann der Einzelpreis. Die Menge
darf danach nicht korrigiert werden!
Wertartikel an/aus
Die Funktion schaltet das Merkmal Wertartikel für den
erfassten Artikel ein bzw. aus.
Kommission an/aus
Die Funktion schaltet das Merkmal einer Kommission für
den erfassten Artikel ein bzw. aus.
Kommission Verkauf an/aus
Die Funktion schaltet das Merkmal des Verkaufs von
Kommissionsware für den erfassten Artikel ein bzw. aus.
Vorverkauf an/aus
Die Funktion schaltet das Merkmal des Vorverkaufs für
den erfassten Artikel ein bzw. aus.
Vorverkauf Abholung an/aus
Die Funktion schaltet das Merkmal des Abholung
vorverkaufter Ware für den erfassten Artikel ein bzw. aus.
Nullpreis Okay an/aus
Diese Funktion kann man anwählen, um zu kennzeichnen,
dass der angegebene Preis 0 wirklich 0 sein soll. Es wird ein Signalfeld „
Nullpreis OK
“
sichtbar geschaltet, das für den Anwender ein Hinweis darauf ist, dass die 0 im
Feld Preis bewusst eingetragen wurde und nicht etwa vergessen wurde den Preis
anzugeben.
Durch erneutes Anwählen dieser Funktion wird dieses
Signalfeld wieder entfernt.
Vorläufiger Preis
an/aus
Diese Funktion kann man anwählen, um zu kennzeichnen,
dass der angegebene Preis nicht der endgültige Preis sein soll. Es wird ein
Signalfeld „
Nicht Endpreis
“
sichtbar geschaltet, das für den Anwender ein Hinweis darauf ist, dass im Feld
Preis ein vorläufiger Preis steht und noch etwas zu tun ist.
Durch erneutes Anwählen dieser Funktion wird dieses
Signalfeld w
[...]


---

## Mögliche Zahlungsvorgänge

Mögliche Zahlungsvorgänge
Es existieren folgende Finanzvorgänge (hier zieht der
Steuerparameter Aut. Buchungen von Finanzvorgängen):
a)
Einzahlung,
d.h.
es wird eingegeben, wie viel von welcher Zahlungsart in die Kasse gegeben wird;
außerdem wird ein Eintrag in den Datenstrom (und über MS dann in die FiBu)
erzeugt. In der vorgeschalteten Maske wird die Art der Einzahlung abgefragt:
entweder sie kommt von einer Bank (Haben: Verrechnungskonto der zugehörigen
Hausbank, Soll: Kassenkonto) oder von einem Kunden (Haben: Kundenkonto, Soll:
Kassenkonto).
b)
Auszahlung an Kunden,
d.h. es
wird eingegeben, wie viel von welcher Zahlungsart aus der Kasse genommen wird.
Dabei muss sich das bargeldlose Zahlungsmittel auch in der Kasse befinden
(Identifikation z.B. über Gutscheinnummer o.ä.). Ebenso muss auch genug Bargeld
vorhanden sein, außerdem wird ein Eintrag in den Datenstrom (und über MS dann in
die FiBu) erzeugt, wobei vorher der Kunde ausgewählt werden muss, an den
ausgezahlt werden soll (Haben: Kassenkonto, Soll: Kundenkonto).
c)
Entnahme mit Zuordnung
Kostenkonto
gemäß FIBU-Eintrag in
AcashStmdKsse. Dabei ist das mit Werten aus AcashStmdKsse vorbelegte
Verrechnungskonto auf diesem Fenster änderbar. (Haben: Kassenkonto, Soll:
gewähltes Verrechnungskonto).
Hier existieren auf der Zahlungsmaske zwei
Einrichterparameter, die dafür sorgen, ob es eine Vorbelegung des Steuersatzes
gemäß Sachkontenstamm geben soll.
(siehe auch EPA)
d)
Zahlungsmeldung für
Kreditrechnungen
Diese funktioniert
ähnlich wie eine Einzahlung jedoch mit passender Bedienerführung (Eingabe eines
Verweises auf die zu begleichende Rechnung und Eingabe des Rechnungsbetrages);
hier muss die Kundennummer auf der Finanzvorgangsauswahlmaske angegeben werden.
Angezeigt werden dann Beleg aus der Warenwirtschaft, die noch nicht teilgezahlt
wurden. Hinterher sollte dann eine Bearbeitung durch eine autorisierte Person in
der Offenen-Posten-Verwaltung stattfinden. (Haben: Kundenkonto, Soll:
K
[...]


---

## Monatsabschluss FIBU

Monatsabschluss FIBU
Die Finanzbuchhaltung ist so flexibel gehalten, dass
man auch ohne Monatsabschluss weiter arbeiten kann und sich ggf. nur auf den
Jahresabschluss konzentrieren muss. Je nach betrieblicher Organisation lassen
sich jedoch die bekannten Abschlussarbeiten durchführen. Siehe dazu:
Buchungen
Fibu - Testprogramm
Kontenblattdruck / KoKoRe
Umsatzsteuervoranmeldung
Auswertungen:
Summen und Saldenliste
GuV
Bilanz
BWA
OP-Listen

---

## Notwendigkeit

Notwendigkeit
Die Kassenabstimmung ist einerseits eine
buchhalterische Anforderung zur Überprüfung der Stimmigkeit von Kasse und Fibu.
Zum anderen ist sie eine technisch bedingte
Notwendigkeit. Durch Abstürze, Programmabbrüche, Programmfehler, Hardwarefehler,
Stromausfälle, Bedienerfehler (schaltet einfach Rechner ab), Timeouts (Server
beendet die Verbindung zu einem Kassenarbeitsplatz) und andere Ursachen können
Unstimmigkeiten in Daten entstanden sein. Unstimmigkeiten können dadurch
entstehen
•
Zwischen Vorgängen in der Ware (Barverkaufsbelegen) und dem
Kassenbuch
•
Innerhalb der Kasse zwischen Belegen, Zahlungen, Zahlungsmitteln und dem
Kassenbericht
•
Zwischen Kassenbuch und Fibu
Die Abstimmung verfolgt 2 Ziele:
•
Unstimmigkeiten aufzuspüren
•
Sie möglichst automatisch (Reorganisationsprogramm) zu bereinigen. Wenn
dieses nicht möglich ist, so sollen wenigstens Hilfestellungen zur Diagnose des
Fehlers und zu seiner manuellen Beseitigung gegeben werden.
Hinweis
Die Kassenabstimmung als technisch bedingte
Notwendigkeit sollte immer einem versierten und geschulten Mitarbeiter der
SoftwareCompany Branchen-ERP überlassen werden.

---

## Oberkonten

Oberkonten
Hauptmenü
Finanzbuchhaltung
Stammdaten
Oberkonten
Direktsprung
[OKS]
Bei Oberkonten handelt es sich um Konten, die
ausschließlich aus Informationsgründen angelegt werden. Obwohl sie Bestandteil
des Kontenplans sind, können Oberkonten natürlich nicht direkt bebucht werden;
auf ihnen werden nur Daten zusammengefasst. Mit ihrer Hilfe werden die Stände
der direkt bebuchbaren Sachkonten schrittweise zu aussagekräftigeren
Gesamtgrößen zusammengezogen. So kann man z.B. die Ergebnisse der Konten
"Erlöse Agrar", "Erlöse
Baustoffe", "Erlöse Mineralöl"
zum Oberkonto
"Erlöse Gesamt"
zusammenziehen.
In dem Erfassungsbildschirm können die nachfolgenden
Felder bearbeitet werden:
Beschreibung
Nummer
Identifikation des
      Oberkontos.
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
      festgelegt, können keine Oberkonten erfasst werden. Dieses Verhalten lässt
      sich per Einrichterparameter „
Nummernkreiszuordnung ignorieren
“
      ändern, indem man den Wert auf
Ja
ändert. Es findet dann kein
      Bereichstest statt.
Matchcode
Matchcode für das
      Oberkonto.
Bezeichnung
Bezeichnung des Oberkontos für
      Auswahllisten etc.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Kontotyp
Hier
      wird der Kontentyp festgelegt:
0
=
      Bilanzkonto
1
      = GuV
3
      = Statistik
Hinter dem Kontotyp kann ein
      Oberkonto noch – bei Bilanzkonten – als Aktiv oder Passivkonto oder – bei
[...]


---

## OP Export für Reimport per DBF-Import

OP Export für Reimport per DBF-Import
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Export
Variante OP-Export für Reimport per
DBF-Import
Direktsprung
[FIEX]
Für den Export aus der Referenz-ERP Finanzbuchhaltung
existiert eine Auswahlliste, in der die OPs bzw. die Belege aufgelistet werden.
Bei den von Referenz-ERP angebotenen Verfahren wird beim Export die Relation
FiBuVorgExport mit den ID‘s aller exportierten Belege gefüllt und bei Erfolg das
Feld FiBuV_ExportIdent  mit einer ID gefüllt, die auf die entsprechenden
Daten in FiBuVorgExport verweist. Diese Auswahlliste für „Reimport per DBF
Import“ ist bereits so aufgebaut, dass die Daten in dem Format zur Verfügung
stehen, wie sie beim DBF Import in die Standardimportschnittstelle erwartet
werden. Als Auswahlkriterium wird lediglich das Eröffnungsbilanzkonto abgefragt.
Dies muss ein gültiges Sachkonto sein, bei dem das Kennzeichen Vortragskonto auf
Ja
gesetzt ist. Wählt man hier den Punkt "Export in DBF-Datei" aus, wird
das angegebene Konto überprüft. Ist es nicht korrekt, erscheint die
Fehlermeldung:
Bei korrekter Eingabe des Kontos werden der Pfad und
Dateiname abgefragt. Pfad und Dateiname werden zwischengespeichert und beim
nächsten Aufruf wieder vorgeschlagen.
Achtung:
Der Dateiname wird zusätzlich mit der Nummer versehen,
die im Fibuvorgstamm im Feld FiBuV_ExportIdent hinterlegt wird. Wenn man also
EXPORT.DBF als Dateinamen angibt, wird der Name um die Nummer (z.B. 4377)
erweitert, so dass der Dateiname EXPORT_4377.DBF lautet.
Nach erfolgreichem Export erscheint folgende
Meldung:

---

## OP-Führung in Fremdwährung

OP-Führung in Fremdwährung
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
Offene Posten können für Personenkonten und unter
bestimmten Vorrausetzungen (siehe unten) auch für Sachkonten in Fremdwährung
geführt werden. Dabei gilt grundsätzlich:
Wenn man OP’s in Fremdwährung führt, so muss bei der
Verrechnung der Betrag in Fremdwährung aufgehen. Die ggf. entstehende Differenz
in Buchwährung wird automatisch als Kursdifferenz ausgebucht.
In den Standardvarianten werden die Beträge in
Fremdwährung und die Währung mit angezeigt und Blau eingefärbt, wenn der
Steuerungsparameter „Anzeige Fremdwährung in Auswahllisten“ auf
Ja
steht.
Oberhalb der Liste befinden sich zwei Zeilen, in denen der Betrag in Buchwährung
und in Fremdwährung angezeigt wird.
Wählt man einen OP aus, der in einer anderen als der
Buchwährung erfasst wurde, wird in der zweiten Zeile sofort die Fremdwährung
dargestellt. Dabei werden bei Personenkonten auch in Buchwährung erfasste
Beträge in diese Fremdwährung umgerechnet. Der Kurs wird aus der
Währungskurstabelle gezogen. Bezugsdatum ist das Belegdatum des umzurechnenden
Beleges.
Um Sachkonten in Fremdwährung zu führen, muss das
Kennzeichen „Währung führen“ im Sachkontenstamm auf
Ja
gestellt
werden.
Im Gegensatz zu den Personenkonten können bei
Sachkonten nur OP’s verrechnet werden, die in der gleichen Währung erfasst
wurden, d.h. es findet keine automatische Umrechnung von der Buchwährung in die
Fremdwährung statt.
Auszifferung geht in Fremdwährung auf:
Beim Ausziffern kann es durch Kursdifferenzen dazu
kommen, dass zwar der Betrag in Fremdwährung aufgeht, die Buchwährung jedoch
eine Differenz aufweist:
USD
Kurs
EUR
Rechnung
4.000,00 S
1,2693
3.151,34 S
Zahlung
4.000,00 H
1,3297
3.008,20 H
Differenz
0,00
143,14 S
Diese Differenz wird automatisch auf das im
Währungsstamm eingetragene Kursgewinn- oder Kursverlustkonto gebucht. Es wird
dabei eine Kursdifferenzbuchung - Belegart KD – erstellt. Diese Belege haben d
[...]


---

## OP-Verwaltung

OP-Verwaltung
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
.
Nach Anwahl des Menüpunkts
OP-Verwaltung
wird
zuerst abgefragt, für welche Buchungsperiode die Bearbeitung durchgeführt werden
soll. Danach wird in den OP - Bildschirm gewechselt, der verschiedene
Bearbeitungsmöglichkeiten anbietet. Hierbei handelt es sich um Funktionen zur
Bearbeitung und Verrechnung von OP’s. Zuerst wird die Kontonummer des OP-Kontos
eingegeben. Zu OP-Konten zählen alle Personenkonten und die
Sachkonten
, die in den Stammdaten das
Kennzeichen OP-Konto auf
Ja
stehen haben.
Bei der Eingabe des Kontos kann der Name oder die
Nummer eingegeben werden und es wird dann nach diesem Kennzeichen gesucht. Wenn
Kontonummer oder der Name nicht bekannt oder eindeutig sind, kann über
F3
nach weiteren
Merkmalen gesucht werden
:
•
Alle Konten nach Kontonummer
•
Personenkonten nach Nachname, Vorname
•
Sachkonten
•
Sachkonten nach Bezeichnung
•
Personenkonten nach Belegnummer
•
Personenkonten nach Betrag
•
Personenkonten nach Datum
•
Personenkonten nach Kontonummer
•
Personenkonten nach Referenznummer
•
Personenkonten nach Bezeichnung

---

## OP-Verwaltung und automatischer Zahlungsverkehr

OP-Verwaltung und automatischer Zahlungsverkehr
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
Die OP-Verwaltung und der automatische Zahlungsverkehr
arbeiten beide auf den offenen Posten. Es kann jetzt vorkommen, dass in der
OP-Verwaltung Belege ausgeziffert werden, die bereits in den Zahlungsvorschlägen
bzw. freigegebenen Zahlungen vorhanden sind. Dies kann gewollt sein oder einen
unerwünschten Fehler darstellen, je nachdem, wie im Unternehmen gearbeitet wird.
OP’s, die man ausziffert, werden aus den Listen/Zahlungsbelegen gelöscht und die
zu zahlende Summe wird angepasst. Um das Verhalten beeinflussen zu können, gibt
es in der OP-Verwaltung einige Einrichtungsparameter:
•
Zahlungsvorschläge beim Ausziffern überprüfen?
Hier kann man
einstellen, ob es erlaubt ist (Einstellung „Ignorieren“), eine Abfrage kommt
(Einstellung „Warnung“) oder es verboten ist (Einstellung „Warnung“), dass diese
OP’S, die bereits in einer Zahlungsvorschlagsliste enthalten sind, ausgeziffert
werden. Die Standardeinstellung ist Warnung.
•
Zahlungsliste beim Ausziffern überprüfen?
Bei bereits freigegebenen
Zahlungsvorschlägen ist diese Abfrage noch wichtiger,  da hier im
Normalfall keine Änderungen an den Zahlungsbelegen mehr erwünscht sind. Auch
hier gibt es die oben genannten Einstellungsmöglichkeiten. Die
Standardeinstellung ist Warnung.
•
¨e-Clearing¨ / ¨Kasse¨ beim Ausziffern überprüfen?
Von der Kasse und
von e-Clearing werden auch OP’s zur Auszifferung vorgesehen. Will man eine
Überprüfung, ob diese Module OP’s zur Auszifferung vorgesehen haben, so kann man
dies über diesen Einrichterparameter vornehmen. Es gibt wieder die drei
Einstellungsmöglichkeiten „Ignorieren“, „Warnung“, „Fehler“ und die Vorbelegung
ist „Warnung“.
•
Per DTA oder per Scheck verarbeitetet OP´s für Auszifferung
sperren?
Sind freigegeben Zahlungsvorschlägen bereits durch Scheckdruck bzw.
per DTA an die Bank gegangen und will man diese Zahlungen auch automatisch in
die
[...]


---

## OP-Führung mit mehreren Fremdwährungen

OP-Führung mit mehreren Fremdwährungen
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
Für Personenkonten besteht die Möglichkeit mehrere
unterschiedliche Währunge miteinander zu verrechnen. Hier ergibt sich eine
weitere Besonderheit, da die unterschiedlichen Fremdwährungen auf eine
Fremdwährung zurückgerechnet werden müssen um die Kursdifferenzen bzw. den
zuviel oder zuwenig gezahlten Betrag bestimmen zu können. Im folgendem einfachen
Beispiel sind die Zahlen so gewählt, dass die Zahlung in Sloty der Rechnung in
US-Dollar zum Tageskurs der Zahlung entspricht.
USD
PLN
Kurs
EUR
Rechnung
10.000,00 S
1,366300
7.319,14 S
Zahlung
30.713,25 H
4,220000
7.278,02 H
Währungsumrechnung 1
-30.713,25 H
4,220000
-7.278,02 H
Währungsumrechnung 2
10.000,00 H
1,374000
7.278,02 H
Kursdifferenz
0,00 H
0,00 H
41,12 S
Wird die Rechnung mit der Zahlung ausgeziffert, so
geschieht intern eine Umrechnung die den gelb markierten Zeilen entspricht. Die
Zahlung wird zum aktuellen Kurs in die Fremdwährung USD der Rechnung
umgerechnet. Dieser Kurs hat sich in der Zwischenzeit von 1,3663 auf 1,374
geändert, was zu dann zu der Kursdifferenz führt. Um diese Umrechnung zu
belegen, wird beim Ausziffern eine technischer Beleg erstellt. Dieser Beleg wird
nicht gebucht. Wird die Auszifferung aufgehoben verschwindet er sofort
wieder.
Geht die Buchung nicht auf 0 auf , so sieht die
Tabelle etwas anders aus.
USD
PLN
Kurs
EUR
Rechnung
10.000,00 S
1,366300
7.319,14 S
Zahlung
30.500,00 H
4,220000
7.227,49 H
Währungsumrechnung 1
-30.500,00 H
4,220000
-7.227,49 H
Währungsumrechnung 2
9.930,57 H
1,374000
7.227,49 H
Kursdifferenz
69,43 H
0,00 H
41,12 S
Hier wurde zuwenig gezahlt und zwar genau 69,43 USD.
Aus den zusätzlich gebildetene Währungsumrechnungszeilen lässt sich dann genau
ablesen, wie die Zahlen zustande kommen.
Hinweis:
Es wird für jeden Beleg, der aus
einer Fremdwährung in eine andere Fremdwährung umgerechnet wird, ein
zusätzlicher Währungsumrechnungsbeleg geb
[...]


---

## Optionen des Fibu-Reorganisators

Optionen
des Fibu-Reorganisators
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Optionen
F10
Direktsprung
[FIREO]
In den Optionen lassen sich für den
Test der Bewegungsdaten
, die
Reorganisation der Bewegungsdaten
bzw. für den
Test Jahreswechsel
einzelne Punkte an
und ausschalten.
Die Voreinstellung der Haken für Test Bewegungsdaten
und Reorganisation ist fest vorgegeben und wird
nicht
gespeichert.
Die Voreinstellung für Kostenstellen und Kostenträger richtet sich danach, ob
die Steuerungsparameter (Direktsprung
[SPA]
) „
Kostenstellenrechnung
angeschlossen
“ bzw. „
Kostenträgerrechnung angeschlossen
“ auf
Ja
stehen oder nicht.
Die Einstellungen für die Optionen „Test Jahreswechsel
…“, der Name und das Verzeichnis der Protokolldatei, in die alle
Auswertungsergebnisse geschrieben werden, sowie die Einstellung, ob diese Datei
vor jedem Test gelöscht werden sollen, werden pro Benutzer in der Datenbank
hinterlegt und somit jedes Mal wieder vorgeschlagen. Wenn man bei
„Temp-Verzeichnis verwenden?“ den Haken setzt, dann wird bei jedem Start vom
Reorganisator das TEMP-Verzeichnis neu bestimmt.

---

## Periodische Buchungen

Periodische Buchungen
Hauptmenü
Finanzbuchhaltung
Erfassung
Periodische Buchungen
Direktsprung
[WZA]
Ständig wiederkehrende Buchungen (z.B.
Mietrechnungen), monatliche Umbuchungen (z.B. einmalige Versicherungsrechnungen)
oder kalkulatorische Buchungen (z.B. AfA) können hier als Stammdaten mit Konto /
Gegenkonto, Buchungstext, Betrag, Turnus und Laufzeit angelegt werden. In der
Anwendung „
Periodische Buchungen“
stehen zwei Varianten zur Verfügung
1.
Wiederkehrende Belege
Hier werden alle erfassten Daten angezeigt und
können bearbeitet werden.
2.
Fällig Belege
Es werden die zum eingegebenen Stichtag anliegenden
Buchungen angezeigt.
Periodische Buchungen erfassen
Feld
Beschreibung
Bezeichnung
Bezeichnung der periodischen Buchung
      zur einfacheren Identifikation. Hier kann z.B. ein Text wie
      „KFZ-Versicherung HUK KI DB-2100“ hinterlegt werden.
Gesperrt
Wenn
      einmal Unklarheiten bei Buchungen existieren und man möchte nicht, dass
      versehentlich diese Buchungen in die Primanota gelangen, so kann man hier
      eine Sperre setzen. Beim Erstellen der Belege wird dann dieser Beleg nicht
      berücksichtigt.
Vorgangsklasse
Die
      Klasse bestimmt, was für eine Belegart später erstellt wird und ggf. wie
      die Stellung des Sollhaben-Kennzeichens ist. Die Klasse entspricht der
      Klasse, wie man sie von der Belegerfassung kennt. Folgende Klassen stehen
      zur Verfügung:
•
ZA
Zahlungseingang bzw. Zahlungsausgang.
            Einschränkend gilt hier analog zur Belegerfassung, dass im
            Hauptkonto nur Sachkonten erfasst werden können.
•
ER
Eingangsrechnung. Es sind im Hauptkonto
            nur Personenkonten und im Gegenkonto nur Sachkonten zugelassen. Das
            Sollhabenkennzeichen ist vorbelegt und kann nicht geändert
            werden.
•
EG
Eingangsgutschrift. Es sind im Hauptkonto
            nur Personenkonten und im Gegenkonto nur Sachkonten zugelassen. Das
            Sollhabenkennzeichen ist vorbelegt
[...]


---

## Plandaten Sachkonten

Plandaten
Sachkonten
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Funktionen
Plandaten
und
Plandatenübernahme
Direktsprung
[SKS]
Für jedes Sachkonto können Plandaten je Periode
angelegt werden. Diese werden in der Tabelle Kontosummen mit den Periodenwerten
abgespeichert und stehen so für Auswertungen zur Verfügung.
Manuelle Übernahme pro Konto
Diese Funktionalität erreicht man über die Funktion
Plandaten
F10
:
Die Periodeneinteilung entspricht der Vorgabe im
Firmenstamm. Je Periode werden die Planwerte eingegeben. Bei gleichen Werten
genügt die Eintragung in der ersten Periode und Auslösung der Funktion
Periodenwerte aus 1.
Periode
.
Die Plandaten des Vorjahres können mittels
Vorjahreswerte
übernehmen
übernommen werden.
Automatische Übernahme für alle Konten
Diese Funktionalität erreicht man über die Funktion
Plandaten übernehmen
SH+F10
.
Beschreibung
Planzahlen/Ist-Zahlen
Sollen die Planzahlen oder die Ist
      Zahlen als Grundlage verwendet werden?
Aus
      dem Jahr
Hier
      gibt man das Jahr an, das als Grundlage dienen soll.
Für
      das Jahr
Für
      dieses Jahr werden die Planzahlen neu generiert.
Oberkonten-Planzahlen
      erstellen
Die
      Werte für Oberkonten ergeben sich bekanntlich aus den Werten der
      Sachkonten. Deswegen existiert hier die Möglichkeit, die Planzahlen gleich
      für die Oberkonten mit zu generieren. Die Verteilung wird dann anhand der
      Struktur der Oberkonten vorgenommen.
Rundung
Bei
      Planzahlen sind im Allgemeinen kleine Beträge nicht von Bedeutung. Hier
      kann man angeben, wie genau die Daten übernommen werden sollen. Werden
      Werte größer 0 angegeben, so bezieht sich die Rundung auf die
      Nachkommastellen, bei Werten kleiner 0 werden die Zahlen vor dem Komma
      gerundet. Gibt man beispielsweise als Rundungsfaktor –2 an, so werden die
      Werte auf voll 100 Euro gerundet:
123456789,123456  =>
      123456800,00
In
      der Zeile unter dem Eingabefeld für die Rundu
[...]


---

## Prüfen des Jahreswechsels

Prüfen des Jahreswechsels
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Direktsprung
[FIREO]
Zum Überprüfen des Jahreswechsels stehen im
Hilfsprogramm „Fibureorganisation“ die Funktionen
•
Test Jahreswechsel PK (Personenkonten)
•
Test Jahreswechsel BK (Bilanzkonten)
zur Verfügung. Diese Tests können zu jedem Zeitpunkt
durchgeführt werden. Es wird dann geprüft, ob der entsprechende Kontenbereich
korrekt abgeschlossen ist. Genauere Informationen befinden sich in der
Dokumentation unter
„
FIBU-Reorganisator
“

---

## Protokoll des Fibu-Reorganisators

Protokoll
des Fibu-Reorganisators
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Protokoll
SF10
Direktsprung
[FIREO]
Das Protokoll ist eine Textdatei, in der alle
Ausgaben, die auf dem Bildschirm erscheinen mitprotokolliert werden. Am Anfang
dieser Datei stehen Datum und Uhrzeit des Aufrufs des Reorganisators, danach
folgen die Mandantenbezeichnung sowie die Version des Programms. Daran schließen
sich die Steuerparameter der Gruppe „Optionen Finanzbuchhaltung“ an. Dies sind
alles Informationen, die bei der Fehlersuche benötigt werden.
08-48-34 15.11.2007 08-48-33
08-48-34 Mandant EntwAhoi Bediener OD
08-48-34 Programmversion 7.2-Dez-Beta-13 11.11.2007
08-48-34
==============================================================================
08-48-34 Steupas Finanzbuchhaltung
08-48-34
==============================================================================
08-48-34
Bezeichnung
wert          Steupaabdat
Steupanumm
08-48-34 Finanzbuchhaltung
angeschlossen
Ja
28-05-1995           5
08-48-34 Wechselbuchhaltung
angeschlossen
Ja
28-05-1995           6
08-48-34 Kostenstellenrechnung
angeschlossen
Ja
28-05-1995           8
08-48-34 Bei Kostenstellen Oberkonten
bebuchen
Ja
01-01-1999         563
08-48-34 Kostenstellen Dimensionen
aktiv
Ja
01-01-2001         582
08-48-34 Kostenträgerrechnung
angeschlossen
Ja
01-01-2005         569
08-48-34 Bei Kostenträgern Oberkonten
bebuchen?
Nein
01-01-1901         570
08-48-34 OP-Verwaltung
aktiv
Ja
28-05-1995         140
08-48-34 Mahnwesen
aktiv
Ja
01-01-1901          37
08-48-34 Zinsabrechnung
aktiv
Ja
01-01-1901          38
08-48-34 Zinsabschlagsteuer
berechnen
Ja
01-02-2003         555
08-48-
[...]


---

## Reorganisation Fragmente

Reorganisation Fragmente
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorg. Kontoblätter
Direktsprung
[FIREO]
Die
Reorganisation der Fragmente
entfernt
Fragmente (siehe
Test Fragmente
) aus der Datenbank.
Diese wären alle Belege, deren Stamm bzw. Summensatz fehlt, alle
Kontoblattpositionen und Summen ohne Stammsatz und alle Journalpositionen, deren
Verweise fehlen.

---

## Reorganisation Kontoblätter

Reorganisation Kontoblätter
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorg. Kontoblätter
Direktsprung
[FIREO]
Bei der Reorganisation der Kontoblätter werden zuerst
unvollständige Kontoblätter entfernt, die Kennzeichen in den Fibupositionen
aktualisiert und anschließend die Kontoblattsummen nachgerechnet, die für den
Übertrag von einem zum anderen Kontoblatt nötig sind.

---

## Reorganisation Oberkonten

Reorganisation Oberkonten
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorg. Oberkonten
Direktsprung
[FIREO]
Die
Reorg
anisation der Oberkonten
ist
dieselbe, die Sie im Pfleger der Oberkontenstammdaten finden. Sie dient
hauptsächlich dazu, die Summen nachzurechnen, falls man die Struktur der
Oberkonten geändert hat. Dort kann man auch die Plandaten aus den Sachkonten
übernehmen, bzw. die Plandaten aus den Oberkonten ab einer bestimmten Stufe
übernehmen.

---

## Reorganisation Währung

Reorganisation Währung
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorg. Währung
Direktsprung
[FIREO]
Die
Reorganisation der Währung
setzt einzelne
Felder innerhalb von Belegen, die zur Währungsverarbeitung benötigt werden.
Diese wären:
1.
Missing zu 0
Es wird die Währungsnummer auf die Buchwährung
gesetzt, falls keine Nummer dort eingetragen ist; der Währungskurs und
Währungsfaktor wird auf 1 gesetzt, falls er fehlt.
2.
Missing zum Originalbetrag
Sind die Währungsbeträge nicht
eingetragen, werden in allen Belegen, die als Währung die Buchwährung stehen
haben, in das Feld für Fremdwährung der Originalbetrag eingetragen.

---

## Reorganisation starten

Reorganisation starten
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Reorganisation
Direktsprung
[FIREO]
Einige dieser Problemfälle können nicht nur erkannt,
sondern auch behoben werden. Dazu dienen die diversen Reorganisationsoptionen.
Der Hauptpunkt
Reorganisation
lässt sich über den Menüpunkt
Optionen
noch genauer klassifizieren. Es sind grundsätzlich nicht alle
Punkte ausgewählt, sondern nur die, die für den Standardablauf  wichtig
sind. Werden noch zusätzliche Reorganisationsoptionen benötigt, so werden Sie
bei eventuellen Fehlermeldungen im Bewegungsdatentest aufgefordert, die
entsprechenden Haken zu setzen. Hier sind alle Reorganisationsmaßnahmen
aufgeführt. Es werden jedoch nie alle ausgeführt, da sie zusätzlich von SPAs und
Optionen abhängig sind.
•
OP – Einträge. Wird nur ausgeführt, wenn die Option „Offenen Posten“
aktiviert wurde.
•
Interne Umbuchungen. Wird nur ausgeführt, wenn die Option „Offenen
Posten“ aktiviert wurde.
•
Forderungen Sonstige Buchungen Re/Gu
•
Forderungen Sonstige Buchungen EB
•
F&V AR / AG
•
F&V ER / EG
•
Sachkonten = 0
•
SONSTIGE – I
•
SONSTIGE - II
•
RestPosten-I
•
RestPosten - II
•
Zahlungen
•
Ausbuchungen
•
Zahlungen
•
Sachkonten - OP - Einträge
•
Fehlende Kontosummeneinträge
•
KontoSummen gebucht & erfasst
•
OPMahnListe zurücksetzen
•
MahnListe zurücksetzen
•
OPMahnListe zurücksetzen
•
Forderungen & Verbindlichkeiten
•
Forderungen Saldierung
•
Kostenstellensummen
•
Fehlbuchungen zurücksetzen

---

## Reporte bearbeiten

Reporte bearbeiten
Die Reporte werden mit Hilfe des Branchen-ERP-Etikettendrucks
bearbeitet. Hier gibt es folgende Besonderheiten:
FS-Formate
Die Daten werden in der Form dargestellt, wie sie in
der Datenbank stehen. D.h. das Feld FIBUVP_SOLLHABEN wird als 1 oder 2
dargestellt. Will man nun im Report die textliche Darstellung sehen, so muss und
kann man dies dem Report mitteilen. Dafür existieren in Dialog „Tabelle
bearbeiten“ in der Funktionsgruppe „Referenz-ERP Formatierung“ alle in der aktiven
Auswahlliste verwendeten FS-Formte. Der Name der Funktion entspricht dem
FS-Format. Im unteren Beispiel sieht man wie der Syntax dieser Funktionen
ist.
Der erste Parameter ist der Zahlenwert, der als Text
umgewandelt wird. Der zweite Parameter ist Optional und gibt die Anzahl der
Zeichen an, die ausgegeben werden sollen. Würde man im unteren Beispiel die
Länge weglassen, dann würde statt „S“ und „H“ in dem Report „Soll“ bzw. „Haben“
erscheinen.
Zusätzliche Variablen
Für die Reporte existieren zusätzliche Variablen.
Unter „
Filter
“ werden Variablen – Label und
Value - mit den Bereichseingrenzungen und den Filtereinstellungen
bereitgestellt.
Un
ter
„Individuelle Zusatzinformation“
stehen Informationen, die über die
Darstellungsfunktion „Vorbelegung“ im Feld „ReportInfo“ definiert wurden.
Dort
kann auf ein View, Tabelle oder auf eine Prozedur zugegriffen werfen:
Der Wert muss als „select
…“ definiert werden. Das Ergebnis sollte immer einen Datensatz zurückliefern,
und zwar auch dann, wenn keine Daten vorhanden sind. Das Ergebnis findet man
dann unter „individuelle Zusatzinformation“
Unter „
Information Bedienerstamm
“ stehen die
Informationen, des Anwenders, der die Liste druckt.
Unter „
Information Mandantenstamm
“ stehen die
Informationen zum Mandanten.
Unter
„Zusatz Informationen“
stehen die Werte,
die aus einer privaten View mit dem Namen „p_ReportHeaderInformation“ liefert.
Achtung:
Diese
View gilt für alle Auswahllisten-Reporte und sollte nur einen Datensatz
l
[...]


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

## RFS-Konto

RFS-Konto
Es handelt sich hierbei in der Regel um das Bisykonto
( Achtung: Das RFS Konto wird bei einigen Buchungsvorgängen nicht benutzt,
enthält aber denn eine Kontonummer !)

---

## Resultset der FIBU-Datenübernahme

Resultset der
FIBU-Datenübernahme
Die Importverfahren FIBU-XML-Import, FIBU-CSV-Import
und FIBU-XLSX-Import haben alle das gleiche Resultset. Der Import ist an die
Belegerfassung Finanzbuchhaltung angelehnt und die Felder haben somit auch die
gleiche Bedeutung.
Fett
dargestellte Felder sind Pflichtfelder.
uebertragungskennung und
      uebertragungsnummer
Beim
      XML-Import werden diese Felder verwendet, um sicherzustellen, dass Daten
      nicht mehrfach eingespielt werden. D.h. in jeder Datei muss sich Kennung
      oder Nummer von den bereits importierten Daten unterscheiden.
Im
      FIBU-CSV-Import und FIBU-XLSX-Import enthalten sie die FA_ID bzw. die
      FA_MNDNR unter der die Datei im Archiv abgelegt wurde.
ident
Zeilen mit gleicher Ident werden
      versucht zu einem Beleg zusammenzufassen. Neben der Ident dürfen sich auch
      Fibuv_klasse, Fibuv_datum, Hauptkonto, Hauptkoststel, Hauptkstr,
      Hauptksobj, (fibuvp_sollhaben ), Jahrnummer und Perinummer nicht
      unterscheiden. Ansonsten wird ein neuer Beleg erstellt.
poszaehler
Gibt
      zum einen die Reihenfolge innerhalb eines Beleges an und dient auch im
      Fehlerfall zur Identifizierung der Zeile
fibuv_klasse
Für
      die Belegklasse sind folgende Werte erlaubt:
1
      Zahlungen
2
      Ausgangsrechnung
3
      Ausgangsgutschriften
4
      Eingangsrechnung
5
      Eingangsgutschriften
6
      Sonstige Belege
Hinweis:
Fibuv_klasse und Sollhaben sind
      für AR, AG, ER und EG eng miteinander verknüpft.
Wird bei der Belegklasse 2 (AR), 3
      (AG), 4 (ER) oder 5 (EG) das falsche Sollhabenkennzeichen angegeben, so
      wird die zum Sollhabenkennzeichen passende Belegklasse verwendet. Wird
      also z.B: bei der Belegklasse 4 (ER) das Sollhabenkennzeichen 2 (Haben)
      angegeben, geht das System davon aus, dass die Belegklasse die 5 (EG) sein
      sollte.
fibuv_herktyp
Kennzeichen, wie der Beleg

[...]


---

## Saldenbestätigung drucken

Saldenbestätigung drucken
Hauptmenü
OP-Verwaltung
Information und Abstimmung
Saldenbestätigung
Die Saldenbestätigung druckt den Stand der offenen
Posten zu einem bestimmten Stichtag aus. Es werden auch Konten mit Saldo 0
gedruckt, solange zu diesem Stichtag offene Posten existieren. Will man alle
Kunden, also auch diejenigen, die zum Stichtag keine offenen Posten mehr haben,
andrucken, so kann man in der
F2
-Auswahl hinter „
Auch Kunden ohne OP’s
drucken
“
Ja
eintragen. Es werden dann auch die Kunden ohne OP’S
gedruckt, wenn irgendwann vor dem Stichtag für diesen Kunden offene Posten
existierten. Es erscheint dann anstelle der Liste nur der Text „Zum Stichtag
sind keine offenen Posten vorhanden.“. Man kann diesen Text in der
F2
-Auswahl in dem Feld „
Hinweistext keine OP’s
“ überschreiben.
Zusätzlich werden der
Stichtag
, der
Kontenbereich
und
das
Datum bis zu dem die
Antwort
erwartet wird, abgefragt.
Stichtag
und
Antwort bis
werden in den
Text der Saldenbestätigung mit übernommen.
Beispielausdruck einer Saldenliste
(Stand
18.10.2007)

---

## Sammelkonto 1 – 5

Sammelkonto 1 – 5
Zahlungen, die hier benannte Konten berühren, werden
auf der Banksammelliste  mit einem * als Sammelbuchungen
gekennzeichnet. Diese Buchungen werden gerafft übertragen

---

## Schnellabschluss

Schnellabschluss
Hierbei wird nur unterbrochen. (F5) Hierbei wird die
Kassensitzung nur vorübergehend unterbrochen und die Verbindung zum Display
geschlossen. Ist dies der Fall, muss als nächste Aktion die Funktionalität „
Fortsetzen „ gewählt werden und die folgenden Einträge werden unter derselben
Kassensitzungsnummer abgespeichert, auch die Verbindung zum Display wird wieder
hergestellt (F4).

---

## Softresearch Lohn-XL/XXL

Softresearch Lohn-XL/XXL
Hauptmenü
Abschlussarbeiten
DATEV / Import / Export
Import
Funktion
F9
Import Starten
Funktion
F4
Importdatei lesen
Direktsprung
[FIIM]
Bei dieser Schnittstelle handelt es sich um den Import
der Lohndaten aus der Software Lohn-XL/XXL. Es handelt sich bei diesen Buchungen
um reine Sachkontenbuchungen. Die Lohnsoftware bietet diverse
Exportschnittstellen an. In Referenz-ERP sind die Schnittstellen F_SR11 und F_SR13
Implementiert.
Satzaufbau F_SR11
Stelle
Länge
Format
Bedeutung
1
1
Buchungskennzeichen S oder
      H
2
6
Linksbündig
Kontonummer
8
6
Linksbündig
Gegenkonto
14
12
Linksbündig
Kostenträger (wird
      ignoriert)
26
10
Linksbündig
Kostenstelle
36
12
Rechtsbündig (12.2)
Betrag
48
6
MMJJJJ
Monat/Jahr
54
8
TTMMJJJJ
Tag/Monat/Jahr
62
25
Linksbündig
Buchungstext
87
6
Linksbündig
Personalnummer (wird
      ignoriert)
93
3
Linksbündig
Lohnartnummer (wird
      ignoriert)
96
9
Linksbündig
Einheit (Stunde/Tage) (wird
      ignoriert)
105
3
Linksbündig
Währungsbezeichnung DM oder
      EUR
108
19
Leer
127
2
CR/LF
Satzaufbau F_SR13
Stelle
Länge
Format
Bedeutung
1
3
Buchungsnummer
4
25
Buchungstext
29
10
TT.MM.JJJJ
Tag/Monat/Jahr
39
1
Buchungskennzeichen S oder
      H
40
8
Rechtsbündig
Kontonummer
48
8
Rechtsbündig
Gegenkonto
56
9
Rechtsbündig 9.2
Betrag
65
3
Linksbündig
Währungskennzeichen DM oder
      EUR
68
2
CR/LF

---

## Spaltendefinition

Spaltendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Spaltendefinition
Direktsprung
[CCD]
Die Spaltendefinition ist die Grundlage einer
Chefcockpitauswertung. Hier legt man fest, wie viele Spalten es gibt, und was
bzw. welcher Zeitraum ausgewertet werden soll. Zusätzlich kann auch ein
abweichender Report festgelegt werden. Standardmäßig werden zwei Reporte
angeboten: „Kennzahlanalyse.rpt“ und „Kennzahlanalyse_quer.rpt“. Für bis zu 9
Spalten wird der Report „Kennzahlanalyse.rpt“ verwendet, ansonsten der Report
„Kennzahlanalyse_quer.rpt“, der im Querformat ausgedruckt wird und bis zu 12
Spalten enthalten kann. Wenn z.B. die Zahlen zu groß werden – im Standard werden
sie dann umgebrochen – oder man einfach ein etwas anderes Design verwenden will,
so kann man unter „
Abweichender Report“
einen privaten Report
hinterlegen. Es ist dabei Sinnvoll, einen der beiden Reporte als Grundlage zu
verwenden.
Was
Hier können zurzeit die Werte Konstante und Formel
eingetragen werden. Konstanten sind fest definierte Werte, die z.B. als
Vergleichswerte in die Liste eingetragen werden. Hier sind nur numerische Werte
erlaubt. Diese werden mit vier Nachkommastellen gespeichert. Mit den Formeln
werden die Werte in den einzelnen Zeilen und Spalten errechnet. Hier kann über
die Kürzel auf Kontenlisten und bereits definierte Zeilenergebnisse zugegriffen
werden. Auch können Datenbankfunktionen aufgerufen werden. Mehr zu Formeln steht
unter der Dokumentation der Zeilendefinition.
Zeitraum Jahr
Hier kann über
F3
angegeben werden, auf welchen
Zeitraum sich diese Spalte beziehen soll. In den Auswertungen wird ein
bestimmter Zeitraum abgefragt. Soll sich die Spalte auf genau diesen beziehen,
so gibt man hier „aktuelles Jahr“ als Zeitraum an. Soll sich die Spalte jedoch
auf das Jahr beziehen, dass vor diesem Zeitraum liegt, so kann man hier
„Vorjahr“ angeben. Die Werte werden dann entsprechend der Eingrenzung
zusammengesucht, nur dass
[...]


---

## Stammdaten der Fibu

Stammdaten der Fibu
Allgemeines zur Anlage des Kontenplans:
Der Sachkontenplan ist die wesentliche Grundlage der
Buchhaltung. Entsprechend sorgfältig sollte deshalb bei der Strukturierung der
Konten vorgegangen werden. Es ist möglich die
DATEV-Kontenpläne
SKR03 bzw. SKR04 zu
übernehmen. Diese können sehr gut als Grundlage dienen, um die eigenen
Vorstellungen in einen fertigen Rahmen einzupassen.
Üblicherweise wird der generelle Aufbau eines
Kontenplans durch Anforderungen des Steuerberaters oder branchenübliche
Verfahren vorgegeben. Innerhalb dieser Rahmenvorgaben werden dann die
individuellen Belange eines Unternehmens untergebracht. Wenn man sich auf einen
vorgegebenen Plan stützt, müssen lediglich noch die individuellen Konten
eingetragen werden.
Zur optischen Gestaltung von GuV, Bilanz, Auswertungen
etc. empfiehlt es sich jedoch, diese Anforderungen ebenfalls bei der Planung zu
berücksichtigen. Referenz-ERP bietet hierzu vielfältige Möglichkeiten
Für die Erfassung und Gliederung eines Kontenplans
sind folgende Parameter besonders wichtig:
•
Konto-Druckposition
•
Sachkonto
•
Oberkonto
Insbesondere bei der kompletten Neuanlage eines
Sachkontenplans sollte die Planung in den oben angegebenen Schritten
erfolgen.
Die Dokumentation für die Stammdaten der Mahnungen,
den automatischen Zahlungsverkehr, Zinswesen, Kostenrechnung, Steuer, E-Clearing
oder Wechselbuchhaltung findet man in dem Kapitel zu diesen Themen.

---

## Stammdaten Finanzbuchhaltung löschen (inkl. 2+28+29)

Stammdaten Finanzbuchhaltung löschen (inkl.
2+28+29)
Es werden die Daten in folgenden Tabellen
gelöscht:
SachKontStamm
SachKontStammAddon
OberSachKonto
SachKontoZins
SachKontDruckPos
KontoSortierPos
Kontostamm unter der Bedingung where (KontoTyp=1) or
(KontoTyp=3)
Beim Löschen der Stammdaten der
Finanzbuchhaltung  werden automatisch die
Vorgänge Finanzbuchhaltung
und die
Anlagenkartei
Stammdaten
und
Bewegungsdaten
mit gelöscht.

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

## Standardvorgänge Fibu

Standardvorgänge Fibu
Hauptmenü
Finanzbuchhaltung
Buchungen / Journal
Standardvorgänge Fibu
Direktsprung
[FISV]
Verschiedene Darstellungsvarianten zum Anzeigen und
ggf. bearbeiten der Buchungssätze stehen zur Verfügung: gebuchte Belege,
ungebuchte Belege, umfassende Selektionsverfahren zum Suchen von Belegen.
Ungebuchte Belege können auch von hier aus gebucht werden; auch Fehlbuchungen
können rückgängig gemacht werden.
In der Variante
Positionsüberblick
/
IDEA
werden alle Felder einer Buchungsposition dargestellt. Die Selektion
ermöglicht Eingrenzungen nach Konto, Datum, usw. . Diese Variante kann zur
Übergabe der Datensätze an die Finanzbehörden genutzt werden:
Nach $ 147 Abs.6 AO ist es der Finanzverwaltung
möglich, die Daten von elektronischen Buchführungssystemen „digital“ zu prüfen,
entweder durch Datenträgerüberlassung und/oder durch mittelbaren bzw.
unmittelbaren Zugriff. Um eine Verwertbarkeit der Daten zu erreichen, müssen die
Dateiformate standardisiert sein. In Referenz-ERP wurde der ASCII-Export so erweitert,
dass eine Datei „Index.xml“ erstellt wird, die dem Beschreibungsstandard
GDPdU-01-08-2002 entspricht. Diese kann parallel zum Export erstellt werden,
indem man entweder in das Feld „index.xml laut GDPdU“ ‚JA’ einträgt oder einzeln
ohne Daten über die Funktion „Index.xml erstellen“ (F9).
Für das Erstellen der Datei index.xml beim
ASCII-Export werden Dokumenttyp-Definitionen benötigt. Diese befinden sich in
den Dateien „gdpdu-01-09-2004.dtd“ oder „gdpdu-01-08-2002.dtd“, die sich auf dem
BIN-Verzeichnis von Referenz-ERP befinden müssen. Wenn diese Dateien nicht vorhanden
waren, erschien lediglich die Meldung: „Die XML-Indexdatei %s lässt sich nicht
erstellen. Setzen Sie sich bitte mit Ihrem Systemadministrator in Verbindung.“
Jetzt wird vor der Erstellung der Datei geprüft, ob die Dateien vorhanden sind.
Es erscheint dann ggf. diese Meldung: „Auf dem Arbeitsverzeichnis von Referenz-ERP
fehlt die Dokumenttyp-Definitionsdatei gdpdu-01-09-2004.dtd od
[...]


---

## Steuerauswertungen

Steuerauswertungen
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuerauswertung
Direktsprung
[UVAA]
Die Auswertungen für die Steuer findet man in der
Finanzbuchhaltung unter dem Menüpunkt „Steuerauswertung“ oder
„Steuerverprobung“. In den Steuerauswertungen lassen sich die Steuerwerte nach
folgenden Kriterien auswerten:
Variante
Klasse / Schlüssel /Datum
Klasse / Schlüssel
Klasse / Gruppe / Schlüssel /
      Datum
Klasse / Gruppe /
      Schlüssel
Steuerkonten
Der
      Saldo aller im Sachkontenstamm als Steuerkonto gekennzeichneten Konten
      wird hier aufgelistet. EU-Erwerbe werden nicht ausgewiesen, wenn sie nicht
      manuell auf Steuerkonten gebucht wurden.
Einzelkonten
Diese Liste kann zusätzlich als
      Steuerverprobung herangezogen werden. Sind Erlös- bzw. Aufwandskonten mit
      unterschiedlichen Steuersätzen bebucht worden, so werden diese gelb
      eingefärbt.
Hier
      steht der Report „
Steuerwerte nach
      Einzelkonten
“
F10
zur
      Verfügung-
Zusätzlich zu der hier erwähnten Anwendung existieren
noch die Anwendungen
Steuerverprobung
,
Zusammenfassende Meldung
,
Vorsteuerabzug
und
Umsatzsteuerwerte
.

---

## Steuersätze einrichten

Steuersätze einrichten
Das Steuersystem in Referenz-ERP basiert auf den
Elementen
•
Steuerklasse
(Umsatzsteuer / Vorsteuer)
•
Steuergruppe
(Sachkonto / Personenkonto)
•
Steuerschlüssel
(Artikel / Fibu)
Die Pfleger hierfür findet man im Menü
Administration
und dort unter
Steuern.
Die einzelnen Steuersätze
ergeben sich aus einer Kombination dieser drei Elemente und dem Steuerabdatum.
Detaillierte Informationen zu diesem Thema finden Sie im Bereich
Steuersätze
.
Achtung:
Für die Umsatzsteuervoranmeldung hat sich für die
Kennzahl 39 eine Änderung ergeben. Siehe dazu
Auswertungspositionen
und
Dauerfristverlängerung/Sondervorauszahlung
.
Es kann vorkommen, dass für andere Länder als
Deutschland besondere gesetzliche Vorschriften gelten. Diese müssen separat in
die Finanzbuchhaltung eingebaut werden. Um welches Land es sich handelt, wird in
dem Steuerparameter 663 „Fibu-Besonderheiten berücksichtigen für“ eingestellt.
Bisher ist neben Deutschland nur Österreich eingerichtet. In Österreich ist die
Umsatzsteuervoranmeldung - Nachkommastellen der Beträge - davon betroffen.

---

## Steuerverprobung

Steuerverprobung
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Steuerverprobung
Direktsprung
[UVSV]
In der Anwendung „Steuerverprobung“ findet man
folgende Auswertungen
Variante
Steuerverprobung
Es
      werden alle steuerlich relevanten Belege ausgewertet unabhängig von der
      Steuerklasse. Dabei wird die Steuer laut Umsatz – also errechnet aus dem
      Betrag und dem Steuersatz – dem Steuerwert, der dem Konto zugewiesen
      wurde, gegenübergestellt.
Umsatzsteuerverbrobung
Es
      werden nur die Belege mit den Steuerklassen 1 und 2 (Umsatzsteuer)
      ausgewertet.
In allen Anwendungen werden die Steuerauswertungen in
einer Auswahlliste dargestellt und könne somit über F4-Kurzliste, Excelexport,
Quickreport, usw. weiterverarbeitet werden. Bei allen Auswahllisten werden die
Steuerklassen nicht mehr nach Brutto und Netto getrennt ausgewertet.
Zusätzlich zu der hier erwähnten Anwendung existieren
noch die Anwendungen
Steuerauswertungen
,
Zusammenfassende Meldung
,
Vorsteuerabzug
und
Umsatzsteuerwerte
.

---

## Tabelle zur Version: 8.3.2305.26

Tabelle zur Version: 8.3.2305.26
ID
Releasenote - Titel
Geprüft
33824
Erstellen einer neuen TSE-Einrichtung
33713
Quellbeleg-Freigabe bei Stornierung von kopierten
      Vorgängen
33805
Bestandsbuchungen bei Quellbeleg-Freigabe in
      Storno-Funktionen

---

## Tabelle zur Version: 9.0.2502.6

Tabelle zur Version: 9.0.2502.6
ID
Releasenote - Titel
Geprüft
37881
Differenzwertberechnungen
38119
Outlook Drag and Drop
38208
Archivansicht
38257
Archiv-Vorschau "großer" Pdf-Inhalte
38074
XRE - Fibuerfassung - Kontonummer nun korrekt

---

## Test Anlagenbuchhaltung

Test Anlagenbuchhaltung
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Anlagenbuchhaltung
Direktsprung
[FIREO]
Im
Test Analgenbuchhaltung
werden die
Einträge auf Konsistenz geprüft. Es werden folgende Tests durchgeführt:
Fehlerhafte Umbuchungsverweise
Wird ein Anlagegut umgebucht, wird intern das
Ursprüngliche Anlagegut vermerkt. Dieser Test listet alle Anlagegüter auf, bei
denen entweder der Eintrag im ursprünglichen Anlagegut fehlt oder der
Umbuchungsbeleg nicht existiert. Sollte dieses Problem auftauchen, muss entweder
der Umbuchungsbeleg gelöscht werden oder der die Umbuchungszeile im
Originalbeleg gelöscht werden.
Fehlerhafter Verweis zur Fibu
Wenn aus der Anlagenbuchhaltung heraus Belege erstellt
werden oder Finanzbuchhaltungsbelege bestimmten Anlagegütern zugewiesen wurden,
wird ein Verweis erstellt. Zeigt der Verweis auf einen nicht existierenden
Beleg, so kann man Fibu und Anlagenbuchhaltung nicht mehr abstimmen. Alle
Fehlerhaften Verweise werden hier aufgelistet.
Restbuchwert
Hier wird getestet, ob der Restbuchwert des
Anlagengutes eventuell kleiner als 0 ist. Dies kann nur dann geschehen, wenn man
ein Anlagegut mit Gewinn verkauft hat und die Aufwands/Ertragszeile noch fehlt.
Es erscheint dann am Ende der Zeile der Hinweis: „Verkauft ohne
Erlös/Aufwandseintrag“. Ist dies nicht der Fall, so erscheint der Hinweis
„Fehler!“. Anlagegüter, deren Restbuchwert kleiner als 0 ist, werden in der
Auswahlliste Anlagestamm (Direktsprung
[ANKAS]
) rot gekennzeichnet.

---

## Test Jahreswechsel

Test Jahreswechsel
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Jahreswechsel
Direktsprung
[FIREO]
Der Jahreswechsel in der Finanzbuchhaltung Referenz-ERP kann
jederzeit, auch wenn alle Perioden des abzuschließenden Jahres noch offen sind,
durchgeführt werden und auch jederzeit wiederholt werden. Außerdem steht es
ihnen offen, den Jahreswechsel auch manuell durchzuführen. Dies birgt natürlich
die Gefahr, dass beim Jahreswechsel Fehler auftreten könnten. Die Menüpunkte
Test Jahreswechsel PK
(Personenkonten) und
Test
Jahreswechsel BK
(Bilanzkonten) prüfen, ob ein Wirtschaftsjahr für den
entsprechenden Kontenbereich korrekt abgeschlossen ist und weist Sie auf Fehler
oder Auffälligkeiten hin. Sie werden bei der Auswahl aufgefordert, eine
Jahreszahl einzugeben. Wenn Sie einfach bestätigen, ohne die Jahreszahl
einzugeben, können für alle Wirtschaftsjahre Tests durchgeführt werden.
Teste Buchungsstatus
Sind alle Belege im abzuschließenden Jahr schon
gebucht? Wenn nein, werden Sie aufgefordert, in den entsprechenden Perioden die
Buchungen nachzuholen.
Teste Summen
Nach einem ordnungsgemäßen Jahreswechsel muss die
Summe aller Konten von Eröffnungs- bis Abschlussperiode Null ergeben. Ansonsten
kann man davon ausgehen, dass noch neue Belege hinzugekommen sind, nachdem der
Jahreswechsel durchgeführt worden ist. Führen Sie den Jahreswechsel erneut
durch.
Vergleiche Abschluss mit Eröffnung
Abschlussbuchungen und Eröffnungsbuchungen müssen
betragsmäßig gleich hoch sein. Unter Optionen kann eingestellt werden, ob man
nur die Konten prüfen will, deren Saldo im Vorjahr ungleich 0 ist. Dann darf bei
„
Vergleich trotz 0-Saldo
“ kein Haken gesetzt sein.
Treten hier
Differenzen auf, müssen evtl. entsprechende manuelle Buchungen nachgeholt
werden.
Wirtschaftsjahrüberschneidung
Belege können über die Periode oder das Belegdatum
einem Wirtschaftsjahr zugeordnet werden. Im Allgemeinen sollte das Belegdatum im
Bereich der Periode liegen, der dies
[...]


---

## Test Bewegungsdaten

Test
Bewegungsdaten
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Bewegungsdaten
Direktsprung
[FIREO]
Im
Test Bewegungsdaten
werden Belege, Summen
und Fehlerprotokolle geprüft und Sie werden gegebenenfalls aufgefordert,
bestimmte Aktionen durchzuführen, um das Problem zu beseitigen. Diese Tests
lassen sich über Optionen steuern (dazu schalten weiterer Tests bzw. Ausblenden
von Test). Die Optionen sind so eingestellt, dass alle für den normalen
Geschäftsablauf nötigen Daten getestet werden.
Fehlbuchungen
Wenn beim Verbuchen von
Belegen Fehler aufgetreten sind, die noch nicht bereinigt wurden, werden Sie
hier noch einmal darauf hingewiesen, dass Handlungsbedarf besteht. Eine genauere
Beschreibung dieser Fehler finden Sie im Bereich Buchungen Fibu unter
Journal/Ereignisprotokoll (Direktsprung
[JOUR]
)
Interne Ident
Hier wir die interne
Verkettung von Belegen geprüft. Sollte wider Erwarten die interne Identifikation
bei einem Beleg nicht stimmen, lässt sich dies durch eine Reorganisation wieder
berichtigen.
Buchwährung
Es muss in jedem Fall ein Eintrag im Währungsstamm für
die Buchwährung vorhanden sein.
Nachkommastellen
Man kann im
Währungsstamm die Anzahl der Nachkommastellen verändern. Tut man dies unbedacht
und ändert die Währung so, dass sich die Nachkommastellen verringern, so kann es
zu Rundungsproblemen kommen. Hier werden alle Belege angezeigt, die mehr
Nachkommastellen haben, als hinterlegt.
Mahnvorschläge ohne OP
Eine Liste der
Mahnvorschläge, zu denen kein OP mehr existiert. Sollte im laufenden Betrieb
nicht vorkommen. Wird durch eine Reorganisation zurückgesetzt, wenn unter
Optionen Mahnwesen separat angeschaltet wird.
OP ohne Mahnvorschläge
Eine Liste der
OPs, die eine Mahnvorschlagsnummer eingetragen haben, für die jedoch keine
Vorschlagsliste mehr existiert. Wird durch eine Reorganisation zurückgesetzt,
wenn unter Optionen Mahnwesen separat angeschaltet wird.
Mahnvorschläge ohne Liste
Hier
existiert
[...]


---

## Test Fragmente

Test Fragmente
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Fragmente
Direktsprung
[FIREO]
Durch Systemabstürze kann es dazu kommen, dass
zusammengehörende Daten nicht vollständig erfasst sind. Durch die interne
Datenstruktur ist es möglich, zu erkennen, wo dieser Fehler aufgetreten ist. Der
Test Fragmente
listet solche unvollständigen Daten für Belege und
Kontenblätter auf.
Beleg ohne Sammelposition
Bei
automatisch erzeugten Belegen wird die Positionszeile mit den Gesamtwerten am
Ende abgespeichert. Bei einem Systemabsturz fehlt diese Position dann
gegebenenfalls. Alle Belege mit diesem Fehler werden hier aufgelistet.
Belege ohne Abschluss/Stammsatz
Erst
wenn ein Abschlusssatz geschrieben worden ist, wird ein Beleg vom System als
vollständig erkannt. Die Belege ohne diesen Satz werden hier aufgelistet.
Kontoblätter ohne
Abschluss/Stammsatz
Kontoblätter sind im Prinzip so aufgebaut wie
Belege, so dass auch hier eine Prüfung stattfinden kann, ob die Kontenblätter
vollständig verarbeitet wurden.
Journaleinträge ohne Beleg
Im Journal
werden nur die Verweise auf den Beleg gespeichert, nachdem er gebucht wurde.
Sind diese Verweise fehlerhaft, oder existiert der Beleg nicht mehr, so werden
sie hier aufgelistet.

---

## Test Währung

Test Währung
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Währung
Direktsprung
[FIREO]
Im
Test Währung
werden die Belege
geprüft, ob die Währungsinformationen in ihnen korrekt sind.
Buchwährung
Es muss in jedem Fall ein
Eintrag im Währungsstamm für die Buchwährung vorhanden sein. Wenn es sich
bei der Buchwährung um Euro handelt wird noch zusätzlich geprüft, ob als
Nachkommastelle für den Betrag eine 2 und für die Rundung die kleinste
zugelassene Einheit 0,01 eingetragen ist. Ist dies nicht der Fall, wird eine
entsprechende Fehlermeldung ausgegeben.
Nachkommastellen
Man kann im
Währungsstamm die Anzahl der Nachkommastellen verändern. Tut man dies unbedacht
und ändert die Währung so, dass sich die Nachkommastellen verringern, so kann es
zu Rundungsproblemen kommen. Hier werden alle Belege angezeigt, die mehr
Nachkommastellen haben, als hinterlegt.
Währungsbetrag auf  0
Prüft, ob
für einen Beleg in Fremdwährung auch ein Betrag in Fremdwährung eingetragen
ist.
Währungskurse
Ist der Währungskurs,
der zum Zeitpunkt der Erfassung aktiv war, für diesen Beleg hinterlegt?
Währungsformel
Ist die Währungsformel
in diesen Beleg hinterlegt?
Währungsbeträge
Für Belege in
Fremdwährung wird auch eine Kontrollsumme geführt. Diese Belege lassen sich
nicht reorganisieren und müssen gegebenenfalls neu erfasst werden.
Auszifferung
Auch für Fremdwährungsbelege gilt, dass währungsseitig
ein Auszifferung auf Null aufgehen muss (siehe Kursdifferenzen). Sollte - durch
was für Umstände auch immer - eine Auszifferung nicht aufgehen, müssen Sie
manuell eingreifen und in der OP-Verwaltung diese Auszifferung mit
F7
zurücksetzen und danach wieder ausziffern. Wenn sich der Fehler dadurch nicht
beseitigen lässt, wenden Sie sich bitte mit einer genauen Fehlerbeschreibung an
Branchen-ERP.

---

## Test Stammdaten

Test Stammdaten
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Stammdaten
Direktsprung
[FIREO]
Im Test Stammdaten werden Ihre Stammdaten - hierzu
gehören der Kundenstamm, der Sachkontenstamm sowie die Forderungsgruppen u.v.m.
- auf korrekte Einrichtung getestet. Um einen möglichst reibungslosen Ablauf zu
gewährleisten, sollten Ihre Daten so eingerichtet werden, dass bei diesem Test
keine Fehler auftauchen.
Steuerklasse 0
Es muss im System
einen Steuersatz mit der Steuerklasse 0 geben. Dieser wird als Fehlersteuersatz
herangezogen. Wird hier ein Fehler angezeigt, so gehen Sie in den
Stammdatenpfleger "Steuersätze einrichten" (Direktsprung
[STS]
) und
tragen dort den fehlenden Satz ein.
Fehlende Konten im Steuersatz
Es kann
vorkommen (z.B. durch Datenimport), dass im Steuersatz Sachkonten fehlen, oder
Sachkonten eingetragen sind, die nicht existieren. Dies darf auf keinen Fall
vorkommen, da Daten, die diese Steuersätze verwenden können, nicht verbucht
werden. Löschen Sie entweder den Steuersatz, oder tragen Sie die Konten im
Stammdatenpfleger für
Sachkonten
(Direktsprung
[SKS]
) nach.
Steuerkonto bei innergemeinschaftlichem
Erwerb
Wenn Steuersätze mit der Steuerformel
„Innergemeinschaftlicher Erwerb“ eingerichtet sind, muss der Steuersatz bei
„Satz innergem.Erw.“ eingetragen werden und nicht bei Steuersatz. Im Normalfall
wird diese Fehleingabe jedoch bereits vom Programm abgefangen.
Steuersätze ohne
Auswertungspositionen
Wenn man die Umsatzsteuervoranmeldung in Referenz-ERP bzw.
die Übertragung via ELSTER verwenden will, so müssen den Steuersätzen gültige
Kennzahlen zugewiesen ein. Es werden hier alle Steuersätze aufgelistet, bei
denen ein Prozentsatz ungleich 0 eingetragen ist, jedoch keine Kennzeichen für
die Umsatzsteuervoranmeldung.
Doppelte Kontonummern
Kontonummern
müssen eindeutig sein. Dies wird für den Normalfall der manuellen Erfassung von
Sach- bzw. Personenkonten auch abgefangen und kann über die im Mandanten
[...]


---

## Test Zinssaldo

Test Zinssaldo
Hauptmenü
Abschlussarbeiten
Reorganisation
Fibureorganisation
Funktion
Test Zinssaldo
Direktsprung
[FIREO]
Im Test Zinssaldo wird der Saldo der Zinsrechnung mit
den tatsächlichen Daten überprüft. Es wird dabei geprüft, ob der Saldo der sich
aus den Belegen ergeben würde zu dem in der Zinsabrechnung hinterlegten Belegen
passt.

---

## Tourzuordnung in Vorgängen

Tourzuordnung in Vorgängen
Hauptmenü
Nebenbuchhaltungen
Tourverwaltung
Tourzuordnung in Vorgängen
Direktsprung
[DIS]
Automatische und manuelle Zuordnung von Vorgängen zu
Touren.
Es gibt in dieser Auswahlliste zwei Varianten; eine
zeigt die Vorgänge mit Tourzuordnung die andere die ohne Tourzuordnung.

---

## Umbuchungen bei Wechsel der Forderungsgruppe

Umbuchungen bei Wechsel der
Forderungsgruppe
Man hat die Möglichkeit für Personenkonten die
Forderungsgruppe zu wechseln. Wenn man dies macht, ergibt sich das Problem, dass
auf den „alten“ Forderungs-/Verbindlichkeitskonten Beträge stehen, die aber ab
dem Zeitpunkt des Wechsels auf die „neuen“ Forderungs-/Verbindlichkeitskonten
gehören würden:
Personenkonto
„altes“
Forderungskonto
„neues“ Forderungskonto
Eröffnung
10.000,00
10.000,00
0,00
Bewegungen laufendes
      Jahr
2.000,00
2.000,00
0,00
Ab
      Periode x des laufenden Jahres wird im Personenkonto eine neue
      Forderungsgruppe und somit ein neues Forderungskonto
      eingetragen.
Bewegungen ab Periode x
295,00
0,00
295,00
Saldo der einzelnen
      Konten
12.295,00
12.000,00
295,00
Beim
      Jahreswechsel wird jedoch, genau wie in den Normalperioden, der Saldo des
      Forderungskontos aus den Buchungen des Personenkontos in der
      Abschlussperiode gebildet. Dieser Buchung kann nur
einem
Forderungskonto zugewiesen werden:
Jahreswechsel
12.295,00
0
12.295,00
Das
      ist auch richtig, denn es fehlt eine Umbuchung vom „alten“ auf das „neue“
      Forderungskonto. Würde man diese Umbuchung weglassen, so würden auf dem
      „alten“ Forderungskonto die Beträge auf alle Ewigkeit stehen bleiben und
      das „neue“ Forderungskonto hätte irgendwann einen negativen Saldo.
Also
      erfolgt bei Jahreswechsel automatisch eine Umbuchung in der letzten
      Normalperiode. Es wird hier empfohlen – genau wie für den automatischen
      Abschluss von Unterkonten auf ihre Hauptkonten - eine 13. Normalperiode
      einzurichten
Umbuchung
-12.000,00
12.000,00
Saldo der einzelnen
      Konten
12.295,00
12.000,00
295,00
Umbuchung + Saldo
12.295,00
0,00
12.295,00
Soll
      beim Jahreswechsel diese automatische Umbuchung nicht durchgeführt werden,
      so kann man mit Hilfe des Steuerungsparameters 968 „Forderungskonten
      umbuchen“ dieses Verhalten abschalten.

---

## Umsatzsteuervoranmeldung

Umsatzsteuervoranmeldung
Hauptmenü
Abschlussarbeiten
Umsatzsteuer
Umsatzsteuerwerte
Direktsprung
[UVA]
Das Finanz- und Warenwirtschaftssystem Referenz-ERP
unterstützt Sie bei der Erstellung Ihrer Umsatzsteuervoranmeldung mit einem von
der OFD Schleswig-Holstein zugelassenen Vordruck für die
Umsatzsteuervoranmeldung.
Der Zulassungsvermerk wird auf der
Umsatzsteuervoranmeldung nicht mehr mit ausgedruckt, da der offizielle Weg
inzwischen via
Elster
erfolgt.
Dieses Formular bezieht die Daten über die
Steuersätze und die dort eingerichteten Auswertungspositionen. Bevor dieses
Formular gedruckt wird, werden vom System einige Prüfungen durchgeführt, ob
bestimmte Zuordnungen und Einrichtungen fehlerfrei sind. Diese Prüfungen können
Sie auch schon bei der Einrichtung der Stammdaten durchführen. Sie finden diese
Tests unter dem Direktsprung FIREO und dort ist es der Menüpunkt "Test
Stammdaten".
Speziell hierfür sind folgende Einrichtungen
nötig:
Im Mandantenstamm müssen die Felder
Bundesland,
Anschrift Finanzamt, Steuernummer
sowie
Voranmeldezeitraum
eingetragen sein.
Es müssen die
Auswertungspositionen
so eingerichtet sein, dass alle
Kennzahlen vorhanden sind, die für das Unternehmen von Belang sind. In den
Steuersätzen müssen die "Kennzeichen Umsatzsteuer-Voranmeldung" so eingetragen
werden, dass sie die Bemessungsgrundlage bzw. die Steuer auf dem
Umsatzsteuervoranmeldungsvordruck widerspiegeln.
Den Aufruf des Umsatzsteuervoranmeldungsformulars
findet man unter dem Menüpunkt Umsatzsteuerwerte (Direktsprung
[UVA]
). In der Variante „Umsatzsteuer nach
Auswertungspositionen“ werden die Daten mit Zwischensummen ausgegeben. Mit der
Funktion „Einzelpositionen“ werden die Belege angezeigt, die den
Auswertungspositionen zugeordnet sind.  Mit der Funktion
"Druck
Umsatzsteuervoranmeldung"
kann der Report sofort gedruckt werden. Vor dem
Ausdruck kommt noch eine Meldung, in der man aufgefordert wird, die zwei Seiten
zusammenzuheften:
Bekanntermaßen ändert sich der Auf
[...]


---

## Verbuchung

Verbuchung
Da es sich um eine kalkulatorische Umbuchung handelt,
werden oben ermittelte Frachten in der Warenstatistik nicht berücksichtigt.
Allerdings werden sie im Vorgang gespeichert und können von dort ausgewertet
werden. Näheres dazu im Anhang.
Entsprechend der Erlöskennziffernzuordnung in der
Frachttabelle erfolgt eine Verteilung in der Finanzbuchhaltung auf Warenerlös
und Frachten:
Im Gegensatz zur kalkulatorischen Buchung wird bei der
echten Frachtermittlung keine Umbuchung ausgelöst, sondern eine direkte Buchung
gesteuert durch die Erlöskennziffer veranlasst. Auch in der Warenwirtschaft
erfolgt eine Buchung, die in WBA in der Spalte Frachten sichtbar wird.

---

## Verfall / Erledigung eines Wechsels!

Verfall / Erledigung eines Wechsels!
Wie schon bei der Weitergabe eines Besitzwechsels gibt
es auch hier zwei Abwicklungsmöglichkeiten.
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
erfassen, wobei als Gegenkonto das Besitz- bzw. das Schuldwechselkonto angegeben
werden muss. Da diese Konten als Wechselkonto gekennzeichnet sind, werden bei
Eingabe des Gegenkontos die zur Verfall / Erledigung fähigen Wechsel in einem
Auswahlbildschirm aufgelistet.
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
In der Anwendung
Wechsel bearbeiten
kann
der Verfall automatisch gebucht werden. Hierbei geht man wie folgt vor:
Wechsel markieren und
Ändern
F5
. Der
Wechsel wird angezeigt.  Mit
F7
Wechselverfall
und
F9
Start
.
Die Buchung erfolgt mit dem Verfalldatum. Der Wechsel
verschwindet aus der Auswahlliste
"Wechsel
bearbeiten".
Bei diesen Buchungen werden drei Fälle
unterschieden:
Besitzwechsel nicht
weitergegeben:
Bank 10.000,00
an
Besitzwechsel 10.000,00
Besitzwechsel
weitergegeben:
(nur wenn Wechselkonto ungleich Obligokonto)
Besitzwechselobligo 10.000,00
an
Besitz Wechsel  10.000,00
Schuldwechsel:
Schuldwechsel 10.000,00
an
Bank 10.000,00

---

## Verrechnungssammelkonto

Verrechnungssammelkonto
Dieses optionale Konto steuerte eine generelle
Umbuchung über ein zentrales Verrechnungskonto ( Vorkonten werden nicht
berücksichtigt.

---

## Verteilung auf Kassenkonten

Verteilung auf Kassenkonten
Es ist möglich, dass beim Kassenabschluss die Bestände
automatisch auf Kassenkonten verteilt werden können, wenn der entsprechende SPA
gesetzt ist. Die unterschiedliche Kontozuordnung erfolgte bisher in der
Anwendung Kassenkonten. Diese Anwendung ist jetzt redundant, die entsprechende
Information wird jetzt in den Kasseneinstellungen in der Gruppe Konten
hinterlegt. Dabei werden bereits existierende Zuordnungen übernommen.
Vorteil: In Verbindung mit den individuellen
Kasseneinstellungen ist es möglich, dass über die Vorlagemechanik für jede Kasse
ein unterschiedliches Konto hinterlegt werden kann, auf das diese Verteilung
laufen soll.

---

## Vorgänge Finanzbuchhaltung löschen (inkl. 29)

Vorgänge Finanzbuchhaltung löschen (inkl. 29)
Es werden die Daten in folgenden Tabellen
gelöscht:
Datevposition
Datevstamm
fibuvorgposition
fibuvorgpostext
fibuvorgposwabew
vorgfibulink
fibuvorgproto
fibuvorgreserv
fibuvorgstamm
FIBUVORGDELPROTO
RFSDTALAUF
RFSZAHLUNG
journal
journalfreigabe
journalposition
Kontosummen
Kontozaehler
KostStelSummen
KOSTENTRAEGERSUMMEN
KOSTENSUMMEN
SteuersatzSummen
Zahlungslauf
Zahlungsbeleg
Zahlungsposition
Zahlvorschlag
Zahlvorschliste
zahlvorschlposit
ZAHLVORSCHPROTOKOLL
MahnPosition
Mahnung
mahnvorschlag
mahnvorschliste
mahnvorschposit
zinsabrechnung
zinsabrposition
zinsliste
offenerposten
wechselabrechnung
wechselabrposit
wechselstamm
wechselprolong
kontoblattstamm
kontoblattposit
kontoblattzaehl
fibuwiedzahlung
FibuWiedZahlPosition
EINGANGSMAPPELEM unter der Bedingung: where
EinMappTyp=1
FIBUVORGUNGEBU
FIBUVORGKOSTSTEL
FIBUVORGKOSTENTRAEGER
AMIC_DTAUS_ASATZ
AMIC_DTAUS_CSATZ
DTADISKHEADER
DTADISKPOSITION unter der Bedingung: where 1=1
DTADISKPOSTEXT unter der Bedingung: where 1=1
DTADISKVERTEIL
EBILANZ_GAAP_RESULT_HEADER unter der Bedingung: where
1=1
FIBUVORGEXPORT
OPAUSLAND
OPAUSLANDSTAT
fibumailversand
meinfibumailversand
fibuwaehrsumme
Es werden die Daten in folgenden Tabellen
aktualisiert:
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'ZAHLUNGSLAUF'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'MAHNVORSCHLISTE'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'ZINSLISTE'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'ZAHLVORSCHLISTE'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'MAHNUNG'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'WECHSELSTAMM'
ident mit Aktualisierung: set identident = 1 unter der
Bedingung: where identcolumnname = 'WECHSELABRECHNUNG'
id
[...]


---

## Vorgänge mittels JPP-Objekten steuern

Vorgänge mittels JPP-Objekten steuern
Um Vorgänge aus einem externen VBScript bearbeiten zu
können werden diverse JPP-Objekte die das  Referenz-ERP-System für
unterschiedliche Anforderungen zur Verfügung stellt verwendet.
•
CVORGANGSHELPER - Vorgangsbearbeitung
•
JVARS - Globales Datenmanagement
•
JDBX - Datenbankabfragen

---

## Warenrückvergütungsbuchungen

Warenrückvergütungsbuchungen
Die in der obigen Anwendung erstellten Umsatzdaten
können mit dieser Anwendung in Buchungssätze verarbeitet werden. Es steht die
Möglichkeit zur Verfügung, zunächst einen oder mehrere Probeläufe durchzuführen,
um das Ergebnis in der Auswahlliste zu überprüfen.
Zum Abschluss muss dann der Schalter Echt lauf auf Ja
gesetzt werden, um die "echten"  Buchungen in die Importschnittstelle der
Finanzbuchhaltung einzustellen.

---

## Warenrückvergütung

Warenrückvergütung
Dieser Bereich erlaubt es, aus den Warenbewegungen des
abgeschlossenen Wirtschaftsjahres eine Tabelle zu erstellen, die die Bewegungen
innerhalb der Mitgliederkonten darstellt.
Solange noch keine Buchung der Warenrückvergütungen
des zu bearbeitenden Jahres in der Finanzbuchhaltung erfolgt ist kann der Punkt
Daten zusammenstellen jederzeit angewählt werden. Die Perioden des Jahres müssen
zur endgültigen Ermittlung abgeschlossen sein, ansonsten erfolgt eine
Warnmeldung.
Das  Abgrenzungsdatum dient zur Ermittlung der zu
berücksichtigen Mitglieder. Wurden Anteile erstmals  nach dem eingegebenen
Abgrenzungsdatum gezeichnet oder übertragen, wird dieses Mitgliedskonto nicht
berücksichtigt. Vorbelegung ist der 31.12. des angegebenen Jahres.
Das Ergebnis der Datenzusammenstellung wird in der
Auswahlliste dargestellt.

---

## weitere Funktionen der Tresenkasse

weitere Funktionen der
Tresenkasse
Lagerabholschein, Kasse
Es ist auch möglich, an der Tresenkasse Artikel als
Lagerartikel zu kennzeichnen, für die dann beim Belegabschluss ein extra Beleg
gedruckt wird, wenn hierfür in den Vorgangsdruckklassen der Druck dieses
Extra-Beleges definiert ist. In den Vorgangsdruckklassen gibt es extra die
Effektsteuerung Lagerabholschein, was bewirkt, dass dieses Formular nur dann
gedruckt wird, wenn es unter den Artikeln mindestens einen Artikel gibt, der als
Lagerartikel gekennzeichnet ist.
Einen Artikel kann man dann solange als Lagerartikel
kennzeichnen (
F9
), wie die zugehörige Position nicht abgeschlossen ist.
Standardmäßig wird die Voreinstellung aus dem Artikel übernommen. Die Funktion
bewirkt nur eine Änderung des Artikelstatus während der Erfassung, wenn der
Status 0 (kein Abholschein / änderbar) bzw. 1 (Abholschein / änderbar) ist.
Ansonsten wird die Vorbelegung aus dem Artikel strikt übernommen
Diese Änderung wird dann auch auf der Maske angezeigt
und ist nur bis zur Erfassung des nächsten Artikels gültig.
Auf der Artikelschnellerfassungsmaske sind dieselben
Funktionen vorhanden wie auf der normalen Positionsteilmaske. Beim Zeilen-Rabatt
bzw. beim Zeilen Zu-Abschlag ist die Erfassungsmöglichkeit des Rabatts
reduziert. Außerdem ex. die Funktion F9 der Lagerausgabe, um auch auf der
Artikelschnellerfassungsmaske Artikel zur Erfassungszeit nachträglich als
Lagerartikel zu kennzeichnen. Korrektur und Löschen von bereits erfassten
Positionen ist bei der Tresenkasse erlaubt, da der Druck erst beim Abschluss des
Vorgangs erfolgt.

---

## Weitere Stichworte

Weitere Stichworte
Produktionsbewertung
Bewertung von Umbuchungen
Periodenabschluss
WAREO
Bewertung der Inventur
Behandlung von Dienstleistungsartikeln in
Bestandsbewertung und Inventur:
Empfohlene Variante1: Bewertungsgruppe=ohne Bewertung.
Mengenmäßig läuft Artikel ins Minus, Bestandsbewertung ist stets 0. Bei Inventur
wird Menge auf 0 ausgeglichen. In Periodenerfolgsauswertung laufen Umsätze auf
-> 100% Rohgewinn.
Empfohlene Variante2: Bewertung über zu pflegenden
EK-Listenpreis, der kalkulatorische Bewertung der Leistung enthält. Bestand
läuft auch wertmäßig ins Minus, bei Inventur wird Menge und damit auch der Wert
auf 0 gebracht. Inventur weist somit eine Differenz aus, die aber nicht wie
Handelsware in der Fibu gebucht wird. Tipp: Gesonderte Inventurgruppe für
Dienstleistungsartikel. Periodenerfolgsauswertung gleicht Umsätze mit der
kalkulatorischen Bewertung ab, Rohgewinn also Umsatz – kalk. Bewertung.
Variante 1b/2b: Dienstleistung als Wertartikel.
Dynamik der Bestandführung und –bewertung:
abgeschlossene Buchungsperioden

---

## Zahlungsarten

Zahlungsarten
Zahlungsarten
1
Bargeld in Kassenwährung
2
Scheck
3
Gutschein
4
EC-Karte
5
Bankeinzug
10
Rückgeld
11
Skonto
12
Bargeld in Fremdwährung

---

## Zahlungsbedingungen ohne Umbuchung

Zahlungsbedingungen ohne Umbuchung
Der Vorkontenmechanismus wird für die hier
eingegrenzten Zahlungsbedingungen deaktiviert. ( RFS-Vorkonten werden bei den
Aeins Zahlungsbedingen eingepflegt) .

---

## Zahlungsformulare

Zahlungsformulare
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Zahlungsformulare
Direktsprung
[FIZAF]
.
Je Formularklasse – Zahlungsausgang oder
Zahlungseingang – und Bank kann es unterschiedliche Formulare geben, wenn z.B.
die Banken unterschiedliche Ansprüche stellen. Hier wird nun die Verbindung
zwischen der Formularklasse, der Formulareinrichtung und der Bank
hergestellt.
Beschreibung
Bank
Erfassung der Bank, für die das
      Formular bestimmt ist. Es kann hier direkt die Bezeichnung oder die
      Bankleitzahl erfasst werden. Bei der Freigabe der
Zahlungsvorschläge
wird die
      Hausbank abgefragt. Die dort eingetragene Bank bestimmt dann das Formular.
      Sind mehreren Formulare eingerichtet, werden diese dort noch einmal
      abgefragt.
Formularklasse
Zahlungseingang oder
      Zahlungsausgang.
Nummer
Laufende Nummer des Formulars in der
      Klasse. Man kann also pro Bank mehrere Formulare hinterlegen, falls dies
      nötig ist.
Formularnummer
Das
      Formular, das ausgedruckt werden soll. Die Gestaltung des Formulars
      erfolgt im Formulareinrichter und muss vor dieser Einrichtung geschehen.
      Hier können Formulare des Typs Scheck (Formulartyp 201) hinterlegt
      werden.
Bezeichnung
Allgemeine Bezeichnung für dieses
      Formular.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.

---

## Zahlungssätze zu Kassenbelegen weichen ab

Zahlungssätze zu Kassenbelegen weichen ab
Zu jedem Kassenbeleg (AcashBelg) können mehrere
Zahlungssätze (AcashBelgZhlg) existieren, etwa wenn Skonto gewährt wurde oder
Rückgeld ausgezahlt wird. Die Daten sind nicht stimmig, wenn Zahlungssätze zu
Belegen fehlen oder umgekehrt es zu Zahlungssätzen keine Belege gibt oder aber
in Zahlungssätzen und Belegen unstimmige Beträge gespeichert sind.
Zur Bereinigung gibt es keine maschinelle
Unterstützung. Nachfolgende SQL Ausdrücke helfen, Fehlern auf die Spur zu
kommen. Fehler werden individuell berichtigt.
Fehlende oder abweichende Zahlungen zu Belegen:
select
(select sum( zahlbetrag) from acashbelgzhlg z1
where z1.zahlks=belegks and
      z1.zahlbelegid=belegid
and
      z1.filialnummer=a.filialnummer and zahlart in (1,2,3,4,5,12)) gegeben,
(select sum( zahlbetrag) from acashbelgzhlg z2
where z2.zahlks=belegks and z2.zahlbelegid=belegid
and
      z2.filialnummer=a.filialnummer and zahlart=10) zurueck,
(select sum( zahlbetrag) from acashbelgzhlg z3
where z3.zahlks=belegks and z3.zahlbelegid=belegid
and
      z3.filialnummer=a.filialnummer and zahlart=11) skonto,
isnull(gegeben,0) - isnull(zurueck,0)  as
      Betrag,
if (gegeben is
      null and zurueck is null and belegsummebrutto != 0) then 'fehlt'
else if
      abs(belegsummebrutto) != abs(Betrag) then 'abweichend' else '' endif endif
      watdenn,
BelegKs,
      BelegKsi,
cast(BelegDatum
      as date) Belegdatumdatum, BelegNr,
(select
      FormLstBezeich from Formatlist
where FormLstKennung = 'AcashBelegAr' and FormLstWert = Belegart
and SprachNummer = 0) BelegArtBez,
Belegart,
BelegSummeBrutto, BelegKunde
from AcashBelg a
where watdenn != ''
order by
      a.FilialNummer, a.BelegKs, a.BelegKsi, a.Belegart,
      a.Belegdatum
Fehlende Belege zu Zahlungssätzen:
select
ZahlKs, ZahlKsi,
today(*)
      Belegdatumdatum, ZahlBelegNr,
(select
      FormLstBezeich from Formatlist
where FormLstKennung = 'AcashBelegAr' and FormLstWert = zahlBelegart
and Sp
[...]


---

## Zahlungsverkehr: Übernahme in die Primanota

Zahlungsverkehr: Übernahme in die
Primanota
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Übernahme in die Primanota
Direktsprung
[ZHB]
Die Buchungssätze für Zahlungsbelege werden erstellt.
Dabei werden die angesprochenen offenen Posten mit dem neu erstellten Beleg
ausgeziffert. Die Funktion „
Buchen mit Kursdifferenz
“
F8
erzeugt genau wie der Menüpunkt „
Starten
“
F9
die
Buchungssätze, nur werden hier die Kursdifferenzen für Belege in Fremdwährung
errechnet und ausgewiesen.
Vor dem Erstellen der Belege müssen noch ein paar
Angaben gemacht werden:
Wenn nicht in der Systemeinstellung (Direktsprung
[NKF]
) vorgesehen und vorgeschlagen,
kann hier ein
Belegnummernkreis
angegeben werden, über den die Verwaltung
der Belege erfolgen soll. Hat man den Einrichterparametern „Nummernkreis der
Hausbank verwenden“ aktiviert, werden diese Felder ausgeblendet und der in der
Hausbank unter „
Nummernkreis autom. Zahlungsverkehr
“
eingetragene
Nummernkreis wird verwendet. Ist die Option „Schecknummer als Belegnummer
vergeben“ gesetzt und eine Schecknummer vergeben, dann wird nach wie vor die
Schecknummer verwendet.
Das
Belegdatum
und das
Valutadatum
für
den Zahlungsbeleg werden hier als erstes abgefragt. Sie werden mit dem Datum der
zuerst in der Auswahl markierten Zahlung vorbelegt. Mit dem Einrichterparameter
„Vorbelegung des Belegdatums mit dem Tagesdatum?“ kann das Verhalten so geändert
werden, dass diese Felder mit dem Tagesdatum vorbelegt werden wird. Anschließend
kann man noch einige Einstellungen vornehmen.
Sammelbuchung:
Es wird pro Zahlung ein
Zahlungsbeleg erstellt oder, wenn der Haken gesetzt ist, pro im Hausbankenstamm
hinterlegtem Konto ein Zahlungsbeleg.
Buchen ungedruckter Zahlungen:
Normalerweise sollten Zahlungen erst dann in die Primanota übernommen
werden, wenn sie auch verarbeitet worden sind. Ist es aus betrieblichen Gründen
nun nötig, unverarbeitete Zahlungen bereits in die Primanota zu übernehmen, so
lässt sich d
[...]


---

## Zahlungsvorschläge in der OP-Verwaltung bearbeiten

Zahlungsvorschläge in der OP-Verwaltung bearbeiten
Hauptmenü
OP-Verwaltung
OP-Bearbeitung
OP-Verwaltung
Direktsprung
[OPV]
Zahlungsvorschläge können in der OP-Verwaltung
bearbeitet werden. Dazu muss der oder die offenen Posten markiert werden. Danach
kann mit der Funktion
hinzu/löschen Zahlvorsch
Strg+F5
der
OP zum Zahlungsvorschlag hinzugefügt werden bzw., wenn er bereits in einer Liste
enthalten ist, daraus gelöscht werden. Dabei wird das im Kundenstamm hinterlegte
Verrechnungskennzeichen berücksichtigt. Ändert sich durch Löschen oder
Hinzufügen eines OPs in eine Zahlungsvorschlagsliste das Vorzeichen, so werden
alle OPs dieses Kunden aus dem Zahlungsvorschlag entfernt, damit nicht ungewollt
aus einem Zahlungsausgang ein Zahlungseingang wird (oder umgekehrt).
Beim Ändern des Skontos mit der Funktion
Ändern
F5
wird auch der in der Zahlungsvorschlagsliste hinterlegte
Skonto geändert.
Werden OPs, die in einer Zahlungsvorschlagsliste
stehen, ausgeziffert, so werden sie automatisch aus der Liste gelöscht.

---

## Zahlungsvorschläge erstellen

Zahlungsvorschläge erstellen
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungsvorschläge erstellen
Direktsprung
[ZHVE]
Der Ablauf zum Erstellen und Bearbeiten der
Zahlungsvorschläge wurde überarbeitet. Die Auswahlmöglichkeit „Zahlungsausgang
SEPA“ und Zahlungseingang SEPA“ sind entfallen. SEPA Zahlungen werden auch über
Regulierungsart „Zahlungsausgang“  bzw. „Zahlungseingang“ abgewickelt. Die
Prüfungen der Bankverbindungen führen jetzt nicht mehr dazu, dass der
Zahlungsvorschlag für dieses Konto nicht erstellt wird. Stattdessen werden die
Problemfälle in der Zahlungsvorschlagsliste angezeigt und man hat die
Möglichkeit diese Daten direkt hier zu korrigieren. Erst bei der
Freigabe
der Zahlungsvorschläge werden die Daten entsprechend den Einstellungen noch
einmal geprüft und ggf. abgewiesen.
Nach Anwahl des Programmpunktes wird sofort in einen
Bildschirm verzweigt, auf dem verschiedene Werte abgefragt werden:
Über die Einstellung
Regulierung
kann man
bestimmen, ob Zahlungsausgang oder -eingang behandelt werden soll. Debitorische
und Kreditorische Fragen werden hierbei nicht abgegrenzt.
Zahlungsausgang
Ausland wird wie Zahlungsausgang behandelt, jedoch werden hier nur OPs
herangezogen, die für den Auslandszahlungsverkehr gekennzeichnet sind. Genauere
Hinweise befinden sich im Teil
Auslandszahlungsverkehr
.
Der
Zahlstichtag
steuert zusammen mit dem
nächsten Stichtag
, welche Belege vorgeschlagen werden. Dabei ist der
nächste Stichtag
das Datum, welches zusammen mit den Bankarbeitstagen aus
den Epas bestimmt, wann Belege gezogen werden. Es werden die Belege gezogen,
deren Valuta- bzw. Skontodatum
vor
dem
nächsten Stichtag
(plus Bankarbeitstage. Siehe unten) liegt.
Ist im Feld
Skonto berücksichtigen
der
Wert „OPs nur laut Valuta heranziehen“ eingetragen, so wird die Skontofrist
nicht berücksichtigt, d.h. das Skonto-Datum wird für die Auswahl ignoriert.
Sollte die Skontofrist für die so ausgewählten OPs nicht abgelaufen sein, so
wird trotzdem Sk
[...]


---

## Zeilendefinition

Zeilendefinition
Hauptmenü
Abschlussarbeiten
Chefcockpit
Chefcockpit-Designer
Definitionstyp
Zeilendefinition
Direktsprung
[CCD]
In der Zeilendefinition wird auf Grundlage der
Spaltendefinition der Inhalt der Zelle festgelegt. Die Spaltendefinition wird
vorgegeben, so dass man nur noch für die einzelnen Spalten die Werte eintragen
muss.
Die Eingabefelder
Davor neue Seite
,
Zeile hervorheben
und
In Graphik auswerten
sowie
Schriftart
und
Schrift-/Hintergrundfarbe
dienen zur
optischen Abgrenzung im mitgelieferten Crystal Report (siehe auch Dokumentation
Überschriftzeile
).
Konstante
Als Konstanten sind nur numerische Werte zugelassen.
Diese werden mit vier Nachkommastellen gespeichert. Die Standard-Auswertung ist
so gebaut, dass alle Werte mit zwei Nachkommastellen ausgegeben
werden
Formel
Der in den Formeln verwendetet Syntax entspricht dem
SQL-Syntax. Im Prinzip wir nichts weiter gemacht als
Set Ergebnis =(
FORMEL
)
Innerhalb der Formel kann man auf Kontenlisten und
Ergebnisse aus anderen Formeln zugreifen. Dazu verwendet man die Abkürzung mit
einem ‚#‘ vorneweg. Bei den Formelergebnissen ist darauf zu achten, dass die
Formeln in der Reihenfolge der Sortierung ausgewertet werden und auch erst dann
zur Verfügung stehen. Auf dem Formelfeld kann man mit
F3
sich die Kürzel
heraussuchen. Sie werden dann an der Stelle, an dem die Schreibmarke gerade
steht, eingefügt.
Wie würde man nun z.B. die Umsatzrentabilität, die
sich aus
Betriebsergebnis *100 / Gesamtleistung
ergibt, als Formel
schreiben? Man erstellt sich zwei Kontendefinition BERG für Betriebsergebnis und
GL für Gesamtleistung. Die Formel sieht dann wie folgt aus
: #BERG * 100 /
# GL
Es ist auch möglich, innerhalb einer Formel auf
Spaltenergebnisse derselben Zeile zuzugreifen. Dies ist z.B. dann nötig, wenn
man eine prozentuelle Abweichung errechnen möchte. Es steht dafür eine Funktion
KZA_GET(Spaltennummer) zur Verfügung. Die Spaltennummer beginnt bei 1. Zu
beachten ist grundsätzlich, dass die
[...]


---

## Zinsmerkmale im Sachkontenstamm

Zinsmerkmale im
Sachkontenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Register „Weitere Optionen“
Direktsprung
[SKS]
Im Sachkontenstamm gibt es " auf dem Register
"Weitere Optionen" in dem Bereich "Sonstige Kennzeichen" das Feld Zinskonto.
Wird dieses auf "JA" gestellt, werden die Felder, in denen die Zinsgruppe und
der Sockelbetrag eingegeben werden können, freigeschaltet.

---

## Zinswesen

Zinswesen
Die Referenz-ERP Fibu ermöglicht es, für folgende 3 Bereiche
automatische Zinsen errechnen zu lassen:
•
Kontokorrentzinsen, Sachkontenzinsen
•
Mahnzinsen
•
Wechseldiskontierung
Die vorliegende Beschreibung beschäftigt sich
ausschließlich mit den Kontokorrentzinsen. Die Handhabung der Mahnzinsen wird im
Kapitel Mahnen beschrieben. Bitte beachten Sie, dass ein Mixen von Kontokorrent-
und Mahnzinsen für einen Kunden unsinnig ist.
Die wesentlichen Leistungsmerkmale des
Kontokorrentzinsmoduls, die nachfolgen ausführlich dargestellt werden, sind:
•
Differenzierung der Konten durch Zinsgruppen
•
Wechsel der Zinssätze im Abrechnungszeitraum möglich
•
Zinsvorschlagsliste
•
Korrektur oder Löschung bzw. zurücksetzen von Zinsen
•
Wiederholbarkeit von Zinsläufen
•
Druck von Zinsabrechnungen über variable Formulareinrichtung
•
automatisches Buchen der Zinsen oder Buchen manuell markierter Zinsen
•
Zinsabschlagsteuer und Solidaritätszuschlag automatisch verbuchen
•
Archivierung der Zinsen
Zu den Stammdaten der Zinsen zählen die Zinsgruppe,
die Stammdaten für die Zinsabschlagsteuer sowie einer Reihe von Feldern im
Kundenstamm und Mandantenstamm.

---

## Zugangslager bei Umbuchungen

Zugangslager bei Umbuchungen
Kann die Lagernummer nicht ermittelt werden, wird sie
mit 0 belegt. Eine Validierung findet nicht statt.
(Positionsparameter: LGUMB_SAx)

---

## Zukünftiges Verfahren ab Referenz-ERP 7.0

Zukünftiges Verfahren ab Referenz-ERP 7.0
Also wird das Kassensystem zukünftig interne Belege
erzeugen, die wie bisher für die Zahlungsmittel bereits in Verwendung
„Automatische Einreichung“ heißen werden. Die Belege werden so aufgebaut, wie
sie für die Fibu erforderlich sind.
Mit der Umstellung der Referenz-ERP Version werden per
Umstellprogramm für zurückliegende Sitzungen diese automatischen Belege für die
Bargeldumbuchungen nachgetragen. Die automatischen Einreichungen für
Zahlungsmittel bleiben so wie sie sind. Damit kann die Abstimmung Kasse – Fibu
auch für frühere Kassendaten durchgeführt werden.
Ferner wird eine weitere Steuerung eingebaut: Es wird
ermöglicht, mit dem Kassenabschluss auch direkt eine Einreichung des ganzen
Bargeldbestands vorzunehmen. Die Einreichung erfolgt dann bei der im Kassenstamm
hinterlegten Hausbank. Zur Verwendung dieser Methode muss ein SPA freigeschaltet
werden.
Automatische Einreichung sorgt implizit auch weiterhin
dafür, dass mit dem Kassenabschluss der Kassensturz als Bargeld an
Differenzkonto gebucht wird. Ohne SPA zami automatisch besteht bei Erfassung des
Kassensturzes die Entscheidungsmöglichkeit, ob die Differenz auch tatsächlich
gebucht werden soll. Der Kassensturz könnte so nur von informatorischem
Charakter sein.
News: EPA „VortragEinreichen“ im Kassenabschluss sorgt
dafür, dass eine Abfrage erscheint, nach deren Quittung man auch eventuelle
Vorträge (und nicht nur die Umsätze der aktuellen Sitzung) einreichen kann.

---

## Zwischenkonto

Zwischenkonto
Achtung: bei gesetzter Option : Anschluss Fibu
Muss hier ein Bilanzkonto aus der
Aeins-Fibu
hinterlegt werden; es wird als Gegenkonto für externe Zahlungsvorgänge
benötigt!

---

