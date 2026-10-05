---
title: "Fuetterungsberatung — integriertes Fachkonzept"
type: specification
audience: [fachlich, produkt, architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Fachliche Gesamtlogik von Betriebsakte, Datenreife, Rationsentscheidung, Ausfuehrung, Controlling und Beratung.
---

# 03 — Fachkonzept

## 1. Fachliches Zielbild

Die Fuetterungsberatung ist kein isolierter Agrarrechner. Sie ist ein
entscheidungsorientierter ERP-Prozessraum, der Stammdaten, Laborwerte,
Herdenanforderungen, Rationen, Versorgung, Kosten, Ausfuehrung und Wirkung
revisionssicher verbindet. Die fachliche Leitfrage lautet immer:

> Welche belastbare Entscheidung ist fuer welche Tiergruppe, auf Basis welcher
> Daten und Regelversion, zu welchem Zeitpunkt freigegeben und mit welcher
> Wirkung umgesetzt worden?

## 2. Fachliche Prinzipien

| ID | Prinzip | Konsequenz |
|---|---|---|
| FEED-FK-001 | Datenreife vor Optimierung | fehlende Analyse, Einheit, Preis oder Gruppenparameter blockiert oder warnt explizit |
| FEED-FK-002 | Version vor Veraenderung | fachlich relevante Freigaben erzeugen unveraenderliche Snapshots |
| FEED-FK-003 | Erklaerung vor Automatik | Vorschlaege zeigen Ziel, Einfluss, Unsicherheit und Alternativen |
| FEED-FK-004 | Wirkung vor Aktivitaet | Beratung wird an Soll-Ist- und Leistungsentwicklung bewertet |
| FEED-FK-005 | Provenienz vor Bequemlichkeit | importierte und berechnete Werte behalten Quelle und Mappingversion |
| FEED-FK-006 | Aufgabe vor Modul | Nutzer starten bei Betriebsfrage und naechster Entscheidung, nicht in einer Maskensammlung |
| FEED-FK-007 | Zentraler Vertrag vor Sondermaske | Meridian rendert ScreenDefinition/RenderPlan; Domain-Overlays bleiben klein |
| FEED-FK-008 | Port vor Provider | Labor, Herdenmanagement und Mixer implementieren neutrale Ports mit Quarantaene |

## 3. Kernobjekte und fachliche Verantwortung

| Objekt | Verantwortung | Unveraenderliche Referenzen |
|---|---|---|
| FeedingBusiness | fachlicher Betriebs- und Zugriffsscope | Tenant, CRM-Partnerreferenz |
| FarmSite/Herd/FeedingGroup | stabile Produktionshierarchie | Business- und Tenantzuordnung |
| Feed/FeedProduct | Identitaet und Einsatzkontext eines Futters | Artikel-/Referenzbezug |
| FeedAnalysis | messwertbezogene Wahrheit zu Zeitpunkt und Probe | Quelle, Methode, Bezugsbasis |
| RequirementProfile | versionierter Bedarf einer Gruppenklasse | Bewertungssystemversion |
| RationVersion | bewertete Zusammensetzung und Entscheidungsstand | Inputs, Regeln, Solverlauf |
| FeedingPlanVersion | freigegebene, ausführbare Mischanweisung | RationVersion, Gültigkeit |
| FeedingExecution | tatsaechliche Ausfuehrung | Planversion, Zeitpunkt, Quelle |
| ConsultingCase | Beratungsanlass, Entscheidung und Massnahmen | Betrieb, Zeitraum, Beteiligte |
| Observation/Measure | Wirkung und Folgearbeit | Quelle, Verantwortlicher, Termin |

Detailgrenzen, Aggregate und Events stehen in Kapitel 04; Tabellen in Kapitel 05.

## 4. Betriebsakte als Prozessanker

Die Betriebsakte zeigt nicht alle Daten gleichzeitig. Sie beantwortet priorisiert:

1. Welche Betriebe liegen im Zugriff des Nutzers?
2. Wo fehlen Gruppen-, Analyse-, Preis- oder Bestandsdaten?
3. Welche Ration wartet auf Bearbeitung oder Freigabe?
4. Welcher Plan ist aktuell, laeuft aus oder wurde ueberholt?
5. Wo weicht die Ausfuehrung fachlich oder wirtschaftlich ab?
6. Welche Massnahme ist faellig und welche Wirkung ist erkennbar?

Die Akte ist eine ObjectPage-Projektion ueber vorhandene Aggregate, kein neues
Monolith-Aggregat. Schreibaktionen bleiben beim fachlich verantwortlichen Service.

## 5. Datenreife und Provenienz

### 5.1 Reifestufen

| Stufe | Bedeutung | Zulässige Aktion |
|---|---|---|
| missing | Pflichtinformation fehlt | erfassen/importieren |
| quarantined | Mapping oder Plausibilitaet ungeklärt | pruefen, zuordnen, verwerfen |
| provisional | verwendbar mit kenntlicher Unsicherheit | simulieren, nicht freigeben wenn blocking |
| validated | technisch und fachlich plausibel | Ration bewerten |
| released | verantwortliche Freigabe erfolgt | in Planversion referenzieren |
| superseded | gueltiger Nachfolger vorhanden | historische Nachvollziehbarkeit |

### 5.2 Wertnachweis

Jeder entscheidungsrelevante Wert fuehrt soweit zutreffend: Wert, Einheit,
Bezugsbasis FM/TM, Erfassungs-/Analysezeit, Gueltigkeitsintervall, Quelle,
Quellreferenz, Methode, Mappingversion, Ersteller und Unsicherheitsstatus.

## 6. Rationsentscheidung

### 6.1 Eingang

- Tiergruppe und gueltiges Anforderungsprofil;
- freigegebene oder bewusst provisorische Futteranalysen;
- Verfuegbarkeit, Preis und Einsatzgrenzen;
- Zielhierarchie, Optimierungsmodus und erlaubte Toleranzen;
- Bewertungssystem- und Solverversion.

### 6.2 Ergebnis

Ein Ergebnis umfasst Zusammensetzung, Nährstoffbewertung, Restriktionsstatus,
Kosten, Risiken, Provenienz, Solverdiagnostik und Alternativen. `optimal` bedeutet
nur mathematisch optimal innerhalb der dokumentierten Eingaben und Grenzen.

### 6.3 Entscheidungsstufen

```text
draft → evaluated → proposed → approved → scheduled → active → retired → archived
```

Guards, verbotene Uebergaenge und Kompensation stehen in Kapitel 08. Eine
Freigabe friert Eingaben, relevante Regeln, Ergebnis und Begruendung ein.

## 7. Varianten und Warnungen

Varianten werden nicht nur anhand eines Scores sortiert. Der Vergleich zeigt
mindestens Mengen, Nährstoffdeckung, Grenznaehe, Kosten, Verfuegbarkeit,
Mischbarkeit, Nachhaltigkeitsindikatoren und geaenderte Risiken. Unbekannte Werte
bleiben Luecken.

Warnungen besitzen vier fachliche Stufen: Information, Hinweis, Warnung,
Blockierung. Jede Warnung fuehrt Ursache, betroffene Position/Wert, Regelquelle,
Handlungsoption und Zeitpunkt. Eine bestaetigte Warnung wird nicht geloescht,
sondern mit Entscheidung und Begruendung auditiert.

## 8. Plan, Ausfuehrung und Versorgung

Nur eine freigegebene Rationsversion kann eine Planversion speisen. Die
Planversion skaliert reproduzierbar auf Tierzahl/Zeitraum, beruecksichtigt
Dosier- und Rundungsregeln und erzeugt eine menschen- sowie maschinenlesbare
Mischfolge. Nach Aktivierung bleibt sie unveraenderlich.

Ist-Mengen referenzieren die ausgefuehrte Planversion. Abweichungen werden nach
Menge, Zeitpunkt, Substitution, Restmenge, Technik und Datenfehler klassifiziert.
Bedarf/Reichweite erzeugt einen Einkaufsvorschlag, niemals ungeprueft eine
Bestellung.

## 9. Soll-Ist und Wirkung

Controlling verbindet Plan, Ausfuehrung und Leistungsbeobachtung auf derselben
Zeitachse. Kennzahlen enthalten Datenabdeckung und Versionsmarker. Ein Wechsel
von Gruppe, Analyse, Ration oder Plan wird im Trend sichtbar, damit Vorher/Nachher
nicht falsch kausal interpretiert wird.

Beratungsmassnahmen besitzen Verantwortlichen, Faelligkeit, erwartete Wirkung,
Status und Wirksamkeitspruefung. Statistische Signale unterstuetzen die Bewertung,
ersetzen aber keine fachliche Kausalentscheidung.

## 10. Integrationsfachkonzept

Alle Importe folgen derselben Kette:

```text
receive → authenticate → persist raw reference → validate schema
→ map/version → deduplicate → quarantine or apply → journal → notify
```

Delta-Sync verarbeitet neue, geaenderte, verschobene und geloeschte Datensaetze.
Idempotenzschluessel verhindern Doppelwirkung. Providerfaehigkeiten werden erst
nach Vertrag und Smoke-Test als live ausgewiesen. Details: Kapitel 12.

## 11. KI-Unterstuetzung

Agenten duerfen lesen, erklaeren, priorisieren, simulieren und Entwuerfe
vorbereiten. Schreibende Tools brauchen Scope, Schema, Idempotenz und Policy;
Freigabe, externe Kommunikation, Bestellung und Maschinenaktion benoetigen ein
Human Gate. Jede Empfehlung nennt Datenstand, Annahmen und Unsicherheit.

## 12. Bedienkonzept

Der Standardmodus ist eine ruhige, entscheidungsorientierte Meridian-Oberflaeche.
Experten erhalten Dichte, Tastatursteuerung, Varianten- und Ursachenanalyse ohne
eine getrennte Anwendung. Responsive Verhalten veraendert Layout und Dichte,
nicht Fachstatus oder Berechnung. Kapitel 07 und 10 sind der Bedienvertrag.

## 13. Fehler- und Konfliktbehandlung

| Konflikt | Fachliche Reaktion |
|---|---|
| stale version | 409, aktuelle Version laden, Unterschiede zeigen |
| fehlender Grant | 403 ohne Ressourceninhalt zu leaken |
| unbekannte Einheit | Quarantaene, keine stillschweigende Konvertierung |
| unloesbare Optimierung | Konfliktgrenzen und kleinste Relaxationen zeigen |
| Provider nicht erreichbar | Retry/Circuit Breaker; letzter Datenstand markiert |
| Plan inzwischen ersetzt | Ausfuehrung blockieren oder explizite Ausnahme auditieren |
| Teilimport | atomare Einheit definieren; Fehlerjournal und Wiederaufnahme |

## 14. Fachliche Kennzahlen

Produktqualitaet wird nicht an Klickzahl allein gemessen. Kernmetriken sind
Datenreifezeit, Zeit bis belastbare Variante, Freigabedurchlauf, Anteil erklaerter
Warnungen, Planaktualitaet, Soll-Ist-Abdeckung, Reichweitenwarn-Vorlauf,
Massnahmenabschluss, Wirkungsmessabdeckung und Zahl manueller Doppelerfassungen.

## 15. Abnahme und Drift

Die fachliche Abnahme verwendet die 15 Journeys aus Kapitel 08 und die stabilen
Tests aus Kapitel 13. Jede Umsetzung aktualisiert Traceability und Arbeitspaket.
Dieses Kapitel beschreibt Semantik; konkrete Felder, Endpunkte, Tabellen und
Formeln bleiben in Kapitel 05/06/09 beziehungsweise ihren Laufzeitquellen.

