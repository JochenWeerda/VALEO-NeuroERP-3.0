---
title: Fuhrpark und MCP Mandantenisolation 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-09
description: Echte SQL-Negativabnahme der Fuhrpark-CRUD-Wege und zentraler MCP-Mandantengrenzen.
---

# FUHRPARK-MCP-ISOLATION-20261009

Cursor lieferte zuvor vier tenant_id-Spalten, Mandantenfilter und fuenf
Fuhrpark-Commands. Die unabhaengige Abnahme reproduzierte danach **21 Fehler**:
frei waehlbare REST-Mandantenheader, falsche Erfolgsvorschauen bei fremden
Datensatz-IDs, fremde Fahrzeugreferenzen in Rechnungen und widerspruechliche
Token-Mandantenaliaswerte.

## Reparatur

- Fuhrpark liest den Mandanten ausschliesslich aus verifizierten OIDC-Claims.
  Ein abweichender Header wird mit 403 abgewiesen; keine Standardmandant-Fallbacks.
- MCP und Fuhrpark verwenden denselben eindeutigen Tenant-Claim-Resolver.
  tenant_id und mandanten_id mit unterschiedlichen Werten werden abgewiesen.
- validate, dryRun, propose und execute pruefen dieselben kanonischen
  Eingabeschemas, Duplikate, Datensatz-IDs und Fremdmandantenreferenzen.
- Rechnungen duerfen nur eigene Fahrzeuge referenzieren, auch bei direktem
  Repository-CRUD. ID, tenant_id, mandanten_id und Auditzeitstempel sind am
  Repository-Rand unveraenderlich.
- Unbekannte Eingabefelder, nicht endliche Zahlen und widerspruechliche ID-Aliase
  werden abgewiesen. MCP nutzt weiterhin Scope-Pruefung und atomaren Audit/Replay.
- Command-Implementierungen und Eingabeschemas sind intern ausgelagert.
  Bestehende Routen und OpenAPI-Schemaidentitaeten bleiben erhalten;
  fuhrpark.py hat 873 Zeilen und benoetigt keine Godfile-Baseline-Ausnahme.

## Nachweise

Original: 21 fehlgeschlagen / 136 bestanden. Nach Reparatur zuerst 408
betroffene Tests bestanden; erweiterte neue Abnahme 237 bestanden.
Der isolierte finale Lieferstand besteht **569 Tests ohne Skip** in 36,98 s.

Neue Tests: tests/test_fuhrpark_isolation_effects.py. **68 echte PostgreSQL-
Wirkungstests** mit den produktiven Repositories und HTTP-/MCP-Commands:
Fremdmandanten-CRUD, alle vier Modi, fremde Fahrzeugreferenzen, geschuetzte
Primaerschluessel, Erfolgswrites, echte Audit-Fehler nach SQL-Write,
vollstaendige Ruecknahme und erfolgreicher idempotenter MCP-Replay.
Dazu 169 zentrale Guard-Tests: alle 56 registrierten MCP-Tools weisen beide
Mandantenoverride-Parameter sowie fremde Header vor SQL ab; widerspruechliche
Token-Aliase werden ebenfalls blockiert.

Der gemeinsame Pruefstand valeo_probe wurde vorab per --status geprueft:
Revision fuhrpark_tenant_ce_20261009. Keine neue Datenbank, kein Container,
kein Reset und keine erneute Migration. Eigene zufaellige Datensatz-/Tenant-IDs
werden in aeusseren Transaktionen isoliert; alle Tests nehmen ihre Daten am Ende
zurueck, auch wenn die produktive Session intern commit/rollback aufruft.

Map/Catalog/Handbuch, OpenAPI und Code-Inventare werden aus dem isolierten
Lieferstand generiert und geprueft. Publiziert wird die bereits auf der Probe
abgenommene Cursor-Fuhrpark-Migration; die fremde uncommittete Versandwege-Head
wird nicht integriert. Fremde OpenAPI-/Inventar-Arbeitsdateien bleiben erhalten.

## Abgrenzung und Betrieb

Die 56 zentralen Guard-Vertraege sind kein echter Datenbank-E2E-Nachweis jedes
Fachhandlers. Vorhandene MCP-Tenant-/Read-/Join-Vertraege wurden mitgeprueft;
neue echte PG-Wirkungsabnahme betrifft die Fuhrpark-Wege. Keine projektweite
Fehlerfreiheit, keine Last-/Konkurrenzabnahme und keine externe OIDC-UAT behauptet.
Die REST-Fuhrpark-Verbraucher benoetigen nun OIDC-Token mit eindeutigem Mandant.
Ein frei waehlbarer Mandantenheader oder Entwicklungstoken ohne Mandantenclaim
ersetzt diesen Vertrag nicht.

FIN-CLOSE gegen ADR-076 und Zahlauf open_high bleiben eigene offene Themen.
Die fuenf frueheren Fuhrpark blocked_missing_tenant-Eintraege sind geschlossen:
41 mapped, 0 blocked_missing_tenant, 0 blocked_no_endpoint, 13 local_ui,
1 open_high; Registry 56. GitHub-Folgeabnahme erfolgt nach Push.
