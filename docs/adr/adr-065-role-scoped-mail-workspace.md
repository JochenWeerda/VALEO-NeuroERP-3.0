---
title: ADR-065 Rollenbasierter ERP-Mailarbeitsplatz
type: adr
audience: [architektur, entwickler, product, qa]
owner: domain/crm
status: proposed
last_reviewed: 2026-08-21
version: 1.0.0
---

# ADR-065 Rollenbasierter ERP-Mailarbeitsplatz

**Status:** Proposed

**Datum:** 2026-08-21

## Kontext

IMAP-Ingest und CRM-Kommunikationsaktivitaeten waren vorhanden, aber nicht als
geschlossener Rollenpostfach-Ablauf mit Beleg, Kontakt, Anlage und Versand.

## Entscheidung

- Der bestehende IMAP-Ingest spiegelt jede Mail Message-ID-idempotent in den
  tenantgebundenen Rollenarbeitsplatz; CRM-Auto-Capture bleibt erhalten.
- Rollen werden serverseitig gefiltert. Kontakt-/Belegzuordnung, Entwurf,
  Provider-Queue und Anlagenuebernahme verlangen Auditgruende.
- Anlagen werden mit Groesse, MIME-Typ und SHA-256 gespeichert; die
  DMS-Uebernahme besitzt einen expliziten Status und Dokumentverweis.
- Ausgehende Mails enden repo-seitig in einer nachvollziehbaren Provider-Outbox;
  erst der externe SMTP-/Graph-Adapter bestaetigt die reale Zustellung.
- `crm/mail-arbeitsplatz` ist eine native Meridian-Worklist.

## Konsequenzen

`L3-GAP-MAIL-010` ist repo-seitig geschlossen. Produktive Zustellung,
Virenscan und Providerquittung bleiben externe Gates.
