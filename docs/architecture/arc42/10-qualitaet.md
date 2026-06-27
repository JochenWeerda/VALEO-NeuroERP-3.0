---
title: arc42 — 10. Qualitätsanforderungen
type: explanation
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 10. Qualitätsanforderungen

Quelle: [Quality & Governance Tooling](../tooling-quality-governance.md), [AI-Dev Standard](../ai-assisted-enterprise-development-standard.md)

| Bereich | Anforderung |
|---|---|
| Tests | pytest-Marker, E2E Playwright, Process-Kernel-Waves mit Testnachweis |
| Doku-Drift | Nightly Drift-Report = 0 kritische Treffer |
| API | OpenAPI generiert; AsyncAPI geplant ([DOC-INTERFACES-001](../../dokumentation/dokumentationskonzept.md)) |
| Mutation UI | Loading-Guards, Toast bei Fehler ([Konventionen](../../entwickler/konventionen.md)) |
| Container-Doku | Generator-Abgleich docker-compose ↔ C4 |

[← Kapitel 9](09-entscheidungen.md) | [Kapitel 11 →](11-risiken.md)
