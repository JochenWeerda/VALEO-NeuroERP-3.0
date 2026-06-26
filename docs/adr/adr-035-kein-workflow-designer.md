---
title: "ADR-035: Kein interaktiver Workflow-Designer"
status: accepted
date: 2026-06-26
deciders: [Jochen Weerda]
---

# ADR-035: Kein interaktiver Workflow-Designer (P2.1 gestrichen)

**Status:** accepted
**Datum:** 2026-06-26

## Kontext

Die YouTube-Gap-Analyse vom 2026-06-23 listete als P2.1 einen visuellen
Workflow-Designer: ein interaktives Canvas zum Modellieren von ERP-Prozessketten
(n8n-ähnlich, mit Drag & Drop, Events, Policies, SLAs).

## Entscheidung

P2.1 wird nicht umgesetzt. VALEO bekommt keinen interaktiven Workflow-Designer.

## Begründung

**1. Fachlich bereits abgedeckt:**
`docs/architecture/process-map.md` dokumentiert alle 6 kritischen Prozessketten
(O2C, P2P, WMS, FIBU, POS, QS) als Mermaid-Diagramme mit Events, Policies und
externen Gates. Das reicht für Entwickler- und Betriebsdokumentation vollständig.

**2. Operativ abgedeckt:**
Der Workflow-Leitstand (`WF-COCKPIT-UI-001`, `VALEO-WF-COCKPIT-001`) liefert die
operative Prozesssicht: laufende Instanzen, Event-Ketten, externe Blocker, Replay.
Das ist der relevante Live-Teil.

**3. Compliance-Risiko:**
VALEO-Kernprozesse (FIBU, QS-Freigabe, Kontrakt-Settlement, POS/TSE) sind durch
Fachregeln, GoBD-Invarianten und Audit-Anforderungen determiniert. Ein
Drag-and-Drop-Umbau dieser Ketten wäre ein Compliance-Risiko, kein Feature.

**4. Aufwand/Nutzen-Verhältnis negativ:**
Ein brauchbarer Workflow-Designer (React Flow o.ä.) ist 3–5 Wochen Entwicklung
für ein Werkzeug, das niemand täglich braucht, weil die Prozessketten stabil sind.

## Konsequenzen

- Prozesskarte (`docs/architecture/process-map.md`) wird bei Prozessänderungen
  manuell gepflegt — das ist der einzige Pflegeaufwand.
- Neue Prozessketten oder Änderungen an bestehenden Ketten erhalten ein
  Mermaid-Diagramm + ADR, kein visuelles Design-Tool.
- Der Workflow-Leitstand bleibt die operative Anlaufstelle für Betrieb und Support.
