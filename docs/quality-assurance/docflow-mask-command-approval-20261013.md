---
title: DocFlow-Commands und Freigaben in der Belegmaske
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# DocFlow-Commands und Freigaben in der Belegmaske

## Vertrag und Integration

Die Belegdefinition erzeugt commandBinding mit dem Transportvertrag docflow.v1 aus dem vorhandenen Kommandoverzeichnis. Der gemeinsame Maskenadapter verwendet die bestehenden Domain-Endpunkte fuer release, post, reverse und convert sowie Freigabeanfrage und -entscheidung. Keine neuen Endpunkte, Container, Tabellen oder fachlichen Freigaberegeln.

Der Renderer-Belegkopf ist Kontext, keine Command-Nutzlast. NativeDetail sammelt fuer gebundene Commands ausschliesslich deklarierte Eingaben. Der Adapter akzeptiert nur die Felder des jeweiligen Aufrufs, bindet erwartete Version und Belegkennung, verweigert fremde Endpunkte und Aufruferidentitaeten und uebersetzt die Domain-Ergebnisse command/status in ActionResult. Bei unsicherem Ausgang bleibt der Idempotenzschluessel fuer denselben Vorgang in der laufenden Maske erhalten. Version, Aktion, Command-Metadaten oder Eingaben aendern den Vorgang. Der im Dialog gesicherte Binding-Snapshot verhindert eine Ausfuehrung nach unbemerkt geaenderten Metadaten. Ein Seitenneuladen ist kein nachgewiesener dauerhafter Wiederanlaufvertrag.

Nur convert bietet eine echte dry_run-Vorschau. Buchen, Stornieren und Freigabeentscheidungen deklarieren keine Vorschau; ihre Bestaetigung und die serverseitige Validierung bleiben verbindlich. Storno verlangt eine Begruendung. Keine Simulation wird als Ausfuehrung gesendet. Schreibende Agentenaktionen werden dadurch nicht freigeschaltet (MCP-WRITE-014).

Freigabe anfragen, erteilen und ablehnen nutzen die bestehenden Domainrollen. Die offene approval_id kommt als Belegaktionsfeld vom Server und wird beim Oeffnen des Dialogs gesichert. Eine andere oder inzwischen ersetzte Freigabe wird nicht still verwendet. Aktion, Mandant, Inhalt, Ablauf und Vier Augen prueft weiterhin die zentrale Freigabe-Engine. Die Rollenprojektion wurde aus beleg_roles.py regeneriert; kein zweites Rechtesystem.

## Nachweise

- 67 Python-/PostgreSQL-Faelle: test_beleg_screen_definition.py, test_beleg_rechte.py, test_freigabe.py auf vorhandenem valeo_probe, Revision control_findings_20261013 (vorher approval_log_20261013). Einschliesslich neun Varianten, serverseitiger Freigabe-ID, Rechte, Funktionstrennung und Inhaltsbindung.
- 57 Vitest-Faelle in fuenf Dateien: Transport, Version, Idempotenzretry, Feldvalidierung ohne Eingabewerte, generische Rechte, Agentensperre, Vorschaugrenze und echte NativeDetail-Orchestrierung. Die Renderer-Attrappe uebergibt bewusst den vollen Belegkopf, um den im Browser gefundenen Context-Fehler abzusichern.
- Belegrollen-Generator --check gruen. ESLint der eigenen Source-Dateien ohne Fehler. Bestehender fokussierter Typecheck gruen; expliziter Typecheck des NativeDetail-Abhaengigkeitsgraphen meldet zwei bestehende ES2021/Array.at-Konflikte in UniversalMaskRenderer.tsx:94 und Breadcrumbs.tsx:86. Kein gruener Gesamt-Typecheck behauptet.
- Lokaler Sichtpruefungsmandant 51: neun bereits freigegebene Pilotdefinitionen aktualisiert, bestehendes Backend neu geladen und healthy. Echte SSO-Neuanmeldung mit der zuvor genehmigten synthetischen Einkaufskennung.
- Reale PIV-2026-000002: Buchen gesperrt, Buchung: Freigabe anfragen aktiv, deklarativer Gruende-Dialog geoeffnet und abgebrochen. Echte convert-Vorschau ueber HTTP, ohne anschliessendes Ausfuehren. Screenshots liegen lokal unter artifacts/docflow-approval-request-dialog-20261013.png und artifacts/docflow-convert-preview-20261013.png.

Keine finanzielle Browsermutation, neue Datenbank, neuer Dockercontainer oder Reset. Die API-Fachwirkungen und Freigaben sind gegen den gemeinsamen Pruefstand getestet; die Browserpruefung belegt Eingabe und Vorschau, keine real ausgefuehrte Buchung.

## Weiter offen

Gesamt-CI und generierte OpenAPI-/Handbuch-Integration bei fremdem WIP, persistenter Wiederanlauf nach Seitenneuladen, ausdruecklicher Idempotenzvertrag fuer Freigabeentscheidungen sowie die sichere Vorschlags-/Simulations-/Publikations-Governance neuer Prozessvarianten. Die Browsermaske zeigt Mengen wie 15.000 im deutschen Kontext; deren Dezimaldarstellung ist separat zu pruefen. Die zwei Array.at-Typecheck-Konflikte sind ebenfalls Folgearbeit.
