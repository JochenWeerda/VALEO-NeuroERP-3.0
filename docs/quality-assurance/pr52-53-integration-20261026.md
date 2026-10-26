---
title: Geordnete Integration PR52 und PR53
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-26
---

# Eigene Dienst-Versionstabellen und Inventory-Fuehrung

PR52 zuerst: exakter Quellstand5b14636e361f34e0e7c9ad9bf579237566612737, gemeinsameBasis9e7d33a03. Inhaltsabgleich ohne Konflikte mit laufenderStudio-/Inbox-Arbeit; Workboard vereint Claude-Fassung und unveraenderten eigenenAnhang. Root-Migrationsinventar aus aktuellenQuellen neu erzeugt, keine aeltere Arbeitskopie uebernommen.

EigeneAbnahme: tests/test_service_alembic_version_tables.py14/14 bestanden, keineSkips, ohneDatenbankzugriff. Autor berichtet erfolgreicheDocsBuild-/Governance-Laeufe, die direkt am exakten PR-Head nachgesehen wurden. Keine eigene neue Gesamt-CI- oder Live-Service-Abnahme behauptet. Kein Datenbankupgrade, keine Anwendung auf valeo_probe, kein Reset oderContainer.

Die Ausnahmen fuer crm-ai/-consent/-gdpr/-marketing bleiben exakt die vier bereits benanntenDienste; Nutzerprioritaet ist deren nachgelagerter Nachlauf durchClaude. Kein RLS-Beginn. Pruefstandsrevision loading_stop_fk_20261023 ist im aktuellenIntegrationszweig vorhanden, die Governancekette setzt darauf auf; alte gegenteiligeHandshakeaussage ist hiermit abgegrenzt.

PR53 wird anschliessend integriert; zu diesem ersten Meilenstein ist dessenUebernahme noch nicht behauptet. Gegen leerheitsgepruefte Kompatibilitaetstabellen ist vor einem Drop ein transaktionaler Schreibschutz erforderlich, damit paralleleDML nicht zwischen Pruefung und Drop Daten einfuegen kann. Dieser Reviewnachlauf erhaelt eigene negativeVertraege.
