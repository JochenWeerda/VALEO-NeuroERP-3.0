---
title: arc42 — 11. Risiken und technische Schulden
type: explanation
audience: [entwickler, product]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 11. Risiken und technische Schulden

Aggregiert aus [Open Gaps & Known Issues](../../project-context/open-gaps-and-known-issues.md):

| Risiko | Auswirkung | Mitigation |
|---|---|---|
| Externe Gates (ERiC, TSE-Produktiv) | Compliance-Freigabe verzögert | Simulation + klare Gate-Dokumentation |
| Hybrid-Architektur (Monolith + CRM-MS) | Komplexität Betrieb/Onboarding | C4 Container, Container-Inventar |
| Schattenmodelle / Legacy L3 | Dateninkonsistenz | Canonical Model ([ADR-003](../../adr/adr-003-canonical-domain-model.md)) |
| Doku-Drift bei hohem Tempo | Falsche Agent-/Dev-Entscheidungen | Docs-as-Code, Generatoren, arc42-Hubs |
| AsyncAPI fehlt noch | Event-Verträge schwer auffindbar | DOC-INTERFACES-001, Koppelung an C4 |

[← Kapitel 10](10-qualitaet.md) | [Kapitel 12 →](12-glossar.md)
