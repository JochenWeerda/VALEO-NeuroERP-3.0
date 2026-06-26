# Kontrakt & Rohware — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (399 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Kontrakt

Kontrakt
Auf diesem Tabs werden gezielt Änderungen eines
Attributs von Datensätzen in Relationen gesucht, die einem bestimmten
Kontraktstamm zuzuordnen sind. Die Angaben in den Feldern
Kontraktnummer
und
KtrId
sind optional, es muss aber mindestens zu einem dieser
Felder eine Eingabe erfolgen. Alle genannten Eingabefelder verfügen über eine
unterstützende Itembox-Anbindung.
Wird lediglich die  Kontraktnummer angegeben, so
ist die Basis für kundenstammbasierte Suchanfragen die Menge aller
Kontraktstammeinträge mit dieser Kontraktnummer, also auch diejenigen mit
eingetragenem Löschkennzeichen.
Wird ein Kontraktstamm per KtrId spezifiziert, so ist
die Basis für kontraktstammbasierte Suchanfragen nur der angegebene
Kontraktstammeintrag.
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
Erreichen der Maximalzahl der Ergebnissätze ab.
Mit der Funktion
Anfrage starten
wir die
Anfrage generiert und zur Abarbeitung an eine entfernte Prozedur übergeben.
Die Maske wird nach Ende der Bearbeitung durch den
Fremdserver automatisch verlassen und das Ergebnis in der Auswahlliste
dargestellt. Werden keine Daten angezeigt, so konnten keine
Logfile-Einträge  entsprechend der gemachten Angaben gefunden werden.

---

## Import und Export der Rohware-Einrichtung

Import und Export der Rohware-Einrichtung
Das mit dem Direktsprung [ROHIE] erreichbare
Programm-Modul zum Import bzw. Export der gesamten Rohwaren-Einrichtung wurde
nun entfernt.
Releasenote Kategorie:
Ticket: 712422[32610]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: ROHIE
Variante: -
Funktion/Report: alle
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 32610, 712422

---

## Kontraktabwahl in der Rohware

Kontraktabwahl in der Rohware
Die Funktion Kontrakt abwählen ist jetzt im jeden Fall
verfügbar, wenn ein Kontrakt ausgewählt wurde.
Releasenote Kategorie:
Ticket: 712846[32813]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [RWB] und [RWBV]
Variante: Variante Rohwarenanlieferung Einkauf und
Variante Rohwarenanlieferung Verkauf
Funktion/Report: .
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32813, 712846

---

## Vorzeichenabhängige Mengendarstellung in der Kontraktauswahlliste

Vorzeichenabhängige Mengendarstellung in der Kontraktauswahlliste
In der Auswahllistenvariante 'Kontrakte'
der Anwendung Kontrakte [KTR] wurde bei der Darstellung der ratierlichen
Werte von Mengen, Restmengen und kumulierten Restmengen die Einstellung des
Kriteriums 'Menge mit Vorzeichen' = 'Ja'  der Bereichsauswahl nicht korrekt
berücksichtigt.  Dieser Umstand wurde nun behoben.  Zudem kam es bei
Kontrakten mit einer anderen Standardkontraktvariante als "Monatl. lin. Abnahme"
zu Unstimmigkeiten bei der Zuordnung von Liefermengen zu den einzelnen
ratierlichen Monaten, da in allen Fällen der Beginn des Kontraktzeitraums zur
Monatszuordnung verwendet wurde. Dieses Verfahren wird jetzt nur noch bei
vorliegen der Standardkontraktvariante "Monatl. lin. Abnahme" genutzt.
In allen anderen Fällen wird das Bewegungsdatum der Lieferung
verwendet.
Releasenote Kategorie:
Ticket: 716987[33201]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Kontrakte [KTR]
Variante: Kontrakte
Funktion/Report: Auswahlliste
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.22, 33201, 716987

---

## Filter in Kontraktauswahlliste

Filter in Kontraktauswahlliste
Der Filterbereich der Kontrakte wurde angepasst. Statt
des Standardlagers, das ohnehin per SPA eingerichtet wird, wird nun der Filter
des Artikellagers angeboten.
Releasenote Kategorie:
Ticket: 717055[33215]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Kontrakt
Variante: Kontrakte
Funktion/Report: Bereich
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33215, 717055

---

## Lagerspezifischer Kontraktartikel

Lagerspezifischer Kontraktartikel
Wird im Kontraktartikel der EPA "Soll das
lagerspezifische Kennzeichen in Kontrakt übernommen werden?" auf "Nein" gesetzt,
so wird auch die Checkbox "lagerspezifisch" nicht mehr angezeigt.
Releasenote Kategorie:
Ticket: 717055[33216]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Kontrakt
Variante: -
Funktion/Report: Artikel
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33216, 717055

---

## Kontrakt

Kontrakt
Die Datumsfelder für die Kontraktgültigkeit waren nach
einer Änderung der Maske zu hoch auf der Registerkarte Konditionen dargestellt
worden (falls dies im EPA so eingerichtet ist). Dies wurde korrigiert.
Releasenote Kategorie:
Ticket: 717055[33217]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Kontraktstamm
Variante: Konrakte
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33217, 717055

---

## Rohware: Behandlung bei Storno mit Kopie

Rohware: Behandlung bei Storno mit Kopie
Für die Funktion Storno mit Kopie von Rohwarebelegen
gibt es den neuen Rohwareparameter 191 "Massebilanz bei Storno mit Kopie".
Dieser ermöglicht, dass bei der Erzeugung von Stornobelegen mit Kopien die
Bewegungen der Originalbelege, die noch keiner festgeschriebenen Massebilanz
zugeordnet worden sind, dennoch bis einschließlich Originalbeleg in der
Massebilanz berücksichtigt werden.  Die zugehörigen Bewegungen des
Stornobelegs und der Belegkopie sowie deren Folgebelege werden in dem Fall nicht
mehr in Massebilanzen berücksichtigt. Näheres dazu ist der Hilfe zu
entnehmen.
Releasenote Kategorie:
Ticket: 707504[33418]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Rohwaren Anlieferung Einkauf,
Rohwarenlieferung Verkauf
Variante: Rohwaren Anlieferung Einkauf,
Rohwarenlieferung Verkauf,  Bearbeiten Sammeldruck Einkauf/Verkauf
Funktion/Report: Abr. Stornobeleg, Sammel-Storno
erstellen
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33418, 707504

---

## Rohware Manuelle Werte

Rohware Manuelle Werte
Es gibt zwei neue Rohwareparameter in [RWPA]:
"Qualitätsergebnis bearbeitbar" mit der Nummer 192 und "Kostenergebnis
bearbeitbar" mit der Nummer 193. Diese Rohwareparameter können global, für
Rohwaregruppen und Abrechnungsschemata mit dem Wert Ja eingestellt werden, wenn
Abrechnungswerte einzelner Qualitäts- oder Kostenzeilen manuell geändert werden
dürfen. Der Standardwert ist Nein. Die Rohwarebearbeitungsmaske wurde
diesbezüglich um 3 weitere Spalten ergänzt.  Manueller Wert in einem Feld
kann zurückgesetzt werden, indem das entsprechende Eingabefeld geleert wird und
mit Return bestätigt wird. Eine Änderung von Analysewert oder Basiswerten
bewirkt auch eine Neuberechnung und damit ein Zurücksetzung auf den
ursprünglichen, nicht manuellen Wert. Dieses gilt auch für die
Rohwarestapelkorrektur. Nähere Informationen sind der Hilfe zu entnehmen.
Releasenote Kategorie:
Ticket: 714243[33525]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: [RWB], [RWBV]
Variante: Rohware Anlieferung Einkauf,
Rohwarestapelkorrektur Einkauf, Rohwarenlieferung Verkauf,
Rohwarestapelkorrektur Verkauf
Funktion/Report: F8, F5
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33525, 714243

---

## Massebilanz

Massebilanz
Es wurden Änderungen im Bereich der Massebilanz
umgesetzt. In einer Rohwarekette (Lieferschein -> Abschlag ->
Folgeabschlag -> Finale) werden nur noch die Bewegungen des letzten
massebilanzrelevanten Belegs in der Auswahlliste Bewegungsübersicht und
Massebilanzbewegungen angezeigt. Nach dem Festschreiben einer Massebilanz lassen
sich die dazugehörigen Bewegungen nicht mehr bearbeiten. Eine Ausnahme davon ist
die Funktion Storno mit Kopie und Sammel-Storno erstellen mit Kopie von
Rohwarebelegen. Die dadurch entstehenden Bewegungen werden wie auch durch
Weiterverarbeitung entstehende Bewegungen nicht mehr in Massebilanzen
berücksichtigt.
Releasenote Kategorie:
Ticket: 708147[33489]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Nachhaltigkeit
Variante: Bewegungsübersicht, Massebilanz,
Massebilanzbewegungen
Funktion/Report: Massebilanz ändern, Massebilanz THG
Änderung, Massebilanz Kompakt Report, Massebilanz Detail Report
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33489, 708147

---

## Rohwarenbelege in der Streckendisposition

Rohwarenbelege in der Streckendisposition
In der Streckendisposition [DISPV] war es möglich,
einen Rohwarenvorgang, der sich bereits in einem Sammelbeleg befand, zu
bearbeiten. Dies ist nicht zulässig und wird künftig verhindert.
Releasenote Kategorie:
Ticket: 721020[33579]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Rohwarebearbeitung [DISPV]
Variante: alle
Funktion/Report: Korrektur per
Rohware-Vorgangshelper
Weitere
Informationen
Tags:
Releasenote, 8.3.2303.31, 33579, 721020

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

## Rohware manuelle Werte. Preisberechnung bei abweichender Mengeneinheit

Rohware manuelle Werte. Preisberechnung bei abweichender Mengeneinheit
Bei einer Rohwareeinrichtung, bei der die
Mengeneinheit einer Kosteneinrichtung von der Mengeneinheit der Ware abweicht,
wurde fälschlicherweise die Mengeneinheit der Ware für die Kosten benutzt.
Dieses wurde korrigiert. Belege mit falschen Preisen können korrigiert werden
durch manuelle Eingabe des Betrags. Dadurch wird der falsche Preis neu und
korrekt berechnet und der eigens bestimmte manuelle Betrag bleibt bestehen.
Releasenote Kategorie:
Ticket: 724088[33885]
Version: 8.3.2306.9
Datum: 09.06.2023
Anwendung: [RWB], [RWBV],[WABD]
Variante: Rohwaren Anlieferung Einkauf,
Rohwarenlieferungen Verkauf, Warenbuch-Details f. Artikel
Funktion/Report: F8, F5
Weitere
Informationen
Tags:
Releasenote, 8.3.2306.9, 33885, 724088

---

## Kontraktstamm: Feld "Standardkontraktvariante"

Kontraktstamm: Feld "Standardkontraktvariante"
Bei einzeln oder mehrfach markierten Kontrakten ist
das Feld Standardkontraktvariante immer gegen Änderung geschützt.
Releasenote Kategorie:
Ticket: 724465[34005]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Kontraktstamm [KTR]
Variante: Kontrakte
Funktion/Report: F5
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34005, 724465

---

## Ref2 und Ref3 bei Rohwaredefinitionen

Ref2 und Ref3 bei Rohwaredefinitionen
Bei der Bearbeitung von Rohwareabrechnungs-Schemata
werden jetzt die Werte der Spalten "Ref 2" und "Ref 3" auch auf den Detailmasken
(Hauptartikelposition, Sekundärartikelposition, Kosten-/Vergütungsposition und
Qualitätsmerkmal) dargestellt.
Releasenote Kategorie:
Ticket: 725440[34048]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [RWG]
Variante: Rohwareguppen nach Bezeichnung,
Rohwaregruppen nach Nummern
Funktion/Report: F2
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34048, 725440

---

## Ertragsschätzung in der Feldbearbeitung

Ertragsschätzung in der Feldbearbeitung
Für Saatsorten und Feldbearbeitung wurde ein Feld für
die Ertragsschätzung (Datenbankfeldname "Ernteschaetzung") angelegt. Der Wert
aus den Saatsorten wird bei der Auswahl der Saatsorte in der Feldbearbeitung als
Vorbelegung herangezogen.
Releasenote Kategorie:
Ticket: 724716[34050]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: SAATS, SAATV
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34050, 724716

---

## Nachhaltigkeitsvorbelegung

Nachhaltigkeitsvorbelegung
Die Vorbelegung des Status auf der Warenpositionsmaske
auf dem Tabreiter Nachhaltigkeit ist immer mit "Nicht Nachhaltig" vorbelegt,
wenn der Kunde kein gültiges Nachhaltigkeitszertifikat für den Artikel besitzt.
Wenn ein Kontrakt nachhaltig ist, obwohl der Kunde des Kontraktes kein gültiges
Nachhaltigkeitszertifikat besitzt, wird bei der Kontraktauswahl auf der
Warenpositionsmaske der Kontrakt automatisch abgewählt und es wird angezeigt für
welchen Kunde und Artikel ein Zertifikat fehlt.  Manuell können auf dem
Nachhaltigkeitstabreiter trotzdem der Status auf Nachhaltig geändert werden.
Mittels F3 kann das Anbauland im Vorgang geändert werden und es werden die dazu
gehörigen THG-Werte gezogen und es wird angezeigt, woher diese kommen.
Außerdem können auf der Kundenmaske auf dem Tabreiter Zertifikate im Grid für
die Nachhaltigkeit in der Artikelstammspalte nur noch nachhaltige Artikel
eingetragen werden.  Artikel bekommt man nachhaltig, wenn man unter [ARS]
Auf dem Tabreiter Konstanten im Nachhaltigkeitsartikel Ja stehen hat.
Releasenote Kategorie:
Ticket: 720760[33582]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Vorgangswesen
Variante: -
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 33582, 720760

---

## Zinsabrechnung drucken

Zinsabrechnung drucken
Um auch Zinsabrechnungen ohne Positionen ausdrucken zu
können, reicht es jetzt nur den Bereich 605 (Zeilentyp) mit mindestens einem
Feld einzurichten.Außerdem wurde das Vorlageformular "-1016 Zinsabrechnung"
angepasst.
Releasenote Kategorie:
Ticket: 730163[34652]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: ZIB
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34652, 730163

---

## Belegdatum bei der Erzeugung von Rohware-Stornobelegen

Belegdatum bei der Erzeugung von Rohware-Stornobelegen
Die Erstellung von Rohwarestornoabrechnungen und
Rohwaresammelstornoabrechnungen können jetzt nicht mehr mit einem Belegdatum
erfolgen, das in einem anderen Geschäftsjahr als das Belegdatum des
Originalbelegs liegt. Wird die Funktion jedoch in der Variante Stornobeleg mit
Erzeugung einer Kopie des Originalbelegs ausgeführt, kann dieses auch mit einem
Belegdatum und Periode aus einem anderen Geschäftsjahr erfolgen, damit eine
ordnungsgemäße jahresübergreifende Abrechnung realisiert werden kann.
Releasenote Kategorie:
Ticket: 730993[34730]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: RWB, RWBV
Variante: alle
Funktion/Report: Abr.Stornobeleg, Sammel-Storno
erstellen
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 34730, 730993

---

## Maintenance

Maintenance
Auf der Kontraktstammmaske auf dem Reiter Konstanten
wurde die F3-Auswahl für das Feld "Herkunfts/Ziel Land"
"IB_StaatStammIntra(Inland + Europa)" durch "IB_STAATSTAMMBEZEICH(alle Staaten)"
ersetzt, damit alle Staaten ausgewählt werden können.
Releasenote Kategorie:
Ticket: 731036[34733]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: [KTR] Kontrakte
Variante: Kontrakte
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 34733, 731036

---

## Zinsabrechnung drucken

Zinsabrechnung drucken
Der Formulardruck für die Zinsabrechnung wurde um den
Druckbereich Seitenfuß erweitert. Insbesondere bei mehrseitigen Zinsabrechnungen
sollte dieser Fuß eingerichtet werden, um die Druckseite optimal
auszunutzen.
Releasenote Kategorie:
Ticket: 731867[34861]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: ZIB
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34861, 731867

---

## Nachhaltigkeitswerte auf Rohwarebelegen, die nicht mehr massebilanzwirksam sind, können nicht mehr verändert werden

Nachhaltigkeitswerte auf Rohwarebelegen, die nicht mehr massebilanzwirksam
sind, können nicht mehr verändert werden
Wenn ein Rohwarebeleg durch "Storno mit Kopie" kopiert
wird, enthält diese Kopie die gleichen Nachhaltigkeitswerte wie der
Originalbeleg. Dies bedeutet nicht, dass diese THG-Werte bei Jahreswechsel oder
einer erneuten Massebilanz auftauchen.  Erläuterung: Rohwarebelege in
festgeschriebenen Massebilanzen erhalten den Wert "1" im Feld
"NachmassebilanzFest" Wenn aus solchen Belegen durch "Storno mit
Kopie" Kopien entstehen, wird hier der Wert "2" im Feld
"NachmassebilanzFest" festgehalten   Dieser Wert sorgt dafür, dass
diese Belege nicht mehr massebilanzwirksam sind und sein können.
Damit dies eindeutig und verständlicher ist, werden in solchen Rohwarebelegen
auf der Rohwaremaske, alle Nachhaltigkeitsfelder weggeschützt. Rohwarebelege
deren Nachhaltigkeitsfelder nicht mehr bearbeitet werden können, sind
somit nicht mehr massebilanzwirksam!
Releasenote Kategorie:
Ticket: 730993[35315]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: [RWB], [RWBV]
Variante: Rohwaren Anlieferung Einkauf,
Rohwarenanlieferung Verkauf
Funktion/Report: Abr. Stornobeleg, F5
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35315, 730993

---

## Belegdatum bei der Erzeugung von Rohware-Stornobelegen

Belegdatum bei der Erzeugung von Rohware-Stornobelegen
Die Erstellung von Rohwaresammeldruck-Belegen,
Rohwarestornoabrechnungen und Rohwaresammelstornoabrechnungen können jetzt nicht
mehr mit einem Belegdatum erfolgen, das in einem anderen Geschäftsjahr als das
Belegdatum des Originalbelegs liegt. Wird die Storno-Funktion jedoch in der
Variante Stornobeleg mit Erzeugung einer Kopie des Originalbelegs ausgeführt,
kann dieses auch mit einem Belegdatum und Periode aus einem anderen
Geschäftsjahr erfolgen, damit eine ordnungsgemäße jahresübergreifende Abrechnung
realisiert werden kann.
Releasenote Kategorie:
Ticket: 730993[35447]
Version: 9.0.2402.2
Datum: 22.10.2024
Anwendung: RWB, RWBV
Variante: alle
Funktion/Report: Abr.Stornobeleg, Sammel-Storno
erstellen
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.2, 35447, 730993

---

## Kontraktstamm Länge des Eingabefeldes Hauptkunde

Kontraktstamm Länge des Eingabefeldes Hauptkunde
Man kann bei der Kontrakterfassung im Feld
Hauptkunde jetzt mehr als 8 Zeichen eingeben um besser nach der Bezeichnung
suchen zu können.
Releasenote Kategorie:
Ticket: 737951[35627]
Version: 9.0.2402.2
Datum: 22.10.2024
Anwendung: KTR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.2, 35627, 737951

---

## Kontraktmengenzeitraum

Kontraktmengenzeitraum
Die Maske "Kontraktmengenzeitraum" konnte nicht mehr
geöffnet werden. Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 737982[35765]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Kontraktstamm [KTR]
Variante: --
Funktion/Report: F5 Ändern -- Mengenzeiträume
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35765, 737982

---

## Mailversand Zinsabrechnung

Mailversand Zinsabrechnung
Alternativ zum Formular für den Mailbody kann in den
Zinsgruppen auch ein Datenbankfunktion hinterlegt werden
Releasenote Kategorie:
Ticket: 735345[35789]
Version: 9.0.2501.5
Datum:
Anwendung: ZIG
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35789, 735345

---

## Rohwaresammeldruck-Mailversand

Rohwaresammeldruck-Mailversand
Die Einstellungen für den
Rohwaresammeldruck-Mailversand können nun unter  [VRGD] in jeder beliebigen
Zeile vorgenommen werden. Vorher war dies nur in der ersten Zeile
möglich.
Releasenote Kategorie:
Ticket: 747598[35856]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: EK-Rohwarenbearbeitung [RWB],
VK-Rohwarenbearbeitung [RWBV]
Variante: Sammelerstdruck Einkauf, Sammelerstdruck
Verkauf
Funktion/Report: Sammel-Erstdruck
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 35856, 747598

---

## Kontraktabwahl bei Nachhaltigkeit im Verkauf

Kontraktabwahl bei Nachhaltigkeit im Verkauf
Im Verkauf wurde bei der Nachhaltigkeitsprüfung für
Kontrakte der Kunde im Beleg, und nicht der Systemkunde herangezogen. Dies
führte dazu, dass Kontrakte abgewählt worden sind, obwohl der Systemkunde mit
der Ware nachhaltig handeln darf.
Releasenote Kategorie:
Ticket: 0[35867]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: [REB] [LIB]
Variante: STD
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35867, 0

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

## Stornierung von Rohwarebelegen

Stornierung von Rohwarebelegen
Im Modul zur Bearbeitung von Rohware-Belegen kam es
zuletzt in den Funktionen zur Erstellung von Stornolieferungen und
Stornoabrechnungen ohne Kopie mit neuem Belegdatum zu einer Meldung, dass das
eingegebene neue Belegdatum nicht zum Wirtschaftsjahr der Originalbelege passt,
obwohl ein Datum zum Wirtschaftsjahr der Quellbelege gewählt wurde. Dieses
Verhalten wurde nun überarbeitet und korrigiert.
Releasenote Kategorie:
Ticket: 740781[35992]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: RWB, RWBV
Variante: alle
Funktion/Report: Erstellen von Stornobelegen
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.8, 35992, 740781

---

## Individuelle Zu-/Abschläge bei Kontrakten

Individuelle Zu-/Abschläge bei Kontrakten
Die Behandlung individueller Zu-/Abschlagsgruppen bei
Kontrakten wurde durch die Einführung eines neuen Steuerparameter  [SPA]
"Individuelle Zu-/Abschläge bei Kontrakten berücksichtigen" (1160) wie folgt
überarbeitet: In Referenz-ERP besteht die Möglichkeit, eine Zu- und Abschlagsgruppe in
einem Kontrakt zu hinterlegen.  Damit ist es bei Verwendung dieses
Kontraktes in einem Vorgang möglich, zusätzlich definitere Zu- und Abschläge zu
ziehen. War im Kontrakt eine Zu- und Abschlagsgruppe hinterlegt und in Kunden /
Artikelkombination eine individuelle Zu- und Abschlagseinrichtung vorhanden,
übersteuerte die Individualeinrichtung die im Kontrakt definierte
Einrichtung.  Dieses Verhalten kann nun global über den "Steuerparameter"
[SPA] 1060 gesteuert werden. Wird dieser mit "Ja" eingestellt, ändert sich am
bisherigen Verfahren nichts. Wird dieser auf "Nein" gestellt, werden
individuelle Zu- und Abschläge nicht mehr gezogen.  Um mehr Flexibilität zu
haben, kann diese Einstellung auch im Kontrakt auf Tab-Reiter Konstanten pro
Kontrakt eingestellt werden. Diese Einstellung übersteuert dann die
SPA-Einstellung.  Wichtig ist, dass individuelle Zu- und Abschläge nur
ziehen, wenn in Zu- und Abschlagsgruppe wirklich ein Wert <>"0" gepflegt
ist.
Releasenote Kategorie:
Ticket: 743049[36294]
Version: 9.0.2501.5
Datum:
Anwendung: Kontrakte, Warenvorgangsbehandlung
Variante: -
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36294, 743049

---

## DB-Prozeduren für Rohware-Pauschalkosten

DB-Prozeduren für Rohware-Pauschalkosten
Die Verwendung von Datenbankprozeduren zur Bestimmung
von Pauschalbeträgen für Rohware-Kosten-/-Vergütungen führte zuletzt nicht zu
dem gewünschten Ergebnis. Es wurde statt des ermittelten Pauschalbetrags unter
Umständen der Betrag 0,00 in der Warenbewegung eingetragen.
Releasenote Kategorie:
Ticket: 743449[36313]
Version: 9.0.2501.5
Datum:
Anwendung: Rohwarengruppen
Variante: alle
Funktion/Report: Neu, Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36313, 743449

---

## Manuelles Valutadatum im Stornobeleg und in der Belegkopie.

Manuelles Valutadatum im Stornobeleg und in der Belegkopie.
In der Rohwarenbearbeitung [RWB] [RWBV] gibt es die
Funktion Storno mit Kopie. Nun kann hier entschieden werden, mit welchem
Valutadatum der Storno und/oder die Kopie versehen wird. Bei Verwendung von
Zinsabrechnungen in der Finanzbuchhaltung kann dies wichtig sein. Zu
beachten ist, dass nur ein manuelles Fälligkeitsdatum angegeben werden kann.
Systemseitig ist vorgeschrieben, dass die Zahlungsbedingung in dem Storno und
der Kopie vom Typ "manuelles Datum" sein müssen. Die entsprechende
Zahlungsbedingung kann auf der Maske ausgewählt werden.
Releasenote Kategorie:
Ticket: 740203[36491]
Version: 9.0.2501.5
Datum:
Anwendung: [RWB], [RWBV]
Variante: Rohware Anlieferung Einkauf, Bearbeiten
Sammeldruck Einkauf, Rohwarenlieferungen Verkauf, Bearbeiten Sammeldruck
Verkauf
Funktion/Report: Sammelstorno erstellen, Abr.
Stornobeleg., Lie. Stornobeleg
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36491, 740203

---

## Rohware-Lieferscheinstornobeleg ohne Belegkopie. Lieferschein fälschlicherweise in Massebilanz

Rohware-Lieferscheinstornobeleg ohne Belegkopie. Lieferschein
fälschlicherweise in Massebilanz
Bei Rohwareeingangs- und
Rohwareausgangslieferscheinen, die einer nicht festgeschriebenen Massebilanz
zugeordnet sind, wurde bei der Lieferscheinstornoerstellung (Lie. Stornobeleg)
ohne Belegkopie der Lieferschein bisher nicht aus der Massebilanz entfernt. Dies
wurde korrigiert.  Der Lieferschein und der dazugehörige Lieferscheinstorno
werden auch nicht in der Variante Bewegungsübersicht unter [NABEW]
angezeigt.
Releasenote Kategorie:
Ticket: 745790[36728]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: [RWB],[RWBV],[NABEW]
Variante: Rohware Anlieferung Einkauf,
Rohwareanlieferung Verkauf, Massebilanz, Bewegungsübersicht
Funktion/Report: Lie. Stornobeleg
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36728, 745790

---

## Vermehrungsvertrag

Vermehrungsvertrag
In den Feldern Vermehrer, VO-Firma, UVO-Firma und
Aufbereiter kann jetzt nebens der Nummer auch die Bezeichnung des Vermehrers,
VO-Firma, UVO-Firma und Aufbereiter eingegeben werden. Das Feld Erntejahr ist
jetzt immer Pflegbar
Releasenote Kategorie:
Ticket: 748412[37673]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Vermehrungsvertrag
Variante: Vermehrungsvertrag
Funktion/Report: Neu
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37673, 748412

---

## Kontraktvariante in Kontraktstammdaten

Kontraktvariante in Kontraktstammdaten
Im Kontraktstamm [KTR] wurde die F3-Auswahl für
Kontraktvarianten (Bezeichner: Variante Kontraktdruck) dahingehend überarbeitet,
dass nun nur noch Eingaben erlaubt sind, die in der F3-Auswahl vorkommen. Alte
bestehende Einträge, welche nicht in der F3-Auswahl enthalten sind, verhindern
das Speichern nicht. Erst bei wiederholter Eingabe im Feld Kontraktvariante wird
die Prüfung (und das Verhindern des Speicherns) angestoßen.  Beim öffnen
eines Kontraktes wird ggf. darauf hingewiesen, dass eine Kontraktvariante nicht
in der F3-Auswahl zu finden ist.
Releasenote Kategorie:
Ticket: 748421[37674]
Version: 9.0.2502.7
Datum:
Anwendung: Kontraktstammdaten [KTR]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 37674, 748421

---

## Zinsabrechnung bei Verwendung von Datenlöschung

Zinsabrechnung bei Verwendung von Datenlöschung
Die Verprobung der Zinsabrechnung erfolgt nur noch für
nicht abgeschlossene Perioden.
Releasenote Kategorie:
Ticket: 748882[38303]
Version: 9.0.2502.7
Datum:
Anwendung: Fibu-Reorganisation [FIREO]
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38303, 748882

---

## Bewegungen in der Kontraktübersicht

Bewegungen in der Kontraktübersicht
Ein Fehler in der Bewegungsübersicht (aufrufbar über
die Kontaktmaske), bei dem die Summen der Lieferwerte und Liefermengen nicht
korrekt dargestellt wurden, wurde behoben. Die Anzeige erfolgt nun wieder
korrekt.
Releasenote Kategorie:
Ticket: 751148[38497]
Version: 9.0.2502.7
Datum:
Anwendung: Kontrakte
Variante: Kontrakte
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.7, 38497, 751148

---

## Fehler in Massebilanz. Falsche Mengen werden in Bewegungsübersicht angezeigt

Fehler in Massebilanz. Falsche Mengen werden in Bewegungsübersicht
angezeigt
Bei Rohwarewarenpositionen ohne zugeordneter
Nettomassebilanz oder ohne zugeordneter Massebilanz wurden in der Auswahlliste
Bewegungsübersicht bei bestimmten
Mengeneinheiten/Mengeneinheitsgruppeneinrichtungen die Massezugang in Tonnen
falsch angezeigt.Dies war nur ein Anzeigefehler, der verschwunden ist, wenn die
Warenbewegung einer Massebilanz zugeordnet wurde.Dieser Fehler wurde
behoben.
Releasenote Kategorie:
Ticket: 751284[38735]
Version: 9.0.2502.9
Datum:
Anwendung: [NABEW] Nachhaltigkeit
Variante: Bewegungsübersicht
Funktion/Report: Massebilanz zuordnen, Massebilanz
entfernen, STRG + R
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38735, 751284

---

## Kontraktvariante [KTVA] Vorbelegung

Kontraktvariante [KTVA] Vorbelegung
In den Kontraktvarianten [KTVA] können als Teil
der Bereiche Festtexte eingerichtet werden. Für diese können nun wieder
Textbausteine gepflegt werden. Für die Pflege der Festtexte wurde jetzt ein
neues Feld "Textbaustein aktiv" hinzugefügt.  Dieses Feld kann als mögliche
Ausprägungen "Ja" oder "Nein" annehmen. Beim Erfassen eines Kontraktes, oder
beim Neuziehen einer Kontraktvariante, werden Textbausteine die mit
"Textbaustein aktiv" "nein" definiert sind, als nicht aktiv
übernommen.
Releasenote Kategorie:
Ticket: 752023[38820]
Version: 9.0.2502.9
Datum:
Anwendung: Kontraktstamm
Variante: -
Funktion/Report: Textbaustein
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38820, 752023

---

## E-Mail Adressen in den Anschriften

E-Mail Adressen in den Anschriften
Beim Löschen einer E-Mail Adresse aus der Liste wurde
diese zwar visuell aus der Liste entfernt, jedoch beim Speichern nicht aus dem
zugehörigen Datensatz gelöscht. Dadurch erschien die entfernte E-Mail Adresse
nach erneutem öffnen wieder in der Liste.Dieses Verhalten wurde korrigiert,
sodass gelöschte E-Mail Adressen nun zuverlässig und dauerhaft entfernt
werden.
Releasenote Kategorie:
Ticket: 753125[39329]
Version: 9.0.2502.9
Datum:
Anwendung: Anschriften
Variante: Anschriften
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39329, 753125

---

## Baustelle (EPA BAUSTAMM)

Baustelle (EPA BAUSTAMM)
Bezeichnung
Standardwert
Erklärung
Abrechnung möglich
Ja
Vorbelegung Rabatt 1 als
      Inzeilerabatt
Ja
Vorbelegung Rabatt 2 als
      Inzeilerabatt
Ja
Vorbelegung Rabatt 3 als
      Inzeilerabatt
Ja
Textnummer für Rabatt1
Textnummer für Rabatt2
Textnummer für Rabatt3

---

## Zinsabrechnung drucken (EPA FIZIABR)

Zinsabrechnung drucken (EPA FIZIABR)
Bezeichnung
Standardwert
Erklärung
Nur
      gebuchte drucken?
Nein
Die
      Einstellung
Ja
bewirkt, dass auf der Maske der Haken bei „Nur
      gebuchte drucken“ automatisch gesetzt ist und nicht geändert werden
      kann.

---

## Zinsbuchung stornieren (EPA FIZISTOR)

Zinsbuchung stornieren (EPA FIZISTOR)
Bezeichnung
Standardwert
Erklärung
Nur
      Buchung der letzten Zinsabrechnung stornierbar
Ja
Im
      Normalfall dürfen nur die Buchungen der letzten Zinsabrechnung storniert
      werden. Sollte es jedoch notwendig sein, die Buchungen älterer
      Zinsabrechnungen zu stornieren, so kann der Test, ob es sich um die letzte
      Zinsabrechnung handelt, hier ausgeschaltet werden.
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

## Kontraktartikel (EPA KTRARTIN)

Kontraktartikel (EPA KTRARTIN)
Bezeichnung
Standardwert
Erklärung
Bezeichnung für die Felder
      allgemeiner Wert / Bemerkung
Mit
      diesem Parameter kann die Bezeichnung für das Feld „Wert / Bemerkung“
      individuell gesetzt werden.
Itembox Artikel
      (lagerspezifisch)
IB_ARTIKEL_NU
Itembox Artikel
      (lagerunspezifisch)
IB_Artikel_Lg_UnSpezifisch_NU
Eigene Artikel Itembox für
      lagerunspezifische Kontrakte
Nein
Soll
      das lagerspezifische Kennzeichen in Kontrakt übernommen
      werden?
Nein
Wird
      dieser EPA gesetzt, so kann ein Eintrag „lagerspezifisch“ im Kontraktstamm
      eingesetzt werden.
Soll
      das Artikellager beim ersten Artikel ins Ziellager übernommen
      werden?
Nein
Sollen die Felder für Planlieferzeit
      und -datum angezeigt werden?
Ja
Mit
      diesem Parameter kann man die Felder Planlieferzeit / -datum anzeigen oder
      verschwinden lassen.
Kontraktpreis in Weltmarktpreis
      übernehmen?
Keine Übernahme
Soll
      das Rohwarengruppenfeld bei Rohwarenkontrakten gesperrt sein?
Ja
Hiermit kann das Rohwarengruppenfeld
      aktiviert oder deaktiviert werden. Dieser Parameter wirkt jedoch nicht,
      wenn der
Steuerparameter 612
auf „Nein“
      steht.
Berechnung der maximalen
      Unter-/Überschreitung auch bei Mengenänderung
Nein
Soll
      die Nachhaltigkeitsüberprüfung ins Fehlerprotokoll geschrieben
      werden?
Nein
Bei
      der Nachhaltigkeitsüberprüfung wird eine Fehlermeldung ausgegeben, so dass
      der Artikel nicht eingegeben werden kann.
Wird
      dieser Parameter auf „Ja“ gesetzt, erscheint die Meldung nicht mehr,
      sondern wird ins Fehlerprotokoll eingetragen.
Soll
      die Gebindeinfos angezeigt werden? (Nur für Testzwecke)
Nein
Mit
      diesem Parameter kann man einen Gebinderechner einschalten. Dies dient
      aktuell aber nur zu Testzwecken.
Prozedur zur Berechnung des
      allgemeinen Wertes
Hier
      kann eine Prozedur zum Berechnen des allgemei
[...]


---

## Kontraktexport (SMTP) (EPA KTREXPORT_SMTP)

Kontraktexport (SMTP) (EPA
KTREXPORT_SMTP)
Bezeichnung
Standardwert
Erklärung
Name
      der Exportprozedur
E-Mailadresse des
      Absenders

---

## Kontraktdruck (EPA KTRDRUCK)

Kontraktdruck (EPA KTRDRUCK)
Bezeichnung
Standardwert
Erklärung
Soll
      der Druckmerker ohne Frage gesetzt werden?
Nein

---

## Kontraktdruck (EPA KTRDRUCKER)

Kontraktdruck (EPA KTRDRUCKER)
Bezeichnung
Standardwert
Erklärung
Soll
      der Druckmerker ohne Frage gesetzt werden?
Nein

---

## Kontrakterledigung (EPA KTRERLEDIGUNG)

Kontrakterledigung (EPA
KTRERLEDIGUNG)
Bezeichnung
Standardwert
Erklärung
Soll
      eine Abfrage beim setzen des Kennzeichens erfolgen?
Nein
Hiermit kann eingestellt werden, ob
      eine Abfrage erfolgen soll, wenn man die Funktion
Erledigung
oder
Erledigung rücksetzen
aufruft.

---

## Kontraktpartien (EPA KTRPARTN)

Kontraktpartien (EPA KTRPARTN)
Bezeichnung
Standardwert
Erklärung
Nummernkreis der
      Kontraktkundengruppe bei neuer Freistellung
0

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

## Ausbuchen Fremd (EPA KTR_AUSBUCHEN_FREMD)

Ausbuchen Fremd (EPA
KTR_AUSBUCHEN_FREMD)
Bezeichnung
Standardwert
Erklärung
Erledigungskennzeichen sofort mit
      setzen
Ja
Kontraktpreis auf
      Gegenbuchungszeile
Nein
Vorgang sofort öffnen nach
      Ausbuchung
Nein
Partie mit rückbuchen
Ja
Preisliste
      Kontraktbuchung
Preisliste ohne
      Kontraktbuchung
Preise auf Null setzen
Ja

---

## Rohwaren Ergänzungsfelder (EPA ROHWAREERGAENZUNGSFELDER)

Rohwaren Ergänzungsfelder (EPA
ROHWAREERGAENZUNGSFELDER)
Bezeichnung
Standardwert
Erklärung
Feldname für die
      Belegreferenz

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

## MaskenTitel (EPA SVRESTM)

MaskenTitel (EPA SVRESTM)
Bezeichnung
Standardwert
Erklärung
Abfrage Restausbuchung
      stellen
Ja
Maske automatisch
      verlassen
Nein
Itembox Kontrakt
Itembox Partie
Menge änderbar
Ja

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktverarbeitung

Kontraktverarbeitung

---

## Kontraktübernahme

Kontraktübernahme
Kontrakte beinhalten zwar häufig umfangreiche
Informationen, in der Regel gleichen sie sich jedoch auch für gleiche
Geschäftsvorfälle. In diesem Fall kann man sich die Arbeit durch die Anlage von
Musterkontrakten (siehe
Stammdaten 2
) oder durch das Kopieren von
bestehenden Kontrakten erleichtern.
(K+MK) kopieren
Mit dieser Funktion kann ein Kontrakt oder ein
Musterkontrakt kopiert werden. Alle Daten werden dann aus dem ausgewählten
Kontrakt kopiert.
Angebot übernehmen
Mit dieser Funktion kann man Angebotskontrakte
(Kontraktklasse 5 / 15) übernehmen. Diese werden kopiert, nach der Übernahme
wird der ursprüngliche Beleg jedoch gelöscht.

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Rohwarenabwicklung

Rohwarenabwicklung

---

## Kontraktverwaltung angeschlossen (SPA 1)

Kontraktverwaltung angeschlossen (SPA 1)
Hiermit kann die Kontraktverwaltung aktiviert („Ja“)
oder deaktiviert („Nein“) werden.

---

## Kontrakt-Report-Zu-/Abschlag: Bezugsdatum (SPA 1002)

Kontrakt-Report-Zu-/Abschlag: Bezugsdatum (SPA 1002)
Hier wird das Bezugsdatum zur Berechnung der im
Kontrakt festgelegten zeitabhängigen Reports festgelegt. Dieses kann das
Preisdatum oder das Lieferdatum, bei Aufträgen entsprechend das Planlieferdatum,
sein.
Hinweis: Diese Einstellung gilt nicht für
Rohwarebelege, hier gilt IMMER das Lieferdatum als Bezugsdatum!

---

## Kontrakt-Parität-Zu-/Abschlag: Bezugsdatum (SPA 1004)

Kontrakt-Parität-Zu-/Abschlag: Bezugsdatum (SPA 1004)
Hier wird das Bezugsdatum zur Berechnung der im
Kontrakt festgelegten Paritäts-Zu-/Abschläge festgelegt. Dieses kann das
Preisdatum oder das Lieferdatum, bei Aufträgen entsprechend das Planlieferdatum,
sein.
Hinweis: Diese Einstellung gilt nicht für
Rohwarebelege, hier gilt IMMER das Lieferdatum als Bezugsdatum!

---

## Kontrakt-Überziehungs-Zu-/Abschlag: Bezugsdatum (SPA 1003)

Kontrakt-Überziehungs-Zu-/Abschlag: Bezugsdatum (SPA 1003)
Hier wird das Bezugsdatum zur Berechnung des im
Kontrakt festgelegten Überziehungs-Zu-/Abschlags festgelegt. Dieses kann das
Preisdatum oder das Lieferdatum, bei Aufträgen entsprechend das Planlieferdatum,
sein.
Hinweis: Diese Einstellung gilt nicht für
Rohwarebelege, hier gilt IMMER das Lieferdatum als Bezugsdatum!

---

## Kontrakt Restmengenanzeig(SPA 1014)

Kontrakt Restmengenanzeig(SPA 1014)
Mit dem Steuerparameter Kontrakt
Restmengenanzeige(1014) kann die Anzeige der Restmenge im
Kontraktverteilungsgrid gesteuert werden.
Verhalten
Bedeutung
Gesamtmenge
Mit
      dieser Einstellung wird die Gesamtrestmenge über die Kontraktlaufzeit
      angezeigt. Unabhängig der Standardkontravariante.
Zeitraumrestmenge
Mit
      dieser Einstellung wird anstelle der Gesamtrestmenge die
      Zeitraumsrestmenge angezeigt, wenn der Kontrakt mehrere Zeiträume
      hat.
Zeitraumrestmenge mit Rest über
      Gesamt
Mit
      dieser Einstellung wird anstelle der Gesamtrestmenge die
      Zeitraumsrestmenge angezeigt, wenn der Kontrakt mehrere Zeiträume hat.
      Aber wenn der Schalter „Restmenge über Gesamtzeit“ auf Ja steht, wird die
      Gesamtrestmenge angezeigt.

---

## Kontraktauswahl im Barverkauf (SPA 1075)

Kontraktauswahl
im Barverkauf (SPA 1075)
Einstellung
Bedeutung
Ja
Aktiviert die Kontraktauswahl im
      Barverkauf.
Nein
Keine Kontraktauswahl im Barverkauf
      (Standard).
Passende Kontrakte direkt
      zuordnen
Passende Kontrakte werden ohne
      Abfrage direkt zugeordnet.

---

## Vertreterabrechnung(Food)-Lizenz (SPA1087)

Vertreterabrechnung(Food)-Lizenz (SPA1087)
Lizenz für Vertreterabrechnung(Food).

---

## DSD-Abrechnung-Lizenz (SPA1109)

DSD-Abrechnung-Lizenz (SPA1109)
Lizenz für das Modul „DSD-Abrechnung“.

---

## Kontrakt-Gesamt-Engagement-Lizenz (SPA1113)

Kontrakt-Gesamt-Engagement-Lizenz (SPA1113)
Lizenz für „Kontrakt-Gesamt-Engagement“.

---

## Kontrakt-Nullsetzung zulässig(SPA 115)

Kontrakt-Nullsetzung zulässig(SPA 115)

---

## Kontraktnachhaltigkeit überschreibt Warenpositionsnachhaltigkeit (SPA 1155)

Kontraktnachhaltigkeit überschreibt
Warenpositionsnachhaltigkeit (SPA 1155)
Standard ist „Nein“
SPA-Einstellung
Kontraktartikel
      nachhaltig
Warenposition
    nachhaltig
Nachhaltigkeitswerte
Resultierender
      Nachhaltigkeitsstatus der Warenposition
Nachhaltigkeitsherkunft
Nein
Nein
Nein
Nachhaltigkeitsstatus der
      Warenposition
Nicht Nachhaltig
Kunde
Nein
Ja
Nein
Nachhaltigkeitsstatus der
      Warenposition
Nicht Nachhaltig
Kunde
Nein
Nein
Ja
Nachhaltigkeitsstatus der
      Warenposition
Nachhaltig
Kunde
Nein
Ja
Ja
Nachhaltigkeitsstatus des
      Kontraktartikels überschreibt den Nachhaltigkeitsstatus der
      Warenposition
Nachhaltig
Kontrakt
Ja
Nein
Nein
Nachhaltigkeitsstatus des
      Kontraktartikels überschreibt den Nachhaltigkeitsstatus der
      Warenposition
Nicht Nachhaltig
Kontrakt
Ja
Ja
Nein
Nachhaltigkeitsstatus des
      Kontraktartikels überschreibt den Nachhaltigkeitsstatus der
      Warenposition
Nachhaltig
Kontrakt
Ja
Nein
Ja
Nachhaltigkeitsstatus des
      Kontraktartikels überschreibt den Nachhaltigkeitsstatus der
      Warenposition
Nicht Nachhaltig
Kontrakt
Ja
Ja
Ja
Nachhaltigkeitsstatus des
      Kontraktartikels überschreibt den Nachhaltigkeitsstatus der
      Warenposition
Nachhaltig
Kontrakt
Wird dieser SPA auf „Nein“ gestellt, dann wird bei der
Nachhaltigkeitsvorbelegung und der Nachhaltigkeitskorrektur durch den
Mandantenserver nur die Warenpositionen mit Nachhaltigkeitswerten des
Kontraktartikels aus einem Kontrakt überschrieben, wenn der Kontraktartikel
nachhaltig ist und der betroffene Kunde für den Artikel ein gültiges
Nachhaltigkeitszertifikat besitzt.
Wird dieser SPA auf „Ja“ gestellt, dann werden immer
bei einem zugeordneten Kontrakt, die Nachhaltigkeitswerte des Kontraktartikels
benutzt, um die Nachhaltigkeitswerte der Warenposition zu überschreiben.
Wenn der Kontraktartikel in diesem Fall nicht
nachhaltig ist, dann wird die Warenposition auch nicht nachhaltig und alle
anderen Nachhaltigkeitsw
[...]


---

## Kontraktabwahl bei Nachhaltigkeitsfehler (SPA 1158)

Kontraktabwahl bei Nachhaltigkeitsfehler (SPA
1158)
Aktuell ist durch diesen SPA nur folgende Kombination
unter Schutz:
Der Kontraktartikel im Kontrakt hat den Nachhaltigkeitsstatus
„Nachhaltig“ und die Warenposition hat den Nachhaltigkeitsstatus „Nicht
Nachhaltig“.
Nur in dieser Kombination greift der SPA und achtet
auf die folgenden Einrichtungsmöglichkeiten.
Standard ist „keine Kontraktabwahl, kein Hinweis“.
SPA-Einstellung
Zertifikat für Lieferant (bei
      Verkauf Mandantkunde) für Artikel
Anzeige einer
Warnung
Kontrakt wird
    abgewählt
Kontraktabwahl, kein
      Hinweis
Abgelaufen, ungültig oder nicht
      nachhaltig
Nein
Nein
Kontraktabwahl, kein
      Hinweis
Gültig und nachhaltig
Nein
Nein
nur
      Hinweis auf notwendige Kontraktabwahl
Abgelaufen, ungültig oder nicht
      nachhaltig
Ja
Nein
nur
      Hinweis auf notwendige Kontraktabwahl
Gültig und nachhaltig
Nein
Nein
Kontraktabwahl und
      Hinweis
Abgelaufen, ungültig oder nicht
      nachhaltig
Ja
Ja
Kontraktabwahl und
      Hinweis
Gültig und nachhaltig
Nein
Nein
Wird dieser SPA auf „Kontraktabwahl, kein Hinweis“
gestellt, dann wird nichts überprüft.
Wird dieser SPA auf „nur Hinweis auf notwendige
Kontraktabwahl“ gestellt, dann wird bei der manuellen oder automatischen
Kontraktauswahl überprüft, ob der für den Beleg relevante Kunde für den Artikel
im Beleg/Kontrakt ein gültiges Nachhaltigkeitszertifikat besitzt. Dies bedeutet,
dass man auf dem Kundenstammpfleger im Tabreiter Zertifikate ein Zertifikat
größer gleich 10 hat. Siehe dem Anwenderformat
AF_NACHHSTAT
.
Wenn kein
Nachhaltigkeitszertifikat vorhanden ist, das Nachhaltigkeitszertifikat den
Status 1-9 hat, oder das Gültigkeitsdatum des Belegs außerhalb des
Nachhaltigkeitszertifikates liegt, dann wird eine Warnung generiert.
Wird dieser SPA auf „Kontraktabwahl und Hinweis“
gestellt, dann wird neben der Warnung auch ein Fehlerprotokolleintrag
geschrieben und der Kontrakt wird abgewählt.

---

## Individuelle Zu-/Abschläge bei Kontrakten berücksichtigen (SPA 1160)

Individuelle Zu-/Abschläge bei Kontrakten berücksichtigen (
SPA 1160
)
Dieser Steuerparameter beeinflusst die
Berücksichtigung individueller Zu-/Abschlagsgruppen bei der Berechnung
allgemeiner Zu-/Abschläge innerhalb von Kontrakten.
Durch die Auswahl einer allgemeinen
Zu-/Abschlagsgruppe am Kontrakt selbst, wird die Berechnung von Zu-/Abschlägen
für den Kontrakt grundsätzlich aktiviert.
Ohne Bestimmung einer solchen
Gruppe am Kontrakt werden keinerlei Zu-/Abschläge berechnet
.
Neben der Zu-/Abschlagsgruppe am Kontrakt können
individuelle Zu-/Abschläge existieren, die sich vorrangig aus der Kombination
von Kontrakttyp, Kunde und Artikel ergeben. Solche individuellen
Zu-/Abschlagsgruppen hatten in der Vergangenheit immer schon Vorrang vor der am
Kontrakt hinterlegten allgemeinen Zu-/Abschlagsgruppe: Wird eine individuelle
Zu-/Abschlagsgruppe gefunden, so wird die Zu-/Abschlagsgruppe am Kontrakt
ignoriert – dieses Verhalten entspricht der Steuer-parameter-Einstellung „Ja“
(Default). Wird der Steuerparameter auf „Nein“ gestellt, so werden individuelle
Zu-/Abschlagsgruppen ignoriert und nur die am Kontrakt hinterlegte
Zu-/Abschlagsgruppe bei der Kontraktberechnung berücksichtigt.
Dieses Verhalten kann zusätzlich über eine direkt am
Kontrakt verfügbare Auswahlmöglichkeit übersteuert werden, so dass sich eine
kontraktspezifische Berücksichtigung individueller Zu-/Abschlagsgruppen
ergibt.

---

## Bei Vorverkauf normale Kontrakte ziehen (SPA 1169)

Bei Vorverkauf normale Kontrakte ziehen (SPA 1169)
Ist dieser Steuerparameter eingeschaltet, so ist es
gestattet, in Vorverkaufspositionen „normale“ Kontrakte zu verwenden. Bei
„Nein“, was die Voreinstellung ist, werden in Vorverkaufspositionen nur
Vorverkaufskontrakte angezeigt und verwendet.

---

## Bei Voreinkauf normale Kontrakte ziehen (SPA 1170)

Bei Voreinkauf normale Kontrakte ziehen (SPA 1170)
Ist dieser Steuerparameter eingeschaltet, so ist es
gestattet, in Voreinkaufspositionen „normale“ Kontrakte zu verwenden. Bei
„Nein“, was die Voreinstellung ist, werden in Voreinkaufspositionen nur
Voreinkaufskontrakte angezeigt und verwendet.

---

## Zahlungsbedingung aus Kundestamm vorbelegen (SPA 1171)

Zahlungsbedingung aus Kundestamm vorbelegen (SPA 1171)
Der SPA 1171 steht per Default auf „Nein“.
Wert
Beschreibung
Nein
Keine Auswirkung
Ja
Bei
      der Kontrakterfassung wird die Zahlungsbedingung nach der Wahl eines
      Hauptkunden zur Kontraktklasse (EK/VK) passend
      vorbelegt.

---

## Individuelle Rabatte bei Kontakten berücksichtigen (SPA 1173)

Individue
lle Rabatte bei Kontakten berücksichtigen
(SPA 1173)
Dieser Steuerparameter bestimmt, welche Rabattlogik
innerhalb eines Kontrakts angewendet wird. Er entfaltet seine Wirkung nur dann,
wenn am Kontrakt eine Rabattgruppe hinterlegt ist und die Option „Individuelle
Rabattgruppe“ auf „wie SPA“ eingestellt ist.
In diesem Fall wird über den Steuerparameter global
festgelegt, ob individuelle Rabatte aus dem Artikel oder die Rabatte aus dem
Kontrakt für die Berechnung herangezogen werden.
Verhalten des Steuerparameters:
Einstellung
Bedeutung
Ja
      (Defautl)
Es
      wird die am Artikel hinterlegte individuelle Rabattgruppe
      verwendet.
Nein
Auch
      wenn am Artikel eine Individuelle Rabattgruppe hinterlegt worden ist, so
      wird diese nicht berücksichtigt. Stattdessen wird der im Kontrakt
      hinterlegte Rabattgruppe angewendet

---

## Individuelle Frachten bei Kontrakten berücksichtigen (SPA 1174)

Individuelle Fracht
en bei Kontrakten berücksichtigen
(SPA 1174)
Dieser Steuerparameter bestimmt, welche
Frachtgruppenlogik innerhalb eines Kontrakts angewendet wird. Er entfaltet seine
Wirkung nur dann, wenn am Kontrakt eine Frachtgruppe hinterlegt ist und die
Option „Individuelle Frachtgruppe“ auf „wie SPA“ eingestellt ist.
In diesem Fall wird über den Steuerparameter global
festgelegt, ob die individuelle Frachtgruppe aus dem Artikel oder die
Frachtgruppe aus dem Kontrakt für die Berechnung herangezogen werden.
Verhalten des Steuerparameters:
Einstellung
Bedeutung
Ja
      (Defautl)
Es
      wird die am Artikel hinterlegte individuelle Frachtgruppe
      verwendet.
Nein
Auch
      wenn am Artikel eine Individuelle Frachtgruppe hinterlegt worden ist, so
      wird diese nicht berücksichtigt. Stattdessen wird die im Kontrakt
      hinterlegte Frachtgruppe angewendet

---

## Rohwarenabrechnung angeschlossen(SPA 135)

Rohwarenabrechnung angeschlossen(SPA 135)
Mit diesem Steuerparameter kann die Rohwarenabrechnung
aktiviert / deaktiviert werden.

---

## Vor Anfang der Laufzeit bebuchbar (SPA 150)

Vor Anfang der Laufzeit bebuchbar (SPA 150)
Wert
Bedeutung
Nein
Ein
      Kontrakt kann nicht vor der Laufzeit bebucht werden.
Ja
Es
      ist möglich einen Kontrakt manuell vor der Laufzeit zu buchen. Die
      Bewegungen werden dem ersten Zeitraum eines Kontrakts zugeordnet.
Der
      Preis wird aus dem ersten Preiszeitraum ermittelt.

---

## Artikel mit inkompatiblen Mengeneinheiten (SPA 153)

Artikel mit inkompatiblen Mengeneinheiten (SPA 153)
Mit diesem Steuerparameter kann festgelegt werden,
dass die Artikel eines Kontrakts unterschiedliche Mengeneinheiten haben können.
Dabei ist zu beachten, dass bestimmte
Auswertungen (z.B. mengenmäßiges Engagement) nicht sinnvoll sind.

---

## Kontraktpreis änderbar bei Vorgangserfassung (SPA 159)

Kontraktpreis änderbar bei Vorgangserfassung (SPA 159)
Steht der Steuerparameter auf „Nein“, kann der
Kontraktpreis bei der Vorgangserfassung nicht überschrieben werden.

---

## Kontraktzuschläge / -abschläge aktiv (SPA 179)

Kontraktzuschläge / -abschläge aktiv (SPA 179)
Hier wird festgelegt, ob im Kontrakt eingerichtete
Überziehungs-, Paritäts- und Reportzuschläge aktiv sein sollen.

---

## Dispositionskennzeichen ist Kontraktnummer bei Einkauf (SPA 188)

Dispositionskennzeichen ist Kontraktnummer bei Einkauf (SPA 188)
Mittels eines neuen Steuerungsparameters kann
aktiviert werden, dass beim Erfassen von Einkaufskontrakten automatisch das
Dispositionskennzeichen mit identischer Nummerierung erzeugt wird, wenn das dann
entsprechend vorbelegte Kennzeichen nicht abweichend überschrieben wird. Die
Kontraktbezeichnung wird mit übernommen.
Somit ist es möglich, sich die Arbeit zu erleichtern,
wenn generell jeder Einkaufskontrakt einer Anzahl von Verkaufskontrakten
zugeordnet werden soll, denn die Zuordnung erfolgt direkt mit der Kontraktnummer
des Einkaufskontrakts.

---

## Kontraktausweichliste aktiv (SPA 198)

Kontraktausweichliste aktiv (SPA 198)

---

## Kontrakt auch bei anderer Währung ziehen (SPA 205)

Kontrakt auch bei anderer Währung ziehen (SPA 205)
Mit dem Wert „Nein“ stehen in der Kontraktauswahl nur
Kontrakte zur Verfügung, die in derselben Währung sind wie die aktuelle
Belegwährung.
Beim Wert „Ja“ stehen Kontrakte unabhängig von der
Kontraktwährung bzw. Belegwährung zur Verfügung.

---

## Rohwarekontrakte in Normalvorgängen (SPA 217)

Rohwarekontrakte in Normalvorgängen (SPA 217)

---

## Lieferung an Objekt(e) mit Abrechnung(SPA 220)

Lieferung an Objekt(e) mit Abrechnung(SPA 220)
Bei ‚Nein‘ wird das Kennzeichen, ‚Abrechnung möglich‘
ausgewertet, ob dieses Objekt zur Fakturation freigegeben wird. Bei ‚Ja‘ wird
dieses Objekt immer berücksichtigt.

---

## Kontrakte auch des Kontraktkunden (SPA 261)

Kontrakte auch des Kontraktkunden (SPA 261)
Steht der Steuerparameter auf „Ja“, werden bei der
Kontraktauswahl auch die Kontrakte des übergeordneten Kontraktkunden zur
Verfügung gestellt.
Beim Wert „Nein“ stehen nur die Kontrakte des Kunden
zur Verfügung.

---

## Kontrakthinweise im Vorgangsdruck (SPA 263)

Kontrakthinweise im Vorgangsdruck (SPA 263)

---

## Kontraktartikel in Rohware mit Sorte anzeigen (SPA 281)

Kontraktartikel in Rohware mit Sorte anzeigen (SPA 281)

---

## Kontrakthinweis im Vorgangsdruck ohne Oberkunde (SPA 283)

Kontrakthinweis im Vorgangsdruck ohne Oberkunde (SPA 283)

---

## Neuer Fremdwarekontrakt je Vorverkauf (SPA 306)

Neuer Fremdwarekontrakt je Vorverkauf (SPA 306)

---

## Liefersperre und Vorgangserfassungssperre bei Kontrakt auswerten (SPA 336)

Liefersperre und Vorgangserfassungssperre bei Kontrakt auswerten (SPA
336)
Wert
Bedeutung
Nein
Es
      findet keine Prüfung bezüglich der Liefer- und Vorgangserfassungssperre
      statt.
Liefersperre
      Verkaufskontrakte
Es
      wird die Liefersperre nur für Verkaufskontrakte ausgewertet
Liefersperre VK /
      Vorgangserfassungssperre EK und VK
Es
      wird die Liefersperre für Verkaufskontrakt ausgewertet, des Weiteren wird
      die Vorgangserfassungssperre für den Einkauf und den Verkauf
      ausgewertet.

---

## Währungsnummer für Rohwaretabellen(SPA 362)

Währungsnummer für Rohwaretabellen(SPA 362)
Hier wird eingetragen, mit welcher Währungsnummer Zu-
/ Abschlagspreise bei Rohware geführt werden.

---

## Zinsabrechnung aktiv(SPA 38)

Zinsabrechnung aktiv(SPA 38)
Mit diesem SPA kann das Zinswesen aktiviert /
deaktiviert werden.

---

## Kontraktauswahl mit Restmenge 0 (SPA 384)

Kontraktauswahl mit Restmenge 0 (SPA 384)
Bei „Nein“ werden in der Kontraktauswahl Kontrakte mit
der Restmenge 0 nicht mehr angezeigt.
Steht der Parameter auf „Ja“ werden auch Kontrakte mit
der Restmenge 0 angezeigt.

---

## Vorgangskopie absichern(SPA 396)

Vorgangskopie absichern(SPA 396)
Einstellungen
Nein
Kopie weiter ohne Rücksicht auf
      Strecke, Partie, Kontrakt möglich. Diese Einstellung ist gefährlich! So
      kann es zum Beispiel zu Zuordnungen von Partien und Kontrakten des
      Ursprungskunden zum neuen Kunden kommen u.a.
Ja
Vorgangskopie bei Vorgängen mit
      Strecke, Partie, Kontrakt nicht möglich
Mit
      Behandlungsschema
Bei
      Vorgangskopie mit Kundenwechsel wird der Kundenwechsel gemäß dem gewählten
      Behandlungsschema vorgenommen. Das Behandlungsschema, das für die
      Vorgangskopie vorgeschlagen wird, kann mit Hilfe des
SPA 827
festgelegt werden.

---

## Vorbelegung Standardtyp (SPA 43)

Vorbelegung Standardtyp (SPA 43)
Mit diesem Steuerparameter kann die Vorbelegung der
Standardkontraktvariante
festgelegt werden.

---

## Kontrakt-Lizenz(SPA 434)

Kontrakt-Lizenz(SPA 434)
Lizenz für Kontrakte.

---

## Rohwaren-Lizenz(SPA 436)

Rohwaren-Lizenz(SPA 436)
Lizenz für Rohware.

---

## Variante Kontraktauswahl (SPA 44)

Variante Kontraktauswahl (SPA 44)
Der Steuerparameter legt fest, wie die Anzeige der
Kontraktauswahl in der Vorgangserfassung erfolgen soll.

---

## Vertreterabrechnung-Lizenz(SPA 442)

Vertreterabrechnung-Lizenz(SPA 442)
Lizenz für Vertreterabrechnung.

---

## Vorbelegung Kontraktpartien analog Mengenzeiträume (SPA 46)

Vorbelegung Kontraktpartien analog Mengenzeiträume (SPA 46)
Bei Vorbelegung „Ja“, werden die entsprechend der
Einteilung des Kontrakts zeitliche Mengen gebildet.

---

## Vorbelegung der Kontraktwährung (SPA 506)

Vorbelegung der Kontraktwährung (SPA 506)
Hier wird entschieden, wie die Währung bei Neuanlage
von Kontrakten vorbelegt wird.
Wert
Bedeutung
0
      (keine)
Es
      erfolgt keine Vorbelegung, d.h. es wird die Währung 0
      verwendet.
1
      (aus Kundestamm)
Die
      Vorbelegung erfolgt mit der Währung des Kunden.
2
      (wie Buchwährung)
Die
      aktuelle Buchwährung wird als Vorbelegung verwendet.

---

## Kontraktsollmengenänderung bei Bewegung (SPA 535)

Kontraktsollmengenänderung bei Bewegung (SPA 535)
Der Parameter gibt an ob die Kontraktsollmenge (auch
nach Verbuchung) geändert werden kann, oder ob sie nur angezeigt wird.

---

## Kontrakte mit Ausweichartikeln wie Gesamtmenge (SPA 544)

Kontrakte mit Ausweichartikeln wie Gesamtmenge (SPA 544)
Steht der Steuerparameter auf „Ja“ werden bei
Einzelmengenkontrakten mit Ausweichlisten die Restmengen wie bei
Gesamtmengenkontrakten ermittelt.

---

## Max. Kontraktlaufzeit berücksichtigen (SPA 559)

Max. Kontraktlaufzeit berücksichtigen (SPA 559)
Steht der Steuerparameter auf „Ja“, wird die maximale
Laufzeit des Kontraktes bei der Kontraktauswahl berücksichtigt.

---

## Neuer Fremdlagerkontrakt je Voreinkauf (SPA 580)

Neuer Fremdlagerkontrakt je Voreinkauf (SPA 580)

---

## Rohwarengruppe und Sorte aus Artikel vor

Rohwarengruppe und Sorte aus Artikel vor
Wert
Beschreibung
Nein
Keine Auswirkung
Ja
Bei
      der Kontraktartikelerfassung für Rohwarekontrakte wird die Rohwarengruppe
      und Rohwarensorte aus dem Artikel vorbelegt.

---

## Suchstrategie zur Kontraktbestimmung (SPA 618)

Suchstrategie zur Kontraktbestimmung (SPA 618)

---

## Lager bei Kontraktauswahl in der Waage(SPA 620)

Lager bei Kontraktauswahl in der Waage(SPA 620)
An diesem Steuerparameter wird das Verhalten für das
Lager nach der Kontraktauswahl festgelegt.
Folgende Optionen sind vorhanden:
Option
Beschreibung
Lager immer aus
      Kontraktartikel
Es
      wird immer das Lager aus dem Kontraktartikel verwendet (nicht das Kontrakt
      Ziellager!).
Standardlager des Bedieners
(Direktsprung [VKONS])
Es
      wird immer das Standardlager des Bedieners verwendet. Wenn der Artikel
      dort nicht vorhanden ist, wird das Lager aus dem Kontraktartikel benutzt.
Kontrakt bestimmt Lager
Es
      wird das Lager aus dem Kontrakt Ziellager verwendet. Wenn der Artikel dort
      nicht vorhanden ist, wird das Lager aus dem Kontraktartikel
      benutzt.
Lager aus Kontrakt wenn Ziellager
      ungleich 0, sonst Standardlager
Es
      wird das Lager aus dem Kontrakt Ziellager verwendet, sofern dieses nicht 0
      ist. Ansonsten wird das Standardlager des Bedieners benutzt. Wenn der
      Artikel dort nicht vorhanden ist, wird das Lager aus dem Kontraktartikel
      benutzt.

---

## Hedging benutzen (SPA 635)

Hedging benutzen (SPA 635)
Gibt an, ob Hedging in Kontrakten verwendet wird oder
nicht.

---

## Automatische Auswahl bei Vorgangsbearbeitung (SPA 64)

Automatische Auswahl bei Vorgangsbearbeitung (SPA 64)
Das Kontraktauswahlfenster in der Vorgangserfassung
wird entweder nie, immer oder ab zwei Kontrakte geöffnet. Bei nie geöffnet wird
der erste gültige Kontrakt verwendet.

---

## Vorbelegung Mengeneinheit (SPA 641)

Vorbelegung Mengeneinheit (SPA 641)
Legt die Standardvorbelegung für die Mengeneinheiten
eines Kontraktes fest.

---

## Washout-Circle Kontraktsteuergruppe (SPA 643)

Washout-Circle Kontraktsteuergruppe (SPA 643)
Dieser Steuerparameter steuert die Steuergruppe für
„Circle und Washout“ Geschäfte. Geben Sie als Wert der speziellen Steuergruppe
ein.
Dabei sollte beachtet werden, dass in Deutschland
keine Steuern auf „Circle und Washout“ Geschäfte anfällt.

---

## Bei Kontrakterledigung ist Restmenge 0 (SPA 649)

Bei Kontrakterledigung ist Restmenge 0 (SPA 649)
Steht der Steuerparameter auf „Ja“, werden die
Restmengen bei Kontrakten mit 0 angezeigt, ansonsten werden die eigentlichen
Restmengen angezeigt.

---

## Rohwarestorno mit Quellbeleg- Kopie(SPA 654)

Rohwarestorno mit Quellbeleg- Kopie(SPA 654)
Hier kann angegeben werden, ob die Option „Kopie nach
Storno“ bei der Umwandlung eines Rohwarebeleges in einen Stornobeleg
freigeschaltet werden soll.

---

## Rohwarestorno mit Alternat. bez. Fibstatus(SPA 655)

Rohwarestorno mit Alternat. bez. Fibstatus(SPA
655)
Für die Funktion ‚Rohwarestornobeleg-Erzeugung‘ wird
hier angegeben, ob es bezüglich des Fibuübertrag-Status des Rohwarequellbelegs
alternative Handlungsweisen geben darf. Durch die Einstellung dieses Parameters
mit dem Wert „erlaubt“ wird auf der Stornierungsmaske das Feld
Stornobeleg
erzeugen
mit unterschiedlichen Einstellmöglichkeiten
freigeschaltet.

---

## Einlagerung Kontrakt Laufzeit(SPA 678)

Einlagerung Kontrakt Laufzeit(SPA 678)
Gibt die Maximale Kontraktlaufzeit von dem
Erfassungsdatum des Rohwarenbeleges bei der Einlagerung an in Jahresschritten
an.

---

## Erledigung ohne Erledigungsschreiben (SPA 68)

Erledigung ohne Erledigungsschreiben (SPA 68)
Bei Einstellung „Ja“, wird auf ein
Erledigungsschreiben verzichtet, das den Kontrakt auch intern als erledigt
kennzeichnet.

---

## Kontraktstandardlaufzeit in Tagen (SPA 681)

Kontraktstandardlaufzeit in Tagen (SPA 681)
Der Steuerparameter legt die Standardlaufzeit eines
Kontrakts fest.

---

## Nachkommastellen für Mengen in Kontrakten (SPA 696)

Nachkommastellen für Mengen in Kontrakten (SPA 696)
Der Steuerparameter legt die Vorbelegung der
Nachkommastellen im Kontraktstamm fest.

---

## Umgewandelte Fremdkontrakte nicht löschen bei Vorgangsstornierung (SPA 699)

Umgewandelte Fremdkontrakte nicht löschen bei Vorgangsstornierung (SPA
699)
Wird ein Vorgang storniert, der durch die Umwandlung
eines normalen Kontraktes in einen Fremdware / -lagerkontrakt entstanden ist und
der Parameter auf „Ja“ steht, wird der Kontrakt nicht gelöscht, sondern in die
ursprüngliche Kontraktklasse umgewandelt.

---

## Maximale Vorausmonate für ratierliche Kontraktmengen (SPA 698)

Maximale Vorausmonate für ratierliche Kontraktmengen (SPA
698)
Die Anzahl der Vorausmonate für die ratierliche
Verteilung kann hier eingerichtet werden. Die Menge wird dann auf die
entsprechenden Monate verteilt. Es gilt dabei immer, dass der erste Monat auch
der aktuelle Monat ist.
Mengen die vor dem aktuellen Monat liegen, werden in
die Spalte „Vormonate“ geschrieben. Mengen die nach den Vorausmonaten liegen,
werden auf die darauffolgenden Spalten verteilt.
(z.B. Anzahl Vorausmonate
ist fünf dann werden die darauffolgenden Wert in die Spalte 6
geschrieben)
.

---

## Berechnung für ratierliche Kontraktmengen aktiv (SPA 701)

Berechnung
für ratierliche Kontraktmengen aktiv (SPA 701)
Damit die ratierlichen Kontraktmengen berechnet
werden, muss der Steuerparameter auf „Ja“ gestellt werden.

---

## Vorverkauf Fremdkontrakt (SPA 710)

Vorverkauf Fremdkontrakt (SPA 710)

---

## Voreinkauf Fremdkontrakt (SPA 711)

Voreinkauf Fremdkontrakt (SPA 711)

---

## Kommission Fremdkontrakt (SPA 713)

Kommission Fremdkontrakt (SPA 713)

---

## Kontrakterledigung automatisch aufheben (SPA 714)

Kontrakterledigung automatisch aufheben (SPA 714)
Bei aktiviertem SPA werden bereits erledigte Kontrakte
wieder aktiviert (das Erledigungskennzeichen wird zurückgesetzt), falls Belege
korrigiert oder gelöscht werden, die sich auf diese Kontrakte beziehen.

---

## Kontraktnummer bei Neuanlage nicht eingebbar (SPA 793)

Kontraktnummer bei Neuanlage nicht eingebbar (SPA 793)
Mit diesem Steuerparameter kann die Eingabemöglichkeit
der Kontraktnummer bei Neuanlage von Kontrakten unterbunden werden.

---

## Ratierliche Berechnung mit dem Kontraktlaufzeit-Bis-Datum (SPA 798)

Ratierliche Berechnung mit dem Kontraktlaufzeit-Bis-Datum
(SPA 798)
Damit die ratierliche Berechnung mit dem
„Laufzeit-Bis-Datum“ arbeitet muss der Steuerparameter auf „Ja“ gestellt werden.
Ansonsten wird mit dem „maximal Laufzeit-Bis-Datum“ gearbeitet.

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

## Ratierliche Einstellungen (SPA 846)

Ratierliche Einstellungen (SPA 846)
In diesem Steuerparameter können Optionen für die
ratierliche Verteilung und/oder ratierliche Restmengenanzeige der
Zeitraum-Tabellen im Kontraktstammpflegemodul eingestellt werden.
Zur Einstellung stehen verschiedene Typen zur
Verfügung.
Typ
Wert
MENGEUEBER
Für
      die Anzeige ratierlicher Monatsmengen in der Standardauswahlliste des
      Kontraktstamm-Pflegemoduls wie auch bei der variablen Zeitraumwahl (Option
      „Variable Kontraktzeitraumzuordnung“) während der
      Warenpositionsbearbeitung eines Vorgangs gilt bei der Einstellung dieser
      Option mit dem Wert „Ja“:
Ist bei der Verteilung die gelieferte
      Menge größer als die ratierliche Menge des Monats, wird die Übermenge in
      den nächsten Monat übernommen.
Übermengen die über die Zeiträume
      hinausgehen, werden im speziellen Feld „UEBERMENGE“ in den jeweiligen
      Tabellen gespeichert.
Variable
      Kontraktzeitraumzuordnung
Bei
      der Einstellung dieser Option mit dem Wert „Ja“ wird bei der Funktion
      „Kontraktzeitraum“ in der Warenpositionsmaske der Vorgangsbearbeitung eine
      erweiterte Kontraktzeitraummaske genutzt, die es ermöglicht, einen anderen
      als den automatisch zugeordneten Zeitraum zur Kontraktpositionszuordnung
      zu nutzen.
Ktr-Anzeige Minusrest in
      Folgezeitraum
Diese Option schaltet bei der
      Einstellung mit dem Wert „Ja“ auf den Zeitraummasken des
      Kontraktpflegemoduls (Mengenzeiträume, Artikelmengen) eine zusätzliche
      Tabellen-Spalte „Rest>0“ frei, in der negative
      Zeitraum-Restmengen/-werte (Übermengen/Überwerte) in den jeweils nächsten
      Zeitraum zur Verrechnung mit der dortigen Restmenge/Restwert übertragen
      werden. Die Restmenge/Restwert der Zeile selbst wird mit dem Wert „0“
      ausgewiesen.
Ktr-Anzeige Kumulierte
      Zeitraum-Reste
Diese Option schaltet bei der
      Einstellung mit dem Wert „Ja“ auf den Zeitraummasken des
      Kontraktpfleg
[...]


---

## Kontrakteinstellungen(SPA 901)

Kontrakteinstellungen(SPA 901)
In diesem Steuerparameter können Optionen für die
Kontraktverwaltung gepflegt werden.
Zur Einstellung stehen verschiedene Typen zur
Verfügung.
Typ
Name
Wert
1
Kontraktdatum nicht in der
      Zukunft
Mit
      der Einstellung „1“ darf bei der Anlage / Bearbeitung eines Kontrakts das
      Kontraktdatum nicht in der Zukunft liegen.

---

## Kontrakterestmengenberechnung ohne Aufträge/Bestellungen (SPA 960)

Kontrakterestmengenberechnung ohne Aufträge/Bestellungen (SPA 960)
Die Restmengendarstellung wird entweder ohne die
Aufträge oder mit Aufträgen (bzw. Bestellungen) abgewickelt.

---

## Verhalten bei Fehlerhaften Rohwarengruppen Zuordnung im Kontrakt(SPA 977)

Verhalten bei Fehlerhaften Rohwarengruppen Zuordnung im Kontrakt(SPA
977)
Verhalten bei falscher Rohwarengruppenzuordnung im
Kontrakt, wenn bei der Rohwarenbelegerzeugung aus der Waage festgestellt wird,
dass die die Rohwarengruppe des Kontrakts nicht zum Artikel passt.
Verhalten
Bedeutung
Meldung ausgeben
Mit
      dieser Einstellung wird eine Meldung bei der Belegerzeugung ausgegeben und
      das Erstellen der Rohwarenbeleges wird unterbunden.
Überschreiben der Rohwarengruppe im
      Kontrakt
Mit
      dieser Einstellung wird die Rohwarengruppe für den Artikel im Kontrakt mit
      der Rohwarengruppe des Artikels überschrieben.

---

## Vertreterabrechnung

Vertreterabrechnung

---

## Auswertungs-Sortier-Definition

Auswertungs-Sortier-Definition
Hauptmenü
Rohwarenabrechnung
Excel-Kommunikation
RW-Ausw.-Sort.Definition
Direktsprung
[RWAS]
Mit diesem Modul werden Schemata zur
Rohware-Excel-Auswertung angelegt, die die Reihenfolge der Datenzeilen und die
Teilsummenauslösungskriterien angibt sowie die Vorbelegung der
Selektionskriterien bestimmt.
In diesem Eingabebildschirm können die nachfolgenden
Felder bearbeitet werden.
Nummer
laufende Nummer, diese kann im Neu-Fall manuell
überschrieben werden
Bezeichnung
Ausführliche Bezeichnung des
Sortier-/Selektions-Schemas.
Rang
Gruppier-Reihenfolge der Liste. In diesem Beispiel
erfolgt die übergeordnete Gruppierung nach Artikelnummer. Erfolgt ein Wechsel
der Artikelnummer, so wird bei der Excel-Auswertung eine Teilergebnis-Bildung
ausgeführt, wenn ein Gruppensummenkennzeichen angegeben ist. Die untergeordneten
Gruppenwechsel werden dann auch mit ausgeführt und die entsprechenden Summen
gebildet. Eine Auswahl mit
F3
ist möglich.
Gruppe
Das Feld, nach dem innerhalb der Liste
gruppiert/sortiert werden soll; dies muss nicht zwingend ein Feld sein, das ein
Summenkennzeichen trägt.. So bedeutet ein Wechsel der Liefernummer in diesem
Beispiel, dass die Sortierung innerhalb der anderen Gruppierungen nach der
Liefernummer erfolgt. Es erfolgt aber keine Teilergebnis-Bildung beim Wechsel
der Liefernummer. Eine Auswahl mit
F3
ist möglich.
Selektion: von bis
Für die ausgewählten Felder wird hier die Vorbelegung
für die Selektion der Auswertungen festgelegt.
Gruppensumme
Hier kann ausgewählt werden, ob bei Wechsel des
Feldwertes bei der Erstellung von Excel-Auswertungen eine Teilergebnisbildung
ausgelöst werden soll oder nicht, sowie bei unterschiedlichen Feldtypen, wie
z.B. Datumsfelder, ob diese bei  Tages-, Wochen- oder Monatswechsel
gebildet werden soll, wobei die Auswahlmöglichkeiten je nach Feld-Typ
unterschiedlich sein können. In der Regel wird es sich hierbei jedoch um Summe
oder - (keine Summe) handeln. Eine Auswahl mi
[...]


---

## Allgemein (Kontrakt-Hedging)

Allgemein (Kontrakt-Hedging)
Hedge – vom englischen Verb „to hedge“ = absichern –
bedeutet im Zusammenhang mit Kontrakten die Absicherung des Währungsrisikos
durch ein Gegengeschäft, das in diesem Fall ein Broker abwickelt. Zum Zweck der
Abwicklung wird die Order in eine Order-Datei geschrieben. Diese wird bei
Erfüllung entsprechender Bedingungen automatisch geschrieben.
Der Kontrakt wird bis zum Eingang der Rückmeldung vom
Broker in Form einer Return-Datei als gesperrt gekennzeichnet.

---

## Anschrift

Anschrift
Üblicherweise entspricht die Kontraktanschrift der
Kundenanschrift. Für Spezialfälle kann hier jedoch auch eine manuelle Anschrift
eingegeben werden, die als Anschrift verwendet wird.

---

## Auswertungen / Listen über Kontrakte

Auswertungen / Listen über Kontrakte

---

## Barcode/Bilderdruck-Druckparameter

Barcode/Bilderdruck-Druckparameter
Die "DruckParameter"
stellen eine Begrifflichkeit im Zusammenhang mit dem Aeins-Druck (Vorgangs-
Kontrakt-Druck etc.) dar und ermöglichen auf ausgewählte Entitäten im
Zusammenhang mit Drucker-Eigenschaften zuzugreifen.
Im Rahmen einer
privaten Barcode- bzw. Bilderdruck-Procedure können diese Druckparameter
übergeben und ausgewertet werden.
Anmerkung: Die
Entitätsaufzählung ist vollzählig, es sollte deswegen aber nicht abgeleitet
werden das auch jede Entität speziell in diesem Beritt sinnvoll bzw. notwendig
ist. Als Beispiel sei die "FA_Id" genannt. Die kann zum Zeitpunkt des Druckes
noch nicht bekannt sein, da die Archivierung erst danach
stattfindet.
Hinweis:
Gross-Kleinschrift ist nicht relevant.
Entität
Beispiel
DruckerNummer
6254
DruSchacht
0
PreScript
FormularId
740
AnzeigeDruckvorgang
false
KeineArchvierung
false
NurArchvieren
false
KeinDruckMerker
false
ZeigSQLKFehler
false
InterneImageErzeugung
false
FA_Id
0
FormularVerpostbar
false
Vorschau
false
DruckerQueue
Microsoft Print to PDF
DruckerKeinArchiv
false
DruckerSendenAn
false
DruckerNulldrucker
true
DruckerSendenAnProc
IstLieblingsdrucker
true
LieblingsdruckerMakroScript
Nacharchivierungs_Modus
false
LieblingsdruckerNurDrucken
0
Folgender Beispiel-Aufruf stellt die „Druckparameter“
einer darauf vorbereiteten privaten Prozedure zur Verfügung:
p_barcode_druckparam_beispiel('{druckparam}')
Beispiel für “Druckparam”
CREATE PROCEDURE
p_barcode_druckparam_beispiel( in in_druckparam long varchar )
Result
(
code long varchar,
codetype long varchar
)
Begin
declare dc_code long varchar;
declare dc_codetype long varchar;
CALL sp_parse_json( 'dc_druckparam',
in_druckparam );
set dc_codetype = 'qrcode';
set dc_code = dc_druckparam.DruckerQueue;
select dc_code as code, dc_codetype as
codetype;
End

---

## Barcode/Bilderdruck-Datenquelle

Barcode/Bilderdruck-Datenquelle
Die "Datenquelle"
ist eine Begrifflichkeit im Zusammenhang mit dem Referenz-ERP-Druck (Vorgangsdruck,
Kontrakt-Druck etc.) und stellt dort die Möglichkeit auf bestimmte Entitäten
zuzugreifen.
Im Rahmen einer
privaten Barcode- bzw. Bilderdruck-Prozedure kann die Datenquelle übergeben und
ausgewertet werden.
Anmerkung: Die
Entitätsaufzählung ist vollzählig, es sollte deswegen nicht erwartet werden,
dass auch jede Entität speziell in diesem Beritt sinnvoll bzw. notwendig ist.
Hinweis:
Gross-Kleinschrift ist nicht relevant.
Entität
Vorgangsdruck
Kontraktdruck
DQBelegQuelle
z.B.
      1
z.B.
      12
DQBelegTyp
Vorgangsklasse. Z.B. 700
1
DQBelegId
v_id
Die
      interne, für den Anwender unsichtbare, Identifikation des Kontraktes für
      sämtliche externen Verweise (
KtrId
).
DQBelegNummer
v_numnummer
Die
      vom Anwender vergebene, eventuell aus einem Nummernkreis gekommende,
      logische Identifikation des Kontraktes bzw. deren eindeutiger numerischer
      Teil (
KtrNummer
).
DQKundenNummer
DQSammeldruck
Kennzeichen
-
DQPDFA
-
-
DQBelegreferenz
Archiv-Referenz
DQFA_Belegreferenz
Archiv-Referenz
DQAttachment
DQV_id
-
DQFormularid
DQFormularidZ
DQV_Klassnummer
-
DQV_UKlassnummer
-
DQV_Jahrnummer
-
DQV_Unternummer
-
DQVerpostung
DQVerposter
DQBelegDatum
DQReason
DQLocation
DQContactInfo
DQFA_Druckdatum
DQFA_NeuanlageBedienerId
DQBelegTypText
z.B.
      „Rechnung windows“
DQBelegTypKlasse
z.B.
      „700“
Folgender Beispiel-Aufruf stellt die „Datenquelle“
einer darauf vorbereiteten privaten Prozedure zur Verfügung:
p_barcode_datenquelle_beispiel('{datenquelle}')
Beispiel für “Datenquelle”
CREATE PROCEDURE
p_barcode_datenquelle_beispiel( in in_datenquelle long varchar )
Result
(
code long varchar,
codetype long varchar
)
Begin
declare dc_code long varchar;
declare dc_codetype long varchar;
CALL sp_parse_json( 'dc_datenquelle',
in_datenquelle );
set dc_codetype = 'qrcode';
set dc_code = dc_datenquelle.DQBelegId;
select dc_
[...]


---

## Bedingungen zum Hedging

Bedingungen zum Hedging
Absicherungen durch Hedging sind anzuraten, wenn die
Kontraktwährung eine Fremdwährung ist.
Die Branchen-ERP-Vorgabe-Prozedur AMIC_HEDGE_GETORDERSTRING
stellt folgende Bedingungen:
Die Kontraktwährung ist eine Fremdwährung
Die Kontraktwährung hat einen Hedge-Teiler-Eintrag im
Währungsstamm, der größer als 0 ist, sowie ein Eintrag, dass die Fremdwährung
stärker als die Buchwährung ist.
In das Anwender Format af_HedgeLoca müssen gültige
Hedge Lokationen eingetragen werden.
Im Artikelstamm muss eine gültige Hedge-Lokation
angegeben werden.

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

## Bitzer Kontraktdaten

Bitzer Kontraktdaten
Folgende XML Struktur wird vom Referenz-ERP System aus mit
den Daten des Kontraktstamm gefüllt.
Die hier angefügten Qualitäten werden aus der
Bestandteil Abteilung des Artikelstamms gelesen. Min und Max Werte sind in dem
Bestandteilbereich pflegbar

---

## Waagenanlieferung

Waagenanlieferung
Um Ware in das Lagerverwaltungssystem einzubuchen
besteht die Möglichkeit, dies per Anlieferung an der Waage zu erfassen.
Folgende Einrichtungen müssen im Referenz-ERP System
vorgenommen werden
1.
Als erstes muss in der
Waage
ein
Rohwarenprofil
angelegt
werden.
2.
Es muss eine Lokalität für die Waage eingerichtet werden. Dabei ist als
Lokalitätstyp Wareneingang aus zu wählen. Es muss das Lager angegeben werden,
auf dem sich die Lokalität befindet. Auf der Registerkarte Dimension brauchen
keine Angaben gemacht werden. Auf der Registerkarte Definition muss auf jeden
Fall im Feld Waagen Vorlage die Vorlage eingetragen werden. Mit dem Schalter
Rohwarenbeleg erzeugen wird nach dem Wiegen direkt ein Rohwarenbeleg erzeugt.
Auf der Registerkarte Maschine brauchen keine Einstellungen vorgenommen
werden.
3.
Der Artikel und die Partie wird über Saatzucht Modul bestimmt. Dazu wird wie
folgt vorgegangen
3.1
Als erstes muss ein Artikel neu angelegt werden, oder es wird ein bestehender
Artikel genommen. Dieser muss auch auf dem Lager der Waage vorhanden sein.
3.2
In dem Saatgut des Artikels muss noch die Fruchtart und die Sorte eingetragen
werden.
3.3
Danach muss ein Vermehrungsvertrag unter SAATV angelegt werden. Nach dem
Vermehrungsvertrag angelegt worden ist. Muss jetzt noch der Schlag zugeordnet
werden. Nach dem der Schlag angelegt worden ist muss dann noch bei der
Schlagzuordnung auf übernehmen geklickt werden. Danach im Vermehrungsvertrag auf
den Schlag ein Doppelklick machen. Jetzt muss in der Feldbearbeitungsmaske die
Laufende Nummer eingegeben werden. In das Feld Partie kann eine Nummer
hinterlegt werden, die beim Erfassen des Waagenvorganges als Partiebezeichnung
genommen wird. Ist das Feld mit der Partie nicht befüllt, so wird die Laufende
Nummer als Partiebezeichnung genommen.

---

## Einzel-/Gesamtmengen

Einzel-/Gesamtmengen
Einzel-/Gesamtmengen
Frei
      Freimengenkontrakt
d.h.
      es werden keine festen Gesamtmengen oder Einzelmengen vereinbart. Der
      Kontrakt dient vor allem zur Festlegung von Preisabsprachen in einem
      Zeitraum.
Gesamtmengenkontrakt
d.h., der Kontrakt wird über eine
      gewisse Menge der angegebenen Warenpositionen abgeschlossen, wobei die
      Einzelmengen der Positionen nicht festgelegt sind. Festgelegt werden in
      der Regel jedoch die Preise der einzelnen Warenpositionen. Diese sehr
      übliche Kontraktart bringt für die Engagementplanung Nachteile mit sich,
      da vertraglich nicht geregelt ist, was exakt verkauft wurde.
Einzelmengenkontrakt
d.h.
      es werden für die einzelnen Warenpositionen Abnahmemengen spezifiziert,
      die Gesamtmenge wird automatisch als Summe der Einzelmengen
      berechnet.
Mengen-/Wertkontrakt
d.h.
      Kontrakte können sowohl über zu liefernde Mengen von Waren abgeschlossen
      und verwaltet werden, als auch über Werte. Die Bestimmung erfolgt in
      diesem Feld.

---

## Vorbereitende Maßnahmen

Vorbereitende Maßnahmen
Zur Normierung der Mengeneinheiten sollte der
Steuerparameter 815
gesetzt sein, wenn
nicht sowieso schon die Verarbeitung komplett in Tonnen abgewickelt wird.
Kontrakte, die nicht mehr aktiv sind, müssen mit der
Kontrakterledigung - Funktion erledigt werden.
Die zu handelnden Artikel sollte in den korrekten
„Fruchtart“ Warengruppen eingeordnet sein, am besten passend zu den an der
Warenbörse gehandelten Gruppe.
In jedem Kontrakt sollte das „Pricing“ Kennzeichen
korrekt eingetragen sein.

---

## Import von Hedge-Order-Returns

Import von Hedge-Order-Returns
Meldet der Broker den Abschluss des
Sicherungsgeschäfts mit einer Return-Datei zurück, so kann diese automatisiert
ausgewertet werden. Dazu rufen Sie aus der Kontraktliste die Funktion
Hedge Datei Import
auf und starten Sie den
Import.
Aus dem im
Einrichterparameter
angegebenen Verzeichnis werden
die Dateien gelesen und ins Formulararchiv mit der Referenz auf diesen Kontrakt
gespeichert.
Die Datei wird danach aus dem Verzeichnis gelöscht.

---

## Kontrakt

Kontrakt
Hauptmenü
Kontraktverwaltung

---

## Positionreport

Positionreport
Hauptmenü
Kontraktverwaltung
Kontraktinformation

---

## Positionreport (ratierlich)

Positionreport  (ratierlich)
Hauptmenü
Kontraktverwaltung
Kontraktinformation

---

## Kontrakt „Kontraktbewertung zum Marktpreis“

Kontrakt „Kontraktbewertung zum Marktpreis“
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
Neben den Varianten „Kontrakte (KBM)“ und „Kontrakte
(KBM) festgeschrieben“, stehen weitere Informationen im
Paritätsstamm
und den dazugehörigen zur
Verfügung.

---

## Kontraktabschreibung

Kontraktabschreibung

---

## Kontrakt „Mahnung“

Kontrakt „Mahnung“
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
In der Kontraktverwaltung besteht die Möglichkeit,
dass für Kontrakte, deren Mengenzeiträume abgelaufen sind, eine sogenannte
Kontraktmahnung gedruckt werden kann.
Hierzu gibt es zuerst eine „Kontraktmahnung
Vorschlagsliste“. In dieser werden nur Kontrakte angezeigt, die unerledigt,
ungelöscht und mindestens ein Mengenzeitraum des Kontraktes zum „Stichtag“ eine
offene Restmenge > 0 aufweist.
Filtereinstellungen
Kontraktnummer:
Hier
      können die Kontrakte durch die entsprechende Kontraktnummer eingegrenzt
      werden.
Kontraktdatum
Hier
      können die Kontrakte durch die Kontraktgültig eingegrenzt werden.
MeZR-Stichtag
Stichtag, zu dem ein Mengenzeitraum
      bereits überschritten und nicht komplett bedient wurde.
Stichtag
      15.06.2017
Ktr: 1
Gültigkeit: 01.01.2017 – 30.06.2017
      /  100T offen
Ktr: 2
Gültigkeit: 01.01.2017 –
      30.03.2017  /   50 T offen
Ktr: 2
Gültigkeit: 01.04.2017 –
      30.06.2017  /   50 T offen
Ktr: 3
Gültigkeit: 01.01.2017 – 31.05.2017
      /    30 T offen
Es
      würde nur der Kontrakt Nr.: 2 und 3 in der Mahnvorschlagsliste erscheinen,
      da diese einen Mengenzeitraum mit offener Restmenge <
Stichtag
besitzen.
Kunde
Hier
      können Kontrakte durch die Kundennummer eingegrenzt werden.

---

## Felder der Standard-Kontrakt-Auswahlliste (Kontrakte)

Felder der Standard-Kontrakt-Auswahlliste
(Kontrakte)
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
Variante:
Kontrakte
Nachfolgend werden einige Felder der
Kontraktstamm-Standardauswahlliste beschrieben:
Variante:
  Kontrakte
Kontraktklasse
Kontraktklasse des
      Kontrakts
Kontraktunterklasse
Kontraktunterklasse des
      Kontrakts
Nummer
Kontraktnummer
Bezeichnung
Kontraktbezeichnung
Artikelnummer
Die
      Nummer eines Artikels der Kontraktartikel
Weitere Artikel
Liste der Nummern der gegebenenfalls
      vorhandenen weiteren Artikel des Kontrakts
Pricing
Pricing-Angabe eines
      Kontraktartikels
Sollmenge
Summe aller Zeitraum-Sollmengen des
      Kontrakts
Waagemenge
Summe der per Kontraktzuordnung in
      der Onlinewaage zugordneten Mengen zum Kontrakt
Restmenge
Summe aller Zeitraum-Restmengen des
      Kontrakts
Zu beachten:
Steuerungsparameter zur Berücksichtigung
      von Restmengen erledigter Kontrakte
gebuchte Menge
Summe aller gebuchten Mengen des
      Kontrakts
Mengeneinheit Menge
Mengeneinheit der
      Mengendarstellungen
Kontraktpreis
Der
      angegeben Preis im Kontrakt
Mengeneinheit Preis
Mengeneinheit der
      Preisdarstellungen
geliefert
Summe aller gelieferten Mengen des
      Kontrakts
disponiert
Summe aller disponierten Mengen des
      Kontrakts
Hauptkunde
Nummer des Hauptkunden der dem
      Kontrakt zugeordneten
Kontraktgruppe
nebst dessen
      Bezeichnung
Staat
ISO-Bezeichnung des Staats der
      Kontrakt-Versandanschrift beziehungsweise Haupanschrift
Ort
Ort
      der Kontrakt-Versandanschrift beziehungsweise Haupanschrift
Ernte
Das
      dem Kontrakt zugeordnete Erntejahr
Start
Das
      Startdatum der Gültigkeit des Kontrakts
Ende
Das
      reguläre Enddatum Gültigkeit des Kontrakts
Disp. Gruppe
Dispositionsgruppe des
      Kontrakts
beteiligte Kunden
Liste der Kundennummern der der
      Kontraktgruppe zugeordneten Kunden
Bestätigung
Druckkennzeichen der
      Kontraktbestä
[...]


---

## Kontraktarten

Kontraktarten

---

## Kontraktartikel

Kontraktartikel
Die Verwaltung von Kontraktartikeln erfolgt auf zwei
Masken. Zum einen handelt es sich um die Anzeigemaske aller bisher zugeordneten
Artikel und zum anderen um die Artikelmaske, in der die Artikel erfasst und
bearbeitet werden.
Von der Anzeigemaske lassen sich weitere Masken, wie
z.B. die „Bewegungen“, „Mengen“ und „Preise“ aufrufen. Von hier aus kann man
auch die zugeordneten Artikel löschen.

---

## Kontraktübersicht

Kontraktübersicht
Hauptmenü
Kontraktverwaltung
Kontraktübersicht
oder Direktsprung
[KTI]

---

## Kontraktdispositionskennzeichen

Kontraktdispositionskennzeichen
Hauptmenü
Kontraktverwaltung
Kontraktdispositionskennzeichen
oder Direktsprung
[KTDI]
Wahlweise ein ganzer Kontrakt oder aber eine Partie
eines Ein- oder Verkaufskontraktes kann hier einem „Auszifferungskennzeichen“
zugeordnet werden, über das, unabhängig von der Partie des Gesamtsystems, Ein-
und Verkaufskontrakte bzw. ihre Teilmengen einander gegenübergestellt werden
können.
Ist der ganze Kontrakt einem Dispositionskennzeichen
zugeordnet, so auch alle seine Partien.
Mittels eines Steuerungsparameters (Automatisches
Dispokennzeichen bei Einkaufskontrakten) kann aktiviert werden, dass beim
Erfassen von Einkaufskontrakten automatisch Dispo-Kennzeichen mit identischer
Nummerierung erzeugt werden, wenn das dann entsprechend vorbelegte Kennzeichen
nicht abweichend überschrieben wird. Die Kontraktbezeichnung wird mit
übernommen.
Somit ist es möglich, sich die Arbeit zu erleichtern,
wenn generell jeder Einkaufskontrakt einer Anzahl von Verkaufskontrakten
zugeordnet werden soll, denn die Zuordnung erfolgt direkt mit der Kontraktnummer
des Einkaufskontrakts.

---

## Kontraktgruppen

Kontraktgruppen
Hauptmenü
Kontraktverwaltung
Kontraktgruppen
oder Direktsprung
[KTGR]
Eine Kontraktgruppe ist ein Personenkreis, der
gemeinsam aus den der Kontraktgruppe zugeordneten Kontrakten mit den dort
vereinbarten Konditionen bedient wird.
Im Normalfall besteht die Kontraktgruppe aus genau
einem Kunden/Lieferanten, dessen Nummer wird hier eingegeben. Ein
Kunde/Lieferant kann in mehreren Kontraktgruppen enthalten sein.
Wird hier jedoch Bezug auf eine Kontraktgruppe mit
mehreren Kunden genommen, so wird mit Angabe der Kontraktgruppe der „Hauptkunde“
dieser Gruppe als Information im Feld darunter angezeigt. Bei einem Kunden ist
er es natürlich selber.
Feld
Beschreibung
Kontraktklasse
Nummer der Kontraktklasse für die
      die Kontraktgruppe gültig sein soll.
Nummer
Nummer der Kontraktgruppe
      (üblicherweise die Nummer des Hauptkunden)
Bezeichnung
Bezeichnung der Kontraktgruppe
      (üblicherweise der Name des Hauptkunden)
Matchcode
Matchcode der
      Kontraktgruppe
Einzelgruppe
Bei
      „Ja“ kann nur ein Kunde in die Datentabelle Kunde eingetragen werden. Der
      Kunde ist dann auch automatisch der Hauptkunden.
Bei
      „Nein“ können in die Datentabelle Kunde mehrere Kunden eingetragen
      werden.
Konzern
Konzern dieser
      Kontraktgruppe
Neben den Kopffeldern der Kontraktgruppe kann dann
noch die Datentabelle Kunden gepflegt werden.
Feld
Beschreibung
Lfd.
      Nr.
Die
      laufende Nummer des Kunden in der Kontraktgruppe. Dient zur Sortierung.
      Jede Nummer darf nur einmal vorkommen.
Nummer
Nummer des Kunden /
      Lieferanten
Hauptkunde
Bei
      „Ja“ gilt der Kunde / Lieferant der Zeile als Hauptkunde der
      Kontraktgruppe. Als Hauptkunde darf nur ein Kunde in der Liste markiert
      werden.

---

## Kontraktgruppe

Kontraktgruppe
Eine Kontraktgruppe ist ein Personenkreis, der
gemeinsam aus den der Kontraktgruppe zugeordneten Kontrakten mit den dort
vereinbarten Konditionen bedient wird.
Wird hier jedoch Bezug auf eine Kontraktgruppe mit
mehreren Kunden genommen, so wird mit Angabe der Kontraktgruppe der “Hauptkunde”
dieser Gruppe als Information im Feld darunter angezeigt. Bei einem Kunden ist
er es natürlich selber.

---

## Kontrakt-Hedging

Kontrakt-Hedging

---

## Historie

Historie
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
Oben auf der Maske zur Erfassung der Stammdaten
befindet sich ein Reiter Historie. Hier wird unter bestimmten Voraussetzungen
aufgelistet, was von wem geändert wurde. Um die Historie zu aktivieren, müssen
folgende Einstellungen gemacht werden:
•
Unter Formularzuordnung / Vorgangsunterklassen (Direktsprung
[FRZ]
) muss auf dem Reiter „Allgemein“ die
Kontraktexportprozedur
eingetragen werden
•
Unter Formularzuordnung / Vorgangsunterklassen (Direktsprung
[FRZ]
)  muss auf dem Reiter „Partie“ der
Schalter „Export im Tagebuch“ auf
Ja
gesetzt werden.
•
Die Unterklasse, die im Kontrakt verwendet wird, muss unter
[FRZ]
berücksichtigt werden.
•
Im Kontraktstammpfleger muss der Einrichterparameter „Kontrakt zusätzlich
auch als XML speichern“ auf
Ja
stehen.

---

## Kontraktstammdaten

Kontraktstammdaten
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
Die Kontraktstammdaten enthalten (z.T. aufbauend auf
anderen Informationen, wie Paritäten, Kontraktgruppen, etc.) alle wichtigen
Informationen zur Verwaltung der Vereinbarungen und stellen diese der
Vorgangsbearbeitung zur Verfügung.
Die Erklärung zu den Einrichterparametern finden sie
auf folgender Seite. (
Kontraktstamm
(EPA KTRSTAM)
)
Die Maske besteht aus den folgenden Bereichen
Kopfdaten
Stammdaten 1
Stammdaten 2
Stammdaten 3
Und diesen Funktionen
Angebot übernehmen
(K+MK) kopieren
Artikel festlegen
Anschrift
Ausbuchen Fremdware/-lager SF5
Kontraktpartie
Textbausteine
Zeiträume festlegen
Als Erklärung dient
Kontrakt-Arten

---

## Kontraktliste

Kontraktliste
Hauptmenü
Kontraktverwaltung
Kontraktliste
oder Direktsprung
[KTL]

---

## Kontraktpartie

Kontraktpartie
Ein Kontrakt kann zum Zweck der Erstellung von
Andienungen bzw. Freistellungen in Kontraktpartien aufgeteilt werden. Eine
solche ist eine Teil- oder Obermenge des oder mehrerer Kontrakte, die im Stück
geliefert (bzw. abgerufen) werden soll — eine Liefereinheit sozusagen.

---

## Kontraktparitätenstamm

Kontraktparitätenstamm
Hauptmenü
Kontraktverwaltung
Paritätsstammdaten
oder Direktsprung
[PARI]
Der Begriff der Parität umschreibt die Kombination
eines (vereinbarten oder tatsächlichen) Übergabeortes einer Ware mit bestimmten
Übergabekonditionen.
Es kann sich aber auch um einen fixen
Lieferort/Übergabeort handeln. Dies wird im Großhandel genutzt, um Kontrakte mit
verschiedenen Übergabeorten kostenmäßig auf einer gemeinsamen Basis zu
vergleichen.
Dieselbe Ware kann, durch Parität beeinflusst, bei
gleichem Preis als verschieden günstig angesehen werden, da der Übergabeort
natürlich die Nebenkosten beeinflusst. Außerdem gehen Konditionen (Fracht,
Versicherung) in die Parität ein.
Kontrakte werden üblicherweise mit einer festgelegten
Parität vereinbart, wobei andere tatsächliche Paritäten unter Umständen
Zu-Abschläge auslösen können.
Folgende Felder stehen auf der Maske zur
Verfügung.
Feld
Beschreibung
Paritätsnummer
Matchcode
Bezeichnung
Paritätstyp
Zugeordnetes Lager
Kalk. Kostensatz
Je
      Anzahl Mengeneinheiten
Mengeneinheiten
      Kostensatz

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

## Kontraktvarianten

Kontraktvarianten
Hauptmenü
Kontraktverwaltung
Kontraktvarianten
oder Direktsprung
[KTVA]
Als Kontrakt-Variante wird die Steuerung für die
Druck-Aufbereitung optisch identisch aufzubereitender Kontrakte bezeichnet.
Insbesondere ergibt sich aus ihr die Reihenfolge der
verschiedenen darzustellenden Daten (Relationen), die einen Kontrakt
beschreiben.
Kontraktvarianten können einem Kontrakt für die
Aufgaben
•
Kontraktdruck
•
Kontrakterledigungsschreiben
•
Kontraktstorno
zugeordnet werden. Dabei kann es sich (jeweils) um
eine Variante für alle Kontrakte handeln, in diesem Fall ist z.B. das
Kontraktbestätigungsschreiben für alle Kontrakte gleich, oder man unterscheidet
Kontrakte inhaltlich (z.B. soll das Bestätigungsschreiben für einen
Futtermittelkontrakt anders aussehen als für einen Futtermischungskontrakt). Im
letzten Fall würde man dann mindestens zwei Varianten anlegen, die den
unterschiedlichen Anforderungen gerecht würden. Mit der Einbindung der
Variantennummer in die Kontraktstammdaten bekommt der Kontrakt also zusätzliche
inhaltliche Bedeutung. Um diese Bedeutung auch bei der Neuerfassung von
Kontrakten sicherzustellen, empfiehlt es sich, Musterkontrakte für jede Variante
anzulegen.
Zu beachten ist, dass Varianten nur in Zusammenhang
mit der eigentlichen Formulareinrichtung gesehen werden können.
Der optische Aufbau eines Schreibens wird in zwei
Programmbereichen eingeteilt:
1.
Im Formulareinrichtungsprogramm wird die generelle Optik des Formulars bestimmt.
Hierbei handelt es sich um die quasi unveränderlichen Elemente des
Kontraktdrucks, z.B. die Position der Anschrift, des Datums, aber auch des
generellen Ausdrucks von Qualitäten, Paritäten, etc.
2.
Die von Kontrakt zu Kontrakt unterschiedlichen Merkmale, wie vereinbarte
Qualitäten, Paritäten, etc. werden hier, in den Varianten, erfasst. Außerdem
wird die Reihenfolge des Ausdrucks bestimmt.
Folgende Felder stehen auf der Erfassungsmaske zur
Verfügung.
Feld
Beschreibung
Kontrakt-Vari
[...]


---

## Kontraktausweichliste

Kontraktaus
weichliste
Hauptmenü
Kontraktverwaltung
Kontraktausweichliste
oder Direktsprung
[KTAU]
Die Kontrakt-Ausweichliste dient dazu, dem Kunden, der
einen Kontrakt über eine Auswahl an Artikeln abgeschlossen hat, die Möglichkeit
zu geben, ähnliche Artikel, die nicht explizit im Kontrakt erwähnt worden sind,
anstelle der aufgeführten Artikel zu vergleichbaren Konditionen abzunehmen. Die
Ausweichartikel werden in einer (für den Kunden unsichtbaren) Liste geführt,
ohne dass sie in jedem Kontrakt explizit eingetragen sein müssten.
Folgende Felder stehen zur Verfügung.
Feld
Beschreibung
Auswahllistennummer
Angabe der Listennummer, unter der
      die Auswahl gespeichert werden soll.
Bezeichnung
Vergabe einer
      Bezeichnung
Fixpreis-Kennzeichen
Wenn
      ja, werden für die Artikel dieser Liste feste Preise vergeben, die bei der
      Kontraktansprache ziehen.
Zu-/Abschläge
Kennzeichen, ob die Zu- und
      Abschläge der Kontraktverwaltung auch bei den Listenartikeln gelten
      sollen.
Preise vom 1. Artikel
Kennzeichen, ob der Preis des ersten
      Kontraktartikels als Grundlage für die Preisermittlung des
      Ausweichartikels genommen werden soll.
Zu-
      und Abschlag auf Preis
Zu-
      oder Abschlag auf den ermittelten Einzelpreis für alle Ausweichartikel.
      Nur sinnvoll bei Preisermittlung aus Listenpreis (kein Schalter
      angeknipst) oder über den ersten Kontraktartikel.
Artikel
Über die Funktion
Artikel
wird in die Ausweichartikelmaske
gewechselt. Hier werden alle Artikel der Ausweichliste angezeigt. Neuanlage,
Änderung und Löschung der Artikel sind in dieser Maske möglich.

---

## Änderungsprotokoll

Änderungsprotokoll
Hauptmenü
Kontraktverwaltung
Kontraktstammdaten
oder Direktsprung
[KTR]
Variante:
Kontraktprotokoll
Änderungen von Sollmengen, Sollwerten und
Zeitraumgrenzen werden in einem Änderungsprotokoll dokumentiert, das in dieser
Auswahlvariante eingesehen werden kann.
Feld
Beschreibung
Änderungsdatum
Datum und Uhrzeit der
      Änderung
Bediener
Das
      Bedienerkürzel gibt Auskunft darüber, wer die Änderung durchgeführt
      hat.
Kontraktklasse
Die
      Bezeichnung der Kontraktklasse des Kontrakts.
Unterklasse
Die
      Kontrakt-Unterklasse des Kontrakts.
Nummer
Die
      Kontraktnummer wird hier ausgewiesen.
Kontraktbezeichnung
Die
      Bezeichnung des Kontrakts ist dieser Spalte zu entnehmen.
Zeitraum
Der
      Beginn des geänderten Zeitraums.
Änderung
Die
      erfolgte Änderung wird in Textform dargestellt.
Artikelnummer
Die
      Artikelnummer einer geänderten Artikelposition.
Lager
Die
      Lagernummer einer geänderten Artikelposition.
Hauptkunde
Die
      Kunden-/Lieferantennummer des Hauptkunden/-lieferanten des Kontrakts laut
      zugehöriger Kontraktgruppe.
Kundenname
Der
      Name des Hauptkunden/-lieferanten des Kontrakts laut zugehöriger
      Kontraktgruppe.
beteiligte Kunden
Hier
      wird eine Liste aller  Kunden-/Lieferantennummern der dem Kontrakt
      zugeordneten Kontraktgruppe ausgewiesen.

---

## Artikelmaske

Artikelmaske
Auf dieser Maske lassen sich die Artikel für den
Kontrakt bearbeiten und einfügen. Ein Artikel kann dabei auch mehrfach in einem
Kontrakt geführt werden, z.B., um unterschiedliche Qualitäten eines Artikels mit
verschiedenen Preisen versehen zu können. Beim Fakturieren werden dann alle
Alternativen, diesen Artikel und Kunden betreffend, angezeigt.
Des Weiteren können auf dieser Maske individuelle
Felder über das „Referenz-ERP Informationssystem (AIS)“ zugeordnet werden. Beim
Einrichten des AIS müssen jedoch einige Besonderheiten beachtet werden. (siehe
dazu „
Kontraktartikel (AIS)
“)
Für die Artikelmaske stehen folgende Felder zur
Verfügung, nach dem Speichern der Daten wird die Maske verlassen und zurück zur
Anzeigemaske gesprungen.
Feld
Beschreibung
Laufende Nummer im
      Kontrakt
Vorgeschlagen wird die nächste freie
      Nummer entsprechend der Erfassungsreihenfolge. Diese Nummer steuert die
      Reihenfolge der Warenpositionen im Ausdruck von Listen.
Lagernummer
Hier
      kann die Lagernummer des Artikels eingegeben werden. Dieses Feld ist nur
      aktiv, wenn der Kontrakt lagerspezifisch ist oder das Lagerspezifisch Feld
      aktiviert wurde.
Artikelnummer
Artikelnummer der
      Artikelposition
Lagerspezifisch
Diese Feld ist nur beim ersten
      Artikel aktiv und wenn der Kontrakt nicht lagerspezifisch ist. Wird das
      Feld aktiviert, erscheint das Lagernummernfeld und die Itembox für
      lagerspezifische Artikel wird auf dem Artikelnummernfeld
      angezeigt.
Über
      einen
Einrichterparameter
lässt sich das Feld in den Kontraktstamm übernehmen.
Rohwarengruppe
(nur
      Rohwarekontrakte)
Dieses Feld wird bei der Auswahl des
      Artikels vorbelegt und sollte nur als Anzeigefeld dienen. Es kann jedoch
      über einen
Einrichterparameter
zum Bearbeiten
      freigeschaltet werden.
Rohwarensorte
(nur
      Rohwarekontrakte)
Hier
      kann die Rohwarensorte des Artikels angegeben werden, die Sorte wird durch

[...]


---

## Variante Kontraktbewegung mit Washout und Circle

Variante Kontraktbewegung mit Washout und Circle
Hauptmenü
Kontraktverwaltung
Kontrakt Stammdaten
oder
[KTR]
In der Variante „Kontraktbewegung mit Washout und
Circle“ werden alle Vorgänge angezeigt die an einem Washout oder Circle
beteiligt sind.
In dieser Variante kann nach Circle, Washout oder
beiden selektiert werden. Des Weiteren ist es möglich, sich die Mengenbuchungen,
Wertbuchung oder beide Buchungstypen anzuschauen.
Die Vorgänge eines Washout oder eines Circle sind über
eine
Vorgangsklammer
geklammert.
Wenn diese Variante privat abgeleitet werden soll,
muss darauf geachtet werden, dass die Funktionen
amic_func_bit_test(warenbewegung.wabewbits1, 8) für Washout und
amic_func_bit_test(warenbewegung.wabewbits1, 9) für Circle
mit in der „select“ Anweisung berücksichtigt
werden.

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

## „Kontraktbewegung zum Marktpreis“

„Kontraktbewegung zum Marktpreis“
Hauptmenü
Kontraktverwaltung
Paritätsstammdaten
oder Direktsprung
[PARI]
Die „Kontraktbewertung zum Marktpreis“ Informationen
befinden sich in den Varianten „Paritäten detailliert (KBM)“ und „Währungskurse
(KBM)“. Dort befindet sich neben den Importen der Marktpreise und der
Paritätssätze, auch die Auswertungen „Marktpreise (KBM)“ und „Paritätssatzliste
(KBM)“.
Über die Importe lassen sich die Marktpreise und die
Paritätssätze einlesen. Die Importdateien müssen sich dafür im Ordner
„Aeins\User“ befinden.
Aufbau Importdatei „Marktpreise“
Name der Datei ist „Marktpreise.xlsx“
Spalte
Feldname
Beschreibung
1
Datum
2
Kunde
3
Artikel
4
Preis
5
VE
6
Stichtag
7
Level
8
Uplift
9
Kosten
10
Profit
11
Preistyp
Beim
      Import kann hier der Preistyp angegeben werden. Standardmäßig wird dieser
      Wert auf „0“ gesetzt. Bei dem Wert „1“ handelt es sich um einen
      nachhaltigen Preis.
Aufbau Importdatei „Paritätssätze“
Name der Datei ist „ParitaetImport.xls“
Spalte
Feldname
Beschreibung
1
Stichtag
2
Gültig ab
3
Nummer
4
Satz

---

## Nachhaltigkeit in der Rohware

Nachhaltigkeit in der
Rohware
Nachhaltigkeitswerte werden
aus den eingetragenen Angaben für die
Artikel
,
Kunden/Lieferanten
,
Kontrakte
etc. auch bei der
Rohwarenerfassung ermittelt (siehe
Nachhaltigkeit
) und in den Beleg übernommen.
Sofern das Kennzeichen
Nachhaltigkeitsartikel
im Artikelstamm zur Lieferposition eines
Rohware-Belegs mit dem Wert
Ja
belegt ist, werden die
Nachhaltigkeitsdaten und deren Herkunft (Artikel, Kunde, Kontrakt, Anbaugebiet
oder manuell) zum Hauptartikel des Rohware-Belegs im oberen rechten
Bearbeitungs-Grid dargestellt.
In der Regel sollten die so ermittelten
Nachhaltigkeitsdaten bereits die zum aktuellen Beleg passenden sein. Dennoch
sind diese Daten grundsätzlich manuell bis einschließlich der ersten
Abrechnungsstufe (Abschlag oder, bei direkter Endabrechnung, Finale) änderbar.
Es ist jedoch zu beachten, dass bei Änderung von Artikel, Kunde/Lieferant oder
Kontrakt eine erneute Initialisierung stattfindet und manuelle Werte eventuell
wieder überschrieben werden. Eine Ausnahme hiervon ist in der Funktion
Schema-/Kundenänderung
zur
nachträglichen Änderung von Abrechnungsschema, Artikel und/oder Kunde/Lieferant
implementiert. Auch dort werden die Nachhaltigkeitswerte zunächst neu ermittelt
aber durch im Ursprungsbeleg manuell geänderte Werte überschrieben!
Sollen THG-/TSW-Werte als
Abrechnungspositionen in Rohwarebelegen berücksichtigt werden, so können
entsprechende Definitionen als
Qualitätsposition mit
Analysewertkopplung
eingerichtet werden. Dabei wird der Analysewert an den
gewünschten THG-/TSW-Wert der bezogenen Warenposition ‚gekoppelt‘.
Soll
der THG Wert als Qualitätsparameter mit erfasst werden, so muss in der
Einrichtung UNBEDINGT die Nummer der Bezeichnung 1501 sein, denn nur in diesem
Falle werden die in der Qualität eingetragenen Wert auch korrekt in die
Massebilanz übernommen.
In der zugrundeliegende Auswahlliste der
Rohwarenanlieferungen wird der Anbau THG Wert mit angezeigt. Weiterhin lassen
sich b
[...]


---

## Spezielle Auswahllisten

Spezielle Auswahllisten
Zusätzlich zu den normalen Auswahllisten existieren
noch spezielle Auswahllisten, welche spezielle Selektionskriterien beinhalten.
Kontraktübersicht
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Kontraktstammdaten
Direktsprung
[NAKTR]
Dies ist die normale Auswahlliste der Kontrakte. Es
gibt dort spezielle Selektionskriterien mit denen Nachhaltige Kontrakte
gefiltert werden können.
Kriterium
Beschreibung
Nachhaltigkeitstatus
Prüft, ob der Kontrakt nachhaltig
      ist oder nicht.
Kundenübersicht
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Kundenübersicht
Direktsprung
[NAKUE]
In der Auswahlliste für Kunden gibt es spezielle
Selektionskriterien, um die Kunden auszufiltern, die Probleme mit Zertifikat
oder Nachhaltigkeitseinträgen haben.
Kriterium
Beschreibung
Nachhaltigkeit ohne
      Zertifikat
Zeigt die Kunden an, die
      Nachhaltigkeitseinträge haben, die keinem Zertifikat zugeordnet sind.
      Diese können in der Kundenmaske über das Feld Auswahl einem Zertifikat
      zugeordnet werden.
Zertifikat ohne
      Nachhaltigkeit
Zeigt die Kunden an, die Zertifikate
      ohne Nachhaltigkeitseintrag haben.
Artikelübersicht
Hauptmenü
Wareneinkauf
Nachhaltigkeit
Artikelstammübersicht
Direktsprung
[NAARS]
Es gibt dort spezielle Selektionskriterien mit denen
nachhaltige Artikelstämmen gefiltert werden können.
Kriterium
Beschreibung
Nachhaltig
Auswahl nach nachhaltigen oder nicht
      nachhaltigen Artikelstämmen.

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

## Periode bearbeiten

Periode bearbeiten
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Hauptmenü
Wareneinkauf
Abschluss
Fibu Übertrag aus Ware
Direktsprung
[FIB]
Hauptmenü
Warenverkauf
Abschluss
Fibu Übertrag aus Ware
Direktsprung
[FIB]
Mit
der Funktion
Periode bearbeiten
lassen sich die Perioden von Vorgängen verändern. Dabei wird zwischen
einzelnen Belegen und Sammelbelegen unterschieden: Bei Sammelbelegen werden alle
dazugehörigen Vorgänge auf die angegebene Periode gesetzt, bei Einzelbelegen
wird dementsprechend nur ein einzelner Vorgang bearbeitet. Wenn Sammelbelege
bearbeitet werden, werden zusätzlich noch die Felder „Belege“ mit der Anzahl der
Belege und „Perioden“ mit der Liste der Perioden, die in dem Sammelbeleg
verwendet werden.
Falls eine Periode aus einem
älteren Geschäftsjahr benutzt werden soll, muss unter [DAT] das Tagesdatum
geändert werden. Das Datum muss  innerhalb des gewünschten Geschäftsjahres
aus der Vergangenheit liegen. Die gewünschte Periode muss noch im Geschäftsjahr
aktiv sein. Dann kann auf der Maske, die sich durch die Funktion
Periode bearbeiten
öffnet, mittels F3 auf
der Spalte Periode eine neue alternative Itembox mit dem Namen „Offene Perioden
vom Tagesdatum“ geöffnet werden. Diese zeigt in Abhängigkeit des gesetzten
Tagesdatum alle offenen Perioden des Geschäftsjahres. Am Ende muss unter [DAT]
das Tagesdatum auf das echte Tagesdatum zurückgesetzt werden.
Um
die Bearbeitung zu erleichtern, lassen sich mehrere Vorgänge gleichzeitig
bearbeiten. Wenn alle Vorgänge auf dieselbe Periode gesetzt werden sollen, muss
man sie bei einem Vorgang auswählen und kann mit der Funktion
Alle auf ausgewählte Periode
F8
allen Vorgängen die Periode
zuweisen.
Mit
der Funktion
Periode zurücksetzen
F7
kann man die Periode eines
Vorgangs zurücksetzen, indem das Jahr und die Periode auf 0 gesetzt werden.

---

## Registerkarte Rohware

Registerkarte Rohware
Feld
Bedeutung
Automatische Rohwaren Partie
      Anlage
Hier
      kann eingestellt werden, ob für die Rohware auch automatisch eine Partie
      angelegt werden soll.
Rohwaren Bestellung
      löschen
Hier
      kann eingestellt werden, dass bei einer Rohwarenerzeugung, gleich die
      Bestellung, wenn vorhanden für die angelieferte Rohware zu löschen. Dieses
      ist aber nur dann möglich, wenn die Bestellung nur eine Artikelposition
      beinhaltet. Das bedeutet im Beispiel. Wurde ein Container mit Getreide
      bestellt, und dieser wird geliefert, so kann aus der Waage heraus ein
      Rohwarenbeleg erzeugt werden und die ursprüngliche Bestellung wird
      storniert. Dieses wird in der Waagenvorlage eingerichtet. Dies ist auf der
      zweiten Registerkarte Vorgangerzeugen unter Rohwaren Bestellung löschen
      einzurichten.
Rohwarenlieferscheine sofort
      erzeugen
Default ist Nein.
Entscheidet man
      sich hier für Ja, dann wird beim Aufruf der Funktion
Rohwarenbeleg erzeugen
sofort
      ein Rohwarenlieferschein erzeugt. Man braucht nicht mehr in die
      Anwendungen Rohwarenbelege (Einkauf oder Verkauf) wechseln und dort die
      Funktion
Lieferungen erzeugen
aufrufen, sondern diese Funktion wird gleich mit ausgeführt. Der Status
      des Rohwarenbeleges steht dann auf erledigt.
Rohwarenbelge
sofort
drucken
Default ist Nein.
Wird
      diese Einstellung auf „ja“ gestellt, so wird nach dem erfolgreichen
      erzeugen eines Rohwarenbeleges dieser sofort ausgedruckt.
Bei Restmengenüberschreitung
      Nettomenge
aufteilen
Bei
      einer Überschreitung der Nettomenge nach Abzug der Qualitäten, wird die
      Restmenge automatisch auf einen weiteren Kontrakt geschrieben, falls
      dieser existiert.

---

## Registerkarte Prozeduren

Registerkarte Prozeduren
Lagerumbuchung / Rohwarenlieferschein
In diesem Feld kann eine private Prozedur hinterlegt
werden, die steuert, ob eine Lagerumbuchung anstelle eines Rohwarenlieferscheins
erzeugt werden soll. Diese Funktion wird benötigt, wenn die Ware eigentlich auf
Lager 99 angeliefert werden sollte, diese aber stattdessen auf Lager 7
angeliefert worden ist.
Als Übergabe Parameter wird die OWaage_Id erwartet.
Eingabe Parameter
Feldtyp
in_owaage_id
integer
Die Prozedur muss folgende Parameter
zurückliefern.
Parameter
Feldtyp
Klasse
integer
Unterklasse
integer
Ursprungslager
Integer
BuchungsTyp
integer
Planlieferdatum
date
BewertungsPreis
numeric(15,4)
Klasse
Wird die Klasse mit einer 0 zurückgegeben so wird ein
Lieferschein erstellt, wird die Klasse mit 5110 zurückgegeben, so wird die
Lagerumbuchung erstellt.
Unterklasse
Hier wird die Unterklasse der Lagerumbuchung
zurückgegeben.
Ursprungslager
Das Ursprungslager ist das Lager, auf dem eigentlich
die Ware angeliefert werden sollte. Das Ziel Lager ist das Lager aus dem Waagen
Satz.
Buchungstyp
Der Buchungstyp für die Lagerumbuchung.
•
0 für Angebot
•
1 für Auftrag
•
2 für Rechnung
Planlieferdatum
Hier kann ein spezielles Planungslieferdatum angegeben
werden bleibt dieser Parameter leer so wird das Tagesdatum genommen.
Bewertungspreis
Wird ein Bewertungspreis > 0 zurückgegeben so wird
dieser Bewertungspreis genommen. Ansonsten startet die normale Preisfindung des
Beleges.
Beispielprozedur
CREATE
PROCEDURE
p_liefer_lagerumbuch
(
in
in_owaage_id
integer
)
Result
(
Klasse
integer
,
Unterklasse
integer
,
Ursprungslager
integer
,
BuchungsTyp
integer
,
Planlieferdatum
date
,
BewertungsPreis
numeric
(
15
,
4
)
)
//
BEGIN
//
Kommentar
//
-------------------------
//
if
in_owaage_id
>
0
then
select
5110
as
Klasse
,
0
as
Unterklasse
,
666
as
Ursprungslager
,
1
as
BuchungsTyp
,
today
()
as
Planlieferdatum
,
3.5
as
BewertungsPreis
from
dummy
;
else
select
0
as
Klasse
,
0
as
Unterklasse
,
0
as
Ursprungslager
[...]


---

## Referenz

Referenz
Ein wichtiger Punkt im Hinblick auf Einführung einer
Archiv-Organisation in der Firma.
Bekanntlich werden Vorgänge, aber auch Partien,
Kontrakte, Finanzbelege etc. pp. bei Neuanlage mit einer Archiv-Referenz-Nummer
ausgestattet. Der Aufbau dieser Referenz-Nummer geschieht mit
Datenbank-Funktionen.
Von Branchen-ERP werden Standard-Datenbankfunktionen
ausgeliefert. Technisch kann man diese Funktionen so belassen, inhaltlich sollte
man es in der Mehrheit der Fälle wohl nicht und sie auf die speziellen eigenen
Gegebenheiten umrüsten.
Am Beispiel der amic_fa_ref_vorg wird das folgende
erklärt.
CREATE
FUNCTION AMIC_FA_REF_VORG
(
IN
v_KlassNummer
integer
,
IN
v_NumNummer
integer
,
IN
in_uklassnummer
integer default
0,
IN
in_jahrnummer
integer default
0,
IN
in_unternummer
integer default
0
) returns
char
(20)
BEGIN
DECLARE
fetch_fa_belegreferenz
char
(20);
select
right
('00'||mandnummer,2)
||
(
select left
(formlstbezeich,2)
from
formatlist
where
formlstkennung='af_vorgang'
and
formlstwert = v_KlassNummer )
||
right
('00000000'|| v_NumNummer,8)
||
right
('0000'||
in_jahrnummer,4)
into
fetch_fa_belegreferenz
from
mandantstamm;
return
fetch_fa_belegreferenz;
END

---

## Restmenge über Gesamtzeit

Restmenge über Gesamtzeit
Restmenge über
      Gesamtzeit
Nein
Die
      Restmenge wird immer über die jeweiligen Zeiträume geprüft.
Ja
Die
      Restmenge wird nur über den gesamten Kontraktzeitraum geprüft. Eine
      Buchung ist also unabhängig von den eingetragenen Teil-Zeiträumen möglich.

---

## Rohware Behandlung

Rohware Behandlung
Für sämtliche Rohwarenbelege gelten folgende
Bedingungen:
•
Es kann zurzeit nur eine Partie pro Position zugeordnet werden
•
Der Einstellung aus
[FRZ]
bezüglich der automatischen Verteilung werden ignoriert. Es werden die
bisherigen Einstellungen in den Rohwareparametern herangezogen

---

## Rohware-Kostengruppen für Kosten-/Vergütungssätze und -pauschalen

Rohware-Kostengruppen für
Kosten-/Vergütungssätze und -pauschalen
Hauptmenü
Rohwarenabrechnung
Kostengruppen Rohwaren
Unter diesem Menupunkt werden
die in den in
Rohwarengruppen
deklarierten und in
Abrechnungsschemata
näher definierten
Kosten- und
Vergütungspositionen
verwendeten Kosten- und Vergütungspauschalen, Kosten-
und Vergütungssätze sowie Kosten- und Vergütungsstaffeln gepflegt. Dabei sind
mehrere Pauschalen wie auch Sätze (nicht jedoch Staffeln) zu Kostengruppen
zusammenfassbar.
Der
‚Typ‘
gibt an, ob es sich bei den Kostengruppen-Werten um
‚Kosten-/Verg.pauschale‘
oder
‚Kosten-/Verg.satz‘
handelt.
Die
Kostengruppe ‚0‘
weist dabei eine
Besonderheit
auf: Alle Werte
dieser Gruppe dienen bei der Erfassung von Rohwarebelegen nur zur
Vorbelegung
und können
manuell
überschrieben werden.
Pauschalkosten-/Vergütungsbeträge
Hauptmenü
Rohwarenabrechnung
Kostengruppen Rohwaren
Variante Kosten-/Vergütungspauschalen
Ein
in einer Abrechnung heranzuziehender Pauschalwert wird per Kostengruppe und
Kostennummer sowie dem größten ‚gültig von‘-Datum, das kleiner als das
Beleg-Lieferdatum ist spezifiziert. Gesucht wird dabei zunächst mit der
Lagernummer
des Rohwarebeleges. Wird so kein Eintrag gefunden, so wird
der Betrag mit der
Lagernummer ‚0‘
bestimmt. Es müssen für andere Läger
als Lager ‚0‘ demnach nur hiervon abweichende Beträge gepflegt werden.
Einträge mit der
Nummer ‚0‘
weisen die
Besonderheit
auf, dass die Werte bei der Erfassung von
Rohwarebelegen nur zur
Vorbelegung
dienen und
manuell
überschrieben werden können. Für Pauschalen anderer Nummern gilt dieses nur,
wenn sie der Kostengruppe ‚0‘ zugeordnet sind.
Kosten-/Vergütungssätze
Hauptmenü
Rohwarenabrechnung
Kostengruppen Rohwaren
Variante Kosten-/Vergütungssätze
Ein
in einer Abrechnung heranzuziehender Kosten-/Vergütungssatz zu einer durch die
Kostendefinition näher bestimmten Menge wird per Kostengruppe und Kostennummer
sowie dem größten ‚gültig von‘-Datum, das kleiner als das Beleg-Lieferdatum ist
[...]


---

## Auswertungs-Listenfeld-Definition

Auswertungs-Listenfeld-Definition
Hauptmenü
Rohwarenabrechnung
Excel-Kommunikation
RW-Auswert.-Definition
Direktsprung
[RWAD]
Mit diesem Modul werden Schemata zur
Rohware-Excel-Auswertung angelegt, die den Zeilenaufbau von Auswertungen
bestimmen und die Behandlung der Spalten bei der Teilsummen-Bildung in Excel
festlegen.
In diesem Eingabebildschirm können die nachfolgenden
Felder bearbeitet werden.
Nummer
laufende Nummer, diese kann im Neu-Fall manuell
überschrieben werden
Bezeichnung
Ausführliche Bezeichnung des
Definitionsschemas.
Listen-Überschriften
Hier können Texte für bis zu drei Überschrift-Zeilen
für das Excel-Blatt angegeben werden.
Spalte
Laufende Nummer der Spalte.
Breite
Angaben zur Breite der Spalte und damit auch der
darstellbaren Größe der Felder sowie der Spaltenüberschrift.
Überschrift
Hier kann ein wahlfreier Text eingegeben werden, der
als Spaltenüberschrift genutzt wird.
Feldinhalt
Hier können die Felder mit
F3
ausgewählt werden, deren Werte in der Tabelle angezeigt werden sollen. Je nach
ausgewähltem Feld-Typ wird eine weitere Auswahlmöglichkeit (Warenpos. zu Ref.Nr.
bei Feld Artikelnummer etc.) erwartet.
Summenfelder
Hier kann die Behandlung der Spalte bei der
automatischen Teilsummenbildung in Excel ausgewählt werden. Eine Auswahl mit
F3
ist möglich.

---

## EK-/VK-Rohwarenauswertung

EK-/VK-Rohwarenauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
EK-Rohwarenauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
VK-Rohwarenauswertung
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report berücksichtigt Belege der ausgewählten
Stufe, auch wenn diese bereits weiterverarbeitet wurden. Nicht berücksichtigt
werden dabei stornierte Belege.
Erzeugt wird pro Beleg je eine Zeile mit den
Angaben
•
Liefernummer
•
Lieferdatum
•
Filialnummer
•
Bruttomenge 1
Dieses ist die
erfasste Liefermenge der Hauptwarenposition (Referenznummer 1) des
Belegs
•
Trockenmeng 1
Dieses
ist die verbleibende Menge der Hauptwarenposition (Referenznummer 1) nach
Anwendung der angegebenen Qualität zur Abrechnung der Feuchte
•
Nettomenge 1
Dieses ist
die verbleibende Menge der Hauptwarenposition (Referenznummer 1) nach Anwendung
aller Qualitätsabrechnungen
•
Anfangspreis 1
Dieses
ist der Preis der Hauptwarenposition (Referenznummer 1) ohne Veränderungen durch
Qualitäten
•
Endpreis 1
Dieses ist
der Preis der Hauptwarenposition (Referenznummer 1) nach Abrechnung aller
Qualitäten
•
Bruttomenge 2
Dieses ist die
erfasste oder eingestellte Liefermenge der per Referenznummer angegeben zweiten
Warenposition des Belegs
•
Nettomenge 2
Dieses ist
die verbleibende Menge der per Referenznummer angegeben zweiten Warenposition
nach Anwendung aller Qualitätsabrechnungen
•
Anfangspreis 2
Dieses
ist der Preis der per Referenznummer angegeben zweiten Warenposition ohne
Veränderungen durch Qualitäten
•
Endpreis 2
Dieses ist
der Preis der per Referenznummer angegeben zweiten Warenposition nach Abrechnung
aller Qualitäten
•
Feuchte %
Analysewert
der per Referenznummer angegeben Qualität zur Feuchtigkeitsabrechnung
•
[Ref 2.Qualität]
Analysewert der per Referenznummer angegeben 2.
Qualität, überschrieben mit dem unter
Text 2.Qualität
des Auswahlbereichs
angegebenen Text
•
Abs-Betrag
Brutto-Abschlagbetrag des Belegs
•
End-Betrag
rechnerischer Brutto-Endbetrag des Belegs
•
R
[...]


---

## EK-/VK-Trocknungskostenerlöse

EK-/VK-Trocknungskostenerlöse
Hauptmenü
Rohwarenabrechnung
Auswertungen
EK-Trocknungskostenerlöse
Hauptmenü
Rohwarenabrechnung
Auswertungen
VK-Trocknungskostenerlöse
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report summiert pro Artikelnummer und
Lagernummer von Rohware-Artikeln aus allen Rohwarenbelegen aktuellster
Abrechnungsstufe entsprechend der Selektionsangaben die
•
Nassmenge
Dieses ist die
erfasste Liefermenge der Hauptwarenposition (Referenznummer 1) des
Belegs
•
Trockenmenge
Dieses ist
die verbleibende Menge der Hauptwarenposition (Referenznummer 1) nach Anwendung
der angegebenen Qualität zur Abrechnung der Feuchte, die durch eine der im
Selektionsbereich angegebenen Qualitätstextnummern identifiziert wird
•
Trocknungskosten
Dieses
ist der Kostenbetrag der Kostenposition, die durch eine der im Selektionsbereich
angegebenen Kostentextnummern identifiziert wird
Neben den üblichen Selektionskriterien kann der
Auswertungsbereich durch die Angabe der kleinsten zu berücksichtigenden
Abrechnungsstufe
•
1
für Lieferscheine
•
2
für Abschlagbelege
•
3
für Folgeabschlagbelege
•
4
für Finalbelege
eingeschränkt werden, zum Beispiel um lediglich
bereits finalisierte Belege auszuwerten.

---

## EK-/VK-Rohwarenkontrakt-Auswertung

EK-/VK-Rohwarenkontrakt-Auswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
EK-Rohwarenkontrakt-Auswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
VK- Rohwarenkontrakt-Auswertung
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report listet zu ausgewählten Kontrakten
Rohwarekontraktbewegungen sortiert nach Kontraktgruppe, Kontraktnummer und
Lieferdatum auf. Nicht berücksichtigt werden dabei stornierte Belege sowie
Buchungen, die nicht durch Rohwarebelege erzeugt wurden.

---

## Auswertungen von Rohware-Belegen

Auswertungen von Rohware-Belegen
Referenz-ERP stellt für die Erstellung von Auswertungen auf
der Grundlage von Rohware-Belegen grundsätzlich zwei Auswertungsmethoden zur
Verfügung. Zum einen gibt es im Bereich der Listendefinitionen in der
Auswallistenvariante ‚
Rohwarenauswertungen
‘ diverse CRW-Reports,
die über zugehörige Vorlauffunktionen zur Datengewinnung verfügen. Diese
Auswertungen sind auch direkt über das Hauptmenu erreichbar.
Eine andere Methode der Auswertung von Rohware-Belegen
stellt die variable
Rohware-Excel-Auswertung
dar. Hier können
individuell gestaltbare Excel-Blätter mit Teilergebnis-Bildungen bis zur 5.
Stufe oder entsprechende Ergebnisse in Auswahllisten-Form erzeugt werden.

---

## RW-CRW-Auswertungen

RW-CRW-Auswertungen
Hauptmenü
Rohwarenabrechnung
Auswertungen
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Im Bereich der Listendefinitionen in der
Auswallistenvariante ‚
Rohwarenauswertungen
‘ stehen diverse
CRW-Reports, die mit zugehörige Vorlauffunktionen zur Datengewinnung verknüpft
sind, zur Verfügung. Die einzelnen Auswertungen sind jeweils auch direkt über
das Hauptmenu im Bereich
‚Rohwarenabrechnung‘
unter der Abteilung
‚Auswertungen‘
zu erreichen.

---

## EK-/VK-Qualitätsauswertung

EK-/VK-Qualitätsauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
EK-Qualitätsauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
VK-Qualitätsauswertung
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Der hier zu erstellende Report berücksichtigt Belege
der jeweils aktuellsten Stufe (Lieferschein, Abschlag, Folgeabschlag, Finale)
eines ausgewählten Artikels mit einem ausgewählten Lager und stellt zu einer per
Referenznummer ausgewählten Qualität die Summen der Trockenmengen der Belege
dar, die zu dem jeweiligen Analysewert der Auswertungs-Qualität ermittelt
werden. Die darzustellenden Analysewerte werden in Schritten zu 0,1 Einheiten
wachsend dargestellt. Dabei wird als Trockenmenge  eines Belegs jeweils die
verbleibende Menge nach Anwendung der angegebenden Qualität zur Abrechnung der
Feuchte herangezogen. Zusäztlich wird nach jeweils 5 Qualitätswertschritten die
Trockenmengensumme des Fünfer-Blocks und die kumulierte Summe ausgegeben.
Trockenmengen zu Belegen, deren Analysewert zur Auswertungs-Qualität nicht
erfasst wurden (=0,0), werden am Ende des Reports gesondert ausgewiesen.

---

## EK-/VK-Auswertung Trockenmengen

EK-/VK-Auswertung Trockenmengen
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Der Report listet summarisch
•
Anlieferungsmenge (Bruttomenge)
Dieses ist die erfasste Liefermenge der
Hauptwarenposition (Referenznummer 1) des Belegs
•
Getrocknete Menge
Dieses ist die verbleibende Menge der
Hauptwarenposition (Referenznummer 1) nach Anwendung der angegebenen Qualität
zur Abrechnung der Feuchte, die durch eine der im Selektionsbereich angegebenen
Qualitätstextnummern identifiziert wird
•
FINAL- Menge
Dieses ist
die bereits finalisierte Nettomenge der Hauptwarenposition (Referenznummer 1)
nach Anwendung aller Qualitätsabrechnungen
•
Trocknungskosten
Dieses
ist der Kostenbetrag der Kostenposition, die durch eine der im Selektionsbereich
angegebenen Kostentextnummern identifiziert wird
Die Sortierung und damit die Untersummenbildung ist
im  zugehörigen Selektionsbereich wählbar
•
Artikelnummer-Lagernummer
Es wird für die selektierten Artikelnummern pro
Lagernummer im selektierten Bereich eine Summenzeile und eine Summenzeile pro
Artikel erzeugt
•
Artikelnummer-Lagernummer-Vertretergruppe
Zusätzlich zur vorhergehenden
Variante wird je Vertretergruppe innerhalb der Artikel-Lager-Kombinationen eine
Summenzeile erzeugt
•
Lagernummer-Artikelnummer
Es wird für die selektierten Lagernummern pro
Artikelnummern  im selektierten Bereich eine Summenzeile und eine
Summenzeile pro Lagernummer erzeugt
•
Lagernummer-Artikelnummer-Vertretergruppe
Zusätzlich zur vorhergehenden Variante wird je
Vertretergruppe innerhalb der Lager-Artikel-Kombinationen eine Summenzeile
erzeugt
•
Vertretergruppe-Artikelnummer-Lagernummer
Es wird für die selektierten Vertretergruppen jeweils
für die selektierten Artikelnummern pro Lagernummer im selektierten Bereich eine
Summenzeile sowie eine Summenzeile pro Artikel und letztendlich eine Summenzeile
für die jeweilige Vertretergruppe erzeugt
•
Vertretergruppe-Lagernummer-Artikelnummer
Es wird für die selektierten Vertretergruppen jeweils
[...]


---

## Aufkauf-/Verkauf-Artikelmengenauswertung

Aufkauf-/Verkauf-Artikelmengenauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
Aufkauf-Artikelmengen-Auswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
VK-Artikelmengen-Auswertung
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report liefert für ausgewählte Belege
kumulierte Zahlen für Trockenmengen, Nassmenge und Schwund, summiert über den
ausgewählten Zeitraum und gesondert für den letzten Tag des ausgewählten
Zeitraums. Es werden dabei die Summen pro Artikelnummer gebildet. Zusätzlich
werden als Einzelzeilen für jede Artikelnummer die Summen pro
Filial-/Lager-Kombination ermittelt.
Die Nassmenge ist immer die Bruttomenge
der Warenposition der Belege. Auch Sekundärpositionen des Artikels in
Rohwarebelegen werden berücksichtigt.
Zur Bestimmung der jeweiligen Trockenmenge und der
Schwundmenge ist die Angabe der Qualitätstextnummer erforderlich, die für die
Berechnung des Feuchtigkeitsabzugs bestimmt ist. Um unterschiedliche
Schemaeinrichtungen in einer Auswertung berücksichtigen zu können, ist die
Angabe von bis zu drei Qualitätstexten möglich. Werden dabei in einem
Abrechnungsschema mehrere der angegebenen Qualitätstexte verwendet, so wird die
verbleibende Menge nach Anwendung der Qualität mit der höchsten
Abrechnungspositionsnummer, die eine der angegebenen Qualitätstexte nutzt und
deren Warenbezug die Lieferposition ist, als Trockenmenge herangezogen.
Dabei ist zu beachten, dass die Schwundmenge die Menge
ist, die durch die berücksichtigte Qualität berechnet wurde. Sind in der
Reihenfolge des Abrechnungsvorgangs eines Belegs bereits vor dieser Qualität
Mengenänderungen durch andere Qualitäten erfolgt, so ergibt die Differenz aus
Nass- und Trockenmenge  folgerichtig nicht unbedingt die Schwundmenge.
Die Angabe
‚Ab Belegtyp‘
mit den Ausprägungen
•
1
für Lieferscheine
•
2
für Abschlagbelege
•
3
für Folgeabschlagbelege
•
4
für Finalbelege
ermöglicht die Einschränkung der Auswertung auf
bereits mindestens per Abschlag abgerechnete Be
[...]


---

## Aufkauf-/Verkauf-Auswertung Abrechnungen

Aufkauf-/Verkauf-Auswertung Abrechnungen
Hauptmenü
Rohwarenabrechnung
Auswertungen
Aufkaufauswertung Abrechnungen
Hauptmenü
Rohwarenabrechnung
Auswertungen
Verkaufsauswertung Abrechnungen
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report berücksichtigt Belege der Stufen
Abschlag, Folgeabschlag oder Finale. Zu einer Rohwarenlieferung wird dabei immer
der aktive (nicht weiterverarbeitete) Beleg der höchsten Stufe
herangezogen.
Erzeugt wird pro Beleg zu Warenpositionen der Typen Haupt- und
Sekundärwarenposition entsprechend der spezifizierten Selektionsbereiche für
eine Rohwarengruppe je eine Zeile mit den Angaben
•
Liefernummer
•
Lieferdatum
•
Feuchtmenge
Liefermenge der
Hauptwarenposition/Sekundärwarenposition
•
Trockenmenge
verbleibende Menge nach Anwendung der angegebenen
Qualität zur Abrechnung der Feuchte
•
Nettomenge
Nettomenge der
Hauptwarenposition/Sekundärwarenposition
•
Anfangspreis
Preis der Hauptwarenposition/Sekundärwarenposition
ohne berechnete Qualitätszu-/-abschläge
•
Endpreis
Preis der Hauptwarenposition/Sekundärwarenposition
nach Qualitätsabrechnung
•
Warenwert
Nettobetrag der
Hauptwarenposition/Sekundärwarenposition
•
Feucht %
Analysewert der per Referenznummer angegeben Qualität
zur Feuchtigkeitsabrechnung
•
[Ref 2.Qualität]
Analysewert der per Referenznummer angegeben
2. Qualität, überschrieben mit dem unter
Text 2.Qualität
des
Auswahlbereichs angegebenen Text
•
[Ref 3.Qualität]
Analysewert der per Referenznummer angegeben
3. Qualität, überschrieben mit dem unter
Text 3.Qualität
des
Auswahlbereichs angegebenen Text
•
Filiale
Filialnummer des Belegs
Die Sortierreihenfolge der Belege und damit die
Untersummierungen können im Auswahllbereich angegeben werden.

---

## Aufkauf-/Verkauf-Auswertung

Aufkauf-/Verkauf-Auswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
Aufkaufauswertung
Hauptmenü
Rohwarenabrechnung
Auswertungen
Verkaufsauswertung
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report listet für die spezifizierten
Selektionsbereiche für eine Rohwarengruppe pro Beleg eine Zeile mit den
Angaben
•
Liefernummer
•
Lieferdatum
•
Bruttomenge 1
Liefermenge der Hauptwarenposition
•
Trockenmenge
verbleibende Menge nach Anwendung der angegebenen
Qualität zur Abrechnung der Feuchte
•
Nettomenge 1
Nettomenge der Hauptwarenposition
•
Anfangspreis 1
Preis der Hauptwarenposition ohne berechnete
Qualitätszu-/-abschläge
•
Endpreis 1
Preis der Hauptwarenposition nach
Qualitätsabrechnung
•
Bruttomenge 2
Liefermenge der per Referenznummer angegeben
Sekundärwarenposition
•
Nettomenge 2
Nettomenge der per Referenznummer angegeben
Sekundärwarenposition
•
Anfangspreis 2
Preis der per Referenznummer angegeben
Sekundärwarenposition ohne berechnete Qualitätszu-/-abschläge
•
Endpreis 2
Preis der per Referenznummer angegeben
Sekundärwarenposition nach Qualitätsabrechnung
•
Feucht %
Analysewert der per Referenznummer angegeben Qualität
zur Feuchtigkeitsabrechnung
•
[Q2-Text]
Analysewert der per Referenznummer angegeben 2.
Qualität, überschrieben mit dem unter Q2-Text des Auswahlbereichs angegebenen
Text
•
Abs-Betrag
Brutto-Abschlagbetrag des Belegs
•
End-Betrag
rechnerischer Brutto-Endbetrag des Belegs
•
Rest
rechnerischer Brutto-Restbetrag des Belegs
Sortiert sind die Belege nach Artikelnummer,
Kunde/Lieferant, Kontrakt, Liefernummer mit Untersummen für Kunden/Lieferanten
und Kontrakten.
Die Angabe
‚Belegtyp‘
mit den Ausprägungen
•
1
für Lieferscheine
•
2
für Abschlagbelege
•
3
für Folgeabschlagbelege
•
4
für Finalbelege
bestimmt die Abrechnungsstufe der auszuweisenden
Belege unabhängig davon, ob sie bereits weiterverarbeitet wurden oder nicht. Es
können somit zum Beispiel unabhängig vom aktuellen Verarbeitungsstatus die Daten
aller Abschlagbelege ein
[...]


---

## Allgemeines zum Rohware-Fibu-Übertrag

Allgemeines zum
Rohware-Fibu-Übertrag
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Die
Übertragung der Rohware-Belege an die Finanzbuchhaltung erfolgt in den Modulen
EK-Rohwarenbearbeitung
für den Bereich
Einkauf
beziehungsweise
VK-Rohwarenbearbeitung
für den Bereich
Verkauf
in den Auswahllisten-Varianten
Fibu-Übertrag Rohware
Einkauf/Verkauf
und
Fibu-Übertrag Sammeldruck
Einkauf/Verkauf
. Dabei regelt die Einstellung des Rohwareparameters
Sammelbuchungen bei
Sammeldruck
, in welcher Form per Sammeldruck zusammengefasste Belege an die
Finanzbuchhaltung zu übergeben sind: Ist die Einstellung des Parametes
‚
Nein
‘, so werden alle Rohware-belege als Einzelbelege an die
Finanzbuchhaltung übergeben, die betreffende Auswahllisten-Variante
Fibu-Übertrag Sammeldruck
ist dann nicht verfügbar. Bei der
Einstellung ‚
Ja
‘ des Parameterwertes sind die per Sammeldruck verbundenen
Belege nur in der jeweiligen Auswahllisten-Variante
Fibu-Übertrag
Sammeldruck
berücksichtigt.
Voraussetzung für die
Belegübergabe an die Finanzbuchhaltung ist immer, dass deren
warenwirtschaftliche Verarbeitung durch den
Mandantenserver
abgeschlossen ist.
Der Steuerparameter
Fibu-Übertragung
auch ungedruckt
legt die Voraussetzung für die Übertragung bezüglich des
Drucks und der Archivierung fest.
Grundsätzlich können nur
Rohware-Belege der Rechnungsstufen (
Abschlag
,
Folgeabschlag
,
Finale
) gebucht werden, wenn diese den Bearbeitungsstatus
‚
abgerechnet
‘ haben und nicht bereits ein Folgebeleg erzeugt wurde, wie
zum Beispiel ein Stornobeleg oder eine Finale zum Abschlag. Wird ein
existierender Folgebeleg jedoch wieder storniert oder per Stornobeleg
egalisiert, so kann der Fibu-Übertrag für den Ursprungsbeleg wieder erfolgen. In
den Auswahllisten zum Fibuübertrag sind die nicht buchbaren Belege in der Spalte
Fib
mit dem Kennzeichen ‚
nn
‘ versehen
[...]


---

## Aufkauf-/Verkauf-Auswertung Lieferungen

Aufkauf-/Verkauf-Auswertung Lieferungen
Hauptmenü
Rohwarenabrechnung
Auswertungen
Aufkaufauswertung Lieferungen
Hauptmenü
Rohwarenabrechnung
Auswertungen
Verkaufsauswertung Lieferungen
Direktsprung
[LST]
Variante
Rohwarenauswertungen
Dieser Report berücksichtigt Belege der Stufe
Lieferschein, auch wenn diese bereits weiterverarbeitet wurden.
Erzeugt wird
pro Beleg zu Warenpositionen der Typen Haupt- und Sekundärwarenposition
entsprechend der spezifizierten Selektionsbereiche für eine Rohwarengruppe je
eine Zeile mit den Angaben
Liefernummer
•
Lieferdatum
•
Feuchtmenge
Liefermenge der
Hauptwarenposition/Sekundärwarenposition
•
Trockenmenge
verbleibende Menge nach Anwendung der angegebenen
Qualität zur Abrechnung der Feuchte
•
Nettomenge
Nettomenge der
Hauptwarenposition/Sekundärwarenposition
•
Anfangspreis
Preis der Hauptwarenposition/Sekundärwarenposition
ohne berechnete Qualitätszu-/-abschläge
•
Endpreis
Preis der Hauptwarenposition/Sekundärwarenposition
nach Qualitätsabrechnung
•
Warenwert
Nettobetrag der
Hauptwarenposition/Sekundärwarenposition
•
Feucht %
Analysewert der per Referenznummer angegeben Qualität
zur Feuchtigkeitsabrechnung
•
[Ref 2.Qualität]
Analysewert der per Referenznummer angegeben
2. Qualität, überschrieben mit dem unter
Text 2.Qualität
des
Auswahlbereichs angegebenen Text
•
[Ref 3.Qualität]
Analysewert der per Referenznummer angegeben
3. Qualität, überschrieben mit dem unter
Text 3.Qualität
des
Auswahlbereichs angegebenen Text
•
Filiale
Filialnummer des Belegs
Die Sortierreihenfolge der Belege und damit die
Untersummierungen können im Auswahllbereich angegeben werden.

---

## Fibu-Übertrag von Rohware-Einzelbelegen

Fibu-Übertrag von
Rohware-Einzelbelegen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung: Fibu Übertrag Rohware
Einkauf
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung: Fibu Übertrag Rohware
Verkauf
Direktsprung
[RWBV]
Die
Standard-Auswahlliste zum Fibu-Übertrag von Rohware-Einzel-Abrechnungen enthält
abgerechnete Rohwarebelege entsprechend der getroffenen Bereichseinschränkungen.
Belege, die Teil eines Sammeldruck-Belegs sind, werden hier nur aufgeführt, wenn
der Rohwareparameter
Sammelbuchungen bei Sammeldruck
mit dem
Wert ‚
Nein
‘ belegt ist. Zur besseren Übersicht werden die folgenden
Inhalte dargestellt:
Auswahlliste Fibu-Übertrag
      (Einzelabrechnungen)
VFKtr
Beleg mit Vorfakturierungskontrakt
      (Ja/Nein)
Belegdatum
Rechnungsdatum des
      Belegs
Belegnummer
Rechnungsnummer des
      Belegs
Klasse
ER für Eingangsrechnung
ERS für
      Stornoeingangsrechnung
AR für Ausgangsrechnung
ARS für
      Stornoausgangsrechnung
Fib
Fibu-Übertrag-Kennzeichen
--
noch nicht übertragen
i.B.
in Bearbeitung, Übertrag läuft
            gerade
ja
Beleg ist schon übertragen
nn
Beleg kann nicht übertragen werden (schon
            weiterverarbeitet, storniert oder Stornobeleg eines nicht
            übertragenen Belegs)
Kontonummer
Kunden-/Lieferanten-Nummer
Kunde/Lieferant
Kunden-/Lieferantenname
LiefNr.
Lieferscheinnummer
Lief.Dat.
Lieferscheindatum
Wiegenummer
Nummer des Wiegescheins
Filiale
Filialnummer
Status
Abrechnungs-Stufe
(Abschlag,
      Folgeabschlag, Finale)
Sperren
Sperrkennzeichen des
        Belegs
B
Bearbeitungssperre
K
Sperre wegen
            Kreditlimitüberschreitung
W
Weiterverabeitungssperre
F
Fibu-Übertrag-Sperre
R
Rechnungseingangsbuch-/Rechnungsausgangsbuch-Sperre
U
Umwandlungsperre
f
Filial-Sperre
Druckkennzeichen
Kennzeichen, ob der Belege bereits
      gedruckt wurde
Ab
Abschlag-Status-Kennzeichen
--
Ohne Abschlag
Ab
Abschlag
      abgerechnet
FAb
Folge-Abschl
[...]


---

## Rohwarebelege abrechnen

Rohwarebelege abrechnen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Abrechnen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Abrechnen
Direktsprung
[RWBV]
Mit
dieser Funktion können die ausgewählten Rohwarebelege abgerechnet werden, sofern
diese für ihre Belegstufe (Abschlag, Folgeabschlag beziehungsweise Finale) in
dem zugehörigen Statusattribut über den Wert ‚Freigegeben‘ verfügen. Nur
abgerechnete Belege können gedruckt, an die Finanzbuchhaltung übergeben, in die
nächste Stufe umgewandelt und/oder storniert werden.
Ist der
Rohwareparameter  [RWPA]
Freigegebene Belege immer
abrechnen
mit dem Wert ‚
Ja
‘ eingestellt, so steht diese dann
überflüssige Funktion nicht zur Verfügung.
Nach Aufruf der Funktion
Abrechnen
erscheint eine Steuerungsmaske, auf der Einstellungen für den
Abrechnungslauf vorgenommen werden können:
Zunächst kann festgelegt
werden, ob das Originaldatum des jeweils abzurechnenden Belegs erhalten bleibt,
oder ob es durch ein dann anzugebendes neues Beleg-Datum (vorbelegt mit dem
aktuellen Tagesdatum) zu ersetzen ist. Die Vorbelegung dieser Auswahl ist mit
dem Rohwareparameter [RWPA]
Rechnungsdatum setzten auf
festgelegt.
Wird hier die Variante mit Belegdatumangabe gewählt, so ist
gegebenenfalls in einem weiteren Feld anzugeben, ob die warenwirtschaftliche
Buchungsperiode der Belege gegebenenfalls an das neue Datum anzupassen ist oder
die bereits festgelegten Perioden beizubehalten sind. Dieses Feld ist auf der
Maske jedoch nur aktiv, wenn der Rohwareparameter [RWPA]
Periode bei
Belegdatum=Abrechnungsdatum
mit der Einstellung ‚
Laut
Maskeneinstellung
‘ versehen ist. Die beiden anderen
Einstellungsmöglichkeiten jenes Parameters (‚
Periode beibehalten
‘ oder
‚
Periodenanpassung an Belegdatum
‘) werden automatisch berücksichtigt.
Für
die Behandlung des Valutadatums (Zahlungsziel) für Belege, deren
Zahlungsbedingung die Eingabe eines festen Datums als Zahlungsziel
[...]


---

## Fibu-Übertrag von Rohware-Sammeldruck-Belegen

Fibu-Übertrag von
Rohware-Sammeldruck-Belegen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung: Fibu Übertrag
Sammeldruck Einkauf
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung: Fibu Übertrag
Sammeldruck Verkauf
Direktsprung
[RWBV]
Mit
dieser Auswahllisten-Variante können Rohware-Sammeldruck-Belege entsprechend der
getroffenen Bereichseinschränkungen geschlossen an die Finanzbuchhaltung
übergeben werden, wenn der Rohwareparameter
Sammelbuchungen bei Sammeldruck
mit dem
Wert ‚
Ja
‘ belegt ist.
Dargestellt wird hier je eine Zeile pro
Sammeldruck-Beleg. Sind Einzelbelege zu einem Sammeldruck-Beleg jedoch nicht zu
einem Fibu-Beleg zusammenfassbar, so wird hier pro entstehendem Fibu-Beleg eine
Zeile dargestellt. Das ist insbesondere dann der Fall, wenn die zum Sammeldruck
gehörenden Einzelbelege unterschiedliche Vorgaben der zu verwendenden
Buchungsperioden oder verschiedene Zahlungsziele haben! Es kann also vorkommen,
dass ein Sammeldruck-Beleg in der Finanzbuchhaltung in mehrere Belege aufgeteilt
wird!
Es werden in der Standard-Auswahlliste die folgenden Inhalte
dargestellt:
Auswahlliste Fibu-Übertrag
      Sammeldruck
Klasse
ER für Eingangsrechnung
ERS für
      Stornoeingangsrechnung
AR für Ausgangsrechnung
ARS für
      Stornoausgangsrechnung
SBel.Datum
Sammelbeleg-Datum = Druckdatum der
      zugehörigen Einzelbelege als Sammeldruck
Drucknummer
Sammeldruck-Nummer = Belegnummer des
      Sammeldruck-Belegs
Druckkennzeichen
Kennzeichen, ob der Belege bereits
      gedruckt wurde
Fib
Fibu-Übertrag-Kennzeichen
--
noch nicht übertragen
i.B.
in Bearbeitung, Übertrag läuft
            gerade
ja
Beleg ist schon übertragen
nn
Beleg kann nicht übertragen werden (schon
            weiterverarbeitet, storniert oder Stornobeleg eines nicht
            übertragenen Belegs)
Kontonummer
Kunden-/Lieferanten-Nummer
Kunde/Lieferant
Kunden-/Lieferantenname
Filiale
Filialnummer
Status
Abrechnungs-S
[...]


---

## Zusatzbeleg-Hinweis in Auswahllisten

Zusatzbeleg-Hinweis in
Auswahllisten
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
In
den Auswahllisten des Rohware-Bearbeitungs-Moduls werden die Belege, die bei der
Erfassung durch das
Belegsplitting-Verfahren bei
Kontraktmengenüberlauf
entstanden sind, und der zugehörige Ausgangsbeleg in
einer gesonderten Spalte durch Ausweisung einer Liste der beteiligten
Liefernummern in roter Schriftfarbe gekennzeichnet.

---

## Belegdaten der Zusatzbelege

Belegdaten der
Zusatzbelege
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
Für
die Erzeugung der Zusatzbelege im Belegsplittingverfahren wegen
Kontraktmengenüberschreitung bei der Erfassung von Rohwarebelegen werden die
Grunddaten des erfassten Belegs Kunden-/Lieferantennummer, Artikelnummer,
Lagernummer und Abrechnungsschemanummer sowie das Belegdatum herangezogen.
Positionsunabhängigen Kopfdaten werden ebenfalls in die Zusatzbelege
übernommen.
Übernommene positionsunabhängigen
      Kopfdaten
Währungsnummer,
      Währungskurs
Wiegenummer
Steuergruppe
Herkunfts-/Zielland und
      -region
Versandart
LKW-Nummer, Anhängernummer,
      Fahrernummer
Vertretergruppe
Verkaufsgebiet
Fakturiergruppe
Zahlungsarten
Zahlungsbedingungen und
      -werte
Partiezuordnung
Abschlag-, Folgeabschlag-,
      Finalstatus, Abschlagsatz
Nachhaltigkeitswerte
Positionsbezogene Daten wie
Mengen von sekundären Warenpositionen und Kosten-/Vergütungspositionen,
individuelle Zu-/Abschlagsätze bei Liefer- und Sekundär-Warenpositionen,
Kosten-/Vergütungs-Sätze und –Pauschalen sowie Analyse- und Basis-Werte der
Qualitätspositionen werden übernommen, sofern diese nicht aufgrund der
Schemadefinition
berechnet werden und die Übernahme nicht durch die Angabe von
‚Nein‘
im
jeweiligen Feld
Übernahme in Folgebeleg bei Kontraktmengenüberschreitung
ausgeschlossen wird.

---

## Stornieren/Löschen von Rohwarelieferungen mit Zusatzbelegen

Stornieren/Löschen von
Rohwarelieferungen mit Zusatzbelegen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
Das
Stornieren und Löschen
von Rohwarelieferungen mit Zusatzbelegen, die bei der Erfassung durch das
Belegsplitting-Verfahren
bei Kontraktmengenüberlauf
entstanden sind, werden aus Konsistenzgründen
immer zusammen gelöscht. Kann einer dieser Belege nicht gelöscht werden, zum
Beispiel weil er bereits weiterverarbeitet wurde, so wird keiner der
zusammengehörigen Lieferscheine gelöscht!

---

## Parameter für Rohware-Datenbank-Prozeduren

Parameter für
Rohware-Datenbank-Prozeduren
Die
möglichen Parameter, die zur Laufzeit versorgt werden sind:
PAR_AUFRUFMODUS
CHAR(12)
Dieser Parameter wurde implementiert, um innerhalb der Prozedur
unterscheiden zu können, zu welchem Zweck die Prozedur aufgerufen wurde.
Einer der Werte ‚FIN_PR‘,
‚ABS_PR‘, ‚WM_PR‘ oder ‚MIN_PR‘  kennzeichnet einen Prozeduraufruf zur
Ermittlung eines Final-/Produktpreises, Abschlagpreises, Weltmarktpreises oder
Mindestpreises.
Der Wert ‚AW‘ zeigt an, dass die Prozedur zur
Qualitäts-Analysewertbestimmung aufgerufen wurde.
‚AWK1‘ bzw. ‚AWK2‘
kennzeichnen die Verwendung der Prozedur zur Bestimmung des korrigierten
Analysewertes in erster bzw. zweiter Stufe (Analysewert-Korrektur 1,
Analysewert-Korrektur 2 der Qualitätsdefinitionsmaske).
Entsprechend stehen
‚UB‘ und ‚OB‘ für die Kennzeichnung des Prozedurergebnisses als unterer bzw.
oberer Basiswert.
Wird
eine Prozedur als Qualitäts-Abrechnungsmethode aufgerufen, so enthält der
Parameter einen der vier Werte:
‚Q_ME_ABR_UB‘ bei
Interpretation des Ergebnisses als Mengenänderung und Aufruf bei Unterschreitung
des unteren Basiswertes durch den korrigierten Analysewert.
‚Q_ME_ABR_OB‘
bei Interpretation des Ergebnisses als Mengenänderung und Aufruf bei
Überschreitung des oberen Basiswertes durch den korrigierten Analysewert.
‚Q_PR_ABR_UB‘ bei
Interpretation des Ergebnisses als Preisänderung und Aufruf bei Unterschreitung
des unteren Basiswertes durch den korrigierten Analysewert.
‚Q_PR_ABR_OB‘
bei Interpretation des Ergebnisses als Preisänderung und Aufruf bei
Überschreitung des oberen Basiswertes durch den korrigierten Analysewert.
Bei
Aufruf einer Prozedur zur Ermittlung eines Kostensatzes wird dieses durch
‚KO_STZ‘
Als
Parameterwert angezeigt, während die Ermittlung einer Kostenpauschale durch
‚KO_PAU‘ kenntlich gemacht wird.
PAR_BELEGMODUS
SMALLINT
Dieser
Parameter gibt an, in welchem Bearbeitungsmodus sich der Rohwarebeleg, zu dem
die den Prozeduraufruf auslösende
[...]


---

## Rohware-Erfassung mit Belegsplitting bei Kontraktmengenüberlauf

Rohware-Erfassung mit
Belegsplitting bei Kontraktmengenüberlauf
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
Wird
einem Rohwarebeleg in der Lieferwarenposition während der Erfassung ein Kontrakt
zugeordnet, dessen Gesamt-Restmenge oder Restmenge im angesprochenen Zeitraum
kleiner als die erfasste Bruttomenge (bei Bruttomengenkontrakten) oder die
berechnete Nettomenge (bei Nettomengenkontrakten) ist, so kann diese Menge auf
die Restmenge reduziert und weitere Belege mit der Differenzmenge unter
Berücksichtigung der weiteren erfassten Werte ( Partiezuordnungen, Analysewerte,
Kostensätze etc. ) erzeugt werden.
Bei der Korrektur von Rohwarebelegen kann
dieses Verfahren nur dann angewendet werden, wenn es sich bei den zu
korrigierenden Belegen um Lieferschein-Vorgänge handelt, denen in der
Hauptposition noch kein Kontrakt zugeordnet wurde. Damit steht das Verfahren
auch für organisatorische Arbeitsabläufe zur Verfügung, bei denen zum Beispiel
nach erfolgter Belegerzeugung aus der Waagen-Schnittstelle die Kontraktzuordnung
erst in einem weiteren Nachbearbeitungsschritt vorgenommen werden soll.
ACHTUNG: Es ist dabei zu
beachten, dass manuelle Qualitäts-Zu-/-Abschlag-Ergebnisse und manuelle
Kosten-/Vergütungsbeträge auch so in die Folgebelege übernommen werden!

---

## Optionales Belegsplitting bei Kontraktmengenüberlauf

Optionales Belegsplitting bei
Kontraktmengenüberlauf
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
Wird
die Erfassung eines Rohwarelieferscheins abgeschlossen, so kann bei zugeordnetem
Kontrakt zur Lieferposition und nicht ausreichender Gesamt-Restmenge oder
Zeitraumrestmenge des Kontrakts bezüglich der erfassten Menge bei einem
Bruttomengenkontrakt beziehungsweise der errechneten Nettomenge bei einem
Nettomengenkontrakt bei entsprechender Einstellung des Rohwareparameters [RWPA]
Erfassungsbeleg
teilen bei Übermenge
das Öffnen einer Maske zur Belegteilung
erzwungen werden.
ACHTUNG: Es ist dabei zu
beachten, dass manuelle Qualitäts-Zu-/-Abschlag-Ergebnisse und manuelle
Kosten-/Vergütungsbeträge auch so in die Folgebelege übernommen werden!
Das
Referenz-ERP-System schlägt in der ersten Zeile eine Reduzierung der erfassten Menge
derart vor, dass die verbleibende Brutto- beziehungsweise Nettomenge der offenen
Restmenge oder Zeitraumrestmenge des angesprochenen Kontrakts entspricht. Die
zweite Zeile enthält zunächst die Differenzmenge zur ursprünglich erfassten
Menge als Bruttomenge, die in einem weiteren zunächst kontraktlosem Vorgang
eingestellt wird. Die Werte der Bruttomengenspalte können, zum Beispiel zur
Rundung, geändert werden, was aber grundsätzlich zur Neuberechnung der
nachfolgenden Zeilen führt.
Dadurch ist gewährleistet,
dass die Summe der Bruttomengen immer der der ursprünglich erfassten Menge
entspricht. Wird die Bruttomenge der letzten Zeile manuell reduziert, so wird
mit der daraus resultierenden Differenzmenge eine zusätzliche Zeile für einen
weiteren Beleg erzeugt.
Für
alle Zusatzbelege, nicht jedoch für den ursprünglichen Beleg in der ersten
Zeile, kann die jeweils vorgeschlagene Belegnummer manuell geändert werden.
Diese muss aber entsprechend dem der Vorgangskl
[...]


---

## Bearbeiten Sammeldruck

Bearbeiten Sammeldruck
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Die
Auswahlvariante ‚
Bearbeiten Sammeldruck
‘ im Einkauf und im Verkauf stellt
Funktionen zur Verfügung, um bestehende Rohware-Sammeldruck-Belege erneut
zu drucken, Storno-Sammeldruck-Belege zu erstellen und zu drucken,
Sammeldruckbelege wieder aufzuheben, eine Auswahlliste der Einzelbelege eines
Sammeldruckbelegs aufzurufen und Ergänzungswerte aller Einzelbelege eines
Sammeldruckbeleges zu bearbeiten.
Für
die Zusammenstellung der Auswahlliste ist eine möglichst gezielte Angabe der
Kriterien der Bereichsauswahl vorzunehmen, da die Informationsbeschaffung für
die Darstellung der virtuellen Sammelbelege aus den zugehörigen Einzelbelegen
unter Umständen längere Antwortzeiten des Datenbanksystems bedeuten kann.
Druck
Die
Funktion
Druck
dient dem wiederholten, bei Stornobelegen auch dem ersten,
Ausdruck der ausgewählten Sammeldruckbelege.
Einzelbelege zeigen
Ist
genau ein Sammeldruckbeleg markiert (ausgewählt), so kann mit
Einzelbelege
zeigen
eine Auswahlliste mit den zugehörigen Einzelbelegen aufgerufen
werden, die wiederum die Ansicht und Vorschau dieser Belege ermöglicht.
Druck zurücksetzen
Die
Funktion
Druck zurücksetzen
löst einen Sammeldruckbeleg wieder auf.
Dieses kann nur für Belege erfolgen, die noch nicht in die Finanzbuchhaltung
übertragen wurden. Sie ist dann auszuführen, wenn an Einzelbelegen eines
Sammeldrucks noch Änderungen vorzunehmen sind oder die
Sammeldruckzusammenstellung nicht das gewünschte Ergebnis erbracht hat. Je nach
Einstellung des Rohwareparameters [RWPA]
Sammelnummer-Release bei
Druckrücksetzen
wird die Drucknummer (Sammelbelegnummer) dabei in den
Nummernkreis zurückgeschrieben oder nicht.
Rohware-Mail erneut
versenden
Sollen beim Erstellen von
Rohwaresammelbelegen erstellte E-Mails bezüglich der E-Mail-Empfänger g
[...]


---

## Sammelerstdruck

Sammelerstdruck
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Die
Auswahlvariante ‚
Sammelerstdruck
‘ im Einkauf und im Verkauf dient der
Erstellung von Rohware-Sammeldruck-Belegen. Unter Berücksichtigung der in der
Bereichsauswahl anzugebenden Auswahlkriterien werden hier Einzelbelege
aufgeführt, die die für die Verwendung in einem Sammeldruck erforderlichen
Kriterien erfüllen:
Die
Belege dürfen noch nicht gedruckt sein
Die
Belege dürfen noch nicht an die Finanzbuchhaltung übertragen sein
Die
Belege dürfen noch nicht weiterverarbeitet sein
Für
die Abrechnungsstufe muss ein Sammelabrechnungsformular in den Belegen
zugeordnet sein
Die
Beleg-Trennung pro Sammeldruck erfolgt automatisch nach den Kriterien
Kunden-/Lieferantennummer
Rechnungsempfänger
Zahlungsempfänger/Zahlungspflichtiger
Währung
UmsatzsteuerID des
Kunden/Lieferanten im Beleg
Eigene UmsatzsteuerID im
Beleg
Wirtschaftsjahr
Warenwirtschaftsperiode
Sammelformularnummer
Zusätzlich können mit den
entsprechenden Rohwareparametern [RWPA] weitere Trennkriterien festgelegt
werden
Vertretergruppe
Kontraktnummer
Versandadresse
Lagernummer
Rohwarengruppe
Abrechnungsschema
Artikel
Liefermonat
Lieferwoche
Währungskurs
Einfluss auf die Trennung hat
auch der Rohwareparameter [RWPA]
Sammeldruck-Sortierung
mit den
Einstellmöglichkeiten ‚
automatisch
‘
und
‚
nach
Belegauswahl‘
. Erstere gewährleistet die Berücksichtigung der Einzelbelege
in einer den internen und den eingestellten Trennkriterien entsprechenden
Reihenfolge, so dass möglichst optimale Trennungen erfolgen. Zu beachten ist in
diesem Falle auch die Einstellung des Parameters
Sammeldrucksortierung
automatisch: mit Wiegenummer
. Die
Einstellung ‚
nach Belegauswahl‘
hingegen berücksichtigt die Einzelbelege
entsprechend der Reihenfolge der getroffenen Auswahl. Dieses ist nur bei
bestimmten Arbeitsweisen sinnv
[...]


---

## Stornoieren/Löschen

Stornoieren/Löschen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Rohwarebelege können mit der
Funktion
Stornieren/Löschen
aus dem Referenz-ERP-Vorgangswesen wieder entfernt
werden. Dieses kann zum Beispiel für eine aus einer Rohwarenlieferung irrtümlich
zu früh erstellte Rohwarenabrechnung geschehen, wenn diese noch nicht gedruckt
oder verschickt wurde. Auch ein Rohwarelieferschein, der mit einer falschen
Kundennummer oder mit einem falschen Lieferartikel erfasst wurde, kann so wieder
gelöscht werden, um ihn anschließend mit den korrekten Daten neu zu
erfassen.
Grundsätzlich werden, wenn möglich, nur genau die ausgewählten
Belege gelöscht.
Eine
Ausnahme
stellen jedoch Lieferscheine da, die
bei der Erfassung durch das
Belegsplitting-Verfahren bei
Kontraktmengenüberlauf
entstanden sind sowie deren jeweiliger
Ausgangsbelege: Diese Lieferscheine werden aus Konsistenzgründen immer zusammen
gelöscht. Kann einer dieser Belege nicht gelöscht werden, zum Beispiel weil er
bereits weiterverarbeitet wurde, so wird keiner der zusammengehörigen
Lieferscheine gelöscht!
Generell können nur Belege
gelöscht werden, die nicht weiterverarbeitet sind: Es darf also weder ein
direkter Stornobeleg noch eine nicht stornierte Abrechnung als Folgebeleg
existieren. Auch ein Beleg, der bereits in die Finanzbuchhaltung übertragen
wurde, kann nicht gelöscht werden. Ist ein zu löschender Beleg Teil eines
Sammelbelegdrucks (Sammelabrechnung), so muss der zugehörige Sammelbeleg
zunächst wieder mit der Funktion
Druck zurücksetzen
in der Auswahllistenvariante
Bearbeiten Sammeldruck
zurückgesetzt werden.

---

## Rohware-Preisfindung per Datenbankprozedur bestimmen

Rohware-Preisfindung per Datenbankprozedur
bestimmen
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Abrechnungsschema
Merkmal-Definition
Direktsprung
[RWG]
Hauptmenü
Administration
Werkzeuge
SQL Textmanager
Direktsprung
[SQLM]
Für
die Bestimmung der Anfangspreise von
Lieferwarenpositionen
und
Sekundärwarenpositionen
in Rohwareabrechnungsschemata können Datenbankprozeduren eingesetzt werden.
Dabei ist zu beachten, dass
ein derart ermittelter Preis für eine Preismengeneinheit der Position normiert
zurückgegeben werden muss.
Hinweis:
Es ist bei der
Verwendung von Datenbankprozeduren unbedingt auf die Performance bei der
Prozedurausführung zu achten, da die Preisfindung während der Erfassung oder
Korrektur eines Rohware bei allen Eingaben durchgeführt wird, die preisrelevant
sein könnten.
Es
kann jeweils ein Prozedurname zur Ermittlung von
•
Produkt-/Finalpreis
•
Abschlagpreis
•
Weltmarktpreis
•
Mindestpreis
jeweils getrennt nach Einkauf
und Verkauf angegeben werden.
Bei
der jeweiligen Einstellung
Prozedurpreis 0,00 überschreibt Preis
=
‚NEIN‘
erfolgt entsprechenden Fall eine Preisfindung ohne Prozedur (
Kontraktpreis, Partiepreis, Listen-/Fixpreis ).
Die
verwendeten Datenbankprozeduren müssen ein RESULT mit einem Attribut
zurückliefern, dass praktischerweise vom Typ ‚numeric‘, oder ‚decimal sein
sollte. Der Name des Ergebnisfeldes ist beliebig wählbar. Bei der Erfassung,
Korrektur und/oder Abrechnung eines entsprechenden Beleges wird der Ergebniswert
ermittelt und der gewünschte Anfangspreis in Abhängigkeit der
Preis-Nachtragseinstellung, der 0-Prozedurpreiseinstellung der
Positionseinrichtung und des Fix-Kennzeichens des Preises im Beleg
überschrieben.
Die Parameter der DB-Prozedur werden mittels festgelegter
Parameternamen bestimmt. Diese sind mit DEFAULT-Werten in der Parameterliste zu
versehen. Aus der
Liste der möglichen
Parameter
müssen nur die tatsächlich benötigten deklariert werden.

---

## EK-Waage-RWLieferungen/VK-Waage-RWLieferungen

EK-Waage-RWLieferungen/VK-Waage-RWLieferungen
Hauptmenü
Rohwarenabrechnung
EK-Waage-RWLieferungen
Direktsprung
[RWWE]
Hauptmenü
Rohwarenabrechnung
VK-Waage-RWLieferungen
Direktsprung
[RWWV]
Alle aus der Waage oder mit der Offline-Waage
erzeugten Rohwarenbelege werden in diese Schnittstelle übertragen. Sofern in dem
Wiegeprozess
auf der
Registerkarte Rohware
für die
Online-Waage nicht der Punkt Rohwarenbelege sofort erzeugen auf „Ja“ steht
können hier noch die erfassten Daten für den Rohwarenbeleg korrigiert
werden.
Ausprägungen des Feldes Status
Bezeichnung
Bedeutung
Übernahme läuft
Dies
      bedeutet, dass zu Importierende Daten in die Schnittstelle übernommen
      werden
Fehl: ÜB!
Fehler bei der Übernahme
--
Einspielung hat funktioniert.
      Datensatz kann weiterverarbeitet werden
Belerz. Läuft
FEHL
      Belerz!
Fehler bei der Belegerzeugung. Die
      Daten müssen mit
Ändern
F5
korrigiert werden.
erledigt!
Es
      wurde ein Rohwarenbeleg erzeugt. Dieser ist unter
[RWE]
für Rohwareneinkauf oder
[RWB]
Rohwarenverkauf zu
      finden.
Funktionen der Waagenimportschnittstelle
Funktion
Bedeutung
RW-Waage Import Shift +
      F12
Mit
      dieser Funktion werden Waagenbelege in die Schnittstelle importiert.
      Einrichtung der Scriptparameter finden Sie
hier
.
Waage Qualitäten Shift
      +F7
Mit
      dieser Funktion können Qualitäten zu einem Satz nach erfasst
      werden.
FEHL: Belerz Rücksetzten Shift
      +F8
Mit
      dieser Funktion kann der Status auf – zurückgesetzt, wenn bei der
      Belegerzeugung ein Fehler aufgetreten ist.
Ganze Überna. Löschen F7
Mit
      dieser Funktion werden markierte Belege komplett aus der Schnittstelle
      gelöscht. Erzeugte Belege und Wiegungen belieben aber
      bestehen.
Aufräumen
Mit
      dieser Funktion werden alle Belege aus der Schnittstelle gelöschte
      erzeugte Beleg bleiben aber bestehen.
Ändern F5
Mit
      dieser Funktion kann ein Satz vorm Erzeugen einer Lieferung noch

[...]


---

## Funktion Beleg löschen

Funktion Beleg löschen
Mit der Funktion
Beleg löschen
kann man Rohwarenbelege
löschen.
Beim Löschen von Rohwarenbelegen wird man gefragt, ob man den
zugehörigen Waagedatensatz auch löschen möchte. Diese Abfrage erscheint nur,
wenn der Rohwarenbeleg nicht den Status erledigt hat, d.h. aus ihm noch keine
Lieferung erzeugt wurde.
Beim Löschen wird unterschieden zwischen
Rohwarenbelegen, die eine VorgangsId der Bestandsführung enthalten und denen die
keine enthalten.
Löschen von Rohwarenbelegen mit Bestandsführung aus
der Waage:
Mit Hilfe der BestandsVorgId im Rohwarenbeleg, der
gelöscht werden soll, wird der zugehörige Waagedatensatz gesucht. Wenn man die
Abfrage, ob der Waagendatensatz auch gelöscht werden soll, mit Ja beantwortet,
dann wird der Waagedatensatz auf den Status gelöscht gesetzt und die VorgangsId
des Bestandsbeleges (gespeichert im Feld owaage_bvid) wird aus ihm entfernt. Der
zugehörige Bestandsbeleg wird storniert.
Falls das Stornieren des
Bestandsbeleges fehlschlägt, erhält man eine Warnung, dass man den Beleg von
Hand löschen muss. Außerdem gibt es einen Eintrag im
Fehlerprotokoll.
entscheidet man sich gegen das Löschen des Waagedatensatzes,
dann wird dieser vom Status ‚mit Vorgang’ auf den Status ‚Abgeschlossen’
zurückgesetzt.
Löschen von Rohwarenbelegen ohne Bestandsführung aus
der Waage:
Mit Hilfe der OwaageId im Rohwarenbeleg, der gelöscht
werden soll, wird der zugehörige Waagedatensatz gesucht.
Wenn man die
Abfrage, ob der Waagendatensatz auch gelöscht werden soll, mit Ja beantwortet,
dann wird der Waagedatensatz auf den Status gelöscht gesetzt.
entscheidet man
sich gegen das Löschen des Waagedatensatzes, dann wird dieser vom Status ‚mit
Vorgang’ auf den Status ‚Abgeschlossen’ zurückgesetzt.

---

## Sammelabrechnung

Sammelabrechnung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Eine
Rohware-Sammelabrechnung (Sammeldruck) ist ein zusammenfassender Ausdruck
mehrerer Rohwareabrechnungen einer Stufe (Abschlag, Folgeabschlag oder Finale),
der über eine separate Drucknummer, einen separaten Kopfteil, einen
zusammenfassenden Fußteil und einen Positionsteil zur Ausgabe der
Detailinformationen der Einzelbelege verfügt. Dabei kann durch geeignete Wahl
des Nummernkreises für die Drucknummer (festgelegt im Modul ‚
Mandanten
Nummernkreise
‘ [MNDNK]) diese auch als Sammelbelegnummer aufgefasst werden
und alle Einzelbelege eines Sammeldrucks als Sammelbuchung unter dieser Nummer
in die Finanzbuchhaltung übertragen werden, sofern der Rohwareparameter [RWPA]
Sammelbuchungen bei
Sammeldruck
mit der Einstellung ‚
Ja
‘ versehen ist. Zu
beachten ist dabei, dass insbesondere die im Fußteil eines Sammeldruckformulars
druckbaren Summen (Bruttosummen, Nettosummen, Steuersummen etc.) tatsächlich
echte Summen der entsprechenden Werte der Einzelbelege sind.

---

## Schema-/Kundenänderung

Schema-/Kundenänderung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Verwenden Sie diese
Funktion bitte nur, nachdem Sie die Hilfe dazu komplett gelesen haben!

---

## Schemaspezifische-Ergänzungsfelder

Schemaspezifische-Ergänzungsfelder
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Abrechnungsschema
Ergänzungsfelder
Direktsprung
[RWG]
Die
hier definierten Felder stehen zusätzlich zu den
‚rohwarengruppenweit’
definierten Feldern für
Belege des betreffenden Abrechnungsschemas zur Verfügung.
Der
Aufbau der Blöcke zur Ergänzungs-Wert- und –Text-Definition entspricht dem der
rohwarengruppen-spezifischen Angaben.
Pflegbar in den Blöcken sind
auf dieser Maske jedoch lediglich die Zeilen 4, 5 und 6, deren Zeilennummern
wiederum das korrespondierende Datenfeld der Relation V_Rohware
(V_RohwareZFeldI4, V_RohwareZFeldI5 bzw. V_RohwareZFeldI6 bzw. V_RohwareZFeldC4,
V_RohwareZFeldC5 bzw. V_RohwareZFeldC6) bestimmen.
Die
Zeilen 1 bis 3 enthalten zur Orientierung die Angaben der zugrunde liegenden
Rohwarengruppe.
Die
Bedeutung der Angaben in den einzelnen Spalten entspricht der der
rohwarengruppen-spezifischen Definitionen.
Im
unteren Maskenbereich werden Ergänzungswert- (1.Block) und Ergänzungstextinhalte
(2.Block) der Rohware-Waage-Schnittstelle den Felddefinitionen zugeordnet. Die
jeweils obere blau unterlegte Zeile entspricht dabei der 1 Spalte des
zugehörigen oberen Definitionsblocks. Darunter kann ein Ergänzungsfeld eines
Waagedatensatzes einer Definitionszeile zugeordnet werden, indem unter der
Definitionszeilennummer die Nummer des Wertes im Waage-Datensatz eingetragen
wird.

---

## Stammdaten 3 (Kontrakt)

Stammdaten 3 (Kontrakt)
Folgende Felder stehen auf der Registerkarte
„Stammdaten 3“ zur Verfügung.
Stammdaten 3
Filialnummer
Hier
      kann die Filialnummer, für welche Filiale der Kontrakt gelten soll,
      eingetragen werden.
Mahntage erste Mahnung
Anzahl der Tage, ab denen bei
      Überschreitung der Laufzeit automatisch Erinnerungsschreiben erstellt
      werden.
Mahntage zweite Mahnung
Anzahl der Tage, ab denen bei
      Überschreitung der Laufzeit automatisch Erinnerungsschreiben erstellt
      werden.
Mahnstufe
Anzeige, wie oft gemahnt
      wurde.
Als
      weitere Informationen werden geführt, wer den Kontrakt erfasst hat, wann
      Kontraktbestätigung, -erledigungsschreiben und -mahnung gedruckt wurden
      und wann ein Stornobeleg erzeugt wurde.
Bediener Neuerzeugung
Bediener der den Kontrakt erzeugt
      hat.
Bediener letzte Änderung
Bediener der die letzte Änderung am
      Kontrakt gemacht hat.
Kontrakt-Bestätigung
Kennzeichnet ob der Kontrakt
      gedruckt wurde.
Kontrakt-Erledigung
Kennzeichen ob der Kontrakt erledigt
      ist.
Kontrakt Storno
Kennzeichen ob der Kontrakt
      storniert wurde.
Maximale Überschreitung
      %
Der
      Prozentsatz, um das das vereinbarte Kontraktvolumen (Menge oder Wert)
      maximal über- bzw. unterschritten werden darf.
Maximale Unterschreitung
      %
Der
      Prozentsatz, um das das vereinbarte Kontraktvolumen (Menge oder Wert)
      maximal über- bzw. unterschritten werden darf.
Zahlungsbedingung
Für
      den Kontrakt kann eine spezielle Zahlungsbedingung hinterlegt werden, die
      dann statt der Standardbedingung des Kunden herangezogen wird. Bei
      Zahlungsbedingungen vom Typ 7 kann auch ein festes Valutadatum eingetragen
      werden. Vorbelegung 0 = Zahlungsbedingung aus
      Deb./Kred.-Stamm.
Zahlungsziel
•
Abweichende
      Zieltage
•
Tag des
      Folgemonats
•
Tag des jew.
      Monats
•
Nächster
      x.
•
Fixes
      Fälligkeitsdatum
In
      Abhängigkei
[...]


---

## Stammdaten 2 (Kontrakt)

Stammdaten 2 (Kontrakt)
Für weitergehende Abwicklungen stehen weitere
Parameter zur Verfügung:
Stammdaten 2
Musterkontrakt
Kennzeichen, ob es sich bei den
      erfassten Daten um einen Musterkontrakt („Template“) handeln soll.
      Musterkontrakte werden bei Kontraktauswahlen niemals herangezogen und
      können auf keinen Fall bebucht werden. Außerdem sind sie natürlich nicht
      unbedingt einer bestimmten Kontraktgruppe zugeordnet.
Ein
      Musterkontrakt kann beim Anlegen eines neuen Kontraktes als
      Vorbelegungshilfe herangezogen, aber auch für spätere Updates (z. B.
      Aufnahme neuer Artikel oder Preise in die zugeordneten Kontrakte)
      verwendet werden.
Im
      praktischen Einsatz legt man sich seine typischen Kontrakte mit allen
      Bedingungen, Texten etc. an und greift dann bei der Neuerfassung hierauf
      zu und gibt die abweichenden Daten ein.
Lagerspezifisch
Ein
      Kontrakt kann fest an ein Lager gebunden sein, d.h. bei Abholung aus einem
      anderen Lager werden die Kontraktbedingungen nicht gezogen.
Ziellager
Das
      Feld Ziellager ist ein rein informatives Feld. Es kann ein Lager
      eingetragen werden.
Warengruppenzuordnung
Kennzeichen, ob der Kontrakt
      warengruppendefiniert ist. Wenn ja, wird bei der Suche nach Kontrakten zu
      einem Artikel durch alle Warenpositionen gesucht, ob eine dabei ist, die
      der richtigen Warengruppe zugehört. Es erfolgt dann eine Abbuchung aus dem
      Kontrakt.
Rabatte zulassen
Hier
      wird entschieden, ob automatische Gruppen- und Zeilenrabatte
      zulässig sind.
RW-Rechnung an HK
(nur bei
      Rohwarekontrakten)
Wenn
      ein Kontrakt verschiedenen Kunden/Lieferanten zugeordnet ist, so kann die
      Rechnungsstellung für den Hauptkunden oder die Lieferanschrift
      erfolgen.
RW-Zahlungspfl. = HK
(nur bei
      Rohwarekontrakten)
Festlegung, ob die Zahlung durch den
      Hauptkunden oder den Lieferempfänger erfolgt.
Abbuchungsmengen
(nur b
[...]


---

## Stammdaten 1 (Kontrakt)

Stammdaten 1 (Kontrakt)
Der Programmteil Kontraktverwaltung ist zuständig für
die Eingabe und Bearbeitung aller Kontraktstamminformationen (Kunde, Termine,
etc.), der Warenpositionen und Warenbewegungen. In die Erfassungsmaske gelangt
man über den bekannten Auswahlbildschirm. In dieser Erfassungsmaske sind alle
Stammdateninformationen auf einer Bildschirmseite zusammengefasst. Bearbeitet
werden in dieser Erfassungsmaske alle Kontraktklassen; es stehen also
prinzipiell alle Funktionen sowohl dem Ein- als dem Verkauf zur Verfügung.
Rechts oben am Bildschirm wird mit der Anwahl ein
Funktionsauswahlfenster geöffnet, dessen Inhalte jedoch vom Bediener, von der
Kontraktklasse und der Kontraktgruppe (siehe später) abhängen. Deshalb werden
diese Funktionen erst ab der Position „Einzel-/Gesamtmengen“ zur Verfügung
gestellt.
Stammdaten 1
Hinweisfeld:
Aktiv
Hier
      werden alle Kontrakte insofern unterschieden, dass aktive und archivierte
      separat geführt werden, so dass man bei sehr vielen archivierten
      Kontrakten nicht immer alle diese überlesen muss, um die aktiven zu
      finden. Bei der Neuanlage ist hier keine Eingabe
      erforderlich.
Hinweisfeld:
Kein
      Artikel zugeordnet
Sollten dem Kontrakt keine Artikel
      zugeordnet sein, erscheint ein roter Text oben rechts auf der
      Registerkarte.
Mengen-/Wertkontrakt
Ein
      Kontrakt kann als Mengen oder als Wertkontrakt gehandelt
      werden.
Matchcode
Eingabe des gewünschten
      Matchcodes.
Standard – Kontrakt -
      Variante
Kennzeichen, ob es sich um einen
      „Standardkontrakt“ handelt, und ggf. um welchen Typ:
Dispositionskennzeichen
Identifikation des
      Dispositionsmerkmals, das die Gegenüberstellung („Auszifferung“) von Ein-
      und Verkaufskontrakten oder deren Teilpartien ermöglicht.
Mittels eines Steuerungsparameters
      kann aktiviert werden, dass beim Erfassen von Einkaufskontrakten
      automatisch Dispo-Kennzeichen mit identischer Nummerierung e
[...]


---

## Standardkontrakt

Standardkontrakt
Mittels der
F2
-Taste oder des Funktionsauswahlmenüs
gelangt man zur Erfassung von Artikeln, Mengen und Preisen. Im Fall des
Standardkontraktes gibt es nur einen (identischen) Preis-/Mengenzeitraum (siehe
Laufzeit von - bis), so dass die Erfassung hier einfach abgehandelt werden kann.
Nach der Eingabe obiger Informationen wird der Erfassungsbildschirm für die
Neuerfassung eines Artikels
aufgerufen.

---

## Standard-Kontrakt-Variante

Standard-Kontrakt-Variante
Standardkontraktvariante
0
kein
      Standardkontrakt
1
Standardkontrakt mit 1 Mengen- und 1
      Preiszeitraum.
Im
      Falle des Standardkontraktes ändern sich natürlich die
      Eingabe-Möglichkeiten. Das Funktionsauswahlfenster wird an diese Variante
      angepasst.
2
Monatlich lineare
      Abnahme
Monatlich wird immer die gleiche
      Menge abgenommen. Sie errechnet sich aus der später einzugebenden
      Gesamtmenge und der Anzahl der Vorauszeiträume (s.u.)
3
Wöchentliche lineare
      Abnahme
Es ist möglich, Kontraktmengen bei der
Kontrakterfassung nicht nur monatsweise linear zu verteilen, sondern auch
wochenweise. Der Unterschied besteht darin, dass die monatliche Verteilung sich
spätestens ab dem zweiten Monat automatisch mit dem Kalendermonat
synchronisiert, die wochenweise Verteilung aber nicht, so dass es auch möglich
ist, alle Wochen von Mittwoch bis Dienstag laufen zu lassen. Maximal 200 Wochen
sind derzeit möglich.

---

## Steuerparameter und Konstanten

Steuerparameter und Konstanten
Mit zahlreichen
Steuerparametern
kann die
Kontraktverwaltung an individuelle Belange angepasst werden.

---

## Kontraktwesen

Kontraktwesen

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

## Rohware-Wandlung

Rohware-Wandlung
Mit der Funktion
Rohware-Wandlung
können
Lieferscheine in Rohware-Lieferscheine gewandelt werden, wenn sie die dafür
notwendigen Bedingungen erfüllen.
Zunächst einmal muss die Wandlung durch
das Kennzeichen
Rohware Vorerfassung
in der Anwendung
Vorgangsunterklasse
[FRZ]
mit einem der Werte
‚möglich‘
oder
,geprüft‘
für die Unterklasse des Lieferscheins belegt sein. Im
ersten Fall werden nachfolgende Bedingungen für eine Rohware-Wandlung beim
Aufruf der Wandlungsfunktion geprüft und die Wandlung gegebenenfalls abgelehnt.
Im zweiten Fall erfolgt die Prüfung bereits bei Abschluss der
Lieferschein-Erfassung. Dadurch ist dann aber für diese Unterklasse kein
Lieferschein erfassbar, der die Wandlungsvoraussetzungen verletzen würde, obwohl
er vielleicht ohnehin nicht zur Wandlung vorgesehen ist. Daher empfiehlt sich
die Einstellung
‚geprüft‘
genau dann, wenn eine eigens für die zur
Rohware-Wandlung vorgesehenen Lieferscheine geschaffene Vorgangsunterklasse
vorhanden ist.
Es können nur Lieferscheine in Rohware-Lieferscheine
gewandelt werden, wenn
-
der Lieferschein genau eine Warenposition enthält
-
der Artikel der Warenposition ein Rohwareartikel ist (eingetragene
Rohwarengruppe)
-
der Lieferschein über keine Zeilen- und Gruppen-Rabatte, -Frachten und
-Zu-/Abschläge verfügt
-
ein im Lieferschein bereits zugeordneter Kontrakt ein Rohwarekontrakt ist
-
keine Gebinde-Mengeneinheit zur Erfassung genutzt wurde
-
der Lieferschein keine Gefahrgutinformation enthält
-
keine Streckenzuordnung vorhanden ist
-
keine oder genau eine Partie zugeordnet ist
-
eine per UFLD-Feld erfasste abweichende Schemanummer zur Rohwarengruppe des
Artikels passt
Nach erfolgreicher Durchführung der Wandlung ist der
Lieferschein nicht mehr in den Lieferschein-Auswahllisten vorhanden, da er ja
nun aufgrund seines Rohware-Charakters im Rohwaremodul dargestellt wird.
ACHTUNG: VorgangsAddOn-Daten werden grundsätzlich bei
der Wand
[...]


---

## Textbausteine

Textbausteine
Die Textbausteine stehen in enger Beziehung zu den
Ausdruckvarianten. Dort werden für die verschiedenen Anforderungen im
Kontraktbestätigungsschreiben, etc. Texteingabemöglichkeiten zur Verfügung
gestellt, die hier den individuellen Anforderungen des konkreten Kontraktes
angepasst werden. Natürlich ist es sinnvoll, die Vorbelegung in den
Kontraktvarianten möglichst vollständig zu erfassen, umso weniger muss hier
ergänzt oder korrigiert werden:
Hier wird auch die Bedeutung des Musterkontraktes
sichtbar. Für den Standardvorfall „Getreidekontrakt“ sind alle Standards
inklusive der Texte sinnvoll vorbelegt, nur Änderungen müssen vorgenommen
werden. Soll dies beim Text geschehen, wird er aufgerufen und geändert:

---

## Varianten kopieren

Varianten kopieren
Wird in der Auswahlliste der Kontraktvarianten die
Funktion
Varianten kopieren
aufgerufen, erscheint die Maske „Kontraktvarianten kopieren“.
Im Kopf der Maske stehen folgende Felder zur
Verfügung.
Feld
Beschreibung
Ursprungsvariante
Nummer der Variante von der die
      Bereiche kopiert werden sollen.
Bezeichnung
Bezeichnung der
      Ursprungsvariante
Zielvariante
Nummer der Zielvariante, dies kann
      eine bereits existierende Variante sein oder eine neue Nummer.
Bezeichnung
Bezeichnung der Zielvariante,
      handelt es sich um eine neue Variante kann hier die Bezeichnung der
      Zielvariante angegeben werden.
Felder in der Datentabelle der Ursprungsvariante.
Feld
Beschreibung
Lfd.Nr.
Die
      laufende Nummer des Bereichs.
(Doppelklick überträgt die Zeile in die
      Zielvarianten Datentabelle)
Bezeichnung
Bezeichnung des Bereichs
Formularbereich
Typ
      des Formularbereichs (
Kontraktvariantenbereich
)
Felder in der Datentabelle der Zielvariante.
Feld
Beschreibung
Kopie
Das
      Feld gibt an, ob die Zeile eine Kopie aus der Ursprungsvariante
      ist.
Lfd.Nr.
Die
      laufende Nummer des Bereichs. Es dürfen keine doppelten Nummern vergeben
      werden.
(Doppelklick entfernt die Zeile aus der
      Datentabelle)
Bezeichnung
Bezeichnung des Bereichs
Itembox
Das
      Feld gibt an, ob die
privaten
      Itemboxes
für Festtexte mit kopiert werden sollen.
Defaultwert
Das
      Feld gibt an, ob die
Standardwerte
mit kopiert werden sollen.
Mit der Funktion
Start kopieren
werden dann die zu
kopierenden Bereiche in die Zielvariante übertragen.

---

## Vermehrungsvertrag

Vermehrungsvertrag
Hauptmenü
Saatzucht
Saatgutabwicklung
Vermehrnungsvertrag
Direktsprung
[SAATV]
Name
Bedeutung
Vertragsnummer
Die
      eindeutige Vertragsnummer für diesen Datensatz.
Erntejahr
Das
      Jahr der Ernte. Es wird nicht gespeichert, sondern steuert die Anzeige in
      der Datentabelle.
Wird
      hier 0 eingetragen, so werden alle Vorhandenen Schläge angezeigt,
      ansonsten nur die des Erntejahres.
Mit
      dem Einrichterparameter „
Aktuelles Jahr als Erntejahr verwenden, sonst
      Geschäftsjahr
“ kann die Vorbelegung des Erntejahrs eingestellt
      werden.
Vermehrer
Hier
      wird die Vermehrernummer - dies ist die Kundennummer aus dem Kundenstamm -
      eingetragen. Mit der F3-Taste kann hier eine Auswahl aufgerufen
      werden
.
Plz/Ort
Die
      Postleitzahl und der Ort des Vermehrers werden hier angezeigt.
Vertreter
Der
      Vertreter zum Vermehrer wird hier angezeigt.
LWK
      offiziell
Landwirtschaftskammer
      offiziell/Anerkennungsstelle. Mit der Taste
F3
kann hier eine
      Auswahl (
IB_Anerkennungsstelle
) aufgerufen
      werden
.
VMKz.
Die
      Vermehrerkennziffer
Registriernummer
Vertragsart
Die
      Vertragsart.
Mit der
      Taste
F3
kann hier eine
      Auswahl (
AF_VERTART
) aufgerufen werden.
Auftragsnummer
Die
      Auftragsnummer
Sortennummer
Die
      Sorte kann hier ausgewählt werden.
Mit der Taste
F3
kann hier eine
      Auswahl (
IB_SGALLESORTEN
) aufgerufen werden
.
Kategorie
Die
      Kategorie der Saatsorte kann hier eingetragen werden. Mit der
      Taste
F3
kann hier eine
      Auswahl (IB_SGKATEGORIE) aufgerufen werden.
Artikel
Der
      Artikel kann hier ausgewählt werden.
Mit der Taste
F3
kann hier eine
      Auswahl (IB_ARTIKEL_FRUSORKAT) aufgerufen werden
.
Aussaat
Der
      Zeitpunkt der Aussaat.
Laufzeit von bis
Die
      Laufzeit dieses Vermehrungsvertrages.
VO-Firma
Identifikation zum Kundenstammsatz
      der VO - Firma (Vemehrerorganisation). Mit der F3-Taste k
[...]


---

## Vertreterabrechnung

Vertreterabrechnung
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreterabrechnung
Direktsprung
[VERA]
Hier findet die eigentliche Vertreterabrechnung statt.
Dabei stehen 5 Varianten zur Verfügung.

---

## Vertreterabrechnung Variante 1(noch zu provisionierende Belege)

Vertreterabrechnung Variante 1(noch zu provisionierende Belege)
Diese Varianten charakterisieren die Vorgehensweise
während der Vertreterabrechnung. Diese lässt sich in zwei Stufen
unterteilen:
In der 1. Variante sind alle Belege zu sehen, die
innerhalb des gewählten Profils noch nicht durch die Provisionierung gelaufen
sind. Jetzt kann man in der 1.Stufe durch Markieren Belege provisionieren. Die
Provisionierung
(F9)
erzeugt gemäß
der untenstehenden Konventionen Einträge in die Relation Warenprovision, d.h.
die Provisionierung erfolgt auf WarenBewegungsebene. Nach der Provisionierung
verschwinden die Belege aus der Anzeige und laufen in die 2. Variante. Die
Provisionierung selbst kann also für durch den Mandantenserver gelaufene Belege
zu jeder Zeit erfolgen. Allerdings sollte man vor dem Auslösen dieser Funktion
sicherstellen, dass alle Stammdaten im Bereich Vertreter korrekt eingerichtet
sind. Während der Provisionierung wird in der Statuszeile (unten am Bildschirm
angezeigt, welcher Beleg gerade durch die Provisionierung läuft. Durch
beliebigen Tastendruck kann man die Provisionierung abbrechen und sie hält nach
Abarbeiten des aktuellen Beleges an. Man kann sie dann zu einem späteren
beliebigen Zeitpunkt fortsetzen, die bereits abgearbeiteten Belege tauchen in
der Liste der noch zu bearbeitenden Belege nicht mehr auf).
Felder:
Feld
Bedeutung
Klasse
Klasse der Abrechnung
VertGrup
Vertretergruppe
Beleg
Beleg für die Abrechnung
BelegDat
Beleg Datum
Kunde
Kunden ID
Bezeichnung
Kunden Name
Nettobetrag
Steuerbetrag
Suchmöglichkeiten
Feld
Bedeutung
Jahr
Von…
      Bis…
Belegnummer
Von…
      Bis…
Belegdatum
Von…
      Bis… (Datum)
Kunde
Von…
      Bis…
VertreterGruppe
Von…
      Bis…
Tour
Von…
      Bis…
Station
Von…
      Bis…
Periode
Von…
      Bis… (Monatszahl)
Unterklasse
Von…
      Bis…
EK/VK
0:
      Alles
1: Verkauf
2: Einkauf
Kundengruppe
%
Oberkunde
Von…
      Bis…
Funktionen:
Funktion
Beschreibung
Keine Provision
(F7)
Provisionserm
[...]


---

## Vertreterabrechnung Variante 2(Provisionierte unabgerechnete Bewegungen)

Vertreterabrechnung Variante 2(Provisionierte unabgerechnete
Bewegungen)
In der 2.Variante sind alle durch den 1.Schritt
erzeugten Warenprovisionen zu sehen, wenn sie innerhalb des gewählten Profils
liegen und noch nicht abgerechnet sind. Zu diesem Zeitpunkt hat man zwei
Möglichkeiten:
entweder man löscht die Provisionierung
F7
, d.h. die Einträge in die Relation
Warenprovision werden für alle markierten Belege gelöscht und die Stati werden
gemäß der untenstehenden Konvention gelöscht. Dabei kann ein Löschen nur dann
erfolgen, wenn noch keine Warenbewegung des markierten Beleges bereits
abgerechnet ist. Wenn dieses Kriterium erfüllt ist, wird die Provisionierung des
markierten Beleges zurückgesetzt und die zugehörigen Einträge verschwinden in
der Auswahlliste und landen in der 1. Variante.
oder man führt die Vertreterabrechnung
F9
durch, d.h. hier kann man für über das
Profil ausgewählte Vertreter durch Markierung die Provisionierungen in
Abrechnungslisten zusammenfassen. Hierbei bekommen alle markierten
Warenprovisionen die gleiche Abrechnungsnummer, die aus dem Nummernkreis gezogen
wird, die in MNDNK (Mandantenstammnummernkreiszuordnung) der Vertreterabrechnung
zugeordnet ist. Auch in diesem Fall verschwinden die markierten Sätze aus der
Auswahlliste und landen in der 4. Variante.
Felder:
Feld
Bedeutung
Vert.
Vertreter
Bezeichnung
Bezeichnung des
      Vertreters
AbrLi-Nr.
Abrechnungslisten-Nummer
AnzBel
Anzahl Belege
Peri/Jahr
Periode / Jahr
Belege v
Belege von
Bis
Belege bis
Gebinde
Menge
Gewicht
Wert
BezMenge
Bezeichnung Menge
BezWert
Bezeichnung Wert
Provision
Anteil
VertGrup
Vertreter Gruppe
ProvGrup
Provisionsgruppe
Suchmöglichkeiten
Feld
Bedeutung
Jahr
Von…
AbrLi-Nr.
Von…
      Bis…
Vertreter
Von…
      Bis…
Kunde
Von…
      Bis…
Funktionen:
Funktion
Beschreibung
Keine Provision
(F7)
Provisionsermittlung
(F9)

---

## Vertreterabrechnung Variante 3(Belege ohne provisionierte Warenbewegung)

Vertreterabrechnung Variante 3(Belege ohne provisionierte
Warenbewegung)
In der 3. Variante werden alle Belege angezeigt, die
durch die Provisionierung gelaufen sind, aber zu denen keine provisionierte
Warenbewegungen existieren, weil sie unter die Konvention 99 fallen. Man hat
jetzt noch die Möglichkeit, die „Nicht-Provisionierung“ des Beleges
zurückzusetzen über F7. Dadurch kann man z.B. Provisionsdaten nachtragen, die
für diesen Beleg notwendig sind.
(ACHTUNG: eine etwaige Änderung der Daten wirkt sich
nicht auf abgerechnete Beleg aus)
Felder:
Feld
Bedeutung
Klasse
Klasse der Abrechnung
VertGrup
Vertretergruppe
BelegNummer
Beleg für die Abrechnung
BelegDat
Beleg Datum
Netto
Steuer
Unterklasse
Suchmöglichkeiten
Feld
Bedeutung
Vertretergruppe
Von…
      Bis…
Belegnummer
Von…
      Bis…
Belegdatum
Von…
      Bis… (Datum)
Funktionen:
Funktion
Beschreibung
Keine Provision
(F7)
Provisionsermittlung
(F9)

---

## Vertreterabrechnung Variante 4(Provi., unabgerechnete Beweg. (je Vert.))

Vertreterabrechnung Variante 4(Provi., unabgerechnete Beweg. (je
Vert.))
Die 4.Variante zeigt alle provisionierte
Warenbewegungen an, die noch nicht abgerechnet sind und gruppiert diese nach
Vertretern, d.h. man kann hier sehen, wieviel Provision jedem einzelnen
Vertreter noch zusteht.
Felder:
Feld
Bedeutung
Vert.
Vertreter
Bezeichnung
Bezeichnung des
      Vertreters
AbrLi-Nr.
Abrechnungslisten-Nummer
AnzBel
Anzahl Belege
Peri/Jahr
Periode / Jahr
Belege v
Belege von
Bis
Belege bis
Gebinde
Menge
Gewicht
Wert
BezMenge
Bezeichnung Menge
BezWert
Bezeichnung Wert
Provision
Anteil
VertGrup
Vertreter Gruppe
ProvGrup
Provisionsgruppe
Suchmöglichkeiten
Feld
Bedeutung
Jahr
Von…
AbrLi-Nr.
Von…
      Bis…
Vertreter
Von…
      Bis…
Kunde
Von…
      Bis…
Funktionen:
Funktion
Beschreibung
Keine Provision
(F7)
Provisionsermittlung
(F9)

---

## Vertreterabrechnung Variante 5(Abgerechnete Listen)

Vertreterabrechnung Variante 5(Abgerechnete Listen)
In der 5. Variante erscheinen jetzt nach Abrechnungen
geordnet die Abrechnungslisten. Diese Listen kann man durch
F7
Löschen Abrechnung wieder in die 2.
Variante zurückbringen, d.h. die Zusammenfassung in Abrechnungslisten wird
aufgehoben. Dieses geschieht wiederum für alle markierten Sätze. Außerdem kann
man von hier die CRW-Reports aufrufen.
Felder:
Feld
Bedeutung
Vert.
Vertreter
Bezeichnung
Bezeichnung des
      Vertreters
AbrLi-Nr.
Abrechnungslisten-Nummer
AnzBel
Anzahl Belege
Peri/Jahr
Periode / Jahr
Belege v
Belege von
Bis
Belege bis
Gebinde
Menge
Gewicht
Wert
BezMenge
Bezeichnung Menge
BezWert
Bezeichnung Wert
Provision
Anteil
VertGrup
Vertreter Gruppe
ProvGrup
Provisionsgruppe
Suchmöglichkeiten
Feld
Bedeutung
Jahr
Von…
AbrLi-Nr.
Von…
      Bis…
Vertreter
Von…
      Bis…
Kunde
Von…
      Bis…
Funktionen:
Funktion
Beschreibung
Keine Provision
(F7)
Provisionsermittlung
(F9)

---

## Vertreterdaten

Vertreterdaten
Innerhalb der Vertreterdaten können alle Daten erfasst
werden, um die Berechnung/Abrechnung von Vertreterprovisionen durchzuführen.

---

## Vertreteranteile

Vertreteranteile
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreter Anteile
Direktsprung
[VEA]
Hier werden die Anteile an Provision bzw. Umsatz der
Vertretergruppe je Vertreter angezeigt
Jeder Vertreter kann an mehreren
Vertretergruppen (z. B. mit verschiedenen Anteilen) beteiligt sein.
Ein Anteil kann entweder einem Vertreter oder wieder
einer Vertretergruppe zugeordnet sein.
Felder der Vertreteranteile
Feld
Bedeutung
Vertreter
ID
      des Vertreters
Hat in
Name
      des Vertreters
Gruppe
Vertretergruppe in der sich der
      Vertreter befindet.
Einen Anteil von:
Name
      der Vertretergruppe
Anteil
Prozentualer Anteil des Vertreters
      in dieser Provisionsgruppe
Suchmöglichkeiten der Vertreteranteile
Feld
Bedeutung
Vertreter
Von…
      Bis…
Funktionen der Vertreteranteile
Diese Auswahlliste dient lediglich zur Übersicht und
hat keine Funktionen.

---

## Vertretergruppen

Vertretergruppen
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertretergruppen
Direktsprung
[VEG]
Vertretergruppen können bei der Provisionierung und
den Anteilen wie Vertreter behandelt werden. Richtig erfasst erlauben sie es,
ein- und mehrstufige Provisionierungen, Gebietsaufteilungen, Einsatz
unterschiedlichster Provisionierungsmodelle durchzuführen.
Vertretergruppen bestehen stets aus ein oder mehreren
Vertretern, die eventuell verschiedene Anteile an der Provisionierung der Gruppe
zugewiesen bekommen.
Ein Vertreter kann natürlich in mehreren
Vertretergruppen eingetragen sein.
Eine Provisionierung erfolgt generell nur über die
Vertretergruppe, nie über den Vertreter direkt - es kann natürlich einfache
Vertretergruppen geben, die nur einen Vertreter haben, der 100 Prozent der
Provision der Gruppe bekommt.
Vertretergruppe 0 bedeutet per Definition, dass keine
Provision ausgeschüttet wird.

---

## Vertreterklasse

Vertreterklasse
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreterklassen
Oder Direktsprung
[VEKL]
Vertreterklassen dienen in Referenz-ERP als Gruppierung für
Vertreter. Der Klassenname sollte also die Gruppierung bestmöglich
beschreiben.
Felder der Vertreterklasse
Feld
Bedeutung
Klasse.
Gibt
      die Klassennummer an.
Bezeichnung
Gibt
      den Klassennamen an.
Suchmöglichkeiten der Vertreterklasse
Feld
Bedeutung
Klasse
Von…
      Bis…
Funktionen der Vertreterklasse
Feld
Bedeutung
Ändern (F5), Ansicht (F6), Löschen
      (F7), Neu (F8)
Ruft
      den Pfleger des Vertreterstamm auf.

---

## Vertreter Provision

Vertreter Provision
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreter Provisionen
Direktsprung
[VEP]
Wahlweise kann die Provision abhängig von der
Vertretergruppe oder vom einzelnen Vertreter festgelegt werden. Beide tauchen
deshalb als Schlüsselattribut auf, von denen aber stets nur eins belegt sein
darf.
Je Vertreter/Vertretergruppe, Provisionsgruppe und
abgegrenzt durch ein Gültigkeitsdatum werden hier die Berechnungsmethode und die
Höhe der Provision festgelegt.
Felder:
Feld
Bedeutung
Vertreter
Zeigt die Nummer des Vertreters
      an
PrGru
Zeigt die Provisionsgruppe
      an
Typ
Gibt
      den Typ an (Einkauf/Verkauf)
PrAbDatum
Formel
Gibt
      an wie die Provision berechnet wird.
Prozent
Gibt
      an, wie viel Prozent Provision der Vertreter bekommt
Betrag
Gibt
      den Endbetrag der Provision an
Suchmöglichkeiten:
Feld
Bedeutung
Vertreter
Von…
      Bis…
Funktionen
Diese Auswahlliste dient lediglich zur Übersicht und
hat keine Funktionen.

---

## Vertreterprovisionsgruppen (Provisionstypen)

Vertreterprovisionsgruppen (Provisionstypen)
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreterprovisionsgruppe
Direktsprung
[VEPGR]
Wahlweise kann die Provision abhängig von der
Vertretergruppe oder vom einzelnen Vertreter festgelegt werden. Beide tauchen
deshalb als Schlüsselattribut auf, von denen aber stets nur eins belegt sein
darf. Je Vertreter/Vertretergruppe, Provisionsgruppe und abgegrenzt durch ein
Gültigkeitsdatum werden hier die Berechnungsmethode und die Höhe der Provision
festgelegt. In diesem Eingabebildschirm können mit Hilfe folgender Funktionen
die nachfolgenden Felder bearbeitet werden.
Provisionsgruppe
Die Provisionsgruppe, wie im Artikelstamm
hinterlegt
Ist für die jeweilige Provisionsgruppe kein gültiger
Provisionssatz hinterlegt, so wird mit Provisionsgruppe 0 (= „Fehlwert“)
weitergesucht. Daher ist es sinnvoll, je Vertreter mindestens einen
Provisionssatz mit Provisionsgruppe 0 und gültig von Anfang an zu hinterlegen.
Dies wird vom System automatisch durchgeführt.
Provisionstyp Einkauf / Verkauf
1     =   es gilt die
Standard-Formel entsprechend der Eintragung in der Vertreter-Provisions-Gruppe
(Vertreterprovisions-Formel EK bzw. VK). Nachfolgend besteht die Möglichkeit,
die Standardvorbelegungen in der Provisionsgruppe für diesen einen
Provisionssatz zu überschreiben:
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
8     =   Provision mit
variablen Mengenbezug
10   =   Staffelung in max. 10
Provisionsberechnungen (siehe unten Provisionsstaffelung)
11   =   Überschussprovision
20   =   Staffelprovision Preis +
Zu – und Abschläge
21   =   Überschussprovision Preis
+ Zu – und Abschläge
101 =   rohgewinnbezogene Provision
Abrechnungstag

---

## Vertreterprovisionstabellen

Vertreterprovisionstabellen
Bei der Einrichtung der Provisionstabellen im
Vertreterstamm bzw. Vertretergruppen muss Folgendes bedacht werden.
Es gibt
grundsätzlich zwei unterschiedliche Ansätze:
Wenn ein stimmiger Abgleich der Vertreterabrechnung
mit z.B. der Verkaufsauswertung gewünscht wird, müssen alle Provisionsgruppen in
den Provisionstabellen eingerichtet sein, also auch solche, die z.Zt. für den
entsprechenden Vertreter/-gruppe nicht angesprochen werden. (mit Satz/Wert 0.00
einrichten!). Nur dann ist gewährleistet, dass Umsätze ohne Provision
(Provision: 0.00) mit gedruckt werden.
Die Umsatzsummen müssen dann mit
einer analogen Selektion in der Verkaufsauswertung übereinstimmen.
Sollen in der Vertreterabrechnung nur Umsätze mit
tatsächlicher Provision gedruckt werden, so dürfen nur Provisionsgruppen in den
Provisionstabellen eingerichtet werden, die eine effektive Provision vorsehen
(mit Satz/Wert > 0.00). Umsatzsummen können dann allerdings nicht mehr mit
anderen Auswertungen übereinstimmen, da nicht provisionierte Umsätze
ausgeblendet sind! (Hinweis: Im Fehlerprotokoll
[FEHLP]
werden für jeden neuen
Vertreterabrechnungslauf nicht eingerichtete Provisionsgruppen als Warnung
vermerkt.)

---

## Vertreterstamm

Vertreterstamm
Hauptmenü
Nebenbuchhaltungen
Vertreterabrechnung
Vertreterstamm
Oder Direktsprung
[VE]
In den Vertreterstammdaten werden alle Informationen
zusammengefasst, um Vertreterabrechnungen, -auswertungen etc. durchzuführen.
Richtig erfasst erlauben sie es, ein- und mehrstufige Provisionierungen,
Gebietsaufteilungen, Einsatz unterschiedlichster Provisionierungsmodelle
durchzuführen.
Je Vertreter gibt es einen Vertreterstamm für
Auswahlen, Gruppierungen und zur Provisionsberechnung.
Jeder Vertreter sollte
eine Anschrift haben und wohl auch mindestens zu einer Vertretergruppe gehören,
weil nur diese Provisionsverweise zugewiesen bekommen.
Im Vertreterstamm gibt es 2 Varianten der
Auswahlliste:

---

## Formate

Formate
Hier finden Sie die Formate, welche im
Streckenerfassungsprofil verwendet werden.
Streckenmenüzuordnung
Partie bei
Übermenge
Lagerauswahl
Lagerbezogene
Artikelauswahl
Zeitintervall
eines Kontrakts
Reporttyp
Auswertungstyp
Streckenmenüzuordnung
Mit diesem Format kann die Streckenmenüzuordnung
festgelegt werden. (
Formatname „DISPOMENUZ“
)
Nr.
Bezeichnung
Beschreibung
0
Verkauf / Einkauf
Menüzuordnung in Verkauf und
      Einkauf
1
Verkauf
Menüzuordnung nur im
      Verkauf
2
Einkauf
Menüzuordnung nur im
      Einkauf
Partie bei
Übermenge
Mit diesem Format wird festgelegt, welche Partie bei
einer Übermenge gezogen wird. (
Formatname „SE_PARTIE“
)
Nr.
Bezeichnung
Beschreibung
0
Erste Partie
Die
      erste gefundene Partie wird gezogen.
1
Letzte Partie
Die
      letzte gefundene Partie wird gezogen.
Lagerauswahl
Mit diesem Format wird festgelegt, aus welchem Lager
der Artikel gezogen werden soll. (
Formatname „SE_AUSWLAGER“
)
Nr.
Bezeichnung
Beschreibung
0
Standardlager
Der
      Artikel wird über das Standardlager gezogen.
1
Kundenlager
Der
      Artikel wird über das Kundenlager gezogen.
Lagerbezogene Artikelauswahl
Mit diesem Format wird festgelegt, wie ein Artikel
Lagertechnisch gezogen wird. (
Formatname „SE_AUSWARTIK“
)
Nr.
Bezeichnung
Beschreibung
0
Lagerbezogen
Der
      Artikel wird hierbei Lagerbezogen ermittelt.
1
Lagerübergreifend
Der
      Artikel wird hier Lagerübergreifen ermittelt.
Zeitintervall eines Kontrakts
Mit diesem Format wird festgelegt, wie der
Zeitraumintervall eines Kontraktes ist. (
Formatname „KTRINTERVALL“)
Nr.
Bezeichnung
Beschreibung
0
Tag
Die
      Kontraktzeiträume sind einen Tag lang.
1
Woche
Die
      Kontraktzeiträume haben eine Laufzeit von einer Woche.
2
Monat
Die
      Kontraktzeiträume haben eine Laufzeit von einem Monat.
3
Jahr
Die
      Kontraktzeiträume haben eine Laufzeit von einem Jahr.
Reporttyp
Mit diesem Format wird festgelegt, um was für einen
Report es sich handelt.
(Formatname „DISPREPO
[...]


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

## Disponierte Menge

Disponierte Menge
Das Feld steht in Abhängigkeit zur Kontraktmenge.
Dieses Feld wurde hinzugefügt, da in der Hofliste erst bei der Vorgangserzeugung
eine Kontraktprüfung stattfindet. Um zu verhindern, dass zu viel Ware
angeliefert oder abgeholt wird, trägt man in dem Feld „Disponierte Menge“ einen
Schätzwert ein.
Die eingegebene Menge wird dann mit allen
anderen „Disponierten Mengen“ bis zum Waagen Status „erste Wiegung“ und alle
Nettomengen die den Waagen Status „zweite Wiegung“ oder „ Abgeschlossen“ haben
zusammenaddiert. Die addierte Menge wird dann gegen den Kontrakt geprüft.
Beispiel:
Vor der Waage stehen 18 LKWs, die auf einen Kontrakt
anliefern, aber nach dem 13. LKW ist schon klar, dass danach der Kontrakt
erfüllt sein wird. Also kann man ab dem 14. LKW alle anderen wegschicken.

---

## Kontraktneuanlage

Kontraktneuanlage
Mit dieser Funktion wird eine neue Maske aufgerufen,
mit der in einfacher Version ein Kontrakt angelegt werden kann.
Ist der Wiegung schon ein Kontrakt zugeordnet, so
werden die Kontraktinformationen angezeigt.
Maskenfelder
Bedeutung
Kontrakt
Dieses Feld wird angezeigt, wenn der
      Wiegung ein Kontrakt zugeordnet wurde.
Kunde
Dieses Feld wird mit der
      Kundennummer aus der Waage vorbelegt. Wenn kein Kunde angegeben worden
      ist, kann hier ein Kunde eingegeben werden.
Sollmenge
Sollmenge des Kontraktes
Variante
Kontraktvariante
Lager
Wird
      aus der Waage vorbelegt
Preisart
Anwenderformat af_Pricing. Folgende
      Standardwerte werden ausgeliefert.
•
0
      Basis
•
1 DP
•
2
      HTA
Bemerkung
Bemerkungsfeld
Artikel
Der Artikel wird aus der Wiegung vorbelegt und kann
nicht manuell hinzugefügt werden.

---

## Kontraktbearbeitung

Kontraktbearbeitung

---

## Partiepflicht

Partiepflicht
Um dem Anwender zu ermöglichen, selbst zu entscheiden,
ob mit oder ohne Partiezwang gearbeitet wird, gilt folgende Wirkungsweise:
Für die Wiegetypen „Rohwareneingang“ und
„Rohwarenausgang“ wird das Feld ‚Partiezuordnung’ (0 = egal, 1 = immer mit
Partie, 2 = ohne Partie) des Artikels auf der Artikelmaske herangezogen. Bei der
Einstellung „immer mit Partie“ wirkt die Partiepflicht in der Waage.
Für andere Wiegetypen hängt die Partiepflicht
weiterhin davon ab, ob der Artikel ein Saatgutartikel ist. In diesem Fall gilt
die Einstellung des Steuerparameters 267 „Zwangs-Partie bei
Saatgut-Lieferung“.

---

## Rohware an der Waage

Rohware an der Waage
Abrechnungsschema(Sorte)
In den Abrechnungsschemas einer Rohwarengruppe könne
folgende Einstellungen für die Übergabe von Werten aus der Waage in den
Rohwarenbeleg verändert werden. Es gibt zwei Arten von Waagenparameter einmal
die Globalen Parameter und die Parameter, die pro Abrechnungsschema gelten.
Globale
Waagenparameter
Feldname
Wert
Liefernummer
0.   Aus Waage
1.   Aus
      Nummernkreis(Standard)
Lieferdatum
0.   Aus Waage
      (Standard)
1.
      Tagesdatum
Sortennummer
0.   Aus Waage
      (Standard)
1.   Default
      Waagensorte
Lagernummer
0.   Aus Waage
      (Standard)
1.   Aus
      Vorgangskonstanten (Standardlager des Bedieners)
Lagerplatznummer
0.Immer Lagerplatz 0
      (Standard)
1.   Aus Waage
Filialnummer
0.   Aus Waage
      (Standard)
1.   Aus
      Vorgangskonstanten (Filiale des Bedieners)
Fakturiergruppe
0.   Entsprechend Sorte
      (Standard)
1.   Aus Waage
Vertretergruppe
0.   Entsprechend Sorte
      (Standard)
1.   Aus Waage
Versandart
0.   Entsprechend Sorte
      (Standard)
1.   Aus Waage
Verkaufsgebiet
0.   Entsprechend Sorte
      (Standard)
1.   Aus Waage
Abrechnungsschema Waagenparameter
Parametername
Einstellungsmöglichkeiten
Kontrakt
0.   Ohne
      Kontrakt
1.   Aus Waage
2.   Automatische
      Kontraktfindung
3.   Aus Waage, bei 0
      automatische Kontraktzuordnung
Partie
0.   Ohne
      Partie
1.   Aus Waage
2.   Automatische
      Partiezuordnung
3.   Automatische
      Partieanlage
Einlagerungsabrechnungsschema
Abrechungsschema für die
      Einlagerung
Kontraktlaufzeit Einlagerung in
      Tagen
Hier
      wird die Laufzeit des Einlagerungskontraktes in Tagen
      eingetragen
Kontraktunterklasse
      Einlagerung
Kontraktunterklasse für die Anlage
      bei eines Einlagerungskontraktes
Einlagerungs-Abrechnungs
      Verknüpfung
Hier
      wird die Abrechnungsart für den Rohwarenbeleg hinterlegt, welcher bei der
      Einlagerung angelegt wird.
0    (-) wenn 0
[...]


---

## Verkaufskontrakt Rohware (3) / Einkaufskontrakt Rohware (13)

Verkaufskontrakt Rohware (3) / Einkaufskontrakt Rohware (13)
In der Anwendung Kontrakte kann man z.B.
Verkaufskontrakte Rohware mit
F8
anlegen, wenn man als Kontraktklasse den Verkaufskontrakt Rohware (Klasse 3)
auswählt.
Man gibt danach die wichtigen Informationen zu diesem
Kontrakt ein, wie Kunde, Kontraktnummer, Standardkontrakt-Variante, Laufzeiten.
Wenn diese Maske gefüllt ist, kann über
F2
die Kontraktartikelmaske für die
Artikelangaben zum Kontrakt geöffnet werden. Dort werden Artikelnummer,
Kontraktmenge und Kontraktpreis angegeben. Zusätzlich kann man die
Rohwarengruppe und die Rohwarensorte angeben.
Nachdem nun ein Verkaufskontrakt Rohware angelegt
wurde, kann man in der Waage z.B. mit
F7
eine Warenausgangswiegung starten. Der
neu angelegte Kontrakt ist nun in der
F3-
Auswahl des Feldes Kontrakt enthalten.
Die Angaben wie Kunde und Artikel werden aus dem Kontrakt in die Waagenmaske
übernommen. Außerdem wird in diesem Fall der Wiegetyp von Warenausgang auf
Rohwarenausgang angepasst.
Nachdem eine Wiegung mit einem Rohwarenkontrakt
durchgeführt und abgeschlossen (
F11
)
wurde, können über die Funktion
Rohwarenbeleg
erzeugen
F9
in der
OptionBox der Auswahlliste Rohwarenbelege erzeugt werden. Aus diesen können dann
in den Anwendungen Rohwarenbeleg Einkauf oder Rohwarenbeleg Verkauf Lieferungen
erzeugt werden. Im Positionsteil der Lieferscheine ist dann der verwendete
Kontrakt enthalten. Nachdem dies geschehen ist, ist die gewogene Menge auch vom
Kontrakt runtergebucht. Dies kann man sich beim entsprechenden Kontrakt über die
Funktionen in der OptionBox Bewegung (
SF9
) oder Artikel (
F2
) anschauen.

---

## Rohwarenbeleg erzeugen

Rohwarenbeleg erzeugen
Diese Funktion ist obsolet. Rohwarenbelege werden
jetzt über die Funktion „
Vorgang erzeugen
“ erzeugt

---

## Waage auf abgeschlossen zurückstellen

Waage auf abgeschlossen zurückstellen
Mit dieser Funktion können Waagenbelege auf
‚Abgeschlossen‘ zurückgestellt werden, wenn diese auf ‚mit Vorgang‘ stehen, aber
kein Vorgang mehr zu diesem Waagenbeleg existiert. Handelt es sich um
Rohwarenbelege, so werden die dazu gehörigen Daten aus der Rohwarenübergabe
entfernt.
Bleibt der Waagenbeleg auf ‚Abgeschlossen‘ stehen, da
der Rohwarenbeleg nicht erzeugt wurde, so werden mit dieser Funktion die dazu
gehörigen Daten aus der Rohwarenübergabe entfernt.
Nach der Bereinigung steht der Datensatz wieder auf
‚Abgeschlossen‘. Die Belegerzeugung kann wieder erneut ausgeführt werden.

---

## Herkunft des Preises

Herkunft des Preises
Neben dem Preis gibt es ein Kennzeichen, das angibt,
aus welcher Quelle der Preis stammt. Als mögliche Quellen seien hier
beispielsweise Kontrakte und Preislisten genannt.
Eine manuelle Eingabe des Preises wird als solche
erkannt und setzt das Kennzeichen neu.
Auch andere Änderungen des Preises z.B. über ein Makro
oder eine Einspielschnittstelle können den Preis setzen. Da die Bezeichnung der
Herkunft dieser durchaus dynamisch entwickelten Einspielungen vielfältig sein
kann, wird ein eigenes Textfeld in der Datenbank bereitgestellt, in dem bis zu
20 Zeichen für die Preisherkunft gespeichert werden können.
Dieses Kennzeichen wird von der Einspielschnittstelle
nach der Preissetzung gesetzt und wird dann in der Erfassungsmaske statt der
Bezeichnung „manuelle Eingabe“ angezeigt.
Technische Beschreibung:
Das Feld WaBewPreisWoherText ergänzt die bekannte
Enumeration des Feldes WaBewPreisWoher durch flexible Beschreibung. Ist das
nummerische Kennzeichen auf manuell (99) gesetzt, so kann hier eine zusätzliche
Information hinterlegt werden. Diese überschreibt, wenn vorhanden auch auf der
Erfassungsmaske die Bezeichnung „manuelle Eingabe“.
Das Kennzeichen muss aus technischen Gründen stets
nach dem Setzen von Preis und Menge eingetragen werden und kann mit der ID
ID_WABEW_PREISWOHERTEXT gesetzt bzw. abgefragt werden.

---

## Zeiträume festlegen

Zeiträume festlegen
Zuerst wird bestimmt, für welchen Zeitraum die
Preis-/Mengenvereinbarungen gelten sollen. Dies erfolgt auf der ersten
Erfassungsseite des Kontraktstamms über die Funktionen
Mengenzeitraum
F10
und
Preiszeitraum
F11
. Nach Betätigen von
F8
können die Zeiträume, ggf.
unterschiedlich für Mengen und Preise, neu erfasst werden.
Für die Bearbeitung der Mengenzeiträume stehen
grundsätzlich zwei Datentabellen zwei Datentabellen zur Verfügung. In der ersten
Tabelle werden die Mengen- beziehungsweise Wert-Zeiträume des Kontrakts
dargestellt, abhängig davon, ob es sich um einen Mengen- oder Wertkontrakt
handelt. Neben Anfangs- und Enddatum des jeweiligen Zeitraums wird die
Gesamt-Sollmenge oder der Gesamt-Sollwert des Zeitraums dargestellt. Handelt es
sich bei dem Kontrakt um einen Einzelmengen- oder Einzelwert-Kontrakt, so
handelt es sich hierbei um die Summe der Sollmengen oder Sollwerte der
Kontraktartikel. Bei Gesamtmengen- /Gesamtwert-Kontrakten und bei
Einzelmengen-/Einzelwert-Kontrakten mit nur einer Kontraktartikelposition kann
der Wert direkt in dieser Spalte geändert werden. Die aktuelle Restmenge
beziehungsweise Restwert wird ebenfalls dargestellt.
Ist die Option
Steuerungsparameter
846 „Ratierliche Einstellungen“ „Ktr-Anzeige
Minusrest in Folgezeitraum“
mit dem Wert
Ja
eingestellt, so wird
eine zusätzliche Spalte
Rest>
0 dargestellt, die negative Restmengen
oder Restwerte eines Zeitraums mit der des Folgezeitraums verrechnet und selbst
mit dem Wert 0 darstellt. Die Einstellung der Option
Steuerungsparameter
846 „Ratierliche Einstellungen“ „Ktr-Anzeige
Kumulierte Zeitraum-Reste“
mit dem Wert
Ja
stellt in einer
weiteren Spalte den kumulierten Rest dar.
Änderungen von Soll-Mengen und Soll-Werten sowie
Zeitraum-Änderungen werden in einem Änderungsprotokoll dokumentiert.
Feld
Beschreibung
Angangsdatum
Beginn des
      Kontraktmengen-Zeitraums
Enddatum
Ende
      des Kontrakt-Zeitraums.
Gesamtmenge
Sollmenge des
      Kontrakt-Z
[...]


---

## Abbuchungsmenge (brutto/netto)

Abbuchungsmenge
(brutto/netto)
brutto:
Die jeweilige Liefermenge wird auf den
Kontrakt angerechnet.
Da bei der Vorfakturierung der Eigenbestand um diese
Menge verändert wurde, wird der Eigenbestand bei der Rohwarenbearbeitung um die
Differenz aus Liefer- und Abrechnungs-Menge korrigiert, während die Fremdware-
bzw. Fremdlager-Bestandsbuchungen mit der Liefermenge erfolgen.
netto:
Die jeweilige abgerechnete Menge der
Lieferposition wird auf den Kontrakt angerechnet. Es erfolgen keine
Eigenbestands-, wohl aber Fremdware- bzw. Fremdlager-Bestandsbuchungen mit der
abgerechneten Menge.

---

## Abrechnung

Abrechnung
Im Angeschlossenen Abrechnungsmodul wird zu diesem
Projekt ein Auftrag erfasst

---

## Abrechnung mit Kunden (Nur wenn „diskontierbar" in Portefeuille auf JA gesetzt ist)

Abrechnung mit
Kunden
(Nur wenn „diskontierbar" in Portefeuille auf
JA
gesetzt ist)
Hauptmenü
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechselbearbeiten
Direktsprung
[
WEB
]
Hier entstehen dann je nach Wechselart und Einstellung
in den Wechselklassen folgende Buchungen
Besitzwechsel:
Kunde an
272,13
Diskontertrag 6,5%
162,50
Spesen 50
      DM
50,00
Provision
      0,25%
25,00
Umsatzsteuer 15%
35,63
oder
Schuldwechsel:
Diskontaufwand 6,5%
162,50
Spesen 50 DM
50,00
Provision 0,25%
25,00
Vorsteuer 15%
35,63
an
      Lieferant
272,13

---

## Abschlagpreis

Abschlagpreis
Der Abschlagpreis wird bei der Erzeugung des
Fremdkontrakts aus der ihn erzeugenden Position des Vorfakturierungs-Belegs mit
dessen Preis belegt.
Er dient hier lediglich zur Information.

---

## Allgemeine Erläuterung

Allgemeine Erläuterung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Diese Funktion bietet die
Möglichkeit den Artikel, das Abrechnungsschema oder den Kunden eines
Rohwarenbeleges zu ändern.
Diese Änderungen kann man mit der normalen
Korrektur nicht vornehmen.
Datensätze die korrigiert
werden sollen, müssen zunächst in der Auswahlliste markiert werden. Bei Anwahl
der Funktion ‚Schema-/Kundenänderung’ öffnet sich ein Fenster, welches die
markierten Datensätze in einem Grid anzeigt, wenn diese mit der Funktion
bearbeitet werden können.
In folgenden Fällen können die Rohwarenbelege nicht
mit dieser Funktion bearbeitet werden und werden nicht in die Maske
übernommen:
Der
Rohwarenbeleg ist kein Lieferschein (Vorgangsklasse 600 / 1600)
Der
Lieferschein ist gesperrt.
Es
wurde keine passende Vorgangsunterklasse zur Vorgangsklasse des Beleges
gefunden. Das kann z.B. der Fall sein,
wenn im
Einrichterparameter
eine
Vorgangsunterklasse eingetragen ist, die für die Vorgangsklasse nicht existiert
oder/und
zur Vorgangsklasse keine Unterklasse mit der Einstellung
RohwareVorerfassung ungleich ‚ohne’ vorhanden ist.
Im
Grid auf der Maske kann man die gewünschten Änderungen vornehmen.
Die
Korrektur für alle Belege auf der Maske startet man mit der Funktion
Start Korrektur F9
.
Die
zu korrigierenden Rohwarenbelege werden storniert und über die Erzeugung eines
neuen Lieferscheines, der in einen Rohwarenbeleg gewandelt wird, neu
erzeugt.
Tritt bei der Neuerzeugung ein Fehler auf, dann ist das Original
schon storniert und die Daten damit verloren.
Deshalb ist es wichtig sich die
Rohwarenbelege vorher ins Archiv zu drucken.
Die
Steuergruppe eines Rohwarenbeleges bleibt erhalten, wenn der Rohwarenparameter
[rwpa] ‚
Steuergruppenvorbelegung
‘ (aus der Parametergruppe Erfassung
Seite 6) auf ‚
aus Kundenstamm
’ steht.
Bei der Einstellung
‚fester
Wert
’ wird die Steuergruppe aus dem Rohwarenparameter
‚

[...]


---

## ANHANG Rohware

ANHANG Rohware
6.1.
Rohwarensteuerungsparameter
6.2.
Beispiele von Gutschriften
a. Anlieferungsschein
b. Abschlags-Gutschrift
c. Folgeabschlagsgutschrift
d. Finalgutschrift
6.3.
Schemaerfassungsbogen

---

## Arbeitsweisen des Programms

Arbeitsweisen des Programms
•
Wird ein Labordatensatz erfasst oder geändert und als gültiger Datensatz
des Belegtyps erstellt, so werden aus der Tabelle „Rohware_Qual_Nachtrag“
bestehende Daten dieses Belegtyps geladen, ergänzt, bzw. abgeändert und in diese
Tabelle zurückgeschrieben. Von dort werden die Daten zur Erstellung der
Belegsabrechnungen verwendet.
•
Wird ein Beleg gelöscht, so werden aus der Tabelle
„Rohware_Qual_Nachtrag“ bestehende Daten dieses Belegtyps geladen. Die Werte des
bestehenden Datensatzes werden entfernt und verbliebene Daten in die Tabelle
zurückgeschrieben.
•
Die Änderungen in der Tabelle „Rohware_Qual_Nachtrag“ erfolgen ohne
Sicherungssperren. Ist der betreffende Satz zum Zeitpunkt der Änderung bereits
mit dem Einspielkennzeichen (abgerechnet) versehen, so wird der Anwender bei
Eingabe der Änderung gewarnt. Beim Speichern erfolgt ein Eintrag ins
Fehlerprotokoll als Warnung.

---

## Aufräumen

Aufräumen
Erledigte Belege werden endgültig aus der Liste
gelöscht. Bei Gesamtauswahl werden auch die zugehörigen verarbeiteten
Rohwaren-Sätze gelöscht.

---

## Ausschlusskriterien für Kundennummernänderung

Ausschlusskriterien für
Kundennummernänderung
Unter folgenden Umständen sind Änderungen der
Kundennummer
nicht
möglich
Kontraktbeteiligungen
Kriterium
Verfahrensweise
Position hat erledigten
      Kontrakt
Beleg enthält Stückliste oder
      Folgeartikel
Beleg wurde aus Teilumwandlung
      erstellt
Warenposition(en) wurde(n)
      weiterdisponiert
Je
      nach Behandlungsschema
Beleg stornieren und neu erfassen
      oder Behandlungsschema anpassen
Partiebeteiligung
Kriterium
Verfahrensweise
Position hat kundenspezifische
      Partie und Partiezwang. Es ist keine Partie für den Zielkunden
      vorhanden
Position stornieren
Je
      nach Behandlungsschema
Beleg stornieren und neu erfassen
      oder Behandlungsschema anpassen

---

## Auswahllisten zur Rohwarenbearbeitung

Auswahllisten zur
Rohwarenbearbeitung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Eine
Reihe von Auswahlvarianten ermöglicht die Übersicht der vorhandenen
Rohwarebelege nach unterschiedlichen Kriterien und
Bearbeitungsmöglichkeiten.
Aus
Performance-Gründen sind nicht alle Attribute in allen Varianten dargestellt.
Grundsätzlich ist es sinnvoll, mit der zugehörigen Bereichsauswahl die Auswahl
der darzustellenden Belege einzuschränken. So weist die Variante
‚
Rohware-Belege mit Gesamtwerten
‘ zum Beispiel Attribute auf, die ‚on the
Fly‘ ermittelt werden:
•
GesamtNetto
: Nettosumme des Beleges inklusive der Werte
vorhergehender Abschlagbelege
•
GesamtSteuer
: Steuersumme des Beleges inklusive der Werte
vorhergehender Abschlagbelege
•
GesamtBrutto
: Bruttowert des Beleges inklusive der Werte
vorhergehender Abschlagbelege
•
Bruttomenge
: Liefermenge der Hauptwarenposition des Beleges
•
Nettomenge
: Errechnete Ergebnismenge der Hauptwarenposition des
Beleges inklusive der Werte vorhergehender Abschlagbelege
•
Wert gesamt
: Berechneter Wert aus
GesamtNetto /
Nettomenge
•
TeilNetto
: Nettosumme des Beleges abzüglich der Werte
vorhergehender Abschlagbelege
•
TeilSteuer
: Steuersumme des Beleges abzüglich der Werte
vorhergehender Abschlagbelege
•
TeilBrutto
: Bruttosumme des Beleges abzüglich der Werte
vorhergehender Abschlagbelege
•
TeilNettomenge
: Errechnete Ergebnismenge der Hauptwarenposition
des Beleges abzüglich der Werte vorhergehender Abschlagbelege
•
Teilwertgesamt
: Berechneter Wert aus
TeilNetto /
Nettomenge
•
Teilwert:
: Berechneter Wert aus
TeilNetto /
TeilNettomenge
Mit
Ausnahme der Mengen stehen diese Werte nur für Lieferungen und abgerechnete
Belege zu Verfügung.

---

## Auswahlvariante ‚Vorfakt. Kontrakte’

Auswahlvariante ‚Vorfakt.
Kontrakte’

---

## Belegart

Belegart
Verschiene Filter zur Selektion nach Aeins
Vorgangsbereichen , insbesondere der Unterscheidung nach Rohware / nicht
Rohware, sind hier möglich.

---

## Best Practice

Best Practice
Hauptmenü
Kontraktverwaltung
Kontraktengagement
Die Anwendung zeigt in der ersten Ansicht die
Übersicht der zuletzt gewählten und berechneten Position.
Vorbereitende Maßnahmen zu korrekten Darstellung sind
hier
beschrieben.
Die Darstellung wird per Standard auf Basis der
Warengruppen jede Nacht aggregiert und zur Verfügung gestellt. Da die
Datenzusammenstellung um 00:01 durchgeführt wird, bezieht sich der Stichtag
immer auf die berechnete Position vom Vortag.
Als Darstellung können folgende System genutzt
werden.
-
Auswahlliste
-
Reportsystem
In der Auswahlliste werden die Mengen, wie auch die
Bewertungen dieser Mengen parallel angezeigt, im Report muss die Darstellung
ausgewählt werden, eine gemeinsame Darstellung der Mengen und Werte wird nicht
unterstützt.
In der Auswahlliste kann zusätzlich noch entschieden
werden, ob alle nicht im Einsatz befindlichen Kontrakttypen ausgeblendet werden
sollen und ob die Darstellung mit den Totalzeilen oder ohne (bei Nutzung eines
Excel Interfaces sinnvoll) angezeigt werden sollen.
Das Auswahlkriterium Warengruppe erlaubt es hier auch
eine Eingrenzung auf die Warengruppen, im Report wird pro Warengruppe eine
einzelne Seite genutzt.
Der Aufbau wird durch ein fest vorgegebenes Korsett
bestimmt, hierbei legt das Systemformat KTRPOSITION fest, welche Zeilen
berechnet werden sollen. Bisher werden unterstützt:
-
Inventory, alle im Bestand liegende Ware dieser Warengruppe. Hierbei wird in
dieser Version noch keine Bewertung vorgenommen:
o
Inventory Cash (Merkmal
A01):
alle im Lager zu dieser Warengruppe vorhandenen Bestände minus der
Bestände der unten aufgeführten Inventory Bereiche.
o
Inventory Basis (Merkmal
A02):
alle im Lager eingelagerten Waren dieser Warengruppe (gekennzeichnet
als Rohware (Unterklasse=9999)) unter Berücksichtigung des Pricing Kennzeichens
im Kontrakt (alle Kontraktlieferungen deren Pricing-Kennzeichen=1 ist).
o
Inventory DP (Merkmal
A03):
alle im Lager eingelage
[...]


---

## Daten von denen bekannt ist, dass sie bisher verloren gehen

Daten von denen bekannt ist, dass
sie bisher verloren gehen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Zusatzangaben wie z.B.
Versandart
Startgebiet
Zielgebiet
Vertretergruppe
Verkaufsgebiet
…
Daten die übertragen
werden
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung: EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Liefernummer
Vorgangsklasse
Liefermenge
und ME_Nummer
V_Datum
Qualitäten
Steuergruppe (siehe dazu den
entsprechenden Text in
Allgemeine
Erläuterung
)
Kontrakt
Partie
Daten des Registers
Ergänzungen
Inhalte von in der Rohwarengruppe bzw. des
Abrechnungsschemas definierten Ergänzungswerten und Ergänzungstexten werden per
Bezeichnung des zugehörigen Maskenfeldes identifiziert und bei Übereinstimmung
übertragen. Wird bei Wechsel von Rohwarengruppe oder Abrechnungsschema zu einem
vorhandenen Ergänzungswert bzw. Ergänzungstext keine Ergänzungsfelddefinition
gleichen Typs mit identischer Bezeichnung gefunden, so geht der ursprüngliche
Wert bzw. Text verloren.

---

## Definition von Ergänzungs-Werten und -Texten

Definition von
Ergänzungs-Werten und -Texten
Ergänzungsfelder für die
Rohware-Bearbeitung stehen dann zur Verfügung, wenn sie in der jeweils zugrunde
liegenden Rohwarengruppe oder im Abrechnungsschema definiert sind.
Dieses geschieht im Modul
‚Rohwarengruppendefinition’ (RWG) und dessen Untermodul ‚Schemadefinitionen’
jeweils durch Aufruf der Funktion ‚Ergänzungsfelder’ aus den ‚Optionen’.

---

## Diskontabrechnung Bank (nur bei Besitzwechsel)

Diskontabrechnung Bank (nur bei Besitzwechsel)
Hauptmenü
Finanzbuchhaltung
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechsel bearbeiten
Direktsprung
[
WEB
]
Ist ein Wechsel an die Bank weitergereicht worden, so
wird man von der Bank mit Diskont belastet. Diese Buchung lässt sich in der
Anwendung
Wechsel bearbeiten
durchführen. Den Wechsel markieren
und
F5
für
Ändern
. Der Wechsel wird angezeigt. Mit
F6
Diskont Bank
kann die Diskontabrechnung erstellt werden.
Buchungen:
Hierbei wird das Wechselobligokonto herangezogen. Ist
dies nicht eingetragen, so wird das Wechselkonto aus dem Hausbankenstamm
herangezogen.
Und fehlt dieses auch, dann wird das Konto aus dem
Wechsel selbst herangezogen!
Die Diskontabrechnung mit der Bank läuft dann
analog:
Nnnn Diskontertrag 5%
125,00
Nnnn Spesen 30 DM
30,00
Nnnn Provision 0,25%
25,00
Nnnn Vorsteuer 15%
27,00
an 1200
      Bank
207,00

---

## Einrichtungen im Abrechnungsschema

Einrichtungen im
Abrechnungsschema
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Abrechnungsschema
Direktsprung
[RWG]
In
einem Abrechnungsschema können zusätzlich zum Lieferartikel noch weitere
mengenrelevante Warenpositionen vorhanden sein. Je nach Anwendung wird man sich
entscheiden müssen, ob diese Menge auch wie Einlagerung / Vereinnahmung oder wie
normal zu buchende Positionen behandelt werden sollen. Hierfür wurden für die
Sekundärartikelpositionen  Kennzeichen geschaffen. Man stellt hier ein ob
deren Buchungsart wie die der Hauptposition zu behandeln ist.
In
Qualitätsdefinitionen kann in den Feldern ‚Berechnung erfolgt‘ und ‚Ausdruck
erfolgt‘ auch für Qualitäten, die sich nicht auf Einlagerungspositionen
beziehen, einstellen, ob die Qualität in Abhängigkeit von Einlagerungs- und
Vereinnahmungskennzeichen abzurechnen bzw. zu drucken ist oder nicht, getrennt
nach linksseitiger (Analysewert kleiner Basiswert) und rechtsseitiger
(Analysewert größer Basiswert) Abrechnungsdefinition. Die Einstellmöglichkeiten
sind hier:
•
Immer
•
Nicht bei Einlagerung
•
Nicht bei Vereinnahmung
•
Nicht bei Einlagerung/Vereinnahmung
•
Nur bei Einlagerung
•
Nur bei Vereinnahmung
•
Nur bei Einlagerung/Vereinnahmung
In
Kosten-/Vergütungs-Definitionen wird auf der Maske im Bereich ‚Berechnen ab:‘
zunächst die Belegstufe und danach der Berechnungsstatus in Abhängigkeit des
Einlagerungs-/Vereinnahmungskennzeichens des Beleges mit entsprechenden
Einstellmöglichkeiten festgelegt.

---

## Einzelbelege bearbeiten

Einzelbelege bearbeiten
Mit der Funktion ‚Einzelbelege bearbeiten’ wird eine
Sub-Auswahlliste mit den zugehörigen Rohware-Belegen mit Funktionen für
Korrektur, Druck, Finalisierung, Abrechnung etc. aufgerufen.

---

## Engagement

Engagement
Das Engagement kann über die Auswahlliste KTREN
angesprochen werden.
Berechnung der Werte
Die folgenden Werte werden je nach den Kontraktdaten
mit in die Berechnung einbezogen.
Mit Kontraktpreis
Ohne
Kontraktpreis
Ohne allgemeinen Wert
Mit allgemeinen Wert
•
Kontraktpreis
•
Allgemeiner Wert
•
Fracht
•
Handling
•
Währungsfaktor
•
Uplift
•
Reportzuschlag
Ohne Hedgeartikel
Mit Hedgeartikel
•
Matifpreis (Marktpreis)
•
Hedgepreis
•
Matif (Tradebasis)
•
Kurs
•
Uplift
•
Fracht
•
Handling

---

## Engagement nach Artikelnummer

Engagement nach Artikelnummer
Das Kontraktengagement nach Artikelnummern ist allein
schon von der Wortwahl konträr zu diskutieren, Einzelartikel haben wenig mit
Engagement zu tun. Werden verschiedene Weizensorten kontraktiert, dann bezieht
sich das Engagement auf eine einzelne Weizensorte, was aber keine Information
über eine long/short Position innerhalb des Artikel spiegelt.

---

## Ergänzungsfelder für Rohware-Belege

Ergänzungsfelder für
Rohware-Belege
Allgemeines
Zusätzlich zu den in der
Rohware-Bearbeitung erfassbaren Standardwerten gibt es die Möglichkeit, bis zu
12 weitere frei definierbare Werte in einem Rohwarebeleg zu erfassen.
Dabei handelt es sich um:
•
bis zu 3 für eine Rohwarengruppe definierte Textfelder
•
bis zu 3 für ein Abrechnungsschema definierte Textfelder
•
bis zu 3 für eine Rohwarengruppe definierte ganzzahlige Felder, ggf. mit
ITEM-Box-Unterstützung und/oder Validierung per SQL-Text
•
bis zu 3 für ein Abrechnungsschema definierte ganzzahlige Felder, ggf.
mit ITEM-Box-Unterstützung und/oder Validierung per SQL-Text
Werte für derartig definierte
Felder können
•
per Rohware-Bearbeitungsmaske auf jeder Stufe (Lieferung, Abschlag,
Folgeabschlag, Finale) erfasst und korrigiert werden
•
Aus Übergabe-Dateien ( Waagenschnittstelle) versorgt werden
•
Auf Rohware-Formularen gedruckt werden

---

## Ergänzungs-Texte

Ergänzungs-Texte
Der
zweite Block enthält die rohwarengruppenweit definierten Ergänzungsfelder, die
einen beliebigen Text beinhalten können.
Die
( nicht änderbare ) Nummer der 1. Spalte bestimmt das Datenfeld
(V_RohwareZFeldC1, V_RohwareZFeldC2 bzw. V_RohwareZFeldC3) der Relation
V_Rohware, in der die korresponierenden Werte der Rohwaren-Belege gespeichert
werden.
Die
Angaben in den Spalten
‚Pos’,  ‚Bezeichnung’
und
‚Verwend.’
Haben hier die gleiche Bedeutung, wie bei den Ergänzungs-Werten (s.o.).
Die
Angabe
‚Länge’
bestimmt die Länge des korrespondierenden Eingabefeldes
auf der Rohwaren-Bearbeitungsmaske. Möglich sind Textlängen von bis zu 255
Zeichen.
Die
Angabe von Länge ‚0’ wird wie Position ‚0’ behandelt: Feld ist nicht
definiert.

---

## Ergänzungs-Werte und –Texte in der Rohware-Bearbeitung

Ergänzungs-Werte und
–Texte in der Rohware-Bearbeitung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Ist
für das Abrechnungsschema des aktuell erfassten oder korrigierten Beleges
mindestens ein rohwarengruppen- oder schemaspezifisches Ergänzungsfeld definiert
(s.o.), so erhält die Bearbeitungsmaske eine weitere Tab-Card mit der
Bezeichnung ‚Ergänzungen’, die die Bearbeitung der korrespondierenden Felder
ermöglicht.
Beim
Umwandeln von Rohware-Belegen ( Abschlag -, Folgeabschlag-, Finale vorbereiten,
Lieferung-Stornobeleg, Abrechnungs-Stornobeleg ) werden Ergänzungsfelder
automatisch übernommen.

---

## Ergänzungs-Werte

Ergänzungs-Werte
Der
erste Block enthält die rohwarengruppenweit definierten Ergänzungsfelder, die
eine ganze Zahl beinhalten können.
Die
( nicht änderbare ) Nummer der 1. Spalte bestimmt das Datenfeld
(V_RohwareZFeldI1, V_RohwareZFeldI2 bzw. V_RohwareZFeldI3) der Relation
V_Rohware, in der die korresponierenden Werte der Rohwaren-Belege gespeichert
werden.
Die
Werte der Spalte
‚Pos’
für Position bestimmt die Erfassungsposition
des Feldes der Rohwarebearbeitungs-Teilmaske für die Ergänzungswerte wie auch
der Korrekturmaske  für Rohware-Waage-Belege. Es handelt sich hierbei um
eine relative Positionsangabe, die Positionsangaben müssen also nicht lückenlos
sein. Die Angabe ‚0’ für die Position bewirkt ein Unterdrücken des Feldes, es
ist dann nicht definiert. Für die Berechnung der Abfrageposition eines
Ergänzungsfeldes werden die ‚Pos’-Angaben aller rohwarengruppen- und
schemaspezifischen Ergänzungsfelddefinitionen in aufsteigender Reihenfolge
sortiert und die zugehörige Eingabefelder in dieser Reihenfolge erzeugt.
Die
Angabe in der Spalte
‚Bezeichnung’
ist auf der Bearbeitungsmaske vor dem
Eingabefeld wiederzufinden, hierdurch identifiziert der Anwender also ein
Ergänzungsfeld.
In
der Spalte
‚Verwend.’
wird festgelegt, ob die Felddefinition für den
Bereich ‚Einkauf’, ‚Verkauf’ oder für beide Bereiche gelten soll.
Mit
den Spalten
‚Min.Wert’
für Mindestwert und
‚Max.Wert’
für
Maximalwert werden korrespondierende Eingaben verprobt und ggf.
zurückgewiesen.
In
der optionalen Spalte
‚Item-Box’
kann eine existierende Item-Box für die
F3-gestütze Erfassung hinterlegt werden. Es ist jedoch darauf zu achten, dass
der RETURN-Wert einer derartigen Item-Box eine ganze Zahl beinhaltet. Es wird
jedoch kein Test durchgeführt, ob eine eingegebene Zahl auch per Item-Box
auswählbar ist (kein Item-Check). Dadurch kann hier auch eine Item-Box als
Vorschlagsliste aufgefasst werden, deren Werte aber nicht bindend sind.
Eine
optionale Eingabe in der Spalte
‚Va
[...]


---

## Ergänzungs-Werte und –Texte in Rohware-Waage-Daten

Ergänzungs-Werte und
–Texte in Rohware-Waage-Daten
Direktsprung
[SCPA]
Die
Hauptrelation der Rohware-Waagen_Schnittstelle enthält je 6 Felder für
Ergänzungs-Werte (Integer-Zahlen) und Egänzungstexte (ErgaenzungsWert1,
ErgaenzungsWert2, ErgaenzungsWert3, ErgaenzungsWert4, ErgaenzungsWert5,
ErgaenzungsWert6, ErgaenzungsText1, ErgaenzungsText1, ErgaenzungsText2,
ErgaenzungsText3, ErgaenzungsText4, ErgaenzungsText5, ErgaenzungsText6), die bei
der Erzeugung von Rohwarebelegen aus der Waagenschnittstelle  den Angaben
der Rohwarengruppen- und Abrechnungsschema-Definition entsprechend übernommen
werden können.
Zur
Versorgung der Schnittstellendatensätze aus einer Übernahmedatei mittels
Daten-Import-Script gibt es dafür zusätzliche Script-Parameter:
Dabei bestimmt der
Parameterwert1 jeweils die Position und der Parameterwert2 die Länge des
jeweiligen Wertes im Übernahmesatz an.
Die
folgende Tabelle enthält die für die Ergänzungsfelder zuständigen
Script-Parameter :
Script-Parameter
Bedeutung
ERGW1_SA1
Rohware-Ergänzungs-Wert_1 in Satzart
  1
ERGW2_SA1
Rohware-Ergänzungs-Wert_2 in Satzart
  1
ERGW3_SA1
Rohware-Ergänzungs-Wert_3 in Satzart
  1
ERGW4_SA1
Rohware-Ergänzungs-Wert_4 in Satzart
  1
ERGW5_SA1
Rohware-Ergänzungs-Wert_5 in Satzart
  1
ERGW6_SA1
Rohware-Ergänzungs-Wert_6 in Satzart
  1
ERGW1_SA2
Rohware-Ergänzungs-Wert_1 in Satzart
  2
ERGW2_SA2
Rohware-Ergänzungs-Wert_2 in Satzart
  2
ERGW3_SA2
Rohware-Ergänzungs-Wert_3 in Satzart
  2
ERGW4_SA2
Rohware-Ergänzungs-Wert_4 in Satzart
  2
ERGW5_SA2
Rohware-Ergänzungs-Wert_5 in Satzart
  2
ERGW6_SA2
Rohware-Ergänzungs-Wert_6 in Satzart
  2
ERGW1_SA3
Rohware-Ergänzungs-Wert_1 in Satzart
  3
ERGW2_SA3
Rohware-Ergänzungs-Wert_2 in Satzart
  3
ERGW3_SA3
Rohware-Ergänzungs-Wert_3 in Satzart
  3
ERGW4_SA3
Rohware-Ergänzungs-Wert_4 in Satzart
  3
ERGW5_SA3
Rohware-Ergänzungs-Wert_5 in Satzart
  3
ERGW6_SA3
Rohware-Ergänzungs-Wert_6 in Satzart
  3
ERGW1_SA4
Rohware-Ergänzungs-Wert_1 in Satzart
  4
[...]


---

## Feldbeschreibungen

Feldbeschreibungen
Felder
Partie-Nummer
Laufende Nummer der Partie, in die
      der Kontrakt aufgeteilt ist.
Partiebezeichnung
Nähere Bezeichnung der
      Partie
Partiegröße
Größe der Partie
Parität
Parität dieser Partie
Dispositionskennzeichen
Identifikation des
      Dispositionsmerkmals, das die Gegenüberstellung („Auszifferung“) von Ein-
      und Verkaufskontrakten oder deren Teilpartien ermöglicht.
Spediteur
Wenn
      per Spediteur geliefert wird, muss er hier bekannt gegeben werden, um
      entsprechende Auswertungen zu bekommen.
Vorgesehener Andientag
Vorgesehener
      Freistelltag
Frühester Liefertag
Spätester Liefertag
Angedient (Ja/Nein)
Freigestellt (Ja/Nein)
Abgeschlossen (Ja/Nein)
Partiezuordnung
Partiezuordnung einer Partie aus dem
      Partiestamm (Beispiel Seeschiff)
Kundenzuordnung
Kundenzuordnung, z.B. als
      Abrechnungskunde im Seeschiff-zuordnungsverfahren

---

## Fibu-Übertrag Rohware

Fibu-Übertrag Rohware
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]

---

## Finalabrechnungspreis

Finalabrechnungspreis
Der Finalabrechnungspreis kann in den Abrechnungen
herangezogen werden.

---

## Formulartypen

Formulartypen
Aus der Typangabe ergeben sich die Bereiche, die für
ein Formular einzurichten sind. Sie sind fest vorgegeben:
Nummer
Formulartyp
1
Standardvorgang
2
Kontoauszug
3
Interner Warenbeleg
4
Kundenetikett
5
Artikel Etikett
6
Überweisungsträger
7
Listen
101
Kontrakte
102
Kontrakt-Erledigungen
103
Kontrakt-Storno
104
Kontrakt-Erinnerungen
105
Kontrakt-Andienungen
106
Kontrakt-Freistellungen
107
Kontrakt-Andienung mit
      Freistellung
200
Fibu-Formular
201
BankScheckSparkasse
202
Mahnschreiben
203
Zinsabrechnung
204
Wechselabrechnung
210
Buchungsjournal Fibu
220
Kontoblatt Fibu
230
Kontenauswertung Fibu

---

## Fremdware-/Fremdlager mit Rohwareartikel

Fremdware-/Fremdlager mit Rohwareartikel
In Referenz-ERP können Fremdware- bzw.
Fremdlager-Positionen, die mittels der
Vorfakturierung
gebildet werden, nun auch im
Rohwarenbearbeitungsmodul abgewickelt werden. Dazu wird bei der Vorfakturierung
eines Rohwareartikels (Artikel mit eingetragener Rohwarengruppe) für den
anzulegenden Fremdkontrakt eine Reihe zusätzlicher Informationen hinterlegt (
Brutto-/Nettomengen-Kennzeichen, Final-/Weltmarkt-/Mindestpreis)
[
Zusatzinfo in
Fremdkontrakt
].
Ein derartiger Kontrakt kann bei der Erfassung von
Rohware-Belegen für die Lieferposition ausgewählt werden. Rohwarebelege mit
Bezug zu einem Fremdkontrakt können aber auch durch Rohware-Wandlung von
entsprechenden Normal-Lieferscheinen sowie durch die Belegerzeugung aus der
Rohware-Waagen-Schnittstelle erstellt werden.
Rohware-Belege mit Fremdkontrakt werden wie andere
Rohware-Belege bearbeitet: Sie können korrigiert, abgerechnet, gedruckt,
finalisiert, storniert, gebucht etc. werden.
AUSNAHME: Es können keine Abschlag- und
Folgeabschlagbelege erstellt werden. Die vorfakturierte Rechnung, die den
Fremdkontrakt erzeugt hat, stellt aus der Sicht der Rohwarenbearbeitung einen
anzurechnenden Abschlag dar.
Dieser Abschlagbetrag wird bei der Abrechnung der
zugehörigen Finalbelege auf den Betrag der jeweiligen Lieferposition
angerechnet, bis er ‚aufgebraucht’ ist.
Bei mehreren Abrechnungen zu einem Fremdkontrakt ist
daher i.d.R. der Buchwert der Anlieferpositionen der ersten Abrechnungen 0,00,
der auf den Beleg anzurechnende Abschlag jeweils der Abrechnungswert der
Anlieferzeile und der Beleg-Gesamtbetrag bei bestehenden Kostenpositionen
negativ.
Erst wenn der Abschlag (vorfakturierter Betrag) ‚aufgebraucht’ ist,
ändert sich dieses.
Es macht daher ggf. Sinn, eine Reihe von
Finalabrechnungen zu einem Fremdkontrakt per Sammelabrechnung zu behandeln.
Zur besseren Orientierung wurde in den für die
Rohwarenbearbeitung relevanten Auswahllisten eine zusätzliche Spalte
aufgenom
[...]


---

## Funktion Hilfe Hinweis RWG an/aus

Funktion Hilfe Hinweis RWG
an/aus
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Mit
dieser Funktion kann man das Öffnen der Hilfe mit dem
wichtigen Hinweis
beim Wechsel der
Rohwarengruppe für den aktuellen Benutzer unterbinden oder aktivieren.

---

## Funktion Hilfe Hinweis an/aus

Funktion Hilfe Hinweis
an/aus
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Mit
dieser Funktion kann man das Öffnen der Hilfe mit dem
wichtigen Hinweis
beim Öffnen der
Maske für den aktuellen Benutzer unterbinden oder aktivieren.

---

## Funktion Spalte füllen ab akt. Position

Funktion Spalte füllen ab
akt. Position
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Diese Funktion ermöglicht es
innerhalb der Spalte Artikel, Abrechnungsschema oder Kunde alle nachfolgenden
Zeilen mit dem Inhalt der Zeile zu füllen auf der man aktuell mit dem Cursor
steht.

---

## Ganze Übernahme löschen

Ganze Übernahme löschen
Ermöglicht es, alle importierten Datensätze (einer
Übernahme von dem Datenträger) einschließlich der Rohwaren-Sätze zu löschen.
Achtung: Hiervon sind auch etwa vorhandene
Rohwaren-Datensätze betroffen, die nur unter Direktsprung [RWWE] oder [RWWV]
sichtbar sind. Ferner können damit auch bereits zu Vorgängen umgewandelte
Übergabesätze entfernt werden.
*** Belegerz. Rücksetzen
Alle Belege, die korrekt oder auch nicht durch die
Belegerzeugung gegangen sind, können zurückgesetzt werden. (Die Brachialmethode,
nur für ENTWICKLER!) Das hat jedoch keinen Einfluss auf bereits erstellte
Belege!

---

## Globale Waagenparameter

Globale
Waagenparameter
Hauptmenü
Rohwarenabrechnung
Globale Waagenparameter
Für
die globalen Rohwaren-Waagen-Parameter Lagernummer, Lieferdatum, Versandart usw.
können hier Werte mit ihren Gültigkeiten hinterlegt werden.
Werte mit Datum 01.01.1901
werden von Branchen-ERP ausgeliefert und dürfen nicht geändert werden.
Zum
Feld Wert gehören für die F3-Auswahl (je nach Parameter ID) unterschiedliche
Formate. Diese findet man bei den Formaten [forma] unter dem Namen RWWAAGPARX
(wobei das x für 1-10 steht).

---

## Hinweis zum tabellarischem Erfassen

Hinweis zum tabellarischem Erfassen
ACHTUNG: Diese Programmfunktion unterstützt bisher nur
die Vorgangsbereiche ARTIKEL. Es werden in diesem Umfeld KEINE Gruppenrabatte,
Gruppen zu/Abschläge, KEINE individuell vergebenen Rabatte / Zu – Abschläge,
keine manuell vergebenen Kontrakte, keine Partien, KEINE Textzeilen, nur bis zu
zweistufigem Gebinde und auch nur eine Gebindezeile, und alle, nicht dem Artikel
automatisch zugeordneten Sonderfunktionen verarbeitet. Um all diese Funktionen
doch nutzen zu können, muss der Beleg mit der Korrekturtaste bearbeitet und
ergänzt werden. Bei Umwandlungen werden die oben erwähnten Bereich NICHT mit
umgewandelt!

---

## Individuelle Zinsgutschrift

Individuelle Zinsgutschrift
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zinswesen
Zinsabrechnung bearbeiten
Variante
Individuelle
Zinsgutschrift
Direktsprung
[ZIB]
In der Praxis werden nach Versand und Buchung der
Zinsabrechnung häufig mit den betroffenen Kunden Vereinbarungen getroffen, die
wie folgt lauten:
•
75% der Zinsen werden berechnet, 25% werden erlassen.
•
Von den ursprünglichen errechneten Zinsen in Höhe von 724,13 € sind nur
500 € zu zahlen.
Referenz-ERP unterstützt diese individuellen Gutschriften.
Dafür existiert in der Anwendung „
Zinsabrechnung bearbeiten
“ die Variante
„
individuelle Zinsgutschrift
“. Hier werden alle gebuchten Zinsen
aufgelistet, von denen jeweils eine ausgewählt werden kann. Wenn man dann die
Funktion auslöst, erscheint folgender Bildschirm.
Zinsliste, Kontonummer und Belegdatum werden aus der
Zinsabrechnung vorbelegt. Das Wertstellungsdatum wird, wie beim Buchen der
Zinsabrechnung, mit dem Belegdatum vorbelegt und kann geändert werden. Jahr und
Periode werden über das Belegdatum bestimmt.
Je nachdem, ob es sich bei den gebuchten Zinsen um
Soll- und/oder Habenzinsen handelt erscheint eine bzw. zwei Zeilen, in denen man
die Abweichung angeben kann.
Das blaue Feld rechts vom Text „Habenzinsen“ enthält
den tatsächlich gebuchten Betrag. Daneben kann man entweder den prozentuellen
Nachlass oder den geminderten Betrag sowie den Text der Buchung eingeben. Im
Feld Gutschrift erscheint dann die tatsächliche Gutschrift. Wenn man dann
Gutschrift erstelle
n
F9
auswählt, werden die hier eingegebenen
Daten in der Tabelle Zinsabrechnung hinterlegt. In dem Beispiel wird dann eine
Gutschrift über 55,64 € erstellt. Dieser Beleg kann dann in der
Belegerfassung/Primanota ggf. noch geändert werden. Bei einer Gutschrift auf
Sollzinsen wird ein Beleg vom Typen „AG“ Ausgangsgutschrift erstellt, bei
Habenzinsen ist der Typ „AR“ Ausgangsrechnung. Eine eventuell berechnete
Zinsabschlagssteuer wird entsprechend berichtigt.
Individuelle Zinsgutschriften k
[...]


---

## Itembox-Unterstützung bei der Erfassung von Analysewerten

Itembox-Unterstützung bei der Erfassung
von Analysewerten
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Abrechnungsschema
Merkmal-Definition
Direktsprung
[RWG]
Hauptmenü
Administration
Werkzeuge
SQL Textmanager
Direktsprung
[SQLM]
Für
die Erfassung und Korrektur von Rohwarebelegen können zur Unterstützung für
manuell zu erfassende Analysewerte in den zugehörigen Qualitätsdefinitionen der
Abrechnungsschemata auch (private) Itembox-Zuordnungen eingetragen werden.
Bei
der Ausführung des SQL-Statements der Itembox kann über eine Reihe festgelegter
Parameter auf die zum Zeitpunkt der Ausführung aktuellen zugehörigen Werte
zurückgegriffen werden.
Die
Namen und Inhalte der Parameter sind nachfolgend erklärt:
PAR_BELEGMODUS
Dieser
Parameter gibt an, in welchem Bearbeitungsmodus sich der Rohwarebeleg, zu dem
die den Itembox-Aufruf auslösende Qualitätsposition gehört, sich befindet. Für
diesen Parameter werden folgende Werte ermittelt:
1 – Erfassung des
Beleges
2 – Korrektur des Beleges
PAR_EINLAGERUNG
Dieser
Parameter gibt liefert den Wert des Einlagerungskennzeichens der
Anliefer-Warenposition (Referenznummer 1) des Rohwarebelegs, zu dem die den
Itembox-Aufruf auslösende Position gehört.
Für
diesen Parameter werden folgende Werte ermittelt:
0 –
keine Einlagerung
1 – Einlagerung
PAR_VEREINNAHMUNG
Dieser
Parameter gibt liefert den Wert des Vereinnahmungskennzeichens aus Einlagerung
der Anliefer-Warenposition (Referenznummer 1) des Rohwarebelegs, zu dem die den
Itembox-Aufruf auslösende Position gehört.
Für diesen
Parameter werden folgende Werte ermittelt:
0 –
keine Vereinnahmung
1 – Vereinnahmung
PAR_ANALYSEWERT
Dieser Parameter liefert den
aktuellen Analysewert der die den Itembox-Aufruf auslösenden
Qualitätsposition.
PAR_KORRANALYSEWERT
Dieser Parameter liefert den aktuellen
„korrigierten“ Analysewert der die den Itembox-Aufruf auslösenden
Qualitätsposition.
PAR_BASISUNTEN
Dieser Parameter
liefert den aktuellen unteren Basiswert der
[...]


---

## Jahresübergreifende Abrechnung

Jahresübergreifende Abrechnung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Sofern für das Geschäftsjahr,
in dem die Rohwarelieferung erfasst wurde, mindestens eine Abrechnung erstellt
wurde, kann eine Folgeabrechnung auch im darauf folgenden Geschäftsjahr erstellt
werden. Hierfür bietet Referenz-ERP zwei mögliche Vorgehensweisen. Zum einen kann auf
der Grundlage einer existierenden Abschlag- oder Folgeabschlagabrechnung die
Erstellung des Folgebelegs durch Eingabe von Datum und Buchungsperioden des
neuen Geschäftsjahres auf der vor der Ausführung der Umwandlungsfunktion
erscheinenden Vorbereitungs-Maske im neuen Jahr erfolgen. Dabei ist jedoch zu
beachten, dass auch bestands- und wertrelevante Buchungen dem neuen Jahr
zugeordnet werden.
Eine
andere Möglichkeit der Realisierung von jahresübergreifenden Abrechnungen ist
die Erstellung von Pro-Forma-Finalabrechnungen zum Jahresende, die dann mittels
der Erstellung einer Stornoabrechnung mit Kopie der ursprünglichen
Finalabrechnungen ins neue Jahr übertragen werden.
Zur Unterstützung bei der
Abwicklung jahresübergreifender Rohwareabrechnungen existieren im Vorgangstamm
im Vorgangstamm der Belege zwei Attribute. Das Feld ‚
V_KennzJWmitKopie
‘
mit Standardwert = 0 (
Nein
) wird in Quellbelegen auf 1 (
Ja
)
gesetzt, wenn diese per Stornobeleg mit Kopie in einem anderen Wirtschaftsjahr
umgewandelt werden. Es wird in den relevanten Standard-Auswahlvarianten
dargestellt. Das zweite Attribut ‚
V_KennzJWAbrPlan
‘, das ebenfalls in den
relevanten Standard-Auswahlvarianten ausgewiesen wird, ist ein pflegbares
Kennzeichen mit Standardeinstellung = 0, dass folgende Werte annehmen kann: 0
(
Nein
), 1 (
Ja
) und 2(
Ja, ohne Fibu-Übertrag
). Das Setzen
dieses Attributs kann bei der Erfassung/Korrektur von Rohwarenbelegen wie auch
per Rohware-Stapel-Korrektur und Rohware -Status-Stap
[...]


---

## Konstanten und Tabellen für die Einrichtung von Abrechnungsschemata (Sorten)

Konstanten und Tabellen
für die Einrichtung von Abrechnungsschemata (Sorten)
Hauptmenü
Rohwarenabrechnung

---

## Kontrakt

Kontrakt
-500004
keine Details verfügbar
-500005
keine Details verfügbar
-500006
keine Details verfügbar
-500007
keine Details verfügbar
-500008
keine Details verfügbar
-500010
keine Details verfügbar
-500011
keine Details verfügbar
-500012
keine Details verfügbar
-500013
keine Details verfügbar
-500014
keine Details verfügbar
-500015
keine Details verfügbar
-500016
keine Details verfügbar
-500017
keine Details verfügbar
-500018
keine Details verfügbar
-500019
keine Details verfügbar
-500020
keine Details verfügbar
-500021
keine Details verfügbar
-500022
keine Details verfügbar
-500023
keine Details verfügbar
-500024
keine Details verfügbar
-500025
keine Details verfügbar
-500026
keine Details verfügbar
-500027
keine Details verfügbar
-500028
keine Details verfügbar
-500029
keine Details verfügbar
-500030
keine Details verfügbar

---

## Kontraktartikel (AIS)

Kontraktartikel (AIS)
In der Kontraktartikelerfassungsmaske kann nicht
sichergestellt werden, dass beim Löschen eines Kontraktartikels auch die
dazugehörigen AIS-Daten mitgelöscht werden.
Aus diesem Grund muss die private Tabelle mit einem
„Fremdschlüssel“ versehen werden, der beim Löschen eines Kontraktartikels den
dazugehörigen AIS-Datensatz löscht.
Beispiel:
create table
admin.kontraktartikelAddon
( ktrid integer
,ktrartiPosit integer
,primary key (ktrid, ktrartiPosit)
,foreign Key (ktrid, ktrartiposit)
References
kontraktartikel ( ktrid, ktrartiposit )
ON DELETE CASCADE
CHECK ON COMMIT
)
Hier eine kleine Erläuterung zum Anlegen des
Fremdschlüssels.
Statement
Beschreibung
foreign Key (ktrid,
      ktrartiposit)
Hiermit wird angegeben aus welchen
      Spalten der Fremdschlüssel besteht.
References kontraktartikel ( ktrid,
      ktrartiposit )
Dieser Teil legt fest auf welche
      Tabelle der Fremdschlüssel zeigt und um welche Spalten es sich hierbei
      handelt. Die Reihenfolge der Spalten muss die gleich wie im „foreign key“
      Teil sein.
ON
      DELETE CASCADE CHECK ON COMMIT
“ON
      DELETE CASCADE” bedeutet, dass beim Löschen die Abhängigen Daten dieser
      Tabelle auch gelöscht werden.
Der
      “CHECK ON COMMIT” Teil sagt aus, dass die Überprüfung erst beim COMMIT
      erfolgen soll.

---

## Kontrakte löschen

Kontrakte löschen
Es dürfen keine Daten in KONTRBEWEGUNG vorhanden sein,
sonst wird nicht gelöscht!
Es werden die Daten in folgenden Tabellen
gelöscht:
KontraktAddon
KONTRAKTAKTSTAT
KONTRAKTANDIEN
KONTRAKTANDIPOSI
KONTRAKTARTIKEL
KONTRAKTBAUSTEIN (
where
isnull(ktrid,0) != 0
)
//
Datensätze für Kontraktvarianten mit Verknüpfungen zu Textbausteinen
(bemerkstamm) nicht mitlöschen
KontraktZuStrecke
KontraktTextBlob
KONTRAKTERINNER
KONTRAKTFREIST
KONTRAKTKORREKT
KontraktMaskeDaten
KONTRAKTMENGE
KontraktMengeIst
KontraktMengeRoh
KONTRAKTMENGEZR
KONTRAKTPARTIE
KONTRAKTPREIS
KontraktPreisRoh
KONTRAKTPREISZR
KONTRAKTSTAMM
KONTRAKTSUMMEN
KONTRAKTTEMPLATE
KONTRANDIBEWEG
KontrArtiRohKost
KontrArtiRohQual
KONTRARTIROHWARE
KONTRAUSWARTI
KONTRAUSWLISTE
KontrAuswPreis
KONTRBEWEGUNG
KONTRDISPOZUORD
KONTRERINNBEWEG
KONTRERINNPOSIT
KONTRFREIBEWEG
KONTRFREIPOSIT
KontrKlNumKreis
KONTRPARILAGER
KontrPariZuAb
KONTRPARTIEMENGE
KONTRUNTER
KontrUnterKlasse
KONTRVARIANTE
KONTRVARIBAUST
KONTRVARIPOSIT
KONTRVARITEXT
Kontraktratierlich_protokoll
Bemerkung unter der Bedingung: where (BemerkTyp = 31)
or (BemerkTyp = 32)

---

## Kontrakteinrichtungen löschen (inkl. 7)

Kontrakteinrichtungen löschen (inkl. 7)
KONTRUNTER
KontrUnterKlasse
KONTRVARIANTE
KONTRVARIBAUST
KONTRVARIPOSIT
KONTRVARITEXT
KONTRDISPOZUORD
KontrKlNumKreis
BemerkPosition unter der Bedingung where (BemerkId in
(select BemerkId from BemerkStamm where (BemerkTyp in (31, 32)))
BemerkPositionWERTE unter der Bedingung where
(BemerkId in (select BemerkId from BemerkStamm where (BemerkTyp in (31,
32)))
BemerkStamm unter der Bedingung where (BemerkTyp in
(31, 32))
Bemerkung unter der Bedingung where (BemerkTyp = 31)
or (BemerkTyp = 32)
31=Kontrakt-Bemerkung
32=Kontraktdispositions-Bemerkung
Beim Löschen der Kontrakteinrichtungen  werden
automatisch die
Kontrakte
mit gelöscht.

---

## Kontrakterledigung

Kontrakterledigung
Kontrakte, die in der Vorschlagsliste angezeigt
werden, können durch das Kennzeichen „Kontrakterledigung“ jederzeit aus der
Liste entfernt werden. Somit ist der Mitarbeiter jederzeit in der Lage die Liste
auf einem aktuellen Stand zu halten.
Kontrakte, die eine
Restmenge
aufweisen, jedoch
trotzdem
nicht gemahnt
werden sollen, lassen sich so auch aus der
Mahnvorschlagsliste entfernen, wenn der Gesamtzeitraum des Kontraktes abgelaufen
ist.

---

## Kontraktmahnung drucken

Kontraktmahnung drucken
Über die Funktion Kontraktmahnung drucken wird ein
Crystal Report aufgerufen, über den mit entsprechender Filterung (muss in der
Kontraktmahnung bearbeiten enthalten sein) die Mahnung physisch ausgedruckt
werden kann.

---

## Kontraktdetails

Kontraktdetails
Die Variante Kontraktmahnung Vorschlagsliste gruppiert
die Kontrakte so, dass pro Kontrakt nur eine Zeile summiert angezeigt wird. Zur
besseren Übersicht besteht die Möglichkeit, sich über die Funktion
„Kontraktdetails“ den Kontrakt detaillierter anzeigen zu lassen.
Der Mitarbeiter ist in der Lage jeden Mengenzeitraum
detailliert zu betrachten.

---

## Kontraktmahnung freigeben

Kontraktmahnung freigeben
Entscheidet sich ein Bediener dazu einen Kontrakt für
einen Mahnlauf freizugeben, so muss der Kontrakt markiert und über die Funktion
„Kontraktmahnung freigeben“ in die „Kontraktmahnung bearbeiten“ übergeben
werden. In der Variante Kontraktmahnung bearbeiten erscheinen nur Kontrakte, die
über die Funktion „Kontraktmahnung freigeben“ übergeben wurden.
Durch die Freigabe zum Mahnlauf wird noch
kein
Druck
erzeugt. Dieser muss in der entsprechenden Variante „Kontraktmahnung
bearbeiten“ separat noch einmal angestoßen werden.

---

## Kontraktmahnung zurücksetzen

Kontraktmahnung zurücksetzen
Entscheidet sich ein Bediener dazu, einen Kontrakt
wieder aus dem Mahnlauf zurückzusetzen, so wird der markierte Kontrakt wieder in
die Mahnvorschlagsliste zurückgesetzt.

---

## Kontrakt-Variante Exportieren

Kontrakt-Variante Exportieren
Wird in der Auswahlliste der Kontraktvarianten die
Funktion
Kontrakt-Varianten Exportieren
aufgerufen, erscheint die Maske zum Export der Variante als SQL-Text.
Es kann der Dateipfad angegeben werden.
Anschließend wird die ausgewählte Kontraktvariante als
Datei abgespeichert.

---

## Lieferung

Lieferung
Der Abbau von
Fremdware- oder Fremdlagerbeständen durch Abholung der Fremdware oder Lieferung
der Fremdlagerware erfolgt über die Lieferscheinerfassung [LIE] bzw. über die
Eingangslieferscheinerfassung [ELE], in der als Kontrakt bei Erfassung der Ware
der Fremdware- bzw. Fremdlagerkontrakte ausgewählt wird.
Bei Abholung
von Fremdware wird der Fremdbestand und der Istbestand um die abgeholte Menge
reduziert. Ebenso wird bei Lieferung von Fremdlagerware der Fremdlagerbestand um
die geliefert Menge reduziert und der Istbestand um diese Menge erhöht.
Bei Abholung
von Fremdware von einem anderen Lager oder bei Anlieferung von Fremdlagerware
auf einem anderen Lager, als das Lager auf dem der Vorverkauf bzw. der
Voreinkauf getätigt wurde, bietet Referenz-ERP die Möglichkeit mit dem
Steuerparameter
„
Lagerumb. Bei Lieferung Voreink.-Vorverk. (603)
“,
dass die Bestände durch ein automatische Lagerumbuchung korrigiert werden. Da
immer die Fremdware- bzw. Fremdlagerbestände auf dem Lager, auf dem der
Vorverkauf bzw. der Voreinkauf getätigt wurde, umgerechnet werden.

---

## Mindestpreis

Mindestpreis
Der Mindestpreis kann, falls benötigt, in
Rohware-Abrechnungen mittels einer speziellen Qualitätsdefinition zur
Preiskorrektur herangezogen werden.

---

## Änderung-/Eintragen von Ergänzungsfelder in der Rohwaren-Waagen-Schnittstelle

Änderung-/Eintragen von
Ergänzungsfelder in der Rohwaren-Waagen-Schnittstelle
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Waage-RWLieferungen
Ändern
Direktsprung
[RWWE]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Waage-RWLieferungen
Ändern
Direktsprung
[RWWV]
Im
Änderungsmodus der Waage-Datensätze können auch die Ergänzungsfelder bearbeitet
werden (Funktion ‚Ergänzungswerte’ der Optionbox). Ist im Waage-Datensatz
bereits eine Schemanummer vorhanden, so erfolgt die Bearbeitung der Felder
entsprechen der Definitionen der zugehörigen rohwarengruppen- und
schemaspezifischen Ergänzungsfelddefinitionen.
In
diesem Fall stehen dann auch die dort angegeben Item-Boxen, Min-/Maximumtest und
SQL-Text-Validierung für Integer-Werte sowie die Längenbegrenzung für Textfelder
zur Verfügung.
Ist
das Abrechnungsschema im Waagedatensatz hingegen nicht bekannt, so erfolgt die
Bearbeitung in der Reihenfolge der Werte im Waagedatensatz (ErgaenzungsWert1 –
6, ErgaenzungsText1 – 6 ).

---

## Neuer Fremdlagerkontrakt je Voreinkauf (580)

Neuer
Fremdlagerkontrakt je Voreinkauf (580)
Ja:     Bei jeder Erfassung einer Fremdlagerposition wird
ein neuer Fremdlagerkontrakt für diese Position angelegt.
Nein: (außer Rohwareartikel) Falls eine Fremdlagerposition mit einer bereits
erfassten Fremdlagerposition in Kunde, Artikel, Lager und Lagerplatz
übereinstimmt, so wird der Kontrakt zu dieser Position um die Menge der neuen
Position erhöht und für die neue Position wird kein eigener Kontrakt
angelegt.
Für Rohwareartikel wird immer ein neuer Fremdlagerkontrakt
angelegt.

---

## Neuer Fremdwarekontrakt je Vorverkauf (306)

Neuer
Fremdwarekontrakt je Vorverkauf (306)
Ja:     Bei jeder Erfassung einer Fremdwareposition wird ein
neuer Fremdwarekontrakt für diese Position angelegt.
Nein: (außer Rohwareartikel) Falls eine Fremdwareposition mit einer bereits
erfassten Fremdwareposition in Kunde, Artikel, Lager und Lagerplatz
übereinstimmt, so wird der Kontrakt zu dieser Position um die Menge der neuen
Position erhöht und für die neue Position wird kein eigener Kontrakt
angelegt.
Für Rohwareartikel wird immer ein neuer Fremdwarekontrakt
angelegt.

---

## Permanente Reorganisation

Permanente Reorganisation
Die aktuell veränderten
Artikel wurden ohne zusätzliche Einstellungen schon seit längerer
Z
eit
protokolliert. Für die Aktivierung der Reorganisation von Kontrakten und Partien
muss der SPA 905 angepasst werden:
Hinweis: Die Itembox zur
Auswahl des Typs der Reorganisation weist
eventuell
noch die Option
‚Artikelreorganisation‘ aus. Die Einstel
l
ung ist nicht
notwendig!
Ferner muss der SPA 628 ‚Datenbestandspflege im
Mandantenserver‘ auf 1 gestellt sein. Hierdurch wird ein im Mandantenserver
verankerter Prozess aktiviert, der die eigentliche Reorganisation der Objekte
durchführt. Dieser Prozess prüft immer nachfolgenden Bedingungen ab, bevor die
eigentliche Reorganisation durchgeführt wird:
Bin ich der einzige eingeloggte Benutzter im System?
Ist der Datenstrom leer?
Habe ich eine Erlaubnis vom Zeitschema?
Das Zeitschema wird mit dem Direktsprung DBP festgelegt:
Prinzipiell kann die automatisierte Abwicklung auch im
laufenden Betrieb eingeschaltet werden. Die oben erwähnten Bedingungen treffen
dann in der Regel nicht zu. Es macht aber Sinn, schon bekannte Zeiten andere
Systeme (z.B. Datensicherung) auszuschließen.
ACHTUNG: zusätzlich zu
ja/nein gibt es noch weiter Einstellung, kläre ich noch ab. Da geht es darum, ob
DBP auch laufen darf, obwohl noch Benutzter im System sind!
In dieser Anwendung befinden sich zudem folgende
nützliche Funktionen:
Datenbestandspflege starten:
Wenn alle oben erwähnten Bedingungen eingehalten sind kann
man die Reorganisation auch direkt starten. Achtung: es gibt dafür keine
Unterbrechung. Wenn man sich auf dem Mandanten dann parallele noch einmal
einloggt, wird die Reorganisation sofort unterbrochen.
Sitzungsprotokoll DBP Läufe:
Jeder Lauf wird protokolliert. Hiermit kann man den
Verlauf der Reorganisation nachvollziehen.
Noch einige technische Hinweise:
Die noch ausstehenden Artikelreorganisationen befinden sich
in der Relation ArchivArtikelAuftrag.
Die noch ausstehenden Kontrakt- und Parti
[...]


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

## Praxisbeispiel Seeschiff :

Praxisbeispiel Seeschiff :
Wird ein Silosystem als Umschlag realisiert, also Ware
angeliefert und auf der anderen Seite wieder ausgeliefert (LKW’s bringen Ware
die durch das Silosystem in ein Seeschiff verbracht werden), dann kann eine
Partie im Kontrakt die Klammer zum Seeschiff darstellen. In jedem
Anlieferkontrakt wird schon in der Anlegephase (oder später bei der Zuordnung
der Kontrakte zum Schiff) die Partie eingetragen. Durch diesen Eintrag wird dann
vollautomatisch im Waagensystem die Anlieferung auch in diese Partie gezogen.
Eine Auswertung (siehe auch Waage) liefert dann z.B. tagesbezogen oder als
Gesamtübersicht die in das Ziel verbrachte Ware (also im Beispiel das
Seeschiff).
Um bei der Partiezuordnung nicht noch zusätzlich die
Partielieferanten- kundenliste nutzen zu müssen, gibt es für den einfachen Fall
der Seeschiffabrechnung die Möglichkeit der Kundenzuordnung in der
Kontraktpartie, was bedeutet, dass der Kontrakt gegen den Kunden abgerechnet
werden kann, die Auslagerung aber dem Seeschiff zugeordnet werden kann.

---

## Prinzipieller Aufbau

Prinzipieller Aufbau
Der
Schwerpunkt des Programm-Moduls liegt auf der freien Eingabe von Konstanten,
Tabellen und Parametern. Daraus resultierend ist die Definition beliebiger
Abrechnungsmodalitäten möglich. Alle weiteren Programmteile wie
Lieferscheinerfassung, Abrechnungserstellung und Statistiken ergeben sich mehr
oder minder automatisch.
Die
von der Rohware erstellten Eingangsrechnungen(„Gutschriften“) und
Ausgangsrechnungen sind in der Regel immer nach demselben Schema aufgebaut:
Horizontal
in der Reihenfolge
•
Analysewert (z.B. 16,80 % )
•
Bezeichnung (z.B. Feuchtigkeit)
•
Zu- oder Abschlag als Menge oder Preis
•
Gesamtbetrag
In
vertikaler
Richtung (von oben nach unten) besteht eine Abrechnung aus den
2 Blöcken
•
Qualitätskriterien
•
Kostenkriterien

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

## Qualitäts- und Kostenmerkmalwerte per Datenbankprozedur bestimmen

Qualitäts- und Kostenmerkmalwerte per
Datenbankprozedur bestimmen
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Abrechnungsschema
Merkmal-Definition
Direktsprung
[RWG]
Hauptmenü
Administration
Werkzeuge
SQL Textmanager
Direktsprung
[SQLM]
Für
die Abrechnung von Qualitäts- und Kostenpositionen können nun auch
Datenbankprozeduren zur Versorgung oder Berechnung bestimmter Werte eingesetzt
werden.
Hinweis:
Es ist bei der
Verwendung von Datenbankprozeduren unbedingt auf die Performance bei der
Prozedurausführung zu achten, da diese während der Erfassung oder Korrektur
eines Rohware bei allen Eingaben durchgeführt wird, die ergebnisrelevant sein
könnten.
Bei
Qualitätsmerkmalen können sowohl die Werte für
•
Analysewert
•
korrigierter Analysewert
•
oberer Basiswert
•
unterer Basiswert
per
Datenbankprozedur ermittelt werden, wie auch die
•
Abrechnungsmethoden
bei
Unterschreitung des unteren Basiswertes und/oder bei Überschreitung des oberen
Basiswertes durch den korrigierten Analysewert als Datenbankprozedur zur
Ermittlung des Preis- oder Mengenzu- oder –abschlags angegeben werden.
Bei
Kosten-/Vergütungsmerkmalen können die Werte für
•
Kosten-/Vergütungssatz
•
Kosten-/Vergütungspauschale
per
Datenbankprozedur ermittelt werden.
Mit
der Einstellung ‚DB-Prozedur‘ für die Analysebestimmung und die Bestimmung des
korrigierten Analysewertes bzw. ‚Basiswertbestimmung per DB-Prozedur‘ im Feld
‚Basis in Beleg‘ für Basiswertfestlegungen auf der zugehörigen
Qualitätsdefinitionsmaske des
Rohwarengruppen-/
Abrechnungsschemadefinitionsmoduls kann im zugehörigen Textfeld der Name der
heranzuziehenden Datenbankprozedur angegeben werden. Es wird hier nur der
jeweilige Prozedurname, nicht aber die Parameter angegeben.
Zur
Bestimmung einer Datenbankprozedur als Abrechnungsmethode wird im Feld ‚Typ‘ auf
der gewünschten Seite (‚Abrechnung bei Analysewert unter Basis‘ bzw. ‚Abrechnung
bei Analysewert über Basis‘) je nach gewünschtem Ergebnistyp der Wert ‚
P
[...]


---

## Ratierliche Verteilung

Ratierliche Verteilung
Bei der ratierlichen Aufteilung von Kontrakten handelt
es sich um eine statistische Aufteilung der Kontraktmenge auf eine festgelegte
Anzahl von Monaten. Angezeigt werden die Werte in der
Kontraktauswahl
.
Die Verteilung erfolgt
nicht
für
„Verkaufskontrakte Fremdware“ und „Einkaufskontrakte Fremdlager“.
Aktivierung
Zum Aktivieren der ratierlichen Aufteilung muss der
Steuerparameter „701“
auf „Ja“
gesetzt werden. Über folgenden Aufruf wird der Event zur Aufteilung der Mengen
angelegt.
call
amic_evt_amic_kontraktratierlich(1)
Soll zusätzlich das tägliche Protokoll mitgeschrieben
werden, kann der Event über folgenden Aufruf angelegt werden.
call
amic_evt_amic_kontraktratierlich_protokoll(1)
Wir eine zusätzliche Berechnung der Kontraktposition
gewünscht, so ist diese im Event einzutragen:
EVT:
Die Zeile
call ktrposition ( today(), ‘0’,
‘999999999’, 1, 0, 1, 0, 0 )
steht hierbei für die Warengruppenspezifische
verarbeitung, wird
call ktrposition ( today(), ‘0’, ‘999999999’, 1, 0, 1, 0,
1 )
so wird die Kontraktposition bis auf den Artikel (ohne Lagerzuordnung)
runtegebrochen.
Einstellungen
Einige Einstellungen müssen in den Steuerparametern
hinterlegt werden.
•
Vorausmonate (
Steuerparameter
„698“
)
•
Mengeneinheit der Mengen (
Steuerparameter „815“
)
•
Enddatum der Berechnung (
Steuerparameter „798“
)
Funktionen
In der
Kontraktauswahl
gibt es zwei
Funktionen mit denen das Protokoll und die Verteilung erneuert werden
können.
Funktion
Beschreibung
Ratierliches Protokoll
      erneuern
Für
      die markierten Kontrakte wird das gesamte Protokoll vom Anfang des
      Kontrakts bis heute erneuert.
Ratierliche Verteilung
      erneuern
Hiermit kann die ratierliche
      Verteilung der markierten Kontrakte erneuert werden.

---

## Reaktion bei Fremdlagerüberbuchung (605)

Reaktion bei Fremdlagerüberbuchung (605)
In Ordnung:   Referenz-ERP reagiert nicht und der
Fremdlagerkontrakt wird überbucht.
Warnung:      Referenz-ERP überbucht den
Fremdlagerkontrakt, gibt aber eine Warnung aus.
Fehler:
Referenz-ERP gibt einen Fehler aus. Die Erfassung wird abgebrochen.

---

## Rekalkulation Zinsrechnung

Rekalkulation Zinsrechnung
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zinswesen
Zinsabrechnung bearbeiten
Variante
Rekalkulation
Zinsabrechnung
Direktsprung
[ZIB]
In der Praxis kommt es nicht selten für zinsmäßig
abgeschlossene Zeiträume zu Nachbuchungen und Valutenberichtigungen.
Solche Buchungen bringen das „Zinsgefüge“
durcheinander. Die Kontokorrentzinsen für so betroffene Kundenkonten und
Zeiträume müssen gegebenenfalls erneut gerechnet werden.
Im Normalfall sind hier folgende Einzelschritte
nötig:
•
Zinsbuchung stornieren.
•
Stornobelege verbuchen
•
Zinsen zurücksetzen
•
Zinsabrechnung erneut erstellen
Da bei all diesen Schritten Fehler auftreten können
bzw. es doch sehr aufwendig ist und als zu umständlich empfunden wird, wurde
eine (versteckte) Variante „
Rekalkulation Zinsabrechnung
“ erstellt. In
dieser Variante werden alle Zinsabrechnungen sortiert nach Kontonummer
(aufsteigend) und Zinslistennummer (absteigend) ausgegeben. In der F2 Auswahl
kann nach folgenden Kriterien eingegrenzt werden:
•
Abrechnungsjahr. Dies ist immer wirksam, also nicht mit Hakentechnik
abschaltbar.
•
Kontonummer : von.. bis
•
Zinsliste : von..bis
•
Zinsgruppe : von..bis
•
Bisdatum : von ... bis
•
Abweichung Soll : von ... bis
•
Abweichung Haben : von ... bis
•
Abweichung saldiert : von ...bis
In der Optionbox zu dieser Variante steht eine weitere
Funktion „Zinsen erneut erstellen“ zur Verfügung.  Innerhalb dieser
Funktion existiert ein Einrichterparameter („Ausgezifferte Zinsbelege
stornieren“). Er steuert, ob die Verarbeitung bei bereits ausgezifferten
Zinsbelegen für das Konto abgebrochen wird oder nicht. Siehe unten.
Beschreibung
Abrechnungsdatum
Dies
      ist der Tag, an dem die Zinsabrechnung erstellt wird. Es wird mit dem
      Tagesdatum vorbelegt. Dieses Datum wird später das Belegdatum der
      automatisch generierten Zinsbelege.
Periode Zinsstorno
Dieser Periode werden eventuell zu
      erstellende Stornobeleg zugeordnet.
Bemerkung
Diese Bemerkung wird in der
[...]


---

## Relation RohwareZusatzQualitaet_Waage

Relation RohwareZusatzQualitaet_Waage
Analysewert
numeric    15 4 .................... Y  N
Datum_VonWaage
date        4 0 .................... N
Y
LfdNummer_VonWaage
integer     4 0 .................... N  Y
Qualitaetnummer
integer     4 0 .................... N  Y
SatzId
integer     4 0 .................... Y  N
UebernahmeID
integer     4 0 .................... N  Y

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

## Rohware-Auswertung in Auswahlliste

Rohware-Auswertung in Auswahlliste
Neben der Funktion RWA mit Excel durchzuführen gibt es
die Möglichkeit diese auch in eine extra dafür vorgesehene Anwendung zu
transportieren und somit z.B. über die Variante Daten zu joinen und einen
Quickreport zu generieren.
Zu beachten ist das die Bezeichnungen in den
entsprechenden Definitionen nun nicht länger Titel einer Excel-Spalte darstellen
sondern technische Spaltennamen einer Datenbank-Relation. Somit gibt es die
Anforderung keine Sonderzeichen und keine Leerzeichen zu verwenden.
Die erzeugte Anwendung heißt
PAW_(Definition)_(Sorte) , wobei alle Zeichen außer
0-9A-Z_ gegen _ ersetzt werden

---

## Rohwarebelege ansehen

Rohwarebelege ansehen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Ansicht
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Ansicht
Direktsprung
[RWBV]
Mit
dieser Funktion können die Daten der ausgewählten Rohwarebelege zur Ansicht
gebracht werden. Im Gegensatz zur Korrektur können auch bereits
weiterverarbeitete Belege sowie Einzelbelege angezeigt werden, die Teil eines
Sammeldruckbelegs sind.
Zur
Orientierung befindet sich in der ersten Maskenzeile ein Informationsfeld, dass
im Korrektur- oder Ansicht-Modus Angaben über den Beleg-Status ausweist. Hier
wird neben der aktuellen Belegstufe (Lieferung, Abschlag, Folgeabschlag, Finale)
und zugehörigem Belegdatum gegebenenfalls auch die Sammeldrucknummer nebst
Sammeldruckdatum ausgewiesen, wenn der Beleg Teil eines Sammeldrucks ist. Bei
Stornobelegen wird das Wort ‚Storno‘ vorangestellt.
Mit einer im
Einrichterparameter ‚
Prozedurname für die freie Anzeige
‘ festlegbaren
privaten Datenbankfunktion kann diese Anzeige durch einen durch die
Datenbankfunktion zurückgelieferten Text ersetzt werden. Einer solchen privaten
Datenbankfunktion wird als Parameter die V_Id des Belegs übergeben. Die
Definition muss demnach etwa wie folgt vorgenommen werden:
Create function meineFunktion
(in in_v_id integer default 0)
returns char(256)
BEGIN
declare
dc_infotext char(256);
.
.
.
return
dc_infotext;
END

---

## Rohwarebelege erfassen

Rohwarebelege
erfassen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Lieferung erfassen
Direktsprung
[RWBV]
Die
Abfragefelder der Erfassungsmaske für Rohware-Lieferscheine wie auch die
Reihenfolge der Abfrage werden durch die generellen Rohwarenparameter [RWPA]
sowie durch das Abrechnungsschema bestimmt.
So
ist zum Beispiel dort festgelegt, ob zunächst der Artikel ausgewählt und damit
das zugehörige Default-Abrechnungsschema der zugeordneten Rohwarengruppe wird,
oder anderenfalls zunächst ein Abrechnungsschema angegeben und ein entsprechend
der zugehörigen Rohwarengruppe passender Artikel zum Lager vorgeschlagen wird.
Aus
dieser Kombination füllt sich der Warenerfassungsteil der Abrechnung
entsprechend der Angaben des gewählten Abrechnungsschemas.
Die
ersten beiden möglichen Erfassungsfelder dienen jedoch der Auswahl von Kontrakt
und Lagernummer. Dabei ist zu beachten, dass die Lagernummer zunächst aus den
Vorgangskonstanten vorbelegt wird. Sie kann jedoch bei Einstellung des
Rohwareparameters
Lager
mit dem Wert
‚
Erfassung
‘ geändert werden.
Ist
der Erfassungsbeginn per Kontraktauswahl durch den Rohwareparameter
Erfassungsstart mit
Kontraktnummer
aktiviert, so kann als erste Aktion der Erfassung ein
Rohwarekontrakt oder ein Voreinkaufs- bzw. Vorverkaufskontrakt angegeben werden.
Hieraus werden dann Artikel- und Kundendaten in den Beleg übernommen und der
Kontrakt bereits der Lieferwarenposition zugeordnet. Dabei wird bei
lagerspezifischen Kontrakten die Lagernummer entsprechend der Kontraktposition
übernommen. Andernfalls wird die vorgegebene Lagernummer beibehalten, sofern der
angesprochene Artikel auf dem Lager existiert.
Während des Erfassungsvorgangs
können auch die Kopfdaten wie Artikelnummer, Lagernummer, Kundennummer und
Kontrakt geändert werden. Dabei werden eventuell bereits gemachte Angaben im
Posi
[...]


---

## Rohwarebelege korrigieren

Rohwarebelege
korrigieren
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Korrektur
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Korrektur
Direktsprung
[RWBV]
Je nach Bearbeitungsstatus und
Einstellung der Rohwarenparameter [RWPA] können die Angaben der ausgewählten
Rohwarebelege hier abgeändert werden. Dabei ist zu beachten, dass ein bereits
entsprechend seiner Stufe abgerechneter Beleg beim Aufruf zu Korrektur wieder in
den Status
‚freigegeben‘
zurückgesetzt wird. Bei entsprechender
Einstellung des Rohwareparameters
Abrechnung nach Belegkorrektur
kann der Beleg nach erfolgreichem Abschluss der Korrektur aber automatisch durch
das Modul in den abgerechneten Zustand versetzt werden.
Nicht geändert werden
können hier die Attribute Kunde bzw. Lieferant, Liefernummer und
Lieferdatum.
Natürlich können z.B. in einem Beleg der Stufe
Finalabrechnung
auch keine Zahlungsbedingungswerte etc. der Stufe
Abschlag
oder
Folgeabschlag
geändert
werden.
Kontraktzuordnungen sowie Lager, Artikel und Abrechnungsschema können
bis zu Belegen der ersten Rechnungsstufe geändert werden.
Bei der Änderung
von Lager, Artikel und Abrechnungsschema werden eventuell bereits gemachte
Angaben im Positionsteil (Mengen, Preise, Analysewerte etc.) auf ein
gegebenenfalls wechselndes Abrechnungsschema übertragen, sofern die
Identifizierung der einzelnen Positionen per übereinstimmender Referenznummer
laut Abrechnungsschemadefinition gegeben ist.
Die manuell gesetzten Werte in
Menge, Preis und Manuell können nach der Erfassung geändert werden, was zur
Neuberechnung der anderen Werte führt.
Es können mit diesem Modul
nur Belege korrigiert werden, die als nicht weiterverarbeitet gekennzeichnet
sind und nicht Teil eines existierenden Sammeldruckbelegs sind.
Zur
Orientierung befindet sich in der ersten Maskenzeile ein Informationsfeld, dass
im Korrektur- oder Ansicht-Modus Angaben über den Beleg-Status ausweist. Hier
wi
[...]


---

## Rohware-Einrichterparameter

Rohware-Einrichterparameter
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Einrichterparameter
Direktsprung
[RWB]
Artikelauswahl auf
Rohwarengruppe des Beleges beschränkt
Vorbelegung Ja
Entscheidet man sich dafür,
dass die Artikelauswahl nicht auf die Rohwarengruppe des zu korrigierenden
Beleges beschränkt ist, dann kann man Rohwarenbelege auch
rohwarengruppenübergreifend korrigieren.
Bitte beachten Sie dazu den
Hinweis zum Wechsel
der Rohwarengruppe
Vorgangsunterklasse des
Zwischenbeleges
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Vorbelegung 0
Hier legt man
die Vorgangsunterklasse fest mit der die Zwischenbelege/Lieferscheine erzeugt
werden. Für diese Unterklasse sollte das Feld RohwareVorerfassung auf ungleich
‚ohne’ stehen, ansonsten wird nach der ersten ‚gültigen’ Vorgangsunterklasse
gesucht.
Wird keine Vorgangsunterklasse mit dem Feld RohwareVorerfassung
ungleich ‚ohne’ gefunden, dann wird der Datensatz nicht in die Maske für die
Verarbeitung geladen.
Rohwarebeleg danach zur
normalen Korrektur öffnen
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Vorbelegung Nein
Möchte man an den korrigierten
Rohwarenbelegen noch weitere Änderungen vornehmen (die nicht über diese Spezial
Korrektur möglich sind, aber über die normale Korrektur), dann kann man mit
Hilfe dieses Einrichterparameters im Anschluss die Belege zur normalen Korrektur
öffnen lassen.

---

## Rohware-Erfassung

Rohware-Erfassung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Die
Erfassung von Einlagerungsbelegen unterscheidet sich nicht von der normalen
Rohwareerfassung.
Bei
der Aufnahme von Vereinnahmungen gibt es jedoch kleine Unterschiede. Aeins führt
über alle Einlagerungen pro Kunde und Artikel ein Bestandskonto.
Bei
der Einlagerung wird dieses Konto erhöht, bei einer Vereinnahmung wird es wieder
entlastet. Der aktuelle Stand dieses Kontos wird angezeigt, sofern man sich auf
dem Mengenfeld einer für die Vereinnahmung relevanten Artikelposition
befindet:

---

## Rohware-Maßeinheiten

Rohware-Maßeinheiten
Hauptmenü
Rohwarenabrechnung
Maßeinheiten Rohwaren
Mengen von Warenpositionen und
Kosten-/Vergütungspositionen sowie Analysewerte von Qualitätspositionen werden
in den
Rohwarengruppendefinitionen
Maßeinheiten zugeordnet, die in diesem Programm-Modul zu hinterlegen sind. Dabei
müssen Maßeinheiten, die für Mengen der Waren-/Kosten-/Vergütungspositionen
vorgesehen sind, die jeweils korrespondierende Mengeneinheit zuzuordnen.
Maßeinheiten ohne Mengeneinheitszuordnung sind als Einheiten für Analysewerte
und gegebenenfalls für Waren-/Kosten-/Vergütungspositionen vorgesehen, die
lediglich als Wertartikel (ohne Menge) oder Pauschalkosten/-vergütungen gebucht
werden.

---

## Rohware-Kostentexte

Rohware-Kostentexte
Hauptmenü
Rohwarenabrechnung
Kostentexte Rohwaren
Kostentexte werden den Kosten-
und Vergütungspositionen in
Rohwarengruppendefinitionen
mittels der Kostentextnummer zugeordnet. Bei der Erfassung, Ansicht oder
Korrektur von Rohwarebelegen bzw. in Auswertungen ist die jeweilige Position
durch die hier angegebene Bezeichnung identifizierbar. Die per
Formulareinrichtung festgelegte Druckposition eines Kosten- oder
Vergütungstextes wird, abweichend zum Artikeltext des durch die Position
gebuchten Artikels, ebenfalls mit dem hier festgelegten Text in der jeweiligen
Belegsprache versorgt.

---

## Rohwarenabwicklung

Rohwarenabwicklung
Hauptmenü
Rohwarenabrechnung

---

## Rohwaren -Anlieferungen erfassen

Rohwaren -Anlieferungen
erfassen
Hauptmenü
Rohwarenabrechnung
Der
Einstieg der Erfassung kann auf 2 Arten erfolgen:
1.
Über die Rohwaren-Vorerfassung
2.
Über die Rohwarenbearbeitung
Die
Rohwarenvorerfassung ist eine Kurzerfassung der Rohware mit Lieferanten-
Nr.,
Artikel und Menge. Die
Erfassung erfolgt über die Vorgangsart Bestellanfrage, Unterklasse
Rohwarenvorerfassung.
Vorteil:
Die Erfassung
unterscheidet sich nicht von den übrigen Erfassungen in der Warenwirtschaft, wie
z.B. Lieferschein, Rechnung, E-Lieferschein.
Dieser vorerfasste Beleg wird
bei der Rohwarenerfassung mit der Taste F8 Vorerfasste Belege
in
die aktuelle Erfassung übernommen und weiterbearbeitet.

---

## Rohwarenbearbeitung

Rohwarenbearbeitung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]

---

## Rohwarengruppen löschen (inkl. 6)

Rohwarengruppen löschen (inkl. 6)
Es werden die Daten in folgenden Tabellen
gelöscht:
ROHWARENGRUPPE
RohWaGruSortKrit
RohWareParamWert unter der Bedingung: where
Rohwarengruppe > 0
Beim Löschen der Rohwarengruppen  werden
automatisch die
Rohwarensorten
mit gelöscht.

---

## Rohwarenkontrakte

Rohwarenkontrakte
Hauptmenü
Kontraktverwaltung
Kontraktbearbeitung
Kontrakt Stammdaten
Direktsprung
[KTR]
Eine
Sonderform der Kontrakte stellen die Rohwarenkontrakte dar.
Wird
bei der Kontraktanlage [KTR] die Klasse Einkauf Rohware (13) oder Verkauf
Rohware (3) gewählt, verändert sich die Maske bei der Artikeleingabe wie
folgt:
Zusätzlich zu Menge und
Ausgangspreis für die finale Rohwarenabrechnung können hier jetzt eine
Rohwarengruppe und ein zugehöriges Abrechnungsschema angegeben werden, die bei
der Kontraktauswahl als Selektionsfilter wirken.
Ebenfalls können evtl.
abzurechnende Nebenpreise
•
Ausgangspreis für Abschlagabrechnung
•
Ausgangspreis für Folgeabschlagabrechnung
•
Mindestpreis-Vereinbarung
•
Weltmarktpreisfestsetzung
•
%-Satz zur Abschlag-/Folgeabschlagermittlung
festgelegt werden, sofern
diese für Rohwareabrechnungen abweichend von im Abrechnungsschema festgelegten
Konditionen vereinbart sind.

---

## Rohware-Formeln für Zu- und Abschläge

Rohware-Formeln für Zu- und Abschläge
Hauptmenü
Rohwarenabrechnung
Formeln für Zu-/Abschläge
In
Rohwarengruppen
deklarierte und in
Abrechnungsschemata
näher definierte
Qualitäten
können unter
anderem mittels Formeln bei der Abrechnung eines Rohwarebeleges einen Zuschlag
oder Abschlag auf die Menge (
Abrechnungsart ‚Mengen-Zu-/Abschlag‘, ‚
Mengen-Zu-/Abschl. mit Preisgew.‘, ‚Mengen-Zu-/Abschl. mit WmPr.gew.‘
)
oder Preis (
Abrechnungsart ‚Preiszu-/abschlag‘
) einer bestimmten
Warenposition bewirken. Ein Zuschlag beziehungsweise Abschlag wird hier dadurch
ermittelt, dass zunächst ein %-Wert aus Umrechnungsfaktor multipliziert mit der
Analysewert/Basiswert-Differenz (ergänzt um die Basiserweiterung) ermittelt
wird, in den Abrechnungsarten mit Preis- bzw. Weltmarktpreisgewichtung
multipliziert mit dem entsprechenden Preis (umgerechnet auf eine Mengeneinheit),
und dieser dann auf die in der Qualitätsdefinition angegebene Bezugsmenge bzw.
den Bezugspreis angewendet wird.
Besonderheiten der
Lagernummer
: Das Abrechnungssystem sucht eine
Zu-/Abschlag-Formel-Einrichtung zunächst mit der Lagernummer des Rohwarebeleges.
Ist diese nicht eingerichtet, so wird auf die Einrichtung zur Lagernummer ‚0‘
zurückgegriffen.

---

## Rohware mit Vorkonto

Rohware mit Vorkonto
Bei ‚Ja’ werden auch Rohwareabrechnungen über den
Vorkontenmechanismus abgewickelt

---

## Rohwarengruppen-Ergänzungsfelder

Rohwarengruppen-Ergänzungsfelder
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Bearbeiten
Ergänzungsfelder
Direktsprung
[RWG]
Die
hier definierten Felder stehen ‚rohwarengruppenweit’, also für Belege aller
Schemata der Rohwarengruppe zur Verfügung.

---

## Rohwarenparameter

Rohwarenparameter
Alle Qualitätswerte werden über die Nummer des
Qualitätskriteriums aus der Waage identifiziert. Um bei der Erstellung der
Belege diese Qualitätskriterien zu berücksichtige, muss der Rohwareparameter
„Umwandlung - Qualität per“ auf „per Waagen-Qualitätsnummer“ stehen.

---

## Rohwaren Tabellen löschen

Rohwaren Tabellen löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
RohWareKostGrup
RohWareKostPau
RohWareKostSatz
RohWareKostStaff
RohWareKostStWrt
RohWareQualiTab
RohWareQualWert
RohWareUmrFaktor
RohWareZA_Formel
RohWareAnKorTab
RohWareAnKorWert
RohWareUmrTab

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

## Rohwareparameter & Rohwarewaagenparameter löschen

Rohwareparameter & Rohwarewaagenparameter
löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
RohWareParamWert unter der Bedingung: where
(RohWaPaAbDatum > '01-01-1901') or (Rohwarengruppe > 0) or (RohSorteId
> 0)
RWWaagenParamWert unter der Bedingung: where AbDatum
> '01-01-1901'

---

## Rohware-Qualitäten [ROHQU]

Rohware-Qualitäten
[ROHQU]
Allgemeines
Wird Ware angeliefert, so kann sofort eine Probe zur
Ermittlung der Qualitäten genommen werden. Diese Probe wird anhand der
Partienummer identifiziert. So kann unabhängig davon, ob bereits ein Beleg
existiert oder nicht, Qualität erfasst und später verarbeitet werden.
Direktsprung
Die Auswahlliste erreichen Sie mit dem Direktsprung
ROHQ
Funktionen
Mit dieser Anwendung erhalten Sie einen Überblick über
erfasste und noch nicht erfasste Qualitäten und können Qualitätsdaten zu Partien
erfassen, ändern oder löschen.
Darüber hinaus steht Ihnen die Möglichkeit zur
Verfügung, einen Mittelwert aus gewählten Qualitäten zu bilden, und diesen als
neuen Qualitätsdatensatz festzulegen.

---

## Rohware-Qualitätstexte

Rohware-Qualitätstexte
Hauptmenü
Rohwarenabrechnung
Qualitätstexte Rohwaren
Qualitätstexte werden den
Qualitäten in
Rohwarengruppendefinitionen
mittels der Qualitätstextnummer zugeordnet. Bei der Erfassung, Ansicht oder
Korrektur von Rohwarebelegen bzw. in Auswertungen ist die jeweilige Qualität
durch die hier angegebene Bezeichnung identifizierbar. Die per
Formulareinrichtung festgelegte Druckposition eines Qualitätstextes wird je nach
Analysewert/Basiswert-Beziehung mit dem jeweils hier festgelegten Text in der
jeweiligen Belegsprache versorgt.

---

## Rohwarequalitäts- und -Kostenpositionen: Datenbankprozedur- und Itembox-Einsatz

Rohwarequalitäts- und
-Kostenpositionen: Datenbankprozedur- und Itembox-Einsatz
Für
die Erfassung und Korrektur von Rohwarebelegen können zur Unterstützung für
manuell zu erfassende Analysewerte in den zugehörigen Qualitätsdefinitionen der
Abrechnungsschemata auch (private) Itembox-Zuordnungen eingetragen werden.
Zur
Abrechnung von Qualitäts- und Kostenpositionen können auch (private)
Datenbankprozeduren zur
Versorgung oder Berechnung bestimmter Werte eingesetzt werden.

---

## Rohware-Tabellen für Zu- und Abschlag-Staffeln

Rohware-Tabellen für Zu- und
Abschlag-Staffeln
Hauptmenü
Rohwarenabrechnung
Staffeln für Zu-/Abschläge RW
In
Rohwarengruppen
deklarierte und in
Abrechnungsschemata
näher definierte
Qualitäten
können unter
anderem mittels Zu- und Abschlag-Staffeln bei der Abrechnung eines
Rohwarebeleges einen Zuschlag oder Abschlag auf die Menge (
Ergebnis als
‚Mengenzu-/abschlag‘
) oder Preis (
Ergebnis als ‚Preiszu-/abschlag‘
)
einer bestimmten Warenposition bewirken. In der Variante
Abrechnung mit
‚einfacher Umrechnungsfaktor‘
wird ausgehend von der
Analysewert/Basiswertdifferenz
ergänzt um die
Basiserweiterung
zunächst der zugehörige
Umrechnungsfaktor
ermittelt. Dieses ergibt
multipliziert mit der (erweiterten) Analysewert/Basiswertdifferenz die Preis-
oder Mengen-Änderung pro 100 Mengen- bzw. Preiseinheiten ( in der Regel also
kg/dt oder ct/Euro ), also in Prozent. Die Basiserweiterung trägt der Tatsache
Rechnung, dass beispielsweise erst ab einem Analysewert über 15,0 % Feuchtigkeit
getrocknet werden soll, dann aber bis auf 14,5 % (Basiserweiterung = 0,5).
Bei einem Analysewert von 18,3% und einem Basiswert von 9,0% würde sich mit
angegebener Beispiel-Staffel folgende Rechnung ergeben:
(Analysewert 18,3 –
Basiswert 9,0) + Basiserweiterung 0,5 = 9,8
Umrechnungsfaktor 1,4 * 9,8 =
13,72%
In
der Variante
Abrechnung mit ‚gestaffelte Abrechnung‘
erfolgt die
Ermittlung des  Ergebnis-Prozentwerts als Summe der ermittelten
Ergebnis-Prozentwerte der einzelnen Intervalle. Bei einem Analysewert von 18,3%
und einem Basiswert von 9,0% würde sich mit angegebener Beispiel-Staffel
folgende Rechnung ergeben:
(Analysewert 18,3 – Basiswert 9,0) +
Basiserweiterung 0,5 = 9,8
1. Intervall: bis 4,4 mit Umrechnungsfaktor 1,2
ergibt 4,4*1,2 =  5,28%
2. Intervall: bis 8,4 mit Umrechnungsfaktor 1,3
ergibt 4,0*1,3 =  5,20%
3. Intervall: bis 9,8 mit Umrechnungsfaktor 1,4
ergibt 1,4*1,4 =  1,96%
ergibt als Ergebnis 5,28+5,20+1,96 = 12,44%
Besonderheiten der
Lagernummer
: Das Abrechnun
[...]


---

## Rohware-Tabellen zur Analysewertkorrektur

Rohware-Tabellen zur
Analysewertkorrektur
Hauptmenü
Rohwarenabrechnung
Tabellen für Analysekorrektur
In
Rohwarengruppen
deklarierte und in
Abrechnungsschemata
näher definierte
Qualitäten
können unter
anderem mittels Analysewert-Korrektur-Tabellen einen erfassten Analysewert bzgl.
der Analysewerte anderer Qualitäten in einen korrigierten Analysewert umrechnen,
der dann anstelle des Originalwertes die Abrechnungsgrundlage bildet. Die Angabe
‚Werte in‘
legt die Interpretation der Tabellenwerte als
‚Prozentsatz‘
oder
‚Korrekturwert in Einheit des zu korrigierenden
Analysewertes‘
fest. Die Indexwerte der Skala beziehen sich auf den
Analysewert (
‚Fixskala‘
) bzw. die Analysewert/Basiswertdifferenz
(
‚relative Skala‘
) einer in der Qualitätsdefinition angegebenen
Referenzqualität. Der Wert, um den der Analysewert der aktuellen Qualität zu
korrigieren ist, wird dann der Spalte
‚Wert‘
zum Skalenwert entnommen.
Die
Angaben in den Feldern ‚
von
‘, ‚
bis
‘ und ‚
Schrittweite
‘
legen die
Indexwerte
der Tabelle für die Pflege fest, zu denen dann die
Ergebniswerte eingetragen werden.
Zu beachten
ist jedoch, dass das
Abrechnungsmodul bei über den hier festgelegten letzten Indexwert auftretendem
Indexwert einen Ergebniswert aus den für die letzten beiden Indexwerte
eingetragenen (zugeordneten) Ergebniswerten zu ermitteln. Dieses geschieht durch
dynamisches fortschreiben der Tabelle mit der angegebenen Schrittweite und der
Differenz der letzten beiden Ergebniswerte. So wäre der Ergebniswert für obiges
Beispiel bei einer Analysewert/Basiswertdifferenz von 6,0 = 3,0
(Indexwert
6,0 – letzter Indexwert 3 = 3 Indexdifferenz
= 3 * Schrittweite
1
also 3 * (letzter Ergebniswert 1,5 – vorletzter Ergebniswert
1) = 1,5
und daher 1,5 + 1,5 = 3,0 Ergebniswert zu Indexwert 6)
Der
Ergebniswert von 6 wird in dem Beispiel für alle
Analysewert/Basiswertdifferenzen der Referenzqualität, die größer als 5 und
kleiner oder gleich 6 sind.
Besonderheiten der
Lagernummer
: Das Abrec
[...]


---

## RW-Auswertung Excel

RW-Auswertung Excel
Hauptmenü
Rohwarenabrechnung
Excel-Kommunikation
RW-Auswertung bereitstellen
Direktsprung
[RWAUS]
Mit diesem Aufruf wird die Rohwarenauswertung
aufgerufen.
Zur Erstellung der Auswertung wird zunächst eine
Listenfeld-Definition angegeben, die die Spalteninhalte sowie die individuelle
Behandlungsweise der Spalten bei Teilsummen- und Endsummenbildung beschreibt.
Hierfür steht neben der direkten Eingabe der Definitionsnummer die
Auswahlfunktion per
F3
-Taste zur Verfügung, in der es auch eine Funktion
‚Stammdaten‘
zum Aufruf des Moduls zur Erstellung und Pflege der
Listenfeld-Definitionen gibt.
Ebenfalls angegeben werden muss die Selektions-
und Gruppierungs-Definition, die die Reihenfolge der Datenzeilen und die
Teilsummenauslösungskriterien angibt sowie die Vorbelegung der
Selektionskriterien enthält. Hierfür steht ebenfalls neben der direkten Eingabe
der Definitionsnummer die Auswahlfunktion per
F3
-Taste zur Verfügung, in
der es auch eine Funktion
‚Stammdaten‘
zum Aufruf des Moduls zur
Erstellung und Pflege der Auswertungs-Sortierungs-Definitionen gibt.
Die
Trennung zwischen Listenfeld-Definition und Selektions- und
Gruppierungs-Definition erfolgt, um Kombinationen dieser beiden Möglichkeiten
zuzulassen.
Die vorbelegten Angaben zur Selektion können nun wie
gewünscht geändert werden.
Im unteren Teil der Maske kann die Art der zu
berücksichtigenden Belege durch aktivieren der/des entsprechenden Buttons (
nicht ausgewählt,
ausgewählt) ausgewählt werden.
Ferner kann man den Ein- oder Ausschluss von
Fremdwarebuchungen (Einlagerung und Vereinnahmung der Einlagerung) festlegen.
Hier ist jedoch darauf zu achten, dass es im Falle der Berücksichtigung des
Einlagerungs-/Vereinnahmungsstatus in der gewählten Sortierdefinition zu keinen
ungewollten Einschränkungen kommt.
Mit der Funktion
‚Starte Aufbereitung …‘
wird
das Modul zur Datengewinnung ausgeführt und die Ergebnisse in einer Auswahlliste
dargestellt, um diese zum Beispiel mit ei
[...]


---

## Rohware / Vermarktung Übersicht

Rohware / Vermarktung
Übersicht
Das
Modul Rohware eignet sich für den Einkauf und Verkauf aller landwirtschaftlichen
oder ähnlich strukturierten (Rohware-)Erzeugnisse.
Es
ist also nicht auf die Abrechnung von Getreide und Raps beschränkt. Vielmehr ist
das Programmsystem derart flexibel gestaltet, dass praktisch alle
Abrechnungsmodalitäten mit allen Rohware-Erzeugnissen schnell und sicher
abgerechnet werden können.
Dadurch stellt sich beim
Einsatz nicht so sehr die Frage, ob eine Abrechnungsmodalität möglich ist,
sondern vielmehr, in welcher Weise das Programm eingestellt werden muss, damit
die gewünschten Ergebnisse erreicht werden. Dazu bedarf es umfangreicher
Kenntnisse über die Möglichkeiten der Einrichtung von Tabellen und Definitionen
von Abrechnungsschemata.
Die
Rohwarenabrechnung unterscheidet sich von ‘normalen’ Warenvorgängen unter
anderem dadurch, dass hier keine Übereinstimmung zwischen der bewegten Menge und
der zu buchenden Menge bestehen muss. Eine angenommene Bruttomenge kann durch
diverse qualitative Einflüsse verändert werden, ebenso haben Qualitäten Einfluss
auf den abzurechnenden Preis.
Die
Qualitätsermittlung kann u.U. längere Zeit in Anspruch nehmen, wodurch eine
vorläufige (Abschlag) vor der endgültigen (finalen) Abrechnung notwendig werden
kann. Hierbei muss die Möglichkeit des Nachtrages von Qualitäten sowie der
nachträglichen Änderung von Abrechnungsmodalitäten gegeben sein.
Anlieferer von Rohwaren im
Landhandelsbereich sind häufig Landwirte, welche nicht über die Möglichkeit
verfügen, Abrechnungen selbst zu erstellen, so dass vom Abnehmer die Erstellung
erwartet wird.
Die
Steuerermittlung gestaltet sich dadurch schwierig, dass es sich bei
Lohnabrechnung der Ware bei z.B. Trocknung um volle Steuersätze, bei Ankauf um
warenbegleitende Dienstleistungen zu reduzierten Steuersätzen handeln kann.
Regionale Unterschiede und die
Vielzahl der abzurechnenden Fruchtarten verlangen eine große Flexibilität in
Beschreibung un
[...]


---

## Rohware-Tabellen für Zu- und Abschläge

Rohware-Tabellen für Zu- und Abschläge
Hauptmenü
Rohwarenabrechnung
Tabellen für Zu-/Abschläge RW
In
Rohwarengruppen
deklarierte und in
Abrechnungsschemata
näher definierte
Qualitäten
können unter
anderem mittels Tabellen für Zu- und Abschläge bei der Abrechnung eines
Rohwarebeleges einen Zuschlag oder Abschlag auf Menge oder Preis einer
bestimmten Warenposition bewirken. Dabei kann die Ermittlung eines Zu- oder
Abschlagwertes auf unterschiedliche Art erfolgen. Grundsätzlich handelt es sich
jedoch immer um eine Art LOOKUP-Verfahren, in dem zu einem Indexwert ein
Ergebniswert aus einer Tabelle bestimmt wird. Die Angabe im Feld ‚
Werte
in
‘ bestimmt zunächst, wie der Ergebniswert der Tabelle zu interpretieren
ist:
•
Prozentsatz vom Preis
•
Prozentsatz von der Menge
•
absolut in Währungseinheiten (zum Beispiel
EUR
bei
Euro)
(festgelegt durch den Steuerparameter ‚Währungsnummer für
Rohwaretabellen‘)
•
absolut in
Mengeneinheiten
(der bezogenen
Warenposition)
Mit
dem Wert im Feld ‚
Faktor
‘ (in der Regel ‚1‘) wird der gefundene
Ergebniswert der Tabelle multipliziert.
Der
Skalentyp ‚
fix
‘ bewirkt, dass der zugrundeliegende Analysewert direkt als
Indexwert herangezogen wird. Die Angabe ‚
relativ
‘ hingegen berechnet den
Indexwert als Differenz zwischen Analyse- und Basiswert der Qualität.
Die
Angaben in den Feldern ‚
von
‘, ‚
bis
‘ und ‚
Schrittweite
‘
legen die
Indexwerte
der Tabelle für die Pflege fest, zu denen dann
Ergebniswerte eingetragen werden.
Die
Felder ‚
von‘
, ‚
bis
‘ und ‚
Schrittweite
‘ sind Pflichtfelder.
Dort bestimmt man, wie die untere Tabelle aufgebaut wird, von Anfangs -
bis Endwert und benötigte Schrittweite.
Achtung
: Sollte einer
der 3 Werte nachträglich geändert werden, gehen alle dort schon eingerichteten
Informationen verloren.
Zu beachten
ist
jedoch, dass das Abrechnungsmodul bei über den hier festgelegten letzten
Indexwert auftretendem Indexwert einen Ergebniswert aus den für die letzten
beiden Indexwerte eingetragene
[...]


---

## Rohware-Vorerfassung

Rohware-Vorerfassung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohware-Vorerfassung
Direktsprung
[RWV]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohware-Vorerfassung bearbeiten
Direktsprung
[RWVB]
Das
Modul zur Vorerfassung von Rohwareanlieferungen dient der schnellen Erfassung
von Rohwarebeleg-Daten wie Wiegenummer, Kunde, Artikel, Menge sowie
gegebenenfalls eine Partienummer, wenn zum Beispiel noch keine
rohwarespezifischen Details bekannt sind.
Die
Daten von Vorerfassungsbelegen können im Rohware-Bearbeitungs-Modul bei der
Erfassung einer Rohwareanlieferung im Maskenfeld
Artikel
mit der Funktion
Vorefassungsdaten übernehmen [F8]
zur Übernahme in den
Rohwarebeleg ausgewählt werden.
Intern wird der
Vorerfassungsbeleg als Vorgang der Vorgangsklasse 1100 (Bestellanfrage) mit
Unterklasse 9999 gespeichert. Durch Vorerfassungsbelege werden noch keine
Bestandsveränderungen vorgenommen, dieses geschieht erst bei der Erfassung der
Rohwarenanlieferung.
Die
Belegnummer
und das
Belegdatum
des Vorerfassungsbeleg werden bei
der Datenübernahme auch als
Liefernummer
und
Lieferdatum
interpretiert. Dieses ist bezüglich der
Nummernkreis-Zuordnung
zu
beachten.
UFLD-Felder, die für die
Vorerfassungsdaten-Übernahme von Bedeutung sind:
Feld
Bezeichnung
Bedeutung
1510
Lagernummer-Vorbesetzung
Wird bei Vorerfassungs-Übernahme
      übernommen
110
Wiegescheinnummer
Wird bei Vorerfassungs-Übernahme
      übernommen
1771
Bemerktext1
Wird als
Partienummer
bei
      Vorerfassungs-Übernahme übernommen
1772
Bemerktext2
Wird als
Bemerktext1
bei
      Vorerfassungs-Übernahme übernommen, ist aber nur bei Druck des Zielbelegs
      sichtbar
1773
Bemerktext3
Wird als
Bemerktext3
bei
      Vorerfassungs-Übernahme übernommen, ist aber nur bei Druck des Zielbelegs
      sichtbar
1774
Bemerktext4
Wird als
Bemerktext4
bei
      Vorerfassungs-Übernahme übernommen, ist aber nur bei Druck des Zielbelegs
      sichtbar
1775
Bemerktext5
Wird als
Bemerktext5
bei
      V
[...]


---

## Sammelbelege: Rohwareergänzungswerte ändern

Sammelbelege: Rohwareergänzungswerte
ändern
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
In
der Variante ‚Bearbeiten Sammeldruck‘ können mit der Funktion ‚Ergänzungswerte‘
nachträglich noch die Rohwarenergänzungsparameter bei Rohwaresammelbelege
der  dazugehörigen Rohwarengruppe geändert werden.
Wenn
noch keine Rohwarenergänzungsparameter eingetragen worden sind, oder die
Rohwarenergänzungsparameter in den einzelnen Belegen den gleichen Inhalt haben,
so kann auf der Maske ein neuer Wert eingetragen werden.
Sind
in den Rohwarenergänzungsparameter unterschiedliche Werte eingetragen worden, so
kann erst der Wert überschrieben werden, wenn das Ankreuzfeld rechts neben dem
Textfeld aktiviert wird.
Man
muss dabei beachten, dass die Rohwarenergänzungsparameter für alle Einzelbelege
des Sammelbeleges überschrieben werden.

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

## Silokontraktanlage in der Waage(SPA 935)|

Silo
kontraktanlage in der Waage(SPA 935)|
Einstellung
Bedeutung
Nein
Keine Auswirkungen
Ja
Im
      Offline Übernahmemodul werden die eingehenden Kontrakte bei nichtvorhanden
      sofort automatisch erzeugt.

---

## Stapelkorrektur

Stapelkorrektur
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Im
Modul Rohwarenbearbeitung können in der Auswahlvariante
‘
Rohwarestapelkorrektur’
Änderungen für mehrere Belege gleicher Stufe in
einem Arbeitsschritt durchgeführt werden.
Hier
wird mit der Funktion ‚
Stapelkorrektur
’ eine Maske zur Eingabe diverser
zu ändernder Daten aufgerufen. Grundsätzlich können nur Lieferungen und nicht
gedruckte und nicht gebuchte Abrechnungsbelege der Stufen Abschlag,
Folgeabschlag und Finale korrigiert werden, wenn diese noch nicht
weiterverarbeitet sind.
Es
werden nur Daten zur Änderung angeboten, die aufgrund der Stufe der ausgewählten
Belege änderbar sind. So können zum Beispiel in Final-Belegen keine
Abschlagdaten geändert werden.
Analysewerte werden mittels der Funktion
‚
Analysewerte
‘ nur dann zur Änderung angeboten, wenn alle ausgewählten
Belege genau einer Rohwarengruppe zugeordnet sind und es sich bei den Belegen um
nicht gedruckte und nicht gebuchte Rechnungen handelt. Analysewertkorrekturen
für Lieferungen sind an dieser Stelle nicht möglich.
Die gewünschten
Änderungen werden mittels der Funktion ‚
Änderungen starten
‘ in allen
ausgewählten Belegen durchgeführt. Wird dabei ein bereits abgerechneter Beleg
verändert, so wird das Abrechnungskennzeichen auf ‚
Freigegeben
‘
zurückgesetzt.
Wird
in der Stapelkorrektur ein Analysewert, unterer Basiswert oder oberer Basiswert
geändert, so wird im zugehörigen zu änderndem Beleg ein gegebenenfalls manuell
überschriebener Qualität-Zu-/-Abschlag bzw. Kosten-/Vergütungsbetrag auf nicht
manuell zurückgesetzt und neu berechnet.

---

## Start Korrektur F9

Start Korrektur F9
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Hiermit startet man die
Korrektur der in der Maske angezeigten Belege.
Die auf der Maske eingegebenen
Werte werden dafür verwendet.
Die zu korrigierenden Rohwarenbelege werden
storniert und über die Erzeugung eines neuen Lieferscheines, der in einen
Rohwarenbeleg gewandelt wird, neu erzeugt.

---

## Statusstapelkorrektur

Statusstapelkorrektur
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Im
Modul Rohwarenbearbeitung können in der Auswahlvariante
‘Rohwarestatusstapelkorrektur’
Belegstatus-Änderungen für mehrere Belege
gleicher Stufe in einem Arbeitsschritt durchgeführt werden, die noch nicht
weiterverarbeitet sind. Final-Belege können nur bverücksichtigt werden, wenn sie
weder gedruckt noch gebucht sind.
Hier wird mit der Funktion
‚
Status-Stapelkorrektur
’ eine Maske zur Eingabe der zu ändernden
Beleg-Status-Kennzeichen aufgerufen.
Grundsätzlich können
Lieferungen und Abrechnungsbelege der Stufen Abschlag, Folgeabschlag und Finale
korrigiert werden. So können zum Beispiel auch in bereits gebuchten
Abschlagbelegen die Statusinformation der Stufen Folgeabschlag und Finale auf
den Wert ‚
Freigegeben
‘ gesetzt werden. Der eigene Status zur Belegstufe
selbst kann nur von ‚
Abgerechnet
‘ zurückgesetzt werden, wenn der Beleg
noch nicht gebucht wurde. Zu beachten ist, dass Rohwarelieferungen zu
Voreinkäufen oder Vorverkäufen nur per Finalabrechnung weiterbearbeitbar sind.
Daher sind für derartige Belege die Statuskennzeichen für die Stufen Abschlag
und Folgeabschlag nicht änderbar. Diese haben immer den Wert ‚
ohne
‘, da
der jeweils zugrundeliegende Voreinkauf beziehungsweise Vorverkauf anteilig als
Abschlagzahlung in der Finalabrechnung berücksichtigt wird.
Neben den
Belegstatus-Werten kann an dieser Stelle auch das Kennzeichen zur Steuerung der
jahresübergreifenden Abrechnung mittels Pro-Forma-Abrechnung angegeben
werden.
Die gewünschten Änderungen werden mittels der Funktion ‚
Änderungen
starten
‘ in allen ausgewählten Belegen durchgeführt.

---

## Steuerbescheinigung Kapitalertragssteuer

Steuerbescheinigung
Kapitalertragssteuer
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zinswesen
Zinsabrechnung bearbeiten
Variante
Steuerbescheinigung
Kapitalertragssteuer
Direktsprung
[ZIB]
Der Zinsabschlag ist eine spezielle Form der
Kapitalertragssteuer. Für die einbehaltene Kapitalertragsteuer kann eine
Bescheinigung gedruckt werden. Dazu müssen die Stammdaten für
Zinsgruppen
und
Zinsabschlag
eingerichtet sein und
die entsprechenden Zinsen gebucht sein. Die so entstandenen Belege findet man
dann in der Variante
Steuerbescheinigung Kapitalertragsteuer
der
Anwendung
Zinsen bearbeiten
wieder. Dort kann dann mit der Funktion
Steuerbescheinigung drucken
der Formulardruck aufgerufen werden. Für den Druck
wird ein Formular vom Typen 600 „Belegdruck Finanzbuchhaltung“
verwendet.
Es wird ein Beispielformular (Formularnummer -1200) mit ausgeliefert. In diesem
Formular wird für die Texte eine spezielle Druckposition verwendet
(ID_FIBU_DRUCKTEXT).  Diese bezieht ihren Text für einzelne Konten über die
Textvorbelegung (Direktsprung
[FITXT]
). Dort können in der Variante
Kontotexte
Texte für Sachkonten hinterlegt werden, die dann beim Druck
der Steuerbescheinigung herangezogen werden.
Ist kein Text hinterlegt, so wird der Text verwendet,
der im Beleg zu diesem Konto steht.

---

## Steuerparameter der Rohwarenabrechnung

Steuerparameter der
Rohwarenabrechnung
Hauptmenü
Administration
Steuerung
Steuerparameter zeigen
Direktsprung
[RWPA]
Wert
Sort.
Bezeichnung
     Gruppe
1
1
"Artikel/Schema-Auswahl"
nur global
1
2          "Erfassungsstapel mit
Liefermengensummen"
1
3          "Ab Kundennummer bei
Folgebeleg"
1
4          "Filiale"
1
5          "Filiale aus
Kundenstamm"
1
6          "Erfassung der
Zentrale"
1
7          "Zentrale aus
Filialstamm"
1
8          "Abteilung"
1
9          "Unterabteilung"
1
10        "Lieferdatum > Erfassungsdatum
erlaubt"
1
11        "Liefermengensperre bei
Korrektur"
1
12        "Kippwaagen-Kontrollrechnung"
1
13        "Kundenanschrift Autoanzeige"
1
14        "Artikelauswahl-Randbedingung"
2
1
"Lager"
Erfassung (Seite 1)
2
2          "Lagerplatz"
2
3          "Liefer-Datum"
2
4          "Lieferscheinnummer"
2
5          "Vorbelegung
Lieferscheinnummer"
2
6          "Wiegenoten-Nummer"
2
7          "Vorbelegung
Wiegenoten-Nummer"
2
8          "Versandart"
2
9          "Vorbelegung
Versandart"
2
10        "abweichende Versandadresse
erlaubt"
2
11        "Kippwaage: Kippmenge"
3
1          "Zahlungsart
Abschlag"
Erfassung (Seite 2)
3
2          "Vorbelegung Zahlungsart
Abschlag"
3
3          "Zahlungsart
Folgeabschlag"
3
4          "Vorbelegung Zahlungsart
Folgeabschlag"
3
5          "Zahlungsart Finale"
3
6          "Vorbelegung Zahlu
[...]


---

## Storno

Storno
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]

---

## Stornoabrechnung:

Stornoabrechnung:
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Den
falschen Beleg in der Rohwarenanlieferung markieren. Danach unten links
Optionen
Die
Erstellung von Stornobelegen erfolgt für Rohwarelieferungen mit der Funktion
Lie. Stornobeleg
und für Rohwareabrechnungen (Abschlag, Folgeabschlag,
Finale) mit der Funktion
Abr. Stornobeleg
in den Auswahllisten mit
Einzelbelegen des Rohwarebearbeitungsmoduls.
Stornobelege zu
Sammeldruckbelegen (Sammelabrechnungen) werden mit der Funktion
Sammel-Storno
erstellen
in der Auswahllistenvariante
Bearbeiten Sammeldruck
erzeugt.
Für
die Funktionen zur Stornobelegerzeugung zu einzelnen Rohwarebelegen gibt es eine
Reihe von Rohwareparametern [RWPA] und Einstellungen auf der Steuerungsmaske,
die das Verhalten steuern und Einfluss auf bestimmte Werte der erzeugten
Stornobelege haben.
Zunächst bestimmt der Parameter
Stornobeleg nur nach
Fibuübertrag
ob die Stornobeleg-Erzeugung auch zu nicht gebuchten
Belegen erfolgen darf. Handelt es sich bei den zu stornierenden Belegen um
Vorgänge aus anderen als dem aktuellen Geschäftsjahr, so bestimmt der Parameter
Storno alter Belege
nach Inventureinspielung
,
wie bei Vorliegen einer
zwischenzeitlich bereits eingespielten Inventur zu verfahren ist.
Der
Parameter
Belegdatum
bei Stornobelegen
legt fest, ob die Stornobelege mit dem Belegdatum der
 Quellbelege erstellt werden sollen oder dieses auf der Steuerungsmaske von
Fall zu Fall einzustellen ist.
Dabei ist zu beachten, dass in der Variante
Stornobelegerstellung ohne Kopie des Originalbelegs das ggf. angegebene
Belegdatum ebenso wie die ggf. angegebene Periode im selben Geschäftsjahr wie
das des zu stornierenden Belegs liegen muss..
Mit dem Parameter
Perioden bei
Stornobelegen
wird die Periodenbehandlung der Stornobelege festgelegt.
Es können die Originalperioden erhalten bleiben o
[...]


---

## Streckenerfassung Report Abruf

Streckenerfassung Report Abruf
Dieser Beleg dient dazu einen Teil der im Kontrakt
vereinbarten Gesamtmenge beim Lieferanten anzufordern. Er gibt dem Lieferanten
sozusagen grünes Licht für die Lieferung und enthält genaue Mengen und
Terminangaben.
Sprachabhängigkeit
Welche Felder gepflegt werden müssen, um die
Sprachabhängigkeit nutzen zu können liest man unter
Sprache der Reporte
.
Sprachabhängige Textfelder in diesem Report
Name Druckfeld
Standard Text im
    Report
Ueberschrift_Abruf
Abruf Nr.:
Anrede
Sehr
      geehrte Damen und Herren,
an
an:
zurLieferung_Abruf
gegen oben genannten Kontrakt
      stellen wir wie folgt zur Lieferung frei:
Unbedingt_angeben
(bitte unbedingt im Lieferschein
      angeben)
Mfg
Mit
      freundlichen Grüßen
Warensorte
Warensorte
Menge
Menge ca.
Anlieferadresse
Anlieferadresse
Termin
Termin
Entladung_gegen
Entladen gegen Kontrakt
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

## SVWARE

SVWARE
Auf der SVWARE Maske wird nach jeder Eingabe eines
Wertes und nach der Kontraktabwahl das zu aktualisieren AIS aufgerufen.
Folgende Nummer, IDs werden in Abhängigkeit des Feldes
an das Makro übergeben. Ist der Typ eine Funktion wie z.B. die Kontraktabwahl,
so konnte dem Aufruf zum aktualisieren des AIS kein eindeutiges Feld auf der
SVWARE Maske zugeordnet werden.
Maskenfeld
Übergebene IDs
Nummer
Typ
LagerNummer$
ID_LAGERNUMMER
1008
Maskenfeld
ArtikelNummer$
ID_ARTIKELNUMMER
1006
Maskenfeld
LagerPlatzNummer$
ID_LAGERPLATZ
1103
Maskenfeld
Menge$
ID_MENGE
1001
Maskenfeld
ME_Nummer$
ID_ME_NUMMER
1108
Maskenfeld
FremdKtrNummer$
ID_KTRNUMMER
3003
Maskenfeld
KTR.KtrNummer$
ID_KTRNUMMER
3003
Maskenfeld
Preis$
ID_PREIS
1000
Maskenfeld
PreisEinh$
ID_PREISEINHEIT
1078
Maskenfeld
ME_NummerPreis$
ID_ME_NUMMERPREIS
1077
Maskenfeld
Netto$
ID_BETRAG
1464
Maskenfeld
SkontoKennz$
ID_SKONTIERFAEHIG
1030
Maskenfeld
ZusatzInfo$
ID_ZUSATZINFO
1353
Maskenfeld
ZusatzInfo2$
ID_ZUSATZINFO2
1358
Maskenfeld
LiefDat$
ID_LIEFDAT
1009
Maskenfeld
Liefernummer$
ID_LIEFNUMMER
1042
Maskenfeld
FiktivMenge$
ID_ME_NUMMER_FIKTIV
1825
Maskenfeld
KolloMEErgebnis$
ID_PREISBEZUG
540
Maskenfeld
GeschaeftsArt$
ID_GESCHAEFTSART
458
Maskenfeld
artirab$
ID_ZUABNUMMER
1343
Maskenfeld
rabsatz$
ID_ZUABPREIS
1242
Maskenfeld
rabnetto$
ID_BETRAGZUAB
1465
Maskenfeld
PartieGrid
ID_PARTIENUMMER
1473
Funktion
Kontraktabwahl
ID_KTRNUMMER
3003
Funktion
Nachhaltig
ID_NH_STATUS
7050
Funktion
Benötigte JVARS
JAVR
Funktion
Bedeutung
VORGANGHANDLE
Lesend
Mit
      dieser JAVR wird der aktuelle Handle des Vorgangs übergeben
WAPOSITIONHANDLE
Lesend
Mit
      dieser JVAR wird der Handle der Warenposition übergeben.
ID
Lesend
Mit
      dieser JVAR wird die Nummer der ID übergeben
FELDNAME
Lesend
Diese JVAR enthält den Namen des
      aufrufenden Feldes. Das Feld kann aber auch eine Funktion sein. Es wird
      der Feldname aus der Spalte Maskenfeld von der Tabelle drüber an das Makro
      übermittelt.
Makro Beispiel
[...]


---

## Tabelle zur Version: 8.3.2306.9

Tabelle zur Version: 8.3.2306.9
ID
Releasenote - Titel
Geprüft
33741
Rücklasten
33823
Kassensystem: Marktkasse Arbeitsspeicher
    Auslastung
33845
Kassensystem: TSE Fehler 4180
33807
Auswahlliste 'Kontrakte auch ohne Artikel'
33885
Rohware manuelle Werte. Preisberechnung bei
      abweichender Mengeneinheit
33865
Neue Version Android-Scannerapp
33203
Darstellung der Stoffstrom-Mengen in der
      Vorgangsübersicht

---

## Tabelle zur Version: 9.0.2402.2

Tabelle zur Version: 9.0.2402.2
ID
Releasenote - Titel
Geprüft
35249
Geodatendienst Mandantenstamm
35635
Belegfluss
35627
Kontraktstamm Länge des Eingabefeldes Hauptkunde
35447
Belegdatum bei der Erzeugung von
      Rohware-Stornobelegen
35519
Onlinewaage Versandanschrift

---

## Vorgangs- und Rohwarendaten

Vorgangs- und Rohwarendaten
Die Konfiguration der Waagenschnittstelle sollte
weitestgehend auf einer Referenzdatenbank (z. B. einer Datensicherung der
Kundendatenbank) vorbereitet werden. Die so vorgefertigte Konfiguration kann
dann problemlos auf der Kundendatenbank eingespielt werden.
Unter Direktsprung [SCPA] wird eine Liste von
Parametergruppen für Makros angezeigt. Für die Waagenschnittstelle ist das Makro
mit der ScpriptPId „WaagenImport“ zuständig. Existiert kein solcher Eintrag, so
kann er über Die Option-Box
** WaagenImport Standard
automatisch erzeugt
werden. Die so erzeugten Parameter entsprechen dem Agricom-Standard, müssen
jedoch trotzdem überarbeitet werden.
In der Dokumentation
Parametrisierung von
Pascal-Skripten – Bedienungsanleitung
ist erläutert, welche weiteren
Funktionen in der Option-Box bereitstehen. So gibt es Funktionen zum Löschen und
zum Duplizieren von ganzen Parametergruppen. Dies macht Sinn, wenn für
verschiedene Kunden oder verschiedene Waagen- / Vorgangsimporte die jeweiligen
Parameter gesichert werden sollen.

---

## Vorgehensweise bei der Einrichtung von Abrechnungsschemata (Sorten)

Vorgehensweise
bei der Einrichtung von Abrechnungsschemata (Sorten)
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Direktsprung
[RWG]
Die
Richtigkeit der Definition von Abrechnungsschemata in der Rohware ist
wesentlicher Bestandteil des Gesamtsystems. Gehen Sie dabei wie folgt vor:
1.  Zunächst gruppieren
Sie Ihre Artikel, die im Einkauf und/oder Verkauf per Rohwarenabrechnung zu
behandeln sind in sinnvolle Rohwarengruppen. Ein einzelner Artikel wird im
Artikelpflegemodul keiner oder genau einer Rohwarengruppe zugeordnet. Natürlich
können mehrere Artikel einer Rohwarengruppe zugeordnet werden. Soll ein Artikel
zum Beispiel für unterschiedliche Kunden- oder Lieferantengruppen auf
unterschiedliche Art und Weise abgerechnet werden, so werden zu diesem Zweck in
der entsprechenden Rohwarengruppe unterschiedliche Abrechnungsschemata
angelegt.
2.
Schreiben Sie alle Abrechnungsschemata (Sorten), die abgerechnet werden sollen,
mit folgenden Hinweisen auf ein Blatt Papier:
a)
Name des Abrechnungsschemas (z.B. Sorte "Gerste normal")
b)
Alle relevanten Qualitätskriterien mit den jeweiligen Basiswerten
•
z.B. "Feuchtigkeit", Basis 15,0 bis 15,5 %
•
z.B. "Protein", Basis 12,5 %
c)
Alle relevanten Kostenkriterien
•
z.B. " Trocknungskosten
•
z.B. Probenahmekosten
•
z.B. Reinigungskosten
d)
Alle Waren- und Finanzkonten, die von diesem Abrechnungsschema angesprochen
werden sollen.
•
Artikelnummer
Sachkonten (Ware /
Dienstleistung)
3.
Prüfen Sie in den Programmen WAWI und FIBU, ob alle relevanten Waren- und
Finanzkonten vorhanden sind.
4.
Legen Sie in nun die benötigten Rohwarengruppen und Abrechnungsschemata an.
Rohwarengruppen
-Definition
Hauptmenü
Rohwarenabrechnung
Rohwaren-Verwaltung
Direktsprung
[RWG]
Mittels der Funktionen
‚
Rohware/Sorten‘, ‚Rohwarenliste‘, ‚Sortenliste‘, ‚Sorten Qualität‘, ‚Sorten
Kosten‘
und
‚Sortenliste Waren‘
können diverse CRW-Reports der
Rohware-Einrichtungsdetails erstellt werden.
Die Funktion
‚Bearbeiten‘
ermöglicht die Änder
[...]


---

## Vorkonto für Rohware

Vorkonto für Rohware
Für Rohware belege wird dieses Vorkonto als Standard
benutzt.

---

## Weiterverarbeitung

Weiterverarbeitung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Direktsprung
[RWB]
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
VK-Rohwarenbearbeitung
Direktsprung
[RWBV]
Erfasste Rohwarelieferungen
können in einer oder mehreren Stufen abgerechnet werden. Die einzelnen Stufen
sind:
Abschlagabrechnung
Folgeabschlagabrechnung
Finalabrechnung
Im
Einkauf können zu bestehenden Finalabrechnungen gegebenenfalls zu einem späteren
Zeitpunkt noch
Nachvergütungen
erstellt werden.
Dazu
ist es zunächst erforderlich, die betreffenden Belege in einen Beleg der
gewünschten Abrechnungsstufe umzuwandeln. Dieses geschieht durch Aufruf einer
der Funktionen
Abschlag
vorbereiten
F-Abschlag
vorbereiten
Finale vorbereiten
Dabei wird jeweils ein neuer
Beleg erzeugt, der aber die Daten des Ursprungsbelegs enthält. Grundsätzlich
kann ein Beleg nur dann in die nächste Stufe übertragen werden, wenn das
entsprechende Statuskennzeichen
Status Abschlag
Status Folgeabschlag
Status Finale
dieses erlaubt:
ohne
(gibt es nicht bei
Status Finale
):
Abschlag bzw. Folgeabschlag ist nicht vorgesehen, es
kann zur Lieferung nur ein Finalbeleg erzeugt werden.
gesperrt:
Der Beleg
wird für diese Stufe erzeugt, kann aber erst abgerechnet werden, wenn er dafür
per Korrektur freigegeben wird.
freigegeben:
Der
Beleg wird für diese Stufe erzeugt und kann auch ohne Korrektur abgerechnet
werden.
Es
wird dabei immer sichergestellt, dass keine vorgesehene Abrechnungsstufe
ausgelassen wird.
Soll zu einer Lieferung direkt ein Finalbeleg erstellt
werden, so muss das Kennzeichen
Status Abschlag
mit dem Wert
ohne
belegt sein. Entsprechend muss das Kennzeichen
Status Folgeabschlag
mit
dem Wert
ohne
belegt sein, wenn der Folgebeleg zur Abschlagabrechnung der
Finalbeleg sein soll. Folgeabschlag-Belege können nur aus Abschlagbelegen
erzeugt werden.
Ist
die Einstellung des Rohwareparameters
nächste
Stufe nur nach Fibuübertrag
für das Abrechnungsschema des Quellbelegs mit dem We
[...]


---

## Weltmarktpreis

Weltmarktpreis
Der Weltmarktpreis kann, falls benötigt, in
Rohware-Abrechnungen mittels bestimmter Qualitätsdefinition zur
Qualitätsabrechnung herangezogen werden.

---

## Wichtiger Hinweis zur Funktion Schema-/Kundenänderung

Wichtiger Hinweis zur Funktion
Schema-/Kundenänderung
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Bevor Sie diese Funktion zum
Ändern des Abrechnungsschemas oder des Kunden für Rohwarenbelege verwenden,
sollten Sie die Belege unbedingt ins Archiv drucken.
Beim Ausführen dieser
Funktion können
Daten verloren
gehen, da der
Originalrohwarenbeleg storniert und ein neuer Lieferschein erzeugt wird, der
dann in einen Rohwarebeleg gewandelt wird.
Eventuell müssen verloren
gegangene Daten in dem neuen Beleg nachgetragen werden. Kontrollieren Sie
deshalb nach Verwendung dieser Funktion immer die neu erzeugten Belege.
Lesen Sie bitte die
komplette Hilfe zu dieser Funktion durch, bevor Sie sie verwenden.
Wenn
Sie diesen Hinweis beim Öffnen der Maske nicht mehr sehen möchten, dann
verwenden Sie die Funktion Hilfe Hinweis an/aus.

---

## Wichtiger Hinweis zum Wechsel der Rohwarengruppe

Wichtiger Hinweis zum Wechsel der
Rohwarengruppe
Hauptmenü
Rohwarenabrechnung
Rohwarenabrechnung
EK-Rohwarenbearbeitung
Schema-/Kundenänderung
Direktsprung
[RWB]
Vorsicht beim Wechsel der
Rohwarengruppe!!
Wenn
Sie die Rohwarengruppe wechseln, dann kann es zu Problemen bei der Zuordnung der
Analysewerte zu den Qualitäten kommen.
Die Referenznummer 1 kann z.B. in der
einen Gruppe die Feuchte sein in der anderen Gruppe aber der Besatz.
Beim
Verwenden der Funktion Schema-/Kundenänderung werden die Analysewerte anhand der
Referenznummer direkt übertragen. Feuchtewerte könnten beim Wechsel der
Rohwarengruppe dann als Besatzwerte angezeigt werden.
Wechseln Sie die
Rohwarengruppe nur, wenn Sie dieses bewusst in Kauf nehmen wollen !!!
Wenn
Sie diesen Hinweis beim Wechsel der Rohwarengruppe nicht mehr sehen möchten,
dann verwenden Sie die Funktion Hilfe Hinweis RWG an/aus.

---

## Zinsabrechnung Mailversand

Zinsabrechnung Mailversand
Zinsabrechnung können so eingerichtet werden, dass
zusätzlich zum Druck oder anstelle des Drucks per Mail versendet werden können.
Dazu müssen folgen Voraussetzungen gegeben sein:
6)
Der Belegversand Lizenz muss aktiv sein.
7)
Ein
Versandprofil
muss eingerichtet
sein.
8)
In den Stammdaten für
Zinsgruppen
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
-1140, das direkt verwendet werden oder als Vorlage benutzt werden kann. In
diesem Formular stehen alle Felder und Bereiche der „Standard Zinsabrechnung“
zur Verfügung. Zusätzlich existiert ein Bereich „Zinsabrechnung Betreffzeile“,
in dem man die Betreff-Zeile der Mail einrichten kann. Ist kein Formular und
keine Datenbankfunktion eingerichtet, so erscheint als Betreff und als
Mailinhalt lediglich der Text „Zinsabrechnung“.
HINWEIS:
Um Grafiken in das Formular mit einzubinden, kann man den bekannten
HTML-Syntax <img src="cid:XXXXXX" alt="mein bild" /> verwenden. Für XXXXXX
muss die GUID aus dem Formulararchiv, in dem die Grafik hinterlegt sein muss,
angegeben werden.
•
Ist das Versandprofil nicht eingerichtet, wird für alle Personenkonten
mit dieser Zinsgruppe kein Mailversand durchgeführt.
9)
In den Hauptanschriften oder den Ansprechpartnern muss eine Mailadresse für
Zinsabrechnung eingerichtet sein. Dazu wählt man in der Auswalliste Anschriften,
die man z.B. übe
[...]


---

## Zinsabrechnung über Zinsformulare (Formulartyp 203) drucken.

Zinsabrechnung über
Zinsformulare (Formulartyp 203) drucken.
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zinswesen
Zinsabrechnung bearbeiten
Funktion
Abrechnung drucken
Direktsprung
[ZIB]
Es existiert ein Standartformular „Zinsabrechnung“ mit
der Nummer –16. Zu dem Formulartyp 203 existieren folgende Formularbereiche:
•
311      Kopf Zinsabrechnung

Formkopf
•
312      Kopf Zinsabrechnung Fortsetzung
        Folgekopf
•
314      Positionsteil Zinsabrechnung

Zeilentyp
•
605      Textzeile

Zeilentyp
•
315      Zinsabrechnung
Betreffzeile
Mail Betreffzeile
•
316      Fuß
Zinsabrechnung
Fuß
•
313      Abschluss Zinsabrechnung

Abschluss
Da Formulare nur gedruckt werden, muss mindestens ein
Zeilentyp eingerichtet sein. Will man seinem Kunden keine detaillierte
Aufstellung der Bewegungen schicken, dann reicht es einfach nur eine Textzeile
(Bereich 605) einzurichten. Es wird dann nur - zusätzlich zu Kopf und Fuß - eine
leere Zeile gedruckt.
Folgende Variablen sind in allen Teilen (Kopf, Fuß und
Zeilentyp) verfügbar. Formularbereiche, die nicht separat mit aufgeführt werden,
enthalten nur Festtext oder diese Felder!
Bezeichnung
Typ
Nr.
Bedeutung
Zinslistnummer
Numerisch
4
Nummer der Zinsliste
Kontonummer
Numerisch
4
Kontonummer des aktiven
      Kunden
ZinsAbrDatum
Normal
5
Erstellungsdatum des
      Zinsabrechnung
ZinsAbrVonDatum
Normal
5
Bereich von dieser
      Zinsabrechnung
ZinsAbrBisDatum
Normal
5
Bereich bis dieser
      Zinsabrechnung
ZinsAbrDruKennz
Numerisch
4
Wenn
      schon vorher einmal gedruckt dann 1 sonst 0
ZinsAbrSollZins
Numerisch
4
Sollzinsen
ZinsAbrHabenZins
Numerisch
4
HabenZinsen
ZinsAbrZinsSaldo
Numerisch
4
Saldo Soll - Haben
ZinsAbrZinsSaldoSH
Normal
3
Sollhaben des Saldos
ZinsAbrSollZinsOrig
Numerisch
4
Sollzinsen
ZinsAbrHabenZinsOrig
Numerisch
4
HabenZinsen
ZinsAbrZinsSaldoOrig
Numerisch
[...]


---

## Zinsen ändern

Zinsen ändern
Hauptmenü
Mahn-/Zahl-/Zinswesen
Zinswesen
Zinsabrechnung bearbeiten
Variante
Zinsen ändern
Direktsprung
[ZIB]
Es ist möglich, die von Referenz-ERP berechneten Zinsen vor
der Übernahme in die Primanota zu ändern. Dafür steht in der Auswahlliste
„Zinsabrechnung bearbeiten“ die (versteckte) Variante „
Zinsen ändern
“ zur
Verfügung. Dabei können sowohl die Soll- als auch die Habenzinsen verändert
werden.
Diese Zinsen werden in der Zinsabrechnung unter
ZinsAbrSollZins bzw. ZinsAbrHabenZins ausgegeben. Die von Referenz-ERP errechneten
Zinsbeträge können parallel als ZinsAbrSollZinsOrig bzw. ZinsAbrHabenZinsOrig
angedruckt werden. Wurden die Zinsen manuell geändert, ist ein Nachweis über die
einzelnen Positionen natürlich nicht mehr sinnvoll.

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

## Zusatzinfo in Fremdkontrakt

Zusatzinfo in Fremdkontrakt
Fremdkontrakte für Artikel mit Rohwarengruppe
enthalten zusätzliche Felder für die Rohware-Bearbeitung:
Abbuchungsmenge
(brutto/netto)
Finalabrechnungspreis
Abschlagpreis
Mindestpreis
Weltmarktpreis

---

