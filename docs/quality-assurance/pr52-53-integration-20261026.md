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

## PR53 nach PR52

PR52 ist auf GitHub als MERGED bestaetigt (Quellmerge3dbaee930). PR53 danach auf codex/migration-parity-repair-20261022 umgestellt; gh-CLI-Projektabfrage scheiterte am abgeschalteten Classic-Projects-Feld, dieselbe eng begrenzte Basisumstellung per REST erfolgreich. Quelle8466bc34790980df801f74189da9291b1fe008db uebernommen, keine Inhaltskonflikte. Migrationsinventar wiederum aus aktuellemQuellenstand erzeugt.

Zusaetzlicher Sicherheitsfix: Bei zu ersetzenden Kompatibilitaetstabellen werden alle vorhandenen Kandidaten in fester Reihenfolge ACCESS EXCLUSIVE gesperrt, danach Form erneut gelesen und erst dann Leerheit geprueft. So kann kein Service-Schreiber zwischen Leerheitspruefung und DROP neue Zeilen verlieren. Der normale bereits-UUID-Pfad bleibt lockfreierNo-op. SQL-Kopien der vier Tabellen bleiben AST-identisch zur Dienstbasis.

EigeneAbnahme:21/21 Unitvertraege (14Versionstabellen,2Schemaparitaet,5Konversionsguards). Kein eigener echter parallelerDML-/Migrationslauf behauptet. VorhandeneZeilen stoppen vorDrop; fehlendeTabellen werden ohneLockversuch angelegt; nachLockwartung bereitskonvertierteForm bleibt unberuehrt. Kein Datenbankupgrade, keine Anwendung auf valeo_probe oderEntwicklungsdatenbank, keinReset/Container. Die Lieferungen sind Integrationsmeilensteine, keine Gesamtfreigabe.
