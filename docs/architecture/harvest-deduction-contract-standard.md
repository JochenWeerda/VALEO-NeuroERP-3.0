---
title: Ernteabrechnung Qualitaetsgrenze Freigrenze und Windabgang
type: reference
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
---

# HARVEST-DEDUCTION-001: Vertragliche Grundlage vor Abrechnung

Fachliche Vorgabe des Nutzers vom 2026-10-15. Das bereitgestellte Recherchepapier ist keine juristische Freigabe konkreter Vertragsbedingungen. Insbesondere werden Folkerts-Bedingungen weder automatisch ausgelegt noch als genehmigtes Regelwerk gespeichert.

## Verbindliche Trennung

| Merkmal | Bedeutung |
| --- | --- |
| quality_limit | Annahme-/Qualitaetsanforderung; keine automatische abzugsfreie Toleranz |
| free_allowance | Ausdruecklich vereinbarter abzugsfreier Anteil; kein impliziter 2-Prozent-Wert |
| measurement_components | Unveraenderte Messwerte mit Fraktionskennung, Untersuchungsmethode und Methodenversion |
| deduction_basis | Vertraglich festgelegte Berechnungsbasis und Rundung |
| overlap_policy | Nachweis, ob Windabgang im Besatz enthalten ist, getrennte Fraktionen vorliegen oder die Abgrenzung ungeklaert bleibt |
| cleaning_charge | Gesonderter Kostenbestandteil mit eigener Grundlage; kein versteckter zweiter Mengenabzug |
| contract_rule_version | Unveraenderliche Regelversion mit Geltungszeit, Inhaltsbindung und Zuordnung zu Vertrag und Mandant |

Eine rechtswirksame Vereinbarung kann die Software nicht aus dem Zahlenwert einer Qualitaetsgrenze ableiten. Unterschiedliche fachlich freigegebene Modelle muessen ausdruecklich unterschieden werden. Messwerte duerfen auch bei ungeklärter Abrechnungswirkung erfasst werden.

Vor verbindlicher Abrechnung muessen vertragliche Regelversion, betroffener Vertrag/Mandant, Geltungszeit, Untersuchungsmethode und Fraktionsabgrenzung zusammenpassen. Ungeklaerte Ueberlappung sperrt einen zusaetzlichen Windabgangsabzug. Dieselbe Fraktion darf nicht unbeabsichtigt zweimal als Mengenverlust eingehen. Kostenpositionen benoetigen eine eigene nachvollziehbare Grundlage und bleiben von Mengenpositionen getrennt.

## Aktuell implementierter Studio-Vertrag

Die manuelle Kalkulationsprobe fordert eine explizite freie Besatzmenge in Prozent. Eine optionale, getrennte Qualitaetsgrenze fuehrt nur zu einer eigenen Bewertung und Warnung; sie veraendert den Mengenabzug nicht. Fehlende Messwerte/Qualitaetsgrenzen bleiben unbekannt.

Windabgang ist im verwendeten bestehenden Domain-Modell ausschliesslich informativ und erzeugt keinen weiteren Abrechnungsabzug. Eine produktive Vertragsfreigabe wird durch diese Vorschau niemals erteilt (settlement_authorized=false). Nicht registrierte alternative Abzugsmodi oder Vertragsgrundlagen werden nicht angenommen. Der bestehende Release-Gate verweigert die Aktivierung dieses Vorschauvertrags.

Regressionsbeispiel: 25.000 kg, Besatz 1,5 Prozent, ausdrueckliche Freigrenze null, Windabgang 0,8 Prozent informativ. Besatzabzug 375 kg, abrechnungsrelevante Menge 24.625 kg vor weiteren vereinbarten Korrekturen. Eine Qualitaetsgrenze von 2 Prozent erteilt keine Freigrenze und keine Vertragsfreigabe. Wird die Qualitaetsgrenze auf 1 Prozent gesenkt, entsteht eine Qualitaetswarnung, kein anderer Abrechnungsbetrag.

## Autoritative Resolvergrenze und kontrollierte Ausfuehrung

Der Domain-Kalkulator hat keinen impliziten 2-Prozent-Standard mehr. Fehlende Freigrenzen werden auch bei fehlendem oder mit null gemessenem Besatz abgewiesen. Der operative HarvestAcceptanceService verlangt eine serverseitige Regelquelle. Der REST-Router bindet dazu den persistenten HarvestRuleStore ein; eine vom Aufrufer behauptete Genehmigung oder Regelquelle ist unzulaessig. Fehlende beziehungsweise ungueltige Nachweise sperren Berechnung und neue finale Gutschrift vor Lagerbewegung, Kontraktverbrauch, Partie und Gutschrift. Bereits gespeicherte Altbetraege koennen die Grenze nicht umgehen. Eine rein nichtfinanzielle Warenannahme bleibt gesondert moeglich.

HarvestDeductionRuleV1 ist ein typisierter, im Arbeitsspeicher unveraenderlicher Eingabevertrag. Er bindet Regelkennung/-version, Mandant, optionalen Kontrakt, Partner, Artikel, Gueltigkeit, Quellenreferenz, Untersuchungsmethode/-version, ausdrueckliche Freigrenze und getrennte Qualitaetsgrenze. Er unterstuetzt vorerst nur den informativen Windmodus und die vorhandene Mengenbasis/Rundung. Fremde Bereiche, ungueltige Zeitraeume, zusaetzliche Felder und nicht unterstuetzte Abzugsmodelle sperren. Der Service validiert auch bereits konstruierte Resolverobjekte erneut.

Der SHA256-Inhaltshash ist eine Inhaltsbindung, keine Signatur oder Genehmigung. Er erhaelt vereinbarte Dezimalstellen ohne Rundung durch den Standard-Dezimalkontext. Die Besatzposition weist Regelkennung, Version und Hash in der Berechnungsformel aus. Gemessene Nullwerte und ausdrueckliche Nullpreise bleiben erhalten; bestehende Besatzbezeichnungen folgen der aktuell angewandten Freigrenze.

Die isolierte grain.v1-Simulation deklariert ihre eigene synthetische Regelversion ausdruecklich: zwei Prozent frei, getrennte Qualitaetsgrenze zwei Prozent, synthetische Untersuchungsmethode. Ihre zufaelligen Mandanten-/Partner-/Artikelkennungen werden in den Snapshot gebunden. Sie verwendet denselben Service und dieselbe Bereichspruefung. Profil, Resolververtrag und Fixture sind im Simulations-Artefakthash enthalten; alte Nachweise werden dadurch ungueltig. Dies ist keine Freigabe realer Vertragsbedingungen.

## Persistenter Versionsspeicher und Freigabebindung

HarvestRuleStore speichert Regelversionen, Genehmigungen, Widerrufe, Messbestaetigungen, Annahmebindungen, Berechnungsnachweise und finanzielle Freigaben ausschliesslich als neue Ereignisse. Datenbanktrigger verhindern UPDATE, DELETE und TRUNCATE der Nachweistabelle. Mandant und handelnde Identitaet werden serverseitig geprueft; Audit und Wiederholungsschutz binden Aussteller und Subjekt der Identitaet. Fachliche Rechte kommen aus den vorhandenen Bereichsrollen.

Eine zweite menschliche Einkaufs- oder Finanzleitung genehmigt die exakte Regelversion. Das aktuelle Messprotokoll wird mit Methode, Methodenfassung, Quelle und Inhalt gebunden. Berechnung und finanzielle Gegenpruefung verwenden denselben autoritativen Resolver. Der unveraenderliche Berechnungsnachweis bindet Quellen, Positionen, Ergebnisse, Rechenimplementierung und Buchungsgrundlagen. Vor Genehmigung und Freigabe erfolgen Inhaltspruefung und erneute wirkungsfreie Berechnung; veraenderte Quellen, Positionen, abgelaufene oder widerrufene Genehmigungen sperren. Eine Qualitaetsausnahme benoetigt eine ausdrueckliche Gegenpruefung. Nachweis und Geschaeftswirkung werden atomar verarbeitet; Wiederholungen erzeugen keine weitere Gutschrift.

Die technische Genehmigungsdauer betraegt hoechstens 24 Stunden fuer die konkrete Berechnung und 366 Tage fuer die Regelversion. Diese Grenzen sind Softwarepolitik, keine gesetzlichen Fristen. Die native Kontrollmaske wird zentral aus ScreenDefinition und UniversalMaskRuntime erzeugt. Die Integration besitzt reale SQL-/HTTP-Vertraege; die finanzielle Browserabnahme und der Liefer-/CI-Nachlauf sind im [aktuellen QA-Stand](../quality-assurance/harvest-rule-store-20261015.md) gesondert ausgewiesen. Ein Hash in frei editierbarem Formeltext ist niemals ein Freigabenachweis.

Diese Luecke darf weder mit frei gelieferten Booleans noch durch Ablage eines angeblichen Vertrags in Labormesswerten geschlossen werden. Die bestehende PriceAdjustmentRule modelliert Preisstaffeln und ersetzt keine geklaerte Mengenfraktionsregel.

Der Nutzer hat fuer die ungeklaerte Konstellation 2026 ausdruecklich keine automatische zusaetzliche Windbelastung vorgegeben. Der informative Domain-Modus fuehrt keinen solchen Zusatzabzug aus. Alternative Modelle bleiben bis zur fachlich und technisch nachgewiesenen Bindung gesperrt.

[Studio-Abnahme](../quality-assurance/studio-semantic-20261015.md), [Resolver-Abnahme](../quality-assurance/harvest-explicit-rule-20261015.md), [Fachsprachlicher Architekturstandard](studio-semantic-standard.md).
