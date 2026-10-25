---
title: NPM-Audit: Befunde je installierter Version
type: qa
audience: [entwickler, qa, sicherheit]
status: active
last_reviewed: 2026-10-25
---

# NPM-Audit: Befunde je installierter Version

## Gate-Korrektur

Der unveraenderte CI-Rohbericht `artifacts/ci38-security-audit-8b81/npm-audit-report.json`
enthaelt 11 Advisory-Zeilen, aber 12 installierte Versionsbefunde. Ein Zod-Advisory
nennt sowohl 3.25.76 als auch 4.1.12. `scripts/check_npm_backport_audit.cjs`
gleicht die Schweregrad-Metadaten deshalb mit den einzelnen `findings[]` ab und
entscheidet jede Version separat. Leere, doppelte und pfadlose
Versionsinventare werden abgelehnt. Ein Review fuer eine Version gibt keine
weitere Version desselben Advisorys frei. Die bestehenden Review-Regeln,
Ausnahmen und Paketversionen wurden nicht erweitert.

Der Rohbericht verteilt sich auf 5 High-, 5 Moderate- und 2 Low-Befunde.
Davon ist nur `node-forge@1.4.0` bereits Gegenstand eines gesondert
hashgebundenen Quellpatch-Reviews. Die 11 uebrigen Versionsbefunde bleiben
ohne neue Reparatur und Abnahme blockierend. Eine lokale Bewertung des
Rohberichts zaehlte 11 Advisories/12 Versionsbefunde und blockierte alle 12,
weil in diesem Reparatur-View kein installierter `node_modules`-Baum fuer die
Quellhashpruefung vorhanden ist. Das ist **keine** Aussage ueber die
Node-forge-Pruefung im CI.

## Neue Paketbefunde und Reparaturumfang

| Paket und installierte Version | Versionsbefunde | Herkunft im Rohbericht | Vom Advisory genannte reparierte Version | Naechste Arbeit |
| --- | ---: | --- | --- | --- |
| `zod@3.25.76` und `4.1.12` | 2 High | Viele Workspaces nutzen 3.x; Root nutzt 4.x, `frontend-web` deklariert 3.x und `zod-openapi@0.9.0` verlangt 3.x. | [4.6.6](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) | Die 4.x-Abhaengigkeit gezielt aktualisieren; fuer 3.x zuerst Verbraucher und Peer-Vertraege pruefen und eine getestete Migration planen. |
| `body-parser@1.20.8` | 1 High | `express@4.21.2` in mehreren Workspaces | [1.20.9](https://github.com/advisories/GHSA-27r3-jxmh-p828) oder 2.4.0 | Express-Aufloesung auf den gepatchten 1.x-Zweig heben und Request-Parsing pruefen. |
| `multer@2.4.0` | 1 High | `procurement-domain` | [2.5.0](https://github.com/advisories/GHSA-q7qp-rjg7-q26m) | Gezieltes Update und Upload-/FileFilter-Abnahme. |
| `nodemailer@10.0.12` | 3 Moderate | `notifications-domain` | [10.1.4](https://github.com/advisories/GHSA-8c8m-p3m8-cjg8) | Gezieltes Update; Adressparser-, Empfaenger- und Versandvertraege pruefen. Weitere Advisories: [GHSA-m943-m63m-w62w](https://github.com/advisories/GHSA-m943-m63m-w62w), [GHSA-85x2-q946-cp5h](https://github.com/advisories/GHSA-85x2-q946-cp5h). |
| `fast-uri@3.1.8` | 2 Moderate, 2 Low | `fastify@5.12.7` ueber AJV/Compiler | [3.1.9](https://github.com/advisories/GHSA-w74x-v6f9-j3xg) | Genaues transitive Update und URL-/Schema-Validierung pruefen. Weitere Advisories: [GHSA-xhq7-xmqj-769h](https://github.com/advisories/GHSA-xhq7-xmqj-769h), [GHSA-wjr9-j795-jxcr](https://github.com/advisories/GHSA-wjr9-j795-jxcr), [GHSA-333x-w4r6-6crp](https://github.com/advisories/GHSA-333x-w4r6-6crp). |

Diese Tabelle ist eine Diagnose aus dem CI-Rohbericht und den verlinkten
primaeren Advisorys. Sie ist keine Freigabe fuer Manifest-/Lockfile-Aenderungen
oder neue Backport-Ausnahmen. Nach Paketkorrekturen sind Frozen-Installation,
Roh-Audit, Quellhash- und Laufzeitpruefung erneut erforderlich.

## Abnahme

`node --test scripts/test_npm_backport_audit.cjs`: 19/19 gruen. Die neuen
Vertraege pruefen zwei Versionen in einem Advisory, eine unreviewte Version
neben einer reviewten, falsche Severity-Zaehleinheiten sowie leere, doppelte
und pfadlose Inventare. Keine Datenbank oder Container wurden benutzt.
