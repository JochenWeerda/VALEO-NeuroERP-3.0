---
title: Kanonische Studio Maskenidentitaeten
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Bereinigung belegter ungenutzter generischer Maskendefinitionen.
---

# Kanonische Maskenidentitäten (2026-10-28)

Die drei generischen Batch-15-Definitionen `finance/bankkonten-stamm`, `finance/kreditoren-stamm` und `qualitaet/reklamation-detail` sind entfernt. Die aktiven Seiten verwenden weiterhin `finance/bankkonto`, `finance/kreditor` und `qualitaet/reklamation` über `createStammNativeDetailPage`. Ihre Routen und Legacy-Fallbacks bleiben bestehen; dies belegt keine vollständige Funktions- oder Releaseabnahme.

Die Quellsuche fand keine direkten produktiven Screen-ID-Aufrufer der entfernten Definitionen. Gleichlautende Architektur- und Navigationspfade sowie die Kreditor-Neuaktion sind URLs und bleiben gültig. `config/studio_screen_versions.json` ist ein erzeugter Katalog und enthält bis zur anschließenden Regeneration noch die alten Einträge; die Inventarratsche enthält zwei alte Aktions-Baseline-Einträge. Historische Dokumente und Kataloge wurden hier nicht geändert. Der Integrationslauf muss den Katalog und die einschlägigen Inventargates aktualisieren und prüfen.

Prüfung: `python -m pytest tests/test_studio_canonical_mask_identities.py -q --noconftest -o addopts=''` — drei Tests bestanden. Sie prüfen das Fehlen der alten nativen Registry-Einträge, das Bauen der kanonischen Definitionen und die bestehende Seitenbindung einschließlich Fallback. Keine Datenbank- oder Browserprüfung.

Integrationsnachtrag: Auch die vierte ungenutzte Batch15-Definition qualitaet/reklamationen ist entfernt; sie zeigte auf Laborauftraege. Die echte Listenroute verwendet qualitaet/reklamationen-liste mit der fachlichen Reklamationsquelle und WorkflowResume. Neue Registry-/Page-Vertraege pruefen dies ausdruecklich. Andere unverifizierte Kandidaten bleiben bis zur Fachparitaet erhalten.
