---
title: Studio-Historie aus dem Maskenkatalog erreichen
type: qa
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Navigationsbindung der Studio-Historie

Historie und Differenzansicht waren als native ScreenDefinitions registriert, hatten jedoch kein kuratiertes Navigationsziel. Deshalb konnte die Omnibox beide Treffer nicht oeffnen; der bestehende Vollstaendigkeitsvertrag scheiterte.

Beide Ansichten verweisen jetzt auf den vorhandenen Arbeitsraum /admin/screen-studio. Dort waehlt der Bearbeiter einen vorhandenen Entwurf und anschliessend dessen Historie oder Vergleich. Ein Katalogtreffer ohne Entwurfskontext erfindet keine Belegkennung und ruft keinen parametrierten Historienendpunkt auf. Die bestehenden Zugriffskontrollen bleiben wirksam.

Zwei direkte Vertrage pruefen das registrierte Frontendziel und die Vollstaendigkeit der nativen Navigationsziele. Ausschliesslich zwei Registry-Eintraege geaendert; fremde Quellenhunks und bestehende Testdateien bleiben erhalten. Keine Datenbank oder Container benoetigt. Eine erneute Browser-Sichtpruefung ist durch diese statischen Vertraege nicht belegt.
