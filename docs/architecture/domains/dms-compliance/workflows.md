---
title: DMS / Compliance — Workflows
type: explanation
audience: [entwickler]
owner: domain/dms-compliance
status: aktiv
last_reviewed: 2026-08-21
version: 1.1.0
---

# DMS / Compliance — Workflows

- Dokumentenablage: ERP → `dms-adapter` → Paperless
- VVVO / Sachkunde: `compliance_vvvo_sachkunde_service`
- PCN Lifecycle: `compliance_pcn_lifecycle_service`
- Artikel-Sperre Audit: `compliance_sperre_audit_service`
- Dokumentenruecklauf: Ursprungsbeleg -> Artefakt -> Versandstatus ->
  erwarteter Eingang -> Pruefung -> Abschluss; jeder Statuswechsel mit Grund
  im append-only Ruecklauf-Audit.
