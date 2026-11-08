---
title: Reklamationsliste Lesevertrag
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Mandantengebundene Reklamationsprojektion ohne erfundene Prioritaet.
---

# Reklamationsliste: Lesevertrag (2026-10-28)

Die bestehende Listenroute liefert weiterhin eine einfache Liste der 200 neuesten Reklamationen des Request-Mandanten. Der Mandant wird bei der SQL-Abfrage und der Lieferantenauflösung verwendet. Die sechs bekannten Fachstatus behalten ihre bisherige Übersetzung; unbekannte Werte werden nicht als neu ausgegeben. Eine fehlende Priorität wird als null ausgewiesen: Datenmodell und Schreibvertrag enthalten derzeit kein Prioritätsfeld. Keine Priorität wird aus Frist oder Status abgeleitet.

Datenbankfehler bei Abfrage oder Referenzauflösung führen nach Rollback zu einer bereinigten 503-Antwort statt einer leeren Liste. Bearer- und Mandantenprüfung bleiben bestehen. Eine zusätzliche Qualitätsleserolle wurde nicht eingeführt: Eine kanonische LESEN[QUALITAET]-Definition oder ein entsprechender bestehender Routervertrag wurde nicht gefunden. Die 200er-Begrenzung und fehlende Paginierung bleiben ein offener fachlicher Umfang; Summen gelten nur für die geladenen Fälle.

Prüfung: `python -m pytest tests/test_complaint_list_read.py -q --noconftest -o addopts=''` — zwei isolierte Tests bestanden; sie prüfen Mandantenparameter, Begrenzung, Statusabbildung, unbekannte Priorität und bereinigten Fehler mit Rollback. Kein Datenbankintegrationstest. Der reguläre Testlauf wurde nach dem Hängen der gemeinsamen Fixture abgebrochen.

Lead-Nachlauf:Die gemeinsame Backendabnahme umfasst35 bestandene Faelle einschliesslich echter signierter REST-/MCP-/CLI- und SQL-Pruefung auf dem gemeinsamen Pruefstand. Die isolierte Fixture-Laufgrenze ist dadurch aufgeloest. Rueckgabeformat und Begrenzung bleiben unveraendert; Details im [Gesamtnachweis](studio-functional-lists-20261028.md).
