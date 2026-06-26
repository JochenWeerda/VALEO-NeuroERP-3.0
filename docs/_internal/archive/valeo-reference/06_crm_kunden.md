# CRM, Kunden- & Lieferantenstamm — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (336 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Kunden

Kunden
Auf diesem Tabs werden gezielt Änderungen eines
Attributs von Datensätzen in Relationen gesucht, die einem bestimmten Kunden-
oder Lieferantenstamm zuzuordnen sind. Die Angaben in den Feldern
Kundennummer
und
KundId
sind optional, es muss aber mindestens zu
einem dieser Felder eine Eingabe erfolgen. Alle genannten Eingabefelder verfügen
über eine unterstützende Itembox-Anbindung.
Wird lediglich die  Kundennummer angegeben, so
ist die Basis für kundenstammbasierte Suchanfragen die Menge aller
Kundenstammeinträge mit dieser Kundennummer, also auch diejenigen mit
eingetragenem Löschkennzeichen.
Wird ein Kundenstamm per KundId spezifiziert, so ist
die Basis für kundenstammbasierte Suchanfragen nur der angegebene
Kundenstammeintrag.
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
Die generierte Abfrage kann relativ komplex werden und
kann eine mehr oder weniger längere Antwortzeit bewirken. Wird zum Beispiel das
Attribut
ArtiZAG_Preis
der Relation
ARTZUABGENSATZ
zu einem
Kundenstamm angegeben, so müssen alle Datensätze des Logfilearchivs gefunden
werden, die mit Schlüsselwerten zur Relation
ARTZUABGENSATZ
versehen
sind, die i
[...]


---

## Homepage anzeigen überarbeitet

Homepage anzeigen überarbeitet
In Anschriften wurde der Reiter "Homepage entfernt".
Stattdessen gibt es unter "Zusätze" ein neues Feld, welches Homepage heißt. Eine
dort angegebene Webadresse öffnet den Browser mit dieser, wenn die Funktion
"Homepage anzeigen" aufgerufen wird.
Releasenote Kategorie:
Ticket: 708457[32085]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Anschriften [ANSCH]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 32085, 708457

---

## Bemerkung für Musterkunden einzeln pflegbar

Bemerkung für Musterkunden einzeln pflegbar
Bei Neuanlage eines
Kunden/Lieferanten/Kontokorrentkunden unter Verwendung eines Musterkunden, wurde
fälschlicherweise dessen Bemerkungs-Id übernommen. Somit hatten alle Kunden, die
gleiche Bemerkung und es konnten keine eigenen Bemerkung für einen einzelnen
Kunden gepflegt werden.
Releasenote Kategorie:
Ticket: 713518[32724]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [KU]
Variante: Kunden
Funktion/Report: F8
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32724, 713518

---

## Bemerkung für Musterkunden einzeln pflegbar

Bemerkung für Musterkunden einzeln pflegbar
Beim Importieren neuer
Kunden/Lieferanten/Kontokorrentkunden über die Anwendung
"Endkontrolle/Einspielung Kunden" wurde beim Musterkundenabgleich dessen
Bemerkungs-Id übernommen.  Somit hatten alle Kunden, die gleiche Bemerkung
und es konnten keine eigenen Bemerkung für einen einzelnen Kunden gepflegt
werden.
Releasenote Kategorie:
Ticket: 713518[32844]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: Endkontrolle/Einspielung Kunden
Variante: Endkontrolle/Einspielung Kunden
Funktion/Report: -> Referenz-ERP Kunden
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32844, 713518

---

## Interessent in Kunden umwandeln

Interessent in Kunden umwandeln
Beim Umwandeln eines Interessenten in einen Kunden
oder Kontokorrent-Kunden wird die nächste Nummer aus dem zugeordneten
Nummernkreis vor belegt.  Jetzt findet vor dem Umwandeln noch eine
zusätzliche Prüfung statt, ob diese Nummer ggf. schon vergeben ist und es wird
die nächste freie Nummer vorgeschlagen.
Releasenote Kategorie:
Ticket: 714300[32845]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: [IN]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32845, 714300

---

## Mail-Funktionen in der Ware

Mail-Funktionen in der Ware
Für Warenbelege gibt es jetzt zwei Funktionen, um
einen Beleg erneut zu versenden.  1) Neu drucken und neu versenden 2) Beleg
erneut versenden (Letzte E-Mail wird aus dem Archiv heraus erneut
versendet. Hier ist eine Anpassung der Mailadresse möglich)
Releasenote Kategorie:
Ticket: 715711[32988]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: -
Variante: -
Funktion/Report: AGB, LIB,AUB, REB, GUB ... etc.
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 32988, 715711

---

## Kundenpfleger: Speichernabfrage

Kundenpfleger: Speichernabfrage
Nachdem ein neuer Kunde abgespeichert worden war,
wurde beim Schließen der Maske erneut nachgefragt, ob die geänderten Daten
gespeichert werden sollen. Dies geschieht nun nicht mehr.
Releasenote Kategorie:
Ticket: 717205[33223]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Kunden
Variante: Kunden
Funktion/Report: Neu
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33223, 717205

---

## Geodaten Lizenz

Geodaten Lizenz
Das Lizenzpflichtige Modul "Geodaten"  wird ab
nun vollumfänglich auf das Vorhandensein einer gültigen Lizenz
geprüft.
Releasenote Kategorie:
Ticket: 717752[33280]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Kunden
Variante: Kunden
Funktion/Report: diverse Funktionen wie Google Maps
und Karte
Weitere Informationen
Tags:
Releasenote, 8.3.2212.23, 33280, 717752

---

## Stoffstrom Kundenreport

Stoffstrom Kundenreport
Der Crystal Report "Stoffstrom Kundenreport" wurde
angepasst und kann nun größere Zahlen anzeigen.
Releasenote Kategorie:
Ticket: 717579[33282]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: -
Variante: -
Funktion/Report: Stoffstrom Kundenreport
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33282, 717579

---

## DSGVO

DSGVO
Die von Branchen-ERP ausgelieferte Einstellung zur
Anonymisierung laut DSGVO wurde in zwei Punkten angepasst:Die Kundenbezeichnung
wird mit anonymisiert. Die Kundenbanken werden gelöscht .
Releasenote Kategorie:
Ticket: 716012[33294]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: DSGVO
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33294, 716012

---

## Geodaten bei Kundenanschriftänderung

Geodaten bei Kundenanschriftänderung
Bei der Änderung von Anschriftdaten auf der
Kundenstamm-Maske gingen Geodaten der Anschrift verloren. Dies wurde behoben
Releasenote Kategorie:
Ticket: 0[33563]
Version: 8.3.2303.31
Datum: 31.03.2023
Anwendung: Kundenstamm
Variante: Standard
Funktion/Report: Ändern
Weitere Informationen
Tags:
Releasenote, 8.3.2303.31, 33563, 0

---

## Kundenstamm Speichern unter

Kundenstamm Speichern unter
Wenn ein Kunde mit der Funktion "Speichern unter" neu
angelegt wird, dann werden  das Zinsabdatum auf den 01.01.1901 gesetzt,der
Bediener und das Datum für die Neuanlage korrekt gesetzt, nur die letzte
Forderungsgruppe übernommen, falls im Original bereits mehrere Forderungsgruppen
hinterlegt waren.
Releasenote Kategorie:
Ticket: 723851[33889]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: KU, IN, LI
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 33889, 723851

---

## Rückbau-Funktionen Lieferanten

Rückbau-Funktionen Lieferanten
Die Funktionen "InfoKu" und "Lieferanten bewerten" in
der Anwendung Lieferanten [LF] wurden entfernt.
Releasenote Kategorie:
Ticket: 725940[34176]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Lieferanten
Variante: Lieferanten
Funktion/Report: InfoKu + Lieferanten bewerten
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34176, 725940

---

## FiBu Datenübernahme im XML-Format

FiBu Datenübernahme im XML-Format
Bei der Datenübernahme [DUEB] wurde beim XML-Import
immer dann, wenn die Steuergruppe mit übergeben wurde, diese mit der
Steuergruppe aus dem Kundenstamm geprüft und ggf. der betroffene Beleg nicht mit
importiert. Diese Prüfung findet nicht mehr statt.
Releasenote Kategorie:
Ticket: 726945[34214]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Datenübernahme [DUEB]
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 8.3.2309.1, 34214, 726945

---

## Drucker-Schachtsteuerung

Drucker-Schachtsteuerung
Im Zuge von notwendigen internen Pflege-/
Wartungsmaßnahmen wurde bedauernswerterweise die Verwendung von
Drucker-Schächten generell abgeschaltet. Ein Work-Around bestand darin in der
Windows-Druckersteuerung selber die Schächte einzustellen. Kunden, die das
gemacht haben, brauchen keine erneute Änderung machen.  Die Verwendung der
Drucker-Schächte funktioniert nun wieder wie in der Vergangenheit.
Releasenote Kategorie:
Ticket: 727976[34430]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: -
Variante: -
Funktion/Report: DIverse Druckszenarien in denen die
Verwendung von Schächten benötigt wird.
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34430, 727976

---

## Ändern eines Rechungsempfängers oder Zahlungspflichtigen

Ändern eines Rechungsempfängers oder Zahlungspflichtigen
Beim Ändern des Rechnungsempfängers oder
Zahlungspflichtigen über den Kundenstamm [KU] kam es unter Umständen dazu, dass
der Datensatz nicht gespeichert werden konnte.  Dies wurde behoben.
Releasenote Kategorie:
Ticket: 729392[34573]
Version: 8.3.2312.22
Datum: 22.12.2023
Anwendung: Kundenstamm
Variante: alle
Funktion/Report: [KU]
Weitere
Informationen
Tags:
Releasenote, 8.3.2312.22, 34573, 729392

---

## Kundenwechsel mit Nachhaltigkeit

Kundenwechsel mit Nachhaltigkeit
Beim Kundenwechsel von einem nachhaltigen Kunden zu
einem nicht nachhaltigen Kunden bzw. umgekehrt, ist im Behandlungsschema
einstellbar, wie mit dieser Situation verfahren werden soll. Hier sind Abbruch
oder Fortsetzung mit und ohne Warnung möglich.
Releasenote Kategorie:
Ticket: 727582[34422]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Eingangsrechnung
Variante: Bearbeiten
Funktion/Report: Kundenwechsel
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34422, 727582

---

## Rechnungsempfänger und Zahlungspflichtiger bei Musterkunden

Rechnungsempfänger und Zahlungspflichtiger bei Musterkunden
Das Anlegen von Rechnungsempfängern und
Zahlungspflichtigen bei Musterkunden ist wieder möglich.
Releasenote Kategorie:
Ticket: 730341[34672]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Kunden [KU], Lieferanten [LF] und
Kontokorrentkunden [KOKU]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.1, 34672, 730341

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

## Kundenstammpfleger für Nachhaltigkeit angepasst.

Kundenstammpfleger für Nachhaltigkeit angepasst.
Um Verwirrungen vorzubeugen ist jetzt auf dem
Kundenstammpfleger auf dem Tabreiter Zertifikate im Grid Nachhaltigkeit ein
neues Feld Indiv, THG-Werte dazu gekommen. Dieser kann entweder Nein oder
Ja sein. Standardmäßig ist das auf Nein, was dazu führt, dass man die THG-Werte
nicht mehr manuell pflegen kann. Bei JA sind diese wieder in der Zeile pflegbar.
Die THG-Werte dort kann man angeben, wenn man nicht möchte, dass die THG-Werte
aus dem Anbauland gezogen werden.  Des Weiteren war es möglich im oberen
Zertifikatgrid falsche Zertifikate im Nachhaltigkeitsgrid einzurichten. Es darf
das Zertifikat mit der Nummer (Zertifikattyp) 5 aus dem Format af_naha_zert
nur für den Mandantkunden eingetragen werden. Den Mandantkunden findet man oder
richtet diesen ein unter dem Direktsprung [MND]. Dort trägt man unter
Systemkundennummer den Mandantkunde ein. Nachdem dieser dort eingetragen ist,
darf man nur auf diesem den Zertifikattyp 5 einrichten. Für alle anderen Kunden
gibt es den Zertifikattyp nicht, aber dafür den Zertifikattyp 4.  Der
Zertifikattyp 5 ist für den Verkauf und die folgenden Vorgangsklassen: 5100,
5110, 5120, 5200, 5210, 5220 Der Zertifikattyp 4 ist für den Einkauf
Releasenote Kategorie:
Ticket: 732500[34936]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Kunden [KU], [MND]
Variante: Kunden
Funktion/Report: F8,F5
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 34936, 732500

---

## X-Rechnung Ansprechpartner

X-Rechnung Ansprechpartner
Der Ansprechpartner der X-Rechnung kommt nun aus dem
Bediener. Sollte dort keine E-Mailadresse und/oder keine Telefonnummer
eingetragen sein, so werden diese Daten aus dem X-Rechnung-Profil entnommen
(Fallback)
Releasenote Kategorie:
Ticket: 728333[35170]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: X-rechnung
Variante: Profile
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.3, 35170, 728333

---

## Abweichende Steuerschlüssel im EU-Ausland

Abweichende Steuerschlüssel im EU-Ausland
Im innereuropäischen Handel mit Endkunden kann es
notwendig sein, ausländische MwSt. zu berechnen. In der Regel werden diese
ausländischen Steuersysteme über Steuergruppen abgebildet. Solange ein Artikel
im Inland und in allen anderen Ländern generell der ermäßigten oder generell der
Regelbesteuerung unterliegt, kein Problem. Wenn der Artikel in Land A
allerdings ermäßigt und in Land B der Regelbesteuerung unterliegt, hatte man in
der Vergangenheit ein Problem. Nun können im Artikelstamm [ARS] neben dem
Standard-Steuerschlüssel auch abweichende Steuerschlüssel je im Vorgang
verwendeter Steuergruppe eingetragen werden.
Releasenote Kategorie:
Ticket: 732051[35213]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Artikelstamm [ARS]
Variante: Standard
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35213, 732051

---

## Abstürze bei Vorgangskopie beseitigt

Abstürze bei Vorgangskopie beseitigt
Kunden hatten gelegentlich Abstürze bei der Nutzung
der Vorgangskopie. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 735121[35280]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: Alle Vorgangsanwendungen
Variante: -
Funktion/Report: Kopieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.3, 35280, 735121

---

## Preiskonditionen

Preiskonditionen
In der Anwendung Preiskonditionen [PRI] wird auf dem
Tabreiter "Allgemein", in der Tabelle "individuelle Preise", das Feld
"Brutto" mit dem im Kundenstamm hinterlegtem Kennzeichen für Bruttorechnung
vorbelegt.
Releasenote Kategorie:
Ticket: 736546[35452]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: PRI
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 35452, 736546

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

## THG-Werte werden automatisch nachgeladen bei manuellen Anbauland

THG-Werte werden automatisch nachgeladen bei manuellen Anbauland
Bei Kunden mit sehr vielen Artikeln hat das
automatische Nachladen nach dem Ändern vom Anbauland während der Belegerfassung
nicht funktioniert. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 738636[35721]
Version: 9.0.2402.3
Datum: 08.11.2024
Anwendung: n/a
Variante: n/a
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.3, 35721, 738636

---

## Kundenbanken

Kundenbanken
Existiert eine Bankleitzahl im Bankenstamm mehrfach,
dann konnte anhand der IBAN keine eindeutige Bank bestimmt werden und die Felder
blieben leer. Das wurde so geändert, dass die F3-Auswahl der Bank sofort
geöffnet wird und nur die Banken mit dieser Bankleitzahl aufgelistet werden.
Releasenote Kategorie:
Ticket: 740047[35968]
Version: 9.0.2501.5
Datum:
Anwendung: KUBA, KU
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35968, 740047

---

## Fallback auf Standard-Mailadresse bei eRechnung

Fallback auf Standard-Mailadresse bei eRechnung
Emailadresse aus dem Anschriftenstamm wird als
Rückfall gezogen, sollte das Email Feld "KundElectronicAdress" des XRE Reiters
im Kunden nicht gefüllt sein.
Releasenote Kategorie:
Ticket: 740566[36059]
Version: 9.0.2402.8
Datum: 04.03.2025
Anwendung: [KU]
Variante: STD
Funktion/Report: -
Weitere Informationen
Tags:
Releasenote, 9.0.2402.8, 36059, 740566

---

## Mailversand bei aktualisierter Mailadresse

Mailversand bei aktualisierter Mailadresse
Während der Vorgangserfassung speichert sich Referenz-ERP
die aktuellen Anschriften. In den Anschriften werden auch die Mailadressen
gespeichert. Stellte man nach Erfassung eines Vorganges fest, dass die
Mailadresse nicht korrekt war, war es mit hohem Aufwand verbunden, die korrekte
Mailadresse in dem Vorgang zu hinterlegen. Wird nun der SPA 1161 auf "Ja"
gestellt, so werden beim Mailversand immer die aktuellen Mailadressen aus dem
jeweiligen Kunden gezogen, ohne das weitere Maßnahmen notwendig sind.
Releasenote Kategorie:
Ticket: 742206[36224]
Version: 9.0.2501.5
Datum:
Anwendung: Rechnung
Variante: Standard
Funktion/Report: Belegversand
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36224, 742206

---

## Kundenreferenz in der eRechnung

Kundenreferenz in der eRechnung
Im Feld BT-46 wird für gewöhnlich die Gegennummer
eingetragen, die im Kundenstamm hinterlegt ist. Sollte diese leer sein, so wird
die Kundennummer des Kunden ausgegeben.
Releasenote Kategorie:
Ticket: 743259[36285]
Version: 9.0.2402.10
Datum: 04.03.2025
Anwendung: Rechnung
Variante: Standard
Funktion/Report: eRechnung exportieren
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.10, 36285, 743259

---

## USTId-Prüfung

USTId-Prüfung
Die Prüfung aller UST-IDs im Kundenstamm führte zu
einer Fehlermeldung. Dies wurde berichtigt.
Releasenote Kategorie:
Ticket: 744146[36384]
Version: 9.0.2501.5
Datum:
Anwendung: Kundenstamm
Variante: [KU]
Funktion/Report: USt-IdNr alle prüfen
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36384, 744146

---

## Mailadressen Datenspeicherung

Mailadressen Datenspeicherung
Beim Pflegen der E-Mail-Adresse im Kundenstamm konnte
es vorkommen, dass die Mailadresse nicht korrekt gespeichert wurde. Das
Verfahren wurde überarbeitet.
Releasenote Kategorie:
Ticket: 743580[36433]
Version: 9.0.2501.5
Datum:
Anwendung: Kundenstamm, Anschriftstamm
Variante: [KU] - [ANSCH]
Funktion/Report: F5
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36433, 743580

---

## Spea kunden mit Auslandsbank

Spea kunden mit Auslandsbank
Aber SEPA- Version 3.7 hat sich für Kunden, der IBAN
nicht mit DE beginnt und deren BIC mit übertragen wird, eine Änderung ergeben,
die in Referenz-ERP integriert wurde. Die Elemente BIC heißen jetzt BICFI : Das
Element  aus V03 wurde in V08/V09 durchgängig in  umbenannt
(siehe  und ).
Releasenote Kategorie:
Ticket: 743757[36482]
Version: 9.0.2501.5
Datum:
Anwendung: ZHB
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36482, 743757

---

## Kundenwechsel im Vorgang

Kundenwechsel im Vorgang
Beim Ändern der Kundennummer in einem Vorgang kann
über das Behandlungsschema [BEH] unter anderem definiert werden, wie mit
vorhandenen Versandadressen umgegangen wird.  Wenn im Behandlungsschema
"verwerfen" gewählt wird, wird die Versandanschrift beim Kundenwechsel nun auf 0
gesetzt.  Zuvor wurde die erste Versandadresse des neuen Kunden vorbelegt,
auch wenn die Lieferung an den Hauptkunden gehen sollte.
Releasenote Kategorie:
Ticket: 737408[36543]
Version: 9.0.2501.5
Datum:
Anwendung: Vorgangswesen
Variante: -
Funktion/Report: Kundenwechsel
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36543, 737408

---

## Archiv-Mail Versand Maske EPAs korrigiert

Archiv-Mail Versand Maske EPAs korrigiert
In der Anwendung Formulararchiv kann man mit der
Funktion E-Mail Senden an die Maske zum erneuten Emailversand öffnen.Dort gibt
es 5 EPAs.Alternative zusätzliche Adresse 1 ( 0 = keine, sonst ADRESSID )
Alternative zusätzliche Adresse 2 ( 0 = keine, sonst ADRESSID ) Alternative
zusätzliche Adresse 3 ( 0 = keine, sonst ADRESSID ) Alternative zusätzliche
Adresse 4 ( 0 = keine, sonst ADRESSID ) Alternative zusätzliche Adresse 5 ( 0 =
keine, sonst ADRESSID ) Versandprofil  Diese EPAs konnte man einrichten,
wurden aber nicht unter allen Umständen korrekt ausgewertet. Dies wurde
korrigiert.
Releasenote Kategorie:
Ticket: 730466[36576]
Version: 9.0.2501.8
Datum:
Anwendung: [FA] Formulararchiv
Variante: Formulararchiv
Funktion/Report: E-Mail Senden An
Weitere Informationen
Tags:
Releasenote, 9.0.2501.8, 36576, 730466

---

## eRechnung: Lieferantensuche

eRechnung: Lieferantensuche
Die Importstatus von eRechnungsimport wurde um
"Kundensuche durchlaufen" und "Kundensuche erfolgreich" bzw. "Kundensuche
fehlgeschlagen" ergänzt.  Wird im Profil eingestellt, dass eine Kundensuche
nicht zum Abbruch führt, so endet der Import bei fehlgeschlagener Kundensuche
mit "Import erfolgreich"
Releasenote Kategorie:
Ticket: 745812[36724]
Version: 9.0.2501.5
Datum:
Anwendung: eRechnung
Variante: Import Vorgänge
Funktion/Report: [XRE]
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36724, 745812

---

## Sonderzeichen in Emailadresse

Sonderzeichen in Emailadresse
Zeichen wie '&', '^' und weitere werden
innerhalb einer Emailadresse korrekt verarbeitet.
Releasenote Kategorie:
Ticket: 744563[36732]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Kunde, Anschrift
Variante: STD
Funktion/Report: Email
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 36732, 744563

---

## eRechnung: UST-Id Seller/Buyer

eRechnung: UST-Id Seller/Buyer
Die Umsatzsteuer-Id des Lieferanten wurde fälschlicher
Weise beim Kunden gespeichert. Dadurch schlug die Lieferantensuche fehl.
Dies wurde behoben.
Releasenote Kategorie:
Ticket: 745812[36729]
Version: 9.0.2501.5
Datum:
Anwendung: eRechnung
Variante: -
Funktion/Report: [XRE]
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 36729, 745812

---

## Tourauswahl in der Vorgangserfassung

Tourauswahl in der Vorgangserfassung
Tourenauswahl in der Vorgangserfassung
Tourenauswahl ohne Kundenzuordnung Es ist nun möglich, bei der Erfassung eines
Vorgangs auch Touren auszuwählen, die nicht kundenspezifisch sind.
Voraussetzung: Der Steuerparameter 1162 – Zeige alle Touren zum Lieferdatum an
muss auf Ja gesetzt sein.  Vorbelegung der Tourstationen bei neuer
Gültigkeit Bei der Neuanlage eines Gültigkeitszeitraums für eine Tour kann jetzt
standardmäßig eine Tourstation vorbelegt werden – sofern eine bestehende
Stationsliste nicht als Vorlage verwendet wird. Voraussetzung: Der
Steuerparameter 1163 – Vorbelegung der Tour-Stationsliste bei neuer Gültigkeit
muss auf Ja gesetzt sein. Vorbelegte Felder: Nr., Prio, Sperr
Releasenote Kategorie:
Ticket: 747072[37117]
Version: 9.0.2501.6
Datum:
Anwendung: Lieferscheinbearbeitung
Variante: Lieferscheinbearbeitung
Funktion/Report: Lieferschein erfassen
Weitere Informationen
Tags:
Releasenote, 9.0.2501.6, 37117, 747072

---

## Zertifikatsübersicht: Archivanzeige in Nachhaltigkeitskundenübersicht

Zertifikatsübersicht: Archivanzeige in Nachhaltigkeitskundenübersicht
In der Anwendung Nachhaltigkeit-Kundenübersicht
[NAKUE] wurde in der Zertifikatsübersicht die Archivfunktion
angebunden.
Releasenote Kategorie:
Ticket: 743207[37122]
Version: 9.0.2501.6
Datum:
Anwendung: Nachhaltigkeit-Kundenübersicht [NAKUE]
Variante: -
Funktion/Report: Archiv anzeigen
Weitere Informationen
Tags:
Releasenote, 9.0.2501.6, 37122, 743207

---

## SEPA - Empfänger und Zeichensatz

SEPA - Empfänger und Zeichensatz
Das Feld des Empfängers/Zahlungspflichtigen in den
Kundenbanken wurde auf 70 Zeichen erweitert und im Kunden/Lieferantenstamm wurde
ein weiteres Feld Zahlungsempfängers/Zahlungspflichtiger hinzugefügt.  Ist
in der Kundenbank kein Wert eingetragen, dann wird das neue Feld aus dem
Kundenstamm verwendet, ist dies nicht gepflegt, dann wird wie bisher die
Kundenbezeichnung verwendet.
Releasenote Kategorie:
Ticket: 749003[37833]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: --
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.5, 37833, 749003

---

## Versandanschriften über Anschrift [ANSCH] löschen

Versandanschriften über Anschrift [ANSCH] löschen
In der Anwendung [ANSCH] konnten bislang keine
Kunden-Versandadressen gelöscht werden. Analog zu der Anwendung
Kundenversandanschriften [KUVS] kann dies nun auch in der Anwendung Anschriften
[ANSCH] Variante Versandanschriften ausgeführt werden.
Releasenote Kategorie:
Ticket: 749938[38225]
Version: 9.0.2502.7
Datum:
Anwendung: Anschriften [ANSCH]
Variante: Versandanschriften
Funktion/Report: löschen
Weitere Informationen
Tags:
Releasenote, 9.0.2502.7, 38225, 749938

---

## Änderung einer Anschrift

Änderung einer Anschrift
Bei der Änderung einer Anschrift wurden bislang die
zugewiesenen E-Mail Adressen beim Speichern nicht korrekt übernommen.Dieses
Verhalten wurde behoben: Ab sofort werden beim Ändern und anschließenden
Speichern eines Anschriftensatzes alle zugehörigen E-Mail Adressen korrekt
übernommen.
Releasenote Kategorie:
Ticket: 752917[39211]
Version: 9.0.2502.9
Datum:
Anwendung: Anschriften
Variante: Anschriften
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 39211, 752917

---

## Variante Betriebsstätten

Variante Betriebsstätten
Felder
Filialnummer
Nummer der Filiale
Bezeichnung
Filialbezeichnung
Ident-Untergrenze
Zeigt die untere Grenze des für
      diese Betriebsstätte festgelegten Ident-Bereiches.
Ident-Obergrenze
Zeigt die obere Grenze des für diese
      Betriebsstätte festgelegten Ident-Bereiches.
Zentrale
Zeigt an ob Betriebsstätte eine
      Zentrale ist.
Filialnummer Zentrale
Zeigt die Filialnummer der
      übergeordneten Betriebsstätte.
Untergeordnete
      Betriebsstätte
Zeigt eine Liste der untergeordneten
      Betriebsstätten.
Funktionen
Pflege-Funktionen
Stammsatz neu, Stammsatz ändern,
      Stammsatz löschen
Replikationsadressen
Partner
Bearbeiten von zugeordneten
      Betriebsstätten der ausgewählten Betriebsstätte
Replikationsadressen Partner
Publikationen
Hinzufügen oder entfernen von
      Publikationen für die ausgewählte Betriebsstätte.
Erstellte
      Publikationen
Datenempfänger
Berechtigungen
Bereiche/Profile
Filialnummer
Ermöglicht Bereichssuche nach
      Filialnummern
-
von
-
bis

---

## Betriebsstätten/Filialen

Betriebsstätten/Filialen
Hauptmenü
Filialsystem
Stammdaten
Betriebsstätten/Filialen

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

## Anschreiben (EPA ANSCHREIBEN)

Anschreiben (EPA ANSCHREIBEN)
Bezeichnung
Standardwert
Erklärung
Archivgruppe zur Eingrenzung der F3
      Auswahl
0
Tabelle oder View der
      Serienbriefgrundlage
Anschriftstamm
Sicherheitsabfrage beim
      Verlassen
Nein
IP
      Adresse des SMTP Gateways
Vorschau speichert ins
      Archiv
Ja

---

## Auswahl pro Kunde (EPA BEBERICH)

Auswahl pro Kunde (EPA BEBERICH)
Bezeichnung
Standardwert
Erklärung
Besuchsintervall (Tage)
60
Bezeichnung Spalte 1 Feld
      1
Feld1
Bezeichnung Spalte 1 Feld
      2
Feld2
Bezeichnung Spalte 1 Feld
      3
Feld3
Bezeichnung Spalte 1 Feld
      4
Feld4
Bezeichnung Spalte 1 Feld
      5
Feld5
Bezeichnung Spalte 1 Feld 6
      (Text)
Feld6
Bezeichnung Spalte 1 Feld 7
      (Text)
Feld7
Bezeichnung Spalte 2 Feld
      1
Nachkomma1
Bezeichnung Spalte 2 Feld
      2
Nachkomma2
Bezeichnung Spalte 2 Feld
      3
Nachkomma3
Bezeichnung Spalte 2 Feld
      4
Nachkomma4
Bezeichnung Spalte 2 Feld
      5
Nachkomma5
Bezeichnung Spalte 3 Feld
      1
Datum1
Bezeichnung Spalte 3 Feld
      2
Datum2
Bezeichnung Spalte 3 Feld
      3
Datum3
Rollbox entfernen
Rollbox
Geben Sie hier die Größe der
      Registerkarte an Breite mal Höhe
Ändert die Größe der Registerkarte
      auf der Maske

---

## Mobile Datenerfassung (EPA BT_POCKETPC)

Mobile Datenerfassung (EPA BT_POCKETPC)
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
Vorgangsklasse
600
Vorgangsunterklasse
0

---

## MaskenTitel (EPA EWWBD_EXPORT)

MaskenTitel (EPA EWWBD_EXPORT)
Bezeichnung
Standardwert
Erklärung
Tragen Sie hier den SMTP Port
      ein.
25
Tragen Sie hier die Absender
      E-Mailadresse ein.
Tragen Sie hier die SMTP Server
      IP-Adresse ein.

---

## Konteninformation (EPA FIKOINF)

Konteninformation (EPA FIKOINF)
Bezeichnung
Standardwert
Erklärung
Obligokunden in einer Itembox
      abfragen?
Nein
Bei
      Obligokunden bei ESC in die Auswahl springen?
Nein
Beim
      Betreten der Maske im Feld Kontonummer starten
Nein
Das
      erste Feld der Maske ist die Jahrnummer. Im Normalfall bestätigt man
      jedoch immer die vorgeschlagene Nummer (aktuelles Jahr). Daher ist es
      sinnvoll im Feld Kontonummer zu starten. Dazu muss hier Ja eingetragen
      werden
Nicht bewegte
      Konten beim Blättern überspringen?
Nein
Man
      kann mit den Blätter-Button zwischen Konten hin und herspringen. Steht
      dieser Einrichterparameter auf
Ja
, so werden die Konten, die keine
      Bewegungen im aktuellen Jahr haben, beim Blättern übersprungen. Gibt man
      die Kontonummer manuell ein, so werden die Werte nach wie vor unabhängig
      von diesem Einrichterparamter angezeigt.

---

## Kontoblätter erstellen (EPA FIKOBLTT)

Kontoblätter erstellen (EPA FIKOBLTT)
Bezeichnung
Standardwert
Erklärung
Kokore auch für Konten ohne
      Bewegungen erstellen?
Nein
Wenn
      auch leere Kokores erstellt werden sollen, dann muss hier ein Ja
      eingetragen werden.
Kokore-Kennzeichen ( Kundenstamm )
      ignorieren?
Ja
Im
      Kundenstamm existiert ein Kennzeichen, das besagt, ob das Kokore für
      diesen Kunden gedruckt werden soll. Wenn dieses Kennzeichen nicht korrekt
      gepflegt wurde, kann man hier die Prüfung abschalten. Es werden dann immer
      alle Kunden zugelassen.
Kokore auch pro Periode mehrfach
      erstellen?
Nein

---

## ZHE Zahlungen erstellen (EPA FIZAHLER)

ZHE Zahlungen erstellen (EPA FIZAHLER)
Bezeichnung
Standardwert
Erklärung
Mehrfache Belegauswahl
      zulassen?
Nein
Wir
      hier ein
Ja
eingetragen, so kann man für einen ausgewählten Kunden
      in der
F3
-Belegauswahl sofort
      mehrere Belege markieren, die dann zu dem Zahlungsbeleg zugeordnet
      werden.
Betragsrundung bei
      Habenbelegen
Hier
      kann man eintragen auf wie viele Stellen die Zahlung gerundet werden
      soll.
Stichtag mit Periode
      prüfen
kein
      Test
Wird
      hier eine Art der Prüfung angegeben, so wird beim Betreten der
      Erfassungsmaske zuerst die Periode abgefragt. Das Datum, welches man
      anschließend als Stichtag angibt wird dann entsprechend der Einstellung
      getestet.
Skonto trotz Datumsüberschreitung
      festlegen
Nein
Wird
      hier
Ja
eingetragen, dann wird Skonto immer gezogen/gewährt, ohne
      dass das Datum berücksichtigt wird.
Betragsrundung bei
      Sollbelegen
Hier
      kann man eintragen auf wie viele Stellen die Zahlung gerundet werden
      soll.

---

## Preispfleger individuelle Preise (EPA HINWEIS_LISTENPREISFUNKTION)

Preispfleger individuelle Preise (EPA HINWEIS_LISTENPREISFUNKTION)
Bezeichnung
Standardwert
Erklärung
Soll
      auf die Listenpreisfunktion in der Kundenauswahlliste hingewiesen
      werden?
Ja
Beim
      Speichern eines Listenpreisprofiles soll eine private Funktion in der
      Optionbox der Auswahlliste, von der aus der Preispfleger aufgerufen wird,
      angelegt werden mit der es ermöglicht werden soll, Listenpreise zu
      pflegen.
Dieser Hinweis kann ein oder
      ausgeschaltet werden, da der Hinweis auch eingeblendet werden kann, wenn
      die Funktion bereits existiert.

---

## Kontraktdispositionen (EPA KDISPO)

Kontraktdispositionen (EPA KDISPO)
Bezeichnung
Standardwert
Erklärung
Bestellvorgänge mit
      erzeugen
Nein
Ufld
      Textfeldnummer für KTRDINr.
0
Vorgangsunterklasse
      Kunde
0
Vorgangsunterklasse
      Lieferant
0
Unterklasse Spediteur
0

---

## Aktionärverwaltung - Aktionäre (EPA KUNDENMITGLIED)

Aktionärverwaltung - Aktionäre (EPA
KUNDENMITGLIED)
Bezeichnung
Standardwert
Erklärung
Verhalten bei Doppelter
      Aktionärsnummer
Fehler
Aktionärsnummer ist gleich der
      Kundennummer
Ja

---

## Wiedervorlage Kunden per Mail (EPA KUNDWIVL)

Wiedervorlage Kunden per Mail (EPA
KUNDWIVL)
Bezeichnung
Standardwert
Erklärung
Bitte geben Sie Verzeichnis und Name
      Ihrer Lotusdatenbank ein.
Bitte geben Sie Verzeichnis und Name
      der Kontaktedatenbank ein.
names.nsf
Bitte geben Sie den
      Lotusdatenbankserver der Kontakte ein.
Bitte geben Sie Ihren
      Lotusdatenbankserver ein.

---

## MaskenTitel (EPA PVARRAY)

MaskenTitel (EPA PVARRAY)
Bezeichnung
Standardwert
Erklärung
autom. Kunde vorbelegen
Nein

---

## Kundenbanken (EPA TBKUBA)

Kundenbanken (EPA TBKUBA)
Bezeichnung
Standardwert
Erklärung
Bestehende Bankverbindungen dürfen
      nicht mehr geändert werden.
Nein
Um
      eine Nachverfolgung der einmal eingerichteten Bankverbindung zu
      gewährleisten, kann man hier einstellen, dass Banken nicht geändert,
      sondern nur neu hinzugefügt werden können.
Im
      autom. Zahlungsverkehr bei diversen Kunden die Bankverbindung nicht
      speichern
Nein
Um
      zu verhindern, dass bei einem „Diversen“ Kunden tausende von
      Bankverbindungen hinterlegt werden, kann man hier die Speicherung
      abschalten. Siehe auch automatischer
Zahlungsverkehr
.
Im
      autom. Zahlungsverkehr Sperre und Ablaufdatum bei manueller Auswahl
      ignorieren
Nein
Wenn
      für Zahlungsvorschläge die Bank manuell geändert wird, so wird im
      Normalfall die Sperre und das Ablaufdatum berücksichtigt, so dass nur
      aktive Bankverbindungen verwendet werden können. Stellt man diesen
      Parameter auf Ja, könne auch Banken, die gesperrt sind ausgewählt
      werden.

---

## Kunden (EPA TBKUNSTB)

Kunden (EPA TBKUNSTB)
Bezeichnung
Standardwert
Erklärung
Bildschirm für Addon
      aufbauen
Nein
Veraltet, da Addon nicht mehr
      unterstützt wird.
Steuergruppe darf nicht 0
      sein
Fehler
Steuergruppe 0 ist für die
      Finanzbuchhaltung / Sachkonten vorgesehen. Daher sollte sie im Kundenstamm
      nicht verwendet werden.
Als
      Vorlage nur Musterkunden auswählbar
Ja
Man
      kann neben Musterkunden auch beliebige Kunden als Vorlage verwenden. Dann
      muss hier ein Ja eingetragen werden.
Bei
      Zinsgruppenänderung auf vorhandene Belege prüfen?
Nein
Es
      wird bei Einstellung „Ja“ dann geprüft, ob Belege existieren und eine
      entsprechende Warnmeldung ausgegeben.
Umsatzsteuer-ID nach Eingabe
      automatisch aktivieren?
Nein
Gibt
      an, ob das „Aktiv“-Feld der Umsatzsteuer-ID automatisch auf „Ja“ gesetzt
      wird, wenn eine neue Umsatzsteuer-ID eingegeben wird
Sollen die Felder für die
      Zertifikatszusatzinformationen angezeigt werden?
Nein
Bestimmt, die Felder für die
      Zusatzinformationen der Zertifikate angezeigt werden sollen oder
      nicht.

---

## Kundenbearbeitung (EPA VORGANG_KUNDENBRB)

Kundenbearbeitung (EPA
VORGANG_KUNDENBRB)
Bezeichnung
Standardwert
Erklärung
Prozedur, welche nach erfolgreichem
      Ändern aufgerufen werden soll.

---

## Mail-Notiz (EPA VORGWIVL)

Mail-Notiz (EPA VORGWIVL)
Bezeichnung
Standardwert
Erklärung
Bitte geben Sie Verzeichnis und Name
      Ihrer Lotusdatenbank ein.
Bitte geben Sie Verzeichnis und Name
      der Kontaktedatenbank ein.
names.nsf
Bitte geben Sie den
      Lotusdatenbankserver für Ihre Kontakte ein.
Bitte geben Sie Ihren
      Lotusdatenbankserver ein.

---

## Bearbeitung

Bearbeitung
Hauptmenü
Filialsystem
Bearbeitung
Bearbeitungsrecht Vorgänge Ware
Kundenzugehörigkeit zu Filialen

---

## Gebiete

Gebiete
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Gebietsstamm [GEB]
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Gebiete
Hier richten Sie Gebiete für den Versand ein. Dies
können z.B. (Bundes-)Länder, Landkreise oder Verkaufsbezirke sein.
Stammdatenpflege
Kunden-/Lieferanten  Kundenstamm
[KU]
Im Kundenstamm wird auf der Registerkarte Klassen das
(Verkaufs-)Gebiet festgelegt in das die Ware für diesen Kunden versendet werden
soll.

---

## Individuelle Preise

Individuelle Preise
Hauptmenü
Stammdatenpflege
Kunden / Lieferanten
Kundenstamm
Direktsprung
[KU]
Hauptmenü
Stammdatenpflege
Kunden / Lieferanten
Lieferanten
Direktsprung
[LF]
Hauptmenü
Stammdatenpflege
Artikelstamm
Artikel
Direktsprung
[AR]
Ein
individueller Preis
, oder eine mengenabhängige
Preisstaffel, werden am Kreuzungspunkt aus Kunde und Artikel gepflegt. Um nicht
für jeden Kunden und jeden einzelnen Artikel eine solche Preispflege vornehmen
zu müssen, werden Kunden in
Preisklassen
und Artikel in
Preisgruppen
organisiert. Die Zuordnung erfolgt
in den jeweiligen Anwendungen zur Stammdatenpflege, hierbei getrennt für eine
Verkaufs- und eine Einkaufs-Seite. Ein Kontokorrentkunde der gleichzeitig Kunde
und Lieferant sein kann, hat üblicherweise zwei Preisklassen (Einkauf und
Verkauf). Ähnliches gilt für einen Artikel der aktiv gehandelt wird, er benötigt
zwei Preisgruppen (auch hier Einkauf und Verkauf).
Individuelle Preise können auf zwei Arten gepflegt
werden: über eine Einzelsatzanwendung, bei welcher Daten an einem der oben
beschriebenen Kreuzungspunkte erfasst werden, also für
eine
Kombination
aus Preisklasse
und
Preisgruppe. Wird hingegen eine der fixierten
Dimensionen freigegeben (Preisgruppe frei
à
Artikel frei wählbar
à
Einstieg über den festen
Kunden/Lieferanten oder Preisklasse frei
à
Kunde frei wählbar
à
Einstieg über den festen Artikel)
benötigt man den im folgenden beschriebenen Preisstapelpfleger für individuelle
Preise.
Da eine der Dimensionen variabel ist, werden die Daten
folglich in einer Tabelle dargestellt: für einen gewählten Kunden/Lieferanten
alle – über ihre Preisgruppe – zugeordneten Artikel, oder für einen gewählten
Artikel alle – über ihre Preisklasse – zugeordneten Kunden. Die Laufvariable ist
dann die Zeit, dargestellt über die Zeiträume [gültig ab, gültig bis]. Erfasst
werden die anzuwendende Ab-Menge und die für diese Menge relevanten
Preisinformationen.
Die Bereitstellung der Daten erfolgt über eine auf den
A
[...]


---

## Steueränderung durch Kundennummernänderung

Steueränderung durch Kundennummernänderung
Wird zu einem Kunden gewechselt, der einen
abweichenden Steuersatz hat (z.B. sind EU-Bürger von außerhalb Deutschlands von
der Steuer befreit), so werden alle Steuersätze von den Positionen
heruntergerechnet.
Hierbei gilt folgendes zu beachten:
Preislisten
•
Wird eine Netto-Preisliste verwendet, so wird der Brutto-Preis ohnehin
durch die Addition eines Steuersatzes berechnet und die Neu-Berechnung eines
Bruttopreises mit einem geringeren oder ohne Steuersatz ist simpel.
•
Wird eine Brutto-Preisliste verwendet, so hat dieser Brutto-Preis eine
bereits einkalkulierte Steuer.
o
Ist der verwendete Steuersatz
unbekannt, der dieser Preisliste zugrunde liegt. In diesem Fall wird der
Steuersatz vom Bruttopreis abgezogen, der sich der Steuergruppe des Kunden und
Steuerschlüssel des Artikels ergibt.
o
In der Preisliste kann und
sollte jedoch der verwendete Steuersatz angegeben werden. Verwenden Sie dazu den
Pfleger für
Preislistenbezeichnungen
(Preise/Konditionen
Konstanten der Preispflege
Preislistenbezeichnungen)
Absolute Rabatte/Zuschläge
Es wird empfohlen an dieser Stelle mit relativen
Rabatten also prozentualem Anteil zu arbeiten. Absolute Werte werden nicht mit
einem Steuersatz berechnet. Sie sind absolut. Das bedeutet, dass die für den
„Normalkunden“ erfassten 10€-Rabatt auch ein Rabatt für den EU-Bürger außerhalb
Deutschlands bedeuten.
So wird der Betrag voll vom Endbetrag abgezogen. Das
führt u.U. dazu, dass dem Kunden ungewollt ein größerer Rabatt als beabsichtigt
gewährt wird.

---

## Steueränderung durch Kundennummernänderung

Steueränderung durch Kundennummernänderung
Wird zu einem Kunden gewechselt, der einen
abweichenden Steuersatz hat (z.B. sind EU-Bürger von außerhalb Deutschlands von
der Steuer befreit), so werden alle Steuersätze von den Positionen
heruntergerechnet.
Hierbei gilt folgendes zu beachten:
Preislisten
•
Wird eine Netto-Preisliste verwendet, so wird der Brutto-Preis ohnehin
durch die Addition eines Steuersatzes berechnet und die Neu-Berechnung eines
Bruttopreises mit einem geringeren oder ohne Steuersatz ist simpel.
•
Wird eine Brutto-Preisliste verwendet, so hat dieser Brutto-Preis eine
bereits einkalkulierte Steuer.
o
Ist der verwendete Steuersatz
unbekannt, der dieser Preisliste zugrunde liegt. In diesem Fall wird der
Steuersatz vom Bruttopreis abgezogen, der sich der Steuergruppe des Kunden und
Steuerschlüssel des Artikels ergibt.
o
In der Preisliste kann und
sollte jedoch der verwendete Steuersatz angegeben werden. Verwenden Sie dazu den
Pfleger für
Preislistenbezeichnungen
(Preise/Konditionen
Konstanten der Preispflege
Preislistenbezeichnungen)
Absolute Rabatte/Zuschläge
Es wird empfohlen, an dieser Stelle mit relativen
Rabatten (also prozentualem Anteil) zu arbeiten. Absolute Werte werden nicht mit
einem Steuersatz berechnet. Sie sind absolut. Das bedeutet, dass die für den
„Normalkunden“ erfassten 10€-Rabatt auch ein Rabatt für den EU-Bürger außerhalb
Deutschlands bedeuten.
So wird der Betrag voll vom Endbetrag abgezogen. Das
führt u.U. dazu, dass dem Kunden ungewollt ein größerer Rabatt als beabsichtigt
gewährt wird.

---

## Änderung der Kundennummer

Änderung der Kundennummer
In einem erfassten Beleg kann die Kundennummer
nachträglich geändert werden. Daran sind jedoch bestimmte Voraussetzungen
geknüpft.

---

## Einrichtung des Filialsystems

Einrichtung des
Filialsystems
Vorbereitendende Schritte
Identifikationskonzept
Folgende Fragen müssen geklärt werden:
-
Welche Betriebsstätte darf welche Artikelnummern, Kundennummern, Preisgruppen,
etc. generieren (z.B. Zentrale)?
-
Wie ist die Primary Key Behandlung der in den Publikationen enthaltenen
Publikationsartikel organisiert (z.B. Ident über Ident-Tabelle oder GUID oder
sonst wie einzigartig vergebener Schlüssel)?
o
Sind Publikationsartikel
vorhanden, die der Einzigartigkeit in der Primary Key-Behandlung widersprechen,
so muss dies abgestellt werden. Dies kann durch entfernen des
Publikationsartikels aus der Publikation erreicht werden oder es muss eine
Änderung der Behandlung vorgenommen werden.
Einrichtung der Filialstruktur
[BST]
-
Einrichtung der
Betriebsstätten/Filialen
-
Ident-Kontingente
für die
einzelnen Betriebsstätten/Filialen einrichten
-
Mandantenstamm
Einrichtung Stammdaten
-
Einrichtung sämtlicher Stammdaten und steuernder Elemente überarbeiten.
Vollständig zentralisierte Einrichtungen sämtlicher Stammdaten insbesondere z.B.
auch
o
Bedienerstamm
o
Bediener
(neue Bediener anlegen oder
Bediener clonen
)
o
Bedienerklassen
für neue Filialen
einrichten und den Bedienern zuordnen
o
Formulare
o
Nummernkreise
o
Drucker
o
Inventurgruppen
o
Vorgangsunterklassen
(insbes. für
Barverkauf)
vollständig und
Betriebsstätten-spezifisch vornehmen.
Artikeleinrichtung
-
Läger und Zuordnungen zu Filialen
-
Artikel für Filialläger anlegen
Vorbereiten
der Infrastruktur
Einrichten der Verzeichnisstruktur für den Austausch
der SQL Remote Nachrichten und der Log-Dateien, sowie für etwaig benötigte
Aufgaben innerhalb der Replikation (Datenbank-Extraktion, FTP, usw.).
Im Aeins-Verzeichnis muss folgendes Verzeichnis
erstellt werden:
..\Aeins\dbrexp
Folgende Aufgaben sind zusätzlich notwendig, wenn
zuvor ein Vorläufer des Filialsystems in Betrieb war:
Vorarbeiten Filialen
-
Aufträge, Lieferscheine fakturieren
-
Export
[...]


---

## Tour

Tour
Auf der Registerkarte „Tour“ befinden sich folgende
Bereiche, die auch über die
Tourverwaltung [TOUR]
zu pflegen sind:
Einfache Tourzuordnung
Anrufliste
Komplexe Tourzuordnung
Einfache
Tourzuordnung
Ein Kunde kann einer festen Tour/Station zugeordnet
werden. Dieses Kennzeichen kann in Listen etc. ausgewertet werden. Es handelt
sich also um ein reines Auswertungskennzeichen.
Feld
Beschreibung
Tour
Nummer der Tour
Station
Nummer der Station
Anrufliste
Feld
Beschreibung
Nr.
Nummer der Anrufliste
F3-Auswahl aus allen vorhandenen
      Anruflisten
Bezeichnung
Bezeichnung der
      Anrufliste
Tag
Wochentag
Uhr
Hier
      kann die Uhrzeit angegeben werden.
Komplexe
Tourzuordnung
Feld
Beschreibung
Tournummer
Nummer der Tour
Bezeichnung
Bezeichnung der Tour
Tag
Geplanter Wochentag der
      Tour
Station
Nummer der Station
Kommentar
Ein
      Kommentar zur Station

---

## Kunden-Übernahme (???) zulässig(SPA 100)

Kunden-Übernahme (???) zulässig(SPA 100)

---

## Auto Refresh im Scanner einstellen (SPA 1006)

Auto Refresh im Scanner einstellen (SPA 1006)
Soll der Scanner in zyklischen Intervallen ein REFRESH
Kommando abgeben, um automatisiert den Bildschirm zu aktualisieren, kann
IP-Adressenbezogen dieser Parameter gesetzt werden. Ein Intervall von 0 Sekunden
löst kein REFRESH aus, ein Intervall > 0 löst nach n Sekunden ein REFRESH der
Scanner-Bildschirms aus.

---

## UstID Prüfung Datenprozedur (SPA 1011)

UstID Prüfung Datenprozedur (SPA 1011)
Der Steuerparameter ermöglicht die Privatisierung der
Adressaufbereitung. Als Standardprozedur dient (AMIC_UStIDPruefAdressen
).
Somit ist durch die Verkettung weiterer Spalten eine
Individualisierung der Adressprüfung realisierbar.

---

## Kunden-Nullsetzung zulässig(SPA 101)

Kunden-Nullsetzung zulässig(SPA 101)

---

## Uhrzeitorientierte Zeiterfassung (SPA 1049)

Uhrzeitorientierte Zeiterfassung (SPA 1049
)
Hier kann festgelegt werden ob die Zeiterfassung bei
Kunden oder Lieferanten auf Basis einer Start- und Endzeit (Ja) oder Basis einer
angegebenen Zeitspanne erfolgen soll (Nein).

---

## UStId-Prüfung im Vorgang (SPA 1062)

UStId-Prüfung im Vorgang (SPA 1062)
Im Vorgang kann bei EU-Auslands-Kunden/Lieferanten die
UmsatzsteuerID asynchron (also nebenläufig) im Vorgang geprüft werden, wenn dies
in diesem Steuerparameter eingeschaltet wird.

---

## Kunden-Übernahme (ZG-Kunden) zulässig(SPA 110)

Kunden-Übernahme (ZG-Kunden) zulässig(SPA 110)

---

## Kunden-Tabellen-Übernahme (ZG) zulässig(SPA 111)

Kunden-Tabellen-Übernahme (ZG) zulässig(SPA 111)

---

## Intervall des Workers (SPA 1150)

Intervall des Workers (S
PA
1150)
Mit diesem Steuerparameter wird pro Worker ein
Intervall in 1/10-Sekunden.Schritten eingestellt. Die Voreinstellung eines
Workers, für den kein Intervall definiert ist, wird aus Worker 0 gelesen. Hier
empfiehlt sich der Wert 10 (1 Sekunde).
Dies ist auch der Voreinstellungswert, falls das
Intervall für Worker 0 nicht definiert wurde.

---

## Nachhaltigkeitsprüfung (SPA 1157)

Nachhaltigkeitsprüfung (SPA 1157)
Standard ist „keine Prüfung“
SPA-Einstellung
Zertifikat für Lieferant (bei
      Verkauf Mandantkunde) für Artikel
Anzeige einer
Warnung
Die Warenposition kann
      abgeschlossen werden.
Keine Prüfung
Abgelaufen, ungültig oder nicht
      nachhaltig
Nein
Ja
keine Prüfung
Gültig und nachhaltig
Nein
Ja
weiche Prüfung mit
      Warnhinweis
Abgelaufen, ungültig oder nicht
      nachhaltig
Ja
Ja
weiche Prüfung mit
      Warnhinweis
Gültig und nachhaltig
Nein
Ja
harte Prüfung
Abgelaufen, ungültig oder nicht
      nachhaltig
Ja
Nein
harte Prüfung
Gültig und nachhaltig
Nein
Ja
Wird dieser SPA auf „keine Prüfung“ gestellt, dann
wird nichts überprüft.
Wird dieser SPA auf „weiche Prüfung mit Warnhinweis“
gestellt, dann wird beim Verlassen der Warenpositionsmaske geprüft, ob der für
den Beleg relevante Kunde für den Artikel im Beleg ein gültiges
Nachhaltigkeitszertifikat besitzt. Dies bedeutet, dass man auf dem
Kundenstammpfleger im Tabreiter Zertifikate ein Zertifikat größer gleich 10 hat.
Siehe dem Anwenderformat
AF_NACHHSTAT
.
Wenn kein Nachhaltigkeitszertifikat vorhanden ist, das
Nachhaltigkeitszertifikat den Status 1-9 hat, oder das Gültigkeitsdatum des
Belegs außerhalb des Nachhaltigkeitszertifikates liegt, dann wird eine Warnung
generiert.
Wird dieser SPA auf „harte Prüfung“ gestellt, dann
wird beim Verlassen der Warenpositionsmaske geprüft, ob der für den Beleg
relevante Kunde für den Artikel im Beleg ein gültiges Nachhaltigkeitszertifikat
besitzt.
Neben der Warnung wird dann auch das Verlassen der
Warenpositionsmaske unterbunden und man muss einen anderen Artikel angeben oder
die Warenpositionsaufnahme abbrechen.

---

## Aktuelle Adresse beim Belegversand verwenden (SPA 1161)

Aktuelle Adresse beim Belegversand verwenden (SPA
1161)
Wenn dieser Steuerparameter eingeschaltet wird, dann
werden beim Belegversand Mailadressen aus zwischenzeitlich (seit dem Druck und
der Bereitstellung) geänderten Anschriften aktuell berücksichtigt.
Dies ist notwendig, wenn
Steuerparameter 574 - Anschriften archivieren
gesetzt
ist und die Anschriften im Beleg historisch verbleiben.

---

## Zeige alle Touren zum Lieferdatum an (SPA 1162)

Zeige alle Touren zum Lieferdatum an (SPA 1162)
Einstellung
Bedeutung
Nein
Die
      Tourenauswahl funktioniert wie gewohnt. (Standard)
Ja
Es
      werden alle Tourenangezeigt unabhängig vom gewählten Kunden.

---

## Neue Kundennummer automatisch vorschlagen(SPA 124)

Neue Kundennummer automatisch vorschlagen(SPA 124)
Ja: Bei Anlage neuer Kunden / Lieferanten / ... wird
die Kundennummer aus dem Nummernkreis vorbelegt.
Nein: Bei Anlage neuer Kunden / Lieferanten / ... wird
keine Nummer vorgeschlagen.

---

## Kundeninfo angeschlossen(SPA 131)

Kundeninfo angeschlossen(SPA 131)
Mit diesem Steuerparameter kann die Kundeninformation
aktiviert / deaktiviert werden.

---

## Kundenindividuelle Adressaufbereitung(SPA 136)

Kundenindividuelle Adressaufbereitung(SPA 136)
Mit diesem Steuerparameter kann die kundenindividuelle
Adressaufbereitung mit Adressmasken aktiviert / deaktiviert werden.
Wert
Text
Beschreibung
0
Nein
Hier
      wird eine festgelegte Adressaufbereitung aus dem Urzeiten von Referenz-ERP
      verwendet.
1
Ja
Hier
      wird die kundenindividuelle Adressaufbereitung mittels
Adressmaske
verwendet. Die verwendete
      Maske kann in der
Anschrift
      auf der Registerkarte „Zusätze“
eingetragen und in [KUAN] erstellt
      werden. Bitte beachten Sie, dass mit der Einstellung „Branchen-ERP-DEFAULT“ in der
      Anschrift stets die „Kunden-Default“-Maske (1) verwendet wird.
2
Ja,
      ohne Nationalitätskennz im Inland
Wie
      [1], aber wenn im
Staatstamm
die Zollgruppe auf „Inland“ steht,
      wird unabhängig von der Einrichtung das Post-Länderkennzeichen und der
      Staats-Name nicht in der Anschrift verwendet.

---

## Abweichender Oberkunde aktiv(SPA 151)

Abweichender Oberkunde aktiv(SPA 151)
Bei „Ja“ kann eine automatische Unterscheidung von
Lieferempfänger und Rechnungsempfänger erfolgen.

---

## Zahlungsart maximal wie im Kundenstamm(SPA 164)

Zahlungsart maximal wie im Kundenstamm(SPA 164)
Mittels dieses Parameters kann die
Zahlungsartvorbelegung frei bei der Belegerfassung überschrieben werden.
Ja: Es kann nur eine kleinere Zahlungsart
vorgeschlagen eingetragen werden (Bsp.: Eintrag ist 4, Änderung nur auf 1-3
möglich, nicht auf 5)
Nein: Keine Einschränkung bei der Vergabe.

---

## Umwandlung trotz Liefersperre(SPA 167)

Umwandlung trotz Liefersperre(SPA 167)
Bei „Ja“ kann sichergestellt werden, dass z.B. bereits
erfasste Lieferungen fakturiert werden können, auch wenn der Kunde auf
Liefersperre steht.

---

## Periodensummen-Anzeige Seite 1 KU(SPA 200)

Periodensummen-Anzeige Seite 1 KU(SPA 200)
nur letztes Jahr:
Sollen auf der 1.Seite im Kundenstammpfleger Umsätze
bzgl. Wert und Fibu-Saldo des laufenden Geschäftsjahres angezeigt werden. Diese
errechnen sich aus den Kundensummen.
Gesamt: es werden die Gesamtumsätze angezeigt.
Nein: es wird angezeigt, durch welche
Tastenkombination geblättert werden kann.

---

## Muster-Objekte bei Kunden-Anlage(SPA 216)

Muster-Objekte bei Kunden-Anlage(SPA 216)
Nein: Es wird kein Musterobjekt bei Kundenanlage
erzeugt. Kundennummer: Bei Kundenanlage wird ein Musterobjekt mit Objektnummer =
Kundennummer erzeugt.
Nummernkreis: Für das erzeugte Musterobjekt wird die
nächste freie Nummer gemäß Nummernkreis verwendet.

---

## Global-Zu-/Abschläge mit Kunden-ZuAb-Kl.(SPA 257)

Global-Zu-/Abschläge mit Kunden-ZuAb-Kl.(SPA 257)

---

## Unterklasse mit Lagernummer=Kundennummer(SPA 259)

Unterklasse mit Lagernummer=Kundennummer(SPA 259)

---

## Zahlungsbedingungs-Abhängigkeit(SPA 40)

Zahlungsbedingungs-Abhängigkeit(SPA
40)
Wie soll die Zahlungsbedingung ermittelt werden?
0: normal, d.h. so wie sie im Kundenstamm auf der
Hauptmaske
hinterlegt ist.
1: Haupt-WG, d.h. wie sie im Kundenstamm in der
Maske Zahlungsbedingungen
für
alle unterschiedlichen Hauptwarengruppen individuell hinterlegt werden
kann.
2: Arti-Gr., d.h. sie wird für jeden Artikel aus ihrer
zugeordneten
Artikelgruppe
gezogen.
Zu empfehlen ist in jedem Fall die Verwendung der
Einstellung "normal". Die Verwendung der anderen Einstellungen erfordert die
Erarbeitung organisatorischer Konzepte, wie eine Weiterbehandlung zu erfolgen
hat. Hinsichtlich OP-Verwaltung und Zahlungsverkehr wirkt Fibu-seitig die erste
verwendete Zahlungsbedingung als die Beleg-Zahlungsbedingung.

---

## Vorgangsdruckklasse, wenn Oberkunde ex.(SPA 433)

Vorgangsdruckklasse, wenn Oberkunde ex.(SPA 433)
Hier wird bei existierendem Oberkunden wie folgt
ausgewertet:
gemäß Oberkunde: es wird die Vorgangsdruckklasse des
Oberkunden herangezogen.
gemäß Kunde: es wird die Vorgangsdruckklasse des
Kunden herangezogen.
Außerdem wird das Kennzeichen Belegversand mit den
möglichen Parametern "Nein", "Mit Belegdruck", "Statt Belegdruck" auf der
Kundenstammmaske auf dem Tabreiter Kennzeichen des jeweiligen Kunden laut SPA
ausgewertet.

---

## Kundeninfo-Lizenz(SPA 441)

Kundeninfo-Lizenz(SPA 441)
Lizenz für Kundeninfo.

---

## Versandadresse bei Oberkunde (Umwandlung in RE)(SPA 465)

Versandadresse bei Oberkunde (Umwandlung in RE)(SPA 465)
Wie soll bei Umwandlungen in Rechnungen und Oberkunden
die Versandadresse befüllt werden
0 - sie wird nie gefüllt
1 - sie wird mit der Versandadresse des
Unterkunden
2 - sie wird mit der ersten Versandadresse des
Unterkunden befüllt (oder der  Adresse des Unterkunden wenn die erste
Adresse leer ist)

---

## Versandadresse bei Oberkunden (RE)(SPA 464)

Versandadresse bei Oberkunden (RE)(SPA 464)
Bei zugeordnetem Rechnungsempfänger wird bei
Rechnungen die Versandadresse wie folgt ermittelt: 0- nie füllen
1- mit der Adresse des Unterkunden
2- mit der ersten Versandadresse des Unterkunden.
Ersatzweise mit 1

---

## LGU/ARU/PRO: Lieferantenpartien zulässig(SPA 497)

LGU/ARU/PRO: Lieferantenpartien zulässig(SPA 497)
Partien können exklusiv Kunden oder Lieferanten
zugeordnet werden. Bei „Ja“ dürfen jetzt auch Lieferantenpartien bei
Lager/Artikelumbuchung sowie Produktion herangezogen werden. Bei „Nein“ können
nur Kundenpartien oder freie Partien umgebucht werden.

---

## Erlösklassenermittlung per(SPA 500)

Erlösklassenermittlung per(SPA 500)
Hier wird zugeordnet, welche Erlösklasse beim
Fibuübertrag herangezogen wird. Bisher wurde (wie jetzt auch die
Standardeinstellung) die Erlösklasse des Zahlungspflichtigen genommen. Man kann
alternativ die Erlösklasse des Kunden/Lieferanten oder des Rechnungsemfängers
zuordnen.

---

## Alle Kredite als Summe übernehmen?(SPA 503)

Alle Kredite als Summe übernehmen?(SPA 503)
Im Kundenstamm gibt es die Funktion Kreditvergabe, in
der mehrere Kredite vergeben werden. Die genehmigten Kredite schlagen sich wie
folgt auf das Kreditlimit im Kundenstamm nieder:
Typ
Wert
Nein
Nur
      der am frühesten genehmigte Kredit (Die erste gültige Zeile) bildet das
      Kreditlimit. Das Kreditlimit kann zusätzlich direkt im
      Kunden-/Lieferantenstamm erfasst werden.
Ja
Die
      Summe aller genehmigten Kredite bildet das Kreditlimit. Es werden nur die
      Kredite berücksichtigt, die nicht gelöscht und noch gültig sind. Dabei
      wird die Einstellung der Summierung des Kredittyps
nicht
berücksichtigt. In dieser Einstellung kann man das Kreditlimit nicht mehr
      im Kunden-/Lieferantenstamm pflegen, da nicht geklärt ist, wie sich dieses
      neue Limit auf die einzelnen genehmigten Kredite niederschlagen soll. Im
      Kundenstamm [KU] steht die Funktion „Kreditsummenübertrag“ zur
      Verfügung.
Wenn
      dieser Wert ausgewählt wird, werden einmalig die manuell gepflegten
      Kreditlimite aus dem Kundenstamm in die Krediterfassung
      übernommen.
Mit
      individueller Datenbankprozedur
Es
      muss eine Prozedur mit dem Namen P_IndivKreditLimit zur Bestimmung des
      gesamten Limits existieren. Diese hat als Übergabeparameter die Kundid und
      muss einen Wert vom Typ Numeric zurückliefern. In dieser Ausprägung ist
      das Kreditlimit nicht im Kunden-/Lieferantenstamm änderbar.
Zu beachten
: Wenn diese
      Ausprägung ausgewählt wurde, wird die individuelle Prozedur auch in den
      folgenden Funktionen von Branchen-ERP verwendet:
•
amic_func_KundKredit
•
amic_func_Update_KundKredit
•
AMIC_Kreditlimit
Es
      gibt zusätzlich den SPA 594: „Erm. Kreditlimit mit P_IndivKreditLimit“.
      Ist dieser auf Ja gesetzt, wird im Vorgang ebenfalls diese individuelle
      Datenbankprozedur zur Ermittlung des Kreditlimits verwendet. Möchten Sie
      beim SPA 503 ein abweiche
[...]


---

## Steuergruppe bei Oberkundenwechsel(SPA 541)

Steuergruppe bei Oberkundenwechsel(SPA 541)
Bei „Ja“ wird beim Wechsel des Oberkunden die
Steuergruppe des Oberkunden herangezogen

---

## Anschriften archivieren(SPA 574)

Anschriften archivieren(SPA 574)
Hier legt man fest ob die alte Anschrift nach der
Änderung einer Kunden-Hauptanschrift im Anschriftenpfleger archiviert wird (z.B.
für den Druck alter Rechnungen)
Beim Löschen von Kunden-Versandanschriften wird die
Adressnummer mit einem negativen Vorzeichen versehen, wenn dieser
Steuerparameter auf Ja steht (analog zur Archivierung von
Kunden-Hauptanschriften).

---

## Lager/Versandadresse/Vertreter ignorieren(SPA 575)

Lager/Versandadresse/Vertreter ignorieren(SPA
575)
Bei „Ja“ werden die Informationen Lagernummer,
Versandadresse und Vertretergruppe aus dem aktuellen Objekt nicht in den Vorgang
übernommen.

---

## Leerzeilen bei Adressen entfernen(SPA 586)

Leerzeilen bei Adressen entfernen(SPA 586)
Bei „Ja“ werden leere Zeilen einer Adresse
unterdrückt.

---

## Adressen von unten aufbauen(SPA 587)

Adressen von unten aufbauen(SPA 587)
Bei „Ja“ werden bei der Druckaufbereitung der Adresse
die Daten vom unteren Rand aufgefüllt. Bei „Nein“ erfolgt die Aufbereitung von
oben her.

---

## Lieferanteneintrag bei aut. Belegpartie(SPA 589)

Lieferanteneintrag bei aut. Belegpartie(SPA 589)
„Ja“ bei der automatischen Anlage der Partie in einem
Warenbeleg (Einstellbar in der Unterklasse) wird die Lieferantennummer in die
Lieferantenliste der Partie eingetragen.
„Nein“ der Eintrag entfällt!

---

## Erm.Kreditlimit mit P_IndivKreditLimit(SPA 594)

Erm.Kreditlimit mit P_IndivKreditLimit(SPA 594)
Bei „Ja“ wird das Kreditlimit eines Kunden nicht aus
dem Kundenstamm sondern durch Aufruf der Datenbankfunktion P_IndivKreditLimit
ermittelt. Diese Funktion muss einen Integer-Parameter besitzen, der mit der
Kundid gefüllt wird. Als Ergebnis wird eine numeric(15,4) Variable erwartet.

---

## Vertretergruppe aus Kundestamm vorbelegen (SPA 611)

Vertretergruppe aus Kundestamm vorbelegen (SPA 611)

---

## Sprache 0 aus Kundenstamm übernehmen(SPA 619)

Sprache 0 aus Kundenstamm übernehmen(SPA 619)
Die Sprachnummer 0 aus dem Kundenstamm wird nur bei
Einstellung „Ja“ als Sprache des Vorgangs übernommen.

---

## CRM-Lizenz(SPA 629)

CRM-Lizenz(SPA 629)
Lizenz für CRM.

---

## abweichender Kunde bei Teilumwandlung(SPA 659)

abweichender Kunde bei Teilumwandlung(SPA 659)
Bei „Ja“ ist es erlaubt, bei der Teilumwandlung auf
Beleg eines anderen Kunden zuzugreifen.
ACHTUNG: Dieses Feature wird von Branchen-ERP nicht
offiziell unterstützt. Es kann zu Unstimmigkeiten in der Abstimmung von
kundenbezogenen Daten kommen.

---

## Umsatzsteuer-Identifikationsnummern auf Mandanten und Belegebene(SPA 703)

Umsatzsteuer-Identifikationsnummern auf Mandanten und Belegebene(SPA
703)
Dieser Steuerparameter sorgt dafür, dass man in der
Belegerfassung der Finanzbuchhaltung für die Belegarten AR, AG, ER, EG und EB
eine abweichende Umsatzsteueridentifikationsnummer (USt.-IdNr.) für den
Kunden/Lieferanten bzw. den  Mandanten erfassen kann. Es können in der
Belegerfassung nur Umsatzsteueridentifikationsnummern erfasst werden, die im
Kundenstammpfleger bzw. im Mandantenstammpfleger erfasst wurden. Diese können
über eine F3-Auswahl ausgewählt werden.
Der Steuerparameter hat drei Ausprägungen:
Nein:
Die Felder werden nicht
abgefragt.
Ja:
Die Felder werden normal
abgefragt.
Mit Vorbelegung:
Wenn nur eine USt.-IdNr
existiert, so wird dieses sofort vorbelegt, ansonsten öffnet sich, sobald man
das noch leere Feld betritt, die F3-Auswahl.

---

## Kundenindividuelle Maske (SPA 726)

Kundenindividuelle Maske (SPA 726)

---

## Scanner Betrieb. (SPA 735)

Scanner Betrieb. (SPA 735)
Wie der Scanner sich verbinden soll, wenn die AeinsCE
Software gestartet wird.
•
Online für eine Verbindung mit der zentralen Datenbank
•
Offline mit der Verbindung zur lokalen Datenbank

---

## Itembox Kunde (SPA 765)

Itembox Kunde (SPA 765)
Hier kann eine private Itembox für die Kunden Auswahl
für die eigene Scanner-Maske hinterlegt werden.

---

## Kopie der Versandanschrift bei Vorgangskopie (SPA 774)

Kopie der Versandanschrift bei Vorgangskopie (SPA 774)
Der SPA ist aus Kompatibilität auf „Ja“. Er bestimmt,
ob bei der Kopie eines Vorgangs zu einem anderen Kunden die Versandanschrift des
Zielkunden ermittelt und eingetragen werden soll.
Steht der SPA auf „Nein“, dann wird die
Versandanschrift nicht gesetzt.

---

## Private Scannerprozedur (SPA 801)

Private Scannerprozedur (SPA 801)
Hier kann zu der IP-Adresse eines Scanners eine
private Abarbeitungsprozedur angegeben werden, die eigene entwickelte Module
aufruft.
Des Weiteren gibt es im Referenz-ERP System schon
vorgefertigte Module die mit der Prozedur
CallScannerModule
aufgerufen werden. Der Steuerparameter 801 muss wie folgt eingerichtet werden,
um ein Modul aufzurufen.
aktiv
IP Adresse
Private Prozedur
Private Prozedur
z.B.
      192.168.241.50
CallScannerModule( oder eine Private
      Prozedur)

---

## Behandlungsschema bei Vorgangskopie Voreinstellung (SPA 827)

Behandlungsschema bei Vorgangskopie Voreinstellung (
SPA
827
)
Hier kann ein
Behandlungsschema für die Kundenänderung
voreingestellt werden, das für den Fall der Vorgangskopie als Voreinstellung
dient.

---

## Verbotslistenprüfung Referenzkunde (SPA 825)

Verbotslistenprüfung Referenzkunde (SPA 825)
Hier wird für die regelmäßige Verbotslistenprüfung ein
Referenzkunde hinterlegt, dessen Hauptanschrift immer geprüft wird, um zu
erkennen, ob eine Prüfung gelaufen ist und wann die letzte Prüfung durchgeführt
wurde.

---

## Bestandsabfrage externes System aktiv (SPA 927)

Bestandsabfrage externes System aktiv (SPA 927)
Dieser Steuerparameter darf nur in Absprache mit der
Entwicklung auf „Ja“ gestellt werden. Die Funktionen, die damit freigeschaltet
werden sind eine kundenindividuelle Entwicklung, die keinerlei nützliche Wirkung
bei „gewöhnlichen“ Anwendern haben können.

---

## Auswahllisten-Refresh(SPA 929)

Auswahllisten-Refresh(SPA 929)
Steuert den Refresh angegebener
Auswahllisten-Varianten.
•
Verwendung = Ja / Nein (Standardwert ist Nein )
•
AWL = Auswahllisten-Variante (IB_AnwendVarianteAlle )
•
Frequenz in sec = Zahl der Sekunden für die Frequenz in der die
Auswahlliste aktualisiert werden soll

---

## openTRANS Vorgangsimport Parameter (SPA 939)

openTRANS Vorgangsimport Parameter (SPA 939)
Hier können Parameter wie z.B. das Standardlager oder
der Standardkunde für den Vorgangsimport per openTRANS festgelegt werden. Diese
Parameter werden stets verwendet, wenn es keinerlei Anhaltspunkte für die
Ermittlung dieser Parameter aus dem openTRANS gibt oder die Ermittlung wegen
bestehender Eindeutigkeit (z.B. nur eine Quelle) nicht gegeben ist.

---

## Kunden-Erstübernahme (Faktura) zulässig(SPA 99)

Kunden-Erstübernahme (Faktura) zulässig(SPA 99)

---

## Abkündigung: JRCON/GS MDE – Einzelhandelslösung MOBILAR (OFFLINE)

Abkündigung: JRCON/GS MDE – Einzelhandelslösung MOBILAR (OFFLINE)
Seit letztem Jahr haben wir für Referenz-ERP eine Online
arbeitende Einzelhandels-MDE Lösung. Die obige Lösung war auf Basis von Windows
CE entwickelt worden. Der Support für dieses Betriebssystem wurde von Microsoft
komplett eingestellt. Ebenso gibt es keine aktuellen Entwicklungsumgebungen mit
denen man Anpassungen an diesen Lösungen vornehmen könnte. Wir kündigen diese
Lösung ab. Sofern Sie Interesse an der neuen MDE-Lösung haben, sprechen Sie
unseren Vertrieb an.
Tags:
Abkündigung

---

## Abkündigung: GS-Kommissionierlösung (Offline)

Abkündigung: GS-Kommissionierlösung (Offline)
Was für die Einzelhandelslösung gilt, gilt auch für
die Offline-Kommissionierlösung. Windows CE wird betriebssystemsseitig von
Microsoft nicht mehr unterstützt und es fehlen die Entwicklungswerkzeuge um
diese Lösung weiter zu entwickeln. Wir haben in den vergangenen Jahren viele
Standard-Prozesse aus der Lagerwirtschaft wie auch aus der Produktion MDE-seitig
umgesetzt. Sofern Sie Interesse an dieser Lösung haben, sprechen Sie unseren
Vertrieb an.
Tags:
Abkündigung

---

## Änderungsverfolgung von Kundendaten

Änderungsverfolgung von Kundendaten
Hauptmenü
Stammdatenpflege
Änderungsübernahme Kundenstamm
Direktsprung
[KUAEN]
Die Änderungsverfolgung von Kundendaten ist ein
Überwachungssystem, um Änderungen an Kundendaten verfolgen und beeinflussen zu
können.
Änderungen an den Anschriften, die nicht über den
Kundendatenpfleger
[KU]
getätigt werden, sondern direkt über den
Direktsprung
[ANSCH]
, werden von diesem System
nicht
überwacht.
Sollte die Änderungsverfolgung für Anschiften
eingerichtet werden, so achten Sie bitte darauf auch die Änderungsverfolgung im
Kundenstamm - hier speziell für das Feld „
AdressIdHauptAdr
“ -
einzurichten.
Änderungen übernehmen
Übernimmt die in der Auswahlliste markierte/n
Zeile/n.
Änderungen verwerfen
Verwirft die in der Auswahlliste markierte/n
Zeile/n.
Über eine Maske lassen sich die gewünschten
Informationen zur Überwachung kennzeichnen. Sollte es zu einer Änderung an einem
überwachten Datensatz kommen, so wird die Änderung im Überwachungssystem
gespeichert, der zuständige Überwacher kann diese Daten einsehen, freigeben oder
ggf. verwerfen.
Hierbei lassen sich Änderungen an folgenden
Kundendaten verfolgen:
Anschriftstamm
Kundenstamm
Kundenbank
KundenKredit
KundenZahlBed
KundenOberKunde
KundenZahlKunde
KundForderGruppe
Werden Änderungen an überwachten Daten vorgenommen, so
sind diese erst sichtbar und wirksam, sobald sie von dem Überwacher freigegeben
wurden.
Weitere Änderungen am gleichen Datensatz des
Kunden/Lieferanten können erst wieder erfolgen, wenn letzten Änderungen
freigegeben oder verworfen wurden!

---

## Aktionäre verwalten

Aktionäre verwalten
Nachdem die Unternehmensdaten eingerichtet wurden,
sollten die Aktionäre eingerichtet werden. Ein Aktionär in Referenz-ERP ist ein Kunde
mit weiteren Aktionärsspezifischen Daten wie einer Aktionärsnummer, einem
Eintrittsdatum, einem Austrittsdatum, einem Geburtsdatum, einem Status, einem
Aktivkennzeichen und eventuell Steuerdaten, die bei der Ausschüttung der
Dividende für ein Wirtschaftsjahr verwendet werden [siehe
Dividenden abrechnen
]. Der Status ist das
Anwenderformat „AF_AKTIOSTAT“ und kann vom Anwender unter dem Direktsprung
[FORMA]
gepflegt werden. Ein Aktionär gilt
als Aktiv, wenn er Aktien besitzt. Die Steuerdaten bestehen aus einem „Steuer
Ab“-Datum, einem „Steuer bis“-Datum und einem Modifikator.
Aktionärsdaten gehören zu den so genannten Stammdaten
und können aus den Listen „Aktionärsübersicht“, „Gesamtliste“ und
„Aktionärsdividende“ wie in Referenz-ERP üblich über die Funktionen
Neu
,
Ändern
,
Ansehen
und
Löschen
gepflegt werden. Nach Anwahl einer
dieser Funktionen öffnet sich die Pflegemaske für die Aktionäre.
In dieser Maske können durch folgende
Einrichterparameter Einstellungen vorgenommen werden:
•
Aktionärsnummer ist gleich der Kundennummer
o
JA - Die Aktionärsnummer kann
nicht angegeben werden. Sie wird mit der Kundennummer belegt.
o
NEIN – Die Aktionärsnummer
kann extra eingegeben werden.
•
Verhalten bei doppelter Aktionärsnummer
o
FEHLER – Keine zwei Aktionärs
können dieselbe Nummer haben. Es erfolgt eine Fehlermeldung.
o
WARNUNG – Es erfolgt eine
Warnung, wenn für einen Aktionär eine bereits vorhandene Aktionärsnummer
eingegeben wird.
o
IGNORIEREN – Es können
Aktionäre mit gleicher Aktionärsnummer erfasst werden.
Bei der Erfassung von Aktionärsdaten durch diese Maske
ist zuerst ein Kunde auszuwählen, der der Aktionär ist. Falls es durch obigen
Einrichterparameter erlaubt ist, dass die Aktionärsnummer von der Kundennummer
abweichen kann, darf eine Aktionärsnummer eingegeben werden. Das Eintrittsdatum
wird mit dem
[...]


---

## Allgemeines (Kontrakt)

Allgemeines (Kontrakt)
Die Kontraktverwaltung ermöglicht die Verwaltung von
Verträgen/Kontrakten mit Kunden und Lieferanten, stellt die Konditionen
(Vereinbarte Preise, Mengen, Zeiträume, etc.) der Fakturierung zur Verfügung,
führt Buch über alle Zu- und Abbuchungen, die diese berühren und überwacht die
Einhaltung der Verträge.
Die Stammdaten der Kontraktverwaltung werden in
folgenden Programmbereichen gepflegt:
1.
In der Kontraktstammverwaltung werden alle Bedingungen eines Kontraktes
zusammengetragen, das sind neben Preisen, Mengen, etc. auch sonstige
vertragliche Bedingungen und optische Gestaltungen des Vertrages.
2.
In den Kontrakt-Varianten werden Alternativen für die optische und inhaltliche
Gestaltung von Kontrakten zur Verfügung gestellt.
3.
Im Formulareinrichtungsprogramm wird die generelle Gestaltung des Ausdrucks
festgelegt.
Für die Einrichtung der Programmfunktionen gilt
folgendes:
1.
Sind Ausdrucke nicht erforderlich, so genügt es, in den Kontraktstammdaten die
vertraglichen Vereinbarungen zu erfassen. Auf sie wird dann bei der Fakturierung
zugegriffen.
2.
Wenn Kontraktbestätigungen etc. erforderlich sind, sollten zuerst die Formulare
gestaltet werden und danach die Kontrakt-Varianten.
Diese Aussagen gelten für alle Formen des
Kontraktgeschäftes, die hier als Kontraktklassen bezeichnet werden. Über diese
Kontraktklassen werden Buchungsmechanismen automatisch gesteuert:
Warenverkauf:
•
Verkaufskontrakt
•
Verkaufskontrakt Fremdlager
•
Verkaufskontrakt Rohware
Wareneinkauf:
•
Einkaufskontrakt
•
Einkaufskontrakt Fremdlager
•
Einkaufskontrakt Rohware

---

## Allgemeine Programmfunktionen

Allgemeine Programmfunktionen
Letzter Hilfebau : 21.05.2026 08:28:35
Systemvoraussetzungen für Referenz-ERP:
•
Client: Alle von Microsoft supporteten Betriebssysteme.
o
Windows
11 Pro /
Enterprise
(23H2 und 24H2) ist freigegeben.
•
Server: Alle von Microsoft supporteten Betriebssysteme (nur in 64-Bit
Version).
•
Windows-Server
2025
wird empfohlen.
Die vollständigen Systemvoraussetzungen und
Empfehlungen für Sie entnehmen Sie dem Dokument Systemvoraussetzungen:
Systemvoraussetzungen
Hinweis:
Windows Server 2012 mit einer Extended Security
Updates (ESU) Lizenzierung wird nicht mehr unterstützt.
Fremdsoftware und deren Anbindung wird ausschließlich
auf Basis gewarteter Versionen unterstützt. Drittanbietersoftware, die nicht
mehr der Wartung des Anbieters untersteht, kann nicht von Referenz-ERP® unterstützt
werden.

---

## Karte - Funktionen

Karte - Funktionen
In verschiedenen Anwendungen wie Kunden und
Anschriften sind Funktionen aktiv, die unter dem Namen „Karte“ zusammengefasst
werden können. Die sind abhängig von der Lizenz für GeoDatenDienste.
Eine genauere Beschreibung dieser Funktionen erhalten
Sie
hier
.

---

## Anschriften

Anschriften
Stammdatenpflege
Kunden-/Lieferantenstamm
Anschriften
Zusätzlich zu der Sicht auf die Kunden kann diese
Sicht auf die Anschriften angewählt werden, die es ermöglicht, alle Anschriften
eines Kunden zu sehen, und es auch erlaubt, diese Anschriften zu bearbeiten, und
ggf. neue zu ergänzen.

---

## Adressmaske

Adressmaske
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Anschriftmaske
Direktsprung
[KUAN]
Die Darstellung der Kunden-/Lieferantenanschriften
kann individuell gestaltet werden. Nach Anwahl der Funktion wird folgender
Bearbeitungsbildschirm angeboten:
In den vier Feldern auf der linken Seite werden
Grundeinstellungen der Anschriften­gestaltung angezeigt, die in der
Formulareinrichtung für die Adressblöcke verwendet werden. Auf diese
Einstellungen kann beim Ausdruck zugegriffen wer­den, indem bei der
Formulargestaltung bei der Einbindung der Anschrift in der Spalte Nk der
Parameterwert 1,2,3,4 eingetragen wird. Wenn man eine neue Adressmaske erstellt,
muss man dieser einen Name geben, der anschließend rechts in Liste und „Masken“
zu finden ist. Um diese individuelle Anschrift einem Kunden oder Lieferanten
zuzuordnen trägt man diese im Anschriftenstamm auf dem Reiter Zusätze und dort
unter „Adressmaske für Druck“ ein.
Die Zeichen in den Anzeigefenstern haben folgende
Bedeutung:
# 1 - #43:
Felder aus dem Kunden-/Anschriftstamm, die ausgedruckt
werden können
$$:
Die Anzahl der $ - Zeichen reserviert exakt diesen
Platz für das auszudruckende Feld. Ist das Feld kleiner, werden Leerzeichen
gedruckt, ist das Feld länger, wird abgeschnitten
§§:
Die Anzahl der § - Zeichen reserviert maximal diesen
Platz für das auszudruckende Feld. Ist das Feld kleiner, wird der Platz
freigegeben, ist es größer, wird abgeschnitten.
Beispiel:
# 3$$$$$$$$$$$$$$$$$$$
Reserviert ein Feld für den Namen mit genau 21 Zeichen
Länge. Wenn der Name kürzer ist, verbleibt der Rest leer.
# 3§§§§§§§§§§§§§§§§§§§
Reserviert ein Feld für den Namen mit genau 21 Zeichen
Länge. Wenn der Name kürzer ist, werden die Zeichen freigegeben.
Aufbau einer Anschrift:
Mit Eintragung der Platzhalter #1 - #40 sowie der
Feldlängen mittels
$
und
§
wird das Anschriftenfenster gestaltet. Mit
F3
werden Eingabemöglichkeiten
angezeigt:
# 1
Anrede
# 2
Vorname
# 3
[...]


---

## Archiv-Fakte

Archiv-Fakte
Hauptmenü
Administration
Archiv
Administration
Archiv-Fakte
Direktsprung
[FAREF]
Bestimmte Objekte in Referenz-ERP (z.B. Vorgänge, Kunden,
Artikel, u.a.) haben feste Regeln hinterlegt, mit deren Hilfe sie automatisch
Archiv-Referenznummern vorgeschlagen bekommen, wenn sie neu ins System kommen.
Diese Objekte zusammen mit ihren Definitionen sind in Referenz-ERP die
Archiv-Fakte.
Felder
Auslieferung
Ja/Nein
Gibt
      an, ob das vorliegende Archiv-Fakt von Branchen-ERP ausgeliefert wird.
Branchen-ERP-Auslieferungen sind solche
      Archiv-Fakte die mit
fam_ref_
beginnen.
Archiv-Fakte
Eindeutiger Schlüsselbegriff der
      Archiv-Fakte.
Es
      stehen maximal 30 Zeichen zur Verfügung.
Beschriftung
Repräsentation des Archiv-Faktes in
      der Benutzeroberfläche.
Branchen-ERP-Referenz
Datenbank-Funktion zur Ermittlung
      der Referenz eines Archiv-Faktes.
Die
      jeweilige Datenbank-Funktion die Branchen-ERP ausliefert ist als Beispiel zu
      sehen. Es kann durchaus sein, dass vor Ort individuelle Anpassungen
      durchgeführt werden müssen.
Allerdings – so zeigt die Praxis –
      ist das selten von Nöten.
Privat-Referenz
Die
      Möglichkeit die Funktionalität der Branchen-ERP-Referenz zu ersetzen.
Wenn
      man hier deine existierende private Datenbank-Funktion einträgt, dann wird
      zur Ermittlung der Referenz genommen, und nicht die
      Branchen-ERP-Referenz!
Relation
Die
      Relation, in der die Kerndaten sowie die Archiv-Referenz des Archiv-Faktes
      gespeichert werden. Das ist ein Fakt.
Referenz-Spalte
Der
      Name der Spalte der Relation, in der die Archiv-Referenz gespeichert wird.
      Das ist ein weiteres Fakt.
Aufruf-Parameter
Die
      Parameter für den Aufruf der jeweiligen Datenbank-Funktion.
Ohne Referenz!
Eine
      statistische Aussage darüber, wie viele Exemplare eines bestimmten
      Archiv-Faktes KEINE eingetragene Archiv-Referenz in der Referenz-Spalte
      der Relation hinterlegt haben.
Dabei handelt es sich vornehmlich um
      Alt-Beständ
[...]


---

## Archiv Mail Versand

Archiv
Mail Versand
Mit der Funktion „
Senden An
“
in der Archivanzeige können Sie ein oder
mehrere markierte Dokumente per Mail und/oder Fax versenden.
Diese Funktion steht u.a. auch in den Auswahllisten
Kunden, Anschriften, Lieferanten und Interessenten als Funktion „
Email
senden
“ zur Verfügung,
Einem Dokument ist in der Regel ein Kunde zugeordnet,
der jedoch neben der Hauptanschrift noch ein Lager und mehrere Ansprechpartner
haben kann. Es wird also eine Liste der möglichen E-Mail-Adressen und Faxnummern
angezeigt, an die die gewählten Dokumente versendet werden sollen. Zudem gibt es
ein Eingabefeld, in dem Sie manuell eine oder mehrere Mailadressen bzw.
Faxnummern mit Semikolon getrennt eingeben können.
Ein Betreff und ein kurzer Beschreibungstext können
hier ebenso für die Verwendung in einer E-Mail oder einem Faxdeckblatt angegeben
werden.
Nun stehen folgende Funktionen zur Verfügung:
•
Versenden – Hier wird die Liste der Dokumente und Empfänger an ein
externes System übermittelt, das sodann den Versand übernimmt. Hier kann z.B.
Tobit verwendet werden. Als Schnittstelle dient ein XML-Dokument, das die für
den Versand notwendigen Daten bereitstellt.
•
Versenden (Outlook) – Hier wird das im
Einrichterparameter
gesetzte Skript aufgerufen, das
die gewählten Dokumente aus der Datenbank extrahiert und ein installiertes
Outlook dazu veranlasst, eine Mail zu öffnen, die die gewählten Empfänger und
die gewählten Dokumente beinhaltet. Die Mail muss dann manuell abgesendet
werden.
Es ist möglich mit einem
alternativen VBS-Skript an dieser Stelle andere Mailclients anzusprechen.
Für die Anbindung eines
Tobit-Clients steht exemplarisch das VBA-Skript „AMIC_FAVersandTobit“ zur
Verfügung.
Neben der ersten Registerkarte, auf der diese
Einstellungen vorgenommen werden können, stehen u.U. weitere Registerkarten mit
einem Datum im Tab-Reiter. Diese geben dem Anwender die Möglichkeit als eine
Historie nachzuvollziehen, wann das Dokument an wen versendet
[...]


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

## Aufgabenplanung Auswallliste

Aufgabenplanung Auswallliste
Hauptmenü
Büro und Internet
Büroumgebung
Aufgabenplanung
oder Direktsprung
[TODO]
Felder der Auswahlliste
Feld
Beschreibung
Aufgenommen von
Kürzel des Erstellers
Aufgenommen am
Datum an dem der Datensatz erstellt
      wurde
Kundennummer
ID
      des Kunden
Kundenbezeichnung
Bezeichnung des Kunden
Verantwortlicher
Kürzel des ToDo Inhabers
Status
0:
      offen
1: erledigt
Termin von
Datum Start
Termin bis
Datum Ende
Betreff
Betreff des ToDos
Suchmöglichkeiten der Auswahlliste
Suchen
Beschreibung
Status
0:
      offen
1: erledigt
Verantwortlicher
Kürzel des ToDo Inhabers
Termin
Von…
      Bis…
Kunde
ID
      des Kunden
Betreff enthält
%
Bemerkung enthält
%
Funktionen der Auswahlliste
Funktion
Beschreibung
Ändern (
F5
),
Ansehen (
F6
),
Löschen (
F7
),
Neu (
F8
)
Datensatz wird zum bearbeiten
      geöffnet
Datensatz wird angezeigt
Ausgewählter Datensatz wird
      gelöscht
Erstellt neuen Datensatz

---

## Schritt für Schritt

Schritt für Schritt
Schritt 1.1: SPA aktivieren
Zuerst mit dem Direktsprung
[SPA]
in die Auswahlliste der SPAs. Dann nach
dem SPA „1065“ suchen und die Lizenz aktivieren.
Schritt 1.2: Beispiel Szenario
Ein Teamleiter datiert für einen Mitarbeiter, einen
Termin mit einem Kunden.
Der Teamleiter legt eine Aufgabe für den Mitarbeiter
an:
-
Mitarbeiter in die Aufgabe eingetragen
-
Kunde wird in die Aufgabe eingetragen
-
Datum wird in die Aufgabe eingetragen
Schritt 1.3: Beispiel in Referenz-ERP
Zuerst navigiert man mit dem Direktsprung
[TODO]
in die Auswahlliste der
Aufgabenplanung. Danach erstellt man mit
F8
einen neuen Datensatz.
Als letztes speichert man den Datensatz ab (
F9
).

---

## Auslandskunden

Auslandskunden
Hauptmenü
Stammdaten
Konstanten Kundenstamm
Auslandskunden
oder Direktsprung
[KUA]
Kunden die im Ausland ansässig sind unterliegen u.U.
speziellen Bedingungen, so dass ihre Daten in einem eigenen Auswahlbildschirm
erfasst werden. Hier werden die Kunden erfasst, bei denen die OP's sofort als
Auslands-OP gekennzeichnet werden sollen
Besonderes Augenmerk ist hierbei auch auf die
jeweilige Steuerpflicht im Hinblick auf Erfüllungsorte u.ä. zu richten.
In der Stammdatenmaske können folgende Daten
eingegeben werden.
Felder
Kunde
Nummer des Kunden, bei Neuanlage
      mit
F8
kann mit
F3
eine Kundenauswahl aus dem
      Kundenstamm mittels einem sich öffnenden Auswahlbildschirm getroffen und
      übernommen werden.
Währung
Eingabe der Währungsnummer, mit
F3
kann wiederum eine Auswahl
      hier aus dem Währungsstamm getroffen werden
DTA
Hier
      kann ein Format für den Datenträgeraustausch eingegeben und mit
F3
ausgewählt werden
Zahlungsart
Hier
      können die Zahlungsarten eingegeben oder mit Hilfe der
F3
Taste ausgewählt werden. Die hier
      hinterlegte Zahlungsart wird als Vorbelegung für den Auslands-OP
      herangezogen.

---

## Bankverbindung

Bankverbindung
Eintragung der
Bankverbindungen
eines Kunden. Wenn man einen
Kunden bearbeite, so kann man direkt mit der Funktion
Bankverbindung
F8
diesem Kunden eine Bankverbindung
zuweisen oder bestehende Bankverbindungen bearbeiten.

---

## Objekt-Stamm

Objekt-Stamm
Auf der Anwendung Objekt-Stamm kann man Projekte
anlegen (für ein oder mehrere Kunden mit einem oder mehreren Lieferanten).
Hauptmenü
Nebenbuchhaltungen
Objekte
Objektverwaltung oder Direktsprung
[OBJ]
Tabreiterübergreifende Felder
Oben links sind Felder, welche dauerhaft eingeblendet
sind
Es gibt folgende Felder:
Feld
Beschreibung
Nummer
Wird
      automatisch mit einer freien Objektnummer gefüllt.
Unter- Nr.
Es
      kann eine Unternummer eingetragen werden, wenn man mehrere Unterobjekte
      mit der gleichen Objektnummer haben möchte.
Bezeichnung
Bezeichnung für das
      Objekt.
Matchcode
Suchbegriff für das
      Objekt.
Das Feld Unter- Nr. ist nur sichtbar, wenn der
Steuerparameter SPA_BAUSTELLE_UNTERBAUSTELLE_AKTIV mit der Nummer 172 gültig
ist.
Das Feld Matchcode wird automatisch mit dem Inhalt des
Feldes Bezeichnung befüllt. In das Feld kann etwas anderes als die Bezeichnung
eingetragen werden.
Allgemein
Auf dem Tabreiter „Allgemein“ sind Felder, welche
teilweise schon vorausgefüllt sind
Es gib folgende Felder:
Feld
Beschreibung
gültig ab
Wird
      automatisch mit dem heutigen Tag gefüllt
gültig bis
Wird
      automatisch mit dem heutigen Tag + 1 Jahr gefüllt
Archivreferenz
Wird
      automatisch mit 00BS0000 + dem Eintrag im Nummernfeld gefüllt
Kunde
Die
      Kundennummer der Kunden. Mittels F3 ist eine Auswahlhilfe verfügbar. Bei
      mehr als einem Kunden wechselt man in den Tabreiter Kundenliste und trägt
      dort im Grid einen weiteren Kunden ein. Falls alle Kunden betroffen sind,
      lässt man das Feld leer.
Lieferant
Die
      Kundennummer der Lieferanten. Mittels F3 ist eine Auswahlhilfe verfügbar.
      Bei mehr als einem Lieferanten wechselt man in den Tabreiter
      Lieferantenliste und trägt dort im Grid einen weiteren Lieferanten ein.
      Falls alle Lieferanten betroffen sind, lässt man das Feld
      leer.
Rechnungsempfänger
Die
      Kundennummer des Rechnungsempfängers, auch als Oberkunde beka
[...]


---

## Beispiel 1 - Dateiinhalt

Beispiel 1 - Dateiinhalt
In diesem Falle werden die Kerndaten sämtlich aus dem
Dateinamen gewonnen.
Man sieht, dass die FA-Spalten (Kerndaten)
„Kundennummer, Belegreferenz, Belegtyptext und Mandant“ explizit ermittelt
werden soll.

---

## Übersicht Kunden und Lieferanten

Übersicht Kunden
und Lieferanten
Hauptmenü
Stammdatenpflege
Kunden-/Lieferanten
In den Kunden- und Lieferantenstammdaten werden alle
Daten über Personenkonten zusammengefasst, die für die Fakturierung und
weiterführende Arbeiten benötigt werden. Die Stammdaten der Personenkonten sind
identisch aufgebaut; sie werden deshalb exemplarisch am Beispiel der
Kundenstammdaten beschrieben.
Vor der Erfassung der Personenkonten ist es sinnvoll
(jedoch nicht erforderlich) die Konstanten anzulegen. Hierauf wird zuerst
eingegangen.

---

## Besuchsberichte

Besuchsberichte
Hauptmenü
Stammdatenpflege
Kunden/Lieferanten
Besuchsberichte
Direktsprung
[BB]
Felder
Kunde
Nummer und Name des
      Kunden
Bericht vom
Datum des Berichtes
Nächster Besuch am
Datum des nächsten Besuches
      (Vorbelegung über den
Einrichterparameter
Besuchsintervall (Tage))
geändert von
Kürzel des Benutzers der zuletzt
      Änderungen vorgenommen hat
am
Datum an dem zuletzt Änderungen
      vorgenommen wurden
Archiv-Referenz
Referenz zum Archiv
Feld
      1-7
Eingabefelder für Text (Label über
Einrichterparameter
einstellbar)
Nachkomma 1-5
Eingabefelder mit Nachkommastellen
      (Label über Einrichterparameter einstellbar)
Datum 1-3
Eingabefelder fürs Datum (Label über
Einrichterparameter
einstellbar)
Rollbox
Box
      zum Scrollen (Label über
Einrichterparameter
einstellbar)
Anlagen
Die
      Anlagenverwaltung in den Besuchsberichten ist veraltet. Bitte das Archiv
      verwenden.
Einrichterparameter für Besuchsberichte
Einrichterparameter
Vorbelegung
Rollbox entfernen
Bezeichnung für die Rollbox; bleibt
      die Bezeichnung leer, dann wird das Feld auf der Maske
      ausgeblendet
Rollbox
Besuchsintervall (Tage)
Füllt das Feld ‚Nächster Besuch am‘
      mit heute + angegebene Anzahl Tage
60
Bezeichnung Spalte 1 Feld
      1
Bezeichnung für das Feld; bleibt die
      Bezeichnung leer, dann wird das Feld auf der Maske
      ausgeblendet
Feld1
Bezeichnung Spalte 1 Feld
      2
Bezeichnung für das Feld; bleibt die
      Bezeichnung leer, dann wird das Feld auf der Maske
      ausgeblendet
Feld2
Bezeichnung Spalte 1 Feld
      3
Bezeichnung für das Feld; bleibt die
      Bezeichnung leer, dann wird das Feld auf der Maske
      ausgeblendet
Feld3
Bezeichnung Spalte 1 Feld
      4
Bezeichnung für das Feld; bleibt die
      Bezeichnung leer, dann wird das Feld auf der Maske
      ausgeblendet
Feld4
Bezeichnung Spalte 1 Feld
      5
Bezeichnung für das Feld; bleibt die
      Bezeichnung leer, dann wird das Feld auf der Maske
[...]


---

## Einrichtung des Scanners

Einrichtung des Scanners
Hier werden alle Schritte beschrieben, die benötigt
werden, um den Scanner für die Inbetriebnahme vorzubereiten.

---

## Scanner Steuerparameter

Scanner Steuerparameter
Die
Steuerparameter
des Scanners werden sind in der
Gruppe Scanner zusammengefasst. Soll ein Steuerparameter für eine bestimmte IP
Adresse gelten, so wird diese im Schlüssel hinterlegt.

---

## Server starten

Server starten
Hier finden Sie die Erklärung der einzelnen
Maskenfelder
Registerkarte Server
Eingabefelder
Bedeutung
Grid
      (TCP/IP Adressen)
In
      dem Grid werden alle aktiven und jemals aktiven Scanner-IP’s
      angezeigt
Serverfehler
In
      dem Feld Serverfehler wird der Datenbank Fehler angezeigt falls es zu
      einem Fehler mit dem Scanner kommt.
Port
In
      dem Feld Port wird der Port der Datenbank eingegeben.
Updatezyklus
In
      dem Feld Updatezyklus wird die Updatezeit eingegeben.
Vorgangsprotokoll
In
      das Feld Vorgangsprotokoll kann eingetragen werden, ob während der
      Verarbeitung eines Scanvorganges in das Vorgangsprotokoll geschrieben
      werden soll. Dies ist nützlich bei einer eventuellen
      Fehlersuche.
Aufräumen
Hier
      kann entschieden werden, ob die gescannten Daten nach erfolgreicher
      Vorgangserzeugung aus den Scannertabellen geleert werden.
Testumgebung
Hier
      kann entschieden werden, ob die Testumgebung genutzt werden
      soll.
Testvorgang
Belegdruckernummer
Verwendet den Drucker der
      standardmäßig unter Windows für den Scannerbenutzer eingetragen worden
      ist. Wird in dem Feld Ja ausgewählt so wird nach der Erstellung des
      Vorgangs der Beleg automatisch ausgedruckt. Steht ein Nein in diesem Feld
      so wird der Beleg manuell gedruckt.
Registerkarte Allgemein
Auf der Registerkarte Allgemein finden Sie noch
weitere Einstellungen, die für den Betrieb der Scanner von Bedeutung sind.
Eingabefelder
Bedeutung
Prozedur Dateieingang
Script Vorgangsabschluss
Kundengruppe für Etikett
      druck
Rückantwort EAN
Protokoll IP
Scanner addiert Menge
Es
      gibt die Möglichkeit die Menge per Hand einzugeben. Stellt man aber diesen
      Punkt auf “JA“, so addiert der Scanner die Menge dies bedeutet, dass jede
      Position eines Artikels einzeln eingescannt werden muss.
Kundensuchkriterium
Im
      AeinsCE gibt es die Möglichkeit für Eingangslieferscheine den Kunden

[...]


---

## Verbotsliste (Compliance)

Verbotsliste (Compliance)
Die Sanktionslistenprüfung wurde aufgrund der
Verordnung
(EG) Nr. 2580/2001
der EU entwickelt. Die Prüfung ermittelt, ob Zulieferer,
Kunden usw. auf dieser Sanktionsliste stehen.
Der internationale Handel unterliegt u.U.
internationalen Handelssanktionen. Der Verstoß dagegen kann empfindliche
Konsequenzen von Bußgeldern über handelsrechtliche Sanktionen oder den Eintrag
auf die Blacklist internationaler Auftraggeber nach sich ziehen. Deshalb ist es
wichtig, seine Auftraggeber zu kennen und gegen eine Sanktionsliste
abzugleichen. Diese Listen sind ständigem Wandel unterworfen und der manuelle
Abgleich vor jedem Vorgang wäre manuell sicher aufwändig.
Firmen wie
AEB
bieten hier die geeignete Möglichkeit,
einen automatisierten Abgleich mit den im ERP-System gespeicherten
Anschrifteninformationen vorzunehmen. Referenz-ERP bietet nun diese Anbindung an den
Sanktionslistenabgleich von AEB als kostenpflichtiges Modul an.
Da das Compliancemodul Modul übergreifend ist, gibt es
verlinkungen auf die jeweiligen Hilfen:
Modul verlinkungen
-
Mandantenstamm
(Register
Verbotsliste)
-
Kundenstamm
-
Anschriftenstamm
SPA Verlinkungen
-
Steuerparameter 707
-
Steuerparameter 824
-
Steuerparameter 1063

---

## DTA

DTA
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
Direktsprung
[ZHB]
Die Daten werden für den Datenträgeraustausch
aufbereitet. Spezielle Einstellungen lassen sich am
Steuerparameter
919
ändern.
Es stehen mehrere DTA-Verfahren zur Verfügung.
•
DTA-Verfahren zwischen Kunde und Bank. Hier wird je nach Einstellung des
Steuerparameters (SPA) „DTA-Ausgabeformat“ unterschieden, welches Format für die
Dateiausgabe verwendet wird. Zurzeit werden folgende Formate unterstützt:
1.
Deutschland: Datenträgeraustausch zwischen Kunde und Bank.
2.
Österreich: EDIFACT-TRANSAKTION für den Inlandszahlungsverkehr
3.
Dänemark: Unitel for PC Format.
4.
SEPA
5.
Datenbankfunktion: Offenes Format, bei dem eine Datenbankfunktion die
Ausgabedaten als long varchar liefert. Diese private Datenbankfunktion wird
unter der Option (Direktsprung [OPT]) DTA_PROZEDUR eingetragen. Als Parameter
erhält diese Prozedur die ASATZ_ID über die die Aufbereiteten Datensätze
identifiziert werden können
Achtung:
Wird die Prozedur im
Vieraugenprinzip-Zahlung verwendet, so wird die ZahllaufId zur Identifizierung
übergeben.
•
DTINT Verfahren
•
DTA-Verfahren für den Auslandszahlungsverkehr. Der
Auslandszahlungsverkehr wird für die DTA-Formate in Deutschland und Dänemark –
dort natürlich für alle Länder - unterstützt.
•
SEPA
.
Für die drei Formate DTA, DTINT und DTA für
Auslandszahlungen sind unterschiedliche Dateinamen vorgesehen, die auch getrennt
voneinander abgespeichert werden. Es ist somit auch möglich, diese Verfahren
parallel zu nutzen und die Ausgabedateien auf unterschiedliche Verzeichnisse
auszugeben.
Um sicherzustellen, dass der an die Bank gesendete
Datenträger Fehlerfrei ist, werden diverse Prüfungen vorgenommen:
•
In und Auslandszahlungsverkehr darf nicht gemischt sein.
•
Nur eine Hausbank pro DTA.
•
Nur Zahlungsausgang oder Zahlungseingang pro DTA.
•
Nur eine Währung beim DTA für Inlandszahlungsverkehr.
•
Nur nicht bereits verarbeitete (gedruckte
[...]


---

## openTRANS

openTRANS
openTRANS-Kunde
Gibt an, ob es sich um einen Kunden handelt, dessen
Vorgänge beim Drucken als openTRANS exportiert werden sollen und ob ggf. ein
Druck gegen die Erstellung eines openTRANS-Exports ersetzt wird.
Wert
Bezeichnung
Bedeutung
0
Nein
Es
      wird kein Belegversand verwendet
1
Mit
      Rechnungsdruck
Der
      openTRANS-Export erfolgt analog zum Rechnungsdruck
2
Statt Rechnungsdruck
Der
      openTRANS-Export erfolgt anstelle des Rechnungsdrucks
Hinweis:
Bitte beachten Sie, dass diese
      Einstellung „Statt Rechnungsdruck“ unter Umständen die Einstellung „mit
      Rechnungsdruck“ im Bereich Belegversand überschreibt. Ist eine dieser
      Einstellungen auf „statt Rechnungsdruck“ gestellt, so entfällt der
      Druck!
PDF Signierung
Dieses Kennzeichen gibt an, ob Vorgänge für diesen
Kunden im Formulararchiv signiert werden sollen und ob ggf. im PDF die
openTRANS-Information in den PDF-Daten enthalten sein soll.
Warnungen
Nicht alle Besonderheiten der Warenwirtschaft, die in
Referenz-ERP abgebildet werden, sind openTRANS-kompatibel. Da openTRANS sowohl für die
Kommunikation von Referenz-ERP zu Referenz-ERP eingesetzt wird, als auch für die
Kommunikation über die e-Billing-Schnittstelle, die die Einhaltung des
openTRANS-Standards verlangt, gibt es verschiedene Vorgehensweisen, wie mit
diesen Unwägbarkeiten umgegangen werden soll:
Wert
Bezeichnung
Bedeutung
0
anzeigen - bereinigter
      Export
Die
      Meldung wird als Fehler im Fehlerprotokoll ins Fehlerprotokoll
      eingetragen. Die inkompatiblen Elemente werden ausgelassen.
1
anzeigen - voller Export
Die
      Meldung wird als Warnung ins Fehlerprotokoll eingetragen. Die
      inkompatiblen Elemente werden exportiert.
2
nicht anzeigen - voller
      Export
Es
      werden keine Meldung ins Fehlerprotokoll geschrieben. Die inkompatiblen
      Elemente werden exportiert.

---

## Eingabe Kundenkredit

Eingabe
Kundenkredit
Hauptmenü
Stammdatenpflege
Kunden / Lieferanten
Kundenstamm
Direktsprung
[KU]
Die Einrichtung der Kreditlimits geschieht in
Abhängigkeit des
Steuerparameters
503
– „Alle Kredite als Summe übernehmen“.
Die Eingabe des Kreditlimits kann von zweiten Seiten
aus geschehen. Zum einen kann das Limit vom Pfleger für
Kunden-/Lieferantenstammdaten
aus eingegeben werden und zum anderen über
den Pfleger der
Kreditvergabe
.
Im Pfleger für
Kunden-/Lieferantenstammdaten
ist lediglich ein Feld „Kreditlimit“ vorhanden, welches je nach Steuerparameter
(s.o.) für eine Bearbeitung freigeschaltet ist oder nicht.
Wird hier ein Wert geändert und gespeichert, so wird
in Folge dessen ein Abgleich mit dem Pfleger der Kreditvergabe durchgeführt.
Zunächst wird der Kredittyp ermittelt zu dem das neue Kreditlimit dort angelegt
werden soll. Vorhandene Einträge werden auf den Status „abgelaufen“ gesetzt und
das neue Limit wird eingetragen.
Hier ein wichtiger Hinweis zum
Kundenkreditlöschkennzeichen
.
Die Anwendung
Kreditvergabe
dient zur
Einrichtung und Kontrolle der Kreditlimits für den gewählten Kunden. Sie zeigt
alle aktiven und inaktiven Kreditlimits in Sortierung nach der Limitart bzw. des
Kreditversicherers an.
Es ist möglich mehrere Einträge zu einem
Kreditversicherer zu erzeugen. Dies ermöglicht zum Beispiel Planung eines Limits
in der Zukunft.
Die Gültigkeit eines Kreditlimits hängt vom Datum der
Genehmigung und des „Gültig Bis“ - Datum ab und davon, ob das Kreditlimit mit in
die Summierung einfließen soll.
Wird für einen Kunden ein Kreditlimit gespeichert, so
wird dieses gleichzeitig in dem zugehörigen Feld im Kunden-/Lieferantenstamm
aktualisiert. Das Feld im Kunden-/Lieferantenstamm enthält immer den zur Zeit
der Betrachtung korrekten Wert.
Wie dieser Wert bestimmt wird, lässt sich mit dem
Steuerparameters 503
– „Alle Kredite
als Summe übernehmen“ – festlegen. Ist keine Summierung erwünscht, so ist das
Feld „Kreditlimit“ in den Kunden-/Liefera
[...]


---

## Einrichtung Verbotsliste

Einrichtung Verbotsliste
Auf dem Register „Zusätze“ in den Anschriften ist, für
die Verbotslistenprüfung, der Prüfstatus dieser Adresse zu setzen:
ID
Bezeichnung
Bedeutung
0
nicht testen
Diese Adresse wird nicht automatisch
      (z.B. durch ein Event) geprüft. Wird diese Adresse ausgewählt und die
      Funktion
Verbotslistenprüfung
gewählt, so wird diese Adresse geprüft.
1
manuell erlaubt
Obwohl die Prüfung eine
      Übereinstimmung gefunden hat, darf diese Adresse verwendet werden. z.B.
      weil die Übereinstimmung zufällig oder die Handelsart nicht vom Embargo
      betroffen ist. Es ist anzuraten, die Gründe für die Setzung dieses Status
      zu dokumentieren!
10
ungeprüft
Diese Adresse ist derzeit nicht
      geprüft, ist jedoch zur Prüfung vorgesehen.
11
nicht zulässig
Diese Adresse ist bei der Prüfung
      auf eine Übereinstimmung gestoßen.
Dieser Status kann nicht manuell
      gesetzt werden!
12
zulässig
Diese Adresse hat die Prüfung
      durchlaufen und ist nicht auffällig.
Dieser Status kann nicht manuell
      gesetzt werden!
99
egal
Dieser Status dient lediglich der
      Filterung der Auswahlliste.
Dieser Status kann nicht manuell
      gesetzt werden!
Ist der Status „nicht zulässig“ oder „zulässig“, so
wird er bei Änderung der Anschrift automatisch auf „ungeprüft zurückgesetzt, da
schließlich die neue Anschrift ein anderes Prüfergebnis zur Folge haben
kann.
Ändern Sie eine Anschrift zum Status „nicht testen“
oder „manuell erlaubt“, so werden Sie um die Eingabe einer Begründung
gebeten.

---

## Email senden

Email senden
Aus den Auswahllisten Kunden, Anschriften, Lieferanten
und Kontokorrentkunden ist die Funktion
Email senden
verfügbar. Mit Hilfe dieser
Funktion kann eine E-Mail an die markierten Kunden (Mailadresse aus der
Kundenhauptanschrift) oder eine Mailadresse aus der Anschrift versendet
werden.
Zu diesem Zweck wird über ein VBA-Skript der
Mailclient Outlook geöffnet und die Mailadressen werden als Liste in den TO bzw.
BCC.Bereich eingefügt. Das Ziel ist in einer kurzen Abfrage zu definieren.
Steht Outlook als Mailclient nicht zur Verfügung, so
kann ein anderes VBA-Skript definiert werden, das den Versand übernimmt. Zu
diesem Zweck ist der Einrichterparameter in
Archiv Mail Versand
anzupassen.

---

## Endkontrolle/Einspielung Kunden

Endkontrolle/Einspielung Kunden
Neuanlage eines Imports
Mit
F8
kann
ein neuer Kundenimport angelegt werden.
Mit
F5
können Datensätze, die über den Stammdatenimport ins System gekommen sind,
bearbeitet und korrigiert werden.
Tabreiter übergreifende Felder
Eingabefelder
Bedeutung
Satznummer
Automatisch generierte
      Zahl
Kundennummer
Gewünschte Kundennummer. Rechts
      davon ein Feld für die gewünschte Kundenbezeichnung
Kundentyp
Mittels F3 kann der Kundentyp
      ausgewählt werden.
Musterkunde
Mittels F3 kann ein Musterkunde
      ausgewählt werden.
Die Kundennummer ist ein Pflichtfeld. Wird eine schon
vorhandenen Kundennummer angegeben, so wird durch den Import der Kunde mit den
Daten aus dem Import aktualisiert.
Gehört die Kundennummer einem Kunden, der gelöscht
wurde, so wird der Import abgebrochen.
Der Kundentyp ist ein Pflichtangabe.
In Abhängig vom Kundentyp werden im Musterkunden die
Musterkunden des Kundentyp angezeigt.
Musterkunden werden in
[KU]
der Variante Musterkunde angelegt.
Der Musterkunde ist ein Pflichtfeld. Aus dem
Musterkunden werden sehr viel Daten für den Import genommen.
Tabreiter Adresse
Eingabefelder
Bedeutung
Anrede
Anrede des Kunden
Vorname
Vorname des Kunden
Name
Nachname des Kunden
Staat
Staat des Kunden
Postleitzahl
Postleitzahl des Kunden
Ort
Ort
      des Kunden
Ortsteil
Ortsteil des Kunden
Straße
Straße des Kunden
Telefon
Telefonnummer des Kunden
Telefax
Telefaxnummer des Kunden
Tabreiter Zusatzinfo/Bank
Eingabefelder
Bedeutung
Kurzname
Kurzname des Kunden
Matchcode
Matchcode des Kunden
Zusatz
Zusatzinformation zum
      Kunden
Partner1
Partner1 des Kunden
Partner2
Partner2 des Kunden
Bankleitzahl
Bankleitzahl des Kunden
Bankname
Mittels F3 kann der Bankname des
      Kunden ausgewählt werden.
Bankkonto
Bankkonto des Kunden
Tabreiter FiBu-Daten
Eingabefelder
Bedeutung
Mahnsperre
Mittels F3 kann eine Mahnsperre
      eingerichtet werden.
Zinssperre
Mittels F3 kann eine Zinssperre
      eingerichtet werden.
Kokore-
[...]


---

## Erfassen mit Mustern

Erfassen mit Mustern
Referenz-ERP
bietet ein sehr mächtiges
Parametersystem. I.d.R. wird es jedoch so sein, dass in einem Unternehmen die
Kunden nach einem (oder wenigen) einheitlichen Schemata erfasst werden. So wird
beispielsweise in einem Unternehmen unterschieden zwischen:
Bauunternehmern: mit Preisklasse 1, normale
Kontoführung in Mahngruppe 1
Landwirten: mit Preisklasse 2, Kontokorrentkonto
verzinst
Alle anderen Parameter sind gleich.
O.a. Werte könnten nun bei der Erfassung der Kunden
jeweils mit eingegeben werden. Da dies jedoch aufwendig ist, bietet
Referenz-ERP
das System der
Musterkunden
an.
Im obigen Beispiel würde man zwei Musterkunden mit den
Namen Bauunternehmen und Landwirt anlegen und ihnen jeweils sämtliche Parameter
zuordnen. Bei der Erfassung eines Landwirts wird dann der "Knopf" Musterkunde
betätigt, Landwirt ausgewählt und es erscheint die bereits vollständig mit
Parametern ausgefüllte Erfassungsmaske, die jetzt lediglich um die Felder
Kundennummer, Anschrift, etc. ergänzt werden muss.
Anlegen eines Musterkunden
Die Neuanlage entspricht exakt der Kundenneuanlage. Im
Feld "Kundentyp" muss angegeben werden, dass es sich um einen "Muster - Debitor"
handelt. Zusätzlich empfiehlt es sich, im Feld "Name" eine aussagekräftige
Bezeichnung, z.B. Landwirt - Muster, zu verwenden. Über diese Bezeichnung
erfolgt später die Suche nach Musterkunden.
Musterkunden in der Auswahlliste
Um sich Musterkunden in der Auswahlliste anzeigen zu
lassen, wird die Anzeigevariante "Musterkunde" aktiviert. Danach werden die
eingetragenen Musterkunden angezeigt und können, z.B. für Korrekturen,
aufgerufen werden.
Andere Muster
Muster gibt es für alle Typen der Kunden- /
Lieferantenstammerfassung, also:
Musterkunden, - Musterkontokorrentkunden, -
Musterinteressenten, - Musterlieferanten

---

## Erlösklasse

Erlösklasse
Hauptmenü
Administration
Erlöskennziffern
Erlösklassen
oder Direktsprung
[ERLK]
Mit Hilfe der Erlösklasse lassen sich für verschiedene
Kundengruppen unterschiedliche Erlös- und Aufwandskonten festlegen
(Profit-Center). Die Erlösklasse wird im Kundenstamm hinterlegt. Wenn eine
solche Differenzierung nicht erwünscht ist, kann die Einrichtung entfallen.
Beispiel:
Differenzierung der Umsätze nach
Inland und Export
Es werden zwei Erlösklassen eingerichtet: Inland und
Export
Diese werden den Kunden im Kundenstamm unter FiBu
Merkmale zugeordnet

---

## Fakturiergruppe

Fakturiergruppe
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Fakturiergruppe
Direktsprung
[FGR]
Die Fakturiergruppe kann als Selektionsmerkmal
eingerichtet werden. Sie wird der Hauptmaske des Kundenstamms zugeordnet und
kann z.B. bei der Rechnungsbearbeitung ausgewertet werden. Ein Beispiel:
Selektion nach Kunden mit den Merkmalen
Tagesrechnung
Wochenrechnung
Monatsrechnung

---

## Forderungsgruppe

Forderungsgruppe
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Forderungsgruppe
Direktsprung
[FORG]
Bei den
Forderungsgruppen
handelt es sich um
Stammdaten, die von der Finanzbuchhaltung benötigt werden.

---

## Datenbankfunktion für Verteilung

Datenbankfunktion für
Verteilung
Es besteht ferner die Möglichkeit, eine eigene
Datenbankprozedur zur automatisierten Partiezuordnung  zu erstellen. Ein
detaillierte Beschreibung kann derzeit noch nicht geliefert werden - bitte mit
der Entwicklung Kontakt aufnehmen.
Ein Beispiel findet man unter ‚Beispiele
für Datenbankfunktionen’
Man hat die Möglichkeit die private Datenbankfunktion
mit F3 auf dem Feld auszuwählen. Ist das Feld gefüllt erscheint in der Option
Box die Möglichkeit mit SHIFT+F8 die zu übergebenen Parameter an die Funktion
auszuwählen. Hier wird also festgelegt welche Informationen für die Funktion zur
weiteren Verarbeitung gebraucht werden. Da jeder Anwender andere Ansprüche hat
wurde hier die Möglichkeit geschaffen die Parameter variabel zu halten.
Beispiel hier

---

## Google Maps

Google Maps
Aus den Auswahllisten Kunden, Anschriften, Lieferanten
und Kontokorrentkunden ist die Funktion
Google Maps
verfügbar. Hier kann entweder
der Standort oder eine Strecke zwischen den markierten Anschriften (Bei Kunden
deren Hauptanschrift) in der Reihenfolge des Anklickens mit Hilfe von Google
Maps angezeigt werden.

---

## Hauptmaske

Hauptmaske
Stammdatenpflege
Kunden-/Lieferantenstamm
Kundenstamm
Der Aufbau der Kunden und Lieferanten Stammdaten soll
exemplarisch am Beispiel des Kundenstamms erläutert werden. Auf Unterschiede
wird separat eingegangen. Folgende Informationen werden in Abhängigkeit von der
Anwendung in der Hauptmaske erfasst:
Nummer
Achtung:
Eine Kontonummer kann nur einmal vergeben werden!
Auch wenn ein Kunde gelöscht wird, kann diese
Kontonummer nicht erneut vergeben werden.
Dies ist der sichtbare (logische) Kundenschlüssel für
Sortierungen und Selektionen.
Die Kunden-/Lieferantennummer ist eindeutiges
Suchkriterium. Die Länge der Nummer kann in den Steuerparametern
[SPA]
eingestellt
werden; die Voreinstellung beträgt
8
Stellen Eine sichere Verwaltung des Kundennummernbereiches wird
über einen im Mandantenstamm hinterlegten Nummernkreis gewährleistet. Darüber
hinaus kann in den
[SPA]
bestimmt werden,
dass bei einer Neuanlage immer die nächste freie Nummer vorgeschlagen wird.
Kurzbezeichnung
Kurzbezeichnung des Kunden für Listen etc.;
vorgeschlagen wird der Nachname.
Matchcode
Suchbegriff für diesen Kunden; vorgeschlagen wird der
Nachname.
Gegen-Nummer
Die Kontonummer für Kunden/Lieferanten wird von Referenz-ERP
je nach Einstellung vergeben. Bei diesen Kunden existiert unsere Firma jedoch
auch als Lieferant/Kunde mit einer eigenen Kontonummer. Diese Nummer wird hier
eingetragen. Sie wird z.B. beim DTA verwendet oder kann beim Vorgangsdruck mit
ausgegeben werden.
Kundentyp
Debitor: Über das Konto werden ausschließlich Verkäufe
abgewickelt
Kontokorrent: Kunde und Lieferant in einer Person,
über das Konto werden Verkäufe und Einkäufe abgewickelt
Interessent: über das Konto werden keine Verkäufe
abgewickelt; die Daten stehen aber z.B. für Marketingmaßnahmen zur
Verfügung.
Muster – Debitor: dient als Standardvorbelegung für
die Debitorenerfassung
Muster – Interessent: dient als Standardvorbelegung
für die Interessenerfassung
Anschrift
Erfassung der Adressinformation de
[...]


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

## Projektverwaltung

Projektverwaltung
Projektverwaltung ist ein Kundenbezogenes Werkzeug zur
Aufnahme, Bearbeitung und Kontrolle von Kundenbezogenen Projekten. Innerhalb
dieses Bereiches können pro Kunde beliebig viele Projekte zu verschiedenen
Zuständen geführt werden, dabei sind Kennzeichen und Objekte wie z.B.
Datumseingaben
Benachrichtigungseingaben
Weiterleitungsinformationen
Wiedervorlageinformationen
Abrechnungsinformationen
Textblockinformationen
Dokumentenverwaltungsinformationen
pflegbar und einsehbar.

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

## Individuelle Preise

Individuelle Preise
Ein individueller Preis eines Artikels für einen
Kunden oder von einem Lieferanten wird durch die Angabe einer individuellen
Preisgruppe im Artikel und einer individuellen Preisklasse im
Kunden-/Lieferantenstamm jeweils im Einkauf bzw. Verkauf zugeordnet. Für die
dadurch festgelegte Gruppen-Klassen-Kombination wird ein Preis oder eine
mengenabhängige Preisstaffel gepflegt. Diese Preisangaben werden zusätzlich über
einen Gültigkeitszeitraum (Ab-Datum, Bis-Datum) qualifiziert. Der Datenraum
individueller Preise ist quasi ein Würfel mit den Dimensionen
Ab-Menge
,
Ab-Datum
und
Preis
:
Die weiteren Dimensionen sind (oben nicht dargestellt)
der
Artikel
(ausgedrückt über die individuelle Preisgruppe) und der
Kunde
(ausgedrückt über die individuelle Preisklasse).
Die Pflege der individuellen Preise folgt diesem
Dimensionenkonzept: werden die Dimensionen Preisgruppe
und
Preisklasse
fixiert, gelangt man zum
Einzelsatzpfleger
für individuelle Preise/Rabatte im Verkauf
[PRI]
und Einkauf
[PRIE]
,
wird eine der
fixierten Dimensionen
freigegeben
(Preisgruppe frei
à
Artikel frei wählbar
à
Einstieg über den festen
Kunden/Lieferanten oder Preisklasse frei
à
Kunde frei wählbar
à
Einstieg über den festen Artikel)
benötigt man den sogenannten
Preisstapelpfleger
für individuelle
Preise.

---

## Einrichtung der Privaten Prüfmethode für das Land Kennzeichen im Swift und in der IBAN

Einrichtung der Privaten Prüfmethode für das Land Kennzeichen im Swift und
in der IBAN
Mit dieser Prüfung soll verhindert werden, dass sich
das Landkennzeichen in einer IBAN von dem Landkennzeichen im Swift Code von der
Bank unterscheidet. Des Weiteren soll beim Speichern des Kunden geprüft werden,
ob das Landkennzeichen des Kunden zum Landkennzeichen der Bank passt.
Aber es gibt Ausnahmen die trotz negativer Prüfung das
Speichern der Daten zulassen.
Folgende Punkte können am Kunden nach der AIS
Einrichtung ausgewählt werden.
1.
Vendor
2.
Ocean Freight vendor
3.
Goods/Services delivered from same country as bank country
4.
Must have Beneficial ownership from a record
Des Weiteren kann es vorkommen, dass der Swift Code
der Bank ein anderes Landkennzeichen enthält als das Landkennzeichen in der IBAN
z.B. der IBAN Country Code ist GB und der Swift Country Code ist IM für die Isle
of Man. Diese Liste ist im AEZ zu pflegen. Diese Liste wird beim Speichern mit
den zu speichernden Daten verglichen. Wurden unterschiedlich Länderkennung in
der IBAN und in dem Swift angegeben und diese  Kombination steht  in
der Ausnahme Liste so wird  der Datensatz gespeichert andernfalls nicht
Einrichtung
Es müssen folgende Punkte eingerichtete werden.
Optionen
Hauptmenü
Administration
Steuerung
Optionen
oder Direktsprung
[OPT]
Um diese Option anzulegen wird mit
F8
oder
Neu
der Pfleger geöffnet. Als Option Name
wird dann „
Pruefe_Bankstaat
“ ausgewählt. Unter Bediener wird
eingetragen für welchen Bediener diese Option zur Verfügung steht. Als Wert wird
der Name z.B.
p_pruefe_bank_staat
der Prüf Prozedur
eingetragen.
AIS
Hauptmenü
Administration
Werkzeuge
Informationssystem
oder Direktsprung
[AIS]
Im AIS müssen vier Eingabefelder vom Feldtyp
„Check-Box“ angelegt werden. Der Name der Gruppe zu diesen Feldern kann z.B.
lauten Kundenaddon004.
Die Namen der Felder müssen wie folgt heißen:
1.
ADMVendor
2.
OceanFVendor
3.
BankCtryisGoodsCtry
4.
Beneficialo
[...]


---

## Druckereinrichtung

Druckereinrichtung
(Besonderheiten bzgl. Terminalserver sind fett
geschrieben)
Wenn eine Kasse als Terminalserver eingerichtet ist,
gibt es Besonderheiten bei der Einrichtung, deren Umsetzung einen reibungslosen
Betrieb gewährleisten kann.
Diese Besonderheiten sind insbesondere auf die
Ansteuerung des lokal angeschlossenen Bondruckers zurückzuführen.
Soweit noch nicht geschehen, sollte der zu verwendende
Drucker mitsamt seinen Steuersequenzen in die entsprechenden Pfleger eingespielt
werden. Für die Kasse stehen dabei mehrere SQL-Dateien zur Verfügung, die das
Befüllen dieser Tabellen für den Anwender übernehmen, d.h. es besteht die
Möglichkeit, über OSQL folgende Drucker einzuspielen (Bem.: Gewisse Modelle sind
bereits auf der Basisdatenbank hinterlegt und müssen daher nicht eingespielt
werden):
Epson_bon.sql: Für den Bondruckkanal eines EPSON TM930
Models
Epson_schacht.sql: Für den Bonschachtkanal eines EPSON
TM930 Models
Oki_bon_sql: Für den Bondruckkanal eines OKI POS90
Bondruckers
Oki_schacht.sql: Für den Bonschachtkanal eines OKI
POS90 Bondruckers
Sni_bon.sql: Für den Bondruckkanal eines SNI ND69
Bondruckers
Sni_schacht.sql: Für den Bonschachtkanal eines SNI
ND69 Bondruckers
Star.sql: Für den Bondruckkanal eines Stardruckers
(dort gibt es keinen Schacht)
Dabei ist dann nur eine freie Druckernummer
einzugeben. Dabei entspricht der _bon.sql der Ansteuerung des Druckers für die
Bonrolle und der _schacht.sql der Ansteuerung des Druckers für den Schacht.
In der Referenz-ERP-Druckansteuerung im Bereich Kasse gibt
es mehrere Wege:
Druck von normalen Barverkäufen (über Direktsprung
BVVE bzw. über POS-Kasse) auf dem normalen Bondrucker.
Druck von Belegen über Geldeinzahlungen, Einreichungen
zur Bank, Zählbericht, ...
Druck von zusätzlichen Belegen über
Geldeinzahlungen,... mit Formularen 51-55, die in FRZ hinterlegt sind auf dem
Bonschacht – zusätzlich als „große Quittung“ zu b)
Druck von Schecks, EC-Lastschriften
Im Normalfall sieht die Ansteuerung w
[...]


---

## Kennzeichen

Kenn
zeichen
Verschiedene Funktionalitäten in
Referenz-ERP
werden über die Kundenkennzeichen gesteuert:
Feld
Beschreibung
Diverses Konto
Das
      Konto steht für die Abwicklung von Kunden, für die kein eigenes Konto
      geführt werden soll, zur Verfügung. Beim Aufruf dieses Kunden zur
      Fakturierung wird automatisch die Adressmaske zur Eingabe der
      Anschriftdaten geöffnet.
Diese Funktion sollte allerdings, da
      sie unter Verzicht auf viele Informationsmöglichkeiten eingesetzt wird,
      sehr sparsam verwendet werden
Barverkauf Konto
Z.Z.
      nicht aktiv.
Sammelrechnung
Es
      kann eingestellt werden, ob ausschließlich Sammel- oder Einzelrechnungen
      erstellt werden oder es fallabhängig ist.
Bruttorechnung
Bei
"J"
erhält der Kunde Bruttorechnungen,
      d.h., alle Beträge — auch die Einzelpreise — werden brutto
      ausgewiesen
KoKoRe
Dieses Kennzeichen wird gesetzt,
      wenn mit dem Kunden ein Kontokorrentverhältnis besteht.
Das bedeutet,
      der Kunde ist sowohl Lieferant/Hersteller als auch Kunde. Sehen Sie hierzu
      auch Kundentyp, im Vorgangsbereich
"Kontokorrent"
und in der
      Funktion
"FIBU-
      Merkmale"
den
      Zinsbereich.
Versandanschrift
Dieses Feld hat keine steuernde
      Bedeutung in Referenz-ERP.
Es
      kann frei verwendet werden!
Raffung
Z.Z.
      nicht aktiv.
Rabattsperre
ZZ.
      nicht aktiv.
Liefersperre
Bei
      einer weichen Liefersperre wird bei dem Versuch, den Kunden zu beliefern,
      eine Warnung angezeigt. Die Lieferung ist aber trotzdem möglich.
Bei einer harten Sperre
      dagegen ist der Kunde komplett für Lieferungen gesperrt.
Bei
      der Umwandlung von Belegen ist es jedoch möglich, auch Belege dieser
      Kunden weiterzuverarbeiten (z.B. in Rechnungen umwandeln), die eine
      Liefersperre haben. Das ist sinnvoll, damit alte Belege, die ohne
      Liefersperre erfasst wurden, auch noch umgewandelt werden können. Neue
      Belege können nicht mehr erzeugt werden. D
[...]


---

## Konstanten / Bearbeitung

Konstanten / Bearbeitung
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
In Abhängigkeit vom Einsatzgebiet können folgende
Konstanten bei der Anlage des Kundenstamms von Bedeutung sein:

---

## Importmapping

Importmapping
Hauptmenü
Stammdatenpflege
Kunden / Lieferanten
Kundenstamm
Direktsprung
[KU]
Wenn ein Vorgang importiert werden soll, so kann von
extern eine Nummer für einen Kunden und dessen Versandanschrift vergeben worden
sein.
Diese Fremdkundennummer wird durch dieses Mapping bei
Belegeingängen zu einer Kundennummer und einer Anschrift in Referenz-ERP zugeordnet
(gemappt).
Die Einträge werden bei jenem Kunden gepflegt, der die
Belege überträgt und die Fremdkundennummer verwendet.

---

## Interessenten

Interessenten
Hauptmenü
Stammdatenpflege
Kunden-/Lieferanten
Interessentenstamm
oder Direktsprung
[IN]
Hier werden Interessenten erfasst. Die Erfassung in
der Maske entspricht der von Kunden (siehe dazu
Hauptmaske
unter Kunden- und
Lieferantenstamm).
Interessenten können später durch die Funktion
‚Interessent -> Kunde‘ zu Kunden bzw. Kontokorrent-Kunden umgewandelt
werden.

---

## Kundenbanken

Kundenbanken
Hauptmenü
Stammdaten
Konstanten Kundenstamm
Kundenbanken
oder Direktsprung
[KUBA]
Alle Grunddaten der Banken, mit denen das System zu
tun hat, werden im allgemeinen Bankenstamm hinterlegt, egal ob es sich um eigene
Hausbanken oder um Banken von Kunden, Lieferanten, Vertretern... handelt.
Hierdurch wird vermieden, dass immer wiederkehrende Informationen, wie die
Bankleitzahl, wiederholt werden müssen.
Die spezifischen Eingaben der Kundenbankdaten werden
im Auswahlbildschirm Kundenbank
erfasst,
der über den Direktsprung
[KUBA]
zu erreichen ist.
In der Stammdatenmaske können folgende Daten
eingegeben werden.
Felder
Kunde
Hier
      kann aus dem Kundenstamm ein Kunde ausgewählt werden, für den die
      folgenden Einstellungen gemacht werden sollen.
IBAN
Die
      „International Bank Account Number“ - kurz IBAN- wird im Zahlungsverkehr
      immer wichtiger. In dem ab dem 28.01.2008 gestarteten SEPA Verfahren wird
      sie an Stelle der Kontonummer verwendet. Bei der Erfassung der
      Kundenbanken wird die IBAN für deutsche, österreichische und belgische
      Banken anhand eines Prüfzifferverfahrens überprüft.
Der
      Test der IBAN kann entweder für jede
Bank
oder global per
Steuerparameter
abgeschaltet werden.
In
      der IBAN ist die Bankleitzahl und Kontonummer enthalten. Anhand der
      Bankleitzahl wird der Bankenstamm durchsucht und dann die Bank und
      Kontonummer eingetragen. Wird keine Bank vorgeschlagen ist entweder der
      Bankenstamm nicht korrekt gepflegt oder die IBAN ist nicht korrekt
      aufgebaut.
Die
      IBAN kann nachträglich über ein Funktion „Generiere IBAN“ für alle
      Kundenbanken mit eingetragener Bank und Kontonummer erzeugt
      werden.
Bank
Banknummer und Text. Eine Auswahl
      mit
F3
ist möglich
BIC
      / BLZ
Hier
      wird die BIC(Swift) der Bank wird angezeigt. Steht der
Steuerparameter
1121 „Bankleitzahl und
      Kontonummer anzeigen“ auf
Ja
, so wird hier auch die BLZ

[...]


---

## Kundenbescheinigung

Kundenbescheinigung
Für jeden Aktionär kann aus den Listen
„Aktionärsübersicht“, „Gesamtliste“ und „Aktionärsdividende“ über der Funktion
Kundenbescheinigung
eine
Bescheinigung über den Aktienbesitz eines Aktionärs an einem Bestimmten Datum
erstellen. Nach Anwahl der Funktion können mit
F2
das Datum und die Aktionäre, für die
Bescheinigung erstellt werden soll, angegeben werden.

---

## Kundengruppen

Kundengruppen
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Kundengruppen
Direktsprung
[KUG]
Hierbei handelt es sich um ein reines
Selektionskriterium, das für Auswertungen etc. genutzt werden kann. Anzugeben
sind die Gruppennummer und eine Bezeichnung. Die Gruppennummer wird direkt im
Kundenstamm oder über den Anwahlpunkt "Kundengruppenzuordnung" dem Kundenstamm
zugeordnet werden. Für eine bessere Übersicht über die Struktur von Forderungen
und Verbindlichkeiten können den Kunden Gruppen zugeordnet werden. Dies kann
z.B.
„Großkunden“, „Landwirte“, „Baustoffhändler“
etc. sein. Ausgewertet
werden diese Informationen z.B. in speziellen Kundenlisten.

---

## Kundenindividuelle Artikelnummern

Kundenindividuelle Artikelnummern
Wenn für bestimmte Abnehmer eigene Artikelnummern
hinterlegt werden, so können diese hier gepflegt werden. Diese Nummern können im
Vorgang z.B. mit ausgedruckt werden.

---

## Kundengruppenzuordnung

Kundengruppenzuordnung
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Kundengruppenzuordnung
Direktsprung
[KUGR]
Die Zuordnung eines
Kunden zur Kundengruppe erfolgt in den Kundenstammdaten oder über den
Anwahlpunkt „Kundengruppenzuordnung“. Es ist hier nach der Kundennummer
lediglich die Gruppe anzugeben
.

---

## Kundenmapping

Kundenmapping
Hauptmenü
Stammdatenpflege
Kunden-/Lieferanten
Kundenmapping
In der Kommunikation zwischen Datenaustauschpartnern
kann es notwendig sein, ein Mapping für Kundennummern zu machen. So wird im
Austausch mit dem ausgewählten Kunden von diesem eine Fremdkundennummer
verwendet, die hier eigenen Kunden/Lieferantennummer zugeordnet werden kann.
Diese Daten können zum Beispiel im Vorgangsimport
verwendet werden.
Felder
Fremdkundennummer
Kundennummer, wie sie der gewählte
      Kunde verwendet
Kundennummer
Kunden/Lieferantennummer, die im
      lokalen System verwendet wird
Kundenbezeichnung
Bezeichnung für den
      Kunden

---

## Kundensummen

Kundensummen
Information über die Jahres- und Vorjahresumsätze.

---

## Kunden- und Lieferantenstamm

Kunden- und Lieferantenstamm
Hauptmenü
Stammdaten
Kundenstamm
Direktsprung
[KU]
Oder
Hauptmenü
Stammdaten
Lieferantenstamm
Direktsprung
[LF]

---

## Kundenzahlungsbedingungen

Kundenzahlungsbedingungen
Hauptmenü
Stammdaten
Konstanten Kundenstamm
Kundenzahlungsbedingungen
Direktsprung
[KUZB]
Der Zahlungsbedingungs-Stamm enthält alle notwendigen
Informationen für Berech­nungen und Ausdruck der Zahlungsbedingungen.
Normale Zahlungsbedingungenen kommen mit einem einzigen Satz aus, bei komplexen
Bedingungen wird jeweils eine Folge-Zahlungsbedingung definiert. Die Art der
Berechnung ergibt sich aus der Zahlungsbedingungsfolge.
Kunde:
Eingabe der entsprechenden Kundennummer
Haupt-Warengruppe:
Zahlungsbedingungen können pro Haupt-Waren­gruppen
unterschiedlich sein. Bei der Umwandlung von Lieferscheinen in Rech­nungen
wird dann immer eine Belegtrennung erfolgen. Für den Standardfall ist hier 0 =
keine unterschiedliche Behandlung einzutragen.
Zahlungsbedingung VK
und
Zahlungsbedingung EK:
Eingabe der Zahlungsbedingungsnummer. Eine Auswahl aus
den bestehenden Zahlungsbedingungen ist mit
F3
möglich.

---

## Kundenversandanschriften

Kundenversandanschriften
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Kundenversandanschriften
oder Direktsprung
[KUVS]
Gibt es zu einer Rechnungsanschrift mehrere
Lieferempfänger, so können verschiedene Versandanschriften hinterlegt werden,
die dann innerhalb der Belegerfassung zum Einsatz kommen.
Für die Nachhaltigkeitsvorbelegung kann hier ein
Anbauland hinterlegt und gespeichert werden. Bei der Belegerfassung, kann dann
auf einem UFLD-Feld(108) die Kundenversandanschrift angegeben werden. Dadurch
kann bei richtiger Einrichtung das in der Versandanschrift hinterlegte Anbauland
gezogen werden.
Im Kunden muss also ein Nachhaltigkeitszertifikat
existieren und der gewünschte Artikel muss in Verbindung mit dem Anbauland aus
der Versandanschrift übereinstimmen. Ansonsten wird das Anbauland aus der
Versandanschrift ignoriert.
An Versandanschriften sind keinerlei Informationen
geknüpft, es handelt sich um reine Anschrifteninformation. Wenn gewünscht wird,
Statistiken an Lieferanschriften zu binden, so ist es sinnvoll, im Kundenstamm
mit Oberkundenbeziehungen zu arbeiten.
Im linken Bereich des Eingabebildschirms wird die
Kundenadresse angezeigt und im rechten die Versandanschrift. Zusätzlich wird die
Anzahl der Versandanschriften pro Kunde angezeigt. Wird dieser Pfleger aus dem
Kundenstamm heraus aufgerufen, so kann man mit den Pfeiltasten zwischen den
Versandanschriften des aktuellen Kunden blättern.
Felder
Gruppe (Intra)
Intrastatgruppe des zugehörigen
      Kunden. Dieses Feld ist nur private Zwecke nutzbar, die offizielle
      Intrastat - Meldung benutzt dieses Feld nicht.
ILN-Nr
ILN
      Nummer dieser Adresse
Hat man zu einem Kunden sehr viele Versandanschriften,
so kann über die Funktion
Suchen
F6
nach Name, Straße und/oder Ort
innerhalb der Versandanschriften dieses Kunden gesucht werden. Auf der sich
öffnenden Suchmaske können entweder bis zu drei Kritieren direkt angegeben
werden oder man sucht mit
F3
über die Itembox.
Beim Löschen v
[...]


---

## Lieferanten / Hersteller

Lieferanten / Hersteller
Die Möglichkeiten zum Pflegen von Lieferanten und
Herstellern findet sich unter Kundenindividuelle Artikelnummern.

---

## Listenpreise

Listenpreise
Ein Listenpreis eines Artikels für einen
Kunden/Lieferanten wird durch die im Artikel hinterlegte
Listenpreisgruppe
(getrennt für
Einkauf und Verkauf), der im Kunden-/Lieferantenstamm hinterlegten
Preisklasse
(getrennt für Einkauf und Verkauf) und der im Artikel hinterlegten
Preismatrix
(getrennt für Einkauf und Verkauf) bestimmt. Dabei werden mit der Preismatrix
eine oder mehrere Preisklassen (und damit in der Regel mehrere
Kunden/Lieferanten) für Artikel mit dieser Preismatrixnummer genau einer
Listenpreisdefinition
zugeordnet. Für alle Artikel gleicher
Listenpreisgruppe gilt der unter dieser Listenpreisdefinition gespeicherte
Preis, gegebenenfalls noch unterschieden nach Gültigkeitszeitraum und, falls in
der Listenpreisgruppe die Staffelpreisnummer einer
Listenpreis-Staffel
festgelegt
ist, mengenabhängig ausgelegt. Die eigentlichen Listenpreise werden im Modul zur
Listenpreispflege
bearbeitet.

---

## Listen / Auswertungen

Listen / Auswertungen
In den Bereichen Informationssystem / Auswertungen /
Auswahlliste Kundenstamm stehen zahlreiche Stammdatenlisten und
betriebswirtschaftliche Auswertungen zur Verfügung.

---

## Umpacken

Umpacken
Grundsätzlich wird im Referenz-ERP-LVS2.0 nur sortenrein auf
einem Ladeträger gelagert. Ausnahme bilden hier nur Ladeträger, die zum Versand
an einen Kunden bestimmt sind. Somit ist auf jedem Ladeträger nur Material EINES
Artikels und EINER Partie vorhanden.
Nun kann es notwendig sein, Material aus Platzgründen
zusammenzufassen und von einem Ladeträger auf einen anderen umzupacken.
Empfohlener Arbeitsablauf Scanner:
•
Scan „UMPACK“
•
Scan der Quell-NVE
o
Anzeige der NVE-Info
•
Scan der Ziel-NVE
o
Prüfung auf Kompatibilität der
Inhalte
o
Erzeugen einer Umpackung im
VIMP

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

## Neuer Interessent SF8

Neuer Interessent SF8
Die Funktion
Neuer Interessent
SHIFT+F8
öffnet die Anschriftenmaske für
eine neue Kunden-Hauptanschrift eines Interessenten. Das Feld Vererben wird
dabei mit Ja vorbelegt (siehe auch
Vererbung
)
Nach Eingabe der Daten wird beim Speichern der
Anschrift im Hintergrund der dazugehörige Kundendatensatz (Typ 4/Interessenten)
angelegt. Dieser ist entweder eine Kopie des zuletzt angelegten Kunden oder
eines Musterkunden. Die Kundennummer des Musterkunden kann im EPA „Kundennummer
eines Musterkunden für neue Interessenten“ hinterlegt werden. Erfolgt dort keine
Eingabe, wird automatisch eine Kopie des zuletzt angelegten Kunden erstellt. Die
Kundennummer für den neuen Kundendatensatz wird aus dem Nummernkreis für
Interessenten im Mandantenstamm geholt. Das Feld Kunde auf der Anschriftenmaske
wird beim Öffnen damit vorbelegt.
Ist kein Nummernkreis für Interessenten hinterlegt,
muss eine neue Kundennummer im Feld Kunde eingegeben werden.
Soll nach dem Abspeichern der neu angelegte
Kundendatensatz zum Bearbeiten geöffnet werden (z.B. für den Eintrag der
Vertretergruppe), ist es ratsam, den EPA „Beim Speichern eines Interessenten den
Kundenpfleger aufrufen“ auf ‚JA’ zu setzen, um dann direkt den entsprechenden
Kundenstamm zu öffnen (Vorbelegung ist ‚JA’).

---

## Neuer Ansprechpartner F8 (Anschriften)

Neuer Ansprechpartner F8 (Anschriften)
Wählt man die Funktion
Neuer Ansprechpartner
, dann wird ein neuer
Ansprechpartner zur Kunden-Hauptanschrift des markierten Datensatzes
angelegt.
Inhalte der Felder werden von der Kunden-Hauptanschrift übernommen
und zu vererbende Felder für Änderungen gesperrt. Siehe dazu auch Vererbung.

---

## Oberfläche – Kunden

Oberfläche – Kunden
Auf der Registerkarte
Kunden
werden die Kunden angezeigt, bei
welchen dieses Profil und die damit verbundenen Prozeduren greifen sollen.
Um hier einen Kunden zuzuordnen muss im Kundenstamm
[KU]
auf dem Register
eRechnung
das entsprechende Profil
angegeben werden.
Im Modus
Neu
ist die Registerkarte nicht
vorhanden.
Auf der Registerkarte
Kunden
sind folgende Felder zu sehen:
Felder
Nummer
Die
      Kundennummer des Kunden
Bezeichnung
Die
      Bezeichnung des hinterlegten Kunden

---

## Oberkunden

Oberkunden
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Oberkunden
oder Direktsprung
[KUOB]
In einigen Branchen ist es üblich, dass der
Warenempfänger nicht gleichzeitig der Rechnungsempfänger ist. Es bestehen so
genannte Verrechnungsketten. An die Verwaltung / EDV sind daher bestimmte
Voraussetzungen geknüpft:
Der Lieferschein soll über den Unterkunden lauten, die
Rechnung muss über den Oberkunden ausgestellt werden. Das heißt, die Verbuchung
im Rechnungsausgangsbuch und in der Fibu erfolgt über den Oberkunden. Die
Verbuchung im Waren­buch erfolgt über den Unterkunden.
Wenn gewünscht wird, Statistiken an Lieferanschriften
zu binden, so ist es sinnvoll, im Kundenstamm mit Oberkundenbeziehungen zu
arbeiten.
Folgende Eintragungen sind erforderlich:
Mit diesen Eingaben werden über den Kunden „Testkunde“
erfasste Lieferscheine bei der Umwandlung in Rechnungen mit der Anschrift
„Mustermann“ versehen. Alle Statistiken verbleiben jedoch bei „Testkunde“.
Hinsichtlich der Finanzbuchhaltungsbuchung hat sich
mit diesen Eintragungen auch noch nichts geändert. Um hier die Umlenkung auf
„Mustermann“ zu erreichen, ist eine Eintragung unter „Zahlungspflichtiger“
erforderlich.

---

## Partie-Bewegung (DRUCK)

Partie-Bewegung (DRUCK)
Hauptmenü
Partieverwaltung
Auswertung
Partie-Bewegung
Diese Auswertung informiert hauptsächlich über den
bewerteten Erfolg einer Partie. Aus Zugangsmengen- und Werten wird dieser
ermittelt. Weitere Details sind Kunden- und Lieferantenbelege mit Datum, Lager,
Bewegungsart und einiges mehr.

---

## Profil Verwaltung: Pfleger

Profil Verwaltung: Pfl
eger
E-M
ail-Profil
Feld
Beschreibung
Id
Die
      Id des Profils, readonly
E-Mail-Adresse
Die
      E-Mail-Adresse des Postfachs
Passwort
Das
      Passwort für den Zugriff auf das Postfach
Client Id
Ermöglicht die eindeutige
      Identifizierung der Anwendung in Microsoft Identity Platform. Sie wird bei
      der Überprüfung der von Identity Platform empfangenen Sicherheitstoken
      herangezogen.
Weitere Informationen findet man
      unter:
https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
Client Secret
Bei
      einem geheimen Clientschlüssel handelt es sich um einen Zeichenfolgenwert,
      der anstelle eines Zertifikats von Ihrer App für die Identifizierung
      verwendet werden kann.
Weitere Informationen findet man
      unter:
https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
Tenant Id
Ein
      Mandant stellt eine Organisation dar. Hierbei handelt es sich um eine
      dedizierte Instanz von Azure AD, die eine Organisation oder ein
      App-Entwickler zu Beginn einer Beziehung mit Microsoft erhält. Diese
      Beziehung kann beispielsweise mit der Registrierung für Azure, Microsoft
      Intune oder Microsoft 365 beginnen.
Weitere Informationen findet man
      unter:
https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-create-new-tenant
Domäne
Die
      Domäne des Dienstes
Wichtig
: Bei Verwendung von Microsoft Graph
      zur Versendung von Mails muss hier der Wert graph.microsoft.com
      eingetragen werden.
Port
Der
      Port für die Kommunikation mit dem Dienst
SSL
      verwenden
Ja/Nein
Excel als PDF/A
Ja/Nein – Sollen angehängte
      Excel-Dokumente in das PDF/A-Format für Langzeitarchivierung konvertiert
      werden?
Plugin Name
Es
      kann zwischen IMAP, Webservice und Graph gewählt werden.
Wichtig
: Bei Auswahl von Graph muss in das
      Feld Domäne der Wert graph.microsoft.com eingetra
[...]


---

## Profil Verwaltung

Profil Verwaltung
Direktsprung
[EMAIL]
Felder der Profil Verwaltung
Feld
Beschreibung
Id
Die Id des
      Profils.
E-Mail-Adresse
Die Adresse des
      Postfachs.
Domäne
Die Domäne des
      Dienstes über den das Postfach ausgelesen werden kann.
Webservice-Url
Die vollständige
      Adresse des Webservices über den das Postfach ausgelesen werden
      kann.
Suchmöglichkeiten der Profil Verwaltung
Feld
Beschreibung
Id
Die Id des
      Profils.
E-Mail-Adresse
Die Adresse des
      Postfachs.
Domäne
Die Domäne des
      Dienstes über den das Postfach ausgelesen werden kann.
Webservice-Url
Die vollständige
      Adresse des Webservices über den das Postfach ausgelesen werden
      kann.
Funktionen der Profil Verwaltung
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
Ruft den
Pfleger
der Profil Verwaltung
auf

---

## Replikationsadressen

Replikationsadressen
Felder
Betrieb
Enthält die Nummer des ausgewählten
      Betriebes oder der Filiale gefolgt von dessen Bezeichnung.
Zentrale
Ja /
      Nein
Wird
      automatisch gesetzt und zeigt an ob es sich bei der im Feld Betrieb
      angegebenen Nummer um die Zentrale Betriebsstätte handelt oder
      nicht.
Übergeordnet
Wird
      automatisch gesetzt und zeigt an welche Betriebsstätte in der Hierarchie
      die nächste übergeordnete Betriebsstätte ist.
Sprache
Auswahl der Sprache für diese
      Betriebsstätte
Untergeordnete
      Betriebsstätten
Übersicht der in der Hierarchie
      untergeordneten Betriebsstätten. Wird automatisch gesetzt.
Erfassung für fremde
      Filiale
Grundmuster für die Datenabgabe an
      untergeordnete Betriebsstätten ( nur Ersteinrichtung )
Zeigt die Publikationen und in
      welcher Form die Datenabgabe an die untergeordneten Betriebsstätten
      erfolgt.
-
Benutzerdefiniert
-
Komplett
-
Vorgänge je
      Filiale
Adressen für einkommende
      Meldungen
MAPI:
(wird technisch nicht mehr
      unterstützt)
FILE: Verzeichnis für einkommende
      Meldungen des Nachrichtensystems
Interne Identifikatoren
Untergrenze: Untergrenze für Idents
      innerhalb der Betriebsstätte
Obergrenze: Obergrenze für Idents
      innerhalb der Betriebsstätte
Beispiel:
-
Zentrale: 0 –
      999999
-
Filiale 1: 1000000 –
      1999999
-
Usw.
Funktionen
Speichern
Speichert die Angaben
Anschrift
Öffnet den Stammdatenpfleger für
      Anschriften

---

## Saatzucht

Saatzucht
Auf der Registerkarte „Saatzucht“ werden die
Saatzuchtdaten des Kunden gepflegt.
Feld
Beschreibung
VO-Firma
Identifikation zum Kundenstammsatz
      der VO - Firma (Vemehrerorganisation). Mit der F3-Taste kann hier eine
      Auswahl aufgerufen werden.
Anerkennungsstelle
Mit
      der F3 -Taste
kann hier eine Auswahl aufgerufen
      werden
.
Vermehrerkennziffer
Kennziffer des
      Vermehrers
Aufbereiter
Die
      Kundennummer des Aufbereiters. Mit der F3-Taste kann hier eine Auswahl
      aufgerufen werden.
Aufb. Kennziffer
Die
      bundesweite gültige Aufbereiterkennziffer.

---

## Kundenspezifische Scannermodule

Kundenspezifische
Scannermodule
Die mittels Scanner erfassten Daten werden in den
Vorgangsimport Tabellen gespeichert. In der Anwendung
Vorgangimport
[VIMP]
Hauptmenü
Externe Kommunikation
Stammdatenimport
Vorgangsimport
können dann die Daten nachträglich bearbeitet werden.
Dort besteht dann auch die Möglich aus den erfassten Daten ein Referenz-ERP Beleg zu
erzeugen.
Einrichtung eines Kundenspezifisches Scanner
Moduls
Um ein spezifisches Scannermodul aufzurufen muss der
Steuerparameter 801
auf Private
Prozedur eingestellt werden. In dem Feld „IP-Adresse“ wird die IP-Adresse oder
die
Alibi
IP-Adresse
des Scanners hinterlegt. In dem Feld „private Prozedur“ muss dann Prozedur
„CallScannerModul“ eingetragen werden. Es kann aber auch eine private Prozedur
hinterlegt werden, die ein privates Modul aufruft.
Mit dem setzten des
Steuerparameters 885
kann eine private Prozedur
hinterlegt werden, die die Standard Sounds für die Fehler und Erfolgmelodie
überscheibt
Mit dem
Steuerparameter 880
kann ein eigens Style-Sheet für die
HTML Anzeige auf dem Scanner hinterlegt werden.
Lagernummer setzen
Bei der Ersteinrichtung eines Scannerbedieners muss
die Lagernummer in den
Vorgangskonstanten
Direktsprung
[VKONS]
gesetzt werden. Dies hat den Grund,
weil die Lagernummer aus den
Vorgangskonstanten
des
Bedieners
bestimmt, auf welchem Lager der Scanner
operiert. Anhand der Lagernummer und dem EAN Code oder der Artikelnummer werden
dann die erfassten Artikel gesucht. Dies gilt auch, wenn im Referenz-ERP System nur
das Lager 0 vorhanden ist.
Nach dem das Lager gesetzt worden ist, kann dieses
mittels Scancode auf dem Scanner gewechselt werden.
Aufbau des Scancodes im EAN 128 verschlüsselt
1.
LG 1 wobei zwischen dem LG und der 1 ein Leerzeichen ist.
2.
VKONS 1 wobei zwischen dem LG und der 1 ein Leerzeichen ist.
Die beiden Befehle können auch manuell per Tastatur
eingegeben werden. Beide Befehle ändern die aktuelle Lagernummer auf die
Lagernummer 1 ab.

---

## Anbindung eines Fremd SDK von einem dritt Hersteller

Anbindung eines Fremd SDK von einem dritt Hersteller
Es wurde die Möglichkeit geschaffen, einen anderen
Scannerhersteller mit der Software Referenz-ERP.CE zu verbinden. Das SDK des
Herstellers kann über eine Interface DLL angebunden werden.
Hierbei muss nur beachtet werden, dass für das
Betriebssystem Windows CE die Version Referenz-ERP.CE benutzt wird und für die Windows
Mobile Version die Software Referenz-ERP.WM.
Erstellen einer DLL zur Anbindung eines Scanners
Voraussetzungen
1.
Visual Studio 2008 oder 2005
2.
Windows CE SDK oder Windows Mobile SDK
3.
Compact Framework
4.
SDK des Geräteherstellers
Das Beispiel wurde mit dem SDK von Datalogic
erstellt
.
Als erste muss ein neues Projekt angelegt
werden
.
Dazu wird wie folgt vorgegangen
:
1.
Öffnen des Visual Studios
2.
Über Datei->Neu->Projekt ein neues Projekt anlegen.
3.
Als Projekttyp wird „Visual C#“ unter dem Punkt „Andere Sprachen“ ausgewählt.
Unter diesem Punkt gibt es den Punkt „Intelligentes Gerät“. Als Vorlage wird
„Projekt für Intelligente Geräte“ gewählt. Als Framework wird das .Net Framework
2.0 angegeben.
4.
Als nächstes öffnet sich das Fenster für die Zielplattform. Hier wird jetzt je
nach Abhängigkeit der Plattform des Scanners ausgewählt. Bei Windows CE ist die
Plattform „Windows CE“ und bei Windows Mobile ist die „Plattform Windows Mobile
6 Professional SDK“. Die .Net Compact Framework-Version auf Version 2.0
zustellen. Als Vorlage ist die Klassenbibliothek zu wählen.
5.
Jetzt wird das Projekt geöffnet.
Einfügen von Verweisen
.
Als nächstes müssen wir Verweise zu dem Projekt
hinzufügen. Als erstes muss die IScannerHardware in den Projektpfad kopiert
werden, da diese in das Projekt mit eingebunden wird.
Vorgangsweise
:
1.
Aufrufen des Projektmappen-Explorer
2.
Rechte Maustaste auf „Verweise“ und „Verweis hinzufügen“ auswählen
2.1. Jetzt kann
auf der Registerkarte „Durchsuchen“ nach der IScannerHardware gesucht
werden. Mit OK wird der Verweis hinzugefügt
2.2. Die DL
[...]


---

## Variante Filialsystem-Optionen

Variante
Filialsystem-Optionen
Felder
Betriebsstätte
Nummer der
      Betriebsstätte
Bezeichnung
Bezeichnung der
      Betriebsstätte
Transaktionslog löschen
Stellt den Wert der Datenbank-Option
      „
delete_old_logs
“ dar
Größe Transaktionslog
Zeigt an, wie groß die
      Transaktionslog-Datei maximal werden kann
Größe Auslagerungslog
Zeigt an, wie groß die
      Auslagerungslog-Datei maximal werden kann
Prozedur Fehlerprotokoll
Stellt den Wert der Datenbank-Option
      „
replication-error
“ dar
Ausführliches Log
Stellt den Steuerungsparameter des
      SQL Remote-Nachrichtenagenten
dbremote
zur Ausgabe von
      ausführlicher Protokollierung dar.
Funktionen
Pflege-Funktionen
Neu,
      Ändern, Ansehen, Löschen
Steuerung der
      Transaktions-Dateien
Datenbank extrahieren
Legt
      im Verzeichnis „
\Aeins\dbrexp
“ ein weiteres Verzeichnis für die
      ausgewählte Betriebsstätte an und legt dort die Extrakt-Datei der
      Datenbank ab. Weiterhin befindet sich dort die durch den Dienst
dbxtract
erstellte
Reload SQL Datei
mit entsprechender
      Betriebsstättenkennzeichnung.

---

## Sharepoint

Sharepoint
Hiermit besitzt man die Möglichkeit
Sharepoint-Adressen (genauer Onenote-Verweise) pro Kunde zu hinterlegen.
Ist noch keine solche Adresse hinterlegt so erfolgt
zunächst die Erfassung einer Adresse durch einen dafür vorgesehenen Dialog.
Die Adressen können im Onenote per
erfasst werden und per
Ctrl
+
V
in die Eingabemaske verbracht werden,
also zum Beispiel:
Die Eingabe muss per
bestätigt werden.
Hiernach wird ein „Klick“ auf
nun die entsprechende Adresse versuchen zu
öffnen.
Folgende Funktionen stehen extra bzw. alternativ zur
Verfügung:
Sharepoint
rücksetzen
: löscht die Adresse
Sharepoint
anzeigen
: wie Klick auf
Sharepoint
pflegen
: ruft den Eingabedialog zum Pflegen der Adresse auf
Sharepoint
debuggen
: um überhaupt eine Möglichkeit zu haben, die Adressen
EDV-technisch zu begutachten
Hinweis: Es können keine „normalen“ Internet-Adressen
mit dieser Technik zur Ansicht gebracht werden!

---

## Sperrbemerkungen

Sperrbemerkungen
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Sperrbemerkungen
Direktsprung
[SPB]
Sperrbemerkungen dienen der Beschreibung von Kunden,
bei denen die Fakturiersperre oder die Liefersperre gesetzt ist. Wenn eines
dieser Kennzeichen aktiv ist und die reguläre Vorgangserfassung behindert, kann
im Kundenstamm eine Bemerkung angegeben werden, warum der Kunde gesperrt ist.
Die Bemerkung wird dann zusätzlich zu der normalen Fehlermeldung angezeigt.

---

## Fehlerbehandlungsblock

Fehlerbehandlungsblock
Bei der Neuanlage von privaten Triggern und privaten
Prozeduren, wird automatisch ein Fehlerbehandlungsblock eingetragen. Dieser
sollte
nicht
entfernt werden, da ansonsten Totalabstürze der Prozedur
oder des Triggers an den Kunden weitergeben werden.
Lässt man den Behandlungsblock in der Prozedur /
Trigger, dann sollte beim Testen beachtet werden, dass jeglicher Fehler ins
Fehlerprotokoll eingetragen wird.
Standardmäßig werden keine Parameter mit ins
Fehlerprotokoll geschrieben. Man sollte diese hinzufügen, damit man bei Fehlern
anhand der übergebenen Parameter das Problem erneut provozieren kann.
Beispiel für zusätzlichen Parameter:
|| amic_func_sprachtexte (
'a'
,
'b'
,
'Parameter (%s): %s'
, -1,
'Param1'
, Param1)
|| '\n'
Ein fertiger Block würde dann wie folgt aussehen
EXCEPTION
when
others
then
Select
ERRORMSG
(),
SQLCODE
,
SQLSTATE
into
dc_ErrorMsg
,
dc_SQLCODE
,
dc_SQLSTATE
;
call
AMIC_FEHLERPROT
(
20
,
amic_func_sprachtexte
(
'a'
,
'b'
,
'Prozedur'
,
-
1
)
,
amic_func_sprachtexte
(
'a'
,
'b'
,
'Beim Ausführen der Prozedur "%s" ist ein Fehler
aufgetreten.'
,
-
1
,
'p_TestProzedur'
)
||
'\n\n'
||
amic_func_sprachtexte
(
'a'
,
'b'
,
'Parameter (%s): %s'
,
-
1
,
'in_Param1'
, in_Param1
)
||
'\n'
||
amic_func_sprachtexte
(
'a'
,
'b'
,
'Parameter (%s):
%s'
,
-
1
,
'in_ Param2'
, in_Param2
)
||
'\n'
||
amic_func_sprachtexte
(
'a'
,
'b'
,
'Parameter (%s): %s'
,
-
1
,
'in_ Param3'
, in_Param3
)
||
'\n'
||
'SQLCODE: '
||
dc_SQLCODE
||
' ['
||
dc_SQLSTATE
||
']'
||
'\n'
||
dc_ErrorMsg
,-
10171
);
End;

---

## Stammdatenexport (Kunden)

Stammdatenexport (Kunden)
Hauptmenü
Externe Kommunikation
Stammdatenimport
Stammdatenexport
Variante „Ansicht für
Stammdatenexport (Kunden)“
In dieser Variante sieht man Felder die über die View
AMIC_StammImportExportKunden zusammengetragen werden.
Mit Hilfe der Funktion
Export Kunden
F9
können die Kundenstammdaten exportiert
werden. Nach Bestätigung einer Abfrage, ob man den Export der ausgewählten
Kunden durchführen möchte, erscheint ein Fenster, in dem der Pfad und die
Ausgabedatei angegeben werden können.
Der Standardvorschlag für den Pfad ist
das Export-Verzeichnis von Referenz-ERP und der Dateiname wird mit AMIC_KUTMP.DBF
vorbelegt.

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

## Steuerbescheinigung/Zweitsteuerbescheinigung

Steuerbescheinigung/Zweitsteuerbescheinigung
Aus der Liste „Aktionärsdividende“ können für
abgeschlossene Wirtschaftsjahre Steuerbescheinigungen für die Aktionäre erstellt
werden. Ähnlich wie bei der Kundenbescheinigung können nach Anwahl der Funktion
über
F2
die Aktionäre und die
Dividende, für die die Steuerbescheinigung ausgestellt werden soll, ausgewählt
werden.
Die Zweitsteuerbescheinigung unterscheidet sich von
der Steuerbescheinigung nur durch Kennzeichnung, dass es sich hierbei um eine
Zweitsteuerbescheinigung handelt.

---

## Stapelkorrektur im Kundenstamm

Stapelkorrektur im Kundenstamm
In Absprache mit dem Kundenbetreuer besteht die
Möglichkeit, Parameter des Kundenstamms im Stapelbetrieb zu ändern.

---

## Steuerung der Transaktions-Dateien

Steuerung der
Transaktions-Dateien
Felder
Betriebsstätte
Im
      Neu-Fall F3-Auswahl der eingerichteten Betriebsstätten aus dem
      Filialstamm. Die Auswahl zeigt alle Betriebsstätten an, die noch nicht
      konfiguriert wurden.
Zentrale
Zeigt an ob es sich bei der Auswahl
      der Betriebstätte um eine Zentrale handelt
Wann
      oder wie sollen Transaktionslog-Dateien gelöscht werden?
Stellt den Wert der Datenbank-Option
      „
delete_old_logs
“ dar.
Mögliche Einstellungen:
-
Off
( Standard )
-
On
-
Delay
-
Sieben
      Tage
-
Dreißig
      Tage
Maximale Dateigröße der
      Transaktionslog-Datei?
Hier
      kann die maximale Größe der Transaktionslog-Datei angegeben werden. Im
      ersten Eingabefeld wird die Zahl eingetragen. Unter „in“ kann die
      Speichermengeneinheit angegeben werden.
-
Byte
-
kB
( kilo Byte)
-
MB
( MegaByte )
-
GB
( GigaByte )
Die Angebe entspricht dem Wert des
      Steuerungsparameters „
-x
“ für den SQL Remote-Nachrichtenagenten
dbremote.
Maximale Dateigröße der
      Auslagerungslog-Datei?
Hier
      kann die maximale Größe der Auslagerungslog-Datei angegeben werden. Im
      ersten Eingabefeld wird die Zahl eingetragen. Unter „in“ kann die
      Speichermengeneinheit angegeben werden.
-
Byte
-
kB
( kilo Byte)
-
MB
( MegaByte )
-
GB
( GigaByte )
Die
      Angebe entspricht dem Wert des Steuerungsparameters „
-os
“ für den
      SQL Remote-Nachrichtenagenten
dbremote.
Name
      der Prozedur für Fehlerbehandlungen?
Stellt den Wert der Datenbank-Option
      „
replication-error
“ dar. Bleibt das Feld leer ( Standard ), so
      werden Replikationsfehler nicht behandelt.
Ausführliche Ausgabe im
      Log?
Auswahl Ja / Nein
Legt
      dabei fest, ob der SQL Remote-Nachrichtenagent
dbremote
eine
      ausführliche Protokollierung ausführen soll ( entspricht dem
      Steuerungsparameter „
-v
“ )
Funktionen
Speichern F9
Speichert die Eingaben in der
      Tabelle Filialsystemoptionen.
Optionen setzen
Wird
[...]


---

## Kundenstammdaten

Kundenstammdaten

---

## Stoffstrom Kundenreport

Stoffstrom Kundenreport
Mit dem Stoffstrom-Kundenreport können die
aufgelaufenen Stoffstromdaten pro Kunde im ausgewählten Zeitraum dargestellt
werden. Der zu berücksichtigende Zeitraum wird entweder durch Angabe von
Anfangs- und Endperiode oder durch Eingrenzung des Lieferdatums festgelegt.
Zusätzlich kann eine Auswahl nach Warengruppen, Oberwarengruppen oder
Hauptwarengruppen erfolgen. Auch die zu berücksichtigenden Belegklassen
(Vorgangsklassen) können ausgewählt werden. Um eine vollständige Übersicht aller
Stoffstrom-Zu- und -Abgänge zu erhalten, müssen hier die Belegklassen für
Lieferscheine und Rechnungen (600,1600,700,1700) eingetragen werden, da
weiterverarbeitete (fakturierte) Lieferscheine nicht im Report verarbeitet
werden. Die zugehörigen Stoffstromdaten werden dann aus den Rechnungspositionen
gewonnen. Es werden im Report grundsätzlich keine stornierten Belege und keine
Stornobelege berücksichtigt.
Die Darstellung der Einzelzeilen
(Belegpositionen) im Report kann unterdrückt werden.
Der Report enthält pro Kunde
•
die Anschrift des Kunden
•
die einzelnen Einkaufspositionen mit
Lieferdatum, Lieferscheinnummer,
Rechnungsnummer, Artikelbezeichnung,
die Menge der Position und für jede
Stoffstromart des Artikels die Stoffstrommenge
sowie den Stoffstromanteil
•
eine Zusammenfassung nach Ware und Stoffart im Einkauf
•
die einzelnen Verkaufspositionen mit
Lieferdatum, Lieferscheinnummer,
Rechnungsnummer, Artikelbezeichnung,
die Menge der Position und für jede
Stoffstromart des Artikels die Stoffstrommenge
sowie den Stoffstromanteil
•
eine Zusammenfassung nach Ware und Stoffart im Verkauf
•
eine Zusammenfassung nach Stoffart mit jeweils
Gesamtstoffstrommenge
im Einkauf, im Verkauf und der saldierten Stoffstrommenge
Im Archiv der einzelnen Kunden wird der jeweils den
Kunden betreffende Teilreport archiviert.
Bei aktivierter Funktion ‚Anzeige des Firmenlogos‘ in
den Crystal Report Optionen wird das im Mandantenstamm hinterlegte Firmenlogo im
Re
[...]


---

## System-Informationen

System-Informationen
Im Betrieb mit Referenz-ERP werden vielfältige
System-Funktionen und System-Gegebenheiten verwendet. Die Varianten dieser
Anwendung dienen dazu diese Fälle an- und aufzuzeigen.

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

## Umsatzsteuer-ID Prüfung

Umsatzsteuer-ID Prüfung
Die Umsatzsteuer-ID (international auch VAT genannt
ist für den Geschäftsverkehr mit Kunden und Lieferanten wichtig zu erfassen.
Insbesondere beim Handel mit ausländischen Kunden stellt sich die Frage der
Überprüfung der ID auf Gültigkeit und Plausibilität.
Dazu bietet das
Bundeszentralamt für Steuern
einen Internetdienst
an. Sowohl mit Hilfe einer Internetseite als auch mit einer Datenschnittstelle
für Software kann dort die Existenz und korrekte Zuordnung zu einer Firma
erfragt werden. Parallel wird auch ein telefonischer Dienst angeboten. Alle
diese Dienste nutzen die gleiche Datenbasis und haben die gleiche Verfügbarkeit.
So sind in der Regel beim Ausfall der Datenschnittstelle auch die Internetseite
und das Info-Telefon nicht zur Prüfung in der Lage.
Bei der Prüfung wird zunächst die Umsatzsteuer-ID auf
ihre Plausibilität (Aufbau, Prüfsumme etc.) geprüft und ob diese überhaupt
vergeben wurde. In einem zweiten Schritt werden dann die beim Handelsregister
des EU-Mitgliedsstaates hinterlegten Daten mit den in Referenz-ERP hinterlegten
Anschriftenangaben und dem hinterlegten Firmennamen verglichen.
Dabei werden folgende Angaben verglichen:
•
Name und Namenszusatz
•
Straße
•
Postleitzahl
•
Ort
Der
Steuerparameter (
SPA 1011
–
UstID Prüfung Datenprozedur
) ermöglicht die Privatisierung der Adressaufbereitung.
Als Standardprozedur dient (AMIC_UStIDPruefAdressen
).
Somit ist durch die Verkettung weiterer Spalten eine
Individualisierung der Adressprüfung realisierbar.
Dieser Vergleich lässt folgende Ergebnisse zu:
Die Daten stimmen überein (A)
Die Daten stimmen nicht überein (B)
Die Daten wurden in Referenz-ERP nicht hinterlegt (C)
Die Daten wurden im Register des EU-Mitgliedsstaats
hinterlegt (D)
Bitte beachten Sie, dass im Fall einer
Nicht-Übereinstimmung oftmals abweichende Schreibweisen hinterlegt sind bzw.
Gesellschaftsformen wie z.B. GmbH, AG, A/S(Aktieselskab = Aktiengesellschaft -
DK) oder e.U. (eingetragenes Unternehmen - AT) in
[...]


---

## UmsatzsteuerId-Prüfung

UmsatzsteuerId-Prüfung
[KU]
Auswahl eines Kunden
UStId prüfen
Diese Funktion prüft mit Hilfe eines Internetdienstes
die Gültigkeit einer Umsatzsteuer-ID.
Hinweise:
•
Diese Funktion ist abhängig von einem externen Internetdienst des
Bundeszentralsamts für Steuern. Dieser ist kostenlos und liegt außerhalb der
Verantwortung von Branchen-ERP. Auf der Webseite
https://evatr.bff-online.de/eVatR/
erfahren Sie mehr über die Verfügbarkeit, über aktuelle Ausfälle und die
Funktion des Webdienstes.
•
Für die Nutzung dieses Dienstes muss der ausführende Rechner über eine
Internetverbindung verfügen.
•
Diese Funktion ist nur für Mandanten mit deutscher Umsatzsteuer-ID im
Mandantenstamm nutzbar.
•
Es können ausschließlich ausländische Umsatzsteuer-ID´s geprüft werden.
Diese Einschränkung ist durch den verwendeten Dienst vorgegeben.

---

## Übersicht über Prüfungen des Webservices:

Übersicht über Prüfungen des Webservices:
Mit dem Direktsprung [USTID] erreicht man die Historie
der Umsatzsteuer-Id-Prüfungen.
Hier kann nach Umsatzsteuer-Id, Vorgang oder Kunde
gefiltert werden.
Aufruf aus anderen Auswahllisten
Ein Aufruf des Direktsprungs aus der
Kundenauswahlliste belegt die Auswahl mit dem markierten Kunden vor.
Ein Aufruf des Direktsprungs aus einer
Vorgangsauswahlliste belegt die Auswahl mit dem markierten Vorgang vor.
Informationen
Die Auswahlliste enthält die folgenden Informationen:
Feld
Beschreibung
Prüfung
Diese Spalte gibt an, ob die Prüfung
      aus einem Kundeneintrag oder aus einem Vorgang heraus initiiert wurde.
UstId
Umsatzsteuer-Id, die geprüft werden
      sollte
Kunde
Kundennummer des zu prüfenden
      Kunden
Vorgang
Vorgangsnummer, wenn
      Vorgangsanfrage
Zeitstempel
Zeitstempel der letzten Änderung des
      Eintrags
Status
•
Neu – ein noch
      nicht verarbeiteter Auftrag
•
Erledigt – ein
      bearbeiteter Auftrag
Name
Prüfergebnis zum Namen
      *)
Straße
Prüfergebnis zur Straße
      *)
PLZ
Prüfergebnis zur Postleitzahl
      *)
Ort
Prüfergebnis zum Ort *)
Code
Ergebniscode des Webservices
Mehr
      dazu auf der Webseite
https://evatr.bff-online.de/eVatR/xmlrpc/codes
Info
Eine
      Zusatzinfo, die ggf. angibt, ob der Kunden oder der Vorgang (noch) nicht
      existieren – dies sollte i.d.R. leer sein
Prüfauftrag
Eine
      Prüfauftrags-Guid kann optional angezeigt werden. Diese dient dem Support
      zur Identifikation des Eintrags in der Datenbank bei einer
      Datenrecherche.
*)
Nicht immer ist das Ergebnis für Name, Straße, PLZ oder Ort eindeutig Okay oder
falsch.
Der Webservice stellt hier
vier Antwortmöglichkeiten bereit:
§
A = stimmt überein
§
B = stimmt nicht überein
§
C = nicht angefragt
§
D = vom EU-Mitgliedsstaat nicht mitgeteilt

---

## Vererbung F4

Vererbung F4
Unten rechts in der Option Box der Anschriftenmaske
gibt es den Punkt
Vererbung
F4
, über den man festlegen kann, welche
Felder beim Ändern einer Hauptanschrift auch bei den jeweiligen Ansprechpartnern
geändert werden sollen.
Die Vererbung erfolgt nur, wenn man das Feld Vererben
für die Kunden-Hauptanschrift auf der Maske auf Ja setzt (Vorbelegung bei einem
neuen Interessenten ist Ja).
Hat man festgelegt, welche Felder vererbt werden
sollen, sind diese bei den zur Hauptanschrift gehörigen Ansprechpartnern nicht
mehr editierbar.

---

## Versandanschrift

Versandanschrift
Erfassung der
Versandanschrift
aus dem Kundenstamm
heraus.

---

## Vertreterinformationen „außerhalb“ des eigentlichen Vertreterstammes

Vertreterinformationen „außerhalb“ des eigentlichen Vertreterstammes
Man kann jeden Vorgang einer Vertretergruppe zuordnen.
Dieses geschieht im Vorgangskopf, d.h. man kann explizit die Vertretergruppe zu
Beginn des Vorgangs erfassen. Als Standardvorbelegung werden die Einträge aus
dem Kundenstamm für Vertretergruppe bzw. aus dem Objektstamm gezogen. Diese
Information wird dann auch sowohl im Vorgang als auch in den einzelnen
Warenbewegungen behalten.
Jedem Artikel kann in weiteren Kennzeichen eine
Provisionsgruppe zugeordnet werden, die automatisch bei der Erfassung der
Warenposition ermittelt und in der Warenbewegung abgelegt wird.

---

## Tabellen des Vorgangsimports

Tabellen des Vorgangsimports
Folgende Relationen müssen für das Importieren von
Vorgängen befüllt werden.
Pflicht Relationen
ImportVorgStamm
In
      dieser Relation müssen alle Daten eingefügt welche für den Vorgangskopf
      benötigt werden.
z.B.
      Kundennummer, Vorgangsklasse, Vorgangsunterklasse
ImportVorgPosition
In
      dieser Relation müssen alle Daten gespeichert die auf Positionsebene
      benötigt werden.
z.B.
      Artikelnummer, Menge, Mengeinheit
Optionale Relationen
ImportVorgTextPosition
In
      dieser Relation können Texte zu einer Position gespeichert
      werden.
Mit
      dem Feld Textposition kann bestimmt werden, wenn es sich um eine
      Textposition handelt, ob der Text vor oder nach einer Position angezeigt
      werden soll.
•
0 Vor der
      Position
•
1 Nach der
      Position
0
      ist der Defaultwert
Die
      Reihenfolge bestimmt der Zeilenzähler.
Folgende Texttypen können gesetzt
      werden
•
0
      Positionstext
0
      ist der Defaultwert des Feldes.
Die
      Textlänge ist auf 255 Zeichen Begrenzt.
ImportVorgPositionAddon
Veraltet !!! Bitte
ImportVorgPosiAddOn
verwenden!
In
      dieser Relation können Daten für die Addonfelder gespeichert
      werden.
ImportVorgPosiAddOn
In
      dieser Relation werden Daten gespeichert, die später in der Tabelle
      WarenbewegungAddon zur Position hinterlegt werden sollen.
Der
      Name des gegebenen AddOn-Feldes muss mit dem Feldnamen in der Tabelle
      übereinstimmen, da sonst keine Daten gespeichert werden können.
ImportVorgPositionPartie
In
      dieser Relation werden Informationen der Partie(n) einer Position
      abgelegt. Eine Partie, die hier eingetragen ist, jedoch im System noch
      nicht existiert, wird angelegt werden.
ImportVorgStammZusatzTexte
In
      dieser Relation können Zusatztexte zum Vorgang gespeichert werden. Diese
      lassen sich dann später mit SQLK auf bestimmten Dokumenten andrucken.
      Diese Texte sind nicht
[...]


---

## Waagenterminal Übersicht

Waagenterminal Übersicht
Folgende Meilensteine sind verwirklicht:
•
COM-Port-IO-Routinen
•
Anbindung von Systemen über UDP-Protokoll
•
Anbindung von Systemen über Hersteller-DLL’s
•
Ein Waagenterminal beschreibt alle zum Betrieb notwendigen technischen
Daten zum Betrieb an einem Aeins-Host.
•
Branchen-ERP bekannte Waagenprofile werden mit Aeins ausgeliefert. Durch einen
Kopiervorgang können diese Schablonen angepasst und aktiviert werden
Die Waagenterminals werden über die Anwendung
„Waagenterminal“ per Direktsprung „WAM“ administriert.

---

## Suchfunktionalität der Bereichsauswahl

Suchfunktionalität der Bereichsauswahl
Bei der Suche innerhalb von Texten – wie z.B.
Kundennamen oder Ort – kann häufig auch mit Platzhaltern gearbeitet werden. Die
Syntax hält sich hier an die SQL-Norm.
Die „%“ – Funktion
Häufig wiederkehrende Fragen sind z.B. „Ich hätte
gerne alle Kunden, die mit „M“ beginnen“. Die Antwort erhält man, indem in einer
der Suchvarianten nach „Nachname“  folgendes eingegeben wird:
Auswahl
Ergebnis
M%
„Ich
      hätte gerne alle Kunden, die mit „M“ beginnen“
%,kiel
Alle
      Kunden aus „Kiel“
m%,k%
Alle
      Kunden mit „M“ aus „K“
me%,ka%
Alle
      „Me“ aus „Ka“
%ma,fritz
Alle, die irgendwo im Namen die
      Zeichenfolge „ma“ aufweisen und mit Vornamen „Fritz“ heißen
Die „_“ Funktion (Unterstrich „Shift –„)
Diese Funktion dient als Platzhalter für
ein
Zeichen.
Auswahl
Ergebnis
_e
Alle
      Kunden mit „e“ an zweiter Stelle
m__er
Alle
      „Meier“, unabhängig ob sie mit „ei, ey, ay, ai“ etc. an zweiter und
      dritter Position geschrieben werden
Achtung:
Hier wird natürlich auch der Name
      „Mauer“ etc. ausgewiesen.
m[_]m__er
Um
      einen echten Unterstrich zu suchen, muss man diesen in eckige Klammern
      setzen. Dieses Beispiel alle Einträge, die mit „m“ beginnen, dann einen
      Unterstrich „_“ haben und danach alle „Meier“, unabhängig ob sie mit „ei,
      ey, ay, ai“ etc. an zweiter und dritter Position geschrieben werden. Also
      z.B.: m_Mayer.
Soll der Unterstrich _ gesucht werden und nicht als
Platzhalter dienen, so ist er in eckigen Klammern zu setzen: [_]
Kombination aus „%“ und „_“
Auswahl
Ergebnis
m__er,%baden
Alle
      mit „M“ an erster Stelle und „er“ an 4.-5. Aus
      „…...baden“
_b%er,%baden
Alle
      mit „b“ an zweiter Stelle und anschließend irgendwo „er“ aus
      „…..baden“

---

## Zahlungsbedingung

Zahlungsbedingung
Für die überwiegende Zahl der Anwendungen genügt die
Eintragung der Standardzahlungsbedingung in der Hauptmaske des Kundenstammes.
Wenn es jedoch erforderlich ist, die Zahlungsbedingung von den
Haupt-Warengruppen abhängig zu machen, so besteht hier dazu die
Eingabemöglichkeit.

---

## Zahlungsbedingungen

Zahlungsbedingungen
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Zahlungsbedingung
Direktsprung
[ZB]
In der Eingabemaske Zahlungsbedingungen bestehen
folgende Eingabemöglichkeiten.
Kopfdaten
Einstellung
Textdarstellung
Kopfdaten
Feldname
Beschreibung
Nummer
Nummer der Zahlungsbedingung, die
      bei der Vorgangserfassung eingegeben wird bzw. im Kundenstamm abgelegt
      ist.
Nummer Gutschrift
Nummer der Zahlungsbedingung, die
      bei der Vorgangserfassung im Falle einer Gut­schrift gezogen werden
      soll.
Maske Standard
Nummer der Aufbereitungsmaske für
      die Zahlungsbedingung.
Maske Gutschrift
Nummer der Aufbereitungsmaske für
      den Fall der Gutschrift.
Bezeichnung
Beschreibung der
      Zahlungsbedingung.
Einstellungen
Die Änderung des
Typs einer Zahlungsbedingung ist nicht unkritisch. Sofern diese
Zahlungsbedingung bereits verwendet wurde, können sich daraus falsche
Datumsangaben entwickeln.
Um dieses zu
verhindern, kann mit Hilfe des
Steuerparameters 951 -
Zahlungsbedingung - Typ ändern
die Änderung des
Typs von verwendeten Zahlungsbedingungen unterbunden werden bzw. es wird vor den
Folgen gewarnt.
Feldname
Beschreibung
Typ
Art
      und Weise, wie die Zahlungsbedingung fälligkeitsseitig berechnet wird.
      (Format „
Typ
“)
Bezug
Berechnung des Bezugsdatums der
      Zahlungsbedingung. (Format „
Bezug
“)
Valutabestimmung
(Format „
Valutabestimmung
“)
Zieltage / max.
Zahlungsziel, in Abhängigkeit vom
      vorher gewählten Zahlungstyp. Bei manuellen Än­de­rungen während
      der Vorgangserfassung kann der Maximalwert nicht über­schritten
      werden.
Skontotage / max.
Zieltage bei Skontoabzug.
Bei
      manuellen Änderungen während der Vorgangserfassung kann der Maximalwert
      nicht überschritten werden.
Wird
      das Skontodatum aus dem Fälligkeitsdatum berechnet, so werden diese Tage
      vom Fälligkeitsdatum rückwärts gerechnet und  die Max-Eingabe ist
      nicht möglich.
Skontosatz / max.
Skonto Satz bei
[...]


---

## Zeiterfassung

Zeiterfassung
Hauptmenü
Stammdatenpflege
Kunden-/Lieferanten
Zeiterfassung
oder Direktsprung
[KU]/
[LF]
Zeiterfassung
Vorbereitung:
Zunächst muss entschieden werden ob bei der
Zeiterfassung nur eine Zeitspanne angegeben werden soll oder man genaue
Uhrzeiten für Anfangs- und Endzeit angeben möchte. Die Einstellung findet sich
im Steuerparameter „Uhrzeitorientierte Zeiterfassung“ (
SPA_1049
).
Uhrzeiterfassung
Stundenerfassung
Erfassung:
In beiden Fällen lässt sich das Datum und der Typ
pflegen. Der Typ kann im Anwenderformat „AF_Zeiterfas“ individuell eingerichtet
werden. Nach Eingabe der Uhrzeiten bzw. der Zeitspanne kann die Zeiterfassung
gespeichert werden.
Bei der Uhrzeiterfassung sorgt eine größere Start- als
Endzeit dafür das die Zeit auf den angegebenen und den darauffolgenden Tag
aufgeteilt wird.
Anzeige:
In der Datentabelle werden alle Datensätze zum
ausgewählten Kunden/Lieferanten angezeigt, welche im ausgewählten
Anzeigezeitraum liegen. Die eingeblendete Gesamtzeit bezieht sich ebenfalls auf
diesen Zeitraum.
Löschen:
Mit einem Klick in das Datum-Feld der Datentabelle
kann ein Datensatz ausgewählt werden. Mit der Funktion „Zeile Löschen“ wird der
Datensatz gelöscht.
EPA:
Im
EPA
„
Bediener_Zeiterfassung
“ kann eine Funktion hinterlegt
werden, welche eine KundId sucht, falls diese nicht mitgegeben wird. So könnte
beispielsweise bei einem Direktsprung auf die Maske eine KundId in Abhängigkeit
des Users gezogen werden.

---

## Zahlungspflichtige Kunden

Zahlungspflichtige Kunden
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Zahlungspflichtige Kunden
oder Direktsprung
[KUZ]
Auf dem Konto des Zahlungspflichtigen werden die
Rechnungen in der Finanzbuchhaltung verbucht. Üblicherweise handelt es sich um
den Rechnungsempfänger, dann ist hier keine Eintragung erforderlich. Nur wenn
sich Rechnungsempfänger und Zahlungspflichtiger unterscheiden, erfolgt also eine
Eintragung. Dies trifft auch auf oben beschriebenen Fall der abweichenden
Rechnungsanschrift zu.
In obigem Beispiel wird also der Lieferschein an
„Testkunde“ geschickt, die Rechnung erhält „Mustermann“ und gezahlt wird von
„Mustermann“. Alle Statistiken der Warenwirtschaft verbleiben bei
„Testkunde“.

---

## Zuordnung JVARS – Kriterien

Zuordnung JVARS – Kriterien
JVAR-Name
Verschlagwortung/Kriterium
Wert
1
Belegklasse
1
2
Belegnummer
2
3
Belegreferenz
3
4
Kundennummer
4
5
Mandant
5
6
Belegtyptext
6
7
Mail
7

---

## Aeins Konto / Belegnummer

Aeins Konto / Belegnummer
Das im Aeins System dem Kunden zugeordnete Konto bzw.
die Belegnummer.

---

## Anlage Mitglied

Anlage Mitglied
Es gibt zwei Möglichkeiten einen Gesellschafter
einzurichten, die erste Möglichkeit ist innerhalb des Kundenstamms
[KU]
ist das entsprechende Personenkonto
auszuwählen und zu markieren. Bei aktivierter Lizenz steht jetzt die Funktion
Mitgliedsbearbeitung
CF11
zur Verfügung.
Die zweite Möglichkeit ist über den Direktsprung
[GESEL]
in der ersten Variante
„Mitglieder“ besteht die Möglichkeit mit
F8
einen neuen Gesellschafter
anzulegen.
Bei der Neuanlage eines Gesellschafters muss
entschieden werden ob der gewählte Kunde zu einem Oberkonto oder Unterkonto
werden soll.
Als nächstes kann entschieden werden ob die
Kundennummer als Mitgliedsnummer übernommen werden soll. Wenn die Kundennummer
nicht als Mitgliedsnummer benutzt werden soll, so kann in das Feld
Mitgliedsnummer eine alternative Nummer eingetragen werden. Diese Nummer kann
mit der Funktion  „
neue Nummer
vergeben
“
SF8
bis zu der
ersten Buchung noch verändert werden.
Die Neuanlage eines Oberkontos erfolgt nur wenn bei
der Anlage gleich gezeichnet wird.
Wird der Kunde zu einem Unterkonto so muss dem Kunden
ein Oberkonto zugewiesen werden. Alle Buchungen zu diesem Unterkonto erfolgen
auf dem Oberkonto.
Für die E-Bilanz kann jetzt am Gesellschafter die
Feststellungserklärungsnummer, die Steuernummer, das Finanzamt, das Bundesland
sowie die Rechtsform des Gesellschafters gespeichert werden.
Zur Unterscheidung von Gesellschaftern mit gleichem
Namen wird zusätzlich ein Geburtsdatum angegeben. Das Feld wird mit dem
01.01.1901 vorbelegt.
Erst bei vergebener Mitgliedsnummer und gezeichneten
Anteilen ist ein Personenkonto unter der Gesellschafterverwaltung - Direktsprung
[GESEL]
- sichtbar.
In das Feld Belegdatum wird das Eingangsdatum des
Antrages auf Mitgliedschaft eingetragen.
Mitgliedsanlage ohne Anteile
In der Variante „Mitglieder ohne Anteile“  werden
alle Mitglieder ohne Anteile angezeigt.
Dort gibt es eine Funktion
„Mitglieder ohne Anteile löschen“ F7
mit
der Datensätze aus d
[...]


---

## Ansprechpartner

Ansprechpartner
Alle Ansprechpartner werden in einem GRID Dargestellt
und ein Ansprechpartner kann per Doppelklick als zugehöriger Ansprechpartner
aktiviert werden.

---

## Arbeitsregeln im Vorgang

Arbeitsregeln im Vorgang
Um betriebsinterne Abläufe, die mit Vorgängen im
Referenz-ERP System zu tun haben, in einer Firma besser steuern zu können, ist ein
Regelsystem implementiert worden.
Regeln sind mehr oder minder komplexe Strukturen, die
Aktionen auslösen, Arbeitsabläufe steuern oder bestimmte Schritte verhindern
können.
Sollen z.B. Druckvorgänge „gestoppt“ werden, wenn
Kriterien nicht erfüllt sind, dann kann dieses mit einer Regel erreicht werden.
Des Weiteren können Umwandlungen blockiert werden, wenn bestimmte Elemente eines
Vorganges nicht den Firmenregeln entsprechen, wie z.B. Partiezuordnung in einem
Vorgang.
Das verbietet oder verhindert nicht das Erfassen von
Informationen, sondern verhindert das Weiterverarbeiten von Vorgängen/Belegen,
wenn bestimmte Elemente noch nicht abgeschlossen sind.
Eine Regel startet mit dem Anlegen eines Vorganges
(siehe dazu
Formularzuordnung
[FRZ]
), es können dann Folgeregeln festgelegt
werden, es können bestimmten Bedienern (Bedienerklassen) bestimmte Regeln
zugeordnet werden, und es können Ausnahmen für Folgeregeln definiert werden, um
den betrieblichen Ablauf Normgerecht (z.B. ISO9000) abzuwickeln und dem
Mitarbeiter keine Schlupflöcher zu erlauben.
Die Inhalte von Regelwerken werden über Makros,
Prozeduren, Skripte, SQL Befehle oder über einfache Zuordnungen gesteuert.
Innerhalb der Vorgangsbearbeitung kann dann bequem
nach diesen Regeln selektiert werden, um eine leichte Abarbeitung der
Prozessketten zu ermöglichen.

---

## Archiv-Ansicht Standard-Auslieferung: Kunden, Vorgang

Archiv-Ansicht
Standard-Auslieferung: Kunden, Vorgang
Die Standard-Auslieferungen sind so konstruiert, dass
sie auch noch auf sehr großen Archiv-Beständen akzeptable Zugriffszeiten
liefern.
Kundenauswahlliste: AMIC_KUNDE
Var
Herkunft
Wert
ZW1
AL
      Return
KundNummer
KUNDNUMMER
AL
      Return
KundNummer
Freies UND
Konstante
fa.fa_kundennummer =
      ':!jvars_5001_ZW1'
Kundendialog: AMIC_KUNDE_DLG
Var
Herkunft
Wert
ZW1
Maskenfeld
h.KundNummer$
REFERENZ
Maskenfeld
h.Fa_Belegreferenz$
KUNDNUMMER
Maskenfeld
h.KundNummer$
Freies UND
Konstante
fa.fa_kundennummer =
      ':!jvars_5001_ZW1'
Vorgangsauswahllisten: AMIC_VORGAWL
Var
Herkunft
Wert
ZW1
AL
      Return
v_id
REFERENZ
SQL
select fa_belegreferenz wert from
      vorgangstamm where v_id = :ZW1
KUNDNUMMER
SQL
select KUNDNUMMER wert from
      vorgangstamm where v_id = :ZW1
Freies UND
Konstante
fa.fa_belegreferenz
      <> '' and  fa.fa_belegreferenz in (select fa_belegreferenz from
      vorgangstamm where v_id=:!jvars_5001_ZW1
union
      select ktr.fa_belegreferenz from v_posikontrakt vpktr join kontraktstamm
      ktr on ktr.ktrid = vpktr.ktrid where
      vpktr.v_id=:!jvars_5001_ZW1
union
      select p.fa_belegreferenz from v_posipartie vpp join partiestamm p on
      p.partieid = vpp.partieid where vpp.v_id=:!jvars_5001_ZW1
)
Signifikante Geschwindigkeitsvorteile konnten mit
folgender Ableitung festgestellt werden:
<?xml version="1.0"
encoding="utf-8"?>
<Description Name="AMIC_LGU" RowHeight="22"
Version="8.1.1.256">
<Field Name="fa.fa_mime" Caption=" "
Mime="true" WidthDisplay="22" />
<Field Name="fa.fa_kundennummer"
Caption="Kundennummer" />
<Field Name="fa.fa_klasse"
Caption="Klassifizierung" Format="af_fa_klasse" Sql="isnull(fa.fa_klasse,0)"
/>
<Field Name="fa.fa_belegtyptext"
Caption="Belegtyp" />
<Field Name="fa.fa_belegnummer"
Caption="Belegnummer" />
<Field Name="fa.fa_belegdatum"
Caption="Belegdatum" />
<Field Name="fa.fa_druckdatum"
Caption="Archiv/Druckdatum" />
<Field
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

## Attribute der Auswahlliste

Attribute der Auswahlliste
Kontonr.
Konto- bzw. Kunden-/Lieferantennummer
Lieferant-/Kunde
Bezeichnung des
Lieferante/Kunden
Kontrakt
Nummer des Fremdkontrakts
Ktr.AbDat.
Beginn der Kontraktlaufzeit
ArtikelNr.
Artikelnummer der Kontraktposition
MeBuTyp
Mengenbuchungstyp des Kontrakts
(brutto/netto)
VorF.Menge
vorfakturierte Menge
(=Kontraktsollmenge)
VorF.Me
Mengeneinheit dazu
Lief.Br.Menge
Hier steht die Summe der Liefermengen
(brutto) aller zugehörigen Rohwarebelege.
Lief.Nt.Menge
Hier steht die Summe der
Abrechnungsmengen (netto) der Lieferpositionen aller zugehörigen
Rohwarebelege.
Geliefert
Diese Menge ist die Kontrakt-Ist-Menge
und beinhaltet außer den Mengen der zugehörigen Rohwarebelege auch diejenigen
der mit diesem Kontrakt erfassten (und nicht in Rohwarebelege gewandelten)
Nicht-Rohware-Belege.
Anz.Bel.
Anzahl der zugehörigen Rohware-Belege
RwGr.
Nummer der zugehörigen Rohwarengruppe
RwGr-Bezeichnung
Bezeichnung der zugehörigen
Rohwarengruppe

---

## Aufbau der Prozeduren

Aufbau
der Prozeduren
Abschnitt-Prozeduren
Die Prozeduren für einen Abschnitt sind als Bausatz zu
verstehen. Hier wird angegeben, welche Segmente in einer Nachricht erscheinen
sollen. Übergabeparameter sind immer die entsprechende Id (in_v_Id, in_wabewid
oder in_datei_id) und die Profil_Id (in_profil_id). Der Rückgabewert sind immer
vier Parameter:
Parameter 1 enthält den Namen des Segmentes. Hierbei
handelt es sich immer um drei Großbuchstaben.
Parameter 2 enthält die Variante des Segmentes. Diese
sind individuell gestaltbar, müssen aber dann in der entsprechenden Prozedur des
Segmentes hinterlegt werden.
Parameter 3 enthält einen Positionszähler. Dieser wird
nur in Verbindung mit den LIN-Segmenten auf Positionsebene gebraucht. Ansonsten
sollte konstant „0“ zurückgegeben werden.
Parameter 4 enthält eine Unterposition. Diese wird
benötigt, wenn auf Abschnittsebene eine Schleife genutzt wird, um der
Segmentprozedur darunter mitzuteilen, in welchem Durchlauf sie ist. Auch hier
sollte „0“ zurückgegeben werden, wenn keine Schleife vorhanden ist.
Segment-Prozeduren
Die Prozeduren für einen Abschnitt sind die
Ausgestaltung der einzelnen Zeilen in einer EDI-Nachricht. Die Eingangsparameter
sind:
Parameter
Bedingung
in_v_id
Falls Segment in Kopfteil,
      Kopfteil-Rabatt, Fußteil oder Fußteilsteuer genutzt wird.
in_wabewid
Falls Segment in Positionsteil,
      Positionsteil-Rabatt oder Gebinde/Display genutzt wird.
in_datei_id
Falls Segment in Rechnungsliste oder
      Rechnungsliste-Steuer genutzt wird.
in_linZahl
Nur
      im LIN-Segement benötigt. (Parameter 3 vom Abschnitt)
in_unterposition
Parameter 4 vom
      Abschnitt.
in_variante
Parameter 2 vom
      Abschnitt.
in_top
Kann
      genutzt werden, um bei einem „Select zum Testen der Prozedur“ per OSQL
      mehr Datensätze zu sehen. Sollte sonst immer 1 sein.
in_profil_id
Wird
      benötigt, um auf die View zuzugreifen und um die Testroutine auf dem
      Profil auszuführen.
Die Rückgabepar
[...]


---

## Aufruf aus der Auswahlliste

Aufruf aus der Auswahlliste
In der Auswahlliste muss entweder eine Adressid
vorhanden sein oder ersatzweise eine Kundis, deren Hauptadresse angezeigt wird.
Mit diesem JPL-Code
call CS
("GoogleMapsPoint")
wird der Browser mit den markierten Adressen
geöffnet
Im PAS-Makro wird der Controlstring aufgerufen
sprintf(buf,"^ CS
("GoogleMapsPoint")");
ctrlstring(buf);

---

## Aufruf aus Kunden [KU] oder Lieferanten [LI]

Aufruf aus Kunden [KU] oder Lieferanten [LI]
Der Einfachheit halber wird im Folgenden nur von
„Kunden“ gesprochen – die Ausführungen gelten analog, wenn mit der Anwendung
Lieferanten gestartet wird.
Nach Auswahl eines Kunden kann der Preisstapelpfleger
über das Kontextmenü, Menüpunkt „individuelle Preispflege“, oder mit der
Tastenkombination Umschalt F5 gestartet werden:
Wie bereits erwähnt, erfolgt die Datenbereitstellung
über die Ladeprozedur
HoleIndividuellePreiseKunde
. Die Ergebnismenge wird
entsprechend in einem Gitter dargestellt:
Gezeigt werden die Daten des zuvor ausgewählten Kunden
„10042“, wir kommen aus der Anwendung KU, also Verkauf „1“. Dieser Kundenseite
wurde die individuelle Preisklasse „123456791“ zugewiesen. Sichtbar sind ferner
die Verkaufsartikel, gefiltert nach den Attributen „Lager“ und „Warengruppe“.
Diesen Artikeln wurde die individuelle Preisgruppe „68704225“ zugewiesen. Am
Kreuzungspunkt dieser Dimensionen stehen die eigentlichen individuellen
Preisdaten, sortiert nach „gültig ab“, „gültig bis“ und der „ab Menge“. Die
Besonderheit des Preisstapelpflegers für die Kundensicht ist die Verwendung
diskreter Preispunkte
– in der aktuellen Ausbaustufe werden maximal drei
Stück unterstützt: im obigen Beispiel können Preise ab „01.10.2025“,
„01.11.2025“ und schließlich ab „01.12.2025“ gepflegt werden. Zu diesem Zweck
muss das gezeigte „gültig ab“ und „gültig bis“ Datum diese Preispunkte
umschließen.

---

## Aufruf innerhalb der Vorgangserfassung

Aufruf innerhalb der
Vorgangserfassung
Wird nach Eingabe der Kundennummer im Vorgangskopfteil
die STRG F7 Taste gedrückt, so erscheint die oben beschriebene zeilenorientierte
Artikelverarbeitungsmaske.
Es können auf diese Maske per Ladeprozedur die im
Bereich MSA gepflegten Artikellisten zur direktanzeige (Ordersatzartig)
angezeigt werden, eine individuelle Ladeprozedur (ggf. auch pro Kunde) ist auch
einrichtbar.
Nach Aufruf des Moduls steht der Cursor im Feld Menge,
die dann bei vorgelegtem Artikelstapel sofort eingegeben werden kann. Eine
Gebindeverarbeitung wird auch in diesem Bereich unterstützt.
Im Mengenfeld ist die Taste F4 mit der Artikelauswahl
verbunden, so dass hier direkt ein Artikel (oder alternativer Artikel)
ausgewählt werden kann.
Wird an dieser Stelle direkt im Mengenfeld ein
alphanumerischer Text eingegeben, so wird sofort eine Spezielle
Artikelauswahlmaske geöffnet, die auf den Matchcode im Artikelstamm
reagiert.
Nbb.: Dieser Bereich wird auch vom Kontrollmakro
unterstützt.

---

## Auslandskunden

Auslandskunden
Hauptmenü
Stammdaten
Konstanten Kundenstamm
Auslandskunden
Direktsprung
[KUA]
Bisher wurden EU-Standardüberweisungen über den
Auslandszahlungsverkehr geregelt. Dazu mussten die Kunden als Auslandskunden
gekennzeichnet werden, so dass alle OPs als Auslands-OPs erstellt wurden. Um nun
diese OPs über das SEPA-Verfahren abzuwickeln, muss man das Kennzeichen wieder
entfernen. Der Kunde muss also aus den Auslandskunden gelöscht werden und
bereits als Auslands-OPs gekennzeichnete Belege müssen zurückgesetzt werden.

---

## Bankenstamm

Bankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Bankenstamm
Direktsprung
[BNK]
.
Hierbei handelt es sich um die Grunddaten der Banken;
sie sind Grundlage der Kunden- und Hausbanken. Folgende Felder werden im
Bankenstamm geführt:
Beschreibung
Nummer
Vergabe einer - laufenden - Nummer
      für die Bank. Sie dient als verweis in anderen Tabellen auf diese
      Bank.
Swift / BIC
Hier
      werden der BIC (Bank Identifier Code) der Bank hinterlegt.
Bezeichnung
Bezeichnung der Bank, z.B. Postbank
      Hamburg
Matchcode
Kurzsuchbegriff nach freier Wahl,
      z.B. PB HH.
Staat
Kennzeichen für den Staat bei
      Auslandsbanken. Für Banken, bei denen nicht Deutschland als Staat
      eingetragen ist – der Staat Deutschland wird am ISO-Code DE erkannt -,
      wird die Bankleitzahl zwar auf Eindeutigkeit geprüft und eine Hinweis wird
      ausgegeben, aber sie werden trotzdem gespeichert. Bei Banken in
      Deutschland ist das Speichern dieser neuen Bank dann nicht möglich.
PLZ/ORT
Postleitzahl und Ort, an dem diese
      Bank ihren Sitz hat.
Bankleitzahl
Als
      Voraussetzung für die Automatisierung des bargeldlosen Zahlungsverkehrs
      sind die Spitzenverbände des Kreditgewerbes und die Deutsche Bundesbank
      mit Wirkung vom 1.Oktober 1970 überein gekommen, im Girogeschäft tätige
      Kreditinstitute im Bundesgebiet durch Bankleitzahlen zu kennzeichnen, die
      nach einem einheitlichen System aufgebaut sind. Die Bankleitzahl ist
      numerisch und umfasst acht Stellen.
In Referenz-ERP dient sie unter
      anderem als Suchkriterium und steht für Ausdrucke, Datenträgeraustausch
      etc. zur Verfügung. Aus der Bankleitzahl werden die Bankregion
      (Bankplatz/Ortsnummer) und die Bankgruppe (Netznummer)
      ermittelt.
Bankgruppe
Die
      Bankengruppe (Netznummer) soll dazu dienen, Banken zu kennzeichnen, die zu
      einem Verbund (z. B. die Volks- und Raiffeisenbanken) gehören, weil es oft
      der Valutierung zuträglich ist, Übe
[...]


---

## Barverkaufskunde im Kundenstamm

Barverkaufskunde im Kundenstamm
Im Kundenstamm müssen ein- oder mehrere Kunden für
Barverkauf, Bareinkauf und ggf. für die POS-Kassen angelegt werden, die später
in der
Kasseneinstellung
zugeordnet werden können.
Diese Kunden werden dann stets als Kunden bzw.
Lieferanten in diesen Barvorgängen vorbelegt.

---

## Baustelle/Silo

Baustelle/Silo
In der Baustelle
[BAU]
muss das für die App relevante Silo
ausgewählt und mit F5 die Bearbeitungsmaske geöffnet werden. Unter dem
Tab-Reiter „Anschrift“ muss nun erneut die VVVO-Nummer gepflegt werden.
Unter dem Tab-Reiter „Kundenliste“ müssen die Kunden
eingetragen werden.

---

## Beispiele für SQL-Texte

Beispiele für SQL-Texte
// ermittelt den Saldo des Kunden
// auf Basis gebuchter Saldo
select
sum(kontosumgebhaben)-sum(kontosumgebsoll) tuwas
from    kontosummen
where   kontonummer =
(select
kontonummer from kundenstamm where kundid =:KUNDID)
// lädt die Bemerkungszeile 1
//
SELECT BemerkPosition.BemerkText
FROM KundenStamm
INNER JOIN (BemerkStamm INNER JOIN BemerkPosition
ON BemerkStamm.BemerkId =
BemerkPosition.BemerkId)
ON KundenStamm.KundBemerk =
BemerkStamm.BemerkId
WHERE BemerkZeile=1
AND   Kundid=:KUNDID
// Privater SQL Text
SQLK_Text_Gu_Re     ---
SELECT (V_WertNetto + V_WertSteuer) AS
Bruttobetrag,
(IF Bruttobetrag
< 0 THEN 'RECHNUNG'
ELSE
'GUTSCHRIFT' ENDIF) AS Belegtext
FROM   Vorgangstamm
WHERE V_Id=:V_Id
// Privater SQL Text
sqlk_Saldo_erfasst     ---
select sum(kontosumerfsoll) - sum(kontosumerfhaben) as
saldo_erfasst,
from    kontosummen
where   kontonummer =
(select
kontonummer from kundenstamm where kundid = :KUNDID)
// effektiver Artikel Bestand
//
SELECT
( ArtiBestMenge + ArtiBestKorr ) as Bestand
FROM
Artikel
LEFT OUTER JOIN ArtiBestand
ON
Artikel.ArtikelID = ArtiBestand.ArtikelID
WHERE
Artikel.ArtikelID=:ARTIKELID

---

## Beispiel Informationsfeld

Beispiel
Informationsfeld
Hauptmenü
Administration
Werkzeuge
Informationssystem
Direktsprung
[AIS]
Im Bankenstamm (Direktsprung
[BNK]
) soll hinter
der Banknummer die Anzahl der Einträge in den Kundenbanken angezeigt werden.
Anlegen des Labels
Im Referenz-ERP Informationssystem legt man sich einen neuen
Eintrag (
F8
) an. Zuerst muss die Gruppe angegeben werden. Hat man bereits
ein oder mehrere Felder zu einer Gruppe erfasst, kann man diese hier mit
F3
auswählen. Die Felder „
Makro
“, „
Ändern Vorlauf
“ und
„
Einfügen Vorlauf
“ werden dann vorbelegt.
Register Feldbeschreibung:
Beschreibung
Feldname
Auch
      für Label, die nicht aus der Datenbank gefüllt werden, müssen Feldnamen
      vergeben werden. Sie sollten so gewählt werden, dass man schon am Namen
      die Bedeutung erkennen kann. In diesem Beispiel soll der Name des Labels
      „
lbl.verwendet
“ heißen. Das Kürzel „lbl“ gefolgt von einem Punkt
      soll zeigen, dass es sich um ein Feld vom Typ Label handelt.
Sortierung
Die
      Sortierung ist bei Labeln, die nicht aus der DB gefüllt werden, nicht
      wichtig und kann auf
0
stehen gelassen werden.
Feldtyp
Der
      Feldtyp für die Beschriftungsfelder muss natürlich
Label
sein.
Datenformat
Wenn
      der Label aus der Datenbank gefüllt wird, kann es nötig sein, ein anderes
      Format als „Character“ einzugeben. In unserem Beispiel reicht
CHARACTER
.
Zeile und Spalte
Die
      Position kann entweder über ein Raster oder pixelgenau angegeben werden.
      Sollen es Pixel sein, so ist ein kleines p an die Zahl anzuhängen (z.B.:
      125p). Um die Felder genau zu positionieren, so dass sie auf gleicher Höhe
      wie die Originalfelder sind, muss in diesem Beispiel das Verfahren mit
      Pixeln gewählt werden. Für die oben dargestellte Maske trägt man bei Zeile
9p
und bei Spalte
200p
ein.
Hinweis: Branchen-ERP kann nicht
      gewährleisten, dass die Positionen der Felder auf einer Maske nach einem
      Update noch gleichgeblieben sind. Es müs
[...]


---

## Beispielszenarien für Belegversand

Beispielszenarien für Belegversand
Szenario
Kunde
VRGD
Belegversand
Sie
      möchten keinen Belegversand für den Kunden
Kein
      Belegversand
Nein
Sie
      möchten eine Rechnung vorab per Mail versenden – der Postversand bleibt
      wie zuvor
•
Mit
      Rechnungsdruck
•
Mailadresse in
      der Hauptanschrift des Rechnungskunden des Beleges hinterlegen
•
Vorgangsdruckklasse
      definieren
Ja
Sie
      möchten eine Rechnung per Mail versenden, jedoch den Druck für den Versand
      nicht durchführen
•
Statt
      Rechnungsdruck
•
Mailadresse in
      der Hauptanschrift des Rechnungskunden des Beleges hinterlegen
•
Vorgangsdruckklasse
      definieren
Ja
Sie
      möchten eine Rechnung per Mail versenden, jedoch ein Formular mit
      Briefkopf-Grafik verwenden, weil dies sonst auf dem Druckpapier
      dargestellt wird
•
Statt
      Rechnungsdruck
•
Mailadresse in
      der Hauptanschrift des Rechnungskunden des Beleges hinterlegen
•
Vorgangsdruckklasse
      definieren
Eigenes Formular als Exklusiv
      kennzeichnen
Szenario
[FRZ]
Sie
      möchten Belege zunächst sammeln und später versenden
•
Richten Sie die
      Prozedur AMIC_Belegversand_Ware_Spaeter oder eine private Ableitung davon
      ein
•
Richten Sie ein
      Event zum Versand der Belege ein
Sichten Sie Belege zum Versand unter
      [MAIL]
Sie
      möchten Belege sofort beim Druck versenden
•
Richten Sie die
      Prozedur AMIC_Belegversand_Ware_Sofort oder eine private Ableitung davon
      ein

---

## Beispiel Vorgang neu anlegen

Beispiel Vorgang
neu anlegen
ZielKundenNummer, ZielKlassennummer etc. sind
Variablen die die zu speicherden Werte enthalten.
An diesem Beispiel kann man sehr schön die
Schachtelungstiefe erkennen
1.
JPP-Objekt erzeugen, füllen, beenden
2.
Vorgang starten, speichern und beenden
3.
neue Warenposition hinzufügen
4.
neue Partie hinzufügen
Nur wenn alle einzelnen Schritte ohne Fehler verlaufen
sind wird ein neuer Vorgang erzeugt.

---

## Beschreibung eines POS-Vorgangs

Beschreibung eines POS-Vorgangs
Innerhalb jedes
Vorgangs
stehen folgende Funktionen zur Verfügung, die allerdings nur zu
gewissen Zeitpunkten innerhalb des Vorgangs gelten und deshalb teilweise
„verschwinden“:
Kundennummer ändern (SF2), d.h. es ist zu Beginn eines
Vorgangs möglich, diesen Vorgang verschiedenen Kunden zuzuordnen. Standardmäßig
wird der Barverkaufskunde vorbelegt.
Belegwährung ändern (SF5), d.h. es ist möglich, zu
Beginn eines Vorgangs die Währung festzulegen, in der die Positionen erfasst
werden sollen. Diese ist standardmäßig mit der Währung des Kunden identisch.
Die Belegnummer wird automatisch aus dem
Barverkaufsnummernkreis vorbelegt und kann nicht manuell geändert werden.
Lagernummer ändern (SF3), d.h. es kann vor der
Erfassung eines Artikels festgelegt werden, aus welchem Lager er stammen soll,
dabei wird zu Beginn eines Vorgangs die Lagernummer gemäß Eintrag in den
Vorgangskonstanten (VKONS) genommen. Diese Vorbelegung gilt auch für den
nächsten Vorgang, wenn die Lagernummer während des letzten Vorgangs über SF3
geändert wurde, d.h. diese Lagernummeränderung ist nur temporär, eine ständige
Änderung sollte über die Vorgangskonstanten eingetragen werden.
Preis manuell ändern (SF9), siehe 2b).
Die Menge ist standardmäßig mit 1 vorbelegt, sie muss
nur verändert werden, wenn größere Einheiten eines Artikels verkauft werden (um
in dieses Feld zu kommen, muss vor der Erfassung des Artikels die Richtungstaste
nach oben betätigt werden). Auch Gebinde werden standardmäßig mit 1 gemäß
Einheit der Grundmengeneinheit vorbelegt.
Um den letzten erfassten Artikel noch mal zu erfassen,
muss nur durch Return der sich noch im Artikeleingabefenster befindliche Artikel
bestätigt werden (wenn der EPA zur Bestätigung des Preises eingeschaltet ist,
ist auch noch der Preis durch Return zu bestätigen).
Mit CF11 kann man dem System mitteilen, dass der
nächste Artikel als Wertartikel erfasst werden soll, d.h. der Artikel, der als
nächstes erfasst w
[...]


---

## Bestell-Ordersatz

Bestell-Ordersatz
In Ordersätzen werden für einen Lieferanten
Artikellisten mit Preisen zusammengestellt, auf die bei der eigentlichen
Vorgangserfassung, z.B. beim Bestellen, unterstützend zurückgegriffen werden
soll (Funktion „Ordersatz“ bei der Vorgangserfassung). Ordersätze werden
verwaltet und anderen Vorgangsklassen bereitgestellt; Bestandsbuchungen nach
Menge und Wert erfolgen nicht.
•
Ordersatz erfassen F
8
Erfassung eines neuen Ordersatzes
•
Stapelverarbeitung
Übernahme eines oder mehrerer Ordersätze in einen Bearbeitungsstapel
•
Erstdruck
F9
Erstdruck eines Ordersatzes
•
Formulardruck
F10
Wiederholungsdruck
•
Korrektur
F5
Korrektur eines Ordersatzes
•
Kopieren
CF8
Kopieren des Ordersatzes für einen auszuwählenden Kunden
•
Vorschau
F11
Druckvorschau

---

## Bestellvorschlagsliste

Bestellvorschlagsliste
Die Bestellvorschlagsliste wird erreicht über den
Direktsprung [BAB], dort die Variante ‚Bestellvorschläge’ wählen.
Alle Artikel die mindestens einen Lieferanten hinterlegt
haben, wo der verfügbare Bestand kleiner dem Meldebestand ist und die weder eine
Bestellsperre im ARTIKEL noch im Kunden/Lieferantenstamm haben, werden hier
angezeigt.
Die Bestellmenge wird auf Basis der Bestellgröße und der
Differenzmenge zwischen verfügbaren Bestand und Soll-Bestand, lagerbezogen
ermittelt.
Diese Auswahlliste kann nach verschiedenen Kriterien
gefiltert werden.
So ist es zum Beispiel möglich diese Bestellvorschläge
auf einen Lieferanten einzugrenzen um gezielt für diesen Lieferanten zu
bestellen.
Die Einstellung –Best.Anfragen berücksichtigen- sorgt
dafür, dass die Mengen aus offene Bestellanfragen in den verfügbaren Bestand mit
eingerechnet werden, da diese Bestellungen in Vorbereitung sind.
Sind für einen Artikel gleich mehrere Lieferanten in
der Auswahllist, so wird die Bestellanfrage für den erstgefundenen Lieferanten
erstellt. Die Kennzeichnung eines Hauptlieferanten ist nicht vorgesehen!
Mit der Funktion „
Anfrage in den Vorgangsimport
“
[Shift +F9
] werden die Ausgewählten
Datensätze in den
VorgangsImport
übernommen. Dort
können dann die Daten noch verändert werden, bevor diese in eine Bestellung
gewandelt werden.
Es besteht bei der Übernahme noch die Möglichkeit die
Artikel nach Lager und Lieferant zu splitten. Dazu muss der Steuerparameter 928
mit der Option „BESTELLVORSCHLAEGELAGERTRENNUNG“ auf 1 gestellt werden.
Im Standard wird nur nach Lieferant gesplittet

---

## Verbotslisten-Übersicht

Verbotslisten-Übersicht
Hauptmenü
Externe Kommunikation
Webservice
Verbotsliste
Diese Auswahlliste dient zur Anzeige der Prüfaufträge,
die aus Anschriften, Kunden und Vorgängen entstehen können.
Felder
Felder
Beschreibung
Prüfung
-
Vorgang:
Die Prüfung ist aus einem
      Vorgang initiiert worden.
-
Kunde:
Die Prüfung ist aus einem Kunden
      initiiert worden
-
Anschrift
Die Prüfung ist aus der
      Anschrift initiiert worden
Kunde
Kundennummer
Vorgang
Vorgangsnummer (wenn vorhanden)
Zeitstempel
Zeitstempel
      des Eintrags
Status
E
rgebnis der Prüfung
-
ungeprüft:
Die Prüfung ist noch nicht
      erfolgt
-
zulässig
Die Prüfung ist erfolgt und die
      Anschrift ist als zulässig gewertet worden
-
unzulässig
Die Prüfung ist erfolgt und die
      Anschrift ist als unzulässig gewertet worden
Quelle
A
nschrift aus
      dem Vorgang
-
Kunde:
Kundenanschrift
-
Rechnung
Rechnungsanschrift aus dem
      Vorgang
-
Zahlungspflichtiger
Zahlungspflichtiger aus dem
      Vorgang
-
Versandanschrift
Versandanschrift aus dem Vorgang
-
Andere
Weitere
      Anschriften aus einer
Datenbankprozedur
, die Anschriften aus dem
      Vorgang bzw. in dessen Umfeld hinzuliest.
AdressId
AdressId der Anschrift
Name
Name
Straße
Straße
PLZ
Postleitzahl
Ort
Ort
Prüfauftrag
GUID
      des Prüfauftrags für Datenbankrecherchen

---

## Crystal Report Optionen

Crystal Report Optionen
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Funktion
CRW-Optionen F10
Direktsprung
[ANWR]
.
Die Darstellung der Reporte kann bis zu einem
bestimmten Grad vom Kunden angepasst werden. Dazu dienen die Crystal Report
Optionen die man im Vorschaumodus des Reports in der Optionbox unter
CRW-Optionen Shift-F11
findet:
Die hier gemachten Einstellungen gelten für den
gesamten Mandanten.
Bedeutung
Anzeige des Mandantennamen im
      Berichtskopf/ Berichtsfuß
Die
      Bezeichnung des Mandanten, die im Mandantenstamm eingetragen ist, kann
      sowohl im Kopfbereich als auch in der Fußzeile ausgegeben
      werden.
Anzeige des Benutzerkürzels/des
      Benutzernamens
Man
      kann auswählen, ob das Benutzerkürzel, mit dem man sich anmeldet oder der
      Name ausgegeben wird.
Anzeige der Buchwährung
im
      Berichtskopf eine Zeile mit „Buchwährung …“ steht, in der die aktuelle
      Buchwährung ausgegeben wird.
Listenkopf nur auf der ersten Seite
      anzeigen
Der
      Listenkopf kann neben der Bezeichnung auch noch diverse andere
      Informationen enthalten und somit viel Platz einnehmen. Daher kann es
      wünschenswert sein, diesen nur auf der ersten Seite anzuzeigen und nicht
      auf jeder Seite zu wiederholen.
Listenkopf und –fuß grau
      einfärben
Der
      Listenkopf und Fuß kann optisch durch Einfärbung vom Rest des Berichts
      abgehoben werden. Sollte es auf dem verwendeten Drucker dadurch
      unleserlich werden, so kann man auf die Einfärbung hier
      verzichten.
Jede
      zweite Zeile grau hinterlegen
Bei
      langen Listen oder bei Listen, bei denen die Informationen über mehrere
      Zeilen geht, kann die Übersichtlichkeit durch einfärben jeder zweiten
      Zeile erhöht werden
Standardoptimierung
      verwenden
Die
      SQL-Abfragen werden im Referenz-ERP-Standard daraufhin optimiert, dass der erste
      Datensatz möglichst schnell zur Verfügung steht. Wird das Häkchen
      entfern
[...]


---

## Die Belegerstellung für den Kunden bzw. Berechnung für Kunde und Lieferant

Die Belegerstellung für den Kunden bzw. Berechnung für Kunde und
Lieferant
Da die Wechselsumme dem Remittenten erst am Verfalltag
des Wechsels zur Verfügung steht, er seine Forderung bis dahin also stunden
muss, stellt er dem Bezogenen die zwischenzeitlichen Zinsverluste in Rechnung.
Diesen Wechselzins nennt man Diskont. Er ist beim Gläubiger (Besitzwechsel) ein
Ertrag (Diskontertrag). Zusätzlich zu den Zinsverlusten können dem
Besitzwechselinhaber Spesen entstehen. Auch diese Spesen werden dem Bezogenen in
Rechnung gestellt.
Bei normalen Warenwechseln sind Diskont und Spesen
umsatzsteuerpflichtig.
Ablauf:
Hauptmenü
Mahn-/Zahl-/Zinswesen
Wechselbuchhaltung
Wechselbearbeiten
Direktsprung
[
WEB
]
Wechsel markieren und Ändern mit
F5
drücken:
Hinweis:
Das Einreichungsdatum wird mit dem Verfalldatum
vorbelegt, kann jedoch hier geändert werden. Dies ist das tatsächliche
Einreichungsdatum, mit dessen Hilfe das Wechselobligo eines Kunden an einem
bestimmten Datum bestimmt wird.
Danach
F5
für Diskont Personenkonto
und
F9
,
ENTER
,
Um die Wechselabrechnung zu drucken
F4
,
ENTER

---

## Die Tammo-App

Die Tammo-App
Wird an die E-Mail Adresse
Projekt@<Domäne>.de
eine E-Mail gesendet, die in
der Betreffzeile ein k:<Kundennummer> oder k:<Kundenbezeichnung>
enthält, dann wird mit dem Body der Mail ein neues Projekt für diesen Kunden
eröffnet, selbstverständlich muss dazu der Tammo Treiber auf Ihrem Referenz-ERP System
installiert sein. Als Rückantwort wird die Projektnummer zurückgegeben, mit
einem Informationsblatt zum Kunden und einem Übersichtsblatt zu den offenen
Projekten dieses Kunden wie auch mit den offenen Projekten des Mitarbeiters.
Wird einfach nur eine Mail abgeschickt ohne Betreff an
die Adresse
Projekt@<Domäne>.de
, dann wird
die dem Mitarbeiter zugeordnete Projektliste zurückgegeben.
Enthält die Betreffzeile ein p:<Projektnummer>
und wird diese Mail, ggf. auch mit Anhängen, direkt dem vorhandenen Projekt
zugeordnet, ist die Projektnummer nicht existent, so wird dem Standardkunden der
Projektverwaltung ein neues Projekt zugeordnet, wenn die sendende Mailadresse
nicht schon einem Kunden zugeordnet ist.

---

## DSGVO Objektdefinition

DSGVO Objektdefinition
Hauptmenü
Stammdatenpflege
Anschriften
DSGVO
Direktsprung
[DSGVO]
Variante
DSGVO-Objekte.
In Referenz-ERP existieren verschiedene Anschriftenarten für
die jeweils Objekte definiert wurden. Hierzu gehören Kundenanschriften,
Lageranschriften, Filialanschriften und viele mehr. Diese Objekte fassen alle
Tabellen zusammen, welche die DSGVO betreffen. Zu dem Kunden/Lieferanten-Objekt
gehören beispielsweise folgende Tabellen:
•
Kundenstamm
•
Anschriftstamm
•
Kundenmatchcode
•
Kundenaddon
Branchen-ERP liefert bereits vorgegebene Definitionen solcher
Objekte aus. Bearbeiten Sie diese mit der Anwendung „DSGVO“ in der Variante
„DSGVO-Objekte“.
Bedeutung
Objekt
Kennung des verwendeten Objekts.
Alle
      Objekte sind von Branchen-ERP vorgegeben und es können keine eigenen Objekte
      angelegt werden. Es können aber jederzeit Tabellen entfernt oder
      hinzugefügt werden. Diese werden mit dem Zusatz „Privat“ vermerkt und
      gespeichert.
Referenztabelle
Nur
      Anzeige:
Jedes Objekt bezieht sich auf
      mehrere Tabellen. Die hier angezeigte Tabelle ist die Basis, auf die sich
      alle anderen Tabellen des Objekts beziehen.
Referenzfeld
      (IDENT)/(ADRESSID)
Nur
      Anzeige:
Der
      Feldname aus der Referenztabelle, auf den sich der „IDENT“- oder der
      „ADRESSID“- Wert beziehen.
Tabelle
Zum
      Objekt gehörende Tabellen.
Bestimmt durch
Durch diesen Spaltennamen wird
      bestimmt, welche Daten der DSGVO zugeordnet werden.
Aktion
Was
      soll mit den Feldern/der Tabelle geschehen? Mögliche Aktionen
      sind:
•
anonymisieren:
      Die Daten in den Feldern werden mit
*
überschrieben.
•
löschen: Die
      Daten in den Feldern werden gelöscht.
Beispiel:
Die Tabelle „KundenMatchcode“
      enthält ein Feld. In diesem Fall löschen Sie diese Daten.
WHERE-Bedingung für die
      Liste
Um
      die Datensätze, zu bestimmen, muss eine verknüpfende WHERE-Bedingung
      angegeben werden.
Für
      die Tabelle „Anschriftstamm“ des O
[...]


---

## Einrichtung:

Einrichtung:
Im Artikelstamm werden die jeweiligen Lieferanten des
Artikels hinterlegt. Ist kein Lieferant im Artikelstamm hinterlegt, so erscheint
dieser Artikel nicht in der Bestellvorschlagsliste.

---

## Einrichtung des Basisstruktur

Einrichtung des Basisstruktur
Es existieren 6 verschieden Arten von
Kontaktdarstellungen :
Stammsatz als Einzeleintrag im Outlook
Kontaktordner
Darstellung als Textnotiz
Darstellung als HTML eingebettete Anlagen
Stammsatz als Einzeleintrag, zusätzlich mit
Ergänzungsinformationen
Darstellung als Textnotiz
Darstellung als HTML eingebettete Anlage
Alle Stammsätze in einem Outlook Kontakt
Darstellung als Textnotiz
Darstellung als HTML eingebettete Anlage

---

## Einrichtung Einzeleintrag ohne Ergänzung

Einrichtung Einzeleintrag ohne Ergänzung
Folgendes Outlookbeispiel soll implementiert werden
:
Der Datensatz Kunden setzt sich aus folgenden
Tabreitern zusammen :
Der erste Tabreiter ist neben dem sinnvollen
Tagesupdate Datum noch mit dem Kennzeichen 0 für Einzeleintrag pro Datensatz und
zwar im Feld Wartezeit in min zu versehen, sowie einer Sperre NEIN.
Der Tabreiter 2 ist in der Menüüberschrift mit dem
Firmennamen aufzufüllen, nach diesem Firmennamen kann später eine Gruppierung im
Outlook erreicht werden. Der Firmenname kann ggf. noch um ein Kennzeichen
erweitert werden, um eine bessere Gruppierung zu erreichen. Dieser zusätzliche
Gruppierungsname wird in der Abteilung Feldposition festgelegt.
Der Tabreiter 3 ist im Feld Feldzuordnung mit einem
Wert zu belegen, dazu muss zunächst mit dem F5 Knopf eine Feldzuordnung erstellt
werden, die dann an dieser Stelle per F3 abgerufen werden kann.
Auf dem nächsten Tabreiter ist nun das komplette SQL
Statement zu spezifizieren, nach dem die einzelnen Datensätze ausgewählt werden
sollen :
Das SQL Statement muss in 5 Teile zu zerlegt werden,
es ist notwendig das die kompletten Teilbefehle eingegeben werden, hier darf ein
from oder ein where NICHT weggelassen werden.
Das obigen Beispiel setzt sich zusammen aus dem select
Befehl :
Select top 100 *
Der besagt, dass die ersten 100 Kundensätze gewählt
werden sollen, einem leeren Spezialfeldbereich, einem From Bereich der Form
from kundenstamm k join KUNDENGRLINK
kgr on (k.kundid=kgr.kundid) join anschriftstamm ans on
(k.adressidhauptadr=ans.adressid)
wobei der Kundenstamm mit dem Adressstamm und der
Kundengruppentabelle verbunden wird, sowie einem where Bereich
where KunGrupNummer=85017 and
k.KundLoeKennz = 0
der eine bestimmte Kundengruppe auswählt und einer
Sortierung, die in diesem speziellen Fall keine Bedeutung hat, außer dass beim
Datentransfer die Datensätze sortiert angezeigt werden
order by k.KundBezeich

---

## Erfassung des Kunden

Erfassung des Kunden
Folgende Möglichkeiten zur Erfassung eines Kunden
bestehen:
Eingabe der Kundennummer
Im ersten Feld kann die Kundennummer, die gleichzeitig
die Kontonummer in der Finanzbuchhaltung ist, eingegeben werden. Existiert die
Nummer, so werden die vollständige Adresse sowie einige Konstanten aus den
Kundenstammdaten (z.B. die zugeordnete Vertretergruppe) angezeigt. Ist es der
richtige Kunde, wird mit der Erfassung fortgefahren. Ist es der falsche, dann
kann mit der “Up” - Taste wieder in das Eingabefeld zurückpositioniert und mit
F3 das Kundenauswahlfenster geöffnet werden. Mit "Pfeil hoch" "Pfeil runter"
bzw. mittels Mausklick kann der gewünschte Kunde ausgewählt werden. Das
Kundenauswahlfenster öffnet sich automatisch, wenn im Feld Kundennummer eine
falsche bzw. unvollständige Nummer eingegeben wurde.
Eingabe Matchcode
Bei Eingabe eines Textes im Feld Kundennummer sucht
das System automatisch nach Namen oder Matchcode. Findet es einen eindeutig
passenden, dann wird die Kundenanschrift angezeigt, ist dies nicht der Fall wird
automatisch wieder das Auswahlfenster geöffnet und eine Auswahl zur Verfügung
gestellt.
Aufruf der Auswahlbox
Mit
F3
kann die Auswahlbox auch direkt
aufgerufen werden. Hier stehen neben den beschriebenen Suchmöglichkeiten (unten
rechts) weitere Optionen (Varianten) zur Verfügung. Diese werden ausgewählt,
indem sie mittels der “Maus” aktiviert werden, der Cursor mittels
“
TAB
” vom Eingabefeld in die Optionswahl positioniert wird und
dann der gewünschte Auswahlmechanismus gewählt wird, oder indem im Feld “Ab” die
Variantennummer und direkt dahinter der Aufsetzbereich eingegeben wird.
Im letzten Fall ist also “2.me” einzugeben, um eine
Liste nach Namen ab “me” auf den Bildschirm zu bekommen. Nach Anwahl der Option
wird (unten links) im Feld “Ab” eingetragen, ab welchem Wert die Anzeige
erfolgen soll. Analog zu 3. ist also die Option “Matchcode” auszuwählen und dann
im Feld “Ab” “me” einzutragen. Alle gültigen
[...]


---

## Erfassung von Fremdwährungsbelegen

Erfassung von Fremdwährungsbelegen
Hauptmenü
Finanzbuchhaltung
Erfassung
Belegerfassung
Direktsprung
[FIBE]
Bei der Erfassung von Eingangs- und Ausgangsrechnungen
in der Finanzbuchhaltung können die Belege direkt in der Fremdwährung erfasst
werden. Es wird für den Kunden/Lieferanten die Währung vorbelegt, die in den
Stammdaten bei Währungstyp hinterlegt sind. Dabei werden die im Währungsstamm
hinterlegten Einstellungen - wie z.B. Nachkommastellen – verwendet. Der
Währungskurs wird anhand der in Referenz-ERP hinterlegten
Währungskurse
vorgeschlagen.
Der Betrag, den man erfasst, ist immer der Betrag in
der Währung, die hinter dem Betrag steht. Sämtliche Betragsfelder ganz rechts
auf der Maske sind in Buchwährung.
Ist im Kunden- / Lieferantenstamm als Währung die
Buchwährung  hinterlegt, dann wird das Feld, in dem der „Kontosaldo in der
im Kundenstamm hinterlegten Währung“ angezeigt wird, ausgeblendet. Die Währung
des Beleges kann mit der Funktion
Währung
F5
geändert werden.
Hier kann man sowohl die Währung oder den Währungskurs
ändern. Bekommt man z.B. von seiner Bank einen Beleg, so ist dort der verwendete
Kurs, der u.U. von den Kursen in der Währungskurstabelle abweicht, angegeben.
Der Kurs, den man hier eingibt, wird nicht in der Währungstabelle sondern nur im
Beleg gespeichert. Es ist immer nur eins der drei Felder mit den Kursen
freigeschaltet. Welches der Felder verwendet wird, ist in den
Einrichterparameter
der Belegerfassung hinterlegt.
Hinter „Aktuelle Kurse gültig ab“ steht das Datum, zu
dem die letzten Kurse gepflegt wurden. Stellt man hier fest, dass man die Kurse
für diesen Tag noch nicht eingetragen hat, kann man von hier sofort mit
F8
diese Stammdaten eintragen.
Anschließend kommt noch eine Abfrage, falls bereits
Daten erfasst wurden:
Rechnungen können immer nur in einer Währung erfasst
werden, daher wird immer der gesamte Beleg umgestellt. Bei Zahlungen verhält es
sich anders. Dort bezieht sich die Währung immer nur auf die aktuelle Posit
[...]


---

## Erfassung von Vorgängen als Tabelle

Erfassung von Vorgängen als Tabelle
Die Schnellerfassung kann über den Direktsprung MAG
aufgerufen werden. Es erscheint ein Bildschirm zur Erfassung der Kundennummer.
Nach Eingabe wird auf Basis der im Kundenstamm hinterlegten
Artikelliste
eine Liste der Artikel
angezeigt.
Folgende Funktionen stehen jetzt dem Bearbeiter zur
Verfügung:

---

## Erforderliche Grundeinstellungen

Erforderliche Grundeinstellungen
Aus obigen Ausführungen ergibt sich, dass sich in
einem Unternehmen Abläufe und Optiken für eigentlich vergleichbare Vorgänge
stark unterscheiden können; so z.B., wenn für spezielle Kunden die Rechnung in
einer ganz bestimmten Optik und Erfassungslogik erstellt werden muss.
Trotz der sich hieraus ergebenen Unterschiede lässt
sich das Prinzip der Vorgangs­erfassung am Beispiel der Rechnungserfassung
stellvertretend für alle Bereiche be­schreiben. Auf Abweichungen wird dann
in den Passagen zu den einzelnen Vor­gangs­arten eingegangen.
Beim Einstieg in die Belegerfassung werden generell
folgende Einstellungen auf Korrektheit überprüft:
Ist die Vorgangsklasse vorhanden?
Ist die Vorgangsunterklasse vorhanden?
Ist das zugeordnete Druckformular vorhanden?
Ist das zugeordnete Bildschirmformular vorhanden?
Ist das zugeordnete Vorschauformular vorhanden?
Ist der Nummerkreis zugeordnet worden? (Gültigkeit
wird nicht überprüft)
Wenn etwas fehlschlägt, kommt eine Meldung, mit
welchen Direktsprüngen was behoben werden kann.

---

## Fehlerprotokoll/Systemhinweise

Fehler
protokoll/Systemhinweise
Systempflege
Abstimmung
Fehlerprotokoll
oder Direktsprung
[
FEHLP
]
Im Fehlerprotokoll werden Systemhinweise gesammelt.
Sie dienen dazu Ausnahmefälle und sonstige Umstände zu protokollieren, die
möglicherweise einen ordnungsgemäßen Betrieb erschwerten oder unmöglich
machten.

---

## Finanzbuchhaltung

Finanzbuchhaltung
Die Finanzbuchhaltung ist voll integriert in das
Referenz-ERP - Konzept. Sämtliche Stammdaten, Parameter etc. werden gemeinsam genutzt.
Dies trifft auch dann zu, wenn man in der Finanzbuchhaltung im Bereich
Stammdaten auf Bereiche wie Kundenstamm u.ä. trifft. Es handelt sich dann nur um
Anwahlpunkte für die gleiche Datengrundlage, die zur Arbeitserleichterung hier
noch einmal zur Verfügung gestellt wurden. Natürlich verfügt die
Finanzbuchhaltung auch über eigenständige Stammdatenbereiche, wie
Mahnparameter,Zinsgruppen,… usw.; diese werden dann hier exklusiv gepflegt.
Insgesamt werden derzeit mit der
Referenz-ERP Fi
nanzbuchhaltung folgende Bereiche
abgedeckt:

---

## Funktionalitäten

Funktionalitäten
Folgende generelle Funktionalitäten stehen in diesem
Bereich zur Verfügung
Artikelstapel im tabellarischen Vorgang
Es könne generelle oder aber spezielle,
kundenübergreifende Artikelstapel-Sätze festgelegt werden. Diese Stapelsätze
werden an den Kunden gebunden, einem Kunden wird ein Stapel zugeordnet. Beim
Aufruf der Schnellerfassung wird dann der entsprechende Artikelstapel passend
zum Kunden angezeigt, und es kann ein Vorgang erfasst werden. Des weiteren kann
ein Auftrag oder eine beliebige andere Vorgangsklasse und ein Stapel
zusammengefasst auf den Bildschirm gebracht werden, um daraus einen Lieferschein
oder eine beliebige andere Vorgangsklasse zu machen, und um die Daten ggf. an
die aktuellen Lagerbestände anzupassen. Es stehen im Artikelstapel 4 Preise zur
Verfügung. Diese Preise werden entsprechend der Kundenpreisklassen bei der
Vorgangserfassung angezeigt.
Schnellerfassung
Die Schnellerfassung ermöglicht es, auf einem
Bildschirm schnell und ohne Maskenwechsel, Belege zu erfassen. Bei der
Schnellerfassung wird per Artikelstapel (s.o.) gearbeitet. Es kann aber auch
selbstverständlich ein Artikel angewählt werden, der nicht im Stapel erfasst
worden ist. Bei der Schnellerfassung werden Menge, ggf. Gebindefaktor 1 und 2
und das Gebindemaß, der Preis und ggf. die Preiseinheit und ein Zusatzfeld
erfasst. Bei der Schnellerfassung stehen 4 Speichermöglichkeiten zur Auswahl, es
kann gespeichert werden unter einer festgelegten Unterklasse, des weiteren
stehen zwei Speicher und Druckfunktionen zur Verfügung, die es erlauben, den
Beleg unter anderen Unterklassen abzuspeichern. Als letzte Möglichkeit steht die
Speicherung mit anschließender Korrektur des Beleges zur Verfügung.
Auftrag in Lieferschein
Die Erfassung von Aufträgen kann so gestaltet werden,
dass bei Anwahl des Kunden sofort seine Aufträge zur Auswahl stehen, um einen
der Aufträge dann evtl. zu ergänzen oder aber sofort (incl.
Korrekturmöglichkeit) in einen Liefersche
[...]


---

## Funktionen

Funktionen
Es steht in den Anwendungen Kunden [KU], Lieferanten
[LF] und Kontokorrentkunden [KUKO] die Funktion „UStId prüfen“ zur Verfügung. Es
wird in diesem Fall die eingetragene UStId und/oder die UStIds des Kunden
geprüft.
Im Kundenstammpfleger steht die Funktion „UStId
prüfen“ zur Verfügung. Diese prüft lediglich die im Feld Umsatzsteuer-ID
eingetragene UStId.
Im Umsatzsteuer-ID-Pfleger des Kundenstammpflegers,
den Sie über die Funktion „UStId bearbeiten“ erreichen steht die Funktion „UStId
prüfen“ zur Verfügung. Es wird die jeweils markierte Umsatzsteuer-ID geprüft.
Die letzten beiden Funktionen können parallel auch als
„UStId amtlich bestätigen“ verwendet werden. In diesem Fall wird eine
schriftliche amtliche Bestätigung des Bundeszentralamtes für Steuern per Post
versendet werden. Empfänger ist die zur im Mandantenstamm als ihre
Umsatzsteuer-ID eingetragene Anschrift.
Jede dieser Funktionen zeigt während der Prüfung ein
Wartefenster, auf dem mit dem Abbruch-Button der Prüfvorgang abgebrochen werden
kann. Im Anschluss an die Prüfung wird eine Historie der Prüfungen
angezeigt.
Darüber hinaus gibt es die Möglichkeit,
UmsatzsteuerId´s gemäß einer Definition „in einem Rutsch“ zu prüfen. Dieser
Auftrag wird Asynchron, also im Hintergrund abgewickelt, weshalb hier auch kein
Wartefenster zu sehen ist. Hier ist wie bei den anderen Prüfungen eine Prüfung
mit und ohne amtlicher Bestätigung möglich. Prüfungen, die am gleichen Tag
erfolgen werden vom Bundeszentralamt für Steuern als Prüfliste amtlich
bestätigt.

---

## Funktionen der Konteninformation

Funktionen der Konteninformation
Hauptmenü
Finanzbuchhaltung
Information
Konteninformation
Direktsprung
[KOI]
.
Da die Konteninformation als Werkzeug dienen kann, bei
direktem Kundenkontakt schnell  Informationen über z.B. Kontostand oder
fällige Zinsen zu erhalten, sind hier entsprechende Funktionen hinterlegt:
Zinsrechner
Dies ist der aus der Zinsrechnung bekannte
Zinsrechner, der sich alle Werte aus den Stammdaten ermittelt (siehe
Dokumentation Zinswesen). Nach Eingabe des Abrechnungsdatums werden die seit der
letzten Zinsabrechnung anfallenden Zinsen ermittelt und angezeigt. Da zur
Zinsabrechnung nur gebuchte Belege herangezogen werden erscheint ggf. die
Meldung „Es existieren ungebuchte Belege“.
Konto ändern F3
Springt in das Feld Kontonummer, um eine anderes Konto
auszuwählen.
Infoblatt drucken F10
Diese Funktion steht hier für Sach- und Personenkonten
zur Verfügung. Man erreicht den Report auch über:
Hauptmenü
Abschlussarbeiten
Kontoblätter
Infoblattdruck
Direktsprung
[KOID]
.
Es wird ein Crystal-Report aufgerufen, der die
gebuchten Daten des ausgewählten Jahres und Kontos druckt. Man kann in der
Bereichsauswahl
F2
die Daten auch
zusätzlich noch über die Periode eingrenzen.
Dieser Report ist ähnlich wie ein Kontoblatt zu sehen,
nur werden die Daten nicht erst zusammengesucht und festgehalten, sondern immer
so ausgewertet wie zum Zeitpunkt des Druckes sind. Für Sachkonten wird die
Druckverdichtung analog der Einstellung im
Sachkontenstamm
unter
Formulardruck
ausgegeben.
Archiv Kokore
Diese Funktion steht nur bei Personenkonten zur
Verfügung. Es werden alle archivierten Kokores dieses Kontos im angegebenen Jahr
aufgelistet und können dann angezeigt werden. Für genauere Informationen über
das Archivwesen steht die Formulararchivdokumentation zur Verfügung.
Archiv STRG+F12
Hier werden alle Archiveinträge des ausgewählten
Personenkontos angezeigt, unabhängig von Belegart und Jahr.
Fibu-Merkmale
Diese Funktion steht nur bei Personenkonten zur
Ve
[...]


---

## Funktionen zur Geodaten-Ermittlung

Funktionen zur
Geodaten-Ermittlung
Auswahlliste (einzelne Punkte)
Kunden
Menü Karte
Geodaten ermitteln
Zunächst einmal lassen sich in den Anwendungen
Anschriften und Kunden die Geodaten für die gewählte Anschrift bzw. die
Hauptanschrift des gewählten Kunden mit der Funktion „Geodaten ermitteln“ im
gewählten Webservice abfragen und in die Anschrift eintragen. Bitte beachten
Sie, dass hierbei je nach Anbieter Kosten anfallen können.
Menüfunktion (initial)
Stammdatenpflege
Anschriften
offene Geodaten ermitteln
Aus dem Menü lassen sich initial Anschriften mit
Geodaten versehen. Eine Prozedur, die im Mandantenstamm festgelegt wird,
ermittelt hier die Anschriften, die mit GeoDaten versehen werden sollen und
fragt für diese die GeoDaten bei dem eingestellten Anbieter ab.
Die Prozedur wird im
Mandantenstamm
eingepflegt
Bitte beachten Sie, dass dies u.U. sehr lange dauern
kann und ggf. Kosten je nach Anbieter nach sich ziehen kann.
Event
Referenz-ERP kann im Zeitplandienst die Menüfunktion
aufrufen und somit z.B. in der Nacht alle neuen Anschriften nachpflegen.

---

## Gelöschte Kunden entfernen (inkl. 1+2)

Gelöschte Kunden entfernen (inkl. 1+2)
Kunden mit einem Löschkennzeichen ungleich 0 werden in
folgenden Tabellen entfernt:
Kundenstamm
KundenAddon
KundenMatchcode
KUNDENAUSLAND
KUNDENBANK
KUNDENBONUS
KUNDENGRLINK
KundenInfoZeile
KundenKredit
KundenMarkier
KUNDENMITGLIED
KUNDENOBERKUNDE
KUNDENSUMMEN
KUNDENVERSANSCHR
KUNDENZAHLBED
KUNDENZAHLKUNDE
artilieferant
KoNTOSTAMM
Zuvor werden folgende Tabellen überprüft, ob der
gelöschte Kunde entfernt werden darf:
Warenbewegung
KONTRGRUPPE
Warenbuch
KontraktGrKunde
KontrUnter
LeergutKonto
BAUSTKUNDLISTE
BAUSTLIEFLISTE
ArtiStueckKunde
PARTIELIEFLISTE
PARTIEKUNDLISTE
Beim Entfernen der gelöschten Kunden werden
automatisch die
Vorgänge Ware
und
Vorgänge
Finanzbuchhaltung
mit gelöscht.

---

## Hinzufügen eines Artikels

Hinzufügen eines Artikels
Mittels Funktionstaste F8 oder Kontextmenü und Auswahl
des Menüeintrags „Kunde/Artikel hinzufügen“ kann in der Kundensicht ein bislang
noch nicht gepflegter Artikel in die Preisstapelpflege einbezogen werden. Die
sich zwecks Artikelauswahl öffnende Dialogbox ist hinsichtlich Waren- und
Lagergruppennummer vorgefiltert:
Nach Auswahl eines Artikels wird das erfolgreiche
Hinzufügen dieses Artikels zum Stapelpfleger bestätigt. Das „gültig ab“ Datum
des neuen Eintrags wird auf den Anfang des Geschäftsjahres gelegt, in dem die
aktuell angezeigten Preispunkte liegen. Das „gültig bis“ Datum wird
standardmäßig auf das Ende des Geschäftsjahres gelegt, in dem der späteste
Preispunkt liegt. Werden aktuell keine Preispunkte angezeigt – was technisch
möglich ist – wird das „gültig bis“ Datum auf den Wert des gleichlautenden
EPA-Parameters gelegt.

---

## Hinzufügen eines Kunden

Hinzufügen eines Kunden
Mittels Funktionstaste F8 oder Kontextmenü und Auswahl
des Menüeintrags „Kunde/Artikel hinzufügen“ kann in der Artikelsicht ein bislang
noch nicht gepflegter Kunde in die Preisstapelpflege einbezogen werden.
Die sich zwecks Kundenauswahl öffnende Dialogbox ist
zunächst ungefiltert, bietet aber die Möglichkeit nach Kundennummern zu
suchen:
Wurde ein Kontokorrentkunde ausgewählt, muss das
System nochmals nachfragen, ob VK- oder EK-Preise anzuwenden sind:
Insofern der gewählte Kunde für die ausgewählte Seite
(Einkauf/Verkauf) noch keinen Preisklasseneintrag besitzt, bietet das System die
Möglichkeit, die Einträge der aktuell selektierten Preisklasse zu kopieren –
aber nur insofern die Seiten passen (Einkauf/Verkauf):
Die erfolgreiche Durchführung der Aktion wird vom
System bestätigt.

---

## Info

Info
Der Reiter „Info“ ist Firmen bezogen. Alle Datensätze,
die hier ausgewertet werden, werden auf Basis der in „Kontakt“ ausgewählten
Firma angezeigt.

---

## Informationen

Informationen
Warenbuchanzeige (SF2)
Verzweig in den Bereich Warenbuchauswertung
[WBA]
. Übergeben werden die Parameter Kunden-
und Artikelnummer.

---

## Informationsbildschirm

Informationsbildschirm
In der rechten unteren Hälfte befindet sich ein
Informationsbereich, in dem wichtige Daten über den Kunden angezeigt werden
können: Umsatz, OP, Sperrvermerk, Wegbeschreibung etc. Welche Informationen
angezeigt werden sollen, kann pro Vorgangs-Klasse / -Unterklasse selbst bestimmt
werden. Die Einrichtung dieses Fensters erfolgt in Formulareinrichter für den
Erfassungsbildschirm und den Bereich „Bildschirm – Information“.

---

## Itembox der Nr. Feldes

Itembox der Nr. Feldes
Normalerweise ist die Artikelstapel Listennummer
ungebunden. Es kann beim Kunden in dem Bereich Zusatzangaben hinterlegt werden,
welcher Kunde welche Listennummer ihm zugeordnet werden soll.
Im Feld Marktstandsatz ist im obigen Beispiel die
Liste 10719 direkt mit diesem Kunden verbunden worden. Um nun eine direkt
Kundenzuordnung zu gewährleisten, kann durch Angabe einer Itembox festgelegt
werden, dass das Listennummernfeld immer an die Kundennummer gebunden werden
soll. Wird eine neue Kundenbezogene Liste erstellt, so wird automatisch die
Listenzuordnung im Kundenstamm eingetragen.

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

## Kontakt

Kontakt
Im Reiter Kontakt kann ein Firmendatensatz ausgewählt
werden, welcher von den Reitern „INFO“ oder „SHOP“ genutzt wird.

---

## KUI

KUI
Verzweigt in das Kundeninformationssystem eines
ausgewählten Kunden.

---

## Kunde

Kunde
Zunächst muss der Kunde gepflegt werden. Hierfür unter
[KU]
den gewünschten Kunden auswählen
und mit F5 bearbeiten. Auf dem Tab-Reiter „Pfleger“ befindet sich nun die
Einstellung für die FutterApp.
Zunächst den Schalter auf „Ja“ setzen und anschließend
in der rechten Tabelle die Warengruppen aussuchen, welche der Kunde auf seiner
App angezeigt bekommen soll. Der Button „alle Warengruppen“ füllt die Tabelle
mit allen in Referenz-ERP eingetragenen Warengruppen.
Im zweiten Schritt muss nun noch die Anschrift
gepflegt werden. Hierfür die Funktion aus der Optionbox auswählen und die der
Anschriftenmaske auf den Tab-Reiter „Zusätze“ wechseln.
Dort muss die VVVO-Nummer eingetragen werden.

---

## Kundenauswahl

Kundenauswahl
Die Kundenauswahl sucht standardmäßig –
-
Nach Kundennummern (wenn der eingegebene Wert eine Zahl ist und die länge
kleiner 6 ist)
-
Nach Telefonnummern, wenn der eingegebene Wert eine Zahl ist, die Zahl mit 0
beginnt oder länger als 6 Zeichen ist
-
Im Feld Kundenbezeichnung, Kundennamen und Kundenort sowie Matchcode, wenn es
sich um eine Texteingabe handelt.

---

## Kundenanruf (SPA 548)

Kundenanruf (SPA 548)
Aus den Auswahllisten Kunden, Lieferanten,
Interessenten ist die Funktion
Kundenanruf
verfügbar, wenn der
Steuerparameter 548
aktiviert
ist.
Um diese Anwendung nutzen zu können benötigen Sie eine
Lizenz
.
Allgemeines zu TAPI/CTI:
Das Telephony Application Programming Interface (TAPI)
ist eine
Programmierschnittstelle
für
Telefonieanwendungen
.
TAPI-
Treiber
sind in Verbindung mit
ISDN
-
Telefonanlagen
zur Konfiguration und Rufbehandlung mittels
CTI
gebräuchlich.
Computer Telephony Integration (CTI,
Rechner-Telefonie-Integration) ist die Verknüpfung von
Telekommunikation
mit
elektronischer
Datenverarbeitung
.
Die CTI ermöglicht, aus
Computerprogrammen
heraus den automatischen Aufbau, die Annahme und Beendigung von
Telefongesprächen
,
den Aufbau von
Telefonkonferenzen
,
das Senden und Empfangen von Faxnachrichten, Telefonbuchdienste, sowie die
Weitervermittlung von Gesprächen.
Mehr zu Telefoniesystemen in Referenz-ERP finden Sie
hier.

---

## Kundenbanken für den Zahlungsverkehr

Kundenbanken für den Zahlungsverkehr
Hauptmenü
Stammdaten
Kunden-/Lieferanten
Kundenstamm bzw. Lieferantenstamm
Direktsprung
[KU]
bzw.
[LF]
Kundenbanken sind die Bankverbindungen der Kunden und
Lieferanten, die im Zahlungsverkehr verwendet werden. Der Stern in der ersten
Spalte kennzeichnet die Bank, die beim automatischen Zahlungsverkehr
herangezogen wird, falls mehrere Banken eingerichtet sind. e-Clearing verwendet
diese Banken, um das Kundenkonto zu bestimmen.
Im Kunden- /Lieferantenstamm ruft man das
Personenkonto mit
F5
auf und gelangt dort über die Funktion
Bankverbindungen
Shift+Strg F8
in die Erfassungsmaske.
Zusätzlich existiert eine Auswahlliste (Direktsprung
[KUBA]
), in der sämtliche Kundenbanken
angezeigt und bearbeitet werden können.
BLZ und Bankkontonummer werden hier nicht mehr
angezeigt bzw. abgefragt, da der Zahlungsverkehr in Deutschland nur noch über
BIC und IBAN abgewickelt wird. Sollte es doch notwendig sein, hier eine
Bankkontonummer zu erfassen, so kann man mit dem
Steuerparameter
1121 „Bankleitzahl
und Kontonummer anzeigen“, diese Felder wieder aktivieren.
Im automatischen Zahlungsverkehr kann diese Maske an
vielen Stellen direkt aufgerufen werden.
Beschreibung
IBAN
Die
      „International Bank Account Number“ - kurz IBAN- wird im Zahlungsverkehr
      immer wichtiger. In dem ab dem 28.01.2008 gestarteten SEPA Verfahren wird
      sie an Stelle der Kontonummer verwendet. Bei der Erfassung der
      Kundenbanken wird die IBAN für deutsche, österreichische und belgische
      Banken anhand eines Prüfzifferverfahrens überprüft.
Der
      Test der IBAN kann entweder für jede
Bank
oder global per
Steuerparameter
abgeschaltet
      werden.
In
      der IBAN ist die Bankleitzahl und Kontonummer enthalten. Anhand der
      Bankleitzahl wird der Bankenstamm durchsucht und dann die Bank und
      Kontonummer eingetragen. Wird keine Bank vorgeschlagen ist entweder der
      Bankenstamm nicht korrekt gepflegt oder die IBAN ist ni
[...]


---

## Kundendatenpflege für Beleg-Mailversand

Kundendatenpflege für
Beleg-Mailversand
Zu guter Letzt sollten Sie beachten, dass eine E-Mail
nur an einen Empfänger gesendet werden kann, wenn der E-Mail-Empfänger auch
bekannt ist.
Im Kundenstamm des Kunden finden Sie das Feld
E-Mail-Adresse. Dort muss für den Kunden eine gültige E-Mail Adresse eingetragen
sein, unter der die Belege zugestellt werden können.
Im Kundenstamm
[KU]
pflegen Sie auf der
Registerkarte Kennzeichen
das Merkmal
Belegversand
.

---

## Kundenbezug einrichten

Kundenbezug einrichten
Wenn in der Artikelzeile unter Kundenbezug ein ja
eingetragen ist, können hier die Kunden hinterlegt werden.
Um die Kunden, die zu diesem Folgeartikel Bezug haben
einzutragen, müssen Sie die jeweilige Folgeartikelzeile markieren. Beim Wechsel
der Folgeartikelizeile wird eine Eintragung gespeichert und die Liste der
Kundenbezüge der aktivierten Zeile geladen.

---

## Kundengruppen

Kundengruppen
In der Option Box gibt es die Funktion Kundengruppen.
Über diese öffnet sich eine Maske in der die Gruppenzugehörigkeit des jeweiligen
Kunden eingetragen und eingesehen werden kann.

---

## Kunden/-Lieferantenstamm

Kunden/-Lieferantenstamm
Hauptmenü
Stammdatenpflege
Kunden/Lieferanten
Kundenstamm
Direktsprung
[KU]
,
[KUKO]
.oder
[LF]
Im
Kunden-/Lieferantenstamm
findet man
die für den Zahlungsverkehr benötigten Felder auf dem Reiter
„Fibu-Merkmale“.
Beschreibung
Zahlungsempfänger/
Zahlungspflichtiger
Beim
      automatischne Zahlungsverkehr wird der Name des Zahlungspflichtigen bzw.
      des Zahlungsempfängers benötig. Hierbei gilt folgende
      Regel.
4)   Ist in der Kundenbank
      ein Empfänger eingetragen, so wird dieser verwendet und sofort in den
      Zahlungsvorschlägen vermerkt.
5)   Ist der Empfänger in
      den Kundenbanken leer, dann wird dieses Feld verwendet. Die Bestimmung
      erfolgt erst beim DTA.
6)   Ist dieses Feld Leer,
      dann wird die Kundenbezeichnung verwendet.
Zahlsperre
Mit
Ja
ist der Kunde für Zahlungen gesperrt.
Verrechnung Gutschriften
Für
      die Erstellung von Zahlvorschlägen kann mit diesem Kennzeichen bestimmt
      werden, ob debitorische und kreditorische Vorgänge miteinander verrechnet
      werden sollen:
•
Keine
      Verrechnung: Es erfolgt auch dann eine Zahlung, wenn der Kunde einen
      negativen Saldo hat
•
Alle Belegarten:
      Es wird nur der Saldo zur Zahlung gestellt
•
Trennung Ein-
      und Verkauf: Es wird der Saldo aus den Einkäufen zur Zahlung
      gestellt
Zahlungsart Eingang
      (Debitor)
Die
      Standardzahlungsart, wenn der Kunde bezahlt:
•
Scheck
•
Datenträgeraustausch
Die Zahlungsart kann bei der
      Vorgangserfassung für den konkreten Vorgang überschrieben
      werden.
Zahlungsart Ausgang
      (Kreditor)
Die
      Standardzahlungsart, wenn an den Kreditor bezahlt wird:
•
Scheck
•
Datenträgeraustausch
Die Zahlungsart kann bei der
      Vorgangserfassung für den konkreten Vorgang überschrieben
      werden.
OP-Typ
Der
      OP-Typ hat drei Ausprägungen
•
Standard hat
      keine Besonderheiten.
•
OP-Raffung bei
      Kokoreerstellung:  Bei der Erstellung des Kokores werd
[...]


---

## Kundennummer (Waagendatenimport-/-export)

Kundennummer (Waagendatenimport-/-export)
Kann die Kundennummer nicht gelesen werden, so wird
sie auf 0 gesetzt. Belege, die unberechtigt mit der Kundennummer 0 belegt
werden, können später nicht in Vorgänge umgewandelt werden!
Steht der ScriptParameter TANKKTE_KUNDx auf 1, so wird
die gelesene Kundennummer als Tankkartennummer interpretiert. Anschließend wird
über die
Relation KundenTankKarte
der zugehörige Kunde ausgewählt. Ein Fehler an
dieser Stelle
bewirkt einen Eintrag im Fehlerprotokoll (und die
Abweisung des Importes dieses Datensatzes): "DBFehler b. Kunden-Ermittl. f.
Tankkarte [...], Datei [...], Übern. #..., Zl. #..."
Die Kundennummer wird zusammen mit EK-/VK-Kennzeichen
bzw. Vorgangsklasse gegen den Kundtyp validiert. Ein Fehler an dieser Stelle
bewirkt einen Eintrag im Fehlerprotokoll (und die Abweisung des Importes dieses
Datensatzes): „KundNr o. Typ falsch [...], Datei [...], Übern. #..., Zl.
# ...“.
(Zugehörige Positionsparameter: KU_SAx)

---

## Kunden Reporte – Beschreibungen

Kunden Reporte – Beschreibungen
Hauptmenü
Administration
Werkzeuge
Anwendung Reports
Direktsprung
[ANWR]
.
In dieser Auswahlliste kann man alle Reporte finden
die in Referenz-ERP vorhanden sind und über die Funktion Liste drucken F9 auch
aufrufen.

---

## Kundenstruktur

Kundenstruktur
Es wird erwartet, dass sämtliche userspezifische
Dateien in diesen Verzeichnissen hinterlegt werden:
\aeins\user
\aeins\user\batch
\aeins\user\rpt
\aeins\user\sql
\aeins\user\script
\aeins\user\Excel
\aeins\user\Winword
\aeins\user\Dateien

---

## Kundenwechsel

Kundenwechsel
Nach Eingabe der Kundennummer oder des Kundennamens
erscheint ein breiter Knopf, auf dem die Kundenbezeichnung festgehalten ist.
Wird dieser Knopf betätigt, so kann der Kunden auch während der Erfassung oder
am Ende der Eingabe noch geändert werden.

---

## Listennummer

Listennummer
Jedem Artikelstapel wird eine Nummer zugeordnet, diese
Nummer kann frei vergeben werden, es ist aber sinnvoll, bei kundenspezifischen
Artikelstapellisten die Listennummer und die Kundennummer parallel laufen zu
lassen, in diesem Fall unterstützt eine ITEM-BOX und eine Automatikfunktion zur
Kundenzuordnung die Arbeit.
Die Listennummer 0 hat eine spezielle Bedeutung, diese
Liste kann zu Vererbungszwecken herangezogen werden.

---

## Mahngruppen

Mahngruppen
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Mahnwesen einrichten
Funktion Mahngruppen
F9
Direktsprung
[FIMSG]
.
Hierbei handelt es sich um eine Klassifizierung der
Mahnungsbehandlung. Die Mahngruppe wird im Kundenstamm hinterlegt.
Beschreibung
Mahngruppe
Laufende Nummer der
      Mahngruppe
Bezeichnung
Textbeschreibung der
      Mahngruppe
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Steuerschlüssel
Welcher Steuerschlüssel soll beim
      Erstellen der Fibu-Belege für Zinsen bzw. Mahngebühren herangezogen
      werden. Bei der Festlegung des Steuerschlüssels ist daran zu denken, dass
      Mahngebühren und Mahnkosten nicht das Entgelt besonderer Leistungen und
      somit nicht steuerbar sind! Aus diesem Grund sollte hier ein
      Steuerschlüssel mit dem Steuersatz 0.0 % hinterlegt werden!
Betrag ist Netto oder
      Brutto
Hier
      kann man hinterlegen, ob die Gebühren Netto oder Brutto gebucht werden.
Wie
      mahnen
Hier
      wird festgelegt, welche Belege auf der Mahnung erscheinen
      sollen:
0
alle Posten
Es werden alle offenen Posten, sowohl fällige als
      auch nicht fällige, in einer Mahnung gedruckt. Beim Berechnen der Summen
      erfolgt eine Verrechnung von Soll und Haben.
1
Mahnbar getrennt nach Mahnstufe
Für alle Mahnstufen wird eine
      separate Mahnung erstellt. Es erfolgt keine Verrechnung von Soll und
      Haben.
2
Mahnbar + weitere Sollposten.
Es werden alle Sollposten, egal ob
      fällig oder nicht, in der Mahnung aufgeführt. Es erfolgt keine Verrechnung
      von Soll und Haben. Für alle Mahnstufen wird nur eine Mahnung
      erstellt.
3
Mahnbar + fällige Habenposten
Es
      erscheinen alle fälligen Belege auf der Mahnung. Beim Berechnen der Summen
      erfolgt eine Verrechnung von Soll und Haben. Für alle Mahnstufen wird nur
      eine Mahnung erstellt.
4.
Ma
[...]


---

## Mehrere Datensätze in einem Kontakt

Mehrere Datensätze in einem Kontakt
Sollen mehrere Datensätze in einem Kontakt abgelegt
werden, wie es z.B. bei einer Preisliste der Fall ist, so muss dieses wie folgt
angelegt werden :
Tabreiter 1 :
Die Wartezeit ist auf 1 zu stellen, und die Sperre auf
Nein.
Tabreiter 2:
Die Menüüberschrift gibt den Outlook „Speichern unter“
Bereich an.
Im Tabreiter 3
wird die oben schon erwähnte Feldzuordnung angegeben,
die dann per F5 aufgefüllt wird, um die Feldzuordnungen zu den einzelnen
Kontaktfeldern herzustellen.
Im Tabreiter 4 :
Ist dann das komplette Sql Statement anzugeben, wobei
der Notizbereich wieder als Feld Notiz mit einem Alias Namen versehen werden
muss.
Unter der Feldzuordnung sind in diesem Beispiel die
Felder von Datum und bis Datum Gültigkeit des Preises in das Feld Vorname
(FirstName) und Nachname (LastName) eingetragen. Die Feldsortierungen über 100
spielen in diesem Bereich keine Rolle.

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

## Menu-Funktionen der MapsTourenplanung

Menu-Funk
tionen der MapsTourenplanung
Optimieren
Die Reihenfolge der Wegpunkte in der Liste bestimmt
sich aus der evtl. vorgegebenen Startadresse, den Anschriften in der
Reihenfolge, wie sie auf der Auswahlliste markiert wurden und ggf. bei einer
Rundtour dem Ausgangspunkt. Diese Punkte können mit den Up/Down-Tasten verändert
werden, um eine andere Route zu erreichen.
Wenn ein API-Key für GoogleMaps vorhanden ist, lassen
sich die Entfernungen der Wegpunkte zu Beginn des Anwendungsstarts ermitteln.
Diese Ermittlung ist u.U. kostenpflichtig.
Mit Hilfe dieser Entfernungen lässt sich mit der
Funktion „Optimieren“ die kürzeste Wegstrecke von der Quelle zum Ziel ermitteln.
Im Browser ansehen
Die ermittelte Wegpunktliste lässt sich als Liste von
Schriften im Browser aufrufen. GoogleMaps zeigt dann im Browser die
Routenführung genau an und diese lässt sich dann ggf. ausdrucken oder an ein
Mobilgerät senden.
Reihenfolge umdrehen
Die ermittelte Wegpunktliste lässt sich auf den Kopf
stellen, also in der Reihenfolge vom letzten zum ersten Verkehren. Somit können
die zunächst als letzte Wegpunkte gewählten Stationen an den Anfang und die
ersten an das Ende gesetzt werden.
Drucken
Hier wird, wenn nicht anders eingestellt, ein
Standard-Report mit der Wegpunktliste und ihren Anschriften erstellt

---

## Änderungen im Ablauf des Zahlungsverkehrs

Änderungen im Ablauf des Zahlungsverkehrs
Der grundsätzlich Ablauf (Zahlungsvorschläge
erstellen, Zahlungsvorschläge freigeben, ...) bleibt bestehen wie er ist. Für
SEPA werden nur die Kunden und Lieferanten herangezogen, deren Bank zu einem der
31 teilnehmenden Länder zählt. Dafür muss das Kennzeichen „SEPA-Teilnahmestaat“
im Staatstamm gesetzt sein und der Bank muss das korrekte Land zugewiesen sein.
Zum SEPA-Lastschriftverfahren werden nur die Kunden herangezogen, bei denen ein
Mandat hinterlegt ist. In der Auswahlliste „
Zahlungsvorschläge bearbeiten
“, gibt
ein Hinweistext genauere Auskunft darüber, warum die Belege ggf. nicht zum
SEPA-Verfahren herangezogen werden.
Zusätzlich kommt bei SEPA-Lastschriften hinzu, dass
Erstlastschriften fünf Bankarbeitstage - sogenannte TARGET-Arbeitstage –,
Folgelastschriften zwei Bankarbeitstage vor Fälligkeit und Firmenlastschriften
einen Tag vor Fälligkeit bei der Bank des Debitors eintreffen müssen. Diese Tage
werden beim Erstellen der Zahlungsvorschläge für SEPA-Lastschriften über „
Zahlvorschläge erstellen
“
(Direktsprung
[ZHVE]
) automatisch berücksichtigt. Die Anzahl der
Tage lässt sich dort in den Einrichterparametern festlegen. Sie stehen
standardmäßig auf 5, 2 bzw. 1 Tage. Sollen auch die Laufzeiten automatisch
mitberücksichtigt werden, so können man hier die Tage auf z.B. 6 und 3 Tage
geändert werden. Bei der Berechnung der Bankarbeitstage werden neben Samstagen
und Sonntagen auch Neujahr, Karfreitag, Ostermontag, der 1.Mai sowie der 1. Und
2. Weihnachtsfeiertag nicht mitgezählt.
Aus diesem Grund kann man das Ausführdatum für SEPA
nicht mehr für die gesamte Datei setzen, wie man es vom DTA her kennt. Das
Ändern des Ausführdatums erfolgt jetzt für jeden Zahlungsbeleg in der Anwendung
„Zahlungen Bearbeiten“ mit der Funktion
Formularänderung
F5.
Dort wird bei der Erfassung des Datums
die Prüfung der Bankarbeitstage noch einmal vorgenommen und das eingegebene
Datum ggf. automatisch angepasst. Das
[...]


---

## Neuanfang

Neuanfang
Ist ein Kunde angewählt, so kann die angefangene
Bearbeitung komplett gelöscht und ein neuer Kunden angewählt werden. Hierzu
steht der Knopf „S“ für Storno in der linken oberen Ecke nach Eingabe der Kunden
zur Verfügung, zu Anfang ist dieser Knopf mit einem K versehen, um ggf. auf
Tablett PCs den Kunden per Stift auswählen zu können.

---

## Oberfläche - Zusatz

Oberfläche - Zusatz
Auf der Registerkarte
Zusatz
werden die weiteren Daten zum
Kunden sowie zur Verarbeitung angezeigt.
Auf dem Register
Zusatz
sind folgende Felder zu sehen:
Ansprechpartner Kontaktdaten
      Default
Telefon
Die
      Telefonnummer des Ansprechpartners, wenn nicht im Bediener
      hinterlegt.
E-Mail-Adresse
Die
      E-Mail-Adresse des Ansprechpartners, wenn nicht im Bediener
      hinterlegt.
Der Ansprechpartner stellt eine Person im eigenen
Unternehmen dar, welche Sie bei Fragen oder Problemen zu dieser Rechnung
kontaktieren können.
Verarbeitung
Dateipfad
Dort
      werden die erstellten XMLs hinterlegt.
Dateipfad Test
Dort
      werden die XMLs hinterlegt, welche durch die Funktion
Rechnung testen
erstellt
      wurden.
Webservice
Ob
      die eRechnung an einen Webservice zur Verifikation weitergeleitet wird,
      dabei gibt es folgende Möglichkeiten:
0
- nicht durchführen:
Das erzeugte Xml wird nicht zur Verifikation an den
      Webservice gesendet.
1
- nur
      protokollieren: Das erzeugte Xml wird zur Verifikation an den Webservice
      gesendet, das Ergebnis wird aber lediglich
      protokolliert.
2
- immer
      beachten: Das erzeugte Xml wird immer an den Webservice gesendet - schlägt
      die Verifikation fehlt, wird der Export sofort wieder gelöscht, nur
      archiviert.
Versandprozedur
(!
      Nur im Exportformat UBL !)
Hier
      kann eine Versandprozedur angegeben werden. Diese muss zwei
      Eingabeparameter haben. Diese sind die
Fa_id
und die
Fa_MndNr
des Archiveintrags, der nach
      der Erstellung versendet werden soll. Die Ziel-Mailadresse wird hier drin
      ermittelt und der Versandprofilstammeintrag u. U. fest verdrahtet
      eingetragen.
Dateinamensfkt.
Hier
      kann eine Datenbankfunktion zur Findung des Dateinamens eingetragen
      werden. Als Standard gilt „AMIC_STD_XRE_Filename“.

---

## Outlook Integration

Outlook Integration
Neben der Möglichkeit, direkt einen Vorgang von Referenz-ERP
heraus in eine e-Mail zu verpacken, und diese dann zu versenden, gibt es noch
die Außendienstanbindung mit Outlook als "Frontend" Programm.
Es wird per Übergabeprogramm die Kontakttabelle von
Outlook mit Daten versorgt, so dass der Außendienstmitarbeiter in seinem Laptop
oder seinem Pocket PC die Informationen über seine Kunden ohne direkte Anbindung
an die Datenbank, also ohne direkte Verbindung zum Referenz-ERP Server, zur Verfügung
hat. Es können dem Außendienst alle Informationen der Datenbank zur Verfügung
gestellt werden.
Ist auch ein AIP System angeschlossen, so können auch
direkt über den e-Mail Weg Daten, wie z.B. Besuchsberichte an den Referenz-ERP Server
zurück übermittelt werden.

---

## Pflege der Kundendaten

Pflege der Kundendaten

---

## Projektaufnahme

Projektaufnahme
Ein in das System kommendes Projekt kann an dieser
Stelle schnell und effizient erfasst werden. Hierzu ist irgendetwas von dem
Kunden einzugeben, wie z.B. der Ort, die Nummer, die Telefonnummer, teile des
Namens, … entweder wird eine Liste der möglichen Kunden angezeigt, oder aber es
wird direkt der Kunde zur Bearbeitung freigegeben.
Jetzt ist nur noch der Grund des Neueintrages zu
erfassen, und schon steht der nächste Projekteintrag zur Verfügung.
Jede Aktivität mit dem Kunden ist als neues Projekt zu
erfassen, eine Übersicht über die Projekte des Kunden steht immer zur
Verfügung.
Als Besonderheit ist zu erwähnen, das jedem Projekt
ein oder mehrere Archiveinträge zugeordnet werden können.
Die Referenz-ERP App auf Basis des Tammo-Treibers lässt
direkt Projekte unter
projekt@<Domäne>.de
mit angegebener Kundennummer erfassen und / oder bearbeiten.
Direkte Benachrichtigungen vom Projekt aus an den
Kunden, Mitarbeiter, Abteilung, … sind schon während der Neuaufnahme
möglich.

---

## Projektverwaltung

Projektverwaltung
Hauptmenü
Stammdatenpflege
Projektverwaltung
Innerhalb Referenz-ERP kann per Direktsprung HL zu jedem
Kunden eine Projektverwaltung mit beliebig vielen Projekten eingerichtet und
verwaltet werden.
Basis der Projektverwaltung ist der
Verwaltungsbildschirm:
Zu jedem Projekt wird eine Fallnummer angelegt, in der
verschiedene Informationen bearbeitet werden können.

---

## Relation KundenTankKarte

Relation
KundenTankKarte
In der Relation KundenTankKarte können zu einer KundId
Tankkartennummern mit einem max. Gültigkeitsdatum hinterlegt werden. Diese
Relation kann auch für Beliebige Umschlüsselungen der Kundennummer verwendet
werden.
Kundid
integer     4 0 .................... N  N
KundTKartBisDatum
date        4 0
today(*)+365         Y  N
KundTKartNr
integer     4 0 .................... N  Y
KundId:
Die Verknüpfung mit dem
Kundenstamm
KundTKartBisDatum:
Letztes Gültigkeitsdatum
(hat nur Informations-Charakter, da eine Validierung nicht stattfindet.
KundTKartNr:
Nummer der Tankkarte, muss absolut
eindeutig sein.

---

## Reorganisation

Reorganisation
Innerhalb des Silosystems lassen sich 3 verschiedene
Reorganisationsmaßnahmen vornehmen:
-
Fehlgebuchten Beleg aus dem Silosystem entfernen
-
Netto- bzw. Sekundärmengen neu berechnen lassen
-
Vom Standard abweichende Qualitätswerte entfernen
Im laufenden Betrieb des Silosystems kann es immer
wieder vorkommen, dass Buchungen entstehen, die aber im Siloumfeld so nicht
gewünscht sind. Diese „Fehlbuchungen“ können mit dem Reorganisationsabschnitt
aus den aktuellen Buchungen wie auch aus dem Silo-Bewegungsprotokoll komplett
entfernt werden, es bleiben dabei keine Inhalte mehr im System. Hierzu ist
einfach der entsprechende Beleg in der Siloanwendung (Variante 1) anzuwählen und
es ist das Reorganisationsmodul aufzurufen. Sind mehrere Belege oder ist kein
Beleg markiert, so wird ein Beleglöschen nicht akzeptiert. Auf der dann
erscheinenden Maske kann nun u.U. noch der zugehörige Waagebeleg mit
„zurückgesetzt“ (von Status „abgeschlossen“ auf Status „zweite Wiegung“) werden.
Nach Anwahl der Funktion wird sofort mit dem Löschvorgang begonnen.
Ein weiterer, häufig auftretender Problemfall, ist
eine Abweichung der gebuchten Menge und ihr zugehöriger Nettomengenanteil (bzw.
Sekundärmengenanteil).  Zum Reorganisieren des Netto- wie auch
Sekundärmengenanteils steht mit der Funktion ein Abschnitt zur Verfügung, der
direkt die kompletten, den Silozellen zugeordneten, Netto/Sekundärmengen aus dem
System entfernt und auf Basis der aktuellen Situation wieder neu berechnet. Es
besteht auch die Möglichkeit für einzelne Silobereich durch Angabe der Silo-von
bzw. bis Nummern eine Reorganisation durchführen zu lassen.
Durch nicht eingerichtete Min-Max Bereiche im
Qualitätserfassungsbereich kann es vorkommen, dass Qualitätswerte nicht korrekt
eingegeben worden sind. Um nun solche „Abweicher“ wieder aus dem System zu
entfernen, gibt es die Möglichkeit, im Artikelbestandteil Abschnitt für jede
Qualität einen Minimalwert und einen Maximalwert
[...]


---

## Replikation-Informationen

Replikation-Informationen
Hauptmenü
Filialsystem
Stammdaten
Übersicht Replikation
oder Direktsprung [
RINFO
]
Dieser Dialog stellt Informationen zur Replikation zur
Verfügung.
Die angezeigten Informationen werden alle 3 Sekunden
aktualisiert.
Felder
Zentrale
Replikationsadressen
      Zentrale
Server
Datenbank-Server
auf
Computer
DB-File
Datenbank-Property
      „File“
DB-Logname
Datenbank-Property
      „Logname“
Server-Zeit
Die
      Zeit des Datenbank-Servers zu Referenzzwecken.
Datenbank
Datenbank-Property
      „alias“
Publisher
Sofern vorhanden der „Current
      Publisher“ des laufenden Mandanten.
Während dieses Feld betreten ist,
      besteht mit F6 oder der Funktion „
DBRemote-Log ansehen
“ die
      Möglichkeit, das DBRemote-Logfile des Publishers in einem Editor zu
      öffnen
Publisher-Address
Zeigt die Adresse des Publishers an.
      Ein Doppelklick öffnet, sofern es sich um das Nachrichtensystem „FILE“
      handelt, den Dateiexplorer an dieser Adresse.
Remote-User
Ein
      Mandant kann ein oder mehrere Replikations-Partner (abgebildet über die
      Remote-User des Datenbanksystems) haben. Hier finden sich Information
      dazu.
Remote-User
Name
      des Remote-Users.
Doppelklick auf den Namen öffnet ein
      weiteres Fenster mit Informationen zu der für diesen Benutzer
      eingerichteten Replikation.
Während dieses Feld betreten ist,
      besteht mit F6 oder der Funktion „
DBRemote-Log ansehen
“ die
      Möglichkeit, das DBRemote-Logfile des Remote-Users in einem Editor zu
      öffnen.
Nachrichtensystem
Zeigt das verwendete
      Nachrichtensystem. (FILE, http, usw.)
Adresse
Die
      Adresse, an die SQL Remote-Nachrichten gesendet werden sollen.
Ein
      Doppelklick öffnet, sofern es sich um das Nachrichtensystem „FILE“
      handelt, den Dateiexplorer an dieser Adresse.
Konsolidiert
Zeigt an, ob dem Benutzer
      "CONSOLIDATE"-Berechtigungen (Y) oder "REMOTE"-Berechtigungen (N) erteilt
      wurden.
Empfang
[...]


---

## Replikationsadressen Partner

Replikationsadressen Partner
Felder
Betrieb
Adressen für einkommende
      Meldungen
Kommunikationspartner
Übersicht der an diese
      Betriebsstätte angeschlossenen Partner
Betrieb
Name
Verfahren
Adresse
Sendezeitpunkt
Funktionen
Speichern
Speichert die Angaben

---

## SEPA-Besonderheiten in den Kundenbanken

SEPA-Besonderheiten in den Kundenbanken
Hauptmenü
Stammdaten
Kunden-/Lieferanten
Kundenstamm bzw. Lieferantenstamm
Direktsprung
[KU]
bzw.
[LF]
Die Pflege der Kundenbank ändert sich dergestalt, dass
es nicht mehr möglich ist bestehende Bankverbindungen zu löschen oder zu ändern,
sobald bei dieser Bankverbindung ein SEPA-Mandat hinterlegt ist. Geändert werden
kann bei Bankverbindungen mit benutztem Mandat immer noch die Sperre, das
Bis-Datum, die Soll- und Haben Obergrenzen, die Währung des Kontos sowie der
Empfänger/Zahlungspflichtige.
Weiterhin muss in den Kundenbanken das neue Feld für
die IBAN gepflegt werden. Die IBAN kann nachträglich über eine Funktion
„Generiere IBAN“ im Pfleger für Kundenbanken (Direktsprung
[KUBA]
) für alle Kundenbanken mit
eingetragener Bank und Kontonummer erzeugt werden. Diese vorgeschlagene IBAN ist
in jedem Fall zu überprüfen. Die IBAN wird ausschließlich von der kontoführenden
Bank vergeben.
Bei der Neuerfassung der Banken wird anhand der IBAN –
für Deutschland, Österreich und Belgien - sowohl Kontonummer als auch die Bank
eingetragen. Geschieht dies nicht, so weicht entweder der Aufbau der Iban ab,
sie ist falsch oder die Banken-Stammdaten sind nicht gepflegt.
Kennt man die IBAN nicht, so kann man nach wie vor
über Kontonummer und Bank die IBAN generieren lassen. Man kann in den
Steuerparametern
die IBAN-generierung
abschalten. Wird die IBAN trotz aktivem SPA nicht vorgeschlagen, so kann dies
daran liegen, dass der im Bankenstamm hinterlegte Staat nicht Deutschland,
Österreich bzw. Belgien ist oder der eingetragene ISO-Code im Staatenstamm
(Direktsprung
[
Staat
]
) nicht DE, AT bzw. BE
ist.
Diese vorgeschlagene Nummer ist in jedem Fall zu
überprüfen, da es sich hier nur um einen Vorschlag handelt. Die IBAN wird
ausschließlich von der kontoführenden Bank vergeben. Sollte es notwendig sein,
die vorgeschlagene IBAN zu ändern, da eine abweichende IBAN vom Kreditinstitut
vergeben wurde, so ist dies durchaus möglich.
[...]


---

## SEPA

SEPA
SEPA ist die Abkürzung für
Single Euro Payments
Area
- auf Deutsch „Einheitlicher Euro-Zahlungsverkehrsraum“. Ziel ist es,
den bargeldlosen Zahlungsverkehr so zu standardisieren, dass es für den
Bankkunden keinen Unterschied mehr zwischen nationalen und grenzüberschreitenden
Zahlungen gibt.
Voraussetzung für den Einzug einer SEPA-Lastschrift
ist das Vorliegen eines gültigen Mandats, das über die heute aus dem deutschen
Lastschriftverfahren bekannte Einzugsermächtigung hinausgeht. Außer der
Ermächtigung des Lastschriftgläubigers zum Einzug enthält das Mandat auch eine
Weisung zur Bezahlung an die Bank des Zahlungspflichtigen. Das Mandat muss in
Papierform oder in elektronischer Form erteilt werden und ist bei Einreichung
einer SEPA-Lastschrift im Datensatz an die zahlende Bank mit zu übermitteln.
Da bereits erteilte
Einzugsermächtigungen des Zahlungspflichtigen nicht für das
SEPA-Lastschriftverfahren gelten, muss hierzu von jedem Zahlungspflichtigen eine
neue Einzugsermächtigung  - das „Lastschriftmandat“ - eingeholt
werden.
Dies sollte zur Vermeidung von Verzögerungen rechtzeitig
vorbereitet werden, sobald die Einführung der SEPA-Lastschrift absehbar ist.
Der Lastschriftgläubiger muss dem Lastschriftschuldner
vor dem Einzug eine Information mit dem genauen Tag der Belastung zusenden.
Dieser Belastungstag ist im Einzugsverfahren einzuhalten, so dass sich der
Zahlungspflichtige bei der Kontodisposition darauf einstellen kann. Wenn ein
Zahlungspflichtiger mit dem Einzug nicht einverstanden ist, kann er
selbstverständlich auch einer SEPA-Lastschrift widersprechen.
Beim Lastschriftverfahren gibt es unterschiedliche
Verfahren: die Firmenlastschrift (für Geschäftskunden ähnlich dem
Abbuchungsauftrag) und die Basislastschrift (ähnlich der früheren
Einzugsermächtigung). Diese Parameter werden im
Mandat
hinterlegt.
Neu hinzugekommen ist eine
Gläubiger-Identifikationsnummer. Für Deutschland übernimmt die Deutsche
Bundesbank die Ausgabe der Gläubig
[...]


---

## SEPA-Mandat für Lastschriften

SEPA-Mandat für Lastschriften
Hauptmenü
Stammdatenpflege
Konstanten Kundenstamm
Kundenbanken
Direktsprung
[KUBA]
Man erreicht diesen Erfassungsschirm, indem man zuerst
die Bank im Ändern-Modus
F5
aufruft
und dort die Funktion „
Mandat verwalten
“
F5
auswählt oder
mit der Maus in die
Spalte
Mandat
klickt.
Voraussetzung für den Einzug einer SEPA-Lastschrift
ist das Vorliegen eines gültigen Mandats, das über die heute aus dem deutschen
Lastschriftverfahren bekannte Einzugsermächtigung hinausgeht. Außer der
Ermächtigung des Lastschriftgläubigers zum Einzug enthält das Mandat auch eine
Weisung zur Bezahlung an die Bank des Zahlungspflichtigen. Das Mandat muss in
Papierform oder in elektronischer Form erteilt werden und wird bei Einreichung
einer SEPA-Lastschrift im Datensatz an die zahlende Bank mit übermittelt.
Beschreibung
Mandatstyp
Es
      sind folgende Mandatstypen möglich:
•
Einzelmandat
: Dieses Mandat gilt nur für eine
      Lastschrift
•
Erstmandat
: Dies ist das erste Mandat. Erhält
      man ein neues Mandat, weil sich Bank, Kontonummer oder ähnliches geändert
      hat, so ist dies ein
•
Folgemandat
: Gibt man Folgemandat an, so öffnet
      sich eine F3-Auswahl, in der man das Vorgängermandat auswählen muss.
Mandatsunterzeichnung
Tag
      der Unterzeichnung. Er wird zur Identifizierung des Mandats mit an die
      Bank gesendet.
Sofern eine Einzugsermächtigung als
      SEPA-Basis-Lastschriftmandat genutzt wird, ist dieses Feld mit dem Datum
      der Unterrichtung des Zahlers über den Wechsel vom Einzug per
      Einzugsermächtigungslastschrift auf den Einzug per SEPA-Basislastschrift
      zu belegen. Dieses Datum muss zwischen dem
9. Juli 2012
und
      mindestens fünf Geschäftstage vor der Fälligkeit der ersten
      SEPA-Basislastschrift (als Erstlastschrift) liegen.
Mandatsreferenz
Mandatsidentifikation. Sie wird beim
      SEPA-Lastschriftverfahren mit an die Bank gesendet.
Lastschriftverfahren
Bei
      Verwendung des SEPA-V
[...]


---

## Server Setup

Server Setup
Bei einer Umstellung des Serverbetriebssystem ist es
auch notwendig, dass die zum Referenz-ERP System gehörigen Datenbanken auch dem
Umstellungsprozess unterzogen werden. Dieser Prozess wird innerhalb der
Installationsphase durchgeführt.

---

## Stammdaten Zahlungsverkehr

Stammdaten Zahlungsverkehr
Referenz-ERP bietet verschiedene Möglichkeiten, den
Zahlungsverkehr mit Kunden und Lieferanten zu automatisieren. Wenn diese
Möglichkeiten genutzt werden sollen, müssen die Stammdaten der Banken hinterlegt
werden. Weiterhin ist es erforderlich, die zulässigen Zahlungsarten, wie z.B.
Scheck, Überweisung, etc. zu bestimmen.  Hierzu sind zuvor folgende
Stammdaten zu erfassen:

---

## Stamm- und Bewegungsdaten übergeben

Stamm- und Bewegungsdaten übergeben
Um im Outlooksystem im Kontaktordner die einem
zugeordneten Kunden / Lieferanten mit ihren Bewegungsdaten sehen zu können,
müssen diese aus dem Referenz-ERP System in das Outlook System übergeben werden.
Hierzu steht folgende Routine zur Verfügung:
Mit dem Direktsprung OUTLK kann über die Funktion
"Outlook Kontakte" ein Export vorgenommen werden.
Nach F3 Auswahl des Profils kann der F9 Startknopf
angewählt werden.
Es werden alle Daten mit ihren angehängten
Bewegungsdaten eines Profils übertragen, wobei nur angefügt und überschrieben
wird, aber nicht gelöscht, so dass durch Mehrfachanwahl dieses Moduls immer
wieder Ergänzungen vorgenommen werden können.
Die Einspielroutine kann aber auch „von Hand“
gestartet werden, und zwar aus dem Bin Verzeichnis heraus mit dem Befehl :
Vbscript.exe qoutlookkontakte.vbs /dsn=<odbc
datasetname> /profil=<profilname>
Wobei der Datasetname der ODBC Verbindung angegeben
werden muss sowie der Name des im Bereich WWW angelegten Profils.

---

## SVMAIN

SVMAIN
Das AIS wird auf der SVMAIN immer nach der Eingabe des
Kunden komplett aktualisiert, die Aktualisierung des AIS in Abhängigkeit der
UFLD-Felder erfolgt per Makro und wird nur dann aufgerufen, wenn ein Wert in dem
UFLD-Feld geändert worden ist.
Des Weiteren kann das AIS nach der Eingabe einer
manuellen Adresse oder einer manuellen Versandadresse aktualisiert werden. Beim
Ändern der Werte in der allgemeinen Vorgangszuordnung wird das AIS auf der
SVMAIN Maske aktualisiert.
Aktualisierungspunkte des AIS auf der SVMAIN
Maske
Feld
Aktion
Kundennummer
Immer
Rückkehr aus der Posbar2
Immer
Unterklassenänderung
Immer
Klassenänderung
Immer
UFLD
Kann
      per Makro gesteuert werden. Es gibt aber Ausnahmen, dort wird schon im
      Standard eine Aktualisierung des kompletten AIS vorgenommen. Es existiert
      aber die Möglichkeit, die komplette Aktualisierung des AIS im Makro zu
      verhindern.
Änderung der Adresse
Das
      Aktualisieren des AIS kann per Makro gesteuert werden. Die JVAR UFLDID
      wird nicht gesetzt.
Änderung der Versandadresse
Das
      Aktualisieren des AIS kann per Makro gesteuert werden. Die JVAR UFLDID
      wird nicht gesetzt
Vorgang Zuordnung
Das
      Aktualisieren des AIS kann per Makro gesteuert werden. Die JVAR UFLDID
      wird nicht gesetzt. In der Feld ID wird die ID des Feldes
      übergeben.
Folgende JVARS werden an das Makro
Übermittelt
JAVR
Funktion
Bedeutung
UFLDID
Lesend
Mit
      dieser JAVR wird die UFLD ID des Feldes übergeben, welches geändert worden
      ist. Dieses Feld ist leer, wenn eine Aktualisierung der manuellen
      Versandadresse vorgenommen wird.
VORGANGHANDLE
Lesend
Mit
      dieser JVAR wird der Vorgangshandel des aktiven Vorgangs
      übergeben.
GLOBALREFRESH
Schreibend
Diese JAVR kann aus dem Makro
      gesetzt werden, damit die Globale AIS Aktualisierung ausgeschaltet werden
      kann, wenn das UFLD-Feld den Wert „Update Mask“ auf ja stehen hat. Im
      Standard steht der Wer
[...]


---

## Tabelle zur Version: 9.0.2401.3

Tabelle zur Version: 9.0.2401.3
ID
Releasenote - Titel
Geprüft
34899
Nach Kunden-indiv. Artikelnummer verbessert und auf den
      aktuellen Kunden begrenzt
35170
X-Rechnung Ansprechpartner
35171
X-Rechnung Zahlungsweg
35275
Baustellenartikellogik in den Itemboxen und somit für
      jeden privatisierbar
35280
Abstürze bei Vorgangskopie beseitigt
35189
Kopie von VorgangAddOns

---

## Tabelle zur Version: 9.0.2501.6

Tabelle zur Version: 9.0.2501.6
ID
Releasenote - Titel
Geprüft
37151
Auswahlliste 2.0, Abbruch des Ladevorgangs
37321
Auswahlliste 2.0 Filterzeile
37138
Anzeige von erfassten Permanenten Inventur
Belege
37122
Zertifikatsübersicht: Archivanzeige in
      Nachhaltigkeitskundenübersicht
37117
Tourauswahl in der Vorgangserfassung

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

## Umfang der bereitgestellten Daten

Umfang der bereitgestellten Daten
Von der mitgelieferten Ladeprozedur
HoleIndividuellePreiseArtikel
werden nachfolgende Daten
bereitgestellt:
Tabellenspalte
Prozedurfeld
Feldtyp
Beschreibung
Kundennummer
KundNummer
integer
Nummer des Kunden
Kunde
KundBezeich
char(40)
Bezeichnung des Kunden
Kundentyp
KundTyp
integer
Kundentyp: Kunde oder
      Lieferant
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
Preis
ArtiIndPreis
numeric(15,4)
Preis zum im Spaltenkopf angegebenen
      Datum
ME-Nr. Menge
MENummerAbMenge
integer
Mengeneinheitsnummer und Bezeichnung
      der ab-Menge. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein.
ME-Bezeichnung
MENumAbMenBez
char(40)
Bezeichnung der
      ab-Menge.
ME-Nr. Preis
MENummer
integer
Mengeneinheitsnummer und Bezeichnung
      der pro-Menge. Muss für alle Einträge mit dem gleichen Gültig-Ab Datum
      identisch sein.
ME-Bezeichnung
MEBezeichnung
char(40)
Bezeichnung der
      pro-Menge.
Brutto-Kennzeichen
ArtiIndKennzBru
integer
F3
      Auswahl Ja/Nein. Es handelt sich um einen Bruttopreis. Das Feld kann nur
      für den ersten Eintrag eines Preiszeitraums – gekennzeichnet durch „ab
      Menge“ 0,00 – geändert werden. Es wird dann für den gesamten Zeitraum
      geändert.
Steuergruppe
ArtiIndSteuerGruppe
integer
Insofern das Brutto-Kennzeichen auf
      Nein gesetzt wurde, also ein N
[...]


---

## Umschlüsselung von Kundennummern

Umschlüsselung von Kundennummern
Man kann hierzu die Funktionalität der
Tankkartenverwaltung einsetzen.

---

## Unterkonten

Unterkonten
Wird im Kundenstamm ein Eintrag zur
Mitgliederzuordnung herangezogen, so kann an dieser Stelle entschieden werden,
ob es sich um ein Unterkonto zu einem schon existierenden Mitgliedskonto
handelt, oder nicht. In der Mitgliedsübersicht werden nur die Oberkonten
angezeigt.
Wird ein zugeordnetes Unterkonto noch einmal zur
Zuordnung herangezogen, so kann die Unter/Oberkontozuordnung mit der F7 Funktion
wieder aufgelöst werden.

---

## Vererbt aus Liste 1 bis 4

Vererbt aus Liste 1 bis 4
Vererbungen der Preise kann auf Basis eine
Vorlagenliste eingestellt werden, hierzu wird z.B. die Liste 0 mit alle Artikel
gepflegt, um dann in den kundenindividuellen Listen nur noch die Vererbung
anzuschalten. Sind in diesem Feld Punkt ...... eingetragen, so bedeutet dieses,
dass keine Vererbung vorliegt, eine 0 in diesem Feld bedeutet, die Preise werden
aus Liste 0 vererbt, usw. ... Ist versehentlich eine Vererbungs-Liste
eingetragen, so kann diese mit der Taste STRG ENTF wieder entfernt
werden.

---

## Verfahrensweise bei Datenbank-Updates

Verfahrensweise bei Datenbank-Updates
Bei einem Datenbank-Update auf einer Kundendatenbank
müssen alle mit ScriptSystem=0 und außerdem alle mit ScriptBesitzer=1
gekennzeichneten Datensätze erhalten bleiben.
Alle Datensätze beider Relationen mit ScriptSystem=1
werden (unter Direktsprung AMICR eingerichtet) gelöscht und neu eingespielt.
In Zukunft soll ein Foreign Key die Relationen
verbinden: Wegen des Foreign Keys müssen dann zuerst die Datensätze der Relation
ScriptParamPar gelöscht, bzw. zuerst die Datensätze der Relation ScripParam
eingespielt werden.
Die Datensätze deren ScriptSystem-Flag nicht gesetzt
ist, werden
nicht
automatisch bei allen Kunden eingerichtet.
Mögliche Problemquellen:
Derzeit kann nicht verhindert werden, dass Detailsätze
mit ScriptSystem=1 eingespielt werden, deren Kopfsatz mit ScriptSystem=0 nicht
auf der Kundendatenbank existiert.
Wichtiger Hinweis
Bis Aeins-Version 4.2.2.181 (22.6.99) werden inaktive
ScriptParameter nicht zuverlässig erkannt. Daher kann es erforderlich sein, nach
Beendigung der Parametrisierungen das SQL-Skript WAAGKORR.SQL aufzurufen. Besser
ist es, vorläufig keine Parameter als inaktiv zu markieren. Das SQL-Skript hat
folgenden Inhalt:
delete from ScriptParamPar WHERE
ScriptPId='WaagenImport' and ScriptPPAktiv=0;
commit;

---

## Vertretergruppe

Vertretergruppe
Konnte der Kunde korrekt ermittelt werden, wird die
Vertretergruppe eingelesen. Schlägt dies fehl, wird die Vertretergruppe aus dem
Kundenstamm verwendet. Ein Fehler an dieser Stelle bewirkt einen Eintrag im
Fehlerprotokoll (und die Abweisung des Importes dieses Datensatzes): DBFehler b.
Verteter-Ermittl. f. KundNr [...], Datei [...], Übern. #..., Zl. #...
(Zugehörige Positionsparameter: VG_SAx)

---

## VKUI

VKUI
Analog zum Kundeninformationssystem kann auch für
einen Vorgang ein Stammblatt angelegt werden. Hier erfolgt die Anzeige und ggf.
Eingabe von Werten.

---

## Voraussetzungen Automation

Voraussetzungen Automation
Das Prozesskontrollsystem arbeitet nur im Referenz-ERP
Umfeld, und es läuft nur auf  einem Windows NT Rechner mit dem
Betriebssystem 4.0 (SP6a) plus dem Windows Scripting Host 5.6 oder einem Windows
2000 oder Windows XP Rechner.
Zusätzlich zu dem Referenz-ERP System müssen noch zwei
selbstregistrierende Objekte im System eingetragen werden, die wie folgt
aktiviert werden:
Das „\aeins\bin\Branchen-ERP.ocx“ Objekt muss mit dem Kommando
regsvr32
Branchen-ERP.ocx
im „\aeins\bin“ Verzeichnis in die
Registrierdatenbank eingefügt werden
Weiterhin muss die Datei FileCompare.wsc aus dem Bin
Verzeichnis mit dem Kontextmenü des Explorers (Rechte Maustaste auf dieser
Datei) registriert werden.

---

## Vordefinierte Gruppen mehrfach verwenden

Vordefinierte Gruppen mehrfach verwenden
Man kann sich vorstellen, dass man für bestimmte
Informationen eine Gruppe definiert, die man mehrfach verwenden möchte. Z.B.
Baut man sich für die Anzeige eines Kunden ein Bereich, der die Anschrift in
einer bestimmten Form enthält. Um nicht für jede AIS-Gruppe, die die
Kundenanschrift enthalten soll, diese Einrichtung kopieren zu müssen, kann man
einfach in der neuen Gruppe auf diese verweisen. Dazu dient der Feldtyp
„
Gruppe
“. In Gruppe A sagt man also „zeige mir auch Gruppe B“. Dieser
Feldtyp kann beliebig oft verwendet werden.
Der Vorteil, dass man dann z.B. für die Anschrift nur
eine Gruppe pflegen muss, muss hier bestimmt nicht extra erwähnt werden.

---

## Vorgangs-Erfassungsparameter

Vorgangs-Erfassungsparameter
Mit Erfassungsparametern wird der Ablauf der
Vorgangserfassung ganz wesentlich beeinflusst. Die Erfassungsparameter im
Vorgangskopf haben
folgende Bedeutung:
Versandart
Vorbelegung der Versandart, wenn aus dem Kundenstamm 0
geliefert wird.
Sofortdruck Abfrage und Vorbelegung
Hier wird festgelegt, ob nach der Vorgangserfassung
die Abfrage nach dem sofor­tigen Druck erfolgen soll und wie sie vorbelegt
ist.
Druck korrekt Abfrage bei Sofortdruck
Einstellmöglichkeit, ob diese Frage beim Sofortdruck
erfolgen soll.
Korrekt Abfrage und Vorbelegung
Hier wird festgelegt, ob nach der Vorgangserfassung
die Abfrage nach der korrekten Erfassung erfolgen soll und wie sie vorbelegt
ist.
Mehrbelegerfassung
Bei “Ja” verbleibt Referenz-ERP nach erfolgter
Belegerfassung im Erfassungsmodus,
Versandadresse immer manuell auswählen
Bei “Ja” wird die automatische
Versandadressenbestimmung ausgeschaltet.
Umwandelsperre abfragen
Bei “Ja” ist keine Wandlung möglich.
Im Barverkauf sofort in Positionsteil
Bei “Ja” wird der Kopfteil übersprungen.
Leerbeleg in Datenbank speichern
Bei „Ja“ wird ein Beleg ohne Positionen
gespeichert.
Neue Feldpositionierung
Dieser EPA wird zurzeit noch nicht berücksichtig.
Wochentagsformat
Hier kann das Format des Wochentags eingestellt
werden, das neben dem Datum angezeigt wird.

---

## Vorgangskopf-ID einrichten

Vorgangskopf-ID einrichten
Beleg-Nummer über
[NKS]
Periode / Jahr = WJ /Periode WaWi muss eröffnet
sein
Belegdatum: es wird das Tagesdatum vorgeschlagen
Kundennummer direkte Eingabe oder Auswahl mit F3

---

## Vorgang Speichern

Vorgang Speichern
Die Funktion oder der zugehörige Knopf erlaubt ein
Speichern der gerade eingegebenen Informationen unter dem zuletzt angewählten
Kunden und der zuletzt angewählten Vorgangsklasse. Die Unterklasse wird über den
EPA Standardunterklasse bestimmt, die Belegnummer wird anhand des zugeordneten
Nummernkreises bestimmt, das unter DAT zugeordnete Datum (normalerweise das
Tagesdatum) bestimmt das Datum des Beleges.

---

## Vorgänge mit dem Vorgangshelper bearbeiten

Vorgänge mit dem
Vorgangshelper
bearbeiten
Das Grundgerüst des Vorgangshelper sieht wie folgt
aus
aeins.jpp_new(hdl,
"CVorgangsHelper")
aeins.jpp_in hdl , "KundNummer",
ZielKundenNummer
aeins.jpp_in hdl , "Klasse",
ZielKlassennummer
aeins.jpp_in hdl , "Unterklasse",
ZielunterKlassennummer
aeins.jpp_in hdl , "NumNummer",
ZielNumNummer
aeins.jpp_ex (hdl,
"StartVorgang")
tu was ….
aeins.jpp_in hdl , "Speichern",
"1"
aeins.jpp_ex hdl,
"BeendeVorgang"
aeins.jpp_delete
hdl
Es wird ein neues Objekt vom Typ “ CVorgangsHelper“
instanziiert, vier IN-Parameter an das Objekt übergeben und der Vorgang
gestartet. Mit „tu was …“ wird der Vorgang bearbeitet. Anschließend wird der
Vorgang gespeichert und beendet (also die Veränderungen übernommen) und das
Handle freigegeben.

---

## Vorraussetzungen zum Prozessaufruf

Vorraussetzungen zum Prozessaufruf
Das Prozesskontrollsystem arbeitet nur im Aeins
Umfeld, und es läuft nur auf einem Windows NT Rechner mit dem Betriebssystem 4.0
(SP6a) plus dem Windows Scripting Host 5.6 oder einem Windows 2000 oder Windows
XP Rechner.
Zusätzlich zu dem Aeins System müssen noch zwei
selbstregistrierende Objekte im System eingetragen werden, die wie folgt
aktiviert werden:
Das \aeins\bin\Branchen-ERP.ocx Objekt muss mit dem Kommando
regsvr32 Branchen-ERP.ocx
im \aeins\bin Verzeichniss in die Registrierdatenbank
eingefügt werden
Weiterhin muss die Datei FileCompare.wsc aus dem Bin
Verzeichnis mit dem Kontextmenü des Explorers (Rechte Maustaste auf dieser
Datei) registriert werden.
Jetzt kann aus der Kommandobox im Windows Verzeichnis
herraus der Prozessüberwachungsmonitor gestartet werden und zwar mit dem
Befehl
webaccess.wsf /process=<prozessname>
/idleloops=<wartezyklen> /wait=<anfangswartesekunden>
/forever=<0|1> /sleeptime=<schlaf_sekunden>
ACHTUNG:
die
Leerzeichen zwischen den Parametern sind zwingend vorgeschrieben!

---

## Weitere Features

Weitere Features
Nach Markieren einer Zeile kann über Direktsprung
[LIB], [REB] etc. in die betreffende Vorgangsliste gesprungen werden, wobei der
neue Beleg vorselektiert ist. (An nachfolgende Auswahllisten wird die
Kundennummer und die Belegnummer übergeben, so kann mit automatischer
Vorselektion in jede Auswahlliste gesprungen werden, die eine der beiden
Vorbelegungen akzeptiert, also z.B. auch Kundenlisten, OP-Listen etc).
Belegerzeugung aus importierten Vorgangsdaten
Die Daten aus einem Datenträger werden in 2 Relationen
abgelegt: Rohwarenbelege erscheinen in der Relation RohwareHauptsatz_Waage und
können über die Direktsprünge [RWWE] und [RWWV] angesehen und weiterverarbeitet
werden.
Belege aus der Faktura, Umbuchungen und
Produktionsbelege erscheinen in der Relation VorgangUebergabe und können über
den Direktsprung [VUEB] angesehen und weiterverarbeitet werden.
Die Funktionen in der Option-Box dieser Auswahlliste
sind weitgehend dieselben wie in den Anwendungen [RWWE] und [RWWV]. D. h. die
Funktionen heißen zwar anders, haben aber denselben Inhalt und werden ohne
Rohwaren-Steuerparameter aufgerufen.
Im einzelnen sind folgende Funktionen bis auf den SPA
identisch:
CEREA_WAAGE_Import
(mit SPA)
=          Vorgang_Import

(ohne SPA)
CEREA_WAAGE_Rueck4
(mit SPA)
=
Vorgang_Import_Rueck4
(ohne SPA)
CEREA_WAAGE_Rueck2
(mit SPA)
=
Vorgang_Import_Rueck2
(ohne SPA)

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

## Weitere Parameter

Weitere Parameter
In vielen Anwendungen ist mit der Erfassung des Kunden
die Kopfinformation abge­schlossen und es kann in die Erfassung der
Artikelpositionen gewechselt werden.
Referenz-ERP bietet jedoch zahlreiche weitere
Erfassungsmöglichkeiten an, die nachfolgend beschrieben werden.
Zusatzangaben
Unterhalb des Feldes Kundennummer werden wichtige
Steuerungsinformationen angezeigt und abgefragt, wie z.B. Vertreter, Versandart,
Lieferanschrift. Hier stellen die Vorgangsklassen unterschiedliche
Anforderungen.
Die konkrete Einstellung dieser Felder wird im
Programmteil Individualfeldgruppen
[UFLD]
vorgenommen.

---

## Wichtige Tabellen des Kassensystems

Wichtige Tabellen des Kassensystems
Tabelle
Beschreibung
Schlüssel
AcashBelg
Kassenbelege
BelegKs (Kassennummer)
BelegId (interne
      Belegidentifikation)
FilialNummer (Betriebsstättennummer
      Erzeuger)
Bei
      Barverkäufen ist der Kassenbeleg über BelegId und V_Id mit einem Vorgang
      verknüpft.
AcashBelgZhlg
Zahlungssätze zu Kassenbelegen. Zu
      einem Kassenbeleg kann es mehrere Zahlungssätze geben.
ZahlKs (Kassennummer)
ZahlBelegId (interne
      Belegidentifikation)
FilialNummer (Betriebsstättennummer
      Erzeuger)
ZahlNummer (fortlaufende
      Nummer)
Verknüpfung mit AcashBeleg über
      BelegKs=ZahlKs und BelegId=ZahlBelegId und die Filialnummern.
AcashBelgZami
Zahlungsmittel bei unbarer
      Zahlung
ZamiIdNr (interne
      Identifikation)
Verknüpfung über
      AcashBelgZhl.ZahlZamiIdNr
AcashBelgKsiz
Kassenbericht. Die Tabelle enthält
      zusammenfassende Information über einzelne Sitzungen.
KsiKsNr (Kassennummer)
KsiASK (sitzungsnummer)
FilialNummer (Betriebsstättennummer
      Erzeuger)
AcashFibuLink
Beschreibt die Verbindungen von
      Kassenbelegen zur Fibu
BelegKs (Kassennummer)
BelegId (interne
      Belegidentifikation)
FilialNummer (Betriebsstättennummer
      Erzeuger)
FibuV_Id (Ident. Des zugeh.
      Fibu-Vorgangs)

---

## Wiedervorlage bei Kunden

Wiedervorlage bei Kunden
Aus den Auswahllisten Kunden, Lieferanten und
Kontokorrentkunden ist die Funktion
Wiedervorlage
verfügbar. Mit Hilfe dieser
Funktion kann man sich für den markierten Kunden eine Wiedervorlage
eintragen.
Es gibt zwei verschiedene Möglichkeiten für die
Wiedervorlage:
Die Funktion
Wiedervorlage
macht einen Eintrag in die
Wiedervorlage der Datenbank der dann über den Direktsprung
[WIEDV]
angesehen werden kann. Außerdem
erhält man beim Start von Referenz-ERP eine Mitteilung im Hauptmenü unter
Systemmeldungen, wenn für den Tag Wiedervorlagen vorhanden sind.
Die Funktion
Wiedervorlage Outlook
macht einen Eintrag
im Kalender von Microsoft Outlook des jeweiligen Bedieners. Es gibt die
Möglichkeit die Uhrzeit für den Termin festzulegen und sich erinnern zu
lassen.
Felder
Notiz
Hier
      trägt man sich einen Text ein, damit man weiß was bei Wiedervorlage zu tun
      ist.
Wiedervorlage
Hier
      kann man ein Häkchen setzen, wenn man eine Wiedervorlage mit genaueren
      Angaben wünscht.
Nur wenn das Häkchen gesetzt ist sind die folgenden
      Felder auf der Maske sichtbar und verwendbar.
Ist das Häkchen nicht
      gesetzt wird beim Verwenden der Wiedervorlage-Funktionen ein Eintrag mit
      den Standardwerten Tagesdatum und 00:00 Uhr gemacht.
Datum
Hier
      trägt man das Datum für die Wiedervorlage ein. Das Feld ist mit dem
      aktuellen Tagesdatum vorbelegt. Mit
F3
kann man ein anderes Datum aus dem
      Kalender auswählen.
Uhrzeit (HH:MM)
Hier
      trägt man die Uhrzeit für die Wiedervorlage im Format HH:MM
      ein.
Erinnerung vorher
Mit
      dem Häkchen wählt man aus, ob man eine Erinnerung möchte. Hat man das
      Häkchen gesetzt ist ein Feld sichtbar in dem man eintragen kann wann (wie
      viele Stunden/Minuten vorher) man an den Termin erinnert werden möchte.
      Das Format für dieses Feld ist HH:MM
Termin /
Aufgabe
Hier
      wählt man die Art der Wiedervorlage aus. Termin ist vorbelegt

---

## Zahlungsart

Zahlu
ngsart
Hauptmenü
Mahn-, Zahl-, Zinswesen
Stammdaten
Zahlungsarten
Direktsprung
[FIZAH]
.
Die Zahlungsart ist ein im Kunden- und
Lieferantenstamm eingetragenes Kennzeichen, über das gesteuert wird, wie die
Zahlung im automatischen Zahlungsverkehr bei Ein- und Ausgang erfolgen soll.
Beschreibung
Nummer
Eindeutige Nummer der Zahlungsart,
      wie sie später im Kunden/Lieferantenstamm hinterlegt wird. Die nächste
      freie Nummer wird vorgeschlagen.
Formularklasse
Wahlweise „Zahlungseingang“ oder
      „Zahlungsausgang“. Eine Auswahl mit
F3
ist
      möglich.
Beim
      Wechseln der Formularklasse wird im Feld eRechnung Zahlungsweg der
      sinnvollste eRechnungs-Zahlungsweg neu vorbelegt.
Bezeichnung
Bezeichnung der Zahlungsart zur
      einfacheren Identifikation in Auswahllisten oder F3-Auswahlen.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Skontierbar
Hier
      kann der Skontotyp eingetragen werden. Eine Auswahl mit
F3
ist
      möglich
•
immer
      Skonto
: Skonto wir
      unabhängig vom Skontodatum immer gewährt/gezogen
•
nie Skonto:
Selbst,
wenn
      im Beleg Skonto vorgesehen ist und die Skontofrist noch nicht abgelaufen
      ist, wird kein Skonto gewährt.
•
Abzug gem.
      Datum
: Dies ist die
      Vorbelegung. Skonto wird dann gewährt, wenn die Frist noch nicht
      abgelaufen ist.
Skontierbar bei
      Verrechnung
Werden Rechnungen mit Gutschriften
      verrechnet, so kann es wünschenswert sein, bei den Gutschriften Skonto
      anders zu behandeln. Ist hier kein Wert eingetragen, so wird bei
      Gutschriften der Wert, der bei „Skontierbar“ eingetragen ist,
      verwendet.
DTA-Typ
Zahlungsart bei Zahlung per
      Datenträgeraustausch. Der DTA-Typ wird nur bei der Formularklasse
      „Zahlungseingang“ abgefragt bzw. im Datenträgeraustausch verwendet. Bei
      Zahlungsausgang
[...]


---

## Zinsgruppen

Zinsgruppen
Hauptmenü
Mahn-/Zahl-/Zinswesen
Stammdaten
Zinsgruppen
Direktsprung
[ZIG]
Im Pfleger für Zinsgruppen lassen sich alle weiteren
Einstellungen für die Zinsabrechnung vornehmen.
Beschreibung
Zinsgruppe
Nummer der Zinsgruppe, wie sie dann
      im Kundenstamm, im Mahnstamm oder in den Wechselkosten hinterlegt wird.
      Die Zinsgruppe 0 bedeutet immer, dass keine Zinsrechnung vorgenommen
      werden soll. Es ist also nicht nötig hier etwas einzutragen.
Bezeichnung
Text
      zur Identifikation der Zinsgruppe.
Ist
      der Steuerungsparameter 34 "Mehrsprachigkeit aktiv“ in Referenz-ERP gesetzt, so
      hat man auf diesem Feld die Möglichkeit mit F3
sprachabhängige Bezeichnungen
zu pflegen.
Ertragskonto
GuV
      Konto, auf das vom automatischen Buchungsmodul die Sollzinsen gebucht
      werden.
Aufwandskonto
GuV-Konto, auf das vom automatischen
      Buchungsmodul die Habenzinsen gebucht werden.
Ertragskonto Gutschrift/
      Aufwandskonto Gutschrift
In
      der Praxis kann es vorkommen, dass für Kunden Zinsen individuell angepasst
      werden müssen. Dafür existiert das Modul „Individuelle
      Zinsgutschrift“.  Hier werden zu einer Zinsabrechnung Gutschriften
      erstellt. Dabei wird das hier angegebene Konto anstelle des Ertrags- bzw.
      Aufwandskontos verwendet.
Kostenstelle
      Soll/Haben
Die
      beim Zinsertrag bzw. Zinsaufwand verwendete
Kostenstelle
.
Kostenträger
      Soll/Haben
Der
      beim Zinsertrag bzw. Zinsaufwand verwendete
Kostenträger
.
Kostenobjekt Soll/Haben
Das
      beim Zinsertrag bzw. Zinsaufwand verwendete
Kostenobjekt
.
Steuerschlüssel
Steuerschlüssel, der bei den
      automatischen Buchungen verwendet werden soll.
Gesamtsaldo
      verbuchen
Ist
      hier ein Haken gesetzt, wird der Saldo aus Soll und Habenzinsen gebildet
      und es entsteht beim Kunden nur ein Buchungssatz. Die Bagatellzinsen
      wirken sich dann erst auf den Saldo aus. Ansonsten entstehen zwei
      getrennte Belege.
Zi
[...]


---

## Zinsmerkmale im Kundenstamm

Zinsmerkmale
im Kundenstamm
Hauptmenü
Stammdatenpflege
Kunden / Lieferanten
Kundenstamm / Lieferantenstamm /
Kontokorrent-Kunden
Direktsprung
[KU] / [LF] / [KUKO]
Im Pfleger für Personenkonten
(Lieferantenstamm/Kundenstamm) lassen sich unter
Fibumerkmale
F11
die kundenspezifischen Merkmale hinterlegen.
Beschreibung
Zinssperre
Steht dieses Feld auf nein, werden
      für diesen Kunden keine Zinsen berechnet.
Zinsgruppe
Hier
      wird die Nummer der Zinsgruppe hinterlegt, die steuert wie die Zinsen
      berechnet werden. Ist hier eine 0 hinterlegt, werden keine Zinsen
      berechnet, da 0 keine gültige Zinsgruppe ist.
Man
      kann per Einrichterparameter einstellen, dass beim Setzen der Zinsgruppe
      geprüft wird, ob bereits Belege, die Verzinst werden müssen, existieren.
      Es wird dann eine Meldung auf dem Bildschirm ausgegeben. Zusätzlich
      erfolgt ein Eintrag ins Fehlerprotokoll.
Zinsen berechnen ab
Es
      gibt diverse Gründe, warum für einen Kunden erst ab einem bestimmten Datum
      Zinsen berechnet werden sollen (z.B. Kunde wurde aus Fremdsystem
      importiert und soll erst ab Datum nn.nn.nnnn in Referenz-ERP mit Zinsen belastet
      werden oder es ist erst zum nn.nn.nnnn Verzinsung mit dem Kunden
      vereinbart worden). Ist hier ein Datum eingetragen, wird zu allen Belegen
      die vor diesem Datum fällig sind, der Zinssaldo ermittelt und auf diesem
      setzt dann die Zinsabrechnung auf. Ist einmal eine Zinsabrechnung erstellt
      worden, ist dieses Datum nicht mehr änderbar.
Zinsperiode
Dieses Feld wird bisher nicht von
      Referenz-ERP ausgewertet und ist für zukünftige Entwicklungen
      vorgesehen.
Bagatellzinsen
Wenn
      man Zinsen bis zu einer gewissen Höhe dem Kunden nicht
      belasten/gutschreiben will, so kann man hier den Wert dafür eintragen. Es
      werden dann für diesen Kunden/Lieferanten trotzdem die Zinsen berechnet
      und er erscheint auch in der Zinsabrechnung. Diese berechneten Zinsen

[...]


---

## Zusatzinformationen zu eine Kontaktkarte

Zusatzinformationen zu eine Kontaktkarte
Soll nun auf einem Kontaktkarte noch zusätzlich eine
Information über die letzten Besuche, oder eine Information über die Rechnungen
zu sehen sein, so kann dieses per Zusatzprofil eingerichtet werden.
Die Verbindung zwischen Hauptsatz und Anhang erfolg
über den Profilnamen, der Hauptprofilname lautet in dem obigen Beispiel KUNDEN,
zu Zusatzprofile sind gekennzeichnet durch KUNDEN_1 bis KUNDEN_4. Es gilt die
Regel, dass der Hauptname von einem Unterstreichung Strich gefolgt werden muss,
und danach eine Zahl angegeben werden muss. Die Zahl ist lückenlos
durchzunummerieren.
Der erste Unterdatensatz sieht dann wie folgt aus
:
Wichtig ist hierbei, dass die Wartezeit auf 2 gestellt
wird, und dass die Sperre auf Ja steht.
Tabreiter 2 steuert die Überschrift zu diesem
Unterbereich, Tabreiter 3 ist komplett freizulassen und Tabreiter 4 Steuert das
SQL Statement.
Wichtig ist hierbei, das das .Ergebnisfeld IMMER Notiz
heisst.
In der Where Bedingung ist nun die Verknüpfung zu dem
Hauptdatensatz anzugeben, in diesem alle über die KundId, die in Spitz Klammern
einzuschließen ist.
Im folgenden Beispiel wird über die Kundennummer der
Offene Posten referenziert :
Das Ergebnis sieht dann wie folgt aus :
In dem Notizblock des Kontaktordners sind alle Daten
hintereinander eingetragen.

---

