---
title: Masken im Fachgespraech erstellen und testen
type: how-to
audience: [anwender, administrator, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Masken im Fachgespraech erstellen und testen

Das Studio benoetigt keine Kenntnis von Tabellen, Spalten oder SQL. Der hier gepruefte Umfang ist eine manuelle Getreide-Kalkulationsprobe mit freigegebenen Fachfeldern. Sie erzeugt keine Geschaeftsbelege, Buchungen oder Bestandsbewegungen. Die Bilder stammen aus der echten lokalen Browserabnahme mit einer synthetischen Kennung und einem Testmandanten.

## 1. Fachlich beschreiben und Rueckfragen beantworten

Unter Administration → Screen Studio im Bereich **Maske im Fachgespraech** den gewuenschten Prozess beschreiben. Zum Beispiel: Getreideannahme mit Nettomenge, Feuchtigkeit, Besatz, Preis und nachvollziehbaren Abrechnungspositionen.

Das Studio fragt nach fehlenden Angaben. Fuer die vorhandene Vorlage die manuelle Testeingabe waehlen und den begrenzten Probeumfang ausdruecklich bestaetigen. Automatische Waagenuebernahme, Lieferanten-/Kontraktbindung und Controllerbenachrichtigungen sind in dieser Vorlage noch nicht implementiert. Eine solche Anforderung wird nicht durch eine erfundene Datenbindung ersetzt.

Der Standarddialog ist kataloggefuehrt und als solcher beschriftet. Ein gespeicherter Entwurf stellt seine Unterhaltung und die ausdruecklich gewaehlten manuellen Entscheidungen beim Oeffnen wieder her. Diese Notizen ersetzen keine fachliche Freigabe.

![Gespeichertes Fachgespraech und manuelle Auswahl](img/studio-dialog-20261015/07-fachgespraech.jpg)

## 2. Vorschlag uebernehmen und Fachfelder auswaehlen

**Geprueften Vorschlag uebernehmen** erstellt eine normale Studio-Maske. Ein neuer Vorschlag ueberschreibt einen zuvor geoeffneten gespeicherten Entwurf nicht automatisch. Unter **Freigegebene Fachfelder** lassen sich optionale Angaben zu- oder abwaehlen. Die vier verpflichtenden Eingaben bleiben verbindlich: angelieferte Nettomenge, Preis, ausdruecklicher Teststeuersatz und ausdruecklich gewaehlter freier Besatz.

Kompatible Testwerte bleiben bei einer Feldanpassung erhalten. Werte eines entfernten Felds werden nicht unsichtbar weiterberechnet. Titel und Gestaltung lassen sich im selben Entwurf ueberarbeiten.

## 3. Eingaben ausprobieren und Ergebnisse sofort pruefen

**Synthetische Beispieldaten laden** fuellt nur die sichtbaren Eingaben mit Testwerten. Die Steuerangabe ist ein ausdruecklicher Testwert und keine Steuerempfehlung. Nach Aenderungen berechnet der vorhandene Agrar-Kalkulator die Ergebnisse mit kurzer Verzoegerung neu. Die Tabelle zeigt Positionen und deren Formeln; ihre Anzahl haengt von den gewaehlten Angaben ab.

Das erste Beispiel mit 25.000 kg, 3 Prozent Besatz, explizit 2 Prozent freiem Besatz, Preis 220 EUR/t sowie 100 EUR Fracht und 15 EUR Wiegegebuehr ergab 5.330,00 EUR netto. Mit ausdruecklich eingegebenen 7 Prozent Teststeuer ergaben sich 373,10 EUR Steuer und 5.703,10 EUR brutto.

![Interaktive Kalkulation mit Testeingaben](img/studio-dialog-20261015/01-berechnung.jpg)

## 4. Qualitaetsgrenze und Freigrenze unterscheiden

**Maximaler Besatz als Qualitaetsanforderung** ist eine separate optionale Angabe. Sie ist keine abzugsfreie Toleranz. Der freie Besatz muss ausdruecklich eingegeben werden. Windabgang ist im verwendeten manuellen Domain-Vertrag nur eine Information und erzeugt keinen weiteren Abrechnungsabzug.

Geprueftes zweites Beispiel: 25.000 kg, 1,5 Prozent Besatz, 0,8 Prozent informativer Windabgang, freier Besatz null, Qualitaetsgrenze 2 Prozent, keine weiteren Abzuege. Ergebnis: 375 kg Besatzabzug, 24.625 kg Abrechnungsgewicht. Bei 220 EUR/t und expliziter Teststeuer null sind dies 5.417,50 EUR.

![Qualitaetsgrenze eingehalten, keine Vertragsfreigabe](img/studio-dialog-20261015/05-qualitaet-und-freigrenze.jpg)

Wird nur die Qualitaetsgrenze auf 1 Prozent gesenkt, bleibt der Betrag 5.417,50 EUR. Es erscheint die Warnung, dass die Qualitaetsgrenze ueberschritten ist. In beiden Faellen ist die Vertragsfreigabe ausdruecklich nicht erteilt. Eine tatsaechliche Abrechnung verlangt die noch anzubindende gepruefte Vertragsregel und Messwertabgrenzung.

![Qualitaetswarnung bei unveraendertem Betrag](img/studio-dialog-20261015/06-qualitaetsgrenze-ueberschritten.jpg)

## 5. Fehler pruefen

Eine negative Nettomenge wird serverseitig zurueckgewiesen. Das bisherige Ergebnis verschwindet; ein spaet eintreffendes altes Ergebnis wird nicht wieder als gueltig angezeigt. Die Meldung nennt das Fachfeld. Auch unzulaessige Wertebereiche, nicht endliche Zahlen und negative Abrechnungsergebnisse werden abgewiesen.

![Negative Nettomenge wird abgewiesen](img/studio-dialog-20261015/02-validierung.jpg)

## 6. Speichern, wieder oeffnen und ueberarbeiten

**Speichern** sichert die Maskendefinition, Unterhaltung und Entscheidungen. Die eingegebenen Probevorgaenge werden nicht als Geschaeftsdaten gespeichert. Beim Wiedereroeffnen ist die Definition vorhanden; Testwerte koennen bewusst erneut geladen werden. Unveraenderte Definitionen lassen sich nicht nochmals ueber den Speicherknopf als neue Fassung ablegen. Wiederholungen desselben Auftrags sind auch serverseitig gegen doppelte Fassungen abgesichert.

Die Browserabnahme umfasste eine erste Speicherung, eine Titel-/Feldueberarbeitung, Verlassen des Studios, regulaere Neuanmeldung, Wiedereroeffnen und eine weitere Erweiterung um die Qualitaetsgrenze. Die Historie zeigt sieben Ereignisse: Anlage, erste Aenderung, Pruefung, Simulation, zweite Aenderung, erneute Pruefung und erneute Simulation. Der Benutzer wird ueber seine gepruefte technische Kennung nachgewiesen; persoenliche Anmeldedaten wurden nicht verwendet.

![Native Historie mit sieben Ereignissen](img/studio-dialog-20261015/04-historie.jpg)

## 7. Zur Pruefung geben und Freigabesperre verstehen

Nach dem Speichern uebergibt **Pruefung** die exakte Fassung zur Pruefung. Eine nachfolgende Aenderung setzt sie wieder in den Entwurfsstatus. Alte Pruefungen gelten damit nicht fuer den geaenderten Inhalt.

**Prozess simulieren** verweigert bei dieser begrenzten Kalkulationsvorlage die Freigabe: Eine vollstaendige produktive Datenbindung und Prozessvariante sind noch nicht abgenommen. Die sichtbare Meldung ist hier der erwartete Sicherheitsnachweis. Sie wird nicht durch erfundene Datenquellen oder fremde Simulationsergebnisse beseitigt. Die getrennt gepruefte bestehende Buchungskette zertifiziert diese neue Vorlage nicht automatisch.

![Unabgenommene Vorlage bleibt gesperrt](img/studio-dialog-20261015/03-freigabesperre.jpg)

## Optional: Konfiguriertes Sprachmodell

Die Option zur Modellinterpretation nutzt den fuer den eigenen Mandanten konfigurierten Anbieter und ein bereits zugewiesenes eigenes Tokenkontingent. Nur Anforderungen beschreiben; keine echten Kunden- oder Zugangsdaten in den Testdialog eingeben. Der Verbrauch wird vorab reserviert und anhand der Anbieterangaben im technischen Verbrauchsnebenbuch abgerechnet. Ein wiederholter gleicher Modellauftrag loest keinen zweiten Anbieteraufruf aus. Ungeklaerte Anbieterabschluesse bleiben reserviert und muessen geprueft werden.

Die synthetische Browserkennung besass kein eigenes Kontingent; ein positiver echter Modellaufruf wurde daher nicht als abgenommen ausgegeben. Die Rechte der Kennung wurden nicht erweitert. Der Katalogdialog funktioniert ohne Modell. Die Modellinterpretation darf weder unbekannte Felder erfinden noch Geschaeftsregeln oder produktive Masken selbst freigeben.

[Technische Abnahme und Restpunkte](../quality-assurance/studio-semantic-20261015.md), [fachlicher Abrechnungsvertrag](../architecture/harvest-deduction-contract-standard.md), [Vier-Augen-Freigabe bereits abgenommener Studio-Varianten](studio-freigabe.md).
