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

## Offene produktive Integration

Der bestehende operative HarvestAcceptanceService verwendet bislang noch den alten Standard der Kalkulator-Freigrenze. Eine mandantengebundene, versionierte Vertragsregelaufloesung fuer diese Angaben ist dort noch nicht implementiert. Diese Luecke darf weder mit frei gelieferten Booleans noch durch Ablage eines angeblichen Vertrags in Labormesswerten geschlossen werden. Die bestehende PriceAdjustmentRule modelliert Preisstaffeln und ersetzt keine geklaerte Mengenfraktionsregel.

Der Nutzer hat fuer die ungeklaerte Konstellation 2026 ausdruecklich keine automatische zusaetzliche Windbelastung vorgegeben; der derzeitige informative Domain-Modus fuehrt keinen solchen Zusatzabzug aus. Alternative Modelle bleiben bis zur fachlich und technisch nachgewiesenen Bindung gesperrt. Der hier beschriebene Sollvertrag ist kein Nachweis einer fertig implementierten produktiven Regelverwaltung.

[Studio-Abnahme](../quality-assurance/studio-semantic-20261015.md), [Fachsprachlicher Architekturstandard](studio-semantic-standard.md).
