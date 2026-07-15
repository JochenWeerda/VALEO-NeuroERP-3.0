---
title: "Fuetterungsberatung — Rollout- und Betriebskonzept"
type: runbook
audience: [produkt, fachlich, devops, support, security, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Kontrollierte Einfuehrung vom internen Referenzbetrieb bis zum mandantenweisen Produktivbetrieb.
---

# 15 — Rollout

## 1. Rolloutprinzip

Die Aktivierung erfolgt mandanten- und faehigkeitsweise hinter dem Modul-Flag
`feeding_advisory`. Datenmigration, Sichtbarkeit, Schreibaktionen, Agententools
und externe Connectoren besitzen getrennte Gates. Ein freigeschaltetes UI ist
kein Nachweis fuer einen produktionsreifen Liveconnector.

## 2. Stufenmodell

| Stufe | Nutzer/Daten | Zweck | Exit-Kriterium |
|---|---|---|---|
| R0 Entwicklung | synthetisch/Fixtures | Domain-, Contract-, Golden- und UI-TDD | fokussierte Tests gruen |
| R1 intern | Referenzbetrieb/Seed | vollstaendige Journey und Supportlernen | keine P0/P1-Defekte, Runbook erprobt |
| R2 Pilot | 1–3 freigegebene Betriebe | reale Daten, Shadow-/Advisory-Modus | Fachabnahme, Datenqualitaet, 14 Tage stabil |
| R3 begrenzt | ausgewaehlte Mandanten | produktive Freigabe und Planung | SLOs, Support und Rollback nachgewiesen |
| R4 allgemein | berechtigte Mandanten | skalierter Betrieb | Release-Gates und Kapazitaet gruen |

## 3. Gate-Matrix

| Gate | Owner | Nachweis |
|---|---|---|
| fachliche Regeln/Golden | Fachowner + QA | versionierte Quelle, Review, Golden-Suite |
| Tenant/RBAC/Grants | Security + Domain | negative Isolation-/403-Tests |
| Datenmigration | Data/Domain | Zaehler, Checksummen, Backfilljournal |
| UI/Accessibility | UX + QA | Meridian-Governance, axe, Keyboard-Journey |
| Performance | Platform | p95/p99, Payload- und Solverbudget |
| Support | Product Ops | Runbook, Alarmwege, bekannte Grenzen |
| Liveprovider | Integration Owner | Vertrag, Consent, Secret, Egress, Smoke |
| KI-Agent | AI Governance | Eval, Toolpolicy, Human Gate, Audit |

## 4. Feature-Flags

- `feeding_advisory`: Modul und Navigation;
- capability flags fuer Editor, Plan, Execution, Consulting und Agenten;
- tenant-/business-spezifische Allowlist;
- Connector-Liveflag getrennt von Mock/Sandbox;
- Kill Switch fuer schreibende Agententools und externe Exporte.

Flags ersetzen keine Autorisierung. Backendrollen und Business-Grants bleiben
auch bei deaktivierter oder manipulierten UI wirksam.

## 5. Pilotvorbereitung

Vor R2 werden Betrieb, Standorte, Herden, Gruppen, Futter, Analysen, Preise,
Bestand und Rollen gemeinsam geprueft. Der Berater absolviert die Journeys
Datenreife, Variante, Freigabe, Plan, Ist, Abweichung und Massnahme. Erwartete
Ergebnisse und bekannte fachliche Grenzen werden unterschrieben dokumentiert.

## 6. Observability und SLO

| Signal | Ziel/Alarm |
|---|---|
| API-Verfuegbarkeit | Release-SLO des Portals; Fehler nach Tenant/Route ohne Fachdatenlabel |
| p95 Worklist | Budget aus ScreenDefinition/Performancevertrag |
| Solverlauf | Laufzeit, Status, Abbruch, Infeasibility, Version |
| Import/Sync | Lag, Quarantaenerate, Dubletten, Deletes/Moves |
| Planaktualitaet | aktive/abgelaufene/ueberholte Plaene |
| Datenreife | fehlende Analysen/Preise/Einheiten je Betrieb |
| Action Audit | Erfolg, Ablehnung, Idempotenz, Actor, Correlation |
| Agent | Toolfehler, Policy-Denial, Human-Gate-Quote, Eval-Drift |

## 7. Datenschutz und Security

Logs enthalten IDs und technische Metadaten, keine frei kopierten Betriebs-
oder Tierdetails. Secrets liegen im Secret Store. Exporte sind autorisiert,
zeitlich begrenzt und auditiert. Supportzugriff benoetigt Zweck, Freigabe,
Business-Grant und Ablaufzeit.

## 8. Cutover

1. Releaseartefakt, Migration und Flags einfrieren.
2. Backup-/Restore- und Forward-Fix-Bereitschaft pruefen.
3. Migration/Backfill tenantweise ausfuehren und validieren.
4. Read-only/Shadow aktivieren, Projektionen vergleichen.
5. Schreibfaehigkeiten stufenweise freigeben.
6. Smoke-Journeys mit Fachnutzer ausfuehren.
7. Hypercare starten und Entscheidung protokollieren.

## 9. Abbruch und Rollback

Abbruchkriterien sind Tenant-Leak, falsche Freigabeversion, unerklärte
Berechnungsabweichung, Datenverlust, doppelte externe Wirkung oder nicht
einhaltbares SLO. Flags werden geschlossen, Jobs pausiert, externe Aktionen
idempotent gestoppt und der letzte stabile Readpfad aktiviert. Daten werden nicht
blind geloescht; Korrektur/Komensation bleibt auditiert.

## 10. Support und Hypercare

R2/R3 besitzen benannten Fach-, Technik-, Data- und Security-On-Call. Triage
klassifiziert P0 Tenant/Daten/Freigabe, P1 Kernjourney, P2 Teilfunktion und P3
Usability. Jeder Defekt beginnt mit reproduzierendem Regressionstest. Erkenntnisse
fliessen in Kapitel 13, 16 und das zugehoerige Arbeitspaket zurueck.

## 11. Allgemeine Freigabe

R4 erfordert Release-A/B/C-DoD, offene Risiken mit Owner/Termin, bestandene
Security-, A11y-, Performance- und Restore-Gates, dokumentierte Providergrenzen,
geschulten Support sowie eine nachvollziehbare Go/No-Go-Entscheidung.
