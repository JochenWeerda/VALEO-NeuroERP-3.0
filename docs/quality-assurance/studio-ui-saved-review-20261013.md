---
title: Studio-Oberflaeche bindet Aktionen an gespeicherten Stand
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Studio-Anmeldung und gespeicherter Stand

Der Studio-API-Client sendet keine erfundenen X-Actor-ID-Header und hat keinen waehlbaren Publisher-Parameter mehr. Der vorhandene authentifizierte API-Client und die serverseitige Tokenpruefung bestimmen die Identitaet.

Die Oberflaeche vergleicht den aktuell angezeigten Entwurf mit der vom Server beim Speichern zurueckgegebenen Definition. Bei lokalen Aenderungen sind Pruefung und Freigabe deaktiviert; erfolglose Speicherung hebt diese Sperre nicht auf. Ein zuvor erzeugter Runtime-Link wird fuer einen geaenderten Entwurf ausgeblendet. Die Oberflaeche erklaert, dass eine andere angemeldete menschliche Administration die Freigabe erteilen muss.

Abnahme: vier Vitest-Dateien mit acht bestandenen Faellen: ScreenStudioPage.test.tsx, studio-api.test.ts, studio-reducer.test.ts, StudioRunPage.test.tsx. Der neue UI-Fall prueft Speichern, Bearbeiten, Sperre, Speicherfehler und erneute Speicherung. Der Transportfall prueft die exakten Argumente aller fuenf Schreibaufrufe ohne Urheberheader. Die gemeinsame Renderer-Vorschau bleibt erhalten.

Offen: Diese lokale Sperre ersetzt keine serverseitige Bindung an den vom Reviewer angezeigten Hash. Der zweite Benutzer braucht noch eine Entwurfs-Auswahl und Wiederaufnahme nach Anmeldewechsel; ein vollstaendiges Statusmodell und Publikationshistorie fehlen. Die vorhandene API lehnt Selbstfreigabe serverseitig ab. Keine reale Rollenvergabe, kein produktiver Schreibvorgang und keine neue Browser-Screenshotabnahme in diesem Slice.
