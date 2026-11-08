---
title: Versionierte Studio-Ausgangsfassungen vorhandener Masken
type: reference
audience: [entwickler, qa]
owner: Codex
status: active
last_reviewed: 2026-10-16
version: 1.0.0
---

# Vorhandene Masken kontrolliert ins Studio uebernehmen

GET /api/v1/studio/native-sources liefert registrierte Masken nach Bezeichnung mit begrenzter Seitengroesse und SHA-256-Quellstand. POST /api/v1/studio/native-imports bindet die Uebernahme ausschliesslich an diese Quelle, den angezeigten Hash und einen Wiederholungsschluessel. Mandant und Urheber stammen aus der geprueften Anmeldung; Zusatzfelder fuer eigene Definitionen, fremde Mandanten oder Freigaben werden abgewiesen. Es gilt das vorhandene beleg_write-Recht.

Der vorhandene Studio-Speicher legt genau eine Ausgangsfassung je Quelle und Mandant an und protokolliert sie in der bestehenden Historie. Originaldefinition und deren Hash bleiben nachvollziehbar erhalten. Die bisherige Maske bleibt aktiv. Ein Import erzeugt keinen Prozessnachweis und keine Freigabe; unvertraegliche Datenquellen/Aktionen werden sichtbar als Hindernis ausgewiesen. Es entsteht keine zweite Versionsdatenbank und kein zweites Rechtesystem.

## Abnahme

14 Backendvertraege einschliesslich SQL-Vertrag auf dem bestehenden gemeinsamen Pruefstand bestanden. Geprueft wurden echte HTTP-Autorisierung, fremde Quellen/Mandanten, veraenderte Quellhashes, unerlaubte Zusatzfelder, Wiederholung, konkurrierender Erstanlageversuch, genau ein Historieneintrag und gesperrte Veroeffentlichung. Die SQL-Pruefung rollt ihre eigenen Daten in der vorhandenen Datenbank zurueck.

Sechs Studio-/Import-Bedienvertraege und TypeScript bestanden. Zwei neue Endpunkte mit vier neuen typisierten Schemas; keine bestehenden API-Pfade oder Schemas geaendert. Architekturzuordnung und Endpunkt-/Service-Inventare enthalten die neue Platform-Komponente.

Reale Browserabnahme ausschliesslich mit vorhandener synthetischer Testkennung im genehmigten Sichtpruefungsmandanten: Duenger importiert, als draft erneut geoeffnet, create-Eintrag mit Revision und verifiziertem Urheber in der Historie sichtbar; aktiv veroeffentlicht=false. Hell-/Dunkelansicht der gemeinsamen Vorschau dokumentiert. Keine Kontingente verbraucht, keine Fachbuchung, keine Rollenvergabe oder Freigabe ausgefuehrt.

## Weiter offen

Dies ist die sichere Bestandsuebernahme. Basis-/Variantenpflege, vollstaendige Belegdaten-/Command-Kataloge, Kopf-/Positionsbearbeitung, alle fachlichen Belegketten-Pruefprofile und die Ablösung saemtlicher bisheriger Einstiege sind damit noch nicht abgeschlossen. grain.v1 bleibt das derzeit implementierte fachliche Studio-Freigabeprofil.
