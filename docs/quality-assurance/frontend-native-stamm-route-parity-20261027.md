---
title: Native-Stamm-Detail- und Anlage-Routen 2026-10-27
type: verification
owner: Codex native_batch_contracts
status: geprueft
last_reviewed: 2026-10-27
---

# Stammrouten und Anlagekennungen

Arbeitsansicht: `artifacts/migration-repair-source`. Das historische Inventar
umfasst 19 Detail-Wrapper. 17 davon waren an falsche oder unregistrierte
Screen-IDs gebunden; zwei Agrar-Wrapper hatten bereits die kanonische ID.
Alle 19 binden jetzt die im Backend registrierten Detaildefinitionen, ihre
bestehenden Legacy-Create-Zweige und die tatsächliche Routenregistry. Das
Inventar ist ein statischer Quellenvertrag und keine Bedienfreigabe aller
Fachseiten.

Die sechs ausdrücklich registrierten Einkauf-Anlagepfade (`anfrage`,
`angebot`, `anlieferavis`, `auftragsbestaetigung`, `lieferant`,
`rechnungseingang`) und dynamische `neu`/`new`-Pfade übergeben keine
Anlagekennung mehr als Detail-ID. Die betroffenen Legacy-Formulare verwenden
die vorhandene `isStammCreationEntityId`-Erkennung oder keinen Detail-ID-Wert.
GET- und Save-URLs, fachliche Validierung und Formulare blieben ansonsten
unverändert. Bestehende Entitäten werden weiterhin vom Native-Detail-Wrapper
gerendert; Anlage bleibt im Legacy-Formular.

Echte Mounts mit gemeinsamer Runtime und Renderer prüfen
`/agrar/saatgut-stamm/synthetic-seed` als Detail sowie
`/agrar/saatgut-stamm/neu` und `/agrar/saatgut-stamm/new` als Neuerfassung.
HTTP und Auth sind ersetzt; die Anlage-Mounts prüfen ausdrücklich, dass
kein GET `/api/v1/agrar/saatgut/neu` oder `/new` erfolgt. Die JSON-Fixture
enthält exakte Ausgaben von fünf kanonischen Python-Buildern; der Python-Test
prüft die Parität.

Abnahme: gezielter Vitest-Lauf mit vier Dateien, 41/41 Tests bestanden
(Vitest 4.1.12, `--maxWorkers=2`); Python-Parität 1/1 bestanden. Kein
Gesamtbuild, keine Datenbank und kein Container in diesem Slice.

Offene Fachgrenzen: `banken/konten-liste` hat zwar eine Detail-Zeilenroute
`/finance/bankkonto/{id}`, aber keine Anlageaktion; `/banken/konto/neu` ist
derzeit einer Listen-Seite zugeordnet. Die operative
`qualitaet/reklamation-detail`-Legacy-Seite ist kein belegtes
Neuerfassungsformular, auch wenn der gemeinsame Wrapper Anlagekennungen
formal an Legacy delegiert. Dafür wird kein Create-Siegel behauptet.
