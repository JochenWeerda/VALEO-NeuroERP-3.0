# Agrar, Feldbuch & Pflanzenbau — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (84 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

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

## Vermehrungsvertrag

Vermehrungsvertrag
Beim Erfassen von Vermehrungsverträgen im Saatgutmodul
wurde die Vertragsnummer nicht korrekt gezogen. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 722654[33694]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: -
Variante: -
Funktion/Report: [SAATV]
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33694, 722654

---

## Artikelabhängige THG Werte in Anbauland / Region

Artikelabhängige THG Werte in Anbauland / Region
In der Anwendung Nachhaltigkeit - THG WERTE, in der
Variante Anbauland / Region wurde die Spalte Gültig-ab-Datum bei den
artikelabhängigen THG-Werten hinzugefügt.
Releasenote Kategorie:
Ticket: 724070[33887]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [NAWER]
Variante: Anbauland / Region
Funktion/Report: F5, F8
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33887, 724070

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

## Geodatendienst Mandantenstamm

Geodatendienst Mandantenstamm
Das neue Kartenmodul in Referenz-ERP arbeitet mit einem
Google-API-Key, der sowohl für die Beschaffung von Geodaten als auch für die
Anzeige der Karte verwendet wird. Da MapQuest zeitgleich seinen kostenlosen
Geodatendienst eingestellt hat, gibt es fortan nur noch einen API-Key von Google
im Mandantenstamm. Die Auswahlmöglichkeit für den Geodatendienst ist
entfallen.
Releasenote Kategorie:
Ticket: 732360[35249]
Version: 9.0.2402.2
Datum: 22.10.2024
Anwendung: Mandantenstamm
Variante: Mandantenstamm
Funktion/Report: Geodaten
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.2, 35249, 732360

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

## Nachhaltigkeit – Anbauland (EPA NHANBAULAND

Nachhaltigkeit –
Anbauland (EPA NHANBAULAND
Bezeichnung
Standardwert
Erklärung
Maximale Einträge bei der die
      Artikelübersicht aktualisiert werden soll
20
Da
      das Aktualisieren der Artikelübersicht etwas Zeit in Anspruch nehmen kann,
      kann mit diesem Parameter eingestellt werden, wie viele Einträge beachtet
      werden sollen.
Bei
      „0“ wird die Übersicht nicht aktualisiert.

---

## Ackerschlagkartei (EPA BTACKERS)

Ackerschlagkartei (EPA BTACKERS)
Bezeichnung
Standardwert
Erklärung
Kundengruppe der Labore
0
Gültigkeit Nährstoffanalyse
      (Monate)
Gültigkeit Schadstoffanalyse
      (Monate)
120
Prüfung der Gehaltsklasse
      (REG)

---

## Feldbearbeitung (EPA BTSCHLAGIMVERTRAG)

Feldbearbeitung (EPA BTSCHLAGIMVERTRAG)
Bezeichnung
Standardwert
Erklärung
Anlage ohne Artikel
      erlaubt
Nein
Anerkennungspartie muss vorhanden
      sein (Kategorie wird vorbelegt)?
Nein
VorgangsKlasse für
      Belegerzeugung.
400
VorgangsUnterKlasse für
      Belegerzeugung.
0

---

## Scandokumente verschlagworten (EPA VERSCHLAGWORTUNG)

Scandokumente verschlagworten (EPA
VERSCHLAGWORTUNG)
Bezeichnung
Standardwert
Erklärung
Ordner der Importdateien
Soll
      automatisch verschlagwortet werden?
Nein

---

## Vorkasse (EPA VORKASSE)

Vorkasse (EPA VORKASSE)
Bezeichnung
Standardwert
Erklärung
Preisaufschlag/Abschlag für die
      Lieferungssorte
0

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

## Variante Partiegruppe bei Saatgut(SPA 245)

Variante Partiegruppe bei Saatgut(SPA 245)

---

## Partiegruppe änderbar bei Saatgut(SPA 252)

Partiegruppe änderbar bei Saatgut(SPA 252)

---

## Zwangs-Partie bei Saatgut-Lieferungen(SPA 267)

Zwangs-Partie bei Saatgut-Lieferungen(SPA 267)

---

## Saatgut-Lizenz (SPA 289)

Saatgut-Lizenz (SPA 289)
Lizenz für Saatgut.

---

## Zu-/Abschlagsgruppe bei manuellen eingebbar(SPA 345)

Zu-/Abschlagsgruppe bei manuellen eingebbar(SPA 345)
Ja: wenn ein manueller Gruppen Zu-/Abschlag erfasst
wird, kann auch die Zu-/Abschlagsgruppe erfasst werden.
Nein: die Zu-/Abschlagsgruppe kann bei manuellen
Gruppen Zu-/Abschlägen nicht verändert werden.

---

## Länge des Schlagnamens bei der Anerkennung(SPA 493)

Länge des Schlagnamens bei der Anerkennung(SPA 493)
Hier kann die Länge der Schlagnummer bei der
Anerkennung eingegeben werden.

---

## Auswahllisten keine NULL-Werte anzeigen(SPA 642)

Auswahllisten keine NULL-Werte anzeigen(SPA 642)
Felder aus Datenbanken ohne Ergebnis (technisch: Der
Wert des Feldes ist nicht besetzt!) werden  bei der Einstellung ‚Ja‘
mit  Punkten oder Leerstellen dargestellt. Bei ‚Nein‘ wird der logische
Ersatzwert  angezeigt (z.B. 0 bei einer Zahl, Leerstellen bei einem
Textfeld).

---

## Ersatzsuche bei F3 Box nach Fehlschlagen Einstiegsvariante(SPA 780)

E
rsatzsuche bei F3 Box nach Fehlschlagen
Einstiegsvariante(SPA 780)
Bei einer gesetzten Einstiegsvariante überprüft
die F3 Box die Eingabe auf dem Maskenfeld mit eben dieser Variante. Ist dieser
SPA auf ‚Ja‘ gestellt, wird auch noch die Hauptvariante zur Überprüfung
herangezogen, wenn die Einstiegvariante keinen Treffer findet.  Diese
Vorgehensweise ist etwas flexibler, da man sowohl  in einer
textorientierten Suche (z.B. In  den Bezeichnungen) als auch in der
numerischen Variante  suchen kann.

---

## Geodaten-Lizenz(SPA 856)

Geodaten-Lizenz(SPA 856)
Lizenz für die Geodaten.

---

## Kartoffelvermehrung (SPA 954)

Kartoffel
vermehrung (SPA 954)
In dem Vermehrungsmodul gibt es zwei verschiedene
Ausprägungen. Der Getreidebereich unterscheidet sich vom Kartoffelbereich in der
Darstellung der Sorten wie auch in der behandlung der

---

## Abschreibung

Abschreibung
Hauptmenü
Anlagenbuchhaltung
Anlagenbuchhaltung
AfA-Vorschlag erstellen
Direktsprung
[ANKAV]
Abschreibungen werden in einem Stapellauf erstellt und
zuerst in eine vorläufige Liste gestellt. Diese Vorschläge können dann in der
Anwendung „AfA-Vorschlag bearbeiten“ (Direktsprung
[ANKAB]
) kontrolliert und geändert werden,
bevor man sie endgültig freigibt.
Beim Errechnen der Abschreibung gibt es eine
Besonderheit bei nachträglichen Anschaffungs- und Herstellungskosten (Zugängen
bzw. Teilabgängen). Die sich aus diesen ergebende neue Bemessungsgrundlage wird
auf die Restnutzungsdauer verteilt, d.h. die Abschreibung wird anteilig mit der
alten Bemessungsgrundlage bis zum Zu- bzw. Teilabgang errechnet. Es gibt jedoch
auch die Möglichkeit aus Vereinfachungsgründen diese Kosten so zu
berücksichtigen, als seien sie zu Beginn des Jahres entstanden (R 7.4 Abs. 9
Satz3 EStR). Dies lässt sich durch die Option „Vereinfachungsregel bei Zu- und
Abgängen anwenden“ im
Firmenstamm
einstellen.
Bevor man die Vorschläge erstellt, werden folgende
Daten abgefragt:
Bedeutung
Bereich
Da
      im Zuge von BilMoG eine Trennung nach Handels- und Steuerrecht möglich
      ist, kann man auch die Abschreibungsvorschläge getrennt
      erstellen.
Stichtag
Er
      wird mit dem aktuellen Tagesdatum vorbelegt und beim Buchen der
      Abschreibung als Belegdatum herangezogen.
Bis
      Periode/Jahr
Die
      Werte werden an Hand des Stichtages vorbelegt. Sie dienen zur Abgrenzung
      des Abschreibungsintervalls. Stichtag, Periode und Jahr werden in die
      Anlagenposition übernommen. Es wird daher geprüft, ob das Datum innerhalb
      der Periode liegt und ggf. die Hinweismeldung
„Das
      Datum 26.03.2008 und die Periode 2/2008 passen nicht
      zusammen!“
ausgegeben.
Bezeichnung
Dieser Text dient zur
      Identifikation. Er wird später beim Buchen des Vorschlags als Text in das
      Protokoll der Veränderungen des Anlagegutes übernommen.
Inventarnummer
G
[...]


---

## Ackerschlagkartei

Ackerschlagkartei
Hauptmenü
Saatzucht
Saatgutstammdaten
Direktsprung
[ACKER]
In diesem Stammdatenpfleger werden die Daten für
Felder/Schläge gepflegt.
Die Dokumentation von schlagbezogenen Maßnahmen ist
zur Pflicht gemacht worden. Unter anderen durch die EU-Verordnung 178/2002 ist
in der gesamten EU die Rückverfolgbarkeit von Lebens- und Futtermitteln sicher
zu stellen, dies wird auch entsprechend kontrolliert.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
Landwirt
Hier
      wird der Landwirt dieses Schlages eingetragen anhand seiner Kundennummer.
      Mit der Taste
F3
kann hier eine
      Auswahl aufgerufen werden.
Schlag
Hier
      wird die Schlagnummer eingetragen und die Bezeichnung des
      Schlages.
ha
      gesamt
Die
      Gesamtfläche dieses Schlages in Hektar.
ha
      genutzt
Die
      genutzte Fläche dieses Schlages in Hektar.
Lagerzuordnung
Die
      Lagernummer.
Bemerkung
Bemerkung Zu Dieses
      Schlag.
Adresse
Adress-Informationen.
FLIK
Der
      Flächenidentifikator dieses Schlages.
Flurstücke (Grid)
Bodenart
Die
      Bodenart kann hier gepflegt werden.
Humus
Der
      Humuswert dieses Schlages kann hier eingetragen werden.
Mit der
      Taste
F3
kann hier eine
      Auswahl (
AF_HUMUS
) aufgerufen
      werden.
Boden
Mit
      der Taste
F3
kann hier eine
      Auswahl (
AF_BODEN
) aufgerufen
      werden
.
Bodentyp
Die
      Eigenart des Bodens kann hier gepflegt werden. Mit der
      Taste
F3
kann hier eine
      Auswahl (
AF_BODENTYP
) aufgerufen
      werden
.
Nutzung
Die
      Schlagnutzung kann hier gepflegt werden. Mit der Taste
F3
kann hier eine
      Auswahl (AF_ACKERNU) aufgerufen werden
.
Tongehalt
Der
      Tongehalt dieses Schlages.
pH
      Wert (ist)
pH-Wert IST
dieses
      Schlages.
pH
      Wert (Ziel)
pH-Wert SOLL
dieses
      Schlages.
Kalkempf.
Kalkempfehlung
      für diesen Schlag.
Labor
Die
      Labornummer.
Analyse
Die

[...]


---

## Registerkarten in Anschriften

Registerkarten in Anschriften

---

## Anzahlungen

Anzahlungen
Anzahlungen oder Abschlagszahlungen werden im
Allgemeinen auf einem Konto „geleistete Anzahlungen und Anlagen im Bau“ geführt.
Nach Fertigstellung der Anlage werden dann die geleisteten Anzahlungen auf ein
entsprechendes Anlagenkonto umgebucht. Sind für diese “Anlage im Bau“ mehrere
Datensätze im Anlagenstamm erfasst worden, so will man natürlich diese trotzdem
zu einem Anlagegut zusammenfassen. Dafür existiert in der Anwendung
„Anlagenstamm“ in der Variante „Anlagenkartei“ die Funktion
Umbuchen
. Man
markiert ein oder mehrere Anlagegüter, die man zusammenfassen möchte.
Anschließend führt man die Funktion
Umbuchen
aus. Es öffnet sich die eine
Maske, in der einige Werte abgefragt werden.
Anschließend öffnet sich sofort die Maske des „neuen“
Anlagegutes, in der man dann ggf. die fehlenden Werte nachtragen bzw. die
vorbelegten Werte ändern kann. Vorbelegt werden diese Werte immer mit den Werten
des zuerst markierten Datensatzes. In der Historie sind alle Anlagegüter als
AHK-Umbuchung wiederzufinden, aus denen sich diese Umbuchung zusammensetzt.

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

## Anerkennung der Partien

Anerkennung der Partien
Hauptmenü
Saatzucht
Saatgutabwicklung
Aufbereitung
Direktsprung
[AUFBE]
Innerhalb des Abschnittes Aufbereitung lassen sich Partien,
die aus fertiger Saatware entstanden sind, per EDV Unterstützung in ein
Anerkennungsverfahren integrieren.
Das Anerkennungsverfahren bereitet die Datensätze so weit
vor, dass eine Antragstellung per Report vorgenommen werden kann.
Hierbei wird berücksichtig dass:
-
Die angelieferte Menge zwar mengenseitig genau gemeldet wird, aber nicht
schlagseitig.
-
Die Anerkennungspartie eine andere Kategorie besitzen kann, als die ehemals im
Vertrag festgelegte Partie
-
Dass die Anerkennungspartie auch aus überjähriger Ware bestehen kann, also ein
Schlag auch Jahresbezogen mehrfach vorkommen kann
-
dass Einmischpartien, die bereits an, wie auch aberkannt worden sind, wieder mit
ihrer Menge in diese Anerkennungspartie fließen kann.
Die Abarbeitung erfolgt mittels der entsprechenden
Maske.

---

## Bearbeitungsmaske Registerkarten

Bearbeitungsmaske Registerkarten
Im unteren Bereich finden Sie 6 Registerkarten.

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
Danach wird auf der Registerkarte Main, das neu angelegte Profil ausgewählt. Mit
dem OK Button oben rechts, wird diese Einstellung gespeichert und die Maske wird
verlassen. Mit einem erneuten öffnen der des Programmes, kann auf der
Registerkarte Status überprüft werden, ob sich der Scanner in das WLAN Netz
verbinden konnte. Neben dem Text IP sollte nun eine IP Adresse angezeigt
werden.
Manuelle Anlage
eines WLAN Profils
1.
Auswählen der Registerkarte Profil
2.
Drücken des Buttons „NEW“.
3.
Jetzt muss der Profilname eingegeben werden und mit OK Bestätigen. Diesen Namen
finden Sie dann auf dem Startbildschirm.
4.
Wählen Sie jetzt bitte auf der linken Seite den Punkt SSID aus und tragen Sie
bitte im rechten Eingabefeld den eindeutigen Namen des WLAN ein, mit dem sich
der Scanner verbinden soll. Hierbei achten Sie bitte auf Groß- und
Kleinschreibung.
5.
Als Encryption wählen Sie bitte die von Ihnen gewählte Verschlüsselungsmethode
der Access Points aus. Durch das Drücken des Buttons  WEP Keys/PSKs
[...]


---

## Einrichtung Datalogic Memor X3

Einrichtung Datalogic Memor X3
Einrichten des
WLAN Moduls
Das WLAN Modul wird mit SCU eingerichtet, dies ist an
dieser
Stelle
beschreiben
worden.
Setzen der
Hintergrundbeleuchtung
Windowssymbol
Settings
Control Panel
Display
Auf der Registerkarte Backlight muss der Schalter
„Turn of backlight when using“
1.
Battery Power auf “5 minutes” gestellt werden.
2.
External Power auf „10 minutes“ gestellt werden.
Power
Einstellungen
Windowssymbol
Settings
Control Panel
Power
Mit dieser Funktion kann eingestellt werden, wann der
Scanner sich nach einer bestimmten Zeit bei Nichtgebrauch abschaltet. Die
Empfehlung ist das automatische Abschalten komplett zu Verhindern.
Dazu wird auf der Registerkarte Auto-Off unter dem
Punkt
1.
„When battery powerd“ die Einstellung „never“ gewählt.
2.
„When externally power“ kann die Einstellung 5 minutes gewählt werden, da der
Scanner meistens sich zum Aufladen an der Steckdose sich befindet.
Datum/Zeit
Einstellung
Windowssymbol
Settings
Control Panel
Date/Time
Hier kann das aktuelle Datum eingestellt werden. Dies
ist wichtig bei der Offline Variante, da auch von dem Datum abhängige
Einstellungen gelesen werden z.B. Steuerparameter
Ausstellen des
Scannermodules, da die Referenz-ERP Software das Scannermodul selbst startet ab
Version 8.0.1.xxx
Klicken auf das Grau oder Gün hinterlegte Barcode
Symbol auf der Taskleiste. Das Häkchen vor dem Punkt „Wedge“ entfernen durch das
klicken auf den Text „Wedge“. Das Symbol sollte jetzt Grau hinterlegt worden
sein.
Einstellung des
Scannermoduls
Windowssymbol
Settings
Control Panel
Decoding
Configure
Oder
Klicken auf das Grau oder Gün hinterlegte Barcode
Symbol auf der Taskleiste.
Configure
Es erscheint jetzt folgende Anzeige.
Parameter
Value
Reader
      Parameter
..
Scan
      Parameter
..
Mit einem Doppelklick auf den Parameter oder auf die
Value wird das jeweilige Untermenü geöffnet.
Sind alle Einstellungen vorgenommen worden wird über
File
Save die Einstellungen
gespeiche
[...]


---

## Eigenschaften

Eigenschaften
Diese Funktionssammlung ist noch in der Entwicklung
und darf vom Anwender selbst eingestellt werden. Im Tabreiter System-Grid
Eigenschaften sind jedoch Vorbelegungen als Vorschlag des Entwicklers
eingetragen.
Felder
Zeilen Trennstriche
Zeigt zwischen den Zeilen einen
      Strich.
Spalten Trennstriche
Zeigt zwischen den Spalten einen
      Strich.
Zeilen Nummer
Diese Funktion bewirkt die Anzeige
      einer extra-Spalte mit fortlaufender Nummer.
Laufbalken anzeigen
Zeigt das Grid mit einem Laufbalken
      an.

---

## Einrichtung der Bereichsauswahl

Einrichtung der Bereichsauswahl
Bei der Einrichtung einer privaten Variante wird auch
der Bereich privatisiert. Man erreicht die Bearbeitung des Bereichs über das
Darstellungsregister
Private
Variante
Strg+F2
Bearbeiten
F5
Zugehöriger Bereich
F5
Es öffnet sich folgende Maske:
Spalte
Bedeutung
Label
Der
      in dieser Spalte eingegebene Text erscheint in der Bereichsauswahl als
      Beschreibung der Zeile.
Typ
Wie
      erfolgt die Abfrage. Dabei können folgende Werte mit F3 ausgewählt
      werden:
Typ
von..bis..
Rechts vom Label werden zwei
            Werte abgefragt, die im SQL-Ausdruck (siehe unten) als PAR1 und PAR2
            verwendet werden können.
gleich
Es wird nur ein Wert
            abgefragt
ungleich
s.o.
like..
s.o.
kleiner
s.o.
größer
s.o.
<=
s.o.
>=
s.o.
in..
s.o.
not in..
s.o.
clause
s.o.
zwei Parameter
Rechts vom Label werden zwei
            Werte abgefragt.
FSFormat
Wird FSFormat ausgewählt, so
            muss in der Spalte FSFormat ein Format ausgewählt werden. In
PAR1
bzw.
VON[idx]
wird der Wert des FS-Formates
            zurückgegeben.
toggle
Ähnlich wie das FSFormat. D.h.
            es muss in der Spalte unter FSFormat etwas eingetragen werden. In
PAR1
bzw.
VON[idx]
wird das zurückgegeben, was im
            FSFORMAT in der Spalte Kommentar/Schnipsel eingetragen
            wurde.
toggle mit
            Parameter
Rechts vom Label werden zwei
            Werte abgefragt. Die Arbeitsweise ist wie
Toggle
, nur kann
            zusätzlich ein weiterer Wert abgefragt werden.
Die
      Formate
gleich, ungleich, like, kleiner, größer, <=, >=, in, not
      in  clause
haben nur noch die Bedeutung, dass nur ein Parameter
      abgefragt wird.
FSFormat
Hier
      wird das zu toggle, toggle with param und FSFormat gehörende Format
      eingetragen. Eine Auswahl ist mit F3 möglich.
Von
Wert, der beim ersten Betreten der
      Bereichsauswahl bzw. nach dem Löschen des Profils im ersten Eingabefeld
      steht.
Hier

[...]


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

## Flächenidentifikator (FLIK)

Flächenidentifikator (FLIK)
Der Flächenidentifikator (FLIK) wird ab dem Jahr 2005
bundesweit eingeführt und wird in Rheinland-Pfalz jeweils für das Flurstück
vergeben. Dies bedeutet, dass der FLIK für alle rheinland-pfälzischen Flächen
bekannt ist und für die Antragsteller ausschließlich nachrichtlichen Charakter
besitzt.
Wenn der Antragsteller aber Flächen in anderen
Bundesländern hat muss er einiges beachten: In den meisten anderen Bundesländern
wird der FLIK nicht auf der Grundlage des Flurstücks gebildet, sondern auf der
Grundlage von Feldblöcken oder anderen Referenzsystemen. Deswegen muss sich der
Antragsteller für jede Nutzung in anderen Bundesländern zusätzlich zu den
Katasterangaben bei der dort zuständigen Behörde den jeweiligen FLIK des Schlags
oder ggf. des Flurstücks (in Abhängigkeit des im jeweiligen Bundesland
eingeführten Referenzsystems) besorgen. Der FLIK besteht aus einer 16-stelligen
Zeichenfolge. Der jeweilige FLIK ist in der Flächennachweis-Agrarförderung 2005
für alle Flächen anzugeben. Hierbei kann es vorkommen, dass für Flächen in
anderen Bundesländern, die mit so genannten Feldblöcken oder anderen
Referenzsystemen arbeiten, für alle Flurstücke eines Schlags der gleiche FLIK
angegeben werden muss. Besonderheiten gibt es auch hinsichtlich der
Landschaftselemente zu beachten, die ja seit 1.1.2005 zur beihilfefähigen Fläche
gehören, wenn Sie Teil dieser sind. Nach Auskunft des rheinland-pfälzischen
Landwirtschaftsministeriums brauchen rheinland-pfälzische Landwirte aufgrund des
GIS- Referenzsystems (Kataster) keine gesonderte Erfassung der
Landschaftselemente vor zu nehmen, da sich die Landschaftselemente auf dem
Flurstück befinden. In Rheinland-Pfalz müssen die Landwirte im
Agrarförderantrag, der bis 17.5.2005 zu stellen ist, ''nur'' angeben, ob die
Landschaftselemente (differenziert nach CC-relevant und sonstige) auf der Fläche
sind und wie hoch der Gesamtumfang ist! Alle übrigen Bundesländer (bis auf
Baden-Württembe
[...]


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
      bei Änderungen am Abgrenzungsdatum des Artikels eine entsprechende Meldung
      auf dem Bildschirm aus.
Datum der Verfügbarkeit
      übernehmen
Dieses Feld ist nur bei „Angebot“,
      „Auftrag“, „Bestellanfrage“ und „Bestellung“ eingebbar. Hier wird
      festgelegt, ob nach einer Änderung des Plandatums in der Warenposition das
      neue Datum auch im Vorgangskopf übernommen werden soll:
•
Nur in der
      Warenposition ändern
•
Auch im Vorgang
      setzen
•
Nur Im Vorgang
      setzen, wenn das neue Datum größer ist
Liefernummer auf Position
      nachtragen
Hier
      kann festgelegt werden, ob in Abhängigkeit von der Einstellung des
      Steuerparameters
826 -
      Liefernummer auf Position eingeben
eine
Erfassung von Lieferscheinnummern auf der
      Warenpositionsmaske
zulässig sein soll.
Diese Einstellung ist erst ab Stufe
      Rechnung / Eingangsrechnung verfügbar.
Kontraktanzeige in
      Warenmaske
Die
      Information zu Kontrakten wird angezeigt
•
Nur wenn
[...]


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

## (Individuelle) Zu-/Abschläge

(Individuelle) Zu-/Abschläge
Allgemeine Hinweise zum Aufruf und zur Arbeitsweise
des Moduls sind
hier
zu finden.
Spalte
Erklärung
Rang
Sortierung bei mehreren
      Zu-/Abschlägen. Wird dieser rausgenommen, kann der Zu-/Abschlag entfernt
      werden.
Art
Art
      des Zu-/Abschlags
Zu/Ab-Tabelle
Nummer der Zu-/Abschlagstabelle in
      Abhängigkeit von der Art. In dieser sind die eigentlichen Zu-/Abschläge
      zeitbezogen (und evtl. mengenbezogen) hinterlegt.
Zu/Ab-Bezeichnung
Bezeichnung der
      Zu-/Abschlagstabelle
Text-Nr.
Text
      der beispielsweise im Formular eingerichtet werden kann.
Text
Text, der zur Text-Nr. hinterlegt
      ist. Wenn ein Text mit einem * versehen ist, ist dieser nicht in der
      Hauptsprache eingerichtet.
Preisfaktor
Menge auf die sich der Zu-/Abschlag
      bezieht. Nicht bei %-Zu-/Abschlägen relevant.
EKZ-Nr.
      (Erlöskennziffer)
Nummer der Erlöskennziffer beim
      Ziehen des Zu-/Abschlags. Wenn eine 0 eingetragen wird, wird die
      Erlöskennziffer des Artikels gezogen.
EKZ-Bezeichnung
Bezeichnung der ausgewählten
      EKZ-Nummer
InZl. (In Zeile)
Kennzeichen, ob der Zu-/Abschlag in
      der Artikelzeile oder als eigene Zeile erzeugt werden soll.
GrpR
      (Gruppenrabatt)
Kennzeichen, ob es sich hierbei um
      einen Gruppenrabatt handelt.
kalk.
      (Kalkulationskennzeichen)
Kennzeichen, ob es sich um einen
      kalkulatorischen Zu-/Abschlag handelt, ob dieser also direkt im Preis
      enthalten ist.
Sp.
      (Sperrkennzeichen)
Möglichkeit der (vorübergehenden)
      Sperrung des Zu-/Abschlags.
Schlüssel
Steuerschlüssel, hinterlegt im
      Zu-/Abschlagssatz. Wenn eine 0 eingetragen wird, wird der Steuerschlüssel
      der Warenposition gezogen). Sichtbar in Abhängigkeit von Steuerparameter
      330 („Separate Steuer auf Zu-/Abschl. möglich“)
Schlüssel-Bezeichnung
Bezeichnung des Steuerschlüssels.
      Sichtbar in Abhängigkeit von Steuerparameter 330 („Separate Steuer auf
      Zu-/A
[...]


---

## Kassensystemverwaltung (Hardware)

Kassensystemverwaltung (Hardware)
Jeder logischen Kasse ist ein Kassensystem zugeordnet.
Dieses Kassensystem beschreibt die Hardwareeinheit.
Durch diese Trennung ist es möglich eine komplette
Hardwareeinheit (Kassensystem) mit ihrer hardwarespezifischen Einrichtung
auszutauschen und an einem definierten Arbeitsplatz (logische Kasse) mit seinen
Regeln und Spezifikationen einzusetzen.
Kassensystem-Kopfdaten
Kassensystemnummer
Nummer des
      Hardware-Systems
Bezeichnung
Bezeichnung des
      Kassensystems
Anlagedatum
Anzeige des Datums der Anlage dieses
      Kassensystems
Änderung am
Anzeige des Datums der letzten
      Änderung
Kassensystem-Drucker
Rechnungsdrucker
Drucker, auf dem Rechnungsbelege
      (keine Bons) gedruckt werden.
Kassensystem-Schublade.
Bezeichnung
      Schubladentyp
Anschlusstyp
Eine
      Schublade kann am Drucker angeschlossen werden.
Anschluss ist
•
Port
z.B.
      COM1 oder LPT1
•
Verbindungsparameter
z.B.
      9600,n,8,1 (Baud, Parity, Data-, Stopbits)
•
Puffergröße
      Eingang
Ist
      1024
•
Puffergröße
      Ausgang
Ist
      1024
Druckertyp (enth.
      Steuerseq)
•
Typ
Normal oder Win7/2008
•
Druckertyp
Druckertyp aus den Druckertypen, die
      mit dem Direktsprung [DRT] gepflegt werden.
•
Druckertyp-Bezeichnung
Anzeige der Bezeichnung des
      Druckertyps
Steuersequenz
Hier
      wird, wenn vorhanden eine Steuersequenz zu diesem Druckertyp angezeigt.
      Ist noch keine Steuersequenz zu dem Druckertyp hinterlegt, an dem Sie die
      Schublade anschließen wollen, so muss diese hier eingetragen werden. Diese
      gilt dann für alle Kassensysteme, die für den Anschluss der Schublade
      diesen Druckertyp verwenden.
Kassensystem-Display
Anzeige auf einem zweizeiligen
      Kundendisplay
Displaytyp
Texteintrag um welches Kassendisplay
      es sich handelt
Steuersequenz
Das
      Display verfügt typerweise über 20 Zeichen pro Zeile. Eine längere
      Zeichenkette würde in der 2. Zeile fortgesetzt,
[...]


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
      eingerichtet werden können
Kass
enstamminformationen Kopfdaten
Kassennummer
Nummer der Kasse (des
      Kassenstandorts)
Bezeichnung
Bezeichnung der Kasse
Anlagedatum
Ebendies
Anmeldedatum
Ebendies
Registerkarte Allgemein
Hauptkasse
Gibt
      an, ob diese Kasse die Hauptkasse ist.
Kassensystem
Kassensystem
      (Hardware-Typ)
Hauptkassennr
Nummer der Hauptkasse
Sitzungsnummer
Anzeige der Nummer
      Kassensitzung
Belegnummer
Anzeige der Nummer des aktuellen
      Kassenbeleges
Kassenkonto FiBu
FiBu-Konto der Kasse
Ver
      konto FiBu
FiBu-Konto Verrechnungen
Nummer Hausbank
Angabe der Hausbank
Akt.
      Bediener
Anzeige aktueller
      Bediener
Wechselgeld
Anzeige Wechselgeldmenge
Vorlage
Einstellungen der Kasse aus den
      Kasseneinstellungen
TSE-ID
Die
      Id der
TSE
Kassenseriennummer
Eine
      vom Hersteller (Branchen-ERP) vergebene Seriennummer der Kasse.
Dieses Feld ist nur editierbar,
      solange noch keine Seriennummer zu dieser Kasse zugewiesen wurde. Die
      Kassenseriennumme
[...]


---

## Kassensicherungsverordnung

Kassensicherungsverordnung
Hauptmenü
Barvorgänge
Stammdaten
Kassensicherungsverordnung Einrichtung
Die Kassensicherungsverordnung in eine Verordnung des
Finanzministeriums, die neue Standards zur Verhinderung von Manipulationen an
Registrierkassen verbindlich vorschreibt. Die KassenSichV vom 26.9.2017 basiert
auf dem Gesetz zum Schutz vor Manipulationen an digitalen Grundaufzeichnungen
vom 16.12.2016. Dieses Gesetz wird auch Kassengesetz oder KassenG genannt.
Ab dem 1.1.2020 müssen in Deutschland
Registrierkassen, deren Bauart es technisch zulässt, mit einer sogenannten
technischen Sicherheitseinrichtung (TSE) ausgestattet sein. Die
Sicherheitseinrichtung speichert die Transaktionen der Kasse auf ihrem internen
Speicher und liefert einen Code zurück an die Kasse. Dieser Code ist auf jeden
Verkaufsbeleg zu drucken. Die Daten werden in einem unveränderbaren Protokoll
gespeichert, das für das Finanzamt exportierbar sein muss.
Für die Erstinbetriebnahme führen wir Sie Schritt für
Schritt durch die Inbetriebnahme:
Erstinbetriebnahme
Wenn Sie einen TSE-Stick austauschen möchten, befolgen
Sie die Schritt-für-Schritt Anleitung für den Austausch:
TSE-Austausch

---

## Zu/Abschläge

Zu/Abschläge
Auf dieser Registerkarte werden die Einstellungen für
die Rabatt-, Fracht- und Zu-Abschlagsgruppen vorgenommen. Hier kann eingestellt
werden, ob die Gruppen des Artikels oder die des Kontraktes verwendet werden
sollen. Des Weiteren besteht die Möglichkeit auch das Verhalten zu steuern, ob
individuelle Gruppen gezogen werden dürfen.
Kontrakt-Zu-Abschlagsgruppen
Hier kann eingestellt werden, ob Zu-Abschlagsgruppen
bei diesem Kontrakt gezogen werden dürfen.
Artikel Zu-Abschlagsgruppe
      verwenden
Ja
Bei
      dieser Einstellung wird, die am Artikel hinterlegte, Zu-Abschlags bzw. die
      am Artikel hinterlegt individuelle Zu-Abschlagsgruppe gezogen
Nein
Bei
      dieser Einstellung wird nicht die am Artikel hinterlegte
      Zu-Abschlagsgruppe verwendet. Es wird die Zu-Abschlagsgruppe aus dem
      Kontrakt gezogen
Steht die Einstellung Artikel Zu-Abschlagsgruppe
verwenden auf Nein und es wurde keine Zu-Abschlagsgruppe ausgewählt, so wird
keine Zu-Abschlagsgruppe gezogen. Dies gilt auch für eine am Artikel hinterlegte
individuelle Zu-Abschlagsgruppe
Wird eine Zu-/Abschlagsgruppe am Kontrakt eingestellt,
so besteht die Möglichkeit noch das Verhalten für die individuellen
Zu-/Abschläge zu steuern.
Indiv. Zu-Abschl.
      verwenden
wie
      SPA
Bei
      dieser Einstellung wird die Einstellung aus dem
Steuerparameter 1160
gezogen. Hier kann dann
      global eingestellt werden, ob individuelle Zu-Abschläge verwendet werden
      sollen.
Ja
Bei
      dieser Einstellung werden die individuellen Zu-Abschläge aus dem Artikel
      gezogen, obwohl ein Zu-Abschlagsgruppe am Kontrakt hinterlegt worden
      ist.
Nein
Es
      wird keine individuelle Zu-Abschlagsgruppe verwendet.
Kontrakt-Frachtgruppen
Hier kann eingestellt werden, ob Frachtgruppen beim
Kontrakt gezogen werden dürfen.
Artikelfrachtgruppen
      verwenden
Ja
Bei
      dieser Einstellung wird, die am Artikel hinterlegte, Fracht bzw. die am
      Artikel hinterlegt indi
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

## Saatsorten

Saatsorten
Hauptmenü
Saatzucht
Saatgutstammdaten
Saatsorten
Direktsprung
[SAATS]
In diesem Stammdatenpfleger werden die Daten über
Saatsorten gepflegt, diese werden einer Fruchtart zugeordnet. Es ist möglich
mehrere Saatsorten einer Fruchtart zuzuordnen.
Erfassungsmaske
Es stehen folgende Eingabefelder und
Eingabemöglichkeiten zur Verfügung.
Name
Bedeutung
BSS-Fruchtartnummer
Hier
      wird die Identifikationsnummer der Fruchtart
      eingetragen.
Mit der Taste
F3
kann hier eine
      Auswahl aus den
Fruchtarten
abgerufen
      werden.
Sortennummer
.
Hier
      wird die Sortennummer eingetragen. Die Sortennummer ist die numerische
      Identifikationsnummer der Saatsorte.
Sortencode
Hier
      wird der Kennzeichnungscode der Saatsorte eingetragen.
Sortenname
Der
      Sortenname enthält die namentliche Bezeichnung für diese
      Saatsorte.
Sortentyp
Der
      Sortentyp wird über das Anwenderformat AF_SORTENTYP gepflegt. Eine Auswahl
      ist mit
F3
möglich.
Zu
      erwartender Ertrag
Ernteschätzung. In der
Feldbearbeitung
wird dieser
      Wert bei Angabe der Saatsorte als Vorbelegung verwendet.
Archiv-Referenz
Formulararchiv Belegreferenz für das
      Archiv.
Bemerkung
Das
      Bemerkungsfeld für die Saatsorte.
Felder auf der Registerkarte Allgemein
Das Register Allgemein enthält mindestens das Land.
Weitere Spalten können individuell in der Anwendung „Griddefinitionen pflegen“
(Direktsprung [GDS]) unter dem Namen „SortenAnmeldedaten_Laender“ eingerichtet
werden.
Der Doppelklick auf die markierte Zeile öffnet einen
weiteren Dialog, in dem alle Informationen, die auch auf der Registerkarte
Allgemein eingerichtet werden können, eingegeben werden können. Hier werden die
für das jeweilige Land zutreffenden Daten eingepflegt
Name
Bedeutung
Ländercode
Der
      Ländercode oder die Landkennung zB. DE für Deutschland oder HU für Ungarn.
      Mit der Taste
F3
kann hier eine
      Auswahl aufgerufen werden.
Sortencode /Sortenname
Anzeige d
[...]


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

## Sonder-AfA

Sonder-AfA
Um für ein Anlagegut Sonder-AfA errechnen zu lassen,
muss man im Anlagenstamm bei Sonder-AfA eine vorher in den
Stammdaten
definierte hinterlegen.
Bei der Erstellung der ersten AfA-Vorschläge wird diese dann errechnet und mit
vorgeschlagen. Nach Beendigung des Begünstigungszeitraums wird dann auf
Restwert-AfA umgestellt. Das folgende Beispiel zeigt ein Anlagegut, welches am
01.Oktober 2000 angeschafft wurde. Nutzungsdauer 8 Jahre, Sonder-AfA 20%
Die Sonder-AfA wird sofort errechnet. Anschließend
wird die Anteilige AfA für das Jahr 2000 ermittelt. Die folgenden vier Jahre
wird die Sonder-AfA bei der Berechnung der Bemessungsgrundlage nicht
berücksichtigt. Nach Beendigung des Begünstigungszeitraums wird dann auf
Restwert-AfA umgeschaltet.
Die Sonder-AfA erscheint im Anlagenspiegel als Summe
zusammen mit der normalen Abschreibung.

---

## Nachhaltigkeit

Nachhaltigkeit
Auf der Registerkarte „Nachhaltigkeit“ stehen die
Informationen der
Nachhaltigkeit
zu der aktuellen
Warenposition.
Feld
Beschreibung
Status
Status der
      Nachhaltigkeit
Herkunft des Status
Herkunft des
      Nachhaltigkeitsstatus
Anbauland
Anbauland der
      Nachhaltigkeit
Herkunft des Anbaulandes
Herkunft des Anbaulandes
Anbau THG
Wert
      des Anbau THGs
Lieferung THG
Wert
      des Lieferung THGs
Verarbeitung THG
Wert
      des Verarbeitung THGs
Herkunft der THG Werte
Herkunft der THG Werte
Zertifikat ID
Identifikation des
      Zertifikats
Zertifikattyp
Typ
      des Zertifikats
Zertifikat
Beschreibung des
      Zertifikats
Herkunft des Zertifikats
Herkunft des Zertifikats
Nachhaltiger Bestand
Zeige nach Klick auf dem Infobutton
      den nachhaltigen Bestand. Dieser Wert hat aber nur informatorischen
      Charakter und kann nicht der exakte Wert sein, da zum Beispiel bei der
      Neuerfassung der neuerfasste Beleg noch nicht gespeichert wurde und somit
      nicht bestandswirksam wurde
Die Vorbelegung des Status wird immer mit "Nicht
Nachhaltig" vorbelegt, wenn der Kunde kein gültiges Nachhaltigkeitszertifikat
für den Artikel besitzt.
Wenn der Kunde kein gültiges Nachhaltigkeitszertifikat
für einen Artikel besitzt und ein Kontrakt mit dem Kunden und Artikel existiert,
der als „Nachhaltig“ angelegt wurde, so wird dieses automatisch abgewählt.
Manuell können die Werte auf dem Tabreiter
Nachhaltigkeit gesetzt werden.
Über die Funktionen „Abwicklung -> Nachhaltigkeit
initialisieren“ lassen sich alle Werte erneut initialisieren.
Über die Funktion „Abwicklung -> Nachhaltigkeit
löschen“ lässt sich der komplette Nachhaltigkeitseintrag löschen.

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
Waagenprofil-Hersteller erkennen auch noch eine Datumsangabe. Nun gilt es diese
Rückgabe in Ihre Bestandteile zu „zerlegen“.
Im Falle der Waagenprofile geschieht das mit regulären
Ausdrücken. Dieses System wurde gewählt, um größtmöglichste Einfachheit und
zugleich Flexibilität bei der Formulierung der Abhängigkeiten zu erreichen.
Regulärer
Ausdruck
Was ist ein
„Regulärer Ausdruck“?
Reguläre Ausdrücke sind Ausdrücke, die nach bestimmten
Regeln (die man im Falle der Waagenprofile nicht alle kennen muss!)
zusammengesetzt sind und die durch Ihre Interpretation Muster abdecken.
Es seien einige exemplarische Erläuterungen
gemacht:
„Aeins32“ ist ein regulärer Ausdruck, er trifft zum
Beispiel auf die  Zeichenketten „Aeins32“, „Aeins32.exe“ zu. Man sieht,
dass „Enthaltensein“ schon ein gutes Kriterium ist. Allerdings benötigt man in
der Praxis noch etwas mehr… Will man z.B. eine beliebige Ziffer beschreiben,
dann muss man wissen, dass das mit dem „Metazeichen“ \d geht. Dem zur Folge wäre
„Aeins\d\d“ auch ein regulärer Ausdruck, der die Zeichenket
[...]


---

## Zertifikate

Zertifikate
Auf der Registerkarte „Zertifikate“ befinden sich
folgende Bereiche.
Zertifikate
Nachhaltigkeit
Die
Nachhaltigkeit
ist mit den Zertifikaten
verknüpft. Das bedeutet zu einem Zertifikat können mehrere Nachhaltigkeiten
gepflegt werden.
Dadurch lassen sich die Nachhaltigkeiten nach Jahren
trennen. Für jedes Jahr werden Zertifikate und die dazugehörigen
Nachhaltigkeitswerte eingetragen.
Zudem ist es möglich mehr als ein Zertifikat pro Jahr
zu haben. Dadurch hat man die Möglichkeit zwei Zertifikate für unterschiedliche
Artikel anzulegen oder zwei Zertifikate (z.B. eins für DE und eins für EU) mit
demselben Artikel.
Zertifikate
Für die Verwaltung der Zertifikate eines Kunden steht
eine Datentabelle zur Verfügung. Dabei können folgende Felder gepflegt
werden.
Feld
Beschreibung
Zertifikate
Hier
      kann der Typ des Zertifikats eingetragen werden.
Für
      die
Nachhaltigkeit
gelten nur bestimmte Typen, die im Format
AF_NAHA_ZERT
nachgelesen werden
      können.
Bemerkung
Eigene Bemerkung / Beschreibung des
      Zertifikats oder z.B. die Nummer des Zertifikats.
Gültig ab
Ab
      wann das Zertifikat gilt, wird nichts eingetragen ist das Ab Datum
      unbegrenzt gültig.
Gültig bis
Bis
      wann das Zertifikat gilt, wird nichts eingetragen ist das Bis Datum
      unbegrenzt gültig.
Zertifizierungsmethode
Hier
      kann die Zertifizierungsmethode des Zertifikats eingetragen werden.
      (Format
AF_ZERTMETH
)
Sortierung
Bei
      mehreren Zertifikaten für den gleichen Zeitraum (z.B. DE und EU), kann
      hier die Sortierung eingetragen werden, damit zum Beispiel das DE
      Zertifikat immer zuerst ermittelt wird.
Kategorie
Hier
      kann die Kategorie des Zertifikats (Format
AF_ZERTKATEG
) eingetragen
      werden.
Kontrollstelle
Feld
      für zusätzliche Informationen (kann per
Einrichterparameter
angezeigt
      werden)
Kontrollnummer
Feld
      für zusätzliche Informationen (kann per
Einrichterparameter
angezeigt
      werden
[...]


---

## Registerkarte Zusatz

Registerkarte Zusatz
In dieser Abteilung sind inhaltlich unterschiedliche
Steuerungen zusammengefasst:
Ausprägung:
An diesem Parameter ist festgemacht, ob bei der
Vorgangs­erfassung bei diesem Artikel ein Fenster zur Erfassung weiterer
Merkmale (z.B. Serien­nummern) aufgeht. Näheres hierzu bei der Beschreibung
der Seriennummernver­wal­tung.
Belegdruck bei Wert = 0
Hier wird festgelegt, ob und ab wann im Vorgang eine
Position mit diesem Artikel gedruckt werden soll, wenn der Wert der Position 0
ist. Dies kann getrennt für Ein- Verkauf gepflegt werden. Folgende Fälle werden
unterschieden:
Aufmaße des Artikels:
Die Maße des Artikels können hier hinterlegt werden.
Eine Standardauswertung steht derzeit nicht zur Verfügung; bei Bedarf ist eine
private Variante anzulegen.
Nachkommastellen:
Die maximale Anzahl der Nachkommastellen wird hier
hinterlegt.
CO2:
Benötigt die Lizenz „CO2-Kostenaufteilung-Lizenz“.
Feld
Bedeutung
CO2-Artikel
Nur
      wenn dieser Wert auf „Ja“ steht, wird im Formular etwas
      angedruckt
Heizwert
Heizwert in Gj/t
Emissionsfaktor
Emissionsfaktor in
      kg(CO2)/kWh
Gewicht pro Me
Um
      eine Berechnung sicherzustellen, muss hier das Gewicht in kg pro
      Grundmengeneinheit eingegeben werden.

---

## Abwicklungsregister

Abwicklungsregister

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
erfolgen. Diese Funktion
      läßt sich nicht wegschützen.
Aktualisieren
Strg+R
Durch Klicken auf die Schaltfläche
werden die Daten mit
      der aktuellen Einstellung erneut aus der Datenbank gelesen. Die zugehörige
      Tastenkompindation lautet
Strg+R
(wie Refresh). Diese Funktion
      läßt sich nicht wegschützen.
Gruppieru
ng
Strg+G
Bei
      einigen Varianten erscheint eine weitere Schaltfläche
. Die Anzeige unterscheidet sich durch ein
      Kreuz an der linken Seite, mit dem die Daten aufblättern kann. Es werden
      in diesen Varianten erst einmal nur noch einige zentralle Informationen
      angezeigt:
Durch Klicken auf das Kreuz bzw.
      durch Drücken der Taste „
Einfg
“ kann der Detailbereich für die
      aktive Zeile aufgeblätter und durch Klicken auf das Minus-Zeichen bzw.
      durch Drücken der Taste „
Entf
“ kann er wieder geschlossen werden.
      Man kann auch gleichzeitig alle Daten aufblättern oder wieder schließen,
      indem man die Tasten + bzw – auf dem Nu
[...]


---

## Archiv Volltext-Recherche

Archiv Volltext-Recherche
Archivmanager
Registerkarte
Volltext-Recherche
Volltext-Lizenz (914)
Ja/Nein
Lizenzspa
      „Volltextrecherche“
Archivtext-Einträge
Anzahl der Einträge der Relation
      „Archivtext“
Informatorisch
Archivtext-Index
Name
      des Volltext-Index
Informatorisch, Standard:
      „ArchivTextIndex“
Der
      Name ist auch in der JVar 2014, „JVAR_ARCHIV_VOLLTEXT_NAME“
      verfügbar
Aktualisierungsfunktion
Name
      der Aktualisierungsfunktion
Standard:
      „volltextrecherche_progress“
Hinweis:
Hier bei dieser Datenbank-Funktion
      geht es lediglich darum den nächsten Kandidaten für die Erzeugung des
      Archivtextes anzugeben!
Die eigentliche
      Volltext-Index-Aktualisierung erfolgt immer durch Referenz-ERP-Programmcode bzw.
      durch interne Sybase-Routinen.
Letzte Aktualisierung
Zeitstempel der letzten
      System-Volltext-Index-Aktualisierung
Volltext-Index-Einträge
Anzahl der in den Volltext-Index
      einfließenden Dokumente
Die Aktualisierungsfunktion ermittelt die nächsten zu
verarbeitenden Kandidaten für die Aufbereitung des Archivtextes. Die von Referenz-ERP
ausgelieferte Funktion kann privatisiert werden um auf besondere Umstände
reagieren zu können.
Auslieferung  :
volltextrecherche_progress
---<summary>Liefert eine vorgebbare
maximal-Anzahl zu verarbeitender
Formulararchiv-Einträge</summary>
---<returns>Key
Formulararchiv und einem Problem-Status, dieser ist ungleich 0 wenn ein Problem
aufgetreten ist.
---</returns>
---<param
name="in_anzahl"></param>
---<param
name="in_zeitschranke"></param>
CREATE PROCEDURE
volltextrecherche_progress( IN in_anzahl INTEGER DEFAULT 1 , IN in_zeitschranke
INTEGER DEFAULT 1 )
RESULT
(
fa_id    INTEGER,
fa_mndnr
INTEGER,
problem  INTEGER
)
BEGIN
DECLARE DC_HOUR
INTEGER;
SET DC_HOUR =
DATEPART( HOUR , NOW() );
IF ( DC_HOUR
< 5 OR DC_HOUR > 19 ) OR ( in_zeitschranke != 1 ) THEN
IF (
NOT EXISTS( select * FROM amic_status_relation(
'archiv'
) WHERE status IN ( 0 , 1 ) )
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
      für das auf der neuen Auswahlliste basierende Archiv und den auf der
      Auswahlliste basierenden
Reporten
zur Verfügung.
Ansichten Verwalten
Dies
      ist eine Möglichkeit der neuen Auswahlliste für alle Anwender die
      Darstellung veralten, ohne private Ableitungen zu bilden.
Schriftart auswählen
Hier
      kann die Schriftart, der Schriftschnitt und die Schriftgrößer eingestellt
      werden. Die Standardeinstellung lautet Verdana-9.
NULL-Darstellung
      auswählen
Datenbankfelder, in die nie ein Wert
      eingegeben wurde und die keinen Default-Wert haben, haben den Wert NULL,
      der nicht mit der Zahl 0 verwechselt werden darf. Hier kann man zwischen
      zwei Werten wählen: <null> oder . (Punkt).
Für
      diese Auswahl existiert im Menü die gleichnamige Funktion
      „NULL-Darstellung auswählen“. Wird diese weggeschützt, so steht diese
      Auswahl nicht zur Verfügung.
Design auswählen
Hier
      kann zwischen verschiedenen Farbgebungen der Auswahlliste ausgewählt
      werden.
Für
      diese Auswahl existiert
[...]


---

## Die Erfassungsmaske

Die Erfassungsmaske
Kopfdaten
Im Kopf wird Ihnen die Partienummer und die
Datensatznummer angezeigt.
Darüber hinaus können Sie einen Belegtyp wählen:
Belegtyp
Abschlag
Ab
      Erstellung des Abschlags
Folgeabschlag
Ab
      Erstellung des Abschlags
Finale
Ab
      Erstellung der finalen Abrechnung
Der hier gewählte Belegtyp gibt an, bei welchem Beleg
dieser Typ berücksichtigt werden soll. Wird also beispielsweise „Abschlag“
gewählt, so wird das Laborergebnis für den Abschlag verwendet. Wenn ohne
Abschlag ein finaler Beleg erstellt wird, so findet das Laborergebnis keine
Berücksichtigung.
Ist ein Belegtyp abgerechnet, so kann dafür zwar ein
Wert eingetragen werden, er wird jedoch nur bei Neuerstellung (nach voriger
Stornierung) des Belegs berücksichtigt !
Existiert ein Datensatz für eine höhere Stufe (z.B.
Finale) beim Erstellen eines Labordatensatzes (z.B. für Abschlag), so erhalten
Sie eine Warnung, denn die Laborergebnisse werden dann beim Beleg der
niedrigeren Stufe berücksichtigt, werden jedoch bei der Erstellung des höheren
Beleges (hier Finale) durch andere Werte ersetzt.
Labordaten
In einer Liste werden Ihnen die Labordaten mit ihrer
Qualitätsnummer, der Bezeichnung und einem Analysewertefeld angezeigt. In
letzteres können Sie bei Änderung und Neuerfassung Daten eingeben.

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
Einstellungen
Für die Einstellungen stehen auf der Maske folgende
Häkchen zur Verfügung.
Name
Beschreibung
Nichts mehr ändern
Ist
      dieses Häkchen gesetzt, werden alle Felder auf der Maske deaktiviert
      (gegen Eingabe geschützt, die automatische Vorbelegung der Eingabefelder
      bleibt erhalten).
Einstellung speichern
Dieses Häkchen ist beim Start der
      Maske immer gesetzt. Schaltet man es ab, werden die Änderungen an den
      Einstellungen nicht gespeichert. Man nutze diese Möglichkeit, wenn man bei
      einer bestimmten Funktion vom Standard abweichende Einstellungen
      vorgenommen hat!
Hinweis:
Die Speicherung der Einstellungen erfolgt auch, wenn
man den Dialog mit der ESC-Taste abbricht.
Wie auch sonst in Referenz-ERP üblich, werden einige Felder
datenabhängig deaktiviert oder aktiviert. Einstellfelder und Eingabefelder
werden völlig ausgeblendet, wenn sie keinerlei Bedeutung für die spezifische
Umwandlungsfunktion besitzen. Manchmal werden Einstellfelder schattier
[...]


---

## Diensteanbieter

Dienstea
nbieter
Für verschiedene Geodatendienste gibt es verschiedene
Dienstanbieter, die jeweils einen sog. API-Key zur Identifikation zur Verfügung
stellen:

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

## Einrichtung des externen Kassendisplays

Einrich
tung des externen
Kassendisplays
Die Einrichtung erfolgt in der Kassenverwaltung. Jeder
logischen Kasse ist ein Kassensystem zugeordnet. Dieses Kassensystem beschreibt
die Hardwareeinheit. Technisch gesehen sind alle der Einstellungen dem
Kassensystem zugeordnet.
Auf der Registerkarte „Geräte“ findet sich im unteren
Bereich ein Rahmen mit der Überschrift
Hardware externes
Display
. Hier richten Sie ein Bildschirmdisplay ein.
Auf der Registerkarte „Anzeige“ findet sich eine
Tabelle mit Feldern, die zur Anzeige eingerichtet werden können.
Diese Tabelle mit Anzeigefeldern ist einem
Anzeigeschema zugeordnet, dass Sie in dem Feld „Schema“ auswählen müssen. Sie
können auch mit der Funktion „Neues Anzeigeschema“ ein neues Schema erstellen.
Hinweis:
Bitte beachten Sie, dass die Angaben des Schemas stets
für alle Anzeigen gelten, die das gleiche Schema verwenden!!!
Registerkarte Anzeige
      Name
Folgende Namen können eingerichtet
    werden
BON
Hier
      wird der laufende Bon dargestellt
LDC
In
      dieses Feld wird das Währungskennzeichen geschrieben. *)
LDT
Text
      der Zeilendisplayzeile *)
LDV
Wert
      der Zeilendisplayzeile *)
LINEDISPLAY
Zeilendisplay – Hier werden Daten
      der o.g. Werte zusammen dargestellt.
SCREEN
Diese Konfiguration dient der
      Größendimensionierung des Fensters
QRCODE
QR-Code für AnyBill, wenn die Lizenz
      vorhanden ist. Diese Einrichtung ist nur bei entsprechender Lizenz
      verfügbar.
SUMME
Hier
      wird die Summe des Bons angezeigt.
(*) Diese Zeilen werden nicht auf dem ScreenDisplay
dargestellt. Die dienen der Füllung und Ausrichtung in einem Feld namens
LINEDISPLAY. Wird beispielsweise das Währungskennzeichen (LDC) linksbündig
angegeben, so wird dies links neben den Wert (LDV) geschrieben.
Wird kein Zeilendisplay und kein Feld mit dem Namen
LINEDISPLAY verwendet, so können diese Felder entfallen.
Positionen
In den nachfolgenden Spalten werden die Positionen
      der Objekte eingerichte
[...]


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

## Funktionen des Bezahlterminals

Funktionen des Bezahlterminals
Das Authentifizierungsverfahren (Unterschrift oder
PIN) ist zunächst einmal von dem Institut abhängig, das die Karte ausgibt.
Darüber hinaus ist die Kombination der technischen Ausstattung der Karte und des
Terminals ausschlaggebend für die Abwicklung der Zahlung.
Der technische Trend zu mehr Sicherheit hat zur Folge,
dass die neueren Karten mit Chips ausgerüstet werden, die die Authentifizierung
mit PIN sichern.
Bezahlen mit EC-Karte oder Kreditkarte
Hier kann mittels der EC-Karte oder Kreditkarte
bezahlt werden. Der Betrag wird an das Terminal übertragen und die Zahlung wird
vom Terminal abgewickelt.
Lastschrift mit EC-Karte oder
Kreditkarte
Mit dieser Funktion kann das elektronische
Lastschriftverfahren forciert werden. Diese Funktion muss gesondert angesteuert
werden. Sie ist keine grundsätzliche Bezahlfunktion und wird von Banken wegen
des möglichen Ausfallrisikos nicht empfohlen. Bitte wenden Sie sich an den
Branchen-ERP-Support.
Bezahlen mit der
Geldkarte
Die Geldkarte wurde 1996 als elektronische Geldbörse
eingeführt. Ein Geldbetrag kann auf den Kartenchip geladen werden und beim
Bezahlen ohne Verifikation per PIN oder Unterschrift abgebucht werden. Diese
Bezahlart ist vorwiegend für Kleinbeträge gedacht und wird inzwischen zwingend
für Zigarettenautomaten eingesetzt, da der Geldkartenchip eine
Altersverifikation gewährleistet.
Für die Abwicklung der Zahlung ist auf Händlerseite
eine sog. Händlerkarte notwendig, die im Gerät eingesetzt wird.
Bezahlen mit der GiroGo
GiroGo ist im Prinzip eine Erweiterung der oben
erwähnten Geldkarte. Das Bezahlen funktioniert technisch genau wie bei
EC-Kartenzahlungen, jedoch gibt es einige Besonderheiten:
•
Ist der Zahlbetrag über 20 €, so wird die Zahlung wie gewohnt mit PIN
autorisiert.
•
Ist der Zahlbetrag kleiner oder gleich 20 €, so wird angeboten die Karte
einzustecken oder vor das Gerät zu halten.
Wird die Karte vor das Gerät gehalten und der
Zahlbetrag ist als Guthaben a
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

## ImportVorgPositionZuAb

ImportVorgPositionZuAb
Zu-Abschläge des Vorgangs
Aus dieser Relation werden Zu- und Abschläge im
Vorgang referenziert
Feld
Bedeutung
IVP_GUID
Guid
      der Position
IVZ_Zaehler
Laufende Nummer des
      Zu-/Abschlags
IVZ_Guid
Referenz auf den Inhalt der Tabelle
ImportVorgZuAbDef

---

## ImportVorgStammZuAb

ImportVorgStammZuAb
Zu-Abschläge des Vorgangs
Aus dieser Relation werden Zu- und Abschläge im
Vorgang referenziert
Feld
Bedeutung
IVS_GUID
Guid
      des Stammsatzes
IVZ_Zaehler
Laufende Nummer des
      Zu-/Abschlags
IVZ_Guid
Referenz auf den Inhalt der Tabelle
ImportVorgZuAbDef

---

## Kassendatum

Kassendatum
Standardmäßig ist das Referenz-ERP Tagesdatum das
Systemdatum. Bekanntlich kann man das aktuelle Tagesdatum mit Direktsprung
[DAT]
verstellen. Dann fungiert das
verstellte Datum als das vorgeschlagene Belegdatum etwa für die
Vorgangserfassung. Auf diese Weise kann man Belege zu einem anderen Datum
erleichtert nach erfassen, ohne jeweils an die Anpassung des Belegdatums
beachten zu müssen. Die eingestellte Datumsänderung gilt höchstens bis zum
Abmelden aus Referenz-ERP. Das Systemdatum wird dadurch nicht beeinflusst.
Von der Änderung des Tagesdatums auf
Kassenarbeitsplätzen ist dringend ab zu raten!
Grund: Das Kassenbuch und die Kassenberichte werden in
strikter Abhängigkeit vom Systemdatum geführt. Hier wird nicht nur ein Datum,
sondern ein Stempel aus Datum und Uhrzeit geführt, der die exakte Chronologie
der Kassenbelege und ihre Einordnung in Kassensitzungen fest hält.
Würde man nun beispielsweise aber trotzdem am 7. April
das Datum auf den 5. April zurück stellen, so würde ein Barverkaufsvorgang
warenseitig mit dem 5. April, im Kassenbuch aber mit dem 7.April geführt werden.
Würde man überdies nun auch noch einen Fibu Übertrag starten, so würden
normalerweise ein Fibu Beleg per 7.April und ein Zahlungsbeleg per 7. April
entstehen. Man sieht also, dass man sich die Abstimmung der Kasse sowohl mit der
Ware wie auch mit der Fibu unnötig erschweren kann.
In der Kasse erfasste Finanzbelege werden meist sofort
und automatisch an die Fibu übertragen (SPA Einstellung). Hier gilt jetzt:
Belegdatum Kasse = Übertragsdatum Fibu. An dieser Stelle wurde die Logik
geändert: bisher wurde für den Übertrag an die Fibu das eingestellte Datum
gewählt.
Unbedingt zu vermeiden ist die Umstellung des
Systemdatums auf Kassenarbeitsplätzen!
Das kann neben Problemen bei Abstimmbarkeit auch
Störungen nach sich ziehen, wenn dadurch etwa der Zeitpunkt des Abschlusses
einer Sitzung vor ihrer Eröffnung liegen würde.
Die Änderung des Tagesdatums kann durch die
Einstellung
[...]


---

## Mahnvorschlagsliste über Formulartyp 202 drucken

Mahnvorschlagsliste über Formulartyp 202 drucken
Hauptmenü
Mahn-, Zahl-, Zinswesen
Mahnwesen
Mahnvorschläge bearbeiten
Funktion Liste über Formular
F8
Direktsprung
[MHVB]
.
Es ist möglich, Mahnvorschläge über das Formular 202
zu drucken. Folgende Formularbereiche werden dabei verwendet.
•
301 MahnKopf Formularkopf
•
303 MahnAbschluß Seiten Ende der letzten Seite
•
304 Mahnposition Einzelne Zeile
•
305 MahnFolgekopf Überschrift der nächsten Seiten
•
306 MahnFuß Seiten Ende
•
308 MahnSummenKopf Überschrift Pro Konto
•
309 MahnSummenFuß SummenZeile Pro Konto
Folgende Variablen sind in allen Teilen (Kopf,
Folgekopf, Fuß und Abschluss) verfügbar, die nicht Zeilentyp sind.
Formularbereiche, die nicht separat mit aufgeführt werden, enthalten nur
Festtext oder diese Felder!
Bezeichnung
Typ
Nr
Beschreibung
Mahnlistnummer
Numerisch
4
Nummer der aktuell gedruckten
      Zahlungsliste
Mahnlistbezeich
Text
3
Bezeichnung der
      Mahnliste
Mahnlsitdatum
Datum
5
Erstelldatum
BedienerId
Numerisch
4
Id
      des Bedieners, der diese Liste erstellt hat.
Bedienerkurz
Text
3
Kurzbezeichnung –""-
Bedienername
Text
3
Name
      –""-
•
304 Positionszeile
Bezeichnung
Typ
Nr
Beschreibung
MahnStufPosition
Numerisch
Mahnstufe ( 0 bei
      Verrechnung)
MahnVorPosbetrag
Numerisch
Betrag der Mahnung ( Siehe
      FiBuVP_Betrag)
MahnVorPosVDatum
Datum
Valutadatum
MahnVorPosZinsen
Numerisch
Zinsen der Position
MahnVorPosZinsSatz
Numerisch
Zinssatz, mit dem die Zinsen dieser
      Position berechnet wurden
MahnVorPosZinsTage
Numerisch
Mit
      wie vielen Tage wurde gerechnet
MahnVorPosZinsGr
Numerisch
Zinsgruppe
      mit der diese Zinsen berechnet wurden.
FiBuV_Id
Numerisch
Intern
FiBuV_PosZaehler
Numerisch
Intern
FiBuVP_BuchTyp
Numerisch
Buchungstyp
Fibuv_klasse
Text
Belegklasse (ZA AR AG ER
      EG.....)
FiBuV_Nummer
Text
Belegnummer
NumKreisnummer
Numerisch
Nummernkreis aus dem sich diese
      Nummer
FiBuV_NumNummer
Numerisch
Numerischer Anteil der
      Belegnummer
FiBuV_F
[...]


---

## Manuelle Zu-/Abschläge

Manuelle Zu-/Abschläge
Zu-/Abschläge können manuell im Anschluss an die
Erfassung einer Warenposition erfasst werden.
Nummer oder Text
Auswahl eines
Zu-Abschlagsatzes
. Wählen Sie hier den für
diesen Zu-/Abschlag gültigen Satz aus. 0 ist die Standardeinstellung für einen
komplett manuell erfassten Zu-/Abschlag.
Zu-/Abschlag-Gruppe
Wird nur angezeigt – die Zu-/Abschlaggruppe des
Artikels
EKZ-Nummer
Erlöskennziffer auf die der Zu-/Abschlag gebucht
werden soll – 0 = die gleiche Erlöskennziffer wie die zugehörige
Warenposition.
Kostenstelle
Hier kann eine von der Warenposition abweichende
Kostenstellennummer für den Zu-/Abschlag angegeben werden.
0 = es wird die
Kostenstellennummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenstellen-Lizenz
aktiviert ist.
Kostenträger
Hier kann eine von der Warenposition abweichende
Kostenträgernummer für den Zu-/Abschlag angegeben werden.
0 = es wird die
Kostenträgernummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenträgerrechnung
angeschlossen
aktiviert ist.
Kostenobjekt
Hier kann eine von der Warenposition abweichende
Kostenobjektnummer für den Zu-/Abschlag angegeben werden.
0 = es wird die
Kostenobjektnummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenobjekt-Lizenz
aktiviert
ist.
Die Bezeichnung dieses Feldes ist in der
OPTION
Kostenobjekt_Label
einrichtbar!
Wirkt auf Preis
Ja – Zu-/Abschlag wirkt auf den Einzelpreis des
Artikels pro Mengeneinheit und wird dann erst mit der Menge multipliziert
Formel
Zu-Abschlagsformel siehe auch
in den automatischen
Zu-/Abschlägen
.
Prozentsatz
Prozentsatz des Zu-/Abschlags (bei prozentualen
Zu-/Abschlägen)
Preis/Satz
Zu-/Abschlagbetrag (nicht bei prozentualen
Zu-/Abschlägen)
Preiseinheit
Die zum Zu-/Abschlagbetrag gehörige Preiseinheit
Bezugsmenge
Ebendies
Bezugswert
Wert auf den sich der Zu
[...]


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

## Registerkarte Steuern

Registe
rkarte Steuern
Auf der Registerkarte Allgemein steht der
Steuerschlüssel für diesen Artikel eingetragen. Soll bei Verwendung bestimmter
Steuergruppen ein abweichender Steuerschlüssel verwendet werden, so kann dieser
hier eingetragen werden.

---

## Saatgut löschen

Saatgut löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
SaatAnerkStelle
SaatAnerkZuord
SaatFruchtArt
SaatFruchtSorte
SaatFruchtSorteAddon
SaatFruchtSorteLaender
SaatgutAnerkennung
SaatgutBearbeitung
SaatgutEtiketten
SaatKategorie
SaatRohware
Vermehrungsvertrag
Feldanerkennung
FeldanerkennungsMenge
FeldBesichtigung
AckerschlagKartei
AckerschlagGruppe

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
stoppen oder synchronisieren
Eine Subskription entfernen:
1.
Wählen Sie in der Ordnerliste SQL Remote-Subskriptionen
2.
Wählen Sie die gewünschte Subskription aus der Registerkarte SQL
Remote-Subskriptionen
3.
Stoppen Sie die Subskription w.o. beschrieben
4.
Klicken Sie die gewählte Subskription mit der RECHTEN Maustaste an
5.
Klicken Sie nun auf „löschen“ und bestätigen Sie den Löschvorgang

---

## Tabelle zur Version: 9.0.2402.3

Tabelle zur Version: 9.0.2402.3
ID
Releasenote - Titel
Geprüft
34809
Datenbankfunktion AMIC_FSTR
35687
neue Auswahllistenvariante im Archiv
35655
Fehler bei Neuanlage eines Mengenzeitraums
35721
THG-Werte werden automatisch nachgeladen bei manuellen
      Anbauland

---

## Zahlvorschläge drucken

Zahlvorschläge drucken
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlvorschlagsliste
Es ist möglich, eine Liste der Zahlvorschläge über
einen Crystal –Report zu drucken. In diesem Report kann sowohl nach Liste, als
auch nach Kontonummer eingegrenzt werden.
Zusätzlich existiert noch eine Möglichkeit sich über
ein Formular vom Typen 201 selber eine Liste zu erstellen und zu drucken. Dafür
existiert ein Vorlageformular mit der Nummer -19. Aufgerufen wird diese Liste
in
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlvorschläge bearbeiten
Liste über Formular
Hinweis:
Diese Liste enthält keine
Informationen über die Bankverbindung und wird nicht weiter
gepflegt.
Folgende Formularbereiche werden dabei verwandt!
•
Zahlkopf

Formularkopf
•
Zahlfolgekopf

Überschrift der nächsten Seiten
•
Zahlposition

Einzelne Zeile
•
Zahlfuß

Seitenende
•
Zahlabschluss

Seitenende der letzte Seite
•
Zahlsummenkopf
Überschrift Pro Konto
•
Zahlsummenfuß
Summenzeile Pro Konto
Folgende Variablen sind in allen Teilen (Kopf, Fuß und
Zeilentyp) verfügbar. Formularbereiche, die nicht separat mit aufgeführt werden,
enthalten nur Festtext oder diese Felder!
Bezeichnung
Typ
Nr.
Bedeutung
Zahllistnummer
Numerisch
4
Nummer der aktuell gedruckten
      Zahlungsliste
Zahllistbezeich
Text
3
Bezeichnung der
      Zahlvorschlagsliste
Zahllistdatum
Datum
5
Erstellungsdatum
Bedienerid
Numerisch
4
Id
      des Bedieners, der diese Liste erstellt hat
Bedienerkurz
Text
3
Kurzbezeichnung -“-
Bedienername
Text
3
Name   -“-
•
503 Positionszeile
Bezeichnung
Typ
Nr.
Bedeutung
Zahlartid
Numerisch
Zahlvorposbetrag
Numerisch
Betrag der Zahlung ( Siehe
      FiBuVP_Betrag)
Zahlvorposdatum
Datum
Zahlvorposskonto
Numerisch
Gezogener Skonto ( Siehe
      FiBuVP_SkoBetrag)
ZahlVorPosSH
Text
Sollhabenkennzeichen
FiBuV_Id
Numerisch
Intern
FiBuV_PosZaehler
Numerisch
Intern
FiBuVP_BuchTyp
Num
[...]


---

## Zinsabschlag

Zinsabschlag
Hauptmenü
Mahn-/Zahl-/Zinswesen
Stammdaten
Zinsabschlag Stammdaten
Direktsprung
[ZAS]
Spezielle Form der Kapitalertragssteuer. Sie gilt mit
der Überschreitung der Freibeträge für alle in- und ausländischen
Kapitalanleger, die ihren Wohnsitz oder gewöhnlichen Aufenthaltsort in
Deutschland haben. Hierbei wird von Zinsen aus verbrieften und nichtverbrieften
Kapitalforderungen ein Zinsabschlag von 30%, bei Schaltergeschäften von 35%
einbehalten. Er ist auf die Einkommens- bzw. Körperschaftssteuer anrechenbar.
Für Personen, die ihren Wohnsitz im Ausland haben, wird keine Zinsabschlagsteuer
erhoben.
Ausnahme hier bilden Schaltergeschäfte, die in
Deutschland getätigt werden.
Ob Zinsabschlag berechnet wird, ist einerseits von
einem Steuerungs-Parameter „Zinsabschlag berechnen“ in der Parametergruppe
"Optionen Finanzwesen" abhängig. Andererseits muss in der
Zinsgruppe
des Kunden bei
„Zinsabschlag berechnen“ ein Haken gesetzt sein.
Wichtig:
Das Kennzeichen „Zinsabschlag
berechnen“ aus der Zinsgruppe wurde in älteren Versionen nicht ausgewertet. Es
muss nun gepflegt werden!
Gültig ab
Da nicht auszuschließen ist, dass der Steuersatz sich
ändern wird, kann man hier angeben, ab wann der entsprechende Prozentsatz gültig
ist.
Kapitalertragssteuer für Dividenden:
Beschreibung
Kontonummer
Auf
      dieses Konto wird die errechnetet Kapitalertragssteuer
      gebucht.
Prozent
Von
      den errechneten Zinsen wird mit diesem Prozentsatz die
      Kapitalertragssteuer errechnet.
Text
Dieser Text wird bei der
„Übernahme in die Primanota“
als
      Text für die Belegposition verwendet.
Zinsabschlag:
Beschreibung
Kontonummer
Auf
      dieses Konto wird der errechnetet Zinsabschlag gebucht.
Prozent
Von
      den errechneten Zinsen wird mit diesem Prozentsatz der Zinsabschlag
      errechnet.
Text
Dieser Text wird beim
„Übernahme in die Primanota“
als
      Text für die Belegposition verwendet.
Anrechenbarer Solidaritätszuschlag:
Beschreibung
Kontonummer

[...]


---

## Zu-/Abschlagsperre im Zu-/Abschlag

Zu-/Abschlagsperre im Zu-/Abschlag
Eine Zu-/Abschlagsperre kann auch im Zu-/Abschlag
selbst eingerichtet werden. So lassen sich eingerichtete Zu-/Abschläge
vorübergehend abschalten.

---

## Zu- und Abschläge löschen (inkl. 1+7)

Zu- und Abschläge löschen (inkl. 1+7)
In folgenden Relationen werden die Datensätze
entfernt:
ZUABSCHKLASSE (ohne die 0 (ohne Zu-/Abschlag) zu
entfernen)
ArtiZuAbGruppe (ohne die 0 (keine Zu-/Abschlaggruppe)
zu entfernen)
ARTZUABTYP
ARTZUABTEXT
ARTZUABZAHLART
ARTZUABZAHLSATZ
ARTZUABVERSART
ARTZUABVERSSATZ
ARTZUABGENERELL
ARTZUABGENSATZ
ArtiZuAbGewicht
ArtZuAbGewiSatz
ArtiZuAbGebinde
ArtZuAbGebiSatz
ArtZuAbLaufzeit
ArtZuAbLaufsatz
ArtZuAbLiefMen
ArtZuAbLiefSatz
In folgenden Relationen wird die 0 eingetragen:
Kundenstamm (Felder ZuAbKlNummerEK, ZuAbKlNummerEKI,
ZuAbKlNummerVK, ZuAbKlNummerVKI)
Artikel (Felder ArtiZuAbGrupEK, ArtiZuAbGrupEKI,
ArtiZuAbGrupVK, ArtiZuAbGrupVKI)
BaustArtikel (Felder ArtiZAGrNummerVK,
ArtiZAGrNummerEK)
Beim Löschen der Zu- und Abschläge werden automatisch
die
Vorgänge
Ware
und
Kontrakte
mit gelöscht.

---

