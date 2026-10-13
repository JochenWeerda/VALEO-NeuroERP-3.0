---
title: Belegpilot Routing und Vorschauabbruch
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-13
version: 1.0.0
description: Realer Pilot-Routenfehler und Weiterlaufen nach fehlgeschlagener Vorschau behoben.
---

# Belegpilot: Routing und Vorschauabbruch

Die von Claude bereitgestellte Route belege/:belegart/:id wurde real mit der
autorisierten Einkaufs-Testkennung am Referenzmandanten geoeffnet. Vorheriger Fehler:
Route references unsupported page group: @/pages/belege/beleg. Der zentrale
PageModuleLoader ordnet belege nun der bestehenden Finance-Gruppe zu, deren
import.meta.glob das neue Belegseitenmodul erfasst. Keine neue Maskenimplementierung.

Der gemeinsame NativeDetail-Dialog ignorierte bisher success=false einer Vorschau
und ging ohne proposedChanges zur Ausfuehrung weiter. Bei fehlgeschlagener Vorschau
bricht er jetzt ab, schliesst den Dialog und zeigt Fehler/Validierungsmeldungen;
kein anschliessender execute-Aufruf. Ein erfolgreicher Vorschauvertrag bleibt
Voraussetzung fuer das Weitergehen. Der DocFlow-Command-Adapter fehlt weiterhin.

22 Vitest-Faelle in vier Dateien bestanden, darunter echter dynamischer Import des
Belegmoduls und zwei gerenderte NativeDetail-Orchestrierungsfaelle mit abgewiesener
Vorschau. Sie beweisen, dass nach Freigabefehler/gesperrter Vorschau nur dryRun und
nie execute aufgerufen wird. Das einzelne Cold-Import-Testtimeout betraegt 20s;
keine globale Timeout-Aenderung. Keine Geschaeftsdaten gebucht/geaendert.

Reale Browser-Zwischenpruefung nach Loaderfix: Seite erreicht den gemeinsamen
NativeDetail-Ladezustand; Schema-API 200, Kopf-Leseweg 404 im noch alten Backend-
Prozess. Bestehender Backend-Container neu gestartet, um die vorhandenen Kopf-/Tab-
Routen zu laden. Vollstaendige Rechnung-/Tab-/Aktions-/Preis-Sichtpruefung bleibt
bis zum erfolgreichen Runtime-Nachweis offen. Keine Abnahme aus einem Fehlerbild.
