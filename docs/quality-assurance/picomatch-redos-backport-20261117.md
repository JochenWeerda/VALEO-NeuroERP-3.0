---
title: picomatch ReDoS (GHSA-fc5q-39xc-vjpf) - lokale Quellkorrektur
type: qa
audience: [entwickler, qa, sicherheit]
owner: Claude-Code-runtime-security
status: active
last_reviewed: 2026-11-17
version: 1.0.0
---

# picomatch ReDoS (GHSA-fc5q-39xc-vjpf) - lokale Quellkorrektur

## Befund
Seit 17.11.2026 meldet der Node-Audit `GHSA-fc5q-39xc-vjpf` (CVE-2026-112366, high) fuer `picomatch` bis 4.0.7: ein
wiederholtes Extglob mit einem freien `*` neben weiterem Inhalt (`+(*a)`, `+(*a|b)`, `*(a*|b)`) wird zu einem
geschachtelten Quantor (`(?:[^/]*?a)+`), der bei einem knappen Fehlschlag exponentiell zurueckverfolgt. Gemessen
(4.0.4 und 4.0.7): `+(*a)` gegen 25 Zeichen rund 200 ms, Verdopplung je Zeichen; `*(a*|b)` gegen `ab` x 11 bricht
nach Minuten ab. Eine Herstellerversion gibt es nicht; der offene Upstream-PR micromatch/picomatch#194 erkennt nur
Zweige, die `?` und `*` mischen, und laesst `+(*a)` exponentiell (nachgemessen).

## Korrektur
- `picomatch` bleibt auf der eingesetzten Version 4.0.4 (Override exakt gepinnt) und wird per
  `pnpm patchedDependencies` gepatcht (`config/security/npm-patches/picomatch@4.0.4.patch`, nur `lib/parse.js`).
  Ein Wechsel auf 4.0.7 braechte keinen Sicherheitsgewinn (gleicher Befund) und liesse GitHubs Dependency Review eine
  "neu eingefuehrte" verwundbare Version melden; der Audit meldet fuer 4.0.4 nur diesen einen Befund.
- `analyzeRepeatedExtglob` erkennt einen Zweig mit freiem `*` neben weiterem Inhalt als riskant - fuer jede Zahl von
  Zweigen. Ein riskantes Muster behandelt picomatch dann wie bisher fuer seine anderen riskanten Formen: als Literal.
  Reine Sterne (`+(*)`), Sternfolgen (`+(*(a)|*(b))`), `@(...)`/`!(...)` und alle gewoehnlichen Globs bleiben, wie
  sie sind. `maxExtglobRecursion: false` schaltet die Pruefung wie upstream ab.
- Bewusste Bedeutungsaenderung: Zwei Faelle der Upstream-Testsuite (`*(a*|b)` gegen `ax`, `*/*(W*, *)*`) passen nicht
  mehr - genau die anfaellige Form. Keine Glob-Konfiguration im Repository nutzt sie.

## Nachweis
- Laufzeitvertrag `scripts/verify_picomatch_security.cjs` (im Gate `check_npm_backport_audit.cjs`): sechs feindliche
  Muster unter 250 ms, Literal-Verhalten, gewoehnliche Globs unveraendert. Negativkontrolle gegen 4.0.4 ohne Patch:
  der Lauf blockiert bis zum Abbruch.
- Upstream-Testsuite 4.0.4 gegen die gepatchte `lib/parse.js`: 1973 von 1975 gruen (die zwei oben genannten; auf 4.0.7
  entsprechend 1981/1983).
- Gate: exakte Hashes von Patch, `package.json`, `pnpm-lock.yaml` und installierter `lib/parse.js` (per echtem
  `pnpm install` nachgeprueft) in `config/security/npm-backport-reviews.json`; Review bis 2027-01-15, danach blockiert
  der Befund wieder. Selbsttests `scripts/test_npm_backport_audit.cjs` 22/22.

## Wiedervorlage
Erscheint eine Herstellerversion mit Fix, Patch, Review- und Gate-Eintrag entfernen und auf die Version heben.
