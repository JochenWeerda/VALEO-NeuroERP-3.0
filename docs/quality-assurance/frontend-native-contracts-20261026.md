---
title: Frontend-Integration und native Listenvertraege
type: verification
owner: Codex
status: in-arbeit
last_reviewed: 2026-10-26
---

# Abnahme 2026-10-26

Arbeitsansicht ausschliesslich `artifacts/migration-repair-source`; keine Aenderung
am Rootindex, keine Installation in gemeinsame Dependencies und keine Datenbank.
Delegation unter dem bestehenden Lead-Claim PENDING-INTEGRATION.

Die Fachaktionsintegration fehlte im Command-Palette-Modell der Arbeitsansicht.
Die bereits vorhandene Workspace-Registry wird jetzt mit Agrar-Featurefilter und
Session-Scopes in die Palette eingebunden. Der neuere debouncte Live-Resolver
bleibt erhalten. Das Clientfilter ersetzt keine serverseitige Autorisierung.
Die vier Command-Mapping-Tests bestehen.

Drei tatsaechlich geroutete Listen nutzten nicht registrierte Screen-IDs:
`einkauf/angebote-liste`, `einkauf/lieferanten-liste`, `agrar/duenger/liste`.
Ihre Seiten binden nun `einkauf/angebote`, `einkauf/lieferanten` und
`agrar/duenger-liste`, jeweils aus dem existierenden Python-Builderregister.
Die Seiten bleiben in der zentralen NativeListPage/Runtime/Renderer-Kette.

Die drei bisherigen Quelltexttests wurden durch echte Mounts ersetzt. Nur
HTTP-Transport und die authentifizierte Testsession sind ersetzt; Compiler,
Runtime, Tabellen, Renderer und Rechteprojektion laufen unveraendert. Die
Schemafixture ist unveraendertes Builder-JSON. Ein Python-Paritaetstest verhindert
Fixture-Drift (Python-Paritaetstest: 1/1 bestanden). Synthetische Zeilen pruefen sichtbare Identitaet, die kanonischen
Screen-GETs, beschriftete Touch-Aktionen und fehlende Schreibrechte. Duenger
prueft zusaetzlich den erlaubten Rollenfall mit Bestaetigung und Pflichtgrund.
Der Datentransport verwendet den echten gemeinsamen Masken-Datenprojektorvertrag.

Erster fokussierter Lauf: 38/41 Dateien bestanden, 297/298 Tests bestanden.
Zwei Suiten scheiterten vor Ausfuehrung am fehlenden direkten `js-yaml`-Paket;
der Lead bearbeitet Manifest/Lock/isolierte Installation. Der dritte Fehler
war die oben korrigierte Command-Palette-Integration. Die drei neuen nativen
Mounttests bestanden vor Ergaenzung des positiven Duenger-Schreibfalls.

Gesamt-CI bleibt offen. Die Basis hatte 48 fehlerhafte Dateien / 214 Fehler.
Viele bestehende UIX-Tests lesen alte Seitenquelltexte und fordern Inline-JSX,
obwohl die Seiten inzwischen ScreenDefinitions verwenden. Diese Erwartungen
muessen am realen nativen Bedienvertrag weitergeprueft werden; weder Legacy-
Wrapper noch Testloeschung oder reduzierte Schwellen sind eine Abnahme.
Dispositions-Schreibaktionen bleiben absichtlich deaktiviert.
