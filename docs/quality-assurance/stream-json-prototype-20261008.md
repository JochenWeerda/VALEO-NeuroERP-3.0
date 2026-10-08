---
title: stream-json Prototype-Schutz und aktuelle Sicherheitsabgrenzung
type: reference
audience: [entwickler, qa, sicherheit, betrieb]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-08
---

# Parser-Sicherheitsabnahme

Der neue [CVE-2026-104183](https://github.com/advisories/GHSA-mjw6-4jj6-33hc)
betrifft den tatsaechlich verwendeten stream-json-Assembler 1.9.1. Direkte
Zuweisung von __proto__ ersetzte den Prototyp des gelesenen Objekts, sowohl
normal als auch mit Reviver. Der vorhandene Tiefenlimit-Backport schuetzte
diesen unabhaengigen Pfad nicht.

Beide Schreibstellen verwenden jetzt CreateDataProperty-aequivalente
Dateneigenschaften. Prototyp bleibt Object.prototype, __proto__ wird als eigene
Dateneigenschaft erhalten, verschachtelte Werte und doppelte Schluessel stimmen
mit JSON.parse ueberein. Kein Null-Prototyp-Ersatzobjekt und kein stiller
3.x-API-Wechsel fuer die CommonJS-/Detox-Verbraucher. Keine neue Audit-Ausnahme.
Der Patch ist regulär in pnpm gebunden; Provenienz enthaelt Patch-SHA256 und
sha512-Integritaet des Originalpakets aus der oeffentlichen npm-Registry.

Negativkontrolle mit verifiziertem Original 1.9.1: zwei normale Vertraege
bestanden, vier Tiefenlimit- und vier Prototype-Regressionen scheiterten wie
erwartet. Mit isoliert gepatchtem Original bestanden dieselben zehn Tests.
Der Lockfilevergleich aendert ausschliesslich vier Patchhash-Referenzen;
frozen/offline-Aufloesung aller 36 Workspaces besteht. Keine neue DB/Container.

Regulaere pnpm-Installation mit frozen Lockfile und ohne Lifecycle-Skripte:
zwoelf echte Runtime-Vertraege gruen (1,64 s), einschliesslich Bildverarbeitung
und Artillery-CSV-Verbraucher. Neun bestehende Security-Policy-Regressionen
gruen; Ablauf, neue/geaenderte Evidenz, falsche Version und erreichbare Pfade
bleiben sperrend. Keine Anhebung eines Audit-Schwellwerts.

Der [JSONC-Befund](https://github.com/advisories/GHSA-hqr4-qq8f-hg3x) ist ein
separater Kommentar-Parserpfad. Im verifizierten 1.9.1-Paket fehlt dieses Modul.
Die GitHub-Versionserkennung bleibt sichtbar; sie wird nicht als abgeschaltet
oder automatisch geschlossen ausgegeben.

## Weitere Sicherheitsbefunde

GitHub meldete am 08.10.2026 acht offene Alerts: drei ChromaDB, zwei stream-json,
node-forge, http-cache-semantics und sprintf-js. Die ChromaDB-Advisories haben
keinen Herstellerfix. Erneute Pruefung der vorhandenen versionsscharfen Policy
gegen aktuelle GHSA-/CVE-Aliase und committed Quell-/Deploymentfingerprints:
drei not_affected, null blocked, ausschließlich eingebetteter Betrieb. Keine
Fingerprints oder Ablaufdaten erneuert; Wiedervorlage bleibt 2026-10-15. Dies
ist keine allgemeine ERP-Mandantentrennungsabnahme und kein behobenes Paket.

node-forge, http-cache-semantics und sprintf-js besitzen laut aktuellen
GitHub-Advisories ebenfalls keinen Herstellerfix. Erreichbarkeit/gezielte
Abhilfe bleiben offen; keine pauschale Freigabe. Der lokale Production-Audit
und GitHub-Alerts haben verschiedene Abhaengigkeitssichten. Eine leere
GitHub- oder Release-Sicherheitsabnahme wird nicht behauptet.

GitHub auf d81a86b38: PostgreSQL, CRM-/Domaenen-Smoke, kritische E2E, OpenAPI,
Service Security, Security Agent und Erntepeak erfolgreich. Quality abgebrochen,
kein Gesamterfolg. Roter Security-Scan stammt ausschliesslich vom Node-Audit:
node-forge GHSA-86w9-cpqp-85rv und braces GHSA-vfj7-8cjw-p6xm (je High, kein
Herstellerfix). ZAP, Trivy, Grype und Bandit waren erfolgreich. Diese beiden
Production-Befunde bleiben fuer einen gezielten Folgeclaim offen; sie sind nicht
mit den acht GitHub-Alerts gleichzusetzen.
