---
title: React Produktionsstart – Handoff
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Reproduzierter React-Startabsturz, zentrale Chunkkorrektur und echter Produktions-Browsercheck.
---

# Ursache und Korrektur

Die Sales-Smokes auf dca5062f8 erhielten HTTP200, aber der Browser blieb leer.
Der Trace dokumentiert Cannot set properties of undefined (setting Children)
im vendor-react-Bundle. Backend und Frontend-Preview waren erreichbar; ein
Login-Redirect war nicht belegt. Lokale Reproduktion mit dem vorhandenen
Produktionsbuild auf /login bestaetigte denselben Fehler und einen leeren Root.

Die manuelle Vendor-Aufteilung gruppierte den Router mit React, lagerte aber
dessen React-Store aus. Dadurch entstand die beim Build gemeldete zyklische
Chunk-Abhaengigkeit. React, ReactDOM, Scheduler, react-is und CommonJS-Interop
bilden nun das Fundament; Router-/Store-Verbraucher werden davon getrennt.
Keine Bibliotheksversion, Anmeldung, Berechtigung oder Fachregel wurde geaendert.

Der korrigierte Produktionsbuild beendet sich erfolgreich und meldet den
React/Store-Chunkzyklus nicht mehr. Der identische Browseraufruf zeigt nun die
bedienbare Schaltflaeche Mit SSO anmelden, ohne PageError. Vorher Roottextlaenge0,
nachher210. [Vorher](screenshots/production-react-boot-20261029/before.png) und
[nachher](screenshots/production-react-boot-20261029/after.png) sind echte Bilder
des kompilierten Produkts, keine nachgebaute Maske.

# Regressionsschutz

scripts/check-production-bootstrap.mjs prueft den oeffentlichen Loginweg gegen
einen vorhandenen Produktions-Previewserver. Ein frischer Browserkontext
verwendet weder Kennungen noch Tokens. Externe Requests werden blockiert,
Geschaefts-API-Antworten im Test explizit durch synthetische401 ersetzt.
Bedienbarer SSO-Knopf und fehlende PageErrors sind Pflicht; bei Fehlern bleibt
der Check rot und speichert Ergebnis/Screenshot. Der Smoke-Workflow fuehrt ihn
vor den fachlichen Browser-Smokes aus. Das bestehende waitForAppReady wird
nicht abgeschwaecht.

Lokaler Aufruf gegen den eigenen Port3012 erfolgreich. Vollstaendige
Typpruefung und Workflow-YAML-/Schrittreihenfolgepruefung sind gruen. Der eigene
Previewprozess auf3012 ist beendet. Vorschau und Diagnoseartefakte betreffen
nur diesen eigenen Prozess; keine gemeinsame DB/Container/Sitzung veraendert.

# Grenzen

Dies ist eine Produktionsstart-Abnahme, keine persoenliche SSO-/MFA-Anmeldung
und keine erneute fachliche Browser-Gesamtabnahme. Weitere bestehende rote
Backend-/Frontend-/Inventar-/Seitenregistrierungsvertraege bleiben getrennt
zu schliessen. GatesA/B/C851,E804/851 und47Runtimepunkte werden dadurch nicht
als fachlich abgeschlossen umetikettiert. Die echten CI-Traces koennen Tokens
enthalten und bleiben ausschliesslich im ignorierten Diagnoseverzeichnis.

Lieferquelle artifacts/migration-repair-source; exact manifest/private index,
GitHub-Integrationszweig codex/migration-parity-repair-20261022.
