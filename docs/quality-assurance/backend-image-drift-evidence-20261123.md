---
title: Dokumentationsnachweis im Backend-Image
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-23
version: 1.0.0
description: Vollstaendige Buildquellen und schlanker Laufzeitbericht statt fehlendem oder veraltetem Hostartefakt.
---

# Backend-Image: echter Driftbericht

## Umsetzung

Dockerfile.backend erzeugt den Bericht in einer eigenen stdlib-only Buildstufe aus Doku-Markdown, API-Modulen, Services, Alembic-Dateien, dem ganzen Frontend-src-Baum und der kanonischen Seitenaltlastliste. Der ganze Frontend-Quellbaum ist noetig, weil der Generator Importketten auch ausserhalb von pages verfolgt. Der bestehende Generator bleibt unveraendert. Nur der erzeugte JSON-Bericht wird nach /app/artifacts kopiert; keine Dokuquellen oder zusaetzliche Bibliotheken im Laufzeit-Image.

Das backend-spezifische Dockerignore uebernimmt die Wurzelregeln und erlaubt nur zusaetzliche Dokumentationsquellen. Verschachtelte .env-Dateien und ausgeschlossene Git-/Paket-/Artefakt-/Python-Cache-Verzeichnisse werden danach erneut gesperrt. Der globale Buildkontext anderer Images bleibt unveraendert. Ein Vertrag erkennt, wenn die gemeinsamen Regeln auseinanderlaufen.

## Nachweise

- Einmaliger vollstaendiger Vergleich der rekonstruierten Buildquellen mit dem Checkout: summary und issues identisch. Der Gesamtbatch brauchte171,34s; dessen spaeter geaenderter Ignore-Regeltest scheiterte noch an seiner alten Assertion, die eng korrigierte Fassung bestand danach separat.
- Fuer laufende CI ersetzt eine kleine deterministische Quellstruktur den teuren Gesamtcheckout-Vergleich: dokumentiertes Endpoint/Service/Migration, echter undokumentierter Endpoint sowie Seitenimport ueber components. Stage- und Vollquellenbericht muessen gleich sein und genau den eingebauten Endpointbefund behalten. Mit bestehenden Schema-Paketvertraegen4 Tests bestanden in1,77s.
- CI Docker Build Smoke legt harmlose Testdateien in docs/.env-evidence-canary.md, docs/node_modules und docs/artifacts an; der echte Build muss diese ausschliessen. Das Laufzeit-Image muss einen auswertbaren Bericht mit konsistenten Zahlen und null Drift liefern. Keine Aufweichung des bestehenden Null-Drift-Gates.
- Python-Code des neuen Image-Smoke-Schritts aus geparstem Workflow kompiliert erfolgreich; git diff --check ohne Fehler.

## Grenzen und Betrieb

Kein lokaler Docker-Build und keine DB-Aktion waehrend fremder Pruefstandnutzung. Die echte Image-Abnahme erfolgt im bestehenden CI-Build; sie ist noch offen. Der Bericht belegt den Buildzeitpunkt und dessen Quellen, nicht die aktuelle externe Umgebung oder Browserfunktion. Er ist kein signierter Commitnachweis. Docker kann die Stufe fuer unveraenderte Eingaben wiederverwenden. Fehlender Bericht in alten Images bleibt ehrlich503 bis zur Bereitstellung des neu gebauten Images. Proplanta-/FAOSTAT-Zugangsluecken werden dadurch nicht geschlossen.
