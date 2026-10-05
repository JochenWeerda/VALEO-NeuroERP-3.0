---
title: "01 — Glossar und Ubiquitous Language Fuetterungsberatung"
type: reference
audience: [produkt, fachlich, architektur, entwickler, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Verbindliche deutschsprachige Fachbegriffe, englische Codebegriffe, Abgrenzungen und verbotene Synonyme fuer den Feeding-Bounded-Context.
---

# 01 — Glossar

## 1. Sprachregeln

- UI und Fachkommunikation verwenden den deutschen Begriff.
- Code, Events und API verwenden den stabilen englischen Codebegriff.
- Ein Begriff bezeichnet genau ein fachliches Konzept; Synonyme werden nur als
  Suchbegriffe, nicht als wechselnde Feldnamen verwendet.
- `Betrieb`, `Mandant`, `Geschaeftspartner` und `Standort` sind nicht synonym.
- `Ration`, `Rationsversion` und `Fuetterungsplanversion` sind nicht synonym.
- `Soll`, `Ist`, `geschaetzt`, `importiert` und `berechnet` muessen unterscheidbar sein.

## 2. Organisation und Tiere

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Mandant | Tenant | rechtlich/organisatorisch isolierter ERP-Datenraum; oberste Sicherheitsgrenze |
| Geschaeftspartner | BusinessPartner | CRM-Stammsatz; wird nicht vom Feeding-Kontext besessen |
| Fuetterungsbetrieb | FeedingBusiness | fachliche Feeding-Aktivierung eines CRM-Partners innerhalb eines Mandanten |
| Betriebsstaette | FarmSite | physischer/organisatorischer Standort eines Fuetterungsbetriebs |
| Stall/Haltungsbereich | HousingArea | optionaler Teil einer Betriebsstaette; keine Herde und keine Tiergruppe |
| Herde | Herd | organisatorischer Tierbestand mit gemeinsamer Betriebs-/Managementzuordnung |
| Tiergruppe | AnimalGroup | planungsrelevante Menge aehnlicher Tiere mit gueltigem Bedarfsprofil |
| Tiergruppenstand | AnimalGroupSnapshot | unveraenderliche Parameterlage einer Tiergruppe zu einem Zeitpunkt/Zeitraum |
| Einzeltier | Animal | extern oder optional gefuehrtes Tier; Feeding arbeitet primaer mit Gruppenprojektion |
| Gruppenwechsel | GroupMembershipChange | zeitlich gueltige Zuordnung/Aenderung; kein Ueberschreiben historischer Werte |
| Leistungsfutterweg | PerformanceFeedingPath | getrennte Zuteilung z. B. Kraftfutterstation/Melkroboter neben dem Futtertisch |
| Betriebsgrant | FeedingBusinessGrant | zeitlich und scope-begrenztes Recht eines Subjects auf eine Feeding-Ressource |

## 3. Futter, Bestand und Analyse

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Futtermittel | Feed | fachliche, betriebsbezogene Futteridentitaet |
| Handelsprodukt | FeedProduct | kauf-/verkaufsfaehige Auspraegung mit Hersteller/Lieferant; nicht der Lagerartikel selbst |
| Referenzwert | FeedReferenceValue | bibliotheks-/normbasierter, nicht betrieblich gemessener Wert mit Herkunft |
| Charge | InventoryLot | physischer Lager-/Qualitaetskontext im Inventory/Feed-Chain-Nachbarkontext |
| Frischmasse | AsFed / FM | Masse im vorliegenden Zustand inklusive Wasser |
| Trockenmasse | DryMatter / TM | Masse ohne Wasser; Bezugsbasis vieler Nährstoffwerte |
| TM-Gehalt | DryMatterFraction | Anteil TM an FM; dimensionslos bzw. Prozent mit klarer Umrechnung |
| Futteranalyse | FeedAnalysis | fachlicher Kopf einer Probe/Analyse mit Labor, Methode, Datum und Originalbeleg |
| Analysewert | FeedAnalysisValue | Wert einer NutrientDefinition mit Einheit, Bezugsbasis, Qualitaet und Herkunft |
| aktive Analyse | ActiveFeedAnalysis | bewusst freigegebene Analyseversion fuer neue Berechnungen; aendert alte Versionen nicht |
| Schaetzwert | EstimatedValue | nicht gemessener Wert; muss pro Kennzahl gekennzeichnet sein |
| Analyse-Mapping | AnalysisMapping | gepruefte Zuordnung externer Probe/Feldkennung zu Futter/Charge/Silo |
| Reichweite | SupplyCoverage | Zeitraum, fuer den verfuegbare Menge einen planbasierten Bedarf deckt |
| Reservierung | FeedReservation | fuer eine Plan-/Mischmenge gebundener Bestand; Eigentum des Lagerkontexts |

## 4. Bedarf, Ration und Optimierung

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Normsystem | EvaluationSystem | benanntes fachliches Bewertungs-/Bedarfssystem, z. B. GfE, mit Version |
| Bedarfsprofil | RequirementProfile | versionierte Eingaben, Ziele und Korridore fuer eine Tiergruppe |
| Nährstoffdefinition | NutrientDefinition | erweiterbare semantische Definition mit Dimension, Bezugsbasis und Anzeige |
| Einheitendefinition | UnitDefinition | kanonische Einheit und erlaubte Umrechnung innerhalb einer Dimension |
| Ration | Ration | fachlicher Lebenszyklus-Kopf fuer eine Tiergruppe; enthaelt Versionen |
| Rationsversion | RationVersion | unveraenderlicher Inhaltsstand aus Komponenten, Constraints, Annahmen und Evaluation |
| Rationsposition | RationItem | Futtermittelmenge und Reihenfolge innerhalb einer Rationsversion |
| Nebenbedingung | RationConstraint | harte/weiche Grenze mit Quelle, Einheit, Scope und Prioritaet |
| harte Nebenbedingung | HardConstraint | darf fuer eine zulaessige Loesung nicht verletzt werden |
| weiche Nebenbedingung | SoftConstraint | darf mit expliziter Penalty/Erklaerung verletzt werden |
| Ausgangsration | BaselineRation | Referenz fuer minimale Umstellung oder Vergleich; nicht automatisch aktiv |
| Optimierungslauf | OptimizationRun | reproduzierbarer Job mit Inputreferenzen, Solver-/Normversion und Parametern |
| Optimierungsergebnis | OptimizationResult | Loesung oder erklaerter Fehlschlag eines Laufs; noch keine Freigabe |
| Variante | RationVariant | benannter Vergleichskandidat, meist eine Rationsversion oder ein Ergebnisentwurf |
| Pareto-Variante | ParetoVariant | nicht dominierte Loesung bei mehreren Zielgroessen |
| Grenzkosten | ShadowPrice | Sensitivitaetsinformation einer Nebenbedingung; nur mit Solver-/Einheitenkontext |

## 5. Bewertung und Freigabe

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Rationsbewertung | RationEvaluation | strukturierte Bewertung einer konkreten Rationsversion |
| Warnung | EvaluationWarning | Kennzahlbezogener Befund mit Ziel, Ursache, Folge, Quelle und Empfehlung |
| Readiness | ReadinessAssessment | Vorbedingungspruefung fuer Analyse, Preis, Bestand und Datenqualitaet |
| Ausnahmefreigabe | ReadinessOverride | begruendete, auditierte Uebersteuerung eines konfigurierbaren Blockers |
| Freigabe | Approval | rollen-/optional vier-augen-gepruefter Statusakt; keine Inhaltsmutation |
| Audit-Ereignis | AuditEvent | unveraenderliche fachliche Spur aus Actor, Zeit, Aktion, Grund und Delta |
| Vier-Augen-Prinzip | FourEyesApproval | Pruefer ist nicht identisch mit Ersteller/letztem fachlichem Bearbeiter |

## 6. Plan, Ausfuehrung und Controlling

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Fuetterungsplan | FeedingPlan | Lebenszyklus-Kopf fuer ausfuehrbare, aus Rationen abgeleitete Planversionen |
| Planversion | FeedingPlanVersion | unveraenderliche, freigegebene Mengen-/Gueltigkeitsbasis fuer die Ausfuehrung |
| Mischanweisung | MixingInstruction | geordnete Komponenten, Gesamtmengen, Teilmischungen, Dosier-/Rundungsregeln |
| Sollmenge | TargetAmount | aus Planversion abgeleitete Menge mit Einheit und Bezug |
| Ist-Fuetterung | ActualFeeding | tatsaechlicher Ausfuehrungsdatensatz mit Quelle und Planversionsreferenz |
| Restfutter | RefusalFeed | nicht aufgenommene/vorgelegte Restmenge mit Zeitpunkt und Bezug |
| Mischgenauigkeit | MixingAccuracy | Abweichung Ist zu Soll je Komponente/Fuetterung; Schwelle ist klassenspezifisch |
| Leistungsdatensatz | PerformanceRecord | Milch-, Tier-, Gesundheits- oder Effizienzwert fuer Gruppe und Zeitraum |
| IOFC | IncomeOverFeedCost | Erloes abzueglich Futterkosten; nur bei belastbarem Milch-/Produktpreis |
| ECM | EnergyCorrectedMilk | energiekorrigierte Milch nach versionierter, getesteter Berechnungsregel |
| Versionsmarker | RationChangeMarker | zeitliche Markierung des Wirksamkeitswechsels in Trend/Analyse |

## 7. Beratung, Integration und KI

| Deutscher Begriff | Codebegriff | Definition / Abgrenzung |
|---|---|---|
| Beratungsfall | ConsultingCase | zeitlich/inhaltlich begrenzter Vorgang eines Betriebs mit Beteiligten und Ziel |
| Beobachtung | Observation | dokumentierter Befund, optional mit DMS-Foto/Datei |
| Empfehlung | Recommendation | begruendeter fachlicher Vorschlag; keine automatische Mutation |
| Massnahme | Measure | verantwortete, faellige, status- und wirksamkeitsgepruefte Aktion |
| Wiedervorlage | FollowUp | geplanter Pruefzeitpunkt einer Massnahme/eines Falls |
| Importauftrag | ImportJob | idempotenter Lebenszyklus eines externen Datenimports |
| Quarantaene | IntegrationQuarantine | sichtbarer Zustand fuer ungueltige/unklare Daten ohne Produktivuebernahme |
| Mapping | IntegrationMapping | versionierte Zuordnung externer zu kanonischer Identitaet/Einheit |
| Connector | Connector | vertraglich konfigurierter technischer Adapter; nicht nur ein UI-Schalter |
| Agentenvorschlag | AgentSuggestion | erklaerbarer, quellengebundener Vorschlag mit Confidence und Human-in-the-loop |
| Human-in-the-loop | HumanApprovalBoundary | Grenze, an der ein berechtigter Mensch prueft und entscheidet |

## 8. Verbotene oder missverstaendliche Verwendung

- `Farm` nicht als Synonym fuer Tenant verwenden.
- `aktiv` nicht fuer einen bloss gespeicherten Entwurf verwenden.
- `Analyse` nicht fuer unmarkierte Datenbankdurchschnittswerte verwenden.
- `Freigabe` nicht als Buttontext fuer Speichern oder Optimieren verwenden.
- `Ist` nicht fuer berechnete oder imputierte Werte verwenden.
- `KI-Empfehlung` nicht als fachlich gepruefte Empfehlung darstellen.
- `API vorhanden` nicht aus einer oeffentlichen Produktbeschreibung ableiten.
- `Ration` nicht als maschinell ausfuehrbaren Plan behandeln, solange keine
  Planversion mit Skalierung, Gueltigkeit und Freigabe existiert.

## 9. Pflege

Neue Begriffe werden in demselben Slice eingetragen, der Code/API/Maske einfuehrt.
Umbenennungen brauchen Migrations-/Aliasstrategie. Siehe `reference-maintenance.md`.
