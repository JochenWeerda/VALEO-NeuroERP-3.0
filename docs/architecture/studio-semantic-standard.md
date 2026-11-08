---
title: Dialogfaehiges Agentic Studio und STUDIO-SEMANTIC-001
type: reference
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# Verbindlicher Entwicklungsauftrag

Vom Nutzer am 2026-10-15 vorgegeben. Die folgenden Regeln und Abnahmekriterien sind verbindlich; die beschriebenen zukuenftigen Funktionen sind keine Behauptung ihres heutigen Lieferstands. Vorlagen bleiben Einstiegspunkte, keine vollwertige Dialogimplementierung.

## VALEO-NeuroERP 3.0 – Entwicklungsplan für ein dialogfähiges Agentic Studio

Die wichtigste Erkenntnis: Der Studio-Agent muss die Fachsprache des Sachbearbeiters verstehen und daraus eine prüfbare, ausführbare Maskendefinition erzeugen – ohne SQL-Kenntnisse, Tabellen- oder Spaltennamen.

Den aktuellen Stand würde ich so bewerten:

| Bereich                                                     | Status                      |
| ----------------------------------------------------------- | --------------------------- |
| Godfile-Ratsche, Dokumentation, PostgreSQL, beide E2E-Läufe | Bestanden                   |
| Gesamte CI-Pipeline                                         | Noch nicht vollständig grün |
| Single-Mask-Builder-Vertrag                                 | Vorhanden                   |
| Vier feste Vorlagen                                         | Vorhanden                   |
| Mehrstufiger fachlicher Agentendialog                       | Fehlt                       |
| Verständliche Auswahl freigegebener Datenfelder             | Fehlt                       |
| Komplexe Maske einschließlich Speichern und Validieren      | Noch nachzuweisen           |

Meine Entscheidung: Wir entwickeln die bestehende Studio- und Meridian-Architektur weiter. Kein zweiter MaskBuilder, kein paralleler Formular-Generator und keine direkte Datenbankmodellierung durch den Agenten.

## 1. Wie der zukünftige Studio-Dialog funktionieren soll

Ein Mitarbeiter beschreibt seine Anforderung beispielsweise so:

> Ich möchte eine Maske für die Getreideannahme. Oben sollen Lieferant, Kontrakt und Fahrzeug stehen. Darunter die Verwiegung. Anschließend Feuchtigkeit, Besatz und Hektolitergewicht. Daraus sollen die Abzüge und der Abrechnungspreis berechnet werden. Bei ungewöhnlichen Werten muss der Controller einen Hinweis bekommen.

Der Studio-Agent soll daraufhin:

1. Die fachliche Absicht erkennen und den geeigneten bestehenden Geschäftsprozess ermitteln.
2. Die freigegebenen Felder, Beziehungen, Regeln und Aktionen aus der Capability Registry ermitteln.
3. Dem Mitarbeiter gezielte fachliche Rückfragen stellen, beispielsweise ob Brutto- und Taragewicht automatisch von der Waage übernommen werden.
4. Eine ScreenDefinition erstellen und die ausgewählten Felder fachlich verständlich erläutern.
5. Eine funktionsfähige Vorschau mit Beispieldaten anzeigen.
6. Datenbindung, Pflichtfelder, Berechnungen, Berechtigungen und Prozessübergänge validieren.
7. Die Maske in einer isolierten Umgebung simulieren.
8. Nach bestandenen Prüfungen eine versionierte Freigabe ermöglichen.

Der Bearbeiter entscheidet über Geschäftsabläufe und Gestaltung. Die Engine entscheidet deterministisch, welche technischen Datenbindungen und Aktionen zulässig sind.

## 2. Die fehlende Komponente: Semantic Business Catalog

Ich würde die bestehende Capability Registry um eine fachliche Bedeutungsschicht erweitern.

| Was der Mitarbeiter sagt | Was die Engine zuordnet                             |
| ------------------------ | --------------------------------------------------- |
| Lieferant                | Autorisierter Geschäftspartner mit Lieferantenrolle |
| Getreidesorte            | Freigegebenes Artikel-/Sortenmerkmal                |
| Feuchtigkeit             | Qualitätsmesswert mit Einheit und Wertebereich      |
| Nettogewicht             | Ergebnis einer zugelassenen Wiegeberechnung         |
| Abzüge                   | Versionierte Qualitäts- und Vertragsregeln          |
| Abrechnungspreis         | Deterministische Preisberechnung                    |
| Freigeben                | Berechtigter Workflow-Übergang                      |

Jeder Katalogeintrag erhält eine verständliche Beschreibung, Synonyme, Einheit, Datentyp, fachlichen Besitzer, Berechtigungen und Verweise auf die gültigen Verträge.

Entscheidend: Der Agent darf keine Datenbankfelder erfinden. Kann er eine Anforderung nicht eindeutig zuordnen, muss er eine Klärung oder eine Erweiterung des fachlichen Vertrags vorschlagen.

## 3. Entwicklungsphasen

Phase 1 – Browser-Baseline sichern

Den vorhandenen Studio-Ablauf vollständig prüfen: Vorlage auswählen, bearbeiten, speichern, erneut öffnen, validieren und Vorschau ausführen.

Abnahme: Kein Datenverlust, keine doppelte Version, nachvollziehbare Fehlermeldungen und eine tatsächlich verwendbare Referenzmaske.

Phase 2 – Fachkatalog und Vertragsauflösung

Bestehende Domain-Schemas, ScreenDefinitions, Actions und Berechtigungen inventarisieren und fachsprachlich beschreiben.

Abnahme: Für jedes verwendete Feld ist der erlaubte technische Vertrag eindeutig identifizierbar.

Phase 3 – Mehrstufiger Agentendialog

Der Agent sammelt Anforderungen, fragt gezielt nach, dokumentiert Entscheidungen und erzeugt einen strukturierten Maskenentwurf.

Abnahme: Ein fachlicher Bearbeiter kann die Referenzmaske ohne SQL-, Tabellen- oder Spaltenkenntnisse erstellen.

Phase 4 – Deterministische Simulation

Test von Dateneingabe, Validierungen, Berechnungen, Berechtigungen, Statusübergängen sowie Fehler- und Stornopfaden.

Abnahme: Keine produktiven Nebenwirkungen; Ergebnisse sind reproduzierbar und dokumentiert.

Phase 5 – Freigabe und Veröffentlichung

Synchronisierung der API-/MCP-Artefakte, Rollenprüfung, Versionshistorie, verpflichtende CI-Gates und abschließende Browserprüfung.

Abnahme: Ausschließlich die geprüfte, unveränderte Version darf veröffentlicht werden.

## 4. Wichtige Testfälle

Ich würde die Entwicklung an einer komplexen Getreideannahme-Maske mit folgenden Szenarien messen:

| Szenario                                         | Erwartung                                           |
| ------------------------------------------------ | --------------------------------------------------- |
| Bearbeiter verwendet nur Fachbegriffe            | Studio findet die korrekten Capability-Verträge     |
| Fachliche Anforderung ist mehrdeutig             | Agent fragt gezielt nach                            |
| Gewünschtes Feld existiert nicht                 | Erweiterungsvorschlag statt erfundener Datenbindung |
| Bearbeiter verändert Anforderungen               | Entwurf wird kontrolliert angepasst und versioniert |
| Agent wiederholt Speichervorgang                 | Keine doppelte Fassung                              |
| Unberechtigter Mitarbeiter fordert Preisänderung | Aktion wird serverseitig verweigert                 |
| Mandant oder Kunde wird manipuliert              | Zugriff wird verweigert                             |
| Berechnung liefert unzulässigen Wert             | Validierung verhindert Freigabe                     |
| Simulation eines Buchungsvorgangs                | Keine Änderung produktiver Finanzdaten              |
| API-Vertrag ändert sich                          | Versions-/Kompatibilitätsprüfung schlägt an         |

Die bestehenden Fehler in der Gesamtpipeline müssen separat klassifiziert werden. Sicherheitsrelevante Fehler dürfen durch die neuen Studio-Funktionen nicht überdeckt oder aus den Quality Gates ausgenommen werden.

## 5. Zusätzliche Architekturregel: STUDIO-SEMANTIC-001

# STUDIO-SEMANTIC-001 – Fachsprachliche Maskenerstellung

Das VALEO Studio ermöglicht die Erstellung und Anpassung komplexer ERP-Masken durch einen mehrstufigen Dialog in natürlicher Fachsprache.

**Verbindliche Vorgaben:**

1. Der Bearbeiter benötigt keine Kenntnisse über Datenbanktabellen, Spaltennamen, SQL, API-Endpunkte oder interne Datenmodelle.
2. Der Agent übersetzt fachliche Anforderungen ausschließlich in registrierte, versionierte und autorisierte Daten-, Aktions- und Workflow-Verträge.
3. Mehrdeutige oder nicht erfüllbare Anforderungen werden durch gezielte Rückfragen geklärt. Fehlende Fachfunktionen dürfen nicht durch erfundene Datenbindungen ersetzt werden.
4. Jeder generierte Entwurf verwendet den bestehenden Meridian-/Single-Mask-Builder-Vertrag und die zentrale ScreenDefinition-Engine.
5. Fachliche Berechnungen, Validierungen, Mandantenisolation und Berechtigungen bleiben in den deterministischen Domain-Services.
6. Der Agent darf Maskenentwürfe erstellen und verändern, aber weder eigenständig produktive Datenbankschemata ändern noch kritische Geschäftsregeln veröffentlichen.
7. Entwürfe müssen idempotent, versioniert und nachvollziehbar gespeichert werden.
8. Vor Veröffentlichung sind Preview, Datenbindung, Berechtigungen, Prozesssimulation, API-Vertragsprüfung und CI-Gates erfolgreich abzuschließen.
9. Für jede veröffentlichte Version müssen Entstehung, Änderungen, verwendete Verträge, Prüfungen und Freigabe nachweisbar bleiben.
10. Bestehende Framework-Komponenten sind wiederzuverwenden. Parallele Masken-Engines und redundante Geschäftslogik sind untersagt.

**Leitprinzip: Fachsprache hinein – geprüfte ERP-Funktionalität heraus.**

## 6. Meine Priorisierung

Die vier festen Vorlagen sollten erhalten bleiben, aber künftig nur noch als Startpunkte für einen fachsprachlich gesteuerten Dialog dienen.

Ich würde dabei ausdrücklich noch keinen autonomen Agenten entwickeln lassen, der eigenständig neue Fachmodule oder Datenbankschemata erzeugt. Zuerst muss die Engine aus den vorhandenen, freigegebenen Geschäftsbausteinen zuverlässig komplexe Masken zusammensetzen können.

Der nächste konkrete Meilenstein lautet:

Ein Sachbearbeiter erstellt im Studio allein durch ein Fachgespräch eine vollständige Getreideannahme-Maske, testet einen Vorgang mit realistischen Simulationsdaten, überarbeitet die Maske und übergibt die geprüfte Version zur Freigabe.

Wenn dieser End-to-End-Nachweis gelingt, ist das ein belastbarer Fortschritt von einem klassischen MaskBuilder zu einem agentenunterstützten ERP-Entwicklungsstudio.

## Einordnung und Nachweisgrenzen

Bestehende [Studio-Governance](domains/platform/studio-governance.md), [MCP-Schreibstandard](mcp-write-standard.md) und [Studio-Freigabestandard](studio-release-standard.md) gelten gemeinsam. Fachkatalog und Dialog sind Erweiterungen bestehender Registry-/Domain-Vertraege, keine zweite Rechteverwaltung oder Masken-Engine. Jede technische Bindung muss Vertragskennung und Version ausweisen. Unbekannte Begriffe ergeben klaerende Rueckfragen oder einen ausgewiesenen Vertragsbedarf, niemals freie SQL-/Endpoint-Erfindung.

Eine interaktive Berechnungsvorschau prueft die Eingaben mit bestehenden Domain-Services. Sie erzeugt keine Buchungen und ersetzt keine revisionsgebundene Prozesssimulation. Das bestehende grain.v1-Profil deckt nur seine ausdruecklich modellierte Variante ab. Neue Regeln, Schreibaktionen und abweichende Varianten bleiben bis zur eigenen Abnahme gesperrt.

Der Dialog liefert pruefbare Vorschlaege. Ohne verfuegbares Sprachmodell muss eine kataloggestuetzte Bedienung als solche erkennbar sein; feste Vorlagen oder Schluesselworterkennung duerfen nicht als lernender Agent ausgegeben werden. Fachliche Entscheidungen, Rueckfragen und Antworten muessen der Entwurfsversion zuordenbar sein; Modellantworten sind unvertrauenswuerdige Eingaben und werden serverseitig gegen erlaubte Vertraege validiert.

Lieferstand und CI-Nachlauf: [QA und Umsetzungsstand](../quality-assurance/studio-semantic-20261015.md).


## Ergaenzung des Nutzers: Abrechnungsgrundlage

[HARVEST-DEDUCTION-001](harvest-deduction-contract-standard.md) trennt Qualitaetsgrenze, echte Freigrenze, Messfraktionen und versionierte Vertragsgrundlage. Eine reine Qualitaetsbewertung oder technisch moegliche Berechnung erteilt keine Vertragsfreigabe. Die manuelle Studio-Probe bleibt vor produktiver Aktivierung gesperrt.
