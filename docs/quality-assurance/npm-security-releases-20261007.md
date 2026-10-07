---
title: NPM-Herstellerfixes und fortlaufende Behavior-Pruefung
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# Herstellerfixes fuer Produktionsabhaengigkeiten

Der neue Production-Audit des Ausgangs-Lockfiles fand zwei High-, 14 Moderate-
und einen Low-Befund, keine Critical-Meldung. Zwoelf echte Herstellerfix-Pins
in `package.json` und der daraus auf committed Workspace-Manifesten erzeugte
Lockfile reduzieren dies auf zwei High, null Moderate, null Low, null Critical.
Das ist der Node-Production-Audit, keine Sicherheitsfreigabe des gesamten Repos.

| Paket | Gelieferte Version | Reparierter Vertrag |
|---|---|---|
| `@fastify/busboy` | 3.2.2 | Bare CR/LF nicht als Upload-Metadaten weitergeben |
| `joi` | 17.13.8 | `__proto__` nicht als Meldungscode kompilieren |
| `fast-copy` | 3.1.0 | Tiefenbegrenzung statt unkontrollierter Stackerschoepfung |
| `i18next-http-backend` | 4.0.2 | URL-Schema-/Namespace-Injection vor dem Request ablehnen |
| OpenTelemetry: pg | 0.73.0 | Datenbankbenutzer nicht ungefragt exportieren |
| OpenTelemetry: mysql, mysql2, mongoose | 0.67.0 | Derselbe Telemetrie-Vertrag |
| OpenTelemetry: knex | 0.65.0 | Derselbe Telemetrie-Vertrag |
| OpenTelemetry: oracledb | 0.46.0 | Derselbe Telemetrie-Vertrag |
| OpenTelemetry: tedious | 0.40.0 | Derselbe Telemetrie-Vertrag |
| OpenTelemetry: cassandra-driver | 0.66.0 | Derselbe Telemetrie-Vertrag |

Quellen sind die offiziellen npm-Registry-Metadaten und Hersteller-Advisories:
[Busboy](https://github.com/advisories/GHSA-gxm5-99cw-xjw9),
[Joi](https://github.com/advisories/GHSA-wr44-6hxh-3jwq),
[Fast-Copy](https://github.com/advisories/GHSA-jggr-w7fw-pc2j),
[i18next](https://github.com/advisories/GHSA-xvq9-wjp8-hwqf) und
[OpenTelemetry](https://github.com/advisories/GHSA-qqmp-wf37-98f9).
Die Engine-/Peer-Vertraege sind mit dem vorhandenen Node-20-CI und
`@opentelemetry/api` 1.9.0 kompatibel. Der Frontend-Sprachloader verwendet
bereits gebuendelte Sprachdateien; der HTTP-Backend-Pin entfernt trotzdem die
verwundbare ausgelieferte Abhaengigkeit. Keine handgefertigten Lockfileeintraege.

## Fortlaufende Abnahme

`scripts/verify_node_security_releases.cjs` laeuft im bestehenden
Security-Workflow nach `pnpm install --frozen-lockfile`, vor dem unveraenderten
Production-Audit. Sechs reale Behavior-Vertraege, alle lokal gruen:

- Fast-Copy: Zyklen und normale Datensaetze erhalten; beide Kopierer begrenzen Tiefe.
- i18next: drei boesartige Sprach-/Namespace-Werte erzeugen keinen Request;
  ein normaler Leseaufruf funktioniert.
- Busboy: manipulierte CR/LF-Metadaten gelangen nicht in die Anwendung;
  ein normaler Datei-Upload liefert Feld- und Dateinamen.
- Joi: Proto-Meldungscodes werden abgelehnt, normale strikte Validierung bleibt erhalten.
- PostgreSQL-Telemetrie: Benutzer/Passwort fehlen im erzeugten Span,
  stabile Datenbank-/Serverattribute und Query bleiben lesbar.
- Alle acht Instrumentierungspakete behalten ihre oeffentlichen Konstruktoren.

Die Pruefung verwendet standardmaessig pnpm hidden-hoist; die globalen Overrides
geben den betroffenen Paketen jeweils genau eine reparierte Aufloesung.
`SECURITY_NODE_RUNTIME` kann auf einen expliziten eigenen Pruefruntime-Pfad
zeigen. Lokal wurden die echten zwoelf Herstellerpakete mit 45 Abhaengigkeiten
in einem kleinen eigenen Artefakt installiert; fremde `node_modules` blieben
unveraendert. Keine HTTP-/DB-Verbindung aus den Behavior-Tests.

Der Lockfile wurde auf 36 committed Workspace-Manifesten erzeugt und mit
`--frozen-lockfile --lockfile-only --ignore-scripts --offline` erfolgreich
geprueft. Vorbestehende Peer-Warnungen fuer Typedoc/TypeScript,
Storybook-Test und React/React-DOM im Mobile-Paket bleiben eigene Restbefunde.
Kein kompletter Workspace-Neubuild mit den neuen Paketen lokal; dieser Nachweis
bleibt im bestehenden CI. Keine neue Datenbank, Dockerinstanz oder Imagekopie.

## Offen: zwei High-Befunde

Im [Security-CI auf 79a0ed571](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37647442109)
bestanden frozen Installation und alle sechs neuen Behavior-Vertraege. Node-Audit
scheitert ausschliesslich an den zwei folgenden High-Befunden; Linux-Imagebau,
Grype, Trivy, ZAP und Bandit sind gruen. Der Gesamtstatus wird weiterhin rot
ausgewiesen. Damit ist auch die pnpm-Aufloesung im echten CI belegt.

[node-forge](https://github.com/advisories/GHSA-86w9-cpqp-85rv) bis 1.4.0 und
[braces](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) bis 3.0.3 haben
laut aktuell abgefragtem Advisory keinen Herstellerfix. Die zwei High-Befunde
bleiben sichtbar und der Audit-Schwellwert bleibt `high`. Keine neue Ausnahme,
kein falscher Versionspin. Erforderlich bleiben ein echter Herstellerfix oder
ein gepruefter Rueckbau/Ersatz ihrer Verbraucher sowie die frische CI-Abnahme.
