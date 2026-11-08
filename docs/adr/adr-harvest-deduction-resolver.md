---
title: ADR Ernte-Abrechnungsregel als vertrauenswuerdige Resolverabhaengigkeit
type: decision
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-15
---

# Explizite Ernte-Abrechnungsregeln statt impliziter Freigrenze

**Status:** Proposed

**Datum:** 2026-10-15

## Kontext

Die bisherige Ernte-Kalkulation verwendete ohne Vertragsaufloesung zwei Prozent freien Besatz. Qualitaetsgrenze und echte Freigrenze sind unterschiedliche Vertragsmerkmale. Der Studio-Prozessnachweis benutzte denselben impliziten Wert und benoetigt stattdessen deklarierte synthetische Bedingungen.

## Entscheidung

HarvestDeductionRuleV1 definiert den internen, streng validierten Snapshot fuer eine vertrauenswuerdige Serverquelle. Keine Anfrage darf eine Genehmigung oder Regelquelle mitbringen. Der Service prueft Bereich und Gueltigkeit vor Berechnung beziehungsweise finanzieller Freigabe. Ohne eingerichtete Quelle wird abgewiesen. Die bestehende isolierte grain.v1-Probe injiziert ausdruecklich synthetische versionierte Daten in denselben Domain-Service.

## Konsequenzen

Der Produktivrouter verwendet den autoritativen HarvestRuleStore. Ohne dessen vollstaendige Nachweise bleibt die Ernte-Abrechnung beziehungsweise neue finale Gutschrift gesperrt. Nichtfinanzielle Annahme bleibt getrennt. Die technischen Simulationen verwenden denselben persistenten Domain-Weg mit deklarierten synthetischen Testbedingungen. Kein alternativer ERP-Rechtepfad, kein neuer Container und keine weitere Datenbank.

Unveraenderlichkeit im Speicher und ein Inhaltshash allein sind keine persistente revisionssichere Genehmigung. Der implementierte append-only Speicher ergaenzt Datenbankschutz, getrennte menschliche Freigabe, Untersuchungsprovenienz und eine unveraenderliche Bindung der Berechnung an ihre Eingaben. [Standard](../architecture/harvest-deduction-contract-standard.md), [urspruengliche Sicherheitsgrenze](../quality-assurance/harvest-explicit-rule-20261015.md) und [aktueller Abnahmestand](../quality-assurance/harvest-rule-store-20261015.md).
