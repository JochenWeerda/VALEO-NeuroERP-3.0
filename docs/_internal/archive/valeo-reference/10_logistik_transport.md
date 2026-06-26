# Logistik, Transport & Versand — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (110 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Belegmailversand wiederholen

Belegmailversand wiederholen
In der Vorgangsbearbeitung wurde die Möglichkeit
geschaffen, bereits versendete Ware-Belege nochmal und gegebenenfalls mit
alternativer Empfänger-Email zu versenden. Dazu wird das bereits versendete
Element aus dem Archiv herangezogen.  Die Funktion Belegversand wiederholen
wurde entfernt. Diese hatte den Druck neu angestoßen und so einen Neuversand
erzeugt.
Releasenote Kategorie:
Ticket: 714727[32865]
Version: 8.3.2210.20
Datum: 20.10.2022
Anwendung: AGB, AUB, BAB, BSB, DAB, EGB, ELB, ERB,
GUB, LIB, REB, LAB, ELAB
Variante: --
Funktion/Report: Beleg erneut versenden
Weitere
Informationen
Tags:
Releasenote, 8.3.2210.20, 32865, 714727

---

## Währungskurs-Abruf

Währungskurs-Abruf
Die Umstellung der Transportverschlüsselung beim Abruf
von Währungskursen machte unter Umständen Probleme.  Dies wurde
behoben.
Releasenote Kategorie:
Ticket: 715321[32969]
Version: 8.3.2211.9
Datum: 09.11.2022
Anwendung: Währungskurse
Variante: Standard
Funktion/Report: Währungskurse abrufen
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.9, 32969, 715321

---

## Teildisposition: Button an Berechtigung angepasst

Teildisposition: Button an Berechtigung angepasst
In der Vorgangsbearbeitung wird bei Verwendung der
Standard-Teildisposition der OK-Button auf der Maske bei fehlenden Rechten
ausgeblendet.
Releasenote Kategorie:
Ticket: 719006[33327]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: -
Variante: -
Funktion/Report: Teildisposition
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33327, 719006

---

## Frachttabellenzuordnung Felderweiterung

Frachttabellenzuordnung Felderweiterung
In der Frachttabellenzuordnung ist das Feld
"Frachtgruppe AR" dahingehend erweitert worden, dass auch Werte > 32.768
eingegeben werden können.
Releasenote Kategorie:
Ticket: 722181[33343]
Version: 8.3.2302.17
Datum: 17.02.2023
Anwendung: Frachtzuordnung
Variante: Frachttabellen
Funktion/Report: Ändern >>
Fachttabellenzuordnung
Weitere
Informationen
Tags:
Releasenote, 8.3.2302.17, 33343, 722181

---

## Mailversand: Dateizuordnung von Mail-Anhängen

Mailversand: Dateizuordnung von Mail-Anhängen
Es kam vor, dass E-Mail Anhänge nicht korrekt erkannt
wurden. Die Erkennung des Dateityps wurde jetzt überarbeitet.
Releasenote Kategorie:
Ticket: 719172[33719]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: Mail
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33719, 719172

---

## Vermailung: Gelöschte Versandprofile

Vermailung: Gelöschte Versandprofile
In der Anwendung [MAIL] kann eine E-Mail erneut
versendet werden. Wenn nun ein Versandprofil gelöscht wurde, konnten keine
Emails mehr über dieses Profil erneut versendet werden. Stattdessen wird man
beim Aufruf einer solchen Mail nun darauf hingewiesen und man kann ein
vorhandenes Profil auswählen.
Releasenote Kategorie:
Ticket: 719644[34062]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Vermailung [MAIL]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34062, 719644

---

## Lange Passwörter im Versandprofilstamm

Lange Passwörter im Versandprofilstamm
Im Versandprofilstamm [VPST] konnten längere
Passwörter nicht gespeichert werden. Dies wurde behoben.
Releasenote Kategorie:
Ticket: 725795[34156]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: Versandprofilstamm [VPST]
Variante: verpostungstamm
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34156, 725795

---

## Mailversand Finanzbuchhaltung: Anzeige von Grafiken

Mailversand Finanzbuchhaltung: Anzeige von Grafiken
Beim Mailversand einer Avise, Mahnung oder
Zinsabrechnung wird die im Formular über HTML eingebundene Grafik in der Mail
wieder angezeigt. Die Grafik wurde bisher beim Versandtyp "Vermailung" nicht
berücksichtigt.
Releasenote Kategorie:
Ticket: 727271[34278]
Version: 8.3.2310.27
Datum: 27.10.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2310.27, 34278, 727271

---

## Mailversand

Mailversand
In der Version 8.3.2310.27 und 9.0.2305.2 konnte es
dazu kommen, dass der Mailversand nicht ordnungsgemäß durchgeführt wurde. Dieses
Problem wurde jetzt behoben.
Releasenote Kategorie:
Ticket: 728666[34499]
Version: 8.3.2311.10
Datum: 10.11.2023
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2311.10, 34499, 728666

---

## Postleitzahlen auf 11 Stellen erweitert

Postleitzahlen auf 11 Stellen erweitert
Die Stellenanzahl bei Postleitzahlen (PLZ) wurden
auf 11 Stellen erweitert. Sie kann aus Zahlen, Buchstaben und Sonderzeichen
bestehen und angezeigt werden. Diese Änderungen betreffen unter anderem den
Bankenstamm, den Anschriftstamm, Versandanschriften, Ansprechpartner sowie den
Kundenstamm.
Releasenote Kategorie:
Ticket: 730594[34716]
Version: 9.0.2401.1
Datum: 28.03.2024
Anwendung: Anschriften
Variante: Anschriften
Funktion/Report: Neuanlage (F8), Ändern (F5)
Weitere Informationen
Tags:
Releasenote, 9.0.2401.1, 34716, 730594

---

## Versandprofilstamm Speicherproblem beseitigt

Versandprofilstamm Speicherproblem beseitigt
In der Bearbeitungsmaske des Versandprofilstamms
[VPST] wurde der Button "Sendeeinstellungen testen" entfernt. Zudem wurden
Probleme beim Speichern behoben.
Releasenote Kategorie:
Ticket: 731528[34788]
Version: 9.0.2401.2
Datum: 24.05.2024
Anwendung: Versandprofilstamm [VPST]
Variante: Verpostungstamm
Funktion/Report: Ändern
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.2, 34788, 731528

---

## Archiveintrag für HTMLBody im Belegversand nicht mehr zwingend

Archiveintrag für HTMLBody im Belegversand nicht mehr zwingend
Bei der Verwendung einer HTML-Body-Funktion im
Belegversand ist die Angabe eines Formulararchiveintrags als Basis Veränderung
zu einem HTML-Body nicht mehr zwingend notwendig. Das HTML kann auch vollständig
in der Body-Funktion entstehen.
Releasenote Kategorie:
Ticket: 735345[34908]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: Formularzuordnung
Variante: Standard
Funktion/Report: Belegversand
Weitere Informationen
Tags:
Releasenote, 9.0.2402.1, 34908, 735345

---

## Es werden Frachtenzeilen korrekt aktualisiert und keine weiteren Frachtzeilen auf der Belegpositionsmaske

Es werden Frachtenzeilen korrekt aktualisiert und keine weiteren
Frachtzeilen auf der Belegpositionsmaske
Bei Nutzung von individuellen Frachten, konnte es
vorkommen, dass für jede neue Warenposition eine eigene Frachtzeile erstellt
wurde, anstatt korrekterweise die vorhandene Frachtenzeile zu aktualisieren um
die neue Warenposition. Dieser Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 735264[35352]
Version: 9.0.2401.4
Datum:
Anwendung: Alle Belegerzeugungsanwendungen
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.4, 35352, 735264

---

## Avise Mailversand

Avise Mailversand
Bei Mailversand der Avise wurde der Mailbody und die
Betreffzeile bisher über ein Formular bestimmt. Jetzt ist es alternativ möglich
diese über eine Datenbankfunktion zu bestimmen.
Releasenote Kategorie:
Ticket: 735345[35377]
Version: 9.0.2501.5
Datum:
Anwendung: FIZAH,ZHB
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35377, 735345

---

## Mailversand mahnwesen

Mailversand mahnwesen
Beim Mailversand im Mahnwesen wurde der Mailbody und
die Betreffzeile bisher über ein Formular bestimmt. Jetzt ist es alternativ
möglich diese über eine Datenbankfunktion zu bestimmen.
Releasenote Kategorie:
Ticket: 735345[35790]
Version: 9.0.2501.5
Datum:
Anwendung: FIMSG,MHB
Variante: --
Funktion/Report: --
Weitere Informationen
Tags:
Releasenote, 9.0.2501.5, 35790, 735345

---

## Makroeinstiegspunkt Belegversand

Makroeinstiegspunkt Belegversand
Im Pfleger Vorgangsunterklassen [FRZ] besteht nun auf
dem Tabreiter "Abwicklung" im Bereich "Versand" die Möglichkeit ein Makro zu
hinterlegen welches optional vor oder nach dem Belegversand aufgerufen
wird.  Die Übergabeparameter sind FA_ID, die FA_MndNr sowie ein
Kennzeichen, das steuert ob der Aufruf vor oder nach dem Belegversand
stattfindet (Vorher = 1, Nachher= 0).
Releasenote Kategorie:
Ticket: 744827[36499]
Version: 9.0.2501.5
Datum:
Anwendung: Formulardruck
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 36499, 744827

---

## Disposition (EPA DISPOSITION)

Disposition (EPA DISPOSITION)
Bezeichnung
Standardwert
Erklärung
Artikelnummer für die ER des
      Maklers
Artikelnummer für die ER der
      Spedition
Lagernummer des Artikels für die ER
      des Maklers
Lagernummer des Artikels für die ER
      der Spedition

---

## An bzw. aberkannte Menge (EPA UH_DISPOSITION)

An bzw. aberkannte Menge (EPA
UH_DISPOSITION)
Bezeichnung
Standardwert
Erklärung
Artikelnummer für den
      Makler
Nein
Speditionsbuchung oder Wertartikel
      aus Hauptartikel
Nein
Speditionsbuchung oder Wertartikel
      aus Hauptartikel
Nein

---

## Änderung der Versandart und Frachtvariante beim Kundenwechsel

Änderung der Versandart und Frachtvariante beim Kundenwechsel
Eine Änderung der Versandart kann die Änderung einer
Frachtvariante nach sich ziehen. Eine Änderung zur Frachtvariante 0 ist
unkritisch. Eine andere Änderung ist jedoch nicht möglich, da Referenz-ERP derzeit die
Neuberechnung der Fracht nicht unterstützt.
Die durch den Kundenwechsel bedingte Änderung der
Versandart wird vollzogen, jedoch ggf. eine Meldung ausgegeben, dass die
Änderung der Frachtvariante abgewiesen wurde. Derzeit besteht lediglich die
Möglichkeit, den Beleg neu zu erfassen, wenn eine Frachtberechnung geändert
werden soll.

---

## Änderung der Versandart und Frachtvariante beim Kundenwechsel

Änderung der Versandart und Frachtvariante beim Kundenwechsel
Eine Änderung der Versandart kann die Änderung einer
Frachtvariante nach sich ziehen. Eine Änderung zur Frachtvariante 0 ist
unkritisch. Eine andere Änderung ist jedoch nicht möglich, da Referenz-ERP derzeit die
Neuberechnung der Fracht nicht unterstützt.
Die durch den Kundenwechsel bedingte Änderung der
Versandart wird vollzogen, jedoch ggf. eine Meldung ausgegeben, dass die
Änderung der Frachtvariante abgewiesen wurde. Derzeit besteht lediglich die
Möglichkeit, den Beleg neu zu erfassen, wenn eine Frachtberechnung geändert
werden soll.

---

## Maps Tourenplanung

Maps Tourenplanung
In Referenz-ERP hat die Maps-Tourenplanung verschiedene
Wegplanungs-Tools und Funktionen zusammengefasst und ersetzt.
•
Das Elara-Google-Karten-AddIn, das in verschiedenen Optionbox-Menus
Kartenfunktionen bereitstellte
•
Die Tourenplanung, die unter
[TOUR]
/
[TOURS]
verfügbar war
•
Die Geodatenermittlung
Einige der Konfigurationsfelder sind gleichgeblieben,
die Notwendigkeit der Nutzung kostenpflichtiger Dienste hinzugekommen.

---

## Tourenplanung-Profil

Tourenpl
anung-Profil
Stammdatenpflege
Anschriften
Maps Tourenplanung Profil
[MTPP]
Die Tourenplanung stellt je nach Profil verschiedene
Ansichten bereit. Mit dem Aufruf dieses Profils werden diese beim Start bereits
aktiviert.
Im Pfleger MapsTourenPlanungProfil
[MTPP]
können die Parameter eingestellt
werden:
Maps Tourenplanung
      Profil
Feld
Bedeutung
Id
Laufende ID des Profils – diese ist
      wichtig für den Aufruf
Startadresse
Soll
      jede geplante Tour an einem bestimmten Punkt (z.b. dem eigenen Standort
      oder dem Auslieferungslager starten, so kann hier die Startadresse
      hinterlegt werden.
Startadresse verwenden
Wird
      hier „Ja“ angegeben, wird die o.a. Startadresse aus Start der Reise
      angegeben.
Start gleich Ziel
Soll
      die Rundreise auch am Ausgangspunkt enden, so muss diese Option gewählt
      werden.
Ziel
      festlegen
Soll
      eine Reise beim letzten gewählten Punkt enden unabhängig von den weiteren
      Streckenpunkten, so wird dies hier angegeben.
Beim
      Start optimieren
Ist
      „Ja“ gewählt, so werden beim Start die Wegpunkte zu der kürzesten zu
      ermittelnden Kette verbunden.
Nur
      Verteilung anzeigen
Wird
      hier „Ja“ angegeben, so wird keine Entfernungsermittlung eingeschaltet.
      Dies spart einen Aufruf des kostenpflichtigen Webservices von Google Maps.
      Es werden lediglich die Punkte auf der Karte als Verteilung angezeigt.
Geodaten ermitteln
Wenn
      „Ja“ angegeben ist, wird Referenz-ERP versuchen fehlende Geodaten beim Einlesen
      der Daten zu ermitteln. Dies kann u.U. Kosten verursachen.
Private Datenprozedur
Hier
      kann eine private Datenprozedur für den Druck-Report angegeben
      werden
Privater Report
Hier
      kann ein privater Report angegeben werden

---

## Maps Tourenplanung

Maps Tour
enplanung
In allen Auswahllisten mit einer adressid oder kundid
in den Returnfeldern heraus kann eine Tourenplanung angeschlossen werden. Die
Anwendung sucht zunächst nach einer AdressId und wenn diese nicht verfügbar ist
nach der KundId, deren Hauptanschrift dann ermittelt wird.
Beispielhaft ist die Funktion in Kunden
[KU]
und Anschriften
[ANSCH]
eingebaut worden.
Der Controlstring lautet
^jpl
MapsTouren <ProfilId>
Die ProfilId bestimmt sich aus dem eingestellten
Profil in
[MTPP]
Die maximale Anzahl der anzuzeigenden Wegpunkt ist je
nach Anwendungsfall beschränkt:
•
Bei Anzeige „nur Verteilung“ gibt es keinerlei Einschränkungen
•
Bei Streckenanzeigen, die einen festen Startpunkt berücksichtigen, dürfen
nur 9 weitere Wegpunkte aufgenommen werden.
•
Bei Streckenanzeigen ohne festen Startpunkt können 10 Wegpunkte angegeben
werden.
Die Beschränkungen liegen in der von Google
bereitgestellten Entfernungsmatrix begründet.

---

## Mailversand per (SPA 1019)

Mailversand per (SPA 1019)
Im Idealfall kann der Datenbankserver E-Mails ins
Internet versenden bzw. die im Versandprofilstamm eingetragenen Mailserver
erreichen. Hier ist der SPA auf „Datenbank“ einzustellen
Ist dies nicht der Fall, muss ein externer Dienst dies
übernehmen, der sowohl die Datenbank als auch den Mailserver erreichen kann.
Dann ist dieser Steuerparameter auf „Dienst oder Exe“ einzustellen.

---

## SGS-Interface-Lizenz (SPA1116)

SGS-Interface-Lizenz (SPA1116)
Lizenz für das Interface zur SGS-Versandsoftware.

---

## Versandartabh. Zu-/Abschläge möglich(SPA 116)

Versandartabh. Zu-/Abschläge möglich(SPA 116)
Bei „Nein“ werden diese Funktionen abgeschaltet.

---

## Vorbelegung der Tour-Stationsliste bei neuer Gültigkeit (SPA 1163)

Vorbelegung der Tour-Stationsliste bei neuer Gültigkeit (SPA 1163)
Mit diesem Steuerparameter kann eingestellt werden, ob
beim Erstellen einer neuen Gültigkeit für eine Tour, die Liste der Station
vorbelegt werden soll. Die Vorbelegung findet immer nur dann statt, wenn in der
Stationsliste kein Eintrag vorhanden ist.
Einstellung
Bedeutung
Nein
Die
      Tourenanlage funktioniert wie gewohnt. (Standard)
Ja
Folgende Werte werden wie folgt
      vorbelegt:
•
Die Nr. mit der
      1
•
Die Priorität
      mit der 1
•
Die Sperre mit
      Nein

---

## Versandanschrift = Hauptanschrift drucken(SPA 117)

Versandanschrift = Hauptanschrift drucken(SPA 117)
Bei „Ja“ wird im Fall gleicher Versand- und
Hauptanschrift die Versandanschrift trotzdem gedruckt.

---

## Sperre Kontraktanschrift in Versandadresse (SPA 154)

Sperre Kontraktanschrift in Versandadresse (SPA
154)
Ist die Einstellung „Nein“, wird die Kontraktanschrift
in die Versandadresse des Vorgangs (üblicherweise Lieferschein) übernommen.
Dieses macht nur Sinn, wenn in einem Lieferschein nur auf Kontrakte einer
Lieferanschrift zugegriffen wird.
Bei „Ja“ wird die Übernahme der Kontraktadresse
unterbunden.
Hinweis: Diese SPA-Einstellung kann durch eine Angabe
in der
Vorgangsunterkasse
überschrieben
werden!

---

## Typ Touren-Tages-Zuordnung(SPA 161)

Typ Touren-Tages-Zuordnung(SPA 161)

---

## Teildisposition mit Zu-/Abschlägen zulässig(SPA 165)

Teildisposition mit Zu-/Abschlägen zulässig(SPA
165)
Die Funktion
Standard-Teildisposition/Mehrfachteildisposition
wird in der Vorgangsbearbeitung auch bei Zu-/Abschlägen zugelassen.

---

## Automatische Frachten(SPA 184)

Automatische Frachten(SPA 184)
Mit diesem Steuerparameter kann das Ziehen
automatischer Frachten aktiviert / deaktiviert werden.

---

## Skontierung von Frachten(SPA 187)

Skontierung von Frachten(SPA 187)
Skonti auf Frachten werden wie folgt behandelt:
wie Ware: sie richten sich nach der Warenposition
nie: auf Frachten gibt es keine Skonti
immer: auf Frachten werden immer Skonti gewährt

---

## Standard-Frachtvariante(SPA 199)

Standard-Frachtvariante(SPA 199)

---

## Erhalten der Unterklasse bei Umwandlung(SPA 256)

Erhalten der Unterklasse bei Umwandlung(SPA 256)
Hierbei geht es um die Bestimmung der Unterklasse
eines Vorgangs, der durch Umwandlung entstanden ist.
Einstellungen
Nein
Diese Einstellung setzt im
      umgewandelten Vorgang die Unterklasse auf 0. Bei den Funktionen
      ‚Teildisposition Lieferschein‘ und ‚Teildisposition Ladeschein‘ in der
      Auftragsbearbeitung wird die Unterklasse aus der Kodierung des Aufrufrufs
      der Funktion aus der Optionbox gewonnen. In der Standardeinstellung von
      Referenz-ERP steht dort ebenfalls ‚0‘
Einzelumwandlung
Bei
      Einzelumwandlungen (z.B. Rechnung aus Lieferschein) wird die Unterklasse
      des Ursprungbelegs beibehalten, nicht jedoch bei Sammelumwandlungen.
immer
Bei
      dieser Einstellung wird immer die Unterklasse erhalten.

---

## Frachtermittlung aktiv(SPA 29)

Frachtermittlung aktiv(SPA 29)
Mit diesem SPA kann die Frachtermittlung aktiviert /
deaktiviert werden.

---

## Skontierung kalkulatorischer Frachten(SPA 315)

Skontierung kalkulatorischer Frachten(SPA 315)

---

## Aut. Frachten bei Kasse aktiv(SPA 327)

Aut. Frachten bei Kasse aktiv(SPA 327)
Hier wird bei der Tresen Kasse entschieden, ob für die
augenblicklich gezogene Position die automatischen Frachten ziehen sollen.
Auch bei der POS-Kasse werden mit diesem
Steuerparameter die automatischen Frachten ausgeschaltet.

---

## Separate Steuer auf Frachten möglich(SPA 331)

Separate Steuer auf Frachten möglich(SPA 331)

---

## Teildisposition nur bei positiver Restmenge(SPA 334)

Teildisposition nur bei positiver Restmenge(SPA 334)
Dieser Steuerparameter wurde deaktiviert. Die
Einstellung kann jetzt für jede Vorgangsklassen-Vorgangsunterklassen-Kombination
als Teildispositionsquelle einzeln vorgenommen werden (
FRZ
).

---

## DTA-Textänderung aktiv(SPA 354)

DTA-Textänderung aktiv(SPA 354)
Mit diesem Steuerparameter kann die manuelle
Texterfassung aktiviert / deaktiviert werden. Es steht dann im DTA eine weitere
Funktion „Text/Avise erfassen“ zur Verfügung.

---

## Typ-Tourverwaltung(SPA 357)

Typ-Tourverwaltung(SPA 357)
Tourverwaltung: mit/ohne integrierter
Stationsliste

---

## Tour- Dispositionsart(SPA 358)

Tour- Dispositionsart(SPA 358)

---

## Fracht-Lizenz(SPA 445)

Fracht-Lizenz(SPA 445)
Lizenz für Fracht.

---

## Sofort-Aktualisierung bei Disposition(SPA 45)

Sofort-Aktualisierung bei Disposition(SPA 45)
Sollen Sofortupdates bei Vorgangs-Disposition
greifen?

---

## Vorgangserweiterungen als Kopie(SPA 520)

Vorgangserweiterungen als Kopie(SPA 520)
Bei den Vorgangserweiterungen handelt es sich um Daten
( Bemerkungstexte, Transportinformationen etc. ), die beim Umwandeln in die
nächste Stufe normalerweise nicht kopiert werden, sondern für alle Kopien
gelten. Bei „Ja“ wird von diesen Daten bei jedem Umwandlungsschritt eine eigene
Kopie angelegt, so dass diese dann individuell für den neuen Vorgang verändert
werden können.

---

## KostenStellen/-träger anwenden(SPA 623)

KostenStellen/-träger anwenden(SPA 623)
In den Frachttabellen konnte man schon Kostenstellen
bzw. Kostenträger eintragen. Die Werte wurden aber nicht in den Beleg
übernommen. Durch die Einstellung „Ja“ werden diese Werte jetzt übernommen.

---

## Teildisposition aktiv(SPA 65)

Teildisposition aktiv(SPA 65)
Mit diesem Steuerparameter kann die Teildisposition
aktiviert / deaktiviert werden.

---

## Versand Mail Lokal(SPA 668)

Versand Mail Lokal(SPA 668)

---

## Versand FAX Lokal(SPA 669)

Versand FAX Lokal(SPA 669)

---

## Nur aktuelle Belege bereitstellen für Beleg-Mailversand (SPA 855)

Nur aktuelle Belege bereitstellen für Beleg-Mailversand
(SPA 855)
Ist dieser Steuerparameter aktiviert, so werden
bisherige Einträge für den Mailversand aus der Tabelle „fa_vermailung“ gelöscht.
Bisher erstellte Versionen des Beleges werden nicht versendet werden.
Hinweis:
Ist in der Vorgangsunterklasse eine
Belegversandprozedur eingestellt, die Belege sofort versendet, so ist dieser
Steuerparameter wirkungslos. Sind Belege bereits über ein Event versendet
worden, so werden sie nicht zurückgerufen.

---

## Belegkorrektur bei Belegversand (SPA 860)

Belegkorrektur bei Belegversand (SPA 860)
Einstellungen
Nie
      sperren
Es
      erfolgt keine Sperre, auch dann nicht, wenn der Beleg bereits per E-Mail
      versendet wurde.
Nur
      Warnung ausgeben
Wenn
      der Beleg bereits per E-Mail versendet wurde, wird eine Warnung ausgegeben
      und der Bediener muss entscheiden, ob er die Korrektur fortsetzen will
      oder die Belegbearbeitung mit F10 ohne Korrektur verlässt.
Gegen Korrektur sperren
Belege, die bereits per E-Mail
      versendet wurden, können nicht korrigiert werden.

---

## Belegversand Lizenz(SPA 870)

Belegversand Lizenz(SPA 870)
Lizenz für den Belegversand.

---

## Belegversand Empfänger (SPA 888)

Belegversand Empfänger (SPA 888)
Beim Belegversand im Vorgang müssen für verschiedene
Vorgangsklassen unterschiedliche Wege gegangen werden, den Empfänger zu
ermitteln. So wird für Rechnungen die Mailadresse des Rechnungsempfängers
ermittelt, bei Lieferscheinen die Mailadresse der Lieferadresse.
Eine privatisierte Version dieser Funktion kann hier
eingetragen werden.
Bereich
Bedeutung /
Option
-
Kein
      Wert
Standard
In
      dieser Option wird eine Datenbankprozedur hinterlegt, welche anstelle der
      Standarddatenbankprozedur „Amic_Belegversand_Mailempfaenger“ im
      Belegversand den Empfänger ermittelt. Dabei ist zu beachten, dass die
      private Datenbankprozedur die gleichen Eingangs- sowie Ausgangsparameter
      der Standarddatenbankprozedur besitzt.
RohwareSammeldruck
In
      dieser Option wird eine Datenbankprozedur hinterlegt, welche anstelle der
      Standarddatenbankprozedur „Amic_Belegversand_RW_Mailempfaenger“ bei
      Rohwaresammeldruck aufgerufen wird. Dabei ist zu beachten, dass die
      private Datenbankprozedur die gleichen Eingangs- sowie Ausgangsparameter
      der Standarddatenbankprozedur besitzt.

---

## Belegversand Ausgabeart (SPA 889)

Belegversand  Ausgabeart (SPA 889)
Beim Belegversand im Vorgang müssen für verschiedene
Vorgangsklassen unterschiedliche Wege gegangen werden, die Quelle der Ausgabeart
( mit Druck/ohne Druck) zu ermitteln. So wird für Rechnungen die Einstellung des
Rechnungsempfängers ermittelt, bei Lieferscheinen die Einstellung des
Warenempfängers.
Eine privatisierte Version der
Standarddatenbankfunktion „AMIC_Belegversand_Ware_Versandart“ kann hier
eingetragen werden.

---

## Belegversand Betreff (SPA 890)

Belegversand Betreff (SPA 890)
Beim Belegversand im Vorgang müssen für verschiedene
Vorgangsklassen unterschiedliche Wege gegangen werden, den Betreff zu ermitteln.
So wird in Abhängigkeit von der Vorgangsklasse und der Belegnummer ein Betreff
erstellt.
Eine privatisierte Version dieser Funktion kann hier
sowohl für den Versand von Einzelbelegen als auch für den Versand von
Rohware-Sammeldruck-Belegen eingetragen werden.
Bereich
Bedeutung /
Option
-
Kein
      Wert
Standard
In
      dieser Option wird eine Datenbankprozedur hinterlegt, welche anstelle der
      Standarddatenbankprozedur „Amic_Belegversand_Betreff“ im Belegversand den
      Betreff für den Belegversand ermittelt. Dieser Eintrag betrifft nicht den
      Versand von Rohware-Sammeldruck-Belegen. Für diese kann eine entsprechende
      Prozedur im Bereich ‚RohwareSammeldruck‘ angegeben werden (s.u.). Dabei
      ist zu beachten, dass die private Datenbankprozedur die gleichen Eingangs-
      sowie Ausgangsparameter der Standarddatenbankprozedur besitzt.
RohwareSammeldruck
In
      dieser Option kann für Rohware-Sammeldruck-Belege eine Datenbankprozedur
      hinterlegt, welche anstelle der Standarddatenbankprozedur
      „Amic_Belegversand_RW_Betreff“ den Betreff für den Belegversand von
      Rohware-Sammeldruck-Belegen aufgerufen wird. Dabei ist zu beachten, dass
      die private Datenbankprozedur die gleichen Eingangs- sowie
      Ausgangsparameter der Standarddatenbankprozedur besitzt.

---

## Rechnungstrennung durch Versandart(SPA 90)

Rechnungstrennung durch Versandart(SPA 90)
Trennen: sind mehrere Lieferscheine mit verschiedenen
Versandarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Versandart eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Versandarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der Versandart
der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Versandarten markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden der Versandart
der Lieferscheine zugeordnet.

---

## Rechnungstrennung durch Versandadresse(SPA 92)

Rechnungstrennung durch Versandadresse(SPA 92)
Trennen: sind mehrere Lieferscheine mit verschiedener
Versandadresse markiert und man will diese in eine Sammelrechnung umwandeln, so
wird für jede Versandadresse eine Rechnung erstellt.
Neu: sind mehrere Lieferscheine mit verschiedenen
Versandadressen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erstellt und die Warenbewegungen werden der
Versandadresse der Rechnung zugeordnet.
Nein: sind mehrere Lieferscheine mit verschiedenen
Versandadressen markiert und man will diese in eine Sammelrechnung umwandeln, so
wird eine Sammelrechnung erzeugt und die Warenbewegungen werden den
Versandadressen der Lieferscheine zugeordnet.

---

## Druckunterdrückung bei nicht kalkulatorischer Gruppenfracht erlaubt(SPA 980)

Druckunterdrückun
g bei nicht kalkulatorischer
Gruppenfracht erlaubt(SPA 980)
Mit diesem Steuerparameter kann im Stammdatenmodul zur
Pflege von Frachttabellen bei nicht kalkulatorischen Gruppenfrachten die
Möglichkeit der Unterdrückung der Druckausgabe der resultierenden
Gruppenfrachtzeile freigeschaltet werde.

---

## „Teildisposition mit Vorlauf“ aktiv (SPA 986)

„Teildisposition mit
Vorlauf“ aktiv (SPA 986)
Mit diesem Steuerparameter kann die
Teildisposition mit Vorlauf
aktiviert
/ deaktiviert werden.

---

## Crystal-Report statt Formulardruck (SPA 997)

Crystal-Report statt Formulardruck (SPA 997)
Im automatischen Zahlungsverkehr werden Avise,
Banksammelliste und Begleitzettel gedruckt. Dies geschah bisher nur über den
Formulardruck. Hier kann man nun für diese drei Bereiche hinterlegen, welcher
Report anstelle des Formulars verwendet werden soll.

---

## Application Identifier des EAN-128 / UCC-128

Application Identifier des EAN-128 /
UCC-128
Liste der Application Identifier
AI
Beschreibung
Länge AI
Länge Daten
FNC1
00
Serial Shipping Container
      Code
2
numerisch 18-stellig
-
01
EAN
      Nummer der Handelseinheit
2
numerisch 14-stellig
-
02
EAN
      Nummer der in der Transporteinheit enthaltenen Waren
2
numerisch 14-stellig
-
10
Losnummer bzw.
      Chargennummer
2
alphanumerisch bis zu
      20-stellig
ja
11
Herstellungsdatum JJMMTT
2
numerisch 6-stellig
-
12
Fälligkeitsdatum JJMMTT
2
numerisch 6-stellig
-
13
Packdatum JJMMTT
2
numerisch 6-stellig
-
15
Mindesthaltbarkeitsdatum
      JJMMTT
2
numerisch 6-stellig
-
17
Verfalldatum JJMMTT
2
numerisch 6-stellig
-
20
Produktvariante
2
numerisch 2-stellig
-
21
Seriennummer
2
alphanumerisch bis zu
      20-stellig
ja
22
HIBCC Nummer
2
alphanumerisch bis zu
      29-stellig
-
23n
Chargennummer
3
numerisch bis zu
      19-stellig
ja
240
zus.
      Produktidentifikation vom Hersteller
3
alphanumerisch bis zu
      30-stellig
ja
241
Kundenteilenummer
3
alphanumerisch bis zu
      30-stellig
ja
250
Seriennummer eines integrierten
      Bauteils
3
alphanumerisch bis zu
      30-stellig
ja
251
Bezug auf die
      Grundeinheit
3
alphanumerisch bis zu
      30-stellig
ja
252
Global Identifier Serialised for
      Trade
3
numerisch 2-stellig
-
30
Menge in Stück
2
numerisch bis zu
      8-stellig
ja
310d
Nettogewicht in
      Kilogramm
4
numerisch 6-stellig
-
311d
Länge, Meter
4
numerisch 6-stellig
-
312d
Breite, Meter
4
numerisch 6-stellig
-
313d
Höhe, Meter
4
numerisch 6-stellig
-
314d
Fläche, Quadratmeter
4
numerisch 6-stellig
-
315d
Nettovolumen, Liter
4
numerisch 6-stellig
-
316d
Nettovolumen, Kubikmeter
4
numerisch 6-stellig
-
320d
Nettogewicht, Pounds
4
numerisch 6-stellig
-
321d
Länge, Inches
4
numerisch 6-stellig
-
322d
Länge, Feet
4
numerisch 6-stellig
-
323d
Länge, Yards
4
numerisch 6-stellig
-
324d
Breite oder Durchmesser,
      Inches
4
numerisch 6-stellig
-
325d
Breite oder Durchmesser,
[...]


---

## Event Manager

Event Manager
Die Hilfe hierzu finden Sie unter
Zusatzprogramme >
Belegversand > Warteschleife für zu versendende Belege > Events für
Beleg-Mailversand
oder
Technisches Umfeld > Events

---

## Schnelle Teildisposition

Schnelle Teildisposition
Unter dem Register „Schnelle Teildisposition“ können
Einstellungen für die „Schnelle Teildisposition“ bei der Artikelerfassung
vorgenommen werden. Die Einstellungen teilen sich in die Bereiche „Unterklasse
als Dispositionsziel“ und „Unterklasse als Dispositionsquelle“ auf.
Unterklasse als Dispositionsziel
Diese Einstellungen beeinflussen das Verhalten des
disponierenden Beleges dieser Klasse/Unterklasse.
Maskenfeld
Beschreibung
Quellbeleg abbuchen
Hier
      kann eingestellt werden, ob dieser Beleg Mengen vom Quellbeleg
      abbucht.
Lagerübergreifende
      Teildisposition
Bei
      „Nein“ wird die Auswahl der Artikel bei der „Schnellen Teildisposition“
      auf Artikel eingeschränkt, die sich in dem gewählten Lager
      befinden.
Bei
      „Ja“ werden alle verfügbaren Artikel angezeigt und bei der Wahl eines
      Artikels, der nicht aus dem gewählten Lager stammt, wird dieser
      lagerübergreifend umgewandelt, sofern er auch in dem gewählten Lager
      vorhanden ist.
Waagenbelege zulassen
Hier
      kann eingestellt werden, ob aus der Waage erzeugte Vorgänge mit der
      „Schnellen Teildisposition“ bearbeitet werden dürfen. Im Standard steht
      der Schalter auf Nein. Wird der Schalter auf „Ja“ gestellt, so kann auch
      die Menge bei der „Schnellen Teildisposition“ abgeändert
      werden.
Achtung: Die „Schnelle
      Teildisposition“ ändert die Original Menge des Vorganges. Wird der Vorgang
      komplett per Teildisposition umgewandelt und danach storniert wird der
      Status der Waage für den Beleg auf abgeschlossen zurück gestellt.
Itembox Quellbelege
Hier
      kann eine individuelle Itembox für die Auswahl der Belege hinterlegt
      werden.
Disponierbare
      Belegklassen
Hier
      kann eingestellt werden aus welcher Belegklasse die Vorgänge stammen,
      deren Artikel für diese Belegunterklasse bei der „Schnellen
      Teildisposition“ angezeigt werden.
Mit
      Mausklick wird die gew
[...]


---

## Gebietsstamm

Gebietsstamm
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Gebietsstamm
Direktsprung
[GEB]
Der Gebietsstamm findet derzeit beim Frachtwesen und
in einigen Auswertungen Anwendung. Einzutragen sind eine laufende Nummer und die
Bezeichnung für das Gebiet sowie ggf. die GTB Nummer (heute jedoch von
abnehmender Bedeutung). Der Gebietstamm wird dem Kunden- und Lagerstamm über die
Anschriftenmaske zugeordnet.

---

## Gefahrgut im Vorgang

Gefahrgut im Vorgang
Es ist gesetzlich vorgeschrieben, beim Transport von
Gefahrgütern Informationen über Art und Umfang mitzuführen. Zudem dürfen der
Umfang und die Kombination vorgeschriebene Höchstgrenzen nicht übersteigen.
Referenz-ERP ermöglicht, z.B. folgende Information automatisch auszugeben:
Um diese Daten ausgeben zu können ist das zugrunde
liegende Formular entsprechend einzurichten.
Die Warenpositionszeile (Bereich 101)
Für die Zusammenfassung aller Gefahrgutinformationen
im Vorgang sind die Be­reiche 60,61,62 anzulegen.
Der Gefahrgutnachweis ist in allen Vorgangsklassen
möglich; nachfolgend ist das Beispiel Lieferschein wiedergegeben.

---

## Funktionen in den Ware-Auswahllisten

Funktionen in den Ware-Auswahllisten
In den Ware-Auswahllisten gibt es Funktionen für den
Belegversand
Funktion
Information
Neu
      drucken und neu verwenden
Verwenden Sie diese Funktion, wenn
      Sie Änderungen im Beleg gemacht haben, die neu gedruckt und dann versendet
      werden sollen.
Beleg erneut versenden
Verwenden Sie diese Funktion, um
      einen einmal erstellten Beleg erneut per E-Mail an den Kunden zu versenden
      , z.B. weil dieser die E-Mail versehentlich gelöscht hat

---

## Funktionen

Funktionen
Funktionen
Freigeben/Versenden
Gibt
      Einträge frei zur Versendung. Wenn der Versand
Synchron
erfolgen soll,
      so werden die E-Mails auch sofort versendet. Anderenfalls werden sie
      zyklisch durch den Dienst versendet.
Bei
      E-Mails mit Mailversandquelle = Ware-Beleg oder Mailversandquelle =
      Eohware-Sammeldruck wird bei erfolgreichem Versand das Kennzeichen
      V_StatusBelegVersand im Vorgangstamm beziehungsweise V_RohwareStatusMail
      in der Relation V_Rohware auf den Wert ‚Versendet‘ gesetzt.
Zurückstellen
Stellt den Eintrag zurück. Dies kann
      eine bewusste Rückstellung zur späteren Klärung sein.
Bereits versendete Einträge lassen
      sich nicht zurückstellen.
Löschen
Löscht den Eintrag
Bereits versendete Einträge lassen
      sich nicht löschen
Bei
      E-Mails mit Mailversandquelle = Ware-Beleg oder Mailversandquelle =
      Eohware-Sammeldruck wird bei erfolgreichem Löschen das Kennzeichen
      V_StatusBelegVersand im Vorgangstamm beziehungsweise V_RohwareStatusMail
      in der Relation V_Rohware auf den Wert ‚Zurück genommen‘
      gesetzt.
Email ändern
Öffnet einen Pfleger zum
      nachträglichen Bearbeiten der Mailadressen. Wenn die Mail bereits
      versendet wurde, wird ein neuer Eintrag erzeugt. Der Inhalt bleibt der
      Originalinhalt. Der Verweis zeigt auf die ursprüngliche Mail und nicht auf
      die ursprüngliche Quelle.
Wenn
      eine Mail mit bereits gelöschter Verpostung erneut versendet werden soll,
      muss beim Ändern eine neue Verpostung ausgewählt werden.
Bereich
Filter der Auswahlliste

---

## Formulararchiv-Einstellungen

Formulararchiv-Einstellungen
Der Belegversand verwendet das Formulararchiv zur
Speicherung des Beleges. Im Formulararchiv kann eine Einstellung verwendet
werden, die das Überschreiben eines archivierten Beleges durch einen erneut zu
archivierenden Beleg (z.B. nach einer Änderung) erlaubt (siehe auch
Archivierungsmerkmal der Dokumente im
Formulararchiv-Manager
).
Je nach Einstellung kann es sein, dass nicht das
gewünschte Formular per Mail versendet wird. In diesem Fall ist die Einstellung
dieses Parameters gegen die Reihenfolge beim Druck abzuwiegen.

---

## Mailversandquellen

Mailversandquellen
Um später die verschiedenen Quellen zu identifizieren,
ist das Anwendungsformat „AF_MVQuelle“ geschaffen worden, deren ersten Felder
von Branchen-ERP vorbelegt wurden. Weitere Quellen können ab ID 100 bei Bedarf
hinzugefügt werden, um nach diesen filtern zu können.
Wert
Beschreibung
0 -
      Unbekannt
Alle nicht näher spezifizierte
      Quellen
1 –
      Avis
Fibu-Avise
2 –
      Mahnung
FiBu-Mahnung
3 –
      Zinsabrechnung
FiBu-Zinsabrechnungen
4 –
      Archiv
Belege, die aus dem Archiv
      versendet wurden
5 –
      Ware-Beleg
Belege aus der Ware (Rechnungen
      etc.)
6 –
      Test-Mail
Test-Mails z.B. aus dem
      Versandprofilstamm
7 –
      Rolle
Rollenanträge
8 –
      Fehlerprotokoll
Mails aus dem
      Fehlerprotokoll
9 –
      Rohware-Sammeldruck
Belege, die per Rohware-Sammeldruck
      erzeugt wurden.
10 –
      Speichern unter
Einträge die beim Ändern von bereits
      versendeten Mails erstellt werden. Es wird auf die ursprüngliche Mail
      referenziert. Ein direkter Bezug zur Originalquelle ist nicht mehr
      vorhanden.

---

## Recherche nach Referenznummern

Recherche nach Referenznummern
Die Aufgabe der Funktion „Recherche“ ist es, anhand
einer vorgegebenen Referenznummer zu versuchen, aus dem System die anderen Daten
zu ermitteln.
Man hat beispielsweise über einen Import einen Beleg
ins Formulararchiv transportiert und weiß zu diesem zunächst nur die
Referenznummer. Die Idee ist nun, dass es schon weitere Verwendung dieser
Referenznummer im System geben könnte, und in einem solchen Falle sollen dann
die Daten zur Vervollständigung des Formulararchiveintrages herangezogen
werden.
Inhaltlich ist also das Vorhandensein einer
Referenznummer unabdinglich, des Weiteren darf die Belegklasse noch nicht
festgelegt sein. Die Belegklasse ist der Erkenner, dass der Eintrag schon
möglicherweise behandelt wurde.
Nun ist die Suchstrategie folgende:
•
Vorgangsstamm anhand von Referenznummer, im Falle eines Treffers sind
somit Belegnummer, Kundennummer und Vorgangsklasse mittelbar. Die Belegklasse
des Formulararchiv-Eintrages wird die Vorgangsbelegklasse.
•
FibuvorgStamm, falls gefunden, sind somit Fibu-Belegnummer, Kontonummer
resp. Kundennummer ermittelt. Belegklasse wird 7000.
•
Kontraktstamm, falls gefunden, wird die Kontraktnummer zur Belegnummer,
der Kunde wird über eine weitere Datenrecherche gewonnen. Belegklasse wird
7500
•
OWaage, falls gefunden, wird die Wiegenummer zur Belegnummer, Kunde
übernommen und Belegklasse 8000
Als letztes wird der Belegtyp-Text konventionsgemäß
ermittelt und festgeschrieben.

---

## Frachten und Frachtwesen

Frachten und Frachtwesen

---

## Tourverwaltung

Tourverwaltung

---

## Belegeingabe

Belegeingabe
Auf dieser Maske lassen sich schnell Belege für
Spedition, Befrachter, Makler, Einladekontrolleur und Löschkontrolleur erzeugen.
Je nachdem wie die Maske aufgerufen wird, werden die Belege unterschiedlich
vorbelegt.
Folgende Felder stehen auf der Maske zur
Verfügung.
Feld
Beschreibung
Kunde
Die
      Vorbelegung des Kunden erfolgt je nach Typ unterschiedlich.
Makler
Es
      wird versucht einen Kunden aus dem Vertreterstamm des ersten gefunden
      Kontrakts der Strecke zu ermitteln.
Spedition /
      Befrachter, Einladekontrolleur, Löschkontrolleur
Je
      Typ wird hier versucht den Kunden aus dem Stammsatz oder
      Positionsstammsatz zu ermitteln.
Lager
Die
      Vorbelegung des Lagers erfolgt aus dem Beleg.
Artikel
Die
      Vorbelegung des Artikels erfolgt aus den
Sekundärschlüsseln
des Artikelstamms. Dort
      kann beim Schlüsseltyp „Referenzartikel“ unterschiedliche Artikel
      hinterlegt werden:
Position
Typ
1
Spedition /
            Befrachter
2
Einladekontrolleur
3
Löschkontrolleur
4
Makler
Wenn
      am Artikelstamm
kein
passender Artikel gefunden wird, gilt der
      übergebene Artikel.
Menge
Die
      Vorbelegung der Menge erfolgt aus dem Beleg
Preis
Die
      Vorbelegung des Preises erfolgt je nach Typ unterschiedlich.
Makler
Es
      wird versucht den Preis aus der Vertreterprovision des ersten gefundenen
      Kontrakts der Strecke zu ermitteln.
Spedition /
      Befrachter, Einladekontrolleur, Löschkontrolleur
Es
      wird versucht den Preis aus der Fracht des ersten gefundenen Kontrakts der
      Strecke zu ermitteln.

---

## Versandarten

Versandarten
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Versandarten
[VS]
Versandarten sind immer wiederkehrende Arten der
Übergabe einer Ware. Neben dem Problem, die Ware vom Transportmittel in das
Lager zu bekommen, wird mit ihrer Hilfe, durch die Regelung des
Übergabezeitpunktes und Ortes, auch die Versicherungspflicht geregelt.
Dies hat gerade bei Artikeln, die einen hohen Wert
haben, eine tragende Bedeutung.
Versandarten können zum Beispiel sein:
Frei Haus
Ab Lager
Ab Werk
FOB
CIF
Innerhalb der Versandarteneingabe/-änderung stehen
folgende Eingabefelder und Eingabemöglichkeiten zum Bearbeiten zur
Verfügung:
Formel
Bedeutung
Versandart-Nummer
Identifikationsschlüssel zur
      Versandart bei Neueingabe wird er vorgeschlagen
Bezeichnung
Texteingabe zur Versandart (Bsp.
      frei Bau, free on board o.ä.)
Fracht-Variante
Über
      die Versandart kann das Frachtwesen gesteuert werden. Die Form der
      Abwicklung, die mit dieser Ver­sand­art verbunden ist, wird hier
      eingetragen. Näheres dazu im Abschnitt „Frachtwesen“ und
Frachtvariante
Speditionsadresse
Die
      Anschrift der Spedition
Spediteur
Die
      Spedition, die diese Versandart durchführt
Preisklasse Verkauf
Die
      Preisklasse
Verkehrszweig
Verkehrszweig für
      Intrastat
Lieferbedingungsbezug
      (EDI)
Im
      Zusammenhang mit dem Verarbeiten von EDI-Nachrichten kann hier der Bezug
      zu einer Lieferbedingung gepflegt werden.
Lieferbedingung (EDI)
Im
      Zusammenhang mit dem Verarbeiten von EDI-Nachrichten kann hier eine
      Lieferbedingung gepflegt werden.

---

## Schnelle Teildisposition

Schnelle
Teildisposition
Wenn bei der Artikelerfassung noch kein Artikel
ausgewählt wurde, besteht die Möglichkeit zu einer schnellen Teilumwandlung von
Warenpositionen aus Quellbelegen. Nach Auswahl dieser Funktion wird wie bei der
Standard-Teildisposition
eine Artikelübersicht angezeigt. Wird
ein Artikel ausgewählt, so wird dieser in die Artikelerfassungsmaske übernommen
und es wird in den Teildispositionsmodus umgeschaltet. Dies ist daran zu
erkennen, dass die maximal zur Disposition zur Verfügung stehende Menge neben
der gewählten Menge angezeigt wird.
Wie gewohnt kann jetzt eine Warenposition erfasst
werden. Die umgewandelte Menge wird erst bei Abschluss des Beleges von der Menge
im Quellbeleg abgezogen. Durch eine normale Artikelauswahl wird der
Teildispositionsmodus wieder verlassen. Weitere Einstellungen wie
„Stornoprozentsatz“, „disponierbare Quellbelegklasse“ oder „lagerübergreifende
Teildisposition“ können in der
Formularzuordnung
[FRZ]
auf dem Register
Schnelle
Teildisposition
vorgenommen werden.
Einschränkungen
Im Gegensatz zur
Standard-Teildisposition
und
Mehrfachteildisposition
sind bei der „Schnellen Teildisposition“ die erzeugten Belege, sobald sie
abgeschlossen wurden, losgelöst von ihren Quellbelegen. Das heißt zum Beispiel,
dass nachträgliche Korrekturen von Quellbelegen nicht in dem erzeugten Beleg
berücksichtigt werden und dass bei der Stornierung von durch die „Schnelle
Teildisposition“ erzeugten Belegen die Quellbelege nicht zurückgerechnet
werden.
Des Weiteren können keine Warenpositionen mit mehr als
einer Gebindezeile, bereits disponierte Warenpositionen oder Warenpositionen mit
Ausprägungen umgewandelt werden.
Bei lagerübergreifender Teilumwandlung (einzustellen
im
Register Schnelle Teildisposition
der Formularzuordnung
[FRZ]
) müssen die umgewandelten Artikel auch
in dem neu gewählten Lager existieren. Ebenso muss eine Partie oder ein Kontrakt
für die Warenposition lagerübergreifend sein und der Steuerparameter
575
[...]


---

## Ablauf im Vorgang

Ablauf im Vorgang
Die Frachtermittlung kann vollautomatisch ablaufen;
nachfolgend wird am Beispiel der Rechnungserfassung ein Erfassungsablauf
dargestellt, bei dem der Bediener Steuerungsmöglichkeiten erhält. Hierzu wurden
mittels UFLD – Steuerung die Felder Lager, Versandart, Gebiet von, Gebiet nach
im Rechnungskopf aktiviert und im Erfassungsbildschirm mittels Formulargenerator
die Zu-/Abschlagszeile (Bereich 121) eingerichtet. Es ergibt sich dann folgender
Ablauf:
Diese Eintragungen führen bei der
Positionserfassung zu folgendem Ergebnis:
Bei der kalkulatorischen Frachtermittlung wird der
Rechnungsbetrag durch die Fracht nicht verändert; sie wird lediglich intern
geführt und kann zu Umbuchungen führen (s.u.). Eine echte Fracht dagegen erhöht
den Rechnungsbetrag und führt zu Buchungen.
Durch Wahl einer anderen Versandart oder Zuordnung
anderer Gebiete verändert sich die Frachtbelastung, so dass hiermit auch die
Problematik von Rundtouren, wo nicht von festen Zuordnungen ausgegangen wird,
gelöst werden kann.

---

## Anhang

Anhang
Die kalkulatorischen Frachten werden im Vorgang
gespeichert in der Relation v_posiware als vp_warekalkfrach.
Folgende view liefert die Werte in eine
Auswahlliste:
// Private View
P_Fracht_Kalk  ---  LA   28.07.2000
//
// Beschreibung:
//
//
//
CREATE VIEW P_Fracht_Kalk AS
//
SELECT
a.artikelnummer,a.artikelbezeich,vp.vp_warekalkfrach,
vp.artikelid,w.lagernummer
//
FROM vorgangstamm vs JOIN v_posiware vp ON
(vs.v_id=vp.v_id)
JOIN warenbewegung w ON
(w.wabewid=vp.wabewid)
JOIN artikel a ON (a.artikelid=w.artikelid)
//
WHERE
vs.v_klassnummer IN
(700,790,800,890,1700,1790,1800,1890) AND
(vs.v_statusweiter
< 2)
Diese view kann dann z.B. in WBA in die Variante „Kum.
Artikel Summen“ mit folgendem Befehl eingebaut werden:
(select sum(fra.vp_warekalkfrach)  from
P_Fracht_Kalk fra
where fra.artikelid=a.artikelid) KalkFra,

---

## Ausgangslage

Ausgangslage
Grundlage der nachfolgenden Beschreibung soll folgende
Ausgangsfragestellung sein:
Ein Unternehmen arbeitet mit eigenen LKW oder
Speditionen
Die Frachten sind im Vorwege bekannt; ggf. jedoch nach
Warengruppen unterschiedlich
Die Preise mit den Kunden werden ohne die
Frachtproblematik zu berücksichtigen ausgehandelt
Wegen der Bedeutung der Frachten sollen sie das
Warengeschäft kalkulatorisch belasten
Die Kunden sind Gebieten zugeordnet für die auf
Grundlage der Entfernung Kosten ermittelt wurden.

---

## Avis als Mail versenden

Avis als Mail
versenden
Eine Avise sollte immer dann versendet werden, wenn
der Platz im Verwendungszweck nicht ausreicht, um die notwendigen Informationen
dort unterzubringen. Die von Branchen-ERP vorgegebene Aufbereitung des Verwendungszecks
kann durch eine eigene Datenbankfunktion in den
Zahlungsarten
überschrieben
werden.
Um die Avise direkt per Mail zu versenden müssen
folgen Voraussetzungen gegeben sein:
1)
Der Belegversand Lizenz muss aktiv sein.
2)
Ein
Versandprofil
muss eingerichtet
sein.
3)
In den Stammdaten für
Zahlungsarten
müssen zusätzliche
Felder gepflegt werden.
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
-1100, das so wie es ist verwendet werden kann oder als Vorlage benutzt werden
kann. In diesem Formular stehen alle Felder und Bereiche der Standard Avis zur
Verfügung. Zusätzlich existiert ein Bereich „AVIS Betreffzeile“, in dem man die
Betreff-Zeile der Mail einrichten kann. Ist kein Formular und keine
Datenbankfunktion hinterlegt, so erscheint als Betreff und als Mailinhalt
lediglich der Text „Avis“.
HINWEIS:
Um Grafiken in das
Formular mit einzubinden, kann man den bekannten HTML-Syntax <img
src="cid:XXXXXX" alt="mein bild" /> verwenden. Für XXXXXX muss die GUID aus
dem Formulararchiv, in dem die Grafik hinterlegt sein muss, angegeben
werden.
•
Ist das Versandprofil nicht eingerichtet, wird für alle Personenkonten
mit dieser Zahlungsart kein Mailversand durchgefüh
[...]


---

## Beispiel zum Formulardruck im Branchen-ERP Etikettendruck

Beispiel zum Formulardruck im Branchen-ERP Etikettendruck
Dies soll ein Beispiel für den gleichzeitigen Druck
eines Frachtbriefes beim Druck eines Lieferscheines sein. Der Frachtbrief wird
über den Branchen-ERP Etikettendruck und dort mit einer Prozedur erstellt und auf dem
DRZ
/
VRGD
Drucker gedruckt.

---

## DTA-Textänderung

DTA-Textänderung
Hauptmenü
Mahn-,Zahl-, Zinswesen
Zahlungsverkehr
Zahlungen bearbeiten
DTA F9
Text/Avise erfassen
Direktsprung
[ZHB]
Die von Branchen-ERP vorgegebene Art und Weise der
Verarbeitung des Verwendungszwecks kann bei aktivem Steuerungsparameter
„
DTA-Textänderung aktiv
“ geringfügig beeinflusst werden. Es steht dann
die Funktion „
Text/Avise erfassen
“
im DTA zur Verfügung. Dort kann man einen Festtext hinterlegen, der entweder an
Stelle des Verwendungszwecks genommen werden kann oder als Überschrift vor dem
erzeugten Text erscheinen kann. Hier kann auch beeinflusst werden, wie die Avise
gedruckt werden soll: „Nie“, „immer“ oder „bei Bedarf“. Standarteinstellung ist
„bei Bedarf“.

---

## Einführung zum Frachtwesen

Einführung zum Frachtwesen
Referenz-ERP bietet umfassende Funktionen für die
Berücksichtigung der Frachtproblematik. Dabei handelt es sich sowohl um Lösungen
der Frachtermittlung als auch solcher zur Behandlung der
Buchführungsproblematiken in der Warenwirtschaft und Finanzbuch­haltung.
In vielen Branchen (Kraftfutterwerke, Kieswerke,
Baustoffe, etc.) werden vergleichbar große (frachtintensive) Mengen mit im
Vergleich zum Warenwert bedeutenden Frachtanteilen im Einkauf, Verkauf und
intern bewegt. Die Kontrolle der Frachten ist für die Unternehmen von
wesentlicher Bedeutung für den Betriebserfolg.
Frachten entstehen:
Bei eigenem Fuhrpark als interne
Verrechnungskosten
Durch Auslieferung an den Kunden
Abholung vom Lieferanten
Transporte zwischen Unternehmensstandorten
Bei Einsatz von Speditionen als Eingangsrechnungen
Durch Auslieferung an den Kunden
Abholung vom Lieferanten
Transporte zwischen Unternehmensstandorten
Frachtkosten fallen immer an, unterschiedlich ist
jedoch die Form der Weiterbelastung:
Kundenpreis wird inklusive Fracht ausgehandelt; für
den Kunden ist der Frachtanteil nicht sichtbar
Ware und Fracht werden explizit ausgehandelt und
abgerechnet
Typisch beim Einsatz von Speditionen (natürlich
sowieso bei eigenem Fuhrpark) ist, dass
Frachtsätze im Vorwege vereinbart werden, also vor
Eintreffen der Frachtrechnung bekannt sind
Frachtrechnungen und Warenrechnungen getrennt
eintreffen (Ware vom Lieferanten, Frachten von der Spedition) und somit eine
disjunkte Zuordnung von Frachten zur Ware erfolgen muss
Angesichts der Bedeutung des Frachtanteils zeitliche
Verzögerungen der Einbuchung massiven Einfluss auf das monatliche
Betriebsergebnis ausüben
Ziel einer Lösung muss also einerseits sein, den
Frachtanteil der Ware möglichst korrekt zu ermitteln und andererseits die
Bewertungen zeitnah zu ermöglichen sowie Rückstellungen für noch ausstehende
Frachtbelastungen (Frachteingangsrechnungen, interne Frachtbelege)
ergebniswirksam einzustellen.
Die Vor
[...]


---

## Einrichten des Events dbrexp_schedule

Einrichten des Events
dbrexp_schedule
Sie können das Ereignis „dbrexp_schedule“ über Sybase
Central oder in Referenz-ERP einrichten. Dieses Ereignis sorgt zum einen für die
Überwachung der laufenden Replikation ([RINFO] in Referenz-ERP) und regelt den
Nachrichtentransport bei Verwendung einer FTP-Verbindung.

---

## Events für Beleg-Mailversand

Events für Beleg-Mailversand
Systempflege
Sonstige
Event-Manager
Je nachdem wann Sie die zu versendenden Rechnungen an
den Mailserver schicken wollen, können Sie mit dem Direktsprung
[EVT]
– Events ein Event einrichten, das eine
der unten aufgeführten Eventprozeduren aufruft.
Erstellen Sie einen Zeitplan für dieses Event, das je
nach gewünschtem Intervall anliegende Rechnungen per Mail versendet.
•
„AMIC_EVT_E_BELEGMAILER()“ bzw. eine private Ableitung davon

---

## Formulararchiv löschen

Formulararchiv löschen
Es werden die Daten in folgenden Tabellen
gelöscht:
BelegVersand
Formulararchiv

---

## Frachtsperren

Frachtsperren
Es gibt nur wenige Gründe, die dazu führen können,
dass eine Fracht abweichend vom Standard nicht berechnet wird.

---

## Frachttabellenzuordnungen

Frachttabellenzuordnungen
Nebenbuchhaltungen
Frachtverwaltung
Frachttabellen
[FRA]
Ändern
Frachttabellenzuordnung
Eine Frachttabelle kann einer Kombination von
Frachtklasse
,
Frachtgruppe
und
Versandart
zugeordnet werden.
Feld
Bedeutung
Frachtklasse
Frachtklasse
aus dem
      Kunden
Frachtgruppe
Frachtgruppe
aus dem
      Artikel
Versandart
Versandart für diese
      Zuordnung
Sperre
Hier
      kann eine Sperre eingetragen werden, die für diese Zuordnung
      gilt.
Gültig ab
Gültigkeitsbeginn
Gültig bis
Gültigkeitsende

---

## Funktion Freie Tourzuordnung

Funktion Freie Tourzuordnung
Mit der freien Tourzuordnung kann eine vorhandene Tour
zum markierten Datensatz zugeordnet werden.

---

## Funktion Tourplanung

Funktion Tourplanung
Mit der Funktion Tourplanung kann eine Tourzuordnung
aufgehoben werden oder eine Tour zugeordnet werden. Es kann zwischen
automatischer und manueller Tourzuordnung gewählt werden.

---

## Grundlegende Programmelemente

Grundlegende Programmelemente
Zu Beginn der Einrichtung sind die SPA einzugeben:
Mit Frachtermittlung aktiv wird die Frachtermittlung
eingeschaltet
Die automatische Frachtermittlung wird hiermit
aktiviert; ansonsten ist nur eine manuelle im Vorgang möglich, hierauf wird
später eingegangen
Als Default Frachtvariante wird hier die gewünschte
eingetragen; auf die Bedeutung wird später eingegangen
Frachten werden häufig im Vorgang nicht skontiert,
dann ist „Nie“ einzutragen. Alternativ erfolgt die Skontierung entsprechend der
Ware oder immer
Obige Möglichkeiten bestehen auch bei kalkulatorischen
Frachten
Die Einrichtung der erforderlichen Parameter erfolgt
im Abschnitt
Frachtverwaltung
:
Zur Lösung des Frachtproblems sind alle Programmpunkte
erforderlich. Darüber hinaus sind folgende Stammdaten betroffen:
Versandarten
Kundenstamm
Artikel
Lagerstamm
Eine
Frachtvariante
ist quasi eine Überschrift
für eine Frachtenabwicklung und besteht aus Nummer und Text:
Es sind die (Fracht-)
Gebiete
festzulegen, für
die später Frachten ermittelt werden sollen. Auch hier sind lediglich Nummer und
Bezeichnung erforderlich. Die GTB Nummer spielt mittlerweile keine Rolle
mehr:
Über
Frachtzonen
werden später
Frachtbelastungen zugeordnet:
Es wird eingegeben:
Die (frei wählbare) Nummer der Frachtzone, eine
Bezeichnung und der Matchcode
Die Frachtzone wird mit der (Fracht-) Variante (s.o.)
verknüpft. In unserem Beispiel wird davon ausgegangen, dass immer die gleiche
Variante eingesetzt wird!
Für die Fahrt von einem Gebiet zum anderen fallen
Frachten an. Im
Entfernungswerk
wird eingetragen:
Entfernung und Frachtzone sind später entscheidende
Faktoren für die Kosten­er­mitt­lung. Auch hier wird die gleiche
Variante für alle Relationen eingesetzt.
Frachttexte
werden bei der Zuordnung der
Frachttabellen verwendet:
In den
Frachttabellen
werden die entscheidenden
Parameter der Frachtkosten­ermitt­lung abgelegt:
Nummer
Numerische Identifikation der
Tabelle
Bezeichnung
Inhaltlic
[...]


---

## LOAD

LOAD
Syntax
LOAD;
Insert into (feld,feld,...) values (%s)
DATEN
.
.
.
LOAD;
Purpose
Beladen einer Tabelle.
Anwendung
Kommandodatei
Berechtigung
Alle Anwender
Siehe auch
IDENTLOAD
,
READ
,
DBFLOAD
Beschreibung
Um ganze Tabellen von einer Datenbank in eine andere
Datenbank zu transportieren, und um nicht jedes Mal das gesamte Insert
-Statement mitzuschleppen, wurde beschlossen, nur in die erste Zeile das Insert
- Statement zu schreibe ( ohne Zeilenumbruch) und in die Folgezeilen die Daten
zu belassen. Durch das Schlüsselwort LOAD erkennt das System, dass in der Folge
eine so aufgebaute Datenstructur folgt und kann somit im Programm das
eigentliche Statement zusammenbauen.
Derartige Dateien können mit einem Utility - das
unter OSQL unter F8 zu finden ist – erstellt werden.
Beispiel
LOAD;
insert into FIBUVORGKLASSE(
FiBuV_Klasse,FiBuV_KlBezeich, FiBuV_KlBeaKennz,fibuv_klKurzBez) values (%s)
1,'Zahlungsverkehr Banken',0,'ZA'
2,'Ausgangsrechnung',0,'AR'
3,'Ausgangsgutschrift',0,'AG'
4,'Eingangsrechnung',0,'ER'
5,'Eingangsgutschrift',0,'EG'
6,'Sonstige Belege',0,'SO'
7,'Restposten',0,'RP'
8,'Skonto',0,'SK'
9,'Ausbuchungen',0,'AB'
10,'Wechselerfassung',0,'WE'
11,'Kursgewinn/Kursverlust',0,'KD'
12,'Jahreswechsel',0,'JW'
13,'Rohwarenzugang',0,'RZ'
14,'Rohwarenausgang',0,'RA'
15,'Eröffnungsbuchung',0,'EB'
16,'Teilzahlung',0,'TZ'
17,'Interne Umbuchung',0,'IU'
18,'Kostenstellenumbuchung',0,'KU'
19,'Scheckeinreicher',0,'SE'
LOAD;

---

## Mailserver für Beleg-Mailversand

Mailserver für Beleg-Mailversand
Für den Belegversand via E-Mail ist ein SMTP-Server
nötig. Dieser kann auf unterschiedliche Weise bereitgestellt werden:
1.
SMTP-Server über Exchange
2.
mx-Record über Kerio
3.
Öffentlicher E-Mail Provider
SMTP-Server über Exchange
Einrichtung eines SMTP-Servers über die Microsoft
Exchange-Software und entsprechender Hardware mit eigener Domain. Diese Art der
Einrichtung kann optimal für viele Versand-, sowie Empfangsaufgaben konfiguriert
werden.
mx-Record über Kerio
Voraussetzungen:
•
Kerio Connect
Packet
•
Eine
Domain
•
mx-record für den
entsprechenden Server
•
1
User (für reinen Belegmailversand)
•
80GB
freien Speicher (für langfristige Verwendung)
•
Eine
entsprechende Installation und Konfiguration der Kerio-Software und Hardware
(z.B. Router)
Die Erledigung von
Massenversand kann mit dieser Art der Einrichtung erreicht werden.
Öffentlicher E-Mail Provider
Bei öffentlichen Providern kann man sich einfach
registrieren und den angebotenen SMTP-Server des Providers nutzen.
Hierzu ist allerdings zu sagen, dass diese Provider
Vorkehrungen gegen SPAM- / Massenmailversand getroffen haben. Diese können
gerade im Bereich des Belegmailversands zu großen Problemen führen. Zum Beispiel
schränken Sende-Limits den Versand von E-Mails ein. Diese Limits können sich von
Provider zu Provider u.U. sehr stark unterscheiden. Auch gibt es
unterschiedliche Limitierungen bei kostenfreien und kostenpflichtigen
Registrierungen bei den öffentlichen Providern.
Bitte informieren Sie sich gründlich im Vorfeld bei
dem Provider Ihrer Wahl über diese Limits und Ihre Möglichkeiten zur
Einflussnahme.

---

## Manuelle Frachten

Manuelle Frachten
Frachten können manuell im Anschluss an die Erfassung
einer Warenposition erfasst werden.
Nummer oder Text
Auswahl eines Frachtsatzes. Wählen Sie hier den für
diesen Fracht gültigen Satz aus. 0 ist die Standardeinstellung für eine komplett
manuell erfasste Fracht.
Frachtgruppe
Wird nur angezeigt – die
Frachtgruppe des Artikels
Erlöskennziffer
Erlöskennziffer auf die die Frachtgebucht werden soll
– 0 = die gleiche Erlöskennziffer wie der Artikel
Kostenstelle
Hier kann eine von der Warenposition abweichende
Kostenstellennummer für die Fracht angegeben werden.
0 = es wird die
Kostenstellennummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenstellen-Lizenz
aktiviert ist.
Kostenträger
Hier kann eine von der Warenposition abweichende
Kostenträgernummer für die Fracht angegeben werden.
0 = es wird die
Kostenträgernummer der Warenposition übernommen
Dieses Erfassungsfeld steht
nur zur Verfügung, wenn der Steuerparameter
Kostenträgerrechnung
angeschlossen
aktiviert ist.
Kostenobjekt
Hier kann eine von der Warenposition abweichende
Kostenobjektnummer für die Fracht angegeben werden.
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
Ja – Fracht wirkt auf den Einzelpreis des Artikels pro
Mengeneinheit und wird dann erst mit der Menge multipliziert
Frachtformel
Frachtformel siehe auch in den
automatischen Frachten
Prozentsatz
Prozentsatz der Fracht (bei prozentualen Frachten)
Preis/Satz
Frachtbetrag (bei Frachtsatz, der nicht prozentual
ist)
Preiseinheit
Ebendies
Bezugsmenge
Ebendies
Bezugswert
Wert auf den sich die Fracht beziehen wird
Betrag
Wird nur angezeigt: Frachtbetrag
Steuer
Wird nur angezeigt: Steuerbetrag
Skontierfähig
Ja/nein
Offen
Wird nur angezeigt: wird die
[...]


---

## Masken-Funktionen der MapsTourenplanung

Masken-Funktione
n der
MapsTourenplanung
Buttons
Auf der Maske befindet sich rechts oben eine
Stationsliste der gewählten Wegpunkte. Diese lassen sich mit den Buttons „oben“
und „unten“ verschieben.
Ziel gleich Start
Die Voreinstellung dieses Hakens erfolgt durch das
Profil. Mit Hilfe dieses Kennzeichens kann erreicht werden, dass der erste Punkt
der Liste zugleich als Zielpunkt der Tour angesetzt wird.
Ziel fixieren
Die Voreinstellung dieses Hakens erfolgt durch das
Profil. Wird dieser Haken gesetzt, so wird der letzte Punkt der Liste der
Zielpunkt und wird bei einer evtl. Optimierung als solcher berücksichtigt.
Streckenanzeige
Hier wird die Gesamtstrecke der Tour angezeigt.
Karte
Die Google-Maps-Karte wird stets nach einer Änderung
der Stationen neu angezeigt. Mit Hilfe des Maus-Scrollrades kann in die Karte am
Maus-Zeiger-Punkt hinein- bzw. herausgezoomt werden.

---

## Mehrfachteildisposition

Mehrfachteildisposition
Mit der Funktion Mehrfachteildisposition können aus
einer Auswahl von Vorgängen Teilmengen übernommen werden: Hierzu wird die
entsprechende Menge in der Spalte Menge eingetragen.
Die Spalten rechts der Mengenspalte dienen der Anzeige
von Informationen.
Mit
STRG +
A
in der Datentabelle der Mehrfachteildisposition werden die Restmengen
der Positionen übernommen.
Mit
F9
werden die Daten übernommen, sprich die Mengen aus dem jeweiligen Vorgang werden
teildisponiert.
Hinweis:
Eine Mehrfachteildisposition von Angeboten mit
Sortimentslager ist nicht möglich. Angebote mit Sortimentslager werden in der
Mehrfachteildisposition nicht angezeigt. Alternativ kann eine
Standardteildisposition durchgeführt werden (siehe
Standard-Teildisposition
).

---

## Sperre in der Frachttabellenzuordnung

Sperre in der Frachttabellenzuordnung
In der Frachttabellenzuordnung kann eine Sperre
eingerichtet werden

---

## Standard-Teildisposition / Mehrfachteildisposition

Standard-Teildisposition /
Mehrfachteildisposition
Hier finden Sie die Erläuterungen zur
Standard-Teildisposition
und
Mehrfachteildisposition
.
Es gibt in Referenz-ERP auch eine
„Schnelle
Teildisposition“
, die im Abschnitt
Artikelerfassung
in dieser Hilfe
erläutert wird.

---

## Standard-Teildisposition

Standard-Teildisposition
Mithilfe der Standard-Teildisposition ist es möglich,
Artikelpositionen aus anderen Vorgängen teilweise zu übernehmen. So können
einzelne Positionen aus verschiedenen vorgelagerten Vorgängen, z.B. aus
verschiedenen Aufträgen, manuell in z.B. einen Lieferschein übernommen werden.
Bei der Anwahl der Funktion werden alle offenen
Vorgänge mit ihren Positionen angezeigt; die für die Standard-Teildisposition
zur Auswahl stehen. Es können Bestellungen, Angebote und Aufträge ausgewählt
werden.
Die gewünschte Position wird ausgewählt. Danach wird
abgefragt, ob die Position in vollem Umfang übernommen werden soll.
Im
Feld „jetzt disponiert“
besteht eine Eingabemöglichkeit
(Einschränkungen s.u.), wenn keine Nebenbuchhaltung angesprochen wurde. Bei
dieser echten Teildisposition ist die Maske mit ,,
Standard-Teildisposition / Manuelle
Disposition
" überschrieben.
Im Feld „Preis“
kann ein abweichender Preis eingegeben werden.
Mit der Bestätigung des vollen Betrages wird die
Position in vollem Umfang übernommen, bei Eingabe eines kleineren Betrages
verbleibt im Quellvorgang eine Restposition und die Teilposition wird
übernommen. Die Eingabe einer Menge größer als der Ursprungsmenge ist nicht
möglich, wenn der Steuerparameter 32 „Über-Disposition zulässig“ auf „Nein“
steht.
Artikelzeilen, die anhängende Folgezeilen
(automatische Zu-/Abschläge, etc.) aufweisen, die einer Gebindeberechnung
unterliegen oder aus Kontrakten abbuchen, können nur vollständig umgewandelt
werden. In diesem Fall wird die Mengeneingabe unterbunden. Die Maske ist in
diesem Fall mit ,,
Standard-Teildisposition /
Positions-Disposition
" überschrieben.
Teilumgewandelte Vorgänge sind anschließend für
Korrekturen gesperrt.
Das Feld „Ziel-Lagernummer“ ist nur dann sichtbar,
wenn es sich bei der Quellposition um ein Angebot mit Sortimentslager handelt
(siehe
Standard-Teildisposition
von Angeboten mit Sortimentslager
).
Hinweis:
Das Lieferdatum kann aus Angeboten und A
[...]


---

## Stücklistenkomponenten

Stücklistenkomponenten
Es kann in Stücklisten eine Einstellung geben, dass
Stücklistenkomponenten nicht einzeln mit einer Fracht belegt werden dürfen.

---

## Tabelle zur Version: 8.3.2309.1

Tabelle zur Version: 8.3.2309.1
ID
Releasenote - Titel
Geprüft
33923
Anpassung für Formulartyp 201
33940
Rosi-Export
33976
Funktion Verpostung per Outlook entfernt
34050
Ertragsschätzung in der Feldbearbeitung
34062
Vermailung: Gelöschte Versandprofile
34088
Stammdatenpflege Funktionalität "Alle Ändern"
34098
Supportersitzung mit Teamviewer
34127
Geschäftsjahr und Schaltjahr
34132
Servicepack 27.005 für Branchen-ERP-Etikettendruck
34171
Crystal Report Druckerauswahl
34176
Rückbau-Funktionen Lieferanten
33909
PDF-Verarbeitung
34156
Lange Passwörter im Versandprofilstamm
33768
eClearing Auszifferung anzeigen
33911
Datev Export verbesserte Fehlermeldung
34139
FiBu Datenübernahmen im Excel XLSX-Format
34140
Fibu Datenübernahme im Excel CSV-Format
34214
FiBu Datenübernahme im XML-Format
34254
Datenübernahme Ustid
33277
Inventurstamm
34054
Bezahlterminal: Neuer Parameter
Authentifizierung
34124
Rabattanzeige auf dem externen Kassendisplay
34005
Kontraktstamm: Feld "Standardkontraktvariante"
33887
Artikelabhängige THG Werte in Anbauland / Region
33017
Produktion: Itembox für Zu- und Abgangsartikel
33122
Produktion: Darstellung der Eingabemaske
33898
Produktion: Feld Artikelbezeichnung
32610
Import und Export der Rohware-Einrichtung
33394
Periode ändern mit Tagesdatum
34048
Ref2 und Ref3 bei Rohwaredefinitionen
33716
Interne Änderung bei den Stammdaten für die
      Preisfindung
33806
Währungskurse
33889
Kundenstamm Speichern unter
34095
Artikelverpackung
34121
CO2 Artikelstammpflege
34134
Rezepturgruppe 0
34202
Artikelstammtexte
33722
Wareo: Vorgangsleichen löschen
33839
Betreff-Zeile bei Mailversand von Vorgängen
33840
Gebindebehandlung bei Mengenkorrektursperre per
      Arbeitsregel
33914
Ursprungsland in Intrastat Varianten
33973
Protokoll FIBU-Übertrag erweitert um
    Artikelnummer
34076
SPA 503 um neue Optionen erweitert

---

## Tabelle zur Version: 8.3.2311.10

Tabelle zur Version: 8.3.2311.10
ID
Releasenote - Titel
Geprüft
34413
Auswahlliste Vermailung
34430
Drucker-Schachtsteuerung
34499
Mailversand
34307
PDF-Engine (PDF-Erzeugung-Bibliotheken)
erneuert.
34004
Zählmenge wird auch vor der Bewertung angezeigt
34447
Artikelstamm: Mengeneinheitengruppe
34509
Tastatursteuerung: Warenbewegung-Addon

---

## Tabelle zur Version: 8.3.2310.27

Tabelle zur Version: 8.3.2310.27
ID
Releasenote - Titel
Geprüft
34298
Crystal Report: Datumsfilter
34278
Mailversand Finanzbuchhaltung: Anzeige von
    Grafiken
34337
OPVerwaltung Teilzahlung

---

## Tabelle zur Version: 9.0.2401.4

Tabelle zur Version: 9.0.2401.4
ID
Releasenote - Titel
Geprüft
35352
Es werden Frachtenzeilen korrekt aktualisiert und keine
      weiteren Frachtzeilen auf der Belegpositionsmaske

---

## Tabelle zur Version: 9.0.2402.8

Tabelle zur Version: 9.0.2402.8
ID
Releasenote - Titel
Geprüft
36020
F2-Suche
36084
Fälligkeitsdatum des Rechnungsbetrages in XRE
36109
PDF: Merge von Pdf-Dateien
36168
Eingabe Multilinefelder über AIS
36096
Mailversand Duplikate
35828
Elster 41.2.4 für 2025
35653
Fehlende Unterscheidung zwischen Markt- und Tresen-
      Kasse bei Zahlungsabbruch hinzugefügt
35850
Fehler in der Index.xml des DSFinV-K-Exports
    behoben
35994
Kontraktdruck: Artikelzeile mit Sollmenge
36126
Nullpointer Problematik bei behoben
35992
Stornierung von Rohwarebelegen
36001
Von Branchen-ERP reservierte Anwendungsformatbereiche
      weggeschützt
36059
Fallback auf Standard-Mailadresse bei eRechnung
36121
Skonto Basisbetrag korrekt herangezogen
36082
eRechnung Umwandlung
36222
eRechnung Adressaufbereitung

---

## Tabelle zur Version: 9.0.2501.8

Tabelle zur Version: 9.0.2501.8
ID
Releasenote - Titel
Geprüft
37460
Itembox 2.0: Verhalten bei Verwendung ITEM1 und
      ITEM2
37462
Report RLF
37497
Feld Kassensitzungsnummer von wieder verfügbar
36576
Archiv-Mail Versand Maske EPAs korrigiert
37605
Aktuelle Warenbestände nicht aufrufbar aus der
      Warenpositionsmaske in einem Beleg

---

## Tourverwaltungsmaske

Tourverwaltungsmaske
Zu jeder Tour lassen sich verschiedene Gültigkeiten
erfassen, die unterschiedliche Stationen beinhalten können. Wenn eine Gültigkeit
zum Bearbeiten geöffnet wurde, können die Daten der Zeiträume mit den Funktionen
Gültigkeit einfügen
,
Gültigkeit bearbeiten
und
Gültigkeit löschen
in einem neuen Fenster
bearbeitet werden.
Die Funktion
Ladeliste n. Tag
ist in der
Tourverwaltung
genauer
beschrieben.
Maskenfelder der Tourverwaltung:
Feld
Bedeutung
Tour
      Nummer
Dieses Feld wird automatisch mit der
      nächsten freien Nummer vorbelegt, aber es kann auch eine eigene Nummer
      vergeben werden.
Bezeichnung
Geben sie der Tour eine
      Bezeichnung.
Wochentag
Geben sie den geplanten Wochentag
      der Tour an.
Tour
      gesperrt
Dies ist ein setzbares
      Sperrkennzeichen, um eine Tour zu deaktivieren, ohne sie gleich zu
      löschen.
Datentabelle: Registerkarte „Allgemein“
Feld
Bedeutung
Gültigkeiten
Hier
      werden die Gültigkeiten für die danebenstehende Stationsliste angezeigt.
      Auf sie kann geklickt werden um die für den jeweiligen Zeitraum gültige
      Stationsliste anzuzeigen.
Stationsliste
Feld
Bedeutung
Nr.
Geben sie die Nummer der Station
      an.
Prio
Hier
      können sie der Station eine Priorität zuweisen.
Sperre
Dies
      ist ein temporär zu setzendes Sperrkennzeichen, um einzelne Stationen
      kurzfristig zu deaktivieren.
Kommentar
Ein
      Kommentar zur Station.
Kundennummer
Tragen sie die Kundennummer
      ein.
Adresse
Hier
      wählen sie aus einer der am Kunden hinterlegten Adresse die aus, an die
      geliefert wird.

---

## Verwendung des Mailversands

Verwendung des Mailversands

---

## Voraussetzungen für den Mailversand

Voraussetzungen für den Mailversand

---

## Vorgangsformen ohne Teildisposition

Vorgangsformen ohne
Teildisposition
Bei einigen Vorgangsformen und Gegebenheiten kann
keine Teildisposition vorgenommen werden, es kann nur die gesamte Menge
übernommen werden.
Das entsprechende Feld innerhalb der Eingabemaske
bleibt Blau markiert eine Eingabe ist also nicht möglich.
Nicht möglich ist die Teildisposition in folgenden
Fällen:
•
Bei Einzelrabatten
•
Bei Rabatten
•
Bei Zu/Abschlägen nur wenn der
Steuerparameter 165 „Teildispo mit Zu-/Abschlägen zulässig“
auf
JA gesetzt ist.
•
Bei Kontrakten
•
Bei Objekten ab Lieferschein (vorher ist Teildisposition zulässig)
•
Bei Partien
•
Bei Leergut

---

