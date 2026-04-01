# SEC-017

## Titel

Security-Regressionen als feste CI-Lane

## Problem

Scanner finden neue Klassen von Problemen, pruefen aber nicht gezielt jeden bereits behobenen Sicherheitsfehler gegen Regressionen.

## Loesung

- dedizierter Regression-Job im Security-Agent-Workflow
- gezielte Backend-Security-Suite
- gezielter Frontend-XSS-Regressionstest
- Docs-Governance in derselben Lane

## Abnahme

- Workflow startet bei relevanten Security-Codeaenderungen automatisch
- behobene Security-Slices sind durch feste Tests abgesichert
- operative README dokumentiert die Lane auch fuer lokale Ausfuehrung
