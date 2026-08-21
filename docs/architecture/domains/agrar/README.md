---
title: Agrar Domain Pack
type: explanation
audience: [entwickler, architect]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Agrar — Domain Pack

Ernteannahme, Kontrakte, Trocknung, Selbstabrechnung, Materialfluss, Futtermittel.

Der native Produktionsleitstand projiziert Mischfutterauftraege und allgemeine
Muehlen-/Umbuchungs-/Stapel-/Nachbearbeitungsvorgaenge, ohne Bestands-, Chargen-
oder FIBU-Logik zu duplizieren.

## Navigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## Sichten

- [C4 Component Agrar](../../views/components/c4-agrar.md)
- [agrar-event-hook-contracts.md](../../agrar-event-hook-contracts.md)
- Index: `domains.agrar`

## UIX / Universal Mask Generator

Agrar bleibt fuer Spezialmasken bewusst differenziert. Waage-, Ernteannahme-,
Silo- und Operator-UIs duerfen Spezialrenderer behalten, muessen aber kuenftig
ScreenDefinition-kompatible Daten-, Action- und Workflow-Vertraege anbieten.
Eine Migration erfolgt erst nach CRM-Pilot und nur ueber Adapter-Paritaet.
