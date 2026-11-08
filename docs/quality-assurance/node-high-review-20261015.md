---
title: Evidenzgebundene Node-Sicherheitsreview 15.10.2026
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-15
version: 1.0.0
---

# Wiedervorlage der beiden Node-Quellreparaturen

Der aktuelle Security-/Service-Security-Nachlauf scheiterte an der am 15.10. abgelaufenen Review. Die bestehenden Gates sperrten korrekt. Geprueft wurden ausschliesslich die bereits vorhandenen eigenen Backports; kein Gate, Workflow, Severity-Limit, Paket, Patch oder gemeinsamer Installationsbaum wurde geaendert.

## Aktuelle primaere Quellen

Die offiziellen npm-Registry-Datensaetze nennen weiterhin node-forge 1.4.0 und braces 3.0.3 als latest. Beide aktuellen GitHub-Advisories fuehren weiterhin keinen gepatchten Release: [RSA DigestAlgorithm](https://github.com/advisories/GHSA-86w9-cpqp-85rv), [Braces Stack-Erschoepfung](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm). Die vorhandene RSA-Quellreparatur stammt aus [Upstream-PR 1152](https://github.com/digitalbazaar/forge/pull/1152); die Braces-Provenienz und Grenzen bleiben im urspruenglichen [Abnahmebericht](node-high-backports-20261008.md) dokumentiert.

## Erneute Abnahme

- Beide Originalarchive erneut vom offiziellen npm-Register geladen; SHA512 gegen Registry und bestehende Reviewintegritaet identisch. Alle 59 node-forge- und zehn Braces-Dateien der Originalgegenprobe stimmen bytegenau mit den Archiven ueberein.
- Originalgegenprobe: drei regulaere Faelle bestehen, neun Angriffstests scheitern erwartungsgemaess. Reparierte regulaere Installation: 51 Sicherheitsvertraege bestanden, keine Skips. Darin enthalten sind die 15 fail-closed Auditkontrolltests.
- Alle 36 committed Workspace-Manifeste im bestehenden isolierten Pfad frozen/offline geprueft; Lockfile byteidentisch. Keine neue Datenbank oder Dockerinstanz.
- Frischer unveraenderter Produktionsaudit: 2053 Abhaengigkeiten, null critical/moderate/low, zwei high; Exit 1 bleibt im Rohbericht erhalten.
- Echte Audit-CLI inklusive zwoelf weiterer Laufzeitvertraege: zwei source_backported, null blocked. Patch-, Manifest-, Lock- und alle installierten Quellhashes stimmen mit den bisherigen Nachweisen ueberein.

Erst nach dieser Abnahme wurden ausschliesslich reviewed_on auf 2026-10-15 und review_by auf 2026-10-22 gesetzt. Alle anderen Reviewwerte blieben identisch. Neue Befunde, andere Versionen, Quellen-/Hashdrift oder erneuter Ablauf sperren unveraendert. Versionsbasierte Dependabot-Meldungen werden nicht als geschlossen ausgegeben. Neue Herstellerreleases sind bei der naechsten Wiedervorlage erneut zu pruefen; Herstellerfix hat Vorrang.

Lokale Nachweise unter artifacts/: high-review-registry-20261015.json, high-review-original-20261015.txt, high-review-runtime-20261015.txt, high-review-frozen-20261015.txt, high-review-audit-20261015.json, high-review-audit-exit-20261015.txt und high-review-decision-20261015.json. Rohberichte bleiben unveraendert; die Quellenbewertung ist getrennt. Neue GitHub-Abnahme nach Push steht aus. Die weiteren Vollsuite-Befunde und fremden CI-Korrekturen werden hier nicht als abgeschlossen behauptet.
