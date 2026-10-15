---
title: Agentic Studio Auftrag und CI-Nachlauf
type: reference
audience: [entwickler, agent, architect]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Abnahmeplan und ehrlicher Lieferstand

## CI-Nachlauf der Baselinesenkung

Gepruefter Commit: bd54b5cd5. Die unabhaengige Integritaetspruefung einschliesslich Godfile-Ratsche war erfolgreich. [Quality Gate](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745449) insgesamt fehlgeschlagen: Backend und Dependency Scan. Diese Fehler werden nicht durch Studio-Ausnahmen verdeckt.

Erfolgreich: [Docs Governance](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745165), [Docs Build](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745247), [PostgreSQL-Tests](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745104), [kritische semantische E2E-Pfade](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745364) und [E2E Smoke](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745100).

Fehlgeschlagen: [Service Security](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745074) und [Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38683745192). Der getrennte CI/CD-Lauf war beim Abruf noch nicht abgeschlossen. Kein Gesamt-Gruen-Nachweis. develop bleibt an der bereits dokumentierten privaten Identitaetspruefung eines fremden CI-Vorgaengers blockiert; kein Hook-Bypass.

## Etappe 1: Architekturauftrag

Nutzerplan als [STUDIO-SEMANTIC-001](../architecture/studio-semantic-standard.md) uebernommen und mit bestehender Governance verknuepft. Dies ist eine Dokumentationsetappe, kein Nachweis fertig implementierter Dialogfunktionen.

## Noch abzuarbeitende Funktionsabnahme

1. Bestehende Studio-Baseline im Browser: anlegen, bearbeiten, speichern, erneut oeffnen, validieren, Vorschau. Eingaben und Historie vergleichen; Wiederholung darf keine Zusatzversion erzeugen.
2. Fachkatalog: freigegebene Vertragskennungen, Versionen, fachliche Bezeichnungen, Synonyme, Einheiten, Wertebereiche, Fachverantwortung und Berechtigungen; fehlende Bindung sichtbar sperren.
3. Mehrstufiger Dialog: Getreideannahme-Anforderung, gezielte Rueckfrage zur Waage, nachvollziehbare Antwort, kontrollierte Entwurfsanpassung; nur freigegebene Katalogelemente.
4. Interaktive Referenzmaske: Lieferant, Kontrakt, Fahrzeug, Verwiegung und Qualitaet; bestehende Domain-Berechnung statt nachgebauter Geschaeftsmathematik. Ungueltige und nicht endliche Werte verweigern. Vorschau ohne produktive Nebenwirkungen.
5. Revisionstreue Prozesssimulation: erlaubte Eingaben, Rollen-/Mandantengrenzen, Wiederholung, Fehler und Korrektur; bestehender grain.v1-Nachweis gilt nicht automatisch fuer neue Varianten.
6. Freigabeuebergabe: exakte unveraenderte Revision, verwendete Vertraege, Historie und Artefaktsynchronisierung; unvollstaendige Nachweise sperren. Kein Agent darf selbst kritische Regeln aktivieren.

Echte Browserbilder und Pruefergebnisse werden erst nach Ausfuehrung ergaenzt. Keine fingierten Screenshots oder Testzahlen. Gemeinsamen Pruefstand wiederverwenden, keine neue Datenbank oder Container.


## Implementierungsstand 2026-10-15

Der Studio-Katalog fuehrt agrar.harvest.manual-preview.v1 mit 13 fachlich benannten Parametern, Einheiten, Synonymen, Schema und Vertragsversion. Vier Eingaben sind verpflichtend, weitere optional. Unbekannte Felder, Quellen und Aktionen werden serverseitig abgewiesen. Fehlende optionale Messwerte bleiben unbekannt und werden nicht als gemessene Null erfunden. Die alte freie feld_N-Spaltenerzeugung wurde aus der Bedienung entfernt.

Der mehrstufige Katalogdialog klaert Prozess und manuelle Wiegeeingabe sowie den begrenzten Umfang. Gespraech und Entscheidungen werden mit der normalen ScreenDefinition gespeichert. Ein neuer Vorschlag ersetzt keinen ausgewaehlten gespeicherten Entwurf stillschweigend. Optionale Fachfelder lassen sich anschliessend aus-/einblenden, kompatible Testwerte bleiben erhalten; entfernte Werte werden aus der Kalkulationsanfrage entfernt. Der zentrale RenderPlan-Cache beruecksichtigt strukturelle Aenderungen unter gleicher Screen-ID/Version.

UniversalFormState und UniversalMaskRenderer tragen die interaktive Vorschau. Der bestehende Domain-Kalkulator liefert dynamische Positionen und exakte Decimal-Betraege; keine nachgebaute Geschaeftsformel. Fehlende Pflichteingaben, nicht endliche Zahlen, Bereichsverletzungen, fremde Mandanten-/Endpoint-Parameter und negative Abrechnungsergebnisse werden verweigert. Alte und verspaetete Berechnungsergebnisse verschwinden bei geaenderten Eingaben. Testwerte werden nicht als Geschaeftsbeleg gespeichert.

## Optionales echtes Sprachmodell

Das bestehende mandantenspezifische Gateway ist angebunden. Der Benutzer muss den Modellmodus ausdruecklich waehlen und ein eigenes vorhandenes Kontingent auswaehlen. Der Server reserviert vorab im vorhandenen identity_quota-Nebenbuch, bindet Auftrag/Issuer/Mandant/Subject und rechnet die vom Anbieter gelieferten Token ab. Redis-Ausfuehrungsbelege verhindern Wiederholungs-Doppellaeufe. Verlorene/unklare Providerabschluesse behalten Reservierungen zur Abstimmung, statt Verbrauch zu erfinden oder automatisch zu erstatten.

Antworten aller drei vorhandenen Providerfamilien werden auf gueltige Verbrauchswerte geprueft. Schemawidrige Modellantworten werden abgewiesen und bekannter Verbrauch trotzdem als fehlgeschlagener Auftrag abgerechnet. Bei Provider-Overruns wird kein Ergebnis geliefert; Reservierung und Auftrag bleiben klaerungspflichtig. Die Reservierung nutzt eine konservative UTF-8-/Ausgabegrenze mit Framingreserve und ist kein exakter Provider-Tokenizer. Produktionsfreigabe benoetigt deshalb auch Anbietergrenzen und Abstimmungsbetrieb fuer solche Vorfaelle.

Im lokalen Sichtpruefungsmandanten ist ein Modell konfiguriert. Die unveraenderte synthetische Testkennung besitzt jedoch kein sichtbares eigenes Kontingent. Der positive reale Modellaufruf wurde deshalb nicht behauptet und kein Kontingent automatisch vergeben. Katalogdialog und Berechnungsvorschau sind davon unabhaengig benutzbar. Modell-/Quotenvertraege sind mit simulierten Anbieterantworten geprueft.

## Pruefungen

27 Frontend-/Compilerfaelle bestanden, darunter echte zentrale FormState-Eingabe, Datenerhalt bei Feldauswahl, verspätete Antworten, Rueckfragen und vorhandene Freigabesperren. Fokussierter Typecheck Status 0. 118 Backend-Vertragsfaelle bestanden; vier reale SQL-/Prozessnachweise separat bestanden, darunter echte grain.v1-Kette mit dreizehn Invarianten, Replay, gescheiterte Beweisspeicherung, fremder Mandant und belegter gemeinsamer Pruefstand. Keine Skips in diesen Abnahmen, keine neue Datenbank oder Container, keine Migration oder Ruecksetzung.

Der erste kombinierte Aufruf verweigerte vier Setups, weil sein Teststarter den Pruefstand zugleich als Entwicklungsdatenbank deklarierte. Das war eine korrekte Schutzentscheidung. Der nachfolgende Prozesslauf nutzte expliziten Pruefstand bei unveraenderter realer Entwicklungsdatenbank-Identitaet; alle vier Faelle bestanden. Keine Schutzpruefung wurde gelockert.

OpenAPI, Serviceinventar, Architekturindex und ADR-Navigation wurden aus HEAD plus eigenen Aenderungen projiziert. Fremde Arbeitskopien blieben erhalten. Vollstaendige Architekturzuordnung: 941 Routen, 295 Dienste, 460 Endpointmodule. Zusaetzlich drei zuvor fehlende exakte Zuordnungen ergaenzt (Studio-Historie, Studio-Prozesssimulation, SEPA-XML), keine generischen Prefixausnahmen.

## Verbleibende Gesamtziel-Luecken

Die manuelle Kalkulationsprobe ist keine vollstaendige Getreideannahme mit Lieferanten-/Kontrakt-/Waagenbindung, Controllerbenachrichtigung oder konfigurierten Trocknungsregeln. Diese Fachvertraege und zugehoerige Variantenabnahmen sind offen. Der neue Vorschauvertrag bleibt deshalb im grain.v1-Release-Gate gesperrt; das Bestehen der bestehenden festen Prozesskette zertifiziert ihn nicht. Einreichung zur Pruefung ist moeglich, produktive Aktivierung nicht. Neue MCP-/CLI-Writes bleiben deaktiviert.

Positive Modell-Browserabnahme mit eigenem Kontingent und Abstimmungsbetrieb unbekannter Providerabschluesse stehen aus. Die bekannten fremden Backend-/Sicherheitsbefunde und die develop-Push-Sperre bleiben separat offen. Kein pauschaler Gesamtabschluss.


Positionsanzeige: Die Besatz-Bezeichnung verwendet jetzt dieselbe explizite Freigrenze wie die vorhandene Formel; bei 0/2/3 Prozent gesondert geprueft. Windabgang bleibt gemaess kanonischem Domain-Kommentar rein informativ und wird in Katalog/Warnung so benannt. Keine neue Abzugsformel eingefuehrt. Ein unpassender kombinierter Teststarter zeigte anschliessend auch die umgekehrte DB-Grenze; die beiden kanonischen getrennten Laeufe bleiben fuehrend, ihre Schutzregeln unveraendert.
