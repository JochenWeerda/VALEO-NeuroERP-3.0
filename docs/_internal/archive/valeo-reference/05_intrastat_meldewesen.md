# Intrastat & Meldewesen — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (143 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Schritt 2 Erweiterung und Anpassung in Referenz-ERP

Schritt 2 Erweiterung und Anpassung in
Referenz-ERP
Schritt 2.1: Prioritäten
Referenz-ERP bietet 3 kombinierbare Wege an, wie die Daten
für die Intrastat Meldung ermittelt werden können :
Die 3 Möglichkeiten werden in folgender Priorität
ausgewertet :
Priorität 1: Intrastat Zusatzdaten und spezieller
Ergänzungsregister Intrastat in den Warenposition
Priorität 2: Explizite Eingaben des EU-Staates und der
Region unter UFLD und in der Warenbewegung
Priorität 3: Automatische Bestimmung aus
Vorgangsdaten
Schritt 2.2: Intrastat Ergänzung bei Warenposition
(Priorität 1)
Um in den Warenpositionen das Zusatzregister
„Intrastat“ angezeigt zu bekommen, muss man zuerst mit dem Direktsprung
[INTRA]
in die Intrastat-Auswahllisten. Dort
dann mit
(F10)
die Funktion
„Intrastat einrichten“
aufrufen. In dieser
Maske muss dann das Feld „Warenbewegung Intrastat“ auf „Ja“ gesetzt werden. Als
letztes mit
(F9)
speichern.
Nach dieser Einstellung wird in den Warenpositionen
das Register „Intrastat“ sichtbar.
Schritt 2.3: Intrastat-Zusatzdaten (Priorität
1)
Um die Intrastat relevanten Daten auch nach dem Fibu
Übertrag noch korrigieren zu können, muss man Direktsprung
[INTRA]
in die Intrastat-Positionen (Variante
1). Hier den gewünschten Datensatz auswählen und diesen mit
(F5)
bearbeiten. Anschließend speichert man
den Datensatz mit
(F9)
ab.
Schritt 2.4: UFLD Felder in der Warenbewegung
(Priorität 2)
Um in der Rechnungserfassung die Felder „Ziel Herkunft
Land“ und „Region“ hinzuzufügen navigiert man mit dem Direktsprung
[UFLD]
in die Benutzerfelder. Hier muss bei
der gewünschte Datensatz für die Rechnung bearbeitet werden
(F5)
. In der Maske Individualfeldgruppen
fügt man nun die Nummern 471 und 470 hinzu und speichert den Datensatz dann mit
(F9) ab.
In einer Rechnungserfassung werden nun die Felder
angezeigt.
Schritt 2.5: Parameter im Rohware Modul(Priorität
3)
Mit dem Direktsprung
[RWPA]
kommt man in die Parametersteuerung
des Rohware Moduls. Danach mit
(F2)
nach
„Herkunft“
suche
[...]


---

## Intrastat Schritt für Schritt

Intrastat Schritt für Schritt
Im Folgenden wird eine Intrastat Meldung Schritt für
Schritt beispielhaft erstellt und die Registrierung bei dem Statistische
Bundesamt erklärt.

---

## Schritt 1 Voraussetzungen

Schritt 1 Voraussetzung
en
Schritt 1.1: Lizenz
Für das Modul Intrastat wird die
Intrastat-Lizenz
benötigt.
Schritt 1.2: Stammdaten
Folgende Stammdaten müssen hinterlegt sein, damit eine
Intrastat-Meldung erstellt werden kann:
-
Kundenstamm
[KU]
Im Register
„Allgemein“
muss
das Land des Kunden hinterlegt sein
Die UST.-Ident muss gepflegt sein
Und
die Steuergruppe darf nicht der Steuergruppe entsprechen, welche im SPA 643
eingetragen ist
-
Lagerstamm
[LGS]
Im Register
„Allgemein“
muss
das Land des Lagerstandortes hinterlegt sein
-
Mandantenstamm
[MND]
Hier muss das Bundesland und
die Steuernummer hinterlegt sein
Schritt 1.3: Artikel mit Intrastat-Nummern
Da jedes meldende Unternehmen eine eigene
Artikelnummerierung aufweist, hat das Statistische Bundesamt eine für die
Intrastat maßgebliche Nummerierung der Artikel bzw. Artikelbereiche vorgenommen.
Das „Warenverzeichnis für die Außenhandelsstatistik“ enthält die Warennummern,
die im Artikelstamm zu hinterlegen sind.
Für diese Einrichtung geht man mit dem Direktsprung
[ARS]
in den
Artikelstamm
. Danach den Artikel auswählen und
bearbeiten
(F5)
. Im Pfleger dann
unter dem Reiter „Konstanten“ die Zollwarennummer des Artikels eintragen. Die
Zollwarennummer gleicht der Intrastat-Nummer.
Nachzulesen sind die Nummern unter:
https://www.zolltarifnummern.de
Schritt 1.4: Intrastat einrichten:
Um die Intrastat-Meldung einzurichten navigiert man
mit dem Direktsprung
[INTRA]
in die
Intrastat-Auswahllisten. Hier ruft man mit
(F10)
die Funktion „Intrastat einrichten“
auf.
Wichtig:
seit
Februar 2020 wird ein neues Format (XML) für die Intrastat-Meldung verlangt. Das
Alte Dateiformat (ASCII) wird nur noch bis zum 30.06.2021 akzeptiert. Alle neu
angemeldeten Benutzer nach dem 31.01.2020 sind verpflichtet das XML-Format zu
nutzen.
Quellen:
-
https://www-idev.destatis.de/idev/doc/intra/hilfe6_1.html
(ASCII)
-
https://www-idev.destatis.de/idev/doc/intra/hilfe6_2.html
(XML)
ASC-Format:
Der ASCII Export wird nur noch bis
[...]


---

## Schritt 3 Meldung erstellen (Beispiel Versand)

Schritt 3 Meldung erstellen
(Beispiel
Versand)
Schritt 3.1: Beispiel Versand
Für die Erstellung einer Intrastat-Meldung müssen
folgende Voraussetzungen erfüllt sein:
-
Rechnung mit einem
EU Kunden
wurde erstellt
[REE]
-
Die Rechnung mit dem
EU Kunden
wurde in die FiBu übertragen
[REB]
Schritt 3.2: Datei Export
Mit dem Direktsprung
[INTRA]
navigiert man
Intrastat-Meldung Versendung
(2. Variante)
oder
Intrastat-Meldung
Einfuhr
(3. Variante). Hier ruft man nun die Funktion
„Versand erzeugen / Einfuhr erzeugen“
(F9)
auf. Nach der Bestätigung des
Exports öffnet sich der Explorer.
(Für die Registrierung wird die Datei mit dem
Dateinamen „XGTEST
-Datum-Uhrzeit
“ abgespeichert Normale Exporte werden
mit
Materialnummer-Datum-Uhrzeit
abgespeichert)
Schritt 3.3: Steuergruppen ausschließen
Mit dem Direktsprung
[STS]
in den Steuerdatenpfleger. Dort mit der
Funktion
Steuergruppen
(F6)
in die Auswahlliste der Steuergruppen.
Hier die Steuergruppe auswählen, welche bei dem Export nicht berücksichtigt
werden soll und diese
Bearbeiten
(F5)
. Nun das Feld
„Intrastat“
auf
„Nein“
setzten und den Datensatz
Speichern
(F9)
.

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

## Bitmapmeldung unterdrücken

Bitmapmeldung unterdrücken
In Formularwesen [FRM] kann man nun unter Details auf
einem Feld mit der Druckposition 22 (Bitmap aus Archiv/Datei) ein Häckchen
setzen. Dieses Häckchen heißt "Bitmapmeldung unterdrücken" und bietet die
Möglichkeit statt des roten Schriftzuges bei Problemen mit der Datei oder dem
Archiv gar keine Meldung zu geben und stattdessen das Feld leer zu lassen. Die
Fehlermeldung im Fehlerprotokoll wird dennoch gegeben, um auf einen Fehler
hinzuweisen.
Releasenote Kategorie:
Ticket: 714562[32967]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: Formularwesen [FRM]
Variante: Formularwesen
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2211.9, 32967, 714562

---

## DATEV Übertrag erstellen. Verbesserte Fehlermeldung.

DATEV Übertrag erstellen. Verbesserte Fehlermeldung.
Beim Erstellen eines DATEV-Übertrages werden die
Kontonummern auf die korrekte Länge getestet. Wird ein DATEV-Ersatzkonto
verwendet, bei dem die Kontonummer nicht der geforderten Länge entspricht, wird
jetzt zusätzlich das Originalkonto im Fehlerhinweis ausgegeben.
Releasenote Kategorie:
Ticket: 716776[33209]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: DATEV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33209, 716776

---

## Kassensystem: Tse-Meldung bei Kasseneröffnung

Kassensystem: Tse-Meldung bei Kasseneröffnung
Bei der Kasseneröffnung kam es zur Tse-Fehlermeldung
4180. Dies wurde nun behoben.
Releasenote Kategorie:
Ticket: 719423[33410]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: BVVE
Variante: Marktkasse
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33410, 719423

---

## Zollwarennummern einspielen

Zollwarennummern einspielen
Unter Umständen konnten Zollwarennummern nicht mehr
eingespielt werden. Dies ist nun behoben.
Releasenote Kategorie:
Ticket: 719735[33459]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Zollwarennummer
Variante: Zollwarennummer
Funktion/Report: Zollwarennummern einspielen
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33459, 719735

---

## Dokumentenverwaltung: Gelegentliche Komplikationen im Archiv-Betrieb

Dokumentenverwaltung: Gelegentliche Komplikationen  im
Archiv-Betrieb
Die interne Verwaltung von
Archiv-Darstellungskomponenten wurde verbessert. Das gelegentlich aufgetretene
Problem mit der Meldung "Retriever.Worker" wurde behoben.
Releasenote Kategorie:
Ticket: 720072[33465]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: Archiv anzeigen
Variante: -
Funktion/Report: Archiv anzeigen
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33465, 720072

---

## Elster: Kennzeichen 87 und 90

Elster: Kennzeichen 87 und 90
UVA: Die neuen Kennzeichen 87 und 90 werden nur für
die Jahre ab 2023 übertragen.
Releasenote Kategorie:
Ticket: 721151[33595]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Umsatzsteuer Voranmeldung
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33595, 721151

---

## Intrastat: Werte und Mengen

Intrastat: Werte und Mengen
Bei der Intrastatmeldung konnte es zu falschen Mengen
und Werten kommen, wenn eine Lagerplatzumbuchung beteilig war. Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 722036[33645]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33645, 722036

---

## Kassensystem: TSE Fehler 4180

Kassensystem: TSE Fehler 4180
Während der Kasseneröffnung kam es zur Fehlermeldung
4180 der TSE. Dieses wurde nun behoben.
Releasenote Kategorie:
Ticket: 723247[33845]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: BVVE
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33845, 723247

---

## Ursprungsland in Intrastat Varianten

Ursprungsland in Intrastat Varianten
Die Varianten in der Anwendung Intrastat [INTRA]
wurden um das Ursprungsland erweitert.
Releasenote Kategorie:
Ticket: 723766[33914]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Intrastat
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33914, 723766

---

## Datev Export verbesserte Fehlermeldung

Datev Export verbesserte Fehlermeldung
Erstellt man einen Datev-Export, so werden auch Belege
mit 0,00 Umsatz mit aufgesammelt. Belege mit Umsatz 0,00 werden jedoch nicht mit
in die Datei übernommen. Sind nur Belege mit Umsatz 0,00 aufgesammelt worden
kommt jetzt die Meldung "Der Export enthält keine Belege. Es wurden keine
Bewegungsdaten exportiert."
Releasenote Kategorie:
Ticket: 724270[33911]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: DATEV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33911, 724270

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

## Systemmeldungen modernisiert

Systemmeldungen modernisiert
Mit der Anwendung Menü [MENU] ist es möglich
Systemmeldungen im Hauptmenü auszugeben. Darüber hinaus wurde die Möglichkeit
geschaffen, diese Meldungen auch als Popup unten rechts am Bildschirm
auszugeben. Hierzu muss man bei der Einrichtung im Feld Desktop "Ja" auswählen.
Dies hat den Vorteil, dass diese Meldungen sichtbar sind, ohne dass man sich im
Hauptmenü befindet. Unter gewissen Konstellation konnte es vorkommen, dass die
Meldungen ohne ersichtlichen Grund aufpoppten. Das Verhalten wurde
korrigiert.
Releasenote Kategorie:
Ticket: 726067[34136]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Menü [MENU]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34136, 726067

---

## Irritierende Fehlermeldung entfernt

Irritierende Fehlermeldung entfernt
In der Inventuraufnahme [IVA] wurde eine irritierende
Fehlermeldung ausgegeben, wenn der ausgewählte Artikel nicht die richtige
Inventurgruppe hatte. Stattdessen kommt nun eine Warnung, dass der ausgewählte
Artikel nicht zur Inventurgruppe passt.
Releasenote Kategorie:
Ticket: 730470[34735]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Inventuraufnahme [IVA]
Variante: Inventuraufnahme
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 34735, 730470

---

## MDE: Fokus auf Eingabefeld

MDE: Fokus auf Eingabefeld
Es ist nun möglich Rückmeldungen von Referenz-ERP so zu
gestalten, dass der Fokus direkt in dem Eingabefeld steht.
Releasenote Kategorie:
Ticket: 0[35008]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: MDE Scanner
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 35008, 0

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

## ZHB - Zahlungen ansehen - Excel Export

ZHB - Zahlungen ansehen - Excel Export
Unter ZHB kann man mit F6 die einzelnen Positionen der
Zahlung ansehen. Hier lieferte der Excel Export einen Fehler.Die Funktion
"Senden an", die in der alten Auswahlliste nur noch eine Meldung ausgab, dass
sie nur in der neuen Auswahlliste funktioniert wird jetzt nicht mehr
eingeblendet.
Releasenote Kategorie:
Ticket: 733495[36002]
Version: 9.0.2501.5
Datum:
Anwendung: ZHB
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36002, 733495

---

## Intrastat Art des Geschäftes vor 2022 und nach 2022 korrekte Werte

Intrastat Art des Geschäftes vor 2022 und nach 2022 korrekte Werte
Die Intrastat-Auswahllisten können jetzt auch Belege
aus den Jahren vor 2022 und nach 2022 mit den korrekten Art des Geschäfts Texten
darstellen.  Ursache war, dass sich die Codierung "Art des Geschäftes" von
2022 auf 2023 geändert hat. Der gleiche Code hat nun in Abhängigkeit des
Belegjahres eine unterschiedliche Bedeutung.
Releasenote Kategorie:
Ticket: 744027[36380]
Version: 9.0.2501.5
Datum:
Anwendung: Intastat
Variante: Intrastat-Positionen, Intrastat-Meldung
(Versendung), Intrastat-Meldung(Einfuhr)
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36380, 744027

---

## IBMSK nicht existierendes Feld

IBMSK nicht existierendes Feld
Es werden keine Fehlermeldungen mehr angezeigt, wenn
das in IBMSK angesprochene Feld nicht existiert.
Releasenote Kategorie:
Ticket: 745034[36522]
Version: 9.0.2501.5
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36522, 745034

---

## Auswahlliste 2.0 Filterzeile

Auswahlliste 2.0 Filterzeile
Wenn man über die Filterzeile eine Eingrenzung
vornimmt und ohne die Filterzeile zu verlassen, in die Bearbeitung springt,
erscheint nach der Bearbeitung eine Fehlermeldung.
Releasenote Kategorie:
Ticket: 747767[37321]
Version: 9.0.2501.6
Datum:
Anwendung: --
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.6, 37321, 747767

---

## Archivansicht

Archivansicht
Bei privaten Auswahllisten mir Archiv-Ansicht kam eine
Fehlermeldung wenn hinter einem Eintrag kein Archivdokument hinterlegt war,
beispielsweise bei einem noch nicht gedruckten Vorgang.  Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 750223[38208]
Version: 9.0.2502.6
Datum:
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.6, 38208, 750223

---

## Statusmeldung in OSQL

Statusmeldung in OSQL
Unter [OSQL] werden die Anzahl der verarbeiteten Daten
wieder in der Statuszeile angezeigt,
Releasenote Kategorie:
Ticket: 751529[38591]
Version: 9.0.2502.9
Datum:
Anwendung: OSQL
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38591, 751529

---

## Intrastat: Ursprungsland

Intrastat: Ursprungsland
Das Ursprungsland kann nun weltweit gewählt werden
(entweder nach Nummer oder nach Bezeichnung).Der Filter kann aber auch auf das
vorherige Verhalten mit Inland oder EU begrenzt werden.
Releasenote Kategorie:
Ticket: 752572[39170]
Version: 9.0.2502.9
Datum:
Anwendung: Intrastat
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2502.9, 39170, 752572

---

## Hotline (EPA WUNSCHLI)

Hotline (EPA WUNSCHLI)
Bezeichnung
Standardwert
Erklärung
Passwort
Postfach
Warnung erzeugen aufgrund
      Rückmeldung
KEINE WARTUNG!
Testspalte für Warnung
Wartung
Testtabelle für Warnung
KundenAddon

---

## Zollausfuhr (EPA ZOLLABWICKLUNG)

Zollausfuhr (EPA ZOLLABWICKLUNG)
Bezeichnung
Standardwert
Erklärung
alternative Ladeort
      Vorbelegungs-Prozedur

---

## Intrastat

Intrastat

---

## LVS-Meldungen unterdrücken (SPA 1060)

LVS-Meldungen unterdrücken (SPA 1060)
LVS 2.0 verwendet einige Funktionen, die zu gehäuften
Warnungsmeldungen im Fehlerprotokoll führen können. Um diese zu unterdrücken
kann dieser Steuerparameter verwendet werden.

---

## Intrastat-Lizenz (SPA1094)

Intras
tat-Lizenz (SPA1094)
Lizenz für Intrastat.

---

## Vorgangsimport vor Import prüfen (SPA 1131)

Vorgangsimport vor Import prü
fen (SPA 1131)
Ist der Steuerparameter deaktiviert, so werden nur
jene Positionen importiert, die gültig sind. Fehlerhafte Zeilen werden auf
fehlerhaft gesetzt und nicht importiert. Meldungen finden sich im
Fehlerprotokoll. Es kann so zu unvollständigen Belegen kommen.
Ist der Steuerparameter aktiviert und der
Import-Parameter useCS=1, wird der Import nicht durchgeführt, wenn dieser bei
der Plausibilitätsprüfung Fehler enthält. Auf diese Weise können keine
teilweisen Importe eines Beleges erfolgen.

---

## Warenbewegungen im Kontenblatt-Druck(SPA 173)

Warenbewegungen im Kontenblatt-Druck(SPA 173)

---

## Warenbewegung vor sonstigen im Kontenblatt(SPA 192)

Warenbewegung vor sonstigen im Kontenblatt(SPA 192)

---

## Variante Sollpreis-Speicherung(SPA 311)

Variante Sollpreis-Speicherung(SPA 311)
Ohne: es wird kein Preis in WaBewSollPreis abgelegt.
Listenpreis: In der Warenbewegung wird ein gefundener
Listenpreis in WaBewSollPreis abgelegt; der Preis selbst kann ja manuell
geändert werden.
Preis zzgl. aut. Zu-/Abschläge: In der Warenbewegung
wird in WaBewSollPreis der gefundene Preis zuzüglich der automatischen Rabatte
und Zu-/Abschläge abgespeichert.
Listenpreis zzgl. aut. Zu/Abschläge: In der
Warenbewegung wird in WaBewSollPreis der gefundene Listenpreis zuzüglich der
automatischen Rabatte und Zu-/Abschläge abgespeichert (wird beim Abschluss des
Vorgangs ermittelt für alle Warenbewegungen)

---

## Fiktive Menge bei Frachtermittlung(SPA 530)

Fiktive Menge bei Frachtermittlung(SPA 530)
In der Warenbewegung kann eine fiktive Menge (für
Mengenbezüge) hinterlegt werden. Die fiktive Menge wird anstelle der
eigentlichen Menge zur Ermittlung von Zu-/Abschlägen und Rabatten herangezogen.
Ist die Einstellung „Ja“, so wird die fiktive Menge
auch bei der Frachtermittlung berücksichtigt!

---

## Meldung bei Steuerzuordnungsproblem(SPA 680)

Meldung bei Steuerzuordnungsproblem(SPA 680)
Wenn ein Steuersatz nicht korrekt ermittelt werden
kann oder durch einen ErsatzSteuerschlüssel(0) gefunden wird, erfolgt bei „Ja“
einmal pro Sitzung eine Meldung auf dem Bildschirm. Bei „Nein“ wird diese
Meldung nur im Ereignisprotokoll hinterlegt.

---

## Ordersatz: WarenbewegungAddon übernehmen(SPA 686)

Ordersatz: WarenbewegungAddon übernehmen(SPA
686)
Bei „Ja“ werden alle Addon-Daten der Quellposition
übernommen.

---

## Nur Fehlerbeep. (SPA 743)

Nur Fehlerbeep. (SPA 743)
Nur bei einem Fehler ertönt eine negative Meldung.

---

## Gültigkeitsdatum des Artikels in der Produktion berücksichtigen (SPA 792)

Gültigkeitsdatum des Artikels in der Produktion berücksichtigen (SPA
792)
Ist das Gültigkeitsdatum eines Artikels noch nicht
erreicht oder überschritten, so wird bei der Verwendung dieses Artikels eine
Fehlermeldung ausgegeben, wenn dieser Artikel verwendet wird.

---

## Zolldatenerfassung-Lizenz (SPA 833)

Zolldatenerfassung-Lizenz (SPA 833)
Lizenz für die Zolldatenerfassung. Dazu zählen u.a.
die
Zollwarennummern
und
Zollstellen
.

---

## Timeout GeoDatenDienst in Sek (SPA 878)

Timeout GeoDatenDienst in Sek (SPA 878)
An dieser Stelle geben Sie einen Wert in Sekunden an
(Im Bereich zwischen 0 und 99 Sekunden), der als Timeout für eine Webabfrage
einer geografischen Koordinate gilt. Bitte beachten Sie, dass dieser Wert nicht
zu klein sein darf, da die Rückmeldung des GeoDatendienstes je nach
Geschwindigkeit und Belastung der Datenverbindungen einige Sekunden dauern kann.

---

## Systemmeldungen dynamisch(SPA 893)

Systemmeldungen dynamisch(
SPA 893
)
Komplexer Steuerparameter.
Steuert die dynamische Wiederholung der
Systemmeldungsprüfung.
Der Schlüssel wird aus dem Format „SYSMSGdyn“
geholt.
Aktiv
Schlüssel / Parameter
Option / Zeitangaben
JA / NEIN
Entscheidet ob der folgende
      Schlüssel ausgewertet werden soll oder nicht.
AnAus
Entscheidet, ob die fortwährende
      dynamische Prüfung der Systemmeldungen überhaupt stattfinden
      soll.
Entscheidungskriterium ist hier der
      Wert unter „
Aktiv
“.
.
JA / NEIN
Entscheidet ob der folgende
      Schlüssel ausgewertet werden soll oder nicht.
Wartezeit
Diese Zeit wird zwischen den
      Prüfungen der Systemmeldungen gewartet
Wert
      in Sekunden angeben.
Voreinstellung sind 60
      Sekunden.
JA / NEIN
Entscheidet ob der folgende
      Schlüssel ausgewertet werden soll oder nicht.
Verfallszeit
Nach
      Ablauf dieser Zeitdauer verfällt eine auf vormals gut erkannte
      Systemmeldung und wird erneut geprüft
Wert
      in Sekunden angeben.
Voreinstellung sind 180
      Sekunden.

---

## IBAN Test nach Standard-Prüfziffernverfahren (SPA 897)

IBAN Test nach Standard-Prüfziffernverfahren (SPA
897)
Bei eingetragenen IBAN’s wird die Prüfziffer ermittelt
und mit der in der IBAN enthaltenen verglichen und dann ggf. eine Warnmeldung
ausgegeben. Da hier nur das Standardverfahren angewendet wird und es Banken
gibt, die ein eigenes Verfahren verwenden, wird immer trotz Meldung gespeichert.
Man kann das Prüfverfahren hier komplett abstellen.

---

## ZMDO mehrere Kunden mit gleicher USTID akzeptieren (SPA 934)

ZMDO mehrere Kunden mit gleicher USTID akzeptieren
(SPA 934)
Für die Zusammenfassende Meldung (Direktsprung
[UVZM]
) werden die Daten zuerst in einer
Auswahlliste –Variante „Zusammenfassende Meldung nach AWPosition“  -
zusammengestellt und diese Informationen von dort an die entsprechenden
Übertragungs- bzw. Informationsbereiche weitergeleitet. Die Auswahlliste
generiert pro Konto die Daten. Dies ist die Standardeinstellung dieses
Steuerungsparameters:
Nein
. Wenn zu unterschiedlichen Konten dieselbe
UDTID hinterlegt ist – weil es sich z.B. um verschiedene Filialen handelt –
kommt es bei der Übertragung zu Problemen, da dieselbe USTID nicht mehrfach ( es
sei denn mit anderen Kennzeichen für Dreiecksgeschäft / Sonstige Leistung)
vorkommen darf. Stellt man den Steuerungsparameter auf
Ja
, so
werden die Daten nach der USTID gruppiert. Die Konten werden dann nur noch
Informatorisch angezeigt.

---

## openTRANS Position mit GUID (SPA 945)

openTRANS Position mit GUID (SPA 945)
Im openTRANS-Export wird die Position mit einer
laufenden Nummer aus dem Vorgang in der LINEID bezeichnet. Um eine Eindeutigkeit
zu erreichen, kann jedoch die GUID der Warenbewegung hier exportiert werden.
Dazu muss der SPA auf „JA“ gestellt werden.

---

## Bei Gutscheinannahme Nummer verproben? (SPA 992)

Bei Gutscheinannahme Nummer verproben? (SPA 992)
Hier wird festgelegt wie die Verprobung der
Gutscheinnummer geschehen soll.
Wert
Bedeutung
0
Keine Verprobung
      (Standard)
1
Warnmeldung bei bereits eingelöstem
      Gutschein
2
Die
      Gutscheinnummer wird abgelehnt bei bereits eingelöstem
      Gutschein

---

## Anmeldung zur Feldbesichtigung

Anmeldung zur Feldbesichtigung

---

## Registerkarte Konstanten

Registerkarte Konstanten
Feld
Bedeutung
Zollwarennummer
8-stellige
Zollwarennummer
für die Ausfuhranmeldung
      und für das Modul
Intrastat
.
Erw.Einfuhr
Die
      Zollwarennummer für die Einfuhranmeldung besteht aus der
Zollwarennummer
zuzüglich
      dieser drei Stellen.
Packstückart
DSD-Gruppe Material
Für
      die DSD-Abwicklung können hier die notwendigen Informationen über
      Materialgruppe und Volumengruppe hinterlegt werden.
DSD-Gruppe Volumen
Für
      die DSD-Abwicklung können hier Angaben zur Volumengruppe gemacht
      werden.
Hedge-Location
Verkaufsbeschränkungen
Hier
      können Verkaufsbeschränkungen wie z.B. Altersgrenzen oder
      Sachkundenachweise ausgewählt werden, die beim Handel in Abhängigkeit der
      Vorgangsunterklasse abgefragt werden können.
Diese Einstellung ist nur sichtbar,
      wenn Steuerparameter
900 –
      Verkaufsbeschränkung
eingeschaltet ist.
Zusätzlich zu den von Branchen-ERP
      vorgegebenen Möglichkeiten können weitere Auswahlkriterien in das
      Anwender-Format „AF_SaleRestr“ eingefügt werden. Bitte beachten Sie, dass
      die ersten 10 Werte für Branchen-ERP reserviert sind.
Verkaufsbeschränkungszertifikatstyp
Hier
      kann ein Zertifikatstyp angegeben werden. Wenn der
Kunde
ein gültiges
Zertifikat
dieses
      Zertifikatstyps besitzt, erfolgt keine Abfrage der „Verkaufsbeschränkung“
      beim Erfassen von Vorgängen.

---

## Einrichten der Auslandskunden für Zollausfuhr

Einrichten der Auslandskunden für Zollausfuhr
Die Zollabwicklung macht nur Sinn, wenn ein Export
nach Außerhalb der EU vorliegt. Deshalb wird die Funktion auch nicht für
Lieferungen innerhalb der EU angeboten.
Bei Kunden, deren Staatbezeichnung außerhalb der EU
liegt, also im Staatstamm die Bedeutung „Drittland“ hat, müssen zusätzliche
Zolldaten für die Zollabwicklung hinterlegt werden.
Diese Daten lassen sich im Anschriftstamm-Eintrag mit
der
Funktion „ZOLLDATEN“
zu dem einzelnen
Kunden erfassen.
Diese Angaben werden, sofern sie eingegeben wurden,
als Vorgabe in die Ausfuhrzollanmeldung übernommen und können so die wiederholte
Eingabe der Texte ersetzen.

---

## Auswertungen zur Partie

Auswertungen zur Partie
Für alle Partieauswertungen ist es grundsätzlich
nötig, dass alle Warenbewegungen im Warenbuch eingetragen sind. Diese Funktion
übernimmt der Mandantenserver
[MS]
.

---

## Einrichtung der Zollausfuhr

Einrichtung der Zollausfuhr
Für den Betrieb der Zollausfuhranmeldung sind folgende
Einrichtungen notwendig:
•
Ein Event zur automatischen Prüfung und Abholung von Ausfuhren muss
eingerichtet werden. Werden dabei auch Mails versandt, so muss auch im
Versandprofilstamm (ehem. Verpostungsstamm) ein Eintrag erstellt werden.
•
Für die Nutzung der Zollausfuhr muss eine Liste der
Zollstellen
heruntergeladen und in
das Referenz-ERP-System eingespielt werden. Diese Liste wird von der europäischen
Union veröffentlicht.
Eine Änderung der Liste kann
unter Umständen monatlich erfolgen!
•
Die Liste der Zollwarennummern muss aktuell gehalten werden.
Jährlich gibt das
Bundesamt
für Statistik in Wiesbaden
ein „Warenverzeichnis für die
Außenhandelsstatistik“ heraus. Dies muss in Form einer sog. LG520-Liste oder
SOVA in Aeins eingespielt werden. Stellen Sie sicher, dass diese Liste
Jahres-aktuell ist.
Für die manuelle Eingabe
einzelner Zollwarennummern steht Ihnen ein Pfleger in der
Anwendung
Zollwarennummer [ZWN]
zur Verfügung
•
Im Lagerstamm kann für jedes Lager eine zuständige Ausfuhrzollstelle
eingerichtet werden. Diese wird dann als Vorbelegung bei der Ausfuhr verwendet.
Welche Zollstelle zuständig ist, erfragen Sie ggf. beim Zoll oder unter
www.zoll.de
. Näheres zur
Einrichtung in der Hilfe zum Lagerstamm.
•
Die Anschrift der Zollanmelders (in der Regel die gleiche wie die des
Mandanten) muss festgelegt werden. Dies können Sie im
Mandantenstamm
einrichten.

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

## Export-Pfad

Export-Pfad
Gibt den Pfad im Dateisystem an, wohin die
exportierten Belege exportiert werden sollen.
Der angegebene Export-Pfad muss leer sein, damit man
sicher sein kann, dass man einen „sauberen“ Stand hat. Ist der Pfad nicht leer,
dann bekommt man die Meldung
Räumen Sie dann z.B. per Windows-Explorer auf, oder
wählen Sie einen anderen Export-Pfad.
Ist der Pfad soweit in Ordnung (existiert, ist leer
und ist beschreibbar), dann erscheint folgende Abfrage

---

## Fehlermeldungen

Fehlermeldungen
Verschiedene Arten der Fehlermeldung können erfolgen.
So reagiert das System z.B. bei der Eingabe von Buchstaben in ein Feld, das
eindeutig numerisch ist (z.B. das Mengeneingabefeld), mit einem
Piepton
und verlangt eine korrekte Eingabe.
Bei Eingabe eines technisch korrekten,
jedoch inhaltlich falschen Wertes (z.B. eine nicht vorhandene Steuergruppe),
werden automatisch die zulässigen Alternativen angezeigt:

---

## Importieren von Zollausfuhrlisten

Importieren von Zollausfuhrlisten
Mit diesem Einspieler werden die Zollausfuhrlisten in
das Referenz-ERP System eingespielt. Dazu werden die Zollausfuhr unter dem Link „Atlas
Ausfuhr Codeliste“ von der
Atlas
Webseite heruntergeladen. Die Dateien müssen auf dem Computer gespeichert
werden, um diese in das Referenz-ERP System ein zuspielen. Nach dem die Dateien
heruntergeladen worden sind, können diese per Funktion „Einspielen“ in das
System importiert werden. Sind alle Dateien erfolgreich eingespielt, so bekomme
diese die Endung „_imported“. Hat das Einspielen der Dateien nicht funktioniert
so, bekommen diese die Endung „_error“.
Maskenfeld
Bedeutung
Import Verzeichnis
In
      diesem Feld wird das Verzeichnis hinterlegt, in dem sich die
      Zollausfuhrlisten befinden. Der Pfad muss relative zum Datenbank Server
      liegen.
Import Funktion
In
      diesem Feld wird die Datenbankprozedur hinterlegt, welche die
      Zollausfuhrlisten in die Datenbank einspielt. Diese Prozedur kann
      privatisiert werden.
Statustext
Zeigt den Status nach dem Export an.
      Tritt die Meldung
„Fehler beim Einspielen der Daten“
      auf so steht im Fehlerprotokoll nähere Informationen zu der
      Meldung
In der Tabelle werden alle eingespielten
Zollausfuhrlisten angezeigt.
Maskenfeld
Bedeutung
ID
Ident der
      Zollausfuhrliste
Name
Name
      der Zollausfuhrliste
Gültig ab
Ab
      welchem Zeitpunkt ist die Datei gültig
System
EX
Version
Versionsnummer der
      Datei.
Folgende Dateien können zurzeit eingespielt
werden:
1.
A0027
2.
A0108
3.
A0122
4.
A0127
5.
A1150
6.
A1270
7.
A1840
8.
C0017
9.
C0018
10.
Coo31
11.
C0092
12.
C0093
13.
I0100

---

## Intrastat-Positionen

Intrastat-Positionen
Hauptmenü
Warenverkauf
Intrastat
Intrastat-Meldung
Variante 1: Intrastat-Positionen
oder Direktsprung
[INTRA]
Felder der Intrastat Positionen
Felder
Beschreibung
Versendung/Einfuhr
Kennzeichen ob Versendung oder
      Einfuhr
1: Versendung
2: Einfuhr
|
      X
|
=
|
      X   |
= Beleg
      ist in der Fibu aber nicht im Interstat
Periode
Siehe
      auch:
Perioden
Jahr
Siehe
      auch:
Jahr
Melden
Meldekennzeichen
1: Ja
9:
      Nein
|
      X   |
=
      Meldung wurde per Pfleger auf Nein gesetzt
Addon
Gibt
      an, ob zugehörige Intrastat Zusatz-Daten vorhanden sind
|
      X   |
=
      Lagerumbuchungsproblem oder die Mandanten-Staatsnummer +
      Kunden-Staatsnummer + Lager-Staatsnummer stimmen überein
UStid Mandant
Umsatzsteuerid des zugehörigen
      Mandanten
Die
      im Vorgang hinterlegte UStid. Ist diese nicht angegeben, wird die
      Default-UStid des Mandantstammes herangezogen.
Siehe auch:
Finanzbuchhaltung Ust-IdNr.
Mnd-Staatnr.
Staatnummer des zugehörigen
      Mandanten
|
      X   |
= Es
      konnte keine UStid ermittelt werden und ist die Meldung auch nicht über
      das Addon verneint. Resultierender Staat existiert nicht, oder UStdid
      falsch
|
      X   |
= Die
      Mandanten-Staatsnummer + Kunden-Staatsnummer + Lager-Staatsnummer stimmen
      überein
|
      X   |
=
      Zollgruppenzuordnung ist nicht Inland bzw. EU-Mitglied
Mnd-Staat
Staat des zugehörigen
      Mandanten
Der
      Iso-Code aus dem Staatstamm.
Siehe auch:
Staatstamm
Mnd-Zollgruppe
Zollgruppe aus dem
      Staatstamm
(Inland, EU-Mitglied)
UStid Kunde
Umsatzsteuerid des
      Kunden
Im
      Normal-Fall die im Vorgang hinterlegte UStid.
Ist
      diese nicht angegeben wird die Default-UStid des Kundenstammes
      herangezogen.
Knd-Staatnr.
Staatnummer des Kunden
|
      X   |
=
      Resultierender Staat existiert nicht, oder UStdid falsch
|
      X   |
= Die
      Mandanten-Staatsnummer +
[...]


---

## Intrastat Auswahllisten

Intrastat Auswahllisten
Für das Modul Intrastat existieren mehrere Varianten.
Generell werden alle Warenbewegungen folgender Vorgänge, zwischen den
EU-Ländern, hier aufgelistet:
-
Rechnung u. Storno
-
Gutschrift und Storno
-
Eingangsrechnung u. Storno
-
Eingangsgutschrift und Storno
-
Lagerumbuchung
-
Artikelumbuchung
-
Produktion Stückliste

---

## Intrastat Zusatzdaten

Intrastat Zusatzdaten
Felder
Mandant
Nur
      Anzeige: Umsatzsteuerid, Länderkennzeichen,
      Zollgruppenzuordnung
Beteiligter Staat
Nur
      Anzeige:
Kunde
Nur
      Anzeige: Umsatzsteuerid, Länderkennzeichen, Zollgruppenzuordnung,
      Kundennummer, Bezeichnung des Kunden
Lager
Nur
      Anzeige: Länderkennzeichen, Zollgruppenzuordnung, Lagernummer, Bezeichnung
      des Lagers
Artikel
Nur
      Anzeige: Artikelnummer, Artikel-Intrastatnummer, Eigenmasse
Meldung
Versendung/Einfuhr
Staat
Region
Art
      des Geschäftes
Art des
      Geschäfts
Besondere Masseinheit
Rechnungswert
Statistischer Wert
abweichendes Jahr
abweichende Periode

---

## Leermeldung

Leermeldung
Mit der Funktion
Leermeldung
wird ein Silo leergemeldet.
Die Leermeldung wird über die Waage abgebildet, d.h. es wird erst automatisch
ein Waagenbeleg erzeugt mit der Differenzmenge zu 0. Nach dem der Waagenbeleg
erzeugt worden ist, wird das Silo leergemeldet. Der Waagenbeleg bekommt dann den
Status abgeschlossen.
Soll eine Silobewegung in ein Leergemeldeten Silosatz
nachgebucht werden, so wird auch eine neue Leermeldung für diesen Silosatz
erzeugt. Der aktuelle Silo bestand wird dadurch nicht verändert.
Soll bei der Leermeldung die Differenzmenge auf ein
Schwundsilo gebucht werden, so wird für das Schwundsilo ebenfalls ein
Waagenbeleg erzeugt. Dieser bebucht das Silo. Der Status des Waagensatzes steht
dann auch auf abgeschlossen.
Damit eine Leermeldung durchgeführt werden kann,
müssen für jedes Lager die Leermeldungs Waagenprozesse eingerichtet sein.
Des Weiteren muss für jedes
Lager
ein Lagerkunde zugewiesen sein. Dieser Kunde
wird für den Waagenbeleg benötigt.
Leermeldungen können sich dann in der Variante
„Silobuch“ mit der Aktivität „Bestandsmeldung Leermeldung“ gefiltert werden.
Meldungen und deren Bedeutung
Meldung
Bedeutung
Es
      konnte kein Artikel auf dem Silo … an der Position … gefunden
      werden.
Dies
      bedeutet, dass das Silo schon leergemeldet worden ist, oder das die
      Ausgewählte Position in der Silobestands Maske leer ist.
Leermeldung kann nicht durchgeführt
      werden. Sa es kein Prozess gibt um eine Waagenbuchung durchzuführen,
      welche die Menge im Silo auf 0 bringt.
Dies
      bedeutet, dass die
Waagenprozesse
für die Leermeldung nicht
      richtig eingerichtet worden sind.
Folgende Prozesse müssen für jedes
      Lager eingerichtet sein
1.   Leermeldung
      Abgang
2.   Leermeldung
      Zugang
Es
      wurde das Schwundsilo … im Prozess … angegeben, Es konnte kein Prozess mit
      dem Prozesstyp Leermeldung Schwundsilobuchung für die Schwundbuchung
      gefunden werden. Leermeldung
[...]


---

## LVS 2.0

LVS 2.0
Das LVS 2.0 ist ein reines Online-Scanner-LVS. Die
„Intelligenz“ dieses Systems steckt ausschließlich in den Scanner-Prozeduren und
dem Workflow. Die Scanner-Applikation wird ausschließlich zur Eingabe eines
Barcodes und der Ausgabe der Rückmeldung genutzt.

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

## SQLK Nachweisvorlage

SQLK Nachweisvorlage
Diese Methode liefert einen einzeiligen Resultset zur
Warenbewegung:
Feld
Beschreibung
Label
'aus
      nachhaltigem Anbau.‘
Text1
'Zertifizierungssystem für
      Nachhaltigkeit:‘ + Text lt. af_zertmeth
Text2
'REDcert, Zertifikatsnummer: ' +
      eingerichteter Bemerkungstext
Text3
'Die
      Ware entspricht den Nachhaltigkeitsverordnungen (BioSt-NachV u.
      Biokraft-NachV)! '
Text4
'Für
      die Berechnung der Treibhausgasbilanzierung soll der Standardwert
      verwendet werden‘
Text5
'(§
      8 u. Anlage 2 der Nachhaltigkeitsverordnungen). '
Zertifizierung
Text
      lt. af_zertmeth
Zertifikatsbemerkung
Eingerichteter
      Bemerkungstext
Zertifikat_BLE
Normierte Zertifikatsausgabe gemäß
      BLE:
DE-B-BLE-BM-10-100-20100009-00000001
Stehend für
      Deutschland-Bund-BLE-Biomasse-
Zertifizierungssystem(10=ISCC)-
Zertifizierungsstelle-Zertifikatsnummer-Liefernummer;
Zur
      Nutzung dieses Formats trägt man bitte alles bis zur Liefernummer in das
      Textfeld zum Zertifikat ein
Zustand
Integer Codierung entsprechend
      Format NACHHSTAT
THG
      Wert
Ermittelter THG Wert
THG
      Herkunft
1=
      Kontrakt
2=Warenbewegung
3=Erzeuger (EK) / Mandant
      (VK)
4=Artikel
Das Label wird zur Darstellung in der Auswahlliste
„Bewegungsübersicht“ verwendet.
Je nach Eingangsparametrisierung kann, die ist
nachhaltig-Methode benutzt werden, um Nachhaltigkeitsinformation für
verschiedene Zwecke zu erhalten.
create procedure
ist_nachhaltig
(
in
in_wabewid        integer default 0
,in   in_wabewgruppe
integer default 90
,in
in_ArtikelId      integer default null
,in
in_KundId         integer default
null
,in
in_KtrId          integer default
null
,in   in_KtrArtiPosit
integer default null
,in
in_Klasse         integer default 0
,in
in_Date
date    default today()
)
RESULT (
zustand
integer
,farbe
integer
,label
char(255)
,text1
[...]


---

## Staatstamm

Staatstamm
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Staatstamm
Direktsprung
[STAAT]
Hier werden Informationen zu Staaten gepflegt
Werte in den
      Zollwarennummern
Bezeichnung
Bezeichnung des Staates
Post
      Länderkennzeichen
postalisches Kürzel des
      Landes
DATEV-Code
ISO-Code
ISO-Code des Landes
Gruppenzuordnung
Zollgruppe
Zollgruppe des Landes
SEPA-Teilnahmestaat
Ja/Nein

---

## Leermeldung unterbinden bei Automatischer Leermeldung (SPA 1010)

Leermeldung unterbinden bei Automatischer Leermeldung (SPA 1010)
Mit diesem Steuerparameter können Optionen für die
Silo Verwaltung eingestellt werden.
Option
Wert
Bedeutung
LEERMELDUNGUNTERBINDENBEIRESTMENGE
0
      ist Nein
1
      ist Ja
Mit
      diesem Steuerparameter kann die automatische Leermeldung ausgestellt
      werden. Bei der automatischen Leermeldung wurden automatisch Waagenbelege
      angelegt, welche die Menge des Silos auf 0 setzt. Danach wird das Silo
      erst leergemeldet.
Ist
      der Steuerparameter auf „Ja“ gestellt, so muss das Silo manuell auf die
      Menge 0 gesetzt werden. Danach darf das Silo erst leergemeldet
      werden.
BISABSMENGELEERMELDUNGOHNEWAAGENBELEG
Menge von 0 bis …
Standard Wert ist 0,01
Mit
      dieser Option kann eingestellt werden, bis zur welcher Grenzmenge eine
      Leermeldung ohne Waagenbeleg erzeugt werden darf. Ist die Menge auf dem
      Silo kleiner als die Grenzmenge, so wird auch bei der gesetzten Option „
      Leermeldung unterbinden bei Restmenge“ auch die Leermeldung
      durchgeführt.

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
die die Statistik erstellt. Diese Prozedur kann privatisiert werden. Das Feld
wird mit der Standardprozedur „TerresdatenexportStatistik“ vorbelegt.
In dem Feld „Pfad zur Ausgabe der Exportdatei“ wird
der Pfad angegeben wohin die Datei mit den Statistikdaten gespeichert wird.
Achtung der Pfad muss relativ zum Datenbankserver
liegen. Der Pfad wird vorbelegt mit dem Export Verzeichnis von Referenz-ERP, wenn
dieses sich Anhand der Logdatei der Datenbank ermitteln lässt. Dafür muss die
Datenbankeigenschaft consolelogfile gesetzt sein. Kann der Pfad nicht vorbelegt
werden, so muss ein Pfad eingetragen werden.
Ablauf
Die Statistik kann manuell übertragen werden oder per
Event als automatischer Lauf.
Bei der manuellen Übertragung ist es möglich für eine
Periode den Export mehrfach anzustoßen, dazu sind die Felder Periode und Jahr
auf der Maske „Datendrehscheibe Statistikexport“ anzugeben. Mit
Statistikexport Starten
[
F9
] wird der Export gestartet.
Bei der Übertragung per
Event
wird die letzte geschlossen Periode
übermit
[...]


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
In der Auswahlliste der Variante „Importierte
Positionen bearbeiten“ können bestimmte Felder farblich markiert, wenn diese zu
einem nicht erfolgreichen Anlegen des Vorgangs führen würden.
Folgende Bedeutung haben die farblich markierten
Felder
Feld
Farben Bedeutung
Status Stamm
1.   Weiß Bereit Vorgang
      kann erzeugt werden
2.   Grün Belegerzeugung
      oder Einspielung läuft
3.   Rot Es sind Fehler
      bei der Einspielung, beim Erzeugen aufgetreten oder der Stammsatz ist
      gelöscht worden.
Kundnr./ Kunde
1.   Weiß Kunde kann
      gewählt werden
2.   Rot der Lieferant hat
      eine Bestellsperre für diesen Artikel
Artikel / Artikelnummer
1.   Artikel kann Bestellt
      werden
2.   Rot der Artikel hat
      eine Bestellsperre
Artikellieferant /
      Artikellieferant
Status Position
1.   Weiß Bereit Vorgang
      kann erzeugt werden
2.   Grün Belegerzeugung
      oder Einspielung läuft
3.   Rot Es sind Fehler
      bei der Einspielung, beim Erzeugen aufgetreten oder der Posi
[...]


---

## Eingangsmeldung drucken

Eingangsmeldung drucken
Die Funktion
Eingangsmeldung drucken
druckt das für
eine/n Eingangsmeldung/Laufzettel in der
Vorlage
hinterlegte Formular auf dem
angegebenen Drucker.
Diese Funktion ist in der OptionBox schon vor dem Status
„Abgeschlossen“ anwählbar, so wie die Funktion
Formular drucken
.

---

## Felder verstecken

Felder verstecken
Über
CF7
kann
man festlegen, welche Felder nicht auf der Waagenmaske zu sehen sein
sollen.
Um diese Funktion in der OptionBox anwählen zu können, muss man die
Maske im Neufall geöffnet haben.
Es erscheint eine Meldung, dass man die
Felder und Label mit Doppelklick auswählen möchte und eine Abfrage, für wen
diese Angaben gespeichert werden soll.
Ja = für alle Bediener
Nein = für
aktuellen Bediener
Abbrechen = bricht die Funktion
Felder verstecken
ab
Nach Beantwortung der Abfrage kann man die
Felder und Label mit einem Doppelklick deaktivieren. Sie verschwinden sofort von
der Maske.
Um die Funktion für die Deaktivierung von Feldern wieder zu
verlassen, wählt man
Versteckte
Felder speichern
CF7
oder
Esc
. Die ausgesuchten Felder und
Label werden sich gemerkt und die Maske geschlossen.
Zum Löschen der Einstellungen verwendet man die
Funktion Profil löschen in der OptionBox. Je nachdem wie man die Funktion
Felder verstecken
gestartet hat, werden
die Einstellungen für den Bediener oder für alle gelöscht.
Versteckte Felder kann man nur durch Löschen der
Einstellungen wieder sichtbar machen, da sie einmal versteckt nicht mehr
anwählbar sind.
Eine pro Bediener angelegte Deaktivierung wird der
Deaktivierung für alle Bediener beim Öffnen der Waagenmaske vorgezogen.

---

## Registerkarte Testwiegung

Registerkarte Testwiegung
Testwiegung
Id
Nummer
Wann
Datum und Zeit von
      Testwiegungen
Inhalt
Ergebnis der Testwiegung
Rückgabe/Textfeld
Ausgabe von
      Rückmeldungen
Nicht druckbare Steuerzeichen werden
      hier durch ein „x“ ersetzt.
Es
      ist möglich den Rückgabetext zu markieren und
      weiterzuverarbeiten.
Prozedur
Name
      der SQL-Prozedur zur Auswertung der Wiegeergebnisse
Editieren
Möglichkeit zum Editieren dieser
      SQL-Prozedur
Berechnen
Ruft
      die Prozedur auf und gibt Wiegenummer, Gewicht und Waagennummer
      zurück
XML
      Edit
Ermöglicht das Editieren eines im
      Archiv abgelegten Waagenprofils
Protokoll
Das
      Protokoll der Testwiegung
Wiegen
Startknopf zum
      Testwiegen

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

## Zolldaten (Kundenstamm)

Zolldaten (Kundenstamm)
Ist dieser Kunde ein Kunde, der seinen Sitz im Ausland
außerhalb der EU hat, so können mit der Funktion „Zolldaten weitere
Informationen als Vorbelegung für die
Zollausfuhr
gespeichert werden.
Parameter
Bedeutung
Anmeldungsart Ausfuhr:
Hierbei handelt es sich um die Art
      der Ausfuhr. Unterschieden wird hier zwischen Ausfuhr in Drittland (EX)
      und Ausfuhr in ein EFTA-Land (EU). Dieses Feld wird vorbelegt über den
      Staatstamm. Je nachdem ob es sich bei der Nationalität der Adresse um ein
      Dritt- oder EFTA-Land handelt.
Bestimmungsland
Land
      in welches die Ausfuhr stattfinden soll. Vorbelegt durch die Nationalität
      der Adresse
Beförderungsmittel
      Inland/Verkehr
Verkehrszweig, welcher für den
      Transport der Ware im Inland verwendet wird
Beförderungsmittel
      Grenze/Verkehr
Verkehrszweig, welcher für den
      Transport der Ware ab dem Überschreiten einer EU-Grenze verwendet
      wird
Beförderungsmittel
      Grenze/Art
Art
      des Beförderungsmittels, welches für den Transport der Ware ab dem
      Überschreiten einer EU-Grenze verwendet wird
Beförderungsmittel
      Grenze/Staat
Nationalität des
      Beförderungsmittels, welches für den Transport der Ware ab dem
      Überschreiten einer EU-Grenze verwendet wird
Ausgangszollstelle
Zollstelle, über welche die Ware die
      EU verlässt
Art
      des Geschäfts
Art
      des Geschäfts welches der Ausfuhr zugrunde liegt
Teilnehmeridentifikation:
Teilnehmeridentifikation (TIN) des
      Empfängers der Ausfuhr.
Deutsche Identifikation:
Angabe ob es sich bei der angegeben
      TIN um eine deutsche TIN handelt.
Vermerk Ausfuhr
Ausfuhrvermerktext
Interne Bemerkung
Interne Bemerkung zu diesem
      Eintrag
Diese Angaben werden, sofern sie eingegeben wurden,
als Vorgabe in die Ausfuhrzollanmeldung übernommen und können so die wiederholte
Eingabe der Texte ersetzen.

---

## Zolldaten (Anschriften)

Zolldaten (Anschriften)
Die Funktion Zolldaten erscheint nur dann, wenn es
sich bei der angegeben Adresse um eine Adresse außerhalb der EU handelt. Um
festzustellen, ob es sich dabei um eine Nicht-EU-Adresse handelt, wird die
Relation StaatStamm zur Rate gezogen. Ist hier bei der Zollgruppe das
Kennzeichen 3 (Drittland) oder 4 (EFTA-Land) eingetragen, wird die Funktion und
damit die Bearbeitung der Zolldaten für diese Anschrift sichtbar gemacht.
Pflegbar ist der Staatstamm über den Direktsprung „STAAT“.
Bei diesen Daten handelt es sich um eine Vorauswahl
einiger, für eine Ausfuhranmeldung, erforderlicher Daten. Diese Daten sind nicht
zwingend für eine für den Kunden bestimmte Ausfuhr. Bei einer Ausfuhr selbst
besteht jederzeit die Möglichkeit diese vorausgewählten Daten zu verändern.
Anmeldungsart Ausfuhr:
Hierbei handelt es sich um die Art
      der Ausfuhr. Unterschieden wird hier zwischen Ausfuhr in Drittland (EX)
      und Ausfuhr in ein EFTA-Land (EU). Dieses Feld wird vorbelegt über den
      Staatstamm. Je nachdem ob es sich bei der Nationalität der Adresse um ein
      Dritt- oder EFTA-Land handelt.
Bestimmungsland:
Land
      in welches die Ausfuhr stattfinden soll. Vorbelegt durch die Nationalität
      der Adresse.
Beförderungsmittel
      Inland/Verkehr:
Verkehrszweig, welcher für den
      Transport der Ware im Inland verwendet wird.
Beförderungsmittel
      Grenze/Verkehr:
Verkehrszweig, welcher für den
      Transport der Ware ab dem Überschreiten einer EU-Grenze verwendet
      wird.
Beförderungsmittel
      Grenze/Art:
Art
      des Beförderungsmittels, welches für den Transport der Ware ab dem
      Überschreiten einer EU-Grenze verwendet wird.
Beförderungsmittel
      Grenze/Staat:
Nationalität des
      Beförderungsmittels, welches für den Transport der Ware ab dem
      Überschreiten einer EU-Grenze verwendet wird.
Beförderungsmittel
      Grenze/KEZ:
Kennzeichen des Beförderungsmittels,
      welches für den Transpor
[...]


---

## Zollstellen

Zollstellen
Hauptmenü
Warenverkauf
Ausfuhrbearbeitung
Zollstellen einspielen
Zollstellen sind Dienststellen des Zolls in
Deutschland und der EU, die unterschiedliche Funktionen haben und im Rahmen
einer Zollausfuhr eine Rolle spielen.
Als Voraussetzung für die Nutzung der Zollstellen muss der
Steuerparameter 833 – Zolldatenerfassung
aktiv
aktiviert werden.
Eine Liste der Zollstellen (Custom Office List) wird von der
europäischen Union veröffentlicht und als XML-Datei bereitgestellt.
Die Liste der Zollstellen kann unter
https://ec.europa.eu/taxation_customs/dds2/col/download_data_generic.jsp?Lang=de
heruntergeladen werden. Dazu muss die „COL-Generic-YYYYMMDD.zip“-Datei
gespeichert und entpackt werden.
In Referenz-ERP ist der dazugehörige Einspieler unter
Warenverkauf / Atlas Ausfuhrbearbeitung / Zollstellen einspielen zu finden. Um
die Zollstellen in das Referenz-ERP-System zu importieren, muss im
Zollstellen-Einspieler unter dem Feld „Dateiname“ der Pfad zur der entpackten
„COL-Generic.xml“ angegeben werden. Mit
F9
kann der Import-Vorgang gestartet
werden. Dabei werden die vorherigen Daten mit den neuen Zollstellen
überschrieben.
Die Liste der Zollstellen ändert sich ungefähr alle
4-6 Wochen. In der Regel ändern sich die Nummern der Zollstellen nicht. Ein
regelmäßiges Update ist hier nur für aktive Nutzer der Zollausfuhr zu empfehlen.
Da die Zollstellennummer z.B. im Lagerstamm gespeichert wird, ist nicht
auszuschließen, dass dort nach dem Update und Erlöschen einer Zollstelle eine
ungültige Zahl stehen bleibt. Das fällt spätestens bei der Zollausfuhr auf.
Hinweis zum Dateinamen:
Der Pfad zur XML-Datei, der im Einspieler angegeben
wird, ist ein relativer Pfad des Datenbankservers! So wird entweder die
heruntergeladene XML-Datei auf dem Datenbankserver oder auf einer für den
Datenbankserver zugreifbaren Netzwerkfreigabe abgelegt und als Pfad angegeben.

---

## Zollwarennummer

Zollwarennummer
Hauptmenü
Warenverkauf
Ausfuhrbearbeitung
Zollwarennummern
[ZWN]
Zollwarennummern sind Nummern, die eine Ware im
internationalen Warenverkehr kennzeichnen. Sie sind jeweils für die Dauer von
einem Jahr gültig und werden vom
Bundesamt für
Statistik in Wiesbaden
in Wiesbaden als Liste herausgegeben.
Die komplette Liste lässt sich in der Form einer sogenannten
SOVA-Leitdatei einspielen. Wenn Sie jedoch nur einige wenige Zollwarennummern
verwenden, so können Sie diese auch manuell mit der Anwendung Zollwarennummer
mit dem Direktsprung
[ZWN]
pflegen.
Werte in den
      Zollwarennummern
Zollwarennummer
Eine
      achtstellige Nummer, die führende Nullen beinhalten kann
Gültig von
Geben Sie hier den ersten Tag der
      Gültigkeit dieser Nummer ein
Gültig bis
Geben Sie hier den letzten Tag der
      Gültigkeit dieser Nummer ein
Bezeichnung
Bezeichnung der Ware
Zusatz
Zusatztext
Mengeneinheitsschlüssel
Der
      Mengeneinheitsschlüssel der Ware lt. Statistischem Bundesamt
Funktionen
Zollwarennummern
      einspielen
Startet das Einspielen der
      Zollwarennummern aus der Sovaleitdatei. Hierbei müssen der Name der
      Sovaleitdatei (z.B. SOVA2013.txt) und das Gültigkeitsjahr ( Jahreszahl,
      z.B. 2013 ) angegeben werden. Dies wird beim Verwenden der Funktion
      abgefragt.

---

## Zollausfuhr

Zollausfuhr
Bei der Zollausfuhr geht es um den Export von Waren
aus Deutschland in das außereuropäische Ausland.
Sie können mehrere Lieferungen für einen Endkunden zu
einem Zollpapier zusammenfassen und damit eine Zollanmeldung erstellen. Aufgrund
dieser Anmeldung wird vom Zoll ggf. eine Genehmigung erteilt und ein
Ausfuhrbegleitdokument (ABD) erstellt.
Mit diesem ABD kann die Ware dann aus der EU
ausgeführt werden.
Letztendlich wird, nachdem die Ware ausgeführt wurde,
von der zuständigen Ausgangszollstelle ein Dokument mit dem Ausgangs-Vermerk
erstellt.

---

## Archiv Anzeigen in Zollausfuhr

Archiv Anzeigen in Zollausfuhr
Wählen Sie die von Ihnen bearbeitete Zollanmeldung aus
der Auswahlliste in der Anwendung Zoll-Lieferscheine mit dem Direktsprung [LIZO]
aus und wählen die Funktion „Archiv Anzeigen“.
Sie bekommen eine Liste folgender Dokumente angezeigt:
•
Lieferscheine, die die Grundlage der angewählten Zollanmeldung sind
•
Ggf. schon abgeholte Ausfuhrbegleit-Dokumente
•
Ggf. schon abgeholte Ausgangsvermerk-Dokumente

---

## Ausfuhrdaten bearbeiten

Ausfuhrdaten bearbeiten
Parameter
Bedeutung
Kundennummer:
Nummer des Kunden auf den die
      Ausfuhranmeldung ausgestellt wird.
Teilnehmeridentifikation:
Teilnehmeridentifikation (TIN) des
      Empfängers der Ausfuhr.
Beispiel: EORI, EORI-Nummer, ggf.
      Niederlassungsnummer
oder:       TCUI,
      TCUI-Nummer
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      Hauptanschrift) des Vorgangs/Kunden
Kennnummer der Sendung:
Optionale Kennnummer der
      Sendung
Interne Bemerkung:
Feld
      zur Aufnahme einer internen Bemerkung
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      Hauptanschrift) des Vorgangs/Kunden
Sie erhalten eine Maske mit drei Registerkarten:

---

## Ausfuhr löschen

Ausfuhr löschen
Es kann sein, dass Sie bei der Zusammenstellung der
Positionen einen Fehler gemacht haben. Vielleicht haben Sie eine Position zu
viel ausgewählt oder vielleicht soll auch diese Ausfuhr aus betrieblichen
Gründen nicht mehr zur Anmeldung beim Zoll vorgelegt werden (Stornierung). Die
Funktion kann für bereits versendete Ausfuhrvorgänge nicht mehr ausgeführt
werden. Daten im Ausfuhrbeleg können dann nur noch im Web-Portal des
Dienstleisters geändert werden.
In diesem Fall haben Sie die Möglichkeit, die als
erfasst angezeigte Ausfuhr zu löschen. Alle erfassten Daten (Positionen,
Packstücke etc.) gehen dabei wieder verloren, die Lieferscheinpositionen stehen
(sofern der Lieferschein nicht inzwischen storniert wurde) wieder für eine neue
Bearbeitung zur Verfügung.

---

## Ausfuhr senden

Ausfuhr senden
Wenn Sie die Bearbeitung Ihrer Datenerfassung
abgeschlossen haben, können Sie die Ausfuhr beim Zoll anmelden.
Dazu wählen Sie die von Ihnen bearbeitete
Zollanmeldung aus der Auswahlliste in der Anwendung Zoll-Lieferscheine mit dem
Direktsprung [LIZO] mit dem Status „erfasst“ aus und wählen die Funktion
„Ausfuhr senden“.
Es wird die Prozedur
AEBAusfuhrAnmeldungAnlegen
aufgerufen. Diese ruft zunächst, falls vorhanden, die private Datenbankprozedur
p_ZollAusfuhrBelegDefaults(in in_vaId integer)
auf,
mittels derer die Daten im Ausgangsvorgang noch automatisiert ergänzt werden
können.
Anschließend wird die Korrektheit der Daten des Ausgangsvorgangs
mittels der Prozedur
AMIC_FUNC_VABeleg_Check
weitestgehend geprüft. Ggf. werden Einträge im Fehlerprotokoll
erstellt.
Werden keine Fehler festgestellt, so wird das für den Webservice
notwendige XML erzeugt und mittels der Prozedur
createOBTAtlas
an den
AEB-Webservice übermittelt.
Die Zollanmeldung wird damit an den Datendienstleister
versendet. Bei korrekter Einstellung „sofort senden“ im Register „Zoll“ des
Mandantenstamm-Pflegemoduls wird diese Anmeldung, sofern sie korrekt ist, vom
Dienstleister an den Zoll weitergeleitet. Anderenfalls bekommen Sie eine
Meldung, die Ihnen den Hinweis gibt, im Fehlerprotokoll nach Problemen beim
Versand zu suchen.
Der Status der Zeile wechselt von „erfasst“ auf
„versendet“. Bei vom Dienstleister festgestellten Fehlern oder
Unvollständigkeiten im gesendeten Beleg müssen die Daten auf dem Web-Portal des
Dienstleisters angepasst werden.

---

## Ausgangsvermerk-Dokumente abholen

Ausgangsvermerk-Dokumente abholen
Hat die Ware zum Ausfuhr-Vorgang das Zollgebiet der EU
verlassen, so wird in der Regel von der Ausgangs-Zollstelle ein Ausgangsvermerk
erstellt. Liegt dieses Dokument beim Dienstleister vor, so wird dieses zur
Abholung bereitgestellt. Der Status der Zollanmeldung ist dann „AgV liegt
bereit“. Sie können nun das Ausgangsvermerk-Dokument abholen.
Dazu wählen Sie die von Ihnen bearbeitete
Zollanmeldung aus der Auswahlliste in der Anwendung Zoll-Lieferscheine mit dem
Direktsprung [LIZO] mit dem Status „AgV liegt bereit“ aus und wählen die
Funktion „Ausgangsvermerk-Dokumente abholen“.
Diese Abholung kann auch periodisch durch ein sog.
Event erfolgen. Mehr dazu im Abschnitt Automatische Prüfung und Abholung.
Der Status der Zeile wechselt von „AgV liegt bereit“
auf „AgV abgeholt“.
Zur Abholung wird die Prozedur
AMIC_ABD_FUNKTION
aufgerufen. Die Prozedur erstellt das für den
Webservice notwendige XML und sendet es über die Prozedur
getAtlasExportTransaction
an den an den AEB-Webservice. Die Rückmeldung
wird verarbeitet, das Ausgangsvermerk-Dokument ins Formulararchiv geschrieben
und die Status-Informationen gesetzt. (Näheres siehe Dokumentation zur
Datenbankprozedur.)

---

## Automatische Prüfung und Abholung

Automatische Prüfung und Abholung
Mit Hilfe eines regelmäßig aufgerufenen Events ist es
möglich die Statusprüfung und die Abholung bereitgestellter
Ausfuhrbegleit-Dokumente und Ausgangsvermerk-Dokumente zu gewährleisten.
Sollen dabei Kontrollmitteilungen über bereitgestellte
oder abgelehnte Zollausfuhranmeldungen versendet werden, so muss im
Versandprofilstamm (ehem. Verpostungsstamm) ein Eintrag für den Typ
„
Infomails Zollanwicklung
“ erstellt werden.
Die Zieladressen für diese beiden Ereignisse sind im
Mandantenstamm auf der Registerkarte Zollausfuhr einzutragen.
Ein regelmäßiger Aufruf der Prozedur
AMIC_GET_ZOLL_STATUS
oder einer analogen Prozedur im Rahmen eines Events
sorgt für die gewünschte Abarbeitung.

---

## Beantragen der Zugangsdaten für Zollausfuhr

Beantragen der Zugangsdaten für Zollausfuhr
Zur Nutzung der Zollausfuhr ist der kostenpflichtige
Zugang zum Webservice des Datendienstleisters AEB notwendig.
Diesen müssen Sie selbst beantragen. Er ist nicht im
Leistungsumfang der Referenz-ERP-Zollabwicklung enthalten.
Auf der Webseite
https://www.aeb.com/
haben Sie die
Möglichkeit, diesen Zugang zu beantragen. Füllen Sie das Online-Formular mit den
Daten Ihrer Firma aus und wählen Sie den für Ihre Situation passenden Tarif.
Klicken Sie am unteren Ende des Formulars auf
„weiter“.
Ihnen werden die Zugangsdaten alsbald von AEB
zugesandt werden, mit denen Sie dann die Zollabwicklung nutzen können, nachdem
Sie die Zugangsdaten im Mandantenstamm [MND] in der
Registerkarte Zollausfuhr
eingetragen
haben.

---

## Begleitdokumente abholen

Begleitdokumente abholen
Wurde eine Zollanmeldung von der Zolldienststelle
genehmigt, so wird ein Ausfuhrbegleitdokument bereitgestellt. Der Status der
Zollanmeldung ist dann „ABD liegt bereit“. Sie können nun das
Ausfuhrbegleitdokument abholen.
Dazu wählen Sie die von Ihnen bearbeitete
Zollanmeldung aus der Auswahlliste in der Anwendung Zoll-Lieferscheine mit dem
Direktsprung [LIZO] mit dem Status „ABD liegt bereit“ aus und wählen die
Funktion „Begleitdokumente abholen“.
Diese Abholung kann auch periodisch durch ein sog.
Event erfolgen. Mehr dazu im Abschnitt Automatische Prüfung und Abholung.
Der Status der Zeile wechselt von „ABD liegt bereit“
auf „ABD abgeholt“.
Zur Abholung wird die Prozedur
AMIC_ABD_FUNKTION
aufgerufen. Die Prozedur erstellt das für den
Webservice notwendige XML und sendet es über die Prozedur
getAtlasExportTransaction
an den an den AEB-Webservice. Die Rückmeldung
wird verarbeitet, das Ausfuhrbegleitdokument ins Formulararchiv geschrieben und
die Status-Informationen gesetzt. (Näheres siehe Dokumentation zur
Datenbankprozedur.)

---

## Beispiel einer eigenen Anwendung

Beispiel einer eigenen Anwendung
Hier wird gezeigt, wie eine private Tabelle in Referenz-ERP
mit AIS gepflegt werden kann. Als Beispiel wird eine manuelle Bestandsmeldung
von Lägern an die Zentrale gewählt.
Zum Anlegen der privaten Tabelle benutzt man den
üblichen Datenbankbefehl.
Create table admin.P_Bestand
( Ident integer not null,
Datum date,
Lager integer default 0,
Artikel char(16),
Bestand numeric ( 30,4 ) default 0.00,
Bemerkung char(64),
Bediener char(16) default current user,
Zeitstempel timestamp default current
timestamp,
primary key ( Ident ) ) ;
Der Befehl kann über OSQL direkt eingegeben oder als
ASQL gespeichert und dann ausgeführt werden.
Wählt man diese Form der Tabellenanlage so erkennt AIS
die Eingabefelder als existent und belässt sie in der Tabelle.
Legt man die Eingabefelder ( Datum, Lager, Artikel,
Bestand, Bemerkung ) nicht mit create an, so werden sie von AIS angelegt
Zusätzlich ist es notwendig, einen Eintrag in der
Tabelle Ident vorzunehmen. Aus dieser Tabelle werden bei Neuerfassung die Werte
für den Primary Key gelesen.
insert into ident
( IdentTableName, IdentColumnName, IdentIdent,
IdentAktivKont, IdentAngefKont)
Values
( 'p_bestand', 'Ident', 0, 1, 0)
Referenz-ERP muss einmal verlassen und neu gestartet werden,
damit dieser neue Eintrag zur Verfügung steht.
Einbinden in Referenz-ERP
Private Variante unter Private Anwendung
[PRANW]
Mit Privater Option Box (P_OB )
In die Option Box fügt man üblicherweise die private
Funktion für Selektion (
F2
) ein.
Menüpunkt einrichten
Der Menüpunkt „
Manuelle Bestandsmeldung
“
wurde wie üblich als Private Funktion (Direktsprung
[PF]
) angelegt und
mit dem Menü „
Individuelle Programme
“ (73) verbunden, einsortiert
und geschützt.
Der vollständige Controlstring lautet hier:
^jpl
aw_vert Private_Anwendungen Private_Anwendungen Private_Anwendungen
466085_21
In der Variante 1 zu AIS muss zunächst mindestens ein
Feld der Gruppe angelegt werden. Wir bauen hier z.B. eine bunte, große
Überschrift.
Die Varia
[...]


---

## Berichtsrückmeldungen

Berichtsrückmeldungen
Um nun einen Rundlauf der Informationen zu bekommen,
d.H. um Besuchsberichte auch auf dem Laptop oder dem Pocket PC erfassen zu
können, muss das AIP System installiert sein, und ein Exchange Server oder ein
vergleichbares e-Mail System  muss die Einlaufenden e-Mails abfangen
können.
Unter diesen Voraussetzungen können nun e-Mail an eine
festgelegte e-Mail Adresse gesendet werden, die dann automatisch die
einkommenden e-Mails in die Besuchsberichtsstruktur von Referenz-ERP integriert.
Die Betreffzeile der e-Mail muss den Text "Besuch:"
gefolgt von der Kundennummer enthalten, und nur diese e-Mails werden dann als
Besuchsberichte in das System übernommen.
Die auf einem Pocket PC eingerichtete Offline
Sendemechanik erlaubt ein erfassen aller Besuchsberichte während des Tages, und
bei Anschluss des Pocket PC's an die Docking Station werden die Berichte sofort
übergeben, um dann im nächsten Schritt auch wieder in die Outlook
Kontaktkarteikarten übernommen werden zu können.

---

## Bestandsmengen

Bestandsmengen
Aussagen über Bestandsmengen lassen sich auf
verschiedene Weisen gewinnen.
Bestandart
Beschreibung
Kumulierter Bestand
Der
      kumulierte Bestand ergibt sich aus der Gesamtheit aller Warenbewegungen,
      die den Lieferbestand verändern. Er kann aufgeschlüsselt
      werden
Je
      Lager
Je
      Lagerplatz
Nach
      Eigen- und Fremdbestand
Nach
      disponiertem Bestand (Verkauf)
Nach
      Bestellungen (Einkauf)
Die
      Bestandsaussagen beruhen auf dem Lieferbestand, der disponierte Bestand
      ergibt sich aus der Gesamtheit aller offenen Aufträge, der Bestellbestand
      ergibt sich aus der Gesamtheit aller nicht gelieferten
      Bestellungen.
Es
      handelt sich um aufgelaufene Mengen ohne Bezug zu einer Zeitachse.
Bestand per Stichtag
Liefert die Bestandsmenge zu einem
      vorzugebenden Stichtag und basiert auf dem Lieferbestand. Damit werden
      also Aussagen der Form „Wie war mein Bestand am tt.mm.jj?“ beantwortet.
      Intern wird diese Form der Bestandsanfrage etwa zum Abgleich der
      Inventurzählmenge mit dem Sollbestand am Erhebungstag benutzt. Weitere
      Anwendung etwa als Feuerversicherungsliste.
Der
      Stichtagsbestand kann aufgeschlüsselt werden:
Je
      Lager
Je
      Lagerplatz
Nach
      Eigen- und Fremdbestand
Disponierter Bestand
Fakturierter Bestand
Warenbuch
Fremdbestand

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

## DotNet-Module

DotNet-Module
-100000
Nur Info
Diese Meldung ist eine Mitteilung, die informellen
Wert hat. Es besteht in den meisten Fällen keinerlei Notwendigkeit zur
Behandlung.
-100002
Unbekannter Kommandoaufruf
Es ist ein Kommandoaufruf an das Startmodul gesendet
worden, den das System nicht kennt. Möglicherweise ist das aufgerufene Modul
nicht oder nicht korrekt installiert.
-100003
Unbekannte Nachricht empfangen
Es wurde über den Nachrichtenaustauschkanal von Referenz-ERP
eine Nachricht unbekannten Typs empfangen. Es besteht u.U. ein
Komatiblitätsproblem zwischen Komponenten der Software.
-100004
Zugehöriges Referenz-ERP läuft nicht mehr
Diese Nachricht ist obsolet. Sie sollte nicht mehr
auftreten.
-100005
Insert/Update/Delete nicht möglich
Ein Insert, Update oder Delete-Befehl in der Datenbank
ist fehlgeschlagen.
-100006
Fehler beim Laden der AddInListe
Die Liste der Elara-AddIns konnte nicht korrekt
geladen werden. Unter Umständen können aufzurufende Module nicht gefunden und
gestartet werden.
-100007
Fehler im Methodennamen des AddIns
Das AddIn, das hier aufgerufen wurde, entspricht mit
seiner Methodendefinition nicht dem Standard. Es wurde eine Methode nicht oder
nicht der Schnittstellendefinition entsprechend implementiert.
-100008
Fehler im Namespace des AddIns
Das AddIn, das hier aufgerufen wurde, entspricht mit
seiner Namespacedefinition nicht der Vorgabe.
-100009
Fehler beim Instanziieren einer Pipe zu Referenz-ERP
Die Kommunikationsverbindung zwischen Referenz-ERP und dem
DotNet-Steuermodul Elara konnte nicht instanziiert werden. Es besteht keine
Verbindung zwischen den Komponenten. AddIns können nicht aufgerufen und
gestartet werden.
-100050
Datenbank-Verbindung nicht hergestellt oder
unterbrochen
-100051
Ein Insert konnte nicht durchgeführt werden
Eine Datenzeile konnte nicht mit Hilfe eines
Insert-Befehls in die Datenbank eingefügt werden. Die Daten wurden nicht
gespeichert.
-100052
Ein Select konnte nicht ausgeführt werden
Eine Datenzeile konnte nicht mit Hilfe eine
[...]


---

## Einrichten der Prozeduren für Zollausfuhr

Einrichten der Prozeduren für Zollausfuhr
In Formularzuordnung [FRZ] gibt es eine
Registerkarte Zoll
. Darin befinden sich
einige Prozeduren, die für bestimmte Funktionen innerhalb der Zollabwicklung
eingerichtet werden können.
Die „Prozedur für Intrastat“ steht in keinem direkten
Zusammenhang mit der Zollabwicklung.

---

## Einrichten der Zugangsdaten für Zollausfuhr

Einrichten der Zugangsdaten für Zollausfuhr
Die Zugangsdaten zum Datendienstleister müssen in den
Mandantenstamm in der
Registerkarte Zollausfuhr
eingetragen
werden.
Zur Nutzung der Zollausfuhr ist der kostenpflichtige
Zugang zum Webservice des Datendienstleisters AEB notwendig.

---

## Erstellen einer Zollanmeldung

Erstellen einer Zollanmeldung
Zunächst rufen Sie die Anwendung Zoll-Lieferscheine
mit dem Direktsprung [LIZO] auf. Dort werden zweierlei Daten aufgelistet:
•
Alle Lieferscheine mit deren Positionen an Kunden außerhalb der EU, die
noch nicht verarbeitet wurden
•
Alle Zollanmeldungen
Wählen Sie die zu einer Lieferung zusammenzufassenden
Lieferscheinpositionen aus. Achten Sie dabei auf die Reihenfolge der
Markierung.
Das Lager der letzten markierten Position bestimmt die
verwendete Ausfuhrzollstelle, also die Zollstelle, bei der die Ausfuhr
angemeldet wird.
Wählen Sie nun die Funktion „Ausfuhrdaten
bearbeiten“.

---

## Fehlermeldungen Branchen-ERP Etikettendruck

Fehlermeldungen Branchen-ERP Etikettendruck
Es können verschiedene Fehlersituationen auftreten,
bei denen eine der folgenden Meldungen ausgegeben wird:
•
Branchen-ERP Etikettendruck konnte nicht initialisiert werden!
•
Keine passende Sprach-DLL (*.lng) gefunden.
Im Auslieferungsumfang
ist die Spach-Dll für Deutsch enthalten. Sollte der Fehler trotzdem auftreten,
so verständigen sie bitte ihren zuständigen Systembetreuer.
•
Referenz-ERP Makro konnte nicht initialisiert werden!
Das angegebene Makro
existiert nicht oder ist fehlerhaft.
•
Fehler beim Druck(Fehlercode)
Beim Druck trat ein Fehler auf. In
Klammern steht die vom „Branchen-ERP Etikettendruck“ zurückgelieferte
Fehlernummer
. Sollte dieser Fehler
auftreten und die teils technischen Hinweise liefern ihnen keine Hilfe, so
setzen sie sich bitte mit ihrem Systembetreuer in Verbindung.
•
Einer der im Report verwendeten Ausdrücke hat einen Fehler.
Der Report
muss überarbeitet werden. Eventuell hat sich die Datengrundlage geändert und
einige Felder, die im Report verwendet werden, werden nicht mehr angeboten.
Dieser Fehler kann z.B. durch Änderung der Auswahlliste – bei Datenherkunft
Auswahlliste - entstehen.
•
Fehler: Der Abschlussbereich ist zu klein eingerichtet!
Branchen-ERP
Etikettendruck versucht die Daten in den eingerichteten Bereich zu drucken. Ist
dieser Bereich zu klein,  wird diese Fehlermeldung ausgegeben. Der Report
muss dann angepasst werden.
•
LlDefineLayout lieferte einen Fehler (Fehlercode).
Beim Aufruf des
interaktiven Designers vom Branchen-ERP Etikettendruck trat ein Fehler auf. In Klammern
steht die vom „Branchen-ERP Etikettendruck“ zurückgelieferte
Fehlernummer
. Sollte dieser Fehler
auftreten und die teils technischen Hinweise liefern ihnen keine Hilfe, so
setzen sie sich bitte mit ihrem Systembetreuer in Verbindung.

---

## Fehlermeldungen und Hinweise

Fehlermeldungen und Hinweise
Tritt ein Fehler auf so wird das Script beendet und
eine Fehlermeldung in die Fehlerprotokolltabelle geschrieben. In den
Fehlermeldungen werden zur schnellen Identifizierung der Fehlerursache das
aufrufende Script, die Funktion, evtl. eine Textposition und ein Hinweis auf den
Fehler angegeben.
Hat der Automatismus einwandfrei funktioniert so
werden diverse Hinweise in die Fehlerprotokolldatei geschrieben. In den
Hinweisen werden die unterschiedlichen Vorgänge sowie die wichtigsten Attribute
wie Kundennummer, Artikelnummer, Partienummer etc. angegeben.
Steht im Fehlerprotokoll - Bereich
„Auftrag
automatisch erzeugen“
so wurde die Meldung vom Script bestellung_start.vbs
generiert. Steht dort
„Bestellung automatisch erzeugen“
so kommt der
Hinweis vom Script „bestellung.vbs“
In der ersten Zeile steht jeweils ein Hinweis was dort
aufgetreten ist, ein
„Fehler!“
oder ein
„Hinweis!“
Ist ein Script automatisch und ohne Fehler abgelaufen
so stehen zurzeit 6 Hinweise im Fehlerprotokoll
Jeweils 2 Meldungen gehören zu einem Vorgang,
der Auftrag steht unter „Auftrag automatisch erzeugen“
(aus bestellung_start.vbs)
wenn der Auftrag erfolgreich bearbeitet wurde wird ein
Eintrag unter „bestellung automatisch erzeugen“ (aus Bestellung.vbs)
erzeugt
Steht zu Beginn der sechs zum Automatismus gehörenden
Spalten unter „was“ nur „Hinweis ! ..:“  (und nicht Fehler !) ist die
automatische Vorgangserstellung korrekt abgelaufen.
Nun kann zur Endkontrolle anhand der Hinweise im
Fehlerprotokoll im Aeins-System kontrolliert werden ob alle Vorgänge auch
korrekt abgearbeitet wurden, die Partien und Mengen stimmen.
Die Fehler- und Hinweismeldungen können über die
Schalter
MSG_ERROR_ON
MSG_HINWEIS_ON
abgeschaltet werden. Dieses ist zurzeit nur im Script
möglich.
Eine Möglichkeit diese über Parameter oder über einen
Konfigurationsabschnitt in der XML-Datei zu steuern ist angedacht.

---

## Fehlermeldungen (Waagendatenimport-/-export)

Fehlermeldungen (Waagendatenimport-/-export)
Die meisten Fehlermeldungen werden direkt in das
Fehlerprotokoll geschrieben und werden nicht unmittelbar ausgegeben. Es gibt
allerdings einige wenige Fehler, die zu sofortiger Anzeige einer Meldung
führen:
Kann Datei nicht finden/öffnen C:\TEMP\WAAGE.DAT
Existiert das im Parameter WAAGEDAT angegebene
Verzeichnis überhaupt?
Unter Windows 95 wird u. U. eine DOS-Box nicht korrekt
beendet. Sobald die DOS-Box auf der Taskleiste erscheint, sollte man sie
anklicken. Sie wird nun beendet, und das Programm arbeitet ordnungsgemäß
weiter.
Wurde unter DATEINAME eine Datei festgelegt, die sich
nicht auf dem Datenträger befindet und MULTI_FILES=0, dann kann es nicht
klappen.
Wurde die Datei evtl. im Editor geöffnet, oder ist die
Importdatei im Windows-Explorer markiert, dann kann sie nicht kopiert werden und
der Zugriff auf des Kopierergebnis schlägt fehl.
Wenn nach dieser Fehlermeldung eine Datei, z. B.
A:\WAGGE.DAT auf der Importdatenträger fehlt, dann wurde im Parameter WAAGEDAT
fälschlicherweise der Name der/einer Importdatei angegeben und nicht ein
Dateiname auf der Festplatte wie C:\TEMP\WAAGE.DAT als Ziel für das Kopieren der
Importdatei/en.

---

## Hauptmenü – Arbeitsbereich

Hauptmenü – Arbeitsbereich
Folgende Objekte werden je nach aktiviertem Bereich
hier angezeigt:
Bereich
Objekte
Menüpunktbereich
Überschriften und
      Menüpunkte
Favoritenbereich
Menüpunkte
Systemmeldebereich
Systemmeldungen

---

## Hauptmenü-Systemmeldebereich

Hauptmenü-Systemmeldebereich
Element
Tastatur
Beschreibung
Icon
Beschriftung
Systemmeldung(X)
X
      steht für die Anzahl der Systemmeldungen
Im Systemmeldebereich werden die
Systemmeldungen
angezeigt.
Mit der Kontextmenü-Funktion „Diese Systemmeldung für
diese Sitzung ignorieren“ lässt sich die betreffende Systemmeldung für die Dauer
der aktiven Aeins-Sitzung ausblenden.
In dem Ausnahmefall das eine technische Störung
auftritt wird dieses durch die geänderte Beschriftung des Systemmeldungs-Icons
mitgeteilt. Sie enthält einen Hinweis auf den namen im Temp-Verzeichnis in dem
der Ausnahme-Meldungstext enthalten ist.

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

## Innergemeinschaftliche Lieferungen

Innergemeinschaftliche Lieferungen
Innergemeinschaftliche Lieferungen (§ 4 Nr.1 Buchst. B
UstG) an Abnehmer mit Ust-IdNr. in Staaten der EU sind in Zeile 210 unter
Kennziffer 41 der Umsatzsteuervoranmeldung einzutragen. Ihr detaillierter
Nachweis erfolgt im Rahmen der Zusammenfassenden Meldung. In Referenz-ERP sind die
Steuerklasse 1 und 2 für Verkauf davon betroffen.
Einrichtung
Um die Steuer für die Innergemeinschaftlichen
Lieferungen auf dem USTVA-Formular ausweisen zu können, sind im
Steuersatzpfleger alle relevanten Kombinationen dieser Steuergruppe
einzutragen. Dabei sind folgende Besonderheiten zu beachten.
•
Steuersatz
0,00 als tatsächlicher Steuersatz
•
Steuerkonto
Fiktives Steuerkonto, falls der Umsatz in Listen
      nach Steuerkonto erscheinen soll
•
AW-Kennz. Umsatz
Auswertungsposition zur Steuerung des
      Umsatzsteuerformulars. In der Beispielliste für
Auswertungspositionen
wäre es
      die Zeile 210 Kennziffer 41.

---

## Innergemeinschaftlicher Erwerb

Innergemeinschaftlicher Erwerb
Bei Warenbezug aus dem EU-Ausland tritt an Stelle der
Einfuhrumsatzsteuer der Tatbestand des innergemeinschaftlichen Erwerbs (§ 1 Abs.
1 Nr. 5 UStG, § 1 a UStG). Das bedeutet, dass Unternehmer und andere
Erwerbssteuerpflichtige für „Importe“ aus anderen EU-Ländern keine
Einfuhrumsatzsteuer an den Zoll bezahlen müssen, sondern ihre Erwerbe in der
Umsatzsteuer-Voranmeldung beim zuständigen Finanzamt anzumelden haben. In Referenz-ERP
sind die Steuerklasse 101 und 102 davon betroffen. Um Lieferanten zu
kennzeichnen, dass sie dem innergemeinschaftlichen Wahrenverkehr unterliegen,
richtet man eine gesonderte Steuergruppe für EU-Kunden/Lieferanten ein.
Diese ist dann im Kundenstamm zu hinterlegen.
Einrichtung
Um die Steuer für den Innergemeinschaftlichen Erwerb
auf dem USTVA-Formular ausweisen zu können, sind im
Steuersatzpfleger
alle relevanten
Kombinationen dieser Steuergruppe einzutragen. Dabei existieren zwei
Möglichkeiten der Einrichtung.
1.
Der Innergemeinschaftliche Erwerb wird nicht auf Konten gebucht, sondern nur in
dem Umsatzsteuerauswertungen fiktiv errechnet und ausgegeben.
Feld
Beschreibung
Steuerformel
Normale Steuer
Steuersatz
0,00
      als tatsächlicher Steuersatz
Satz
      innergm.Erw.
Steuersatz, dem der Artikel
      eigentlich unterliegt.
AW-Kennz. Umsatz
Auswertungsposition zur Steuerung
      des Umsatzsteuerformulars. In der Beispielliste
für
Auswertungspositionen
wären
      es die Zeilen 350, 360 oder 370 und somit die Kennziffern 89,93 oder 95 je
      nach Einfuhrsteuersatz.
Steuer
Bleibt frei, also 0.
Einfuhrsteuer (MwSt)
Hier
      gehört die Auswertungsposition analog des AW-Kennzeichens  hinein,
      also auch 350, 360 oder 370 je nach Einfuhrsteuersatz. Auf dem
      Umsatzsteuerformular wird hier dann die fiktive anfallende Erwerbssteuer
      errechnet und ausgewiesen.
Einfuhrsteuer (Vst)
Hier
      gehört die Auswertungsposition hinein, die die Vorsteuerbeträge aus dem
      innergem
[...]


---

## Intrastat

Intrastat

---

## Intrastat: Art des Geschäftes

Intrastat: Art des
Geschäftes
Es handelt sich hierbei um eine Angabe über bestimmte
Klauseln des Geschäftsvertrages. Diese Daten sind Teil der Auslieferung und
nicht pflegbar. Die „Arte des Geschäfts“ kann bei den
Intrastat
Zusatzdaten
hinterlegt werden.
Format
Bezeichnung
11
Endgültiger Kauf/Verkauf
12
Ansichts- oder Probesendungen,
      Sendungen mit Rückgaberecht und Kommissionsgeschäfte
13
Kompensationsgeschäfte
      (Tauschhandel)
14
Finanzierungsleasing
      (Mietkauf
19
Geschäfte mit Eigentumsübertragung,
      Sonstiges
21
Rücksendung von Waren
22
Ersatz für zurückgesandte
      Waren
23
Ersatz (z. B. wegen Garantie) für
      nicht zurückgesandte Waren
29
Rücksendung von Waren ...,
      Sonstiges
31
Warenlieferungen im Rahmen von durch
      die Europäische Gemeinschaft ...
32
andere Hilfslieferungen öffentlicher
      Stellen
33
sonstige Hilfslieferungen (von
      Privaten ...)
34
sonstige Geschäfte
41
Warensendung zur Lohnveredelung,
      vor. Zurückgelangung
42
Warensendung zur Lohnveredelung,
      vor. Nichtzurückgelangung
51
Warensendung nach Lohnveredelung,
      Zurückgelangung
52
Warensendung nach Lohnveredelung,
      nicht Zurückgelangung
71
für
      militärische Zwecke
72
für
      zivile Zwecke
81
Geschäfte mit Lieferung von
      Baumaterial...
91
Miete, Leihe und Operate
      Leasing
99
Andere Geschäfte, die sich den
      anderen Schlüsseln nicht zuordnen lassen

---

## Intrastat-Meldung (Einfuhr)

Intrastat-Meldung (Einfuhr)
Hauptmenü
Warenverkauf
Intrastat
Intrastat-Meldung
Variante 3: Intrastat-Meldung
(Einfuhr)
oder Direktsprung
[INTRA]
Felder der Intrastat-Meldung
Feld
Bezeichnung
Jahr
Siehe auch:
Jahr
Periode
Siehe auch:
Perioden
Kalenderjahr
Monat
Beteiligtes Land
Staat des zugehörigen Mandanten
      (Iso-Code aus dem Staatstamm)
Das
      für die Intrastatmeldung relevante Land.
Siehe auch:
Staatstamm
UStid Mandant
Umsatzsteuerid des zugehörigen
      Mandanten
Im
      Normal-Fall die im Vorgang hinterlegte UStid. Ist diese nicht angegeben
      wird die Default-UStid des Mandantstammes herangezogen.
Siehe auch:
Finanzbuchhaltung Ust-IdNr.
UStid Kunde
Umsatzsteuerid des
      Kunden
Artikel-Intrastatnummer
Die
      im Artikelstamm hinterlegte Intrastatnummer des Artikels:
|
      X   |
=
      Intrastat-Artikel Nummer wurde nicht im Artikelstamm
      hinterlegt
Artikel
ID
      des Artikels
Art
      des Geschäftes
Art des
      Geschäftes
Verkehrszweig
Verkehrszweig
Region
Wert
Statischer Wert
Masse
Besondere Maßeinheit
Paginiernummer
Die
      Meldungen benötigen eine fortlaufende Nummer
DATA
Hilfsfeld für den Export von
      ACCI-Dateien.
Suchmöglichkeiten der Intrastat-Meldung
Suchen
Beschreibung
Periode
Von…
      bis…
Jahr
Von…
      bis…
Artikel-Intrastatnummer
%
UstId Mandant
%
UstId Kunde
%
Verkehrszweig
%
Funktionen der Intrastat-Meldung
Suchen
Beschreibung
Einfuhr erzeugen (
F9
)
Erstellt die Intrastat Dateien, je
      nach Einstellungen der
Intrastat
      Einrichtung
(XML/ASCII)
Der
      Export wird
nicht
nach den eingegeben Suchkriterien erstellt,
      sondern immer auf Basis aller Daten (eingegrenzt von Jahr &
      Periode)
Intrastat einrichten (
F10
)
Ruft
      die Maske zu
Intrastat
      Einrichtung
auf

---

## Intrastat-Meldung (Versendung)

Intrastat-Meldung (Versendung)
Hauptmenü
Warenverkauf
Intrastat
Intrastat-Meldung
Variante 2: Intrastat-Meldung
(Versendung)
oder Direktsprung
[INTRA]
Felder der Intrastat-Meldung
Feld
Bezeichnung
Jahr
Siehe auch:
Jahr
Periode
Siehe auch:
Perioden
Kalenderjahr
Monat
Beteiligtes Land
Staat des zugehörigen Mandanten
      (Iso-Code aus dem Staatstamm)
Siehe auch:
Staatstamm
UStid Mandant
Umsatzsteuerid des zugehörigen
      Mandanten
Im
      Normal-Fall die im Vorgang hinterlegte UStid. Ist diese nicht angegeben
      wird die Default-UStid des Mandantstammes herangezogen.
Siehe auch:
Finanzbuchhaltung Ust-IdNr.
UStid Kunde
Umsatzsteuerid des
      Kunden
Artikel-Intrastatnummer
Die
      im Artikelstamm hinterlegte Intrastatnummer des Artikels:
|
      X   |
=
      Intrastat-Artikel Nummer wurde nicht im Artikelstamm
      hinterlegt
Artikel
ID
      des Artikels
Art
      des Geschäftes
Art
      des Geschäftes
Verkehrszweig
Verkehrszweig
Region
Wert
Statischer Wert
Masse
Besondere Maßeinheit
Paginiernummer
Die
      Meldungen benötigen eine fortlaufende Nummer
DATA
Hilfsfeld für den Export von
      ACCI-Dateien.
Suchmöglichkeiten der Intrastat-Meldung
Suchen
Beschreibung
Periode
Von…
      bis…
Jahr
Von…
      bis…
Artikel-Intrastatnummer
%
UstId Mandant
%
UstId Kunde
%
Verkehrszweig
%
Funktionen der Intrastat Meldung
Suchen
Beschreibung
Versand erzeugen (
F9
)
Erstellt die Intrastat Dateien, je
      nach Einstellungen der
Intrastat
      Einrichtung
(XML/ASCII).
Der Export wird
nicht
nach den eingegeben
      Suchkriterien erstellt, sondern immer auf Basis aller Daten (eingegrenzt
      von Jahr & Periode)
Intrastat einrichten (
F10
)
Ruft
      die Maske zu Intrastat Einrichtung auf

---

## Gesetzliche Grundlagen

Gesetzliche Grundlagen
Die Intrahandelsstatistik ist eine in allen 27
EU-Staaten vorgeschriebene Meldepflicht zur
Erhebung von Statistiken über die
innergemeinschaftlichen Warenbewegungen
mit
"Gemeinschaftswaren". Mit den Intrastat-Meldungen wird
der tatsächliche Warenverkehr
von Gemeinschaftsware zwischen Mitgliedstaaten der
Europäischen Gemeinschaft
(Versendungen und Eingänge) durch das
Statistische Bundesamt
statistisch erfasst.
Von der Meldepflicht für die jeweilige
Verkehrsrichtung (Versendung bzw. Eingang) sind in
Deutschland umsatzsteuerpflichtige Unternehmen
befreit, deren Versendungen in andere
EU-Mitgliedstaaten bzw. Eingänge aus anderen
EU-Mitgliedstaaten den Wert von jeweils
400.000 Euro
im Vorjahr nicht überschritten
haben.
Es liegt in der Natur der Sache, dass eine enge
Verbindung zu den anderen EU relevanten Meldungen besteht :
Umsatzsteuervoranmeldung, Position
„Innergemeinschaftliche Lieferung“
dito., Positionen zum „Innergemeinschaftlichen
Erwerb“
Zusammenfassende Meldung
Auch die Nationalen Finanzbehörden der EU – Staaten
haben ihre EDV – Systeme offensichtlich „quergeschaltet“. Die gemeldeten Zahlen
werden auf Konsistenz geprüft.
Meldeformen :
Online Formulareingabe im Internet
Datei-Upload von Meldedateien
Papierform mittels Vordrucke NV 2002 und NE 2002
Zeitliche Grundlage ist das tatsächliche Lieferdatum
der Warenbewegung. Die Intrastat – Meldung muss monatlich bis spätestens zum
10ten Arbeitstag des Folgemonats abgegeben sein.

---

## Mandanten Server - Fehler

Mandanten Server - Fehler
Hauptmenü
Systempflege
Mandantenserver
Mandantenserver Fehler
Dieser Report listet Meldungen des Mandantenservers.

---

## Menü-Anmeldungen

Menü-Anmeldungen
Administration
Menü
Menü-Anmeldungen
oder Direktsprung
[
MENUA
]
In dieser technischen Variante werden die
Menü-Anmeldungen an das Aeins-System angezeigt.
Jede Aeins-Laufzeit-Instanz bekommt eine weltweit
eindeutige GUID zugewiesen, anhand derer die Systeme die Aeins-Laufzeit-Instanz
eindeutig bestimmen können.
Eine Aeins-Laufzeit-Instanz besitzt diverse
Umgebungsparameter:
Menü-Anmeldungen
Bedienerid
Die
      Id des Bedieners der Aeins-Instanz.
Kurzname
Der
      Kurzname des Bedieners zur einfacheren Identifikation.
Anmeldung
Der
      Datenbank-Server-Zeitpunkt, an dem das Aeins-System den Anwender an das
      Hauptmenü weitergeleitet hat.
Status
Eigen
: Ihre eigene Instanz!
Folgende Ausprägungen werden jeweils
      beim Aufbau der Variante ermittelt:
Abgemeldet
: Die Instanz ist nicht mehr mit dem
      Datenbank-Server verbunden.
Aktiv
: Die Instanz ist aktiv mit dem
      Datenbank-Server verbunden.
Connection
Die
      technische Verbindungsidentifikation der Aeins-Instanz mit dem
      Datenbank-Server
Host
Der
      Hostname des Rechners auf dem die Aeins-Instanz läuft.
Prozess-ID
Die
      Windows-PID des Prozesses.
Menü
ActiveX
:
Technische Basis des verwendeten
      Haupt-Menüs ist ActiveX
(Referenz-ERP-Standard-Hauptmenü)
A1Net
:
Technische Basis des verwendeten
      Haupt-Menüs ist ActiveX/.NET
(Aktivierbar über Referenz-ERP-Parameter:
      menu=false)
Externes
      Menü
:
In der
      Entwicklung befindendes Haupt-Menü.
Menü-Version
Technische Versions-Nummer des
      verwendeten Menüs.
Programm-Version
Programm-Version der laufenden
      Aeins-Instanz.
Instanz
Identifikation der
      Aeins-Instanz.
Windows-User
Zur
      leichteren Identifikation, wenn z.B. mehrere Verbindungen mit dem gleichen
      Kurznamen da sind.
Funktionen stehen in dieser Version keine zur
Verfügung.

---

## Meldung Meldebestände wurden unterschritten

Meldung Meldebestände wurden unterschritten
Wenn Meldebestände von Artikel unterschritten werden
erscheint beim Start von Referenz-ERP ein Eintrag (Meldebestände wurden
unterschritten) im Hauptmenü unter Favoriten.
Mit einem Doppelklick auf diese
Meldung ruft man einen Report auf, der alle betroffenen Artikel
anzeigt.
Wurde bei einem Artikel sogar der Mindestbestand unterschritten wird
der Ist-Wert im Report rot gedruckt.

---

## Meldungen im Fehlerprotokoll

Meldungen im Fehlerprotokoll
Fehler, die während er Datenübernahme auftreten,
werden ins Fehlerprotokoll geschrieben. Importfehler können am
Fehlerprotokollbereich „DATA_IMPORT“ erkannt werden. Die einzelnen
Fehlermeldungen sind selbsterklärend. Die Fehlerursache wird im Zweifelsfall im
Kontext der Programmablaufbeschreibung erläutert.

---

## Pfad und Name der Protokolldatei

Pfad und Name der Protokolldatei
Geben Sie hier bitte einen gültigen Pfad und
Dateinamen an. Der Pfad muss existieren, die Datei wird, sofern sie noch nicht
vorhanden ist, neu angelegt. In dieser Datei werden sämtliche
Ausnahmesituation  ( Fehlermeldungen / falsche Kontenzuordnungen etc )
sowie jede erfolgreiche Datenerstellung  protokolliert.

---

## Positionen in Zollausfuhr

Positionen in Zollausfuhr
Bei der Registerkarte „Positionen“ handelt es sich um
alle im der Ausfuhranmeldung zugehörigen Lieferschein enthaltenen Positionen,
die keine Leergutartikel sind (Artikelstamm.Artistamtyp ungleich 5).
Hier ist jeder Artikel per Doppelklick einzeln
aufrufbar. Bei betätigen der Taste F5 wird eine Liste aller Positionen erstellt.
Diese Positionen können bis zum Versenden der Ausfuhr verändert werden.
Genaueres zum Verändern der Positionsdaten im Abschnitt „Zollpositionen“.
Parameter
Bedeutung
Artikelnummer
Artikelnummer des geladenen
      Artikels
Artikel
Bezeichnung des Artikels
Packstückart
Kurz-Bezeichnung des
      Packstücks
Bezeichnung Packstück
Bezeichnung des
      Packstücks
Anzahl
Anzahl der Packstücke
Zeichen/Nummern
Beschriftung der
      Packstücke
Gewicht
Gesamtgewicht der Packstücke

---

## Post

Post
Hauptmenü
Büro und Internet
Büroumgebung
Referenz-ERP Post
Direktsprung
[POST]
In Referenz-ERP existiert die Möglichkeit einzelnen oder
allen Benutzern eine Mitteilung zu senden. Sollte der Empfänger der Meldung im
System angemeldet sein, so erhält er eine Mitteilung, dass die Meldung
eingegangen ist. Ist er nicht im System angemeldet, wird ein für ihn sichtbarer
Eintrag in die Favoritenliste gesetzt. Dieser Eintrag wird beim nächsten
Anmelden in Referenz-ERP dargestellt.

---

## Prozedur für Herkunftsbundesland

Prozedur für Herkunftsbundesland
In dieses Feld kann eine private Prozedur eingetragen
werden, welche die Herkunft für die, in einer Ausfuhr enthaltenen, Positionen
vorbelegt. Als Standard wird, über die Funktion Zoll_Herkunftsbundesland.sql,
die beim Anlegen, des zur Ausfuhr zugehörigen Lieferscheins, definierte Herkunft
übernommen.

---

## Prozedur für Intrastat / Zollabwicklung

Prozedur für Intrastat / Zollabwicklung
In dieses Feld kann eine private Prozedur eingetragen
werden, welche Einfluss auf die beiden Felder HerkunftZielLand und
HerkunftZielRegion in der Warenbewegung nimmt. Ist in diesem Feld keine Private
Prozedur eingetragen, so wird die Vorbelegung aus den UFLD Feldern in der
Vorgangserfassung Maske für jede einzelne Warenposition herangezogen. Die
Vorbelegung für das Herkunft Ziel Land und Herkunft Ziel Region wird aus der
Hauptadressen Anschrift des Kunden gezogen. Das Bundesland entspricht der
Herkunft Ziel Region diese gilt aber nur für Deutschland. Das Land des Kunden
entspricht Herkunft Ziel Region. In der Warenposition gibt es die Möglichkeit
die Vorbelegung für die Felder manuell zu überschreiben.
Soll für die Bestimmung von Herkunft Ziel Land und
Herkunft Ziel Region eine private Datenbankprozedur benutzt werden, so müssen
einigen Richtlinien eingehalten werden.
create procedure
p_landregion
(  in
in_ufld_land
integer default 0
,
in
in_ufld_region
integer default
null
,
in
in_wabew_land
integer default 0
,
in
in_wabew_region
integer default
null
,
in
in_ArtikelID
integer
,
in
in_PartieID
integer
,
in
in_KontraktID
integer
,
in
in_Menge
Numeric(15,4)
,
in
in_KundID
integer
,
in
in_LagerNummer
integer
)
RESULT(
"HerkunftZielLand"
integer
,
"HerkunftZielRegion"
integer
)
Begin
declare
dc_HerkunftZieLand
integer
;
declare
dc_HerkunftZielRegion
integer
;
--Bestimmung des
HerkunftZielLand und HerkunftZielRegion
select
dc_HerkunftZieLand
as
HerkunftZielLand, dc_HerkunftZielRegion
as
HerkunftZielRegion
from dummy
;
END

---

## Prozedur für Packstücke

Prozedur für Packstücke
In dieses Feld kann eine private Prozedur eingetragen
werden, welche für alle Positionen einer Ausfuhranmeldung die dazugehörigen
Packstücke definiert. Dieses Feld muss gefüllt werden, da sonst eine
Platzhalterfunktion verwendet wird. Die Vorbelegung durch die
Platzhalterfunktion Zoll_Packstuecke.sql ist also nicht aussagekräftig.

---

## Prozedur für Positionsvermerk

Prozedur für Positionsvermerk
In dieses Feld kann eine private Prozedur eingetragen
werden, welche die Vermerke für die, in einer Ausfuhr enthaltenen, Positionen
vorbelegt. Dieses Feld muss gefüllt werden, da sonst eine Platzhalterfunktion
verwendet wird. Die Vorbelegung durch die Platzhalterfunktion Zoll_Vermerk.sql
ist also nicht aussagekräftig. Als Quelle für den Positionsvermerk kann
beispielsweise die Tabelle WarenbewegungAddon genutzt werden.

---

## Registerkarte Allgemein in Zollausfuhr

Registerkarte Allgemein in Zollausfuhr
Bei der Registerkarte „Allgemein“ handelt es sich um
das Fenster zur Eingabe für die Ausfuhr erforderlichen Grunddaten. Beim ersten
Öffnen können bereits Felder vorbelegt sein. Die Vorbelegung erfolgt durch die
beim Anschriftstamm (Funktion „Zollausfuhrdaten“) vordefinierten Werte für eine
Adresse. Hier sind diese Daten bis zum Zeitpunkt der Versendung der Ausfuhr
änderbar. Wurde die Ausfuhr versendet, werden sämtliche Eingabefelder gesperrt,
um den Zustand bei Versendung beizubehalten.
Parameter
Bedeutung
Anmeldungsart
      Überführung:
Anmeldungsart der Überführung. In
      dieser Version immer festgelegt auf „AM a“ (Vollständige Ausfuhranmeldung
      zum zweistufigen Normalverfahren). Erweiterung bei späteren Versionen
      möglich.
Anmeldungsart Ausfuhr:
Hierbei handelt es sich um die Art
      der Ausfuhr. Unterschieden wird hier zwischen Ausfuhr in Drittland (EX)
      und Ausfuhr in ein EFTA-Land (EU). Dieses Feld wird vorbelegt über den
      Staatstamm. Je nachdem ob es sich bei der Nationalität der Adresse um ein
      Dritt- oder EFTA-Land handelt.
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      Hauptanschrift) des Vorgangs/Kunden
Anmeldezeitpunkt:
Termin zu dem die Ausfuhranmeldung
      angelegt wurde.
Vermerk:
Vermerk zur Ausfuhr. Wird an die
      Zollverwaltung übertragen, hat aber keine direkte zollrechtliche
      Auswirkung.
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      Hauptanschrift) des Vorgangs/Kunden
Beteiligtenkonstellation:
Konstellation aller an der Ausfuhr
      beteiligten Organisationen. In dieser Version immer 0000 (Anmelder ist
      Ausführer, ohne Vertretung). Erweiterung bei späteren Versionen
      möglich.
Sachbearbeiter
Name
      des Sachbearbeiters, der die Ausfuhranmeldung erstellt hat
(aus
      Bedienerstamm des Bedieners)
Anmelder
Anmelder der Ausfuhranmeldung aus

[...]


---

## Registerkarte Export-Adresse in Zollausfuhr

Registerkarte Export-Adresse in Zollausfuhr
Die Registerkarte „
Export-Adresse
“ enthält die
mit den Daten aus der Versandanschrift bzw. Kundenanschrift zum Vorgang
vorbelegten Adressdaten der Lieferung.
Diese sind sollten nur im Ausnahmefall
geändert werden, wenn die Adressdaten im Originalvorgang zum Beispiel Tippfehler
enthalten.

---

## Registerkarte Ladeort-Transp.-Bef.Route in Zollausfuhr

Registerkarte Ladeort-Transp.-Bef.Route in Zollausfuhr
Die Registerkarte „Ladeort/Transp./Bef.Route“ ist für
die Zollausfuhr ebenfalls auszufüllen.
Der Abschnitt „
Ladeort
“ definiert den Ort des
Beladens der zu versendenden Ware sowie die beteiligte Ausfuhrzollstelle und
Ausgangszollstelle.
Diese Angaben sind vorbelegt durch die Angaben im
Lagerstamm des Lagers, aus dem die letzte in der Auswahlliste angeklickte
Position dieser Sammlung geladen wird.
Soll eine alternative Prozedur zur Ermittlung des
Lagers verwendet werden, so kann diese im Einrichterparameter „alternative
Ladeort Vorbelegungs-Prozedur“ hinterlegt werden.
Ein Beispiel für die Prozedur kann sein:
create procedure
mas_test_proc(V_ID
integer
, V_POSIZAEHLER
integer
)
BEGIN
select
'MEINLager'
as
Ladezusatz,
'MeineStrasse 1'
as
AdressStrasse,
'12345'
as
AdressPLZ,
'Meinestadt'
as
AdressOrt,
'DE002101'
as
AusfuhrZollstelle
from DUMMY
END
Auch diese Daten sind bis zum Versenden der Ausfuhr
änderbar.
Parameter
Bedeutung
Bezeichnung / Zusatz
Zusatz zur Angabe des Ortes, an dem
      die Beladung der Ware auf das Transportmittel stattfindet
Straße
Straße des Ortes, an dem die
      Beladung der Ware auf das Transportmittel stattfindet
Ort
Ort,
      an dem die Beladung der Ware auf das Transportmittel
      stattfindet
Postleitzahl
Postleitzahl des Ortes, an dem die
      Beladung der Ware auf das Transportmittel stattfindet
Ausfuhrzollstelle
Deutsche Zollstelle, welche den
      Transport der Ware verwaltet
Ausgangszollstelle
Zollstelle, über welche die Ware die
      EU verlässt
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      Hauptanschrift) des Vorgangs/Kunden
Der Abschnitt „
Transport
“ enthält wichtige
Angaben zum Warentransport.
Parameter
Bedeutung
Verkehrszweig Inland
Verkehrszweig, welcher für den
      Transport der Ware im Inland verwendet wird
Die
      Vorbelegung erfolgt aus den Zolldaten zur Anschrift (Versandanschrift oder
      H
[...]


---

## Report Ladeliste n. Tag

Report Ladeliste n. Tag
Dieser Report zeigt Vorgänge für ausgewählte Touren
an. Dafür ist ein bestimmtes Lieferdatum auszuwählen. In der Bereichsauswahl
kann man außerdem festlegen, ob statt der Artikelbezeichnung der
Warenbewegungstext angezeigt werden soll. In der Standardeinstellung für den
Vorgangstyp werden Lieferscheine angezeigt; dieser kann beliebig mit Hilfe der
F3-Auswahl geändert werden.

---

## SET OUTERR Statement

SET OUTERR
Statement
Syntax
SET OUTERR [Dateiname]
Purpose
Fehlermeldungen umlenken in Datei (append)
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
CONTINUE
,
SET ERROR
Beschreibung
Fehlermeldungen, die während des Laufes einer
Kommandodatei entstehen können in eine Datei umgelenkt werden, um sie
Anschließend zu kontrollieren. Dies ist umso wichtiger, wenn man die
Fehlermeldung auf dem Bildschirm ausgeschaltet hat. Geschlossen wird die
Fehlerdatei wieder, wenn SET OUTERR ohne Dateinamen angegeben wird.
Beispiel
SET ERROR NODISPLAY;
SET OUTERR c:\ERR.TXT;
Select * from
DIESERELATIONEXISTIERTNICHT;
SET ERROR NODISPLAY;
SET OUTERR;

---

## Steuerkonten bebuchen

Steuerkonten bebuchen
In der Belegerfassung der Finanzbuchhaltung ist es
nicht ohne weiteres möglich, Steuerkonten direkt zu bebuchen. Bei der
Einfuhrumsatzsteuer ist es jedoch so, dass ein gesonderter Beleg für die Steuer
eintrifft ohne unmittelbaren Bezug auf die Rechnung. Jetzt darf man auf keinen
Fall auf die Idee kommen, einfach das Kennzeichen für Steuerkonten schnell mal
auf
Nein
zu setzen, das Konto manuell zu bebuchen und es anschließend
wieder zurückzusetzen. Dabei würde die Steuer zwar auf dem richtigen Konto
landen, aber bei den Steuerauswertungen nicht als Steuer interpretiert.
Der richtige Weg führt über die Einrichtung eines
Steuersatzes mit der Steuerformel "100%". Dies sorgt dafür, dass der
gesamte in der Belegerfassung eingegebene Betrag auf dem Steuerkonto landet,
anstatt auf dem Erlöskonto.
Als Erlöskonto sollte man sich ein eigenes Konto
einrichten, bei dem diese Steuerklasse und dieser Steuerschlüssel fest
hinterlegt werden. Beträge werden dort nie landen, wenn es nur für die
Steuerumbuchung verwendet wird. Wenn man nun die Steuer buchen will, gibt man
als Erlöskonto dieses Hilfskonto an. Dann wird der eingerichtete Steuersatz
gezogen und der Betrag landet auf dem Steuerkonto.

---

## Tabelle zur Version: 8.3.2211.9

Tabelle zur Version: 8.3.2211.9
ID
Releasenote - Titel
Geprüft
32856
Großer HTML-Body eBeleg
32967
Bitmapmeldung unterdrücken
32968
Makro-Programme
32781
Archiv: Drag- und Drop, Behandlung Anlagen und Images
      in der Mail
32979
OLAP Funktion entfernt
32958
Automatischer Zahlungsverkehr/ SEPA-Version
32965
Datenübernahme: FiBu-XML-Import
32997
Paginiernummer (Archivreferenz)
33032
DUEB: FiBu-XML-Import
32918
Produktion: Einfügen und entfernen von Zeilen bei
      Komponenten
32927
Druck von Vorgangstexten basierend auf
Dokumenten
32969
Währungskurs-Abruf

---

## Systemmeldungen

Systemmeldungen
Administration
Menü
Systemmeldungen
oder Direktsprung
[
MENU
]
Systemmeldungen sind gemäß folgenden Regeln
aufzubauen. Diese Regeln werden von Referenz-ERP zur Laufzeit geprüft, und die
entsprechenden Systemmeldungen werden dann im
Hauptmenü-Systemmeldebereich
dargestellt.
Die Systemmeldungen sind über
Steuerparameter 893
zu parametrisieren.
Felder
Name
Eindeutiger technischer Name der
      Systemmeldung.
Aktiv
Ja/Nein
Bestimmt ob die Systemmeldung
      überhaupt aktiv sein soll, d.h. ob die Bedingungen für eine Anzeige beim
      Programmstart überhaupt geprüft werden sollen.
Beschriftung
Die
      explizite Beschriftung der Systemmeldung.
Hinweis: Es handelt sich hierbei
      nicht um die Beschriftung der Funktion.
Funktion
Die
      Funktion, die ausgeführt werden soll wenn ein User die Systemmeldung
      klickt.
Sie
      können hier private Funktionen anbinden.
Funktionsart
Informatorisch die
      Funktionsart.
Rolle
Die
      Anzeige der Systemmeldung
und
das Recht der Ausführung der Funktion
      hängt ab vom Rollenkontext der Funktion.
Exklusiv-User
Gemäß Rollenkontext kann es
      Bedienerklassen geben, denen die Systemmeldung vorlegt wird.
      (Rolle)
Durch Angabe eines Kurznamens lässt
      sich die Systemmeldung weiter einschränken. (Es kann auch durch
      komma-getrennte Liste von Kurznamen angegeben werden)
Sortierung
Kriterium für die Reihenfolge der
      Abarbeitung der Systemmeldungen.
Vorlage vorhanden?
Es
      existiert eine Kopiervorlage mit deren Hilfe Sie die Systemmeldung auf
      Standard-Auslieferung zurücksetzen können.
Ein
      „Ja“-Eintrag wird informatorisch
gelb
markiert, wenn sich das
Systemmeldungsstatement
von dem der Vorlage unterscheidet.
Funktionen
Pflege-Funktionen
[
F8
],[
F5
],[
F6
],[
F7
]
Neu,
      Ändern, Ansehen, Löschen
Funktionen ansehen/bearbeiten
      [
F11
]
Ruft
      den Anseh- bzw. Pflegedialog für die angegebene Funktion der Systemmeldung
      direkt auf.
Export
[...]


---

## Systemmeldungen - Vorlage

Systemmeldungen - Vorlage
Administration
Menü
Systemmeldungen (Vorlagen)
oder Direktsprung
[
MENUD
]
Die Systemmeldungs-Vorlagen können für die Erstellung
einer Systemmeldung dienen.
(siehe
Neu aus Vorlage
)
Felder
Name
Eindeutiger technischer Name der
      Systemmeldung.
Auslieferung
Ja/Nein
Kennzeichen, ob die
      Systemmeldungs-Vorlage in der Auslieferung ist.
Beschriftung
Die
      explizite Beschriftung der Systemmeldung.
Hinweis: Es handelt sich hierbei
      nicht um die Beschriftung der Funktion.
Funktion
Die
      Funktion, die ausgeführt werden soll, wenn ein User die Systemmeldung
      klickt.
Funktionsart
Informatorisch die
      Funktionsart.
Statement
Das
      zugrundeliegende Systemmeldungs-Statement.
(siehe auch
Systemmeldungstatement
)
Achtung das tatsächlich gespeicherte
      Statement kann wesentlich länger als die hier angezeigten maximalen 255
      Zeichen sein!
Funktionen
Pflege-Funktionen
[
F8
],[
F5
],[
F6
],[
F7
]
Neu,
      Ändern, Ansehen, Löschen
Außer „Ansehen“ ausschließlich für
      Entwicklung.
Funktionen ansehen/bearbeiten
      [
F11
]
Ruft
      den Anseh- bzw. Pflegedialog für die angegebene Funktion der Systemmeldung
      direkt auf.
Funktion Informationen
      [
F9
]
Ruft
      den Funktions-Informationsdialog für die angegebene Funktion der
      Systemmeldung auf.
Suchen
Name
Name
      like
Funktion
Funktion like
Beschriftung
Beschriftung like
Statement
Statement like
Auslieferung
Ja,Nein;Egal

---

## Tabelle zur Version: 8.3.2210.20

Tabelle zur Version: 8.3.2210.20
ID
Releasenote - Titel
Geprüft
32748
Intrastat Export Anpassung
32752
Nummernkreise/Zählkreise
32786
Staatstamm "Staaten einspielen" entfernt
32787
Makro: Checkbox "Profiler" von Maske entfernt
32798
Branchen-ERP-Etikettendruck Versionserhöhung
32865
Belegmailversand wiederholen
32891
Excelimport [EXCELI]
32797
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
32879
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
32686
eClearing
32842
SEPA Lastschrifteinzug und Skonto
32898
Jahreswechsel bei Wechsel der Forderungsgruppe im
      Kundenstamm
32886
TSE-Ansteuerung
32729
Produktionserfassung: Eingabe Komponentenmenge
32788
Produktion: Produktionserfassung
32813
Kontraktabwahl in der Rohware
32724
Bemerkung für Musterkunden einzeln pflegbar
32795
Pfleger: Artikel & Artikelstamm
32840
Anschrift im Objektstamm
32844
Bemerkung für Musterkunden einzeln pflegbar
32845
Interessent in Kunden umwandeln
32734
Individuelle Preiskonditionen

---

## Technische Information zur Konfiguration des Kassenmakros

Technische Information zur Konfiguration des Kassenmakros
Das Kassenmakro ist für jede Kasse einzeln zu
definieren. Als Beispiel dient AMIC_BZT_MUSTER.
Dort finden Sie auch die Beispiele für die Abmeldung
eines Terminals und die Initiierung des Kassenschnitts.
Erfolgt die Kommunikation mit dem Terminal per LAN, so
wird hier die IP-Adresse angegeben. Diese darf sich beim Terminal nicht per DHCP
ändern.
Bitte kontaktieren Sie hierzu den Administrator des
Netzwerkes bzw. weisen Sie in Absprache mit dem Netzwerkadministrator eine feste
IP-Adresse zu. Die Hilfe dazu bietet die Bedienungsanleitung des jeweiligen
Terminals.
Im Fall von LAN wird ebenso ein Port angegeben. Dieser
ist von Hersteller zu Hersteller unterschiedlich. Im Protokoll ist der Port
20007 vorgesehen, der Hersteller Thales z.B. verwendet nach eigenen Angaben
jedoch 22000, Ingenico den Port 5577.
Hinweis:
Einige Terminals weisen der Erfahrung nach zuweilen
Kommunikationsprobleme zu Referenz-ERP auf. Dadurch kann es vorkommen, dass Referenz-ERP auf
Rückmeldungen vom Terminal erwartet, jedoch nicht bekommt. In diesem Fall würde
Referenz-ERP dauerhaft warten. Um diesen Wartemodus abbrechen zu können, muss der
Parameter „SHOWABORT“ auf TRUE gesetzt werden.
Der Parameter Terminalname wurde ersetzt durch den
Parameter Authentifizierung:
Parameter AUTHENTIFIZIERUNG: TRUE / FALSE Standard:
TRUE.
Legt fest, ob das Terminal LogOn beim Start benötigt.
THALES_0001 entspricht TRUE / INGENICO_0001 entspricht FALSE
Weitere Einstellungen finden Sie unter
Technisches
Umfeld

---

## Umsatzsteuervoranmeldungsformular

Umsatzsteuervoranmeldungsformular
Dieses Formular ist das Vordruckformular von Elster
und unterscheidet sich im Kopf von dem von Referenz-ERP verwendeten Report.
Seite 1
Seite 2

---

## Unerwartetes Verhalten beim Beleg-Mailversand

Unerwartetes Verhalten beim Beleg-Mailversand
Die Rückmeldungen des Empfängermailservers über die
Unzustellbarkeit einer Mail muss ebenso wie die Bearbeitung der Einträge im
Fehlerprotokoll durch betriebsinterne Abläufe sichergestellt werden. Der Beleg
gilt als gedruckt, wenn er an das Mailsystem abgegeben wurde.
•
Ist die Mailadresse des Rechnungsempfängers nicht im Anschriftenstamm
eingetragen, so wird ein Eintrag ins Fehlerprotokoll geschrieben. Das
Druckkennzeichen wird dennoch gesetzt, das Mailkennzeichen wird nicht
gesetzt.
•
Ist die Mailadresse des Rechnungsempfängers ungültig oder die Mail nicht
zustellbar, so gilt die Rechnung als versandt. Eine Verarbeitung einer
Rückmeldung vom Mailserver findet an dieser Stelle nicht statt. Der Mailserver
wird jedoch an die Absender-Mailadresse eine Unzustellbarkeitsmitteilung geben,
der dann nachgegangen werden muss.

---

## Unzustellbare E-Mails

Unzustellbare E-Mails
Die Rückmeldungen des Empfängermailservers über die
Unzustellbarkeit einer Mail muss ebenso wie die Bearbeitung der Einträge im
Fehlerprotokoll durch betriebsinterne Abläufe sichergestellt werden. Der Beleg
gilt als versendet, wenn er erfolgreich an das Mailsystem abgegeben wurde.

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
Vorzeichen Eigenware
      Voreinkauf
wbc_SigniFremdware_EINL
Numeric(15,4)
Vorzeichen Fremdware
      Einlagerung
wbc_SigniFremdlager_KOM
Numeric(15,4)
Vorzeichen Fremdlager
      Kommission
wbc_SigniEigenBestand
Numeric(15,4)
Vorzeichen Eigenbestand
wbc_SigniLagerBestand
Numeric(15,4)
Vorzeichen Lagerbestand
wbc_SigniEinkauf
Numeric(15,4)
Vorzeichen Einkauf
wbc_SigniVerkauf
Numeric(15,4)
Vorzeichen Verkauf
wbc_Eigenware
Numeric(15,4)
Menge Eigenware
wbc_Fremdware_VVK
Numeric(15,4)
Menge Vorverkauf
wbc_Fremdlager_VEK
Numeric(15,4)
Menge Voreinkauf
wbc_Fremdware_EINL
Numeric(15,4)
Menge Einlagerung
wbc_Fremdlager_KOM
Numeric(15,4)
Menge Kommission
wbc_EigenBestand
Numeric(15,4)
Menge Eigenbestand
wbc_LagerBestand
Numeric(15,4)
Menge Lagerbestand
wbc_Einkauf
Numeric(15,4)
Menge Einkauf
wbc_Verkauf
Numeric(15,4)
Menge Verkauf
wbc_Eigenware_Wert
Numeric(15,4)
Wert
      Eigenware
wbc_Fremdware_VVK_Wert
Numeric(15,4)
Wert
      Vorverkauf
wbc_Fremdlager_VEK_Wert
Numeric(15,4)
Wert

[...]


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

## ZMDO / Zusammenfassende Meldung via ELSTER

ZMDO / Zusammenfassende Meldung
via ELSTER
Wichtiger Hinweis zur Datenschutz-Grundverortung:
ELSTER schreibt
vor, dass vor dem Versand der Daten die Informationen zur
Datenschutz-Grundverordnung
einmal akzeptiert werden. Um dies zu gewährleisten,
wird jeder ELSTER-Anwender vor dem Versand einer Umsatzsteuervoranmeldung oder
der Zusammenfassenden Meldung einmal aufgefordert aktiv zu bestätigen, dass er
die Datenschutzgrundverordnung gelesen und akzeptiert hat.
Seit Mai 2012 bietet Elster die Möglichkeit die ZMDO
(Zusammenfassende Meldung Daten Online) auf elektronischen Weg ohne den Umweg
über das ELSTER-ONLINE Portal zu machen. Diese Möglichkeit ist ab Version 8.1
auch in Referenz-ERP integriert.
Mindestsystemanforderungen
Diese Anforderungen werden von dem Programm-Modul der
bayerischen Steuerverwaltung gestellt und können von Branchen-ERP nicht beeinflusst
werden.
•
Betriebssystem
Windows 8 oder Windows 10
•
Internetzugang
Via Modem, ISDN, DSL etc.
•
Software
PDF-Reader mind. Adobe Acrobat Reader 5.x oder
      vergleichbar für verschlüsselte PDFs

---

## Zollabwicklung löschen

Zollabwicklung löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
VorgangPosi
VorgangPack
VorgangAusfuhrMessage

---

## Zoll

Zoll
Datenbankfunktionen für die Bestimmung einer
eindeutigen Ausfuhranmeldung

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

## Zollstatus prüfen

Zollstatus prüfen
Wurde eine Zollanmeldung erfolgreich versendet, so
wird sie irgendwann vom Zoll bearbeitet worden sein. Sie können manuell den
Status dieser Anmeldung beim Datendienstleister anfragen.
Dazu wählen Sie die von Ihnen bearbeitete
Zollanmeldung aus der Auswahlliste in der Anwendung Zoll-Lieferscheine mit dem
Direktsprung [LIZO] mit dem Status „versendet“ aus und wählen die Funktion
„Zollstatus prüfen“.
Diese Prüfung kann auch periodisch durch ein sog.
Event erfolgen. Mehr dazu im Abschnitt Automatische Prüfung und Abholung.
Mögliche weitere Status sind:
•
nicht genehmigt
•
ABD bereitgestellt
•
ABD abgeholt
•
AgV bereitgestellt
•
AgV abgeholt
Zur Statusprüfung wird die Prozedur
AMIC_STATUS_FUNKTION aufgerufen. Die Prozedur erstellt das für den Webservice
notwendige XML und sendet es über die Prozedur
getAtlasExportTransaction
an den an den AEB-Webservice. Die Rückmeldung wird verarbeitet,
Status-Informationen gesetzt und Meldungen zusammengestellt. (Näheres siehe
Dokumentation zur Datenbankprozedur.)

---

## Zusammenfassende Meldung

Zusammenfassende Meldung
Zum 1. Januar 2010 ergibt sich eine erweiterte
Erklärungspflicht für die Zusammenfassende Meldung (ZM). Künftig sind neben den
innergemeinschaftlichen Lieferungen auch die innergemeinschaftlichen Leistungen
in der vierteljährlich abzugebenden ZM anzugeben. Für die Zusammenfassende
Meldung wird nur noch die Variante "
Zusammenfassende Meldung nach AWPosition"
unterstützt.
Achtung:
Seit dem 01.01.2007 ist die Zusammenfassende
Meldung a
uf elektronischem
Weg nach Maßgabe der Steuerdaten-Übermittlungs-Verordnung  zu
übermitteln
. Siehe dazu weiter unten unter Zusammenfassende
Meldung Excel Export
Innergemeinschaftliche Lieferungen (Zeile 21,
Kennziffer 41 der Umsatzsteuervoranmeldung) sind z.Zt. je Quartal in Form der
Zusammenfassenden Meldung aufzuführen.
Wer muss eine Zusammenfassende Meldung
abgeben?
Meldepflichtig sind alle Unternehmer, die Steuerfreie
innergemeinschaftliche Warenlieferungen oder innergemeinschaftliche
Warenbewegungen durchgeführt haben. Führen pauschalierende Land- bzw. Forstwirte
innergemeinschaftliche Warenlieferungen aus, so müssen sie ebenfalls eine
Zusammenfassende Meldung abgeben, obwohl diese Umsätze nicht steuerfrei
sind.
Was ist zu melden?
Innergemeinschaftliche Warenlieferungen(§18a
Abs. 4 Satz 1 Nr. 1 und 2 UStG)
a )
Innergemeinschaftliche
Lieferungen im Sinne §6a Abs. 1UStG mit Ausnahme neuer Fahrzeuge an Abnehmer
ohne USt-IdNr.
b )
Innergemeinschaftliche Lieferungen gleichgestellter
Verbringungen i.S.d. § 3 Abs. 1a i.V.m. § 6a Abs. 2 UStG..
Maßgeblich ist
stets die umsatzsteuerliche Beurteilung des Vorgangs.
Innergemeinschaftliche Sonstige Leistungen(§18a
Abs. 4 Satz 1 Nr. 3 UStG)
Innergemeinschaftliche sonstige Leistungen sind nach §
3a Abs. 2 UStG im übrigen Gemeinschaftsgebiet ausgeführte steuerpflichtige
sonstige Leistungen, für die der in einem anderen Mitgliedstaat ansässige
Leistungsempfänger die Steuer dort schuldet,
Lieferungen im Rahmen von innergemeinschaftlichen
Dreiecksges
[...]


---

## Zusammenfassende Meldung Excel Export

Zusammenfassende Meldung Excel Export
Hauptmenü
Abschlussarbeiten
Zusammenfassende Meldung
Variante ZM nach AW.Position
Direktsprung
[UVZM]
Unternehmer, die steuerfreie innergemeinschaftliche
Warenlieferungen und/oder Lieferungen i.S.d. § 25b Abs. 2 Umsatzsteuergesetz
(UStG) im Rahmen von innergemeinschaftlichen Dreiecksgeschäften ausgeführt
haben, sind seit dem 01.07.2010 verpflichtet die Zusammenfassende Meldung (ZM)
um 25. Tage nach Ablauf jedes Meldezeitraums beim BZSt, Dienstsitz Saarlouis,
auf elektronischem Weg nach Maßgabe der Steuerdaten-Übermittlungs-Verordnung
( StDÜV) zu übermitteln
(§ 18a Abs. 1 Satz 1 UStG).
Für die elektronische Übermittlung
einer
ZM (bis
1000
Meldezeilen
) steht Ihnen der sichere Zugang "Elster-Online-Portal" mit
Authentifizierung, oder alternativ der "freie Zugang" über den Formularserver
der Bundesfinanzverwaltung zur Verfügung
Referenz-ERP stellt diese Daten der ZM (Meldezeilen auf
Seite 2) als
MS-Excel-Tabelle
zur Verfügung. Diese kann dann anschließend mit einem vom BZSt kostenlos zur
Verfügung gestellten Makro in das erforderliche XML-Format konvertiert werden.
In Referenz-ERP gibt es unter dem Menü Umsatzsteuer die
Anwendung "Zusammenfassende Meldung". Dort kann man zur Variante
"Zusammenfassende Meldung nach AWPosition" eine Funktion "Übergabe Excel"
finden. Bevor die Daten Exportiert und in eine Excel-Datei auf dem
Unterverzeichnis „..\Export\Zusammenfassende Meldung“ geschrieben werden, werden
vom System einige Prüfungen durchgeführt, ob bestimmte Zuordnungen und
Einrichtungen fehlerfrei sind. Diese Prüfungen können Sie auch schon bei der
Einrichtung der Stammdaten durchführen. Sie finden diese Tests unter dem
Direktsprung FIREO und dort ist es der Menüpunkt "Test Stammdaten".
Die so erstellte Datei kann dann mit dem Makro der
BfinV weiterverarbeitet werden. Die Voraussetzungen für den Import von XML-Daten
in das Online-Formular auf dem Formularserver sowie Details zum Procedere und
das für die Datenerfassung in MS
[...]


---

## Zusammenfassende Meldung über zugelassenen Vordruck

Zusammenfassende Meldung über
zugelassenen Vordruck
Achtung:
Seit dem 01.01.2007 ist die Zusammenfassende
Meldung a
uf elektronischem
Weg nach Maßgabe der Steuerdaten-Übermittlungs-Verordnung  zu
übermitteln
. Siehe dazu weiter unten unter
„
Zusammenfassende Meldung Excel
Export
“.
In Referenz-ERP kann die Zusammenfassende Meldung über ein
vom Bundesamt für Finanzen zugelassenes Formular ausgedruckt werden. Zwar wird
im Zulassungsbescheid darauf hingewiesen, dass Unternehmer, die ein von Dritten
erstelltes Verfahren zur Erstellung ihrer Zusammenfassenden Meldung verwenden,
dies erneut beim Bundesamt für Finanzen zulassen müssen. Auf den Ausdruck der
Daten der Zulassung auf dem Vordruck kann jedoch verzichtet werden, wenn im
Zusammenhang darauf hingewiesen wird, dass die abweichenden Vordrucke mit der
von der Software Company Branchen-ERP GmbH hergestellten Software erstellt werden. Die
Einsendung der ZM mit einem bereits zugelassenen abweichenden Vordruck gilt
bereits als Antrag.
Der Zulassungsvermerk (Software Company Branchen-ERP GmbH –
BfF vom 31. Okt. 2003, S 7427 a – St l 322 – SW/258) wird auf der
Zusammenfassenden Meldung immer mit ausgedruckt.
Dieses Formular bezieht die Daten über die
Steuersätze und die dort eingerichteten Auswertungspositionen. Für die
Zusammenfassende Meldung werden die Steuersätze herangezogen, für die die
Auswertungspositionen mit den Kennzahlen für "Innergemeinschaftliche Lieferung
"(bisher 41) bzw. "Lieferungen des ersten Abnehmers bei innergemeinschaftlichen
Dreiecksgeschäften" (bisher 42) und – seit Januar 2010 – „„Nicht
steuerbare sonstige Leistungen gem. § 18b Satz 1 Nr.  2 UStG“ ( 21 )
eingetragen sind. Diese Kennzahlen werden in der zugrundeliegenden Auswahl
abgefragt.
Bevor dieses Formular gedruckt wird, werden vom System
einige Prüfungen durchgeführt, ob bestimmte Zuordnungen und Einrichtungen
fehlerfrei sind. Diese Prüfungen können Sie auch schon bei der Einrichtung der
Stammdaten durchführen. Sie finden diese Tests un
[...]


---

## Zusatzinfo

Zusatzinfo
Das Feld Zusatzinfo kann mit einer ITEM-BOX belegt
werden (EPA), der Inhalt des Feldes wird in der Warenbewegung im Zusatzfeld1
gespeichert.

---

