---
title: Shared und Einkauf Integrationsabnahme
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Gezielter Integrationsnachweis mit ausdruecklichen Abnahmegrenzen.
---

# Shared und Einkauf Integrationsabnahme

Claudes Shared-Slice3d31a3145 ist nach Einkauf integriert. Parallele Auditfixes
wurden harmonisiert: Token-Subject aus der Route und optionaler Constructoraktor
sind kompatibel; eindeutige aktive Nutzerzuordnung im Mandanten, gefilterte
Audit-E-Mail und Rollback bleiben erhalten.

114 Tests der Module test_rls_domain_shared.py und test_rls_domain_einkauf.py
bestanden auf dem gemeinsamen valeo_probe, keine Skips (49,02s). Policies wurden
als valeo_app geprueft; Fachketten pruefen separat die Anwendungsfilter. Alle
Migrationen/Testdaten nur in aeusseren zurueckgerollten Transaktionen.
Vorher/nachher loading_stop_fk_20261023, keine fremden Sitzungen. Nachher keine
temporaeren Shared-Branch-Policies. Fenster freigegeben, keine neue DB/Container,
kein Reset, keine Live-Policy. Inventar:635 RLS-Tabellen,86 zurueckgestellt.

Die konfigurierte Keycloak-Exportdefinition enthaelt email und email_verified
mit Tokenmappern und defaultClientScope email. Das ist ein Konfigurationsbeleg,
kein Nachweis eines aktuell ausgestellten persoenlichen Tokens. Keine Zugangsdaten
oder Token gespeichert. Unfertige Reklamations-Runtimeentwuerfe sind ausserhalb
der akzeptierten Quellen erhalten; kein Funktionsmigrationsabschluss behauptet.
