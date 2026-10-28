---
title: Studio Audit und Vorlage – Handoff
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Funktionale Abnahme, gepruefte Lieferquellen und verbleibende Runtime-Familien.
---

# Handoff

Kontraktprotokoll und CRM-Kampagnenvorlage abgenommen; siehe
[QA](../../quality-assurance/studio-audit-template-20261028.md).58gezielteFaelle,
Typpruefung/Build und12synthetischeBrowseransichten gruen.49 Runtimepunkte verbleiben.
Keine neue DB/Container; eigene SQL-Zeilen zurueckgerollt; Pruefstand SharedHead,
0Sessions. Eigene Vorschau3011 beendet, Einstiegdateien entfernt.

Akzeptierte Lieferquelle ausschliesslich artifacts/migration-repair-source.
Root ist stale/fremd und enthaelt zusaetzlich versehentliche Edits des Vorlagenagenten
an denselben fuenf Vorlagenpfaden; nicht blind aus HEAD wiederherstellen.
Keine persoenlichen Kennungen, E-Mails, Tokens oder lokalen .env-Dateien liefern.
Commit/Push ausschliesslich via exakter Manifest-/Private-Index-Strecke auf den
bestehenden codex/migration-parity-repair-20261022 Integrationszweig.

Naechste Familien bleiben dieselben urspruenglichen49 Runtime-Punkte. Andere
CRM-Details ignorieren noch IDs und brauchen vollstaendige Felder/Aktionen,
Prozessraeume brauchen echte instanzgebundene Primitive; keine pauschale Umbenennung.
resource.v1 ist eine eng begrenzte Human-REST-Kompatibilitaet, kein Domaincommand
und keine MCP-Schreibfreigabe. Untrusted Studioentwuerfe duerfen sie nicht aktivieren.
