---
title: Platform — Identitaet und Agentensteuerung
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-12
description: Gemeinsame Identitaetsgrenze im bestehenden Backend, Keycloak und Redis.
---

# Platform: Identitaetsintegration

Die bestehenden Container Backend, Keycloak und Redis tragen die gemeinsame
Identitaetsgrenze. Es entsteht kein zusaetzlicher Identitaetsdienst.

Die HTTP- und Streamgrenze bindet Provider, ERP-Mandant, Sitzung und internen
Ausfuehrungskontext. Fachliche Rollen verbleiben an ihren jeweiligen Bereichen.
Ein angemeldeter Agent erhaelt dadurch keine pauschalen Fachrechte.

[API und Sitzungsabnahme](api.md),
[ADR-083](../../../adr/adr-083-shared-session-and-agent-boundary.md) und
[operativer Identitaetsentwurf](../../security/central-identity-agent-management-proposal.md)
benennen Entscheidung und Liefergrenzen. Gesamtlieferstatus:
[Process Kernel STATUS](../../process-kernel/STATUS.md).
