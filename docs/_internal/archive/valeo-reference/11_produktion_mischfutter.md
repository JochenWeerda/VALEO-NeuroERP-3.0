# Produktion & Mischfutterherstellung — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (154 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Produktionserfassung: Eingabe Komponentenmenge

Produktionserfassung: Eingabe Komponentenmenge
Bei der Produktionserfassung kam es vor, dass trotz
Mengenüberschreitung der ausgewählten Partie die Mengenangabe nicht geprüft
wurde.  Die Mengenprüfung der Komponente mit Partie wird jetzt nach den
Einstellungen in der Vorgangsunterklasse [FRZ] ausgeführt.
Releasenote Kategorie:
Ticket: 713172[32729]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: PROB
Variante: Produktion
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32729, 713172

---

## Produktion: Produktionserfassung

Produktion: Produktionserfassung
Bei der Produktionserfassung war es möglich die Felder
für Menge und Preis vor der Eingabe des Rezeptes zu pflegen. Dies führte zu
falschen Anteilen bei den Komponenten. Die Eingabe von der Menge oder dem Preis
vor Eingabe der Rezeptnummer ist jetzt nicht mehr möglich.
Releasenote Kategorie:
Ticket: 714134[32788]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: PROE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32788, 714134

---

## Produktion: Einfügen und entfernen von Zeilen bei Komponenten

Produktion: Einfügen und entfernen von Zeilen bei Komponenten
Bei der Produktionserfassung/-änderung kam es beim
Einfügen von Leerzeilen zwischen den Komponenten zu langen Wartezeiten. Bei
variablen Rezepten können Komponenten nur noch hinter bestehenden
Komponenten hinzugefügt werden. Bestehende Komponenten können nur noch bei
variablen Rezepten entfernt werden.
Releasenote Kategorie:
Ticket: 714820[32918]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: PROE, PROB
Variante: Produktion
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32918, 714820

---

## Produktion: Darstellung der Eingabemaske

Produktion: Darstellung der Eingabemaske
Die Produktionsmaske wurde für eine Auflösung von 1920
x 1080 Bildpunkte optimiert.
Releasenote Kategorie:
Ticket: 716016[33122]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: PROE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33122, 716016

---

## Produktion: Feld Artikelbezeichnung

Produktion: Feld Artikelbezeichnung
Das Feld Artikelbezeichnung hat jetzt im Standard eine
Länge von 40 Zeichen.
Releasenote Kategorie:
Ticket: 720576[33898]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: PROE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33898, 720576

---

## Rezepturgruppe 0

Rezepturgruppe 0
Es wurde eine Standard-Rezepturgruppe 0 hinzugefügt.
Diese kann ausgewählt werden und wird wie "keine Rezepturgruppe" behandelt.
Releasenote Kategorie:
Ticket: 723257[34134]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Produktionsrezepturen
Variante: Rezepturen
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34134, 723257

---

## Komponenten-Artikelauswahl in Produktionsvorgängen [FRZ]

Komponenten-Artikelauswahl in Produktionsvorgängen [FRZ]
In der Anwendung Formularzuordnung/Vorgangsunterklasse
[FRZ] für Produktionsvorgänge optional eingetragenen Itemboxen (F3-Auswahl) für
Komponenten-Zugangs- und -Abgangsartikel wurden bei der Erfassung und
Bearbeitung von Produktionsvorgängen nicht immer zur Artikelauswahl
herangezogen. Die Ursache für dieses Verhalten wurde nun lokalisiert und
behoben.
Releasenote Kategorie:
Ticket: 734771[35291]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: PROE, PROB
Variante: ALle
Funktion/Report: Erfassung, Bearbeitung
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35291, 734771

---

## Scanner Konfiguration

Scanner Konfiguration
Neue Funktion in der Android-Scannerkonfiguration Ab
sofort ist es möglich, in der Scannerkonfiguration individuelle Einstellungen
pro Scanner und basierend auf dessen Status vorzunehmen. Folgende Optionen
können dabei festgelegt werden: Verwendung der Hardwaretastatur Automatischer
Fokus auf das Eingabefeld Einblenden der On-Screen-Tastatur   Diese
Erweiterung ermöglicht eine noch gezieltere Anpassung des Scannerverhaltens an
unterschiedliche Nutzungsszenarien.
Releasenote Kategorie:
Ticket: 744182[36639]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: SCTCP
Variante: Scanner Konfiguration
Funktion/Report: Scanner
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36639, 744182

---

## Partieauswahl bei Lieferant EK Liste

Partieauswahl bei Lieferant EK Liste
In der Produktion lässt sich nun bei den Komponenten
eine Partie mit F3 (Itembox) auswählen, bei denen im Partiestamm der Lieferant
EK (Liste) eingestellt ist. Der nicht zur Produktion gehört.
Releasenote Kategorie:
Ticket: 733346[36651]
Version: 9.0.2501.5
Datum:
Anwendung: Produktion
Variante: Erfassung
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36651, 733346

---

## Steuerparameter 1046 SPA_TEILPRODUKTION

Steuerparameter 1046 SPA_TEILPRODUKTION
Der Steuerparameter 1046 SPA_TEILPRODUKTION ist in die
Gruppe deaktiviert verschoben worden.
Releasenote Kategorie:
Ticket: 747423[37192]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Steuerparameter
Variante: Steuerparameter
Funktion/Report: Gültigkeiten
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 37192, 747423

---

## Rezepturverwaltung (EPA ARTSTLI)

Rezepturverwaltung (EPA ARTSTLI)
Bezeichnung
Standardwert
Erklärung
Vorbelegung Produktpartie
      anteilig
Nein

---

## MaskenTitel (EPA PRODUKT)

MaskenTitel (EPA PRODUKT)
Bezeichnung
Standardwert
Erklärung
Item
      Box Neuartikel
IB_ARTIKEL_PAR
Diese Itembox wird für die Felder
      der Spalte Komponente aktiv, wenn für die verwendete Rezeptur die
      Einstellung ‚
Variable Komponenten
’ auf Ja
      steht. Dann ist dieses Feld nämlich zur Eingabe weiterer Komponenten
      betretbar.
Lagerplatz und Lagerplatzort durch
      die Bezeichnung auswählbar
Nein
Mengenkontrolle
      an/abschaltbar
Nein
Entscheidet man sich hier für Ja,
      dann ist das Häkchen für ‚
Mengenkontrolle zwischen Produkt und
      Komponenten aktiv
’ editierbar. Bei Nein kann man dieses Häkchen
      nicht verändern.
Mengenkontrolle
      ausschalten
Nein
Hier
      kann man die
Mengenkontrolle
für die
      Korrektur deaktivieren. Damit besteht die Möglichkeit zu verhindern, dass
      sich Werte beim Zufügen einer Komponente unerwünscht ändern.
Mengenübersicht anzeigen
Nein
Man
      kann sich auf der Maske eine Mengenübersicht zur Kontrolle anzeigen
      lassen. Je nachdem, ob man damit arbeiten möchte oder nicht, kann man die
      Anzeige hier aktivieren oder deaktivieren.
Mengenübersicht anstelle der
      Optionbox anzeigen
Nein
Mengenprüfung ja/nein
Nein
Die Menge des Produktes
      und die Menge der Komponenten werden miteinander verglichen. Überschreitet
      z.B. die Komponentenmenge die Produktmenge, dann erhält man beim Verlassen
      der Maske eine Meldung.
Produktpartiemenge überschreibt
      Produktmenge
Nein
Rezeptmengeneinheit
      übernehmen
Nein
Die
      Mengeneinheit der Rezeptur (z.B. Tonnen) wird in das Mengeneinheitsfeld
      des Produktes übernommen. Man kann dann die Produktmenge z.B. in Tonnen
      angeben, obwohl die einzelnen Komponenten die Einheit Kilogramm
      haben.
Maske wird an die in den EPA´s
      eingerichteten Werte angepasst
Nein
Einrichtung: Maskenhöhe (muss größer
      als 47,50 sein)
47.50
Einrichtung: Anzahl Zeilen in
      Datentabelle Kompon
[...]


---

## Produktion (EPA PRODUKTION)

Produktion (EPA PRODUKTION)
Bezeichnung
Standardwert
Erklärung
Addonfeld 1
Addonfeld 2
Format des Addonfeldes 1
Format des Addonfeldes 2
Bezeichnung des Addonfeld
      1
Bezeichnung des Addonfeld
      2
Item
      Box Neuartikel
IB_ARTIKEL_PAR
Prozedur zur Bestimmung des
      Komponentenartikel
AMIC_ProduktionsArtikel
Mengenkontrolle
      an/abschaltbar
Nein
Mengenkontrolle anzeigen
Nein
Mengenprüfung bei der
      Eingabe
Nein
Nachkommastellen im Bestand
      (0,1,2,3,V)
V
Preisfelder sperren
Nein
Feld, das für das Partieabdatum
      genutzt werden soll (leer=Heute)
Feld, das für das Partiebisdatum
      genommen werden soll
neue
      Produktpartienummer = Produktionsnummer
Nein
Produktpartie automatisch
      anlegen
Nein
Rezeptmengeneinheit
      übernehmen
Nein
Vorbelegung des
      Produktlagers
0

---

## MaskenTitel (EPA SVWPAR01_F3)

MaskenTitel (EPA SVWPAR01_F3)
Bezeichnung
Standardwert
Erklärung
F3
      Produktion-Produkt
F3
      bei Produktkomponenten
F3
      bei Schnellkorrektur
F3
      Itembox bei LUM
F3
      beim LUM im Zugang
F3
      im Warenbereich
F3
      bei Waage

---

## Produktion

Produktion
Feld
Beschreibung
Komponentenzeilenprozedur
Im Produktionssystem kann über eine
      Prozedur die automatische Rezeptur-Mengenverteilung der Komponenten mit
      dieser Prozedur übersteuert werden. Als Beispiel wird folgender Prozedur
      mitgeliefert:
create
procedure
ProduktionsZeilen
(
in
in_status_vorgang
integer
,
in
in_produktartikelnummer
char
(
40
),
in_Gesamtmenge
numeric
(
15
,
4
),
in
in_zeile
integer
default
1
,
in
in_artikelId
integer
,
in
in_menge
numeric
(
15
,
4
)
)
result
(
menge
numeric
(
15
,
4
)
)
begin
declare
dc_diesenr
char
(
40
);
if
(
in_status_vorgang
<>
2
)
then
if
(
in_Gesamtmenge
<>
0
)
then
select
first
artikelnummer
into
dc_diesenr
from
artikel
where
artikelid
=
in_artikelid
and
substring
(
artikelnummer
,
2
,
3
)=
substring
(
in_produktartikelnummer
,
2
,
3
);
if
dc_diesenr
is
not
NULL
then
select
5
;
else
select
NULL;
end
if
;
else
select
NULL
from
dummy
where
1
=
2
;
end
if
;
else
select
NULL
from
dummy
where
1
=
2
;
end if;
end
Gridbreite in PIXEL
Die
      Breite der drei Grids in der Produktionserfassungsmaske kann mit diesem
      Wert festgelegt werden, insbesondere kann hierdurch bei großen
      Bildschirmen eine bessere Anzeige der Informationen erreicht
      werden.
Itembox Artikel Zugang
Hier
      kann eine alternative Itembox für die Zugangsartikel hinterlegt werden.
Itembox Artikel Abgang
Hier
      kann eine alternative Itembox für die Abgangsartikel hinterlegt
      werden.
Partie angeben
Ist
      im Komponenten Grid die Partienummer eingebbar? Ja/Nein
Dieses Kennzeichen kann durch die
      Partieführung aus dem Artikel, Tab - Reiter Partie „Behandlungs Kz ausw.“
      mit „Ja“ übersteuert werden.

---

## Produktionsverarbeitung

Produktionsverarbeitung

---

## Produktionsverarbeitung

Produktionsverarbeitung

---

## Produktionsverarbeitung

Produktionsverarbeitung

---

## Produktionsverarbeitung

Produktionsverarbeitung

---

## Produktionsverarbeitung

Produktionsverarbeitung

---

## Teilproduktion (SPA 1046)

Teilproduktion (SPA 1046)
SPA wurde in die Gruppe
deaktiviert verschoben.

---

## Permanente Inventur Bewertungsverhalten (SPA 1083)

Permanente Inventur Bewertungsverhalten (SPA 1083)
Beim Export der Produktion kann hier die Hierarchie
ein wenig flacher gestaltet werden. Wird der Steuerparameter eingestellt, so
wird ein Produkt/Komponentenknoten vervielfältigt, wenn es mehrere Partien gibt,
so dass für jede Partie eine eigene Komponente gibt.
Ohne diese Einstellung wird die Liste der Partien in
jedem Produkt/Komponenten-Knoten dargestellt

---

## Stücklistenverwaltung angeschlossen(SPA 28)

Stücklistenverwaltung angeschlossen(SPA 28)
Steuert das Programmverhalten bei Artikeln mit
hinterlegten Rezepturen. Die Rezepturen werden nur aufgelöst, wenn hier „Ja“
eingetragen ist.

---

## Preisklasse für Komponente + Prod. in Produktion(SPA 286)

Preisklasse für Komponente + Prod. in Produktion(SPA 286)
Dieser Parameter ist nur in Verbindung mit dem
Parameter 285 = Listenpreis aktiv.

---

## Komponentenlagerwahl für Produktion(SPA 302)

Komponentenlagerwahl für Produktion(SPA 302)
Produktion: Legt fest, aus welchem Lager die
Komponenten für eine Rezeptur genommen werden.

---

## Rezeptur-Definition aus Vorgangsbearbeit(SPA 309)

Rezeptur-Definition aus Vorgangsbearbeit(SPA 309)
Noch nicht verfügbar. Reserviert für spätere
Erweiterungen.

---

## Komponentendaten auf Produktionsmaske unveränderbar(SPA 321)

Komponentendaten auf Produktionsmaske unveränderbar(SPA 321)
Falls im Produktionsmodul keine Komponentendaten
während der Erfassung verändert werden dürfen ist hier „Ja“ einzustellen.

---

## Produktion Partiezuordnungszwang Komponenten(SPA 409)

Produktion Partiezuordnungszwang Komponenten(SPA 409)
Nein: In der Produktionserfassung müssen den
Komponenten keine Partie zugeordnet werden.
Artikel mit Partiezwang: Es müssen in der
Produktionserfassung Komponenten, bei denen  das Partiekennzeichen
hinterlegt ist, Partien zugeordnet werden.
Alle Artikel: Es müssen in der Produktionserfassung
für alle Komponenten Partien zugeordnet werden.

---

## Produktion Partiemengenausgleichszwang Komponenten(SPA 410)

Produktion Partiemengenausgleichszwang Komponenten(SPA 410)
Nein: In der Produktionserfassung müssen die Mengen
bei zugeordneten Partien (zu Komponenten) nicht ausgeglichen sein.
Ja: Wenn in der Produktionserfassung Partie (zu
Komponenten) zugeordnet sind, müssen die Mengen ausgeglichen sein.

---

## Produktion Partiemengenausgleichszwang Produkt(SPA 412)

Produktion Partiemengenausgleichszwang Produkt(SPA 412)
Nein: In der Produktionserfassung muss die Menge bei
zugeordneten Partien (zum Produkt) nicht ausgeglichen sein.
Ja: Wenn in der Produktionserfassung eine Partie (zum
Produkt) zugeordnet ist, muss die     Menge ausgeglichen
sein.

---

## Preis aus Partie übernehmen(SPA 415)

Preis aus Partie übernehmen(SPA 415)
Ja: Wenn in der Produktionserfassung einer Komponente
eine Partie zugeordnet wird, erfolgt eine Übernahme des Partiepreises, sofern
der Partiepreis ungleich 0 ist und im zugehörigen Rezept der Bewertungstyp nicht
gleich „2 Produkt anteilgewichtet“ oder „3 Produkt wertgewichtet“ eingestellt
ist.
Nein: Es werden keine Partiepreise übernommen.

---

## Lagerplatzverwaltung auch bei Produktion(SPA 458)

Lagerplatzverwaltung auch bei Produktion(SPA 458)
Mit diesem SPA wird die Lagerplatzeingabe für
Rezeptur, Produkt und Komponenten aktiviert. Wirkt nur bei aktivierter
Lagerplatzverwaltung!

---

## Produktion-Lizenz(SPA 451)

Produktion-Lizenz(SPA 451)
Lizenz für Produktion.

---

## Mengennormalisierung nur in % Rezepturen(SPA 471)

Mengennormalisierung nur in % Rezepturen(SPA 471)
Bei Rezepturen, in denen die Komponenten in
Mengeneinheiten angegeben sind, ist eine Mengennormalisierung nicht nötig bzw.
sogar fehlerhaft. Der Steuerparameter sollte daher immer auf „Ja“ eingestellt
werden. Für die Kompatibilität zu vorhandenen Installationen ist der
Standard-Wert jedoch auf „Nein“ eingestellt. D.h. das Programm arbeitet wie vor
der Umstellung.

---

## Nur n Produktionszugänge pro Vorgang, 0=beliebig?(SPA 491)

Nur n Produktionszugänge pro Vorgang, 0=beliebig?(SPA 491)
Ein Wert ungleich 0 begrenzt die Anzahl der
Produktionszugängen pro Vorgang auf den gewählten Wert. Der Wert 0 steht für
eine unbegrenzte Anzahl.
Eine Trennung der Positionen erfolgt nur bei der
Neuerfassung einer Produktion.

---

## Nur eine Artikelgruppe in Rezeptur?(SPA 492)

Nur eine Artikelgruppe in Rezeptur?(SPA 492)
Ja: Es dürfen in einer Rezeptur nur Artikel aus einer
Artikelgruppe genommen werden.
Nein: Es dürfen in einer Rezeptur Artikel aus mehreren
Artikelgruppen genommen werden.

---

## Produktion Gebindefaktor Warenposition verwend(SPA 600)

Produktion Gebindefaktor Warenposition verwend(SPA 600)
Bei Umrechnung von Gebinden die Faktoren aus der
Warenposition verwenden

---

## Ordersatz mit Stücklistenübernahme(SPA 672)

Ordersatz mit Stücklistenübernahme(SPA 672)
Bei „Ja“ wird die Rezepturgruppe und die
Rezepturvariante aus dem Artikel des Ordersatzes übernommen und es erfolgt
eine Auflösung dieser Stückliste im Zielbeleg.

---

## Produktion Preiseinheiten aus Tabellen(SPA 689)

Produktion Preiseinheiten aus Tabellen(SPA 689)
Dieser Steuerparameter dient als Vorbelegung  im
Pfleger für Rezepturen für das Feld: Preise aus Tabellen.
Wird im Rezept dort  „Ja“ eingestellt,
werden  alle Preise, die nicht aus Bewertungsmethoden kommen, mit ihren
zugehörigen Preiseinheiten und Preismengeneinheiten übernommen.

---

## Produktion Bewertung korrekte Preisumrechnung(SPA 688)

Produktion Bewertung korrekte Preisumrechnung(SPA 688)
Dieser Steuerparameter dient als Vorbelegung im
Pfleger für Rezepturen für das Feld: Korrekte Bewertung.
Wird im Rezept dort  „Ja“ eingestellt, wird eine
korrigierte Fassung der Umrechnung der Bewertungspreise  aktiviert.

---

## AdHoc Updates aktiv (SPA 894)

AdHoc Updates aktiv (SPA 894)
Hier kann für verschiedene Bereiche in Referenz-ERP
festgelegt werden, ob AdHoc-Updates gemacht werden sollen.
Einstellung
Bedeutung
Artikel
Artikelbestände
Objekt
Partiebestände
Kontrakt
Kontraktbestände
Partie
Partiebestände
Produktion
AdHoc-Updates durch Komponenten oder
      Produkte der Produktion
Hinweis:
Bitte beachten Sie, dass diese Steuerungsparameter NUR
verändert werden dürfen, wenn der Mandantenserver alle Belege abgearbeitet hat
und während der Änderung keine neuen Belege entstehen (Betriebsruhe), da sonst
erstellte AdHoc-Updates nicht zurückgesetzt werden und Bestandsangaben falsch
dargestellt werden.

---

## Produktions-Schnellerfassung aktiv(SPA 962)

Produktions-Schneller
fassung aktiv(SPA 962)
Aktiviert  das Modul zur
Produktions-Schnellerfassung, wenn hier „Ja“ eingetragen ist. Die
Standardeinstellung ist „Nein“.
ACHTUNG: Die Schnellerfassung verfügt nicht über den
vollen Leistungsumfang, wie er im Standard-Produktionsmodul mittels der
Direktsprünge PROB und PROE zur Verfügung steht.

---

## Abteilungen

Abteilungen
Zur Pflege von Abteilungen kann in diesem Bereich
Eingaben vorgenommen werden. Abteilungen können im Standardbereich
Vorgangskonstanten zugeordnet werden.
Abteilungen
Hauptmenü
Administration
Abteilungen
Abteilungen
oder Direktsprung
[ABT]
Neue Abteilung mit
F8
anlegen. Abteilungsnummer, Matchcode und
Name sinnvoll vergeben und mit
F9
abspeichern.
Unterabteilungen
Hauptmenü
Administration
Abteilungen
Unterabteilungen
oder Direktsprung
[ABTU]
Neue Unterabteilung mit
F8
anlegen. Nummer für die Unterabteilung
vergeben, Name und Matchcode eintragen und in dem Feld Abteilung mit
F3
die entsprechende Abteilung
zuordnen.
Abteilungs-Gruppen
Hauptmenü
Administration
Abteilungen
Abteilungs-Gruppen
oder Direktsprung
[ABTGR]
Neue Abteilungsgruppe mit
F8
anlegen. Die Nummer wird automatisch
fortlaufend vergeben, wenn eine andere Nummer gewünscht wird, kann diese auch
überschrieben werden. Name entsprechend pflegen.
Artikel/Abteilungen
Hauptmenü
Administration
Abteilungen
Artikel/Abteilungen
oder Direktsprung
[ABTA]
Hier erfolgt mit
F8
die Zuordnung der Abteilung zur
Unterabteilung und zur Abteilungsgruppe. Mit
F3
kann jeweils die entsprechende Auswahl
getroffen werden.
Abteilungszugehörigkeit
Hauptmenü
Administration
Abteilungen
Abteilungszugehörigkeit
oder Direktsprung
[ABTB]
Hier besteht die Möglichkeit einzelne Abteilungen
bestimmte Bedienerklassen zuzuordnen.

---

## Referenz-ERP Sprache

Referenz-ERP Sprache
Hauptmenü
Administration
Werkzeuge
Fremdsprache pflegen
Direktsprung
[SPRA]
In Referenz-ERP existieren verschiedene Sichten der
Sprachdarstellung.
•
Die Sprache in der Referenz-ERP dargestellt wird.
•
Die Sprache in der
die Bezeichnung der Stammdaten
dargestellt wird.
•
Die Sprache, in der Kunden angeschrieben werden (Mahnungen, Rechnungen,
usw...).
Grundsätzlich wird Referenz-ERP in Deutsch - immer
Sprachnummer 0 - entwickelt. Diese Sprachnummer hat nichts mit der Sprachnummer
im Sprachestamm zu tun, sondern wird separat im Stammdatenpfleger Sprachtexte in
der Variante „Referenz-ERP Sprache“ gepflegt. Die hier vorhandenen Sprachen werden nur
von Branchen-ERP festgelegt. Bisher sind folgende Sprachen vorgesehen:
Nummer
Bezeichnung
ISO 639-1
ISO 639-2
Lizenz
0
Deutsch
de
deu
Nein
1
Englisch
en
eng
Ja
2
Dänisch
da
dan
Ja
3
Polnisch
pl
pol
Nein
4
Niederländisch
nl
nld
Ja
5
Französisch
fr
fre
Ja
6
Ungarisch
hu
hun
Nein
7
Italienisch
it
ita
Nein
8
Spanisch
es
spa
Nein
9
Portugiesisch
pt
por
Nein
10
Tschechisch
cs
ces
Nein
11
Slowakisch
sk
slk
Nein
Bisher kann für die Sprachen Englisch, Dänisch,
Niederländisch und Französisch eine Lizenz erworben werden. Bei der ersten
Verwendung der Sprache kann eine 60-Tage Lizenz freigeschaltet werden.
Spätestens nach 60 Tagen muss dann die echte Lizenz erworben werden.
Hinweis:
7 Tage vor Ablauf der 60-Tage Lizenz erscheint beim
Start von Referenz-ERP ein Hinweis auf dem Informationsbildschirm.
Um Referenz-ERP in einer anderen Sprache als Deutsch
darzustellen sind zwei Einstellungen notwendig.
•
Der Steuerparameter (Direktsprung
[SPA]
) „
Mehrsprachigkeit aktiv
“ muss
auf
Ja
stehen.
•
Im
Bedienerstamm
(Direktsprung
[BD]
) muss die
Sprache, in der Referenz-ERP ausgeführt werden soll, für den einzelnen Bediener
hinterlegt werden.
Das Erscheinungsbild von Referenz-ERP ist also
Bedienerabhängig, d.h. auf einer Datenbank kann gleichzeitig in
unterschiedlichen Sprachvarianten gearbeitet werden. Wenn man im Bedienerstamm
das erste Mal eine der Lizenzabhängigen Spra
[...]


---

## Akt. Komponente Partieverteilung F6

Akt. Komponente Partieverteilung F6
Es öffnet sich die Partieverteilung für die in der
Erfassungsmaske aktuell angewählte Komponente. Es können die gewünschten Partien
hinterlegt werden. Genau eine ausgewählte Partie wird in der Spalte Partie in
der Erfassungsmaske für die Komponente angezeigt. Bei mehreren Partien pro
Komponente wird nur die erste Partie in der Spalte Partie angezeigt. Im
Informationsfeld unten links auf der Maske steht aber wie viele und welche
Partien zugeordnet sind.

---

## Aktuelle Komponente Partieverteilung

Aktuelle Komponente Partieverteilung
Diese Funktion erlaubt nur Partieverteilung der
ausgewählten (Cursorposition) Komponente. Ein Wechseln der Komponenten ist im
Untermenü dann nicht mehr möglich.

---

## Rollenantrag

Rollenantrag
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenantrag
oder Direktsprung
[ZUGA]
Innerhalb der
Rollenkontexte
können Anträge auf Rollenänderungen
gestellt werden.
Hier können diese Anträge nun freigeschaltet,
verworfen und ggf. vermailt werden.
Es ist kein Auswahl-Bereich vorgesehen.
Felder:
Felder
Rolle
Die
Rolle
für die eine
      Änderung beantragt wird.
Rollenantrag
Die
      Rolle die beantragt wird.
Alle
      Kontexte?
JA/NEIN
Informatorisch ob die Änderung
      zusätzlich zum Rollenkontext alle Kontexte betrifft oder nur den
      übermittelten.
Funktion
Funktion des
      Rollenkontextes.
Kontext
Kontext des
      Rollenkontextes.
Beschriftung
Informatorische Beschriftung der
      Funktion.
Funktionsart
Informatorische Funktionsart der
      Funktion.
Kurzname
Der
      Antragssteller.
Rollenantrag vom
Zeitpunkt der
      Antragstellung.
Die
      Auswahlliste ist absteigend nach diesem Kriterium sortiert.
gewähren
Listet die Bedienerklassen auf,
      denen ein Zugriffsecht eingeräumt würde.
entziehen
Listet die Bedienerklassen auf,
      denen ein Zugriffsrecht entzogen würde.
Mail
      am
Zeitpunkt der
      Antrags-Mailzustellung
Funktionen:
Funktionen
Antrag genehmigen (F9)
Führt ohne weitere Abfrage die
      Genehmigung des Antrages durch.
Antrag löschen (F7)
Führt ohne weitere Abfrage die
      Stornierung des Antrages durch.
Antrag versenden (F10)
Versendet die ausgewählten Anträge
      an die dafür vorgesehenen Empfänger.
Die
      Anträge werden gerafft, d.h. es werden z.B. 4 Einträge in einer Mail
      tabellarisch zusammengefasst.

---

## Archiv-Ansichten definieren

Archiv-Ansichten definieren
Hauptmenü
Administration
Archiv
Zugriffssteuerung
Direktsprung
[FAA]
In dieser administrativen Anwendung „
Archiv
Ansichten
“ werden die
Archiv-Ansichten
gepflegt.
Dazu stehen folgende Varianten zur Verfügung:
•
Archiv-Ansichten-Variante: Ansichten
•
Archiv-Ansichten-Variante: Ansichten – Vorkommen
•
Archiv-Ansichten-Variante: Ansichten – Detailvorkommen
•
Archiv-Ansichten-Variante: Ansichten – Richtlinien
Neben den üblichen Pflege-Funktionen stehen folgende
Spezial-Funktionen bereit:
Details …
F5
Wechselt in die
      Archiv-Ansichten-Details.
Ansichten
      Details
Duplizieren
Dupliziert eine
      Archiv-Ansichts-Definition samt ihrer Details.
Dabei wird vorher eine
      Bedienerklasse abgefragt, die dem Duplikat dann zugewiesen
      wird.
Die
      Bedienerklasse -1 bedeutet „alle Bedienerklassen“.
Das Duplikat ist in jedem Fall eine
      Archiv-Ansichts-Definition die Besitzer „Privat“ hat.
Export
Exportiert eine
      Archiv-Ansichten-Definition.

---

## Archiv-Ansichten-Variante: Ansichten – Vorkommen

Archiv-Ansichten-Variante:
Ansichten – Vorkommen
Hauptmenü
Administration
Archiv
Zugriffssteuerung
Ansichten - Vorkommen
Direktsprung
[FAA]
In dieser administrativen Variante „
Ansichten -
Vorkommen
“ werden die technischen Aufrufe der Archiv-Ansichten innerhalb von
Referenz-ERP offengelegt.
Sie verschafft eine Übersicht darüber, in welcher
Optionbox (der dazugehörigen Anwendung bzw. Variante) sich welcher Aufruf
welcher Archiv-Ansicht verbirgt.
Felder
Funktion
Funktions-Identifikation
Beschriftung
Beschriftung
Optionbox
Optionbox innerhalb der sich die
      Funktion befindet
Zugehörige Anwendung
Ermittlung der Anwendung des
      Kontextes
bzw.
      Variante
Ermittlung der Variante des
      Kontextes
Ausliefer-Grundlage
Mögliche Einsatzgebiete:
1)   Dialog
2)
      Auswahlliste
3)   Frei
4)   Keine
      Angabe
Ansicht
Der
      Name der Archiv-Ansicht
EA
Gruppe
Siehe Gruppe
Taste
Die
      zugeordnete Funktionstaste im Kontext.
Standard ist
CF12
.
SteuPa
Steuerparameter
Lizenzspa für Archiv ist SPA
      508
Suchen
Suchen …
Sucht in den Feldern
Funktion, Beschriftung, Optionbox,
      „Zugehörige Anwendung“, „bzw. Variante“ , Ansicht
Funktionen
Funktion ansehen/bearbeiten
F11
Funktion bearbeiten
Ansicht ansehen
F6
Archiv-Ansichtsdefinition
      ansehen
Ansicht
      bearbeiten
F5
Archiv-Ansichtsdefinition
      bearbeiten
Funktion
      Informationen
F9
Funktionsinformationen
Kontext …
Optionbox-Pfleger
(nur
      für Entwicklung)
Starte Anwendung …
Startet die Anwendung
(nur
      für Entwicklung)

---

## Archiv-Ansichten-Variante: Ansichten – Detailvorkommen

Archiv-Ansichten-Variante: Ansichten – Detailvorkommen
Hauptmenü
Administration
Archiv
Zugriffssteuerung
Ansichten - Detailvorkommen
Direktsprung
[FAA]
In dieser administrativen Variante „
Ansichten -
Dateilvorkommen
“ werden die Details der
Archiv-Ansichten
aufgelistet.

---

## Archiv-Dokumenten-Import

Archiv-Dokumenten-Import
Hauptmenü
Administration
Archiv
Importverwaltung
Direktsprung
[FAI]
Hier werden die Dokumenten-Importe verwaltet. Ein
Dokumenten-Import wird durch ein Import-Profil beschrieben.
Felder
Name
Eindeutiger Name des
      Dokumenten-Import-Profils
(mögliche Farbgebungen siehe
      „Ziel-Datenbank-Name“)
Automatik
Bei
      Einstellung
Ja
übernimmt der Mandantenserver den Import
Ident
Ident des Imports
Zusammen mit der Bedienerklasse ist
      der technische Schlüssel gegeben.
Bedienerklasse
-1
      ist die sogenannte „Defaultklasse Kunden“, das bedeutet das keine
      spezielle Bedienerklasseneinschränkung vorhanden ist.
-1
      ist der Standard.
Referenz-ERP verwendet für interne Zwecke
      (z.B. Archiv-Ansichten) auch andere Bedienerklassen
Bedienerklassenbezeichnung
Bezeichnung der
      Bedienerklasse
Weitere Elemente …
Import-Datenbank-Name
Der
      Datenbank-Datei-Name gegen den der Import prüfen soll, ob der „richtige“
      Mandant vorliegt.
Durch Duplikate der Datenbank kann
      es leicht passieren, dass der Import Dateien aus Verzeichnissen
      importiert, die ausschließlich dem Original-Mandanten vorbehalten sind.
      Deshalb wird nun geprüft, ob der Datenbank-Datei-Name des Mandanten der
      den Import ausführt mit „Ziel-Datenbank-Namen“ übereinstimmt.
Ist
      eine Differenz festzustellen wird der „Name“ gelb eingefärbt, ist
      zusätzlich die Automatik aktiviert, dann wird der „Name“ rot eingefärbt.
      Diese Farbgebungen dienen lediglich der Information. Importe führt das
      System nicht aus.
Wartezeit in Minuten
Es
      existieren Scanner-Systeme die ihr Erzeugnis in mehreren Schritten
      erzeugen. Um diese „Reifezeit“ von Referenz-ERP zu unterstützen gibt es hier die
      Möglichkeit eine Wartezeit in Minuten anzugeben, bevor das
      Referenz-ERP-Archiv-Import-System die Datei verarbeitet.
Max.
      Anzahl pro Durchlauf
Da
      je nach Dateiaufkommen und -größe der allgemeine Mandantenserve
[...]


---

## Archiv-Import über JPP-Methode JVAR_IMPORT aus JFA_Import

Archiv-Import über JPP-Methode JVAR_IMPORT aus JFA_Import
Diese Methode wird u.a. im Hinzufügen-Dialog als
Basis-Methode des Archivs eingesetzt. Als JPP-Methode steht sie GUI-los auch zum
Costumizing bereit.
Diese Methode wird im Rahmen des Integrationstestes
amic_test_jarchivexport_tofile verwendet.
Parameter:
Owner
Pflichtfeld
Gibt
      den JVAR-Owner vor, in dem die folgenden dynamischen Parameter gesucht
      werden.
$file
Pflichtfeld
Dateipfad
$delete
Optional
Löschen der Datei nach
      Import
Standard 0 = Nein
fa_mandant
Optional
fa_kundenummer
Optional
fa_belegtyptext
Optional
fa_belegnummer
Optional
fa_belegreferenz
Optional
fa_info_autor
Optional
fa_info_betreff
Optional
fa_info_kategorie
Optional
fa_info_stichwoerter
Optional
fa_info_kommentar
Optional
fa_info_titel
Optional
fa_belegdatum
Optional
fa_mndnr
Optional
fa_barcode
Optional
fa_klasse
Optional
Standard ist 0
fa_belegklasse
Optional
Standard ist 0
fa_bedienerklasse
Optional
Standard ist die Bedienerklasse des
      ausführenden Users
Bei erfolgreicher Archivierung befindet sich
systemüblich in
5000
JVARS_LAST_FA_ID
5000
JVARS_LAST_FA_MNDNR
der Primary-Key des hinzugefügten Archiv-Dokuments der
Relation Formulararchiv.

---

## Auswertung (Produktion)

Auswertung (Produktion)
Nach Mandantenserver erfolgt Bestandsmehrung auf
Produkt, Bestandsminderung auf Komponente. In der Relation ARTISUMMEN werden die
produzierten Mengen und Werte (Produkt) sowie die verwendeten Mengen und Werte
(Komponente) je Periode getrennt aufsummiert.
Die Zuordnung erfolgt hier zu interner Zugang bzw.
interner Abgang. Siehe hierzu die Auswertungsmöglichkeiten von Produktion als
Perioden-Erfolgsauswertung.

---

## Bearbeitungsmaske Kopfdaten

Bearbeitungsmaske Kopfdaten
Die im Kopf der Maske stehenden Felder im Einzelnen:
Typ
Der Typ gibt die Herkunft der Griddefinition an.
Mögliche Konfigurationen:
•
System (vom Entwickler vorgegeben) – Diese Einstellungen sind vom
Anwender nicht zu ändern.
•
Anwender – Diese Einstellungen/Konfigurationen sind vom Anwender selbst
erstellt worden
Name
Der Name der Griddefinition. Bei der Erstellung wählen
Sie bitte einen Namen, anhand dessen sich die Definition leicht identifizieren
und von anderen unterscheiden lässt.
Beschreibung
Hier ist der Platz für eine genauere Beschreibung für
den Verwendungszweck der Griddefinition
SystemSQL
Das System-SQL beschreibt den Aufbau der Daten in dem
Grid mit einem vom Entwickler vorgegebenen SQL-Befehl. Der Name des hinterlegten
SQL-Befehls muss mit „g_“ beginnen.
Dieses SQL ist vom Anwender nicht editierbar.
Beispiel:
// SQLK TEXT für Griddefinition
wohnung_jdb
select w.*,k.kundnummer, a.AdressVorname || ' ' ||
a.Adressname as Name
:USER_FIELDS
from wohnungjdb as w
left outer join kundenstamm k on (k.kundid = w.kundid
)
left outer join AnschriftStamm a on (k.AdressIdHauptAdr
= a.AdressId)
:USER_JOINS
where w.Hausident =
:HAUSIDENT
UserSQL
Das User-SQL erweitert das vorgegebene System-SQL um
weitere vom Anwender gewünschte Felder. Der Name des SQL-Befehls muss mit „g_“
beginnen und auf „_p“ enden. Das System-SQL muss die Variablen „:USER_FIELDS“
und „:USER_JOINS“ enthalten, damit die Einträge des UserSQL berücksichtigt
werden können.

---

## Variante „Besondere Systemordner“

Variante „Besondere Systemordner“
Hauptmenü
Administration
Werkzeuge
Besondere Systemordner
Direktsprung
[
BESY
]
Mit Hilfe dieser Variante lassen sich die besonderen
Systemordner des Referenz-ERP-Clients anzeigen.
Besondere Systemordner sind Ordner wie Programme
(im Windows-Verzeichnis), Programme (im Startmenü), System oder Autostart, die
allgemeine Informationen enthalten. Besondere Ordner werden in der
Standardeinstellung vom System festgelegt, oder sie werden vom Benutzer bei der
Windows-Installation festgelegt.
Felder
Auswahlliste
Name
Logischer Name des
      Verzeichnisses
Die
      besonderen Systemordner sind von Microsoft vorgeben und
dokumentiert
.
Verzeichnis
Das
      resultierende Verzeichnis auf dem laufenden Referenz-ERP-Client.
Auswahlbedingungen
Finden
Führt eine Like-Suche in den Feldern
      Name und Verzeichnis durch
Funktionen
Besonderen Systemordner
      öffnen[F10]
Öffnet den besonderen Systemordner
      im Windows-Explorer

---

## Einfügen

Einfügen
Seiten:
Funktion
Beschreibung
Leere Seite
Fügt
      eine Leere Seite ein
Seitenumbruch
Setzt einen Seitenumbruch an die
      gewünschte Zeile
Tabellen:
Funktion
Beschreibung
Tabelle
Fügt
      eine Tabelle mit der gewünschten Dimension ein
Illustrationen:
Funktion
Beschreibung
Bild
Öffnet einen Dialog zum auswählen
      eines Bildes
Setzt einen Paltzhalter, welcher
      später über Referenz-ERP gefüllt warden kann
Diagram
Spalte
Linie
Kreis
Balken
Fläche
Punkt
Kurs
Netz
Form
Linien
Rechtecke
Standardformen
Blockpfeile
Formelform
Flussdiagramm
Sterne und Banner
Legenden
Bereich erstellen
Bereiche ein/ausblenden
Strichcode
Anleitung zum
      Dynamischen laden eines QR-Codes in Referenz-ERP
QRCode
Bis zu 1270 ASCII-Werte oder 1850
            alphanumerische Werte
Code128
EAN13
13 Ziffern
UPCA
12 Ziffern
EAN8
8 Ziffern
Interleaved2of5
nur Ziffern
Postnet
Postleitzahlen
Code39
Alphanumerische Werte
AztecCode
bis zu 1300 ASCII-Zeichen
IntelligentMail
Postleitzahlen (Nachfolger von
          Postnet)
Datamatrix
Bis zu 1301 ASCII-Zeichen
PDF417
Bis zu 1500 ASCII-Zeichen
MicroPDF
Bis zu 250 ASCII-Zeichen
Codabar
Ziffern und die Zeichen
-
,
$
,
:
,
/
,
.
und
+
Fourstate
8 Zeichen
Code11
Bis zu 50 Ziffern
Code93
Alphanumerische Werte und die Zeichen
-
,
$
,
:
,
/
,
.
und
+
PLANET
Ziffern
RoyalMail
Alphanumerische Werte und die Zeichen
(
und
)
Maxicode
Zeichenfolgen (wird vom United Parcel
            Service verwendet)
Hyperlinks:
Funktion
Beschreibung
Hyperlink
Fügt
      einen Hyperlink ein.
Textmarke
Einfügen
Bearbeiten
Löschen
Anzeigen
Kopf- und Fußzeilen:
Funktion
Beschreibung
Kopfzeile
Lässt die Kopfzeile
      bearbeiten
Fußzeile
Lässt die Fußzeile
      bearbeiten
Seitezahl
Kann
      im Bearbeitungsmodus der Fußzeile hinzugefügt warden
Text:
Funktion
Beschreibung
Textrahmen
Erstellt einen
      Textrahmen
Datei
Öffnet die angegebene Datei und fügt
      den enthaltenen Text ein
Symbol:
Fügt das gewünschte Symbol ein.

---

## QR-Code Beispiele zum dynamischen Laden

QR-Code Beispiele zum dynamischen Laden
Neben den üblichen Textgestaltungsmöglichkeiten lassen
sich über die Punkte „Einfügen“ („Illustrationen“) mit „Bild“ und „Strichcode“
jeweils statische Elemente integrieren.
Für „Bild“ siehe „Bild…“.
Für „Strichcode“ siehe im Kontext-Menü „Formatieren…“
und dort unter „Strichcode Layout“ im Register „Typ und Farbe“ und da unter
„Typ“ die Elemente „Kodierung“ und „Text“.
Im Zusammenhang mit einer geeigneten privaten
Datenbank-Routine lässt sich der Strichcode „dynamisieren“. Zum Zeitpunkt der
Druckaufbereitung wird die Datenbank-Routine mit der WabewId der zugehörenden
Warenpositionszeile aufgerufen. Anhand dieser kann dann ein Text für den
Strichpunkt aufbereitet und zurückgegeben werden.
Aktiviert wird diese Mechanik durch eintragen des
Namens der Strichcode-Datenbank-Routine im Element „Text“
Zu beachten ist die Konvention das eine solche Routine
den Prefix „p_“ hat, also zum Beispiel: p_Barcode
Beispiel für eine solche
Strichcode-Datenbank-Routine:
---<summary>Ermittelt aus
der WabewId den zugehörigen Artikel-Code und gibt den Code-Typen
bekannt</summary>
---<param
name="in_wabewid">wabewid</param>
---<returns>
---code    : der zugeordnete Code
---codetyp : der zugeordnete Codetyp
---</returns>
Create
Procedure
p_Barcode
(
in
in_wabewid
integer
)
Result
(
code long
varchar
,
codetype
char
(
32
)
)
Begin
select
'Democode für QrCode-Beispiel'
||
', wabewid='
||
in_wabewid
as
code
,
'QrCode'
as
codetype
End

---

## Druckerstamm

Druckerstamm
Hauptmenü
Administration
Drucker
Druckerstamm
oder Direktsprung
[DRST]
In dieser Variante können Referenz-ERP-Drucker definiert
werden.
Felder des Druckerstamm:
Felder
Beschreibung
D
Es
      kann einen Drucker mit „*“-Kennzeichnung geben. Es handelt sich dann um
      den als Default-Drucker bezeichneten Standard-Referenz-ERP-Drucker.
Dieser Drucker wird auch im
      Hauptmenü angezeigt.
Druckernummer
Laufende Druckernummer
Bezeichnung
Druckerbezeichnung
Queue / Datei
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
Druckertyp
Referenz-ERP-Druckertyp
Einrichtung erfolgt über
      Direktsprung
[DRT]
Kurzname
Alphanumerischer Code zur
      Identifizierung eines Druckers
Windows (Druck)
Ja:
      Windows Drucker
Nein: ASCII-Drucker
Senden An
Ja:
      Drucker unterstützt direkt „Senden An“-Funktionalität des
      Archives.
Nein: Keine Wirkung.
Senden An-Funktion
Senden-An und Nulldrucker zur
      Laufzeit per Funktion bestätigen
Archiv aus
Ja:
      Auch wenn eine Archivierung durchgeführt werden würde findet sie nicht
      statt!
Nein: Keine Wirkung
Nulldrucker
Ja:
      Der Drucker wird zur Druckaufbereitung herangezogen aber es erfolgt kein
      Abschluss der Druckerwarteschlange, d.h. in der Praxis „es erfolgt kein
      Druck“
Nein: Keine Wirkung
Bemerkung
Ergänzende
      Informationen.
Suchmöglichkeiten des Druckerstamm
Suchen
Beschreibung
Druckernummer ab
Bereich von
      Druckernummern
Bezeichnung wie
Filtert nach Kriterium
Bemerkung wie
Filtert nach Kriterium
Funktionen des Druckerstamm
Es stehen neben Pflege-Funktionen folgende weitere
Funktionen zur Verfügung:
Funktionen
Beschreibung
Standa
[...]


---

## Druckertypen

Druckertypen
Hauptmenü
Administration
Druckertypen
oder Direktsprung
[DRT]
Beim Druckertyp werden die Steuerzeichen für die ASCII
– Ansteuerung der Drucker hinterlegt.
In der Basis-DB sind folgende Typen eingerichtet:
•
OKI 320 Nadeldrucker
•
HP- Laser

---

## Einrichtungen

Einrichtungen
Folgende Punkte müssen eingerichtet werden, bevor man
mit der Produktionserfassung beginnen kann.

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

## Beispiele für eine NzuM-Produktion

Beispiele für eine NzuM-Produktion
Erster Schritt für alle Beispiele ist das Anlegen
einer Rezepturgruppe 36000 für Bier unter
[REZG]:

---

## Konfiguration

Konfiguration
Scanner
:
Um eine Verbindung zu dem Rechner herzustellen, auf
dem die PC Software installiert wurde gehen Sie nun wie folgt vor:
Klicken Sie auf dem Desktop des Scanners auf
„
MyDevice
“, anschließend auf „
Program Files
“, „
mde
“ und
starten das Konfigurationstool über die
MultiLinkIP.exe
Datei.
Feld
Funktion
Dropdown-Menü
Auswahl der
      Verbindungsdaten
Großer, leerer Knopf
      dahinter
Öffnet Eingabe für die Namen oder IP
      des Rechners, zu dem verbunden werden soll.
-
Eingeben und
      anschließend OK klicken
:
      Zahl
Angabe des zu verwendenden Ports
      8591
Knopf „Add“
Die
      Angaben auf dem großen Knopf und des Ports werden zusammengeführt und in
      die Liste zur Auswahl im Dropdown-Menü hinzugefügt.
Test
Testet die ausgewählte
      Verbindung.
Write
Erzeugt einen Eintrag in den
      Einstellungen des Scanner-Programms für den ausgewählten
      Rechner.
Quit
Verlassen des Programms
Nach dem Start des Konfigurationstools klicken Sie auf
den großen, leeren Knopf. Ein Eingabebereich wird geöffnet und Sie tragen den
Namen des Zielrechners ein. Bestätigen Sie die Eingabe mit Ok rechts unten. Der
verwendete Port ist 8591. Mit einem Klick auf den Knopf „Add“ werden die Daten
in das Programm übernommen. Nun wählen Sie die neue Verbindung oben aus und
klicken anschließend auf den Knopf „Write“ um die Konfiguration
abzuschließen.
Die Scanner-IP muss anschließend in die Datei
ScannerIP.txt eingetragen werden. Diese befindet sich unter
MyDevice,
Application, mde.
Öffnen Sie diese Datei mit dem Editor oder einem ähnlichen
Programm, tragen die Scanner-IP ein und speichern Sie die Datei.
Starten Sie das Programm
Multilink.exe
auf
Ihrem Rechner aus dem Verzeichnis
Program Files
. Sie sehen nun das Log.
Oben befinden sich die Menüs Datei, Einstellungen, Log und Info.
Zum Konfigurieren der Software wählen Sie hier das
Menü Einstellungen, PlugIn Einstellungen und GenericDatabase aus.
Die Konfiguration kann bequem
[...]


---

## Sonderfall Produktionsauftrag (PO)

Sonderfall
Produktionsauftrag (PO)
Der Standard openTRANS ist für den Austausch von
Handelsvorgängen vorgesehen. Ein Produktionsauftrag gehört nicht zu dem Umfang
des Standards.
Da Referenz-ERP diesen Prozess jedoch abbilden sollte, ist
ein Protokoll zum Austausch von Produktionsaufträgen und Status erschaffen
worden, der sich im Wesentlichen an dem bestehenden der openTRANS®-Struktur
ORDER orientiert, jedoch zur Unterscheidung „PROD_ORDER“ (kurz PO) genannt wird.
Einrichtung Produktionsauftrag
SPA 850 und die Formularzuordnung
Da mit Steuerparameter
Steuerparameter 850 – Belegänderungssperre durch Beteiligung
von openTRANS
die Einstellungsmöglichkeit besteht, Belege gegen
Bearbeitung zu sperren, für die bereits ein openTRANS erstellt worden ist, kann
in der
Formularzuordnung auf der
Registerkarte SPA
diese Sperre abgeschaltet werden. Dies wird für die
Vorgangsklasse 5220 (Produktion) empfohlen.
Prozeduren
Auf der
Registerkarte openTRANS (OT) in der Formularzuordnung
sind eine Reihe spezifischer Einstellungen für die Vorgangsklasse 5220
(Produktion) einzurichten.
OpenTRANS ist zu aktivieren und es sind diverse
Prozeduren zur Ermittlung Produktionsspezifischer Daten individuell
einzurichten. Diese hier aufzuzählen käme der Beschreibung eines
Individualfalles gleich, der bei Neueinrichtung sicher nicht vorliegt.
Als Beispiel seien jedoch UDX, Partie-Details,
Item-Features, Umschlüsselungen und Dateinamen genannt.
Kopfinformationen
Kopfinformationen eines Produktionsauftrages werden im
PO-Header eingetragen.
Einige der Informationen lassen sich in das PO-Format
einfügen, andere werden in den UDX-Header übernommen.
Kopfinformationen im
      UDX-Header
Bestellnummer KWS
UDX_HEADER/UDX.PROD_ORDER_NO
Positionsnummer KWS
UDX_HEADER/UDX.PROD_ORDER_POS
Status
UDX_HEADER/UDX.STATE
Vorgangstexte
UDX_HEADER/UDX.TEXT
Liste der Vorgangstexte
UDX_HEADER/UDX.TEXT/UDX.TEXT
      Sequence=(1….n)
Produktionsart
UDX_OPERATION
Beispiel:
Eine vom Auftraggeber an den Auftrag
[...]


---

## Die Anwendung “JVARS”

Die Anwendung “JVARS”
Administration
Werkzeuge
oder Direktsprung
[
JVARS
]
JVARS sind zur Laufzeit existierende Speicherinhalte,
die somit nur auf dem aktiven Client existieren und erst einmal per Se keinen
Datenbankbezug haben.
Felder
Beschreibung
Bereich
Die
      Owner von JVARS sind in folgende Bereiche aufgeteilt:
Papierkorb
(0): Spezial-JVar. Sie wird vom
      Basissystem für kurzfristige Speicherungen verwendet. Eine eigene
      Verwendung ist nicht vorgesehen!
Branchen-ERP
(1 bis 9999): Branchen-ERP-JVars,
Schreibzugriffe sollten vermieden werden
Beschreibung einiger
      ausgewählter JVARS
Anwender/Support
(10000 bis 19999): Private JVARS:
      Diese JVars werden vom Programm nicht verwendet. Diese JVARS können
eigenverantwortlich
gewählt und verwendet werden.
Programm/Laufzeit
(ab 20000): normale JVars zur
      Laufzeit, also solchen die die API-Funktionen zur Gewinnung einer JVAR
      verwenden.
Owner
Eine
      ganzzahlige Zahl >= 0
Jeder Laufzeit-Instanz einer Maske
      wird ein Owner zugeordnet.
Der
      Owner der aktiv war zum Zeitpunkt des Aufrufs dieser Anwendung JVARS wird
grün
dargestellt.
JVar
Ein
      alphanumerischer Schlüsselbegriff der eine JVAR bezeichnet, innerhalb
      eines Owners sind diese eindeutig!
Die
      JVARS des Owners 3561 werden
gelb
dargestellt.
Wert
Ein
      alphanumerischer Wert
Felder
Beschreibung
Owner
Numerisch, von – bis
Name
Like
Wert
Like
Felder
Beschreibung
hexadezimale
      Debuganzeige
Erlaubt die hexadezimale
      Speicher-Einsicht eines JVAR-Wertes
Beispiel:
73 65
      6C 65 63 74 20 6F  62 2E 61 6E 77 66 75 6E  select
      ob.anwfun
6B 69
      64 2C 20 6F 62 2E  6F 70 74 62 6F 78 69 64  kid,
      ob.optboxid
2C 20
      69 66 20 27 4F 42  5F 6A 76 61 72 73 27 20  , if 'OB_jvars'
3D 20
      6F 62 2E 6F 70 …
Stack-Anzeige
Jede
      JVAR ist intern als Stack aufgebaut, kann also mehrere Werte
      verwalten.
Beispiel für eine JVAR mit mehr als
      einem Eintrag im Stack:
<stackdump
[...]


---

## Komponenten Partieverteilung

Komponenten Partieverteilung
Über diese Funktion kann die jeweilige Komponente den
einzelnen Partien entnommen werden.
Anfangs wird die gesamte Menge der ersten Komponente
vorgeschlagen. Über die Pfeiltasten (<<, <, >, >>) ist ein
Wechsel zwischen den Komponenten möglich. Diese Menge wird nun in einzelne
Partieteilmengen aufgeteilt. Die „Summe“ ist das Ergebnis der Erfassung, „Soll“
ist die Gesamtmenge dieser Komponente und „Rest“ ist die Differenz daraus.
Nachdem die Mengen aufgeteilt wurden, werden diese
Teilmengen den jeweiligen Partien zugeordnet. Über
Partieauswahl
F5
wird für die Menge (Cursorposition) eine
Partie ausgewählt.
Das Einrichten einer neuen Partie bei der
Komponentenauswahl ist nicht möglich. Nach erfolgreicher Partieauswahl
erscheinen diese Partien dann im Fenster „Mengen/Partieaufteilung“
.
Diese Aufteilung der Komponenten wird ebenfalls in
Fenster „Produktion“ übernommen.

---

## Komponenten Partieverteilung F5

Komponenten Partieverteilung F5
Es öffnet sich die Partieverteilung für alle
Komponenten. Im unteren Gitter wählt man die gewünschte Komponente aus für die
man Partien festlegen will. Im oberen Bereich können dann die gewünschten
Partien für die angewählte Komponente hinterlegt werden.
Genau eine
ausgewählte Partie wird in der Spalte Partie in der Erfassungsmaske für die
Komponente angezeigt. Bei mehreren Partien pro Komponente wird nur die erste
Partie in der Spalte Partie angezeigt. Im Informationsfeld unten links auf der
Maske steht aber wie viele und welche Partien zugeordnet sind.
In der Spalte
PM erscheinen bei Zuordnung einer Partie folgende Zeichen
*
dafür, dass eine Partie angegeben wurde
!
          für

---

## Ladeträgerzuordnung in der Produktion

Ladeträgerzuordnung in der Produktion
Mit der Funktion Ladeträgerzuordnung in der Produktion
können nachträglich dem Produkt und den einzelnen Komponenten einer Produktion /
Vermahlung Ladeträger zugewiesen werden.
Achtung:
Die N zu M Produktion wird in
diesem Modul nicht unterstützt.
Voraussetzungen:
1.
In dem
Lagerstamm
muss an den
jeweiligen Lägern ein Kunde hinterlegt sein.
2.
Es müssen
Waagenprofile
für
den
Produktionszugang
sowie für
den
Produktionsabgang
angelegt
werden.
3.
Der Steuerparameter
Lagerverwaltungssystem 636
muss auf Ja gestellt
sein.
Funktionsweise des Moduls:
In der ersten Zeile des Grids wird entweder das
Produkt oder der Ausgangsartikel einer Vermahlung dargestellt. Alle weiteren
Zeilen sind die Komponenten der Produktion / Vermahlung. Hier besteht die
Möglichkeit jeder Position ein Ladeträger zuzuordnen. Mit der Funktionalität
„Starte Zuordnung“ werden die zugeordneten Ladeträger mit den Positionsdaten
bebucht.
Löschen /
Einfügen von im Grid
Es können keine „Stamm“ Positionen aus dem Grid
gelöscht werden. Bei aufgeteilten Positionen kann nur die angefügte Position
gelöscht werden. Des Weiteren ist das Einfügen von neuen Positionen nicht
möglich.
Position
Aufteilen
Es besteht die Möglichkeit eine Produktionsposition
auf mehrere Ladeträger aufzuteilen. Dazu wird die neue Menge in die zu teilende
Position eingetragen. Das Programm legt dann automatisch eine neue Position des
gleichen Artikels mit der Differenzmenge an. Diese Position kann dann mit
„STRG-SHIFT-ENTF“ wieder gelöscht werden. Die Differenz wird dann automatisch
wieder auf die eigentliche Position addiert.
Buchen von
Position in das Lagerverwaltungssystem
Das Buchen der einzelnen Position in das
Lagerverwaltungssystem übernimmt die
Waage
. Beim Ausführen der Funktion „Starte
Zuordnung“ wird für jede Position die eine Ladeträgerzuordnung hat, ein neuer
Waagensatz
mit den jeweiligen
Informationen der Position angelegt. Dieser Waagesatz wird automatis
[...]


---

## Materialverbrauch Produktion

Materialverbrauch Produktion
Wenn Material aus der Bereitstellungszone im LVS für
die Produktion entnommen wird, so muss die Menge in der Bereitstellungszone
reduziert werden. Dazu gibt es verschiedene Strategien. Die Auswahl hängt von
der Frage ab, ob Restmaterialien (teilentleerte Kisten/Paletten) evtl. wieder
ins Lager zurückgebracht werden sollen.
Szenario1: Restmaterialien ins Lager
Sobald die Produktion beendet ist, wird in der
Schnittstelle der Verbrauch des Materials und der entsprechende Ladeträger
angegeben. So kann gerechnet werden: Menge auf dem Ladeträger Minus Verbrauch =
neuer Bestand Ladeträger.
Eine Anzeige muss alle Ladeträger mit Material darauf
anzeigen, die in der Bereitstellungszone ohne Allokation stehen und dem Bediener
anbieten, diese mit einem Fahrauftrag ins Lager zu versehen.
Diese Lösung stellt die Anforderung ans
Produktionssystem, die entnommene Menge pro Ladeträger(Palette)
zurückzumelden.
Szenario2: Material verbleibt in der
Bereitstellungszone
Sobald das Material in der Bereitstellungszone ankommt
wird in einem Makro das Material vom ankommenden Ladeträger auf einen
Sammelladeträger in der Produktion gebucht.
Beim Eingang der Ende-Meldung wird die verbrauchte
Menge von Sammel-Ladeträger (
Typ Linie
–
eingerichtet in SPA 1037
)
abgebucht. Die Materialien werden stets vollständig verbraucht oder durch eine
1:1-Produktion wieder im LVS angemeldet.

---

## Makroprogramme

Makroprogramme
Hauptmenü
Administration
Makroverarbeitung
Makro-Programme
Direktsprung
[MAKRO]
In der Variante „Makroprogramme“ werden die
Makro-Programme von Referenz-ERP gepflegt.
Makro-Programme mit dem „Scriptbesitzer“ 0 (=Branchen-ERP)
werden ausgeliefert.
Felder
Name
Makroname (eindeutig zusammen mit
      dem Scriptbesitzer)
P1
Parameter 1
P2
Parameter 2
P3
Parameter 3
P4
Parameter 4
Freigabe
Kennzeichen: Ja = Makro ist
      freigegeben
Besitzer
0 =
      Branchen-ERP, 1 = privat
Geändert
Datum der letzten
      Änderung
ScriptId
Technische Identifikation des Makros
      (eindeutig zusammen mit dem Scriptbesitzer)
Suchen
Filtername
Like-Suche nach „Name“
Scripttyp
Von-Bis – Suche in den
      Scipttypen
Script enthält
Like-Suche im Programmtext
      (zeilenweise)
Freigabe
Freigabe-Kennzeichen
      auswerten
Funktionen
Filter /
      bereichsauswahl
F2
bearb./ausführen
      F5
Ruft
      Pflege-Dialog für ein bestehendes Makro auf.
Neu F8
Ruft
      Pflege-Dialog für ein neu zu erfassendes Makro auf
Script Export
Exportiert ein Makro in eine
      vorgebbare Sql-Datei.
Löschen F7
Löscht ein existierendes
      Makro
Makro ansehen
      SHF6
Zeigt den Makrotext im Editor
      an.
Ansehen F6
Zeigt das Makro im
      Ansehen-Modus.

---

## Änderungsprotokoll

Änderungsprotokoll
Menü: Administration
Werkzeuge: Projekte (Direktsprung: [SUPP])
Variante: Änderungsprotokoll
Mit der Variante
Änderungsprotokoll
können aus
archivierten Logfile-Daten Änderungen von Datensätzen der Referenz-ERP-Datenbank
nachvollzogen werden. Es werden damit Antworten auf die Fragestellungen der Art
„Wer hat wann ein bestimmtes Attribut einer bestimmten Relation geändert,
gelöscht oder eingefügt?“ geliefert.
Grundsätzlich erfolgt die Logfile-Archivierung auf
einem Fremdserver, um das Referenz-ERP-System durch die schnell wachsende Datenmenge
und gegebenenfalls der Komplexität und damit durchaus möglichen längeren
Laufzeiten von Anfragen nicht unnötig zu belasten. Die Einrichtung eines
entsprechenden Systems zur Logfile-Archivierung wird durch den Referenz-ERP-Support
unter Berücksichtigung der individuellen Gegebenheiten durchgeführt.
Änderungsabfragen werden den Eingaben entsprechend
mittels Datenbankfunktionen der Referenz-ERP-Datenbank generiert und einer
“entfernten“ Prozedur der Fremdserverdatenbank zur Ausführung übergeben. Als
Ergebnis werden die Statements der gefundenen Logfile-Einträge, ergänzt durch
den verursachenden Bediener und dem Archivierungsdatum, in die Auswahlliste
übernommen.
Die Funktion
Query zusammenstellen
ruft eine
Maske zur Eingabe der gewünschten Daten auf. Auf verschiedenen Tabs können
unterschiedliche Anfragevarianten realisiert werden:

---

## Partie und Produktion

Partie und Produktion
Hauptmenü
Produktion / Umbuchung
Produktionsabwicklung
Produktion oder Produktionszugang
erfassen
oder Direktsprung
[PROB]
oder
[PROE]
Durch die Produktion werden unterschiedliche
Komponenten zu einem Produkt verarbeitet. Durch diesen Prozess entsteht
üblicherweise auf dem Produkt eine neue Partie und die Komponenten werden von
bestehenden Partien abgebucht. Diese Verbuchung der Partien im Rahmen einer
Produktion ist ab der Referenz-ERP Version 4.4. möglich.
Bei der Erfassung des Produktionszuganges stehen für
diese Verbuchung nachfolgende Funktionen bereit:
Produkt Partieverteilung
Komponenten Partieverteilung
Akt.
Komponente Partieverteilung

---

## Partiezuordnung im Positionsteil

Partiezuordnung im Positionsteil
Im Positionsteil der Warenbelegerfassung lassen sich
Partien artikelübergreifend zuordnen. Die hierbei benutzte Dialogmaske wird (mit
einigen kleinen Unterschieden) auch in folgenden Bereichen eingesetzt:
•
Erfassung von Produktionen (Komponentenpartien / Produktpartien)
•
Bei Umbuchungen
•
Rohware (zurzeit nur mit einer Partie pro Position!!)
•
Lieferscheinschnellkorrektur
•
Partien nachtragen (auch in abgeschlossenen Vorgängen)
In im unteren Bereich werden die aktuellen
Warenpositionen angezeigt. Es kann sowohl mit der Maus als auch (praktischer)
mit den Pfeiltasten in Verbindung mit der Strg-Taste von Artikel zu Artikel
positioniert werden. Im oberen Bereich wird ähnlich wie bei der Warenerfassung
die Partiezuordnung vorgenommen. Allerdings stehen hier mehr Funktionen in der
Optionbox zur Verfügung:
•
F8
= Partie neu erfassen
•
SH8
= Falls eine automatische
Partiezuordnung eingerichtet, wird diese manuell gestartet
•
F7
= Löschen der gesamten
Partiezuordnung
•
F6
= Den noch verbleiben Rest
übernehmen
•
F10
= startet einen
Übersichtdialog zu der aktuellen Partie
•
SF10
= Übersichtdialog für
alle in diesem Belege angesprochenen Partien
•
F9
Umpacken: Ein Spezialmodul
zur Umlagerung von Partien
Der Schalter ‚Partiepreise übernehmen’ regelt an
dieser Stelle, ob durch geänderte Partiezuordnungen nochmalig die
Preisbestimmung überprüft werden soll.
ACHTUNG: Durch Veränderung des Preisgefüges werden
unter Umständen auch andere Daten des Beleges angepasst und es können schon
geänderte, manuelle Einstellungen wieder auf den Standardwert gesetzt
werden!!
Wichtiger Hinweis zur Restbestandsanzeige in der F3
Box bei der Partienummer
:
Es wird hier der Bestand angezeigt, der schon alle
Partien vor dem Öffnen dieses Dialoges berücksichtigt (die Partien wurden also
schon abgebucht / zugebucht). Während der Veränderung der Partiezuordnung kann
die Restbestandsanzeige nicht aktualisiert werden. Es wird allerdings beim
Abschlu
[...]


---

## Patch einspielen

Patch einspielen
Hauptmenü
Administration
Werkzeuge
Patch einspielen
oder Direktsprung
[PATCH]
Wird diese Funktion aufgerufen, öffnet sich ein
externes Programm (Referenz-ERP.Libraryviewer.exe), mit dessen Hilfe die von Branchen-ERP
bereitgestellten Patche eingespielt werden können. Die Installation des Patches
muss – wie vorher schon mit der repair.bat - pro Referenz-ERP-Installation und falls
SQL-Skripte eingespielt werden müssen, pro Mandant ausgeführt werden.
Funktion
Sicherheitskopie
      erstellen
Die
      Patch-Bibliothek „aeins0.lib“ wird als Datensicherung in das Verzeichnis
      „.\masken\libraryviewer\backup“ kopiert. Dabei wird eine Nummer hinter dem
      Dateinamen hochgezählt, damit ältere Sicherungen nicht überschrieben
      werden.
Wiederherstellen
Wird
      diese Funktion ausgewählt, öffnet sich ein Dateiauswahldialog auf dem
      Verzeichnis „.\masken\libraryviewer\backup“ und man kann eine der vorher
      gespeicherten Bibliotheken (s.o.) auswählen. Die in dieser Bibliothek
      enthaltenen Daten werden aufgelistet und man kann diese einzeln auswählen.
      Der Pfeil in der Mitte überträgt sie in die aktive
      Patch-Bibliothek.
Mit
      Escape verlässt man diesen Modus.
Löschen
Einzelne Dateien können aus der
      Patch-Bibliothek gelöscht werden. Tritt hierbei ein Fehler auf, z.B. weil
      der Anwender keine Schreibrechte hat, dann werden diese in die Log-Datei
      unter „.\masken\libraryviewer\log“ geschrieben.
Patch einspielen
Man
      kann mit dieser Funktion die von Branchen-ERP bereitgestellte ZIP-Datei auswählen,
      oder einfach die Dateien aus dem Explorer mit Drag and Drop in das
      Anzeigefenster ziehen. Zip Dateien werden automatisch in das
      Unterverzeichnis LibraryViewer.Temp des Referenz-ERP-Temp-Ordners entpackt (Im
      Explorer %temp%\Referenz-ERP\LibraryViewer.Temp) . Daten mit der Endung „.pub“,
      „.jam“ und Dateien ohne Dateinamenserweiterung werden sofort in die
      Aeins0.Lib eingespielt. Dateien mit de
[...]


---

## Perioden

Perioden
Hauptmenü
Administration
Geschäftsjahr / Perioden
Hinweis: Nur geöffnete Perioden können bebucht
werden.
a) Perioden eröffnen:
Hauptmenü
Administration
Geschäftsjahr / Perioden
Periodeneröffnung
Oder Direktsprung:
[PERER]
Grundsätzlich stehen alle Perioden nach dem Anlegen
eines neuen Wirtschaftsjahres erst dann zur Verfügung, wenn diese eröffnet sind.
Eine nicht eröffnete Periode kann nicht bebucht werden.
Um in der Startphase nicht ständig eine Warnmeldung zu
erhalten, sollten alle zulässigen Perioden eröffnet werden.
b) Perioden schließen:
Hauptmenü
Administration
Geschäftsjahr / Perioden
Buchungsschluss
Oder Direktsprung:
[PERBS]
Hier können die Perioden für die Erfassung neuer
Belege geschlossen werden.
Die schon in der Periode erfassten Belege müssen noch
nicht gebucht sein. Skontobelege oder Restposten werden nur auf Nachfrage in
diesen Perioden erstellt. Der Reorganisator greift noch auf diese Perioden
zu.
c) Periode wiedereröffnen:
Hauptmenü
Administration
Geschäftsjahr / Perioden
Wiedereröffnung
Oder Direktsprung:
[PERWE]
Eine Wiedereröffnung der Periode, die über
Buchungsschluss
[PERBS]
geschlossen
wurde, ist jederzeit möglich.
d) Perioden Abstimmmprotokoll
Hauptmenü
Administration
Geschäftsjahr / Perioden
Perioden Abstimmprotokoll
Oder Direktsprung:
[PERAP]
In dem Perioden Abstimmprotokoll sieht man alle
relevanten Einträge, welche für den Periodenabschluss der Ware notwendig
sind:
-
Belege, welche nicht an die Fibu übertragen wurde
-
Abweichungen von dem Wirtschaftsjahr zum Lieferdatum
-
Sonderperioden für die Ware, welche falsch eingerichtet wurden
-
Perioden mit Datumslücken/Überlappungen
-
nicht abgeschlossene Perioden aus Vorjahren
-
Statusfehler in der Inventurperiode
-
Belege, welche den Inventurabgrenzung verletzen
-
nicht erhobene Artikel
e) Periodenabschluss in der Ware
Hauptmenü
Administration
Geschäftsjahr / Perioden
Periodenabschluss Ware
Oder Direktsprung:
[PERAW]
Für die Inventur
[...]


---

## Produktion mit Partiepflicht

Produktion mit Partiepflicht
Ist die Partiepflicht eingeschaltet (siehe SPA), dann
prüft das Produktionsmodul auf korrekte Erfassung. In nachfolgendem Beispiel
wurde für die Komponenten Partiezwang im Artikel eingerichtet
und der SPA für die Produktion auf Überwachung bei
Artikeln mit Partiezwang geschaltet.
In der rechten Spalte wird je Komponente mit !
kenntlich gemacht, ob Partiezwang besteht. Mit * wird angezeigt, dass die
Partiebuchung erfolgte. Auf der Produktionsmaske erfolgt die Erfassung je
Position mittels
F5
.
Es wird dann die Menge eingegeben und mit
F5
auf die Partiezuordnung verzweigt. Ist
die Partienummer bekannt, wird sie hier eingegeben, ansonsten wird sie mit
F3
gesucht. Je Menge ist eine Partie
zulässig. Mehrere Partien werden einer Komponente durch Eingabe von jeweiliger
Menge und Nr. zugeordnet.

---

## Produkt Partieverteilung

Produkt Partieverteilung
Durch diese Funktion wird dem neu entstandenen Produkt
genau eine Partie zugeordnet oder angelegt. Bei Anwahl dieser Funktion wird ein
Fenster „Mengen/Partieaufteilung“ geöffnet (siehe
Komponenten Partieverteilung
). Eine
Aufteilung der Mengen je Partie ist nur in der Funktion für die Komponenten
erlaubt. Über
Partieauswahl
F5
kann dieser Produktmenge eine Partie
zugeordnet oder anschließend über
neue
Partie
F8
eine neue Partie
erzeugt werden.

---

## Produktion (Modul)

Produktion (Modul)
Unter Produktion wird die Buchung (Menge und Wert) von
Komponente zu Produkt nach der körperlichen Durchführung verstanden. Jedes
Artikelkonto kann hierbei sowohl Komponente wie Produkt sein (Bsp.
Vormischung).
Stückliste ist verkaufsbelegbezogene Auflösung von
Zusammensetzungen. Hierbei sind inhaltlich zu unterscheiden:
•
Auftragsfertigung
•
Setbildung
•
Zuordnungen (Dienstleistung gehört zum Artikel)
Das zugrunde liegende Schema ist bei allen angeführten
Zusammenhängen gleich, die nachfolgend dargestellten Parameter sind für den
gewünschten Ablauf einzustellen.
Es sind unterschiedliche Prinzipien der Bewertung
vorstellbar, die hier nur skizziert werden können. Die internen Verbuchungen von
Komponenten zu Produkten können den Gesamtrohertrag nicht verändern, ihn
allerdings verschieben. Werden die Komponenten mit ihren Zugangswerten in der
Produktion verbucht, fallen alle Roherträge auf der Ebene Produkt an, der
Zugangswert Produkt ist vermutlich zu niedrig. Falls dies so nicht gewollt ist,
bieten sich also zwei Lösungswege an:
•
Zuschlag auf Komponentenpreis
Es wird auf den Zugangswert
Komponente per Kalkulation ein Aufschlag erhoben. Mit diesem Aufschlag geht die
Komponente in die Produktion.
•
Zuschlag als Produktionsfaktor
Es werden die vermuteten
Produktionskosten als Rezepturbestandteil, Artikelkonto (Wertartikel)
aufgenommen. Jetzt läuft auf diesem Konto der angesetzte Betrag an.

---

## Produkt Partieverteilung F4

Produkt Partieverteilung F4
Es öffnet sich die Partieverteilung für das Produkt.
Es können die gewünschten Partien hinterlegt werden. Ist mindestens eine Partie
fürs Produkt hinterlegt, wird dieses auf der Erfassungsmaske unten links im
Informationsfeld mit angezeigt.
Wird eine Produktion mit Lagerplatzzuordnungen
durchgeführt, so können bei der Partieverteilung im Produkt unterschiedliche
Lagerplätze angegeben werden. Dieses bedeutet, dass zunächst einmal der
Produktionsprozess auf dem Produktlagerplatz durchgeführt wird, der auf der
Hauptmaske angegeben ist. Hierbei wird auf der Komponentenseite von den
Lagerplätzen abgebucht, die komponentenseitig zugeordnet sind, und auf der
Produktseite wird auf den Lagerplatz des Produktes gebucht.
Wird nun in der Maske der Produktpartieverteilung eine
Partiezuordnung vorgenommen, so kann zusätzlich zu der Partienummer und der
Menge auch noch ein Lagerplatz angegeben werden. Durch Angabe von mehreren
Partieverteilungszeilen (hierbei sind auch gleiche Partien erlaubt), ist es nun
möglich, in dem Produktionsprozess sofort eine korrekte Zuordnung von Teilmengen
des Produktionsprozesses auf Ziellagerplätze vorzunehmen.
Das System bucht diese Lagerplatzverteilungen per
Artikelumbuchung, die entsprechenden Vorgänge können in der Abteilung
„Lagerplatzumbuchung“ angesehen und bearbeitet werden. Die Buchungen werden im
Zugang/Abgang Verfahren vorgenommen, d.h. bei einer Korrektur oder einem Storno
wird eine Differenzbuchung zusätzlich zu der Originalbuchung erzeugt.

---

## Handelsstücklisten anlegen

Handelsstücklisten anlegen
Im Rezepturpfleger [REZ] wählt man die Variante
Handelsstücklisten aus.
Es gibt dort die Funktionen Neu F8 und Bearbeiten
F5.
Duplikat erzeugen F7

---

## Rücklieferung in Stückliste

Rücklieferung in Stückliste
Bei der Rücklieferung eines Stücklistenartikels tritt
inhaltlich das Problem auf, dass das erzeugte Produkt nicht wieder in seine
Komponenten zerlegt werden kann. In diesem Fall richte man eine zweite Rezeptur
ein, welche als Komponente das Produkt mit 100% enthält. Dadurch wird
realisiert, dass trotz Verwendung der Stückliste, die Rücklieferung auf das
Produkt gebucht wird. Evt. Preis- und Bewertungsabschläge können über den
Eintrag einer negativen Wertposition bezogen auf das Produkt realisiert
werden.
Die Variantenauswahl kann dann wie folgt
erscheinen:
Hier könnte beispielsweise die Komponentenvariante wie
folgt eingerichtet sein:

---

## Rezepturgruppen [REZG]

Rezepturgruppen [REZG]
Hauptmenü
Produktion / Abwicklung
Produktion Stammdaten
Rezepturgruppen
oder Direktsprung
[REZG]
Struktur
Es wird unterschieden zwischen Rezepten,
Rezepturgruppen und Artikeln. Hierbei stellt ein Artikel das Handelskonto dar.
Ein (oder auch mehrere) Artikel kann (können) einer Rezepturgruppe zugeordnet
werden. Innerhalb der Rezepturgruppe können sich wiederum mehrere Rezepte
befinden (evt. zeitlich befristete Varianten der Rezeptur).
Die Rezepturgruppe stellt also das Material dar, das
vielleicht unter verschiedenen Handelsnamen in Verkehr gebracht wird.
Unter einer Rezepturgruppe werden Rezepturen
vergleichbarer inhaltlicher Bedeutung zusammengefasst, z.B. alle
Pumpen-Stücklisten für eine Pumpe bestimmten Typs. Unterschiedliche
Komponentenlisten können hier somit zum gleichen Endprodukt führen. Die
Rezepturgruppe wird später beim Produkt (=Artikel) eingetragen. Bei der
Erfassung über das Produkt kann dann aus den eingetragenen Handelsstücklisten
der Rezepturgruppe ausgewählt werden.
Bei eindeutiger Zuordnung Material zu Artikel
empfiehlt sich hier eine Nummernvergabe gleich lautend zum Artikel.
Für die Vorschau und den Druck der Komponentenliste
können über den Formulareinrichter eigene Formulare definiert werden. Sie müssen
als Formulartyp 300 eingerichtet werden. Wird hier kein Formular eingetragen, so
wird das in der Stückliste fest hinterlegte Formular herangezogen.

---

## Rezepturen

Rezepturen
Hauptmenü
Produktion / Abwicklung
Produktion Stammdaten
Rezepturen
oder Direktsprung
[REZ]
Hier sind die eigentlichen Rezepturen einzugeben. Es
wird unterschieden zwischen „Rezepturen“ und „Handelsstücklisten“. In der
Auswahlliste ist für den hier diskutierten Fall „Rezeptur“ zu wählen.
Felder
Rezepturgruppe
Rezepturgruppe zu der die Rezeptur
      gehören soll
Rezepturnummer
Nummer der Rezeptur
Die
      Rezepturnummer darf nicht größer als 32767 sein.
Bezeichnung (Rezeptur)
Name
      der Rezeptur
Gültigkeit
Zeitraum der Verwendung
Gesperrt
Darf
      (evtl. vorübergehend) nicht verwendet werden
Verwendungstyp
Gibt
      an, wo die vorliegende Rezeptur verwendet werden kann:
•
Ausschließlich
      in der Produktion (0 – Produktion)
•
Ausschließlich
      in der Vermahlung (3 - Vermahlung)
•
In allen
      Ausprägungen (1 - Alle)
Dieser Verwendungstyp steht nur noch im
      Ändern-Fall zur Auswahl, wenn eine Rezeptur mit diesem Typ angelegt wurde.
      Im Neu-Fall wird dieser Verwendungstyp ab sofort nicht mehr
      angeboten.
•
Ausschließlich
      in der NzuM-Produktion (4 - NzuM-Produktion)
Anteile: Typ
Bei
      der Rezepturerfassung wird gegen die hier formulierten Werte geprüft. Mit
      Prüfung heißt, dass eine Verprobung zur rechts dazu einzugebenden Summe
      erfolgt.
•
Prozent mit
      Prüfung: prüft Prozentsumme
•
Prozent ohne
      Prüfung: keine Prozentprüfung
•
je ME ohne
      Prüfung: Stückliste ohne Mengenprüfung
•
je ME mit
      Prüfung: Stückliste mit Mengenprüfung
Anteile: Summe
Falls Anteile geprüft werden sollen,
      muss hier die Prüfsumme eingetragen werden
Rezeptgröße
Diese Rezeptgröße beschreibt die
      produzierte Menge des Rezeptes.
Werden zum Beispiel drei Komponenten
      zu gleichen Anteilen zusammen gemischt, kann für jede Komponente die Menge
      1kg und die produzierte Menge 3kg angegeben werden. So werden
      periodische Kommazahlen bei den Mengenangaben vermieden.
Es
      wi
[...]


---

## Rollenanalyse

Rollenanalyse
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Reorganisation
oder Direktsprung
[ROREO]
Es kann eventuell vorkommen, dass sich Rollen in den
Tabellen Rollenklasse bzw. Rollenkontext befinden, zu denen es kein
Stamm-Eintrag in der Relation Rollenstamm gibt. Diese Vorkommen werden hier als
Probleme aufgelistet, und können hier auch aufgelöst werden.
Felder der Rollenanalyse
Felder
Relation
Welche Relation ist
      beteiligt.
Zurzeit kommen in „Rollenkontext“
      und „Rollenklasse“ in Betracht.
Problem
Nähere Beschreibung des
      Problems.
mit
      Rolle
Die
      betroffene Rolle.
Anzahl Bedienerklassen
Informatorische Anzahl der
      Bedienerklassen der betroffenen Rolle.
Anzahl Kontexte
Informatorische Anzahl der Kontexte
      der betroffenen Rolle.
Bedienerklassen dürfen
Liste der
      Bedienerklassen
Bedienerklasse dürfen
      nicht
Liste der ausgeschlossenen
      Bedienerklassen
Suchmöglichkeiten der Rollenanalyse
Suchkriterien
Relation
Like
Problem
Like
Rolle
Like
Funktionen der Rollenanalyse
Funktionen
Problem beheben
      (
F9
)
Behebt die markierten
      Probleme.

---

## Rollenkontext

Rollenkontext
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenkontext
oder Direktsprung
[ROLLE]
oder
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Funktionen
oder Direktsprung
[ZUGF]
Einführende Erläuterungen finden sich unter
Zugriffsrechte
Funktionen
.
Felder des Rollenkontext
Felder
Rolle
Zuordnung des Rollenkontextes zur
Rolle
.
Funktion
Ein
      Rollenkontext besteht aus einer Funktion (Identifikation einer
      Anwendungsfunktion) und dem Auftreten der Funktion in der
      Benutzeroberfläche (Kontext).
Da
      Funktionen in Referenz-ERP auch immer eine Nicht-Benutzeroberflächen-artige
      Bindung haben, muss dieser Fall mit berücksichtigt werden. Das wird in
      diesem Falle dann über einen
leeren Kontext
signalisiert.
Kontext
Ein
      Rollenkontext besteht aus einer Funktion (Identifikation einer
      Anwendungsfunktion) und dem Auftreten der Funktion in der
      Benutzeroberfläche (Kontext).
Da
      Funktionen in Referenz-ERP auch immer eine Nicht-Benutzeroberflächen-artige
      Bindung haben, muss dieser Fall mit berücksichtigt werden. Das wird in
      diesem Falle dann über einen
leeren Kontext
signalisiert.
Beschriftung
Die
      textuelle Repräsentation einer Funktion in der
      Benutzeroberfläche.
Funktionsart
Funktionen senden Botschaften an das
      Referenz-ERP-System. Die Botschaften lassen sich in den Funktionsarten nach
      ihrem Wesen klassifizieren.
Siehe Funktionsarten.
Direktsprung
Ausgewählte Funktionen sind per
      Direktsprung erreichbar. Es kann mehrere Direktsprünge für die gleiche
      Funktion geben, diese werden hier angelistet.
Bezeichnung
Eine
      kurze Erläuterung zu der Funktion durch den Entwickler. Es handelt sich
      meist um die Beschriftung, es kann aber hilfreiche Abweichungen geben, um
      besser eine Funktion „einschätzen“ zu helfen.
Anmerkung
Anmerkung, siehe auch
      Bezeichnung.
Steupa
Steuerparameter
Pulldown
Gibt
      den technischen Bezug zum verwend
[...]


---

## Informationen

Informationen
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenkontext
oder Direktsprung
[ROLLE]
oder
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Funktionen
oder Direktsprung
[ZUGF]
Dieser Dialog zeigt je nach
Funktionsart
zusätzliche Informationen
zu einer Funktion in den Feldern „Funktions-Detail“ und „Funktions-Information“
an.
Funktions-Informationen:
Funktions-Informationen
Funktion
Die
      Identifikation der Funktion
Beschriftung
Textuelle Repräsentation der
      Funktion in der Benutzeroberfläche (Label)
Reservierung
Wenn
      was anderes als „Otto Normalbenutzer“
Bezeichnung
Wenn
      sie sich von der „Beschriftung“ unterscheidet.
Funktionsart
Funktionsart
Controlstring
Die
      Botschaft die bei Ausführung der Funktion an Referenz-ERP gesendet
      wird.
Anmerkung
Wenn
      vorhanden eine Anmerkung
Pulldown
Wenn
      es um eine Pulldown-Zuweisung der Funktion vorhanden ist.
Direktsprung
Wenn
      Direktsprünge zur Funktion vorhanden sind.
Maske
Wenn
      die Funktion einen Dialog aufruft, der Maskenname
Titel
Wenn
      die Funktion einen Dialog aufruft, der Titel der Maske
Menü/Favorit
Wenn
      die Funktion einem Menü-Favoriten zugeordnet ist.
Menü-Überschrift
Wenn
      es bei der Funktion sich einen Hauptmenü-Eintrag handelt, dann wird hier
      der „Pfad“ aufgelistet.
Zum
      Beispiel für OSQL:
Administration->Werkzeuge->Branchen-ERP
      SQL Zugriff
Menü-Aufrufer
Gibt
      den „Weg“ im Haupt-Menü an, um von ganz links nach rechts zu
      gelangen.
Zum
      Beispiel für OSQL:
MENU_2/Firmenstamm
menu_14/MENU_3_9786_Branchen-ERP
Das
      bedeutet der Kontext MENU_2 ruft durch die Funktion „Firmenstamm“ den
      Kontext „menu_14“ auf, wo wiederum die Funktion „MENU_3_9786_Branchen-ERP“ den
      Kontext „menu_41“ aufruft in dem sich die Menü-Funktion „MENU_AMIC_SQL“
      befindet.

---

## Diese Verbindungen

Diese Verbindungen
Hauptmenü
Administration
Werkzeuge
Anwendung FunkListe
oder Direktsprung [ANWF]
Eine spezialisierte Anwendung des Rollenkontextes ist
„Diese Verbindungen“.
Im Ändern-Dialog unter Menüpunkt „Verbinden“ lassen
sich über die Funktion „Diese Verbindungen (F10)“ die Rollenkontexte der
Verbindungen dieser Funktion administrieren.

---

## Rollenkontext: Pfleger

Rollenkontext: Pfleger
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenkontext
oder Direktsprung
[ROLLE]
oder
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Funktionen
oder Direktsprung
[ZUGF]
Pflege des
Rollen-Kontextes der Funktion in der Optionbox.
Ein solcher „Kontext“ beschreibt die Rechtezuordnung
der Bedienerklassen an genau dieser Stelle im Programm durch die Zuweisung einer
Rolle.
Ändert sich diese Zuweisung, werden also
Bedienerklassen Rechte erteilt bzw. entzogen, führt das zu einer neuen
Rollendefinition. Das System prüft automatisch, ob es schon eine solche
Rechtekonfiguration gibt, und stellt diese zur Verfügung. Im Falle das es die
gewünschte Konfiguration als Rolle noch nicht gibt wird diese vom System
angelegt.
Sollen Rollen insgesamt geändert werden, also für alle
Vorkommen der Rolle in allen Kontexten gleichzeitig, empfiehlt sich der
Rollenpfleger
.
In Umgebungen in denen spezielle Bedienerklasse für
die Abarbeitung und Überwachung der Rollenänderungen eingerichtet sind lassen
sich sogenannte Rollenanträge erstellen und ggf. vermailen.
Felder des Rollenkontext Pfleger
Felder
Kontext
Zuordnung des Rollenkontextes zu dem
      Kontext.
Funktion
Zuordnung des Rollenkontextes zu der
      Funktion.
Rolle
Die
      zugeordnete
Rolle
des
      Rollenkontextes.
Rolle ist per
F3
aus den vorhandenen Rollen
      auswählbar.
Neue
      Rolle
Zeigt an, ob die Rolle neu erstellt
      wird
Ist
Status der Bedienerklasse innerhalb
      der zuordneten Rolle.
Bedienerklasse
Bedienerklasse
Soll
Der
      gewünschte neue Status der Bedienerklasse.
Geänderte Soll-Stati im Vergleich
      zum Ist-Status werden farblich zur besseren Übersicht
      abgegrenzt.
Bedienerklassen-bezeichnung
Die
      Bezeichnung der Bedienerklassen.
Ein
      vorangestellter Stern (*) bedeutet das die Bedienerklasse eine
      Controller-Klasse ist, somit die Bedienerklasse Mitglied der
Controller-Rolle
ist.
Bediener
Informatorisch
[...]


---

## Rollenmapping

Rollenmapping
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Mapping
oder Direktsprung
[ROLLM]
Neue Funktionen in Kontexten erhalten
vereinbarungsgemäß beim Update die „Controllerrolle“ zugewiesen.
Werden von Entwicklern neue Funktionen ins System
verbracht, die alte Funktionalitäten ablösen, dann ist es in vielen Fällen
sinnvoll die bestehenden Rollen zu übernehmen.
Diese werden hier hinterlegt und auf Kundensystemen
nach einem Programm-Update zum Abgleich gebracht.
Felder des Rollenmapping
Felder
Optionbox
Optionbox des
Rollenkontextes
.
Funktion
Funktion des
      Rollenkontextes.
Rolle
Die
      aktuelle
Rolle
des
      Rollenkontextes.
Done
Anpassung durchgeführt
      worden.
Quelle Rolle
Ursprungsrolle die als Vorlage der
      Rolle für die Funktion gelten soll.
Quelle Optionbox
Optionbox des
      Quellen-Rollenkontextes.
Quelle Funktion
Funktion des
      Quellen-Rollenkontextes.
Quelle sichtbar?
Bestimmt ob der Quell-Kontext
      „sichtbar“ bleibt.
Dies
      wird benötigt, wenn eine Funktion in der Quelle nicht mehr in der Quellen-
      Optionbox vom System angezeigt werden soll.
Suchmöglichkeiten des Rollenmapping
Suchkriterien
Suchen
Suchen in den Optionbox- und
      Funktionsfeldern
Quelle sichtbar?
Suchen im Feld „Quelle
      sichtbar?“
Möglich sind Ja, Nein und
      Egal.
Funktionen des Rollingmapping
Funktionen
Ändern, Löschen, Neu
      (
F5,F7,F8
)
Stehen ausschließlich der
      Entwicklung zur Verfügung
Ansehen (
F6
)
Ansehen
Funktion Informationen
      (
F9
)
Aufruf eines
Informationsdialoges zur
      Funktion
.
Stapelzuordnung aus
      Optionbox
Steht ausschließlich der Entwicklung
      zur Verfügung.

---

## Rollen vereinigen

Rollen
vereinigen
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rolle
Rollenstamm
oder Direktsprung
[ROLLE]
Hiermit besteht die Möglichkeit Rollen zu hinsichtlich
ihrer Rollenklasse und ihren Rollenkontexte zu vereinigen.
Felder
Folgende Rollen
Die
      in der Auswahlliste vorselektierten Rollen zur Vereinigung
In
      dieser Rolle zusammenführen
Die
      Zielrolle, in der die obigen Rollen zusammengefasst werden.
Die
      Zielrolle kann entweder eine der vorselektierten Rollen sein oder eine
      ganz neue.
Als
      Ergebnis der Vereinigung erhält die Zielrolle die Vereinigung aller
      Bedienerklassen-Zuordnungen der beteiligten Rollen, sowie wird allen
      Kontexten der beteiligten Rollen die Ziel-Rolle zugeordnet.
Funktionen
Rolle vereinigen (
F9
)
Rollen vereinigen

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

## Produktion Schnellerfassung

Produktion Schnellerfassung
Hauptmenü
Produktion / Abwicklung
Produktionsabwicklung
Produktion
oder Direktsprung
[PROB]
und
[PROSE]
Dieses Modul ist nur bei entsprechend eingestelltem
Steuerparameter Produktions-Schnellerfassung aktiv.
In den Varianten der Produktion [PROB] steht die
Funktion Produktion Schnellerfassung zur Verfügung. Mit dem Direktsprung [PROSE]
kann das Modul auch direkt aufgerufen werden.
ACHTUNG: Die Schnellerfassung verfügt nicht über den
vollen Leistungsumfang, wie er im Standard-Produktionsmodul mittels der
Direktsprünge PROB und PROE zur Verfügung steht.
Felder Register
      Produktion
Lager
Produktionsdatum
Umfuhr
MHD
Produktnummer
Lagerplatz
Rezeptur
Hier
      wählt man die Rezeptur an, die man verwenden möchte.
Produktmenge
Preis
Felder Register
    Optionen
Produktinformation
Komponenteninformation

---

## SQL Textmanager

SQL Textmanager
Hauptmenü
Administration
Werkzeuge
SQL Textmanager
oder Direktsprung
[SQLM]

---

## SQL Texte

SQL Texte
Hauptmenü
Administration
Werkzeuge
SQL Textmanager
oder Direktsprung
[SQLM]
Die Anwendung „SQL Texte“ bündelt eine Reihe von
Varianten, die sich um die Pflege von Datenbank-Objekten kümmern, zusammen.
Die zugehörigen Daten werden in der Datenbank-Tabelle
„SQL_Stamm“ vorgehalten, und die privaten Objekte werden bei Änderungen auch in
der Datenbank aktualisiert.
Variante
Direktsprung
Bedeutung
SQL
      Texte
ITEM
      BOXES
[SQLI]
TRIGGER
[SQLT]
PROCEDURES
[SQLP]
VIEWS
[SQLV]
ASQL
      Scripte
[SQLS]
Views für Crystal Report
[SQLC]
Anwendungen (Branchen-ERP
      Systemvarianten)
Private SQL Texte
[SQLK]
Private Itemboxen
[SQLPI]
Private Datenbanktrigger
[SQLPT]
Private
      Datenbankproceduren
[SQLPP]
Private Views
[SQLPV]
Private ASQL Scripte
[SQLPS]
Anwendungen (private
      Varianten)
[SQLPA]
Views für private Crystal
      Reports
[SQLPC]
Suche Bezeichnung in
      SQL_Text
Views in der DB
Proceduren in der DB
Trigger in der DB

---

## Private Datenbankprozeduren

Private Datenbankprozeduren
Hauptmenü
Administration
Werkzeuge
SQL Textmanager und dann Variante „Private
Datenbankprozeduren“
oder Direktsprung
[SQLPP]
Auswahlliste
Bedeutung
SQL
      Text
Eindeutiger Arbeitsname innerhalb
      der Datenvorhaltung.
Datenbankname
System-Name des Objektes in der
      Datenbank (kann sich - sollte aber gemäß Empfehlung nicht - vom
      Arbeitsnamen unterscheiden)
Definition
Der
      Text der Prozedure gemäß System-Datenbank-Tabelle
      „sysprocedure“
Source
Der
      Quelltext der Prozedure gemäß Referenz-ERP-Datenbank-Tabelle
      „Sql_Stamm“
Bereichsauswahl/Filter
Bedeutung
Textname
Suchen im Arbeitsnamen „SQL
      Text“
Funktionen
Bedeutung
Neu
      (F8)
Es
      öffnet sich ein Dialog in dem sich ein privater Arbeitsname unter
      „Sql-Text“ angeben lässt. Empfohlen ist privaten Arbeitsnamen ein
p_
voranzustellen.
Mittels „Template“ lässt sich als Vorlage der
      Text einer bestehenden privaten Datenbank-Prozedure auswählen.
Wird
      das Feld „Template“ leer gelassen öffnet sich der Editor mit einem
      Vorschlag.
Als Beispiel für die fiktive private Datenbank-Funktion
      „P_Beispiel“:
-- Priv. Prozedur p_beispiel --- Streckeunit
      20.11.2023
--
--
      Beschreibung
--
--
--
CREATE PROCEDURE
      p_beispiel ( )
--
BEGIN
-- Hier kann die
      Verarbeitung beginnen
--
--
--
EXCEPTION
when others
      then
call amic_exception( ERRORMSG() || CHAR(10) || CHAR(13) || TRACEBACK(),
      SQLCODE , SQLSTATE , 'p_beispiel' , -1 , in_commit = 1);
--
      ggf. sofortiges commit mit in_commit=0 unterbinden (z.B. bei Verwendung in
      Trigger, Atomic)
ENDD
Editieren (F5)
Der
      Editor öffnet sich mit dem Text der Datenbank-Prozedure (siehe
      „Source“)
Löschen (F7)
Entfernt die Datenbank-Prozedure aus
      dem System-.
Create (F10)
Legt
      das Datenbank-Objekt gemäß der „Source“ an.
Drop
      (F11)
Entfernt ggf. ein vorhandenes
      Datenbank-Objekt.
Export (Umschalt F8)
Expor
[...]


---

## Steuerparameter (Produktion)

Steuerparameter (Produktion)
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
oder Direktsprung
[SPA]
Die einzurichtenden Steuerparameter findet man indem
man in der Auswahlliste die Bereichsauswahl auf die
Gruppe Rezeptur/Stückliste/Produktion
abgrenzt.
Zunächst sind die Steuerparameter
[SPA]
einzurichten:
Steuerparameter
Parameter 666:
Positionsumbuchung
      Mengenbehandlung
Berechnung des Komponentenanteils in
      der Maske Positionskalkulation. 0 bedeutet der Anteil wird wie in der
      Komponente angegeben berechnet. 1 bedeutet Menge wird wie im Rezept
      angegeben berechnet.
Parameter
      28:
Stücklistenverwaltung angeschlossen
Steuert das Programmverhalten bei
      Artikeln mit hinterlegten Rezepturen. Die Rezepturen werden nur aufgelöst,
      wenn hier „Ja“ eingetragen ist.
Parameter
      302:
Komponentenlagerwahl für Produktion
Legt
      fest, aus welchem Lager die Komponenten für eine Rezeptur genommen
      werden.
Das
      Lager für die Komponenten ist in der Regel gleich Lager des Produktes,
      hier ist nur bei speziellen Einrichtungen anderes
      einzustellen.
0 =
      wie Zugangslager
1 =
      wie im Rezept hinterlegt
Parameter 321:
Komponentendaten
      auf Produktionsmaske unveränderbar
Falls im Produktionsmodul keine
      Komponentendaten während der Erfassung verändert werden dürfen ist hier
      „Ja“ einzustellen.
Parameter 322:
Korrektursperre
      bei Importdaten
Werden Daten aus einem vorgelagerten
      Produktionssystem importiert, sollen sie möglicherweise (i.d.R.) nicht
      mehr korrigiert werden.
Parameter
      458:
Lagerplatzverwaltung auch bei Produktion
Wenn
      die Lagerplatzverwaltung aktiviert ist, sollen ggf. auch die Buchungen für
      Produkt, Komponente und Rezeptur lagerplatzbezogen erfolgen. Dies ist hier
      dann zu aktivieren.
Parameter
      309:
Rezeptur-Definition aus Vorgangsbearbeit
Die
      Rezepturdefinition aus der Belegerfassung heraus ist z.Z.
[...]


---

## Rezeptur/Stückliste/Produktion

Rezeptur/Stückliste/Produktion

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

## TSE-Pfleger

TSE-Pfleger
Eine TSE-Konfiguration zeichnet sich durch eine
TSE ID
und dem
Gültig Ab
aus.
Die TSE-ID
wird vom System vergeben. Das
Feld
Gültig Ab
gibt das Datum an, ab
welchem die Konfiguration gelten soll.
Mehrere TSE-Konfigurationen zur gleichen
TSE-ID
sind möglich.
Sie werden durch
F5
und
Speichern unter
ermöglicht.
Erläuterungen zur
Behandlung des
Laufwerks
bei
Client-Transaktionen: Referenz-ERP versucht die richtige TSE selbst zu finden. Falls
das nicht gelingt, wird versucht diese automatisch zu „mappen“, wenn bei
Manueller Host
eine Freigabe eingetragen
ist.
Durch den automatischen Suchalgorithmus muss auf den
Clienten selbst das in „Laufwerk“ hinterlegte Laufwerk nicht zwingend den
gleichen Laufwerksbuchstaben haben.
Kopfdaten des TSE Pflegers
Feld
Beschreibung
TSE-ID
Gibt
      die TSE-ID der Konfiguration an.
Gültig ab
Gibt
      an, ab wann die TSE-Konfiguration gültig ist.
Aktiv-Datum
Hier
      wird das
Gültig ab
der zurzeit
      maßgeblichen TSE-Einstellung angezeigt.
Hinweis:
Das
      beantwortet die Frage „Welche Konfiguration würde zum jetzigen Zeitpunkt
      vom System herangezogen?
Ist
      nur eine Konfiguration zur „TSE-ID“ vorhanden, stimmen
Aktiv-Datum
und
Gültig Ab
überein.
Status/Verfügbarkeit
Gibt
      an, ob die TSE aus Sicht des aktuellen Arbeitsplatzes verfügbar
      ist.
Wenn
nein
aktiviert
      ist
, dann gibt es eine textuelle Erläuterung.
Wenn
ja
aktiviert ist, wird
Datum und Uhrzeit
des letzten
      Zugriffs gemäß TSE-Spezifikation angezeigt.
Hardware-Host
Name/IP des Hosts zum Zeitpunkt der
      Ersteinrichtung.
(Je nach Ausstattung können mehrere IPs aufgelistet
      werden)
Dieser Rechner
Name/IP des aktuellen
      Arbeitsplatzrechners
(Je
      nach Ausstattung können mehrere IPs aufgelistet werden).
Bezeichnung
Frei
      wählbare Bezeichnung der TSE.
Laufwerk
Bei
      der Erstinstallation zugewiesener Windows-Laufwerksbuchstabe. (A-Z sind
      theoretisch denkbar)
Lizenz
Der
      Label ist je
[...]


---

## Zugriffsrechte Funktionen

Zugriffsrechte Funktionen
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Funktionen
oder Direktsprung
[ZUGF]
oder
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Rollen
Rollenkontext
oder Direktsprung
[ROLLE]
Funktionen sind Aufträge (sogenannte Controlstrings)
an das Referenz-ERP-System eine vordefinierte Funktionalität auszuführen. Funktionen
sind innerhalb der Benutzeroberfläche von Referenz-ERP in sogenannten Kontexten
zusammengefasst. Unabhängig davon können Funktionen auch außerhalb eines jeden
Kontextes veranlasst werden, diese Funktionen sind zur weiteren Unterscheidung
einem leeren Kontext zugeordnet.
Funktionen können privat vom Anwender ins System
integriert werden. Außerdem können mit jedem Programm-Update auch neue
Funktionen ins System kommen.
Diese Gegebenheiten machen es unerlässlich die
Ausführungsberechtigung an
Bedienerklassen
zu binden, dieses wird in
Referenz-ERP über die
Rolle
, die
Rollenklassen
und die jeweiligen
Rollenkontexte
abgebildet.
Report Zugriffsrechte Funktionen
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Funktionen
oder Direktsprung
[ZUGF]
In der Option Box der Auswahlliste gibt es eine
Funktion, die den Report Zugriffsrechte Funktionen aufruft.
Mit Hilfe dieses Reports für die Administration kann
man sich alle Zugriffsrechte zu einer Rolle ansehen.
Es werden die Funktionen
zu einer Rolle angezeigt, sowie die Pfade wie man übers Menü zu ihnen gelangt
(soweit vorhanden). Die Funktionen zu einer Rolle sind nach ihrem Eintrag im
Menü gruppiert.
Hiermit hat man dann einen sehr guten Überblick darüber
welche Funktionen ein Bediener,
der einer bestimmten Rolle zugeordnet ist,
ausführen darf.
Zugriffsrechte Varianten
Hauptmenü
Administration
Firmenkonstanten
Zugriffsrechte Varianten
oder Direktsprung
[ZUGV]
Alle Varianten in Auswahllisten (also z.B. Rechnung
(komplexe Auswahl) in
[REB]
) werden in
einer Auswahl­liste angezeigt. Hier kann man jetzt für eine einzelne
(Einzelbearbeitung) oder einen selektiert
[...]


---

## Zusammensetzung F10

Zusammensetzung F10
Felder
Rezepturgruppe
Rezepturgruppe zu der die Rezeptur
      gehören soll
Rezepturnummer
Nummer der Rezeptur für die die
      Zusammensetzung angezeigt wird.
Mengenanteil
      Hauptprodukt
Nur
      sichtbar und eingebbar bei NzuM-Produktion
Wertanteil Hauptprodukt
Nur
      sichtbar und eingebbar bei NzuM-Produktion
Tabellenfelder
Nur
      für NzuM-Produktion und Vermahlung sichtbar
Abgang/Zugang
Über
      die F3-Auswahl kann zwischen Zugang und Abgang für die einzelne Komponente
      gewählt werden.
Anteil Abgang
In
      diesem Feld ist der Anteil für den Abgang einzugeben, wenn beim Feld
      ‚Abgang/Zugang‘ Abgang gewählt wurde.
Anteil Zugang
In
      diesem Feld ist der Anteil für den Zugang einzugeben, wenn beim Feld
      ‚Abgang/Zugang‘ Zugang gewählt wurde.
Wertanteil Zugang
Nicht sichtbar für
      Vermahlung
Summen
Nur
      für NzuM-Produktion und Vermahlung sichtbar
Anteile Abgang
Anzeigefeld
Anteile Zugang
Anzeigefeld
Wertanteile Zugang
Anzeigefeld, nur bei NzuM-Produktion
      sichtbar
Die Zusammensetzung einer Rezeptur kann sowohl aus
Artikel als auch aus weiteren Rezepten bestehen. In der Tabelle erkennt man
Rezepte daran, dass in der Spalte „Artikel-Rezeptnr“ die Rezeptgruppe und
-variante steht, außerdem ist das Feld in diesem Fall farblich hervorgehoben.
In der Auswahlliste der Artikel unterscheiden sich
Rezepte von Artikel darin, dass Rezepte bei „Rezept“ „Ja“ und bei „Variante“ ein
Wert ungleich 0 steht, Artikel haben dagegen in diesen Feldern immer den Wert
„Nein“ bzw. 0.
Hier kann je Rezeptposition festgelegt werden, ob es
sich um eine Wertposition (wird bei Mengenrechnung nicht berücksichtigt), um
eine Pauschalposition (wird unabhängig von der Produktmenge berücksichtigt) oder
um eine Position mit Fixpreis (Preisfindung unabhängig von der unter
[SPA]
eingestellten Methode) handelt.
Hinweis
Es ist bei der Rezeptureingabe im Mehrlagerbetrieb auf
die korrekte Lagerzuordnung zu achten. Es kö
[...]


---

## Aktionsfelder

Aktionsfelder
Hauptmenü
Administration
Werkzeuge
Informationssystem
Register Aktionsfeld
Direktsprung
[AIS]
Das Register “Aktionsfeld” erscheint immer dann, wenn
der Feldtyp ein Push-Button oder Anwendungsgrid ist. Hier wird dann festgelegt,
was geschehen soll, wenn auf den Knopf gedrückt wird.
Als Aktion sind folgende Möglichkeiten vorgesehen:
1. Anwendungsfunktion aufrufen
Es wird eine unter ANWF bzw. PF (Private Funktion)
hinterlegte Funktion aufgerufen. Es sind hier nur Menüfunktionen möglich. Der
Controlstring, der ausgeführt wird, lautet:
^jpl
aw_funk :ANWFUNKID
Die ANWFUNKID kann mit
F3
ausgewählt
werden.
2. Anwendung aufrufen
Es wird eine Anwendung aufgerufen. Anzugeben ist hier
die ANWID. Diese kann per F3 ausgewählt werden. Der Controlstring, der
ausgeführt wird, lautet:
^jpl
aw_vert :ANWID
3. Anwendungsvariante aufrufen
Es wird eine vorgegebene Variante einer Anwendung
aufgerufen. Im obigen Beispiel ist es die Variante „STANDARD“ der Anwendung
„KUNDEN“. Der Controlstring sieht also im Beispiel folgendermaßen aus:
^jpl
ais_vert KUNDEN STANDARD Feldname
Bei Varianten lassen sich die Werte aus dem
Auswahlbereich (
F2
) vorbelegen. Welche Felder als VON bzw.
BIS-Vorbelegung herangezogen werden können, lässt sich mit
F3
auswählen.
Bei Push-Buttons kann man in den Spalten „Vorbelegung Von“ und „Vorbelegung Bis“
einen Festen Wert oder ein Maskenfeld eintragen. Beim Anwendungsgrid sind
zusätzlich die Felder aus der Fieldsanweisung als Parameter möglich. Wenn in der
Fieldsanweisung also
FIELD
Konto,k.KontoNummer,I4,8
steht, so muss in der/ Vorbelegungsspalten
„k.KontoNummer“ stehen. Es wird dann der Wert aus der Zeile an den
Auswahlbereich übergeben.
4. Crystal Report aufrufen
Ein Report, der über die ANWRPTID identifiziert wir,
die über
F3
ausgewählt werden kann, wird geöffnet. Die Art und Weise, wie
er gestartet werden soll, lässt sich in dem dann sichtbaren Feld „Wie starten“
angeben. Es stehen die Möglichkeiten
0.
Vorschau und bestät
[...]


---

## Basisdaten

Basisdaten
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register Allgemein
Direktsprung
[ANWR]
.
Auf dem Register
Allgemein
befinden sich folgen
Eingabefelder
Feld
Bedeutung
Auswahlbereich
Hier
      wird die Bezeichnung des Auswahlbereichs, der dann mit
F6
bearbeitet werden kann, eingetragen.
Vorlauf-OptBox
Hier
      kann man eine zusätzliche Optionbox angeben. Sie wird dann zusätzlich zu
      den Standardfunktionen angezeigt. Diese kann z.B. einen speziellen
      Hilfe-Aufruf oder Funktionen zum Aufruf von Stammdatenpflegern
      enthalten.
Vorlauf-Funktion
JPL-Funktion (*.j), mit deren Hilfe
      Daten aufgesammelt oder Tests durchgeführt werden können. Wird von der
Funktion
ein Wert
      ungleich 0 (S_OK) zurückgeliefert, wird der Report nicht
      gestartet.
Formatierte Eingabe
Hiermit wird festgelegt, welcher Art
      die Vorlauffunktion ist. Es existieren die Ausprägungen “Ohne Vorlauf“ und
      „jpl Aufruf maskenlos“.
Nachlauf-Funktion
Ist
      hier eine JPL-Funktion (*.j) eingetragen, so wird diese nach Beendigung
      des Reports aufgerufen.
Reportviews
Die
      Daten eines Reports sollen über Views zusammengesucht werden. In diesen
      Views können dann auch die Eingrenzungen vorgenommen werden.
Status
Entwicklungsstatus
Export-Verzeichnis
Hier
      kann ein Verzeichnis angegeben werden, auf dem der Export dieses Reports
      geschrieben werden soll. Dieses Feld wird nicht ausgeliefert und auch
      nicht  beim Kunden überschrieben. Ist kein Verzeichnis angegeben,
      werden die Dateien in das Verzeichnis „Crystalexport“
      geschrieben.
Zugriffsschutz für
      Exportbutton
Hier
      kann über die in Referenz-ERP üblichen Schutzmechanismen der Exportbutton, der
      sich links oben im Anzeigebereich des Reports befindet, weggeschützt
      werden. Für den Crystal Report Version 13.0.2000.0 besteht zusätzlich die
      Möglichkeit für alle Reporte den Exportbutton dadurch zu schützen, dass
      man die F
[...]


---

## Beispiel 1 für NzuM-Produktion:

Beispiel 1 für NzuM-Produktion:
Anlegen eines Rezeptes zur Rezepturgruppe 36000 mit
Rezepturnummer 1 unter
[REZ]
:
Für den Verwendungstyp wurde NzuM-Produktion
gewählt.
Anteile Typ wurde auf ‚je ME ohne Prüfung‘ gesetzt, dass heißt das
bei der Zusammensetzung des Rezeptes keine Prüfung der Summe der Komponenten
stattfindet.
Die Rezeptgröße von 1000 Litern bezieht sich nur auf das
Hauptprodukt (in unserem Fall Altbier).
Als Bewertungstyp wurde ‚Komponenten
addieren‘ gewählt, dadurch bestimmen die Werte der Komponenten den Wert des
Produktes.
Unter
Zusammensetzung F10
können danach die
Komponenten für das Rezept 1 eingegeben werden. In unserem Beispiel ergibt die
Summe der Anteile des Hauptproduktes 1739,5 (siehe unten auf der Maske im Kasten
Summen im Feld Anteile Abgang). Die Summe wird hier vom System nicht geprüft, da
für den Anteile: Typ ‚je ME ohne Prüfung‘ angegeben wurde (auch wenn das Feld
Summe im Rezept im Beispiel mit der entsprechenden Zahl gefüllt wurde).
Der
Mengenanteil des Hauptproduktes wird hier mit 70 angegeben. Für den Treber ist
ein Mengenanteil von 30 in der Spalte ‚Anteil Zugang‘ angegeben.
Der
Wertanteil für das Hauptprodukt soll 90 sein, der Wertanteil Zugang für den
Treber 10.
Unter
[PROE]
wird dann die Produktion erfasst.
Der Positionsteil sieht wie folgt aus:
Unter Produktnummer ist die Rezepturgruppe angegeben
und unter Rezept wählt man die entsprechende Rezeptur aus, in diesem Fall das
Rezept 1. Dann gibt man die Menge an, die produziert werden soll. In diesem Fall
sind es 2000 Liter.
Bei den Komponenten in der Spalte ‚Menge Abgang‘ kann
man erkennen, dass sich die Mengen für das Hauptprodukt (aus dem Rezept)
verdoppelt haben, da die doppelte Menge des Hauptproduktes produziert werden
soll. Für die ‚Menge Zugang‘ (den Treber) ergibt sich dann der Anteil 857,1429.
Dieser errechnet sich aus der Produktionsmenge (2000 l) geteilt durch den
Mengenanteil des Hauptproduktes von 70 multipliziert mit dem Anteil Zugang von
[...]


---

## Beispiel 2 für NzuM-Produktion:

Beispiel 2 für NzuM-Produktion:
Anlegen eines Rezeptes zur Rezepturgruppe 36000 mit
Rezepturnummer 10 unter
[REZ]
:
Für den Verwendungstyp wurde NzuM-Produktion
gewählt.
Anteile Typ wurde auf ‚je ME mit Prüfung‘ gesetzt, dass heißt das
bei der Zusammensetzung des Rezeptes eine Prüfung der Summe der Komponenten
stattfindet.
Die Rezeptgröße von 1000 Litern bezieht sich auf die Summe der
Produkte.
Unter
Zusammensetzung F10
können danach die
Komponenten für das Rezept 10 eingegeben werden. In unserem Beispiel ergibt die
Summe der Anteile des Hauptproduktes 1739,5. Dies wird hier vom System geprüft,
da für den Anteile: Typ ‚je ME mit Prüfung‘ angegeben wurde. Gibt man in der
Summe zu wenig oder zu viele Anteile für die Komponenten des Hauptproduktes an
erscheint beim Speichern oder Verlassen der Maske eine Hinweis-Meldung.
Der Mengenanteil des Hauptproduktes wird hier mit
70 angegeben. Für den Treber ist ein Mengenanteil von 30 in der Spalte ‚Anteil
Zugang‘ angegeben.
Unter
[PROE]
wird die Produktion nun erfasst.
Der Positionsteil sieht wie folgt aus:
Unter Produktnummer ist die Rezepturgruppe (36000)
angegeben und unter Rezept wählt man die entsprechende Rezeptur aus, in diesem
Fall das Rezept 10.
Dann gibt man noch die Menge an, die man produzieren
will. In diesem Fall sind es 700 Liter (von dem Hauptprodukt).
Da im Rezept eine Rezeptgröße von 1000 Litern für die
Summe der Produkte angegeben war, bleibt dann für den Treber noch 300 über. Die
Mengen für das Feld ‚Menge Abgang‘ der einzelnen Komponenten berechnen sich dann
aus dem Feld ‚Anteil Abgang‘ aus dem Rezept geteilt durch die Rezeptgröße (1000)
multipliziert mit der zu produzierenden Menge (700).
Der Bildschirmabzug wurde unter
[PROB]
erstellt.
Die Voreinstellung für die Mengenkontrolle steht hier
auf aktiv, so wie es im Rezept 10 für die Beleg-Korrektur angegeben wurde. Dort
stand laut Masken-EPA. Schaut man in die Einrichterparameter dieser Maske sieht
man, dass die Mengenkontrolle hier an
[...]


---

## Beispiel eines eigenständigen Pflegers

Beispiel eines eigenständigen Pflegers
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Es soll diese einfache Maske zur Erfassung von
Beladeort, Container und Menge erstellt werden.
Anlegen des Labels
Im Referenz-ERP Informationssystem legt man sich einen neuen
Eintrag (
F8
) an. Zuerst muss die Gruppe angegeben werden, in diesem
Beispiel soll sie „Aeinszusatz3“ heißen. Hat man bereits ein oder mehrere Felder
zu einer Gruppe erfasst, kann man die Gruppe hier mit
F3
auswählen. Die
Felder „
Makro
“, „
Ändern Vorlauf
“ und „
Einfügen
Vorlauf
“ werden dann vorbelegt. Sie können in diesem Fall leer
bleiben.
Register Feldbeschreibung:
Beschreibung
Feldname
Auch
      für Label, die nicht aus der Datenbank gefüllt werden, müssen Feldnamen
      vergeben werden. Sie sollten so gewählt werden, dass man schon am Namen
      die Bedeutung erkennen kann. In diesem Beispiel soll der Name des ersten
      Labels „lbl.Lieferdatum“ heißen. Das Kürzel „lbl“ gefolgt von einem Punkt
      soll uns zeigen, dass es sich um einen Label handelt.
Sortierung
Die
      Sortierung ist bei Labeln, die nicht aus der DB gefüllt werden, nicht
      wichtig und kann auf 0 stehen gelassen werden.
Feldtyp
Der
      Feldtyp für die Beschriftungsfelder muss natürlich
Label
sein.
Datenformat
Wenn
      der Label aus der Datenbank gefüllt wird, kann es nötig sein, ein anderes
      Format als „Character“ einzugeben. In unserem Beispiel reicht CHARACTER.
Zeile und Spalte
Die
      Position kann entweder über ein Raster oder pixelgenau angegeben werden.
      Sollen es Pixel sein, so ist ein kleines p an die Zahl anzuhängen (z.B.:
      125p). In unserem Beispiel sollen die Felder sich am Raster orientieren,
      also Spalte 1 und Zeile 1.
Länge
Wie
      viel Zeichen darf der Label lang sein. Soll der Text „Lieferdatum“
      erscheinen, so muss hier mindestens eine 11 eingetragen
      werden.
Beschriftung
Lieferdatum
Tipptext
Ist
      ein Hinweistext, der e
[...]


---

## Beispiel eines Eingabefeldes in Vorgängen

Beispiel eines Eingabefeldes in
Vorgängen
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Das Erstellen eines Eingabefeldes in Vorgängen ist in
vielen Belangen analog zur Erstellung eines „normalen“
Informationsfeldes
. In diesem Beispiel
wird darauf eingegangen, wie man weitere Daten in einer privaten Tabelle
speichern kann.
Erstellen der Tabelle
Hier wird eine private Tabelle erstellt, die eine
zusätzliche Bemerkung zu dem Vorgang speichern soll:
create table
VorgangBemerkungAddon
(
V_Id integer,
Bemerkung char(255),
primary key (V_Id)
)
Erstellen des Feldes
Der Großteil der Einrichtung des Feldes ist analog zu
„Beispiel Informationsfeld“. Der einzige Unterschied besteht in der
Datenbeschreibung:
Der Herkunftstyp ist jetzt eine Relation, zu der man
den Namen und das Ident Feld angeben muss.
Maskenzuordnung
Die Maskenzuordnung ist ebenfalls ähnlich, mit dem
Unterschied, dass der Name einer Vorgangsmaske eingegeben wird und das Ident
Feld V_ID$ heißt.
Gruppenweise Maskenzuordnung
Bis jetzt wurde die neue AIS-Gruppe nur der
allgemeinen Vorgangsmaske zugewiesen. Da einzelne Gruppen aber in der Regel
nicht in allen Vorgangsklassen angezeigt werden sollen, kann man einzelnen
Vorgangsunterklassen bestimmte AIS-Gruppen zuweisen. Dazu geht man in die
Formularzuordnung
[FRZ]
, wählt mit
Ändern
F5
die gewünschte Vorgangsklasse aus und
kann auf dem Register „AIS“ in der Tabelle „Gruppenzuordnung Vorgangskopf“ die
AIS-Gruppen zuordnen.
Um auf der Maske mehr Platz für die AIS-Felder zu
haben, kann man hier zusätzlich die Option-Box auf der Maske verschieben, indem
man ihr eine neue Position zuweist. An diese Position wird die Option-Box
verschoben, sobald mindestens eine AIS-Gruppe angezeigt wird.
Vorgang-Backpatch
Um die Daten in der oben erstellten Beispielrelation
VorgangBemerkungAddon aktuell zu halten und sie wieder zu löschen, wenn der
dazugehörige Vorgang gelöscht wird, muss die Relation noch in die Relation
VorgangBackpatc
[...]


---

## Beispiel Maskenzuordnung

Beispiel Maskenzuordnung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Variante „Maskenzuordnung“
Direktsprung
[AIS]
Man kann den Gruppen prinzipiell auf fünf verschiedene
Arten Masken zuweisen.
1.
Zu bestehenden Masken als zusätzlichen Informationsbereich.
2.
Zu bestehenden Stammdatenpflegern zur Neuerfassung/Änderung.
3.
Als eigenständiger Stammdatenpfleger mit Zuweisung einer eigenen Ident.
4.
Als eigenständiger Pfleger mit Verweis auf eine bestehende Ident.
5.
Als eigenständiges Informationsblatt.
Zuordnung einer Gruppe als
Informationsbereich.
Bei der Einrichtung eines einfachen
Informationsbereiches ist eigentlich nichts weiter zu beachten, als dass die
Daten nicht pflegbar sind. Ansonsten kann man zu jeder Maske in Referenz-ERP Felder
zur Ansicht von Daten hinzudefinieren.
Zuordnung einer Gruppe zu einem bestehenden
Pfleger
Dies ist ein Beispiel für die Zuordnung der Gruppe
„SachKontStammaddonSach0006“ zum Stammdatenpfleger für Sachkonten (der
Maskenname lautet „Sachkontstamm“). Das Feld auf der Maske, das den Wert für den
Primärschlüssel der neuen Zusatzrelation liefert, heißt h.KontoNummer$. Der Typ
bei bestehenden Feldern ist nicht mehr wie früher auf Integer beschränkt. Es
muss auf Groß- und Kleinschreibung geachtet werden.
Es wird hier nicht die Funktion verbinden angezeigt,
da es bei bestehenden Pflegern nicht notwendig ist.
Zuordnung einer Gruppe als eigenständiger
Pfleger
Zu beachten ist hier, dass die Masken AEZADDON bzw.
AEZADDOND sowie die Masken AEZADDONT1 bis AEZADDONT22 als eigenständige
Pflegemaske für das Referenz-ERP Informationssystem entwickelt wurden. Voraussetzungen
sind:
•
Die Anwendung, aus der der Pfleger aufgerufen wird, muss heißen wie die
zu pflegende Relation
•
Die zu pflegende Relation muss ein Identfeld haben, das vom Typ Integer
ist und „IDENT“ heißt.
Die Funktion „
Verbinden
“ legt in diesem
Fall zwei Funktionen an:
Ändern
und
Ansehen
.
Zuordnung einer Gruppe als Pfleger mit Verweis
auf eine beste
[...]


---

## CRW-Archivdefinition

CRW-Archivdefinition
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register CRW-Archivdefinition
Direktsprung
[ANWR]
.
Wird ein Report gedruckt, so ist es möglich diesen
auch zu archivieren. Wenn der Report nicht über
JPP
aufgerufen
wird und dort die Werte für Kundnummer, Belegnummer, Belegdatum und
Belegreferenz nicht übergeben werden, können auf diesem Register dafür diverse
Einstellungen vorgenommen werden.
Feld
Bedeutung
Archivierungsmerkmal
Wie
      soll archiviert werden. Es lassen sich hier mit F3 folgende Einstellungen
      auswählen:
•
nicht
      archivieren
•
archivieren und
      Probleme immer melden
•
archivieren und
      Probleme nur einmal melden
•
archivieren und
      Nachricht im Fehler-/Ereignisprotokoll
Archiv Belegklasse
Für
      Report ist die Belegklasse bisher immer nur CRW-Report(6000) gewesen.
      Jetzt kann hier bei privaten Reporten eine Belegklasse hinterlegt
      werden.
Archivierungsgruppe
Hier
      steht ein Anwenderformat zur Verfügung. Folgende Werte sind von Branchen-ERP
      vorgegeben:
•
keine
      Gruppe
•
Streckengeschäft
•
Führender
      Beleg
Weitere Gruppen können individuell
      erfasst werden.
Ausgabeformat
Im
      Normalfall werden die Reporte im PDF-Format archiviert. Es ist jedoch auch
      möglich, den Report im Word-Format zu archivieren
Je nach Einstellung der Gruppe werden unterschiedliche
Verweise auf Kunden im Archiv hinterlegt:
Keine Gruppe
Wird in den Feldern
nichts angegeben wird der
Report ohne einen Bezug zu einem Kunden bzw. Datum im Archiv gespeichert. Will
man die Zuordnung zu Kontonummer, Belegnummer und Belegdatum im Archiv
herstellen, so müssen die folgenden Felder belegt
werden.
Um einen Report zu archivieren, der eigentlich die
Daten mehrerer Konten enthält, muss er für das Archiv getrennt werden. Intern
wird der Report dann noch einmal, jedoch diesmal pro angesprochenem Konto bzw.
Beleg erzeugt. Das Feld „Select für Archivtrennung“ ist dann für die äußere
S
[...]


---

## Crystal Report definieren

Crystal Report definieren
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Direktsprung
[ANWR]
.
Das Design und die Eingrenzung der Daten der Reporte
werden in Referenz-ERP vom Programm gesteuert. Dazu sind einige Informationen
notwendig, die über diese Anwendung hinterlegt werden.
Feld
Bedeutung
Ident
Die
      eindeutige Identifikation des Reports. Diese ist vierzig Stellen lang. Bei
      der Erfassung wird geprüft, ob ein Report mit dieser Ident existiert und
      ggf. eine Meldung ausgegeben.
Mit der Funktion aw_list kann der Report
      dann aufgerufen werden. Man gibt dazu diese Ident als ersten Parameter
      an.
Private Reporte müssen mit
PR_
beginnen.
Name/Titel
Titel des Reports, wie er in der
      Auswahlliste erscheint. Dieser Titel wird über die Formel „TITEL“ an den
      Report übergeben und kann dort z.B. als Überschrift verwendet
      werden.
Aktiver Report
Dies
      ist nur ein Anzeigefeld. Der unter
Reportdateien
aktivierte Report
      wird hier angezeigt.
NICHT übersetzen
Reporte, die nicht in die
      Übersetzung mit einfließen sollen ( z.B. technische Reporte ), können hier
      von der Übersetzung ausgenommen werden. Dazu ein
Ja
eintragen.

---

## Das Dashboard

Das Dashboard
Administration
Menü
Dashboard
oder
Direktsprung
[DASH]
Ab dem März Release ist es mit der 64-Bit Version
möglich auf einem extra Menü-Register ein Dashboard einzurichten. Ein Dashboard
besteht aus verschiedenen Kacheln mit unterschiedlichen Darstellungsarten.

---

## Datenbeschreibung

Datenbeschreibung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Register Eingabeprüfung
Direktsprung
[AIS]
Hier wird festgelegt, woher der Inhalt der Felder
kommen soll.
Es gibt vier Möglichkeiten – Relation / Prozedur / SQL
/ Favoriten - die Felder mit Inhalt zu versorgen. Im Folgenden wird jeweils auf
die Felder IDENT [,  IDENT2 [,  IDENT3 [,  IDENT4] ] ]
zugegriffen. Die Felder IDENT [,  IDENT2 [,  IDENT3 [,  IDENT4]]]
erhalten ihren Inhalt über die in der Maskenzuordnung zugeordneten
Masken-Feldnamen und sind ein Synonym für diese. Es müssen in der
Maskenzuordnung also immer mindestens genauso viele Identfelder vorhanden sein,
wie hier verwendet. Mehr Informationen hierüber unter
Maskenzuordnung
oder im Beispiel
weiter unten.
ACHTUNG:
Wird auf der Maske als Datenherkunft Favoriten
verwendet, so wird das Feld IDENT von der entsprechenden Ident aus den Favoriten
versorgt. Der Wert in der Maskenzuordnung wird ignoriert.
0. Relation
Das Feld wird mit dem Wert aus der angegeben Relation
gefüllt. Existiert das Feld, dass unter Feldbeschreibung angegeben wurde, nicht
in der Relation, so wird es angelegt. Existiert die Relation noch nicht, so wird
diese angelegt. Dabei wird das unter Identfeld angegebene Feld als
Primärschlüssel angelegt.
Man muss zusätzlich zur Relation mindestens ein
„
Ident Feld
“ angeben. Der „
Handel“
(Bildschirmhandel) ist
optional, sollte aber angegeben werden, wenn man über Makros auf die Felder
zugreifen will, da sich die Feldnamen auf der Maske aus dem Handel und dem
Feldname zusammensetzen. Der von AIS automatisch vergebene Handel kann sich ggf.
ändern. Wurde bereits einmal ein Eintrag mit dieser Relation vorgenommen, so
werden „
Ident Feld
“ und „
Handel
“ so vorbelegt.
Da Tabellen von Referenz-ERP unter Umständen mehr als einen
Schlüssel zur Identifikation besitzen, existieren insgesamt vier
Ident
Felder
.
Das
Ident Feld
ist der Name des
Datenbankfeldes, das den Primärschlüssel zur eindeutigen Identifikation des

[...]


---

## Definition in Referenz-ERP

Definition in Referenz-ERP
Hauptmenü
Administration
Werkzeuge
Branchen-ERP Etikettendruck
Direktsprung
[ETIDR]
.
In die Auswahlliste stehen zwei Varianten zur
Verfügung:
1.
Private Branchen-ERP Etikettendruck Reporte
Hier können sie die Definitionen
hinterlegen, die Reporte mit Anwendungen von Referenz-ERP verbinden und unter
bestimmten Voraussetzungen den Designer vom „Branchen-ERP Etikettendruck“ aufrufen.
2.
Vorlagen Branchen-ERP Etikettendruck Reporte
Hier stehen einige von Branchen-ERP
erstellte Vorlagen, die in den privaten Bereich übernommen werden können.
Definition neu erstellen
In der Variante “Private Branchen-ERP Etikettendruck Reporte“
kann man mit der Funktion „
Neu
F8
“ die Informationen hinterlegen,
die das Programm zur Einbindung und Darstellung benötigt. Es erscheint folgender
Bildschirm:
Besitzer:
Besitzer kann sein
privat
oder
Branchen-ERP
. Reporte mit dem Besitzer Branchen-ERP werden
bei jedem Update überspielt. Sollten sie vorhaben, einen Report mit dem Besitzer
Branchen-ERP zu ändern, muss dieser vorher aus der Vorlage übernommen werden.
Funktionsident:
Dies ist die eindeutige Kennzeichnung des Reports über
die vom Programm auf den Report zugegriffen wird.
Funktionslabel:
Beim
Verbinden
des Reports mit einer
Anwendung wird dieser Label in der Optionbox angezeigt. Wird der Report
archiviert, dann wird der Label als Belegtyp im Archiv eingetragen.
Dateityp:
Der Dateityp kann solange geändert werden, wie noch
kein Report definiert wurde. Es werden drei verschiedene Ausgabeformate
unterstützt.
Etiketten:
         Hier stehen nur Variablen im
Report zur Verfügung.
Karteikarten:     Wie Etiketten, nur
dass nach jeder Karteikartei ein Seitenwechsel durchgeführt wird.
Listen:
Es stehen Variablen für den Kopf und Fußbereich und Felder für die Tabelle zur
Verfügung.
Register Allgemein
Feld
Bedeutung
Datenherkunft
Die
      Datenherkunft kann solange geändert werden, wie noch kein Report definiert
      wurde. Es werden drei Arten der Datenherkunft unterstützt:
1.
Auswahlliste
Der Report bezieht die Da
[...]


---

## Dialog „Datenbank Trace“

Dialog „Datenbank Trace“
Hauptmenü
Administration
Werkzeuge
Tracefile
oder Direktsprung
[
TRON
]
Die Aeins-Trace-Funktionalitäten unterstützen eine
Analyse der aeins-seitig gegen die Datenbank verbrachten Datenbank-Anweisungen.
Zwar sind nicht durchgängig in allen Fällen alle tatsächlich verwendeten
Parameter ermittelbar, aber für einen ersten Überblick sind detaillierte Angaben
über Art und Beschaffenheit, sowie Laufzeitverhalten - auch ohne weitere
Entwicklungswerkzeuge – gegeben.
Felder
Dialog „Datenbank Trace“
Dateiname
Textdatei mit den ermittelten
      Daten.
Diese Textdatei stellt ein
      OSQL-Einspielskript in die Relation „amic_tracefile“ dar. (
Aufbau der
      Datenbank-Tracedatei
)
wie
      öffnen
Überschreiben
Anhängen
Status
Aus
An
Genau
Hochkomma umwandeln
Ja
Nein
Insert am Ende
Ja
Nein
Stammdateninterface
      protokollieren
Ja
Nein
Menüaktivitäten
      protokollieren
Ja
Nein
Funktionen
Dialog „Datenbank Trace“
Datei editieren [F4]
Öffnet die Textdatei im
      Notepad.
Übernehmen [F9]
Übernimmt die getätigten
      Einstellungen

---

## Die Anwendung/Variante Winword / Rtf

Die Anwendung/Variante Winword / Rtf
Hauptmenü
Administration
Werkzeuge
Word2Rtf
In dieser Variante werden die Identitäten aufgelistet,
die eine Zuordnung von RTF-Dokumenten zu Winword-Dokumenten aufweisen.

---

## Eingabeprüfung

Eingabeprüfung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Register Eingabeprüfung
Direktsprung
[AIS]
Beschreibung
Eingabe erforderlich
Wenn
      erzwungen werden soll, dass in das Feld ein Wert eingetragen werden soll,
      dann trägt man hier ein
Ja
ein. Man kann dann dieses Feld nur
      verlassen, wenn es Daten enthält bzw. es wird vor dem Speichern geprüft,
      ob es Daten enthält.
nicht Löschen
Dies
      bedeutet, dass nach dem Speichern dieses Feld nicht gelöscht wird, sondern
      der vorher eingegebene Inhalt erhalten bleibt. Auch springt der Cursor
      nicht wieder in dieses Feld, sondern in das erste Feld, in dem bei „nicht
      Löschen“ ein
Nein
steht.
Itembox
Will
      man die Möglichkeit schaffen, dass die Werte, die in dem Feld eingegeben
      werden können aus einer Liste von Werten auswählt werden können, so hat
      kann man hier eine Itembox angeben, die auf eine Tabelle verweist. Eine
      Liste der Itemboxen erhält man mit
F3
.
Itembox eindeutig
Steht hier ein
Ja
, so muss
      der eingegebene Wert in den Daten der Itembox vorhanden sein. Bei
Nein
dienen die Werte nur als Vorschlag und es können auch Werte
      erfasst werden, die nicht in der Itembox vorhanden sind.
Itembox Information
Häufig gibt es zusätzliche
      Informationen zu Feldern, die sich auf andere Relationen beziehen. Eine
      der häufigsten Informationen, die man sehen will ist die Bezeichnung, die
      einem bestimmten Wert zugeordnet ist. Diese Information kann man hier
      erhalten. Dabei muss man das Feld angeben, wie es in der Itembox in der
      Returnliste steht, gefolgt von „>“ und dem Maskenfeld.
      Beispiel:
LKW_Bezeich>LKWTEXT
Das
      Maskenfeld LKWTEXT muss natürlich auch angelegt werden bzw. auf der Maske
      existieren.
Man
      könnte auch noch mehr Informationen aus der Itembox herauslesen. Dazu kann
      man, mit Komma getrennt, weitere Felder in der obigen Syntax angeben.
      Also:
LKW_Bezeich
[...]


---

## Erstellen eine BI Interfaces

Erstellen eine BI Interfaces
Um auf Basis eine Standardvariante oder einer privaten
Ableitung einer Variante ein BI Interface zu erstellen muss diese Variante in
der Funktion „ENTW Konfiguration“ angesteuert werden:
Die Funktion BI-Interface startet dann einen
Bildschirm, der zwei Hauptfunktionen enthält:
Erzeugung oder Update eines BI Interfaces.
Hinzufügen eines abgeänderten Excel Blattes in dieses
BI Interface.
In dem oberen Bereich wird angezeigt, auf welcher
Datenbankverbindung dieses BI arbeitet, darunter befinden sich die
Identifikationen der Anwendung und der Variante sowie die Kennzeichnung zur
Standard=0 oder Privat=1 Ableitung.
Der mit dem Zahnrad versehene Knopf erstellt nun zu
dieser Variante ein Interface.
Die drei Felder Anwendung Variante und Besitzer können
auch auf dieser Maske angepasst werden, % Platzhalter in den ID Felder sind
erlaubt, d.h. wird in der Anwendung und in der Variante ein % angegeben so wird
für alle 4500 Anwendungsvarianten ein BI Interface mit passendem Menüpunkt
erzeugt.
Während der Erstellphase können mehrere
Fehlerbedingungen auftreten, die wie
hier
beschrieben behoben werden
müssen.
Zum Schluss wird noch automatisch ein Excel Template
erstellt und in die Datenbank verbracht, so dass sofort mit der Arbeit an dieser
Auswertung begonnen werden kann. Hierzu muss einfach nur das Programm verlassen
und wieder neu gestartet werden, um im Informationsbereich den neuen Menüpunkt
zu sehen.

---

## Export / Import

Export / Import
Hauptmenü
Administration
Werkzeuge
Informationssystem
Funktion
F9
Muster/Import/Export
Direktsprung
[AIS]
Grundsätzlich lassen sich nur Mustervorlagen
exportieren und importieren. Diese Mustervorlagen können dann anschließend als
Gruppe übernommen werden bzw. die zu exportierenden Daten mussten vorher als
Mustervorlage vorliegen.
Export
Wenn man „Muster exportieren“ ausgewählt hat, so muss
man zuerst die Mustervorlage angeben – eine Auswahl mit
F3
ist möglich –
sowie den Dateinamen. Mit
F3
öffnet sich für das Feld Exportdateiname
eine Dateiauswahlbox, in der das Verzeichnis und der Dateiname angegeben werden
können.
Ist bei „Datei löschen“ kein Haken gesetzt, werden an
bestehende Dateien die Daten angehängt.
Hat eine Mustervorlage Untergruppen werden diese
automatisch mit exportiert.
Der Export erfolgt im XML-FORMAT (siehe OSQL XMLExport
/ XMLImport).
Import
Bei der Funktion „Muster importieren“ muss lediglich
der Dateiname (Auswahl über eine Dateiauswahlbox mit
F3
) angegeben
werden. Diese Datei muss eine im XML-Format vorliegende Datei sein, die zuvor
mit dem Exportverfahren erstellt worden ist.
Das in dieser Datei existierende Muster wird dann in
die Datenbank übernommen, wobei ein evtl. bereits existierendes Muster mit
demselben Namen überschrieben wird.

---

## Feldbeschreibung

Feldbeschreibung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Register Feldbeschreibung
Direktsprung
[AIS]
Beschreibung
Feldname
Der
      Feldname dient zur Identifikation des Feldes und
muss
angegeben
      werden. (Gruppe und Feldname bilden die Eindeutige Identifikation des
      Datensatzes). In diesem Feld sind nur dann die Zeichen „.“ und „$“
      erlaubt, wenn der Feldtyp
Label
ist oder es sich um ein
existierendes Feld
handelt. Da das Maskensystem die Länge von
      Feldname auf 31 Zeichen beschränkt, sind hier nur 25 Zeichen zulässig. Die
      restlichen 6 Zeichen werden von AIS für interne Zwecke
      verwendet.
Feld
      existiert
Im
      Normalfall werden Felder neu angelegt. Gibt man hier
Ja
ein, so
      geht das System davon aus, dass kein neues Feld angelegt werden soll,
      sondern bestehende Felder modifiziert werden sollen. Das kann z.B.
      Sinnvoll sein, um das Funktionsmenü anders zu positionieren oder um
      Felder, die unbedingt ausgefüllt werden sollen, farbig zu hinterlegen. Es
      stehend dann jedoch nur folgende Einstellungsmöglichkeiten zur
      Verfügung:
•
Datumsprüfung.
      Die Prüfung auf die im Geschäftsjahrstamm eingestellten Werte kann für
      Datumsfelder abgeschaltet werden.
•
Zeile/Spalte
•
Bis
      Zeile/Spalte: wird nur für Felder von Typen Push-Button, Label und Box
      ausgewertet.
•
Länge: Die Länge
      kann nur bis zu maximalen Feldlänge erweitert werden.
•
Schriftart
•
Schrift-/Hintergrundfarbe
•
Tipptext
•
Eingabefeld. Man
      kann Eingabefelder deaktivieren (=
Nein
), jedoch keine deaktivierten
      Felder aktivieren.
•
Verstecken. Man
      kann Felder verstecken (=
Ja
), jedoch keine versteckten Felder
      sichtbar machen.
•
Zu setzende
      JVar
•
Auf dem Register
      Eingabeprüfung die Entry-Funktion, Exit-Funktion und
      Validation-Funktion
Man
      kann alle Einstellmöglichkeiten bis auf
Datumsprüfung,
Eingabefeld
und
Verstecken
leer lassen
[...]


---

## Funktionen

Funktionen
Neues
Planungsrezept
Mit dieser Funktion legen Sie ein neues Planungsrezept
an. Dieses kann ein Gültigkeitsdatum in der Zukunft haben.
Planungsrezept ändern
Sie können die Komponenten abändern oder Zielartikel
hinzufügen oder entfernen. Wenn Sie einen oder mehrere Zielartikel entfernen,
gilt das bisherige Planungsrezept weiter für die entfernten Artikel.
Planungsrezept ansehen
Sie können ein Planungsrezept eines bestimmten Datums
ansehen. Sie sehen u.U. Artikel, für die inzwischen ein neueres Planungsrezept
besteht. Insofern kann die Ansicht von der einer Änderung abweichen, weil dort
nur aktuelle Einträge angezeigt werden.

---

## Funktion Feld verschieben

Funktion Feld verschieben
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Die Funktion ist dafür gedacht einzelne Felder aus
einer Gruppe herauszulösen und einer anderen Gruppe zuzuordnen. Existiert diese
Gruppe noch nicht, wird eine Kopie der Originalgruppe erstellt. Um diese
Funktion auszuführen markiert man die Datensätze, die man einer anderen Gruppe
zuordnen will und wählt dann die Funktion „
Feld verschieben
“
F10
. Es öffnet
sich dann folgende Maske:
Um jetzt das Feld zu verschieben, gibt man den Namen
der neuen Gruppe an. Dazu kann man entweder mit F3 aus einer Liste bereits
vorhandener Gruppen auswählen oder gibt einen neuen Namen für die neu
anzulegende Gruppe an.
Dann wählt man entweder
Speichern
, dann gilt die Änderung jedoch
nur für diesen Datensatz oder „
Alle
ändern
“. Dann wird sofort versucht alle Felder der neuen Gruppe
zuzuordnen. Existiert in der neuen Gruppe bereits ein Feld mit dem Namen, bricht
der Vorgang mit einer entsprechenden Meldung ab.

---

## Funktionen zur Reportbearbeitung

Funktionen zur Reportbearbeitung
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Funktion
Ändern F5
Direktsprung
[ANWR]
.
Wenn man einen Report ausgewählt und ihn zum Ändern
geöffnet hat, stehen folgende Funktionen zur Verfügung:
Funktion
Bedeutung
Report
      aktivieren
Nur
      wenn das Register
Reportdateien
aktiv ist. Sind mehrere Reporte für
      diese Definition angegeben, so kann man mit dieser Funktion einen dieser
      Reporte als den aktiven Report definieren. Man muss dazu vorher die
      Schreibmarke (den Cursor) in der entsprechenden Zeile auf dem Register
      „Reportdateien“ platziert haben. Es erscheint dann in der ersten Spalte
      für den angewählten Report ein Stern (*).
Speichern
Die
      Reportdefinition wird gespeichert und der nächste Datensatz wird
      aufgerufen.
Crystal View
      edit.
Hier
      kann direkt das angegebene View editiert werden. Es öffnet sich dann der
      Editor mit der Viewdefinition. Sind mehrere Views eingetragen, so wird
      entweder das erste View genommen, oder das, auf dem die Schreibmarke (der
      Cursor) steht.
Crystal View
      create
Das
      Programm versucht alle Views neu anzulegen. Eventuelle auftretende Fehler
      werden angezeigt.
Zugehöriger
      Bereich
Hier
      kann man direkt den Bereich, den man unter Auswahlbereich angegeben hat,
      bearbeiten.
Verbinden
Hier
      kann man den Aufruf des Reports direkt einer Anwendung / Optionbox oder
      einem Menü zuordnen. Es wird dabei eine Anwendungsfunktion mit einem
      Controlstring „jpl aw_list Ident“ erstellt und dem Bereich
      zugeordnet.
Report
      aktualisieren
Alle
      Reporte werden zusätzlich in der Datenbank gespeichert und aus dieser
      aufgerufen. Die Reporte in der Datenbank werden nur dann aktualisiert,
      wenn der Report, der sich im rpt-Verzeichnis befindet, jünger ist als der
      in der Datenbank. Hat man nun eine Änderung im Report vorgenommen, sich
      dann
[...]


---

## Gridbeschreibung

Gridbeschreibung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Register Gridbeschreibung
Direktsprung
[AIS]
Wenn auf dem Register “Feldbeschreibung” als Feldtyp
“Grid“ eingestellt wurde, erscheint das Register „Gridbeschreibung“. Was ist ein
Grid? Bei einem Grid handelt es sich um ein Anzeigeformat, das Werte in
Listenform anzeigt. In der Abbildung unten ist ein Grid zu sehen. Es wird
zwischen Grids mit und ohne Neuerfassung unterschieden. In Grids, bei denen die
Datenherkunft auf Relation steht und die Relation den unten angezeigten
Kriterien entspricht, können die Daten geändert werden. Grids mit anderer
Datenherkunft sind nicht änderbar und dienen lediglich zur Darstellung von
Informationen.
Grid für Einfügemodus aktivieren
Dies ist ein Kompatibilitäts-Schalter. In früheren
Versionen wurden im Einfüge-Fall die Daten des Grids nicht gespeichert. Damit
nun nicht dafür geschriebene Lösungen mit der Behebung dieses Problems
kollidieren, wurde dieser Schalter geschaffen. Wenn er auf Ja steht, werden die
Griddaten auch im Einfügen-Fall gespeichert, ansonsten verhält sich das System
wie zuvor.
Feldname
Innerhalb des Grids werden Daten spaltenorientiert
dargestellt. Im Feldnamen gibt man den Namen aus der Tabelle an, der in der
Spalte angezeigt werden soll. Auf der Maske setzt sich der Feldname dann aus dem
Namen des Grids und dem Feldnamen in der Datenbank zusammen
(<GridName>.<Datenbankname>$). Die daraus entstehende Länge darf 31
Zeichen nicht überschreiten.
Überschrift
Hier hinterlegt man die Spaltenüberschrift.
Feldformat
Das Feldformat ist bereits aus der Feldbeschreibung
bekannt. Es existiert auch hier eine Itembox(
F3
) mit einer Auswahl der
möglichen Formate:
Format
Wenn im Feldformat das FS-Format ausgewählt wurde, so
kann man dieses Feld betreten und muss hier das Format eintragen oder es über
F3
auswählen.
Itembox
Wenn in einem Feld nur Werte angegeben werden dürfen,
die auch in einer anderen Tabelle vorhanden sind, so kann man h
[...]


---

## Darstellungsart Balkendiagramm

Darstellungsart
Balkendiagramm
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Balkendiagramm
Das
      Balkendiagramm unterscheidet sich vom den anderen Diagrammarten dadurch,
      dass im Balkendiagramm die Typen der Achsen „vertauscht“ sind. So werden
      im Balkendiagramm für die X-Achse (horizontale Achse) numerische Werte
      erwartet. Die Minimal- und Maximalwerte der X-Achse können mit den Feldern
XAxisMinValue
und
XAxisMaxValue
festgelegt
      werden.
Hinweis:
Im Balkendiagramm kann der Achsentyp
      nicht auf „date“ gestellt werden. Für Datumsangaben werden daher die
      anderen Diagrammarten empfohlen.

---

## Basisdesign

Basisdesign
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Jede Prozedur bzw. jede View kann zur Gestaltung die
folgenden Felder verwenden. Es wird empfohlen eine View für das Basisdesign im
Dashboard zu hinterlegen und für die einzelnen Kacheln in den Prozeduren nur
dort Werte zurückzuliefern, wo eine Abweichung vom Basisdesign gewünscht
wird.
Allgemeingültige Felder
Pixelsize
Optional. Jede Kachel hat
      standardmäßig eine Seitenlänge von 166 Pixeln bzw. ein Vielfaches davon.
      Es kann hier ein Wert zwischen 120 und 360 Pixeln für die zu verwendenden
      Kantenlänge angegeben werden.
Header
Text, der als Überschrift der Kachel
      verwendet wird. Wird dieses Feld nicht von der View geliefert oder ist
      leer, dann wird keine Überschriftzeile generiert und der Platz steht dem
      Mittelteil zur Verfügung.
HeaderForecolor
Optional. Die Vordergrundfarbe der
      Kopfzeile. Ist sie nicht gesetzt, so ist die Schriftfarbe Schwarz. Die
      Angabe aller Farben erfolgt in RGB-Form, entweder hexadezimal mit einem #
      vorweg oder dezimal durch einen Schrägstich '/' getrennt.
'#FF0000‘ as
      headerbordercolor
Oder
'255/00/00'
HeaderBackcolor
Optional. Die Hintergrundfarbe der
      Kopfzeile. Ist sie nicht gesetzt, behält der Hintergrund dieselbe Farbe
      wie der Mittelteil.
HeaderBackcolor2
Optional. Wird HeaderBackcolor2 mit
      angegeben und unterscheidet sich von Backcolor, dann wird die
      Hintergrundfarbe der Kachel als Farbverlauf dargestellt:
Select '255/128/0' as headercolor, '255/254/0' as
      headercolor2
HeaderBorderStyle
Rahmen um die
      Kachel-Überschriftszeile.
•
'none' as
      borderstyle
•
'solid' as
      borderstyle
•
'raised' as
      borderstyle
•
'inset‘ as
      borderstyle
Standardeinstellung ist
      'none'
HeaderBorderColor
Die
      Rahmenfarbe wird nur beim Borderstyle 'solid' ausgewertet.
Headeralign
Ausrichtung der Überschrift.
      Mögli
[...]


---

## Darstellungsart Bild

Darstellungsart Bild
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Bild
Neben den bekannten Feldern muss die
      View zusätzlich ein Feld
Picture
mit dem Bildinhalt
      zurückliefern. Dafür bietet sich das Formulararchiv an. Erlaubte Formate
      sind Bitmap, Icon, JPEG, GIF und PNG.
Beispielview:
CREATE VIEW p_dash_warnung AS
select
(select
      count(*) from fehlerprotokoll where FehlProtDB_USER = USER)
      Anzahl,
if Anzahl
      > 0 then 'Fehlerprotokoll' else '' endif as footer,
'center'
      footeralign,
'#FFFFFF'
      as color,
'#333333' as bordercolor,
'solid'
      as borderstyle,
'Demo-Dashboard' as toolTipHeader,
if Anzahl > 0
then
'Es sind ' || Anzahl
      || ' Einträge im Fehlerprotokoll enthalten. <br>Bitte
      überprüfen.'
else
'Keine
      Fehlerprotokoll-Einträge vorhanden.'
endif as
      toolTipText,
--
-- Bilder können
      aus dem Archiv geladen werden. Dazu benötigt man die FA_ID.
--
AMICBLOB as picture from
      amic_fa_get_from_key(if Anzahl = 0 then 48045 else if Anzahl>10 then
      48044 else 48043 endif endif) as picture

---

## Darstellungsart Säulen-, Flächen und Liniendiagramm

Darstellungsart Säulen-,
Flächen und Liniendiagramm
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Säulen-, Flächen und Liniendiagramm
In
      einem Säulen-, Flächen und Liniendiagramm können jeweils bis zu
zehn
Serien (Datenreihen) angezeigt werden. Dabei wird jede Serie
      in einer eigenen Farbe dargestellt. Jede Serie besteht aus ein oder
      mehreren Datenpunkten. Die Datenpunkte werden mit
X
(Werte der horizontalen Achse) und
Y
(Werte der vertikalen
      Achse) angegeben.
Achsen
Die Diagramme bestehen aus einer
      horizontalen X- und einer vertikalen Y-Achse. Auf der Y-Achse werden
      ausschließlich numerische Werte angezeigt, während auf der X-Achse sowohl
      Text als auch numerische Werte angeben werden können.
Bei der X-Achse ist zu beachten,
      dass die Werte sequenziell - so wie sie von der Prozedur geliefert werden
      - und
nicht
sortiert nach ihren Werten, angeordnet werden.
      Ausnahme: Für Datumsangaben auf der X-Achse kann in der View/Prozedur das
      Feld
XAxisType
mit dem Wert „date“ angegeben werden. Dann werden
      die Werte auf der X-Achse automatisch nach dem Datum sortiert.
Mit den Feldern
XAxisTitle
und
YAxisTitle
kann ein Titel für die Achsen vergeben werden.
      Außerdem kann für die Y-Achse optional ein Minimal- und Maximalwert
      (
YAxisMinValue
und
YAxisMaxValue
) festgelegt werden.
Über die Felder
XAxisInterval
und
YAxisInterval
kann das Intervall für die Beschriftung der X-
      bzw. Y-Achse vorgegeben werden. Gleichzeitig wird hiermit auch der Abstand
      zwischen den Gitternetzlinien festgelegt. Wird ein Wert von „0“ oder kein
      Wert für das Intervall angegeben, so wird das Intervall automatisch
      bestimmt.
Handelt es sich bei X-Achse um eine
      Datumsachse (XAxisType „date“), so wird das Intervall in Form von Anzahl
      in
[...]


---

## Darstellungsart Fortschrittsbalken

Darstellungsart
Fortschrittsbalken
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Fortschrittsbalken
Der
      Fortschrittsbalken benötigt zusätzlich zu den Feldern, die auch die
      Darstellungsart Text haben, noch die Felder, die den ihn
      beschreiben:
ProgressbarMinimum,
      muss den Datenbanktypen integer liefern. Standard ist 0.
ProgressbarMaximum,
      muss den Datenbanktypen integer liefern. Standard ist 100.
ProgressbarValue
,

      muss den Datenbanktypen integer liefern. Der Wert sollte zwischen Minimum
      und Maximum liegen.
ProgressbarText

      (Optional). Wenn nicht angegeben, so wird „{nnn}% vom
      {ProgressbarMaximum}“ ausgegeben
Beispielview:
CREATE VIEW p_dash_fortschritt AS
select
'Auftragseingang' as header,
'von
      01.01.' || year(Today(*)) ||' bis heute' as footer,
'Text' as
      text,
'255/255/255' as Backcolor,
'63/63/63' as bordercolor,
'solid' as borderstyle,
-- Der Fortschrittsbalken benötigt folgende
      Felder
0   as
progressdBarMinimum
,
(select count() from amic_v_vorgaenge vs
      where vs.v_klassnummer=400 and vs.V_Datum=today())
as
progressdBarMaximum
,
(select count() from amic_v_vorgaenge vs
      where vs.v_klassnummer=400 and vs.V_Datum=today() and v_statusUmwand >=
      5)
as
progressdBarValue
,
' ' as
progressdBarText

---

## Darstellungsart Kalender

Darstellungsart Kalender
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Kalender
Der
      Kalender ist ein Control, welches zur Auswahl eines Stichtages verwendet
      werden kann. Das Design ist über folgende Felder in der View/Prozedur zu
      steuern:
•
SelectedDate:
Das Datum, das in der Anzeige als
      ausgewählt erscheint. Das ausgewählte Datum bestimmt den Monat, der
      angezeigt wird. Standard ist das Tagesdatum.
•
Fontname
: Name der Schriftart. Standard ist
      „Verdana“.
•
Fontsize
: Größe der Schriftart. Die Größe
      des Kalenders wird durch die Größe der Schriftart gesteuert. Standard ist
      9.
•
TitleBackColor
: Hintergrundfarbe der Überschrift
      mit Monat und Jahr.
•
TitleForeColor
: Vordergrundfarbe der Überschrift
      mit Monat und Jahr.
•
TrailingForeColor:
Die Farbe für die Tage, die nicht
      zum Monat gehören. Standard ist Transparent.
•
DimensionX
und
•
DimensionY:
Es besteht die
      Möglichkeit mehrere Monate nebeneinander und/oder untereinander
      darzustellen. Standardeinstellung ist 1 für X und 1 für Y. Setzt man z.B.
      für DimensionX auf 4 und DimensionY auf 3 sieht das Ergebnis
      folgendermaßen aus:
Beispielview:
CREATE VIEW
      p_dash_v_kalender AS
select
'Stichtag' as header,
'solid'
      as borderstyle,
'68/68/68' as bordercolor,
'Verdana'
      as fontname,
9.0       as fontsize,
4         as
      DimensionX,
3         as DimensionY
Um
      eine Datenbankvariable mit dem Stichtag setzen zu können, muss diese dann
      in der Refresh-Prozedur gesetzt werden. In dem Feld in_Ident1 wird der
      ausgewählte Tag übergeben.
Beispiel
      Refresh-Prozedur:
CREATE PROCEDURE
      p_dash_refresh_kalender
(in in_board
      integer,
in
      in_kachel integer,
in
      in_ident1 date      default null,
in
      in_ident2 char(100)
[...]


---

## Darstellungsart Deutschland-/Europakarte

Darstellungsart
Deutschland-/Europakarte
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Deutschland- und Europakarte
Es
      steht eine Karte von Deutschland und Europa zur Verfügung, in der man sich
      Google-Maps Koordinaten anzeigen kann. Zusätzlich zu den Standardfeldern
      müssen die Felder
Label, X,
      Y
angegeben werden.
Der
      Label lässt sich mit HTML formatieren und wird angezeigt, wann man mit der
      Maus über einen Punkt fährt.
Ein
      weiteres optionales Feld „
Serie
“ bestimmt das Symbol und die Farbe.
      Serie muss im Bereich von 0 bis 9 liegen. Jede Serie wird mit einer
      anderen Farbe und einem anderen Symbol dargestellt:
Serie 0
Serie 1
Serie 2
Serie 3
Serie 4
Serie 5
Serie 6
Serie 7
Serie 8
Serie 9
Zu
      einer Serie kann man einen
SeriesTitle
angeben, der erscheint, wenn
      man auf den Knopf rechts oben klickt. Dieser Knopf ist nur dann sichtbar,
      wenn man mehrere Serien verwendet. Hierüber können dann einzelne Serien
      ein- und ausgeblendet werden.:
Mit
      dem mittleren Mausrad oder den Tasten Bild
▼
und Bild
▲
lässt sich ein Ausschnitt
      vergrößern oder verkleinern.
Mit
      Strg+Maus lässt sich ein Bereich auswählen.
Mit
      den Pfeiltasten lässt sich der Bereich verschieben.
Mit
      Pos1 wird die Anfangsgröße wieder herstellen.
Fährt man mit der Maus auf ein
      Symbol der Serie, so wird der mit Label angegebene Text
      eingeblendet.
Ist
      eine Klick-Funktion angegeben, so wird ein Hand-Symbol als Mauszeiger
      angezeigt, wenn man mit der Maus über einen Punkt fährt.
Beispielview mit Rückgabe der
      Adressid der angezeigten Anschrift:
CREATE VIEW p_dash_geographicMap AS
select
'solid'
      as borderstyle,
'#333333'
      as bordercolor,
-- Pro Angezeigter
      Position muss ein Datensatz mit dem
-- >label< u
[...]


---

## Darstellungsart Skala

Darstellungsart Skala
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Skala
Die
      Skala ähnelt sehr dem Fortschrittsbalken, hat jedoch ein paar mehr
      Einstellmöglichkeiten:
Minimum
muss den Datenbanktypen integer liefern.
            Standard ist 0
Maximum
muss den Datenbanktypen integer liefern.
            Standard ist 100.
Value
Der Wert wird durch den Zieger
            dargestellt. Er muss den Datenbanktypen integer liefern und zwischen
            Minimum und Maximum liegen.
Majorinterval
Das Intervall des Markers unter den
            Zahlen. Standartmäßig wird dieses Intervall mit (Maximum-Minimum) /
            5 berechnet.
Minorinterval
Das Intervall für die kleineren
            Markierungen. Standartmäßig wird dieses Intervall mit Majorintervall
            / 5 berechnet.
Farbangaben
Die Skala kann in bis zu drei Farbbereiche
            unterteilt werden.
LowerFillingColor
Die Farbe am linken Rand, in den
            Beispielabbildungen ist es die Farbe #FF3333. Wenn keine Farbe
            angegeben wird, dann wird die Hintergrundfarbe verwendet. Es wird
            ein Verlauf von LowerFillingColor auf Fillingcolor dargestellt.
LowerFillingTo
Eine Zahl, die zwischen Minimum und
            Maximum liegen muss. Diese Zahl gibt die Breite an, die
            LowerFillingColor einnehmen darf. Setzt man diesen Wert auf Minimum
            werden nur FillingColor bzw. UpperFillingColor
            dargestellt.
Hinweis:
Soll es so aussehen, als ob nur
            zwei Farben verwendet werden, so setzt man LowerFillingTo auf
            Minimum.
FillingColor
Die Farbe wird zwischen zwischen
            LowerFillingTo und UpperFillingFrom dargestellt.
UpperFillingColor
Die Farbe am rechten Rand, in den
            Beispielabbildungen ist es die Farbe #33FF33. Wenn keine Farbe

[...]


---

## Darstellungsart Kombinationsdiagramm

Darstellungsart
Kombinationsdiagramm
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Kombinationsdiagramm
Das
      Kombinationsdiagramm unterscheidet sich vom
Säulen-, Flächen- und Liniendiagramm
dadurch, dass im Kombinationsdiagramm für jede Serie eine Darstellungsart
      ausgewählt wird. Die Darstellungsart wird in der View/Prozedur mit dem
      Feld
SeriesType
angegeben.
Es
      kann zwischen folgenden Typen gewählt werden:
•
Area
      (Fläche)
•
Column
      (Säule)
•
Line
      (Linie)

---

## Darstellungsart Tachometer

Darstellungsart Tachometer
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Tachometer
Für
      das Tachometer können in der View/Prozedur folgende Felder eingerichtet
      werden:
Minimum
Der minimale Wert des Tachometers. Der
            Standardwert ist 0.
Maximum
Der maximale Wert des Tachometers. Der
            Standardwert ist 100.
Value
Mit dem Feld
Value
wird der Wert
            angegeben, der mit dem Zeiger dargestellt werden soll. Der Wert wird
            außerdem im unteren Bereich des Tachometers (unterhalb des Zeigers)
            angezeigt. Er muss zwischen Minimum und Maximum liegen.
Majorinterval
Das Intervall für die Hauptmarkierungen
            (mit den Zahlen). Standartmäßig wird dieses Intervall mit
            (
Maximum
-
Minimum
) / 10 berechnet.
Minorinterval
Das Intervall für die kleineren
            Markierungen. Standartmäßig wird dieses Intervall mit
Majorinterval
/ 5 berechnet.
Farbangaben
Das
      Tachometer kann in bis zu drei Farbbereiche unterteilt werden.
LowerFillingColor
Mit
LowerFillingColor
wird die
            Farbe am linken Rand angegeben. In der Beispielabbildung ist es die
            Farbe #FF3333. Wird keine Farbe angegeben, dann wird die
            Hintergrundfarbe verwendet.
LowerFillingTo
Mit diesem Feld wird angegeben, bis zu
            welchem Wert die
LowerFillingColor
angezeigt werden soll. Der
            Wert muss zwischen dem Minimum und dem Maximum liegen.
FillingColor
Hier wird die Farbe angegeben, die
            zwischen
LowerFillingTo
und
UpperFillingFrom
dargestellt werden soll. In der Beispielabbildung wird die Farbe
            #ffff66 verwendet.
UpperFillingColor
Mit
UpperFillingColor
wird die
            Farbe am rechten Rand angegeben. In der Beispielabbildung ist es die
            Farbe #33FF33. Wird keine Farbe angegeben, dann wir
[...]


---

## Darstellungsart Tabelle

Darstellungsart Tabelle
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Tabelle
In
      dieser Tabelle lassen sich ausgewählte Daten darstellen. Die Tabelle ist
nicht
für Massendaten vorgesehen und bietet
nicht
die
      Möglichkeiten der Auswahlliste. Die angegebene Klick-Funktion reagiert
      beim Klick auf die Zeile. Aus der zugrundeliegenden View werden alle
      Spalten, die mit „
col(
“ beginnen,
      angezeigt. Dabei steht in Klammern die Überschrift. Die Breite richtet
      sich nach der Breite der Datenfelder, numerische Werte werden immer mit
      zwei Nachkommastellen ausgegeben.
Beispielview:
Create view p_dash_tabelle
Select TOP
      20
(select Count(*) from offenerposten where KontoNummer
      = k.KontoNummer ) as AnzahlOPs,
(select sum(kontoSumerfSoll-KontoSumerfhaben) from
      kontosummen where KontoNummer = k.KontoNummer ) as SummeOPs,
kundbezeich    as "
col(Bezeichnung)
",
AnzahlOPs      as "
col(OPs)
",
SummeOPs       as "
col(Saldo)
",
KundId       as
      ID1,
ans.AdressId as ID2,
if
      ans.AdressId = pdb_adressid then 1 else 0 endif as selected
From Kundenstamm k
join
      anschriftstamm ans on ans.adressid=k.adressidhauptadr and adresstyp =
      11
join anschriftgeodata geo on
      ans.adressid=geo.adressid
where
      kundid>0 and kundloekennz=0
order by
      AnzahlOps desc
Um
      auf das Klicken in eine Zeile zu reagieren und ggf. mehr Informationen
      anzuzeigen, kann dies mit der Refresh-Prozedur geschehen. An die Prozedur
      werden die Werte übergeben, die in der View/der Prozedur als ID1, ID2, ID3
      und ID4 geliefert werden.
Beispiel
      Refresh-Prozedur:
CREATE PROCEDURE
      p_dash_Refresh_tableview
(in in_board integer,
in in_kachel
      integer,
in in_ident1 integer
      default null,
in in_ident2 integer
      default null,
in in_
[...]


---

## Darstellungsart Tortendiagramm

Darstellungsart
Tortendiagramm
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Tortendiagramm
In
      einem Tortendiagramm können bis zu zehn Datensätze („Tortenstücke“)
      angezeigt werden. Der Wert und die Bezeichnung des Datensatzes werden in
      der View/Prozedur mit den Feldern
Wert
und
Label
angegeben.
Im
      Tortendiagramm besteht die Möglichkeit kleinere Tortenstücke in einem
      einzelnen Tortenstück („Sonstige“) zusammenzufassen. Dazu wird in der
      View/Prozedur dem Feld
OthersCategoryInPercent
ein Wert größer 0
      zugewiesen. Mit diesem Wert gibt man eine Schwelle an, unter der alle
      Tortenstücke zusammengefasst werden. Beispiel:
In
      der View wird für das Feld OthersCategoryInPercent eine 2 angegeben. Dann
      werden alle Datensätze, die weniger als 2% ausmachen, in dem Tortenstück
      „Sonstige“ zusammengefasst.
Hinweis:
Auf dem Tortenstück „Sonstige“ kann
      keine Klick-Funktion ausgeführt werden. Des Weiteren wird im Tooltip nur
      der Text „Sonstige“ angezeigt.
Legende
Mithilfe des Feldes
LegendVisible
kann eingestellt werden, ob die Legende standardmäßig
      ein- oder ausgeblendet ist. Unabhängig von dieser Option kann die Legende
      über die Funktion
Legende
      ein-/ausblenden
(rechte Maustaste auf der Kachel) aktiviert bzw.
      deaktiviert werden. Des Weiteren ist die Position (
LegendPosition
)
      und die Ausrichtung (
LegendOrientation
) der Legende über die
      View/Prozedur einstellbar. Mögliche Werte sind:
LegendPosition
•
Right
•
Left
•
Bottom
•
Top
LegendOrientation
•
Vertical
•
Horizontal
Hinweis:
Im Tortendiagramm besteht die
      Möglichkeit die Klick-Funktion über die Legende
      auszuführen.
Tooltipp
Mit
      dem Feld
SliceTooltip
kann der Tooltip über HTML formatiert werden.
      Der Tooltip erscheint, wenn der Maus
[...]


---

## Darstellungsart Text

Darstellungsart Text
Administration
Menü
Dashboard
Variante Kachel
oder
Direktsprung
[DASH]
Variante
Kachel
Neben den hier beschriebenen Feldern stehen zusätzlich
alle Felder aus dem
Basisdesign
zur Verfügung.
Text
Für
      die Darstellungsart Text benötigt die View zusätzlich zu den
      Standardfeldern nur das Feld
Text
. Optional kann noch Textalign
      verwendet werden, um anzugeben, wo der Text dargestellt wird. Mögliche
      Werte sind 'left', 'center' und 'right'. Wird Textalig nicht angegeben, so
      wird der Text zentriert dargestellt.
Beispielview:
CREATE VIEW p_dash_button_oder_text AS
select
'Auftragsvolumen' as
Header
,
trim(AMIC_FSTR(sum(WaBewWert), 20, 2))
      as
Text,
'center' as
Textalign
'vom 01.01.'|| year(today(*)) || ' bis heute'  as
Footer,
'255/255/255' as
      color,
'
solid
' as borderstyle,
'#333333' as
      bordercolor
from
. . .

---

## Kontoblätter mit dem Branchen-ERP Etikettendruck drucken

Kontoblätter mit dem Branchen-ERP Etikettendruck drucken
Hauptmenü
Administration
Werkzeuge
Etikettendruck
Direktsprung
[FRM]
Man kann sich mit dem Branchen-ERP Etikettendruck eigene
Kontoblätter erstellen. Damit hat man die Möglichkeit sich alle Daten, die auf
Kontoblättern benötigt werden, zusammen zu suchen und den Report so zu
gestalten, dass auch das Design das eigene Unternehmen wiederspiegelt. In den
Vorlagen zum Branchen-ERP Etikettendruck existiert ein Report „Kontoblatt“. Diesen kann
man mit der Anwendung „KONTOBLATT_INTERN“ (Kontoblätter) oder
„KONTOBLATT_ARCHIV“ (Kokore)  verbinden und so die erstellten Kontoblätter
ausdrucken bzw. den Report bearbeiten.
Die Daten dieses Vorlagekontoblattes werden auf Basis
eine Views („p_etikettendruck_kontoblatt“)  zusammengesucht und dann als
Liste ausgedruckt.
Die Firmenanschrift ist fest im Beispielreport
eingetragen und muss angepasst werden.
Als Steuerinformation wird der im Steuersatz
hinterlegte Exportschlüssel ausgegeben. So kann man die Kombination aus Klasse,
Gruppe und Schlüssel auch für Kunden, die ggf. diesen Report als Kokore
erhalten, lesbar darstellen.

---

## Maskenzuordnung

Maskenzuordnung
Hauptmenü
Administration
Werkzeuge
Informationssystem
Variante „Maskenzuordnung“
Direktsprung
[AIS]
Bei der Zuordnung der erstellten Gruppen zu den Masken
gibt es prinzipiell vier verschieden Arten:
1.
Zuordnung zu bestehenden Masken als zusätzlichen Informationsbereich. Hier sind
z.B. die Konteninformation bzw. OP-Verwaltung zu nennen. Hier kann AIS nur zur
Anzeige benutzt werden. Will man hier Daten speichern, so muss dies
selbstständig programmiert werden.
2.
Zuordnung zu bestehenden Stammdatenpflegern zur Neuerfassung/Änderung.
3.
Einbindung als eigenständiger Stammdatenpfleger mit Zuweisung einer eigenen
Ident.
4.
Einbindung als eigenständiger Pfleger mit Verweis auf eine bestehende Ident.
Bei der Zuordnung zu bestehenden Masken ( 1. und 2. )
können bis zu vier Identfelder zugeordnet werden. Dies ist ggf. dann notwendig,
wenn der eindeutige Schlüssel aus mehr als einem Feld besteht.
Man kann einer Maske grundsätzlich mehrere Gruppen
zuordnen.
Maske
Welcher Maske soll diese Gruppe zugeordnet werden?
Dies kann ein existierender Stammdatenpfleger sein. Den Maskennamen eines
Stammdatenpflegers erhält man durch Drücken von
shift+strg+F5
auf der
entsprechenden Maske. Im Kundenstamm lautet der Name der Maske z.B. TBKUNSTB.
Soll es ein eigenständiger Pfleger werden, so stehen hier die Masken
AEZADDON oder AEZADDOND sowie die Masken AEZADDONT1 bis AEZADDONT22, bei denen
Register verwendet werden können, zur Verfügung. Die Maske AEZADDOND
unterscheidet sich nicht von AEZADDON. Bei diesen eigenständigen
Stammdatenpflegern kann nur eine Ident Name/Wert erfasst werden. Der Name wird
mit h.Ident$ vorbelegt.
Die Masken AEZADDON(D) und AEZADDON
T
unterscheiden sich inhaltlich dadurch, dass
bei der Maske AEZADDON(D) immer nur eine Gruppe dargestellt wird und bei den
Masken AEZADDONT1 bis 22 jeweils alle unter der Maskenzuordnung angegebenen
Gruppen gleichzeitig dargestellt werden.
Vollbildmodus
Hier wird eingestellt, ob die Maske i
[...]


---

## Menü-Favoriten

Menü-Favoriten
Administration
Menü
Favoriten
oder Direktsprung
[
MENUV
]
Die Menü-Favoriten (kurz Favoriten) stellen eine
bequeme Möglichkeit dar aus dem jeweiligen Haupt-Menü bestimmte vordefinierte
Programm-Punkte per Mausklick zu erreichen.
In dieser Anwendung werden die Favoriten der Anwender
aufgelistet, und man erhält die Möglichkeit die Sortierung durch einen Pfleger
vorzugeben.
Felder
Auswahlliste
  Favoriten
Kurzname
Kurzname des Bedieners
Sortierung
Anhand dieser Angabe wird die
      Sortierung vorgenommen.
Beschriftung
Beschriftung des
      Favoriten
Funktion
Funktions-Identifikation
Funktionsart
Funktionsart
Rollenerlaubnis
Ja/Nein
Die
      Funktion, die den Favoriten kennzeichnet, kann durchaus in mehreren
      Kontexten vorkommen. Damit ein Favorit auch angezeigt wird benötigt er in
      mindesten einem dieser Kontexte eine Erlaubnis per zugeordneter
      Rolle!
Die
      Rollenerlaubnis wird
rot
hinterlegt, wenn keine
      Rollenerlaubnis mehr vorliegen sollte.
Suchen
Auswahlliste
  Favoriten
Kurzname
Kurzname des Bedieners
Mit
      [
F3
] kann ein Kurzname ausgewählt werden.
Vorbelegung ist der Kurzname des
      aktuellen Aeins-Bedieners.
Beschriftung
Like
Funktion
Like
Funktionsart
Gleich
Funktionen
Auswahlliste
  Favoriten
Favoriten Sortierung
Menü-Favoriten-Sortierung

---

## Mimetypen in Referenz-ERP

Mimetypen in
Referenz-ERP
Hauptmenü
Administration
Archiv
Mime
Direktsprung
[MIME]
In dieser Variante werden die verwendbaren Mimetypen
aufgelistet. Diese Mimetypen werden mit dem Update von Referenz-ERP ausgeliefert.
Felder
Mime
Multipurpose
      Internet Mail Extensions
Extension
Dateinamenserweiterung
(Schlüssel der Relation
      AMIC_MIME)
Archiv-Volltext
Kennzeichen ob ein interner Filter
      existiert, der aus dem zugehörigen Blob Archivtext generiert
Archiv-Vorschau
Kennzeichen ob im Archiv(Strg+F12)
      eine Vorschau implementiert ist
Blob
Kennzeichen ob es sich
      programm-technisch um einen
"Blob"
handelt.
Beschreibung
Ebendies.
PDF
Kennzeichen ob es sich um
PDF
handelt.
Link
Kennzeichen (reserviert)
Signatur
Kennzeichen ob der Mimetyp im Sinne
      von Referenz-ERP „signaturfähig“ ist.
Kennung
Interne Referenz-ERP-Kennzeichnung und
      Kriterium für Referenz-ERP-Auslieferung.
Mimetypen mit einer Kennung kleiner
      1000 werden mit „skip on existing“ ausgeliefert.
Die
      Auslieferungsmethode „On Existing Skip“ bedeutet Kunden haben nach der
      erstmaligen Auslieferung freie Hand; Entwickler müssen (notwendige)
      Änderungen per ATF ausliefern!
Archiv-Icon
Die
      Archiv-Anzeigen-Funktionen ermitteln die Icon-Zuordnungen einmalig zur
      Laufzeit aus der Windows-Systemregistrierung. Dies geschieht deshalb,
      damit der Anwender „seine“ Programme dort visuell wiederfinden
      kann.
Da
      aber das lesen aus der Windows-Registrierung von Administratoren
      unterbunden sein kann bzw. diese Windows-Registrierung gar nicht mehr den
      aktuellen Plattenzustand widerspiegelt (z.B. fehlerhafte Deinstallation
      von Programmen) musste ein Weg gefunden werden der zumindest ein
      Default-Icon anzeigt, das im Falle der Nicht-Verfügbarkeit angezeigt
      werden soll.
Den
      Namen der entsprechenden Aeins-Ressource kann hier hinterlegt
      werden.
Der
      Name muss mit der entsprechenden Aeins-Ressource korrelieren. Es b
[...]


---

## Mustervorlagen

Mustervorlagen
Hauptmenü
Administration
Werkzeuge
Informationssystem
Funktion
F9
Muster/Import/Export
Direktsprung
[AIS]
Mustervorlagen können selber erstellt oder von Branchen-ERP
vorgegebene Muster können als Vorlage für eigene AIS-Anwendungen verwendet
werden. Muster von Branchen-ERP beginnen immer mit „
AMIC_
“. Bei den Mustern von
Branchen-ERP gibt es eine Besonderheit:
Ruft man mit der JPL-Funktion AISLOAD eine Gruppe
auf, die nicht existiert, so wird vom System geprüft, ob es eventuell eine
Gruppe in den Mustervorlagen gibt, die mit AMIC_ beginnt und sonst so heißt, wie
die angegebene Gruppe. Diese wird dann automatisch übernommen, es sei denn, die
Gruppe besitzt Untergruppen und diese existieren bereits. Dieser Fall wird dann
im Fehlerprotokoll festgehalten.
Als Muster speichern
Alle erstellten Gruppen lassen sich als Mustervorlagen
speichern.
Dazu gibt man zuerst den Namen der Gruppe an –
vorbelegt ist dieses Feld mit der zurzeit in der Auswahlliste aktiven Gruppe.
Existieren in der ausgewählten Gruppe verweise auf anderen
Gruppen
, so werden diese in der gleichen
Spalte mit angezeigt.
Man muss dem neuen Muster einen Namen geben, der auch
vom dem Original abweichen kann. Hier wird der Name der Originalgruppe
vorbelegt. Existiert bereits ein Muster mit diesem Namen, so wird am Ende eine
Zahl angehängt. Diese Vorbelegung kann man jederzeit ändern.
Gibt man keinen Namen in der Spalte „übernehmen als
Muster“ an, so wird auch die Gruppe bzw. Untergruppe nicht mit übernommen. Gibt
man den Namen eine existierenden Musters an, so erscheint die folgende Meldung
für
jedes
existierende Muster.
Wird diese Sicherheitsabfrage mit
Ja
beantwortet, oder existiert ein Muster mit diesem Namen noch nicht, so wird die
Einrichtung als Mustervorlage übernommen.
Aus Muster übernehmen
Will man eine Mustervorlage übernehmen und in die
eigene Anwendung einbinden, so muss man die Funktion “Aus Muster übernehmen“
anwählen. Zuerst wählt man eine Mustervorlage aus. Eine Liste der existieren
[...]


---

## Optionbox

Optionbox
Administration
Werkzeuge
Optionboxes bearbeiten
oder Direktsprung
[
OB
]
Die „Optionbox“ gruppiert Funktionen und bildet mit
diesen und weiteren kontext-abhängigen Optionboxen den sogenannten „Kontext“ zum
Zeitpunkt der Ausführung.
Private Optionboxes sind konventionsgemäß solche,
deren Identifikation mit „POB_“ bzw. „PO_“ beginnt.
Felder
Dialog „Option
  Boxes“
OptionBox Id.
Identifikation der
      Optionbox
Mit
      [
F3
] lässt sich eine Optionbox auswählen.
Funktionen
Neu
Nach
      Eingabe der „OptionBox Id.“ erfolgt der Wechsel in den Optionbox-Pfleger,
      falls es die Optionbox noch nicht gibt.
Ändern
Nach
      Eingabe der „OptionBox Id.“ erfolgt der Wechsel in den Optionbox-Pfleger,
      falls es die Optionbox gibt.
Löschen
Löscht die Optionbox ohne
      Rückfrage.
Steht nur Entwicklung zur
      Verfügung.

---

## OSQL

OSQL
Alle folgenden Befehle sind nicht SQL-Standard,
sondern unter Aeins implementiert, um kurzfristige systemnahe Operationen zu
vereinfachen bzw. um Skripte für einmalige Prozesse zu schreiben. Weiterhin
können JPL und Pascalskripte von hier aus gestartet werden.
Handhabung
In dem Eingabefenster links oben können SQL-Befehle
eingegeben und mit
F9
ausgeführt
werden. Das Ergebnis erscheint dann in dem Feld darunter. Will man wieder auf
den vorherigen Befehl zugreifen, so kann man mit
Strg+Pfeil nach Oben
bzw.
Strg+Pfeil nach Unten
in den Kommandos
blättern. Mit
Strg+F3
kann man eine
F3-Auswahl öffenen in der alle bisher ausgeführten Befehle angezeigt werden. Man
kann dort auch auf Befehle anderer Benutzer zugreifen.
Eine weitere hilfreiche Taste ist
Tab
bzw.
Shift+Tab
. Mit ihr kann zwischen den
Tabellen, Views, Prozeduren und Triggern – dies wird je nach Kommando bestimmt –
weitergeblättert werden. Bei
Tab
wird
das in alphabetischer Reihenfolge nächste Datenbankobjekt angezeigt, bei
Shift+Tab
das vorherige. Gibt man als
z.B.
show view
AMIC_V_D
und drückt
Tab
, dann wird das Kommando automatisch
auf
show view
AMIC_V_DATEVSTAMM
erweitert.
Will man ein Datenbankobjekt eines bestimmten
Anwenders sehen, so kann man dessen Kürzel vorwegstellen (In diesem Fall Test
Bediener: TB). Dies wird auch von
Tab
und
Shift+Tab
berücksichtigt:
show VIEW
TB.MandantBitmap

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

## Produktion

Produktion
Produktion
anlegen
Produktionen können auf zweierlei Weisen angelegt
werden:
1.
Angabe eines Produkts mit automatischer Auflösung eines Rezepts. (klassisch)
Produktion
mit Scanner
In diesem Fall geben Sie als
einzige Position den Produktartikel mit seiner Menge an.
Im Vorgangstamm lassen Sie
das Feld „Importtyp“ bitte auf NULL bzw. setzen eine 0 ein.
2.
Angabe eines Produkts und der Komponenten mit Kennungen
In diesem Fall setzen Sie
zunächst im Vorgangstamm das Feld „Importtyp“ bitte auf 1.
In der Tabelle
ImportvorgPosition muss für das Produkt nun das Feld „ArtikelVariante“ mit 201
gekennzeichnet werden. Die Stücklistenkomponenten werden mit der Artikelvariante
101 gekennzeichnet.
Für Wertartikel gelten
entsprechend 102.
Produktion
ändern
Produktionen können auf zweierlei Weisen geändert
werden:
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
Die Zuordnung von Produkt
und Komponenten erfolgen wie oben beschrieben über die ArtikelVariante in der
ImportVorgPosition.

---

## Produktion

Produktion
Scanne Produktionslaufzettel.
Und es erscheint auf dem Scanner folgend Anzeige:
Die produzierte Menge eingeben.
Eingabe mit der Taste „ENT“ bestätigen. Danach
erscheint folgende Anzeige:
Entweder kann jetzt der Ende-Code gescannt (vom
Produktionszettel) werden oder es kann eine weitere Menge für eine Partie
eingegeben werden.
Nach dem Scannen des Ende-Codes werden nacheinander
alle Aufträge und der dazugehörige Kommisionierplätze für diesen Artikel
angezeigt.
Das entsprechende Regal scannen und es erscheint
folgende Anzeige:
Die aus dem Regal 801 (Palette aus der Produktion)
entnommene Menge eingeben und mit der Taste „ENT“ bestätigen. Anschließend die
verbleibende Restmenge auf Regal 801 eingeben und mit der Taste „ENT“
bestätigen.
Wird eine falsche Restmenge eingegeben erscheint
folgende Anzeige:
Die vorhandene Restmenge ist erneut einzugeben. Danach
erscheint eine Aufforderung zum Eingeben der Prüfziffer des Regals. Anschließend
erscheint folgende Anzeige:
Es ist das Zielregal für die vorhandene Restmenge
einzugeben. Danach ist die Umbuchungsmenge einzugeben. Abschließend ist die
Prüfziffer des Zielregals einzugeben.
Jetzt kann die nächste Produktion verarbeitet
werden.

---

## Reportdateien

Reportdateien
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Register Reportdateien
Direktsprung
[ANWR]
.
Man kann zu einer Reportdefinition mehrere physische
Reporte angeben, die alle mit derselben Datengrundlage arbeiten.
Feld
Bedeutung
(erste Spalte)
Der
      aktive Report ist mit einem Stern * gekennzeichnet. Bei mehreren Reporten
      kann man den markierten Report durch die Funktion
„Report
      aktivieren“
F4
aktivieren.
(zweite Spalte)
Hier
      steht entweder A wie Branchen-ERP oder p, wenn es sich um einen privaten Report
      handelt, der dieselbe Reportdefinition verwenden soll.
Reportdatei
Der
      Name des Reports. Ohne Verzeichnis. Steht der Report nicht im
      RPT-Verzeichnis von Referenz-ERP, so trägt man dieses in die Spalte
      „Reportverzeichnis“ ein.
Sprache
Referenz-ERP kann in verschiedenen
      Sprachen laufen. Wenn man einen Report speziell für eine andere Sprache
      als Deutsch ( Nummer 0 ) entwickelt hat, so kann man hier die Sprache
      hinterlegen. Für Benutzer mit Sprache 0 wird dann weiterhin der
      Standardreport vorbelegt, für Benutzer, die im Bedienerstamm eine
      abweichende Sprache eingetragen haben, wird dann dieser Report
      verwendet.
Reportverzeichnis
Bei
      abweichendem Verzeichnis - also nicht das RPT-Verzeichnis – wird hier das
      Verzeichnis angegeben.

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

## Variante „Server-/Verbindungs-Eigenschaften“

Variante „Server-/Verbindungs-Eigenschaften“
Hauptmenü
Administration
Werkzeuge
Server-/Verbindungs-Eigenschaften
Direktsprung
[
SRVPROP
]
Mit Hilfe dieser Variante lassen sich die
Server-Properties des Datenbank-Servers einsehen und recherchieren.
Weitere Erläuterungen siehe
Zugreifen
auf Werte von Verbindungseigenschaften
und
Zugreifen
auf Werte von Datenbankservereigenschaften
.
Felder
Auswahlliste
Eigenschaft
Gibt
      an ob das eine Servereigenschaft ist oder eine
      Verbindungseigenschaft.
Nummer
Jede
      Verbindung hat eine eindeutige Nummer, welche vom System vergeben
      wird.
Name
Verbindungseigenschaftsname
Beschreibung
Kurze Erläuterung der
      Verbindungseigenschaft
Wert
Der
      Wert der Verbindungseigenschaft
Auswahlbedingungen
Finden
Führt eine Like-Suche in den Feldern
      Name, Beschreibung und Wert durch.
Nummer
Hiermit kann über die
      Verbindungsnummer gesucht werden. Diese lässt sich über die
      Verbindungseigenschaft mit dem Namen „AppInfo“ ermitteln.
Eigenschaft
Hiermit kann man entweder nach
      „Verbindung“ oder „Server“ gesucht werden.
Funktionen
keine

---

## Technische Information zur Konfiguration des Thales-Terminals

Technische Information zur Konfiguration des Thales-Terminals
Es gibt im Terminal zweierlei Konfigurationen, die
separat einzustellen sind:
1.
Die Einstellung,
wie das Terminal mit dem Netzanbieter kommunizieren soll.
Diese Einstellung ist i.d.R. zwischen ISDN und LAN
einzustellen.
2.
Die Einstellung,
wie das Terminal mit der Kasse kommunizieren soll.
Diese Einstellung ist möglich zwischen
COM-Port(RS232), USB und LAN. Referenz-ERP unterstützt jedoch nur COM und LAN.
Bitte beachten Sie, dass in der Regel die
Kommunikation zwischen dem Terminal und Referenz-ERP konfiguriert werden muss. Die
Einstellung entnehmen Sie bitte dem Handbuch des Terminals. Auf der Webseite
http://www.easycash.de/anleitungen.html
finden Sie Bedienungsanleitungen verschiedener gängiger Terminals.
Hier die Hinweise zu dem von uns getesteten Terminal
Thales Artema Hybrid und sind ohne Gewähr:
•
Die Voreinstellung des Konfigurationspassworts des getesteten Terminals
Thales Artemis Hybrid ist 111111.
Einstellung der Verbindung zum
Netzanbieter
Verwaltung
Service
Service-Funktionen
DFÜ-AUSWAHL
LAN   (für LAN)
Einstellung der Kommunikation mit
der Referenz-ERP-Schnittstelle
•
Verwaltung
Service
Service-Funktionen
Kassenprotokoll
ZVT
aktiv
•
Verwaltung
Service
Service-Funktionen
Kassenprotokoll
Schnittstelle
LAN
(Für LAN-Betrieb)
•
Verwaltung->Service
Service-Funktionen
DFÜ-Parameter
DHCP
JA
(für DHCP)
•
Verwaltung
Service
Service-Funktionen
DFÜ-Parameter
IP-Adresse
(zum Ansehen bzw. setzen der
IP-Adresse wenn kein DHCP)

---

## Umstellung KUI/AO -> AIS

Umstellung KUI/AO -> AIS
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Das System muss per Schalter vom alten System auf AIS
umgestellt werden. Dieser Schalter befindet sich in der Anwendung „Referenz-ERP
Informationssystem“. Die Funktion „
AIS
aktivieren
“ führt dann eine Umstellung durch. Bei der Umstellung auf AIS
wird versucht, die bestehenden Einrichtungen so zu übernehmen. Dabei gibt es
natürlich die Einschränkung, dass Prozeduren, die auf Maskenfelder zugreifen
jetzt evtl. Probleme bekommen, da die Felder anders benannt werden. Diese
Prozeduren müssen manuell angepasst werden. Nach der Umstellung kann auf dem
aktuellen Arbeitsplatz sofort mit AIS gearbeitet werden, alle anderen Anwender
müssen einmal Referenz-ERP neu starten.
Das alte Addon-System wird sofort für AIS aktiviert,
das KUI-System wird zwar auch übernommen, jedoch noch nicht für AIS aktiviert.
Bei allen Gruppen erscheint auf der Bearbeitungsmaske dann der Text „NOCH NICHT
AKTIV“ neben dem Namen der Gruppe. Zusätzlich steht dann eine Funktion
„
Aktivieren
“ bereit. Erst wenn diese Funktion aufgerufen wird,
wird diese Kuiseite über das AIS-System gesteuert.
Dies hat den Vorteil, dass AIS in Ruhe getestet und
umgestellt werden kann, ohne dass der Arbeitsalltag dadurch gestört wird! Alle
alten Daten von KUI und ADDON bleiben so wie sie sind bestehen und können
jederzeit angesehen werden.
ACHTUNG:
Es ist
NICHT
mehr
möglich wieder auf den alten Modus zurück zu schalten.
Diese Umstellung übernimmt einen Großteil der Arbeit,
jedoch ist es so, dass sich die internen Feldnamen im neuen System von den alten
unterscheiden. Wenn das bisherige Kui/Addonsystem auf ihrem System so aufgebaut
war, dass Feldnamen an Prozeduren / Makros weitergereicht werden, so ist es
wahrscheinlich notwendig diese von Hand anzupassen. Am Ende der Umstellung
erscheint dann eine Meldung, dass das System vollständig umgestellt wurde.
Existieren KUI-Einrichtungen, so wird noch gefragt, ob diese je
[...]


---

## Vba

Vba
Hauptmenü
Administration
Makroverarbeitung
Scripting
Direktsprung
[VBA]
In der Variante „Scripte“ werden die VBA-Scripte von
Referenz-ERP gepflegt.
Scripte deren Namen mit „Branchen-ERP“ anfangen werden
ausgeliefert.
Felder
Name
Script-Identifikation
Thema
Beschreibung
Lokal
Wird
      nicht mehr unterstützt.
Typ
Typisierungsmöglichkeit des
      Scriptes.
geändert
Zeitstempel der letzten
      Änderung
Version
Möglichkeit der
      Versionierung.
Autor
Möglichkeit einen Autor
      anzugeben.
Größe
Größe des Scriptes in
      Bytes.
Suchen
Id
Von
      – bis
Suchen …
Sucht in den Feldern
Name, Thema und dem
      VBA-Script-Text.
Funktionen
Filter /
      bereichsauswahl
F2
Duplizieren
Shift + F10
Bietet die Möglichkeit ein Duplikat
      des Scriptes anzulegen.
Export
Exportiert ein Script
Ändern, Ansehen, Löschen,
      Neu
Standard-Pflege-Operationen
Ausführen
F9
Führt das VBA-Script
      aus.
VBA bedient folgende interne Schnittstelle:
namespace
VisualBasicAeins.Scripting.Interface
{
///
<summary>
///
Aeins-Vba-Schnittstelle
///
</summary>
public
interface
IScriptAeins
{
///
<summary>
///
Param
///
</summary>
///
<param
name="
s
"></param>
///
<returns></returns>
string
Param(
string
s);
///
<summary>
///
Jpp_Create
///
</summary>
///
<param
name="
jpp_class
"></param>
///
<returns></returns>
string
Jpp_Create(
string
jpp_class);
///
<summary>
///
Jpp_New
///
</summary>
///
<param
name="
jpp_hdl
"></param>
///
<param
name="
jpp_class
"></param>
///
<returns></returns>
int
Jpp_New(
string
jpp_hdl,
string
jpp_class);
///
<summary>
///
Jpp_Delete
///
</summary>
///
<param
name="
jpp_hdl
"></param>
///
<returns></returns>
int
Jpp_Delete(
string
jpp_hdl);
///
<summary>
///
Jpp_Ex
///
</summary>
///
<param
name="
jpp_handle
"></param>
///
<param
name="
jpp_method
"></param>
///
<returns></returns>
int
Jpp_Ex(
string
jpp_handle,
string
jpp_method);
///
<summary>
///
Jpp_Do
///
</summary>
///
<param
name="
jpp_handle
"></param>
///
<param
name="
jpp_funct
[...]


---

## Zurücksetzen der TCPIP Scanner Tabellen (inkl. Produktion)

Zurücksetzen der TCPIP Scanner Tabellen (inkl.
Produktion)
Es werden die Daten in folgenden Tabellen
gelöscht:
TCPIP_Scanner
Tcpip_ScannerDaten
Tcpip_Scanner_Positionen
Tcpip_Scanner_Stack
Tcpip_Scanner_Delete
Tcpip_Scanner_Druck
Tcpip_Scanner_Ib_Box
Tcpip_Scanner_markierident
Tcpip_Scanner_maschine
Tcpip_Scanner_produktion
Tcpip_Scanner_protokoll
ProduktionLeerenFuellen
Tcpip_Scanner_Maschine

---

## Zurücksetzen von Regalplätzen auf unbebucht

Zurücksetzen von Regalplätzen auf unbebucht
Mit dem Scannerkommando
BK <nr>
kann ein Kommissionierplatz komplett entleert werden,
um nach Abarbeit der Tagesproduktion die Kommissonierplätze wieder zu
entleeren.
Mit den Kommandos
BR <nr> für buche Regal
BI <nr> für Buche internen Verbrauch
BS <nr> für buche Schwund
BV <nr> für buche Vorplanung
können alle anderen Regalbereiche zurückgesetzt
werden. Bei Nichteingabe von <nr> werden alle Regale des entsprechenden
Typs auf unbebucht gesetzt.

---

