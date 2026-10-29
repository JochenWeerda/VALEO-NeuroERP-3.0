---
title: Verifizierte Backend-Sicherheitsupdates 2026-10-23
type: reference
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-23
---

# Backend-Sicherheitsupdates

Die bestehenden Backend-Abhaengigkeiten erhalten drei offiziell bestaetigte Sicherheitskorrekturen:

- GitPython3.2.1 gegen [GHSA-83vg-56qc-22m7](https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-83vg-56qc-22m7).
- Black26.10.1 gegen [GHSA-cg8m-r9f2-5wm2](https://github.com/advisories/GHSA-cg8m-r9f2-5wm2).
- OpenTelemetryAPI/SDK/HTTP-Exporter1.45.1 mit Instrumentierung0.66b1 gegen [GHSA-xcq7-p3pf-p88h](https://github.com/advisories/GHSA-xcq7-p3pf-p88h). Zusammengehoerige Versionen und Abhaengigkeiten direkt gegen PyPI geprueft.

Die komplette requirements.txt ist frisch und ohne Veraenderung der laufenden Umgebung aufgeloest. Alle155 daraus bestimmten direkten und transitiven Pakete sind explizit auditiert: keine bekannten Schwachstellen. Es wurden keine Ausnahmen ergaenzt. Gepatchte Bibliotheken liegen nur in einem lokalen Pruefverzeichnis. Der neue Kompatibilitaetstest fuehrt einen echten HTTP-Request und eine SQL-Abfrage aus und weist beide Spans nach; kein Exportnetzwerk, keine PostgreSQL-Schreibzugriffe, keine neue DB oder Docker-Ressource.

Dieser kleine Hotfix basiert auf dem unveraenderten main-Stand8086c464f. Er enthaelt ausschliesslich diese sieben Versionsanpassungen, den Kompatibilitaetstest und zugehoerige Dokumentation. Die noch nicht abgenommene Maskenmigration aus Entwurfs-PR38 wird damit nicht aktiviert. Ein erfolgreicher lokaler Abhaengigkeitsaudit ist kein behaupteter gruener Gesamt-CI-Lauf und keine pauschale Schliessung aller weiteren Security-Funde.
