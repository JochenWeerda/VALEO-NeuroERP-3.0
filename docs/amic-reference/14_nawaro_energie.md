# NaWaRo, Bioenergie & Nachhaltigkeit — Referenz-ERP Referenzwissen
> Quelle: Branchen-ERP Referenz-ERP Hilfe (7 Seiten)
> Dieses Dokument dient als fachliche Referenz für VALEO NeuroERP.

## CO2-Kostenaufteilung

CO2-Kostenaufteilung
Das neue Modul zur CO2-Kostenaufteilung wurde
fertiggestellt.
Releasenote Kategorie:
Ticket: 717732[33255]
Version: 8.3.2212.23
Datum: 23.12.2022
Anwendung: CO2-Kostenaufteilung
Variante: -
Funktion/Report: -
Weitere
Informationen
Tags:
Releasenote, 8.3.2212.23, 33255, 717732

---

## CO2 Artikelstammpflege

CO2 Artikelstammpflege
Im Artikelstammpfleger wurde im Modul
CO2-Kostenaufteilungsgesetz die Feldbezeichnung zum Feld "Gewicht pro ME" für
die CO2-Angabe korrigiert. Statt "t/(Mengeneinheit)" lautet er jetzt
"kg/(Mengeneinheit)", da intern mit "kg/(Mengeneinheit)" gerechnet wird.
Releasenote Kategorie:
Ticket: 719616[34121]
Version: 8.3.2309.1
Datum: 30.09.2023
Anwendung: [ARS]
Variante: n/a
Funktion/Report: n/a
Weitere
Informationen
Tags:
Releasenote, 8.3.2309.1, 34121, 719616

---

## LVS Beim Leeren ins Minus buchen (SPA 1125)

LVS Beim Leeren ins Minus buchen (SPA
1125)
Im LVS kann ein Ladeträger um eine gegebene Menge
reduziert werden. Dies kann dazu führen, dass die Menge auf dem Ladeträger ins
Negative gesetzt wird, was physikalisch unmöglich ist.
Gerade bei ungenau zu beziffernden Waren, die
Feuchtigkeit aufnehmen oder abgeben können, kann leicht das Gewicht um wenige
Prozent schwanken.
Um eine Minusbuchung beim Leeren eines Ladeträgers zu
vermeiden, kann diese Möglichkeit hier abgeschaltet werden.
0 – Entnahme von mehr als dem Inhalt erzeugt einen
Null-Eintrag – Der Ladeträger wird geleert und in die Leerpalettenlokalität
verbracht.
1 – Es wird weiterhin bei Entnahme > der Menge eine
Minus-Menge auf dem Ladeträger verbleiben.
•
Alle Lokalitäten, die im Wirtschaftsjahr im Rahmen einer permanenten
Inventuraufnahme besucht wurden
•
Alle Lokalitäten, auf denen im Verlauf des Wirtschaftsjahres Ware bewegt
oder inventarisiert wurde.

---

## CO2-Kostenaufteilung-Lizenz (SPA1141)

CO2-Kostenaufteilung-Lizenz (SPA1141)
Lizenz für die CO2-Kostenaufteilung.

---

## Allgemein

Allgemein
Feld
Beschreibung
Adresstyp
Person/Firma (Sanktion)
Typ
      der Angaben dieser Anschrift siehe
Verbotslisteneinrichtung
Kurzbezeichnung
Anrede
Vorname
Name
Zusatz1
Namenszusatz
Straße
PLZ/Ort zur Straße
Ortsteil
Postfach
PLZ/Ort zum Postfach
Postleitzahl und Ort, die dem
      Postfach zugeordnet sind
Staat
Ort
Anbauland
Anbauland das bei
      Nachhaltigkeitsvorbelegung gezogen werden soll
Telefon
FAX
Mobiltelefon
e-Postbrief
Partner1
Partner2
E-Mail
In
      dieser Tabelle können diverse Mailadressen hinterlegt werden. In der
      ersten Spalte gibt man den Bereich an, für welchen die Mailadresse gültig
      sein soll:
•
1 = Standard
      e-Mail1
•
2 = Standard
      e-Mail2
•
3 = Avise (nur
      Hauptanschrift)
•
4 = Mahnung (nur
      Hauptanschrift)
•
5 =
      Zinsabrechnung (nur Hauptanschrift)
Für
      Avise, Mahnung und Zinsabrechnung kann zusätzlich angegeben werden, ob der
      Belegversand mit oder statt Belegdruck, oder gar nicht geschehen
      soll.
Zusätzliche Bereiche können über das
      Anwendungsformat „af_mailtyp“ erfasst werden. Zum Lesen der Daten
      existiert die SQL-Funktion „Mailadresse“. Mit folgendem Statement erhält
      man die unter dem Bereich Avise erfasste Mailadresse der
      Kundenhauptanschrift:
select Mailadresse(AdressIdHauptadr,3) from
      Kundenstamm where KontoNummer=10111

---

## Reduzierung der Fontgröße um

Reduzierung der Fontgröße um
Reduzierung der Schriftgröße um angegebene Punkte bei
generell compressed zu druckenden Bereichen.
Man kann für Bereiche festlegen,
dass sie compressed gedruckt werden sollen. Verwendet man z.B. in der
Fonttabelle 3 Schriftarten mit den Größen 12, 10 und 8 und stellt für die
Reduzierung 2 Punkte ein, dann werden diese Schriftarten im komprimierten
Bereich mit den Größen 10, 8 und 6 gedruckt.

---

## Tabelle zur Version: 8.3.2212.23

Tabelle zur Version: 8.3.2212.23
ID
Releasenote - Titel
Geprüft
33155
Windows11-Anpassung: Asynchrones Anzeigen von
      Informationen
33156
Auswahlliste 2.0 im Dialogmodus
33157
Belegfluss erstellen Finanzbeleg
33255
CO2-Kostenaufteilung
33257
Referenz-ERP Temporäre Dateien
33235
Office 365 Online-Exchange-Authentifizierung
33280
Geodaten Lizenz
33209
DATEV Übertrag erstellen. Verbesserte
    Fehlermeldung.
33219
Neue Elster-Version
33181
Artikelpfleger: Inventurgruppe
33223
Kundenpfleger: Speichernabfrage
33283
Preiskalkulation Excel auf Artikelebene nicht mehr
      möglich.
33292
Artikelstamm: SQL-Fehler
32857
Reaktivierung von Quellbelegen bei Erstellung des
      Stornobelegs
33004
Stoffstromanteil pflegen
33282
Stoffstrom Kundenreport
33324
Teildisposition v_statusWeiter

---

