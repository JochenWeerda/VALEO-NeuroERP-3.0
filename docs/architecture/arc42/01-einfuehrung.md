---
title: arc42 — 1. Einführung und Ziele
type: explanation
audience: [entwickler, product, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
description: arc42 Kapitel 1 — Aufgabenstellung, Qualitätsziele, Stakeholder.
---

# 1. Einführung und Ziele

Hub-Seite im [arc42-Template](https://arc42.org/). Verweist auf bestehende Quellen — kein Duplikat.

## Aufgabenstellung

VALEO NeuroERP ist ein **Multi-Mandanten-ERP für Landhandel, Agrargenossenschaften und angrenzende Handels-/Logistikprozesse**.

Kernziele:

- End-to-End-Prozesse ohne Medienbruch (Kontrakt → Annahme → Qualität → Settlement → FiBu)
- GoBD-/DSGVO-konforme Auditierbarkeit
- Agentenfähige Commands und Integrationen
- Mandantenfähige Modulkonfiguration

Quellen: [Zielbild Landhandel ERP](../target-state-landhandel-erp.md), [System Overview](../../project-context/system-overview.md)

## Qualitätsziele

| Ziel | Kennzahl / Nachweis |
|---|---|
| Fachliche Konsistenz | Canonical Domain Model ([ADR-003](../../adr/adr-003-canonical-domain-model.md)) |
| Prozesszuverlässigkeit | Process Kernel, Workflow-/Policy-Layer ([ADR-004](../../adr/adr-004-command-action-layer.md)) |
| Dokumentations-Aktualität | Drift-Report = 0 ([Dokumentationskonzept](../../dokumentation/dokumentationskonzept.md)) |
| Lieferstand | [Process Kernel STATUS](../process-kernel/STATUS.md) |

## Stakeholder

Siehe [Stakeholder & Concerns](../views/stakeholder-concerns.md) und [Dokumentationskonzept §2](../../dokumentation/dokumentationskonzept.md).

## Navigation arc42

| Kapitel | Seite |
|---|---|
| 2 | [Randbedingungen](02-randbedingungen.md) |
| 3 | [Kontext & Scope](03-kontext-scope.md) |
| 4 | [Lösungsstrategie](04-loesungsstrategie.md) |
| 5 | [Bausteinsicht](05-bausteinsicht.md) |
| 6 | [Laufzeitsicht](06-laufzeitsicht.md) |
| 7 | [Verteilungssicht](07-verteilungssicht.md) |
| 8 | [Querschnittliche Konzepte](08-querschnitt.md) |
| 9 | [Entscheidungen](09-entscheidungen.md) |
| 10 | [Qualitätsanforderungen](10-qualitaet.md) |
| 11 | [Risiken](11-risiken.md) |
| 12 | [Glossar](12-glossar.md) |
