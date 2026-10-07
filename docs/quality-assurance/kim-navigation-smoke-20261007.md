---
title: KIM-Deep-Link - deterministischer Navigations-Smoke
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: lokal_geprueft
last_reviewed: 2026-10-07
---

# KIM-Smoke-Reparatur

Das Browser-Artefakt des [fehlgeschlagenen Laufs](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/37636718903)
zeigt nach korrekter Weiterleitung den ehrlichen Zustand `Datensatz nicht gefunden`.
Der Test hatte fuer `PERF-K1` keinen Kunden angelegt oder bereitgestellt. Eine
laengere Wartezeit oder eine geaenderte Produktfehlermeldung wuerde das nicht loesen.

`kim-performance-smoke.spec.ts` liefert deshalb ausschliesslich den GET eines
konkreten Kunden mit gueltiger UUID als Browser-Lesefixture. Die echte
ScreenDefinition und der native Renderer bleiben im CI-Test erhalten.
Geprueft werden die vollstaendige Ziel-URL mit Kundenkennung und `tab=chef`,
die native Kundenmaske, der sichtbare Firmenwert und das aktive
Stammdatenregister. Fehler-/Nichtgefunden-Zustaende sind im Erfolgsfall verboten.
Ein zweiter Test liefert fuer denselben GET einen 404 und verlangt den
Nichtgefunden-Zustand ohne native Maske. Das bisherige Oeffnungsbudget der
Kundenlisten-Weiterleitung bleibt unveraendert.

## Abnahme

Zwei echte Chromium-Browserpruefungen bestanden in 6,7 Sekunden gegen die
isolierte committed Frontendquelle. Fuer diesen lokalen Lauf wurden die echte
kanonische ScreenDefinition aus derselben Quelle und leere optionale Tabellen
als Lesefixture bereitgestellt; es lief kein lokales Backend. Diese zusaetzliche
lokale Vorbereitung ist nicht Teil des CI-Tests. Die erste kalte lokale
Ausfuehrung scheiterte an einer noch fehlenden Schema-Artefaktdatei; nach ihrer
Bereitstellung bestanden beide Pruefungen. Kein Produktcode geaendert.

Der Browservertrag beweist Navigation, Identitaetsanzeige, Registerwahl und
Fehlerdarstellung; er ist kein CRM-Persistenz- oder Tenantintegrationsnachweis.
Keine DB, neuer Container, Migration oder Reset. Die GitHub-Smoke-Abnahme
des gelieferten Commits bleibt separat erforderlich.
