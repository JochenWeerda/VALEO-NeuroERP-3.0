# SEC-018

## Titel

Frontend-HTML-/Print-Pfade inventarisieren und als Guard absichern

## Problem

Nach der XSS-Haertung der bekannten Printpfade fehlte noch ein fester Schutz dagegen, dass neue rohe HTML-Sinks spaeter unbemerkt in das Frontend gelangen.

## Loesung

- statische Inventur der Frontend-Sourcen auf gefaehrliche HTML-Sinks
- explizite Allowlist fuer die drei bekannten, bereits gehaerteten `document.write`-Pfade
- CI-Regressionstest fuer neue rohe HTML-Sinks

## Abnahme

- keine weiteren HTML-Sinks in `packages/frontend-web/src`
- neue Vorkommen schlagen den Frontend-Security-Test fehl
- CI-Lane fuehrt den Guard standardmaessig mit aus
