# ADR-025 Standard für konfliktarme Parallelbearbeitung in Kernprozessen

**Status:** Accepted  
**Date:** 2026-03-11

## Context
Kernprozesse in ERP-Systemen werden parallel von mehreren Rollen, Standorten und Systemen bearbeitet. Ohne Standard für konfliktarme Parallelbearbeitung entstehen stille Überschreibungen, unklare Konflikte und inkonsistente Prozesszustände.

## Decision
VALEO NeuroERP führt einen verbindlichen Standard für konfliktarme Parallelbearbeitung ein.

Verbindliche Grundsätze:
1. Änderungsrelevante Kernobjekte werden grundsätzlich als konfliktfähig betrachtet.
2. Optimistic Locking ist der Standard, sofern kein begründeter Sonderfall vorliegt.
3. Konflikte werden explizit angezeigt und nicht stillschweigend überschrieben.
4. Konfliktauflösung, Re-Read und Retry werden als definierte UX- und Prozesspfade behandelt.
5. Workflow-, Policy- und Freigabelogik müssen Konfliktsituationen berücksichtigen.
6. Audit und Telemetrie müssen Konflikte, Auflösungen und verlorene Updates nachvollziehbar machen.

## Consequences
Positiv:
- Weniger stille Datenverluste
- Bessere Beherrschung paralleler Arbeit in Kernprozessen
- Einheitlicherer UX-Standard für Konfliktfälle

Negativ:
- Mehr Implementierungsaufwand für Objekt- und UI-Pfade
- Höhere Anforderungen an API- und Query-Verträge
- Bestehende implizite Updatepfade müssen angepasst werden

## References
- [ADR-006 Read-Model / Query-Contract-Prinzip](adr-006-read-model-query-contract-prinzip.md)
- [ADR-010 Policy-Override-Modell](adr-010-policy-override-modell.md)
