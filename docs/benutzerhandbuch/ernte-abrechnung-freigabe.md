---
title: Ernteabrechnung pruefen und genehmigen
type: how-to
audience: [anwender, administrator, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Ernteabrechnung pruefen und genehmigen

Die Kontrollmaske liegt unter **Administration → Screen Studio → Ernte-Abrechnung: Vertragsregeln, Messnachweise und Freigaben**. Alle Bilder zeigen die reale lokale Browserabnahme mit ausschliesslich synthetischen Daten. Die verbindliche Abrechnungssteuerung ist von der manuellen Studio-Kalkulationsprobe getrennt.

## Anmelden und fachlich auswaehlen

Mit **Mit SSO anmelden** die Unternehmensanmeldung oeffnen. Anschliessend Annahme, Kunde beziehungsweise Lieferant, Artikel und gegebenenfalls Kontrakt ueber die beschrifteten Suchfelder auswaehlen. Dafuer sind keine technischen Tabellen- oder Spaltennamen erforderlich. Einen angebotenen Treffer ausdruecklich auswaehlen; eingegebener Suchtext allein ist keine Zuordnung.

![Arbeitsplatz nach erfolgreicher Unternehmensanmeldung](img/ernte-freigabe-20261015/anmeldung.jpg)

## Vertragsfassung anlegen und gegenpruefen

Regelbezeichnung, Vertragspartner, Artikel, Gueltigkeitszeitraum, Vertragsgrundlage sowie Untersuchungsmethode und Methodenfassung angeben. Den **vereinbarten abzugsfreien Besatz** ausdruecklich eintragen; auch null ist eine bewusste Angabe. Die getrennte Qualitaetsgrenze ist keine Freigrenze. **Regelversion erstellen** speichert eine neue unveraenderliche Fassung.

In der Versionsliste mit **Regelversion pruefen** eine konkrete Fassung auswaehlen. Eine andere menschliche Identitaet mit entsprechender Einkaufs- oder Finanzleitungsrolle kann **Regel genehmigen** ausfuehren. Im Dialog die angezeigte Fassung und Inhaltsbindung pruefen, die Ausfuehrung ausdruecklich auswaehlen, einen Pruefvermerk und eine kuenftige Genehmigungsfrist eingeben. Die eigene Fassung darf nicht selbst genehmigt werden.

![Genehmigungsdialog mit konkreter Regelversion und Pruefvermerk](img/ernte-freigabe-20261015/regelgenehmigung.jpg)

## Annahme, Messung und Berechnung verbinden

Die Annahme auswaehlen und **Annahme und Nachweise laden** ausfuehren. Dann die genehmigte Regelversion **an die Annahme binden**. Unter **Messung und Freigabe** die Nachweisquelle des vorhandenen Messprotokolls angeben und **Messnachweis bestaetigen** ausfuehren. Untersuchungsmethode und Methodenfassung muessen zur Regel passen. Veraenderte Protokolle oder fehlende Nachweise sperren die Berechnung.

**Verbindlich berechnen** erzeugt eine nachvollziehbare Berechnungsfassung. Netto, Steuer und Brutto werden schreibgeschuetzt angezeigt. Unter **Berechnungspositionen** stehen Mengen, Abzuege und Formeln; die **Nachweishistorie** zeigt die ausgefuehrten Schritte und ihre Urheber. Bei veraenderten Eingaben muss neu berechnet und erneut genehmigt werden.

![Betragsuebersicht der finanziell geprueften synthetischen Berechnung](img/ernte-freigabe-20261015/berechnungsuebersicht.jpg)

## Finanzielle Gegenpruefung

Eine zweite menschliche Finanzprueferidentitaet laedt dieselbe Annahme mit ihren Nachweisen. Vor **Berechnungsfassung genehmigen** Betraege, Positionen, Vertragsgrundlage und gegebenenfalls Qualitaetsabweichungen pruefen. Eine gemeldete Qualitaetsausnahme benoetigt eine ausdrueckliche Bestaetigung fuer genau diese Berechnung.

Der Dialog zeigt Annahme, Betraege und Berechnungsbindung. Ausfuehrung, Pruefvermerk und Genehmigungsfrist sind bewusst anzugeben. Die Genehmigung gilt ausschliesslich fuer diese unveraenderte Fassung. Im gezeigten synthetischen Beispiel ergeben sich 5.417,50 EUR netto, 379,23 EUR Steuer und 5.796,73 EUR brutto.

![Finanzielle Gegenpruefung mit Betrag und konkreter Berechnungsbindung](img/ernte-freigabe-20261015/finanzgenehmigung.jpg)

## Gutschrift und Wareneingang ausfuehren

Der berechtigte Bearbeiter laedt den aktuellen Stand erneut und oeffnet **Gutschrift und Wareneingang erzeugen**. Die angezeigte Fassung und Betraege vor der ausdruecklichen Bestaetigung vergleichen. Fehlende, abgelaufene oder inzwischen unpassende Nachweise sperren die Ausfuehrung. Eine erneute Ausfuehrung darf keine zweite Geschaeftswirkung erzeugen.

![Ausfuehrungsdialog vor einer ausdruecklichen Bestaetigung](img/ernte-freigabe-20261015/ausfuehrungspruefung.jpg)

**Stand der dokumentierten Browserabnahme:** Anmeldung, Regelanlage und -genehmigung, Regelbindung, Messbestaetigung, Berechnung und finanzielle Gegenpruefung sind real erfolgt. Die abschliessende Geschaeftsausfuehrung ist noch gesondert abzunehmen; die letzte Abbildung zeigt deren Pruefdialog vor der Bestaetigung. Es wurde dabei keine Zahlung oder externe Meldung ausgefuehrt. Die temporaere Prueferrolle wurde anschliessend entzogen und die Kennung gesperrt. [Technischer Abnahmestand](../quality-assurance/harvest-rule-store-20261015.md).
