---
title: Explizite SQL-Testgrenzen und fachgerechter Ernte-Leitstand
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Gemeinsamen Pruefstand korrekt benutzen

Zwei SQL-Fixtures riefen die produktive Studio-Probe-Auswahl auf, obwohl die gesamte Testsitzung bereits auf dem gemeinsamen Pruefstand laeuft. Die produktive Absicherung verbietet zu Recht eine Simulation auf derselben Datenbank wie dem Entwicklungsbetrieb. Sie bleibt unveraendert. Die Fixtures verwenden jetzt ausdruecklich die vorhandene, mit pruefstand_erlaubt verifizierte Testengine und binden nur innerhalb des Tests die Simulation daran. Eigene Datensaetze bleiben in zurueckgerollten aeusseren Transaktionen; kein Reset, keine neue Datenbank und kein Container. Ein bisheriger Skip bei fehlender Probe-Konfiguration ist durch die ausdrueckliche Testgrenze ersetzt.

Die Ernte-Abrechnungssteuerung ist als cockpit klassifiziert: Sie bearbeitet Regeln und Annahmen als mehrere Aggregate. objectPage hatte faelschlich eine einzelne Identitaet vorausgesetzt. Zentrale Maskenregeln und deren Tests werden nicht abgeschwaecht.

34 SQL-/Simulations-/JWT-Grenzvertraege sowie 119 bestehende Masken-/Layoutvertraege bestanden. Der Backend-Gesamtlauf ergab 24175 bestandene Faelle; die fuenf uebrigen Befunde waren ausschliesslich fehlende kanonische Dateien im lokalen Testexport (unter anderem Dockerfile, CODEOWNERS und Nginx-Konfiguration). Nach Ergaenzung exakt dieser Git-Dateien bestanden alle elf zugehoerigen Repository-Vertraege. Das ist ein kombinierter lokaler Nachweis, kein behaupteter neuer vollstaendiger Einzellauf und keine vorweggenommene GitHub-Abnahme.

Die lokale isolierte PyJWT-2.15-Laufzeit entspricht der bereits vorhandenen Repository-Abhaengigkeit. Die globale alte Installation wurde nicht veraendert; kein JWT-Test abgeschwaecht. Vollstaendige Frontend-Suite: 1350 Tests in 271 Dateien bestanden; spaetere Studio-Standardfeldumstellung zusaetzlich mit sechs Bedienfaellen und TypeScript geprueft.
