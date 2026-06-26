# eRechnung, EDI & Schnittstellen — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (438 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Anwendung

Anwendung
Gelesene Dateien werden zunächst serialisiert in den
Typ „Branchen-ERP.ProduktionsInterface.Produktion“ und dann an die Methode
„VerarbeiteRueckMeldung“ der Klasse „ProduktionsAenderung“ übergeben.
XmlSerializer ser;
StreamReader reader =
null
;
Produktion prod =
null
;
Encoding enc = Encoding.GetEncoding(
"ISO-8859-1"
);
try
{
reader =
new
StreamReader(filename);
ser =
new
XmlSerializerFactory().CreateSerializer(
typeof
(Produktion));
prod  =
(Produktion)ser.Deserialize(reader);
reader.Close();
}
finally
{
if
(reader !=
null
)
{
reader.Close();
}
}
//Nur weiter, wenn eine
Produktionsänderung erkannt wurde
if
(prod ==
null
)
{
return
;
}
int
bedienerMand =
D.GetExecuteScalar<
int
>(-1,
"select bedienerid from bedienerstamm where BedienerKurz
= 'MAND'"
);
ProduktionsAenderung pa =
new
ProduktionsAenderung();
pa.VerarbeiteRueckMeldung(prod,
bedienerMand);
Zu Exportierende Daten werden zunächst serialisiert
und dann in eine Datei geschrieben
ProduktionsExport pe = new
ProduktionsExport();
Produktion prod = pe.ExportData(v_id,
ProdStatus.Rezept);
XmlSerializer ser;
XmlTextWriter xmlTextWriter = null;
string XML = "";
MemoryStream ms = null;
Encoding enc = Encoding.GetEncoding("ISO-8859-1");
try
{
ms = new MemoryStream();
xmlTextWriter = new XmlTextWriter(ms, enc);
ser = new
XmlSerializerFactory().CreateSerializer(typeof(Produktion));
ser.Serialize(xmlTextWriter, prod);
//Memorystream füllen
ms = (MemoryStream)xmlTextWriter.BaseStream;
//XML als String ermitteln
ms.Seek(0, SeekOrigin.Begin);
XML = enc.GetString(ms.ToArray());
}
finally
{
if (ms != null)
{
ms.Close();
}
}
///Es muss ein XML geschrieben worden sein
if (string.IsNullOrEmpty(XML))
{
return;
}
//String wegschreiben.
StreamWriter sw = null;
try
{
sw = new StreamWriter(Path.Combine(exportPfad,
"parts_"+v_id.ToString()+".xml"), false,
Encoding.GetEncoding("ISO-8859-1"));
sw.Write(XML);
sw.Flush();
}
finally
{
if (sw != null)
{
sw.Flush();
sw.Close();
}
}

---

## Schema

Schema
Die Struktur des XML beschreibt das nachfolgende
Schema:
<?xml version="1.0"
encoding="utf-8"?>
<xs:schema elementFormDefault="qualified"
xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:import
namespace="http://microsoft.com/wsdl/types/" />
<xs:element name="Produktion" nillable="true"
type="Produktion" />
<xs:complexType name="Produktion">
<xs:complexContent
mixed="false">
<xs:extension
base="ClassExtender">
<xs:sequence>
<xs:element minOccurs="0" maxOccurs="1" name="Produkte" type="ArrayOfProdukt"
/>
<xs:element minOccurs="0" maxOccurs="1" name="Komponenten"
type="ArrayOfKomponente" />
<xs:element minOccurs="1" maxOccurs="1" name="ProduktionsNummer"
type="xs:int" />
<xs:element minOccurs="1" maxOccurs="1" name="Jahrnummer" type="xs:int"
/>
<xs:element minOccurs="1" maxOccurs="1" name="VorgangsKlasse" type="xs:int"
/>
<xs:element minOccurs="1" maxOccurs="1" name="VorgangsUnterKlasse"
type="xs:int" />
<xs:element minOccurs="1" maxOccurs="1" name="VorgangsGuid"
xmlns:q1="http://microsoft.com/wsdl/types/" type="q1:guid" />
<xs:element minOccurs="1" maxOccurs="1" name="PositionsGuid"
xmlns:q2="http://microsoft.com/wsdl/types/" type="q2:guid" />
<xs:element minOccurs="1" maxOccurs="1" name="Status" type="xs:int" />
<xs:element minOccurs="0" maxOccurs="1" name="Command" type="xs:string"
/>
<xs:element minOccurs="0" maxOccurs="1" name="Linie" type="xs:string"
/>
<xs:element minOccurs="0" maxOccurs="1" name="Produktionstyp"
type="xs:string" />
<xs:element minOccurs="0" maxOccurs="1" name="Kundenauftragsnummer"
type="xs:string" />
<xs:element minOccurs="0" maxOccurs="1" name="Ladetraeger"
type="ArrayOfLadetraeger" />
</xs:sequence>
</xs:extension>
</xs:complexContent>
</xs:complexType>
<xs:complexType name="ClassExtender"
/>
<xs:complexType name="Ladetraeger">
<xs:complexContent
mixed="false">
<xs:extension
base="ClassExtender">
<xs:sequence>
<xs:element minOccurs="0" maxOccurs="1" name="NVE" type="xs:string" />
<xs:element minOccurs="1" maxOc
[...]


---

## Kommandos

Kommandos
Das XML kennt folgende Kommandos im „COMMAND“-Tag:
COMMAND
Kommando
Richtung
LVS
Bedeutung
BEGIN
IN
      Referenz-ERP
Nein
Hier
      wird in die Tabelle „
ProduktionsInfo“
die Linne eingetragen,
      auf der diese Produktion jetzt laufen soll. In die Tabelle
„ProduktionsInfo“
wird
      eingetragen, in welchem Status sich die Produktion befindet.
MATERIAL
IN
      Referenz-ERP
Ja
Hier
      wird von der Produktion Material als Fertigware an das LVS gemeldet. Der
      angegebene Ladeträger wird in der Lokalität der Fertigware der angegebenen
      Linie mit Hilfe eines Vorgangsimports (LVS) erzeugt.
END
IN
      Referenz-ERP
Nein
Mit
      den Verbrauchsdaten und den Produktionsdaten wird die Produktion in Referenz-ERP
      korrigiert.
MATERIALREQUEST
IN
      Referenz-ERP
Ja
Hier
      wird eine Materialanforderung gegeben. Diese kann, muss aber nicht einer
      Produktion zugeordnet sein. Wichtig ist die Angabe der Linie, da diese im
      LVS die Bereitstellungszone bestimmt.
Die
      Materialanforderung wird in die LVS_Materialorder geschrieben
PARTS
AUS
      Referenz-ERP
NEIN
Dies
      ist die Stückliste der Produktion

---

## Produktions-Interface

Produktions-Interface
Es gibt für die Kommunikation mit Produktionssystemen
eine XML-Dateiaustausch-basierende Schnittstelle.
Diese erledigt verschiedene Aufgaben:
6.
Übertragung der Produktionsdaten an das Produktionssystem
Hier wird die
Komponentenliste mit den Mengen an die Produktion übertragen.
7.
Empfang von Materialbedarf
In Referenz-ERP wird eine
Materialorder erstellt.
8.
Empfang von Ware-Fertig-Meldungen
Hier werden in Referenz-ERP
Ladeträger an der Fertigstellungslokalität der Linie erstellt und beladen.
(siehe auch
[PRODL]
)
9.
Empfang von Verbrauchsmeldungen
Hier wird die verbrauchte
Menge vom Ladeträger in der Bereitstellungszone abgebucht. (siehe auch
[PRODL])
10.
Empfang von Fertigmeldung einer Produktion. Hier werden die Verbräuche und die
Produktmenge in der Produktion korrigiert.
Mit Hilfe von Makro 2.0 kann man in C# bequem ein
Makro erstellen, dass die Dateien z.B. im Rahmen eines Mandantenserverprozesses
erstellt bzw. einliest. Um Pfade in Test- und Livesystem pflegen zu können,
empfehlen wir dazu die
Mandantenprofile
zu verwenden.

---

## eRechnung

eRechnung
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Hauptmenü Direktsprung
[XRE]
Das Modul Referenz-ERP.® eRechnung basiert auf dem
gesetzlich vorgeschriebenen XRechnung-Standard, der den strukturierten,
elektronischen Austausch von Rechnungsdaten ermöglicht.
Die eRechnung ermöglicht die automatische Erstellung
und Vorverarbeitung von B2B-Rechnungen, was Ihre Durchlaufzeiten optimiert, die
Effizienz steigert und Fehler reduziert.
Dabei werden die gesetzlichen
Anforderungen aus der
EN16931
berücksichtigt.
.
Dabei wird folgendes Format unterstützt für Export und
Import:
è
UBL-XML
- Dateien – Universal Business
Language. Entwickelt von OASIS (Organization for the Advancement of Structured
Information Standards), ist ein auf XML basierender Standard für den Austausch
von elektronischen Dokumenten wie Rechnungen, Bestellungen und
Lieferscheinen.
Für den Import wird dazu das folgende Format
unterstützt:
è
ZUGFeRD
Zentraler User Guide des Forums
elektronische Rechnung Deutschland, das gemäß der Richtlinie EU/2014/55 und des
Standards EN16931 UN/CEFACT-
XML
in
PDF
/A-3-Dateien einbettet.
Überblick eRechnung-Modulpakete
Die folgenden Modulpaketen der eRechnung stehen Ihnen
bei Lizenzierung zur Verfügung:
Sie möchten Ihren eingehende
eBelege automatisiert weiterverarbeiten und Ihre Geschäftsprozesse
verschlanken?
Mit dem Komplettpaket bieten wir Ihnen auf Ihre
Geschäftsprozesse zugeschnittene Lösungen.

---

## WARNINGFUNCTION

WARNINGFUNCTION
Mit „Warningfunction“ ist ein individuell designbares
System entstanden, welches es ermöglicht auf der
neuen Auswahlliste
ein Symbol im Hintergrund
einzublenden, wenn gewisse Bedingungen erfüllt sind. Hier soll eine
Beispieleinrichtung dargestellt werden.
Einstufige-Version
Man kann eine Prüffunktion direkt an eine Auswahlliste
hängen. Dies ermöglicht das direkte Abprüfen eines Kriteriums.
Vorteile:
•
einfache Anbindung
•
schnelle Konsistenzprüfung (bei jedem Refresh der Auswahlliste)
Workflow:
•
Warnsymbol erscheint im Hintergrund.
•
Fehler erkennen und beheben.
•
Danach verschwindet das Warnsymbol mit dem nächsten Aktualisieren der
Auswahlliste.
Beispiel:
In der Anwendung „Fehlerprotokoll“ Variante
„Benutzerhinweis“ ist die Funktion „AuswahllisteWarnung“ hinterlegt. Diese prüft
ab, ob ein Fehlerprotokolleintrag existiert. Es wird empfohlen diese als Vorlage
zu nutzen.
Zweistufige-Version
Im Gegensatz zu der einstufigen Version hat man hier
die Möglichkeit ein Verhalten bzw. einen Zustand zu fest definierten Zeitpunkten
zu überprüfen. Schlägt die Überprüfung fehl, so wird der Benutzer durch den
Hinweis bei der entsprechenden Auswahlliste aufmerksam gemacht. Dabei wird
außerdem wird eine Meldung im Fehlerprotokoll erzeugt, welche genauere
Informationen über die Art des Hinweises enthält.
Vorteile:
•
zeitgesteuerte Abfrage
•
Formulierung des Fehlers und ein Hinweis wie dieser behoben werden
kann.
•
Verlauf wird im Fehlerprotokoll dokumentiert
•
Hinweis kann abgestellt werden, ohne Daten zu ändern
Workflow:
•
Warnsymbol erscheint im Hintergrund.
•
Direktsprung [
FEHLH
].
•
Abarbeitung der angezeigten Meldungen.
•
Meldung auf „erledigt“ setzen.
•
Mit „ESC“ zurück zur ursprünglichen Auswahlliste.
•
Danach verschwindet das Warnsymbol mit dem nächsten aktualisieren der
Auswahlliste.
Einrichtung
:
•
Eintragen der Funktion „AuswahllisteWarnungEvent“ bzw. eine Ableitung in
einem Event
[EVT]
.
o
Hierin werden die
Zuständigkeit und das Aussehen
[...]


---

## Editieren teildisponierter Positionen

Editieren teildisponierter Positionen
Mit einer passenden Einstellung im [FRZ] (Tabreiter:
Sperren - Teildisponierte Position editierbar) ist es nun möglich,
teildisponierte Positionen im Quellbeleg nachträglich zu ändern.
Releasenote Kategorie:
Ticket: 708903[32077]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Formularzuordnung
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2211.30, 32077, 708903

---

## eClearing

eClearing
In der Anwendung [ECL] wird das Feld "eClearing" aus
der Variante "Zahlung per Datenträger" jetzt auch in der Variante
"Einzelpositionen" angezeigt.
Releasenote Kategorie:
Ticket: 712891[32686]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: Zahlung per Datenträger
Variante: Einzelpositionen
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2210.20, 32686, 712891

---

## Produktion: Itembox für Zu- und Abgangsartikel

Produktion: Itembox für Zu- und Abgangsartikel
Auf dem Tab - Reiter Produktion wurden in der
Anwendung [FRZ] Formularzuordnung 2 neue Felder hinzugefügt.  Diese Felder
dienen zur Erfassung einer Itembox für Artikel im Produktionszugang und
Produktionsabgang. Ist hier keine Itembox hinterlegt wird weiterhin der Standard
verwendet. Die Erfassungsreihenfolge auf der Produktionsmaske wurde angepasst
auf Zu-/Abgangsposition, Lagernummer, Artikel.
Releasenote Kategorie:
Ticket: 734771[33017]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Produktionszugang erfassen [PROE]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33017, 734771

---

## Teildisposition Erledigung bei Übererfüllung

Teildisposition Erledigung bei Übererfüllung
Es gibt jetzt in [FRZ] (Tabreiter: Sperren -
Mengenüberziehung erledigt Beleg) eine Einstellung, ob per Teildisposition
übererfüllte Teildispositionen als erledigt oder als teildisponiert gelten
sollen. Die Standardeinstellung ist die bisherige Behandlung "Ja".
Releasenote Kategorie:
Ticket: 714285[33031]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: -
Variante: -
Funktion/Report: Formularzuordnung
Weitere Informationen
Tags:
Releasenote, 8.3.2211.30, 33031, 714285

---

## Windows11-Anpassung: Asynchrones Anzeigen von Informationen

Windows11-Anpassung: Asynchrones Anzeigen von Informationen
Laufzeitfehler im Zusammenspiel zwischen Referenz-ERP/Editor
und Windows 11 wurden behoben.
Releasenote Kategorie:
Ticket: 716156[33155]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Basis-Funktion
Variante: -
Funktion/Report: AsyncNotepad
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33155, 716156

---

## eClearing

eClearing
Ruft man aus der Anwendung eClearing [ECL] die
Funktion Anzeigen/Bearbeiten auf, öffnet sich eine weitere Anwendung, in der
DTADiskIdent und DTADiskzaehler vorbelegt sind.  Die Eingrenzung des
DTADiskzaehlers im SQL-Text wurde nur auf gleich und nicht auf von/bis
eingrenzt. Dies wurde korrigiert.
Releasenote Kategorie:
Ticket: 717525[33290]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2302.17, 33290, 717525

---

## Teildisposition v_statusWeiter

Teildisposition v_statusWeiter
Bei der Version 8.3.2211.30 wurde das
Weiterverarbeitungskennzeichen eines Vorgangs von "teildipsoniert" auf
"erledigt" gesetzt, wenn man diesen im Änderungmodus geöffnet hat. Dies wurde
behoben.  Für Version 8.3.2211.30 können Sie einen Patch anfordern.
Releasenote Kategorie:
Ticket: 718718[33324]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Teildisposition
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33324, 718718

---

## Kunden Kreditvergabe

Kunden Kreditvergabe
Die Zeilenbeschränkung in der Krediterfassung wurde
aufgehoben.
Releasenote Kategorie:
Ticket: 715812[33354]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33354, 715812

---

## Bediener Deaktivieren/Aktivieren

Bediener Deaktivieren/Aktivieren
Bediener, der Kurzname einem SQL-Schlüsselwort
entspricht (Z.B. "AS", "ASC", ...), können jetzt auch aktiviert und deaktiviert
werden.
Releasenote Kategorie:
Ticket: 720319[33475]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: BD
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33475, 720319

---

## e-Clearing Hausbank

e-Clearing Hausbank
Sollten zu einer IBAN mehrere Hausbanken existieren,
so ist es nicht möglich, die Hausbank automatisch zuzuordnen. Damit
e-Clearing-Auszüge trotzdem als buchbar erkannt werden, existiert jetzt eine
Funktion "Hausbank zuordnen".
Releasenote Kategorie:
Ticket: 720614[33537]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: [ECL]
Variante: Zahlung per Datenträger
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33537, 720614

---

## Auswahlliste Funktionen

Auswahlliste Funktionen
Die in einer Auswahlliste verwendeten Zeichen werden
in einer XML-Struktur verwaltet. Wenn in einer Funktionsbezeichnung ein nicht
XML-Kompatibles Zeichen enthalten war, kam es zu einem XML-Parser-Fehler. Dieses
Problem wurde beseitigt.
Releasenote Kategorie:
Ticket: 721750[33620]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: alle
Variante: alle
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33620, 721750

---

## Rollenkontext (Bediener)

Rollenkontext (Bediener)
Es wurde die Variante "Rollenkontext" in der Anwendung
"Rollen" ([ROLLET]) erstellt, welche die freigegebenen Funktionen pro Bediener
ausweist.
Releasenote Kategorie:
Ticket: 720205[33614]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Rollen
Variante: Rollenkontext (Bediener)
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33614, 720205

---

## Bedienerstamm: Neuanlagedatum

Bedienerstamm: Neuanlagedatum
Der Bedienerstamm wurde um ein Feld mit dem
Neuanlagedatum erweitert. Dieses Feld wird bei bereits bestehenden Bedienern mit
dem Datum des Updates befüllt, da die Information der ursprünglichen
Bedieneranlage nicht vorliegt.
Releasenote Kategorie:
Ticket: 721532[33644]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33644, 721532

---

## e.Clearing Format CAMT.053

e.Clearing Format CAMT.053
In e-Clearing kann unter anderem das Format SEPA
CAMT.053 importiert werden. Diese Dateien müssen im so genannten Zip SEPA
Containern vorliegen und werden automatisch von Referenz-ERP entpackt. Beim Entpacken
wurde nicht erkannt, ob dabei ein Fehler auftrat. Es wird auf den Fehler
hingewiesen und die Fehlermeldungen werden ins Fehlerprotokoll geschrieben.
Releasenote Kategorie:
Ticket: 720598[33655]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2304.28, 33655, 720598

---

## eClearing Auszifferung anzeigen

eClearing Auszifferung anzeigen
Bisher war es so, dass im Modul e-Clearing nach der
Übernahme in die Primanota die Auszifferungsinformationen nicht mehr angezeigt
wurden. Für Belege, die mit dieser Version erstellt werden, kann sich die
Auszifferung jetzt weiter in e-Clearing angesehen werden.
Releasenote Kategorie:
Ticket: 723115[33768]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [ECL]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33768, 723115

---

## SPA 503 um neue Optionen erweitert

SPA 503 um neue Optionen erweitert
Der Steuerparameter 503 "Alle Kredite als Summe
übernehmen?" wurde um neue Optionen erweitert. Für eine detaillierte Auflistung
der verschiedenen Werte und Bedeutungen schauen Sie bitte unter dem angegebenen
Link in die Kundenhilfe.
Releasenote Kategorie:
Ticket: 724433[34076]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: -
Variante: -
Funktion/Report: amic_func_KundKredit,
amic_func_Update_KundKredit, AMIC_Kreditlimit
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 34076, 724433

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

## Artikelbestand Fremdware

Artikelbestand Fremdware
In der Variante "Artikelbestände mit FremdwareDispo"
ist eine neue Spalte eingefügt worden: Die Spalte "Verf. Fremd" zeigt den
verfügbaren Bestand zuzüglich nicht disponierter Fremdware an.  So können
nicht disponierte Aufträge als verfügbare Ware gerechnet werden, während
vorverkaufte aber noch nicht abgeholte Waren in der Spalte "Verfügbar" nicht
mitgerechnet werden.
Releasenote Kategorie:
Ticket: 721652[34047]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Artikelbestand
Variante: Artikelbestände mit FremdwareDispo
Funktion/Report: Auswahlliste
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34047, 721652

---

## Tausendertrennzeichen bei Zahlungsbedingungen

Tausendertrennzeichen bei Zahlungsbedingungen
In der textlichen Darstellung der Zahlungsbedingungen
[ZB] werden jetzt numerische Werte wie z.B. der Brutto-Betrag mit einem
Tausendertrennzeichen versehen, außer die angegebene Länge ist zu kurz. Reicht
die angegebene Länge nicht aus, um den numerischen Wert darzustellen, wird der
Wert nicht mehr abgeschnitten, sondern es werden im Zahlungsbedingungstext statt
des Wertes nun Sterne (***) angezeigt.  Mit dem neuen Steuerparameter 1148
- "Leerzeichen bei Zahlungsbedingungstext entfernen" kann jetzt
abgeschaltet werden, dass die einzelnen Werte im Zahlungsbedingungstext mit
Leerzeichen aufgefüllt werden.
Releasenote Kategorie:
Ticket: 726959[34235]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Zahlungsbedingungen [ZB]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34235, 726959

---

## Auswahlliste: Eigene Schaltfläche für die Ansichten

Auswahlliste: Eigene Schaltfläche für die Ansichten
In der Auswahlliste gibt es jetzt eine eigene
Schaltfläche für die Ansichten. So können die Profile und Ansichten getrennt
voneinander ausgewählt werden. Die Schaltfläche für die Ansichten ist nur dann
sichtbar, wenn für den Bediener neben der Standardansicht noch weitere Ansichten
existieren.
Releasenote Kategorie:
Ticket: 731003[34740]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34740, 731003

---

## eClearing CAMT 53 Format

eClearing CAMT 53 Format
In der Anwendung eClearing [ECL] kann die Funktion
"Datei laden" aufgerufen werden. Für das Format CAMT53 wurde bisher nur die
Dateiendung .c53 im Dateiauswahldialog angeboten. Jetzt kann man zusätzlich
komprimierte Zip-Archive mit der Endung ZIP verwenden.
Releasenote Kategorie:
Ticket: 732832[35013]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: eClearing [ECL]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 35013, 732832

---

## Kundentypänderung

Kundentypänderung
Ein Kundentyp kann nur geändert werden, solange keine
Belege vorhanden sind, wenn die Kundentypänderung eine Änderung der Kundennummer
durch Wechsel des Nummernkreises bedingen würde. Hintergrund ist, dass die
bestehenden Belege durch eine Änderung der Kundennummer verwaist
würden.
Releasenote Kategorie:
Ticket: 732061[34999]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Kunden
Variante: Kunden
Funktion/Report: Ändern
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 34999, 732061

---

## SQL-Meldung bei individuellem Kreditlimit

SQL-Meldung bei individuellem Kreditlimit
Mit der aktiven Einstellung ("Ja") für
den Steuerparameter 594 - "Erm.Kreditlimit mit P_IndivKreditLimit" kam es
in der Vorgangsbearbeitung zu einem SQL-Fehler mit dem Hinweis auf den
limitierten Ausdruck "Limit". Dieses Problem wurde nun behoben. Der verwendete
Alias in dem SQL-Statement wurde auf "Kreditlimit" geändert.
Releasenote Kategorie:
Ticket: 733459[35039]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Vorgangsbearbeitung
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 35039, 733459

---

## eClearing CAMT 53 Format

eClearing CAMT 53 Format
In der Anwendung eClearing [ECL] kann die Funktion
"Datei laden" aufgerufen werden. CAMT-Dateien werden in einem komprimierten
Zip-Archiv geliefert und können mehrere Dateien enthalten. Beim Import wurde
fälschlicherweise nur die erste dieser Dateien verarbeitet. Dies wurde nun
korrigiert.
Releasenote Kategorie:
Ticket: 733664[35082]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: eClearing [ECL]
Variante: --
Funktion/Report: Datei laden
Weitere Informationen
Tags:
Releasenote, 9.0.2401.2, 35082, 733664

---

## e-Clearing Anzeige Adressblocj

e-Clearing Anzeige Adressblocj
Bei der Bearbeitung von e-Clearing kam es im
Adressblock zu einer geringfügigen Verschiebung einiger Texte. Das
Anzeigeproblem wurde behoben.
Releasenote Kategorie:
Ticket: 734884[35246]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: ECL
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35246, 734884

---

## eClearing CAMT.053

eClearing CAMT.053
Beim Einspielen der CAMT.053 Dateien wurden
Sammelbuchungen nicht korrekt ausgewertet.
Releasenote Kategorie:
Ticket: 734905[35286]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 35286, 734905

---

## Zugriffschutz auf Varianten

Zugriffschutz auf Varianten
Unter [ZUGV], in der Variante "geschützte Varianten"
wurde durch ein fehlerhaftes IDENTSQL auf die falsche Tabelle zugegriffen und
dadurch die bereits eingetragenen Bedienerklassen nicht geladen.
Releasenote Kategorie:
Ticket: 737530[35571]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: ZUGV
Variante: Geschützte Varianten
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35571, 737530

---

## eCLearing CAMT53

eCLearing CAMT53
Im CAMT63 - Format können mehrere Zeilen
Verwendungszweck vorhanden sein. Dies wird jetzt beim Import berücksichtigt.
Releasenote Kategorie:
Ticket: 737152[35637]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35637, 737152

---

## neue Auswahllistenvariante im Archiv

neue Auswahllistenvariante im Archiv
Eine neue Variante im Archiv zeigt eRechnungen an.
Hier lässt sich eine eRechnung importieren und manuell weiterverarbeiten.
Entsprechende Filter spezialisieren diese Auswahlliste für eRechnungen
Releasenote Kategorie:
Ticket: 728333[35687]
Version: 9.0.2402.3
Datum: 08.11.2024
Anwendung: Formulararchiv [FA]
Variante: Formulararchiv eRechnung
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.3, 35687, 728333

---

## Neue Auswahllistenvariante im Archiv

Neue Auswahllistenvariante im Archiv
Eine neue Variante im Archiv zeigt eRechnungen an.
Hier lässt sich eine eRechnung importieren und manuell weiterverarbeiten.
Entsprechende Filter spezialisieren diese Auswahlliste für eRechnungen.
Releasenote Kategorie:
Ticket: 728333[35742]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Formulararchiv [FA]
Variante: Formulararchiv eRechnung
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35742, 728333

---

## Archiv-Verlinkung von eRechnungsexporten bei privatisierten Belegreferenzen

Archiv-Verlinkung von eRechnungsexporten bei privatisierten
Belegreferenzen
Falls unter [FAREF] beim Archiv-Fakt eine private
Prozedur zur Erstellung der Belegreferenz von Vorgängen verwendet wurde, dann
hat die Verbindung zum Archiv nicht funktioniert.Das bedeutet, dass nach dem
Erstellen eines Beleges und danach einen eRechnungsexport durchgeführt hat, per
Strg + F12 den eRechnungsexport nicht im Archiv angezeigt bekommen hat.Dies
wurde behoben.
Releasenote Kategorie:
Ticket: 740061[35788]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: [FAREF] Formulararchiv Administration
Variante: Archiv-Fakte
Funktion/Report: F5, F8
Weitere Informationen
Tags:
Releasenote, 9.0.2402.4, 35788, 740061

---

## Fehler in der Index.xml des DSFinV-K-Exports behoben

Fehler in der Index.xml des DSFinV-K-Exports behoben
Beim Erstellen der Index.xml-Datei für den
DSFinV-K-Export wird jetzt als RecordDelimiter der Wert &#13;&#10;
verwendet. Außerdem wurde für Felder mit Numerischen-Datentyp das Accuracy-Tag,
welches die Anzahl der vorhandenen Nachkommastellen  angibt,
hinzugefügt.
Releasenote Kategorie:
Ticket: 740079[35850]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: DSFinV-K Export
Variante: -
Funktion/Report: Export erzeugen (F10)
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 35850, 740079

---

## Eclearing

Eclearing
Der Zinsstatus für das Hauptkonto (Konto der Hausbank)
wurde beim Erstellen des Zahlungsbeleges ohne Zinsstatus gespeichert. Dies ist
behoben.
Releasenote Kategorie:
Ticket: 739712[35969]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35969, 739712

---

## Standard F3-Auswahl und Auswahlliste

Standard F3-Auswahl und Auswahlliste
Die neue F3-Auswahl mit fester Fensterposition wurde
als Standard festgelegt, wenn sie beim Bediener "Standard Programmvorgabe" unter
"Version F3-Auswahl"eingetragen ist.  Bei der Neuanlage von Bedienern wird
die neue Auswahlliste als Standard eingestellt. Die Vorbelegung des
Suchkriteriums kann jetzt auch über die Schlüsselwörter ITEM1 und ITEM2
geschehen.
Releasenote Kategorie:
Ticket: 739402[35977]
Version: 9.0.2501.5
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35977, 739402

---

## eRechnung Umwandlung

eRechnung Umwandlung
Ein Beleg, der als eRechnung exportiert wurde kann nun
zu einer Gutschrift umgewandelt werden.
Releasenote Kategorie:
Ticket: 741662[36082]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Rechnung
Variante: n/a
Funktion/Report: Gutschrift aus Rechnung
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 36082, 741662

---

## Hausbankenstamm [BNKH] - Hausbank in eRechnung

Hausbankenstamm [BNKH] - Hausbank in eRechnung
Bei den Hausbanken [BNKH] gibt es einen neuen Bereich
namens "eRechnung", in welchem ausgewählt werden kann, ob diese Hausbank in
eRechnungen verwendet werden soll.
Releasenote Kategorie:
Ticket: 741942[36085]
Version: 9.0.2501.5
Datum:
Anwendung: BNKH
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36085, 741942

---

## Mailversand Duplikate

Mailversand Duplikate
In der Anwendung [MAIL] werden Datensätze je Anhang
(.pdf, .xml, etc) angezeigt. Das begründet sich in der Vorschau-Funktion dieser
Anwendung. Leider führte dies jedoch beim Versenden dazu, dass pro Datensatz
eine E-Mail mit allen Anhängen versendet wurde. Dieses Verhalten wurde
angepasst. Es werden weiterhin Datensätze je Anhang angezeigt, jedoch führt die
Versand-Funktion jeweils nur noch einen Versand mit allen Anhängen aus.
Releasenote Kategorie:
Ticket: 741775[36096]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Mailversand [MAIL]
Variante: alle
Funktion/Report: Freigeben/Versenden
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 36096, 741775

---

## Nullpointer Problematik bei behoben

Nullpointer Problematik bei behoben
Nullpointer Problematik bei
WarenPosition::GetZahlBedingung() behoben. Zahlbedingung wird wenn Kundzahlbed
== null aus VorgZahlBed gezogen.
Releasenote Kategorie:
Ticket: 740638[36126]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: [PIVB]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36126, 740638

---

## Steuerkategorien für eRechnung

Steuerkategorien für eRechnung
Steuerkategorien für die eRechnung können nun bei den
Steuersätzen gepflegt werden. Als Default ist "S" - Standard Rate eingepflegt
worden. Die abweichenden Steuerkategorien  (Bei Befreiungen auch die
Ausnahmebegründungen) werden dann vom Steuersatz in das eRechnungs-Dokument
übernommen.
Releasenote Kategorie:
Ticket: 742137[36122]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: Steuersätze
Variante: n/a
Funktion/Report: Neu/Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36122, 742137

---

## eRechnung Adressaufbereitung

eRechnung Adressaufbereitung
Die Reihenfolge von Angaben in eRechnungs-Anschriften
wurde optimiert.
Releasenote Kategorie:
Ticket: 742981[36222]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: Rechnung
Variante: n/a
Funktion/Report: eRechnung exportieren
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36222, 742981

---

## Felder im eRechnungs-Export

Felder im eRechnungs-Export
Die Felder BT-14, BT-17 und BT-18 werden nun auch im
eRechnungs-Export ausgegeben
Releasenote Kategorie:
Ticket: 740922[36257]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: Rechnungen
Variante: Standard
Funktion/Report: eRechnung exportieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36257, 740922

---

## GLN in der eRechnung

GLN in der eRechnung
Das Feld BT-71 GLN in der eRechnung wird nun korrekt
ausgegeben.
Releasenote Kategorie:
Ticket: 743108[36286]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: Rechnung
Variante: Standard
Funktion/Report: eRechnung exportieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36286, 743108

---

## Eclearing CAMT.053 auch ungepackt als XML importieren

Eclearing CAMT.053 auch ungepackt als XML importieren
Das CAMT053-Format lässt sich jetzt auch ungepackt als
XML-Datei importieren.
Releasenote Kategorie:
Ticket: 743497[36404]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36404, 743497

---

## Korrektur der Rechnungsadresse bei abweichenden Empfänger in eRechnungen

Korrektur der Rechnungsadresse bei abweichenden Empfänger in
eRechnungen
Wenn ein Oberkunde (abweichender
Rechnungsempfänger) vorhanden ist, wird nun die korrekte Adresse in das
xRechnungs-Attribut (XML) für die "postaladress" übernommen.
Releasenote Kategorie:
Ticket: 743700[36409]
Version: 9.0.2501.5
Datum:
Anwendung: eRechnung
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36409, 743700

---

## Zahlungsbedingungen löschen

Zahlungsbedingungen löschen
Zahlungsbedingungen [ZB] können nun auch gelöscht
werden. Zu diesem Zweck wird ein Löschkennzeichen gesetzt. Die so gelöschten
Zahlungsbedingungen können über die Funktion "Wiederherstellen" reaktiviert
werden.
Releasenote Kategorie:
Ticket: 736601[36495]
Version: 9.0.2501.5
Datum:
Anwendung: Zahlungsbedingungen
Variante: [ZB]
Funktion/Report: Löschen
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36495, 736601

---

## Referenz-ERP Passwortrichtlinien

Referenz-ERP Passwortrichtlinien
Passwort-Richtlinien können nun hinterlegt werden. Die
Einstellung erfolgt über die Bedienerklassen [BDKL]. Unter dem Reiter
Passwortrichtlinien können Sie nun individuelle Passwortrichtlinien auf Ihre
Unternehmensrichtlinien angepasst eintragen.
Releasenote Kategorie:
Ticket: 737928[36573]
Version: 9.0.2501.5
Datum:
Anwendung: [BDKL]
Variante: Bedienerklasse
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36573, 737928

---

## UFLD "Keine Änderung"

UFLD "Keine Änderung"
Es gibt UFLD-Felder, die lediglich zur Anzeige
vorgesehen sind. Diese werden unter UFLD mit  dem neuen Erfassungslevel
"Keine Änderung" systemseitig gekennzeichnet. Dieser Erfassungslevel kann bei
anderen UFLD-Feldern nicht durch den Bediener gesetzt werden. Dieser
Erfassungslevel kam im Rahmen der eRechnungsintegration in die
Software.
Releasenote Kategorie:
Ticket: 744553[36647]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Vorgänge wie EK-Rechnung
Variante: n/a
Funktion/Report: Erfassung
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36647, 744553

---

## Supportingdocuments in eRechnung

Supportingdocuments in eRechnung
Sind in einer eingehenden eRechnung digitale Dokumente
enthalten, so werden diese nun beim Import ebenfalls extrahiert und in einer
Gruppe mit der eRechnung ins Formulararchiv gespeichert.
Releasenote Kategorie:
Ticket: 744828[36649]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Formulararchiv
Variante: Formulararchiv eRechnung
Funktion/Report: eRechnung verarbeiten
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36649, 744828

---

## Formulararchiv eRechnung Datenanzeige

Formulararchiv eRechnung Datenanzeige
Im Formulararchiv [FA] in der Variante "Formulararchiv
eRechnung" trat unter bestimmten Filterbedingungen ein Problem auf, das jetzt
behoben ist.
Releasenote Kategorie:
Ticket: 745684[36675]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Formulararchiv
Variante: Formulararchiv eRechnung
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36675, 745684

---

## Eclearing Auszugsnummer CAMT053

Eclearing Auszugsnummer CAMT053
Beim CAMT-Import wurde bisher die ID (Referenz des
erstellenden Instituts, die diesen Informationen-Sammler eindeutig kennzeichnet)
als Auszugsnummer übernommen. Diese wird jetzt, falls im CAMT-Dokument
vorhanden, von der papierhaften Auszugsnummer (Element LglSeqNb) oder der
laufende elektronische Auszugsnummer des Auszugs (Element ElctmSeqNb)
abgelöst.   Die Eindeutigkeitsprüfung, also ob der Auszug bereits
eingelesen wurde, erfolgt jedoch weiter über die ID.
Releasenote Kategorie:
Ticket: 744446[36659]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36659, 744446

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

## AIS Multilinefeler

AIS Multilinefeler
Bei Multilinefelder in AIS kann mit F3 oder per
Doppelklick der Text in einem Editor bearbeitet werden.
Releasenote Kategorie:
Ticket: 0[36695]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: AIS
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36695, 0

---

## eClearing

eClearing
In eClearing wurden die Funktionen "Kundenbank
ändern", "Fibumerkmale" und "Kundenbemerkungen" nicht mehr im Menü des Pflegers
angeboten.
Releasenote Kategorie:
Ticket: 743838[36717]
Version: 9.0.2501.5
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36717, 743838

---

## Exportformat: ZugFeRD in eRechnung-Profilpfleger [XRE]

Exportformat: ZugFeRD in eRechnung-Profilpfleger [XRE]
Im eRechnungs-Profilpfleger [XRE] gibt es jetzt die
Angabe des Exportformats. Zur Auswahl stehen UBL (universal Business Language) -
das wie bisher ein XML im UBL-Format exportiert und neu CII/ZugFeRD, das die
eRechnung als ZugFeRD als in ein PDF eingebettetes CII-Xml exportiert.
Releasenote Kategorie:
Ticket: 0[36843]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: eRechnung [XRE]
Variante: Export-Profile
Funktion/Report: Anlegen / Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36843, 0

---

## Formularchivbelegdatum der eRechnung entspricht jetzt dem Belegdatum des Ursprungsbelegs.

Formularchivbelegdatum der eRechnung entspricht jetzt dem Belegdatum des
Ursprungsbelegs.
Das Belegdatum des eRechnung-Xml im Formulararchiv
entspricht nun dem Datum des Vorgangs.
Releasenote Kategorie:
Ticket: 746506[36956]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: [FA]
Variante: Formulararchiv eRechnung
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36956, 746506

---

## Formulararchiv eRechnung "Dokument speichern" Funktion

Formulararchiv eRechnung "Dokument speichern" Funktion
In der Anwendung "Formulararchiv" [FA], Variante
"Formulararchiv eRechnung" wurde die Funktion "Dokument speichern"
hinzugefügt.  Mit der Funktion wird der Eintrag aus dem Archiv auf einen
Datenträger gespeichert.
Releasenote Kategorie:
Ticket: 746170[36913]
Version: 9.0.2501.5
Datum:
Anwendung: [FA]
Variante: Formulararchiv eRechnung
Funktion/Report: Dokument speichern
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36913, 746170

---

## eClearing Reihenfolge Positionen in CAMT053

eClearing Reihenfolge Positionen in CAMT053
Im eClearing konnte es beim Einspielen der
Kontoauszüge im CAMT053-Format dazu kommen, dass die vorgegebene Reihenfolge der
Positionen nicht übernommen wurde. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 746114[36920]
Version: 9.0.2501.5
Datum:
Anwendung: eClearing [ECL]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36920, 746114

---

## StandardbelegflussPostfächer für den Import

StandardbelegflussPostfächer für den Import
In der Anwendung eRechnung [XRE], Variante Import
Vorgänge, kann jetzt über die Funktion "Importeinstellungen bearbeiten" je ein
Belegflusspostfach für die Warenwirtschaft und die Finanzbuchhaltung
eingerichtet werden.
Releasenote Kategorie:
Ticket: 746729[36960]
Version: 9.0.2501.5
Datum:
Anwendung: eRechnung [XRE]
Variante: Import-Vorgänge
Funktion/Report: Importeinstellungen bearbeiten
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36960, 746729

---

## eClearing CAMT53 Zusatzinformationen

eClearing CAMT53 Zusatzinformationen
Werden im eClearing [ECL] Informationen zu Gebühren
der Transaktion mit in der CAMT53-Datei übermittelt, so werden diese
informatorisch im Textteil mit angezeigt.
Releasenote Kategorie:
Ticket: 746620[37158]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37158, 746620

---

## Belegversand zieht Daten aus eRechnungseinrichtung, wenn Prozedur AMIC_Belegversand_Ware_Spaeter genutzt wird

Belegversand zieht Daten aus eRechnungseinrichtung, wenn Prozedur
AMIC_Belegversand_Ware_Spaeter  genutzt wird
Es wurde die
Prozedur AMIC_Belegversand_Ware_Spaeter  für eRechnung spezialisiert.
Das hat dazu geführt, dass durch das Ausfüllen von eRechnungsdaten im
betroffenen Kunden immer die eRechnungsmailadresse beim Belegversand gezogen
wurde.  Die neue Prozedur AMIC_Belegversand_Ware_Spaeter_ohne_xRechnung
wurde aus früheren Version der Prozedur AMIC_Belegversand_Ware_Spaeter
erstellt. Das bedeutet, dass man in [FRZ] für zum Beispiel Aufträge und
Angebote die Prozedur AMIC_Belegversand_Ware_Spaeter_ohne_xRechnung
und für Rechnung und Gutschriften AMIC_Belegversand_Ware_Spaeter
Releasenote Kategorie:
Ticket: 747369[37315]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Alls Anwendung wo man Vorgänge drucken
kann.
Variante: Alle Varianten wo man Vorgänge drucken
kann.
Funktion/Report: Formulardruck(F10)
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37315, 747369

---

## Importprobleme bei fehlendem BG-14 - Invoicing Period

Importprobleme bei fehlendem BG-14 - Invoicing Period
Es gab einige eRechnungen wo der Businesstermin
14( BG-14 - Invoicing Period) in der XML leer war. Beim Import wurde damit
nicht korrekt umgegangen und es wurde dann die eRechnung nicht korrekt
importiert und dann nicht in eine HTML-Datei umgewandelt. Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 748040[37470]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Formulararchiv
Variante: Formulararchiv eRechnung
Funktion/Report: eRechnung verarbeiten
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37470, 748040

---

## Auswahllisten der Anwendung eRechnung [XRE]

Auswahllisten der Anwendung eRechnung [XRE]
Die Performance im Aufbau der Auswahllisten in der
Anwendung eRechnung [XRE] wurde durch Überarbeitung des Datenbankschemas
(Indizes) optimiert.
Releasenote Kategorie:
Ticket: 747987[37471]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: eRechnung [XRE]
Variante: alle
Funktion/Report: Auswahllistengenerierung
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37471, 747987

---

## eRechnung ID nur Ansicht

eRechnung ID nur Ansicht
Bei der direkten Erfassung von Eingangs-Rechnungen und
-Gutschriften aus [FIBE] kann die eRechnungs-ID nicht mehr gepflegt werden. Dies
geschieht über das Modul Belegfluss.
Releasenote Kategorie:
Ticket: 748264[37640]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: FIBE
Variante: STD
Funktion/Report: Fibu Beleg Erfassen (ER / EG)
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37640, 748264

---

## Differenzwertberechnungen

Differenzwertberechnungen
Unter bestimmten Umständen konnte es auf einigen
Masken bei Differenzwertberechnungen um eine Abweichung von 0,01 kommen.
 Dieses Verhalten wurde korrigiert.
Releasenote Kategorie:
Ticket: 749245[37881]
Version: 9.0.2502.6
Datum:
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.6, 37881, 749245

---

## eClearing Fremdwährung

eClearing Fremdwährung
Im eClearing [ECL] wurde das Format CAMT.053
erweitert, so dass nun auch Belege in Fremdwährung korrekt verarbeitet werden.
Es wird beim Einlesen der in den Währungskursen gepflegte Kurs verwendet. Dieser
kann direkt in der Bearbeitung geändert werden.
Releasenote Kategorie:
Ticket: 750497[38449]
Version: 9.0.2502.7
Datum:
Anwendung: eClearing [ECL]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38449, 750497

---

## eRechnung Artikelbeschreibung

eRechnung Artikelbeschreibung
Für die eRechnung werden nun auch manuelle
Artikeltexte aus einem Vorgang übermittelt.
Releasenote Kategorie:
Ticket: 751361[38545]
Version: 9.0.2502.8
Datum:
Anwendung: eRechnung [XRE]
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.8, 38545, 751361

---

## eRechnung

eRechnung
Leere Contact-Tags werden aus der eRechnung
entfernt.
Releasenote Kategorie:
Ticket: 751230[38544]
Version: 9.0.2502.8
Datum:
Anwendung: XRE
Variante: eRchnungsexport
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.8, 38544, 751230

---

## Eclearing CAMT053

Eclearing CAMT053
Es kann bei Kontoauszügen Im CAMT053-Format dazu
kommen, dass Bewegungen ohne Detailbereich übermittelt werden. Diese Bewegungen
werden jetzt auch in Referenz-ERP eingespielt.  Zusätzlich wird noch das Element
AddtlNtryInf mit übernommen. Dies enthält   Zusätzliche Informationen
zum Umsatz wie zum Beispiel "SB-Einzahlung", "Bargeldauszahlung" oder
"Überweisungsgutschr."
Releasenote Kategorie:
Ticket: 751396[38799]
Version: 9.0.2502.9
Datum:
Anwendung: ECL
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2502.9, 38799, 751396

---

## Variante Publikationen

Variante Publikationen
Felder
Publikation
Name
      der Publikationen
Eigenschaft
Zeigt die Eigenschaft einer
      Publikation:
-
Amic-Standard
-
benutzerdefiniert
Anzahl Artikel
Anzahl der in der Publikation
      enthaltenen Artikel
Anzahl aktive Artikel
Anzahl der Artikel in einer Aktiven
      Publikation
Funktionen
Pflege-Funktionen
Neu
Upgrade Tabellen
Weist alle noch nicht zugeordneten
      Tabellen der Publikation „
AMIC_nicht_zugeordnet
“ zu.
Bereiche/Profile
Publikation wie
Ermöglicht Suche nach
      Publkationsnamen
F3
ermöglicht die konkrete Auswahl und
      informiert über den Publikationstypen.
Eigenschaft
Ermöglicht Suche nach
      Publikationseigenschaft
-
Amic-Standard
-
benutzerdefiniert

---

## Auswahlbedingungen (EPA AWMSKDYN)

Auswahlbedingungen (EPA AWMSKDYN)
Bezeichnung
Standardwert
Erklärung
Spacing für den ¨Radio-Button¨ links
      in Pixeln
0
Ob man
      diesen EPA verwenden muss hängt von der Einstellung der Anzeige ab. Steht
      diese auf 96 DPI (Standard) muss man nichts machen. Ansonsten kann man
      hier die bei anderen Einstellungen nicht passenden Abstände der
      Radio-Buttons korrigieren.

---

## zahMaskenTitel (EPA BEDIKLAG)

zahMaskenTitel (EPA BEDIKLAG)
Bezeichnung
Standardwert
Erklärung
Maximale Stufe für Einsicht in
      Kontensaldo
1

---

## Bedienerstamm (EPA BEDISTAM)

Bedienerstamm (EPA BEDISTAM)
Bezeichnung
Standardwert
Erklärung
Andere Bezeichnung für Name
      Extern
Hier kann
      die Feldbezeichnung „Name Extern“ überschrieben werden.

---

## EDIFACT Codierung (EPA BT_BUNDN)

EDIFACT Codierung (EPA BT_BUNDN)
Bezeichnung
Standardwert
Erklärung
HRC2000 nur wenn Steuerschlüssel
      unterschiedlich
Nein

---

## EDIFACT Codierung (EPA BT_BUNDNIMPORT)

EDIFACT Codierung (EPA
BT_BUNDNIMPORT)
Bezeichnung
Standardwert
Erklärung
Private Ableitung der
      STDDAT
P_STDDAT
Schema

---

## Sicherheitsklasse (EPA Bediklas)

Sicherheitsklasse (EPA Bediklas)
Bezeichnung
Standardwert
Erklärung
Feld
      Sicherheitsklasse freischalten
Nein
Damit kann das Feld für die
      Sicherheitsklassen-Bearbeitung zugänglich gemacht werden.

---

## Archiv Mail Versand (EPA FA_MAIL)

Archiv Mail Versand (EPA FA_MAIL)
Bezeichnung
Standardwert
Erklärung
Absender aus
      Bedienerstamm
Nein
Versandfunktion
Archiveintraege_Versenden
SQL-Prozedur die zum Versenden
      verwendet werden soll.
Eigene Prozedur zur
      Adressaufbereitung
FA_mail_senden_an_Adressen
Die
      Adressen werden in der oberen Tabelle des Senden-An Pflegers zur Verfügung
      gestellt und können individuell angepasst werden.
Die
      Standard Vorbelegung, welche auch privatisiet werden kann ist die
      Prozedur:
FA_mail_senden_an_Adressen
Diese sammelt ausgehend vom
      Formulararchiv die E-Mail-Adressen der Kunden, welche im Kundenstamm des
      zugehörigen Kunden sowie unter dem Vorgangskunden
und dem
      Rechnungskunden
im zugehörigen Vorgang
      eingetragen sind.
Versand-XML anzeigen
Nein
Mit
      dieser Einstellung kann das Versand-XML zu Debug-Zwecken angezeigt
      werden
Alternative zusätzliche Adresse 1 (
      0 = keine, sonst ADRESSID )
0
Im
      Standard nicht implementiert.
Alternative zusätzliche Adresse 2 (
      0 = keine, sonst ADRESSID )
0
Im
      Standard nicht implementiert.
Alternative zusätzliche Adresse 3 (
      0 = keine, sonst ADRESSID )
0
Im
      Standard nicht implementiert.
Alternative zusätzliche Adresse 4 (
      0 = keine, sonst ADRESSID )
0
Im
      Standard nicht implementiert.
Alternative zusätzliche Adresse 5 (
      0 = keine, sonst ADRESSID )
0
Im
      Standard nicht implementiert.
Lager-Adressen aus Vorgang
      ermitteln
Ja
Hiermit kann festgelegt werden, ob
      bei Vorgängen die Adresse des Lagers ermittelt wird.
IP-Adresse des SMTP-Relays für
      Mails
IP-Adresse des SMTP-Servers der für
      den Versand der E-Mails verwendet werden soll.
Maske nach korrekter Versendung
      verlassen
Nein
Soll
      die Maske nach dem Versenden verlassen werden, wenn keine
      Fehlerprotokolleinträge vorhanden sind.
Adressmaske bei Doppelklick auf
      Mail-Adresse/Fax-Nummer aufrufen
Nein
S
[...]


---

## Kreditvergabe (EPA HIDE_LOEKENNZ_GELOESCHT)

Kreditvergabe (EPA HIDE_LOEKENNZ_GELOESCHT)
Bezeichnung
Standardwert
Erklärung
Nur
      aktive Datensätze anzeigen?
Nein
Es
      kann angegeben werden, ob gelöschte oder inaktive Datensätze von
      Kreditvergaben angezeigt werden.

---

## Preis Info System (EPA PIN)

Preis Info System (EPA PIN)
Bezeichnung
Standardwert
Erklärung
Vergl.kunden nach Artikel-Eingabe
      autom. anzeigen
Ja
Für
      jeden Bediener der das Preis Info System einmal verwendet hat werden die
      angegebenen Vergleichskunden gespeichert. Öffnet man das System erneut und
      wählt einen neuen Artikel aus werden die Preise für die hinterlegten
      Vergleichskunden gleich mit angezeigt.
Möchte man dies nicht muss der
      Einrichterparameter auf Nein gesetzt werden.

---

## Datenübernahme Oracle (EPA SU_DATAEDIT)

Datenübernahme Oracle (EPA SU_DATAEDIT)
Bezeichnung
Standardwert
Erklärung
Artikeltyp, 0=Standard,
      1=sorte/Kat/Behandlung
1
Tabellenname Oracle
OracleTransfertabelle

---

## Gruppen-Rabatt (EPA SVGRAB)

Gruppen-Rabatt (EPA SVGRAB)
Bezeichnung
Standardwert
Erklärung
nach
      Nummerneingabe sofort abschließen
Nein
Berechnungsformel ( Vorschlag
      )
Proz. v. Warenwert abz. vorh.
      Zu-/Abschl.
Bezeichnung des
      Zu-/Abschlags
Gruppenrabatt

---

## Gruppen-Zu-/Abschlag (EPA SVGZUAB)

Gruppen-Zu-/Abschlag (EPA SVGZUAB)
Bezeichnung
Standardwert
Erklärung
nach
      Nummerneingabe sofort abschließen
Nein
Berechnungsformel ( Vorschlag
      )
Proz. v. Warenwert abz. vorh.
      Zu-/Abschl.
Druckform offen=Ja,
      verdeckt=Nein
Ja
Bezeichnung des
      Zu/-Abschlags
Zu-/Abschlag

---

## Zeilen-Rabatt (EPA SVZRAB)

Zeilen-Rabatt (EPA SVZRAB)
Bezeichnung
Standardwert
Erklärung
nach
      Nummerneingabe sofort abschließen
Nein
Berechnungsformel ( Vorschlag
      )
Proz. v. Warenwert abz. vorh.
      Zu-/Abschl.
Ausweisung(Druck) in Bezugszeile
      (Ja) oder Extrazeile (Nein)
Nein
Zu-/Abschlagstext
Rabatt

---

## Zeilen-Zu-/Abschlag (EPA SVZZUAB)

Zeilen-Zu-/Abschlag (EPA SVZZUAB)
Bezeichnung
Standardwert
Erklärung
nach
      Nummerneingabe sofort abschließen
Nein
Berechnungsformel ( Vorschlag
      )
Proz. v. Warenwert abz. vorh.
      Zu-/Abschl.
Einzelpreis Bezugszeile inklusiv
      Zu-/Abschlag ( z.B. Fracht )
Nein
Ausweisung(Druck) in der
      Bezugszeile=Ja oder Extrazeile=Nein
Nein
Druckform
      Offen=Ja/Verdeckt=Nein
Ja
Zu-/Abschlagstext
Zu-/Abschlag

---

## Sekundärartikelposition (EPA TBRWSOA2)

Sekundärartikelposition (EPA TBRWSOA2)
Bezeichnung
Standardwert
Erklärung
Nur
      Preise editierbar
Nein

---

## Frachten

Frachten
Definition lt. Wikipedia:
Fracht ist das
Entgelt
, welches ein
Frachtführer
für die im
Frachtvertrag
vereinbarte Beförderung
von Gütern erhält (synonym verwendete -juristisch jedoch nicht ganz korrekte-
Begriffe: Frachtgeld, Frachtlohn).
Verwendung in Referenz-ERP
Frachten lassen sich in Referenz-ERP als automatische
Berechnung einrichten. Ebenso können Frachten manuell im Anschluss an die
Erfassung einer Warenposition erfasst werden.
Die Berechnung einer Fracht kann pro Warenposition
oder für eine Gruppe von Warenpositionen einer Gruppe (Rabattgruppe) als
Gruppenfracht berechnet werden.
Lizenz für Frachten
Frachten sind ein lizensierungspflichtiges Modul. (SPA
445)

---

## Variante Inhalte von Publikationen

Variante Inhalte von Publikationen
Felder
Publikation
Name
      der Publikationen
Eigenschaft
Zeigt die Eigenschaft einer
      Publikation:
-
Amic-Standard
-
benutzerdefiniert
Artikel
Name
      des in der Publikation angegebenen Artikels.
(Name der Tabelle)
PK
      vorhanden
JA/Nein
Zeigt an, ob der Artikel ( Tabelle )
      über Primary Key-Felder verfügt.
Sollte hier ein „Nein“ verzeichnet
      sein so ist dieser Artikel im Falle der Verwendung in Publikationen,
      welche in Replikationen verwendet werden sollen, mit einem gültigen
      Primary Key zu versehen!
Publikations-Artikel
      aktiv
Zeigt an, ob der Artikel in einer
      aktiven Publikation enthalten ist.
Suche nach:
-
ja
-
nein
-
egal
Partitionsbedingung
Subscribe by
Restriktionsbedingung
where-Klausel
Lock-Status
Zeigt an, ob die Tabelle des
      Artikels gerade gesperrt ist.
Suche nach:
-
ja
-
nein
-
egal
Lock-Bediener
Zeigt eine Liste der Bediener,
      welche die Tabelle eines Artikels gerade sperren.
Funktionen
Pflege-Funktionen
Neu,
      Ändern, Löschen
Pfleger
      Publikationen
Zuordnung vergleichen
Zuordnung
      vergleichen
Bereiche/Profile
Publikation wie
Ermöglicht Suche nach
      Publikationsnamen
F3
ermöglicht die konkrete Auswahl und
      informiert über den Publikationstypen.
Eigenschaft
Ermöglicht Suche nach
      Publikationseigenschaft
-
Amic-Standard
-
Benutzerdefiniert
Artikel
Ermöglicht Suche nach
      Artikeln
Artikel aktiv
Suche nach
-
ja
-
nein
-
egal
Lock-Status
Suche nach
-
ja
-
nein
Lock-Bedienerliste
Suche nach
      Bedienerkurzbezeichnungen

---

## Einrichtung und Pflege von Limitarten

Einrichtung und Pflege von
Limitarten
An dieser Stelle können die verschiedenen
Kreditversicherer eingerichtet werden. Diese werden einfach über eine
Limitart-Nummer und der Bezeichnung des Kreditversicherers gespeichert.
Einträge können neu angelegt, angesehen, bearbeitet
oder gelöscht werden. Ebenso ist es möglich, einen markierten Eintrag als
Standard-Limitart festzulegen.
Die Standard-Limitart wird immer dann benötigt, wenn
die Bearbeitung des Kreditlimits im Pfleger der Kunden-/Lieferantenstammdaten
stattfinden soll. Zu beachten ist dabei, dass hierzu der
Steuerparameter 503
– „Summierung der Kreditlimits“ -
auf dem Wert
Nein
, also keine Summierung, steht.

---

## Kundenkreditlöschkennzeichen

Kundenkreditlöschkennzeichen
Das Kreditlimitlöschkennzeichen hat genau zwei
Ausprägungen.
Aktiv: Wert gleich 0  /  teilt mit, das es
sich um ein aktives Kreditlimit handelt
Nicht aktiv: Wert ungleich 0  /  teilt mit,
das es sich um ein nicht aktives Kreditlimit handelt
Nur aktive Kreditlimits können zur Berechnung
herangezogen werden.
WICHTIG:
Private Einrichtungen, in denen das Kreditlimit
verwendet wird, müssen auf die korrekte Berücksichtigung des
Kreditlimitlöschkennzeichens überprüft werden. Hinweise hierzu findet man ggf.
auch im Fehlerprotokoll
[FEHLP].
Zur korrekten Verwendung müssen die
privaten Einrichtungen um den folgenden Wert erweitert werden:
KundKredLoekennz = 0
            für aktive
Limit
KundKredLoekennz != 0
           für nicht aktive
Limits

---

## Einrichtung der Marktkasse

Einrichtung der Marktkasse
Bei der Marktkasse kommen zwei neue, innovative
Techniken in Referenz-ERP zum Tragen:
-
Das gesamte Design erfolgt mit dem AIS-Werkzeug.
-
Die Marktkasse ist mit einem berührungsempfindlichen Bildschirm bedienbar
(Touch).
Bisher wurde AIS einerseits zur Ergänzung von
Standarddialogen eingesetzt(ADDON!). Anderseits können mit AIS kundeneigene
Dialoge realisiert werden, in denen die Verarbeitungslogik durch ein
Zusammenspiel von Datenbankfunktionen und MAKRO-Programmen implementiert wird.
Bei der Marktkasse wird AIS zur kompletten Gestaltung der Optik herangezogen,
die Verarbeitungslogik ist jedoch von Referenz-ERP vorgegeben. Hierbei sind einige
Konventionen bezüglich der Benennung der Felder sowie deren Formatierung
einzuhalten.
Die Touch-Fähigkeit setzt voraus, dass jede Form der
Eingabe durch das Berühren eines ’Buttons‘ ausgelöst werden kann. Hierzu gehört
insbesondere die Eingabe von Ziffern und Sondertasten (Eingabetaste, Minustaste,
Komma).

---

## Vorgangsimport mit openTRANS

Vorgangsimport mit openTRANS
Referenz-ERP kann nur XML im openTRANS-Standard 2.1
importieren.
Ausgangsdaten im XML-Format
Ausgangsdaten liegen unter Umständen im XML-Format
vor. XML allein ist jedoch nur die Anweisung, Daten strukturiert darzustellen.
Eine Definition, welche Daten wo zu finden ist, ist damit jedoch nicht
getroffen. Ein XML-Dokument allein ist noch nicht geeignet, Daten daraus zu
importieren.
Andere XML-Dateien können mit sog. Stylesheets zu
openTRANS-Dateien konvertiert werden. Diese Stylesheet-Dateien müssen in einem
Verzeichnis abgelegt werden, auf das der Importprozess zugreifen darf.
So können z.B. SAP-IDOCs oder andere XML zu openTRANS
konvertiert werden. Diese Stylesheets können naturgemäß keine Konverter „von der
Stange“ sein, da es in jedem Quell-System Individualitäten und verschiedene
Versionen gibt.
Interpretation der Daten
Die Daten stammen aus einer definierten Quelle. Sie
enthalten Informationen, die vom Absender übertragen werden sollen. Jedoch sind
die verwendeten Artikel- Partie- und Kundennummern die des Absenders und nicht
unbedingt die des eigenen Systems. Auch Mengeneinheiten werden in den beiden
Systemen unterschiedlich interpretiert. Aus diesem Grund ist es notwendig ein
C#-Makro zur Interpretation der Daten zu schreiben.
Das C#-Makro für den Vorgangsimport gehört zu den
Makros, die vom System aufgerufen werden und deshalb bestimmte Interfaces
implementieren müssen. Siehe auch Hilfe zu
C#-Makros
.
Dieses Makro bekommt als Parameter ein Datenobjekt des
eingelesenen Vorgangs übergeben und gibt die gelesenen Daten als eine Liste von
Datenobjekten zurück, die die zu importierenden Vorgangsinformationen enthalten.
So ist es zum Beispiel möglich, eine Bestellung
zugleich in eine Lagerumbuchung und einen Ausgangslieferschein zu wandeln, wenn
die Bestellung hier eine Lagerumbuchung als vorangehenden Schritt erfordert.
Die erwähnten Datenobjekte, die als Ergebnis des
Makros erstellt werden, ähneln nicht zufällig der Dat
[...]


---

## PayPal/Freier Datenimport

PayPal/Freier Datenimport
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Direktsprung
[ECL]
Der "Freie Datenimport" und der PayPal Import
unterscheiden sich nur in wenigen Punkten. Für PayPal-Kontoauszüge im CSV-Format
sind das Dateiformat (*.CSV) und die Datenbankprozedur von Branchen-ERP vorgegeben. Beim
"Freien Datenimport" muss der Anwender das Dateiformat und die private
Datenbankprozedur selbst festlegen.
Schritt 1: Lizenzen
Für das Einspielen von PayPal-Kontoauszügen wird neben
der
e-Clearing-Lizenz eine PayPal-Lizenz
benötigt. Nutzt man den "Freien
Datenimport", so ist die
Freier D
atenimport
Lizenz
zusätzlich zur e-Clearing-Lizenz notwendig.
Schritt 2: Einrichtung
In den
e-Clearing Optionen
F10
werden alle Einrichtungen vorgenommen
werden. Hier werden PayPal und der "Freie Datenimport" als
Zahlungsdienstleister
angelegt. Außerdem können dem
Zahlungsdienstleister eine Hausbank und ein
Gebührenkonto
sowie weitere dem
Zahlungsdienstleister betreffende Optionen zugeordnet werden. Die Angabe einer
Hausbank sowie die private Datenbankprozedur beim "Freien Datenimport" sind
zwingend erforderlich.
Schritt 3: Kontoauszug herunterladen
PayPal
Für
PayPal
gilt folgendes: Die Kontoauszüge
sind auf der Website von PayPal unter dem Punkt “Abrechnungen” > “Monatliche
Kontoauszüge” als .csv-Datei herunterzuladen.
Freier Import
Wo die Daten des "Freien Datenimport" herkommen muss
hausintern dokumentiert werden.
Schritt 4: Kontoauszug in Referenz-ERP importieren
Mithilfe der Funktion
Datei
laden
können die Kontoauszüge in Referenz-ERP eingespielt werden.
PayPal
Dazu wird die Funktion
PayPal Datei laden
und anschließend die zu
importierende CSV-Datei ausgewählt. Vor dem Einspielen der PayPal-Kontoauszüge
werden folgende Sachverhalte geprüft:
1.
Wurde dem Zahlungsdienstleister eine Hausbank zugeordnet? Verfügt die Hausbank
über ein Konto für die Finanzbuchhaltung?
2.
Soweit die Währung geliefert wird, wird geprüft, ob die Währung der Buchwährung
ent
[...]


---

## Publikationen

Publikationen
Hauptmenü
Filialsystem
Stammdaten
Publikationen
oder Direktsprung [
PUB
]

---

## Publikationen / Subskriptionen

Publikationen / Subskriptionen
Eine genaue Übersicht der in der Replikation
enthaltenen Publikationen und Subskriptionen erhalten Sie über Sybase Central in
der verwendeten Datenbank.

---

## Sybase Umstellung (SPA 1013)

Sybase Umstellung (SPA 1013)
In neueren Systemen wie Rosi und Eddyson werden die
Profile der EDI Übertragung per Kundenzuordnung vorgenommen. Damit die alten
Einrichtungen auch noch ohne Umstellung funktionieren, kann hier die
Profilerkennung ausgewählt werden.

---

## Lesen der Teildispositionseinstellungen aus richtiger Unterklasse (SPA 1053)

Lesen der Teil
dispositionseinstellungen aus
richtiger Unterklasse (SPA 1053)
In der Vorgangsunterklasse werden Werte wie
•
Mengenüberziehung zulassen
•
Mengenüberziehung erledigt Beleg
•
Teildisponierte Position editierbar
gepflegt.
Diese werden aus der Unterklasse 0 gezogen, wenn der
SPA aktiviert wurde (Ja). Dies ist die Standardeinstellung.
Ist der SPA deaktiviert (Nein), so können und müssen
die Werte auf der Vorgangsunterklasse einzeln festgelegt werden.
Achtung:
Wird der Steuerparameter auf „
Nein
“ gestellt,
so müssen die Einstellungen für die Teildisposition auch in die richtige
Unterklasse eingetragen werden, sonst kann es passieren, dass die
Teildisposition sich nicht mehr so verhält wie vor der Umstellung des
Steuerparameters.

---

## Edi-Profil-Lizenz(SPA1054)

Edi-Profil-Lizenz(SPA1054)
Lizenz für die Anzahl der erstellbaren
EDI-Profile.

---

## Zahlungsbedingung aus Eingangsmappe (SPA 1067)

Zahlungsbedingung aus Eingangsmappe (SPA 1067)
Der Steuerparameter 'Zahlungsbedingung aus
Eingangsmappe' regelt die Behandlung der Zahlungsbedingung bei der Erfassung von
Eingangsrechnungen und Eingangsgutschriften mit Datenübernahme aus der
Eingangsmappe.
Ist die Einstellung für die jeweilige Belegart
(Eingangsrechnung, Eingangsgutschrift oder beide) freigegeben, so wird die
Zahlungsbedingung aus der Eingangsmappe mit dem dort angegebenen Skontosatz
übernommen. Valuta- und Skontodatum werden, soweit es der Zahlungsbedingungstyp
zulässt, ebenfalls übernommen.

---

## Schnittstelle-Landdata-Lizenz (SPA1077)

Schnittstelle-Landdata-Lizenz (SPA1077)
Lizenz für die Nutzung der Landdata-Schnittstelle.

---

## Kreditlimitverwaltung-Lizenz (SPA1099)

Kreditlimitverwaltung-Lizenz (SPA1099)
Lizenz für die Kreditlimitverwaltung.

---

## GFK-Schnittstelle-Lizenz (SPA1115)

GFK-Schnittstelle-Lizenz (SPA1115)
Lizenz für die GFK-Schnittstelle.

---

## Excel-Archivimport-Lizenz (SPA1127)

Excel-Archivimport-Lizenz (SPA1127)
Lizenz für den Import von
Excel-Dateien (.xlsx und .xlsm) als
XML
beim Archivimport.

---

## Leerzeichen bei Zahlungsbedingungstext entfernen (SPA 1148)

Leerzeichen bei Zahlungsbedingungstext entfernen (SPA
1148)
Standardmäßig werden die einzelnen Werte im
Zahlungsbedingungstext mit Leerzeichen aufgefüllt, wenn diese kleiner als die
angegebene Länge sind. Dieses Verhalten lässt sich abschalten, indem man den
Steuerparameter auf „Ja“ stellt.

---

## Freier Import Eclearing Lizenz(SPA1151)

Freier Import Eclearing Lizenz(SPA1151)
Lizenz, um den freien Import im eClearing-Modul nutzen
zu können. Der freie Import ermöglicht es dem Anwender, Dateien per privater
Datenbankprozedur einzuspielen und alle Funktionalitäten des eClearing-Moduls
anzuwenden.

---

## eRechnung Lizenz(SPA1152)

eRechnung Lizenz(SPA1152)
Lizenz, um eRechnung freizuschalten. eRechnung ist die
Möglichkeit, Rechnungsbelege im Format UBL2.1 als sog. eRechnung zu
exportieren.

---

## eRechnung editieren (SPA 1153)

eRechnung editieren (SPA 1153)
Mit diesem SPA wird das verhalten eingestellt, das
Referenz-ERP zeigt, wenn eine Rechnung geöffnet werden soll, für die ein
eRechnungs-Export erstellt wurde.
Einstellung
Bedeutung
Nein
Editiersperre - Die Editiersperre
      kann durch Rücksetzen des Exports aufgehoben werden.
Warnung
Vor
      dem Öffnen des Belegs wird gewarnt, dass der Beleg bereits zu einer
      eRechnung exportiert wurde.
Ja
Der
      Beleg darf beliebig editiert werden

---

## Preis je Gebinde unabhängig von Faktoren(SPA 125)

Preis je Gebinde unabhängig von Faktoren(SPA 125)
Bei „Ja“ wird bei der Preisberechnung das Gebinde als
eine Einheit aufgefasst (keine Auflösung der Gebindefaktoren und Umrechnung in
die Ergebnismengeneinheit).

---

## Abteilungs-Zuordnung je Bedienerklasse(SPA 176)

Abteilungs-Zuordnung je Bedienerklasse(SPA 176)

---

## Gebindeanzahl UND Menge = Faktor rechnen(SPA 207)

Gebindeanzahl UND Menge = Faktor rechnen(SPA 207)
Spezialbehandlung bezüglich der Mengenberechnung. Bei
„Ja“ wird der erste Gebindefaktor aus den anderen Angaben errechnet, sobald man
die Gebindemenge (Ergebnismenge) eingibt  und die Gebindeanzahl  nicht
0 ist.

---

## Valutadatum im Kontenblatt(SPA 274)

Valutadatum im Kontenblatt(SPA 274)
Beim Erstellen eines Kokores wird, wenn dieser
Steuerparameter auf „Ja“ steht, je nach Eintrag in den Zahlungsbedingungen
entweder das Valutadatum der Belege aufs mittlere Valuta oder aufs
Kontoblattdatum gesetzt.

---

## Korrektursperre bei Importdaten(SPA 322)

Korrektursperre bei Importdaten(SPA 322)
Dieser Parameter ist für automatisch erfasste Belege
gedacht, die im Allgemeinen nicht mehr von Bedienern verändert werden
dürfen.

---

## Bezugsdatum für Steuerermittlung(SPA 332)

Bezugsdatum für Steuerermittlung(SPA 332)
Der SPA 332 zieht lediglich das Lieferdatum aus dem
Vorgangstamm heran. In den Positionen anders lautende Daten werden nicht
berücksichtigt.
Auch bei Teil-/Mehrfachdispo werden die Lieferdaten
der Warenpositionen nicht zur Abgrenzung herangezogen. Es gilt das Lieferdatum
im Vorgangstamm, i. a. dann identisch mit dem Rechnungsdatum.
Bei Sammelrechnungen führen unterschiedliche
Steuergültigkeitsdaten zu einer Trennung der Belege.

---

## Datev-Export-Schnittstelle-Lizenz(SPA 380)

Datev-Export-Schnittstelle-Lizenz(SPA 380)
Lizenz für Datev-Export-Schnittstelle.

---

## Zahlungsbedingung Oberkunde/Zahlungspflichtiger(SPA 392)

Zahlungsbedingung Oberkunde/Zahlungspflichtiger(SPA 392)
Hier kann aktiviert werden, ob die Zahlungsbedingung
des Oberkunden oder des Zahlungspflichtigen gezogen wird. Es wird je nach
Einstellung  in der folgenden Reihenfolge nach der ZB gesucht:
Zunächst der Zahlungspflichtige ( falls
abweichend),
dann der Oberkunde ( falls abweichend)
zuletzt der Belegkunde.

---

## Vorgangsschnittstelle-Lizenz(SPA 452)

Vorgangsschnittstelle-Lizenz(SPA 452)
Lizenz für die Vorgangschnittstelle.

---

## eClearing-Lizenz (SPA 461)

eClearing-Lizenz (SPA 461)
Lizenz für das Modul „eClearing“.

---

## Gewichtsberechnung komplett(SPA 469)

Gewichtsberechnung komplett(SPA 469)
Bei Einstellung „Ja“ wird die Berechnung des Gewichtes
in den Warenposition mit kompletter Umrechnung der Menge in die zugehörige
Grundmengeneinheit durchgeführt. Bei „Nein“ wird lediglich die erfasste Menge
mit dem Gewicht aus dem Artikelstamm multipliziert.

---

## Standard-Provisionierungsformel(SPA 47)

Standard-Provisionierungsformel(SPA 47)
Hier kann hinterlegt werden, welcher Provisionstyp
während der Provisionierung gezogen werden soll, wenn in den Provisionsmerkmalen
„Standard-Provisionsberechnung“ gesetzt ist.

---

## DSD-Gewichtsberechnung komplett(SPA 470)

DSD-Gewichtsberechnung komplett(SPA 470)
Bei Einstellung „Ja“ wird die Berechnung des Gewichtes
für die DSD-Ermittlung mit kompletter Umrechnung der Menge in die zugehörige
Grundmengeneinheit durchgeführt. Bei „Nein“ wird lediglich die erfasste Menge
herangezogen.

---

## Gutschrift wechselt Zahlungsbedingung(SPA 531)

Gutschrift wechselt Zahlungsbedingung(SPA 531)
Bei „Ja“ wird bei Umwandlung einer Rechnung in eine
Gutschrift oder bei der Neuerfassung die zur Gutschrift gehörende
Zahlungsbedingung gezogen.
Achtung: Da sich hierbei auch die Konditionen
ändern, sollte zur kompletten Aufhebung einer Rechnung eine Stornorechnung
anstelle einer Gutschrift erzeugt werden!

---

## Oberkontentrennung S/H (externe Ausw.)(SPA 542)

Oberkontentrennung S/H (externe Ausw.)(SPA 542)
Ermöglicht die Trennung der Oberkonten nach Soll und
Haben (Pflege im Sachkontenstamm). Die getrennten Summen werden nur durch eine
Neuberechnung zu den angegebenen Perioden erzeugt. Die Werte können in der
Anwendung „Externe Oberkontenauswertung“ angezeigt und exportiert werden.

---

## Fakt. Einheiten nachkalk. EDI/Metro(SPA 550)

Fakt. Einheiten nachkalk. EDI/Metro(SPA 550)

---

## Rechnungstrennung durch Zahlbednummer(SPA 568)

Rechnungstrennung durch Zahlbednummer(SPA 568)
Der Steuerparameter „Rechnungstrennung durch
Zahlungsbed.“ trennt Belege  anhand der ermittelten Valutadaten unabhängig
davon, ob sich die Zahlungsbed. Nummern unterscheiden.
Dieser Parameter trennt Belege, wenn sich die
Zahlungsbedingungsnummer unterscheidet (wenn  „JA“).

---

## Datenbestandspflege im Mandantenserver(SPA 628)

Datenbestandspflege im Mandantenserver(SPA 628)
Bei „Ja“, „*“ oder „?“ wird das Modul
Datenbestandspflege (DBP) periodisch vom Mandantenserver aufgerufen. Das Modul
prüft dabei selbstständig alle notwendigen Startbedingungen wie etwa
Einzelplatzmodus oder zeitabhängige Laufeinschränkungen.
Parameter:
0 = „--“: Start nicht zulässig
1 = „ja“: Start zulässig mit Prüfbedingungen
2 = „*“: Start auch bei noch anderen angemeldeten
Referenz-ERP-Benutzern möglich
3 = „?“: wie * und zusätzlich Start auch bei noch
vorhandenen unbearbeiteten Mandantenserver Aufträgen möglich

---

## Waagemaske Kreditlimit(SPA 667)

Waagemaske Kreditlimit(SPA 667)
Mit diesem Steuerparameter kann eingestellt werden, ob
eine Kreditlimitüberprüfung an der Waage durchgeführt werden soll.

---

## Waagemaske Kreditlimit disponierte Menge(SPA 690)

Waagemaske Kreditlimit disponierte Menge(SPA
690)
Mit diesem Steuerparameter kann eingestellt werden, ob
die disponierte Menge bei der Kreditlimit Überprüfung mit berechnet werden
soll.

---

## Ladeschein ins Kreditlimit einberechnen(SPA 695)

Ladeschein ins Kreditlimit einberechnen(SPA 695)
Bei „Nein“ werden die Ladescheine nicht mit in das
Kreditlimit einberechnet. Bei „Ja“ werden Ladescheine mit in das Kreditlimit
einberechnet.

---

## Mindestanzahl Vorstart Elara für Autostart (SPA 706)

Mindestanzahl Vorstart Elara für Autostart (SPA
706)
Mit diesem Steuerparameter kann eingestellt werden,
wie oft ein Bediener das Hilfsprogramm Elara aufgerufen haben muss, bevor dies
beim Referenz-ERP-Start automatisch durch eine Veränderung des Eintrags .Net Vorstart
im Bedienerstamm vorgestartet wird, um lange Vorlaufzeiten beim ersten Start
eines Elara-AddIns zu vermeiden.

---

## OpenTRANS ®-Lizenz (SPA 721)

OpenTRANS ®-Lizenz (SPA 721)
Steuert die Sichtbarkeit der Optionen für die
openTRANS-Schnittstelle zum Export / Import von Vorgängen mit dem
XML-basierenden Format openTRANS.

---

## Name Sicherheit Login aktivieren (SPA 769)

Name Sicherheit Login aktivieren (SPA 769)
Hier wird angegeben ob das Referenz-ERP-System das
Standard-Login-verfahren von Referenz-ERP durch die Vorgaben in Name Sicherheit im
Bedienerstamm übersteuert. Mit Einstellung dieses SPA’s wird keinem Bediener
mehr ein Referenz-ERP-Login gestattet, der nicht auch über einen Eintrag in „Name
Sicherheit“  verfügt.

---

## Kreditlimit bei Ladescheine in Vorgangsmappe verrechnen(SPA 783)

Kreditlimit bei Ladescheine in Vorgangsmappe verrechnen(SPA 783)
Dieser Steuerparameter ist abhängig vom
Steuerparameter „Ladeschein ins Kreditlimit einberechnen“
(695)
. Wenn beide Steuerparameter auf „Ja“ stehen,
werden bei der Kreditlimitberechnung die Lieferungen mit den Ladescheinen
verrechnet, soweit dieses sich innerhalb einer Vorgangsmappe befinden.

---

## Private Kredit Funktion (SPA 812)

Private Kredit Funktion (SPA 812)
Dieser Steuerparameter entscheidet, ob eine private
Funktion an Stelle der AMIC_FUNC_KREDIT verwendet werden soll.
•
Spalte „Verwendung“: Ja / Nein – Standard = Nein
•
Spalte „private Funktion“: Enthält den Namen der privaten Prozedur

---

## SQL-Editor (SPA 814)

SQL-Editor (SPA 814)
In diesem Steuerparameter kann der Referenz-ERP-Editor für
SQL-Texte und Anwendungen für definierte eingeschaltet werden.

---

## Zahlungsbedingungen für den Kunden beim Washout (SPA 816)

Zahlungsbedingungen für den Kunden beim Washout (SPA 816)
Mit diesem Steuerparameter kann eingestellt werden,
welche Zahlungsbedingung für den Kunden beim Washout gilt.

---

## Zahlungsbedingungen für den Lieferant beim Washout (SPA 817)

Zahlungsbedingungen für den Lieferant beim Washout (SPA 817)
Mit di
esem Steuerparameter kann eingestellt werden, welche
Zahlungsbedingung für den Lieferant beim Washout gilt.

---

## Zahlungsbedingungen für den Kunden beim Circle (SPA 818)

Zahlungsbedingungen für den Kunden beim Circle (SPA 818)
Mit diesem Steuerparameter kann eingestellt werden,
welche Zahlungsbedingung für den Kunden beim Circle gilt.

---

## Zahlungsbedingungen für den Lieferant beim Circle (SPA 819)

Zahlungsbedingungen für den Lieferant beim Circle (SPA 819)
Mit diesem Steuerparameter kann eingestellt werden,
welche Zahlungsbedingung für den Lieferant beim Circle gilt.

---

## Belegversand Dateiname Funktion (SPA 822)

Belegversand Dateiname Funktion (SPA 822
)
Hier kann pro Bediener festgelegt werden, welche
Datenbankfunktion für die Ermittlung des Dateinamens der versendeten Datei im
Belegversand dienen soll.

---

## Belegimport (SPA 829)

Belegimport (
SPA 829
)
In diesem Steuerparameter können Optionen für den
Belegimport eingestellt werden.
Zur Einstellung stehen verschiedene Typen zur
Verfügung.
Typ
Wert
IMPORTPFAD
Standardpfad für den Import der
      XML-Daten. Der Pfad muss dabei auf einen gültigen Pfad auf dem
      Datenbankserver zeigen.
IMPORTPROZEDUR
Alternative Datenbankfunktion für
      den Import der XML-Daten.
KUNDE
Standardkundennummer für die
      Eingangsrechnungsbelege.
MAKRO_KOPF_START
Hier
      kann ein Makro eingetragen werden, welches vor der Funktion „StartVorgang“
      aufgerufen wird.
MAKRO_KOPF_ENDE
Hier
      kann ein Makro eingetragen werden, welches nach der Funktion
      „StartVorgang“ aufgerufen wird.
MAKRO_POSI_START
Hier
      kann ein Makro eingetragen werden, welches vor der Funktion „PositionNeu“
      aufgerufen wird.
MAKRO_POSI_ZWISCHEN
Hier
      kann ein Makro eingetragen werden, welches nach der Funktion „PositionNeu“
      und vor „PositionAdd“ aufgerufen wird.
MAKRO_POSI_ENDE
Hier
      kann ein Makro eingetragen werden, welches nach der Funktion „PositionAdd“
      aufgerufen wird.
UNTERKLASSUMSCHLUESSEL
Hier
      wird die Klasse des Umschlüsselwerks eingetragen, welche eine Zuordnung
      zwischen dem Referenz-ERP Lager und der Vorgangsunterklasse herstellt. Ist diese
      Ausprägung nicht gesetzt, so wird die Unterklasse 0 genommen.
BELEGDATUMTODAY
Mit
      diesem Steuerparameter kann eingestellt werden, ob die Referenz-ERP
      Eingangsrechnung das Belegdatum der Terresrechnung erhalten soll. Oder ob
      die Referenz-ERP Eingangsrechnung das Tagesdatum erhält.
Wert
Bedeutung
0
Referenz-ERP
            Eingangsrechnung erhält das Datum der Terres
        Rechnung.
1
Es wird das Tagesdatum
        verwendet.
Info zu Makro
Beim Aufruf der „MAKRO_KOPF…“ und „MAKRO_POSI…“ werden
folgende Parameter aufgerufen.
Parameter
Beschreibung
PARAM1
Dieser Parameter enthält den Modus,
      durch welchen das Makro aufgerufen wurde. Mögliche Werte stehen
[...]


---

## Versionierung im Archiv-Editor (SPA 848)

Versionierung im Archiv-Editor (SPA 848)
Word- und Excel-Dokumente können im Archiv mit Hilfe
der Funktion „Editieren“ abgeändert und wieder gespeichert werden. Wenn dabei
eine Versionierung, also keine Überschreibung der ursprünglichen Datei erfolgen
soll, so muss dieser Steuerungsparameter aktiviert sein.

---

## Belegänderungssperre durch Beteiligung von openTRANS (SPA 850)

Belegänderungssperre durch Beteiligung von openTRANS (SPA
850)
Mit diesem Steuerparameter wird festgelegt, wie die
Sperre für die Bearbeitung von openTRANS-Belegen sich verhalten soll
Wert
Verhalten
0 – keine
      Sperre
Die
      Belege können frei editiert werden. Es wird beim Druck ein neues openTRANS
      erstellt.
1 –
      nur Warnung
Es
      wird lediglich eine Warnung ausgegeben, dass bereits ein openTRANS
      erstellt wurde. Der Beleg bleibt editierbar
4 –
      Sperre für alle openTRANS-Belege
Es
      ist keine Bearbeitung von Belegen mit openTRANS möglich.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Betragsvorzeichen bei Zahlungsbedingungstext berücksichtigen (SPA 852)

Betragsvorzeichen bei Zahlungsbedingungstext berücksichtigen (SPA 852)
Bei der Ermittlung von Zahlungsbedingungstexten in
Rechnungen und Gutschriften wird als Unterscheidungskriterium grundsätzlich nur
die Vorgangsklasse ausgewertet. Mit Aktivierung dieses Steuerparameters wird
auch der Gesamtbetrag des Beleges berücksichtigt, so dass als Text der
Zahlungsbedingung z.B. bei einer Rechnung mit einem negativen Betrag der Text
der Gutschrift verwendet wird.

---

## Fehlerprotokolloptimierung aktiv (SPA 868)

Fehlerprotokolloptimierung aktiv (SPA 868)
Im Fehlerprotokoll werden standardmäßig unerledigte
Systemhinweise nicht erneut eingetragen, sondern der Zähler eines bereits
vorhandenen Systemhinweises wird hochgesetzt. (Fehlerprotokolloptimierung aktiv
= Ja)
Mit diesem Steuerparameter kann festgelegt werden, ob
weiterhin nur der Zähler der unerledigten Systemhinweise hochgezählt, oder ob
ein neuer Systemhinweis erzeugt werden soll.

---

## EDI-Datentransfer Rechenzentrum Aktivierung/Deaktivierung (SPA 909)

EDI-Datentransfer Rechenzentrum Aktivierung/Deaktivierung (SPA 909)
EDI-Datentransfer Rechenzentrum aktiv, passiv bzw.
versteckt konfigurieren

---

## EDI Nachrichtenausgang zum Provider sperren (SPA 922)

EDI Nachrichtenausgang zum Provider sperren (SPA 922)
Nachrichtenausgang zum EDI-Provider sperren

---

## EDI Nachrichteneingang vom Provider sperren (SPA 923)

EDI Nachrichteneingang vom Provider sperren (SPA 923)
Nachrichtenausgang vom EDI-Provider sperren

---

## Allgemeiner Steuerparameter für die Waage(SPA 925)

Allgemeiner Steuerparameter für die Waage(SPA
925)
An diesem Steuerparameter werden Optionen für die
Waage eingetragen.
Folgende Optionen sind verfügbar:
Option
Wert
KREDITLIMITFUNKTION
Hier
      kann eine Prozedur hinterlegt werden, die die Standard Kreditlimitfunktion
      an der Waage überschreibt. Mit dem
Steuerparameter 667(Waagenmaske
      Kreditlimit)
wird die Kreditlimitprüfung an der Waage an- und
      ausgestellt.
ARTIKELBYQUALITÄTEN
Hier
      kann eine Prozedur hinterlegt werden, die vor dem Abschließen einer
      Wiegung aufgerufen wird. Der Prozedur wird die OwaageId als
      Eingangsparameter übergeben. In dieser Prozedur können dann Daten an dem
      Owaagesatz auf Relationsebene geändert werden. Nach dem Aufruf der
      Prozedur wird die Waagenmaske mit den neuen Werten geladen. Beim Abändern
      der Daten muss sorgfältig vorgegangen werden, damit keine Inkonsistenten
      Daten erzeugt werden.
FLICHTFELDERWAAGENPROZESS
Hier
      kann eine private Prozedur hinterlegt werden, die bestimmt welche Felder
      auf der Waagenmaske als
Pflichtfelder
in Abhängigkeit des
Prozesses
markiert werden
      sollen.
SILOPOSLOESCHENBEILOESCHEWIEGUNG
Mit
      dieser Option wird eingestellt, ob beim Löschen von Wiegungen die dazu
      gehörigen Positionen aus dem Lagerverwaltungssystem / Silo ausgebucht
      werden soll
KONTRAKTABWAHLAUFTRAGSUEBERBUCHUNG
Mit
      dieser Option wird eingestellt, ob im Auftrag der Kontrakt automatisch
      abgewählt werden soll, wenn im Auftrag und in der Waage die Menge größer
      ist als die Kontraktrestmenge, damit die gesamte Kontraktrestmenge in dem
      daraus resultierenden Lieferschein / Rechnung verfügbar ist.
0 =
      deaktiviert
1 = aktiviert
WIEGETYPAENDERNBEIROHWARE
Wenn
      diese Einstellung aktiviert wird, dann wird der Wiegetyp automatisch auf
      Rohware geändert, wenn bei der normalen Warenausgangs bzw. –eingangs
      Wiegung ein Rohwarekontrakt zugewiesen wird.
0
[...]


---

## Allgemeiner Steuerparameter für die Vorgangsimportschnittstelle (SPA 928)

Allgemeiner Steuerpa
rameter für die
Vorgangsimportschnittstelle (SPA 928)
An diesem Steuerparameter werden Optionen für die
Vorgangsimportschnittstelle eingetragen.
Folgende Optionen sind verfügbar:
Option
Wert
UNTERKLASSERECHNUNG
Hier
      kann eine abweichende Unterklasse für die Rechnung hinterlegt werden. Die
      Unterklasse wird bei der Belegerzeugung ausgewertet und überschreibt die
      Unterklasse aus der Relation ImportVorgStamm. Ist in diesem
      Steuerparameter diese Option nicht hinterlegt, so wird die Unterklasse aus
      der Relation ImportVorgStamm genommen.
UNTERKLASSEGUTSCHRIFT
Hier
      kann eine abweichende Unterklasse für die Gutschrift hinterlegt werden.
      Die Unterklasse wird bei der Belegerzeugung ausgewertet und überschreibt
      die Unterklasse aus der Relation ImportVorgStamm. Ist in diesem
      Steuerparameter diese Option nicht hinterlegt, so wird die Unterklasse aus
      der Relation ImportVorgStamm genommen.
UNTERKLASSEUNBEKANNTERBELEG
Hier
      kann eine Unterklasse für einen undefinierten Vorgang hinterlegt werden.
      Beim Einspielen der Daten in die Relation ImportVorgStamm muss der
      Steuerparameter ausgewertet werden. Die Unterklasse muss dann mit dem Wert
      aus dem Steuerparameter gepflegt werden. Diese Option wird vom Standard
      nicht ausgewertet.
KLASSEUNBEKANTERBELEG
Hier
      kann eine Klasse für einen undefinierten Vorgang hinterlegt werden. Beim
      Einspielen der Daten in die Relation ImportVorgStamm muss der
      Steuerparameter ausgewertet werden. Die Klasse muss dann mit dem Wert aus
      dem Steuerparameter gepflegt werden. . Diese Option wird vom Standard
      nicht ausgewertet.
UMSCHLUESSELKUNDEDATEIIMPORT
Hier
      kann eine Umschlüsselungsklasse für den Kunden hinterlegt werden. Diese
      Option wird vom Standard nicht bedient.
BESTELLVORSCHLAEGELAGERTRENNUNG
Mit
      diesem Steuerparameter kann eingestellt werden, ob bei der Erzeugung von
      Bes
[...]


---

## Hauptmenü-Tooltip verwenden (SPA 931)

Hauptmenü-Tooltip verwenden (SPA 931)
Hier kann pro Bediener hinterlegt werden, ob die
Hauptmenü-Tooltips aktiv sind oder nicht. (Standard ist „Ja“)

---

## Herkunft der Qualitätswerte zur Berechnung von durchschnittlichen Siloqualitäten(SPA 940)

Herkunft der Qualitätswerte zur Berechnung von durchschnittlichen
Siloqualitäten(SPA 940)
Einstellung
Bedeutung
Immer aus
      Waage-Qualitäten
Es
      werden zur Berechnung der durchschnittlichen Qualitätswerte eines Silos
      immer die zugehörigen in der Waage erfassten Qualtitätswerte
      herangezogen.
Aus
      aktuellsten Rohwarebelegen
Wenn
      Rohwarebelege zum Waagenbeleg vorhanden sind, so werden hier anstatt der
      Waagequalitäten die Qualitätswerte der jeweils aktuellsten zugehörigen
      Rohwarebelege zur Berechnung der durchschnittlichen Qualitätswerte eines
      Silos herangezogen.

---

## CS-Makro Debugsession für Bediener erhalten (SPA 941)

CS-Makro Debugsession für Bediener erhalten (SPA
941)
In diesem SPA können mehrere Bediener definiert
werden, deren C#-Makros abhängig vom Bedienerkürzel statt mit der
Datenbanksession mit der hinterlegten Debug-Einstellung kompiliert werden. So
können Entwickler von Makros nach einem Neustart von Referenz-ERP auch weiter eine
externe DLL oder einen externen Code debuggen, ohne dies jeweils auf der
Makromaske einstellen zu müssen.

---

## Zahlungsbedingung - Typ ändern (SPA 951)

Zahlungsbedingung - Typ ändern (SPA 951)
Einstellung
Bedeutung
0 – Änderung immer
      erlaubt
Die
      Änderung des Zahlungsbedingungstyps ist immer erlaubt.
1 –
      Warnung bei benutzter ZB in Vorgängen
Die
      Änderung des Zahlungsbedingungstyps ist erlaubt. Es wird eine Warnung
      ausgegeben, dass der Zahlungsbedingungstyp in Vorgängen verwendet
      wird.
2 –
      Nicht erlaubt bei benutzter ZB in Vorgängen
Die
      Änderung des Zahlungsbedingungstyps ist nicht erlaubt, wenn dieser in
      Vorgängen verwendet wird.
Partien. Zusätzlich muss auch die Feldgeneration
korrekt geführt werden. Hier kann pro Bediener festgelegt werden, in welchem
Zucht/Vermehrungsbereich gearbeitet werden soll.

---

## EDI Eigenschaften (SPA 957)

EDI Eigenschaften (SPA 957)
Verschiedenste Ausprägungen der Standard EDI
Eigenschaften (auch OpenTrans)

---

## GETPAID Schnittstellen Option (SPA 959)

GETPAID Schnittstellen
Option (SPA 959)
In diesem Steuerparameter werden Optionen für die
Schnittstelle mit GETPAID hinterlegt. Unter anderem das Exportverzeichnis, in
dem die Exportdateien abgelegt werden sollen.

---

## Buchsperre setzen für Bedienerklasse (SPA 971)

Buchsperre setzen für Bedienerklasse (SPA 971)
Hier in diesem Steuerparameter kann man die
Bedienerklassen eintragen, für die bei der Erfassung von
Finanzbuchhaltungsbelegen sofort die Buchsperre gesetzt werden soll.

---

## Bitzer Fehlerprotokoll (SPA 970)

Bitzer
Fehlerprotokoll (SPA 970)
Bei der Datenübertragung vom Bitzer System an die
Waage können ggf. Schnittstellenprobleme auftraten. Hiermit können diese
Probleme (weil unwichtig) NICHT ins Fehlerprotokoll übernommen werden.

---

## Webportal-Bedienerklassen(SPA 984)

Webportal-Bedienerklassen(SPA 984)
Komplexer Steuerparameter
Ein Eintrag mit der Bezeichnung
‚WebUser‘
sorgt
dafür, dass Bediener in der WebPortal-Datenbank mit der angegebenen
Bedienerklasse erzeugt werden.

---

## Webportal-Optionen(SPA 994)

Webportal-Optionen(SPA 994)
Komplexer Steuerparameter.
Hier können über das Systemformat „WebPortOpt“
verschiedene Optionen für das Webportal angegeben werden.
•
BedienerId ab:
Untere Grenze, ab welcher Nummer Bediener
für das Webportal im Bedienerstamm angelegt werden sollen
•
Mailtyp:
Typ unter dem die Mail-Adressen der
WebPortal-Kunden im Kundenstamm in der Hauptanschrift für das Portal gespeichert
sind. Ist diese Option nicht eingerichtet oder wird unter dem angegebenen
Mailtyp keine Mailadresse gefunden, so wird, falls eingerichtet, die unter dem
Mailtyp 1 (Standard) eingerichtete Mailadresse gesucht.
•
Versandprofilnummer:
Nummer/Id des Versandprofiles
aus dem Versandprofilstamm für Mailversand aus dem Webportal
•
Bestellung Vorgangsklasse:
Vorgangsklasse für die
Bestellungen/Bestellanfragen, die aus dem WebPortal heraus in Referenz-ERP generiert
werden. Ist in dieser Option keine Vorgangsklasse zugeordnet, so wird ein
Vorgang der Klasse 400 (Auftrag) erzeugt.
•
Bestellung Unterklasse:
Vorgangsunterklasse für die
Bestellungen/Bestellanfragen, die aus dem WebPortal heraus in Referenz-ERP generiert
werden. Diese Option muss eingerichtet sein.
•
KennwortVergessen-MailBody-Prozedur:
Name einer privaten
Prozedur zum ermitteln des Mailbodys für die
Kennwortvergessen-Funktion.
•
Dokumente ab Datum:
Ist hier ein Datum angegeben, so werden
im WebPortal nur Vorgänge und Dokumente angezeigt, deren Belegdatum größer oder
gleich dem angegebenen Datum ist. Ist hier kein Datum angegeben, werden nur
Belege des laufenden Kalenderjahres berücksichtigt.
•
Webportal-Archiv-Daten-Filter-Funktion:
Hinterlegen Sie
hier eine private Funktion zum Filtern von Archivdaten, die im Webportal
angezeigt werden sollen.
•
Webportal-Archiv-Gruppentyp:
Hinterlegen Sie hier den Typ
aus dem Anwendungsformat AF_FA_GRUPPE, welcher für die Kennzeichnung von
Webportal-Dokumenten angegeben wurde.
•
Rohware-Details-NurErsteWaPos:
Ist für diese Option einer
der Werte ‚Ja‘ oder ‚1‘ eingetragen,
[...]


---

## SMTP - Mailversand (SPA 999)

SMTP - Mailversand (SPA 999)
Es kann entschieden werden, ob der Mail Versand aus
Referenz-ERP heraus per Standard SMTP (port 25) oder per MAPI Outlook abgewickelt
werden soll. Bei der MAPI Schnittstelle muss der Datenbankserver im
Benutzer-Account des passenden Outlook Kontos arbeiten und die Sicherheitsstufe
des Outlook muss auf „Script zulassen“ eingestellt sein. Weiterhin kann auch die
.NET Schnittstelle genutzt werden, um direkte SMTP Mail zu versenden.

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

## Zu-/Abschläge

Zu-/Abschläge
Definition lt. Wikipedia:
Die
Zulage
(auch
Zuschlag
) ist ein
spezieller
Tarif
,
der für Sonderleistungen zu entrichten ist, die über die normalen
Vertragsbedingungen hinausgehen. Im Rahmen von
Arbeits-
oder
Dienstverhältnis handelt es sich um eine Sonderzahlung bzw. einen finanziellen
Bonus
, der bei
Vorliegen bestimmter Voraussetzungen von der Beschäftigungsbehörde oder dem
Arbeitgeber
als Ausgleich
besonderer Umstände oder Belastungen gewährt werden kann. Auch bei der Benennung
besonderer
Sozialleistungen
und
Subventionen
wird der
Ausdruck häufig verwendet.
Verwendung in Referenz-ERP
Neben dem Zuschlag als zusätzlichem Preisaufschlag für
definierte Konditionen gibt es analog den Abschlag, der eine Preisminderung für
definierte Konditionen festlegt.

---

## Abkündigung: EDI – Spezielle Lösungen

Abkündigung: EDI – Spezielle Lösungen
Im Laufe der Jahre sind eine Vielzahl von
individualisierten EDI-Umsetzungen durchgeführt worden. Seit 2016 treiben wir
unser Produkt ROSIE entwicklungstechnisch immer weiter voran. ROSIE verfügt über
Konfigurationsmasken, mit denen sich EANCOM-Standard Strukturen abbilden lassen.
ROSIE ist komplett in die Vorgangsbearbeitung des Standardsystems integriert.
ROSIE liest und erzeugt direkt EANCOM-Dateien der Version 96a und 01b. Sie
benötigen für die Erzeugung dieser Dateien keinen zusätzlichen Provider, außer
einer Ihrer Kunden verlangt andere, als oben angegebene EANCOM-Versionen. Sie
ersparen sich hiermit zum einen die Kosten für die Provider wie auch den
zusätzlich Klärungsaufwand, der im Viererverhältnis „Ihr Kunde“, „Sie“, „Amic“
und „Provider“ zwangsläufig gegeben ist. „Ihr Kunde“ schickt ihnen bei Problemen
das Segment, welches nicht okay ist. Man erkennt direkt auf Referenz-ERP Seite wo das
Problem liegt und muss nicht mehr den Support des Providers konsultieren. Nur
der Support des Providers kann einem sagen, an welcher Stelle der
Inhouse-Schnittstelle eine Veränderung vorgenommen werden muss, damit die Datei
korrekt an den Kunden verschickt wird.Es gab mehre Ansatzpunkte in der
VergangenheitHaben Sie einen Eddyson-Vertrag und verschicken Sie EDI-Nachrichten
über den Direktsprung EDI? Wenn ja, sind Sie von diesem Punkt betroffen. Dieses
Verfahren wird mit Referenz-ERP 64 Bit nicht mehr unterstützt. Sprechen Sie unseren
Vertrieb an.Es gab andere Umsetzungen, die über den Provider EDDYSON gelaufen
sind. Sofern diese Umsetzungen nach der 64 Bit Umstellung laufen, stellt die
Verwendung kein Problem dar. Diese Entwicklungen wurden individuell für Kunden
nach den individuellen jeweiligen Bedürfnissen aufgebaut. Zur Anwendung kamen
MAKRO 1.0 oder MAKRO 2.0 Funktionalitäten, um einen Vorgang auszulesen und in
die Tabelle „StdDat“ oder in „XML“ Strukturen zu schreiben oder umgekehrt Daten
aus dieser Tabelle / XML zu
[...]


---

## Abkündigung: JRCON-Online Waage

Abkündigung: JRCON-Online Waage
Seit vielen Jahren verfügt Referenz-ERP über eine
Online-Waage die vielfach im Einsatz ist. Die JRCON-Online Waage ist eine
Entwicklung, die auf Visual Basic Basis betrieben wurde. Hierfür gibt es von
Seiten aktueller Betriebssysteme nur noch bedingt Unterstützung. Die Betreuung
und der Support der JRCON-Online Waage wird komplett eingestellt. Uns ist nicht
bekannt, dass diese Lösung noch im Einsatz ist. Bei mehr als 700 aktiven Kunden,
können wir es allerdings nicht mit 100 prozentiger Wahrscheinlichkeit sagen.
Sollten Sie diese Lösung im Einsatz haben, sprechen Sie unseren Vertrieb an.
Tags:
Abkündigung

---

## Abgelaufene Kreditlimits

Abgelaufene Kreditlimits
Laufen Kreditlimits aufgrund des Erreichens des
Ablaufdatums ab, so dürfen diese Kreditlimitbeträge natürlich auch nicht mehr
zur Berechnung des aktuellen Kreditlimits herangezogen werden.
Ein Prozess, gesteuert über den Mandantenserver, sucht
solche abgelaufenen Kreditlimits und aktualisiert die entsprechenden Einträge
automatisch.

---

## Abgrenzung des Archives

Abgrenzung des Archives
Die Archivierung ins Dateisystem bedient sich der
sogenannten AMICAR-Methode. Dabei werden die Belege nach bestimmten
Namenskonventionen ins Dateisystem abgelegt und eine dazugehörige Steuerdatei
abgelegt.
Beispiel:
Die Txt-Dateien enthalten jeweils die textuelle
Darstellung der Belege, in der AR-Datei liegen die Steuerinformationen der
Belege. Dabei wird pro Wirtschaftsjahr und Periode immer eine neue AR-Datei
angelegt. Würde keine Abgrenzung aktiv sein, dann würden die AR-Dateien strikt
nach Jahr und Monat benannt werden.

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

## Referenz-ERP Hinweis Bildschirm

Referenz-ERP Hinweis Bildschirm
Hauptmenü
Administration
Firmenkonstanten
Bedienerbezogenes Hinweissystem
Direktsprung
[HINW]
Der Hinweis Bildschirm wird dafür verwendet, um
wichtige Meldungen an den Bedienern beim Einstieg in Referenz-ERP anzuzeigen, welche
dann vom Bediener gelesen werden müssen. Solange die Hinweise vom Bediener als
nicht gelesen markiert worden sind, werden diese immer wieder beim Anmelden in
Referenz-ERP neu angezeigt.
Die Informationen und Hinweise werden von Branchen-ERP oder in
Eigenregie für interne Zwecke erstellt und gepflegt. Die Meldungen und Hinweise
stammen entweder aus der Hilfe, aus dem Archiv oder von einem Hyperlink, der auf
ein HTML-Dokument zeigt.
Bei Informationen und Hinweisen, die den Besitzer Branchen-ERP
gehören, kann der Kunde nur das Gelesen-Kennzeichen zurücksetzen, aber diese
Informationen oder Hinweise nicht löschen.
Um einen neuen Hinweis zu erstellen, wird unter
[HINW]
die Taste
F8
gedrückt.
Mit
F9
können vorher ausgewählte Hinweise für alle Bediener, welche diesen Hinweis
erhalten sollten, als gelesen markiert werden.

---

## Allgemein

Allgemein
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Aktionärsverwaltung
oder Direktsprung
[AKTIO]
Mit der Aktionärsverwaltung in Referenz-ERP kann ein
Unternehmen einfach und unkompliziert seine Aktionäre verwalten. Es können
Aktionäre angelegt, editiert und gelöscht werden. Für die Aktionäre können
Aktientransaktionen erfasst werden und es können für Zeiträume Dividenden
festgelegt werden, die an die Aktionäre ausgeschüttet werden können. Das heißt,
dass Buchungen für die gezahlten Dividenden in der Finanzbuchhaltung erzeugt
werden. Für jeden Aktionär kann dann eine Steuerbescheinigung über die gezahlte
Dividende ausgedruckt werden.
Um die Aktionärsverwaltung zu verwenden, sollten
zuerst die Unternehmensdaten wie Aktienanzahl, Stammkapital und Nominalwert
erfasst werden [siehe
Die
Unternehmensdaten einrichten/verwalten
]. Danach können Aktionäre angelegt
und für diese Aktientransaktionen erfasst werden [siehe
Aktionäre verwalten
und
Aktientransaktionen / Die Historische
Tabelle
]. Es gibt diverse Anzeigemöglichkeiten für die Aktionäre und ihre
Bestände und es können Kundenbescheinigungen mit einer Bestandsübersicht
erstellt werden [siehe
Kundenbescheinigung
].
Am Ende eines Wirtschaftsjahres eines Unternehmens
werden Dividenden an die Aktionäre ausgeschüttet. Dazu sollten zuerst einige
Angaben wie Höhe pro Stückaktie, Zahldatum und Zeitraum gemacht werden [siehe
Dividenden verwalten
]. Dann kann
das Wirtschaftsjahr bzw. die Dividende abgeschlossen und Buchungsbelege in der
Finanzbuchhaltung erzeugt werden [siehe
Dividenden abrechnen
]. Nach Abschluss
eines Wirtschaftsjahres kann für einen Aktionär eine Steuerbescheinigung für
dieses Wirtschaftsjahr ausgedruckt werden. Es besteht dann auch die Möglichkeit
zum Ausdruck einer Zweitsteuerbescheinigung [siehe
Steuerbescheinigung/Zweitsteuerbescheinigung
].
Folgende Ansichten stehen dem Benutzer zur
Verfügung:
•
Aktionärsübersicht
(mit folgenden speziellen Funktionen)
o
(Aktionär)
Neu
[siehe
Aktion
[...]


---

## Archiv Ansehen

Archiv Ansehen
Archivierte Belege und Dokumente zur Ansicht
bringen.
Um nachfolgende Erläuterungen verstehen zu wollen,
muss man etwas über sogenannte Mimetypen wissen. Umfassende Informationen
bekommt man etwa bei
http://de.wikipedia.org/wiki/Multipurpose_Internet_Mail_Extensions
und folgende.
Das Formulararchiv speichert durchweg binäre
Informationen, die für sich allein keinen Informationsgehalt darstellen. Man
benötigt eine weitere Klassifizierung, um was es sich bei den Daten handelt, um
sinnvoll damit interagieren zu können. Es wird also so etwas wie die Extension
zusätzlich benötigt, um diese Informationen dann entsprechend
weiterzuverarbeiten. Da Extensionen aber nicht immer hinreichend sind (so können
z.B. *.doc - Dateien von ganz verschiedenen Programmen stammen!), verwendet
Referenz-ERP von Anfang an das etwas umfassendere Konzept der Mime-Typen. Siehe z.B.
http://www.webmaster-toolkit.com/mime-types.shtml.
Referenz-ERP und das Formulararchiv „kennen“ folgende Typen,
die in der Relation AMIC_Mime hinterlegt sind und zum Zeitpunkt der Drucklegung
folgenden Umfang besitzt:
Diese Definitionen werden von Branchen-ERP ausgeliefert und
werden in späteren Versionen frei konfigurierbar zur Verfügung gestellt.
Die Blob-Spalte weist das Ansichts-System an, die
Darstellung im Referenz-ERP-eigenen Rahmen durchzuführen, sobald der Mimetyp als
nicht-blob-fähig gekennzeichnet ist.
Die PDF-Kennung ist selbsterklärend und informiert das
Referenz-ERP-System, welcher Mimetyp intern als PDF zu behandeln ist.

---

## „Archiv ansehen“

„Archiv ansehen“
Woher weiß denn das Programm eigentlich, nach welcher
Referenz-Nummer bzw. welchem Kunden es suchen soll? Ausgehend von Auswahlliste
oder Dialog können die Umgebungsparameter aus ganz anderen Quellen und
Möglichkeiten herstammen.
Referenz-ERP bedient sich eines Konzeptes, in der man über
sogenannte „Formulararchiv Ansichten“ (
Archiv-Ansicht-Definition
) definieren kann,
woher Referenz-ERP an welcher Stelle die Daten bekommt und man kann gleichzeitig für
nachfolgende Aufgaben bestimmte Umgebungsparameter festlegen.

---

## Archiv-Ansichten-Variante: Ansichten – Richtlinien

Archiv-Ansichten-Variante:
Ansichten – Richtlinien
Hauptmenü
Administration
Archiv
Zugriffssteuerung
Richtlinien
Direktsprung
[FAA]
Ansichten werden von Branchen-ERP ausgeliefert. Für Kunden
besteht die Möglichkeit diese generell zu privatisieren, aber ebenso auch pro
Bedienerklasse. Damit steht ein sehr ohnehin schon ein flexibles
Konfigurationsmodell für die Archiv-Ansichten zur Verfügung.
Eine weitere Unterstützung bieten nun zusätzlich die
sogenannten „Richtlinien“. Diese werden von Referenz-ERP einmalig ausgeliefert und
können dann individuell zur Parametrisierung der Ansichten herangezogen werden.
Die Richtlinien werden in der Anwendung „Archiv-Ansichten“ und dort in der
Variante „Ansichten-Richtlinien“ gepflegt. Sobald eine Richtlinie aktiviert wird
hat diese Vorrang vor den Einstellungen in den Branchen-ERP-Ansichten. Die privaten
Ansichten bleiben davon unberührt.
Allerdings ist es möglich mit dem SPA
„Archiv-Richtlinien in privaten Ansichten berücksichtigen“ (782) die privaten
Ansichten den Richtlinien unterzuordnen.
Im Ansichtspfleger wird signalisiert, dass Richtlinien
aktiviert sind und die entsprechenden Felder sind dunkelgeschaltet. Richtlinien
ändern die zugrunde liegenden Felder nicht.
Mit Hilfe der Richtlinien lassen sich nun auch größere
Installationen mit sehr vielen Mandanten hinsichtlich der Ansichten einfach
administrieren, dazu muss die Relation „fa_view_firma auf die jeweiligen
Mandanten verbracht werden.
Felder
Detailbezeichnung
Bezeichnung eines
      Details
Richtlinie
Aktiviert/Nicht
      aktiviert
Detailname
Technische Identifikation der
      Richtlinie
Detailwert
Der
      Wert der Richtlinie.
Hinweis: Es sind hier je nach
      Richtlinie andere Typen.
Funktionen
Ansehen
Ansehen der Details
Ändern
Ändern der Richtlinie. Es können
      Aktiv-Status und Richtlinien-Wert geändert werden.
Bereich/Profile
Detailbezeichnung
Suche in den
      Bezeichnungen
Detailname
Suche in den Detailname
Dialog
Archiv-Ansichten
      Richtlinien
De
[...]


---

## Archiv-Ansichten-Variante: Ansichten

Archiv-Ansichten-Variante: Ansichten
Hauptmenü
Administration
Archiv
Zugriffssteuerung
Ansichten
Direktsprung
[FAA]
Feld
Name
Bezeichnung der
      Archiv-Ansicht
Bedienerklasse
Zugeordnete
      Bedienerklasse.
Sind
      mehrere Ansichten gleichen Namens vorhanden, entscheidet die
      Bedienerklasse darüber, welche Archiv-Ansicht zur Verfügung gestellt
      wird.
Somit ist es möglich, jeweils
      verschiedenen Bedienerklassen auch bestimmte Archiv-Ansichten zukommen zu
      lassen.
Die
      Bedienerklasse -1 steht stellvertretend für alle
      Bedienerklassen.
Die
      Bezeichnung dieser „Bedienerklasse“ ist „
Defaultklasse
      Kunden
“
Bedienerklassenbezeichnung
Bezeichnung der
      Bedienerklasse
Besitzer
Branchen-ERP
:
Auf
      Kundendatenbanken handelt es sich dabei um eine
      „Auslieferung“.
Privat
:
Eine
      privatisierte Auslieferung oder eine neu erstellte Ansicht, deren
      Ansichts-Name keiner Auslieferung zugeordnet ist.
Grundlage
Versucht über das Einsatzgebiet der
      Archiv-Ansich
ten
zu informieren.
Mögliche Identifizierungen
      sind:
0 :
      Frei
1 :
      Auswahlliste
2 :
      Dialog
3 :
      Extern
4:
      Auswahl
Ansichts-Status
Auslieferung
:
Auslieferungen sind Ansichten, die
      mit „
AMIC_
“ beginnen und deren Besitzer „
Branchen-ERP
“
      ist.
Privatisierte
      Auslieferung:
Privatisierte Auslieferungen sind
      Auslieferungen die in aller Regel durch die Funktion „Ansicht duplizieren“
      erzeugt wurden.
Sie
      lassen sich aber ebenso komplett neu erstellen. Das wichtige
      Erkennungsmerkmal ist, dass eine solche Ansicht den gleichen Namen wie
      eine „Auslieferung“ hat.
Privat:
Eine
      private Ansicht ist weder eine Auslieferung noch eine privatisierte
      Auslieferung.
Ableitung:
Private Ansichten, also solche mit
      Ansichts-Status „Private Auslieferung“ oder „Privat“, können weiter
      abgeleitet werden.
Egal:
Einer der obigen
      Ansichts-Stati.
Einsatz
B
[...]


---

## Archivierung Datenbank – Import

Archivierung Datenbank – Import
Import Belege aus dem Dateisystem. Dabei erkennt der
Import selbständig, um welches Verfahren es sich handelt.
Verarbeitet können Exporte mit der AMICAR-Methode,
sowie der XML-Methode.
Die XML-Methode ist das Standard-Importverfahren.

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

## Aufgabenplanung Pfleger

Aufgabenplanung Pfleger
Felder des Aufgabenplanung Pflegers
Feld
Beschreibung
Aufgenommen von
Kürzel des Erstellers
Aufgenommen am
Datum an dem der Datensatz erstellt
      wurde
Verantwortlicher
Kürzel des ToDo Inhabers
Status
0:
      offen
1: erledigt
Termin von
Datum
Uhrzeit
Termin bis
Datum
Uhrzeit
Für
      Kunde
Kunden ID (
F3
)
Betreff
Betreff des ToDos
Beschreibung
Text
      zum ToDo
Funktionen des Aufgabenplanung Pflegers
Funktion
Beschreibung
Neu
      (
F8
),
Speichern (
F9
)
Erstellt neuen
      Datensatz
Speichert aktuellen Datensatz

---

## Ausdruck der Gebinde im Vorgang

Ausdruck der Gebinde im Vorgang
Die Faktoren, Ergebnisse und Rechenwege der
Gebindeberechnung können in den Vorgangsformularen ausgedruckt werden. Das kann
auch die Zwischenergebnisse der Gebindeberechnung, und zwar als Summe über ggf.
mehrere Gebindezeilen, betreffen.
Beispiel: Eine Palette umfasst 24 Kartons à 20 Dosen
zu 850g
Es können die Anzahl Gebinde, das Endergebnis in kg,
die Anzahl Kartons und Dosen ausgewiesen werden.

---

## Backupevents

Backupevents
Backups, also Datensicherungen der Datenbank sind ein
wesentlicher Bestandteil der Datensicherheit in Ihrem System. Deshalb sollten
Sie regelmäßig Sicherungen Ihrer Datenbank vornehmen lassen. Backupevents sind
Events, wie alle anderen auch. Sie sorgen lediglich für die Erstellung eines
Backups und werden mit Hilfe eines eigenen Pflegers erstellt, der Ihnen die
wesentlichen Parameter setzt.
Neues Backup
Event
Mit dieser Funktion lassen sich Backupevents schnell
einrichten.
Feld
Beschreibung
Backup Name
Der
      Name des Backups ist zugleich der Name des Backup-Events. Deshalb darf der
      Name keine Leerzeichen enthalten. Eingegebene Leerzeichen werden beim
      Verlassen des Eingabefeldes in Unterstriche ‚_‘ gewandelt.
BackupTyp
Wählen Sie beim Backuptyp
      zwischen
•
Vollbackup
      ohne Logfileaufbewahrung:
Hier wird die komplette Datenbank
      in das Backupverzeichnis kopiert und das aktuelle Transaktionslog nach
      Erstellung der Sicherungskopie verkürzt und neu gestartet.
•
Vollbackup
      mit Logfileaufbewahrung:
Hier wird die komplette Datenbank
      in das Backupverzeichnis kopiert. Der Datenbankserver wird veranlasst, das
      aktuelle Transaktionslog nach Erstellen der Sicherungskopie umzubenennen.
      Die Sicherungskopie des Transaktionslogs erhält einen Namen mit dem Format
JJMMTTnn.log
, um der umbenannten Kopie des aktuellen
      Transaktionslogs zu entsprechen.
•
Tagesbackup
      ohne Logfileaufbewahrung:
Hier wird NUR das Transaktionslog
      kopiert und das aktuelle Transaktionslog nach Erstellung der
      Sicherungskopie verkürzt und neu gestartet.
•
Tagesbackup
      mit Logfileaufbewahrung:
Hier wird das Transaktionslog
      kopiert. Der Datenbankserver wird veranlasst, das aktuelle Transaktionslog
      nach Erstellen der Sicherungskopie umzubenennen. Die Sicherungskopie des
      Transaktionslogs erhält einen Namen mit dem Format
JJMMTTnn.log
, um
      der umbenannten Kopie des ak
[...]


---

## Bearbeitungsmaske Spaltenbeschreibungen

Bearbeitungsmaske Spaltenbeschreibungen
In den
System- und Anwenderspalten finden Sie eine Liste von Einträgen. Diese können
Sie in der Liste mit den wichtigsten Werten versehen. Wenn Sie die Option
„Spaltenbeschreibungen“ wählen, so können Sie diese Werte für jede Zeile
editieren.
Dabei sind nicht immer alle der im Folgenden benannten
Felder sichtbar bzw. notwendig.
Spalte
•
System gibt an, dass es sich um eine vom Entwickler vorgegebene Spalte
handelt, die vom Anwender nicht editiert werden kann.
•
Anwender gibt an, dass es sich um eine vom Anwender definierte und
editierbare Spaltendefinition handelt.
Überschrift
Dies ist die Überschrift für die Spalten.
Die Überschrift wird im Zusammenhang mit
Baumdarstellungen bei Blattinformationen als Bezeichner des Wertes angezeigt. In
Knoten hat die Überschrift keine Bedeutung, in Blattinformationen soll sie
eingetragen sein.
Dragname
Dieser Wert wird nur im Zusammenhang mit
Baumdarstellungen verwendet.
Wird ein Element angeklickt, abgelegt oder verändert,
so sollen Informationen an eine definierte Knotenprozedur gegeben werden. Die
Namen der Parameter, in die die Werte geschrieben werden sollen, werden hier
festgelegt. Wird der Inhalt dieses Feldes leer gelassen, so wird dieser Wert
nicht an eine Prozedur übertragen.
Ist das Feld vom Typ „Blatt Abfragbar“, und wird der
Wert im Blatt verändert, so wird der ursprüngliche Wert mit dem hier angegebenen
Parameternamen übergeben.
Dropname
Dieser Wert wird nur im Zusammenhang mit
Baumdarstellungen verwendet.
Wird ein Element mit Drag&Drop abgelegt oder
geändert, so sollen Informationen an eine definierte Knotenprozedur gegeben
werden. Die Namen der Parameter, in die die Werte geschrieben werden sollen,
werden hier festgelegt.
Ist das Feld vom Typ „Blatt Abfragbar“, und wird der
Wert im Blatt verändert, so wird der geänderte Wert mit dem hier angegebenen
Parameternamen übergeben.
Feldname
Dies ist der Name des Datenfeldes im Resultset einer
Prozedur oder de
[...]


---

## Standard Bedienerklassen

Standard Bedienerklassen
In Referenz-ERP gibt es mehre Standardklassen, welche
genutzt werden können.
Defaultklasse
Diese Bedienerklassen werden von Referenz-ERP zur Abwicklung
weiterführender Programmmodule benötigt und sollten nicht geändert werden.
Momentan sind folgende Bedienerklassen technisch
notwendig:
Technische
      Bedienerklassen
-1
Defaultklasse Kunden
-9999
Defaultklasse Branchen-ERP
Controllerklasse
Bedienerklassen die Mitglieder der
Controller-Rolle
sind
Controllerklassen.
Sicherheitsklasse
Es ist möglich, Referenz-ERP mit der neu eingeführten
„Sicherheitsklasse“ in einen Schutzsystem-Zustand zu überführen: In diesem haben
nur noch die Mitglieder der „Sicherheitsklasse“ – sogenannte „Technische
Administratoren“ Zugriff auf die Änderung der Schutzeinstellungen der
Anwendungsfunktionen in Referenz-ERP (siehe auch
Zugriffsrechte Funktionen
).
Praktisch bedeutet dies, dass den „Technischen
Administratoren“ nur die Anwendung „Zugriffsrechte Funktionen“ (
Zugriffsrechte Funktionen
)
und Teile der Anwendung „Bedienerstamm“ (
Einrichtung Bediener]
) zur Verfügung
stehen – keine weiteren.
Außer den Mitgliedern der Sicherheitsklasse werden
„Schutzänderungen“ in „Dieses Menü“ nicht mehr erlaubt. Stattdessen wird den
Mitgliedern ein sogenannter „Schutzantrag“ per Mail über den Datenbank-Server
zugestellt. Das Referenz-ERP-System verifiziert die gewünschte letzte Änderung auf
Gültigkeit. Der „Technische Administrator“ darf keinen Schutz so verändern das
er nach der Änderung selber mehr und auch nicht weniger Rechte hat.
Im Bedienerstamm sind nach Aktivierung des
„Sicherheitsklassen“-Status die Funktionen des Bedienerklassenwechsels und
Änderungen der „Name Sicherheit“-Einstellungen sowie diverse Situationen beim
Ändern und Speichern derart geändert worden, dass sie die Situation eines
aktiven „Sicherheitsstatus“ gewährleisten und unterstützen.
Das Aktivieren der
Einstellung „Sicherheitsklasse“ ist nicht rückgängig zu machen.

---

## Bedienerklasse: Pfleger

Bedienerklasse: Pfleger
Register:
Allgemein
Felder
Beschreibung
Bedienerklasse
Eindeutige numerische Identifikation
      der Bedienerklasse
Bezeichnung
Bezeichnung der
      Bedienerklasse
Betriebsstätte
Bei
      angeschlossenem Filialsystem Zuordnung der Bedienerklasse zur
      Betriebsstätte.
Standard: 0, ohne Filiale
Konflikte, die sich beim Wechsel der
      Betriebstätte bzgl. „
Name Sicherheit
“ ergeben könnten, werden
      erkannt und der Wechsel dann unterbunden.
Bezeichnung
      Betriebsstätte
Bezeichnung der
      Betriebsstätte
Login-Sperre
JA/NEIN
Login-Sperre aller Bediener dieser
      Bedienerklasse
Formular
      FiBu-Infofenster
JA/NEIN
Zusätzliche
      Informationen in der Finanzbuchhaltung aktivieren
Toolbar aktiv
JA/NEIN
Aktiviert die standardmäßig
      ausgelieferte Toolbar.
Abteilung
Hier
      kann die Bedienerklasse einer Abteilung zugeordnet werden.
Abteilungen
Controllerklasse
Controllerklasse
Controllerklassen werden gelb
hervorgehoben
.
Sicherheitsklasse
Sicherheitsklasse
Formulararchiv
Hier kann für eine Bedienerklasse festgelegt werden,
welche Formulare des Archivs (abhängig von den zugeordneten Bedienerklassen)
eingesehen werden dürfen.
Diese Rechte können auch beim
Bediener
(Register Formulararchiv)
eingesehen werden.
Passwortrichtlinien
Felder
Beschreibung
Mindestlänge
Wie
      viele Zeichen das Passwort mindestens haben soll.
Höchstlänge
Wie
      viele Zeichen das Passwort maximal haben darf.
Das Limit liegt bei 10
      Zeichen.
Zahlen
Wie
      viele Zeichen im Passwort mindestens eine Zahl (0-9) sein
      müssen.
Sonderzeichen
Wie
      viele Zeichen im Passwort mindestens ein Sonderzeichen sein
      müssen.
Ausgenommen sind folgende Zeichen: „ \ ; - ‘
Aktualisierung in Tagen
Nach
      wie vielen Tagen seit der letzten Passwortänderung das Passwort wieder
      geändert werden muss.
Die Passwortrichtlinien werden je nach
Bedienerklasse individuell verwaltet und gepflegt.
Die Bearbeitung und A
[...]


---

## Bedienerwesen: Bediener, Bedienerklassen und Erfasser

Bedienerwesen: Bediener, Bedienerklassen und Erfasser
Hauptmenü
Administration
Firmenkonstanten
Bediener
oder Direktsprung
[BD]
Oder
Hauptmenü
Administration
Firmenkonstanten
Bedienerklassen
oder Direktsprung
[BDKL]
Oder
Hauptmenü
Administration
Firmenkonstanten
Erfasserstamm
oder Direktsprung
[ERF]
Wie auch sonst in Referenz-ERP üblich, stellt sich das
Bedienerwesen als hierarchisches System dar. Auf der untersten Stufe werden alle
EDV-relevanten Mitarbeiter eingetragen. Stufe 2 der Hierarchie bilden die
Bedienerklassen. Hier lassen sich Bediener mit gleichen Aufgabenbereichen
zusammenfassen.
Wie bei jedem hierarchischen System erfolgt die Pflege
prinzipiell von „oben nach unten“.

---

## Bediener clonen

Bediener clonen
Diese Funktion erlaubt es, einen Bediener mit allen
Daten zu kopieren und nach Eingabe eines neuen eindeutigen Namens, mit diesen
kopierten Daten zu erstellen.
Kopfdaten:
Felder
Beschreibung
Nehme nächste freie ID
      ab
Beim
      Duplizieren eines Bedieners wird diese ID als Vorgabe
      verwendet.
Sind
      mehrere Bediener zum duplizieren ausgewählt, dann wird diese Vorgabe
      jeweils um 1 erhöht.
Nach
      Eingabe wird die Spalte „Clone-ID“ des Grids neu kalkuliert.
Clone-Kurzname vorne erweitern
      um
Der
      Kurzname eines Bedieners muss eindeutig im System.
Nach
      Eingabe wird die Spalte „Clone-Kurzname“ im Grid neu
      kalkuliert.
jede
      Clone-Bedienerklasse setzen auf
Nach
      Auswahl einer Bedienerklasse wird diese in die Spalte „C-Bedienerklasse“
      übernommen und die Spalte „C-Betriebsstätte“ angepasst, sowie die Spalte
      „C-Windows Login Name“ neu auf Plausibilität geprüft.
Felder:
Felder
Beschreibung
ID
BedienerID des
      Vorlage-Bedieners
Clone-ID
Clone-BedienerID
Kurzname
Kurzname des
      Vorlage-Bedieners
Clone-Kurzname
Clone-Kurzname
Bedienerklasse
Bedienerklasse des
      Vorlage-Bedieners
Clone-Bedienerklasse
Clone-Bedienerklasse
Betriebsstätte
Betriebsstätte des
      Vorlage-Bedieners
Windows Login Name
Windows Login Name des
      Vorlage-Bedieners
Clone-Windows Login Name
Clone-Windows Login Name
Funktionen:
Die Eingaben im Grid werden auf mögliche Konflikte hin
geprüft. Eingaben die nicht plausibel sind werden farblich
hervorgehoben
.
Funktionen
Beschreibung
Bediener clonen
Dupliziert nach einer erneuten
      Plausibilitätsprüfung, die vorgegeben Bediener samt der zugehörigen
      Detailtabellen.

---

## Bedienung über das Favoritenmenü

Bedienung über das Favoritenmenü
In Standarddarstellung des Menüs haben wir auf der
linken Seite die Hauptauswahlbereiche, an oberster Stelle die Favoriten. Bei
Auswahl eines Hauptbereiches werden auf der rechten Seite der Maske die
zugehörigen Funktionen gezeigt. Zur Verwaltung der Favoriten dient die
F2
Taste. Fahren Sie mit der Maus über die
Funktionen der rechten Seite: Mit Auslösungen
F2
fügen Sie die Funktion den Favoriten
hinzu. Auf dem Favoritenmenü selbst nimmt
F2
den Favoritenstatus zurück.

---

## Bediener – Codepage

Bediener – Codepage
Es ist möglich, einem einzelnen Bediener im System
eine andere Codepage als die Westeuropäische Codepage zuzuordnen. Es sind
momentan einige wenige Codepagezuordnungen vorbereitet, wichtig hierbei ist,
dass die Mitteleuropäische Codepage zur Verfügung steht. Dadurch werden die
Sonderzeichen z.B. der polnischen Zeichensatztabelle auch korrekt im Referenz-ERP
System dargestellt und auf den Ausdrucken (Crystal Report und Formulareinrichter
(NICHT im Branchen-ERP Etikettendruck)) gedruckt.
Wichtig ist dabei, dass Referenz-ERP NUR im ASCII Mode (also
ein-byte pro Zeichen) arbeitet, ein ausschneiden und einfügen von Zeichen aus
Unicode getriebenen Programmen ist NICHT möglich.
Der Bediener muss seine Zeichensatztabelle auf dem
Windows Zeichensatzselector eingestellt haben, um auch die passenden Zeichen
eingeben und anschließend sehen zu können.
Beispiel:
Es muss im Falle von Crystal Report darauf geachtet
werden, dass die Umwandlung der Zeichensätze in die von CRW genutzte UTF8
Tabelle vorgenommen wird, es ist also in jedem Falle eine Privatisierung des
Reports notwendig (der Kontraktdruck per CRW ist im Standard schon entsprechend
angepasst).

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

## Bitzer Adressdaten

Bitzer Adressdaten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten der Adressstamm Tabelle gefüllt.

---

## Bitzer Artikeldaten

Bitzer Artikeldaten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten des Artikelstamms gefüllt.
Die hier angefügten Qualitäten werden aus der
Bestandteil Abteilung des Artikelstamms gelesen. Min und Max Werte sind in dem
Bestandteilbereich pflegbar

---

## Bitzer Qualitäten

Bitzer Qualitäten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten des
Bestandteilstamms
gefüllt.

---

## Bitzer Vorgang

Bitzer Vorgang
<?xml version="1.0"
?>
<vorgang nummer="11677" art="1">
<kontrakt-nummer>1105366</kontrakt-nummer>
<kontrakt-referenz-nummer />
<spediteur-adresse-nummer />
<kunden-adresse-nummer>1513520</kunden-adresse-nummer>
<kunden-adresse-name>GmbH</kunden-adresse-name>
<liefer-herkunftsort-adresse-nummer />
<artikel-nummer>11400</artikel-nummer>
<artikel-name>Raps Saat EU
zertifiziert</artikel-name>
<fahrzeug-kennung />
<fahrzeug-typ>0</fahrzeug-typ>
<fahrzeug-zuladung>0,0</fahrzeug-zuladung>
<kfz-kennzeichen>PZ947
FS</kfz-kennzeichen>
<kfz-haenger-kennzeichen />
<datum-uhrzeit>20150506
15:11:18</datum-uhrzeit>
<datum-uhrzeit-geaendert>20150506
14:58:17</datum-uhrzeit-geaendert>
- <!--
schnittstellen-id: 1
-->
- <!--
bitzer-vorgangs-id: 13661
-->
- <!--
bitzer-kontrakt-id: 3682
-->
- <!--
bitzer-artikel-id: 271
-->
- <!--
bitzer-kunde-adr-id: 476
-->
- <!--
bitzer-sped-adr-id: 0
-->
- <!--
bitzer-liefer-herk-adr-id: 0
-->
<gewicht-netto>
<einheit>kg</einheit>
<wert>26980</wert>
</gewicht-netto>
<schlag-lagerort />
<info-text-1 />
<info-text-2 />
<info-text-3 />
<info-text-4 />
<proben-nummer />
<zusatz>
<vorgangstyp-kennzeichen />
<proben-nummer />
<dispo-nummer>105366001</dispo-nummer>
<verkehrszweig />
<beleg-nummer />
</zusatz>
<lager>
<nummer>100</nummer>
<name1>Aktiengesellschaft</name1>
<name2>Silo </name2>
<name3 />
<strasse>
Aktiengesellschaft</strasse>
<plz>39126</plz>
<ort>Magdeburg</ort>
</lager>
<artikel nummer="11400">
<name1>Raps Saat EU
zertifiziert</name1>
<name2 />
<sorte />
</artikel>
<kunde nummer="1513520">
<name1> GmbH</name1>
<name2 />
<name3 />
<strasse>Christoph-Probst-Weg
1</strasse>
<plz>20251</plz>
<ort>Hamburg</ort>
</kunde>
<spediteur nummer="">
<name1 />
<name2 />
<name3 />
<strasse />
<plz />
<ort />
</spediteur>
<liefer-herkunftsort nummer="">
<name1 />
<name2 />
<name3 />
<strasse />
<plz />
<ort />
</liefer-herkunftsort>
<waegung art="1">
<waagennummer>1</waagennummer>
<laufende-nummer>4823</laufende-nummer>
<gewicht ha
[...]


---

## EAN-128 / UCC-128

EAN-128 / UCC-128
Gültige Zeichen:
Nahezu der gesamte ASCII Zeichensatz inkl.
      Steuerzeichen
Länge:
variabel (keine fest vorgegebene
      Länge)
Prüfziffer:
Berechnung nach Modulo
      103
ActiveBarcode berechnet die Prüfsumme für Sie automatisch
ActiveBarcode Typ#:
EAN/UCC-128 - #15 -
      CODEEAN128
EAN/UCC-128 AI - #28 - CODEEAN128AI
Beispiel:
Beschreibung:
Der
EAN/UCC 128
dient dem Handel und der Industrie vor allem der Waren-
      und Palettenauszeichnung.
Der EAN/UCC 128 ist eine Sonderform des
Code 128
. Er sieht
      die Verwendung eines besonderen Zeichens - dem FNC1 - unmittelbar nach dem
      Startzeichen vor. Diese direkte Aufeinanderfolge von Startzeichen und FNC1
      am Anfang ist ein eindeutiges Kennzeichen für einen EAN 128.
Die
      Länge ist des Codes ist variabel. Jedoch sollte die maximale Länge des
      Codes nicht mehr als 165mm betragen. Insgesamt dürfen maximal 48
      Nutzzeichen (inkl. der
Datenbezeichner/AIs
und eventueller FNC1 Trennzeichen) codiert werden.
In einem
      EAN/UCC 128 Barcode können mehrere Daten gleichzeitig codiert werden. So
      ist es z.B. üblich Lebensmittelpaletten neben dem Produktcode (wie beim
EAN 13
) auch
      zusätzlich mit Gewichtsangaben und dem Haltbarkeitsdatum im Barcode
      auszuzeichnen.
Um diese unterschiedlichen Daten in einem Barcode
      codieren zu können gibt es einen internationalen Standard für
      Datenbezeichner, die angeben welche Daten codiert sind. Dies sind die
Application
      Identifier
. Ein Barcode könnte z.B. so aussehen:
Die Werte innerhalb der
      Klammern sind die
Application
      Identifier
(kurz: AI) und die Werte danach die entsprechenden
      Daten. Die Klammern dienen nur der Lesbarkeit der Klarschriftzeile und
      sind nicht in dem Strichcode codiert. Die "(01)" kennzeichnet
      beispielsweise den Produktcode, welcher immer in 14 Ziffern angegeben
      wird. Diese 14 Ziffern folgen dem
AI
. Daraufhin folgt
      der nä
[...]


---

## Beispiel XML Datei

Beispiel XML Datei
<?xml version="1.0"
encoding="iso-8859-1"?>
<Scans
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
Stop = "false"
>
<ScanListe>
<Scan Code="-1"
Stop = "false">IV</Scan>
<Scan Code="-4"
Stop = "false">6666000000001</Scan>
<Scan Code="-30"
Stop = "false" WaitTime = "500">15</Scan>
<Scan Code="-1"
Stop = "false"  Close = "true">IVENDE</Scan>
</ScanListe>
</Scans>
XML Elemente
Bedeutung
<Scans>
Kann
      mehrere Scanlisten enthalten
<ScanListe>
Die
      ScanListe enthält alle Scanns die für eine komplette Erfassung eines
      Scannvorgangs nötig sind.
<Scan>
Enthält die einzelen
      Scannpositionen
Attribute
Attribut
Bedeutung
Code
Hier wird der
            Scanncode angegeben.
Folegende
            Scanncodes sind offiziell möglich.
-1
Steht für nicht
            Identfizierten Code. Dieser wird für die Start und Endcodes eines
            Vorganges benutzt. Dieser kann auch verwendet werden, wenn ein ein
            EAN 128 Code erfasst werden und per Prozedur SPLIT AI ausgewertet
            werden soll
-4
Steht für ein
            EAN 13 Code
-8
Steht für ein
            EAN 8 Code
-30 Steht für
            die Mengeneingabe
Stop
•
True
•
False
Wird das Attribut auf true gesetzt, so
            wird der ScannCode nicht abgearbeitet
Close
•
True
•
False
Wird das
            Attribut auf true gesetzt, so wird nach der Abarbeitung die
            Scannersoftware automatisch geschlossen.
Das Attribut
            muss nicht immer gesetzt werden, der Standardfall ist
            false.
WaitTime
•
Zeit in
            Millisekunden
•
Vorbelegung =
          0
Ist dieses
            Attribut größer als Null, entspricht die Wartezeit, die der Scanner
            nach einem Befehl wartet,  dem angebenen Wert in Millisekunden.
            Ansonsten sind die Wartezeiten standardmäßig 1000(1s) für normale
            Befehle und 10000(10s) für
      Ende-Befehle.

---

## Schritt 1 Setup

Schritt 1 Setup
Schritt 1.1: AEB Zugang
Um die Sanktionslistenprüfung in Referenz-ERP zu nutzen,
braucht man einen Zugang zu den Diensten von AEB. Diese übenhemen den Abgleich
der Adress/Personendaten in Referenz-ERP mit den Sanktionslisten der EU. Man muss also
einen Zugang zu den Dienstleitungen von AEB erwerben (dies ist nicht im Preis
des Moduls enthalten). Die Angebote von AEB finden sie unter:
https://www.aeb.com/de-de/produkte/compliance-screening/preise-compliance-screening.php
.
Schritt 1.2: Steuerparameter konfigurieren.
Mit dem Direktsprung
[SPA]
gelangt man in die Übersicht der
Steuerparameter. Dort kann man mit
F2
nach der Bezeichnung „Verbot“ suchen und bekommt die Übersicht aller
Steuerparameter für Compliance angezeigt, indem man mit
F9
die Suche speichert.
SPA 707:
Dieser Steuerparameter ist die Lizenz für dieses Modul
und nach dem Erwerb zu aktivieren.
SPA
1063
:
Der Steuerparameter 1063 für das Compliancemodul
beinhalten Prozeduren, welche die Abfragen der Adress/Personendaten
beeinflussen. Da diese in der Komplexität recht anspruchsvoll werden können,
muss dies von unserem Amic Support angepasst werden.
In dem Steuerparameter sind auch Werte, welche
unkomplex und einfach zu ändern sind:
-
GoodGuys berücksichtigen
: (0: nein, 1: ja)
-
Ansprechschwelle
(ist ein Prozentualer Wert, welcher bei Ähnlichkeiten
von Namen/Adressen von AEB berechnet wird)
-
Adressen des Vorgangs:
Eine Datenbankprozedur, die
als Eingabeparameter eine V_ID bekommt und alle Anschriften des Vorgangs
ermittelt. Als Standardbeispiel wird hier die Prozedur
„AMIC_DEMO_COMPLIANCE_ADRESSEN_VORGANG“ eingetragen.
-
Adressen des Kunden:
Eine Datenbankprozedur,
die als Eingabeparameter eine KundID  bekommt und alle Anschriften des
Kunden ermittelt. Als Standardbeispiel wird hier die Prozedur
„AMIC_DEMO_COMPLIANCE_ADRESSEN_KUNDEN“ eingetragen.
-
Adressen für zyklische Anschriftenprüfung
Eine Datenbankprozedur,
die Anschriften für eine regelmäßige Anschriftenprüfung ermittelt.
Als
[...]


---

## Client-Cache

Client-Cache
Cache
(engl. [
kæʃ
];
selten auch: [
kaʃ
]
[1]
)
bezeichnet in der
EDV
einen
schnellen
Puffer
-
Speicher
,
der (erneute) Zugriffe auf ein langsames
Hintergrundmedium
oder aufwändige Neuberechnungen zu vermeiden hilft. Inhalte/Daten, die bereits
einmal beschafft/berechnet wurden, verbleiben im Cache, so dass sie bei späterem
Bedarf schneller zur Verfügung stehen. Auch können Daten, die vermutlich bald
benötigt werden, vorab vom Hintergrundmedium abgerufen und vorerst im Cache
bereitgestellt werden.
Caches können als Hardware- oder Softwarestruktur
ausgebildet sein. In ihnen werden Kopien zwischengespeichert.
Cache
ist ein
Lehnwort
aus dem Englischen. Seinen Ursprung hat es im französischen
cache
, das
eigentlich die Bedeutung
Versteck
besitzt.
[2]
[3]
Der Name verdeutlicht den Umstand, dass dem Verwender in der Regel der Cache und
seine Ersatzfunktion für das angesprochene Hintergrundmedium verborgen bleibt.
Wer das Hintergrundmedium verwendet, muss Größe oder Funktionsweise des Caches
prinzipiell nicht kennen, denn der Cache wird nicht direkt angesprochen. Der
Verwender „spricht das Hintergrundmedium an“, und es „antwortet“ stattdessen der
Cache – genau auf die Art und Weise, wie auch das Hintergrundmedium geantwortet,
also Daten geliefert hätte. Man spricht wegen der Unsichtbarkeit dieser
zwischengeschalteten Einheit auch von
Transparenz
.
Praktisch ist er eine gespiegelte Ressource, die stellvertretend für das
Original sehr schnell bearbeitet/verwendet wird.
Greifen außer dem Cache-verwendenden Gerät noch
weitere auf das Hintergrundmedium zu, so könnte es zu
Inkohärenzen
kommen – um auf ein identisches Datenabbild zugreifen zu können, ist es
notwendig, zuvor die Änderungen des Caches in das Hintergrundmedium zu
übernehmen.
Cachestrategien
wie
Write-Through
oder
Write-Back
sind hier praktikabel. Im Extremfall muss ein kompletter „Cache Flush“ erfolgen.
Außerdem muss ggf. der Cache informiert werden, dass sich Daten auf dem
Hinte
[...]


---

## Der Referenz-ERP Startbildschirm

Der Referenz-ERP Startbildschirm
Zum Anmelden: Den Kurznamen als auch das Passwort
eines Benutzers eingeben (Erstellung eines Logins unter:
Bediener Modul
).
Zum schnellen Anmelden: Die Tastenkombination:
(Alt + A)
benutzen.

---

## Der Bediener „Branchen-ERP“

Der Bediener „Branchen-ERP“
Der Bediener Branchen-ERP dient der Durchführung von Wartungs-
bzw. Support-Aufgaben.
In aktiven Filialsystemen wird dem Bediener Branchen-ERP das
Login in Mandanten verwehrt, deren Filialnummer nicht der seiner
Filialzugehörigkeit lt. Bedienerklasse entspricht.

---

## Dokumenten Editor

Dokumenten Editor
Der Dokumenten Editor in Referenz-ERP ist die Lösung für
perfekt zugeschnittene Druckergebnisse. Hier können individuelle Anpassungen für
den Druck getätigt werden.

---

## Datei

Datei
Funktion
Beschreibung
Beenden
Beendet den Referenz-ERP Dokumenten
      Editor
Speichern
Speichert das Dokument im
      gewünschten Dateiformat im Dateisystem ab
Hilfe
Ruft
      diese Hilfe auf

---

## Start

Start
Der Referenz-ERP Dokumenten Editor bietet vielfältige
Möglichkeiten das Dokument anzupassen.
Zwischenablage
Funktion
Beschreibung
Einfügen
(STRG +V)
Fügt
      den Zwischenspeicher in das Dokument ein
Ausschneiden
(STRG + X)
Schneidet aus dem Dokument aus und
      schreibt die Daten in den Zwischenspeicher
Kopieren
(STRG + C)
Kopiert aus dem Dokument und
      schreibt die Daten in den Zwischenspeicher
Schriftart:
Funktion
Beschreibung
Schriftart
Setzt die Schriftart des markierten
      Textes (und dem folgenden)
Schriftgröße
Setzt die Schriftgröße des
      markierten Textes (und dem folgenden)
Schriftfarbe
Setzt die Schriftfarbe des
      markierten Textes (und dem folgenden)
Fett
Setzt die Schrifteigenschaft des
      markierten Textes auf FETT (und dem folgenden)
Kursiv
Setzt die Schrifteigenschaft des
      markierten Textes auf KURSIV (und dem folgenden)
Unterstrichen
Setzt die Schrifteigenschaft des
      markierten Textes auf Unterstrichen (und dem folgenden)
Durchgestrichen
Setzt die Schrifteigenschaft des
      markierten Textes auf Durchgestrichen (und dem folgenden)
Hochstellen
Setzt die Schrifteigenschaft des
      markierten Textes auf Untertext (und dem folgenden)
Tiefstellen
Setzt die Schrifteigenschaft des
      markierten Textes auf Kopftext (und dem folgenden)
Text-Typ
Formatiert den Text in das
      angegebene Textlayout
Farbe (Hintergrund)
Setzt die
Farbe (Text)
Absatz:
Funktion
Beschreibung
Aufzählungen
Erstellt eine Auflistung
Absatzeinrückung
(TAB)
Rückt den Text ein:
Vor
Zurück
Textrichtung
Stellt die Textrichtung
      ein
Links
Rechts
Tabulatoren
Stellt die Tabulatoren
      ein
Kontrollzeichen
Zeigt Umbrüche und Leerzeichen
      an
Bündigkeit
Stellt die ausrichtung
      ein
Links
Zentriert
Rechts
Block
Zeilenabstand
Stellt den Zeilenabstand
      ein
Rahmen
Erstellt/bearbeitet einen
      Rahmen
Erstellen
Hintergrundfarbe
Rahmenfarbe
Rahmenbreite
Formatvorlagen
Hier können Formartvorlagen bearbeitet / erstellt
we
[...]


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

## Druckerzuordnung

Druckerzuordnung
Hauptmenü
Administration
Drucker
Druckerzuordnung
oder Direktsprung
[DRZ]
Je Bediener ist die Zuordnung eines Standarddruckers
für den Ausdruck im ASCII-Format erforderlich. Ist ein Bediener neu angelegt,
wird er beim Start aufgefordert, eine Druckerzuordnung vorzunehmen. Auf dem
zugeordneten Drucker erfolgt dann im Standardfall der Ausdruck. Dies wird jedoch
durch Eintragungen in den Vorgangsdruckklassen
[VRGD]
übersteuert. Näheres dazu findet sich
u. a. im Kundenstamm.
Mit
F3
kann
aus den eingerichteten Druckern ausgewählt werden.
Wichtig:
Soll mit dem Laserdrucker gearbeitet werden, ist
darauf zu achten, dass in den Formularen
[FRM]
mit
Ändern
F5
die Länge von 72 auf 64 geändert wird.
Sollen Auswahllisten (
F4
) gedruckt
werden, ist pro Bediener
[BD]
das
Formular 112 unter Form. Kurzliste einzutragen!

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

## DSO

DSO
Das Formulararchiv bedient sich einer
Microsoft-Technologie, um im Falle einer Dateieingliederung ins Formulararchiv
auf NTFS-Systemen die erweiterten Datei-Attribute zu ermitteln. Die Abfolge wird
über das VBA-Script AMIC_FA_INFO abgewickelt.
Technisch muss die Datei
dsofile.dll
als
COM-Objekt auf dem System registriert sein.
Das erledigt man „händisch“ auf dem System über
regsvr32 dsofile.dll

---

## eClearing

eClearing

---

## eClearing

eClearing

---

## eRechnung

eRechnung

---

## eRechnung

eRechnung

---

## eRechnung

eRechnung

---

## eRechnung

eRechnung

---

## EDI-Datenaustausch

EDI-Datenaustausch

---

## Bedienerklassen

Bedienerklassen
Hauptmenü
Administration
Firmenkonstanten
Bedienerklassen
oder Direktsprung
[BDKL]
Bedienerklassen fassen Mitarbeiter mit gleichen
Rechten zusammen; sie dienen also somit einer Strukturierung der
Rechtevergabe.
Felder der Bedienerklasse:
In der Variante „Bedienerklasse“ werden folgende
Felder behandelt:
Felder
Beschreibung
Bedienerklasse
Im
      Normalfall eine nicht-negative Zahl die Bediener gruppiert.
Als
      Spezialfälle gibt es technische Bedienerklassen
Bedienerklasse: Defaultklasse
.
Bezeichnung
Bezeichnung der
      Bedienerklasse
Betriebsstätte
Bei
      angeschlossenem Filialsystem Zuordnung der Bedienerklasse zur
      Betriebsstätte.
Standard: 0, ohne Filiale
Bezeichnung
      Betriebsstätte
Bezeichnung der
      Betriebsstätte
Gesperrt
JA/NEIN
Login-Sperre aller Bediener dieser
      Bedienerklasse
Sicherheitsklasse
Sicherheitsklasse
Controllerklasse
Controllerklassen werden gelb
hervorgehoben
.
Bedienerlisten-Info
Liste der zugehörigen
      Bediener.
Angezeigt werden nur Bediener, die
      weder gelöscht oder gesperrt sind, und die in der Datenbank als User
      verzeichnet sind.
Suchmöglichkeiten der Bedienerklasse:
Suchkriterien
Bedienerklasse
von
      … bis …
Funktionen der Bedienerklasse
In der Variante „Bedienerklasse“ stehen folgende
Funktionen zur Verfügung.
Funktionen
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
Bedienerklasse:
      Pfleger
auf. Innerhalb dieser Funktion lässt sich mit
Speichern unter…
eine neue
      Bedienerklasse erzeugen.
Dabei werden dann auch sämtliche
      Schutzeinstellungen der Funktionen (
Zugriffsrechte Funktionen
)
      übernommen.
EPAs
      zeigen
(F10)
Individuelle Steuerungen von
      Abläufen können in Anwendungen über Einrichterparameter (EPA) vorgenommen
      werden.
Diese Funktion ruft die
      entsprechende Anwendung zur Ansicht und Pflege der Einrichterparameter
      auf.
Hauptmenü
Administration
Steuerung
EPAs zeig
[...]


---

## Zeiterfassung (EPA Zeiterfassung)

Zeiterfassung
(EPA Zeiterfassung)
Bezeichnung
Standardwert
Erklärung
Bediener_Zeiterfassung
Es
      kann eine Funktion hinterlegt werden, welche eine KundId sucht, falls
      diese nicht mitgegeben wird. So könnte beispielsweise bei einem
      Direktsprung auf die Maske eine KundId in Abhängigkeit des Users gezogen
      werden.
Beispielfunktion: „Zeiterfassung
      Bediener“

---

## Lagerkopierer (EPA LAKO)

Lagerkopierer
(EPA LAKO)
Bezeichnung
Standardwert
Erklärung
Folgende Bediener dürfen nur das
      Sortimentslager bearbeiten
In
      diesem Parameter wird eine Liste vom Bedienern, welche durch Komma
      getrennt werden, hinterlegt. Diese Bediener dürfen nur das Sortimentslager
      bearbeiten.

---

## eRechnung

eRe
chnung
Auf der Registerkarte „eRechnung“ werden alle Daten
gepflegt, welche für das gleichnamige Modul gebraucht werden.
Electronic Address
Die „Electronic Address“ wird als Information in die
XML der eRechnung übernommen. Dabei wird als Mailempfänger die „Electronic
Address“ herangezogen, wenn folgende Voraussetzungen erfüllt sind:
1.
Der eBeleg ist eingerichtet und der Versandweg generiert eine Mail, in der nur
die eRechnung als Anhang enthalten ist.
2.
Alle aktuellen Versandprozeduren AMIC_Belegversand_Ware_Spaeter oder
AMIC_Belegversand_Ware_Sofort unter [FRZ] auf Tabreiter Abwicklung sind
eingetragen.
Hinweis: Private Prozeduren müssen ggf. um dieses
Verhalten erweitert werden.
Leitweg
Leitweg für die elektronische Zustellung von eRechnung
an Behörden.
In der Tabelle kann dem
Kunden das passende Profil zugeordnet
werden.
Versandweg UBL
Unterschiedliche Möglichkeiten zum Versand von
eRechnungen.
Wert
Bezeichnung
Bedeutung
1
Manuell
Es
      erfolgt kein automatisierter Versand. Die eRechnung wird über die
      Varianten in der Belegerfassung generiert. Der Transport der Datei muss
      anders geregelt werden.
2
eBeleg ohne PDF
Nur
      die eRechnung wird per eBeleg verschickt. Es wird kein PDF-Dokument
      verschickt. Der Empfänger der Mail ist die Adresse, die im Feld
      „electronic Address“ gepflegt ist. Ist dort nichts gepflegt, wird die
      Mailadresse über die eBeleg-Einrichtung übermittelt.
3
eBeleg mit PDF
Dies
      ist die Vorbelegung. Die eRechnung und das zugehörige PDF-Dokument werden
      in einer Mail an den Mailempfänger aus der eBeleg-Einrichtung
      versendet.
4
eBeleg PDF und XML
      getrennt
Das
      PDF und die XML werden in gesonderten Mails verschickt. Die PDF wird an
      den Mailempfänger gemäß eBeleg-Einrichtung verschickt. Die eRechnung wird
      an die Mailadresse verschickt, die unter „electronic Address“ eingetragen
      ist. Ist dort nichts gepflegt, wird auch hier die Mailadres
[...]


---

## Erfasser: Pfleger

Erfasser: Pfleger
Felder:
Felder
Beschreibung
Nummer
ID
      des Erfassers.
Kurzname
Kurzbeschreibung des
      Erfassers.
Name
Name
      des Erfassers.
Passwort
Hier
      wird das Passwort des Erfassers gesetzt.
Bediener
Gibt
      an, an welchen Bediener der Erfasser gebunden ist.
Funktionen:
Funktionen
Beschreibung
Speichern
(F9)
, Neu
(F8)
, Speichern unter…
(shift + F9)

---

## Erfassung Produktion

Erfassung Produktion
Hauptmenü
Produktion / Abwicklung
Produktionsabwicklung
Produktionszugang erfassen
oder Direktsprung
[PROE]
Hauptmenü
Produktion / Abwicklung
Produktionsabwicklung
Produktion
oder Direktsprung
[PROB]
Mit
[PROE]
gelangt man in die Erfassungsmaske Produktion. Der Direktsprung
[PROB]
lässt die Verwaltung erfasster
Produktionen zu. Hier kann mit der Funktion
Produktion erfassen F8
auch erfasst
werden.
Zuerst ist das Lager Produktzugang anzugeben.
Die Einrichtung der Erfassungsfelder ist mittels
[UFLD]
möglich.
Mit
F5
wird
die Umbuchungsmaske geöffnet.
Hier ist bei Einrichtung des Rezeptes wie oben
beschrieben die Artikelnummer Produkt, die zugehörende Rezeptnummer sowie die
produzierte Menge einzugeben.
Eventuell (siehe
Steuerparameter
) sind jetzt die
Komponentenmengen und deren Preise zu pflegen.
Je nach gewähltem Bewertungstyp wird in dieser Maske
von Produkt zu Komponenten oder umgekehrt verrechnet.
Je Beleg können mehrere Produktionen eingetragen
werden. Korrekturaufruf erfolgt über die Produktposition.
In der linken Spalte im Komponentenbereich wird der
Status der jeweiligen Position gekennzeichnet:
•
W         Wertartikel
•
P         Pauschalposition
•
F
Fixpreiskomponente
•
G         Gegenzeile

---

## Erweiterungen

Erweiterungen
Die Partieverwaltung ist in ihrer Optik und
Funktionalität vollständig überarbeit worden. In diesem Dokument werden sowohl
die Bedienung der neuen Dialoge beschrieben als auch einige Unterschiede in den
internen Datenformaten und deren Auswirkung auf die Gestaltung von privaten
Auswahllisten sowie MAKROS erläutert.
Das wesentliche Merkmal der neuen Partieverwaltung ist
die Möglichkeit, einer Warenposition mehrere Partien zuzuordnen. Nun ergeben
sich aber gerade aus dieser an sich kleinen Änderung erhebliche Änderungen in
der Bedienung. Bisher wurde immer die Menge der Warenposition 1 zu 1 auf die
Partie gebucht. Bei einer nachträglichen Änderung der Menge musste man an der
Partiezuordnung nichts ändern, soweit keine Patiebestandsunterschreitung
festgestellt wurde. Mit Einführung der Mehrfachzuordnung von Partien müssen
jetzt auch Mengen eingegeben werden.
Wir haben versucht, den Standardablauf (insbesondere
mit nur einer Partie) durch sinnvolle Vorbelegungen mit nur wenigen
Tastendrücken zu erledigen. Hierzu wurde auf das bisher benutzte
Partieauswahlfenster als eigenständiger Dialog verzichtet. Die Eingabe wird
explizit auf der Warenpositionsmaske vorgenommen. Da diese Maske (abhängig von
der Einrichtung) schon sehr viele Felder enthält, haben wir uns entschlossen,
den Platz der Funktionsliste (OPTIONBOX) mit den Eingabefeldern der Partie zu
teilen. Bei der Partiezuordnung wird daher die Optionbox ausgeblendet und durch
die Eingabefelder der Partie ersetzt. Die Funktionen der Optionbox stehen aber
natürlich weiter zur Verfügung. Sie können auf folgende Weise ausgelöst
werden:
Mit der Maus (rechte Maustaste )
Durch Funktionstasten, soweit belegt
Es kann aber auch zu jeder Zeit das Partiefenster
durch wiederholtes Betätigen der Funktion Partieauswahl
CF7
geschlossen / wieder geöffnet werden
(die zugeordneten Partien bleibt bei geschlossenem Fenster natürlich
erhalten!).

---

## Export XML-Verfahren

Export XML-Verfahren
Die XML-Methode ist die Standard-Methode, um Belege
aus dem Formulararchiv zu exportieren.
Die Volumeneinstellung greift bei der XML-Methode
nicht.
XML im Allgemeinen ist die Methode schlechthin um
Daten von A nach B zu transportieren. Diesen Umstand trägt Referenz-ERP in besonderer
Form Rechnung, als dass es neben der reinen Datenausgabe auch noch gleichzeitig
die Ansehen-Möglichkeit integriert.
Nach erfolgtem Export
sieht das Export-Verzeichnis in etwa so aus
Interessant dabei ist zunächst die erzeugte XML-Datei
archiv_export.xml.
Das Format der XML-Datei ist dabei wie folgt (Inhalt
gekürzt!)
<?xml version="1.0"
encoding="ISO-8859-1"?>
<?xml-stylesheet type="text/xsl"
href=".\archiv_export.xsl"?>
<archiv>
<VOM>15.02.2005</VOM>
<BELEG>
<MND>5</MND>
<KND>0</KND>
<TYP>QR: test</TYP>
<BEL>1</BEL>
<DAT>10.02.2005</DAT>
<REF>test</REF>
<DRUCK>10-02-05 10:28:29</DRUCK>
<DATEI>.\00008892.pdf</DATEI>
<STEUER>a2005_02.xml</STEUER>
<GROESSE>2512</GROESSE>
<NKR>00008892</NKR>
<MIME>application/pdf</MIME>
<MD5>4d04b4f8bd9427ec5bd75788c4c887fe</MD5>
<BKL>6400</BKL>
</BELEG>
<BELEG>
<MND>5</MND>
<KND>10005</KND>
<TYP>Vorgangklasse 790</TYP>
<BEL>7450</BEL>
<DAT>27.01.2005</DAT>
<REF>0500007450</REF>
<DRUCK>09-02-05 17:45:54</DRUCK>
<DATEI>.\00008893.pdf</DATEI>
<STEUER>a2005_02.xml</STEUER>
<GROESSE>16430</GROESSE>
<NKR>00008893</NKR>
<MIME>application/pdf</MIME>
<MD5>dc01eeb1932a2ab69ccc7e01d7f631ac</MD5>
<BKL>790</BKL>
</BELEG>
</archiv>
Wie man unschwer erkennen kann befindet sich der
wesentliche Inhalt der Relation Formulararchiv in der XML-Datei wieder.
Mit Hilfe des XML-Formates können externe Programme
nun leicht die Daten weiterverarbeiten.
Schaut man sich diese XML-Datei im Explorer an, so
wird vom Betriebssystem ein weiteres Schmankerl (die XSL-Datei) zur Ansicht
herangezogen und der Export repräsentiert sich so:
Wie man unschwer erkennt, sind die Belege per Link
erreichbar, also bei Interesse einfach anklicken. Im Internet-Explorer sucht m
[...]


---

## Externe Relation Formulararchiv abbauen

Externe Relation Formulararchiv abbauen
Bei sehr großen Formulararchiv-Relationen haben wir
angeraten, die Relation Formulararchiv samt Massendaten extern zu halten.
Weiterentwicklungen in Referenz-ERP führen jedoch dazu, dass diese Maßnahme nicht
länger nötig ist, ja sie sogar unbedingt rückgängig gemacht werden sollte.
Waren „früher“ noch alle Daten des Archivs in der
einen Relation Formulararchiv konzentriert, so ist der Stand heute, dass die
binären Dokumente des Formulararchivs – und das ist der weitaus größte
Datenanteil – sich in der dafür extra geschaffenen Relation Archiv befinden.
Rahmen- und Steuerdaten befinden sich nun in der Relation Formulararchiv. Dieses
Vorgehen hat enorme positive Auswirkungen auf die Geschwindigkeit, mit der das
Basissystem Recherchen anstellen kann. Weiterhin sind so Nachforschungen
möglich, die mit einer einzelnen externen Relation Formulararchiv-Relation nicht
machbar wären.
Somit steht man vor der Aufgabe ggf. eine externe
Relation Formulararchiv in eine interne Relation zu überführen.
Bitte überprüfen Sie zunächst ob die Relation
formulararchiv auch extern ist.
Kommando hierfür:
select
remote_location from sys.systable where table_name = 'formulararchiv'
Existiert ein nichtleere remote_location, ist die
Relation Formulararchiv extern und es sind weitere Schritte nötig.
Wir werden nun eine leere Relation formuararchiv_neu
anlegen (Schritt1), die Daten von formulararchiv in diese Relation transferieren
(Schritt2) und zum Schluß die Relation formulararchiv droppen und die Relation
formulararchiv_neu in die relation formulararchiv umbenennen. (Schritt3)
Restaurieren der Indizes (Schritt4)
Als letzte Maßnahme wird eine Reorganisation der
Datenbank empfohlen.
Bevor Sie weitermachen kommen Sie bitte Ihrer
Sorgfaltspflicht nach und überzeugen sich, dass sie eine lauffähige Sicherung
der beteiligten Datenbanken haben, um im Bedarfsfalle möglicherweise auftretende
Problemfälle notfalls dadurch rückgängig machen zu könne
[...]


---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen
Frage: Was passiert, wenn man einen Bediener
löscht? Erhält er lediglich ein Kennzeichen?
Antwort:
Mit der Funktion
„Bediener löschen“
werden die
Einträge des Bedieners irreversibel aus verschiedenen Tabellen in Referenz-ERP
gelöscht! Im Bedienerstamm bleibt der Bediener bestehen und wird als inaktiv
gekennzeichnet. Eine Wiederstellung des Bedieners ist nicht möglich! Auch eine
„Speichern unter“-Funktion steht in diesem Fall nicht zur Verfügung.
Möchte man lediglich erreichen, dass sich der Bediener
nicht mehr in Referenz-ERP anmelden kann, dann trägt man im Bedienerstamm im Feld
„Sperre“ ein „Ja“ ein. Eine Reaktivierung ist über die Aufhebung des
Sperrkennzeichens jederzeit möglich.
Frage: Ein Mitarbeiter
sieht keine oder nicht alle archivierten Belege.
Antwort:
Hierbei handelt es sich
i.d.R. um eine Frage von Berechtigungen. Diese werden je Bedienerklasse
vergeben. In den archivierten Dokumenten ist die Bedienerklasse desjenigen
Mitarbeiters eingetragen, der das Dokument archiviert hat. Die Anzeige des
Dokuments im Archiv ist nur für Bediener freigeschaltet, die einer mit dieser
Berechtigung ausgestatteten Bedienerklasse angehören. Die Erteilung dieser
Berechtigungen wird unter dem Direktsprung BDKL eingestellt. Dort markiert man
die betreffende Bedienerklasse, der Ansichtsrechte erteilt werden sollen, und
fügt mit “Ändern” (F5) auf dem Reiter “Formulararchiv” die Bedienerklassen
hinzu.
Beispiel: Hat Herr Müller
ein Dokument archiviert und gehört er der Bedienerklasse 200 an, dann muss in
der Bedienerklasse 200 auch unter BDKL bei “erlaubte Bedienerklassen für das
Formulararchiv” die 200 eingetragen sein, damit er das Dokument sehen kann. Soll
auch Frau Schmidt aus der Bedienerklasse 300 dieses Dokument sehen können, so
muss in der Bedienerklasse 300 unter BDKL bei “erlaubte Bedienerklassen für das
Formulararchiv” ebenfalls die 200 eingetragen sein.

---

## Vorgang

Vorgang
Frage: In der
Rechnungsbearbeitung [REB] fehlt eine Belegnummer. Was ist mit dieser
Rechnung?
Antwort:
Wenn in einer Auswahlliste
ein Beleg nicht wie erwartet angezeigt wird, kann es mehrere Gründe geben.
Prüfen Sie als erstes die Auswahlbedingungen im F2-Filter. Vielleicht wurde hier
eine unzutreffende Eingrenzung vorgenommen.
Eine andere Möglichkeit ist, dass der Beleg über die
Funktion „Stornieren“ (F7) aus dem System entfernt worden ist. Unter dem
Direktsprung STOPO (Stornoprotokoll) sind die Belegnummern und weitere Eckdaten
aufgeführt. Der Beleg ist dann nicht mehr existent und aufrufbar. Die
Einstellung des Steuerparameters [SPA] Nr. 490 „Storno-Belegnummern wieder
reaktivieren“ auf den Wert „Nein“ verhindert die erneute Vergabe der
Belegnummer.
Frage: Beim Erfassen von Eingangsrechnungen ist bei
uns für den Administrator „Zeilen-Zu-/Abschlag“ freigeschaltet. Der normale
Bediener sieht diese Zeile in der Option Box unten links nicht. Wo kann ich für
Normalbediener alle Funktionen in der Option Box freischalten?
Antwort:
Die Berechtigungen für Funktionen in Option Boxes kann
man ändern, wenn man als Administrator in der betreffenden Option Box auf den
untersten Eintrag navigiert: „Dieses Menü“.
Entweder filtert man dann mit
F2
den Text der Beschriftung oder wählt
direkt aus der Auswahlliste.
Ist der entsprechende Datensatz markiert, so öffnet
sich mit
„Ändern“
(F5)
eine Maske, auf der für die
Bedienerklassen ablesbar und einstellbar ist, ob ihnen die Funktion zur
Verfügung steht.
Die Einträge in der Spalte „Soll“ können hier
angepasst werden. Die Zuweisung der Berechtigungen (Ja/Nein) erfolgen immer je
Bedienerklasse. Angezeigt werden auch die Kurzbezeichnungen der dieser Klasse
zugehörigen Bediener. Die Namen zu den Bediener-Kurzbezeichnungen findet man im
Bedienerstamm
[BD]
.
Zusatzhinweis: Wenn es die Kombination aus
Bedienerklassen bereits gibt, dann wird die entsprechende Rollenbezeichnung oben
im Feld „Rolle“ eingesetzt.
[...]


---

## Formate der Zahlungsbedingungen

Formate der Zahlungsbedingungen
Hier finden Sie die Formate und dazugehörigen
Beschreibungen, welche in der Zahlungsbedingung verwendet werden.
Typ
Bezug
Automatisch
aufblenden
Formel
Valutabestimmung
Typ
Mit diesem Format wird der Typ einer Zahlungsbedingung
festgelegt.
(Formatname „ZBEDTYP“)
Nr.
Bezeichnung
Beschreibung
1
Fälligkeit in n Tagen
Fälligkeit der Zahlung beginnt nach
      der Zeitspanne von n Tagen abhängig vom Bezugsdatum
2
Fällig am Tag X des Folgemonats
      (Skto auf Bezug)
Fälligkeit der Zahlung zum genauen
      Stichtag im Folgemonat abhängig vom Bezugsdatum
Skonto berechnet sich in Tagen nach
      dem Belegdatum
3
Fällig am Tag X dieses Monats (Skto
      auf Bezug)
Fälligkeit der Zahlung am Stichtag
      des laufenden Monats abhängig vom Bezugsdatum
Skonto berechnet sich in Tagen nach
      dem Belegdatum
4
Fällig zum nächstmöglichen Tag X
      (Skto auf Bezug)
Wenn
      das Bezugsdatum der Fälligkeit
vor
dem Tag
X
des Monats
      liegt, wird der Betrag fällig am Tag
X
des
laufenden
      Monats
.
Wenn
      das Bezugsdatum der Fälligkeit
nach
dem Tag
X
liegt, wird
      der Betrag fällig am Tag
X
des
nächsten Monats
.
Skonto berechnet sich in Tagen nach
      dem Belegdatum
5
Fällig Monatsende
      Folgemonat
Fälligkeit der Zahlung zum
      Monatsende des Folgemonats abhängig vom Bezugsdatum
6
Fällig Monatsende aktueller
      Monat
Fälligkeit der Zahlung zum
      Monatsende des aktuellen Monats
7
Datum manuell eingebbar
Manuelles
      Fälligkeitsdatum
8
Fällig am Tag X der nächsten Woche
      (Skto auf Bezug)
Fälligkeit der Zahlung am Wochentag
      X in der nächsten Kalenderwoche
Skonto berechnet sich in Tagen nach
      dem Belegdatum
Als
      Wochentag wird hier Sonntag= 1, Montag = 2 usw. gerechnet
9
Fällig am Tag X des Folgemonats
      (Skto auf Fälligkeit)
Fälligkeit der Zahlung zum genauen
      Stichtag im Folgemonat abhängig vom Bezugsdatum
Skonto berechnet sich in Tagen vor
      dem Fäll
[...]


---

## Funktion Löschen/Wiederherstellen

Funktion Löschen/Wiederherstellen
Mit Hilfe der Funktionen
Löschen
und
Wiederherstellen
— die in Referenz-ERP auf der
Taste
F7
liegen — kann man
Kunden/Interessenten löschen oder gelöschte Kunden/Interessenten
wiederherstellen.
Siehe auch
Generelle Programmbedienung
.

---

## Generelle Programmbedienung

Generelle Programmbedienung
Referenz-ERP vereinigt alle bewährten Bedienmöglichkeiten
unter einer gemeinsamen Benutzeroberfläche.
Diese sind:
Aufruf der Programme mittels klassischer Menütechnik
über die Tastatur
direkter Funktionsaufruf über Tastatureingabe eines
Kürzels (Direktsprung)
Anwahl mittels Maus
Anwahl über Drop Down bzw. Popup Menü
Darüber hinaus kann die Bedieneroberfläche an die
Anforderungen der Betriebe, einzelner Abteilungen oder Mitarbeiter angepasst
werden.
Dies kann so weit gehen, dass einige Mitarbeiter nur
wenige Programmfunktionen angezeigt bekommen, während andere das komplette
Programmangebot nutzen können.
Nachfolgend wird jedoch vom
Standardauslieferungsumfang ausgegangen.
Es können sich somit im Einzelfall Abweichungen zur
vorliegenden Installation ergeben.

---

## Display

Display
DMD 202 Kundendisplay von EPSON
(an COM-Schnittstelle anschließen)
Zweitbildschirm
Als Kunden Display wird empfohlen einen Full HD (1920
x 1024) Monitor als zweiten Bildschirm zu wählen.

---

## Drucker

Drucker
Drucker wurden traditionell an den parallelen Port
(LPT) angeschlossen. Die Ansteuerung bedient diesen Post auch heute noch, auch
wenn dieser faktisch kaum noch hardwareseitig implementiert ist. Ein Drucker
kann jedoch an eine virtuelle LPT-Schnittstelle angeschlossen werden, die dann
die Daten weiterleitet.
TM 950 von EPSON mit Kassenschublade von
MOGLER
(wenn nicht vorhanden, Drucker über epson_bon.sql bzw.
epson_schacht.sql einspielbar)
OKIPOS90 Bondrucker
(wenn nicht vorhanden, Drucker über oki_bon.sql bzw.
oki_schacht.sql einspielbar)
STAR Bondrucker
(wenn nicht vorhanden, Drucker über star.sql
einspielbar)
Epson
Thermodirekt-Bonducker
Bixolon
SRP-350plusIII

---

## Bezahlterminals

Bezahlterminals
Wenn Sie die Bezahlung mit dem Bezahlterminal nicht
manuell, sondern mit einer Datenschnittstelle zwischen Referenz-ERP und dem
Bezahlterminal durchführen wollen, achten Sie darauf, dass das Terminal die
Schnittstelle ZVT700 unterstützt.
Es werden im Prinzip alle Bezahlterminals unterstützt,
die das Datenprotokoll ZVT700 unterstützen.
Die Anbindung des Terminals erfolgt über TCPIP, eine
Anbindung über RS232 wird nicht mehr unterstützt.
Im Terminal muss deshalb auch die Kommunikation mit
der Kasse auf LAN umgestellt sein.

---

## Erstellen eines Hinweises

Erstellen eines Hinweises
Hauptmenü
Administration
Firmenkonstanten
Bedienerbezogenes Hinweissystem
Direktsprung
[HINW]
Allgemeine Felder
Maskenfelder
Bedeutung
Typ
Hier
      kann zwischen Archiv, Hilfe, Internet/Intranet unterschieden
      werden.
Ident
Ist
      der Ident für die gültige Datei.
Gültig ab
Hier
      kann das Datum angegeben werden, ab wann die Meldung zu sehen ist.
      Standard ist das Tagesdatum.
Start Zeit
Hier
      kann die Uhrzeit angegeben werden, ab wann der Hinweis zu sehen sein soll.
      Standard ist 0 Uhr.
Gültig bis
Hier
      kann das Datum eingestellt werden wie lang die Information auf der
      Anzeigemaske beim Referenz-ERP-Start angezeigt werden soll. Standard ist das
      Tagesdatum.
End
      Zeit
Hier
      kann die Uhrzeit eingetragen werden, bis wann die Information gültig ist.
      Standard ist 23:59.
Register Allgemein
Maskenfelder
Bedeutung
Bezeichnung
Hier
      kann ein Kurztext eingetragen werden, der auf der Information Anzeigemaske
      angezeigt werden soll.
Bedienerklasse
Bestimmt für welche Bedienerklasse
      die Information gelten soll.
Priorität
Hier
      kann zwischen „Normal“ und „Hoch“ gewählt werden. Informationen, die eine
      hohe Priorität haben, stehen oben auf der Anzeigemaske.
Bedingt durch Prozedur
Gibt
      eine Datenbank-Prozedur an, die entscheidet, ob der Hinweis angezeigt
      werden soll.
Die
      Prozedur kann einen oder zwei Rückgabewerte haben. Der Rückgabewert mit
      Namen „
result
“ ist vom Typ Integer und muss in jedem Fall
      zurückgeliefert werden. Ist der Wert größer 0, so wird der Hinweis
      angezeigt.
Der
      zweite optionale Rückgabewert mit dem Name „
result_text
“ ist vom
      Typ char(255) und liefert einen Variablen Text zurück, der den unter
Bezeichnung
angegebenen Text überschreibt.
Typ
In Abhängigkeit des Typs muss im Feld Ident der
richtige Inhalt eingetragen werden. Der Inhalt des Feldes Ident enthält die
Identifikation des Do
[...]


---

## Identass Inventur Schnittstelle

Identass Inventur Schnittstelle
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
Inventurdaten können via Scanner erfasst werden.
Identass liefert hier eine Inventur Software, welche teils auf dem Scanner und
teils auf einem PC installiert wird.
Grundsätzlich werden alle gescannten
Daten in Referenz-ERP gespeichert. Die korrekt erfassten Daten sind direkt in einem
Inventurbuchungsblatt eingetragen und können dort weiter verarbeitet werden. Die
Daten mit manuellem Nachbearbeitungsbedarf sind in einer Puffertabelle mit
entsprechenden Hinweisen abgelegt. Im Anschluss an die manuelle Nachbearbeitung
können auch diese Daten in das Inventurblatt übertragen und dort weiter
verarbeitet werden. Diese Arbeitsweise lässt sich ggf. durch Steuerparameter
beeinflussen.

---

## IB Maskenbedingungen

IB Maskenbedingungen
Hauptmenü
Administration
Werkzeuge
IB-Maskenbedingung
oder Direktsprung
[IBMSK]
Wenn eine F3-Auswahl privatisiert wird und man auf ein
Feld zugreifen möchte, welches auf der aufrufenden Maske vorhanden ist, kann man
dies mit der Anwendung „IB-Maskenbedingung“ bewerkstelligen.:
Beschreibung
Name
Hier
      trägt man eine eindeutige Bezeichnung ein, mit der man später auf diese
      Einrichtung zugreift. In dem SQL-Text der zugehörigen F3-Auswahl muss man
      dann
:∼
dem Namen voranstellen.
Maske
Name
      der Maske, auf dem das Feld zu finden ist. Den Namen der Maske erhält man,
      indem man auf dieser Maske die Tastenkombination Umschalt-Strg-F5
      drückt.
Feld
Dies
      ist der Name des Feldes, dessen Inhalt man haben möchte. Hier ist es
      wichtig, dass Groß- und Kleinschreibung dabei beachtet wird. Den Namen des
      Feldes erhält man entweder über die Tastenkombination Umschalt-Strg-F5
      oder über Umschalt-F3.
Bedingung
Hier
      kann eine komplette Bedingung unter Verwendung irgend eines Namens mit
      vorangestelltem Doppelpunkt stehen
and :Name = 5
oder
      einfach nur der Name mit vorangestelltem Doppelpunkt.
:Name
Für
:Name
wir vom
      Programm der Inhalt des angesprochenen Feldes eingetragen. Existiert die
      Maske oder das Feld nicht, dann wird ein leerer Wert geliefert. Es
      erscheint keine Fehlermeldung
Beispiel:
Der SQL-Text der dazugehörigen F3-Auswahk kann dann
folgendermaßen aussehen:
TITLE Versandarten
INFO alle Versandarten
IB_LABEL Nummer ab
MASK ITEM60
FIELD   Nummer,VersArtId,I4,8
FIELD Bezeichnung,VersArtBezeich,char,40
FIELD Lagernumemr(SVMAIN),Wert,char,20
RETURN VersArtId, VersArtBezeich
SQL select :FIELDS,
':~LagerNummerAusIBMSK' as Wert
from amic_v_VersandArt
where (VersArtId >=':ITEMWAHL')
:LOOKUP
order by VersArtId
LOOKUP and (VersArtId = ':ITEMWAHL')
OPTIONBOX OB_IB_VERSANDART
Der Wert aus IBMSK ':~LagerNummerAusIBMSK' steht hier
in Hochkomma, damit es keine Syn
[...]


---

## Inventur mit der Vorgangsimport Schnittstelle

Inventur mit der Vorgangsimport Schnittstelle
Hauptmenü
Externe Kommunikation
Stammdatenimport
Vorgangsimport
Um eine Inventur mit dem Scanner über die
Vorgangsimport Schnittstelle
zu erfassen muss folgendes eingerichtet werden.
Folgende Steuerparameter müssen eingerichtet
werden
1.
Steuerparameter 727
2.
Steuerparameter 728
3.
Steuerparameter 801
4.
Steuerparameter 842
Folgende
Scancodes
müssen ausgedruckt
auswerden.
Ablauf der
Inventur
Um die Daten für die Inventur aufzunehmen muss als
erstes der Scancode
IV
mit dem Scanner erfasst werden. Der
Scancode
IV
startet nicht die Inventur, sondern nur
den Erfassungsblock. Es ist zu empfehlen, pro Regal ein Erfassungsblock zu
starten. Wird der Scancode
IV
während eines offenen Blockes ein
zweites Mal gescannt, so kommt die Meldung, dass es noch eine offene
Inventurerfassung gibt. Jetzt hat man zwei Möglichkeiten, entweder es werden
weitere Inventurdaten erfasst, oder mit nochmaligen Scannen des Scancodes werden
alle erfassten Daten im
Vorgangsimport
auf gelöscht gesetzt, und ein
neuer Inventurblock wird gestartet.
Stürzt die Scannersoftware ab, oder der Scanner muss
neugestartet werden, oder der Akku des Scanners ist leer, so kann nach dem
Neustart der Software mit dem aktuellen Block weitergearbeitet werden. Dazu
braucht man nur einen Artikel erfassen oder eine Menge eingeben. Fällt bei der
Erfassung des Scanners das WLAN aus, so werden alle erfassten Scancodes zwischen
gespeichert, bis ein rotes X angezeigt wird. Ist das WLAN wieder vorhanden, so
werden durch drücken auf das X die Daten übertragen. Wird die Software auf dem
Scanner neu gestartet, wenn das X Angezeigt wird so werden die erfassten Daten,
die im Speicher sind nicht neu übertragen.
Nach dem erfassen des Scancodes IV können jetzt die
Artikel erfasst werden. Bei der Erfassung eines Artikels wird dieser mit der
Menge 1 vorbelegt. Dies gilt auch für Gebindeartikel hier wird die Gebindeanzahl
mit 1 vorbelegt und die Ergebnismenge wird in d
[...]


---

## Krediterfassung

Krediterfassung

---

## Kreditlimit

Kreditlimit
Siehe Eingabe Kreditlimit

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

## Auswahl der Artikel

Auswahl der Artikel
In der Auswahlliste können zu zählende Artikel
ausgewählt und ein Report über diese Artikel und deren Standort gedruckt werden.
Nun sucht der Bediener die Standorte der Artikel auf.
Dort identifiziert er die Palette mit Hilfe der NVE und erhält die Information
über den Inhalt. Die Menge wird jedoch nicht angezeigt. Diese hat er nun zu
zählen und einzugeben.
Die Differenz, so es denn eine gibt wird gebucht und
im LVS-Bewegungsprotokoll als Bestandkorrektur festgehalten.

---

## Materialbedarf Produktion

Materialbedarf Produktion
Es gibt drei Möglichkeiten, den Bedarf der
Produktionslinie zu decken:
1.
Der Bediener schreibt manuell einen Materialbedarf für die Linie
(die für den Bediener
aufwändigste Lösung)
Der Bediener erstellt mit
dem Materialorder-Pfleger
[LVSMO]
eine Materialorder und legt dabei
Artikel, Partie, Menge und Mengeneinheiten fest.
2.
Der Linienbedarf wird errechnet
(die wohl technisch
aufwändigste Lösung)
Die Linie sendet ein
„BEGIN“, worauf hin die Produktion als aktiviert gilt. Bis zur Beendigung einer
Produktion mit „END“ aus der Produktionsschnittstelle gilt diese Produktion als
aktiv. Ein regelmäßig laufender Prozess rechnet den bedarf lauf Rezept durch,
summiert diesen über alle aktiven Produktionen und zieht davon Materialien ab,
die bereits in der Bereitstellungszone stehen bzw. dorthin unterwegs sind. Die
Differenz wird in eine Materialorder für die Linie geschrieben und allokiert.
Diese Implementation stellt hohe Anforderungen an die Produktionsschnittstelle
und muss in der Regel individuell abgestimmt werden.
3.
Die Produktionslinie fordert Materialien an.
(Die technisch einfachste
Lösung)
Dabei werden Artikelnummern
aus Referenz-ERP verwendet. Die Mengen werden in Kg bzw. Stück angegeben. In diesem
Fall wird die Materialorder über die Produktionsanbindung geschrieben. Diese
Lösung ist in der
Produktionsanbindung
implementiert.

---

## Produktionsanbindung

Produktionsanbindung
Es gibt für die Kommunikation mit Produktionssystemen
eine XML-Dateiaustausch-basierende Schnittstelle.
Diese Schnittstelle erledigt verschiedene
Aufgaben:
1.
Übertragung der Produktionsdaten an das Produktionssystem
Hier wird die
Komponentenliste mit den Mengen an die Produktion übertragen.
2.
Empfang von Materialbedarf
In Referenz-ERP wird eine
Materialorder [
LVSMO
]
erstellt.
3.
Empfang von Ware-Fertig-Meldungen
Hier werden in Referenz-ERP
Ladeträger an der Fertigstellungslokalität der Linie erstellt und beladen.
(siehe auch
[PRODL]
)
4.
Empfang von Verbrauchsmeldungen
Hier wird die verbrauchte
Menge vom Ladeträger in der Bereitstellungszone abgebucht. (siehe auch
[PRODL]
)
5.
Empfang von Fertigmeldung einer Produktion. Hier werden die Verbräuche und die
Produktmenge in der Produktion korrigiert.
Näheres dazu in
Produktionsinterface
.

---

## Dateiname im Mailversand

Dateiname im Mailversand
In den Standard-Versandfunktionen
ist beispielhaft implementiert, wie ein Dateiname mittels einer
Datenbankfunktion ermittelt wird. Diese kann im Steuerparameter „
822 - Belegversand Dateiname Funktion
“
pro Bediener festgelegt werden. Als Beispiel kann die Funktion
„AMIC_BelegVersandDateiname“ dienen.

---

## Maske Waagenprofil

Maske Waagen
profil
Allgemeine Felder
Profil
Waagenprofilname zur eindeutigen
      Identifikation des Waagenprofils. Dahinter folgt die Waagenprofil-ID (
      wp_id ) des Waagenprofils.
Bediener
Hier
      kann explizit das Waagenprofil für einen Bediener festgelegt
      werden.
Aktiv
Hiermit legt man fest, ob ein Profil
      für den Produktivbetrieb freigegeben ist.
(Es
      bedeutet also nicht, dass eine Waage gerade aktiv ist!)
Vorbelegung im Neu-Fall ist
      „Ja“
Funktionen
Hilfe
F1
      Öffnet die Hilfe
Speichern
F9
      Speichert Änderungen
Speichern unter…
SF9
      Möglichkeit zur Übernahme aus einem anderen Waagenterminal
Neu
F8
      Neuanlage
Berechnen
F10
Teste Port
F11
      sind die Angaben unter Port und Parameter gemacht worden kann man hier
      diese Einstellungen testen
Archiv anzeigen
CF12
      öffnet das Archiv zu diesem Waagenterminal
Ende
ESC
      Verlässt die Maske

---

## Aktualisierung der Nachhaltigkeitswerte

Aktualisierung der
Nachhaltigkeitswerte
Bei der Änderung von
Stammdaten
müssen die
Nachhaltigkeitsbewegungen nachkalkuliert werden. Da es sich bei den Bewegungen
um eine große Anzahl von Daten handeln kann und die erneute Berechnung der Werte
einige Zeit in Anspruch nimmt, wird die Berechnung durch den Mandantenserver
vorgenommen.
Aktualisierungseinstellungen
Auf der Maske lassen sich für einzelne Wochentage die
abzuarbeitenden Vorgänge je Intervall einstellen. Dadurch kann man den
Mandantenserver so einstellen, dass er am Tag wenig und in der Nacht viele
Belege abarbeitet. Somit kann verhindert werden, dass der Mandantenserver zu
Stoßzeiten zu lange blockiert wird.
Wenn Aktualisierungseinstellungen existieren, aber
kein passender Eintrag gefunden wurde, werden
keine
Belege abgearbeitet.
Sollten jedoch keine Aktualisierungseinstellungen existieren, wird die
Standardanzahl von
50
Belegen verwendet.
Zusätzlich zu diesen Einstellungen lassen sich ein
paar Einstellungen am
Steuerparameter
844
ändern.
Folgende Felder stehen zur Verfügung.
Feld
Beschreibung
Wochentag
Hier
      kann der Wochentag eingerichtet werden, für den die Anzahl gelten
      soll.
Von
Die
      Start Uhrzeit für die Anzahl Belege.
Bis
Die
      End Uhrzeit für diese Anzahl Belege.
Anzahl
Die
      Anzahl der zu verarbeitenden Belege.
Bei sich überschneidenden Zeiträumen gilt immer der
Eintrag, der am nächsten an der aktuellen Zeit dran ist und die niedrigste
Anzahl hat.
Beispiel:
Wochentag
Von
Bis
Anzahl
Montag
00:00
23:59
100
Montag
08:00
12:00
25
Montag
09:00
13:00
30
•
Um 6:45 würde der Wert 100 verwendet werden.
•
Um 8:35 würde der Wert 25 verwendet werden.
•
Um 9:43 würde der Wert 30 verwendet werden.
•
Um 12:51 würde der Wert 30 verwendet werden.
•
Um 14:42 würde der Wert 100 verwendet werden.
Staffelung
Zusätzlich existiert dann noch eine Staffelung der
Belege, je nachdem wieviel der Mandantenserver aktuell zu tun hat. Der
ermittelte Wert aus Wochentag und Uhrzeit wird
[...]


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
nicht vollständig zugeordnet wurden. Markiert man dort einen Beleg steht die
Funktion „Verteilung/Zuordnung“ zur Verfügung. Man kann hier die Anlage so
erfassen, dass sie dem Fibubeleg zugeordnet wird. Es ist dabei möglich bei
Belegen vom Typ Eingangsrechnung den Betrag auf mehrere Anlagegüter zu
verteilen. Es werden die bekannten Daten vorbelegt.
Werden in dieser Variante
mehrere Eingangsrechnungen markiert und dann die Funktion „Verteilung/Zuordnung“
ausgewählt, so geht das Programm davon aus, dass man diese Eingangsrechnungen
gesammelt einem einzigen Anlagegut zuordnen will. Man hat dann nur die
Möglichkeit einen neuen Anlageneintrag vorzunehmen oder ein bestehendes
Anlagegut auszuwählen.
3.
Direkt im Anlagenstamm über Neuerfassung.
Bei den ersten beiden Methoden erhält der Eintrag in
der Anlagenbuchhaltung einen Verweis zum Fibubeleg. Für den so entstehenden
Eintrag in der Anlagenbuchhaltung werden dann die Werte direkt übernommen.
Löschen in der Primanota wirkt sich
nicht
auf das Anlagegut aus. Lösch
[...]


---

## Auswahlliste

Auswahlliste
Hauptmenü
Administration
Steuerung
Optionen
oder Direktsprung
[OPT]
Felder der Auswahlliste
Felder
Beschreibung
Name
Name
      der Option
Beschreibung
Beschreibung der Option
Bediener
Bediener ID, bei welcher die Option
      angesprochen werden kann
Kurzname
Name
      des Bedieners
Wert
Der
      Wert welcher von Referenz-ERP ausgelesen wird
Global
Nur
      ja, wenn jeder Bediener auf die Option zugreifen kann
Suchmöglichkeiten der Auswahlliste
Suchen
Beschreibung
Option
Like
      …
Funktionen der Auswahlliste
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
Öffnet den Pfleger der Optionalen
      Parameter
Export Option
(Shift + F8)
Exportiert den ausgewählten
      Parameter

---

## Pfleger der Optionalen Parameter

Pfleger der Optionalen Parameter
Felder des Auswallistenpflegers
Feld
Beschreibung
ID
ID
      der Option (wird automatisch generiert)
Nur
      global
Legt
      fest, ob jeder Bediener auf diese Option zugreifen kann
Option Name
Name
      der Option (F3-Auswahl)
Beschreibung
Beschreibung der Option
Bediener
Legt
      fest für welchen Bediener diese Option zur Verfügung steht (setzt das „Nur
      global“-Feld automatisch auf nein, sobald dieses Feld mit einem Bediener
      gefüllt wurde
Wert
Der
      Wert welcher von Referenz-ERP ausgelesen wird
Funktionen des Auswahllistenpflegers
Funktion
Beschreibung
Speichern (F9)

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

## Programmstart

Programmstart
Durch ein ausgeklügeltes Schutzsystem wird
sichergestellt, dass nur autorisierte Benutzer
Referenz-ERP
bedienen können und
welche Funktionen ein Anwender zur Verfügung gestellt bekommt. Im System ist
hinterlegt, welche Funktionen einem Anwender mit einem bestimmten Passwort bei
einem Mandanten erlaubt sind. Erst die korrekte Eingabe dieser Kombination
öffnet die Tür zur Anwendung.
Beim Anwählen des
Referenz-ERP
- Systems muss zuerst
die Benutzerkennung - so wie sie im Bedienerstamm angelegt wurde - und
anschließend das Passwort eingegeben werden.

---

## Proxy-Tabelle

Proxy-Tabelle
Das externe Archiv bedient sich des Konzepts
sogenannter Proxy-Tabellen. Dadurch wird durch einen logischen Verweis eine
Tabelle einer anderen Datenbank eingebunden. Diese Einbindung geschieht mittels
Angabe einer ODBC-Verbindung.
In seltenen Fällen kann die händische Auffrischung
einer solchen Verbindung von Nöten sein.
Hierzu führe man in OSQL folgendes auf der
Nicht-Archiv-Datenbank
aus:
1.
select remote_location from sys.systable where table_name = 'formulararchiv'
Man merke sich den Wert der
unter remote_location angegeben ist!
2.
Drop table formulararchiv
3.
Create existing table admin.formulararchiv at ‘GEMERKTER WERT’
Dies veranlasst das System die Verbindung zu
refreshen.
Wie stellt man die externen Server eines Systems
fest?
select
srvid from sys.sysservers

---

## Qualitätswerte manuell eingeben

Qualitätswerte manuell
eingeben
Neben der automatischen Qualitätsberechnung können
Qualitätsmerkmale auch manuell eingegeben werden. So können Messergebnisse von
Proben in das System eingepflegt werden. Die manuell eingegeben
Qualitätsmerkmale sind an einem „Ja“ im Feld „manuell“ erkennbar.
Außerdem kann festgehalten werden, ob ein
Qualitätssatz noch aktuell ist oder ob die Werte veraltet sind. So werden zum
Beispiel, wenn ein manueller Qualitätsdatensatz erfasst wird, alle späteren
automatisch-berechneten Qualitätsdatensätze auf „nicht mehr aktuell“ gesetzt. So
bleiben die Datensätze erhalten, werden aber nicht mehr verarbeitet und können
nicht mehr bearbeitet werden.
Pro Ladeeinheit können mehrere Qualitätssätze
existieren, die sich durch den Zeitpunkt unterscheiden müssen. Der Zeitpunkt
kann dabei millisekundengenau angegeben werden.

---

## Replikationsmonitor – Subskriptionen / Publikationen

Replikationsmonitor – Subskriptionen / Publikationen
Felder
Remote-User
Name
      des ausgewählten Remote Benutzers
Subskriptionen
Gruppe der für den Benutzer
      angelegten Subskriptionen
Publikation
Publikation für die diese
      Subskription eingerichtet wurde
SUBSCRIBE BY
Der
      Wert des Ausdrucks "SUBSCRIBE BY" für die Subskription, falls
      vorhanden
Gestartet
Y =
      Ja
N =
      Nein
Publikationen
Name
      der ausgewählten Publikation.
Zeigt die Gruppe der Artikel
      (Tabellen) welche für die in der Gruppe „Subskriptionen“ ausgewählte
      Publikation.
Artikel
Tabellenname
WHERE
Diese Spalte enthält die
      Suchbedingung für Artikel, die eine Teilmenge von Zeilen enthalten, die in
      einer WHERE-Klausel festgelegt sind
SUBSCRIBE BY
Diese Spalte enthält den Ausdruck
      für Artikel, die eine Teilmenge von Zeilen enthalten, die in einem
      SUBSCRIBE BY-Ausdruck festgelegt sind
Tabellenbesitzer
Eigentümer der Tabelle
Artikel
Name
      des ausgewählten Artikels.
Zeigt die Gruppe der Spalten für den
      in der Gruppe „Publikationen“ ausgewählten Artikel.
Feldname
Wenn
      für den Artikel nur spezielle Felder ausgewählt wurden, so werden diese
      hier angezeigt. Ansonsten werden „Alle Felder“ des Artikels
      repliziert.
Suche Artikel
Übergibt die Eingabe an OSQL. Das
      dort angezeigte Statement einfach mit F9 ausführen und das Ergebnis
      betrachten.
Suche Feldnamen
Übergibt die Eingabe an OSQL. Das
      dort angezeigte Statement einfach mit F9 ausführen und das Ergebnis
      betrachten.
Funktionen
keine

---

## Rollenklassen: Pfleger

Rollenklassen: Pfleger
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenklasse
oder Direktsprung
[ROLLE]
Hier kann hauptsächlich die Zuordnung der
Rolle
zu den
Bedienerklassen
eingesehen werden.
Eine etwas dynamischere Herangehensweise ist z.B. mit
dem
Rollenpfleger
möglich.
Felder
Rolle
Zuordnung der Rollenklasse zur
Rolle
.
Bedienerklasse
Zuordnung der Rollenklasse zur
Bedienerklasse
.
Funktionen
Löschen (
F7
)
Löscht Rollenklasse.
Speichern (
F9
)
Speichert ggf.
      Änderungen.
Neu
      (
F8
)
Legt
      eine neue Rollenklasse an.
Speichern unter… (
Shift+F9
)
Übernimmt die Rollenklasse und
      bietet somit die Möglichkeit daraus eine neue Rollenklasse zu
      bilden.

---

## Rollenklasse

Rollenklasse
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenklasse
oder Direktsprung
[ROLLE]
Zuordnung der
Bedienerklassen
zu einer
Rolle
. Eine Bedienerklasse gehört
zu einer Rolle, oder eben nicht.
Die Funktionalität der Pfleger dieser Variante finden
sich auch in übersichtlicher Form zu jeweiligen Rolle im
Rollenpfleger
. Gleichwohl besticht diese
Variante in der Einfachheit, wenn es darum geht eine Bedienerklasse einer Rolle
hinzufügen bzw. zu entfernen.
Felder der Rollenklasse
Felder
Rolle
Zuordnung der Rollenklasse zur
Rolle
.
Bedienerklasse
Zuordnung der Rollenklasse zur
Bedienerklasse
.
Suchmöglichkeiten der Rollenklasse
Suchkriterien
Rolle
Like
Bedienerklasse
Von
      … Bis
D.h.
      man kann hier u.a. gezielt schauen, welche Bedienerklasse in welcher Rolle
      ist.
Funktionen der Rollenklasse
Funktionen
Neu
      (
F8
)
Anlage einer neuen
      Rollenklasse.
Es
      erfolgt eine automatische Übernahme einer evtl. Selektierung in der
      Auswahlliste und es wird die nächste Bedienerklasse, die in Frage kommt
      automatisch vorgeschlagen.
Das
      bedeutet das die Rollenkontexte, die die beteiligte Rolle zugeordnet haben
      nun der zugefügten Bedienerklasse ein Zugriffsrecht gewährleisten
      werden.
Bitte beachten Sie, dass die
      Zuordnungen in den Kontexten (und auch in dem Haupt-Menü) bis zum Ende des
      Programmes zwischengespeichert sind. Die beteiligten Funktionen/Kontexte
      werden also erst nach Neustart der jeweiligen Referenz-ERP die neue Situation
      erkennen.
Für
      Details siehe
Rollenklassenpfleger
.
Ändern (
F5
)
Ein
      Ändern im eigentlichen Sinne gibt es nicht da die Rollenklasse nur die
      Felder Rolle und Bedienerklasse beinhaltet.
Gleichwohl besteht die Möglichkeit
      per „Speichern unter…“ eine Rollenklasse als Vorlage für eine neue zu
      nehmen.
Für
      Details siehe
Rollenklassenpfleger
.
Ansehen (
F6
)
Ansehen der
      Rollenklasse.
Für
      Det
[...]


---

## Rollenstamm

Rollenstamm
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenstamm
oder Direktsprung
[ROLLE]
Es ergibt sich für jeden Kontext „Listen“ von
Bedienerklassen, die die Funktion ausführen dürfen. Eine Rolle ist ein Synonym
für eine solche Liste. Es ist eine bis zu 255 Zeichen umfassende freiwählbare
Zeichenkette, die innerhalb der Rollen eindeutig sein muss.
Es ist möglich für jeden Kontext eine eigene Rolle
anzulegen, da aber für den Großteil der Funktionen sich in der Praxis gleiche
Rollen ergeben, wird man sich für diese auf eine Rolle einigen wollen.
Felder des Rollenstamm
Felder
Beschreibung
Rolle
Eindeutiger Bezeichner für eine
      Rolle. Bis zu 255 Zeichen.
Die
      Bezeichner sind nach der Erstinitialisierung technisch anmutend
      durchnummeriert: R000R, R001R, R002R, … usw. Diese Bezeichnung hat den
      Vorteil in anderen Auswahllisten leichter auffindbar zu sein.
Es
      gibt eine nicht durch ihren Namen, der ist ebenso frei wählbar, aber durch
      ihre Funktionalität ausgezeichnete Rolle: Die sogenannte
Controller-Rolle
. Diese Controller-Rolle ist die
      Rolle, die neuen Kontexten -also Funktionen, die zu Kontexten hinzugefügt
      werden oder auch per Neuanlage oder Update ins System kommen- zugeordnet
      werden. Das System unterbindet das Löschen dieser Controller-Rolle bzw.
      stellt auch ggf. sicher das eine solche Controller-Rolle existiert, falls
      von Nöten. Eine Controller-Rolle muss es geben, um neue Funktionalitäten
      zunächst einmal nur eine dafür vorgesehenen Bedienerschaft zugänglich zu
      machen.
Anzahl Bedienerklassen
Informatorische Anzahl der
      zugeordneten Bedienerklassen zu dieser Rolle.
Es
      kann Rollen ohne Bedienerklassen geben. Ordnet man einem Kontext eine
      solche Rolle zu darf kein Anwender die betreffende Funktion in dem Kontext
      ausführen.
Anzahl Kontexte
Informatorische Anzahl der
      zugeordneten Kontexte zu dieser Rolle.
Je
      nach
[...]


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

## Rollen tauschen

Rollen
tauschen
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenstamm
oder Direktsprung
[ROLLE]
Hier kann auf einfache Weise von einer Ausgangsrolle
mit einer auszuwählenden Rolle die Bedienerklassenzuordnung und/oder die
Rollenkontexte ausgetauscht werden.
Felder:
Felder
Von
      der Rolle
Die
      Ausgangsrolle mit der etwas getauscht werden soll.
Wird
      mit der Rolle
Die
      Tauschrolle, die mit der Ausgangsrolle etwas tauscht.
Rollenklasse
Schalter, der angibt ob die
      zugehörigen Rollenklassen der beteiligten Rollen ausgetauscht werden
      sollen.
Nach
      dem Austausch besitzt die Ausgangsrolle die Bedienerklassen-Zuordnung der
      Tauschrolle und umgekehrt.
Rollenkontext
Schalter, der angibt ob die
      zugehörigen Rollenkontexte der beteiligten Rollen ausgetauscht werden
      sollen.
Nach
      dem Austausch besitzt die Ausgangsrolle die Rollenkontext-Zuordnungen der
      Tauschrolle und umgekehrt.
Funktionen:
Funktionen
Rolle umbenennen (
F5
)
Rolle umbenennen.
Speichern (
F9
)
Speichert ggf.
      Änderungen.
Neu
      (
F8
)
Legt
      eine neue Rolle an.
Speichern unter… (
Shift+F9
)
Übernimmt die
      Bedienerklassen-Zuordnung der Rolle und bietet somit die Möglichkeit
      daraus eine neue Rolle zu bilden.

---

## Kommandozeile

Kommandozeile
Folgende Kommandozeilenparameter stehen ab der
Version  8.3.2.XXX zur Verfügung.
Die Scanner Software kann auch per Kommandozeile
gestartet werden. Beim Start des Scanners per Kommandozeile besteht die
Möglichkeit eine XML Datei anzugeben, welche dann Automatisch startet.
Parameter
Wert
conn=
Wird
      eine Verbindungszeichenekette(Connectionstring) übergeben, so verbindet
      sich der Scanner mit der angegebenen Datenbank. Die Verbindungsdaten aus
      der dbconfig.xml werden nicht berücksichtig.
Beispiel:
eng=dbserver;dbn=datenbankname;uid=USER;pwd=PASSWORD;links=tcpip{HOST=ServerIp};pooling=false;idle=60;lto=30;
cf=
Mit
      dem Parameter kann ein Pfad zu einer alternativen Datei mit
      Verbindungsparameter angegeben werde.
scans=
An
      diesem Parameter kann ein Pfad zu einer XML Datei mit
Scanbefehlen
angegeben werden, die beim
      Starten der Software automatisch ausgeführt wird
scip=
Mit
      diesem Parameter kann dem Scanner eine IP-Adresse zugewiesen werden.
      Anhand dieser IP-Adresse werden die Steuerparameter aus dem Referenz-ERP System
      geladen. Diese IP-Adresse wird auch dazu verwendet um die erfassten Daten
      einem Scanner zuzuweisen.
Pip
Mit
      diesem kann dem Scanner eine Profil IP-Adresse mit gegeben werden. Anhand
      der Profil IP-Adresse wird aus der Datei mit den Verbindungsparameter der
      richtige Datensatz gelesen. Ist die Profil IP-Adresse in der Datei nicht
      vorhanden, so wird der Standard Datensatz gelesen.
Durch die Möglichkeit die Scanner mit Übergabe
Parameter  ab der Version 8.3.2.XXX zu starten ist es sinnvoll auf den
Scannern bat Dateien anzulegen, mit denen dann die Software gestartet werde
kann. Beispiel für eine Bat Datei auf dem Scanner
cd \windows\aeins
start Referenz-ERP.scanner.exe
conn=uid=USER;pwd=PASSWORT;dbn=DBN;eng=ENG;links=tcpip
Bei der Bat Datei für den Scanner ist darauf zuachten,
dass
immer
in das Referenz-ERP Verzeichnis gewechselt werden muss, um die
Scanne
[...]


---

## Schutzwort

Schutzwort
Hauptmenü
Administration
Steuerung
Schutzwort ändern
oder Direktsprung
[SCH]
Das Schutzwort aller Bediener wird bei der Neuanlage
mit Branchen-ERP vorbelegt. Nach wiederholter Eingabe des Schutzwortes wird abgefragt,
ob es in der ahoi.ini gespeichert werden soll. Wenn ja, wird es beim
Programmeinstieg vorgeschlagen – der Schutz entfällt also: Üblicherweise sollte
deshalb die Abfrage mit „nein“ beantwortet werden.

---

## Schritt 3 Einrichtung Fallbeispiel

Schritt 3 Einrichtung Fallbeispiel
Schritt 3.1: Szenario
Um das Belegfluss Modul so effektiv wie möglich zu
nutzen, muss man sich eine Aufteilung überlegen. Folgendes ist lediglich ein
Beispielaufbau:
Schritt 3.2: Poststelle
In der Poststelle sollen alle Daten ankommen, um diese
dort auf die Abteilungen aufzuteilen.
Private Prozeduren:
Datenbankvariable:
Um in einer privaten Prozedur festzustellen, mit
welchem Postfach diese aufgerufen wurde, kann die Datenbankvariable
DBVAR_BELEGFLUSS_POSTFACH
verwendet
werden. Diese Variable enthält die Postfach-ID und kann innerhalb der privaten
Prozeduren abgefragt werden. Nach dem Verlassen der Maske wird die
Datenbankvariable automatisch gelöscht.
Beispiel
declare dc_PostfachId
integer;
if VAREXISTS('DBVAR_BELEGFLUSS_POSTFACH') <> 0
then
select DBVAR_BELEGFLUSS_POSTFACH into
dc_PostfachId;
…
end if;
Anforderung:
CREATE PROCEDURE
"ADMIN"."p_BelegflussZeigePostfaecher_1" ()
result (nummer integer, bezeich char(255))
begin
select postfach as nummer, PostfachBezeich as
bezeich
from BelegflussPostfach
where 1 = 1
and Postfach in
(2,3)
EXCEPTION
when others then call fehlerprotokoll (
in_text='Problem bei BelegflussZeigePostfaecher '||errormsg()||' '||traceback()
);
END
Verarbeitung:
CREATE PROCEDURE
"ADMIN"."p_BelegflussGenehmigung_1" ( in in_GenehmigungsStufe integer,
in in_fa_id integer,
in in_fa_mndNr integer,
in in_angefordert integer,
in in_neueHaken char(255),
in in_entfernteHaken char(255))
result (status char(255))
begin
declare local temporary table
temp_PostfaecherNeu (postfach integer, primary key(postfach) ) on commit
preserve rows;
declare local temporary table
temp_PostfaecherEntfernen (postfach integer, primary key(postfach) ) on commit
preserve rows;
insert into temp_PostfaecherNeu (postfach) on
existing skip select trim(row_value) from sa_split_list(in_neueHaken,',');
insert into temp_PostfaecherEntfernen (postfach)
on existing skip select trim(row_value) from
sa_split_list(in_entfernteHaken,
[...]


---

## Steuerungsparameter des Vertreters

Steuerungsparameter des Vertreters
Über Steuerungsparameter können Voreinstellungen
vorgenommen werden. Sie finden sich in der Parametergruppe „Vertreter /
Provision“:
Standard Provisionierungsformel
Mit diesem SPA kann eingestellt werden, welcher Typ
zur Provisionsberechnung als Standardprovisionsberechnungstyp herangezogen
werden soll.
-1    =   Standard
Provisionsberechnung
0     =   keine
Provision
1     =   prozentuale
Provision vom Nettobetrag
2     =   prozentuale
Provision vom Bruttobetrag
3     =
mengeneinheitsbezogene Provision
4     =
gebindeanzahlbezogene Provision
5     =
gewichtsbezogene Provision
6     =   postenbezogene
Provision
7     =   pauschale
Provision je Vorgang
10   =   Staffelung in max. 10
Provisionsberechnungen (siehe unten Provisionsstaffelung)
11   =   Überschussprovision
101 =   rohgewinnbezogene Provision
Offene Posten berücksichtigen
Mit diesem Steuerparameter kann eingestellt werden, ob
offene Posten bei der Provisionsberechnung berücksichtigt werden.
JA =
Markierte Belege werden nur dann
provisioniert, wenn sie komplett an die FiBu übergeben wurden und somit keine
offenen Posten auf dem Beleg existieren.
Nein =
Es werden alle markierten Belege
provisioniert, die zumindest im Warenbuch eingetragen wurden.

---

## Stapel-Berechnung von Stoffstromdaten

Stapel-Berechnung von Stoffstromdaten
Mit dem Modul zur Stapel-Berechnung von
Stoffstromdaten können die zugehörigen Werte zu einer großen Zahl von
ausgewählten Warenbewegung neu berechnet werden. Aufrufbar ist das Modul in
diversen positionsorientierten Auswahllistenvarianten der
Vorgangsbearbeitungsmodule sowie in der Auswahllistenvariante ‚Produktion mit
Positionen‘ des Produktionsmoduls (zu beachten:
Stoffstromdaten in Produktionsbelegen
).
Die Auswahllistenvariante
‚Stoffstrom-Positionen‘
des Moduls
‚Vorgangsübersicht‘
stellt zu den per Bereichsauswahl zu selektierenden
Vorgängen nur Positionen zu denjenigen Artikeln dar, denen per
Artikelstamm-Zusammensetzung Stoffstrompositionen zugeordnet sind und eignet
sich daher besonders als Grundlage zur Änderung der Stoffstromdaten von ganzen
Vorgangsgruppen.
Das Berechnungsverfahren entspricht dem
des im
Stoffstromdaten-Editor
genutzten
Berechnungsverfahrens, insbesondere unter Berücksichtigung der jeweiligen
Einstellung des Merkmals
‚Herkunft der Werte‘.
Bei Auslösen der
Funktion durch Betätigen des Buttons
Stoffstrom-Daten neu berechnen
wird
die Berechnungsfunktion für alle ausgewählten Vorgangspositionen durchgeführt.
Wurden in den zugehörigen Artikelstamm-Zusammensetzungen Stoffstrom-Bestandteile
hinzugefügt, die in einer betroffenen Vorgangsposition noch nicht enthalten ist,
so werden diese mit dieser Funktion automatisch nachgetragen und berechnet.

---

## Stoffstromdatenberechnung mit Mengeneinheiten

Stoffstromdatenberechnung mit Mengeneinheiten
Manchmal hat man das Problem, dass Angaben für
Stoffstromanteile in andere Form vorliegen als sie benötigt werden. Ist zum
Beispiel eine Angabe für Phosphor (P oder PO4-P) x kg/kg gegeben, gebraucht wird
aber die Angabe P2O5 y kg/kg, so kann diese auch mittels speziell hierfür
einzurichtende Mengeneinheiten realisiert werden: P>P205 mit
Umrechnungsfaktor 2,2914 * dem üblichen Umrechnungsfaktor zur Grundmengeneinheit
(bei kg als Grundmengeneinheit = 1).
Derartige Umrechnungsfaktoren für die Umrechnung von
Nähstoffen zwischen Elementform und Oxidformen sind für gängige Handelswaren im
Internet zu finden.
Tipp: Wird der anzuwendende Umrechnungsfaktor aufgrund
der mangelnden Verfügbarkeit von Nachkommastellen zu ungenau, so kann der
Kehrwert als Umrechnungsfaktor in der Mengeneinheit mit gleichzeitiger
Aktivierung des Schalters ‚verwende 1/Umrechnungsfaktor‘ =‘Ja‘ eingetragen
werden!

---

## Stoffstromdatenberechnung per Datenbankprozedur

Stoffstromdatenberechnung per Datenbankprozedur
Die Berechnung der Stoffstrommenge erfolgt
grundsätzlich im Stoffstrommodul durch Ermittlung der resultierenden Menge aus
der Warenpositionsmenge und dem angegebenen Anteil in Verbindung mit dem
Anteiltyp (% oder als Anzahl Mengeneinheit / Stoffstrom-Grundmengeneinheit). Das
Ergebnis dieser Berechnung kann jedoch durch Einsatz einer privaten
Datenbank-Prozedur geändert werden.
Zum einen kann eine solche Prozedur für die eine oder
andere Stoffstromart in der Anwendung Bestandteile für den betreffenden
Bestandteil angegeben werden. Für die Namensgebung derartiger privater
Prozeduren ist lediglich zu beachten, dass diese mit
‚P_‘
beginnen und
ohne Parameter anzugeben sind.
Ist eine Datenbankprozedur für die zu
berechnende Stoffstromart angegeben, so wird diese mit Versorgung der im
Prozedurkopf angegeben Parametern nach der internen Wertberechnung aufgerufen
und anschließend das Prozedurergebnis verarbeitet.
Ist keine
stoffartspezifische Datenbankprozedur angegeben, so wird stattdessen, falls
vorhanden, die ebenfalls private Datenbankprozedur
‚p_StoffStromBerechnung‘
aufgerufen.
Während letztere
Datenbankprozedur nicht in der Datenbank vorhanden sein muss, wird bei nicht
Vorhandensein der angegebenen stoffstromspezifischen Datenbankprozedur eine
Fehlermeldung im Fehlerprotokoll erzeugt.
Das Berechnungsmodul erwartet als Ergebnis einer
derartigen Datenbankprozedur ein RESULT mit den Attributen
-
Aktion
integer
-
Anteil
decimal(20,8)
-
MEAnteil
integer
-
Menge
decimal(20,8)
-
BerechneMenge
integer
-
SetHerkunft
integer
Bedeutung der Werte:
-
Aktion
Nur wenn der Wert dieses Attribut =
1
ist werden die
zurückgegebenen Daten berücksichtigt. Andernfalls wird das vor Prozeduraufruf
ermittelte Ergebnis beibehalten.
-
Anteil
Ist der Wert des Attributs
Aktion = 1
, so ersetzt der im
Attribut
Anteil
zurückgegebene Wert den vor Prozeduraufruf ermittelten
Wert des Stoffstrom-Anteils.
-
MEAnteil
Ist der Wert des A
[...]


---

## Editieren von Stoffstromdaten

Editieren von
Stoffstromdaten
Mit dem Modul zum Ansehen und zur Korrektur von
Stoffstromdaten können die zugehörigen Werte zu je einer Warenbewegung angesehen
beziehungsweise geändert werden. Aufrufbar ist das Modul  in diversen
positionsorientierten Auswahllistenvarianten der Vorgangsbearbeitungsmodule
sowie in den dafür geeigneten Auswahllistenvarianten der Rohwarebearbeitung (zu
beachten:
Stoffstromdaten in
Rohwarebelegen
),  wie auch der Auswahllistenvariante
‚Produktion mit
Positionen‘
des Produktionsmoduls (zu beachten:
Stoffstromdaten in Produktionsbelegen
).
Die Auswahllistenvariante
‚Stoffstrom-Positionen‘
des Moduls
‚Vorgangsübersicht‘
stellt zu den per Bereichsauswahl zu selektierenden
Vorgängen nur Positionen zu denjenigen Artikeln dar, denen per
Artikelstamm-Zusammensetzung Stoffstrompositionen zugeordnet sind und eignet
sich daher besonders als Grundlage zur Änderung der Stoffstromdaten von ganzen
Vorgangsgruppen.
Dargestellt werden auf der Maske neben einigen Daten
zur Vorgangs- und Positionsidentifikation die zur angezeigten Position aktuell
gespeicherten Stoffstromdaten (Anteil, Anteiltyp und Stoffstrommenge) sowie
für Verkaufsbelege der (optional) anzugebende Lieferant
der Position.
Sind diesem Lieferanten im zugehörigen
Artikelstammsatz der Position individuelle Stoffstromparameter zugeordnet, so
ersetzen diese diejenigen aus der Artikelzusammensetzung. Für
Einkaufsbelege
ist dieses Maskenfeld nicht vorhanden, da der gesamte
Vorgang einem Lieferanten zugeordnet ist.
Wurde dem Artikelstamm seit der
Berechnung der Daten der Position in seiner
Zusammensetzung
ein weiterer
Stoffstrombestandteil hinzugefügt, so wird dieser mit dem dort angegebenen
Anteil, aber ohne berechnete Menge ebenfalls dargestellt, obwohl diese Daten
(noch) nicht zur Position gespeichert sind.
Die Funktion
‚Berechnen‘
löst eine Neuberechnung der dargestellten Werte aus. Mit der Funktion
‚Reset‘
können die Werte bei Fehleingaben wieder auf die ursprünglich
ei
[...]


---

## Stoffstromdatenberechnung mit prozentualem Anteil

Stoffstromdatenberechnung mit prozentualem Anteil
Bei der Berechnung
von Stoffstrommengen wird bei Angabe des Stoffstrom-Anteils in Prozent zunächst
die Kompatibilität der Mengeneinheit der Positionsmenge mit der Mengeneinheit
der auszuweisenden Stoffstrommenge geprüft. Bei inkompatiblen Mengeneinheiten
(zum Beispiel Liter versus Kilogramm) wird per in der Position angegebenem
Gewicht (zum Beispiel ermittelt aus der Gewichtsangabe pro Grundmengeneinheit im
Artikelstamm) der prozentuale Anteil der Positionsmenge in die Mengeneinheit der
auszuweisenden Stoffstrommenge umgerechnet.
Ist in einem solchen Fall kein
Gewicht in der Position eingetragen, weil es weder erfasst noch im Artikelstamm
eingetragen ist, so wird die Stoffstrommenge als dem prozentualen Anteil zur
Positionsmenge interpretiert.

---

## Stoffstromdatenberechnung bei Teildisposition

Stoffstromdatenberechnung bei  Teildisposition
Auch bei der Teildisposition erfolgt die Berechnung
von Stoffstrommengen wie im
Stoffstromdaten-Editor
beschrieben.
Bei
im Quellvorgang festgeschriebenen manuellen Stoffstrommengen ist hier in der
Regel eine Nachbearbeitung mittels
Stoffstromdaten-Editor
notwendig.

---

## Sperren in der Datenbank

Sperren in der Datenbank
In der Übersicht Systemlocks wird angezeigt welche
Benutzer welche Tabellen blockieren.
Spalten
Wer
Kürzel des Benutzers
Name
Voller Name des Benutzers, wie im
      Bedienerstamm hinterlegt
Tabelle
Tabelle die gesperrt ist
Typ
Art
      der Sperre:
Shared – Tabelle kann noch bearbeitet werden
Intent –
      Tabellenzeilen sind gesperrt
Verbindung
Hier
      steht die Verbindungsnummer

---

## Belegimport

Belegimport
Hauptmenü
Externe Kommunikation
Datendrehschreibe
Belegimport
Direktsprung
[TERRB]
Der Belegimport importiert Belege, meist
Eingangsrechnungen aus der TERRES Schnittstelle in Referenz-ERP.
Im Weiteren können die automatisch einfließenden
Eingangsrechnungen in das System übernommen werden. In einer Auswahlliste können
die Eingangsrechnungen mit dem passenden Eingangslieferschein verprobt werden
und nach Endkontrolle dann in das Referenz-ERP System eingespielt werden.
Allgemeine Einstellungen für den Belegimport müssen im
Steuerparameter „
829
“ hinterlegt sein.
Dem Referenz-ERPBeleg wird die erste Lagernummer aus dem
importierten Beleg zugeordnet.

---

## Textzeilen

Textzeilen
Hier erfolgt die Pflege des Artikeltextes im
Korrekturfall. Die Bedienung entspricht der der Neuerfassung.
Mit den Funktionen ‚Dokument als Anhang‘ und
‚Positionsdokument‘ wird der Dokumenten-Editor für das jeweilige Dokument
gestartet und die es lassen sich die Gestaltungsmöglichkeiten nutzen.
Hinweis
:
Vermeiden Sie automatische
Nummerierungen
wie sie zum Beispiel mit „Nummerierte Liste“ und
„Strukturliste“ erzeugt werden können. Unsere Druckaufbereitungsroutinen können
diese Features aktuell noch nicht wunschgemäß aufbereiten (bei Aufsplittungen
wird jeweils von vorne nummeriert).
Beim laden des Dokumentes, öffnet sich der
Dokumenten Editor

---

## Einrichtung

Einrichtung
Feld
Beschreibung
Tabellenname
Auswahl der zu Überwachenden
      Tabelle.
Bei
      gesperrten oder geblockten Tabellen, ist die jeweilige Zeile rot
      gekennzeichnet.
Es
      gibt zwei Besonderheiten bei den Tabellen:
1)   Wenn man die Tabelle
      „Kundenkredit“ überwacht, muss man auch das Feld KundKredit im Kundenstamm
      überwachen.
2)   Wenn man die Tabelle
      „KundForderGruppe“ überwacht, so muss man auch das Feld ForGrupNummer im
      Kundenstamm überwachen.
Es
      erscheinen bei der Einrichtung entsprechende Meldungen.
Tabellenfeld
Zeigt die Felder der ausgewählten
      Tabelle.
Überwachen?
Hier
      kann entschieden werden, ob das Feld überwacht werden soll oder
      nicht.
Hinweisfeld (unten
      links)
Es
      wird geprüft ob Tabellen aktuell für eine Bearbeitung durch einen
      Mitarbeiter gesperrt sind. Ist dies der Fall, so wird hier ein Hinweis mit
      der gesperrten Tabelle, sowie dem Benutzer, der die Sperre verursacht
      angezeigt.
Hilfe F1
Ruft diese Hilfe auf.
Alle Felder überwachen F5
Hiermit werden in alle Felder der Spalte
„
überwachen?
“ eine
JA
eingetragen.
Überwachung löschen F7
Hiermit werden in alle Felder der Spalte
„
überwachen?
“ eine
NEIN
eingetragen.
Speichern F9
Um die gewünschten Änderungen zu übernehmen, ist die
Funktion „Speichern“ im Funktionsmenü zu verwenden. Hierbei werden intern
private Trigger erstellt, welche eine Überwachung der gewählten Daten
gewährleisten sollen.
Sind hierfür benötigte Tabellen aktuell gesperrt, so
können keine Trigger angelegt werden. Erst nach Freigabe dieser Tabelle können
diese privaten Trigger erstellt werden.
Sollte es einmal nötig sein diese privaten Trigger neu
zu erstellen (z.B.: nah Änderungen am System oder den überwachten Tabellen), so
können Sie alle überwachten Felder einer Tabelle auf „Nein“ stellen und diese
Änderungen speichern. Die privaten Trigger dieser Tabelle werden entfernt. Nun
können Sie die Feldüberwachung für
[...]


---

## Verfahren

Verfahren
Das Verfahren mit dem Export durchgeführt werden
soll.
Es existieren momentan die Verfahren
1.
AMICAR
2.
XML

---

## Userfelder

Userfelder
Hier können zu den Standardvorgangsfeldern noch
weitere Felder in Abhängigkeit der Bedienerklasse, Vorgangsklasse und der
Vorgangsunterklasse angezeigt werden.
Positionierung
Die Felder können dabei frei auf der Maske
positioniert werden. Um die Einrichtung zu erleichtern, werden die Koordinaten
beim Erstellen eines neuen Feldes automatisch vorgegeben.
Wird das erste Feld eingefügt, stehen die Bezeichnung
und die Beschreibung in Zeile 13,79 und der Wert in Zeile 13,36. Die
Spaltenwerte sind 0,5 für die Bezeichnung, 18,17 für den Wert und 38,00 für die
Beschreibung. Wenn schon Felder existieren und der Cursor in die erste freie
Zeile bewegt wird, wird das Feld bestimmt, das am weitesten unten steht. Auf die
Zeilenwerte dieses Feldes wird 1,71 addiert, um die neuen Zeilenwerte zu
erhalten. Die Spaltenwerte für das neue Feld übernommen.
Wird per
F8
zwischen zwei bestehenden Feldern ein neues Feld eingefügt, werden alle
nachfolgenden Felder nach unten verschoben, indem 1,71 auf die Zeilenwerte
addiert werden.
Das Verhalten beim Löschen eines Feldes kann mit einem
Einrichterparameter bestimmt werden. Es besteht die Wahl zwischen:
-
Alle nachfolgenden Felder rücken automatisch eine Zeile nach oben
-
Die nachfolgenden Felder bleiben an ihrer alten Position
-
Bei jedem Löschen wird nachgefragt, ob die Felder nachrücken sollen
Maskenfelder
Feld
Bedeutung
Feldgruppe
Folgende Gruppen stehen zur
      Verfügung
1.   Strecke
2.   Text1
3.   Umbuchung
4.   Vorgang
Bed.Klasse
In
      diesem Feld wird die Bedienerklasse hinterlegt, welche die zugordneten
      Userfelder bei der Vorgangserfassung sehen darf.
Vorg.Klasse
Folgende UFLD Felder werden bei
      dieser Vorgangsklasse angezeigt
Unterklasse
Folgende UFLD Felder werden bei
      dieser Vorgangsunterklasse angezeigt
Gridbeschreibung
Bezeichnung
Bedeutung
Bezeichnung
In
      diesem Feld steht die Bezeichnung des UFLD Feldes
Feld
ID
      Nummer des UFLD Feldes
Schnellerfassung

[...]


---

## Vertretergruppen Variante 1

Vertretergruppen Variante 1
Felder:
Feld
Bedeutung
Nr
Nummer der Gruppe
Bezeichnung
Bezeichnung der Gruppe
Berechnungs-Variante
Gibt
      die Berechnungsvariante der Gruppe an
Anteilsausschöpfung
Gibt
      die prozentuale Ausschöpfung der Vertretergruppe an
Einzelprovision
Gibt
      an, ob die Gruppe eine Einzelprovision hat.
Suchmöglichkeiten
Feld
Bedeutung
Vertretergruppe
Von…
      Bis…
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

## Vertretergruppen Variante 3 (Fehlerhafte Vertretergruppen)

Vertretergruppen Variante 3 (Fehlerhafte Vertretergruppen)
Felder:
Feld
Bedeutung
Nr
Nummer der Gruppe
Bezeichnung
Bezeichnung der Gruppe
Berechnungs-Variante
Gibt
      die Berechnungsvariante der Gruppe an
Anteilsausschöpfung
Gibt
      die prozentuale Ausschöpfung der Vertretergruppe an
Einzelprovision
Gibt
      an, ob die Gruppe eine Einzelprovision hat.
Suchmöglichkeiten
Feld
Bedeutung
Vertretergruppe
Von…
      Bis…
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

## Vertretergruppen Variante 4 (Unvollständige Vertretergruppen)

Vertretergruppen Variante 4 (Unvollständige Vertretergruppen)
Felder:
Feld
Bedeutung
Nr
Nummer der Gruppe
Bezeichnung
Bezeichnung der Gruppe
Berechnungs-Variante
Gibt
      die Berechnungsvariante der Gruppe an
Anteilsausschöpfung
Gibt
      die prozentuale Ausschöpfung der Vertretergruppe an
Einzelprovision
Gibt
      an, ob die Gruppe eine Einzelprovision hat.
Suchmöglichkeiten
Feld
Bedeutung
Vertretergruppe
Von…
      Bis…
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

## Vorgangsimport Schnittstelle

Vorgangsimport Schnittstelle
In diese Schnittstelle können Vorgangsdaten in das
Referenz-ERP System importiert werden, aus denen dann ein Referenz-ERP Vorgang erzeugt
werden kann.

---

## Vorkasse

Vorkasse
In Referenz-ERP gibt es jetzt die Möglichkeit Vorkasse
Lieferungen zu erfassen. Mit der Vorkasse kann erreicht werden, dass Kunden
Lieferungen bis zur Höhe des Kreditlimits plus eingegangene Zahlungen erhalten
können, da die zu liefernde Menge anhand der Liquidation berechnet wird.
Das Vorkassen Modul wird über das
Streckenmodul
aufgerufen. Dies bedeutet, dass alle
Belege sowie Kontrakte, die an diesem Geschäft beteiligt sind werden bequem in
einer Strecke angezeigt.

---

## Mailversand allgemein

Mailversand allgemein
Es gibt viele Quellen, die E-Mails aus Referenz-ERP
versenden möchten. Alle diese Mailquellen sollten im Idealfall die gemeinsame
Schnittstelle zum Versand von E-Mails verwenden.
Voraussetzung für den Versand von Belegen ist,
•
dass diese ins Archiv gedruckt wurden / werden
•
dass der Mailempfänger bekannt ist oder im Rahmen der Abarbeitung bekannt
gemacht wird
•
dass der Zugang zum Mailserver im Versandprofilstamm hinterlegt ist oder
die Daten an die Schnittstelle übertragen werden.
Pflege
•
Kundenstammpflege
•
Kundenanschriftenpflege
Verwendung
•
Quellen für den
Mailversand
•
Auswahlliste
[MAIL]

---

## Wiegen (letzte Vorlage) CF8

Wiegen (letzte Vorlage) CF8
Beim Aufruf dieser Funktion startet die Wiegemaske mit
der vom Bediener zuletzt verwendeten Vorlage (siehe dazu auch
Vorlage einrichten
).
Vergleiche
dazu die Möglichkeit private Funktionen zum Aufruf der Wiegemaske mit bestimmten
Vorlagen einzurichten (Funktion:
Vorlage als Menüpunkt
).

---

## Vorgang editieren F5

Vorgang editieren F5
Vorgang editieren öffnet bei einer Wiegung mit Status
‚mit Vorgang’ den entsprechenden Vorgang zum Editieren.

---

## Vorgangdrucken

Vorgangdrucken
Druckt die Vorgänge aus, die aus dem Waagen-Beleg
erzeugt worden sind. Es wird der Default Drucker des Bedieners genommen

---

## Vorgang erz. / edit. SHIFT+F6

Vorgang erz. / edit. SHIFT+F6
Diese Funktion erzeugt einen Vorgang und öffnet diesen
zum Editieren. Vorgänge können nicht im Stapel erzeugt werden, sondern nur für
jeden Waagedatensatz einzeln. Bevor der Vorgang zum Bearbeiten geöffnet wird,
muss darauf gewartet werden, dass der Beleg im Mandantenserver verarbeitet
worden ist. Während des Wartens wird abgefragt, ob man warten möchte bis der
Beleg freigegeben worden ist. Wird diese Frage verneint, so wird der Beleg nicht
im bearbeiten Modus geöffnet.
Der Vorgang ist trotzdem erzeugt worden.

---

## Registerkarte Schnittstelle / ME

Registerkarte Schnittstelle / ME
Hier wird der technische Anschluss eines Wägesystems
abgehandelt.
Schnittstelle / ME
Typ
Typ
      des Waagen-Anschlusses
Mögliche
      Anschlussarten
Knopf „Editieren“
Wird
      die Anschlussart „XML“ verwendet, so ist dieser Knopf aktiviert und
      ermöglicht das Editieren eines im Archiv abgelegten
      XML-Dokuments.
Im
      Neu-Fall sorgt dieser Knopf für die Erstellung eines XML-Templates,
      welches dann auch zum Editieren geöffnet wird.
XML
      kopieren von…
Wird
      die Anschlussart „XML“ verwendet, hat man an dieser Stelle die
      Möglichkeit, ein bereits in einem anderen Waagenprofil verwendetes
      XML-Dokument in das gerade bearbeitete Waagenprofil zu
      übernehmen.
Parameter
Siehe
Parameter
Prozedur
Name
      der SQL-Prozedur zur Auswertung der Wiegeergebnisse
Zusatzversuche
Maximal-Anzahl
      der Wiederholungsversuche
Standard ist 0,
      das bedeutet mindestens eine Wiegung
Status
Verfügbarkeit des
      ausgewählten Ports
.
Sind
      die Angaben unter Port und Parameter gemacht worden kann man nun mit der
      Funktion „Test Port“ die Einstellungen testen.
Es
      erfolgt eine technische Status-Überprüfung im Rahmen des Möglichen und das
      Ergebnis wird hier repräsentiert.
Die
      Prüfung bedeutet noch nicht, dass man Kontakt zur Waage hat, sondern nur,
      dass die technischen Möglichkeiten auch so gehalten sind, dass eine
      Kontaktaufnahme physikalisch sinnvoll wäre …
Gibt
      es hier einen „Status“ „NICHT OK“, dann sollte geprüft werden, ob z.B. der
      verlangte COM-Port am administrierenden Host auch vorhanden ist, oder im
      Falle des UDP-Systems auch der angegebene Host kontaktierbar
      ist.
ME-Nummer
Hier
      hinterlegt man die Grundmengen-Einheit der Waage
Host/IP
Durch die Angabe eines expliziten
      Hostnamens kann bewirkt werden, dass das Waagenprofil nur an dem hier
      angegebenen Host zur Verfügung steht
Hostport
Hier
[...]


---

## Wissenswertes zur Auswahlbox

Wissenswertes zur Auswahlbox
Um die Problematik mit externen Formulararchiv und
internen Joins in den Griff zu bekommen, bedient sich das Formulararchiv der
Technik, die Daten in einer temporären Tabelle zusammenstellen und auf diesen
die internen Joins ablaufen zu lassen.
Die Auswahlliste ist um diese Fähigkeit erweitert
worden, um die stringgemäße Übergabe zu ermöglichen. Dazu expandiert das System
an den Stellen wo „:§“ entsprechende Zeichenketten SQL-Syntax-gerecht auf.
// Auswahllistenfunktion :
Formulararchiv
TITLE FormularArchiv
INFO FormularArchiv
MASK AW_MASK
FIELD ID,
     FA_ID,
I4  , 8,HIDDEN
FIELD
KndNr.,
FA_Kundennummer,  I4,   8
FIELD
Beleg-Typ,
FA_BelegtypText,  char, 22
FIELD
Beleg-Nr,
FA_BelegNummer,   char, 10
FIELD Beleg-Datum,
FA_BelegDatum,    char, 10
FIELD
Archiv/Druck-Datum,
FA_DruckDatum,    char, 17
FIELD Beleg-Referenz,
FA_BelegReferenz, char, 10
FIELD Herkunft,
FA_Herkunft,      FS FAHerkunft
FIELD Anleger,
FA_NeuAnlageBediener,char,8
FIELD Inhalt,
FA_Mime,          char, 20
FIELD Beleg-Klasse,
FA_Belegklasse,   FS FAKlasse
FIELD
Mnd,
FA_Mandant,       char, 8
FIELD
MndNr,         FA_MndNr, I4,
8,HIDDEN
FIELD Autor      ,
fa_info_autor       , char, 16
FIELD Betreff    ,
fa_info_betreff     , char, 16
FIELD Titel      ,
fa_info_titel       , char, 16
FIELD Kategorie  , fa_info_kategorie   ,
char, 16
FIELD Kommentar  , fa_info_kommentar   ,
char, 16
FIELD Stichwörter, fa_info_stichwoerter, char, 16
SQL
select :FIELDS from amic_fa('
:§AUSW_1
:§AUSW_2
:§AUSW_3
:§AUSW_4
:§AUSW_5
:§AUSW_6
:§AUSW_7
:§AUSW_8
:§AUSW_9
:§AUSW_10
:§AUSW_11
:§AUSW_12
:§AUSW_13
:§AUSW_14
:§AUSW_15
:§AUSW_16
')
where ( 1= 1 )
:ZUSATZ
:ZUSATZ1
:ZUSATZ2
:ZUSATZ3
and
(amic_fa_bedkl(db_bedienerklasse,fa_bedienerklasse) is not null)
order by FA_Druckdatum desc
RETURN FA_Id,FA_Mandant,FA_MNDNR
IDENT FA_Id,FA_Mandant,FA_MNDNR
IDSQL select *
from FormularArchiv
[...]


---

## Zuordnung von Funktionen zu Bedienerklassen (Rollen)

Zuordnung von Funktionen zu Bedienerklassen (Rollen)
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
oder Direktsprung
[ROLLE]
Das Schutzsystem für Funktionen wird über die
Zuordnung von
Bedienerklassen
zu Funktionen geregelt. So
steht für jede Funktion fest, ob eine Bedienerklasse diese ausführen darf oder
nicht. Da eine Funktion in mehreren Kontexten innerhalb von Referenz-ERP verwendet
werden kann, ist jeden solchen Vorkommen ein Schutz zugeordnet.

---

## Ableitung (XML-Beschreibung)

Ableitung (XML-Beschreibung)
Die Ermittlung der Dokumente erfolgt auf Basis eines
SQL welches durch folgende XML-Beschreibungssprache mitgestaltet werden
kann.
Element
Description
Name
Informatorisch der Name der
      Beschreibung.
RowHeight
Höhe
      einer Datenzeile in Pixel.
(Standard bzw. Vorgabe ist
      22)
Version
Informatorische
      Versionsnummer.
Field
Name
Name
      für die Zuordnung eines Sql-Elementes.
Caption
Die
      Spaltenüberschift.
Sql
Ist
      ein Sql angegeben dann ist das Ergebnis dieses Sql’s der
      Spalteninhalt.
WidthDisplay
Opt.
      vorgebbare Start-Spaltenbreite in Pixel.
Format
Opt.
      Angabe eines Aeins-Formats für die Darstellung des Wertes.
Mime
Standard: false
Stellt den Mime-Typen (fa_mime) als
      Mini-Icon in der Spalte dar.
Icon
Standard: false
Wenn
      angegeben, dann sollte der zugehörige Wert über Sql einer der folgenden
      fest vorgegebenen Möglichkeiten  sein:
„plus“
„minus“
„clip“
Visible
Standard: true
Damit lässt sich also eine Spalte
      „wegblenden“, der Wert wird aber ermittelt.
With
Der
      Wert des Elements gibt die With-Erweiterung vor.
Limitation
Der
      Wert des Elements gibt die Limitierung der Anzahl der Datensätze
      an.
Beispiel: top 50
From
From-Klausel
Standard:
from formulararchiv
      fa
Join
Opt.
      zusätzliche Join-Klausel
Where
Where Klausel.
GroupBy
GroupBy-Klausel.
Die Klauseln können mit einem Condition-Attribut
dekoriert werden. Der Condition-Ausdruck kann einen Gleichheitsoperator (==)
oder einen Ungleichheitsoperator (!=) beinhalten. Es werden damit nur Strings
verglichen. Ist eine „Profil-Zuordnung“ dem Archiv-Profil zugeordnet, dann
findet ein Colon-Processing statt.
Hierbei gibt es eine Besonderheit wenn die
Auswahl-Variable „AUSW_VT“ verwendet wird: In diesem Falle behält sich
letztendlich Referenz-ERP vor den Inhalt in Abhängigkeit des Volltext-Systemstatus
weiterzuleiten.
Neben den XML-Kommentaren ist es zusätzlich noch
möglich innerh
[...]


---

## Aktivierung des neuen Auswahllisten-Designs

Aktivierung des neuen
Auswahllisten-Designs
Hauptmenü
Administration
Firmenkonstanten
Bediener
Register Auswahlliste
oder Direktsprung
[BD]
Bei neuanlage eines Bedieners ist die neue
Auswahlliste aktiv, kann aber pro Anwendung auf das alte Design zurückgestellt
werden. Des geschieht im Bedienerstamm (Direktsprung
[BD]
) auf dem Register Auswahlliste. Als
erstes kann man sich entscheiden, was für den Benutzer standard sein soll.
•
folgende Anwendungen mit der neuen Auswahlliste darstellen:
Hier
bleibt Grundsätzlich das alte Design aktiv, bis auf die in der darunter
liegenden Tabelle ausgewählten Anwendungen. Dies ist zur Zeit die
Standardeinstellung.
•
folgende Anwendungen NICHT mit der neuen Auswahlliste darstellen:
Hier ist die Sichtweise genau anders herum. Das neue Design ist
grundsätzlich aktiv, bis auf die Anwendungen, die man in der Tabelle angegeben
hat.

---

## Branchen-ERP TCP-Client

Branchen-ERP TCP-Client
Es wird die Verwendung
dieses Clienten nicht länger empfohlen. Bitte stellen Sie wenn möglich auf
Aeinswiege
um!
Nach den guten Praxis-Ergebnissen des UDP-Clienten ist
dieser, um die Möglichkeit auch auf TCP basierende Systeme bedienen zu können
erweitert worden.
Um die neuen Möglichkeiten zu demonstrieren, verwende
ich den exemplarischen Zugriff auf unseren Webserver, der sollte Internetzugang
vorausgesetzt für Testzwecke wie diesen dann verfügbar sein.
Neu hinzugekommen ist das sogenannte „technische
Protokoll“. Das ist notwendig um zwischen UDP- und TCP_Systemen unterscheiden zu
können. Als logisches „Protokoll“ wird höchstwahrscheinlich in allen Anwendungen
„Ohne Protokoll“ aktiviert sein. Beachten Sie bitte das bei Verwendung von
Hardware-Lösungen die einen COM-Port umsetzen auf TCP es unter Umständen nötig
ist das der Client eine entsprechende Protokoll-Anbindung erfährt, um solche
Systeme auch „logisch“ bedienen zu können. Der Client besitzt außer dem
einfachen Protokoll „ohne Protokoll“ ( was „schicken-warten-Holen“ bedeutet )
noch Anpassungen für die wesentlichen komplexeren Protokolle DDP-Protokolle.
Grade auch bei der 1:1-Umsetzung von COM auf TCP kann
es nun passieren das den Wiegesystemen nicht druckbare Steuerzeichen, also
solche z.B. im Bereich von 0 – 31 gesendet werden müssen. Für diese
Spezialzeichen ist eine Metasprache analog den Referenz-ERP-Profilen eingeführt
worden. So versendet man beispielsweise ein „Cariage Return (13)“ über das
Metazeichen {CR}.
Es gilt die Umsetzung des Referenz-ERP-Formates
COMBITHELPER, also
Bitte beachten Sie den Unterschied bei den Klammern,
es werden geschweifte statt der Runden verwendet. Das ist notwendig, da der
Waagenclient  über Kommandozeile aufgerufen wird und die Kleiner bzw.
Größerzeichen dort Umleitungen bedeuten!
Neben der eigentlichen Ergebnisdatei ist es nun noch
möglich eine Logdatei zu schreiben die hauptsächlich dazu dient zu sehen, wann
der Client genau welche Zeichen sen
[...]


---

## Ansicht

Ansicht
Dokumentenansichten:
Funktion
Beschreibung
Seitenlayout
Setzt den Editor in den
      Seitenansichts-Modus
Vollbildmodus
Setzt den Editor in den
      Vollbild-Modus
Zoom:
Funktion
Beschreibung
Zoom
Zoom
      in das Dokumment
100%
Setzt den Zoom wieder zurück auf
      100%
Ganze Seite
Zoomt den Editor so, dass die ganze
      Seite zu sehen ist
Seitenbreite
Zoomt den Editor so, dass die Breite
      des Dokuments bis an den Rand geht
Textbreite
Zoomt den Editor so, dass der Text
      des Dokumentes bis an den Rand geht
Lineale und Statusleiste:
Funktion
Beschreibung
Horizontales Lineal
Zeigt eine Statusleiste an
      (oben)
Vertikales Lineal
Zeigt eine Statusleiste an
      (links)
Statusleiste
Zeigt eine Statusleiste an
      (unten)
Anzeigen:
Funktion
Beschreibung
Tabellen-Rasterlinien
Ausblenden
Anzeigen
Textmarken
Ausblenden
Anzeigen
Textrahmenbegrenzungslinien
Ausblenden
Anzeigen
Form-Begrenzungslinien
Ausblenden
Anzeigen
Kontrollzeichen
Ausblenden
Anzeigen
Textanker für Objekte
Ausblenden
Anzeigen

---

## Anzeigen / Bearbeiten

Anzeigen / Bearbeiten
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Anzeigen / Bearbeiten
F5
Direktsprung
[ECL]
Um einen Bankbeleg bearbeiten zu können, muss
Beleg/Kontoauszug markiert werden und gelangt man nach
F5
„Anzeigen/Bearbeiten“
in eine weitere
Auswahl, die zu dem angewählten Beleg/Kontoauszug die einzelnen Positionen
anzeigt. Oder man verwendet direkt die Variante „Einzelpositionen“.
Personenkonten, die mit einer Zahlsperre versehen sind, werden in diesen
Auswahllisten mit
gelbem Hintergrund
dargestellt. Sind einem Sachkonto Steuern zugeordnet, zu denen kein Eintrag im
Steuersatz existiert, so werden die Steuerinformationen mit
rotem Hintergrund
dargestellt. Diese Positionen
können dann mit
F5
direkt bearbeiten werden oder Verwendungszweck,
Auszifferungsvorschlag bzw. die Kontenaufteilung ansehen bzw. überprüft werden.
Solange der Beleg nicht in die Primanota übertragen wurde, lassen sich folgende
Felder bearbeiten:
Kontonummer
Jedoch nur, wenn keine
      Kontenaufteilung vorgenommen wurde und noch kein Auszifferungsvorschlag
      besteht. Die Kontonummer kann über eine F3-Auswahl ausgewählt werden. In
      dieser F3-Auswahl existieren Varianten, bei denen direkt ein Beleg
      auswählt werden kann (Pers.Kto nach Belgnr., Pers.Kto nach Betrag, … ).
      Wird das Personenkonto über eine dieser Varianten ausgewählt und passt der
      Betrag mit dem Betrag auf dem Kontoauszug überein – ggf. mit Skonto, dann
      wird für diesen Beleg sofort ein Auszifferungsvorschlag
      gebildet.
Wertstellung
Dieses Datum wird als
      Werstellungsdatum in die Primanota übernommen und u.a. verwendet, um den
      in Referenz-ERP gepflegten Währungskurs zu bestimmen.
Kurs
Der
      Kurs wird nur angezeigt, wenn es sich um eine Position in Fremdwährung
      handelt. Beim Einlesen der Daten wird der Kurs laut den in Referenz-ERP
      gepflegten Währungskursen vorbelegt und kann direkt hier in der Erfassung
      geändert werden.
Ste
[...]


---

## Archiv-Ansichten: Technische Unterstützung

Archiv-Ansichten: Technische Unterstützung
Unterstützende
      Datenbank-Objekte
View
amic_v_fa_view_profil_deliver
Liefert die von Branchen-ERP ausgelieferten
      Archiv-Ansichten für die Bedienerklasse -1.
Schlüssel favp_id, favp_besitzer aus
      fa_view_profil und den Kernbegriff den Profilnamen favp_name
View
amic_v_fa_view_profil_deliver_privat
Liefert die Privatierungen von Branchen-ERP
      ausgelieferten Archiv-Ansichten
Schlüssel favp_id, favp_besitzer aus
      fa_view_profil und den Kernbegriff den Profilnamen favp_name  sowie
      den Schlüssel der dazugehörigen Branchen-ERP-Auslieferung der Ansicht
View
amic_v_fa_view_profil_privat
Liefert diejenigen privaten
      Archiv-Ansichten die weder gemäß amic_v_fa_view_profil_deliver eine von
      Branchen-ERP ausgelieferte Archiv-Ansicht sind noch eine daraus privatisierte
      Archiv-Ansicht sind (siehe auch
      amic_v_fa_view_profil_deliver_privat)
Geliefert werden Schlüssel favp_id,
      favp_besitzer aus fa_view_profil und der Kernbegriff Profilname
      favp_name

---

## Archiv mit der Auswahlliste 2.0

Archiv mit der Auswahlliste 2.0
Wenn man die Auswahlliste
2.0 im
Bedienerstamm
aktiviert hat, so
werden auch die Archiv-Anwendungen mit der Auswahlliste 2.0 dargestellt. Auf der
rechten Seite erscheint ein Bereich, der das Archiv-Dokument darstellt. Dieser
kann genau wie vorher in der Dokumentenverwaltung ein und ausgeblendet werden.
Ob die Auswahlliste diesen Bereich darstellt hängt lediglich davon ab, ob die
Felder FA_ID und FA_MNDNR in der Variante existieren.
Zusätzlich entfallen für die
neuen Archivanwendungen die Funktionen „Druck/Quickreport“ und „Favoriten“.
Funktion
Beschreibung
Archiv anzeigen
Öffnet den für den Mime-Typen vom
      Windows-System vorgesehenen Viewer.
Das
      kann für PDF-Dateien z.B. der Adobe Acrobat-Reader sein, für Mails z.B.
      Outlook.
Eine
      detaillierte Aufstellung welche Mimetypen für die Vorschau vorgesehen bzw.
      implementiert sind findet sich unter
Mimetypen in Referenz-ERP
Anlagen
Listet die zugehörigen Anlagen zu
      einem Dokument in einer eigenen Auswahlliste auf.
Senden an
Ruft
      den Dialog „Archiv Mail Versand“ auf.
Im
      Kundenstamm gibt es diese Funktion ebenfalls als „Email
      senden“.
Archiv Mail
      Versand
Speichern unter
Speichert die selektierten Dokumente
      in einen vorgebbaren Ordner. Die Dokumente erhalten die Standard-Namen bei
      Archiv-Export – außer es ist ein Dateiname in den Stammdaten
      vorgegeben.
Bei
      erfolgreichem Export der Dokumente wird sich das Export-Verzeichnis
      sitzungsübergreifend gemerkt.
Signierung
PDF
Signieren eines
      PDF-Dokumentes.
Unterstützt PDF-Signierung durch
      Signotec-System.
Siehe
Signature Pad
      einrichten
Volltext-Menü
Bietet Schnellzugriffsmöglichkeiten
      auf Volltext-Funktionalitäten.
Archiv-Volltext
Das
      Feature „Volltext“ ist in Referenz-ERP Lizenz-geschützt, mit diesen Funktionen
      lassen sich aber die Funktion bis maximal 10 Einträge
      „ausprobieren“.
Siehe Suchbereich „Volltext“
[...]


---

## ARTIKEL [AR]

ARTIKEL   [AR]
Feld
Bemerkung
Sollbestand
Bis
      zu diesem Bestand wird entsprechend der Bestellgröße aufgefüllt. Ist
      dieser Bestand auf 0 gesetzt, so wird der Mindestbestand
      gezogen.
Mindestbestand
Findet keine Berücksichtigung
      hinsichtlich der Berechnung der Bestellmenge. Ist der verfügbare Bestand
      niedriger als der Mindestbestand so wird dieser Bestellvorschlag in ROT
      gekennzeichnet.
Meldebestand
Unterschreitet der verfügbare
      Bestand diesen Meldebestand so erscheint dieser Artikel in die
      Bestellvorschlagsliste. Dieser Bestellvorschlag wird in GELB
      gekennzeichnet.
Anmerkung
:
Die Bestellsperre im Artikel und im
Kunden/Lieferantenstamm werden berücksichtigt in der Auswahlliste !!

---

## Aufruf-Parameter

Aufruf-Parameter
Das Pascal-Script der Waagen-Schnittstelle kann mit 3
Aufruf-Parametern gestartet werden. Alle Parameter sind optional und haben
folgende Bedeutung:
Parameter 1:
Pfad und Dateiname der
Waagen-Datei. Wenn hier nichts angegeben ist, wird "WAAGE.DAT" als Default
angenommen.  Ist der Parameter belegt, so wird sogar die Einstellung des
Parameters MULTI_FILES=1 übersteuert.
Beispiel:
WAAGE.TXT
Parameter 2:
Lager - falls in den
ASCII-Daten kein Lager gelesen werden kann, oder Lager=0, dann wird das Lager
aus Parameter 2 verwendet. Ist auch dort kein Lager angegeben, so wird das Lager
herangezogen, das
im Parameter DEFAULT_LAGER steht.
Beispiel: 1
Parameter 3:
SCRIPTPID – Defaultmäßig
gilt SCRIPTPID="WaagenImport". Im 3. Parameter kann für den Fall, dass mehrere
verschiedene Importverfahren benötigt werden, eine andere Kennung für die
ScriptParameter angegeben werden, die sich dann im allgemeinen auf eine private
Gruppe von ScriptParametern beziehen.
Beispiel:
p_WaagenImport2
Anmerkung:
Ist ein Parameter mit 0 belegt, wird er als leer
interpretiert. Auf die Übergabe von Leerstrings in der Form „“ sollte unbedingt
verzichtet werden, wenn das Skript aus einer Anwendfunktion heraus aufgerufen
wird, da es hier zu unerwünschten Ergebnissen kommen kann.
Pascal-Scripte können im wesentlichen auf 2
verschiedenen Wegen gestartet werden
Start mit einer Anwendfunktion:
Der ControlString kann auch die 3 Parameter aufnehmen
und hat dann z. B. folgendes Aussehen:
Beispiel:
^jpl pascal p_WaagenImport 0 0
p_Waage2
Die Nullen werden vom Skript speziell so
interpretiert, daß die betreffenden Parameter 1 und 2 leer sind und lediglich
Parameter 3 einen Inhalt besitzt.
Start über Makro-Funktion (Direktsprung [MAKRO])
Der parametrisierte Aufruf kann dann in folgender
Weise erfolgen:
Der Start eines Scriptes erfolgt dann jeweils mit
F9.

---

## Ausführen von SQL-Texten

Ausführen von SQL-Texten
Wenn man auf einem Aktionsfeld lediglich ein unter
[SQLK]
gespeichertes Statement
ausführen will, so kann man dies mit folgendem Controlstring erreichen:
^dbx_select
( "SQLK", "#(sqlk_test,1)", "TMP" )
Die Funktion hat folgende Parameter
Parameter
Im Beispiel
Beschreibung
Cursorname
"SQLK"
Name
      des Cursors. Dieser ist relativ beliebig, darf jedoch nicht länger als 30
      Zeichen sein. Man findet diesen Namen z.B. im Tracefile
      wieder.
Statement
"#(sqlk_test,1)"
Dies
      ist eine spezielle Syntax um dem System zu sagen, dass das auszuführende
      Statement aus den SQL-Texten kommt.
Dabei ist das Zeichen
`#`
sozusagen das Kommandowort. Der erste Parameter ist der Name des
      SQL-Textes und der zweite der Besitzer. Für unter SQLK erfasste Texte muss
      hier immer eine
„1“
stehen
.
Option
"TMP"
Sorgt dafür, dass der Cursor
      automatisch wieder freigegeben wird.

---

## Ausgehende Nachrichten (Batch).

Ausgehende Nachrichten (Batch).
Der ROSI – EDI Nachrichtenaustausch dient dazu,
Nachrichten mit einem Geschäftspartner seiner Wahl auszutauschen. Nach
Erfolgreicher Einrichtung exportiert das System eine *.edi Nachricht in den
angegebenen Exportordner. Die Datei kann dann über z.B. eine X400 – Leitung
übertragen werden.
Es wird die beispielhafte Einrichtung und Anwendung
einer ausgehenden „INVOIC“-Nachricht gezeigt. Die Einrichtung erfolgt in
folgenden Abschnitten:
•
Grundeinrichtung
•
Erstellung des Rosi-Profils
•
Zuweisung zum Kunden

---

## Bediener für Lieferbelege

Bediener für Lieferbelege
Auf diesem Feld steht eine F3 Auswahl zum
Bedienerstamm zur Verfügung.

---

## Bedienelemente / Anzeigen

Bedienelemente / Anzeigen
Einen Überblick über den Zustand eines Beleges verschafft
man sich durch Eingabe der Vorgangsklasse und der Belegnummer. Durch den Button
‚Problemfälle laden’‚ kann eine Liste aller problematischen Belege geladen
werden (kann etwas dauern, da der gesamte Vorgangstamm untersucht wird). Durch
Anklicken einer Zeile aus dieser Liste lässt sich ein Beleg zur Bearbeitung
selektieren.
Die Belegübersicht zeigt Informationen aus dem Vorgangstamm
(vs.V_id, vs_Datum, Jahrnummer), den Zustand im Mandantenserver (= DS_STATUS
oder ----, falls kein Eintrag vorhanden ) und die wesentlichen Daten aus der
Vorgreservierung(V_Id, v_NumNummer, V_UnterNummer , V_ResNeuKennz).
Wählt man aus der Belegübersicht eine Zeile an, so werden
unter ‚Auswahl Aktion’ zu dem Typ passende Aktionen angeboten.
Es gibt folgende Typen:
•
Vorgangstamm und Vorgreservierung sind korrekt miteinander verbunden, der
Beleg ist zumindest technisch korrekt!
•
Es gibt nur den Vorgangstamm, eine Vorgreservierung mit passender V_Id
existiert nicht (= Vorgangsleiche ?!).
•
Es gibt nur einen Eintrag in Vorgreservierung.
Diese Klassifizierung spiegelt aber nicht alle möglichen
Konstellationen wieder. Insbesondere gibt es nach der Korrektur eines Beleges
den (gewollten) Zustand, dass ein Vorgangstamm keine Vorgreservierung hat. Erst
wenn der Mandantenserver den Originalbeleg vor der Korrektur per ‚technischen
Storno’ entfernt hat, ist alles wieder im Lot. Generell gilt aber: Wenn der
Mandantenserver alle Einträge bearbeitet hat und kein Benutzer in der
Vorgangsbearbeitung verweilt, dann müssen alle Vorgreservierungen und
Vorgangstämme 1 zu 1 (per V_Id) korrespondieren.
Folgende Aktionen können angeboten werden:

---

## Bedienung

Bedienung
Befehl
Resultat
F1
Öffnet das Hilfefenster
Strg-C (1..n ausgewählte
      Zeilen)
Kopiert den SQL-Text
aller
ausgewählten Zeilen ins Clipboard
Linksklick in ein SQL-Text
      Feld
Öffnet den
      SQL-Text im Text Editor des Systems
Zum Einlesen kann die Trace-Datei per Drag and Drop,
oder per Klick auf den Button „Load Trace“ geladen werden.
Die Datei wird daraufhin ausgelesen und auf einer
Tabelle abgebildet.
Die Tabelle kann über die Checkboxen gefiltert werden.
Außerdem kann man das SQL-Feld über die Textsuche filtern (case
insensitive).

---

## Bedingungen

Bedingungen
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register Bedingung
Direktsprung
[ANWR]
.
Dies ist eine veraltete Technik die Daten des Reports
einzugrenzen. Neue Reporte werden über Views, die nur die anzuzeigende
Datenmenge darstellen, mit Daten versorgt.

---

## Überblick Editfact Anwendung

Überblick Editfact Anwendung
In diesem Abschnitt werden alle Programmbereiche aus
Sicht der Entwicklungsabteilung erläutert und beschrieben.

---

## Beschreibung der Relationen

Beschreibung der Relationen
Relation ScriptParam
ScriptParam ist die Kopfrelation, die eine ganze
Gruppe von Parameter unter einer Id zusammenhält. In der Relation ScriptParamPar
sind die Details, also die einzelnen Parameter selbst abgelegt.
ScriptPBedKorr
Bedienerkennzeichen, wird auf die UserId des letzten
Bearbeiters gesetzt.
ScriptPBesitzer
0: allgemeine öffentliche Parametergruppe, 1: private
Parametergruppe
Private Parametergruppen dürfen bei einem
Datenbank-Update nicht verändert werden.
Das Recht, private Parameter anzulegen und zu
bearbeiten wird über die
optionalen Parameter
(Direktsprung [OPT]
eingestellt. Hierzu muss für den betreffenden Bediener ein Satz mit dem Namen
SKRIPTPARAMETER_PRIVAT
angelegt sein. Ein Wert ist nicht
erforderlich.
Öffentliche Parameter dürfen kundenseitig nur unter
Entwicklerhoheit angelegt oder verändert werden.
Wichtig:
Öffentliche Parametersätze
werden bei einem Update
nicht
gelöscht! Dies geschieht lediglich mit
Systemparametern.
ScriptPBezeich
Eine allgemeinverständliche Klartextbezeichnung für
die Parametergruppe .
ScriptPId
Die Id, die einen Satz von Skriptparameter
zusammenhält (Primary Key) Mit dieser
ScriptPId
wird in einem Pascal-Skript
gekennzeichnet, welche Gruppe von Parametern gewählt werden soll.
ScriptSystem
System-Flag. 0: nicht gesetzt, 1: gesetzt: Die
Bearbeitungshoheit für derartige Parametersätze liegt allein im Hause Branchen-ERP. Bei
einem Update werden alle Datensätze mit ScriptSystem =1 gelöscht und neu
angelegt.
Relation ScriptParamPar
ScriptParamPar ist die Detailrelation, die durch das
Attribut
ScriptPId
per FOREIGN
KEY an die Relation ScriptParam gebunden ist.
Jeder Datensatz ist durch eine
ScriptPPId
gekennzeichnet, die
zusammen mit der
ScriptPId
eindeutig ist.
Ein Datensatz kann unter einer Id bis zu 3
verschiedene Werte enthalten.
ScriptPId
Bindeglied zwischen Kopfsatz und Detailsätzen.
ScriptPPAktiv
0: Der Parameter ist nicht aktiv, 1: Der Parameter ist
aktiv. Nicht zu verwechseln
[...]


---

## Besonderheiten bei der Verwendung als Tankstellen-Schnittstelle

Besonderheiten bei der Verwendung als
Tankstellen-Schnittstelle

---

## Bestandsbuchführung und Bestandsbewertung

Bestandsbuchführung und Bestandsbewertung
Referenz-ERP bedient je nach Verwendungszweck
unterschiedliche Methoden zur Bestandsführung. Die Basiskonzepte werden im
Folgenden beschrieben.

---

## Block Leerzeilen

Block Leerzeilen
Hier kann hinterlegt werden, ob bei der Ausgabe von
Textblöcken (dazu gehören Adressen, Bemerkungen, Zahlungsbedingungen) pro
Ausgabezeile je eine zusätzliche Leerzeile erzeugt werden soll.
Diese Einstellung kann für folgende Konstellation
hilfreich sein:
Bei einem Windows-Druckformular wird der Zeilenabstand
durch Anpassung der Zeilenskalierung in der Fonttabelle sehr klein eingestellt.
Alle gewöhnlichen Text- und Datenausgaben werden in
einem Font erstellt, der doppelt so hoch ist wie das zugrunde liegende
Zeilenraster.
Die Druckpositionen werden in jeder zweiten Zeile
positioniert.
Nur ein geringer Teil der Angaben (wie z.B.
Bankverbindung, juristische Firmenbezeichnung etc.) werden in kleiner Schriftart
erstellt.
Durch diesen Trick können also unterschiedliche
Zeilenabstände simuliert werden.
Ein Problem tritt jedoch bei blockorientierten
Ausgaben (z.B. Adresse) auf, da diese auf fortlaufenden Zeilen gedruckt werden.
Mit Hilfe der im Formulareinrichter eingetragenen Block-Leerzeilen kann nun hier
der richtige Zeilenabstand wiederhergestellt werden.
Druckaufbereitung von Adressen
Um den Druck von Adressen anzupassen, wurden für die
Vorgangsbearbeitung zwei neue Steuerparameter erstellt:
Parameter 586: „Leerzeilen bei Adressen entfernen“
Bei der Einstellung „Ja“ werden alle Leerzeilen aus
Adressen entfernt (z.B. leere Zusätze oder Namensteile)
Parameter 587: „Adressen von unten aufbauen“
Bei der Einstellung „Ja“ wird die Adresse ausgehend
von der untersten Zeile des Ausgabeblockes aufgefüllt. Die Adresse ist also
immer an den unteren Rand ausgerichtet. Ist der Ausgabeblock auf dem Formular
kleiner als die Anzahl der Adresszeilen, so werden bei dieser Einstellung die
obersten Zeilen unterdrückt.

---

## Business Intelligence

Business Intelligence
Als Erweiterung der bisherigen Schnittstelle aller
Auswahllisten und Grid Darstellungen zum Excel System (STRG + E) kann jetzt ein
Business Intelligence Interface im Referenz-ERP genutzt werden, um komplexe
Auswertungen auf Basis von Referenz-ERP-Daten zu erstellen. Die Grundlage bildet
wiederum unser vorhandenes Auswahllistenelement das einem Excel System direkt
zur Verfügung gestellt werden kann. Die Excel Arbeitsmappe kann hierbei dann
bequem per Datenverbindung auf diese Informationen zugreifen.
Ein Mehrmandanten Zugriff oder ein Mehrtabllen (BI)
Zugriff ist dabei auch Problemlos möglich.
Durch Anwahl der technischen Ebene im
Auswahllistensystem („ENTW Konfiguration“) kann hierbei pro Variante (Standard
wie auch privat) ein Interface erstellt werden. Die Erstellung wird abgewickelt
in einem
Zusatzbildschirm
, in dem auch für
mehrere Varianten ein Interface gleichzeitig vorbereitet werden kann. Wird mit
der Auslieferung schon ein Interface bereitgestellt, so ist diese Funktion nur
zur Erneuerung der Basisstrukturen (neue Felder, andere Auswahlkriterien)
einzusetzen.
Während der Erstellung eines Interfaces zu dieser
Anwendung wird eine View im System angelegt, die die Daten passend und auf Basis
eines dynamischen Auswahlbereiches und/oder Profils bereitstellt. Weiterhin
werden zwei neue Menüpunkte im System eingerichtet, die den Zugriff auf die
Excel Struktur erlauben, einerseits im Hauptmenü unter dem Abschnitt
„Informationen“ und in der zugehörigen Anwendung innerhalb der Optionbox. Diese
neue Funktion trägt die Variantenbezeichnung gefolgt von den zwei Buchstaben
(BI) als Label.
Zusätzlich wird ein Excel Template vorbereitet,
welches die Grundlage der späteren Anwendung darstellt.
Nach Erzeugung des Interfaces (bei ggf. auftretenden
Inkompatibilitätsproblemen
, sind diese
wie
unten
beschrieben zu beheben) kann nach Neustart der Referenz-ERP Anwendung sofort mit dem
Excel Blatt
gearbeitet werden. Durch Anwahl der Funktion wird zunächst
[...]


---

## Compliance-Statistik

Compliance-Statistik
Hauptmenü
Informationen
Sonstiges
Compliance Statistik
Diese Auswahlliste dient lediglich zur Übersicht und
hat keine Suchfunktion oder Funktionen. Hier werden die Statistiken im Bezug auf
Compliance angezeigt.
Felder
Felder
Beschreibung
Typ
-
Anfragen:
Anfragen, die vom Webservice
      beantwortet wurden
-
Vorgangs-Detail-Anzeige:
Prüfungen, die von der
      Vorgangsdetails-Anzeige aus gestartet wurden
-
Zyklische
      Anfrage:
Prüfungen, die von der Funktion
      „definierte Anschriften prüfen“ ausgelöst wurden
-
Goodguy-Definition:
Anzahl der
      Good-Guy-Definitionen
-
Auswahlliste:
Prüfungen, die von der
      Auswahlliste (
[KU]
,
[ANSCH]
,
[VORG]
) ausgelöst wurden
-
Änderung:
Prüfungen, die nach der Änderung
      einer Anschrift ausgelöst wurden
-
Neuerfassung:
Prüfungen, die von der
      Neuerfassung einer Anschrift ausgelöst wurden
-
Vorgangserfassung:
Prüfungen, die von der Erfassung
      eines Vorgangs ausgelöst wurden
-
Unbekannt:
Tests
-
Vorhandene:
Prüfungen, die nicht an den
      Webservice weitergeleitet wurden, weil das Ergebnis innerhalb des im
      SPA824 definierten Zeitraums bereits ermittelt wurde
Anzahl
Gibt
      die Anzahl des jeweiligen Typen wieder

---

## CREATE STRUCT Statement

CREATE STRUCT
Statement
Syntax
CREATE STRUCT table-name [INTO Dateiname]
Purpose
Erstellt für eine Tabelle die Beschreibung
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
ALTER
STRUCT
Beschreibung
Um die Beschreibung ( das create table Statement) für
eine Tabelle zu erhalten, steht dieses Statement zur Verfügung. Es erstellt eine
Datei ( Achtung immer „Overwrite“ ) in der das Create-Statement zuzüglich der
Indexe enthalten ist. Wird „INTO Dateiname“ nicht angegeben, wird der table-name
mit der Endung „.SQL“ als Dateiname verwendet.
Beispiel
CREATE STRUCT FIBUVORGKLASSE INTO
c:\FIBUKL.SQL;

---

## Darstellung der Auswahlliste

Darstellung der Auswahlliste
Die Darstellung von Auswahllisten lässt sich über
private Ableitungen oder über den Gestaltungsdialog festlegen. Der
Gestaltungsdialog steht für alle Anwender zur Verfügung, die im Bedienerstamm
das Kennzeichen „Auswahllistenadministrator“ auf „Ja“ oder „Temporär“ gesetzt
haben. Temporär bedeutet, dass die im Gestaltungsdialog vorgenommenen
Einstellungen nicht gespeichert werden und nur für die aktuelle Referenz-ERP-Sitzung
gelten.
Der Gestaltungsdialog ist den privaten Ableitungen
vorzuziehen.

---

## Cursor in die Bildschirmschnittstelle übernehmen

Cursor in die Bildschirmschnittstelle übernehmen
Der mit dem DBX_SELECT Befehl angesprochenen
Datenbankcursor wird aus der Cursorstruktur in die Maskenstruktur übertragen.
Anfruf
call dbx_get_buf ( cursor, Bildschirm_Handle,
von_BS_Position, bis_BS_Position )
Parameter
t:2 Cursor Name des zu nutzenden Datenbankcursors,
hier ist ein eindutiger Text anzugeben. BildschirmHandle alle Bildschirmfelder
mit diesem Alias (a.) Namen werden über diesen Befehl angesprochen vonpos Ab
welcher Bildschirmposition ( 0=alle ). bispos Bis zu welcher Bildschirmposition
( 0=alle ).
Returnwert
keiner, Fehler werden auch nich Reportet
Umfeld
Diese Routine ist im JPL und im COM Interface nutzbar.
Beispiel
call dbx_select ( "x", "select
db_kundid", "TMP" )
if ( DBERR != 0 )
{
call dbx_get_buf ( "x",
"h", 0, 0 )
}
call dbx_freecursor ( "x" )

---

## Das Hauptauswahlmenü

Das Hauptauswahlmenü
Das Hauptauswahlmenü gliedert sich in folgende
Bereiche:
Mandant-Kurztext
Favoritenbereich
Menüpunktbereich
Systemmeldebereich
Menü-Hauptpunkte-Bereich
Arbeitsbereich
Arbeitsbereich
Arbeitsbereich
Menülogobereich
Arbeitsbereich
Arbeitsbereich
Arbeitsbereich
Die Bedienung ist kontext-orientiert, bestimmte
Funktionalitäten hängen also von dem Bereich ab in dem sich der Mauszeiger
befindet. Das äußert sich z.B. an einem dynamischen Kontextmenü, das sich je
nach Positionierung der Maus den jeweiligen Gegebenheiten anpassen kann.

---

## Dateien laden

Dateien laden
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Daten laden
Direktsprung
[ECL]
Der Dateiname wird über eine Dialogmaske abgefragt.
Den Dateiformaten werden feste Dateierweiterung zugeordnet, erkannt "*.STA" für
MT940, "*.DTI" für das DTA-Format, "*.C53", "*.ZIP" oder ungepackt als "*.XML"
für das SEPA CAMT.053-Format und "*.CSV" für PayPal. Das angegebene Verzeichnis
und die ausgewählte Dateierweiterung werden vom Programm gespeichert, so dass
beim nächsten Aufruf sofort auf dieses Verzeichnis zugegriffen wird. Die SEPA
CAMT Dateien mit der Extension ZIP bzw. C53 werden in einem so genannten
ZIP-SEPA Container zusammengefasst. Vor dem Einlesen wird dieser Container
automatisch in ein Temporäres-Verzeichnis entpackt und von dort werden dann die
Dateien eingespielt.
Während des Ladens werden diverse Prüfungen auf
Richtigkeit der Datei durchgeführt.
DTA-Format: Dateierweiterung
"*.DTI"
•
Stimmt die Struktur mit dem geforderten Datenträgerformat
überein?
•
Stimmt die Anzahl der Datensätze mit denen im Datenträgernachsatz
überein?
•
Stimmt die Summe der DM-Beträge der Datensätze mit denen im
Datenträgernachsatz überein?
•
Stimmt die Summe der Kontonummern der Datensätze mit denen im
Datenträgernachsatz überein?
•
Stimmt die Summe der Bankleitzahlen der Datensätze mit denen im
Datenträgernachsatz überein?
•
Stimmt die Summe der Euro-Beträge der Datensätze mit denen im
Datenträgernachsatz überein?
Für MT940(Swift)-Format: Dateierweiterung "*.STA"
•
Stimmen alle Feldnummern überein?
•
Stimmt der Anfangssaldo plus aller Bewegungen mit dem Endsaldo
überein?
•
Ist die Währung Euro (früher auch DM)?
Für das SEPA CAMT.053-Format: Dateierweiterung
"*.C53", "*.ZIP" oder ungepackt als XML. Die Auswahl der Dateierweiterung
erfolgt im Dateiauswahldialog.
•
Stimmen alle Feldnamen überein?
•
Ist die Währung Euro?
Für PayPal (CSV-Format): Dateierweiterung "*.CSV"
•
Stimmt der Anfangssaldo plus aller Bewegungen mit dem Endsaldo überei
[...]


---

## Berechtigungen

Berechtigungen
Felder
Betrieb
Filialnummer der ausgewählten
      Betriebsstätte. Dahinter dessen Bezeichnung.
Empfänger Betriebsstätte
Filialnummer der Betriebsstätte des
      Empfängers
Von
      Daten aus der Publikation
Name
      der Publikation deren Daten an den Empfänger übertragen werden
      sollen.
Teilmenge
Der
      hier angegebene stellt den Vergleichswert dar. Dieser wird mit dem Inhalt
      der in der
„subscribe by“
-Klausel angegebenen Tabellenfeld, eines
      Artikels dieser Publikation verglichen. Nur Zeilen bzw. Datensätze, die
      diesen Vergleich erfüllen werden für die Replikation an den Datenempfänger
      berücksichtigt.
Beispiel:
Feld
      Teilmenge
: 2
„subscribe
      by“-Klausel
:
      subscribe by filialnummer
Ergebnis
: es werden alle Datensätze dieses
      Artikels repliziert die im Tabellenfeld Filialnummer den Wert 2 stehen
      haben!
Funktionen
Speichern
Speichert die Angaben
Zeile einfügen
Fügt
      eine Zeile ein
Zeile entfernen
Entfernt die gewählte
      Zeile

---

## Dokumentation für die POS-KASSE

Dokumentation für die POS-KASSE
Bitte beachten Sie:
Die POS-Kasse wird von Branchen-ERP nicht mehr unterstützt.
Die nachfolgenden Texte sind lediglich als historisch zu verstehen.
Die POS-Kasse ist ein Modul, das einen zügigeren
Ablauf bei der Erfassung von Barverkäufen bietet. Dieses wird durch einen Druck
ermöglicht, der parallel zur Erfassung abläuft und außerdem den Erfassungsmodus
für Artikelerfassung und Bezahlung ebenso auf einer Maske stattfinden lässt wie
das Anlegen und Abschließen des einzelnen Vorgangs.
Diese Art der Erfassung bezieht sich ausschließlich
auf Barverkäufe, d.h. die Routinen für Bareinkäufe, Bargutschriften,
Einzahlungen, Abschöpfungen, Zahlungsmeldungen,... bzw.
Kasseneröffnungen/Abschlüsse bleiben erhalten. Es wird außerdem auf denselben
Tabellen gearbeitet, so dass auch die Übersichten nutzbar sind.
Allerdings stehen weniger Funktionalitäten/Module in
diesem POS-Erfassungsvorgang zur Verfügung.
Das Modul selbst befindet sich im Hauptauswahlmenü:
Warenwirtschaftssystem/Barvorgänge/POS-Kasse.

---

## Druckbereiche

Druckbereiche
Druckbereich 820 / Kassenkopf
Variablenname
Druckposition
Bedeutung
Kasse
4
      ZahlVariable
6200
Kassennummer
Kassierer
3
      TextVariable
6207
Userkürzel
Kassierername
3
      TextVariable
6208
Name
      des Bedieners lt. Bedienerstamm
BelegArt
3
      TextVariable
6205
Belegarttext
BelegDatum
5
      DatumVariable
6203
Das
      Belegdatum
BelegNr
4
      ZahlVariable
6204
Die
      Belegnummer
BelegId
4
      ZahlVariable
6202
Beleg ID
Sitzung
4
      ZahlVariable
6206
Kassensitzungsnummer
Filialnummer
4
      ZahlVariable
6201
Filialnummer
FilialBezeich
3
      TextVariable
6209
Die
      Bezeichnung der Filiale
FilialStrasse
3
      TextVariable
6210
Die
      Straße der Filiale
FilialPLZ
3
      TextVariable
6212
Die
      Postleitzahl der Filiale
FilialOrt
3
      TextVariable
6211
Der
      Ort der Filiale
MandantBezeich
3
      TextVariable
6221
Die
      Bezeichnung des Mandanten
MandantStrasse
3
      TextVariable
6222
Die
      Straße des Mandanten
MandantPLZ
3
      TextVariable
6223
Die
      Postleitzahl des Mandanten
MandantOrt
3
      TextVariable
6224
Der
      Ort des Mandanten
Kopie
3
      TextVariable
6226
Bei
      Wiederholungsdruck wird der Beleg als Kopie markiert
Storno
3
      TextVariable
6225
Bei
      Stornierung wird der Beleg als Storno markiert
BelegName
3
      TextVariable
6217
Der
      Name des Kunden bzw. Kontobezeichnung je nach Belegart
BelegText
3
      TextVariable
6213
Bemerkungstext
BelegBetrag
4
      ZahlVariable
6215
Die
      Belegsumme in Buchwährung
BelegKWBetrag
Die
      Belegsumme in Kassenwährung (derzeit nicht unterstützt)
BelegWaehrung
3
      TextVariable
6214
Das
      Währungskürzel der Buchwährung
BelegKW
Das
      Währungskürzel der Kassenwährung (derzeit nicht unterstützt)
Konto
4
      ZahlVariable
6218
Kontonummer Kunde/Konto je nach
      Belegart
Ort
3
      TextVariable
6219
Wohnort des Kunden lt.
      Anschriftstamm, falls kundenbezo
[...]


---

## DTA und e-Clearing

DTA und e-Clearing
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Direktsprung
[ECL]
Bei selbst eingereichten Zahlungsaufträgen über DTA
kommt es im Zusammenspiel mit e-Clearing zu einer Besonderheit, wenn man dort
die Zahlungsbelege in die Primanota übernimmt.

---

## EDI Nachrichtenaustausch mit Eddyson

EDI Nachrichtenaustausch mit Eddyson
Zunächst muss ein Profil eingerichtet werden, welches
die Rohdaten eines Vorgangs in eine einheitliche Struktur bring. Dazu steht die
Tabelle STDDAT zur Verfügung. Profile sind vorbereitet für die Kunden Rewe,
Edeka, Grohage, Markant, Netto und können bei Branchen-ERP angefordert werden. Nach
einrichtung des Profils wird der Provider Eddyson die Schnittstelle zum
Rechenzentrum vorbereiten und die Profilabbildung ausbauen.

---

## EDI Nachrichtentransfer

EDI Nachrichtentransfer

---

## EDIT Statement

EDIT Statement
Syntax
EDIT [Dateiname];
Purpose
Öffnet mit notepad die angegebene Datei
Anwendung
Befehlszeile
Berechtigung
Alle Anwender
Beschreibung
Unter Osql werden desöfteren Daten oder Strukturen in
Dateien geschrieben. Das EDIT Statement bietet eine einfache und praktikable
Möglichkeit diese Daten direkt zu prüfen bzw. zu bearbeiten.
Beispiel
Create Struct Kontosummen into
c:\Kontosummen.sql;
EDIT c:\kontosummen.sql;

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

## Einfuhrumsatzsteuer

Einfuhrumsatzsteuer
Entrichtete Einfuhrumsatzsteuer (§15 Abs. 1 Nr. 2
UStG), die z.B. durch den Lieferanten oder Spediteur uns in Rechnung gestellt
wird, wird in Referenz-ERP durch das direkte Bebuchen von Steuerkonten realisiert
(siehe Steuerkonten bebuchen).
Einrichtung
Um die Einfuhrumsatzsteuer auf dem USTVA-Formular
ausweisen zu können, sind im Steuersatzpfleger alle relevanten
Kombinationen dieser Steuergruppe einzutragen. Dabei sind folgende
Besonderheiten zu beachten.
•
Steuerformel
Steuer 100% (Steuerkonten bebuchen
  s.o.)
•
Steuersatz
Wird automatisch auf 100% gesetzt.
•
Steuerkonto
Steuerkonto, auf das der gesamte Betrag bei
      Erfassung gehen soll.
•
AW-Kennz. Umsatz
0, da nicht auszuweisen auf der USTVA
      Steuerkonto, auf das der gesamte Betrag bei Erfassung gehen
soll.
•
Steuer
In der Beispielliste oben wäre es Zeile 570 und
      somit Kennziffer 62. In der USTVA 2007 findet man die Einfuhrumsatzsteuer
      in Zeile 57.

---

## Eingehende Nachrichten (Batch).

Eingehende Nachrichten (Batch).
Der ROSI – EDI Nachrichtenaustausch dient dazu,
EDI-Nachrichten mit einem Geschäftspartner seiner Wahl auszutauschen. Nach
Erfolgreicher Einrichtung importiert das System eine *.edi Nachricht aus den
angegebenen Importordner. Die Datei kann dann über z.B. eine X400 – Leitung
übertragen werden.
Es wird die beispielhafte Einrichtung und Anwendung
einer eingehenden „ORDERS“-Nachricht gezeigt. Die Einrichtung erfolgt in
folgenden Abschnitten:
•
Grundeinrichtung
•
Erstellung des Rosi-Profils
•
Zuweisung zum Kunden

---

## Einrichten / Bearbeiten eines Events

Einrichten / Bearbeiten eines Events
Folgende Tasten stehen zur Verarbeitung zur
Verfügung.
Buttons
Anzeige=F6
Mit
      dieser Funktion zeigen Sie in einem Editor den SQL-Befehl an, der zum
      Anlegen des Events generiert wird.
OK=F9
Mit
      dieser Funktion speichern Sie den Event
Abbruch=ESC
Mit
      dieser Funktion brechen Sie die Neuerstellung bzw. die Bearbeitung ab.
Die Einrichtungsmaske enthält folgende
Registerkarten:
Allgemein
Sonstiges
Bedingungen
Verarbeitungsroutine
Vorlagen
Registerkarte
Allgemein
Felder
Name
Geben Sie ganz oben den Namen Ihres
      Events ein. Bei der Bearbeitung eines Events steht hier der Eventname.
Typ
Legen Sie hier den Typ des Events
      fest.
Ersteller
Hier
      wird vom System automatisch der Username des Erstellers eingetragen und
      angezeigt.
Kommentar
Schreiben Sie hier eine kurze
      Information, zu welchem Zweck das Event dient. So können Sie Informationen
      hinterlegen, die später sonst in Vergessenheit geraten.
Registerkarte
Sonstiges
Felder und
    Auswahlboxen
Ereignis aktiviert
Mit
      diesem Haken setzen Sie, ob das Ereignis nur eingetragen oder sogar zum
      vereinbarten Zeitpunkt ausgeführt werden soll. Deaktivierte Ereignisse
      werden nicht ausgeführt.
Prozedur gestoppt
Wenn
      ein Event einen unerwartet langen Lauf hat, so dass gleich nach Beendigung
      das nächste Event startet, dann kann dies zu großer Last auf der Datenbank
      führen. Unglücklicherweise lassen sich laufende Events nicht deaktivieren.
Deshalb gibt es eine
      Sollbruch-Stelle. In Eventprozeduren wird zu Beginn eine Abfrage
      eingebaut, die bestätigt, ob die Prozedur überhaupt ausgeführt werden
      soll. So kann sichergestellt werden, daß der nächste Lauf des Events nur
      kurz ist und eine Abbruchmöglichkeit vorliegt.
Mit
      dem Aktivieren dieser Funktion bestätigen Sie, dass die Prozedur ihren
      Auftrag nicht ausführen soll.
Diese Funktion steht nur
      Event-P
[...]


---

## Einrichtung

Einrichtung
SPA 952 einrichten
SPA 953 einrichten
SPA 801 Scannerprozedur eintragen
Für jeden einzelnen Scanner muss die private Prozedur,
wie
SPA 734 einrichten
dbconfig.xml
In der Datei „dbconfig-xml“ im Aeins\Bin- Verzeichnis
wird die Verknüpfung zur Datenbank geregelt. Dazu ist folgende Zeile mit den
ensprechenden Daten einzutragen:
<DBConn
Engine="Aeins_Engine" Dbn="testdb" User="TEST" Password="S1234"
Commlinks="tcpip{HOST=192.168.202.2}" Extras="idle=60;lto=30;pooling=false;"
Path="" Remote="" Standard="1" IPAdresse="192.168.202.4"
     ProfilIPAdresse="192.168.202.4">ZSCANNER1</DBConn>
Bedienereinrichtung
Für jeden Scanner ist ein Bediener einzurichten
Für jeden Bediener eines Scanners muss im
Bedienerstamm die Persönliche Kennung (Es sind nur Ziffern erlaubt) eingerichtet
werden.
Man meldet sich nun im Aeins mit seinem Kürzel
und  als Passwort  <„s“+die eingegebenene Nummer> an.

---

## Einrichtung der Schnittstelle

Einrichtung der Schnittstelle
Die wesentlichen Einrichtungsdaten werden unter dem
Direktsprung RFSV ( RFS Voreinstellungen) festgelegt:

---

## Einrichtung der POS-Kasse

Einrichtung der POS-Kasse
Bitte beachten Sie:
Die POS-Kasse wird von Branchen-ERP nicht mehr unterstützt.
Die nachfolgenden Texte sind lediglich als historisch zu verstehen.

---

## Einrichtung des Publishers und der Remote-User mit Sybase Central

Einrichtung des Publishers und der Remote-User mit Sybase Central
Die Einrichtung des Publishers und der Remote-User
lässt sich auch in Sybase Central unkompliziert erledigen.
1.
Starten Sie Sybase Central
2.
Verbinden Sie sich mit der gewünschten Datenbank
3.
Klicken Sie in der Ordneransicht mit der RECHTEN Maustaste auf Benutzer
à
Neu
4.
Im Assistenten zum Erstellen von Benutzern geben Sie zunächst den Namen des
anzulegenden Benutzers ein. Der erste Name ist BST1. Bei weiteren anzulegenden
Benutzern wird die Zahl jeweils um Eins erhöht (BST2). Klicken Sie anschließend
auf „Weiter“
5.
Vergeben Sie das Passwort für den Benutzer
6.
Lassen Sie die Login-Richtlinie auf „root“ und klicken Sie anschließend auf
„Weiter“
7.
Vergeben Sie die benötigten Rechte des Benutzers und klicken Sie anschließend
auf „Weiter“. Mindestens:
a.
DBA
b.
Ressource
c.
Entfernter DBA
d.
Alle anderen schaden jedenfalls nicht…
8.
Geben Sie einen Kommentar ein (optional) und klicken Sie anschließend auf
„Fertig stellen“
9.
Suchen Sie nun den Benutzer den Sie gerade angelegt haben in der Ordneransicht
aus der Liste der Benutzer heraus und klicken Sie diesen mit der RECHTEN
Maustaste an und klicken anschließend auf Neu
à
Mitgliedschaft
10.
Markieren Sie die Gruppe ADMIN und bestätigen Sie mit OK
11.
Klicken Sie den Benutzer erneut mit der RECHTEN Maustaste an und wählen Sie
anschließend „Auf Publikationseigentümer ändern“ oder für SQL Remote Benutzer
„auf entfernten Benutzer ändern…“  aus
12.
Klicken Sie in der Ordneransicht nun auf SQL Remote Benutzer und wechseln Sie
anschließend auf die Registerkarte „Nachrichtentypen“
13.
Klicken Sie dort mit der RECHTEN Maustaste auf den Eintrag „File“ und wählen
dort Eigenschaften
14.  Geben
Sie hier die Adresse des Publikationseigentümers ein
15.
Bestätigen Sie die Änderung mit OK
Zum Anlegen der SQL Remote Benutzer können Sie auch
direkt durch Anklicken des Menüpunktes SQL Remote Benutzer in de
[...]


---

## Einrichtung des Reports

Einrichtung des Reports
Im Editor des Crystal-Reports muss die Seite wie folgt
eingerichtet sein:
Unter dem Menüpunkt „Datei“ existiert der Punkt „Seite
einrichten…“. Im nun geöffneten Dialog müssen die Häkchen wie im Bild gesetzt
werden.

---

## Einrichtung mehrerer verschieden parametrisierter Waagen-Schnittstellen auf einer Kundendatenbank

Einrichtung mehrerer verschieden parametrisierter Waagen-Schnittstellen auf
einer Kundendatenbank
Dies ist grundsätzlich möglich. Hierfür ist generell
folgende Vorgehensweise erforderlich:
Für jede Schnittstelle wird in der Relation
ScriptParam ein Datensatz  mit einer bestimmten ScriptPId angelegt. Die
ScriptPId muss mit ‚p_‘ beginnen und der ScriptPBesitzer auf 1 gesetzt werden,
damit bei einem Update nichts zufällig versehentlich gelöscht wird.
Für jede Schnittstelle werden die Datensätze aus der
Relation ScriptParamPar dupliziert und mit einer neuen ScriptPId gemäß 1.
versehen. (Entladen der Relation und manuelle Umschlüsselung des Attributes
ScriptPId durch Suchen und Ersetzen).
Für den Aufruf des Pascal-Scriptes ist für jede
Schnittstelle eine private Funktion zu schaffen, die als 3. Aufrufparameter die
betreffende ScriptPId enthält.

---

## EPAS

EPAS
Unter dem Punkt können auf Masken für einzelne
Bedienerklassen Felder versteckt, angezeigt oder gegen Eingabe geschützt
werden.
Feldname
Bedeutung
Maskenname
In
      diesem Feld wird der Name angezeigt
Bedienerklasse
Für
      welche Bedienerklasse soll die Einstellungen gelten.
Feldname
Name
      des Feldes
Standard
Standard des
      Auslieferungszustandes
Nicht abfragen
Das
      Feld wird für die Eingabe gesperrt.
Nicht zeigen
Feld
      wird für die gewählte Bedienerklasse ausgeblendet.
Nicht verbergen
Feld
      wird für die gewählte Bedienerklasse eingeblendet

---

## EPAs zurücksetzen auf Grundeinstellung (default)

EPAs zurücksetzen auf Grundeinstellung (default)
Es werden die Daten in folgenden Tabellen
gelöscht:
BEDIENERPROFIL

---

## eRechnung – im Archiv

eRechnung – im Archiv
Im Archiv gibt es für eRechnung eine eigene Variante.
In das Archiv kann
manuell importiert
werden oder mit
[EMAIL]
oder
[FAI]
.
In dieser Variante werden folgende Datentypen
angezeigt:
Belegklassen XML
Belegklasse 8040
Dies
      ist das exportierte Xml.
Belegklasse 8041
Das
      ist die HTML-Visualisierung des exportierten Xml
Belegklasse 8042
Der
      eRechnungsexport ist fehlerhaft.
Belegklasse 8049
Das
      ist der eRechnungsexport mit ZUGFerD (
ab Herbstversion
      2025
)
Belegklassen Import
Belegklasse 8044
Dies
      ist ein ZUGFerD-Pdf mit eingebetteter Xml-Datei. (
ab Herbstversion
      2025
)
Belegklasse 8045
Dies
      ist das importierte Xml.
Belegklasse 8046
Das
      ist die HTML-Visualisierung des Xml

---

## eRechnung - Import

eRechnung - Import
Der Import von eRechnung kann auf drei Weisen
geschehen:
1.
Als
Dateiimport ins
Formulararchiv mittels
[FAI]
.
Dazu muss die Option
eRechnung
import
mit
Ja
aktiviert
sein.
2.
Als Dateiimport im Rahmen des
eMailConnectors
[email]
.
Dazu muss die Option
eRechnung
import
mit
Ja
aktiviert
sein.
3.
Im Formulararchiv selbst kann die Funktion „
Hinzufügen
“ für einen manuell
importierten Beleg aufgerufen werden.

---

## eRechnung Importeinstellungen einrichten

eRechnung Importeinstellungen einrichten
In der Anwendung eRechnung
[XRE],
Variante
Import-Vorgänge
hat die Funktion
Importeinstellungen bearbeiten.
Hier richten Sie die Importeinstellungen der eRechnung
ein.
Felder
Fehlerbehandlung HTML
Gibt
      an, ob eine nicht erfolgreiche Erstellung einer HTML-Visualisierung als
      Fehler gelten soll (Default
Ja
)
Fehlerbehandlung Kunde
Gibt
      an, ob eine nicht erfolgreiche Findung eines Kunden/Lieferanten als Fehler
      gelten soll (Default
Nein
)
Fehlerbehandlung
      Validierung
Gibt
      an, ob eine nicht erfolgreiche Validierung eines Imports als Fehler gelten
      soll (Default
Ja
)
Fehlerfunktion
Gibt
      eine Datenbankfunktion an, die die Fehlermeldungen eines Imports aufnehmen
      und z. B. per E-Mail weiterleiten soll.
Als
      Eingabeparameter wird die ImportId gegeben.
Als
      Vorlage kann hier die ausgelieferte Funktion
      „AMIC_DEMO_XRE_ImportFehlerFunc“ dienen.
Kundenfindungsfunktion
Gibt
      eine Datenbankfunktion an, die aus den importierten Daten einen
      Kunden/Lieferanten ermitteln soll.
Als
      Eingabeparameter wird die ImportId gegeben, als Ausgabe wird die KundId
      des Kunden/Lieferanten erwartet.
Als
      Vorlage kann hier die ausgelieferte Funktion
      „AMIC_STD_XRE_ImportKundensuche“ dienen.
Belegflusspostfach
      Warenwirtschaft
Standardbelegflusspostfach für
      eRechnungsimporte im Bereich Warenwirtschaft
Belegflusspostfach
      Finanzbuchhaltung
Standardbelegflusspostfach für
      eRechnungsimporte im Bereich Finanzbuchhaltung

---

## eRechnung – Profilpfleger

eRe
chnung – Profilpfleger
Direktsprung
[XRE]
Der Profilpfleger ist in
der Anwendung
eRechnung
zu finden,
und zwar in der Variante
Export
Profil
.
Hier können die verschiedenen Profile für den Export gepflegt
werden, welche zur Erstellung von eRechnungen genutzt werden sollen. Dabei kann
man selbst angepasste Prozeduren angeben und diese verschiedenen Kunden
zuordnen.

---

## Erstellte Publikationen

Erstellte Publikationen
Felder
Betrieb
Filialnummer der ausgewählten
      Betriebsstätte. Dahinter dessen Bezeichnung.
Publikationsname
Name
      der Publikationen
Eigenschaft
Zeigt die Eigenschaft einer
      Publikation:
-
Amic-Standard
-
benutzerdefiniert
Funktionen
Speichern
Speichert die Angaben
Zeile einfügen
Fügt
      eine Zeile ein
Zeile entfernen
Entfernt die gewählte
      Zeile

---

## Erstellung des Exports

Erstellung
des Exports
Diese Funktion sorgt dafür, dass aus dem Kunden der
Rechnung das zugehörige Profil ermittelt und die eRechnung in drei Stufen aus
den Rechnungsdaten erstellt wird.
1
.
Daten extrahieren
1.
Die im
Exportprofil
eingetragenen Prozeduren
lesen Daten aus den Rechnungsdaten der Datenbank
und speichern diese in einen Tabellensatz zwischen.
2.
Diese Prozeduren können mit Hilfe des Profilpflegers auf Funktionalität und
Inhalt gestestet werden. Die Zuordnungen der Daten ergeben sich aus der
Spezifikation 3.0.1 der
XRechnung
. Alle Daten, die ermittelt werden, werden in Tabellen gespeichert,
deren Namen sich an diese Spezifikation anlehnen.
Die Datenbankprozeduren
stellen die einzige Möglichkeit dar, Individualisierungen in den Daten
vorzunehmen.
Als Orientierung für die
Herkunft von Daten haben wir Standard-Prozeduren mit dem Namenspräfix
„AMIC_STD_XRE_“ zur Verfügung gestellt.
2.   Xml
formulieren
1.
Die ermittelten Daten werden nun in das Datenaustauschformat UBL (
Universal
Business Language
), einem XML-Format, gelesen, erstellt und in eine Datei im
vorgegebenen Verzeichnis gespeichert.
2.
Dabei werden die Business-Terms gemäß der
Spezifikation
für UBL2.1
in die Felder der einzelnen Businessterms (
BT
) gelesen.
Das Mapping ist vom Standard
vorgegeben und es können keine Änderungen an der Zuordnung vorgenommen
werden.
3.
Archivieren
Zusätzlich wird das
erstellte XML auch noch im Archiv als eRechnung-Export (Belegklasse
8040
– eRechnung Xml) gespeichert.
Hinweis:
Eine Erweiterung des eRechnung-Standards um
kundenspezifische Felder ist
NICHT
vorgesehen. Es können also außerhalb
des Standards keine weiteren Informationen in diesem Format exportiert werden.
Zur Vermeidung von Problemen bei der Konsistenzprüfung
warnen wir ausdrücklich vor dem Missbrauch ungenutzter Datenfelder zum Transport
von artfremden Daten!

---

## Erstellung des Rosi-Profils (eingehend)

Erstellung des Rosi-Profils (eingehend)
Für die Erstellung eines Rosi-Profils sind die
folgenden Schritte durchzuführen:
•
Nachrichtenprofil anlegen
•
Kommunikationsbatch anlegen
•
EDI-Partner anlegen
Nachrichtenprofil anlegen
In dem Nachrichtenprofil wird angegeben, in welche
Richtung und um welchen Typ von EDI-Nachricht es sich handelt. Es wird eine
EDI-Nachricht vom Typ „ORDERS“ verwendet.
1.
Die Anwendung „Rosi Einrichtung“ mit dem Direktsprung [ROSIE] aufrufen.
2.
Die Variante „Rosi Nachrichtenprofil“ auswählen.
3.
Mit der Taste „F8“ die Maske zum Anlegen eines neuen Nachrichtenprofils
aufrufen.
=> Die Maske zum Anlagen des Nachrichtenprofils wird
geöffnet.
4.
Die Zahl im Feld „ID“ wird vom Programm automatisch vergeben. Es kann aber auch
vom Benutzer eine Zahl eingegeben werden. Wird eine existierende Nummer
eingegeben, so führt dies beim Speichern zu einer Fehlermeldung.
5.
Im Feld „Bezeichnung“ die Bezeichnung „
Rosi ORDERS Test
“ eingeben.
6.
Im Feld „Richtung“ die Taste „F3“ drücken und die Richtung „eingehend“
auswählen.
7.
Im Feld „Typ“ die Taste „F3“ drücken und den EDI-Nachrichtentyp „ORDERS“
auswählen.
8.
Im Feld „Mapping-ID“ die Zahl ‚0‘ eintragen.
9.
Das Feld „Makroname“ bleibt leer.
10.  Die
Eingaben mit der Taste „F9“ speichern. Anschließend die Maske mit der Taste
„ESC“ schließen.
Kommunikationsbatch anlegen
In dem Kommunikationsbatch wird angegeben: Die
Richtung und das Quellverzeichnis der EDI-Nachricht.
1.
Die Anwendung „Rosi Einrichtung“ mit dem Direktsprung [ROSIE] aufrufen.
2.
Die Variante „Rosi Konfiguration Batch“ auswählen.
3.
Mit der Taste „F8“ die Maske zum Anlegen eines neuen Kommunikationsbatches
aufrufen.
=> Die Maske zum Anlagen des Kommunikationsbatches wird
geöffnet.
4.
Die Zahl im Feld „ID“ wird vom Programm automatisch vergeben. Es kann aber auch
vom Benutzer eine Zahl eingegeben werden. Wird eine existierende Nummer
eingegeben, so führt dies beim Speichern zu einer Fehlerm
[...]


---

## Ethernet-(LAN-)COM-Ports

Ethernet-(LAN-)COM-Ports
Wenn Sie einen Terminalserver betreiben und an Ihrem
Terminalclient keine seriellen Schnittstellen zur Verfügung stellen, dann
empfiehlt sich zum Beispiel der Einsatz eines Seriellen-Geräte-Servers. Dies ist
ein Gerät, das Sie im Netzwerk betreiben und an das Sie serielle Geräte wie z.B.
das Kundendisplay anschließen können.
Die Software, die mit diesem Geräten (z.B. Moxa NPort
5110) mitgeliefert wird, stellt Ihnen dann einen virtuellen COM-Port über das
Netzwerk zur Verfügung.

---

## Excel Einrichtung Verbindungen

Excel Einrichtung Verbindungen
Ein über die BI Schnittstelle arbeitende Excel-Mappe
bedient sich per Datenquery an Daten aus dem Referenz-ERP System. Hierbei wird für
jede Variante der Auswahlliste eine View bereitgestellt, die mit BI_ beginnt und
dann zunächst die ID der Anwendung gefolgt von der ID der Variante als Namen
trägt und zum Abschluss eine 0 für Standard Variante und 1 für private Variante.
Als Beispiel sei hier die Auswahlliste „Vorgangsübersicht“ mit der Variante
Vorgangsübersicht.
Intern trägt die Anwendung Vorgangsübersicht den Namen
SV_UEBERSICHT und die erste Variante den Namen Status, somit lautet der Name der
passenden BI View : BI_Uebersicht_Status_0. Zusätzlich dazu existiert dann immer
eine passende View zum angewälten Profil mit der Endung _Profil:
Die Felder des BI Interfaces entsprechen den Felder
der Auswahlliste, und zwar des SQL Statements bereinigt um alle doppelten
Felder. Zusätzlich werden alle Felder, die mit einen Formatstring verbunden sind
(siehe auch FIELD) als textliche Representation mit angegeben, hierbei wird die
Endung _Text an das .Feld angehängt.
Im Excel wird dann einfach nur die Query auf diese
View gelegt (in Excel zu errreichen über den Abschnitt DATEN ->
Verbindungen):

---

## Exportieren der EDI-Nachrichten (ausgehend)

Exportieren der EDI-Nachrichten (ausgehend)
Wird für den Kunden, für den eine Rosieinrichtung
eingerichtet ist eine Rechnung geschrieben, so erscheint der jeweilige Name der
Einrichtung in der Auswahlliste (REB).
Soll die Rechnung per EDI übertragen werden, so muss
der Beleg über den Menüpunkt (Elektronische Rechnung ->
EDI-Datentransfermonitor) exportiert werden.
Hier werden alle markierten Rechnungen zunächst nach
EDI-Partner auseinandersortiert und die im EDI-Profil hinterlegten Prüfroutinen
durchlaufen. Es werden nur Rechnungen mit EDI-Partner berücksichtigt, welche
noch nicht erstellt wurden. Falls die Prüfroutinen bestanden werden, erscheint
nun der Button „Edi-Nachricht erstellen“.
Mit einem Klick auf den Button „Edi-Nachricht
erstellen“ wird die Nachricht erstellt und falls es im Profil hinterlegt ist,
auch die zugehörige Datei erzeugt und versendet.

---

## Exportstatus im Beleg

Exportstatus im Beleg
Für jeden Beleg wird der eRechnungs-Exportstatus in
der Tabelle „XRe_ExportStatus“ festgehalten. Je nach Einstellung des
SPA 1153 - eRechnung editieren
wird
entweder das Editieren nach dem Export nur nach Warnung, generell oder gar nicht
erlaubt.

---

## Exportprotokoll (Bei Problemen mit dem Export von eRechnungen)

Exp
ortprotokoll
(Bei Problemen mit dem Export von eRechnungen)
Im Direktsprung
[XRE]
findet sich eine Variante
Exportprotokoll. Dort werden alle Stufen des Exports in allen Teilschritten für
jeden Beleg dokumentiert.
Zunächst finden sich Einträge für jede aufgerufene
Prozedur mit ihren Parametern und der Info für den Erfolgs- bzw.
Misserfolgsfall. Ggf. wird von hier auf das Fehlerprotokoll
[FEHLP]
verwiesen.
Im Anschluss finden sich Einträge für die Verarbeitung
der ermittelten Daten ins XML. Auch hier kann ggf. auf das Fehlerprotokoll
[FEHLP]
verwiesen werden.
Letztlich finden sich Einträge für die Serialisierung
der Daten zum XML und die Archivierung der Datei ins Archiv.

---

## Farbzuordnung

Farbzuordnung
Zu den im Bedienerstamm festgelegten Farben besteht
folgende Zuordnung
Bereich
Hintergrund
Schrift
Systeminfobereich
wie
      Menü-Hauptpunkte-Bereich
„Titel Schrift“
Favoritenbereich
wie
      Arbeitsbereich
„Titel Schrift“
Menüpunktbereich
wie
      Arbeitsbereich
„Titel Schrift“
Systemmeldebereich
wie
      Arbeitsbereich
„Titel Schrift“
Menü-Hauptpunkte-Bereich
„Hauptmenü Hintergund“
Farbverlauf von dieser Farbe zur
      Farbe des Arbeitsbereiches.
„Hauptmenü Schrift“
Arbeitsbereich
„Auswahlmenü
      Hintergrund“
„Auswahlmenü Schrift“
Überschriften haben die gleiche
      Farbe wie die Hauptmenü-Punkte
Menülogobereich
wie
      Menü-Hauptpunkte-Bereich
hier
      sind Grafiken möglich, siehe
Hauptmenü-Menülogobereich
Nicht einrichtbar sind die Farben der Tooltips, die
selektierten Menü-Hauptpunkte, deren Vorselektierungen sowie die der
Menü-Punkte.

---

## Feldauswahl der Auswahlliste

Feldausw
ahl der Auswahlliste
In den Auswahllisten wird von Branchen-ERP eine bestimmte
Feldauswahl vorgegeben, die nicht immer für jeden Anwender passend sein muss. Im
Gestaltungsdialog hat man die Möglichkeit nicht benötigte Spalten auszublenden
bzw. aus den zur Verfügung stehenden Spalten diejenigen auszuwählen, die
sinnvoll sind.
Auf dem Register
Feldauswahl
findet man links
alle zur Verfügung stehenden Felder mit den Feldtypen, die von Branchen-ERP vorgegeben
wurden und den Filtertypen (nur Auswahlliste 2.0). Rechts findet man die Felder,
die dann in der Auswahlliste tatsächlich erscheinen mit den ggf. vom Anwender
geänderten Feld- und Filtertypen.
Im SQL-Text kann man Spalten bereits im Vorwege
ausblenden. Dazu dient das Schlüsselwort HIDDEN.
FIELD
Text,fibuvp_text,char,20
,HIDDEN
Dieses Feld erscheint dann nur in der linken Anzeige
des Registers
Feldauswahl
und kann dann vom Anwender eingeblendet
werden.
Für die Feldtypen steht eine F3-Auswahl zur Verfügung.
Um geänderten Feldtypen wieder auf die von Branchen-ERP vorgegebenen Originalfeldtypen
zu setzen, kann man die Funktion „Original wiederherstellen“ ausführen.
Es stehen zwei verscheiden Filtertypen zur
Verfügung:
•
Standard
: Hier kann man
entweder im Filter frei einen Wert eingeben oder einen Wert aus den angebotenen
Daten auswählen. Zusätzlich besteht die Möglichkeit den Vergleichsoperanden
auszählen:
•
Mehrfachauswahl
: Hier kann
die Werte frei eingegeben oder aus einer Auswahl aller Werte, die in den Daten
vorkommen, mehrere Werte auswählen. Es besteht jedoch keine Möglichkeit den
Vergleichsoperator auszuwählen.
Im SQL-Text kann man Spalten bereits im Vorwege so
einstellen, dass der Filtertyp
Mehrfachauswahl
verwendet wird. Dazu dient
das Schlüsselwort EXTENDEDFILTER.
FIELD
Mahndatum,Mahndatum,d4,20
,EXTENDEDFILTER
Alle Spalten mit einem FS-Format
haben automatisch immer den Filtertypen
Mehrfachauswahl
.
In der Spalte Vergleich kann festgelegt werden, mit
welchem Operator in der Filterzeile gesucht
[...]


---

## FRZ-Zuordnung

FRZ-Zuordnung
Sie haben nun zahlreiche Elemente auf ihrer
Bedienoberfläche angebracht. Die Namen durften Sie dabei frei wählen. Nun müssen
diese noch mit den von der Entwicklung zur Verfügung gestellten Datenstrukturen
verknüpft werden. Dazu wird in der Formularzuordnung
[FRZ]
auf der
Registerkarte Kasse
eine Zuordnung eingetragen.
Ordnen Sie die von Ihnen benannten Elemente den
einzelnen Elementen zu.
Funktionsschaltflächen haben bereits einen
Funktionscode. Diese brauchen hier nicht zugeordnet werden.
Pflichtfelder
Eingabefeld
Das
      Eingabefeld, das für Eingaben verwendet wird. Dieses Feld ist ein rein
      technisches Feld.
Artikelnummer
Eingabefeld
      Artikelnummer
Menge
Eingabefeld Mengen
Preis
Eingabefeld Preis
Abfrage Sperrcode
Eingabefeld für den
      Sperrcode
Bon
      Vorschau (Positionen)
Bon-Vorschau-Fenster
BelegSumme
Ausgabe Belegsumme
Noch
      zu zahlender Betrag
Ausgabe Restzahlbetrag
Zahlwährung
Währung, in der gezahlt
      wird
Rückgeld
Ausgabefeld des
      Rückgelds
RückWährung
Währung des Rückgelds
Belegwährung
Ausgabefeld Belegwährung
Weitere Felder
Lagernummer
Eingabe einer
      Lagernummer
Lagerbezeichnung
Ausgabe einer
      Lagerbezeichnung
Artikelbezeichnung
Ausgabe einer
      Artikelbezeichnung
Anzeige Eingabestatus
Anzeigefeld für den
      Eingabestatus
TestDialogFeld1
TestDialogFeld2
Dialoggruppe Leergut
Name
      der Gruppe für Leerguterfassung
Leergut Menge
Eingabefeld Leergutmenge im
      Leergut-Grid
Leergut Artikelnummer
Ausgabefeld Leergutartikelnummer im
      Leergut-Grid
Leergut
      Artikelbezeichnung
Ausgabefeld Leergutartikel
      Bezeichnung im Leergut-Grid
Rabatt Eingabe Feld
Eingabefeld für Rabatte
Leergut ArtikelId
Ausgabefeld Leergutartikelid im
      Leergut-Grid
Dialoggruppe
      Mengenkorrektur
Name
      der Gruppe für Mengenkorrektur
Korrekturfeld Menge
Eingabefeld
      Mengenkorrektur
Dialoggruppe
      Preiskorrektur
Name
      der Gruppe für Preiskorrektur
Korrek
[...]


---

## Geschäftsvorfallcode

Geschäftsvorfallcode
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Geschäftsvorfallcode
F11
Direktsprung
[ECL]
Werden die Daten im Format MT940 oder CAMT053
importiert, so enthält der Verwendungszweck ggf. auch eine Zeile mit dem
Geschäftsvorfallcode (=GVC). Der Geschäftsvorfallcode definiert alle aus der
Bankbuchung resultierenden Geschäftsvorfälle in Form eines dreistelligen
Schlüssels. Man kann zu jedem Geschäftsvorfall einen separaten Text hinterlegen,
der beim Einlesen als Text und später beim Buchen als Positionstext übernommen
wird.
Die Option „Ersatzauftraggeber unterdrücken“ wird nur
ausgewertet, wenn zu einer Hausbank die Option „Auftraggeber aus
Verwendungszweck verwenden“ aktiviert ist. Bei einigen Geschäftsvorfällen steht
der Auftraggeber nicht im Verwendungszweck. Soll in diesen Fällen der Text aus
dem Verwendungszweck nicht übernommen werden, so kann muss man hier
Ja
eintragen.

---

## Geschäftsvorfallcode

Geschäftsvorfallcode
Hauptmenü
Mahn-,Zahl-, Zinswesen
Stammdaten
Geschäftsvorfallcode
Direktsprung
[FIGVC]
Dies sind Stammdaten, die nicht vom automatischen
Zahlungsverkehr, sondern von dem Modul E-Clearing verwendet werden. Siehe
hierfür unter
e-Clearing
.

---

## Gruppen ein-/ausblenden (nur Auswahlliste 2.0)

Gruppen ein-/ausblenden (nur Auswahlliste 2.0)
Das Ein- und Ausblenden der Gruppen dient lediglich
dazu, nicht notwendige Bereiche auszublenden, wenn die Größe des Bildschirms
nicht ausreicht, um das Menü in kompletter Breite darzustellen. Es lassen sich
lediglich folgende Gruppen auf dem ersten Register (Anwendungsregister)
ausblenden.
•
Filter
•
Stammdatenpflege
•
Export
Die Funktionen stehen trotzdem weiterhin zur
Verfügung.

---

## Handhabung der Schnittstelle

Handhabung der Schnittstelle
Die Handhabung der Schnittstelle setzt sich
hauptsächlich aus folgenden Arbeitsschritten zusammen:
Übergabe der Belege in die internen Datenbereich der
RFS-Schnittstelle.
Kontrolle der aktuell anliegenden Zahlungen
Erstellen der DTA-Dateien und Protokolldateien
Beide Arbeitsgänge werden in der Regel täglich
ausgeführt, da das Grundprinzip der RFS-Schnittstelle auf den täglich
anfallenden ( nach Fälligkeiten  sortierten) Zahlungsvorgängen beruht.

---

## Hauptmenü-Favoritenbereich

Hauptmenü-Favoritenbereich
Element
Tastatur
Beschreibung
Icon
Beschriftung
Favoriten(X)
X
      steht für die Anzahl der Favoriten
Favoriten sind vom Referenz-ERP-Bediener individuell
ausgewählte Menü-Punkt zwecks schnelleren Zugriffs auf häufig verwendete
Menüpunkte des Arbeitsbereiches.
Zusätzliche Informationen zum Favoriten-Handling
finden sich unter
Menüpunkte
und
Kontextmenüs der Menüpunkte
.
Für Pflege und Sortierung der Favoriten siehe
Menü-Favoriten
und
Menü-Favoriten-Sortierung
.

---

## Hauptmenü - Menüpunkte

Hauptmenü -
Menüpunkte
Nach Anklicken eines Menüpunktes werden entsprechende
Referenz-ERP-Aktivitäten ausgelöst.
Hinweis: Gewisse Referenz-ERP-Aktivitäten ziehen keine
sofortige User-Interaktion nach sich. Gründe hierfür können langwierige
Berechnungen bzw. Datenerhebungen sein. Das bedeutet das unter Umständen der
Eindruck entstehen mag, dass Referenz-ERP nicht reagiert. In späteren Referenz-ERP-Releases
wird das Hauptauswahlmenü diesen Umstand berücksichtigen und vorbeugend dem
Referenz-ERP-Anwender eine visuelle Rückmeldung geben das nicht-visuelle
Referenz-ERP-Aktivitäten durchgeführt werden.
Je nach Aktivität(*) gibt es folgende
Icon-Zuordnungen
Funktionsart
Privat
Icon-Zuordnung
Standard-Zuordnung
  (**)
Dialog
Nein
menuicon_anwendung
window_dialog
Dialog
Ja
menuicon_privatanwendung
window_dialog_user
Liste, Crystallreport
Nein
menuicon_druck
printer2
Liste, Crystallreport
Ja
menuicon_privatdruck
printer2_user
Anwendung
Nein
menuicon_auswahlliste
table2_selection-row
Anwendung
Ja
menuicon_privatauswahlliste
table2_selection_row_user
BusinessIntelligence
Für
      Beide
menuicon_businessintelligence
excel_2013
Alle
      übrigen wie folgt, entweder
Nein
menuicon_keinicon
placeholder
oder
Ja
menuicon_privat
user
(*) Die Funktionsarten werden über den Controlstring
einer Funktion ermittelt. Maßgeblich ist dafür die Datenbank-Prozedure
amic_get_funktionsart
.
(**) Das resultierende Icon wird dann über die
Relation
Iconzuordnung
ermittelt. Es ist angedacht in späteren
Aeins-Releases hier private Iconzuordnungen durchführen zu können. Somit besteht
dann die Möglichkeit private Funktionen mit „eigenen“ Icons auszustatten.
Jeder Menü-Punkt ist mit einem Menü-Punkt-Tooltip
versehen und besteht aus folgenden Bestandteilen:
Komponente
Daten-Herkunft im
      Anwendungsfunktion-Pfleger
Überschrift
Tiptext Titel
Text
Tiptext
(optional) Direktsprung
Direktsprung
Die Anzeige der Tooltips ist über Steuerparameter 931
pro Bediener abschaltbar.

---

## Hausbanken

Hausbanken
Hauptmenü
Finanzbuchhaltung
Stammdaten
Hausbanken
Direktsprung
[BNKH]
.
Hausbanken
sind die eigenen Banken des
jeweiligen Man­danten für den Zahlungsverkehr. Sie werden im Automatischen
Zahlungsverkehr, von e-Clearing, der Wechselbuchhaltung und vom Zahlungsverkehr
Bank verwendet. Hier werden alle Informationen hinterlegt, die für die
Abwicklung der Bankgeschäfte notwendig sind:
Allgemein
Hausbanknummer
Eine
      frei zu vergebende eindeutige Nummer, über die dann auf die Hausbank
      verwiesen wird.
Währung
Währung, in der das Hausbankkonto
      geführt wird.
IBAN
Ab
      dem 28.01.2008 wird für den Zahlungsverkehr SEPA (Single Euro Payments
      Area) eingeführt. Dieses Verfahren benötigt die IBAN (International Bank
      Account Number). Diese kann/muss in dem Feld IBAN eingetragen werden. Es
      erscheint folgender Hinweis, wenn keine IBAN eingetragen wird:
Wenn sie den Zahlungsverkehr ab dem
      20.01.2008 auf SEPA-Basis laufen lassen, müssen sie die IBAN
      eintragen.
Hat
      man eine IBAN eingetragen, so wird aus dieser (für Deutschland, Österreich
      und Belgien) die Bank und Kontonummer generiert. Werden diese Daten nicht
      vorgeschlagen, so ist entweder die IBAN nicht nach dem Standardschema
      aufgebaut, falsch eingegeben oder die Stammdaten der Banken sind nicht
      korrekt gepflegt (z.B. nicht eingetragener Staat) .
Anschließend wird sie über ein
      Prüfziffernverfahren getestet. Bei fehlerhafter Nummer erscheint folgende
      Fehlermeldung:
Die Prüfziffernberechnung ergibt,
      dass diese IBAN falsch ist.
Diese Meldung ist nur eine
      Warnmeldung. Änderungen werden trotz Meldung abgespeichert.
Der
      Test der IBAN kann entweder für einzelne
Banken
oder global per
Steuerparameter
abgeschaltet
      werden.
Bank
Verweis auf die im
Bankenstamm
festgelegte Bank.
      Man kann direkt die Bezeichnung oder die BLZ eingeben. In der F3-Auswahl
      kann zusätzlich auch nach BIC oder
[...]


---

## Historie

Historie
Jede der Prüf-Funktionen zeigt im Anschluss eine
Historie der Prüfungen.
Historie
Datum
Zeitstempel der Prüfung
Bediener
Ausführender Bediener
UStId
Geprüfte UmsatzsteuerId
Code
Code
      der Prüfung.
Mehr
      dazu auf der Webseite
https://evatr.bff-online.de/eVatR/xmlrpc/codes
Prüfung
Textform des
      Prüfergebnisses
Name
Angabe, ob der hinterlegte Name zu
      dieser UStId gehört
Strasse
Angabe, ob die hinterlegte Strasse
      zu dieser UStId gehört
PLZ
Angabe, ob die hinterlegte
      Postleitzahl zu dieser UStId gehört
Ort
Angabe, ob der hinterlegte Ort zu
      dieser UStId gehört
Amtl. Best
Gibt
      an, ob eine amtliche Bestätigung angefordert wurde

---

## Importieren einer EDI-Nachricht (eingehend)

Importieren einer EDI-Nachricht (eingehend)
1.
Eine Datei mit einer „ORDERS“-EDI-Nachricht in das Verzeichnis „..\Rosi-Test“
hineinlegen.
2.
Das Import-Programm mit dem Befehl „GSCEdiImport.exe db 0“ aufrufen.
db =>
Name der Datenbank
3.
Jetzt das Makro „C#AMIC_ROSI_EDI_ORDRSP_FRESSNAPF“ ausführen.
=> Es wird
ein Vorgang (Auftrag) angelegt.

---

## Importprotokoll

Importprotokoll
In der Anwendung
eRechnung
[XRE]
gibt die Variante „Import Protokoll“
Aufschluss über die importierten Archiveinträge und den Status der einzelnen
Importschritte.

---

## ImportVorgStammUFLD

ImportVorgStammUFLD
UFLD-Felder
In dieser Relation werden die Setzungen von
UFLD-Feldern für den Vorgang vorgenommen.
Bitte beachten Sie, dass nur UFLD-Felder gesetzt
werden können, die vom importierenden Bediener für die jeweilige
Vorgangs(unter-)klasse gemäß Einrichtung gesetzt werden dürfen.
Feld
Bedeutung
IVS_GUID
Guid
      des Stammsatzes
UFLDID
Id
      Nummer des User Feldes
UFLDWert
Inhalt des Feldes

---

## Inbetriebnahme

Inbetriebnahme
Die App muss im Apple AppStore die APP auf das
Endgerät zu installieren. Downloadlink:
https://apps.apple.com/de/app/a-eins/id1450152656
Sobald man im Portal freigeschaltet wurde, kann man
das Gerät auf registrieren. Die Zugangsdaten dafür stellt der Branchen-ERP Support oder
der zuständige Systemadministrator bereit. I.d.R bekommt man diese auf die
Applemail.

---

## Intrastat einrichten

Intrastat einrichten
Felder
Beschreibung
Ausgabeformat
0:
      ASCII-Format
1:INSTAT/XML
Aus
      Gründen der Datensicherheit und der ab Bezugszeitraum Januar 2022
      verpflichtenden Angabe von Umsatzsteuer-Identifikationsnummer des
EU
-Handelspartners
      und des Ursprungslandes der Ware in der Verkehrsrichtung Versendung wird
      eine Ablösung der Dateimeldungen im Festformat ASCII-Fix zum 30.06.2021
      angestrebt.
Neuanträge zur Meldung in
      diesem Format werden daher ab 01.02.2020 nicht mehr
      genehmigt!
Materialnummer Versand
5-stellige Materialnummer
      (Versand)
Die
      5-stellige alphanumerische Materialnummer für den Versand wird nach
      erfolgreicher Prüfung der gelieferten Testdateien vom Statistischen
      Bundesamt vergeben. Für die Übermittlung der Testdatei muss hier „XGTEST“
      stehen.
Materialnummer Einfuhr
5-stellige Materialnummer
      (Versand)
Die
      5-stellige alphanumerische Materialnummer für die Einfuhr wird nach
      erfolgreicher Prüfung der gelieferten Testdateien vom Statistischen
      Bundesamt vergeben. Für die Übermittlung der Testdatei muss hier „XGTEST“
      stehen.
Warenbewegung Intrastat
0:
      Nein
1: Ja
Gibt
      die Eingabemöglichkeiten der
Intrastat
      Zusatzdaten
schon
      in der Vorgangserfassung frei.
Intrastat Dateipfad
Verzeichnis für die Ausgabedateien.
      Im Format INSTAT/XML werden dort noch zwei weitere Verzeichnisse „Einfuhr“
      und „Versendung“ angelegt.
Intrastat Dateiname
      Versand
und
Intrastat Dateiname Einfuhr
Diese Felder wird nur im
      ASCII-Format abgefragt.
Im INSTAT/XML-Format setzt sich der Name
      automatisch wie folgt
      zusammen:
Materialnummer_YYYYMM_YYYYMMDD_HHMM.XML
wobei YYYYMM der Beginn des Auswertungszeitraums ist,
      YYYYMMDD das Tagesdatum und HHMM die Uhrzeit(Stunden und Minuten), an dem
      das Dokument erstellt wurde.
Wenn es eine Testmeldung ist, dann steht
      statt der Materialnummer d
[...]


---

## Kontenerkennung und automatische Auszifferung

Kontenerkennung und
automatische Auszifferung
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Kontierung
/Auszifferung
Direktsprung
[ECL]
Dieser Prüfungslauf kann jederzeit separat gestartet
werden. Zusätzlich kann man per
Option
F10
einstellen, dass
nach erfolgreicher Dateneinspielung der Prüfungslauf automatisch startet.
Folgende Tests werden in der angegebenen Reihenfolge durchgeführt:
Anhand der Bankleitzahl und der Kontonummer wird die
Hausbank bestimmt. Ist dies nicht möglich, wird ein Hinweis ausgegeben und
dieser Belege als nicht zu verarbeiten markiert. Dieses Problem kann auf mehrere
Arten behoben werden:
1.
Man trägt die Hausbank manuell über die Funktion „Hausbank zuordnen“ ein. Hier
öffnet sich eine F3-Auswahl mit zwei Varianten. Die aktive Variante zeigt alle
Hausbanken mit der gleichen IBAN aus dem Kontoauszug an, die zweite Variante
zeigt alle Hausbanken an.
2.
Die nicht gefundene Bank wird im Hausbankenstamm hinterlegt.
3.
Es kann vorkommen, dass in der Übergabedatei die Kontonummern in einem Format
übergeben werden, dass nicht dem gängigen Format mit 10-stelligen Kontonummern
entspricht. Dafür gibt es im Hausbankenstamm das Feld „abw. Bankkonto
e-Clearing“. Ist hier eine Nummer hinterlegt, so wird mit dieser Nummer versucht
die Hausbank zu bestimmen. Die Optionen „
Bei 11-stelligem Hausbankkonto
"Deutsche Bank" Format annehmen
“ und „
Hausbankkonto bei Commerzbank
anpassen
“ werden dann nicht angewendet.
Anschließend werden die einzelnen Positionen
verarbeitet. Die Suchstrategie erfolgt in der hier angegebenen Reihenfolge.
Als erstes Suchverfahren kann die
VWZ-Zuordnung
F11
herangezogen
werden. Die VWZ-Zuordnung wird für die Datensätze gleich zu Beginn ausgeführt,
wenn im Feld „Ausführungszeitpunkt“ der Wert „
vor
Kontenerkennung
steht.  Wird für den Bereich Gutschrift bzw. Lastschrift im
Verwendungszweck der entsprechende Text gefunden, wird das dort hinterlegte
Konto entsprechend vorbelegt.
Sind
[...]


---

## Kontrolle der aktuell anliegenden Zahlungen

Kontrolle der aktuell anliegenden Zahlungen
Der Direktsprung RFS  öffnet eine tabellarische
Übersicht aller Daten  der RFS Schnittstelle.
Mittels der üblichen Auswahllisten-Mechanik von Aeins
bieten sich hier verschiedene Darstellungs- und Auswahlmöglichkeiten:

---

## Kostenstellen

Kostenstellen
Hauptmenü
Kostenrechnung
Kostenstellenstamm
Kostenstellen
Direktsprung
[KST]
Um mit Kostenstellen zu arbeiten, gibt es folgende
Vorbedingungen bzw. Einstellungsvoraussetzungen:
1.
Der Steuerparameter "
Kostenstellenrechnung angeschlossen
" muss gesetzt
sein.
2.
Die Kostenstellen müssen eingerichtet sein. Hierzu gibt es zwei
Stammdatenpfleger
•
Kostenstellen (ohne Verteilung)
•
Verteilkostenstellen (mit Verteilung)
3.
Im
Sachkontenrahmen
Direktsprung
[SKS]
muss bei den in Frage kommenden Aufwandskonten im Feld „Sperre
Kostenstelle“ aus folgenden Möglichkeiten gewählt werden
•
Gesperrt
:    Es wird keine Kostenstelle
abgefragt
•
Kann
:         Es kann eine
Kostenstelle eingeben werden, muss aber nicht
•
Muss
:         Es muss eine
Kostenstelle eingegeben werden
•
Fest
:          Es
muss die im Sachkontenstamm festgelegte Kostenstelle verwendet werden
Im Feld Kostenstelle kann
hier die Nummer einer Kostenstelle eingegeben werden, die dann bei der
Belegerfassung automatisch vorgeschlagen wird.
4.
Damit auch Rechnungen aus der Warenwirtschaft beim Fibu-Übertrag automatisch in
die Kostenstellenrechnung eingetragen werden können ist es nötig,
Kostenstellengruppen
zu
definieren, in denen die Kostenstellen des Artikels für Einkauf und Verkauf
angegeben werden können.
Diese werden dann im Artikel über die Funktion
Kostenst./Statistik/Abteil
gepflegt, und
wenn dann der Artikel im Vorgang angesprochen wird, wird die jeweilige
Kostenstelle bebucht.
5.
Im Mandantenstamm sollte eine Fehlerkostenstelle eingerichtet werden. Diese
Kostenstelle wird herangezogen, wenn zu GuV-Konten keine Kostenstelle hinterlegt
ist und die „Sperre Kostenstelle“ des angesprochenen Kontos nicht auf Gesperrt
oder Fest seht.
Erfassung der Kostenstellen
Folgende Felder können in dem folgenden
Eingabebildschirm erfasst werden
Beschreibung
Kostenstelle
Nummer der Kostenstelle. Es ist zwar
      möglich eine Kostenstelle mit der Nummer 0 zu erfassen, jedoch wir
[...]


---

## Kostenträger

Kostenträger
Hauptmenü
Kostenrechnung
Kostenträgerstamm
Kostenträger
Direktsprung
[KSTRS]
Um mit Kostenträgern zu arbeiten, gibt es folgende
Vorbedingungen bzw. Einstellungsvoraussetzungen:
1.
Der Steuerparameter "Kostenträgerrechnung angeschlossen" muss gesetzt sein.
2.
Die Kostenträger müssen eingerichtet sein. Hierzu gibt es zwei
Stammdatenpfleger
•
Kostenträger (ohne Verteilung)
•
Verteilkostenträger (mit Verteilung)
3.
Im
Sachkontenrahmen
Direktsprung
[SKS]
muss bei den in Frage kommenden Aufwandskonten im Feld Sperre
Kostenträger aus folgenden Eintragsmöglichkeiten gewählt werden
•
Gesperrt
Es
wird kein Kostenträger abgefragt
•
Kann
Es kann
ein Kostenträger eingeben werden, muss aber nicht
•
Muss
Es muss
ein Kostenträger eingegeben werden.
•
Fest
Es muss
der im Sachkontenstamm festgelegte Kostenträger verwendet werden.
Im Feld Kostenträger kann
hier die Nummer eines Kostenträgers eingegeben werden, der dann bei der
Belegerfassung automatisch vorgeschlagen wird.
4.
Damit auch Rechnungen aus der Warenwirtschaft beim Fibu -Übertrag automatisch in
die Kostenträgerrechnung eingetragen werden können, ist es nötig,
Kostenträgergruppen zu definieren, in denen die Kostenträger des Artikels für
Einkauf und Verkauf angegeben werden können.
Diese werden dann im Artikel
über die Funktion
Kostenst./Statistik/Abteil
gepflegt, und
wenn dann der Artikel im Vorgang angesprochen wird, wird der jeweilige
Kostenträger bebucht.
5.
Im Mandantenstamm sollte ein Fehlerkostenträger eingerichtet werden. Dieser
Kostenträger wird herangezogen, wenn zu GuV-Konten versehentlich kein
Kostenträger hinterlegt ist und die „Sperre Kostenträger“ des angesprochenen
Kontos nicht auf
Gesperrt
oder
Fest
seht.
Erfassung der Kostenträger
Folgende Felder können in dem folgenden
Eingabebildschirm erfasst werden
Beschreibung
Kostenträger
Nummer des Kostenträgers. Es ist
      zwar möglich einen Kostenträger mit der Nummer 0 zu erfassen, jedoch wird
      dieser nicht al
[...]


---

## Kunden löschen (inkl. 1+2+7+35)

Kunden löschen (inkl. 1+2+7+35)
Es werden die Daten in folgenden Tabellen
gelöscht:
Anschriftstamm unter der Bedingung: where (AdressTyp =
11) or (AdressTyp = 12)
AnschriftAddon unter der Bedingung: where (AdressTyp =
11) or (AdressTyp = 12)
BEMERKPOSITION unter der Bedingung: where (BemerkTyp =
0) or (BemerkTyp = 1)
BEMERKPOSITIONWERTE unter der Bedingung: where
(BemerkTyp = 0) or (BemerkTyp = 1)
BEMERKSTAMM unter der Bedingung: where
(BemerkTyp = 0) or (BemerkTyp = 1)
Bemerkung unter der Bedingung: where (BemerkTyp = 0)
or (BemerkTyp = 1)
KundenMatchcode
KundenAusland
KundenBank
KundenBonus
KundenBonusSteu
KundenGrLink
KundenMitglied
KundenNotizen
KundenOberKunde
KundenSuchBegr
KundenSummen
KundenZahlBed
KundenZahlKunde
KundenVersAnschr
KundenStamm
KundenAddon
kundengruppe
kundenmatchcode
kontostamm unter der Bedingung: where kontotyp=2
KONTRAKTGRKUNDE
KONTRGRUPPE
PartieKundListe
PartieLiefListe
Wiedervorlage unter der Bedingung: where (WiederTyp =
2)
BesuchsBericht
kundennachhaltigkeit
amic_sharepoint
UmsatzsteueridListe_SteuerGruppe unter der Bedingung
MandantKunde nicht geich 0
UmsatzsteueridListe unter der Bedingung Mandantkunde
nicht gleich 0
disposition
MitarbeiterGruppeLink
Anschriftennichtvererben
zeiterfassung
KundenMitglAktion
WarenrueckBASIS
RemoteKunden
KundenTankKarte
KundeMaskeDaten
KundenKredit
KundenInfoZeile
EZG_KundBeitrag
EZG_KundenListe
AHOI
wunschliste
BAUSTKUNDLISTE
BAUSTLIEFLISTE
SPEDISTAMM
KREDITLIMITPROTOKOLL
Beim Löschen der Kunden werden automatisch die
Vorgänge Ware
,
Vorgänge
Finanzbuchhaltung
,
Kontrakte
und
gelöschte Kunden
mit gelöscht.

---

## Kundenspezifischen Einstellungen

Kundenspezifischen Einstellungen
Die für die RFS-Schnittstelle maßgebliche
Kontenzuordnung ( Bisykonto ) wird unter Aeins im Feld „ Ext. Nr.“ hinterlegt (
Feld 3 = Kundennummer unter XCOM !). Weitere wichtige Felder sind:
Die Zahlungsbedingung ( falls der Vorkontenmechanismus
benötigt wird)
Die Bankverbindung ( für Bankeinzüge etc )
Die Zahlungsart zur Steuerung , ob Bankeinzug benutzt
werden soll ( Funktion FIBU-Merkmale )

---

## Lastschriftzahlungen

Lastschriftzahlungen
Empfohlene Vorgehensweise
Ab 2014 werden lediglich SEPA-Lastschriften im
Zahlungsverkehr unterstützt. Bis 2016 gibt es für innerdeutsche Überweisungen
eine Übergangsfrist.
Aus diesem Grund empfehlen wir dringend, die
Lastschriften über ein
Bezahlterminal
durchzuführen oder
besser hier das Bezahlverfahren mit PIN zu verwenden. In diesem Fall werden die
Bankeinzüge durch den Betreiber des Terminals durchgeführt.
Veraltete Vorgehensweise
Für die Lastschriftzahlungen wurden zuvor Kontonummer
und Bankleitzahl mit der Tastatur oder einem Kartenleser aus dem Magnetstreifen
einer EC-Karte erfasst.
Aus dieser Zeit stammen auch die nachfolgenden
Beschreibungen, für deren Funktionalität wir keine Gewähr mehr übernehmen
können.
Dieses Lastschriftverfahren gilt nur für
DTA-Lastschriftverfahren und kann für SEPA nicht verwendet werden! Da nach
Ablauf einer Übergangsfrist bis 2016 (im internationalen Zahlungsverkehr bereits
ab 2014) keine herkömmlichen Lastschriften mehr verwendet werden, wird diese das
DTA-Verfahren von uns nicht weiter unterstützt. Die Dokumentation dazu ist als
historisch zu betrachten.

---

## Lieferbelegstamm

Lieferbelegstamm
Lieferbelege erhalten beim Anlegen eine eindeutige
Nummer, die vom Bediener nicht zu ändern ist.
Lieferbelegdatensätze können
nicht geändert werden. Wenn ein Datensatz fehlerhaft ist, muss er gelöscht
werden. Er erhält dann ein Löschkennzeichen und die dazugehörigen Positionen
werden gelöscht.

---

## Löschen

Löschen
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Löschen
F8
Direktsprung
[ECL]
Löschen sollte nur mit äußerster Vorsicht verwendet
werden, da diese Daten benötigt werden, um doppelte Einspielungen zu verhindern.
Es steht daher auch nur zur Verfügung, wenn eine oder mehrere Zeilen markiert
sind (nicht bei Gesamtauswahl). Es werden nur ungebuchte Daten gelöscht.

---

## Mahnstufen

Mahnstufen
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Funktion Mahnstufen
F7
Direktsprung
[FIMSG]
.
Hierbei handelt es sich lediglich um Texte für die
verschiedenen Mahnstufen in einem Unternehmen.
Nummer
Laufende Nummer der Mahnstufe
Bezeichnung
Textbeschreibung der Mahnstufe z.B. 3.Mahnstufe.
Dieser Text kann im Mahnformular im Bereich 307 (Summen pro Mahnstufe) mit
ausgegeben werden. Ist der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in
Referenz-ERP gesetzt, so hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu
pflegen.

---

## Mahnwesen

Mahnwesen
Das
Mahnwesen basiert auf verschiedenen Parametern, die unter
"Stammdaten"
im Abschnitt
"Mahnwesen"
eingerichtet werden können.
Das Mahnwesen selber ist lediglich eine
Auswertung dieser Parameter
(Mahnabstand, Anschreiben, Gebühren,
etc.)
sowie der in
den offenen Posten hinterlegten Informationen
(Fälligkeit, Betrag,
etc.)
.
Zum Erstellen von Mahnungen sind folgende Schritte
notwendig:
•
Mahnvorschläge
erstellen
•
Mahnvorschläge
bearbeiten und freigeben
•
Mahnungen
bearbeiten

---

## Manueller Import

Manueller Import
In der Archivvariante können manuell XML-Dateien zum
Archiv hinzugefügt werden.
Verwenden Sie dazu die Funktion
Hinzufügen
die Belegklasse
8045
(eRechnung-Import-Xml) bzw
8044
(ZUGFerD-Pdf)
(ab Herbstversion
2025).
Mit der Funktion
eRechnung verarbeiten
kann nun manuell das
Xml bzw. Pdf eingelesen und in die Importtabellen geschrieben werden.

---

## Mandanten Server

Mandanten Server
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver
Direktsprung
[MS]
Dialog-Felder
Mandantenserver
Startzeit
Zeit
      an dem der Mandantenserver aufgerufen wurde
Lfd.Nr.
Nummer des bearbeiteten
      Prozesses
Zeit
Zeit
      der Erstellung des Prozesses
Bediener
Zum
      Prozess gehöriger Bediener
Vorgang
Beschreibung des bearbeiteten
      Prozesses
Status
Status der
      Verarbeitung
Mandant
Mandant des
      Mandantenservers
erledigt
Anzahl der erledigten
      Prozesse
fehlerhaft
Anzahl der fehlerhaften
      Prozesse
Zeit
      letzter Beleg
Zeit
      die die Verarbeitung des letzten Beleges gedauert hat
Zeit
      im Durchschnitt
Durchschnittlich benötigte Zeit für
      die Verarbeitung der Prozesse

---

## Maskenfelder im SQL verwenden

Maskenfelder im SQL verwenden
Man kann in den SQL-Statements, die man bei
Datenherkunft
SQL
auch auf Maskenfelder zugreifen. Man muss dann nur
einen Doppelpunkt vor den Name des Maskenfeldes schreibe und unbedingt Groß- und
Kleinschreibung beachten. Beispiel:
select AdressAnrede||' '||AdressVorName ||' '||
Adressname
from Anschriftstamm a join Kundenstamm k on
k.Adressidhauptadr=a.adressid
where Kontonummer=:ais1.KontoNummer$
Achtung:
So wie das Statement hier
formuliert ist kommt es zu einem Syntaxfehler, sollte das Feld ais1.KontoNummer$
keine Daten enthalten. Daher sollte man bei der Verwendung von Maskenfeldern
immer einfache Hochkomma verwenden:
select AdressAnrede||' '||AdressVorName ||' '||
Adressname
from Anschriftstamm a join Kundenstamm k on
k.Adressidhauptadr=a.adressid
where Kontonummer=
':ais1.KontoNummer$'
Die Typkonvertierung wird dann automatisch von der
Datenbank vorgenommen.

---

## Maskensteuerung durch die Anwender

Maskensteuerung durch die Anwender
Der Aeins Anwender hat die Möglichkeit Einfluss darauf
zu nehmen, wie eine Maske angezeigt werden soll, z.B. ob es Pflicht Felder gibt
oder ob bestimmte Felder für bestimmte Bedienerklassen nicht angezeigt werden
sollen. Wenn man auf der Maske
Shift+F3
drückt so wird die Maske noch einmal geöffnet und alle im Standard
sichtbaren Felder sind nun Gelb hinterlegt.
Durch Klicken mit der rechten Maustaste kann ein
Kontextmenu mit folgenden Funktionen aufgerufen werden:
•
Feldeigenschaften setzen (z.B. Tabulatorreihenfolge)
•
EPAS
•
Properties anzeigen
•
Tabulatorreihenfolge löschen
•
Feldeigenschaften löschen
•
User Jpl editieren
Mit den ersten drei Punkten wird ausgewählt, was
geschehen soll, wenn man auf ein Feld klickt. Die Funktion ist dann mit einem
Haken versehen. Wenn man nun mit der linken Maustaste in ein Feld klickt wur die
entsprechende Funktion für dieses Feld ausgeführt.
Die letzten beiden Funktionen werden sofort
ausgeführt.
Hinweis:
Diese Funktion (Shift F3) kann für
Anwender weggeschützt werden, indem die Funktion " EPA_FELD_EINSTELLER" über
Zugriffsrechte Funktionen
(Direktsprung
[ZUGF]
) geschützt wird.

---

## Menü

Menü
Das
Aeins-Hauptmenü
stellt
die Bereiche und die Funktionen, die schutztechnisch erlaubt sind, bereit.
Es gibt einen Bereich („Hauptmenü“, siehe
Bedienerstamm Farb-Einrichtung), in dem die Aeins-Bereiche übersichtlich
dargestellt werden, und nach Aktivierung eines Bereiches im sogenannten
Auswahl-Menü die Funktionen übersichtlich in Kategorien dargestellt werden.
Durch diese Aufteilung („2-Klick-Strategie“) ist es
sehr schnell möglich eine bestimmte Funktion zur Ausführung zu bringen.
Weitere Merkmale sind:
•
Präsentation der Systemmeldungen
•
Favoriten sind von den Systemmeldungen optisch getrennt und haben eine
eigene Tab-Seite.
•
Möglichkeit der Einbindung eines Firmenlogos aus dem Archiv
•
Kontextsensitive Menüs, integriertes Schutzsystem
•
Erheblich besseres Tastaturhandling im SHIFT-F4 – Umfeld
•
Bedingt durch die geänderte Präsentation der Bereich eingeschränkte
Farbgebungsmerkmale. Als Ausgleich aber user-individuelle
Style-Möglichkeiten.

---

## Menü-Favoriten-Sortierung

Menü-Favoriten-Sortierung
Administration
Menü
Favoriten-Sortierung
oder Direktsprung
[
FAVO
]
Bietet die Möglichkeit die Favoriten zu sortieren.
Felder
Dialog
      Favoriten-Sortierung
Kurzname
Kurzname des Bedieners
Optionbox
Optionbox die die Favoriten des
      Anwenders verwaltet.
Bedienerid
Technische Identifikation des
      Bedieners
Beschriftung
Beschriftung des
      Favoriten
Sortierung
Anhand dieser Angabe wird die
      Sortierung vorgenommen.
Funktion
Informatorische
      Funktions-Identifikation
Funktionen
Dialog
      Favoriten-Sortierung
Sortierung speichern
[
F9
]
Speichert die
      Sortierung.
Eine
      Aktualisierung im Hauptmenü
findet beim Programm-Neustart
      statt.

---

## Änderung der Lagernummer

Änderung der Lagernummer
Die Änderung der Lagernummer auf dem Beleg bedeutet
lediglich die Änderung der Vorbelegung für nachfolgend erfasste Positionen.
Die Lagernummer kann/muss für jede erfasste Position
nach der Erfassung geändert werden.
Da einige Eigenschaften der Position von der
Lagernummer abhängig sind, gilt es beim Wechsel der Lagernummer einige Fragen zu
beantworten. Um diese nicht bei jedem Wechsel entscheiden zu müssen, gibt es
dafür ein Behandlungsschema, das die Behandlungen der verschiedenen Themen
klärt.

---

## Neuer Drucker mit IP-Adresse

Neuer Drucker mit IP-Adresse
Druckumleitung den in VRGD zugeordneten Drucker 4010
(siehe oben) für Bediener am Kassenterminalserver auf ihren lokalen Drucker:

---

## Oberfläche - Startseite

Oberfläche - Startseite
Auf der Startmaske sind folgende Felder zu sehen:
Felder
Profil
(In
      allen Modi außer
Neu):
Id des
      Profils
Profilname
Hier
      wird der Name des Profils hinterlegt.
Exportformat
Wählen Sie das Format aus, in dem
      die eRechnung exportiert werden soll. Zur Auswahl stehen:
•
UBL
•
ZugFeRD / CII
ab Herbstversion
      2025
Aktiv
Legen Sie fest mit der
      Optionsauswahl
Ja
oder
Nein
, ob dieses Profil aktiviert
      ist.
Bereich
Geben Sie alle Bereiche (Relationen)
      an, welche für die eRechnung befüllt werden können.
Prozedur
Wählen Sie eine Prozedur aus, welche
      die Informationen für den entsprechenden Bereich sammelt.
Im
Ändern
-Modus gibt es zusätzlich die
Funktionen:
Funktionen
Private Prozedur
Von
      der zuletzt markierten Prozedur wird eine private Prozedur erstellt,
      welche ggf. angepasst werden kann.
Falls dort schon eine private
      Prozedur hinterlegt wurde, wird diese zum Bearbeiten geöffnet.
Prozedur testen
Die
      zuletzt markierte Prozedur wird getestet.
Dabei nimmt er die auf dem
      Testreiter hinterlegten
Ids
am
      Ende der Maske und stellt für diese Vorgänge oder Warenbewegungen die
      Ergebnisse dar.
Damit können entweder die Prozeduren oder die
Ids
auf ihre Richtigkeit bzw.
      Vollständigkeit getestet werden.
Rechnung testen
Eine
      komplette eRechnung wird erstellt und anschließend geöffnet.
Dabei ist
      dies allerdings ein Test, somit werden sämtliche nachfolgende Effekte oder
      Informationen rückgängig gemacht.

---

## Optionen

Optionen
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Optionen
F10
Direktsprung
[ECL]
Allgemein
Hier lassen sich bestimmte Einstellungen
vornehmen:
Beschreibung
Test
      nach erfolgreicher Einspielung sofort starten
Soll
      direkt nach dem Einlesen der Datei für die erfolgreich eingespielten
      logischen Dateien der Test gestartet werden (Kontenerkennung und
      automatische Auszifferung F6)?
Datei nach erfolgreicher Einspielung
      umbenennen
Soll
      nach erfolgreicher Einspielung die physikalische Datei umbenannt werden?
      Dies dient zur Sicherheit, um ein doppeltes Einlesen zu verhindern. Die
      Namensvergabe ist fest vorgegeben. Für die Formate *.DTI und MT940 wird
      der neue Name aus der Einspielnummer mit der Erweiterung „.TXT“ gebildet.
      Bei dem Format CAMT.053 wird einfach die Einspielnummer hinten als
      Extension angehängt.
Bei
      fehlender Hausbank Daten nicht einlesen
Sollen bei fehlender Hausbank der
      Kontoauszug nicht eingelesen werden? Wenn mehrere Bankkonten bei der
      Hausbank für verschiedene Mandanten existieren, kann man die nicht zum
      Mandanten gehörenden Kontoauszüge hierüber ausfiltern.
Anfangs- und Endsaldo aus Sicht der
      Bank übernehmen (nur CAMT053)
Beim
      Einspielen der Daten wird der Anfangs- und Endsaldo entweder aus Bank-
      oder aus Kundensicht eingespielt. Der Standard ist „aus Kundensicht“.
      Bestehende Daten werden von dieser Einstellung nicht
      verändert.
GVC-Textersetzung als Belegtext
      übernehmen (MT940 und CAMT053)
Soll
      der Text, der einem Geschäftsvorfallcode (s.u.) zugeordnet ist, als Text
      beim Buchen übernommen werden? Diese Option wird nur ausgewertet, wenn die
      Datei das Format MT940 oder CAMT053 besitzt.
Bei
      11-stelligem Hausbankkonto "Deutsche Bank" Format annehmen
Kontonummern werden im e-Clearing
      normalerweise rechtsbündig auf 10 Stellen formatiert, da in Deutschland i
[...]


---

## OT – openTRANS

OT – openTRANS
Einstellungen für die Verarbeitung für openTRAN.
openTRANS ist ein Datenformat, das es erlaubt
Informationen zu einem Vorgang in einem technischen Standardformat (xml) zu
speichern.
openTRANS aktiv
Gibt an, ob openTRANS-Export aktiv ist. Ist der Kunde
dieses Vorgangs ein openTRANS-Kunde, so wird beim Druck des Dokuments ein Export
gemacht.
Pfad für
Dateiablage
Pfad für die Ablage eines openTRANS-Exports als Datei.
Bei jedem Export wird eine Datei erstellt, die in diesem Pfad abgelegt wird. Der
Dateiname kann von Referenz-ERP oder über eine optionale Prozedur erstellt werden.
Prozedur für
Dateinamen
Hier kann der Name einer Prozedur angegeben werden,
die den Dateinamen für den openTRANS-Export eines Vorgangs bestimmt. Wird kein
Name angegeben, so wird der Dateiname des Exports von Referenz-ERP bestimmt.
create procedure p_otdateiname(in in_v_id
integer)
result ("V_UKlassOTPath" varchar(1000)
)
Profil
für
Export
Hier wird das Profil angegeben das beim
openTRANS-Export verwendet wird. Das Profil können Sie unter dem Direktsprung
[OT] definieren.
OT->EDI-Konverter
Hier kann der Name einer Funktion angegeben werden,
die als Eingabeparameter die Vorgangs-ID und ein XML vom Typ long varchar
bekommt und dieses verändert im gleichen Typ long varchar wieder zurückgibt.
Diese Funktion kann verwendet werden, um nachträglich Informationen in das XML
einzubetten, zu verändern oder zu entfernen, die für den Empfänger über den
Standard hinaus notwendig oder nützlich oder nicht relevant sind.
create function p_otediconvert(in in_v_id integer, in
in_otxml long varchar)
returns  long varchar
ME-Umschlüsselungsprozedur
Hier kann der Name einer privaten Prozedur angegeben
werden, die eine Mengeneinheitsnummer aus Referenz-ERP übergeben bekommt und
eigenständig die dazu gehörige UN-Mengeneinheit und den Umrechnungsfaktor
ermittelt. Der Faktor gibt an, in welchem Verhältnis die Referenz-ERP-Mengeneinheit zu
der UM-Mengeneinheit steht. Werden beispielsweise Referenz-ERP-Tonnen (t)
[...]


---

## Periodenerfolgsauswertung

Periodenerfolgsauswertung
Periodenerfolgsauswertungen gibt es in
unterschiedlichen Sortierungen und Gruppierungen.
Die Erfolgsauswertungen liefern das Betriebsergebnis
für ein Wirtschaftsjahr, das bis zu einer vorgegebenen Periode aufgelaufen ist.
Es bedient sich ausschließlich fakturierter Summen.
Man macht sich schnell klar, dass hinsichtlich der
Umsätze das Ergebnis nur endgültig ist, wenn man ausschließlich abgeschlossene
Buchungsperioden betrachtet. Die Einschätzung des ausgewiesenen Rohgewinns ist
zusätzlich von der gewählten Methode zur Bestandsbewertung abhängig. Die von
Branchen-ERP empfohlenen Methoden (s.o.) stellen sicher, dass sich Betriebsergebnisse
für abgeschlossene Perioden nicht mehr dynamisch ändern können. Das gilt
übrigens auch für den durchschnittlichen Jahreseinkaufspreis, der passend
konstruiert ist und ebenfalls stets den Durchschnitt bis zu einer vorzugebenden
Periode liefert. Im Gegensatz dazu würde das übliche empirische Mittel über alle
Einkäufe eines Wirtschaftsjahres auch Aussagen über den Rohgewinn bereits
abgeschlossener Perioden dynamisch verändern.
Die Aussagekraft des ausgewiesenen Rohgewinns hängt
überdies von weiteren Faktoren ab:
Faktor
Beschreibung
Zeitnah
Je
      nach der gewählten Bewertungsmethode spielt es eine mehr oder weniger
      starke Rolle, ob alle Warenbewegungen gemäß ihrem Lieferdatum erfasst
      werden. Denn nur die Lieferchronologie kann das Maß sein, die Entwicklung
      einer Bestandsbewertung fortzuschreiben. Wichtig in diesem Zusammenhang
      ist auch, dass die dem Lieferdatum entsprechenden Wirtschaftsperioden auch
      bebuchbar sind. Zu späte Periodeneröffnung und zu früher Abschluss (bzw.
      Buchungsschluss) können hinderlich sein. Die Zeitnähe muss sich auch etwa
      in der Erfassung von Frachtrechnungen niederschlagen. Sorgfalt bei der
      Erfassung unterstützt durch entsprechende organisatorische Maßnahmen ist
      also gefragt.
Bewertungsmethode
Welcher Artikel ist mi
[...]


---

## Pfleger Publikationen

Pfleger Publikationen
Felder
Publikation
Name
      der Publikationen
Artikel
Zeigt die in der Publikation
      enthaltenen Artikel.
Partitionsbedingung ( subscribe by
      )
Restriktionsbedingung ( where
      )
Funktionen
Speichern
Speichert die Angaben

---

## Pflege von Basisdaten

Pflege von Basisdaten
Hinweis
Pflegen Sie Ihre Daten korrekt und vollständig!
Beachten Sie, dass unvollständig gepflegte Daten zur
Zurückweisung des Dokumentes von Ihrer Gegenstelle führen können.
In den folgenden Bereichen müssen zur korrekten
Funktionalität des eRechnung-Exports Daten gepflegt werden:
Mandantenstamm
•
Handelsregister
•
Handelsname
•
Electronic Address
•
UStIdnr
Kundenstamm
•
Gegen-Nummer
•
eRechnung-Profile
•
EKS-Nr.
•
Handelsregister
•
Handelsname
Steuerparameter 1153
eRechnung-Profil
•
Daten für den Export
ImportSettings
•
Daten für den Import
Bedienerstamm
•
Telefon
•
Mailadresse
Zahlungsarten
•
Zahlungsweg
Beachten Sie hier insbesondere die Zahlungsart mit
Nummer
0
, die oft für „unbekannt“ steht.
Kundenbank
•
Gültiges
SEPA-Mandat
für Ihren Kunden bei Lastschrift als Zahlungsart.
Dabei muss das Feld Mandatsreferenz gefüllt werden.
Mengeneinheiten
•
ME-Einheitenzuordnung
Steuersätzen
•
Vom Standard abweichende Steuerkategorien (E – Ausnahmen oder Z –
Befreiungen u. ä.)

---

## PPTyp 0: allgemeine Parameter

PPTyp 0: allgemeine
Parameter
Hier gibt es keine spezielle Bedeutung der 3 Werte. Im
allgemeinen wird nur der 1. Wert belegt. Zu Zwecken der Optimierung könnte man
allerdings bis zu 3 Parameter aus einem Datensatz bedienen.

---

## Preislisten pflegen

Preislisten pflegen
Felder
Preislistennummer
Nummer der Preisliste
Bezeichnung
Preislistenbezeichnung
Währung
Währung der Preisliste
Bruttopreis
Gibt
      an, ob es sich um eine Bruttopreisliste handelt
Steuergruppe
Wenn
      Bruttopreisliste eine Steuergruppe, die die zur Berechnung der Preise
      gültigen Steuersätze enthält
Kalkulationsformeln linksseitig
      erlaubt, auch bei gesetzter Korrektursperre
‚Ja‘
      in diesem Feld ermöglicht eine Kalkulation dieser Preisliste. Bei
      gesetzter Korrektursperre bedeutet das, dass der Preis per Formel
      berechnet und dadurch ggf. geändert, manuell jedoch nicht verändert werden
      kann.
Sortierung (Kalkulation)
Dieser Wert bestimmt die Reihenfolge
      der Preise auf der Kalkulationsmaske. Dabei werden Preise zu Preislisten
      mit Sortierung= 0.00 nicht berücksichtigt.
Rundungseinheiten
Hier
      wird angegeben wie ein kalkulierter Wert nach Auswertung einer Formel zu
      runden ist. Es wird dabei kaufmännisch gerundet.

---

## Privateinrichtungen

Privateinrichtungen
Es werden die Daten in folgenden Tabellen
gelöscht:
SQL_Text unter der Bedingung: where SQL_TextBesitzer =
1
AnwendVariante unter der Bedingung: where
AnwVarBesitzer = 1
AnwendCondition unter der Bedingung: where
AnwCondBesitzer = 1
Optionbox unter der Bedingung: where AnwFunkId in
(select AnwFunkId from AnwendFunktion where AnwFunkBesitzer = 1 and
isnull(AnwRptId,'') = '')
AnwendFunktion unter der Bedingung: where
AnwFunkBesitzer = 1 and isnull(AnwRptId,'') = ''
AnwendCondition unter der Bedingung: where
AnwCondBesitzer = 1 and AnwCondId in (select AnwCondId from AnwendReport where
AnwRptBesitzer=1)
AnwendReport unter der Bedingung: where AnwRptBesitzer
= 1
Optionbox unter der Bedingung: where AnwFunkId in
(select AnwFunkId from AnwendFunktion where AnwFunkBesitzer = 1 and
isnull(AnwRptId,'') != '')
AnwendFunktion unter der Bedingung: where
AnwFunkBesitzer = 1 and isnull(AnwRptId,'') != ''
SQL_Text unter der Bedingung: where SQL_TextBesitzer
in (12,13,14)
UserFelder
QReportDefine unter der Bedingung: where QRNummer <
1000

---

## Programmstrukturen anpassen.

Programmstrukturen anpassen.
Der erste Abschnitt entpackt die Sybase 17 Programme
und läd die neue Umgebung in den Referenz-ERP Bereich, passt die Servicestrukturen an
und erweitert die ODBC Schnittstelle um den SQL Anywhere 17 Bereich.

---

## Protokollstruktur

Protokollstruktur
Die Protokollstruktur ist abhängig von der Art wie sie
gespeichert wird. Zurzeit gibt es nur die Auswahl von XML-Struktur und keine
XML-Struktur. Um zu erkennen ob es sich um eine XML-Struktur handelt, enthält
die Spalte „protoXML“ der Tabelle Protokoll den Wert „1“.
XML-Struktur
Keine
XML-Struktur
XML-Struktur
Bei der XML-Struktur werden die protokollierten Daten
in einer XML-Struktur gespeichert. Dadurch kann man später gezielter auf die
Daten zugreifen.
Beispiel:
<?xml version="1.0"
encoding="iso-8859-1" ?>
<root>
<mode>UPDATE</mode>
<Felder>
<Field id="KtrId"
label="Ident">
<alt>473543</alt>
<neu>473543</neu>
</Field>
<Field id="KtrAbDatum" label="Ab
Datum">
<alt>12-04-2010</alt>
<neu>12-04-2010</neu>
</Field>
<Field id="KtrBisDatum"
label="Bis Datum">
<alt>22-04-2010</alt>
<neu>22-04-2010</neu>
</Field>
<Field id="KtrBisDatumFix"
label="Bis Datum (max)">
<alt>22-04-2010</alt>
<neu>22-04-2010</neu>
</Field>
<Field id="KtrDatum"
label="Datum">
<alt>12-04-2010</alt>
<neu>12-04-2010</neu>
</Field>
<Field id="KtrErlediStatus"
label="Erledigungsstatus">
<alt>0</alt>
<neu>0</neu>
</Field>
<Field id="KtrNummer"
label="Nummer">
<alt>24332</alt>
<neu>24332</neu>
</Field>
<Field id="KtrStornoStatus"
label="Stornostatus">
<alt>0</alt>
<neu>0</neu>
</Field>
<Field id="WaehrNummer"
label="Währungsnummer">
<alt>20</alt>
<neu>20</neu>
</Field>
</Felder>
</root>
Erklärung der XML-Tags
XML-Tag
Bedeutung
<root>
Dieser Tag kennzeichnet nur den
      Start der XML-Struktur.
<mode>
Der
      „Mode“ sagt aus, wodurch die Daten entstanden sind. In dem Beispiel sind
      die Daten durch ein „Update“ entstanden.
<Felder>
Dies
      ist der Start-Tag unter dem sich alle mitprotokollierten Felder
      befinden.
<Field>
Der
      „Field“ Tag ist ein Tag für eine einzelne Spalte. Innerhalb des Tags
      existieren noch der „id“ und „label“ Parameter.
ID = Der Spaltenname aus der
      Tabelle.
LABEL = Die Bezeichnung die in dem
      Stammdaten
[...]


---

## Publikationen verwalten

Publikationen verwalten
Sie können über Sybase Central neue Publikationen
anlegen, aber auch die Artikel einer Publikation bearbeiten
1.
Starten Sie Sybase Central unter: ..\Aeins\bin64\scjview.exe
2.
Verbinden Sie sich mit der gewünschten Datenbank
3.
Klicken Sie nun auf der Registerkarte „Inhalt“ oder in der Ordnerübersicht auf
Publikationen
Eine neue Publikation anlegen:
1.
Klicken Sie auf einer freien Stelle der Registerkarte „Publikationen“ mit der
RECHTEN Maustaste und wählen Neu
à
Publikation
2.
Folgen Sie den Anweisungen des Assistenten zum Erstellen von Publikationen
Einen Artikel zu einer Publikation hinzufügen:
1.
Wählen Sie die gewünschte Publikation
in der Ordneransicht
, die Sie
ändern möchten
2.
Klicken Sie diese dort mit der RECHTEN Maustaste an und wählen Neu
à
Artikel
3.
Folgen Sie den Anweisungen des Assistenten zum Erstellen von Artikeln
Einen Artikel bearbeiten:
1.
Markieren Sie die gewünschte Publikation
in der Ordneransicht
, die Sie
ändern möchten
2.
Zum Bearbeiten wählen Sie den gewünschten Artikel auf der Registerkarte Artikel
aus und klicken diesen mit der RECHTEN Maustaste an
3.
Klicken Sie nun auf Eigenschaften
4.
In dem Fenster lassen sich die Eigenschaften des Artikels in dieser Publikation
ändern
Einen Artikel entfernen:
1.
Markieren Sie die gewünschte Publikation
in der Ordneransicht
, die Sie
ändern möchten
2.
Zum Bearbeiten wählen Sie den gewünschten Artikel auf der Registerkarte Artikel
aus und klicken diesen mit der RECHTEN Maustaste an
3.
Klicken Sie nun auf „löschen“ und bestätigen Sie den Löschvorgang

---

## Replikation defekt! Was nun?

Replikation defekt! Was nun?
In ALLEN Fällen kann man zunächst folgende Schritte in
dieser Reihenfolge vornehmen, um ein Problem mit der Replikation zu
ermitteln:
1.
Jede Replikation legt LOG-Dateien im Ordner „dbrexp“ an. Diese Log-Dateien
tragen hier nach Anleitung den Namen des Publishers für die Datenbank die
Repliziert werden soll. Diese Log-Datei öffnen und ans Ende scrollen. Hier wird
dokumentiert, was zuletzt vom DBRemote gemeldet wurde!
2.
Sofern Zugriff auf Aeins möglich, hier den Direktsprung
RINFO
verwenden um Informationen zur
Replikation und den angeschlossenen DBRemote-Usern zu erhalten.
3.
Prüfen Sie unter Dienste den Status den Dienst des DatenbankServers und den
Status des DBRemote-Dienstes. Starten Sie diese Dienste ggf. neu.
4.
Prüfen Sie, wenn verwendet das Event „dbrexp-schedule“
Wird festgestellt, dass die Replikation bereits
dermassen defekt ist, zum Beispiel infolge eines versäumten Updates der
Filialdatenbank, so hilft meist nur ein Neueinrichten der defekten Seite.
Führen Sie zunächst ein Extrakt auf Seiten der
korrekten Datenbank durch:
1.
Starten Sie scjview.exe und verbinden sich mit der Datenbank
2.
Suchen Sie den Eintrag „SQL Remote-Benutzer“
3.
Klicken Sie mit der rechten Maustaste den dort in der Liste geführten
Remote-User an und klicken auf „Datenbank extrahieren“
4.
Beim Extrakt sollen Struktur und Daten mitgenommen werden
5.
Verwenden sie die reload.sql Option zum späteren leichteren Einspielen
6.
Nach Abschluss des Extraktes müssen diese Daten auf die defekte Seite geschafft
und dort wieder eingespielt werden.
7.
Um Fehler beim Einspielen zu vermeiden muss:
7.1
die Pfadangaben im reload.sql entsprechend den örtlichen Strukturen angepasst
werden
7.2
Die Tabellen, welche durch das reload.sql Skript erstellt werden sollen, müssen
entfernt werden
8.
Nach dem Start des Skripts verfolgen Sie die Arbeitsschritte und bewerten und
reagieren Sie entsprechend auf die gezeigt
[...]


---

## Report Oberkonten

Report Oberkonten
Mit dem Report Oberkonten kann man sich die
gewünschten Kontonummern mit Oberkonto, Matchcode, der Bezeichnung und der
prozentualen Verteilung auf Konten ausdrucken.
Über den Auswahlbereich
F2
(siehe auch
Generelle Programmbedienung
) kann man
die Datenmenge mit Hilfe der Angabe von Kontonummer und/oder Oberkonto nach
Wunsch begrenzen.
Das Aussehen des Reports kann man über die Funktion
CRW-Optionen
Shift+F11
etwas variieren. Da gibt es
Einstellmöglichkeiten für z.B. das Anzeigen des Firmenlogos oder dem grau
Hinterlegen jeder zweiten Zeile.
Alle verfügbaren Einstellungen findet man
unter
Crystal Report Optionen
.

---

## RFS Schnittstelle

RFS Schnittstelle
Bei der Realisierung der RFS-Schnittstelle im
Aeins-System wurde besonders viel Wert darauf gelegt, das Original ( bestehende
RFS-Schnittstelle im XCOM Paket) ohne Änderungen der inhaltlichen Abläufe
abzubilden. Im Hinblick auf eine externe Überprüfung erleichtert diese
Vorgehensweise den Vergleich beider Systeme.
Deutliche Unterschiede zeigen sich jedoch in der
optischen Aufbereitung der Bedienelemente  dieser Schnittstelle.
Zusätzlich  zur allgemeinen Einrichtung  ( Direktsprung RFSV = RFS
Voreinstellungen) wurden  Teile der Einrichtungsdaten in bestehenden
Pflegemodulen integriert.
Dieses Handbuch gibt Auskunft über:
Einrichtung der Schnittstelle
Organisatorische  Abläufe
Abweichende Optionen

---

## Skriptparameter

Skriptparameter
Eine Liste der aktuellen Einstellungen der
Scriptparameter lässt sich über den Direktsprung [SCPA] und die Funktion
Script-Parameter (DRUCK) als Crystal-Reports-Liste ausdrucken. Im Auswahlbereich
sollte man die Id der gewünschten Waagen-Schnittstelle (normalerweise
„WaagenImport“) abgrenzen. Für den Typ ist 0 bis 2 einzustellen.
Die Parameter der Waage haben folgende Funktion (Die
Liste ist nach Typ und ScriptPPId sortiert):
ScriptPPId
Beschreibung, Hinweise
Wert1
Wert2
Wert3
Typ
ART_AUS_SORT1 ..
      ART_AUS_SORT4
Für
      jede von 4 Satzarten kann unabhängig eingestellt werden:
1:
      Artikel wird über Konvertierungstabelle aus den Sortennummern ermittelt;
      zieht stärker als die ggf. gelesene Artikelnummer.
0:
      Artikelnummer wird ausschließlich aus Datei gelesen.
Defaultwert ist 0. Siehe Parameter
      SORTART%.
Darf
      nicht auf 1 gesetzt werden wenn SORT_AUS_ART auch auf 1 steht.
In
      diesem Zusammenhang werden folgende Parameter benötigt: SORTART01 ...,
      ART_DEFAULT
Belegt
Unbenutzt
Unbenutzt
0
ART_DEFAULT
Default-Artikelnummer bei
      Konvertierung Artikel aus Sortennummer.
In
      diesem Zusammenhang werden folgende Parameter benötigt ART_AUS_SORT1 bis
      ART_AUS_SORT4 und SORTART01 ...
Belegt
Unbenutzt
Unbenutzt
0
BELART_DEFAULT
Bei
      Verwendung von Vorgangsdaten außerhalb der Rohware wird hier die Default
      Belegart in Form der Vorgangsklasse angegeben. Ist dieser Parameter nicht
      aktiv, so wird 1600 (Eingangslieferschein) eingestellt.
Belegt
Unbenutzt
Unbenutzt
0
BELARTKZ_EGU
Kennzeichen, an dem man folgende
      Vorgangsklasse erkennt: Eingangsgutschrift.
Dieser Parameter wird nur bei
      Zielansprache FAKTURA benötigt.
Belegt
Unbenutzt
Unbenutzt
0
BELARTKZ_EGUS
Kennzeichen, an dem man folgende
      Vorgangsklasse erkennt: Storno Eingangsgutschrift. Dieser Parameter wird
      nur bei Zielansprache FAKTURA benötigt.
Belegt
Unbenutzt
Unbenutzt
0
BELARTKZ_ELI
Kennzeic
[...]


---

## SLEEP

SLEEP
Syntax
SLEEP [RANDOM] nnnn;
Purpose
Wartet nnnn Milisekunden, bevor das nächste Statement
ausgeführt wird.
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Beschreibung
Dieses Kommando wartet lediglich einige Milisekunden,
bis dass nächste Statement ausgeführt wird. Entweder gibt man direkt an, wie
viele Milisekunden es sein sollen oder zusätzlich noch das Schlüsselwort RANDOM.
Dann wird eine Zufallszahl erzeugt, die mit der angebebenen zahl multipliziert
wird. Dies ist nützlich, wenn man automatische Tests in Mehrbenutzerumgebungen
durchführen will und eine asynchrone Verarbeitung erreichen will.
Beispiel
SLEEP 1000 // Wartet 1 Sekunde

---

## Sonderberechnung

Sonderberechnung
Ist für den heutigen Tag die Position noch nicht
berechnet worden, so kann mit der Funktion:
die tagesaktuelle Position berechnet werden.

---

## SQL-Variablen in der Auswahlliste verwenden

SQL-Variablen in der Auswahlliste
verwenden
Wenn in der Auswahlliste Spalten fehlen, ist es nicht
unbedingt notwendig, eine private Ableitung der Auswahlliste zu bilden. Man kann
sich eigene SQL-Variablen erstellen, die dann wie ein Subselect in das
SQL-Statement eingefügt werden. Wenn man den Reiter SQL-Variablen das erste Mal
aufruft, sieht man nur eine Liste, in der in der ersten Zeile „(Neu)“ steht.
Klick man in diese Zeile, so öffnet sich eine weitere Maske, in der dann die
notwendigen Informationen angeben werden kann:
Bedeutung
Überschrift
Die
      Überschrift, die über der neuen Spalte erscheinen soll.
Typ
Der
      Typ des Feldes, wie er auch in der FIELD-Anweisung verwendet wird. Eine
      Auswahl der möglichen Typen ist mit F3 möglich. Hier können sowohl
      Basistypen als auch FS-Formate ausgewählt werden.
FS-Format
Wenn
      man als Typen FS ausgewählt hat, kann man hier ein Format angeben. Eine
      Auswahl des FS-Formats ist mit F3 möglich.
Aktiv
Wenn
      man ein Subselect momentan nicht ausführen möchte, aber die Arbeit, die
      man in die Formulierung gesteckt hat, nicht über den Haufen werden will,
      so kann man hier die SQL-Variable einfach deaktivieren. Sie wird dann
      komplett ignoriert.
Herkunft
Dies
      ist nur ein Anzeigefeld und kann vom Anwender nicht direkt beeinflusst
      werden. Es hat folgernde Ausprägungen:
•
Anwender: Dies
      ist die Standardeinstellung, wenn die Variable über den Gestaltungsdialog
      angelegt wurde.
•
Steuerparameter:
      Der Steuerparameter „Reklamationsmaßnahmen“ (SPA 1040) nutzt IBVariablen
      um verwendete Spalten automatisch der Anwendung „Reklamationen“
      hinzuzufügen. Diese können zwar hier bearbeitet aber nicht gelöscht
      werden.
SQL-Ausdruck
Der
      SQL-Befehl, der in die Auswahlliste eingebaut werden soll. Hier kann man
      auf alle Felder zugreifen, die auch in dem SQL-Statement stehen. Nur wenn
      hier etwas eingetragen wurde, ers
[...]


---

## Status

Status
Zahlungen, die noch nicht in einem DTA-Lauf
verarbeitet wurden, gelten als ungebucht, andernfalls als gebucht. Die Daten der
RFS –Schnittstelle werden also nicht gelöscht – sie stehen daher zu Kontroll-
oder Abstimmzwecken jederzeit zur Verfügung !

---

## Starten von Events

Starten von
Events
Sie können den ausgewählten Event auch außerhalb der
von Ihnen festgelegten Bedingungen und Zeitpläne einmalig manuell starten. Dazu
verwenden Sie die Funktion “Starten”.  Sie müssen nun nur noch die
Sicherheitsabfrage bestätigen, um das Event sofort manuell zu starten.

---

## Summe im SQL-Text

Summe im SQL-Text
Damit die Summe über eine Spalte gebildet wird, muss
man das Schlüsselwort SUM in die Fieldanweisung schreiben:
FIELD Betrag,ZahlVorBetrag,N2,20,
SUM
Es wird dann dieses Feld aufsummiert und sowohl im
Tiptext, als auch in der unteren Tabelle neben den Auswahlbedingungen,
dargestellt.
Man kann aber auch Formeln angeben
FIELD
Betrag,ZahlVorBetrag,N2,20,
SUM=(ZahlVorBetrag*(3-Zahlvorsollhaben*2))
Die Syntax der Formeln entspricht der SQL-Syntax.
Soll das Format vom Format der aktuellen Spalte
Abweichen, so kann man noch zusätzlich mit dem Schlüsselwort SUMFORMAT ein
abweichendes Format angeben.
FIELD
Betrag,ZahlVorBetrag,N2,20,SUM=(ZahlVorBetrag*(3-Zahlvorsollhaben*2)),
SUMFORMAT=S2

---

## Sybase 17

Sybase 17
Die Umstellung auf Sybase 17 wird im Abschnitt
Systeminformationen (SYSIN) auf der Tab-Karte Datenbanken vorgenommen.
Der Bereich gliedert sich in
-
Programme und Schnittstellen anpassen
-
Datenbanken auf Umstellungslevel bringen und ggf. Überprüfen
-
Datenbank umstellen

---

## Systemmeldungen

Systemmeldungen
Es wird empfohlen die
Systemmeldung
AMIC_WARNUNG_AEINSFEHLP
zu aktivieren.
Mit Hilfe von
Protokollkontrolle
können Sie festlegen welcher Bediener über die Systemmeldung benachrichtigt
werden soll.

---

## Systemmeldungspfleger

Systemmeldungspfleger
Felder
Name
Eindeutiger technischer Name der
      Systemmeldung.
Aktiv
Ja/Nein
Bestimmt, ob die Systemmeldung
      überhaupt aktiv sein soll, d.h. ob die Bedingungen für eine Anzeige beim
      Programmstart überhaupt geprüft werden sollen.
Desktop
Bestimmt, ob die Systemmeldung
      zusätzlich als Benachrichtigung auf dem Windows-Desktop dargestellt werden
      soll.
Funktion
Die
      Funktion, die ausgeführt werden soll wenn ein User die Systemmeldung
      klickt.
Sie
      können hier private Funktionen anbinden.
Beschriftung
Die
      explizite Beschriftung der Systemmeldung.
Hinweis: Es handelt sich hierbei
      nicht um die Beschriftung der Funktion.
Sortierung
Kriterium für die Reihenfolge der
      Abarbeitung der Systemmeldungen.
Statement
Auf
      Basis dieses Statements wird entschieden, ob eine Systemmeldung
      durchgeführt werden soll oder nicht.
Das
      Statement ist so zu formulieren, dass der Ziel-Alias „wert“ heißt.
Dann
      entscheidet der Wert:
1
      bedeutet Systemmeldung anzeigen.
0
      bedeutet keine Systemmeldung anzeigen.
Exklusiv-User
Gemäß Rollenkontext kann es
      Bedienerklassen geben, denen die Systemmeldung vorlegt wird.
      (Rolle)
Durch Angabe eines Kurznamens lässt
      sich die Systemmeldung weiter einschränken. (Es kann auch durch
      komma-getrennte Liste von Kurznamen angegeben werden)
Hinweis zur internen Statement-Verarbeitung:
Das angegebene Statement wird ausgeführt. Führt die
Ausführung nicht auf einen Fehler, dann wird die Rückgabe ausgewertet. Wie
dokumentiert führt das Ergebnis 0 dazu, das keine Systemmeldung angezeigt
wird.
Alle anderen Rückgaben führen zur Ausgabe der Systemmeldung, auch der
Umstand das eine Ausführung zum Prüfungszeitpunkt technische Probleme
hatte.
Beispiel hierfür kann sein, dass Ressourcen durch andere Prozesse zum
Zeitpunkt der Prüfung blockiert waren.

---

## Systemmeldungs-Vorlage-Pfleger

Systemmeldungs-Vorlage-Pfleger
Felder
Name
Eindeutiger technischer Name der
      Systemmeldung.
Aktiv
Ja/Nein
Bestimmt, ob die Systemmeldung
      überhaupt aktiv sein soll, d.h. ob die Bedingungen für eine Anzeige beim
      Programmstart überhaupt geprüft werden sollen.
Funktion
Die
      Funktion, die ausgeführt werden soll, wenn ein User die Systemmeldung
      klickt.
Sie
      können hier private Funktionen anbinden.
Beschriftung
Die
      explizite Beschriftung der Systemmeldung.
Hinweis: Es handelt sich hierbei
      nicht um die Beschriftung der Funktion.
Statement
Auf
      Basis dieses Statements wird entschieden, ob eine Systemmeldung
      durchgeführt werden soll oder nicht.
Das
      Statement ist so zu formulieren, dass der Ziel-Alias „wert“ heißt.
Dann
      entscheidet der Wert:
1
      bedeutet Systemmeldung anzeigen.
0
      bedeutet keinen Systemmeldung anzeigen.
Typ
SQL
      (Standard)
JPP
      ist möglich, aber nicht allgemein!

---

## Tabelle zur Version: 8.3.2302.17

Tabelle zur Version: 8.3.2302.17
ID
Releasenote - Titel
Geprüft
33294
DSGVO
33334
FehlProtBereich erweitert
33413
Einrichtungshilfe: Benutzerformate
33426
Auswahlliste: Tastatursteuerung
33399
Belegfluss
33290
eClearing
33291
Geschäftsjahr/Fibuperioden
33471
Elsterpatch: Report
33347
PIV-Belege Partien
33410
Kassensystem: Tse-Meldung bei Kasseneröffnung
33463
Druck Tse-QR-Code
33217
Kontrakt
33354
Kunden Kreditvergabe
33425
Bankleitzahlen aktualisieren
33327
Teildisposition: Button an Berechtigung
angepasst
33343
Frachttabellenzuordnung Felderweiterung
33367
Druck EPC-QR-Code
33382
Lagerumbuchung: Tastensteuerung

---

## Tabelle zur Version: 9.0.2401.1

Tabelle zur Version: 9.0.2401.1
ID
Releasenote - Titel
Geprüft
34636
Excelimport von xls-Dateien
34136
Systemmeldungen modernisiert
34197
Auswahlliste 2.0 Spalten fixieren
34234
Bereichsauswahl mit Häkchentechnik
34235
Tausendertrennzeichen bei Zahlungsbedingungen
34299
AIS: Dashboards
34423
Compliance
34445
Excel-Export über AW2.0
34477
Nummernkreisgültigkeiten
34675
Masken mit Ribboncontrol
34739
Auswahlliste: Ansichten
34740
Auswahlliste: Eigene Schaltfläche für die
    Ansichten
34741
F3-Auswahl 2.0 (Itembox)
34889
Steuerparameter 791 umbenannt
34186
Archiv-Import über Mandantenserver
34187
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34250
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34463
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34621
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34729
Excelimport [EXCELI]: Import an Offsetposition
34770
C#-Makro: Fehlerbereinigung
34547
Elster Version für 2024
34652
Zinsabrechnung drucken
34861
Zinsabrechnung drucken
34131
Anzeige Inventuraufnahme
34222
Bewertungspreise für Artikel mit Bewertungsgruppe
    0
34949
Direktsprung [TSE] zu TSE Pflegen eingebaut
32861
Kontraktbewegung zu Aufträgen und Bestellungen mit
      Belegnummer
33582
Nachhaltigkeitsvorbelegung
34757
Artikelstamm THG-Werte wurden ausgebaut. Im
      Artikelstamm kann ein Artikel für Einkauf und Verkauf künstlich als nicht
      nachhaltig vorbelegt werden.
34758
Nachhaltigkeit: Anbauländer
34532
Excel-Import: Excelimport aktualisieren
34535
Nummernkreise mit Gültigkeit
34672
Rechnungsempfänger und Zahlungspflichtiger bei
      Musterkunden
34716
Postleitzahlen auf 11 Stellen erweitert
34891
Veränderung bei Artikel Ein- und Verkaufssperre
34180
Streckendisposition - Funktion "Position
    kopieren"
34181
Streckenerfassungsprofil Kopiervorlagen
32321
Mengeneinheit und Gebinde bei individuellen
      Artikelnummern
33584
Anzeigen von Barvorgängen
34047
Artikelbestand Fremdware
34073
Vorgangserfassung: Unerwartete Scrollbalken
[...]


---

## Tabelle zur Version: 9.0.2401.2

Tabelle zur Version: 9.0.2401.2
ID
Releasenote - Titel
Geprüft
34919
Veraltete DTA-Formate IN SPA [521] deaktiviert
35039
SQL-Meldung bei individuellem Kreditlimit
35113
VKA Anzeige von alphanumerischen Belegnummern
35013
eClearing CAMT 53 Format
35082
eClearing CAMT 53 Format
34733
Maintenance
35007
MDE: Nachkommazahlen
35008
MDE: Fokus auf Eingabefeld
34788
Versandprofilstamm Speicherproblem beseitigt
34999
Kundentypänderung
35000
Artikel F3-Auswahl auf Warenposition optimiert
35147
Warenpositionsmaske Cursor Fokus
35015
Fehlerbereinigung Ermittlung der
Bewertungspreise

---

## Tabelle zur Version: 9.0.2502.7

Tabelle zur Version: 9.0.2502.7
ID
Releasenote - Titel
Geprüft
38271
Dokumentenverwaltung - Hinzufügen von Dokumenten über
      [F8] Neu
38282
Dokumentenverwaltung: Vorschau von
    Word-Dokumenten
38284
Dokumentenverwaltung: Vorschau von Excel-Dateien
38449
eClearing Fremdwährung
38055
KOKORE-Druck - fälliger Saldo nach Datenlöschung
38331
Elster Version 43.2.6
38403
Auszifferung mit Skonto aufteilen
38462
Aus [OPV] die Konteninformation [KOI] aufrufen
38345
Kassensturz-Beleg
37674
Kontraktvariante in Kontraktstammdaten
38497
Bewegungen in der Kontraktübersicht
38225
Versandanschriften über Anschrift [ANSCH]
löschen
38303
Zinsabrechnung bei Verwendung von Datenlöschung

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

## Tabelle zur Version: 9.0.2502.9

Tabelle zur Version: 9.0.2502.9
ID
Releasenote - Titel
Geprüft
34996
Es können mehr AIS-Einrichtungen gleichzeitig genutzt
      werden.
38591
Statusmeldung in OSQL
38799
Eclearing CAMT053
38709
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
39717
Periodische Buchungen Valutatdatum
39170
Intrastat: Ursprungsland
39397
TAR-Export ist nun auch nach Ablauf des
      TSE-Zertifikates
39519
Fehler bei Fibu-Übertrag von Barverkaufsbelegen mit
      Gruppenrabatt
38820
Kontraktvariante [KTVA] Vorbelegung
38735
Fehler in Massebilanz. Falsche Mengen werden in
      Bewegungsübersicht angezeigt
38898
Fehler in Variante Preiskalkulation Protokoll bei
      Dokument anzeigen behoben
39135
Druckerstamm Löschen
39329
E-Mail Adressen in den Anschriften
38897
Lagerwechsel in der Online Waage
39211
Änderung einer Anschrift

---

## Tankkartenverwaltung

Tankkartenverwaltung
Soll die Waagenschnittstelle als
Tankstellenschnittstelle fungieren, so wird i. d. R. anstelle einer Kundennummer
die Kartennummer der Tankkarte übergeben. Kundenseitig sind alle ausgegebenen
Tankkarten die
Auswahlliste Kunden / Variante Kunden mit Tankkarte
zu
erfassen. Dieses Verfahren kann auch für eine beliebige andere Umschlüsselung
der Kundennummer eingesetzt werden.

---

## Umschlüsselungen Excel zu Aeins

Umschlüsselungen Excel zu Aeins
Excel-Datentyp
Aeins-Relationstyp
Aeins-FIELD-Typ
Auswahllisten-Cast (siehe
      *)
String
long
      varchar
char,30
cast
      a char(255)
Double
double
N4,12
Datetime
date
D4,16
Decimal
numeric(15,4)
N4,12
Integer
Shortint o. integer
I2,
      I4, FS_xxxxx
**
Zu (*):
Die Anzeige von String-Feldern ist in der Auswahlliste
auf 255 Zeichen beschränkt, die Suche erfolgt aber in der kompletten Information
der Datenbank-Spalte.
(**)
Boolsche Felder müssen im Zahlenformat 0 (FALSE) oder
1 (TRUE) vorliegen. Eine Konvertierung eines Texts wie „true“ oder „false“ in
ein boolsches Feld ist NICHT möglich. Die Darstellung in Referenz-ERP erfolgt über
FS-Formate

---

## Update/Fehlerbehebung der TSE (+TSE Maintenance Tool)

Update/Fehlerbehebung der TSE (+TSE Maintenance Tool)
Voraussetzungen:
•
Das
TSE Maintenance Tool
•
Die Admin-PIN.
(Einzusehen im TSE-Pfleger
unter Tab:
Zugang USB ->
Feld:
Admin Pin
).
•
TSE ist
lokal
am USB-Slot des PCs mit dem TSE Maintenance Tool
eingesteckt (ein Update über
Netuse
bzw.
Netzwerklaufwerk
ist
nicht möglich!).
TSE Maintenance Tool:
1.
Das Maintenance-Tool unter:
https://www.swissbit.com/tse/maintenanceTool/setup.exe
herunterladen.
Tipp!
Im TSE-Maintenance-Tool gibt es unter der Funktion
Help -> Documentation
eine
Anleitung zum Update der TSE.
In dieser Anleitung sind ebenfalls Hilfestellungen zur
Fehlerbehebung der TSE.
Um das Update durchzuführen, wie folgt vorgehen:
2.
Wenn der PC das die TSE als Speichermedium erkannt hat, den Laufwerksbuchstaben
(in diesem Beispiel Laufwerk
D
) merken.
3.
Das TSE Maintenance Tool starten
4.
Den jeweiligen Laufwerksbuchstaben eintragen.
5.
Die Funktion
Check TSE
ausführen.
4.
Falls für die TSE ein Update vorhanden ist, kommt folgende Meldung (diese mit
Ja
bestätigen):
Nach der Bestätigung fragt
das Tool nach der Admin Pin.
5.
Die Pin in das Feld eintragen und mit
Weiter
bestätigen. (Dieser Vorgang kann
mehrere Minuten dauern!)
Nachdem der Vorgang
abgeschlossen ist, erscheint folgende Meldung:
è
Damit ist die TSE erfolgreich
geupdatet.
6.
TSE Maintenance Tool nach dem Update beenden!
TSE-Fehlercodes:
Fehlerbehebung:
1.
Sobald ein Fehler auftritt, einen Selbsttest der TSE durchführen:
Zu
Hauptmenü: Barverkauf -> Kassensicherungsverordnung Einrichtung -> TSE
Pflegen (
F10
) -> Datensatz
auswählen -> Funktion:
Selbsttest
… (
F10
) navigieren.
2.
Alle Verbindungen prüfen (sowohl USB-Slot als auch Netzwerkkomponenten /
Stabilität / Qualität).
3.
Falls weiterhin Fehler auftreten, das TSE-Maintenance-Tool benutzen.
4.
Falls auch danach immer noch Fehler auftreten, den Branchen-ERP-Support
kontaktieren.
Fehlercode
Beschreibung
0
Kein
      Error
1
Falscher Parameter
2
Keine TSE
[...]


---

## User Jpl editieren

User Jpl editieren
Hier können private JPL Validierungsfunktionen
erstellt und bearbeitet werden.

---

## Variante Übersicht Adressen

Variante Übersicht Adressen
Felder
Nr.
Filialnummer des
      Publishers
Sender
Filial-Bezeichnung des
      Publishers
an
Filialnummer des Senders
Remote
Filial-Bezeichnung des
      Senders
Type
Übertragungsart
RemoteAdr
Adresse
Remote Agent
File-Empf.
Funktionen
keine
Bereiche/Profile
Filialnummer
Ermöglicht Bereichssuche nach
      Filialnummern
-
von
-
bis

---

## Variante Benutzerhinweis

Variante Benutzerhinweis
Diese Variante kann mit dem Direktsprung
[FEHLH]
direkt aufgerufen werden.
Im Unterschied zu den anderen Varianten werden hier
nur unerledigte Meldungen vom Typ 101 (Benutzerhinweis), 102 (Benutzerwarnung),
103 (Benutzerfehler) berücksichtigt, welche dem aktuellen User oder seiner
Benutzerklasse zugeordnet sind.
Es steht nur die Funktionalität „Ändern“ zur
Verfügung, welche genutzt werden soll, um die offenen Punkte auf erledigt zu
setzen. Ein Kommentar zum Erledigen ist immer anzugeben.
Diese Einträge ins Fehlerprotokoll werden nicht vom
System geschrieben, sondern können nur vom Anwender eingetragen werden. Dies ist
gedacht, um Arbeitsregeln in Funktionen abzuprüfen und anschließend mit Hilfe
von „
WARNINGFUNCTION
“ zu visualisieren.
Sieht der Mitarbeiter also ein solches Warnsymbol auf seinem Bildschirm, kann er
direkt in diese Variante springen und alle Meldungen abarbeiten, welche ihm
zugewiesen sind.

---

## Variante Übersicht Publikationen

Variante Übersicht Publikationen
Felder
Nr.
Filialnummer des
      Publishers
Sender
Filial-Bezeichnung des
      Publishers
an
Filialnummer des Senders
Remote
Filial-Bezeichnung des
      Senders
Publikation
Teilmenge
Funktionen
keine
Bereiche/Profile
Filialnummer
Ermöglicht Bereichssuche nach
      Filialnummern
-
von
-
bis

---

## Varianten

Varianten
Es gibt in diesem Bereich vier Varianten.
Varianten
Name
Bedeutung
Variante 1
Mehrmandant Einstamm
Einstellungen für den Server
      und Empfänger/Alt
Variante 2
Mehrmandant Transfer
Einstellungen für die
      angebundenen Relationen
Variante 3
XML
      Transfertabelle
Inhalt der Proxytabelle
Variante 4
Server
Einrichtung und Löschung der
      Server

---

## Variante Systemhinweise

Variante
Systemhinweise
Felder
Wann
Zeitpunkt des
      Systemhinweises
Version
Die
      Aeins-Versionsnummer zum Zeitpunkt des Systemhinweises.
Bereich
Klassifizierung seitens des
      Programmes, in welchem Bereich der Hinweis erzeugt wurde.
Anzahl
Die
      Anzahl der unerledigten Vorkommen des Systemhinweises.
Steuerparameter 868  -
      „Fehlerprotokolloptimierung aktiv?“
steuert hier, ob bei erneutem
      Auftreten eines bis dato unerledigten Systemhinweises diese Anzahl erhöht
      oder ein „neuer“ Systemhinweis generiert werden soll.
Typ
Die
      auch „Fehlerstufe“ genannte Kategorisierung eines Eintrags.
30 =
      schwerer Fehler
20 =
      Fehler
10 =
      Warnung
1 =
      Testlauf
0 =
      Ereignis
Wer
Der
      Kurzname des Referenz-ERP-Bedieners
IP
Die
      IP-Adresse des Referenz-ERP-Client
Verm.
Über
      diesen Vermerk haben Sie die Möglichkeit einen Hinweis mit einer Anmerkung
      zu versehen.
Erl.
Hier
      kann ein Erledigungskennzeichen gesetzt werden.
Verm.
Erledigungsvermerk
Fehlernummer
Die
      meisten der internen Aeins-Systemhinweise sind mit Meldungen hinsichtlich
      der „Fehlernummer“ ausgestattet. Das erlaubt im Zweifel eine zusätzliche
      Bewertung der jeweiligen Umstände.
Was
Der
      Systemhinweistext
ID
Eindeutige Identifizierung des
      Systemhinweises.
Funktionen
Pflege-Funktionen
Ändern, Löschen
Fehlerprotokoll Event
Pfleger zum Erzeugen von Events die
      das Fehlerprotokoll zyklisch löschen.
Fehlerprotokoll
      zurücksetzen
Löscht nach Rückfrage alle
      Fehlerprotokoll-Einträge
Zeitdifferenz messen
Bietet die Möglichkeit, die
      Zeitdifferenz zweier markierter Einträge in Millisekunden zu
      berechnen.
Bereich/Profile
Tage
      zurück
Listet alle Systemhinweise innerhalb
      des Zeitraumes.
Bereich wie
Ermöglicht die Suche in den
      Bereichen.
F3
ermöglicht die konkrete Auswahl und
      informiert über die Anzahl der jeweiligen Bereichs-Einträge.
Fehlerstufe von .
[...]


---

## Verlauf des Imports

Verlauf des Imports
Nachdem eine eRechnungs-XML im Formulararchiv abgelegt
wird, kann diese importiert werden.
Die Schritte, die hier gemacht werden, sind:
1.
Prüfung, ob es sich bei dem markierten Eintrag um einen der Belegklasse
8045
(eRechnung-Import-Xml).handelt
2.
Prüfung, ob es sich beim Xml um eines der Formate UBL-Invoice, UBL-CreditNote
oder CII handelt.
3.
Validierung des Xml nach den Regeln der KoSIT
4.
Einlesen der Daten in die Tabellen XRe
5.
Ggf. die Ermittlung eines Kunden/Lieferanten
Bei der Verwendung von
[FAI]
und
[EMAIL]
werden diese Schritte automatisch
angestoßen.
Beim manuellen Import muss dies mit der Funktion
eRechnung bearbeiten
manuell für den
Eintrag aufgerufen werden.

---

## Vieraugenprinzip beim DTA Verfahren

Vieraugenprinzip beim DTA
Verfahren
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Variante „Zahlungen nach DTA-Laufnr.
Vieraugen“
Direktsprung
[ZHB]
Gerade im Zahlungsverkehr kann es wünschenswert sein,
dass es eine Trennung zwischen den Bedienern gibt, die einen Zahlungsauftrag
erstellen und denen die den Auftrag prüfen und dann an die Bank geben. Um das zu
gewährleisten sind folgende Einrichtungsschritte notwendig:
1)
Die Bediener, welche die Zahlungen erstellen, müssen in einer anderen
Bedienerklasse sein als die Bediener, die die Zahlungen kontrollieren und
freigeben.
2)
Der
Steuerparameter 716
„Vieraugenprinzip
beim DTA Verfahren“ muss angeschaltet werden. Dieser Steuerparameter sorgt
dafür, dass die Variante „Zahlungen nach DTA-Laufnr. Vieraugen“ aktiviert wird,
und beim Erstellen des Datenträgeraustausch die Ausgabedatei nicht geschrieben
wird und auch der Explorer – unabhängig von den Einstellungen in den
Einrichterparametern – nicht geöffnet wird.
Die Funktion „Übernahme in
die Primanota“ steht bei gesetztem Steuerparameter nur in der Variante
„Zahlungen nach DTA-Laufnr. Vieraugen“ zur Verfügung. Dort werden nur Zahlungen
an die Primanota übertragen, deren Status „Übertragen“ ist.
3)
Der Druck der Banksammelliste, des Diskettenbegleitzettels und der Avisen werden
weiterhin beim Erstellen abgefragt.
4)
Folgende Nachlauffunktionen, die in den Einrichterparametern der
Erstellungsmaske eingestellt werden können, werden beim Zusammenstellen der
Daten weiterhin ausgeführt und können z.B. dazu genutzt werden, um die Anwender
aus der Kontroll-Bedienerklasse per Mail automatisch zu informieren. Zu beachten
ist, dass die Datei, die mit /FILE= an das Skript übergeben wird, nicht
existiert:
a.
VBS-Skript ausführen.
b.
VBA-Skript ausführen.
c.
SQL-Prozedur ausführen.
d.
Crystal Report ausführen.
5)
Mithilfe des Schutzsystems „Zugriffsrechte Varianten“ (Direktsprung
[ZUGV]
) muss die Variante „Zahlun
[...]


---

## Vorbelegung Kassennummer

Vorbelegung
Kassennummer
Die Nummer der Kasse an der der Bediener sitzt, wird
in der Regel vor der ersten Erfassung abgefragt. Um diese Abfrage zu umgehen,
können zwei Wege beschritten werden:
1.
In der AHOI.INI im Windows-Verzeichnis kann in der Abteilung [ACASH2] der Wert
Kassensystem mit der Nummer des vorzubelegenden Kassensystems belegt werden.
Achtung! Es handelt sich hier um die Nummer des Kassensystems, also der
Hardware, nicht der Kasse (obwohl diese i.d.R. identisch sein könnte).
Diese Vorgehensweise
empfiehlt sich selbstredend nicht für eine Referenz-ERP-Installation auf dem
Terminalserver.
[ACASH2]
Kassensystem=34
2.
In der Registry kann im Pfad [HKEY_CURRENT_USER\Software\Branchen-ERP\Referenz-ERP\ACASH2] der
Wert Kassensystem eingetragen werden.
Diese Vorgehensweise kann
bei der Referenz-ERP-Installation auf einem Terminalserver verwendet werden.
Windows Registry Editor Version 5.00
[HKEY_CURRENT_USER\Software\Branchen-ERP\Referenz-ERP\ACASH2]
"Kassensystem"="3"

---

## Vorkonten

Vorkonten
Da RFS-Vorkonten an die Zahlungsbedingungen gekoppelt
sind, werden diese im Aeins auch mit dem Pflegemodul für Zahlungsbedingungen
eingerichtet ( Direktsprung ZB ):

---

## VWZ-Zuordnung

VWZ-Zuordnung
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
VWZ-Zuordnung
F11
Direktsprung
[ECL]
Es kommt vor, dass im Verwendungszweck Formulierungen
vorkommen, die keine Kontonummer beinhalten, jedoch einem festen Konto
zuzuordnen sind ("Miete Bürogebäude", "Zinsgutschrift",....). Oder man will für
bestimmte Auftraggeber die Konten nach Gutschrift und Lastschrift teilen. Für
diese Anforderungen kann man hier – getrennt für Gutschrift und Lastschrift –
Konten hinterlegen, die bei der automatischen Kontierung
F6
herangezogen
werden.
Der obere Teil dient dazu, die Bestandteile zu
bestimmen, welche zur Identifikation verwendet werden sollen. Die Haken in der
linken Spalte besagen, welches dieser Kriterien aktiv zur Bestimmung
herangezogen wird. Es muss mindestens ein Haken aktiv sein. Im Beispiel oben
wird also nach einer Lastschrift über 19,94 Euro von ADDVISION-WESLEY
gesucht.
Beschreibung
Ausführungszeitpunkt
Hier
      kann „Vor Kontenerkennung“ oder „Nach Kontenerkennung“ angegeben werden.
      Standardeinstellung ist „Nach Kontenerkennung“.
Sortierung
In
      dieser Reihenfolge werden die Zuordnungen zur Bestimmung des Kontos
      herangezogen. Kann das Konto bestimmt werden, werden die folgenden
      VWZ-Zuordnungen ignoriert. Hat man zum Beispiel zwei
      Verwendungszweckzuordnungen eingerichtet, der erste so wie oben abgebildet
      und beim zweiten - bei dem dann Sortierung auf 2 steht -  nur den
      Auftraggeber aktiviert, so werden die Lastschriften über 19,94 dem Konto
      aus der ersten Verwendungszweckzuordnung zugeordnet, alle anderen Zeilen
      mit diesem Auftraggeber gehen auf das Konto der zweiten
      Zuordnung,
Zahlungsart
Man
      kann die Suche so trennen, dass sie nur für Lastschriften oder nur für
      Gutschriften gelten.
Groß-/Kleinschreibung
      ignorieren
Diese Einstellung gilt für die
      Felder Verwendungszweck und Auftraggeber
Verwendungszweck
Hier
      können Texte,
[...]


---

## Waagenimport

Waagenimport
Unterschiedliche Branchen-ERP-Kunden benötigen ähnliche
Import- oder Exportschnittstellen, die mit Hilfe der Pascal-Skriptsprache
realisiert werden können. Für jede Problematik soll es möglichst nur ein
Standard-Pascal-Skript geben. Dies hat entscheidende Vorteile z. B. im
Update-Handling und in der Wartung.
Die Datensicherheit dieser Parameter spielt eine
wichtige Rolle. Kleine Manipulationen führen sofort dazu, dass ganze Skripte
nicht mehr ordnungsgemäß funktionieren. Daher müssen die Bearbeitungsrechte
restriktiv behandelt werden.

---

## Waagenschnittstelle – Standardeinstellungen

Waagenschnittstelle – Standardeinstellungen
Durch die Einrichtung der Waage nach untenstehenden
Vorgaben wird kann die Standard-Waagenschnittstelle im Referenz-ERP mit
geringmöglichem Aufwand eingerichtet werden:
Dateiformat
ASCII
Transferdateiname
WAAGE.DAT
Anzahl der Satzarten
2
Satzartkennung Cerea
CER
Satzartkennung Faktura
FAK
Datumsformat
JJMMTT
Laufwerk für Import
A:\
Konvertierung Sorte nach Artikel in
      Satzart Cerea
Ja
Default-Lagernummer
1
Fehlerakzeptanz LKW mit unbekanntem
      Kennzeichen
Ja
Default-Steuerschlüssel
1
Datenimport wird nur akzeptiert,
      wenn alle Daten fehlerfrei sind
Ja
interne Zwischendatei
C:\TEMP\WAAGE.DAT
Wiegenummer
aus
      Waage
Default-Mengeneinheit
1
(ME_Nummer für „kg“ in
      Basis-Datenbank)
Aufbau der Importdatei
Position
Länge
Artikel (Satzart
      Faktura)
37
6
Kunde
4
8
Lieferscheindatum
20
6
Lieferscheinnummer
12
8
Menge
55
6
      (Cerea), 5 (Faktura)
Qualität 1
61
4
Qualität 2
66
6
Qualität 3
71
4
Qualität 4
75
4
Qualität 5
79
2
Qualität 6
81
3
Qualität 7
86
4
Satzartkennung
1
3
Sorte
33
2
Steuerschlüssel
11
1
Wiegenummer
12
8
Wichtiger Hinweis
Bei Aeins-Versionen bis 4.2.2.181 (21.06.1999) ist
nach Beendigung der Konfigurationen das SQL-Script WAAGKORR.SQL per Direktsprung
[OSQL] F3 einzuspielen. Es enthält folgendes Statement:
delete from ScriptParamPar WHERE
ScriptPId='WaagenImport' and ScriptPPAktiv=0;
commit;

---

## XMLExport

XMLExport
Syntax
XMLEXPORT Relationsname [
ON
EXISTING
{
ERROR
|
SKIP
|
UPDATE
} ]
[
REPLACING ColumnName=Value ]
[
WHERE
search-condition
]
[
WITH DELETE]
[ WITH FOREIGNKEY]
[ INTO Filename ]
Purpose
Schreibt die Werte dieser Relation in eine Datei im
XML-Format
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
DBFLOAD
,
DBFCREATE
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
,
XMLIMPORT
Beschreibung
Hier werden die Daten der Relation „Relationsname“ und
alle über Foreign Keys verbundene Relationen
in eine Datei im XML-Format
ausgegeben. Gibt man optional ON EXISTING an wird diese Option in die Datei
geschrieben:
<insert-option>ON EXISTING SKIP</insert-option>
Diese Option wird von XMLLOAD ausgewertet. Ein Export für Tabellen ohne
PRIMARY KEY mit dieser Option ist nicht möglich. Es erscheint dann die
Fehlermeldung:
Der optionale Parameter REPLACING teilt dem System
mit, dass die folgenden Spalten einem anderen Wert bekommen sollen.
Beispiel:
REPLACING
FormularId=@JVARS(1000,‘FormularID‘)
oder
REPLACING
FormularId=7000
Es können auch mehrere Spalten durch komma getrennt
angegeben werden.
Der Optionale Parameter WHERE gefolgt von der
Searchcondition sorgt dafür, das nicht alle Daten der Relation exportiert
werden
Die Option „WITH DELETE“ sorgt dafür, dass eine
Option
<delete-option>[WHERE serach-condition]</delete-option> in
die Datei geschrieben wird. Beim Import wird diese Option dann ausgewertet und
vor dem Insert werden entweder alle Daten oder nur die über die Where-Bedingung
eingegrenzten gelöscht.
Wenn „WITH FOREIGNKEY“ angegeben wird, so wird
geprüft, ob in dieser Tabelle Foreign-Keys existieren. Wenn Ja, so werden diese
Tabellen mit exportiert.
Mit INTO gefolgt vom Dateinamen kann das
Exportverzeichnis angegeben werden. Wird diese Option weggelassen, werden die
Daten auf das Exportverzeichnis geschrieben.
Die XML-Datei hat folgendes Aussehen:
<?xml version="1.0"
encoding="UTF-8" ?>
- <OSQLXML App="

[...]


---

## XML-Struktur

XML-Struktur
Beispiel einer Rechnungsverbuchung:
<?xml version="1.0"
encoding="ISO-8859-1"?>
<EDILD01>
<Header>
<Empfaengername>Buchungsstelle</Empfaengername>
<Erstellungsdatum>18.09.07</Erstellungsdatum>
<Erstellungszeit>15:12</Erstellungszeit>
<Nachrichtentyp>accounting</Nachrichtentyp>
<Testuebertragung>1</Testuebertragung>
<externe-Referenz>Branchen-ERP-13652314315</externe-Referenz>
<AnzahlBelege>1</AnzahlBelege>
<LaufendeNr>1</LaufendeNr>
<Belegdaten>
<Belegart>Rechnung</Belegart>
<Rechnungsnummer>4426</Rechnungsnummer>
<GWS-Nr>461456141</GWS-Nr>
<Mandant>Musterfirma</Mandant>
<Verk-an-Deb-Nr>27754</Verk-an-Deb-Nr>
<Verk-an-Adresse>A-Strasse</Verk-an-Adresse>
<Verk-an-PLZ-Code>24011</Verk-an-PLZ-Code>
<Verk-an-Ort>Kiel</Verk-an-Ort>
<Verk-an-Name>Martin Steyer</Verk-an-Name>
<Faelligkeitsdatum>18.09.07</Faelligkeitsdatum>
<Soll-Haben>Soll</Soll-Haben>
<Rechnungssumme>1562,00</Rechnungssumme>
<Rechnungssumme-inkl-mwst>1858,78</Rechnungssumme-inkl-mwst>
<MWST-Summe>296,78</MWST-Summe>
<VST-Summe>0,00</VST-Summe>
<Belegdatum>18.09.07</Belegdatum>
<Buchungsdatum>18.09.07</Buchungsdatum>
<Erstdruckinformation>18.09.07</Erstdruckinformation>
<Storno-Beleg>0</Storno-Beleg>
<Belegsteuer>
<Soll-Haben-Steuer>Haben</Soll-Haben-Steuer>
<Steuertyp>Ust</Steuertyp>
<MWST-p>19,00</MWST-p>
<MWSTBetrag>296,78</MWSTBetrag>
</Belegsteuer>
<Positionsdaten>
<Zeilennr>2</Zeilennr>
<Art>Artikel</Art>
<Nr>Fleischwurst</Nr>
<Beschreibung>kleine Fleischwurst</Beschreibung>
<Beschreibung-2>Wurstfleisch</Beschreibung-2>
<Lieferungsnr>4426</Lieferungsnr>
<Lieferdatum>18.09.07</Lieferdatum>
<Lagerortcode>Saatlager</Lagerortcode>
<Menge-Basis>100,00</Menge-Basis>
<Menge-Verkaufseinheit>100,00</Menge-Verkaufseinheit>
<Verkaufseinheitencode>Stck</Verkaufseinheitencode>
<Basiseinheitencode>Stck</Basiseinheitencode>
<Soll-Haben-Position>Haben</Soll-Haben-Position>
<Steuertyp-Position>Ust</Steuertyp-Position>
<MWST-p>19,00</MWST-p>
<Betrag>1562,00</Betrag>
<Betrag-inkl-MWST>1858,78</Betrag-inkl-MWST>
<
[...]


---

## XMLImport

XMLImport
Syntax
XMLImport Dateiname;
Purpose
Importiert Daten aus einer XML-Datei. Format ist
vorgegeben. Siehe dazu XMLExport
Anwendung
Befehlszeile, Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
DBFLOAD
,
DBFCREATE
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
,
XMLEXPORT
Beschreibung
Daten die mit XMLExport ausgelagert wurden, bzw. die
dieselbe Struktur haben, können hier importiert werden. Exsitiert die Tabelle
nicht, so wird diese angelegt. Existieren einzelne Felder nicht in der Relation,
so werden diese angelegt. Ist dies nicht möglich – z.B. Tabelle von einem
Benutzer gesperrt – werden die Daten nicht eingespielt. Es erscheint dann der
Fehlerhinweis
Existiert auf der Zieldatenbank zu dieser Tabelle kein
Primary Key, so wird er – gegebenenfalls nach Ausführen des Delete-Statements -
angelegt. Es wird nicht geprüft, ob der Primary Key sich unterscheidet.
Indexe werden nicht angelegt.
Beispiel
XMLImport c:\AEINS\EXPORT\Fibuvorgklasse.xml

---

## XML-Transfertabelle

XML-Transfertabelle
Die dritte Variante zeigt Ihnen, welche Daten in der
Zwischen Relation sich befinden.

---

## Zahlungsbeleg erstellen (Buchen)

Zahlungsbeleg erstellen
(Buchen)
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zahlungsverkehr
e-Clearing
Funktion
Übernahme in Primanota
F8
Direktsprung
[ECL]
Zum Buchen zugelassen werden nur Daten, die noch nicht
gebucht wurden und bei denen in sämtlichen Positionen Konten eingetragen wurden.
Sollten bei den Konten auch Sachkonten hinterlegt sein, wird direkt vor dem
Buchen geprüft, ob zu allen Konten, bei denen eine Kostenstelle Pflicht ist,
auch eine eingetragen ist. Ansonsten wird eine Liste mit Fehlern ausgegeben und
der Beleg kann nicht gebucht werden.
Sollte man mit Kostenträgern arbeiten,
werden auch die im Sachkontenstamm hinterlegten Kostenträger auf diese Weise
geprüft. Einträge, bei denen der Kostenträger Pflicht ist und kein Kostenträger
angegeben ist, führen zum Fehler. Der Beleg kann dann nicht gebucht werden. Dies
gilt genauso für
Kostenobjekte
.
Weiterhin wird bei Sachkonten die hinterlegte
Steuerinformation ausgewertet und gegebenenfalls eine Steuerposition erzeugt.
Steuerpositionen werden gerafft dargestellt, d.h. wenn mehrere Positionen mit
demselben Steuersatz existieren, so wird nur eine Summenzeile erzeugt. Diese hat
dann als Text „Sammelposition e-Clearing(nnn/nnn) Auszug nnn vom nnn“. Der
Betrag wird immer Brutto interpretiert und es wird dementsprechend auch der
Steuersatz für Bruttobuchungen herangezogen (also Steuerklasse 2 oder
Steuerklasse 102). Fehlerhafte Stammdaten - fehlender Steuersatz bzw. fehlendes
Steuerkonto – führen dazu, dass der Beleg nicht gebucht werden kann. Es wird ein
Fehlerhinweis ausgegeben.
Beim Erstellen von
Zahlungsdienstleister-Zahlungsbelegen werden die Gebühren des
Zahlungsdienstleisters auf das ihm hinterlegte
Gebührenkonto
gebucht. Wurde dem
Zahlungsdienstleister kein Gebührenkonto zugeordnet, so werden die Gebühren
nicht gebucht. Abhängig von der Option „
Gebühren des Zahlungsdienstleisters als Summe
buchen
“ wird entweder eine einzelne Gebührenposition erzeugt oder es
wird pro Gebühr eine Gebühre
[...]


---

## Zapfsäulen-Schlüsselung

Zapfsäulen-Schlüsselung
Zapfsäulen bzw. verschiedene Treibstoffe können wie Sorten
verarbeitet werden, wobei eine Umschlüsselung von Sorte zu Artikel stattfinden
muss. Übertragung der Script-Parameter zum Kunden.
Um die Parameter der Waagenschnittstelle auf eine
Kundendatenbank zu übertragen, geht man wie folgt vor:
Start von Aeins mit der Referenzdatenbank, auf der
sich das für den Kunden vorbereitete Waagen-Modul befindet.
Direktsprung [MAKRO],  Auswahl des Makros
Waagenschnittstelle_an_Kunde
. Taste
F5, Taste F9 (ausführen).
Das Script erzeugt eine Datei mit dem Namen
WAAGE_AN_KUNDE.SQL.
Der Datenträger wird auf der Kundendatenbank wie folgt
eingespielt:
Direktsprung [OSQL], Taste F3, Button Filebox,
Auswählen der Datei mit dem Namen
WAAGE_AN_KUNDE.SQL
. Button Start.
Fertig.
Das Import-Script der Waagen-Schnittstelle kann
individuell parametrisiert werden. Eine Reihe von Parametern steht dazu zur
Verfügung, die im folgenden erläutert werden. Die Pflege der Parameter erfolgt
über den Direktsprung [SCPA] in der Anwendung Scriptparameter. Die
Parametergruppe mit der
ScriptPId „WaagenImport“
ist für die Steuerung
der Waagenschnittstelle zuständig. Im Detailbereich sind die einzelnen der unten
beschriebenen Parameter aufrufbar. Anwender mit der entsprechenden
Zugangsberechtigung können die Werte der Parameter individuell an die eigene
Waagendatei anpassen.
Zur besseren Übersicht kann eine Liste der Parameter
mit einer Crystal-Reports-Liste ausgedruckt werden. Diese Funktion steht
innerhalb der Anwendung unter
Script-Parameter (DRUCK)
zur Verfügung.

---

## Zuordnung zum Kunden (ausgehend)

Zuordnung zum Kunden (ausgehend)
Dieses Kapitel beschreibt die Zuordnung des
EDI-Partners zu dem Kunden. Eine Zuordnung ist nur dann sinnvoll, wenn das
Rosi-Profil vollständig angelegt wurde. Die Erstellung des Rosi-Profils wird im
vorran­gegangen Kapitel beschrieben.
1.
Die Anwendung „Kundenstamm“ mit dem Direktsprung [KU] aufrufen.
2.
Den entsprechenden Kunden markieren und mit Taste „F5“ zum Bearbeiten
öffnen.
3.
Im Feld „GLN-Nr.“ steht die ILN-Nummer für den EDI-Partner. Wenn dieses Feld
leer ist, dann die ILN-Nummer eintragen.
4.
Im Feld „EDI-Partner“ die Taste „F3“ drücken und den Eintrag „Rosi INVOICE Test“
auswählen. Das Auswahlfenster wird geschlossen und die Auswahl erscheint im Feld
„EDI-Partner“.
5.
Die Eingaben mit der Taste „F9“ speichern. Die Maske zum Bearbeiten des Kunden
wird geschlossen.

---

## Zuordnung zum Kunden (eingehend)

Zuordnung zum Kunden (eingehend)
Dieses Kapitel beschreibt die Zuordnung des
EDI-Partners zu dem Kunden. Eine Zuordnung ist nur dann sinnvoll, wenn das
Rosi-Profil vollständig angelegt wurde. Die Erstellung des Rosi-Profils wird im
vorran­gegangen Kapitel beschrieben.
1.
Die Anwendung „Kundenstamm“ mit dem Direktsprung [KU] aufrufen.
2.
Den entsprechenden Kunden markieren und mit Taste „F5“ zum Bearbeiten
öffnen.
3.
Im Feld „GLN-Nr.“ steht die ILN-Nummer für den EDI-Partner. Wenn dieses Feld
leer ist, dann die ILN-Nummer eintragen.
4.
Im Feld „EDI-Partner“ die Taste „F3“ drücken. Wenn der EDI-Partner in der
Auswahl vorhanden ist, dann weiter mit Schritt 12.
5.
Die Funktion „Itembox/Daten pflegen“ (oder Tastenkürzel „Shift + F2“)
auswählen.
=> Der Pfleger für den EDI-Partner wird geöffnet.
6.
Im Feld „Nr.“ eine Zahl eintragen.
7.
Im Feld „Textersetzung“ die Bezeichnung „Rosi ORDERS Test“ eingeben.
8.
Im Feld „Kommentar, Schnipsel“ den String „400=x“ eingeben.
400 =>
Vorgangsklasse für Aufträge
x => ID des EDI-Partners (siehe Kapitel
„EDI-Partner anlegen“ Schritt 4).
9.
Im Feld „Aktiv“ die Taste „F3“ betätigen und den Eintrag „aktiv“ auswählen.
10.  Die
Eingaben mit der Taste „F9“ speichern. Die Eingabemaske wird geschlossen.
11.  Die
Funktion „Liste aktualisieren“ (oder Taste „F2“) auswählen. Die Auswahl wird
aktualisiert.
12.  Den
Eintrag „Rosi ORDERS Test“ auswählen. Das Auswahlfenster wird geschlossen und
die Auswahl erscheint im Feld „EDI-Partner“.
13.  Die
Eingaben mit der Taste „F9“ speichern. Die Maske zum Bearbeiten des Kunden wird
geschlossen.

---

## Zuordnung vergleichen

Zuordnung vergleichen
Felder
Publikation 1
Name
      der Publikationen aus der Auswahlliste.
F3
      Funktion zur Auswahl einer anderen Publikation.
Publikation 2
F3
      Funktion zur Auswahl einer Publikation.
Artikel
Zeigt die Artikel, die in der
      jeweils ausgewählten Publikation enthalten sind.
Funktionen
Kopieren
Kopiert die/den ausgewählten Artikel
      in die jeweils andere Publikation.
Entfernen
Entfernt den/die ausgewählten
      Artikel aus der beinhaltenden Publikation.
Alles markieren
Markiert alle Artikel der
      beinhaltenden Publikation.
Gleiche markieren
Sucht übereinstimmende Artikel
      beider Publikationen und markiert diese.
Differenzen
Sucht die Artikel beider
      Publikationen heraus, die nicht in der jeweils anderen Publikation
      vorhanden sind und markiert diese.
Aktualisieren
Lädt
      die Artikel beider Publikationen neu und aktualisiert somit die
      Ansicht.

---

## Zusatzfelder für EDI in der Auswahlliste

Zusatzfelder für EDI in der Auswahlliste
Feld
Bedeutung
Export
Rot
= Die Datei wurde vom Rechenzentrum
      an den Partner übermittelt und der Partner meldet das der Beleg falsch
      ist.
Gelb
= Die Datei wurde an das
      Rechenzentrum übermittelt
Grün
= Die Datei wurde übermittelt und
      der Partner schickt eine Meldung das alles OK ist.
EDI-Partner
Rot
= Der Partner ist
      falsch eingerichtet oder es fehlt z.B. eine ILN
Grün
= Alles richtig
      eingerichtet

---

