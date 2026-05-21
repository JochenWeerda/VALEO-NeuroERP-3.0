# Compliance, Qualität & Zertifizierung — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (40 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## SPA350 Druck Quellinfo einstufig in [FRZ]

SPA350 Druck Quellinfo einstufig in [FRZ]
Steuerparameter 350 - "Druck Quellinformation
einstufig" kann nun in [FRZ] übersteuert werden. Folgende
Einstellungsmöglichkeiten gibt es:   ¨Nein¨: Alle Quellvorgänge (außer
Vorgangsklasse Ladeschein) werden gedruckt.  ¨Ja¨: Die letzte Quelle vor
dem Beleg wird gedruckt. Beim Lieferschein ist das immer der Auftrag (nicht der
Ladeschein) Wie Spa
Releasenote Kategorie:
Ticket: 717141[33278]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Formularzuordnung
Variante: Vorgangsunterklassen
Funktion/Report: Registerkarte SPA
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33278, 717141

---

## Complianceprüfung Webanbindung

Complianceprüfung Webanbindung
Das von uns ausgelieferte Modul "Sanktionsliste" wurde
ergänzt, da die Complianceprüfung ab dem 01.02.2023 ein anderes
Sicherheitsprotokoll erwartet.
Releasenote Kategorie:
Ticket: 720381[33486]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: n/a
Variante: n/a
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33486, 720381

---

## Partiestamm: Funktion "Qualitäten"

Partiestamm: Funktion "Qualitäten"
In der Anwendung Partiestamm [PAR] wurde die Funktion
"Qualitäten" fälschlicherweise über eine Lizenz geschützt. Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 728667[34533]
Version: 8.3.2312.8
Datum: 08.12.2023
Anwendung: Partiestamm [PAR]
Variante: -
Funktion/Report: Qualitäten (F9)
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.8, 34533, 728667

---

## Compliance

Compliance
Der Abruf der terrorgefährdeten Personen über den
Compliance-Automat wurde verbessert.
Releasenote Kategorie:
Ticket: 727888[34423]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Anschriften [ANSCH]
Variante: -
Funktion/Report: Verbotslistenprüfung
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34423, 727888

---

## TAR-Export ist nun auch nach Ablauf des TSE-Zertifikates

TAR-Export ist nun auch nach Ablauf des TSE-Zertifikates
TAR-Export ist nun auch nach Ablauf des
TSE-Zertifikates möglich.
Releasenote Kategorie:
Ticket: 752960[39397]
Version: 9.0.2502.9
Datum:
Anwendung: TSE
Variante: STD
Funktion/Report: TAR-Export, Löschen /
Wiederherstellen
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39397, 752960

---

## LWK-Qualitätsanalyse (EPA BTQUALITAETSDATEN1)

LWK-Qualitätsanalyse (EPA
BTQUALITAETSDATEN1)
Bezeichnung
Standardwert
Erklärung
KF
      Auszählung auf Basis 2 mal 50:Ja, 100:Nein
Ja
Tabreiter 3 Gridüberschrift Feld
      1
Schad/Nährstoffe
Tabreiter 3 Gridüberschrift Feld
      2
<
Tabreiter 3 Gridüberschrift Feld
      3
Menge
Tabreiter 3 Name
Lufa
TAB-Karte - 1 -
      deaktivieren
Nein
TAB-Karte - 2 -
      deaktivieren
Nein
TAB-Karte - 3 -
      deaktivieren
Nein
Erstes Eingabefeld
Prozedur für die Qualitätsdaten im
      Kopfbereich
Kundengruppe LUFA Labore
0
Zusammensetzung per Artikelstamm,
      sonst alle Bestandteile
Nein

---

## Qualitätslabor nach ISTA (EPA LABORDATEN)

Qualitätslabor nac
h ISTA (EPA
LABORDATEN)
Bezeichnung
Standardwert
Erklärung
Name
      des Startfeldes
h.ProbenTyp$
Name
      des Feldes in dem die Schreibmarke nach öffnen der Eingabemaske stehen
      soll.
F3
      Itembox für die Partiebezeichnung
Name
      der Itembox die auf dem Eingabefeld Partiebezeichnung genutzt werden
      soll.
Nachkommastellen Reinheit auf 4
      Stellen
Nein
Bei
      Einstellung
Ja
werden die Eingabefelder „KU1“, „KU2“, „KU3“,
      „KUSum“, „UK1“, „UK2“, „UKSum“, „UV“ und „Scler.“ mit 4 Nachkommastellen
      angezeigt.
Kundengruppe LUFA Labore
0
Auswahl welche Kundengruppe im
      Verfahren „Lufa“ für das Prüfinstitut herangezogen wird.
Erweiterte Einstellungen
Nein
Bei
      Einstellung
Ja
werden die Eingabefelder des Verfahrens „TKM
      Leguminosen“ mit vier Nachkommastellen angezeigt. Das Endergebnis der
      Untersuchung wird vorbelegt. Bei dem Verfahren „Besatz“ wird die
      Untersuchungsmenge mit drei Nachkommastellen angezeigt. Bei dem Verfahren
      „TKM Extern“ wird der Wert für TKM g mit vier Nachkommastellen angezeigt.
      In allen Verfahren zur „Keimfähigkeit“ wird das Eingabefeld „Menge Körner“
      durch das Eingabefeld „Behandlungsmenge ersetzt.“
Methodenauswahl auf Probentyp
      einschränken
Nein
Ist
      hier der Wert
Ja
eingetragen, so erfolgt bei der Methodenauswahl
      eine Filterung nach dem angegebenen Probentyp (Zweck)
Waagenterminal für die
      Probenannahme
0
Nummer des
      Waagenterminals.
Für
      folgende Bediener nur Hybridity anzeigen
Eine
      durch Komma getrennte Liste der Anwender, die nur das Verfahren Marker
      bearbeiten können.
Nicht verwendete Verfahren
      ausblenden
Ja
Auf
      der Maske Labordaten existieren Registerkarten, auf denen mehrere
      Verfahren dargestellt werden. Steht dieser EPA auf
Ja,
so werden
      nicht verwendete Verfahren ausgeblendet. Stellt man diesen EPA aus
Nein,
so reagiert das System wie früher und lä
[...]


---

## DSGVO-Lizenz(SPA1035)

DSGVO-Lizenz(SPA1035)
Lizenz für das DSGVO-Modul.

---

## Zertifikatsverwaltung-Lizenz (SPA1112)

Zertifikatsverwaltung-Lizenz (SPA1112)
Lizenz für das Modul „Zertifikatsverwaltung“.

---

## Bei neuer Partie Qualitätssatz anlegen(SPA 526)

Bei neuer Partie Qualitätssatz anlegen(SPA 526)
Steht dieser Steuerparameter auf „Ja“ (1), so wird im
Partieneuanlagefall sofort ein Qualitätsdatensatz mit angelegt.

---

## Artikelverpackung 1-stuf. Gebinde(SPA 591)

Artikelverpackung 1-stuf. Gebinde(SPA 591)
Vorbelegung der Gebindenummern in einer
Artikelverpackung, wenn ein einstufiges Gebinde erforderlich ist.

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

## Verbotsliste

Verbotsliste
Diese Funktionen sind exklusiv für das Compliancemodul
von Referenz-ERP.
-
Verbotslistenprüfung: prüft die ausgewählte Anschrift.
-
Als Good-Guy definieren: Hier kann eine Ausnahme für die Verbotslistenprüfung
hinzugefügt werden.
-
Definierte Anschriften prüfen: Abhängig von der Prozedur des SPA 1063 wird hier
eine Verbotslistenprüfung ausgeführt.
-
Verbotsliste Ausnahme anzeigen: fall der Datensatz als Good-Guy definiert wurde,
kann man die Begründung einsehen.

---

## Formulararchiv (Belege mit NULL-Dok.)

Formulararchiv (Belege mit
NULL-Dok.)
Diese Spezialvariante hilft „leere“ Dokumente im
Archiv aufzufinden.
Neben der Möglichkeit sich anzuschauen um welche
Formulararchiv-Einträge es sich handelt lassen sich auch hier ggf. die
NULL-Dokumente mit Hilfe der Funktion „Löschen der NULL-Dokumente“
stornieren.

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

## Allgemeine Scanner Einstellungen

Allgemeine Scanner Einstellungen
Für das Zusammenspiel zwischen dem Scanner und unserer
Aeins Software sind noch ein paar allgemeine Einstellungen nötig.
Tipp: Es ist zu empfehlen, dass alle nicht benötigten
ScanCodes ausgestellt werden.
Häufig benötigte Scancodes
EAN
      8
EAN
      13
UPCA
CODE
      128
EAN
      128

---

## Qualitätsmerkmale(EPA Qualitätsmerkmale)

Qualitätsmerkmale(
EPA
Qualitätsmerkmale
)
Bezeichnung
Standardwert
Erklärung
Erweiterte Einstellungen
Nein
Zeigt neu hinzugefügte Felder
      an.

---

## Referenz-ERP FAQ

Referenz-ERP FAQ
Im Folgenden werden Sie eine Auflistung von Fragen mit
den dazugehörigen Antworten finden. Dazu navigieren Sie zuerst in den
Themenbereich und suchen dann ihre Frage.
Erläuterung: An dieser
Stelle finden Sie Fragen, die von Anwendern so oder ähnlich häufig gestellt
werden. Unsere Antworten hierauf sind eine erste allgemeine Erklärung bzw.
Handlungsempfehlung. Greift diese im Einzelfall nicht, gilt es weitere
Möglichkeiten, die Situation aufzuklären.

---

## Gewinnung aus Dateiinhalt

Gewinnung aus Dateiinhalt
Sollen die Kern-Daten aus dem Dateiinhalt gewonnen
werden, sollte man sich zunächst vergegenwärtigen das Dateiinhalt etwas sehr
abstraktes und möglicherweise etwas höchst Binäres ist …
Es muss also eine „Absprache“ geben, wie diese Daten
aufzufinden sind.
Moderne Scanner-Systeme legen Ihren binären
Informationen das Ergebnis einer OCR-Erkennung bei. Damit ist es möglich gezielt
nach Mustern zu suchen. Wenn die Dokumente also bei Drucklegung bzw. Erzeugung
entsprechend ausgelegt worden sind, ist mit hoher Wahrscheinlichkeit ein
gewisser Widererkennungswert gesichert.
Somit wird eine Möglichkeit bereitgestellt, eine
Startkennung, sowie eine optionale Ende-Kennung anzugeben. Diese werden dann
dazu verwendet, das entsprechende „Schnipsel“ aus der binären Datei
herauszufinden, um dann zur weiteren Verarbeitung verwendet werden zu
können.
Hier bei gilt das die Start-Kennung und auch die
Ende-Kennung – sobald eine angegeben –
exakt
übereinstimmen müssen. Es
sei angemerkt das die Kennungen möglichst „eindeutig“ gewählt sein sollten,
damit eine eindeutige Bestimmung überhaupt sinnvoll sein kann. Referenz-ERP kann
leider nicht in jedem Falle das Muster bestimmen, weil es gar nicht die
Ausgangsbelege erzeugt!
Ist keine Ende-Kennung angegeben, liest das System
maximal 128 Bytes ein.

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

## Einrichtung

Einrichtung
Neben den Einrichtungen der Stammdaten sind noch
spezielle Einrichtungsmaßnahmen erforderlich.
•
Nachhaltigkeitsstatus (Format
AF_NACHHSTAT
)
•
Zertifizierungsmethode (Format
AF_ZERTMETH
)
•
Zertifizierungstyps (Format
AF_NAHA_ZERT
)
•
Kategorie des Zertifikats (Format
AF_ZERTKATEG
)
•
SQLK Texte für Nachhaltigkeitsausweise im Formulardruck
•
Formularzuordnung
Die hier aufgelisteten Einzelmaßnahmen werden in den
folgenden Abschnitten erläutert.
SQLK Nachweisvorlage
Eine Vorlage zum Nachweis nachhaltiger Ware auf einem
Vorgangsformular liefern wir unter SQLK_Nachhaltig eine Musterlösung mit. Dabei
wird eine Zulieferfunktion „ist_nachhaltig“ in Form einer Datenbankprozedur mit
Resultset verwendet. Dieser Nachweis ist in jedem Fall für
Verkäufe
relevant, einzelne Anforderungen beziehen sich jedoch auch auf Einkäufe bzw.
Getreidegutschriften. (siehe SQLK Nachweisvorlage)
Einrichtung Vorgangswesen FRZ
U.U. kann es gewollt sein, dass man für Lieferungen
steuern möchte, ob nachhaltige oder nicht nachhaltige Ware geliefert werden
soll. Für solche Kunden trägt man auf dem Zertifikate-Register die
Nachhaltigkeit ein.
In der
Formularzuordnung
(FRZ) trägt man im
Register Abwicklung für die betreffenden Vorgangsunterklassen ein, wie die
Vorgangserfassung zu reagieren hat, wenn ein als nachhaltig geführter Artikel an
einen als nicht nachhaltig geführten Kunden geliefert werden soll. (Feld „Kunde
ungültige Nachhaltigkeit“)

---

## Qualitätsdaten

Qualitätsdaten
In dieser Variante werden die Qualitäten der Partie
gepflegt.

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

## DSGVO-Anonymisieren

DSGVO-Anonymisieren
Die Funktion zum Anonymisieren finden Sie in der
DSGVO-Liste.
Es wird automatisch für das Objekt im Anschriftenstamm
ein Protokolleintrag erzeugt. So ein Eintrag beschreibt, wer die Anonymisierung
wann vorgenommen hat.
Achtung
:
Anonymisieren kann nicht
zurückgenommen werden!

---

## DSGVO Suche

DSGVO Suche
Hier werden Daten gefiltert nach DSGVO-Objekten
angezeigt. Eine weitere Eingrenzung kann über die bekannten Methoden der
Auswahlliste erfolgen.
Mit der Funktion „DSGVO-Liste F10“ können die
markierten Datensätze nun in der DSGVO-Liste angezeigt werden.

---

## DSGVO Feldzuordnung

DSGVO Feldzuordnung
Hauptmenü
Stammdatenpflege
Anschriften
DSGVO
Direktsprung
[DSGVO]
Variante
DSGVO-Feldzuordnung.
Nicht alle Felder müssen oder dürfen anonymisiert
werden.
In der Variante „DSGVO-Feldzuordnung“ werden alle
Objekte und die dazugehörigen Felddefinitionen angezeigt.
Der Bearbeitungsdialog zeigt im oberen Bereich die
Objektdefinition. Die zugeordneten Felder werden in der unteren Tabelle
dargestellt:
Spalte
Bedeutung
Sortierung
Gibt
      die Reihenfolge an, in der die Felder auf der Liste erscheinen. Um z.B.
      das Feld Geburtstag vor dem Feld AdressGeburtsLandISO auszudrucken, würde
      man beim Geburtstag eine 2 eintragen. Das Feld wird dann in diese Zeile
      eingefügt und alle weiteren Felder werden nach hinten
      verschoben
Datenbankfeld
Name
      des Feldes in der Datenbank. Eine Auswahl ist mit F3 möglich. In dieser
      Auswahl werden nur die Felder angeboten, die noch nicht eingetragen sind.
      Sind die Felder von Branchen-ERP vorgegeben, so lässt sich diese Zelle nicht
      ändern.
Bezeichnung in der Liste
Die
      Bezeichnung, die vor dem Wert steht. Wird keine Bezeichnung angegeben,
      dann wird die Bezeichnung des Datenbankfeldes angedruckt.
Rechtsgrundlage
Hier
      kann hinterlegt werden, aufgrund welcher Rechtsgrundlage die
      Anonymisierung erfolgt.
Verarbeitung
Hier
      existieren zwei Auswahlmöglichkeiten:
•
Nur Auskunft:
      Das Feld wird in der Liste angedruckt, jedoch bei der Anonymisierung
      ignoriert,
•
Anonymisieren:
      Das Feld wird sowohl in der Liste angedruckt, als auch bei der
      Anonymisierung verarbeitet.
Um Felder aus dieser Liste zu entfernen kann man
Zeilen mit der Tastenkombination Strg+Umschalt+Entf entfernen, die Zeile wird
dann grau hinterlegt. Die Löschung kann mit derselben Tastenkombination wieder
aufgehoben werden.

---

## EU-DSGVO (Datenschutz-Grundverordnung)

EU-DSGVO
(Datenschutz-Grundverordnung)
Was sind die Datenschutz-Grundverordnung (DSGVO) und
das Bundesdatenschutzgesetz (BDSG)?
Seit dem 25 Mai 2018 gelten die
Datenschutz-Grundverordnung (DSGVO) und das neue Bundesdatenschutzgesetz (BDSG).
Die DSGVO soll natürlichen Personen mehr Kontrolle über die Speicherung,
Übermittlung und Verwendung ihrer persönlichen Daten geben. Sie soll dabei
gleichzeitig die Einheitliche europäische Regelung des Datenschutzrechts
vereinfachen.
Die DSGVO wirkt sich auf Organisationen und
Unternehmen, die innerhalb der EU Geschäfte tätigen und personengebundene Daten
von EU-Bürgern speichern und verarbeiten aus.
Das deutsche Bundesdatenschutzgesetz (BDSG)
regelt ebenso den Umgang mit personenbezogenen Daten und stellt eine
Konkretisierung und Ergänzung zur DSGVO dar.
Weitere Informationen:
DSGVO -
https://eu-datenschutz.org/
BDSG -
https://www.gesetze-im-internet.de/bdsg_2018/
DSGVO und Referenz-ERP
Mit dem Modul „DSGVO“ stellen wir in Referenz-ERP Werkzeuge
als Unterstützung zur Umsetzung der gesetzlichen Vorgaben zur Verfügung.
Hierbei liefern wir bereits Voreinstellungen und
Funktionen innerhalb des Moduls, welche Sie jedoch auch individuell erweitern
können.

---

## Fehlernummern

Fehlernummern
Im Fehlerprotokoll werden Fehlernummern angezeigt.
Diese können unter Umständen hilfreich sein, um herauszufinden, was die Ursache
des Fehlers. Die Fehlertextbeschreibung im Fehlerprotokoll ist unter Umständen
zu kurz, um eine genaue Behandlung darzustellen. Hier gibt es eine
ausführlichere Information dazu:

---

## Gebindemaß 1 und 2

Gebindemaß 1 und 2
Dieses System unterstützt bis zu zweistufige Gebinde.
Die Gebindefaktoren können hier angegeben werden.

---

## Labordaten Ansehen

Labordaten Ansehen
Wählen Sie einen Laborsatz einer Partie aus, deren
Qualitätsdatensatz Sie ansehen möchten und wählen Sie die Funktion „Ansehen“ an.
Ihnen werden die Werte des Datensatzes angezeigt.
Verlassen Sie die Erfassungsmaske mit der ESC-Taste.

---

## Labordaten löschen

Labordaten löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
Qualitaetsdaten (where isnull (method,0)>0)
Qualitaetsaddon entsprechend
Keimfaehigkeit
Besatz
BesatzBesatz
Reinheit
ReinheitBesatz
Gesundheit

---

## Löschen von Labordaten

Löschen von Labordaten
Wählen Sie einen Laborsatz einer Partie aus, deren
Qualitätsdatensatz Sie löschen möchten und wählen Sie die Funktion „Löschen“ an.
Ihnen werden die Werte des Datensatzes angezeigt.
Wenn Sie diesen Datensatz löschen möchten, so
beantworten Sie den Dialog mit „Ja“.

---

## Ändern von Labordaten

Ändern von Labordaten
Wählen Sie einen Laborsatz einer Partie aus, deren
Qualitätsdatensatz Sie ändern möchten und wählen Sie die Funktion „Ändern“ an.
Ihnen werden die Werte des Datensatzes angezeigt.
Der Belegtyp, die Gültigkeit und die dritte Spalte mit
den Analysewerten ist änderbar.
Ändern Sie die Werte.
Verlassen Sie die Erfassungsmaske mit der ESC-Taste.
Wenn Sie die Daten speichern wollen, beantworten Sie
den nachfolgenden Dialog mit „Ja“.

---

## Neue Erfassung von Labordaten

Neue Erfassung von Labordaten
Wählen Sie eine Partie (mit oder ohne Laborsatz) aus,
zu der Sie einen neuen Qualitätsdatensatz erfassen möchten und wählen Sie die
Funktion „Neu“ an.
Wählen Sie einen Belegtyp und geben Sie an, ob dieser
Datensatz für diesen Belegtyp verwendet werden soll.
Alle Werte in der dritten Spalte der Tabelle
Labordaten stehen auf 0,0000. Geben Sie hier Ihre Daten ein.
Verlassen Sie die Erfassungsmaske mit der ESC-Taste.
Wenn Sie die Daten speichern wollen, beantworten Sie
den nachfolgenden Dialog mit „Ja“.

---

## Primanota

Primanota
Nachdem die Belege über die Belegerfassung erfasst
wurden bzw. aus der Warenwirtschaft oder einem sonstigen System in die
Finanzbuchhaltung übertragen wurden, stehen sie so lange
vorläufig
in der Primanota (frei übersetzt: erster Eintrag) bis sie endgültig verbucht
werden. Die Salden sind jedoch bereits aktualisiert und stehen somit bereits –
z.B. in der Konteninformation – zur Verfügung.
Dieser
vorläufige
Status bedeutet:
•
Die Belege können noch geändert werden. Bei Belegen aus der
Referenz-ERP-Warenwirtschaft kann nur eingeschränkt geändert werden (Erlöskonten,
Kostenträger, Kostenstellen, Text). Auch bei Belegen, die vom System erstellt
wurden, wie z.B. Skontobelege, sind nur diese eingeschränkten
Änderungsmöglichkeiten gegeben,
•
Alle Belege können gelöscht werden. Bei Belegen aus der Warenwirtschaft
wird der Übertragsmerker entsprechend zurückgesetzt. Bei automatisch erstellten
Belegen aus der Finanzbuchhaltung (automatischer Zahlungsverkehr, Zinswesen,
Mahnwesen, ...) wird der Buchungsmerker entsprechend zurückgesetzt. Belege, die
automatisch beim Ausziffern erstellt wurden (Kursdifferenzbuchungen,
Skontobuchungen) können nicht gelöscht werden. Diese Belege verschwinden wieder
automatisch, wenn die Auszifferung zurückgesetzt wird (siehe
OP-Verwaltung).
•
Eine Primanota kann gedruckt werden. Dazu stehen vier fest definierte
Crystal-Reporte zur Verfügung.
1.
Primanota nach Belegart: In der Referenz-ERP-Finanzbuchhaltung werden die Belege in
Belegarten unterteilt (ER, EG, AR, AG, ZA, EB, ...). In diesem Report werden die
Belege nach dieser Belegart gruppiert und sortiert nach Belegart und Belegnummer
aufgelistet
2.
Primanota chronologisch: Die Belege werden in der Reihenfolge ausgegeben, wie
sie ins System gekommen sind.
3.
Primanota EURO/Fremdwährung: Die Sortierung erfolgt wie im Report Primanota nach
Belegart, jedoch werden die Beträge sowohl in Buchwährung als auch in
Fremdwährung ausgegeben.
4.
Primanota Hauptbuch: Die erfass
[...]


---

## Reparatur von Vorgängen

Reparatur von Vorgängen
Leider kommt es noch häufiger vor, dass nach
Systemabstürzen oder auch nach internen Fehlern inkonsistente Zustände bezüglich
der Relationen Vorgangstamm / Vorgreservierung existieren.
Seitens des Supports werden diese Ungereimtheiten in der
Regel per OSQL (sehr zeitaufwendig) korrigiert. Wir haben daher ein kleines Tool
entwickelt , das
•
den Zustand bezüglich eines Vorganges übersichtlich darstellt
•
den Supporter bei der Korrektur unterstützt.
Da zur Zeit keine Versionserstellung möglich ist, kann
dieses Tool auch ohne Versionsupdate mit den bekannten Methoden (repair.bat) vor
Ort beim Kunden installiert werden – in der nächsten Version von Aeins wird
dieses Tool unter dem Direktsprung KORVR zur Verfügung stehen.

---

## Variante Fehlernummer

Variante Fehlernummer
In Variante Fehlerprotokoll werden Fehlernummern
angezeigt. Diese können unter Umständen hilfreich sein, um herauszufinden, was
die Ursache des Fehlers war. Die Fehlertextbeschreibung im Fehlerprotokoll ist
unter Umständen zu kurz, um eine genaue Behandlung darzustellen. Hier gibt es
eine ausführlichere Information dazu:
Felder
Define
Alphanumerische Entsprechung der
      Nummer.
(Fehlernummern)
Nr
Fehlernummer
Die
      Fehlernummern sind von Aeins vordefiniert.
Bereich/Profile
Fehlernummer
Ermöglicht die Eingrenzung nach
      Fehlernummern
Define wie
Ermöglicht die Suche in den
      Defines.

---

## Wiederherstellen des Branchen-ERP-Auslieferungszustandes der DSGVO-Einrichtung

Wiederherstellen des Branchen-ERP-Auslieferungszustandes der DSGVO-Einrichtung
Hauptmenü
Stammdatenpflege
Anschriften
DSGVO
Direktsprung
[DSGVO]
Variante
DSGVO-Feldzuordnung und DSGVO-Objekte.
In den Anwendungsvarianten
DSGVO –
Feldzuordnung
und
DSGVO – Objekte
befindet sich im Menü die Funktion
zum wiederherstellen des Auslieferungszustandes der DSGVO-Einrichtung.
Hierzu einfach die Funktion „Branchen-ERP-Standard
wiederherstellen“ im Menü auswählen und die Ausführungsanfrage beantworten.
Die Wiederherstellung wird bei Erfolg durch eine
Meldung bestätigt. Fehler werden im Fehlerprotokoll protokolliert.
ACHTUNG!
Bei der Wiederherstellung des
Branchen-ERP-Auslieferungszustandes werden sämtliche selbst vorgenommenen
DSGVO-Einrichtungen entfernt.

---

