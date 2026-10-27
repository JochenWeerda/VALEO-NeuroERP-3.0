---
title: Batch 11/12 Frontend-Routen- und Buildervertraege
type: verification
owner: Codex
status: geprueft
last_reviewed: 2026-10-26
---

# Batch 11/12 Vertragskorrektur

Arbeitsansicht: `artifacts/migration-repair-source`. Die historischen Inventare
umfassen 59 Batch-11- und 83 Batch-12-Seiten. Ihre Quelltextpruefungen belegen
Routenbindungen, nicht die Bedienfreigabe aller 142 Seiten. Keine Seite oder
fachliche Aktion wurde fuer diese Korrektur geaendert.

Vier fruehere NativeListPage-Erwartungen entsprachen der tatsaechlichen Route
nicht mehr: `admin/audit-log.tsx` nutzt die konsolidierte Batch-12-Definition
`admin/audit-log`; `crm/lead-detail.tsx` nutzt bei Entity-ID PartyNativePage
und fuer die Anlage weiterhin den passenden Mask-/Legacy-Pfad;
`fibu/debitoren.tsx` bleibt der operative Finanz-Einstieg mit OP-Abfrage,
Tabelle und CSV; `admin/control-center/index.tsx` bleibt die operative
Planungs-/Vorfallseite mit ihren Incident-Aktionen. Fuer die letzten drei
Seiten wird hier kein NativeListPage-Siegel behauptet.

Zwei tatsaechlich geroutete Seiten sind zusaetzlich als echte Mounts geprueft:
`crm/kunden-liste` laedt den kanonischen Builder, rendert die synthetische
Zeile und oeffnet deren Detailroute; `admin/integrationen-quarantaene` laedt
den Kontroll-Builder und verbirgt Retry/Erledigen ohne Fachrecht. Der gemeinsame
Compiler, die Runtime und Renderer bleiben im Test unvermockt. Die eigene
JSON-Fixture ist exakt die Ausgabe von `build_crm_kunden_liste()` und
`build_batch12_kontroll_screen("admin/integrationen-quarantaene")`; nur HTTP,
Testsession und Navigationshook werden ersetzt. Ein Python-Paritaetstest
erkennt Builder-Drift.

Fokussierte Abnahme: Vitest 2 Dateien, 147/147 Tests bestanden (Vitest 4.1.12,
`--maxWorkers=2`); pytest 1/1 bestanden. Die nicht gemounteten Inventareintraege
bleiben reine Quellvertraege und beduerfen fuer ein Native-Siegel eigener
Bedien-/Fachabnahme. Keine Datenbank, kein Container, keine Installation.
