# SEC-017

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** .github/workflows/security-agent.yml, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

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
