---
title: DMS / Compliance Domain Pack
type: explanation
audience: [entwickler, architect]
owner: domain/dms-compliance
status: aktiv
last_reviewed: 2026-08-21
version: 1.1.0
---

# DMS / Compliance — Domain Pack

Paperless-ngx, Archiv, VVVO, PCN, Artikel-Sperren, Regulatory.

Der native Dokumentenruecklauf `docflow/dokumenten-ruecklauf` verbindet
Docflow-Headers, versionierte Artefakte, Versandstatus, erwarteten Ruecklauf,
Verantwortlichkeit und Ursprungsbeleg in einer serverseitigen Worklist.

Mailanlagen werden im nativen `crm/mail-arbeitsplatz` mit SHA-256 und
Uebernahmestatus nachgewiesen. Die DMS-Referenz wird erst nach einer
begruendeten Uebernahme gesetzt; produktiver Virenscan bleibt externes Gate.

## Navigation

| Thema | Datei |
|---|---|
| API | [api.md](api.md) |
| Workflows | [workflows.md](workflows.md) |
| Tests | [tests.md](tests.md) |
| Entscheidungen | [decisions.md](decisions.md) |

## L3 Deep-Mask-Paritaet

`auswertungen/dms-volltext` durchsucht lokale Dokumentreferenzen tenantgebunden
und bietet eine externe Vorschau nur bei konfiguriertem DMS. Die getrennten
Masken fuer Terrorschutz Personal und Kunden schreiben Scope, Objektbezug,
Benutzer und Zeitpunkt in ein tenantgebundenes Pruefprotokoll.

## Sichten

- [C4 DMS/Compliance](../../views/components/c4-dms-compliance.md)
- [dms-paperless-integration.md](../../dms-paperless-integration.md)
