---
title: ADR-072 Explizite MCP-Ausfuehrungsadapter
type: explanation
audience: [agent, entwickler, architektur]
owner: Codex
status: proposed
last_reviewed: 2026-09-21
description: ERP-Schreibadapter verwenden Fachservices, verifizierte Identitaet und transaktionales Replay.
---

# ADR-072: Explizite MCP-Ausfuehrungsadapter

**Status:** Proposed
**Datum:** 2026-09-21

## Kontext

Der Tool-Katalog ist kein Ausfuehrungsnachweis. Ein freies Weiterleiten beliebiger
Katalog-URLs wuerde Berechtigungen, Fachvalidierungen und nicht implementierte
Handler vermischen.

## Entscheidung

Schreibadapter werden einzeln an vorhandene
Fachservices angeschlossen. Der erste Adapter nutzt den bestehenden OIDC-
Verifier und dessen Scopes; er fuehrt kein neues Authentifizierungsmodell ein.

Identitaet und Mandant stammen aus dem verifizierten Token. Fachdatensatz,
Audit und Replay-Journal liegen in einer Transaktion. Ein bestehender Service-
Commit wird durch eine untergeordnete Session auf einen Savepoint beschraenkt.
Die Replay-Pruefung ist fuer denselben Mandanten, Tool und Schluessel serialisiert.
Client-Freigabe-Flags ersetzen niemals eine serverseitige Human-Approval-Bindung.

## Konsequenzen

Neue Tools benoetigen einen Persistenz-, Berechtigungs- und Negativnachweis.
Der CRM-Kontaktadapter ist kein Nachweis fuer alle Masken und kein vollstaendiger
MCP-Transport. Details: [Vertrag und QA](../quality-assurance/mcp-execution-crm-20260921.md).
