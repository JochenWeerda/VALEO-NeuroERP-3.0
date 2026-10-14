---
title: Studio-Governance und Revisionshistorie
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Studio-Governance — Impact Note

Die bestehende Studio-API und der bestehende Draft-Speicher im Backend bleiben fuehrend. Die additive Tabelle domain_shared.screen_definition_history haelt jeden neuen Inhalts-/Statusstand in derselben Transaktion fest. Kein Container, Dienst oder konkurrierendes Vorschlagsregister entsteht; C4-Grenzen bleiben unveraendert.

Freigabe setzt verifizierte menschliche Adminidentitaet, getrennten Editor, eingereichten Reviewstatus, Inhaltskatalog und erwartete Revision voraus. AI-Proposer koennen durch Metadaten keine Sicherheitsregeln oder produktiven Code aendern. MCP-Schreibadapter bleiben gemaess MCP-WRITE-014 deaktiviert, solange Capability-/Rollenabnahme fehlt.

Die Historie bewahrt Snapshot und Subject ohne erfundene lokale Benutzer-/E-Mail-Zuordnung. PostgreSQL blockiert nachtraegliche Zeilenmutation sowie TRUNCATE. Keine Kaskade entfernt Historie mit dem Draft. Historienabfragen sind paginiert und mandantengebunden. Bestehende Stande vor der Migration werden nicht nachtraeglich zu einer Freigabehistorie umgedeutet.

Migration und Nachweise: [Studio-Revisionshistorie](../../../quality-assurance/studio-revision-history-20261014.md). Idempotenz, Agenten-/Korrelationsattribute, maskenseitige Historie und fachliche Prozessvariantensimulation sind nachfolgende Integrationen. Die vollstaendige Engine-Abnahme ist dadurch noch nicht erreicht.
