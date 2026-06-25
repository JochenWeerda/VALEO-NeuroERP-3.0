---
title: RBAC & Rollen
type: how-to
audience: [tenant-admin, security]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# RBAC & Rollen

Zugriffe werden rollenbasiert (RBAC) und mandantenisoliert gesteuert.
Authentifizierung erfolgt über OIDC-Bearer-Token; Autorisierung über Rollen und
Scopes.

## Grundprinzipien

- **Authentifizierung:** Bearer-Token (OIDC) wird in der Middleware erzwungen.
- **Mandant:** Aus `X-Tenant-ID`/Token-Claim; jeder Zugriff bleibt im Mandanten.
- **Autorisierung:** Rollen bündeln Berechtigungen/Scopes (z. B. `sales:write`).
- **Least Privilege:** Nutzer:innen erhalten nur die benötigten Rollen.

## Rollen zuweisen

1. Bereich *Administration* → *Benutzer & Rollen*.
2. Nutzer:in auswählen.
3. Rollen hinzufügen/entfernen.
4. Speichern; Änderung greift bei nächster Anmeldung/Token-Erneuerung.

## Scopes & MCP-Tools

KI-Agents/MCP-Tools arbeiten mit denselben Scopes (z. B. `crm:read`,
`finance:read`). Risikoreiche Tools erfordern zusätzlich Human-Approval — siehe
[Guardrails](../agent-docs/guardrails.md).

## Häufige Fehler

- **403 trotz Login:** Rolle/Scope fehlt für die Aktion.
- **Mandantenübergreifender Zugriff erwartet:** nicht möglich — bewusste
  Isolation.
