# Waage, Annahme & Hofliste — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (152 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## Belegfluss

Belegfluss
Der Belegfluss wurde um ein Feld für die Belegart (nur
Finanzbuchhaltung) erweitert. Für die Belegart SO-Belege wird das
Soll/Haben-Kennzeichen ausgewertet.  Achtung: Der Datenbanktyp des Feldes
"SollHaben" wurde von "CHAR" auf "integer" geändert. Private Funktionen, die das
Feld "SollHaben" bereits verwenden, müssen angepasst werden.
Releasenote Kategorie:
Ticket: 715736[33022]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Archiv Belegfluss
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33022, 715736

---

## Vorzeichen bei rechnungebearbeitung

Vorzeichen bei rechnungebearbeitung
Der Bruttowert der Fremdwährung wurde in der
Auswahlliste Rechnungsbearbeitung mit falschem Vorzeichen angezeigt. Dieser
Fehler wurde behoben.
Releasenote Kategorie:
Ticket: 716315[33117]
Version: 8.3.2211.30
Datum: 25.11.2022
Anwendung: Rechnungsbearbeitung
Variante: Standard
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2211.30, 33117, 716315

---

## Belegfluss erstellen Finanzbeleg

Belegfluss erstellen Finanzbeleg
Wurde vom Belegfluss aus ein Beleg erstellt, der
sowohl Netto als auch Brutto Beträge enthält, wurde der Wechsel von Netto auf
Brutto nicht erkannt. Dieses Problem wurde behoben.
Releasenote Kategorie:
Ticket: 714269[33157]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: Belegfluss [BF]
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33157, 714269

---

## Auftragskorrektur: Brutto-Belege

Auftragskorrektur: Brutto-Belege
Wurde ein Beleg als Bruttobeleg angelegt und davon
teildisponiert, war die Auftragskorrektur nicht möglich, da die entsprechenden
Stornobelege als Netto-Belege definiert wurden und keine Teildisposition aus dem
Ursprungs-Bruttobeleg zuließen. Dies wurde nun korrigiert.  Die
Auftragskorrektur erstellt nun einen Brutto-Beleg zur Restausbuchung aus einem
Brutto-Beleg.
Releasenote Kategorie:
Ticket: 721934[33697]
Version: 8.3.2304.28
Datum: 28.04.2023
Anwendung: Auftragskorrektur
Variante: -
Funktion/Report: [AUK]
Weitere
Informationen
Tags:
Releasenote, 8.3.2304.28, 33697, 721934

---

## Kopieren eines Vorgangs mit Teildispositionskennzeichen

Kopieren eines Vorgangs mit Teildispositionskennzeichen
Bei der Erzeugung einer Kopie eines Vorgangs mittels
der Funktion 'Kopieren' wurde das Teildispositionskennzeichen 'V_KennzTeilV' mit
in die Kopie übernommen. Dieses wurde nun unterbunden.
Releasenote Kategorie:
Ticket: 724602[34094]
Version: 8.3.2308.18
Datum: 18.08.2023
Anwendung: AGB,BAB,AUB,BSB,LIB,ELB,REB,ERB,GUB,EGB
Variante: alle
Funktion/Report: Kopieren
Weitere
Informationen
Tags:
Releasenote, 8.3.2308.18, 34094, 724602

---

## Artikelverpackung

Artikelverpackung
Bisher wurde beim Löschen eines
Artikelverpackung-Stammdatensatzes [AVP] nur ein Löschkennzeichen gesetzt. Jetzt
wird kein Löschkennzeichen mehr gesetzt, sondern der Datensatz wird direkt aus
der Datenbank entfernt.
Releasenote Kategorie:
Ticket: 0[34095]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [AVP]
Variante: -
Funktion/Report: F7 - Löschen
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34095, 0

---

## MDE: Fokus

MDE: Fokus
Der Scanner Webdienst übergibt das Fokuskennzeichen an
die Android Scanner App.
Releasenote Kategorie:
Ticket: 0[35130]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: MDE Scanner
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35130, 0

---

## Kopie von VorgangAddOns

Kopie von VorgangAddOns
VorgangsAddons werden nun auch in den neuen Beleg
kopiert, wenn aus der Auswahlliste die Funktion "Teildisposition ..." aufgerufen
wird und in der Quellvorgangs(Unter-)klasse das Kennzeichen "AddOns kopieren"
aktiv ist.
Releasenote Kategorie:
Ticket: 730400[35189]
Version: 9.0.2401.3
Datum: 07.06.2024
Anwendung: Formularzuordnung [FRZ]
Variante: Standard
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 9.0.2401.3, 35189, 730400

---

## Waage: AeinsWiege-UDP-Protokoll-Erweiterung

Waage: AeinsWiege-UDP-Protokoll-Erweiterung
Das UDP-Protokoll wurde darauf hin erweitert, dass es
nun am Ende auf eine Send-Anweisung ohne eine leere Expect-Anweisung geben
kann.
Releasenote Kategorie:
Ticket: 0[35328]
Version: 9.0.2402.1
Datum: 30.09.2024
Anwendung: -
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.1, 35328, 0

---

## Druckerstamm: Kennzeichen "Ohne ASCII Konvert."

Druckerstamm: Kennzeichen "Ohne ASCII Konvert."
Im Zusammenhang mit dem Feature "Queue / Datei" und
dem Druck in eine Datei wurde offenbar das Kennzeichen "Ohne ASCII Konvert."
nicht berücksichtigt. Das führte dazu das die Umlaute der üblichen
Sonderbehandlung im ASCII-Druck-Umfeld unterlagen, was aber im "Datei-Druck" zu
Fehlern führt, da dieser die Umlaute schon richtig erzeugt. Durch den nun
funktionierenden Schalter lässt sich die "Sonderbehandlung" abstellen, mit dem
Effekt das die Umlaute unverändert und richtig durchgeleitet werden. Zusätzliche
Erläuterung sei erwähnt:Wenn z.B. in eine Spool-Datei (Notepad) / auf ein Fax
gedruckt wurde, wurden gewisse Zeichen (z.B. Umlaute) nicht korrekt dargestellt.
Hierfür ist dieses Kennzeichen eingerichtet. Wird dieses auf "Ja" gestellt,
wird die zusätzliche Zeichenkonvertierung ausgeschaltet und auch diese
Sonderzeichen werden korrekt dargestellt. Die "Defaulteinstellung" ist
"Nein", das Verhalten bleibt wie bisher. Bei normalen Druckern sollte die
Voreinstellung "Nein" beibehalten bleiben.
Releasenote Kategorie:
Ticket: 740321[35876]
Version: 9.0.2402.4
Datum: 06.12.2024
Anwendung: Druckerstamm
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 9.0.2402.4, 35876, 740321

---

## Branchen-ERP Etikettendruck export Archivkennzeichen

Branchen-ERP Etikettendruck export Archivkennzeichen
Beim Export von Branchen-ERP-Etikettendruck Reporten
wurde das Archivierungskennzeichen grundsätzlich nicht mit exportiert. Jetzt
wird bei privat erstellten Reporten das Kennzeichen mit übertragen.
Releasenote Kategorie:
Ticket: 740495[35965]
Version: 9.0.2501.5
Datum:
Anwendung: ETIDR
Variante: --
Funktion/Report: --
Weitere
Informationen
Tags:
Releasenote, 9.0.2501.5, 35965, 740495

---

## Vermehrungsvertrag Owaage

Vermehrungsvertrag Owaage
Wenn in der Online-Waage ein Artikel per
Vermehrungsvertrag bestimmt und gesucht wurde, so wurde bislang das
Löschkennzeichen des Artikelstamm nicht berücksichtigt. Dies Verhalten ist nun
abgeändert worden.  Des Weiteren ist die Itembox IB_KU_Vertrag_Nu um die
ArtikelId und Anerkid in der Returnliste erweitert worden.
Releasenote Kategorie:
Ticket: 739549[36878]
Version: 9.0.2502.5
Datum: 15.10.2025
Anwendung: Owaage
Variante: Hofliste
Funktion/Report: Vermehrungsvertrag Auswahl
Weitere Informationen
Tags:
Releasenote, 9.0.2502.5, 36878, 739549

---

## Lagerwechsel in der Online Waage

Lagerwechsel in der Online Waage
Beim Ändern der Lagernummer innerhalb eines
Waagensatzes wurde der Lagerwechsel nicht übernommen, wenn das Feld Lagernummer
nicht aktiv verlassen wurde. Dies trat insbesondere dann auf, wenn der Benutzer
den Cursor noch im Feld hatte und direkt F11 – Wiegung abschließen ausführte. In
solchen Fällen blieb der Artikel weiterhin auf dem ursprünglichen Lager
gespeichert. Dadurch kam es zu Inkonsistenzen zwischen:  dem Lager des
Artikels (z.B. weiterhin Lager 1) und dem Lager, das im Waagensatz hinterlegt
war (z.B. Lager 2).  Bei der anschließenden Vorgangserzeugung wurde das
Lager des im Waagensatz hinterlegten Artikels verwendet – und nicht das Lager
des Waagensatzes selbst. Da der Artikel durch das nicht verlassene
Lagernummernfeld nicht aktualisiert wurde, blieb dessen ursprüngliches Lager
bestehen und bestimmte somit das Lager des erzeugten Vorgangs.  Das
Systemverhalten wurde angepasst: Der Lagerwechsel des Artikels wird nun auch
dann korrekt übernommen, wenn das Feld Lagernummer nicht aktiv verlassen wurde.
Wird der Vorgang über F11 – Wiegung abschließen abgeschlossen, wird der Artikel
zuverlässig auf das Lager des Waagensatzes aktualisiert.  Auswirkung:
Verhindert Inkonsistenzen zwischen Artikel- und Waagensatzlager. Stellt sicher,
dass Vorgänge immer mit dem tatsächlich gültigen Lager erzeugt werden.
Releasenote Kategorie:
Ticket: 751599[38897]
Version: 9.0.2502.9
Datum:
Anwendung: Hofliste
Variante: Hofliste
Funktion/Report: Wiegung abschließen
Weitere
Informationen
Tags:
Releasenote, 9.0.2502.9, 38897, 751599

---

## Änderung des Brutto/Netto-Kennzeichens

Änderung des Brutto/Netto-Kennzeichens
In der Marktkasse im Rahmen der Funktion
Speichern unter
und unter Umständen auch
in einem UFLD-Feld lässt sich das Brutto/Netto-Kennzeichen eines Vorgangs
ändern.
Diese Funktion ist mit Vorsicht zu verwenden, denn es
findet nicht immer eine verlustfreie Umrechnung der Beträge in Brutto oder Netto
statt.
Rundungsdifferenzen
Ist ein Beleg als Bruttobeleg erfasst worden, und soll
nachträglich als Nettobeleg gespeichert werden, so werden alle Beträge von
Brutto auf Netto unter Abzug des jeweils für die Position gültigen Steuersatz
umgerechnet. Das Ergebnis einer Umwandlung in einen Brutto-Beleg kann hier zu
Rundungsdifferenzen führen.
Beispiel für Rundungsdifferenzen:
Betrag Brutto sei 13€ - nach Umrechnung auf Netto bei
19% Steuer
⇨
10,92€ (gerundet)
Bei Rückrechnung mit 19% Steuer ergibt die Summe
11,99€
Absolute Rabatte/Zuschläge
Vorsicht ist auch geboten bei der Verwendung von
absoluten Rabatten. Diese werden nicht von Brutto in Netto gewandelt!
Aus diesem Grund wird empfohlen, in solchen
Konstellationen prozentuale Rabatte statt absoluten Beträgen zu verwenden.
Beispiel für Absolute Rabatte beim
Brutto/Netto-Wechsel:
Es wird eine Brutto-Rechnung mit dem Betrag von 119€
abzüglich 10€ absolutem Rabatt erfasst. Der Bruttobetrag ist 109€.
Wird diese Brutto-Rechnung nun z.B. in der Marktkasse
in einen Netto-Lieferschein gewandelt.
Nun wird gerechnet: 119€ abzüglich 19% Steuern = 100€
Abzüglich 10€ absolutem Rabatt (Dieser wird nicht umgerechnet!)
⇨
90€ ist nun der Nettobetrag.
Bei Umwandlung des Netto-Lieferscheins in eine
Brutto-Rechnung ergibt das 90€ + 19% Steuern
⇨
107,10€.

---

## Wiegungen raffen (EPA AH_WAAGE_RAFFUNG)

Wiegungen raffen (EPA
AH_WAAGE_RAFFUNG)
Bezeichnung
Standardwert
Erklärung
Sollen beim Raffen die Partien
      beachtet werden
Nein
adsad
Funktion für Raffen der
      Wiegungen
AMIC_WAAGE_RAFFEN

---

## Online Waage (EPA OWAAGE)

Online Waage (EPA OWAAGE)
Bezeichnung
Standardwert
Erklärung
Wiegenummer bei manuellen Wiegungen
      ausblenden
Ja
Die
      Wiegenummer kann zur Vereinfachung der Bedienung bei manuellen Wiegungen
      ausgeblendet werden.
Sollen die Aufträge komplett
      storniert werden (sonst ausbuchen)?
Nein
Wirksam für die
      Vorgangskopie.
Hat
      man sich hier für Ja entschieden, dann wird der Auftrag storniert (das
      bedeutet, er verschwindet aus dem System; es kann in keiner Form mehr auf
      ihn zugegriffen werden.).
Bei Nein wird die Menge des Auftrages auf
      Null gesetzt. Er bleibt im System erhalten.
Basiskategorie bei Auswahl nach
      Art/Sorte
0
Plan-, und Lieferdatum aus Waage
      ziehen
Nein
Bei
      der Vorgangserzeugung aus der Waage wird das Plandatum, so wie das
      Lieferdatum auf das Datum der Wiegung gesetzt.
Vorgang erzeugen: Belegdatum der
      Waage als Lieferdatum anstatt des Tagesdatums
Nein
Bei
      der Waage-Anwendung „Vorgang erzeugen“ wird im Lieferschein als
      Lieferdatum das Tagesdatum (Datum der Vorgangserzeugung) eingetragen. Es
      gibt die Möglichkeit, das Datum des Waagenbeleges auch als Lieferdatum im
      Lieferschein zu übernehmen. Dazu muss der EPA „Vorgang erzeugen:
      Belegdatum als Lieferdatum anstatt des Tagesdatums“ auf ‚JA’ gesetzt
      werden. Das ist vor allem dann sinnvoll, wenn aus Wiegungen erst einige
      Wochen später Vorgänge erzeugt werden.
Belegdatum bearbeiten
Nein
Setzt man diesen Einrichterparameter
      auf Ja, besteht die Möglichkeit, das Datum zu ändern.
Das
      Belegdatum wird mit dem aktuellen Datum (heute) vorbelegt. Es ist nicht
      das Tagesdatum/Vorbelegungsdatum welches man über den Direktsprung
[DAT]
setzen kann bzw. welches beim
      Start von Referenz-ERP mit dem Rechnerdatum vorbelegt wird. Dieses Tagesdatum
      ändert sich nämlich nicht, wenn man über Nacht in Referenz-ERP eingeloggt bleibt
      bzw. ist falsch belegt, wenn die Rechnereinst
[...]


---

## Wiegungen aufteilen (EPA WAAGE_LVSAUFTEILUNG)

Wiegungen aufteilen (EPA
WAAGE_LVSAUFTEILUNG)
Bezeichnung
Standardwert
Erklärung
Private LVS Aufteilen
      Funktion
amic_waage_lvsaufteilen

---

## Hofliste (EPA owaage71)

Hofliste (EPA owaage71)
Bezeichnung
Standardwert
Erklärung
Mandanten Wahl bei NEU
Letzter gewählter ...
Partievorerfassung
      zulassen
Ja

---

## Online-Waage-Lizenz (SPA 1032)

Online-Waage-Lizenz (SPA 1032)
Lizenz für die Online-Waage.

---

## DATEV Festschreibungskennzeichen übertragen(SPA 1061)

DATEV Festschreibungskennzeichen übertragen(SPA 1061)
Das Festschreibungskennzeichen wird standardmäßig
gesetzt. Dies bewirkt, dass der Empfänger diese Daten nicht ändern kann. Es kann
jedoch wünschenswert und notwendig sein, dass die übertragenen Belege vom
Empfänger bearbeitet werden müssen.
0: ohne Festschreibungskennzeichen
1: mit Festschreibungskennzeichen
Achtung:
Beim DATEV-Übertrag werden nur
gebuchte Belege exportiert und diese sind bekanntlich in Referenz-ERP nicht änderbar.
Dieses Verhalten wird durch diesen SPA
nicht
beeinflusst.

---

## Offline-Waage-Lizenz (SPA1101)

Offline-Waage-Lizenz (SPA1101)
Lizenz für die Offline-Waage.

---

## Automatische Verpackungs-/Bruttogewicht(SPA 158)

Automatische Verpackungs-/Bruttogewicht(SPA 158)

---

## Max. Netto-Abweichung von Vorgabe (Cent)(SPA 210)

Max. Netto-Abweichung von Vorgabe (Cent)(SPA 210)

---

## ReBuch-Sperre aus Quellvorgang übernehm.(SPA 273)

ReBuch-Sperre aus Quellvorgang übernehm.(SPA 273)
Bei Umwandlungen wird das Sperrkennzeichen für die
Übernahme des Vorgangs ins Rechnungsausgangsbuch bzw. Rechungseingangsbuch wie
folgt gesetzt (wenn es gesetzt ist, ist die Übernahme nicht
möglich):
gem. Unterklasse: das Kennzeichen wird aus der
Klasse/Unterklasse übernommen, wie es in der Zielklasse defaultmäßig vorbelegt
ist (FRZ/Formularzuordnung) aus der Quelle: das Kennzeichen wird aus dem
Quellvorgang in den Zielvorgang übernommen. setzen, n. löschen: das Kennzeichen
wird immer gesetzt für den Zielvorgang, in den umgewandelt wird.

---

## Waage, LKW-Nr. Zwang(SPA 379)

Waage, LKW-Nr. Zwang(SPA 379)
Ja: Vor der Wiegeerfassung muss als erstes eine
LKW-Nr. eingetragen werden

---

## Waage, Wiegeschein Druckzwang(SPA 402)

Waage, Wiegeschein Druckzwang(SPA 402)

---

## Produktion Partiezuordnungszwang Produkt(SPA 411)

Produktion Partiezuordnungszwang Produkt(SPA 411)
Nein: In der Produktionserfassung muss dem Produkt
keine Partie zugeordnet werden.
Artikel mit Partiezwang: Es muss in der
Produktionserfassung dem Produkt, bei dem das Partiekennzeichen hinterlegt ist,
eine Partie zugeordnet werden.
Alle Artikel: Es muss in der Produktionserfassung für
das Produkt immer eine Partie zugeordnet werden.

---

## Gefahrgutmesszahl per Netto(SPA 518)

Gefahrgutmesszahl per Netto(SPA 518)
Nein: Die Gefahrgutmesszahl wird aus dem Bruttogewicht
ermittelt.
Ja: Die Gefahrgutmesszahl wird aus dem Nettogewicht
ermittelt.

---

## Waage, Wiegen in der Vorgangserzeugung(SPA 615)

Waage, Wiegen in der Vorgangserzeugung(SPA 615)
Der Steuerparameter 615 „Waage, Wiegen in der
Vorgangserzeugung“ bestimmt ob aus der Vorgangserzeugung heraus gewogen werden
kann. Standardmäßig ist er vorbelegt mit Nein.

---

## Endpreis in Warenbewegung immer netto(SPA 684)

Endpreis in Warenbewegung immer netto(SPA 684)
Bei „Ja“ wird das Feld WabewEndpreis in der Tabelle
Warenbewegung immer netto geführt, auch wenn der zugehörige Vorgang als
Bruttovorgang angelegt wurde. Bei „Nein“ ist der Preist gemischt netto oder
brutto.
ACHTUNG eine Änderung des Steuerparameters
bewirkt keine Anpassung schon bestehender Warenbewegungen. Dieser
Steuerparameter sollte also nicht ständig geändert werden.

---

## Umwandlungssperre für MS Einträge bei Vollreplikation(SPA 895)

Umwandlungssperre für MS Einträge bei Vollreplikation(SPA 895)
Ist ein Beleg in eine Vollreplikationsumgebung noch
nicht abgearbeitet (also durch den Mandantenserver durchgelaufen), so darf
dieser Beleg nicht umgewandelt werden, da sonst Probleme im Partiebereich wie
auch im Kennzeichenbereich auftreten können.
Es kann dann passieren, dass bei
Umwandlungsbuchungen ganze Partiebewegungen nicht mit berücksichtigt werden und
dass in Rechnungen umgewandelte Lieferscheine sofort wieder freigegeben werden,
was zu Doppelbuchungen (zwei Rechnungen für einen Lieferschein) führt.

---

## Waagenmaske(SPA 906)

Waagenm
aske(SPA 906)
Wird zurzeit nicht ausgewertet

---

## LKW Vorbelegung an der Waage(SPA 916)

LKW Vorbelegung an der Waage(SPA 916)
Mit diesem Steuerparameter kann eingestellt werden, ob
bei der Kundeneingabe in der Waage die LKW Bezeichnung vorbelegt werden
soll.

---

## Waagenmasken mit dem Widget Navigator starten(SPA 918)

Waagenmasken mit dem Widget Navigator starten(SPA
918)
Mit diesem Steuerparameter kann eingestellt werden, ob
die Waagenmasken mit dem geänderten Layout per Widget Navigator gestartet werden
soll. Dazu wird der Steuerparameter 918 auf ja gestellt. Die Waagenmaske wird
nun mit dem neuen Überarbeitenden Standard Layout gestartet.

---

## Qualitätswerte erst ab der ersten Wiegung speichern(SPA 917)

Qualitätswerte erst ab der ersten Wiegung speichern(SPA
917)
Mit diesem Steuerparameter kann eingestellt werden, ob
die Qualitätswerte an der Waage erst ab dem Status „erste Wiegung“ gespeichert
werden soll. Im Standard werden die Qualitäten schon beim Status „Eröffnet“
gespeichert.

---

## Qualitätsverarbeitung in der Waage(SPA 932

Qualitätsverarb
eitung in der Waage(SPA 932
Einstellung
Bedeutung
Bis
      max 20 in der Waage ausschließlich
Dies
      ist die Standard Einstellung für den SPA. Dies bedeutet, dass die
      Erfassung der Qualitäten per Standard auf der Waagenmaske passiert mit den
      20 Qualitätsfeldern.
Über
      den Bereich Artbestandteil, beliebig viele Qualitäten
Die
      Tabellenform gestützte Erfassung wird angeschaltet.

---

## Archiv-Vorgänge mit Löschkennzeichen versehen?(SPA 937)

Archiv-Vorgänge mit Löschkennzeichen versehen?(SPA 937)
Standard : Nein
Damit werden u.a. beim Storno von Vorgängen die
zugehörigen Archiv-Vorgänge nicht mit Löschkennzeichen versehen, was praktisch
bedeutet, sie werden nicht gelöscht.

---

## Doppelte Vorgänge aus der Waage führen zur Sperrung(SPA 964)

Doppelte Vorgänge aus der Waage führen zur Sperrung(SPA 964)
Wird dieser Steuerparameter auf Ja gestellt, so wird
bei der Belegerzeugung abgeprüft, ob es schon ein Vorgang aus dem Waagensatz
erzeugt wurde. Ist dies der Fall so werden die Belege werden dann gesperrt.

---

## Waagenanbindungen

Waagenanbindungen

---

## Waagenanbindungen

Waagenanbindungen

---

## Waagenanbindungen

Waagenanbindungen

---

## Waagenanbindungen

Waagenanbindungen

---

## Archiveinträge löschen

Archiveinträge löschen
Archiv-Einträge können gelöscht werden.
Die Löschung erfolgt über das Setzen eines
Kennzeichens in der Formulararchiv-Relation. Ein so gelöschter Archiv-Eintrag
ist in den gängigen Archiv-Auflistungen nicht sichtbar.
Eine Archiv-Löschung kann rückgängig gemacht werden,
und zwar nur in der Variante
Formulararchiv-Administration
.
Eine endgültige Löschung per Benutzeroberfläche ist
vorerst nicht vorgesehen.

---

## Archiv-Manager Sonstiges

Archiv-Manager Sonstiges
Signieren durchstarten
JA/NEIN - Kennzeichen
Automatik-Profile
JA/NEIN - Kennzeichen
Automatik-Import
JA/NEIN - Kennzeichen
Anlagen-Zuordnung
Legt
      fest welche Gruppe den Anlagen zugeordnet wird.
Signatur-Importpfad
Legt
      den Pfad für Signatur-Importe fest.
Mandantenserver
      Intervall
Legt
      die Wartezeit in Sekunden fest in der Mandantenserver höchstens
      hintereinander Archiv-Importe ausführen soll. (Standard ist 2)

---

## Formulararchiv-Gruppen

Formulararchiv-Gruppen
Das Archiv ist um die Möglichkeit der Gruppierung
erweitert worden. Es können jetzt Archivelemente in einer Gruppe zusammengefasst
werden; diese Gruppe trägt eine Gruppennummer sowie zwei weitere Kennzeichen.
Das erste Kennzeichen steuert die Priorität des Beleges innerhalb dieser Gruppe
(Typ Zahl), das zweite Kennzeichen steuert eine Linie innerhalb dieser Gruppe
(Typ Zeichenkette).
Beispiel: Alle Belege einer Streckenverarbeitung
besitzen eine Streckennummer, diese Streckennummer ist die Gruppe. Innerhalb der
Strecke gibt es gewisse Zusammenhänge zwischen Belegen, wie z.B. der
Lieferschein 1000 mit seinem Touravis, dem Frachtpapier und dem Zolldokument.
Der Zusammenhalt dieser Belege wird über das Linienkennzeichen festgehalten. Des
Weiteren ist nun innerhalb so einer Linie ein Beleg als der führende Beleg
ausgezeichnet, dieser bekommt dann das Prioritätskennzeichen 1, alle anderen
z.B. 2. Wird nun die Linie Lieferschein mit Frachtbrief, Zollschein und Touravis
in die Poststraße gegeben, so wird in der Poststraße auf Basis des
Prioritätskennzeichens eingetütet, damit das Anschriftenfeld auch immer richtig
als erste Seite erscheint.
Die Gruppe ist zu jedem Archiv-Eintrag manuell
pflegbar.
Der Gruppentyp ist ein Anwenderformat (AF_FA_GRUPPE)
und ist als solches frei bestimmbar. Wir liefern eine Beispielkonfiguration aus.
Wichtig ist zu bedenken, dass der Eintrag 0 des Formates dem Programm
vorbehalten ist und die Bedeutung „keine Archivgruppe“ hat.
Im Vorgangsdruck ist eine Steuerung von
Archiv-Dokumenten zu einem Artikel über einen angebaren Gruppentyp im Formular
möglich.

---

## Funktionen auf der Waagenmaske

Funktionen auf der Waagenmaske

---

## Vorgänge erzeugen und editieren SF9

Vorgänge erzeugen und editieren SF9
Das Erzeugen und Editieren von Vorgängen aus einer
Wiegung ist an dieser
Stelle
beschrieben, da das
Verhalten aus der Hofliste dem Verhalten aus der Maske entspricht.
Es kann immer nur ein Vorgang editiert werden. Sollen
aus der Auswahlliste heraus mehrere Vorgänge mit der Funktion aufgerufen werden,
so wird immer der erste Vorgang gewählt.

---

## Vorgänge erzeugen CF9

Vorgänge erzeugen CF9
Das Erzeugen von Vorgängen aus einer Wiegung ist an
dieser
Stelle
beschrieben, da das Verhalten aus der Hofliste dem Verhalten aus der Maske
entspricht.

---

## Wiegung abschließen F11

Wiegung abschließen F11
Das Abschließen von Wiegungen ist an dieser
Stelle
beschrieben,
da das Verhalten aus der Hofliste dem Verhalten aus der Maske entspricht.

---

## Abschließen Rückgängig SF11

Abschließen Rückgängig SF11
Das Wiedereröffnen von Wiegungen ist an dieser
Stelle
beschrieben, da das Verhalten aus der Hofliste dem Verhalten aus der Maske
entspricht.

---

## Importumsetzer

Importumsetzer
Hauptmenü
Externe Kommunikation
Stammdatenimport
Importumsetzer [
IMPUM
]
Mit dem Importumsetzer können Kennzeichen von einem
Fremdsystem wie z.B. Terres bequem auf Referenz-ERP Kennzeichen umgeschlüsselt werden.
Dies gilt natürlch auch in die andere Richtung.
Es wird zu jedem Fremdkennzeichen (Eingangsschlüssel)
ein Referenz-ERP Kennzeichen (Umsetzung) innerhalb einer Schlüsselklasse
zugeordnet.
Variante
Import-Umsetzer
In dieser Variante können neue Umschlüsselungen
angelegt werden.
Funktionen: Neu [F8] -  Ändern [F5] -
Löschen [F7
]
Mit der Funktion Neu, Ändern oder Löschen wir die
Maske Import Umsetzer geöffnet.
Maske
Feld
Bedeutung
Schlüsselklasse
In diesem Feld wird die Klasse
      angegeben in dem sich das Umschlüsselungpaar befindet.
Eingangsschlüssel
Der Wert welcher Umgeschlüsselt
      werden soll.
Umsetzung
Zugewiesenner
      Umschlüsselungswert
Info-Text
Informationstext
Besondere
Funktionen
Im Änderfall steht die Funktion
Alle Ändern
[
F5
] zur Verfügung, wenn in der Auswahlliste
mehr als ein Datensatz markiert worden ist. Dies bedeutet, falls die Änderung
gemacht wird, wird dies für alle Datenstätze mitübernommen werden. Des Weiteren
kann mit
Speichern unter…
[
SF9
] eine neue Umsetzung angelegt werden.
Im Löschenfall steht die Löschfunktion
Alle
Lösche [SF7]
zur Verfügung, wenn in der Auswahlliste mehr als ein
Datensatz markiert worden ist. Damit werden alle ausgewählten Datensätze
gelöscht.
Funktion Ändern(Tabellarisch) [SF5]
Diese Funktion steht nur zur Verfügung, wenn in der
Variante „Import-Umsetzer Itemboxzuordnung“ eine Zuordnung zu der
Schlüsselklasse existiert. Die umzuschlüsselnden Werte werden in einer Prozedur
bestimmt. Diese werden in die Maske geladen. Diesen Werten können dann die
Referenz-ERP Kennzeichen zugeordnet werden. Wurde eine Itembox eingerichtet, so kann
der Wert darüber ausgewählt werden. Beim Verlassen der Maske werden die Daten,
die ein Umschlüsselungspaar darstellen abgespeichert.
Variante Import Sch
[...]


---

## inplausible Gebinde

inplausible Gebinde
Im Pfleger für Mengeneinheiten
[ME]
existiert die Variante „inplausible
Gebinde“. In dieser Variante sind die unkorrekt/unvollständig eingerichteten
Gebinde aufgeführt. Um diese jetzt zu korrigieren (Setzen des Löschkennzeichens
natürlich auch möglich), ist folgendes Vorgehen erforderlich:
Fall 1: Grundmengeneinheit und Ergebnismengeneinheit
sind inkompatibel
Lösung:
man geht ins Feld Ergebnismengeneinheit und führt eine
F3-Box aus → man kann die Ergebnismengeneinheit nur auf eine zur Grundeinheit
kompatible Men­geneinheit setzen
man validiert ohne F3 einfach die
Ergebnismengeneinheit und die Grund­einheit wird automatisch auf die
Grundeinheit der Ergebniseinheit gesetzt
Fall 2: Als Grundmengeneinheit/Ergebnismengeneinheit
ist ein Gebinde eingetragen
Lösung:
Man validiert das Feld Ergebnismengeneinheit und es
wird als Grundeinheit die Grund­einheit des Gebindes eingetragen, das als
Ergebnismengeneinheit eingetragen war. Dann kann man über F3 im Feld
Ergebnismengeneinheit passend zur ge­änderten Grundmengeneinheit auch die
Ergebnismengeneinheit anpassen.
Fall 3: Es ist keine Grundmengeneinheit eingetragen,
aber eine Ergebnismengen­einheit
Lösung:
man validiert das Feld Ergebnismengeneinheit und die
Grundeinheit wird auto­matisch auf die Grundeinheit der Ergebniseinheit
gesetzt
man führt ein F3 auf dem Feld Ergebnismengeneinheit
aus und hat die Wahl aus allen Mengeneinheiten. Wenn diese Wahl vollzogen wurde,
wird die Grundeinheit der gewählten Ergebnismengeneinheit automatisch in die
Grund­einheit des in Bearbeitung befindlichen Gebindes eingetragen
Fall 4: Es ist weder eine Grundmengeneinheit noch eine
Ergebnismengeneinheit ein­getragen
Lösung:
Man kann vorgehen wie bei einer Neuanlage einer
Mengeneinheit.

---

## inplausible Mengeneinheiten

inplausible Mengeneinheiten
Im Pfleger für Mengeneinheiten
[ME]
existiert die Variante "inplausible
Mengeneinheiten". In diesen Varianten sind die unkorrekt/unvollständig
einge­rich­teten Mengeneinheiten aufgeführt. Um diese jetzt zu
korrigieren (Setzen des Lösch­kennzeichens ist natürlich auch möglich), ist
folgendes Vorgehen erforderlich:
Es reicht, die nicht eingetragene Grundmengeneinheit
über
F5
im Pfleger
nach­zutragen.

---

## Waagenanbindung / Online Waage

Waagenanbindung
/ Online Waage
Wareneingang
Hauptmenü
Wareneinkauf
Online -Waage
Online-Waage Einkauf
oder Direktsprung
[WAGEK]
Varianten
Hofliste Einkauf:
In dieser Variante
werden alle Einkaufsbelege angezeigt.
Offline Wiegungen
Als Basisdatenstruktur für eine Offlinewiegung steht
die Bitzer-Schnittstelle zur Verfügung.
Warenverkauf
Hauptmenü
Warenverkauf
Online -Waage
Online-Waage Verkauf
oder Direktsprung
[WAGVK]
Varianten
Hofliste Verkauf:
In dieser Variante
werden alle Verkaufsbelege angezeigt.
Waage Allgemein
Hauptmenü
Saatzucht
Saatgutabwicklung
Online-Waage
oder Direktsprung
[WAAGE]
Varianten
Hofliste:
Hier sind alle Wiegungen zu
finden Wareneinkauf wie Warenverkauf.
Speicherabfrage
Die „Speichern Ja/Nein“-Abfrage in der Owaage
erscheint nur dann, wenn Eintragungen in der Maske vorgenommen worden sind, ohne
dass ein Artikel oder ein Kunde hinterlegt worden ist.

---

## Felder verschieben

Felder verschieben
Die Funktion
Felder Verschieben
kann über den
Steuerparameter
918
angeschaltet und
ausgeschaltet werden. Im Standard wird die Owaage Maske mit dem Standard-Layout
gestartet
Über
CF8
kann man die Positionierung der Felder in der Waagemaske festlegen. Um diese
Funktion in der OptionBox anwählen zu können, muss man die Maske im Neufall
geöffnet haben. Danach erfolgt eine Abfrage, für welches Profil die
Positionierung gespeichert werden soll. Das gewählte Profil wird sofort
angelegt.
Mit einem Klick auf ein Element kann es verschoben
werden. Das Feld wird eingefärbt und es öffnet sich dann ein kleines Fenster, in
dem sich Knöpfe zum Navigieren des gewählten Elementes befinden. Ebenso ist es
jetzt aber auch möglich, das Element über die Pfeiltasten zu steuern oder mit
TAB auf den nächsten Tabreiter zu schieben.
In dem Textfeld „Schrittweite“ kann die Schrittweite
beim Navigieren des Feldes angegeben werden. Ist keine Schrittweite angegeben,
wird standardmäßig „1“ verwendet. Des Weiteren kann mit SEITE RAUF und SEITE
RUNTER die Schrift des Feldes vergrößert oder verkleinert werden. Ebenso kann
mit POS1 und ENDE die Breite eines Feldes vergrößert oder verkleinert werden.
Diese letzten beiden Funktionen stehen nicht bei allen Feldern zur Verfügung.
Mit ESCAPE wird die Positionierung des Elementes abgeschlossen. Wenn man alle
Elemente wie gewünscht positioniert hat, kann man mit
CF8
die Positionierung speichern. Über die
Funktion
Felder zurücksetzen
werden
die Felder auf ihren ursprünglichen Ausgangsort zurückgesetzt.
Mit der Funktion
Profil löschen
wird das gewählte Profil,
d.h. „aktueller Bediener“ oder „alle Bediener“ gelöscht. Dadurch kann man in der
Anzeige der Felder auf die höhere Positionierung zurückfallen, da vorrangig die
Positionierung für den aktuellen Bediener angezeigt wird, falls diese nicht
vorhanden ist, die für alle Bediener oder ansonsten die voreingestellte
Positionierung. Die Funktionen in der Optionbox sind b
[...]


---

## Offline-Wiegedaten

Offline-Wiegedaten
Neben der einrichtbaren Waagenschnittstelle steht die
Bitzer Offline Schnittstelle im Standard direkt nutzbar zur Verfügung. Diese
Schnittstelle wird einerseits durch das
Bitzer System
beschrieben, zusätzlich
steht aber auch noch eine Excel-basierende Wiegedaten- und
Laborwerte-Verarbeitungsmechanik in diesem Bereich zur Verfügung.
XML Bitzerstrukturen, wie auch einfache XLS Excel
Dateien werden in diesem Bereich direkt in eine Zwischentabelle eingelesen, um
dann zu Hoflistenelementen gemacht zu werden. Die Hoflistenelemente können dann
direkt in Belege verschiedenster Art umgewandelt werden.
Die Einspielung

---

## Partieetiketten

Partieetiketten
Auswahlliste
Felder
Artikel-Nummer
Artikelstamm-Nummer
Nummer
Partienummer, vom Benutzer vergebene
      Identifikation der Partie
Anerkennung
Anerkennungsnummer
Code
Fruchtart
Bezeichnung der
      Fruchtart
Botanisch
Botanische Bezeichnung
Sorte
Saatsorte
Probenahme
Datum der Probenahme
Attest
Datum
KF
Keimfähigkeit
TKG
Tausendkorngewicht
PID
Partie-ID
Dialog „Etiketten erstellen“
Felder
Anzahl
Anzahl der zu erstellenden
      Etiketten
Jahr
Anerkennungsstelle
Nummer und Name der
      Anerkennungsstelle
Type
Lager
Art
Fruchtart
Botanisch
Botanische Bezeichnung
Sorte
Saatsorte
Probenahme
Datum der Probenahme
Gewicht
TKG
Tausendkorngewicht
KF
Keimfähigkeit
Beize
Name
      des Pflanzenschutzmittels
Zulassungs-Nummer
Zulassungs-Nummer des
      Pflanzenschutzmittels
Wirkstoff
Wirkstoff des
      Pflanzenschutzmittels
Verpackungseinheit
Qualitätsbemerkung
Bescheid
Herkunft
Wiederverschluß
Dazu
      Probedatum

---

## Registerkarte Lohnwiegung

Registerkarte Lohnwiegung
Dieser Punkt ist für
Fremdwiegungen(Lohnwiegungen)
interessant bei denen z.B. Ware für
eine andere Firma gewogen wird die selbst keine Waage besitzt.
Feld
Bedeutung
Dienstleistungsartikel
Wird
      hier ein Dienstleistungsartikel hinterlegt, so wird der
      Dienstleistungsartikel und nicht die Ware in Rechnung gestellt.
Bei der
      Vorgangserzeugung wird dann die Warenposition des Lieferscheines oder der
      Rechnung als
Wertartikel
gebucht. Des Weiteren erhält der
      Beleg eine neue Position, die den Dienstleistungsartikel
      enthält.
Bei
      der Erzeugung des Vorgangs wird das Lager des Dienstleistungsartikels in
      folgender Reihenfolge gesucht.
1.   Lager des
      Waagebeleges
2.   Lager aus dem
      Profil
3.   Lager des Benutzers
      (VKONS)
4.   Lager des Artikels,
      der im Profil eingetragen wurde
Entsprechend wird eine Stufe tiefer
      gesucht, wenn es kein Artikel in dem entsprechenden Lager
      gibt.
Wertartikel
Default ist Nein.
Stellt man Ja
      ein, dann wird der Dienstleistungsartikel als Wertartikel
      behandelt.
Anzahl Wiegungen
Standard ist ‚zwei
      Wiegungen’.
Hier
      wird festgelegt nach wie vielen Wiegungen aus der
Vorgangserzeugung
heraus der
      Waagedatensatz auf den Status ‚mit Vorgang’ gesetzt werden soll.
Soll
      beim Wiegetyp Lohnwägung (auch Schüttwiegung oder Fremdwiegung) nur eine
      Wiegung durchgeführt werden, dann muss dieses Feld auf ‚eine Wiegung’
      gesetzt werden.

---

## Registerkarte Bildschirm

Registerkarte Bildschirm
Feld
Bedeutung
Vorbelegung des
      Klammertyps
Belegt den Klammertyp in der Waage
      mit dem hier hinterlegten Klammertyp
Spedition und LKW als
      Textfelder
Mit
      diesem Schalter kann eingestellt werden, ob das LKW-Feld als Textfeld
      behandelt werden soll.
Den
      letzten LKW vorbelegen
Die
      letzte Schlagbezeichnung vorbelegen
TAB
      Deck Einstellungen deaktivieren
Mit
      dieser Einstellung kann die Registerkarte Einstellungen ausgeblendet
      werden.
Länge der
      Bemerkungsfelder
Hier
      kann die Textlänge der Bemerkungsfelder hinterlegt werden
Dispomengenfeld
      deaktivieren
Blendet die Dispomengenfelder auf
      der Waagenmaske aus, wenn der Schalter auf Ja steht.
Lagerplatzfelder
      deaktivieren
Wenn
      diese Einstellung auf Ja gestellt wird, so werden die Lagerfelder auf
      Waagenmaske aus geblendet-
Kunden-Ort mit anzeigen
Rohwarenschema mit
      abfragen
Mit
      dieser Einstellung wir das Rohwarenschema ausgeblendet.
Artikelbezeichnung nicht aktiv
      abfragen
Wird der Schalter auf Nein gestellt,
      so kann die Artikelbezeichnung geändert werden.
Sonderqualitäten
      deaktivieren
Hiermit können die Felder der
      Sonderqualitäten deaktiviert werden. (Felder: Feuchteprozent,
      Fremdfeuchte, Frachtkennzeichen)
Ladungszeiten aktivieren
Wird
      dieses Feld auf „Nein“ gestellt, so werden die Felder für die
      Ladungszeiten deaktiviert.
Schlag/Sorte/Gebiet
      aktiv
Wird
      dieses Feld auf „Nein“ gestellt, so werden die Felder für den Schlag, die
      Sorte und das Gebiet deaktiviert.
Vorfracht aktiv
Noch
      nicht implementiert
Breite der Waagenmaske in
      Pixel
Hiermit kann die Breite der
      Waagenmaske verändert werden. Sobald die Waagenmaske breit genug ist
      werden die Qualitätstabellen, so wie der Abstufungsrtikel und die Infratec
      Datentabelle auf die Registerkarte Allgemein geschoben.
Sobald eine Qualitä
[...]


---

## Registerkarte Drucken

Registerkarte Drucken
Man legt in der Vorlage das Formular und den Drucker
für den Wiegeschein fest.
Es können nur Formulare vom Formulartyp Wiegeschein
ausgewählt und angegeben werden.
Die Angaben sind wirksam für die Funktion
Wiegeschein drucken
.
Man kann außerdem ein Formular und einen Drucker für
den Druck einer/eines Eingangsmeldung/Laufzettels angeben.
Im Feld Druck
Verkaufsbeschränkung kann hinterlegt werden, ob ein Laufzettel bei Artikeln mit
Verkaufsbeschränkung
(vom Typ beschränkter Ausgangsstoff für Explosivstoffe)
gedruckt werden soll.
Die Angaben auf diesen Feldern sind wirksam für die
Funktion
Eingangsmeldung drucken
.
Im Feld
Anzahl wird die Anzahl hinterlegt, wie oft das Formular oder der Wiegeschein
ausgedruckt werden soll.

---

## Registerkarte Spezialitäten

Registerkarte Spezialitäten
Feld
Bedeutung
Scheinmenge für die erste
      Wiegung
Hier
      kann eine Scheinmenge für die erste Wiegung eingetragen warden, die bei
      der Netto Wiegung verwendet warden soll.
Waagenprofil
Hier
      kann man festlegen, welches Terminal man verwenden möchte.
Normalerweise wird das Feld Terminal
      beim Öffnen der Waagenmaske mit dem zuletzt verwendeten Profil gefüllt.
      Dies ist auch weiterhin so, wenn man eine Vorlage verwendet, in der kein
      Terminal angegeben ist.
Neue
      Wiegung
Öffnet man die Waagenmaske im
      Neufall mit einer Vorlage, für die ein Terminal hinterlegt ist, dann wird
      dieses Terminal in die Maske übernommen und das Feld Terminal deaktiviert.
Wechsel der
      Vorlage
Wechselt man die Vorlage, dann
      wird das Feld Terminal entsprechend mit angepasst, wenn die Vorlage ein
      Terminal enthält. Enthält sie keines, dann wird das Feld Terminal wieder
      zum Editieren freigegeben.
Bearbeiten
Öffnet man die Waagenmaske mit
F5
zum Bearbeiten, dann wird
      das Feld Terminal abhängig von der Wiegung bzw. vom Status
      gefüllt.
Status eröffnet:
Es
      wurde noch keine Wiegung durchgeführt, deshalb wird zunächst das zuletzt
      verwendete Terminal geladen. Enthält die verwendete Vorlage ein Terminal,
      so wird dieses Terminal in die Maske übernommen und das Feld
      deaktiviert.
Status 1te Wiegung:
Wurde die 1te Wiegung durchgeführt,
      dann wird die Maske mit dem dort verwendeten Terminal
      gestartet.
Status 2te Wiegung:
Wurde die 2te Wiegung durchgeführt,
      dann wird die Maske mit dem dort verwendeten Terminal gestartet.
Nacherfassung von
      Wiegungen
Hier
      kann für die nachträgliche manuelle Erfassung von Wiegungen das Wiegedatum
      über das Belegdatum gesteuert werden, so dass nicht die eigentliche
      Eingabezeit der Wiegung als Wiegedatum festgehalten wird, sondern z.B. der
      Tag vorher.
Für die Nacherfassung empf
[...]


---

## Qualitätswerte automatisch berechnen

Qualitätswerte automatisch
berechnen
Mit der Funktion
Qualitätswerte automatisch berechnen
werden für die ausgewählten Ladeeinheiten die durchschnittlichen
Qualitätswerte zu einem Zeitpunkt berechnet. Dabei werden alle Zugänge, die per
Onlinewaage abgewickelt wurden, sowie Zugänge aus anderen Ladeeinheiten mit
ihren jeweiligen Qualitäten, gewichtet mit der Bewegungsmenge, berücksichtigt.
Nicht erfasste Qualitäten (Wert = Null im Waagen-Beleg UND 0,0 im zugehörigen
aktuellsten Rohwarebeleg) werden dabei, auch für die jeweilige Gewichtsmenge,
nicht berücksichtigt. Dadurch wird für eine betroffene Anlieferung für diese
Qualität ein Wert im Durchschnittsbereich unterstellt, um bei einer großen
Anzahl von Anlieferungen, von denen für eine bestimmte Qualität nur wenige Werte
nicht erfasst sind, statistisch eine möglichst geringe Abweichung des
berechneten vom tatsächlich messbarem Durchschnitt zu erhalten.
Betrachtet
werden alle Bewegungen bis zu einem festgelegten Zeitpunkt, das ist in der Regel
für eine Ladeeinheit die Bewegungszeit der letzten Bewegung. Gibt es jedoch nach
der letzten Bewegung einen
manuell
festgeschriebenen Qualitätssatz
, so wird dessen Zeitpunkt (plus einer
Millisekunde) als Ergebnis-Zeitpunkt für den automatisch zu bestimmenden
Qualitätssatz bestimmt. Der Eintrag des Qualitätssatzes erfolgt mit dem so
bestimmten Zeitpunkt. Zur Berechnung der Qualitätsdurchschnitte wird zunächst
der Anfangspunkt bestimmt,  das ist die zuletzt erfolgte Leermeldung zur
Ladeeinheit (vor dem Ergebnis-Zeitpunkt) oder, wenn vorhanden, die letzte
gültige automatische oder manuelle Qualitätsbestimmung (nach der zuletzt
erfolgten Leermeldung, vor dem Ergebnis-Zeitpunkt). Alle Bewegungen,
gegebenenfalls beginnend mit dem zuvor erwähnten Qualitätsbestimmungseintrag,
zwischen diesen beiden Zeitpunkten werden zur Berechnung herangezogen. Dabei
werden die Qualitätswerte von Zugängen aus anderen Ladeeinheiten rekursiv zum
Zeitpunkt der Abgangsbewegung der
[...]


---

## Stammdatenpflege

Stammdatenpflege
Zunächst müssen Sie die bestehenden Anschriften
bearbeiten. Es ist eine Unterscheidung notwendig, ob es sich bei der Anschrift
um eine Person oder um eine Firma/Organisation handelt. Setzen Sie dazu im
Anschriftenstammpfleger das Kennzeichen Person/Firma.
Handelt es sich bei der Anschrift um eine Person, so
kann es sinnvoll sein, bei Auslandskontakten weitere Daten wie z.B. die
Sozialversicherungsnummer oder Reisepassdaten, Geburtsdaten etc. abzufragen.
Diese Daten sind streng vertraulich, und deshalb auch
nur einem eingeschränkten Personenkreis zugänglich.

---

## Vorgang-Detailansicht

Vorgang-Detailansicht
Dies ist eine Ansicht, die speziell aus der
Silo Verwaltung
und aus der
Hofliste
aufgerufen
wird.
In dieser Ansicht werden alle Belege, die zu einem
Silo oder einem Waagenbeleg gehören, dargestellt. Dies beinhaltet Normalware,
sowie Rohware.
Um die verschiedenen Vorgangstypen anzuzeigen, gibt es
die Funktion
Ansicht
, um sich die
Vorgänge im Ansichtsmodus zu öffnen.
•
F6
ist für die Normalware
•
Shift+F6
ist für die
Rohware
•
Mit
F11
wird wie gewohnt die
Druckvorschau geöffnet.

---

## Vorgang-Details

Vorgang-Details
Mit dieser Funktion wird die Auswahlliste
Vorgangsübersicht
geöffnet. In dieser werden alle Vorgänge, die zu dem ausgewählten Waagenbeleg
gehören angezeigt.

---

## Ampelwiegung 1 CF9

Ampelwiegung 1 CF9
Beim Start der Ampelwiegung 1 führt man nur die 1te
Wiegung durch.
Das kann notwendig sein, wenn bei der
Ampelwiegung (CF5)
z.B. das Gewicht der ersten Wiegung
nicht korrekt übertragen wurde. Man möchte dann eine erneute erste Wiegung
durchführen. Die Funktion
Ampelwiegung (CF5)
würde diese
Wiegung für die 2. Wiegung halten, wenn der Waagenstatus ‚1te Wiegung’
ist.
Deshalb verwendet man in diesem Fall bewusst die Funktion
Ampelwiegung 1
CF9
.

---

## Wiegung 1 automatisch F9

Wiegung 1 automatisch F9
Man kann die 1.Wiegung automatisch starten. Dabei
werden die Werte der Waage ans System übergeben.
Das ist hilfreich, wenn bei
der automatischen Wiegung z.B. die erste Wiegung nicht korrekt abgelaufen ist.
Also möchte man evtl. eine erneute 1. Wiegung durchführen. Die automatische
Wiegung würde nun diese Wiegung für die 2. Wiegung halten.
Deshalb verwendet
man in dem Fall bewusst
Wiegung 1
automatisch
. Der erste Wert wird dann im System überschrieben.

---

## Ampelwiegung 2 CF10

Ampelwiegung 2 CF10
Beim Start der Ampelwiegung 2 führt man nur die 2te
Wiegung durch.
Das kann notwendig sein, wenn bei der
Ampelwiegung (CF5)
z.B. das Gewicht
der zweiten Wiegung nicht korrekt übertragen wurde. Man möchte dann eine erneute
zweite Wiegung durchführen. Die Funktion
Ampelwiegung (CF5)
weiß nicht,
welcher Wiegung sie das ankommende Gewicht zuordnen soll, wenn der Waagenstatus
‚2te Wiegung’ ist und ist deshalb in diesem Status nicht ausführbar.
Deshalb
verwendet man in diesem Fall bewusst die Funktion
Ampelwiegung 2
CF10
.

---

## Wiegung 1 manuell SHIFT+F9

Wiegung 1 manuell SHIFT+F9
Man kann die 1. Wiegung manuell eingeben.
Das ist
dann hilfreich, wenn die Waage intakt ist, die Verbindung zum Computer aber
Probleme bereitet, so dass die Wiegung nicht automatisch ausgeführt werden
kann.
Wurde im Terminal auf der Registerkarte Vorgang /
Zugang die Maximal-, Minimal- und das Taktungsgewicht angegeben, so wird das
hier erfasste Gewicht auf Plausibilität geprüft. D.h. Es kann nur ein Gewicht
eingegeben, welches auch von der Waage geliefert wird.
z.B.
Maximal Gewicht 40 t
Minimal Gewicht 1 t
Taktgewicht 0,002 t
So wäre eine Eingabe von 1,233 Tonnen, sowie 41Tonnen
und 0,5 Tonnen nicht möglich.

---

## Wiegung 2 automatisch F10

Wiegung 2 automatisch F10
Man kann die 2.Wiegung automatisch starten. Dabei
werden die Werte der Waage ans System übergeben.
Das ist hilfreich, wenn bei
der automatischen Wiegung z.B. die zweite Wiegung nicht korrekt abgelaufen ist.
Also möchte man evtl. eine erneute 2. Wiegung durchführen.
Deshalb
verwendet man in dem Fall bewusst
Wiegung 2
automatisch
. Der Wert der zweiten Wiegung wird dann im System
überschrieben.

---

## Wiegung 2 manuell SHIFT + F10

Wiegung 2 manuell SHIFT + F10
Man kann die 2. Wiegung manuell eingeben.
Das ist
dann hilfreich, wenn die Waage intakt ist, die Verbindung zum Computer aber
Probleme bereitet, so dass die Wiegung nicht automatisch ausgeführt werden
kann.
Wurde im Terminal auf der Registerkarte Vorgang /
Zugang die Maximal-, Minimal- und das Taktungsgewicht angegeben, so wird das
hier erfasste Gewicht auf Plausibilität geprüft.
D.h. Es kann nur ein Gewicht eingegeben, welches auch
von der Waage geliefert wird.
z.B.
Maximal Gewicht 40 t
Minimal Gewicht 1 t
Taktgewicht 0,002 t
So wäre eine Eingabe von 1,233 Tonnen, sowie 41Tonnen
und 0,5 Tonnen nicht möglich.

---

## Abschließen rückgängig

Abschließen rückgängig
Das Rückgängigmachen von Wiegungen ist dann von
Interesse, wenn man noch ein Feld nachträglich pflegen will, welches beim Status
Abgeschlossen geschützt ist.
Die Felder Bemerkungen oder Formular und Drucker
für den Wiegescheindruck sind auch noch nach dem Abschließen editierbar.
Man kann an zwei Stellen der Online-Waage das
Wiegungen abschließen rückgängig machen:
In der Auswahlliste
SF11
:
Man kann mehrere Datensätze mit Status abgeschlossen
markieren und das Abschließen rückgängig machen. Es erscheint eine Abfrage, ob
man das Abschließen der Wiegungen wirklich rückgängig machen möchte.
Wenn man keinen Datensatz markiert hat und somit für
alle Wiegungen Abschließen rückgängig wählt wird man gefragt, ob man dies
wirklich für alle Wiegungen tun möchte.
Der Status wird dann auf 2te Wiegung gesetzt.
In der Waagen-Maske
SF11
:
Hier kann man die in der Maske geöffnete Wiegung von
Status Abgeschlossen auf Status 2teWiegung ändern.
Bei angeschlossener
Silo
/
Ladeträgerverwaltung
wird die Zuordnung
dieser Wiegung aus den zugeordneten Silo / Ladeträger entfernt.
Ausführliche Informationen zu diesem Punkt ist in der
Hilfe
Ladeträgerverwaltung an der
Waage
beschrieben.

---

## UFLD und AIS in der Waage

UFLD und AIS in der Waage

---

## UFLD Felder in der Waage anzeigen

UFLD Felder in der Waage anzeigen
Mithilfe des AIS Systems können auf der Waagenmaske
UFLD-Felder angezeigt werden. Dazu müssen diese Felder im AIS mit der Feldnummer
des UFLD-Feldes und "UFLD" als Präfix bezeichnet werden (z.B.: "UFLD1767").
Das Laden der Informationen aus den UFLD Felder
funktioniert nur, wenn gegen einen Vorgang gewogen wird. Änderungen an den
UFLD-Feldern, welche auf der Waagenmaske vorgenommen werden, werden nicht in das
jeweilige UFLD Feld übernommen.

---

## AIS Felder auf dem Wiegeschein andrucken

AIS Felder auf dem Wiegeschein andrucken
Um AIS Felder auf dem Wiegeschein anzudrucken,
verwendet man im
Formulareinrichter
[FRM]
für den Bereich 1000/Wiegekopf die
Formulardruckposition 454/Zugriff auf OWAAGEADDON Daten. In der Spalte Text kann
man dann mit
F3
aus den Feldern im
OwaageAddOn das Feld auswählen, welches man andrucken möchte. Siehe auch
Wiegeschein drucken
. Des Weiteren
besteht die Möglichkeit, per SQLK sich Daten dazu zuladen. Der Name der ID,
welche die OWaage_id enthält, heißt ID_OWAAGE_ID.
Beispiel:
select
Kundnummer from OWaage as ow
join Kundenstamm as ks on (ks.KundId =
ow.OWaage_Kundeid)
where ow.OWaage_id =
:ID_OWAAGE_ID

---

## AIS Felder einrichten

AIS Felder einrichten
Mit dem
Referenz-ERP Informationssystem
[AIS]
können Zusatzfelder auf der Waagenmaske
angezeigt und abgefragt werden. Über die Funktion
Felder verschieben
können die
Felder auf der Waagenmaske verschoben werden.

---

## Ampelwiegung CF5

Ampelwiegung CF5
Die Wiegung wird automatisch durchgeführt. Die
ankommenden Daten der Waage werden in die Anzeigefelder auf der Maske
übertragen, sobald sie verwertbar sind. Es wird vom System anhand des
Waagenstatus erkannt, ob es sich um die 1. Wiegung handelt oder ob schon eine
Wiegung existiert und somit die 2. Wiegung durchgeführt werden muss.
Auf der Maske wird nach dem Starten der Funktion
Ampelwiegung
CF5
eine Ampel rechts neben den
Gewichtsangaben angezeigt, die drei Zustände haben kann:
Rot
: Die Werte, die die Waage liefert, sind
nicht verwertbar. Eventuell wackelt der LKW auf der Waage noch zu stark. Es wird
weiter auf verwertbare Daten gewartet. Der Bediener der Waage muss nichts weiter
tun als auf das grüne Signal und die Datenübernahme zu warten.
Gelb
: Die Waage liefert ein Gewicht kleiner
oder gleich Null zurück. Evtl. steht noch kein LKW auf der Waage. Es wird weiter
auf verwertbare Daten gewartet. Der Bediener der Waage muss nichts weiter tun
als auf das grüne Signal und die Datenübernahme zu warten.
Grün
: Die Waage liefert ein Gewicht. Dieses
wird sofort in die Anzeige übernommen und der Status der Wiegung wird
entsprechend gesetzt. Damit ist die Ampelwiegung abgeschlossen.
Zusätzlich zur Ampel wird ein Text (unterhalb der
Anzeigefelder fürs Gewicht) angezeigt, der darauf hinweist, dass die
Ampelwiegung stattfindet. Abbrechen kann man die Ampelwiegung mit der TAB Taste.
Sobald die Ampel grün und das Gewicht der Waage in die Anzeige übernommen
werden, zeigt auch der Text an, dass die Wiegung durchgeführt wurde.

---

## Archivierung von Wiegescheinen

Archivierung von Wiegescheinen
Wiegescheine zu Waagedatensätzen können archiviert und
von der Auswahlliste der Waage aus angezeigt werden.
Dafür muss in der
Einrichtung des Wiegescheins die Archivierung aktiviert sein.
Für jeden
neuen Waagedatensatz wird eine Archiv-Referenznummer angelegt, die unter anderem
die Belegnummer enthält. Druckt man den archivierbaren Wiegeschein, dann wird
der Eintrag ins Formulararchiv mit dieser Referenznummer versehen. Über die
Funktion
Archiv anzeigen
CF12
in der Auswahlliste kann man sich dann
den Wiegeschein zu einem markierten Datensatz anzeigen lassen.

---

## Bedienerspeicherung

Bedienerspeicherung
Der Bediener der 1ten und der 2ten Wiegung wird im
Waagedatensatz gespeichert.
Dadurch kann man verfolgen, wer z.B. eine Wiegung
nachträglich manuell geändert hat.
Es werden jetzt folgende Felder in der Auswahlliste
jeweils für die erste und die zweite Wiegung angezeigt:
Wiegenr
: Die Nummer, die bei der Wiegung von
der Waage übertragen wird oder die bei einer manuellen Wiegung im zweiten
Eingabefeld eingegeben wird
Wiegeart
: Manuell oder automatisch; zeigt an,
wie die Wiegung durchgeführt wurde
Bed
: Der Bediener, der die Wiegung durchgeführt
hat
Mitschrift
: Inhalt der Daten die übertragen
wurden
BedMitschr
: Der Bediener, der die Wiegung mit
Waagenmitschrift durchgeführt hat
Zeit
: Zeit der Wiegung mit Waagenmitschrift
Die ersten drei Felder stammen aus dem Waagedatensatz,
die letzten drei Felder aus der Waagenmitschrift.
Das Feld Bed und BedMitschr
können unterschiedlichen Inhaltes sein, wenn eine automatische Wiegung z.B.
manuell überschrieben wurde. Für diesen Fall steht außerdem das Feld Wiegeart
auf manuell und im Feld Mitschrift steht ‚Wiegung manuell überschrieben’.

---

## Boxmanagement

Boxmanagement
Der SPA 614 schaltet die Funktion
Boxmanagement starten
frei. Mit der
Funktion lässt sich dann die Maske ‚Waage Boxmanagement’ aufrufen. Dort muss für
die Wiegung die Anzahl der Boxen und die einzelnen Boxen eingetragen werden.
Dabei wird das Taragewicht der einzelnen Boxen berechnet und beim Speichern an
die aktuelle Wiegung übergeben. Die Wiegenummer ist dabei die gleiche, wie die
der ersten Wiegung.
Beim Wiederaufruf des Boxmanagements werden die
eingetragenen Boxen angezeigt, können aber nicht bearbeitet werden. Das Tara
Gewicht muss dabei nicht dem Gesamtleergewicht der Boxen entsprechen, sollte das
Taragewicht an der Wiegung oder das Leergewicht an der Box geändert worden
sein.
Die Funktion ist nur verfügbar, wenn ein Lager in der
Wiegung gesetzt wurde. Standardmäßig ist das Lager mit dem Lager in den
Vorgangskonstanten (VKONS) gefüllt.
Das Boxmanagement kann erst gestartet werden, wenn die
erste Wiegung eingetragen wurde. Sollte die zweite Wiegung nicht durch das
Boxmanagement erfasst worden sein, so kann die Maske auch nicht aufgerufen
werden.

---

## Bearbeiten

Bearbeiten
Über Bearbeiten hat man die Möglichkeit, einige Felder
einer Wiegung nachträglich zu pflegen. Man kann z.B. Bemerkungen nachtragen.
Wenn man z.B. bei einer abgeschlossenen Wiegung nachträglich die Feuchte
eingeben will, dann ist das Feld im Bearbeiten Modus gesperrt. Man kann aber das
Abschließen der Wiegung rückgängig machen (
F11
), so dass sie den Status 2te Wiegung
erhält und die Feuchte editierbar ist.

---

## Beleg löschen SF7

Beleg löschen SF7
In der Auswahlliste kann man markierte Wiegungen
löschen. Wenn man die Abfrage mit Ja bestätigt, werden die markierten Belege auf
den Status ‚Gelöscht’ gesetzt, wenn sie nicht schon den Status ‚mit Vorgang’
haben. Wiegungen mit Vorgängen dürfen nicht gelöscht werden.

---

## Archiv anzeigen CF12

Archiv anzeigen CF12
Mit dieser Funktion werden alle zu archivierende
Belege zu dieser Wiegung angezeigt.

---

## Formular drucken

Formular drucken
Die Funktion
Formular drucken
druckt das in der
Waagenmaske angegebene Formular auf dem angegebenen Drucker.
Diese Funktion
ist in der OptionBox anders als die Funktion
Wiegeschein drucken
schon vor dem
Status „Abgeschlossen“ anwählbar und führt vorher auch keine Prüfung der Felder
durch.
Das ermöglicht den Formulardruck z.B. schon nach der
1. Wiegung für einen Annahmeschein.
Dafür wurde die
F3
-Auswahl auf dem Feld Formular um eine
Variante erweitert, die alle Formulare (und nicht nur die Wiegescheine)
anzeigt.

---

## Kennzeichen Vorgangserzeugung (statusVorgangerreicht)

Kennzeichen Vorgangserzeugung (statusVorgangerreicht)
In der Relation owaage gibt es ein Feld, welches
anzeigt, ob für einen Datensatz schon einmal ein Vorgang erzeugt wurde
(statusVorgangerreicht = 1). Default ist 0.
Das Feld wird per Update Trigger auf 1 gesetzt, wenn
sich der Status eines Waagedatensatzes von 4 (abgeschlossen) auf 5 (mit Vorgang)
ändert.
Hat man in der Waage Belege mit Hilfe der Funktion
Wiegungen raffen
erzeugt, dann werden
diese Belege wie folgt gelöscht:
Der geraffte Beleg wird echt gelöscht (verschwindet
ganz aus der Datenbank); die Original-/Ursprungsbelege werden vom Status
‚gerafft gelöscht’ auf ‚abgeschlossen’ zurückgesetzt.
Existiert zu der Wiegung ein Eintrag in der
Siloverwaltung / Lagerverwaltungssystem so kann durch das Setzen des
Steuerparameters 925
mit der Option
„
SILOPOSLOESCHENBEILOESCHEWIEGUNG
“
eingestellt werden, ob die Position aus dem Silo / Ladeträger ausgebucht werden
soll. Ist eine Position schon als gelöscht markiert worden, und die dazu
gehörige Position im Ladeträger / Silo wurde noch nicht ausgebucht, so kann mit
der Funktion
Löschen
die Position
vom Ladeträger / Silo gebucht werden.

---

## Kreditlimitprüfung an der Waage

Kreditlimitprüfung an der Waage
An der Waage kann schon während der Erfassung einer
Verkaufswiegung
geprüft
werden, ob das Kreditlimit des Kunden überzogen ist. In Abhängigkeit des
Steuerparameters 233
(Kreditlimit-Prüfung)
wird das Sperrverhalten übernommen. Dies Bedeutet,
dass ab der Stufe Sperren keine
Verkaufswiegungen
mehr für den
Kunden
durchgeführt werden
können.
Die Kreditlimitprüfung kann für die Waage mit dem
Steuerparameter 667 (Waagemaske
Kreditlimit)
separat an- und ausgeschaltet werden. Diese Prüfung findet
zurzeit nur bei
Verkaufswiegung
(Normalware wie Rohware)
statt.
Wenn
Steuerparameter 690(Waagenmaske Kreditlimit Dispomenge)
gesetzt worden ist und ein
Kontrakt
an der Wiegung hinterlegt wurde, dann werden alle noch nicht zu Lieferscheine
gewandelten Waagenbelege des Kontraktes zusammen gezählt und vom Kreditlimit
abgezogen.
Eine Prüfung der aktuellen Wiegemenge gegen den
Markpreis des Wiegeartikels findet noch nicht statt. Dies bedeutet, die aktuelle
Wiegung wird nicht zur Kreditlimit Funktion herangezogen, wenn der Wiegung kein
Kontrakt
zugeordnet worden ist.
Die Kreditlimitprüfung wird zurzeit nicht
durchgeführt, wenn ein Rohwarenlieferschein aus der Hofliste erzeugt werden
soll. Für die Normalware wird die Prüfung auch beim Erzeugen eines Beleges aus
der Hofliste durchgeführt.
Die Überprüfung des Kreditlimits passiert nach den
folgenden Eingaben.
1.
Nach der Kundenauswahl
2.
Nach der Kontraktauswahl
3.
Vorm Abschließen der Wiegung
4.
Vorm Erzeugen des Beleges
5.
Nach der Eingabe der Menge
6.
Nach Eingabe des Disponiertenmenge
Privatisierung der Kreditlimit Funktion
An dem
Steuerparameter 925(Allgemeiner Steuerparameter Waage)
kann eine private Kreditlimit Prozedur hinterlegt werden. Diese Prozedur wird
dann anstelle der Standard-Kreditlimitberechnung an der Waage aufgerufen. Die
Eingangsparameter der Prozedur müssen genauso heißen wie an dieser
Stelle
beschrieben.
Gibt die Prozedur als Fehler eine eins zurück,
[...]


---

## Lagerumbuchung

Lagerumbuchung
Für die Lagerumbuchung ist es nötig, sich ein
Wiegeprozess
einzurichten mit
dem Wiegetyp Lagerumbuchung und der passenden Vorgangsklasse und
-unterklasse.
Diese Vorlage ist dann in der Waagenmaske auszuwählen.
Anstelle des Kundeneingabefeldes erscheinen zwei Felder für das Ziellager und
den Ziellagerplatz.
Es sind Lager und Lagerplatz für den Abgang und den
Zugang anzugeben. Die Lagerplatzangabe für das Ziel ist nicht zwingend
notwendig. Man erhält aber bei der Prüfung einen Hinweis, wenn man ihn nicht
angegeben hat. Bei keiner Eingabe wird die Lagerplatznummer des Abganges auch
für den Zugang verwendet. Weitere Pflichtangaben sind die Artikelnummer und
mindestens die erste Wiegung. Steht für den ausgewählten Artikel die
Partiezuordnung auf ‚immer mit Partie’, dann wird man durch die Prüfung beim
Abschließen der Wiegung gezwungen eine Partie anzugeben.
Hat man eine Partie
angegeben, dann wird diese Nummer in den Zu- und Abgang übernommen.
Unter dem Direktsprung
[LGU]
für Lagerumbuchung findet man nach der
Vorgangserzeugung den zugehörigen Datensatz.
Zu beachten ist:
Die Lagerplatzabfrage für den Abgang ist auf der Maske
nur aktiv, wenn der Einrichterparameter
‚
Lagerplatzabfrage aktiv
’ entsprechend
gesetzt ist.

---

## Wiegungen aufteilen(LVS)

Wiegungen aufteilen(LVS)

---

## Lohn/Schüttwiegung F8

Lohn/Schüttwiegung F8
Die Lohn-/Schüttwiegung wird gewählt, wenn eine Ladung
z.B. von einem LKW auf eine Waage geschüttet wird. Es wird nur die Ware
gewogen.
Wenn man sich mit
F8
für
eine Lohn/Schüttwiegung entschieden hat, öffnet sich die Wiegemaske, in der man
die wichtigen Angaben für eine Wiegung macht. Man kann individuell festlegen, in
welche Felder der Cursor in welcher Reihenfolge springen soll, so dass die
Angaben zügig gemacht werden können (siehe
Feldreihenfolge festlegen
).
Bei Anwahl dieser Funktion wird die
F3-
Auswahl auf dem Feld Vorlage auf
Vorlagen mit dem Typ Lohnwägung beschränkt. Die Wiegemaske wird mit der zuletzt
verwendeten Vorlage geöffnet, wenn es sich dabei um eine Lohnwägung handelt.
Ansonsten wird die erste Vorlage vom Typ Lohnwägung genommen. Wird keine Vorlage
mit dem Typ Lohnwägung gefunden wird die erste Vorlage genommen, die gefunden
wird.

---

## Maskenfelder der Waage bearbeiten

Maskenfelder der Waage bearbeiten
Mit dieser Funktion können die
Verschobene / Versteckten
Maskenfelder
angezeigt werden.

---

## Mustervorlage in der Waage

Mustervorlage in der Waage
Es ist jetzt möglich eine Mustervorlage eines
Waagensatzes zu erzeugen und diesen abzuspeichern. Die Mustervorlage kann nur
bis zur ersten Wiegung erstellt werden. Diese werden mit dem Waagenstatus 9
gespeichert. Das Speichern und Laden der Mustervorlage funktioniert per Knopf
hinter der Anlieferungsnummer.
Wird die Shift Taste beim Drücken des Knopfes
gedrückt, so wird der Waagensatz als Mustervorlage gespeichert, ohne drücken der
Shift Taste kann eine Mustervorlag ausgewählt werden.
Folgende Felder werden gespeichert:
1.
Kontrakt
2.
Artikel
3.
Bemerkungsfelder
4.
Fahrer
5.
Lkw
6.
Lager
7.
Silo Informationen
8.
Sorten
9.
Kunde
10.
Schlag
11.
Sortentext
12.
Nachhaltigkeitstext

---

## Neue Partie anlegen F8

Neue Partie anlegen F8
Mit dieser Funktion hat man die Möglichkeit, nach
Eingabe eines Artikels direkt eine neue Partie anzulegen und in die Waagenmaske
zu übernehmen. Es öffnet sich das Fenster zum Neuanlegen einer Partie, in dem
die notwendigen Angaben (wie z.B. Gültigkeiten) gemacht werden müssen.
Die Vorbelegung für die Partiebezeichnung wird über
den Einrichterparameter „Vorbelegung der Partiebezeichnung“ bestimmt. Dieser EPA
kann folgende Werte annehmen:
•
Anlieferungsnummer
•
Artikeltext
: Die Artikelbezeichnung
•
Automatisch als Jahr (2st.) und Vertragsnr.
: Die zweistellige
Jahrnummer und die sechsstellige Vertragsnummer. Sollte die Vertragsnummer
kürzer sein, wird sie linksseitig mit Nullen aufgefüllt. Wenn sie länger ist,
werden nur die letzten sechs Stellen verwendet.
•
per Makro
: Es wird das Makro ausgeführt, dass im
Einrichterparameter „Makro zur Vorbelegung der Partiebezeichnung“ eingetragen
ist. Das Makro muss die ermittelte Partiebezeichnung in der LDB-Variablen
LDB_TRANSFER$VC ablegen. Aus technischen Gründen ist es momentan nicht möglich,
einzelne Hochkommata in der erzeugten Partiebezeichnung zu verwenden.

---

## Partie auswählen F7

Partie auswählen F7
Man kann in der Waagenmaske über
F7
entweder eine vorhandene Partie
auswählen oder eine neue anlegen.
Ist in der Waagenmaske bereits ein Artikel
angegeben und man wählt
F7
, öffnet
sich eine Maske für die Partie Verteilung, in der man auf dem Feld Partienr mit
F3
aus vorhandenen Partien auswählen
kann. Die gewählte Partie wird in die Maske Partie Verteilung übernommen und
beim Verlassen dieser in die Waagenmaske eingetragen.
Steht in der
F3
-Auswahl für die Partienr keine Partie
zur Verfügung oder möchte man eine neue Partie anlegen, wählt man
F8
. Es öffnet sich eine Maske für die
notwendigen Angaben (wie z.B. Gültigkeiten) zur neuen Partie. Mit
F9
kann man die neue Partie dann
übernehmen.

---

## Zurücksetzen aller Feldeinstellungen CF11

Zurücksetzen aller Feldeinstellungen CF11
Diese Funktion löscht alle Einstellungen für die
Felder auf der Waagenmaske, die mit den Funktionen
Feldreihenfolge festlegen
,
Felder verstecken
und
Felder verschieben
vorgenommen
wurden.

---

## Speicherung einer Wiegung

Speicherung einer Wiegung
Normalerweise werden Datensätze in der Waage beim
Verlassen der Waagemaske gespeichert.
Es gibt aber ein paar
Spezialfälle:
Fall: Öffnen der Waagenmaske im Neufall und direktes
Anwählen der 1ten Wiegung
Waagedatensätze ohne relevante Eingaben (z.B. Kunde,
Artikel) wurden bisher nur gespeichert, wenn beim Durchführen der ersten Wiegung
eine Wiegenummer ungleich Null angegeben wurde. Der Speichermechanismus wurde
erweitert, so dass der Datensatz nun auch gespeichert wird, wenn das Gewicht der
ersten Wiegung ungleich Null und die Wiegenummer dabei 0 ist.
Fall: Öffnen der Waagenmaske im Neufall und sofortiges
Verlassen mit
ESC
In diesem Fall wurde der Datensatz bisher nicht
gespeichert.
Es gibt aber Firmen, die Datensätze mit Status
„Eröffnet“, aber ohne eine weitere Eingabe speichern möchten. Sie benötigen nur
die Belegnummer, um schon Etiketten drucken zu können, bevor die LKWs an der
Waage ankommen. Wenn der LKW dann kommt, erhält der Fahrer einen Aufkleber und
der Datensatz mit der Belegnummer, die auf dem Aufkleber ist, wird aus den
Datensätzen rausgesucht und entsprechend gefüllt.
Dafür wurde eine Abfrage beim Verlassen der Maske
eingebaut, die erscheint, wenn keine Daten eingegeben wurden. Man hat dann die
Möglichkeit, den Datensatz trotzdem zu speichern.

---

## Vorgang erzeugen F6

Vorgang erzeugen F6
Normalware
Vorgänge können nur erzeugt werden, wenn es sich nicht
um Rohwarewiegungen handelt.
Vorgänge können hier nicht im Stapel erzeugt werden,
sondern nur für jeden Waagedatensatz einzeln. Für die Vorgangserzeugung im
Stapel muss man die Funktion
Vorgänge erzeugen
in der Auswahlliste
anwählen.
Es wurde jetzt die Möglichkeit geschaffen, eine
alternative Vorgangserzeugung an der Waage aufzurufen, dazu wird im
Waagenprozess
eine J-Datei oder
ein Makro angegeben. Dieser Datei wird dann die OwaageId übergeben.
Bei der Vorgangserzeugung kann jetzt der Vorgang
direkt mit ausgedruckt werden. Dazu muss im Waagenprofil auf der
Registerkarte Vorgang
der
Schalter „Vorgang nach der Erzeugung drucken“ auf Ja gestellt werden. Bei der
Funktion Vorgang erzeugen editieren wird der Schalter nicht ausgewertet.
Rohware
Für abgeschlossene Wiegungen mit dem Wiegetyp
Rohwareneingang, Rohwarenausgang oder Lohnwägung kann man in der Auswahlliste
für mehrere Wiegungen und in der Maske für die aktuelle Wiegung Rohwarenbelege
erzeugen.
Beim Start dieser Funktion erscheint eine Abfrage, ob
man Rohwarenbelege erzeugen möchte.
Mit dem Einrichterparameter ‚Feuchte muss zum Erzeugen
von Rohwarenbelegen angegeben werden’ kann man bewirken, dass keine
Rohwarenbelege für Datensätze erzeugt werden, wenn die Feuchte nicht eingetragen
wurde.
Der Status der Wiegung wird auf „mit Vorgang“ gesetzt.
Ist der Wiegetyp Rohwareneingang, wird ein Rohwarenbeleg mit dem EK/VK
Kennzeichen gleich Einkauf erzeugt, den man sich in den EK Rohwarenbelegen
anschauen kann.
Ist der Wiegetyp Rohwarenausgang, wird ein Rohwarenbeleg mit
dem EK/VK Kennzeichen gleich Verkauf erzeugt, den man sich in den VK
Rohwarenbelegen anschauen kann.
Ist der Wiegetyp Lohnwägung, wird ein
Rohwarenbeleg mit einem EK/VK Kennzeichen abhängig von der in der Vorlage
eingegebenen Lohnklasse erzeugt, den man sich dann entsprechend in den EK oder
VK Rohwarenbelegen anschauen kann.
Wenn in einer abgeschlo
[...]


---

## F3 Auswahlen/ Itemboxen für die Vorgangskopie

F3 Auswahlen/ Itemboxen für die Vorgangskopie
Für die Vorgangskopie kann man in den
Wiegeprozessen
für die Waage auf
der
Registerkarte
F3-Auswahlen
Itemboxes angeben. Dies ermöglicht die individuelle Eingrenzung
der auswählbaren Vorgänge auf dem Feld Kunde in der Waagenmaske mit privaten
Itemboxen. In den Standard Itemboxen werden jetzt durch Bediener geblockte
Belege rot angezeigt.
Folgenden Standard Itemboxen stehen zur Auswahl:
Verkauf
1.
IB_KU_MIT_AUFTRAG_WAAGE
2.
IB_KU_MIT_AUFTRAG_nam_waage
Einkauf
1
IB_KU_MIT_BESTELLUNG_WAAGE
2
IB_KU_MIT_BESTELLUNG_nam_waage
Lohn
1.
IB_KU_MIT_AUFTRAG_BESTELLUNG_WAAGE
2.
IB_KU_MIT_AUFTRAG_BESTELLUNG_nam_waage
Weitere Wahlmöglichkeiten:
Diese Itemboxen sollen
als Beispiel/Vorlage dienen, wenn man z.B. verhindern möchte, dass Vorgänge in
der Waage mehrfach auswählbar sind.
Verkauf
1.
IB_KU_MIT_AUFTRAG_OFFEN_WAAGE
2.
IB_KU_MIT_AUFTRAG_OFFEN_nam_WAAGE
Einkauf
1.
IB_KU_MIT_BESTELLUNG_OFFEN_WAAGE
2.
IB_KU_MIT_BESTELLUNG_OFFEN_WAAGE

---

## Vorlage ändern

Vorlage ändern
Mit dieser Funktion kann man im Bearbeiten-Modus der
Waagenmaske das Feld Vorlage zum Bearbeiten freischalten, wenn es geschützt ist.
Nach Auswahl einer neuen Vorlage wird das Feld sofort wieder geschützt.

---

## Waagenterminal einrichten F10

Waagenterminal einrichten F10
Um ein
Waagenterminal
einzurichten, kann in der
Hofliste
F10
gedrückt werden, oder
per aus Direktsprung
[WAMA]
.

---

## Warenausgang Wiegung / Rohwarenausgang F7/CF7

Warenausgang
Wiegung / Rohwarenausgang F7/CF7
Die Warenausgang Wiegung wird gewählt, wenn man einen
Warenausgang einer Ware z.B. auf einem LKW hat. Der LKW und der Fahrer werden
mitgewogen. Die Differenz der beiden Wiegungen ergibt das Gewicht der Ware.
Wenn man sich mit
F7
für einen Warenausgang entschieden hat, öffnet sich die Wiegemaske, in der man
die wichtigen Angaben für eine Wiegung macht. Man kann individuell festlegen, in
welche Felder der Cursor in welcher Reihenfolge springen soll, so dass die
Angaben zügig gemacht werden (siehe
Feldreihenfolge festlegen
).
Handelt es sich bei dem Warenausgang um einen
Rohwarenausgang, kann man dies über die Vorlage entsprechend auswählen (siehe
dazu auch
Vorlage einrichten
). Bei Auswahl der
entsprechenden Vorlage wird der Wiegetyp dann in die Maske übernommen. Aus
Rohwarenwiegungen können später keine Vorgänge, sondern nur Rohwarebelege
erzeugt werden.
Bei Rohwarenwiegungen (Wiegetyp: Rohwareneingang oder
Rohwarenausgang) werden auf der Waagenmaske die Felder für Unterklassen
ausgeblendet. Diese Unterklassen (Klassen 9998 und 9999) sind bei der Erzeugung
von Rohwarebelegen bereits genau festgelegt und können daher auch nicht
abgeändert werden. Daher ist eine Anzeige dieser Felder hier überflüssig.
Bei Anwahl dieser Funktion wird die
F3-
Auswahl auf dem Feld Vorlage auf
Vorlagen mit dem Typ Warenausgang (auch Rohwarenausgang) beschränkt. Die
Wiegemaske wird mit der zuletzt verwendeten Vorlage geöffnet, wenn es sich dabei
um einen Warenausgang handelt. Ansonsten wird die erste Vorlage vom Typ
Warenausgang genommen.
Wird keine Vorlage mit dem Typ Warenausgang gefunden
wird die erste Vorlage genommen, die gefunden wird.

---

## Wiegen F5

Wiegen
F5
Mit der Funktion
Wiegen
wird eine Maske geöffnet, die im
Bedienerstamm
auf der
Registerkarte Waage
hinterlegten Kombinationen von Terminal(
Waagentermina l
) und Prozess(
Waagenvorlagen
) anzeigt. An jeder Schaltfläche ist ein Prozess aus
dem Bedienerstamm hinterlegt. Wird die Schaltfläche betätigt, so wird die
Waagenmaske mit dem jeweiligen Prozess (Terminal, Prozess) gestartet.
Ist im
Bedienerstamm
nur eine aktive Zuordnung zwischen
Terminal und Prozess eingetragen, so wird die Waagenmaske gleich geöffnet, wenn
die Funktion Wiegen aufgerufen wird.
Die Maske ist in drei Bereiche unterteilt.
1.
Eingangswiegungen
kann
Normalware wie Rohware sein
2.
Ausgangswiegungen
kann
Normalware wie Rohware sein
3.
Lohnwiegungen
/
Lagerumbuchungen
Im Bereich Eingangs - Ausgangswiegungen werden jeweils
maximal 12 Kombinationen angezeigt. Im Bereich Lohnwiegungen / Lagerumbuchungen
werden für jede Art maximal 3 Kombinationen angezeigt.
Wurde im Terminal(
Waagenterminal
) ein Bild hinterlegt, so wird dieses Bild auf der Schaltfläche
angezeigt. Ist kein Bild hinterlegt worden, so steht als Text in der
Schaltfläche „Wiegen“.
Wird in der Hofliste
kein Wiegesatz
markiert und die Funktion
Wiegen
wird aufgerufen, so werden alle Möglichkeiten die im
Bedienerstamm
hinterlegt worden sind auf der Maske
angezeigt.
Wurde in der Hofliste
ein Wiegesatz
markiert und die Funktion
Wiegen
wird aufgerufen, so werden nur all die Funktionen angezeigt, die zu dem
markierten Wiegesatz kompatibel sind. Wird dann eine Schaltfläche gedrückt und
dieser Schaltfläche ist ein anderes
Waagenterminal
zugeordnet als das
Waagenterminal
des
Wiegesatz, so wird das
Waagenterminal
des Wiegesatzes mit dem an
der Schaltfläche hinterlegen
Waagenterminal
überschrieben.
Private Funktion
Es besteht die Möglichkeit diese Mechanik zu
privatisieren. Dabei wird nicht mehr die Auswahlmaske aufgerufen, sondern direkt
die Waagenmaske. Die Waagenmaske wird dann mit dem im Bedienerstamm hinterlegten
Prozess
[...]


---

## Wiegeprozesse festlegen SF8

Wiegeprozesse festlegen SF8
Mit dieser Funktion wird der Pfleger aufgerufen mit
dem die
Wiegeprozesse
eingerichtet werden.

---

## Wareneingang Wiegung / Rohwareneingang F6/SF6

Wareneingang
Wiegung / Rohwareneingang F6/SF6
Die Wareneingang Wiegung wird gewählt, wenn man einen
Wareneingang einer Ware z.B. auf einem LKW hat. Der LKW und der Fahrer werden
mitgewogen. Die Differenz der beiden Wiegungen ergibt das Gewicht der
angelieferten Ware.
Wenn man sich mit F6 für einen Wareneingang entschieden
hat, öffnet sich die Wiegemaske, in der man die wichtigen Angaben für eine
Wiegung macht. Man kann individuell festlegen, in welche Felder der Cursor in
welcher Reihenfolge springen soll, so dass die Angaben zügig gemacht werden
können (siehe
Feldreihenfolge festlegen
).
Handelt es sich bei dem Wareneingang um einen
Rohwareneingang, kann man dies über die Vorlage entsprechend auswählen (siehe
dazu auch
Vorlage einrichten
). Bei Auswahl der
entsprechenden Vorlage wird der Wiegetyp dann in die Maske übernommen. Aus
Rohwarenwiegungen können später keine Vorgänge, sondern nur Rohwarebelege
erzeugt werden.
Bei Rohwarenwiegungen (Wiegetyp: Rohwareneingang oder
Rohwarenausgang) werden auf der Waagenmaske die Felder für Unterklassen
ausgeblendet. Diese Unterklassen (Klassen 9998 und 9999) sind bei der Erzeugung
von Rohwarebelegen bereits genau festgelegt und können daher auch nicht
abgeändert werden. Daher ist eine Anzeige dieser Felder hier überflüssig.
Bei Anwahl dieser Funktion wird die
F3
-Auswahl auf dem Feld Vorlage auf
Vorlagen mit dem Typ Wareneingang (auch Rohwareneingang) beschränkt. Die
Wiegemaske wird mit der zuletzt verwendeten Vorlage geöffnet, wenn es sich dabei
um einen Wareneingang handelt. Ansonsten wird die erste Vorlage vom Typ
Wareneingang genommen.
Wird keine Vorlage mit dem Typ Wareneingang gefunden
wird die erste Vorlage genommen, die gefunden wird.

---

## Wiegeprozess festlegen

Wiegeprozess festlegen
Mit dieser Funktion wird der Pfleger aufgerufen mit
dem die
Wiegeprozesse
eingerichtet werden.

---

## Wiegung automatisch F5

Wiegung automatisch F5
Die Wiegung wird automatisch durchgeführt. Die Werte
der Waage werden an das System übertragen.
Es wird vom System erkannt, ob es
sich um die 1. Wiegung handelt oder ob schon eine Wiegung existiert und somit
die 2. Wiegung stattfindet.

---

## Wiegeschein drucken

Wiegeschein drucken
Es gibt die Möglichkeit, für den Anlieferer einen
Wiegeschein als Beleg zu drucken, auf dem festgehalten ist, wieviel Ware
angeliefert wurde, sobald die Wiegung mindestens den Status Abgeschlossen hat.
Erst dann erscheint diese Funktion in der OptionBox der Waagenmaske.
Im Feld Formular auf der Waagenmaske wird festgelegt,
welchen Wiegeschein man drucken will.
Im Feld Drucker wird festgelegt, auf
welchem Drucker gedruckt werden soll.
Im Formulareinrichter zum Wiegeschein gibt es im
Wiegekopf (Bereich 1000) einige Positionen, die einem das Erstellen eines
Wiegescheines erleichtern. Das sind z.B. die Positionen
453 (Zugriff auf Owaage Daten)
454 (Zugriff auf Owaage Addon Daten)
106 (ID_KUNDNUMMER)

---

## Wiegungen abschliessen

Wiegungen abschliessen
Wiegungen kann man an zwei Stellen der Online-Waage
abschließen:
In der Auswahlliste
F11
:
Man kann einen oder mehrere Datensätze mit Status 2te
Wiegung markieren und abschließen. Es erscheint eine Abfrage, ob man die
Wiegungen wirklich abschließen möchte.
Wenn man keinen bestimmten Datensatz
markiert hat und Wiegungen abschließen wählt, erscheint eine Abfrage, ob man
wirklich alle Datensätze abschließen möchte. Bestätigt man dann mit Ja, werden
alle Wiegungen in der Auswahlliste mit Status 2te Wiegung abgeschlossen.
Sind
Wiegungen dazwischen, die diesen Status nicht haben, erhält man eine Mitteilung,
dass diese nicht abgeschlossen werden konnten.
Der Status der Wiegungen, die
abgeschlossen werden konnten, wird auf abgeschlossen gesetzt.
In der Waagen-Maske
F11
:
Hier kann man die in der Maske geöffnete Wiegung
abschließen, wenn der Status 2te Wiegung ist.
Bei angeschlossener
Silo
/
Ladeträgerverwaltung
wird die Wiegemenge in
die zugewiesenen Silo / Ladeträger gebucht. Ausführliche Informationen zu diesem
Punkt ist in der Hilfe
Ladeträgerverwaltung an der
Waage
beschrieben.
Ist der Schalter „
Bei
Restmengenüberschreitung Nettomenge aufteilen
“ im Wiegeprozess auf der
Registerkarte Rohware auf „Ja“ gestellt, wird bei Abschluss der Wiegung
automatisch geprüft, ob die Nettowiegemenge nach Abzug der Qualitäten die
Kontraktrestmenge nicht übersteigt. Ist dies der Fall, wird der Überschuss auf
einen weiteren Kontrakt verteilt, falls einer vorhanden ist. Eine automatische
Aufteilung auf mehr als zwei Kontrakte ist nicht vorgesehen.

---

## Wiegungen raffen SF10

Wiegungen raffen SF10
Über
SF10
hat man die Möglichkeit, mehrere Wiegungen zusammenzufassen:
Auf der Auswahlliste markiert man die Wiegungen, die
man raffen möchte. Dann wählt man die Funktion
Wiegungen raffen
und es öffnet sich ein
Fenster, in dem im oberen Bereich angezeigt wird, welche Wiegungen gerafft
werden sollen. Im unteren Bereich wird der aus dem Raffen entstehende Datensatz
angezeigt. (Ist dies nicht der Fall hilft ein Return im Feld Raffen, wo der
Cursor steht oder ein Klick mit der Maus in das darunterliegende Feld).
In der Spalte Raffen hat man nun noch die Möglichkeit,
Datensätze vom Raffen auszunehmen, indem man die entsprechende Zeile mit Nein
versieht. Der Datensatz im unteren Bereich wird dann entsprechend neu
berechnet.
Mit
F10
startet man das
Raffen.
Nach einer kurzen Sicherheitsabfrage wird durch Bestätigen mit Ja der
zusammengefasste Datensatz erzeugt und die anderen Datensätze werden auf
gelöscht gesetzt. Man erhält einen Hinweis, dass die Raffung durchgeführt
wurde.
Über den Einrichterparameter „Funktion für Raffen
der Wiegungen“ der Maske „Wiegungen raffen“ kann man festlegen, wie die
Datensätze zusammengefasst werden sollen. Es stehen zwei Funktionen zur
Verfügung.
AMIC_WAAGE_RAFFEN : Die Menge wird summiert und die
Feuchte gemittelt
AMIC_WAAGE_RAFFEN_GEWM: Die Menge wird summiert und
die Feuchte wird gewichtet gemittelt
Hier sind auch private Anpassungen über neue
Funktionen möglich, die dann im Einrichterparameter angegeben werden.

---

## Kontraktverteilung in der Waage

Kontraktverteilung in der Waage
Das Waagemodul wurde um die Kontraktverteilung
erweitert. Die Kontraktverteilung kann auf der Registerkarte LVS/Silo/Kontrakt
vorgenommen werden. Soll der Wiegung nur ein Kontrakt zugeordnet werden, so kann
die Kontraktzuordnung wie gewohnt über das Kontraktfeld auf der Registerkarte
Wiegungen vorgenommen werden. Ist in der Datentabelle Kontraktzuordnung mehr als
ein Eintrag vorhanden, so wird das Kontraktfeld auf der Registerkarte Wiegung
gesperrt.
Besonderheit
Bei der Vorgangserzeugung wird immer pro Zeile in der
Datentabelle Kontraktzuordnung ein neuer Waagensatz erzeugt. Es wird bei der
Vorgangserzeugung kein Vorgang erzeugt, der eine Warenposition und N
Kontraktzeilen hat.
Wiegebelege, die eine Kontraktzuordnung mit
mehreren Kontrakten haben, können nur aus der Hofliste erzeugt
werden
.
Datentabellenbeschreibung
Kontraktaufteilung
Feldname
Bedeutung
Kontraktnummer
In
      diesem Feld wird die Kontraktnummer eingetragen.
Menge
In
      diesem Feld wird die Menge eingetragen. Sie wird immer in die
      Mengeneinheit des Kontraktes umgerechnet. Ist die eingegeben Menge kleiner
      als die Wiegemenge, so wird automatisch eine Position mit der Restmenge
      angefügt. Die Restmenge wird in der Mengeneinheit der Wiegung dargestellt.
Falls die automatische
      Kontraktaufteilung aktiviert ist und ein zweiter aktiver Kontrakt
      existiert, welcher die Übermenge fassen kann, wird die Übermenge
      automatisch auf diesen gebucht.
Sollte kein Kontrakt existieren,
      welcher die komplette Übermenge aufnehmen kann, aber zumindest noch ein
      Kontrakt der einen Teil hiervon aufnehmen kann, so wird dieser bebucht.
      Der dann noch verbliebene Rest wird auf den Tagespreis gebucht (Kontrakt
      0).
Bei
      einer abweichenden Einheit von Kontrakt 1 zu Kontrakt 2 kann es zu
      Rundungsfehlern kommen.
ME-Bezeich
Mengeneinheit des
      Kontraktes
Laufzeitab
Begin der Laufzeit des
      Kontrakt
[...]


---

## Waagenvorlage in Vorgangsunterklasse [FRZ] festlegen

Waagenvorlage in Vorgangsunterklasse [FRZ] festlegen
Im Feld ‚Vorlage für OnlineWaage in Vorgangserzeugung’
wird festgelegt welche Vorlage für die erst oder zweit Wiegung in einem
entsprechenden Vorgang (Vorgangsklasse/-unterklasse) verwendet werden soll. Ohne
Angabe einer Vorlage kann die Wiegung aus den Positionen heraus nicht angestoßen
werden.

---

## Funktion Vorlage als Menüpunkt SF9

Funktion Vorlage als Menüpunkt
SF9
Wenn man in der Auswahlliste der Vorlagen eine Vorlage
markiert, erscheint in der Option Box diese Funktion.
Sie bewirkt, dass die
markierte Vorlage als private Funktion in die OptionBox der Waagen-Auswahlliste
eingetragen wird. Dieser Eintrag erhält den Namen der Vorlage.
Über den Punkt
Dieses Menü
, dann Anwählen der
OB_Hofliste und Aufruf von
Private
Sortierung/Tasten
F5
in der
Waagen-Auswahlliste kann man dann die Sortierung der privaten Funktion sowie
z.B. ein Tastenkürzel bestimmen.
Wählt man nun diese als Menüpunkt eingefügte Funktion
in der Waagen-Auswahlliste an, dann öffnet sich die Waagenmaske mit der
verknüpften Vorlage und allen in ihr hinterlegten Einstellungen (wie z.B.
Wiegetyp, Terminal).
Die ursprünglichen Funktionen
WE Wiegung
F6
,
WA
Wiegung
F7
und
Lohn/Schüttwiegung
F8
können weggeschützt und dafür eigene
Funktionen passend zu den häufig verwendeten Vorlagen angelegt werden.

---

## Prozess einrichten

Prozess einrichten
Es ist möglich, über
SF8
Vorlagen einzurichten, die man dann
über
F3
auf dem Feld Vorlage in der
Waagenmaske auswählen kann.
In der Vorlage können wichtige Voreinstellungen
gemacht werden, die einem das Arbeiten an der Waage erleichtern.
Einstellungen
Feld
Beschreibung
Name
Name
      vom Waageprozess
Bezeichnung
Bezeichnung für den
      Waagenprozess
Wiegetyp
In
      diesem Feld wird der Wiegetyp für die Waagenvorlage
      festgelegt.
Nummer
Wiegetyp
1
Wareneingang
2
Warenausgang
3
Rohwareneingang
4
Rohwarenausgang
5
Lohnwägung
6
Lagerumbuchung
Nummernkreis
Man
      kann in der Vorlage einen Nummernkreis für die Belegung der Belegnummer
      hinterlegen.
Wird hier keiner angegeben (Default ist 0), dann wird wie
      bisher der Nummernkreis aus dem Mandantenstamm (der dort pro
      Bedienerklasse hinterlegt werden kann) genommen.
Beim
      Öffnen der Waagemaske wird die Belegnummer aus dem entsprechenden
      Nummernkreis vorbelegt. Wechselt man die Vorlage, wird diese Belegnummer
      wieder freigegeben und eine neue Belegnummer gezogen. Diese stammt
      entweder aus dem Nummernkreis der Vorlage oder aus dem
      Mandantenstamm.
Das
      ist aber nur dann notwendig, wenn die neue Vorlage einen anderen
      Nummernkreis als die alte enthält.

---

## Pflichtfelder an der Waagenmaske

Pflichtfelder an der Waagenmaske
Es wurde die Möglichkeit geschaffen auf der
Waagenmaske Pflichtfelder abzufragen. Dazu werden im
Waagenprozess
die Pflichtfelder auf der
Registerkarte
Bildschirm
definiert. Die Waagenmaske kann erst nach den Eingaben der Pflichtfelder
verlassen werden.

---

## Variante Inaktive Arbeitsprofile

Variante Inaktive Arbeitsprofile
Nachdem ein Waagenprofil aus den Mustervorlagen
verschoben worden ist, kann dieses an dieser Stelle bearbeitet werden. Des
Weiteren können an dieser Stelle eigene Waagenprofile erstellt werden.
Folgende Funktionen stehen zur Verfügung
1.
Anlegen eines neuen Waagenprofils
2.
Ändern eines Waagenprofils
3.
Ansehen eines Waagenprofils
4.
Löschen eines Waagenprofils

---

## Variante Branchen-ERP-Mustervorlagen

Variante Branchen-ERP-Mustervorlagen
Die Branchen-ERP-Mustervorlagen können bei der Integration
eines Wägesystemes als Vorlage dienen, die nur noch für die eigenen Zwecke
angepasst zu werden braucht.
Folgende Muster werden zurzeit ausgeliefert
Name
Aktiv
Auslieferung
Dokumentation
Branchen-ERP
      STANDARDWAAGE
Nein
11.07.2008
Nein
Branchen-ERP
      SOEHNLE
Nein
05.05.2014
Nein
Branchen-ERP
      Sartorius PR1613
Nein
02.04.2014
Nein
Branchen-ERP
      VIDRA SJ
Nein
11.09.2008
Nein
Branchen-ERP
      Testwaage
Nein
08.08.2008
Nein
Branchen-ERP
      ESSMANN TCP
Nein
02.07.2008
Nein
Branchen-ERP
      Minipond25-PMN ( ULTSCH )
Nein
20.05.2008
Nein
Branchen-ERP
      Vibra DJ und DJH Feinwaag
Nein
01.01.2008
Nein
Branchen-ERP
      AND GP-12K Laborwaage
Nein
01.01.2008
Nein
Branchen-ERP
      CONTADOR Körnerzählgerät
Nein
24.01.2008
Nein
Branchen-ERP
      Pfister DWT 410
Nein
25.09.2007
Nein
Branchen-ERP
      VBS
Nein
22.03.2007
Nein
Branchen-ERP
      ESSMANN
Nein
22.03.2007
Nein
Branchen-ERP
      Spool
Nein
14.03.2006
Nein
Branchen-ERP
      IT3000E
Nein
31.01.2006
Nein
Branchen-ERP
      RAG 701
Nein
07.03.2005
Nein
Branchen-ERP
      Widra 300 S
Nein
29.11.2004
Nein
Branchen-ERP
      Disomat B [ DDP8785 ]
Nein
09.08.2004
Nein
Branchen-ERP
      Weberwaage
Nein
18.05.2004
Nein
Branchen-ERP
      Netscale
Nein
29.04.2004
Nein
Branchen-ERP
      Minipond 85 ( DSV )
Nein
24.03.2004
Nein
Branchen-ERP
      Pfister DWT 6/11
Nein
24.03.2004
Nein
Branchen-ERP
      RHEWA Auswertegerät 84
Nein
17.03.2004
Nein
Branchen-ERP
      Minipond 85
Nein
24.02.2004
Nein
Branchen-ERP
      IT6000 B
Nein
28.01.2004
Nein
Branchen-ERP
      MiniPond25-PMN
Nein
26.01.2004
Nein
Branchen-ERP
      IT6000
Nein
27.01.2004
Nein
Mit der Funktion „ins Arbeitsprofil“ (F10) lässt sich
ein Waagenprofi ins Arbeitsprofil kopieren.
Das kopierte Waagenprofil findet sich nach
Durchführung in der Variante „Inaktive Arbeitsprofile“ wieder und kann dort ggf.
verändert werden. Die Branchen-ERP-Mustervorlagen bleiben von der Maßnahme unberührt und
können ggf. für weitere Arbeitsprofile herhalten.

---

## Waagensteuerung

Waagensteuerung

---

## Versteckte Verschobene Felder auf der Waagenmaske

Versteckte Verschobene Felder auf
der Waagenmaske
Versteckte Felder
In dieser Variante befinden sich alle Felder, die
nicht auf der Maske angezeigt werden. Neu hinzugefügte Felder auf der Maske
werden automatisch als Versteckte Felder eingetragen. Die neuen Felder habe den
Status „per Update“ auf „Ja“ stehen. Damit ausgeblendete Felder wieder auf der
Maske angezeigt werden sollen, werden dies einfach über
Löschen
F7
ausgelöscht.
Verschobene Maskenfelder
Sobald ein Feld mit dem Widgetnavigator verschoben
worden ist, werden alle Felder der Waagenmaske in dieser Variante angezeigt.
Verschobene Felder können mit
Löschen
F7
aus der Liste gelöscht werden, dann
werden diese Felder wieder an ihrem Ursprünglichen Platz angezeigt. Mit
Ändern
F5
kann das Feld unabhängig des
Widgetnavigators auf eine andere Position verschoben werden

---

## Online Wiegen in der Vorgangserzeugung

Online Wiegen in der
Vorgangserzeugung

---

## Anzahl Wiegungen für Wiegetyp Lohnwägung in der Vorlage festlegen

Anzahl Wiegungen für Wiegetyp Lohnwägung in der Vorlage festlegen
Ist die verwendete WaagenVorlage vom Typ Lohnwägung,
dann muss dort noch festgelegt werden nach wie vielen Wiegungen der Waagenbeleg
auf den Status ‚mit Vorgang’ gesetzt werden soll. Vorbelegung ist ‚zwei
Wiegungen’.

---

## Wiegen in Lagerumbuchung

Wiegen in Lagerumbuchung
Bei der Erfassung der Lagerumbuchung kann jetzt die
ausgehende und eingehende Artikel Menge gewogen werden. Es müssen unter
[FRZ]
auch Waagenvorlagen für die
Lagerumbuchung eingetragen werden. Es ist kann erst gewogen werden, wenn unter
dem Lagerstamm ein Kunde dem Lager zugewiesen wurde, denn die Onlinewaage
benötigt für eine korrekte Wiegung einen Kunden. Die Rückwiegung findet analog
zu der Wiegung im Vorgang statt.

---

## Wiegen in Vorgangserfassung

Wiegen in Vorgangserfassung
Bei der Erfassung eines Vorganges (z.B. Lieferschein)
ist es zunächst notwendig für die Position einen Artikel anzugeben. Ohne Eingabe
eines Artikels kann nicht gewogen werden, denn der ist unbedingt notwendig für
die Anlage eines Waagedatensatzes.
Danach kann die Funktion
Wiegen
aus der Option Box aufgerufen
werden.
Es wird ein neuer Waagedatensatz angelegt. Die Inhalte der Felder
Kunde, Artikel, Lager und Lagerplatz werden in den Waagedatensatz mit
übernommen. Wurde vorm Wiegen auch eine Partie für die Position hinterlegt, dann
wird diese auch übertragen. Bei Angabe mehrerer Partien wird die erste Partie
übernommen.
Dann wird eine automatische Ampelwiegung durchgeführt. Das
gewogene Gewicht wird in das Feld Menge der Positionszeile übernommen und
validiert. Die Id des neu angelegten Waagedatensatzes wird in die Warenbewegung
übergeben.
Um eine zweite Wiegung durchzuführen, wählt man erneut die
Funktion
Wiegen
im Vorgang an. Die
Differenz der beiden Wiegungen wird in das Feld Menge übernommen und validiert.
Der Waagedatensatz wird auf den Status ‚mit Vorgang’ gesetzt.
Um eine Rückwiegung durchzuführen, ohne den Vorgang zu
öffnen, gibt es jetzt eine eigene Variante (Offene Waagenbelege z.B. unter der
Anwendung Lieferschein Bearbeiten
[LIB]
). Hier kann in der Auswahlliste ein
Datensatz markiert und durch Ausführen der Funktion
Rückwiegung
wird die Menge im Vorgang
automatisch gesetzt.
Beim Speichern des Lieferscheines wird dessen VorgangsId
in den erzeugten Waagedatensatz eingetragen, so dass die Verbindung der beiden
Datensätze hergestellt ist.
Wird der Vorgang (Lieferschein) zwischen der ersten
und zweiten Wiegung verlassen/gespeichert, dann gibt es in der OnlineWaage
Datensätze mit dem Status ‚erste Wiegung’ und einer VorgangsId.
Da diese
Datensätze von der OnlineWaage aus nicht mehr geändert werden dürfen (die
Änderung würde nicht in den Lieferschein übertragen werden) werden sie dort nur
noch geschützt angeze
[...]


---

## Wiegen in Rohwareerfassung

Wiegen in Rohwareerfassung
Bei der Erfassung einer Rohwarenlieferung ist es
zunächst notwendig einen Artikel und einen Kunden anzugeben. Ohne Eingabe eines
Artikels und Kundens kann nicht gewogen werden, denn diese Angaben sind
unbedingt notwendig für die Anlage eines Waagedatensatzes.
Die Funktion
Wiegen
ist in der Option Box nur
anwählbar, wenn der Cursor im Feld Menge steht.
Wird diese Funktion
aufgerufen, dann wird ein neuer Waagedatensatz angelegt und die erste Wiegung
als Ampelwiegung ausgeführt. Das gewogene Gewicht wird in das Feld Menge
übernommen und die Id des neu angelegten Waagedatensatzes an den
Rohwaredatensatz übergeben.
Um eine zweite Wiegung durchzuführen wählt man
erneut die Funktion
Wiegen
an. Die
Differenz der beiden Wiegungen wird in das Feld Menge übernommen. Der
Waagedatensatz wird auf den Status ‚mit Vorgang’ gesetzt.
Beim Speichern des
Rohwarenbeleges wird dessen VorgangsId in den erzeugten Waagedatensatz
eingetragen, so dass die Verbindung der beiden Datensätze hergestellt ist.

---

## Aktiv Passivsetzung

Aktiv Passivsetzung
Es können ALLE in der Auswahlliste angewählten
Aktiv-Passiv Kennzeichen umgewandelt werden, steht ein Kennzeichen auf aktiv, so
wird es passiv und umgekehrt.

---

## Altteilsteuer

Altteilsteuer
Allgemein
Die Umsätze beim Austauschverfahren in der
Kraftfahrzeugwirtschaft sind in der Regel Tauschlieferungen mit Baraufgabe. Der
Lieferung eines aufbereiteten funktionsfähigen Austauschteils (z.B. Motor,
Aggregat,...) durch den Unternehmer der Kraftfahrzeugwirtschaft stehen eine
Geldzahlung und eine Lieferung des reparaturbedürftigen Kraftfahrzeugteils
(Altteils) durch den Kunden gegenüber. Als Entgelt für die Lieferung des
Austauchteils sind demnach die vereinbarte Geldzahlung und der gemeine Wert des
Altteils anzusetzen. Dabei könne Altteile mit einem Durchschnittswert von
10.v.H. des Bruttoaustauschentgeldes bewertet werden. Als Bruttoaustauschentgeld
ist der Betrag anzusehen, den der Endabnehmer für den Erwerb eines dem
zurückgegebenen Altteil entsprechenden Austauschteil abzüglich Umsatzsteuer,
jedoch ohne Abzug eines Rabattes zu zahlen hat. Setzt ein Unternehmer bei der
Abrechnung an Stelle des Durchschnittswerts andere Werte an, so sind die
tatsächlichen Werte der Umsatzsteuer zu unterwerfen.
(Siehe auch UstR 153)
Beispiel
Bei einem PKW wird die Lichtmaschine ausgetauscht.
Diese hat einen Nettowert von 350,00 Euro. In der Rechnung über die Lieferung
des Austauschteils braucht der Wert des Altteils nicht in den Rechnungsbetrag
einbezogen werden. Es genügt, dass der Unternehmer den auf den Wert des Altteils
entfallenden Steuerbetrag angibt.
Austauschlichtmaschine
350,00
€
+ Ust (19%)
66,50
€
+ Ust (19%) auf den Wert des Altteils von 100,00
      €
(10% von 350,-- €)
6,65
€
---------
--
423,15
€
Altteile in Referenz-ERP
Unter Referenz-ERP gibt es keine Möglichkeit einen
Steuersatz so einzurichten, dass er sich auf 10 v.H. einer Bemessungsgrundlage
bezieht, der bereits ein anderer Steuersatz zugeordnet ist. In der
Finanzbuchhaltung kann man jedoch über das Bebuchen der
Steuerkonten erreichen, dass der entsprechende Steuerbetrag auf das Konto
gelangt. Die Bemessungsgrundlage und die daraus entstehende Steuer ist selbst zu
errechnen.

---

## Branchen-ERP-Standardwaagenprofil

Branchen-ERP-Standardwaagenprofil
Vorbereitende Maßnahmen am vorgesehen
Wiegesystemstandort
Referenz-ERP hat mit dem Branchen-ERP-STANDARD-WAAGENPROFIL eine
genormte Schnittstelle mit fest vorgegebenen Parametern bekommen und jedes
Wiegesystem was diese genormte Schnittstelle erfüllt, ist ohne Probleme zu
erwarten in das Referenz-ERP-Wiege-System zu integrieren.
Ob ein Wiegesystem die minimalen Anforderungen des
Branchen-ERP-STANDARD-WAAGENPROFILS erfüllt, lässt sich schon ohne Referenz-ERP-Installation
vor Ort beantworten.
Wenn Sie prüfen möchten, ob Ihr Wiegesystem den
Anforderungen des Branchen-ERP-STANDARD-WAAGENPROFILS genügt, bringen Sie bitte in
Erfahrung ob es eine existierende Softwarelösung gibt, mit deren Hilfe man eine
Datei erzeugen  kann, die auf Anforderung mindestens die Daten Gewicht und
Alibi- bzw. Wiegenummer enthält. Achten Sie bitte sehr genau darauf, dass im
Falle von eichfähigen Wiegungen unbedingt eine Referenznummer des Wiegesystems
übermittelt wird. Referenz-ERP ermöglicht es so dem Eichamt die entsprechende
Information für eine Recherche der Beamten im Wiegesystem an die Hand
zugeben.
Möglicherweise bieten Wiegesystemanbieter bereits die
Möglichkeit, ein vom Wiegesystemanbieter zur Verfügung gestelltes Programm
aufzurufen, von dem man die Ausgabe in eine Datei umleiten kann bzw. welche man
per Parameter mitteilen kann, wo es die Ausgabe abzulegen hat. Wenn es solche
Lösung nicht direkt gibt, dann besteht eventuell die Möglichkeit die
Wiegesoftware zu automatisieren, um das gewünschte Ergebnis z.B. per Vbscript
abzubilden.  Andernfalls setzen Sie sich mit dem betreuenden
Wiegesystemhaus in Verbindung um die Möglichkeiten abzuschöpfen. Eventuell
besteht auch die Option sich eine solche Software als Auftragsarbeit erstellen
zu lassen.
Für einige Wiegesysteme hat Branchen-ERP selbst externe
Programme geschaffen, die den Anforderungen des Branchen-ERP-STANDARD-WAAGENPROFILS
genügen. Dieses sind natürlich meistens sehr spezielle Lösungen, die als
Auftragsarbeit durchgeführt worden sind und
[...]


---

## Branchen-ERP UDP-Client

Branchen-ERP UDP-Client
Der Branchen-ERP UDP-Client ist entwickelt worden um den
Datentransfer mit dem Schenk-Waagenwiegeterminal
DISOMAT Tersus
durchzuführen. Der UDP-Client ist als Standalone-Applikation konstruiert
worden.
Mit diesem Produkt sind somit gewährleistet:
Es kann für technische Connectivity-Prüfungen
herangezogen werden.
Es kann direkt durch durch Referenz-ERP über das
Standard-Branchen-ERP-Waagenprofil-Verfahren eingesetzt werden
Weiterentwicklungen des UDP-Clienten bedürfen keines
Referenz-ERP-Gesamt-Updates
Für den
DISOMAT Tersus
sind 3
Kommunikations-Protokolle implementiert worden. Diese bauen technisch jeweils
aufeinander auf. Ziel war es dafür zu sorgen dass die Schenck
Process-Norm-Prozedur (DDP 8672) abgewickelt werden kann. Diese sorgt für einen
gesicherten Transport der Wiegedaten im Eichbetrieb der Waage.
Die UDP-Schnittstelle von Schenck ist folgendermaßen
aufgebaut bzw. macht folgende Vorgaben, die durch den UDP-Clienten abgewickelt
werden:
2 UDP/IP Schnittstellen als weitere "virtuelle
serielle Schnittstellen" vorzugsweise zur Kopplung mit der EDV
Schnittstelle.
Unter 432:Schnittstellen können die neuen
Schnittstellen "NW1" und "NW2" angewählt werden. Nach Anwahl einer der beiden
"Schnittstellen" kann als einziger Parameter die "Fern-IP-Adresse" konfiguriert
werden. Diese legt fest, zu welcher Server-IP
aktive
Ausgaben geschickt
werden.
Unter 4331:Edv kann dann NW1 bzw NW2 als
"Schnittstelle" gewählt werden. Der DISOMAT öffnet dann für NW1 den UDP Port 350
und für NW2 den UDP Port 351. Über diesen können externe Programme "Datengramme"
an den DISOMAT übertragen, die vorzugsweise jeweils eine ganze "EDV-Einheit"
(Ack, Nac, Telegramm) enthalten.
Mit Eingang des ersten Datengramms einer Gegenstelle
schaltet der DISOMAT den UDP Port in den
verbundenen
Modus, d. h. er
akzeptiert ab jetzt nur noch Datengramme von der Gegenstelle, die das Datengramm
geschickt hat und er antwortet auch nur dieser Gegenstelle. Dieser
verbundene
Modus endet 45 Sekunden nach
[...]


---

## Bruttokennzeichen, Gesamtpreiskennzeichen

Bruttokennzeichen, Gesamtpreiskennzeichen
Das Bruttokennzeichen besagt, ob es sich bei dem Preis
um einen Bruttopreis handelt (Wert1=1) oder nicht (Wert1=0). Ist dieser Wert
nicht lesbar, wird 0 angenommen.
Das Gesamtpreiskennzeichen besagt, ob es sich bei dem
Preis um einen Gesamtpreis handelt (Wert1=1) oder nicht (Wert1=0). Ist dieser
Wert nicht lesbar, wird 0 angenommen.
(Zugehörige
Parameter: BRUTTOPREIS_SAx, GESPREIS_SAx)

---

## Einrichtungshilfen :

Einrichtungshilfen :
In dem Waageprozess muss eine spezielle
Vorgangserzeugungsfunktion eingetragen werden.

---

## Excel Anbindung

Excel Anbindung
Werden Wiegedaten über eine Excel Mappe verarbeitet,
dann können diese durch ein einfaches Makro auch dem Offline-Waagesystem zur
Verfügung gestellt werden.

---

## Import-Script WaagenImport

Import-Script WaagenImport
Das Pascal-Script WaagenImport führt die erste Stufe
des Datenimportes durch: Das Einlesen der ASCII-Daten von dem Datenträger in
Zwischenrelationen.

---

## Integration des Branchen-ERP UDP-Client als Anwendung der Branchen-ERP-Standardwaage

Integration des Branchen-ERP UDP-Client als Anwendung der Branchen-ERP-Standardwaage
Es wird die Verwendung
dieses Clienten nicht länger empfohlen. Bitte stellen Sie wenn möglich auf
Aeinswiege
um!
In einem ersten Schritt legt man sich das
Arbeitsgerüst des Waagenprofils an, das wie folgt aussieht:
Die Beispiel-Wiegung des Branchen-ERP-UDP_Clieneten lässt sich
hervorragend dafür verwenden die nachfolgende Auswertung des Wertestrings in
Referenz-ERP verwenden und kann einfach durch markieren im Clienten und mit Copy und
Paste zunächst in das Beispiel-Feld übertragen werden:
Für die direkte Verwendung muss nun noch die
Steuerzeichen-Sequenzen um ihre numerische Anreicherung erleichtert werden:
Daraufhin erfolgt die inhaltliche Zuordnung und
Sicherstellung das es sich um einen gültigen Wiegestring handelt:
Als letzter Schritt muss eine Ableitung des Scriptes
AMIC_STANDARDWAAGE gebildet werden. Der Name dafür sollte wie oben vorgesehen
TERSUS_AMIC_STANDARDWAAGE sein.
Der Bereich zwischen den Gleichheitszeichen ist der
einzige der angepasst werden muss.
Er sorgt im Wesentlichen für den geeigneten
Parameter-Aufruf von AMIC_UDP_CLIENT.exe
Nun wird das System bei einer Testwiegung, oder aus
der WAM-Auswahlliste heraus per „Probewiegung“ in der Lage sein ein Ergebnis zu
liefern.
Anmerkung:
So wie sich das System jetzt darstellt, ist es in
folgenden Szenarien einsetzbar:
dedizierter Einzelplatz
Punkt 1 impliziert dedizierten
Terminalservereinsatz
Da der DISOMAT Tersus in der Konfiguration eine feste
IP-Adresse hinterlegt und sich damit auf einen festen Kommunikationspartner
beschränkt ist das vorliegende System nicht ohne weiteres direkt einsetzbar in
Citrix-Load-Balancing – Systemen. Dort müsste die Verwendung auf einen
Terminalserver fest vorgegeben werden. Des Weiteren ist der Einsatz also
insbesondere nicht mehrplatzplatzfähig.
Branchen-ERP hat aber inzwischen Mittel und Wege auch diese
beiden Handicaps softwaretechnisch zu lösen. ( Branchen-ERP – Waagenclient/Waagenserver
– System )

---

## Kurzanleitung

Kurzanleitung
Waagenprofil-Erstellung unbekannter Wiegesysteme
1.
Ermittlung des Anschlusses ( COM1, COM2, …)
2.
COM-Port testen mit „Teste Port“
3.
Verbindungsparameter ermitteln
4.
Gewichtsanforderung bzw. irgendwelche Vorläufe in Erfahrung bringen
5.
Mit Registerkarte und F11 probewiegen.
6.
DANN Ergebnis nach Registerkarte Beispiel kopieren
7.
Nun reguläre Ausdrücke bilden um das gewünschte Ziel zu erreichen.

---

## Kurzübersicht

Kurzübersicht
Rohwarenanlieferung
erfassen
[RWB]  in
Rohwarenabrechnung gehen
F8
in Rohwarenanlieferungserfassung gehen
Artikel eingeben bzw. auswählen
Abrechnungsschema auswählen
Kunde eingeben bzw. auswählen
Liefernummer und -datum vom Wiegeschein/
Annahmeschein übernehmen
Liefermenge eintragen mit F5 oder Gesamtmenge direkt eingeben
Qualitätskennzeichen lt. Menü eintippen
Kostenmerkmale z.B. Erzeugerbeitrag mit MINUS erfassen
Zahlungsart
und Zahlungsbedingungen eingeben
Immer pro Abrechnungsschema
erst eine Testabrechnung zur Kontrolle erstellen!
ohne Abschlag
mit Abschlag
mit Abschlag u.
      Folgesbschlag
Finale vorbereiten
Abschlag vorbereiten
Abschlag vorbereiten
Korrekturen/Ergänzungen
Korrekturen/Ergänzungen
Korrekturen/Ergänzungen
Abrechnen und Druck
Abrechnen und Druck
Abrechnen und Druck
FiBu Übertrag
ggf. FiBu Übertrag
ggf. FiBu Übertrag
Finale vorbereiten
Folgeabschlag
      vorbereiten
Korrekturen/Ergänzungen
Korrekturen/Ergänzungen
Abrechnen und Druck
Abrechnen und Druck
FiBu Übertrag
ggf. FiBu Übertrag
Finale vorbereiten
Korrekturen/Ergänzungen
Abrechnen und Druck
FiBu Übertrag

---

## LKW-Kennzeichen

LKW-Kennzeichen
Das Kfz-Kennzeichen wird gegen den LKW-Stamm validiert
und die zugehörige LKW_Nummer ermittelt. Der Parameter LKW_FEHLER_ABBR bestimmt,
ob ein nicht gefundener LKW zur Abweisung des Importsatzes führt (Wert1=1) oder
nicht (Wert1=0). Bei einem Fehler wird folgender Satz ins Fehlerprotokoll
geschrieben: „LKW [...] fehlt in LKW_Stamm [...], Übern. #..., SatzId #..., Zl.
# ...“. Standardmäßig wird kein Fehlerabbruch durchgeführt.
(Zugehörige
Positionsparameter: LKW_SAx)

---

## LKW Verwaltung

LKW Verwaltung

---

## OWaage

OWaage
-14000
Vorgangserzeugung: Fehler beim Setzten des
Belegdatums
-14001
Vorgangserzeugung: Fehler beim setzten der
Vorgangsnummer
-14002
Vorgangserzeugung: Fehler beim Setzten der
Wiegenummer
-14003
Vorgangserzeugung: Fehler beim Setzten der
Lagernummer
-14004
Vorgangserzeugung: Fehler beim Setzten desr
VersandId
-14005
Vorgangserzeugung: Fehler beim Setzten der LKW
Nummer
-14006
Vorgangserzeugung: Fehler beim Setzten des
Lagerplatzes
-14007
Vorgangserzeugung: Fehler beim Setzten des
Mengenkonvertieres
-14008
Vorgangserzeugung: Fehler beim Setzten der Me
Nummer
-14009
Vorgangserzeugung: Fehler beim Setzten der Owaage
Id
-14010
Vorgangserzeugung: Fehler beim Setzten der
Artikelvarinate
-14011
Vorgangserzeugung: Fehler beim Setzten des Preises
-14012
Vorgangserzeugung: Fehler beim Setzten des Netto
Preis
-14013
Vorgangserzeugung: Fehler beim Anfügen der
Warenposition
-14014
Vorgangserzeugung: Fehler beim Setzten der
Warenposition
-14015
Vorgangserzeugung: Fehler beim Setzten des
Kontraktes
-14016
Vorgangserzeugung: Fehler beim Setzten der
Kontraktfindung
-14017
Vorgangserzeugung: Fehler beim Setzten des
Artikeltextes
-14018
Vorgangserzeugung: Fehler beim Setzten der
Wiegung1
-14019
Vorgangserzeugung: Fehler beim Setzten der
Wiegung1
-14020
Vorgangserzeugung: Fehler beim Setzten des
Waagenprofils1
-14021
Vorgangserzeugung: Fehler beim Setzten des
Waagenprofils2
-14022
Vorgangserzeugung: Fehler beim Setzten des
Partiestyps
-14023
Vorgangserzeugung: Fehler beim Setzten der
Partienummer
-14024
Vorgangserzeugung: Fehler beim setzten der
Mengenherkunft
-14025
Vorgangserzeugung: Fehler beim setzten des
Wertartikeles
-14026
Vorgangserzeugung: Fehler beim setzten der
Warenposition
-14027
Vorgangserzeugung: Fehler beim setzten der Menge
-14028
Vorgangserzeugung: Fehler beim Anlegen des
Vorganges
-14029
Vorgangserzeugung: Fehler beim setzen des
Einlagerungskennzeichen

---

## Platzhalter für Zahlungsbedingungen

Platzhalter für
Zahlungsbedingungen
Nr.
Bezeichnung
Nr.
Bezeichnung
1
Betrag netto
2
Betrag brutto
3
Steuerbetrag
4
Skontierfähiger Betrag
5
Skontobetrag
6
Skontosatz
7
Skontotage
8
Skontodatum
9
Valutadatum
10
Zieltage
11
Zahlbetrag
17
Plan- / Lieferdatum
18
Währungstext
19
Ext.
      Kundennummer
20
BLZ
21
Bankkontonummer
22
Bezugsdatum
23
Zielverlängerungstage
24
BIC
25
IBAN
26
Bankbezeichnung
27
GläubigerID
28
Mandat
29
SEPA
      Ausführungsdatum
Um einen Platzhalter in den Text einzufügen, muss der
gewünschte Platzhalter in geschweiften Klammern geschrieben werden. Der Aufbau
ist {Nummer, Länge, Kommastellen}.
Ist der Wert kürzer als die in den Zahlungsbedingungen
angegebene Länge, so wird der Wert mit Leerzeichen aufgefüllt. Dieses Verhalten
lässt sich mit dem
SPA 1148
„Leerzeichen bei Zahlungsbedingungstext entfernen“
abstellen.
Den numerischen Werten (z.B. Betrag brutto) wird
automatisch ein Tausendertrennzeichen hinzugefügt, außer die angegebene Länge
ist zu kurz. Reicht die Länge nicht aus, um den numerischen Wert darzustellen,
wird im Zahlungsbedingungstext statt des Wertes „*“ angezeigt.
Beispiel:
Ausgabe des Bruttobetrages
{2,10,2}
Ausgabe des Wahrungstextes {18}
Ausgabe der
Zielverlängerungstage {23,2,0}

---

## Programmablauf

Programmablauf
Zuerst werden die wesentlichen Scriptparameter aus der
Relation ScriptparamPar mit der ScriptPId = „WaagenImport“ eingelesen. Bei nicht
vorhandenen oder inaktiv geschalteten  Datensätzen wird eine
Standardeinstellung für die betreffenden Programmvariablen vorgenommen. Bei
schwerwiegenden Fehlern beim Einlesen der Scriptparameter stoppt das Programm
mit der Fehlermeldung "SKRIPT FALSCH PARAMETRISIERT!". Es erfolgt ein Eintrag
ins Fehlerprotokoll wie „Skript gestoppt: ART_AUS_SORTx=1 und SORT_AUS_ARTx=1“
oder „Skript gestoppt: ART_AUS_SORTx<>1 und ART_SAx=0 bzw.
ARTLEN_SAx=0“.
Nach erfolgreichem Einlesen der Parameter, was einige
Sekunden benötigt, wird die Datei zum Lesen geöffnet und auf die Platte kopiert.
Bei Einstellung des Parameters MASKE_QUELLPFAD=1 wird
zuvor eine Maske angezeigt, die zur Eingabe des vollständigen Pfades der
Importdatei auffordert. Wird nichts eingegeben oder ist MASKE_QUELLPFAD=0, so
wird der Name der Datei und das Laufwerk durch die Scriptparameter DISK und
DATEINAME eingestellt.
Der Parameter WAAGEDAT enthält den vollständigen
Dateipfad des Kopier-Zieles auf der Platte. Steht MULT_FILES=1, so werden ALLE
Dateien von dem Datenträger gelesen und zusammenkopiert, egal was in DATEINAME
steht.
Wird beim Aufruf des Scriptes als 1. Parameter ein
Dateiname angegeben, so wird versucht, ausschließlich die angegebene Datei
einzulesen, unabhängig von der Einstellung von MULTI_FILES.
Bei dem Vorgang des Einlesens kann es besonders unter
Windows 95 zu Problemen kommen (Fehlermeldung „Kann Datei nicht finden / öffnen
...“, die zum Abbruch des Scriptes führen (Behebung s. unten:
Fehlermeldungen).
Nun beginnt der eigentliche Einlesevorgang der Daten.
Da die Originaldaten nicht markiert sind, kann leider nicht festgestellt werden,
ob die Daten doppelt eingelesen werden.
Zunächst wird eine eindeutige UebernahmeId erzeugt,
die für alle Datensätze eines Datenimportes gilt. (Außerdem wird an späterer
Stelle im Programm fü
[...]


---

## SEPA-Kennzeichen im Hausbankenstamm

SEPA-Kennzeichen im
Hausbankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Hausbanken
Direktsprung
[BNKH]
2)
Das SEPA-Verfahren unterliegt einer ständigen Weiterentwicklung. So kann es
vorkommen, dass unterschiedliche Banken auch unterschiedliche Versionen
verwenden. In Referenz-ERP ist die Übertragung für folgende Versionen implementiert
und kann im Hausbankenstamm hinterlegt werden:
Format
Gültig ab
Gültig bis
Version 2.5
01.11.2010
11.2021
Version 2.7
04.11.2013
11.2022
Hierbei handelt es sich um dasselbe
      Format wie „Version 2.7 pain.001.003.03 / 008.003.02 gültig ab November
      2013“, nur dass bei Bankverbindungen, bei denen die IBAN mit DE beginnt,
      die BIC grundsätzlich nicht mit übertragen wird, da die Identifikation der
      Bank innerhalb Deutschlands bereits mit der IBAN erfolgen
      kann.
Version 3.0
20.11.2016
11.2023
Es
      gibt folgende Änderungen zur Vorgängerversion:
•
Die
      Vorlauffristen sind jetzt für Erst-, Folge-, Letzt- und
      Einmallastschriften bei Basislastschriften einheitlich 1 Tag lang. Sobald
      bei einer Hausbank die neue Version eingetragen ist, wird beim
      automatischen Zahlungsverkehr bei Basislastschriften die Einstellung der
      Eillastschrift gezogen.
•
Es wird nicht
      mehr zwischen „Basislastschrift“ und „Basislastschrift mit Verkürzter
      Laufzeit“ („Eillastschrift“) unterschieden. Es ist nicht notwendig die
      Stammdaten zu ändern, da bei Verwendung der Version 3.0 die eingestellten
      Werte vom Programm gleich richtig interpretiert werden.
Die
      Mandatsreferenz darf jetzt theoretisch Leerzeichen enthalten, es wird aber
      von den Kreditinstituten empfohlen, keine Leerzeichen zu verwenden, da sie
      auf papierhaften Mandat nicht immer eindeutige dargestellt werden
      können
Version 3.1 bis 3.2
19.11.2017
11.2023
pain.001.001.03_GBIC_2 /
      008.001.02_GBIC_2
Version 3.3 bis 3.6
17.11.2019
11.2025
pain.001.001.03_GBIC_3 /
      008.001.02_GBIC_3
[...]


---

## SEPA-Kennzeichen im Staatstamm

SEPA-Kennzeichen im Staatstamm
Hauptmenü
Stammdatenpflege
Allgemeine Stammdaten
Staatstamm
Direktsprung
[STAAT]
Im Staatstamm wurde ein neues Kennzeichen eingeführt.
Dieses besagt, ob der Staat am SEPA-Verfahren
teilnimmt oder nicht. Dieses Kennzeichen wird einmal automatisch für die 32
bisher am SEPA-Verfahren teilnehmenden Länder gesetzt. Voraussetzung für dieses
automatische Update ist, dass der ISO-Code korrekt gepflegt ist.
Beim Zusammenstellen der Zahlungen bzw. der
Zahlungsvorschläge wird für alle Banken mit einem Staat bei dem „SEPA
Teilnahmestaat“ auf
Ja
steht, ein Kennzeichen in den Zahlungsvorgängen
gesetzt, dass hier das SEPA-Verfahren anzuwenden ist. Eine Änderung des
Kennzeichens bewirkt sofort eine Anpassung der Zahlungsvorschläge. Freigegebene
Zahlungen werden nicht mehr verändert.
Hinweis:
Will man das SEPA-Verfahren
vorläufig lediglich für ausländische Lieferanten bzw. genauer: Lieferanten deren
Bank im Ausland sitzt durchführen, so kann man das Kennzeichen „SEPA
Teilnahmestaat“ für Deutschland auf Nein stellen. Dies ist eventuell deswegen
hilfreich, weil es unter Umständen sehr lange dauern kann, bevor man von allen
Lieferanten die IBAN-Nummern hat.

---

## SET COMMAND_DELIMITER Statement

SET COMMAND_DELIMITER Statement
Syntax
SET COMMAND_DELIMMTER [?]
Purpose
Legt das Zeilenendekennzeichen fest.
Anwendung
Kommandodatei, Befehlszeile
Berechtigung
Alle Anwender
Siehe auch
SET DELIMITER
Beschreibung
Im Normalfall ist der COMMAND_DELIMITER das Semikolon
>;<. Es kann aber Fälle geben, in denen es Sinnvoll ist, dieses
umzudefinieren ( z.B.: beim Anlegen von Prozeduren). Dies erfolgt durch diesen
Befehl. Im unten angegebenen Beispiel gilt nach dem ändern des COMMAND_DELIMITER
das gesamte Create - Statement bis zum nächsten # als ein Statement. Ohne dies
wäre nach dem Semikolon Ende und Sybase würde einen Fehler zurückliefern, da das
„END“ fehlt.
Gibt man kein neues Zeichen an, wird wieder das
Ursprüngliche >;< genommen.
Beispiel
SET COMMAND_DELIMITER #;
CREATE TRIGGER FiBuVorgStamm_aftdel
AFTER DELETE ON FiBuVorgStamm
REFERENCING OLD AS alt
FOR EACH ROW
WHEN ( alt.FiBuV_BUCHSTAT!=3 )
BEGIN
delete from FiBuVorgUngebu where
FibuV_id=alt.FibuV_id;
END#
SET COMMAND_DELIMITER#
EXIT;

---

## Standardwaagenprofil-Unterstützung: Aeinswiege

Standardwaagenprofil-Unterstützung:
Aeinswiege
AeinsWiege ist ein Programm, welches das Wiegen von
solchen Waage-Protokollen unterstützen soll, bei denen die Bordmittel von Aeins
nicht ausreichen.
AeinsWiege ist so konzipiert das es "einfach" mit
Hilfe des Standard-Waagenprofils in Aeins angesprochen wird.
In der jetzigen Ausbaustufe wird AeinsWiege durch eine
XML gesteuert.
Da hier mit XML hantiert wird werden statt der sonst
aus dem WAM gewohnten <STX>,<ETX>,usw. eben [STX],[ETX],usw.
verwendet.
Interessant sind u.a. 3 neue "Direktiven":
1.
BCC
Vom WAM her dürfte schon die
Möglichkeit bekannt sein die Prüfsumme für ausgehende Kommandos zu berechnen.
AeinsWiege kann das auch für eingehende Waagendaten. Das ist wichtig, da manche
Protokolle nach Sendung der Wiegedaten ( die mit BCC von der Waage aus gesendet
werden ) noch eine positive Quittierung brauchen. Es ist einfach viel
geschickter, wenn AeinsWiege diese BCC auch geprüft hat und dann entsprechend
verfährt!
Beispiel:
<Sequence Send="[SOH]Ap[ENQ]"
Expect="[SOH]A[STX]
([DATA][ETX])[BCC]
"
Result="1"/>
Hinweis: Ausgehend - also im
Send - ist die %BCC%-Syntax, eingehend - also im Expect - ist die
[BCC]-Syntax.
2.
DATA
Steht für eine beliebige
Anzahl von unbekannten Zeichen.
Beispiel hierfür ist die
obige Sequenz. AeinsWiege schickt an die Waage "[SOH]Ap[ENQ]", die Waage sendet
daraufhin "[SOH]A[STX]QA[SP]0016060000000025140206144407[ETX]6" zurück. Der
gesamte Anteil zwischen [STX]…[ETX] entspricht dabei ohne dass STX und ETX eben
DATA, wobei die Prüfsumme von der Waage über [DATA] incl. [ETX] gebildet wurde
und in diesem Falle 6 ist.
3.
DATE
Mit Hilfe dieser
Konstruktion lassen sich formatierte Zeitwerte innerhalb eines Send-Strings
definieren.
Beispiel:
<Sequence
Send="[SOH]A[STX](ZSD
{ddMMyyyyHHmm}%DATE%
[ETX])%BCC%[ENQ]"
Expect="[ACK]" Wait="1000" />
Innerhalb der geschweiften
Klammern steht der Format-String für die C#-Funktion ToString von
DateTime-Objekt.
Alle Möglichkeit
[...]


---

## Status einer E-Mail

Status einer E-Mail
Das Mailing-Kennzeichen hat folgende Ausprägungen:
Wert
Bezeichnung
Bedeutung
0
Wartet auf Freigabe
Der
      Beleg befindet sich in der Warteschleife und soll versendet werden. Die
      E-Mail kann jetzt manuell Freigegeben/Versendet werden. Die
Standard-Eventmail
      Funktion
versendet diese E-Mails ebenfalls, sobald das Event
      startet.
1
Freigegeben
Der
      Beleg ist zum Versand freigegeben. Diesen Status haben E-Mails die manuell
      versendet werden sollen oder von einem
Dienst oder Exe
verschickt werden.
2
Versendet
Der
      Beleg wurde erfolgreich versendet.
10
Zurückgestellt
Dieser Beleg wurde zurückgestellt.
      Die E-Mail wird erst nach erneuter Freigabe versendet.
95
Unzustellbar
Der
      Beleg kann nicht zugestellt werden.
99
fehlerhaft
Der
      Beleg konnte auf Grund eines Problems nicht versendet werden.
Im Fall einer fehlerhaften E-Mail kann der Fehlercode
Aufschluss über die Ursache geben. Zusätzlich finden sich Einträge im
Fehlerprotokoll.

---

## Tabelle zur Version: 8.3.2308.18

Tabelle zur Version: 8.3.2308.18
ID
Releasenote - Titel
Geprüft
34094
Kopieren eines Vorgangs mit
      Teildispositionskennzeichen

---

## Tabelle zur Version: 9.0.2402.4

Tabelle zur Version: 9.0.2402.4
ID
Releasenote - Titel
Geprüft
35763
Patch einspielen von SQL-Dateien
35815
Privater Crystal Report Daten anzeigen
35831
CS-Makro Funktion CompileAll
35848
Rollenpflegerstamm Aktualisierung
35849
Formularstamm - Pfleger
35876
Druckerstamm: Kennzeichen "Ohne ASCII Konvert."
35742
Neue Auswahllistenvariante im Archiv
35732
Fehlermeldungen im Barverkauf mit der Herbstversion
      9.0.2402.2
35765
Kontraktmengenzeitraum
35867
Kontraktabwahl bei Nachhaltigkeit im Verkauf
35788
Archiv-Verlinkung von eRechnungsexporten bei
      privatisierten Belegreferenzen
35814
Kundentypwechsel

---

## Tabelle zur Version: 9.0.2501.5

Tabelle zur Version: 9.0.2501.5
ID
Releasenote - Titel
Geprüft
36368
Abkündigung: Infocenter
35868
Datenbank-Backup: AMIC_EVT_Backup_ARCHIV
35948
Auswahlliste 2.0 JPP-Zugriff
35965
Branchen-ERP Etikettendruck export Archivkennzeichen
35966
Geschäftsjahr Prüfung Enddatum
35973
Reporte
35977
Standard F3-Auswahl und Auswahlliste
36231
Crystal: Druck über Makro
36522
IBMSK nicht existierendes Feld
36573
Referenz-ERP Passwortrichtlinien
36957
HTML-Dateien im Belegfluss im Browser anzeigen
36959
Belegfluss gelöschte Formulararchiveinträge
      wiederherstellen
37055
Pfleger individuelle Artikelnummern aus der
      Belegflussmaske öffnen
37061
Belegfluss: Daten aktualisieren als neue
      Refresh-Funktion über eine Prozedur
37062
Fibudirektverbuchungprozedur für Belegfluss um eine
      Parameter erweitert
37065
Belegfluss: Postfach-Einrichtung teilt Einrichtung in
      Kopf und Kostenverteilungsgrid.
37068
Belegflussmaske Kostenaufteilungsgrid
    zurücksetzen
37091
Nummernkreis optional auf der
      Belegflusspostfach-Einrichtungsmaske
36913
Formulararchiv eRechnung "Dokument speichern"
      Funktion
36960
StandardbelegflussPostfächer für den Import
35497
Hilfelink gefixt
36384
USTId-Prüfung
35377
Avise Mailversand
35636
GuV mit Vorvorjahreswerten
35637
eCLearing CAMT53
35665
Vermailung von Mahnungen
35789
Mailversand Zinsabrechnung
35790
Mailversand mahnwesen
35969
Eclearing
36002
ZHB - Zahlungen ansehen - Excel Export
36404
Eclearing CAMT.053 auch ungepackt als XML
      importieren
36482
Spea kunden mit Auslandsbank
36659
Eclearing Auszugsnummer CAMT053
36711
CAMT053 Anfangs- bzw. Abschlusssaldo aus Sicht des
      Kunden
36717
eClearing
36920
eClearing Reihenfolge Positionen in CAMT053
36542
Inventurabschluss PIV ignorieren
36861
Permanente Inventur angezeigte Menge
35734
Steuerung Kassenabschluss
36342
TSE-Description für BSI-Zertifizierungs-ID
      hinzugefügt.
36294
Individuelle Zu-/Abschläge bei Kontrakten
36859
Individualpreispfleger EKZ-Nummer
36651
Partiea
[...]


---

## Test-Wägungen sollen übergangen werden und keine Fehler verursachen

Test-Wägungen sollen übergangen werden und keine Fehler verursachen
Falls die reguläre Waagen-Datei auch Testwägungen
enthält, die nicht weiter verarbeitet werden sollen, aber auch keinen
Fehlerabbruch herbeiführen dürfen, so ist im ScriptParameter ZI_DEFAULT der Wert
99 einzutragen.
Ferner ist sicherzustellen, dass der Bereich der
Daten, an dem die Zielansprach-Kennung erwartet wird, bei Testdaten einen Wert
enthält, der mit keiner gültigen Zielansprache verwechselt werden könnte.
Beispiel: CER = Cerea, FAK=Faktura, ___ (3
Leerzeichen)=Testwägung.

---

## Vorgreservier. LOESCHEN

Vorgreservier. LOESCHEN
Die Vorgreservierung wird gelöscht. In Kombination mit
HINZUFUEGEN kann eine klassische Situation behoben werden: Der Vorgangstamm ist
schon komplett geschrieben, die Vorgreservierung hat aber in der V_ID noch eine
‚0’ und des Neu-Kennzeichen steht auf ‚1’, die Verbindung zum Vorgang hat also
nicht funktioniert. Man behebt dies durch Löschen der Vorgreservierung und
HINZUEGEN beim unvollständigen Beleg.
Die typische Situation: Aeins ist während der Erfassung
eines Beleges abgestürzt (es existiert nur die Vorgreservierung mit V_ID = ‚0’
und Neu-Kennzeichen = ‚1’ wird durch Löschen dieses Eintrages behoben. ABER
VORSICHT: Solche Einträge wird man im laufenden Betrieb natürlich häufig
finden!!!!! Also immer vergewissern, dass kein Bediener in der Erfassung
ist!

---

## Waagenterminals

Waagenterminals

---

## Was sind die Vorteile eines Anschlusses über das Branchen-ERP-STANDARD-WAAGENPROFIL?

Was sind die Vorteile eines Anschlusses über das
Branchen-ERP-STANDARD-WAAGENPROFIL?
Trennung von Hard- und Software
Mögliche Probleme lassen sich eindeutig eingrenzen und
damit auch in der Regel sehr schnell beheben. Mit Hilfe des WP lässt sich immer
sofort – meist ohne großen Aufwand – prüfen, ob die zugrunde liegende Technik
noch so funktioniert, wie einmal erwartet.
Änderungen des WIEGESYSTEMS lassen sich in sehr vielen
Fällen ohne großen Aufwand seitens Referenz-ERP bewerkstelligen, nämlich zum Beispiel
dann wenn die Behandlung des WP gleich bleibt. Ändert sich der Aufbau der
Rückgabe des WP dann ist in aller Regel nur das Waagenprofil (WAM) in Referenz-ERP
anzupassen. Da das WAM sehr flexibel auf solche Änderungen reagieren kann sind
in fast allen denkbaren Fällen keine Referenz-ERP-Programm-Update-Szenarien nötig.
Ein System, welches die Technik des
Branchen-ERP-STANDARD-WAAGENPROFIL verwendet, kann bei vorausgesetzter
TCPIP-Erreichbarkeit als „mehrplatzfähig“ angesehen werden. Branchen-ERP besitzt die
Technik einen solchen Arbeitsplatz in den Stand zu heben. Diese Möglichkeit ist
ein kostenpflichtiges Zusatzmodul von Referenz-ERP.
Die sehr leichte Integration eines
Branchen-ERP-STANDARD-WAAGENPROFILES in Referenz-ERP.
In aller Regel ist nur noch die Beschreibung bzw. der
Anpassung der Rückgabe des WP durchzuführen. Selbst diese entfällt, wenn sich
das WP strikt an das Branchen-ERP-STANDARD-WAAGENPROFIL hält. Allerdings kann es sein,
dass der Aufbau leicht variiert bzw. noch weitere Daten übermittelt, die zur
späteren Auswertung in Referenz-ERP herangezogen werden.
Die automatische Zusatzprotokollierung in extra dafür
vorgesehener Relation der WP-Rückgaben. Somit stehen in Sonderfällen neben den
in Referenz-ERP gewonnen Daten über die Profilbeschreibung, und den Daten im
Wiegesystem noch die Originaldaten der WP-Ergebnisse zur Verfügung.
Es kann seitens Referenz-ERP schon eine Waageneinrichtung
vorgenommen und durchgetestet (Abläufe, Hofliste, Wiegescheine, etc. pp) werden,
bevor überhaupt ein reales WP verfügbar ist. Das
[...]


---

## Wechselkennzeichen im Hausbankenstamm

Wechselkennzeichen im Hausbankenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Hausbanken
Direktsprung
[
bnkh
]
Im Hausbankenstamm müssen das Wechselkonto, das
Wechselobligokonto und das Schuldwechselkonto eingerichtet werden.
Das
Wechselkonto enthält alle erhaltenen Wechsel, das Obligokonto alle an die
Hausbank weitergereichten Wechsel bis zum Verfall, und das Schuldwechselkonto
enthält alle selbst ausgegebenen Wechsel!

---

## Wechselkennzeichen im Sachkontenstamm

Wechselkennzeichen im Sachkontenstamm
Hauptmenü
Finanzbuchhaltung
Stammdaten
Sachkonten
Direktsprung
[SKS]
Im Sachkontenstamm gibt es das Feld
Wechselkonto
das auf
"JA"
gestellt werden muss. Wechselkonten
müssen
im Sachkontenstamm als Wechselkonto gekennzeichnet werden! Von
diesem Kennzeichen hängt ab, wie diese Konten in der Belegerfassung
interpretiert werden.
In der Basisdatenbank sind davon folgende Konten
betroffen:
Besitzwechsel Kontonummer 1370
Besitzwechselobligo Kontonummer 1371
Schuldwechsel Kontonummer 1660

---

